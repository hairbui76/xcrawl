---
adr_id: ADR-0005
title: Phương pháp backup và restore cho SQLite
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B11]
source_refs: [SRC-SPEC §3.6, SRC-SPEC §6.4, SRC-SPEC §7.3, SRC-SPEC §9.3, SRC-SPEC §13, SRC-SPEC AC-12, SRC-PLAN §3.1, SRC-PLAN §10, SRC-PLAN §11]
requirement_refs: [REQ-D58, REQ-S7.3-04, REQ-S6.4-01, REQ-AC12, REQ-S9.3-08, REQ-S13-09]
invariant_refs: [I15, I08]
amendment_refs: [AMD-B11]
decision_refs: [B11, AMD-B11]
consumers: [PC08]
affected_packages: [PC08]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0005 — Phương pháp backup và restore

## Bối cảnh

SRC-SPEC D58 và §7.3 mô tả backup là "copy file SQLite" và restore là "đặt file về chỗ cũ". SRC-PLAN §3.1 nêu vấn đề kỹ thuật: WAL là một phần trạng thái bền của DB; tách file DB khỏi WAL có thể mất transaction đã commit. Một bản copy lấy khi DB đang ghi không bảo đảm nhất quán.

Đặc tả cũng không nói gì về ba thứ khác cần khôi phục: hàng đợi job, token của collector, và artifact/cấu hình của model embedding. Và không nói gì về việc sau khi restore thì các side effect cũ (outbox Telegram, job đang chờ) có được chạy lại không.

## Quyết định

1. **Backup** tạo snapshot nhất quán bằng **SQLite Online Backup API** hoặc `VACUUM INTO`, an toàn với WAL. Không dùng `cp` trên file DB đang hoạt động.
2. Mỗi backup kèm **manifest** ghi: hash file DB, phiên bản schema, danh sách artifact và cấu hình embedding (tên model, phiên bản, dimension, generation đang active), thời điểm tạo, phạm vi.
3. Phiên X (profile Chrome) và token trên máy cá nhân **không** nằm trong backup của server; chúng được ghi vào runbook như phần phải thiết lập lại bằng tay.
4. **Restore** thực hiện vào môi trường sạch với **khóa side effect**: dispatcher và worker claim bị dừng, outbox cũ không replay, `first_announced` không bị reset trước khi kiểm tra toàn vẹn.
5. Sau restore, chạy integrity check: count và hash của Saved, report, coverage ledger phải khớp manifest; lease cũ bị thu hồi; chỉ khi reconciliation xong mới mở lại dispatch.
6. **Retention:** giữ vô thời hạn (giữ nguyên D58 phần retention). RPO/RTO cụ thể do PC08 chốt cùng Owner.

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Điểm 1 sửa câu chữ của D58 (UQ) nên cần Owner phê chuẩn qua AMD-B11. Bằng chứng restore thật (E2/E3) **chưa có** và được ghi `NOT_RUN`; ADR này chỉ chốt phương pháp.

## Hệ quả

### Tích cực
- I15 giữ được: restore không tự gửi lại outbox cũ, không chạy lại job side effect, không reset `first_announced` mà không kiểm tra.
- Có một oracle thật cho REQ-AC12: hash snapshot của Saved trước và sau restore phải bằng nhau.
- Manifest làm cho việc khôi phục có thể kiểm chứng bởi người khác, đúng yêu cầu "một người khác đọc runbook có thể biết phục hồi tới mốc nào".

### Tiêu cực và chi phí
- Backup mất thời gian hơn `cp`, và `VACUUM INTO` cần dung lượng đĩa tạm bằng cỡ DB.
- Restore không còn là thao tác một bước; cần một drill có kịch bản và có người thực hiện.
- Phần secret trên máy cá nhân phải thiết lập lại bằng tay sau sự cố; đây là một khoảng trống có chủ đích, phải ghi rõ trong runbook.

### Bất biến được giữ
I15, I08 (Save là snapshot bất biến; restore không được làm đổi snapshot).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| `cp` file DB như D58 nguyên văn | Đơn giản, đúng chữ đặc tả | Có thể mất transaction đã commit vì WAL nằm ở file khác | Không dùng làm bằng chứng khôi phục được |
| Dừng hẳn dịch vụ rồi copy | Nhất quán tuyệt đối | Có downtime mỗi lần backup | Không cần thiết khi API đã cung cấp snapshot nóng |
| Chỉ dựa vào snapshot của volume/hạ tầng | Không cần code | Phụ thuộc nhà cung cấp; không có manifest nội dung; không kiểm được schema version | Không kiểm chứng được ở mức ứng dụng; vẫn nên có nhưng là lớp bổ sung |
| Đưa profile Chrome vào backup server | Khôi phục nhanh hơn | Đồng bộ phiên X lên server, trái §11.2 | Vi phạm ràng buộc bảo mật đã xác nhận |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §3.6 (D58), §6.4, §7.3, §9.3 (hàng hết ổ đĩa), §13 (M8), AC-12; SRC-PLAN §3.1 (SQLite WAL, Backup API), §10 (`RESTORE_UNVERIFIED`, `STORAGE_WRITE_FAILED`), §11 (PC08).
- Oracle bị ảnh hưởng: REQ-AC12 thêm bước restore; thêm oracle âm cho `RESTORE_UNVERIFIED`.
- Amendment: AMD-B11.
