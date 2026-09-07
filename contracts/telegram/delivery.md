---
contract_id: CT-telegram-delivery
version: 0.1.0
status: draft
owner_role: interaction contract owner
source_refs:
  - "SRC-SPEC §3.6 D35, D38, D57"
  - "SRC-SPEC §5.3 (digest và Save)"
  - "SRC-SPEC §5.4 (một cảnh báo cho một run)"
  - "SRC-SPEC §8.2 hàng 8, hàng 9"
  - "SRC-SPEC §9.1 (tách hai vòng đời), §9.3 (Telegram gửi lỗi)"
  - "SRC-SPEC §12 AC-04, AC-14"
  - "SRC-PLAN §3 B01, B03, §3.1 (Telegram không có idempotency key của client)"
  - "SRC-PLAN §5.1 (outbox, timeout là không biết kết quả)"
  - "SRC-PLAN §8.3 (bảng transition delivery)"
  - "SRC-PLAN §10 TELEGRAM_SEND_UNCERTAIN, TELEGRAM_PERMANENT_FAILURE"
  - "SRC-PLAN §11 PC07"
requirement_refs: [REQ-D04, REQ-D15, REQ-D38, REQ-D53, REQ-D54, REQ-D57, REQ-AC04, REQ-AC10, REQ-AC14, REQ-OQ07, REQ-S9.1-01, REQ-S9.3-06]
decision_refs: [B01, B03, AMD-B01, AMD-B03, ADR-0003, ADR-0004]
invariant_refs: [I05, I08, I09, I13]
producers: [MOD-delivery-service, MOD-telegram-adapter]
consumers: [MOD-web-ui, MOD-report-service, MOD-job-service]
dependencies:
  - contracts/state/delivery.yaml
  - contracts/retry-policy.yaml
  - contracts/errors.yaml
  - contracts/data/entities.yaml
  - contracts/schemas/report.schema.json
  - contracts/telegram/commands.yaml
  - contracts/reporting/time-and-tags.md
scope: >-
  Cách một báo cáo đã publish trở thành một hoặc nhiều tin Telegram: outbox intent tạo trong
  transaction publish, cấu trúc digest, giới hạn định dạng, tách phần, thủ tục gửi khớp với
  contracts/state/delivery.yaml, xử lý `unknown`, cảnh báo `needs_user`, và văn bản amendment
  thay thế lời hứa "không có tin nào bị gửi hai lần" của REQ-AC14. File này KHÔNG định nghĩa
  lại state machine (PC03 sở hữu) và KHÔNG đặt số retry mới.
verification: >-
  E0: mọi trạng thái delivery được nhắc phải tồn tại trong contracts/state/delivery.yaml; mọi
  error code phải tồn tại trong contracts/errors.yaml; mọi con số retry phải trích từ
  contracts/retry-policy.yaml (EV-PC07-02). Fixture (a)–(e) trong acceptance/fixtures/telegram/.
  E1–E4: NOT_RUN. Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có mạng).
claim_ceiling: DRAFT_FOR_REVIEW
---

# Telegram delivery

## 1. Nguyên tắc

Ba câu quyết định toàn bộ file này:

1. **Delivery không đổi nội dung report đã publish** (B01, I05). Nội dung được đóng băng ở
   transaction publish; việc gửi chỉ đọc.
2. **Vòng đời delivery tách rời vòng đời run** (SRC-SPEC §9.1, I09). Telegram lỗi không làm
   run thất bại và không làm report biến mất.
3. **Telegram không nhận idempotency key từ client** (SRC-PLAN §3.1). Vì vậy hệ thống không
   thể hứa exactly-once ở mạng ngoài; nó chỉ hứa những gì quan sát được ở phía mình.

## 2. Outbox intent

Tạo trong **transaction publish**, không phải sau đó.

