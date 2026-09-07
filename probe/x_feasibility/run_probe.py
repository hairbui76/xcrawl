"""Drive one SP1 probe run and write its §5 record. Read-only observation, nothing else.

What one run does (``contracts/ops/collector-probe.md`` §3 and §5):

1. refuse to start unless the §6 Owner gate is open and the §3.1 schedule guards allow it;
2. open the **project's own** Chrome profile as a Playwright persistent context (REQ-D09);
3. for each configured search term, open X's live search and scroll within budget, never
   faster than ``request_min_interval_ms``;
4. after every navigation and every scroll, classify the page with
   :mod:`probe.x_feasibility.signals` and **stop on any §4 condition**;
5. count what was observed and append one JSONL record.

What it never does. It never clicks anything -- there is no click call in this module, and
``tests/contract/test_x_probe_boundaries.py`` asserts that, because "never click
verification" (I10) is only credible if there is no click to accidentally point at a
challenge. It never sets a user agent, never configures a proxy, never touches an account
list, never solves or bypasses a challenge, and never retries a stopped run. It does not
call the server: M0 is dry-run (§1 P6), so ``ingest.submit_batch`` and ``worker.report_stop``
are not called from here -- the §5 record is the whole output.

Exit codes: 0 run completed and recorded, 2 a gate refused the run (Owner gate, schedule
guard, config), 3 the run stopped on a §4 source condition (still recorded), 4 usage/IO.
"""

from __future__ import annotations

# ruff: noqa: E402 -- the sys.path bootstrap below must run before the package imports.
import sys
from pathlib import Path as _Path

if __name__ == "__main__" and __package__ in {None, ""}:
    # The card gives this command as a FILE PATH (§8: `python probe/x_feasibility/run_probe.py`).
    # Python then puts *this file's directory* on sys.path -- not the repo root -- so
    # `import probe.…` would fail on the first import line. Putting the repo root first makes
    # the documented command work. It is a no-op for `python -m probe.x_feasibility.run_probe`
    # and for every import, which never enter this branch.
    sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

import argparse
import json
import logging
import signal
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import FrameType
from typing import Any, Protocol

from probe.x_feasibility import PROTOCOL_VERSION
from probe.x_feasibility.config import (
    PROBE_MIN_GAP_MINUTES,
    PROBE_RUN_COUNT_MAX,
    PROBE_RUNS_PER_DAY_MAX,
    ConfigError,
    ProbeConfig,
    load_config,
)
from probe.x_feasibility.dom import (
    PAPER_LINK_HOSTS,
    POST_ID_RE,
    SELECTOR_AUTHOR,
    SELECTOR_CHALLENGE_WIDGET,
    SELECTOR_LOGGED_IN,
    SELECTOR_PHOTO,
    SELECTOR_POST,
    SELECTOR_TIME,
    PostObservation,
)
from probe.x_feasibility.record import (
    ProbeRunRecord,
    RunCounters,
    append_record,
    append_seen_ledger,
    format_utc_ms,
    hash_post_id,
    load_seen_ledger,
    new_ulid,
    read_records,
    redact,
    utc_now_ms,
)
from probe.x_feasibility.signals import (
    ST_5,
    Detection,
    MarkerSet,
    PageObservation,
    detect,
    detect_limit,
    limit_kind_for,
    operator_stop,
)

LOG = logging.getLogger("probe.x_feasibility")

RUNS_FILENAME = "runs.jsonl"
LEDGER_FILENAME = "seen-post-ids.sha256"
LOG_FILENAME = "probe.log"

#: §4 ST-5 with the scroll allowance as the budget that was reached. Split out as a
#: constant so the one place the probe records a stop it did not *observe* on the page is
#: visible, named, and testable.
SCROLL_BUDGET_STOP = Detection(
    stop_condition=ST_5,
    stop_reason="limit_reached",
    error_code=None,
    wire_stop_reason="limit_reached",
    counter_field=None,
    detail_vi=(
        "Hết số bước cuộn đã cấu hình (max_scroll_steps_per_term) cho mọi từ khóa, "
        "trong ngân sách §3.2."
    ),
    matched_marker="scroll_steps_exhausted",
)


SOURCE_STOP_REASONS: frozenset[str] = frozenset(
    {"captcha", "session_expired", "source_blocked", "rate_limited", "source_layout_changed"}
)


class GateRefused(RuntimeError):
    """A gate refused to let this run start. Never a failure of X -- a failure to qualify."""


