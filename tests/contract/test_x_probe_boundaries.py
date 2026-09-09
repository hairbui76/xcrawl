"""E1 — the §2 boundaries, the two gates, and the run loop with a fake driver.

``contracts/ops/collector-probe.md`` §2 says the ethical and technical boundaries "không
phải tham số cấu hình" -- they are constraints, and violating one breaks the probe rather
than optimising it. A boundary that only lives in prose is a boundary nobody can check, so
this file checks the ones that can be checked by machine:

* the probe's own source contains no evasion mechanism, no click of any kind, and no user
  agent, proxy or fingerprint control;
* the config refuses the forbidden keys, the OS default Chrome profile, a non-X host, and
  any attempt to raise a §3 budget;
* the Owner gate (§6 / ``SG-02``) and the schedule guards (§3.1) refuse before a browser is
  ever opened;
* the run loop stops on the first §4 condition and never touches the driver again (I10:
  CAPTCHA does not auto-retry or auto-resume).

Playwright is never imported, installed or launched here. The run loop is exercised with a
fake driver that returns hand-written pages.
"""

from __future__ import annotations

import ast
import json
import logging
import re
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from probe.x_feasibility import config as config_module
from probe.x_feasibility.config import (
    OWNER_CONFIRMATION_KEYS,
    PROBE_MAX_DURATION_S,
    PROBE_MAX_POSTS_PER_RUN,
    PROBE_REQUEST_MIN_INTERVAL_MS,
    ConfigError,
    load_config,
    parse_config,
)
from probe.x_feasibility.dom import observe_html, parse_posts
from probe.x_feasibility.record import ProbeRunRecord, append_record, new_ulid
from probe.x_feasibility.run_probe import (
    LOG,
    GateRefused,
    PlaywrightXDriver,
    _StopState,
    check_owner_gate,
    check_schedule,
    main,
    run_one,
    setup_console_logging,
)
from probe.x_feasibility.signals import PageObservation

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE_DIR = REPO_ROOT / "probe"
PAGES = Path(__file__).parent / "x_probe_synthetic_pages"


def _probe_sources() -> list[Path]:
    return sorted(PROBE_DIR.rglob("*.py"))


# --- §2 boundaries, read off the source ---------------------------------------------
#: Patterns that would *be* an evasion mechanism if present. Matched against calls and
#: assignments, not bare words: ``config.py`` legitimately lists "captcha_solver" as a
#: forbidden config key, and ``signals.py`` legitimately names "recaptcha" as a marker to
#: recognise -- recognising a challenge is the opposite of evading one.
FORBIDDEN_SOURCE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\.click\s*\(", "không được có lời gọi click nào — 'không tự bấm xác minh' (I10)"),
    (r"\buser_agent\s*=", "không được đặt user agent (§2: không giả fingerprint)"),
    (r"set_user_agent|--user-agent", "không được đổi user agent"),
    (r"\bproxy\s*=", "không được cấu hình proxy (§2: không luân chuyển proxy)"),
    (r"set_extra_http_headers|extra_http_headers\s*=", "không được giả header"),
    (r"add_init_script|init_script\s*=", "không được tiêm script che dấu vết"),
    (r"webdriver\s*=|disable-blink-features", "không được che dấu hiệu tự động hóa"),
    (
        r"2captcha|anticaptcha|capsolver|deathbycaptcha|captcha_solver\s*\(",
        "không dịch vụ giải CAPTCHA",
    ),
    (r"rotate_account|next_account|account_pool|switch_account", "không luân chuyển account"),
    (
        r"api\.twitter\.com|api\.x\.com",
        "không dùng X API (SRC-SPEC §2.3 xếp X API trả phí ngoài phạm vi)",
    ),
)


@pytest.mark.parametrize(("pattern", "why"), FORBIDDEN_SOURCE_PATTERNS)
def test_probe_source_contains_no_evasion_mechanism(pattern: str, why: str) -> None:
    compiled = re.compile(pattern)
    offenders = [
        f"{path.relative_to(REPO_ROOT)}:{lineno}"
        for path in _probe_sources()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if compiled.search(line)
    ]
    assert not offenders, f"{why}; thấy ở {offenders}"


