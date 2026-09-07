---
adr_id: ADR-0007
title: Timezone và chuẩn timestamp
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B08]
source_refs: [SRC-SPEC §3.3, SRC-SPEC §3.6, SRC-SPEC §8.2, SRC-SPEC §10.3, SRC-SPEC §13.1, SRC-SPEC AC-02, SRC-PLAN §5.1, SRC-PLAN §9.1]
requirement_refs: [REQ-D56, REQ-D13, REQ-D15, REQ-D27, REQ-AC02, REQ-S8.2-08, REQ-S10.3-05, REQ-OQ06]
invariant_refs: [I06]
amendment_refs: [AMD-B08]
decision_refs: [B08, AMD-B08]
consumers: [PC03, PC04]
affected_packages: [PC03, PC04]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0007 — Timezone và chuẩn timestamp

## Bối cảnh

SRC-SPEC D56 nói "Timezone lấy theo máy chạy app". Hệ thống có ít nhất ba đồng hồ: browser của người dùng, server, và máy cá nhân chạy collector. "Máy chạy app" không xác định máy nào, và ba máy có thể ở ba múi giờ khác nhau.

Điều này không phải chi tiết hiển thị: D13 định nghĩa giờ trong lịch là "mốc sớm nhất được chạy" và D15 gộp các đợt quá hạn — cả hai cần một mốc giờ xác định. D27 tính coverage theo "ngày phát hiện", nên ranh giới ngày cũng phụ thuộc timezone. SRC-PLAN §5.1 yêu cầu chốt độ chính xác timestamp và tie-break bằng ingest sequence **trước PC04**.

## Quyết định

1. Hệ thống lưu **một IANA timezone duy nhất** trong Settings, do Owner xác nhận. Giá trị mặc định tạm: `Asia/Ho_Chi_Minh` (PROVISIONAL).
2. Mọi timestamp bền lưu ở **UTC theo RFC 3339, độ chính xác mili giây**. Lý do chọn mili giây: đủ để phân biệt các lô ingest liên tiếp mà không phụ thuộc độ phân giải đồng hồ của từng hệ điều hành; các mục cùng mili giây được phân định bằng **ingest sequence** đơn điệu tăng do server cấp.
3. `discovered_at` dùng thời điểm **server chấp nhận lần đầu**, không tin clock của worker. `published_at` của X là trường khác và có thể sai lệch tùy nguồn.
4. Timezone chỉ dùng để (a) diễn giải lịch chạy và (b) hiển thị. Không dùng để lưu.
5. Quy tắc DST và catch-up: PC03 viết thành bảng — bao gồm giờ bị bỏ qua khi chuyển sang DST, giờ lặp lại khi kết thúc DST, và cách gộp nhiều đợt quá hạn thành một.

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Điểm 1 sửa câu chữ D56 (UQ) và cần Owner xác nhận **giá trị timezone thật**. Nếu Owner ở múi khác thì mọi fixture lịch của PC03/PC04 phải dựng lại — nhưng bản thân quyết định "một timezone lưu trong settings" không đổi.

## Hệ quả

### Tích cực
- Lịch, chạy bù và ranh giới coverage tính được một cách xác định và tái lập bằng fake-clock.
- Hai bản ghi cùng mili giây vẫn có thứ tự xác định nhờ ingest sequence, nên I06 (coverage nối liền, half-open) không bị phá bởi tie.
- REQ-S10.3-05 (hiện ngày phân tích kèm ngày phát hiện) có định nghĩa rõ về "ngày" của ai.

### Tiêu cực và chi phí
- Nếu Owner đi du lịch hoặc đổi múi giờ, lịch **không** tự đổi theo — đây là hành vi có chủ đích và phải nói rõ trong UI Settings.
- Thêm cột ingest sequence và ràng buộc đơn điệu tăng ở phía server.
- Fixture lịch phải cố định timezone, không được dựa vào giờ máy chạy test.

### Bất biến được giữ
I06.

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Giữ D56 nguyên văn ("máy chạy app") | Không phải sửa gì | Không xác định máy nào; ba đồng hồ khác nhau; fixture không tái lập được | Không có oracle cho REQ-AC02 |
| Dùng timezone của browser mỗi lần | Hiển thị luôn đúng chỗ người dùng đang đứng | Lịch chạy ở server sẽ trôi theo nơi người dùng mở app | Lịch phải ổn định, không phụ thuộc nơi mở app |
| Chạy mọi thứ theo UTC, không có timezone | Đơn giản nhất | "08:00" trong lịch trở nên vô nghĩa với người dùng; ví dụ §8.2 hàng 8 không diễn đạt được | Trái trải nghiệm mà đặc tả mô tả |
| Timestamp độ chính xác giây | Nhẹ hơn | Nhiều mục cùng giây trong một lô ingest; tie-break phải làm việc nhiều hơn | Mili giây rẻ và giảm số lần phải tie-break |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §3.3 (D13, D15), §3.6 (D56), §8.2 hàng 8, §10.3, §13.1 hàng 6, AC-02; SRC-PLAN §5.1, §9.1.
- Oracle bị ảnh hưởng: REQ-AC02 dùng fake-clock cố định theo timezone đã cấu hình.
- Amendment: AMD-B08.
