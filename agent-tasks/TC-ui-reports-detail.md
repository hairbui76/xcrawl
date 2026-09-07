---
card_id: TC-ui-reports-detail
title_vi: UI Reports và Report detail: cùng revision phân tích, có provenance
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED cho read model và nhãn provenance. Chất lượng nội dung là E4.
owner_modules: [MOD-web-ui]
scenario_refs: [SC09, SC10, SC11, SC15, SC49]
invariant_refs: [I04, I05, I07, I13]
evidence_manifest_id: EVM-TC-ui-reports-detail
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-ui-reports-detail — UI Reports và Report detail: cùng revision phân tích, có provenance

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. Stack (Option A / Python) là **PROVISIONAL** theo `precode/adr/ADR-0006-stack-option-a.md`; mọi đường dẫn ở §3 và mọi lệnh ở §8 có điều kiện *"nếu ADR-0006 được chấp nhận"*.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-FCW4f-20260907`** (thay `PC10-PIN-FCW4e-20260907`; các epoch cũ hơn: `PC10-PIN-FCW4d-20260907`, `PC10-PIN-FCW4c-20260907`, `PC10-PIN-FCW4b-20260907`, `PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). Hash dưới đây được **tính lại trực tiếp trên repo**; thay đổi duy nhất so với `FCW4e` là `contracts/modules.yaml` (năm denied case thêm `event_type`; không oracle nào của card bị ảnh hưởng). **Card là nguồn chuẩn của tên epoch**; mọi file khác khẳng định pin hiện hành phải đọc tên từ đây, không chép tay (finding `F-A2R1-03`). Trước khi bắt đầu, chạy `sha256sum` trên **mọi** dòng dưới đây. Lệch một dòng ⇒ card `STALE`, DỪNG (`precode/change-control.md` §5, quy tắc `INV-06`/`INV-09` của `precode/gates.yaml`).

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/baseline.json` | `e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` | 97620 |
| `precode/decision-register.md` | `212441a429420d1cc11cdc4a9c79a11648e45e1b92278a08f77a9779943ad15d` | 97899 |
| `contracts/modules.yaml` | `11af00fd97a03d5357fc1a72d0e4e61293164f449c3a50e700c03a202e1166c7` | 105642 |
| `contracts/capabilities.yaml` | `fae5891cff5ff25757f168d8182111fa4fc6b49f6b851ac7cc07105fef952cf7` | 45672 |
| `contracts/ports.yaml` | `93ba159856a4821ad46d1d05199987f475c8ae5603d8f9200e1418b0e2eab42e` | 126182 |
| `contracts/errors.yaml` | `b63eef7abd4cee328581e5e06cbc8314e60e52e03468dbe6acea42a0a843ad26` | 62269 |
| `contracts/retry-policy.yaml` | `5e083230e2cc5db481736adcf189a6cf8e302ebdf45cad614582731698cf06d5` | 41620 |
| `contracts/data/entities.yaml` | `c2ceeafd1b78705941f368bfe73f67cf097ffad8179c7455b2d4eeda571b5a1e` | 221041 |
| `contracts/ui/screens.yaml` | `db78678cba7e46b33669596f02963e1eac5e65804c6f9a997bf22d72ba6bc296` | 47481 |
| `contracts/schemas/report.schema.json` | `a7c7255a5bae703b0bdcd1ba761153dbce686b5766b05dfbaa1606392338d07b` | 31129 |
| `contracts/ai/grounding.md` | `b54cec8b3f9f6a9cb2221daaafe8a61a149d0a6686d0d23dcbf7bf9f17995172` | 15293 |
| `contracts/reporting/selection.md` | `cc62af2bd476c51efa9b156bae66be6dae3a0bcd712eb79cd1d4ba3a3d5c2fc0` | 34622 |
| `contracts/telegram/delivery.md` | `cb3a4b30a26f2a5ca5cf9d11359b84ce5612c003dfe51c3acbdbba5d7fde226c` | 16807 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | `c08f8670b19e8a0758062988570701ccb96f6d4beefac7b4d80ed6906b95c5f1` | 5228 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `64c0793eeca31b6ac0606813adac96fa483e01eb4b81eaef950edfff16fd3194` | 5459 |
| `acceptance/fixtures/reporting/README.md` | `2c7974e82c4f7ac6e2554050cc1ffda79bfd926faef2c01ed0d4070b8cc45663` | 14516 |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | `0d4d98c87000e19c886fc65748d101f07df79b4e2711f805726c18cc78fbce96` | 8955 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | `e2de531e3b5bbad92946b4f6b3ea5f960bbed7afb687df92252391095e24a624` | 14510 |
| `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json` | `dc1defe222b82dfae97582216d2251fb35663ff177822b388334789a30c9ddea` | 5694 |
| `acceptance/fixtures/ai/d-schema-valid-but-uncited.json` | `cf4662a1713d11fd4c60698cc416b0637bd1cfbfb35dce3a86b298e26c52bcbe` | 6158 |
| `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json` | `7b588ca0ad1999bacdfa78ffb17ba6f0ad1336e399cb291502397f079168079b` | 7475 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/ui/README.md` | `c7ac5d304c33ff48228f5256ac2e56e097eb20121a6648ee4cca431041670dce` | 6380 |
| `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json` | `5b6e4f52b7558533b0555362fd38cad17ea23bb2349fe6600d08d311b9c5b8d8` | 10455 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-ui-reports-detail`
- **Milestone:** M4 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-web-ui`

