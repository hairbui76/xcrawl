# REVIEW TASK_PACKET PKT-A3-R2 — Scoped re-review of F-A3R1-01…15 fixes + the ENT-owner amendment (FC-P1 epoch 2)

- packet_id: `PKT-A3-R2` · assignee: `auditor-A3` · authority `AUTH-COORD-A3-R2` (parent `AUTH-OWNER-20260907-03`) · lease null (read-only; running tests/linters may create only git-ignored artefacts — check `git status --porcelain` before/after)
- report path: `…/scratchpad/audits/A3-R2-report.md` · helpers under `…/scratchpad/a3/`
- Frozen candidate FC-P1 epoch 2 manifest: `…/scratchpad/audits/FC-P1e2-manifest.txt` (manifest_sha256 in header). Recompute at start and end.

## Inputs
Your `A3-R1-report.md`; rulings `…/scratchpad/packets/FIX-A3R1-rulings.md`; addenda: PC02-FIX12 (entities amendment AMD-ENT-owner-01 + change-control + register rows), P0-FIX2 (faults.py adoption, README, regenerated rr_contracts), TC-IDENTITY-FIX1, TC-INGEST-FIX1, TC-STORAGE-FIX1, TC-AUTH-FIX1, PC10-FIX18 (re-pin P1c); the cards' updated evidence manifests if re-issued.

## Method
1. For each F-A3R1-01…15: re-run your original reproduction against epoch-2 bytes; verdict VERIFIED | NOT_VERIFIED | PARTIAL with evidence. In particular: force both Alembic branch orders and assert the owner constraint set (F-01); run the new `tests/contract/test_schema_matches_entities.py` and independently diff `PRAGMA table_info`/`foreign_key_list`/`sqlite_master` DDL against entities.yaml for every table (F-02, F-05, F-14); restart the factory mid-lockout (F-06); count exercised sweep events vs the 36 and check the 15 CAPABILITY_DENIED are recorded NOT_TESTABLE, not passed (F-08); token hashing + constant-time compare (F-12); install hooks on the bare factory (F-11); delimiters (F-13); `__init__` (F-10); fixtures exercised or NOT_RUN (F-09); faults.py adoption recorded (F-07); README (F-15); five foreign tables moved to `0002b_shared_move_set_tables` with ownership header (F-04). F-03 (index.json) is PC09's and will be verified in a later round — record as DEFERRED, not verified.
2. **Contract amendment review** (you are independent of it): AMD-ENT-owner-01 in entities.yaml — four fields, reasons cite secrets.md/D05, version bumped, amendment block with decision refs and "Owner may object", CONTRACT_READY retained with re-verification note; change-control.md entry per its own format; decision-register row PROVISIONAL; `shared/rr_contracts` regenerated (GENERATED_FROM hashes = current entities.yaml; generated-matches tests pass); no other contract file changed (diff vs `da886f8` for contracts/, acceptance/, precode/ excluding the recorded PC00/PC02/PC10 changes).
3. Full evidence reproduction again: `uv sync --all-packages`, `uv run pytest` (whole workspace), ruff, mypy, web tests, e0_check read-only (24/24 or the new count), verify_cards (13/13, epoch P1c), OpenAPI validator; compare with the Workers' claims.
4. Per-card claim verdicts: may IMPLEMENTATION_VERIFIED stand for each of the four (scoped as you state)? Skeleton verdict. Overall verdict. New findings only in the fix diff (`F-A3R2-nn`); other observations deferred.

## Report
Verification table; amendment verdict; per-card + claim verdicts; overall; residual list. Reply ONLY: overall; per-card claim verdicts; verification verdicts one line each; new finding counts; report path (≤30 lines).
