---
contract_id: CT-fixtures-identity
version: 0.1.0
status: accepted
ratification_ref: OD-20260907-01
owner_role: data contract owner
source_refs:
  - "SRC-PLAN §11 PC02 (danh mục fixture bắt buộc)"
  - "SRC-PLAN §13 (ma trận truy vết AC → SC)"
  - "SRC-SPEC §12 AC-04, AC-07, AC-09, AC-12, AC-13"
requirement_refs: [REQ-D17, REQ-D25, REQ-D26, REQ-D31, REQ-D33, REQ-D38, REQ-D55, REQ-AC04, REQ-AC07, REQ-AC09, REQ-AC12, REQ-AC13]
decision_refs: [B05, B06, B07, B15, AMD-B05]
invariant_refs: [I02, I03, I04, I08, I16, I17]
producers: [MOD-backend-api]
consumers: [MOD-report-service, MOD-analysis-worker, MOD-x-collector, MOD-telegram-adapter]
dependencies:
  - contracts/data/entities.yaml
  - contracts/data/identity.md
  - contracts/data/invariants.md
  - contracts/schemas/target.schema.json
  - contracts/schemas/ingest-batch.schema.json
scope: >-
  Bộ fixture cho identity, ingest idempotency và Saved snapshot. Đây là DỮ LIỆU VÀO + ORACLE,
  không phải test đã chạy. Ở gói PC02 chỉ E0 (validate tĩnh) được thực hiện; E1/E2 là NOT_RUN.
verification: "EV-PC02-01 (parse), EV-PC02-02 (target + wire schema), EV-PC02-03 (tham chiếu entity)."
claim_ceiling: CONTRACT_READY
---

# Fixture identity — chỉ mục và cách dùng

## 0. Quy tắc khóa trong `rows` (ruling R4-01, bắt buộc ở CẢ SÁU thư mục fixture)

> Dưới `given` → `rows` → `<entity>[]` và `expected` → `rows` → `<entity>[]`, mỗi khóa phải là MỘT trong:
> (a) một cột tồn tại trong `contracts/data/entities.yaml` cho entity đó, HOẶC
> (b) một annotation có khóa **bắt đầu bằng `_`** (`_note`, `_target`, `_note_vi`,
> `_save_channel_note`, `_created_in_transaction`, `_payload_contains`, …), HOẶC
> (c) một cột mang marker `pending_cr: CR-…` trong chính file đó.
> Không có allowlist riêng theo gói.

Lý do: một khóa trần trông giống một cột. Khi nó không phải cột, người đọc hợp đồng không phân
biệt được "fixture khẳng định một cột" với "fixture ghi chú cho người đọc", và gate kiểm cột
buộc phải mang allowlist — allowlist đó chính là chỗ lỗi ẩn nấp (F-A1R3-01). Tiền tố `_` làm
ranh giới đó hiện lên trong chính dữ liệu.

Gate `fixture-field-existence` hiện thực đúng ba nhánh trên và chạy trên cả sáu thư mục.

## 1. Danh mục

| File | Fixture ID | Kiểm tra | Scenario | Invariant | Quyết định |
| --- | --- | --- | --- | --- | --- |
| `a-merge-doi-arxiv.json` | FX-ID-A | Hai work rời rạc được nối bằng bằng chứng DOI↔arXiv; winner tất định; snapshot lịch sử không đổi | SC07, SC09 | I03, I17 | B06, B15 |
| `b-post-only-missing-ids.json` | FX-ID-B | Không có định danh → target `post`, không tạo work, không đoán | SC29 | I03 | B06, B15 |
| `c-identity-conflict.json` | FX-ID-C | DOI mâu thuẫn → `identity_conflict` quarantine, không merge, giữ nguồn | SC23 | I03 | B15 |
| `d-concurrent-save-app-telegram.json` | FX-ID-D | Save đồng thời app + Telegram → đúng một Saved active | SC13 | I08 | B01 |
| `e-source-deleted-snapshot-intact.json` | FX-ID-E | Post bị xóa trên X (quan sát qua `ingest.submit_batch`) + restart → snapshot không đổi | SC12 | I08, I17, I02 | B01 |
| `f-ingest-replay-idempotent.json` | FX-ID-F | Replay cùng idempotency key → cùng receipt, số đếm không đổi; key trùng payload khác → conflict | SC21 | I02 | B05, AMD-B05 |
| `g-arxiv-version-v1-v2.json` | FX-ID-G | v1→v2 là một work hai `work_version`; generation phân tích mới, bản cũ giữ nguyên | SC30 | I03, I04 | B06, B07 |
| `h-five-posts-thread-one-target.json` | FX-ID-H | 5 post + thread tác giả cùng arXiv ID → một mục công trình; 5 biến thể chuẩn hóa | SC07 | I03 | B06 |
| `pos-ingest-batch-valid.json` | FX-ID-WIRE-POS | Batch hợp lệ (positive của wire schema) | SC31 | I02 | B05 |
| `neg-ingest-batch-missing-idempotency-key.json` | FX-ID-WIRE-NEG-1 | Thiếu `idempotency_key` → từ chối | SC31 | I02 | B05 |
| `neg-ingest-batch-bad-payload-hash.json` | FX-ID-WIRE-NEG-2 | `payload_hash` sai định dạng → từ chối | SC31 | I02 | B05 |
| `neg-ingest-batch-empty-items.json` | FX-ID-WIRE-NEG-3 | `items` rỗng → từ chối | SC31 | I02 | B05 |
| `neg-ingest-batch-unknown-field.json` | FX-ID-WIRE-NEG-4 | Trường lạ ở cấp gốc → từ chối | SC31 | I02 | B05 |
| `neg-ingest-batch-timestamp-precision.json` | FX-ID-WIRE-NEG-5 | Timestamp thiếu mili-giây → từ chối | SC31 | I02 | B05 |

