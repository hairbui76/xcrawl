---
contract_id: CT-precode-owner-decisions-09
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260908-09
issuer: Owner (người dùng của phiên Claude Code này), qua phỏng vấn AskUserQuestion
issued_at: 2026-09-08
evidence_ref: "Claude Code session session_017CTbS7F4oTr4ZtFYkhdabD, 2026-09-08"
authority_created: AUTH-OWNER-20260908-10
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-09.md (bản gốc của biên bản này)"
  - precode/owner-decisions-05.md (OD-20260908-05 — cấp quyền đọc tài liệu và lối vào Giai đoạn 5 có điều kiện)
  - precode/decision-register.md §8.14, §8.14.1, §8.14.2, §8.14.3
  - contracts/telegram/delivery.md §3.4
requirement_refs: [precode/requirements.csv, REQ-A7]
decision_refs: [OD-20260908-05, OD-20260908-07, CR-PC07-04, CR-PC00-31]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-05.md, precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-08, vòng chín (một mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó THAY THẾ điều kiện khởi động Giai đoạn 5 của
  OD-20260908-05 (từ "năm dữ kiện land" thành "khởi động có phạm vi, chỉ văn bản thuần") và
  KHÔNG giải ba dữ kiện Telegram còn lại.
verification: E0 — self-validation (EV-PC00-14) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260908-09` — 2026-09-08 (vòng chín)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260908-09` |
| Người ban hành | **Owner** — qua phỏng vấn `AskUserQuestion` |
| `evidence_ref` | Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08 |
| Authority phát sinh | **`AUTH-OWNER-20260908-10`** — parent của lượt dispatch Giai đoạn 5 **có phạm vi** |
| Biên bản liên quan | `OD-20260908-05` (điều kiện cũ), `OD-20260908-07` (nới quyền tìm kiếm ở vòng ba) |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260908-09.md` do Coordinator phát |

**Quy tắc chuyển ngữ.** File này ghi lại nguyên nội dung biên bản. Cột "Quyết định của Owner" là câu trả lời
**nguyên văn**; cột "Hiệu lực" là hệ quả do **chính biên bản** nêu. Ghi chú của PC00 nằm ngoài bảng (§4–§6).

## 2. Một quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | Phạm vi Giai đoạn 5 (Telegram), trong tình huống `CR-PC07-04` **vẫn** `PARTIALLY_RESOLVED` (2/5 dữ kiện — độ dài tin tối đa, rate limit gửi; `callback_data`/escape parse-mode/số nút mỗi hàng bị chặn thật sự bởi **giới hạn kích thước trang của công cụ đọc**, **không** phải một khoảng trống chính sách) | **Bắt đầu với văn bản thuần ngay, thêm định dạng sau** | Các card Giai đoạn 5 (`TC-telegram-linking-auth` → `TC-saved-snapshot` → `TC-telegram-unknown-delivery`) được phép khởi động, **giới hạn ở tin nhắn văn bản thuần**: cắt tin theo giới hạn 4096 ký tự và điều tiết nhịp gửi bằng **hai** dữ kiện đã giải. **Không** `parse_mode` (Markdown/HTML), **không** inline keyboard, **không** nút mang `callback_data` — ba đường mã đó **chưa được hiện thực** (**không** phải stub-rồi-giấu; **tường minh nằm ngoài phạm vi**, có `SG-01` canh) cho tới khi ba dữ kiện còn lại được giải. |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này: ba dữ kiện Telegram còn lại rốt cuộc sẽ được giải **bằng cách nào** (một amendment
> công cụ cho phép fetch phân trang, hoặc Owner tự đọc trang ấy) — hoãn sang một vòng sau.

## 4. Điều vòng này **thay đổi** so với `OD-20260908-05` — và điều nó không

Đây là điểm dễ ghi sai nhất, nên nói thẳng: **điều kiện khởi động Giai đoạn 5 đã được THAY, không phải đã
được THỎA.**

| | `OD-20260908-05` mục 2 | `OD-20260908-09` mục 1 |
| --- | --- | --- |
| Điều kiện | *"một khi **năm** dữ kiện land"* | *"bắt đầu với văn bản thuần ngay"* |
| Trạng thái điều kiện cũ | **chưa bao giờ thỏa** — 2/5 | **không còn hiệu lực**, bị thay thế |
| Phạm vi cho phép | toàn bộ Giai đoạn 5 (ngầm) | **chỉ văn bản thuần** |

`CR-PC00-31` — mục tôi mở ở `PKT-PC00-FIX26` để hỏi *"ai kết luận Giai đoạn 5 có được khởi động không"* —
nay **đã được giải, và giải bằng đúng cách đáng lẽ phải thế**: Owner **đổi điều kiện** thay vì để ai đó tuyên
bố điều kiện cũ đã thỏa. Ghi `condition_met: true` cho điều kiện *"năm dữ kiện land"* sẽ là một câu **sai
kiểm được**: nó vẫn là 2/5. Vì vậy `agent_profile/registry.json` ghi lại **cả hai** — điều kiện cũ kèm trạng
thái *chưa thỏa, đã bị thay*, và điều kiện mới kèm phạm vi của nó.

**`CR-PC07-04` vẫn `PARTIALLY_RESOLVED`, không `CLOSED`.** Ba dữ kiện vẫn `BLOCKED_DEPENDENCY`. Vòng chín
**không** giải chúng; nó quyết định **đi tiếp mà không cần chúng**, bằng cách cắt bỏ đúng phần công việc phụ
thuộc vào chúng.

## 5. Vì sao "chưa hiện thực" khác "stub rồi giấu" — và vì sao biên bản nói rõ điều đó

Biên bản dùng đúng cụm *"stay unimplemented (not stubbed-and-hidden; explicitly out of scope, `SG-01`-guarded)"*.
Khác biệt ấy là thật, không phải cách nói:

- **Stub rồi giấu** nghĩa là có một hàm `send_with_parse_mode` trả về gì đó trông hợp lệ. Người gọi tiếp theo
  không có cách nào biết nó chưa dựa trên một dữ kiện đã kiểm — và một giới hạn `callback_data` **đoán** sẽ
  đi vào mã sản phẩm mà không ai thấy.
- **Tường minh ngoài phạm vi + `SG-01` canh** nghĩa là đường mã ấy **không tồn tại**, và nếu ai đó gọi tới
  thì gặp một guard dừng lại có tên. Một khoảng trống **ồn ào** thì an toàn; một khoảng trống **im lặng** thì
  không.

Đây cùng một luật đã áp cho `research_connector_rate_limit` khi bốn giá trị còn `null`: connector **từ chối
khởi động** thay vì chạy với số đoán. Vòng chín áp lại luật ấy cho Telegram.

**Hai dữ kiện được dùng đều có nguồn trích dẫn nguyên văn** (§8.14.1): 4096 ký tự cho `sendMessage.text`; và
nhịp gửi 1 tin/giây trong một chat, 20 tin/phút trong một group, ~30 tin/giây khi broadcast. Việc cắt tin và
điều tiết nhịp vì vậy đứng trên dữ kiện, không trên phỏng đoán — đó chính là điều làm cho phạm vi hẹp này
hợp lệ.

## 6. Những gì quyết định này **không** làm

1. **Không giải `CR-PC07-04`.** Vẫn `PARTIALLY_RESOLVED`; ba dữ kiện vẫn `BLOCKED_DEPENDENCY` (§8.14.3 ghi
   cả ba đường đã thử ở vòng ba, gồm cả việc `web.archive.org` **bị chặn ở tầng công cụ**).
2. **Không cho phép định dạng hay bàn phím.** `parse_mode`, inline keyboard và `callback_data` **ngoài phạm
   vi**, có guard. Không ai được "tạm" thêm chúng.
3. **Không mở quyền mạng mới.** Quyền đọc tài liệu `core.telegram.org` của `OD-20260908-05` và phần nới tìm
   kiếm của `OD-20260908-07` giữ nguyên như đã cấp; `api.telegram.org` vẫn **cấm**, không bot token, không
   gửi tin thật.
4. **Không tạo bằng chứng runtime.** Cho phép **viết** mã Giai đoạn 5 không phải là đã chạy nó; E3/E4 vẫn
   `NOT_RUN`, và `REQ-A7` không đổi.
5. **Không nâng trần claim của file nào** và **không đóng finding nào.**

## 7. Ghi chú quy trình — hai lần lease chồng nhau trong vòng này

Ghi theo yêu cầu của Coordinator, cùng tinh thần với bài học "đóng băng `precode/`":

Chuỗi công việc dẫn tới biên bản này (chọn `REQ-OQ03` → nghiên cứu điều khoản Anthropic cho `REQ-A5` → Owner
ký `REQ-A5` → ba vòng tìm dữ kiện Telegram → vòng chín) có **hai** lần Coordinator dispatch tạo **lease chồng
nhau** giữa `worker-WT` và `worker-WAI`. Cả hai lần đều được kiểm và **không mất dữ liệu**.

**Nhưng "không mất dữ liệu" là một kết quả, không phải một bảo đảm.** Dưới `PROV-PC00-08`, lease được theo dõi
bằng **thông điệp**, không có fencing thật: hai Worker cùng ghi một file sẽ **không** bị nền tảng chặn, và
lần ghi sau đơn giản đè lên lần trước. Việc hai lần ấy vô hại là nhờ hai Worker tình cờ chạm vùng khác nhau —
không nhờ một cơ chế nào ngăn điều ngược lại. Đây đúng là chế độ hỏng (b) mà `PROV-PC00-08` đã liệt kê khi
Owner chấp nhận rủi ro còn lại, nay xảy ra thật **hai lần trong một vòng**.

Điều tự nó cứu được hồ sơ trong cả hai lần vẫn là thứ đã cứu ba lần trước: **mỗi phát biểu mang mốc thời
gian, và mỗi Worker đọc lại file ngay trước khi ghi** thay vì tin vào bản đọc cũ. Ở chính gói này tôi gặp lại
điều đó — `decision-register.md` đã đổi byte giữa lúc tôi đọc và lúc tôi ghi, và cách xử lý đúng là đọc lại
rồi **thêm** vào phần của mình, không phải viết đè.

**Đề nghị** (không phải quyết định của tôi): nếu còn nhiều vòng song song nữa, rẻ nhất là Coordinator **không
cấp hai packet chạm cùng một file trong cùng một cửa sổ**, thay vì trông vào việc các Worker tránh nhau. → `CR-PC00-32`.

## 8. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/owner-decisions.md` | Dòng trỏ tới biên bản vòng chín này |
| `precode/decision-register.md` §0 | Nhãn `ACCEPTED (OD-20260908-09)` và đoạn "Cập nhật vòng chín" |
| `precode/decision-register.md` §8.14.x | **Của `worker-WT`** — ba vòng tìm dữ kiện; PC00 **không** chạm |
| `precode/owner-decision-request.md` | Phiếu trả lời vòng chín |
| `precode/baseline.json` | Anchor `OD-20260908-09` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260908-10`; `phase_5_conditional_entry` ghi **cả** điều kiện cũ (chưa thỏa, đã bị thay) **và** điều kiện mới |
| `contracts/telegram/delivery.md` | **Không sửa ở gói này** — thuộc PC07 |
| `precode/requirements.csv` | **Không sửa** |
