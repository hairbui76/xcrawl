"""The server-side secret store: envelope encryption, and the only code that sees a value.

``contracts/ops/secrets.md`` §4.1 in three lines:

* every secret is encrypted under its **own** data key (AEAD, 256-bit);
* the data key is encrypted under a **master key**;
* the master key comes from the container's environment or a ``0400`` file mount, and
  **never** from the database -- "nếu nằm cùng DB thì mã hóa vô nghĩa khi mất file DB".

Why there is no master key in this repository
---------------------------------------------
``SG-MASTER-KEY`` of the card is explicit: no default key is generated, none is committed,
and none is baked into an environment variable that ships with the repo. :func:`load_master_key`
reads ``RR_SECRET_MASTER_KEY`` and **raises** when it is absent. A deployment without a key
cannot store or reveal a secret; it can still run, log in, collect, and report, because
``REQ-D51`` says no key is mandatory. That is the intended shape of the failure, not an
accident of it: a store that invents a key on first boot silently re-encrypts nothing and
loses every secret the next time the process restarts with a different one.

Where the ciphertext lives, and the contract gap that decides it
----------------------------------------------------------------
``secrets.md`` §4.1 puts the ciphertext in "bảng của ``MOD-secret-service``", located by
``secret_ref.store_locator``. ``contracts/data/entities.yaml`` declares **no entity** for that
table -- the module owns exactly three: ``secret_ref`` (a pointer and a state, explicitly
"không giữ giá trị"), ``task_credential`` and ``secret_audit``. Shipping a fourth, undeclared
table fails ``tests/contract/test_schema_matches_entities.py`` on its first assertion, and
writing a new entity is a contract change this card may not make (``SG-CONTRACT``,
``SG-EDGE``).

So the material sits behind :class:`SecretMaterialStore`, chosen by the composition root, and
the gap is reported as ``CR-TC-SECRET-01`` rather than papered over. Two implementations ship:
:class:`InMemoryMaterialStore` (tests, and a deployment that has not configured a store) and
:class:`FileMaterialStore` (``0600`` files under a directory the operator controls). Neither
is inside the database, which has one honest consequence worth writing down: a restored
database does **not** carry its secrets, and the operator re-enters the API key -- exactly the
"kế hoạch khôi phục secret riêng" that ``backup-restore.md`` §5 already requires because the
master key was never in the backup either.

The cipher itself lives in :mod:`server.app.secret.cipher`: **AES-256-GCM**, chosen from the
two ``secrets.md`` §4.1 offers because ``cryptography`` does not implement the other
(XChaCha20-Poly1305). It reached the lockfile in ``PKT-P0-FIX7``, which closed
``CR-TC-SECRET-02``; the lazy import and ``CipherUnavailable`` guard that stood in for it are
deleted rather than kept as dead scaffolding.

Nothing here logs. :class:`SecretValue` exists so that a value which escapes into an f-string
prints ``<redacted>`` instead of a key, and :func:`redact` is the second net for strings that
are about to be written to ``secret_audit.outcome_detail_safe`` or an error envelope.
"""

from __future__ import annotations

import base64
import os
import re
import secrets as _secrets
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Protocol

from cryptography.exceptions import InvalidTag

from server.app.secret.cipher import (
    ALGORITHM,
    KEY_BYTES,
    NONCE_BYTES,
    AeadCipher,
    AesGcm256,
    new_data_key,
    new_nonce,
)

#: ``secrets.md`` §4.1 "Nguồn master key: biến môi trường của container, hoặc file 0400".
#: The name is this implementation's; the *rule* -- outside the DB, outside the repo -- is the
#: contract's. Recorded in the handoff for ``docs/owner-runbook.md`` (outside this write set).
MASTER_KEY_ENV: Final = "RR_SECRET_MASTER_KEY"

#: Where a :class:`FileMaterialStore` puts its blobs when the composition root asks for one.
MATERIAL_DIR_ENV: Final = "RR_SECRET_MATERIAL_DIR"

