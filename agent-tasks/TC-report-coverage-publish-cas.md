---
card_id: TC-report-coverage-publish-cas
title_vi: Đóng kỳ báo cáo: coverage nối liền và publish bằng CAS
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-report-service]
scenario_refs: [SC05, SC08, SC09, SC19, SC22, SC24, SC35, SC49, SC50]
invariant_refs: [I05, I06, I07, I12]
evidence_manifest_id: EVM-TC-report-coverage-publish-cas
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-report-coverage-publish-cas — Đóng kỳ báo cáo: coverage nối liền và publish bằng CAS

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. Stack (Option A / Python) là **PROVISIONAL** theo `precode/adr/ADR-0006-stack-option-a.md`; mọi đường dẫn ở §3 và mọi lệnh ở §8 có điều kiện *"nếu ADR-0006 được chấp nhận"*.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-FCW4f-20260907`** (thay `PC10-PIN-FCW4e-20260907`; các epoch cũ hơn: `PC10-PIN-FCW4d-20260907`, `PC10-PIN-FCW4c-20260907`, `PC10-PIN-FCW4b-20260907`, `PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). Hash dưới đây được **tính lại trực tiếp trên repo**; thay đổi duy nhất so với `FCW4e` là `contracts/modules.yaml` (năm denied case thêm `event_type`; không oracle nào của card bị ảnh hưởng). **Card là nguồn chuẩn của tên epoch**; mọi file khác khẳng định pin hiện hành phải đọc tên từ đây, không chép tay (finding `F-A2R1-03`). Trước khi bắt đầu, chạy `sha256sum` trên **mọi** dòng dưới đây. Lệch một dòng ⇒ card `STALE`, DỪNG (`precode/change-control.md` §5, quy tắc `INV-06`/`INV-09` của `precode/gates.yaml`).

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/baseline.json` | `e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` | 97620 |
| `precode/decision-register.md` | `212441a429420d1cc11cdc4a9c79a11648e45e1b92278a08f77a9779943ad15d` | 97899 |
| `contracts/modules.yaml` | `11af00fd97a03d5357fc1a72d0e4e61293164f449c3a50e700c03a202e1166c7` | 105642 |
| `contracts/capabilities.yaml` | `fae5891cff5ff25757f168d8182111fa4fc6b49f6b851ac7cc07105fef952cf7` | 45672 |
| `contracts/ports.yaml` | `93ba159856a4821ad46d1d05199987f475c8ae5603d8f9200e1418b0e2eab42e` | 126182 |
| `contracts/errors.yaml` | `b63eef7abd4cee328581e5e06cbc8314e60e52e03468dbe6acea42a0a843ad26` | 62269 |
| `contracts/retry-policy.yaml` | `5e083230e2cc5db481736adcf189a6cf8e302ebdf45cad614582731698cf06d5` | 41620 |
| `contracts/data/entities.yaml` | `c2ceeafd1b78705941f368bfe73f67cf097ffad8179c7455b2d4eeda571b5a1e` | 221041 |
| `contracts/reporting/time-and-tags.md` | `7a3a3845707e6160c52601f25baf16190be1ecee3933b94755acb808e6f075e0` | 59747 |
| `contracts/reporting/selection.md` | `cc62af2bd476c51efa9b156bae66be6dae3a0bcd712eb79cd1d4ba3a3d5c2fc0` | 34622 |
| `contracts/state/report.yaml` | `2b22c27df302c7fbf733b352ad41390a1d407ac98cfa7b1a816cf3580349aba0` | 27154 |
| `contracts/state/run.yaml` | `c92e7c4e6fc6dce8a0280e64a182c1463a1e7a4b07d3c26f8036e37fd34579ec` | 91779 |
| `contracts/schemas/report.schema.json` | `a7c7255a5bae703b0bdcd1ba761153dbce686b5766b05dfbaa1606392338d07b` | 31129 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `contracts/data/invariants.md` | `9def66cd6e918077a96a730327646c0040acd02a6a4c29135b28e5281e64b36d` | 27782 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `64c0793eeca31b6ac0606813adac96fa483e01eb4b81eaef950edfff16fd3194` | 5459 |
| `precode/adr/ADR-0007-timezone-handling.md` | `334abf600467fba70e7797113956c99406acb3617b2da6f3ccce56f8f5786ed7` | 4843 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `5ed7b2c429ef7e060140f8b6bbaa71b761b482134aaac155ad32d64bef34b8c0` | 4924 |
| `acceptance/fixtures/reporting/README.md` | `2c7974e82c4f7ac6e2554050cc1ffda79bfd926faef2c01ed0d4070b8cc45663` | 14516 |
| `acceptance/fixtures/reporting/a-tag-removed-before-publish.json` | `1a88edc26f5e48cd77b12cb0745045e6e421dac29b52635ddcb6db2960a0e7b5` | 15287 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | `4d5f14c423c1764e9e866df55becd63e6ee6d828e788abc79b17d39db3b6f089` | 5189 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | `e619c514f35956db8d4454df4779eb5df56f4fab814acb4c9d3c55fdc790f7e3` | 8045 |
| `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json` | `6584abee3fdb83ff04be11f9e4992e8650e60095a7fc7d058d5c5177e4dfdfa9` | 12841 |
| `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json` | `4427374d434a82a0aeeb1841c15200e58628b37dae62f8c63ec2892d0331a0b2` | 4961 |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | `0d4d98c87000e19c886fc65748d101f07df79b4e2711f805726c18cc78fbce96` | 8955 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | `e2de531e3b5bbad92946b4f6b3ea5f960bbed7afb687df92252391095e24a624` | 14510 |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | `39ef6a819b4f09b041d6d2b3e4b9338023a46c20b7e11da0871546f7e5c8e231` | 28343 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/e2e/README.md` | `74790ee8435791e5dbc360cf84a0737f660e2bebcbdb0749cdc1528a669d9ca8` | 6013 |
| `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json` | `a925781ecf2d36e3cd02a3d666819bc5186c8d809e7865e51bac77d387678c00` | 30745 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-report-coverage-publish-cas`
- **Milestone:** M4 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-report-service`