| Thuộc tính | Giá trị |
| --- | --- |
| Operation | `delivery.create_intent` (caller: `MOD-report-service` cho digest, `MOD-job-service` cho alert) |
| Transition | `T-DL-00` trong `contracts/state/delivery.yaml` → trạng thái `pending` |
| Hàng ghi cùng transaction | `outbox_intent` + `delivery(state = pending, telegram_link_generation)` cùng với nội dung nguồn |
| Idempotency | `logical_delivery_key` = (`report_id` hoặc `run_alert_id`) + `channel` |
| Kind | `report_digest` \| `run_alert` |

Lý do dùng outbox: SRC-PLAN §5.1 cấm gọi mạng bên trong transaction SQLite. Intent được commit
cùng dữ liệu, dispatcher đọc sau. Nếu tiến trình chết giữa publish và gửi, intent vẫn còn và
việc gửi tiếp tục — không mất digest, không gửi digest cho một report chưa publish.

**Kỳ rỗng không tạo intent** (REQ-D57): `COUNT(outbox_intent WHERE kind='report_digest')` = 0
cho một kỳ rỗng. Kỳ rỗng vẫn có `coverage_window` và vẫn hiện ở Runs — nó chỉ không có digest.

`telegram_link_generation` được **chụp tại đây**. Đổi liên kết về sau ⇒ intent cũ bị `cancelled`
(`T-DL-08`), không chuyển sang recipient mới.

## 3. Nội dung digest

### 3.1 Cấu trúc

Thứ tự cố định, phản chiếu Report detail:

1. **Tiêu đề kỳ** — ngày publish (quy đổi sang `owner.timezone_iana`) và khoảng bao trùm
   `[coverage_from, coverage_to)`. Với run chạy bù, câu này ghi **khoảng bao trùm của cả các
   đợt đã gộp** (REQ-D15, SRC-SPEC §8.2 hàng 8) — không phải chỉ đợt cuối.
2. **Khối "hướng đang nổi"** — ở ĐẦU (REQ-D53). Mỗi hướng: nhãn, các work thuộc vùng, và
   **nhãn bắt buộc "ứng viên để đọc sâu"** (REQ-D54). Hướng có
   `evidence_state = insufficient_evidence` hiển thị là chưa đủ bằng chứng và **không** được
   gọi là hướng đang nổi (B14).
3. **Danh sách mục** — mỗi mục:
   - tiêu đề công trình (hoặc trích ngắn của post với mục chỉ-có-post),
   - summary ngắn theo hình dạng REQ-D20: nội dung · điểm khác · một dòng hạn chế,
   - **nhãn mức độ đọc** (`post_only` / `abstract` / `full_text`) — REQ-D21, REQ-AC11,
   - **dòng "khớp tag nào"** — REQ-D20, REQ-AC10,
   - nhãn `prior_reference` kèm "đã báo cáo <ngày D>" nếu là tham chiếu (REQ-D29),
   - **deep link về app** (REQ-D04) và link nguồn,
   - **nút Save** với callback payload theo `contracts/telegram/commands.yaml` §CMD-save.
4. **Chân tin** — số mục, `quality` (`complete`/`partial`) và, nếu `partial`, số mục còn thiếu
   summary (B17). Không bao giờ im lặng về phần thiếu.

Mục tiêu là REQ-AC10: người đọc trên Telegram quyết định được **mà không cần mở nguồn**. Nếu
một trường bắt buộc thiếu, mục hiển thị nhãn thiếu, không hiển thị như đầy đủ.

### 3.2 Deep link

`https://<app_host>/reports/<report_id>#item-<report_item_id>`. Host lấy từ cấu hình, không
lấy từ nội dung nguồn. Link phải mở được trên điện thoại (REQ-D04).

### 3.3 Escaping

Nội dung nguồn (tiêu đề paper, text post, nhãn chủ đề, output AI) là **dữ liệu không đáng tin
cậy** (SRC-SPEC §11.4, I11).

