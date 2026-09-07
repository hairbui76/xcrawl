# HANDOFF — PKT-PC09 (khóa oracle, traceability, evidence và readiness)

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09` |
| worker principal | `worker-W6` |
| authority_id | `AUTH-COORD-PC09` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC09-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` — không có OS enforcement; quiescence là quan sát, không phải fence runtime |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| audit_route | `INDEPENDENT_REQUIRED` — **chưa chạy** (`NOT_RUN`) |

Lý do `DONE_WITH_CONCERNS` chứ không phải `DONE`: mọi write target đã được tạo trọn vẹn, nhưng
lần chạy E0 thật thoát với **exit code 1** (hai check FAIL, 28 vi phạm), và mười hai scenario
không có fixture. Cả hai đều được báo nguyên vẹn thay vì được làm cho biến mất.

---

## 2. Changes — mọi file đều `CREATE`, baseline `ABSENT`

| Path | Op | Before | After sha256 | Bytes |
| --- | --- | --- | --- | ---: |
| `acceptance/scenarios.yaml` | CREATE | ABSENT | `fd7f7a1100caee829b2d5d57c57be7846d3def138d7811e38ba4cee27b2d207e` | 151546 |
| `acceptance/traceability.csv` | CREATE | ABSENT | `2001cd12e8cdd84387b7bd63b3cdbd568b31f142686a687eb2a62faf553bb0ea` | 89283 |
| `evidence/manifest.schema.json` | CREATE | ABSENT | `68d1da65e2c7a9530ac8692b918be9be1359217f7715d6ceacc6f3063c4f86cc` | 20766 |
| `evidence/index.json` | CREATE | ABSENT | `78b4715794e2ab368f979382ccb03ec7f01cc1b9c6d62c5f5c158f403ec14c94` | 181334 |
| `evidence/tools/README.md` | CREATE | ABSENT | `de16e90090b445313bc45cab0af709d6cac9445411eb93171f3eb481282961ae` | 12303 |
| `evidence/tools/e0_check.py` | CREATE | ABSENT | `6a480278086966a0421afb2e5462a4461e4430eb58b9ce87873e035a4722fda2` | 81195 |
| `evidence/runs/E0-20260906T193716Z.json` | CREATE | ABSENT | `fe1c74ed16cbd63fa15ea19505e41383dfe0468cc5bfe9964d40d508d1b86e93` | 38366 |
| `precode/gates.yaml` | CREATE | ABSENT | `57e138334782737d8541cf2ce73e0bd13772a80a674fee11073fa5f91122770c` | 29460 |
| `precode/review.md` | CREATE | ABSENT | `0f8a24f79f2a94d7c8feff66cb89daf73180b15b99ab9de4c6ec5b14d9863eb0` | 58141 |
| `evidence/handoffs/PC09-handoff.md` | CREATE | ABSENT | *(file này — Coordinator rehash độc lập)* | — |

Hai thư mục được cấp và đã tạo: `evidence/tools/`, `evidence/runs/`.

**Side effects đã kiểm.** Không file nào ngoài danh sách trên bị chạm. `find . -name '__pycache__'
-o -name '*.pyc'` (trừ `.git`) trả rỗng — mọi lần chạy python đều đặt `PYTHONDONTWRITEBYTECODE=1`
và mọi script phụ trợ nằm dưới `…/scratchpad/w6/`, không nằm trong repo. Không lệnh git nào làm
thay đổi repo. Không truy cập mạng. Không secret. Không spawn agent.

**Một file trung gian đã bị xóa có chủ đích:** `evidence/runs/E0-20260906T193638Z.json` được tạo
rồi xóa (bằng `python3 -c "os.remove(...)"`) vì lần chạy đó bắt được một lỗi trong chính
`precode/review.md` của tôi (một citation sai dạng `REQ-S4-*` mà `E0-06` đọc thành `REQ-S4`). Tôi
sửa prose rồi chạy lại. Ghi lại ở đây thay vì im lặng: file đã tồn tại trong repo khoảng 40 giây.
Lần chạy được giữ lại là lần duy nhất được đăng ký trong `evidence/index.json`.

---

## 3. Source baseline đã dựa vào

### 3.1 Nguồn pinned — KHỚP ở cả hai lần kiểm (trước khi bắt đầu và trước handoff)

| Ref | Path | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |

Khớp baseline §2. **Không có điều kiện `STALE_BASELINE`.**

### 3.2 Read set — FC-W3 epoch 3, và drift quan sát được

Ở đầu gói tôi xác minh **toàn bộ 151 entry** của `…/scratchpad/audits/FC-W3-manifest.txt`:
`sha256sum -c` cho **151/151 OK**, 0 mismatch, 0 missing.

Trước handoff tôi kiểm lại cùng manifest: **57 / 151 file đã đổi** so với epoch 3. Đây **không**
phải stop gate — Coordinator đã báo trước rằng đợt FIX4 (W2/W3/W4/W5) đang land song song và chỉ
thị tôi chạy E0 ở lần pass cuối trên bytes hiện hành và ghi lại hash. Drift theo nhóm:

| Nhóm | Số file | Ai sửa (theo chỉ thị của Coordinator) |
| --- | ---: | --- |
| `acceptance/fixtures/` (6 thư mục) | 39 | W3 (identity, telegram), W5 (reporting), W4 (collection), W2 (recovery README) — đợt FIX4 theo ruling R4-01/R4-02 |
| `contracts/` | 8 | `capabilities.yaml`, `errors.yaml`, `http/openapi.yaml`, `ops/collector-probe.md`, `ports.yaml`, `retry-policy.yaml`, `schemas/analysis-result.schema.json`, `state/run.yaml` |
| `evidence/handoffs/` | 9 | các gói ghi addendum FIX4 |
| `precode/baseline.json` | 1 | PC00-FIX3 (anchor SC45–SC48) |

**Hai file quyết định của hai FAIL còn lại KHÔNG đổi:** `contracts/modules.yaml` (nguồn của 36
cạnh bị cấm) và `contracts/state/analysis.yaml` (nguồn của mâu thuẫn TSR-A01). Nên `CR-PC09-02` và
`CR-PC09-04` đúng với bytes hiện hành, không phải với một ảnh chụp cũ.

### 3.3 Nguồn ngoài repo đã đọc

`…/scratchpad/packets/00-coordination-baseline.md`, `PC09-packet.md`, `FIX-A1R1-rulings.md`,
`FIX3-rulings.md`, `FIX4-rulings.md`; `…/scratchpad/audits/A1-R1-report.md`, `A1-R2-report.md`,
`A1-R3-report.md`; `agent_profile/worker.md`, `protocol.md`. Cả ba AUDIT_REPORT được đọc đầy đủ và
kết luận của chúng được gấp vào `precode/review.md` §4.

---

## 4. Evidence records

Tất cả là **`SELF_VALIDATION`**, producer `worker-W6`. **Không phải audit độc lập.** Chi tiết đầy
đủ của 55 bản ghi nằm trong `evidence/index.json`; bảng dưới là bốn bản ghi mà packet yêu cầu.

Runtime: Linux 7.0.0-30-generic, python3 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3. Mọi script phụ
trợ dưới `…/scratchpad/w6/`, `PYTHONDONTWRITEBYTECODE=1`.

### EV-PC09-01 — chạy `e0_check.py` thật (packet EV-01)

- **Command:** `PYTHONDONTWRITEBYTECODE=1 python3 /mnt/virtual/repo/xcrawl/evidence/tools/e0_check.py --repo /mnt/virtual/repo/xcrawl --json-out /mnt/virtual/repo/xcrawl/evidence/runs/E0-20260906T193716Z.json`
- **started / ended (UTC):** 2026-09-06T19:37:16Z / 2026-09-06T19:37:19Z · **exit code 1**
- **Oracle:** 19 check, không check nào FAIL, exit code 0.
- **Observed:** **17 PASS · 2 FAIL · 0 BLOCKED · 28 vi phạm · exit code 1** → **`FAIL`**
- **Artifact:** `evidence/runs/E0-20260906T193716Z.json` (`fe1c74ed…b86e93`, 38366 B), gồm
  `baseline_hashes` của **121 file** tại thời điểm chạy.

| Check | Kết quả | Kiểm | Vi phạm |
| --- | --- | ---: | ---: |
| `E0-01-parse` | PASS | 101 | 0 |
| `E0-02-metaschema` | PASS | 8 | 0 |
| `E0-03-fixture-schema` | PASS | 28 | 0 |
| `E0-04-operation-refs` | PASS | 766 | 0 |
| `E0-05-error-code-refs` | PASS | 700 | 0 |
| `E0-06-requirement-refs` | PASS | 2072 | 0 |
| `E0-07-id-refs` | PASS | 2779 | 0 |
| `E0-08-contract-header` | PASS | 127 | 0 |
| **`E0-09-state-lint`** | **FAIL** | 67 | **2** |
| `E0-10a-denied-edge-scenario` | PASS | 36 | 0 |
| **`E0-10b-denied-edge-oracle`** | **FAIL** | 36 | **26** |
| `E0-11a-no-orphan` | PASS | 246 | 0 |
| `E0-11b-invariant-polarity` | PASS | 17 | 0 |
| `E0-12-forbidden-strings` | PASS | 609 | 0 |
| `E0-13-coverage-windows` | PASS | 11 | 0 |
| `E0-14-fixture-actor-edge` | PASS | 279 | 0 |
| `E0-15-fixture-field-existence` | PASS | 1054 | 0 |
| `E0-16-scenario-catalogue` | PASS | 81 | 0 |
| `E0-17-declared-deviations` | PASS | 5 | 0 |

**Chạy xác nhận lần hai** ngay trước handoff trên bytes hiện hành: verdict **giống hệt** (17 PASS,
2 FAIL, 28 vi phạm, exit 1); 0 / 121 file trong `baseline_hashes` đổi giữa hai lần chạy. Ba check
có `items_checked` tăng nhẹ (101→103, 2779→2832, 609→612) vì `evidence/index.json` và chính file
run được thêm vào phạm vi quét sau lần chạy đầu — không phải thay đổi nội dung hợp đồng.

**Chi tiết hai FAIL:**

1. `E0-09-state-lint` (2): `contracts/state/analysis.yaml` khai `terminal_state_rule` TSR-A01 với
   nguyên văn *"Từ `valid` không có transition đi ra"*, trong khi cùng file có **T-AN-12**
   (`valid → pending`) và **T-AN-13** (`valid → valid`). → `CR-PC09-04`.
2. `E0-10b-denied-edge-oracle` (26): 26 / 36 cạnh bị cấm của `contracts/modules.yaml` không có
   `denied_cases[]` với `expected_error_code`. → `CR-PC09-02`.

**`fixture-field-existence` theo từng thư mục** (theo phương pháp đếm đã chốt: một đơn vị cho mỗi
key không bắt đầu bằng `_` dưới `rows.<entity>[]`, đếm một lần cho mỗi hàng):

| Thư mục | files | columns_checked | unresolved | annotations_skipped | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `ai` | 11 | 40 | 0 | 0 | PASS |
| `collection` | 8 | 0 | 0 | 0 | **`NOT_APPLICABLE_FREEFORM`** |
| `identity` | 14 | 372 | 0 | 52 | PASS |
| `recovery` | 10 | 0 | 0 | 0 | **`NOT_APPLICABLE_FREEFORM`** |
| `reporting` | 13 | 528 | 0 | 26 | PASS |
| `telegram` | 18 | 114 | 0 | 31 | PASS |

`collection/` và `recovery/` nêu oracle bằng văn xuôi (`durable_rows_expected`,
`expected_target_state`) chứ không bằng `rows.<entity>[]`, nên check này **không chạm tới chúng**.
`0 unresolved` ở hai thư mục đó có nghĩa "không đo được", **không** có nghĩa "sạch" — đã ghi ở
`evidence/tools/README.md` §5 và `precode/review.md` §3.3 theo đúng chỉ thị của Coordinator.

