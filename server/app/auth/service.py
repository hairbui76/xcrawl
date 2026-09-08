"""``auth.login`` / ``auth.logout`` / ``auth.get_session`` over ``ENT-owner`` and ``ENT-session``.

Contracts
---------
* ``contracts/ports.yaml`` -- the three operation ids, their ``auth_scope``, ``mutation``
  flag and declared ``error_codes``.
* ``contracts/http/openapi.yaml`` -- wire shapes ``LoginRequest`` / ``SessionInfo``,
  the security schemes, and the status codes.
* ``contracts/ops/secrets.md`` §2 -- every parameter below, each PROVISIONAL with a
  number, a unit and a reason in that file. This module restates them as named constants
  so a reviewer can diff code against contract by eye.
* ``contracts/data/entities.yaml`` -- ``ENT-owner`` (singleton, ``singleton_guard = 1``)
  and ``ENT-session`` (``token_hash``, ``issued_at``, ``expires_at``, ``revoked_at``,
  ``user_agent_redacted``).

What this module deliberately does not do
-----------------------------------------
* **No signup, no automated password reset** (REQ-D05). The single account is created by
  the operator with :func:`bootstrap_owner`, which is a CLI/console call. There is no HTTP
  path to it and there is no second row in ``owner`` -- the table's ``singleton_guard``
  makes that a database error, not a code convention.
* **No secret ever leaves here.** The session token is returned once to the caller and
  stored only as ``sha256:<hex>``; passwords are stored only as an Argon2id hash; neither
  value, nor the CSRF token, is ever put in a log line or an error envelope
  (``contracts/ops/secrets.md`` §6, invariant I11).
"""

from __future__ import annotations

import hashlib
import os
import secrets
import sqlite3
import time
from contextlib import suppress
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Protocol

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from argon2.low_level import Type
from rr_contracts.generated.errors import RETRY_CLASS, SCOPE, ErrorCode
from rr_contracts.generated.operations import OperationId
from sqlalchemy import Connection, Engine, text
from sqlalchemy.exc import SQLAlchemyError

from server.app.auth.csrf import new_csrf_token

# --------------------------------------------------------------------------------------
# Parameters. Every one of these is PROVISIONAL in contracts/ops/secrets.md §2.2 and §2.3
# and needs Owner confirmation; none of them is invented here.
# --------------------------------------------------------------------------------------

#: Argon2id, memory_cost 64 MiB expressed in KiB as argon2-cffi wants it.
ARGON2_MEMORY_COST_KIB = 64 * 1024
ARGON2_TIME_COST = 3
ARGON2_PARALLELISM = 1
ARGON2_SALT_BYTES = 16
ARGON2_HASH_BYTES = 32

#: Session token length: 256 random bits (secrets.md §2.3 "Độ dài token").
SESSION_TOKEN_BYTES = 32

#: Idle timeout 12 h, absolute timeout 30 d (secrets.md §2.3).
IDLE_TIMEOUT_MS = 12 * 60 * 60 * 1000
ABSOLUTE_TIMEOUT_MS = 30 * 24 * 60 * 60 * 1000

#: 5 failed logins inside 15 minutes lock the account for 15 minutes (secrets.md §2.3).
LOGIN_FAIL_THRESHOLD = 5
LOGIN_FAIL_WINDOW_MS = 15 * 60 * 1000
LOCKOUT_DURATION_MS = 15 * 60 * 1000

#: Engineering value, not a contract number: sliding the idle window writes a row, so it
#: is only written when it actually moves the deadline by more than this. Without it every
#: read request would become a write.
SESSION_SLIDE_MIN_STEP_MS = 60 * 1000

#: `user_agent_redacted` is "họ trình duyệt + hệ điều hành", not the full UA string
#: (secrets.md §2.3). This is the cap on what is kept.
USER_AGENT_REDACTED_MAX_CHARS = 60


