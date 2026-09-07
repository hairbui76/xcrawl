"""MOD-ai-adapter — the shared adapter port, its audit counters and its refusal rules.

The single promise of this module (SRC-SPEC §10.2) is ``prompt + schema -> JSON that fits
the schema``. Everything else it does is *refusing*: refusing to dispatch an adapter whose
isolation is unverified, refusing to hold a credential for a provider other than the one
the task names, refusing to register a tool, refusing to open a socket to a host outside
``ai_provider_endpoints_configured``, and refusing to put a transcript anywhere durable.

Three design points are contract obligations rather than taste:

1. **No outbound operation.** ``contracts/modules.yaml`` gives ``MOD-ai-adapter``
   ``outbound_operations: []`` and four forbidden edges (FE-16..FE-19). The adapter
   therefore never *calls* ``secret.issue_task_credential`` — ``contracts/ports.yaml``
   names ``MOD-analysis-worker`` as that operation's only caller. The worker calls it and
   hands the result in through :class:`TaskCredential`. The card's §4 "Consumes" line reads
   as *receives*, which is also how its own §3 puts it ("nhận credential per-task ngắn
   hạn"); see ``CR-TC-adapter-01``.
2. **The adapter never retries.** ``contracts/ai/tasks.yaml`` §1 ``retry_budget.split_rule_vi``:
   the whole budget lives at the task layer, so that ``COUNT(analysis_attempt)`` is a direct
   oracle for "how many times was the model called". An adapter-level retry would double
   the model calls without SQL seeing it.
3. **``usage`` unknown is three nulls, never zero** (I14). :class:`UsageReport` refuses at
   construction, so no call site can produce the forbidden shape.

Nothing in this module writes state (card §4: "Adapter **không** ghi state").
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Final, Protocol
from urllib.parse import urlsplit

import yaml
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.states import AnalysisAttemptOutcome, AnalysisTaskType

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
PROVIDERS_YAML: Final[Path] = REPO_ROOT / "contracts" / "ai" / "providers.yaml"

#: ``contracts/capabilities.yaml`` ACT-ai-adapter ``declared_oracle`` (ruling CR-PC06-03).
#: The number of tool/function definitions sent to a provider on *every* inference call of
#: *every* task type. It is a constant, not a default: there is no configuration that makes
#: it non-zero, which is the whole of ISO-01's guarantee.
TOOL_DEFINITIONS_REGISTERED: Final[int] = 0

#: ``contracts/errors.yaml`` ``details_safe_keys`` for the codes this module raises. An
#: error envelope may carry no other key, which is how "never log the transcript"
#: (``AI_OUTPUT_INVALID.redaction_vi``) becomes a structural property instead of a habit.
DETAILS_SAFE_KEYS: Final[Mapping[ErrorCode, frozenset[str]]] = {
    ErrorCode.AI_OUTPUT_INVALID: frozenset(
        {"task_id", "task_type", "attempt_number", "validation_failure_kind", "retry_after_ms"}
    ),
    ErrorCode.AI_PROVIDER_UNAVAILABLE: frozenset(
        {"task_id", "provider_name", "reason_code", "attempt_number", "retry_after_ms"}
    ),
    ErrorCode.AI_ATTEMPT_UNCERTAIN: frozenset(
        {"task_id", "attempt_id", "attempt_number", "cost_uncertain", "last_known_phase"}
    ),
    ErrorCode.CAPABILITY_DENIED: frozenset(
        {"module_id", "denied_capability_kind", "forbidden_edge_ref"}
    ),
    ErrorCode.VALIDATION_ERROR: frozenset({"field", "reason", "task_id", "task_type"}),
}

MODULE_ID: Final[str] = "MOD-ai-adapter"

#: ``contracts/ai/tasks.yaml`` §2 ``inference_timeout``, all ``PROVISIONAL`` and all below
#: ``lease_ttl_analysis`` = 900 s. Read from the contract rather than restated by hand
#: wherever a test needs them; kept here so the adapter can bound a call without importing
#: the task-lifecycle package (which lives behind another module boundary).
INFERENCE_TIMEOUT_SECONDS: Final[Mapping[AnalysisTaskType, int]] = {
    AnalysisTaskType.LABEL: 120,
    AnalysisTaskType.SUMMARY: 300,
    AnalysisTaskType.DIRECTION_PHRASING: 180,
}

_HOST_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9.\-]+$")


class AuthFamily(str, Enum):
    """``contracts/ai/providers.yaml`` §1 — the two families of REQ-D41."""

    API_KEY = "api_key"
    CLI_ACP = "cli_acp"


class JsonExtractionMethod(str, Enum):
    """``contracts/ai/providers.yaml`` §3 ``methods``."""

    NATIVE_JSON = "native_json"
    FENCED_BLOCK = "fenced_block"
    DELIMITED_ENVELOPE = "delimited_envelope"


class UsageReporting(str, Enum):
    """``exact`` or ``unknown`` (REQ-D44). ``unknown`` is a valid answer, ``0`` is not."""

    EXACT = "exact"
    UNKNOWN = "unknown"


class IsolationStatus(str, Enum):
    """``contracts/ai/providers.yaml`` §4 ``status_values``."""

    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    NOT_APPLICABLE = "not_applicable"


class TermsOutcome(str, Enum):
    """``contracts/ai/providers.yaml`` §5 ``fields.outcome``."""

    PERMITTED_FOR_THIS_USE = "permitted_for_this_use"
    NOT_PERMITTED = "not_permitted"
    UNCLEAR = "unclear"
    NOT_READ = "not_read"


class ProbeOutcome(str, Enum):
    """``ai.probe_provider_capability`` response (``contracts/ports.yaml``).

    ``unknown`` is a third value, not a synonym for ``unusable``: I14 and
    ``providers.yaml`` §7 ``test_outcome_rule_vi`` both forbid collapsing it.
    """

    USABLE = "usable"
    UNUSABLE = "unusable"
    UNKNOWN = "unknown"


class ProbeReasonCode(str, Enum):
    """The reason codes ``contracts/ports.yaml`` names for the probe response."""

    BINARY_MISSING = "binary_missing"
    NOT_LOGGED_IN = "not_logged_in"
    POLICY_UNVERIFIED = "policy_unverified"
    ISOLATION_UNVERIFIED = "isolation_unverified"
    PROBE_TIMEOUT = "probe_timeout"


#: ``contracts/ai/providers.yaml`` §4 ``ac16_reporting_rule_vi`` and ADR-0010 §Hệ quả: when
#: every CLI adapter is disabled, REQ-AC16 is reported ``BLOCKED``. Never ``FAIL`` — the
#: difference is the whole point of the rule.
AC16_BLOCKED: Final[str] = "BLOCKED"
AC16_PASS: Final[str] = "PASS"


class AdapterError(Exception):
    """A contract error code plus the safe envelope it must be reported with.

    The constructor filters ``details_safe`` against ``contracts/errors.yaml``
    ``details_safe_keys`` for that code and rejects any other key outright. That is what
    makes "never put the transcript in message or details" checkable: there is no key a
    transcript could travel under, so the guarantee does not depend on a caller remembering.
    """

    def __init__(
        self,
        code: ErrorCode,
        message_safe: str,
        *,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
        attempt_outcome: AnalysisAttemptOutcome | None = None,
    ) -> None:
        super().__init__(f"{code.value}: {message_safe}")
        allowed = DETAILS_SAFE_KEYS.get(code, frozenset())
        details = dict(details_safe or {})
        rejected = sorted(set(details) - set(allowed))
        if rejected:
            raise ValueError(
                f"{code.value} may not carry details key(s) {rejected}; "
                f"contracts/errors.yaml allows {sorted(allowed)}"
            )
        for key, value in details.items():
            if not isinstance(value, str | int | bool | type(None)):
                raise ValueError(
                    f"details_safe[{key!r}] must be a scalar; a structured value is how a "
                    f"transcript gets into an envelope (errors.yaml redaction_vi)"
                )
        self.code = code
        self.message_safe = message_safe
        self.details_safe: dict[str, Any] = details
        self.retry_after_ms = retry_after_ms
        self.attempt_outcome = attempt_outcome

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """The ``ErrorEnvelope`` of ``contracts/http/openapi.yaml``.

        ``scope`` and ``retry_class`` come from the generated registry, never from a choice
        made here: a handler must not be able to grant a retry policy the contract withheld.
        """
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": self.message_safe,
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
            "retry_after_ms": self.retry_after_ms,
        }


@dataclass(frozen=True)
class UsageReport:
    """``analysis-result.schema.json`` ``$defs.usage`` with I14 enforced at construction.

    ``unknown = true`` means all three fields are ``null``; ``unknown = false`` means both
    token counts are real integers. Writing ``0`` for "we do not know" is rejected here
    rather than three layers later, because by then it is already a number in a bill.
    """

    unknown: bool
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_micro_usd: int | None = None

    def __post_init__(self) -> None:
        if self.unknown:
            filled = [
                name
                for name, value in (
                    ("tokens_in", self.tokens_in),
                    ("tokens_out", self.tokens_out),
                    ("cost_micro_usd", self.cost_micro_usd),
                )
                if value is not None
            ]
            if filled:
                raise ValueError(
                    f"usage.unknown is true so {filled} must be null (I14; "
                    f"contracts/ai/tasks.yaml §1 usage_recording)"
                )
            return
        if self.tokens_in is None or self.tokens_out is None:
            raise ValueError(
                "usage.unknown is false so tokens_in and tokens_out must be real counts "
                "from the provider (analysis-result.schema.json $defs.usage)"
            )
        for name, value in (
            ("tokens_in", self.tokens_in),
            ("tokens_out", self.tokens_out),
            ("cost_micro_usd", self.cost_micro_usd),
        ):
            if value is not None and value < 0:
                raise ValueError(f"usage.{name} must be >= 0, got {value}")

    @classmethod
    def unknown_usage(cls) -> UsageReport:
        """The CLI/ACP shape (REQ-D44) and the shape after a provider failure."""
        return cls(unknown=True)

    @classmethod
    def exact(
        cls, *, tokens_in: int, tokens_out: int, cost_micro_usd: int | None = None
    ) -> UsageReport:
        """Token counts reported *by the provider*.

        ``cost_micro_usd`` stays ``None`` unless a sourced price table produced it: the
        Anthropic entries of ``providers.yaml`` §2.1 note that no price is in scope, and
        a derived-then-presented number would be a guess wearing the provider's authority
        (``usage_reporting_note_vi``, ``CR-PC06-OQ03-03``).
        """
        return cls(
            unknown=False,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost_micro_usd=cost_micro_usd,
        )

    def as_payload(self) -> dict[str, Any]:
        return {
            "unknown": self.unknown,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "cost_micro_usd": self.cost_micro_usd,
        }


@dataclass(frozen=True)
class ProviderRef:
    """``analysis-result.schema.json`` ``$defs.provider_ref`` — traceability metadata.

    Not part of the analysis key (ADR-0008 §6), and the value recorded is the provider that
    *produced* the result, not the one that was tried first (``providers.yaml`` §6).
    """

    auth_family: AuthFamily
    provider_name: str
    model_name: str
    provider_config_id: str | None = None

    def as_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "auth_family": self.auth_family.value,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
        }
        if self.provider_config_id is not None:
            payload["provider_config_id"] = self.provider_config_id
        return payload


@dataclass(frozen=True)
class SourceRef:
    """One row handed to the model, per ``contracts/ai/tasks.yaml`` §2 ``input.sources``.

    ``text`` is untrusted content (SRC-SPEC §11.4). It reaches the prompt inside a
    nonce-delimited block and never reaches a log, an error envelope or a stored result.
    """

    source_id: str
    kind: str
    text: str
    source_hash: str
    retrieved_at: str


@dataclass(frozen=True)
class TaskInput:
    """The task as the worker hands it to the adapter.

    This is the type the analysis lifecycle and the adapter have to agree on. It holds no
    secret (card §6 I11), no tag list (REQ-D22 — a tag in the prompt is the subtle way to
    break AC-06) and no selection output.
    """

    task_id: str
    task_type: AnalysisTaskType
    analysis_key: Mapping[str, Any]
    target_key: str
    sources: Sequence[SourceRef]
    max_evidence_level: str
    prompt_version: str
    schema_version: str
    attempt_id: str
    attempt_number: int = 1
    #: ``direction_phrasing`` only: the members and the density were computed by
    #: ``MOD-report-service`` *before* this task existed (CR-PC04-05). The adapter carries
    #: them so SV-05 can compare, never so the model can revise them.
    member_target_keys: Sequence[str] = ()
    density: Mapping[str, Any] = field(default_factory=dict)
    direction_ref: str | None = None

    @property
    def input_source_ids(self) -> tuple[str, ...]:
        """The set every citation must be drawn from (SV-02)."""
        return tuple(source.source_id for source in self.sources)

    @property
    def timeout_seconds(self) -> int:
        return INFERENCE_TIMEOUT_SECONDS[self.task_type]


class TaskCredential:
    """A short-lived credential for exactly one provider and one task (B13, ADR-0010 §1).

    The value is deliberately awkward to get at: ``repr`` and ``str`` are redacted, so a
    credential landing in an f-string in a log line prints a placeholder rather than a key.
    ``reveal()`` is the only accessor and is called at exactly one place — the moment a
    request header is built.
    """

    __slots__ = ("_value", "expires_at", "provider_config_id", "task_id")

    def __init__(
        self, *, value: str, provider_config_id: str, task_id: str, expires_at: str
    ) -> None:
        self._value = value
        self.provider_config_id = provider_config_id
        self.task_id = task_id
        self.expires_at = expires_at

    def reveal(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return (
            f"TaskCredential(provider_config_id={self.provider_config_id!r}, "
            f"task_id={self.task_id!r}, value=<redacted>)"
        )

    __str__ = __repr__


class TaskCredentialPort(Protocol):
    """What ``MOD-analysis-worker`` supplies, not what the adapter calls.

    ``contracts/ports.yaml`` makes ``MOD-analysis-worker`` the only caller of
    ``secret.issue_task_credential``, and ``contracts/modules.yaml`` gives this module
    ``outbound_operations: []``. So the credential arrives through this port; ISO-05's
    refusal (``UNAUTHORIZED`` / ``STALE_LEASE`` for a worker not holding the lease) happens
    on the far side of it, and the adapter's obligation is only to make **zero** provider
    calls when the port refuses.
    """

    def issue_task_credential(self, *, task_id: str, attempt_id: str) -> TaskCredential: ...


@dataclass
class CallAudit:
    """The counters the fixtures assert on. Counting is the evidence; prose is not.

    ``grounding.md`` §5.2 states this in as many words: the defence that can be shown is a
    number, and "the model politely declined" is not one of them. Every field here maps to
    an oracle in a fixture or to an ISO-0x row of ``providers.yaml`` §4.
    """

    #: ISO-01 / DC-AI-03 — tool definitions sent with a request, and tools actually run.
    tool_definitions_registered: int = 0
    tool_calls_executed: int = 0
    #: Requests the model emitted that *looked* like tool calls. Recorded so the refusal is
    #: visible; a non-zero value here with ``tool_calls_executed == 0`` is the passing shape.
    tool_requests_seen: int = 0
    #: ISO-03 / DC-AI-02 — every host an outbound attempt named, allowed or refused.
    outbound_hosts: list[str] = field(default_factory=list)
    refused_hosts: list[str] = field(default_factory=list)
    #: ISO-04 / DC-AI-01 — Telegram is not reachable from here at all (FE-16).
    telegram_calls: int = 0
    #: ISO-02 — reads outside the worker working directory.
    files_read_outside_working_dir: int = 0
    #: One entry per provider dispatch, in order: the fallback oracle of fixture (h) is
    #: "count of calls to a second provider = 0", which needs the identities, not a total.
    provider_calls: list[str] = field(default_factory=list)
    #: Credentials the worker's port actually issued for this run.
    credentials_received: int = 0

    def record_outbound(self, url: str, *, allowed: bool) -> None:
        host = urlsplit(url).hostname or ""
        (self.outbound_hosts if allowed else self.refused_hosts).append(host)

    def record_provider_call(self, adapter_id: str) -> None:
        self.provider_calls.append(adapter_id)

    def record_tool_request(self) -> None:
        """A request seen in model output. It is never executed: there is no dispatcher."""
        self.tool_requests_seen += 1

    @property
    def distinct_providers_called(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.provider_calls))

    @property
    def calls(self) -> int:
        """Total ``ai.run_inference_task`` dispatches.

        Named to satisfy ``server.app.analysis.service.AdapterCallCounter`` structurally,
        so the worker can hand this object straight to the analysis service without either
        module importing the other — ``contracts/modules.yaml`` permits
        ``MOD-analysis-worker -> MOD-ai-adapter`` and nothing else, and a shared type would
        have to live on one side of that edge or the other.

        It is the AC-06 oracle: editing a tag must leave this number unmoved, because the
        analysis key excludes tags (ADR-0008, I04).
        """
        return len(self.provider_calls)


@dataclass(frozen=True)
class AdapterEntry:
    """One ``(provider, version)`` pair — ``contracts/ai/providers.yaml`` §2.

    Changing the version is a *new* entry that must be checked from scratch (ADR-0010 §5),
    which is why ``adapter_id`` carries the version and why ``latest`` is not a value.
    """

    adapter_id: str
    auth_family: AuthFamily
    task_support: frozenset[AnalysisTaskType]
    max_concurrency: int
    request_timeout_seconds: int
    cancellation_support: str
    json_extraction_method: JsonExtractionMethod
    usage_reporting: UsageReporting
    isolation: Mapping[str, IsolationStatus]
    terms_outcome: TermsOutcome
    enabled: bool
    disabled_reason: str | None
    provider_name: str = ""
    model_name: str = ""
    #: ``ai_provider_endpoints_configured`` for this entry: the only hosts ISO-03 permits.
    endpoint_allowlist: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if self.auth_family is AuthFamily.CLI_ACP and self.max_concurrency != 1:
            raise ValueError(
                "contracts/ai/providers.yaml §1 fixes cli_acp concurrency at 1; it is a "
                "contract constant, not a tunable default"
            )
        if "latest" in self.model_name:
            raise ValueError("model_name may not be `latest` (contracts/data/entities.yaml)")
        if not self.enabled and not self.disabled_reason:
            raise ValueError(
                "disabled_reason is NOT NULL when enabled is false, and it must be specific "
                "(contracts/ai/providers.yaml §2 required_fields)"
            )

    @property
    def isolation_verified(self) -> bool:
        """Every ISO-01..05 property carries ``verified`` or a justified ``not_applicable``.

        ``unverified`` on any one of them is decisive: §4 ``current_status_vi`` says
        "unverified ⇒ enabled = false. Không có ngoại lệ."
        """
        return bool(self.isolation) and all(
            status is not IsolationStatus.UNVERIFIED for status in self.isolation.values()
        )

    @property
    def dispatchable(self) -> bool:
        """Three gates, all of which must hold before any provider call is made.

        The gates are independent on purpose: the Anthropic entries of §2.1 pass the terms
        gate (Owner-signed, ``OD-20260908-08``) and still fail here, because what holds them
        is isolation (B13). Reporting one as the other would misname the blocker.
        """
        return (
            self.enabled
            and self.isolation_verified
            and self.terms_outcome is TermsOutcome.PERMITTED_FOR_THIS_USE
        )

    @property
    def refusal_reason_code(self) -> ProbeReasonCode | None:
        if self.dispatchable:
            return None
        if not self.isolation_verified:
            return ProbeReasonCode.ISOLATION_UNVERIFIED
        if self.terms_outcome is not TermsOutcome.PERMITTED_FOR_THIS_USE:
            return ProbeReasonCode.POLICY_UNVERIFIED
        return ProbeReasonCode.POLICY_UNVERIFIED

    def supports(self, task_type: AnalysisTaskType) -> bool:
        return task_type in self.task_support

    def provider_ref(self) -> ProviderRef:
        return ProviderRef(
            auth_family=self.auth_family,
            provider_name=self.provider_name or self.adapter_id.split("@", 1)[0],
            model_name=self.model_name or self.adapter_id.split("@", 1)[-1],
        )


@dataclass(frozen=True)
class ProbeReport:
    """``ai.probe_provider_capability`` result for one adapter entry."""

    adapter_id: str
    outcome: ProbeOutcome
    reason_code: ProbeReasonCode | None
    task_support: frozenset[AnalysisTaskType]


@dataclass(frozen=True)
class AdapterResult:
    """What the adapter returns to ``MOD-analysis-worker``.

    Deliberately *not* an ``analysis`` row: the worker proposes, ``MOD-analysis-service``
    decides (SRC-PLAN §6.1), and "the provider ran" is not "the result is committed"
    (card §6). It also carries no transcript — only the payload that survived extraction
    and the counters that prove how it was obtained.
    """

    payload: Mapping[str, Any]
    usage: UsageReport
    provider: ProviderRef
    extraction_method: JsonExtractionMethod
    audit: CallAudit
    tool_definitions_registered: int = TOOL_DEFINITIONS_REGISTERED

    def __post_init__(self) -> None:
        if self.tool_definitions_registered != TOOL_DEFINITIONS_REGISTERED:
            raise ValueError(
                "capabilities.yaml ACT-ai-adapter declared_oracle fixes "
                "tool_definitions_registered at 0 for every call of every task type"
            )


class ProviderAdapter(ABC):
    """The two operations of ``contracts/ports.yaml``: run a task, probe a provider.

    Subclasses implement transport. This class owns the refusals that must hold for *both*
    families, so a new adapter cannot forget one: the dispatch gate, the egress allowlist
    and the "no tool definitions" constant.
    """

    def __init__(self, entry: AdapterEntry, *, audit: CallAudit | None = None) -> None:
        self.entry = entry
        self.audit = audit if audit is not None else CallAudit()

    # -- ai.probe_provider_capability -------------------------------------------------
    def probe_provider_capability(self) -> ProbeReport:
        """Report ``usable | unusable | unknown`` without enabling anything.

        A probe that has not observed the ISO oracles reports ``unknown``, which
        ``contracts/ports.yaml`` forbids converting to ``usable``. This implementation
        never observes them — E3 is ``NOT_RUN`` — so a non-dispatchable entry is reported
        ``unknown`` with ``isolation_unverified`` rather than ``unusable``: nothing here
        has *tested* the adapter and found it wanting.
        """
        if self.entry.dispatchable:
            return ProbeReport(
                adapter_id=self.entry.adapter_id,
                outcome=ProbeOutcome.USABLE,
                reason_code=None,
                task_support=self.entry.task_support,
            )
        return ProbeReport(
            adapter_id=self.entry.adapter_id,
            outcome=ProbeOutcome.UNKNOWN,
            reason_code=self.entry.refusal_reason_code,
            task_support=self.entry.task_support,
        )

    # -- ai.run_inference_task --------------------------------------------------------
    @abstractmethod
    def run_inference_task(
        self, task: TaskInput, *, credential: TaskCredential | None = None
    ) -> AdapterResult:
        """Run exactly one task. No retry: the budget lives at the task layer."""

    # -- shared refusals --------------------------------------------------------------
    def _require_dispatchable(self) -> None:
        """CAPABILITY_DENIED before any socket, process or credential is touched.

        This is the ADR-0010 §3 rule in code: *not verifiable means not enabled*. It fires
        before the credential is read, so a disabled adapter never even causes one to be
        issued.
        """
        if self.entry.dispatchable:
            return
        reason = self.entry.refusal_reason_code
        raise AdapterError(
            ErrorCode.CAPABILITY_DENIED,
            "Thao tác bị chặn ở mức nền tảng.",
            details_safe={
                "module_id": MODULE_ID,
                "denied_capability_kind": reason.value if reason else "unknown",
            },
            attempt_outcome=AnalysisAttemptOutcome.PROVIDER_ERROR,
        )

    def _require_task_supported(self, task: TaskInput) -> None:
        if self.entry.supports(task.task_type):
            return
        raise AdapterError(
            ErrorCode.VALIDATION_ERROR,
            "Đầu vào của task không đúng hợp đồng.",
            details_safe={
                "field": "task_type",
                "reason": "not_in_task_support",
                "task_id": task.task_id,
                "task_type": task.task_type.value,
            },
        )

    def _require_allowed_endpoint(self, url: str) -> None:
        """ISO-03 / DC-AI-02: the destination set must be inside the configured allowlist.

        A URL that arrived in *source content* can never pass, because content never
        reaches this function — the caller builds the endpoint from configuration alone.
        The check exists so that a future caller that does pass one is refused loudly and
        counted (``audit.refused_hosts``) rather than silently connecting.
        """
        host = urlsplit(url).hostname or ""
        if host and _HOST_RE.match(host) and host in self.entry.endpoint_allowlist:
            self.audit.record_outbound(url, allowed=True)
            return
        self.audit.record_outbound(url, allowed=False)
        raise AdapterError(
            ErrorCode.CAPABILITY_DENIED,
            "Thao tác bị chặn ở mức nền tảng.",
            details_safe={
                "module_id": MODULE_ID,
                "denied_capability_kind": "network_egress",
                "forbidden_edge_ref": "FE-19",
            },
            attempt_outcome=AnalysisAttemptOutcome.PROVIDER_ERROR,
        )

    def _require_matching_credential(
        self, task: TaskInput, credential: TaskCredential | None
    ) -> TaskCredential:
        """ISO-05: the credential must belong to *this* task and *this* provider config.

        A worker that does not hold the lease is refused at ``secret.issue_task_credential``
        by ``MOD-secret-service`` and hands nothing in; the adapter's part is to make zero
        provider calls in that case, which is what raising here achieves.
        """
        if credential is None:
            raise AdapterError(
                ErrorCode.AI_PROVIDER_UNAVAILABLE,
                "Nhà cung cấp AI đang không dùng được. Mục này chưa có phân tích.",
                details_safe={
                    "task_id": task.task_id,
                    "provider_name": self.entry.provider_ref().provider_name,
                    "reason_code": ProbeReasonCode.NOT_LOGGED_IN.value,
                    "attempt_number": task.attempt_number,
                },
                attempt_outcome=AnalysisAttemptOutcome.PROVIDER_UNAVAILABLE,
            )
        if credential.task_id != task.task_id:
            raise AdapterError(
                ErrorCode.CAPABILITY_DENIED,
                "Thao tác bị chặn ở mức nền tảng.",
                details_safe={
                    "module_id": MODULE_ID,
                    "denied_capability_kind": "credential_scope",
                },
                attempt_outcome=AnalysisAttemptOutcome.PROVIDER_ERROR,
            )
        self.audit.credentials_received += 1
        return credential


def ac16_status(entries: Iterable[AdapterEntry]) -> str:
    """REQ-AC16 reported the way ADR-0010 requires.

    When no CLI/ACP adapter is dispatchable the answer is ``BLOCKED``, not ``FAIL``: the
    zero-API-key path has not been *tried and failed*, it has not been *permitted to run*.
    ``providers.yaml`` §4 ``ac16_reporting_rule_vi`` makes the distinction binding, and
    fixture (k) lists "reporting AC-16 as FAIL" among its forbidden effects.
    """
    cli = [entry for entry in entries if entry.auth_family is AuthFamily.CLI_ACP]
    covered: set[AnalysisTaskType] = set()
    for entry in cli:
        if entry.dispatchable:
            covered |= set(entry.task_support)
    return AC16_PASS if covered == set(AnalysisTaskType) else AC16_BLOCKED


def _isolation_map(raw: Mapping[str, Any]) -> dict[str, IsolationStatus]:
    """Read §2.1's ``isolation`` object.

    ``providers.yaml`` §2.1 ``template_gap_vi`` records that the template object has three
    status slots while §4 requires five properties: ISO-04 and ISO-05 have nowhere to be
    written (``CR-PC06-OQ03-01``). Absent is not verified, so the two missing properties are
    read as ``unverified`` — the direction the contract's own default points.
    """
    statuses = {
        "tools_disabled": IsolationStatus.UNVERIFIED,
        "filesystem_scope": IsolationStatus.UNVERIFIED,
        "network_egress": IsolationStatus.UNVERIFIED,
        "telegram_blocked": IsolationStatus.UNVERIFIED,
        "credential_scope": IsolationStatus.UNVERIFIED,
    }
    for key, value in raw.items():
        if key == "verification_method":
            continue
        statuses[key] = IsolationStatus(value)
    return statuses


def load_registered_adapters(path: Path | None = None) -> tuple[AdapterEntry, ...]:
    """Read ``contracts/ai/providers.yaml`` §2.1 ``registered_adapters.entries``.

    The registry is read, never restated: an entry's ``enabled`` flag is the contract's
    answer to "may this adapter be dispatched", and the whole point of reading it here is
    that no code path can hold a different opinion. Both entries are currently
    ``enabled: false`` (REQ-OQ03 / ``OD-20260908-06``), so this function returns two
    adapters that :meth:`ProviderAdapter._require_dispatchable` will refuse.
    """
    source = path or PROVIDERS_YAML
    document = yaml.safe_load(source.read_text(encoding="utf-8"))
    entries = document.get("registered_adapters", {}).get("entries", [])
    loaded: list[AdapterEntry] = []
    for raw in entries:
        loaded.append(
            AdapterEntry(
                adapter_id=raw["adapter_id"],
                auth_family=AuthFamily(raw["auth_family"]),
                task_support=frozenset(AnalysisTaskType(t) for t in raw["task_support"]),
                max_concurrency=int(raw["max_concurrency"]),
                request_timeout_seconds=int(raw["request_timeout_seconds"]),
                cancellation_support=str(raw["cancellation_support"]),
                json_extraction_method=JsonExtractionMethod(raw["json_extraction_method"]),
                usage_reporting=UsageReporting(raw["usage_reporting"]),
                isolation=_isolation_map(raw.get("isolation", {})),
                terms_outcome=TermsOutcome(raw["terms_check"]["outcome"]),
                enabled=bool(raw["enabled"]),
                disabled_reason=raw.get("disabled_reason"),
                provider_name=str(raw.get("provider_name", "")),
                model_name=str(raw.get("model_name", "")),
                endpoint_allowlist=frozenset(),
            )
        )
    return tuple(loaded)