**SC32 (xóa dữ liệu gốc) chưa có fixture ở gói này.** Ràng buộc PC02 sở hữu đã được khóa dưới
dạng oracle trong `contracts/data/entities.yaml` (`entities[saved_snapshot].survives_data_deletion`
và `entities[data_deletion_audit].pc02_constraint`): sau `data.delete_target`,
`#saved_snapshot` và mọi `content_hash` không đổi, `#first_announced_ledger` không đổi. Fixture
đầy đủ cần ngữ nghĩa xóa của PC01/PC08 nên **thuộc PC09** (ruling R-04) — xem `CR-PC02-13`.

### `actor`, `performed_by`, `event_type` — ba khóa khác nhau

| Khóa | Nghĩa | Bị kiểm thế nào |
| --- | --- | --- |
| `operation` | Operation được gọi. **Phải** tồn tại trong `contracts/ports.yaml`. | EV-PC02-04 |
| `actor` | **Caller** — module phát ra lời gọi. Phải nằm trong `ports.yaml.<op>.caller_modules` **và** bộ ba `(actor, owner_module, operation)` phải có trong `modules.yaml.allowed_edges`. | EV-PC02-05 (`fixture-actor-edge`) |
| `performed_by` | Module **thực thi** transaction, tức chủ sở hữu operation. **KHÔNG phải một khẳng định về caller** và **không** tạo ra một cạnh giao tiếp nào. Có mặt để fixture nói được "ai ghi dữ liệu" mà không ngụ ý "ai gọi". | Chỉ kiểm là MOD id hợp lệ |
| `event_type` | Sự kiện **không phải** operation: mất ACK, khởi động lại máy, đứt mạng. Dùng thay cho `operation`, không dùng cùng lúc. | EV-PC02-05 (mỗi event phải có một trong hai) |

Phân biệt này ra đời từ finding **F-A1R1-02**: 10/22 event trước đây đặt module *thực thi* vào
`actor`, tức là khẳng định một cạnh giao tiếp mà `modules.yaml` cấm theo default-deny. Ví dụ
`research.fetch_work_metadata` do `MOD-research-connector` **sở hữu**, nhưng caller hợp lệ là
`MOD-ingest-service`; fixture nay ghi `actor: MOD-ingest-service`,
`performed_by: MOD-research-connector`.

**Cấm:** viết vào `actor` một module chỉ vì nó là nơi dữ liệu được ghi. Nếu ý là "nơi thực
thi", dùng `performed_by`.

**SC29, SC30, SC31 là scenario ID mới** do PC02 đề nghị (baseline §3 cho phép `SC29+`).
Chuyển tới PC09 để đăng ký vào `acceptance/scenarios.yaml`: **CR-PC02-08**.
SC29 = target chỉ-có-post; SC30 = phiên bản arXiv mới; SC31 = wire schema của ingest batch từ chối payload sai.

## 1b. Trạng thái phê chuẩn của thư mục này

Cả **14 fixture** mang `x-contract.claim_ceiling: CONTRACT_READY`,
`x-contract.status: accepted`, `x-contract.ratification_ref: OD-20260907-01` — ruling
F-A2R5-04: fixture của hai thư mục đã phê chuẩn (`identity/`, `reporting/`) là **oracle chấp
nhận** của chính phạm vi đó, nên chúng không được đứng dưới README vốn đã claim CONTRACT_READY.

`ratification_ref` nằm trong **header hợp đồng** (`x-contract` của mỗi file JSON), không nằm
trong văn xuôi — đó là điều kiện F-A2R5-03 đặt ra để gate đọc được nó.

Mỗi `x-contract` cũng mang `runtime_evidence: NOT_RUN`: E1–E4 chưa chạy, chưa có code, và
SQLite chưa từng được yêu cầu ép các ràng buộc mô tả trong hợp đồng. `CONTRACT_READY` nói bộ
hợp đồng đủ trường và đã kiểm ví dụ hợp lệ/bất hợp lệ ở mức E0 — **không** nói code chạy được.

