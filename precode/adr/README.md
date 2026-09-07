---
contract_id: CT-precode-adr-index
version: 0.1.0
status: draft
owner_role: requirements owner (PC00)
source_refs: [SRC-PLAN §3, SRC-PLAN §8, SRC-PLAN §9, SRC-SPEC §3, SRC-SPEC §6, SRC-SPEC §9]
requirement_refs: [precode/requirements.csv]
decision_refs: [B01, B02, B03, B06, B07, B08, B11, B12, B13, B15]
invariant_refs: [I02, I03, I04, I05, I07, I09, I11, I12, I15]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/baseline.json, precode/decision-register.md]
scope: >
  Chỉ mục và mẫu ADR cho giai đoạn Pre-code. Mỗi ADR ghi lại một quyết định cấu trúc phát sinh
  từ một blocker B01-B17 hoặc từ một lựa chọn kỹ thuật bắt buộc. Không ADR nào trong thư mục này
  ở trạng thái accepted.
verification: E0 - kiểm bằng script rằng mỗi file ADR có đủ các mục bắt buộc (EV-PC00-05).
claim_ceiling: DRAFT_FOR_REVIEW
---

# Chỉ mục ADR — Research Radar Pre-code

## Ngoại lệ header đã được khai báo (ruling R-05)

ADR **không** mang đủ header hợp đồng của baseline §3. Đây là một **ngoại lệ được khai báo**, không phải
thiếu sót: ADR là *decision record*, không phải hợp đồng — nó không có producer/consumer runtime, không có
schema và không được kiểm bằng fixture, nên các trường `contract_id`, `version`, `owner_role`, `producers`,
`dependencies`, `scope`, `verification` không có nghĩa với nó.

- **Nguồn ngoại lệ:** finding `F-A1R1-05` của `auditor-A1` (AUDIT_REPORT PKT-A1-R1) → ruling **R-05** của
  Coordinator, 2026-09-06T18:00Z. Coordinator đã sửa baseline §3 tương ứng (đoạn "Exception (Coordinator
  ruling R-05…)").
- **Front-matter bắt buộc của một ADR** — đúng mười trường, không thiếu trường nào:

  `adr_id` · `title` · `status` · `date` · `decision_owner` · `source_refs` · `requirement_refs` ·
  `decision_refs` · `affected_packages` · `supersedes`

- Các trường `blocker_refs`, `amendment_refs`, `invariant_refs`, `consumers`, `claim_ceiling` được **giữ thêm**
  vì đã tồn tại từ epoch 1 và có ích cho truy vết. `decision_refs` là hợp của `blocker_refs` và
  `amendment_refs`; `affected_packages` trùng nội dung với `consumers`. Cả hai cặp phải nhất quán.
- `supersedes` là danh sách ADR bị thay thế. Hiện mọi ADR đều `[]`: chưa có ADR nào bị thay thế.
- Ngoại lệ này cũng được ghi trong `evidence/handoffs/PC00-handoff.md` (addendum PKT-PC00-FIX1) như một
  declared exception, đúng yêu cầu remediation của `F-A1R1-05`.

Ngoại lệ khai báo còn lại của PC00: `precode/requirements.csv` mang header trong
`precode/baseline.json` khóa `requirements_csv_contract_header` (xem baseline §3 và handoff §6.3).

## Trạng thái được phép

| Status | Nghĩa | Ai chốt |
| --- | --- | --- |
| `proposed` | Quyết định làm đổi hành vi đã cam kết hoặc đánh đổi mà người dùng đã chọn; chờ Owner | Owner |
| `provisional-accepted` | Chi tiết thuần kỹ thuật, nằm trong phạm vi ủy quyền; đã ghi căn cứ; vẫn có thể bị Owner đảo | Coordinator dưới `AUTH-OWNER-20260906-01` |
| `accepted` | Owner đã phê chuẩn | Owner, qua `OD-20260907-01` |

**Cập nhật 2026-09-07.** Cả **10** ADR nay ở trạng thái `accepted`, phê chuẩn bằng `OD-20260907-01`
(`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`, evidence
`session_017QmDJtMqD9o1z79waqSB9W`). Mỗi file mang `ratified_by`, `ratified_at` và `evidence_ref` trong
front-matter, cùng một banner ở mục "Trạng thái"; lập luận lúc còn `proposed` được **giữ nguyên bên dưới**
để truy vết, không bị viết lại.

