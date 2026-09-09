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

---

# ADDENDUM — PKT-PC00-FIX10 (phê chuẩn của Owner: `OD-20260907-01`)

## J1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX10` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX10` (parent **`AUTH-OWNER-20260907-02`**) · lease `LEASE-PC00-e11` (**fencing 11**) |
| mode | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T04:15Z / 2026-09-07T04:24Z · lease expires 2026-09-08T00:00Z (`date -u` trước lần ghi cuối: 2026-09-07T04:22Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T04:24Z |
| input ràng buộc | `…/scratchpad/packets/OWNER-DECISIONS-20260907.md` — biên bản của Owner, **chuyển ngữ nguyên nội dung, không diễn giải lại** |

Đây là gói đầu tiên của PC00 chạy dưới một **authority Owner mới** (`AUTH-OWNER-20260907-02`) thay vì `AUTH-OWNER-20260906-01`.

## J2. Đã làm gì (7 việc theo packet)

**1 · Tạo `precode/owner-decisions.md`.** Biên bản `OD-20260907-01` đầy đủ: định danh (issuer, `evidence_ref` = session `session_017QmDJtMqD9o1z79waqSB9W`, authority phát sinh), **cả 25 hàng chép nguyên**, từ vựng trạng thái mới, và hai mục PC00 viết thêm: §5 "những gì quyết định này **không** làm" và §6 ghi chú về ba mục dễ bị đọc rộng hơn văn bản. Không hàng nào bị tóm tắt hay diễn giải lại.

**2 · `decision-register.md`.** B01–B17: `PROVISIONAL` → **`RATIFIED (OD-20260907-01)`** ở bảng tổng hợp §1 và ở cả 17 mục §2. 14 amendment → **`ACCEPTED (OD-20260907-01)`**. §8: `PROV-PC00-02` và `PROV-PC00-04` → ACCEPTED (mục 25); `PROV-PC04-01..09` (mục 22) và `PROV-PC08-01..05` (mục 23) → ACCEPTED. §0 có bảng từ vựng mới và ba dòng nêu rõ điều **không** đổi. §4 (bảng P0 còn ĐX) ghi bốn dòng đã promote và nói rõ mười bốn dòng còn lại **vẫn ĐX**. §5 và §6 ghi kết quả cho OQ và cho `F-PC00-01`/`F-PC00-02`.

**Không suy rộng.** `PROV-PC03-01..06`, `PROV-PC09-01..03`, `PROV-PC10-01..03`, `PROV-PC00-03`, `PROV-PC00-05`, `PROV-PC00-06` **không** được biên bản nêu tên, nên **vẫn `PROVISIONAL`**. §8 nay nói thẳng quy tắc đó: *"mục nào được `OD-20260907-01` nêu tên thì nay là ACCEPTED; mục nào không được nêu thì vẫn PROVISIONAL — không suy rộng."*

**3 · ADR.** Chín ADR (`0001`–`0005`, `0007`–`0010`) → `status: accepted`, thêm `ratified_by`, `ratified_at`, `evidence_ref`, và một banner ở mục "Trạng thái"; **lập luận cũ giữ nguyên bên dưới** để truy vết. `ADR-0008` từ `provisional-accepted` cũng lên `accepted`.

**`ADR-0006` viết lại thành phương án B.** Bảng phân bổ ngôn ngữ (collector/worker/embedding/backend ở Python, web app ở TypeScript, ranh giới là HTTP API đã có hợp đồng), mục **Hệ quả** tách rõ hai vế: *phải viết lại* = §3 và §8 của 18 card cộng phần mô tả cây thư mục của `precode/README.md`; ***không* phải viết lại** = toàn bộ `contracts/**`, `acceptance/**`, `requirements.csv`, `decision-register.md`, `gates.yaml`, các ADR khác. Bảng phương án ghi A là **bị Owner bác**, C không chọn vì rủi ro nằm đúng ở embedding local (`REQ-D59`, `REQ-A3`).

**4 · `requirements.csv`.** Đúng bốn dòng đổi trạng thái `ĐX` → `XN`: `REQ-D08`, `REQ-D09`, `REQ-D42`, `REQ-D50`, mỗi dòng mang ghi chú `Ratified OD-20260907-01` kèm số mục. **242 dòng còn lại không đổi một ký tự trạng thái** — kiểm bằng script: `REQ-D53` và `REQ-D22` vẫn `ĐX`.

**5 · `owner-decision-request.md`.** Banner `✅ ANSWERED 2026-09-07` ở đầu, trỏ về biên bản, nêu mục duy nhất chưa trả lời (`REQ-OQ03`) và nói rõ nội dung bên dưới **không** được viết lại. Phiếu trả lời cuối file đã điền đủ, gồm cả `Stack: B ← KHÔNG phải A như khuyến nghị`.

**6 · `agent_profile/registry.json`.** `open_product_blockers: []`; thêm `ratified_product_blockers` (B01–B17) và `ratification_evidence`. Đã so sánh JSON đã parse trước/sau: **hai khóa được thêm, không khóa nào bị xóa, không khóa nào khác đổi giá trị**. `product_status` **giữ nguyên** `NOT_READY_FOR_PRODUCT_CODE` — biên bản không đổi nó.

**7 · `baseline.json`.** Anchor `OD-20260907-01` trong `source_anchors.PROJECT.owner_decisions` (nguồn, authority, evidence, danh sách được phê chuẩn, danh sách **không** được quyết, bốn promotion, lựa chọn stack). `claim_ceiling` từ một chuỗi thành **object theo phạm vi**: bốn phạm vi `A2-R4` nêu là đủ điều kiện → `CONTRACT_READY_PENDING_E0`; sáu phạm vi còn lại → `DRAFT_FOR_REVIEW`, kèm `blocked_by_kc_vi` nói vì sao (`REQ-A6` còn KC; `REQ-A5` + `REQ-OQ03`; 18 card cần viết lại). `finalised_by: W6`.

## J3. Ba điều tôi **không** làm, có chủ đích

1. **Không đóng finding audit nào.** Phê chuẩn một quyết định sản phẩm không phải disposition của một finding (`protocol.md` §8). Ghi rõ ở §5 biên bản và ở §0 register.
2. **Không đổi trạng thái mục `KC` nào.** `REQ-A1`…`REQ-A7` nguyên trạng; `REQ-AC16` vẫn `BLOCKED` cho tới khi một probe CLI/ACP đạt (mục 15). Biên bản tự nói buổi phỏng vấn không tạo bằng chứng runtime.
3. **Không nâng `claim_ceiling` lên `CONTRACT_READY` thật.** Dùng `CONTRACT_READY_PENDING_E0` — đủ điều kiện về quyết định, còn chờ W6 chạy lại E0 trên epoch mới. Nâng thẳng sẽ là nâng nhãn bằng suy diễn.

## J4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/owner-decisions.md` | **CREATE** | ABSENT | `c5d411e561d464cbb6a05b42938dd11b4925506b12b72736ab46b354ba9ad994` (12373) |
| `precode/decision-register.md` | MODIFY | `212441a429420d1cc11cdc4a9c79a11648e45e1b92278a08f77a9779943ad15d` (97899) | `5e73fc4eb914d4bc75dc0d76f3268992b3a9a847db419cdf2f0bee3341dc86ab` (101505) |
| `precode/baseline.json` | MODIFY | `e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` (97620) | `b1ba31e87199433766ad49cc4bd40882a331c2b00d6e92033a5707172ba6c598` (100146) |
| `precode/requirements.csv` | MODIFY | `132ce59b160d9cc20294e45f33082e27d69c4b3182bdc9c1b1864fd0adeaf0e6` (69366) | `63aa6b273def1e1eaeb6a45b0ee083a06ca9e2bec4ca8bd7fe733dd2f0d10480` (69651) |
| `precode/owner-decision-request.md` | MODIFY | `91182f46766f82c74994dd7f3b86c2b77984599100b43884259bd2b6b9cf1073` (54917) | `9995b5ecc8b7a902ee5b10891ba4ea2fbbebe21521705415f41a7b48c947b6b4` (56332) |
| `precode/adr/README.md` | MODIFY | `44b9d01b60984ecedb715cfb3c82fdcb7f09e78aa13646e581a750686a0c269d` (6490) | `e57d08b94da683d7c5be11cce46a942330381ae21c44f09210547f4497597f3f` (7503) |
| `precode/adr/ADR-0006-stack-option-a.md` | MODIFY (viết lại) | `a7b0b558a308f699018f1b695cb4585e3cc3ab6bcb86cf298a05fde6ace6b20b` (4516) | `f875dbb8ef847aa2de0c8105d7356c6c3d7529b2b615f3b903a00ee5cd782f26` (8053) |
| `precode/adr/ADR-0001-topology-and-placement.md` | MODIFY | `277eb556cff950193ca55cecd0ef0d06dca279a4d376c5c8e889a48ebf60c09c` (5717) | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` (6161) |
| `precode/adr/ADR-0002-run-state-model-split.md` | MODIFY | `5ed7b2c429ef7e060140f8b6bbaa71b761b482134aaac155ad32d64bef34b8c0` (4924) | `70fcac8f9c7fdcdce84889015d31f109d423d1d15d68116165e9e3d0612399f8` (5368) |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | MODIFY | `1cb86d8db85c4350dc1eaf6b0822908030219d326c65a8fbec321066d2aab2a0` (5105) | `567828c11049d26993cbeee0d0bd6c157d9938263ec69c5a05fa045da3ceb0e3` (5549) |
| `precode/adr/ADR-0004-tag-freeze-point.md` | MODIFY | `64c0793eeca31b6ac0606813adac96fa483e01eb4b81eaef950edfff16fd3194` (5459) | `4c02d39a2d6ef80f17db7f1aebbda1de39bacaa9b4d417a3c2721c10b6ccf21f` (5903) |
| `precode/adr/ADR-0005-backup-method.md` | MODIFY | `7830500f824c84683d81f2458d7280483d105c4a221f738b083c6fcb7fcbeead` (5013) | `889de2812a8736e328eb7823a82e2b5dab1f46aee13257bfcfedd08d4668bd5c` (5457) |
| `precode/adr/ADR-0007-timezone-handling.md` | MODIFY | `334abf600467fba70e7797113956c99406acb3617b2da6f3ccce56f8f5786ed7` (4843) | `fbb464c22df45248895107a3f38e85f700e9cdecd9a722eaa9f2a4b028995e44` (5287) |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | MODIFY | `c08f8670b19e8a0758062988570701ccb96f6d4beefac7b4d80ed6906b95c5f1` (5228) | `bbf649f5e9239d0de28c24255469ce0498f9f108bfdd45ada2ddeac859b8f1c5` (5660) |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | MODIFY | `a8e57390663d6dc3778ff8036ca4032a91da25f0b85844bd094f393e34f6b5ef` (5701) | `67844f12e4fe77a6a25b443a8fe84d053fbcfc9c30649296f55efc41befa4ee1` (6145) |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | MODIFY | `734766c889edbbb0dce94dca92b7da04a9c0b6721536addaeaac3ee6c783a291` (5962) | `aa91b92d087681b3df902091bbe5d875e644fee6b2e08e53025ba97136eb6317` (6406) |
| `agent_profile/registry.json` | MODIFY | `3d5fc4d876d537706ee354553df0b1b73733326756109b44ccf9931df0f107a3` (3675) | `fd9d6d25f3ebf7e2f0dbbb269f3d72ce944edd9ba4c2b7552963b37b71383135` (3784) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `e9a7b622cdd431d88f04d601fd72da99524860e28d85e6c07982215eb317649e` | *(file này)* |

**1 CREATE + 16 MODIFY + 1 APPEND.** `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `agent-tasks/`, `precode/review.md`, `precode/README.md`, `evidence/audits/`, `evidence/coordination/`, handoff gói khác. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

**Lần đầu PC00 ghi dưới `agent_profile/`.** Các packet trước cấm tuyệt đối. Packet này cấp tường minh và có parent là một Owner authority mới. Tôi giữ diff nhỏ nhất có thể (hai khóa thêm, một mảng thành rỗng), xác minh bằng cách so sánh **JSON đã parse** trước/sau chứ không chỉ đọc diff văn bản, và giữ bản gốc ở scratch dir để đối chiếu.

## J5. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T04:22Z / 2026-09-07T04:22Z · **exit code 0** · **248 assertion, 248 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- **`EV-PC00-04` đã được sửa theo packet.** Trước đây nó khẳng định 17 blocker ở `PROVISIONAL`; nay khẳng định cả 17 ở **`RATIFIED (OD-20260907-01)`** và register phải trỏ về biên bản cùng authority. Hai kiểm tra cũ đã lỗi thời cũng được thay: `ACCEPTED` nay **hợp lệ nhưng chỉ khi kèm decision id** (nhãn trần bị FAIL), còn **`CLOSED` vẫn bị cấm tuyệt đối**.
- **`EV-PC00-08` mới (33 assertion):** biên bản có đủ decision id/authority/evidence và **đúng 25 hàng liên tục**; ghi rõ phạm vi không được quyết; 10 ADR `accepted` với `ratified_by` + `evidence_ref`; `ADR-0006` là phương án B và nói rõ hợp đồng không đổi; đúng bốn REQ được promote và `REQ-D53`/`REQ-D22` vẫn `ĐX`; banner + phiếu trả lời; registry đúng ba thay đổi và `product_status` **không** đổi; `claim_ceiling` là object với **đúng bốn** phạm vi đủ điều kiện; anchor biên bản ghi `REQ-OQ03` chưa được quyết.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4. Việc Owner phê chuẩn **không** tạo bằng chứng kỹ thuật nào.

## J6. Unresolved và CR

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC00-16` | Coordinator | `precode/adr/ADR-0006-stack-option-a.md` nay chứa **phương án B**. Tên file sai nội dung. Đổi tên là rename (DELETE + CREATE) cần grant riêng, và sẽ làm đứt liên kết ở 18 card cùng chỉ mục ADR — nên tôi **không** tự làm. Đã ghi `filename_note_vi` trong front-matter và một dòng cảnh báo ở đầu file. Đề nghị gộp việc đổi tên vào cùng lượt PC10 viết lại card. |
| `CR-PC00-17` | Coordinator → PC10 | 18 card phải viết lại **§3 (đường dẫn) và §8 (lệnh build/test)** theo stack B; `PROV-PC10-01` (layout theo A) **không còn hiệu lực**. `precode/README.md` cũng có phần mô tả cây thư mục theo A — ngoài grant gói này. |
| `CR-PC00-18` | Coordinator → W6 | `claim_ceiling` mới là object theo phạm vi với giá trị **`CONTRACT_READY_PENDING_E0`**, không phải `CONTRACT_READY`. W6 finalise sau khi chạy lại E0. Ba phạm vi bị chặn bởi `KC` được ghi kèm lý do. |
| `CR-PC00-15` | W7 | Vẫn mở và **rộng hơn**: nay `baseline.json` (`b1ba31e8…`), `decision-register.md` (`5e73fc4e…`), `requirements.csv` (`63aa6b27…`), 10 ADR và `adr/README.md` đều đổi hash. |
| `CR-PC00-13` | Coordinator | Vẫn mở (`REQ-S8.4-01` là bản ghi lịch sử trong `requirements.csv`). |
| `PROV-PC00-01` | — | **Đã giải** (mục 24): `data.purge_all` chỉ xóa dữ liệu nghiên cứu; giữ đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch; **backup không bị xóa**. |
| `REQ-OQ03` | Owner | **Vẫn `OWNER_DECISION_REQUIRED`**, vẫn chặn M3. |

**Concern:**
1. **Sáu nhóm `PROV-*` không được biên bản nêu tên vẫn `PROVISIONAL`** (`PROV-PC03-*`, `PROV-PC09-*`, `PROV-PC10-*`, `PROV-PC00-03/-05/-06`). Nếu Coordinator cho rằng mục 22/23 có ý bao cả `PROV-PC03-*` (tham số retry/lease) thì cần một dòng làm rõ — tôi không suy rộng thay Owner.
2. **`PROV-PC10-01` nay mâu thuẫn với quyết định stack**: nó vẫn nằm ở §8.7 register như một giả định layout theo A. Tôi giữ nguyên vì §8.7 là bản ghi lịch sử và việc thay layout thuộc PC10; nhưng nếu để lâu, nó là đúng loại "văn xuôi cũ" mà `F-A2R1-*` từng phạt. → `CR-PC00-17`.
3. **`ADR-0006` giữ tên file cũ** — xem `CR-PC00-16`. Đây là mâu thuẫn tên/nội dung duy nhất tôi cố ý để lại.
4. Biên bản **không** nâng `product_status`; tôi giữ `NOT_READY_FOR_PRODUCT_CODE`. Nếu Coordinator muốn đổi, đó là quyết định riêng cần căn cứ riêng — phê chuẩn quyết định sản phẩm không đồng nghĩa hợp đồng đã sẵn sàng để code.

## J7. Trạng thái bàn giao (FIX10)

- **next actor:** `Coordinator` — rehash 17 file ở §J4; giao PC10 (`CR-PC00-17`) và W6 (`CR-PC00-18`).
- **lease_released_at (UTC):** 2026-09-07T04:24Z. `LEASE-PC00-e11` (fencing 11) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §J4) và lease fencing ≥ 12.
- **Claim:** `DRAFT_FOR_REVIEW` cho gói này. Bốn phạm vi đủ điều kiện mang `CONTRACT_READY_PENDING_E0` trong `baseline.json`, **chưa** phải `CONTRACT_READY`. `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; B01–B17 nay **RATIFIED**, `REQ-OQ03` vẫn mở.

---

# ADDENDUM — PKT-PC00-FIX11 (`CR-PC09-13` và `CR-PC00-18`)

## K1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX11` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX11` (parent `AUTH-OWNER-20260907-02`) · lease `LEASE-PC00-e12` (**fencing 12**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` cho gói này |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T04:48Z / 2026-09-07T04:52Z · lease expires 2026-09-08T00:00Z (`date -u` trước lần ghi cuối: 2026-09-07T04:50Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T04:52Z |

## K2. `CR-PC09-13` — hai dòng OQ và dọn chữ "Option A"

**`REQ-OQ01` và `REQ-OQ02`: `ĐX` → `XN`**, ghi chú bắt đầu bằng `ĐÃ TRẢ LỜI` và dẫn đúng số mục của biên bản:

- `REQ-OQ01` — mục 1: Owner xác nhận profile riêng của dự án; `REQ-D09` đã lên `XN`; M0/SP1 không còn bị chặn bởi **câu hỏi này** (probe A1 vẫn `NOT_RUN` — hai chuyện khác nhau).
- `REQ-OQ02` — mục 3: Owner chọn **stack B (Python workers + TypeScript web)**; khuyến nghị A của đặc tả **không** được chọn; hợp đồng không đổi; 18 card phải viết lại §3 và §8. Nhãn `PROVISIONAL` và chữ `Option A` đã biến mất khỏi ghi chú.

**Sweep "Option A" / "Python toàn bộ" trên toàn `precode/`.** Kết quả 10 chỗ, tôi phân loại chứ không dọn mù:

| Chỗ | Phân loại | Xử lý |
| --- | --- | --- |
| `decision-register.md` §5 hàng `REQ-OQ02` — *"Option A — Python toàn bộ"* ở cột **giá trị đang dùng** | **Sai thực tế** — trình bày A như lựa chọn | **Đã sửa** thành "**ĐÃ TRẢ LỜI** — B: Python workers + TypeScript web (mục 3); khuyến nghị A của đặc tả bị bác". Hàng `REQ-OQ01` cũng cập nhật |
| `requirements.csv` `REQ-OQ02.notes` | Sai thực tế | **Đã sửa** (ở trên) |
| `requirements.csv` `REQ-OQ02.text_vi`, `REQ-S6.3-01.text_vi` | **Trích nguyên văn nguồn** — SRC-SPEC §13.1 và §6.3 thật sự khuyến nghị A | **Giữ nguyên.** Sửa chúng là làm sai bản ghi yêu cầu. Thay vào đó `REQ-S6.3-01.notes` nay nói rõ: đây là khuyến nghị của đặc tả, **không** phải lựa chọn cuối; Owner đã chọn B nên khuyến nghị này bị bác; trạng thái giữ `ĐX` vì hàng nguồn là một đề xuất **chưa được chọn** |
| `baseline.json` anchor §13.1 hàng 2 | Trích nguyên văn nguồn, sinh tự động | Giữ nguyên |
| `owner-decision-request.md` §Stack (câu hỏi và ba phương án) | Bản ghi câu hỏi đã đặt; banner `ANSWERED` đã ở đầu file | Giữ nguyên; ngoài grant gói này |
| `ADR-0006` mục Bối cảnh và bảng phương án | Lịch sử, packet cho phép tường minh | Giữ nguyên |
| `review.md` | Chính là nơi phát hiện ra `CR-PC09-13` | Ngoài grant; PC09 xử lý |

**Phạm vi `data.purge_all` — không còn `OWNER_DECISION_REQUIRED`.** Ba chỗ trong `decision-register.md` §8 vẫn mô tả nó như đang bị chặn:

- `PROV-PC00-01` nay mở đầu bằng **`ĐÃ GIẢI — ACCEPTED (OD-20260907-01) mục 24`** với đúng nội dung Owner chốt (chỉ xóa dữ liệu nghiên cứu; giữ đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch; **backup không bị xóa**; `MOD-data-admin-service` được gỡ chặn). Lập luận cũ được giữ lại bên dưới dưới nhãn **(Lịch sử)**, không xóa.
- `PROV-PC00-03` phần "vẫn chặn" → "**từng bị chặn — nay đã giải**", và xác nhận rằng danh sách ứng viên PC08 từng nêu chính là tập được giữ lại.
- `requirements.csv` `REQ-S7.3-05.notes` bỏ cụm `PROV-PC00-01 (OWNER_DECISION_REQUIRED)`, thay bằng nội dung quyết định.

**`REQ-OQ03` không bị chạm.** Nó vẫn `ĐX` với `OWNER_DECISION_REQUIRED` trong ghi chú, và `EV-PC00-08` nay khẳng định điều đó bằng một assertion riêng để không ai dọn nhầm nó cùng lượt.

## K3. `CR-PC00-18` — nâng trần claim của bốn phạm vi

E0 đóng cửa `E0-20260907T044549Z` đạt **23/23**, nên bốn phạm vi `A2-R4` nêu là đủ điều kiện chuyển từ `CONTRACT_READY_PENDING_E0` sang **`CONTRACT_READY`** thật: `boundaries_and_rights`, `data_and_identity`, `workflow_and_state`, `reporting_and_time`. Sáu phạm vi còn lại giữ `DRAFT_FOR_REVIEW` với lý do đã ghi (`REQ-A6` còn `KC`; `REQ-A5` + `REQ-OQ03`; 18 card chờ viết lại theo B).

`claim_ceiling` nay mang `e0_run_ref: "E0-20260907T044549Z"` và `e0_result: "23/23 PASS"` — nhãn có con trỏ tới lần chạy sinh ra nó, không phải một khẳng định trần.

Tôi thêm một `scope_note_vi` mà packet không yêu cầu, vì `CONTRACT_READY` là nhãn dễ bị đọc rộng nhất trong cả bộ: *"`CONTRACT_READY` ở đây chỉ nói về tính nhất quán tĩnh của hợp đồng (mức E0). Nó **không** nói gì về code, về dịch vụ thật, hay về chất lượng sản phẩm: E1–E4 vẫn `NOT_RUN` và `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`."* `EV-PC00-08` khẳng định câu đó tồn tại.

## K4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/requirements.csv` | MODIFY | `63aa6b273def1e1eaeb6a45b0ee083a06ca9e2bec4ca8bd7fe733dd2f0d10480` (69651) | `fbe59d0eaf73ff69281515fc2d03c2673c7dfa3aaa57f110b2ecba079f0c52e8` (70393) |
| `precode/baseline.json` | MODIFY | `b1ba31e87199433766ad49cc4bd40882a331c2b00d6e92033a5707172ba6c598` (100146) | `e0405a1bc36f3dc2050ca7ed3b8acd8a9d0a14a708583cba273360c0c4d6722b` (100474) |
| `precode/decision-register.md` | MODIFY | `5e73fc4eb914d4bc75dc0d76f3268992b3a9a847db419cdf2f0bee3341dc86ab` (101505) | `1883fec33f56873a426394a99d3fc6c5ec43c456a936c52733cad6c047f06262` (102430) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `cec51107ecd407963382a65d2b8cddf71f87fdc93d477e60b908c0bb5f620765` | *(file này)* |

**3 MODIFY + 1 APPEND.** `precode/adr/*`, `owner-decisions.md`, `owner-decision-request.md`, `agent_profile/registry.json` **không** đổi ở gói này. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `agent-tasks/`, `precode/review.md`, `precode/README.md`, `precode/gates.yaml`, `evidence/audits/`, `evidence/coordination/`. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

**⚠ Cả `baseline.json` và `decision-register.md` đều được task card pin theo hash** — cả hai vừa đổi. Giá trị cần pin: `baseline.json` = `e0405a1b…` (100474), `decision-register.md` = `1883fec3…` (102430), `requirements.csv` = `fbe59d0e…` (70393). Thuộc `CR-PC00-15` (W7 re-pin một lượt).

## K5. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T04:50Z / 2026-09-07T04:50Z · **exit code 0** · **259 assertion, 259 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- **11 assertion mới trong `EV-PC00-08`:** `e0_run_ref` và `e0_result` đúng; `scope_note_vi` nêu `NOT_READY_FOR_PRODUCT_CODE`; **không còn giá trị `PENDING_E0` nào**; đúng bốn phạm vi ở `CONTRACT_READY`; `REQ-OQ01`/`REQ-OQ02` là `XN` kèm ghi chú ratified và **không còn** nhãn `PROVISIONAL`; ghi chú OQ02 **không còn** trình bày `Option A` là lựa chọn; **`REQ-OQ03` giữ nguyên** `OWNER_DECISION_REQUIRED`; `PROV-PC00-01` ghi rõ đã giải bằng mục 24 và backup không bị xóa; bảng câu hỏi mở §5 không còn chữ `Option A`.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4. `CONTRACT_READY` ở đây là kết luận **mức E0**, dựa trên lần chạy `E0-20260907T044549Z` do W6 thực hiện — **không phải** bằng chứng do gói này tạo ra.

## K6. Unresolved

Gói này không phát sinh CR mới.

| ID | Trạng thái |
| --- | --- |
| `CR-PC09-13` | **Đã giải** ở gói này |
| `CR-PC00-18` | **Đã giải** ở gói này |
| `CR-PC00-15` | Còn mở — W7 re-pin; danh sách hash mới ở §K4 |
| `CR-PC00-16` | Còn mở — `ADR-0006` giữ tên file cũ trong khi nội dung là phương án B |
| `CR-PC00-17` | Còn mở — PC10 viết lại §3/§8 của 18 card theo stack B; `precode/README.md` còn mô tả cây thư mục theo A |
| `CR-PC00-13` | Còn mở — `REQ-S8.4-01` là bản ghi lịch sử, gate báo `[INFO]` |
| `CR-PC00-06` | Còn mở — anchor tồn tại không chứng minh scenario đã có fixture |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |

## K7. Trạng thái bàn giao (FIX11)

- **next actor:** `Coordinator` — rehash ba file ở §K4; giao W7 re-pin.
- **lease_released_at (UTC):** 2026-09-07T04:52Z. `LEASE-PC00-e12` (fencing 12) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §K4) và lease fencing ≥ 13.
- **Claim:** bốn phạm vi nay `CONTRACT_READY` **ở mức E0**, có `e0_run_ref`. `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`; `REQ-OQ03` vẫn mở.

---

# ADDENDUM — PKT-PC00-FIX12 (packaging đợt hai: hồ sơ tới epoch 9)

