# HANDOFF — PKT-PC00

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00` |
| worker principal | `worker-W1` |
| role | Worker (development), `physical_write: true` |
| authority_id | `AUTH-COORD-PC00` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC00-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` — **không có OS enforcement**; lease được theo dõi bằng thông điệp, Worker tự thực thi scope |
| audit_route | `INDEPENDENT_REQUIRED` — audit độc lập **chưa xảy ra**; mọi verification dưới đây là `SELF_VALIDATION` |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` (trần của packet; không nâng) |
| started_at (UTC) | 2026-09-06T16:53Z |
| finished_at (UTC) | 2026-09-06T17:27Z |
| lease expires_at (UTC) | 2026-09-07T00:00Z — kiểm bằng `date -u` trước lần ghi cuối: 2026-09-06T17:25Z, còn hiệu lực |
| next actor | `Coordinator` |
| lease_released_at (UTC) | 2026-09-06T17:27Z |

**Lý do `DONE_WITH_CONCERNS`:** mọi write target đã tạo, mọi verification đã chạy và đạt, nhưng gói này
(a) phải tự quyết hai điểm sản phẩm không nằm trong baseline §5 (F-PC00-01, F-PC00-02), (b) có một sai lệch
định dạng có chủ đích ở `requirements.csv` (§6.3), và (c) quan sát thấy PC01/PC02 đã chạy song song mà
**không** đọc `precode/`, tạo rủi ro lệch tham chiếu REQ/ADR (§6.4, CR-PC00-01).

## 2. Changes

Tất cả là `CREATE`, baseline `ABSENT` (đã kiểm bằng `ls` trước khi ghi; thư mục `precode/`, `precode/source/`,
`precode/adr/`, `evidence/handoffs/` được tạo mới).

| Path | Operation | Before | After sha256 | Bytes |
| --- | --- | --- | --- | --- |
| `precode/baseline.json` | CREATE | ABSENT | `0eb98c6c5f87e770faaec6f73102c35ff4cb006080a6a5f01e8bff64c2325684` | 75160 |
| `precode/source/spec-v0.2.md` | CREATE | ABSENT | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `precode/source/pre-code-plan-v0.1.md` | CREATE | ABSENT | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |
| `precode/requirements.csv` | CREATE | ABSENT | `e98764972845bd9fc19608ba2e2428e1ed33d37145000e77129570865fb7a0a5` | 67964 |
| `precode/decision-register.md` | CREATE | ABSENT | `9f212849d6da284bf288353720a7e93bd5898610c7e66b07ac7240f359796480` | 61394 |
| `precode/adr/README.md` | CREATE | ABSENT | `020a59b26417f8df0857868d17bc052be7dde136ec7b1412a3c57e67d6ffa9f7` | 4317 |
| `precode/adr/ADR-0001-topology-and-placement.md` | CREATE | ABSENT | `b1c5a51614e33f5baab225523ce751c2befd7dbda1cd17b5e6ea16948bd540fa` | 5634 |
| `precode/adr/ADR-0002-run-state-model-split.md` | CREATE | ABSENT | `7c24b080d2162f517d1ab326df725e7985e8f569ae4a20dbbd9734130447b195` | 4842 |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | CREATE | ABSENT | `4129d7af7bbe57e0552d92b68fd5f53f5c5fef725504578e03ff3275f41b178e` | 5034 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | CREATE | ABSENT | `2083a50b50727ad35863279f12e2b27ae078be409d41d3ab0e9ee6110ca77d80` | 5368 |
| `precode/adr/ADR-0005-backup-method.md` | CREATE | ABSENT | `f405273f95eb8aace2288aacc5c9507cff684c53149a9be91b837b91349b5b45` | 4942 |
| `precode/adr/ADR-0006-stack-option-a.md` | CREATE | ABSENT | `50423d0420fbf6de91714ed9d02ec756ade4ab3b489f2ea1a5853cb84471fa47` | 4372 |
| `precode/adr/ADR-0007-timezone-handling.md` | CREATE | ABSENT | `f09235d9b1d4eca111cf87801e74c88a8badd453f4a9ec85ec14b97ee4dce680` | 4766 |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | CREATE | ABSENT | `5e2cfc13715a6135125c808963e93674f28b6919c822d4eacbb68f7ea198573e` | 5151 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | CREATE | ABSENT | `b2eeecb99f38fe76c171f02c8f963e06ca85083c4b1d4b005190a4e24761c271` | 5619 |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | CREATE | ABSENT | `ea5221a74fc6186991af67c5684ec5e1b5d81d5c84c12fb2b49d5b163fce34f0` | 5888 |
| `precode/owner-decision-request.md` | CREATE | ABSENT | `b0128efbc97b7f2ca325263b89036759584d1b34d6b7eba82de4ea30589ffb0e` | 37004 |
| `evidence/handoffs/PC00-handoff.md` | CREATE | ABSENT | *(file này — Coordinator rehash độc lập)* | — |

Tổng: **17 file nội dung** cộng handoff này. Không path nào ngoài write target của packet bị chạm.

**Danh sách đầy đủ `precode/adr/`** (directory-scoped grant): `README.md`, `ADR-0001-topology-and-placement.md`,
`ADR-0002-run-state-model-split.md`, `ADR-0003-delivery-unknown-state.md`, `ADR-0004-tag-freeze-point.md`,
`ADR-0005-backup-method.md`, `ADR-0006-stack-option-a.md`, `ADR-0007-timezone-handling.md`,
`ADR-0008-analysis-key-and-generation.md`, `ADR-0009-identity-alias-target-union.md`,
`ADR-0010-secret-scoping-and-cli-isolation.md` — 11 file, không có file nào khác.

### Hiệu ứng phụ (side effects)

- Thư mục được tạo: `precode/`, `precode/source/`, `precode/adr/`, `evidence/`, `evidence/handoffs/`.
- Không có `__pycache__` hay `.pyc`: mọi helper chạy với `PYTHONDONTWRITEBYTECODE=1` từ scratch dir
  `/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w1/`. Đã kiểm bằng
  `find . -name '__pycache__' -o -name '*.pyc'` (loại trừ `.git`) → kết quả rỗng.
- Không có lệnh git nào làm thay đổi repo được chạy. Chỉ `git status --porcelain` (chỉ đọc).
- Không network, không secret, không product code.
- Helper script nằm ngoài repo (scratch dir), không nằm trong write target và không được kê là artifact.

## 3. Source baseline đã dựa vào

Kiểm `sha256sum` **hai lần**: trước khi bắt đầu (2026-09-06T16:53Z) và trước handoff (2026-09-06T17:25Z).
Cả hai lần đều khớp giá trị pin trong baseline §2. Không có `STALE_BASELINE`.

| Ref | Path | sha256 | Bytes |
| --- | --- | --- | --- |
| SRC-SPEC | `/mnt/virtual/repo/xcrawl/research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| SRC-PLAN | `/mnt/virtual/repo/xcrawl/research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

Read-only dependency khác (không sửa): `agent_profile/worker.md`, `agent_profile/protocol.md`,
`agent_profile/registry.json`, và hai file packet trong scratch dir. `project-overview.md` và
`master-interview-prompt.md` **không** được dùng (SRC-PLAN §1 cấm dùng overview cũ để đảo quyết định mới).

## 4. Evidence records

Runtime: Linux 7.0.0-30-generic, `python3` (thư viện chuẩn: `csv`, `json`, `hashlib`, `re`, `glob`),
`sha256sum` (coreutils), `cmp`. Mọi record dưới đây là **`SELF_VALIDATION`** do chính principal viết file
thực hiện. **Không có `INDEPENDENT_AUDIT`.** Không có E1–E4.

### EV-PC00-01 — Bản sao nguồn bất biến

- **type:** SELF_VALIDATION · **producer:** `worker-W1`
- **command:** `sha256sum research-radar-spec.md research-radar-pre-code-plan.md precode/source/spec-v0.2.md precode/source/pre-code-plan-v0.1.md` và `cmp research-radar-spec.md precode/source/spec-v0.2.md` (tương tự cho plan); lặp lại trong `validate.py` mục EV-PC00-01.
- **started/ended (UTC):** 2026-09-06T16:55Z / 2026-09-06T16:55Z; chạy lại 17:24Z.
- **input hashes:** như §3.
- **oracle:** sha256 của bản sao **bằng** sha256 của nguồn; byte count 41770 và 64915; `cmp` exit 0.
- **expected/observed:** khớp hoàn toàn; `cmp` không in khác biệt.
- **exit code:** 0 · **status:** `PASS`
- **limitations:** chứng minh bản sao giống nguồn tại thời điểm chạy; **không** chứng minh nguồn là bản người dùng đính kèm — provenance đó đến từ hash pin trong `agent_profile/registry.json` và baseline §2.

### EV-PC00-02 — Cấu trúc `requirements.csv`

- **type:** SELF_VALIDATION · **command:** `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` (mục EV-PC00-02), chạy từ scratch dir.
- **started/ended (UTC):** 2026-09-06T17:20Z / 2026-09-06T17:24Z (lần chạy cuối).
- **input:** `precode/requirements.csv` (sha256 `e9876497…`, 67964 bytes), `precode/baseline.json` (sha256 `0eb98c6c…`).
- **oracle:** (1) header đúng 10 cột theo packet; (2) mọi dòng đúng 10 ô; (3) `req_id` duy nhất; (4) số dòng trong khoảng 150–250; (5) mọi `blocked_by` ∈ B01..B17; (6) mọi `impacted_packages` ∈ PC00..PC10 và không rỗng; (7) mọi `status` ∈ {XN, UQ, ĐX, KC}; (8) không ô nào chứa newline; (9) mọi `source_anchor` (bỏ hậu tố `#row-nn`) tồn tại trong bảng anchor của `baseline.json`.
- **observed:** **246 dòng**, 0 vi phạm ở cả 9 kiểm tra.
- **exit code:** 0 · **status:** `PASS`
- **limitations:** kiểm cấu trúc và enum, **không** kiểm nội dung `text_vi` có trung thực với nguồn hay không — việc đó cần đọc đối chiếu của người/Auditor.

### EV-PC00-03 — Độ phủ so với nguồn

- **type:** SELF_VALIDATION · **command:** như EV-PC00-02, mục EV-PC00-03. Danh sách kỳ vọng được **trích tự động từ `research-radar-spec.md`** (regex trên hàng bảng), không gõ tay.
- **oracle:** mọi D-ID trong SRC-SPEC §3 (kể cả hàng `C03/D-tag`), AC-01..18, P0-01..12, P1-01..05, OOS-01..06, A1..A7, OQ01..10 đều xuất hiện như một `req_id`; và mỗi mục văn xuôi bắt buộc (§1.4, §4, §5.1–5.5, §6.1–6.4, §7.3, §8.1–8.3, §9.1–9.3, §10.1–10.4, §11.1–11.4, §13, §13.2) có ít nhất một dòng.
- **observed:** spec có đúng 59 hàng decision log; 0 mục thiếu ở mọi nhóm; 0 mục văn xuôi thiếu.
- **exit code:** 0 · **status:** `PASS`
- **limitations:** kiểm "có mặt", **không** kiểm "đủ nguyên tử" — một hàng nguồn có thể còn tách nhỏ hơn được. Số dòng 246 nằm sát trần 250 của packet; nếu Auditor thấy có dòng thừa hoặc thiếu, đó là finding hợp lệ.

### EV-PC00-04 — Sổ quyết định và bản yêu cầu Owner

- **type:** SELF_VALIDATION · **command:** như trên, mục EV-PC00-04.
- **oracle:** (1) `decision-register.md` có đúng B01..B17, mỗi cái một mục, đúng thứ tự; (2) bảng tổng hợp ghi cả 17 ở `PROVISIONAL`; (3) không dùng `CLOSED`/`ACCEPTED` làm giá trị trạng thái (regex loại trừ câu cấm ở §0 và nhãn `ACCEPTED_RISK` theo `protocol.md` §8); (4) mọi `AMD-B..` được nhắc đều có mục định nghĩa; (5) sáu amendment packet yêu cầu (AMD-B01/02/03/05/10/11) tồn tại; (6) có mục §4 (P0 còn ĐX), §5 (câu hỏi mở), §6 (phát hiện mới); (7) `owner-decision-request.md` có đúng một mục cho mỗi B01..B17 cộng Stack, Timezone, OQ defaults; (8) tự khai `grants_authority: false`; (9) tám trường bắt buộc mỗi mục xuất hiện ≥ 17 lần.
- **observed:** 17/17 blocker; **14 amendment** được định nghĩa (AMD-B01, B02, B03, B04, B05, B07, B08, B09, B10, B11, B12, B15, B16, B17); 0 AMD bị nhắc mà không định nghĩa; 20 mục trong owner-decision-request; tất cả trường ≥ 19 lần.
- **exit code:** 0 · **status:** `PASS`
- **limitations:** kiểm cấu trúc và tính đầy đủ, **không** kiểm chất lượng lập luận hay tính đúng của trích dẫn nguồn.

### EV-PC00-05 — Hình dạng ADR

- **type:** SELF_VALIDATION · **command:** như trên, mục EV-PC00-05.
- **oracle:** đúng 10 file `ADR-*.md`; mỗi file có đủ 6 mục (`Bối cảnh`, `Quyết định`, `Trạng thái`, `Hệ quả`, `Phương án đã cân nhắc`, `Nguồn và truy vết`); front-matter có `adr_id`, `title`, `status`, `decision_owner`, `source_refs`, `requirement_refs`, `consumers`, `claim_ceiling`; `status` ∈ {`proposed`, `provisional-accepted`}; mỗi file được liệt kê trong `README.md`; `adr_id` chạy liên tục ADR-0001..ADR-0010.
- **observed:** 10/10 đạt mọi kiểm tra; 9 file `proposed`, 1 file `provisional-accepted` (ADR-0008).
- **exit code:** 0 · **status:** `PASS`
- **limitations:** kiểm hình dạng, không kiểm chất lượng quyết định.

### Những gì KHÔNG chạy

| Hạng mục | Kết quả | Lý do |
| --- | --- | --- |
| Audit độc lập của PC00 | `NOT_RUN` | `audit_route: INDEPENDENT_REQUIRED`; Auditor A1 audit sau freeze. Worker không được tự audit candidate của mình. |
| E1 contract tests | `NOT_RUN` | PC00 không tạo contract/schema |
| E2 integration / fault injection | `NOT_RUN` | Chưa có code |
| E3 live probe (X, AI, Telegram) | `NOT_RUN` | Cấm network trong phiên; probe A1 thuộc cổng SP1 |
| E4 review nội dung nhiều kỳ | `NOT_RUN` | Chưa có dữ liệu |
| Đối chiếu từng dòng `text_vi` với nguồn bởi người | `NOT_RUN` | Thuộc phạm vi Auditor |

## 5. Checklist của packet