### EV-PC09-02 — `evidence/index.json` validate với `manifest.schema.json` (packet EV-02)

- **Command:** `PYTHONDONTWRITEBYTECODE=1 python3 w6/validate_index.py`
- **Oracle:** mỗi bản ghi của `records[]` validate được với `evidence/manifest.schema.json`, 0 lỗi.
- **Observed:** **55 / 55 hợp lệ, 0 lỗi** · exit 0 → `PASS`. Schema cũng qua
  `Draft202012Validator.check_schema`.
- **Sai lệch có chủ đích so với văn bản packet, đã khai:** packet viết "`evidence/index.json`
  validates against `manifest.schema.json`". Một schema mô tả MỘT manifest không thể validate một
  danh sách manifest. Tôi đọc câu đó là "mỗi bản ghi validate được", và `index.json` là một object
  chỉ mục mang metadata lần sinh cộng `records[]`. Cách đọc này được ghi tường minh trong chính
  `index.json` (`shape_note_vi`) để không ai hiểu nhầm.

### EV-PC09-03 — traceability (packet EV-03)

- **Command:** cùng lệnh EV-PC09-01, check `E0-11a-no-orphan`.
- **Oracle:** số dòng `traceability.csv` == số dòng `requirements.csv`; không dòng P0 với status
  XN/UQ nào là `ORPHAN`.
- **Observed:** **246 == 246**; **`ORPHAN` = 0** (tổng, không chỉ P0/XN/UQ) → `PASS`.
  Phân bố: `COVERED` 76 · `PARTIAL` 74 · `BLOCKED_B01..B17` 84 · `DEFERRED_P1` 6 ·
  `OUT_OF_SCOPE` 6.
- **Điều phải nói kèm:** **50 dòng `PARTIAL` là P0 với status XN hoặc UQ.** Trước gói này,
  **51 yêu cầu không được bất kỳ file nào dưới `contracts/` hay `acceptance/` trích dẫn**, gồm cả
  năm bước của luồng thiết lập lần đầu (`REQ-S5.1-01` … `-05`, bốn dòng XN). SC50–SC53 được viết ra
  chính để đóng nhóm đó. → `CR-PC09-03`.

### EV-PC09-04 — danh mục scenario (packet EV-04)

- **Command:** cùng lệnh EV-PC09-01, check `E0-16-scenario-catalogue` + `E0-11b-invariant-polarity`.
- **Oracle:** mỗi AC-01..AC-18 có scenario; mỗi invariant có ≥ 1 scenario dương và ≥ 1 âm; mỗi mã
  lỗi có ≥ 1 scenario.
- **Observed:** **18/18 AC có scenario; 17/17 invariant có cả hai cực; 28/28 mã lỗi có scenario;
  53 scenario, id liên tục SC01–SC53, không trùng, mọi `status` là `NOT_RUN`** → `PASS`.
- **Điều phải nói kèm:** **12 scenario có `fixture_refs: [MISSING]`** → `CR-PC09-01`.

### Những gì KHÔNG chạy

- **E1, E2, E3, E4: `NOT_RUN` ở cả 53 scenario.** 32 placeholder tường minh trong
  `evidence/index.json` (8 nhóm scenario × 4 cấp), mỗi cái nêu lý do cụ thể.
- **Audit độc lập của chính gói này: `NOT_RUN`.** `audit_route` là `INDEPENDENT_REQUIRED` và Worker
  không được tự audit candidate của mình.
- **Validator OpenAPI 3.1: không có** trong môi trường và packet cấm cài. 221 KB của
  `contracts/http/openapi.yaml` chỉ được kiểm như YAML cộng toàn vẹn tham chiếu — **không** kiểm
  tuân thủ đặc tả OpenAPI.
- **Xác minh lại nội dung kỹ thuật của PC00–PC08:** không thực hiện. Khi `review.md` §8.2 ghi "CR
  đã được đáp ứng ngược dòng", đó là lời tự khai của gói phát ra CR, không phải kết luận độc lập
  của tôi.

---

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Mọi P0 và AC-01..18 map tới contract, invariant, scenario và loại bằng chứng — và cả registry D | **DONE** | `acceptance/traceability.csv` (246 dòng, 0 ORPHAN); `acceptance/scenarios.yaml` (53 scenario) |
| 2 | Fixture có dữ liệu đúng/sai độc lập; mock được vs. cần live/human | **PARTIAL** | Mỗi scenario có `mockable_vi` và `needs_live_or_human_vi`. 12 scenario chưa có fixture → `CR-PC09-01` |
| 3 | E0 validation chạy thật; kết quả được ghi, gồm cả FAIL | **DONE** | `evidence/runs/E0-20260906T193716Z.json`, exit 1, 2 FAIL báo nguyên vẹn |
| 4 | Evidence manifest + quy tắc invalidation; NOT_RUN ở mọi chỗ chưa chạy | **DONE** | `evidence/manifest.schema.json`; `precode/gates.yaml` §`invalidation_rules` (INV-01..INV-10); 32 placeholder NOT_RUN |
| 5 | Thiết kế A2/A3/A4 với tập calibration/evaluation tách biệt; rubric khóa trước | **DONE** | `precode/review.md` §7 |
| 6 | Rà soát B01–B17, ĐX/KC, quyết định, phạm vi code-ready theo module | **DONE** | `precode/review.md` §5 (B01–B17), §6 (ĐX/KC), §9 (25 module), §10 (PROVISIONAL chờ Owner) |

### Ràng buộc "Đạt khi" của SRC-PLAN §11 PC09

- *"không orphan requirement"* — **đạt**: 0 ORPHAN trên 246 dòng.
- *"không invariant thiếu negative case"* — **đạt**: 17/17 invariant có cả mặt dương và mặt âm.
- *"không assertion 'done' không có evidence reference"* — **đạt**: mọi trạng thái cổng trong
  `gates.yaml` trỏ tới một `evidence_ref` hoặc được ghi `NOT_MET`; không cổng nào ghi `MET`.

---

## 6. Unresolved refs — change request PC09 phát ra

| ID | Gửi tới | Nội dung | Chặn gì |
| --- | --- | --- | --- |
| `CR-PC09-01` | PC01, PC03, PC04, PC07, PC08 | **12 scenario chưa có fixture:** SC10, SC32, SC33, SC34, SC35, SC36, SC44, SC49 (26/36 cạnh), SC50, SC51, SC52, SC53. Ưu tiên **SC50** (danh mục hiện KHÔNG có đối chứng dương đầu-cuối nào) và **SC44** (operation phá hủy nhất trong inventory). SC33–SC36 đã có `scenario_definitions` trong `run.yaml`, chỉ thiếu dữ liệu | G3, G4; E1 của các nhóm liên quan |
| `CR-PC09-02` | PC01 | **26/36 cạnh bị cấm không có `denied_cases[]` với `expected_error_code`** (E0-10b FAIL). Gồm **FE-08** — chính cạnh `COL→AW` mà AMD-B12 gỡ vì nó phá I02. PC09 **không** tự chọn mã: ranh giới `FORBIDDEN_EDGE`/`UNAUTHORIZED`/`CAPABILITY_DENIED` đã từng là `CR-PC08-03`/`-04` | G1-X5, G4-X5 |
| `CR-PC09-03` | PC03, PC05, PC06, PC07 | **50 dòng P0/XN-hoặc-UQ ở `PARTIAL`.** Nhóm cần xử lý thật: thiết lập/vận hành (`REQ-S5.1-01`…`-03`, `REQ-S5.4-03`, `REQ-S6.1-01`, `REQ-S11.2-05`, `-06`) và màn hình/luồng đọc (`REQ-S4-01`, `-08`, `-09`, `-10`, `REQ-S5.3-01`, `-03`). Nhóm mốc triển khai và chỉ tiêu thành công **nên giữ PARTIAL** — chúng phủ bằng cổng, ép thành COVERED là làm đẹp con số | G4 |
| `CR-PC09-04` | PC03 | `contracts/state/analysis.yaml`: TSR-A01 viết "Từ `valid` không có transition đi ra" trong khi cùng file có T-AN-12 và T-AN-13 (E0-09 FAIL). MINOR nhưng đúng lớp lỗi `F-A1R1-01` | G2-X3, G4-X5 |
| `CR-PC09-05` | PC08 | `acceptance/fixtures/recovery/README.md` mô tả ca (i) là `FORBIDDEN_EDGE`, và `oracle_vi` **bên trong chính fixture** vẫn viết "audit ghi hai lần từ chối với mã FORBIDDEN_EDGE" — trong khi `error_code` của fixture và ruling `CR-PC08-04` đều nói `UNAUTHORIZED`. Fixture tự mâu thuẫn là chỗ dễ nhất để harness lấy sai kỳ vọng | Không chặn cổng; chặn oracle của SC41 |
| `CR-PC09-06` | PC00 | **Phân xử dải scenario (đóng `CR-PC07-06`):** đã kiểm — PC05 và PC06 **không lấy ID nào** (fixture của hai gói chỉ trích SC01–SC31); PC07 lấy **SC45–SC48**, **không va chạm**. PC09 cấp **SC49–SC53** và cần anchor với `subject_vi` lấy từ `acceptance/scenarios.yaml` | G0 anchor completeness |
| `CR-PC09-07` | PC10 | `precode/gates.yaml` §`invalidation_rules` (INV-01..INV-10) và `precode/change-control.md` (write target của PC10) mô tả cùng chủ đề từ hai phía. `change-control.md` **không** được định nghĩa lại quy tắc invalidation mà nên trích `INV-nn`; nếu không, lớp lỗi "một hành vi, hai mô tả" lặp lần thứ tư | G5 |

### 6.1 Scenario ID PC09 đã cấp — cần PC00 neo anchor

| ID | Chủ đề | Vì sao cần |
| --- | --- | --- |
| `SC49` | Quét default-deny trên cả 36 cạnh bị cấm | Trước PC09, **không cạnh nào** trong 36 cạnh có scenario |
| `SC50` | Đường chạy THÀNH CÔNG đầu-cuối theo SRC-SPEC §5.2 | 48 scenario đầu đều là nhánh lỗi hoặc một lát cắt; không cái nào khẳng định một đợt bình thường kết thúc đúng |
| `SC51` | Thiết lập lần đầu theo SRC-SPEC §5.1 | Năm dòng `REQ-S5.1-01..05` (bốn XN, P0) hoàn toàn không được trích dẫn ở đâu |
| `SC52` | Dựng lại embedding generation rồi chuyển active nguyên tử | I12 trước đó chỉ có mặt âm (bị chặn) |
| `SC53` | Đối soát sau restore HOÀN TẤT → dispatcher mở, outbox cũ vẫn không phát lại | I15 trước đó chỉ có mặt âm (bị khóa) |

### 6.2 Quyết định PC09 đưa ra (không có trong baseline §5)

Không có stop gate §6 nào kích hoạt. Ba quyết định, đều mang tính phương pháp chứ không phải sản
phẩm, và đều được ghi tại chỗ:

1. **Quy tắc `coverage_status` của `traceability.csv`** (ghi đủ ở front-matter `precode/review.md`,
   khóa `traceability_csv_contract_header.coverage_status_rule_vi`). Điểm đáng soi: một dòng nhận
   `BLOCKED_B<nn>` khi nó nằm trong danh sách "REQ ảnh hưởng" của `AMD-B<nn>` — nghĩa là **văn bản
   cam kết của chính dòng đó** đổi nếu Owner phê chuẩn. 84 dòng rơi vào diện này. Với mọi dòng bị
   ghi đè, cột `notes` vẫn giữ độ phủ nền (`coverage=COVERED` / `coverage=PARTIAL`) để không mất
   thông tin. Nếu Coordinator muốn một quy tắc khác thì đây là chỗ đổi, và con số ở `review.md` §2
   phải tính lại.
