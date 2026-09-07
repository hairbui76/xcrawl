# Coordinator rulings — FIX7 (residuals from E0 run E0-20260907T012946Z, check E0-04b) — 2026-09-07T01:40Z

| Token (where) | Ruling | Owner |
| --- | --- | --- |
| `run.rate_limited_at` (openapi, collector-probe, run.yaml) | Real column introduced by PC03-FIX3 but missing from entities.yaml → **add** `run.rate_limited_at` (nullable RFC3339 ms). No change in the citing files. | W3 |
| `report.selection_version` (selection.md; also in report.schema.json) | Real, missing → **add** `report.selection_version` (string, selection algorithm/config version; NOT NULL for published reports). | W3 |
| `delivery.created_at` (retry-policy.yaml, delivery.md) | Missing → **add** `delivery.created_at` (RFC3339 ms, NOT NULL); add `created_at`/`updated_at` where the transaction map relies on them. | W3 |
| `tag.updated_at` (screens.yaml) | Missing → **add** `tag.created_at`, `tag.updated_at`. | W3 |
| `run.last_run` (time-and-tags.md) | D12 "last_run" is a display value of the worker, not a run column → cite `worker_registration.last_run_at` (**add** that column, nullable RFC3339) and rewrite the prose. | W3 (column), W5 (prose) |
| `work.resolution_rule` (selection.md) | Not a column; cite the identity resolution rule id from `contracts/data/identity.md` instead. | W5 |
| `embedding.start_generation`, `embedding.switch_generation` (reporting fixture n note) | Stale names in an in-file note → rewrite the note without the stale tokens (history lives in the handoff). | W5 |
| `SAVE_ALREADY_EXISTS` (entities.yaml note, ports.yaml note) | Historical mentions of an unregistered code do not belong in contract prose → remove; history stays in handoffs. | W3 (entities), W2 (ports) |
| E0-04b design | A `<a>.<b>` token resolves if it is an operation in ports.yaml **or** an `entity.column` pair in entities.yaml; otherwise violation. Split reporting into `E0-04b-prose-op-tokens` and `E0-04c-prose-column-tokens`. Run a negative self-test for both (mutate one id) and record it. | W6 |
| SC54–SC56 anchors | PC00 anchors with `subject_vi` from scenarios.yaml (origin PC09). | W1 |
| Card pins | After W2/W3/W5 land: re-pin as `PC10-PIN-FCW4d-20260907`. | W7 |