| # | Hạng mục | Trạng thái | Nằm ở đâu |
| --- | --- | --- | --- |
| 1 | Baseline + bản sao bất biến + hash + source anchor cho từng §/D/AC/A/OQ (spec) và §/B/I/error/SC/gate (plan) | **DONE** | `precode/baseline.json` khóa `source_anchors` — 57 mục spec + 44 mục plan, 59 decision, 18 AC, 7 assumption, 12 P0, 5 P1, 6 OOS, 10 OQ, 17 blocker, 15 invariant, 16 error code, 19 scenario, 9 gate. Bản sao ở `precode/source/`. |
| 2 | Registry nguyên tử, một dòng một yêu cầu, đủ nhóm bắt buộc | **DONE** | `precode/requirements.csv`, 246 dòng. Phủ 59 D-row (gồm `REQ-CTAG`), AC-01..18, P0-01..12, P1-01..05, OOS-01..06, A1..A7, OQ01..10 và 129 dòng văn xuôi từ §1.4, §4, §5, §6.1–6.4, §7.3, §8, §9, §10, §11, §13, §13.2. Status giữ đúng như spec; dòng văn xuôi có suy diễn trạng thái kèm lý do ở cột `notes`. |
| 3 | Blocker register B01–B17: trích mâu thuẫn hai phía, khuyến nghị, `PROVISIONAL`, decision_owner `Owner`, contract bị ảnh hưởng, gate bị chặn, thay đổi oracle, phần còn bị chặn nếu Owner bác bỏ | **DONE** | `precode/decision-register.md` §1 (bảng tổng hợp) và §2 (17 mục chi tiết, mỗi mục đủ 8 trường) |
| 4 | Amendment với before/after và thay đổi oracle | **DONE** | `precode/decision-register.md` §3 — **14 amendment**: 6 cái packet yêu cầu (AMD-B01, B02, B03, B05, B10, B11) cộng 8 cái phát sinh (AMD-B04 coverage kỳ rỗng, AMD-B07 làm rõ D25, AMD-B08 timezone, AMD-B09 ngoại lệ linking, AMD-B12 xóa cạnh §6.2 COL→AW, AMD-B15 phạm vi chỉ số 0 trùng, AMD-B16 ba loại phát biểu, AMD-B17 phạm vi summary). B06/B13/B14 ghi rõ **không** cần sửa câu chữ. AMD-B02 kèm bảng ánh xạ 13 dòng enum cũ → mới. |
| 5 | 10 ADR theo hình dạng chuẩn | **DONE** | `precode/adr/ADR-0001..0010` đúng chủ đề packet chỉ định. 9 `proposed`; ADR-0008 (analysis key) là `provisional-accepted` vì thuần kỹ thuật và không đảo hành vi nào người dùng đã chọn — lý do ghi trong mục "Trạng thái" của chính file. |
| 6 | Liệt kê tường minh các mục P0 còn ĐX + tuyên bố "không promote" | **DONE** | `precode/decision-register.md` §4 — bảng 18 dòng gồm D09 và D53 mà packet nêu đích danh, cộng D08, D42, D50, D11, D22, D33, D21, D26, D37, D38, D43, D44, D15, D16, D12, D18. Có câu tuyên bố không promote. |
| 7 | OWNER_DECISION_REQUEST một mục cho mỗi quyết định, 8 trường, đánh dấu là REQUEST | **DONE** | `precode/owner-decision-request.md` — 20 mục (B01–B17, Stack, Timezone, OQ defaults), mỗi mục đủ 8 trường, cộng bảng hai phát hiện tự quyết và một phiếu trả lời gợi ý. Header ghi `grants_authority: false` và có câu "Đây là một REQUEST, không phải một grant". |

## 6. Unresolved refs, change request và sai lệch

### 6.1 Hai quyết định sản phẩm PC00 phải tự chọn (ngoài baseline §5)