**ADR-0006 là ngoại lệ về nội dung:** Owner chọn phương án **B (Python workers + TypeScript web)**, không phải
A. File đã được viết lại; **tên file giữ nguyên** `ADR-0006-stack-option-a.md` vì 18 task card và chỉ mục này
trỏ theo đường dẫn đó — đổi tên cần một packet riêng (`CR-PC00-16`).

Không ADR nào được ghi `superseded` hay `deprecated` trong phiên này.

## Bảng chỉ mục

| ADR | Tiêu đề | Blocker | Status | Gói tiêu thụ |
| --- | --- | --- | --- | --- |
| [ADR-0001](ADR-0001-topology-and-placement.md) | Topology và nơi chạy từng module | B12 | accepted | PC01, PC05, PC06 |
| [ADR-0002](ADR-0002-run-state-model-split.md) | Tách mô hình trạng thái run | B02 | accepted | PC03, PC07 |
| [ADR-0003](ADR-0003-delivery-unknown-state.md) | Trạng thái delivery không xác định | B03 | accepted | PC07 |
| [ADR-0004](ADR-0004-tag-freeze-point.md) | Mốc freeze tag tại publish | B01, B04 | accepted | PC04, PC07 |
| [ADR-0005](ADR-0005-backup-method.md) | Phương pháp backup và restore | B11 | accepted | PC08 |
| [ADR-0006](ADR-0006-stack-option-a.md) | **Stack Option B (Python workers + TypeScript web)** | — (REQ-OQ02) | accepted | PC10 |
| [ADR-0007](ADR-0007-timezone-handling.md) | Timezone và chuẩn timestamp | B08 | accepted | PC03, PC04 |
| [ADR-0008](ADR-0008-analysis-key-and-generation.md) | Analysis key và generation | B07 | accepted | PC02, PC06 |
| [ADR-0009](ADR-0009-identity-alias-target-union.md) | Identity, alias và target tagged union | B06, B15 | accepted | PC02, PC04 |
| [ADR-0010](ADR-0010-secret-scoping-and-cli-isolation.md) | Phạm vi secret và cô lập CLI/ACP | B13 | accepted | PC01, PC06, PC08 |

## Mẫu ADR

```markdown
---
adr_id: ADR-NNNN
title: <tiêu đề ngắn>
status: proposed | provisional-accepted | accepted
decision_owner: Owner | Coordinator (delegated)
date: YYYY-MM-DD
ratified_by: OD-…            # khi status = accepted
evidence_ref: "…"           # khi status = accepted
blocker_refs: [B..]
source_refs: [SRC-SPEC §.., SRC-PLAN §..]
requirement_refs: [REQ-..]
invariant_refs: [I..]
amendment_refs: [AMD-B..]
decision_refs: [B.., AMD-B..]      # bắt buộc theo R-05: hợp của blocker_refs và amendment_refs
consumers: [PC..]
affected_packages: [PC..]          # bắt buộc theo R-05: trùng consumers
supersedes: []                     # bắt buộc theo R-05: danh sách ADR bị thay thế
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-NNNN — <tiêu đề>

## Bối cảnh
<vấn đề, nguồn mâu thuẫn, ràng buộc>

## Quyết định
<phát biểu quyết định ở thể khẳng định, có số và đơn vị nếu có>

## Trạng thái
<status + ai phải chốt + điều kiện để đổi trạng thái>

## Hệ quả
### Tích cực
### Tiêu cực và chi phí
### Bất biến được giữ

## Phương án đã cân nhắc
| Phương án | Ưu | Nhược | Vì sao không chọn |

## Nguồn và truy vết
<source refs, requirement refs, invariant refs, oracle bị ảnh hưởng>
```

## Quy tắc

1. Một ADR cho một quyết định. Không gộp hai blocker vào một ADR trừ khi chúng chia chung đúng một cơ chế (ADR-0009 gộp B06 và B15 vì cùng dựa trên canonical identity).
2. ADR không thay thế amendment: amendment sửa **câu chữ** của đặc tả, ADR ghi **lý do và đánh đổi**. Xem `precode/decision-register.md` §3.
3. ADR mới đánh số tăng dần, bốn chữ số, không dùng lại số đã cấp kể cả khi ADR bị bác bỏ.
