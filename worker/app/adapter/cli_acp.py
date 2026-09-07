"""The ``cli_acp`` family — a local CLI session, JSON lifted out of a transcript.

This path exists because REQ-D51 promises the system runs with **no API key at all**, and
REQ-AC16 only passes when all three tasks can go through it (embedding is local, REQ-D48/
D50). It is also the path with the sharper isolation problem: a vendor CLI normally reads
files, calls tools and reaches the network, and the content going into its prompt is
untrusted by definition (SRC-SPEC §11.4).

ADR-0010 answers that with a default rather than a mitigation: **not verifiable means not
enabled**. So this module ships complete and refuses to run. No CLI adapter has passed
``contracts/ops/cli-acp-probe.md`` §4 — every probe is ``NOT_RUN`` (E3) — so every entry
has ``isolation.* = unverified`` and :meth:`CliAcpAdapter.run_inference_task` raises
``CAPABILITY_DENIED`` before spawning anything.

The reporting rule that follows is the one thing most easily got wrong, so it lives in code
as well as prose: when every CLI adapter is disabled, **REQ-AC16 is ``BLOCKED``, not
``FAIL``** (:func:`worker.app.adapter.base.ac16_status`, ``providers.yaml`` §4
``ac16_reporting_rule_vi``). The zero-key path was not tried and found wanting; it was not
permitted to run.

Per the card's §9, this path's claim ceiling is ``CONTRACT_READY`` — the interface the
contract requires, with no probe behind it.
"""

from __future__ import annotations

import secrets
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import AnalysisAttemptOutcome

from worker.app.adapter.base import (
    MODULE_ID,
    TOOL_DEFINITIONS_REGISTERED,
    AdapterEntry,
    AdapterError,
    AdapterResult,
    AuthFamily,
    CallAudit,
    JsonExtractionMethod,
    ProbeReasonCode,
    ProviderAdapter,
    TaskCredential,
    TaskInput,
    UsageReport,
)
from worker.app.adapter.extract_json import (
    ExtractionError,
    assert_nonce_absent_from_sources,
    envelope_marker,
    extract_json,
)
from worker.app.adapter.validate import validate_result

#: 32 hex characters. The nonce must be unguessable from the transcript, because the whole
#: soundness of ``delimited_envelope`` is that source content cannot forge an envelope.
NONCE_BYTES: int = 16


@dataclass(frozen=True)
class CliInvocation:
    """The process the adapter would start, described rather than started.

    ``tools_enabled``, ``network_enabled`` and ``filesystem_scope`` are recorded on the
    invocation so that a probe run has something to *observe*: ``providers.yaml`` §4 says a
    property that cannot be observed is not verified, and a flag that only exists inside a
    subprocess call is not observable.
    """

    argv: tuple[str, ...]
    prompt: str
    timeout_seconds: int
    tools_enabled: bool = False
    network_enabled: bool = False
    filesystem_scope: str = "worker_working_dir"
    tool_definitions_registered: int = TOOL_DEFINITIONS_REGISTERED


@dataclass(frozen=True)
class CliTranscript:
    """What the CLI printed, plus the counters a probe needs.

    ``text`` is the transcript. It goes to :func:`extract_json` and nowhere else: not to a
    log, not into an error envelope, not into the returned result
    (``errors.yaml`` ``AI_OUTPUT_INVALID.redaction_vi``).
    """

    text: str
    tool_requests: int = 0
    tool_calls_executed: int = 0
    files_read_outside_working_dir: int = 0


class CliRunner(Protocol):
    """Starts the CLI. ``subprocess`` in production; recorded in tests.

    Injected for the same reason the HTTP transport is: the only code that can spawn a
    process is code the caller supplied, so "no process was started" is a property a test
    can assert rather than trust.
    """

    def run(self, invocation: CliInvocation) -> CliTranscript: ...


class CliUnavailable(Exception):
    """The CLI could not run at all — binary missing, not logged in, or timed out."""

    def __init__(self, reason_code: ProbeReasonCode) -> None:
        super().__init__(reason_code.value)
        self.reason_code = reason_code