class PageDriver(Protocol):
    """The narrow surface the run loop needs. Deliberately has no ``click``."""

    def goto(self, url: str) -> None: ...

    def observe(self, *, expects_feed: bool = True) -> PageObservation: ...

    def collect_posts(self) -> list[PostObservation]: ...

    def scroll(self) -> None: ...

    def close(self) -> None: ...


# --- the run loop -------------------------------------------------------------------
@dataclass
class _StopState:
    detection: Detection | None = None
    interrupted: bool = False


def run_one(
    cfg: ProbeConfig,
    driver: PageDriver,
    *,
    seen_digests: set[str],
    stop_state: _StopState | None = None,
    sleep: Any = time.sleep,
    now: Any = lambda: datetime.now(UTC),
) -> tuple[ProbeRunRecord, set[str]]:
    """Perform one run against ``driver`` and return its record and the new id digests.

    Pure orchestration: every side effect goes through ``driver``, ``sleep`` and ``now``,
    which is why the whole loop is testable with a fake driver and no browser.
    """
    state = stop_state or _StopState()
    markers = MarkerSet(extra=cfg.extra_markers)
    counters = RunCounters()
    started = now()
    started_at = format_utc_ms(started)
    new_digests: set[str] = set()
    terms_started: list[str] = []
    stop: Detection | None = None
    interval_s = cfg.request_min_interval_ms / 1000.0

    def elapsed() -> float:
        return float((now() - started).total_seconds())

    def check_budget() -> Detection | None:
        return detect_limit(
            posts_seen=counters.posts_seen,
            max_posts=cfg.max_posts_per_run,
            elapsed_s=elapsed(),
            max_duration_s=cfg.max_duration_s,
        )

    def tally(posts: list[PostObservation]) -> None:
        for post in posts:
            counters.posts_seen += 1
            if post.parsed_ok:
                counters.posts_parsed_ok += 1
                digest = hash_post_id(str(post.x_post_id))
                if digest not in seen_digests and digest not in new_digests:
                    new_digests.add(digest)
                    counters.posts_new_vs_previous_runs += 1
            if post.has_paper_link:
                counters.posts_with_paper_link += 1
            if post.is_image_only:
                counters.posts_image_only += 1

    for term in cfg.search_terms:
        if stop is not None or state.interrupted:
            break
        terms_started.append(term)
        LOG.info(
            "mở tìm kiếm cho một từ khóa (thứ %d/%d)",
            len(terms_started),
            len(cfg.search_terms),
        )
        driver.goto(cfg.search_url(term))
        sleep(interval_s)

        observation = driver.observe(expects_feed=True)
        detection = detect(observation, markers)
        if detection.should_stop:
            counters.bump(detection.counter_field, at=utc_now_ms())
            stop = detection
            break

        seen_ids_this_page: set[str] = set()
        max_container_count = 0
        for step in range(cfg.max_scroll_steps_per_term):
            if state.interrupted:
                break
            posts = driver.collect_posts()
            max_container_count = max(max_container_count, len(posts))
            fresh = [p for p in posts if p.x_post_id not in seen_ids_this_page]
            for post in fresh:
                if post.x_post_id:
                    seen_ids_this_page.add(post.x_post_id)
            tally(fresh)

            budget = check_budget()
            if budget is not None:
                stop = budget
                break

            driver.scroll()
            sleep(interval_s)
            observation = driver.observe(expects_feed=True)
            detection = detect(observation, markers)
            if detection.should_stop:
                counters.bump(detection.counter_field, at=utc_now_ms())
                stop = detection
                break
            # B05: the feed shrinking well below what it had already rendered is how a lost
            # cursor shows up from the outside. Recorded, never "recovered from".
            if (
                observation.post_node_count
                and max_container_count
                and (observation.post_node_count * 2 < max_container_count)
            ):
                counters.cursor_invalidated = True
            if step == cfg.max_scroll_steps_per_term - 1:
                LOG.info("hết số bước cuộn cho từ khóa này; chuyển từ khóa tiếp theo")
        if stop is not None:
            break
        counters.terms_completed.append(term)

    if stop is None and state.interrupted:
        stop = operator_stop()
    if stop is None:
        stop = check_budget()
    if stop is None:
        # Every term was walked to the end of its scroll allowance while still inside the
        # §3.2 budget. §4 has no "finished naturally" row, and inventing one would put a
        # value outside the §5 enum into the record. The true statement is that the run
        # ended at a budget of its own -- ``max_scroll_steps_per_term`` -- so it is recorded
        # as ST-5 with ``limit_kind = posts`` and a note naming which budget ran out.
        stop = SCROLL_BUDGET_STOP

    ended = now()
    unobserved = _unobservable_scope(cfg, counters, stop, terms_started)
    record = ProbeRunRecord(
        probe_run_id=new_ulid(),
        started_at=started_at,
        ended_at=format_utc_ms(ended),
        duration_s=int((ended - started).total_seconds()),
        search_terms=list(cfg.search_terms),
        posts_seen=counters.posts_seen,
        posts_parsed_ok=counters.posts_parsed_ok,
        posts_new_vs_previous_runs=counters.posts_new_vs_previous_runs,
        posts_with_paper_link=counters.posts_with_paper_link,
        posts_image_only=counters.posts_image_only,
        author_threads_opened=counters.author_threads_opened,
        challenge_count=counters.challenge_count,
        session_expired_count=counters.session_expired_count,
        blocked_count=counters.blocked_count,
        rate_limited_count=counters.rate_limited_count,
        rate_limited_at=counters.rate_limited_at,
        parser_degraded_count=counters.parser_degraded_count,
        stop_reason=str(stop.stop_reason),
        limit_kind=limit_kind_for(stop),
        cursor_invalidated=counters.cursor_invalidated,
        unobservable_scope_vi=unobserved,
        notes_vi=redact(f"{stop.detail_vi} [tín hiệu: {stop.matched_marker}]"),
        protocol_version=PROTOCOL_VERSION,
    )
    return record, new_digests


