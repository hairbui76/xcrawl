# GENERATED — do not edit; source sha256 contracts/schemas/analysis-result.schema.json=f26720ee04852161…, contracts/schemas/ingest-batch.schema.json=8ab444f557645ee8…, contracts/schemas/ingest-receipt.schema.json=ff5232f46bb08369…, contracts/schemas/report.schema.json=8bf6bc9ccd6040c0…, contracts/schemas/saved-snapshot.schema.json=1178d314deb8dfdf…, contracts/schemas/target.schema.json=d1ce487d2e4ba24b…, contracts/schemas/worker-assignment.schema.json=14efde6fdbff8a19…, contracts/state/analysis.yaml=06b18de42c3bbfff…, contracts/state/delivery.yaml=318789179ec79a4e…, contracts/state/report.yaml=77969cb473c84a7d…, contracts/state/run.yaml=479125cb0d927c69…, contracts/state/storage.yaml=a77803f1690ee774…, contracts/errors.yaml=640991c91ad046eb…, contracts/ports.yaml=c7c7734001b98f25…, contracts/http/openapi.yaml=a3e7e42203bdb2c2…
# Produced by shared/rr_contracts/generate.py from the contract file(s) named above.
# Editing this file by hand makes code and contract drift apart silently; the rule is
# ADR-0011 (Hệ quả) and agent-tasks/README.md §5.3. To change behaviour: change the
# contract, regenerate, and mark the affected task cards STALE per INV-06.
#   contracts/schemas/analysis-result.schema.json  sha256:f26720ee04852161b4e71b4ab61c0f11c0187fcbfd25759e05245cfdb7ac172d
#   contracts/schemas/ingest-batch.schema.json  sha256:8ab444f557645ee85dbd0951af7261ac4355d3a0b8ca6b96d8450c9e1a5ae690
#   contracts/schemas/ingest-receipt.schema.json  sha256:ff5232f46bb08369ea9af653d652d7782a42ea16798992f2507878c964ac537c
#   contracts/schemas/report.schema.json  sha256:8bf6bc9ccd6040c06f4ba709ea638e647ab8349e1bac4f26cd6049df76b7ba60
#   contracts/schemas/saved-snapshot.schema.json  sha256:1178d314deb8dfdfbe24a9bd4645fd0fd34424fa1db0c237971b3dba3705ce3c
#   contracts/schemas/target.schema.json  sha256:d1ce487d2e4ba24b094f702b38a5fcac517443981fe8faea36472089124dc0fd
#   contracts/schemas/worker-assignment.schema.json  sha256:14efde6fdbff8a19ed2d931660a2752cc40ae96a2ecb1aa5594bdcba87fd5c18
#   contracts/state/analysis.yaml  sha256:06b18de42c3bbffff9a74b2e990025361cf2b179736f1994a5558f5eef3618ce
#   contracts/state/delivery.yaml  sha256:318789179ec79a4e21939a82d4fb78bfb3cd257ed7c3af4c519bf2ab631ee807
#   contracts/state/report.yaml  sha256:77969cb473c84a7df90e6b784ad1afa637313e813ccbb59d99b1ea329241245f
#   contracts/state/run.yaml  sha256:479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27
#   contracts/state/storage.yaml  sha256:a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849
#   contracts/errors.yaml  sha256:640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f
#   contracts/ports.yaml  sha256:c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412
#   contracts/http/openapi.yaml  sha256:a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d

"""Generated contract bindings.

Nothing in this package is written by hand. See shared/rr_contracts/generate.py.
"""

from rr_contracts.generated import constants as constants
from rr_contracts.generated import errors as errors
from rr_contracts.generated import models as models
from rr_contracts.generated import operations as operations
from rr_contracts.generated import states as states
from rr_contracts.generated.errors import ErrorCode as ErrorCode
from rr_contracts.generated.operations import OperationId as OperationId

__all__ = [
    "ErrorCode",
    "OperationId",
    "constants",
    "errors",
    "models",
    "operations",
    "states",
]
