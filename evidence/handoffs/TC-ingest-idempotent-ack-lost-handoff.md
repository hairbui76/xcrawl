---
handoff_id: TC-ingest-idempotent-ack-lost-handoff
packet_id: TC-ingest-idempotent-ack-lost
worker_principal: worker-WI
authority_id: AUTH-COORD-TC-INGEST
parent_authority: AUTH-OWNER-20260907-03
lease_id: LEASE-TC-INGEST-e1
decision_refs: [B05, B06, B12, B15, AMD-B05, ADR-0001, ADR-0002, ADR-0007, ADR-0009, ADR-0011, R-01, R5-01]
invariant_refs: [I01, I02, I03, I10]
scenario_refs: [SC03, SC04, SC07, SC21, SC23, SC31, SC49, SC50]
requirement_refs: [REQ-AC03, REQ-AC04, REQ-AC07, REQ-D08, REQ-D17, REQ-D33, REQ-P0-03, REQ-P0-12]
evidence_manifest_id: EVM-TC-ingest-idempotent-ack-lost
next_actor: Coordinator
lease_released_at: 2026-09-07T10:35Z
---

# HANDOFF — TC-ingest-idempotent-ack-lost (Giai đoạn 1, M1, cổng G5)

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `TC-ingest-idempotent-ack-lost` |
| `worker_principal` | `worker-WI` |
| `authority_id` | `AUTH-COORD-TC-INGEST` (parent `AUTH-OWNER-20260907-03`) |
| `lease_id` | `LEASE-TC-INGEST-e1` (exclusive, message-tracked; hết hạn 2026-09-08T12:00Z) |
| **`status`** | **`DONE_WITH_CONCERNS`** |
| `completion_claim` | mọi test của card §8 đã chạy thật và xanh; nhưng **không** tự khai `IMPLEMENTATION_VERIFIED`: đó là nhãn Coordinator/Auditor cấp. `evidence/manifest.schema.json` giới hạn một bản ghi `SELF_VALIDATION` ở `CONTRACT_READY`, nên manifest **cố ý bỏ trống** `claim.supports_label` thay vì khai một nhãn mà lần tự kiểm không chống đỡ được (xem `CR-TC-ingest-06`). |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T10:35Z |

**Vì sao `DONE_WITH_CONCERNS` chứ không phải `DONE`.** Sáu change request mở (mục 6), trong
đó hai chạm hợp đồng (`CR-TC-ingest-02`, `CR-TC-ingest-05`) và một chạm chính trần claim của
card (`CR-TC-ingest-06`). Không cái nào được tự sửa: hợp đồng, fixture và oracle là read-only
với card này.

**Vì sao không phải `STALE_BASELINE`.** `§0` của card được tái phát hành **hai lần** trong
lúc gói này chạy (epoch `PC10-PIN-OD01e` → `PC10-PIN-P1` → `PC10-PIN-P1b-20260907`). Bảng pin
hiện hành được kiểm lại bằng máy ngay trước handoff: **37/37 dòng khớp cả hash lẫn byte
count**, và `SRC-SPEC`/`SRC-PLAN` khớp ở đầu phiên **và** trước handoff. Chi tiết ở mục 3.

## 2. Changes — mọi file đã tạo hoặc sửa

Tất cả `CREATE` với baseline `ABSENT`, trừ dòng cuối (`MODIFY`, một khối include có ranh giới).

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/ingest/idempotency.py` | CREATE | ABSENT | `a0d088ad3938d8bfb42aa0730ac1fbc4c39b0a245de91d0cd63fca8c135af691` | 6703 |
| `server/app/ingest/repository.py` | CREATE | ABSENT | `c4e971d03b613bf42d91879a4220542429c5b1a46c4d3b61a7dd1f1933a13fc4` | 16303 |
| `server/app/ingest/router.py` | CREATE | ABSENT | `3aaf85fc93d19decfb80d6ba1edd309b53b466eae26c06ab670ce402fa209776` | 11867 |
| `server/app/ingest/service.py` | CREATE | ABSENT | `6e22df31df9ba40188d86d89d1e3b6648c42e821952dd014a1f48f027644108a` | 45504 |
| `server/migrations/versions/0003_tc_ingest_idempotent_ack_lost.py` | CREATE | ABSENT | `8ecfcc8038762b6d47e413ecd0a7e339a48228c75719ab40880a39570f7ae802` | 7751 |
| `tests/contract/test_ingest_batch_schema.py` | CREATE | ABSENT | `d5ee349da78eef50a3eca66f065269d5ff62caffee897a3844aa74e4111aa669` | 9444 |
| `tests/contract/test_ingest_idempotency.py` | CREATE | ABSENT | `a80306638f7fe657056c8622b7a428384a14622db8794c9b1b1a81af4029cb37` | 21199 |
| `tests/integration/test_ingest_ack_lost.py` | CREATE | ABSENT | `894be724c63850466ff260fc750ad991154c62d1f5098c0f0457f99519562718` | 26094 |
| `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json` | CREATE | ABSENT | `b93b6e4fc73df3ce80a517f28098564659b3365fc4587bcce4ab2c9720fd29ad` | 14467 |
| `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md` | CREATE | ABSENT | *(chính file này)* | — |
| `server/app/main.py` | MODIFY | *(bản của TC-storage-write-blocked-readiness, đã sửa bởi hai card khác trước tôi)* | `adfcde38ab8191ed54ad088a8c6d33550a009a2b06026371ce3838867db0bd44` | 8014 |

### 2.1 Sửa `server/app/main.py`

Đúng **một** khối include, có ranh giới rõ, thêm vào cuối chuỗi include đã có, theo Phase 1
dispatch mục 2. Không dòng nào khác của file bị chạm:

```
    # --- BEGIN include: TC-ingest-idempotent-ack-lost (MOD-ingest-service) -------------
    from server.app.ingest.router import install_ingest_error_handlers
    from server.app.ingest.router import router as ingest_router

    install_ingest_error_handlers(app)
    app.include_router(ingest_router)
    # --- END include: TC-ingest-idempotent-ack-lost ------------------------------------