**Mục tiêu.** Reports, Report detail và Work detail hiển thị đúng revision phân tích mà Telegram digest dùng, tách `author_claim` / `source_verified` / `ai_inference`, hiện `discovered_at` và `analyzed_at`, và đánh dấu reference lịch sử có ngày thay vì phát hiện mới.

**Non-goals.**

- Không viết report builder (card 8).
- Không thêm nút export Saved (hoãn P1).
- Không tự diễn giải kết quả AI thành khẳng định đã kiểm chứng.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0008-analysis-key-and-generation.md`, `precode/adr/ADR-0004-tag-freeze-point.md`.
3. Hợp đồng nghiệp vụ: `contracts/ui/screens.yaml`, `contracts/schemas/report.schema.json`, `contracts/ai/grounding.md`, `contracts/reporting/selection.md`, `contracts/telegram/delivery.md`, `contracts/http/openapi.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json`, `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json`, `acceptance/fixtures/ai/d-schema-valid-but-uncited.json`, `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/web/views/reports.py` | read model `SCR-reports` |
| `server/app/web/views/report_detail.py` | read model `SCR-report-detail` |
| `server/app/web/views/work_detail.py` | read model `SCR-work-detail` |
| `server/app/web/templates/report_detail.html` | nhãn evidence level và provenance |
| `tests/contract/test_report_read_model.py` | cùng revision với payload Telegram |
| `tests/integration/test_provenance_labels.py` | author_claim / source_verified / ai_inference |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces:** không operation nào. Card này là **caller**, không sở hữu operation trong `contracts/ports.yaml`.

**Consumes** (chỉ được gọi đúng những operation này):

- `report.list`
- `report.get`
- `work.get_detail`
- `save.create`
- `save.remove`
- `save.list`
- `analysis.request_reanalysis`

**Schema:**

- report và item → `contracts/schemas/report.schema.json`
- read model → `contracts/ui/screens.yaml`

**State effects.** Chỉ đọc, trừ `save.create`/`save.remove`/`analysis.request_reanalysis` (owner_session + CSRF).

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-report` (abort_reason, selection_version). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được phép gọi:**

- MOD-report-service
- MOD-identity-service
- MOD-saved-service
- MOD-analysis-service

**Đường bị cấm (denied paths):**

- Không truy cập SQLite trực tiếp.
- Không hiển thị `ai_inference` như thể là `source_verified` (B16).
- Không bịa comparator: thiếu ⇒ `comparator: unknown` (B16).

Bảo mật (chốt post-FIX1 trong `contracts/http/openapi.yaml`): `owner_session` cho mutation nghĩa là `ownerSessionCookie` **AND** `ownerCsrfToken` trong **một** security requirement; collector và analysis worker dùng bearer riêng; mọi route `backup.*` chỉ nhận `backupOperatorToken`.