def _unobservable_scope(
    cfg: ProbeConfig,
    counters: RunCounters,
    stop: Detection,
    terms_started: list[str],
) -> str:
    """Compose §5 ``unobservable_scope_vi``. Never empty -- GO-7 depends on it.

    It describes what the run did **not** see, from what actually happened: terms never
    opened, the term cut mid-way, the budget ceiling, and the cursor. The Owner adds
    anything else through ``--note``.
    """
    parts: list[str] = []
    not_started = len(cfg.search_terms) - len(terms_started)
    if not_started > 0:
        parts.append(
            f"{not_started}/{len(cfg.search_terms)} từ khóa chưa được mở lần nào trong đợt này."
        )
    incomplete = len(terms_started) - len(counters.terms_completed)
    if incomplete > 0:
        parts.append(f"{incomplete} từ khóa bị cắt giữa chừng khi đợt dừng.")
    parts.append(
        f"Chỉ quan sát tab 'Mới nhất' của tìm kiếm, giới hạn {cfg.max_posts_per_run} bài và "
        f"{cfg.max_duration_s}s; phần feed sau mốc dừng KHÔNG được quét."
    )
    parts.append(
        "Không mở thread, không mở reply, không mở trang tác giả — nên phần ngữ cảnh của "
        "mỗi bài nằm ngoài quan sát (SL-1, SL-2)."
    )
    if counters.cursor_invalidated:
        parts.append(
            "Con trỏ feed mất hiệu lực giữa chừng: khoảng giữa hai lần cuộn có thể đã bị bỏ."
        )
    if stop.stop_reason != "limit_reached":
        parts.append(
            f"Đợt dừng sớm vì {stop.stop_reason}; phần còn lại của ngân sách không được dùng."
        )
    return " ".join(parts)


