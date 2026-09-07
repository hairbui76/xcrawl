---
card_id: TC-ingest-idempotent-ack-lost
title_vi: Ingest idempotent khi mất ACK
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M1
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-ingest-service]
scenario_refs: [SC07, SC21, SC23, SC31, SC03, SC04, SC49, SC50]
invariant_refs: [I01, I02, I03]
evidence_manifest_id: EVM-TC-ingest-idempotent-ack-lost
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-ingest-idempotent-ack-lost — Ingest idempotent khi mất ACK

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
| `contracts/schemas/ingest-batch.schema.json` | `3c00a33a20da6600e9db10f971d3b646390107201b1800678247e2b7a85d90fc` | 15400 |
| `contracts/schemas/ingest-receipt.schema.json` | `ff5232f46bb08369ea9af653d652d7782a42ea16798992f2507878c964ac537c` | 16970 |
| `contracts/schemas/target.schema.json` | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` | 7283 |
| `contracts/data/identity.md` | `62fd06635c5e29a955f40cc1d56bea9d4dde9d444607fe7c07da5164993468ce` | 20576 |
| `contracts/data/invariants.md` | `9def66cd6e918077a96a730327646c0040acd02a6a4c29135b28e5281e64b36d` | 27782 |
| `contracts/state/run.yaml` | `c92e7c4e6fc6dce8a0280e64a182c1463a1e7a4b07d3c26f8036e37fd34579ec` | 91779 |
| `contracts/state/storage.yaml` | `f67e78f528a13b768b97ab72f55542ac9bac439b8f5472e8e03247b41dae72c2` | 27018 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `277eb556cff950193ca55cecd0ef0d06dca279a4d376c5c8e889a48ebf60c09c` | 5717 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `5ed7b2c429ef7e060140f8b6bbaa71b761b482134aaac155ad32d64bef34b8c0` | 4924 |
| `precode/adr/ADR-0007-timezone-handling.md` | `334abf600467fba70e7797113956c99406acb3617b2da6f3ccce56f8f5786ed7` | 4843 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | `a8e57390663d6dc3778ff8036ca4032a91da25f0b85844bd094f393e34f6b5ef` | 5701 |
| `acceptance/fixtures/identity/README.md` | `a6beae39f431a06104ff797094c79d51b21736a74908271b355bdeb2cf8209e5` | 11369 |
| `acceptance/fixtures/identity/pos-ingest-batch-valid.json` | `c4ad116eaa0434fbdb0cc573b31639e1a66fc963d6a26669e375ae1dae7a3644` | 2237 |
| `acceptance/fixtures/identity/neg-ingest-batch-missing-idempotency-key.json` | `95967e6004574b840029a611323eb9c4d6a5ebaf8df472fb799da68e01b6a405` | 2358 |
| `acceptance/fixtures/identity/neg-ingest-batch-bad-payload-hash.json` | `5a6f14986261f606e84b85cdbb0d7eb1c7e4d872a37c0a03117dce5a32f10261` | 2311 |
| `acceptance/fixtures/identity/neg-ingest-batch-empty-items.json` | `f95cd4a2f67f2389abfedb27585b5afe41cd49700d82f0d0b7ac06646148e11f` | 1778 |
| `acceptance/fixtures/identity/neg-ingest-batch-unknown-field.json` | `10ff2e91f754538f82faf395ca6339a2db81e6397d4d03169bb9ebfd3364d97a` | 2518 |
| `acceptance/fixtures/identity/neg-ingest-batch-timestamp-precision.json` | `5675c24e751ebf70c11f90a7acd2608716e00d7fd3f2dfa7c64b44c87e93567f` | 2408 |
| `acceptance/fixtures/identity/f-ingest-replay-idempotent.json` | `ea3c1b65adf186e6102ed88e61e986e5cb8051f47c51591f89afad2a44f1d996` | 12469 |
| `acceptance/fixtures/collection/d-duplicate-ingest-replay.json` | `1dc4318167004f3d085fff0b402c9c7bf6c220854db3130c51eb5900d85120fe` | 10417 |
| `acceptance/fixtures/collection/b-cursor-invalidated-reread-dedup.json` | `6ea2b75b3690af3a85b218ee8b3b32c9f339f285a86ca0a3a683c206628ec775` | 12816 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/e2e/README.md` | `74790ee8435791e5dbc360cf84a0737f660e2bebcbdb0749cdc1528a669d9ca8` | 6013 |
| `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json` | `a925781ecf2d36e3cd02a3d666819bc5186c8d809e7865e51bac77d387678c00` | 30745 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-ingest-idempotent-ack-lost`
- **Milestone:** M1 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-ingest-service`

