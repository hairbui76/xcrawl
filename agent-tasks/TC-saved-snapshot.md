---
card_id: TC-saved-snapshot
title_vi: Save là snapshot bất biến
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M1 → M6
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-saved-service]
scenario_refs: [SC12, SC13, SC48, SC32, SC49]
invariant_refs: [I08, I17]
evidence_manifest_id: EVM-TC-saved-snapshot
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-saved-snapshot — Save là snapshot bất biến

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
| `contracts/schemas/saved-snapshot.schema.json` | `1178d314deb8dfdfbe24a9bd4645fd0fd34424fa1db0c237971b3dba3705ce3c` | 16298 |
| `contracts/data/invariants.md` | `9def66cd6e918077a96a730327646c0040acd02a6a4c29135b28e5281e64b36d` | 27782 |
| `contracts/data/identity.md` | `62fd06635c5e29a955f40cc1d56bea9d4dde9d444607fe7c07da5164993468ce` | 20576 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `contracts/ui/screens.yaml` | `db78678cba7e46b33669596f02963e1eac5e65804c6f9a997bf22d72ba6bc296` | 47481 |
| `contracts/telegram/commands.yaml` | `fc1a18dac332ea51e63721536d6a47b1d5a3048ed408af24ae787a91874e3556` | 24834 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | `a8e57390663d6dc3778ff8036ca4032a91da25f0b85844bd094f393e34f6b5ef` | 5701 |
| `acceptance/fixtures/identity/README.md` | `a6beae39f431a06104ff797094c79d51b21736a74908271b355bdeb2cf8209e5` | 11369 |
| `acceptance/fixtures/identity/d-concurrent-save-app-telegram.json` | `a9b5b041f41407066722861a04ce347513cb65d949e11774fd33c340d3d08b8d` | 7733 |
| `acceptance/fixtures/identity/e-source-deleted-snapshot-intact.json` | `2cbbe8c91a24ab9dfe46c8396e3a63b5372005b3186d314d41d09ced613188c2` | 8943 |
| `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json` | `3630edc83719ada07cae9b39f5da7ad8d1894379509c96bb1128cf958ca6ea0b` | 3462 |
| `acceptance/fixtures/telegram/j-concurrent-save-app-telegram.json` | `1df94cec7d7b44998cd07ebb5fd6d493f4d33327f7b3190aa6f0929137b8ff5b` | 8124 |
| `acceptance/fixtures/telegram/k-save-then-source-deleted.json` | `8a27e20ffb5611374b3ff566b78e95fe0e3f621fc05bd4787a2f29c94a82b434` | 7373 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-missing-content-hash.json` | `254528d628f9f5e855650ea15045ba9f8af8d28e48ee96b048399945d6f813de` | 3491 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-bad-hash-format.json` | `2b02188603feda3f9050f74bf8345bc3fd2f28aff39dc2633825b4f80a5bb0ac` | 3505 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-item-without-snapshot.json` | `76454f6e05984d307c91526b844f640bd4dd4ea8140024041ecb2a3ef3308acd` | 3553 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-target-both-ids.json` | `2cd134a69a7e83696c25541664cfb8a554b3fba14e5bec22ddda641a37c2c95d` | 3635 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-summary-missing-limitation.json` | `ff348f509d050cb27435d46203ea8bd77b43a6d8ab0e539bf0d5a474f0968df4` | 3570 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/recovery/k-delete-target-preserves-saved.json` | `0a02102333a7701b92c2b1c5b22032940cc0710d8b5faf98d67181ac16606486` | 8045 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-saved-snapshot`
- **Milestone:** M1 → M6 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-saved-service`

**Mục tiêu.** Save tạo snapshot bất biến của target tại thời điểm lưu; một target có tối đa một Saved active; bỏ tag hoặc bài gốc bị xóa trên X **không** làm mất snapshot; Save từ app và từ Telegram đồng thời chỉ tạo một Saved.

**Non-goals.**

