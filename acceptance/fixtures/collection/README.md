---
contract_id: CT-fixture-collection-index
version: 0.4.0
status: draft
owner_role: connector contract owner
source_refs: [SRC-PLAN §11 PC05, SRC-PLAN §13, SRC-SPEC §9.2, SRC-SPEC §9.3, SRC-SPEC §12]
requirement_refs: [REQ-AC01, REQ-AC03, REQ-AC04, REQ-AC11, REQ-AC15, REQ-D08, REQ-D11, REQ-D31, REQ-D32, REQ-D33, REQ-S9.2-01, REQ-S9.3-07, REQ-A1, REQ-A6, REQ-A7]
decision_refs: [B02, B05, B06, B10, B12, B15, AMD-B02, AMD-B05, AMD-B10, CR-PC05-01, "R-01 (A1-R1)", "R-02 (A1-R1)", "R4-01 (FIX4)", "R4-02 (FIX4)", "FIX3 rulings (2026-09-06T19:05Z)", "FIX4 rulings", "R5-02 (FIX5)"]
invariant_refs: [I01, I02, I03, I10, I11, I13, I15]
producers: [MOD-x-collector]
consumers: [MOD-ingest-service, MOD-job-service]
dependencies:
  - contracts/http/openapi.yaml
  - contracts/schemas/worker-assignment.schema.json
  - contracts/schemas/ingest-receipt.schema.json
  - contracts/schemas/ingest-batch.schema.json
  - contracts/state/run.yaml
  - contracts/errors.yaml
  - contracts/retry-policy.yaml
scope: >-
  Chỉ mục của tám fixture thu thập. Mọi fixture là TĨNH và chạy được HOÀN TOÀN OFFLINE — không fixture nào
  yêu cầu X live (SRC-PLAN §11 PC05: "không để test nền tảng bắt buộc có X live").
verification: >-
  EV-PC05-02 (SELF_VALIDATION): mọi body mang `validate_request_against` / `validate_response_against` được
  validate bằng jsonschema Draft 2020-12 với registry các file schema cục bộ; mọi event dùng khóa `operation`
  (R4-02) và gate FAIL TO nếu gặp khóa lạ; mọi `events[].actor` là caller hợp lệ theo contracts/ports.yaml VÀ
  bộ ba (caller, owner, operation) có trong contracts/modules.yaml.allowed_edges (R-02); gate field-level R4-01
  chạy qua thư mục này; mọi mã lỗi tồn tại trong contracts/errors.yaml.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture thu thập (collection)

## Cách đọc

Mỗi file là một kịch bản đầy đủ, cùng một hình dạng:

| Khóa | Nghĩa |
| --- | --- |
| `x-contract` | Header hợp đồng (baseline §3 cho phép fixture JSON mang header dạng `x-contract`) |
| `preconditions_vi` | Trạng thái trước khi kịch bản bắt đầu |
| `events[]` | Chuỗi sự kiện theo thứ tự. Mỗi sự kiện có `actor`, `operation_id`, `http`, request/response |
| `events[].operation` | ID operation theo `contracts/ports.yaml`. **Khóa là `operation`** ở mọi thư mục fixture (ruling R4-02); khóa cũ `operation_id` đã bị đổi ở FIX2 |
| `events[].event_type` | BẮT BUỘC khi `operation` là `null` (R4-02). Giá trị dùng ở đây: `local_observation` — sự kiện xảy ra trên máy cá nhân, không có lời gọi HTTP nào. Nhờ khóa này, gate actor-edge bỏ qua sự kiện theo QUY TẮC thay vì phải đoán |
| `events[].actor` | Module **gọi**. Phải là một caller được phép theo `contracts/ports.yaml.caller_modules` VÀ bộ ba `(caller, owner_module, operation)` phải có trong `contracts/modules.yaml.allowed_edges` (ruling R-02, siết ở FIX3) |
| `events[].performed_by` | Service **thực hiện** transaction. **KHÔNG** phải một khẳng định về cạnh gọi (ruling R-02) |
| `events[].validate_*_against` | File schema mà body phải validate được. Đây là móc nối cho EV-PC05-02 |
| `durable_rows_expected` | Hàng nào phải bền sau kịch bản |
| `forbidden_effects` | Điều gì **không được** xảy ra. Đây là phần có giá trị nhất của mỗi fixture |
| `oracle_vi` | Phép kiểm cụ thể, đếm được |

Một sự kiện có `response_status: null` là **có chủ đích**: nó mô hình hóa việc client **không biết kết quả**
(timeout transport — SRC-PLAN §5.1). Đó không phải chỗ thiếu dữ liệu.

## Danh mục

