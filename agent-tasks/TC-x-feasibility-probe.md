---
card_id: TC-x-feasibility-probe
title_vi: SP1 — Probe khả thi collector X (chỉ probe, đầu ra là bằng chứng)
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M0
gate: SP1
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
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

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P6-20260909`** (thay `PC10-PIN-P5c-20260909`; các epoch cũ hơn: `PC10-PIN-P5c`, `PC10-PIN-P5b`, `PC10-PIN-P4b`, `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. **`P4`** pin sau `PKT-PC00-FIX30` (`OD-20260908-10`) — lần ghi `precode/` cuối của vòng này. Đợt sửa Giai đoạn 4/6 chạy song song chỉ chạm code, test, handoff và manifest: **không** file nào trong số đó được card pin, nên chúng không tạo ra một lần pin lại. **`P4b`** pin sau `PKT-PC00-FIX32`: `precode/adr/ADR-0011-frameworks-and-toolchain.md` được sửa (phạm vi `mypy`, `CR-PC00-35`). `ADR-0011` nằm trong read set của **mọi** card, nên một mình nó đủ làm cả 19 card `STALE`. Gói song song chỉ chạm bộ file dựng gói (pyproject, uv lockfile), workflow CI, Makefile, .gitignore và một test smoke của server — **không** file nào trong số đó được card pin hay trích dẫn, đã kiểm trực tiếp. **`P5`** pin sau `AMD-ENT-maintenance-01` (`PKT-PC02-FIX16`): `contracts/data/entities.yaml` thêm entity `maintenance_window` và chia lại tập purge (37/22/2), kéo theo `precode/change-control.md` và `precode/decision-register.md`. Thư mục nay có **20 card** — `TC-secret-settings-service` (khoảng trống `G-6`) được thêm ở `PKT-PC10-FIX28`. Tên `P5` **không bao giờ được phát hành**: nó được pin trong lúc đợt propagate của `PKT-PC02-FIX17` còn đang ghi, nên tập byte của nó sai ngay khi vừa ghi xong và bị `P5b` thay trước khi có ai đọc. Ghi lại ở đây để không ai đi tìm một epoch `P5` hợp lệ. **`P5c` (2026-09-09)** pin sau `PKT-PC02-FIX19`: bản `E0-18` siết chặt của W6n bắt hai fixture `acceptance/fixtures/recovery/` vẫn ghi tập purge cũ (20/21) trong khi hợp đồng đã sang 37/22/2; W3n sửa chúng, và fixture **có** pin nên card phải pin lại. Tên epoch mang ngày pin, không phải ngày của thay đổi. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

**`dispatch_status: DISPATCHED (OD-20260907-03, 2026-09-07)`** — Owner đã ra lệnh bắt đầu Giai đoạn 2 (`OD-20260907-03` mục 3): 2A là mốc M0 với hai card `TC-x-feasibility-probe` và `TC-collector-checkpoint-resume`. Dòng này chỉ ghi **trạng thái điều phối** và §1–§13 không đổi vì nó. **Cổng Owner ở `contracts/ops/collector-probe.md` §6 nay đủ cả bốn xác nhận:** mục 1 (D09) ở `OD-20260907-01`, mục 2, 3 và 4 ở `OD-20260907-04` mục 1. Nhưng — theo đúng chữ của §6 — cổng đó **mở về mặt HÀNH CHÍNH, không phải về mặt vận hành**: nó gỡ trạng thái `OWNER_DECISION_REQUIRED` và **không** cho phép bất kỳ Worker, agent hay tiến trình tự động nào chạy probe (`OD-20260907-04` mục 1: *"Không Worker nào được chạy nó."*). Probe chỉ chạy **trên máy của chính Owner**, trên **tài khoản X thật của Owner**, sau khi Owner tự làm các bước ở `evidence/handoffs/TC-x-feasibility-probe-handoff.md` §11. Cổng mở **không** sinh ra bằng chứng: mọi số liệu probe vẫn `NOT_RUN`. Điểm dừng ở §10 vẫn nguyên hiệu lực; quyền thi công đến từ TASK_PACKET, không từ dòng này.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` | 27451 |
| `precode/baseline.json` | `cf59b2c937c334ce21d2cebc7e10dcc84c872f83432fc59d86a1477bd2311875` | 130132 |
| `precode/decision-register.md` | `24e6765f86a88c77ca3efa3af10c600345f3a462ad6abe2d8e06aeceb01eb8c1` | 190995 |
| `contracts/modules.yaml` | `7a4e19bdbb43e1339f305cd4715f1e7ac704b09720408ccf1db48a01b23c1e25` | 108912 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412` | 128872 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `0ec6bc91eccca0588075c385060f8095d640819ce03910f64d1397ef1e4d4c4c` | 256458 |
| `contracts/ops/collector-probe.md` | `9cf2b0185b100d0dc4fc8c69bc6d964c2b3853fb9814852444b56c8cdcbb0b79` | 32713 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/ops/secrets.md` | `22f7a0075ada77c69dfce6b8b7d6e6b0af625317f2fc4c1be726abf5c3c391a5` | 25323 |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` | 19568 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
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
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0001-topology-and-placement.md`.
3. Hợp đồng nghiệp vụ: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/ops/deployment.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `probe/x_feasibility/run_probe.py` | kịch bản probe theo `collector-probe.md` §3 và §5 |
| `probe/x_feasibility/record.py` | ghi biểu mẫu mỗi đợt theo §5 |
| `evidence/runs/SP1-x-feasibility/` | thư mục kết quả: log đã che danh tính, biểu mẫu mỗi đợt, manifest |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

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

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 3 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | **Chưa chạy.** REQ-OQ01 (D09 — Chrome profile riêng của dự án) **đã được Owner trả lời** (`OD-20260907-01` mục 1); quyết định không còn chặn M0. `contracts/ops/collector-probe.md` §0 vẫn ghi bằng chứng **NOT_RUN** — probe là việc phải làm, không phải việc đã làm. |
| `SG-02` | Chưa đủ bốn xác nhận của Owner ở `collector-probe.md` §6 ⇒ trạng thái `OWNER_DECISION_REQUIRED` và probe **không được chạy**. Đây là stop tuyệt đối. |
| `SG-03` | Bị chặn thì **dừng và báo**. Mọi hành vi né tránh làm card này FAIL ngay lập tức, bất kể kết quả thu được. |
| `SG-04` | Giới hạn nhịp gọi và yêu cầu định danh của arXiv/OpenAlex vẫn `KC` (`collector-probe.md` §9.2; `CR-PC05-03`: **không nguồn đã pin nào chứa URL tài liệu**). Probe này không chạm connector nghiên cứu; nếu packet mở rộng sang đó ⇒ DỪNG. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
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
