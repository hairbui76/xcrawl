# PKT-PC07-FIX-TELEGRAM — resolve CR-PC07-04 (Telegram Bot API format limits)

Dispatched to a new Worker (`worker-WT`), 2026-09-08. Authority `AUTH-COORD-TELEGRAM-FACTS` (parent `AUTH-OWNER-20260908-06`, see `packets/OWNER-DECISIONS-20260908-05.md` item 2). Lease `LEASE-PC07-TELEGRAM` on: `contracts/telegram/delivery.md` §3.4 only, `precode/decision-register.md`, `precode/change-control.md`, `precode/requirements.csv` (the CR-PC07-04-related row(s) only), `acceptance/traceability.csv` (matching row(s) only), plus a handoff at `evidence/handoffs/PC07-TELEGRAM-handoff.md`. No other file.

**Network grant — read this twice:** you may fetch documentation pages ONLY under `core.telegram.org` (specifically `core.telegram.org/bots/api`, the sendMessage/sendPhoto/answerCallbackQuery reference and the general Bots FAQ/rate-limit pages on the same host). You are FORBIDDEN from calling `api.telegram.org` (the live Bot API), using any bot token, or sending anything. Documentation pages only, via WebFetch, same as the REQ-A6 fact-finding round.

Resolve the five facts currently `KC` in `contracts/telegram/delivery.md` §3.4:
1. Maximum length of a single message (text).
2. Maximum length of `callback_data` (currently a PROVISIONAL 64-byte assumption baked into the id format `1:<ri>:<ii>:<lg>:<rv>` — check whether that assumption holds).
3. The parse mode and its exact escape-character table (Markdown, MarkdownV2, or HTML — pick or confirm one and lock its escape rules; do not blend two modes' rules).
4. Maximum inline-keyboard buttons per row and per keyboard.
5. Message-send rate limit (per chat and/or global) — note that Telegram's own `Retry-After` on a live 429 always wins over any number here; this fact is a planning ceiling, not an override.

Quote each verbatim with URL and retrieval date (2026-09-08). Update `contracts/telegram/delivery.md` §3.4 status off `KC` for all five rows, with citations. Update `precode/decision-register.md` and `precode/change-control.md` in their existing conventions (mirror the REQ-A6 amendment shape). Correct `precode/requirements.csv`/`acceptance/traceability.csv` rows tied to `CR-PC07-04` — note in your reply that `precode/review.md` currently records `CR-PC07-04` as `CLOSED_CLAIMED` but **not independently verified**; your fact-finding is what actually closes it for real, so the wording should reflect a genuine resolution, not just repeat the old self-claim.

Run `evidence/tools/e0_check.py` read-only. If any fact isn't findable on the allowed host after a reasonable search, report BLOCKED for that fact specifically — do not guess, do not fall back to general knowledge of the Bot API.

Reply ONLY: status, the five resolved facts with citations (one line each), files changed + hashes, e0 result, handoff path (≤20 lines).