#: Exceptions that mean "the write did not happen", mapped to ``STORAGE_WRITE_FAILED``.
#:
#: Same tuple, and for the same reason, as ``server/app/ingest/service.py``
#: (``WRITE_FAILURES``) and ``server/app/identity/service.py``: SQLAlchemy wraps a failure
#: raised inside ``cursor.execute`` as ``OperationalError``/``IntegrityError``, but a failure
#: raised from a connection-level event hook -- which is how ``server/app/db/faults.py``
#: reproduces a full disk -- arrives as the bare ``sqlite3`` exception and is **not** wrapped.
#: Catching only ``SQLAlchemyError`` therefore let a genuine write failure escape as an
#: unhandled 500 instead of the 503 the contract declares for this path (``CR-TC-AUTH-11``).
#: ``sqlite3.Error`` is the base of every DBAPI error the driver raises, so it closes the
#: gap without guessing at a list of subclasses.
WRITE_FAILURES: tuple[type[Exception], ...] = (SQLAlchemyError, sqlite3.Error)


# --------------------------------------------------------------------------------------
# Small contract-shaped helpers
# --------------------------------------------------------------------------------------

_CROCKFORD32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def new_ulid(now_ms: int | None = None) -> str:
    """A ULID as ``contracts/data/entities.yaml`` defines it: 26 Crockford base32 chars.

    Time-ordered, so ``ORDER BY id`` is a stable pagination order and no extra column is
    needed (the contract's stated reason for choosing ULID over UUID).
    """
    timestamp = int(time.time() * 1000) if now_ms is None else now_ms
    value = (timestamp << 80) | int.from_bytes(os.urandom(10), "big")
    out = [""] * 26
    for index in range(25, -1, -1):
        out[index] = _CROCKFORD32[value & 0x1F]
        value >>= 5
    return "".join(out)


