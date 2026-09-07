---
adr_id: ADR-0010
title: Phạm vi secret theo task và cô lập adapter CLI/ACP
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B13]
source_refs: [SRC-SPEC §3.7, SRC-SPEC §10.2, SRC-SPEC §11.2, SRC-SPEC §11.4, SRC-SPEC §13.2, SRC-SPEC AC-16, SRC-SPEC AC-17, SRC-PLAN §6, SRC-PLAN §6.1, SRC-PLAN §11]
requirement_refs: [REQ-D41, REQ-D43, REQ-D51, REQ-A5, REQ-S10.2-02, REQ-S10.2-06, REQ-S11.2-01, REQ-S11.4-03, REQ-AC16, REQ-AC17, REQ-S13.2-02, REQ-S13.2-03]
invariant_refs: [I11, I14]
amendment_refs: []
decision_refs: [B13]
consumers: [PC01, PC06, PC08]
affected_packages: [PC01, PC06, PC08]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0010 — Phạm vi secret và cô lập CLI/ACP

## Bối cảnh

Đặc tả cam kết hai họ provider (D41, XN) và cam kết hệ thống chạy được **không cần API key nào** nếu mọi tác vụ AI đi qua CLI (D51, XN). §10.2 mô tả đường API key giữ key ở secret store của server và "worker lấy qua backend", nhưng không nói worker được nhận key nào, trong bao lâu, và có được nhận cả bộ hay không.

Đường CLI/ACP tạo một rủi ro khác: CLI của một nhà cung cấp thường có khả năng đọc file, gọi tool và ra mạng. §11.4 lại yêu cầu "Nội dung ngoài không được sửa system prompt, gọi tool, đọc secrets, hay điều khiển việc gửi Telegram" — và nội dung ngoài chính là thứ đi vào prompt.

A5 (KC) yêu cầu đọc điều khoản của từng nhà trước khi bật đường CLI/ACP; SRC-PLAN §11 (PC06) nói thêm: không dùng tên ACP để suy ra mọi CLI tương thích.

## Quyết định

1. **Secret theo task.** Worker chỉ nhận credential của **đúng provider cho task được giao**, với thời hạn ngắn. Không có đường nào để worker lấy toàn bộ secret store.
2. **Cô lập CLI/ACP.** Adapter CLI/ACP phải chạy với tool, truy cập file và truy cập mạng bị tắt, ngoài phần inference được phép.
3. **Không kiểm chứng được thì không bật.** Nếu mức cô lập không kiểm chứng được cho một provider thì adapter của provider đó **giữ trạng thái disabled**; đây là mặc định, không phải hình phạt.
4. **Điều khoản trước khi bật.** Adapter của một nhà chỉ được bật sau khi đã đọc tài liệu chính thức của chính nhà đó (A5). Chưa đọc thì trạng thái là disabled, và ghi rõ lý do.
5. **Capability matrix theo từng provider và từng version:** auth family, task hỗ trợ, concurrency, timeout, cancellation, cách bóc JSON, và usage có "unknown" hay không. Không giả định các provider tương thích cùng một giao thức.
6. **Usage không rõ là `unknown`,** không được ghi thành 0 (I14). Fallback chỉ theo allowlist và thứ tự do Owner cấu hình, không do model chọn.
7. Phiên X và phiên CLI **giữ trên máy cá nhân**; server không bao giờ nhận chúng.

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Điểm 3 có thể dẫn tới việc một họ provider bị tắt, ảnh hưởng phạm vi của D41 và D51 — hai quyết định **XN**. Vì vậy Owner phải biết và chấp nhận trước khi PC06 đóng hợp đồng. Nếu Owner yêu cầu bật một adapter chưa kiểm cô lập thì phải ghi `ACCEPTED_RISK` có căn cứ, không được ghi là đã giải quyết.

## Hệ quả

### Tích cực
- I11 kiểm chứng được bằng canary và audit số lần gọi tool, thay vì bằng lời hứa.
- REQ-AC17 có oracle thật: secret canary trong transcript không bị lộ, số lần gọi tool bằng 0, quyền gửi Telegram không đổi.
- Bán kính thiệt hại của một prompt injection thành công bị giới hạn ở đúng credential của một task.

### Tiêu cực và chi phí
- REQ-AC16 (không có API key) chỉ pass khi có ít nhất một adapter CLI qua được kiểm cô lập. Nếu mọi adapter CLI bị disabled thì REQ-AC16 phải ghi `BLOCKED`, **không** phải `FAIL` — đây là một khác biệt quan trọng khi báo cáo.
- Cấp credential ngắn hạn theo task cần thêm cơ chế phát và thu hồi ở backend.
- Việc đọc điều khoản là công việc tay, không tự động hóa được, và phải làm lại khi provider đổi phiên bản.

### Bất biến được giữ
I11 (nội dung nguồn và output AI không đọc được secret, không gọi tool, không đổi recipient), I14 (usage unknown không ghi thành 0).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Gửi toàn bộ secret store cho worker | Đơn giản, worker tự chọn | Một lỗ hổng ở worker làm mất mọi key | Trái §11.2 và I11 |
| Bật mọi adapter CLI, tin vào cấu hình mặc định của nhà cung cấp | Nhiều lựa chọn provider ngay | Không kiểm chứng được tool bị khóa; nội dung ngoài có thể gọi tool | Trái §11.4; không có oracle |
| Bỏ hẳn đường CLI, chỉ dùng API key | Đơn giản và dễ kiểm | Phá D51 (chạy được không key nào) và một nửa D41 | Đảo hai quyết định XN |
| Chạy CLI trong container cô lập | Cô lập tốt hơn | CLI/ACP cần phiên đăng nhập của người dùng và Chrome cần cửa sổ; §6.4 nói rõ không container | Trái ràng buộc triển khai đã có lý do |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §3.7 (D41, D43, D44, D51), §10.2, §11.2, §11.4, §13.2, AC-16, AC-17; SRC-PLAN §6 (bảng edge), §6.1, §11 (PC06, PC08).
- Oracle bị ảnh hưởng: REQ-AC16 (điều kiện pass/BLOCKED), REQ-AC17 (canary và tool audit).
- Không có amendment: đây là bổ sung chính sách, không sửa câu chữ nào của đặc tả.
