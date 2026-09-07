# OWNER_DECISION record — 2026-09-08 (ninth round)

- decision_id: `OD-20260908-09`
- issuer: Owner (session user), via AskUserQuestion.
- evidence_ref: Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08.
- authority created: `AUTH-OWNER-20260908-10` — parent of the scoped Phase 5 dispatch.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | Phase 5 (Telegram) scope, given `CR-PC07-04` stays `PARTIALLY_RESOLVED` (2/5 facts — max message length, send rate limit; `callback_data` length/parse-mode escaping/buttons-per-row genuinely blocked on a fetch-tool page-size limitation, not a policy gap) | **Start with plain text now, add formatting later** | Phase 5 cards (`TC-telegram-linking-auth` → `TC-saved-snapshot` → `TC-telegram-unknown-delivery`) are authorised to start, scoped to plain-text messages only: message splitting (4096-char limit) and send-rate throttling using the two resolved facts. No `parse_mode` (Markdown/HTML), no inline keyboards, no callback_data-bearing buttons — those three code paths stay unimplemented (not stubbed-and-hidden; explicitly out of scope, `SG-01`-guarded) until the remaining three facts resolve. |

Not decided in this round: how the three remaining Telegram facts eventually get resolved (tool amendment for paginated fetch, or Owner reading the page directly) — deferred to a later round.
