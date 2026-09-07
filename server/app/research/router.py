"""The **internal** entry point for ``research.*``. It publishes no HTTP route.

``contracts/ports.yaml`` types both operations ``transport: internal`` with
``auth_scope: internal_only``, and ``contracts/capabilities.yaml`` §internal_only spells out
what that does and does not mean::

    Port trong tiến trình, không tiếp cận được từ mạng. Không phải "không cần kiểm soát":
    edge nội bộ vẫn theo allowed_edges của contracts/modules.yaml và bị chặn bằng import rule.

So this module is the place where the *edge* is checked, not the place where a URL is
registered. Adding a path for either operation would create an ingress
``contracts/http/openapi.yaml`` does not describe, which is the default-deny violation
``SG-EDGE`` names. ``install_research`` therefore attaches a port object to ``app.state``
and registers nothing -- and ``server/app/main.py`` is left untouched by this card.

Three refusals live here, each with the code ruling ``R5-01`` assigns it (card §5; choosing
the wrong code is a FAIL, not a detail):

======================================================  ==================
a caller module that is not in ``allowed_edges``        ``FORBIDDEN_EDGE``
a network target outside the configured allowlist       ``CAPABILITY_DENIED``
any attempt to drive a browser / reach the X path       ``CAPABILITY_DENIED``
======================================================  ==================
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol

from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

from server.app.auth.middleware import require_edge
from server.app.research.repository import SourceFetchLogRepository
from server.app.research.service import (
    MODULE_ID,
    ConnectorSettings,
    MetadataResult,
    NormalizedIdentifier,
    ResearchContext,
    ResearchError,
    fetch_work_metadata,
    get_connector_health,
)

#: ``contracts/modules.yaml`` ``forbidden_edges``: the connector may not reach the X web
#: surface (``FE-20``) or a Chrome profile (``FE-21``). Both are listed in
#: ``acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`` rows 20 and 21 with
#: ``expected_error_code: CAPABILITY_DENIED``.
FORBIDDEN_EDGE_X_WEB: str = "FE-20"
FORBIDDEN_EDGE_CHROME_PROFILE: str = "FE-21"

#: Import prefixes that would give this module a browser. Checked by the boundary test as a
#: static rule (``enforcement: [ENF-import-rule, ENF-process-capability]``): the honest
#: enforcement of "does not drive Chrome" is that the code to do so is not reachable.
BROWSER_IMPORT_PREFIXES: frozenset[str] = frozenset(
    {"playwright", "selenium", "pyppeteer", "undetected_chromedriver", "collector"}
)


def _capability_denied(kind: str, *, edge_ref: str | None) -> ResearchError:
    return ResearchError(
        ErrorCode.CAPABILITY_DENIED,
        details_safe={
            "module_id": MODULE_ID,
            "denied_capability_kind": kind,
            "forbidden_edge_ref": edge_ref,
        },
    )


def assert_target_allowed(host: str, *, allowlist: Iterable[str]) -> None:
    """Refuse a network target that is not on the configured allowlist.

    This is the *capability* half of the boundary, and it is separate from
    :func:`~server.app.research.service.inspect_url` on purpose. ``inspect_url`` decides
    whether a request may be sent and answers by degrading the item to post-only; this one
    answers a direct question -- "may this module talk to that host at all" -- and the sweep
    fixture pins its code as ``CAPABILITY_DENIED``.
    """
    normalised = host.lower().rstrip(".")
    allowed = {entry.lower().rstrip(".") for entry in allowlist}
    if normalised in allowed:
        return
    edge_ref = FORBIDDEN_EDGE_X_WEB if _is_x_host(normalised) else None
    raise _capability_denied("network_egress", edge_ref=edge_ref)


def _is_x_host(host: str) -> bool:
    """Recognise the X surface only so ``FE-20`` can be *named* in the refusal.

    The refusal itself does not depend on this: anything off the allowlist is denied. This
    exists so the audit trail says which registered forbidden edge was attempted, which is
    what the sweep fixture asserts on.
    """
    return host == "x.com" or host.endswith(".x.com") or host in {"twitter.com", "t.co"}


def assert_no_browser_capability(module_globals: dict[str, Any]) -> None:
    """Refuse if a research module has pulled a browser driver into scope (``FE-21``)."""
    for value in module_globals.values():
        name = getattr(value, "__name__", "")
        if isinstance(name, str) and name.split(".", 1)[0] in BROWSER_IMPORT_PREFIXES:
            raise _capability_denied("browser_control", edge_ref=FORBIDDEN_EDGE_CHROME_PROFILE)


class ResearchPort(Protocol):
    """The in-process shape ``MOD-ingest-service`` and ``MOD-health-service`` call."""

    def fetch_work_metadata(
        self, *, caller_module: str, identifier: NormalizedIdentifier, work_id: str | None = None
    ) -> MetadataResult: ...

    def get_connector_health(self, *, caller_module: str) -> dict[str, Any]: ...


class ResearchConnector:
    """The port implementation. Checks the edge, then delegates to the service."""

    def __init__(self, context: ResearchContext) -> None:
        self._context = context

    @property
    def context(self) -> ResearchContext:
        return self._context

    def fetch_work_metadata(
        self, *, caller_module: str, identifier: NormalizedIdentifier, work_id: str | None = None
    ) -> MetadataResult:
        """``research.fetch_work_metadata``; ``MOD-ingest-service`` is its only caller."""
        require_edge(OperationId.RESEARCH_FETCH_WORK_METADATA, caller_module)
        return fetch_work_metadata(self._context, identifier=identifier, work_id=work_id)

    def get_connector_health(self, *, caller_module: str) -> dict[str, Any]:
        """``research.get_connector_health``; ``MOD-health-service`` is its only caller."""
        require_edge(OperationId.RESEARCH_GET_CONNECTOR_HEALTH, caller_module)
        return get_connector_health(self._context)


def build_connector(
    *,
    owner_id: str,
    settings: ConnectorSettings,
    transport: Any,
    repository: SourceFetchLogRepository | None = None,
    **context_kwargs: Any,
) -> ResearchConnector:
    """Assemble a connector from explicit parts.

    ``transport`` is required and has no default. A default would mean this factory decides
    whether the process can reach the internet, and card §10 ``SG-LIVE`` puts that decision
    with the deployment: tests pass an :class:`httpx.MockTransport`, a deployment passes a
    real one, and nothing in between can drift.
    """
    context = ResearchContext(
        owner_id=owner_id,
        settings=settings,
        transport=transport,
        repository=repository,
        **context_kwargs,
    )
    return ResearchConnector(context)


def install_research(app: Any, connector: ResearchConnector | None = None) -> None:
    """Attach the port to ``app.state.research_connector``. Registers **no** route.

    ``connector`` may be ``None``: an app built with no research configuration then reports
    ``app.state.research_connector is None``, and a caller that needs it fails loudly rather
    than silently receiving a connector that would call a public API at an undocumented
    rate.
    """
    app.state.research_connector = connector
