---
contract_id: CT-handoff-TC-tag-service
version: 1.0.0
status: draft
document_type: HANDOFF
card_ref: agent-tasks/TC-tag-service.md
packet_id: OD-20261017-12 item 6 (Owner go-ahead)
worker: claude-code session_01XQgXrAiGrnAUFS3jowQf2w
authority: AUTH-OWNER-20261017-13
owner_modules: [MOD-tag-service]
evidence_manifest_id: EVM-TC-tag-service
evidence_record: evidence/runs/TC-tag-service-E1-20261017T042623Z.json
pin_epoch: PC10-PIN-P7-20261017
claim_ceiling: DRAFT_FOR_REVIEW
---

# HANDOFF — `TC-tag-service` (card 21, `CR-P0-07`, `CR-TC-BACKFILL-07`)

## 1. Status

**DONE_WITH_CONCERNS**, `SELF_VALIDATION`. Eight `tag.*` operations, three new tables
(migration `0016`), six HTTP routes, and the two adapters that let `MOD-report-service` use the
real tag service. `app.state.report_context` is now wired: `GET /v1/reports` answers **200** on
a wired app instead of the `500` of `F-A3-P5-03`. **19 card tests** pass; the full suite, ruff,
`mypy --strict`, `e0` and `verify_cards` are clean.

The concerns are eight change requests (§4): the contracts disagree with each other in places a
tag service cannot resolve on its own, and the card records each choice rather than hiding it.

## 2. Write set, before → after

| Path | Before | After (sha256 · bytes) |
| --- | --- | --- |
| `server/migrations/versions/0016_tc_tag_service.py` | ABSENT | `b6c150a361fbde17…` · 4374 |
| `server/app/tags/service.py` | ABSENT | `84c2e923e173aff8…` · 53061 |
| `server/app/tags/router.py` | ABSENT | `680c2a54031bf7ec…` · 13324 |
| `server/app/main.py` | modified | `17e398296f776582…` · 16905 |
| `server/app/wiring.py` | modified | `e1c6ffda0559af14…` · 37508 |
| `server/app/settings.py` | modified | `98701f095b4577f7…` · 13370 |
| `server/tests/test_wiring.py` | modified | `1b5274128f58b9ca…` · 20050 |
| `tests/integration/test_tag_service.py` | ABSENT | `c7c6f7fd0471d479…` · 29844 |

## 3. What was measured, and what was not

Measured on fixtures (`tests/integration/test_tag_service.py`): `reporting/j-backfill-add-remove-readd`,
`reporting/a-tag-removed-before-publish`, `reporting/c-tag-changed-after-publish-before-send`,
`recovery/h-unauthenticated-owner-api`, `recovery/i-collector-token-calls-save`, and the empty
state of `ui/sc51-first-time-setup`. `boundary/a-default-deny-sweep-36-edges` is exercised by the
existing sweep tests; this card adds an AST check of the `FE-23` import rule and of tag → report.

One defect found by self-review and fixed before handoff: vectors are generated before the rows,
so a `tag.create` refused *after* embedding (no `backfill_days`) left orphan vectors and inflated
`built_vector_count`, which a generation's activation guard counts. `ActivationPort.preflight`
now refuses first; `test_a_refused_create_leaves_no_orphan_vector` fails without it (2 orphan
rows) and passes with it.

**NOT_RUN** — `ui/sc51-first-time-setup` count `tag_config_version__total: 1` after three
creates: this module writes one version per mutation, as `ports.yaml` and fixtures `a`/`c` require;
the disagreement is `CR-TC-TAG-01` and the count is not asserted.

**NOT_RUN** — any similarity measured with a real model (`REQ-A3`), and an end-to-end report
build/publish through the real tag port with real vectors: no production process calls
`build_report` / `publish_report` yet, and no local model exists in this environment.

## 4. Change requests

| CR | To | Detail |
| --- | --- | --- |
| `CR-TC-TAG-01` | PC04 / PC09 | `ports.yaml` (`tag.create`/`update`/`delete`: "tạo `tag_config_version` mới") and fixtures `a`/`c` count one version per mutation; `ui/sc51` expects one version after three creates; `ENT-tag-config-version.created_at` says snapshot time = publish time (PROVISIONAL). Implemented: per mutation, de-duplicated by `ux_tag_config_version_owner_hash`. |
| `CR-TC-TAG-02` | PC01 | `tag.create` must open a D28 activation in `backfill_ledger` (owned by `MOD-report-service`); `modules.yaml` has no tag → report edge. Implemented as `BackfillActivationAdapter` in the composition root, on the tag transaction's connection; the tag package imports nothing from report. The same applies to `TAG_VERSION_STALE` having to arrive as a `ReportError` (`TagConfigVersionAdapter`). |
| `CR-TC-TAG-03` | PC02 | `request_id` idempotency of `tag.create`/`update`/`delete` has no column; process-local, same disposition as `CR-TC-BACKFILL-04`. |
| `CR-TC-TAG-04` | PC02 | `tag.freeze_config_version` idempotency on `report_build_id` has no column; process-local. The publisher also calls freeze **before** the publish transaction, not inside it as `time-and-tags.md` §4.5 says (unchanged here — publisher is not in this write set). |
| `CR-TC-TAG-05` | PC04 | With no local model or no active generation, mutations succeed with `vectors.state = "pending"`; a report build then refuses (`selection.md` §5.3). `embedding.generate_vectors` failing with no active generation answers `NOT_FOUND`, which `tag.create` does not list. A generation rebuild has no path that re-embeds tags (fixture `n` event 3; embedding → tag is `FE-23`). |
| `CR-TC-TAG-06` | PC04 | `text` is not editable: the backfill identity is the normalized text and vectors are keyed by `(subject, generation)` without the text. UC-02 (`updated_at` mismatch ⇒ `CONFLICT`) is not implemented because `CONFLICT` is not an error code of `tag.update`. |
| `CR-TC-TAG-07` | PC05 | Every `/v1/tags*` body is `GenericObject`; the card pins the shapes (§4). |
| `CR-TC-TAG-08` | PC08 / PC04 | `settings.update_config` stores `backfill_days`; `report/backfill.py` reads `reporting.backfill_days`. The activation adapter reads the contract key first and the settings-service key second; neither is a code default. With neither set, `tag.create` refuses with `VALIDATION_ERROR` naming the key. |

Closed by this card: `CR-P0-07` (report context wired), `CR-TC-BACKFILL-07` (tag operations
implemented), `CR-TC-BACKFILL-12` (rescan routed), and the first half of `CR-TC-REPORT-01`
(the tag tables exist). The FK half of `CR-TC-REPORT-01` and `CR-TC-BACKFILL-10` stay open.

## 5. Evidence

`evidence/runs/TC-tag-service-E1-20261017T042623Z.json` — validated against `evidence/manifest.schema.json`. **Not** registered in
`evidence/index.json`: that file is PC09's and this card does not write it.