| File | Kịch bản | Scenario | Invariant | Điều khóa được |
| --- | --- | --- | --- | --- |
| `a-feed-layout-changed.json` | X đổi bố cục, parser bóc được 12/40 bài | SC03, SC15 | I02, I10, I13 | Commit phần bóc được, rồi **dừng và báo** bằng `SOURCE_LAYOUT_CHANGED`. Không đoán trường thiếu, không parser thay thế, không luân chuyển gì. Đúng **một** alert intent |
| `b-cursor-invalidated-reread-dedup.json` | Con trỏ feed mất hiệu lực, phải đọc lại | SC03, SC21 | I02 | Đọc lại **được phép**; cam kết là không **ingest** trùng. Oracle là số hàng, **không** phải số request (AMD-B05) |
| `c-challenge-mid-batch.json` | CAPTCHA giữa lô đã tải nhưng chưa ingest | SC04 | I02, I10, I13 | Đúng **một** alert intent; 7 bài trong RAM không phải checkpoint bền; `status`/`run-now` không resume (AMD-B10) |
| `d-duplicate-ingest-replay.json` | Mất ACK sau khi server đã commit | SC21 | I02 | Tra receipt **trước** khi retry; replay trả `receipt_hash` y hệt; payload khác ⇒ 409 |
| `e-limit-reached-stop.json` | Chạm giới hạn 200 bài | SC03 | I02, I13 | `stop_reason = limit_reached` **không** phải lỗi và **không** phải hoàn tất-trọn-vẹn (AMD-B02) |
| `f-two-workers-claim-same-assignment.json` | Hai worker, lease epoch cũ và mới | SC20 | I02, I10 | Epoch cũ bị từ chối **trước mọi write**; không có ghi một phần |
| `g-schedule-due-claim.json` | Lịch tới hạn, collector online | SC01 | I01, I10, I15 | Đăng ký **không** cấp lease; claim bị chặn khi `storage.health = recovery_required` |
| `h-metadata-unavailable-post-only.json` | arXiv/OpenAlex không trả metadata | SC11 | I03, I11, I13 | Target ở mức `post_only`; **không đoán** DOI/arXiv id; lô vẫn commit |

Tám file trên là (a)–(h) của PKT-PC05, theo đúng thứ tự.

**Bốn file thêm ở FIX4** (ruling R5-02) phủ các scenario mà `contracts/state/run.yaml` §scenario_definitions đã
định nghĩa nhưng chưa có fixture:

| File | Kịch bản | Scenario | Invariant | Điều khóa được |
| --- | --- | --- | --- | --- |
| `i-run-now-while-active.json` | Bấm "chạy ngay" 5 lần khi đang có run | SC33 | I10, I13 | COALESCE: trả run đang có, **không** tạo run thứ hai và **không** trả lỗi |
| `j-dst-boundary-occurrences.json` | Giờ DST bị nhảy và giờ DST lặp | SC34 | I06, I13 | Mỗi mốc danh nghĩa sinh **đúng một** occurrence; không bỏ, không nhân đôi |
| `k-cancel-from-every-non-terminal.json` | Cancel từ cả 5 trạng thái non-terminal | SC35 | I02, I10, I13 | Lease thu hồi; dữ liệu đã commit **không** bị xóa; delivery đã `sent` **không** bị thu hồi |
| `l-storage-write-blocked-mid-run.json` | `write_blocked` giữa run, hai nhánh hồi phục | SC36 | I02, I13, I15 | Nhánh B: còn `restore_record` chưa đối soát ⇒ về `recovery_required`, **không** `healthy` |

Bốn file này dùng `given.rows` / `expected.rows` có cấu trúc, nên gate field-level (R4-01) **không còn rỗng**
trên thư mục này.

## Vì sao các fixture này chạy offline được

Chúng ghi lại **hợp đồng dây**, không phải hành vi của X. Mỗi sự kiện là một cặp request/response HTTP đã biết
trước, nên một test harness có thể phát lại chúng bằng một server giả mà không cần trình duyệt, không cần
phiên X, không cần mạng.

Điều này quan trọng vì `contracts/ops/collector-probe.md` ghi rõ: probe M0 chạy **dry-run** và **không** gọi
`ingest.submit_batch`. Nghĩa là đường ingest **không** được probe kiểm chứng — nó được kiểm ở đây. Hai thứ bù
cho nhau và không thay thế nhau.

## Quy ước ghi chú trong `rows` (ruling R4-01) — bắt buộc ở cả sáu thư mục fixture

Dưới `given.rows.<entity>[]` và `expected.rows.<entity>[]`, **mọi khóa** phải là một trong ba loại:
(a) một cột CÓ THẬT trong `contracts/data/entities.yaml` cho entity đó; (b) một chú thích có khóa **bắt đầu
bằng `_`** (`_note`, `_target`, `_note_vi`, `_save_channel_note`, `_created_in_transaction`,
`_payload_contains`, …); hoặc (c) một cột mang marker `pending_cr: CR-…` ngay trong file. **Không có
allowlist riêng cho từng gói.**