class CliAcpAdapter(ProviderAdapter):
    """``ai.run_inference_task`` over a local CLI/ACP session.

    Refuses a credential outright. ``providers.yaml`` §1 and REQ-D51 put ``secret_ref`` at
    ``NULL`` for this family and ADR-0010 §7 keeps the CLI's login session on the personal
    machine — the server never receives it. An adapter that accepted a key here would
    quietly turn the zero-key path into a keyed one.
    """

    def __init__(
        self,
        entry: AdapterEntry,
        *,
        runner: CliRunner,
        argv: Sequence[str] = (),
        audit: CallAudit | None = None,
    ) -> None:
        if entry.auth_family is not AuthFamily.CLI_ACP:
            raise ValueError(
                f"{entry.adapter_id} is {entry.auth_family.value}; CliAcpAdapter serves the "
                f"cli_acp family only (contracts/ai/providers.yaml §1)"
            )
        super().__init__(entry, audit=audit)
        self._runner = runner
        self._argv = tuple(argv)

    def run_inference_task(
        self, task: TaskInput, *, credential: TaskCredential | None = None
    ) -> AdapterResult:
        """Refuse while the entry is not dispatchable; otherwise run once and extract.

        The first line is the whole of B13. It runs before the nonce is drawn and before
        the runner is touched, so a disabled entry produces no process, no prompt and no
        transcript — which is what makes ``CAPABILITY_DENIED``'s "đếm outbound call = 0"
        oracle true by construction rather than by inspection.
        """
        self._require_dispatchable()
        self._require_task_supported(task)
        if credential is not None:
            raise AdapterError(
                ErrorCode.CAPABILITY_DENIED,
                "Thao tác bị chặn ở mức nền tảng.",
                details_safe={
                    "module_id": MODULE_ID,
                    "denied_capability_kind": "credential_scope",
                },
                attempt_outcome=AnalysisAttemptOutcome.PROVIDER_ERROR,
            )

        nonce = secrets.token_hex(NONCE_BYTES)
        assert_nonce_absent_from_sources(nonce, [source.text for source in task.sources])
        invocation = self._build_invocation(task, nonce)
        self.audit.tool_definitions_registered = invocation.tool_definitions_registered
        self.audit.record_provider_call(self.entry.adapter_id)

        try:
            transcript = self._runner.run(invocation)
        except CliUnavailable as exc:
            raise self._unavailable(task, exc.reason_code) from exc

        for _ in range(transcript.tool_requests):
            self.audit.record_tool_request()
        self.audit.tool_calls_executed += transcript.tool_calls_executed
        self.audit.files_read_outside_working_dir += transcript.files_read_outside_working_dir

        method = self.entry.json_extraction_method
        try:
            payload = extract_json(transcript.text, method, nonce=nonce)
        except ExtractionError as exc:
            raise exc.failure.as_error(
                task_id=task.task_id,
                task_type=task.task_type.value,
                attempt_number=task.attempt_number,
            ) from exc

        validate_result(payload, task)
        return AdapterResult(
            payload=payload,
            usage=UsageReport.unknown_usage(),
            provider=self.entry.provider_ref(),
            extraction_method=method,
            audit=self.audit,
        )

    # -- helpers ----------------------------------------------------------------------
    def _build_invocation(self, task: TaskInput, nonce: str) -> CliInvocation:
        marker = envelope_marker(nonce)
        blocks = "\n".join(
            f"{marker}source id={source.source_id}\n{source.text}\n{marker}"
            for source in task.sources
        )
        prompt = (
            f"Trả về đúng một JSON object cho task {task.task_type.value}, "
            f"bọc giữa {marker} và {marker}.\n{blocks}"
        )
        return CliInvocation(
            argv=self._argv,
            prompt=prompt,
            timeout_seconds=min(task.timeout_seconds, self.entry.request_timeout_seconds),
            tools_enabled=False,
            network_enabled=False,
            filesystem_scope="worker_working_dir",
        )

    def _unavailable(self, task: TaskInput, reason: ProbeReasonCode) -> AdapterError:
        """Usage is ``unknown`` here and stays so: nothing ran, and nothing is 0."""
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


def default_extraction_method() -> JsonExtractionMethod:
    """``delimited_envelope`` — the only one source content cannot forge.

    ``fenced_block`` is legal in ``providers.yaml`` §3 and is supported by
    :func:`worker.app.adapter.extract_json.extract_json`, but a fence is a string an
    attacker can also write. A per-run nonce is not, which is why this is the default rather
    than a preference.
    """
    return JsonExtractionMethod.DELIMITED_ENVELOPE
