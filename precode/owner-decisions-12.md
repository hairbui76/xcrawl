---
contract_id: CT-precode-owner-decisions-12
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20261017-12
issuer: Owner (người dùng của phiên Claude Code này), qua AskUserQuestion sau lượt kiểm tra trạng thái repo trên commit `8281274`
issued_at: 2026-10-17
evidence_ref: "Claude Code session session_01XQgXrAiGrnAUFS3jowQf2w, 2026-10-17"
authority_created: AUTH-OWNER-20261017-13
owner_role: requirements owner (PC00)
source_refs:
  - docs/owner-runbook.md §11 (bảng khoảng trống) và §12.2 (mười việc chỉ Owner làm được)
  - precode/owner-decisions-11.md (OD-20260909-11 — vòng trước)
  - evidence/handoffs/TC-secret-settings-service-handoff.md §8 (CR-TC-SECRET-01)
  - evidence/coordination/FIX-A3P5R1-rulings.md (F-A3-P5-03)
requirement_refs: [precode/requirements.csv]
decision_refs: [REQ-OQ04, REQ-OQ09, REQ-A3, CR-PC07-01, CR-TC-SECRET-01, CR-P0-07, CR-TC-BACKFILL-07, F-A3-P5-03]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/decision-register.md, precode/baseline.json, precode/change-control.md]
scope: >
  Biên bản quyết định của Owner ngày 2026-10-17, vòng mười hai (sáu mục). Owner trả lời qua hai lượt
  AskUserQuestion, mỗi câu có một phương án khuyến nghị; Owner chọn phương án khuyến nghị ở mọi câu.
  Khác với vòng mười một, không có bản ghi hiệu lực nào khác: file này VÀ decision-register §8.17
  là hai nửa của cùng một bản ghi, viết cùng lượt.
verification: E0 — self-validation + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20261017-12` — 2026-10-17 (vòng mười hai)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20261017-12` |
| Người ban hành | **Owner** — qua `AskUserQuestion`, sau lượt kiểm tra trạng thái repo trên `8281274` |
| `evidence_ref` | Claude Code session `session_01XQgXrAiGrnAUFS3jowQf2w`, 2026-10-17 |
| Authority phát sinh | **`AUTH-OWNER-20261017-13`** |
| Bản ghi hiệu lực | file này + `precode/decision-register.md` §8.17 |

## 2. Sáu quyết định

Mỗi câu hỏi đưa ra hai tới ba phương án, phương án đầu được đánh dấu *khuyến nghị*. Cột "Câu hỏi" chép ý,
không chép nguyên văn giao diện.

| # | Mục | Câu hỏi | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- | --- |
| 1 | `G-10` — token của `rr-backup` | Hệ chạy trên máy một người dùng hay máy dùng chung? | **Máy riêng một người dùng** | CLI so `sha256` của token với `RR_BACKUP_OPERATOR_TOKEN_SHA256` qua `Settings` — cùng digest server dùng; biến bản rõ `..._EXPECTED` thôi được đọc. **Không** sửa `secrets.md`: mô hình đe doạ được chọn **không** đòi token là ranh giới giữa các user cục bộ. Giới hạn ấy được ghi ở docstring của `tools/backup_cli.py` và `docs/owner-runbook.md` §9.1 |
| 2 | Các giá trị `PROVISIONAL` đang dùng | Chốt nguyên `N = 7` (`REQ-OQ04`) và ba tham số mã liên kết (`CR-PC07-01`: `^RR-[0-9A-HJKMNP-TV-Z]{8}$`, hạn 15 phút, 5 lần thử/chat/giờ)? | **Chốt nguyên như vậy** | `REQ-OQ04` `ĐX` → `XN`; `contracts/telegram/commands.yaml` ba mục `PROVISIONAL` → `ACCEPTED`, `ratified_by: OD-20261017-12`; `contracts/reporting/time-and-tags.md` §6.1 và §10, `contracts/ui/screens.yaml` cập nhật chữ. Version các file ấy **không** đổi — phê chuẩn không phải một thay đổi hợp đồng (quy ước của `AMD-ENT-owner-01`, `PKT-PC02-FIX14`) |
| 3 | `CR-TC-SECRET-01` — material của secret store | Chấp nhận file ngoài DB, hay chuyển vào một bảng? | **Chấp nhận file ngoài DB** | `contracts/ops/secrets.md` 0.1.0 → 0.1.1: ô "Nơi lưu ciphertext" của §4.1 nay nói đúng điều mã đang làm (một file `0600` mỗi locator trong thư mục `0700`, sau `SecretMaterialStore`) và vì sao `entities.yaml` **cố ý không** khai bảng; đoạn "Hệ quả" nói thêm rằng ciphertext cũng không có trong backup DB. `contracts/ops/backup-restore.md` 0.1.0 → 0.1.1: hàng master key của bảng khôi phục sửa cho khớp. Không đổi mã, không migration |
| 4 | `F-A3-P5-03` — `GET /v1/reports` trả `500` | Giữ `500` chờ `CR-P0-07`, hay thêm `503` vào `openapi.yaml`? | **Giữ `500`, chờ `CR-P0-07`** | Không sửa hợp đồng HTTP. Ruling `FIX-A3P5R1` ("dùng mã đã khai gần nhất, không bịa") đứng nguyên; lỗi hết khi `report_context` được nối |
| 5 | `REQ-OQ09` — model embedding | Chọn ứng viên làm việc rồi đo sau, hay giữ `BLOCKED` tới khi đo? | **Ứng viên làm việc `intfloat/multilingual-e5-small`, đo sau** | Ghi ở `precode/requirements.csv` `REQ-OQ09` như một giá trị `PROVISIONAL`. `REQ-OQ09` và `REQ-A3` **giữ `KC`**: chọn một ứng viên không phải đo nó. Mục đích duy nhất là để `report_context` có một model thật để nối |
| 6 | `MOD-tag-service` (`CR-TC-BACKFILL-07`, `CR-P0-07`) | Viết card và hiện thực, chỉ viết card, hay chưa làm? | **Viết card và hiện thực** | Đây là **lệnh bắt đầu bằng văn bản** mà `SG-G5` của mọi card đòi, cho đúng một card mới — card tag service. Nó không mở lại bất kỳ card nào khác |

