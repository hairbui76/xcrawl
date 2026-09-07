# OWNER_DECISION record — 2026-09-08 (fifth round)

- decision_id: `OD-20260908-05`
- issuer: Owner (session user), via AskUserQuestion interview following the Coordinator's "have you done everything?" status report.
- evidence_ref: Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08.
- authority created: `AUTH-OWNER-20260908-06` — parent of the Telegram fact-finding packet and Phase 5 card dispatch; also covers the REQ-OQ03 research task.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | `REQ-OQ03` (AI provider + specific model for bulk labeling vs. summary generation) — no safe default exists per `contracts/ai/providers.yaml`'s `no_vendor_claims` clause | **Research and recommend; Owner gives final approval** | Coordinator researches candidate providers against the technical requirements in `contracts/ai/tasks.yaml`/`providers.yaml` (JSON output, usage reporting, isolation, concurrency) and proposes a pick. This does **not** itself resolve `REQ-A5` (reading that specific provider's real terms before enabling) — a Worker still does that, separately, before any adapter is set `enabled = true`. `REQ-OQ03` stays `OWNER_DECISION_REQUIRED` until the Owner explicitly approves a specific recommendation. |
| 2 | `CR-PC07-04` (Telegram Bot API format limits — 5 facts, `contracts/telegram/delivery.md` §3.4, currently `KC`) | **Fetch docs now, start Phase 5 in parallel** | One-off, narrowly-scoped network grant: a Worker may fetch documentation pages only under `core.telegram.org` (specifically `core.telegram.org/bots/api`) to read and quote the current format limits. No live Bot API calls (no `api.telegram.org`), no bot token used, no message sent. Phase 5 (`TC-telegram-linking-auth` → `TC-saved-snapshot` → `TC-telegram-unknown-delivery`) is authorised to start once the five facts land. |

Not decided in this round: the actual REQ-OQ03 pick (pending the Coordinator's research and a follow-up Owner approval); REQ-A5 (per-provider terms reading, separate gate, per adapter, whenever one is proposed for enabling).