#: Re-exported from :mod:`server.app.secret.cipher` so this module has no second opinion
#: about key or nonce length. ``ALGORITHM`` is carried for the evidence manifest to cite.
_KEY_BYTES: Final = KEY_BYTES
_NONCE_BYTES: Final = NONCE_BYTES

#: ``secrets.md`` §4.3 "Dạng token": ≥ 24 chars of base64url/hex with no whitespace.
_TOKEN_LIKE = re.compile(r"[A-Za-z0-9_\-+/=]{24,}")

#: ``secrets.md`` §4.3 "Tiền tố nhà cung cấp".
_PROVIDER_PREFIXED = re.compile(r"\b(?:sk|xoxb|ghp|xai|api)[-_][A-Za-z0-9_\-]{6,}")


class MasterKeyUnavailable(RuntimeError):
    """No master key is configured, so no secret can be stored or revealed.

    Deliberately not an ``ErrorCode``: this is an operator/deployment condition, not a wire
    error. The service layer turns it into the wire shape its caller is entitled to see, and
    never into a message that quotes the environment.
    """


class SecretMaterialMissing(LookupError):
    """``secret_ref.store_locator`` points at material this store does not hold."""


class MasterKeyMismatch(MasterKeyUnavailable):
    """The material exists but does not authenticate under the configured master key.

    A subclass of :class:`MasterKeyUnavailable` on purpose: to every caller it is the same
    operator-side condition -- this deployment cannot open this store -- and the service layer's
    existing handling therefore covers it without a new branch. It has its own name because the
    two causes need different fixes: a missing key is "set the variable", a mismatched key is
    "you restored a database whose secrets were written under a different key", and a traceback
    that says which one is the difference between a five-minute fix and an afternoon.

    The message never names the key, the locator's contents, or any part of the plaintext.
    """


