"""``MOD-research-connector`` -- the two ``research.*`` operations and the boundary they run behind.

===============================  ==============================  =========================
operation id                     function                        transaction
===============================  ==============================  =========================
``research.fetch_work_metadata`` :func:`fetch_work_metadata`     none (one log INSERT)
``research.get_connector_health`` :func:`get_connector_health`   none (read, in memory)
===============================  ==============================  =========================

What this module refuses, and what it no longer refuses
------------------------------------------------------
``contracts/retry-policy.yaml`` ``research_connector_rate_limit`` used to carry four
``null`` values under ``status: PLACEHOLDER_KC``. **Version 0.8.0 resolved all four**, each
with a URL, a retrieval date of 2026-09-07 and a verbatim quotation, under the new status
``DOCS_derived``:

* arXiv -- one request every three seconds, **and a single connection at a time**;
* OpenAlex -- 100 requests per second, plus a daily budget stated in money rather than in
  calls and therefore observable only at run time through ``X-RateLimit-*`` headers;
* neither source's current documentation requires the caller to identify itself.

So card §10 ``SG-A6``'s condition -- "the four values are still ``null``" -- **no longer
holds**, and the shipped :class:`ConnectorSettings` now carries those documented rates. Two
things did *not* change and are worth stating because both look like candidates for tidying:

1. ``min_interval_ms = 3000`` stays, and stays the binding constraint. For arXiv it happens
   to equal the documented rate; for OpenAlex it is roughly 300× slower than permitted, and
   :meth:`SourceConfig.effective_interval_ms` takes the **stricter** of the two on purpose.
   Learning a source's real limit is a reason to be no faster than it, never a licence to
   speed up to it (the contract's ``rationale_vi`` says this in as many words).
2. The ``SG-IDENT`` mechanism stays in the code even though nothing triggers it today. The
   contract's ``identification.rule_vi`` is explicit: "``SG-IDENT`` KHÔNG được xoá chỉ vì hôm
   nay nó không kích hoạt." A source that starts demanding identification is configured with
   ``requires_contact_identity=True`` and is then not called until the identity exists.

What a deployment must still supply is **where each API lives**. The contract cites two
*documentation* pages, not API base URLs, and no contract here states either service's API
host, so ``endpoint_template`` and ``host_allowlist`` remain configuration and remain a
refusal condition (card §10 ``SG-DOC``). ``research.get_connector_health`` reports the two
kinds of gap under separate keys so "we never read the rate" and "nobody told us the URL"
cannot be mistaken for each other.

The response *parsers* in :mod:`server.app.research.client_arxiv` and
:mod:`server.app.research.client_openalex` remain the one place a wire shape is assumed, and
the handoff records that as a limitation E3 must close.

Network boundary
----------------
``contracts/ops/internet-boundary.md`` §3.2, enforced here rather than trusted:
``https`` only; host on the configured **allowlist** (an allow list, never a block list);
DNS resolved, every resolved address checked against the loopback/private/link-local/
metadata ranges, and the connection made to the **checked address**; at most three
redirects with the whole rule set re-applied at each hop; connect/total timeouts; a cap on
decompressed response bytes. A violation means **no request** (or an aborted one) and
``SOURCE_METADATA_UNAVAILABLE`` for that item -- never a guessed DOI (CN-6, I03).
"""

from __future__ import annotations

import hashlib
import ipaddress
import socket
import time
from collections import deque
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from typing import Any, Final, Literal
from urllib.parse import quote, urlsplit, urlunsplit

import httpx
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.identity.normalization import (
    REJECT,
    ArxivId,
    IdScheme,
    normalize_arxiv,
    normalize_doi,
)
from server.app.research.repository import (
    SourceFetchLogRepository,
    SourceFetchLogRow,
    new_ulid,
)

# --------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------

#: contracts/errors.yaml §details_safe_keys, verbatim. A key outside its code's set is
#: refused by the producer ("Khóa lạ ⇒ producer tự từ chối, không gửi ra").
DETAILS_SAFE_KEYS: Final[dict[ErrorCode, frozenset[str]]] = {
    ErrorCode.SOURCE_METADATA_UNAVAILABLE: frozenset(
        {"target_key", "connector_name", "attempt_number", "retry_after_ms"}
    ),
    ErrorCode.RATE_LIMITED: frozenset(
        {"source_kind", "retry_after_ms", "attempt_number", "window_seconds", "rate_limited_at"}
    ),
    ErrorCode.CAPABILITY_DENIED: frozenset(
        {"module_id", "denied_capability_kind", "forbidden_edge_ref"}
    ),
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.NOT_FOUND: frozenset({"operation_id", "resource_kind"}),
    ErrorCode.INTERNAL: frozenset({"correlation_id", "operation_id"}),
}

#: contracts/errors.yaml message_safe templates for the codes card §7 assigns to this module.
MESSAGE_SAFE: Final[dict[ErrorCode, str]] = {
    ErrorCode.SOURCE_METADATA_UNAVAILABLE: (
        "Chưa lấy được thông tin bài báo từ nguồn học thuật. " "Mục hiển thị ở mức “chỉ có post”."
    ),
    ErrorCode.RATE_LIMITED: "Nguồn đang giới hạn nhịp truy cập. Hệ thống chờ rồi thử lại.",
    ErrorCode.CAPABILITY_DENIED: "Thao tác bị chặn ở mức nền tảng.",
    ErrorCode.VALIDATION_ERROR: "Dữ liệu gửi lên không hợp lệ.",
    ErrorCode.NOT_FOUND: "Không tìm thấy mục bạn yêu cầu.",
    ErrorCode.INTERNAL: "Có lỗi hệ thống. Trạng thái của thao tác chưa xác định.",
}

HTTP_STATUS: Final[dict[ErrorCode, int]] = {
    ErrorCode.SOURCE_METADATA_UNAVAILABLE: 502,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.CAPABILITY_DENIED: 403,
    ErrorCode.VALIDATION_ERROR: 400,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.INTERNAL: 500,
}

#: The connector's own name, used as ``details_safe.connector_name``. Not a host name: the
#: envelope must not leak which URL was attempted (errors.yaml §redaction_vi for
#: SOURCE_METADATA_UNAVAILABLE, "Không ghi URL đầy đủ do model đề xuất").
CONNECTOR_NAME: Final[str] = "research-connector"
MODULE_ID: Final[str] = "MOD-research-connector"

SourceType = Literal["arxiv_api", "openalex_api"]


