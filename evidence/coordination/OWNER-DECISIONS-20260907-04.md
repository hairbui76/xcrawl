# OWNER_DECISION record — 2026-09-07 (fourth round)

- decision_id: `OD-20260907-04`
- issuer: Owner (session user), via AskUserQuestion interview on the two items left open by OD-20260907-03.
- evidence_ref: Claude Code session (Coordinator), 2026-09-07.
- authority created: `AUTH-OWNER-20260907-05` — parent of the REQ-A6 fact-finding packet and the probe-gate record.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | `contracts/ops/collector-probe.md` §6 items 2–4: per-run budget/stop conditions (§3/§4, PROVISIONAL 200 posts or 30 min, stop on challenge/block/rate-limit/session-expiry, never click verification); go/no-go criteria (§7); real-account risk (REQ-A7) | **Accept all three** | §6 items 1–4 now all satisfied (item 1/D09 was already ratified in OD-20260907-01). The probe's *live* execution remains physically gated on the Owner's own machine (Playwright install, hand-login to a project-only Chrome profile, filled `probe-config.json`, 4× owner_confirmations with an evidence_ref to this decision) — see `TC-x-feasibility-probe-handoff.md` §"Owner must do". No Worker may run it. |
| 2 | REQ-A6 (arXiv max request rate + identification requirement; OpenAlex rate limit + identification/mailto requirement) — four facts currently `PLACEHOLDER_KC` in `contracts/retry-policy.yaml`, needed before the connector card can leave DRAFT | **Let a Worker fetch the official docs** | One-off, narrowly-scoped network grant: a Worker may fetch *documentation pages only* under `arxiv.org` / `info.arxiv.org` and `openalex.org` / `docs.openalex.org` to read and quote the current rate-limit and identification policy. It may **not** call `export.arxiv.org` or `api.openalex.org` (or any other live endpoint) — reading docs only, no live API traffic. Each fact recorded with source URL, retrieval date and a short verbatim quote. |

Not decided in this round: none — this closes every item left open by OD-20260907-03.