2. **Header của `acceptance/traceability.csv` được đặt ở front-matter `precode/review.md`**, theo
   đúng tiền lệ đã được chấp nhận cho `requirements.csv` (ruling ghi ở `precode/baseline.json`):
   một dòng comment hay front-matter sẽ làm `csv.DictReader` đọc sai. `e0_check` `E0-17` kiểm sự
   tồn tại và đầy đủ của header thay thế này.
3. **`x-contract.deviations` chấp nhận tên trường đồng nghĩa.** Ruling FIX4 chốt bộ
   `{rule, deviation, reason, evidence_refs}`; `contracts/schemas/analysis-result.schema.json` của
   PC06 đã land với bộ tên dài hơn (`convention_deviated_from`, `what_this_schema_does_instead`,
   `reason_vi`, `finding_ref`/`ruling_ref`). Vì ruling nói "deviation đã khai báo là PASS-với-note,
   không FAIL", tôi chấp nhận đồng nghĩa và **ghi một note nêu đích danh tên đã dùng**, thay vì
   FAIL một deviation đã được khai đầy đủ về nội dung. Nếu Coordinator muốn ép đúng bốn tên thì
   đây là một sửa nhỏ ở PC06 cộng một dòng ở `e0_check`.

### 6.3 Sai lệch có chủ đích so với văn bản packet

| Packet nói | PC09 làm | Vì sao |
| --- | --- | --- |
| "`evidence/index.json` validates against `manifest.schema.json`" | `index.json` là object chỉ mục; **mỗi bản ghi** trong `records[]` validate được (55/55) | Một schema mô tả một manifest không validate được một danh sách manifest. Cách đọc được ghi trong chính `index.json` |
| "SC01–SC28 + SC29+ nếu cần" | 53 scenario, SC49–SC53 là của PC09 | Bốn lỗ hổng đo được: 36 cạnh không scenario; không có đối chứng dương đầu-cuối; §5.1 không scenario; I12/I15 chỉ có mặt âm |
| "expect G0–G3 `MET_PROVISIONAL` at best" | G0 = `MET_PROVISIONAL`; **G1, G2, G3 = `PARTIALLY_MET`** | Mỗi cổng có ít nhất một điều kiện ra đo được và **chưa đạt**: G1-X5 (26 cạnh), G2-X3 (TSR-A01), G3-X5 (`REQ-A6` và `CR-PC07-04` còn `KC`). Ghi `MET_PROVISIONAL` cho chúng sẽ là nâng nhãn bằng suy diễn |

### 6.4 Mối lo còn lại

1. **Đây là `SELF_VALIDATION` do người viết một phần corpus tự chạy.** Tôi viết cả
   `e0_check.py` lẫn `scenarios.yaml`, `traceability.csv` và `gates.yaml` mà nó kiểm. Một công cụ
   chỉ nhìn nơi tác giả của nó nghĩ tới — `F-A1R3-01` tồn tại đúng vì lý do đó. Auditor nên chạy
   một checker độc lập, không phải chạy lại của tôi.
2. **Drift 57 file trong lúc gói chạy.** Kết luận E0 gắn với đúng 121 hash trong
   `baseline_hashes` của file run. Auditor nên đo lại trên bytes của epoch kế tiếp.
3. **Năm finding của A1-R3 chưa được xác minh trên epoch mới**, và các bản sửa FIX4 chưa được ai
   độc lập kiểm. `gates.yaml` G4-X7 ghi điều này là chưa đạt. Lần chạy `E0-15` của tôi cho
   0 unresolved trên bốn thư mục đo được — nhưng đó là số của PC09, **không** phải xác minh độc lập.
4. **Không đóng finding nào, không phê chuẩn quyết định nào.** Trạng thái đúng của mọi finding do
   PC09 chạm tới là `FIX_PROPOSED` hoặc `OPEN`. B01–B17 vẫn `OPEN`; product status vẫn
   `NOT_READY_FOR_PRODUCT_CODE`.
5. **`review.md` §8.2 phân loại 70 CR của các gói khác dựa trên lời tự khai của chính chúng.** Tôi
   không xác minh từng cái. Coordinator nên coi cột "đã được đáp ứng ngược dòng" là một danh sách
   cần kiểm, không phải một kết luận.

---

## 7. Trạng thái bàn giao

- **next actor:** `Coordinator`.
- **Việc đề nghị Coordinator làm:** (1) rehash độc lập 9 file ở §2 trước khi phát
  `FROZEN_CANDIDATE`; (2) định tuyến `CR-PC09-01` … `CR-PC09-07`; (3) chuyển `CR-PC09-06`
  (anchor SC49–SC53) cho PC00; (4) phát packet cho A2/Auditor độc lập trên epoch mới — người xác
  minh **không được** là người viết bản sửa (protocol §8); (5) chuyển
  `precode/owner-decision-request.md` (24 mục) lên Owner, kèm `precode/review.md` §10 làm bản đối
  chiếu "mục nào chặn cái gì".
- **lease_released_at (UTC):** 2026-09-06T19:42Z. `LEASE-PC09-e1` được nhả tại đây. Sau thời điểm
  này `worker-W6` **không ghi thêm bất kỳ file nào**, kể cả sửa lỗi đánh máy. Mọi sửa đổi tiếp theo
  cần packet mới, baseline mới (hash ở §2) và lease mới với fencing ≥ 2.
- **Freeze:** PC09 **không** tự chứng nhận freeze. Việc phát hành `FROZEN_CANDIDATE` thuộc
  Coordinator.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng. `NOT_READY_FOR_PRODUCT_CODE` giữ nguyên; B01–B17 vẫn
  `OPEN` trong `agent_profile/registry.json`.

---

# ADDENDUM — PKT-PC09-FIX1 (sau đợt FIX5)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09-FIX1` · worker `worker-W6` |
| authority_id | `AUTH-COORD-PC09-FIX1` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC09-e2` (exclusive, fencing 2) |
| status | **`DONE`** · completion_claim `DRAFT_FOR_REVIEW` |
| audit_route | `INDEPENDENT_REQUIRED` — **A2 chưa chạy** (`NOT_RUN`) |

## H1. Changes

Mọi `before` là hash trong bảng §2 của handoff gốc (đã rehash ngay trước khi sửa; không file nào
bị chạm giữa hai lease).

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `acceptance/scenarios.yaml` | MODIFY | `fd7f7a11…d207e` (151546) | `ca7d40012e20afea27797aed30cee54b16e04860bf44b22cab44dce48a453747` (156201) |
| `acceptance/traceability.csv` | MODIFY | `2001cd12…bb0ea` (89283) | `f0bafff588a3b47d30a9e346ea3ddafdb946f27b525514de1d1247870c89b7b5` (92480) |
| `evidence/index.json` | MODIFY | `78b47157…4fe94` (181334) | `499ce474f77ceece9051e113d921827548e45ea3f25c6e9d7981cbe08e834fe4` (183498) |
| `evidence/tools/e0_check.py` | MODIFY | `6a480278…2fda2` (81195) | `d13d8c2a1263e3aa21f90801a297f8ff064848f80b7c14a550cf91c5f5a98443` (88422) |
| `evidence/tools/README.md` | MODIFY | `de16e900…961ae` (12303) | `0232eba4c64be2e8d779d470deb9ea58741e31438fbe6ad19af2dcdc179941ca` (14519) |
| `precode/gates.yaml` | MODIFY | `57e13833…2770c` (29460) | `2554ea6b7b37205f170b8d0312159716b537c8aadfca98774fa6c5c6e30d3cf4` (30893) |
| `precode/review.md` | MODIFY | `0f8a24f7…863eb0` (58141) | `5907f37bb4e487088c44c52f87c52c09075a58af6036b7b0aee369d2dfc2003d` (70984) |
| `evidence/runs/E0-20260907T004621Z.json` | CREATE | ABSENT | `366ab4ecd66d3b6e1a9fc42bc52ad4c7ac943d7e235ed19ef49c6eee629a6a5f` (35879) |
| `evidence/handoffs/PC09-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* | — |

`evidence/manifest.schema.json` **không đổi** (`68d1da65…f86cc`, 20766 B).

**File run trung gian đã xóa.** Trong đợt này tôi chạy E0 nhiều lần và mỗi lần đều xóa file run
trước rồi ghi file mới, để `evidence/runs/` chỉ chứa **đúng một** lần chạy — lần được đăng ký
trong `evidence/index.json`. Sáu file run trung gian đã tồn tại rồi bị xóa (`E0-20260906T193638Z`,
`193716Z`, `20260907T004056Z`, `004127Z`, `004146Z`, `004341Z`, `004527Z`). Ghi lại thay vì im
lặng. Không có `__pycache__`/`.pyc`; không lệnh git mutation; không mạng; không secret; không
spawn agent; mọi script phụ trợ dưới `…/scratchpad/w6/`.

## H2. Cổng chờ

Poll `evidence/handoffs/PC08-handoff.md` theo chỉ thị. Addendum **PKT-PC08-FIX2** với
`lease_released_at 2026-09-07T00:28Z` đã có mặt **ngay ở lần poll đầu tiên** — không phải chờ.
`PKT-PC01-FIX8` (thêm `event_type` cho năm sự kiện `operation: null` của fixture `boundary/`) và
`PKT-PC01-FIX9` cũng đã land trước lần chạy cuối.

**Drift quan sát được, ghi theo yêu cầu:** giữa hai lần chạy thử,
`acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` đổi hash
`795d19a6ff080817487ed470208f3ec4905372a28c1eb2b66e53d3ae55eda8ee` →
`ffab4679078e8d93227bb2751743482b44981ec6a84de1f404a389f59ec0213e`. Verdict E0 của cả hai lần đều
19/19 PASS, nên drift không đổi kết luận — nhưng nó đổi *bytes mà kết luận gắn vào*. Tôi kiểm file
ổn định trong 45 giây rồi mới chạy lần cuối. Hash tại lần chạy cuối là `ffab4679…0213e`, và
`baseline_hashes` của run file có **136 mục, 0 mục drift** tính tới lúc bàn giao.

## H3. Việc đã làm theo packet

1. **`fixture_refs` cho 12 scenario** (ruling R5-02): SC10, SC32, SC33, SC34, SC35, SC36, SC44,
   SC49, SC50, SC51, SC52, SC53 nay trỏ tới file thật. **Không scenario nào còn `MISSING`.**
   `notes_vi` của từng scenario được viết lại: nêu fixture nào cấp, và — quan trọng hơn — **cái gì
   vẫn chưa được đóng** (ví dụ SC44: fixture khóa được CƠ CHẾ hai pha nhưng không khóa được DANH
   SÁCH LOẠI TRỪ, vốn vẫn `OWNER_DECISION_REQUIRED`).
2. **`CR-PC04-11`:** `event_order` của SC52 nay trích hai operation authoritative
   `embedding.start_generation_rebuild` và `embedding.activate_generation`. Hai tên cũ
   (`embedding.start_generation`, `embedding.switch_generation`) **không tồn tại** trong
   `ports.yaml`. Chúng lọt qua `E0-04` vì `E0-04` chỉ đọc trường **có cấu trúc**, còn `event_order`
   là danh sách câu văn — một ví dụ cụ thể của giới hạn đã khai và nay được ghi vào `review.md` §13.
