"""E1 -- the collector's stop vocabulary, checked against the contracts that define it.

Card ``TC-collector-checkpoint-resume`` §3 gives this file one job: "ánh xạ stop_reason ↔
error code". The mapping tables live in :mod:`collector.app.client`; this module asserts them
against ``contracts/ports.yaml``, ``contracts/state/run.yaml`` and ``contracts/errors.yaml``
rather than against a second copy written here. A test that restates the table it is
checking proves only that someone typed it twice.

Four things get measured, all of them by comparison with a contract file or a fixture:

1. **The vocabulary.** The eight values the collector may send are exactly the eight
   ``contracts/ports.yaml`` lists for ``worker.report_stop``, and each maps to a
   ``run.stop_reason`` that exists in ``contracts/state/run.yaml``. The two vocabularies are
   *not* the same, and three pairs differ -- that difference is the thing most likely to be
   got wrong silently.
2. **The codes.** Every error code the collector raises is a member of the generated
   ``ErrorCode`` enum, and every one of them is registered against ``worker.report_stop`` in
   ``contracts/errors.yaml``. ``limit_reached`` maps to *no* code, which ``AMD-B02`` requires
   and which I13 makes load-bearing.
3. **The destinations.** Each stop reason lands the run where ``run.yaml`` says: a challenge
   in ``needs_user``, a rate limit in ``running/enriching`` and explicitly **not**
   ``blocked`` (stop gate ``SG-RATE``), a layout change in ``blocked`` with its own code.
4. **The client's shape.** It has methods for the nine operations card §4 permits and for
   nothing else -- the structural form of default deny (``SG-DENY``, SC49).

Scenarios: SC01, SC03, SC11, SC20, SC21, SC49, SC50.

Fixtures used as data: ``collection/a-feed-layout-changed``, ``collection/e-limit-reached-stop``,
``collection/b-cursor-invalidated-reread-dedup``, ``collection/d-duplicate-ingest-replay``,
``collection/f-two-workers-claim-same-assignment``, ``collection/g-schedule-due-claim``.

Nothing here touches X, a browser, a network socket or a database. The HTTP layer is an
``httpx.MockTransport`` replaying fixture bodies, which is exactly what
``acceptance/fixtures/collection/README.md`` says those files are for: "Chúng ghi lại hợp
đồng dây ... nên một test harness có thể phát lại chúng bằng một server giả".
"""

from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any

import httpx
import pytest
import yaml
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.states import RunStopReason

