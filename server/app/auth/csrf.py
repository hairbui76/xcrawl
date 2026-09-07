"""CSRF double-submit primitives.

Contract: ``contracts/ops/secrets.md`` §2.3 and ``contracts/http/openapi.yaml``
``components.securitySchemes.ownerCsrfToken``.

The mechanism, in one sentence: the same random value is written to a **non-HttpOnly**
cookie ``rr_csrf`` and must be echoed back in the header ``X-CSRF-Token`` on every owner
mutation, so a cross-site form post -- which carries cookies automatically but cannot read
them -- cannot produce the header.

Two rules that are easy to get wrong and are therefore enforced here rather than at each
call site:

* A missing or mismatched token is ``CSRF_REJECTED`` (403), **not** ``FORBIDDEN_EDGE``:
  the caller→callee edge is legitimate, only the proof of user intent is absent
  (``contracts/errors.yaml`` code ``CSRF_REJECTED``, ``distinct_from_vi``; card §10
  ``SG-CSRF``).
* The session is **not** revoked by a CSRF failure. Turning an integration bug into a
  forced logout is listed under ``forbidden_vi`` of the same code.

Token values are never logged, never put in an error envelope and never compared with
``==``: :func:`csrf_matches` uses :func:`hmac.compare_digest`.
"""

from __future__ import annotations

import hmac
import secrets

#: Non-HttpOnly cookie carrying the CSRF token (contracts/ops/secrets.md §2.3).
CSRF_COOKIE_NAME = "rr_csrf"

#: Header the browser must echo it in (openapi `components.parameters.CsrfTokenHeader`).
CSRF_HEADER_NAME = "X-CSRF-Token"

#: contracts/ops/secrets.md §2.3 `csrf_token_length` = 128 bit (PROVISIONAL).
CSRF_TOKEN_BITS = 128

#: 128 bits rendered as hex = 32 characters, which satisfies the openapi schema for
#: `X-CSRF-Token` (`minLength: 32`, `maxLength: 128`) at its lower bound.
_CSRF_TOKEN_BYTES = CSRF_TOKEN_BITS // 8


def new_csrf_token() -> str:
    """Return a fresh 128-bit CSRF token as 32 lowercase hex characters."""
    return secrets.token_hex(_CSRF_TOKEN_BYTES)


def csrf_matches(header_value: str | None, cookie_value: str | None) -> bool:
    """Whether the double-submit holds.

    Absent on either side is a mismatch: a request that never carried the header is
    exactly the cross-site case this check exists for, so "missing" and "wrong" get the
    same answer and the same error code.
    """
    if not header_value or not cookie_value:
        return False
    return hmac.compare_digest(header_value, cookie_value)