3. **`e0_check.py`:**
   - `E0-07-id-refs`: range marker (`SC54+`) không còn bị coi là citation, và
     **`evidence/handoffs/` được loại khỏi lượt quét văn xuôi** của cả `E0-06` lẫn `E0-07`. Lựa
     chọn thứ hai là quyết định, không phải điều hiển nhiên: handoff là bản ghi bằng chứng, chúng
     trích dẫn hợp lệ range marker và các ID sai dạng mà chính chúng đang *báo cáo*. Trường **có
     cấu trúc** trong handoff vẫn được kiểm. Giá phải trả, nói thẳng: một ID sai chỉ nằm trong câu
     văn của handoff sẽ không bị bắt. Ghi ở `evidence/tools/README.md` §5.7.
   - Ba thư mục mới `boundary/`, `e2e/`, `ui/` nằm trong phạm vi mọi cửa fixture (các cửa khớp
     theo tiền tố nên nhận tự động); thêm `EXPECTED_FIXTURE_DIRS` để một thư mục **biến mất** bị
     báo lỗi thay vì đếm là 0.
   - `NOT_APPLICABLE_FREEFORM` giữ nguyên ngữ nghĩa.
   - **Luật mới:** sự kiện `operation: null` phải khai `event_type` ∈ {`local_observation`,
     `in_process_call`}. Khi thêm, luật bắt đúng năm sự kiện của fixture `boundary/`; W2 đã sửa cả
     năm trước lần chạy cuối.
   - **`CR-PC01-11`:** `E0-10b` được siết từ "có mặt" sang **song ánh khớp nội dung** — xem H4.
4. **Chạy lại E0**, cập nhật `index.json`, `traceability.csv`, `gates.yaml`, `review.md`. A2 được
   ghi là **pending** ở `review.md` §4.1 và ở `gates.yaml` G4-X7.

## H4. `CR-PC01-11` — và một self-test âm

`E0-10b` bản cũ chỉ hỏi *"cạnh này có một denied case với `expected_error_code` không rỗng
không?"*. Câu hỏi đó pass ngay cả khi denied case nói về một cạnh khác, hoặc khi fixture kỳ vọng
một mã khác với hợp đồng. Bản mới kiểm một song ánh ba chiều có khớp nội dung: mỗi `FE-nn` ↔ đúng
một `denied_cases[]` (khớp `attempted_edge.caller/callee`, mã đã đăng ký) ↔ đúng một sự kiện trong
fixture quét (khớp `actor`, `callee`, `denied_case_ref`, `expected_error_code`, và `operation` khi
có nêu), cộng hai chiều ngược chống tham chiếu treo và trỏ trùng.

Kết quả: **36 cạnh ↔ 36 denied case ↔ 36 sự kiện, 0 vi phạm.**

Vì một `PASS` chỉ đáng tin khi check thật sự bắt được lỗi, tôi chạy một **self-test âm** trên một
bản sao corpus trong thư mục scratch: đổi `expected_error_code` của `NC-01`, trỏ
`denied_case_ref` của một sự kiện sang `NC-99` không tồn tại, đổi `actor` của một sự kiện khác.
Check bắt **cả ba**, mỗi lỗi một dòng nêu đúng chỗ lệch. Bản sao đã bị xóa; nó không bao giờ nằm
trong repo.

## H5. Evidence

- **EV-PC09-01** — `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py --repo … --json-out evidence/runs/E0-20260907T004621Z.json`
  · started/ended 2026-09-07T00:46:21Z · **exit code 0** · **19/19 PASS, 0 vi phạm** ·
  `baseline_hashes` 136 mục, 0 drift.
- **EV-PC09-02** — 55/55 bản ghi của `evidence/index.json` validate với `manifest.schema.json`,
  0 lỗi.
- **EV-PC09-03** — traceability 246 == 246 dòng; `ORPHAN` 0. `COVERED` 76 → **90**, `PARTIAL`
  74 → **60**, `PARTIAL` P0 XN/UQ 50 → **37** (8 gate-only, 19 contract-only, 10 scenario-only).
- **EV-PC09-04** — 18/18 AC có scenario; 17/17 invariant có cả hai cực; 28/28 mã lỗi có scenario;
  53 scenario, **0 scenario thiếu fixture**; 87 fixture trên 9 thư mục.
- **Kiểm card (Coordinator giao, PC10 không chạy):** hạng mục P0 có ≥ 1 card — **0/12 trực tiếp**
  (không card nào trích id hạng mục P0; 18 card chỉ trích 7 id yêu cầu) và **12/12 bắc cầu** qua
  scenario. Đọc đúng: card tham chiếu *scenario*, scenario mang `requirement_refs` — thiết kế hợp
  lệ theo SRC-PLAN §15, nên "0/12" không phải khiếm khuyết. Nhưng chuỗi bắc cầu chỉ bền khi mọi
  hạng mục P0 có scenario: khi chạy lần đầu, `REQ-P0-08` có **0 card theo cả hai cách** vì không
  scenario nào trích nó — tôi thêm nó vào SC12 và SC13 (chính xác, không độn số) và con số thành
  12/12. **53/53 scenario được ít nhất một card trích dẫn.** Cards pin theo epoch
  `PC10-PIN-FCW4-20260907`, trích file PC09 theo đường dẫn + SC id, không theo hash — cách pin
  đúng.
- **`NOT_RUN`:** E1–E4 ở cả 53 scenario (32 placeholder tường minh); audit độc lập của chính gói
  này; validator OpenAPI 3.1 (không có trong môi trường, packet cấm cài).

## H6. Trạng thái cổng

G0 `MET_PROVISIONAL` · **G1 `PARTIALLY_MET` → `MET_PROVISIONAL`** · **G2 `PARTIALLY_MET` →
`MET_PROVISIONAL`** · G3 `PARTIALLY_MET` · G4 `PARTIALLY_MET` · G5 / SP1 `NOT_MET` · G6 / G7
`NOT_APPLICABLE_YET`.

G4 còn đúng hai điều kiện chưa đạt, và **không Worker nào gỡ được cái nào**: G4-X6 (Owner phê
chuẩn B01–B17) và G4-X7 (A2 xác minh trên epoch chứa FIX4/FIX5).

## H7. CR còn lại

| ID | Trạng thái | Ai |
| --- | --- | --- |
| `CR-PC09-01`, `-02`, `-03`, `-04`, `-05` | `FIX_PROPOSED` — đóng bởi ruling R5-01…R5-05, **chờ A2 xác minh** | — |
| `CR-PC09-06` | **OPEN** — neo anchor `SC49`–`SC53` vào `baseline.json` | W1 (PC00), ruling R5-06 |
| `CR-PC09-07` | **OPEN** — `change-control.md` phải TRÍCH `INV-01`…`INV-10` thay vì định nghĩa lại | W7 (PC10-FIX1), ruling R5-07 |
| `CR-PC09-08` | **OPEN, mới** — đưa kiểm tra "mỗi hạng mục P0 có ≥ 1 card" thành check E0 thường trực sau khi `agent-tasks/` ổn định. Một lần chạy tay không ngăn được hồi quy; tôi không thêm vào `e0_check.py` ở đợt này vì `agent-tasks/` ngoài read set gốc và PC10 vẫn đang đổi | Coordinator định tuyến |
| `CR-PC04-11` | **ĐÓNG** ở gói này | — |

## H8. Mối lo còn lại

1. **19/19 PASS là con số của phía sửa, chạy bằng công cụ do phía sửa viết.** A2 nên chạy một
   checker **độc lập**, không phải chạy lại `e0_check.py`. Hai lỗi tìm được trong chính đợt này —
   `CR-PC04-11` (hai operation không tồn tại trong `event_order`) và `CR-PC01-11` (check cũ quá
   yếu) — đều là lỗi mà công cụ của tôi **không** bắt trước khi có người chỉ ra.
2. **`collection/` và `recovery/` có cột được đo nhờ fixture MỚI, nhưng fixture GỐC của chúng vẫn
   ở dạng văn xuôi** và vẫn ngoài tầm với của cửa kiểm cột. `boundary/` báo
   `NOT_APPLICABLE_FREEFORM` một cách chính đáng: oracle của nó là "không hàng nào đổi", không
   phải một tập hàng.
3. **Bốn mục `KC` không giải được trong phiên này vì không có mạng:** `REQ-A5`, `REQ-A6`/`REQ-D34`,
   `CR-PC07-04`, `CR-PC05-03`. Hai trong số đó chặn cứng hai module. Không giá trị nào bị bịa.
4. Không finding nào được đóng, không quyết định nào được phê chuẩn. B01–B17 vẫn `OPEN`; product
   status vẫn `NOT_READY_FOR_PRODUCT_CODE`.

## H9. Trạng thái bàn giao

- **next actor:** `Coordinator` → sau đó **A2** (auditor độc lập cuối).
- **lease_released_at (UTC):** 2026-09-07T00:47Z. `LEASE-PC09-e2` nhả tại đây; `worker-W6` không
  ghi thêm file nào, kể cả sửa lỗi đánh máy. Sửa tiếp cần packet mới, baseline mới (hash ở §H1) và
  lease fencing ≥ 3.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng.

---

# ADDENDUM — PKT-PC09-FIX2 (sau AUDIT_REPORT PKT-A2-R1 và đợt FIX6)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09-FIX2` · worker `worker-W6` |
| authority_id | `AUTH-COORD-PC09-FIX2` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC09-e3` (exclusive, fencing 3) |
| status | **`DONE_WITH_CONCERNS`** · completion_claim `DRAFT_FOR_REVIEW` |
| audit_route | `INDEPENDENT_REQUIRED` — A2 đã chạy **`PKT-A2-R1`** (verdict PC09 = FAIL); **`PKT-A2-R2` chưa chạy** |

Lý do `DONE_WITH_CONCERNS`: mọi mục của packet đã làm, nhưng lần chạy E0 cuối thoát **exit code 1**
với 13 vi phạm `E0-04b`, tất cả nằm trong file **ngoài quyền ghi** của PC09.

## J1. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `acceptance/scenarios.yaml` | MODIFY | `ca7d4001…53747` (156201) | `4985c22f5b9b0c5caaf8ca49f2759e3b5d2372d4e1527b1739b2910570fcbfdc` (167813) |
| `acceptance/traceability.csv` | MODIFY | `f0bafff5…9b7b5` (92480) | `cef95b2fc487e39bd84b5c5f89f8aacb4fe4f0d716bae8f8d5df734a9d62bf94` (92754) |
| `evidence/index.json` | MODIFY | `499ce474…34fe4` (183498) | `738c49e6f64a85eb700d59c6c34f7a3632b1e10917c2618ac22cc40f8880f6cf` (189087) |
| `evidence/tools/e0_check.py` | MODIFY | `d13d8c2a…98443` (88422) | `e162add6b704331532859ce5cc97336e550e952405cf7a1aa3cd8362302f583c` (99472) |
| `evidence/tools/README.md` | MODIFY | `0232eba4…41ca` (14519) | `f177c59884f1405884b38847ff7197f87eea8caff00a9cdc2cf13235e327001b` (16684) |
| `precode/gates.yaml` | MODIFY | `2554ea6b…d3cf4` (30893) | `0ddf0bfedea0a446b7c9b8915e2d4ba802fcad3e0fb90027f9c726b5612e0ee5` (31561) |
| `precode/review.md` | MODIFY | `5907f37b…2003d` (70984) | `0e40600bb69b0c597ac40ab95ca36e1504a3e997165d6e4477e0c5787138591d` (91312) |
| `evidence/runs/E0-20260907T012946Z.json` | CREATE | ABSENT | `6aaaf6ae80ae47e793df1f70ea41eb5db3c996e3d76b78ed9a281e12cf16496b` (42047) |
| `evidence/handoffs/PC09-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* | — |

`evidence/manifest.schema.json` không đổi. Nguồn pinned khớp ở cả hai lần kiểm. Không
`__pycache__`/`.pyc`; không lệnh git mutation; không mạng; không secret; script phụ trợ dưới
`…/scratchpad/w6/`. Các file run trung gian được xóa để `evidence/runs/` chỉ giữ đúng lần chạy
được đăng ký.

## J2. Cổng chờ

Poll ba addendum theo chỉ thị: **PKT-PC01-FIX10**, **PKT-PC02-FIX6**, **PKT-PC00-FIX5** — cả ba
có mặt kèm `lease_released_at` trước lần chạy cuối. PC10-FIX3 cũng đã land. Trong lúc chờ,
`contracts/data/entities.yaml` có một khoảng **không parse được** (W3 đang ghi giữa chừng); tôi
không dùng số nào từ khoảng đó và chỉ suy ra số sau khi cả ba cổng mở.