from collector.app.batcher import (
    Batcher,
    CheckpointProposal,
    batch_idempotency_key,
    compute_payload_hash,
)
from collector.app.client import (
    STOP_REASON_ERROR_CODE,
    WIRE_TO_RUN_STOP_REASON,
    CollectorClient,
    OutcomeUnknown,
    ServerError,
    WireStopReason,
    new_ulid,
)
from collector.app.limits import (
    PER_RUN_DURATION_LIMIT_S,
    PER_RUN_POST_LIMIT,
    LimitKind,
    SegmentBudget,
)
from collector.app.reader import (
    REQUIRED_ITEM_FIELDS,
    SIGNAL_STOP_REASON,
    FeedPage,
    SourceSignal,
    parse_page,
    parse_post,
    requires_owner_action,
    resume_position,
)
from collector.app.session import (
    ChromeProfile,
    CollectorSession,
    ProfileRefused,
    XSessionState,
    is_default_profile_dir,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
COLLECTOR_TOKEN = "collector-token-for-tests-only-not-a-secret"
ASSIGNMENT_ID = "KZA8XXCYQBY4190TVQJ05NMPZ3"
LEASE_ID = "08ZSTPHZ4MKNY25V807H2ESQCC"
JOB_ID = "DHMAQFP0HX86VVAWN9W2Z7YRSN"
RUN_ID = "6PNQ047XA29K4GVSEEXF8WFNJT"


# --------------------------------------------------------------------------- contract loaders


@pytest.fixture(scope="module")
def ports() -> dict[str, Any]:
    return yaml.safe_load((REPO_ROOT / "contracts" / "ports.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def run_contract() -> dict[str, Any]:
    return yaml.safe_load(
        (REPO_ROOT / "contracts" / "state" / "run.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="module")
def errors_contract() -> dict[str, Any]:
    return yaml.safe_load((REPO_ROOT / "contracts" / "errors.yaml").read_text(encoding="utf-8"))


def operation(ports: dict[str, Any], operation_id: str) -> dict[str, Any]:
    for entry in ports["operations"]:
        if entry["operation_id"] == operation_id:
            return dict(entry)
    raise AssertionError(f"{operation_id} is not in contracts/ports.yaml")


def transition(run_contract: dict[str, Any], transition_id: str) -> dict[str, Any]:
    for entry in run_contract["transitions"]:
        if entry.get("id") == transition_id:
            return dict(entry)
    raise AssertionError(f"{transition_id} is not in contracts/state/run.yaml")


# --------------------------------------------------------------------------- 1. vocabulary


def test_wire_stop_vocabulary_is_exactly_the_one_ports_yaml_defines(ports: dict[str, Any]) -> None:
    """The eight values come from the contract, not from this package's imagination.

    ``worker.report_stop.request_summary_vi`` spells the set inline; the backticked tokens
    between the braces are the vocabulary. Extracting them is a little crude, but it reads
    the authority rather than a transcription of it, and a value added or renamed there
    fails here.
    """
    summary = operation(ports, "worker.report_stop")["request_summary_vi"]
    inside_braces = re.search(r"\{([^}]*)\}", summary)
    assert inside_braces is not None, "report_stop no longer states its stop_reason set"
    contract_values = set(re.findall(r"`([a-z_]+)`", inside_braces.group(1)))
    assert contract_values == {reason.value for reason in WireStopReason}


def test_every_wire_reason_maps_to_a_real_run_stop_reason(run_contract: dict[str, Any]) -> None:
    """``WIRE_TO_RUN_STOP_REASON`` is total, and its values exist in ``run.yaml``."""
    declared = set(run_contract["enums"]["stop_reason"]["values"])
    assert set(WIRE_TO_RUN_STOP_REASON) == set(WireStopReason)
    for wire, stored in WIRE_TO_RUN_STOP_REASON.items():
        assert stored.value in declared, f"{wire.value} maps to an unknown run.stop_reason"


def test_the_three_renamed_pairs_are_renamed_and_the_rest_are_not() -> None:
    """The wire vocabulary and the stored vocabulary differ in exactly three places.

    Pinning this stops a later "tidy-up" from making the two identical, which would break
    T-RUN-09 (``challenge_required`` -> ``captcha``) without any single change looking wrong.
    """
    renamed = {
        wire: stored
        for wire, stored in WIRE_TO_RUN_STOP_REASON.items()
        if wire.value != stored.value
    }
    assert renamed == {
        WireStopReason.CHALLENGE_REQUIRED: RunStopReason.CAPTCHA,
        WireStopReason.WORKER_SHUTDOWN: RunStopReason.WORKER_LOST,
        WireStopReason.LOCAL_STORAGE_UNAVAILABLE: RunStopReason.STORAGE_UNAVAILABLE,
    }


def test_reading_signals_that_are_not_stops_have_no_stop_reason() -> None:
    """``ok`` and ``end_of_feed`` are observations, not stops (I13).

    An exhausted feed is reported by releasing the assignment with ``completed_phase``; the
    wire vocabulary has no "finished" value, and giving one to ``end_of_feed`` would turn a
    normal completion into a stop reason an operator has to interpret.
    """
    assert SourceSignal.OK not in SIGNAL_STOP_REASON
    assert SourceSignal.END_OF_FEED not in SIGNAL_STOP_REASON
    assert set(SIGNAL_STOP_REASON.values()) <= set(WireStopReason)


# --------------------------------------------------------------------------- 2. error codes


def test_every_mapped_code_is_registered_for_report_stop(errors_contract: dict[str, Any]) -> None:
    """No invented codes: each one is in ``contracts/errors.yaml`` and lists the operation."""
    registered = {entry["code"]: entry for entry in errors_contract["codes"]}
    for reason, code in STOP_REASON_ERROR_CODE.items():
        if code is None:
            continue
        assert code.value in registered, f"{code.value} is not in contracts/errors.yaml"
        operations = registered[code.value].get("operations") or []
        assert "worker.report_stop" in operations, (
            f"{code.value} is mapped to stop reason {reason.value} but errors.yaml does not "
            "list worker.report_stop among its operations"
        )


def test_limit_reached_and_worker_shutdown_carry_no_error_code() -> None:
    """Hitting a budget is not a failure (``AMD-B02``, T-RUN-02, I13).

    ``T-RUN-02.forbidden_vi`` forbids ``status = failed`` for this case in as many words.
    Giving ``limit_reached`` an error code is how that rule gets broken one layer down, in a
    UI that renders anything with a code as an error.
    """
    assert STOP_REASON_ERROR_CODE[WireStopReason.LIMIT_REACHED] is None
    assert STOP_REASON_ERROR_CODE[WireStopReason.WORKER_SHUTDOWN] is None


def test_challenge_and_session_expiry_share_one_code_by_contract(
    errors_contract: dict[str, Any],
) -> None:
    """``X_CHALLENGE_REQUIRED`` covers both, and the registry says so."""
    entry = next(e for e in errors_contract["codes"] if e["code"] == "X_CHALLENGE_REQUIRED")
    assert "phiên đã hết hạn" in entry["title_vi"]
    assert STOP_REASON_ERROR_CODE[WireStopReason.CHALLENGE_REQUIRED] is (
        ErrorCode.X_CHALLENGE_REQUIRED
    )
    assert STOP_REASON_ERROR_CODE[WireStopReason.SESSION_EXPIRED] is (
        ErrorCode.X_CHALLENGE_REQUIRED
    )


def test_layout_change_is_not_access_blocked() -> None:
    """Two different codes because the fix is different (CR-PC05-01, T-RUN-24).

    ``a-feed-layout-changed.forbidden_effects`` states the consequence of confusing them:
    using ``X_ACCESS_BLOCKED`` here "sẽ để một lỗi SỬA ĐƯỢC nằm chờ như một lỗi không sửa
    được".
    """
    assert (
        STOP_REASON_ERROR_CODE[WireStopReason.SOURCE_LAYOUT_CHANGED]
        is ErrorCode.SOURCE_LAYOUT_CHANGED
    )
    assert STOP_REASON_ERROR_CODE[WireStopReason.SOURCE_BLOCKED] is ErrorCode.X_ACCESS_BLOCKED
    assert (
        STOP_REASON_ERROR_CODE[WireStopReason.SOURCE_LAYOUT_CHANGED]
        != STOP_REASON_ERROR_CODE[WireStopReason.SOURCE_BLOCKED]
    )


# --------------------------------------------------------------------------- 3. destinations


def test_challenge_sends_the_run_to_needs_user(run_contract: dict[str, Any]) -> None:
    """T-RUN-09, and the alert intent is capped at one per run (REQ-AC04)."""
    row = transition(run_contract, "T-RUN-09")
    assert row["operation_id"] == "worker.report_stop"
    assert row["to"]["status"] == "needs_user"
    assert "challenge_required" in row["guard_vi"]
    assert any("TỐI ĐA MỘT alert" in effect for effect in row["effects_vi"])
    assert requires_owner_action_for(WireStopReason.CHALLENGE_REQUIRED)


def test_rate_limit_is_partial_not_blocked(run_contract: dict[str, Any]) -> None:
    """Stop gate ``SG-RATE``: rate limiting is ``partial``, never ``blocked``.

    T-RUN-25 sends the run to ``running/enriching`` and forbids ``blocked`` explicitly --
    "Đặt status = blocked: rate limit KHÔNG chặn đợt sau" -- because turning a condition
    that clears itself into one that needs a person is a real cost to the Owner. This test
    reads that row rather than restating it.
    """
    row = transition(run_contract, "T-RUN-25")
    assert row["to"]["status"] == "running"
    assert row["to"]["phase"] == "enriching"
    assert row["to"]["stop_reason"] == "rate_limited"
    assert any("blocked" in forbidden for forbidden in row["forbidden_vi"])
    assert "RATE_LIMITED" in row["error_codes"]
    assert STOP_REASON_ERROR_CODE[WireStopReason.RATE_LIMITED] is ErrorCode.RATE_LIMITED
    # And the collector does not wait for a person over a rate limit.
    assert not requires_owner_action_for(WireStopReason.RATE_LIMITED)


def test_rate_limit_is_never_retried_inside_the_same_run() -> None:
    """``contracts/retry-policy.yaml`` sets ``x_rate_limit_in_run_retries`` to 0.

    One of the few numbers in that file that is not PROVISIONAL: SRC-SPEC §9.3 is XN. The
    collector honours it structurally -- a rate-limit signal returns from the segment loop --
    so this test asserts the contract still says 0 rather than asserting on a log.
    """
    policy = yaml.safe_load(
        (REPO_ROOT / "contracts" / "retry-policy.yaml").read_text(encoding="utf-8")
    )
    budget = policy["budgets"]["x_rate_limit_in_run_retries"]
    assert budget["value"] == 0
    assert budget["status"] == "XN_derived"


def test_limit_reached_closes_the_segment_and_keeps_the_checkpoint(
    run_contract: dict[str, Any],
) -> None:
    """T-RUN-02: ``running/enriching``, checkpoint untouched, coverage note required."""
    row = transition(run_contract, "T-RUN-02")
    assert row["to"] == {"status": "running", "phase": "enriching"}
    assert "GIỮ NGUYÊN" in row["transaction_vi"]
    assert any("x_coverage_note_vi" in forbidden for forbidden in row["forbidden_vi"])


def test_layout_change_blocks_and_alerts(run_contract: dict[str, Any]) -> None:
    """T-RUN-24: ``blocked``, exactly one alert, and the missing field names recorded."""
    row = transition(run_contract, "T-RUN-24")
    assert row["to"]["status"] == "blocked"
    assert row["to"]["stop_reason"] == "source_layout_changed"
    assert "TÊN trường thiếu" in row["transaction_vi"]
    assert requires_owner_action_for(WireStopReason.SOURCE_LAYOUT_CHANGED)


def requires_owner_action_for(reason: WireStopReason) -> bool:
    """Helper: ask :func:`requires_owner_action` about a bare stop reason."""
    from collector.app.reader import Completion, SegmentOutcome

    return requires_owner_action(SegmentOutcome(completion=Completion.STOPPED, stop_reason=reason))


# --------------------------------------------------------------------------- 4. client shape


def test_client_exposes_only_the_operations_the_card_permits() -> None:
    """Default deny, made structural (``SG-DENY``, SC49, denied case NC-01).

    Card §4 lists nine operations and card §5 forbids every other edge -- notably
    ``MOD-x-collector -> MOD-saved-service``. A client with no ``save`` method cannot call
    ``save.create`` by accident, so the boundary is enforced by the code's shape and not
    only by the server's 401.
    """
    callable_names = {
        name
        for name, member in vars(CollectorClient).items()
        if not name.startswith("_") and inspect.isfunction(member)
    }
    assert callable_names == {
        "register_capabilities",
        "claim_assignment",
        "heartbeat",
        "report_stop",
        "release_assignment",
        "get_receipt",
        "submit_batch",
        "commit_checkpoint",
        "get_liveness",
        "close",
    }
    for forbidden in ("save", "create_save", "get_health", "storage", "analysis", "telegram"):
        assert not any(forbidden in name for name in callable_names)


# --------------------------------------------------------------------------- payload hashing


def test_payload_hash_agrees_with_the_server_implementation() -> None:
    """The collector's hash and the server's must be the same function.

    The collector package deliberately does not import the server one (card §5 default
    deny, ``SL-7``), so the two are independent implementations of
    ``ingest-batch.schema.json`` §payload_hash_definition. That freedom needs an oracle, and
    this is it: the *test* may import both, and does, so a divergence fails here instead of
    surfacing in production as an ``IDEMPOTENCY_CONFLICT`` on every ack-loss retry.
    """
    from server.app.ingest.idempotency import compute_payload_hash as server_hash

    batch = {
        "request_id": new_ulid(),
        "schema_version": "0.1.0",
        "idempotency_key": batch_idempotency_key(ASSIGNMENT_ID, 1, 1),
        "payload_hash": "",
        "job_id": JOB_ID,
        "lease_id": LEASE_ID,
        "lease_epoch": 1,
        "items": [
            {
                "x_post_id": "1900000000000000001",
                "author": {"handle": "acc1"},
                "url": "https://x.com/acc1/status/1900000000000000001",
                "text": "một bài về protein folding",
                "collected_at": "2026-09-07T08:00:00.000Z",
                "media_refs": [],
                "referenced_links": [],
            }
        ],
        "client_checkpoint_proposal": {
            "phase": "collecting",
            "cursor_token": "cursor-page-2",
            "cursor_state": "valid",
            "items_collected_in_run": 1,
            "stop_hint": "none",
        },
    }
    assert compute_payload_hash(batch) == server_hash(batch)


def test_payload_hash_ignores_request_id_but_not_items() -> None:
    """A retry mints a new ``request_id`` and must still hash the same (schema §x-contract)."""
    base = {
        "schema_version": "0.1.0",
        "items": [{"x_post_id": "1"}],
        "client_checkpoint_proposal": {"phase": "collecting", "cursor_state": "valid"},
    }
    with_request_id = {**base, "request_id": new_ulid(), "lease_epoch": 9}
    assert compute_payload_hash(base) == compute_payload_hash(with_request_id)

    changed_items = {**base, "items": [{"x_post_id": "2"}]}
    assert compute_payload_hash(base) != compute_payload_hash(changed_items)


def test_batch_idempotency_key_matches_the_schema_pattern() -> None:
    """``^[A-Za-z0-9_.:-]{16,128}$`` and, above all, deterministic."""
    schema = json.loads(
        (REPO_ROOT / "contracts" / "schemas" / "ingest-batch.schema.json").read_text("utf-8")
    )
    pattern = schema["properties"]["idempotency_key"]["pattern"]
    key = batch_idempotency_key(ASSIGNMENT_ID, 1, 1)
    assert re.match(pattern, key)
    assert key == batch_idempotency_key(ASSIGNMENT_ID, 1, 1)
    assert key != batch_idempotency_key(ASSIGNMENT_ID, 1, 2)


def test_batcher_refuses_to_build_an_empty_batch() -> None:
    """``items.minItems = 1``: the end of a segment is a stop operation, not an empty batch."""
    batcher = Batcher(assignment_id=ASSIGNMENT_ID, job_id=JOB_ID, lease_id=LEASE_ID, lease_epoch=1)
    proposal = CheckpointProposal(
        phase="collecting", cursor_token=None, cursor_state="valid", items_collected_in_run=0
    )
    assert batcher.build(request_id=new_ulid(), proposal=proposal) is None


# --------------------------------------------------------------------------- parsing


def test_parser_never_invents_a_missing_field() -> None:
    """I03 generalised by T-RUN-24: a missing required field yields *no item* and a name."""
    raw = {
        "x_post_id": "1900000000000000099",
        "author": {"id": "a1"},  # no handle
        "url": "https://x.com/acc1/status/1900000000000000099",
        "text": "bài không đọc được tác giả",
        # no published_at
    }
    item, missing = parse_post(raw, collected_at="2026-09-07T08:00:00.000Z")
    assert item is None
    assert missing == ["author.handle", "published_at"]
    assert set(missing) <= set(REQUIRED_ITEM_FIELDS)


def test_page_parse_keeps_the_readable_items_and_names_the_broken_fields() -> None:
    """``a-feed-layout-changed``: 12 of 40 parse, and the 12 are kept, not discarded."""
    good = {
        "x_post_id": "1900000000000000001",
        "author": {"handle": "acc1", "id": "a1"},
        "url": "https://x.com/acc1/status/1900000000000000001",
        "text": "đọc được",
        "published_at": "2026-09-07T07:50:00.000Z",
    }
    broken = {"x_post_id": "1900000000000000002", "author": {}, "url": "", "text": ""}
    parsed = parse_page(FeedPage(raw_posts=(good, broken)), collected_at="2026-09-07T08:00:00.000Z")
    assert parsed.posts_seen == 2
    assert parsed.posts_parsed_ok == 1
    assert parsed.failed_count == 1
    assert "author.handle" in parsed.missing_required_fields


# --------------------------------------------------------------------------- budget


def test_budget_defaults_come_from_the_retry_policy() -> None:
    """200 posts / 1800 s -- ACCEPTED working values (OD-20260907-01 item 20)."""
    policy = yaml.safe_load(
        (REPO_ROOT / "contracts" / "retry-policy.yaml").read_text(encoding="utf-8")
    )
    assert policy["budgets"]["per_run_post_limit"]["value"] == PER_RUN_POST_LIMIT
    assert policy["budgets"]["per_run_duration_limit"]["value"] == PER_RUN_DURATION_LIMIT_S


def test_budget_stops_on_whichever_threshold_comes_first() -> None:
    """``evaluation: first_of_either``, and ``limit_kind`` records which one."""
    clock = [0.0]
    budget = SegmentBudget(max_posts=10, max_duration_s=60, monotonic=lambda: clock[0])
    budget.start()
    budget.record_observed(9)
    assert budget.reached() is None

    clock[0] = 60.0
    assert budget.reached() is LimitKind.DURATION

    clock[0] = 0.0
    budget.record_observed(1)
    assert budget.reached() is LimitKind.POSTS


def test_coverage_note_is_never_empty_when_a_limit_is_hit() -> None:
    """T-RUN-02 forbids an empty ``x_coverage_note_vi`` when ``limit_hit`` is true."""
    budget = SegmentBudget(max_posts=200, max_duration_s=1800, monotonic=lambda: 0.0)
    budget.start()
    budget.record_observed(200)
    for kind in LimitKind:
        note = budget.coverage_note_vi(kind)
        assert note.strip()
        assert "KHÔNG được quét" in note


# --------------------------------------------------------------------------- session / D09


def test_default_chrome_profile_is_refused_with_capability_denied() -> None:
    """REQ-D09: the project's own profile, never the machine's default one."""
    for default in (
        Path.home() / ".config" / "google-chrome",
        Path("/Users/someone/Library/Application Support/Google/Chrome"),
        Path("C:/Users/someone/AppData/Local/Google/Chrome/User Data"),
    ):
        assert is_default_profile_dir(default)
        with pytest.raises(ProfileRefused) as raised:
            ChromeProfile(user_data_dir=default)
        assert raised.value.code is ErrorCode.CAPABILITY_DENIED

    project_profile = Path("/srv/research-radar/chrome-profile")
    assert not is_default_profile_dir(project_profile)
    assert ChromeProfile(user_data_dir=project_profile, ready=True).ready


def test_profile_error_never_leaks_an_absolute_path() -> None:
    """``error_envelope.forbidden_content_vi`` bars absolute personal-machine paths."""
    with pytest.raises(ProfileRefused) as raised:
        ChromeProfile(user_data_dir=Path.home() / ".config" / "chromium")
    assert "/" not in str(raised.value.details_safe["profile_dir_name"])
    assert str(Path.home()) not in str(raised.value.details_safe)


def test_capabilities_never_claim_embedding_and_never_promote_unknown() -> None:
    """``embedding_supported`` is ``const: false`` (B12/D50); ``unknown`` stays ``unknown``."""
    session = CollectorSession(
        worker_instance_id="FB6MS98AKQTGXNW6Q3EC11G2VF",
        profile=ChromeProfile(user_data_dir=Path("/srv/rr/profile"), ready=True),
    )
    assert session.capabilities()["embedding_supported"] is False
    assert session.capabilities()["x_session_state"] == XSessionState.UNKNOWN.value
    assert not session.may_claim(), "an unobserved session must not be treated as ok"
    assert session.observing(XSessionState.OK).may_claim()
    assert not session.observing(XSessionState.CHALLENGE).may_claim()


# --------------------------------------------------------------------------- fixture replays


def fixture(name: str) -> dict[str, Any]:
    path = REPO_ROOT / "acceptance" / "fixtures" / "collection" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def find_event(data: dict[str, Any], operation_id: str, index: int = 0) -> dict[str, Any]:
    matches = [e for e in data["events"] if e.get("operation") == operation_id]
    return dict(matches[index])


def client_over(handler: Any) -> CollectorClient:
    return CollectorClient(
        base_url="https://server.local",
        token=COLLECTOR_TOKEN,
        transport=httpx.MockTransport(handler),
        sleep=lambda _seconds: None,
    )


def test_ack_loss_looks_up_the_receipt_before_resending(  # SC21
) -> None:
    """``d-duplicate-ingest-replay``: timeout, then ``get_receipt``, then **no** resend.

    The forbidden effect the fixture names first is "Gửi lại mà chưa tra get_receipt". The
    oracle here is the request log: the POST that timed out is followed by a GET, and there
    is no second POST, because the receipt came back committed and the batch was already
    durable.
    """
    data = fixture("d-duplicate-ingest-replay")
    receipt_body = find_event(data, "ingest.get_receipt")["response_body"]
    calls: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.method == "POST":
            raise httpx.ReadTimeout("no response", request=request)
        return httpx.Response(200, json=receipt_body)

    with client_over(handler) as client:
        receipt = client.submit_batch(
            {"idempotency_key": "batch-2026-09-07-0001-aaaa", "items": []},
            assignment_id=ASSIGNMENT_ID,
        )

    assert [method for method, _ in calls] == ["POST", "GET"]
    assert calls[1][1].startswith("/v1/ingest/receipts/")
    assert receipt["status"] == "committed"
    assert receipt["receipt_hash"] == receipt_body["receipt"]["receipt_hash"]


def test_not_committed_is_the_only_answer_that_authorises_a_resend() -> None:
    """The other half of the ack-loss rule: ``not_committed`` -> resend under the same key."""
    calls: list[tuple[str, str]] = []
    posts = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append((request.method, request.url.path))
        if request.method == "POST":
            posts["n"] += 1
            if posts["n"] == 1:
                raise httpx.ConnectError("connection reset", request=request)
            assert request.headers["Idempotency-Key"] == "batch-2026-09-07-0001-aaaa"
            return httpx.Response(200, json={"receipt": {"status": "committed", "counts": {}}})
        return httpx.Response(
            200,
            json={
                "not_committed": {
                    "idempotency_key": "batch-2026-09-07-0001-aaaa",
                    "status": "not_committed",
                    "checked_at": "2026-09-07T08:00:00.000Z",
                    "safe_to_resubmit": True,
                }
            },
        )

    with client_over(handler) as client:
        receipt = client.submit_batch(
            {"idempotency_key": "batch-2026-09-07-0001-aaaa", "items": []},
            assignment_id=ASSIGNMENT_ID,
        )

    assert [method for method, _ in calls] == ["POST", "GET", "POST"]
    assert receipt["status"] == "committed"


def test_persistent_transport_failure_reports_unknown_rather_than_guessing() -> None:
    """When the outcome stays unknown, it is raised as unknown -- not as success or failure."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            raise httpx.ReadTimeout("no response", request=request)
        return httpx.Response(
            200, json={"not_committed": {"status": "not_committed", "safe_to_resubmit": True}}
        )

    with client_over(handler) as client, pytest.raises(OutcomeUnknown):
        client.submit_batch(
            {"idempotency_key": "batch-2026-09-07-0001-aaaa", "items": []},
            assignment_id=ASSIGNMENT_ID,
        )


def test_stale_lease_is_raised_and_carries_the_registry_code() -> None:  # SC20
    """``f-two-workers-claim-same-assignment``: the old epoch is refused, nothing changes."""
    data = fixture("f-two-workers-claim-same-assignment")
    envelope = find_event(data, "ingest.submit_batch")["response_body"]
    assert envelope["code"] == ErrorCode.STALE_LEASE.value

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json=envelope)

    with client_over(handler) as client, pytest.raises(ServerError) as raised:
        client.submit_batch(
            {"idempotency_key": "batch-2026-09-07-0001-aaaa", "items": []},
            assignment_id=ASSIGNMENT_ID,
        )
    assert raised.value.code is ErrorCode.STALE_LEASE
    assert raised.value.is_lease_lost
    assert raised.value.retry_class == "none"


def test_heartbeat_with_a_stale_epoch_is_refused() -> None:  # SC20
    """The same rejection on the heartbeat path (fixture ``f`` event 2)."""
    data = fixture("f-two-workers-claim-same-assignment")
    envelope = find_event(data, "worker.heartbeat")["response_body"]

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body["heartbeat_request"]["lease_epoch"] == 1
        return httpx.Response(409, json=envelope)

    with client_over(handler) as client, pytest.raises(ServerError) as raised:
        client.heartbeat(
            assignment_id=ASSIGNMENT_ID,
            lease_id=LEASE_ID,
            lease_epoch=1,
            posts_seen_in_run=30,
            posts_submitted_in_run=12,
            elapsed_s=400,
            x_session_state="ok",
        )
    assert raised.value.code is ErrorCode.STALE_LEASE


def test_no_work_is_not_an_error() -> None:  # SC01
    """``g-schedule-due-claim`` event 3: ``no_work`` comes back as data, not an exception.

    ``worker-assignment.schema.json`` says it in the schema itself: "Response khi không có
    việc. KHÔNG phải lỗi." Raising here would make an idle collector look broken (I13).
    """
    data = fixture("g-schedule-due-claim")
    body = find_event(data, "worker.claim_assignment", index=1)["response_body"]
    assert "no_work" in body

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    with client_over(handler) as client:
        answer = client.claim_assignment(
            claim_request_id="claim-2026-09-07-0801-aaa",
            worker_instance_id="KZA8XXCYQBY4190TVQJ05NMPZ3",
            capabilities={
                "collector_online": True,
                "chrome_profile_ready": True,
                "x_session_state": "ok",
                "embedding_supported": False,
            },
        )
    assert answer["no_work"]["reason"] == "assignment_already_held"
    assert answer["no_work"]["retry_after_ms"] == 45000


def test_registration_grants_no_lease() -> None:  # SC01, I10
    """``g-schedule-due-claim`` event 1 asserts ``lease_granted: false`` explicitly."""
    data = fixture("g-schedule-due-claim")
    body = find_event(data, "worker.register_capabilities")["response_body"]
    assert body["lease_granted"] is False

    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json=body)

    session = CollectorSession(
        worker_instance_id="JJ1KC0KSPYNFGC7NTA9BMRVHYP",
        profile=ChromeProfile(user_data_dir=Path("/srv/rr/profile"), ready=True),
        x_session_state=XSessionState.OK,
    )
    with client_over(handler) as client:
        answer = client.register_capabilities(session.registration_payload(7))

    assert answer["lease_granted"] is False
    assert captured["capabilities"]["embedding_supported"] is False
    assert captured["worker_kind"] == "collector"


def test_resume_reads_the_cursor_from_the_server_checkpoint() -> None:  # SC03, SC21
    """``b-cursor-invalidated-reread-dedup``: the assignment's checkpoint wins, always.

    And an invalidated cursor yields ``None`` -- re-reading from the start is permitted
    (``AMD-B05``, §CP-05). The fixture's own oracle warns against the wrong measurement:
    "Dùng SỐ REQUEST làm oracle -- AMD-B05 nói thẳng: request count KHÔNG phải oracle."
    """
    data = fixture("b-cursor-invalidated-reread-dedup")
    assignment = find_event(data, "worker.claim_assignment")["response_body"]["assignment"]

    cursor, state = resume_position(assignment)
    checkpoint = assignment["checkpoint"]
    if checkpoint["cursor_state"] == "invalidated":
        assert cursor is None
    else:
        assert cursor == checkpoint["cursor_token"]
    assert state == checkpoint["cursor_state"]

    invalidated = {
        "checkpoint": {
            "cursor_token": None,
            "cursor_state": "invalidated",
            "acked_through_ingest_sequence": 5,
        }
    }
    assert resume_position(invalidated) == (None, "invalidated")

    local_guess = {
        "checkpoint": {
            "cursor_token": "cursor-page-9",
            "cursor_state": "valid",
            "acked_through_ingest_sequence": 5,
        }
    }
    assert resume_position(local_guess) == ("cursor-page-9", "valid")


def test_commit_checkpoint_refuses_a_reason_outside_the_three_the_contract_allows() -> None:
    """§CP-07: ``empty_page``, ``end_of_feed``, ``segment_close`` -- and nothing else."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"receipt": {}})

    with client_over(handler) as client, pytest.raises(ValueError):
        client.commit_checkpoint(
            assignment_id=ASSIGNMENT_ID,
            checkpoint_seq=2,
            lease_id=LEASE_ID,
            lease_epoch=1,
            cursor_token=None,
            cursor_state="invalidated",
            proposed_acked_through_ingest_sequence=5,
            reason="because_i_felt_like_it",
        )


def test_commit_checkpoint_sends_the_shape_the_fixture_shows() -> None:
    """``b-cursor-invalidated-reread-dedup`` event 1 pins the request body field for field."""
    data = fixture("b-cursor-invalidated-reread-dedup")
    event = find_event(data, "ingest.commit_checkpoint")
    expected = event["request_body"]["checkpoint_only_request"]
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content)["checkpoint_only_request"])
        return httpx.Response(200, json=event["response_body"])

    with client_over(handler) as client:
        client.commit_checkpoint(
            assignment_id=expected["assignment_id"],
            checkpoint_seq=expected["checkpoint_seq"],
            lease_id=expected["lease_id"],
            lease_epoch=expected["lease_epoch"],
            cursor_token=expected["cursor_token"],
            cursor_state=expected["cursor_state"],
            proposed_acked_through_ingest_sequence=expected[
                "proposed_acked_through_ingest_sequence"
            ],
            reason=expected["reason"],
        )

    for key in (
        "assignment_id",
        "checkpoint_seq",
        "lease_id",
        "lease_epoch",
        "cursor_token",
        "cursor_state",
        "proposed_acked_through_ingest_sequence",
        "reason",
    ):
        assert captured[key] == expected[key], key


def test_limit_stop_report_carries_the_fields_the_fixture_pins() -> None:  # SC03
    """``e-limit-reached-stop`` event 2: ``limit_kind``, totals, and a non-empty note."""
    data = fixture("e-limit-reached-stop")
    event = find_event(data, "worker.report_stop")
    expected = event["request_body"]
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(200, json=event["response_body"])

    with client_over(handler) as client:
        ack = client.report_stop(
            assignment_id=expected["assignment_id"],
            stop_report_id=expected["stop_report_id"],
            lease_id=expected["lease_id"],
            lease_epoch=expected["lease_epoch"],
            stop_reason=WireStopReason.LIMIT_REACHED,
            last_acked_ingest_sequence=expected["last_acked_ingest_sequence"],
            extra={
                "limit_kind": expected["limit_kind"],
                "posts_observed_total": expected["posts_observed_total"],
                "x_coverage_note_vi": expected["x_coverage_note_vi"],
            },
        )

    assert captured["stop_reason"] == "limit_reached"
    assert captured["limit_kind"] == "posts"
    assert captured["x_coverage_note_vi"].strip()
    assert ack.alert_intent_created is False, "a limit creates no alert (fixture e)"
    assert ack.run["status"] == "running"
    assert ack.run["phase"] == "enriching"
    assert ack.run["stop_reason"] == "limit_reached"


def test_layout_change_409_is_an_acknowledgement_not_a_client_failure() -> None:  # SC03
    """``a-feed-layout-changed`` answers 409 to a report that was accepted and acted on."""
    data = fixture("a-feed-layout-changed")
    event = find_event(data, "worker.report_stop")
    body = event["response_body"]
    assert body["error"]["code"] == ErrorCode.SOURCE_LAYOUT_CHANGED.value

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json=body)

    with client_over(handler) as client:
        ack = client.report_stop(
            assignment_id=ASSIGNMENT_ID,
            stop_report_id="9XGPKVJCD94JQ768HNREVKT4N1",
            lease_id=LEASE_ID,
            lease_epoch=1,
            stop_reason=WireStopReason.SOURCE_LAYOUT_CHANGED,
            last_acked_ingest_sequence=12,
            extra={"missing_required_fields": ["author.handle", "published_at"]},
        )
    assert ack.echoed_code is ErrorCode.SOURCE_LAYOUT_CHANGED


def test_a_validation_error_on_report_stop_is_still_raised() -> None:
    """Only the stop codes are echoes. Everything else is a failure and must not be swallowed."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            409,
            json={
                "code": ErrorCode.IDEMPOTENCY_CONFLICT.value,
                "scope": "request",
                "retry_class": "none",
                "message_safe": "Yêu cầu trùng khóa nhưng nội dung khác.",
                "correlation_id": "QKEW1HGJVZ2R5X4EZBPM99RA3Q",
                "details_safe": {},
                "retry_after_ms": None,
            },
        )

    with client_over(handler) as client, pytest.raises(ServerError) as raised:
        client.report_stop(
            assignment_id=ASSIGNMENT_ID,
            stop_report_id="9XGPKVJCD94JQ768HNREVKT4N1",
            lease_id=LEASE_ID,
            lease_epoch=1,
            stop_reason=WireStopReason.LIMIT_REACHED,
            last_acked_ingest_sequence=200,
        )
    assert raised.value.code is ErrorCode.IDEMPOTENCY_CONFLICT


def test_the_bearer_token_never_appears_in_an_error() -> None:
    """``forbidden_content_vi``: no Authorization header, key or cookie in an envelope."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == f"Bearer {COLLECTOR_TOKEN}"
        return httpx.Response(
            401,
            json={
                "code": ErrorCode.UNAUTHORIZED.value,
                "scope": "request",
                "retry_class": "none",
                "message_safe": "Yêu cầu thiếu hoặc sai xác thực cho operation này.",
                "correlation_id": "QKEW1HGJVZ2R5X4EZBPM99RA3Q",
                "details_safe": {"operation_id": "ingest.submit_batch"},
                "retry_after_ms": None,
            },
        )

    with client_over(handler) as client, pytest.raises(ServerError) as raised:
        client.submit_batch(
            {"idempotency_key": "batch-2026-09-07-0001-aaaa", "items": []},
            assignment_id=ASSIGNMENT_ID,
        )
    rendered = f"{raised.value} {raised.value.details_safe} {raised.value.message_safe}"
    assert COLLECTOR_TOKEN not in rendered


def test_ports_and_errors_disagree_about_storage_write_failed_on_report_stop(
    ports: dict[str, Any], errors_contract: dict[str, Any]
) -> None:
    """A recorded asymmetry between two pinned contracts, raised as ``CR-TC-COLLECTOR-05``.

    ``contracts/ports.yaml`` lists ``STORAGE_WRITE_FAILED`` among ``worker.report_stop``'s
    ``error_codes``; ``contracts/errors.yaml`` does not list ``worker.report_stop`` among
    that code's ``operations``. Both readings are coherent on their own -- the ports entry
    means "the server may fail to persist the stop", the registry entry scopes the code to
    the store's own operations -- so this does not block the collector, which maps
    ``local_storage_unavailable`` to no code at all.

    The test asserts the *current* state deliberately. It is not an approval: it makes the
    inconsistency visible, fails the day either file is corrected, and stops a future reader
    from concluding the pairing was checked and found sound. Resolving it is change control's
    job, not this card's -- contracts are read-only here.
    """
    ports_codes = set(operation(ports, "worker.report_stop")["error_codes"])
    registry = {entry["code"]: entry for entry in errors_contract["codes"]}
    registry_operations = set(registry["STORAGE_WRITE_FAILED"].get("operations") or [])

    assert "STORAGE_WRITE_FAILED" in ports_codes
    assert "worker.report_stop" not in registry_operations
    assert STOP_REASON_ERROR_CODE[WireStopReason.LOCAL_STORAGE_UNAVAILABLE] is None
