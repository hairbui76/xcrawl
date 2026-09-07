---
adr_id: ADR-0008
title: Analysis key và generation
status: provisional-accepted
decision_owner: Coordinator (delegated under AUTH-OWNER-20260906-01)
date: 2026-09-06
blocker_refs: [B07]
source_refs: [SRC-SPEC §3.5, SRC-SPEC §7.1, SRC-SPEC §7.3, SRC-SPEC §9.2, SRC-SPEC §9.3, SRC-SPEC §10.4, SRC-SPEC AC-06, SRC-PLAN §8.2, SRC-PLAN §9.3]
requirement_refs: [REQ-D25, REQ-D26, REQ-AC06, REQ-S7.3-02, REQ-S9.2-03, REQ-S10.4-02, REQ-S8.1-04]
invariant_refs: [I04, I12]
amendment_refs: [AMD-B07]
decision_refs: [B07, AMD-B07]
consumers: [PC02, PC06]
affected_packages: [PC02, PC06]
supersedes: []
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0008 — Analysis key và generation

## Bối cảnh

SRC-SPEC D25 (XN) nói "Phân tích và summary tạo **một lần** cho mỗi công trình rồi tái sử dụng". D26 (ĐX) ngay bên dưới lại cho phép phân tích lại khi người dùng bấm tay hoặc paper có phiên bản mới. Đọc theo nghĩa đen, D25 loại trừ D26 và loại trừ cả việc thử lại sau lỗi (§9.3 cho phép thử lại một lần).

Bảng `analysis` ở §7.1 chỉ có "phiên bản" mà không có source fingerprint hay task key, nên không có cách nào phát biểu chính xác "một lần" là một lần theo chiều nào.

## Quyết định

1. **Analysis key** gồm năm thành phần: canonical id của target, source version/fingerprint, task type, phiên bản prompt/schema, và generation.
2. Với mỗi analysis key, hệ thống giữ **tối đa một kết quả hợp lệ**.
3. **Đổi tag không đổi key** — đây là điều làm cho REQ-AC06 đúng và là hệ quả trực tiếp của việc tách ba lớp ở §8.1.
4. Reanalysis theo D26 tạo **generation mới**; bản cũ được giữ (D26 đã yêu cầu).
5. Attempt thất bại hoặc không xác định (`unknown_attempt`) **không** phải kết quả. Output sai schema không bao giờ được ghi thành `valid`.
6. Đổi provider hoặc model **không tự** invalidate kết quả cũ; giữ đến khi Owner yêu cầu reanalysis. Đây là mặc định rẻ nhất và có thể đảo.
7. Vector embedding có generation riêng: đổi model embedding xây generation mới, kiểm đủ vector rồi mới chuyển active generation một cách nguyên tử. Không trộn vector khác model/dimension trong cùng một lần selection.

## Trạng thái

`provisional-accepted`. Đây là chi tiết kỹ thuật nằm trong phạm vi ủy quyền: nó **không** đảo bất kỳ hành vi nào người dùng đã chọn — D25 vẫn đúng (một kết quả hợp lệ, tái sử dụng), D26 vẫn đúng (phân tích lại tạo bản mới, giữ bản cũ). Amendment AMD-B07 chỉ làm rõ câu chữ. Owner vẫn có thể đảo; nếu đảo thì D26 phải bị loại bỏ.

## Hệ quả

### Tích cực
- I04 kiểm chứng được: retry không tạo hai kết quả hợp lệ cùng key; đổi tag không gọi AI lại.
- Chi phí AI kiểm soát được đúng như §10.4 mô tả, nhưng có đường thoát hợp lệ cho reanalysis có chủ đích.
- Crash sau khi model đã chạy nhưng trước khi submit được biểu diễn trung thực bằng `unknown_attempt`, thay vì giả vờ chưa tốn tiền.

### Tiêu cực và chi phí
- Khóa năm thành phần phức tạp hơn "một hàng cho một work"; migration sau này tốn hơn.
- Đổi phiên bản prompt sẽ sinh key mới cho toàn kho — cần cân nhắc trước mỗi lần sửa prompt, nếu không sẽ phát sinh chi phí AI lớn.
- Giữ bản cũ nghĩa là bảng `analysis` chỉ lớn dần; hợp với retention vô thời hạn của D58 nhưng cần theo dõi dung lượng.

### Bất biến được giữ
I04, I12 (không so sánh vector khác model/generation/dimension trong cùng lần selection).

## Phương án đã cân nhắc

| Phương án | Ưu | Nhược | Vì sao không chọn |
| --- | --- | --- | --- |
| Một hàng `analysis` cho một `work_id` | Đúng nghĩa đen D25; đơn giản nhất | Không có chỗ cho D26, cho retry, cho phiên bản paper mới | Loại bỏ một quyết định của đặc tả |
| Khóa theo `(work_id, task_type)` | Đơn giản hơn | Đổi prompt hoặc đổi source version không invalidate được | Kết quả cũ dựa trên input cũ bị dùng lại âm thầm |
| Đổi provider/model tự invalidate toàn bộ | Kết quả luôn "mới nhất" | Một lần đổi model là một lần chạy lại toàn kho, chi phí lớn và không do người dùng chủ động | Trái §10.4 về kiểm soát chi phí |
| Ghi attempt lỗi thành một kết quả có cờ `failed` | Ít bảng hơn | Truy vấn "đã có kết quả chưa" phải luôn nhớ lọc cờ; dễ sai | Tách trạng thái attempt khỏi kết quả an toàn hơn |

## Nguồn và truy vết

- Nguồn: SRC-SPEC §3.5 (D25, D26), §7.1 (`analysis`), §7.3, §9.2, §9.3 (hàng AI lỗi một mục), §10.4, AC-06; SRC-PLAN §8.2, §9.3.
- Oracle bị ảnh hưởng: REQ-AC06 đo bằng provider call counter delta cho **cùng key và generation**.
- Amendment: AMD-B07.