## J3. Từng finding của A2

| Finding | Đã làm |
| --- | --- |
| **F-A2R1-01** MAJOR | Sửa **9** id operation không tồn tại trong `event_order` của 8 scenario về tên authoritative của `ports.yaml` (SC01, SC12, SC24, SC27, SC42, SC43, SC53). **SC12 bước 3 được VIẾT LẠI, không đổi tên**: quan sát nguồn bị xóa đi kèm lô ingest dưới dạng trường `source_deleted_observed_at` của `ingest.submit_batch` — PC01 đã bác một operation riêng. Thêm check **`E0-04b-prose-op-tokens`** quét mọi chuỗi (văn xuôi lẫn có cấu trúc) dưới `contracts/` và `acceptance/`, loại trừ có nguyên tắc (tên file, `<entity>.<field>` đã khai, `<máy trạng thái>.<field\|enum>` đã khai, danh sách từ vựng trạng thái viết trong công cụ) |
| **F-A2R1-02** MAJOR | Mọi con số headline nay **sinh ra** bởi `derive_numbers.py` và ghi kèm khóa nguồn; dòng tổng của một bảng được **parse từ chính bảng đó**. Bốn con số sai đã sửa: transition 63→**67**, fixture 87→**86**, module 10/15→**9/16**, DoR 10/0/2→**8/2/2** (dòng #5 chuyển ✅→⚠️ theo F-A2R1-09). Tôi chạy một cổng tự kiểm so review với giá trị suy ra: **CONSISTENT** |
| **F-A2R1-03** MEDIUM | §9.1 nay **đọc** epoch từ card bằng một lệnh `grep` được ghi ra, và ghi giá trị tại thời điểm chạy: `PC10-PIN-FCW4c-20260907`, **18/18 card đồng nhất** |
| **F-A2R1-04** MEDIUM | §8.2 sinh bằng `crtable.py` quét toàn repo: **99 CR** (86 từ PC00–PC08, 8 PC09 — nay 11, 5 PC10), mỗi id một dòng trạng thái theo một quy tắc duy nhất được ghi ra. Hai disposition của Coordinator ghi nguyên văn: **`CR-PC01-09` APPROVED**, **`CR-PC02-18` ACCEPTED_AS_LIMITATION** |
| **F-A2R1-05** MEDIUM | `E0-10b` nay kiểm operation được gọi tên phải **do chính callee sở hữu** khi callee là `MOD-*`; khi callee là `EXT-*` thì theo quy ước W2 đã viết vào `modules.yaml default_deny`. 36/36 sạch |
| **F-A2R1-08** LOW | `E0-15` nay báo `files_with_rows` / `files_without_rows` mỗi thư mục; §13 mục 5 có bảng đầy đủ 9 thư mục. Bản trước thiếu `ai/` — **9/11 file** của thư mục đó không dùng `rows[]` |
| **F-A2R1-09** LOW | DoR dòng 5 chuyển ✅→⚠️ và **nêu tên** 5 operation thiếu `scenario_refs`/`error_codes` |
| **F-A2R1-10** LOW | `E0-11b`: `mixed` nay tính cho **không cực nào**. Ba invariant lộ ra thiếu: I04 (không âm), I14 (không cực nào), I16 (không âm) → thêm **SC54, SC55, SC56** |
| **F-A2R1-11** INFO | `evidence/runs/` bị loại khỏi phạm vi quét nên `files_scanned` tái lập được; ghi ở tools README |

## J4. Ba scenario mới — và vì sao tôi KHÔNG đổi nhãn thay vì thêm

`SC54` (negative, I04) · `SC55` (positive, I14) · `SC56` (negative, I14 + I16). Cả ba **không tạo
dữ liệu mới** — chúng trỏ vào fixture `ai/` đã có.

A2 đã đọc SC16 và SC28 và kết luận rằng **nội dung** của SRC-PLAN §7 vẫn được thỏa: các phản chứng
có thật, chỉ nằm lẫn trong ca hỗn hợp. Tôi có thể đổi nhãn SC16 → `positive` và SC28 → `negative`
và mọi thứ sẽ xanh ngay. Tôi **không** làm thế: đổi nhãn cho hợp checker chính là lỗi mà bản trước
đã mắc ở dạng khác, và nó làm mất thông tin thật (hai ca đó thực sự khẳng định cả hai chiều). Tách
phần phản chứng ra thành ca đứng riêng đắt hơn nhưng đúng với điều SRC-PLAN §7 đòi: **một
counterexample có thể fail một mình**.

Ba ID cần PC00 neo anchor (`CR-PC09-06` mở rộng từ SC49–SC53 thành SC49–SC56).

## J5. Evidence

- **EV-PC09-01** — `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py --repo … --json-out evidence/runs/E0-20260907T012946Z.json` · **exit code 1** · **20 check: 19 PASS, 1 FAIL, 13 vi phạm**.
- **EV-PC09-02** — 56/56 bản ghi `evidence/index.json` validate với `manifest.schema.json`.
- **EV-PC09-03** — traceability 246 dòng; `COVERED` 90 · `PARTIAL` 60 · `BLOCKED_B*` 84 · `DEFERRED_P1` 6 · `OUT_OF_SCOPE` 6 · **`ORPHAN` 0**; `PARTIAL` P0 XN/UQ = **37** (19 contract-only, 8 gate-only, 10 scenario-only).
- **EV-PC09-04** — 18/18 AC có scenario; **17/17 invariant có cực dương VÀ cực âm chuyên dụng**; 28/28 mã lỗi có scenario; **56** scenario, **0** thiếu fixture; **86** fixture trên **9** thư mục.
- **EV-PC09-05 (mới)** — `derive_numbers.py` → `numbers.json`, `crtable.py` → `cr_table.md` + `cr_summary.json`. Artefact của F-A2R1-02/-04. Cổng tự kiểm so ba con số headline với giá trị suy ra: **CONSISTENT**.
- **Self-test âm của `E0-10b`** (từ đợt trước) vẫn hợp lệ. **Không** chạy self-test âm cho `E0-04b` — thiếu sót đã biết, xem J7.
- **`NOT_RUN`:** E1–E4 ở cả 56 scenario (32 placeholder); audit độc lập bản sửa này; validator OpenAPI 3.1.

## J6. FAIL còn lại — 13 vi phạm `E0-04b`, không cái nào trong file của PC09

| Nhóm | Số | Ở đâu | CR |
| --- | ---: | --- | --- |
| `SAVE_ALREADY_EXISTS` chưa đăng ký | 2 | `entities.yaml`, `ports.yaml` | **`CR-PC09-09`** → W3/W2 (ruling F-A2R1-06 chưa land) |
| Sáu tên cột không tồn tại được gọi trong văn xuôi | 9 | `openapi.yaml`, `collector-probe.md`, `selection.md`, `time-and-tags.md`, `retry-policy.yaml`, `state/run.yaml`, `telegram/delivery.md`, `screens.yaml` | **`CR-PC09-10`** → gói sở hữu từng file. `run.rate_limited_at`, `run.last_run`, `report.selection_version`, `work.resolution_rule`, `delivery.created_at`, `tag.updated_at` — **cùng lớp lỗi F-A2R1-01, mở rộng sang cột** |
| Tên operation cũ trong ghi chú fixture | 2 | `acceptance/fixtures/reporting/n-…json` | **`CR-PC09-11`** → W5 |

Tôi **không** sửa file ngoài quyền ghi và **không** nới check để chúng biến mất.

## J7. Mối lo còn lại

1. **Hai MAJOR của A2 đều là lỗi của tôi, và cùng một hình dạng:** một điều đúng được viết ra rồi
   không được biến thành thứ tự động kiểm được. §13 của bản trước cảnh báo đúng lớp lỗi
   `F-A2R1-01` bằng chữ; câu mở đầu của bản trước hứa mọi số đến từ E0. Cả hai lời đúng, cả hai
   không được ép. Bản này thay hai lời hứa bằng hai cửa kiểm — nhưng **một cửa kiểm mới chỉ chứng
   minh được chính nó sau khi một người độc lập chạy nó**.
2. **Tôi không chạy self-test âm cho `E0-04b`.** Với `E0-10b` tôi đã làm (đột biến ba chỗ, bắt cả
   ba). Với `E0-04b` tôi chỉ có bằng chứng gián tiếp: nó bắt 29 hit ngay lần chạy đầu và số giảm
   đúng theo từng loại trừ có nguyên tắc tôi thêm. Đó **không** phải bằng chứng nó bắt được một
   token sai mới. Đề nghị A2 tự đột biến một id.
3. **`E0-11b` từng tuyên bố nhiều hơn oracle của nó** (tính `mixed` cho cả hai cực). Bất kỳ check
   nào khác cũng có thể mang cùng khuyết tật — tiêu đề rộng hơn phép đo — và tôi không có cách
   phát hiện nó ngoài việc có người đọc từng oracle.
4. **`E0-10a` từng âm thầm tụt xuống `items_checked: 0` mà vẫn PASS** khi vòng lặp của nó bị mất
   trong một lần tôi sửa `E0-10b` ở đợt trước. Nay có `Check.finalize()` ép mọi check kiểm 0 mục
   thành `BLOCKED`. Điều đáng lo là nó đã lọt qua một lần.
5. **Quy tắc trạng thái của sổ CR là cơ học, và `CLOSED_CLAIMED` là lời khai, không phải closure.**
   16 CR mang nhãn đó chỉ vì một dòng handoff nói đã đóng.
6. B01–B17 vẫn `OPEN`; E1–E4 `NOT_RUN`; `NOT_READY_FOR_PRODUCT_CODE` giữ nguyên. Không finding nào
   được đóng, không quyết định nào được phê chuẩn.

## J8. Trạng thái bàn giao

- **next actor:** `Coordinator` → **A2 (`PKT-A2-R2`)** trên epoch 5.
- **lease_released_at (UTC):** 2026-09-07T01:33Z. `LEASE-PC09-e3` nhả tại đây; `worker-W6` không
  ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §J1) và lease fencing ≥ 4.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng.

---

# ADDENDUM — PKT-PC09-FIX3 (đợt FIX7)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09-FIX3` · worker `worker-W6` · lease `LEASE-PC09-e4` (fencing 4) |
| authority_id | `AUTH-COORD-PC09-FIX3` (parent `AUTH-OWNER-20260906-01`) |
| status | **`DONE_WITH_CONCERNS`** · completion_claim `DRAFT_FOR_REVIEW` |
| audit_route | `INDEPENDENT_REQUIRED` — `PKT-A2-R2` **chưa chạy** |

`DONE_WITH_CONCERNS` vì lần chạy cuối thoát **exit 1**: `E0-04c` còn 8 vi phạm, tất cả ở file
ngoài quyền ghi của PC09.

