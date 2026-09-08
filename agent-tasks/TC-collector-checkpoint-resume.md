---
card_id: TC-collector-checkpoint-resume
title_vi: Collector X: checkpoint, dừng đúng và resume
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M0 → M1
gate: G5 (chạy thật cần SP1)
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED (E1/E2). Không được tuyên bố collector hoạt động trên X thật.
owner_modules: [MOD-x-collector]
scenario_refs: [SC01, SC03, SC04, SC11, SC20, SC21, SC49, SC50]
invariant_refs: [I02, I10, I13]
evidence_manifest_id: EVM-TC-collector-checkpoint-resume
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-collector-checkpoint-resume — Collector X: checkpoint, dừng đúng và resume

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P4b-20260908`** (thay `PC10-PIN-P4-20260908`; các epoch cũ hơn: `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. **`P4`** pin sau `PKT-PC00-FIX30` (`OD-20260908-10`) — lần ghi `precode/` cuối của vòng này. Đợt sửa Giai đoạn 4/6 chạy song song chỉ chạm code, test, handoff và manifest: **không** file nào trong số đó được card pin, nên chúng không tạo ra một lần pin lại. **`P4b`** pin sau `PKT-PC00-FIX32`: `precode/adr/ADR-0011-frameworks-and-toolchain.md` được sửa (phạm vi `mypy`, `CR-PC00-35`). `ADR-0011` nằm trong read set của **mọi** card, nên một mình nó đủ làm cả 19 card `STALE`. Gói song song chỉ chạm bộ file dựng gói (pyproject, uv lockfile), workflow CI, Makefile, .gitignore và một test smoke của server — **không** file nào trong số đó được card pin hay trích dẫn, đã kiểm trực tiếp. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

**`dispatch_status: DISPATCHED (OD-20260907-03, 2026-09-07)`** — Owner đã ra lệnh bắt đầu Giai đoạn 2 (`OD-20260907-03` mục 3): 2A là mốc M0 với hai card `TC-x-feasibility-probe` và `TC-collector-checkpoint-resume`. Dòng này chỉ ghi **trạng thái điều phối** và §1–§13 không đổi vì nó. **Cổng Owner ở `contracts/ops/collector-probe.md` §6 nay đủ cả bốn xác nhận:** mục 1 (D09) ở `OD-20260907-01`, mục 2, 3 và 4 ở `OD-20260907-04` mục 1. Nhưng — theo đúng chữ của §6 — cổng đó **mở về mặt HÀNH CHÍNH, không phải về mặt vận hành**: nó gỡ trạng thái `OWNER_DECISION_REQUIRED` và **không** cho phép bất kỳ Worker, agent hay tiến trình tự động nào chạy probe (`OD-20260907-04` mục 1: *"Không Worker nào được chạy nó."*). Probe chỉ chạy **trên máy của chính Owner**, trên **tài khoản X thật của Owner**, sau khi Owner tự làm các bước ở `evidence/handoffs/TC-x-feasibility-probe-handoff.md` §11. Cổng mở **không** sinh ra bằng chứng: mọi số liệu probe vẫn `NOT_RUN`. Điểm dừng ở §10 vẫn nguyên hiệu lực; quyền thi công đến từ TASK_PACKET, không từ dòng này.

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
| `contracts/ops/collector-probe.md` | `9cf2b0185b100d0dc4fc8c69bc6d964c2b3853fb9814852444b56c8cdcbb0b79` | 32713 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/ops/secrets.md` | `14b3d8988a9de21bf70de076c2b85a21b3e87394c493f18082af51c191690ee9` | 25301 |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` | 95222 |
| `contracts/schemas/worker-assignment.schema.json` | `14efde6fdbff8a19ed2d931660a2752cc40ae96a2ecb1aa5594bdcba87fd5c18` | 19506 |
| `contracts/schemas/ingest-batch.schema.json` | `8ab444f557645ee85dbd0951af7261ac4355d3a0b8ca6b96d8450c9e1a5ae690` | 15986 |
| `contracts/schemas/ingest-receipt.schema.json` | `ff5232f46bb08369ea9af653d652d7782a42ea16798992f2507878c964ac537c` | 16970 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `70fcac8f9c7fdcdce84889015d31f109d423d1d15d68116165e9e3d0612399f8` | 5368 |
| `acceptance/fixtures/collection/README.md` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 12636 |
| `acceptance/fixtures/collection/a-feed-layout-changed.json` | `2cf0fd00657c63883ae69d42a81d31cdb02d51d2e3d7c4c36a82dd5818506b70` | 13611 |
| `acceptance/fixtures/collection/b-cursor-invalidated-reread-dedup.json` | `6ea2b75b3690af3a85b218ee8b3b32c9f339f285a86ca0a3a683c206628ec775` | 12816 |
| `acceptance/fixtures/collection/c-challenge-mid-batch.json` | `b4330c7e473779279ba545f0ecb6d9cd8f2a811beb0bae7310c62ff5dcf7e16b` | 12528 |
| `acceptance/fixtures/collection/e-limit-reached-stop.json` | `ce13e459e9e82755ab6b25f01b1e5e77e76f9a4f073ee7b69e2ab5eb9364c34e` | 7892 |
| `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json` | `7b588ca0ad1999bacdfa78ffb17ba6f0ad1336e399cb291502397f079168079b` | 7475 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/e2e/README.md` | `74790ee8435791e5dbc360cf84a0737f660e2bebcbdb0749cdc1528a669d9ca8` | 6013 |
| `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json` | `a925781ecf2d36e3cd02a3d666819bc5186c8d809e7865e51bac77d387678c00` | 30745 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-collector-checkpoint-resume`
- **Milestone:** M0 → M1 (SRC-SPEC §13) · **Cổng:** G5 (chạy thật cần SP1) (SRC-PLAN §12)
- **Module sở hữu:** `MOD-x-collector`