Owner cũng chọn cách giao: commit theo nhóm việc lên nhánh làm việc và mở một pull request vào `main`, việc
nhỏ trước, card tag service sau cùng.

## 3. Không được quyết ở vòng này

Những mục sau nằm ở `docs/owner-runbook.md` §12.2 và **không** được hỏi, vì câu trả lời của chúng là một
**lần chạy** chứ không phải một lựa chọn:

- `G-8` — cô lập AI `ISO-01..05` và lần chạy E3 của một adapter. Cả hai adapter vẫn `enabled: false`.
- `G-9` — ba dữ kiện Bot API (`CR-PC07-04`). Telegram vẫn khoá ở phạm vi chỉ chữ.
- `SP1` — probe khả thi X trên máy của Owner.
- Drill restore thật và phép đo `RPO`/`RTO`; review giao diện thật (E4); đọc 3–4 kỳ báo cáo thật.
- Chính sách tái xử lý nội dung của arXiv/OpenAlex/X — Owner vẫn **gánh** bảo đảm ấy.
- `REQ-A5` cho nhà cung cấp khác Anthropic.

## 4. Điều vòng này **làm** — và điều nó **không** làm

1. **Được gỡ: tính tạm thời của bốn con số** (`N`, định dạng mã, hạn mã, rate limit). Trước vòng này chúng là
   "giá trị làm việc Owner đã chấp nhận"; nay là giá trị Owner chốt. Đổi chúng về sau là một thay đổi hợp đồng
   bình thường theo `precode/change-control.md`, không còn là "chốt một giá trị tạm".
2. **Không được gỡ: giới hạn của bằng chứng.** Chốt `N = 7` không chứng minh 7 là đúng với nhu cầu; chọn
   `multilingual-e5-small` không chứng minh nó đủ tốt trên thuật ngữ khoa học (`REQ-A3`). Mức bằng chứng của
   mọi card **không** đổi vì biên bản này.
3. **Không đóng finding nào.** `F-A3-P5-03` đã `VERIFIED` từ `A3-P5-R2`; mục 4 chỉ nói Owner không muốn đổi
   hợp đồng để có một mã đẹp hơn. `CR-TC-SECRET-01` được **trả lời** ở mục 3; đóng nó trong `precode/review.md`
   là việc của chủ bảng ấy.
4. **Một chỗ cố ý để nguyên.** `acceptance/scenarios.yaml` (`SC` của liên kết Telegram) vẫn mô tả ba tham số
   mã là "giá trị làm việc, không phải giá trị chốt". Sửa file đó làm mọi manifest E1 ghim nó thành `STALE`
   (`CR-PC09-16`, vẫn `OPEN`); câu mô tả sẽ được cập nhật ở lượt PC09 kế tiếp, không phải ở đây.

## 5. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/decision-register.md` §0 và §8.17 | Nhãn `ACCEPTED (OD-20261017-12)`, đoạn "Cập nhật vòng mười hai", bảng hiệu lực |
| `precode/owner-decisions.md` | Dòng trỏ |
| `precode/baseline.json` | Anchor `OD-20261017-12` |
| `agent_profile/registry.json` | `AUTH-OWNER-20261017-13` |
| `precode/owner-decision-request.md` | Khối "VÒNG MƯỜI HAI · ĐÃ TRẢ LỜI" |
| `precode/requirements.csv`, `acceptance/traceability.csv` | `REQ-OQ04` → `XN`; ghi chú `REQ-D28`, `REQ-OQ09` |
| `contracts/telegram/commands.yaml` | Ba tham số `CR-PC07-01` → `ACCEPTED` |
| `contracts/reporting/time-and-tags.md`, `contracts/ui/screens.yaml` | Chữ của `N = 7` |
| `contracts/ops/secrets.md` 0.1.1, `contracts/ops/backup-restore.md` 0.1.1 | Mục 3 |
| `tools/backup_cli.py`, `docs/owner-runbook.md` §9.1 | Mục 1 |
| `agent-tasks/` | Mọi card ghim một file ở trên ⇒ `STALE` ⇒ **một** lượt pin lại, epoch `PC10-PIN-P7-20261017` |
