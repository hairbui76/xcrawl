"""The security schemes of ``contracts/http/openapi.yaml``, applied. Default deny.

This module is the surface other cards import. A router does not decide who may call it;
it declares which scheme guards it and this module answers.

The scheme names are the ones in the contract, verbatim
--------------------------------------------------------
``rr_contracts.generated.constants.SECURITY_SCHEMES`` is generated from
``components.securitySchemes`` of the OpenAPI document, and the six constants below are
checked against it at import time. A renamed scheme therefore fails to import rather than
silently guarding nothing.

The AND that matters
--------------------
For an owner **mutation** the contract puts ``ownerSessionCookie`` and ``ownerCsrfToken``
in **one** security requirement, which in OpenAPI means *and*. Cookie alone is not enough.
For an owner **read** the cookie stands alone: CSRF protects state changes, not reads. That
distinction is data here (:data:`SCHEME_REQUIREMENTS`), not prose, and
``tests/contract/test_auth_scheme_matrix.py`` asserts it against all 54 HTTP operations.

The four refusal codes, and which is which (ruling R5-01, card §5)
-----------------------------------------------------------------
============================================  ==========================
Situation                                     Code
============================================  ==========================
HTTP call from a principal class the           ``UNAUTHORIZED`` (401)
operation does not admit -- a collector token
calling ``save.create`` (NC-01/NC-02)
In-process call across an edge absent from     ``FORBIDDEN_EDGE`` (403)
``contracts/modules.yaml.allowed_edges``
Missing process/network/filesystem/tool        ``CAPABILITY_DENIED``
capability
Owner mutation without a valid CSRF            ``CSRF_REJECTED`` (403),
double-submit                                  session **not** revoked
============================================  ==========================

Only the first and the fourth rows are this module's job: they are decided at the HTTP
boundary. The second is an in-process concern (import rules and the callers of internal
ports); the third belongs to the process sandbox. :func:`classify_denial` names which of
the four applies so a caller cannot quietly pick the wrong one.
"""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from enum import Enum

from fastapi import Request
from rr_contracts.generated.constants import SECURITY_SCHEMES
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OWNER_MODULE as OWNER_MODULE_OF
from rr_contracts.generated.operations import OperationId

from server.app.auth.csrf import CSRF_COOKIE_NAME, CSRF_HEADER_NAME, csrf_matches
from server.app.auth.service import AuthError, AuthService, SessionRecord, hash_bearer_token

# --------------------------------------------------------------------------------------
# Scheme names -- verbatim from contracts/http/openapi.yaml components.securitySchemes
# --------------------------------------------------------------------------------------

OWNER_SESSION_COOKIE_SCHEME = "ownerSessionCookie"
OWNER_CSRF_TOKEN_SCHEME = "ownerCsrfToken"
COLLECTOR_TOKEN_SCHEME = "collectorToken"
ANALYSIS_WORKER_TOKEN_SCHEME = "analysisWorkerToken"
TELEGRAM_INGRESS_SECRET_SCHEME = "telegramIngressSecret"
BACKUP_OPERATOR_TOKEN_SCHEME = "backupOperatorToken"

#: Cookie carrying the session token (openapi: `apiKey` in cookie, name `rr_session`).
SESSION_COOKIE_NAME = "rr_session"

#: The webhook secret header of `telegramIngressSecret`.
TELEGRAM_SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"

if tuple(SECURITY_SCHEMES) != (
    OWNER_SESSION_COOKIE_SCHEME,
    OWNER_CSRF_TOKEN_SCHEME,
    COLLECTOR_TOKEN_SCHEME,
    ANALYSIS_WORKER_TOKEN_SCHEME,
    TELEGRAM_INGRESS_SECRET_SCHEME,
    BACKUP_OPERATOR_TOKEN_SCHEME,
):  # pragma: no cover - import-time contract guard
    raise RuntimeError(
        "security scheme names drifted from contracts/http/openapi.yaml: " f"{SECURITY_SCHEMES!r}"
    )


