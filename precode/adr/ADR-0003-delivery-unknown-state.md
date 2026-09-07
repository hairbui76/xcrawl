---
adr_id: ADR-0003
title: Trạng thái delivery không xác định
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B03]
source_refs: [SRC-SPEC §9.1, SRC-SPEC §9.3, SRC-SPEC AC-14, SRC-PLAN §3.1, SRC-PLAN §8.3, SRC-PLAN §10]
requirement_refs: [REQ-AC14, REQ-D38, REQ-S9.1-03, REQ-S9.2-05, REQ-S9.3-06, REQ-S5.3-02, REQ-S5.4-02]
invariant_refs: [I09, I13]
amendment_refs: [AMD-B03]
decision_refs: [B03, AMD-B03]
consumers: [PC07]
affected_packages: [PC07]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0003 — Trạng thái delivery không xác định

## Bối cảnh

AC-14 hứa "không có tin nào bị gửi hai lần". SRC-SPEC §9.3 định nghĩa cơ chế chống trùng là "`delivery` một hàng cho một (report, kênh)". Nhưng SRC-PLAN §3.1 chỉ ra: tài liệu Telegram Bot API `sendMessage` mô tả kết quả Message khi thành công và **không** có tham số idempotency key do client cung cấp. Do đó một ràng buộc UNIQUE trong SQLite chỉ chứng minh được rằng *hệ thống này* không ghi hai hàng; nó không chứng minh được rằng *Telegram* không nhận hai tin.

Tình huống cụ thể: hệ thống gửi request, Telegram nhận và xử lý, nhưng phản hồi mất trên đường về. Hệ thống không biết tin đã tới hay chưa. Retry thì có thể gửi trùng; không retry thì có thể mất tin. Cả hai lựa chọn đều là một đánh đổi, và đánh đổi đó phải hiện ra trong trạng thái chứ không bị giấu.

## Quyết định

1. Delivery có enum: `pending` → `sending` → `sent`; nhánh `retry_wait`, `failed`, `unknown`, `cancelled`.
2. Attempt được ghi **trước** network call.
3. Timeout, mất kết nối hoặc crash sau điểm có thể đã gửi đưa delivery vào `unknown`. **Không retry tự động từ `unknown`.** App nêu rõ trạng thái chưa xác định; Operator (chính là Owner) quyết định có chấp nhận nguy cơ gửi trùng hay không.
4. Chỉ retry tự động khi **chắc chắn chưa được nhận** hoặc nhận lỗi retryable có nghĩa rõ ràng, trong budget và backoff đã đóng số.
5. Digest nhiều message lưu `delivery_part` với index, payload hash và receipt từng phần. Phần `unknown` không được gửi lại chỉ vì tổng thể chưa `sent`.
6. Hủy liên kết hoặc đổi link generation đưa delivery đang chờ về `cancelled`; không chuyển payload cũ sang recipient mới.

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Quyết định này **thay đổi câu chữ của AC-14** — một tiêu chí nghiệm thu người dùng đã đọc — nên bắt buộc Owner phê chuẩn (AMD-B03). Cho tới lúc đó, PC07 không được tuyên bố `CONTRACT_READY` cho phần delivery.

## Hệ quả

### Tích cực
- Bảo đảm được phát biểu ở dạng kiểm chứng được: "không gửi lặp **tự động**" thay cho "không bao giờ gửi hai lần".
- Sự không chắc chắn hiện ra ở UI thay vì bị làm tròn thành `sent` hoặc `failed` (I13).
- Report trong app hoàn toàn độc lập với kết quả delivery (I09).

### Tiêu cực và chi phí
- Owner có thể phải xử lý tay một số trường hợp `unknown`. Số lượng chưa đo được và phải theo dõi.
- Thêm bảng `delivery_part` và thêm một trạng thái vào mọi read model liên quan.
- AC-14 nguyên văn không còn đúng; tài liệu nghiệm thu phải cập nhật.

### Bất biến được giữ
I09 (Telegram thất bại không làm report biến mất), I13 (unknown là một trạng thái hiển thị riêng).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Giữ AC-14 nguyên văn, dựa vào UNIQUE ở DB | Không phải sửa tài liệu | UNIQUE chỉ chặn ghi hai hàng nội bộ, không chặn hai tin ở Telegram | Là một bảo đảm không kiểm chứng được; SRC-PLAN §9 cấm nâng nhãn bằng suy diễn |
| Retry tự động luôn, chấp nhận gửi trùng | Không mất tin | Người dùng nhận digest hai lần, mâu thuẫn tinh thần AC-14 | Không ai chọn giúp Owner đánh đổi này được |
| Không retry bao giờ | Không bao giờ trùng | Mất tin khi lỗi mạng tạm thời | Mất giá trị chính của kênh Telegram |
| Dùng `getUpdates` để tự dò xem tin đã gửi chưa | Có vẻ giải quyết được | Bot không đọc được lịch sử tin do chính nó gửi một cách bảo đảm; thêm phụ thuộc API | Không có bằng chứng API hỗ trợ; sẽ là suy diễn |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §9.1, §9.3 (hàng Telegram gửi lỗi), AC-14; SRC-PLAN §3.1 (Telegram Bot API), §8.3 (bảng transition delivery), §10 (`TELEGRAM_SEND_UNCERTAIN`, `TELEGRAM_PERMANENT_FAILURE`).
- Oracle bị ảnh hưởng: REQ-AC14 đổi phát biểu; thêm fixture "Telegram nhận tin rồi cắt response".
- Amendment: AMD-B03.
