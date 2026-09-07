"""State-signal detector for the §4 stop conditions of ``contracts/ops/collector-probe.md``.

This module is **pure**: it takes a :class:`PageObservation` -- a snapshot of what a page
looked like -- and returns one :class:`Detection`. It never touches a browser, a network,
or a clock. That is what makes it testable offline: ``tests/contract/`` feeds it hand-written
synthetic HTML and asserts the decision, with no Playwright and no X.

Two vocabularies, on purpose
----------------------------
``stop_reason`` exists twice in the contracts and the two spellings are **not** a defect:

* the **run** vocabulary (``contracts/state/run.yaml`` §1, and the probe record of
  ``collector-probe.md`` §5) uses ``captcha``;
* the **wire** vocabulary of ``worker.report_stop`` (``contracts/http/openapi.yaml``,
  ``contracts/ports.yaml``) uses ``challenge_required``.

The probe writes the *run* vocabulary, because §5 says its first six values match
``run.yaml``. :attr:`Detection.wire_stop_reason` records the wire spelling as well, so the
collector card that does call ``worker.report_stop`` inherits the mapping instead of
re-deriving it. The probe itself never calls the wire (M0 is dry-run, §1 P6).

Fail closed
-----------
The default when a page cannot be recognised as a healthy feed is **stop**, not continue:
:data:`ST_7` (``source_layout_changed``). A detector that guesses "probably fine" on an
unknown page turns every unrecognised block into a silent zero-post run. §7 GO-6 then reads
that as a clean probe. Refusing to parse is the honest outcome; §4 has no condition that
permits "retry and continue".
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

# --- §4 stop condition ids ----------------------------------------------------------
ST_1 = "ST-1"  # CAPTCHA / verification challenge
ST_2 = "ST-2"  # session expired / logged out
ST_3 = "ST-3"  # access blocked (403, block page, account limited)
ST_4 = "ST-4"  # rate limit signal (429, "slow down" page)
ST_5 = "ST-5"  # probe_max_posts_per_run reached
ST_6 = "ST-6"  # probe_max_duration_s reached
ST_7 = "ST-7"  # feed layout changed beyond parsing
ST_8 = "ST-8"  # Owner pressed stop

#: No stop condition met: keep observing within budget.
CONTINUE = "CONTINUE"


@dataclass(frozen=True)
class PageObservation:
    """Everything the detector is allowed to look at.

    Deliberately small and serialisable: a test can build one by hand, and a real run
    builds one from the live page without the detector ever seeing the page object.

    ``visible_text`` is lower-cased before matching, so markers are written lower-case.
    """

    #: Final URL after redirects. Query string included -- X moves the session to
    #: ``/i/flow/login`` and challenges to ``/account/access`` by URL alone.
    url: str = ""
    title: str = ""
    visible_text: str = ""
    #: HTTP status of the main document, when the driver exposes one; ``None`` when the
    #: navigation was a client-side transition and no status was observed.
    http_status: int | None = None
    #: Count of post containers found by the structural selector.
    post_node_count: int = 0
    #: Of those, how many yielded every required field.
    parsed_ok_count: int = 0
    #: Names of required fields that were missing on at least one post container.
    missing_required_fields: tuple[str, ...] = ()
    #: True when a marker that only exists for a logged-in session was present.
    logged_in_marker_present: bool = True
    #: True when the page is expected to carry a feed at all (a search results page).
    expects_feed: bool = True
    #: True when a CAPTCHA/verification widget was found structurally (iframe, testid).
    challenge_widget_present: bool = False


@dataclass(frozen=True)
class Detection:
    """One decision about one observation."""

    #: One of the ``ST_*`` ids, or :data:`CONTINUE`.
    stop_condition: str
    #: The probe record value for ``collector-probe.md`` §5 ``stop_reason``; ``None`` while
    #: the run continues.
    stop_reason: str | None
    #: ``contracts/errors.yaml`` code, when the condition maps to one. ``limit_reached``
    #: and ``operator_stop`` map to no error: they are not failures (AMD-B02).
    error_code: str | None
    #: The ``worker.report_stop`` wire spelling, for the collector card. ``None`` when the
    #: condition has no wire counterpart (``operator_stop`` is probe-only, §5).
    wire_stop_reason: str | None
    #: Which counter of §5 this increments; ``None`` for the limit conditions.
    counter_field: str | None
    #: Short, redaction-safe reason. Never contains page text, cookies or a URL query.
    detail_vi: str
    #: The marker that fired, for the log. Never the surrounding page text.
    matched_marker: str | None = None

    @property
    def should_stop(self) -> bool:
        return self.stop_condition != CONTINUE


# --- §4 row -> record vocabulary ----------------------------------------------------
#: The one place the mapping lives. ``tests/contract/test_x_probe_signals.py`` asserts it
#: against ``contracts/state/run.yaml``, ``contracts/errors.yaml``, the openapi wire enum
#: and the collection fixtures -- so a contract edit breaks the test, not the run.
STOP_CONDITION_MAP: dict[str, dict[str, str | None]] = {
    ST_1: {
        "stop_reason": "captcha",
        "error_code": "X_CHALLENGE_REQUIRED",
        "wire_stop_reason": "challenge_required",
        "counter_field": "challenge_count",
    },
    ST_2: {
        "stop_reason": "session_expired",
        "error_code": "X_CHALLENGE_REQUIRED",
        "wire_stop_reason": "session_expired",
        "counter_field": "session_expired_count",
    },
    ST_3: {
        "stop_reason": "source_blocked",
        "error_code": "X_ACCESS_BLOCKED",
        "wire_stop_reason": "source_blocked",
        "counter_field": "blocked_count",
    },
    ST_4: {
        "stop_reason": "rate_limited",
        "error_code": "RATE_LIMITED",
        "wire_stop_reason": "rate_limited",
        "counter_field": "rate_limited_count",
    },
    ST_5: {
        "stop_reason": "limit_reached",
        "error_code": None,
        "wire_stop_reason": "limit_reached",
        "counter_field": None,
    },
    ST_6: {
        "stop_reason": "limit_reached",
        "error_code": None,
        "wire_stop_reason": "limit_reached",
        "counter_field": None,
    },
    ST_7: {
        "stop_reason": "source_layout_changed",
        "error_code": "SOURCE_LAYOUT_CHANGED",
        "wire_stop_reason": "source_layout_changed",
        "counter_field": "parser_degraded_count",
    },
    ST_8: {
        "stop_reason": "operator_stop",
        "error_code": None,
        # §5: `operator_stop` is the probe's OWN value; real operation has no manual stop
        # button for the collector, so there is no wire spelling to map to.
        "wire_stop_reason": None,
        "counter_field": None,
    },
}


# --- markers ------------------------------------------------------------------------
# PROVISIONAL. These strings are what X's interface is *expected* to say; this package was
# written without network access, so not one of them has been observed on a live page. The
# runbook (probe/README.md §6) tells the Owner to add whatever their own account actually
# shows via `extra_markers`, which is additive only. A marker that never fires costs
# nothing; the fail-closed default (ST-7) catches the page a marker missed.
CHALLENGE_MARKERS: tuple[str, ...] = (
    "xác minh bạn là con người",
    "xác minh danh tính",
    "hãy xác minh",
    "verify you are human",
    "verify you're human",
    "verify your identity",
    "confirm your identity",
    "we need to confirm",
    "unusual activity",
    "hoạt động bất thường",
    "prove you're not a robot",
    "solve this puzzle",
    "recaptcha",
    "arkose",
    "hcaptcha",
)
SESSION_EXPIRED_MARKERS: tuple[str, ...] = (
    "đăng nhập vào x",
    "sign in to x",
    "log in to x",
    "sign in to twitter",
    "phiên đăng nhập đã hết hạn",
    "your session has expired",
    "you are not logged in",
)
BLOCKED_MARKERS: tuple[str, ...] = (
    "tài khoản của bạn đã bị khóa",
    "tài khoản của bạn bị tạm ngưng",
    "account has been locked",
    "account is suspended",
    "account has been suspended",
    "your account is temporarily restricted",
    "access denied",
    "truy cập bị từ chối",
    "you are not authorized",
    "this request looks automated",
)
RATE_LIMIT_MARKERS: tuple[str, ...] = (
    "rate limit exceeded",
    "vượt quá giới hạn",
    "bạn đã thao tác quá nhanh",
    "you are rate limited",
    "too many requests",
    "please wait a few moments",
    "try again later",
    "thử lại sau",
    "slow down",
)

#: URL path fragments that identify a state on their own, before any text matching.
CHALLENGE_URL_FRAGMENTS: tuple[str, ...] = ("/account/access", "/i/flow/challenge", "/challenge")
SESSION_URL_FRAGMENTS: tuple[str, ...] = ("/i/flow/login", "/login", "/i/flow/signup")

#: Fields a post container must yield for the probe to count it as parsed. Missing any of
#: them on a container is a §4 ST-7 signal, never a guessed value (I03; fixture
#: ``acceptance/fixtures/collection/a-feed-layout-changed.json`` forbids guessing).
REQUIRED_POST_FIELDS: tuple[str, ...] = ("x_post_id", "author.handle", "created_at")

#: Below this share of parsed posts the feed counts as unreadable even when containers were
#: found. PROVISIONAL: it is GO-5's 0.90 read as a *per-page* tripwire so a run stops at the
#: first degraded page instead of finishing a full budget of unparseable containers.
PARSE_DEGRADED_RATIO = 0.90


@dataclass(frozen=True)
class SignalRule:
    """One ordered rule. ``matches`` returns the marker that fired, or ``None``."""

    stop_condition: str
    name: str
    matches: Callable[[PageObservation, MarkerSet], str | None]


@dataclass(frozen=True)
class MarkerSet:
    """Default markers plus the config's additive extras."""

    challenge: tuple[str, ...] = CHALLENGE_MARKERS
    session_expired: tuple[str, ...] = SESSION_EXPIRED_MARKERS
    blocked: tuple[str, ...] = BLOCKED_MARKERS
    rate_limited: tuple[str, ...] = RATE_LIMIT_MARKERS
    extra: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def for_state(self, state: str) -> tuple[str, ...]:
        base: tuple[str, ...] = getattr(self, state)
        return base + tuple(self.extra.get(state, ()))