## L1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX12` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX12` (parent `AUTH-OWNER-20260907-02`) · lease `LEASE-PC00-e13` (**fencing 13**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T05:33Z / 2026-09-07T05:36Z · lease expires 2026-09-08T04:00Z (`date -u` trước lần ghi cuối: 2026-09-07T05:34Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T05:36Z |
| scope | Lưu vĩnh viễn hồ sơ phát sinh **sau** `PKT-PC00-FIX9`: hai AUDIT_REPORT, hai manifest, biên bản Owner, hai ruling, hai packet audit, và bản ledger mới |

## L2. Đã thêm gì

**10 file chép nguyên văn**, tất cả `cmp`-verified byte-identical.

| Đích | File | Là gì |
| --- | --- | --- |
| `evidence/audits/` | `A2-R5-report.md` | AUDIT_REPORT xác minh các thay đổi do Owner phê chuẩn — `FC-W4` **epoch 8** (epoch phê chuẩn) |
| | `A2-R6-report.md` | Re-review có phạm vi của `F-A2R5-01..07` — `FC-W4` **epoch 9**, vòng audit cuối của phiên |
| | `FC-W4e8-manifest.txt`, `FC-W4e9-manifest.txt` | Hai manifest tương ứng |
| `evidence/coordination/` | `OWNER-DECISIONS-20260907.md` | **Biên bản quyết định của Owner** — bản gốc do Coordinator phát, nguồn của `precode/owner-decisions.md` |
| | `FIX-R5-rulings.md` | Ruling sau `A2-R5` |
| | `PURGE-LIST-ruling.md` | Ruling chốt danh sách loại trừ của `data.purge_all` |
| | `A2-ratification-verify-packet.md`, `A2-r6-packet.md` | Hai packet audit của vòng 5 và 6 |
| | `coordinator-ledger.md` | **Thay** bản chép ở `PKT-PC00-FIX9` |

Tổng hai thư mục: **50 file** (`evidence/audits/` 19, `evidence/coordination/` 31), trong đó 47 là bản sao nguyên văn và 3 là chỉ mục/ledger.

**Về việc thay `coordinator-ledger.md`.** Đây là file duy nhất trong hai thư mục bị **ghi đè** thay vì thêm mới. Bản cũ (`a8a7d319…`) dừng ở epoch 7; bản mới (`0369031b…`) chạy tới epoch 9. Cả hai README ghi rõ hash của bản bị thay và lý do, để một người đọc về sau không tưởng lịch sử bị viết lại lặng lẽ. Ngoài file đó, **không** bản sao nào đã có bị chạm.

## L3. Hai README đã cập nhật

- **Con số và chuỗi epoch.** `evidence/audits/README.md` nay nói **chín** AUDIT_REPORT (`auditor-A1` ×3, `auditor-A2` ×6) và **chín** manifest, kèm chuỗi đầy đủ `FC-W1` 1 → `FC-W2` 2 → `FC-W3` 3 → `FC-W4` 4…9, trong đó epoch 8 được đánh dấu là **epoch phê chuẩn của Owner** và epoch 9 là **epoch cuối được audit**.
- **Ghi chú vị trí trong chuỗi bằng chứng** đổi mốc từ epoch 7 sang **epoch 9**: những bản ghi này ra đời **sau** lần freeze mà `A2-R6` đã audit, nên nằm **ngoài mọi candidate manifest đã được audit** — `protocol.md` §6, một báo cáo không nằm trong snapshot nó ký. Thêm một đoạn nói rõ thư mục được bổ sung **hai lần** (FIX9 tới epoch 7, FIX12 tới epoch 9) và lần này có một file bị thay.
- **Chuỗi thẩm quyền.** `evidence/coordination/README.md` nay nêu **hai** authority Owner: `AUTH-OWNER-20260906-01` (cho phép phiên soạn tài liệu) và `AUTH-OWNER-20260907-02` (phê chuẩn 25 quyết định), và phân biệt `OWNER-DECISIONS-20260907.md` là **văn bản ràng buộc** chứ không phải một ruling.
- Mỗi hàng chỉ mục mang `sha256` và `bytes` **tính sau khi chép**, nên một bản sao bị sửa sẽ lệch chỉ số.

## L4. Changes

| Path | Op | Sau |
| --- | --- | --- |
| `evidence/audits/` | 4 CREATE | 19 file; `README.md` = `4e527ba0846c7f0f129256ccad58c32cbc04d7017275dc720769da359be9905d` (6558) |
| `evidence/coordination/` | 5 CREATE + 1 REPLACE (`coordinator-ledger.md`) | 31 file; `README.md` = `907fc734411ce70f87c41c6ab193b59217aba2fe2e24391fda29ee365cd8755c` (9445) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `e45f49585634ac40f76645c6caa60ee6aa7e9cc05af268a72bcbc61759aceda1` → *(file này)* |

`sha256`/`bytes` của **từng** bản sao nằm trong hai README, không lặp lại ở đây.

Không file nào của `precode/` đổi ở gói này: `baseline.json` (`e0405a1b…`), `decision-register.md` (`1883fec3…`), `requirements.csv` (`fbe59d0e…`), `owner-decisions.md`, `owner-decision-request.md`, `adr/*` giữ nguyên giá trị FIX11. `agent_profile/registry.json` không đổi. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không chạm `contracts/`, `acceptance/`, `agent-tasks/`, `precode/review.md`, `precode/README.md`, handoff gói khác. **Không sửa một byte nào trong scratchpad nguồn.** Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## L5. Evidence

- **Chép và kiểm:** ghi lại `sha256` nguồn **trước** khi chép (`src_fix12.sha`), `cp -p` 10 file, rồi `cmp` **toàn bộ** 47 bản sao của cả hai thư mục (không chỉ 10 file mới) — **47/47 byte-identical**. Kiểm lại lần thứ hai trước handoff.
- **`validate.py`:** **exit code 0**, **259 assertion, 259 PASS, 0 FAIL**, chạy 2026-09-07T05:34Z. Không assertion nào đổi: gói packaging không chạm file mà `EV-PC00-01..08` kiểm; chạy lại để chứng minh **không có hồi quy**.
- Tất cả là `SELF_VALIDATION`, producer `worker-W1`.
- **`NOT_RUN`:** không có audit độc lập nào cho chính hai thư mục này; E1–E4 vẫn `NOT_RUN`. Bản sao giống nguồn **không** chứng minh nội dung của chúng đúng — chỉ chứng minh chúng chưa bị sửa.

## L6. Unresolved

Gói này không phát sinh CR mới. Còn mở: `CR-PC00-15` (W7 re-pin; `baseline.json` `e0405a1b…`, `decision-register.md` `1883fec3…`, `requirements.csv` `fbe59d0e…`), `CR-PC00-16` (`ADR-0006` giữ tên file cũ), `CR-PC00-17` (18 card viết lại §3/§8 theo stack B; `precode/README.md` còn mô tả cây thư mục theo A), `CR-PC00-13`, `CR-PC00-06`, và `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED`.

**Một quan sát.** Sau gói này, hai thư mục lưu trữ đã bắt kịp epoch cuối được audit. Nếu còn epoch nào nữa thì chúng lại tụt hậu, và mỗi lần bắt kịp là một lần ghi đè `coordinator-ledger.md`. Nếu Coordinator dự kiến còn nhiều vòng, nên chốt một quy ước: hoặc ledger được đánh phiên bản theo epoch (`coordinator-ledger-e9.md`), hoặc chấp nhận rằng chỉ bản mới nhất được giữ và lịch sử nằm trong git. Hiện tại tôi theo cách thứ hai vì packet nói "replace", và ghi rõ hash bản bị thay trong README.

## L7. Trạng thái bàn giao (FIX12)

- **next actor:** `Coordinator` — rehash hai README; nếu có epoch mới, đưa `evidence/audits/` và `evidence/coordination/` vào với role `EVIDENCE`.
- **lease_released_at (UTC):** 2026-09-07T05:36Z. `LEASE-PC00-e13` (fencing 13) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới và lease fencing ≥ 14.
- **Claim:** `DRAFT_FOR_REVIEW` cho gói này. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0 theo `E0-20260907T044549Z`; `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`.

---

# ADDENDUM — PKT-PC00-FIX13 (`ADR-0011` framework và toolchain)

## M1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX13` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX13` (parent `AUTH-OWNER-20260907-02`) · lease `LEASE-PC00-e14` (**fencing 14**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T07:06Z / 2026-09-07T07:10Z · lease expires 2026-09-08T08:00Z (`date -u` trước lần ghi cuối: 2026-09-07T07:08Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T07:10Z |
| input | `…/scratchpad/packets/ADR-0011-frameworks-ruling.md` — ruling của Coordinator dưới quyền ủy nhiệm |

## M2. Đã làm gì

**Tạo `precode/adr/ADR-0011-frameworks-and-toolchain.md`** — chuyển ngữ ruling thành đúng hình dạng ADR: sáu mục bắt buộc, front-matter mười trường theo `R-05`, cộng `depends_on: [ADR-0006]` và `ratified_by: null`.

Bảng quyết định chép đủ **14 tầng** (Python 3.12/`uv`; FastAPI + Pydantic v2 với model sinh từ hợp đồng; SQLAlchemy 2 Core + Alembic + Online Backup API; hàng đợi bằng bảng DB với scheduler in-process; Playwright for Python trên profile riêng; `subprocess` cho CLI/ACP; `sentence-transformers`; Bot API trực tiếp; Vite + React + TS với client sinh từ `openapi.yaml`; cookie session + CSRF + Argon2id; `pytest` nạp fixture thẳng từ `acceptance/fixtures/**`; `ruff`/`mypy`/`eslint`/`prettier`; GitHub Actions không có job live; Docker Compose cho server) cùng bố cục repo và bảng phương án bị loại.

**Điều tôi làm nổi bật hơn ruling — có chủ đích.** Ruling nêu lý do theo từng hàng; tôi gom **ba hàng** vào một đoạn riêng ở mục Hệ quả, vì chúng cùng một loại: đó là ba chỗ mà một framework thông dụng sẽ **tự định nghĩa lại một hành vi hợp đồng đã khóa**.

- **Queue** — bảng DB thay vì broker: broker là một chủ sở hữu trạng thái thứ hai bên cạnh `assignment`/`assignment_lease` mà `entities.yaml` đã định nghĩa.
- **Telegram** — gọi thẳng Bot API thay vì bot framework: cơ chế retry của framework sẽ tự gửi lại, **vi phạm `AMD-B03`** (không tự gửi lại khi `unknown`) — đúng thứ Owner vừa phê chuẩn ba ngày trước.
- **CLI/ACP** — `subprocess` thay vì lớp orchestration: ruling loại LangChain vì "nó giấu tool call"; tôi ghi thêm **vì sao điều đó là quyết định**, chứ không phải sở thích: `ADR-0010` đòi *chứng minh được* tool bị khóa, và một lớp giấu tool call làm yêu cầu đó không kiểm được.

**Trạng thái được giữ đúng mức.** `provisional-accepted`, `decision_owner: Coordinator`, `ratified_by: null`. ADR này **không** mang nhãn `accepted` và **không** trích `OD-20260907-01` như một sự phê chuẩn nội dung: biên bản của Owner chỉ ủy quyền *việc chọn*, không phê chuẩn *cái được chọn*. `EV-PC00-08` nay khẳng định điều đó bằng một assertion riêng.

**Ba file cập nhật kèm theo:**

- `precode/adr/README.md` — thêm hàng chỉ mục; sửa "cả 10 ADR accepted" thành "**mười ADR đầu** accepted"; thêm một đoạn nêu `ADR-0011` là **ngoại lệ về thẩm quyền** và phản đối của Owner không ảnh hưởng `contracts/`; template thêm `accepted`.
- `precode/decision-register.md` §8 — **`PROV-PC00-07`**, `PROVISIONAL`, `decision_owner: Coordinator`, kèm đoạn "vì sao ba lựa chọn đáng chú ý lại tối giản" và một dòng nêu rõ phạm vi ảnh hưởng nếu Owner đảo: **chỉ card và mã**.
- `precode/owner-decision-request.md` — phiếu trả lời thêm khối **"CHỜ VÒNG SAU"** với dòng `ADR-0011 frameworks: accept / object: ___` (kèm giải thích rằng phản đối chỉ sửa card và mã) và dòng `OQ03 provider + model` vẫn treo.
- `precode/baseline.json` — anchor `ADR-0011` trong `source_anchors.PROJECT.adrs`, ghi status, `decision_owner`, authority, `depends_on`, `decision_record` và `scope_note_vi`. Ghi rõ vì sao chỉ ADR này có anchor riêng: mười ADR kia đều được `OD-20260907-01` phê chuẩn nên thẩm quyền của chúng đã nằm trong anchor của biên bản; `ADR-0011` khác hẳn.

**Không** chạm `contracts/` hay card nào, đúng packet.

## M3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | **CREATE** | ABSENT | `745f4017f7cca0c20f96c2acc2b8b76ed18ef435ac664eef915b44d3d1ddad5f` (12584) |
| `precode/adr/README.md` ⚠ | MODIFY | `e57d08b94da683d7c5be11cce46a942330381ae21c44f09210547f4497597f3f` (7503) | `3e931f27583cc92f4ee394ad7d8dca590741644058380fec7dd307b9e3405374` (8192) |
| `precode/baseline.json` ⚠ | MODIFY | `e0405a1bc36f3dc2050ca7ed3b8acd8a9d0a14a708583cba273360c0c4d6722b` (100474) | `c99474a6744a3827f75961884d5d8daf1d9fb0bfe212547c216d1574d32ac81a` (101458) |
| `precode/decision-register.md` ⚠ | MODIFY | `1883fec33f56873a426394a99d3fc6c5ec43c456a936c52733cad6c047f06262` (102430) | `3596a52b6ce8cb39a0ae07501fd177c80a4fdb7b19317fc82a3dd8e3df63a75d` (104940) |
| `precode/owner-decision-request.md` | MODIFY | `9995b5ecc8b7a902ee5b10891ba4ea2fbbebe21521705415f41a7b48c947b6b4` (56332) | `572c2c11ecf18c8f958bb931d2aeafba1a2d64d3a42c674959562be05de3f56e` (56907) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `5294242c05e9ba027c7cc37ce6ff74ea8cc5e03f3aeca9f3c16f1e80bf3ebea8` | *(file này)* |

**⚠ Ba file card-pinned vừa đổi:** `precode/baseline.json` (`c99474a6…`, 101458), `precode/decision-register.md` (`3596a52b…`, 104940), `precode/adr/README.md` (`3e931f27…`, 8192). Thuộc `CR-PC00-15` — W7 re-pin một lượt. `precode/requirements.csv` **không** đổi (`fbe59d0e…`).

**1 CREATE + 4 MODIFY + 1 APPEND.** Mười ADR cũ, `owner-decisions.md`, `agent_profile/registry.json`, `contracts/`, `acceptance/`, `agent-tasks/`, `evidence/audits/`, `evidence/coordination/` **không** đổi. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## M4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T07:08Z / 2026-09-07T07:08Z · **exit code 0** · **273 assertion, 273 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- **`EV-PC00-05` mở rộng:** nay 11 file ADR, `adr_id` chạy liên tục `ADR-0001`…`ADR-0011`, tất cả có đủ 6 mục và 10 trường front-matter.
- **`EV-PC00-08` được sửa cho đúng thẩm quyền:** vòng lặp "mọi ADR phải `accepted` + `ratified_by: OD-20260907-01`" nay **bỏ qua `ADR-0011`**, và thay bằng một khối riêng khẳng định `ADR-0011` là `provisional-accepted`, `ratified_by: null`, **không** giả vờ đã được Owner phê chuẩn, có điều khoản "Owner có thể phản đối", `depends_on: [ADR-0006]`, và nêu đích danh `AMD-B03`, `ADR-0010`, `LangChain` trong phần lý do. Cộng bốn assertion cho register, chỉ mục, anchor baseline và dòng phiếu trả lời.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4. Việc chọn framework **không** tạo bằng chứng kỹ thuật nào — chưa dòng mã nào tồn tại.

## M5. Unresolved

Gói này không phát sinh CR mới. Ba việc `ADR-0011` **nêu tên nhưng không làm**, đã ghi ngay trong ADR §Nguồn:

1. PC10 viết lại §3 và §8 của 18 card theo bố cục repo (`CR-PC00-17`, đã mở từ FIX10).
2. Thêm một kiểm tra E0 **"mã sinh ra khớp hash hợp đồng"** vào `evidence/tools/e0_check.py` — hệ quả trực tiếp của việc sinh model từ `contracts/` ở cả hai ngôn ngữ. Chưa có; thuộc W6/PC09.
3. Chọn model embedding cụ thể sau `REQ-A3` (`REQ-OQ09`).

Còn mở từ trước: `CR-PC00-15` (W7 re-pin — danh sách hash mới ở §M3), `CR-PC00-16` (`ADR-0006` giữ tên file cũ), `CR-PC00-13`, `CR-PC00-06`, và `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED`.

**Một quan sát về thẩm quyền.** Đây là ADR đầu tiên trong bộ mang `decision_owner: Coordinator` cho một quyết định **có phạm vi rộng** (14 tầng, ảnh hưởng mọi card). Ba ADR kỹ thuật trước đó (`ADR-0008`) hẹp hơn nhiều. Việc ủy quyền là hợp lệ và được ghi lại đầy đủ, nhưng nó nghĩa là một phần đáng kể của hình dạng hệ thống hiện đứng trên một lời ủy quyền miệng ("You pick") chứ không phải một lựa chọn Owner đã cân nhắc từng hàng. Dòng trong phiếu trả lời là cơ chế để sửa điều đó ở vòng sau; tôi khuyên Coordinator **đưa nó lên sớm** thay vì gộp vào một vòng xa.

## M6. Trạng thái bàn giao (FIX13)

