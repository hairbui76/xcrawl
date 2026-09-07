# OWNER_DECISION record — 2026-09-07 (ratification interview)

- decision_id: `OD-20260907-01`
- issuer: Owner (the user of this Claude Code session), interviewed by the Coordinator question by question
- evidence_ref: Claude Code session `session_017QmDJtMqD9o1z79waqSB9W`, 2026-09-07 (answers captured via structured prompts; transcript retained by the platform)
- authority created: `AUTH-OWNER-20260907-02` — ratifies the items below; converts the corresponding PROVISIONAL decisions into ACCEPTED amendments/ADRs; parent of any Worker packet that records them.
- scope not decided: REQ-OQ03 (provider/model) stays `OWNER_DECISION_REQUIRED`; M3 remains blocked. Everything marked KC stays KC (no runtime evidence was produced by this interview).

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | B12 / D09 Chrome profile | **Dedicated project profile** | D09 ĐX → XN; REQ-OQ01 answered; M0/SP1 no longer blocked on this decision (probe still NOT_RUN) |
| 2 | B12 topology | **Remove the direct collector→analysis edge** | AMD-B12 ACCEPTED; D08/D42/D50 ĐX → XN; ADR-0001 accepted |
| 3 | Stack (REQ-OQ02) | **B — Python workers + TypeScript web** | ADR-0006 rewritten: decision = B (supersedes the proposed A), status accepted; all 18 task cards' §3 paths and §8 build/test commands must be rewritten for B; contracts unchanged |
| 4 | B08 timezone | **(a) one IANA timezone; value `Asia/Ho_Chi_Minh` confirmed** | AMD-B08 ACCEPTED; ADR-0007 accepted; schedule fixtures stand |
| 5 | B01 | (a) freeze at publish | AMD-B01 ACCEPTED; ADR-0004 accepted |
| 6 | B02 | (a) four fields, delivery separate | AMD-B02 ACCEPTED (incl. AC-03 wording); ADR-0002 accepted |
| 7 | B03 | (a) delivery.unknown, no auto-retry | AMD-B03 ACCEPTED (AC-14 wording); ADR-0003 accepted |
| 8 | B04 | (a) separate coverage/pending/backfill ledgers | AMD-B04 ACCEPTED |
| 9 | B05 | (a) no duplicate ingest by post ID | AMD-B05 ACCEPTED (AC-04 wording) |
| 10 | B06 | (a) alias + versions + target union | data model addition ACCEPTED; ADR-0009 accepted |
| 11 | B07 | (a) analysis key + generation | AMD-B07 ACCEPTED; ADR-0008 accepted |
| 12 | B09 | (a) narrow link-code exception | AMD-B09 ACCEPTED |
| 13 | B10 | (a) app-only resume, 3 commands, unlink in app | AMD-B10 ACCEPTED; F-PC00-01 confirmed |
| 14 | B11 | (a) consistent snapshot + manifest + restore drill | AMD-B11 ACCEPTED (D58 wording); ADR-0005 accepted; RPO/RTO per item 20 |
| 15 | B13 | (a) scoped secrets, CLI tools disabled, disabled-until-verified | ADR-0010 accepted; AC-16 stays BLOCKED until a probe passes |
| 16 | B14 | (a) insufficient_evidence | ACCEPTED; D53 stays ĐX-in-P0 only regarding parameter calibration (A4) |
| 17 | B15 | (a) scoped metric + conflict count | AMD-B15 ACCEPTED |
| 18 | B16 | (a) three statement kinds + comparator unknown | AMD-B16 ACCEPTED (AC-11 wording) |
| 19 | B17 | (a) selected items only, partial with pending list | AMD-B17 ACCEPTED |
| 20 | OQ defaults | **accept all**: N=7 days; 200 posts or 30 min; 08:00/20:00 local; no quiet hours; threshold/model unset until measured; Saved export deferred to P1 (F-PC00-02 confirmed) | values stay PROVISIONAL-by-nature where measurement is required (OQ05 after M0, OQ08 after M3, OQ09 after A3) but are Owner-accepted as working values |
| 21 | REQ-OQ03 provider/model | **decide later** | stays OWNER_DECISION_REQUIRED; blocks M3 only |
| 22 | PC04 parameters (8) + empty period | **accept all + option (b)** | PROV-PC04-01..09 → Owner-accepted working values; threshold remains `uncalibrated` until A2 |
| 23 | PC08 parameters | **accept all** (RPO 24 h, RTO 2 h, backup 03:00, 14d+8w+monthly, Argon2id, 12 h idle / 30 d absolute, 5/15 min lockout, token 180 d, audit 365 d, deletions forever) | PROV-PC08-01..05 → Owner-accepted |
| 24 | data.purge_all scope | **(a) research data only**; keep login, secrets, Telegram link, provider config, schedule; **backups are NOT deleted** | PROV-PC00-01 / PROV-PC01-03 resolved; TXN-purge-all exclusion list = the kept set; MOD-data-admin-service unblocked |
| 25 | Technical changes | **accept both** (CSRF_REJECTED code; resume-from-blocked with mandatory reason) | PROV-PC00-02/-04 accepted |

Status vocabulary from now on: a ratified item is `ACCEPTED (OD-20260907-01)`; blockers B01–B17 move from `PROVISIONAL` to `RATIFIED` in the decision register and the registry's `open_product_blockers` becomes empty with a `ratified_product_blockers` list citing the evidence ref. Contract `claim_ceiling` may be raised to `CONTRACT_READY` only in the four scopes A2-R4 named eligible (boundaries and rights; data and identity; workflow and state; reporting and time) and only for files whose remaining dependencies are not KC.
