---
adr_id: ADR-0006
title: Stack Option B - Python workers + TypeScript web
status: accepted
decision_owner: Owner
date: 2026-09-06
revised_at: 2026-09-07
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: []
source_refs: [SRC-SPEC §6.3, SRC-SPEC §13.1, SRC-PLAN §1, SRC-PLAN §11, SRC-PLAN §12]
requirement_refs: [REQ-S6.3-01, REQ-OQ02, REQ-D48, REQ-D49, REQ-D07, REQ-D59, REQ-A3]
invariant_refs: []
amendment_refs: []
decision_refs: [OD-20260907-01]
consumers: [PC10]
affected_packages: [PC10]
supersedes: []
filename_note_vi: >
  Tên file giữ nguyên "ADR-0006-stack-option-a.md" vì 18 task card và precode/adr/README.md
  đang trỏ theo đường dẫn này; đổi tên là một thao tác rename cần grant riêng. Nội dung là
  phương án B. Xem CR-PC00-16.
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0006 — Stack Option B (Python workers + TypeScript web)

> **Lưu ý về tên file.** File này tên `ADR-0006-stack-option-a.md` vì lý do lịch sử: bản đầu ghi nhận phương án A. Owner đã chọn **B** ngày 2026-09-07. Tên file giữ nguyên để 18 task card và chỉ mục ADR không đứt liên kết; đổi tên cần một packet riêng (`CR-PC00-16`).

## Bối cảnh

SRC-SPEC §6.3 so sánh ba phương án và **khuyến nghị A (Python toàn bộ)**, với lý do hai khối khó nhất — điều khiển Chrome và embedding local — đều mạnh nhất ở Python, và MVP một người dùng không đòi hỏi giao diện phức tạp đến mức phải đổi lấy hai ngôn ngữ. Đặc tả ghi rõ đây là *đề xuất*, cần người dùng chọn, và §13.1 xếp câu hỏi này là **chặn M1**.

Bản đầu của ADR này (2026-09-06) ghi nhận **A** là lựa chọn PROVISIONAL, dùng **duy nhất** để PC10 viết được đường dẫn và lệnh build trong task card, và nói rõ: nếu Owner chọn B hoặc C thì chỉ §3 và §8 của mỗi card phải viết lại, hợp đồng không đổi.

Ngày 2026-09-07 Owner trả lời: **B — Python workers + TypeScript web** (`OD-20260907-01` mục 3).

## Quyết định

**Phương án B.**

| Khối | Ngôn ngữ / nền tảng |
| --- | --- |
| X collector (máy cá nhân) | **Python** — Playwright Python |
| Analysis worker + AI adapter (máy cá nhân) | **Python** |
| Embedding service (server) | **Python** — model local |
| Backend, API, job queue, report builder, Telegram adapter (server) | **Python** |
| Web app (server) | **TypeScript** |
| Data store | SQLite (không phụ thuộc lựa chọn stack) |

Ranh giới giữa hai ngôn ngữ là **HTTP API đã có hợp đồng** trong `contracts/http/openapi.yaml`: web app TypeScript là một consumer của owner API, không chia sẻ tiến trình hay module với phần Python. Nhờ vậy việc thêm ngôn ngữ thứ hai **không** tạo thêm một ranh giới quyền nào ngoài những cạnh đã có trong `contracts/modules.yaml`.

Các ràng buộc công nghệ đã xác nhận không phụ thuộc lựa chọn stack và giữ nguyên: SQLite là data store chuẩn (D07), embedding dùng model local (D48) — vẫn ở phía Python nên `REQ-D59`/`REQ-A3` không bị ảnh hưởng, tính tương đồng bằng SQLite thuần quét tuyến tính ở MVP (D49), Chrome thật với profile riêng của dự án (D09, nay **XN**).

## Trạng thái

**`accepted`** — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` mục 3 (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`). Quyết định này **thay thế** phương án A mà bản đầu của ADR ghi nhận; `REQ-OQ02` đã được trả lời và **M1 không còn bị chặn** bởi câu hỏi stack.

## Hệ quả

### Phải viết lại — và chỉ chừng này

