---
adr_id: ADR-0002
title: Tách mô hình trạng thái run thành phase / status / outcome / stop_reason
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B02, B05]
source_refs: [SRC-SPEC §5.2, SRC-SPEC §9.1, SRC-SPEC §8.3, SRC-SPEC AC-03, SRC-SPEC AC-15, SRC-PLAN §8.1]
requirement_refs: [REQ-S5.2-01, REQ-S9.1-01, REQ-S9.1-02, REQ-AC03, REQ-AC15, REQ-D14, REQ-S8.3-01, REQ-S8.3-02, REQ-S8.3-03]
invariant_refs: [I09, I13, I10]
amendment_refs: [AMD-B02]
decision_refs: [B02, B05, AMD-B02]
consumers: [PC03, PC07]
affected_packages: [PC03, PC07]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0002 — Tách mô hình trạng thái run

## Bối cảnh

Đặc tả mô tả trạng thái run ở hai chỗ và hai chỗ đó không khớp. SRC-SPEC §5.2 vẽ `reporting --> delivered` và `reporting --> delivered_partial` **bên trong** vòng đời run. SRC-SPEC §9.1 lại khẳng định "Trạng thái job và trạng thái gửi báo cáo là hai thứ độc lập". Ngoài ra một enum duy nhất phải mang ba loại thông tin khác nhau: đang làm gì (`collecting`), đang ở tình trạng nào (`needs_user`), và kết quả ra sao (`failed_partial`). `stopped_limit` là ví dụ rõ nhất: nó vừa là lý do dừng vừa ngụ ý một kết quả.

SRC-SPEC §8.3 yêu cầu ba trạng thái phải phân biệt được trên giao diện — "không có nội dung phù hợp", "đợt dừng sớm", "đợt thất bại" — nhưng enum phẳng không đủ chiều để biểu diễn ba thứ đó cùng với tiến độ.

## Quyết định

Run mang bốn trường độc lập:

- `phase` ∈ {`collecting`, `enriching`, `analyzing`, `reporting`} — đang làm bước nào.
- `status` ∈ {`queued`, `running`, `waiting_retry`, `needs_user`, `blocked`, `completed`, `failed`, `cancelled`} — tình trạng thực thi.
- `outcome` ∈ {`complete`, `partial`, `empty`, `failed`, `cancelled`} — chỉ có giá trị khi run kết thúc.
- `stop_reason` — ví dụ `limit_reached`, `captcha`, `session_expired`, `source_blocked`, `storage_unavailable`, `worker_lost`.

Delivery là **vòng đời riêng** (xem ADR-0003), không phải trạng thái của run. Bảng ánh xạ từ enum cũ sang mô hình mới nằm trong `precode/decision-register.md` §3, AMD-B02. Độ bao phủ nguồn đã biết và độ thiếu hụt là metadata riêng: `completed` **không** có nghĩa đã quét đủ toàn bộ X.

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Quyết định này sửa câu chữ của AC-03 nên phải có Owner phê chuẩn (AMD-B02). Không được đổi enum trong đặc tả trước khi PC03 viết xong bảng transition đầy đủ.

## Hệ quả

### Tích cực
- I09 và I13 trở nên kiểm chứng được: ba read model của REQ-AC15 khác nhau ở bộ `(status, outcome, stop_reason)`.
- Một run dừng sớm vẫn có thể có `outcome = partial` và vẫn sinh được báo cáo một phần.
- Thêm được `blocked` và `empty` — hai trạng thái đặc tả cần nhưng enum cũ không có.

### Tiêu cực và chi phí
- Read model của UI phức tạp hơn: phải diễn giải bốn trường thay vì một chuỗi.
- Mọi fixture và scenario viết theo enum cũ phải viết lại; SC01–SC04, SC15 chịu ảnh hưởng.
- Bảng ánh xạ phải được giữ vĩnh viễn để đọc lại tài liệu và dữ liệu cũ.

### Bất biến được giữ
I09 (Telegram thất bại không làm run thành thất bại thu thập), I10 (CAPTCHA không tự retry; worker stale không commit), I13 (empty/incomplete/failed/unknown hiển thị riêng).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Giữ enum phẳng của §9.1 | Không phải sửa AC-03, ít việc | `delivered` vẫn nằm trong run theo §5.2; không biểu diễn được "dừng sớm nhưng vẫn có báo cáo" | Vi phạm I09 ngay ở mức hợp đồng |
| Giữ enum phẳng nhưng thêm giá trị mới (`stopped_limit_partial`, ...) | Đổi ít | Số giá trị nhân theo tổ hợp; không mở rộng được | Bùng nổ tổ hợp, mỗi lý do dừng mới sinh vài enum |
| Tách hai trường `status` và `result` | Đơn giản hơn bốn trường | Không biểu diễn được "đang ở bước nào" khi resume; mất `stop_reason` | Resume cần biết phase để tiếp đúng chỗ |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §5.2, §8.3, §9.1, AC-03, AC-15; SRC-PLAN §8.1 (bảng transition đầy đủ).
- Oracle bị ảnh hưởng: REQ-AC03 (đích trạng thái đổi), REQ-AC15 (so sánh bộ ba thay vì một enum).
- Amendment: AMD-B02, kèm bảng ánh xạ enum cũ sang mới.
- Liên đới B05: `stop_reason = captcha` cộng checkpoint chỉ trên dữ liệu đã ACK.