# --- gates --------------------------------------------------------------------------
def check_schedule(records: list[dict[str, Any]], *, now: datetime) -> None:
    """§3.1 schedule guards. Raises :class:`GateRefused` with the contract's own numbers."""
    if len(records) >= PROBE_RUN_COUNT_MAX:
        raise GateRefused(
            f"Đã có {len(records)} đợt; §3.1 probe_run_count_max = {PROBE_RUN_COUNT_MAX}. "
            "Trần tồn tại để probe không biến thành 'dùng thật mà chưa có hợp đồng'. "
            "Tính go/no-go bằng probe/go_no_go.py thay vì chạy thêm."
        )
    today = now.date().isoformat()
    today_count = sum(1 for r in records if str(r["started_at"])[:10] == today)
    if today_count >= PROBE_RUNS_PER_DAY_MAX:
        raise GateRefused(
            f"Hôm nay đã chạy {today_count} đợt; §3.1 probe_runs_per_day_max = "
            f"{PROBE_RUNS_PER_DAY_MAX}. Chạy tiếp vào ngày khác — §3.1 cũng đòi các đợt "
            "trải qua ít nhất 3 ngày khác nhau (probe_span_days_min)."
        )
    if records:
        last_end = datetime.strptime(records[-1]["ended_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=UTC
        )
        gap = now - last_end
        if gap < timedelta(minutes=PROBE_MIN_GAP_MINUTES):
            remaining = timedelta(minutes=PROBE_MIN_GAP_MINUTES) - gap
            raise GateRefused(
                f"Đợt trước kết thúc {int(gap.total_seconds() // 60)} phút trước; §3.1 "
                f"probe_min_gap_minutes = {PROBE_MIN_GAP_MINUTES}. Chờ thêm "
                f"{int(remaining.total_seconds() // 60) + 1} phút. Chạy sát nhau làm nhiễu "
                "phép đo challenge rate."
            )


def check_owner_gate(cfg: ProbeConfig) -> None:
    """§6 / card ``SG-02``: an absolute stop, not a warning."""
    gate = cfg.owner_gate()
    if not gate.is_open:
        raise GateRefused(gate.explain_vi())


# --- Playwright driver (never constructed in tests) ---------------------------------
class PlaywrightXDriver:
    """A :class:`PageDriver` over a real Chrome, opened with the project's own profile.

    Constructed only by :func:`open_driver`, which imports Playwright lazily so importing
    this module never needs the package and never touches a browser binary.

    Launch options are deliberately plain: ``channel="chrome"`` uses the Chrome that is
    installed, ``user_data_dir`` is the project's profile, ``headless=False`` because the
    Owner must be able to see and answer a challenge themselves. No ``user_agent``, no
    ``proxy``, no ``extra_http_headers``, no init script -- §2 of the contract.
    """

    def __init__(self, context: Any, page: Any) -> None:
        self._context = context
        self._page = page

    def goto(self, url: str) -> None:
        self._last_response = self._page.goto(url, wait_until="domcontentloaded")

    def observe(self, *, expects_feed: bool = True) -> PageObservation:
        page = self._page
        status = getattr(getattr(self, "_last_response", None), "status", None)
        posts = self.collect_posts()
        missing: set[str] = set()
        for post in posts:
            missing.update(post.missing_fields)
        return PageObservation(
            url=page.url,
            title=page.title(),
            visible_text=(page.inner_text("body") or "")[:20000],
            http_status=status,
            post_node_count=len(posts),
            parsed_ok_count=sum(1 for p in posts if p.parsed_ok),
            missing_required_fields=tuple(sorted(missing)),
            logged_in_marker_present=page.locator(SELECTOR_LOGGED_IN).count() > 0,
            expects_feed=expects_feed,
            challenge_widget_present=page.locator(SELECTOR_CHALLENGE_WIDGET).count() > 0,
        )

    def collect_posts(self) -> list[PostObservation]:
        out: list[PostObservation] = []
        containers = self._page.locator(SELECTOR_POST)
        for index in range(containers.count()):
            node = containers.nth(index)
            hrefs = node.locator("a").evaluate_all(
                "nodes => nodes.map(n => n.getAttribute('href') || '')"
            )
            post_id = None
            for href in hrefs:
                match = POST_ID_RE.search(href)
                if match:
                    post_id = match.group(1)
                    break
            text = (node.inner_text() or "").lower()
            haystack = " ".join(hrefs).lower() + " " + text
            out.append(
                PostObservation(
                    x_post_id=post_id,
                    has_author_handle=node.locator(SELECTOR_AUTHOR).count() > 0,
                    has_created_at=node.locator(SELECTOR_TIME).count() > 0,
                    has_paper_link=any(host in haystack for host in PAPER_LINK_HOSTS),
                    has_photo=node.locator(SELECTOR_PHOTO).count() > 0,
                )
            )
        return out

    def scroll(self) -> None:
        """Scroll the feed. Keyboard only -- this class has no click of any kind."""
        self._page.mouse.wheel(0, 2000)

    def close(self) -> None:
        self._context.close()


def open_driver(cfg: ProbeConfig) -> tuple[PlaywrightXDriver, Any]:
    """Open the project Chrome profile as a persistent context. Imports Playwright here."""
    from playwright.sync_api import sync_playwright  # noqa: PLC0415 - lazy on purpose

    playwright = sync_playwright().start()
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(cfg.chrome_user_data_dir),
        channel=cfg.chrome_channel,
        headless=False,
    )
    page = context.pages[0] if context.pages else context.new_page()
    return PlaywrightXDriver(context, page), playwright


# --- logging ------------------------------------------------------------------------
class RedactingFormatter(logging.Formatter):
    """Every log line passes through :func:`redact` before it reaches a file or a terminal."""

    def format(self, record: logging.LogRecord) -> str:
        return redact(super().format(record))


def setup_logging(log_path: Path, *, verbose: bool = False) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    formatter = RedactingFormatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    LOG.handlers = [file_handler, stream_handler]