**Mục tiêu.** Build và publish một kỳ: freeze tag config version tại **publish transaction**, kiểm CAS trên coverage predecessor, ghi report items + first-announcement ledger + backfill consumption + delivery intent trong một commit, và giữ các cửa sổ coverage half-open nối liền kể cả khi kỳ rỗng.

**Non-goals.**

- Không gửi Telegram (card `TC-telegram-unknown-delivery`); report service chỉ tạo intent.
- Không sửa report đã publish (B01/AMD-B01).
- Không viết backfill/pending ledger (card `TC-backfill-pending-ledger`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0004-tag-freeze-point.md`, `precode/adr/ADR-0007-timezone-handling.md`, `precode/adr/ADR-0002-run-state-model-split.md`.
3. Hợp đồng nghiệp vụ: `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/state/report.yaml`, `contracts/state/run.yaml`, `contracts/schemas/report.schema.json`, `contracts/http/openapi.yaml`, `contracts/data/invariants.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/a-tag-removed-before-publish.json`, `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json`, `acceptance/fixtures/reporting/d-empty-period-coverage-only.json`, `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json`, `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json`, `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json`, `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `acceptance/fixtures/reporting/m-density-worked-example.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/e2e/README.md`, `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/report/builder.py` | chọn nội dung theo `selection.md` trên snapshot input có version |
| `server/app/report/publisher.py` | TXN-report-publish + CAS coverage predecessor |
| `server/app/report/coverage.py` | cửa sổ half-open `[from, to)`, kỳ rỗng |
| `server/app/report/router.py` | HTTP handler `report.list`, `report.get` |
| `tests/contract/test_report_schema.py` | `report.schema.json` |
| `tests/integration/test_publish_cas.py` | hai publisher đồng thời |
| `tests/integration/test_coverage_contiguous.py` | nhiều kỳ, kỳ rỗng, crash publisher |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `report.build`
- `report.publish`
- `report.list`
- `report.get`

**Consumes** (chỉ được gọi đúng những operation này):

- `tag.get_active_config_version`
- `tag.freeze_config_version`
- `embedding.get_active_generation`
- `embedding.generate_vectors`
- `identity.resolve_target`
- `analysis.enqueue_tasks`
- `delivery.create_intent`
- `storage.get_health`

**Schema:**

- report và report item → `contracts/schemas/report.schema.json`

**State effects.** `contracts/state/report.yaml` — `building → published`, nhánh `aborted` với `abort_reason` bắt buộc (`CR-PC04-08/09` **đã đóng** ở FCW4d — cột tồn tại với enum `empty_period | tag_version_stale | embedding_generation_mismatch | cas_conflict | builder_failure | cancelled`, CHECK NOT NULL khi và chỉ khi `status='aborted'`). `quality: complete | partial` là trường riêng. Kỳ rỗng vẫn ghi coverage record và **không** gửi digest.

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-report` (abort_reason, selection_version); `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at); `ENT-tag` (removed_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-job-service` — internal cho `report.build`
- `MOD-web-ui` — owner_session cho `report.list`/`report.get`

**Được phép gọi:**

- MOD-tag-service
- MOD-embedding-service
- MOD-identity-service
- MOD-analysis-service
- MOD-delivery-service
- MOD-data-store

**Đường bị cấm (denied paths):**

- Report service **không** gọi Telegram trực tiếp và **không** sửa phân tích đã commit (SRC-PLAN §6).
- Delivery **không** đổi nội dung report đã publish (B01).

Bảo mật (chốt post-FIX1 trong `contracts/http/openapi.yaml`): `owner_session` cho mutation nghĩa là `ownerSessionCookie` **AND** `ownerCsrfToken` trong **một** security requirement; collector và analysis worker dùng bearer riêng; mọi route `backup.*` chỉ nhận `backupOperatorToken`.

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
| `I05` | report lưu tag version, selection version, evidence refs; không đổi nội dung sau publish |
| `I06` | coverage window nối liền, half-open; pending không mất khi con trỏ tiến |
| `I07` | một canonical work chỉ có một first-announcement |
| `I12` | không trộn generation trong một lần selection |

**Transaction và commit point:**

- `TXN-report-publish` — kiểm expected coverage predecessor + tag/model version rồi ghi report items, first-announcement ledger, backfill consumption và delivery intent trong **một** commit.

**Race, replay và forbidden effects:**

- Hai publisher đồng thời ⇒ kẻ thua CAS đọc lại, **không** publish kỳ chồng (fixture `g`).
- Tag đổi ngay trước CAS ⇒ `TAG_VERSION_STALE`, build abort hoặc rebuild; report cũ không bị mutate (fixture `c`).
- Builder crash ⇒ backfill **không** bị tiêu thụ (fixture `k`, thuộc card 9).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `TAG_VERSION_STALE` | build abort/rebuild; report đã publish giữ nguyên |
| `EMBEDDING_GENERATION_MISMATCH` | selection blocked trước commit |
| `CONFLICT` | thua CAS; đọc lại |
| `IDEMPOTENCY_CONFLICT` | publish trùng key |
| `VALIDATION_ERROR` | 400 |
| `UNAUTHORIZED` | 401 cho `report.list`/`report.get` |
| `STORAGE_WRITE_FAILED` | không commit; coverage không tiến |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC05
- SC08
- SC09
- SC19
- SC22
- SC24
- SC35
- SC49
- SC50

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_report_schema.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_publish_cas.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_coverage_contiguous.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Coverage ledger: các `[from, to)` **nối liền**, không chồng, không hở — kể cả kỳ rỗng và kỳ sau crash.
- Fixture `a`: target bị bỏ tag trước freeze **không** nằm trong `expected_selected_ids`.
- Fixture `g`: đúng một report `published` cho một kỳ; publisher thua có trace CAS conflict.
- Fixture `h`/`i`: một canonical work có đúng một first-announcement; lần sau là reference **có ngày**.
- `report.tag_config_version` bất biến sau publish; hash nội dung report không đổi khi delivery chạy.

**Evidence artifacts:** log pytest; dump coverage ledger; CAS conflict trace; hash report trước/sau delivery.

**Yêu cầu live.** Không cần live. Tính hữu ích của nội dung là E4, ngoài phạm vi.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC04-04` còn OPEN: `report.publish.error_codes` trong `contracts/ports.yaml` **chưa** có `CONFLICT` trong khi `contracts/errors.yaml` khai `CONFLICT.operations` **có** `report.publish`. Hai file lệch nhau ⇒ DỪNG trước khi code nhánh CAS, raise CR. |
| `SG-02` | `CR-PC04-08/09` **đã đóng** ở FCW4d: `report.abort_reason` tồn tại trong `contracts/data/entities.yaml` với enum đúng sáu giá trị `empty_period | tag_version_stale | embedding_generation_mismatch | cas_conflict | builder_failure | cancelled`. Dùng **đúng** sáu giá trị đó — hai giá trị mà bản card trước phỏng đoán (`cas_lost`, `builder_crash_or_stale`) **không** tồn tại. Cần một giá trị thứ bảy ⇒ DỪNG và raise CR. |
| `SG-03` | `CR-PC02-06` (kế thừa `first_announced` sau merge) còn OPEN ⇒ nhánh I07 sau merge chưa claim được. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-canonical-identity-merge`
- `TC-embedding-generation-switch`
- `TC-analysis-once-per-generation`
- `TC-backfill-pending-ledger`

## §12. Reviewer scope

Reviewer đọc `contracts/reporting/time-and-tags.md`, `contracts/state/report.yaml` (`publish_cas`), 8 fixture reporting/*. Câu hỏi bắt buộc: có đường nào report đã publish bị sửa không, và coverage có hở không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-report-coverage-publish-cas`
- **Vị trí:** `evidence/runs/TC-report-coverage-publish-cas/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