**Mục tiêu.** Collector chạy trên máy cá nhân: claim assignment, đọc X bằng Chrome profile riêng, nộp lô, giữ checkpoint đã ACK, và dừng đúng khi gặp giới hạn, CAPTCHA, bị chặn hoặc bố cục đổi — không tự né, không tự resume.

**Non-goals.**

- Không viết bất kỳ cơ chế nào để né CAPTCHA hoặc che giấu danh tính (SRC-SPEC §13.2 — tuyệt đối).
- Không ghi SQLite của server; không gọi Telegram; không giữ secret của provider AI.
- Không tự đẩy task phân tích (B12: server phát task sau ingest commit).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0001-topology-and-placement.md`, `precode/adr/ADR-0002-run-state-model-split.md`.
3. Hợp đồng nghiệp vụ: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/state/run.yaml`, `contracts/schemas/worker-assignment.schema.json`, `contracts/schemas/ingest-batch.schema.json`, `contracts/schemas/ingest-receipt.schema.json`, `contracts/retry-policy.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/a-feed-layout-changed.json`, `acceptance/fixtures/collection/b-cursor-invalidated-reread-dedup.json`, `acceptance/fixtures/collection/c-challenge-mid-batch.json`, `acceptance/fixtures/collection/e-limit-reached-stop.json`, `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/e2e/README.md`, `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `collector/app/session.py` | Chrome profile riêng của dự án (D09), không dùng profile mặc định |
| `collector/app/reader.py` | đọc feed, phát hiện challenge / layout changed |
| `collector/app/batcher.py` | gom lô, tính `payload_hash`, `batch_idempotency_key` |
| `collector/app/client.py` | gọi `worker.*` + `ingest.*` bằng `collectorToken`; tra receipt trước retry |
| `collector/app/limits.py` | giới hạn đợt PROVISIONAL 200 post hoặc 30 phút |
| `tests/contract/test_collector_stop_reasons.py` | ánh xạ stop_reason ↔ error code |
| `tests/integration/test_collector_resume_after_challenge.py` | checkpoint giữ, một alert intent, không tự claim lại |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces:** không operation nào. Card này là **caller**, không sở hữu operation trong `contracts/ports.yaml`.

**Consumes** (chỉ được gọi đúng những operation này):

- `worker.register_capabilities`
- `worker.claim_assignment`
- `worker.heartbeat`
- `worker.report_stop`
- `worker.release_assignment`
- `ingest.submit_batch`
- `ingest.commit_checkpoint`
- `ingest.get_receipt`
- `health.get_liveness`

**Schema:**

- lô gửi lên → `contracts/schemas/ingest-batch.schema.json`
- receipt nhận về → `contracts/schemas/ingest-receipt.schema.json`
- assignment nhận về → `contracts/schemas/worker-assignment.schema.json`

**State effects.** Collector **không** sở hữu state nào của server. Nó chỉ báo cáo: `worker.report_stop` với `stop_reason ∈ {limit_reached, captcha, session_expired, source_blocked, storage_unavailable, worker_lost}` (`contracts/state/run.yaml`). Chuyển `running/collecting → needs_user` là hệ quả server ghi (`T-RUN-05`).

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at); `ENT-worker-registration` (online_state, last_run_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được phép gọi:**

- MOD-job-service (`worker.*`, bearer `collectorToken`)
- MOD-ingest-service (`ingest.*`, bearer `collectorToken`)
- Chrome profile riêng của dự án trên máy cá nhân (D09)

**Đường bị cấm (denied paths):**

- `MOD-x-collector → MOD-saved-service` bị cấm: token collector gọi `save.create` ⇒ 401 (denied case NC-01).
- Không truy cập SQLite server, không nhận secret AI, không mở cổng vào máy cá nhân (SRC-SPEC §6.4).
- Không đổi account, không dùng proxy, không giả click xác minh khi bị chặn.

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
| `I02` | checkpoint không đi trước dữ liệu bền — dữ liệu đã tải nhưng chưa ingest **không** phải checkpoint |
| `I10` | CAPTCHA không tự retry/resume |
| `I13` | empty ≠ limit ≠ failure |

**Transaction và commit point:**

- Collector không có transaction; điểm commit nằm ở server. Trước mọi retry mutation phải gọi `ingest.get_receipt` (SRC-PLAN §5.1).

**Race, replay và forbidden effects:**

- Timeout transport = **không biết kết quả**, không phải rollback: tra receipt rồi mới quyết định.
- Con trỏ feed mất hiệu lực ⇒ được đọc lại theo recovery policy, dedup ở ingest (B05/AMD-B05).
- Lease hết hạn giữa lô ⇒ dừng, không commit tiếp bằng lease cũ.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `X_CHALLENGE_REQUIRED` | báo `worker.report_stop`; server đưa run về `needs_user`; đúng **một** alert intent/run |
| `X_ACCESS_BLOCKED` | run `blocked`; ghi điều kiện gỡ chặn; dừng hẳn |
| `SOURCE_LAYOUT_CHANGED` | dừng và báo; **không** đoán selector mới (`CR-PC05-01`) |
| `STALE_LEASE / WORKER_LEASE_EXPIRED` | dừng ngay, không nộp thêm lô |
| `INGEST_ACK_LOST` | tra `ingest.get_receipt`; chỉ replay khi receipt nói `not_committed` |
| `STORAGE_WRITE_FAILED` | dừng nộp; không tiến cursor cục bộ |
| `SOURCE_METADATA_UNAVAILABLE` | item ở mức post-only; không đoán DOI |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC01
- SC03
- SC04
- SC11
- SC20
- SC21
- SC49
- SC50

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_collector_stop_reasons.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_collector_resume_after_challenge.py -q` (PROVISIONAL)
- Probe thật: theo `contracts/ops/collector-probe.md` — thuộc card `TC-x-feasibility-probe`, **NOT_RUN**

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `c-challenge-mid-batch.json`: sau challenge, `COUNT(alert intent) = 1`, không có request thu thập mới trước resume, checkpoint = mốc đã ACK.
- Fixture `e-limit-reached-stop.json`: `stop_reason = limit_reached`, checkpoint hash ổn định.
- Fixture `a-feed-layout-changed.json`: `SOURCE_LAYOUT_CHANGED`, 0 post ghi bằng selector đoán.
- Fixture `b-cursor-invalidated-reread-dedup.json`: đọc lại nhưng `COUNT(post)` không tăng trùng.