- Escape theo đúng parse mode được chọn **trước** khi ghép chuỗi; không bao giờ nội suy thô.
- Không cho nội dung nguồn tạo entity liên kết: URL trong tin chỉ đến từ trường URL đã được
  kiểm, không từ văn bản.
- Nội dung nguồn **không** quyết định recipient, không kích hoạt tool, không đổi quyền gửi
  (I11, REQ-AC17).
- Nếu escaping thất bại hoặc không chắc, gửi **plain text**; mất định dạng đẹp là chấp nhận
  được, chèn markup từ nội dung ngoài thì không.

### 3.4 Giới hạn định dạng — `KC`

| Hạng mục | Trạng thái | Ghi chú |
| --- | --- | --- |
| Độ dài tối đa một tin | `KC` | Phải đọc tài liệu chính thức trước khi triển khai |
| Độ dài callback data | `KC` (PROVISIONAL 64 byte) | Định dạng `1:<ri>:<ii>:<lg>:<rv>` được thiết kế để vừa |
| Parse mode và tập ký tự phải escape | `KC` | Chọn MỘT parse mode và khóa bảng escape của đúng chế độ đó |
| Số nút mỗi hàng / mỗi bàn phím | `KC` | |
| Rate limit gửi | `KC` | `Retry-After` của Telegram **thắng** mọi số trong `retry-policy.yaml` |

Nguồn phải đọc: <https://core.telegram.org/bots/api#sendmessage>.

**Chưa đọc trong gói này** — không có mạng (baseline §3). Mọi số ở trên là giả định cho tới khi
có người đọc tài liệu thật và ghi lại; đó là điều kiện của SRC-SPEC §13.2 và REQ-A6 áp dụng cho
Telegram. Cấm suy ra giới hạn từ trí nhớ.

### 3.5 Tách phần

Khi digest vượt giới hạn một tin, tách thành nhiều `delivery_part`:

- Mỗi part có `part_index` (0-based), `payload_hash` và **receipt riêng** (`DP-01`).
- Ranh giới tách phải ở **ranh giới mục**, không cắt giữa một mục — người đọc không bao giờ
  thấy nửa mục.
- Khối "hướng đang nổi" nằm trọn trong part 0.
- Mỗi part tự nêu vị trí (ví dụ "phần 2/3") để một part `unknown` không làm người đọc tưởng
  mất nội dung.
- Một mục vượt giới hạn một tin ⇒ cắt phần summary và thêm deep link "đọc đầy đủ trong app";
  không tách một mục ra hai tin.

## 4. Thủ tục gửi

Khớp `contracts/state/delivery.yaml`; ở đây chỉ diễn giải, **không** định nghĩa lại.

| Bước | Transition | Điều bắt buộc |
| --- | --- | --- |
| Dispatch | `T-DL-01` `pending → sending` | Giữ **sender lease**; kiểm `trạng thái kho không thuộc {write_blocked, recovery_required}`; **COMMIT hàng attempt TRƯỚC network call** |
| Thành công | `T-DL-02` `sending → sent` | Lưu receipt kèm `provider_message_id`; retry sau đó chỉ trả receipt |
| Lỗi retry được | `T-DL-03` `sending → retry_wait` | Chỉ khi **chắc chắn chưa nhận** hoặc lỗi retryable có nghĩa rõ |
| Không rõ | `T-DL-04` `sending → unknown` | Timeout / mất kết nối / crash sau điểm có thể đã gửi |
| Đến hạn | `T-DL-05` `retry_wait → pending` | Cùng `logical_delivery_key` |
| Quyết định | `T-DL-06` `unknown → pending\|failed\|cancelled` | **Chỉ** qua `delivery.decide_unknown` (người dùng) |
| Hết budget | `T-DL-07` → `failed` | App vẫn giữ report |
| Đổi liên kết | `T-DL-08` `pending\|retry_wait → cancelled` | Không gửi tới recipient cũ, không chuyển sang recipient mới |

### 4.1 Ghi attempt trước network call

