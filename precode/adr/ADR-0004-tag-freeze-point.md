---
adr_id: ADR-0004
title: Mốc freeze tag tại transaction publish báo cáo
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B01, B04]
source_refs: [SRC-SPEC §3.4, SRC-SPEC §3.5, SRC-SPEC §5.5, SRC-SPEC §8.1, SRC-SPEC §8.2, SRC-SPEC §9.2, SRC-SPEC AC-05, SRC-SPEC AC-08, SRC-PLAN §8.2, SRC-PLAN §9.2]
requirement_refs: [REQ-CTAG, REQ-D23, REQ-D24, REQ-D27, REQ-D28, REQ-D57, REQ-AC05, REQ-AC08, REQ-S8.1-03, REQ-S8.2-01, REQ-S8.2-02, REQ-S9.2-04, REQ-S10.4-03]
invariant_refs: [I05, I06, I07]
amendment_refs: [AMD-B01, AMD-B04]
decision_refs: [B01, B04, AMD-B01, AMD-B04]
consumers: [PC04, PC07]
affected_packages: [PC04, PC07]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0004 — Mốc freeze tag tại transaction publish

## Bối cảnh

Hàng `C03/D-tag` của SRC-SPEC §3.4 nêu hai mốc trong cùng một câu: "Mốc hiệu lực tag theo **thời điểm gửi**: bộ tag lúc **tạo báo cáo** quyết định nội dung". Gửi và tạo là hai thời điểm khác nhau, và khoảng cách giữa chúng có thể kéo dài khi Telegram đang retry. Trong khoảng đó người dùng có thể thêm hoặc bỏ tag.

SRC-SPEC §9.2 lại ghi: sau khi report được dựng thì "Không dựng lại; chỉ gửi lại". Nếu mốc thật sự là lúc gửi thì "chỉ gửi lại" sẽ gửi một nội dung không còn khớp bộ tag hiện hành — hoặc phải dựng lại, mâu thuẫn chính câu đó.

Vấn đề liên đới (B04): coverage tiến vào lúc nào. Nếu coverage suy ra từ danh sách report hiển thị thì kỳ rỗng (D57 cấm gửi báo cáo rỗng) sẽ tạo lỗ hổng trong chuỗi kỳ nối liền của D27.

## Quyết định

1. Bộ tag được **đóng băng tại transaction publish của báo cáo**. Cụm "thời điểm gửi" trong `C03/D-tag` được đọc lại là "thời điểm publish report".
2. Báo cáo lưu `tag_config_version` **bất biến**; mọi thay đổi tag sau publish chỉ ảnh hưởng kỳ sau.
3. Delivery **không bao giờ** làm đổi nội dung đã publish. Retry Telegram gửi lại đúng payload đã đóng, kèm payload hash.
4. Nếu tag hoặc phiên bản model đổi sau khi selection được tính nhưng **trước** khi commit, transaction bị abort hoặc rebuild (`TAG_VERSION_STALE`); không bao giờ sửa một report đã publish.
5. Coverage là khoảng nửa mở `[from, to)` lấy từ **sổ coverage authoritative**, độc lập với việc có report hiển thị hay không. Coverage chỉ tiến tại commit publish, kể cả với kỳ rỗng (AMD-B04).
6. Sổ pending item và sổ backfill độc lập với con trỏ kỳ. Backfill N ngày tiêu thụ đúng một lần cho mỗi subscription activation đã định danh; crash của builder không tiêu thụ backfill.

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Điểm 1 sửa câu chữ của một quyết định **XN** (`C03/D-tag`) nên bắt buộc Owner phê chuẩn. Điểm 5 bổ sung hành vi cho D57 (UQ) và cũng cần Owner biết.

## Hệ quả

### Tích cực
- I05 giữ được: report lưu tag version và không bị đổi nội dung âm thầm sau publish.
- I06 giữ được kể cả khi có kỳ rỗng: các cửa sổ coverage nối liền, không hở và không chồng lấn.
- REQ-AC05 và REQ-AC08 có oracle tái lập được bằng số hàng và bằng hash payload.

### Tiêu cực và chi phí
- Một mục vừa khớp tag mới thêm lúc 20h01 sẽ không vào báo cáo publish lúc 20h00, dù người dùng có cảm giác "đã thêm trước khi nhận tin". Đây là đánh đổi phải nói rõ với Owner.
- Thêm một sổ (coverage ledger) và hai sổ phụ (pending, backfill) so với mô hình chỉ có bảng `report`.
- Publisher chạy song song phải dùng CAS trên coverage predecessor; kẻ thua phải đọc lại và không được publish kỳ chồng.

### Bất biến được giữ
I05, I06, I07 (một canonical work chỉ có một first-announcement).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Freeze tại thời điểm gửi (đọc theo nghĩa đen của `C03/D-tag`) | Đúng nguyên văn một nửa của hàng nguồn | Phải thiết kế report revision, xử lý đã gửi một phần, và nội dung app khác nội dung Telegram | Phá I05; phá "không dựng lại, chỉ gửi lại" của §9.2 |
| Freeze tại thời điểm bắt đầu build | Đơn giản nhất để cài đặt | Tag đổi giữa build và commit sẽ tạo report không nhất quán với chính snapshot nó dùng | Không có điểm CAS rõ ràng để chống publisher song song |
| Freeze tại thời điểm thu thập | Tránh mọi tranh chấp về sau | Trái hẳn `C03/D-tag` và trái ví dụ §8.2 hàng 1 và 2 | Đảo ngược một quyết định XN |
| Suy coverage từ danh sách report hiển thị | Không cần sổ riêng | Kỳ rỗng không có report nên tạo lỗ hổng, trái D27 | Phá I06 |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §3.4 (`C03/D-tag`, D23, D24), §3.5 (D27, D28, D57), §5.5, §8.1, §8.2 hàng 1–4 và 9, §9.2, AC-05, AC-08; SRC-PLAN §8.2, §9.2.
- Oracle bị ảnh hưởng: REQ-AC05 (mốc so sánh), REQ-AC08 (thêm case kỳ rỗng).
- Amendment: AMD-B01, AMD-B04.
