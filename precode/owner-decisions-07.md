---
contract_id: CT-precode-owner-decisions-07
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260908-07
issuer: Owner (người dùng của phiên Claude Code này), qua phỏng vấn AskUserQuestion sau báo cáo trạng thái của hai Worker (WT/WAI)
issued_at: 2026-09-08
evidence_ref: "Claude Code session session_017CTbS7F4oTr4ZtFYkhdabD, 2026-09-08"
authority_created: AUTH-OWNER-20260908-08
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-07.md (bản gốc của biên bản này)"
  - precode/owner-decisions-05.md (OD-20260908-05 — quyền đọc tài liệu Telegram ban đầu)
  - precode/decision-register.md §8.14.2, §8.14.3
  - contracts/ai/providers.yaml §5
requirement_refs: [precode/requirements.csv, REQ-A5]
decision_refs: [OD-20260908-05, OD-20260908-08, CR-PC07-04, CR-PC06-OQ03-02]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-05.md, precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-08, vòng bảy (hai mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó NỚI quyền tìm dữ kiện Telegram sang WebSearch (vẫn
  chỉ để định vị nội dung của chính trang tài liệu ấy) và chốt rằng người ký REQ-A5 phải là
  Owner, không phải một Worker được ủy quyền. Hiệu lực thực chất đã được worker-WT ghi ở §8.14.3;
  file này là bản ghi song hành theo quy ước, KHÔNG quyết lại điều gì.
verification: E0 — self-validation (EV-PC00-15) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260908-07` — 2026-09-08 (vòng bảy)

> **File này là bản ghi SONG HÀNH THEO QUY ƯỚC, không phải nơi quyết định.** Hiệu lực thực chất của vòng bảy
> đã được `worker-WT` ghi ở `precode/decision-register.md` **§8.14.3** ngay khi nó xảy ra. `PKT-PC00-FIX28`
> tạo file này để vòng bảy có cùng hình dạng hồ sơ như các vòng khác (file độc lập + anchor baseline +
> authority trong registry) — **không** để quyết lại điều gì. Khi hai bên lệch: **§8.14.3 thắng**.

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260908-07` |
| Người ban hành | **Owner** — qua phỏng vấn `AskUserQuestion`, sau báo cáo trạng thái của **hai** Worker (`WT`/`WAI`) |
| `evidence_ref` | Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08 |
| Authority phát sinh | **`AUTH-OWNER-20260908-08`** — parent của lượt tìm dữ kiện Telegram **đã nới quyền** |
| Bản ghi hiệu lực | `precode/decision-register.md` **§8.14.3** (`worker-WT`) |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260908-07.md` |

**Quy tắc chuyển ngữ.** Cột "Quyết định của Owner" là câu trả lời **nguyên văn**; cột "Hiệu lực" là hệ quả do
**chính biên bản** nêu. Ghi chú của PC00 nằm ngoài bảng (§4).

## 2. Hai quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | Ba dữ kiện Telegram còn lại (độ dài `callback_data`, bảng escape parse-mode, số nút mỗi hàng/bàn phím) bị chặn bởi một **cắt cụt của công cụ fetch** trên `core.telegram.org/bots/api`, **không** phải một vấn đề phạm vi | **Nới quyền: cho phép thêm một lần tìm kiếm web** (mọi luật chỉ-đọc-tài-liệu khác giữ nguyên — không gọi Bot API thật, không bot token, không gửi gì) | Worker nay được dùng **WebSearch** (không chỉ `WebFetch` trên bốn/năm host đã nêu trước) để tìm **một đường đọc tới các phần bị cắt của chính trang ấy** — ví dụ một bản cache/lưu trữ của `core.telegram.org/bots/api`. Truy vấn tìm kiếm **phải** xoay quanh việc **định vị nội dung của trang ấy**; nó **không** cho phép lấy một con số **khác** từ các site Telegram-lân-cận tùy ý. Vẫn cấm: `api.telegram.org`, mọi bot token, mọi lần gửi tin. |
| 2 | Người duyệt `REQ-A5` theo `contracts/ai/providers.yaml` §5 lẽ ra phải là **Owner đích thân**, không phải một Worker được ủy quyền (`CR-PC06-OQ03-02`) | **Owner sẽ tự đọc và ký** | Coordinator trình phát hiện của Worker (trích dẫn, câu trích, hai điều kiện còn mở) **trực tiếp** cho Owner trong phiên này để thực sự duyệt và ký — xem phần tiếp theo trong cùng lượt. Cho tới khi Owner ký tường minh, `CR-PC06-OQ03-02` **vẫn mở** và trường reviewer **không** được điền tên một Worker. |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này: chính chữ ký `REQ-A5` (được hỏi ngay sau đó trong cùng lượt, tách riêng khỏi biên
> bản này).

Chữ ký ấy là **`OD-20260908-08`** — `precode/owner-decisions-08.md`, §8.15.1.

## 4. Ghi chú của PC00

- **Mục 1 nới đúng một bậc, và biên bản tự vẽ ranh giới.** Điều được mở là **công cụ** (`WebSearch` cạnh
  `WebFetch`), **không** phải phạm vi nội dung: mục tiêu vẫn là **chính trang** `core.telegram.org/bots/api`.
  Câu *"không cho phép lấy một con số khác từ một site khác"* là ranh giới đáng giữ — nếu bỏ nó, một hạn mức
  đọc được từ blog của bên thứ ba sẽ đi vào hợp đồng dưới danh nghĩa "tài liệu chính thức". Đây chính là
  điều mà `worker-WT` đã dừng lại ở vòng hai (§8.14.2) và Owner nay giải bằng một **amendment quyền**, đúng
  cách mà bản ghi vòng hai đã nói là cách duy nhất hợp lệ.
- **Nới quyền KHÔNG kéo theo kết quả.** Vòng ba đã chạy dưới quyền mới và **cả ba dữ kiện vẫn
  `BLOCKED_DEPENDENCY`** — WebSearch giới hạn host không trả về câu cần trích, còn `web.archive.org` **bị
  chặn ở tầng công cụ** (không phải 404, không phải quyền). Chi tiết ở §8.14.3. Một quyền rộng hơn chỉ mở
  thêm đường thử; nó không tạo ra dữ kiện.
- **Mục 2 là một sửa sai về THẨM QUYỀN, không phải về nội dung.** Worker đã đọc điều khoản đúng và ghi đủ
  trích dẫn; cái sai là **ai được ký**. `providers.yaml` §5 nói reviewer là Owner, và điền tên một Worker vào
  đó sẽ làm một trường thẩm quyền nói sai sự thật. Owner chọn tự đọc — nên `CR-PC06-OQ03-02` **giữ mở** qua
  hết vòng bảy và chỉ đóng ở vòng tám.

## 5. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/decision-register.md` §8.14.3 | **Bản ghi hiệu lực** (`worker-WT`) — PC00 **không** chạm |
| `precode/decision-register.md` §0 | Đoạn "Cập nhật vòng bảy và vòng tám" |
| `precode/owner-decisions.md` | Dòng trỏ |
| `precode/baseline.json` | Anchor `OD-20260908-07` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260908-08` |
| `precode/requirements.csv` | **Không sửa** |
