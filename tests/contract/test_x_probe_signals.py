"""E1 — the §4 state-signal detector, offline.

Two oracles are used here and they answer different questions.

The **hand-written pages** in ``x_probe_synthetic_pages/`` answer "a page that looks like
this -- what does the detector say?". They are inputs, not an oracle; the directory README
records why they are not under ``acceptance/fixtures/``.

The **contracts** answer "and is that what the system is supposed to say?":
``contracts/state/run.yaml`` for the run ``stop_reason`` enum, ``contracts/http/openapi.yaml``
for the ``worker.report_stop`` wire enum, ``contracts/errors.yaml`` for the error codes, and
``acceptance/fixtures/collection/{a,c,e,g}`` for the four situations the collection fixtures
already pin. A contract edit breaks these tests -- which is the point: the mapping table in
``probe.x_feasibility.signals`` must never drift away from the contracts on its own.

No browser is installed, launched or imported anywhere in this file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

from probe.x_feasibility.dom import observe_html
from probe.x_feasibility.signals import (
    CONTINUE,
    RULES,
    ST_1,
    ST_2,
    ST_3,
    ST_4,
    ST_5,
    ST_6,
    ST_7,
    ST_8,
    STOP_CONDITION_MAP,
    MarkerSet,
    PageObservation,
    detect,
    detect_limit,
    limit_kind_for,
    operator_stop,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PAGES = Path(__file__).parent / "x_probe_synthetic_pages"

#: page file -> (URL it would have been reached at, HTTP status, expected ST id)
CASES: tuple[tuple[str, str, int | None, str], ...] = (
    ("healthy-feed.html", "https://x.com/search?q=x&f=live", 200, CONTINUE),
    ("challenge-verify.html", "https://x.com/account/access", 200, ST_1),
    ("challenge-arkose-iframe.html", "https://x.com/search?q=x&f=live", 200, ST_1),
    ("session-expired-login.html", "https://x.com/i/flow/login", 200, ST_2),
    ("access-blocked.html", "https://x.com/search?q=x&f=live", 403, ST_3),
    ("rate-limited.html", "https://x.com/search?q=x&f=live", 429, ST_4),
    ("layout-changed-missing-fields.html", "https://x.com/search?q=x&f=live", 200, ST_7),
    ("layout-changed-no-containers.html", "https://x.com/search?q=x&f=live", 200, ST_7),
)


def _observe(name: str, url: str, status: int | None) -> PageObservation:
    observation, _posts = observe_html(
        (PAGES / name).read_text(encoding="utf-8"), url=url, http_status=status
    )
    return observation  # type: ignore[return-value]


# --- the pages are synthetic, and stay that way -------------------------------------
def test_every_synthetic_page_declares_itself_synthetic() -> None:
    """A real capture dropped in here would carry session data. Make that impossible to miss."""
    files = sorted(PAGES.glob("*.html"))
    assert files, "không có trang tổng hợp nào — bộ test này sẽ pass vì không kiểm gì"
    for path in files:
        head = path.read_text(encoding="utf-8")[:200]
        assert "SYNTHETIC" in head, f"{path.name} thiếu dòng khai báo SYNTHETIC"


def test_no_browser_is_imported_by_this_test_module() -> None:
    """Playwright must not be installed or launched in tests (packet capability rule)."""
    assert "playwright" not in sys.modules


# --- detection ----------------------------------------------------------------------
@pytest.mark.parametrize(("name", "url", "status", "expected"), CASES)
def test_detects_expected_stop_condition(
    name: str, url: str, status: int | None, expected: str
) -> None:
    detection = detect(_observe(name, url, status))
    assert detection.stop_condition == expected, (
        f"{name}: mong đợi {expected}, nhận {detection.stop_condition} "
        f"(marker={detection.matched_marker})"
    )


def test_healthy_feed_yields_three_parsed_posts() -> None:
    observation, posts = observe_html(
        (PAGES / "healthy-feed.html").read_text(encoding="utf-8"),
        url="https://x.com/search?q=x&f=live",
        http_status=200,
    )
    assert len(posts) == 3
    assert all(p.parsed_ok for p in posts)
    assert sum(p.has_paper_link for p in posts) == 1
    assert sum(p.is_image_only for p in posts) == 1
    assert observation.parsed_ok_count == 3  # type: ignore[attr-defined]


def test_unknown_page_fails_closed_to_layout_changed() -> None:
    """The default on an unrecognised feed page is stop, never continue."""
    observation = PageObservation(
        url="https://x.com/search?q=x&f=live",
        visible_text="một trang hoàn toàn lạ",
        post_node_count=0,
        expects_feed=True,
    )
    assert detect(observation).stop_condition == ST_7


def test_blocked_wins_over_rate_limit_text() -> None:
    """Rule order is part of the contract reading: 'not let in' outranks 'slow down'."""
    observation = PageObservation(
        url="https://x.com/search?q=x&f=live",
        visible_text="Tài khoản của bạn đã bị khóa. Thử lại sau.",
        http_status=200,
        post_node_count=0,
    )
    assert detect(observation).stop_condition == ST_3


def test_challenge_wins_over_missing_login_marker() -> None:
    """An access-challenge page also lacks the logged-in markers; reading it as a session
    expiry would invite a re-login attempt, and I10 forbids anything resembling auto-recovery.
    """
    observation = PageObservation(
        url="https://x.com/account/access",
        visible_text="hãy xác minh",
        logged_in_marker_present=False,
        post_node_count=0,
    )
    assert detect(observation).stop_condition == ST_1


def test_rule_order_is_the_documented_one() -> None:
    assert [rule.stop_condition for rule in RULES] == [ST_3, ST_4, ST_1, ST_2, ST_7]


def test_extra_markers_are_additive_only() -> None:
    """A config can teach a new signal; it can never unteach one (§4 has no opt-out)."""
    markers = MarkerSet(extra={"blocked": ("một câu chặn riêng của tài khoản này",)})
    custom = PageObservation(
        url="https://x.com/search?q=x&f=live",
        visible_text="một câu chặn riêng của tài khoản này",
        post_node_count=0,
    )
    assert detect(custom, markers).stop_condition == ST_3
    default_still_fires = PageObservation(
        url="https://x.com/search?q=x&f=live",
        visible_text="access denied",
        post_node_count=0,
    )
    assert detect(default_still_fires, markers).stop_condition == ST_3


def test_parse_ratio_below_threshold_is_layout_changed() -> None:
    observation = PageObservation(
        url="https://x.com/search?q=x&f=live",
        visible_text="",
        post_node_count=10,
        parsed_ok_count=5,
    )
    assert detect(observation).stop_condition == ST_7


# --- limits -------------------------------------------------------------------------
def test_posts_limit_is_evaluated_before_duration() -> None:
    both = detect_limit(posts_seen=200, max_posts=200, elapsed_s=1800, max_duration_s=1800)
    assert both is not None
    assert both.stop_condition == ST_5
    assert limit_kind_for(both) == "posts"


def test_duration_limit_sets_duration_kind() -> None:
    hit = detect_limit(posts_seen=10, max_posts=200, elapsed_s=1801, max_duration_s=1800)
    assert hit is not None
    assert hit.stop_condition == ST_6
    assert limit_kind_for(hit) == "duration"


def test_no_limit_within_budget() -> None:
    assert detect_limit(posts_seen=1, max_posts=200, elapsed_s=1, max_duration_s=1800) is None


def test_limit_kind_is_null_for_every_non_limit_condition() -> None:
    """§5: ``limit_kind`` is NOT NULL exactly when ``stop_reason = limit_reached``."""
    non_limit_pages = {
        ST_1: PageObservation(url="https://x.com/account/access", post_node_count=0),
        ST_2: PageObservation(url="https://x.com/i/flow/login", post_node_count=0),
        ST_3: PageObservation(url="https://x.com/search", http_status=403, post_node_count=0),
        ST_4: PageObservation(url="https://x.com/search", http_status=429, post_node_count=0),
        ST_7: PageObservation(url="https://x.com/search", post_node_count=0),
    }
    for condition, observation in non_limit_pages.items():
        detection = detect(observation)
        assert detection.stop_condition == condition
        assert limit_kind_for(detection) is None
    assert limit_kind_for(operator_stop()) is None


# --- the mapping table against the contracts ----------------------------------------
def _run_yaml() -> dict:
    return yaml.safe_load((REPO_ROOT / "contracts/state/run.yaml").read_text(encoding="utf-8"))


def test_probe_stop_reasons_match_run_yaml_enum() -> None:
    """§5: the first six values match ``contracts/state/run.yaml`` §1."""
    enum = set(_run_yaml()["enums"]["stop_reason"]["values"])
    for condition, row in STOP_CONDITION_MAP.items():
        reason = row["stop_reason"]
        if condition == ST_8:
            assert reason == "operator_stop"
            assert reason not in enum, (
                "operator_stop là giá trị RIÊNG của probe (§5); nếu nó xuất hiện trong "
                "run.yaml thì §5 cần đọc lại, không phải code cần sửa"
            )
        else:
            assert reason in enum, f"{condition}: {reason!r} không có trong run.yaml"


def test_wire_stop_reasons_match_the_openapi_enum() -> None:
    """``worker.report_stop`` uses ``challenge_required`` where the run uses ``captcha``.

    Two vocabularies, not a defect: the collector card inherits this mapping instead of
    re-deriving it, and this test is what keeps the two spellings tied together.
    """
    text = (REPO_ROOT / "contracts/http/openapi.yaml").read_text(encoding="utf-8")
    spec = yaml.safe_load(text)
    stop_report = spec["components"]["schemas"]["StopReport"]
    wire_enum = set(stop_report["properties"]["stop_reason"]["enum"])
    for condition, row in STOP_CONDITION_MAP.items():
        wire = row["wire_stop_reason"]
        if condition == ST_8:
            assert wire is None, "ST-8 không có giá trị wire: vận hành thật không có nút dừng tay"
        else:
            assert wire in wire_enum, f"{condition}: {wire!r} không có trong enum wire"
    assert STOP_CONDITION_MAP[ST_1]["stop_reason"] == "captcha"
    assert STOP_CONDITION_MAP[ST_1]["wire_stop_reason"] == "challenge_required"


def test_error_codes_exist_in_errors_yaml() -> None:
    errors = yaml.safe_load((REPO_ROOT / "contracts/errors.yaml").read_text(encoding="utf-8"))
    known = {row["code"] for row in errors["codes"]}
    for condition, row in STOP_CONDITION_MAP.items():
        code = row["error_code"]
        if code is None:
            assert condition in {
                ST_5,
                ST_6,
                ST_8,
            }, f"{condition} phải có mã lỗi; chỉ giới hạn ngân sách và dừng tay là không lỗi"
        else:
            assert code in known, f"{condition}: mã {code!r} không có trong contracts/errors.yaml"


# --- against the four collection fixtures -------------------------------------------
def _fixture(name: str) -> dict:
    path = REPO_ROOT / "acceptance/fixtures/collection" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _stop_reports(fixture: dict) -> list[dict]:
    return [
        event["request_body"]
        for event in fixture["events"]
        if event.get("operation") == "worker.report_stop"
    ]


def test_fixture_a_feed_layout_changed_agrees_with_st7() -> None:
    reports = _stop_reports(_fixture("a-feed-layout-changed"))
    assert reports
    for report in reports:
        assert report["stop_reason"] == STOP_CONDITION_MAP[ST_7]["wire_stop_reason"]


def test_fixture_c_challenge_agrees_with_st1() -> None:
    reports = _stop_reports(_fixture("c-challenge-mid-batch"))
    assert reports
    for report in reports:
        assert report["stop_reason"] == STOP_CONDITION_MAP[ST_1]["wire_stop_reason"]


def test_fixture_e_limit_reached_agrees_with_st5() -> None:
    reports = _stop_reports(_fixture("e-limit-reached-stop"))
    assert reports
    report = reports[0]
    assert report["stop_reason"] == STOP_CONDITION_MAP[ST_5]["wire_stop_reason"]
    assert report["limit_kind"] == "posts"
    assert report["x_coverage_note_vi"].strip(), (
        "fixture e đòi coverage note khi chạm giới hạn — cùng kỷ luật GO-7 áp cho "
        "unobservable_scope_vi của probe"
    )


def test_fixture_g_source_limits_match_what_the_probe_enforces() -> None:
    """SL-4 ``chrome_scope: x_only`` is the limit the probe's URL gate implements."""
    fixture = _fixture("g-schedule-due-claim")
    claim = next(
        event for event in fixture["events"] if event.get("operation") == "worker.claim_assignment"
    )
    limits = claim["response_body"]["assignment"]["search_config"]["source_limits"]
    assert limits["chrome_scope"] == "x_only"
    assert limits["author_thread_only"] is True
    assert limits["external_replies"] == "excluded"
    assert limits["image_only_post_policy"] == "post_only_no_id_guess"
