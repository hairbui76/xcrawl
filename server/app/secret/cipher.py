"""The one cryptographic primitive this module needs: a 256-bit AEAD.

``contracts/ops/secrets.md`` §4.1, row *Thuật toán*:

    AEAD 256-bit (AES-256-GCM hoặc XChaCha20-Poly1305) | PROVISIONAL | AEAD cho cả bí mật lẫn
    toàn vẹn; chọn cụ thể khi chốt stack (ADR-0006, Option A Python).

**AES-256-GCM is the choice**, and §10 is what makes it this card's to make: "Ngôn ngữ/thư viện
cụ thể để hiện thực băm và AEAD | PC10 sau khi chốt stack". The clause names two algorithms and
mandates neither; the second is not available. ``cryptography`` 46 ships ``AESGCM`` and the
IETF ``ChaCha20Poly1305`` (96-bit nonce), but **not** XChaCha20-Poly1305 (192-bit nonce) —
different construction, different nonce budget, not the thing §4.1 names. So the reachable
option is the first, and it is recorded here rather than in a commit message because a future
reader deserves to know that the alternative was checked and found absent, not overlooked.

Why this is a port and not a function
-------------------------------------
``AeadCipher`` exists so that :class:`server.app.secret.store.SecretStore` depends on an
interface rather than on a package. That is what let the store be written, tested and reviewed
while ``uv.lock`` still had no AEAD at all (``CR-TC-SECRET-02``, now closed by ``PKT-P0-FIX7``
adding ``cryptography>=43,<47``). The port stays because it is also how a test substitutes a
deliberately-not-encryption double without that double living in production code.

Nonce discipline
----------------
GCM's failure mode is nonce reuse under the same key: two messages sharing a (key, nonce) pair
leak their XOR and, worse, the authentication subkey. This module therefore mints every nonce
from :func:`secrets.token_bytes` and never accepts one from a caller, and each secret gets its
own data key, so the birthday bound is computed per data key over a handful of messages rather
than across the whole store. ``tests/contract/test_secret_scope_matrix.py`` asserts uniqueness
across repeated encryptions instead of trusting this paragraph.
"""

from __future__ import annotations

import secrets as _secrets
from typing import Final, Protocol

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

#: AES-256: 32-byte keys, and the reason ``load_master_key`` rejects anything shorter.
KEY_BYTES: Final = 32

#: 96 bits, the size GCM is specified for. Anything else forces GCM's nonce-derivation path,
#: which is a different (and weaker-documented) construction.
NONCE_BYTES: Final = 12

#: What §4.1 was satisfied with, recorded as data so a manifest can cite it.
ALGORITHM: Final = "AES-256-GCM"


class AeadCipher(Protocol):
    """256-bit AEAD over an explicit (key, nonce, plaintext, associated data).

    Anything satisfying this and actually being an AEAD is a legitimate backend; anything
    satisfying it and *not* being one has to say so in its own name.
    """

    def encrypt(self, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes: ...

    def decrypt(self, key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes: ...


class AesGcm256:
    """AES-256-GCM via ``cryptography`` — the production backend.

    The import is now a plain module-level import: ``cryptography>=43,<47`` is a declared
    dependency of ``rr-server`` (``PKT-P0-FIX7``), so a deployment that can import this package
    can encrypt. The previous lazy import and its ``CipherUnavailable`` guard existed only
    because the dependency was missing, and they are gone rather than left as decoration — an
    unreachable guard is a claim about the world that stopped being true.
    """

    algorithm: Final = ALGORITHM

    def encrypt(self, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes:
        return bytes(AESGCM(key).encrypt(nonce, plaintext, aad))

    def decrypt(self, key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
        return bytes(AESGCM(key).decrypt(nonce, ciphertext, aad))


def new_nonce() -> bytes:
    """A fresh 96-bit nonce. The only nonce source in this package."""
    return _secrets.token_bytes(NONCE_BYTES)


def new_data_key() -> bytes:
    """A fresh 256-bit data key — one per secret, per ``secrets.md`` §4.1's envelope rule."""
    return _secrets.token_bytes(KEY_BYTES)


__all__ = [
    "ALGORITHM",
    "KEY_BYTES",
    "NONCE_BYTES",
    "AeadCipher",
    "AesGcm256",
    "new_data_key",
    "new_nonce",
]