- **`agent-tasks/`: §3 (đường dẫn) và §8 (lệnh build/test) của cả 18 task card.** Các card thuộc web app đổi sang cây TypeScript; các card collector, worker, embedding, backend và report giữ cây Python. `PROV-PC10-01` (layout đường dẫn theo A) **không còn hiệu lực** và phải được thay bằng layout B.
- **`precode/README.md`** ở chỗ nào mô tả cây thư mục theo A.

### **Không** phải viết lại

`contracts/**` (mọi hợp đồng, schema, state machine, error map, port), `acceptance/**` (56 scenario, toàn bộ fixture, traceability), `precode/requirements.csv`, `precode/decision-register.md`, `precode/gates.yaml`, và các ADR khác. Đây chính là điều SRC-PLAN §12 thiết kế để đạt được — *"Chưa chọn stack không cản soạn invariant và wire schema; nó cản card triển khai có đường dẫn/build/test chính xác"* — và nó đã đúng: một quyết định stack đến muộn tốn **một lượt sửa 18 card**, không tốn một dòng hợp đồng nào.

### Tích cực

- Web app ở mức "tốt nhất" theo chính bảng so sánh của đặc tả, thay vì "khá" như A. App phải truy cập được từ ngoài và mở được trên điện thoại (D04), nên chất lượng giao diện không phải thứ trung tính.
- Hai khối khó nhất — điều khiển Chrome và embedding local — **vẫn ở Python**, tức phương án B giữ nguyên toàn bộ lý do kỹ thuật mà đặc tả dùng để loại C.

### Tiêu cực và chi phí

- **Hai ngôn ngữ phải bảo trì.** Đây là cái giá đặc tả đã nêu và Owner đã chấp nhận có ý thức. Nó nghĩa là hai bộ dependency, hai chuỗi build, hai cách chạy test, và một ranh giới HTTP phải được tôn trọng thay vì gọi hàm trực tiếp.
- **Công sức MVP ở mức trung bình** thay vì thấp nhất (bảng §6.3).
- Rủi ro trôi hợp đồng ở ranh giới TS↔Python cao hơn so với một ngôn ngữ: một thay đổi schema phải được phản ánh ở cả hai phía. Giảm thiểu bằng cách sinh kiểu từ `openapi.yaml` thay vì gõ tay — thuộc phạm vi PC10, chưa được quyết ở đây.

### Bất biến được giữ

Không có invariant nào phụ thuộc lựa chọn ngôn ngữ. Đó là điều kiện để ADR này đổi từ A sang B mà **không** làm sai một dòng hợp đồng nào.

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Kết quả |
| --- | --- | --- | --- |
| A. Python toàn bộ | Một ngôn ngữ; công sức MVP thấp nhất; collector và embedding mạnh nhất | Web app chỉ ở mức khá | **Bị Owner bác** ngày 2026-09-07. Là khuyến nghị của đặc tả và là nội dung bản đầu của ADR này |
| **B. Python worker + TypeScript web** | Web app tốt nhất; collector và embedding vẫn ở Python | Hai ngôn ngữ; công sức trung bình | **Được chọn** (`OD-20260907-01` mục 3) |
| C. TypeScript toàn bộ | Web app tốt nhất; một ngôn ngữ | Embedding local yếu hơn, ít lựa chọn model — đe dọa `REQ-D59` và `REQ-A3`; Playwright Node cho collector | Không chọn: rủi ro nằm đúng ở khối khó nhất |
| Hoãn tiếp | Không đoán thay Owner | PC10 không viết được card có đường dẫn thật; M1 vẫn chặn | Không còn cần: Owner đã trả lời |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §6.3 (bảng so sánh và khuyến nghị A), §13.1 hàng 2 (chặn M1); SRC-PLAN §1, §11 (PC10), §12 (G5).
- Quyết định: `OD-20260907-01` mục 3 — `precode/owner-decisions.md`; authority `AUTH-OWNER-20260907-02`; evidence `session_017QmDJtMqD9o1z79waqSB9W`.
- Không có amendment: đặc tả đã ghi §6.3 là *đề xuất*, nên không câu chữ nào của đặc tả bị sửa. Điều đổi là **lựa chọn**, không phải cam kết đã viết.
- Việc còn lại: `CR-PC00-16` (đổi tên file cho khớp nội dung) và lượt PC10 viết lại §3/§8 của 18 card.