def test_the_driver_exposes_no_interaction_method() -> None:
    """The driver's surface is the boundary: what it cannot do, the run loop cannot do."""
    for forbidden in ("click", "tap", "fill", "type", "press", "check", "select_option"):
        assert not hasattr(PlaywrightXDriver, forbidden), (
            f"PlaywrightXDriver.{forbidden} tồn tại — bề mặt driver phải không có thao tác nào "
            "có thể vô tình trỏ vào trang xác minh"
        )


def test_playwright_is_never_imported_at_module_import_time() -> None:
    """Tests must not install or launch a browser; importing the CLI must stay cheap."""
    assert "playwright" not in sys.modules


def test_playwright_is_imported_only_inside_open_driver() -> None:
    """Nothing at module level imports Playwright, so importing the CLI costs nothing.

    Which is also why the whole test suite runs with no browser installed: the import that
    would need one happens in exactly one function, and that function is never called here.
    """
    source = (PROBE_DIR / "x_feasibility/run_probe.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    module_level_imports = [
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("playwright")
    ] + [
        alias.name
        for node in tree.body
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name.startswith("playwright")
    ]
    assert not module_level_imports, "playwright không được import ở cấp module"

    open_driver = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "open_driver"
    )
    inside = set(range(open_driver.lineno, (open_driver.end_lineno or open_driver.lineno) + 1))
    outside = [
        number
        for number, line in enumerate(source.splitlines(), start=1)
        if "sync_playwright" in line and number not in inside
    ]
    assert not outside, f"sync_playwright chỉ được dùng trong open_driver; thấy ở dòng {outside}"


# --- config gate ---------------------------------------------------------------------
def base_config(tmp_path: Path, **overrides: object) -> dict:
    data: dict = {
        "chrome_user_data_dir": str(tmp_path / "rr-x-profile"),
        "search_terms": ["protein folding"],
        "output_dir": str(tmp_path / "out"),
        "owner_confirmations": {
            key: {"confirmed": True, "evidence_ref": "OD-XXXX (test)"}
            for key in OWNER_CONFIRMATION_KEYS
        },
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize("key", sorted(config_module.FORBIDDEN_CONFIG_KEYS))
def test_config_rejects_every_forbidden_key(tmp_path: Path, key: str) -> None:
    with pytest.raises(ConfigError, match="§2"):
        parse_config(base_config(tmp_path, **{key: "anything"}))


@pytest.mark.parametrize(
    "profile",
    [
        "/home/tester/.config/google-chrome",
        "/home/tester/.config/google-chrome/Default",
        "/home/tester/Library/Application Support/Google/Chrome",
        "/home/tester/AppData/Local/Google/Chrome/User Data",
    ],
)
def test_config_refuses_the_default_chrome_profile(tmp_path: Path, profile: str) -> None:
    """P1: the project uses its own profile and the default profile is not touched (REQ-D09)."""
    with pytest.raises(ConfigError, match="MẶC ĐỊNH"):
        parse_config(base_config(tmp_path, chrome_user_data_dir=profile))


def test_config_requires_an_absolute_profile_path(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="tuyệt đối"):
        parse_config(base_config(tmp_path, chrome_user_data_dir="rr-x-profile"))


@pytest.mark.parametrize("url", ["https://arxiv.org", "https://example.com", "http://x.com"])
def test_config_refuses_a_non_x_base_url(tmp_path: Path, url: str) -> None:
    """SL-4 ``chrome_scope: x_only`` — the collector's Chrome only ever deals with X."""
    with pytest.raises(ConfigError):
        parse_config(base_config(tmp_path, x_base_url=url))


def test_config_cannot_raise_a_budget(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="max_posts_per_run"):
        parse_config(base_config(tmp_path, max_posts_per_run=PROBE_MAX_POSTS_PER_RUN + 1))
    with pytest.raises(ConfigError, match="max_duration_s"):
        parse_config(base_config(tmp_path, max_duration_s=PROBE_MAX_DURATION_S + 1))


def test_config_cannot_go_below_the_request_interval_floor(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="SÀN"):
        parse_config(
            base_config(tmp_path, request_min_interval_ms=PROBE_REQUEST_MIN_INTERVAL_MS - 1)
        )


def test_config_may_ask_for_less_than_the_budget(tmp_path: Path) -> None:
    cfg = parse_config(base_config(tmp_path, max_posts_per_run=50, max_duration_s=600))
    assert cfg.max_posts_per_run == 50
    assert cfg.max_duration_s == 600


def test_search_url_stays_on_x(tmp_path: Path) -> None:
    cfg = parse_config(base_config(tmp_path))
    url = cfg.search_url("protein folding & more")
    assert url.startswith("https://x.com/search?q=")
    assert "protein%20folding" in url


def test_redacted_summary_hides_the_profile_path(tmp_path: Path) -> None:
    cfg = parse_config(base_config(tmp_path))
    summary = json.dumps(cfg.redacted_summary(), ensure_ascii=False)
    assert str(tmp_path) not in summary
    assert summary.count("rr-x-profile") == 1  # only the leaf name survives


def test_load_config_reads_a_file(tmp_path: Path) -> None:
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(base_config(tmp_path)), encoding="utf-8")
    assert load_config(path).search_terms == ("protein folding",)