**Mục tiêu.** Hiện thực đường ingest của server sao cho một lô post commit đúng một lần dù collector mất ACK và gọi lại: cùng `idempotency_key` + cùng `payload_hash` trả lại receipt đã commit, `payload_hash` khác trả `IDEMPOTENCY_CONFLICT`, và checkpoint không bao giờ trỏ vượt quá dữ liệu đã bền.

**Non-goals.**

- Không viết collector (card `TC-collector-checkpoint-resume`).
- Không viết identity merge (card `TC-canonical-identity-merge`); ở đây chỉ gọi `identity.resolve_target`/`identity.record_alias`.
- Không tạo endpoint mới, không đổi `contracts/schemas/ingest-batch.schema.json`.
- Không viết UI, không viết scheduler.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0001-topology-and-placement.md`, `precode/adr/ADR-0002-run-state-model-split.md`, `precode/adr/ADR-0007-timezone-handling.md`, `precode/adr/ADR-0009-identity-alias-target-union.md`.
3. Hợp đồng nghiệp vụ: `contracts/schemas/ingest-batch.schema.json`, `contracts/schemas/ingest-receipt.schema.json`, `contracts/schemas/target.schema.json`, `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/state/run.yaml`, `contracts/state/storage.yaml`, `contracts/http/openapi.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/identity/README.md`, `acceptance/fixtures/identity/pos-ingest-batch-valid.json`, `acceptance/fixtures/identity/neg-ingest-batch-missing-idempotency-key.json`, `acceptance/fixtures/identity/neg-ingest-batch-bad-payload-hash.json`, `acceptance/fixtures/identity/neg-ingest-batch-empty-items.json`, `acceptance/fixtures/identity/neg-ingest-batch-unknown-field.json`, `acceptance/fixtures/identity/neg-ingest-batch-timestamp-precision.json`, `acceptance/fixtures/identity/f-ingest-replay-idempotent.json`, `acceptance/fixtures/collection/d-duplicate-ingest-replay.json`, `acceptance/fixtures/collection/b-cursor-invalidated-reread-dedup.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/e2e/README.md`, `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/ingest/router.py` | HTTP handler cho `ingest.submit_batch`, `ingest.commit_checkpoint`, `ingest.get_receipt` |
| `server/app/ingest/service.py` | TXN-ingest-batch và TXN-checkpoint-only |
| `server/app/ingest/idempotency.py` | tra receipt theo `assignment_id + batch_idempotency_key`, so `payload_hash` |
| `server/app/ingest/repository.py` | repository port giới hạn đúng bảng của MOD-ingest-service |
| `tests/contract/test_ingest_batch_schema.py` | 6 fixture pos/neg của `ingest-batch.schema.json` |
| `tests/contract/test_ingest_idempotency.py` | replay cùng key, replay khác payload, checkpoint-only |
| `tests/integration/test_ingest_ack_lost.py` | crash sau commit trước ACK; đếm hàng và hash checkpoint |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `ingest.submit_batch`
- `ingest.commit_checkpoint`
- `ingest.get_receipt`
- `ingest.get_checkpoint`

**Consumes** (chỉ được gọi đúng những operation này):

- `identity.resolve_target`
- `identity.record_alias`
- `identity.quarantine_conflict`
- `research.fetch_work_metadata`
- `embedding.generate_vectors`
- `analysis.enqueue_tasks`
- `storage.get_health`

**Schema:**

- request `ingest.submit_batch` → `contracts/schemas/ingest-batch.schema.json`
- response `ingest.submit_batch` / `ingest.get_receipt` → `contracts/schemas/ingest-receipt.schema.json`
- target resolve → `contracts/schemas/target.schema.json`

**State effects.** Commit `post` + `ingest_receipt` + `client_checkpoint_proposal` trong **một** transaction (`TXN-ingest-batch`). ACK chỉ sau commit. `ingest.commit_checkpoint` chỉ dùng cho lô rỗng (`empty_page | end_of_feed | segment_close`, `item_count = 0`) qua `TXN-checkpoint-only`. `discovered_at` do **server** cấp; clock của worker không được tin (ADR-0007).

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-x-collector` — collector_token (bearer `collectorToken`)
- `MOD-job-service` — internal_only, chỉ đọc qua `ingest.get_checkpoint`

**Được phép gọi:**

- MOD-identity-service (internal)
- MOD-research-connector (internal)
- MOD-embedding-service (internal)
- MOD-analysis-service (internal)
- MOD-data-store (repository port)

**Đường bị cấm (denied paths):**