class AuthScope(str, Enum):
    """The ten ``auth_scope`` values of ``contracts/ports.yaml``."""

    PUBLIC_LOGIN = "public_login"
    PUBLIC_MINIMAL = "public_minimal"
    OWNER_SESSION = "owner_session"
    OWNER_SESSION_OR_LINKED_CHAT = "owner_session_or_linked_chat"
    COLLECTOR_TOKEN = "collector_token"
    ANALYSIS_WORKER_TOKEN = "analysis_worker_token"
    COLLECTOR_TOKEN_OR_ANALYSIS_WORKER_TOKEN = "collector_token_or_analysis_worker_token"
    BACKUP_OPERATOR = "backup_operator"
    TELEGRAM_INGRESS_SECRET = "telegram_ingress_secret"
    INTERNAL_ONLY = "internal_only"


class PrincipalKind(str, Enum):
    """Who is calling, as far as the HTTP boundary can tell."""

    ANONYMOUS = "anonymous"
    OWNER_SESSION = "owner_session"
    COLLECTOR = "collector"
    ANALYSIS_WORKER = "analysis_worker"
    BACKUP_OPERATOR = "backup_operator"
    TELEGRAM_INGRESS = "telegram_ingress"


#: `auth_scope` x `mutation` -> the alternative security requirements of the contract.
#: Each inner frozenset is one requirement object, i.e. an **and** of scheme names; the
#: tuple of them is the **or**. Read straight off contracts/http/openapi.yaml -- the
#: contract test regenerates this mapping from the document and asserts equality.
SCHEME_REQUIREMENTS: dict[tuple[AuthScope, bool], tuple[frozenset[str], ...]] = {
    # `security: []` in the document: an empty *list of requirements*, i.e. nothing to
    # satisfy. Not the same as one empty requirement, which is why this is `()`.
    (AuthScope.PUBLIC_LOGIN, True): (),
    (AuthScope.PUBLIC_MINIMAL, False): (),
    (AuthScope.OWNER_SESSION, False): (frozenset({OWNER_SESSION_COOKIE_SCHEME}),),
    (AuthScope.OWNER_SESSION, True): (
        frozenset({OWNER_SESSION_COOKIE_SCHEME, OWNER_CSRF_TOKEN_SCHEME}),
    ),
    (AuthScope.OWNER_SESSION_OR_LINKED_CHAT, False): (
        frozenset({OWNER_SESSION_COOKIE_SCHEME}),
        frozenset({TELEGRAM_INGRESS_SECRET_SCHEME}),
    ),
    (AuthScope.OWNER_SESSION_OR_LINKED_CHAT, True): (
        frozenset({OWNER_SESSION_COOKIE_SCHEME, OWNER_CSRF_TOKEN_SCHEME}),
        frozenset({TELEGRAM_INGRESS_SECRET_SCHEME}),
    ),
    (AuthScope.COLLECTOR_TOKEN, False): (frozenset({COLLECTOR_TOKEN_SCHEME}),),
    (AuthScope.COLLECTOR_TOKEN, True): (frozenset({COLLECTOR_TOKEN_SCHEME}),),
    (AuthScope.ANALYSIS_WORKER_TOKEN, False): (frozenset({ANALYSIS_WORKER_TOKEN_SCHEME}),),
    (AuthScope.ANALYSIS_WORKER_TOKEN, True): (frozenset({ANALYSIS_WORKER_TOKEN_SCHEME}),),
    (AuthScope.COLLECTOR_TOKEN_OR_ANALYSIS_WORKER_TOKEN, True): (
        frozenset({COLLECTOR_TOKEN_SCHEME}),
        frozenset({ANALYSIS_WORKER_TOKEN_SCHEME}),
    ),
    (AuthScope.BACKUP_OPERATOR, True): (frozenset({BACKUP_OPERATOR_TOKEN_SCHEME}),),
    (AuthScope.TELEGRAM_INGRESS_SECRET, True): (frozenset({TELEGRAM_INGRESS_SECRET_SCHEME}),),
}

#: Which principal class can satisfy which scheme. This is the whole of "a valid token on
#: the wrong edge is refused": the token is genuine, its class is simply not in the set.
_SCHEME_PRINCIPAL: dict[str, PrincipalKind] = {
    OWNER_SESSION_COOKIE_SCHEME: PrincipalKind.OWNER_SESSION,
    COLLECTOR_TOKEN_SCHEME: PrincipalKind.COLLECTOR,
    ANALYSIS_WORKER_TOKEN_SCHEME: PrincipalKind.ANALYSIS_WORKER,
    BACKUP_OPERATOR_TOKEN_SCHEME: PrincipalKind.BACKUP_OPERATOR,
    TELEGRAM_INGRESS_SECRET_SCHEME: PrincipalKind.TELEGRAM_INGRESS,
}