# --- Owner gate (§6 / SG-02) ----------------------------------------------------------
@pytest.mark.parametrize("missing", OWNER_CONFIRMATION_KEYS)
def test_owner_gate_refuses_when_any_confirmation_is_absent(tmp_path: Path, missing: str) -> None:
    data = base_config(tmp_path)
    data["owner_confirmations"][missing] = {"confirmed": False, "evidence_ref": ""}
    cfg = parse_config(data)
    with pytest.raises(GateRefused, match="OWNER_DECISION_REQUIRED"):
        check_owner_gate(cfg)
    assert missing in cfg.owner_gate().missing


def test_owner_gate_refuses_a_confirmation_without_a_written_reference(tmp_path: Path) -> None:
    """§6 asks for the confirmation "bằng văn bản": a bare ``true`` is not a confirmation."""
    data = base_config(tmp_path)
    data["owner_confirmations"]["go_no_go_criteria"] = {"confirmed": True, "evidence_ref": "  "}
    with pytest.raises(GateRefused):
        check_owner_gate(parse_config(data))


def test_owner_gate_opens_only_with_all_four(tmp_path: Path) -> None:
    check_owner_gate(parse_config(base_config(tmp_path)))


def test_a_config_with_no_confirmations_block_is_closed(tmp_path: Path) -> None:
    data = base_config(tmp_path)
    del data["owner_confirmations"]
    cfg = parse_config(data)
    assert cfg.owner_gate().missing == OWNER_CONFIRMATION_KEYS


# --- schedule guards (§3.1) -------------------------------------------------------------
def _record_dict(started: str, ended: str) -> dict:
    return {"started_at": started, "ended_at": ended}


def test_schedule_refuses_beyond_the_ten_run_ceiling() -> None:
    records = [_record_dict("2026-09-01T08:00:00.000Z", "2026-09-01T08:30:00.000Z")] * 10
    with pytest.raises(GateRefused, match="probe_run_count_max"):
        check_schedule(records, now=datetime(2026, 9, 30, tzinfo=UTC))


def test_schedule_refuses_a_fifth_run_in_one_day() -> None:
    records = [
        _record_dict("2026-09-08T0%d:00:00.000Z" % i, "2026-09-08T0%d:30:00.000Z" % i)
        for i in range(1, 5)
    ]
    with pytest.raises(GateRefused, match="probe_runs_per_day_max"):
        check_schedule(records, now=datetime(2026, 9, 8, 23, tzinfo=UTC))


def test_schedule_refuses_a_run_inside_the_sixty_minute_gap() -> None:
    last_end = datetime(2026, 9, 8, 8, 30, tzinfo=UTC)
    records = [_record_dict("2026-09-08T08:00:00.000Z", "2026-09-08T08:30:00.000Z")]
    with pytest.raises(GateRefused, match="probe_min_gap_minutes"):
        check_schedule(records, now=last_end + timedelta(minutes=59))


def test_schedule_allows_a_run_after_the_gap() -> None:
    records = [_record_dict("2026-09-08T08:00:00.000Z", "2026-09-08T08:30:00.000Z")]
    check_schedule(records, now=datetime(2026, 9, 8, 10, tzinfo=UTC))


def test_schedule_allows_the_first_run() -> None:
    check_schedule([], now=datetime(2026, 9, 8, tzinfo=UTC))


