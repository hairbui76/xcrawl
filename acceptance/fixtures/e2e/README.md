---
contract_id: CT-fixture-e2e-index
version: 0.1.0
status: draft
owner_role: connector contract owner
source_refs: [SRC-SPEC §5.2, SRC-SPEC §9.1, SRC-SPEC §9.2, SRC-PLAN §8.1, SRC-PLAN §9.2, SRC-PLAN §13]
requirement_refs: [REQ-S5.2-01, REQ-P0-03, REQ-P0-04, REQ-P0-05, REQ-P0-06, REQ-P0-07, REQ-P0-09, REQ-S9.2-02, REQ-S9.2-03, REQ-S9.2-06, REQ-S10.4-01, REQ-D07, REQ-D22, REQ-D46, REQ-D53, REQ-D54]
decision_refs: [B01, B02, B04, B05, B07, B12, B17, AMD-B02, AMD-B05, AMD-B07, "R-01 (A1-R1)", "R4-01 (FIX4)", "R4-02 (FIX4)", "R5-02 (FIX5)"]
invariant_refs: [I02, I04, I05, I06, I07, I09, I12, I13, I16]
producers: [MOD-scheduler, MOD-x-collector, MOD-analysis-worker]
consumers: [MOD-job-service, MOD-ingest-service, MOD-analysis-service, MOD-report-service, MOD-delivery-service]
dependencies:
  - contracts/state/run.yaml
  - contracts/state/analysis.yaml
  - contracts/state/report.yaml
  - contracts/state/delivery.yaml
  - contracts/data/entities.yaml
  - contracts/http/openapi.yaml
  - acceptance/scenarios.yaml
scope: >-
  Thư mục fixture đầu-cuối. Hiện có đúng một file, cho SC50 — đường chạy THÀNH CÔNG từ mốc lịch tới tin đã gửi.
  Mọi file ở đây dùng `rows.<entity>[]` có cấu trúc để gate field-level (R4-01) không rỗng.
verification: >-
  EV-PC05-07 (SELF_VALIDATION) và `evidence/tools/e0_check.py` (đọc-only): `E0-14-fixture-actor-edge` và
  `E0-15-fixture-field-existence` chạy qua thư mục này. `evidence_status` của mọi fixture là `NOT_RUN`.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture đầu-cuối (e2e)

## Vì sao thư mục này tồn tại

48 scenario đầu tiên của danh mục đều là **nhánh lỗi** hoặc **một lát cắt**: CAPTCHA, mất ACK, lease cũ, hết ổ
đĩa, tag đổi trước CAS, delivery không rõ. Không cái nào khẳng định rằng một đợt chạy **bình thường** kết thúc
đúng.

Một bộ hợp đồng chỉ có ca âm không chứng minh được ca dương nào. Nó có thể mô tả một hệ thống từ chối mọi thứ
một cách hoàn hảo. SC50 là đối chứng dương: nó nói ra, bằng số hàng cụ thể, một đợt chạy thành công **để lại
đúng cái gì** trong cơ sở dữ liệu.

## Danh mục

| File | Scenario | Chủ đề |
| --- | --- | --- |
| `a-happy-path-schedule-to-delivered.json` | `SC50` | Lịch tới hạn → claim → thu thập → ingest + checkpoint → làm giàu → nhãn + embedding + summary → build → publish (CAS) → outbox intent → gửi → `delivery.state = sent` |

## Hình dạng file

| Khóa | Nghĩa |
| --- | --- |
| `given.rows.<entity>[]` | Hàng đã tồn tại TRƯỚC scenario |
| `events[]` | Chuỗi sự kiện theo thứ tự; khóa operation là **`operation`** (R4-02) |
| `events[].actor` | Module **gọi** — phải là caller được phép theo `contracts/ports.yaml.caller_modules` |
| `events[].performed_by` | Service **thực hiện** transaction. **KHÔNG** phải khẳng định về cạnh gọi (R-02) |
| `events[]._commit_boundary` | Ranh giới commit mà sự kiện đó đóng lại (B1…B11). Đây là trục chính của fixture |
| `expected.rows.<entity>[]` | Hàng bền SAU scenario, theo từng entity |
| `expected.counts` | Số hàng kỳ vọng — phần dễ kiểm nhất bằng SQL |
| `expected.equalities_vi` | Sáu đẳng thức bất biến phải ĐỒNG THỜI đúng |
| `forbidden_effects` | Điều **không được** xảy ra kể cả ở đường thành công |

## Quy ước ghi chú trong `rows` (ruling R4-01) — bắt buộc ở cả bảy thư mục fixture

Dưới `given.rows.<entity>[]` và `expected.rows.<entity>[]`, **mọi khóa** phải là một trong ba loại:
(a) một cột CÓ THẬT trong `contracts/data/entities.yaml` cho entity đó; (b) một chú thích có khóa **bắt đầu
bằng `_`** (`_note`, `_target`, `_case`, `_commit_boundary`, …); hoặc (c) một cột mang marker
`pending_cr: CR-…` ngay trong file. **Không có allowlist riêng cho từng gói.**

Lý do: nếu mỗi gói tự giữ một danh sách ngoại lệ riêng thì gate kiểm cột không còn đáng tin — nó có thể báo
PASS trong khi hàng chục khóa chưa resolve (F-A1R3-01: 89 khóa trên 25 file). Một quy ước duy nhất làm cho một
checker độc lập cho ra CÙNG con số với checker của gói.

## `edge_assertion: forbidden` (ruling R4-02)

Một sự kiện CỐ Ý khẳng định một cạnh **bị cấm** phải mang `edge_assertion: "forbidden"`; khi đó gate actor-edge
**đảo kỳ vọng** (bộ ba phải VẮNG khỏi `allowed_edges`, lỗi mong đợi là `UNAUTHORIZED` / `FORBIDDEN_EDGE` /
`CAPABILITY_DENIED`).

**Không fixture nào ở đây dùng nó, và đúng ra là vậy:** SC50 là đường thành công, nên mọi cạnh trong nó phải
là cạnh ĐƯỢC PHÉP. Một `edge_assertion` xuất hiện trong thư mục này sẽ là dấu hiệu fixture đã lạc chủ đề.

## Giới hạn đã biết

1. **Chưa chạy.** `evidence_status: NOT_RUN`. Fixture mô tả hợp đồng, không phải kết quả quan sát được.
2. **`report.report_build_id` và `report.abort_reason`** được dùng theo bảng field-level của ruling FIX3.
   Nếu `entities.yaml` chưa khai hai cột đó thì gate field-level sẽ báo — đó là hành vi ĐÚNG, và là mặt còn
   lại của F-A1R2-01.
3. **Một đợt chạy THẬT đầu-cuối là E3**, thuộc SP1 và giai đoạn triển khai. Giá trị của khối "hướng đang nổi"
   là E4 và cần 3–4 kỳ thật (REQ-A4). Fixture này chỉ chứng minh **hình dạng dữ liệu**, không chứng minh chất
   lượng nội dung.
4. **Số hàng ở đây là tối thiểu** (2 post, 2 work, 2 analysis) — đủ để mọi đẳng thức có ý nghĩa mà vẫn đọc
   được. Nó không đại diện cho tải thật.
