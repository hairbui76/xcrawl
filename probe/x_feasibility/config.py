"""Configuration for the SP1 probe, and the two gates that stand in front of it.

Gate 1 -- the Owner gate (``collector-probe.md`` §6, card stop condition ``SG-02``).
    Four written confirmations are required *before any run*. Item 1 (D09) was answered in
    ``OD-20260907-01``; items 2, 3 and 4 are still ``OWNER_DECISION_REQUIRED`` as of
    2026-09-07. :meth:`ProbeConfig.owner_gate` reports which are missing and
    :mod:`probe.x_feasibility.run_probe` refuses to open a browser until all four carry a
    written evidence reference. This code does not *grant* the permission -- it only
    refuses to act without it.

Gate 2 -- the profile gate (REQ-D09, prerequisite P1).
    The probe drives a Chrome profile that belongs to the project. Pointing it at the
    user's default profile is refused outright: P1 says the default profile "is not
    touched", and a config typo is exactly how it would be.

The budget fields are bounded by ``collector-probe.md`` §3 and cannot be relaxed here: a
config may ask for *less* than the contract budget, never more, and never a faster request
cadence than the ``probe_request_min_interval_ms`` floor. There is deliberately **no**
field for a user agent, a proxy, a fingerprint or an account list -- see §2 of the
contract; those are not settings that happen to be absent, they are mechanisms this probe
must not have.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

# --- contract-pinned bounds (contracts/ops/collector-probe.md §3) --------------------
#: §3.1 ``probe_run_count_min`` / ``probe_run_count_max``.
PROBE_RUN_COUNT_MIN = 5
PROBE_RUN_COUNT_MAX = 10
#: §3.1 ``probe_runs_per_day_max`` and ``probe_min_gap_minutes``.
PROBE_RUNS_PER_DAY_MAX = 4
PROBE_MIN_GAP_MINUTES = 60
#: §3.2 ``probe_max_posts_per_run`` / ``probe_max_duration_s`` / ``probe_request_min_interval_ms``.
PROBE_MAX_POSTS_PER_RUN = 200
PROBE_MAX_DURATION_S = 1800
PROBE_REQUEST_MIN_INTERVAL_MS = 2000

#: The four confirmations of ``collector-probe.md`` §6, in the contract's order.
OWNER_CONFIRMATION_KEYS: tuple[str, ...] = (
    "d09_project_chrome_profile",
    "budget_and_stop_conditions",
    "go_no_go_criteria",
    "account_risk_understood",
)

#: What each key means, quoted from §6 so an error message is readable without the contract.
OWNER_CONFIRMATION_TEXT_VI: dict[str, str] = {
    "d09_project_chrome_profile": (
        "§6.1 — D09: dùng Chrome profile riêng của dự án (đã trả lời: OD-20260907-01)."
    ),
    "budget_and_stop_conditions": (
        "§6.2 — Ngân sách §3 và điều kiện dừng §4 là chấp nhận được với tài khoản X của Owner."
    ),
    "go_no_go_criteria": ("§6.3 — Tiêu chí go/no-go §7 là tiêu chí Owner đồng ý dùng để kết luận."),
    "account_risk_understood": (
        "§6.4 — Hiểu rằng probe chạy trên tài khoản X thật của Owner và mang rủi ro bị hạn "
        "chế tài khoản (REQ-A7), rủi ro đó không kiểm chứng được trước."
    ),
}

#: Hosts the probe is allowed to open. ``SL-4`` (``chrome_scope: x_only``): the collector's
#: Chrome only ever deals with X. arXiv/OpenAlex metadata is the server's job (``SL-5``).
ALLOWED_HOSTS: frozenset[str] = frozenset({"x.com", "www.x.com", "twitter.com", "www.twitter.com"})

#: Path fragments of the *default* Chrome profile on each OS. A ``chrome_user_data_dir``
#: whose resolved path is one of these -- or lives inside one -- is refused (P1).
DEFAULT_PROFILE_MARKERS: tuple[str, ...] = (
    ".config/google-chrome",
    ".config/chromium",
    "Library/Application Support/Google/Chrome",
    "Library/Application Support/Chromium",
    "AppData/Local/Google/Chrome/User Data",
    "AppData/Local/Chromium/User Data",
)

#: Keys that must never appear in a probe config. Their presence is not a validation
#: warning -- it is a §2 boundary violation, and the config is rejected.
FORBIDDEN_CONFIG_KEYS: frozenset[str] = frozenset(
    {
        "user_agent",
        "userAgent",
        "proxy",
        "proxies",
        "accounts",
        "account_rotation",
        "fingerprint",
        "captcha_solver",
        "captcha_service",
        "solver_api_key",
        "stealth",
        "evasion",
    }
)


class ConfigError(ValueError):
    """The configuration is unusable. Always names the field and the contract clause."""


@dataclass(frozen=True)
class OwnerConfirmation:
    """One of the four §6 confirmations, plus where it was written down."""

    confirmed: bool
    #: Where the Owner's written answer lives (a decision record id, a packet path, a
    #: dated quote). An empty reference is treated as *not confirmed*: §6 asks for the
    #: confirmation "bằng văn bản", so a bare ``true`` is not a confirmation.
    evidence_ref: str = ""

    @property
    def is_satisfied(self) -> bool:
        return self.confirmed and bool(self.evidence_ref.strip())


@dataclass(frozen=True)
class OwnerGate:
    """Result of evaluating the §6 gate. ``is_open`` is the only thing that opens Chrome."""

    satisfied: tuple[str, ...]
    missing: tuple[str, ...]

    @property
    def is_open(self) -> bool:
        return not self.missing

    def explain_vi(self) -> str:
        if self.is_open:
            return "Cổng §6 mở: đủ bốn xác nhận bằng văn bản của Owner."
        lines = [
            "OWNER_DECISION_REQUIRED — chưa đủ bốn xác nhận của "
            "contracts/ops/collector-probe.md §6; probe KHÔNG được chạy (card SG-02).",
            "Còn thiếu:",
        ]
        lines += [f"  - {key}: {OWNER_CONFIRMATION_TEXT_VI[key]}" for key in self.missing]
        return "\n".join(lines)


@dataclass(frozen=True)
class ProbeConfig:
    """A validated probe configuration. Construct it with :func:`load_config`."""

    chrome_user_data_dir: Path
    search_terms: tuple[str, ...]
    output_dir: Path
    owner_confirmations: dict[str, OwnerConfirmation]
    x_base_url: str = "https://x.com"
    chrome_channel: str = "chrome"
    max_posts_per_run: int = PROBE_MAX_POSTS_PER_RUN
    max_duration_s: int = PROBE_MAX_DURATION_S
    request_min_interval_ms: int = PROBE_REQUEST_MIN_INTERVAL_MS
    #: Upper bound on scroll steps per search term. A guard against an infinite loop when
    #: the feed keeps yielding; the real stop conditions are §4, not this number.
    max_scroll_steps_per_term: int = 60
    #: Extra state markers, ADDED to :mod:`probe.x_feasibility.signals` defaults. Additive
    #: only: a config can teach the detector a new way to notice a stop condition, never
    #: unteach one. Removing a marker would weaken a §4 stop condition by configuration.
    extra_markers: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # -- gates ---------------------------------------------------------------------
    def owner_gate(self) -> OwnerGate:
        """Evaluate ``collector-probe.md`` §6 over the four confirmations."""
        satisfied, missing = [], []
        for key in OWNER_CONFIRMATION_KEYS:
            confirmation = self.owner_confirmations.get(key)
            if confirmation is not None and confirmation.is_satisfied:
                satisfied.append(key)
            else:
                missing.append(key)
        return OwnerGate(satisfied=tuple(satisfied), missing=tuple(missing))

    def search_url(self, term: str) -> str:
        """The live-search URL for one term. Only ever a host from :data:`ALLOWED_HOSTS`."""
        from urllib.parse import quote

        return f"{self.x_base_url.rstrip('/')}/search?q={quote(term)}&f=live"

    def redacted_summary(self) -> dict[str, Any]:
        """Config for a log or an evidence manifest, with the profile path removed.

        The profile path contains the OS user name; §5 forbids writing absolute paths
        carrying a user name into the record. Only the *depth* and the leaf name survive,
        which is enough to tell two project profiles apart.
        """
        return {
            "chrome_profile_leaf": self.chrome_user_data_dir.name,
            "chrome_channel": self.chrome_channel,
            "x_base_url": self.x_base_url,
            "search_terms_count": len(self.search_terms),
            "max_posts_per_run": self.max_posts_per_run,
            "max_duration_s": self.max_duration_s,
            "request_min_interval_ms": self.request_min_interval_ms,
            "owner_gate_open": self.owner_gate().is_open,
        }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConfigError(message)


def _check_profile_dir(raw: str) -> Path:
    path = Path(raw).expanduser()
    _require(
        path.is_absolute(),
        f"chrome_user_data_dir phải là đường dẫn tuyệt đối (REQ-D09 / P1); nhận: {raw!r}",
    )
    as_posix = path.as_posix()
    for marker in DEFAULT_PROFILE_MARKERS:
        if as_posix.endswith(marker) or f"/{marker}/" in f"{as_posix}/":
            raise ConfigError(
                "chrome_user_data_dir trỏ vào profile Chrome MẶC ĐỊNH của người dùng "
                f"(khớp {marker!r}). Prerequisite P1 của contracts/ops/collector-probe.md "
                "yêu cầu profile RIÊNG của dự án và nói rõ profile mặc định không bị chạm. "
                "Tạo một thư mục riêng, ví dụ ~/rr-x-profile, rồi đăng nhập X trong đó."
            )
    return path


def _check_budgets(data: dict[str, Any]) -> tuple[int, int, int]:
    max_posts = int(data.get("max_posts_per_run", PROBE_MAX_POSTS_PER_RUN))
    max_duration = int(data.get("max_duration_s", PROBE_MAX_DURATION_S))
    interval = int(data.get("request_min_interval_ms", PROBE_REQUEST_MIN_INTERVAL_MS))
    _require(
        1 <= max_posts <= PROBE_MAX_POSTS_PER_RUN,
        f"max_posts_per_run phải trong 1..{PROBE_MAX_POSTS_PER_RUN} "
        "(collector-probe.md §3.2 probe_max_posts_per_run); config không được nới ngân sách.",
    )
    _require(
        1 <= max_duration <= PROBE_MAX_DURATION_S,
        f"max_duration_s phải trong 1..{PROBE_MAX_DURATION_S} "
        "(collector-probe.md §3.2 probe_max_duration_s).",
    )
    _require(
        interval >= PROBE_REQUEST_MIN_INTERVAL_MS,
        f"request_min_interval_ms phải >= {PROBE_REQUEST_MIN_INTERVAL_MS} "
        "(collector-probe.md §3.2 probe_request_min_interval_ms là SÀN, không phải mặc định).",
    )
    return max_posts, max_duration, interval


def parse_config(data: dict[str, Any], *, base_dir: Path | None = None) -> ProbeConfig:
    """Validate an already-parsed config mapping. Raises :class:`ConfigError`."""
    forbidden = sorted(FORBIDDEN_CONFIG_KEYS.intersection(data))
    if forbidden:
        raise ConfigError(
            f"Config chứa khóa bị cấm: {forbidden}. contracts/ops/collector-probe.md §2 — "
            "không giả fingerprint/user-agent, không proxy, không luân chuyển account, "
            "không dịch vụ giải CAPTCHA. Đây là ràng buộc, không phải tham số."
        )

    for key in ("chrome_user_data_dir", "search_terms"):
        _require(key in data, f"Thiếu trường bắt buộc {key!r} trong config.")

    profile_dir = _check_profile_dir(str(data["chrome_user_data_dir"]))

    terms_raw = data["search_terms"]
    _require(
        isinstance(terms_raw, list) and bool(terms_raw),
        "search_terms phải là mảng không rỗng (tag ở đây CHỈ để tìm kiếm — REQ-D24).",
    )
    terms = tuple(str(t).strip() for t in terms_raw)
    _require(all(terms), "search_terms không được chứa chuỗi rỗng.")
    _require(
        len(terms) <= 200,
        "search_terms tối đa 200 mục (worker-assignment.schema.json §search_config.tags).",
    )

    base_url = str(data.get("x_base_url", "https://x.com"))
    host = (urlsplit(base_url).hostname or "").lower()
    _require(
        host in ALLOWED_HOSTS,
        f"x_base_url phải trỏ tới X ({sorted(ALLOWED_HOSTS)}); nhận host {host!r}. "
        "SL-4 chrome_scope=x_only: Chrome của collector CHỈ lo X.",
    )
    _require(
        urlsplit(base_url).scheme == "https",
        "x_base_url phải dùng https.",
    )

    max_posts, max_duration, interval = _check_budgets(data)

    out_raw = str(data.get("output_dir", "evidence/runs/SP1-x-feasibility"))
    out_path = Path(out_raw).expanduser()
    if not out_path.is_absolute():
        out_path = (base_dir or Path.cwd()) / out_path

    confirmations: dict[str, OwnerConfirmation] = {}
    raw_conf = data.get("owner_confirmations", {})
    _require(isinstance(raw_conf, dict), "owner_confirmations phải là object.")
    unknown = sorted(set(raw_conf) - set(OWNER_CONFIRMATION_KEYS))
    _require(
        not unknown,
        f"owner_confirmations có khóa lạ {unknown}; bốn khóa hợp lệ: "
        f"{list(OWNER_CONFIRMATION_KEYS)} (collector-probe.md §6).",
    )
    for key in OWNER_CONFIRMATION_KEYS:
        item = raw_conf.get(key) or {}
        _require(isinstance(item, dict), f"owner_confirmations.{key} phải là object.")
        confirmations[key] = OwnerConfirmation(
            confirmed=bool(item.get("confirmed", False)),
            evidence_ref=str(item.get("evidence_ref", "")),
        )

    extra_raw = data.get("extra_markers", {})
    _require(isinstance(extra_raw, dict), "extra_markers phải là object {state: [chuỗi]}.")
    extra: dict[str, tuple[str, ...]] = {}
    for state, markers in extra_raw.items():
        _require(
            isinstance(markers, list) and all(isinstance(m, str) for m in markers),
            f"extra_markers.{state} phải là mảng chuỗi.",
        )
        extra[str(state)] = tuple(str(m) for m in markers)

    steps = int(data.get("max_scroll_steps_per_term", 60))
    _require(1 <= steps <= 500, "max_scroll_steps_per_term phải trong 1..500.")

    return ProbeConfig(
        chrome_user_data_dir=profile_dir,
        search_terms=terms,
        output_dir=out_path,
        owner_confirmations=confirmations,
        x_base_url=base_url,
        chrome_channel=str(data.get("chrome_channel", "chrome")),
        max_posts_per_run=max_posts,
        max_duration_s=max_duration,
        request_min_interval_ms=interval,
        max_scroll_steps_per_term=steps,
        extra_markers=extra,
    )


def load_config(path: str | Path) -> ProbeConfig:
    """Read and validate a JSON config file."""
    config_path = Path(path).expanduser()
    if not config_path.is_file():
        raise ConfigError(f"Không tìm thấy file config: {config_path}")
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - message is the whole value
        raise ConfigError(f"Config không phải JSON hợp lệ: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError("Config phải là một object JSON ở cấp cao nhất.")
    return parse_config(data, base_dir=config_path.parent)