## 2. Hình dạng chung của một fixture

```text
fixture_id, title, purpose
fixture_format_version, x-contract   <- header hợp đồng: status, ratification_ref,
                                        claim_ceiling, runtime_evidence
scenario_refs, invariant_refs, decision_refs, requirement_refs, source_refs
contract_refs, owner_id, evidence_status
given → rows    : ảnh chụp các hàng trước sự kiện, theo tên bảng của entities.yaml
events[]         : chuỗi có thứ tự {seq, at, actor, operation, transaction?, description}
expected         : rows / counts / hash_oracles / (after_event_N cho fixture nhiều mốc)
forbidden_effects: những gì KHÔNG được xảy ra — là phần bắt lỗi thật sự
```

Fixture wire (`pos-*`, `neg-*`, và cả `e-`, `f-`, `h-`) thêm:
`validation_target`, `expected_validation` (`accept` | `reject`), `batch`, và với negative là
`expected_violation` → `json_pointer`.

## 3. Quy ước về hash

Fixture **không** khẳng định một chuỗi hex cụ thể cho hash nội dung. Chúng khẳng định **quan hệ**:

```json
{"symbolic": "H_S1", "computed_by": "sha256(JCS(saved_snapshot.payload))"}
```

Giá trị thật được tính lúc chạy test theo quy tắc canonical JSON (RFC 8785) trong
`contracts/data/entities.yaml` → `§ conventions → hashes`. Oracle nằm ở `expected` → `hash_oracles`,
ví dụ "`content_hash` sau merge bằng `content_hash` trước merge". Viết một chuỗi hex bịa vào
fixture sẽ tạo ra một oracle không ai tái lập được, nên bị cấm ở đây.

**Ngoại lệ có chủ ý:** `payload_hash` trong các fixture wire là hex **thật**, tính bằng
`sha256(JCS(payload_core))` với `payload_core = {schema_version, items, client_checkpoint_proposal}`.
EV-PC02-02 tính lại và so sánh, nên giá trị đó tái lập được và không phải là hằng số bịa.

## 4. Cách dùng ở từng cấp bằng chứng

| Cấp | Dùng fixture thế nào | Trạng thái ở PC02 |
| --- | --- | --- |
| E0 | Parse JSON; validate mọi target object trong `given`/`expected` theo `target.schema.json`; validate `batch` theo `ingest-batch.schema.json`; kiểm mọi tên bảng tồn tại trong `entities.yaml`; tính lại `payload_hash`; kiểm `operation` tồn tại trong `ports.yaml`; kiểm `(actor, owner, operation)` nằm trong `allowed_edges`; so sánh hai chiều entity ↔ `data_owner_of` | **ĐÃ CHẠY** (EV-PC02-01…06, SELF_VALIDATION) |
| E1 | Nạp `given` → `rows` vào một kho trống, phát `events` qua đúng operation, so `expected` → `rows`/`counts`/`hash_oracles`, và khẳng định mọi mục trong `forbidden_effects` KHÔNG xảy ra | `NOT_RUN` — cần code |
| E2 | Thêm fault injection tại các mốc trong `transactions[*].failure_timeline` (crash trước/sau COMMIT, mất ACK, lease hết hạn) | `NOT_RUN` |
| E3/E4 | Không áp dụng cho bộ fixture này | `NOT_APPLICABLE` (fixture là dữ liệu offline theo thiết kế; live X/AI thuộc PC05/PC06) |

**Quy tắc trích target object của E0** (để kiểm tra tái lập được): duyệt đệ quy `given` và
`expected`; mọi object có thuộc tính `kind` với giá trị `work` hoặc `post` là một target
object và phải validate. Phép duyệt theo GIÁ TRỊ, không theo tên khóa, nên việc đổi `target`
thành `_target` (R4-01) không ảnh hưởng. Fixture cố ý **không** dùng khóa `kind` cho mục đích
khác — các trường phân loại khác mang tên `conflict_type`, `item_type`, `link_kind_hint`,
`media_type`, `version_scheme`.

## 5. Cái các fixture này KHÔNG chứng minh

- Không chứng minh code chạy đúng: chưa có code (SRC-PLAN §14.2 E0).
- Không chứng minh collector lấy được dữ liệu từ X (REQ-A1, thuộc SP1/PC05).
- Không chứng minh chất lượng summary hay nhãn (E4, thuộc PC06/PC09).
- Không chứng minh "0 trùng" ở mức khoa học: chỉ ở mức canonical identity đã biết (B15).
- Không thay thế fixture của gói khác: cache analysis (PC06), coverage/backfill (PC04),
  delivery unknown (PC07), restore (PC08) có bộ fixture riêng.

## 6. Bất biến khi sửa fixture

Sửa một `expected` để cho triển khai pass là vi phạm hợp đồng (SRC-PLAN §15, `agent_profile/worker.md`).
Nếu một oracle sai, mở change request có bằng chứng, đừng sửa fixture.