## K1. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `acceptance/scenarios.yaml` | MODIFY | `4985c22f…cbfdc` (167813) | `c831a6953f13eae5fe77be362c6e3e7e8f0423285973766eacf5a604da54831b` (167895) |
| `acceptance/traceability.csv` | MODIFY | `cef95b2f…2bf94` (92754) | `cef95b2fc487e39bd84b5c5f89f8aacb4fe4f0d716bae8f8d5df734a9d62bf94` (92754) — **không đổi**, sinh lại cho ra byte giống hệt |
| `evidence/index.json` | MODIFY | `738c49e6…80f6cf` (189087) | `3101ef97d20410c921a17aeac30b9bbb11a56067e7f9fb274ab1e1d58ae07ec1` (195459) |
| `evidence/tools/e0_check.py` | MODIFY | `e162add6…2f583c` (99472) | `3dcac5f48c3c9e0a0ec4042fd0dd6dcca9eb55979b80f61e6c1782431973693c` (102459) |
| `evidence/tools/README.md` | MODIFY | `f177c598…7001b` (16684) | `a57b339f07c2d0ca0285dbec761d06886cb620dcd6fad5fa18c86516f7be8246` (19671) |
| `precode/gates.yaml` | MODIFY | `0ddf0bfe…e0ee5` (31561) | `b949559c7ee797c17686a7a8ef41af4dab99538a4e6f98aae0240ad55246c734` (31998) |
| `precode/review.md` | MODIFY | `0e40600b…8591d` (91312) | `4ef032cb635aa0585416907ca4c8060f25383747c86e00a429fc2fb949a9bbab` (94795) |
| `evidence/runs/E0-20260907T014517Z.json` | CREATE | ABSENT | `1b2038bb61180a1384d3b954b1b95c13b3daebecbb07d32f537391b98aaf3ed6` (41282) |
| `evidence/handoffs/PC09-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* | — |

Nguồn pinned khớp ở cả hai lần kiểm. Không `__pycache__`/`.pyc`, không git mutation, không mạng,
không secret. `evidence/runs/` giữ đúng một file — lần chạy được đăng ký.

## K2. Cổng chờ

Poll đủ: **PKT-PC02-FIX7**, **PKT-PC01-FIX11**, **PKT-PC04-FIX4**, **PKT-PC00-FIX7** (và
**PKT-PC00-FIX8**) — tất cả có `lease_released_at` trước lần chạy cuối. PC10-FIX4 cũng đã nhả
(01:48Z); card epoch nay là `PC10-PIN-FCW4d-20260907`, đọc từ card bằng lệnh `grep` được ghi
trong `review.md` §9.1, **18/18 đồng nhất**. Coordinator xác nhận không còn thay đổi nội dung nào
trước freeze, nên đây là lần chạy cuối trên epoch này.

## K3. Tách `E0-04b` làm ba

Quy tắc do W2 viết vào `contracts/ports.yaml` `conventions.prose_token_rule_vi` — **nguồn duy
nhất**; công cụ chỉ thực thi. Một `` `<a>.<b> `` phân giải nếu là **operation của ports.yaml**
HOẶC **`<entity>.<column>` của entities.yaml**; phân đoạn đầu không phải domain operation cũng
không phải tên entity thì bỏ qua.

- **`E0-04b-prose-op-tokens`** — nửa operation. 284 kiểm, **0 vi phạm**.
- **`E0-04c-prose-column-tokens`** — nửa cột. 208 kiểm, **8 vi phạm** (§K5).
- **`E0-04d-prose-error-tokens`** — mã lỗi. 154 kiểm, **0 vi phạm**. `STATUS_VOCABULARY` nay gồm
  từ vựng trạng thái/claim của baseline §3 **và** các message type của `protocol.md`
  (`TASK_PACKET`, `HANDOFF`, `AUDIT_REPORT`, `FROZEN_CANDIDATE`, …), theo ruling.

Tách vì hai chế độ hỏng có **chủ sở hữu khác nhau và cách sửa khác nhau**: "gọi tên một operation
không tồn tại" và "gọi tên một cột không tồn tại" trước đây bị trộn vào một con số.

## K4. Self-test âm cho cả ba — và một bài học từ lần thử đầu

| Check | Đột biến | Kết quả |
| --- | --- | --- |
| `E0-04b` | `worker.claim_assignment` → `worker.grab_assignment` (`state/run.yaml`) | Bắt được |
| `E0-04c` | `saved_snapshot.content_hash` → `saved_snapshot.body_digest` (`scenarios.yaml`) | Bắt được |
| `E0-04d` | `TELEGRAM_SEND_UNCERTAIN` → `TELEGRAM_TOTALLY_MADE_UP` (`state/delivery.yaml`) | Bắt được |

**Lần thử đầu tiên của tôi chứng minh không gì cả, và trông giống như thành công.** Tôi tiêm bằng
`str.replace` mà **không kiểm** kết quả; hai token đích không tồn tại ở dạng tôi giả định
(`IDENTITY_CONFLICT` không được đặt backtick trong `errors.yaml`), nên đột biến không hề landing
và check báo `PASS`. Script nay in từng lần tiêm và thoát khác 0 nếu một token đích vắng mặt.
Thêm một điểm: phải chọn đột biến ở namespace **không nhập nhằng** — `report.publish_immediately`
là đột biến tồi để chứng minh `E0-04b` vì `report` vừa là domain operation vừa là tên entity, nên
token rơi vào nhánh "cả hai". Ghi cả hai bài học vào `evidence/tools/README.md` §5b.

## K5. Kết quả E0 và residual

Run `evidence/runs/E0-20260907T014517Z.json` · **22 check · 21 PASS · 1 FAIL · 8 vi phạm** ·
exit 1.

**Residual của lần chạy TRƯỚC (`E0-20260907T012946Z`), đếm lại từ chính file run đó:** 13 vi phạm
= **9 tham chiếu cột + 2 nhắc tên operation cũ + 2 nhắc mã lỗi chưa đăng ký**; theo *token phân
biệt* là 6 cột + 2 tên operation + 1 mã lỗi. Dispatch của FIX7 mô tả là "7 tham chiếu cột + 3 nhắc
tên cũ + 1 rule mis-cite" — **không khớp artefact**. Tôi ghi theo artefact và nêu khác biệt ở
`review.md` §3.2 thay vì chép con số của dispatch: một số headline không được lệch khỏi file nó
trích, đó chính là `F-A2R1-02`. Cả 13 đã được FIX7 xử lý (W3 thêm 6 cột, W5 sửa 2 đoạn prose,
W2/W3 gỡ 2 chỗ nhắc `SAVE_ALREADY_EXISTS`).

**FAIL hiện tại — `CR-PC09-12`, 8 token, không cái nào ở file của PC09.** Đây là các token mà bản
tách mới soi tới lần đầu:

| Token | Số | File | Vấn đề |
| --- | ---: | --- | --- |
| `coverage_window.predecessor` | 2 | `state/report.yaml`, `state/run.yaml` (W4) | Cột thật là `predecessor_window_id` |
| `post.mark_source_deleted` | 2 | `openapi.yaml` (W2), `ingest-batch.schema.json` (W3) | Operation PC01 đã **bác**, nay viết như một cột của `post` |
| `data_deletion_audit.does_not_guarantee` | 2 | `backup-restore.md`, `secrets.md` (W2) | Câu tiếng Anh bị đặt backtick thành dạng đường dẫn |
| `backup_snapshot.does_not_guarantee` | 1 | `backup-restore.md` (W2) | như trên |
| `telegram_link_code.format_match_attempt_count` | 1 | `fixtures/telegram/README.md` (W3) | Cột **từng được đề xuất** ở `CR-PC07-02`, chưa bao giờ tồn tại |

Một token là của tôi và đã sửa: SC07 dẫn `identity_alias.alias_value`; cột thật là
`id_value_normalized` (cộng `id_value_raw`). Oracle của SC07 nay khẳng định đúng hai cột đó.

## K6. Số liệu (đều do `derive_numbers.py` / `crtable.py` sinh)

246 dòng traceability · `COVERED` 90 · `PARTIAL` 60 · `BLOCKED_B*` 84 · `ORPHAN` **0** ·
`PARTIAL` P0 XN/UQ 37 · 56 scenario, 0 thiếu fixture · 86 fixture / 9 thư mục · 67 transition ·
85 operation · 36 cạnh cấm ↔ 36 denied case ↔ 36 sự kiện quét · 60 entity · 28 mã lỗi ·
module 9 READY / 16 BLOCKED / 5 chặn cứng · DoR 8 ✅ / 2 ⚠️ / 2 ❌ · **105 CR** (89 PC00–PC08,
12 PC09, 5 PC10; OPEN 62 · RULED 23 · CLOSED_CLAIMED 18 · APPROVED 1 · ACCEPTED_AS_LIMITATION 1).
Cổng tự kiểm so bốn con số headline với giá trị suy ra: **CONSISTENT**.

`evidence/index.json`: **58 bản ghi, 58/58 validate** với `manifest.schema.json`; 32 placeholder
`NOT_RUN` cho E1–E4.

## K7. Mối lo còn lại

1. **`E0-04c` còn 8 vi phạm thật.** Chúng ở file của W2/W3/W4 và tôi không sửa, không nới check.
   Hai trong số đó (`post.mark_source_deleted`) là cùng lớp lỗi `F-A2R1-01` xuất hiện lần thứ ba
   — một operation đã bị bác vẫn được gọi tên trong hợp đồng.
2. **Bản tách làm lộ thêm token mà bản gộp không thấy** (8 mới so với 13 cũ, tập khác nhau). Nghĩa
   là con số "13" của lần trước chưa bao giờ là toàn bộ vấn đề — nó là toàn bộ *phần công cụ khi
   đó nhìn thấy*. Bất kỳ con số vi phạm nào cũng nên đọc như vậy.
3. **`gen_index.py` của tôi vỡ ở id `E0-04c`** (regex chỉ chấp nhận hậu tố `a`/`b`). Lỗi tự lộ ra
   và đã sửa, nhưng nó cho thấy script phụ trợ của tôi không có test của chính nó.
4. Ba bài học self-test ở §K4 đều là về **cách một kiểm tra có thể trông như đã chạy mà không
   chạy**. Đó là lớp lỗi nguy hiểm nhất trong toàn bộ công việc này.
5. B01–B17 vẫn `OPEN`; E1–E4 `NOT_RUN`; A2 chưa xác minh lại;
   `NOT_READY_FOR_PRODUCT_CODE` giữ nguyên. Không finding nào được đóng.

## K8. Trạng thái bàn giao

- **next actor:** `Coordinator` → **A2 (`PKT-A2-R2`)**.
- **lease_released_at (UTC):** 2026-09-07T01:52Z. `LEASE-PC09-e4` nhả tại đây; `worker-W6` không
  ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §K1) và lease fencing ≥ 5.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng.

---

# ADDENDUM — PKT-PC09-FIX4 (đợt FIX8, lần chạy đóng)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09-FIX4` · worker `worker-W6` · lease `LEASE-PC09-e5` (fencing 5) |
| authority_id | `AUTH-COORD-PC09-FIX4` (parent `AUTH-OWNER-20260906-01`) |
| status | **`DONE`** · completion_claim `DRAFT_FOR_REVIEW` |
| audit_route | `INDEPENDENT_REQUIRED` — **`PKT-A2-R2` là lượt xác minh đang chờ trên chính epoch này** |