class ResearchError(Exception):
    """A registered error code plus only the envelope fields the contract permits.

    It never carries a URL, a redirect chain, a header or a response body: an envelope that
    cannot hold them cannot leak them (SRC-PLAN §5.1, errors.yaml §redaction).
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        details_safe: Mapping[str, Any] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.details_safe: dict[str, Any] = dict(details_safe or {})
        self.retry_after_ms = retry_after_ms
        unknown = set(self.details_safe) - DETAILS_SAFE_KEYS[code]
        if unknown:
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")

    @property
    def http_status(self) -> int:
        return HTTP_STATUS[self.code]

    def envelope(self, correlation_id: str) -> dict[str, Any]:
        """``contracts/errors.yaml`` §error_envelope. ``scope``/``retry_class`` are read from
        the generated registry so a handler cannot grant a retry policy the contract did not."""
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": MESSAGE_SAFE[self.code],
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
            "retry_after_ms": self.retry_after_ms,
        }


class ConnectorNotConfigured(RuntimeError):
    """Refusal to start: a REQ-A6 fact is still ``null``.

    Deliberately NOT an :class:`ResearchError`. A contract error code describes something
    that happened to a request; this describes a connector that must not make requests at
    all. Callers translate it (see :func:`fetch_work_metadata`), and
    :func:`get_connector_health` reports it as ``unavailable``.
    """

    def __init__(self, source_type: SourceType, missing: Sequence[str]) -> None:
        super().__init__(f"{source_type}: refusing to run; unresolved facts: {', '.join(missing)}")
        self.source_type = source_type
        self.missing: tuple[str, ...] = tuple(missing)


class ConcurrencyLimitExceeded(RuntimeError):
    """More simultaneous connections to one source than its documentation permits.

    Raised, not queued. arXiv's terms bound parallelism explicitly, and the connector is
    single-threaded per source by construction, so arriving here means a caller broke that
    assumption -- a defect to surface, not a wait to absorb.
    """

    def __init__(self, source_type: SourceType, limit: int) -> None:
        super().__init__(f"{source_type}: more than {limit} concurrent connection(s)")
        self.source_type = source_type
        self.limit = limit


# --------------------------------------------------------------------------------------
# Settings -- every vendor fact is data, none of it is code
# --------------------------------------------------------------------------------------

#: contracts/retry-policy.yaml research_connector_rate_limit.values.min_interval_ms.
#: PROVISIONAL and deliberately conservative; NOT a claim about either source's real limit.
DEFAULT_MIN_INTERVAL_MS: Final[int] = 3000

#: contracts/ops/internet-boundary.md §3.2 -- all PROVISIONAL there, all reproduced here.
DEFAULT_MAX_REDIRECTS: Final[int] = 3
DEFAULT_CONNECT_TIMEOUT_S: Final[float] = 10.0
DEFAULT_TOTAL_TIMEOUT_S: Final[float] = 30.0
DEFAULT_MAX_RESPONSE_BYTES: Final[int] = 10 * 1024 * 1024

#: contracts/retry-policy.yaml research_connector_attempts / research_connector_backoff.
DEFAULT_ATTEMPTS: Final[int] = 2
DEFAULT_BACKOFF_S: Final[tuple[int, ...]] = (5, 30)


@dataclass(frozen=True)
class SourceRateLimit:
    """One source's documented call rate. ``None`` still means "not read from a document".

    The class keeps its ``None`` defaults even though the contract now has values. A bare
    ``SourceRateLimit()`` is "nothing was read", and that has to stay expressible: the
    resolved numbers below carry a **retrieval date**, and ``expiry_vi`` of the contract
    block says in as many words that they do not renew themselves. A type whose default was
    a number could not represent the state the project spent two packets getting out of.

    :param max_concurrent_connections: arXiv's terms constrain *parallelism* as well as
        rate. It is a separate field because it is a separate promise: obeying one request
        every three seconds while holding four sockets open still breaks the terms.
    """

    requests_per_window: int | None = None
    window_seconds: int | None = None
    max_concurrent_connections: int | None = None

    def missing_facts(self, source_type: SourceType) -> tuple[str, ...]:
        prefix = "arxiv" if source_type == "arxiv_api" else "openalex"
        missing: list[str] = []
        if self.requests_per_window is None:
            missing.append(f"{prefix}_requests_per_window")
        if self.window_seconds is None:
            missing.append(f"{prefix}_window_seconds")
        return tuple(missing)

    @property
    def interval_ms(self) -> int | None:
        """The documented spacing between two requests, in milliseconds."""
        if self.requests_per_window is None or self.window_seconds is None:
            return None
        if self.requests_per_window <= 0 or self.window_seconds <= 0:
            return None
        return int(self.window_seconds * 1000 / self.requests_per_window)


#: The date the four REQ-A6 facts were read from the sources, copied from
#: ``contracts/retry-policy.yaml`` ``research_connector_rate_limit.sources[*].retrieved_at``.
#: It travels with the numbers because the contract's ``expiry_vi`` insists it must: "Dữ kiện
#: có hạn dùng ... KHÔNG tự gia hạn." A repeated ``429`` under these limits is a signal to
#: re-read the source and open a CR, never to edit a number here.
CONTRACT_RATE_FACTS_RETRIEVED_AT: Final[str] = "2026-09-07"

#: arXiv, from ``https://info.arxiv.org/help/api/tou.html``: "make no more than one request
#: every three seconds, and limit requests to a single connection at a time."
CONTRACT_ARXIV_RATE_LIMIT: Final[SourceRateLimit] = SourceRateLimit(
    requests_per_window=1,
    window_seconds=3,
    max_concurrent_connections=1,
)

#: OpenAlex, from ``https://help.openalex.org/api/authentication/``: "Two things return
#: `429 Too Many Requests`: exceeding your daily budget, or making more than 100 requests per
#: second." The daily budget is stated in money, not in calls, so it is deliberately absent
#: here -- it is observable only at run time through the ``X-RateLimit-*`` headers.
CONTRACT_OPENALEX_RATE_LIMIT: Final[SourceRateLimit] = SourceRateLimit(
    requests_per_window=100,
    window_seconds=1,
    max_concurrent_connections=None,
)


@dataclass(frozen=True)
class SourceConfig:
    """Everything the connector knows about one source, all of it configuration.

    :param endpoint_template: an ``https`` URL containing exactly one ``{id}`` placeholder.
        It is configuration rather than a constant because the pinned sources carry no
        documentation for either API (``CR-PC05-03``): a path baked into code here would be
        a guess wearing the costume of an implementation detail.
    :param host_allowlist: the *only* hosts this source may reach. An allow list, never a
        block list (``contracts/ops/internet-boundary.md`` §3.2: "Không phải 'chặn host xấu'
        mà là 'chỉ cho host đã biết'").
    :param contact_identity: an identity string sent to the source, if the deployment has
        one. As of ``retrieved_at`` **neither** source requires one -- see
        ``requires_contact_identity``.
    :param requires_contact_identity: whether *this source* makes identification a
        precondition of calling it. ``False`` for both sources today, from
        ``contracts/retry-policy.yaml`` ``research_connector_rate_limit.identification``.
        The flag is not dead code and must not be deleted: the contract's own ``rule_vi``
        says so -- "Quy tắc vẫn phải nằm trong code: nếu một nguồn đổi chính sách, nó là thứ
        chặn ta, và ``SG-IDENT`` KHÔNG được xoá chỉ vì hôm nay nó không kích hoạt." A source
        that starts requiring identification is configured with ``True`` and is then not
        called until the identity exists.
    """

    source_type: SourceType
    endpoint_template: str | None = None
    host_allowlist: frozenset[str] = frozenset()
    rate_limit: SourceRateLimit = field(default_factory=SourceRateLimit)
    contact_identity_param: str | None = None
    contact_identity: str | None = None
    requires_contact_identity: bool = False

    def missing_req_a6_facts(self) -> tuple[str, ...]:
        """The REQ-A6 half: rate values, and an identity a source *requires* but lacks.

        This is the exact condition card §10 ``SG-A6`` names. Since
        ``contracts/retry-policy.yaml`` 0.8.0 it is empty for both shipped sources, so
        ``SG-A6`` no longer fires -- which is a change in the *facts*, not in the rule.
        """
        missing = list(self.rate_limit.missing_facts(self.source_type))
        if self.requires_contact_identity and not self.contact_identity:
            missing.append(f"{self.source_type.removesuffix('_api')}_contact_identity")
        if self.requires_contact_identity and not self.contact_identity_param:
            missing.append(f"{self.source_type.removesuffix('_api')}_contact_identity_param")
        return tuple(missing)

    def missing_deployment_config(self) -> tuple[str, ...]:
        """The deployment half: where the API actually lives.

        Kept apart from :meth:`missing_req_a6_facts` because the two are unresolved for
        different reasons and are closed by different people. The four rate facts were an
        external document, now read. The endpoint and host are a **deployment** decision:
        ``contracts/retry-policy.yaml`` cites the two *documentation* pages, not API base
        URLs, and no contract in this repository states either service's API host. Writing
        one here would be exactly the invention card §10 ``SG-DOC`` forbids, so the
        connector still refuses a source whose endpoint it has not been given.
        """
        missing: list[str] = []
        prefix = self.source_type.removesuffix("_api")
        if not self.endpoint_template:
            missing.append(f"{prefix}_endpoint_template")
        if not self.host_allowlist:
            missing.append(f"{prefix}_host_allowlist")
        return tuple(missing)

    def missing_facts(self) -> tuple[str, ...]:
        """Everything still unresolved, REQ-A6 facts first.

        The result is the reason string in ``research.get_connector_health`` and the reason
        :class:`ConnectorNotConfigured` is raised. Empty tuple ⇒ the source may be called.
        """
        return self.missing_req_a6_facts() + self.missing_deployment_config()

    def effective_interval_ms(self, floor_ms: int) -> int:
        """The spacing actually used: the **stricter** of the floor and the documented rate.

        ``max``, never ``min``. arXiv's documented rate and the self-imposed floor are both
        3000 ms, so they coincide; OpenAlex's is 10 ms, and the floor stays in force at 3000.
        The contract's ``rationale_vi`` is explicit that this is deliberate: "Ta KHÔNG nới nó
        lên 100 req/s ... không có nhu cầu, còn rủi ro chạm ``429`` và ngân sách ngày thì có
        thật." Learning a source's real limit is a reason to be no faster than it, never a
        licence to speed up to it.
        """
        documented = self.rate_limit.interval_ms
        return floor_ms if documented is None else max(floor_ms, documented)

    @property
    def configured(self) -> bool:
        return not self.missing_facts()

    def require_configured(self) -> None:
        missing = self.missing_facts()
        if missing:
            raise ConnectorNotConfigured(self.source_type, missing)

    def build_url(self, identifier: str) -> str:
        """Substitute ``{id}`` (percent-encoded) and, if configured, the contact identity.

        The identifier is quoted with an empty ``safe`` set: a normalised DOI may contain
        ``/`` and every other character class, and letting any of it pass through unencoded
        is how a "lookup" becomes a path traversal into a different endpoint.
        """
        if not self.endpoint_template:  # pragma: no cover - require_configured runs first
            raise ConnectorNotConfigured(self.source_type, self.missing_facts())
        url = self.endpoint_template.replace("{id}", quote(identifier, safe=""))
        if self.contact_identity_param and self.contact_identity:
            parts = urlsplit(url)
            joiner = "&" if parts.query else ""
            query = (
                f"{parts.query}{joiner}"
                f"{quote(self.contact_identity_param, safe='')}="
                f"{quote(self.contact_identity, safe='')}"
            )
            url = urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))
        return url


#: The shipped arXiv config: the documented rate facts, no endpoint.
#:
#: Every REQ-A6 fact is filled from ``contracts/retry-policy.yaml`` 0.8.0, so ``SG-A6`` no
#: longer fires. ``endpoint_template`` and ``host_allowlist`` stay empty because no contract
#: in this repository states arXiv's API host -- see :meth:`SourceConfig.missing_deployment_config`.
#: A deployment supplies those two; it does not supply, and should not override, the rate.
DEFAULT_ARXIV: Final[SourceConfig] = SourceConfig(
    source_type="arxiv_api",
    rate_limit=CONTRACT_ARXIV_RATE_LIMIT,
    requires_contact_identity=False,
)

#: The shipped OpenAlex config. ``requires_contact_identity`` is ``False`` because the
#: contract's ``identification`` block records that the current documentation mandates no
#: identification: the ``mailto``/polite-pool convention REQ-D34 assumed is gone, replaced by
#: an **optional** ``api_key``. If the Owner chooses to configure a key it is a secret and
#: travels through ``contracts/ops/secrets.md``, carried here as ``contact_identity`` --
#: which is why the mechanism stays even though nothing requires it today.
DEFAULT_OPENALEX: Final[SourceConfig] = SourceConfig(
    source_type="openalex_api",
    rate_limit=CONTRACT_OPENALEX_RATE_LIMIT,
    requires_contact_identity=False,
)

#: Kept as names for the state "nothing was read from any document". Nothing constructs them
#: by default any more; tests use them to prove the refusal path is still reachable, and a
#: future source added without documentation starts here.
UNCONFIGURED_ARXIV: Final[SourceConfig] = SourceConfig(source_type="arxiv_api")
UNCONFIGURED_OPENALEX: Final[SourceConfig] = SourceConfig(
    source_type="openalex_api", requires_contact_identity=True
)


@dataclass(frozen=True)
class ConnectorSettings:
    """The connector's whole configuration surface.

    Since ``contracts/retry-policy.yaml`` 0.8.0 the defaults carry the **documented** rate
    for each source, so the connector is no longer inert out of the box on REQ-A6 grounds.
    What a deployment still has to supply is where each API lives: the contract cites the two
    *documentation* pages, not API base URLs, and this module will not invent one (``SG-DOC``).
    So the shipped state is "knows how fast it may go, does not yet know where to go" -- and
    it says exactly that through ``research.get_connector_health``, which reports the two
    kinds of gap under separate keys rather than blurring them into one "not configured".
    """

    arxiv: SourceConfig = DEFAULT_ARXIV
    openalex: SourceConfig = DEFAULT_OPENALEX
    min_interval_ms: int = DEFAULT_MIN_INTERVAL_MS
    max_redirects: int = DEFAULT_MAX_REDIRECTS
    connect_timeout_s: float = DEFAULT_CONNECT_TIMEOUT_S
    total_timeout_s: float = DEFAULT_TOTAL_TIMEOUT_S
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES
    attempts: int = DEFAULT_ATTEMPTS
    backoff_s: tuple[int, ...] = DEFAULT_BACKOFF_S

    def source(self, source_type: SourceType) -> SourceConfig:
        return self.arxiv if source_type == "arxiv_api" else self.openalex


# --------------------------------------------------------------------------------------
# The network boundary (contracts/ops/internet-boundary.md §3.2)
# --------------------------------------------------------------------------------------

#: Address ranges no outbound call from source data may ever reach. Checked against the
#: RESOLVED ADDRESS, never against the name: a public name can point at 127.0.0.1.
_EXPLICIT_BLOCKED_NETWORKS: Final[tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]] = (
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)

#: The cloud metadata address, called out separately in internet-boundary.md §3.2 because it
#: is the single most valuable SSRF target and sits inside link-local.
METADATA_ADDRESS: Final[str] = "169.254.169.254"

ALLOWED_SCHEMES: Final[frozenset[str]] = frozenset({"https"})

#: A resolver takes a host and returns the addresses it resolves to, as strings.
Resolver = Callable[[str], tuple[str, ...]]


def system_resolver(host: str) -> tuple[str, ...]:
    """Resolve with the OS resolver. Replaced in tests so no test touches DNS."""
    infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    # `sockaddr[0]` is the address for both AF_INET and AF_INET6; `dict.fromkeys` keeps the
    # resolver's order while removing the duplicates a dual-stack answer contains.
    return tuple(dict.fromkeys(str(info[4][0]) for info in infos))


def address_is_blocked(address: str) -> bool:
    """True when ``address`` is in a range source data may never reach.

    Uses :mod:`ipaddress`'s own classifications (loopback/private/link-local/multicast/
    reserved/unspecified) plus the four ranges internet-boundary.md names explicitly. Using
    the library's classification rather than a hand-written list is deliberate: a
    hand-written list is the thing that is always missing one range.
    """
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return True  # not an address at all -> refuse; never "assume it is fine"
    if ip.is_loopback or ip.is_private or ip.is_link_local:
        return True
    if ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True
    if str(ip) == METADATA_ADDRESS:
        return True
    return any(ip in network for network in _EXPLICIT_BLOCKED_NETWORKS)


@dataclass(frozen=True)
class UrlDecision:
    """The verdict on one URL, with **every** rule it broke -- not just the first.

    Fixture ``acceptance/fixtures/recovery/g-ssrf-redirect-private.json`` states that its
    third hop breaks two rules independently ("Bước 3 cũng vi phạm scheme allowlist (http)
    -- hai quy tắc độc lập cùng chặn"). Reporting only the first match would make that
    fixture unfalsifiable.
    """

    url: str
    host: str
    violations: tuple[str, ...]
    resolved_addresses: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        return not self.violations


def inspect_url(url: str, *, host_allowlist: Iterable[str], resolver: Resolver) -> UrlDecision:
    """Apply every rule of internet-boundary.md §3.2 to one URL, before any socket opens."""
    violations: list[str] = []
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme not in ALLOWED_SCHEMES:
        violations.append("scheme_not_allowed")

    host = (parts.hostname or "").lower().rstrip(".")
    allowlist = {entry.lower().rstrip(".") for entry in host_allowlist}
    if not host:
        violations.append("host_missing")
    elif host not in allowlist:
        violations.append("host_not_in_allowlist")
    if parts.username or parts.password:
        # Credentials in a URL are how a redirect smuggles authentication somewhere new;
        # internet-boundary.md §3.2 says no credential is ever sent to a source host.
        violations.append("userinfo_present")

    resolved: tuple[str, ...] = ()
    if host:
        try:
            resolved = resolver(host)
        except OSError:
            violations.append("dns_resolution_failed")
        else:
            if not resolved:
                violations.append("dns_resolution_failed")
            elif any(address_is_blocked(address) for address in resolved):
                # ANY resolved address being blocked refuses the whole name. Picking a
                # "good" address out of a mixed answer is precisely the DNS-rebinding
                # window internet-boundary.md §3.2 closes.
                violations.append("resolved_address_blocked")
    return UrlDecision(
        url=url, host=host, violations=tuple(violations), resolved_addresses=resolved
    )


@dataclass
class NetworkJournal:
    """What the boundary actually did, so the oracle can count instead of read a log.

    Card §8 asks for two counts: hosts outside the allowlist (must be 0) and connections to
    loopback or private ranges (must be 0). Both are answered from these lists.
    """

    inspected: list[UrlDecision] = field(default_factory=list)
    dispatched_hosts: list[str] = field(default_factory=list)
    dispatched_addresses: list[str] = field(default_factory=list)

    def refused(self) -> list[UrlDecision]:
        return [decision for decision in self.inspected if not decision.allowed]

    def dispatched_to_blocked_address(self) -> list[str]:
        return [a for a in self.dispatched_addresses if address_is_blocked(a)]

    def dispatched_outside(self, allowlist: Iterable[str]) -> list[str]:
        allowed = {entry.lower().rstrip(".") for entry in allowlist}
        return [host for host in self.dispatched_hosts if host not in allowed]


@dataclass(frozen=True)
class GuardedResponse:
    """A response that survived every boundary rule."""

    status_code: int
    body: bytes
    headers: Mapping[str, str]
    final_url: str
    retry_after_ms: int | None


class BoundaryRefusal(Exception):
    """The boundary refused a URL. Carries the rule names, never the URL's contents."""

    def __init__(self, decision: UrlDecision, *, hop: int) -> None:
        super().__init__(f"hop {hop}: {', '.join(decision.violations)}")
        self.decision = decision
        self.hop = hop


class ResponseTooLarge(Exception):
    """The decompressed body passed ``max_response_bytes`` and the read was aborted."""


class GuardedSession:
    """An HTTP client that cannot leave the allowlist.

    Redirects are followed **manually** (``follow_redirects=False``) because the whole rule
    set has to be re-applied at each hop; letting the library follow them would check the
    first URL and connect to the last. Bytes are counted as they stream so a decompression
    bomb is cut off rather than measured after the fact.
    """

    def __init__(
        self,
        *,
        transport: httpx.BaseTransport,
        settings: ConnectorSettings,
        host_allowlist: Iterable[str],
        resolver: Resolver = system_resolver,
        journal: NetworkJournal | None = None,
    ) -> None:
        self._settings = settings
        self._host_allowlist = frozenset(entry.lower().rstrip(".") for entry in host_allowlist)
        self._resolver = resolver
        self.journal = journal if journal is not None else NetworkJournal()
        self._client = httpx.Client(
            transport=transport,
            follow_redirects=False,
            timeout=httpx.Timeout(settings.total_timeout_s, connect=settings.connect_timeout_s),
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GuardedSession:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def get(self, url: str, *, headers: Mapping[str, str] | None = None) -> GuardedResponse:
        """GET ``url``, re-checking the boundary at every redirect hop."""
        current = url
        for hop in range(self._settings.max_redirects + 1):
            decision = inspect_url(
                current, host_allowlist=self._host_allowlist, resolver=self._resolver
            )
            self.journal.inspected.append(decision)
            if not decision.allowed:
                raise BoundaryRefusal(decision, hop=hop)

            self.journal.dispatched_hosts.append(decision.host)
            self.journal.dispatched_addresses.extend(decision.resolved_addresses)
            response = self._client.send(
                self._client.build_request("GET", current, headers=dict(headers or {})),
                stream=True,
            )
            try:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        raise BoundaryRefusal(
                            replace(decision, violations=("redirect_without_location",)), hop=hop
                        )
                    current = str(httpx.URL(current).join(location))
                    continue
                body = self._read_capped(response)
            finally:
                response.close()
            return GuardedResponse(
                status_code=response.status_code,
                body=body,
                headers=dict(response.headers),
                final_url=current,
                retry_after_ms=_retry_after_ms(response.headers.get("retry-after")),
            )
        raise BoundaryRefusal(
            UrlDecision(
                url=current,
                host=(urlsplit(current).hostname or "").lower(),
                violations=("too_many_redirects",),
                resolved_addresses=(),
            ),
            hop=self._settings.max_redirects + 1,
        )

    def _read_capped(self, response: httpx.Response) -> bytes:
        limit = self._settings.max_response_bytes
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > limit:
                raise ResponseTooLarge(f"response exceeded {limit} bytes")
            chunks.append(chunk)
        return b"".join(chunks)


def _retry_after_ms(value: str | None) -> int | None:
    """``Retry-After`` in milliseconds, or ``None``.

    Only the delta-seconds form is honoured. An HTTP-date form is answered with the
    configured floor by the caller rather than parsed here: mis-parsing a date into ``0``
    would turn "wait" into "hammer", and that is the one failure mode worth being crude to
    avoid.
    """
    if value is None:
        return None
    try:
        seconds = int(value.strip())
    except ValueError:
        return None
    return max(seconds, 0) * 1000


# --------------------------------------------------------------------------------------
# Rate gate
# --------------------------------------------------------------------------------------


class RateGate:
    """The per-source pacing floor. **Per source**, not per call.

    Card §6: "Cửa nhịp gọi là **theo nguồn**, không theo lời gọi, nên song song không được
    lách sàn." Two concurrent lookups of the same id therefore cannot halve the interval.

    ``Retry-After`` from the source always wins over anything configured
    (``retry-policy.yaml`` ``research_connector_rate_limit.rationale_vi``): :meth:`penalise`
    pushes the next-allowed instant out and no configured number pulls it back.
    """

    def __init__(
        self,
        *,
        min_interval_ms: int,
        interval_ms_by_source: Mapping[str, int] | None = None,
        max_concurrent_by_source: Mapping[str, int | None] | None = None,
        monotonic: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._min_interval_s = min_interval_ms / 1000.0
        self._interval_s = {
            source: ms / 1000.0 for source, ms in (interval_ms_by_source or {}).items()
        }
        self._max_concurrent = dict(max_concurrent_by_source or {})
        self._monotonic = monotonic
        self._sleeper = sleeper
        self._next_allowed: dict[str, float] = {}
        self._in_flight: dict[str, int] = {}
        self.waits_s: list[float] = []
        #: The highest simultaneous in-flight count seen per source. A test asserts it never
        #: passed arXiv's documented ceiling of one; a counter is checkable where a comment
        #: saying "we only make one call at a time" is not.
        self.peak_in_flight: dict[str, int] = {}

    def interval_s(self, source_type: SourceType) -> float:
        return self._interval_s.get(source_type, self._min_interval_s)

    def acquire(self, source_type: SourceType) -> None:
        now = self._monotonic()
        earliest = self._next_allowed.get(source_type, 0.0)
        if now < earliest:
            wait = earliest - now
            self.waits_s.append(wait)
            self._sleeper(wait)
            now = max(self._monotonic(), earliest)
        self._next_allowed[source_type] = now + self.interval_s(source_type)

    def penalise(self, source_type: SourceType, retry_after_ms: int) -> None:
        """Honour a source's own ``Retry-After``; never shorten an existing penalty."""
        target = self._monotonic() + retry_after_ms / 1000.0
        self._next_allowed[source_type] = max(self._next_allowed.get(source_type, 0.0), target)

    @contextmanager
    def connection(self, source_type: SourceType) -> Iterator[None]:
        """Hold one of ``source_type``'s permitted concurrent connections for the block.

        arXiv's terms of use bound parallelism as well as rate -- "limit requests to a single
        connection at a time" -- and that is a second promise, not a restatement of the
        first: one request every three seconds while holding four sockets open still breaks
        it. ``max_concurrent_connections`` is ``None`` for a source whose documentation sets
        no such bound (OpenAlex), in which case this is only bookkeeping.

        Exceeding the bound raises rather than queueing. A queue would hide the breach behind
        a delay; the connector is single-threaded per source by construction, so reaching
        this is a defect in the caller and must be visible as one.
        """
        limit = self._max_concurrent.get(source_type)
        current = self._in_flight.get(source_type, 0)
        if limit is not None and current >= limit:
            raise ConcurrencyLimitExceeded(source_type, limit)
        self._in_flight[source_type] = current + 1
        self.peak_in_flight[source_type] = max(self.peak_in_flight.get(source_type, 0), current + 1)
        try:
            yield
        finally:
            self._in_flight[source_type] = self._in_flight[source_type] - 1


# --------------------------------------------------------------------------------------
# Requests, results and provenance
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class NormalizedIdentifier:
    """The only input ``research.fetch_work_metadata`` accepts (CN-4, ``DC-RC-02``).

    A raw string, a URL from a post, or anything a model produced is **not** one of these.
    :func:`normalized_identifier` is the only constructor that admits outside data, and it
    re-runs the contract's own normalisation and demands an exact match, so "already
    normalised" is verified rather than promised.
    """

    scheme: IdScheme
    value: str
    version: str | None = None

    @property
    def source_type(self) -> SourceType:
        return "arxiv_api" if self.scheme is IdScheme.ARXIV else "openalex_api"

    @property
    def alias_key(self) -> str:
        return f"{self.scheme.value}:{self.value}"


def normalized_identifier(
    scheme: IdScheme, value: str, *, version: str | None = None
) -> NormalizedIdentifier:
    """Build a :class:`NormalizedIdentifier`, or raise ``VALIDATION_ERROR``.

    Two refusals, both required by the contract rather than defensive habit:

    * a value that does not normalise to **itself** is not normalised, so accepting it would
      make the connector the place where an un-normalised string becomes a network call
      (CN-4, I03, ``DC-RC-02``);
    * a scheme outside ``{doi, arxiv}`` is refused because those are the only two canonical
      schemes (``identity.md`` §2.3) -- and because ``landing_url`` as a lookup key is
      literally "fetch this URL somebody wrote in a post", the exact edge ``NC-07`` forbids.
    """
    if scheme not in {IdScheme.DOI, IdScheme.ARXIV}:
        raise ResearchError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.RESEARCH_FETCH_WORK_METADATA.value,
                "field_path": "/identifier/scheme",
                "violation_kind": "scheme_not_canonical",
            },
        )
    if scheme is IdScheme.DOI:
        canonical = normalize_doi(value)
        ok = canonical is not REJECT and canonical == value
    else:
        parsed = normalize_arxiv(value)
        ok = isinstance(parsed, ArxivId) and parsed.base == value and parsed.version is None
    if not ok:
        raise ResearchError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.RESEARCH_FETCH_WORK_METADATA.value,
                "field_path": "/identifier/value",
                "violation_kind": "not_normalized",
            },
        )
    if version is not None and scheme is IdScheme.ARXIV and not _VALID_VERSION(version):
        raise ResearchError(
            ErrorCode.VALIDATION_ERROR,
            details_safe={
                "operation_id": OperationId.RESEARCH_FETCH_WORK_METADATA.value,
                "field_path": "/identifier/version",
                "violation_kind": "bad_version_label",
            },
        )
    return NormalizedIdentifier(scheme=scheme, value=value, version=version)