**Evidence artifacts:** log pytest; trace HTTP đã che token; dump checkpoint trước/sau.

**Yêu cầu live.** AC-01 và AC-04 chỉ đạt E3 khi có collector run thật. Card này **không** được tự chạy live: live thuộc SP1 và cần Owner mở cổng theo `contracts/ops/collector-probe.md` §6.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED (E1/E2). Không được tuyên bố collector hoạt động trên X thật.`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 5 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/schemas/ingest-receipt.schema.json`, `contracts/schemas/worker-assignment.schema.json`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-RATE` | **Rate limit của X là `partial`, KHÔNG phải `blocked`** (ruling trên `CR-PC10-02`, nay đã landing). `worker.report_stop` nhận `stop_reason = rate_limited` và mã `RATE_LIMITED`; transition là `T-RUN-25` → `running/enriching`, run kết thúc `outcome: partial`. Cấm: đưa run về `blocked` (biến một tình huống tự hết thành việc phải làm tay), thử lại trong cùng đợt, hoặc để `run.x_coverage_note_vi` trống — nó **bắt buộc** nhắc mốc `run.rate_limited_at`. |
| `SG-01` | **SP1 vẫn chưa chạy.** REQ-OQ01 (D09 — Chrome profile riêng của dự án) **đã được Owner trả lời** (`OD-20260907-01` mục 1), nên M0 không còn bị chặn bởi *quyết định* đó. Nhưng `contracts/ops/collector-probe.md` §0 vẫn ghi bằng chứng là **NOT_RUN**: chưa ai chạy thật. Không được tuyên bố bất kỳ điều gì về hành vi của X; cần dữ liệu thật ⇒ DỪNG. |
| `SG-02` | Bốn xác nhận của Owner ở `collector-probe.md` §6 chưa đủ ⇒ trạng thái `OWNER_DECISION_REQUIRED` và probe **không được chạy**. |
| `SG-03` | Nếu X đổi bố cục hoặc chặn ⇒ dừng và báo. Cấm mọi hành vi né tránh; đó là điều kiện không thương lượng. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-scheduler-lease-claim` (`worker.*`).
- `TC-ingest-idempotent-ack-lost` (`ingest.*`).
- `TC-x-feasibility-probe` cho mọi khẳng định live.

## §12. Reviewer scope

Reviewer đọc `contracts/ops/collector-probe.md` §2 và §4, `contracts/state/run.yaml` `T-RUN-04/05/10`, 5 fixture ở §2. Câu hỏi bắt buộc: có dòng code nào tự vượt qua challenge hoặc tự resume không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-collector-checkpoint-resume`
- **Vị trí:** `evidence/runs/TC-collector-checkpoint-resume/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