## L1. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `evidence/index.json` | MODIFY | `3101ef97…07ec1` (195459) | `aea081a32056d68191151ca44a854d1ef080a24c3cc5f4fdf0a0030473e77c3b` (194774) |
| `evidence/tools/README.md` | MODIFY | `a57b339f…e8246` (19671) | `d8cf7e3cd9fc4c105411b6881b2d07a613f5df72922a03951648e268deef76f9` (22089) |
| `precode/gates.yaml` | MODIFY | `b949559c…6c734` (31998) | `1bc64527c527c2a6db4b20ef3fd27d6ee404510f2ceb649447be93f2c52fbd00` (31552) |
| `precode/review.md` | MODIFY | `4ef032cb…9bbab` (94795) | `095c392b883376ecb73cbc343b6bc16dd5d108d00371bf458eb312a46060ffd8` (95916) |
| `evidence/runs/E0-20260907T015929Z.json` | CREATE | ABSENT | `a94aed6fdf7b51e9722644269ba0030c9365d7aeb8ddb56ae84dd05086167183` (39610) |
| `evidence/handoffs/PC09-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* | — |

**Không đổi ở đợt này:** `acceptance/scenarios.yaml` (`c831a695…54831b`),
`acceptance/traceability.csv` (`cef95b2f…2bf94`, sinh lại cho ra byte giống hệt),
`evidence/tools/e0_check.py` (`3dcac5f4…3693c`), `evidence/manifest.schema.json`. Công cụ **không
bị chạm**: 8 vi phạm cuối được đóng bằng cách các gói sở hữu sửa nội dung, không bằng cách tôi nới
check. Nguồn pinned khớp cả hai lần kiểm; không `__pycache__`, không git mutation, không mạng.

## L2. Cổng chờ

Poll `evidence/handoffs/PC10-handoff.md` cho **PKT-PC10-FIX5**: mở sau ~3 phút. Card epoch nay là
`PC10-PIN-FCW4e-20260907`, đọc từ card bằng lệnh `grep` ghi trong `review.md` §9.1 — **18/18 đồng
nhất**. Đã đọc addenda FIX8 của W2 (PC08-FIX3), W3 (PC02-FIX8, PC07-FIX4) và W4 (PC03-FIX5,
PC05-FIX5).

## L3. Kết quả E0 — **22/22 PASS, 0 vi phạm, exit code 0**

Run `evidence/runs/E0-20260907T015929Z.json`. Ba check prose sạch: `E0-04b` 284 kiểm / 0 ·
`E0-04c` **215** kiểm / **0** (trước: 208 / 8) · `E0-04d` 154 / 0.

Cả 8 vi phạm cuối (`CR-PC09-12`) đã được đóng bởi các gói sở hữu: `coverage_window.predecessor` →
`predecessor_window_id` (W4, hai file state) · `post.mark_source_deleted` gỡ khỏi `openapi.yaml`
và `ingest-batch.schema.json` (W2/W3) · ba `*.does_not_guarantee` viết lại (W2) ·
`telegram_link_code.format_match_attempt_count` gỡ khỏi README (W3).

Điều đáng ghi về **cách** cả ba đợt kết thúc: FAIL của FIX6 (13), FIX7 (8) và FIX8 (0) đều được
đóng bằng cách **sửa nội dung hợp đồng**, không lần nào bằng cách nới một check. `e0_check.py`
không đổi một byte ở đợt này.

## L4. `CR-PC07-10` — ghi lại, KHÔNG thực hiện

W3 nêu một phản biện đúng: gate coi **mọi** token `a.b` là một khẳng định về operation hoặc cột,
nên một phần các sửa đổi ở FIX7/FIX8 là **thích nghi với hình dạng của gate**, không phải sửa nội
dung sai. Đề xuất: namespace được khai báo (`schema:`, `api:`, `§`) để nói rõ ý định thay vì né
dấu chấm.

Đánh đổi đầy đủ ở `evidence/tools/README.md` §5c. Tóm tắt: **được** — ý định tường minh, hết false
positive cho tham chiếu ngoài hợp đồng, và một tham chiếu tới API ngoài (Telegram) trở nên kiểm
được thay vì bị bỏ qua; **mất** — phải sửa toàn bộ prose hiện có một lần nữa, thêm một quy ước mọi
người phải nhớ, và prefix sai/thiếu trở thành một lớp lỗi **mới** cần gate riêng.

**Không làm bây giờ** vì nó chạm mọi file hợp đồng, ngay trước freeze, để đổi *cách diễn đạt* chứ
không phải sửa một khiếm khuyết đang tồn tại — ba check hiện 0 vi phạm. Thời điểm đúng là **sau**
khi A2 xác minh epoch này, kèm một lần rà toàn corpus. Ghi ở đây để "chưa làm" là một quyết định
có lý do, không phải một chỗ bị bỏ sót.

## L5. Số liệu (đều do `derive_numbers.py` / `crtable.py` sinh; cổng tự kiểm: CONSISTENT)

246 dòng traceability · `COVERED` 90 · `PARTIAL` 60 · `BLOCKED_B*` 84 · **`ORPHAN` 0** ·
`PARTIAL` P0 XN/UQ 37 · 56 scenario, 0 thiếu fixture · 86 fixture / 9 thư mục · 67 transition ·
85 operation · 36 cạnh cấm ↔ 36 denied case ↔ 36 sự kiện quét · 60 entity · 28 mã lỗi ·
17/17 invariant có cực dương **và** cực âm chuyên dụng · module 9 READY / 16 BLOCKED / 5 chặn cứng
· DoR 8 ✅ / 2 ⚠️ / 2 ❌ · **107 CR** (90 PC00–PC08, 12 PC09, 5 PC10; OPEN 63 · RULED 23 ·
CLOSED_CLAIMED 19 · APPROVED 1 · ACCEPTED_AS_LIMITATION 1).

`evidence/index.json`: **58 bản ghi, 58/58 validate**; 32 placeholder `NOT_RUN` cho E1–E4.

## L6. Trạng thái cổng

G0 · G1 · G2 `MET_PROVISIONAL` · G3 `PARTIALLY_MET` · **G4 `PARTIALLY_MET`** (G4-X5 nay **đạt**;
còn G4-X6 Owner phê chuẩn B01–B17, và G4-X7 A2 xác minh) · G5 · SP1 `NOT_MET` · G6 · G7
`NOT_APPLICABLE_YET`.

## L7. Mối lo còn lại

1. **`PKT-A2-R2` chưa chạy trên epoch này.** A2 chưa kiểm lại **bất kỳ** bản sửa nào của FIX6,
   FIX7 hay FIX8 — gồm 11 finding của chính A2-R1, ba check prose mới, và toàn bộ thay đổi nội
   dung đưa `E0-04c` về 0. "22/22 PASS" là con số của **phía sửa, chạy bằng công cụ do phía sửa
   viết**; nó là bằng chứng cần được kiểm, không phải một verdict.
2. **0 vi phạm nghĩa là "không còn gì mà 22 check này nhìn thấy".** Mỗi lần bộ check được mở rộng
   (19 → 20 → 22) nó lại tìm ra lỗi thật đã nằm sẵn ở đó. Không có lý do để tin lần mở rộng tiếp
   theo sẽ khác.
3. **`CR-PC07-10` còn OPEN** và là món nợ kỹ thuật đã biết: một phần prose hiện tại được viết cho
   hình dạng của gate.
4. B01–B17 vẫn `OPEN`; E1–E4 `NOT_RUN` ở cả 56 scenario; hai module chặn cứng vì `KC` cần mạng;
   `NOT_READY_FOR_PRODUCT_CODE` giữ nguyên. Không finding nào được đóng, không quyết định nào được
   phê chuẩn ở gói này.

## L8. Trạng thái bàn giao

- **next actor:** `Coordinator` → **A2 (`PKT-A2-R2`)** trên epoch này.
- **lease_released_at (UTC):** 2026-09-07T02:04Z. `LEASE-PC09-e5` nhả tại đây; `worker-W6` không
  ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §L1) và lease fencing ≥ 6.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng.

---

# ADDENDUM — PKT-PC09-FIX5 (đợt FIX9, sau A2-R2)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09-FIX5` · worker `worker-W6` · lease `LEASE-PC09-e6` (fencing 6) |
| authority_id | `AUTH-COORD-PC09-FIX5` (parent `AUTH-OWNER-20260906-01`) |
| status | **`DONE`** · completion_claim `DRAFT_FOR_REVIEW` |
| audit_route | `INDEPENDENT_REQUIRED` — A2-R2 **PASS tổng thể**; bốn finding LOW mới đã sửa ở đợt này và **chưa ai xác minh** |

## M1. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/review.md` | MODIFY | `095c392b…0ffd8` (95916) | `b8e833f02a650c415f7d5e5ac181216455c0f8d2d7a8560d088dfd9d5dd12a41` (99604) |
| `precode/gates.yaml` | MODIFY | `1bc64527…fbd00` (31552) | `8b88a12ba8d06d8ea408658b8d1bd24de85cb92626ca1c4d7584ea6badf32e28` (31862) |
| `evidence/index.json` | MODIFY | `aea081a3…77c3b` (194774) | `22da200cf01662798c08edb4c0615b7c70f6fecb6cec6256e86688e650a9c2e8` (195576) |
| `evidence/tools/e0_check.py` | MODIFY | `3dcac5f4…3693c` (102459) | `9f5605686fce036ced12c591a2d081df50bb75ebc61890600f0e5a41e2d43e43` (103024) |
| `evidence/tools/README.md` | MODIFY | `d8cf7e3c…f76f9` (22089) | `44c2245093ace05034cec79cb494c04ce4ac3f6a84984408cec89c50b55da3e8` (23394) |
| `evidence/runs/E0-20260907T021812Z.json` | CREATE | ABSENT | `8b8f9ccbd7aaa5759c814f38e7baed7d00f9a18bde650fff3982035348235896` (39265) |
| `evidence/runs/numbers-20260907T021812Z.json` | CREATE | ABSENT | `ac05335249d0663cea0e88948fcf1edb866afd2c2f50e7d59368dfe15d4ec607` (14040) |
| `evidence/runs/cr_summary-20260907T021812Z.json` | CREATE | ABSENT | `b3f651ef3208c53424e72ff3220eb546e18240b38e2fdfe6d73a4f1b7cb234e8` (2091) |
| `evidence/handoffs/PC09-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* | — |

`acceptance/scenarios.yaml` và `acceptance/traceability.csv` **không đổi** ở đợt này. Nguồn pinned
khớp cả hai lần kiểm; không `__pycache__`, không git mutation, không mạng.

## M2. Cổng chờ

Poll `evidence/handoffs/PC01-handoff.md` cho **PKT-PC01-FIX12**: mở trước lần chạy đóng. W2 đã bổ
sung `event_type` cho cả sáu case `operation: null` (NC-08, NC-12, NC-15, NC-22, NC-24, NC-28).

## M3. Bốn finding của A2-R2

| Finding | Đã làm |
| --- | --- |
| **F-A2R2-01** ba câu cũ mâu thuẫn với chính file | DoR dòng 11 nay đọc epoch từ card (`card_pin_current`, **cùng nguồn** với §9.1); §9 điều kiện (d) nêu đúng lý do thật (bốn finding LOW chưa xác minh, không phải "A2 chưa chạy"); §13 mục 9 đếm số report từ đĩa (`audit_reports` = 5). **Ràng buộc gốc được thực hiện đúng tinh thần:** trạng thái audit nay được phát biểu ở **một chỗ duy nhất** — §4.1 — và mọi mục khác trỏ về đó. Kỷ luật `numbers.json` áp cho *trạng thái*, không chỉ *số* |
| **F-A2R2-02** DoR dòng 5 nói ít hơn artefact | Dòng 5 quay lại **✅**, và danh sách ngoại lệ nay **sinh từ `ports.yaml`** (khóa `dor5`): 0 operation thiếu `scenario_refs`, 0 thiếu `error_codes`, 0 mutation thiếu khai báo idempotency. Một lỗ hổng được vá nay **tự đóng dòng** |
| **F-A2R2-03** artefact provenance nằm ngoài candidate | `numbers.json` và `cr_summary.json` được sao vào `evidence/runs/` kèm dấu thời gian của lần chạy, **đăng ký làm artefact của `EV-PC09-01`**, và `review.md` trích chúng **theo đường dẫn** |
| **F-A2R2-04** quy tắc null-operation ghi thành note | `E0-10b` nay coi đó là **violation**. Đây là điểm quan trọng nhất trong bốn: một note là thứ **không ai phải làm gì với nó**, nên một quy tắc chỉ được canh bằng note thì thực tế không được canh |

## M4. Kết quả E0 — **22/22 PASS, 0 vi phạm, exit 0**

Run `evidence/runs/E0-20260907T021812Z.json`. **Không còn note nào thuộc lớp "vi phạm quy tắc ghi
thành note"** — 12 note còn lại đều là đo lường hoặc ngữ cảnh có chủ đích: bảng theo thư mục của
`E0-15`, hai deviation đã khai, hai fixture `expected_validation: not_applicable`, và dòng đếm
song ánh của `E0-10b`.

Quy tắc mới đã được viết vào `evidence/tools/README.md` §7 mục 2: **đừng ghi một vi phạm quy tắc
thành note.** Note là để đo lường và ngữ cảnh; nếu một quy tắc trong hợp đồng nói "phải", cửa kiểm
trích quy tắc đó phải `fail`.

## M5. Cổng tự kiểm bắt được lỗi của chính tôi, lần nữa

Khi tôi chuyển DoR dòng 5 từ ⚠️ về ✅ theo `F-A2R2-02`, tôi **quên dòng tổng** bên dưới bảng. Cổng
tự kiểm so dòng tổng với bảng báo `MISMATCH` (review 8/2/2, derived 9/1/2) và tôi sửa. Con số đó
đã đi 7/3/2 → 10/0/2 (sai, `F-A2R1-02`) → 8/2/2 → **9/1/2**, và mỗi lần đổi là vì một dòng của
bảng đổi. Ghi lại vì nó cho thấy đúng thứ mà `F-A2R1-02` tồn tại để chặn vẫn tái diễn khi con số
được sửa bằng tay — cổng chạy sau mỗi lần sửa là thứ duy nhất bắt được nó.

## M6. Số liệu (sinh; artefact nay nằm trong candidate)

246 dòng traceability · `COVERED` 90 · `PARTIAL` 60 · `ORPHAN` **0** · 56 scenario, 0 thiếu
fixture · 86 fixture / 9 thư mục · 85 operation (**0** thiếu `scenario_refs`, **0** thiếu
`error_codes`) · 36 cạnh cấm ↔ 36 denied case ↔ 36 sự kiện quét · 17/17 invariant có cả hai cực
chuyên dụng · module 9 READY / 16 BLOCKED / 5 chặn cứng · **DoR 9 ✅ / 1 ⚠️ / 2 ❌** · **107 CR** ·
index **58 bản ghi, 58/58 validate**. Card epoch tại thời điểm chạy: **`PC10-PIN-FCW4e-20260907`**
(18/18) — **W7 sẽ re-pin sau gói này**, nên lệnh `grep` trong §9.1 luôn là nguồn đúng, không phải
giá trị đã in.

## M7. Mối lo còn lại

1. **Bốn bản sửa của đợt này chưa được ai xác minh.** A2-R2 PASS tổng thể nhưng để lại chính bốn
   finding này; người viết bản sửa không được là người xác minh (protocol §8).
2. **`CR-PC07-10` còn OPEN** — một phần prose hiện tại được viết cho hình dạng của gate, không
   phải ngược lại. Đánh đổi ở `tools/README.md` §5c; nên làm sau freeze.
3. **`E0-06`/`E0-07` vẫn không quét văn xuôi trong `evidence/handoffs/`** (A2-R2 §7 mục 15).
4. **41 trên 86 fixture nằm ngoài tầm với của cửa kiểm cột**, khai đủ theo từng thư mục;
   `CR-PC02-18` `ACCEPTED_AS_LIMITATION`.
5. B01–B17 vẫn `OPEN`; E1–E4 `NOT_RUN` ở cả 56 scenario; hai module chặn cứng vì `KC` cần mạng;
   `NOT_READY_FOR_PRODUCT_CODE` giữ nguyên.

## M8. Trạng thái bàn giao

- **next actor:** `Coordinator` → W7 (re-pin card) → A2 nếu Coordinator muốn xác minh bốn bản sửa.
- **lease_released_at (UTC):** 2026-09-07T02:26Z. `LEASE-PC09-e6` nhả tại đây; `worker-W6` không
  ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §M1) và lease fencing ≥ 7.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng.

---

# ADDENDUM — PKT-PC09-FIX6 (đợt FIX10, sau A2-R3)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC09-FIX6` · worker `worker-W6` · lease `LEASE-PC09-e7` (fencing 7) |
| authority_id | `AUTH-COORD-PC09-FIX6` (parent `AUTH-OWNER-20260906-01`) |
| status | **`DONE`** · completion_claim `DRAFT_FOR_REVIEW` |