def _VALID_VERSION(label: str) -> bool:
    """``entities.yaml`` ``work_version.version_label``: ``^v[1-9][0-9]{0,2}$`` for arXiv."""
    return (
        len(label) >= 2
        and label[0] == "v"
        and label[1] in "123456789"
        and label[1:].isdigit()
        and len(label) <= 4
    )


@dataclass(frozen=True)
class Provenance:
    """Exactly the shape ``identity_alias.evidence_ref`` expects (``identity.md`` §7).

    ``response_hash`` is the join back to a
    :class:`~server.app.research.repository.SourceFetchLogRow`, which is what makes an
    alias's evidence re-checkable rather than merely asserted.
    """

    api_endpoint: str
    retrieved_at: str
    response_hash: str
    source_fetch_log_id: str
    evidence_source: str

    def as_evidence_ref(self) -> dict[str, Any]:
        return {
            "api_endpoint": self.api_endpoint,
            "retrieved_at": self.retrieved_at,
            "response_hash": self.response_hash,
        }


@dataclass(frozen=True)
class WorkMetadata:
    """What one source said about one work. Every field may be ``None``.

    ``None`` means "the source did not say", and it is never upgraded to a value from
    somewhere else. In particular ``canonical_doi`` stays ``None`` when the source did not
    return a DOI: deriving one from a title would be the guess REQ-D33 and I03 forbid.
    """

    source_type: SourceType
    canonical_doi: str | None = None
    canonical_arxiv_base: str | None = None
    version_label: str | None = None
    title: str | None = None
    abstract_text: str | None = None
    paper_url: str | None = None
    code_url: str | None = None
    announced_at: str | None = None
    provenance: Provenance | None = None


