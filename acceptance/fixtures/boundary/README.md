---
contract_id: CT-fixture-boundary-index
version: 0.1.0
status: draft
owner_role: architecture owner
source_refs: [SRC-PLAN §6, SRC-PLAN §7 I01, SRC-PLAN §7 I11, SRC-PLAN §13, SRC-SPEC §6.1, SRC-SPEC §11.4, SRC-SPEC §12 AC-17, SRC-SPEC §12 AC-18]
requirement_refs: [REQ-D01, REQ-D08, REQ-D42, REQ-D50, REQ-S6.1-01, REQ-S6.1-02, REQ-S6.1-03, REQ-S11.2-01, REQ-S11.2-02, REQ-AC17, REQ-AC18]
decision_refs: [B12, B13, AMD-B12, ADR-0001, ADR-0010, R5-01, R5-02]
invariant_refs: [I01, I11]
producers: [MOD-backend-api]
consumers: [MOD-web-ui, MOD-x-collector, MOD-analysis-worker, MOD-ai-adapter, MOD-telegram-adapter, MOD-backup-cli, MOD-scheduler]
dependencies:
  - contracts/modules.yaml
  - contracts/capabilities.yaml
  - contracts/ports.yaml
  - contracts/errors.yaml
  - acceptance/scenarios.yaml
scope: >
  Fixture cho `SC49` — quét default-deny trên **toàn bộ** 36 cạnh bị cấm của `contracts/modules.yaml`.
  Mỗi cạnh có một event mang `edge_assertion: forbidden`, caller là chính module bị cấm, credential là credential
  **hợp lệ** của caller đó, và mã lỗi mong đợi lấy nguyên từ `denied_cases[].expected_error_code`.
verification: >
  E0: fixture parse; mọi `operation`, mã lỗi và module được trích tồn tại ở upstream; mọi event
  `edge_assertion: forbidden` có bộ ba **không** nằm trong `allowed_edges`; số event bằng số `forbidden_edges`.
  Chưa chạy: **NOT_RUN**.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture ranh giới (default deny) — SC49

## Danh mục

| File | Nội dung | Scenario | Invariant |
| --- | --- | --- | --- |
| `a-default-deny-sweep-36-edges.json` | 36 event, một cho mỗi cạnh `FE-01`…`FE-36`; mỗi event mang `edge_assertion: forbidden`, `denied_case_ref`, `expected_error_code` và `enforcement` | SC49 | I01, I11 |

## Vì sao thư mục này tồn tại

`SC49` là mặt **âm** của toàn bộ registry: nó khẳng định rằng mọi cạnh **không** có trong `allowed_edges` đều bị
từ chối. Trước ruling R5-01, chỉ 10 trong 36 cạnh có mã lỗi được pin, nên scenario có oracle "không đổi trạng
thái" cho cả 36 nhưng chỉ có oracle "đúng mã lỗi" cho 10 — check `E0-10b-denied-edge-oracle` FAIL với 26 vi phạm.
Nay `contracts/modules.yaml` có **36 `denied_cases`** khớp 1–1 với 36 `forbidden_edges`, và fixture này là dữ liệu
vào tương ứng.

## Bảng mã lỗi (ruling R5-01, ràng buộc)

| Tình huống | Mã |
| --- | --- |
| Request HTTP bởi một **lớp principal không được phép** cho operation đó | `UNAUTHORIZED` (401) |
| Lời gọi/import **trong cùng tiến trình** qua cạnh không có trong `allowed_edges` | `FORBIDDEN_EDGE` |
| Thiếu **capability** tiến trình/mạng/filesystem/tool của actor | `CAPABILITY_DENIED` |
| Mutation của owner session thiếu CSRF hợp lệ | `CSRF_REJECTED` |

Phân bố thực tế trên 36 cạnh: `CAPABILITY_DENIED` 15 · `UNAUTHORIZED` 9 · `FORBIDDEN_EDGE` 7 ·
`UNAUTHORIZED_COMMAND` 3 · `RESTORE_UNVERIFIED` 2.

