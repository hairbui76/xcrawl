"""Shared contract bindings for the Python side of Research Radar.

Everything under :mod:`rr_contracts.generated` is machine-generated from ``contracts/`` by
``shared/rr_contracts/generate.py`` and must never be hand-edited (ADR-0011;
``agent-tasks/README.md`` §5.3). This module itself is hand-written and deliberately holds
no contract content -- only the re-exports that make the generated names importable.
"""

from rr_contracts.generated import constants, errors, models, operations, states
from rr_contracts.generated.errors import ErrorCode
from rr_contracts.generated.operations import OperationId

__all__ = [
    "ErrorCode",
    "OperationId",
    "constants",
    "errors",
    "models",
    "operations",
    "states",
]