class SecretValue:
    """A plaintext secret with a redacted ``repr``.

    The same trick ``worker/app/adapter/base.py`` plays on ``TaskCredential``, for the same
    reason: the realistic leak is not a deliberate ``print``, it is a value that lands in an
    f-string inside an exception message a year from now.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        self._value = value

    def reveal(self) -> str:
        """The one accessor. Call it where the value is used, never to build a log line."""
        return self._value

    def __repr__(self) -> str:  # pragma: no cover - trivial, but it is the whole point
        return "SecretValue(<redacted>)"

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecretValue):
            return NotImplemented
        return _secrets.compare_digest(self._value, other._value)

    def __hash__(self) -> int:  # pragma: no cover - values are not used as keys
        raise TypeError("a SecretValue is not hashable; that would leak it into a dict repr")


@dataclass(frozen=True)
class SecretMaterial:
    """One envelope: the wrapped data key and the ciphertext it decrypts.

    Stored as opaque bytes by whichever :class:`SecretMaterialStore` the deployment uses.
    Neither field is ever rendered into a message.
    """

    wrapped_data_key: bytes
    nonce: bytes
    ciphertext: bytes

    def serialise(self) -> str:
        return ".".join(
            base64.urlsafe_b64encode(part).decode("ascii")
            for part in (self.wrapped_data_key, self.nonce, self.ciphertext)
        )

    @classmethod
    def parse(cls, blob: str) -> SecretMaterial:
        try:
            wrapped, nonce, ciphertext = (
                base64.urlsafe_b64decode(part.encode("ascii")) for part in blob.split(".", 2)
            )
        except (ValueError, base64.binascii.Error) as exc:  # type: ignore[attr-defined]
            raise SecretMaterialMissing("secret material is not readable") from exc
        return cls(wrapped_data_key=wrapped, nonce=nonce, ciphertext=ciphertext)


class SecretMaterialStore(Protocol):
    """Where the envelope bytes live. See the module docstring for why this is a port."""

    def put(self, locator: str, blob: str) -> None: ...

    def get(self, locator: str) -> str | None: ...

    def delete(self, locator: str) -> None: ...


class InMemoryMaterialStore:
    """Process-local material. The default, and what the tests use.

    A restart loses the ciphertext, which is why a deployment that means to keep an API key
    across restarts configures :class:`FileMaterialStore` (or, once ``CR-TC-SECRET-01`` lands
    an entity, a table).
    """

    def __init__(self) -> None:
        self._blobs: dict[str, str] = {}

    def put(self, locator: str, blob: str) -> None:
        self._blobs[locator] = blob

    def get(self, locator: str) -> str | None:
        return self._blobs.get(locator)

    def delete(self, locator: str) -> None:
        self._blobs.pop(locator, None)


class FileMaterialStore:
    """One ``0600`` file per locator under a ``0700`` directory.

    The permission rule is ``secrets.md`` §3's, applied to the server side of the same idea:
    a secret file readable by more than its owner is a finding, not a warning. The directory
    is created with the right mode rather than fixed up afterwards.
    """

    def __init__(self, directory: Path) -> None:
        self._directory = directory
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(directory, 0o700)

    def _path(self, locator: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_\-]{1,120}", locator):
            raise SecretMaterialMissing("locator is not a valid file name")
        return self._directory / f"{locator}.env"

    def put(self, locator: str, blob: str) -> None:
        path = self._path(locator)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(descriptor, "w", encoding="ascii") as handle:
            handle.write(blob)
        os.chmod(path, 0o600)

    def get(self, locator: str) -> str | None:
        path = self._path(locator)
        if not path.exists():
            return None
        mode = stat.S_IMODE(path.stat().st_mode)
        if mode & 0o077:
            # Wider than 0600. `secrets.md` §3 refuses to start rather than warn; the
            # server-side equivalent is to refuse to read.
            raise MasterKeyUnavailable("secret material file has permissions wider than 0600")
        return path.read_text("ascii")

    def delete(self, locator: str) -> None:
        self._path(locator).unlink(missing_ok=True)


def load_master_key(environ: dict[str, str] | None = None) -> bytes:
    """The master key, from the environment. Never generated, never defaulted.

    Accepts base64url (with or without padding) or hex, and requires exactly 32 bytes. A
    malformed value raises the same error as a missing one, and neither message quotes the
    value or its length in a way that would help an attacker who can read logs.
    """
    source = os.environ if environ is None else environ
    raw = source.get(MASTER_KEY_ENV)
    if not raw:
        raise MasterKeyUnavailable(
            f"{MASTER_KEY_ENV} is not set; the secret store cannot be opened "
            "(contracts/ops/secrets.md §4.1)"
        )
    candidate = raw.strip()
    for decode in (_decode_base64url, bytes.fromhex):
        try:
            key = decode(candidate)
        except (ValueError, base64.binascii.Error):  # type: ignore[attr-defined]
            continue
        if len(key) == _KEY_BYTES:
            return key
    raise MasterKeyUnavailable(
        f"{MASTER_KEY_ENV} must decode to {_KEY_BYTES} bytes of base64url or hex"
    )


def _decode_base64url(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def generate_master_key() -> str:
    """A key an **operator** can paste into their environment. Never called by the server.

    It exists so the runbook can say "run this once and store the output where you keep your
    other secrets" instead of leaving the operator to invent a key generation ritual. Nothing
    in the request path calls it, and it writes nothing to disk.
    """
    return base64.urlsafe_b64encode(new_data_key()).decode("ascii").rstrip("=")


def redact(text: str, *known: str) -> str:
    """Mask before writing (``secrets.md`` §4.3 / ``SEC-P6``), not before displaying.

    Order matters: the known plaintexts first (they may be shorter than the token pattern),
    then provider-prefixed keys, then anything token-shaped. The pattern net is the *second*
    line of defence -- §4.3 says so in as many words -- and this function existing is not a
    licence to build a string that contains a key.
    """
    masked = text
    for value in known:
        if value:
            masked = masked.replace(value, "[REDACTED:value]")
    masked = _PROVIDER_PREFIXED.sub("[REDACTED:provider-key]", masked)
    return _TOKEN_LIKE.sub("[REDACTED:token-like]", masked)


class SecretStore:
    """Envelope encryption over an injected :class:`SecretMaterialStore`.

    One data key per secret, wrapped under the master key. The locator is bound into both
    AEADs as associated data, so material moved between locators -- by a restore, a bug, or a
    hand edit -- fails to decrypt instead of decrypting as the wrong secret.
    """

    def __init__(
        self,
        *,
        master_key: bytes,
        material: SecretMaterialStore,
        cipher: AeadCipher | None = None,
    ) -> None:
        if len(master_key) != _KEY_BYTES:
            raise MasterKeyUnavailable("master key must be 32 bytes")
        self._master_key = master_key
        self._cipher: AeadCipher = AesGcm256() if cipher is None else cipher
        self._material = material

    def store(self, *, locator: str, purpose: str, value: str) -> None:
        """Encrypt ``value`` under a fresh data key and hand the envelope to the store."""
        data_key = new_data_key()
        aad = self._aad(locator, purpose)
        wrap_nonce = new_nonce()
        wrapped = wrap_nonce + self._cipher.encrypt(self._master_key, wrap_nonce, data_key, aad)
        nonce = new_nonce()
        ciphertext = self._cipher.encrypt(data_key, nonce, value.encode("utf-8"), aad)
        envelope = SecretMaterial(wrapped_data_key=wrapped, nonce=nonce, ciphertext=ciphertext)
        self._material.put(locator, envelope.serialise())

    def reveal(self, *, locator: str, purpose: str) -> SecretValue:
        """Decrypt. The only path from stored bytes back to a plaintext, and it is not public.

        ``contracts/ops/secrets.md`` §4.2: only ``MOD-secret-service`` reads a value. The
        service layer calls this to build a task credential and for nothing else; no operation
        returns what comes back here to a caller outside the module.
        """
        blob = self._material.get(locator)
        if blob is None:
            raise SecretMaterialMissing(f"no material for locator {locator!r}")
        envelope = SecretMaterial.parse(blob)
        aad = self._aad(locator, purpose)
        wrap_nonce, wrapped = (
            envelope.wrapped_data_key[:_NONCE_BYTES],
            (envelope.wrapped_data_key[_NONCE_BYTES:]),
        )
        try:
            data_key = self._cipher.decrypt(self._master_key, wrap_nonce, wrapped, aad)
            plaintext = self._cipher.decrypt(data_key, envelope.nonce, envelope.ciphertext, aad)
        except InvalidTag as exc:
            # AEAD authentication failed: wrong master key, or material moved between locators
            # or purposes (both are bound in as associated data). Deliberately not retried and
            # not softened into "missing" -- an unreadable secret and an absent one are
            # different facts about the deployment.
            raise MasterKeyMismatch(
                "stored secret material does not authenticate under the configured master key"
            ) from exc
        return SecretValue(plaintext.decode("utf-8"))

    def forget(self, *, locator: str) -> None:
        self._material.delete(locator)

    @staticmethod
    def _aad(locator: str, purpose: str) -> bytes:
        return f"{purpose}:{locator}".encode()


__all__ = [
    "MASTER_KEY_ENV",
    "MATERIAL_DIR_ENV",
    "ALGORITHM",
    "AeadCipher",
    "AesGcm256",
    "FileMaterialStore",
    "InMemoryMaterialStore",
    "MasterKeyMismatch",
    "MasterKeyUnavailable",
    "SecretMaterial",
    "SecretMaterialMissing",
    "SecretMaterialStore",
    "SecretStore",
    "SecretValue",
    "generate_master_key",
    "load_master_key",
    "redact",
]
