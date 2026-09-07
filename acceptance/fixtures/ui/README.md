---
contract_id: CT-fixtures-ui
version: 0.1.0
status: draft
owner_role: interaction contract owner
source_refs:
  - "SRC-SPEC §4 (bảng màn hình)"
  - "SRC-SPEC §5.1 (thiết lập lần đầu, bước 1–5)"
  - "SRC-SPEC §5.3 (đọc và Save)"
  - "SRC-SPEC §12 AC-10"
  - "acceptance/scenarios.yaml SC10, SC51"
  - "FIX5-rulings R5-02, R5-03"
requirement_refs:
  - REQ-AC10
  - REQ-D19
  - REQ-D20
  - REQ-D21
  - REQ-D05
  - REQ-D09
  - REQ-D35
  - REQ-D39
  - REQ-D41
  - REQ-D46
  - REQ-S4-02
  - REQ-S4-03
  - REQ-S4-04
  - REQ-S4-07
  - REQ-S4-08
  - REQ-S5.1-01
  - REQ-S5.1-02
  - REQ-S5.1-03
  - REQ-S5.1-04
  - REQ-S5.1-05
  - REQ-S5.3-01
  - REQ-S5.3-02
  - REQ-S5.3-03
  - REQ-OQ01
decision_refs: [B01, B09, B13, AMD-B09, AMD-B16, ADR-0010]
invariant_refs: [I01, I05, I11, I12, I16]
producers: [MOD-web-ui, MOD-report-service, MOD-delivery-service]
consumers: [MOD-web-ui, MOD-telegram-adapter]
dependencies:
  - contracts/ui/screens.yaml
  - contracts/telegram/commands.yaml
  - contracts/telegram/delivery.md
  - contracts/data/entities.yaml
  - contracts/ports.yaml
  - acceptance/scenarios.yaml
scope: >-
  Fixture cho hai scenario mà trước đây không có: SC10 (một analysis revision hiển thị giống
  nhau trên app và Telegram, đủ năm trường REQ-D20) và SC51 (thiết lập lần đầu theo SRC-SPEC
  §5.1 bước 1–5). Đây là DỮ LIỆU VÀO + ORACLE, không phải test đã chạy.
verification: "Gate dùng chung: fixture-actor-edge và fixture-field-existence (R4-01) trên cả sáu thư mục. E1–E4: NOT_RUN."
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture UI — chỉ mục và cách dùng

## 0. Quy tắc khóa trong `rows` (ruling R4-01, bắt buộc ở CẢ SÁU thư mục fixture)

> Dưới `given` → `rows` → `<entity>[]` và `expected` → `rows` → `<entity>[]`, mỗi khóa phải là MỘT trong:
> (a) một cột tồn tại trong `contracts/data/entities.yaml` cho entity đó, HOẶC
> (b) một annotation có khóa **bắt đầu bằng `_`** (`_note`, `_target`, `_note_vi`, …), HOẶC
> (c) một cột mang marker `pending_cr: CR-…` trong chính file đó.
> Không có allowlist riêng theo gói.

Lý do: một khóa trần trông giống một cột. Khi nó không phải cột, người đọc hợp đồng không phân
biệt được "fixture khẳng định một cột" với "fixture ghi chú cho người đọc", và gate kiểm cột
buộc phải mang allowlist — allowlist đó chính là chỗ lỗi ẩn nấp (F-A1R3-01). Tiền tố `_` làm
ranh giới đó hiện lên trong chính dữ liệu.

Theo **R4-02**: event object dùng khóa `operation` (không phải `operation_id`); sự kiện không
phải operation dùng `event_type`. Thư mục này **không** có event cạnh bị cấm nên không dùng
marker `edge_assertion: forbidden`.

## 1. Danh mục

