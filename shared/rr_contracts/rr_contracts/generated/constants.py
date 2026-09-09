# GENERATED — do not edit; source sha256 contracts/http/openapi.yaml=a3e7e42203bdb2c2…, contracts/errors.yaml=640991c91ad046eb…
# Produced by shared/rr_contracts/generate.py from the contract file(s) named above.
# Editing this file by hand makes code and contract drift apart silently; the rule is
# ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change behaviour: change the
# contract, regenerate, and mark the affected task cards STALE per INV-06.
#   contracts/http/openapi.yaml  sha256:a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d
#   contracts/errors.yaml  sha256:640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f

"""Wire constants generated from the contracts.

``CONTRACT_SCHEMA_VERSION`` is ``info.version`` of contracts/http/openapi.yaml. It
is the version a process declares it speaks (SRC-PLAN §5.1); it is not the version
of this package.
"""

from __future__ import annotations

CONTRACT_SCHEMA_VERSION: str = "0.3.0"
OPENAPI_VERSION: str = "3.1.0"

#: Field names of the error envelope (contracts/errors.yaml `error_envelope.fields`).
ERROR_ENVELOPE_FIELDS: tuple[str, ...] = ('code', 'scope', 'retry_class', 'message_safe', 'correlation_id', 'details_safe', 'retry_after_ms')

#: Security scheme names of contracts/http/openapi.yaml, in contract order.
SECURITY_SCHEMES: tuple[str, ...] = ('ownerSessionCookie', 'ownerCsrfToken', 'collectorToken', 'analysisWorkerToken', 'telegramIngressSecret', 'backupOperatorToken')