@dataclass(frozen=True)
class Principal:
    """The authenticated caller. ``session`` is set only for ``OWNER_SESSION``."""

    kind: PrincipalKind
    session: SessionRecord | None = None


class TokenRegistry:
    """Maps a bearer token to the principal class it belongs to, **by hash**.

    ``contracts/ops/secrets.md`` §3 says of the collector and analysis-worker tokens:
    "server lưu ``sha256``, không lưu bản rõ". This registry therefore reduces every token
    to ``sha256:<hex>`` on the way in and keeps no plaintext, and it compares with
    :func:`hmac.compare_digest` over **every** entry rather than returning on the first
    match, so neither the stored value nor the position of the match is recoverable from
    timing (``F-A3R1-12``).

    Deliberately empty by default. The three bearer credentials are files on other machines
    and no card may put one in the repo; the operator installs them at boot. An empty
    registry means every bearer is ``UNAUTHORIZED``, which is the correct default-deny
    answer rather than a convenient one.
    """

    def __init__(self, tokens: dict[str, PrincipalKind] | None = None) -> None:
        """``tokens`` maps a *plaintext* token to its class; only hashes are retained."""
        self._by_hash: dict[str, PrincipalKind] = {
            hash_bearer_token(token): kind for token, kind in (tokens or {}).items()
        }

    @classmethod
    def from_hashes(cls, hashes: dict[str, PrincipalKind]) -> TokenRegistry:
        """Build from stored ``sha256:<hex>`` digests -- the real operator path.

        The server never needs the plaintext, so a deployment configures the digests and
        the token itself only ever exists on the machine that presents it.
        """
        registry = cls()
        registry._by_hash = dict(hashes)
        return registry

    def kind_for(self, token: str) -> PrincipalKind | None:
        digest = hash_bearer_token(token)
        found: PrincipalKind | None = None
        for stored, kind in self._by_hash.items():
            if hmac.compare_digest(stored, digest):
                found = kind
        return found


# --------------------------------------------------------------------------------------
# Default deny at the module-edge level (ruling R5-01 row 2)
# --------------------------------------------------------------------------------------
#
# `contracts/modules.yaml` declares `default_deny`: an edge that is not in `allowed_edges`
# is forbidden. Two registries express that, because the contract expresses it two ways:
#
# * per operation -- `contracts/ports.yaml.caller_modules` says who may call it. This is
#   the form that matters, because two forbidden edges (`FE-28` report -> analysis,
#   `FE-33` telegram -> job) are between module pairs that ARE allowed for *other*
#   operations. A pair-level check alone would wave those through.
# * per module pair -- for the two sweep rows that name no operation at all
#   (`FE-08`, `FE-26`, both `event_type: in_process_call`).
#
# Both tables are hand-written contract data (`CR-TC-AUTH-05`): the generator emits
# `OWNER_MODULE`, `TRANSPORT` and `MUTATION` but not `caller_modules`. Two tests in
# `tests/contract/test_auth_scheme_matrix.py` rebuild them from the contracts and assert
# equality, so a contract change breaks the build instead of drifting past it.