## N1. Changes

| Path | Op | Before sha256 (bytes) | After sha256 (bytes) |
| --- | --- | --- | --- |
| `precode/review.md` | MODIFY | `b8e833f0…12a41` (99604) | `db747393f184b2ef4d40e5956cee7648201aadee6197c517797065c19f72e061` (101710) |
| `evidence/tools/README.md` | MODIFY | `44c22450…da3e8` (23394) | `fef1544bd03a2bd249fab6792a36a7c861b4c2c9420c37028d5240e7b11788cf` (25976) |
| `evidence/index.json` | MODIFY | `22da200c…9c2e8` (195576) | `37f451ccce3427a79a64627dc6507fbbb2fb3f7488cab128a32ed80118cc06ca` (195576) |
| `evidence/runs/E0-20260907T023000Z.json` | CREATE | ABSENT | `11cf8db96cd8ad28f819de883f8edc83b850e2e6d6d2b616716e382bbb7849cb` (39265) |
| `evidence/runs/numbers-20260907T023000Z.json` | CREATE | ABSENT | `9383037b72eb429a283ad6fd32ea933dd5790fc1d05b20a3117b919dcf7a75db` (14209) |
| `evidence/runs/cr_summary-20260907T023000Z.json` | CREATE | ABSENT | `b3f651ef3208c53424e72ff3220eb546e18240b38e2fdfe6d73a4f1b7cb234e8` (2091) |
| `evidence/handoffs/PC09-handoff.md` | APPEND | *(file này — Coordinator rehash độc lập)* | — |

Ba file `evidence/runs/` của epoch trước được thay bằng bộ mới cùng dấu thời gian (`numbers.json`
đổi ⇒ đăng ký một lần chạy mới, theo packet). `precode/gates.yaml`, `acceptance/*`,
`evidence/tools/e0_check.py` **không đổi**. Nguồn pinned khớp cả hai lần kiểm.

## N2. Ba finding của A2-R3

**`F-A2R3-01` — DoR dòng 11 in một epoch cũ trong khi tự khai là "đọc từ card".** Đây là finding
đáng chú ý nhất trong ba, và A2 nói đúng về lý do: một **khẳng định provenance sai mạnh hơn một
giá trị cũ trần, vì nó bảo người đọc đừng kiểm**. Dòng đó đã sai ở ba epoch liên tiếp
(`FCW4c` → `FCW4e` → và sẽ lại sai ở `FCW4f`) chính vì mỗi lần tôi sửa nó bằng cách in một giá trị
mới thay vì bỏ hẳn việc in.

Bản sửa không phải là in `FCW4f`: **dòng 11 nay không nhắc lại tên epoch nữa**. Nó nói "18 card
đều pin cùng một epoch — tên epoch được in ở §9.1 và chỉ ở đó". Một sự thật, một nguồn, in một
lần. Đó là cùng quy tắc mà `numbers.json` áp cho *số* và §4.1 áp cho *trạng thái audit*.

**`F-A2R3-02` — lệnh được công bố làm nguồn trả bảy tên, không phải một.** Dòng pin của mỗi card
nêu cả epoch hiện hành lẫn mọi epoch đã bị thay, nên `grep -ho "PC10-PIN-[A-Za-z0-9-]*"` trả
`PC10-PIN-20260907`, `FCW4`, `FCW4b`, `FCW4c`, `FCW4d`, `FCW4e`, `FCW4f`. Bộ sinh dùng một quy tắc
chặt hơn, và **hai quy tắc tách nhau ra** — đúng lớp lỗi của `F-A2R3-01` ở một tầng khác.

Lệnh công bố nay là chính quy tắc bộ sinh áp dụng, và tôi đã **chạy nó để kiểm** trước khi in:

```
sed -n 's/^\*\*Pin epoch: `\([A-Za-z0-9-]*\)`.*/\1/p' agent-tasks/TC-*.md | sort -u
```

trả đúng một giá trị, `PC10-PIN-FCW4f-20260907`, từ 18/18 card. Quy tắc — epoch hiện hành là token
trong cặp backtick **đầu tiên** của dòng bắt đầu bằng `**Pin epoch: ` — nay ở cả `review.md` §9.1,
`evidence/tools/README.md` §5d và khóa `card_pin_command` của bộ sinh.

**`F-A2R3-03` — chuỗi định dạng chưa được thay thế ở câu mở đầu §4.1.** Đã render từ
`audit_reports`. A2 nêu đúng điều đáng học: **một dòng "được sinh" mà vẫn ship kèm placeholder thì
chưa thật sự được sinh** — bước thay thế chưa bao giờ được chạy, và không có gì phát hiện điều đó.

Nhân đây sửa một sai số của chính câu đó: nay có **6** AUDIT_REPORT (A1-R1, A1-R2, A1-R3, A2-R1,
A2-R2, A2-R3), không phải 5 — con số đến từ `audit_reports_count`, đếm từ đĩa, nên nó tự đúng ở
lần audit sau.

## N3. Cổng tự kiểm nay có tám kiểm, ba trong số đó được thêm sau khi bắt được lỗi thật

`gate.py` chạy sau **mỗi** lần sửa `review.md`:

| # | Kiểm | Kết quả |
| --- | --- | --- |
| 1–4 | Bốn dòng tổng khớp bảng của chính chúng (DoR, module, hai dòng E0) | OK |
| 5 | Số AUDIT_REPORT khớp `audit_reports_count` | OK — 6 |
| 6 | **Lệnh pin công bố được CHẠY** và trả đúng một giá trị bằng `card_pin_current` | OK — `PC10-PIN-FCW4f-20260907` |
| 7 | **Không còn placeholder định dạng chưa thay** ở bất kỳ đâu trong file | OK — **0** |
| 8 | **Không có tên epoch cũ nào** ngoài dòng lịch sử đã khai | OK — 0 |

Kiểm 6, 7 và 8 là mới ở đợt này, mỗi cái thêm vào sau khi một finding chứng minh nó cần thiết. Đó
là mẫu hình chung của toàn bộ gói này: mỗi lần một điều đúng chỉ được viết bằng chữ, nó lại lệch;
mỗi lần nó được biến thành một phép kiểm chạy được, nó thôi lệch.

## N4. Kết quả

E0 `evidence/runs/E0-20260907T023000Z.json`: **22/22 PASS, 0 vi phạm, exit 0** (không đổi so với
epoch trước — `e0_check.py` không bị chạm ở đợt này). Cổng tự kiểm: **CONSISTENT**, 8/8.
`evidence/index.json`: 58 bản ghi, 58/58 validate; ba artefact `evidence/runs/` mới được đăng ký
làm artefact của `EV-PC09-01`.

## N5. Mối lo còn lại

1. **Ba bản sửa của đợt này chưa được xác minh** (protocol §8).
2. **Chu kỳ re-pin vs. re-generate vẫn chưa có thứ tự bắt buộc.** `review.md` §9.1 in một giá trị
   tại thời điểm chạy; nếu W7 re-pin **sau** khi tôi sinh, giá trị in lại cũ ngay — đúng cách
   `F-A2R3-01` phát sinh ba lần. Bản sửa của tôi thu hẹp thiệt hại (chỉ còn **một** chỗ in, và
   lệnh bên cạnh luôn đúng), nhưng **không** loại bỏ nguyên nhân. Cần một ruling về thứ tự: hoặc
   re-pin luôn đứng trước lần sinh cuối, hoặc `review.md` không in giá trị mà chỉ in lệnh.
3. `CR-PC07-10` còn OPEN; `E0-06`/`E0-07` vẫn không quét văn xuôi trong `evidence/handoffs/`;
   41/86 fixture ngoài tầm cửa kiểm cột (`CR-PC02-18` ACCEPTED_AS_LIMITATION).
4. B01–B17 `OPEN`; E1–E4 `NOT_RUN`; `NOT_READY_FOR_PRODUCT_CODE` giữ nguyên.

## N6. Trạng thái bàn giao

- **next actor:** `Coordinator`. Đề nghị một ruling cho mục N5.2 (thứ tự re-pin ↔ re-generate).
- **lease_released_at (UTC):** 2026-09-07T02:34Z. `LEASE-PC09-e7` nhả tại đây; `worker-W6` không
  ghi thêm file nào. Sửa tiếp cần packet mới, baseline mới (hash ở §N1) và lease fencing ≥ 8.
- **Claim:** `DRAFT_FOR_REVIEW`, không nâng.
