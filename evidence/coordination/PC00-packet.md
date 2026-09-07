# TASK_PACKET PKT-PC00 — Khóa nguồn, nguyên tử hóa yêu cầu và xử lý mâu thuẫn

- packet_id: `PKT-PC00` · assignee_role: Worker · assignee_principal: `worker-W1`
- authority_id: `AUTH-COORD-PC00` (parent `AUTH-OWNER-20260906-01`) · lease_id: `LEASE-PC00-e1` (exclusive, fencing 1)
- created_at: 2026-09-06T16:55Z · expires_at: 2026-09-07T00:00Z (check `date -u` before every write)
- enforcement_mode: DOCUMENTARY_DRAFT · audit_route: INDEPENDENT_REQUIRED (A1 audits after freeze) · completion_ceiling: DRAFT_FOR_REVIEW
- scratch dir for helper scripts: `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w1/` (create it; nothing else under /tmp)

## Goal
Execute plan §11 **PC00** in full: immutable source baseline, atomic requirement registry, blocker register B01–B17 with provisional resolutions, amendments with before/after and oracle changes, ADRs, and a draft OWNER_DECISION_REQUEST bundling every decision the Owner must ratify.

## Non-goals
No contracts/schemas (PC01+). No stack choice beyond recording it as PROVISIONAL. Do not close any blocker. Do not rewrite the spec.

## Read set
- `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/packets/00-coordination-baseline.md` (this session's rules — binding)
- SRC-PLAN, SRC-SPEC (hashes in baseline §2) — read completely
- `/mnt/virtual/repo/xcrawl/agent_profile/worker.md`, `protocol.md`, `registry.json`

## Write targets (all CREATE, baseline ABSENT; no other path)
| Path | Content |
| --- | --- |
| `precode/baseline.json` | source refs (repo path + registry path), sha256, bytes, read date, plan/spec versions, ID conventions summary, session mode, claim ceiling |
| `precode/source/spec-v0.2.md` | byte-identical copy of SRC-SPEC (`cp`, then verify sha256 equals `d35e1f2d…`) |
| `precode/source/pre-code-plan-v0.1.md` | byte-identical copy of SRC-PLAN (verify sha256) |
| `precode/requirements.csv` | atomic registry; columns exactly: `req_id,source_anchor,text_vi,status,priority,scope,category,blocked_by,impacted_packages,notes` |
| `precode/decision-register.md` | B01–B17 register + amendments + provisional decisions + open questions |
| `precode/adr/README.md` | ADR index + template |
| `precode/adr/ADR-0001-*.md` … | one ADR per structural decision (see below) |
| `precode/owner-decision-request.md` | draft OWNER_DECISION_REQUEST |
| `evidence/handoffs/PC00-handoff.md` | HANDOFF (baseline §4) |

Directory-scoped grant: `precode/adr/` (list every file in handoff). Create parent directories as needed (`precode/`, `precode/source/`, `precode/adr/`, `evidence/handoffs/`).

## Checklist (plan PC00, each must be DONE or explained)
1. [ ] Baseline: `precode/baseline.json` + immutable copies with hash verification. Assign a **source anchor** to every §/D/AC/A/OQ of the spec and every §/B/I/error/SC/gate of the plan (a table in baseline.json or referenced from requirements.csv).
2. [ ] Requirements registry: one row per atomic requirement using the ID forms in baseline §3. Cover: all D-rows (incl. C03/D-tag), AC-01..18, P0-01..12, P1/OOS rows, A1..A7, OQ01..10, plus atomic prose requirements from spec §4 (per-screen rows), §5, §6.4, §7.3, §8.1–8.3, §9.2–9.3, §10, §11, §13.2. Status column = XN/UQ/ĐX/KC as the spec states (P0 items inherit XN unless the row says otherwise; prose items: derive and justify in notes). `blocked_by` lists B-IDs. `impacted_packages` lists PC IDs. Expect roughly 150–250 rows; do not pad.
3. [ ] Blocker register: for each B01–B17: source conflict quoted (both sides), recommendation (from baseline §5), status `PROVISIONAL`, decision_owner `Owner`, impacted contracts/files, gates blocked, oracle change, and what remains blocked if the Owner rejects.
4. [ ] Amendments AMD-B01, AMD-B02, AMD-B03, AMD-B05, AMD-B10, AMD-B11 (+ any other you find necessary, e.g. spec §6.2 edge COL→AW removal under B12, D58 backup): each with before (quoted), after (proposed text), why, replacement guarantee, test/oracle that proves it, affected REQ IDs.
5. [ ] ADRs (status `proposed`, decision owner Owner unless purely technical → `provisional-accepted` with rationale): ADR-0001 topology & placement (B12), ADR-0002 run state model split (B02), ADR-0003 delivery unknown state (B03), ADR-0004 tag freeze point (B01), ADR-0005 backup method (B11), ADR-0006 stack option A (PROVISIONAL, Owner), ADR-0007 timezone handling (B08), ADR-0008 analysis key & generation (B07), ADR-0009 identity/alias/target union (B06/B15), ADR-0010 secret scoping & CLI isolation (B13). Use the standard ADR shape: context, decision, status, consequences, alternatives, source refs, requirement refs.
6. [ ] P0 items still ĐX explicitly listed (D09, D53 etc.) with "not promoted" statement.
7. [ ] `precode/owner-decision-request.md`: one section per decision (B01–B17, stack, timezone, OQ defaults): question, material reason, source refs, options with trade-offs, recommendation, blocked scope, safe scope that continues, requested authority. Mark as REQUEST, not grant.

## Invariants / forbidden effects
- Copies of sources must be byte-identical. No edits to the two source files or anything under `agent_profile/`.
- No requirement text invented; every row quotes or closely paraphrases the source and cites its anchor.
- CSV must parse (python csv module), UTF-8, quoted fields, no embedded newlines in `text_vi` (use `; `).

## Verification (record as EV-PC00-nn, SELF_VALIDATION)
- EV-01: sha256 of both copies equals sources.
- EV-02: CSV parse: row count, unique req_id, every `blocked_by` ∈ B01..B17, every `impacted_packages` ∈ PC00..PC10, every status ∈ {XN,UQ,ĐX,KC}.
- EV-03: coverage check: every D-ID in spec §3, AC-01..18, P0 1..12, A1..A7, OQ1..10 appears as a req_id (script the list and diff).
- EV-04: decision-register lists exactly B01..B17 once each, each with status PROVISIONAL; every AMD referenced exists.
- EV-05: every ADR file has the required sections; ADR index lists all.
Record exact commands, outputs (summarised), exit codes.

## Stop gates
Baseline §6. If the spec and plan disagree on a requirement's status, keep the spec's status and note the plan's view in `notes`; do not change it.