ALLOWED_CALLERS: dict[OperationId, frozenset[str]] = {
    OperationId.AUTH_LOGIN: frozenset({"MOD-web-ui"}),
    OperationId.AUTH_LOGOUT: frozenset({"MOD-web-ui"}),
    OperationId.AUTH_GET_SESSION: frozenset({"MOD-web-ui"}),
    OperationId.SETTINGS_GET_CONFIG: frozenset({"MOD-web-ui"}),
    OperationId.SETTINGS_UPDATE_CONFIG: frozenset({"MOD-web-ui"}),
    OperationId.SETTINGS_TEST_PROVIDER: frozenset({"MOD-web-ui"}),
    OperationId.TAG_LIST: frozenset({"MOD-web-ui"}),
    OperationId.TAG_CREATE: frozenset({"MOD-web-ui"}),
    OperationId.TAG_UPDATE: frozenset({"MOD-web-ui"}),
    OperationId.TAG_DELETE: frozenset({"MOD-web-ui"}),
    OperationId.TAG_PREVIEW_MATCHES: frozenset({"MOD-web-ui"}),
    OperationId.TAG_RESCAN_CORPUS: frozenset({"MOD-web-ui"}),
    OperationId.TAG_GET_ACTIVE_CONFIG_VERSION: frozenset({"MOD-report-service"}),
    OperationId.TAG_FREEZE_CONFIG_VERSION: frozenset({"MOD-report-service"}),
    OperationId.RUN_LIST: frozenset({"MOD-telegram-adapter", "MOD-web-ui"}),
    OperationId.RUN_GET: frozenset({"MOD-web-ui"}),
    OperationId.RUN_RUN_NOW: frozenset({"MOD-telegram-adapter", "MOD-web-ui"}),
    OperationId.RUN_RESUME: frozenset({"MOD-web-ui"}),
    OperationId.RUN_CANCEL: frozenset({"MOD-web-ui"}),
    OperationId.SCHEDULER_EVALUATE_DUE: frozenset({"MOD-scheduler"}),
    OperationId.JOB_ENQUEUE_SCHEDULED_RUN: frozenset({"MOD-scheduler"}),
    OperationId.JOB_COALESCE_OVERDUE: frozenset({"MOD-scheduler"}),
    OperationId.WORKER_REGISTER_CAPABILITIES: frozenset({"MOD-analysis-worker", "MOD-x-collector"}),
    OperationId.WORKER_CLAIM_ASSIGNMENT: frozenset({"MOD-x-collector"}),
    OperationId.WORKER_HEARTBEAT: frozenset({"MOD-x-collector"}),
    OperationId.WORKER_REPORT_STOP: frozenset({"MOD-x-collector"}),
    OperationId.WORKER_RELEASE_ASSIGNMENT: frozenset({"MOD-x-collector"}),
    OperationId.WORKER_GET_STATUS: frozenset({"MOD-web-ui"}),
    OperationId.INGEST_SUBMIT_BATCH: frozenset({"MOD-x-collector"}),
    OperationId.INGEST_COMMIT_CHECKPOINT: frozenset({"MOD-x-collector"}),
    OperationId.INGEST_GET_CHECKPOINT: frozenset({"MOD-job-service"}),
    OperationId.INGEST_GET_RECEIPT: frozenset({"MOD-x-collector"}),
    OperationId.RESEARCH_FETCH_WORK_METADATA: frozenset({"MOD-ingest-service"}),
    OperationId.RESEARCH_GET_CONNECTOR_HEALTH: frozenset({"MOD-health-service"}),
    OperationId.IDENTITY_RESOLVE_TARGET: frozenset({"MOD-ingest-service", "MOD-report-service"}),
    OperationId.IDENTITY_RECORD_ALIAS: frozenset({"MOD-ingest-service"}),
    OperationId.IDENTITY_QUARANTINE_CONFLICT: frozenset({"MOD-ingest-service"}),
    OperationId.IDENTITY_MERGE_WORKS: frozenset({"MOD-identity-service", "MOD-ingest-service"}),
    OperationId.IDENTITY_RESOLVE_CONFLICT: frozenset({"MOD-web-ui"}),
    OperationId.WORK_GET_DETAIL: frozenset({"MOD-web-ui"}),
    OperationId.ANALYSIS_ENQUEUE_TASKS: frozenset({"MOD-ingest-service", "MOD-report-service"}),
    OperationId.ANALYSIS_CLAIM_TASK: frozenset({"MOD-analysis-worker"}),
    OperationId.ANALYSIS_GET_TASK_INPUT: frozenset({"MOD-analysis-worker"}),
    OperationId.ANALYSIS_HEARTBEAT: frozenset({"MOD-analysis-worker"}),
    OperationId.ANALYSIS_SUBMIT_RESULT: frozenset({"MOD-analysis-worker"}),
    OperationId.ANALYSIS_REPORT_ATTEMPT_UNKNOWN: frozenset({"MOD-analysis-worker"}),
    OperationId.ANALYSIS_REQUEST_REANALYSIS: frozenset({"MOD-web-ui"}),
    OperationId.AI_RUN_INFERENCE_TASK: frozenset({"MOD-analysis-worker"}),
    OperationId.AI_PROBE_PROVIDER_CAPABILITY: frozenset({"MOD-analysis-worker"}),
    OperationId.SECRET_STORE_PROVIDER_KEY: frozenset({"MOD-settings-service"}),
    OperationId.SECRET_ISSUE_TASK_CREDENTIAL: frozenset({"MOD-analysis-worker"}),
    OperationId.SECRET_REVOKE_TASK_CREDENTIAL: frozenset({"MOD-analysis-service"}),
    OperationId.EMBEDDING_GENERATE_VECTORS: frozenset(
        {"MOD-ingest-service", "MOD-report-service", "MOD-tag-service"}
    ),
    OperationId.EMBEDDING_GET_ACTIVE_GENERATION: frozenset(
        {"MOD-report-service", "MOD-tag-service"}
    ),
    OperationId.EMBEDDING_START_GENERATION_REBUILD: frozenset({"MOD-settings-service"}),
    OperationId.EMBEDDING_ACTIVATE_GENERATION: frozenset({"MOD-embedding-service"}),
    OperationId.REPORT_BUILD: frozenset({"MOD-job-service"}),
    OperationId.REPORT_PUBLISH: frozenset({"MOD-report-service"}),
    OperationId.REPORT_LIST: frozenset({"MOD-web-ui"}),
    OperationId.REPORT_GET: frozenset({"MOD-web-ui"}),
    OperationId.SAVE_CREATE: frozenset({"MOD-telegram-adapter", "MOD-web-ui"}),
    OperationId.SAVE_REMOVE: frozenset({"MOD-web-ui"}),
    OperationId.DATA_DELETE_TARGET: frozenset({"MOD-web-ui"}),
    OperationId.DATA_PURGE_ALL: frozenset({"MOD-web-ui"}),
    OperationId.SAVE_LIST: frozenset({"MOD-web-ui"}),
    OperationId.SAVE_EXPORT: frozenset({"MOD-web-ui"}),
    OperationId.TELEGRAM_RECEIVE_UPDATE: frozenset({"EXT-telegram-api"}),
    OperationId.TELEGRAM_EXECUTE_COMMAND: frozenset({"MOD-telegram-adapter"}),
    OperationId.TELEGRAM_ISSUE_LINK_CODE: frozenset({"MOD-web-ui"}),
    OperationId.TELEGRAM_CONSUME_LINK_CODE: frozenset({"MOD-telegram-adapter"}),
    OperationId.TELEGRAM_UNLINK: frozenset({"MOD-web-ui"}),
    OperationId.TELEGRAM_SEND_PAYLOAD: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_CREATE_INTENT: frozenset({"MOD-job-service", "MOD-report-service"}),
    OperationId.DELIVERY_DISPATCH_NEXT: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_RECORD_RECEIPT: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_MARK_UNKNOWN: frozenset({"MOD-delivery-service"}),
    OperationId.DELIVERY_GET_STATUS: frozenset({"MOD-web-ui"}),
    OperationId.DELIVERY_DECIDE_UNKNOWN: frozenset({"MOD-web-ui"}),
    OperationId.BACKUP_CREATE_SNAPSHOT: frozenset({"MOD-backup-cli"}),
    OperationId.BACKUP_VERIFY_SNAPSHOT: frozenset({"MOD-backup-cli"}),
    OperationId.BACKUP_RESTORE_SNAPSHOT: frozenset({"MOD-backup-cli"}),
    OperationId.BACKUP_RECONCILE_AFTER_RESTORE: frozenset({"MOD-backup-cli"}),
    OperationId.HEALTH_GET_LIVENESS: frozenset(
        {"MOD-analysis-worker", "MOD-web-ui", "MOD-x-collector"}
    ),
    OperationId.HEALTH_GET_READINESS: frozenset({"MOD-web-ui"}),
    OperationId.STORAGE_GET_HEALTH: frozenset({"MOD-health-service", "MOD-job-service"}),
}

