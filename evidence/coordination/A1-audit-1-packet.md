# REVIEW TASK_PACKET PKT-A1-R1 — Independent audit of frozen candidate FC-W1 (PC00, PC01, PC02)

- packet_id: `PKT-A1-R1` · assignee_role: Auditor · assignee_principal: `auditor-A1`
- authority_id: `AUTH-COORD-A1-R1` (parent `AUTH-OWNER-20260906-01`) · lease_id: null (read-only; you write nothing in the repo)
- write_targets: none in the repo. Your AUDIT_REPORT goes to `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/audits/A1-R1-report.md` (Coordinator-designated evidence sink outside the project tree). Helper scripts only under `…/scratchpad/a1/`. PYTHONDONTWRITEBYTECODE=1. No git mutation, no network.
- audit_route rationale: agent-authority-style contracts with cross-package dependencies; residual uncertainty about ID consistency and requirement coverage; HIGH complexity → INDEPENDENT_REQUIRED.
- completion_ceiling of the candidate: DRAFT_FOR_REVIEW.

## Independence declaration required
You have authored nothing in this repo. State this in the report. If you find you cannot judge without editing, report BLOCKED — never patch.

## Frozen candidate FC-W1 (epoch 1)
The Coordinator's manifest (path, sha256, bytes) is in `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/audits/FC-W1-manifest.txt`. Recompute every hash at the start and at the end; any mismatch → verdict STALE for the affected scope. Writers W1/W2/W3 have released their leases (handoffs in `evidence/handoffs/PC00|PC01|PC02-handoff.md`).

## Read set
- Coordinator baseline: `…/scratchpad/packets/00-coordination-baseline.md` (rules the candidate must meet), packets `PC00-packet.md`, `PC01-packet.md`, `PC02-packet.md` (the requirements each worker had).
- Sources SRC-PLAN, SRC-SPEC (hashes in baseline §2).
- `agent_profile/auditor.md`, `protocol.md`.
- All manifest files.

## Method (protocol §7 + auditor.md)
1. Hash verification; manifest completeness vs handoff `changes` tables (every file listed in handoff exists, every created file is in the manifest; extra untracked files in `precode/`, `contracts/`, `acceptance/`, `evidence/` not in the manifest = finding).
2. Requirement → contract chain: sample ≥ 25 requirement rows across categories from `precode/requirements.csv` and check source fidelity (does the anchor say that?), status fidelity (XN/UQ/ĐX/KC matches the spec), and coverage (every D-ID, AC, P0, A, OQ present — rerun the coverage check yourself).
3. Blocker register: B01–B17 each present once, PROVISIONAL (never CLOSED), recommendation matches baseline §5, amendments have before/after/oracle, ADRs consistent with register and with PC01/PC02 choices (e.g. topology in ADR-0001 = modules.yaml edges; identity in ADR-0009 = identity.md).
4. PC01: default-deny stated; every plan §6 row represented; every negative case present with error code; ports.yaml complete against the packet's minimum operation list; no duplicate operation IDs; each mutation has exactly one owner module; operations referenced by modules.yaml exist.
5. PC02: entities cover spec §7.1 + packet additions; `owner_id` everywhere; target union; UNIQUE guarantees stated honestly; transaction map has commit points & failure timelines; invariants I02/I03/I04/I08 have oracle + counterexample; fixtures (a)–(h) present and internally consistent (expected counts follow from given/events); schemas pass metaschema; fixture targets validate; ingest negatives rejected — run these checks yourself.
6. Cross-package consistency: PC02's entity names vs PC01's data_owner_of; PC01 operation names vs PC02 transaction map references; ID conventions (baseline §3) obeyed; language rule; header fields per baseline §3 present in every contract file; no file asserts a claim above DRAFT_FOR_REVIEW; no "TBD" numbers; nothing labelled CLOSED/ACCEPTED.
7. Evidence honesty: handoff EV records have commands/exit codes; anything claimed PASS that you can re-run, re-run.

## Report (AUDIT_REPORT → the path above)
Sections: frozen ref + epoch + manifest hash (recompute per protocol §6 algorithm `sha256-path-role-hash-bytes-v1`, show the value); reviewer identity + independence declaration; scope checked / excluded; evidence records (commands, exit codes); findings table: `F-A1R1-nn`, severity (`CRITICAL | MAJOR | MINOR`), file/ref, condition, expected vs observed, impact, remediation constraint (what must be true, not a patch); verdict per package (`PASS | FAIL | BLOCKED | STALE`) and overall; limitations; completion ceiling statement. Findings are OPEN; you do not close them.

Return to the Coordinator ONLY: overall verdict, per-package verdict, count of findings by severity, the five most important findings in one line each, and the report path (under 30 lines).