@dataclass(frozen=True)
class MetadataResult:
    """The outcome of one ``research.fetch_work_metadata`` call.

    ``evidence_level`` is ``abstract`` only when an abstract actually arrived; otherwise
    ``post_only`` (REQ-D21, REQ-AC11, CN-5). Card §7 forbids raising it above the level the
    data supports.
    """

    metadata: WorkMetadata
    evidence_level: Literal["abstract", "post_only"]
    fetch_log_ids: tuple[str, ...]


# --------------------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------------------

HealthState = Literal["ok", "degraded", "unavailable"]


@dataclass(frozen=True)
class BudgetObservation:
    """What a source last said about the caller's remaining budget.

    OpenAlex has two limits stacked on top of each other: an instantaneous rate (100 req/s)
    and a **daily budget stated in money, not in calls**. The contract is explicit that the
    daily one is not a configuration constant -- "hạn mức ngày là thứ chỉ QUAN SÁT ĐƯỢC LÚC
    CHẠY" -- and names the ``X-RateLimit-*`` headers as the source of truth. So the connector
    reads what the source reports instead of holding a number it would have had to invent.

    Every field is ``None`` when the source sent no such header, which is the normal case for
    arXiv. ``None`` here means "not reported", never "unlimited".
    """

    limit: int | None = None
    remaining: int | None = None
    credits_used: str | None = None
    reset_seconds: int | None = None
    observed_at: str | None = None

    @property
    def reported(self) -> bool:
        return any(
            value is not None
            for value in (self.limit, self.remaining, self.credits_used, self.reset_seconds)
        )

    @property
    def exhausted(self) -> bool:
        """``True`` only when the source itself reported nothing left.

        Deliberately not "remaining is falsy": ``None`` is unknown and must not read as
        empty (I13 -- an undetermined state is never converted into a definite one).
        """
        return self.remaining is not None and self.remaining <= 0