**Hai mã ngoài bảng, đã được phê chuẩn** (Coordinator ruling FIX6, A2-R1 — `CR-PC01-09` **APPROVED**: hai mã
này hợp lệ cho denied case nằm ngoài bảng bốn dòng R5-01 khi đặc tả gọi tên chúng)**:**

- `UNAUTHORIZED_COMMAND` (FE-30, FE-31, FE-33) — attempt đến qua **ingress Telegram**, nơi đặc tả bắt buộc **bỏ im
  lặng** (REQ-S11.3-02, AC-18): trả lời "không có quyền" cho một chat lạ là tự xác nhận bot tồn tại. Đây vẫn là
  dòng "sai lớp principal" của bảng, chỉ được hiện thực bằng mã chuyên biệt mà `errors.yaml` đã đăng ký cho đúng
  đường này.
- `RESTORE_UNVERIFIED` (FE-34, FE-35) — cạnh bị chặn bởi **guard trạng thái** (`storage.health =
  recovery_required`), không bởi thiếu quyền: **cùng caller đó được phép** sau khi `backup.reconcile_after_restore`
  thành công. "Chưa được phép lúc này" khác "đường đi không tồn tại", và I15 cần phân biệt được hai thứ.

## Quy ước chú thích trong `given.rows` / `expected.rows` (R4-01, ràng buộc mọi thư mục fixture)

> Dưới `given.rows.<entity>[]` và `expected.rows.<entity>[]`, **mọi khóa** phải là một trong ba loại: (a) một cột
> **tồn tại** trong `contracts/data/entities.yaml` cho đúng entity đó; (b) một chú thích có khóa **bắt đầu bằng
> `_`** (`_note`, `_target`, `_note_vi`, …); hoặc (c) một cột mang **`pending_cr: CR-…`** ngay trong file. Không có
> allowlist riêng cho từng gói.

**Trạng thái của thư mục này:** fixture SC49 khẳng định về **cạnh và mã lỗi**, không về hàng dữ liệu — oracle của
nó là "tổng `COUNT(*)` mọi bảng **không đổi**", một phép đo không cần liệt kê cột nào. Do đó không có
`rows.<entity>[]` và **0 cột** thuộc phạm vi quy tắc trên. Nếu về sau cần khẳng định ở mức hàng, quy tắc áp dụng
ngay.

## Quy ước `actor` và `edge_assertion` (R4-02)

- Khóa của event là **`operation`** (không phải `operation_id`).
- `edge_assertion: forbidden` là dấu chuẩn cho event cố tình thử cạnh bị cấm. Gate `fixture-actor-edge` kiểm hai
  điều: bộ ba `(actor, owner_module, operation)` **không** có trong `allowed_edges`, **và** `expected` chứa một mã
  hợp lệ cho ca âm. **Cả 36 event ở đây đều là `forbidden`** — đó là toàn bộ mục đích của thư mục.
- `actor` ở đây là **caller bị cấm**, đúng như `denied_cases[].attempted_edge.caller`.
- **Event có `operation: null` PHẢI mang `event_type`** (R4-02; gate dùng chung thực thi điều này). Năm event ở
  đây rơi vào trường hợp đó — FE-03, FE-08, FE-17, FE-20, FE-21 — vì cạnh của chúng không tương ứng một operation
  nào của `ports.yaml`: đó là truy cập tài nguyên hoặc mở kết nối trực tiếp. Hai giá trị được dùng:

| `event_type` | Nghĩa | Oracle | Event |
| --- | --- | --- | --- |
| `in_process_call` | Lời gọi mã/IPC cục bộ qua một cạnh không có trong `allowed_edges` | Import/dependency rule, phân tích tĩnh | seq 8 (FE-08), seq 26 (FE-26) |
| `local_observation` | Attempt chạm tài nguyên hoặc mở kết nối mạng, không tương ứng operation nào | Đếm kết nối theo host class, process capability | seq 3 (FE-03), 17 (FE-17), 20 (FE-20), 21 (FE-21) |

  Hai giá trị này khớp với cách bảng R5-01 phân loại mã lỗi: `in_process_call` đi cùng `FORBIDDEN_EDGE`,
  `local_observation` đi cùng `CAPABILITY_DENIED`. 31 event còn lại có `operation` thật nên không mang khóa này.
  Mỗi event `null` cũng giữ `operation_absent_reason_vi` và `event_type_reason_vi` giải thích lựa chọn.

