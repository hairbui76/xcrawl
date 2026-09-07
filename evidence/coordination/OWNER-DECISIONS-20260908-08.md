# OWNER_DECISION record — 2026-09-08 (eighth round)

- decision_id: `OD-20260908-08`
- issuer: Owner (session user), via AskUserQuestion, reviewing the Worker-prepared REQ-A5 summary (Anthropic Commercial ToS eff. 2025-06-17, Usage Policy eff. 2025-09-15, Service Specific Terms eff. 2026-06-08 — full citations in `precode/owner-decisions-06.md` §3) presented directly in this session.
- evidence_ref: Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08.
- authority created: `AUTH-OWNER-20260908-09`.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | `REQ-A5` sign-off for Anthropic (Claude Sonnet 5 / Claude Opus 5, `api_key` family) | **Yes, sign off** — explicitly accepting the `TC-A5-01` input-rights warranty (the Owner, not Anthropic, is representing that this system has the right to submit third-party research text — arXiv/OpenAlex abstracts and similar — as Input) | `contracts/ai/providers.yaml` §5's `reviewer = Owner` convention is now satisfied for Anthropic specifically, this exact read (the three dated pages above). `CR-PC06-OQ03-02` closes. This does **not** set `enabled = true` on either adapter — that remains gated on `B13` isolation verification (`ISO-03`/`ISO-05` unverified, `E3 NOT_RUN`), unrelated to this sign-off. The conclusion expires if any of the three cited pages changes version (per `ADR-0010`'s own rule, already recorded by the Worker). |

Not decided in this round: whether arXiv/OpenAlex/X's own policies permit this system reprocessing their content this way (`TC-A5-01`'s underlying question, distinct from Anthropic's terms) — flagged by the Worker as a separate, unanswered question, not resolved by this sign-off.
