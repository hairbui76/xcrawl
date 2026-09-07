---
card_id: TC-x-feasibility-probe
title_vi: SP1 — Probe khả thi collector X (chỉ probe, đầu ra là bằng chứng)
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M0
gate: SP1
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: LIVE_FEASIBILITY_VERIFIED — và chỉ trong điều kiện đã ghi. Không suy ra 'X sẽ không bao giờ chặn', không suy ra collector đã hoạt động, không suy ra AC-01/AC-04 đã pass.
owner_modules: [MOD-x-collector]
scenario_refs: [SC01, SC03, SC04, SC49]
invariant_refs: [I10]
evidence_manifest_id: EVM-TC-x-feasibility-probe
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-x-feasibility-probe — SP1 — Probe khả thi collector X (chỉ probe, đầu ra là bằng chứng)

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
| `contracts/ops/collector-probe.md` | `03e88010ce8d9a8e7ed7afbb5ab01caf4099ac77cde1298fb155731dddd55ca1` | 26780 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/ops/secrets.md` | `2ed96d93ecdbb74fd825e952abd85541ddecfe25cfd1c08efd739d708c165d48` | 24387 |
| `contracts/ops/deployment.md` | `7e1c03776b4c8be20f596a0317ea1c79429cf4ecaa78fadc1f0ec3e5158088f5` | 17759 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `277eb556cff950193ca55cecd0ef0d06dca279a4d376c5c8e889a48ebf60c09c` | 5717 |
| `acceptance/fixtures/collection/README.md` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 12636 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-x-feasibility-probe`
- **Milestone:** M0 (SRC-SPEC §13) · **Cổng:** SP1 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-x-collector`

**Mục tiêu.** Chạy 5–10 đợt đọc X bằng Chrome profile riêng của dự án, ghi số bài lấy được và số lần bị đòi xác minh ra file, **không** DB, **không** AI. Đầu ra của card này là **bằng chứng**, không phải tính năng.

**Non-goals.**

- **Không viết product code.** Không tạo bảng, không gọi backend API, không ingest.
- Không tối ưu, không mở rộng phạm vi thu thập.
- Không kết luận 'collector đã hoạt động' — probe chỉ nói về điều kiện đã ghi.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0001-topology-and-placement.md`.
3. Hợp đồng nghiệp vụ: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/ops/deployment.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `probe/x_feasibility/run_probe.py` | kịch bản probe theo `collector-probe.md` §3 và §5 |
| `probe/x_feasibility/record.py` | ghi biểu mẫu mỗi đợt theo §5 |
| `evidence/runs/SP1-x-feasibility/` | thư mục kết quả: log đã che danh tính, biểu mẫu mỗi đợt, manifest |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces:** không operation nào. Card này là **caller**, không sở hữu operation trong `contracts/ports.yaml`.

**Consumes:** không operation nào của hệ thống.

**Schema:**

- biểu mẫu ghi nhận mỗi đợt → `contracts/ops/collector-probe.md`

**State effects.** **Không** chạm state nào của hệ thống. Không DB, không outbox, không job.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được phép gọi:**

- Chrome profile riêng của dự án trên máy cá nhân (D09)

**Đường bị cấm (denied paths):**

- Không thêm bất kỳ cơ chế nào để né CAPTCHA hoặc che giấu danh tính — **không thương lượng** (SRC-SPEC §13.2, `collector-probe.md` §2).
- Không đổi account, không proxy, không tự động hóa xác minh.
- Không gọi backend API, không ghi SQLite, không gọi AI, không gửi Telegram.
- Không chuyển sang X API trả phí nếu probe thất bại — đó là quyết định của Owner (SRC-PLAN §12).

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
| `I10` | CAPTCHA không tự retry/resume — áp dụng cả trong probe |

**Transaction và commit point:**

- Không có transaction.

**Race, replay và forbidden effects:**

- Không áp dụng.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `X_CHALLENGE_REQUIRED` | dừng đợt, ghi nhận, chờ người; **không** tự tiếp tục |
| `X_ACCESS_BLOCKED` | dừng hẳn probe và báo Owner |
| `SOURCE_LAYOUT_CHANGED` | ghi nhận và dừng; không đoán selector |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC01
- SC03
- SC04
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python probe/x_feasibility/run_probe.py --runs 5` (PROVISIONAL, chỉ sau cổng §6 của `collector-probe.md`)
- Không có lệnh test tự động: đầu ra là biểu mẫu và log, được review thủ công

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Tiêu chí go/no-go ở `contracts/ops/collector-probe.md` §7 — áp dụng nguyên văn, không nới.
- Mỗi đợt có đủ trường ở §5: thời điểm, số bài, số lần bị đòi xác minh, lý do dừng, giới hạn quan sát.
- Log không chứa cookie, token hay danh tính tài khoản.
- Nếu no-go ⇒ báo **blocked cho nguồn X**, không tự chuyển phương án.

**Evidence artifacts:** `evidence/runs/SP1-x-feasibility/` với biểu mẫu mỗi đợt; log đã che danh tính; manifest theo `evidence/manifest.schema.json` (pending PC09).

**Yêu cầu live.** Đây **là** card live. Không có bằng chứng thay thế bằng fixture.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `LIVE_FEASIBILITY_VERIFIED — và chỉ trong điều kiện đã ghi. Không suy ra 'X sẽ không bao giờ chặn', không suy ra collector đã hoạt động, không suy ra AC-01/AC-04 đã pass.`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | **Chưa chạy.** `contracts/ops/collector-probe.md` §0 ghi trạng thái bằng chứng NOT_RUN. REQ-OQ01 (xác nhận D09 — Chrome profile riêng của dự án thay cho profile mặc định) **chặn M0** và là câu hỏi Owner phải trả lời. |
| `SG-02` | Chưa đủ bốn xác nhận của Owner ở `collector-probe.md` §6 ⇒ trạng thái `OWNER_DECISION_REQUIRED` và probe **không được chạy**. Đây là stop tuyệt đối. |
| `SG-03` | Bị chặn thì **dừng và báo**. Mọi hành vi né tránh làm card này FAIL ngay lập tức, bất kể kết quả thu được. |
| `SG-04` | Giới hạn nhịp gọi và yêu cầu định danh của arXiv/OpenAlex vẫn `KC` (`collector-probe.md` §9.2; `CR-PC05-03`: **không nguồn đã pin nào chứa URL tài liệu**). Probe này không chạm connector nghiên cứu; nếu packet mở rộng sang đó ⇒ DỪNG. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- Không phụ thuộc card nào. **Là dependency của `TC-collector-checkpoint-resume` cho mọi khẳng định live.**

## §12. Reviewer scope

Reviewer đọc `contracts/ops/collector-probe.md` toàn bộ (đặc biệt §2, §6, §7, §10) và biểu mẫu kết quả. Câu hỏi bắt buộc: có hành vi né tránh nào không, và kết luận có vượt quá điều kiện đã ghi không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-x-feasibility-probe`
- **Vị trí:** `evidence/runs/TC-x-feasibility-probe/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
