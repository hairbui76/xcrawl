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
