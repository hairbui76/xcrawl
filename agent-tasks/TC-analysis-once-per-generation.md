---
card_id: TC-analysis-once-per-generation
title_vi: Một kết quả phân tích hợp lệ trên một khóa và một generation
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M3
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-analysis-service]
scenario_refs: [SC06, SC10, SC11, SC17, SC22, SC28, SC49]
invariant_refs: [I04, I16, I14, I10]
evidence_manifest_id: EVM-TC-analysis-once-per-generation
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-analysis-once-per-generation — Một kết quả phân tích hợp lệ trên một khóa và một generation

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-OD01c-20260907`** (thay `PC10-PIN-OD01b-20260907`; các epoch cũ hơn: `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). Bản pin sau wave lan truyền hậu A2-R5 (`FIX-R5-rulings.md`): phạm vi `data.purge_all` đã phê chuẩn được chép nhất quán vào mọi artefact, và hai thư mục fixture `identity/`, `reporting/` lên `CONTRACT_READY`. Hash dưới đây tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG (`precode/change-control.md` §5, `INV-06`/`INV-09`).

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/baseline.json` | `e0405a1bc36f3dc2050ca7ed3b8acd8a9d0a14a708583cba273360c0c4d6722b` | 100474 |
| `precode/decision-register.md` | `1883fec33f56873a426394a99d3fc6c5ec43c456a936c52733cad6c047f06262` | 102430 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `d95784bf5f67a332597b7ac4ef60a34b13d807b087d3ced9fdc46fba83c0cba5` | 46995 |
| `contracts/data/entities.yaml` | `766fe760bf487781a0b75f070d21960d84d52bccff0465fdaac65dd6ad140ce7` | 228394 |
| `contracts/state/analysis.yaml` | `06b18de42c3bbffff9a74b2e990025361cf2b179736f1994a5558f5eef3618ce` | 34958 |
| `contracts/ai/tasks.yaml` | `0048bbdd3185fc4b7719014e7d70238c50720766f19e2968cb8e25101bbc05e7` | 31787 |
| `contracts/schemas/analysis-result.schema.json` | `f26720ee04852161b4e71b4ab61c0f11c0187fcbfd25759e05245cfdb7ac172d` | 24391 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | `bbf649f5e9239d0de28c24255469ce0498f9f108bfdd45ada2ddeac859b8f1c5` | 5660 |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | `aa91b92d087681b3df902091bbe5d875e644fee6b2e08e53025ba97136eb6317` | 6406 |
| `acceptance/fixtures/ai/README.md` | `6b7ede2bc9866eed00ecdd45d52009fe7c3b895ed3c64764694b42c1f577c6a0` | 12646 |
| `acceptance/fixtures/ai/i-crash-after-provider-completion.json` | `0e7563734963fb71666f023d5d84b3a2d819afc3bb76cd9b1de9c3cc2c0dead0` | 4302 |
| `acceptance/fixtures/ai/j-same-key-resubmitted-one-result.json` | `9bc1dc1b6404dd1892ce291dd23136f2291e8a40816c4cafbe8d4814516e76f9` | 4947 |
| `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json` | `dc1defe222b82dfae97582216d2251fb35663ff177822b388334789a30c9ddea` | 5694 |
| `acceptance/fixtures/reporting/b-tag-removed-then-readded-reuse-analysis.json` | `57d26a0a8381b1b76c0c3109358e132a40bd3a2b5873c515bb5c5dcc828bc1c3` | 16540 |
| `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` | `ed7395620db5bd1b569bd087590b02e9b7cd5dbd06add2822d64ddd24f5a83b4` | 10989 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-analysis-once-per-generation`
- **Milestone:** M3 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-analysis-service`

**Mục tiêu.** Vòng đời task phân tích: enqueue theo khóa (canonical id + source fingerprint + task type + prompt/schema version + generation), claim có lease, submit đúng một kết quả hợp lệ, và đổi tag **không** làm gọi lại AI.

**Non-goals.**

- Không viết adapter (card `TC-analysis-adapter-validation`).
- Không tự quyết định đổi provider có invalidate cache hay không — mặc định giữ kết quả cũ tới khi owner yêu cầu reanalysis (B07).
- Không cho worker sửa tag/report/Saved.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0008-analysis-key-and-generation.md`, `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md`.
3. Hợp đồng nghiệp vụ: `contracts/state/analysis.yaml`, `contracts/ai/tasks.yaml`, `contracts/schemas/analysis-result.schema.json`, `contracts/retry-policy.yaml`, `contracts/http/openapi.yaml`, `contracts/data/invariants.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/ai/README.md`, `acceptance/fixtures/ai/i-crash-after-provider-completion.json`, `acceptance/fixtures/ai/j-same-key-resubmitted-one-result.json`, `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json`, `acceptance/fixtures/reporting/b-tag-removed-then-readded-reuse-analysis.json`, `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/analysis/service.py` | enqueue / claim / heartbeat / submit / unknown / reanalysis |
| `server/app/analysis/key.py` | tính analysis key theo ADR-0008 |
| `server/app/analysis/router.py` | HTTP handler `analysis.*` |
| `server/app/analysis/repository.py` | repository port theo bảng của MOD-analysis-service |
| `tests/contract/test_analysis_key.py` | khóa không đổi khi chỉ đổi tag |
| `tests/integration/test_analysis_once_per_key.py` | resubmit cùng key ⇒ một kết quả |
| `tests/integration/test_attempt_not_result.py` | crash sau provider ⇒ `unknown_attempt`, 0 kết quả |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `analysis.enqueue_tasks`
- `analysis.claim_task`
- `analysis.get_task_input`
- `analysis.heartbeat`
- `analysis.submit_result`
- `analysis.report_attempt_unknown`
- `analysis.request_reanalysis`

