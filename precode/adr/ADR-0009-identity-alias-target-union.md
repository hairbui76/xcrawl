---
adr_id: ADR-0009
title: Identity, alias và target tagged union
status: accepted
decision_owner: Owner
date: 2026-09-06
ratified_by: OD-20260907-01
ratified_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07"
blocker_refs: [B06, B15]
source_refs: [SRC-SPEC §1.4, SRC-SPEC §3.2, SRC-SPEC §3.5, SRC-SPEC §7.1, SRC-SPEC §9.2, SRC-SPEC §9.3, SRC-SPEC AC-07, SRC-SPEC AC-09, SRC-SPEC AC-13, SRC-PLAN §7, SRC-PLAN §9.1, SRC-PLAN §10]
requirement_refs: [REQ-D17, REQ-D29, REQ-D33, REQ-S1.4-03, REQ-AC07, REQ-AC09, REQ-AC13, REQ-S9.2-02, REQ-S9.3-05, REQ-S9.3-09]
invariant_refs: [I03, I07, I08]
amendment_refs: [AMD-B15]
decision_refs: [B06, B15, AMD-B15]
consumers: [PC02, PC04]
affected_packages: [PC02, PC04]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0009 — Identity, alias và target tagged union

## Bối cảnh

Hai blocker cùng dựa trên một cơ chế nên được gộp vào một ADR.

**B06.** SRC-SPEC §7.1 định nghĩa `work` với `doi` UNIQUE và `arxiv_id` UNIQUE. Ràng buộc đó chặn được việc **ghi** hai hàng cùng ID, nhưng không giải được trường hợp hai hàng đã tồn tại (một chỉ có DOI, một chỉ có arXiv ID) rồi sau đó mới biết là cùng một công trình. D33 tạo mục "chỉ có post" nhưng §7.1 không có model phân tích cho post-only, và `saved_item` dùng ký hiệu `UNIQUE(owner, work/post)` — hai cột nullable không cho một ràng buộc duy nhất đúng.

**B15.** SRC-SPEC §1.4 đặt chỉ số "0 trường hợp trùng" ở trạng thái **Đã xác nhận**. Nhưng metadata có thể thiếu (arXiv/OpenAlex lỗi, §9.3) hoặc mâu thuẫn. Một chỉ số tuyệt đối trên một tập không xác định được thì không đo được.

## Quyết định

1. **Canonical identity** được định nghĩa bằng quy tắc chuẩn hóa tường minh cho DOI và arXiv ID (bao gồm phiên bản arXiv vN), viết thành fixture ở `acceptance/fixtures/identity/`.
2. **Bảng alias** ánh xạ mọi định danh đã gặp về canonical id, kèm **audit trail** cho mỗi lần merge: ai/khi nào/dựa trên bằng chứng gì.
3. `work` có **phiên bản**: arXiv vN là phiên bản của cùng một công trình, không phải công trình khác.
4. **Target** là tagged union `work | post`, dùng thống nhất cho Saved, analysis và report item. Không dựa vào hai cột nullable với một UNIQUE mơ hồ.
5. **Merge identity** phải chuyển reference, first-announcement và Saved theo quy tắc conflict tường minh, giữ nguyên audit trail và **không làm đổi historical snapshot**.
6. Xung đột đưa target vào trạng thái quarantine `identity_conflict`; giữ mọi nguồn; **không merge đoán**. Report không tính hai alias nghi trùng là hai hướng chắc chắn.
7. Bất biến "0 trùng" được phát biểu lại: **0 trường hợp trùng trong phạm vi canonical identity đã biết**, cộng một số đếm riêng cho `identity_conflict` đang chờ xử lý (AMD-B15).

## Trạng thái

**`accepted` — Owner phê chuẩn ngày 2026-09-07 bằng `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`).** Đoạn dưới đây là lập luận lúc ADR còn ở trạng thái `proposed`; giữ nguyên để truy vết, **không** còn là trạng thái hiện tại.

`proposed`. Điểm 7 sửa một chỉ số ở trạng thái **Đã xác nhận** trong SRC-SPEC §1.4, nên bắt buộc Owner phê chuẩn. Các điểm 1–6 là bổ sung định nghĩa còn thiếu, không đảo quyết định nào.

## Hệ quả

### Tích cực
- I03 kiểm chứng được: một canonical identity chỉ có một work; alias conflict không bị merge đoán.
- I07 giữ được sau merge: một canonical work chỉ có một first-announcement, tham chiếu lịch sử có ngày.
- REQ-AC13 có oracle đúng cho cả target post-only, không chỉ cho work.
- Chỉ số §1.4 trở nên đo được, với phần chưa giải quyết hiện ra tường minh thay vì bị giấu.

### Tiêu cực và chi phí
- Thêm bảng alias và bảng audit; mỗi lần merge là một transaction có nhiều bảng.
- Trạng thái `identity_conflict` cần một chỗ trong UI để Owner nhìn thấy và xử lý; nếu không nhìn thấy thì nó chỉ là rác tích tụ.
- Chỉ số thành công không còn là một con số tuyệt đối; báo cáo phải kèm mẫu số và phạm vi.

### Bất biến được giữ
I03, I07, I08 (Save là snapshot bất biến; merge không làm đổi snapshot đã lưu).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Chỉ dùng hai cột UNIQUE như §7.1 | Đơn giản; đúng chữ đặc tả | Không giải được merge sau khi đã tồn tại hai hàng; post-only không có khóa | Phá REQ-AC13 và REQ-AC07 ở trường hợp thực tế |
| Merge tự động khi tiêu đề giống nhau | Giảm số conflict phải xử lý tay | Merge đoán; sai một lần là mất nguồn và sai first-announcement | SRC-PLAN cấm merge đoán; hậu quả không đảo được |
| Không merge bao giờ, chấp nhận hai hàng | Không bao giờ mất dữ liệu | Vi phạm D17 và chỉ số §1.4 ngay ở trường hợp phổ biến nhất | Mất chính giá trị mà người dùng cần |
| Giữ chỉ số "0 trùng" tuyệt đối | Không phải sửa §1.4 | Không đo được vì mẫu số không xác định | PC09 không lập được traceability cho chỉ số |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §1.4 (chỉ số vận hành), §3.2 (D33), §3.5 (D17, D29), §7.1, §9.2, §9.3 (hàng arXiv/OpenAlex lỗi và hàng Save lặp), AC-07, AC-09, AC-13; SRC-PLAN §7 (I03, I07), §9.1, §10 (`IDENTITY_CONFLICT`).
- Oracle bị ảnh hưởng: REQ-S1.4-03 (phạm vi), REQ-AC07 (alias map và provenance), REQ-AC09 (first-announced sau merge).
- Amendment: AMD-B15.