ALLOWED_MODULE_EDGES: frozenset[tuple[str, str]] = frozenset(
    {
        ("EXT-telegram-api", "MOD-telegram-adapter"),
        ("MOD-analysis-service", "MOD-secret-service"),
        ("MOD-analysis-worker", "MOD-ai-adapter"),
        ("MOD-analysis-worker", "MOD-analysis-service"),
        ("MOD-analysis-worker", "MOD-health-service"),
        ("MOD-analysis-worker", "MOD-job-service"),
        ("MOD-analysis-worker", "MOD-secret-service"),
        ("MOD-backup-cli", "MOD-backup-service"),
        ("MOD-delivery-service", "MOD-delivery-service"),
        ("MOD-delivery-service", "MOD-telegram-adapter"),
        ("MOD-embedding-service", "MOD-embedding-service"),
        ("MOD-health-service", "MOD-data-store"),
        ("MOD-health-service", "MOD-research-connector"),
        ("MOD-identity-service", "MOD-identity-service"),
        ("MOD-ingest-service", "MOD-analysis-service"),
        ("MOD-ingest-service", "MOD-embedding-service"),
        ("MOD-ingest-service", "MOD-identity-service"),
        ("MOD-ingest-service", "MOD-research-connector"),
        ("MOD-job-service", "MOD-data-store"),
        ("MOD-job-service", "MOD-delivery-service"),
        ("MOD-job-service", "MOD-ingest-service"),
        ("MOD-job-service", "MOD-report-service"),
        ("MOD-report-service", "MOD-analysis-service"),
        ("MOD-report-service", "MOD-delivery-service"),
        ("MOD-report-service", "MOD-embedding-service"),
        ("MOD-report-service", "MOD-identity-service"),
        ("MOD-report-service", "MOD-report-service"),
        ("MOD-report-service", "MOD-tag-service"),
        ("MOD-scheduler", "MOD-job-service"),
        ("MOD-scheduler", "MOD-scheduler"),
        ("MOD-settings-service", "MOD-embedding-service"),
        ("MOD-settings-service", "MOD-secret-service"),
        ("MOD-tag-service", "MOD-embedding-service"),
        ("MOD-telegram-adapter", "MOD-job-service"),
        ("MOD-telegram-adapter", "MOD-saved-service"),
        ("MOD-telegram-adapter", "MOD-telegram-adapter"),
        ("MOD-web-ui", "MOD-analysis-service"),
        ("MOD-web-ui", "MOD-auth-service"),
        ("MOD-web-ui", "MOD-data-admin-service"),
        ("MOD-web-ui", "MOD-delivery-service"),
        ("MOD-web-ui", "MOD-health-service"),
        ("MOD-web-ui", "MOD-identity-service"),
        ("MOD-web-ui", "MOD-job-service"),
        ("MOD-web-ui", "MOD-report-service"),
        ("MOD-web-ui", "MOD-saved-service"),
        ("MOD-web-ui", "MOD-settings-service"),
        ("MOD-web-ui", "MOD-tag-service"),
        ("MOD-web-ui", "MOD-telegram-adapter"),
        ("MOD-x-collector", "MOD-health-service"),
        ("MOD-x-collector", "MOD-ingest-service"),
        ("MOD-x-collector", "MOD-job-service"),
    }
)