def _header_int(headers: Mapping[str, str], name: str) -> int | None:
    raw = headers.get(name)
    if raw is None:
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def read_budget_headers(headers: Mapping[str, str], *, at: str) -> BudgetObservation:
    """Read the ``X-RateLimit-*`` family named by ``A6-OPENALEX-BUDGET``.

    Header names are lowercased by httpx, so the lookup is lowercase. ``credits_used`` stays
    a string: the contract describes the daily budget in money, and coercing a currency
    amount into an integer would be the kind of quiet lossy reading this whole block exists
    to avoid.
    """
    return BudgetObservation(
        limit=_header_int(headers, "x-ratelimit-limit"),
        remaining=_header_int(headers, "x-ratelimit-remaining"),
        credits_used=headers.get("x-ratelimit-credits-used"),
        reset_seconds=_header_int(headers, "x-ratelimit-reset"),
        observed_at=at,
    )


@dataclass
class ObservationWindow:
    """The last few outcomes per source, held in **process memory**.

    Health is read from memory rather than from ``source_fetch_log`` on purpose: it has to
    keep answering when the database cannot be read or written
    (``contracts/ops/deployment.md`` §5, SRC-PLAN §8.4). The table remains the durable
    provenance record; this is the live signal.
    """

    size: int = 20
    outcomes: dict[str, deque[tuple[str, str]]] = field(default_factory=dict)

    #: Last budget report per source. Not a deque: only the most recent one is meaningful.
    budgets: dict[str, BudgetObservation] = field(default_factory=dict)

    def record(self, source_type: SourceType, outcome: str, at: str) -> None:
        window = self.outcomes.setdefault(source_type, deque(maxlen=self.size))
        window.append((outcome, at))

    def record_budget(self, source_type: SourceType, budget: BudgetObservation) -> None:
        """Keep a budget report only when the source actually sent one.

        A response without the headers must not erase what the previous one said; "the
        source stopped telling us" is not "the budget reset".
        """
        if budget.reported:
            self.budgets[source_type] = budget

    def budget(self, source_type: SourceType) -> BudgetObservation | None:
        return self.budgets.get(source_type)

    def recent(self, source_type: SourceType) -> list[tuple[str, str]]:
        return list(self.outcomes.get(source_type, ()))


