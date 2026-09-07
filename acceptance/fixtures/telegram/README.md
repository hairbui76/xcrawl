---
contract_id: CT-fixtures-telegram
version: 0.1.0
status: draft
owner_role: interaction contract owner
source_refs:
  - "SRC-PLAN §11 PC07 (danh mục fixture bắt buộc)"
  - "SRC-PLAN §8.3 (delivery), §3 B03/B09/B10"
  - "SRC-SPEC §11.3, §8.2 hàng 10, §8.3, §12 AC-12..AC-15, AC-18"
requirement_refs: [REQ-D35, REQ-D36, REQ-D37, REQ-D38, REQ-D55, REQ-D57, REQ-AC04, REQ-AC12, REQ-AC13, REQ-AC14, REQ-AC15, REQ-AC18]
decision_refs: [B01, B03, B09, B10, AMD-B03, AMD-B09, AMD-B10, CR-PC01-02]
invariant_refs: [I05, I08, I09, I11, I13, I17]
producers: [MOD-delivery-service, MOD-telegram-adapter, MOD-saved-service]
consumers: [MOD-web-ui]
dependencies:
  - contracts/ui/screens.yaml
  - contracts/telegram/commands.yaml
  - contracts/telegram/delivery.md
  - contracts/schemas/saved-snapshot.schema.json
  - contracts/state/delivery.yaml
  - contracts/retry-policy.yaml
  - contracts/errors.yaml
  - contracts/data/entities.yaml
scope: >-
  Fixture cho delivery Telegram, cổng vào chat, liên kết, Save hai kênh và ba trạng thái run.
  Đây là DỮ LIỆU VÀO + ORACLE, không phải test đã chạy. Ở gói PC07 chỉ E0 được thực hiện.
verification: "EV-PC07-01..05. E1–E4: NOT_RUN."
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture Telegram — chỉ mục và cách dùng

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

| File | ID | Kiểm tra | Scenario | Invariant |
| --- | --- | --- | --- | --- |
| `a-multipart-part2-unknown-no-resend.json` | FX-TG-A | Digest 2 phần, part 2 timeout → `unknown`; part 1 `sent`; **0 lần gửi lại tự động** | SC14 | I09, I13 |
| `b-response-lost-unknown-operator-decides.json` | FX-TG-B | Telegram đã nhận nhưng phản hồi mất → `unknown`; người dùng quyết định | SC14 | I09, I13 |
| `c-permanent-failure-report-intact.json` | FX-TG-C | Lỗi vĩnh viễn → `failed`; report nguyên vẹn; `run.outcome` không đổi | SC14, SC15 | I05, I09, I13 |
| `d-unlink-before-send-cancelled.json` | FX-TG-D | Hủy liên kết trước khi gửi → `cancelled`, 0 lời gọi | SC25 | I09 |
| `e-relink-old-generation-cancelled.json` | FX-TG-E | Liên kết lại → delivery generation cũ `cancelled`, không tự gửi cho generation mới | SC25 | I09 |
| `f-stale-callback-no-save.json` | FX-TG-F | Callback mang `lg`/`rv` cũ → không Save, trả lời an toàn | SC13, **SC46** | I08 |
| `g-link-code-used-twice.json` | FX-TG-G | Mã dùng hai lần → lần hai im lặng | SC18, **SC47** | I11 |
| `h-unknown-chat-status-silent.json` | FX-TG-H | Chat lạ gửi `/status` → **outbound = 0**, 0 mutation | SC18 | I11 |
| `i-unknown-chat-valid-code-format.json` | FX-TG-I | Chat lạ gửi chuỗi đúng định dạng mã → đối chiếu (ngoại lệ B09); sai mã vẫn im lặng | SC18, **SC47** | I11 |
| `j-concurrent-save-app-telegram.json` | FX-TG-J | Save app + Telegram đồng thời → **một** Saved; snapshot từ revision đang đọc; 5 lần bấm = 5 phản hồi | SC13 | I08, I17 |
| `k-save-then-source-deleted.json` | FX-TG-K | Save rồi nguồn bị xóa + restart → snapshot không đổi | SC12 | I08, I17 |
| `l-run-now-while-needs-user.json` | FX-TG-L | `/run_now` khi `needs_user` → không resume; trả lời trỏ vào app | SC04, **SC45** | I13 |
| `m-three-run-states-distinct-text.json` | FX-TG-M | Ba run → ba câu phân biệt; cụm bị cấm xuất hiện 0 lần | SC15 | I13 |
| `neg-saved-snapshot-missing-content-hash.json` | FX-TG-NEG-1 | Schema Saved từ chối: thiếu `content_hash` | **SC48** | I08 |
| `neg-saved-snapshot-item-without-snapshot.json` | FX-TG-NEG-2 | Schema Saved từ chối: `saved_item` không trỏ snapshot | **SC48** | I08 |
| `neg-saved-snapshot-target-both-ids.json` | FX-TG-NEG-3 | Schema Saved từ chối: target union đặt cả hai id | **SC48** | I08 |
| `neg-saved-snapshot-summary-missing-limitation.json` | FX-TG-NEG-4 | Schema Saved từ chối: summary thiếu dòng hạn chế | **SC48** | I08 |
| `neg-saved-snapshot-bad-hash-format.json` | FX-TG-NEG-5 | Schema Saved từ chối: `content_hash` sai định dạng | **SC48** | I08 |
| `README.md` | — | Chỉ mục này | — | — |

Thư mục có **19 file**: 18 JSON (13 kịch bản `a`–`m` + 5 `neg-saved-snapshot-*`) và README này.
Bảng trên liệt kê đủ cả 19. *Packet PKT-PC07-FIX2 ghi "23 file"; số thật đếm được là 19 —
xem addendum PKT-PC07-FIX2 §B6.*