SRC-PLAN §8.3 nguyên văn. Lý do: nếu tiến trình chết ngay sau khi gọi mạng, hàng attempt đã
commit cho phép hệ thống biết **có thể đã gửi** thay vì gửi lại mù. Không có hàng attempt thì
mọi crash đều trông giống "chưa gửi", và đó là cách sinh ra tin trùng.

### 4.2 Số

Trích từ `contracts/retry-policy.yaml` (**không** đặt số mới ở đây):

| Budget | Giá trị | Đơn vị |
| --- | --- | --- |
| `telegram_send_attempts` | 4 | attempts mỗi `delivery_part` |
| `telegram_send_backoff` | 5 / 30 / 300 / 1800 (jitter ±20%) | giây |
| `telegram_send_max_window` | 21600 (6 giờ) kể từ `delivery.created_at` | giây |
| `telegram_attempt_before_send` | 1 hàng durable trước network call | — |
| `delivery_sender_lease_ttl` | 120 | giây |
| `delivery_alert_per_run` | 1 | intent mỗi run |

Tất cả `PROVISIONAL` theo PC03. `Retry-After` của Telegram thắng mọi giá trị trên.

## 5. `unknown`: điều được hứa và điều không

### 5.1 AMD-B03 — sửa REQ-AC14

**REQ-AC14 nguyên văn:** *"app vẫn giữ báo cáo đầy đủ và không có tin nào bị gửi hai lần."*

**Vấn đề** (SRC-PLAN §3.1): tài liệu `sendMessage` không có tham số idempotency key do client
cung cấp. Nếu request đã tới Telegram nhưng phản hồi mất, hệ thống **không thể biết** tin đã
gửi hay chưa. Một UNIQUE trong SQLite chứng minh hệ thống không tự gọi hai lần; nó không chứng
minh người nhận không thấy hai tin.

**Văn bản thay thế (AMD-B03):**

> Given báo cáo đã dựng và Telegram gửi thất bại
> When retry
> Then app vẫn giữ báo cáo đầy đủ; hệ thống **không tự động gửi lại một phần mà nó không biết
> chắc đã gửi hay chưa**; phần đó được đánh dấu `unknown` và hiển thị riêng cho người dùng
> quyết định.

**Điều được bảo đảm:**

1. Không có lần gửi tự động nào cho một `delivery_part` ở `unknown` (`forbidden_transitions`:
   `unknown → sending` tự động bị cấm).
2. Mỗi lần gửi ra ngoài có đúng một hàng attempt commit trước đó.
3. `sent` chỉ được ghi khi có `provider_message_id` thật.
4. Report trong app không đổi ở mọi nhánh (`report.content_hash` trước/sau bằng nhau).
5. `run.outcome` không đổi vì kết quả delivery (I09).

**Điều KHÔNG được bảo đảm:** người nhận không bao giờ thấy tin trùng. Nếu người dùng chọn
`resend_accepting_duplicate_risk`, tin trùng là kết quả **đã được chấp nhận tường minh**, không
phải lỗi.

### 5.2 Quyết định của người dùng

`delivery.decide_unknown` (auth `owner_session`, chỉ trong app):

| Lựa chọn | Nghĩa | Hệ quả |
| --- | --- | --- |
| `resend_accepting_duplicate_risk` | Chấp nhận nguy cơ trùng | part → `pending`, gửi lại; UI **phải** nói rõ nguy cơ trước khi xác nhận |
| `mark_not_delivered` | Coi như chưa tới | part → `failed`; không gửi lại |
| `abandon` | Bỏ qua | part → `cancelled` |

Hệ thống không bao giờ tự chọn. Không có timeout tự chuyển `unknown` sang trạng thái khác.

### 5.3 Part `unknown` trong digest nhiều phần