# --- CLI ----------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_probe",
        description=(
            "Probe khả thi SP1 cho nguồn X (contracts/ops/collector-probe.md). "
            "CHỈ quan sát, không ingest, không gọi server, không né gì cả."
        ),
    )
    parser.add_argument("--config", required=True, help="File JSON cấu hình probe")
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help=(
            "Số đợt trong lần gọi này (mặc định 1 — khuyến nghị). Các cổng lịch §3.1 vẫn "
            "áp: tối đa 4 đợt/ngày và cách nhau >= 60 phút."
        ),
    )
    parser.add_argument(
        "--note",
        default="",
        help="Ghi chú của Owner, nối vào unobservable_scope_vi của đợt này",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Kiểm config và các cổng rồi thoát. KHÔNG mở trình duyệt, KHÔNG chạm X.",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"Config không hợp lệ: {exc}", file=sys.stderr)
        return 2

    out_dir = cfg.output_dir
    runs_path = out_dir / RUNS_FILENAME
    ledger_path = out_dir / LEDGER_FILENAME
    setup_logging(out_dir / LOG_FILENAME, verbose=args.verbose)

    try:
        check_owner_gate(cfg)
    except GateRefused as exc:
        LOG.error("%s", exc)
        print(str(exc), file=sys.stderr)
        return 2

    existing = read_records(runs_path) if runs_path.is_file() else []
    try:
        check_schedule(existing, now=datetime.now(UTC))
    except GateRefused as exc:
        LOG.error("%s", exc)
        print(str(exc), file=sys.stderr)
        return 2

    if args.runs < 1:
        print("--runs phải >= 1", file=sys.stderr)
        return 4
    if len(existing) + args.runs > PROBE_RUN_COUNT_MAX:
        msg = (
            f"--runs {args.runs} cùng {len(existing)} đợt đã có sẽ vượt trần "
            f"{PROBE_RUN_COUNT_MAX} của §3.1."
        )
        print(msg, file=sys.stderr)
        return 2
    if args.runs > PROBE_RUNS_PER_DAY_MAX:
        msg = (
            f"--runs {args.runs} vượt §3.1 probe_runs_per_day_max = {PROBE_RUNS_PER_DAY_MAX}. "
            "Chạy --runs 1 mỗi lần, cách nhau ít nhất 60 phút, trải qua >= 3 ngày."
        )
        print(msg, file=sys.stderr)
        return 2

    if args.dry_run:
        # Redacted before printing: the Owner is likely to paste this straight back to the
        # Coordinator, and an output path on a personal machine carries the user name.
        print(
            redact(
                json.dumps(
                    {
                        "gate": "open",
                        "config": cfg.redacted_summary(),
                        "runs_recorded": len(existing),
                        "runs_file": str(runs_path),
                        "note_vi": (
                            "dry-run: cổng §6 và cổng lịch §3.1 đã qua. KHÔNG mở trình duyệt, "
                            "KHÔNG chạm X. Bỏ --dry-run để chạy thật."
                        ),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        )
        return 0

    state = _StopState()

    def _on_sigint(_signum: int, _frame: FrameType | None) -> None:
        state.interrupted = True
        LOG.warning("nhận tín hiệu dừng của Owner (ST-8); đóng đợt và ghi bản ghi")

    signal.signal(signal.SIGINT, _on_sigint)

    exit_code = 0
    for index in range(args.runs):
        if index > 0:
            wait_s = PROBE_MIN_GAP_MINUTES * 60
            LOG.info("chờ %d phút giữa hai đợt (§3.1 probe_min_gap_minutes)", PROBE_MIN_GAP_MINUTES)
            time.sleep(wait_s)
        driver, playwright = open_driver(cfg)
        try:
            seen = load_seen_ledger(ledger_path)
            record, new_digests = run_one(cfg, driver, seen_digests=seen, stop_state=state)
        finally:
            driver.close()
            playwright.stop()
        if args.note:
            record.unobservable_scope_vi = f"{record.unobservable_scope_vi} {redact(args.note)}"
        payload = append_record(runs_path, record)
        append_seen_ledger(ledger_path, new_digests)
        LOG.info(
            "đợt xong: stop_reason=%s posts_seen=%d posts_parsed_ok=%d challenge=%d",
            payload["stop_reason"],
            payload["posts_seen"],
            payload["posts_parsed_ok"],
            payload["challenge_count"],
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if payload["stop_reason"] in SOURCE_STOP_REASONS:
            LOG.error(
                "đợt dừng vì tình huống nguồn (%s). Không tự chạy tiếp, không thử lại. "
                "Xem probe/README.md §7.",
                payload["stop_reason"],
            )
            exit_code = 3
            break
        if state.interrupted:
            exit_code = 3
            break
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