# --------------------------------------------------------------------------------------
# Context
# --------------------------------------------------------------------------------------


@dataclass
class ResearchContext:
    """Everything the two operations need, injected rather than constructed.

    ``transport`` is an :class:`httpx.BaseTransport`. In tests it is an
    :class:`httpx.MockTransport` replaying recorded responses; in a deployment it is
    ``httpx.HTTPTransport``. Nothing else in this module knows the difference, which is what
    keeps "no live call" a property of the wiring instead of a promise in a comment.
    """

    owner_id: str
    settings: ConnectorSettings
    transport: httpx.BaseTransport
    repository: SourceFetchLogRepository | None = None
    resolver: Resolver = system_resolver
    clock: Callable[[], datetime] = lambda: datetime.now(tz=UTC)
    monotonic: Callable[[], float] = time.monotonic
    sleeper: Callable[[float], None] = time.sleep
    observations: ObservationWindow = field(default_factory=ObservationWindow)
    journal: NetworkJournal = field(default_factory=NetworkJournal)
    _gate: RateGate | None = None

    def gate(self) -> RateGate:
        """The pacing gate, built once from the documented rates plus the self-imposed floor."""
        if self._gate is None:
            floor = self.settings.min_interval_ms
            self._gate = RateGate(
                min_interval_ms=floor,
                interval_ms_by_source={
                    source.source_type: source.effective_interval_ms(floor)
                    for source in (self.settings.arxiv, self.settings.openalex)
                },
                max_concurrent_by_source={
                    source.source_type: source.rate_limit.max_concurrent_connections
                    for source in (self.settings.arxiv, self.settings.openalex)
                },
                monotonic=self.monotonic,
                sleeper=self.sleeper,
            )
        return self._gate

    def now(self) -> str:
        moment = self.clock().astimezone(UTC)
        return moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"


def redact_endpoint(url: str) -> str:
    """``source_fetch_log.endpoint`` -- "URL đã gọi, đã che tham số nhạy cảm".

    Scheme, host and path are kept because they are the evidence; every query value is
    replaced. The contact identity OpenAlex requires travels in the query string, and it is
    the one secret this module holds (``capabilities.yaml`` ``ACT-research-connector``), so
    the query is redacted wholesale rather than by a list of key names that would have to
    stay in step with the configuration.
    """
    parts = urlsplit(url)
    if not parts.query:
        return urlunsplit((parts.scheme, parts.hostname or "", parts.path, "", ""))
    keys = sorted({pair.split("=", 1)[0] for pair in parts.query.split("&") if pair})
    redacted = "&".join(f"{key}=<redacted>" for key in keys)
    return urlunsplit((parts.scheme, parts.hostname or "", parts.path, redacted, ""))


