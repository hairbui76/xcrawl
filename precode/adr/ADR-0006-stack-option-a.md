---
adr_id: ADR-0006
title: Stack Option A - Python toàn bộ (PROVISIONAL)
status: proposed
decision_owner: Owner
date: 2026-09-06
blocker_refs: []
source_refs: [SRC-SPEC §6.3, SRC-SPEC §13.1, SRC-PLAN §1, SRC-PLAN §11, SRC-PLAN §12]
requirement_refs: [REQ-S6.3-01, REQ-OQ02, REQ-D48, REQ-D49, REQ-D07]
invariant_refs: []
amendment_refs: []
decision_refs: []  # khong gan B/AMD; quyet dinh goc la REQ-OQ02 (cau hoi mo), baseline §5 hang Stack
consumers: [PC10]
affected_packages: [PC10]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0006 — Stack Option A (Python toàn bộ)

## Bối cảnh

SRC-SPEC §6.3 so sánh ba phương án stack và **khuyến nghị A: Python toàn bộ**, với lý do hai khối khó nhất — điều khiển Chrome và embedding local — đều mạnh nhất ở Python, và MVP một người dùng không đòi hỏi giao diện phức tạp đến mức phải đổi lấy hai ngôn ngữ. Đặc tả ghi rõ đây là *đề xuất*, cần người dùng chọn. SRC-SPEC §13.1 xếp câu hỏi này là **chặn M1**.

SRC-PLAN §12 nói rõ: "Chưa chọn stack" không cản soạn invariant và wire schema; nó cản card triển khai có đường dẫn, build và test chính xác. Nghĩa là PC01–PC09 vẫn làm được, chỉ PC10 bị chặn.

## Quyết định

Ghi nhận **Option A (Python toàn bộ)** là lựa chọn PROVISIONAL, dùng **duy nhất** cho mục đích viết đường dẫn file, lệnh build và lệnh test trong task card của PC10. Không gói hợp đồng nào khác được phép phụ thuộc vào lựa chọn này: `contracts/` phải độc lập framework.

Các ràng buộc công nghệ đã xác nhận không phụ thuộc lựa chọn stack và vẫn giữ nguyên: SQLite là data store chuẩn (D07), embedding dùng model local (D48), tính tương đồng bằng SQLite thuần quét tuyến tính ở MVP (D49), Chrome thật với profile riêng.

## Trạng thái

`proposed`. Đây là câu hỏi mở REQ-OQ02 và Owner phải trả lời. PC10 **không được** viết card có đường dẫn thật trước khi có câu trả lời; nếu Owner chọn B hoặc C thì chỉ phần đường dẫn/build/test của card phải viết lại, không phải hợp đồng.

## Hệ quả

### Tích cực
- PC01–PC09 tiếp tục được mà không cần chờ: hợp đồng và schema độc lập framework.
- Một ngôn ngữ để bảo trì; Playwright Python và thư viện embedding local là hai điểm mạnh nhất của lựa chọn này.

### Tiêu cực và chi phí
- Web app ở Python "khá" chứ không "tốt nhất" theo chính bảng so sánh của đặc tả; nếu sau này giao diện phức tạp lên thì chi phí đổi cao.
- Nếu Owner chọn B (Python worker + TS web) thì phải bảo trì hai ngôn ngữ; nếu chọn C (TypeScript toàn bộ) thì embedding local yếu hơn và ít lựa chọn model, ảnh hưởng REQ-D59 và REQ-A3.

### Bất biến được giữ
Không có invariant nào phụ thuộc lựa chọn này. Đó là điều kiện để ADR này được phép ở trạng thái PROVISIONAL mà không chặn các gói khác.

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| A. Python toàn bộ | Collector và embedding mạnh nhất; một ngôn ngữ; công sức MVP thấp nhất | Web app chỉ ở mức khá | **Được chọn tạm** theo khuyến nghị của đặc tả |
| B. Python worker + TS web | Web app tốt nhất; collector và embedding vẫn mạnh | Hai ngôn ngữ phải bảo trì; công sức trung bình | MVP một người dùng không cần giao diện phức tạp đến mức đó |
| C. TypeScript toàn bộ | Web app tốt nhất; một ngôn ngữ | Embedding local yếu hơn, ít lựa chọn model; Playwright Node cho collector | Rủi ro ở đúng khối khó nhất |
| Hoãn hẳn quyết định | Không đoán thay Owner | PC10 không viết được card có đường dẫn thật | Đã hoãn: đây chính là lý do ADR ở trạng thái proposed |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §6.3 (bảng so sánh và khuyến nghị), §13.1 hàng 2 (chặn M1); SRC-PLAN §1, §11 (PC10), §12 (G5).
- Không có amendment: đặc tả đã ghi đây là đề xuất, nên không có câu chữ nào bị sửa.
- Blocked scope nếu Owner chưa trả lời: PC10 và gate G5.