def _first_hit(haystack: str, needles: Sequence[str]) -> str | None:
    for needle in needles:
        if needle in haystack:
            return needle
    return None


def _url_hit(url: str, fragments: Sequence[str]) -> str | None:
    lowered = url.lower()
    for fragment in fragments:
        if fragment in lowered:
            return f"url:{fragment}"
    return None


def _match_blocked(obs: PageObservation, markers: MarkerSet) -> str | None:
    if obs.http_status in (401, 403):
        return f"http:{obs.http_status}"
    return _first_hit(obs.visible_text, markers.for_state("blocked"))


def _match_rate_limited(obs: PageObservation, markers: MarkerSet) -> str | None:
    if obs.http_status == 429:
        return "http:429"
    return _first_hit(obs.visible_text, markers.for_state("rate_limited"))


def _match_challenge(obs: PageObservation, markers: MarkerSet) -> str | None:
    if obs.challenge_widget_present:
        return "widget:challenge"
    return _url_hit(obs.url, CHALLENGE_URL_FRAGMENTS) or _first_hit(
        obs.visible_text, markers.for_state("challenge")
    )


def _match_session_expired(obs: PageObservation, markers: MarkerSet) -> str | None:
    hit = _url_hit(obs.url, SESSION_URL_FRAGMENTS)
    if hit:
        return hit
    text_hit = _first_hit(obs.visible_text, markers.for_state("session_expired"))
    if text_hit:
        return text_hit
    if obs.expects_feed and not obs.logged_in_marker_present:
        return "marker:logged_in_absent"
    return None