- Không gọi Telegram, không gọi provider AI, không đọc secret của provider (FE/NC trong `contracts/modules.yaml`).
- Collector **không** được ghi SQLite trực tiếp; mọi ghi đi qua operation ở §4.
- Không có network call nào bên trong transaction SQLite (SRC-PLAN §5.1).
- Không mở đường `MOD-x-collector → MOD-analysis-service` (B12/ADR-0001: task phân tích do server phát sau ingest commit).

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
| `I01` | mutation chỉ qua domain port đã xác thực |
| `I02` | receipt chỉ ACK sau commit; `checkpoint.acked_through_ingest_sequence ≤ max(committed ingest_receipt.sequence)` |
| `I03` | một canonical identity → một work; alias conflict không merge đoán |

**Transaction và commit point:**

- `TXN-ingest-batch` — commit point là commit của transaction này; ACK phát sau đó.
- `TXN-checkpoint-only` — chỉ cập nhật `checkpoint` + receipt của lần commit; không có hàng `post`.

**Race, replay và forbidden effects:**

- Replay do mất ACK: cùng key + cùng payload ⇒ receipt cũ, số hàng không đổi.
- Hai lô cùng key khác payload ⇒ `IDEMPOTENCY_CONFLICT`, không ghi đè.
- Lease hết hạn giữa lô ⇒ `STALE_LEASE`/`WORKER_LEASE_EXPIRED`, không commit.
- `storage.health = write_blocked` ⇒ `STORAGE_WRITE_FAILED`, con trỏ không tiến.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `VALIDATION_ERROR` | 400, không ghi một phần nào; `item_count ≠ 0` ở checkpoint-only cũng rơi vào đây |
| `UNAUTHORIZED` | 401, token không hợp lệ hoặc sai cạnh |
| `STALE_LEASE` | không ghi; checkpoint giữ nguyên giá trị đã commit |
| `WORKER_LEASE_EXPIRED` | assignment bị thu hồi; worker cũ không commit được |
| `IDEMPOTENCY_CONFLICT` | không ghi đè; trả receipt cũ chỉ khi payload trùng |
| `INGEST_ACK_LOST` | client uncertain; server giữ receipt nếu đã commit; retry phải tra `ingest.get_receipt` trước |
| `IDENTITY_CONFLICT` | target vào quarantine; không merge đoán; post vẫn giữ |
| `STORAGE_WRITE_FAILED` | `storage.write_blocked`; không ACK, không tiến cursor, không tuyên bố đã persist lỗi |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC07
- SC21
- SC23
- SC31
- SC03
- SC04
- SC49
- SC50

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_ingest_batch_schema.py -q` (PROVISIONAL)
- `python -m pytest tests/contract/test_ingest_idempotency.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_ingest_ack_lost.py -q` (PROVISIONAL)
- `python3 evidence/tools/e0_check.py` — E0 lint do PC09 cung cấp; hiện `NOT_RUN`

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Sau replay: `COUNT(post)` và `COUNT(ingest_receipt)` không đổi; hash receipt bằng lần đầu.
- `checkpoint.acked_through_ingest_sequence ≤ max(ingest_receipt.sequence)` đúng sau **mọi** dãy lời gọi.
- 5 fixture `neg-ingest-batch-*` đều trả `VALIDATION_ERROR` và **0 hàng** được ghi.
- `discovered_at` trong receipt do server cấp, khác `published_at` của X.

**Evidence artifacts:** log pytest đã che secret; dump `COUNT(*)` trước/sau replay; hash của receipt JSON.

**Yêu cầu live.** Không cần live. E1/E2 bằng fixture và fault injection là đủ cho card này.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Nếu `identity.resolve_target` chưa có (card 2 chưa xong) ⇒ card này chỉ đi tới E1 với stub theo `contracts/schemas/target.schema.json`; **không** tự viết logic merge. |
| `SG-02` | `CR-PC02-12` (diễn giải append-only của `TXN-checkpoint-only`) còn OPEN. Nếu implementation cần UPDATE tại chỗ ⇒ DỪNG, đó là đổi mô hình bảng. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- Không phụ thuộc card nào để bắt đầu.
- `TC-canonical-identity-merge` để đạt claim đầy đủ ở nhánh IDENTITY_CONFLICT.
- `TC-storage-write-blocked-readiness` cho nhánh `STORAGE_WRITE_FAILED`.

## §12. Reviewer scope

Reviewer đọc: `contracts/ports.yaml` (4 operation), `contracts/schemas/ingest-*.schema.json`, `contracts/data/invariants.md` §I02, 10 fixture ở §2. Reviewer **không** cần đọc UI, Telegram hay AI. Câu hỏi review bắt buộc: sau replay, số hàng có đổi không, và checkpoint có vượt post bền không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-ingest-idempotent-ack-lost`
- **Vị trí:** `evidence/runs/TC-ingest-idempotent-ack-lost/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