### Scenario ID mới của PC07

`SC45` run-now bị chặn bởi `needs_user` · `SC46` callback Telegram cũ (revision/generation) ·
`SC47` vòng đời mã liên kết và ngoại lệ B09 · `SC48` schema Saved từ chối payload sai.

**Rủi ro trùng ID.** FIX3-rulings §"Scenario IDs registered" nói SC33–SC44 đã dùng và
"PC05/PC06/PC07 take SC45+ if needed". Tại thời điểm viết handoff PC07,
`evidence/handoffs/PC06-handoff.md` **chưa tồn tại**, nên PC07 không kiểm được PC06 đã lấy
số nào. PC07 lấy **SC45–SC48** và ghi nhận rủi ro trùng với PC05/PC06 → **CR-PC07-06** đề nghị
PC09 phân xử khi cả ba handoff đã có.

## 2. Hình dạng chung

```text
fixture_id, title, purpose
scenario_refs, invariant_refs, decision_refs, requirement_refs, source_refs
contract_refs, owner_id, claim_ceiling, evidence_status
given → rows       : ảnh chụp hàng trước sự kiện, theo tên bảng của entities.yaml
events[]            : {seq, at, actor, operation | event_type, performed_by?, description}
expected            : rows / counts / outbound_call_counts / hash_oracles / ui_labels
forbidden_effects[] : những gì KHÔNG được xảy ra
```

Fixture kiểm schema thêm `validation_target`, `expected_validation` (`accept` | `reject`),
`saved`, và với negative là `expected_violation` → `json_pointer`.

## 3. `actor`, `performed_by`, `event_type`

Giống quy ước của `acceptance/fixtures/identity/README.md` và **bắt buộc** theo ruling
FIX3 §Fixtures:

| Khóa | Nghĩa | Kiểm bởi |
| --- | --- | --- |
| `operation` | Operation được gọi; phải tồn tại trong `contracts/ports.yaml` | EV-PC07-02 |
| `actor` | **Caller** — module phát ra lời gọi. Phải ∈ `ports.yaml.<op>.caller_modules` **và** `(actor, owner_module, operation)` ∈ `modules.yaml.allowed_edges` | EV-PC07-03 |
| `performed_by` | Module **thực thi** (chủ sở hữu operation). **KHÔNG phải khẳng định về caller**; không tạo ra cạnh giao tiếp nào | chỉ kiểm là MOD id hợp lệ |
| `event_type` | Sự kiện không phải operation (timeout, mất phản hồi, restart, Telegram nhận request) | EV-PC07-03 (mỗi event có một trong hai) |

`EXT-telegram-api` là actor hợp lệ **duy nhất** của `telegram.receive_update`: Telegram là bên
gọi vào, không phải module của hệ thống.

## 4. `outbound_call_counts`

Mọi fixture khai số lời gọi RA Telegram, tách theo phương thức
(`telegram.sendMessage`, `telegram.answerCallbackQuery`). Đây là oracle mạnh nhất của bộ này:

- REQ-AC18 (fixture h): tổng = **0**.
- AMD-B03 (fixture a): số lần gửi lại tự động của part `unknown` = **0**.
- REQ-D38 (fixture j): 5 lần bấm ⇒ 5 `answerCallbackQuery`, nhưng **1** hàng `saved_item`.

## 5. Quy tắc hash

Như bộ identity: fixture khẳng định **quan hệ** giữa các hash
(`{"symbolic": …, "computed_by": …}`), không khẳng định chuỗi hex cụ thể. Ngoại lệ có chủ ý:
`saved_snapshot.content_hash` trong fixture (j) và (k) là hex **thật**, tính bằng
`sha256(JCS(saved_snapshot.payload))`; EV-PC07-01 tính lại và so sánh.

## 6. Cột chưa tồn tại trong entities.yaml

EV-PC07-04 chạy gate `fixture-field-existence` (R4-01, §0) trên **cả sáu** thư mục fixture,
không riêng thư mục này. Cột chưa tồn tại phải mang marker `pending_cr_fields` ngay trong
fixture kèm CR tương ứng; không có marker mà cột không tồn tại ⇒ gate FAIL.

**Hiện không còn marker nào đang mở trong thư mục này.** `CR-PC07-02` đã đóng: bộ đếm rate
limit của ngoại lệ B09 nay là entity `telegram_link_attempt` với các cột thật
`telegram_link_attempt.chat_id_hash`, `telegram_link_attempt.attempted_at`,
`telegram_link_attempt.outcome` và `telegram_link_attempt.link_code_id`. Oracle đếm là
`COUNT(telegram_link_attempt WHERE chat_id_hash = H AND attempted_at trong cửa sổ trượt)`;
vượt ngưỡng thì ghi một hàng `outcome = 'rate_limited_not_checked'` và **vẫn im lặng**.

## 7. Cái bộ fixture này KHÔNG chứng minh

- Không chứng minh code chạy đúng (E0, SRC-PLAN §14.2).
- Không chứng minh Telegram thật hoạt động như mô tả — giới hạn định dạng vẫn là `KC`
  (`contracts/telegram/delivery.md` §3.4); cần đọc tài liệu chính thức.
- Không chứng minh exactly-once ở mạng ngoài — điều đó là bất khả thi với API không nhận
  idempotency key (SRC-PLAN §3.1); xem AMD-B03.
- Không thay thế fixture của gói khác (identity: PC02; reporting: PC04; recovery: PC08).

## 8. Bất biến khi sửa

Sửa một `expected` để triển khai pass là vi phạm hợp đồng (SRC-PLAN §15). Oracle sai ⇒ mở
change request kèm bằng chứng.
