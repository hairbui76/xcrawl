---
card_id: TC-embedding-generation-switch
title_vi: Embedding generation: rebuild và chuyển active nguyên tử
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M3 → M5
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-embedding-service]
scenario_refs: [SC24, SC08, SC49, SC52]
invariant_refs: [I12]
evidence_manifest_id: EVM-TC-embedding-generation-switch
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-embedding-generation-switch — Embedding generation: rebuild và chuyển active nguyên tử

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
| `contracts/reporting/selection.md` | `cc62af2bd476c51efa9b156bae66be6dae3a0bcd712eb79cd1d4ba3a3d5c2fc0` | 34622 |
| `contracts/state/report.yaml` | `2b22c27df302c7fbf733b352ad41390a1d407ac98cfa7b1a816cf3580349aba0` | 27154 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `contracts/ops/deployment.md` | `7e1c03776b4c8be20f596a0317ea1c79429cf4ecaa78fadc1f0ec3e5158088f5` | 17759 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `277eb556cff950193ca55cecd0ef0d06dca279a4d376c5c8e889a48ebf60c09c` | 5717 |
| `acceptance/fixtures/reporting/README.md` | `2c7974e82c4f7ac6e2554050cc1ffda79bfd926faef2c01ed0d4070b8cc45663` | 14516 |
| `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json` | `c1035509a76e42802859138297ee9ac0d575538e3d1a3ce95ad1336c072543f2` | 5746 |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | `39ef6a819b4f09b041d6d2b3e4b9338023a46c20b7e11da0871546f7e5c8e231` | 28343 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json` | `a526022dfba75c7ee06eb6ba58697d4ea849a844ef4b0f49707a651c25e75d34` | 18395 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-embedding-generation-switch`
- **Milestone:** M3 → M5 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-embedding-service`

**Mục tiêu.** Đổi model embedding sinh một generation mới; selection bị chặn thay vì trộn vector khác model/dimension; chuyển active generation là một thao tác nguyên tử sau khi đủ vector.

**Non-goals.**

- Không gọi provider API để thay embedding local (D48/D50).
- Không chốt model embedding cụ thể (REQ-OQ09, sau A3).
- Không viết thuật toán mật độ (card `TC-report-coverage-publish-cas` và `contracts/reporting/selection.md`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0001-topology-and-placement.md`.
3. Hợp đồng nghiệp vụ: `contracts/reporting/selection.md`, `contracts/state/report.yaml`, `contracts/http/openapi.yaml`, `contracts/ops/deployment.md`, `contracts/data/entities.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json`, `acceptance/fixtures/reporting/m-density-worked-example.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/embedding/service.py` | generate / get_active / start_rebuild / activate |
| `server/app/embedding/generation.py` | generation, model id, dimension, đếm phủ |
| `server/app/embedding/repository.py` | vector repository port |
| `tests/contract/test_embedding_generation_guard.py` | cosine giữa hai generation bị chặn |
| `tests/integration/test_generation_activation.py` | chuyển active nguyên tử, không trộn |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `embedding.generate_vectors`
- `embedding.get_active_generation`
- `embedding.start_generation_rebuild`
- `embedding.activate_generation`

**Consumes** (chỉ được gọi đúng những operation này):

- `storage.get_health`

**Schema:**

- không có JSON Schema riêng; hình dạng ở `ENT-embedding-generation` và `ENT-tag-vector` → `contracts/data/entities.yaml`

**State effects.** `ENT-embedding-generation` có `model_id`, `dimension`, `state`, số vector đã phủ. Trong lúc rebuild: dùng generation cũ **hoặc** chặn selection có lý do; không trộn.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-ingest-service` — internal
- `MOD-tag-service` — internal
- `MOD-report-service` — internal
- `MOD-settings-service` — internal cho `embedding.start_generation_rebuild`

**Được phép gọi:**

- Model embedding local trên server
- MOD-data-store (vector repository port)

**Đường bị cấm (denied paths):**

- Không gọi provider API/CLI (SRC-PLAN §6: 'Embedding service … Đường bị cấm: Provider API/CLI').
- Không đổi subscription; không âm thầm thay embedding local bằng API.

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
| `I12` | vector khác model/generation/dimension không được so sánh trong cùng một lần selection |

**Transaction và commit point:**

- `embedding.activate_generation` là một CAS: chỉ đổi con trỏ active khi generation mới đã đủ phủ theo ngưỡng PROVISIONAL trong `contracts/reporting/selection.md`.

**Race, replay và forbidden effects:**

- Report build đang chạy khi generation đổi ⇒ `EMBEDDING_GENERATION_MISMATCH`, build abort/rebuild, report đã publish **không** bị mutate.
- Hai lệnh rebuild đồng thời ⇒ một thắng.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `EMBEDDING_GENERATION_MISMATCH` | selection blocked; giữ vector; không cosine giữa khác dimension/model |
| `VALIDATION_ERROR` | 400 |
| `IDEMPOTENCY_CONFLICT` | rebuild trùng |
| `NOT_FOUND` | generation không tồn tại |
| `STORAGE_WRITE_FAILED` | không ghi vector, không đổi active |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC24
- SC08
- SC49
- SC52

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_embedding_generation_guard.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_generation_activation.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `l-embedding-generation-switch-blocked.json`: hai generation xen kẽ ⇒ selection bị chặn **trước** report commit, 0 phép cosine chéo generation.
- Sau `activate_generation`: mọi vector dùng trong một lần selection có cùng `(model_id, generation, dimension)`.
- Trong lúc rebuild: `report.build` hoặc dùng generation cũ, hoặc trả `EMBEDDING_GENERATION_MISMATCH` — không có đường thứ ba.

**Evidence artifacts:** log pytest; dump `embedding_generation`; đếm phép so sánh chéo generation (phải = 0).

**Yêu cầu live.** Chất lượng ngưỡng tương đồng (REQ-OQ08, A3) cần dữ liệu thật; ngoài phạm vi card.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Ngưỡng tương đồng và ngưỡng phủ đều PROVISIONAL (`contracts/reporting/selection.md`). Không chỉnh số để test pass (SRC-PLAN §14.2). |
| `SG-02` | Nếu thiếu dữ liệu để đánh giá mật độ ⇒ `insufficient_evidence`, **không** gọi là 'đang nổi' (B14). |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-report-coverage-publish-cas` để chứng minh chặn xảy ra trước publish commit.

## §12. Reviewer scope

Reviewer đọc `contracts/reporting/selection.md`, fixture `l` và `m`. Câu hỏi bắt buộc: có phép so sánh nào giữa hai generation lọt qua không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-embedding-generation-switch`
- **Vị trí:** `evidence/runs/TC-embedding-generation-switch/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