`DP-02` là quy tắc quan trọng nhất: **một part `unknown` không được gửi lại chỉ vì aggregate
chưa `sent`**. Aggregate được suy ra từ các part với thứ tự ưu tiên
`unknown > failed > retry_wait > sending > pending > sent` (`DP-03`) — trạng thái cần chú ý
nhất thắng, để UI không bao giờ nói "đã gửi" khi còn một phần chưa rõ (I13).

Fixture (a) là ca này: part 1 `sent`, part 2 `unknown` ⇒ aggregate `unknown`, số lần gửi lại
tự động = 0, và part 1 **không** bị gửi lại.

## 6. Cảnh báo `needs_user`

| Thuộc tính | Giá trị |
| --- | --- |
| Kind | `run_alert` |
| Số lượng | **Đúng một intent cho một run** (`delivery_alert_per_run` = 1, REQ-AC04) |
| Tạo khi | Transaction ghi `run.status = needs_user` |
| Nội dung | Đợt đang chờ xác minh; hướng dẫn xử lý trên máy cá nhân; **trỏ vào app** để bấm Tiếp tục |
| Cấm | Lặp cảnh báo cho cùng run; kèm nút resume trong tin (resume là hành động app, AMD-B10) |

Oracle: một run gặp CAPTCHA hai lần vẫn chỉ có `COUNT(run_alert intent) = 1`.

## 7. Kỳ rỗng, chạy bù, giờ yên lặng

- **Kỳ rỗng:** không digest (REQ-D57). Trạng thái ghi ở run và coverage ledger. Không gửi tin
  "hôm nay không có gì" — đó là tin rỗng đội lốt nội dung.
- **Chạy bù:** nhiều đợt quá hạn gộp thành một; tin ghi **khoảng bao trùm** (REQ-D15).
  Không gửi bù các báo cáo cũ (REQ-D16).
- **Giờ yên lặng:** REQ-OQ07 chưa có câu trả lời. **PROVISIONAL: không có giờ yên lặng** —
  digest gửi ngay khi publish. Nếu Owner muốn, giờ yên lặng làm **hoãn** intent, không **hủy**
  nó, và không bao giờ làm mất một digest.

## 8. Nút Save trong digest

Payload, thứ tự kiểm tra và mẫu phản hồi ở `contracts/telegram/commands.yaml` §CMD-save.
Ràng buộc thuộc file này:

- Nút được dựng từ **report revision đã publish**; `rv` = 8 ký tự đầu của `report.content_hash`.
- Nút gắn `telegram_link_generation` lúc dựng payload; generation đổi ⇒ callback cũ không Save.
- Bấm 5 lần ⇒ một `saved_item`, năm phản hồi (REQ-D38, SRC-SPEC §8.2 hàng 10).
- Snapshot chụp từ analysis revision của `report_item` trong kỳ đó, không phải bản mới hơn.

## 9. Điều tuyệt đối không làm

| # | Cấm | Căn cứ |
| --- | --- | --- |
| 1 | Gửi lại tự động một part `unknown` | AMD-B03, `forbidden_transitions` |
| 2 | Hiển thị `unknown` thành `sent` hoặc `failed` | I13 |
| 3 | Đổi `run.status`/`run.outcome` theo kết quả delivery | I09 |
| 4 | Đổi nội dung report đã publish khi gửi | I05, B01 |
| 5 | Chuyển payload của recipient cũ sang recipient mới | SRC-PLAN §8.3 |
| 6 | Gọi mạng bên trong transaction SQLite | SRC-PLAN §5.1 |
| 7 | Gửi khi trạng thái kho là `recovery_required` | I15 |
| 8 | Gửi digest cho kỳ rỗng | REQ-D57 |
| 9 | Hơn một alert intent cho một run | REQ-AC04 |
| 10 | Để nội dung nguồn quyết định recipient hoặc chèn markup | I11, REQ-AC17 |
| 11 | Xóa report khi delivery `failed` | REQ-AC14 |
| 12 | Suy ra giới hạn định dạng Telegram từ trí nhớ thay vì tài liệu | §3.4, SRC-SPEC §13.2 |
