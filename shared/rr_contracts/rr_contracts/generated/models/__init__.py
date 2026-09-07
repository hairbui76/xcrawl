# GENERATED — do not edit; source sha256 contracts/schemas/analysis-result.schema.json=f26720ee04852161…, contracts/schemas/ingest-batch.schema.json=8ab444f557645ee8…, contracts/schemas/ingest-receipt.schema.json=ff5232f46bb08369…, contracts/schemas/report.schema.json=8bf6bc9ccd6040c0…, contracts/schemas/saved-snapshot.schema.json=1178d314deb8dfdf…, contracts/schemas/target.schema.json=d1ce487d2e4ba24b…, contracts/schemas/worker-assignment.schema.json=14efde6fdbff8a19…
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

"""Pydantic v2 models generated from contracts/schemas/*.json."""

from rr_contracts.generated.models import analysis_result as analysis_result
from rr_contracts.generated.models import ingest_batch as ingest_batch
from rr_contracts.generated.models import ingest_receipt as ingest_receipt
from rr_contracts.generated.models import report as report
from rr_contracts.generated.models import saved_snapshot as saved_snapshot
from rr_contracts.generated.models import target as target
from rr_contracts.generated.models import worker_assignment as worker_assignment

__all__ = [
    "analysis_result",
    "ingest_batch",
    "ingest_receipt",
    "report",
    "saved_snapshot",
    "target",
    "worker_assignment",
]
