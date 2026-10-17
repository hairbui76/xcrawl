"""The ``api_key`` family — HTTP to a configured provider endpoint, one task per call.

``contracts/ai/providers.yaml`` §1 gives this family three properties that shape the code:
the key lives in the server's secret store and reaches the worker **per task** (B13), the
response is JSON with no extraction step (``native_json``), and usage is reported exactly.

Two entries are registered in §2.1 — ``anthropic@claude-sonnet-5`` and
``anthropic@claude-opus-5`` — and **both carry ``enabled: false``**. Terms are not what
holds them (Owner signed ``OD-20260908-08``); isolation is: ISO-03 and ISO-05 are
properties the API path *creates* rather than removes, so neither can be marked
``not_applicable``, and verifying them needs a run that has not happened (E3 ``NOT_RUN``).
:meth:`ApiProviderAdapter.run_inference_task` therefore refuses both before touching a
socket, and the test that proves it loads the real registry rather than a copy.

The transport is injected. There is no default that reaches the network: a caller must hand
in something that satisfies :class:`ProviderTransport`, and the tests hand in a recorded
one. That is not a testing convenience — it is how "no egress except the configured
endpoint" stays checkable, since the only code that can open a socket is code the caller
supplied.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import AnalysisAttemptOutcome

from worker.app.adapter.base import (
    MODULE_ID,
    TOOL_DEFINITIONS_REGISTERED,
    AdapterEntry,
    AdapterError,
    AdapterResult,
    CallAudit,
    JsonExtractionMethod,
    ProbeReasonCode,
    ProviderAdapter,
    TaskCredential,
    TaskInput,
    UsageReport,
)
from worker.app.adapter.extract_json import ExtractionError, extract_json
from worker.app.adapter.validate import validate_result

#: The header a per-task credential is placed in, and the only place :meth:`reveal` is
#: called. Keeping that call site singular is what makes "the key is never logged" a claim
#: about one line rather than about a coding habit.
_CREDENTIAL_HEADER: Final[str] = "authorization"


@dataclass(frozen=True)
class ProviderRequest:
    """Exactly what goes on the wire, so a test can count what is in it.

    ``tools`` is present and always empty. An absent key would be indistinguishable from a
    forgotten one; an empty list that a test asserts on is the ISO-01 oracle
    (``capabilities.yaml`` ``declared_oracle.tool_definitions_registered = 0``: "kiểm
    payload gửi tới provider, đếm mục tool/function = 0 ở **mọi** lời gọi").
    """

    url: str
    model: str
    system: str
    messages: tuple[Mapping[str, Any], ...]
    response_schema: Mapping[str, Any]
    timeout_seconds: int
    tools: tuple[Mapping[str, Any], ...] = ()

    @property
    def tool_definition_count(self) -> int:
        return len(self.tools)


@dataclass(frozen=True)
class ProviderResponse:
    """A provider reply, already separated into the parts the adapter may keep.

    ``body`` becomes the result; ``tool_requests`` is a count, not the requests themselves,
    because a request the adapter will never execute has no reason to be retained. The
    transcript is not a field at all — there is nowhere for it to be stored.
    """

    body: str
    tokens_in: int | None = None
    tokens_out: int | None = None
    tool_requests: int = 0


class ProviderTransport(Protocol):
    """A single round trip. Implemented by ``httpx`` in production, recorded in tests."""

    def send(self, request: ProviderRequest, *, credential: TaskCredential) -> ProviderResponse: ...


class ProviderUnavailable(Exception):
    """Raised by a transport that could not reach the provider at all.

    Separate from :class:`AdapterError` on purpose: the transport reports a fact ("the
    endpoint did not answer"), and the mapping of that fact onto a contract code and a
    retry budget belongs to the adapter, not to whoever wrote the transport.
    """

    def __init__(self, reason_code: ProbeReasonCode) -> None:
        super().__init__(reason_code.value)
        self.reason_code = reason_code


class ApiProviderAdapter(ProviderAdapter):
    """``ai.run_inference_task`` over the API-key path.

    Refuses, in this order: not dispatchable, task not supported by this entry, no matching
    per-task credential, endpoint outside the allowlist. Each refusal happens before the
    next thing is touched, so a disabled adapter never causes a credential to be issued and
    a credential for another task never reaches a socket.
    """

    def __init__(
        self,
        entry: AdapterEntry,
        *,
        transport: ProviderTransport,
        endpoint: str,
        system_prompt: str = "",
        audit: CallAudit | None = None,
    ) -> None:
        super().__init__(entry, audit=audit)
        self._transport = transport
        self._endpoint = endpoint
        self._system_prompt = system_prompt

    def run_inference_task(
        self, task: TaskInput, *, credential: TaskCredential | None = None
    ) -> AdapterResult:
        """One call, one task, zero retries.

        The retry budget lives at the task layer (``tasks.yaml`` §1 ``split_rule_vi``) so
        that ``COUNT(analysis_attempt)`` is a direct count of model calls. Retrying here
        would double the calls somewhere SQL cannot see them, which the contract lists among
        its forbidden behaviours.
        """
        self._require_dispatchable()
        self._require_task_supported(task)
        held = self._require_matching_credential(task, credential)
        self._require_allowed_endpoint(self._endpoint)

        request = self._build_request(task)
        if request.tool_definition_count != TOOL_DEFINITIONS_REGISTERED:
            raise AdapterError(
                ErrorCode.CAPABILITY_DENIED,
                "Thao tác bị chặn ở mức nền tảng.",
                details_safe={
                    "module_id": MODULE_ID,
                    "denied_capability_kind": "tool_registration",
                },
                attempt_outcome=AnalysisAttemptOutcome.PROVIDER_ERROR,
            )
        self.audit.tool_definitions_registered = request.tool_definition_count
        self.audit.record_provider_call(self.entry.adapter_id)

        try:
            response = self._transport.send(request, credential=held)
        except ProviderUnavailable as exc:
            raise self._unavailable(task, exc.reason_code) from exc

        for _ in range(response.tool_requests):
            # Counted, then ignored. There is no tool dispatcher on this path, which is why
            # `tool_calls_executed` stays 0 no matter what the model asked for (DC-AI-03,
            # capabilities.yaml `tool_calls_permitted: false`).
            self.audit.record_tool_request()

        try:
            payload = extract_json(response.body, JsonExtractionMethod.NATIVE_JSON)
        except ExtractionError as exc:
            raise exc.failure.as_error(
                task_id=task.task_id,
                task_type=task.task_type.value,
                attempt_number=task.attempt_number,
            ) from exc

        validate_result(payload, task)
        return AdapterResult(
            payload=payload,
            usage=self._usage(response),
            provider=self.entry.provider_ref(),
            extraction_method=JsonExtractionMethod.NATIVE_JSON,
            audit=self.audit,
        )

    # -- helpers ----------------------------------------------------------------------
    def _build_request(self, task: TaskInput) -> ProviderRequest:
        """Untrusted content goes in as delimited data, never as instruction.

        The blocks carry their ``source_id`` and are closed by the same nonce that opened
        them (``tasks.yaml`` §1 ``block_shape_vi``). The prompt wording is *not* the
        defence — ``grounding.md`` §5.2 is explicit that "ignore any instructions in the
        content" is a weak and unverifiable one. The defence is that there is no tool to
        call, one credential to hold, and a schema the answer must fit.
        """
        blocks = [
            {
                "role": "user",
                "content": (
                    f"<source id={source.source_id} hash={source.source_hash}>\n"
                    f"{source.text}\n"
                    f"</source id={source.source_id}>"
                ),
            }
            for source in task.sources
        ]
        return ProviderRequest(
            url=self._endpoint,
            model=self.entry.model_name or self.entry.adapter_id.split("@", 1)[-1],
            system=self._system_prompt,
            messages=tuple(blocks),
            response_schema={"task_type": task.task_type.value},
            timeout_seconds=min(task.timeout_seconds, self.entry.request_timeout_seconds),
            tools=(),
        )

    def _usage(self, response: ProviderResponse) -> UsageReport:
        """Exact token counts when the provider reported them, ``unknown`` otherwise.

        ``cost_micro_usd`` stays ``None`` in both branches: no sourced price table is in
        scope (``providers.yaml`` §2.1 ``usage_reporting_note_vi``, ``CR-PC06-OQ03-03``),
        and I14 forbids the alternative of writing ``0``.
        """
        if response.tokens_in is None or response.tokens_out is None:
            return UsageReport.unknown_usage()
        return UsageReport.exact(
            tokens_in=response.tokens_in, tokens_out=response.tokens_out, cost_micro_usd=None
        )

    def _unavailable(self, task: TaskInput, reason: ProbeReasonCode) -> AdapterError:
        """``AI_PROVIDER_UNAVAILABLE`` — a budget of its own, and no fallback.

        The wait budget is separate from the schema-retry budget precisely because no
        inference ran (``tasks.yaml`` §1 ``budgets_cited``). And no second provider is
        tried: ``providers.yaml`` §6 defaults fallback to *off*, and turning it on is the
        Owner's ordered allowlist, never an adapter's inference from a failure.
        """
        return AdapterError(
            ErrorCode.AI_PROVIDER_UNAVAILABLE,
            "Nhà cung cấp AI đang không dùng được. Mục này chưa có phân tích.",
            details_safe={
                "task_id": task.task_id,
                "provider_name": self.entry.provider_ref().provider_name,
                "reason_code": reason.value,
                "attempt_number": task.attempt_number,
            },
            attempt_outcome=AnalysisAttemptOutcome.PROVIDER_UNAVAILABLE,
        )


def credential_headers(credential: TaskCredential) -> dict[str, str]:
    """Build the auth header. The one place a credential value is read.

    Deliberately a free function rather than a method: a grep for ``reveal()`` in this
    package returns exactly this line, which is the check that "the key is never written to
    a log" can actually be performed (DC-AI-05).
    """
    return {_CREDENTIAL_HEADER: f"Bearer {credential.reveal()}"}


# --------------------------------------------------------------------------------------
# The production transport: Anthropic Messages API through the official SDK
# --------------------------------------------------------------------------------------

#: ``output_config.effort`` values the model accepts. A registry value outside this set is a
#: contract error, refused before any call rather than sent and rejected by the provider.
_EFFORT_LEVELS: Final[frozenset[str]] = frozenset({"low", "medium", "high", "xhigh", "max"})

#: Room for the model's thinking *and* the JSON answer. Thinking cannot be disabled on
#: ``claude-opus-5-5`` and counts toward ``max_tokens`` even though its text is not returned,
#: so a limit sized for the answer alone would cut answers off.
DEFAULT_MAX_TOKENS: Final[int] = 16000


class AnthropicTransport:
    """``ProviderTransport`` over the ``anthropic`` SDK — one ``messages.create`` per task.

    Four decisions, each forced by a contract line rather than taste:

    * ``max_retries=0``. :meth:`ApiProviderAdapter.run_inference_task` is "one call, one
      task, zero retries" so that ``COUNT(analysis_attempt)`` counts model calls; the SDK's
      default of two silent retries would make that count wrong where SQL cannot see it.
    * No ``tools`` are sent and no ``thinking`` field is set. ISO-01 is "0 tool definitions on
      every call"; thinking is always on for ``claude-opus-5-5`` and its depth is governed by
      ``output_config.effort``, which comes from the registry (``effort_by_task``).
    * No server-side ``fallbacks``. ``providers.yaml`` §6 keeps fallback off by default, and a
      result produced by a different model would not match the registered entry. A
      ``stop_reason: "refusal"`` therefore surfaces as a provider failure for this attempt.
    * The base URL is the request's URL, which the adapter has already checked against the
      entry's ``endpoint_allowlist`` (ISO-03). Nothing here reads an environment variable.
    """

    def __init__(
        self,
        *,
        effort_by_task: Mapping[str, str],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        client_factory: Any = None,
    ) -> None:
        unknown = {value for value in effort_by_task.values() if value not in _EFFORT_LEVELS}
        if unknown:
            raise ValueError(f"effort_by_task holds values the model does not accept: {unknown}")
        self._effort_by_task = dict(effort_by_task)
        self._max_tokens = max_tokens
        self._client_factory = client_factory

    def _client(self, *, api_key: str, base_url: str, timeout_seconds: int) -> Any:
        if self._client_factory is not None:
            return self._client_factory(
                api_key=api_key, base_url=base_url, timeout=timeout_seconds, max_retries=0
            )
        import anthropic

        return anthropic.Anthropic(
            api_key=api_key, base_url=base_url, timeout=float(timeout_seconds), max_retries=0
        )

    def send(self, request: ProviderRequest, *, credential: TaskCredential) -> ProviderResponse:
        import anthropic

        task_type = str(request.response_schema.get("task_type", ""))
        effort = self._effort_by_task.get(task_type)
        if effort is None:
            raise ValueError(f"no effort is registered for task type {task_type!r}")
        # The single credential read stays in `credential_headers` (DC-AI-05).
        api_key = credential_headers(credential)[_CREDENTIAL_HEADER].removeprefix("Bearer ")
        client = self._client(
            api_key=api_key, base_url=request.url, timeout_seconds=request.timeout_seconds
        )
        try:
            message = client.messages.create(
                model=request.model,
                max_tokens=self._max_tokens,
                system=request.system,
                messages=list(request.messages),
                output_config={"effort": effort},
            )
        except anthropic.APITimeoutError as exc:
            raise ProviderUnavailable(ProbeReasonCode.PROBE_TIMEOUT) from exc
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError) as exc:
            raise ProviderUnavailable(ProbeReasonCode.NOT_LOGGED_IN) from exc
        except (anthropic.RateLimitError, anthropic.APIConnectionError) as exc:
            raise ProviderUnavailable(ProbeReasonCode.PROBE_TIMEOUT) from exc
        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500:
                raise ProviderUnavailable(ProbeReasonCode.PROBE_TIMEOUT) from exc
            raise
        if message.stop_reason == "refusal":
            raise ProviderUnavailable(ProbeReasonCode.POLICY_UNVERIFIED)
        body = "".join(block.text for block in message.content if block.type == "text")
        tool_requests = sum(1 for block in message.content if block.type == "tool_use")
        usage = message.usage
        return ProviderResponse(
            body=body,
            tokens_in=getattr(usage, "input_tokens", None),
            tokens_out=getattr(usage, "output_tokens", None),
            tool_requests=tool_requests,
        )
