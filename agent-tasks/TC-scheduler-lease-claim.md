---
card_id: TC-scheduler-lease-claim
title_vi: Scheduler, hàng đợi và lease claim một-chủ
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M7
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-scheduler, MOD-job-service]
scenario_refs: [SC01, SC02, SC04, SC15, SC20, SC33, SC49, SC34, SC35]
invariant_refs: [I01, I10, I13]
evidence_manifest_id: EVM-TC-scheduler-lease-claim
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-scheduler-lease-claim — Scheduler, hàng đợi và lease claim một-chủ

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P4b-20260908`** (thay `PC10-PIN-P4-20260908`; các epoch cũ hơn: `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. **`P4`** pin sau `PKT-PC00-FIX30` (`OD-20260908-10`) — lần ghi `precode/` cuối của vòng này. Đợt sửa Giai đoạn 4/6 chạy song song chỉ chạm code, test, handoff và manifest: **không** file nào trong số đó được card pin, nên chúng không tạo ra một lần pin lại. **`P4b`** pin sau `PKT-PC00-FIX32`: `precode/adr/ADR-0011-frameworks-and-toolchain.md` được sửa (phạm vi `mypy`, `CR-PC00-35`). `ADR-0011` nằm trong read set của **mọi** card, nên một mình nó đủ làm cả 19 card `STALE`. Gói song song chỉ chạm bộ file dựng gói (pyproject, uv lockfile), workflow CI, Makefile, .gitignore và một test smoke của server — **không** file nào trong số đó được card pin hay trích dẫn, đã kiểm trực tiếp. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` | 27451 |
| `precode/baseline.json` | `e8cf3910c6f2351a2c7c4a8620121b0415a58c5c7ec86eee7ba5d33c343c1a70` | 127222 |
| `precode/decision-register.md` | `a38e2ce1a953279b7d1ca0ba6ae2ad52f97886a887f98e596b9ade0f4fdb211b` | 185553 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `ebcf460fa2e415cc6897cdbe7cee144bda9368e4a5af9cd514ec676224399936` | 241542 |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` | 95222 |
| `contracts/state/storage.yaml` | `a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849` | 29908 |
| `contracts/schemas/worker-assignment.schema.json` | `14efde6fdbff8a19ed2d931660a2752cc40ae96a2ecb1aa5594bdcba87fd5c18` | 19506 |
| `contracts/reporting/time-and-tags.md` | `70f4bc57a0fa2733d92136194eb4d563fa5d9145726141ee30493fe3a2b1a66c` | 61837 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` | 19568 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `70fcac8f9c7fdcdce84889015d31f109d423d1d15d68116165e9e3d0612399f8` | 5368 |
| `precode/adr/ADR-0007-timezone-handling.md` | `fbb464c22df45248895107a3f38e85f700e9cdecd9a722eaa9f2a4b028995e44` | 5287 |
| `acceptance/fixtures/collection/README.md` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 12636 |
| `acceptance/fixtures/collection/g-schedule-due-claim.json` | `32a9defa30bbbbe334b6e28378b8bcf09f2bc1d002a2fc2275886b6df5ca60ba` | 11845 |
| `acceptance/fixtures/collection/f-two-workers-claim-same-assignment.json` | `92939afbb6896caae0510ea2d34e638ba5a8d74ea94be89bd9755de33dbe0518` | 9384 |
| `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json` | `e9f9d893a954f92c1918ea2fbb79f7ac0d65a31a60bbf009f7786be25612a1f1` | 13675 |
| `acceptance/fixtures/recovery/b-post-restore-stale-lease-rejected.json` | `4655e8d95fcc433bba5912c273b0642d4da21e8b730b1c3a046db956e693e88c` | 3455 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/collection/i-run-now-while-active.json` | `b2b809e1e3fb4ca5553d29ab4eeb3400cdf5af9056e3f96d73eaff1dc64a074e` | 7470 |
| `acceptance/fixtures/collection/j-dst-boundary-occurrences.json` | `d709a547e557842d021e1b65d5a63f4c009e71e06578d3daae2dfff96b5983de` | 6372 |
| `acceptance/fixtures/collection/k-cancel-from-every-non-terminal.json` | `4c7a46b976baac02a2fbe95064f5620c22ac8ae04b84a2fd1f36321a3cb06d76` | 12397 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-scheduler-lease-claim`
- **Milestone:** M7 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-scheduler`, `MOD-job-service`

**Mục tiêu.** Lịch tới hạn tạo đúng một assignment; nhiều kỳ quá hạn gộp thành một đợt bù; hai worker claim cùng assignment thì chỉ một thắng và epoch cũ bị từ chối vĩnh viễn.