def _match_layout_changed(obs: PageObservation, _markers: MarkerSet) -> str | None:
    if obs.missing_required_fields:
        return f"missing_fields:{','.join(sorted(obs.missing_required_fields))}"
    if not obs.expects_feed:
        return None
    if obs.post_node_count == 0:
        return "no_post_container"
    if obs.parsed_ok_count < obs.post_node_count * PARSE_DEGRADED_RATIO:
        return f"parse_ratio:{obs.parsed_ok_count}/{obs.post_node_count}" f"<{PARSE_DEGRADED_RATIO}"
    return None


#: Evaluation order, and why it is this order.
#:
#: 1. ``ST-3`` blocked  -- "X does not let you in" is the most severe reading; a page that
#:    says both "blocked" and "try again later" is a block, not a rate limit.
#: 2. ``ST-4`` rate limited -- X let you in and asked you to slow down. Kept *above* the
#:    challenge rules because a 429 body sometimes also renders a login prompt.
#: 3. ``ST-1`` challenge -- verification is checked before "logged out" because the access
#:    challenge page also lacks the logged-in markers; reading it as a session expiry would
#:    invite a re-login attempt, and I10 forbids anything that looks like auto-recovery.
#: 4. ``ST-2`` session expired.
#: 5. ``ST-7`` layout changed -- last, because it is the fail-closed default: anything that
#:    was not recognised as one of the four source states, and is not a readable feed, is
#:    "we got in but cannot read", which is the condition a developer must fix.
RULES: tuple[SignalRule, ...] = (
    SignalRule(ST_3, "blocked", _match_blocked),
    SignalRule(ST_4, "rate_limited", _match_rate_limited),
    SignalRule(ST_1, "challenge", _match_challenge),
    SignalRule(ST_2, "session_expired", _match_session_expired),
    SignalRule(ST_7, "layout_changed", _match_layout_changed),
)