Lý do quy ước này tồn tại: nếu mỗi gói tự giữ một danh sách ngoại lệ riêng thì gate kiểm cột trở nên không
đáng tin — nó có thể báo PASS trong khi hàng chục khóa chưa resolve (đúng điều F-A1R3-01 phát hiện: 89 khóa
trên 25 file). Một quy ước duy nhất, viết ra ở đây và ở năm README kia, làm cho một checker độc lập cho ra
CÙNG con số với checker của gói.

**Trạng thái của thư mục này (cập nhật FIX4):** tám fixture gốc (a)–(h) **không dùng** hình dạng
`given.rows` / `expected.rows`; bốn fixture (i)–(l) thêm ở FIX4 **có dùng**.
Chúng ghi kỳ vọng bằng `durable_rows_expected` (danh sách câu văn) và `expected_target_state`. Vì vậy gate
field-level chạy qua thư mục này kiểm **0 cột** và cho **0 chưa resolve** — con số đó nghĩa là *không có gì
để kiểm*, **không phải** "đã kiểm và sạch". Xem `Giới hạn đã biết` mục 6.

## `edge_assertion: forbidden` (ruling R4-02)

Một sự kiện CỐ Ý khẳng định một cạnh **bị cấm** (để chứng minh default deny có hiệu lực) phải mang
`edge_assertion: "forbidden"`. Khi đó gate actor-edge **đảo kỳ vọng**: bộ ba `(actor, owner_module, operation)`
phải **VẮNG MẶT** khỏi `allowed_edges`, và response mong đợi phải là `UNAUTHORIZED`, `FORBIDDEN_EDGE` hoặc
`CAPABILITY_DENIED`.

Không có marker này, một checker độc lập sẽ báo chính các ca âm cố ý là vi phạm — loại dương tính giả mời
người review bỏ qua cả những vi phạm thật (F-A1R3-02).

**Trạng thái của thư mục này: KHÔNG fixture nào ở đây dùng `edge_assertion`.** Quy ước được ghi lại vì ruling
R4-02 nêu đích danh `collection` cùng `recovery`, và để một fixture âm thêm về sau có sẵn khóa đúng. Ca âm gần
nhất hiện có là `f-two-workers-claim-same-assignment.json` — nhưng nó là **stale lease**, một cạnh HỢP LỆ bị
từ chối vì epoch cũ, KHÔNG phải một cạnh bị cấm; nó đúng khi không mang marker.

## Giới hạn đã biết

1. **Chưa chạy.** Đây là fixture, không phải kết quả test. Trạng thái bằng chứng: `NOT_RUN`.
   EV-PC05-02 chỉ kiểm rằng các body **validate được theo schema**, không kiểm rằng một implementation nào đó
   hành xử đúng như vậy.
2. **`a-feed-layout-changed.json` — `pending_cr` đã được gỡ ở FIX1.** `CR-PC05-01` được ruling FIX3 chấp
   nhận: `SOURCE_LAYOUT_CHANGED` nay có trong `contracts/errors.yaml` và `stop_reason: source_layout_changed`
   có trong `contracts/state/run.yaml` (T-RUN-24). Fixture đã chuyển sang mã thật và mang thêm một sự kiện
   thứ ba chứng minh "một alert intent mỗi run". Phần `worker.report_stop.stop_reason` phía
   `contracts/ports.yaml` do PKT-PC01-FIX3 land — xem concern ở addendum PC05-FIX1.
3. **Một số body dùng `GenericObject`.** Các operation mà schema chi tiết thuộc gói khác (`worker.report_stop`
   nhận body do PC03 mô tả bằng prose, `worker.register_capabilities` theo `contracts/capabilities.yaml`)
   chưa có schema đóng để validate. Những body đó **không** mang `validate_*_against` và được đánh dấu rõ.
4. **`accepted_items` được rút gọn.** Ở các lô lớn, fixture chỉ liệt kê một hai mục đại diện thay vì đủ 200 —
   `counts` mới là phần mang nghĩa cho oracle.
5. **Gate field-level KHÔNG còn rỗng kể từ FIX4.** Tám fixture gốc (a)–(h) vẫn ghi kỳ vọng bằng
   `durable_rows_expected` (câu văn) và không đóng góp cột nào cho gate. Bốn fixture mới (i)–(l) dùng
   `given.rows`/`expected.rows` có cấu trúc, nên `E0-15-fixture-field-existence` kiểm được cột thật trên thư
   mục này thay vì báo `NOT_APPLICABLE_FREEFORM`. Chuyển tám file cũ sang hình dạng `rows` là một thay đổi
   thiết kế, không phải sửa lỗi, nên nó chưa được làm.
6. **Không có giá trị secret nào.** Header `Authorization` trong fixture là văn bản mô tả, không phải token.
   Fixture không bao giờ chứa token, cookie hay chat ID thật (SRC-SPEC §11.2).