Cả hai theo đúng stop gate của baseline §6 ("chọn khuyến nghị của kế hoạch nếu có, gắn nhãn PROVISIONAL,
ghi vào unresolved refs"). Cả hai đã được đưa vào `owner-decision-request.md`.

| ID | Mâu thuẫn | Lựa chọn PROVISIONAL | Căn cứ |
| --- | --- | --- | --- |
| `F-PC00-01` | SRC-SPEC D36 và §11.3 nói **đúng 3 lệnh** Telegram, nhưng D37 yêu cầu "có lệnh hủy liên kết" — tức lệnh thứ tư | Hủy liên kết là hành động **trong app**; Telegram giữ đúng 3 lệnh | SRC-PLAN §3 hàng B10: "không tự thêm lệnh Telegram thứ tư" |
| `F-PC00-02` | SRC-SPEC §4 liệt kê hành động **export** cho màn hình Saved, trong khi REQ-OQ10 vẫn hỏi có cần export ở MVP không | Hoãn export sang P1; MVP không có nút export | Baseline §5 hàng "OQ defaults": "Saved export deferred to P1 (PROVISIONAL)" |

### 6.2 Giá trị PROVISIONAL do PC00 ghi nhận (đều từ baseline §5, không phải tự nghĩ)

`Asia/Ho_Chi_Minh` (timezone), N = 7 ngày (backfill), 200 post hoặc 30 phút (giới hạn đợt), 08:00 và 20:00
(lịch), không có giờ yên lặng, hoãn export Saved, Stack Option A. Mỗi giá trị có một dòng lý do trong
`decision-register.md` §5. **REQ-OQ03 (provider và model cụ thể) không có mặc định** và được giữ ở
`OWNER_DECISION_REQUIRED`.

### 6.3 Sai lệch định dạng có chủ đích

`precode/requirements.csv` **không** mang YAML front-matter theo baseline §3 ("Contract file header"), vì packet
quy định header row phải là **đúng 10 cột đã cho** và thêm bất cứ dòng nào khác sẽ làm CSV không parse đúng.
Các trường bắt buộc theo SRC-PLAN §5 được ghi thay thế trong `precode/baseline.json` khóa
`requirements_csv_contract_header` (contract_id `CT-precode-requirements`, version, status, owner_role,
source_refs, decision_refs, invariant_refs, producers, consumers, dependencies, scope, verification,
claim_ceiling, cộng đặc tả cột, dấu phân tách danh sách và encoding). Nếu Coordinator muốn khác, cần packet sửa.

### 6.4 Change request tới gói khác

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-01` | Coordinator → PC01, PC02 | Quan sát lúc 17:25Z: `contracts/` (9 file), `acceptance/fixtures/identity/` (15 file) và `evidence/handoffs/PC01-handoff.md`, `PC02-handoff.md` đã tồn tại. Handoff của PC01 tự ghi rằng nó **không** đọc/ghi `precode/` và lo ngại "nếu PC00 đánh số ADR khác cho quyết định topology" thì cần packet sửa. PC00 nay đã cố định: **ADR-0001** = topology/placement (B12), **ADR-0009** = identity/alias/target (B06/B15), **ADR-0008** = analysis key (B07), **ADR-0010** = secret/CLI (B13). Đề nghị Coordinator phát packet đối chiếu `requirement_refs`/`decision_refs` của PC01 và PC02 với `precode/requirements.csv` và `precode/adr/`, vì hai gói đó soạn khi registry chưa tồn tại. PC00 **không** đọc nội dung `contracts/` và **không** sửa file nào của chúng. |
| `CR-PC00-02` | Coordinator → PC09 | `precode/decision-register.md` §6 ghi 6 phát hiện `F-PC00-01..06`; bốn cái sau đã nằm trong B01–B17, hai cái đầu thì không. PC09 cần đưa `F-PC00-01` và `F-PC00-02` vào `precode/review.md` và `precode/gates.yaml` như hai mục còn mở của G0, nếu không chúng sẽ rơi khỏi tầm nhìn. |
| `CR-PC00-03` | Coordinator → PC03, PC04 | AMD-B02 định nghĩa 13 dòng ánh xạ enum cũ → mới; AMD-B08 chốt timestamp UTC RFC 3339 **mili giây** cộng ingest sequence. Hai giá trị này là đầu vào bắt buộc của `contracts/state/run.yaml` và `contracts/reporting/time-and-tags.md`; nếu PC03/PC04 đã chọn giá trị khác thì phải hòa giải trước G2. |

### 6.5 Ràng buộc còn mở mà gói sau phải tôn trọng

- B01–B17 vẫn `OPEN` trong `agent_profile/registry.json`. PC00 **không** sửa registry đó (ngoài write target).
- Không mục P0 nào được promote; D09 và D53 vẫn `ĐX` trong một hạng mục P0.
- Mọi tham số của khối "hướng đang nổi" (B14) là PROVISIONAL cho tới khi có 3–4 kỳ dữ liệu thật (A4).
- REQ-AC16 (chạy không cần API key) chỉ pass khi có ít nhất một adapter CLI qua kiểm cô lập; nếu không thì
  ghi `BLOCKED`, **không** phải `FAIL` (ADR-0010).
- Product status giữ nguyên `NOT_READY_FOR_PRODUCT_CODE`.

## 7. Trạng thái bàn giao

- **next actor:** `Coordinator`.
- **Việc Coordinator cần làm:** rehash độc lập 17 file ở §2 trước khi phát `FROZEN_CANDIDATE`; xử lý
  `CR-PC00-01..03`; chuyển `precode/owner-decision-request.md` lên Owner.
- **lease_released_at (UTC):** 2026-09-06T17:27Z. Sau thời điểm này `worker-W1` **không ghi thêm bất kỳ file nào**,
  kể cả sửa lỗi đánh máy. Mọi sửa đổi tiếp theo cần packet mới, baseline mới (hash ở §2) và lease mới với
  fencing cao hơn.
- **Freeze:** PC00 **không** tự chứng nhận freeze. Việc phát hành `FROZEN_CANDIDATE` thuộc Coordinator.

---

# ADDENDUM — PKT-PC00-FIX1 (remediation cho AUDIT_REPORT PKT-A1-R1)

## A1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX1` |
| worker principal | `worker-W1` |
| authority_id | `AUTH-COORD-PC00-FIX1` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC00-e2` (exclusive, **fencing 2** — thay `LEASE-PC00-e1` đã released ở epoch 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at (UTC) | 2026-09-06T17:52Z |
| finished_at (UTC) | 2026-09-06T17:59Z |
| lease expires_at (UTC) | 2026-09-07T04:00Z — `date -u` trước lần ghi cuối: 2026-09-06T17:57Z, còn hiệu lực |
| next actor | `Coordinator` |
| lease_released_at (UTC) | 2026-09-06T17:59Z |
| audit input | `…/scratchpad/audits/A1-R1-report.md` §5 (9 finding) + `…/scratchpad/packets/FIX-A1R1-rulings.md` (R-01..R-09) |
| scope của packet này | **`F-A1R1-05`, `F-A1R1-06`, `F-A1R1-08`, `F-A1R1-09`** cộng phần PC00 của **R-04**. `F-A1R1-01/02/03/04/07` thuộc PC01/PC02 và **không** được chạm. |

**Không finding nào được đóng ở đây.** Cả 9 finding vẫn `OPEN` → `FIX_PROPOSED`. Theo `protocol.md` §8, chuyển sang `VERIFIED`/`CLOSED` cần A1 kiểm lại trên **epoch mới** (FC-W1 epoch 2), và người kiểm không được là principal đã viết bản sửa — tức không phải `worker-W1`.

## A2. Từng finding: đã đổi gì

### F-A1R1-05 (MINOR) — ADR thiếu 8 trường header của baseline §3 → **ngoại lệ được khai báo**

Ruling R-05: ADR là *decision record*, không phải hợp đồng, nên được miễn header baseline §3; front-matter bắt buộc là đúng mười trường `adr_id, title, status, date, decision_owner, source_refs, requirement_refs, decision_refs, affected_packages, supersedes`.

- **Đã thêm vào cả 10 ADR** ba trường còn thiếu: `decision_refs` (hợp của `blocker_refs` và `amendment_refs`), `affected_packages` (trùng `consumers`), `supersedes: []`. Bảy trường còn lại đã có sẵn từ epoch 1.
- ADR-0006 (stack) có `decision_refs: []` vì không gắn B/AMD nào; kèm comment YAML chỉ về `REQ-OQ02` và baseline §5 hàng "Stack" để trống không bị đọc nhầm là bỏ sót.
- Giữ nguyên `blocker_refs`, `amendment_refs`, `invariant_refs`, `consumers`, `claim_ceiling` — thừa so với R-05 nhưng có ích cho truy vết và đã được PC01/PC02 tham chiếu.
- **Ngoại lệ được khai báo tường minh** ở đầu `precode/adr/README.md`, mục "Ngoại lệ header đã được khai báo (ruling R-05)": lý do miễn, danh sách mười trường, quan hệ `decision_refs`↔`blocker_refs`+`amendment_refs` và `affected_packages`↔`consumers`, cùng con trỏ tới addendum này. Mẫu ADR trong README cũng đã cập nhật.
- **Đáp ứng remediation constraint:** audit yêu cầu "deviation phải xuất hiện trong handoff/decision record như một declared exception, không để ngầm". Nay có ở ba nơi: baseline §3 (Coordinator sửa), `precode/adr/README.md`, và mục này.

### F-A1R1-06 (MINOR) — `requirements_csv_contract_header` thiếu `requirement_refs`

- Đã thêm `requirement_refs` vào `precode/baseline.json.requirements_csv_contract_header`: liệt kê theo họ ID (`REQ-D01..REQ-D59` với ghi chú D03 không tồn tại, `REQ-CTAG`, `REQ-AC01..18`, `REQ-P0-01..12`, `REQ-P1-01..05`, `REQ-OOS-01..06`, `REQ-A1..A7`, `REQ-OQ01..10`, và `REQ-S<section>-<nn>` cho 28 mục văn xuôi).
- Thêm `requirement_refs_note_vi` giải thích vì sao trường này tự quy chiếu: file **là** registry yêu cầu, nên tập ID đầy đủ chính là cột `req_id` của 246 dòng.
- Object nay có đủ **14/14** trường tối thiểu của baseline §3; đã đưa vào EV-PC00-06 như một kiểm tra tự động thay vì kiểm bằng mắt.
- **Đính chính tuyên bố ở §6.3 của bản handoff gốc.** §6.3 viết rằng object thay thế mang "các trường bắt buộc theo SRC-PLAN §5" và liệt kê chúng; danh sách đó **thiếu `requirement_refs`**, nên câu đó **đã nói quá** đúng như audit ghi nhận. §6.3 giữ nguyên (handoff epoch 1 là bản ghi lịch sử, chỉ append). Tuyên bố đúng tính từ epoch 2 là: object chứa đủ 14 trường tối thiểu, gồm `requirement_refs`, và điều đó được EV-PC00-06 kiểm chứ không phải được khẳng định.

### F-A1R1-08 (MINOR) — SC19–SC28 gộp thành một anchor

- Thay anchor gộp `SRC-PLAN:SC19-SC28` bằng **mười anchor riêng** `SRC-PLAN:SC19` … `SRC-PLAN:SC28`, mỗi cái có `line: 505` (câu "Bổ sung tối thiểu SC19–SC28…" của SRC-PLAN §13), `list_position` 1–10 và `subject_vi` lấy đúng thứ tự trong câu nguồn: SC19 tag đổi sau publish trước delivery · SC20 stale lease · SC21 ingest ACK mất · SC22 late analysis/backfill crash · SC23 identity conflict · SC24 embedding generation switch · SC25 Telegram relink · SC26 disk full · SC27 restore với outbox cũ · SC28 worker chết sau AI call.
- Thêm anchor nhóm `SRC-PLAN:§13-extra` và **bốn anchor** cho scenario phát sinh ngoài văn bản §13: `SC29` post-only target, `SC30` arXiv phiên bản mới, `SC31` ingest-batch schema rejection, `SC32` delete-target. Mỗi cái mang `anchor_scope: SRC-PLAN:§13-extra`, `origin_package` và `maps_to_req`; `line: null` vì chúng **không** có trong nguồn — ghi rõ để không ai tưởng chúng là trích dẫn.
- Tổng anchor scenario: 19 → **33** (SC01–18 + SC19–28 + nhóm + SC29–32).
- **Hệ quả cho PC09:** mười citation SC19–SC28 đang có trong `contracts/ports.yaml` nay kiểm được theo ID. Thứ tự đúng được EV-PC00-06 kiểm bằng đối chiếu từ khóa chủ đề, không phải bằng đọc.

### F-A1R1-09 (MINOR) — `REQ-S4-05` không dẫn về quyết định hoãn export

- `notes` của `REQ-S4-05` nay mang cảnh báo phạm vi tường minh: hành động `export` trong hàng IA **không** thuộc MVP; dẫn `F-PC00-02`, `REQ-OQ10`, trạng thái PROVISIONAL với `decision_owner: Owner`, và `save.export lifecycle_status: deferred_p1` của `contracts/ports.yaml`; kèm điều kiện đảo ("nếu Owner giữ export ở MVP thì hàng này và `save.export` phải đổi cùng lúc"). Registry, ports contract và Owner request nay nói cùng một điều.
- `REQ-D37`: audit ghi nhận cross-reference đã có về **nội dung** nhưng chuỗi `F-PC00-01` không xuất hiện, nên grep theo ID không tìm ra. Đã thêm tên finding, tên operation `telegram.unlink` (chỉ gọi được từ `MOD-web-ui`) và con trỏ tới `AMD-B10` cùng mục B10 của Owner request.
- Trạng thái `UQ` của `REQ-S4-05` và `ĐX` của `REQ-D37` **giữ nguyên**: chỉ `notes` đổi, không đụng cột `status` (fidelity trạng thái là điều audit đã PASS).

### R-04 (từ F-A1R1-04, MAJOR — phần thuộc PC00)

`F-A1R1-04` là finding của PC01 (thiếu operation trong `ports.yaml`); phần PC00 phải làm là ghi lại quyết định và đưa phần chưa giải được lên Owner.

- **`precode/decision-register.md` §8 mới** — "Quyết định tạm thời phát sinh sau audit A1-R1", mở đầu bằng `PROV-PC00-01`: ba thao tác xóa của `REQ-S7.3-05` và phạm vi loại trừ của `data.purge_all`. Mục này theo đúng khuôn của §2: nguồn yêu cầu, điều audit phát hiện, ruling, quyết định PROVISIONAL, phần vẫn chặn, file bị ảnh hưởng, gate, thay đổi oracle, "nếu Owner bác bỏ", liên kết.
  - Thay đổi oracle đáng chú ý: `REQ-S7.3-05` chuyển từ "có ba thao tác riêng" (kiểm bằng đọc) sang kiểm tra truy vết requirement→operation, cộng hai oracle âm — sau `data.delete_target`, số hàng `saved_snapshot` của target **không đổi** (D55) và `first_announced` **không** bị reset (I07).
  - Phạm vi loại trừ của `data.purge_all` giữ **`OWNER_DECISION_REQUIRED`**, không gán giá trị PROVISIONAL.
- **`precode/owner-decision-request.md`** — thêm mục "Phạm vi của `data.purge_all`" với đủ tám trường, ba phương án (chỉ dữ liệu nghiên cứu / tất cả trừ tài khoản / tất cả) kèm đánh đổi, và **cố ý không đưa khuyến nghị**: cả ba đều làm mất một thứ đặc tả không cho phép suy ra, và phương án (c) còn đòi một cơ chế bootstrap mà D05 (không signup, không quên-mật-khẩu tự động) chưa có. Bảng "Cách đọc" thêm mức thứ tư **"Không có mặc định"**; phiếu trả lời thêm một dòng; `scope` ở front-matter sửa 20 → 21 mục.
- **`REQ-S7.3-05`** `notes` nay trỏ tới cả ba operation, ghi rõ `save.remove.requirement_refs` phải trỏ về chính nó, và dẫn `SC32` cùng `PROV-PC00-01`.
- PC00 **không** định nghĩa operation nào: `contracts/ports.yaml` ngoài write target.

## A3. Changes (MODIFY / APPEND)

Mọi baseline "before" dưới đây khớp đúng bảng §2 của handoff epoch 1 — đã kiểm lại bằng `sha256sum` ngay trước khi sửa; không file nào bị agent khác chạm giữa hai epoch.

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `0eb98c6c…2325684` (75160) | `ccd3972b01aad4897d97950f6600c2a20228e2b9d0b9be2ae784ade8f330d6df` (80485) |
| `precode/requirements.csv` | MODIFY | `e9876497…5fb7a0a5` (67964) | `1bf60a1c54721adeedc7bc13b0313fd409d064bb3d3f44283b24885f584b9dbb` (68969) |
| `precode/decision-register.md` | MODIFY | `9f212849…59796480` (61394) | `0a64b05095a44ded2ab94ff405881ffe09e26d1277928503d49b1643d101f4c6` (66108) |
| `precode/owner-decision-request.md` | MODIFY | `b0128efb…589ffb0e` (37004) | `da03f3fdc337916d4a3e69ac79a3392bb3773dd902fd85c0be8ba60ecb6dd512` (41284) |
| `precode/adr/README.md` | MODIFY | `020a59b2…7d6ffa9f7` (4317) | `44b9d01b60984ecedb715cfb3c82fdcb7f09e78aa13646e581a750686a0c269d` (6490) |
| `precode/adr/ADR-0001-topology-and-placement.md` | MODIFY | `b1c5a516…48bd540fa` (5634) | `277eb556cff950193ca55cecd0ef0d06dca279a4d376c5c8e889a48ebf60c09c` (5717) |
| `precode/adr/ADR-0002-run-state-model-split.md` | MODIFY | `7c24b080…30447b195` (4842) | `5ed7b2c429ef7e060140f8b6bbaa71b761b482134aaac155ad32d64bef34b8c0` (4924) |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | MODIFY | `4129d7af…3b3f4d29e` (5034) | `1cb86d8db85c4350dc1eaf6b0822908030219d326c65a8fbec321066d2aab2a0` (5105) |
| `precode/adr/ADR-0004-tag-freeze-point.md` | MODIFY | `2083a50b…0ca77d80` (5368) | `64c0793eeca31b6ac0606813adac96fa483e01eb4b81eaef950edfff16fd3194` (5459) |
| `precode/adr/ADR-0005-backup-method.md` | MODIFY | `f405273f…1349b5b45` (4942) | `7830500f824c84683d81f2458d7280483d105c4a221f738b083c6fcb7fcbeead` (5013) |
| `precode/adr/ADR-0006-stack-option-a.md` | MODIFY | `50423d04…4471fa47` (4372) | `a7b0b558a308f699018f1b695cb4585e3cc3ab6bcb86cf298a05fde6ace6b20b` (4516) |
| `precode/adr/ADR-0007-timezone-handling.md` | MODIFY | `f09235d9…7ee4dce680` (4766) | `334abf600467fba70e7797113956c99406acb3617b2da6f3ccce56f8f5786ed7` (4843) |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | MODIFY | `5e2cfc13…7fea198573e` (5151) | `c08f8670b19e8a0758062988570701ccb96f6d4beefac7b4d80ed6906b95c5f1` (5228) |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | MODIFY | `b2eeecb9…e24761c271` (5619) | `a8e57390663d6dc3778ff8036ca4032a91da25f0b85844bd094f393e34f6b5ef` (5701) |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | MODIFY | `ea5221a7…5b163fce34f0` (5888) | `734766c889edbbb0dce94dca92b7da04a9c0b6721536addaeaac3ee6c783a291` (5962) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `8704a56f67a8d94c51777fa43da8c25f71f3421c8cb4c5cc0e3dbe4198fabbe3` (21313) | *(file này — Coordinator rehash độc lập)* |

**15 file MODIFY + 1 APPEND.** Không path nào khác bị chạm.

- `precode/source/spec-v0.2.md` và `precode/source/pre-code-plan-v0.1.md`: **không sửa**, đúng lệnh packet. Đã rehash sau khi xong: vẫn `d35e1f2d…` / `f65bb046…`, khớp nguồn.
- Không chạm `contracts/`, `acceptance/`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC02-handoff.md`, `agent_profile/`.
- Không lệnh git nào làm thay đổi repo. Không `__pycache__`/`.pyc` (mọi helper chạy `PYTHONDONTWRITEBYTECODE=1` từ scratch dir). Không network, không secret.
- `precode/requirements.csv` vẫn **246 dòng**, đúng 10 cột, không dòng nào thêm/bớt: chỉ ba ô `notes` đổi (`REQ-S4-05`, `REQ-D37`, `REQ-S7.3-05`). Không ô `status` nào đổi.

## A4. Evidence — chạy lại EV-PC00-02..05 cộng EV-PC00-06 mới

Tất cả là **`SELF_VALIDATION`**, producer `worker-W1`. **Không phải audit độc lập** và không thay thế lượt kiểm lại của A1 trên epoch 2.

- **Lệnh (một lần chạy, cả năm record):** `cd /tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **Runtime:** Linux 7.0.0-30-generic; `python3` thư viện chuẩn (`csv`, `json`, `hashlib`, `re`, `glob`).
- **started/ended (UTC):** 2026-09-06T17:56Z / 2026-09-06T17:56Z.
- **Kết quả tổng:** **121 assertion, 121 PASS, 0 FAIL, exit code 0.**

| Record | Phạm vi | Thay đổi so với epoch 1 | Kết quả |
| --- | --- | --- | --- |
| `EV-PC00-01` | Bản sao nguồn byte-identical | không đổi | `PASS`, exit 0 |
| `EV-PC00-02` | Cấu trúc `requirements.csv` (9 kiểm tra) | không đổi; anchor check nay chấp nhận 33 anchor scenario | `PASS` — 246 dòng, 0 vi phạm |
| `EV-PC00-03` | Độ phủ so với nguồn | không đổi | `PASS` — 0 mục thiếu |
| `EV-PC00-04` | `decision-register` + `owner-decision-request` | không đổi | `PASS` — 17/17 blocker `PROVISIONAL`, 14 AMD, 21 mục Owner request |
| `EV-PC00-05` | Hình dạng ADR | **oracle mạnh hơn**: front-matter kiểm theo đúng 10 trường R-05 (thêm `date`, `decision_refs`, `affected_packages`, `supersedes`; bỏ kiểm `consumers`, `claim_ceiling` khỏi tập bắt buộc vì R-05 không đòi) | `PASS` — 10/10 ADR |
| `EV-PC00-06` | **Mới** — remediation A1-R1 | `F-06`: 14/14 trường header, `requirement_refs` không rỗng · `F-08`: SC19–SC32 có anchor riêng, anchor gộp cũ đã biến mất, chủ đề SC19–SC28 khớp thứ tự §13, có nhóm `§13-extra`, SC29–32 trỏ về nhóm · `F-05`: README khai báo ngoại lệ và liệt kê trường bắt buộc · `F-09`: `REQ-S4-05` dẫn `F-PC00-02`+`REQ-OQ10`+P1, `REQ-D37` dẫn `F-PC00-01` · `R-04`: `REQ-S7.3-05` dẫn cả hai operation, register có `PROV-PC00-01` với `OWNER_DECISION_REQUIRED`, Owner request có mục `data.purge_all` đủ 8 trường | `PASS` — 24/24 |

**Không chạy (giữ `NOT_RUN`):** audit độc lập epoch 2 (thuộc A1, và `worker-W1` bị cấm tự kiểm bản sửa của mình); E1–E4; đối chiếu từng dòng `text_vi` với nguồn bởi người. Oracle của `EV-PC00-06` là *sự hiện diện và tính nhất quán của tham chiếu*, không phải tính đúng ngữ nghĩa của quyết định.

## A5. Unresolved refs và change request

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `PROV-PC00-01` | Owner (qua Coordinator) | Phạm vi loại trừ của `data.purge_all` — **`OWNER_DECISION_REQUIRED`**, không có giá trị PROVISIONAL. Xem `decision-register.md` §8 và mục "Phạm vi của `data.purge_all`" trong Owner request. |
| `CR-PC00-04` | Coordinator → PC01 | PC00 đã trỏ `REQ-S7.3-05` sang `data.delete_target` / `data.purge_all` / `save.remove` và đăng ký anchor `SC32`. Nếu PC01-FIX đặt tên operation khác, đặt `SC32` cho việc khác, hoặc không sửa `save.remove.requirement_refs` thành `REQ-S7.3-05`, thì `precode/requirements.csv` và `precode/baseline.json` **lệch** và cần packet sửa PC00 tiếp. PC00 không đọc `contracts/ports.yaml` ở packet này, nên chưa xác nhận được sự khớp. |
| `CR-PC00-05` | Coordinator → PC09 | Bổ sung `EV-PC00-06` vào tập E0 mà PC09 chạy lại, và đưa các anchor `SRC-PLAN:SC19`…`SC32` vào `acceptance/traceability.csv` như ID kiểm được. `CR-PC00-02` (theo dõi `F-PC00-01`/`F-PC00-02` ở G0) vẫn còn hiệu lực và nay thêm `PROV-PC00-01`. |
| `CR-PC00-01`, `CR-PC00-03` | Coordinator | Vẫn mở, không đổi so với epoch 1. `CR-PC00-01` (đối chiếu REQ/ADR ref của PC01/PC02) nay được củng cố bởi `F-A1R1-03`. |

**Concern còn lại của PC00:** (1) `EV-PC00-06` kiểm tham chiếu **trong** phạm vi PC00; nó không thể phát hiện việc PC01/PC02 dùng ID khác — đó là lý do `CR-PC00-04` tồn tại. (2) Bốn finding MAJOR `F-A1R1-01..04` nằm ngoài scope packet này và vẫn `OPEN`; verdict `FAIL` của FC-W1 chưa được gỡ bởi bản sửa này. (3) Số dòng registry vẫn 246, sát trần 250 của packet gốc — nếu gói sau cần tách thêm dòng thì phải xin nới trần.

## A6. Trạng thái bàn giao (FIX1)

- **next actor:** `Coordinator` — rehash độc lập 15 file ở §A3, freeze **FC-W1 epoch 2**, chuyển A1 kiểm lại `F-A1R1-05/06/08/09`.
- **lease_released_at (UTC):** 2026-09-06T17:59Z. `LEASE-PC00-e2` (fencing 2) được nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §A3) và lease với fencing ≥ 3.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng. Product status vẫn `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`; cả 9 finding vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX2 (đợt FIX3: A1-R2 + CR của PC03/PC04/PC08)

## B1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX2` |
| worker principal | `worker-W1` |
| authority_id | `AUTH-COORD-PC00-FIX2` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC00-e3` (exclusive, **fencing 3**) |
| enforcement_mode | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at / finished_at (UTC) | 2026-09-06T18:29Z / 2026-09-06T18:38Z |
| lease expires_at (UTC) | 2026-09-07T06:00Z — `date -u` trước lần ghi cuối: 2026-09-06T18:36Z, còn hiệu lực |
| next actor / lease_released_at | `Coordinator` / 2026-09-06T18:38Z |
| scope | `F-A1R2-05`; anchor SC33–SC44; đăng ký quyết định PROVISIONAL và câu hỏi Owner của PC03/PC04/PC08; `CSRF_REJECTED`, `data.purge_all`, `run.resume`-từ-`blocked` |
| inputs đã đọc | `A1-R2-report.md` §5, `FIX3-rulings.md`, `evidence/handoffs/PC03-handoff.md` §6, `PC04-handoff.md` §7.3–7.5, `PC08-handoff.md` §6, `contracts/errors.yaml`, `contracts/ports.yaml` (`data.purge_all`, `run.resume`), `contracts/state/run.yaml` §11, `contracts/state/storage.yaml` |

**Không finding nào được đóng ở đây.** `F-A1R2-05` chuyển OPEN → FIX_PROPOSED; A1 xác minh ở freeze kế tiếp, và người xác minh không được là `worker-W1`.

## B2. Đính chính bản addendum trước (PKT-PC00-FIX1 §A3)

Bảng §A3 của addendum FIX1 ghi **sai** phần rút gọn của hai giá trị `before sha256`. Bản gốc **không** được sửa (chỉ append). Giá trị đúng — như đã ghi ở §2 của handoff epoch 1, và là giá trị thật của bytes epoch 1:

| File | §A3 ghi (SAI) | Giá trị đúng |
| --- | --- | --- |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | `4129d7af…3b3f4d29e` | `4129d7af7bbe57e0552d92b68fd5f53f5c5fef725504578e03ff3275f41b178e` |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | `5e2cfc13…7fea198573e` | `5e2cfc13715a6135125c808963e93674f28b6919c822d4eacbb68f7ea198573e` |

Chỉ phần **hiển thị rút gọn** sai; các giá trị `after` trong §A3 đầy đủ 64 ký tự và đúng, và bytes trên đĩa chưa bao giờ khác. Bài học đã áp cho addendum này: **mọi hash đều ghi đủ 64 ký tự**, không rút gọn.

## B3. Từng mục: đã đổi gì

### F-A1R2-05 (MINOR) — anchor lạc `SC29+`

- Gỡ hẳn entry `SRC-PLAN:§13-extra` (nhãn `SC29+`) khỏi `source_anchors.SRC-PLAN.scenarios`. Nay **mọi nhãn trong danh sách là một scenario ID thật**; đã thêm assertion regex `SC[0-9]{2}` vào `EV-PC00-06` để lớp lỗi này không quay lại.
- Việc nhóm không biến mất mà đổi cách biểu diễn: SC29–SC44 mang trường mô tả `allocation_group: "post-§13"` — một **nhãn**, không phải anchor, nên không thể bị trích dẫn nhầm như `SC29+` trước đây.
- Thêm khối `scenario_id_allocation` ở cấp cao của `baseline.json`: dải nào thuộc gói nào (SC01–18 và SC19–28 từ SRC-PLAN §13; SC29–31 PC02; SC32 PC01/R-04; SC33–36 PC03; SC37–38 PC04; SC39–43 PC08; SC44 PC01/FIX3; **SC45+ chưa cấp**, PC05/PC06/PC07 lấy từ đó và phải khai trong handoff), kèm dòng ghi rõ `SC29+` đã bị gỡ và không được trích dẫn.

### Anchor SC33–SC44

Đăng ký 12 anchor mới, mỗi cái có `subject_vi`, `origin_package`, `maps_to_req`, `registered_by_ruling`, và `line: null` — `null` **cố ý**, để không ai đọc nhầm chúng là trích dẫn từ SRC-PLAN. Chủ đề lấy **từ chính file của gói sở hữu**, không phải tôi đặt: SC33–SC36 từ `contracts/state/run.yaml` §11 và `storage.yaml`; SC37–SC38 từ `CR-PC04-06`; SC39–SC43 từ `CR-PC08-01`; SC44 từ ruling FIX3 và `ports.yaml data.purge_all`.

Tổng anchor scenario: 33 → **44** (SC01…SC44 liên tục, không khoảng trống, không nhãn lạ).

### Quyết định PROVISIONAL mới của PC00

- **`PROV-PC00-02` — `CSRF_REJECTED`.** Giải xung đột `CR-PC08-03`: `openapi.yaml` ánh xạ thiếu CSRF sang `FORBIDDEN_EDGE`, nhưng `errors.yaml` định nghĩa mã đó là "cạnh không có trong `modules.yaml`" — mà request thiếu CSRF đi qua **đúng** cạnh. Mã mới: 403, `scope: request`, `retry_class: none`, không đổi state. Kèm theo, `CR-PC08-04` được chấp nhận đúng như PC08 lập luận: collector token gọi `save.create` là **`UNAUTHORIZED` 401**, vì ba file đã đóng băng (`modules.yaml` NC-01/NC-02, oracle của `errors.yaml`, mô tả `collectorToken` trong `openapi.yaml`) đều nói vậy và văn bản packet PC08 là nguồn thứ tư lạc nhịp. `decision_owner: Coordinator (delegated)` — kỹ thuật, không đảo hành vi Owner đã chọn.
- **`PROV-PC00-03` — hình dạng hai pha của `data.purge_all` + `SC44`.** Ghi lại cách `ports.yaml` thực hiện "xác nhận gõ tay" của §7.3 **mà không** sinh operation thứ tư: một operation, hai `phase`, idempotency key là `purge_challenge_id`. Bổ sung hai hệ quả vận hành PC08 phát hiện mà Owner phải biết **trước khi** trả lời `PROV-PC00-01`: (1) nếu purge xóa credential đăng nhập thì Owner có thể tự khóa mình ra ngoài app, vì D05 cấm signup và cấm quên-mật-khẩu tự động; (2) dữ liệu đã purge **vẫn còn trong backup** cho tới khi backup bị xóa — "xóa toàn bộ" không đồng nghĩa "không còn ở đâu nữa".
- **`PROV-PC00-04` — `run.resume` mở rộng cho `blocked`.** Giải `CR-PC03-02`: hiện `blocked` chỉ thoát được bằng `run.cancel`, buộc Owner vứt tiến độ. Guard mới cho phép Owner mở chặn với `unblock_reason` **bắt buộc**. `decision_owner: Owner` vì nó chạm câu §5.4 bước 5 mà Owner đã đọc. Ranh giới được ghi rõ và **không** nới: không đường tự động, không lệnh Telegram, luôn cấp lease mới, `status`/`run-now` vẫn không đưa run rời `blocked`.

### Đăng ký quyết định của gói khác — `decision-register.md` §8.5

Bảng 20 dòng: `PROV-PC03-01..06`, `PROV-PC04-01..09`, `PROV-PC08-01..05`. PC00 **ghi nhận, không thẩm định lại**; chủ sở hữu vẫn là gói gốc. Ba dòng được đánh dấu để Owner và Auditor chú ý:

- `PROV-PC03-04` (`analysis_unknown_attempt_auto_rerun = 1`): PC03 **tự khai** rằng đây là chỗ họ diễn giải khác câu "never retry unknown outcome" trong packet của họ, và **đề nghị Auditor soi kỹ**. Tôi giữ nguyên lời tự khai đó thay vì làm mềm đi. Lập luận của họ — hậu quả xấu nhất ở AI là tốn phí, còn ở delivery là người nhận thấy tin trùng, không quan sát được và không hoàn tác được — nhất quán với `AMD-B03`, nhưng đây không phải kết luận của tôi.
- `PROV-PC04-09` (kỳ rỗng phương án (b)): PC04 **không** theo khuyến nghị (a) của Coordinator, và nêu lý do kỹ thuật cụ thể (`coverage_window` không có khóa idempotency). Đã ghi cả hai phía và cách đảo ngược nếu Coordinator/Owner vẫn muốn (a).
- `PROV-PC04-06` (ngưỡng `0.8000` mang nhãn `PROVISIONAL_BOOTSTRAP` + `uncalibrated`): kèm ràng buộc **cấm tuyên bố đạt chỉ tiêu §1.4 khi còn `uncalibrated`** — đây là điều giữ cho `REQ-D52` không bị nâng nhãn bằng suy diễn.

Cũng ghi phần **cố ý để trống, có gate**: `research_connector_rate_limit` của PC03 giữ bốn giá trị `null` với `status: PLACEHOLDER_KC` và một sàn an toàn `min_interval_ms = 3000`, vì `REQ-A6` vẫn **KC**. Đó là cách đúng: không bịa hạn mức.

### Câu hỏi Owner — `owner-decision-request.md`

Ba mục mới, mỗi mục đủ tám trường: **"Tham số báo cáo và mật độ"** (8 quyết định của PC04 dưới dạng bảng đọc được cho người không đọc hợp đồng, cộng lựa chọn (a)/(b) cho kỳ rỗng), **"Vận hành và bảo mật"** (RPO 24 h / RTO 2 h, retention backup, tham số phiên đăng nhập, vòng đời token), **"Hai thay đổi kỹ thuật cần Owner biết"** (`CSRF_REJECTED`, `run.resume` từ `blocked`). Hai mục cũ được bổ sung: **Timezone** (hệ quả: đổi múi giờ ⇒ dựng lại toàn bộ fixture lịch của PC03 và PC04; hai quy tắc DST của PC03 chưa kích hoạt vì `Asia/Ho_Chi_Minh` không có DST) và **`data.purge_all`** (hai hệ quả PC08 + hình dạng hai pha). Bảng "Cách đọc" thêm mức **"Đã có số tạm, cần xác nhận"**; phiếu trả lời thêm 6 dòng; `scope` 21 → 24 mục.

Trong ba mục mới, mục PC08 là mục duy nhất tôi đưa **khuyến nghị hẹp** ("nếu chỉ đổi một thứ thì đổi phiên đăng nhập 12 giờ") — vì đó là con số Owner va vào hằng ngày và nới nó không ảnh hưởng gói nào khác. Với PC04 tôi khuyến nghị xác nhận cả tám nhưng chỉ ra hai mục đáng để ý (#2 backfill không cấp lại, #6 ngưỡng chưa hiệu chỉnh).

### `requirements.csv` — hai cross-reference

246 dòng, 10 cột, **không dòng nào thêm/bớt, không ô `status` nào đổi**; chỉ hai ô `notes`:

- `REQ-S9.3-08`: ghi rằng `ports.yaml` trích `REQ-S8.4-01` ở `health.get_liveness`, `health.get_readiness`, `storage.get_health` nhưng **ID đó không tồn tại** (SRC-SPEC không có §8.4; §8.4 là của SRC-PLAN), và kênh health độc lập DB thuộc chính hàng này ⇒ PC01 trỏ sang `REQ-S9.3-08`. Thêm `SC36`. Đây là `CR-PC03-01`; ruling giao phần sửa `ports.yaml` cho PC01, PC00 chỉ cung cấp ID đúng.
- `REQ-S7.3-05`: thêm `PROV-PC00-03` và `SC44`.

## B4. Changes

Mọi `before` khớp đúng bảng §A3 của addendum FIX1 — đã rehash ngay trước khi sửa; không file nào bị chạm giữa hai epoch. **Hash ghi đủ 64 ký tự** (xem §B2).

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `ccd3972b01aad4897d97950f6600c2a20228e2b9d0b9be2ae784ade8f330d6df` (80485) | `61fb00b78e2a62bcf0e7fce041077e79b90e6fb670f4e679cb88f1ad2a284931` (87560) |
| `precode/decision-register.md` | MODIFY | `0a64b05095a44ded2ab94ff405881ffe09e26d1277928503d49b1643d101f4c6` (66108) | `4532045f286bb42f9fba25efa22d76664713877105797b9cd83c67a8877a8643` (79647) |
| `precode/owner-decision-request.md` | MODIFY | `da03f3fdc337916d4a3e69ac79a3392bb3773dd902fd85c0be8ba60ecb6dd512` (41284) | `32f66afa10727e7b97f7a96c965b34246a8a04d7ff2d32883f28969af3239fcd` (54351) |
| `precode/requirements.csv` | MODIFY | `1bf60a1c54721adeedc7bc13b0313fd409d064bb3d3f44283b24885f584b9dbb` (68969) | `132ce59b160d9cc20294e45f33082e27d69c4b3182bdc9c1b1864fd0adeaf0e6` (69366) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `4aa2a3d77f883475ae97d14d673162552ae1cf37ff3093718070929d5ba1748f` (39324) | *(file này — Coordinator rehash độc lập)* |

**4 MODIFY + 1 APPEND.** `precode/adr/*` **không** đổi ở đợt này (giá trị FIX1 còn nguyên). `precode/source/*` không sửa; rehash sau khi xong: `d35e1f2d…` / `f65bb046…`, khớp nguồn. Không chạm `contracts/`, `acceptance/`, handoff của gói khác, `agent_profile/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## B5. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-06T18:35Z / 2026-09-06T18:35Z · **exit code 0** · **166 assertion, 166 PASS, 0 FAIL**
- Tất cả là **`SELF_VALIDATION`**, producer `worker-W1`. Không phải audit độc lập.

| Record | Thay đổi ở đợt này | Kết quả |
| --- | --- | --- |
| `EV-PC00-01` | không đổi | `PASS` — bản sao byte-identical, nguồn khớp pin |
| `EV-PC00-02` | không đổi (anchor check nay đối chiếu 44 anchor scenario) | `PASS` — 246 dòng, 0 vi phạm |
| `EV-PC00-03` | không đổi | `PASS` — 0 mục thiếu |
| `EV-PC00-04` | không đổi | `PASS` — 17/17 blocker `PROVISIONAL`, 14 AMD, 24 mục Owner request |
| `EV-PC00-05` | không đổi | `PASS` — 10/10 ADR theo bộ 10 trường R-05 |
| `EV-PC00-06` | **oracle mạnh hơn**: khẳng định `§13-extra` **đã biến mất**; mọi nhãn khớp `SC\d\d`; SC19–SC44 có anchor riêng; đúng 44 anchor; `origin_package` khớp dải đã cấp; có bảng `scenario_id_allocation` với `SC45+` để trống | `PASS` |
| `EV-PC00-07` | **mới** — `PROV-PC00-02/03/04` tồn tại; register nhắc `CSRF_REJECTED`/`run.resume`/`SC44`; có §8.5 và §8.6; ≥ 20 quyết định của PC03/PC04/PC08 được đăng ký (kiểm đích danh `PROV-PC03-04`, `PROV-PC04-06`, `PROV-PC04-09`, `PROV-PC08-03`); ba mục Owner mới đủ 8 trường; mục purge nêu hai hệ quả PC08; có RPO/RTO; `REQ-S9.3-08` ghi rõ `REQ-S8.4-01` không tồn tại; `REQ-S7.3-05` dẫn `SC44` | `PASS` |

**`NOT_RUN`:** audit độc lập epoch kế tiếp (thuộc A1; `worker-W1` bị cấm tự kiểm bản sửa của mình); E1–E4; kiểm chứng ngữ nghĩa các quyết định của PC03/PC04/PC08 mà tôi chỉ **đăng ký**. Oracle của `EV-PC00-07` là *sự hiện diện và nhất quán của tham chiếu*, không phải tính đúng kỹ thuật của các quyết định đó.

## B6. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-06` | Coordinator → PC09 | PC00 đã cấp dải scenario tới `SC44` và ghi `SC45+` là chưa cấp. PC05/PC06/PC07 phải khai dải của mình trong handoff, và PC09 phải đối chiếu `acceptance/scenarios.yaml` với 44 anchor này — anchor tồn tại **không** chứng minh scenario đã được viết. |
| `CR-PC00-07` | Coordinator → PC01 | Ba việc PC00 không tự làm được: (a) `ports.yaml` phải đổi `REQ-S8.4-01` → `REQ-S9.3-08` (ID đúng nay có trong `notes` của hàng đó); (b) `run.resume` phải mở guard cho `blocked` với `unblock_reason` bắt buộc theo `PROV-PC00-04`; (c) `data.purge_all.scenario_refs` phải là `[SC44]`. |
| `CR-PC00-08` | Coordinator → PC03 + PC05 | `CSRF_REJECTED` mới chỉ tồn tại như một quyết định trong `decision-register.md`; nó **chưa** có trong `contracts/errors.yaml` (tôi đã kiểm: 0 hit). PC03 FIX1 phải đăng ký, PC05 phải ánh xạ, và `FORBIDDEN_EDGE` phải thu hẹp về đúng các ca `NC-*`. Nếu chỉ sửa fixture thì tái tạo đúng lớp lỗi `F-A1R1-01`. |
| `CR-PC00-01`, `-02`, `-03`, `-04`, `-05` | Coordinator | Vẫn mở, không đổi. |
| `PROV-PC00-01` | Owner | Phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`; nay có thêm hai hệ quả PC08 để Owner cân nhắc. |

**Concern:**
1. Tôi **đăng ký** 20 quyết định của PC03/PC04/PC08 nhưng **không thẩm định** chúng; `EV-PC00-07` chỉ chứng minh chúng có mặt và tham chiếu khớp. `PROV-PC03-04` (tự chạy lại một lần từ `unknown_attempt`) là chỗ chính gói đó xin Auditor soi kỹ — tôi giữ nguyên lời tự khai, không làm mềm.
2. `PROV-PC00-02` và `PROV-PC00-04` mô tả hành vi mà **file hợp đồng chưa có** (`CSRF_REJECTED` chưa ở `errors.yaml`; `run.resume` chưa mở guard). Cho tới khi PC01/PC03/PC05 landing, `decision-register.md` và `contracts/` **lệch nhau** ở đúng hai điểm này — đã nêu ở `CR-PC00-07`/`CR-PC00-08` để không ai đọc register rồi tưởng hợp đồng đã có.
3. `owner-decision-request.md` nay 24 mục và dài; nếu Owner chỉ đọc một lần, phiếu trả lời cuối file là đường ngắn nhất. Nếu Coordinator muốn một bản rút gọn cho Owner, đó là packet khác — tôi không tự tạo bản thứ hai vì hai bản sẽ lệch nhau.
4. Bốn finding MAJOR của vòng R1 và các finding R2 ngoài scope vẫn `OPEN`; đợt này không gỡ verdict nào.

## B7. Trạng thái bàn giao (FIX2)

- **next actor:** `Coordinator` — rehash độc lập 4 file ở §B4, freeze epoch mới, chuyển A1 xác minh `F-A1R2-05`.
- **lease_released_at (UTC):** 2026-09-06T18:38Z. `LEASE-PC00-e3` (fencing 3) nhả tại đây; `worker-W1` không ghi thêm file nào, kể cả sửa lỗi đánh máy. Sửa tiếp cần packet mới, baseline mới (hash ở §B4) và lease fencing ≥ 4.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX3 (anchor SC45–SC48)

## C1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX3` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX3` |
| lease_id | `LEASE-PC00-e4` (exclusive, **fencing 4**) |
| enforcement_mode | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · ceiling `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-06T19:00Z / 2026-09-06T19:03Z |
| lease expires_at (UTC) | 2026-09-07T08:00Z — `date -u` trước lần ghi cuối: 2026-09-06T19:02Z, còn hiệu lực |
| next actor / lease_released_at | `Coordinator` / 2026-09-06T19:03Z |
| scope | Chỉ `F-A1R3-03` / ruling `R4-03`: anchor SC45–SC48 và quy tắc trọng tài cho SC49+ |
| inputs | `FIX4-rulings.md` R4-03; `A1-R3-report.md` §5 `F-A1R3-03`; `acceptance/fixtures/telegram/README.md` |

`F-A1R3-03` chuyển OPEN → FIX_PROPOSED. Không finding nào được đóng ở đây; A1 xác minh ở freeze kế tiếp và người xác minh không được là `worker-W1`.

## C2. Đã đổi gì

**Bốn anchor mới**, `origin_package: PC07`, `line: null` (không phải trích dẫn từ SRC-PLAN), `allocation_group: post-§13`, `registered_by_ruling: R4-03`:

| Anchor | `subject_vi` | `maps_to_req` |
| --- | --- | --- |
| `SRC-PLAN:SC45` | run-now bị chặn bởi `needs_user` | `REQ-AC04` |
| `SRC-PLAN:SC46` | callback Telegram cũ (revision/generation) | `REQ-D38` |
| `SRC-PLAN:SC47` | vòng đời mã liên kết và ngoại lệ B09 | `REQ-S11.3-02` |
| `SRC-PLAN:SC48` | schema Saved từ chối payload sai | `REQ-D55` |

**Nguồn của chủ đề — và một điểm lệch cần Coordinator biết.** Packet mô tả bốn scenario là *"multipart unknown part / lost response / unlink before send / relink"*, nhưng cũng nói rõ **lấy chủ đề từ `acceptance/fixtures/telegram/README.md`**. Hai mô tả **không khớp nhau**: README (dòng 54–55, và các hàng fixture ở dòng 42–50) khai SC45–SC48 đúng như bảng trên. Tôi theo README vì (a) packet chỉ đích danh nó là nguồn, (b) nó là file đã đóng băng mà fixture của PC07 thực sự trích dẫn, và (c) đặt chủ đề theo cách diễn đạt trong ruling sẽ tạo ra đúng lớp lỗi "một hành vi, nhiều mô tả" mà `F-A1R1-01` đã phạt. Bốn chủ đề trong ruling (multipart, lost response, unlink trước khi gửi, relink) mô tả **những tình huống khác** — chúng gần với `SC14`/`SC25` đã tồn tại; nếu Coordinator thật sự muốn bốn scenario đó thì chúng cần **số khác** và một ruling riêng. Xem `CR-PC00-09`.

**Quy tắc cấp phát SC49+.** `scenario_id_allocation` nay ghi `SC45-SC48` thuộc PC07, và thay dòng `SC45+` cũ bằng `SC49+`: **chưa cấp, trọng tài là PC09**, không gói nào được tự lấy số, và một packet PC00 cuối cùng sẽ đăng ký anchor sau khi PC09 bàn giao. Đây là câu trả lời trực tiếp cho vế thứ hai của remediation constraint trong `F-A1R3-03` — *"the allocation rule for SC45+ must name an arbiter (PC09) so concurrent packages cannot collide rather than merely happening not to"*. **Không đoán SC49+**, đúng chỉ thị packet.

Bất biến anchor được giữ và nay được kiểm chặt hơn: mọi nhãn khớp `SC\d\d`, **liên tục SC01–SC48 không khoảng trống**, đúng 48 entry, `origin_package` khớp dải đã cấp.

## C3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `61fb00b78e2a62bcf0e7fce041077e79b90e6fb670f4e679cb88f1ad2a284931` (87560) | `604e2c1c618ec53ba1515f0a80eb18b0df7f84973e4cb8baa4ec60496459933f` (89856) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `3688a32831eed125f7ba47d778a59ba93b7e973203866af2cbe69a21ae8c1f3f` (56144) | *(file này — Coordinator rehash độc lập)* |

**1 MODIFY + 1 APPEND.** Không path nào khác bị chạm: `precode/requirements.csv`, `decision-register.md`, `owner-decision-request.md`, `precode/adr/*` giữ nguyên giá trị FIX2. `precode/source/*` không sửa; rehash sau khi xong: `d35e1f2d…` / `f65bb046…`, khớp nguồn. Không chạm `contracts/`, `acceptance/`, handoff của gói khác, `agent_profile/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## C4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-06T19:02Z / 2026-09-06T19:02Z · **exit code 0** · **168 assertion, 168 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- `EV-PC00-06` được siết theo packet: SC19–SC48 đều có anchor riêng; **đúng 48** entry; dãy số **liên tục 1–48**; mọi nhãn khớp `SC\d\d`; SC29–SC48 mang `allocation_group: post-§13`; `origin_package` của SC45–48 là `PC07`; bảng cấp phát có `SC45-SC48` và `SC49+` với trọng tài `PC09`, và **không còn** dòng `SC45+` mơ hồ.
- `EV-PC00-01..05` và `EV-PC00-07` chạy lại nguyên trạng, đều `PASS`.
- **`NOT_RUN`:** audit độc lập epoch kế tiếp; E1–E4; kiểm chứng rằng bốn scenario này đã được **viết** trong `acceptance/scenarios.yaml` — anchor tồn tại chỉ chứng minh ID có chỗ neo, không chứng minh scenario tồn tại.

## C5. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-09` | Coordinator | Ruling R4-03 và `acceptance/fixtures/telegram/README.md` mô tả SC45–SC48 **khác nhau** (xem §C2). Tôi theo README. Nếu bốn chủ đề trong ruling (multipart unknown part, lost response, unlink trước khi gửi, relink) là scenario thật sự cần có, chúng phải mang **số khác** — SC49+ do PC09 cấp — và cần một ruling riêng; sửa `subject_vi` của SC45–48 sẽ làm anchor lệch khỏi fixture PC07 đã đóng băng. |
| `CR-PC00-06` | PC09 | Nay mạnh hơn: PC09 **là trọng tài** của SC49+ theo R4-03. PC09 vẫn phải đối chiếu `acceptance/scenarios.yaml` với 48 anchor — anchor tồn tại không chứng minh scenario đã được viết. |
| `CR-PC00-07`, `-08` | PC01 / PC03 / PC05 | Vẫn mở, không đổi: `REQ-S8.4-01` → `REQ-S9.3-08`; `run.resume` mở guard cho `blocked`; `data.purge_all.scenario_refs: [SC44]`; `CSRF_REJECTED` chưa có trong `contracts/errors.yaml`. |
| `PROV-PC00-01` | Owner | Phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`. |

**Concern:** (1) điểm lệch chủ đề ở `CR-PC00-09` là thứ duy nhất trong gói này tôi phải tự quyết, và tôi chọn nguồn mà packet chỉ đích danh; (2) `F-A1R3-03` nằm ở scope PC07 chứ không phải PC00 — bản sửa này gỡ vế anchor, nhưng verdict `FAIL` của PC07 do `F-A1R3-01` (một evidence record báo PASS trong khi 31 cột ở 13 fixture không resolve) **không** được đợt này chạm tới; (3) SC49+ cố ý để trống.

## C6. Trạng thái bàn giao (FIX3)

- **next actor:** `Coordinator` — rehash `precode/baseline.json`, freeze epoch mới, chuyển A1 xác minh `F-A1R3-03`.
- **lease_released_at (UTC):** 2026-09-06T19:03Z. `LEASE-PC00-e4` (fencing 4) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §C3) và lease fencing ≥ 5.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX4 (anchor SC49–SC53; đăng ký quyết định PC09/PC10)

## D1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX4` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX4` |
| lease_id | `LEASE-PC00-e5` (exclusive, **fencing 5**) |
| enforcement_mode | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · ceiling `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T00:16Z / 2026-09-07T00:19Z |
| lease expires_at (UTC) | 2026-09-07T12:00Z — `date -u` trước lần ghi cuối: 2026-09-07T00:18Z, còn hiệu lực |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T00:19Z |
| scope | Ruling `R5-06`: anchor SC49–SC53; đăng ký quyết định PROVISIONAL và câu hỏi Owner của PC09 và PC10 |
| inputs | `FIX5-rulings.md` R5-06 (và R5-07 để đối chiếu); `acceptance/scenarios.yaml`; `evidence/handoffs/PC09-handoff.md` §6.1–6.3; `evidence/handoffs/PC10-handoff.md` §6.4–6.5 |

**Ghi chú về lần chạy bị ngắt.** Lượt trước của packet này bị API rate limit cắt **trước khi có bất kỳ lần ghi nào**. Tôi đã tự kiểm chứng điều đó trước khi làm lại, chứ không tin lời mô tả: bốn file trong grant (`baseline.json`, `decision-register.md`, `owner-decision-request.md`, và handoff) đều còn **đúng hash sau FIX3** (`604e2c1c…`, `4532045f…`, `32f66afa…`, `82998ffa…`), và hai file nguồn vẫn khớp pin. Không có partial write, không cần rollback. Đồng hồ và hạn lease được kiểm lại trước khi bắt đầu.

## D2. Đã đổi gì

### Anchor SC49–SC53 (ruling R5-06)

Năm anchor mới, `origin_package: PC09`, `line: null`, `allocation_group: post-§13`, `registered_by_ruling: R5-06`. `subject_vi` **sao chép** từ `acceptance/scenarios.yaml` — ở đó trường mang tên `title_vi`, và tôi chép nguyên văn nội dung chứ không diễn đạt lại:

| Anchor | `subject_vi` | `maps_to_req` |
| --- | --- | --- |
| `SRC-PLAN:SC49` | Quét default-deny: mọi cạnh bị cấm trong `modules.yaml` đều bị từ chối, không đổi trạng thái nào | `REQ-D01` |
| `SRC-PLAN:SC50` | Đường chạy THÀNH CÔNG đầu-cuối: lịch → thu thập → làm giàu → phân tích → publish → gửi | `REQ-S5.2-01` |
| `SRC-PLAN:SC51` | Thiết lập lần đầu theo SRC-SPEC §5.1: đăng nhập, nhập tag, cấu hình provider, liên kết Telegram, đăng nhập X | `REQ-S5.1-01` |
| `SRC-PLAN:SC52` | Dựng lại embedding generation rồi chuyển active NGUYÊN TỬ → selection dùng đúng một generation | `REQ-D48` |
| `SRC-PLAN:SC53` | Đối soát sau restore HOÀN TẤT → dispatcher mở lại, outbox cũ vẫn không tự phát lại | `REQ-D58` |

Bảng cấp phát: thêm dòng `SC49-SC53` thuộc PC09; dòng `SC49+` cũ được thay bằng **`SC54+` — chưa cấp, trọng tài PC09**. Anchor completeness nay **SC01–SC53, liên tục, 53 entry**, mọi nhãn khớp `SC\d\d`.

Năm scenario này lấp bốn lỗ hổng PC09 đo được, đáng ghi vì chúng nói điều gì đó về bộ hợp đồng: trước SC49 **không cạnh nào** trong 36 cạnh bị cấm có scenario; 48 scenario đầu **đều** là nhánh lỗi hoặc một lát cắt, không cái nào khẳng định một đợt bình thường kết thúc đúng (SC50); năm dòng `REQ-S5.1-01..05` (bốn XN, P0) hoàn toàn không được trích dẫn ở đâu (SC51); I12 và I15 trước đó chỉ có **mặt âm** — chỉ chứng minh bị chặn, chưa bao giờ chứng minh đường đúng chạy được (SC52, SC53).

### PC09 — đã kiểm, đúng như packet dự đoán: không có quyết định sản phẩm, không có câu hỏi Owner

Packet viết "PC09: none expected — verify". Tôi đọc `PC09-handoff.md` §6.2 và xác nhận: ba quyết định của PC09 đều **mang tính phương pháp**, nằm trong phạm vi ủy quyền của verification owner, không đổi cam kết nào với Owner. Vẫn đăng ký ở `decision-register.md` §8.7 (`PROV-PC09-01..03`) để chúng không vô hình:

- `PROV-PC09-01` quy tắc `coverage_status` — điểm đáng soi mà chính PC09 nêu: **84 dòng** nhận `BLOCKED_B<nn>` vì nằm trong "REQ ảnh hưởng" của một amendment, nghĩa là văn bản cam kết của chính dòng đó sẽ đổi nếu Owner phê chuẩn.
- `PROV-PC09-02` header của `traceability.csv` đặt ở front-matter `review.md` — theo đúng tiền lệ `requirements.csv`.
- `PROV-PC09-03` chấp nhận tên trường đồng nghĩa trong `x-contract.deviations`.

Ghi thêm một điều **PC09 làm đúng và không nên bị "sửa" cho gọn**: packet của nó viết "expect G0–G3 `MET_PROVISIONAL` at best", nhưng PC09 ghi `G0 = MET_PROVISIONAL` và `G1, G2, G3 = PARTIALLY_MET`, vì mỗi cổng còn ít nhất một điều kiện đo được chưa đạt (G1-X5: 26 cạnh; G2-X3: TSR-A01; G3-X5: `REQ-A6` và `CR-PC07-04` còn **KC**). Đó là từ chối nâng nhãn bằng suy diễn, đúng SRC-PLAN §2 và §9.

### PC10 — ba giả định PROVISIONAL và một ngoại lệ định dạng

`PROV-PC10-01` layout đường dẫn stack A · `PROV-PC10-02` ba không gian ID mới (`EVM-<Task ID>`, `SG-<nn>`, `PC10-PIN-<ngày>`) · `PROV-PC10-03` hai nhãn claim. Với `PROV-PC10-03` tôi **không** để mở: đối chiếu ruling `R5-07` cho thấy nó **đã được chốt** — `CONTRACT_ONLY` phải thay bằng nhãn của SRC-PLAN §2 (PC10-FIX1 thực hiện), còn `LIVE_FEASIBILITY_VERIFIED` vốn **có** trong §2 nên giữ. Ghi rõ trạng thái "đã có ruling" thay vì liệt kê nó như một câu hỏi còn treo.

Ngoại lệ front-matter của card `TC-*.md` được ghi lại như một **ngoại lệ khai báo**, kèm lý do PC10 nêu (card không phải hợp đồng mà là lệnh giao việc pin một hợp đồng).

### Owner request — chỉ một sửa, có chủ đích

Tôi **không** tạo mục Owner mới cho các hạng mục PC10. Lý do: đọc `PC10-handoff.md` §6.4 thì `PROV-PC10-02` (không gian ID) và ngoại lệ front-matter là việc **Coordinator** xác nhận, không phải Owner; `PROV-PC10-03` đã có ruling. Thứ duy nhất thật sự thuộc Owner là **hệ quả của lựa chọn stack**, và mục đó đã tồn tại. Nên tôi bổ sung vào chính mục **Stack**: PC10 đã bàn giao **18 task card** dựng trên giả định A; nếu Owner chọn B/C thì **chỉ §3 (đường dẫn) và §8 (lệnh build/test) của mỗi card phải viết lại** — hợp đồng, schema, scenario và fixture không đổi. Tức là trả lời muộn không làm hỏng gì, chỉ tốn một lượt sửa 18 card. Tạo thêm một mục Owner cho những thứ Owner không quyết sẽ làm loãng một tài liệu đã 24 mục.

## D3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `604e2c1c618ec53ba1515f0a80eb18b0df7f84973e4cb8baa4ec60496459933f` (89856) | `be50ca8bd033d9a911bb0d569e76bd62213522a796d71b3121bcfb05da4cb0c4` (92807) |
| `precode/decision-register.md` | MODIFY | `4532045f286bb42f9fba25efa22d76664713877105797b9cd83c67a8877a8643` (79647) | `da0a58ba4121519de3bf3b77855f62375eb76d4fdbc73194f3e95e260751a35f` (85259) |
| `precode/owner-decision-request.md` | MODIFY | `32f66afa10727e7b97f7a96c965b34246a8a04d7ff2d32883f28969af3239fcd` (54351) | `91182f46766f82c74994dd7f3b86c2b77984599100b43884259bd2b6b9cf1073` (54917) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `82998ffa027f90c838666fcbb3602c074e31689f3594bc186e0d0d34fa1fc460` (63731) | *(file này — Coordinator rehash độc lập)* |

**3 MODIFY + 1 APPEND.** `precode/requirements.csv` và `precode/adr/*` không đổi. `precode/source/*` không sửa; rehash sau khi xong: `d35e1f2d…` / `f65bb046…`, khớp pin. Không chạm `contracts/`, `acceptance/`, handoff của gói khác, `agent_profile/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## D4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T00:18Z / 2026-09-07T00:18Z · **exit code 0** · **179 assertion, 179 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- `EV-PC00-06` siết theo R5-06: SC19–SC53 đều có anchor riêng; **đúng 53** entry; dãy **liên tục 1–53**; mọi nhãn khớp `SC\d\d`; SC29–SC53 mang `allocation_group: post-§13`; `origin_package` của SC49–53 là `PC09`; bảng cấp phát có `SC49-SC53` và `SC54+` với trọng tài PC09, và **không còn** dòng `SC45+`/`SC49+` mơ hồ.
- `EV-PC00-07` thêm: §8.7 tồn tại; `PROV-PC09-01..03` và `PROV-PC10-01..03` đều được đăng ký; kết quả kiểm "PC09 none expected" được ghi thành chữ; ngoại lệ front-matter của card được ghi nhận; mục Stack nêu hậu quả 18 card.
- `EV-PC00-01..05` chạy lại nguyên trạng, đều `PASS`.
- **`NOT_RUN`:** audit độc lập epoch kế tiếp; E1–E4; kiểm chứng nội dung kỹ thuật của các quyết định PC09/PC10 mà tôi chỉ **đăng ký**.

## D5. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-10` | Coordinator | Nay đã có **bốn** ngoại lệ header cùng loại: ADR (ruling R-05), `requirements.csv`, `traceability.csv` (`PROV-PC09-02`), và card `TC-*.md` (R5-07). Đề nghị khi sửa baseline §3 lần tới thì gom thành **một câu quy tắc chung** — "file không phải hợp đồng (decision record, registry dạng CSV, task card) mang header riêng đã khai báo, liệt kê tại …" — thay vì bốn ngoại lệ rời rạc mà mỗi lượt audit phải đối chiếu lại. |
| `CR-PC00-06` | PC09 | Vẫn mở và nay áp cho 53 anchor: anchor tồn tại **không** chứng minh scenario đã được viết. R5-08 giao PC09 điền `fixture_refs` cho 12 scenario. |
| `CR-PC00-09` | Coordinator | Vẫn mở: mô tả SC45–SC48 trong ruling R4-03 khác `acceptance/fixtures/telegram/README.md`; tôi theo README. |
| `CR-PC00-07`, `-08` | PC01 / PC03 / PC05 | Vẫn mở: `REQ-S8.4-01` → `REQ-S9.3-08`; `run.resume` mở guard cho `blocked`; `data.purge_all.scenario_refs: [SC44]`; `CSRF_REJECTED` chưa có trong `contracts/errors.yaml`. |
| `PROV-PC00-01` | Owner | Phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`. |

**Concern:**
1. Tôi **đăng ký** sáu quyết định của PC09/PC10 nhưng **không thẩm định** chúng; `EV-PC00-07` chỉ chứng minh chúng có mặt.
2. `PROV-PC09-01` đáng để Auditor soi: quy tắc `coverage_status` khiến **84 dòng** traceability mang trạng thái phụ thuộc việc Owner có phê chuẩn amendment hay không. Đó là con số lớn, và nó nói rằng phần lớn "độ phủ" hiện tại là **có điều kiện**.
3. `SC54+` cố ý để trống; tôi không đoán.
4. Verdict FAIL còn tồn của các gói khác không được đợt này chạm tới.

## D6. Trạng thái bàn giao (FIX4)

- **next actor:** `Coordinator` — rehash ba file ở §D3, freeze epoch mới.
- **lease_released_at (UTC):** 2026-09-07T00:19Z. `LEASE-PC00-e5` (fencing 5) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §D3) và lease fencing ≥ 6.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX5 (đăng ký I16/I17; trạng thái CR của PC00)

## E1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX5` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX5` |
| lease_id | `LEASE-PC00-e6` (exclusive, **fencing 6**) |
| enforcement_mode | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · ceiling `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T01:12Z / 2026-09-07T01:15Z |
| lease expires_at (UTC) | 2026-09-07T16:00Z — `date -u` trước lần ghi cuối: 2026-09-07T01:14Z, còn hiệu lực |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T01:15Z |
| scope | `F-A2R1-07` (ruling FIX6 F-07): đăng ký I16/I17; và trạng thái cho bốn CR của PC00 mà `F-A2R1-04` thấy chưa có trạng thái |
| inputs | `A2-R1-report.md` §F-A2R1-07 (và §F-A2R1-10 để đối chiếu polarity); `FIX6-rulings.md` hàng F-07; `contracts/data/invariants.md` §I16, §I17; `contracts/data/entities.yaml`; `acceptance/scenarios.yaml`; `precode/review.md` §12 |

Baseline trước khi sửa đã được kiểm lại: `baseline.json` `be50ca8b…` (92807), `decision-register.md` `da0a58ba…` (85259) — khớp §D3 của addendum FIX4; hai file nguồn khớp pin.

## E2. Đã đổi gì

### I16 và I17 — decision record (`PROV-PC00-05`, `PROV-PC00-06`)

Finding nói đúng chỗ đau: baseline §3 cho phép `I16+` **chỉ khi có decision record**, nhưng lời biện minh cho hai invariant này chỉ tồn tại **bên trong `contracts/data/invariants.md`** — tức bên trong chính hợp đồng tiêu thụ chúng. Như A2 viết: *"Defining an invariant inside the contract that consumes it is what the rule exists to prevent."*

`decision-register.md` §8.8 nay có hai record đầy đủ theo đúng khuôn của các quyết định tự đưa ra khác: phát biểu (nguyên văn nguồn), **vì sao cần một invariant riêng chứ không phải một dòng phụ của I04/I03/I08**, nguồn SRC-PLAN/SRC-SPEC, owner contract, counterexample phải FAIL, oracle, scenario theo cực, trạng thái, "nếu bị bác bỏ", liên kết. Lập luận kỹ thuật là **của PC02** và tôi không viết lại — tôi ghi nhận, gắn trạng thái, và nêu phần còn thiếu.

Cả hai ở `PROVISIONAL`, `decision_owner: Owner` (không phải Coordinator): I16 siết cách hiển thị một mục thiếu summary — chạm `REQ-D19` (XN) và `AMD-B17`; I17 là cơ chế thực thi của `REQ-D29` (XN) và `REQ-D55` sau merge, và của `AMD-B15`. Cả hai đều chạm phần Owner đã đọc.

**Một khoảng trống tôi ghi thay vì lấp.** I16 có scenario dương (`SC10`, `SC50`) nhưng **không** có scenario nào khai `polarity: negative`. `SC28` trích I16 nhưng khai `mixed`, mà theo `F-A2R1-10` thì `mixed` không tính cho cực nào. Tôi **không** tự khai lại polarity của một scenario mình không sở hữu, và cũng không cấp `SC54+` để lấp — cả hai việc đó thuộc `F-A2R1-10` (W6). Khoảng trống được viết thành chữ trong `PROV-PC00-05` và vào cả `negative_scenarios: []` của anchor, để nó đếm được chứ không nằm trong văn xuôi. I17 thì đủ cả hai cực (`SC07`/`SC12` dương, `SC23` âm).

### Anchor và convention trong `baseline.json`

- `id_conventions.invariant.form`: `I01..I15` → **`I01..I17`**, kèm ghi chú rằng hai cái mới được nhận vào **đúng theo** điều kiện của chính quy tắc, trỏ về `decision-register.md` §8.8, và `I18+` vẫn phải có decision record mới.
- Anchor đặt ở **nhóm mới `source_anchors.PROJECT.invariants`**, không đặt trong nhóm `SRC-PLAN`. Đây là chỗ tôi phải tự quyết: ruling nói "cite in baseline.json anchors" và audit nói "alongside I01–I15", nhưng I16/I17 **không có trong văn bản SRC-PLAN**. Nhét chúng vào nhóm `SRC-PLAN` sẽ tạo một anchor giả nguồn — đúng lớp lỗi mà chính finding này phạt. Nhóm `PROJECT` giữ được cả hai yêu cầu: mỗi ID có anchor riêng, dãy `I01..I17` liên tục và kiểm được bằng script, mà không ai đọc nhầm chúng là trích dẫn từ kế hoạch. Mỗi entry mang `source_file`, `heading`, `owner_contract`, `decision_record`, scenario theo ba cực, `status`, `decision_owner`, `registered_by_ruling`.

### Trạng thái CR của PC00 — `decision-register.md` §8.9

Bảng 10 dòng cho `CR-PC00-01`…`-10`. Bốn dòng packet chỉ định dùng đúng trạng thái được giao: `-01` giải bằng lượt hòa giải FIX1; `-03` giải bởi PC03/PC04; `-09` giải bởi `PKT-PC00-FIX3`; `-10` giải bởi quy tắc header chung. Sáu dòng còn lại tôi **không** tự đặt trạng thái mà lấy nguyên từ `precode/review.md` §12 để hai file không lệch: `-02`, `-05`, `-06` là "còn mở, giao PC09, đã xử lý"; `-04`, `-07`, `-08` là "đã được đáp ứng ngược dòng".

Bảng kết bằng một dòng về **mức bằng chứng**: "đã được đáp ứng ngược dòng" là **lời tự khai của gói nhận** — `review.md` nói rõ PC09 ghi nhận chứ không tự xác minh từng cái. Không dòng nào là `CLOSED`; đóng một CR hay một finding cần authority được chỉ định sau xác minh độc lập trên epoch mới, và người xác minh không được là người viết bản sửa.

## E3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `be50ca8bd033d9a911bb0d569e76bd62213522a796d71b3121bcfb05da4cb0c4` (92807) | `9f7f193a96aa905cea6eb5e4666ee96ece88e3fd7454099e89482373aafd0971` (95055) |
| `precode/decision-register.md` | MODIFY | `da0a58ba4121519de3bf3b77855f62375eb76d4fdbc73194f3e95e260751a35f` (85259) | `b4ad99f3380a76fe5e75bc8ca9a43b0f122418209c3018167565db5dc0f93a3b` (95535) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `4d5fe0cb2f69c4d312f1c5d8d767abf24bd08eda1ff268842326c5df579c667a` (75470) | *(file này — Coordinator rehash độc lập)* |

**2 MODIFY + 1 APPEND.** `precode/requirements.csv`, `precode/owner-decision-request.md`, `precode/adr/*` không đổi. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, handoff gói khác, `agent_profile/`, và **không** chạm `precode/review.md` (ngoài grant — W6 hợp nhất 75 CR ở đó song song với gói này). Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## E4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T01:14Z / 2026-09-07T01:14Z · **exit code 0** · **193 assertion, 193 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- `EV-PC00-07` thêm cho FIX6: anchor invariant **liên tục `I01..I17`** (15 ở `SRC-PLAN` + 2 ở `PROJECT`); `id_conventions.invariant.form == "I01..I17"`; convention trỏ về §8.8; I16/I17 đều `PROVISIONAL`/`Owner`; **không** anchor nào của chúng bắt đầu bằng `SRC-` (chống giả nguồn); register có §8.8, `PROV-PC00-05`, `PROV-PC00-06`, và câu ghi nhận khoảng trống cực âm của I16; §8.9 liệt kê **đúng** `CR-PC00-01..10` một lần, đúng thứ tự, kèm câu "không dòng nào là `CLOSED`".
- `EV-PC00-01..06` chạy lại nguyên trạng, đều `PASS` (anchor scenario vẫn SC01–SC53 liên tục, 53 entry).
- **`NOT_RUN`:** audit độc lập epoch kế tiếp; E1–E4; kiểm chứng ngữ nghĩa của I16/I17 trên một cơ sở dữ liệu thật (oracle của chúng là đếm hàng, chưa hàng nào tồn tại).

## E5. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-11` | Coordinator → W6 (`F-A2R1-10`) | I16 **chưa có** scenario khai `polarity: negative`; `SC28` trích I16 nhưng khai `mixed`. Cần hoặc tách `SC28`, hoặc thêm một scenario âm ở `SC54+`. Nếu cấp ID mới, PC00 sẽ neo anchor bằng một addendum một dòng (đúng cơ chế `F-A2R1-10` đã dự liệu). PC00 **không** tự khai lại polarity của scenario mình không sở hữu. |
| `CR-PC00-06` | PC09 | Vẫn mở: anchor tồn tại không chứng minh scenario đã được viết; `R5-08` giao PC09 điền `fixture_refs` cho 12 scenario. |
| `CR-PC00-02`, `-05` | PC09 | Còn mở, đã xử lý ở `gates.yaml` / traceability — xem §8.9. |
| `CR-PC00-04`, `-07`, `-08` | PC01/PC03/PC05 | "Đã được đáp ứng ngược dòng" theo lời tự khai; **chưa** có xác minh độc lập trên epoch mới. |
| `PROV-PC00-01` | Owner | Phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`. |

**Concern:**
1. Đặt anchor I16/I17 ở nhóm `PROJECT` thay vì `SRC-PLAN` là **diễn giải của tôi** đối với chữ "alongside I01–I15" trong remediation constraint. Nếu Coordinator muốn chúng nằm đúng trong danh sách `SRC-PLAN`, đó là một lần sửa generator — nhưng tôi khuyên không, vì nó tạo anchor giả nguồn.
2. Hai record này **ghi nhận** lập luận của PC02; `EV-PC00-07` chỉ chứng minh chúng tồn tại và tham chiếu khớp, không chứng minh invariant đúng.
3. `PROV-PC00-05` và `PROV-PC00-06` mang `decision_owner: Owner` nhưng **chưa** có mục trong `precode/owner-decision-request.md` — file đó ngoài grant của packet này. Nếu Coordinator muốn Owner phê chuẩn hai invariant, cần một packet mở grant cho ODR. Xem `CR-PC00-12` dưới đây.
4. `CR-PC00-12` → Coordinator: quyết định xem I16/I17 có cần một mục trong Owner request hay không; hiện chúng là PROVISIONAL với `decision_owner: Owner` mà Owner chưa được hỏi.

## E6. Trạng thái bàn giao (FIX5)

- **next actor:** `Coordinator` — rehash hai file ở §E3, freeze epoch mới, chuyển A2 xác minh `F-A2R1-07`.
- **lease_released_at (UTC):** 2026-09-07T01:15Z. `LEASE-PC00-e6` (fencing 6) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §E3) và lease fencing ≥ 7.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`; `F-A2R1-07` chuyển OPEN → FIX_PROPOSED, không đóng.

---

# ADDENDUM — PKT-PC00-FIX6 (CR-PC01-12 id đã bị gỡ; CR-PC00-12 decision_owner của I16/I17)

## F1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX6` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX6` · lease `LEASE-PC00-e7` (**fencing 7**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T01:17Z / 2026-09-07T01:19Z · lease expires 2026-09-07T16:00Z (`date -u` trước lần ghi cuối: 2026-09-07T01:18Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T01:19Z |
| scope | `CR-PC01-12` (id đã bị gỡ còn sót trong `precode/`) và `CR-PC00-12` (`decision_owner` của I16/I17) |

Baseline trước khi sửa khớp §E3 của addendum FIX5 (`9f7f193a…` / `b4ad99f3…`); hai file nguồn khớp pin.

## F2. `CR-PC01-12` — quét toàn bộ `precode/` tìm REQ id không tồn tại

Viết một script quét (`req_sweep.py`, chạy từ scratch dir) đối chiếu **mọi** REQ id xuất hiện dưới `precode/` với cột `req_id` của `precode/requirements.csv`. Loại trừ `precode/source/` (bản sao nguồn bất biến, không phải trích dẫn của PC00) và các **mẫu** ID (`REQ-S<section>-<nn>`), vì chúng là quy ước chứ không phải id.

**Kết quả: đúng một id lạ trong toàn bộ `precode/` — `REQ-S8.4-01`, ở hai chỗ.** Không có id lạ nào khác. Cả hai chỗ đều là **mô tả về chính lỗi đó**, không phải trích dẫn đang dùng:

| Vị trí | Bản chất | Xử lý |
| --- | --- | --- |
| `precode/decision-register.md:661` — hàng `CR-PC00-07` của bảng §8.9 | Tóm tắt CR: "id sai → id đúng" | **Đã sửa.** Viết lại thành *"`ports.yaml` trích một REQ id **không tồn tại** trong registry (SRC-SPEC không có §8.4; §8.4 là của SRC-PLAN) → phải trỏ sang `REQ-S9.3-08`"*. Nội dung CR giữ nguyên; chỉ không còn phát ra một token trông như trích dẫn hợp lệ |
| `precode/requirements.csv:197` — ô `notes` của `REQ-S9.3-08` | Bản ghi phát hiện gốc của `CR-PC03-01`, do chính PC00 viết ở FIX2 để PC01 biết id đúng | **Không sửa — ngoài grant.** Packet FIX6 chỉ cấp `decision-register.md`, `baseline.json`, `owner-decision-request.md` |

Tôi thêm một **ghi chú chống hồi quy** ngay dưới bảng §8.9: hàng đó cố ý không viết ra id sai, và người đọc sau **đừng "khôi phục"** nó — vì id ấy đã bị PC01-FIX3 gỡ khỏi `ports.yaml` và nhắc lại nguyên văn sẽ làm gate quét id báo động đúng cái `CR-PC01-12` vừa yêu cầu dọn.

Gate này nay **tự động**: `EV-PC00-07` chạy lại chính phép quét đó ở mỗi lần validate, FAIL nếu một id lạ xuất hiện trong bất kỳ file nào PC00 có quyền sửa, và **in ra** (không FAIL) những chỗ nằm ngoài grant để chúng không biến mất khỏi tầm nhìn. Hiện phần in ra đúng một dòng: `REQ-S8.4-01` tại `precode/requirements.csv:197`.

## F3. `CR-PC00-12` — `decision_owner` của I16 và I17

Đổi từ `Owner` thành **`Coordinator (provisional, technical)`** ở cả hai nơi: `decision-register.md` §8.8 và `baseline.json` → `source_anchors.PROJECT.invariants`, kèm `owner_note_vi` nêu rõ **không cần** một mục riêng trong `precode/owner-decision-request.md` **trừ khi Owner phản đối**.

Lập luận được viết vào chính hai record, chứ không chỉ nằm ở đây:

- **I16** là ranh giới **đọc** giữa hai bảng `analysis` và `analysis_attempt`. `REQ-D19` ("mỗi mục có summary hiển thị ngay tại mục") vẫn đúng nguyên văn; I16 chỉ nói rằng khi **chưa** có kết quả hợp lệ thì mục đó phải hiện là thiếu summary — đúng như `AMD-B17` đã chốt. Không cam kết nào của Owner đổi.
- **I17** là cơ chế **thực thi** của `REQ-D29` (XN), `REQ-D55` (UQ) và `AMD-B15` sau merge. Owner đã chọn "không báo lại" và "Saved là snapshot"; I17 chỉ nói merge không được phép âm thầm làm hai điều đó sai.

Vì vậy `precode/owner-decision-request.md` **không đổi** ở gói này (hash giữ nguyên `91182f46…`) — đúng điều kiện "only if a cross-ref is needed" của packet. Việc này cũng gỡ concern §E5 mục 3–4 của addendum trước: hai record không còn mang `decision_owner: Owner` mà thiếu mục Owner tương ứng.

## F4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `9f7f193a96aa905cea6eb5e4666ee96ece88e3fd7454099e89482373aafd0971` (95055) | `a6c52229e533bff803ff5294384839352eeb08e1ab4e117f028ed7f735f155b6` (95611) |
| `precode/decision-register.md` | MODIFY | `b4ad99f3380a76fe5e75bc8ca9a43b0f122418209c3018167565db5dc0f93a3b` (95535) | `43d41b0473e8d7861e0c09576fb5b9f5c59a9fe5202c395a68cb6c0fbf140627` (97034) |
| `precode/owner-decision-request.md` | *(không đổi)* | `91182f46766f82c74994dd7f3b86c2b77984599100b43884259bd2b6b9cf1073` (54917) | không sửa — không cần cross-ref |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `677176163616f5b36f6fdf11f108d69b0a6e7b6938934da1e81573c00936c56c` (85953) | *(file này — Coordinator rehash độc lập)* |

**2 MODIFY + 1 APPEND.** `precode/requirements.csv` và `precode/adr/*` không đổi. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `precode/review.md`, handoff gói khác, `agent_profile/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## F5. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py` (và `req_sweep.py` cho phần khảo sát ban đầu).
- **started/ended (UTC):** 2026-09-07T01:18Z / 2026-09-07T01:18Z · **exit code 0** · **197 assertion, 197 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- Mới trong `EV-PC00-07`: (a) không REQ id lạ nào trong các file PC00 có quyền sửa; (b) `decision-register.md` không còn nhắc `REQ-S8.4`; (c) I16 và I17 đều mang `decision_owner: Coordinator (provisional, technical)` **và** một `owner_note_vi` nói rõ điều kiện "trừ khi Owner phản đối"; (d) một dòng `[INFO]` liệt kê id lạ còn lại **ngoài** grant.
- `EV-PC00-01..06` chạy lại nguyên trạng, đều `PASS` (anchor scenario SC01–SC53; invariant I01–I17).
- **`NOT_RUN`:** audit độc lập epoch kế tiếp; E1–E4.

## F6. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-13` | Coordinator → chủ sở hữu `requirements.csv` (PC00, cần grant) | `precode/requirements.csv:197` (ô `notes` của `REQ-S9.3-08`) vẫn chứa `REQ-S8.4-01` như **bản ghi phát hiện** của `CR-PC03-01`. Ngoài grant FIX6 nên tôi không sửa. Hai lựa chọn: (a) để nguyên vì nó là bằng chứng lịch sử của defect, và cho gate whitelist đúng một dòng đó; (b) cấp grant để tôi viết lại như đã làm với §8.9. Tôi **khuyên (a)**: ô đó là lý do PC01 biết id đúng, và xóa dấu vết một defect đã sửa làm mất chuỗi truy vết. |
| `CR-PC00-11` | W6 (`F-A2R1-10`) | Vẫn mở: I16 chưa có scenario khai `polarity: negative`. |
| `CR-PC00-06` | PC09 | Vẫn mở: anchor tồn tại không chứng minh scenario đã được viết. |
| `CR-PC00-12` | — | **Đã giải** ở gói này. |
| `PROV-PC00-01` | Owner | Phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`. |

**Concern:** (1) `CR-PC00-13` ở trên — id lạ duy nhất còn lại nằm ngoài grant, và tôi cho rằng **nên** để nguyên chứ không dọn; cần Coordinator quyết để lần audit sau không coi đó là hồi quy. (2) Gate quét id nay chỉ FAIL trong phạm vi file PC00 sửa được; nếu Coordinator muốn nó phủ cả `contracts/` và `acceptance/`, đó là việc của PC09/W6 chứ không phải của `validate.py` này.

## F7. Trạng thái bàn giao (FIX6)

- **next actor:** `Coordinator` — rehash hai file ở §F4; PC10 có thể re-pin ngay.
- **lease_released_at (UTC):** 2026-09-07T01:19Z. `LEASE-PC00-e7` (fencing 7) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §F4) và lease fencing ≥ 8.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX7 (anchor SC54–SC56)

## G1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX7` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX7` · lease `LEASE-PC00-e8` (**fencing 8**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T01:34Z / 2026-09-07T01:36Z · lease expires 2026-09-07T18:00Z (`date -u` trước lần ghi cuối: 2026-09-07T01:34Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T01:36Z |
| scope | Anchor SC54–SC56; completeness SC01–SC56; SC57+ chưa cấp, trọng tài PC09 |
| input | `acceptance/scenarios.yaml` sha256 `4985c22f5b9b0c5caaf8ca49f2759e3b5d2372d4e1527b1739b2910570fcbfdc` — **đã kiểm khớp** giá trị packet nêu trước khi đọc |

## G2. Đã đổi gì

Ba anchor mới, `origin_package: PC09`, `line: null`, `allocation_group: post-§13`, `registered_by_ruling: FIX7`. `subject_vi` sao chép nguyên văn từ `title_vi` của `scenarios.yaml`:

| Anchor | `subject_vi` | Cực | Invariant |
| --- | --- | --- | --- |
| `SRC-PLAN:SC54` | Hai kết quả hợp lệ cho cùng một `(analysis_key, generation)` là KHÔNG THỂ — phản chứng của I04 | `negative` | I04 |
| `SRC-PLAN:SC55` | Usage không biết được ghi là `unknown` với ba trường NULL — mặt dương của I14 | `positive` | I14 |
| `SRC-PLAN:SC56` | Ghi 0 cho usage không biết, tự bật fallback, hoặc đếm attempt là kết quả — ba phản chứng của I14 và I16 | `negative` | I14, I16 |

Bảng cấp phát: thêm `SC54-SC56` thuộc PC09 (lấp cực polarity còn thiếu, `F-A2R1-10`); dòng `SC54+` cũ thay bằng **`SC57+` — chưa cấp, trọng tài PC09**. Anchor completeness nay **SC01–SC56, liên tục, 56 entry**; mọi nhãn khớp `SC\d\d`; `EV-PC00-06` kiểm cả ba điều đó và kiểm rằng **không còn** dòng `SCnn+` mơ hồ nào (`SC45+`, `SC49+`, `SC54+`).

**`SC56` lấp đúng khoảng trống tôi đã báo ở `CR-PC00-11`.** Ở addendum FIX5 tôi ghi rằng I16 có cực dương (`SC10`, `SC50`) nhưng **không** có scenario nào khai `polarity: negative` — `SC28` trích I16 nhưng khai `mixed`, và theo `F-A2R1-10` thì `mixed` không tính cho cực nào. `SC56` khai `negative` và trích I16, nên khoảng trống đó **đã đóng**. Tôi cập nhật anchor của I16: `negative_scenarios: ["SC56"]` (trước là `[]`), kèm `polarity_note_vi` ghi lại lịch sử để không ai tưởng nó chưa từng thiếu.

## G3. Hai điều cần Coordinator xử lý ngay

1. **`precode/baseline.json` đang được 18 task card pin theo hash.** Giá trị cũ `a6c52229…` (95611 byte) xuất hiện trong **18** file `agent-tasks/TC-*.md` ở bảng "Read set". Sau gói này hash là `320bde32…` (97614 byte), nên **cả 18 card đang pin một hash đã lỗi thời** cho tới khi PC10 re-pin. Đây là hệ quả biết trước của packet chứ không phải lỗi, nhưng nó **chặn** việc coi card là ready: một card pin sai hash thì người nhận card không thể xác minh baseline. → `CR-PC00-15`.
2. **Văn xuôi §8.8 của `precode/decision-register.md` nay đã cũ.** Nó vẫn viết rằng I16 "chưa có scenario nào khai `polarity: negative`" — đúng lúc viết, sai từ khi `SC56` tồn tại. File đó **ngoài grant** của packet này nên tôi không sửa; tôi ghi mâu thuẫn vào chính anchor I16 (`polarity_note_vi`) và kiểm bằng script, để nó không nằm im. → `CR-PC00-14`.

Tôi cố ý **không** tự mở rộng grant sang `decision-register.md` dù chỉ để sửa một câu: đó đúng là loại "tiện tay sửa" mà giao thức cấm, và một câu sai đã được ghi nhận thì vô hại hơn một lần ghi ngoài quyền.

## G4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/baseline.json` | MODIFY | `a6c52229e533bff803ff5294384839352eeb08e1ab4e117f028ed7f735f155b6` (95611) | `320bde327a71352490180eba7090a0a6624daea5e17bb032b4dc2e8ad5a43d2f` (97614) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `a691286259dc98773387858d4c3e37b7ec771e81d42df45cf195ed6c9561d5a4` (94642) | *(file này — Coordinator rehash độc lập)* |

**1 MODIFY + 1 APPEND.** Không file PC00 nào khác đổi (`requirements.csv`, `decision-register.md`, `owner-decision-request.md`, `adr/*` giữ nguyên giá trị FIX6). `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `agent-tasks/`, `precode/review.md`, handoff gói khác, `agent_profile/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## G5. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T01:35Z / 2026-09-07T01:35Z · **exit code 0** · **199 assertion, 199 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- `EV-PC00-06`: SC19–SC56 đều có anchor riêng; **đúng 56** entry; dãy **liên tục 1–56**; SC29–SC56 mang `allocation_group: post-§13`; `origin_package` của SC54–56 là `PC09`; bảng cấp phát có `SC54-SC56` và `SC57+` (trọng tài PC09) và không còn dòng `SCnn+` mơ hồ.
- `EV-PC00-07`: cực âm của I16 nay là `["SC56"]`; anchor I16 mang ghi chú trỏ `CR-PC00-14`.
- `EV-PC00-01..05` chạy lại nguyên trạng, đều `PASS`.
- **`NOT_RUN`:** audit độc lập epoch kế tiếp; E1–E4. Anchor tồn tại **không** chứng minh ba scenario này đã có fixture — `R5-08` giao PC09 điền `fixture_refs`.

## G6. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-14` | Coordinator → PC00 (cần grant `decision-register.md`) | §8.8 còn câu "chưa có scenario nào khai `polarity: negative`" cho I16; `SC56` đã lấp. Một dòng sửa, nhưng ngoài grant FIX7. |
| `CR-PC00-15` | Coordinator → PC10 | 18 card `agent-tasks/TC-*.md` pin `precode/baseline.json` ở hash cũ `a6c52229…` (95611); hash mới là `320bde32…` (97614). Cần một lượt re-pin trước khi coi card là ready. |
| `CR-PC00-11` | W6 (`F-A2R1-10`) | **Đã giải** bằng `SC56`. |
| `CR-PC00-13` | Coordinator | Vẫn mở: `REQ-S8.4-01` còn ở `precode/requirements.csv:197` như bản ghi lịch sử; tôi vẫn khuyên để nguyên. |
| `CR-PC00-06` | PC09 | Vẫn mở: anchor ≠ scenario đã viết; `fixture_refs` do `R5-08` giao. |
| `PROV-PC00-01` | Owner | Phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`. |

**Concern:** mỗi lần PC00 sửa `baseline.json` là một lần 18 card lệch pin. Nếu còn nhiều đợt anchor nữa, đề nghị Coordinator gom chúng lại rồi cho PC10 re-pin **một lần** ở cuối, thay vì re-pin sau mỗi packet — hiện tại chi phí đối soát lớn hơn giá trị của việc pin liên tục.

## G7. Trạng thái bàn giao (FIX7)

- **next actor:** `Coordinator` — rehash `precode/baseline.json`; giao PC10 re-pin 18 card (`CR-PC00-15`).
- **lease_released_at (UTC):** 2026-09-07T01:36Z. `LEASE-PC00-e8` (fencing 8) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §G4) và lease fencing ≥ 9.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX8 (giải `CR-PC00-14`: đồng bộ văn xuôi §8.8 với anchor)

## H1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX8` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX8` · lease `LEASE-PC00-e9` (**fencing 9**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T01:36Z / 2026-09-07T01:38Z · lease expires 2026-09-07T18:00Z (`date -u` trước lần ghi cuối: 2026-09-07T01:37Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T01:38Z |
| scope | Chỉ `CR-PC00-14`. Không việc gì khác. |

Đây là gói đầu tiên của chuỗi PC00 kết ở **`DONE`** chứ không phải `DONE_WITH_CONCERNS`: nó không phát sinh CR mới, không để lại mâu thuẫn nào, và mọi thứ nó chạm đều nằm gọn trong grant.

## H2. Đã đổi gì

### `precode/decision-register.md` §8.8 — ba câu

1. **Dòng scenario của I16.** Trước: *"Âm: **chưa có scenario nào khai `polarity: negative`**"*. Sau: âm là **`SC56`**, trích nguyên văn tiêu đề của nó, và `SC28` được xếp đúng chỗ là **hỗn hợp** — kèm câu giải thích vì sao `mixed` không thay thế được một cực âm thật (`F-A2R1-10`).
2. **Một mục "Lịch sử của mục này" mới.** Ghi lại đầy đủ đường đi thay vì lặng lẽ ghi đè: ở FIX5 I16 thật sự không có cực âm; PC00 ghi khoảng trống thành chữ và báo `CR-PC00-11` thay vì tự khai lại polarity của scenario mình không sở hữu; PC09 cấp `SC56` ở FIX7 và khoảng trống đóng. Cùng mục này ghi hai ID còn lại của cùng đợt PC09 — **`SC54`** (âm, phản chứng I04) và **`SC55`** (dương, mặt dương I14) — vì register có nhắc I04/I14 ở phần liên kết và người đọc cần biết cực của chúng nay nằm ở đâu.
3. **Câu về I17.** Trước: *"I17 là invariant **duy nhất trong hai cái mới** đã có đủ một cực dương và một cực âm"* — đúng lúc viết, sai từ khi `SC56` tồn tại. Sau: I17 có đủ hai cực **ngay từ đầu**; I16 đạt điều đó sau `SC56`.

Dòng **Liên kết** của I16 nay dẫn `I04 (cực âm riêng: SC54)`, `I14 (cực dương riêng: SC55)` và thêm `SC56`.

### `precode/baseline.json` — gỡ ghi chú mâu thuẫn

`polarity_note_vi` của anchor I16 trước đây nói *"Văn xuôi của §8.8 còn nói 'chưa có' — xem `CR-PC00-14`"*. Câu đó **đã lỗi thời** ngay khi §8.8 được sửa ở trên, nên nó được thay bằng một ghi chú **lịch sử** thuần: cực âm từng thiếu ở bản FIX5, PC09 cấp `SC56` ở FIX7, và §8.8 nay ghi đủ lịch sử (`CR-PC00-14` đã giải ở FIX8). `negative_scenarios: ["SC56"]` giữ nguyên.

Tôi **không** xóa hẳn trường đó. Một anchor nói "chưa từng có vấn đề" thì sai; anchor nói "đã từng thiếu, lấp bằng SC56, ở đợt nào" thì đúng và giúp lần audit sau không phải dựng lại lịch sử từ tám addendum.

### Gate mới, để lớp lỗi này không quay lại

`EV-PC00-07` nay kiểm **sự khớp giữa văn xuôi và dữ liệu**, không chỉ sự tồn tại: §8.8 không được chứa câu "chưa có scenario nào khai…"; §8.8 phải dẫn cả `SC54`, `SC55`, `SC56`; và câu "duy nhất trong hai cái mới" không được còn. Trước đây một câu văn xuôi cũ chỉ bị phát hiện khi có người đọc; nay nó FAIL.

## H3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/decision-register.md` | MODIFY | `43d41b0473e8d7861e0c09576fb5b9f5c59a9fe5202c395a68cb6c0fbf140627` (97034) | `212441a429420d1cc11cdc4a9c79a11648e45e1b92278a08f77a9779943ad15d` (97899) |
| `precode/baseline.json` | MODIFY | `320bde327a71352490180eba7090a0a6624daea5e17bb032b4dc2e8ad5a43d2f` (97614) | `e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` (97620) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `bcc70f25a7e427b07814f087e10b73edf9128cdf80450caa1902d65bd62ecfa9` (94642+) | *(file này — Coordinator rehash độc lập)* |

**2 MODIFY + 1 APPEND.** `requirements.csv`, `owner-decision-request.md`, `adr/*` không đổi. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `agent-tasks/`, `precode/review.md`, handoff gói khác, `agent_profile/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

**Pin của card.** `precode/baseline.json` đổi hash lần thứ hai trong đợt này (`a6c52229…` → `320bde32…` → `e4c3f456…`). W7 re-pin **một lần** sau khi cả đợt lắng, đúng như Coordinator đã sắp xếp và đúng đề nghị tôi nêu ở `CR-PC00-15`; giá trị cần pin là **`e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` (97620 byte)** nếu không còn packet nào chạm file này. `precode/decision-register.md` cũng đổi (`212441a4…`, 97899) — card nào pin file đó cũng phải lấy giá trị mới.

## H4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T01:37Z / 2026-09-07T01:37Z · **exit code 0** · **202 assertion, 202 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- Mới: §8.8 không còn câu "chưa có scenario nào khai…"; §8.8 dẫn `SC54`/`SC55`/`SC56`; câu "duy nhất trong hai cái mới" đã biến mất; `polarity_note_vi` của I16 mang dạng lịch sử (`CR-PC00-14 da giai`) chứ không còn là cảnh báo.
- `EV-PC00-01..06` chạy lại nguyên trạng, đều `PASS` (anchor scenario SC01–SC56 liên tục; invariant I01–I17).
- **`NOT_RUN`:** audit độc lập epoch kế tiếp; E1–E4. Anchor và văn xuôi khớp nhau **không** chứng minh ba scenario đó đã có fixture — `R5-08` giao PC09 điền `fixture_refs`.

## H5. Unresolved

Gói này **không phát sinh CR mới**. Trạng thái các CR còn lại của PC00:

| ID | Trạng thái |
| --- | --- |
| `CR-PC00-14` | **Đã giải** ở gói này |
| `CR-PC00-11` | **Đã giải** (PC09 cấp `SC56` ở FIX7) |
| `CR-PC00-15` | Còn mở — W7 re-pin 18 card một lần sau đợt này; giá trị mới ở §H3 |
| `CR-PC00-13` | Còn mở — `REQ-S8.4-01` ở `precode/requirements.csv:197` là bản ghi lịch sử; tôi vẫn khuyên để nguyên, gate báo `[INFO]` chứ không FAIL |
| `CR-PC00-06` | Còn mở — anchor tồn tại không chứng minh scenario đã có fixture (`R5-08` giao PC09) |
| `PROV-PC00-01` | Còn mở — phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED` |

## H6. Trạng thái bàn giao (FIX8)

- **next actor:** `Coordinator` — rehash hai file ở §H3; W7 re-pin sau khi đợt lắng.
- **lease_released_at (UTC):** 2026-09-07T01:38Z. `LEASE-PC00-e9` (fencing 9) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §H3) và lease fencing ≥ 10.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`.

---

# ADDENDUM — PKT-PC00-FIX9 (packaging: lưu hồ sơ audit và điều phối)

## I1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX9` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX9` · lease `LEASE-PC00-e10` (**fencing 10**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T02:35Z / 2026-09-07T02:38Z · lease expires 2026-09-07T20:00Z (`date -u` trước lần ghi cuối: 2026-09-07T02:37Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T02:38Z |
| scope | Packaging phase: lưu vĩnh viễn 7 AUDIT_REPORT, 7 FROZEN_CANDIDATE manifest, baseline điều phối, 11 TASK_PACKET của PC00–PC10, 6 packet audit, 6 file ruling và sổ tiến độ của Coordinator |

## I2. Đã tạo gì

**39 file mới**, trong đó **37 là bản sao nguyên văn** và 2 là chỉ mục do tôi viết.

| Thư mục | Nội dung | Số file |
| --- | --- | --- |
| `evidence/audits/` | 7 AUDIT_REPORT (`A1-R1..R3` của `auditor-A1`; `A2-R1..R4` của `auditor-A2`) + 7 manifest (`FC-W1`, `FC-W2`, `FC-W3`, `FC-W4`, `FC-W4e5`, `FC-W4e6`, `FC-W4e7`) + `README.md` | 15 |
| `evidence/coordination/` | `00-coordination-baseline.md`; 11 packet `PC00`–`PC10`; 6 packet audit (`A1-audit-1/2/3`, `A2-final-audit`, `A2-verify`, `A2-rereview`); 6 file ruling (`FIX-A1R1`, `FIX3`…`FIX7`); `coordinator-ledger.md` (bản sao `progress.md`) + `README.md` | 26 |

Cộng một dòng vào bảng bản đồ thư mục của `precode/README.md` trỏ tới hai thư mục này.

**Bản sao là byte-identical, đã kiểm hai lần.** Chép bằng `cp -p`, rồi `cmp` từng cặp file **ngay sau khi chép** và **một lần nữa trước handoff**: 37/37 giống hệt cả hai lần. SHA-256 trong hai README được tính **sau khi chép**, từ chính bản đã nằm trong repo — nên nếu ai đó sửa một bản sao, chỉ số sẽ lệch. Tôi **không** biên tập, tóm tắt hay sửa chính tả bất kỳ file nào được chép, kể cả những đoạn nói về công việc của chính tôi hoặc phê bình nó.

## I3. Điều hai README phải nói rõ, và vì sao

Cả hai README mở đầu bằng cùng một ghi chú: **những bản ghi này ra đời sau lần freeze `FC-W4` epoch 7 mà `A2-R4` đã audit**, nên chúng **không** nằm trong bất kỳ candidate manifest nào đã được audit.

Đó không phải một lời xin lỗi mà là một ràng buộc của giao thức. `protocol.md` §6 viết: *"Persist audit report là new evidence artifact trong packaging phase; không chèn report vào manifest mà report đang ký."* Một báo cáo không thể nằm trong chính snapshot nó ký, và một manifest không thể chứa chính nó. Nếu sau này có epoch mới, epoch đó **có thể** bao gồm thư mục này với role `EVIDENCE` — nhưng không bao giờ như candidate.

Hai README cũng nêu ba giới hạn mà người đọc về sau dễ hiểu sai:

1. **Verdict trong báo cáo có phạm vi.** Mỗi PASS/FAIL chỉ áp cho phần auditor thật sự kiểm; không cái nào là product acceptance. Cả bảy báo cáo ở mức **E0** — kiểm tính nhất quán tĩnh của văn bản hợp đồng. Không có E1–E4; không có gì được chạy.
2. **Finding không bị đóng bởi việc lưu trữ này.** Chuyển sang `CLOSED` cần authority được chỉ định sau xác minh độc lập trên epoch mới, và người xác minh không được là người viết bản sửa (`protocol.md` §8).
3. **`coordinator-ledger.md` là lời tự thuật của một bên.** Nó do Coordinator viết về chính công việc điều phối; tôi ghi rõ điều đó trong README thay vì để nó trông ngang hàng với một báo cáo audit độc lập.

## I4. Changes

Tất cả là `CREATE`, baseline `ABSENT` (hai thư mục chưa tồn tại trước gói này), trừ một `MODIFY`.

| Path | Op | Ghi chú |
| --- | --- | --- |
| `evidence/audits/` | CREATE | 14 bản sao nguyên văn + `README.md` (`8d2a33cad295b30426be93d4e63a6c21773026817084cc6e4422b066ed053370`, 5347 byte) |
| `evidence/coordination/` | CREATE | 24 bản sao nguyên văn + `coordinator-ledger.md` + `README.md` (`0ccb55defb949d89dde7600c9e87b6c019b8460ae73480701dbd319b076eba18`, 7183 byte) |
| `precode/README.md` | MODIFY | thêm **một** hàng vào bảng bản đồ thư mục → `44c36fba4f2c9ad254c10a165113309db171abf42106e80815bfae8054747e01` (15292 byte) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* |

SHA-256 và byte count của **từng** bản sao nằm trong hai README, không lặp lại ở đây.

Không file PC00 nào khác đổi: `baseline.json` (`e4c3f456…`), `decision-register.md` (`212441a4…`), `requirements.csv`, `owner-decision-request.md`, `adr/*` giữ nguyên giá trị FIX8. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `agent-tasks/`, `precode/review.md`, handoff gói khác, `agent_profile/`, và **không** sửa một byte nào trong scratchpad nguồn. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

**Pin của card không bị ảnh hưởng:** gói này không chạm `precode/baseline.json`, nên giá trị W7 cần pin vẫn là `e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` (97620). Nhưng `precode/README.md` **có** đổi — card nào pin file đó phải lấy `44c36fba…` (15292).

## I5. Evidence

- **Chép và kiểm:** `cp -p` cho 37 file, sau đó `cmp` từng cặp; chạy hai lần (ngay sau khi chép, và trước handoff). **37/37 byte-identical cả hai lần.** SHA-256 nguồn được ghi lại trước khi chép (`src_audits.sha`, `src_coord.sha` trong scratch dir).
- **`validate.py`:** `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` → **exit code 0**, **202 assertion, 202 PASS, 0 FAIL**, chạy lúc 2026-09-07T02:36Z. Không assertion nào đổi ở gói này — gói packaging không chạm file mà `EV-PC00-01..07` kiểm; chạy lại để chứng minh **không có hồi quy**.
- Toàn bộ là `SELF_VALIDATION`, producer `worker-W1`.
- **`NOT_RUN`:** không có audit độc lập nào cho chính thư mục vừa tạo; E1–E4 vẫn `NOT_RUN`. Việc hai bản sao giống nguồn **không** chứng minh nội dung của chúng đúng — nó chỉ chứng minh chúng chưa bị sửa.

## I6. Unresolved

Gói này không phát sinh CR mới. Còn mở từ trước: `CR-PC00-15` (W7 re-pin 18 card; nay thêm `precode/README.md`), `CR-PC00-13` (`REQ-S8.4-01` là bản ghi lịch sử trong `requirements.csv`, khuyên để nguyên), `CR-PC00-06` (anchor ≠ scenario đã có fixture), `PROV-PC00-01` (phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`).

**Một quan sát cho Coordinator.** Thư mục `evidence/coordination/` giữ chính những packet đã cấp quyền ghi cho các Worker, trong đó có tôi. Đặt chúng vào repo làm chuỗi thẩm quyền kiểm lại được — nhưng cũng nên nói rõ: chúng là **bản ghi** của grant, không phải grant còn hiệu lực. Mọi lease trong đó đã được nhả, và không file nào ở đây cấp cho ai quyền ghi gì. README của thư mục đã nêu điều này.

## I7. Trạng thái bàn giao (FIX9)

- **next actor:** `Coordinator` — rehash `precode/README.md` và hai README mới; nếu muốn, đưa `evidence/audits/` và `evidence/coordination/` vào epoch kế tiếp với role `EVIDENCE`.
- **lease_released_at (UTC):** 2026-09-07T02:38Z. `LEASE-PC00-e10` (fencing 10) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới và lease fencing ≥ 11.
- **Claim:** `DRAFT_FOR_REVIEW`. `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 vẫn `OPEN`; cả bảy báo cáo audit vẫn giữ nguyên finding của chúng.