def require_edge(
    operation: OperationId, caller_module: str, *, edge_ref: str | None = None
) -> None:
    """Raise ``FORBIDDEN_EDGE`` if ``caller_module`` may not call ``operation``.

    This is the **in-process** half of ruling R5-01 and it is a different question from
    ``require_owner_session`` and friends: those ask *who are you* at the HTTP boundary and
    answer ``UNAUTHORIZED``; this one asks *is this call path in the registry at all* and
    answers ``FORBIDDEN_EDGE``. Choosing the wrong one of the two is a FAIL by card §10
    ``SG-DENY``, so they are separate functions with separate codes.
    """
    if caller_module not in ALLOWED_CALLERS[operation]:
        raise AuthError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": OWNER_MODULE_OF[operation],
                "forbidden_edge_ref": edge_ref,
            },
        )


def require_module_edge(
    caller_module: str, callee_module: str, *, edge_ref: str | None = None
) -> None:
    """The same rule for a call that names no operation.

    Used by the two sweep rows whose ``event_type`` is ``in_process_call``: one component
    reaching into another with no port between them. There is no operation to key on, so
    the module pair itself is checked against ``allowed_edges``.
    """
    if (caller_module, callee_module) not in ALLOWED_MODULE_EDGES:
        raise AuthError(
            ErrorCode.FORBIDDEN_EDGE,
            details_safe={
                "caller_module": caller_module,
                "callee_module": callee_module,
                "forbidden_edge_ref": edge_ref,
            },
        )


