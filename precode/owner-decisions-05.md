---
contract_id: CT-precode-owner-decisions-05
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260908-05
issuer: Owner (người dùng của phiên Claude Code này), qua phỏng vấn AskUserQuestion sau báo cáo trạng thái của Coordinator
issued_at: 2026-09-08
evidence_ref: "Claude Code session session_017CTbS7F4oTr4ZtFYkhdabD, 2026-09-08"
authority_created: AUTH-OWNER-20260908-06
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-05.md (bản gốc của biên bản này)"
  - precode/owner-decisions-04.md (OD-20260907-04 — vòng trước)
  - contracts/ai/providers.yaml, contracts/ai/tasks.yaml
  - contracts/telegram/delivery.md §3.4
  - precode/decision-register.md §8.14, §8.14.1, §8.14.2
requirement_refs: [precode/requirements.csv, REQ-OQ03, REQ-A5]
decision_refs: [OD-20260907-04, OD-20260908-06, CR-PC07-04]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-04.md, precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-08, vòng năm (hai mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó ỦY QUYỀN việc nghiên cứu REQ-OQ03 (không giải nó) và
  cấp một quyền mạng hẹp chỉ-đọc-tài-liệu cho CR-PC07-04, kèm lối vào Giai đoạn 5 CÓ ĐIỀU KIỆN.
verification: E0 — self-validation (EV-PC00-13) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260908-05` — 2026-09-08 (vòng năm)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260908-05` |
| Người ban hành | **Owner** — qua phỏng vấn `AskUserQuestion`, tiếp sau báo cáo trạng thái *"đã làm hết chưa?"* của Coordinator |
| `evidence_ref` | Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08 |
| Authority phát sinh | **`AUTH-OWNER-20260908-06`** — parent của packet tìm dữ kiện Telegram **và** của lượt dispatch card Giai đoạn 5; **cũng** phủ nhiệm vụ nghiên cứu `REQ-OQ03` |
| Biên bản trước | `OD-20260907-01` … `OD-20260907-04` |
| Biên bản sau | **`OD-20260908-06`** — Owner tự chọn model cụ thể; ghi riêng bởi `worker-WAI`, **không** chép lại ở đây (§5) |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260908-05.md` do Coordinator phát |

**Quy tắc chuyển ngữ.** File này ghi lại nguyên nội dung biên bản. Cột "Quyết định của Owner" là câu trả lời
**nguyên văn**; cột "Hiệu lực" là hệ quả do **chính biên bản** nêu. Ở đâu PC00 thêm ghi chú, ghi chú đó nằm
ngoài bảng và được đánh dấu rõ (§4, §5, §6).

## 2. Hai quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | `REQ-OQ03` — nhà cung cấp AI và model cụ thể cho gán nhãn hàng loạt so với sinh summary; **không có mặc định an toàn** theo điều khoản `no_vendor_claims` của `contracts/ai/providers.yaml` | **Nghiên cứu và đề xuất; Owner phê duyệt cuối cùng** | Coordinator nghiên cứu các nhà cung cấp ứng viên đối chiếu yêu cầu kỹ thuật ở `contracts/ai/tasks.yaml`/`providers.yaml` (JSON output, báo cáo usage, cô lập, đồng thời) và đề xuất một lựa chọn. Việc này **tự nó không** giải `REQ-A5` (đọc điều khoản thật của đúng nhà cung cấp đó trước khi bật) — một Worker vẫn phải làm việc ấy **riêng**, trước khi bất kỳ adapter nào được đặt `enabled = true`. `REQ-OQ03` **giữ** `OWNER_DECISION_REQUIRED` cho tới khi Owner phê duyệt tường minh một đề xuất cụ thể. |
| 2 | `CR-PC07-04` — giới hạn định dạng của Telegram Bot API: **5** dữ kiện, `contracts/telegram/delivery.md` §3.4, hiện `KC` | **Lấy tài liệu ngay, khởi động Giai đoạn 5 song song** | Quyền mạng **một lần, phạm vi hẹp**: một Worker được tải **chỉ trang tài liệu** dưới `core.telegram.org` (cụ thể `core.telegram.org/bots/api`) để đọc và trích giới hạn định dạng hiện hành. **Không** gọi Bot API thật (**không** `api.telegram.org`), **không** dùng bot token, **không** gửi tin nào. Giai đoạn 5 (`TC-telegram-linking-auth` → `TC-saved-snapshot` → `TC-telegram-unknown-delivery`) được phép khởi động **một khi năm dữ kiện land**. |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này: lựa chọn `REQ-OQ03` thật (chờ nghiên cứu của Coordinator và một vòng phê duyệt
> tiếp theo của Owner); `REQ-A5` (đọc điều khoản của từng nhà cung cấp, một cổng riêng, theo từng adapter,
> mỗi khi một adapter được đề nghị bật).

## 4. Trạng thái thật của mục 2 tính đến lúc ghi file này — **Giai đoạn 5 CHƯA được gỡ chặn**

Đây là điều quan trọng nhất của bản ghi này, và nó **không** phải nội dung biên bản mà là **sự kiện quan sát
được** (2026-09-08). Điều kiện của Owner ở mục 2 là *"một khi **năm** dữ kiện land"*. Chúng **chưa** land.

`worker-WT` chạy hai vòng (`PKT-PC07-FIX-TELEGRAM`, rồi `PKT-PC07-FIX-TELEGRAM-2`). Kết quả:
**`CR-PC07-04` = `PARTIALLY_RESOLVED`** — **hai** trong năm dữ kiện có nguồn, **ba** vẫn `BLOCKED_DEPENDENCY`.
Bản ghi chuẩn là `precode/decision-register.md` **§8.14.1** và **§8.14.2**, do `worker-WT` viết; file này
**không** chép lại nội dung đó.

| Dữ kiện | Trạng thái |
| --- | --- |
| Độ dài tối đa một tin (`4096`) | `RESOLVED` |
| Rate limit gửi | `RESOLVED` |
| Độ dài `callback_data` | **`BLOCKED_DEPENDENCY`** |
| Parse mode + bảng escape | **`BLOCKED_DEPENDENCY`** |
| Số nút mỗi hàng / mỗi bàn phím | **`BLOCKED_DEPENDENCY`** |

**Vì vậy PC00 KHÔNG tuyên bố Giai đoạn 5 đã được gỡ chặn.** Điều kiện Owner đặt ra là năm, không phải hai;
2 ≠ 5. Quyết định đó thuộc Coordinator/Owner sau khi vòng của `WT` kết thúc, không phải hệ quả tự động của
biên bản này. → `CR-PC00-31`.

**Một chi tiết đáng giữ về vì sao ba dữ kiện kia dừng.** Chúng dừng vì **giới hạn công cụ đọc**, không vì
thiếu cố gắng — và ở vòng hai, Worker **từ chối** một `WebSearch` mà packet gợi ý, với lý do **quyền**: biên
bản này cấp quyền cho `core.telegram.org`, còn một truy vấn tìm kiếm là lời gọi tới **host khác**. Đó là
`BLOCKED_SCOPE` đúng nghĩa, và nó bảo vệ chính độ tin cậy của hai dữ kiện đã lấy được. Muốn đi hướng ấy cần
một **amendment của Owner**, không phải một câu trong packet.

## 5. Vòng sau — `OD-20260908-06` (không chép lại ở đây)

Mục 1 nói Owner sẽ phê duyệt sau. Việc đó **đã xảy ra** trong một vòng riêng: Owner tự chọn model cụ thể —
**Claude Sonnet 5** cho `label`/`direction_phrasing`, **Claude Opus 5** cho `summary`. Quyết định ấy là
**`OD-20260908-06`**, được ghi bởi `worker-WAI` ở bản ghi riêng của nó.

**PC00 cố ý KHÔNG chép nội dung đó vào đây**, vì hai lý do: (a) tránh hai bản ghi cùng mô tả một quyết định
rồi lệch nhau — đúng lớp lỗi mà `F-A1R1-01` đã phạt; (b) `OD-20260908-06` là một biên bản **riêng**, không
phải một phần của biên bản này. Dòng này chỉ là **con trỏ**. Khi hai bên lệch: **bản ghi của
`OD-20260908-06` thắng**.

**Hệ quả cho `REQ-OQ03` phải đọc từ bản ghi ấy, không phải từ đây.** Điều file này khẳng định là hẹp hơn
nhiều: tính đến `OD-20260908-05`, `REQ-OQ03` **vẫn** `OWNER_DECISION_REQUIRED` — vòng năm chỉ ủy quyền
**việc nghiên cứu**.

## 6. Những gì quyết định này **không** làm

Sáu điều dưới đây do PC00 ghi thêm; chúng suy trực tiếp từ §2 và §3 của chính biên bản.

1. **Không giải `REQ-OQ03`.** Vòng năm ủy quyền **nghiên cứu và đề xuất**; nó tự nói `REQ-OQ03` giữ
   `OWNER_DECISION_REQUIRED` cho tới khi Owner phê duyệt một đề xuất **cụ thể**. Một lời ủy quyền nghiên cứu
   không phải một quyết định sản phẩm.
2. **Không giải `REQ-A5`.** Biên bản nêu đích danh: đọc điều khoản thật của một nhà cung cấp là **cổng
   riêng**, theo **từng adapter**, và phải xong **trước** khi đặt `enabled = true`. Chọn được model không
   làm cổng ấy biến mất.
3. **Không gỡ chặn Giai đoạn 5.** Điều kiện là **năm** dữ kiện; hiện có **hai** (§4).
4. **Không mở mạng nói chung.** Quyền là **một lần** và **hẹp theo host**: chỉ `core.telegram.org`, chỉ
   **trang tài liệu**. `api.telegram.org` bị **cấm đích danh**; **không** bot token; **không** gửi tin. Quyền
   mạng nền không đổi: cài gói đã khai báo từ PyPI/npm (`OD-20260907-02` mục 4) cộng các allowlist đọc-tài-liệu
   đã cấp trước đó.
5. **Không nâng trần claim của file nào**, kể cả `contracts/telegram/delivery.md` — §8.14 ghi rõ điều đó.
6. **Không đóng finding nào**, và `CR-PC07-04` là `PARTIALLY_RESOLVED`, **không** `CLOSED`.

## 7. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/owner-decisions.md` | Dòng trỏ tới biên bản vòng năm này |
| `precode/decision-register.md` §0 | Nhãn `ACCEPTED (OD-20260908-05)` và đoạn "Cập nhật vòng năm" |
| `precode/decision-register.md` §8.14, §8.14.1, §8.14.2 | **Của `worker-WT`** — kết quả packet tìm dữ kiện; PC00 **không** chạm |
| `precode/decision-register.md` §8.15 | **Của `worker-WAI`** — `OD-20260908-06`; PC00 **không** chạm |
| `precode/owner-decision-request.md` | Phiếu trả lời vòng năm |
| `precode/baseline.json` | Anchor `OD-20260908-05` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260908-06` |
| `contracts/telegram/delivery.md` §3.4 | **Không sửa ở gói này** — thuộc PC07/`worker-WT` |
| `precode/requirements.csv` | **Không sửa** — `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED`, `REQ-A5` vẫn `KC` |