_DETAIL_VI: dict[str, str] = {
    ST_1: "X đòi xác minh. Dừng đợt và chờ người; probe không bao giờ tự bấm xác minh (I10).",
    ST_2: "Phiên đăng nhập không còn hiệu lực. Dừng đợt và báo; probe không tự đăng nhập lại.",
    ST_3: "X chặn truy cập. Dừng hẳn probe và báo Owner; không luân chuyển gì (§2).",
    ST_4: (
        "Nguồn báo giới hạn nhịp. Đóng đợt, KHÔNG thử lại trong đợt; "
        "đợt theo lịch kế tiếp chạy bình thường."
    ),
    ST_5: "Chạm ngân sách số bài của đợt. Không phải lỗi (AMD-B02).",
    ST_6: "Chạm ngân sách thời gian của đợt. Không phải lỗi (AMD-B02).",
    ST_7: "Không bóc được trường bắt buộc từ feed. Dừng và ghi tên trường thiếu; không đoán.",
    ST_8: "Owner bấm dừng.",
}


def _build(stop_condition: str, marker: str | None) -> Detection:
    row = STOP_CONDITION_MAP[stop_condition]
    return Detection(
        stop_condition=stop_condition,
        stop_reason=row["stop_reason"],
        error_code=row["error_code"],
        wire_stop_reason=row["wire_stop_reason"],
        counter_field=row["counter_field"],
        detail_vi=_DETAIL_VI[stop_condition],
        matched_marker=marker,
    )


CONTINUE_DETECTION = Detection(
    stop_condition=CONTINUE,
    stop_reason=None,
    error_code=None,
    wire_stop_reason=None,
    counter_field=None,
    detail_vi="Không có tín hiệu dừng; tiếp tục trong ngân sách.",
)


def detect(obs: PageObservation, markers: MarkerSet | None = None) -> Detection:
    """Classify one page observation against §4. Never raises; never continues on doubt."""
    marker_set = markers or MarkerSet()
    text_lower = obs.visible_text.lower()
    normalised = PageObservation(
        url=obs.url,
        title=obs.title,
        visible_text=text_lower,
        http_status=obs.http_status,
        post_node_count=obs.post_node_count,
        parsed_ok_count=obs.parsed_ok_count,
        missing_required_fields=obs.missing_required_fields,
        logged_in_marker_present=obs.logged_in_marker_present,
        expects_feed=obs.expects_feed,
        challenge_widget_present=obs.challenge_widget_present,
    )
    for rule in RULES:
        hit = rule.matches(normalised, marker_set)
        if hit is not None:
            return _build(rule.stop_condition, hit)
    return CONTINUE_DETECTION


def detect_limit(
    *, posts_seen: int, max_posts: int, elapsed_s: float, max_duration_s: int
) -> Detection | None:
    """§4 ST-5 / ST-6. Evaluated as OR: whichever threshold is hit first wins.

    Posts are checked before duration so a run that hits both in the same tick records
    ``limit_kind = posts``, matching ``e-limit-reached-stop``'s reading of a budget stop.
    """
    if posts_seen >= max_posts:
        return _build(ST_5, f"posts:{posts_seen}>={max_posts}")
    if elapsed_s >= max_duration_s:
        return _build(ST_6, f"duration:{int(elapsed_s)}s>={max_duration_s}s")
    return None


def operator_stop() -> Detection:
    """§4 ST-8 -- the Owner interrupted the run."""
    return _build(ST_8, "operator")


def limit_kind_for(detection: Detection) -> str | None:
    """§5 ``limit_kind``: NOT NULL exactly when ``stop_reason = limit_reached``."""
    if detection.stop_condition == ST_5:
        return "posts"
    if detection.stop_condition == ST_6:
        return "duration"
    return None