# --------------------------------------------------------------------------------------
# The decision function. Everything below it is plumbing.
# --------------------------------------------------------------------------------------


def satisfied_scheme_set(
    scope: AuthScope, *, mutation: bool, principal: PrincipalKind, csrf_ok: bool
) -> frozenset[str] | None:
    """The requirement this caller satisfies, or ``None`` if none of them.

    ``csrf_ok`` is consulted only where the contract puts ``ownerCsrfToken`` in the
    requirement, so a read never fails for a missing header and a mutation never passes
    without one.
    """
    requirements = SCHEME_REQUIREMENTS.get((scope, mutation))
    if requirements is None:
        return None
    if requirements == ():
        # `security: []` -- auth.login and health.get_liveness. Open by contract.
        return frozenset()
    for requirement in requirements:
        # `ownerCsrfToken` is not a principal class; it is a proof carried *by* a class,
        # so it is checked separately from the who-are-you question.
        classes = {_SCHEME_PRINCIPAL[s] for s in requirement if s in _SCHEME_PRINCIPAL}
        if classes != {principal}:
            continue
        if OWNER_CSRF_TOKEN_SCHEME in requirement and not csrf_ok:
            continue
        return requirement
    return None


def classify_denial(
    scope: AuthScope, *, mutation: bool, principal: PrincipalKind, csrf_ok: bool
) -> ErrorCode | None:
    """``None`` when the call is admitted; otherwise the one code ruling R5-01 assigns.

    ``CSRF_REJECTED`` is returned only when the principal class *is* admitted and the sole
    failure is the double-submit -- exactly the "valid edge, unproven intent" case. Using
    ``FORBIDDEN_EDGE`` there is a FAIL by card §10 ``SG-CSRF``, so the two branches are kept
    apart here rather than at each call site.
    """
    if scope is AuthScope.INTERNAL_ONLY:
        # An internal port has no HTTP path at all (openapi
        # `x-internal-operations-not-exposed`), so **no** principal class can ever satisfy
        # it from the wire. At this boundary that is row 1 of R5-01 -- wrong principal
        # class -- and the code is `UNAUTHORIZED`, which is what the sweep fixture pins for
        # `FE-07` and `FE-13` (`analysis.enqueue_tasks`, `report.publish`, both `internal`,
        # both `enforcement: ENF-api-auth-test`).
        #
        # `FORBIDDEN_EDGE` is the answer to the *other* question -- an in-process call
        # across an edge that is not in the registry -- and that one is :func:`require_edge`.
        # Returning it here would answer an in-process question to an HTTP caller.
        return ErrorCode.UNAUTHORIZED
    if satisfied_scheme_set(scope, mutation=mutation, principal=principal, csrf_ok=csrf_ok):
        return None
    admitted_without_csrf = satisfied_scheme_set(
        scope, mutation=mutation, principal=principal, csrf_ok=True
    )
    if admitted_without_csrf is not None and OWNER_CSRF_TOKEN_SCHEME in admitted_without_csrf:
        return ErrorCode.CSRF_REJECTED
    return ErrorCode.UNAUTHORIZED


# --------------------------------------------------------------------------------------
# FastAPI dependencies. These are the names other cards depend on.
# --------------------------------------------------------------------------------------


def _auth_service(request: Request) -> AuthService | None:
    """``app.state.auth_service``, or ``None`` if the app was built without one.

    An unconfigured backend is answered with ``UNAUTHORIZED``, not with a 500. Default deny
    is the rule (``contracts/modules.yaml.default_deny``): if the server cannot establish
    who is calling, nobody is authenticated. Raising here instead would turn a wiring
    mistake into an exception on a path that other cards' routers also depend on.
    """
    service = getattr(request.app.state, "auth_service", None)
    return service if isinstance(service, AuthService) else None


def _token_registry(request: Request) -> TokenRegistry:
    registry = getattr(request.app.state, "token_registry", None)
    return registry if isinstance(registry, TokenRegistry) else TokenRegistry()


