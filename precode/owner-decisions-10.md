---
contract_id: CT-precode-owner-decisions-10
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260908-10
issuer: Owner (người dùng của phiên Claude Code này), qua AskUserQuestion sau commit Giai đoạn 3/5 `fb3944a`
issued_at: 2026-09-08
evidence_ref: "Claude Code session session_017CTbS7F4oTr4ZtFYkhdabD, 2026-09-08"
authority_created: AUTH-OWNER-20260908-11
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-10.md (bản gốc của biên bản này)"
  - precode/owner-decisions-09.md (OD-20260908-09 — Giai đoạn 5 phạm vi văn bản thuần)
  - precode/decision-register.md §8.14.x (CR-PC07-04 còn PARTIALLY_RESOLVED)
  - agent-tasks/TC-saved-snapshot.md, agent-tasks/TC-telegram-linking-auth.md
requirement_refs: [precode/requirements.csv, REQ-AC11, REQ-D36, REQ-S11.3-01]
decision_refs: [OD-20260908-09, AMD-B16, CR-TC-SAVED-04, CR-TC-TGAUTH-02, CR-TC-TGAUTH-04, CR-PC07-04]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-09.md, precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-08, vòng mười (ba mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Ba mục đều là câu hỏi do card Giai đoạn 5 nêu ra khi
  chạm phải một ràng buộc đã chốt (B16, CR-PC07-04, quy tắc im lặng với chat lạ). Nó KHÔNG giải
  CR-PC07-04 và KHÔNG sửa fixture nào.
verification: E0 — self-validation (EV-PC00-16) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260908-10` — 2026-09-08 (vòng mười)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260908-10` |
| Người ban hành | **Owner** — qua `AskUserQuestion`, **sau** commit Giai đoạn 3/5 `fb3944a` |
| `evidence_ref` | Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08 |
| Authority phát sinh | **`AUTH-OWNER-20260908-11`** |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260908-10.md` |

**Quy tắc chuyển ngữ.** Cột "Quyết định của Owner" là câu trả lời **nguyên văn**; cột "Hiệu lực" là hệ quả do
**chính biên bản** nêu. Ghi chú của PC00 nằm ngoài bảng (§4, §5).

## 2. Ba quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | `CR-TC-SAVED-04` — lưu một target **chưa có** analysis (B16 cấm bịa dòng summary; hiện đang từ chối bằng `VALIDATION_ERROR`, 0 hàng) | **Cho phép lưu; hiển thị nhãn "chưa phân tích"** | `save.create` **thành công** với khối summary được đánh dấu **thiếu tường minh** (**không** văn bản bịa); một analysis sau này có thể được gắn vào bằng reanalysis. Do `TC-saved-snapshot` (W5B) hiện thực; câu chữ nhãn là một **chuỗi cố định, không suy luận**; nếu chưa có trường schema mang nhãn đó thì một CR hợp đồng được mở. |
| 2 | `CR-TC-TGAUTH-02` — trigger Save tạm thời từ Telegram trong lúc nút callback còn bị chặn (`CR-PC07-04`) | **Giữ `/save <id>` làm trigger văn bản thuần** | Giữ **cho tới khi** nút inline khả thi; ánh xạ vào `CMD-save` đã có; **không** thêm lệnh hợp đồng mới. |
| 3 | `CR-TC-TGAUTH-04` — một chat **đã liên kết** gửi văn bản ngoài allowlist ba lệnh (fixture quét biên: im lặng; `commands.yaml`: nhắc) | **Nhắc ngắn ba lệnh** (chỉ chat **đã liên kết**; chat **lạ vẫn im lặng**, 0 outbound) | Mã như đã ship **đứng nguyên**; hàng fixture quét biên được sửa ở **vòng hợp đồng kế tiếp** (CR cho PC08). |

## 3. Vì sao ba mục này là quyết định của Owner, không phải lựa chọn kỹ thuật

Cả ba đều là chỗ một card **chạm vào một ràng buộc đã chốt** và dừng lại thay vì tự chọn — đúng hành vi
`worker.md` đòi. Chúng khác nhau về loại, và loại ấy đáng ghi:

- **Mục 1 chạm `AMD-B16`.** B16 cấm bịa phát biểu; nên "lưu một target chưa phân tích" biến thành một câu hỏi
  thật: **từ chối lưu**, hay **lưu kèm một chỗ trống có nhãn**? Owner chọn vế thứ hai, và biên bản buộc nhãn
  là **chuỗi cố định, không suy luận** — nghĩa là B16 **không** bị nới, chỉ được áp theo cách khác: chỗ trống
  được **nói ra**, không được **lấp**.
- **Mục 2 chạm `CR-PC07-04`.** Nút inline cần độ dài `callback_data` — một trong ba dữ kiện **vẫn**
  `BLOCKED_DEPENDENCY`. Owner giữ `/save <id>` làm đường tạm, **ánh xạ vào lệnh đã có**, **không** thêm lệnh
  hợp đồng. Đây là một quyết định **có hạn**: nó tự hết vai khi dữ kiện kia được giải.
- **Mục 3 chạm một mâu thuẫn giữa hai artifact đã đóng băng** — fixture quét biên nói "im lặng", còn
  `commands.yaml` nói "nhắc". Owner chốt theo `commands.yaml` cho chat **đã liên kết**, và **giữ nguyên** quy
  tắc im lặng cho chat **lạ**. Ranh giới ấy là phần quan trọng nhất của mục này: nó bảo toàn `AMD-B09`
  (không phản hồi gì với chat chưa liên kết ngoài mã liên kết hợp lệ).

## 4. Những gì quyết định này **không** làm

1. **Không giải `CR-PC07-04`.** Vẫn `PARTIALLY_RESOLVED`; ba dữ kiện vẫn `BLOCKED_DEPENDENCY`. Mục 2 là một
   **đường vòng có nhãn**, không phải một lời giải.
2. **Không nới `AMD-B16`.** Nhãn "chưa phân tích" là chuỗi cố định; **không** văn bản suy luận nào được sinh.
   Nếu ai đó hiện thực nó thành một câu do model viết thì đó là vi phạm B16, không phải thi hành mục 1.
3. **Không cho chat lạ nhận bất kỳ outbound nào.** Chỉ chat **đã liên kết** được nhắc; chat lạ giữ **0
   outbound**, đúng `AMD-B09`.
4. **Không sửa fixture nào ở vòng này.** Hàng fixture quét biên được sửa ở **vòng hợp đồng kế tiếp** — một CR
   cho **PC08**, không phải việc của PC00 và không phải việc của gói này. → `CR-PC00-34`.
5. **Không thêm lệnh Telegram.** Vẫn đúng **ba** lệnh (`AMD-B10`, `F-PC00-01`); `/save <id>` ánh xạ vào
   `CMD-save` đã có.
6. **Không nâng trần claim của file nào và không đóng finding nào.**

## 5. Trạng thái Giai đoạn 4/6 tại thời điểm ghi — sự kiện, không phải tuyên bố

Ghi theo yêu cầu của Coordinator, và cố ý **chỉ** là sự kiện có ngày:

Tính đến **2026-09-08**, đợt **sáu card** của Giai đoạn 4 (M4/M5) và Giai đoạn 6 (M7/M8) — `report`,
`backfill`, `ui-runs`, `ui-reports`, `scheduler`, `backup` — **đã land** và đang ở **vòng sửa trước khi đóng
băng**.

**Đây không phải một claim.** Chưa có freeze, chưa có manifest `FC-P4`, chưa có audit độc lập, và PC00
**không** nói gì về chất lượng hay mức bằng chứng của sáu card ấy. Nhãn của chúng sẽ do vòng audit tương ứng
quyết định, không do dòng này. Ghi lại chỉ để hồ sơ có mốc: vòng mười của Owner xảy ra **trong khi** đợt đó
đang chạy, và ba câu hỏi ở §2 đến từ các card Giai đoạn 5 đã ship trước đó.

## 6. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/owner-decisions.md` | Dòng trỏ tới biên bản vòng mười |
| `precode/decision-register.md` §0 | Nhãn `ACCEPTED (OD-20260908-10)` và đoạn "Cập nhật vòng mười" |
| `precode/owner-decision-request.md` | Phiếu trả lời vòng mười |
| `precode/baseline.json` | Anchor `OD-20260908-10` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260908-11` |
| `agent-tasks/TC-saved-snapshot.md`, `TC-telegram-linking-auth.md` | **Không sửa ở gói này** — thuộc PC10/W5B |
| `acceptance/fixtures/**` (hàng quét biên) | **Không sửa** — vòng hợp đồng kế tiếp, CR cho PC08 (`CR-PC00-34`) |
| `precode/requirements.csv` | **Không sửa** |
