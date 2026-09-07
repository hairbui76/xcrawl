# TASK_PACKET PKT-PC09 — Khóa oracle, traceability, evidence và readiness

- packet_id: `PKT-PC09` · assignee_role: Worker · assignee_principal: `worker-W6`
- authority_id: `AUTH-COORD-PC09` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC09-e1` (exclusive, fencing 1)
- expires_at: 2026-09-07T12:00Z · enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir: `…/scratchpad/w6/`

## Goal
Execute plan §11 **PC09**: the scenario catalogue with oracles (SC01–SC28+), full traceability (every P0/D/AC/invariant/error → contract → scenario → evidence type), the evidence manifest schema + index, the gate definitions, the E0 static-check tooling (run for real, results recorded), baseline-invalidation rules, A2/A3/A4 evaluation design, and the readiness/blocker review. You are the verification owner: you check the whole baseline PC00–PC08 and record what is READY/BLOCKED per module.

## Non-goals
Do not fix other packages' files (raise findings as `CR-PC09-nn` in your review; the Coordinator dispatches remediation). No E1–E4 execution (record NOT_RUN). No product code. Do not change the sources.

## Read set (frozen at dispatch; you will be given the manifest path)
Everything under `precode/`, `contracts/`, `acceptance/`, `evidence/handoffs/`, plus baseline, SRC-PLAN, SRC-SPEC, `agent_profile/*`. Also the Coordinator's audit reports (paths given in the dispatch) — treat their OPEN findings as inputs to your blocker review.

## Write targets (all CREATE, baseline ABSENT)
| Path | Content |
| --- | --- |
| `acceptance/scenarios.yaml` | SC01–SC18 (one per AC, aligned to plan §13 table), SC19–SC28 (plan §13 list, in order), plus any SC29+ needed so that every invariant I01–I15 has ≥1 positive and ≥1 negative scenario and every error code in `contracts/errors.yaml` has ≥1 scenario. Each scenario: id, title_vi, requirement_refs, invariant_refs, contract_refs (file paths + contract ids), error_refs, fixture_refs (existing fixture files — reference by path; if a needed fixture is missing, mark `fixture: MISSING` and raise CR), input/event order, expected durable state (rows/counts/hashes), forbidden effects, oracle (independent expected result), evidence level required for acceptance (E0–E4), what can be mocked vs what needs live/human review, status `NOT_RUN`. |
| `acceptance/traceability.csv` | columns: `req_id,req_status,priority,contract_refs,invariant_refs,scenario_refs,error_refs,evidence_level,coverage_status,notes`. One row per requirement in `precode/requirements.csv` (all of them, not only AC). `coverage_status ∈ {COVERED, PARTIAL, ORPHAN, DEFERRED_P1, OUT_OF_SCOPE, BLOCKED_B..}`. |
| `evidence/manifest.schema.json` | JSON Schema 2020-12 for evidence manifests per plan §14.1 (identity, baseline, environment, inputs, execution, result enum, artifacts with sha256, limitations, NOT_APPLICABLE requires reason + decision ref). |
| `evidence/index.json` | validates against manifest.schema.json: one entry per E0 check you ran (real command, timestamps, exit code, result), plus explicit `NOT_RUN` placeholders for E1–E4 per scenario group. Include contract file hashes (baseline) at the time of the run. |
| `evidence/tools/README.md` + `evidence/tools/e0_check.py` | the E0 tool (python3 stdlib + PyYAML + jsonschema only): (1) YAML/JSON parse of every file under contracts/ acceptance/ precode/; (2) JSON schemas metaschema check; (3) fixture validation against their schemas (registry of local `$id`s); (4) reference integrity: every operation id cited anywhere exists in ports.yaml; every error code exists in errors.yaml; every REQ id cited exists in requirements.csv; every SC/I/B/ADR/AMD id cited exists; every contract header has the baseline §3 fields; (5) state lint (enums/transitions/terminals) for contracts/state/*.yaml; (6) denied-edge scenarios exist for every forbidden edge in modules.yaml; (7) traceability: no ORPHAN P0/XN/UQ requirement; every invariant has ≥1 negative scenario; (8) forbidden strings: `TBD`, `CLOSED`, `ACCEPTED` (as status), claims above DRAFT_FOR_REVIEW; (9) coverage windows contiguous in reporting fixtures. Output: machine-readable JSON report + human summary; exit non-zero on FAIL. Run it from your scratch dir; write its JSON output to `evidence/runs/E0-<UTC>.json`. |
| `evidence/runs/E0-<UTCstamp>.json` | the real E0 output (may contain FAILs — report them honestly; do not edit other files to make them pass). |
| `precode/gates.yaml` | G0–G7, SP1: entry conditions, exit conditions (machine-checkable where possible, referencing e0_check checks and scenario groups), invalidation rules (plan §16: which changes STALE which evidence), current status per gate with evidence refs (expect G0–G3 `MET_PROVISIONAL` at best, G4 conditional on owner ratification and open findings, G5+ NOT_MET). |
| `precode/review.md` | Front-matter. Readiness report: per module (from modules.yaml) READY_FOR_CARD / BLOCKED with reasons (open B, open findings, missing fixtures, KC gates); requirement coverage numbers; E0 results summary with run id; list of all PROVISIONAL decisions awaiting the Owner (aggregate from decision-register + every package's unresolved refs + handoffs); all CR-* raised by packages, consolidated with disposition proposal (not decision); A2/A3/A4 evaluation design (rubrics locked before tuning, calibration vs evaluation sets, denominators, who judges, weekly success criteria, minimum periods; insufficient data → insufficient evidence); B01–B17 re-review table; ĐX/KC registry review; explicit claim: `DRAFT_FOR_REVIEW`, with the conditional statement of which scopes become CONTRACT_READY upon which ratifications and finding closures. |
| `evidence/handoffs/PC09-handoff.md` | HANDOFF |

Directory grants: `evidence/tools/`, `evidence/runs/`.

## Checklist (plan PC09)
1. [ ] All P0 and AC-01..18 mapped to contract, invariant, scenario, evidence type — and the full D registry too.
2. [ ] Fixtures with independent right/wrong data; mockable vs live/human stated.
3. [ ] E0 validation actually run; results recorded (FAILs included).
4. [ ] Evidence manifest + invalidation rules; NOT_RUN everywhere nothing ran.
5. [ ] A2/A3/A4 design with separated calibration/evaluation sets; rubric locked.
6. [ ] B01–B17, ĐX/KC, decisions, code-ready scope per module reviewed.

## Verification (EV-PC09-nn, SELF_VALIDATION)
- EV-01: e0_check run (exit code, counts). EV-02: index.json validates against manifest.schema.json. EV-03: traceability.csv row count == requirements.csv row count; no ORPHAN among P0/XN/UQ or explain. EV-04: scenarios.yaml: every AC has SC; every invariant has pos+neg; every error code has SC.

## Stop gates
Baseline §6. Do not "fix" upstream files. Do not downgrade a FAIL to PASS by narrowing checks; instead report and CR.