| File | ID | Kiểm tra | Scenario | Invariant |
| --- | --- | --- | --- | --- |
| `sc10-same-analysis-revision-app-and-telegram.json` | FX-UI-SC10 | Một `analysis` revision hiển thị trên app và Telegram với đủ năm trường REQ-D20; `analysis_id` giống nhau ở hai kênh; bản mới hơn xuất hiện sau publish KHÔNG được dùng | SC10 | I05, I16 |
| `sc51-first-time-setup.json` | FX-UI-SC51 | Thiết lập lần đầu §5.1 bước 1–5: đăng nhập, tag + preview, provider config, mã liên kết Telegram, đăng ký collector với profile Chrome riêng | SC51 | I01, I11, I12 |
| `README.md` | — | Chỉ mục này | — | — |

Thư mục có **3 file**: 2 JSON + README.

## 2. Năm trường bắt buộc của SC10

`content` · `difference_from_prior` · `limitation_vi` · `evidence_level` · `matched_tags[]`.

Nguồn: REQ-D20 (nội dung + điểm khác với cái đã có + một dòng hạn chế), REQ-D21 (nhãn mức độ
đọc), REQ-AC10 (dòng "khớp tag nào"). Thiếu **bất kỳ** trường nào ở **bất kỳ** kênh nào khiến
scenario FAIL — fixture khẳng định điều này ở `expected` → `oracles`, không để ngầm.

Oracle mạnh nhất của SC10 là **sự bằng nhau**: `analysis_id ở kênh app bằng analysis_id ở kênh Telegram`. Trong
`given` cố ý có một `analysis` thứ hai (generation 2) xuất hiện **sau** `report.published_at`;
bất kỳ kênh nào tham chiếu nó là vi phạm I05.

## 3. Marker `pending_cr`: hiện KHÔNG còn cái nào

Trước PKT-PC02-FIX5, `sc51-first-time-setup.json` khai `provider_config.terms_check_at` với
`pending_cr: CR-PC07-07` vì `ENT-provider-config` chỉ có `enabled`, nên oracle của SC51 chỉ
khẳng định được dạng **yếu** (`COUNT(enabled = true) = 0`).

PC02 đã thêm `terms_check_at`, `terms_check_by`, `terms_doc_ref` cùng CHECK
`ck_provider_config_terms_before_enable` (`enabled ⇒ terms_check_at IS NOT NULL`). Marker vì
vậy đã được gỡ và oracle nay ở **dạng mạnh**:
`COUNT(provider_config WHERE enabled = true AND terms_check_at IS NULL) = 0` — ép được ở mức
dữ liệu, không còn là văn xuôi (REQ-A5, ADR-0010).

`terms_doc_ref` vẫn là `KC`: giai đoạn Pre-code không có mạng nên chưa điều khoản của nhà nào
được đọc. Cột khóa CHỖ ĐỂ GHI; điền giá trị suy đoán vào đó bị cấm.

## 4. Cái bộ fixture này KHÔNG chứng minh

- SC10 cần **E4**: "không cần mở nguồn để quyết định" là phán đoán của người đọc trên desktop,
  điện thoại và Telegram thật, theo rubric `contracts/ai/grounding.md` §6. Fixture chỉ neo được
  sự hiện diện của năm trường và sự bằng nhau của `analysis_id` (E1).
- SC10 phần render Telegram còn phụ thuộc giới hạn định dạng vẫn `KC` (CR-PC07-04).
- SC51 bước 5 cần **E3**: Chrome thật, profile riêng thật, một người xử lý màn hình xác minh
  thiết bị mới của X. **REQ-OQ01 (xác nhận REQ-D09) vẫn CHẶN M0**; fixture KHÔNG promote D09,
  vốn vẫn ở trạng thái `ĐX` trong một hạng mục P0.
- Không fixture nào ở đây chứng minh code chạy đúng: chưa có code (E0).

## 5. Bất biến khi sửa

Sửa một `expected` để triển khai pass là vi phạm hợp đồng (SRC-PLAN §15). Oracle sai ⇒ mở
change request kèm bằng chứng.
