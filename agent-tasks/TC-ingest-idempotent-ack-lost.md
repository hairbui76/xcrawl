---
card_id: TC-ingest-idempotent-ack-lost
title_vi: Ingest idempotent khi mất ACK
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M1
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
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

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-OD01c-20260907`** (thay `PC10-PIN-OD01b-20260907`; các epoch cũ hơn: `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). Bản pin sau wave lan truyền hậu A2-R5 (`FIX-R5-rulings.md`): phạm vi `data.purge_all` đã phê chuẩn được chép nhất quán vào mọi artefact, và hai thư mục fixture `identity/`, `reporting/` lên `CONTRACT_READY`. Hash dưới đây tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG (`precode/change-control.md` §5, `INV-06`/`INV-09`).

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/baseline.json` | `e0405a1bc36f3dc2050ca7ed3b8acd8a9d0a14a708583cba273360c0c4d6722b` | 100474 |
| `precode/decision-register.md` | `1883fec33f56873a426394a99d3fc6c5ec43c456a936c52733cad6c047f06262` | 102430 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `d95784bf5f67a332597b7ac4ef60a34b13d807b087d3ced9fdc46fba83c0cba5` | 46995 |
| `contracts/data/entities.yaml` | `766fe760bf487781a0b75f070d21960d84d52bccff0465fdaac65dd6ad140ce7` | 228394 |
| `contracts/schemas/ingest-batch.schema.json` | `8ab444f557645ee85dbd0951af7261ac4355d3a0b8ca6b96d8450c9e1a5ae690` | 15986 |
| `contracts/schemas/ingest-receipt.schema.json` | `ff5232f46bb08369ea9af653d652d7782a42ea16798992f2507878c964ac537c` | 16970 |
| `contracts/schemas/target.schema.json` | `d1ce487d2e4ba24b094f702b38a5fcac517443981fe8faea36472089124dc0fd` | 8915 |
| `contracts/data/identity.md` | `71fedc7f6996f5eebace1a53ec42b19bb16f0df4489d93a906e5c895bbb4f4fd` | 20610 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` | 95222 |
| `contracts/state/storage.yaml` | `a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849` | 29908 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `70fcac8f9c7fdcdce84889015d31f109d423d1d15d68116165e9e3d0612399f8` | 5368 |
| `precode/adr/ADR-0007-timezone-handling.md` | `fbb464c22df45248895107a3f38e85f700e9cdecd9a722eaa9f2a4b028995e44` | 5287 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | `67844f12e4fe77a6a25b443a8fe84d053fbcfc9c30649296f55efc41befa4ee1` | 6145 |
| `acceptance/fixtures/identity/README.md` | `ce9ec21ec1cebe8a257a677e67097f1883a35c403b4421d3219862d185335e14` | 12611 |
| `acceptance/fixtures/identity/pos-ingest-batch-valid.json` | `00886301c74078211be6720d3c6ec620a0a6355534cd58e73ce267073a0178f9` | 4047 |
| `acceptance/fixtures/identity/neg-ingest-batch-missing-idempotency-key.json` | `a6424d8023a43ae94457a3dc77f551b91252daa1da8d2ce9d35f2c2d434b384c` | 4151 |
| `acceptance/fixtures/identity/neg-ingest-batch-bad-payload-hash.json` | `d52521fa8a72dcab4631e49d99dee5112d97c499f19b2c801335a138042a9f08` | 4059 |
| `acceptance/fixtures/identity/neg-ingest-batch-empty-items.json` | `bc0d2deb84b51e3a254113470a1de07324086a56e88d467af1973c9c9e8fa227` | 3534 |
| `acceptance/fixtures/identity/neg-ingest-batch-unknown-field.json` | `c57bdd621e1ca75dba3888458ce29c29f972ee6b320fefe0f167acf7e8d17020` | 4370 |
| `acceptance/fixtures/identity/neg-ingest-batch-timestamp-precision.json` | `39a5c2deab2a7f215d48bfb7c1d6b0590da103ac0b6f4bc5e00c5492dd204151` | 4166 |
| `acceptance/fixtures/identity/f-ingest-replay-idempotent.json` | `27839c63e322c1dbdd9fbe98a7d98acc2cd37fa1d1a66f8a9f66ac36aa73a32b` | 14386 |
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

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

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

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

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

**Phạm vi đã phê chuẩn** (`OD-20260907-01`). Read set của card này nằm trong bốn phạm vi mà A2-R4 xác định đủ điều kiện — *ranh giới và quyền*, *dữ liệu và định danh*, *workflow và trạng thái*, *báo cáo và thời gian* — và không chạm `contracts/ai/`, `contracts/telegram/`, hay bất kỳ file `contracts/ops/` nào ngoài `deployment.md` (file này đã lên `CONTRACT_READY` ở PC01-FIX13). 17 blocker B01–B17 nay là `RATIFIED`, nên điểm dừng dạng *"B0x còn PROVISIONAL"* đã gỡ khỏi §10.

  **Nhưng nền hợp đồng CHƯA đồng nhất `CONTRACT_READY`.** 2 file hợp đồng trong read set của card này vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW` trong chính header của nó: `contracts/http/openapi.yaml`, `contracts/schemas/ingest-receipt.schema.json`. Vì vậy **không** được đọc mục này là "mọi hợp đồng đã sẵn sàng"; hãy đọc là "phạm vi nghiệp vụ đã được phê chuẩn, và 2 file còn lại phải lên `CONTRACT_READY` trước khi claim của card vượt quá `IMPLEMENTATION_VERIFIED`". Kiểm lại bằng `grep -h claim_ceiling <file>` — đừng tin dòng này.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Nếu `identity.resolve_target` chưa có (card 2 chưa xong) ⇒ card này chỉ đi tới E1 với stub theo `contracts/schemas/target.schema.json`; **không** tự viết logic merge. |
| `SG-02` | `CR-PC02-12` (diễn giải append-only của `TXN-checkpoint-only`) còn OPEN. Nếu implementation cần UPDATE tại chỗ ⇒ DỪNG, đó là đổi mô hình bảng. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
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