**Non-goals.**

- Không chạy Chrome, không đọc X (card `TC-collector-checkpoint-resume`).
- Không gửi digest, không đánh dấu report đã giao (`contracts/modules.yaml` cấm cạnh này).
- Không tự quyết giá trị lịch thật: 08:00 và 20:00 là PROVISIONAL (baseline §5 hàng OQ defaults).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0002-run-state-model-split.md`, `precode/adr/ADR-0007-timezone-handling.md`.
3. Hợp đồng nghiệp vụ: `contracts/state/run.yaml`, `contracts/state/storage.yaml`, `contracts/schemas/worker-assignment.schema.json`, `contracts/reporting/time-and-tags.md`, `contracts/http/openapi.yaml`, `contracts/ops/deployment.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/g-schedule-due-claim.json`, `acceptance/fixtures/collection/f-two-workers-claim-same-assignment.json`, `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json`, `acceptance/fixtures/recovery/b-post-restore-stale-lease-rejected.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/collection/i-run-now-while-active.json`, `acceptance/fixtures/collection/j-dst-boundary-occurrences.json`, `acceptance/fixtures/collection/k-cancel-from-every-non-terminal.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/scheduler/evaluator.py` | `scheduler.evaluate_due` với fake-clock injectable |
| `server/app/jobs/service.py` | enqueue, coalesce, claim, heartbeat, release |
| `server/app/jobs/lease.py` | lease epoch, TTL, thu hồi |
| `server/app/jobs/router.py` | HTTP handler `worker.*` và `run.*` |
| `tests/contract/test_worker_assignment_schema.py` | `worker-assignment.schema.json` |
| `tests/integration/test_scheduler_catchup.py` | nhiều kỳ offline → một đợt bù |
| `tests/integration/test_lease_two_claimants.py` | hai worker, một thắng, epoch cũ bị reject |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `scheduler.evaluate_due`
- `job.enqueue_scheduled_run`
- `job.coalesce_overdue`
- `worker.register_capabilities`
- `worker.claim_assignment`
- `worker.heartbeat`
- `worker.report_stop`
- `worker.release_assignment`
- `worker.get_status`
- `run.list`
- `run.get`
- `run.run_now`
- `run.resume`
- `run.cancel`

**Consumes** (chỉ được gọi đúng những operation này):

- `ingest.get_checkpoint`
- `storage.get_health`
- `delivery.create_intent`

**Schema:**

- payload claim → `contracts/schemas/worker-assignment.schema.json`

**State effects.** `contracts/state/run.yaml` — `T-RUN-01` (claim), `T-RUN-11` (lease hết hạn, tăng epoch), `T-RUN-10` (resume từ `needs_user`), `T-RUN-17a/b/c` (cancel). `run.status` là **read-only** với Telegram; `run.run_now` không ghi đè `needs_user` (B10/AMD-B10).

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at); `ENT-worker-registration` (online_state, last_run_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-web-ui` — owner_session (+CSRF cho mutation)
- `MOD-telegram-adapter` — owner_session_or_linked_chat cho `run.list` và `run.run_now`
- `MOD-x-collector` — collector_token cho `worker.*`
- `MOD-analysis-worker` — analysis_worker_token cho `worker.register_capabilities`

**Được phép gọi:**

- MOD-ingest-service (`ingest.get_checkpoint`, chỉ đọc)
- MOD-data-store
- MOD-delivery-service (alert intent)

**Đường bị cấm (denied paths):**

- Scheduler **không** gọi Chrome, không gửi Telegram, không đánh dấu report đã giao (SRC-PLAN §6).
- Telegram không có lệnh thứ tư; hủy liên kết là hành động app (`F-PC00-01`, `CR-PC01-02`).
- Không đường `MOD-job-service` ghi bảng `checkpoint` — chỉ đọc (ruling R-01).

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
| `I01` | mutation qua port đã xác thực |
| `I10` | worker stale/cancelled không commit kết quả mới |
| `I13` | empty / limit / failure / unknown hiển thị riêng |

**Transaction và commit point:**

- Claim là CAS trên assignment + cấp lease epoch mới trong một transaction.
- Coalesce nhiều kỳ quá hạn ghi `schedule_occurrence_ids` của đợt bù; không tạo N đợt.

**Race, replay và forbidden effects:**