# --- the run loop, with a fake driver ---------------------------------------------------
class FakeDriver:
    """A :class:`PageDriver` over a scripted list of synthetic pages. No browser anywhere."""

    def __init__(self, pages: list[str], *, statuses: list[int | None] | None = None) -> None:
        self._pages = pages
        self._statuses = statuses or [200] * len(pages)
        self.index = 0
        self.calls: list[str] = []
        self.url = "https://x.com/search?q=protein%20folding&f=live"

    def goto(self, url: str) -> None:
        self.calls.append(f"goto:{url}")
        self.url = url

    def _html(self) -> str:
        position = min(self.index, len(self._pages) - 1)
        return (PAGES / self._pages[position]).read_text(encoding="utf-8")

    def observe(self, *, expects_feed: bool = True) -> PageObservation:
        self.calls.append("observe")
        status = self._statuses[min(self.index, len(self._statuses) - 1)]
        observation, _ = observe_html(
            self._html(), url=self.url, http_status=status, expects_feed=expects_feed
        )
        return observation  # type: ignore[return-value]

    def collect_posts(self):  # type: ignore[no-untyped-def]
        self.calls.append("collect")
        return parse_posts(self._html())

    def scroll(self) -> None:
        self.calls.append("scroll")
        self.index += 1

    def close(self) -> None:
        self.calls.append("close")


def _cfg(tmp_path: Path, **overrides: object):  # type: ignore[no-untyped-def]
    return parse_config(base_config(tmp_path, **overrides))


def test_run_loop_records_a_healthy_run(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, max_scroll_steps_per_term=2)
    driver = FakeDriver(["healthy-feed.html"])
    record, digests = run_one(cfg, driver, seen_digests=set(), sleep=lambda _s: None)
    assert record.posts_seen == 3
    assert record.posts_parsed_ok == 3
    assert record.posts_new_vs_previous_runs == 3
    assert record.posts_with_paper_link == 1
    assert record.posts_image_only == 1
    assert record.stop_reason == "limit_reached"
    assert record.unobservable_scope_vi.strip()
    assert len(digests) == 3


def test_previously_seen_posts_are_not_counted_as_new(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, max_scroll_steps_per_term=1)
    first, digests = run_one(
        cfg, FakeDriver(["healthy-feed.html"]), seen_digests=set(), sleep=lambda _s: None
    )
    second, _ = run_one(
        cfg, FakeDriver(["healthy-feed.html"]), seen_digests=digests, sleep=lambda _s: None
    )
    assert first.posts_new_vs_previous_runs == 3
    assert second.posts_new_vs_previous_runs == 0
    assert second.posts_seen == 3


def test_challenge_stops_the_run_and_never_touches_the_driver_again(tmp_path: Path) -> None:
    """I10: no auto-retry, no auto-resume, no second look."""
    cfg = _cfg(tmp_path, max_scroll_steps_per_term=10)
    driver = FakeDriver(["challenge-verify.html"])
    record, _ = run_one(cfg, driver, seen_digests=set(), sleep=lambda _s: None)
    assert record.stop_reason == "captcha"
    assert record.challenge_count == 1
    assert record.limit_kind is None
    assert "scroll" not in driver.calls, "sau tín hiệu dừng không được cuộn thêm"
    assert driver.calls.count("goto:" + cfg.search_url("protein folding")) == 1