def _bearer(request: Request) -> str | None:
    header = request.headers.get("Authorization")
    if not header or not header.lower().startswith("bearer "):
        return None
    return header[len("bearer ") :].strip() or None


def _unauthorized(scope: AuthScope) -> AuthError:
    return AuthError(ErrorCode.UNAUTHORIZED, details_safe={"required_auth_scope": scope.value})


def require_owner_session(request: Request) -> Principal:
    """``ownerSessionCookie``. Sufficient on its own **only** for reads.

    A mutation must additionally depend on :func:`require_csrf`, declared after this one so
    that a request with neither credential is refused as ``UNAUTHORIZED`` and not as
    ``CSRF_REJECTED`` -- the order fixture
    ``acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`` seq3/seq4 pins.
    """
    service = _auth_service(request)
    if service is None:
        raise _unauthorized(AuthScope.OWNER_SESSION)
    session = service.authenticate(request.cookies.get(SESSION_COOKIE_NAME))
    principal = Principal(kind=PrincipalKind.OWNER_SESSION, session=session)
    request.state.principal = principal
    return principal


def require_csrf(request: Request) -> None:
    """``ownerCsrfToken``: header ``X-CSRF-Token`` must equal cookie ``rr_csrf``.

    Raises ``CSRF_REJECTED`` (403) and leaves the session untouched. It never revokes,
    never partially applies a mutation, and never logs either token value.
    """
    if not csrf_matches(
        request.headers.get(CSRF_HEADER_NAME), request.cookies.get(CSRF_COOKIE_NAME)
    ):
        raise AuthError(ErrorCode.CSRF_REJECTED, details_safe={})


def _require_bearer(request: Request, expected: PrincipalKind, scope: AuthScope) -> Principal:
    token = _bearer(request)
    if token is None:
        raise _unauthorized(scope)
    kind = _token_registry(request).kind_for(token)
    if kind is not expected:
        # Either the token is unknown, or it is a genuine token of a different class being
        # used on an edge that class does not open: NC-01 / NC-02, and the code is
        # UNAUTHORIZED in both cases (modules.yaml denied_cases, ruling on CR-PC08-04).
        raise _unauthorized(scope)
    principal = Principal(kind=kind)
    request.state.principal = principal
    return principal


def require_collector_token(request: Request) -> Principal:
    """``collectorToken``. Opens ``worker.*`` and ``ingest.*`` and nothing else."""
    return _require_bearer(request, PrincipalKind.COLLECTOR, AuthScope.COLLECTOR_TOKEN)


def require_worker_token(request: Request) -> Principal:
    """``analysisWorkerToken``. Opens ``analysis.*`` and ``secret.issue_task_credential``."""
    return _require_bearer(request, PrincipalKind.ANALYSIS_WORKER, AuthScope.ANALYSIS_WORKER_TOKEN)


def require_backup_operator_token(request: Request) -> Principal:
    """``backupOperatorToken``: the **only** scheme any ``backup.*`` route accepts.

    A browser session must not reach restore (``CR-PC08-02``); that is why this is a
    separate bearer identity and not a role on the owner session.
    """
    return _require_bearer(request, PrincipalKind.BACKUP_OPERATOR, AuthScope.BACKUP_OPERATOR)


__all__ = [
    "ALLOWED_CALLERS",
    "ALLOWED_MODULE_EDGES",
    "ANALYSIS_WORKER_TOKEN_SCHEME",
    "BACKUP_OPERATOR_TOKEN_SCHEME",
    "COLLECTOR_TOKEN_SCHEME",
    "OWNER_CSRF_TOKEN_SCHEME",
    "OWNER_SESSION_COOKIE_SCHEME",
    "SESSION_COOKIE_NAME",
    "SCHEME_REQUIREMENTS",
    "TELEGRAM_INGRESS_SECRET_SCHEME",
    "AuthScope",
    "Principal",
    "PrincipalKind",
    "TokenRegistry",
    "classify_denial",
    "require_backup_operator_token",
    "require_collector_token",
    "require_csrf",
    "require_edge",
    "require_module_edge",
    "require_owner_session",
    "require_worker_token",
    "satisfied_scheme_set",
]