- Hai worker claim đồng thời ⇒ đúng một thắng, kẻ thua nhận `IDEMPOTENCY_CONFLICT`/`STALE_LEASE`.
- Worker cũ heartbeat sau khi epoch tăng ⇒ `WORKER_LEASE_EXPIRED`, không reset `needs_user` đã lưu.
- `run.run_now` khi run đang `needs_user` ⇒ không đổi trạng thái (fixture `l-run-now-while-needs-user.json`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `VALIDATION_ERROR` | 400 |
| `UNAUTHORIZED` | 401 |
| `UNAUTHORIZED_COMMAND` | chat lạ im lặng; không đổi domain state |
| `STALE_LEASE` | lời gọi bị từ chối, dữ liệu authoritative không đổi |
| `WORKER_LEASE_EXPIRED` | assignment revoked; run về `queued` hoặc giữ `needs_user`/`blocked` đã lưu |
| `IDEMPOTENCY_CONFLICT` | claim thua |
| `X_CHALLENGE_REQUIRED` | `run.resume` từ chối khi phiên còn challenge |
| `X_ACCESS_BLOCKED` | run giữ `blocked`; không luân chuyển account |
| `CONFLICT` | `run.resume` sai guard |
| `STORAGE_WRITE_FAILED` | không enqueue, không ACK |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC01
- SC02
- SC04
- SC15
- SC20
- SC33
- SC49
- SC34
- SC35

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_worker_assignment_schema.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_scheduler_catchup.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_lease_two_claimants.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Ba kỳ offline ⇒ đúng **một** hàng run bù, `schedule_occurrence_ids` có 3 phần tử.
- Hai claimant ⇒ `COUNT(assignment_lease active) = 1`; lời gọi của kẻ thua trả `STALE_LEASE`.
- `run.run_now` trên run `needs_user` ⇒ transition log **rỗng**.
- Fake clock: lịch tới hạn lúc T ⇒ assignment tồn tại trước T + toleransi đã ghi trong `retry-policy.yaml`.

**Evidence artifacts:** log pytest; dump bảng `run` + `assignment_lease`; transition log.

**Yêu cầu live.** Live collector run có timestamp là bằng chứng E3 của AC-01; **không** thuộc card này (thuộc SP1/M0).

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Phạm vi đã phê chuẩn** (`OD-20260907-01`). Read set của card này nằm trong bốn phạm vi mà A2-R4 xác định đủ điều kiện — *ranh giới và quyền*, *dữ liệu và định danh*, *workflow và trạng thái*, *báo cáo và thời gian* — và không chạm `contracts/ai/`, `contracts/telegram/`, hay bất kỳ file `contracts/ops/` nào ngoài `deployment.md` (file này đã lên `CONTRACT_READY` ở PC01-FIX13). 17 blocker B01–B17 nay là `RATIFIED`, nên điểm dừng dạng *"B0x còn PROVISIONAL"* đã gỡ khỏi §10.

  **Nhưng nền hợp đồng CHƯA đồng nhất `CONTRACT_READY`.** 2 file hợp đồng trong read set của card này vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW` trong chính header của nó: `contracts/http/openapi.yaml`, `contracts/schemas/worker-assignment.schema.json`. Vì vậy **không** được đọc mục này là "mọi hợp đồng đã sẵn sàng"; hãy đọc là "phạm vi nghiệp vụ đã được phê chuẩn, và 2 file còn lại phải lên `CONTRACT_READY` trước khi claim của card vượt quá `IMPLEMENTATION_VERIFIED`". Kiểm lại bằng `grep -h claim_ceiling <file>` — đừng tin dòng này.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC03-02` còn OPEN: không operation nào đưa run rời `blocked` ngoài `run.cancel`. Nếu cần đường unblock, DỪNG và raise CR — **không** tự thêm operation. |
| `SG-02` | Lịch 08:00/20:00 giờ owner và giới hạn 200 post hoặc 30 phút nay là **giá trị làm việc được Owner chấp nhận** (`OD-20260907-01` mục 20); timezone `Asia/Ho_Chi_Minh` đã xác nhận (mục 4). Vẫn **đọc từ settings**, không hard-code: REQ-OQ05 còn phải đo lại sau M0. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-ingest-idempotent-ack-lost` cho `ingest.get_checkpoint`.
- `TC-owner-auth-session` cho `run.*` qua owner session.

## §12. Reviewer scope

Reviewer đọc `contracts/state/run.yaml` (26 transition), `worker-assignment.schema.json`, 4 fixture ở §2. Câu hỏi bắt buộc: có đường nào để worker epoch cũ ghi được dữ liệu không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-scheduler-lease-claim`
- **Vị trí:** `evidence/runs/TC-scheduler-lease-claim/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