def _hash_body(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _log(
    ctx: ResearchContext,
    *,
    source_type: SourceType,
    endpoint: str,
    outcome: str,
    response_hash: str | None,
    work_id: str | None,
    at: str,
) -> str:
    """Write one ``source_fetch_log`` row and record the outcome for health. Returns its id."""
    row_id = new_ulid()
    ctx.observations.record(source_type, outcome, at)
    if ctx.repository is not None:
        ctx.repository.insert(
            SourceFetchLogRow(
                id=row_id,
                owner_id=ctx.owner_id,
                source_type=source_type,
                endpoint=endpoint,
                requested_at=at,
                outcome=outcome,
                response_hash=response_hash,
                work_id=work_id,
            )
        )
    return row_id


def _unavailable(
    identifier: NormalizedIdentifier, *, attempt: int, retry_after_ms: int | None = None
) -> ResearchError:
    """The one error an item-level failure may become.

    ``target_key`` carries the alias key rather than a work id: at this point in the flow no
    work necessarily exists, and inventing one would be a claim about identity the connector
    is not allowed to make (``DC-RC-03``).
    """
    return ResearchError(
        ErrorCode.SOURCE_METADATA_UNAVAILABLE,
        details_safe={
            "target_key": identifier.alias_key,
            "connector_name": CONNECTOR_NAME,
            "attempt_number": attempt,
            "retry_after_ms": retry_after_ms,
        },
        retry_after_ms=retry_after_ms,
    )


# --------------------------------------------------------------------------------------
# research.fetch_work_metadata
# --------------------------------------------------------------------------------------


def fetch_work_metadata(
    ctx: ResearchContext,
    *,
    identifier: NormalizedIdentifier,
    work_id: str | None = None,
) -> MetadataResult:
    """``research.fetch_work_metadata`` -- ``contracts/ports.yaml``, ``mutation: false``.

    Reads one normalised identifier from one allowlisted source and returns what the source
    said, with provenance. Writes exactly one ``source_fetch_log`` row per outbound call --
    including the failed ones, because a call that leaves no trace is a call whose pacing
    cannot be audited (card §6).

    :raises ConnectorNotConfigured: never -- it is translated below. The refusal reaches the
        caller as ``SOURCE_METADATA_UNAVAILABLE`` with zero requests made, so an unconfigured
        deployment degrades to post-only rather than failing the run (CN-5, T-RUN-03).
    :raises ResearchError: ``VALIDATION_ERROR`` for a bad identifier, ``RATE_LIMITED`` when
        the source says so, ``SOURCE_METADATA_UNAVAILABLE`` for every other failure.
    """
    # Imported inside the function: the client modules type-import this one, and a module
    # cycle at import time would make the order of two imports load-bearing.
    from server.app.research import client_arxiv, client_openalex

    source_type = identifier.source_type
    config = ctx.settings.source(source_type)

    try:
        config.require_configured()
    except ConnectorNotConfigured:
        # SG-A6 / SG-IDENT. No socket is opened, no source_fetch_log row is written (there
        # was no call to log), and the item degrades to post-only.
        raise _unavailable(identifier, attempt=0) from None

    url = config.build_url(identifier.value)
    endpoint = redact_endpoint(url)
    log_ids: list[str] = []
    last_error: ResearchError | None = None

    with GuardedSession(
        transport=ctx.transport,
        settings=ctx.settings,
        host_allowlist=config.host_allowlist,
        resolver=ctx.resolver,
        journal=ctx.journal,
    ) as session:
        for attempt in range(1, max(ctx.settings.attempts, 1) + 1):
            ctx.gate().acquire(source_type)
            at = ctx.now()
            try:
                # The connection guard spans exactly the outbound call, so arXiv's "a single
                # connection at a time" is enforced by the same object that enforces its
                # rate -- and `peak_in_flight` gives a test a number to assert on.
                #
                # No identification header is added here. Neither source's documentation
                # requires one (retry-policy 0.8.0 `identification`), and adding an
                # identifying string on this module's own initiative would be a new outbound
                # value no contract asked for. An identity the Owner *does* configure travels
                # as `contact_identity` through `SourceConfig.build_url`, not from here.
                with ctx.gate().connection(source_type):
                    response = session.get(url, headers={"Accept": "*/*"})
            except BoundaryRefusal:
                # No request left the process, but the attempt is still recorded: a refusal
                # is exactly the kind of event an operator must be able to count.
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="error",
                        response_hash=None,
                        work_id=work_id,
                        at=at,
                    )
                )
                raise _unavailable(identifier, attempt=attempt) from None
            except (httpx.TimeoutException, ResponseTooLarge):
                # RP-01: a transport timeout is an UNKNOWN outcome, not "the source has no
                # data". Recording it as `error` would assert something nobody observed.
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="timeout_unknown",
                        response_hash=None,
                        work_id=work_id,
                        at=at,
                    )
                )
                last_error = _unavailable(identifier, attempt=attempt)
                continue
            except httpx.HTTPError:
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="error",
                        response_hash=None,
                        work_id=work_id,
                        at=at,
                    )
                )
                last_error = _unavailable(identifier, attempt=attempt)
                continue

            body_hash = _hash_body(response.body)
            # Read before branching on the status: a 429 is exactly the response whose
            # budget headers matter most, and it must not be the one path that drops them.
            ctx.observations.record_budget(
                source_type, read_budget_headers(response.headers, at=at)
            )

            if response.status_code == 429:
                retry_after = response.retry_after_ms
                if retry_after is not None:
                    ctx.gate().penalise(source_type, retry_after)
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="rate_limited",
                        response_hash=body_hash,
                        work_id=work_id,
                        at=at,
                    )
                )
                raise ResearchError(
                    ErrorCode.RATE_LIMITED,
                    details_safe={
                        "source_kind": source_type,
                        "retry_after_ms": retry_after,
                        "attempt_number": attempt,
                        "window_seconds": config.rate_limit.window_seconds,
                        "rate_limited_at": at,
                    },
                    retry_after_ms=retry_after,
                )

            if response.status_code == 404:
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="not_found",
                        response_hash=body_hash,
                        work_id=work_id,
                        at=at,
                    )
                )
                raise ResearchError(
                    ErrorCode.NOT_FOUND,
                    details_safe={
                        "operation_id": OperationId.RESEARCH_FETCH_WORK_METADATA.value,
                        "resource_kind": "work_metadata",
                    },
                )

            if response.status_code >= 400:
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="error",
                        response_hash=body_hash,
                        work_id=work_id,
                        at=at,
                    )
                )
                last_error = _unavailable(identifier, attempt=attempt)
                continue

            parser = (
                client_arxiv.parse_response
                if source_type == "arxiv_api"
                else client_openalex.parse_response
            )
            try:
                parsed = parser(response.body, identifier=identifier)
            except ValueError:
                # A body we cannot read is not a body that says "no data": the source may
                # have changed shape. It degrades to post-only and never to a guess.
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="error",
                        response_hash=body_hash,
                        work_id=work_id,
                        at=at,
                    )
                )
                last_error = _unavailable(identifier, attempt=attempt)
                continue

            if parsed is None:
                log_ids.append(
                    _log(
                        ctx,
                        source_type=source_type,
                        endpoint=endpoint,
                        outcome="not_found",
                        response_hash=body_hash,
                        work_id=work_id,
                        at=at,
                    )
                )
                raise ResearchError(
                    ErrorCode.NOT_FOUND,
                    details_safe={
                        "operation_id": OperationId.RESEARCH_FETCH_WORK_METADATA.value,
                        "resource_kind": "work_metadata",
                    },
                )

            log_id = _log(
                ctx,
                source_type=source_type,
                endpoint=endpoint,
                outcome="ok",
                response_hash=body_hash,
                work_id=work_id,
                at=at,
            )
            log_ids.append(log_id)
            metadata = replace(
                parsed,
                provenance=Provenance(
                    api_endpoint=endpoint,
                    retrieved_at=at,
                    response_hash=body_hash,
                    source_fetch_log_id=log_id,
                    evidence_source=source_type,
                ),
            )
            return MetadataResult(
                metadata=metadata,
                evidence_level="abstract" if metadata.abstract_text else "post_only",
                fetch_log_ids=tuple(log_ids),
            )

    raise last_error or _unavailable(identifier, attempt=ctx.settings.attempts)