def to_timestamp_utc_ms(moment: datetime) -> str:
    """RFC 3339 UTC with mandatory millisecond precision (AMD-B08, entities conventions)."""
    utc = moment.astimezone(UTC)
    return utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{utc.microsecond // 1000:03d}Z"


def epoch_ms(moment: datetime) -> int:
    return int(moment.astimezone(UTC).timestamp() * 1000)


def from_epoch_ms(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000, tz=UTC)


def hash_session_token(token: str) -> str:
    """``sha256:<64 hex>`` as the ``hash_sha256`` type of the entity contract requires."""
    return "sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest()


def hash_bearer_token(token: str) -> str:
    """The same reduction for the three bearer credentials.

    ``contracts/ops/secrets.md`` §3 on the collector and analysis-worker tokens: "server lưu
    ``sha256``, không lưu bản rõ". Separate name from :func:`hash_session_token` because the
    two are different credentials with different lifetimes, even though the reduction is the
    same one.
    """
    return "sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest()


def redact_user_agent(user_agent: str | None) -> str | None:
    """Keep a short, non-identifying prefix. Never the full UA string (secrets.md §2.3)."""
    if not user_agent:
        return None
    return user_agent[:USER_AGENT_REDACTED_MAX_CHARS]


# --------------------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------------------

#: `message_safe_template_vi` of contracts/errors.yaml, for the codes this card raises.
#: Hand-copied because the generator does not yet emit them (see CR-TC-AUTH-05);
#: `tests/contract/test_auth_scheme_matrix.py` asserts each string still equals the
#: contract, so a drift is a test failure rather than a silent divergence.
MESSAGE_SAFE: dict[ErrorCode, str] = {
    ErrorCode.UNAUTHORIZED: "Không có quyền thực hiện thao tác này.",
    ErrorCode.CSRF_REJECTED: "Yêu cầu không hợp lệ. Hãy tải lại trang rồi thử lại.",
    ErrorCode.FORBIDDEN_EDGE: "Đường gọi này không được phép.",
    ErrorCode.VALIDATION_ERROR: "Dữ liệu gửi lên không hợp lệ.",
    ErrorCode.RATE_LIMITED: "Nguồn đang giới hạn nhịp truy cập. Hệ thống chờ rồi thử lại.",
    ErrorCode.STORAGE_WRITE_FAILED: (
        "Hệ thống tạm thời không ghi được dữ liệu. Đã dừng nhận việc mới."
    ),
}

#: `details_safe_keys` of contracts/errors.yaml for the same codes. A key outside this set
#: must never be sent (errors.yaml §error_envelope `details_safe`).
DETAILS_SAFE_KEYS: dict[ErrorCode, frozenset[str]] = {
    ErrorCode.UNAUTHORIZED: frozenset({"operation_id", "required_auth_scope"}),
    ErrorCode.CSRF_REJECTED: frozenset({"operation_id"}),
    ErrorCode.FORBIDDEN_EDGE: frozenset({"caller_module", "callee_module", "forbidden_edge_ref"}),
    ErrorCode.VALIDATION_ERROR: frozenset(
        {"operation_id", "field_path", "violation_kind", "limit_name", "limit_value"}
    ),
    ErrorCode.RATE_LIMITED: frozenset(
        {"source_kind", "retry_after_ms", "attempt_number", "window_seconds", "rate_limited_at"}
    ),
    ErrorCode.STORAGE_WRITE_FAILED: frozenset(
        {"storage_health", "failed_operation_id", "observed_at", "retry_after_ms"}
    ),
}

#: HTTP status per code, taken from the responses declared in contracts/http/openapi.yaml.
HTTP_STATUS: dict[ErrorCode, int] = {
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.CSRF_REJECTED: 403,
    ErrorCode.FORBIDDEN_EDGE: 403,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.RATE_LIMITED: 429,
    ErrorCode.STORAGE_WRITE_FAILED: 503,
}


class AuthError(Exception):
    """A refusal carrying exactly one registered error code.

    The code is an :class:`ErrorCode` member, never a string literal: an error code that is
    not in ``contracts/errors.yaml`` does not exist (Phase 1 dispatch rule 7).
    """

    def __init__(
        self,
        code: ErrorCode,
        *,
        details_safe: dict[str, object] | None = None,
        retry_after_ms: int | None = None,
    ) -> None:
        super().__init__(code.value)
        self.code = code
        self.http_status = HTTP_STATUS[code]
        self.details_safe = dict(details_safe or {})
        self.retry_after_ms = retry_after_ms
        unknown = set(self.details_safe) - DETAILS_SAFE_KEYS[code]
        if unknown:
            # errors.yaml: "Khóa lạ ⇒ producer tự từ chối, không gửi ra."
            raise ValueError(f"{code.value} may not carry details keys {sorted(unknown)}")

    def envelope(self, correlation_id: str) -> dict[str, object]:
        """The wire envelope of ``contracts/errors.yaml`` §error_envelope.

        ``correlation_id`` is generated in process memory, so the envelope is complete even
        when the database cannot be written (EPR-01 / SRC-PLAN §8.4).
        """
        return {
            "code": self.code.value,
            "scope": SCOPE[self.code],
            "retry_class": RETRY_CLASS[self.code],
            "message_safe": MESSAGE_SAFE[self.code],
            "correlation_id": correlation_id,
            "details_safe": self.details_safe or None,
            "retry_after_ms": self.retry_after_ms,
        }


# --------------------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SessionRecord:
    """One row of ``ENT-session``. The raw token is never part of it."""

    id: str
    owner_id: str
    issued_at_ms: int
    expires_at_ms: int
    revoked_at_ms: int | None
    user_agent_redacted: str | None

    def is_live(self, now_ms: int) -> bool:
        if self.revoked_at_ms is not None:
            return False
        if now_ms >= self.expires_at_ms:
            return False
        return now_ms < self.issued_at_ms + ABSOLUTE_TIMEOUT_MS


@dataclass(frozen=True)
class LoginResult:
    """What ``auth.login`` hands back once, and only once."""

    session: SessionRecord
    session_token: str
    csrf_token: str


class StorageHealthPort(Protocol):
    """The ``storage.get_health`` port this card *consumes* (card §4).

    ``TC-storage-write-blocked-readiness`` owns the implementation. Coding against the port
    keeps the dependency one-directional; until that card lands, ``AuthService`` is
    constructed without a provider and a write failure surfaces from the database itself as
    ``STORAGE_WRITE_FAILED`` rather than from a health pre-check.
    """

    def get_health(self) -> str:  # pragma: no cover - protocol declaration
        ...


# --------------------------------------------------------------------------------------
# Login lockout
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LockoutState:
    """The two ``ENT-owner`` columns that make the login lockout durable.

    ``contracts/ops/secrets.md`` §2.3 fixes ``login_fail_threshold`` 5 and
    ``lockout_duration`` 15 minutes. Amendment ``AMD-ENT-owner-01`` (raised as
    ``CR-TC-AUTH-03``, accepted after ``F-A3R1-06``) put ``failed_login_count`` and
    ``locked_until`` on the owner row, so the counter is written in the **same transaction**
    as the attempt that moved it and survives a process restart. It used to be a deque in
    process memory, which a restart cleared -- a rate limit an attacker could wait out.

    One honest deviation, ``CR-TC-AUTH-07``: the contract phrases the threshold as "5 lần /
    15 phút" but the amended columns carry no window start, so this implementation counts
    **consecutive** failures (the wording ``failed_login_count`` itself uses: "số lần đăng
    nhập sai liên tiếp") and clears them on success or when a lock expires. That is a
    superset of the contract's rule -- it never locks later than the contract requires, and
    it can lock for failures spread wider than 15 minutes. Narrowing it needs a window-start
    column, which is change control, not a code decision.
    """

    failed_login_count: int
    locked_until_ms: int | None

    def locked(self, now_ms: int) -> bool:
        return self.locked_until_ms is not None and now_ms < self.locked_until_ms

    def after_failure(self, now_ms: int) -> LockoutState:
        """One more consecutive failure; the threshold arms the lock and resets the count."""
        count = self.failed_login_count + 1
        if count >= LOGIN_FAIL_THRESHOLD:
            return LockoutState(failed_login_count=0, locked_until_ms=now_ms + LOCKOUT_DURATION_MS)
        return LockoutState(failed_login_count=count, locked_until_ms=None)


#: A successful login, and an expired lock, both return the owner row to this.
UNLOCKED = LockoutState(failed_login_count=0, locked_until_ms=None)


# --------------------------------------------------------------------------------------
# The service
# --------------------------------------------------------------------------------------


class AuthService:
    """Session lifecycle for the single owner account.

    Transactions. The card declares no business transaction -- the checkpoint is the
    middleware, before the domain is reached. The two writes here are each a single
    ``BEGIN…COMMIT`` opened by :func:`server.app.db.session_scope`:

    * :meth:`login` -- **commit point: the INSERT into ``session``**. The token is only
      returned to the caller after that commit, so a client never holds a cookie for a row
      that does not exist.
    * :meth:`logout` -- **commit point: the UPDATE that sets ``revoked_at``**. Revocation is
      a write, not a delete (``ENT-session``: "thu hồi là ghi, không xóa").
    """

    def __init__(self, engine: Engine, *, storage_health: StorageHealthPort | None = None) -> None:
        self._engine = engine
        self._storage_health = storage_health
        self._hasher = PasswordHasher(
            time_cost=ARGON2_TIME_COST,
            memory_cost=ARGON2_MEMORY_COST_KIB,
            parallelism=ARGON2_PARALLELISM,
            hash_len=ARGON2_HASH_BYTES,
            salt_len=ARGON2_SALT_BYTES,
            type=Type.ID,
        )

    # -- operator-only bootstrap ---------------------------------------------------------

    def bootstrap_owner(
        self,
        *,
        display_name: str,
        password: str,
        timezone_iana: str = "Asia/Ho_Chi_Minh",
        now: datetime | None = None,
    ) -> str:
        """Create (or re-credential) the single owner row. **Operator/CLI only.**

        There is no HTTP route to this method and there must never be one: REQ-D05 forbids a
        signup page, and ``contracts/ops/secrets.md`` §2.1 makes access recovery "một thao
        tác vận hành tại chỗ". ``owner.singleton_guard`` makes a second row a database
        error.

        :returns: the owner id.
        """
        moment = now or datetime.now(UTC)
        password_hash = self._hasher.hash(password)
        with self._engine.begin() as connection:
            existing = connection.execute(text("SELECT id FROM owner LIMIT 1")).first()
            if existing is not None:
                owner_id = str(existing[0])
                connection.execute(
                    text(
                        "UPDATE owner SET password_hash = :h, password_updated_at = :t, "
                        "failed_login_count = 0, locked_until = NULL WHERE id = :id"
                    ),
                    {"h": password_hash, "t": to_timestamp_utc_ms(moment), "id": owner_id},
                )
                # "Đổi mật khẩu thu hồi MỌI session" (secrets.md §2.3).
                connection.execute(
                    text(
                        "UPDATE session SET revoked_at = :t "
                        "WHERE owner_id = :id AND revoked_at IS NULL"
                    ),
                    {"t": to_timestamp_utc_ms(moment), "id": owner_id},
                )
                return owner_id
            owner_id = new_ulid(epoch_ms(moment))
            connection.execute(
                text(
                    "INSERT INTO owner (id, singleton_guard, display_name, timezone_iana, "
                    "created_at, password_hash, password_updated_at, failed_login_count, "
                    "locked_until) VALUES (:id, 1, :name, :tz, :t, :h, :t, 0, NULL)"
                ),
                {
                    "id": owner_id,
                    "name": display_name,
                    "tz": timezone_iana,
                    "t": to_timestamp_utc_ms(moment),
                    "h": password_hash,
                },
            )
            return owner_id

    # -- auth.login ----------------------------------------------------------------------

    def login(
        self,
        username: str,
        password: str,
        *,
        user_agent: str | None = None,
        now: datetime | None = None,
    ) -> LoginResult:
        """``auth.login``. Commit point: the end of the single transaction below.

        Every outcome writes, so every outcome commits before it is reported:

        * success -- the INSERT into ``session`` plus the reset of the lockout columns;
        * wrong password / unknown account -- the increment of ``owner.failed_login_count``,
          and the arming of ``owner.locked_until`` when it reaches the threshold;
        * locked -- nothing is written, and no attempt is counted against a lock already in
          force.

        The refusal is raised **after** the ``with`` block, never inside it: raising inside
        would roll the transaction back and discard the very failure it is meant to record,
        which is how the counter used to be lost (``F-A3R1-06``).

        The account is a singleton, so ``username`` is matched against
        ``owner.display_name``. A wrong password and an unknown account return the **same**
        ``UNAUTHORIZED``: secrets.md §2.3 requires not revealing whether the account exists.
        """
        moment = now or datetime.now(UTC)
        now_ms = epoch_ms(moment)
        self._guard_storage(OperationId.AUTH_LOGIN)

        refusal: AuthError | None = None
        result: LoginResult | None = None
        try:
            with self._engine.begin() as connection:
                row = connection.execute(
                    text(
                        "SELECT id, display_name, password_hash, failed_login_count, "
                        "locked_until FROM owner LIMIT 1"
                    )
                ).first()
                lockout = (
                    UNLOCKED
                    if row is None
                    else LockoutState(
                        failed_login_count=int(row[3]),
                        locked_until_ms=None if row[4] is None else _parse_ms(str(row[4])),
                    )
                )

                if lockout.locked(now_ms):
                    assert lockout.locked_until_ms is not None
                    remaining = lockout.locked_until_ms - now_ms
                    refusal = AuthError(
                        ErrorCode.RATE_LIMITED,
                        details_safe={
                            "source_kind": "owner_login",
                            "retry_after_ms": remaining,
                            "window_seconds": LOGIN_FAIL_WINDOW_MS // 1000,
                        },
                        retry_after_ms=remaining,
                    )
                else:
                    stored_hash = None if row is None or row[2] is None else str(row[2])
                    names_match = row is not None and str(row[1]) == username
                    verified = False
                    if row is None or not names_match or stored_hash is None:
                        # Verify against a dummy hash anyway: an early return here would make
                        # "unknown account" measurably faster than "wrong password".
                        self._verify_dummy(password)
                    else:
                        try:
                            self._hasher.verify(stored_hash, password)
                            verified = True
                        except (VerifyMismatchError, InvalidHashError):
                            verified = False

                    if not verified:
                        if row is not None:
                            self._write_lockout(
                                connection, str(row[0]), lockout.after_failure(now_ms)
                            )
                        refusal = AuthError(
                            ErrorCode.UNAUTHORIZED,
                            details_safe={
                                "operation_id": OperationId.AUTH_LOGIN.value,
                                "required_auth_scope": "public_login",
                            },
                        )
                    else:
                        assert row is not None and stored_hash is not None
                        owner_id = str(row[0])
                        if self._hasher.check_needs_rehash(stored_hash):
                            # secrets.md §2.2: changing the parameters rehashes on next
                            # successful login.
                            connection.execute(
                                text("UPDATE owner SET password_hash = :h WHERE id = :id"),
                                {"h": self._hasher.hash(password), "id": owner_id},
                            )
                        self._write_lockout(connection, owner_id, UNLOCKED)
                        result = self._insert_session(
                            connection, owner_id, moment, now_ms, user_agent
                        )
        except WRITE_FAILURES as exc:
            raise self._storage_write_failed(OperationId.AUTH_LOGIN, moment) from exc

        if refusal is not None:
            raise refusal
        assert result is not None
        return result

    def _write_lockout(self, connection: Connection, owner_id: str, state: LockoutState) -> None:
        """Persist the two lockout columns. Always inside the caller's transaction."""
        connection.execute(
            text(
                "UPDATE owner SET failed_login_count = :count, locked_until = :until "
                "WHERE id = :id"
            ),
            {
                "count": state.failed_login_count,
                "until": (
                    None
                    if state.locked_until_ms is None
                    else to_timestamp_utc_ms(from_epoch_ms(state.locked_until_ms))
                ),
                "id": owner_id,
            },
        )

    def _insert_session(
        self,
        connection: Connection,
        owner_id: str,
        moment: datetime,
        now_ms: int,
        user_agent: str | None,
    ) -> LoginResult:
        session_token = secrets.token_urlsafe(SESSION_TOKEN_BYTES)
        # Pure double-submit: the CSRF value is never stored server-side. The check is
        # "header equals cookie", and both come from the browser, so a column for it would
        # add a secret to the database that buys nothing (secrets.md §2.3; openapi
        # `ownerCsrfToken`).
        csrf_token = new_csrf_token()
        expires_at_ms = min(now_ms + IDLE_TIMEOUT_MS, now_ms + ABSOLUTE_TIMEOUT_MS)
        record = SessionRecord(
            id=new_ulid(now_ms),
            owner_id=owner_id,
            issued_at_ms=now_ms,
            expires_at_ms=expires_at_ms,
            revoked_at_ms=None,
            user_agent_redacted=redact_user_agent(user_agent),
        )
        connection.execute(
            text(
                "INSERT INTO session (id, owner_id, token_hash, issued_at, "
                "expires_at, revoked_at, user_agent_redacted) "
                "VALUES (:id, :owner, :hash, :issued, :expires, NULL, :ua)"
            ),
            {
                "id": record.id,
                "owner": owner_id,
                "hash": hash_session_token(session_token),
                "issued": to_timestamp_utc_ms(moment),
                "expires": to_timestamp_utc_ms(from_epoch_ms(expires_at_ms)),
                "ua": record.user_agent_redacted,
            },
        )
        return LoginResult(session=record, session_token=session_token, csrf_token=csrf_token)

    # -- auth.logout ---------------------------------------------------------------------

    def logout(self, session_token: str | None, *, now: datetime | None = None) -> None:
        """``auth.logout``. Commit point: the UPDATE that sets ``revoked_at``.

        Idempotent by contract (``ports.yaml``: "Gọi lại trên session đã hủy trả kết quả
        thành công idempotent"), so an already-revoked row is not an error.
        """
        moment = now or datetime.now(UTC)
        if not session_token:
            raise AuthError(
                ErrorCode.UNAUTHORIZED,
                details_safe={
                    "operation_id": OperationId.AUTH_LOGOUT.value,
                    "required_auth_scope": "owner_session",
                },
            )
        try:
            with self._engine.begin() as connection:
                connection.execute(
                    text(
                        "UPDATE session SET revoked_at = :t "
                        "WHERE token_hash = :hash AND revoked_at IS NULL"
                    ),
                    {"t": to_timestamp_utc_ms(moment), "hash": hash_session_token(session_token)},
                )
        except WRITE_FAILURES as exc:
            raise self._storage_write_failed(OperationId.AUTH_LOGOUT, moment) from exc

    # -- auth.get_session ----------------------------------------------------------------

    def get_session(
        self, session_token: str | None, *, now: datetime | None = None
    ) -> SessionRecord:
        """``auth.get_session``: resolve a token to a live session or refuse.

        Both deadlines are checked on **every** request against the stored row -- the cookie
        is never trusted for its own expiry (``contracts/ops/secrets.md`` §2.3, "Thu hồi").
        """
        return self.authenticate(session_token, now=now)

    def authenticate(
        self, session_token: str | None, *, now: datetime | None = None
    ) -> SessionRecord:
        """The check every owner-session route runs. Raises ``UNAUTHORIZED`` if not live."""
        moment = now or datetime.now(UTC)
        now_ms = epoch_ms(moment)
        if not session_token:
            raise self._unauthorized_session()
        with self._engine.begin() as connection:
            row = connection.execute(
                text(
                    "SELECT id, owner_id, issued_at, expires_at, revoked_at, "
                    "user_agent_redacted FROM session WHERE token_hash = :hash"
                ),
                {"hash": hash_session_token(session_token)},
            ).first()
            if row is None:
                raise self._unauthorized_session()
            record = SessionRecord(
                id=str(row[0]),
                owner_id=str(row[1]),
                issued_at_ms=_parse_ms(str(row[2])),
                expires_at_ms=_parse_ms(str(row[3])),
                revoked_at_ms=None if row[4] is None else _parse_ms(str(row[4])),
                user_agent_redacted=None if row[5] is None else str(row[5]),
            )
            if not record.is_live(now_ms):
                raise self._unauthorized_session()

        slid = min(now_ms + IDLE_TIMEOUT_MS, record.issued_at_ms + ABSOLUTE_TIMEOUT_MS)
        if slid - record.expires_at_ms >= SESSION_SLIDE_MIN_STEP_MS and self._slide(
            record.id, slid
        ):
            record = replace(record, expires_at_ms=slid)
        return record

    def _slide(self, session_id: str, expires_at_ms: int) -> bool:
        """Extend the idle window. Returns whether the new deadline was committed.

        A separate transaction from the read above, and a **best-effort** one: extending the
        idle window is bookkeeping, not the answer to "is this session live". If the write
        fails the session is still valid -- the deadline simply does not move, and the next
        request tries again.

        Swallowing the failure is what the wire contract requires, not a convenience:
        ``contracts/http/openapi.yaml`` declares ``200 / 401 / 403 / 500`` for
        ``GET /v1/auth/session`` and **no 503**, so a failed bookkeeping write must not turn
        a valid session into ``STORAGE_WRITE_FAILED``. It must not turn into a 500 either,
        which is what it did before this transaction was split out.
        """
        try:
            with self._engine.begin() as connection:
                connection.execute(
                    text("UPDATE session SET expires_at = :t WHERE id = :id"),
                    {"t": to_timestamp_utc_ms(from_epoch_ms(expires_at_ms)), "id": session_id},
                )
        except WRITE_FAILURES:
            return False
        return True

    # -- internals -----------------------------------------------------------------------

    def _verify_dummy(self, password: str) -> None:
        with suppress(VerifyMismatchError, InvalidHashError):
            self._hasher.verify(_DUMMY_HASH, password)

    def _guard_storage(self, operation: OperationId) -> None:
        if self._storage_health is None:
            return
        health = self._storage_health.get_health()
        if health in {"write_blocked", "maintenance"}:
            raise AuthError(
                ErrorCode.STORAGE_WRITE_FAILED,
                details_safe={
                    "storage_health": health,
                    "failed_operation_id": operation.value,
                },
            )

    def _storage_write_failed(self, operation: OperationId, moment: datetime) -> AuthError:
        return AuthError(
            ErrorCode.STORAGE_WRITE_FAILED,
            details_safe={
                "failed_operation_id": operation.value,
                "observed_at": to_timestamp_utc_ms(moment),
            },
        )

    @staticmethod
    def _unauthorized_session() -> AuthError:
        return AuthError(
            ErrorCode.UNAUTHORIZED,
            details_safe={"required_auth_scope": "owner_session"},
        )


def _parse_ms(value: str) -> int:
    return epoch_ms(datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=UTC))


#: A well-formed Argon2id hash of a value nobody knows, used only to keep the timing of
#: "no such account" close to the timing of "wrong password".
_DUMMY_HASH = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST_KIB,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_BYTES,
    salt_len=ARGON2_SALT_BYTES,
    type=Type.ID,
).hash(secrets.token_urlsafe(32))


__all__ = [
    "ARGON2_MEMORY_COST_KIB",
    "ARGON2_PARALLELISM",
    "ARGON2_TIME_COST",
    "ABSOLUTE_TIMEOUT_MS",
    "AuthError",
    "AuthService",
    "DETAILS_SAFE_KEYS",
    "HTTP_STATUS",
    "IDLE_TIMEOUT_MS",
    "LOCKOUT_DURATION_MS",
    "LOGIN_FAIL_THRESHOLD",
    "LOGIN_FAIL_WINDOW_MS",
    "LoginResult",
    "LockoutState",
    "MESSAGE_SAFE",
    "SessionRecord",
    "StorageHealthPort",
    "WRITE_FAILURES",
    "hash_bearer_token",
    "hash_session_token",
    "new_ulid",
    "to_timestamp_utc_ms",
]