- Không làm export Saved — hoãn P1 (`F-PC00-02`, REQ-OQ10).
- Không viết Telegram adapter (card `TC-telegram-linking-auth`).
- Không xóa dữ liệu gốc (đó là `data.delete_target`, phạm vi riêng).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0009-identity-alias-target-union.md`.
3. Hợp đồng nghiệp vụ: `contracts/schemas/saved-snapshot.schema.json`, `contracts/data/invariants.md`, `contracts/data/identity.md`, `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml`, `contracts/telegram/commands.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/identity/README.md`, `acceptance/fixtures/identity/d-concurrent-save-app-telegram.json`, `acceptance/fixtures/identity/e-source-deleted-snapshot-intact.json`, `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json`, `acceptance/fixtures/telegram/j-concurrent-save-app-telegram.json`, `acceptance/fixtures/telegram/k-save-then-source-deleted.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-missing-content-hash.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-bad-hash-format.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-item-without-snapshot.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-target-both-ids.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-summary-missing-limitation.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/recovery/k-delete-target-preserves-saved.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/saved/service.py` | create / remove / list |
| `server/app/saved/snapshot.py` | canonical JSON + `content_hash` |
| `server/app/saved/router.py` | HTTP handler `save.*` |
| `tests/contract/test_saved_snapshot_schema.py` | 1 pos + 5 neg fixture |
| `tests/integration/test_concurrent_save.py` | app + Telegram đồng thời |
| `tests/integration/test_snapshot_survives_delete.py` | bài gốc bị xóa, restart, restore |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `save.create`
- `save.remove`
- `save.list`

**Consumes** (chỉ được gọi đúng những operation này):

- `identity.resolve_target`
- `storage.get_health`

**Schema:**

- snapshot đã lưu → `contracts/schemas/saved-snapshot.schema.json`
- target union → `contracts/schemas/target.schema.json`

**State effects.** `ENT-saved-item` + `ENT-saved-snapshot`. Snapshot bất biến; `content_hash` tính trên canonical JSON. `save.remove` gỡ Saved active nhưng **không** xóa snapshot (D55, AC-12).

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-web-ui` — owner_session + CSRF
- `MOD-telegram-adapter` — owner_session_or_linked_chat cho `save.create`

**Được phép gọi:**

- MOD-identity-service
- MOD-data-store

**Đường bị cấm (denied paths):**

- `collectorToken` gọi `save.create` ⇒ 401 (denied case NC-01).
- `analysisWorkerToken` **không** mở đường tới Saved (denied case NC-02).
- Identity merge **không** đổi snapshot đã lưu (I17).

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
| `I08` | Save là snapshot bất biến; một target tối đa một Saved active; bỏ tag không xóa snapshot |
| `I17` | merge không đổi snapshot lịch sử |

**Transaction và commit point:**

- `TXN-save-target` — tạo `saved_item` + `saved_snapshot` trong một commit; UNIQUE trên (owner, target) khi active.

**Race, replay và forbidden effects:**

- Save từ app và từ Telegram cùng lúc ⇒ đúng một Saved, cả hai đường nhận phản hồi nhất quán (fixture `d`, `j`).
- Callback Telegram lặp ⇒ không tạo Saved thứ hai (fixture `f-stale-callback-no-save.json`, card 11).
- Restart / restore ⇒ `content_hash` không đổi (fixture `e` ở recovery).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `VALIDATION_ERROR` | 400 — 5 fixture `neg-saved-snapshot-*` phải rơi vào đây |
| `UNAUTHORIZED / CSRF_REJECTED` | 401/403 |
| `UNAUTHORIZED_COMMAND` | Save từ chat chưa liên kết ⇒ im lặng, không đổi state |
| `NOT_FOUND` | target không tồn tại |
| `IDEMPOTENCY_CONFLICT` | save trùng key |
| `STORAGE_WRITE_FAILED` | không commit |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC12
- SC13
- SC48
- SC32
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_saved_snapshot_schema.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_concurrent_save.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_snapshot_survives_delete.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- `COUNT(saved_item active WHERE target=T) ≤ 1` sau mọi dãy thao tác.
- `saved_snapshot.content_hash` trước restart = sau restart = sau restore.
- 5 fixture `neg-saved-snapshot-*` ⇒ `VALIDATION_ERROR`, 0 hàng ghi.
- Sau `save.remove` và sau khi bài gốc bị xóa trên X: snapshot vẫn đọc được.

**Evidence artifacts:** log pytest; hash snapshot trước/sau; dump `saved_item`.

**Yêu cầu live.** Không cần live.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `save.export` tồn tại trong `contracts/ports.yaml` nhưng MVP **hoãn** export (`F-PC00-02`). Không hiện nút export; nếu packet yêu cầu, DỪNG và hỏi. |
| `SG-02` | Danh sách loại trừ của `data.purge_all` là `OWNER_DECISION_REQUIRED` (`PROV-PC00-01`). Card này **không** được hiện thực `data.purge_all`. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-canonical-identity-merge` (I17).
- `TC-telegram-linking-auth` cho đường Save từ Telegram.

## §12. Reviewer scope

Reviewer đọc `contracts/schemas/saved-snapshot.schema.json`, `contracts/data/invariants.md` §I08/§I17, 11 fixture ở §2. Câu hỏi bắt buộc: có đường nào snapshot bị sửa hoặc bị xóa theo tag không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-saved-snapshot`
- **Vị trí:** `evidence/runs/TC-saved-snapshot/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