# --------------------------------------------------------------------------------------
# research.get_connector_health
# --------------------------------------------------------------------------------------

#: Outcomes that mean the source answered usefully. ``not_found`` is one of them: a source
#: that correctly says "I do not have this" is working.
_HEALTHY_OUTCOMES: Final[frozenset[str]] = frozenset({"ok", "not_found"})


def _budget_report(ctx: ResearchContext, source_type: SourceType) -> dict[str, Any] | None:
    """The source's own last word on the caller's remaining budget, or ``None``."""
    budget = ctx.observations.budget(source_type)
    if budget is None:
        return None
    return {
        "limit": budget.limit,
        "remaining": budget.remaining,
        "credits_used": budget.credits_used,
        "reset_seconds": budget.reset_seconds,
        "observed_at": budget.observed_at,
        "exhausted": budget.exhausted,
    }


def _source_health(ctx: ResearchContext, source_type: SourceType) -> dict[str, Any]:
    """One source's state, with the two kinds of gap reported under separate keys.

    ``unresolved_facts`` is the REQ-A6 half -- a rate or a required identity nobody has read
    from a document. Since ``contracts/retry-policy.yaml`` 0.8.0 it is empty for both shipped
    sources. ``missing_configuration`` is the deployment half -- the API endpoint and host,
    which no contract states and this module will not invent (``SG-DOC``).

    They are separate because they are closed by different people and mean different things.
    Collapsing them into one "not configured" was defensible while both were empty for the
    same reason; now that one is resolved and the other is not, it would hide which.
    """
    config = ctx.settings.source(source_type)
    unresolved = config.missing_req_a6_facts()
    unconfigured = config.missing_deployment_config()
    if unresolved or unconfigured:
        return {
            "state": "unavailable",
            "reason_code": ("rate_facts_unresolved" if unresolved else "endpoint_not_configured"),
            "reason_safe": (
                "Chưa có dữ kiện nhịp gọi/định danh đọc từ tài liệu chính thức (REQ-A6); "
                "connector từ chối gọi nguồn này."
                if unresolved
                else "Đã có nhịp gọi từ tài liệu, nhưng triển khai chưa cấu hình endpoint "
                "và host allowlist cho nguồn này; connector không tự đoán địa chỉ API."
            ),
            "unresolved_facts": list(unresolved),
            "missing_configuration": list(unconfigured),
            "rate_facts_retrieved_at": CONTRACT_RATE_FACTS_RETRIEVED_AT,
            "effective_interval_ms": config.effective_interval_ms(ctx.settings.min_interval_ms),
            "budget": _budget_report(ctx, source_type),
            "last_outcome": None,
            "last_requested_at": None,
        }

    base: dict[str, Any] = {
        "unresolved_facts": [],
        "missing_configuration": [],
        "rate_facts_retrieved_at": CONTRACT_RATE_FACTS_RETRIEVED_AT,
        "effective_interval_ms": config.effective_interval_ms(ctx.settings.min_interval_ms),
        "budget": _budget_report(ctx, source_type),
    }

    recent = ctx.observations.recent(source_type)
    if not recent:
        # I13: an undetermined state is never reported as a good one. `ok|degraded|
        # unavailable` is a closed enum (ports.yaml), so "not observed yet" is reported as
        # `degraded` with a reason that says exactly that -- not as `ok`.
        return {
            **base,
            "state": "degraded",
            "reason_code": "no_observation_yet",
            "reason_safe": "Chưa có lời gọi nào tới nguồn này kể từ khi tiến trình khởi động.",
            "last_outcome": None,
            "last_requested_at": None,
        }

    last_outcome, last_at = recent[-1]
    healthy = [o for o, _ in recent if o in _HEALTHY_OUTCOMES]
    budget = ctx.observations.budget(source_type)
    if budget is not None and budget.exhausted:
        # The source said the daily budget is gone. That is `unavailable` regardless of how
        # the last call went, and it is the source's own claim rather than our arithmetic.
        state: HealthState = "unavailable"
        reason_code = "daily_budget_exhausted"
    elif last_outcome in _HEALTHY_OUTCOMES:
        state = "ok"
        reason_code = "last_call_succeeded"
    elif healthy:
        state = "degraded"
        reason_code = f"last_call_{last_outcome}"
    else:
        state = "unavailable"
        reason_code = f"all_recent_calls_{last_outcome}"
    return {
        **base,
        "state": state,
        "reason_code": reason_code,
        "reason_safe": "Trạng thái suy ra từ các lời gọi gần đây; không chứa URL hay bí mật.",
        "last_outcome": last_outcome,
        "last_requested_at": last_at,
    }


def overall_state(states: Iterable[HealthState]) -> HealthState:
    """``contracts/ops/deployment.md`` §5 row ``research_sources``, applied here so
    ``MOD-health-service`` maps one value instead of re-deriving the rule."""
    collected = list(states)
    if any(state == "ok" for state in collected):
        return "ok"
    if all(state == "unavailable" for state in collected) and collected:
        return "unavailable"
    return "degraded"


def get_connector_health(ctx: ResearchContext) -> dict[str, Any]:
    """``research.get_connector_health`` -- per-source state plus a redacted reason.

    A degraded source is a **return value**, not an error (``ports.yaml``
    ``error_note_vi``, ruling ``F-A2R1-09``): the only code this operation may raise is
    ``INTERNAL``, and it takes no parameters, so ``VALIDATION_ERROR`` cannot apply either.
    """
    try:
        sources = {
            "arxiv_api": _source_health(ctx, "arxiv_api"),
            "openalex_api": _source_health(ctx, "openalex_api"),
        }
    except Exception as exc:  # pragma: no cover - defensive; only INTERNAL is permitted here
        raise ResearchError(
            ErrorCode.INTERNAL,
            details_safe={
                "correlation_id": new_ulid(),
                "operation_id": OperationId.RESEARCH_GET_CONNECTOR_HEALTH.value,
            },
        ) from exc
    return {
        "sources": sources,
        "overall": overall_state(source["state"] for source in sources.values()),
        "min_interval_ms": ctx.settings.min_interval_ms,
        "min_interval_ms_status": "PROVISIONAL_SELF_IMPOSED_FLOOR",
        # The rates are now documented facts with a retrieval date, and the date travels with
        # them: the contract's `expiry_vi` says they do not renew themselves, so an operator
        # reading this screen can see how old the reading is without opening a contract.
        "rate_facts_status": "DOCS_derived",
        "rate_facts_retrieved_at": CONTRACT_RATE_FACTS_RETRIEVED_AT,
    }
