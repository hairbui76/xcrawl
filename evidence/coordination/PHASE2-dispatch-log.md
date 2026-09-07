# Phase 2 dispatch log — reconstructed 2026-09-08

Coordinator note (in response to `CR-PC00-30`): under `PROV-PC00-08`, Phase 2 packets were sent as `SendMessage` text directly to already-running Worker agents rather than written to the scratchpad first, unlike every Phase 0/1 round. This is a genuine process gap flagged by W1n's packaging pass — the authority chain was auditable down to the Owner decision records and to what Workers quoted back in their handoffs, but not to packet text. This file reconstructs, verbatim, every dispatch packet sent this phase, in chronological order, closing that gap. Each block below is the exact message text sent; nothing has been altered or improved with hindsight.

---

## PKT-TC-RESEARCH (initial connector card dispatch, to worker-WN)

You are Worker principal `worker-WN` under the Research Radar agent_profile protocol: the only role that writes files; no subagents; self-validation only; stop at stop conditions instead of improvising. Dispatched by the Coordinator at 2026-09-07 ~13:05Z to execute task card **`agent-tasks/TC-research-connector-metadata.md`** (Phase 2B, M2 paper connector). Lease LEASE-TC-RESEARCH-e1 (exclusive on the card's §3 write set + migration if any + handoff + evidence manifest), authority AUTH-COORD-TC-RESEARCH (parent AUTH-OWNER-20260907-04; record packets/OWNER-DECISIONS-20260907-03.md), expires 2026-09-08T20:00Z, completion ceiling IMPLEMENTATION_VERIFIED (E1 with recorded fixtures; E3 live calls are NOT permitted here).

WAIT GATE first: the card is being written right now by worker-WP (PKT-PC10-FIX20). Poll until both exist: the file agent-tasks/TC-research-connector-metadata.md AND an addendum "PKT-PC10-FIX20" with a released-lease timestamp in evidence/handoffs/PC10-handoff.md (sleep 60, up to 60 min). Meanwhile read (read-only): the coordination baseline and Phase-1 dispatch template packets; agent_profile/worker.md; root README.md and the Phase 1 card handoffs; contracts/ops/collector-probe.md §9 (connector rules), contracts/ops/internet-boundary.md, contracts/retry-policy.yaml `research_connector_rate_limit` (four PLACEHOLDER_KC nulls — binding: the connector reads rate/identity settings from configuration and REFUSES to run when any is null; you may not guess a number; tests use explicit test values), contracts/ports.yaml research.* ops, contracts/http/openapi.yaml, contracts/errors.yaml (SOURCE_METADATA_UNAVAILABLE, RATE_LIMITED, CAPABILITY_DENIED), contracts/data/entities.yaml (work, work_version, source_fetch_log), acceptance/fixtures/identity/{b,g,h}-*.json and collection/h-metadata-unavailable-post-only.json. When the card lands, its §1–§13 are your requirements; follow its §3 write set exactly.

Implementation notes: arXiv and OpenAlex clients behind an `httpx` transport that tests replace with recorded responses (write the recorded fixtures yourself, clearly synthetic, under the card's test paths); strict allowlisted hosts (no redirects to private ranges — reuse/mirror internet-boundary.md rules); DOI/arXiv normalisation via `server.app.identity.normalization`; provenance and `source_fetch_log` rows; degraded path → post-only item with SOURCE_METADATA_UNAVAILABLE, never a guessed DOI; connector health op. Network only for uv installs; no live arXiv/OpenAlex calls; no git mutation; PYTHONDONTWRITEBYTECODE=1; scratch under the scratchpad `wn/` dir.

When done: HANDOFF at evidence/handoffs/TC-research-connector-metadata-handoff.md and manifest evidence/runs/TC-research-connector-metadata-E1-<UTC>.json (validate). Reply ONLY: status, files created, tests run (counts, command), evidence manifest path, CRs (≤25 lines).

---

## Owner interview (AskUserQuestion, closing OD-20260907-03's two open items → OD-20260907-04)

Q1 "Probe gate (collector-probe.md §6): do you accept the per-run budget and stop conditions (§3/§4: PROVISIONAL 200 posts or 30 min per run, stop on challenge/block/rate-limit/session expiry, never click verification), the go/no-go criteria (§7) as the criteria you will accept for the conclusion, and that the probe runs on your real X account with an unverifiable risk of account restriction (REQ-A7)?" → answered "Accept all three (items 2, 3, 4)".

Q2 "REQ-A6: the connector needs four facts from official documentation (arXiv max request rate and identification requirement; OpenAlex rate limit and identification/mailto requirement). Workers have no network by rule. How should these be obtained?" → answered "Let a Worker fetch the official docs (Recommended)".

Both recorded verbatim in `packets/OWNER-DECISIONS-20260907-04.md` (already persisted).

---

## PKT-TC-IDENTITY-FIX2 (to worker-WM)

PKT-TC-IDENTITY-FIX2 — small scoped fix, your card's write set only. New authority `AUTH-COORD-TC-IDENTITY-FIX2` (parent `AUTH-OWNER-20260907-04`), lease `LEASE-TC-IDENTITY-e2` on `tests/integration/test_identity_merge_audit.py` only. Completion ceiling stays `IMPLEMENTATION_VERIFIED` (no claim change).

Context: a new Phase-2B migration `server/migrations/versions/0005_tc_research_connector_metadata.py` now exists (written by another card, outside your lease). Reported as `CR-TC-research-01` by that card's worker: your test at `tests/integration/test_identity_merge_audit.py:1502` hard-codes the single-head literal `"0004_merge_phase1_heads"`, which is now wrong once `0005_…` lands — it will fail the full suite for everyone, not just you.

Fix: replace the hard-coded literal comparison with a structural assertion — get the Alembic script directory's heads (however your existing test already obtains them) and assert `len(heads) == 1`, without asserting *which* revision id is the head (that will keep changing as more migrations land; that's expected and correct). Do not touch anything else in the file. Re-run this test file plus the full suite to confirm 0 failures (some other in-flight file may still be red from a different card — if so, name it, don't fix it).

Lease-release your handoff addendum to `evidence/handoffs/TC-canonical-identity-merge-handoff.md` (file hash before/after, test result). Reply ONLY: status, hash before/after, full-suite result (pass/fail/xfail counts), any file still failing that isn't yours (≤10 lines).

---

## PKT-PC00-FIX21 (to worker-W1n)

PKT-PC00-FIX21 — record the fourth Owner decision round. New authority `AUTH-OWNER-20260907-05` (parent of the REQ-A6 fact-finding packet and the probe-gate closure). Lease `LEASE-PC00-e22` on your usual PC00 write set (`precode/owner-decisions.md`, `precode/decision-register.md`, `precode/baseline.json`, `precode/owner-decision-request.md`, `agent_profile/registry.json`) + CREATE `precode/owner-decisions-04.md`.

Source: `packets/OWNER-DECISIONS-20260907-04.md` (read it — full text of the two items and the Owner's answers). Summary: (1) `collector-probe.md` §6 items 2–4 all **accepted** — the probe gate is now administratively fully open (item 1/D09 was already ratified in OD-20260907-01); live execution still requires the Owner's own machine and is not something any Worker may do. (2) REQ-A6 — Owner authorised a Worker to fetch official arXiv/OpenAlex **documentation pages only** (no live API calls) to resolve the four `PLACEHOLDER_KC` facts in `contracts/retry-policy.yaml`; that fact-finding packet is running in parallel as a new worker (not gated on this one).

Record: `precode/owner-decisions-04.md` (same format as your prior rounds) citing `OD-20260907-04`; decision-register rows for the probe-gate item (§6 items 2-4 → closed/answered, cite OD-20260907-04) and REQ-A6 (status stays open until the fact-finding worker lands the numbers — do NOT mark REQ-A6 resolved yet, just note the authorization); registry.json gets `AUTH-OWNER-20260907-05`. Run e0 read-only before releasing.

Reply ONLY: status, files touched + hashes, e0 result (≤12 lines).

---

## PKT-PC03-FIX-REQA6 (to new worker-WF, first spawn)

You are Worker principal `worker-WF` under the Research Radar agent_profile protocol (Coordinator/Worker/Auditor; see agent_profile/worker.md and protocol.md — read them first). You write files under an exclusive message-tracked lease with an exact write set; you never edit outside it; you self-validate and report, you never claim more than SELF_VALIDATION.

Task: **PKT-PC03-FIX-REQA6** — resolve REQ-A6 (the last KC fact-gap blocking the M2 paper-connector contract). Authority `AUTH-COORD-REQA6` (parent `AUTH-OWNER-20260907-05`, see `packets/OWNER-DECISIONS-20260907-04.md` item 2 — read it first, it is your authorization). Lease `LEASE-PC03-REQA6` on: `contracts/retry-policy.yaml`, `precode/decision-register.md`, `precode/change-control.md`, plus a handoff at `evidence/handoffs/PC03-REQA6-handoff.md`. No other file. Completion ceiling: your part is a contract/documentation change, so it stays `ACCEPTED`/`PROVISIONAL`-cleared per the repo's existing decision-register convention — do not touch code.

**Critically important boundary — read this twice:** You have ONE narrow network grant, explicitly authorised by the Owner for this task only: fetch **documentation pages** (read-only, GET requests to human-readable doc/help pages) under these hosts ONLY: `arxiv.org`, `info.arxiv.org` (arXiv's API Terms of Use / user manual pages); `openalex.org`, `docs.openalex.org` (OpenAlex's rate-limit / authentication / polite-pool documentation). You are FORBIDDEN from: calling `export.arxiv.org` (the actual arXiv API), calling `api.openalex.org` (the actual OpenAlex API), fetching any other host, or making any request that looks like a real data query rather than reading a documentation page. Use the WebFetch tool for this (not curl/Bash network calls).

Read first (read-only, no lease needed): `contracts/retry-policy.yaml` (the `research_connector_rate_limit` block); `precode/decision-register.md` (the REQ-A6 row); `precode/change-control.md` (the format every prior amendment entry uses); `agent-tasks/TC-research-connector-metadata.md` §10 SG-A6.

Do: (1) fetch arXiv's official rate-limit/identification documentation, quote verbatim with URL + retrieval date 2026-09-07; (2) fetch OpenAlex's official rate-limit/identification documentation, same; (3) fill the four `PLACEHOLDER_KC` values in retry-policy.yaml with a citation block, flip status if all four resolved, bump version; (4) update the decision-register REQ-A6 row to RESOLVED, decision_ref OD-20260907-04, cite URLs + date; (5) add a change-control.md entry; (6) run e0_check.py read-only.

If you cannot find an authoritative statement on the allowed hosts after a reasonable search (2-3 fetches per source), report BLOCKED — do not guess.

Reply ONLY: status (DONE | DONE_WITH_CONCERNS | BLOCKED), the four resolved values with citations, files changed + hashes, e0 result, handoff path (≤20 lines).

---

## PKT-PC03-FIX-REQA6-part2 (to worker-WF, continuation)

PKT-PC03-FIX-REQA6-part2 — continuation, same lease reopened (`LEASE-PC03-REQA6-p2`) on the same three files plus your existing handoff. Authority: the Owner just answered "Add help.openalex.org to the allowlist" when told `docs.openalex.org` redirects there and is outside your original grant.

**Updated network grant** (replaces the old one, same restriction otherwise): you may now also fetch documentation pages under `help.openalex.org`. Still forbidden: `api.openalex.org`, `export.arxiv.org`, or any live-query-shaped endpoint.

Do: (1) fetch OpenAlex's rate-limit and identification/mailto documentation from `help.openalex.org`, quote verbatim with URL + date; (2) finish retry-policy.yaml with the resolved OpenAlex values, flip status off PLACEHOLDER_KC, bump version 0.7.0→0.8.0; (3) update decision-register §8.13 to RESOLVED (both halves), change-control.md additive entry; (4) re-run e0_check.py.

If help.openalex.org also redirects outside the now-four-host list, or no authoritative number is found after 2-3 tries, stop and report BLOCKED.

Reply ONLY: status, the two OpenAlex values + citation, files changed + hashes, e0 result, handoff addendum (≤15 lines).

---

## PKT-PC00-FIX22 (to worker-W1n)

PKT-PC00-FIX22 — Coordinator ruling on the item W3n correctly declined to resolve on their own authority. Lease `LEASE-PC00-e23` on `precode/decision-register.md` §3 only.

**Ruling:** `research-radar-spec.md` line 101 states OpenAlex requires a contact email as part of REQ-D34's premise. Now known factually superseded by the officially documented policy read 2026-09-07. **The spec file itself is never edited** — this is a documented correction of understanding, not a spec amendment in the sense of changing spec content.

Record a new entry `AMD-SPEC-D34-01` in decision-register.md §3: spec ref `research-radar-spec.md:101` (REQ-D34); nature: factual premise superseded by documentation, not a spec defect requiring a rewrite; evidence citations; effect: requirements.csv/traceability.csv already carry this correction in their notes (done by W3n) — this entry is the canonical record they point back to. State explicitly the spec text stands unedited.

Run e0 read-only. Reply ONLY: status, hash before/after, e0 result (≤8 lines).

---

## PKT-PC02-FIX15 (to worker-W3n)

PKT-PC02-FIX15 — CR-PC02-23, your own flag from the last packet. Lease `LEASE-PC02-e17` on `precode/requirements.csv` (rows REQ-D34 and REQ-S13.2-01 only) + `acceptance/traceability.csv` (the REQ-A6 row only). Authority `AUTH-COORD-PC02-FIX15` (parent `AUTH-OWNER-20260907-05`).

Context: REQ-A6 is fully RESOLVED. The resolved facts show OpenAlex's current documentation carries no mailto/polite-pool/User-Agent identification requirement — this may contradict REQ-D34 and REQ-S13.2-01 if they claim OpenAlex requires a contact email.

Do NOT just flip status the way you did for REQ-A6 — read each row's actual text first. If a row's core requirement doesn't depend on the false premise, correct the factual claim in place and add a note citing §8.13.2 and the retrieval date, keeping status/priority as your judgment says correct. If a row's entire justification was the mailto requirement and nothing else, say so plainly rather than silently resolving it. Also sync traceability.csv's REQ-A6 row status to match requirements.csv.

Reply ONLY: status, each row's before/after text (or a flag for Coordinator), hash before/after per file (≤20 lines).

*(Two follow-up messages to the same worker, same day: one to sync `traceability.csv`'s REQ-D34/REQ-S13.2-01 rows to `XN` once the requirements.csv rows landed; content was the same shape as above, addressed to the two remaining out-of-step rows.)*

---

## PKT-PC00-FIX23 (to worker-W1n)

PKT-PC00-FIX23 — fix your own CR-PC00-29 flag. Lease `LEASE-PC00-e24` on `precode/owner-decisions-04.md` §7 and the `baseline.json` OD-04 anchor entry only.

Both currently describe REQ-A6's OpenAlex half as unresolved/pending — stale since your own FIX21 predates WF's second pass. REQ-A6 is now fully RESOLVED (both halves). Update both spots to say so plainly, citing §8.13.2, correct attribution to OD-20260907-04. Don't touch anything else.

Run e0 read-only. Reply ONLY: status, hash before/after, e0 result (≤8 lines).

---

## PKT-PC05-PROBEGATE (to worker-WX, two rounds)

Small scoped packet outside your original card write set — new lease `LEASE-PC05-PROBEGATE` on `contracts/ops/collector-probe.md` only. Authority `AUTH-COORD-PROBEGATE` (parent `AUTH-OWNER-20260907-05`).

Task: update §6 (the Owner gate list) to record that items 1–4 are now all satisfied — item 1 (D09) already ratified in OD-20260907-01; items 2–4 accepted via OD-20260907-04. Add one clear sentence stating the gate being administratively closed does not mean any Worker or automated process may run the probe — live execution happens only on the Owner's own machine.

*(Second round, `LEASE-PC05-PROBEGATE-2`, `CR-TC-research-06`): §9.2 still lists all five REQ-A6 rows as `KC` — update to reflect resolved facts, citing retry-policy.yaml 0.8.0 and decision-register §8.13.2 rather than forking a second copy of the numbers.)*

Bump version per the file's own convention; run e0 read-only. Reply ONLY: status, hash before/after, e0 result (≤8 lines).

*(A third quick follow-up bumped `probe/x_feasibility/__init__.py`'s `PROTOCOL_VERSION` string to match.)*

---

## PKT-TC-RESEARCH-2 (to worker-WN, continuation)

Follow-up packet, same lease shape reopened on your card's write set (`LEASE-TC-RESEARCH-e2`) — `server/app/research/*.py`, your two test files, and your handoff addendum.

Context: REQ-A6 is now fully RESOLVED. Do: (1) update `ConnectorSettings` so shipped defaults come from the resolved contract values instead of `null` — the connector should now activate out of the box; (2) re-run/extend tests to demonstrate activation with contract-derived defaults, still against recorded/synthetic httpx fixtures, no live calls, plus a regression that an explicit null/invalid config still refuses; (3) if `SG-IDENT` currently hard-requires a mailto/User-Agent and would now behave incorrectly, report as a CR rather than guess; (4) update handoff, full suite must stay green.

Reply ONLY: status, files changed + hashes, test results, whether scope-level blockers are clear, handoff path (≤15 lines).

---

## PKT-PC10-FIX21 (to worker-WP)

PKT-PC10-FIX21 — combined packet. New lease `LEASE-PC10-e22` on: `agent-tasks/TC-x-feasibility-probe.md` (one wording fix) + all 19 cards' §0 pin blocks + README/TEMPLATE/WALKTHROUGH epoch references.

Context: retry-policy.yaml and collector-probe.md both moved multiple times; connector code + tests changed; several precode/ files moved (multiple Owner-decision recording packets).

Wording fix first: `TC-x-feasibility-probe.md` line ~28 still says §6 items 2–4 are unanswered — false now. Update to say answered/accepted with the same administrative-only caveat. Then: full re-pin, one epoch (`PC10-PIN-P2b-20260907`), across all 19 cards. Update README/TEMPLATE/WALKTHROUGH. Run verify_cards + generator verifier + self-test.

Reply ONLY: status, wording-fix hash before/after, new epoch id, verify_cards result, self-test result, any CR (≤15 lines).

---

## PKT-PC10-FIX22 (to worker-WP)

PKT-PC10-FIX22 — fix your own CR-PC10-14 (blocking). New lease `LEASE-PC10-e23` on `agent-tasks/TC-research-connector-metadata.md` §9/§10/front-matter only.

Fix: §10 `SG-A6` currently says the four REQ-A6 values are null and the connector must refuse — false now; rewrite to state the actual current stop condition (refuses only on explicit null/invalid config, regression-tested). `SG-IDENT` currently calls the OpenAlex contact-identity fact `KC` — also false; state resolved (no source requires identification; default `False`, contract-derived, mechanism retained). Update §9/claim-ceiling rationale to cite the real current blockers (no API host in contract = SG-DOC; E3 forbidden = SG-LIVE) instead of stale PLACEHOLDER_KC.

Run verify_cards + self-test again. Reply ONLY: status, hash before/after, verify_cards result, self-test result (≤10 lines).

---

## PKT-PC10-FIX23 (to worker-WP)

PKT-PC10-FIX23 — one more re-pin, and this is the last one: precode/ freeze declared (CR-PC10-15 accepted). `precode/baseline.json` moved again after your P2c pin, staling all 19 cards on that one file. New lease `LEASE-PC10-e24` on the same re-pin write set.

Re-pin all 19 cards under a new epoch (`PC10-PIN-P2d-20260907`), update README/TEMPLATE/WALKTHROUGH/precode/README.md, run verify_cards + generator verifier + self-test, confirm 0 violations, confirm no file touched outside the re-pin write set.

Reply ONLY: status, new epoch id, verify_cards result, self-test result, confirmation of write-set-only scope (≤10 lines).

---

## PKT-PC09-P2 (to worker-W6n)

PKT-PC09-P2 — register Phase 2 (FC-P2) into the evidence/gates/traceability system. Lease `LEASE-PC09-e2` on `evidence/index.json`, `precode/gates.yaml`, `acceptance/traceability.csv`, `precode/review.md`, `evidence/tools/e0_check.py` if needed, + handoff. Authority `AUTH-COORD-PC09-P2` (parent `AUTH-OWNER-20260907-05`).

Frozen candidate FC-P2 (manifest `dafc1c83ca2108d50ccc5cc700115849b9537be31ff0155f5dd37c7bc5e469f0`, 466 entries). Independent audit A3-P2-R1: overall PASS, 2 new LOW. Rulings on both disclosed (PARKED, non-blocking).

Do: register new evidence (both card manifests + regenerated E1 record); add the A3-P2-R1 INDEPENDENT_AUDIT record (claim-cap rule: caps at IMPLEMENTATION_VERIFIED); update gates.yaml (probe gate administratively open but not MET — no evidence exists); regenerate review.md Phase 2 section with real numbers; run e0.

Reply ONLY: status, files touched + hashes, e0 result, new index.json record count, gates.yaml deltas, review.md regenerated (y/n), any CR (≤20 lines).

---

## PKT-PC09-P2-FIX1 (to worker-W6n)

PKT-PC09-P2-FIX1 — close your own CR-PC09-20, the one you flagged as biggest concern. Expanded lease `LEASE-PC09-e3` adding `acceptance/scenarios.yaml` (the specific SC rows the three Phase-2 cards claim, only).

Task: find the 13 scenarios the three cards claim, determine honestly whether the card's actual tests exercise each (PASS-E1, PASS-E2, or NOT_RUN — don't upgrade anything the evidence doesn't support). Update scenarios.yaml's status for exactly those 13 rows, update G6-X1's count in gates.yaml, reflect corrected numbers in review.md. Also resolve CR-PC09-19/-21 if in scope.

Reply ONLY: status, the 13 scenarios' new statuses, gates.yaml/review.md deltas, hashes, e0 result, remaining CRs (≤20 lines).

---

## PKT-PC00-FIX24 (to worker-W1n)

PKT-PC00-FIX24 — final Phase 2 packaging. Lease `LEASE-PC00-e25` on `evidence/audits/` and `evidence/coordination/` only.

Persist from the scratchpad: A3-P2-R1-report.md (resolves CR-PC09-18); FC-P2-manifest.txt; OWNER-DECISIONS-20260907-04.md; every dispatch packet pertaining to this Phase-2 round. Same directory convention as the Phase-0/1 packaging round.

Reply ONLY: status, count of files persisted + where, any hash mismatch found, any CR (≤10 lines).