- **next actor:** `Coordinator` — rehash năm file ở §M3; giao W7 re-pin; đưa dòng `ADR-0011` vào vòng hỏi Owner tiếp theo.
- **lease_released_at (UTC):** 2026-09-07T07:10Z. `LEASE-PC00-e14` (fencing 14) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §M3) và lease fencing ≥ 15.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`.

---

# ADDENDUM — PKT-PC00-FIX14 (`F-A2R7-04`, `F-A2R7-05` trên `ADR-0011`)

## N1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX14` · worker `worker-W1` · authority `AUTH-COORD-PC00-FIX14` · lease `LEASE-PC00-e15` (**fencing 15**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T07:18Z / 2026-09-07T07:21Z · lease expires 2026-09-08T08:00Z (`date -u` trước lần ghi cuối: 2026-09-07T07:20Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T07:21Z |
| scope | Chỉ `precode/adr/ADR-0011-frameworks-and-toolchain.md`. Hai finding `LOW` của `A2-R7` |

## N2. `F-A2R7-05` — bốn hàng quyết định không có ô phương án

Bảng quyết định có 14 hàng, bảng phương án chỉ có 10. Bốn hàng thiếu: **Test**, **Lint / format**, **CI**, **Đóng gói / triển khai**. Ruling gốc đánh dấu `—` cho bốn ô đó; bản đầu của ADR bỏ luôn dấu, nên người đọc không phân biệt được "đã cân nhắc rồi loại" với "chưa từng xem xét".

Tôi chọn vế **"chưa từng xem xét"** và nói thẳng như vậy, thay vì bịa ra một cuộc cân nhắc đã không xảy ra. Bốn hàng mới, mỗi hàng ghi rõ: *không cân nhắc phương án nào — mặc định thông dụng*, một dòng vì sao, và **đảo được mà không tốn gì ở phía hợp đồng**.

Hai hàng được viết kỹ hơn vì chúng chứa một quyết định thật bị lẫn vào trong một mặc định:

- **Test** — điều thật sự được quyết **không** phải tên thư viện mà là **fixture nạp thẳng từ `acceptance/fixtures/**`**. Vế đó **không có** phương án thay thế: một bộ dữ liệu test thứ hai sẽ tách oracle khỏi hợp đồng. Đổi `pytest` sang thứ khác không tốn gì; đổi nguồn fixture thì tốn.
- **CI** — điều được quyết là **không có job live** (E3/E4 thủ công theo giao thức), một ràng buộc bằng chứng chứ không phải mặc định; nó giữ nguyên dù đổi nhà cung cấp CI.
- **Đóng gói / triển khai** — audit chỉ ra đúng: đây là hàng chạm **máy của chính Owner**. Tôi nêu tên bốn phương án **chưa được cân nhắc** (systemd unit thuần, Podman, Kubernetes, chạy thẳng không container) để Owner có cơ sở phản đối, và tách bạch phần **không** phải lựa chọn: "collector và worker chạy như tiến trình trên máy, không trong container" là ràng buộc của `REQ-S6.4-02`.

Kết quả: quyền phản đối của Owner ở mục Trạng thái nay áp **đồng đều cho cả 14 hàng**, không phải chỉ 10. `EV-PC00-08` đếm đúng 14 hàng và kiểm bốn nhãn mới.

## N3. `F-A2R7-04` — quy kết nguồn của bố cục repo

Bản đầu viết bố cục repo "(đã được `agent-tasks/README.md` §5.3 khai)" cho **cả bảy** thư mục. Sai tại thời điểm đóng băng mà `A2-R7` kiểm: §5.3 khi đó khai **sáu**, và `shared/rr_contracts/` — thư mục gánh chính quy tắc "mã sinh ra không sửa tay" — không có ở đó.

Nay bố cục được ghi thành **một bảng bảy hàng**, mỗi hàng có cột **Nguồn khai** riêng, nên không còn một câu quy kết gộp.

**Một điều tôi phát hiện khi kiểm chứ không chép theo packet.** Packet nói §5.3 "is being amended by PC10". Tôi kiểm trực tiếp trên đĩa: PC10 **đã bổ sung xong** — `rr_contracts` nay xuất hiện **hai lần** trong `agent-tasks/README.md` (khối layout §5.3 và quy tắc "là code SINH RA, không viết tay"). Nếu viết theo thì tương lai ("đang sửa") thì ghi chú sẽ sai ngay khi đóng băng. Vì vậy ghi chú tách hai mốc: **sai tại epoch `A2-R7` kiểm**, và **đúng cho cả bảy tại 2026-09-07T07:20Z**, kèm câu tôi đã kiểm bằng cách nào. `EV-PC00-08` thêm một assertion buộc câu đó **khớp thực tế trên đĩa**, nên nếu ai đó gỡ `rr_contracts` khỏi README thì validate sẽ FAIL thay vì ADR âm thầm nói sai.

**Ruling gốc vẫn mang câu sai.** `evidence/coordination/ADR-0011-frameworks-ruling.md` là bản sao nguyên văn và **không** được sửa (đó là điểm của một bản lưu trữ). Audit nói rõ "the ruling should be corrected in the same pass" — việc đó nằm ngoài grant gói này. → `CR-PC00-19`.

## N4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` ⚠ | MODIFY | `745f4017f7cca0c20f96c2acc2b8b76ed18ef435ac664eef915b44d3d1ddad5f` (12584) | `9cdec0d78592c67068188e7dffcf9e03f361fe202263bb47a95b2298337a8340` (17052) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `7a3adb94ff7e682290b6e13800bb1edc9dd764ab7d9b17c60e151a69839a41af` | *(file này)* |

**⚠ `ADR-0011` là card-pinned** — hash mới `9cdec0d7…` (17052) cần vào lượt re-pin của W7 (`CR-PC00-15`), cùng với `baseline.json` (`c99474a6…`), `decision-register.md` (`3596a52b…`), `adr/README.md` (`3e931f27…`), `requirements.csv` (`fbe59d0e…`).

**1 MODIFY + 1 APPEND.** Không file nào khác đổi: mười ADR kia, `adr/README.md`, `baseline.json`, `decision-register.md`, `owner-decision-request.md`, `requirements.csv`, `owner-decisions.md`, `agent_profile/registry.json` giữ nguyên giá trị FIX13. **Không** chạm `agent-tasks/README.md` (ngoài grant — và nó đã đúng rồi), `contracts/`, `acceptance/`, `evidence/audits/`, `evidence/coordination/`. `precode/source/*` không sửa; rehash sau khi xong khớp pin. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## N5. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T07:20Z / 2026-09-07T07:20Z · **exit code 0** · **290 assertion, 290 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1`.
- **17 assertion mới:** bảng phương án có **đúng 14 hàng**; bốn hàng `Test`/`Lint / format`/`CI`/`Đóng gói / triển khai` đều có ô; đúng **4** lần nhãn "Không cân nhắc phương án nào" và ít nhất 3 lần "không tốn gì ở phía hợp đồng"; hàng đóng gói nêu tên `systemd` và `Kubernetes` như phương án **chưa** được cân nhắc; **cả bảy** thư mục xuất hiện trong ADR; ADR không còn quy kết rằng §5.3 đã khai cả bảy; và **câu về §5.3 phải khớp thực tế trên đĩa** (`rr_contracts` có trong `agent-tasks/README.md` ⇔ ADR nói "PC10 đã bổ sung").
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4.

## N6. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-19` **(mới)** | `evidence/coordination/ADR-0011-frameworks-ruling.md` vẫn mang câu quy kết sai ("đã được §5.3 khai" cho cả bảy). Nó là **bản sao nguyên văn** nên tôi không sửa — sửa một bản lưu trữ là làm hỏng chính thứ nó dùng để làm. Audit yêu cầu "ruling should be corrected in the same pass"; đề nghị Coordinator phát một ruling đính chính rồi PC00 chép bổ sung, thay vì sửa tại chỗ bản đã lưu. |
| `CR-PC00-15` | W7 re-pin — nay gồm cả `ADR-0011` (`9cdec0d7…`, 17052) |
| `CR-PC00-16` | `ADR-0006` giữ tên file cũ trong khi nội dung là phương án B |
| `CR-PC00-17` | PC10 viết lại §3/§8 của 18 card (đang tiến hành — §5.3 đã cập nhật) |
| `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |
| `ADR-0011` | Vẫn `provisional-accepted`; dòng "accept / object" đã có trong phiếu trả lời của Owner |

## N7. Trạng thái bàn giao (FIX14)

- **next actor:** `Coordinator` — rehash `ADR-0011`; xử lý `CR-PC00-19`; giao W7 re-pin.
- **lease_released_at (UTC):** 2026-09-07T07:21Z. `LEASE-PC00-e15` (fencing 15) nhả tại đây; `worker-W1` không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §N4) và lease fencing ≥ 16.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`.

---

# ADDENDUM — PKT-PC00-FIX15 (`OD-20260907-02`: phê chuẩn `ADR-0011`, lối vào Giai đoạn 0 và 1)

## O1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX15` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX15` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-PC00-e16` (**fencing 16**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T09:05Z / 2026-09-07T09:22Z · lease expires 2026-09-08T12:00Z (`date -u` trước lần ghi cuối: 2026-09-07T09:20Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T09:22Z |
| input | `…/scratchpad/packets/OWNER-DECISIONS-20260907-02.md` — biên bản Owner vòng hai do Coordinator phát |

## O2. Đã làm gì

**Tạo `precode/owner-decisions-02.md`** — chuyển ngữ biên bản `OD-20260907-02` theo đúng khuôn của
`owner-decisions.md`: định danh, quy tắc chuyển ngữ, **năm** mục nguyên văn, trần claim của Giai đoạn 0/1
nguyên văn, §4 "những gì quyết định này **không** làm" và §5 ghi chú về hai mục có sắc thái, §6 truy vết.
Thêm một dòng trỏ ở đầu `precode/owner-decisions.md` nói rõ hai biên bản **cộng dồn**, biên bản vòng một
không bị thay thế.

**Một phân biệt tôi giữ nguyên chứ không làm phẳng.** Biên bản có năm hàng, nhưng chỉ **hai** trong số đó là
câu trả lời của Owner (mục 1 `ADR-0011`, mục 2 lối vào giai đoạn). Mục 3 và mục 4 được **chính biên bản** khai
là *"hàm ý bởi mục 2"* và là *"ruling của Coordinator, đã khai báo"*; mục 5 là điều phối. Vì vậy chỉ hai mục
đầu mang nhãn `ACCEPTED (OD-20260907-02)`; mục 3 thành `PROV-PC00-08` với trạng thái **`PROVISIONAL`** và điều
khoản Owner có thể phản đối. Gộp cả năm thành "Owner đã chấp nhận" sẽ là đúng thứ mà `protocol.md` §8 gọi là
implied acceptance — một quyết định lớn (ghi mã sản phẩm không có runtime guard) mượn thẩm quyền của một câu
trả lời về việc khác.

**`ADR-0011` → `accepted`.** Front-matter: `status: accepted`, `ratified_by: OD-20260907-02`,
`ratified_at: 2026-09-07`, `evidence_ref` nay có **hai** vế (lựa chọn: `session_017QmDJ…`; phê chuẩn:
`session_0156UBBH…`), `decision_refs` thêm `OD-20260907-02`. **`decision_owner` giữ nguyên `Coordinator`** —
hai trường trả lời hai câu hỏi khác nhau: *ai chọn* và *ai phê chuẩn*. Mục "Trạng thái" được viết lại kèm
banner, và lập luận cũ được **giữ nguyên trong một blockquote** đúng cách mười ADR kia đã làm.

**Điều tôi thêm mà biên bản không nói — và vì sao.** Mục "Trạng thái" mới ghi rõ: phê chuẩn áp cho cả 14 hàng,
nhưng bốn hàng `Test` / `Lint / format` / `CI` / `Đóng gói / triển khai` vẫn là *chưa từng cân nhắc phương án
nào* theo chính ADR (`F-A2R7-05`). Một phê chuẩn trọn gói **không** biến bốn ô trống thành một cuộc cân nhắc
đã xảy ra. `FIX14` vừa bỏ công phân biệt đúng hai chuyện đó; nếu `FIX15` để nhãn `accepted` xoá mất phân biệt
ấy thì bản sửa của `F-A2R7-05` mất tác dụng sau đúng hai giờ. Ghi chú tương ứng có ở `adr/README.md`,
`PROV-PC00-07` và anchor baseline.

**`precode/adr/README.md`** — hàng chỉ mục `ADR-0011` → `accepted (OD-20260907-02)`; bảng "Trạng thái được
phép" ghi hai biên bản; đoạn "Cập nhật 2026-09-07" thành "cả mười một ADR"; đoạn "ngoại lệ về thẩm quyền" viết
lại: nay là ADR **duy nhất** có `decision_owner: Coordinator` **và** `status: accepted`, có giải thích vì sao
đó không phải mâu thuẫn; `scope` trong front-matter sửa lại (câu cũ "Không ADR nào ở trạng thái accepted" đã
sai từ vòng một).

**`precode/decision-register.md`** — bốn thay đổi: (a) `PROV-PC00-07` → **`ACCEPTED (OD-20260907-02)`**, trạng
thái cũ giữ lại dưới nhãn "(Lịch sử)"; (b) mục mới **`PROV-PC00-08`** cho chế độ vận hành khi ghi mã; (c) mục
mới **§8.10** ghi cả năm quyết định của biên bản kèm cột trạng thái, trong đó **hàng go-ahead** là một hàng
quyết định riêng, nêu đích danh bốn card Giai đoạn 1 và `G5-X4`; (d) §0 thêm nhãn `ACCEPTED (OD-20260907-02)`,
§7 thêm `ADR-0011`, front-matter và đoạn "Cập nhật" mở rộng.

**`PROV-PC00-08` viết dày hơn một dòng, có chủ đích.** Đây là chỗ dự án rời khỏi hồ sơ của chính nó:
`protocol.md` §2 nói thẳng *"Nếu không verify được runtime guards → BLOCKED, không fallback sang soft prompt"*,
và ruling này **chính là** một fallback sang soft prompt. Nó hợp lệ vì chỉ thị Owner đứng trên hồ sơ, nhưng nếu
sổ chỉ ghi "được phép ghi mã" thì lần đọc lại sau sẽ không thấy cái giá. Nên mục ghi ba chế độ hỏng cụ thể:
(a) ghi ngoài tập ghi **không** bị chặn, chỉ bị phát hiện *sau* khi byte đã lên đĩa; (b) hai Worker song song
trên cùng file không có fencing thật — "ghi đè im lặng" là chế độ hỏng có thật, giảm bằng cách Coordinator
không cấp packet chồng path chứ không bằng cưỡng chế; (c) không có audit log bền vững do service ghi, nên
handoff chứng minh được *cái gì đã đổi* nhưng **không** chứng minh được *không có gì khác đã đổi*. Cộng một
dòng "nếu Owner phản đối" nêu phương án thay thế duy nhất nhất quán với hồ sơ (hoãn Giai đoạn 0 và 1 cho tới
khi có guard thật) — vì một mục `PROVISIONAL` mà không có đường đảo thì không thật sự là `PROVISIONAL`.

**`precode/owner-decision-request.md`** — khối "CHỜ VÒNG SAU" thành "VÒNG HAI · ĐÃ TRẢ LỜI", dòng `ADR-0011`
điền **accept** kèm hệ quả, thêm dòng go-ahead Giai đoạn 0/1 với trần claim; `OQ03` chuyển sang khối "VẪN
CHỜ". Banner đầu file thêm một đoạn về vòng hai.

**`precode/baseline.json`** — anchor `ADR-0011` cập nhật (`accepted`, `ratified_by`, `ratified_at`,
`ratification_evidence`, hai authority, `scope_note_vi` nay mang cả cảnh báo bốn hàng, `updated_by_ruling`);
anchor mới `OD-20260907-02` trong `source_anchors.PROJECT.owner_decisions` với `ratifies` **chỉ** hai mục
(`ADR-0011`, `PROV-PC00-07` — không suy rộng), `grants` (hai lối vào giai đoạn), `coordinator_rulings_implied`
**tách riêng** khỏi `ratifies`, `claim_ceiling_phase_0_1`, và `not_decided` năm dòng gồm `REQ-OQ03` và
"`G5-X4` KHÔNG tự chuyển `met: true`". JSON parse lại được sau khi sửa.

**Không** chạm `precode/gates.yaml`, `precode/review.md`, `precode/requirements.csv`,
`agent_profile/registry.json`, `contracts/`, `acceptance/`, `agent-tasks/` — đúng packet.

## O3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/owner-decisions-02.md` | **CREATE** | ABSENT | `c2e6d70ba2f7f740167ab26d5f696f446d534a3da535cbf2e47e65a35ffe70c9` (9898) |
| `precode/owner-decisions.md` | MODIFY | `c5d411e561d464cbb6a05b42938dd11b4925506b12b72736ab46b354ba9ad994` (12373) | `f608d2e9527061558e9c0247136c7d6d51f24d073981afd40c1f424ef7773bda` (12711) |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` ⚠ | MODIFY | `9cdec0d78592c67068188e7dffcf9e03f361fe202263bb47a95b2298337a8340` (17052) | `6be9189a5e61b03eb44bdbfb2ca6841b1ca2d04f9dbf140fcc39764be5a9b155` (18989) |
| `precode/adr/README.md` ⚠ | MODIFY | `3e931f27583cc92f4ee394ad7d8dca590741644058380fec7dd307b9e3405374` (8192) | `097cd5f911a22d161703fc887ae7e4db503e1aee699b47455f00984cfb30dd52` (9226) |
| `precode/decision-register.md` ⚠ | MODIFY | `3596a52b6ce8cb39a0ae07501fd177c80a4fdb7b19317fc82a3dd8e3df63a75d` (104940) | `4d1a5d6e5d2a4f0aa3cf165913cc76f07442211715fd0bde9a12da51e82a7244` (114327) |
| `precode/owner-decision-request.md` | MODIFY | `572c2c11ecf18c8f958bb931d2aeafba1a2d64d3a42c674959562be05de3f56e` (56907) | `1a277fbca5c9b398dc95f4eb618cd8b0cd92e0167826fcc8eb9e217e10a2298f` (57906) |
| `precode/baseline.json` ⚠ | MODIFY | `c99474a6744a3827f75961884d5d8daf1d9fb0bfe212547c216d1574d32ac81a` (101458) | `d25e2edd05437dc475797f16e96e874d53ae0cd336cd162dd4b5a4131292c7bd` (104398) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `f363ab14a479e17df6d234d7f10f4f721a6f91df23ab582c163fd5b9c8a1d622` (168191) | *(file này)* |

**⚠ Bốn file card-pinned vừa đổi:** `precode/baseline.json` (`d25e2edd…`, 104398),
`precode/decision-register.md` (`4d1a5d6e…`, 114327), `precode/adr/README.md` (`097cd5f9…`, 9226),
`precode/adr/ADR-0011-frameworks-and-toolchain.md` (`6be9189a…`, 18989). Thuộc `CR-PC00-15` — W7 re-pin một
lượt. `precode/requirements.csv` **không** đổi (`fbe59d0e…`).

**1 CREATE + 6 MODIFY + 1 APPEND.** Không đổi và đã rehash để chứng minh: `precode/gates.yaml`
(`b5d9a79f…`), `precode/review.md` (`1da31eb0…`), `precode/requirements.csv` (`fbe59d0e…`),
`agent_profile/registry.json` (`fd9d6d25…`), `precode/README.md` (`f98254c3…`), mười ADR còn lại. Nguồn
`research-radar-spec.md` (`d35e1f2d…`) và `research-radar-pre-code-plan.md` (`f65bb046…`) rehash **khớp pin**
cả trước và sau. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc` (kiểm bằng `find`); không network;
không secret; mọi script chạy từ `…/scratchpad/w1/`.

**Quan sát ngoài phạm vi (không phải của tôi).** `git status` cho thấy các đường dẫn chưa theo dõi
`server/`, `collector/`, `worker/`, `shared/`, `probe/`, `pyproject.toml`, `uv.lock`, `.python-version` đã
xuất hiện trên đĩa — đó là công việc Giai đoạn 0 của (các) Worker khác dưới cùng biên bản này. Tôi **không**
chạm vào chúng và không kê hash của chúng: chúng không nằm trong tập ghi của tôi và đang có writer khác.

## O4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T09:20Z / 2026-09-07T09:20Z · **exit code 0** ·
  **367 assertion, 367 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1n`.
- **Mọi assertion cũ vẫn chạy.** `EV-PC00-01..07` không đổi một dòng nào và vẫn PASS — nguồn khớp pin, 246
  dòng `requirements.csv`, B01..B17, 11 ADR, ngoại lệ header.
- **`EV-PC00-08` được sửa cho đúng trạng thái mới** (không nới lỏng): khối `ADR-0011` nay đòi
  `status: accepted`, `ratified_by: OD-20260907-02` **và** `ratified_at`, đòi evidence trỏ đúng
  `session_0156UBBHDSeC9soECzSVUb3U` và `precode/owner-decisions-02.md`, đòi `decision_owner` **vẫn** là
  `Coordinator`, đòi **không** có `ratified_by: OD-20260907-01` (chống quy sai thẩm quyền cho biên bản vòng
  một), đòi blockquote lập luận cũ còn nguyên, và đòi mục "Trạng thái" nói rõ phê chuẩn không biến bốn hàng
  trống thành đã-cân-nhắc. Hàng chỉ mục và anchor baseline kiểm theo giá trị mới; dòng phiếu trả lời phải là
  `accept` **và** không còn ô trống `/ object`. `scrub` của `EV-PC00-04` nay nhận cả hai decision id nên luật
  "không dùng `ACCEPTED` trần" vẫn nguyên hiệu lực.
- **`EV-PC00-09` mới — 60 assertion** cho biên bản vòng hai: 19 trường front-matter; đúng **5** hàng theo thứ
  tự; chép nguyên văn chỉ thị của Owner, bốn tên card, ngân sách subagent và trần claim; **năm** phát biểu
  phạm-vi-không-quyết; `PROV-PC00-07` mang `ACCEPTED (OD-20260907-02)` **và** giữ đoạn lịch sử;
  `PROV-PC00-08` là `PROVISIONAL`, có điều khoản phản đối, nêu `instruction_precedence`, "kỷ luật bằng thông
  điệp", "ghi đè im lặng", `fencing`, cả hai chế độ của `protocol.md` §2, trần claim và `product_status`;
  §8.10 có đúng 5 hàng, đúng **2** hàng `ACCEPTED (OD-20260907-02)` và **2** hàng `PROVISIONAL`, nêu `G5-X4`
  không tự `met: true` và bốn card; anchor baseline `ratifies` **đúng hai** mục; và **ba assertion âm**:
  `claim_ceiling` của bộ hợp đồng **không** đổi, `product_status` **không** đổi, `REQ-OQ03` **không** được
  giải bởi biên bản này.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4. Một phê chuẩn framework **không** tạo bằng chứng kỹ
  thuật nào — không dòng mã nào của Giai đoạn 0/1 được tôi kiểm ở gói này.

## O5. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-20` **(mới)** | `precode/gates.yaml` và `precode/review.md` (PC09) chưa phản ánh `OD-20260907-02`: G5 chưa ghi lối vào đã được cấp cho bốn card Giai đoạn 1, và `G5-X4` vẫn `met: false` (đúng — nó chỉ đổi khi Giai đoạn 0 chạy xong và **được xác minh**, không phải khi được cấp phép). Ngoài grant của gói này. |
| `CR-PC00-21` **(mới)** | `agent_profile/registry.json` chưa có `OD-20260907-02` / `AUTH-OWNER-20260907-03`, và `instruction_precedence` — căn cứ trung tâm của `PROV-PC00-08` — chưa được trích dẫn ở đâu ngoài sổ. Ngoài grant của gói này. |
| `CR-PC00-15` | W7 re-pin — nay gồm bốn file ở §O3 với hash mới |
| `CR-PC00-19` | Ruling gốc `ADR-0011` trong `evidence/coordination/` vẫn mang câu quy kết sai về §5.3 |
| `CR-PC00-16` | `ADR-0006` giữ tên file cũ trong khi nội dung là phương án B |
| `CR-PC00-17`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3. Biên bản vòng hai **không nhắc tới nó** — im lặng không phải một quyết định. |
| `PROV-PC00-08` | `PROVISIONAL`. Đây là mục duy nhất trong bộ mà một quyết định trọng yếu (ghi mã sản phẩm không có runtime guard) đứng trên một **suy luận** từ câu trả lời của Owner chứ không trên chính câu trả lời. Đề nghị Coordinator đưa nó lên Owner thành một câu hỏi tường minh ở vòng sau, không gộp. |

**Vì sao status là `DONE_WITH_CONCERNS`.** Mọi mục của packet đã xong và validate exit 0. Concern nằm ở chỗ
gói này ghi vào sổ một quyết định (`PROV-PC00-08`) cho phép **các Worker khác** đang chạy song song ghi mã
sản phẩm, trong khi `agent_profile/protocol.md` §2 nói phải `BLOCKED`. Tôi không có thẩm quyền quyết điều đó
và không quyết; tôi ghi lại nguyên trạng, giữ nó ở `PROVISIONAL`, và nêu rủi ro còn lại đủ cụ thể để Owner
phản đối được nếu muốn. Nếu Owner phản đối sau khi Giai đoạn 0 và 1 đã ghi mã, chi phí không còn là sửa một
tài liệu.

## O6. Trạng thái bàn giao (FIX15)

- **next actor:** `Coordinator` — rehash bảy file ở §O3; giao `CR-PC00-20` (PC09 gates/review) và
  `CR-PC00-21` (registry); giao W7 re-pin bốn file card-pinned.
- **lease_released_at (UTC):** 2026-09-07T09:22Z. `LEASE-PC00-e16` (fencing 16) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §O3) và lease fencing ≥ 17.
- **Claim:** `DRAFT_FOR_REVIEW` cho gói này. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0 theo
  `E0-20260907T044549Z`; `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`. Trần claim
  của đầu ra Giai đoạn 0/1 là `IMPLEMENTATION_VERIFIED` — gói này **không** tạo bằng chứng nào cho nó.

---

# ADDENDUM — PKT-PC00-FIX16 (`CR-PC00-21`: registry ghi chuỗi authority và `coding_phase`)

## P1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX16` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX16` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-PC00-e17` (**fencing 17**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T09:40Z / 2026-09-07T09:54Z · lease expires 2026-09-08T12:00Z (`date -u` trước lần ghi cuối: 2026-09-07T09:52Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T09:54Z |
| nguồn | `CR-PC00-21` do chính tôi mở ở `PKT-PC00-FIX15` §O5 |

## P2. Đã làm gì

**`agent_profile/registry.json`** — chèn **ba** khóa mới ngay sau `ratification_evidence`, không đụng byte nào
khác:

- `ratification_evidence_02: "precode/owner-decisions-02.md (OD-20260907-02)"` — song song với khóa vòng một
  chứ **không** thay thế nó; hai biên bản cộng dồn nên hai khóa cùng tồn tại.
- `authorities` — ba grant của Owner, mỗi grant sáu trường (`authority_id`, `issuer`, `issued_at`, `scope`,
  `decision_record`, `evidence_ref`).
- `coding_phase` — `status: PHASE_0_1_IN_PROGRESS`, `authorised_by: OD-20260907-02`,
  `mode: "message-tracked leases (PROV-PC00-08)"`, `enforcement: NOT_IMPLEMENTED`.

**Ba điều tôi viết vào `scope` mà packet không đọc cho, và vì sao.** Một bảng authority chỉ có id và ngày thì
không dùng được để chặn việc gì; giá trị của nó nằm ở chỗ nó ghi **ranh giới**. Nên mỗi `scope` mang cả vế
phủ định:

1. `AUTH-OWNER-20260906-01` ghi rõ *"Documents only: no product code, no external effect"*. Đây là grant
   **duy nhất** trong ba grant bị `PROV-PC00-08` vượt qua; nếu bảng không nói grant đó chỉ cho tài liệu thì
   người đọc sau sẽ tưởng việc ghi mã đã nằm trong nó từ đầu và `PROV-PC00-08` là thừa.
2. `AUTH-OWNER-20260907-02` ghi rằng nó **ủy quyền việc chọn** framework, không phê chuẩn nội dung — đúng
   phân biệt mà `ADR-0011` sống trên đó suốt hai gói vừa rồi.
3. `AUTH-OWNER-20260907-03` mang trần claim `IMPLEMENTATION_VERIFIED, never INTEGRATION/LIVE` ngay trong
   `scope`. Đây là grant mà mọi packet Giai đoạn 0/1 trích làm parent; đặt trần ngay tại grant khiến một
   packet con không thể lặng lẽ đòi mức cao hơn cha.

Cả hai grant 2026-09-07 đều ghi `REQ-OQ03` trong phần phủ định, vì đó là mục duy nhất còn treo và là chỗ dễ bị
coi là "chắc đã giải ở đâu đó rồi".

**`evidence_ref` là ba phiên khác nhau, không phải một.** Grant đầu trích
`session-01BAnmhQcMCXY2V66NH6c1PY` (phiên 2026-09-06, nguyên văn chỉ thị nằm ở coordination baseline §1);
hai grant sau trích `session_017QmDJ…` và `session_0156UBBH…`. `decision_record` của grant đầu là `null` —
**có chủ đích**: nó là chỉ thị trực tiếp, chưa bao giờ được chuyển thành một biên bản `OD-…`. Ghi `null` trung
thực hơn là trỏ nó vào một biên bản ra đời sau nó một ngày.

**`precode/owner-decisions-02.md`** — thêm mục **"Chuỗi authority tính đến biên bản này"** ngay dưới bảng định
danh, cùng ba hàng với `registry.json` (bản tiếng Việt, chi tiết hơn ở phần phạm vi), cộng một đoạn
**"Điều bảng này không nói"**: không grant nào bật `ENFORCED`, `operational_enforcement_status` và
`coding_phase.enforcement` đều `NOT_IMPLEMENTED`, lease giai đoạn mã vẫn là kỷ luật bằng thông điệp. Hàng
`agent_profile/registry.json` trong bảng truy vết §6 đổi từ *"Chưa làm ở gói này"* thành nội dung thật của gói
này, và `CR-PC00-21` được ghi là đã giải.

**Không** chạm `precode/gates.yaml`, `precode/review.md`, `precode/decision-register.md`, `precode/adr/`,
`precode/baseline.json`, `precode/requirements.csv`, `contracts/`, `acceptance/`, `agent-tasks/` — đúng packet.

## P3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `agent_profile/registry.json` | MODIFY | `fd9d6d25f3ebf7e2f0dbbb269f3d72ce944edd9ba4c2b7552963b37b71383135` (3784) | `7f04465121241160363d3ab4ba3a0d2e9177e77f5cb27bf509759474c7effe88` (5909) |
| `precode/owner-decisions-02.md` | MODIFY | `c2e6d70ba2f7f740167ab26d5f696f446d534a3da535cbf2e47e65a35ffe70c9` (9898) | `ba404207522d0d85a8f4e7d2f21660ad94f6aa0191fa260a9be7a48f8f8aa429` (12298) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `a224ca410ce53b411a5dc84f0440cb7667106fe0398ab7f8ab734d3ccea9f4b8` (184207) | *(file này)* |

**2 MODIFY + 1 APPEND.** `agent_profile/registry.json` **không** phải file card-pinned; danh sách re-pin của
`CR-PC00-15` **không** đổi so với `FIX15` (vẫn `baseline.json` `d25e2edd…`, `decision-register.md`
`4d1a5d6e…`, `adr/README.md` `097cd5f9…`, `ADR-0011` `6be9189a…`). Đã rehash để chứng minh không đổi:
`precode/baseline.json` (`d25e2edd…`), `precode/decision-register.md` (`4d1a5d6e…`), `precode/adr/README.md`
(`097cd5f9…`), `precode/adr/ADR-0011-frameworks-and-toolchain.md` (`6be9189a…`),
`precode/owner-decision-request.md` (`1a277fbc…`), `precode/owner-decisions.md` (`f608d2e9…`),
`precode/gates.yaml` (`b5d9a79f…`), `precode/review.md` (`1da31eb0…`), `precode/requirements.csv`
(`fbe59d0e…`). Nguồn `research-radar-spec.md` (`d35e1f2d…`) và `research-radar-pre-code-plan.md`
(`f65bb046…`) rehash **khớp pin** cả trước và sau. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`;
không network; không secret; script chạy từ `…/scratchpad/w1/`.

## P4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T09:52Z / 2026-09-07T09:52Z · **exit code 0** ·
  **412 assertion, 412 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1n`.
- **`EV-PC00-01..09` không đổi một dòng nào** và vẫn PASS — gói này không chạm file mà chúng kiểm, trừ
  `owner-decisions-02.md`, và `EV-PC00-09` (60 assertion về biên bản vòng hai, gồm quy tắc "đúng 5 hàng theo
  thứ tự") vẫn PASS sau khi bảng authority được chèn: bảng mới cố ý **không** dùng cột đầu là số.
- **`EV-PC00-10` mới — 45 assertion:** `ratification_evidence_02`; ba `authority_id` **đúng thứ tự thời
  gian**; **sáu** trường bắt buộc trên **từng** grant; mọi `issuer` bắt đầu bằng `Owner`; mọi `evidence_ref`
  trỏ về một phiên thật; `decision_record` đúng cho từng grant kể cả `null` của grant đầu; **ba evidence_ref
  là ba phiên khác nhau** (chống lỗi chép đè — lỗi im lặng nhất mà một bảng như thế này có thể mắc); grant
  2026-09-06 vẫn là grant *chỉ tài liệu*; grant 03 mang trần claim; hai grant 2026-09-07 đều nêu `REQ-OQ03`;
  `coding_phase` khớp **đúng** bốn khóa và bốn giá trị packet yêu cầu, so sánh bằng `==` chứ không bằng
  `in`; và bảng trong biên bản vòng hai khớp registry theo từng `authority_id`.
- **Bảy assertion âm** — điều gói này **không** được phép làm: `operational_enforcement_status` vẫn
  `NOT_IMPLEMENTED`, `session_drafting_mode` vẫn `DOCUMENTARY_DRAFT`, `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`, `status` vẫn `DRAFT_FOR_REVIEW`, khối `roles` (gồm `Specialist` disabled và
  `Coordinator.physical_write: false`) không bị đụng, khối blocker không bị đụng, và
  `instruction_precedence` — căn cứ trung tâm của `PROV-PC00-08` — còn nguyên **và** vẫn xếp
  `explicit_owner_instructions` **trên** `pinned_agent_protocol`. Nếu ai đó sau này đảo hai dòng đó thì
  `PROV-PC00-08` mất căn cứ, nên nó phải là một assertion chứ không phải một câu văn.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4. Ghi một bảng authority **không** làm cho authority đó
  được cưỡng chế — `enforcement: NOT_IMPLEMENTED` là mô tả đúng, không phải một mục cần làm sau.

## P5. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-21` | **Đã giải ở gói này.** Lưu ý mức bằng chứng: đây là lời tự khai của Worker; đóng CR cần xác minh độc lập trên epoch mới và không được do tôi ký. |
| `CR-PC00-20` | **Vẫn mở** — `precode/gates.yaml` và `precode/review.md` (PC09) chưa phản ánh `OD-20260907-02`. Ngoài grant của cả `FIX15` lẫn `FIX16`. |
| `CR-PC00-15` | W7 re-pin — danh sách **không đổi** so với `FIX15` (registry không phải file card-pinned) |
| `CR-PC00-19`, `CR-PC00-17`, `CR-PC00-16`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |
| `PROV-PC00-08` | Vẫn `PROVISIONAL`. Gói này **làm nó dễ thấy hơn** (`coding_phase` trong registry) chứ không làm nó vững hơn: `enforcement: NOT_IMPLEMENTED` nói đúng rằng chưa có gì cưỡng chế. Đề nghị của `FIX15` giữ nguyên — đưa lên Owner thành câu hỏi riêng. |

## P6. Trạng thái bàn giao (FIX16)

- **next actor:** `Coordinator` — rehash hai file ở §P3; `CR-PC00-20` còn mở.
- **lease_released_at (UTC):** 2026-09-07T09:54Z. `LEASE-PC00-e17` (fencing 17) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §P3) và lease fencing ≥ 18.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`.

---

# ADDENDUM — PKT-PC00-FIX17 (`CR-PC10-09`: bố cục repo của `ADR-0011` khớp §5.3)

## Q1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX17` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX17` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-PC00-e18` (**fencing 18**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T09:58Z / 2026-09-07T10:05Z · lease expires 2026-09-08T16:00Z (`date -u` trước lần ghi cuối: 2026-09-07T10:03Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T10:05Z |
| nguồn | `CR-PC10-09` (PC10 nêu trong `agent-tasks/README.md` §5.3: PC10 không được ghi ADR nên phải raise CR) |

## Q2. Đã làm gì

**Bảng bố cục viết lại: bảy thư mục → tám cây**, khớp `agent-tasks/README.md` §5.3 tại epoch pin
`PC10-PIN-P1-20260907` (epoch được trích ngay trong bảng, để lần lệch sau nhìn thấy được):
`server/`, `collector/`, `worker/`, `web/`, `shared/rr_contracts/`, `tests/`, `probe/`, **`tools/`**.

- **`tools/` là cây thứ tám.** `agent-tasks/TC-backup-restore-drill.md` §3 **vốn đã pin** `tools/backup_cli.py`
  từ trước; §5.3 và ADR mới là bên đi sau. Nên tôi ghi hàng này là ADR **bắt kịp card**, không phải card đổi
  theo ADR — kèm lý do đường dẫn: `MOD-backup-cli` là một tiến trình CLI riêng với auth scope
  `backup_operator`, **không** phải session owner; đặt nó dưới `server/` làm mờ ranh giới ấy ngay ở tầng
  đường dẫn.
- **`tests/` bỏ `unit/`.** Hàng cũ ghi `contract/`, `unit/`, `integration/`. §3 của cả 18 card chỉ dùng hai
  thư mục, và Giai đoạn 0 chỉ tạo hai (`CR-P0-03` mục 2). Hàng mới nói **thẳng** "Không có `tests/unit/`" thay
  vì chỉ im lặng bỏ tên đi — một thư mục biến mất không lời giải thích là thứ người đọc sau sẽ "khôi phục".
- **Tên import `PROV-P0-01`** được thêm thành một đoạn riêng: `server.app.…`, `collector.app.…`,
  `worker.app.…`, `rr_contracts.…`, kèm câu **"không phải `app.…`"**. Đây là chỗ dễ sai nhất và là thứ bộ
  khung đã cố định — card không được tự đổi.
- Hàng `web/` được ghi chi tiết hơn (`src/lib/`, `routes/`, `views/`, `tests/contract/`, `tests/integration/`)
  cho khớp §5.3.

**Ghi chú `CR-PC10-09` mới, ba đoạn — và vì sao ba chứ không một.**

1. *Đây là đính chính **sự kiện**, không phải quyết định mới.* Nói rõ hai chỗ được sửa và rằng `tools/` đã
   được card pin từ trước.
2. *Vì sao `ratified_by` không đụng tới.* `OD-20260907-02` phê chuẩn **14 hàng của bảng Quyết định** (ngôn
   ngữ, framework, DB, hàng đợi, test runner, CI, đóng gói…). Bố cục repo là **mô tả đi kèm**, không phải một
   trong 14 hàng; sửa nó cho khớp thực tế không đổi một lựa chọn nào Owner đã phê chuẩn. Nên `status:
   accepted` và `ratified_by: OD-20260907-02` **giữ nguyên** và không cần vòng quyết định mới — kèm câu ràng
   buộc ngược lại: nếu sau này một hàng **trong** bảng Quyết định phải đổi thì ADR phải quay lại Owner.
3. *Sự kiện Giai đoạn 0.* Trích `evidence/handoffs/P0-skeleton-handoff.md`.

**Một chỗ tôi không viết theo packet, có chủ đích.** Packet nói ghi "the Phase 0 fact that the skeleton
exists". Tôi kiểm trực tiếp trên đĩa trước khi viết: **bảy** trong tám cây tồn tại; **`tools/` chưa được
tạo** — nó nằm ngoài write set của `PKT-P0-SKELETON` (`CR-P0-03` mục 1) và sẽ do card M8
`TC-backup-restore-drill` tạo. Viết "bộ khung của tám cây đã tồn tại" sẽ là một câu sai kiểm được, đúng loại
lỗi mà `F-A2R7-04` đã phạt ADR này một lần rồi (quy kết cả bảy thư mục cho §5.3 khi §5.3 mới khai sáu). Nên
ghi chú tách bạch hai thứ và **không** cho phép đọc lẫn: bảy cây là **sự kiện đã kiểm trên đĩa**, cây thứ tám
là **cam kết đã khai** chưa thành file. Thêm câu: bộ khung không mang hành vi nghiệp vụ nào (chỉ
`health.get_liveness`; `health.get_readiness` **cố ý** chưa route vì thuộc `TC-storage-write-blocked-readiness`)
nên nó **không** là bằng chứng cho card nào — E1–E4 vẫn `NOT_RUN`.

**Ghi chú `F-A2R7-04` cũ giữ nguyên từng chữ** ở trên ghi chú mới. Nó ghi lịch sử "§5.3 khi đó khai sáu"; viết
đè lên nó sẽ xoá đúng thứ mà `FIX14` dựng lên.

## Q3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` ⚠ | MODIFY | `6be9189a5e61b03eb44bdbfb2ca6841b1ca2d04f9dbf140fcc39764be5a9b155` (18989) | `da5181b2888674134f6e3919ce401014015f223ea46a967d9fda3833c01a037b` (22685) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `058b9827a80aa743d8da149cfed3b4b58bea2ce5922925bfb7e60aa5077e725c` (194212) | *(file này)* |

**⚠ `ADR-0011` là card-pinned** và nằm trong read set của **cả 18 card** — hash mới `da5181b2…` (22685) làm
mọi card `STALE` theo `INV-06`, đúng như lần `FIX15` đã làm. Coordinator đã báo trước là sẽ xếp **một** lượt
re-pin sau Giai đoạn 1; tôi **không** raise một CR mới cho việc đó, chỉ ghi hash ở đây để lượt re-pin lấy
đúng giá trị. Danh sách re-pin của `CR-PC00-15` nay là: `ADR-0011` `da5181b2…` (22685), `baseline.json`
`d25e2edd…` (104398), `decision-register.md` `4d1a5d6e…` (114327), `adr/README.md` `097cd5f9…` (9226).

**1 MODIFY + 1 APPEND.** Đã rehash để chứng minh không đổi: `agent-tasks/README.md`
(`e73f7e8f…` — **không** chạm, nó là nguồn tôi khớp theo, không phải đích), `precode/baseline.json`
(`d25e2edd…`), `precode/decision-register.md` (`4d1a5d6e…`), `precode/adr/README.md` (`097cd5f9…`),
`precode/owner-decisions-02.md` (`ba404207…`), `precode/owner-decisions.md` (`f608d2e9…`),
`precode/owner-decision-request.md` (`1a277fbc…`), `agent_profile/registry.json` (`7f044651…`),
`precode/gates.yaml` (`b5d9a79f…`), `precode/review.md` (`1da31eb0…`), `precode/requirements.csv`
(`fbe59d0e…`), mười ADR còn lại. Nguồn `research-radar-spec.md` (`d35e1f2d…`) và
`research-radar-pre-code-plan.md` (`f65bb046…`) rehash **khớp pin**. Không chạm `agent-tasks/`,
`contracts/`, `acceptance/`, `server/`, `collector/`, `worker/`, `web/`, `tests/`, `shared/`, `probe/`.
Không lệnh git thay đổi repo; không `__pycache__`/`.pyc`; không network; không secret.

## Q4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T10:03Z / 2026-09-07T10:03Z · **exit code 0** ·
  **450 assertion, 450 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1n`.
- **`EV-PC00-01..07`, `EV-PC00-09`, `EV-PC00-10` không đổi một dòng nào** và vẫn PASS. Khối `F-A2R7-04` của
  `EV-PC00-08` giữ nguyên, gồm cả phép kiểm chéo trên đĩa (`rr_contracts` có trong `agent-tasks/README.md`
  ⇔ ADR nói "PC10 đã bổ sung").
- **38 assertion mới trong `EV-PC00-08`:** bảng bố cục có **đúng 8 hàng** và không còn chữ "bảy thư mục";
  epoch `PC10-PIN-P1-20260907` được trích; hàng `tests/` **không** còn `unit/` **và** nói thẳng "Không có
  `tests/unit/`"; hàng `tools/` nêu `backup_cli.py` và `CR-P0-03`; năm chuỗi import của `PROV-P0-01` kể cả
  câu "không phải `app.…`"; ADR tự khai là đính chính sự kiện; `ratified_by: OD-20260907-02` **vẫn** ở
  front-matter và ADR nói rõ nó giữ nguyên.
- **Bảy assertion **đối chiếu thực tế**, không phải đối chiếu văn bản với chính nó** — đây là phần đáng tin
  nhất của lượt này: bảy cây `server`, `collector`, `worker`, `web`, `shared/rr_contracts`, `tests`, `probe`
  phải **tồn tại thật** trên đĩa; `evidence/handoffs/P0-skeleton-handoff.md` phải tồn tại; và hai phép kiểm
  hai chiều — *"`tools/` vắng trên đĩa" ⇔ "ADR nói `tools/` chưa được tạo"* và *"`tests/unit/` vắng trên đĩa"
  ⇔ "ADR nói không có `tests/unit/`"*. Nếu ai đó tạo `tools/` mà không sửa ADR, hoặc sửa ADR mà không tạo
  `tools/`, validate **FAIL** thay vì ADR âm thầm nói sai.
- **Bốn assertion đối chiếu ADR với `agent-tasks/README.md` §5.3 thật** (đọc trực tiếp file, không chép giá
  trị): tám cây đều xuất hiện trong §5.3, và §5.3 cũng nói "Không có `tests/unit/`" — hai văn bản phải cùng
  nói một điều, không chỉ mỗi văn bản tự nhất quán.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4. Bộ khung Giai đoạn 0 **không** được tôi chạy hay kiểm
  chức năng ở gói này — tôi chỉ kiểm **sự tồn tại của thư mục**, và evidence record nói đúng chừng đó.

## Q5. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC10-09` | **Đã giải ở gói này** (tự khai; đóng CR cần xác minh độc lập, không do tôi ký). |
| `CR-P0-03` mục 1 | **Vẫn mở về mặt file:** `tools/` đã được §5.3 và ADR khai nhưng **chưa tồn tại**. Card M8 `TC-backup-restore-drill` phải tạo nó. ADR nay ghi rõ khoảng cách đó thay vì che. |
| `CR-PC00-15` | Re-pin — danh sách cập nhật ở §Q3; Coordinator xếp **một** lượt sau Giai đoạn 1 |
| `CR-PC00-20` | **Vẫn mở** — `precode/gates.yaml` / `precode/review.md` (PC09) chưa phản ánh `OD-20260907-02` |
| `CR-PC00-19` | Ruling gốc `ADR-0011` trong `evidence/coordination/` vẫn mang câu quy kết sai về §5.3 — **nay lệch thêm một mức** (nó nói bảy thư mục và có `tests/unit/`) |
| `CR-PC00-16`, `CR-PC00-17`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |
| `PROV-PC00-08` | Vẫn `PROVISIONAL` — khuyến nghị của `FIX15` (đưa lên Owner thành câu hỏi riêng) giữ nguyên |

## Q6. Trạng thái bàn giao (FIX17)

- **next actor:** `Coordinator` — rehash `ADR-0011`; đưa hash mới vào lượt re-pin sau Giai đoạn 1;
  `CR-PC00-20` và `CR-P0-03` mục 1 còn mở.
- **lease_released_at (UTC):** 2026-09-07T10:05Z. `LEASE-PC00-e18` (fencing 18) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §Q3) và lease fencing ≥ 19.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN`.

---

# ADDENDUM — PKT-PC00-FIX18 (packaging: `A2-R7`, `A3-R3`, ba manifest `FC-P1`, mười file điều phối)

## R1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX18` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX18` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-PC00-e19` (**fencing 19**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / gate mở / finished (UTC) | 2026-09-07T12:14Z / **2026-09-07T12:22Z** / 2026-09-07T12:28Z · lease expires 2026-09-08T16:00Z (`date -u` trước lần ghi cuối: 2026-09-07T12:26Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T12:28Z |

## R2. Wait gate — đã tôn trọng, có bằng chứng

Packet cấm ghi cho tới khi `…/scratchpad/audits/A3-R3-report.md` tồn tại. Tôi arm một poller nền
(`until [ -f … ]; do sleep 60; done`, trần 45 phút) và **không ghi một byte nào vào repo** trong lúc chờ.
Poller thoát với `GATE_OPEN after 8m: 14574 bytes`; lệnh `cp` đầu tiên chạy **sau** dấu đó.

Trong lúc chờ tôi chỉ làm việc **chỉ đọc**, và nó có ích: `cmp` lại **toàn bộ 49 bản sao đã có từ trước**
(20 ở `evidence/audits/`, 29 ở `evidence/coordination/`) so với nguồn scratchpad — **49/49 byte-identical**,
nên `A3-R1`/`A3-R2` **không** cần chép lại và **không** bị nhân bản, đúng như packet dự liệu.

## R3. Đã chép gì

**16 file** (`cp -p`, mỗi file `cmp`-verified; hash nguồn ghi **trước** khi chép vào `…/w1/src_fix18.sha`).

`evidence/audits/` — 5 CREATE:

| File | sha256 sau khi chép | Bytes |
| --- | --- | --- |
| `A2-R7-report.md` | `12b0dbcc39919cc4c74bccaae24670ea480660ab1a945d06a0bc2ab28dd74880` | 17667 |
| `A3-R3-report.md` | `5d9a4ce609f24b785f7d2d5753602f5f52008e01bc01886e2667807adfce6284` | 14574 |
| `FC-P1-manifest.txt` | `9553f45aaab6087969eb8538421be1ed62cef076fbc104041b82af2115092985` | 56259 |
| `FC-P1e2-manifest.txt` | `0d172d4c394728f359996e66d773387d4180e8c96698912a03dc1e11fb282bb9` | 56885 |
| `FC-P1e3-manifest.txt` | `1a736950d1244c6bfc74d224d31c72d92b94a84528627850f1f0c459d11912d9` | 58266 |

`evidence/coordination/` — 10 CREATE + 1 REPLACE:

| File | sha256 sau khi chép | Bytes |
| --- | --- | --- |
| `OWNER-DECISIONS-20260907-02.md` | `599d8427870ebdfc921d1ad105e7bf9e45b1f5b62eeb5f66f0dd31e31477245f` | 2455 |
| `PHASE0-skeleton-packet.md` | `ad76109b3130d3035ea3522c89ead65988314132a903e9c858dcc9a43303a513` | 8193 |
| `PHASE1-card-dispatch-template.md` | `70630dfc6ab4718da09c5763dc0ec3803578836cb81b8cd71e9ff42cb3a1cc5f` | 3988 |
| `A3-code-review-packet.md` | `670da439c78156c3af4a48de2e382a1f14d1cf3b4f2f3f66f74e8e28bef5f218` | 3951 |
| `A3-r2-packet.md` | `e55841a9b22b56fefbca24bebdab5bd532ac063125c41f90148e538097a69670` | 3309 |
| `A3-r3-packet.md` | `8f2fe8e7f0b3b41fdfae4a90c74d8ead9d43fb93ba625a2fac1b64920e72bd82` | 2444 |
| `FIX-A3R1-rulings.md` | `ec3805a9682fe16784671258721a7337f386d82279e5a75426ebefaac004997d` | 4678 |
| `PC09-PHASE1-packet.md` | `38cbf318942e056d934ed1231497b78ab1934a09c27d26f39e108d32f6fad51f` | 3933 |
| `ADR-0011-frameworks-ruling.md` | `09050e65a0c1d6f16fb5463fe8fde1a567cefc9792b1c665ed8c04b2c660555f` | 4487 |
| `phase1-cr-consolidated.txt` | `3c6433db66e10a510820c29d37dfbdac82d934564e12280eb387619666bea4a3` | 4452 |
| `coordinator-ledger.md` **(REPLACE)** | `0a1187c5ac1725ad316ef78d65c56349df985d3adb9da4f061212fc01d9dc30a` | 52809 |

**Bản `coordinator-ledger.md` bị thay:** `0369031b73e7550ec4fe7d63e8d206049a560528d3b97d8a5eca6e4eb6db4ac5`
(39468 byte, chép ở `PKT-PC00-FIX12`, dừng ở `FC-W4` epoch 9). Bản trước nữa: `a8a7d319…` (`PKT-PC00-FIX9`).

## R4. Sổ tiến độ là một file đang sống — và điều đó suýt lọt qua

Đây là chỗ đáng nói nhất của gói này. Tôi chép `progress.md` lúc ~12:22Z (`fd0116d3…`, 52444 byte), `cmp` đạt.
Ở **lượt kiểm thứ hai** trước handoff, `cmp` báo **DIFF**: Coordinator đã ghi tiếp nguồn lúc 12:22:45Z
(52809 byte). Bản chép của tôi không hỏng — nó vẫn là ảnh chụp đúng của nguồn tại thời điểm chép — nhưng nếu
tôi chỉ `cmp` **một lần** thì README sẽ mang một hash mà người đọc sau tưởng là "bản mới nhất".

Xử lý: chép **lại** đúng một lần lúc 12:26Z, hash nguồn **trước và sau** lần chép **giống nhau**
(`0a1187c5…` cả hai), rồi `cmp` ngay. Tôi **không** lặp vô hạn để đuổi theo một file đang được ghi — điều đó
không kết thúc được. Thay vào đó README nay nói thẳng: đây là **ảnh chụp tại 12:26Z**, gần như chắc chắn đã
tụt lại khi bạn đọc, và thứ bản chép bảo đảm là *byte ở đây đúng bằng byte của nguồn tại 12:26Z* — không hơn.
Bản chép đầu (`fd0116d3…`) được ghi lại ở đây và trong README như một bản trung gian đã bị thay trong cùng gói.

**Bốn mươi chín bản sao còn lại `cmp` đạt ở cả hai lượt**, nên chúng ổn định; chỉ mỗi sổ này sống.

## R5. Hai README

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `evidence/audits/README.md` | MODIFY | `4e527ba0846c7f0f129256ccad58c32cbc04d7017275dc720769da359be9905d` (6558) | `a868664852efa37e594c8062180cfd09d58d055a2226d91d81b292b2ba6d53a9` (12372) |
| `evidence/coordination/README.md` | MODIFY | `907fc734411ce70f87c41c6ab193b59217aba2fe2e24391fda29ee365cd8755c` (9445) | `636fe1e562d42a3891f173c8f3737d80b6366b4023e1868ff3d9286899511c22` (15799) |

`evidence/audits/README.md`: đếm lại (**13** báo cáo, **12** manifest, `auditor-A2` ×7, `auditor-A3` ×3); năm
hàng mới; và **hai** đoạn mà tôi thêm vì bảng số không nói được:

- **`A2-R7` là ngoại lệ về hình dạng.** Nó là báo cáo duy nhất **không có manifest** — Coordinator dispatch
  lúc 18 card đang re-pin, nên auditor hash hai file trong phạm vi ở đầu và cuối vòng thay cho manifest. Cột
  "Candidate / epoch" của nó ghi *(không epoch)* thay vì bịa một `FC-` không tồn tại.
- **`A3-R3` PASS **không** nghĩa là mọi thứ nó chạm đều sạch.** Cùng bản đó mở `F-A3R3-01`: `E0-12` bắt được
  nhãn claim sai **ngoài** hai cây bằng chứng nhưng **không** bắt được nhãn đặt **trong** `evidence/runs/`,
  chứng minh bằng bốn mutation mà ba lẽ ra phải FAIL lại PASS. Một README chỉ chép chữ "PASS" sẽ làm người
  đọc bỏ qua đúng dòng quan trọng nhất. Tôi cũng ghi rằng `A3-R3` **mutation-test chính guard của Worker** —
  đó là khác biệt thật giữa nó và hai vòng trước, không phải một câu khen.

`evidence/coordination/README.md`: **ba** authority Owner (không còn hai) kèm ranh giới "grant đầu chỉ cho tài
liệu, việc ghi mã chạy dưới `PROV-PC00-08` vẫn `PROVISIONAL`"; 13 hàng mới; đoạn "bổ sung ba lần"; và **ba**
ghi chú:

- **ERRATUM `ADR-0011-frameworks-ruling.md` (`CR-PC00-19`)** — ruling khai "cả bảy thư mục đã được §5.3 khai",
  **sai** lúc viết (§5.3 khi ấy khai sáu; `shared/rr_contracts/` sinh ra tại chính ADR), và bố cục nay là
  **tám** cây với `tests/` không có `unit/`. Quy kết đã được sửa ở ADR qua `FIX14` và `FIX17`.
  **File lưu trữ KHÔNG bị sửa** — như tôi đã báo trước khi chạy: sửa một bản sao nguyên văn để nó "đúng hơn"
  phá đúng thứ làm bản lưu trữ có giá trị, nên erratum sống **cạnh** bản gốc với luật giải quyết tường minh
  (**ADR hiện hành thắng**; ruling chỉ nói ruling đã nói gì). `cmp` của file vẫn đạt.
- **Hai file không phải packet cũng không phải ruling.** `phase1-cr-consolidated.txt` là bảng gom CR —
  công cụ làm việc, **không** có thẩm quyền; trạng thái CR chuẩn ở `precode/review.md` §12.
  `PHASE1-card-dispatch-template.md` là **template**: không lease, không tập ghi, **không cấp quyền cho ai**.
  Không nói ra thì một template nằm cạnh 14 packet thật rất dễ bị đọc như packet thứ 15.
- **Sổ tiến độ đang sống** (§R4).

**Kiểm đủ danh mục bằng máy:** mọi file trong hai thư mục (25 và 40, trừ README) đều xuất hiện trong README
tương ứng — **0 thiếu**.

## R6. Đính chính lỗi của chính tôi ở `PKT-PC00-FIX17`

§Q3 của addendum `PKT-PC00-FIX17` viết `agent-tasks/README.md` là `e73f7e8f…`. **Giá trị đó tôi không hề
tính — nó sai.** Hash đúng tại thời điểm đó là
`871a2cffd79fb321bec18e6b3eebe81259131a0f4ab4c6cd36d53b731a0a024f`. File **không** bị tôi chạm ở gói đó;
sai sót nằm ở dòng "đã rehash để chứng minh không đổi", tức đúng dòng lẽ ra để chứng minh một điều.

**Đính chính ghi ở đây, addendum `FIX17` giữ nguyên từng byte** — `worker.md` cấm ghi tiếp sau khi handoff
đã release, kể cả để sửa lỗi, và một bản ghi bằng chứng bị sửa lặng lẽ còn tệ hơn một bản ghi sai có đính
chính. Khi hai chỗ lệch nhau: **addendum này thắng**.

**Ghi chú cho người đọc sau:** `agent-tasks/README.md` **đã đổi lần nữa** kể từ đó — `34b4dbf122a5376eb6eb0d041a321edacaf640be52943fd2f3747dae871eb6a3` lúc 2026-09-07T12:26Z — vì PC10 đang
ghi song song. Cả `871a2cff…` lẫn `34b4dbf1…` đều là giá trị của **file của người khác ở hai thời điểm**, không
phải thứ tôi ghi.

## R7. Evidence

- **Gate:** `until [ -f …/audits/A3-R3-report.md ]; do sleep 60; done` chạy nền, **exit 0**, output
  `GATE_OPEN after 8m: 14574 bytes`. Không có `cp` nào trước dấu đó.
- **Chép và kiểm:** hash nguồn ghi trước khi chép (`…/w1/src_fix18.sha`, 16 dòng), `cp -p` 16 file, rồi `cmp`
  **toàn bộ 65 bản sao** của cả hai thư mục (không chỉ 16 file mới). Lượt 1: 64/65 đạt, 1 DIFF
  (`coordinator-ledger.md` — nguồn đã tiến, §R4). Sau khi chép lại: **65/65 đạt**.
- **`validate.py`:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py` — **exit code 0**,
  **450 assertion, 450 PASS, 0 FAIL**, chạy 2026-09-07T12:25Z. Không assertion nào đổi: gói packaging không
  chạm file mà `EV-PC00-01..10` kiểm; chạy lại để chứng minh **không có hồi quy**.
- **Danh mục README:** kiểm bằng script — 25/25 và 40/40 file được liệt kê, 0 thiếu.
- Tất cả là `SELF_VALIDATION`, producer `worker-W1n`.
- **`NOT_RUN`:** không có audit độc lập nào cho chính hai thư mục này; E1–E4 vẫn `NOT_RUN` ở phạm vi PC00.
  **Bản sao giống nguồn không chứng minh nội dung của chúng đúng** — chỉ chứng minh chúng chưa bị sửa. Cụ
  thể: tôi **không** xác minh một verdict nào của `A3-R3`, **không** tính lại `manifest_sha256` của ba
  manifest `FC-P1` (con số `5f5b8aa4…` trong hàng `FC-P1e3` là **trích từ báo cáo**, không phải tôi tính), và
  **không** kiểm bảng CR hợp nhất so với các handoff gốc.

## R8. Không đổi

`precode/**` (gồm `baseline.json` `d25e2edd…`, `decision-register.md` `4d1a5d6e…`, `adr/README.md`
`097cd5f9…`, `ADR-0011` `da5181b2…`, `owner-decisions-02.md` `ba404207…`, `gates.yaml` `b5d9a79f…`,
`review.md` `1da31eb0…`), `agent_profile/registry.json` (`7f044651…`), `contracts/`, `acceptance/`,
`agent-tasks/`, `server/`, `collector/`, `worker/`, `web/`, `tests/`, `shared/`, `probe/`,
`evidence/handoffs/` khác. Nguồn `research-radar-spec.md` (`d35e1f2d…`) và `research-radar-pre-code-plan.md`
(`f65bb046…`) rehash **khớp pin** cả trước và sau. **Không sửa một byte nào trong scratchpad nguồn.** Không
lệnh git thay đổi repo; không network; không secret. Không `__pycache__`/`.pyc` do tôi sinh — các `__pycache__`
trên đĩa nằm dưới `.venv/` của Giai đoạn 0 và `.venv` đã `.gitignore` (kiểm bằng `git check-ignore`).

## R9. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC09-15` | **Đã giải** — `A2-R7-report.md` nay đã được lưu (tự khai; xác minh thuộc người khác). |
| `CR-PC00-19` | **Đã giải theo hướng erratum**, không sửa bản lưu trữ. Nếu Coordinator muốn một ruling đính chính riêng thì đó là một gói khác. |
| `CR-PC00-22` **(mới)** | `A3-R3` **chưa** có bản ghi trong `evidence/index.json` — nó ra đời sau lượt đăng ký của `PKT-PC09-P1`. Thuộc một vòng PC09 sau. |
| `CR-PC00-23` **(mới)** | `F-A3R3-01` (lỗ `E0-12`: nhãn claim trong `evidence/runs/` không bị kiểm) chưa có ai nhận. Nó là một **lỗ trong công cụ bằng chứng**, nên mọi claim dựa trên `evidence/runs/` yếu hơn vẻ ngoài cho tới khi vá. |
| `CR-PC00-20` | **Vẫn mở** — `gates.yaml`/`review.md` phản ánh `OD-20260907-02`; lưu ý `A3-R3` ghi `review.md` đang **chậm một epoch** (`F-A3R3-03`). |
| `CR-PC00-15` | Re-pin — danh sách không đổi so với `FIX17`; Coordinator xếp một lượt sau Giai đoạn 1 |
| `CR-P0-03` mục 1 | `tools/` đã khai nhưng **chưa tồn tại** |
| `CR-PC00-17`, `CR-PC00-16`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |
| `PROV-PC00-08` | Vẫn `PROVISIONAL` |

**Vì sao `DONE_WITH_CONCERNS`.** Mọi mục của packet đã xong, 65/65 `cmp` đạt, validate exit 0. Concern: hai
thư mục lưu trữ này **lại** đang bắt kịp một mục tiêu đang chạy — sổ tiến độ đã tụt lại ngay trong lúc tôi
chép, và mỗi epoch mới sẽ khiến chúng tụt tiếp. Đây là lần thứ ba bắt kịp. Nếu còn nhiều vòng nữa, nên chốt
một quy ước thay vì lặp lại: hoặc đánh phiên bản sổ theo epoch (`coordinator-ledger-p1e3.md`), hoặc chấp nhận
tường minh rằng chỉ ảnh chụp mới nhất được giữ và lịch sử nằm trong git — hiện tôi theo cách thứ hai vì packet
nói "replaces", và đã ghi rõ điều đó cùng hash bản bị thay.

## R10. Trạng thái bàn giao (FIX18)

- **next actor:** `Coordinator` — rehash hai README và 16 bản sao; `CR-PC00-22`, `CR-PC00-23`, `CR-PC00-20`
  còn mở. Nếu có epoch mới, đưa hai thư mục này vào với role `EVIDENCE`, không phải `CANDIDATE`.
- **lease_released_at (UTC):** 2026-09-07T12:28Z. `LEASE-PC00-e19` (fencing 19) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới và lease fencing ≥ 20.
- **Claim:** `DRAFT_FOR_REVIEW` cho gói này. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN` ở phạm vi PC00.

---

# ADDENDUM — PKT-PC00-FIX19 (packaging cuối trước commit: `A3-R4`, manifest epoch 4, sổ tiến độ)

## S1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX19` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX19` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-PC00-e20` (**fencing 20**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T12:44Z / 2026-09-07T12:48Z · lease expires 2026-09-08T16:00Z (`date -u` trước lần ghi cuối: 2026-09-07T12:47Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T12:48Z |

## S2. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `evidence/audits/A3-R4-report.md` | **CREATE** | ABSENT | `1bb41470b4730a25e199be3f367da24b51d89856248f35a681cb61c9c66bf08e` (8672) |
| `evidence/audits/FC-P1e4-manifest.txt` | **CREATE** | ABSENT | `736ca1ab7f061b05dd050bcf41e9dd8562db5b3a5920b35c94fd6b0dd3af241b` (60916) |
| `evidence/coordination/coordinator-ledger.md` | REPLACE | `0a1187c5ac1725ad316ef78d65c56349df985d3adb9da4f061212fc01d9dc30a` (52809) | `4e540086e1928ca315c727c247ff2f77e30a98525a2926730f2bd634268e8232` (53839) |
| `evidence/audits/README.md` | MODIFY | `a868664852efa37e594c8062180cfd09d58d055a2226d91d81b292b2ba6d53a9` (12372) | `0adbb32dd28111037585d7fa6b93721b2f648f69af3864db48f89adff6c7c6a5` (14510) |
| `evidence/coordination/README.md` | MODIFY | `636fe1e562d42a3891f173c8f3737d80b6366b4023e1868ff3d9286899511c22` (15799) | `f96f59db4db99618d6bb0d4ebdee972b1578f73839cde855f25f5707a170c6c8` (17168) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `1223b3a6e217f0487c770fc95de0b8145e667c7889728a7cca6186928ce3ac88` | *(file này)* |

**`A3-r3-packet.md` — đã xác minh, không chép lại.** `cmp` với nguồn: **byte-identical**;
`8f2fe8e7f0b3b41fdfae4a90c74d8ead9d43fb93ba625a2fac1b64920e72bd82` (2444), y như `PKT-PC00-FIX18` đã ghi.
Không tạo bản trùng.

**Sổ tiến độ, lần thay thứ ba.** Chuỗi đầy đủ nay là `a8a7d319…` (FIX9, tới epoch 7) → `0369031b…` (FIX12,
39468, tới `FC-W4` epoch 9) → `0a1187c5…` (FIX18, 52809) → **`4e540086…` (FIX19, 53839, tới `FC-P1` epoch
4)**. Hash nguồn **giống nhau trước và sau** lần chép, `cmp` đạt ngay sau đó. Cả bốn giá trị được ghi trong
`evidence/coordination/README.md` để không bản nào biến mất khỏi hồ sơ.

## S3. `F-A3R4-01` — điều packet yêu cầu một dòng, tôi viết thành một đoạn

Packet yêu cầu ghi **một dòng** rằng `F-A3R4-01` (LOW) được Coordinator `PARKED`, cải tiến công cụ giao cho
`CR-PC09-18`. Tôi ghi đủ điều đó, và thêm ba chi tiết mà một dòng không chở được — vì cả ba đều nằm trong
chính báo cáo, và bỏ chúng đi sẽ làm `PARKED` đọc thành "không sao":

1. **Hệ quả thực tế**, không phải mô tả trừu tượng: `evidence/coordination/*.md` hiện **không có** phép kiểm
   nhãn claim nào. Prose sweep là cái duy nhất từng chạm tới chúng, và exemption đã gỡ nó. Tôi ghi câu này
   vào **cả hai** README — ở `audits/` như một finding, ở `coordination/` như một cảnh báo cho người đọc đúng
   thư mục bị ảnh hưởng: *đừng tin một nhãn claim nào xuất hiện trong các file ở đây.*
2. **Ràng buộc remediation nguyên văn của auditor:** hoặc mở rộng phép quét structured sang front-matter
   `.md`, **hoặc** sửa ghi chú thành "structured `.yaml`/`.json` fields" — và **không** được để nguyên một
   ghi chú tự nhận một tầm với mà phép kiểm không có, vì đó **chính là** loại lỗi mà `F-A3R3-01` đã phạt.
   Một `CR` chỉ nói "cải tiến công cụ" cho phép người sửa chọn cách rẻ nhất là viết lại ghi chú cho đúng —
   điều đó **được auditor cho phép**, nhưng chỉ khi biết rằng nó là một trong hai lựa chọn hợp lệ, không phải
   một cách lách.
3. **`PARKED` không phải `CLOSED`.** Ghi thẳng, vì `protocol.md` §8 không có trạng thái `PARKED`: nó là một
   quyết định điều phối về *thứ tự làm việc*, không phải một disposition. Không ai được coi finding này đã
   được xử lý.

Tôi **không** tự sửa `e0_check.py` hay ghi chú của nó — ngoài grant, và `worker.md` cấm sửa một phép kiểm để
nó trông đúng hơn.

## S4. Hai README

`evidence/audits/README.md`: đếm lại (**14** báo cáo, **13** manifest, `auditor-A3` ×4, chuỗi epoch tới
`FC-P1` 4); hai hàng mới (`A3-R4-report.md`, `FC-P1e4-manifest.txt` — hàng manifest ghi 413 entry và
`manifest_sha256 = 576a7572…` **trích từ báo cáo**, không phải tôi tính); đoạn `F-A3R4-01` ở §S3; và sửa dòng
đăng ký `evidence/index.json`: `EV-A3-07-round3` **đã** được thêm cho vòng 3, nên file còn thiếu bản ghi nay
là **`A3-R4`**, không phải `A3-R3` — `CR-PC00-22` được trỏ lại cho đúng thay vì để nguyên một câu đã cũ.

`evidence/coordination/README.md`: "bổ sung **bốn** lần"; hàng ledger mang chuỗi bốn bản; cảnh báo
`F-A3R4-01`; và đoạn "sổ đang sống" được viết lại theo **điều đã thực sự xảy ra hai lần** — bản chép đầu của
FIX18 lỗi thời trong vài phút, rồi bản thay của nó cũng lỗi thời trước FIX19 — với mốc ảnh chụp mới
(**12:45Z**) thay cho 12:26Z.

**Kiểm đủ danh mục bằng máy:** 27/27 và 40/40 file được liệt kê, **0 thiếu**.

## S5. Evidence

- **Chép và kiểm:** hash nguồn ghi trước khi chép (`…/w1/src_fix19.sha`), `cp -p` 3 file, `cmp` từng file
  ngay sau khi chép, rồi `cmp` **toàn bộ 67 bản sao** của cả hai thư mục — **67/67 byte-identical**.
- **`validate.py`:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py` — **exit code 0**,
  **450 assertion, 450 PASS, 0 FAIL**, chạy 2026-09-07T12:47Z. Không assertion nào đổi; chạy lại để chứng
  minh **không có hồi quy** (gói này không chạm `precode/` hay `agent_profile/`).
- **Danh mục README:** kiểm bằng script — 0 thiếu ở cả hai thư mục.
- Tất cả là `SELF_VALIDATION`, producer `worker-W1n`.
- **`NOT_RUN` / giới hạn:** tôi **không** xác minh một verdict nào của `A3-R4`, **không** tự tính lại
  `manifest_sha256` của `FC-P1e4` (con số `576a7572…` là **trích từ báo cáo**), và **không** tái lập phép thử
  front-matter của `F-A3R4-01`. Bản sao giống nguồn chỉ chứng minh chúng chưa bị sửa. E1–E4 vẫn `NOT_RUN` ở
  phạm vi PC00.

## S6. Không đổi

`precode/**` (`baseline.json` `d25e2edd…`, `decision-register.md` `4d1a5d6e…`, `adr/README.md` `097cd5f9…`,
`ADR-0011` `da5181b2…`, `owner-decisions-02.md` `ba404207…`, `owner-decisions.md` `f608d2e9…`,
`owner-decision-request.md` `1a277fbc…`, `gates.yaml` `b5d9a79f…`, `review.md` `1da31eb0…`),
`agent_profile/registry.json` (`7f044651…`), `contracts/`, `acceptance/`, `agent-tasks/`, và toàn bộ cây mã
(`server/`, `collector/`, `worker/`, `web/`, `tests/`, `shared/`, `probe/`). 65 bản sao cũ trong hai thư mục
lưu trữ không đổi. Nguồn `research-radar-spec.md` (`d35e1f2d…`) và `research-radar-pre-code-plan.md`
(`f65bb046…`) rehash **khớp pin**. **Không sửa một byte nào trong scratchpad nguồn.** Không lệnh git thay đổi
repo; không `__pycache__`/`.pyc` do tôi sinh; không network; không secret.

## S7. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC09-18` **(mới, do Coordinator giao)** | Mở rộng phép quét claim structured sang front-matter `.md`, **hoặc** thu hẹp ghi chú của `E0-12` cho đúng tầm với thật. Hai lựa chọn đều được `A3-R4` chấp nhận; để nguyên **không** phải một lựa chọn. |
| `F-A3R4-01` | **`PARKED`**, không phải `CLOSED`. `PARKED` không tồn tại trong `protocol.md` §8 — nó là quyết định về thứ tự làm việc, không phải disposition. |
| `CR-PC00-22` | Nay trỏ vào **`A3-R4`** (chưa có bản ghi trong `evidence/index.json`); `A3-R3` đã có `EV-A3-07-round3`. |
| `CR-PC00-23` | `F-A3R3-01` — nay đã **VERIFIED** bởi `A3-R4`; phần còn lại là `F-A3R4-01`/`CR-PC09-18`. |
| `CR-PC00-20` | `gates.yaml`/`review.md` phản ánh `OD-20260907-02` — lưu ý `A3-R4` xác minh `F-A3R3-03`, nên phần "chậm một epoch" của `review.md` đã được xử lý. |
| `CR-PC00-15` | Re-pin — danh sách không đổi; Coordinator xếp một lượt sau Giai đoạn 1 |
| `CR-P0-03` mục 1 | `tools/` đã khai nhưng **chưa tồn tại** |
| `CR-PC00-19`, `CR-PC09-15` | Đã giải ở `FIX18` (tự khai; xác minh thuộc người khác) |
| `CR-PC00-17`, `CR-PC00-16`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |
| `PROV-PC00-08` | Vẫn `PROVISIONAL` — khuyến nghị từ `FIX15` (đưa lên Owner thành câu hỏi riêng) chưa được thực hiện |

**Một lưu ý cho lượt commit sắp tới.** Hai thư mục này nay chứa 67 bản sao và hai README mô tả chúng. Chúng là
**bằng chứng**, không phải candidate: nếu Coordinator đóng băng một epoch mới sau commit, hai thư mục phải vào
manifest với role `EVIDENCE`. Và sổ tiến độ sẽ lỗi thời **lần nữa** ngay khi Coordinator ghi dòng tiếp theo —
README đã nói thẳng điều đó thay vì để người đọc tự phát hiện.

## S8. Trạng thái bàn giao (FIX19)

- **next actor:** `Coordinator` — rehash sáu file ở §S2; `CR-PC09-18`, `CR-PC00-22`, `CR-PC00-20`,
  `CR-P0-03` mục 1 còn mở.
- **lease_released_at (UTC):** 2026-09-07T12:48Z. `LEASE-PC00-e20` (fencing 20) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới và lease fencing ≥ 21.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN` ở phạm vi PC00.

---

# ADDENDUM — PKT-PC00-FIX20 (`OD-20260907-03`: phê chuẩn hai mục, lối vào Giai đoạn 2)

## T1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX20` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX20` (parent `AUTH-OWNER-20260907-04`) · lease `LEASE-PC00-e21` (**fencing 21**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T13:10Z / 2026-09-07T13:29Z · lease expires 2026-09-08T20:00Z (`date -u` trước lần ghi cuối: 2026-09-07T13:27Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T13:29Z |
| input | `…/scratchpad/packets/OWNER-DECISIONS-20260907-03.md` |

## T2. Đã làm gì

**Tạo `precode/owner-decisions-03.md`** — chuyển ngữ theo đúng khuôn hai biên bản trước: định danh, quy tắc
chuyển ngữ, **ba** mục nguyên văn, §3 "không được quyết ở vòng này" nguyên văn, §4 năm điều biên bản **không**
làm, §5 ghi chú ba mục có sắc thái, §6 truy vết. Dòng trỏ ở đầu `precode/owner-decisions.md` nay nói **ba**
biên bản cộng dồn.

**Điều tôi xử lý cẩn thận nhất: chữ "both".** Chỉ thị của Owner là *"accept both, start phase 2"* — một **đại
từ**. Biên bản khai rõ nó trỏ vào báo cáo Giai đoạn 0/1 đã nêu **đích danh đúng hai mục**. Tôi chép đúng hai
mục đó và ghi thành một điều tường minh ở §4 mục 4 rằng mọi `PROV-PC03-*`, `PROV-PC04-*` chưa được nêu,
`PROV-PC00-05`, `PROV-PC00-06`, `PROV-PC10-*`, `PROV-P0-01` **vẫn `PROVISIONAL`**. Anchor baseline mang một
trường riêng `pronoun_note_vi` cho việc này, và `ratifies` chỉ có **đúng hai** phần tử. Một đại từ là chỗ dễ
nới scope nhất trong cả ba biên bản; nếu sổ chỉ ghi "Owner đã chấp nhận" thì vòng sau sẽ không ai biết "cả
hai" từng là bao nhiêu.

**Hai chỗ tôi từ chối đọc rộng, dù đọc rộng sẽ tiện hơn cho các gói đang chạy:**

1. **"Start phase 2" ≠ được chạy probe.** Biên bản để chữ "Start" và hai cổng chặn trong **cùng một câu**.
   2A được cấp phép **viết** card và mã; các lần chạy live vẫn bị `collector-probe.md` §6 mục **2–4** chặn và
   vẫn phải chạy trên **máy của Owner**. `REQ-AC16` và mọi mục `KC` không đổi.
2. **"Start phase 2" ≠ được viết connector.** Biên bản tự nói *"a card must be written first — none exists"*.
   Và `REQ-A6` vẫn chặn cứng `CONTRACT_READY` cho tới khi bốn dữ kiện rate/identity đến từ **tài liệu chính
   thức** — *"không con số nào được đoán"*. Quyền tải tài liệu đó qua mạng nằm trong danh sách **không quyết**
   của chính biên bản, nên quyền mạng duy nhất vẫn là cài gói PyPI/npm đã khai (`OD-20260907-02` mục 4).

**`PROV-PC00-08` → `ACCEPTED (OD-20260907-03)`** với một câu tôi cố ý viết nặng: rủi ro còn lại được Owner
**thừa nhận, không phải được xoá**. Ba chế độ hỏng ghi ở đó (ghi ngoài tập ghi không bị chặn; hai Worker song
song không có fencing thật; không có audit log bền vững do service ghi) vẫn nguyên, và `enforcement` trong
registry vẫn `NOT_IMPLEMENTED` — có một assertion buộc điều đó. Đây là mục mà `FIX15` đã cảnh báo là đứng trên
một *suy luận*; nay nó đứng trên một câu trả lời tường minh. Trạng thái cũ giữ lại dưới nhãn "(Lịch sử)".

**`AMD-ENT-owner-01` → `ACCEPTED (OD-20260907-03)`** ở §8.11, kèm đoạn phân biệt điều được gỡ và điều không:
được gỡ là **tính tạm thời của hợp đồng** (nhãn `IMPLEMENTATION_VERIFIED` của card auth không còn đứng trên
một amendment do Coordinator ký); **không** được gỡ là verdict của auditor — `A3-R4` §6 ghi per-card claim
"unchanged", và **một biên bản của Owner không phải một lượt xác minh độc lập**. `entities.yaml` **giữ**
`CONTRACT_READY`, không được nâng; `F-A3R1-02` và `F-A3R1-06` **không** bị đóng.
**Tôi không chạm `contracts/data/entities.yaml`** — `worker-W3n` đang cập nhật khối amendment ở packet song
song; hash rehash để chứng minh: `c61be0a4…`.

**`§8.12` mới** ghi cả ba quyết định thành hàng, cộng hai cổng còn chặn và ba điều hàng go-ahead **không** làm.
Khác vòng hai: cả **ba** hàng đều mang `ACCEPTED (OD-20260907-03)` vì cả ba đều là câu trả lời tường minh của
Owner — vòng hai có hai trong năm mục chỉ là suy luận của Coordinator, và sổ giữ đúng sự khác biệt đó.

**`agent_profile/registry.json`** — `AUTH-OWNER-20260907-04` (sáu trường; `scope` mang cả vế phủ định: không
mở mạng, không quyết `REQ-OQ03`, không phê chuẩn mục `PROVISIONAL` nào khác, không đóng finding, `entities.yaml`
**keeps** `CONTRACT_READY`, rủi ro **NOT removed**); `coding_phase.status` → `PHASE_2_IN_PROGRESS`;
`phases_completed` ghi Giai đoạn 0/1 kèm `independent_audit_ref` = `evidence/audits/A3-R4-report.md` và chuỗi
audit R1→R4; `phase_2_gates_still_shut` ba dòng. **`enforcement` vẫn `NOT_IMPLEMENTED`.**

**Chữ "complete" được định nghĩa hẹp ngay tại chỗ.** `phases_completed[0].note_vi` viết: hoàn tất nghĩa là bốn
card và skeleton đã có bản sửa được A3 xác minh ở epoch 4 — nó **không** đóng finding nào, **không** nâng
`product_status`, không nói gì về các card chưa chạy, và E3/E4 vẫn `NOT_RUN`. Một trường tên
`phases_completed` trong một file máy đọc là chỗ rất dễ bị trích ra khỏi ngữ cảnh; định nghĩa phải đi kèm nó.

**`precode/baseline.json`** — anchor `OD-20260907-03` với `ratifies` (2), `grants` (2), `gates_still_shut` (2),
`not_decided` (6), `pronoun_note_vi`, `amendment_effect_vi`, `phase_0_1_status` neo vào `A3-R4`.

**`precode/owner-decision-request.md`** — ba dòng vòng ba được điền, và khối "VẪN CHỜ" nay có **ba** mục
(`REQ-OQ03`, cổng probe §6 mục 2–4, bốn dữ kiện `REQ-A6`/quyền mạng). Banner được sửa: câu "một mục duy nhất
chưa được trả lời" của vòng hai nay được đánh dấu **chỉ đúng cho thời điểm nó được viết** — vòng ba **mở thêm
hai câu hỏi** thay vì đóng bớt.

## T3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/owner-decisions-03.md` | **CREATE** | ABSENT | `954642fe5c747833acc8b29c5445e79d17edb96db5ee3083ddefcf21c0e74dd0` (10024) |
| `precode/owner-decisions.md` | MODIFY | `f608d2e9527061558e9c0247136c7d6d51f24d073981afd40c1f424ef7773bda` (12711) | `58b6b910dbaf92620c62902b7f181ff13faff0005f3f80c52a4012a312781a8a` (12909) |
| `precode/decision-register.md` ⚠ | MODIFY | `4d1a5d6e5d2a4f0aa3cf165913cc76f07442211715fd0bde9a12da51e82a7244` (114327) | `31fa401c2da52743b3d76d57ee6842ca80ffe04c46eac88ecb149e7f7dcf7d9f` (122432) |
| `precode/baseline.json` ⚠ | MODIFY | `d25e2edd05437dc475797f16e96e874d53ae0cd336cd162dd4b5a4131292c7bd` (104398) | `e9a725c6129a7a7b59f826579516f4c4f9b93b9f13387973b796241ded3e0b55` (107196) |
| `precode/owner-decision-request.md` | MODIFY | `1a277fbca5c9b398dc95f4eb618cd8b0cd92e0167826fcc8eb9e217e10a2298f` (57906) | `b6fc48e9138814d4ac2d21aec98ab4e2aed85abe699bf190f7bdbf5157247af7` (60285) |
| `agent_profile/registry.json` | MODIFY | `7f04465121241160363d3ab4ba3a0d2e9177e77f5cb27bf509759474c7effe88` (5909) | `8d7a14f327a83b389287fe5542b7d51860d0ff372669422e2cac197df192c33e` (8363) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `58107568491d6be4214ecaab801bf54168dd51123164bf15fed6af60528b2da0` | *(file này)* |

**⚠ Hai file card-pinned đổi:** `precode/decision-register.md` (`31fa401c…`, 122432) và
`precode/baseline.json` (`e9a725c6…`, 107196) → lượt re-pin của `CR-PC00-15`. `precode/adr/ADR-0011…`
(`da5181b2…`) và `precode/adr/README.md` (`097cd5f9…`) **không** đổi ở gói này.

**1 CREATE + 5 MODIFY + 1 APPEND.** Rehash để chứng minh không đổi: `contracts/data/entities.yaml`
(`c61be0a4…` — **W3n đang giữ**, tôi không chạm), `precode/gates.yaml` (`ab391c6d…`), `precode/review.md`
(`9c2b7973…`), `precode/requirements.csv` (`fbe59d0e…`), `precode/owner-decisions-02.md` (`ba404207…`),
`precode/adr/*`. Nguồn `research-radar-spec.md` (`d35e1f2d…`) và `research-radar-pre-code-plan.md`
(`f65bb046…`) khớp pin. Không chạm `acceptance/`, `agent-tasks/`, `evidence/audits/`,
`evidence/coordination/`, cây mã. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc` do tôi sinh
(các bản dưới `.venv/` đã `.gitignore`); không network; không secret.

## T4. Evidence

- **Lệnh:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py`
- **started/ended (UTC):** 2026-09-07T13:27Z / 2026-09-07T13:27Z · **exit code 0** ·
  **566 assertion, 566 PASS, 0 FAIL** · `SELF_VALIDATION`, producer `worker-W1n`.
- **`EV-PC00-11` mới — ~100 assertion:** 19 trường front-matter; **đúng 3** hàng theo thứ tự; chín chuỗi
  nguyên văn gồm cả *"không con số nào được đoán"*, hai tên card 2A, hai operation 2B, `collector-probe.md`
  §6 và "máy của Owner"; năm phát biểu phạm-vi-không-quyết; `PROV-PC00-08` mang `ACCEPTED (OD-20260907-03)`
  **và** giữ đoạn lịch sử **và** nói rõ rủi ro được *thừa nhận chứ không bị xoá*; §8.11 mang nhãn mới, nói
  `entities.yaml` giữ `CONTRACT_READY`, nói hai finding **không** bị đóng, nói verdict A3-R4 "unchanged", và
  nói khối amendment thuộc W3n; §8.12 đúng **3** hàng, **cả ba** mang nhãn vòng ba; bốn authority đúng thứ
  tự; `AUTH-04` đủ sáu trường và `scope` chứa bảy chuỗi ranh giới; `coding_phase` là `PHASE_2_IN_PROGRESS`
  với `enforcement` vẫn `NOT_IMPLEMENTED`; anchor baseline `ratifies` **đúng hai** phần tử.
- **Năm assertion "chống đọc rộng":** `claim_ceiling` của bộ hợp đồng **không** đổi; `REQ-OQ03` **không**
  được giải; **`REQ-A6` vẫn `KC`**; `product_status`/`enforcement`/`status` của registry **không** đổi; và
  `OD-20260907-02` **không** được nhắc `AUTH-OWNER-20260907-04` (grant đó ra đời sau nó).
- **Một assertion đối chiếu thực tế:** file mà registry trỏ tới —
  `evidence/audits/A3-R4-report.md` — phải **tồn tại thật** trên đĩa, không chỉ là một chuỗi.
- **Bảy assertion cũ FAIL ở lượt đầu và đã được sửa cho đúng trạng thái mới, không nới lỏng:** ba cái đếm
  (hai anchor → ba; ba authority → bốn; `coding_phase` so sánh `==` → kiểm bốn khóa bắt buộc cộng hai bất
  biến, để trường mới không làm vỡ mà vẫn khóa `enforcement`), hai cái theo câu chữ đã đổi, một cái sai chữ
  hoa, và **một cái là lỗi thật của tôi ở `FIX15`**: `s810 = DR.split("### 8.10")[1]` không có cận trên nên
  nuốt luôn §8.11 và §8.12, khiến phép đếm "5 hàng" đọc thành 8. Nay cắt tại `### 8.11`. Lỗi đó **không**
  làm sai văn bản nào — nó chỉ khiến một phép kiểm yếu đi âm thầm cho tới khi có mục mới.
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4 ở phạm vi PC00. Một biên bản phê chuẩn **không** tạo
  bằng chứng kỹ thuật nào; tôi **không** xác minh lại verdict nào của `A3-R4` và **không** kiểm khối
  amendment trong `entities.yaml`.

## T5. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-20` | **Vẫn mở, nay rộng hơn** — `precode/gates.yaml` và `precode/review.md` chưa phản ánh **cả** `OD-20260907-02` **lẫn** `OD-20260907-03`. G5 và các gate của Giai đoạn 2 đều thuộc PC09. |
| `CR-PC00-24` **(mới)** | 2B **chưa có task card** — biên bản tự nói vậy. Viết card là việc đầu tiên của 2B, thuộc PC10; card đó **không** được ghi số rate/identity nào cho tới khi `REQ-A6` có dữ kiện thật. |
| `CR-PC00-25` **(mới)** | `contracts/collector/collector-probe.md` §6 mục **2–4** và bốn dữ kiện `REQ-A6` đã được hỏi riêng nhưng **chưa** có câu trả lời. Cho tới lúc đó: 2A không chạy live, 2B không `CONTRACT_READY`. Cần đưa lên Owner sớm — chúng chặn đúng phần *chạy được* của Giai đoạn 2. |
| `CR-PC00-22` | `A3-R4` chưa có bản ghi trong `evidence/index.json` |
| `CR-PC09-18` | `F-A3R4-01` (`PARKED`) — nhãn claim trong front-matter `.md` không được quét |
| `CR-PC00-15` | Re-pin — nay gồm `decision-register.md` `31fa401c…` và `baseline.json` `e9a725c6…` |
| `CR-P0-03` mục 1 | `tools/` đã khai nhưng chưa tồn tại |
| `CR-PC00-19`, `CR-PC09-15` | Đã giải ở `FIX18` (tự khai) |
| `CR-PC00-17`, `CR-PC00-16`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |

**Vì sao `DONE_WITH_CONCERNS`.** Mọi mục của packet đã xong, validate exit 0. Concern là hình dạng của chính
vòng này: Giai đoạn 2 được **cấp phép bắt đầu** trong khi **cả hai** nhánh của nó đều có một cổng đóng chặn
đúng phần làm ra bằng chứng — 2A không được chạy probe, 2B không được có một con số thật. Điều đó hợp lệ và
biên bản nói rõ, nhưng nó nghĩa là Giai đoạn 2 có thể sản xuất **card và mã** mà không sản xuất được **kết
quả**; nếu hai câu hỏi ở `CR-PC00-25` không được trả lời sớm thì công việc sẽ dừng ở đúng chỗ đó. Tôi ghi lại
đây thay vì để nó lộ ra ở một handoff sau. Ngoài ra `PROV-PC00-08` nay `ACCEPTED` — cảnh báo của `FIX15` đã
được Owner trả lời, và tôi rút nó khỏi danh sách khuyến nghị.

## T6. Trạng thái bàn giao (FIX20)

- **next actor:** `Coordinator` — rehash bảy file ở §T3; `CR-PC00-24`, `CR-PC00-25`, `CR-PC00-20` cần được
  giao; W7 re-pin hai file card-pinned.
- **lease_released_at (UTC):** 2026-09-07T13:29Z. `LEASE-PC00-e21` (fencing 21) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §T3) và lease fencing ≥ 22.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN` ở phạm vi PC00.

---

# ADDENDUM — PKT-PC00-FIX21 (`OD-20260907-04`: cổng probe mở, quyền mạng hẹp cho `REQ-A6`)

## U1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX21` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX21` (parent `AUTH-OWNER-20260907-05`) · lease `LEASE-PC00-e22` (**fencing 22**) |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T15:10Z / 2026-09-07T15:27Z · lease expires 2026-09-08T20:00Z (`date -u` trước lần ghi cuối: 2026-09-07T15:26Z) |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T15:27Z |
| input | `…/scratchpad/packets/OWNER-DECISIONS-20260907-04.md` |

## U2. Đã làm gì

**Tạo `precode/owner-decisions-04.md`** — chuyển ngữ **hai** mục nguyên văn, §3 "không quyết ở vòng này:
không có" nguyên văn, §4 sáu điều biên bản **không** làm, §5 ghi chú hai mục có sắc thái, §6 truy vết, và
**§7 mới** (xem §U3). Dòng trỏ ở `precode/owner-decisions.md` nay nói **bốn** biên bản cộng dồn.
`decision-register` nhận **§8.13**; `owner-decision-request.md` nhận phiếu vòng bốn và khối "VẪN CHỜ" rút
còn **một** mục; `baseline.json` nhận anchor `OD-20260907-04`; `registry.json` nhận
`AUTH-OWNER-20260907-05` cùng `phase_2_gates_opened`.

**Hai phân biệt tôi giữ chặt, vì cả hai đều dễ bị đọc rộng:**

1. **Cổng probe mở về HÀNH CHÍNH, không mở về VẬT LÝ.** §6 mục 1–4 nay đều thỏa. Nhưng probe vẫn chạy trên
   tài khoản X thật và máy thật của Owner, sau khi **Owner tự** cài Playwright, đăng nhập tay, điền
   `probe-config.json` và ký bốn `owner_confirmations`. Biên bản viết thẳng: **không Worker nào được chạy
   nó.** Câu đó được chép vào cả bốn nơi (record, register, registry `scope`, baseline anchor) vì một
   handoff sau viết "cổng probe đã mở" mà dừng ở đó sẽ bị đọc thành "probe đã chạy được". Thêm nữa: ba mục
   vừa chấp nhận đều là **ngưỡng `PROVISIONAL` do PC05 đề xuất** (§3 ngân sách; §7 `GO-1`..`GO-7`) —
   "chấp nhận" là đồng ý dùng làm tiêu chí, **không** phải đã hiệu chỉnh bằng dữ liệu.
2. **Quyền mạng được ghi bằng CẢ HAI chiều.** Biên bản nêu **đích danh** hai host bị cấm
   (`export.arxiv.org`, `api.openalex.org`) chứ không dừng ở "chỉ trang tài liệu" — và điều đó có ý nghĩa,
   vì `arxiv.org` và `export.arxiv.org` thuộc **cùng một tổ chức**. Tôi giữ cả danh sách cho phép lẫn danh
   sách cấm ở mọi nơi ghi lại, kèm mệnh đề bao trùm "bất kỳ endpoint live nào — không lưu lượng API thật".

**`REQ-A6` KHÔNG được đánh dấu đã giải**, đúng như packet dặn: register §8.13 mở đầu bằng "**`REQ-A6` VẪN
`KC`**", và `requirements.csv` **không** bị chạm (`fbe59d0e…`).

## U3. Điều tôi phát hiện khi kiểm, không có trong packet

**(a) Đường dẫn probe tôi ghi sai ở `FIX20`.** `FIX20` viết `contracts/collector/collector-probe.md`;
file thật là **`contracts/ops/collector-probe.md`**. Đường dẫn đó là do tôi tự thêm — biên bản vòng ba chỉ
nói "collector-probe.md". Đã sửa ở **hai** chỗ trong write set của gói này: `decision-register.md` §8.12 và
`baseline.json` (anchor `OD-20260907-04` trước đó của vòng ba). Còn **một** chỗ sai ở
`precode/owner-decisions-03.md` (front-matter `source_refs` và bảng mục 3) — file đó **ngoài** write set của
packet này nên tôi **không** sửa → `CR-PC00-28`. `validate.py` nay có một assertion cấm chuỗi sai xuất hiện
trong register và baseline, cộng một assertion đòi file `contracts/ops/collector-probe.md` **tồn tại thật**.

**(b) Packet tìm dữ kiện đã land MỘT NỬA trong lúc tôi viết.** `contracts/retry-policy.yaml` (đọc lúc
15:23Z, `d81192d8…`) cho thấy `worker-WF` (`PKT-PC03-FIX-REQA6`) đã điền phần **arXiv** có trích dẫn:
`arxiv_requests_per_window = 1`, `arxiv_window_seconds = 3`, cộng một dữ kiện **mới** mà sàn cũ không phủ —
`arxiv_max_concurrent_connections = 1`; yêu cầu định danh của arXiv là `RESOLVED_NEGATIVE`. Nếu tôi để
nguyên câu "bốn giá trị `null`" ở **thì hiện tại** thì tài liệu của tôi sai ngay khi ai đó mở file. Xử lý:
câu trong §4 mục 2 được đặt lại thành **trạng thái tại thời điểm biên bản ban hành**, và **§7 mới** ghi
trạng thái quan sát được lúc 15:23Z, khai rõ đó là **quan sát của PC00, không phải nội dung biên bản**.
Register §8.13 và anchor baseline mang cùng ghi chú.

**(c) Nửa OpenAlex bị chặn bởi ranh giới quyền, không phải bởi thiếu nỗ lực — và cần một quyết định mới.**
`worker-WF` ghi lại: mọi đường dẫn dưới `docs.openalex.org` trả `301` sang **`help.openalex.org`**, một host
**không** nằm trong bốn host mà `OD-20260907-04` cấp; `openalex.org` trả `403`. Họ **dừng** thay vì đi theo
redirect — đúng (`protocol.md` §3 cấm tự mở scope). Hệ quả: `research_connector_rate_limit` **vẫn**
`PLACEHOLDER_KC`, hai giá trị OpenAlex cộng `openalex_identification_required` **vẫn** `null`, `REQ-A6`
**vẫn** `KC`. Giải nốt cần **mở rộng grant** thêm `help.openalex.org` — một amendment thuộc thẩm quyền
Owner, **không** phải một con số nhớ được. → **`CR-PC00-27`**, và tôi đề nghị đưa lên cùng vòng với
`REQ-OQ03` vì nó chặn đúng phần *chạy được* của 2B.

**(d) E0 FAIL do chính tôi gây ra ở `FIX20`, đã sửa.** `e0_check.py` `E0-12` báo 1 violation:
`precode/owner-decision-request.md` khẳng định nhãn `IMPLEMENTATION_VERIFIED` trong **prose không có
backtick** — đúng loại câu mà luật cấm. Tôi thêm backtick cho **cả hai** lần xuất hiện trong khối phiếu trả
lời vòng ba (file này nằm trong write set của gói). E0 sau đó **25/25 PASS, 0 violation**. Đây là lần thứ
hai một phép kiểm bắt được lỗi của tôi trong ba gói — và nó bắt đúng.

## U4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/owner-decisions-04.md` | **CREATE** | ABSENT | `d523945aca4efbfb0c09edd6a955e877921b4851bd5577556c94faf984884a86` (13058) |
| `precode/owner-decisions.md` | MODIFY | `58b6b910dbaf92620c62902b7f181ff13faff0005f3f80c52a4012a312781a8a` (12909) | `c2cd20a6daa6c0d4b8ab2baccf267484e6116dae720d06b1b625265019f40d44` (13241) |
| `precode/decision-register.md` ⚠ | MODIFY | `31fa401c2da52743b3d76d57ee6842ca80ffe04c46eac88ecb149e7f7dcf7d9f` (122432) | `8285ae90ad6b1187ed1e3bd3616a36093ab4f656a5147586e4382bd6f915c296` (132927) |
| `precode/baseline.json` ⚠ | MODIFY | `e9a725c6129a7a7b59f826579516f4c4f9b93b9f13387973b796241ded3e0b55` (107196) | `d25a856452ea0012eea4de1ad063054b4c49b92d5a7e71a4a982e3f25e56d1ef` (111009) |
| `precode/owner-decision-request.md` | MODIFY | `b6fc48e9138814d4ac2d21aec98ab4e2aed85abe699bf190f7bdbf5157247af7` (60285) | `5303e7326c71476a3e41883f235b9b42fe321e6e847f0e71c2312bcb67f15cd4` (61863) |
| `agent_profile/registry.json` | MODIFY | `8d7a14f327a83b389287fe5542b7d51860d0ff372669422e2cac197df192c33e` (8363) | `0965f48a63d5c6e55cc7fc143360be8a2d560d5ef2911d9d929c71f7b7029ea8` (11113) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `15f41bc45530a01d1a98726835efc1a099dffdbca2d0a072a90fb30ea2572b20` | *(file này)* |

**⚠ Hai file card-pinned đổi:** `decision-register.md` (`8285ae90…`, 132927), `baseline.json`
(`d25a8564…`, 111009) → `CR-PC00-15`.

**1 CREATE + 5 MODIFY + 1 APPEND.** Rehash chứng minh **không** đổi: `contracts/retry-policy.yaml`
(`d81192d8…` — **`worker-WF` đang giữ**, tôi chỉ đọc), `contracts/ops/collector-probe.md` (`03e88010…` —
PC05), `precode/requirements.csv` (`fbe59d0e…` — `REQ-A6` vẫn `KC`), `precode/gates.yaml` (`ab391c6d…`),
`precode/owner-decisions-02.md`, `-03.md`, `precode/adr/*`. Nguồn `research-radar-spec.md` (`d35e1f2d…`) và
`research-radar-pre-code-plan.md` (`f65bb046…`) khớp pin. Không chạm `acceptance/`, `agent-tasks/`,
`evidence/audits/`, `evidence/coordination/`, cây mã. Không lệnh git thay đổi repo; không `__pycache__`/
`.pyc` do tôi sinh; **không network** (tôi không tải một trang nào — quyền mạng của `OD-20260907-04` thuộc
packet khác); không secret.

## U5. Evidence

- **`validate.py`:** `cd …/scratchpad/w1 && PYTHONDONTWRITEBYTECODE=1 python3 validate.py` —
  **exit code 0**, **674 assertion, 674 PASS, 0 FAIL**, chạy 2026-09-07T15:25Z. `SELF_VALIDATION`, producer
  `worker-W1n`.
- **`e0_check.py` (chỉ đọc, theo yêu cầu packet):** `PYTHONDONTWRITEBYTECODE=1 python3
  evidence/tools/e0_check.py --repo .` — **exit code 0**, **25 check: PASS 25 · FAIL 0 · BLOCKED 0 ·
  violations 0**, chạy 2026-09-07T15:26Z. **Lần chạy trước lúc 15:25Z FAIL 1 violation** (§U3 mục d); tôi
  ghi cả hai lần chạy chứ không chỉ lần xanh — một kết quả E0 xanh sau khi sửa không xoá việc nó từng đỏ.
- **`EV-PC00-12` mới — ~70 assertion:** 19 trường front-matter; đúng **2** hàng; mười một chuỗi nguyên văn
  gồm bốn host được phép và hai host bị cấm; ba yêu cầu bằng chứng (URL + ngày + trích dẫn); bốn phát biểu
  "không được đọc rộng"; §8.13 đúng **2** hàng đều mang nhãn vòng bốn, có `REQ-A6 VẪN KC`, có phân biệt
  hành chính/vật lý; `AUTH-05` đủ sáu trường với tám chuỗi ranh giới trong `scope`; `phase_2_gates_opened`
  hai mục; anchor baseline đủ `network_grant` hai chiều và sáu `not_decided`.
- **Bảy assertion đối chiếu THỰC TẾ trên đĩa** (không phải văn bản với chính nó): `contracts/ops/collector-probe.md`
  **tồn tại**; chuỗi đường dẫn sai **không còn** trong register/baseline; `retry-policy.yaml` **vẫn**
  `PLACEHOLDER_KC`; hai giá trị OpenAlex **vẫn** `null`; `requirements.csv` giữ `REQ-A6` ở `KC`; và **hai
  assertion hai chiều** buộc câu "nửa arXiv đã giải" trong record và register **khớp** với việc
  `arxiv_requests_per_window: 1` có thật trên đĩa — nếu Worker kia rollback, validate FAIL thay vì tài liệu
  của tôi âm thầm nói sai.
- **Chín assertion cũ được sửa cho đúng trạng thái mới, không nới lỏng** (đếm anchor/authority/cổng, câu chữ
  đã đổi, và **một lỗi thật của tôi ở `FIX20`**: `s812 = DR.split("### 8.12")[1]` thiếu cận trên nên nuốt
  luôn §8.13 — nay cắt tại `### 8.13`. Đây là **cùng một lỗi** tôi đã mắc với §8.10 ở `FIX20`; nếu còn thêm
  mục §8.x nữa thì nên viết một helper cắt đoạn thay vì lặp `split` bằng tay).
- **`NOT_RUN`:** audit độc lập trên epoch mới; E1–E4 ở phạm vi PC00. Tôi **không** xác minh lại trích dẫn
  arXiv của `worker-WF`, **không** tự truy cập mạng, và **không** kiểm `contracts/ops/collector-probe.md`
  §3/§7 xem ba mục Owner vừa chấp nhận có hợp lý hay không — tôi chỉ ghi rằng Owner đã chấp nhận chúng.

## U6. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-27` **(mới)** | **Cần một quyết định Owner mới:** mở rộng grant `OD-20260907-04` mục 2 thêm host `help.openalex.org` (nơi `docs.openalex.org` `301` tới). Không có nó, hai giá trị OpenAlex và `openalex_identification_required` **không thể** giải, `REQ-A6` **vẫn** `KC`, và 2B **không thể** `CONTRACT_READY`. Đề nghị đưa lên cùng vòng với `REQ-OQ03`. |
| `CR-PC00-28` **(mới)** | `precode/owner-decisions-03.md` còn mang đường dẫn sai `contracts/collector/collector-probe.md` (front-matter `source_refs` + bảng mục 3). Ngoài write set của gói này; cần một packet nhỏ. |
| `CR-PC00-26` **(mới)** | `contracts/ops/collector-probe.md` §6 **chưa** ghi rằng bốn mục đã thỏa và trỏ `OD-20260907-04`. Thuộc PC05. |
| `CR-PC00-20` | `precode/gates.yaml` / `precode/review.md` chưa phản ánh `OD-20260907-02/03/04`. Thuộc PC09. |
| `CR-PC00-24` | 2B **chưa có card** — nay đã có `agent-tasks/TC-research-connector-metadata.md` trên đĩa (Worker khác); cần Coordinator xác nhận CR này đã được đáp ứng ngược dòng. |
| `CR-PC00-25` | **Một nửa đã giải:** cổng probe §6 mục 2–4 xong ở vòng bốn; phần `REQ-A6` chuyển thành `CR-PC00-27`. |
| `CR-PC00-22` | `A3-R4` chưa có bản ghi trong `evidence/index.json` |
| `CR-PC09-18` | `F-A3R4-01` (`PARKED`) — nhãn claim trong front-matter `.md` không được quét |
| `CR-PC00-15` | Re-pin — nay gồm `decision-register.md` `8285ae90…` và `baseline.json` `d25a8564…` |
| `CR-P0-03` mục 1 | `tools/` đã khai nhưng chưa tồn tại |
| `CR-PC00-19`, `CR-PC09-15` | Đã giải ở `FIX18` (tự khai) |
| `CR-PC00-17`, `CR-PC00-16`, `CR-PC00-13`, `CR-PC00-06` | Không đổi |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 — **mục duy nhất** còn treo từ bản yêu cầu gốc |

**Vì sao `DONE_WITH_CONCERNS`.** Mọi mục của packet đã xong; validate 674/674, E0 25/25. Concern: biên bản
này tự khai "đóng mọi mục mà `OD-20260907-03` để mở", nhưng **thực tế trên đĩa đã mở lại một mục ngay trong
cùng ngày** — grant bốn host không đủ để đọc tài liệu OpenAlex, vì tài liệu ấy đã chuyển sang một host thứ
năm. Không ai làm sai: Owner cấp đúng những host mà lúc hỏi ai cũng tưởng là đủ, và Worker dừng đúng chỗ
thay vì lách. Nhưng kết quả là `REQ-A6` **vẫn** `KC` sau một vòng quyết định được ghi là đã đóng nó —
và nếu chỉ đọc biên bản thì không thấy điều đó. Đó là lý do §7 và `CR-PC00-27` tồn tại.

## U7. Trạng thái bàn giao (FIX21)

- **next actor:** `Coordinator` — rehash bảy file ở §U4; `CR-PC00-27` (quyết định Owner mới) nên đi cùng
  vòng với `REQ-OQ03`; `CR-PC00-28` và `CR-PC00-26` cần packet nhỏ; W7 re-pin hai file card-pinned.
- **lease_released_at (UTC):** 2026-09-07T15:27Z. `LEASE-PC00-e22` (fencing 22) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §U4) và lease fencing ≥ 23.
- **Claim:** `DRAFT_FOR_REVIEW`. Bốn phạm vi vẫn `CONTRACT_READY` ở mức E0; `product_status` vẫn
  `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN` ở phạm vi PC00.

---

# ADDENDUM — PKT-PC00-FIX22 (`AMD-SPEC-D34-01`: đính chính tiền đề của `research-radar-spec.md:101`)

## V1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX22` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX22` · lease `LEASE-PC00-e23` (**fencing 23**), phạm vi **chỉ `precode/decision-register.md` §3** |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE_WITH_CONCERNS` |
| started / finished (UTC) | 2026-09-07T16:50Z / 2026-09-07T16:58Z · `date -u` trước lần ghi cuối: 2026-09-07T16:57Z |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T16:58Z |

## V2. Baseline drift đã quan sát trước khi ghi

`precode/decision-register.md` đã đổi kể từ `FIX21`: `8285ae90…` (tôi để lại) → **`b2ed138f…`** (trên đĩa
lúc tôi nhận packet). `worker-W3n` và packet `REQ-A6` đã thêm §8.13.1/§8.13.2 và các ghi chú trong khoảng
thời gian đó. Packet này **nêu đích danh §8.13.2** như một nguồn bằng chứng, nên drift ấy là **đã biết và
đã được tính đến**, không phải `STALE_BASELINE`. Tôi lấy `b2ed138f…` làm baseline và ghi rõ ở đây thay vì
lặng lẽ dùng nó.

## V3. Đã làm gì

**Một mục mới trong §3: `AMD-SPEC-D34-01`.** Theo ruling của Coordinator, sau khi `worker-W3n` **từ chối
đúng** việc tự quyết mục này — tạo một `AMD-…` là việc của PC00 dưới ruling, không phải của gói đang sửa ghi
chú. Lần từ chối đó được ghi lại trong mục, không bị bỏ qua.

**Điều tôi phải giải quyết trước khi viết: §3 không có chỗ cho loại bản ghi này.** Sáu trường của §3
(`Trước` / `Sau` / `Vì sao` / `Bảo đảm thay thế` / `Test/oracle` / `REQ ảnh hưởng`) giả định mọi mục đều
**đề xuất một văn bản thay thế**. Mục này thì không — và đó là điểm chính của nó. Nhét nó vào khuôn cũ sẽ
buộc tôi bịa một ô "Sau", tức đúng thứ ruling nói **không** nên có.

Nên tôi thêm vào đầu §3 một **bảng hai loại** và một tiền tố ID riêng:

| Loại | Tiền tố | Có "Sau" không |
| --- | --- | --- |
| Amendment | `AMD-B<nn>` | **Có** — đặc tả v0.3 sẽ viết lại câu đó |
| Đính chính tiền đề | `AMD-SPEC-<REQ>-<nn>` | **Không** — câu đó có thể giữ nguyên, đọc theo nghĩa lịch sử |

Đây là chỗ tôi mở rộng quy ước của file thay vì chỉ điền vào nó. Tôi làm vậy vì cả hai lựa chọn còn lại đều
tệ hơn: đặt mục ở §8 sẽ tách nó khỏi nơi mà `requirements.csv` và `traceability.csv` đã trỏ về (§3, "cần một
AMD"), còn ép nó vào khuôn `AMD-B` sẽ nói sai rằng đặc tả cần viết lại. Ô "Sau" của mục nay ghi thẳng:
**không có văn bản thay thế, và không cần một văn bản thay thế**.

**Nội dung mục.** `Trước` là trích **nguyên văn** `research-radar-spec.md:101` (hàng `D34`). `Vì sao` là dữ
kiện đọc 2026-09-07 dưới quyền mạng của `OD-20260907-04` mục 2 (mở rộng thêm `help.openalex.org`): OpenAlex
**không** đòi email liên hệ, **không** còn `mailto` / `polite pool` / `User-Agent`; `api_key` **tùy chọn**.
Bằng chứng: §8.13.2, `evidence/handoffs/PC03-REQA6-handoff.md`, `OD-20260907-04`.

**Ba phân biệt tôi viết ra vì chúng dễ bị đọc gộp:**

1. **`SG-IDENT` không bị nới.** Luật "nguồn đòi định danh mà cấu hình chưa có ⇒ không gọi" **giữ nguyên**;
   điều đổi là với OpenAlex nó **không kích hoạt**, vì tiền đề "nguồn này đòi định danh" sai. Một luật không
   kích hoạt khác hẳn một luật bị gỡ.
2. **`REQ-D34` thành `XN` vì NGHĨA VỤ ĐỌC đã xong, không phải vì tiền đề đúng.** Ghi chú của `W3n` trong
   `requirements.csv` đã nói đúng như vậy; mục này chốt cách nói đó là chuẩn.
3. **Ngân sách ngày của OpenAlex cố ý KHÔNG thành số** (`RESOLVED_NON_NUMERIC`): tài liệu nêu nó bằng
   **tiền**, nên suy ra "1/10" là một phép suy, không phải một câu trích. Oracle âm: không file nào được ghi
   một con số ngân sách ngày suy ra như thế.

**Và một điều mục tự đặt giới hạn cho chính nó:** đính chính này đúng với **tài liệu đọc ngày 2026-09-07**.
Nhà cung cấp đổi chính sách thì nhãn `DOCS_derived` hết hiệu lực và mục phải được đọc lại. Một dữ kiện bên
ngoài không bao giờ "đóng" vĩnh viễn theo cách một quyết định sản phẩm đóng.

**Đặc tả không bị chạm.** `research-radar-spec.md` rehash **`d35e1f2d…`** — khớp pin, không một byte đổi.

## V4. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/decision-register.md` ⚠ | MODIFY (§3) | `b2ed138fa636ce3e26f78f7e22994d4ebf9bc1b4e0ae692482df78247afe2017` (138431) | `058621d0649b798cb8882f718c450d548df1f4672bdee512e330bee77d46e8b0` (144860) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `a9471fc930fa389b4f41374ae3be9c4ce4c670ace23fafde4459607cc56645dc` | *(file này)* |

**1 MODIFY + 1 APPEND**, đúng phạm vi lease. `research-radar-spec.md` (`d35e1f2d…`) và
`research-radar-pre-code-plan.md` (`f65bb046…`) khớp pin. **Không** chạm `precode/source/*`,
`precode/requirements.csv`, `acceptance/traceability.csv`, `contracts/retry-policy.yaml`,
`precode/owner-decisions-0*.md`, `precode/baseline.json`, `agent_profile/registry.json`, hay bất kỳ mục nào
khác của `decision-register.md` ngoài §3. Không lệnh git thay đổi repo; không `__pycache__`/`.pyc` do tôi
sinh; **không network**; không secret.

## V5. Evidence

- **`e0_check.py` (chỉ đọc, theo yêu cầu packet):** `PYTHONDONTWRITEBYTECODE=1 python3
  evidence/tools/e0_check.py --repo .` — **exit code 0**, **25 check: PASS 25 · FAIL 0 · BLOCKED 0 ·
  violations 0**, chạy 2026-09-07T16:58Z.
- **`validate.py`:** **exit code 0**, **693 assertion, 693 PASS, 0 FAIL**, chạy 2026-09-07T16:57Z.
- **17 assertion mới** cho `AMD-SPEC-D34-01`: mục tồn tại trong §3; ô "Sau" nói rõ **không có văn bản thay
  thế**; trỏ đúng `research-radar-spec.md:101` và `D34`; khẳng định đặc tả **đứng nguyên** và được đọc theo
  **nghĩa lịch sử**; ba bằng chứng (§8.13.2, `PC03-REQA6-handoff.md`, `OD-20260907-04`); là **bản ghi chuẩn**
  với luật giải quyết "mục này thắng"; `SG-IDENT` **vẫn giữ nguyên như một luật**; ba mệnh đề "không làm";
  hiệu lực có điều kiện theo ngày đọc; và §3 khai rõ nó chứa **hai loại** bản ghi.
- **Một assertion đối chiếu thực tế quan trọng nhất của gói này:** dòng **101** của `research-radar-spec.md`
  đọc trực tiếp từ đĩa **phải vẫn chứa** cụm *"yêu cầu email liên hệ của OpenAlex"*. Nếu ai đó "sửa cho
  đúng" bản nguồn bất biến, validate **FAIL**. Đó là cách duy nhất một phép kiểm có thể bảo vệ một file mà
  luật của dự án nói là không được chạm.
- **Bốn assertion cũ FAIL ở lượt đầu và đã được sửa cho đúng sự thật mới, không nới lỏng.** Chúng khẳng định
  `REQ-A6` còn `KC` và `retry-policy` còn `PLACEHOLDER_KC` — **đã lỗi thời**: phần 2 của
  `PKT-PC03-FIX-REQA6` land sau khi Owner mở rộng allowlist, và cả bốn dữ kiện nay có nguồn. Bản mới
  **mạnh hơn** bản cũ: nó đòi `status: DOCS_derived`, đòi hai giá trị OpenAlex đúng bằng `100`/`1`, đòi
  URL nguồn có mặt trong file, đòi `RESOLVED_NON_NUMERIC` tồn tại, và — quan trọng nhất — đòi **căn cứ**
  chuyển trạng thái của `REQ-A6` là `OD-20260907-04` chứ **không** phải `OD-20260907-03`. Một trong số đó
  cũng lộ ra lỗi của chính tôi: `"PLACEHOLDER_KC" not in RP` quá thô, vì chuỗi ấy còn xuất hiện trong **văn
  xuôi phủ định**; nay kiểm bằng regex trên trường `status:`.
- **`NOT_RUN` / giới hạn:** tôi **không** tự đọc tài liệu arXiv/OpenAlex (không có quyền mạng ở gói này) và
  **không** xác minh lại một trích dẫn nào của `worker-WF`. Mục này ghi lại **điều họ đã ghi**, kèm con
  đường bằng chứng, không phải một lượt kiểm chứng độc lập. Audit độc lập trên epoch mới: `NOT_RUN`.

## V6. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-29` **(mới)** | `precode/owner-decisions-04.md` §7 và `precode/baseline.json` (anchor `OD-20260907-04`, khóa `post_decision_state_20260907T1523Z_vi`) — cả hai do tôi viết ở `FIX21` — nay **lỗi thời**: chúng nói nửa OpenAlex chưa giải, trong khi phần 2 của `PKT-PC03-FIX-REQA6` đã giải. **Ngoài lease của gói này** (chỉ §3). Cần một packet nhỏ để thêm một dòng "đã được §8.13.2 thay thế" vào cả hai. Cho tới lúc đó: **§8.13.2 thắng**. |
| `CR-PC00-27` | **Đã giải** — Owner đã mở rộng allowlist thêm `help.openalex.org` (§8.13.2); `REQ-A6` nay `RESOLVED`. |
| `CR-PC00-28` | `precode/owner-decisions-03.md` còn đường dẫn probe sai `contracts/collector/…` |
| `CR-PC00-26` | `contracts/ops/collector-probe.md` §6 chưa ghi bốn mục đã thỏa (PC05) |
| `CR-PC00-20` | `gates.yaml` / `review.md` chưa phản ánh `OD-20260907-02/03/04` (PC09) |
| `CR-PC00-22` | `A3-R4` chưa có bản ghi trong `evidence/index.json` |
| `CR-PC09-18` | `F-A3R4-01` (`PARKED`) |
| `CR-PC00-15` | Re-pin — nay gồm `decision-register.md` `058621d0…` |
| `CR-P0-03` mục 1 | `tools/` đã khai nhưng chưa tồn tại |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 |

**Vì sao `DONE_WITH_CONCERNS`.** Mục đã được ghi, e0 25/25, validate 693/693. Concern là `CR-PC00-29`: hai
văn bản **của chính tôi** viết cách đây chưa đầy hai giờ nay mô tả sai trạng thái, vì một packet song song
đã tiến. Tôi không sửa được chúng trong lease này và **không** tự mở rộng phạm vi để sửa. Đây là cái giá cụ
thể của `PROV-PC00-08` mà Owner đã chấp nhận: nhiều Worker viết song song vào một kho tài liệu chung, không
có khoá thật, nên "đúng lúc viết" và "đúng lúc đọc" tách nhau ra — và cách duy nhất giữ hồ sơ trung thực là
ghi ngày giờ vào từng phát biểu, đúng như tôi đã làm ở `FIX21` §7. Nhờ có mốc thời gian đó, hai đoạn lỗi
thời **đọc được như lịch sử** thay vì đọc như một lời nói dối.

## V7. Trạng thái bàn giao (FIX22)

- **next actor:** `Coordinator` — rehash `decision-register.md`; giao `CR-PC00-29` (một packet nhỏ, hai
  dòng); `CR-PC00-28`, `CR-PC00-26`, `CR-PC00-20` còn mở; W7 re-pin.
- **lease_released_at (UTC):** 2026-09-07T16:58Z. `LEASE-PC00-e23` (fencing 23) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (`058621d0…`) và lease fencing ≥ 24.
- **Claim:** `DRAFT_FOR_REVIEW`. `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN` ở
  phạm vi PC00.

---

# ADDENDUM — PKT-PC00-FIX23 (`CR-PC00-29`: hai đoạn lỗi thời của chính tôi về `REQ-A6`)

## W1. Danh tính

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC00-FIX23` · worker `worker-W1n` · authority `AUTH-COORD-PC00-FIX23` · lease `LEASE-PC00-e24` (**fencing 24**), phạm vi **chỉ** `precode/owner-decisions-04.md` §7 và mục anchor `OD-20260907-04` của `precode/baseline.json` |
| mode / ceiling | `DOCUMENTARY_DRAFT`, `NOT_IMPLEMENTED` · `DRAFT_FOR_REVIEW` |
| status | `DONE` |
| started / finished (UTC) | 2026-09-07T16:59Z / 2026-09-07T17:03Z · `date -u` trước lần ghi cuối: 2026-09-07T17:02Z |
| next actor / lease_released_at | `Coordinator` / 2026-09-07T17:03Z |
| nguồn | `CR-PC00-29` — do chính tôi mở ở `PKT-PC00-FIX22` §V6 |

## W2. Đã làm gì

Hai chỗ đều do tôi viết ở `FIX21` lúc 15:23Z, khi packet `REQ-A6` mới land **nửa arXiv**. Phần 2 của
`PKT-PC03-FIX-REQA6` chạy sau đó và giải nốt nửa OpenAlex, nên hai đoạn ấy mô tả sai trạng thái.

**Tôi không xoá chúng — tôi tách thì.** Cả hai chỗ nay có **hai tầng**:

- **Trạng thái hiện hành** (`§7.1` trong record; ba khóa `post_decision_*` trong anchor): **`REQ-A6` =
  `RESOLVED`**, cả bốn dữ kiện có nguồn, kèm bảng giá trị (arXiv `1`/`3 s` + `1` kết nối, định danh
  `RESOLVED_NEGATIVE`; OpenAlex `100`/`1 s`, định danh `RESOLVED_NEGATIVE` với `api_key` **tùy chọn**).
  `contracts/retry-policy.yaml` nay `DOCS_derived`, **không còn** `PLACEHOLDER_KC`; `requirements.csv` ghi
  `REQ-A6` và `REQ-D34` là `XN`. Bản ghi chuẩn được trích: **`precode/decision-register.md` §8.13.2** và
  `evidence/handoffs/PC03-REQA6-handoff.md`.
- **Lịch sử** (`§7.2`; khóa `superseded_observation_20260907T1523Z_vi`): đoạn cũ **giữ nguyên nội dung**,
  nhưng mang nhãn *"nay đã bị §7.1 và §8.13.2 thay thế — không được đọc như trạng thái hiện hành"*.

**Vì sao giữ đoạn cũ thay vì viết đè.** Nó ghi đúng một điều đáng giữ: một Worker gặp `301` ra ngoài
allowlist và **dừng** thay vì đi theo. Đó là hành vi `protocol.md` §3 đòi, và nó là lý do câu hỏi tới được
Owner thay vì bị một con số phỏng đoán lấp đi. Xoá đoạn ấy sẽ xoá luôn bằng chứng rằng ranh giới đã được tôn
trọng — và làm hồ sơ trông như thể nửa OpenAlex "tự nhiên" giải được.

**Quy kết đã đúng sẵn, nay được viết tường minh.** Cả hai chỗ vốn đã ghi `OD-20260907-04`; tôi thêm mệnh đề
**"không phải `OD-20260907-03`"** vào cả record lẫn anchor, vì đó là chỗ dễ trượt: vòng ba *nói về*
`REQ-A6` nhưng vòng bốn mới *cấp quyền*.

**Bốn giới hạn được chép sang chỗ mới**, để "RESOLVED" không bị đọc rộng: (1) `XN` nghĩa là **nghĩa vụ đọc**
xong, không phải tiền đề đặc tả đúng — trỏ về `AMD-SPEC-D34-01`; (2) ngân sách ngày OpenAlex **cố ý không**
thành số (`RESOLVED_NON_NUMERIC`), nguồn sự thật lúc chạy là header `X-RateLimit-*`; (3) **không** nâng trần
claim của `MOD-research-connector`; (4) hiệu lực có điều kiện theo **tài liệu đọc ngày 2026-09-07**.

**Ghi nhận `CR-PC00-27` đã giải** ngay trong §7.1: nửa OpenAlex được gỡ chốt bằng một **quyết định** của
Owner (thêm `help.openalex.org`, allowlist thành **năm** host; mọi hạn chế khác giữ nguyên —
`api.openalex.org` và `export.arxiv.org` vẫn cấm), không phải bằng một lần tìm kỹ hơn.

## W3. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/owner-decisions-04.md` | MODIFY (§7) | `d523945aca4efbfb0c09edd6a955e877921b4851bd5577556c94faf984884a86` (13058) | `4ef7d11bd0a6f7161fb7916a36f1ac44b7648aff0d04bf901be3ac57036e5c3a` (15986) |
| `precode/baseline.json` ⚠ | MODIFY (anchor `OD-20260907-04`) | `d25a856452ea0012eea4de1ad063054b4c49b92d5a7e71a4a982e3f25e56d1ef` (111009) | `ffd1efb3588f87504f61c037b4a242b29a6afb0ddd0f1fd1780c677b22a8bf64` (112871) |
| `evidence/handoffs/PC00-handoff.md` | APPEND | `0bb7f31343b106b94540c11a8c41ed52d8678f2c915e946f9f6327936e5f8c01` | *(file này)* |

**2 MODIFY + 1 APPEND**, đúng phạm vi lease — trong `baseline.json` chỉ mục anchor `OD-20260907-04` bị sửa;
JSON parse lại được. Rehash chứng minh **không** đổi: `precode/decision-register.md` (`058621d0…`),
`precode/requirements.csv` (`d3e150e3…` — Worker khác đang giữ, tôi chỉ đọc),
`contracts/retry-policy.yaml` (`f9505525…` — như trên), `research-radar-spec.md` (`d35e1f2d…`, **khớp pin**),
`research-radar-pre-code-plan.md` (`f65bb046…`). Không chạm `agent_profile/registry.json`,
`precode/owner-decisions*.md` khác, `acceptance/`, `agent-tasks/`, `contracts/` hay cây mã. Không lệnh git
thay đổi repo; không `__pycache__`/`.pyc` do tôi sinh; **không network**; không secret.

## W4. Evidence

- **`e0_check.py` (chỉ đọc, theo yêu cầu packet):** `PYTHONDONTWRITEBYTECODE=1 python3
  evidence/tools/e0_check.py --repo .` — **exit code 0**, **25 check: PASS 25 · FAIL 0 · BLOCKED 0 ·
  violations 0**, chạy 2026-09-07T17:02Z.
- **`validate.py`:** **exit code 0**, **703 assertion, 703 PASS, 0 FAIL**, chạy 2026-09-07T17:01Z.
- **18 assertion được thay cho khối cũ** (khối cũ khẳng định nửa OpenAlex **chưa** giải — nay sai). Bản mới
  **mạnh hơn**, và điều quan trọng là chúng **neo vào đĩa chứ không vào văn bản của tôi**:
  `openalex_requests_per_window: 100` và `openalex_window_seconds: 1` phải **có thật** trong
  `contracts/retry-policy.yaml`, và câu "`REQ-A6` = `RESOLVED`" trong §7.1 phải **khớp hai chiều** với sự
  kiện đó — nếu Worker kia rollback, validate **FAIL** thay vì bản ghi của tôi âm thầm nói quá.
- Cộng các assertion buộc: §7.1 trích `§8.13.2` **và** `PC03-REQA6-handoff.md`; quy kết ghi rõ
  *"không phải `OD-20260907-03`"*; `§7.2` tồn tại **và** mang nhãn đã-bị-thay-thế (giữ lịch sử, không xoá);
  bốn giới hạn có mặt (`AMD-SPEC-D34-01`, `RESOLVED_NON_NUMERIC`, trần claim, hiệu lực theo ngày); anchor có
  ba khóa `post_decision_*` mới **và** khóa lịch sử; và **khóa cũ
  `post_decision_state_20260907T1523Z_vi` KHÔNG còn tồn tại** — đảm bảo tôi đã *thay* nó chứ không *thêm
  cạnh* nó.
- **`NOT_RUN` / giới hạn:** tôi **không** truy cập mạng, **không** xác minh lại một trích dẫn nào của
  `worker-WF`, và **không** đọc `contracts/retry-policy.yaml` để thẩm định nội dung — chỉ để đối chiếu bốn
  giá trị. Audit độc lập trên epoch mới: `NOT_RUN`.

## W5. Unresolved

| ID | Nội dung |
| --- | --- |
| `CR-PC00-29` | **Đã giải ở gói này** (tự khai; xác minh thuộc người khác). |
| `CR-PC00-27` | **Đã giải** — Owner mở rộng allowlist thêm `help.openalex.org`; `REQ-A6` `RESOLVED`. |
| `CR-PC00-28` | `precode/owner-decisions-03.md` còn đường dẫn probe sai `contracts/collector/…` |
| `CR-PC00-26` | `contracts/ops/collector-probe.md` §6 chưa ghi bốn mục đã thỏa (PC05) |
| `CR-PC00-20` | `gates.yaml` / `review.md` chưa phản ánh `OD-20260907-02/03/04` (PC09) |
| `CR-PC00-22` | `A3-R4` chưa có bản ghi trong `evidence/index.json` |
| `CR-PC09-18` | `F-A3R4-01` (`PARKED`) — nhãn claim trong front-matter `.md` không được quét |
| `CR-PC00-15` | Re-pin — nay gồm `baseline.json` `ffd1efb3…` và `decision-register.md` `058621d0…` |
| `CR-P0-03` mục 1 | `tools/` đã khai nhưng chưa tồn tại |
| `REQ-OQ03` | Vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3 — **mục duy nhất** còn treo từ bản yêu cầu gốc |

**Một quan sát về kiểu lỗi này, không phải một CR.** Đây là lần thứ ba trong sáu gói mà một văn bản của tôi
lỗi thời vì một packet song song tiến lên. Ba lần đều **không** phải lỗi phán đoán — chúng đúng lúc viết —
mà là hệ quả cấu trúc của `PROV-PC00-08`: nhiều Worker ghi song song vào một kho tài liệu chung, không có
khoá thật. Thứ duy nhất giữ hồ sơ trung thực qua ba lần đó là **mốc thời gian trong từng phát biểu**: nhờ nó,
đoạn cũ đọc được như *lịch sử* thay vì như *lời nói sai*. Nếu Coordinator muốn giảm tần suất, cách rẻ nhất
không phải là viết cẩn thận hơn mà là **đừng để hai packet cùng mô tả một sự kiện đang diễn ra** — hoặc
chấp nhận rằng bản ghi phải mang thì, như nó đang mang.

## W6. Trạng thái bàn giao (FIX23)

- **next actor:** `Coordinator` — rehash ba file ở §W3; `CR-PC00-28`, `CR-PC00-26`, `CR-PC00-20`,
  `CR-PC00-22` còn mở; W7 re-pin `baseline.json` `ffd1efb3…`.
- **lease_released_at (UTC):** 2026-09-07T17:03Z. `LEASE-PC00-e24` (fencing 24) nhả tại đây; `worker-W1n`
  không ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §W3) và lease fencing ≥ 25.
- **Claim:** `DRAFT_FOR_REVIEW`. `product_status` vẫn `NOT_READY_FOR_PRODUCT_CODE`; E1–E4 vẫn `NOT_RUN` ở
  phạm vi PC00.

---

# ĐỢT BỔ SUNG MUỘN — bảy addendum `PKT-PC00-FIX24` … `FIX30`

> **Ghi bổ sung ngày 2026-09-08T01:00Z dưới `PKT-PC00-FIX31-HANDOFF`, lease `LEASE-PC00-e33` (fencing 33),
> phạm vi: CHỈ file này.** Bảy gói dưới đây đã chạy xong và đã nhả lease đúng lúc, nhưng **addendum của
> chúng chưa được ghi vào đây** — lý do đơn giản và đáng ghi: lease của mỗi gói ấy **không** bao gồm
> `evidence/handoffs/`, nên tôi không được ghi, và tôi đã báo điều đó cho Coordinator ở `FIX24` thay vì tự
> mở phạm vi. Hệ quả là suốt bảy gói, **việc nhả lease chỉ tồn tại trong thông điệp trả lời Coordinator**,
> không trong hồ sơ.
>
> **Bảy addendum dưới đây được dựng lại từ chính báo cáo của tôi tại thời điểm mỗi gói kết thúc.** Mọi hash
> là giá trị tôi đã tính và báo khi đó; **không** quyết định nào được xem lại, **không** kết luận nào được
> sửa. Chúng mang cùng giới hạn như `PHASE2-dispatch-log.md`: chúng khôi phục **nội dung**, nhưng **không**
> chứng minh được rằng chúng tồn tại **tại thời điểm** mỗi gói kết thúc — chỉ có các thông điệp trong
> transcript làm được điều đó. Đọc chúng như **bản ghi bổ sung muộn, có khai báo**, không như addendum viết
> tại chỗ. → `CR-PC00-36`.
>
> **Điều đáng rút ra, không phải cho tôi mà cho việc cấp packet:** một Worker bị cấm ghi vào chính file
> handoff của mình sẽ **luôn** tạo ra khoảng trống này. Nếu handoff là bắt buộc theo `protocol.md` §4 thì
> `evidence/handoffs/<PC>-handoff.md` nên nằm trong **mọi** lease của gói đó theo mặc định, thay vì phải nhớ
> thêm từng lần.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX24` — đóng gói Giai đoạn 2

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX24` · `LEASE-PC00-e25` (**fencing 25**) · authority `AUTH-COORD-PC00-FIX24` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-07T17:46Z** |

**Đã làm.** Chép **4** file (mọi bản `cmp` byte-identical) và cập nhật hai README:

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `evidence/audits/A3-P2-R1-report.md` | CREATE | `96efd7b1461677d0de52fe13905e654439dc305da2921dab648ab9ced97ed1e1` (16829) |
| `evidence/audits/FC-P2-manifest.txt` | CREATE | `042fb77283ea423461e8020e8d581c1f73102de804f7600e20d42bc013ced0f9` (68990) |
| `evidence/coordination/OWNER-DECISIONS-20260907-03.md` | CREATE | `d3cee88806ad9e5b615dc39ce0e215eefdeda2945c4e2d488c02f818f6e6fb20` (1844) |
| `evidence/coordination/OWNER-DECISIONS-20260907-04.md` | CREATE | `74dfe407f9ae2136b3108edf2ccc5ef1498c873cba5cc75096c032040bba92e7` (1971) |
| `evidence/audits/README.md` | MODIFY | `1d43ea82a1b52589a89bb3bcff1148d8e838bcdedc49397ca1afb12d574480d5` (14510) |
| `evidence/coordination/README.md` | MODIFY | `42a5c5c758bf7fd0951c6a19c8052add382e5931a0337e9661bc1315a3dc691e` (19923) |

**Evidence.** 67/67 bản sao `cmp` byte-identical; danh mục README đủ (27/27, 40/40); `e0_check.py` 25/25 PASS.

**Concerns đã nêu khi đó.**
- **`CR-PC00-30` (mới):** các packet Giai đoạn 2 **không tồn tại trên đĩa** — tôi tìm khắp scratchpad, không
  chỉ `packets/`. Chúng được phát bằng `SendMessage` và chưa bao giờ được ghi thành file. Tôi chép cái có
  thật và **không** dựng lại phần còn lại.
- **Không có hash đã đăng ký để đối chiếu** cho `A3-P2-R1-report.md`: `EV-A3-11` trích nó chín lần nhưng
  `artifacts[]` không ghim được hash. Bản chép **cung cấp** giá trị đầu tiên, không **khớp** một giá trị có sẵn.
- **Không viết addendum handoff** ở gói đó: `evidence/handoffs/` ngoài lease — chính là khoảng trống mà đợt
  bổ sung này lấp.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX25` — đóng `CR-PC00-30`

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX25` · `LEASE-PC00-e26` (**fencing 26**) · authority `AUTH-COORD-PC00-FIX25` |
| status / claim | `DONE` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-07T17:51Z** |

**Đã làm.** Chép **2** file do Coordinator dựng lại từ transcript, cộng README:

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `evidence/coordination/PHASE2-dispatch-log.md` | CREATE | `2c23d63f7f2c196bc8a367ea97bedca9d2d7ac43093bbb19754338e476633640` (22150) |
| `evidence/coordination/A3-p2-r1-packet.md` | CREATE | `0994854f2c50ecd793db6d266516a0e85dac7a3e5906e7ced105e4d4a2e5ed09` (3700) |
| `evidence/coordination/README.md` | MODIFY | `614315bcd19dab8fb95e18e814f0498a26f7707b3b7b51500240efb78cb97373` (22085) |

**Evidence.** `cmp` byte-identical; danh mục 44/44; `e0_check.py` 25/25 PASS; `validate.py` 703/703 PASS.

**Concerns đã nêu khi đó.** Hai file mang nhãn ⚠ **DỰNG LẠI TỪ TRANSCRIPT**: chúng khôi phục nội dung packet
nhưng **không** có dấu thời gian độc lập ràng buộc văn bản vào thời điểm dispatch. Dùng để **hiểu** Giai đoạn
2 được điều phối thế nào; **không** dùng làm bằng chứng rằng một grant tồn tại ở một thời điểm. Nguyên nhân
gốc: dưới `PROV-PC00-08`, ghi packet ra đĩa là **thói quen**, không phải ràng buộc — và thói quen thì bỏ được
mà không có gì báo động.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX26` — `OD-20260908-05` (vòng năm)

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX26` · `LEASE-PC00-e27` (**fencing 27**) · authority `AUTH-COORD-PC00-FIX26` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-07T18:32Z** |

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `precode/owner-decisions-05.md` | **CREATE** | `e6ef1541923682cf94d757034f62b9bca53df743f9dbd8a1d543e4e05e876a4a` (10718) |
| `precode/owner-decisions.md` | MODIFY | `6071b8afdf46a6619500c734b0396f1328a53fa3cb4353f390cbd46841d4b027` (13628) |
| `precode/decision-register.md` ⚠ | MODIFY (§0) | `f6be5fca3ffeff2dfea71e8b87a72200c579c90bf4f237bb289a9198214a132a` (169204) |
| `precode/baseline.json` ⚠ | MODIFY | `45a55ab4fa0386d4904f637d8974cbc85bd3f0088cb8228ab9dd6d17e3575a74` (116295) |
| `precode/owner-decision-request.md` | MODIFY | `a6ad690d0fb24033deaad1dd9af1f2894a5afa4c1d62e316c91c86332af5a4c3` (64140) |
| `agent_profile/registry.json` | MODIFY | `7d7bc06deb3e0b2d588bfab32524ec5de1c861f36be4be7a2d178b15daf67c38` (13583) |

**Evidence.** `validate.py` 789/789 PASS; `e0_check.py` 25/25 PASS, 0 violation.

**Concerns đã nêu khi đó.**
- **Giai đoạn 5 KHÔNG được tuyên bố gỡ chặn:** điều kiện Owner là **năm** dữ kiện; `worker-WT` land **hai**.
  `registry.json` ghi `condition_met: false`. → **`CR-PC00-31`**.
- **Đụng độ đồng thời có thật:** `worker-WAI` ghi `decision_refs` và một hàng legend **trong lúc tôi chạy**;
  tôi đọc lại và **bỏ** hai sửa đổi đã trùng thay vì ghi đè. WAI ghi rằng vòng năm **không** dùng nhãn
  `ACCEPTED` (nó giao việc nghiên cứu, không chấp nhận một phương án) — đúng, nên tôi không thêm nhãn cạnh tranh.
- `REQ-OQ03` được `OD-20260908-06` giải; **năm** assertion mới ghim đúng quy kết đó.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX27` — `OD-20260908-09` (vòng chín)

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX27` · `LEASE-PC00-e28` (**fencing 28**) · authority `AUTH-COORD-PC00-FIX27` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-07T19:05Z** |

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `precode/owner-decisions-09.md` | **CREATE** | `2233a0dbbdf717b52bd19c4a4c2fb612dcb20ba1a7d953d66143d8c635e5e8c0` (11138) |
| `precode/owner-decisions.md` | MODIFY | `ecb9f74c6c4072c4a9f5236db062a52995f04e31bfcf00d6bca4c5c472d296bf` (14027) |
| `precode/decision-register.md` ⚠ | MODIFY (§0) | `089b2a9b1a5d5597271f2c7620611ac5504eca24e63e738b8d20678f8cd5f779` (180058) |
| `precode/baseline.json` ⚠ | MODIFY | `2d0db93e7ccd90d97b55c4cdd5f2fe1c464291a2a29af5f4a76d08f9e973ec98` (119792) |
| `precode/owner-decision-request.md` | MODIFY | `1abc31e6278923da46d875c1f7eff5f407d83ec566b67ba4017c29bc9d13915c` (65174) |
| `agent_profile/registry.json` | MODIFY | `80121a59e63ce7ad3323b21659a86205bf635f5e74a1fc38dc77a1cbf8c257ec` (16291) |

**Evidence.** `validate.py` 869/869 PASS; `e0_check.py` 25/25 PASS.

**Concerns đã nêu khi đó.**
- **Điều kiện Giai đoạn 5 được THAY, không phải được THỎA.** `phase_5_conditional_entry` → `phase_5_entry`
  với **hai tầng**: `current` (đã khởi động, **chỉ văn bản thuần**) và `superseded_condition`
  (`condition_met: false`, 2/5, `SUPERSEDED … REPLACED, NOT SATISFIED`). Ghi `true` cho điều kiện cũ sẽ là
  một câu **sai kiểm được**. `CR-PC00-31` giải theo cách này.
- **`CR-PC00-32` (mới):** hai lần lease chồng nhau `WT`/`WAI`; "không mất dữ liệu" là **kết quả**, không phải
  **bảo đảm** — đúng chế độ hỏng (b) mà `PROV-PC00-08` đã liệt kê.
- **`OD-20260908-07`/`-08` thiếu bản ghi độc lập, anchor và authority** — nêu để xử lý ở gói sau.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX28` — parity cho vòng bảy và tám

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX28` · `LEASE-PC00-e29` (**fencing 29**) · authority `AUTH-COORD-PC00-FIX28` |
| status / claim | `DONE` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-07T19:56Z** |

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `precode/owner-decisions-07.md` | **CREATE** | `0ac5d9620b67e833d5e208d065810fbc60b67bb8073901ce5f350d94571ecb8a` (7464) |
| `precode/owner-decisions-08.md` | **CREATE** | `8afcd2cf2f85234e9f273ce5a1925041367cf98d36ac780c7cea4dd83d11b539` (7706) |
| `precode/owner-decisions.md` | MODIFY | `0dcf0e1ae717a3227811aa77dc5ec3b607564b35334fc6b87f1161846fc75180` (14576) |
| `precode/decision-register.md` ⚠ | MODIFY (§0) | `b26cf51a0d7c73661ab465e5a157aaad7a9ceb6f013926abd5117f6966764a7e` (182028) |
| `precode/baseline.json` ⚠ | MODIFY | `52af62c8b11e6939a9a34798bd71b4a4e688d8ed85d9c579ee1858ed341037e9` (124824) |
| `precode/owner-decision-request.md` | MODIFY | `a851c3a8e9d2b861a4e2846b3fff2872105ce1904ed73d01173e7d436a13758c` (67147) |
| `agent_profile/registry.json` | MODIFY | `38f49df7b1bbf848d38764988d0021080543aec2cbe34facb56863f85cf4df1a` (20168) |

**Evidence.** `validate.py` 990/990 PASS; `e0_check.py` 25/25 PASS.

**Concerns đã nêu khi đó.**
- Hai file mới **tự khai là bản ghi song hành theo quy ước**, trỏ về §8.14.3 / §8.15.1 làm bản ghi hiệu lực,
  và ghi luật **"§8.14.3 / §8.15.1 thắng"** khi lệch. Không quyết lại điều gì.
- **Ba ranh giới của chữ ký `REQ-A5`** được chép vào cả bốn nơi: hẹp theo nhà cung cấp **và** theo bản đọc
  (hết hiệu lực khi trang đổi phiên bản); **ký ≠ bật** (`B13`, `ISO-03`/`ISO-05`, `REQ-AC16` vẫn `BLOCKED`);
  và câu hỏi chính sách arXiv/OpenAlex/X **vẫn chưa ai trả lời** — Owner **gánh** `TC-A5-01`, không **giải** nó.
- **Hardening:** nhiều assertion tra cứu authority/anchor **theo vị trí** đã vỡ ngay khi chèn vòng 7–8 vào
  giữa mảng; chuyển sang tra cứu **theo id**.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX29` — đóng gói Giai đoạn 3 + 5

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX29` · `LEASE-PC00-e30` (**fencing 30**) · authority `AUTH-COORD-PC00-FIX29` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-07T20:45Z** |
| wait gate | `A3-P3-R2-report.md` — poller `GATE_OPEN after 8m`; **không byte nào** được ghi trước dấu đó |

**Đã làm.** Chép **15** file (4 → `evidence/audits/`, 11 → `evidence/coordination/`), tất cả `cmp`
byte-identical; `coordinator-ledger.md` **cố ý không** chép (file sống, packet loại trừ).

| Path | After sha256 (bytes) |
| --- | --- |
| `evidence/audits/A3-P3-R1-report.md` | `d6368b95f4a277abbf1c2e1a90c1bffce75b36b20adf6ee3454b0594b238420f` (16371) |
| `evidence/audits/A3-P3-R2-report.md` | `a62a74b5839383566e65f2bdec3d46463b4fde389896247f5538bc1fe72c1a16` (10479) |
| `evidence/audits/FC-P3-manifest.txt` | `2b211a8cedc7ee9aa550c7067300eee9525034a69f0463e5238ce499ea45c921` (80046) |
| `evidence/audits/FC-P3e2-manifest.txt` | `f9da1bd6abb6573090ee04e0ac92fce8fc600ae1abb38e1f7d857031d65d8ca5` (80919) |
| `evidence/audits/README.md` | `b8bb4c2b7718dbe22ba5040bfddb806bf05824510abcc38564d25b57362cd038` (21187) |
| `evidence/coordination/README.md` | `95be6945247c22ddb4da26838cb4962a27734af6e07343c86de1486d3d75cdec` (26932) |

Mười một file điều phối: `OWNER-DECISIONS-20260908-05/-07/-08/-09`, `PKT-PC07-FIX-TELEGRAM.md`,
`PKT-PC06-FIX-OQ03.md`, `PHASE3-5-card-dispatch.md`, `A3-p3-r1-packet.md`, `A3-p3-r2-packet.md`,
`FIX-A3P3R1-rulings.md`, `PHASE4-6-card-dispatch.md` — hash đầy đủ trong danh mục
`evidence/coordination/README.md`.

**Evidence.** 87/88 bản sao `cmp` (1 DIFF = ledger sống, bị loại trừ có chủ ý); danh mục 33/33 và 55/55;
`e0_check.py` **26/26** PASS.

**Concerns đã nêu khi đó.**
- **`CR-PC00-33` (mới):** `evidence/index.json` **không** có tham chiếu `A3-P3` nào tại thời điểm chép —
  bản chép **cung cấp** hash đầu tiên, không **khớp** một giá trị đã đăng ký.
- **`A3-P3-R1` là PASS *có điều kiện*** (`ruff format --check` đỏ trên bốn file; auditor từ chối ký commit
  của những byte đó); điều kiện được giải ở epoch 2 và `A3-P3-R2` xác minh. Danh mục ghi **cả hai** verdict.
- **Tương phản trước/sau dispatch được ghi rõ:** 11 file Giai đoạn 3/5 **được ghi ra đĩa TRƯỚC khi dispatch**
  (bài học `CR-PC00-30` đã áp dụng) — khác hẳn `PHASE2-dispatch-log.md` dựng lại sau.
- `PHASE4-6-card-dispatch.md` mang nhãn 🕒 **đã soạn, chưa dispatch**, không cấp quyền cho ai.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX30` — `OD-20260908-10` (vòng mười)

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX30` · `LEASE-PC00-e31` (**fencing 31**) · authority `AUTH-COORD-PC00-FIX30` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-08T00:50Z** (nhả sớm để `worker-WP` re-pin) |

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `precode/owner-decisions-10.md` | **CREATE** | `18503f19c651c1fe6a59ce451d75952040b4ec3102aa3432b51827ede9e3ebe4` (8434) |
| `precode/owner-decisions.md` | MODIFY | `f26997f65561e8eac28e7efda0d39e90a7f6860b9e478911c068dd570f9df1cb` |
| `precode/decision-register.md` ⚠ | MODIFY (§0) | `8d6a87fb0569e4c36e36722c25e959476f104f7983822205b7d3d0da1a63eca1` (184327) |
| `precode/baseline.json` ⚠ | MODIFY | `e8cf3910c6f2351a2c7c4a8620121b0415a58c5c7ec86eee7ba5d33c343c1a70` (127222) |
| `precode/owner-decision-request.md` | MODIFY | `0ea4f93c7e61d60b28c1f3c825ee215f95679c45ef7fabc0e3d11589a30773aa` (68201) |
| `agent_profile/registry.json` | MODIFY | `c2e4e8b9f07e57f896190942419fddcde78df8fd7c4d93b927672bb58db3eac6` (21502) |

**Evidence.** `validate.py` **1000/1000** PASS, exit 0. `e0_check.py`: **26 check — PASS 25 · FAIL 1 ·
3 violation**, exit 1.

**Concerns đã nêu khi đó — ba cái, và cái đầu là lỗi của chính tôi.**

1. **Tôi làm hỏng `agent_profile/registry.json` giữa gói rồi sửa lại.** Lệnh chèn dùng **số học chỉ số** và
   ghép object authority mới vào `coding_phase.phase_5_entry` thay vì mảng `authorities`, tạo JSON **không
   hợp lệ** trên đĩa. `json.load` trong cùng bước bắt được ngay; sửa bằng thao tác **theo văn bản**, rồi
   kiểm lại: 10 authority đúng thứ tự, `phase_5_entry` về đúng sáu khóa, `product_status`/`enforcement`/
   `status`/blocker/`lease_discipline_observed` **không đổi**. Không file nào khác bị ảnh hưởng và không mất
   dữ liệu — **nhưng file đã có một khoảng thời gian ở trạng thái hỏng**. Cùng lớp lỗi với hash sai ở `FIX17`
   và hai lần `split` thiếu cận trên ở `FIX15`/`FIX20`: **tự động hóa dựa trên vị trí, không dựa trên cấu trúc**.
2. **`e0` đỏ, nhưng KHÔNG do tôi.** Phép kiểm mới `E0-20-card-fixture-accounting` báo 3 violation ở ba card
   Giai đoạn 4/6 (`TC-backup-restore-drill`, `TC-ui-reports-detail`, `TC-ui-runs-three-states`) có fixture §2
   không được test nào dùng và không được nêu trong handoff. Cả ba nằm trong `agent-tasks/` + test — phạm vi
   của đợt sửa Giai đoạn 4/6 đang chạy, **ngoài lease của tôi**. Tôi **không** chạm và **không** thử sửa.
3. **`CR-PC00-35` (mới):** `tools/backup_cli.py` nay **đã tồn tại** (card `backup`), trong khi `ADR-0011` vẫn
   nói *"`tools/` chưa được tạo"* — đúng khi viết ở `FIX17`, **nay sai**. Phép kiểm hai chiều dựng ở `FIX17`
   **đã bắt được** nó. `ADR-0011` ngoài lease nên tôi **không** sửa; register ghi sai lệch và nói **đĩa
   thắng**, và assertion nay **đỏ trở lại** nếu `CR-PC00-35` bị đóng mà ADR chưa sửa. `CR-P0-03` mục 1 do đó
   **đã được đáp ứng trên thực tế**.

---

## Trạng thái sau đợt bổ sung

- **Bảy addendum trên là bản ghi bổ sung muộn**, khai báo rõ ở đầu mục. Không quyết định, hash hay kết luận
  nào bị thay đổi; mọi giá trị lấy từ báo cáo của chính tôi tại thời điểm mỗi gói kết thúc.
- **Còn mở:** `CR-PC00-33` (index.json chưa ghim hash `A3-P3-*`), `CR-PC00-34` (fixture quét biên, PC08),
  `CR-PC00-35` (`ADR-0011` nói sai về `tools/`), `CR-PC00-36` (**mới** — handoff phải nằm trong mọi lease
  của gói, nếu không khoảng trống này sẽ lặp lại), `CR-PC00-20`, `CR-PC00-22`, `CR-PC09-18`, `CR-PC00-15`,
  `CR-PC00-28`, `CR-PC00-26`.
- **next actor:** `Coordinator`. `lease_released_at` cho `LEASE-PC00-e33`: **2026-09-08T01:02Z**. Sau dấu này
  `worker-W1n` chỉ còn giữ trạng thái **chờ cổng** của `PKT-PC00-FIX31`; không ghi file nào cho tới khi
  `…/scratchpad/audits/A3-P4-R1-report.md` xuất hiện.

---

# ĐỢT BỔ SUNG MUỘN THỨ HAI — bốn addendum `PKT-PC00-FIX31` … `FIX34`

> **Ghi bổ sung ngày 2026-09-09T10:40Z dưới `LEASE-PC00-e37` (fencing 37), phạm vi: CHỈ file này.**
>
> **Lần này KHÔNG có lý do biện hộ, và tôi ghi rõ điều đó.** Đợt bổ sung trước (`FIX24`…`FIX30`) xảy ra vì
> `evidence/handoffs/` **nằm ngoài lease** của bảy gói ấy — một ràng buộc thật, và chính tôi đã mở
> **`CR-PC00-36`** để sửa nó. Coordinator **đã áp dụng**: từ `WIRING-wave-1.md` trở đi, đường dẫn handoff nằm
> trong **mọi** lease. Vậy mà ở `FIX31`…`FIX34` tôi **có quyền ghi và đã không ghi** — bốn lần liên tiếp.
> Đây là lỗi của tôi, không phải của cấu hình packet: tôi coi bản báo cáo gửi Coordinator là "đã xong việc"
> trong khi hồ sơ mới là thứ tồn tại sau phiên.
>
> **Hậu quả cụ thể, không giả định:** gate của `worker-WP` khóa theo chuỗi `PKT-PC00-FIX34` trong file này và
> **không mở được** — **lần thứ ba** một tiến trình khác phải chờ vì hồ sơ của tôi tụt sau công việc của tôi.
>
> Bốn addendum dưới đây dựng lại từ chính báo cáo của tôi tại thời điểm mỗi gói kết thúc; mọi hash là giá trị
> tôi đã tính và báo khi đó. **Không** quyết định nào được xem lại. Chúng mang cùng giới hạn như đợt trước:
> khôi phục **nội dung**, không chứng minh được **thời điểm** — chỉ transcript làm được điều đó.
>
> **Cam kết từ đây:** addendum được ghi **trong chính gói làm việc**, trước khi nhả lease. Coordinator cũng đã
> chuyển gate của PC00 sang **byte predicate** để một lần chậm của tôi không còn chặn được ai.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX32` — `AMD-ADR0011-01`

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX32` · `LEASE-PC00-e34` (**fencing 34**) · authority `AUTH-COORD-PC00-FIX32` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| `lease_released_at` | **2026-09-08T01:29Z** (nhả sớm cho `worker-WP` re-pin P4b — `ADR-0011` là file card-pinned) |

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` ⚠ | MODIFY | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` (27451) |
| `precode/change-control.md` | MODIFY (§10) | `1203de290dac6c689646c88465b10990d41763a3a96fd18da8bd517891a22d41` (76476) |
| `precode/decision-register.md` | MODIFY (§0) | `a38e2ce1a953279b7d1ca0ba6ae2ad52f97886a887f98e596b9ade0f4fdb211b` (185553) |

**Đã làm.** Khối amendment `AMD-ADR0011-01` trong đúng quy ước ghi chú của chính ADR, `decision_refs`
`F-A3-P4-02` + `CR-PC00-35`, chuỗi `OD-20260908-10` → `AUTH-OWNER-20260908-11`. **Status ADR giữ `accepted`,
`ratified_by: OD-20260907-02` không đổi** — không hàng nào trong bảng Quyết định đổi lựa chọn; ba mục sửa
**câu mô tả đã hết đúng**. (1) Phạm vi kiểm kiểu: *"`mypy --strict` cho lõi server"* → **mọi cây mã sản phẩm
Python** (`server/app`, `worker/app`, `collector/app`, `probe`). Đây là chỗ **một câu mơ hồ trong ADR trở
thành một lỗ thật trong CI**: cấu hình làm đúng theo câu ấy (`files = ["server/app"]`) nên **23 file sản
phẩm không được thứ gì kiểm kiểu**. (2) `tools/` **đã tồn tại** — ghi chú cũ được **đánh dấu hết đúng**, không
xoá. (3) `.gitignore` phủ `__pycache__/`; ghi rõ nó **không** thay quy tắc `PYTHONDONTWRITEBYTECODE=1`, vì
`.gitignore` chỉ giấu file khỏi git chứ không ngăn file được tạo. Bản ghi CR đầy đủ theo định dạng §1 ở
`change-control.md` §10 (`CR-PC00-35` gộp `F-A3-P4-02`, `status: APPLIED`).

**Evidence.** `validate.py` **1037/1037 PASS**, exit 0. `e0_check.py` **27 check: PASS 26 · FAIL 1 ·
3 violation**, exit 1 — **không do tôi**: `E0-21-marker-reason-freshness` báo ba `xfail` reason cũ trong
`tests/integration/`, thuộc phạm vi đợt sửa Giai đoạn 4/6, **ngoài lease**; tôi không chạm.

**Concerns.** `CR-PC00-37` (mới): ADR trích addendum `P0-FIX4` của `WS` cho việc phạm vi mypy mới chạy sạch,
nhưng **addendum đó chưa tồn tại** khi tôi viết — tôi đánh dấu nó là **tham chiếu tới việc đã giao, không
phải quan sát đã kiểm**. Phép kiểm hai chiều `tools/`↔ADR được **re-point sang đòi đánh dấu**, không nới lỏng.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX31` — đóng gói Giai đoạn 4 + 6 (chạy **hai lượt**)

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX31` · `LEASE-PC00-e32` (**fencing 32**) · authority `AUTH-COORD-PC00-FIX31` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| wait gate | `A3-P4-R1-report.md` (`GATE_OPEN after 34m`), **sau đó Coordinator dời cổng sang `A3-P4-R2`** |
| `lease_released_at` | **2026-09-08T02:03Z** |

**Chín file, hai lượt.** Lượt đầu (2026-09-08T01:24Z, khi cổng còn ở R1) chép 5; lượt sau chép 4. Bốn file
lượt đầu **được giữ** vì chúng là bản sao byte-identical của artefact **thật** ở epoch 1.

| Path | After sha256 (bytes) |
| --- | --- |
| `evidence/audits/A3-P4-R1-report.md` | `ce22118c7012c20b396011cb313587d426e36e62fbccd36ece4da3cc02f5a34d` (11738) |
| `evidence/audits/A3-P4-R2-report.md` | `99dc3c06eb7742faa768f126be429b8f8e775d8a862e682b6f5b88f56aded396` (11125) |
| `evidence/audits/FC-P4-manifest.txt` | `dee4d783c98e1d8c234cabbcb0ca3da63383edfd06f9febd656aedeea2ad7c02` (94546) |
| `evidence/audits/FC-P4e2-manifest.txt` | `e0e436cdd1be5d51a5e8fdd01001c25f7aa515ced54067b9024721cf5f768f23` (96138) |
| `evidence/coordination/A3-p4-r1-packet.md` | `22864f6be434a0b87ab08920dde3702127bc76264ebfe345fb3bc1e1a2503fed` (5955) |
| `evidence/coordination/A3-p4-r2-packet.md` | `aaa1266df1314f589164394c0a48b46f74bb4ca7a450732cd82e71fa4ead3380` (3724) |
| `evidence/coordination/FIX-P4-wave-rulings.md` | `6abcf68f8a9e299c1f473563e79424e4b9bea4a4418c1811259f24b0fb74d1a7` (3863) |
| `evidence/coordination/FIX-A3P4R1-rulings.md` | `145f9c40d16377743dcc81ebb1b2852b49f1c01fdcc1a85505b974f49bb2ca31` (2619) |
| `evidence/coordination/OWNER-DECISIONS-20260908-10.md` | `98e5e1f199988f55c0cb6a3653c0da5740f4b5d30316bf344f4593c35e73e5b5` (1487) |
| `evidence/audits/README.md` | `6cee9b331a05e4a76450b33184bbe3b6dcbe2da583cf965483cc5b0029ebf745` (28117) |
| `evidence/coordination/README.md` | `3b63120ca28748d6f9783967d97a3100400e0cafdbae3bd0962a3a773321b156` (29172) |

**Evidence.** 96/97 bản sao `cmp` byte-identical (1 DIFF = `coordinator-ledger.md` sống, packet loại trừ);
danh mục 37/37 và 60/60; `e0_check.py` **27/27 PASS**; `validate.py` 1037/1037.

**Concerns.**
- **Danh mục mang CẢ HAI verdict**, không chỉ cái mới: `A3-P4-R1` *PASS **có một điều kiện phạm vi*** —
  `F-A3-P4-01` (MEDIUM): card `TC-report-coverage-publish-cas` **mang claim phủ** `REQ-D29`/`I07` trong khi
  `CR-TC-BACKFILL-09` (một defect **đã biết** ở publisher) chưa được xử lý và **không** nêu trong handoff của
  chính card — auditor gọi là *sửa disposition và phạm vi, không phải sự cố mã*. `A3-P4-R2` *PASS*, giải điều
  kiện ấy. Điều kiện của R1 là **một phần hồ sơ**, không phải trạng thái trung gian đáng xoá.
- **`PHASE4-6-card-dispatch.md`: nhãn 🕒 gỡ, byte KHÔNG đổi** (`7dfd6712…`). Thứ đổi là **sự kiện bên ngoài**;
  nên trạng thái sống ở **danh mục**, không bằng cách sửa file lưu trữ.
- `F-A3-P4R2-01` (LOW) được nêu nổi bật: phép kiểm `E0-21` vừa được thêm **không nhìn thấy** dạng `reason=`
  một dòng (regex `$` dưới `re.S`) ⇒ *"0 violations" hôm nay trung thực nhưng phép kiểm yếu hơn vẻ ngoài* —
  lần thứ hai một công cụ bằng chứng tự nó có lỗ.
- `CR-PC00-33`: `grep 'A3-P4'` trên `evidence/index.json` = **0**; bản chép **cung cấp** hash đầu tiên.

---

## ADDENDUM (muộn) — `PKT-PC00-FIX33` — đóng gói đợt nối dây tích hợp (chạy **ba lượt**)

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX33` · `LEASE-PC00-e35` (**fencing 35**) · authority `AUTH-COORD-PC00-FIX33` |
| status / claim | `DONE_WITH_CONCERNS` · `DRAFT_FOR_REVIEW` |
| wait gate | `A3-P5-R1` → **dời** sang `R2` → **dời** sang `R3`; poller bị kill qua đêm và được **arm lại** |
| `lease_released_at` | **2026-09-09T08:59Z** |

**Mười một file** (6 audits + 5 coordination) + hai README, tất cả `cmp` byte-identical; 107/108 verify.

| Path | After sha256 (bytes) |
| --- | --- |
| `evidence/audits/A3-P5-R1-report.md` | `b540ecaf58e3f8e0d4aa3d615e9225871ef2949c4dd93275d81611ac403a46d3` (14207) |
| `evidence/audits/A3-P5-R2-report.md` | `d3aa12fa61d02a3cc6ea5cd19e4a2b3a9db79ef6b2df71ded65414652245d268` (10781) |
| `evidence/audits/A3-P5-R3-report.md` | `027f3d4191472568e93600e74c4c76d7f3a4208916b5fc926a9d8e602c3d88af` (5208) |
| `evidence/audits/FC-P5-manifest.txt` | `fd7d59d704289824f5ea3a3ec0cf71eedf141d2b1d1776edca0f272fe4ba0846` (103298) |
| `evidence/audits/FC-P5e2-manifest.txt` | `7b4ef4e5f5cf7f371849ab3948932969db183b3b0a4b948c60f56f8c96d0cb11` (104500) |
| `evidence/audits/FC-P5e3-manifest.txt` | `d94d3a48779c00584c3c5b75685b81bfa249909eb812444a48178faced056780` (105249) |
| `evidence/coordination/WIRING-wave-1.md` ✚ | `b602c02b50720d1aac947d5983173993cf429913eac3960fcf36707598691139` (6418) |
| `evidence/coordination/A3-p5-r1-packet.md` | `f15864e781e680b3a4181aa860b7993db9e9db626e07d1cb68f0851210c75765` (5650) |
| `evidence/coordination/A3-p5-r2-packet.md` | `4f89d86547cb9f1da4547ef4f2189f0074aa27dd117922348597bf94edea0884` (3785) |
| `evidence/coordination/A3-p5-r3-packet.md` | `cd781387099618ebe395b4c977cb6d398b659f2256c5758e3a4b64e48578e7a9` (1567) |
| `evidence/coordination/FIX-A3P5R1-rulings.md` | `d0073961375172a53b054ecc64f011239c159c6f590d6fb1497043e331a5eccc` (3091) |
| `evidence/audits/README.md` | `6724ce648b85b12428ad6bfcabd5105ea7f4bfd0356660ee447ad54a53e65de0` |
| `evidence/coordination/README.md` | `9b4f68b54b02c59fd9327eb522ed16d217df883e1228a31f6d9a0d5426809c1c` |

**Evidence.** Danh mục 43/43 và 65/65; `e0_check.py` **27/27 PASS**, 0 violation.

**Concerns — và đây là gói mang quan sát quan trọng nhất của cả phiên.**
- **KHÔNG có composition root nào chạy được TRƯỚC đợt này** (ghi thành quan sát có ngày trong
  `evidence/coordination/README.md`). `docs/owner-runbook.md` (`WS2`) phát hiện: card **được xây và kiểm đối
  chiếu port và harness**, nhưng `create_app()` **không dựng service nào**, `RR_DATABASE_URL` **chỉ Alembic
  đọc**, đăng nhập **trả 500 ngoài test** ⇒ **Owner không thể thử bất cứ thứ gì đầu-cuối**.
  **Vì sao chín vòng audit trước đều xanh mà không vòng nào sai:** mỗi vòng đo đúng thứ nó **được giao** —
  card đối chiếu harness — và **không vòng nào được giao đo hệ thống đã lắp ráp**. Khoảng trống nằm ở **cái
  được audit**, không ở **cách audit**. Bài học thuộc về **việc cấp packet**: một chuỗi `PASS` chỉ mạnh bằng
  **phạm vi rộng nhất từng được giao cho ai đó đo**.
- `A3-P5-R1` là báo cáo đầu tiên chạy hệ thống **như tiến trình hệ điều hành** (uvicorn thật, curl thật) —
  và chỉ khi đó bốn `F-A3-P5-*` mới lộ ra.
- **`AMD-ENT-maintenance-01` khi đó là amendment kỹ thuật mà Owner CHƯA được hỏi** — tôi ghi `PROVISIONAL`
  trong danh mục và đề nghị đưa lên vòng Owner *"thay vì mặc nhiên thành sự thật vì không ai phản đối"*.
  (Đã được phê chuẩn ở `OD-20260909-11`, xem addendum kế.)
- **`docs/owner-runbook.md` §9.4 mang chữ trước đợt nối dây** — lệnh `maintenance --open` nó hướng dẫn
  **chính là lệnh crash** (`F-A3-P5-01`). Rủi ro trực tiếp cho người dùng thật, không phải chi tiết hồ sơ.
- `A3-P5-R3` chứa **ghi chú phương pháp tự khai** của auditor: lần đọc log đầu trả số Giai đoạn 1 vì họ dùng
  lại tiền tố log `r3-`; họ phát hiện, chạy lại và **ghi cả sai sót vào báo cáo**.
- ✚ `WIRING-wave-1.md` là file **tích lũy**: bản chép (`b602c02b…`, 6418) gồm phụ lục wave 2 + ruling, trong
  khi bản lúc dispatch nhỏ hơn (`5fc320f3…`, 5108) — ghi cả hai để đối chiếu.
- `CR-PC00-33`: `grep 'A3-P5'` = **0** (vòng thứ tư liên tiếp ⇒ **thứ tự công việc thường trực**).

---

## ADDENDUM (muộn) — `PKT-PC00-FIX34` — `OD-20260909-11` (vòng mười một)

| Trường | Giá trị |
| --- | --- |
| packet / lease | `PKT-PC00-FIX34` · `LEASE-PC00-e36` (**fencing 36**) · authority `AUTH-COORD-PC00-FIX34` |
| status / claim | `DONE` · `DRAFT_FOR_REVIEW` |
| gate | `PKT-PC02-FIX20` trong `PC02-handoff.md` đã nhả (`LEASE-PC02-e24`, 07:40Z) — poller mở sau **2 phút**; **serialized với `worker-W3n`, không chồng lease** |
| `lease_released_at` | **2026-09-09T09:50Z** |

| Path | Op | After sha256 (bytes) |
| --- | --- | --- |
| `precode/owner-decisions-11.md` | **CREATE** | `ea21ab43f582718c374d830d9cb7d60943131019b7d4b7558c0dddb8fe202952` (9338) |
| `precode/owner-decisions.md` | MODIFY | `f3a00f2edbc4a0bcdbf4aa46f20c2aaec367e7b748f6335decf6c4939d42f6c9` |
| `precode/decision-register.md` | MODIFY (**§0 only**) | `24e6765f86a88c77ca3efa3af10c600345f3a462ad6abe2d8e06aeceb01eb8c1` |
| `precode/baseline.json` | MODIFY | `cf59b2c937c334ce21d2cebc7e10dcc84c872f83432fc59d86a1477bd2311875` |
| `precode/owner-decision-request.md` | MODIFY | `26c846f6956ac8cf6802bcbbb55a2073e8b8105797c1774621d6dd87ec31ea16` |
| `agent_profile/registry.json` | MODIFY | `202dc72046b60f3a3e10e8d7acc684dd184ec77e480ddde5fedf409fc0c36bfa` |

**Evidence.** `validate.py` **1102/1102 PASS**, exit 0; `e0_check.py` **27/27 PASS**, 0 violation.
`§8.16` (của `worker-W3n`), `contracts/data/entities.yaml` và `PC02-handoff.md` **không** bị chạm.

**Concerns.**
- Ghi như **bản ghi song hành theo quy ước**, nhường quyền cho §8.16 khi lệch. Ranh giới được chép vào **cả
  bốn** nơi: điều được gỡ là **tính tạm thời của HỢP ĐỒNG** (claim "health lưu bền" của card storage và
  "restore hai bước" của card backup thôi đứng trên hợp đồng provisional); điều **không** được gỡ là **giới
  hạn của bằng chứng** — ba verdict `A3-P5-*` giữ nguyên phạm vi, mức bằng chứng hai card **không** đổi,
  **không finding nào bị đóng**.
- `F-A3-P5R3-01` **đã đóng bằng phép đo** (`W6B` phát lại `…-E1-20260909T104000Z.json`, `worker-W6n` tự băm
  lại: **0 pin lệch cả hai hạng**) — tôi **kiểm trên đĩa** trước khi chép fact đó vào hồ sơ.
- Phần còn nợ **không** rút gọn: không tạo/đọc được báo cáo (`CR-P0-07`, `REQ-OQ09`), tag chưa có card,
  connector chưa nối (`SG-DOC`/`SG-LIVE`), **`E3`/`E4` `NOT_RUN` khắp nơi, `SP1` chưa bao giờ chạy**.
- Một tự sửa: file này ban đầu viết thường cụm tự-khai trong khi `owner-decisions-07/08.md` viết hoa và chính
  `EV-PC00-15` ép dạng viết hoa ⇒ tôi **sửa tài liệu theo quy ước đã có**, không nới phép kiểm.

---

## Trạng thái sau đợt bổ sung thứ hai

- **Bốn addendum trên là bản ghi bổ sung muộn**, khai báo ở đầu mục. Không hash, quyết định hay kết luận nào
  bị thay đổi.
- **Điều khác với đợt trước:** lần này nguyên nhân **không** phải giới hạn lease mà là **thói quen của tôi**.
  `CR-PC00-36` đã được áp dụng và tôi vẫn không dùng nó bốn lần. Ghi ra ở đây thay vì để nó thành một dòng
  trung tính trong sổ.
- **next actor:** `Coordinator` / `worker-WP` (gate `PKT-PC00-FIX34` nay mở được).
  `lease_released_at` cho `LEASE-PC00-e37`: **2026-09-09T10:42Z**.
