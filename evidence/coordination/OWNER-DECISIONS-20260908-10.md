# OWNER_DECISION record — 2026-09-08 (tenth round)

- decision_id: `OD-20260908-10` · issuer: Owner via AskUserQuestion after the Phase 3/5 commit `fb3944a` · evidence_ref: session `session_017CTbS7F4oTr4ZtFYkhdabD` · authority created: `AUTH-OWNER-20260908-11`.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | `CR-TC-SAVED-04` — saving a target that has no analysis yet (B16 forbids inventing summary lines; today refused with `VALIDATION_ERROR`, 0 rows) | **Allow the save; show a "not analysed yet" label** | `save.create` succeeds with the summary block explicitly marked missing (no invented text); a later analysis can be attached by reanalysis. Implemented by `TC-saved-snapshot` (W5B); the label wording is a fixed, non-inferential string; contract CR filed for the schema field that carries it if none exists. |
| 2 | `CR-TC-TGAUTH-02` — interim Save trigger from Telegram while the callback button is blocked (`CR-PC07-04`) | **Keep `/save <id>` as the plain-text trigger** | Stays until the inline button becomes possible; maps to the existing `CMD-save`; no new contract command. |
| 3 | `CR-TC-TGAUTH-04` — a **linked** chat sends text outside the three-command allowlist (sweep fixture: silence; `commands.yaml`: reminder) | **Short reminder of the three commands** (linked chats only; unknown chats stay silent, 0 outbound) | Code as shipped stands; the boundary-sweep fixture row is corrected in the next contract round (CR to PC08). |