def test_blocked_page_stops_with_source_blocked(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    driver = FakeDriver(["access-blocked.html"], statuses=[403])
    record, _ = run_one(cfg, driver, seen_digests=set(), sleep=lambda _s: None)
    assert record.stop_reason == "source_blocked"
    assert record.blocked_count == 1


def test_rate_limited_page_records_the_first_stamp(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    driver = FakeDriver(["rate-limited.html"], statuses=[429])
    record, _ = run_one(cfg, driver, seen_digests=set(), sleep=lambda _s: None)
    assert record.stop_reason == "rate_limited"
    assert record.rate_limited_count == 1
    assert record.rate_limited_at is not None


def test_layout_change_stops_and_names_no_guessed_field(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    driver = FakeDriver(["layout-changed-missing-fields.html"])
    record, digests = run_one(cfg, driver, seen_digests=set(), sleep=lambda _s: None)
    assert record.stop_reason == "source_layout_changed"
    assert record.parser_degraded_count == 1
    assert record.posts_seen == 0, "không đếm bài từ một trang không bóc được"
    assert digests == set()


def test_second_term_is_not_opened_after_a_stop(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, search_terms=["a", "b"])
    driver = FakeDriver(["challenge-verify.html"])
    record, _ = run_one(cfg, driver, seen_digests=set(), sleep=lambda _s: None)
    assert sum(1 for c in driver.calls if c.startswith("goto:")) == 1
    assert "1/2 từ khóa chưa được mở" in record.unobservable_scope_vi


def test_operator_stop_is_recorded(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path)
    state = _StopState(interrupted=True)
    record, _ = run_one(
        cfg,
        FakeDriver(["healthy-feed.html"]),
        seen_digests=set(),
        stop_state=state,
        sleep=lambda _s: None,
    )
    assert record.stop_reason == "operator_stop"
    assert record.limit_kind is None


def test_post_budget_stops_the_run(tmp_path: Path) -> None:
    cfg = _cfg(tmp_path, max_posts_per_run=2, max_scroll_steps_per_term=5)
    record, _ = run_one(
        cfg, FakeDriver(["healthy-feed.html"]), seen_digests=set(), sleep=lambda _s: None
    )
    assert record.stop_reason == "limit_reached"
    assert record.limit_kind == "posts"
    assert record.posts_seen >= 2


def test_every_produced_record_validates(tmp_path: Path) -> None:
    """Whatever the loop produces must satisfy §5 -- checked on write, not on review."""
    cfg = _cfg(tmp_path)
    for page, statuses in [
        ("healthy-feed.html", None),
        ("challenge-verify.html", None),
        ("access-blocked.html", [403]),
        ("rate-limited.html", [429]),
        ("layout-changed-no-containers.html", None),
        ("session-expired-login.html", None),
    ]:
        record, _ = run_one(
            cfg, FakeDriver([page], statuses=statuses), seen_digests=set(), sleep=lambda _s: None
        )
        append_record(tmp_path / "out" / "runs.jsonl", record)


# --- the CLI refuses before opening anything ---------------------------------------------
def _explode(*_args: object, **_kwargs: object):  # pragma: no cover - must never run
    raise AssertionError("open_driver được gọi dù cổng chưa mở")


def test_cli_refuses_when_the_owner_gate_is_closed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("probe.x_feasibility.run_probe.open_driver", _explode)
    data = base_config(tmp_path)
    data["owner_confirmations"]["account_risk_understood"] = {
        "confirmed": False,
        "evidence_ref": "",
    }
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert main(["--config", str(path)]) == 2


def test_cli_dry_run_opens_no_browser(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr("probe.x_feasibility.run_probe.open_driver", _explode)
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(base_config(tmp_path)), encoding="utf-8")
    assert main(["--config", str(path), "--dry-run"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["gate"] == "open"
    assert "KHÔNG mở trình duyệt" in payload["note_vi"]


def test_cli_refuses_more_runs_than_the_daily_maximum(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("probe.x_feasibility.run_probe.open_driver", _explode)
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(base_config(tmp_path)), encoding="utf-8")
    assert main(["--config", str(path), "--runs", "5"]) == 2


def test_cli_refuses_when_the_ceiling_is_already_reached(tmp_path: Path, monkeypatch) -> None:
    """The card's example ``--runs 5`` is refused with the contract clause that refuses it."""
    monkeypatch.setattr("probe.x_feasibility.run_probe.open_driver", _explode)
    out = tmp_path / "out"
    for index in range(10):
        append_record(
            out / "runs.jsonl",
            ProbeRunRecord(
                probe_run_id=new_ulid(
                    now_ms=1_700_000_000_000 + index, randomness=bytes([index]) * 10
                ),
                started_at=f"2026-09-{1 + index:02d}T08:00:00.000Z",
                ended_at=f"2026-09-{1 + index:02d}T08:30:00.000Z",
                duration_s=1800,
                search_terms=["protein folding"],
                posts_seen=10,
                posts_parsed_ok=10,
                posts_new_vs_previous_runs=1,
                posts_with_paper_link=0,
                posts_image_only=0,
                author_threads_opened=0,
                challenge_count=0,
                session_expired_count=0,
                blocked_count=0,
                rate_limited_count=0,
                rate_limited_at=None,
                parser_degraded_count=0,
                stop_reason="limit_reached",
                limit_kind="duration",
                cursor_invalidated=False,
                unobservable_scope_vi="tổng hợp",
            ),
        )
    path = tmp_path / "probe.json"
    path.write_text(json.dumps(base_config(tmp_path)), encoding="utf-8")
    assert main(["--config", str(path)]) == 2


# --- G-5: where output lands, and the promise that a dry run lands nothing ---------------
def _tree(root: Path) -> set[Path]:
    """Every path under ``root``, files and directories alike."""
    return set(root.rglob("*"))


def test_relative_output_dir_resolves_against_cwd_not_the_config_file(
    tmp_path, monkeypatch
) -> None:
    """Wiring gap G-5.

    The config file used to decide where evidence landed: a relative ``output_dir`` was
    resolved against the config's own directory, so shipping the example config inside
    ``probe/`` sent the default to ``probe/evidence/runs/SP1-x-feasibility/`` -- a directory
    the Owner never named. CWD is the rule now, and it is the rule ``probe/go_no_go.py``
    already assumed for its default argument.
    """
    config_dir = tmp_path / "somewhere" / "else"
    config_dir.mkdir(parents=True)
    workdir = tmp_path / "workdir"
    workdir.mkdir()

    data = base_config(tmp_path)
    data["output_dir"] = "evidence/runs/SP1-x-feasibility"
    config_path = config_dir / "probe.json"
    config_path.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.chdir(workdir)
    cfg = load_config(config_path)

    assert cfg.output_dir == workdir / "evidence/runs/SP1-x-feasibility"
    assert (
        config_dir not in cfg.output_dir.parents
    ), "output_dir không được bám theo thư mục chứa file config (G-5)"


def test_absolute_output_dir_is_used_verbatim(tmp_path) -> None:
    cfg = parse_config(base_config(tmp_path, output_dir=str(tmp_path / "elsewhere")))
    assert cfg.output_dir == tmp_path / "elsewhere"


def test_dry_run_creates_nothing_anywhere(tmp_path, monkeypatch, capsys) -> None:
    """A dry run must leave the filesystem exactly as it found it.

    Not "nothing outside the output directory" -- nothing at all, the output directory
    included. A command whose whole purpose is to check whether it is *allowed* to run has
    no business creating the place it would have written to.
    """
    monkeypatch.setattr("probe.x_feasibility.run_probe.open_driver", _explode)
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    config_path = tmp_path / "probe.json"
    data = base_config(tmp_path)
    data["output_dir"] = "evidence/runs/SP1-x-feasibility"
    config_path.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.chdir(workdir)
    before = _tree(tmp_path)
    assert main(["--config", str(config_path), "--dry-run"]) == 0
    after = _tree(tmp_path)

    assert after == before, f"dry-run đã tạo: {sorted(str(p) for p in after - before)}"
    payload = json.loads(capsys.readouterr().out)
    assert payload["wrote_nothing"] is True


def test_a_refused_run_creates_nothing_either(tmp_path, monkeypatch) -> None:
    """The gate-refusal path used to build the output directory before refusing."""
    monkeypatch.setattr("probe.x_feasibility.run_probe.open_driver", _explode)
    workdir = tmp_path / "workdir"
    workdir.mkdir()
    data = base_config(tmp_path)
    data["output_dir"] = "evidence/runs/SP1-x-feasibility"
    data["owner_confirmations"]["go_no_go_criteria"] = {"confirmed": False, "evidence_ref": ""}
    config_path = tmp_path / "probe.json"
    config_path.write_text(json.dumps(data), encoding="utf-8")

    monkeypatch.chdir(workdir)
    before = _tree(tmp_path)
    assert main(["--config", str(config_path)]) == 2
    assert _tree(tmp_path) == before, "một lần bị cổng từ chối không được để lại thư mục nào"


def test_console_logging_opens_no_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    setup_console_logging()
    assert not any(isinstance(h, logging.FileHandler) for h in LOG.handlers)
    assert _tree(tmp_path) == set()


def test_the_example_config_default_lands_in_the_repo_evidence_tree(monkeypatch) -> None:
    """Run from the repo root, the shipped example writes where card §3 says it should."""
    data = json.loads((REPO_ROOT / "probe/probe-config.example.json").read_text(encoding="utf-8"))
    data["chrome_user_data_dir"] = "/home/tester/rr-x-profile"
    monkeypatch.chdir(REPO_ROOT)
    cfg = parse_config(data)
    assert cfg.output_dir == REPO_ROOT / "evidence/runs/SP1-x-feasibility"