```

`app.state.ingest_context` và `app.state.collector_token` **không** được đặt mặc định ở đây:
router từ chối (500 `INTERNAL` cho context thiếu, 401 `UNAUTHORIZED` cho token thiếu) thay vì
tự dựng một kết nối DB hay chấp nhận mọi collector. Baseline "before" của file này là bản do
`TC-owner-auth-session` và `TC-storage-write-blocked-readiness` để lại; tôi không có bản chụp
byte ngay trước lần ghi của mình và không khai một con số mình không đo được.

### 2.2 Đổi tên revision migration (đáp lại chỉ đạo của Coordinator)

File `server/migrations/versions/0002_tc_ingest_idempotent_ack_lost.py` do chính tôi tạo ở
đầu phiên đã bị **xoá** và thay bằng `0003_tc_ingest_idempotent_ack_lost.py`. Hai lý do, cả
hai đến từ việc các card khác đổ bộ song song:

1. `0002_base_entities` (do `TC-canonical-identity-merge` viết) **đã tạo `post`**. Bản 0002
   của tôi cũng tạo `post` ⇒ hai định nghĩa của một bảng trên cùng một chuỗi migration. Bản
   0003 **chỉ** tạo `ingest_receipt` và `checkpoint`, và chạy **sau** `0002_base_entities`.
2. Ba card cùng phân nhánh từ `0001`, nên `alembic heads` báo **ba head** và
   `alembic upgrade head` từ chối chạy. Revision của tôi nay là **merge point**:
   `down_revision = ("0003_tc_canonical_identity_merge", "0002_tc_owner_auth_session")`.
   Sau thay đổi này `alembic heads` báo **đúng một head**, và `alembic upgrade head` chạy sạch
   trên một DB trắng qua cả năm revision (bằng chứng `EV-WI-04`).

Phụ thuộc thật là nhánh identity (nó tạo `post`); phụ thuộc lên nhánh auth **chỉ là thứ tự**,
vô hại vì hai nhánh không chạm bảng chung. Nếu Coordinator muốn một file merge riêng thay vì
merge-point kiểu này thì đó là packet khác — tôi không tạo file ngoài write set.

## 3. Source baseline đã dựa vào

| Ref | Path | SHA-256 | Kiểm |
| --- | --- | --- | --- |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp đầu phiên **và** trước handoff |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp đầu phiên **và** trước handoff |

**Bảng pin §0 của card (37 dòng):** kiểm bằng máy ngay trước handoff, **0 lệch** trên cả hash
lẫn byte count, ở epoch `PC10-PIN-P1b-20260907`.

Lịch sử drift trong phiên, ghi lại vì nó là tín hiệu thật chứ không phải nhiễu:

* Lúc bắt đầu (epoch `PC10-PIN-OD01e`), **ba** file pin lệch: `ADR-0011`, `precode/baseline.json`,
  `precode/decision-register.md` — đúng bộ ba mà `CR-P0-01` của `P0-skeleton-handoff` đã báo.
  Card được tái phát hành với hash mới trong lúc tôi đang đọc, và bảng khớp lại.
* Trước handoff, `ADR-0011` lệch **lần nữa**; card lại được tái phát hành
  (`PC10-PIN-P1b-20260907`, ghi nhận `PKT-PC00-FIX17` thi hành `CR-PC10-09`) và khớp.

Cả hai lần lệch đều nằm ở file **ghi chép** (ADR toolchain, baseline.json, decision register),
không ở hợp đồng nghiệp vụ nào mà oracle của card dựa vào: `contracts/**` và
`acceptance/fixtures/**` giữ nguyên byte suốt phiên.

Read set khác đã đọc đủ: `contracts/ports.yaml` (4 operation ingest + 4 operation consume),
`contracts/schemas/ingest-batch.schema.json`, `contracts/schemas/ingest-receipt.schema.json`,
`contracts/schemas/target.schema.json`, `contracts/data/entities.yaml`
(`ENT-post`, `ENT-ingest-receipt`, `ENT-checkpoint`, `TXN-ingest-batch`, `TXN-checkpoint-only`,
`conventions`), `contracts/data/invariants.md` §I02, `contracts/data/identity.md`,
`contracts/modules.yaml` (36 `forbidden_edges`, 36 `denied_cases`, bảng R5-01),
`contracts/errors.yaml` (qua `rr_contracts.generated.errors`), `contracts/state/storage.yaml`,
`contracts/state/run.yaml`, `contracts/http/openapi.yaml` (3 path `/v1/ingest/*`,
`ErrorEnvelope`, `securitySchemes`), 4 ADR nghiệp vụ + `ADR-0011`, 9 fixture bắt buộc,
`evidence/manifest.schema.json`, `README.md`, `evidence/handoffs/P0-skeleton-handoff.md`,
`agent_profile/worker.md`, và hai packet điều phối.

## 4. Evidence records — tất cả `SELF_VALIDATION`

Mọi lệnh chạy ở `/mnt/virtual/repo/xcrawl` với `PYTHONDONTWRITEBYTECODE=1`. Không lệnh nào
chạm mạng (kể cả `uv` — môi trường đã cài sẵn từ Giai đoạn 0). Không secret nào tồn tại trong
repo; `collector_token` trong test là một chuỗi test tự khai, không phải credential.

| ID | Loại | Lệnh chính xác | Kết quả |
| --- | --- | --- | --- |
| `EV-WI-01` | E1 contract | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" -W ignore::DeprecationWarning tests/contract/test_ingest_batch_schema.py` | **PASS**, 14 passed, exit 0 |
| `EV-WI-02` | E1 contract | `… tests/contract/test_ingest_idempotency.py` | **PASS**, 12 passed, exit 0 |
| `EV-WI-03` | E1+E2 integration | `… tests/integration/test_ingest_ack_lost.py` | **PASS**, 15 passed, exit 0 |
| `EV-WI-04` | E0 migration | `cd server && RR_DATABASE_URL=<tmp> uv run alembic heads` rồi `… alembic upgrade head` trên DB trắng | **PASS**: `0003_tc_ingest_idempotent_ack_lost (head)` — một head; upgrade chạy hết 5 revision, exit 0 |
| `EV-WI-05` | E0 lint/type | `uv run ruff check .` · `uv run ruff format --check .` · `uv run mypy` | **PASS**: `All checks passed!` · `58 files already formatted` · `Success: no issues found in 24 source files` |
| `EV-WI-06` | E1 toàn cây | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" -q` | **1 failed, 261 passed, 4 xfailed** — xem mục 4.1 |
| `EV-WI-07` | E0 baseline | `sha256sum -c` trên 37 dòng pin §0 + 2 nguồn | **PASS**, 0 lệch |
| — | E0 (PC09) | `python3 evidence/tools/e0_check.py` | **NOT_RUN** — card §8 nói PC10 không chạy nó |
| — | E3 live | — | **NOT_RUN** — card §8: không cần live |

Ba lệnh của card §8 (`python -m pytest tests/contract/test_ingest_batch_schema.py -q`,
`… test_ingest_idempotency.py -q`, `… tests/integration/test_ingest_ack_lost.py -q`) được chạy
dưới dạng `uv run pytest` theo `ADR-0011`/`Makefile` — cùng interpreter, cùng file, chỉ khác
cách gọi. `-o addopts=""` được thêm **chỉ để in ra dòng đếm**: `addopts` của repo có `-q`, nên
cộng thêm `-q` nữa thành `-qq` và pytest giấu tổng số.

**Tổng của card: 41 passed, 0 failed, 0 xfailed, 0 skipped, exit 0.**

Không test nào của card bị `xfail`. Kế hoạch dự phòng "xfail(reason='pending TC-…')" cho
identity **không cần dùng**: `server/app/identity/service.py` đã có mặt lúc chạy, nên nhánh
identity được kiểm thật qua port thật (`test_a_post_linked_to_a_known_work_resolves_to_that_target`
vẫn giữ `pytest.importorskip(..., reason="pending TC-canonical-identity-merge")` để nó tự
chuyển thành skip nếu card kia bị rút). Tương tự với storage: `server/app/storage/guard.py`
đã có, nên nhánh `write_blocked` được kiểm bằng `StorageGuard` thật chứ không phải giả.

### 4.1 Lỗi duy nhất của toàn cây — không thuộc card này

`server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0` FAIL: nó khẳng định
`GET /v1/health/readiness` trả 404, nay trả 401 vì `TC-storage-write-blocked-readiness` đã
đăng ký route đó trong `create_app`. Đây là một smoke test của Giai đoạn 0 nay đã lỗi thời,
không phải hồi quy của ingest: include của tôi chỉ thêm ba route `/v1/ingest/*`. Tôi **không**
sửa nó — `server/tests/test_smoke.py` nằm ngoài write set. Chủ sở hữu: card readiness hoặc một
packet dọn dẹp của Coordinator.

## 5. Checklist của card

| Mục card | Trạng thái | Ở đâu |
| --- | --- | --- |
| §3 `server/app/ingest/router.py` — 3 HTTP handler | **DONE** | `POST /v1/ingest/batches`, `POST /v1/ingest/checkpoints`, `GET /v1/ingest/receipts/{idempotency_key}`; `ingest.get_checkpoint` **cố ý không** có route (transport `internal`), có test khẳng định điều đó |
| §3 `server/app/ingest/service.py` — TXN-ingest-batch + TXN-checkpoint-only | **DONE** | mỗi transaction là đúng một `with ctx.engine.begin()`; commit point được nêu tên trong docstring của `submit_batch` và `commit_checkpoint`; response dựng **sau** khi block thoát |
| §3 `server/app/ingest/idempotency.py` | **DONE** | tra receipt theo `(owner_id, idempotency_key)`, so `payload_hash`, ba hàm hash JCS |
| §3 `server/app/ingest/repository.py` | **DONE** | đúng 3 bảng; `count_rows` **từ chối** mọi tên bảng khác; không mở/commit transaction |
| §3 ba file test | **DONE** | 41 test, 0 skip cho scenario P0 |
| §4 produces 4 operation | **DONE** | tên hàm lấy từ `ports.yaml` operation id |
| §4 consumes | **PARTIAL** | `identity.resolve_target` (read-only) và `storage.get_health`/`assert_writable` được gọi thật. `identity.record_alias`, `identity.quarantine_conflict`, `research.fetch_work_metadata`, `embedding.generate_vectors`, `analysis.enqueue_tasks` **chưa gọi** — xem mục 5.1 |
| §5 default deny + bảng R5-01 | **DONE** cho cạnh chạm module này | principal sai ⇒ `UNAUTHORIZED` 401 (3 biến thể: không credential, sai token, cookie owner), có test; không có lời gọi Telegram/AI/secret ở đâu trong package; không network trong transaction |
| §6 I01/I02/I03 | **DONE** cho I01, I02; **PARTIAL** cho I03 | I02 có oracle đếm hàng + hash + bất đẳng thức con trỏ, khẳng định sau **mọi** sự kiện. I03 chỉ tới mức resolve read-only |
| §7 nghĩa vụ mã lỗi | **DONE** trừ hai mã | `VALIDATION_ERROR`, `UNAUTHORIZED`, `STALE_LEASE`, `WORKER_LEASE_EXPIRED`, `IDEMPOTENCY_CONFLICT`, `STORAGE_WRITE_FAILED` đều có test. `INGEST_ACK_LOST` **không phải response của server** (openapi `x-error-codes-reported-not-returned`) nên được kiểm bằng đúng quy trình của nó (`get_receipt` → replay). `IDENTITY_CONFLICT` xuất hiện trong `receipt.warnings` của 2xx — có đường mã, **chưa có oracle** |
| §8 4 lệnh | **3 DONE, 1 NOT_RUN** | `e0_check.py` NOT_RUN theo chính card |
| §8 oracle | **DONE** | 5/5 gạch đầu dòng có assertion đo được; không oracle nào đọc log |
| §13 evidence manifest | **DONE** | `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json`, validate sạch (0 lỗi) với `evidence/manifest.schema.json` |
| §13 đăng ký vào `evidence/index.json` | **NOT_DONE** | file của PC09, ngoài write set. Việc của Coordinator |

### 5.1 Phạm vi đã hiện thực và phạm vi cố ý bỏ ngỏ

**Đã hiện thực đầy đủ:** hai transaction, bốn operation, guard cursor của R-01, clock clamp
(`CR-PC04-03`), cấp `ingest_sequence` đơn điệu theo owner, dedup theo `x_post_id`, ghi đơn điệu
`source_deleted_observed_at`, envelope lỗi 7 trường với `correlation_id` sinh trong bộ nhớ,
xác thực `collectorToken` so sánh hằng thời gian, và ba header bắt buộc của openapi.

**Cố ý bỏ ngỏ (không phải quên):**

* **Alias và work linking.** Card §1 nói rõ non-goal là "không viết identity merge; ở đây chỉ
  gọi `resolve_target`/`record_alias`". Tôi gọi `resolve_target` (`mutation: false`) nhưng
  **không** gọi `record_alias`: tạo `work` + `identity_alias` + `post_work` mới là đúng phần
  logic mà `TC-canonical-identity-merge` sở hữu, và gọi nó từ đây sẽ ghi vào bảng của card
  khác dưới lease của tôi. Hệ quả đo được: `counts.works_linked` **luôn = 0**, và một post
  không khớp alias nào có sẵn được lưu `identity_resolution = 'pending'` — nghĩa là "chưa
  giải", không phải "chỉ có post" và không phải "đã liên kết". Không đoán (REQ-D33, B15).
* **`counts.quarantined` luôn = 0.** Không có đường nào trong card này tạo quarantine — xem
  `CR-TC-ingest-05`, mâu thuẫn hợp đồng khiến giá trị > 0 không biểu diễn được.
* **Kiểm lease chỉ chạy khi có cổng.** Không có `TC-scheduler-lease-claim` thì không có bảng
  `assignment_lease` để hỏi. Service nhận một cổng đọc tùy chọn; khi không có, kiểm lease
  **không chạy** và caller phải cấp `run_id`. Điều này được ghi trong docstring chứ không
  giấu, và test dùng một cổng giả để kiểm cả `STALE_LEASE` lẫn `WORKER_LEASE_EXPIRED`.

### 5.2 Quyết định kỹ thuật cần Coordinator biết

1. **Server tự tính lại `payload_hash` và từ chối khi lệch** (`VALIDATION_ERROR`,
   `violation_kind = payload_hash_mismatch`). Hợp đồng định nghĩa `payload_hash` là một **hàm**
   của `payload_core`; nếu server nhận một hash nó chưa kiểm thì toàn bộ bảo đảm idempotency
   nằm ở phép tính của client, và hai lô khác nhau có thể được ép trùng hash. Đây là **thi
   hành** hợp đồng, không phải thêm mã lỗi mới — nhưng nó là một cửa từ chối mà card không
   liệt kê tường minh, nên tôi báo ra đây.
2. **Khoá idempotency của `ingest.commit_checkpoint`** được lưu là `"{assignment_id}:{checkpoint_seq}"`
   theo `ports.yaml` (`assignment_id + checkpoint_seq`), **không** lấy từ header
   `Idempotency-Key`. Fixture `b-cursor-invalidated-reread-dedup` để header là
   `ckpt-2026-09-07-0002-aaaa` trong khi `receipt.idempotency_key` của chính nó là
   `batch-2026-09-07-0001-aaaa` — hai giá trị không nhất quán trong cùng một sự kiện, nên tôi
   theo `ports.yaml` là nguồn chuẩn về phạm vi khoá.
3. **Khoá ngoại hoãn (`DEFERRABLE INITIALLY DEFERRED`)** giữa `ingest_receipt.checkpoint_id` và
   `checkpoint.created_by_receipt_id`. Hai hàng tham chiếu vòng và được ghi trong **một**
   transaction; chỉ khi kiểm tại COMMIT thì "rows written together" của `TXN-ingest-batch` mới
   trở thành thứ SQLite ép được, và một lần ghi nửa vời sẽ **fail đúng ở commit point** thay vì
   được nhận.
4. **`recovery_required` KHÔNG chặn ingest.** `contracts/state/storage.yaml` liệt kê tường minh
   nhóm operation mà trạng thái đó từ chối (`worker_claim`, `dispatch`, `publish`,
   `schedule_enqueue`) và ingest không nằm trong đó; hơn nữa `worker_claim` bị chặn nên không
   lease nào tồn tại để mà ingest. Tôi để `StorageGuard` quyết định — service chỉ dịch
   `StorageRefused` sang envelope, không tự chọn trạng thái nào chặn cái gì.
5. **HTTP 422 cho `VALIDATION_ERROR`**, theo openapi, không phải 400 như bảng §7 của card
   (`CR-TC-ingest-04`).

## 6. Change requests và unresolved refs

| ID | Nội dung | Bằng chứng | Ảnh hưởng |
| --- | --- | --- | --- |
| `CR-TC-ingest-01` | `entities.yaml` yêu cầu `post.ingest_receipt_id -> ingest_receipt(id)`, `post.owner_id -> owner(id)`, `post.discovered_by_run_id -> run(id)`, `ingest_receipt.run_id -> run(id)`, `ingest_receipt.lease_id -> assignment_lease(id)`. `0002_base_entities` để `post.ingest_receipt_id` và `post.discovered_by_run_id` là **cột trần**, và `run`/`assignment_lease` chưa tồn tại. SQLite **không** thêm được khóa ngoại vào bảng đã có nếu không dựng lại bảng 12 bước — mà `post` là bảng của card khác. | `0002_base_entities` docstring nói "the ingest card adds the constraint"; tôi không dựng lại bảng của card khác | Ràng buộc tham chiếu của I02 hiện **chỉ** được ép giữa `ingest_receipt` ↔ `checkpoint`. Cần một revision phối hợp do Coordinator giao. |
| `CR-TC-ingest-02` | `acceptance/fixtures/identity/f-ingest-replay-idempotent.json` khai `given.rows.post` có 3 hàng cùng `ingest_receipt: []` và `checkpoint: []`. Trạng thái đó **không tồn tại được**: `ENT-post.ingest_receipt_id` là NOT NULL + FK tới `ingest_receipt`. Fixture mâu thuẫn với chính `entities.yaml` mà nó khai là dependency. | so `given.rows` với `ENT-post.fields` | Tôi **không** sửa fixture. Test tạo 3 post đó bằng một `ingest.submit_batch` sớm hơn — đường duy nhất chúng có thể tồn tại thật. Hệ quả: số thứ tự tuyệt đối 91..93 / 100 của fixture là minh hoạ; **mọi** oracle quan hệ (đếm hàng, 7+3+0=10, hash bằng nhau, bất đẳng thức con trỏ) vẫn được khẳng định nguyên vẹn. |
| `CR-TC-ingest-03` | `ports.yaml → ingest.commit_checkpoint.request_summary_vi` bắt buộc trường `item_count: 0`, nhưng `ingest-receipt.schema.json#/$defs/checkpoint_only_request` đặt `additionalProperties: false` và **không khai** `item_count`. Hai hợp đồng không thể cùng đúng. | đọc cả hai | Tôi theo wire schema: body mang `item_count` bị từ chối như trường lạ ⇒ `VALIDATION_ERROR`, thoả nghĩa vụ §7 cho **mọi** giá trị. Có test. |
| `CR-TC-ingest-04` | Card §7 ghi `VALIDATION_ERROR` = **400**; `contracts/http/openapi.yaml` ghi **422** cho cả ba route `/v1/ingest/*`. | so card §7 với `paths./v1/ingest/batches.responses` | Tôi theo openapi (422). Nếu card đúng thì openapi phải sửa, và ngược lại. |
| `CR-TC-ingest-05` | `ingest-receipt.schema.json` bắt buộc `counts.quarantined` và khai bất biến `received = inserted + deduplicated + quarantined + rejected`; `ENT-ingest-receipt` **không có cột** `quarantined` và khai `CHECK (posts_inserted + posts_duplicate + items_rejected = items_received)`. Khi `quarantined > 0` hai ràng buộc **không thể** cùng đúng. | so `counts` của schema với `fields` của `ENT-ingest-receipt` | Chưa cắn vào card này vì đường quarantine chưa tới được (identity merge ngoài scope), nên tôi hiện thực đúng cột của `entities.yaml` và phát `quarantined: 0` ra wire. **Trước khi** ai đó hiện thực quarantine, một trong hai hợp đồng phải sửa. |
| `CR-TC-ingest-06` | `evidence/manifest.schema.json` chặn `review_type: SELF_VALIDATION` khỏi `claim.supports_label` ≥ `IMPLEMENTATION_VERIFIED`; nhưng card §9 đặt trần chính là `IMPLEMENTATION_VERIFIED` và Worker chỉ được tự kiểm. Không có đường nào để một Worker chống đỡ trần của chính card mình. | `allOf` nhánh 7 của schema | Manifest bỏ trống `supports_label` và liệt kê `not_established_vi`. Cần Coordinator/Auditor cấp nhãn, hoặc PC09 nới schema. |
| *(quan sát, không phải CR)* | `server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0` FAIL toàn cây, do card readiness đăng ký `/v1/health/readiness`. | mục 4.1 | Ngoài write set; không sửa. |
| *(quan sát)* | Card §9 vẫn nói `contracts/http/openapi.yaml` và `contracts/schemas/ingest-receipt.schema.json` còn khai `claim_ceiling: DRAFT_FOR_REVIEW`. Kiểm lại bằng `grep -h claim_ceiling`: **vẫn đúng** — `ingest-receipt.schema.json` là `DRAFT_FOR_REVIEW`. | `grep` | Trần claim của card không được vượt `IMPLEMENTATION_VERIFIED` cho tới khi hai file đó lên `CONTRACT_READY`. |

Không có `OWNER_DECISION_REQUIRED` mới. Không blocker sản phẩm nào được quyết trong gói này.

## 7. Stop gate — đối chiếu

| Gate | Kết quả |
| --- | --- |
| `SG-HASH` | **Không trigger** ở thời điểm handoff: 37/37 pin khớp. Có drift giữa phiên, đã ghi ở mục 3; card được tái phát hành cả hai lần. |
| `SG-01` (identity chưa có) | **Không trigger**: `identity/service.py` đã có, gọi qua port thật với chữ ký thật; không viết logic merge nào trong package của tôi. |
| `SG-02` (`CR-PC02-12`, append-only) | **Không trigger**: checkpoint là append-only, không UPDATE tại chỗ; có test so tập `(id, sequence, acked_through)` trước/sau. |
| `SG-STACK` | **Không trigger**: framework do `ADR-0011` nêu tên (FastAPI, SQLAlchemy 2 Core, Alembic, pytest); tôi không chọn thư viện nào mới. |
| `SG-PC09` | `acceptance/scenarios.yaml` đã đọc bản mới nhất; **không** thấy oracle nào mâu thuẫn với §8. |
| `SG-DENY` | Cạnh chạm module này được kiểm: principal sai ⇒ `UNAUTHORIZED`. 36 cạnh cấm còn lại thuộc sweep chung `SC49`, không phải card này. |
| `SG-CONTRACT` | **Trigger một phần**: 4 mâu thuẫn hợp đồng (`CR-TC-ingest-02..05`). Không cái nào chặn được toàn bộ card, nên tôi báo CR và đi tiếp trên nhánh không mâu thuẫn thay vì dừng cả gói — và **không** sửa hợp đồng, fixture hay expectation nào. |
| `SG-EDGE` | **Không trigger**: không cần cạnh, bảng, secret hay capability nào ngoài §5. |

---

*Sau file này tôi không ghi thêm bất kỳ file nào. Sửa tiếp cần packet mới, baseline mới và
lease mới.*

---

# ADDENDUM — `PKT-TC-INGEST-FIX1` (đợt sửa sau A3-R1)

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-INGEST-FIX1` |
| `authority_id` | `AUTH-COORD-TC-INGEST-FIX1` (parent `AUTH-OWNER-20260907-03`) |
| `lease_id` | `LEASE-TC-INGEST-e2` (fencing 2) |
| **`status`** | **`DONE`** |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T11:15Z |

Phạm vi: `F-A3R1-05`, `-09`, `-10`, `-11`, `-13` theo `FIX-A3R1-rulings.md`. Không finding nào
còn mở ở phía card này.

## A1. `F-A3R1-05` — khóa ngoại của owner scoping và của liên kết receipt

**Chọn phương án (b): dựng lại bảng `post` trong revision của card này**, không chuyển DDL
`ingest_receipt` sang base revision. Lý do: `0002_base_entities` là file của worker-WM và
**không** nằm trong MODIFY grant của tôi, còn packet cho phép rõ đường dựng lại. Base revision
đã tự viết sẵn câu tương ứng ("*the ingest card adds the constraint when it creates the
referenced tables*"), nên phần "document the choice in both migrations" đã có ở phía WM bằng
chính đoạn đó; tôi ghi chi tiết ở phía mình. Nếu Coordinator muốn WM nói rõ hơn thì đó là một
dòng trong packet của họ, không phải việc tôi tự sửa file của card khác.

Ba thay đổi trong `0003_tc_ingest_idempotent_ack_lost.py`:

1. `checkpoint.owner_id` và `ingest_receipt.owner_id` nay là `REFERENCES owner (id) ON DELETE
   RESTRICT ON UPDATE RESTRICT`. Audit đúng: `owner` tồn tại trên nhánh cha nên lẽ ra phải khai
   ngay từ CREATE. Không có lý do kỹ thuật nào cho thiếu sót đó — nó là thiếu sót.
2. `post.ingest_receipt_id` nay là `REFERENCES ingest_receipt (id) … DEFERRABLE INITIALLY
   DEFERRED`, qua thủ tục dựng lại bảng của SQLite (`POST_REBUILD_STEPS`): tạo `post_rebuilt`,
   `INSERT … SELECT` **liệt kê cột tường minh** (không `SELECT *`, để một cột mới thêm ở base
   revision sẽ nổ ngay lúc migrate thay vì lệch giá trị âm thầm), `DROP TABLE post`,
   `ALTER TABLE post_rebuilt RENAME TO post`, rồi dựng lại hai unique index.
   `DEFERRABLE` là bắt buộc chứ không phải trang trí: `TXN-ingest-batch` chèn `post` **trước**
   hàng receipt mà nó trỏ tới, nên kiểm ngay lập tức sẽ làm hỏng chính transaction hợp lệ.
3. Chốt chặn kỹ thuật đáng nêu: Alembic chạy một revision **bên trong** một transaction, và
   `PRAGMA foreign_keys` là no-op ở đó. Thủ tục 12 bước trong sách hướng dẫn SQLite giả định
   tắt được `foreign_keys`. Tôi dùng `PRAGMA defer_foreign_keys = ON` — pragma **có** tác dụng
   trong transaction, hoãn mọi kiểm FK tới COMMIT, và tự reset khi transaction kết thúc nên
   không rò sang code ứng dụng.

`down_revision` của revision này quay lại **một** cha (`0002_base_entities`). Merge point nay
là `0004_merge_phase1_heads` (do worker-WM viết theo chỉ đạo Coordinator); giữ thêm một merge
ở revision của tôi khiến auth và identity thành tổ tiên hai lần, khó đọc hơn chính vấn đề nó
giải.

**Kiểm chứng (`PRAGMA foreign_key_list`, DB trắng, `alembic upgrade head`):**

```
post            [('ingest_receipt_id','ingest_receipt'), ('owner_id','owner')]
checkpoint      [('created_by_receipt_id','ingest_receipt'), ('owner_id','owner')]
ingest_receipt  [('checkpoint_id','checkpoint'), ('owner_id','owner')]
post_work       [('moved_by_merge_id','identity_merge_audit'), ('owner_id','owner'),
                 ('post_id','post'), ('work_id','work')]
PRAGMA foreign_key_check → []      alembic heads → 0004_merge_phase1_heads (head)
```

`post_work.post_id → post` **sống sót** qua lần dựng lại — đó là rủi ro thật của thủ tục này
và nó được khẳng định bằng pragma, không bằng suy luận. Hai unique index của `post` cũng được
kiểm lại tên. Thêm một test ghi một `post` trỏ tới receipt không tồn tại và khẳng định nó
**fail ở COMMIT**: ràng buộc được *ép*, không chỉ được *khai*.

## A2. `F-A3R1-10` — `server/app/ingest/__init__.py`

Đã thêm (1220 B). Không re-export gì: một caller gọi `server.app.ingest.service` đang nói rõ
nó gọi tầng nào, còn một re-export tiện tay ở đây sẽ khiến import tầng router trông giống
import tầng service.

## A3. `F-A3R1-11` — write gate nay thật sự chạy trên factory

`server/app/ingest/router.py::_context` nay đọc `app.state.storage_guard` và gắn vào
`IngestContext` bằng `dataclasses.replace` khi context chưa mang guard nào. Không cần `xfail`:
worker-WR đã landing `install_storage(app, guard=None, *, readiness_provider=…, …)` trong
`server/app/health/router.py`, và hàm đó **luôn** đặt `app.state.storage_guard`.

Guard được **lấy**, không được **tạo**: hai `StorageGuard` là hai máy trạng thái độc lập trong
bộ nhớ, nên một lần hỏng đĩa mà cái này thấy sẽ để cái kia vẫn báo `healthy` — đúng kiểu hỏng
mà I02 tồn tại để chặn. Context đã mang guard sẵn (thường là từ test) **không** bị ghi đè.

Hai test mới trên `create_app()` trần: một dựng app thật, đẩy guard của chính factory sang
`write_blocked`, POST một lô và khẳng định **503 `STORAGE_WRITE_FAILED` + `Retry-After: 30` +
0 hàng**; một khẳng định guard tiêm tường minh không bị guard của app ghi đè.

## A4. `F-A3R1-13` — delimiter của include

Khối include của card trong `server/app/main.py` nay nằm trong
`# >>> TC-ingest-idempotent-ack-lost (MOD-ingest-service) >>>` …
`# <<< TC-ingest-idempotent-ack-lost <<<`, và **cả hai import nằm trong** delimiter. Không dòng
nào ngoài khối bị chạm.

## A5. `F-A3R1-09` — kiểm kê fixture §2/§8

| Fixture (§2) | Trạng thái |
| --- | --- |
| `identity/pos-ingest-batch-valid.json` | **exercised** — `test_ingest_batch_schema.py` (validate + tính lại `payload_hash`) |
| `identity/neg-ingest-batch-*.json` (5) | **exercised** — validate + json_pointer đúng chỗ + service từ chối với 0 hàng |
| `identity/f-ingest-replay-idempotent.json` | **exercised** — `test_ingest_idempotency.py` |
| `collection/d-duplicate-ingest-replay.json` | **exercised** — `test_ingest_ack_lost.py` |
| `collection/b-cursor-invalidated-reread-dedup.json` | **exercised** — `test_ingest_ack_lost.py` |
| `e2e/a-happy-path-schedule-to-delivered.json` | **exercised (một phần, đã ghi rõ)** — hai sự kiện `ingest.submit_batch` (seq 4, 5) được **chạy thật** qua service; 16 sự kiện còn lại thuộc scheduling / enrichment / analysis / report / delivery và là `NOT_RUN` với card này |
| `boundary/a-default-deny-sweep-36-edges.json` | **exercised như một phép kiểm bao phủ** — khẳng định **0/36** cạnh cấm có `MOD-ingest-service` ở vai caller hoặc callee; nếu sau này thêm một cạnh chạm module này, assertion vỡ và card buộc phải phủ nó thay vì lặng lẽ tiếp tục không kiểm gì |
| `identity/README.md`, `boundary/README.md`, `e2e/README.md` | **NOT_RUN** — văn bản mô tả thư mục fixture, không có oracle chạy được |

Nói cách khác: `F-A3R1-09` đúng, và im lặng là khuyết điểm. Nay cả 9 fixture JSON trong §2 đều
có test chạm tới, và phần **không** chạm được nêu tên cùng lý do.

## A6. Changes của đợt này

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `server/app/ingest/__init__.py` | CREATE | `437e169ec09921fa9abcbdec7606d5d1848b0823d1f83fa09a1b0bbf019099a5` | 1220 |
| `server/app/ingest/router.py` | MODIFY | `fc4a137f56234ad0698c927305bd3247383b5de9b2f24f99e9191ef2a2892945` | 12825 |
| `server/migrations/versions/0003_tc_ingest_idempotent_ack_lost.py` | MODIFY | `a38688825c0446ea62e0dcf61cb3945c1195341e5969246b6b30dc34639cab65` | 11971 |
| `tests/integration/test_ingest_ack_lost.py` | MODIFY | `48791222c4918706c1c6290a4505c7be89c88bd23eff03edebff2f6b6e3e7227` | 35141 |
| `server/app/main.py` | MODIFY (chỉ khối include của card) | `1c21e48eca2f8c680612bfb3f6ce721ed8feb1af75f664181b8b4a5353e3a865` | 7830 |

`idempotency.py`, `repository.py`, `service.py` và hai file test contract **không đổi** (hash
giữ nguyên như bảng mục 2).

## A7. Verification của đợt này

| ID | Lệnh | Kết quả |
| --- | --- | --- |
| `EV-WI-08` | `cd server && RR_DATABASE_URL=<tmp> uv run alembic upgrade head` trên DB trắng, rồi `PRAGMA foreign_key_list` / `foreign_key_check` / `index_list(post)` | **PASS** — bảng FK ở mục A1; `foreign_key_check` rỗng; một head `0004_merge_phase1_heads` |
| `EV-WI-09` | `uv run pytest tests/contract/test_ingest_batch_schema.py tests/contract/test_ingest_idempotency.py tests/integration/test_ingest_ack_lost.py -p no:cacheprovider -o addopts="" -q` | **PASS** — **47 passed** (14 / 12 / 21), 0 failed, 0 xfail, 0 skipped, exit 0 |
| `EV-WI-10` | `uv run pytest -p no:cacheprovider -o addopts="" -q` (toàn cây) | **287 passed, 4 xfailed, 0 failed**, exit 0 |
| `EV-WI-11` | `uv run ruff check <10 file của card>` · `ruff format --check` · `uv run mypy` | **PASS** · `10 files already formatted` · `Success: no issues found in 25 source files` |

Số test của card: **41 → 47** (thêm 6: hai FK, hai write-gate trên factory, hai fixture §2).

**Một lần chạy toàn cây trung gian báo 2 FAIL** trong `tests/integration/test_denied_edges.py`;
chạy lại ngay sau đó xanh, và số test toàn cây tăng 282 → 287 giữa hai lần. Nguyên nhân là các
worker khác đang ghi file trong lúc pytest thu thập, không phải hồi quy. Tôi ghi lại thay vì
bỏ qua, vì "chạy lại thì hết" là đúng thứ không nên tin nếu không nói ra.

## A8. Baseline ở thời điểm release lease e2

Bảng pin §0 (epoch `PC10-PIN-P1b-20260907`): **35/37 khớp, 2 lệch** —
`contracts/data/entities.yaml` và `precode/decision-register.md`. Cả hai đang được sửa **ngay
lúc này** bởi `AMD-ENT-owner-01` (`F-A3R1-02`), và chính ruling đã xếp lịch "WP re-pin
(entities changed)" sau đợt fix. Tôi kiểm nội dung thay vì đoán: thay đổi nằm **hoàn toàn**
trong `ENT-owner` (bốn cột credential). `ENT-post`, `ENT-ingest-receipt`, `ENT-checkpoint` giữ
nguyên từng trường, và `TXN-ingest-batch` / `TXN-checkpoint-only` giữ nguyên. **Không** kết
luận nào của card này phụ thuộc phần đã đổi. `SRC-SPEC` và `SRC-PLAN` khớp.

## A9. CR

* `CR-TC-ingest-01` **CLOSED** bởi đợt này: `post.ingest_receipt_id` nay có FK được ép thật.
  Phần còn lại của nó — `post.discovered_by_run_id → run(id)` và `ingest_receipt.lease_id →
  assignment_lease(id)` — vẫn **mở**, vì `run` và `assignment_lease` chưa tồn tại
  (`TC-scheduler-lease-claim`). Card đó nên dựng lại `post` cùng cách khi nó tạo `run`.
* `CR-TC-ingest-02 … 06` **không đổi**, vẫn mở như mục 6.
* **CR mới `CR-TC-ingest-07` (nhỏ, không thuộc card này):**
  `server/migrations/versions/0002b_shared_move_set_tables.py` của worker-WM có 2 lỗi `ruff`
  `E501` (dòng 24, 25 — bảng trong docstring dài 101 ký tự), nên `uv run ruff check .` toàn
  repo hiện **đỏ**. Mọi file của card này sạch. File đó ngoài grant của tôi; tôi không sửa.

*Sau addendum này tôi không ghi thêm file nào. Lease `LEASE-TC-INGEST-e2` released.*

---

# ADDENDUM — `PKT-TC-INGEST-FIX2` (tái phát hành evidence manifest)

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-INGEST-FIX2` |
| `authority_id` | `AUTH-COORD-TC-INGEST-FIX2` (parent `AUTH-OWNER-20260907-03`) |
| `lease_id` | `LEASE-TC-INGEST-e3` (fencing 3) |
| **`status`** | **`DONE`** |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T11:42Z |

Phạm vi: `F-A3R2-03` (by extension) — manifest E1 cũ chạy **trước** `PKT-TC-INGEST-FIX1` và ghim
byte của những file mà chính đợt sửa đó đã đổi. Không có mã sản phẩm nào được sửa ở đợt này.

## B1. Hai bản ghi

| | Bản cũ | Bản mới |
| --- | --- | --- |
| `evidence_id` | `EV-E1-01-tc-ingest-idempotent-ack-lost` | `EV-E1-02-tc-ingest-idempotent-ack-lost` |
| Đường dẫn | `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json` | `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T113827Z.json` |
| sha256 | `b2e9f3272c32fdcefee5c80bf98cedcb1c148355eb941f9ec63196c3e4af5d13` (15 772 B) | `77db76334961424b2472fcc91faa32a153380b91d77874e62ffee13f07115d3b` (18 271 B) |
| `result` | **`STALE`** (trước là `PASS`) | `PASS` |

Bản cũ được đánh dấu **`STALE`, không phải `FAIL`**: không có gì trong nó được chứng minh là
sai — nó chỉ nói về một cây mã không còn tồn tại (SRC-PLAN §16). `stale_reason` liệt kê đích
danh năm file làm nó hết hiệu lực, và `invalidation.invalidated_by_paths` ghi cùng danh sách ở
dạng máy đọc được. Bản cũ **được giữ nguyên** chứ không bị xoá: một bản ghi bằng chứng đã phát
hành là lịch sử, và xoá nó sẽ làm mất khả năng đối chiếu "trước FIX1 hệ thống đo được gì".

## B2. Bản mới ghim gì

* **Baseline tính lại từ byte hiện tại**, không chép lại bảng pin. Bảng pin §0 của card ở epoch
  `PC10-PIN-P1c-20260907` đã được kiểm: **37/37 khớp** ở thời điểm chạy — hai dòng lệch mà
  addendum FIX1 §A8 báo (`contracts/data/entities.yaml`, `precode/decision-register.md`) đã được
  WP re-pin đúng như ruling xếp lịch.
* `baseline.contract_hashes` nay còn ghi thêm **hash của chính 10 file triển khai** (5 file
  package, migration, 3 file test, `main.py`). Đó là điều bản cũ thiếu và là lý do nó hết hiệu
  lực mà không ai biết: một manifest ghim hợp đồng nhưng không ghim mã thì không nói được nó
  đang mô tả bản mã nào.
* `invalidation.invalidated_by_paths`: 14 đường dẫn (mã ingest, hai migration, ba schema, ba
  fixture chính, `entities.yaml`, `ports.yaml`, `errors.yaml`). Đổi bất kỳ file nào trong đó là
  bản ghi này STALE — nói trước, thay vì để một audit sau phát hiện.
* Oracle bổ sung hai mục (i) và (j) cho phần FIX1 đã thêm: bảng `PRAGMA foreign_key_list` và
  write gate chạy thật trên `create_app()`.

## B3. Lần chạy mới (mọi con số dưới đây chạy lại từ đầu ở đợt này)

| ID | Lệnh | Kết quả |
| --- | --- | --- |
| `EV-WI-12` | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" -W ignore::DeprecationWarning tests/contract/test_ingest_batch_schema.py tests/contract/test_ingest_idempotency.py tests/integration/test_ingest_ack_lost.py` (11:37:35Z → 11:37:45Z) | **47 passed**, 0 failed, 0 xfail, 0 skipped, exit 0 (14 / 12 / 21) |
| `EV-WI-13` | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider -o addopts="" -q` (11:37:45Z → 11:38:27Z) | **303 passed, 4 xfailed, 0 failed**, exit 0 |
| `EV-WI-14` | `cd server && RR_DATABASE_URL=<tmp> uv run alembic upgrade head` + `alembic heads` + `PRAGMA foreign_key_list` / `foreign_key_check` | **PASS** — một head `0004_merge_phase1_heads`; FK y như addendum FIX1 §A1; `foreign_key_check` rỗng |
| `EV-WI-15` | `uv run ruff check .` · `ruff format --check .` · `uv run mypy` | **PASS** · sạch · `Success: no issues found in 25 source files` |
| `EV-WI-16` | validate cả **hai** manifest bằng `Draft202012Validator` với `evidence/manifest.schema.json` | **0 lỗi** ở cả hai |

Đáng chú ý so với manifest cũ: toàn cây nay **xanh hoàn toàn** (303 passed / 0 failed), trong
khi bản cũ ghi 261 passed / **1 failed** — lỗi smoke `/v1/health/readiness` đã được card
readiness sửa. `CR-TC-ingest-07` (2 lỗi `ruff E501` trong `0002b_shared_move_set_tables.py` của
worker-WM) cũng đã được họ sửa: `ruff check .` toàn repo nay sạch. Tôi **đóng**
`CR-TC-ingest-07`.

## B4. Changes của đợt này

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T113827Z.json` | CREATE | `77db76334961424b2472fcc91faa32a153380b91d77874e62ffee13f07115d3b` | 18271 |
| `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json` | MODIFY (`result`, `stale_reason`, `invalidation`) | `b2e9f3272c32fdcefee5c80bf98cedcb1c148355eb941f9ec63196c3e4af5d13` | 15772 |

Không file mã, hợp đồng, fixture hay test nào bị chạm ở đợt này.

## B5. CR

`CR-TC-ingest-07` **CLOSED** (worker-WM đã sửa). `CR-TC-ingest-01` vẫn đóng một phần (còn
`run` / `assignment_lease`). `CR-TC-ingest-02 … 06` **không đổi, vẫn mở**. `evidence/index.json`
vẫn chưa đăng ký hai run này — file của PC09, ngoài write set; `PKT-PC09-P1` cần trỏ vào
**bản mới** `EV-E1-02`, không phải bản `STALE`.

*Sau addendum này tôi không ghi thêm file nào. Lease `LEASE-TC-INGEST-e3` released.*