## Khi nào một event được mang tên `operation` (F-A2R1-05)

`attempted_edge.operation` — và `operation` của event tương ứng — chỉ được mang một tên khi **callee phục vụ được**
nó:

| Callee | Quy tắc | Ví dụ |
| --- | --- | --- |
| `MOD-*` | Chỉ khi **chính callee đó sở hữu** operation trong `ports.yaml` | seq 6 (FE-06) `save.create` do `MOD-saved-service` sở hữu |
| `EXT-*` | Hệ thống ngoài không sở hữu operation nào của ta, nên tên ở đây là **port nội bộ mà kẻ vi phạm đang cố tạo ra hiệu ứng của nó** — đọc là "module này cố tự làm việc mà chỉ port kia được phép làm" | seq 16 (FE-16) `telegram.send_payload` cho `EXT-telegram-api` |
| Không thoả cả hai | `operation: null` + `event_type` + `operation_absent_reason_vi` | seq 26 (FE-26) |

Trường hợp seq 26 (`FE-26` `MOD-scheduler → MOD-x-collector`) là lý do quy tắc này được viết ra. Trước FIX10 nó ghi
`operation: worker.claim_assignment` — nhưng operation đó do **`MOD-job-service`** sở hữu và caller duy nhất của nó
là **`MOD-x-collector`**, tức nó chạy theo chiều **ngược lại**. Máy cá nhân không lắng nghe cổng nào, nên "gọi nó
rồi khẳng định lỗi" là một oracle **không chạy được** cho đúng cạnh bảo vệ "không gì gọi vào máy cá nhân". Nay nó
là `operation: null`, `event_type: in_process_call`, `expected_error_code: FORBIDDEN_EDGE` (cái vắng mặt là **cạnh**
— collector **kéo** việc theo D11 — chứ không phải một capability của scheduler).

Quy ước cho `EXT-*` trước FIX10 **không được ghi ở đâu**; nay nó nằm trong
`contracts/modules.yaml` `default_deny.attempted_edge_operation_rule_vi` và được gate kiểm.

## Song ánh cạnh ↔ denied case ↔ event (CR-PC01-10)

Mỗi cạnh trong 36 `forbidden_edges` có **đúng một** `denied_cases[]` và **đúng một** event ở đây, và bộ
`(caller, callee)` của cả ba phải bằng nhau. Gate của W2 kiểm điều này từ FIX9; trước đó nó chỉ kiểm "có một case
được pin", cũng như `E0-10b`.

Vì sao cần thêm phép kiểm này: `FE-20` (`MOD-research-connector → EXT-x-web`) và `FE-21`
(`MOD-research-connector → EXT-chrome-profile`) từng **cùng** trỏ tới `EXT-chrome-profile` — `NC-08` mang
`forbidden_edge_ref: FE-20` nhưng `attempted_edge.callee` là `EXT-chrome-profile`, và `NC-24` mô tả đúng cạnh đó
lần thứ hai. Kết quả: `FE-20` không có case nào mô tả đúng cạnh của nó, trong khi mọi check hiện có vẫn PASS. Đây
là lớp lỗi "đếm đủ nhưng nội dung sai" mà chỉ một phép so **nội dung** mới bắt được.

Sau FIX9: `NC-08` → `FE-21` (profile Chrome trên máy cá nhân; oracle là process capability), `NC-24` → `FE-20`
(nguồn X trên mạng; oracle là đếm kết nối tới host của X từ container server). Hai cách thất bại khác nhau nên
cần hai case, không phải hai bản sao của một case.

## Điều fixture này **không** chứng minh

Nó là dữ liệu vào và oracle, **`NOT_RUN`**. Một fixture nhất quán với registry không chứng minh guard nào chạy: 36
cạnh có lý do và mã lỗi vẫn chỉ là văn bản cho tới khi có import rule thật, API auth test thật và process sandbox
thật (SRC-PLAN §14.2, E0). Đặc biệt FE-21 (`EXT-chrome-profile`) chỉ kiểm được đầy đủ trên máy cá nhân có Chrome
thật.
