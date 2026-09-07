# OWNER_DECISION record — 2026-09-08 (seventh round)

- decision_id: `OD-20260908-07`
- issuer: Owner (session user), via AskUserQuestion interview following the two-worker (WT/WAI) status report.
- evidence_ref: Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08.
- authority created: `AUTH-OWNER-20260908-08` — parent of the widened Telegram fact-finding retry.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | 3 remaining Telegram facts (`callback_data` length, parse-mode escape table, buttons per row/keyboard) blocked by a fetch-tool truncation on `core.telegram.org/bots/api`, not a scope problem | **Widen the grant: also allow a web search** (same docs-only rule otherwise — no live Bot API calls, no bot token, nothing sent) | The Worker may now use WebSearch (not just WebFetch on the four/five previously-named hosts) to find a way to reach the truncated sections of the same official page — e.g. a cached/archived copy of `core.telegram.org/bots/api` itself. The search query must stay about locating that page's content; it does not authorise fetching arbitrary other Telegram-adjacent sites for a *different* number. Still forbidden: `api.telegram.org`, any bot token, any message send. |
| 2 | `REQ-A5` reviewer per `contracts/ai/providers.yaml` §5 is meant to be the Owner personally, not a delegated Worker (`CR-PC06-OQ03-02`) | **Owner will review and sign off personally** | Coordinator presents the Worker's findings (citations, quotes, the two open conditions) directly to the Owner in this session for actual review and sign-off — see the follow-up in this same turn. Until the Owner explicitly signs off, `CR-PC06-OQ03-02` stays open and the reviewer field is not filled with a Worker's name. |

Not decided in this round: the actual REQ-A5 sign-off itself (asked as an immediate follow-up in the same turn, separately from this record).
