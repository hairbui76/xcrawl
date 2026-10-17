---
card_id: TC-tag-service
title_vi: Tag service — lớp subscription, phiên bản cấu hình tag và cổng cho báo cáo
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED (E1 trên fixture; không có model embedding thật, không live claim)
owner_modules: [MOD-tag-service]
scenario_refs: [SC05, SC06, SC19, SC22, SC24, SC37, SC40, SC41, SC49, SC51]
invariant_refs: [I01, I05, I06, I08, I12]
evidence_manifest_id: EVM-TC-tag-service
source_refs: [SRC-SPEC §3.4, SRC-SPEC §7.1, SRC-SPEC §8.1, SRC-PLAN §3 B01, SRC-PLAN §3 B04, SRC-PLAN §11 PC10, SRC-PLAN §12]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản — đã có: OD-20261017-12 mục 6"
---

# TC-tag-service — Tag service: lớp subscription, phiên bản cấu hình tag và cổng cho báo cáo

> **Lệnh bắt đầu đã có.** Owner ra lệnh "viết card và hiện thực" ở `OD-20261017-12` mục 6 (`precode/owner-decisions-12.md`) — lệnh bằng văn bản mà `SG-G5` của mọi card đòi, cho **đúng một** card: card này. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`). Card thứ 21; được viết **sau** khi phần lớn mã của nó đã có hình dạng, nên §3 ghi đúng những file đã viết và §8 ghi đúng những gì đã chạy.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P8-20261017`** (thay `PC10-PIN-P7-20261017`; các epoch cũ hơn: `PC10-PIN-P7`, `PC10-PIN-P6`, `PC10-PIN-P5c`, `PC10-PIN-P5b`, `PC10-PIN-P4b`, `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **Card thứ 21**, pin tại cùng epoch với 20 card kia: **không** file đã pin nào đổi byte giữa lần pin `P7` và lúc card này được thêm, nên 20 card kia **không** được sinh lại. Cùng epoch nghĩa là cùng tập byte nguồn. **`P8` (2026-10-17)** pin sau vòng `OD-20261017-13`: `contracts/ai/providers.yaml` lên `0.3.0` (một mục `anthropic@claude-opus-5-5` thay cặp Sonnet 5 / Opus 5; endpoint `api.anthropic.com`; vẫn `enabled: false`), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/baseline.json`, `precode/owner-decision-request.md`, `precode/owner-decisions.md`. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` | 27451 |
| `precode/baseline.json` | `187bf7106ef1c213bdc221a2c20b955953c51b97d244b55b514a45f7d6a2e848` | 133122 |
| `precode/decision-register.md` | `9eddddb41ae6d1839ed471896107904fcdc204099e925d189e3c1167d95816c5` | 196193 |
| `contracts/modules.yaml` | `7a4e19bdbb43e1339f305cd4715f1e7ac704b09720408ccf1db48a01b23c1e25` | 108912 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412` | 128872 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `0ec6bc91eccca0588075c385060f8095d640819ce03910f64d1397ef1e4d4c4c` | 256458 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `contracts/reporting/time-and-tags.md` | `fabfc77ecd9cfe2a4e687bf612f997bd4d42deefef36f09c2299fdd1f6b69bb3` | 62003 |
| `contracts/reporting/selection.md` | `781effb61be2865a07fa3be4373196229bb6bd89048abbb943d646ca95401fe4` | 37357 |
| `contracts/http/openapi.yaml` | `a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d` | 231727 |
| `contracts/ui/screens.yaml` | `7e67f884c6bb42e6b287261578613c4b9f12e03ddf94fd08281b5218ed73ed64` | 51233 |
| `acceptance/fixtures/reporting/README.md` | `cdb2008913f53562ec41fe7ed179c3c17d3a568ee9d5dc8027e16405dcf2b54f` | 16228 |
| `acceptance/fixtures/reporting/a-tag-removed-before-publish.json` | `cd543ec22a34fbf18b923b1e4fb4d733e54075a6586f810175bf28767f691d44` | 16121 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | `3b0d6f24a06ac907ce6c65b139d6124f09dd9ff89389e64d58256a844004a3fa` | 6023 |
| `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json` | `b074e9f353e4b9646cdf58c88864e1677b86adccdff1b38ab049cbc5e9a4cd4a` | 6842 |
| `acceptance/fixtures/recovery/README.md` | `fa733add0f408dee3f1d870b1ca6f6da977337f2d940e0e13afe74ec4efccc79` | 12235 |
| `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json` | `32883c7a2a12b36d964f7974c45952e731f2330cc1416b43c9e4895ae1ad5119` | 4024 |
| `acceptance/fixtures/recovery/i-collector-token-calls-save.json` | `78e6e6ee47008b5d9b44dbdf65994f93c7ce89ee33ef7f96e7699ee7e0372886` | 5229 |
| `acceptance/fixtures/ui/README.md` | `c7ac5d304c33ff48228f5256ac2e56e097eb20121a6648ee4cca431041670dce` | 6380 |
| `acceptance/fixtures/ui/sc51-first-time-setup.json` | `19820cec74bb3a73dd9945674ce3dd88fd9d18f1d15ae0b48ebef938b92f18d7` | 13282 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-tag-service`
- **Milestone:** M4 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-tag-service`

**Mục tiêu.** Hiện thực tám operation `tag.*` của `contracts/ports.yaml` để Owner **có** một lớp subscription — tag, alias, exclusion — và để `MOD-report-service` có một `TagConfigVersionPort` thật. Đó là thứ còn thiếu để `app.state.report_context` được nối (`CR-P0-07`) và là thứ `CR-TC-BACKFILL-07` / `CR-TC-REPORT-01` nói chưa card nào viết. Hai bảng của module đã có từ `0013` (`tag`, `rescan_ledger`); card này thêm ba bảng còn lại (`tag_alias`, `tag_exclusion`, `tag_config_version`) và route cho `tag.rescan_corpus` đã có service mà chưa có HTTP (`CR-TC-BACKFILL-12`).

**Non-goals.**

- **Không** chọn hay tải model embedding. `REQ-OQ09` có ứng viên làm việc `intfloat/multilingual-e5-small` (`OD-20261017-12` mục 5) nhưng vẫn `KC`; card chỉ cho phép **cấu hình** một đường dẫn model cục bộ.
- Không viết vòng job tự build/publish báo cáo theo lịch: chưa có tiến trình production nào gọi `build_report` / `publish_report`; đó là việc của card khác.
- Không viết màn hình `SCR-topics` ở `web/` (một card UI riêng).
- Không khởi tạo `embedding_generation` (`embedding.start_generation_rebuild` thuộc `MOD-settings-service`).
- Không thêm khóa ngoại cho `report.tag_config_version_id` hay `backfill_ledger.tag_id` — cột của module khác (`CR-TC-REPORT-01`, `CR-TC-BACKFILL-10`).

## §2. Read set

Đọc đủ danh sách ở §0. Thứ tự đề nghị:

1. `precode/README.md`, `precode/change-control.md`, `precode/owner-decisions-12.md` → baseline, điều cấm, và lệnh bắt đầu.
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md`.
3. Hợp đồng nghiệp vụ: `contracts/reporting/time-and-tags.md` (§3 freeze, §6 backfill, §7 rescan, §8.5), `contracts/reporting/selection.md` (§2–§5), `contracts/ui/screens.yaml` (`SCR-topics`, `SCR-tag-matching-preview`), `contracts/data/invariants.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`, `contracts/http/openapi.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/a-tag-removed-before-publish.json`, `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json`, `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json`, `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`, `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc51-first-time-setup.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn | Vai trò |
| --- | --- |
| `server/migrations/versions/0016_tc_tag_service.py` | `tag_alias`, `tag_exclusion`, `tag_config_version` — chép đúng `entities.yaml` |
| `server/app/tags/service.py` | bảy operation (trừ rescan): list, create, update, delete, preview, get-active, freeze; `TagContext`, `TagError`, ba port |
| `server/app/tags/router.py` | sáu route HTTP của `MOD-web-ui`, gồm `tag.rescan_corpus` (đóng `CR-TC-BACKFILL-12`) |
| `server/app/main.py` | **chỉ** khối `# >>> TC-tag-service >>>` |
| `server/app/wiring.py` | `TagConfigVersionAdapter`, `BackfillActivationAdapter`, `UnconfiguredEncoder`, `local_encoder`; nối `tag_context`, `rescan_context`, `report_context` |
| `server/app/settings.py` | bốn biến `RR_EMBEDDING_MODEL_*` |
| `server/tests/test_wiring.py` | khẳng định `report_context` nay được nối |
| `tests/integration/test_tag_service.py` | oracle fixture `a`, `c`, `j`, `h`, `i`, `sc51` + ranh giới import |

`server/app/tags/rescan.py` (của `TC-backfill-pending-ledger`) **không** bị sửa; router gọi nó như một thư viện.

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript** — `agent-tasks/README.md` §5.3.

## §4. Consumes / produces

**Produces** (ID lấy từ `contracts/ports.yaml`):

- `tag.list`
- `tag.create`
- `tag.update`
- `tag.delete`
- `tag.preview_matches`
- `tag.rescan_corpus`
- `tag.get_active_config_version`
- `tag.freeze_config_version`

**Consumes** (chỉ được gọi đúng những operation này):

- `embedding.generate_vectors`
- `embedding.get_active_generation`

**Schema.** Nguồn schema của bảng → `contracts/data/entities.yaml`. Body HTTP là `GenericObject` trong `contracts/http/openapi.yaml`, nên card chốt hình dạng ở đây và raise `CR-TC-TAG-07` để PC05 đóng schema:

- `POST /v1/tags`: `{text, aliases?: [string], exclusions?: [string], similarity_threshold?: number|null}` → 201 `{tag, tag_config_version, backfill, vectors}`.
- `PATCH /v1/tags/{tag_id}`: `{aliases?, exclusions?, similarity_threshold?}` — **không có `text`** (xem `CR-TC-TAG-06`).
- `DELETE /v1/tags/{tag_id}`: `{request_id?}` → `{tag, tag_config_version, already_removed}`.
- `POST /v1/tags/preview-matches`: `{tag_id}` **hoặc** `{text}`, `similarity_threshold?` → `{matched_labels, excluded_labels, threshold_used, embedding_generation_id, empty_state_vi}`.
- `POST /v1/tags/rescan-corpus`: `{tag_id?, scope_from?}`; `Idempotency-Key` là `request_id` → 202.
- Payload của `tag_config_version`: đúng hình dạng `TagSet.from_payload` của `server/app/report/builder.py` parse — `{tags:[{id,text,similarity_threshold}], tag_aliases:[{id,tag_id,text}], tag_exclusions:[{id,tag_id|null,text}]}`, chỉ hàng active, theo id.

**State effects.** Mỗi mutation ghi phiên bản cấu hình của bộ tag nó để lại, **trong cùng transaction**; `ux_tag_config_version_owner_hash` làm việc này idempotent theo nội dung. `tag.create` mở **một** activation backfill (D28) qua `BackfillActivationAdapter` trên **cùng connection**. `tag.delete` chỉ đặt `state = removed`. Vector được sinh **trước** khi ghi hàng (một writer SQLite); thiếu model hoặc generation active ⇒ `vectors.state = pending`.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**.

**Được gọi bởi:**

- `MOD-web-ui` — HTTP qua `owner_session` (+ CSRF cho bốn mutation)
- `MOD-report-service` — internal, `tag.get_active_config_version` và `tag.freeze_config_version`

**Được phép gọi:**

- MOD-data-store (SQLite)
- MOD-embedding-service (`embedding.generate_vectors`, `embedding.get_active_generation`)

**Đường bị cấm (denied paths):**

- `MOD-x-collector` → tag (`FE-11`), `MOD-analysis-worker` → tag (`FE-12`): HTTP ⇒ `UNAUTHORIZED`.
- `MOD-embedding-service` → tag (`FE-23`): import package tag từ package embedding bị cấm; kiểm bằng AST.
- `MOD-telegram-adapter` → tag (`FE-30`): không có lệnh chat nào sửa subscription (`UNAUTHORIZED_COMMAND`).
- Tag **không** import package report: backfill activation và lỗi `ReportError` đi qua composition root (`CR-TC-TAG-02`).

Bảo mật: `owner_session` cho mutation nghĩa là `ownerSessionCookie` **AND** `ownerCsrfToken` trong **một** security requirement.

**Ranh giới mã lỗi khi bị từ chối (ruling R5-01, bắt buộc — chọn sai mã là FAIL):**

| Tình huống | Mã |
| --- | --- |
| Request HTTP từ một lớp principal không được phép cho operation đó (ví dụ token collector gọi `save.create`) | `UNAUTHORIZED` (401) |
| Lời gọi/import trong tiến trình đi qua một cạnh **không** có trong `allowed_edges` (ví dụ FE-08 collector → analysis worker, scheduler → Telegram) | `FORBIDDEN_EDGE` |
| Actor thiếu capability tiến trình/mạng/filesystem/tool (adapter mở socket, connector điều khiển Chrome) | `CAPABILITY_DENIED` |
| Mutation dùng phiên owner mà thiếu/sai CSRF token | `CSRF_REJECTED` (403; **không** hủy phiên) |

Mỗi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` có `denied_cases[]` với `expected_error_code` theo bảng trên và `scenario_refs: [SC49]`. Oracle chung: `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §6. Invariants và transaction

| Invariant | Nội dung |
| --- | --- |
| `I01` | mọi hàng mang `owner_id`; xóa tag không xóa dữ liệu nào |
| `I05` | báo cáo đã publish trỏ vào một hàng `tag_config_version` bất biến; đổi tag sau đó không đổi một byte |
| `I06` | một subscription identity tiêu thụ backfill đúng một lần — kể cả qua bỏ rồi thêm lại |
| `I08` | bỏ tag không chạm Saved |
| `I12` | vector chỉ ở một generation; không có encoder giả trong triển khai thật |

**Transaction và commit point:**

- `tag.create`: tag + alias + exclusion + `backfill_ledger` + `tag_config_version` trong **một** `engine.begin()`. Vector sinh trước, trong transaction riêng của embedding service.
- `tag.update` / `tag.delete`: hàng của tag + phiên bản mới trong một transaction.
- `tag.freeze_config_version`: so phiên bản đang sống với `expected_tag_config_version_id`; lệch ⇒ `TAG_VERSION_STALE`. Lặp lại trong cùng `report_build_id` trả cùng phiên bản.

**Race, replay và forbidden effects:**

- Cùng `Idempotency-Key`, cùng payload ⇒ trả lại kết quả cũ; payload khác ⇒ `IDEMPOTENCY_CONFLICT`. Sổ này **trong tiến trình** (`CR-TC-TAG-03`).
- Trùng chữ (casefold + NFC) với một tag active ⇒ `VALIDATION_ERROR`, kiểm lại **trong** transaction ghi.
- Thêm lại một alias đã bỏ ⇒ kích hoạt lại **đúng hàng cũ** (`ux_tag_alias_owner_tag_text` phủ cả hàng `removed`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml`. Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ |
| --- | --- |
| `UNAUTHORIZED` | không phiên owner, hoặc bearer của collector/worker |
| `CSRF_REJECTED` | mutation qua phiên owner thiếu `X-CSRF-Token` |
| `VALIDATION_ERROR` | body sai, thiếu header wire, chữ trùng, có `text` trong body của lệnh sửa, thiếu `reporting.backfill_days` |
| `NOT_FOUND` | tag không tồn tại; chưa có phiên bản nào cho `tag.get_active_config_version` |
| `IDEMPOTENCY_CONFLICT` | cùng khóa, payload khác |
| `EMBEDDING_GENERATION_MISMATCH` | vector không sinh được vào generation active; preview khi chưa có generation |
| `TAG_VERSION_STALE` | bộ tag đổi giữa build và publish |
| `STORAGE_WRITE_FAILED` | storage guard từ chối; không có gì được ghi |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. Khóa `details_safe` lạ bị từ chối ngay khi dựng lỗi.

## §8. Verification

**Scenario.**

- SC05 — fixture `a`
- SC06 — re-add dùng lại analysis: chỉ phần tag (tag id mới, cùng identity) được đo
- SC19 — fixture `c`
- SC22 — `tag.rescan_corpus` qua HTTP
- SC24 — preview khi chưa có generation bị từ chối, không đoán
- SC37 — fixture `j`
- SC40 — fixture `h`
- SC41 — fixture `i`
- SC49 — ranh giới import FE-23 + bảng R5-01
- SC51 — fixture `sc51`: chỉ trạng thái trống của preview

**Lệnh đã chạy:**

- `uv run pytest tests/integration/test_tag_service.py -q` — 19 passed
- `uv run pytest -q` toàn cây; `uv run ruff check .`; `uv run mypy`
- `uv run python evidence/tools/e0_check.py --repo .`; `uv run python evidence/tools/verify_cards.py --repo .`

**Oracle** (đếm hàng hoặc so chuỗi):

- Fixture `j`: activation 1 `granted` / `first_activation`; activation 2 trên **tag id mới** `denied_already_consumed` với **đúng** chuỗi lý do của fixture; một `subscription_identity_hash`; đúng 1 hàng đã tiêu thụ.
- Fixture `a`: sau khi xóa, phiên bản active chỉ còn `protein folding`, và `TagSet.from_payload` parse được nó; freeze với id đó thành công, với id trước khi xóa ⇒ `ReportError(TAG_VERSION_STALE)`.
- Fixture `c`: đổi sau freeze ⇒ phiên bản mới; phiên bản đã freeze đọc lại cùng `id`, `content_hash`, `payload`; freeze lặp lại idempotent.
- Fixture `h`: `DELETE` không phiên ⇒ 401; có phiên thiếu CSRF ⇒ 403 `CSRF_REJECTED`; `GET /v1/tags` trước = sau.
- Fixture `i`: `PATCH` bằng token collector hợp lệ ⇒ 401; không đổi gì.
- `GET /v1/reports` trên app đã nối ⇒ **200** (trước đây 500, `F-A3-P5-03`).

**NOT_RUN, ghi rõ:** con số `tag_config_version__total: 1` của `sc51` sau ba lần tạo — mâu thuẫn với `ports.yaml` và fixture `a`/`c` (`CR-TC-TAG-01`); mọi phép đo similarity với một model thật (`REQ-A3`); build/publish một báo cáo đầu-cuối bằng tag port thật **và** một generation có vector thật.

**Yêu cầu live.** E3 **NOT_RUN**: không có model embedding thật trong môi trường kiểm.

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED (E1 trên fixture; không có model embedding thật, không live claim)`.**

Read set chạm `contracts/reporting/` (phạm vi đã phê chuẩn) và `contracts/ui/screens.yaml`. Các điểm dừng KC (`REQ-OQ09`, `REQ-A3`) **giữ nguyên**: chọn một ứng viên không phải đo nó.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-MODEL` | **Không tải model, không chọn model thay `REQ-OQ09`.** Model chỉ được nạp từ một đường dẫn cục bộ mà Owner cấu hình; không có đường dẫn ⇒ `UnconfiguredEncoder`, **không bao giờ** một encoder test trong triển khai thật. |
| `SG-TEXT` | `text` của tag không sửa tại chỗ (`CR-TC-TAG-06`). Muốn cho phép ⇒ CR, vì nó đổi khóa subscription của backfill. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Cần chọn framework/thư viện mới ⇒ DỪNG và raise CR. |
| `SG-G5` | Đã đạt: `OD-20261017-12` mục 6 là lệnh bắt đầu bằng văn bản cho đúng card này. |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0. Card này **không** sửa chúng; đăng ký manifest vào `evidence/index.json` là việc của PC09. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` chạm tới module của card phải bị từ chối bằng đúng mã của bảng R5-01 (§5). Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Lệch một hash ở §0 ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle mâu thuẫn với hợp đồng ⇒ raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp không có trong §5 ⇒ DỪNG. Hai chỗ card chạm ranh giới — activation backfill và lỗi `ReportError` — được đặt ở composition root, không ở package tag, và được raise (`CR-TC-TAG-02`). |

**Change request phát sinh** (chi tiết trong `evidence/handoffs/TC-tag-service-handoff.md`):

| CR | Gửi | Một dòng |
| --- | --- | --- |
| `CR-TC-TAG-01` | PC04 / PC09 | `sc51` đếm 1 phiên bản sau 3 lần tạo; `ports.yaml` + fixture `a`/`c` đòi một phiên bản mỗi mutation; `entities.yaml` nói `created_at` = lúc publish (PROVISIONAL) |
| `CR-TC-TAG-02` | PC01 | `tag.create` phải mở activation trong `backfill_ledger` (của report) nhưng không có cạnh tag → report |
| `CR-TC-TAG-03` | PC02 | idempotency theo `request_id` của ba mutation không có cột lưu — sổ trong tiến trình |
| `CR-TC-TAG-04` | PC02 | freeze idempotent theo `report_build_id` không có cột lưu — sổ trong tiến trình |
| `CR-TC-TAG-05` | PC04 | không model / không generation ⇒ mutation vẫn thành công với `vectors: pending`; rebuild generation chưa có đường nhúng lại vector tag (fixture `n` sự kiện 3) |
| `CR-TC-TAG-06` | PC04 | `text` không sửa được; UC-02 (`updated_at` lệch ⇒ `CONFLICT`) không hiện thực vì `CONFLICT` không có trong mã lỗi của `tag.update` |
| `CR-TC-TAG-07` | PC05 | body `/v1/tags*` là `GenericObject`; hình dạng chốt ở §4 |
| `CR-TC-TAG-08` | PC08 / PC04 | `settings.update_config` ghi khóa `backfill_days`, backfill đọc `reporting.backfill_days`; adapter đọc khóa hợp đồng trước, khóa kia sau |

Khi dừng: báo Coordinator với trạng thái, đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-owner-auth-session` — phiên owner + CSRF.
- `TC-embedding-generation-switch` — `EmbeddingService`, `tag_vector`, kiểm generation.
- `TC-backfill-pending-ledger` — `open_activation`, `rescan.py`.
- `TC-report-coverage-publish-cas` — người tiêu thụ `TagConfigVersionPort`; card này **không** sửa nó.

## §12. Reviewer scope

Reviewer đọc `contracts/reporting/time-and-tags.md` §3 và §6, `contracts/ports.yaml` (tám `tag.*`), `entities.yaml` (`tag*`, `tag_config_version`), và `server/app/wiring.py` (hai adapter). Ba câu hỏi bắt buộc: (1) có đường nào một mutation để lại hàng tag mà không có phiên bản hoặc activation tương ứng không; (2) freeze có thể trả một phiên bản **khác** phiên bản build đã đọc mà không báo `TAG_VERSION_STALE` không; (3) có đường nào một vector không do model thật sinh ra lọt vào database không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-tag-service`
- **Vị trí:** `evidence/runs/TC-tag-service-E1-<timestamp>.json`
- **Schema:** `evidence/manifest.schema.json` (PC09). Đăng ký vào `evidence/index.json` là việc của PC09.
- **Bắt buộc có:** `spec_sha256` = hash ở §0; `contract_hashes` copy nguyên văn từ §0; `review_type: SELF_VALIDATION`; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card viết trong phiên `session_01XQgXrAiGrnAUFS3jowQf2w` dưới `AUTH-OWNER-20261017-13`. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
