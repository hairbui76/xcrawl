# REVIEW TASK_PACKET PKT-A3-P2-R1 — independent review of Phase 2 (FC-P2)

- packet_id: `PKT-A3-P2-R1` · assignee: `auditor-A3` · authority `AUTH-COORD-A3-P2-R1` (parent `AUTH-OWNER-20260907-05`) · lease null (read-only; running tests/linters may create only git-ignored artefacts — check `git status --porcelain` before/after)
- report path: `…/scratchpad/audits/A3-P2-R1-report.md`
- Frozen candidate: `…/scratchpad/audits/FC-P2-manifest.txt` (manifest_sha256 `dafc1c83ca2108d50ccc5cc700115849b9537be31ff0155f5dd37c7bc5e469f0`, 466 entries, algorithm `sha256-path-role-hash-bytes-v1`, git-tracked + untracked-not-ignored, `.claude/` deliberately excluded). Recompute at start and end.

## What's new since FC-P1 (Phase 0/1), for orientation — verify all of it independently
1. Two new task cards implemented: `TC-collector-checkpoint-resume` and `TC-research-connector-metadata`. Both claim `IMPLEMENTATION_VERIFIED` at SELF_VALIDATION pending review.
2. Third card, tooling only: `TC-x-feasibility-probe` — produces probe tooling, not a live feasibility result; `evidence/runs/SP1-x-feasibility/runs.jsonl` must not exist.
3. Contract changes: `contracts/data/entities.yaml` amendment `AMD-ENT-owner-01` ratified; `contracts/retry-policy.yaml` 0.6.0→0.8.0 (`research_connector_rate_limit` PLACEHOLDER_KC → DOCS_derived, all four REQ-A6 facts resolved from official documentation under a one-off Owner-authorised, narrowly-hosted network grant — verify citations are real quotes at real URLs); `contracts/ops/collector-probe.md` 0.3.0→0.5.0.
4. Owner decisions OD-20260907-03 and -04 recorded. Verify the network-grant boundary was honoured: no code/test/fixture references `export.arxiv.org`/`api.openalex.org` as anything but forbidden; no evidence of a live call to either API.
5. `precode/requirements.csv` + `acceptance/traceability.csv`: REQ-A6, REQ-D34, REQ-S13.2-01 moved KC→XN; new `AMD-SPEC-D34-01` records the spec's OpenAlex-contact-email premise as superseded without editing the immutable spec file — verify byte-unchanged against pin.
6. All 19 cards re-pinned four times this phase (P2→P2b→P2c→P2d, final `PC10-PIN-P2d-20260907`) chasing precode/contract churn — verify §1–§13 byte-identical across epochs, only §0 moved.
7. `TC-research-connector-metadata` §9/§10 rewritten mid-phase (CR-PC10-14) — verify current wording matches current code behaviour.
8. Migration `0005_tc_research_connector_metadata` added; single-head test fixed (CR-TC-research-01) to assert `len(heads)==1` structurally — verify the fix is real, not a cover-up.

## Method
1. Full regression from clean env: uv sync, uv run pytest (whole workspace), ruff, mypy --strict, web tests, e0_check.py, verify_cards.py, OpenAPI validator, alembic (confirm exactly one head from blank DB).
2. For each code card: independently verify claims, confirm no network call anywhere (instrument/patch sockets), confirm connector defaults derive from retry-policy.yaml (not duplicated), confirm null-override still refuses.
3. Independently re-derive at least two of the four REQ-A6 facts from official documentation yourself (same docs-only network grant, same host restriction) and confirm they match retry-policy.yaml.
4. Spot-check AMD-SPEC-D34-01 format against decision-register.md §3's convention; confirm spec file hash matches long-standing pin.
5. Scan the whole diff for undeclared writes, scope creep, or lease violations.

## Report
Verification table; overall verdict; new findings (`F-A3-P2-nn`) with severity; residual open list. Reply ONLY: overall verdict, per-card claim verdicts, key check results, new finding count + severities, report path (≤30 lines).