**Consumes** (chỉ được gọi đúng những operation này):

- `secret.revoke_task_credential`
- `storage.get_health`

**Schema:**

- kết quả submit → `contracts/schemas/analysis-result.schema.json`

**State effects.** `contracts/state/analysis.yaml` — `pending → running → valid`, nhánh `retry_wait`, `failed`, `unknown_attempt` (T-AN-01…T-AN-13). Output sai schema **không bao giờ** thành `valid`. Reanalysis tạo **generation mới**, không ghi đè generation cũ.

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-analysis-worker` — analysis_worker_token (bearer)
- `MOD-web-ui` — owner_session + CSRF cho `analysis.request_reanalysis`
- `MOD-ingest-service / MOD-report-service` — internal cho `analysis.enqueue_tasks`

**Được phép gọi:**

- MOD-secret-service (`secret.revoke_task_credential`)
- MOD-data-store

**Đường bị cấm (denied paths):**

- Analysis worker **không** được gọi `tag.*`, `report.*`, `save.*` — token chỉ mở `analysis.*` và `secret.issue_task_credential` (denied case NC-02).
- Không có đường `MOD-x-collector → MOD-analysis-service` (B12).
- Worker không tự quyết 'work này đã báo cáo' (SRC-PLAN §6.1).

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
| `I04` | analysis hợp lệ bất biến theo generation; đổi tag không gọi lại AI; retry không tạo hai kết quả cùng key |
| `I16` | attempt không bao giờ là kết quả |
| `I14` | usage unknown ≠ 0 |
| `I10` | worker stale không commit |

**Transaction và commit point:**

- `TXN-analysis-accept` — kiểm khóa, ghi kết quả và đóng task trong một commit; UNIQUE trên analysis key + generation.

**Race, replay và forbidden effects:**

- Submit hai lần cùng key ⇒ một hàng `analysis` hợp lệ (fixture `j`).
- Crash sau khi provider trả lời ⇒ `unknown_attempt`; chạy lại ghi **attempt mới**, không phải kết quả thứ hai (fixture `i`).
- Lease phân tích hết hạn giữa chừng ⇒ `WORKER_LEASE_EXPIRED`; kết quả muộn của worker cũ bị từ chối.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `AI_OUTPUT_INVALID` | `retry_wait` → `failed` khi hết budget |
| `AI_ATTEMPT_UNCERTAIN` | `unknown_attempt` |
| `IDEMPOTENCY_CONFLICT` | cùng key khác payload |
| `STALE_LEASE / WORKER_LEASE_EXPIRED` | không commit |
| `VALIDATION_ERROR` | 400 |
| `UNAUTHORIZED / CSRF_REJECTED` | 401/403 |
| `STORAGE_WRITE_FAILED` | không ACK |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC06
- SC10
- SC11
- SC17
- SC22
- SC28
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_analysis_key.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_analysis_once_per_key.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_attempt_not_result.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- AC-06: bỏ tag rồi thêm lại ⇒ **provider call counter delta = 0** cho phân tích cùng generation (fixture `b`).
- Resubmit cùng key ⇒ `COUNT(analysis WHERE status='valid' AND key=K AND generation=G) = 1`.
- Crash sau provider ⇒ `COUNT(analysis_attempt) = 1`, `COUNT(analysis valid) = 0`.
- View kết quả hợp lệ **không** chứa hàng attempt nào (I16).

**Evidence artifacts:** log pytest; provider call counter; dump bảng `analysis` + `analysis_attempt`.

**Yêu cầu live.** Chất lượng nội dung (A2/A3) cần E4 review nhiều kỳ; ngoài phạm vi card này.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ai/tasks.yaml` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 3 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ai/tasks.yaml`, `contracts/http/openapi.yaml`, `contracts/schemas/analysis-result.schema.json`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC06-02` còn OPEN: enum của `ENT-analysis-task` (`claimed`/`done`/`abandoned`) lệch với `contracts/state/analysis.yaml`. DỪNG và raise CR nếu phải chọn; **không** tự hợp nhất hai enum. |
| `SG-02` | `CR-PC06-01` còn OPEN: timeout inference theo task chưa nằm trong `contracts/retry-policy.yaml`. Nếu hai file mâu thuẫn, `retry-policy.yaml` thắng và raise CR. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-analysis-adapter-validation`.
- `TC-ingest-idempotent-ack-lost` (nguồn enqueue).

## §12. Reviewer scope

Reviewer đọc `contracts/state/analysis.yaml` (13 transition), ADR-0008, fixture `i`/`j`/`b`. Câu hỏi bắt buộc: đổi tag có làm khóa đổi không, và attempt có lọt vào view kết quả không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-analysis-once-per-generation`
- **Vị trí:** `evidence/runs/TC-analysis-once-per-generation/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