**Ranh giới mã lỗi khi bị từ chối (ruling R5-01, bắt buộc — chọn sai mã là FAIL):**

| Tình huống | Mã |
| --- | --- |
| Request HTTP từ một lớp principal không được phép cho operation đó (ví dụ token collector gọi `save.create`) | `UNAUTHORIZED` (401) |
| Lời gọi/import trong tiến trình đi qua một cạnh **không** có trong `allowed_edges` (ví dụ FE-08 collector → analysis worker, scheduler → Telegram) | `FORBIDDEN_EDGE` |
| Actor thiếu capability tiến trình/mạng/filesystem/tool (adapter mở socket, connector điều khiển Chrome) | `CAPABILITY_DENIED` |
| Mutation dùng phiên owner mà thiếu/sai CSRF token | `CSRF_REJECTED` (403; **không** hủy phiên) |

Mỗi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` có `denied_cases[]` với `expected_error_code` theo bảng trên và `scenario_refs: [SC49]`. Oracle chung: `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §6. Invariants và transaction

| Invariant | Nội dung |
| --- | --- |
| `I04` | analysis hợp lệ bất biến theo generation |
| `I05` | report giữ tag version và evidence references |
| `I07` | reference lịch sử có ngày, không tính là phát hiện mới |
| `I13` | phân biệt thiếu dữ liệu với không có kết quả |

**Transaction và commit point:**

- Không có transaction.

**Race, replay và forbidden effects:**

- Reanalysis chạy trong lúc đang xem ⇒ view hiện generation đang active, có nhãn thời điểm.
- Report đã publish **không** đổi nội dung dù tag đổi sau đó (B01).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `UNAUTHORIZED` | về `SCR-login` |
| `NOT_FOUND` | 404 view |
| `CSRF_REJECTED` | 403, không đăng xuất |
| `STORAGE_WRITE_FAILED` | banner 'chưa lưu được' |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC09
- SC10
- SC11
- SC15
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_report_read_model.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_provenance_labels.py -q` (PROVISIONAL)
- Render review desktop / mobile / Telegram — thủ công, ghi vào evidence manifest

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- AC-10: payload app và payload Telegram cùng `analysis_revision`; so sánh trường-với-trường, không so văn bản.
- AC-11: item chỉ có post ⇒ evidence level `post-only`; mọi claim có provenance; thiếu comparator ⇒ `comparator: unknown`.
- Fixture `h`/`i`: work đã announced hiện là **reference có ngày**, không nằm trong mục phát hiện mới.
- `analyzed_at` và `discovered_at` cùng hiển thị (`CR-PC06-05`).

**Evidence artifacts:** log pytest; diff payload app ↔ Telegram; ảnh chụp render; biên bản human groundedness review.

**Yêu cầu live.** Groundedness review là E4 theo rubric ở `contracts/ai/grounding.md` §6; cần người đánh giá thật.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED cho read model và nhãn provenance. Chất lượng nội dung là E4.`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC06-05` còn OPEN: Settings phải nói rõ đổi provider/model chỉ áp dụng cho phân tích **mới**. Nếu màn hình Settings chưa có câu đó ⇒ raise CR, không tự viết chính sách mới. |
| `SG-02` | `CR-PC04-05` còn OPEN: task `direction_phrasing` chỉ **diễn đạt lại** object đã tính; UI không được để AI chọn thành viên hay đổi nhãn. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-report-coverage-publish-cas`
- `TC-analysis-once-per-generation`
- `TC-saved-snapshot`
- `TC-owner-auth-session`

## §12. Reviewer scope

Reviewer đọc `contracts/ai/grounding.md`, `contracts/schemas/report.schema.json`, `contracts/ui/screens.yaml` ba màn hình. Câu hỏi bắt buộc: người đọc có phân biệt được suy luận của AI với dữ kiện đã kiểm chứng không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-ui-reports-detail`
- **Vị trí:** `evidence/runs/TC-ui-reports-detail/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
