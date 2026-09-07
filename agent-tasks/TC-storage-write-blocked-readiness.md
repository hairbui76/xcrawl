---
card_id: TC-storage-write-blocked-readiness
title_vi: Storage không ghi được: không ACK, readiness đỏ qua kênh độc lập
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M1 → M8
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-data-store, MOD-health-service]
scenario_refs: [SC15, SC26, SC27, SC42, SC36, SC49]
invariant_refs: [I02, I13, I15]
evidence_manifest_id: EVM-TC-storage-write-blocked-readiness
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-storage-write-blocked-readiness — Storage không ghi được: không ACK, readiness đỏ qua kênh độc lập

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P3b-20260908`** (thay `PC10-PIN-P3-20260908`; các epoch cũ hơn: `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

**`dispatch_status: DISPATCHED (OD-20260907-02, 2026-09-07)`** — Owner đã ra lệnh bắt đầu Giai đoạn 1 và cấp G5 entry cho bốn card M1 (`OD-20260907-02` mục 2: `TC-ingest-idempotent-ack-lost`, `TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness`). Dòng này chỉ ghi **trạng thái điều phối**. Nội dung nghĩa vụ của card **không đổi**: §1–§13 giữ nguyên từng chữ qua các lần pin lại `PC10-PIN-P1-20260907`, `PC10-PIN-P1b-20260907`, `PC10-PIN-P1c-20260907`, `PC10-PIN-P1d-20260907` `PC10-PIN-P2-20260907` `PC10-PIN-P2b-20260907` `PC10-PIN-P2c-20260907` `PC10-PIN-P2d-20260907` `PC10-PIN-P3-20260908` và `PC10-PIN-P3b-20260908`; thứ duy nhất đổi ở những lần pin đó là các hàng hash trong bảng dưới. Quyền thi công vẫn do TASK_PACKET của Coordinator mở (lease + write set), không do dòng này; mọi điểm dừng ở §10 vẫn nguyên hiệu lực và trần claim vẫn như front-matter khai.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `da5181b2888674134f6e3919ce401014015f223ea46a967d9fda3833c01a037b` | 22685 |
| `precode/baseline.json` | `52af62c8b11e6939a9a34798bd71b4a4e688d8ed85d9c579ee1858ed341037e9` | 124824 |
| `precode/decision-register.md` | `b26cf51a0d7c73661ab465e5a157aaad7a9ceb6f013926abd5117f6966764a7e` | 182028 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `ebcf460fa2e415cc6897cdbe7cee144bda9368e4a5af9cd514ec676224399936` | 241542 |
| `contracts/state/storage.yaml` | `a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849` | 29908 |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` | 19568 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` | 95222 |
| `contracts/ui/screens.yaml` | `e1a57407c0733aa709b464b61da3313f0f6109f5696bd8b39b7e77fc5d5d9074` | 51212 |
| `precode/adr/ADR-0005-backup-method.md` | `889de2812a8736e328eb7823a82e2b5dab1f46aee13257bfcfedd08d4668bd5c` | 5457 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
| `acceptance/fixtures/recovery/README.md` | `982311e721d8e9e740f51ae011c557c363ba3d0de8151dd0643755ecb926dac8` | 12235 |
| `acceptance/fixtures/recovery/c-disk-full-mid-ingest.json` | `8f6379b4b0c633ca7d3b48be039671b17ece9da58c1f96067003bf2fb0194092` | 3532 |
| `acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json` | `b518ea3ac66e00e2c117b6586eadb648746fe71947b0c37a17ab50f81cdf7e82` | 3665 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/collection/l-storage-write-blocked-mid-run.json` | `7f5f751e9f23ea48ddb0623ce38a168967e621a014f2ca954b5852add193aeaf` | 9225 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-storage-write-blocked-readiness`
- **Milestone:** M1 → M8 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-data-store`, `MOD-health-service`

**Mục tiêu.** Khi hết ổ hoặc DB không ghi được: process chuyển `write_blocked`, ngừng nhận job mới, **không** ACK mutation, và báo qua kênh readiness/health **độc lập** với DB; UI phân biệt last-known state với trạng thái chưa lưu được.

**Non-goals.**

- Không viết backup/restore (card 15).
- Không viết UI (card 16).
- Không tuyên bố đã persist lỗi khi không ghi được vào DB.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0005-backup-method.md`, `precode/adr/ADR-0001-topology-and-placement.md`.
3. Hợp đồng nghiệp vụ: `contracts/state/storage.yaml`, `contracts/ops/deployment.md`, `contracts/http/openapi.yaml`, `contracts/state/run.yaml`, `contracts/ui/screens.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/c-disk-full-mid-ingest.json`, `acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/collection/l-storage-write-blocked-mid-run.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/storage/health.py` | `storage.health` state machine `T-ST-01`…`T-ST-09` |
| `server/app/storage/guard.py` | chặn mutation khi `write_blocked` |
| `server/app/health/router.py` | `health.get_liveness`, `health.get_readiness` — kênh độc lập DB |
| `tests/integration/test_disk_full_no_ack.py` | disk-full giữa ingest |
| `tests/integration/test_readiness_independent_channel.py` | readiness đỏ khi DB không ghi được |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `storage.get_health`
- `health.get_liveness`
- `health.get_readiness`

**Consumes:** không operation nào của hệ thống.

**Schema:**

- không có JSON Schema riêng; hình dạng ở `contracts/state/storage.yaml` → `contracts/state/storage.yaml`

**State effects.** `healthy | write_blocked | maintenance | recovery_required`. `independent_health_channel` HC-01…HC-04 trong `contracts/state/storage.yaml` là ràng buộc bắt buộc: kênh báo không được phụ thuộc vào việc ghi DB.

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-health-service` — internal
- `MOD-job-service` — internal
- `MOD-web-ui / MOD-x-collector / MOD-analysis-worker` — `health.get_liveness` là `public_minimal`; `health.get_readiness` là `owner_session`

**Được phép gọi:**

- MOD-data-store

**Đường bị cấm (denied paths):**

- Không ACK mutation khi `write_blocked`.
- Không tuyên bố 'đã persist lỗi' nếu không ghi được trạng thái lỗi vào DB (SRC-PLAN §8.4).
- Không tiến cursor, không tiêu thụ backfill, không đóng coverage khi `write_blocked`.

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
| `I02` | checkpoint không đi trước dữ liệu bền |
| `I13` | last-known state khác trạng thái mới chưa lưu được |
| `I15` | sau restore chưa đối soát thì dispatcher khóa |

**Transaction và commit point:**

- Sau phục hồi, **transaction receipt và lease epoch** quyết định phần nào đã commit — không phải log.

**Race, replay và forbidden effects:**

- Disk-full giữa ingest ⇒ receipt **absent**, readiness đỏ, collector coi kết quả là chưa biết.
- Restore chưa đối soát xong ⇒ `recovery_required`, dispatch khóa (fixture `j`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `STORAGE_WRITE_FAILED` | `storage.write_blocked`; job không được ACK; không hứa đã persist |
| `RESTORE_UNVERIFIED` | `storage.recovery_required`; dispatcher/worker claim dừng |
| `UNAUTHORIZED` | 401 cho `health.get_readiness` |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC15
- SC26
- SC27
- SC42
- SC36
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/integration/test_disk_full_no_ack.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_readiness_independent_channel.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `c-disk-full-mid-ingest.json`: `ingest_receipt` **absent** và readiness **đỏ** — hai điều kiện phải cùng đúng.
- Không có hàng nào ghi 'đã persist lỗi' khi DB không ghi được.
- `health.get_liveness` vẫn trả lời khi DB chết (kênh độc lập).
- Fixture `j`: `recovery_required` ⇒ `COUNT(delivery attempt sau restore) = 0`.

**Evidence artifacts:** log pytest; readiness response đã che secret; đếm hàng receipt.

**Yêu cầu live.** Không cần live; fault injection là đủ.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Phạm vi đã phê chuẩn** (`OD-20260907-01`). Read set của card này nằm trong bốn phạm vi mà A2-R4 xác định đủ điều kiện — *ranh giới và quyền*, *dữ liệu và định danh*, *workflow và trạng thái*, *báo cáo và thời gian* — và không chạm `contracts/ai/`, `contracts/telegram/`, hay bất kỳ file `contracts/ops/` nào ngoài `deployment.md` (file này đã lên `CONTRACT_READY` ở PC01-FIX13). 17 blocker B01–B17 nay là `RATIFIED`, nên điểm dừng dạng *"B0x còn PROVISIONAL"* đã gỡ khỏi §10.

  **Nhưng nền hợp đồng CHƯA đồng nhất `CONTRACT_READY`.** 2 file hợp đồng trong read set của card này vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW` trong chính header của nó: `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml`. Vì vậy **không** được đọc mục này là "mọi hợp đồng đã sẵn sàng"; hãy đọc là "phạm vi nghiệp vụ đã được phê chuẩn, và 2 file còn lại phải lên `CONTRACT_READY` trước khi claim của card vượt quá `IMPLEMENTATION_VERIFIED`". Kiểm lại bằng `grep -h claim_ceiling <file>` — đừng tin dòng này.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Nếu không thể chứng minh kênh readiness độc lập với DB trong stack đã chọn ⇒ DỪNG. Đây là ràng buộc hợp đồng, không phải chi tiết triển khai. |
| `SG-02` | Không dùng UI để suy ra readiness; UI hiển thị last-known và phải nói rõ là last-known (I13). |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-ingest-idempotent-ack-lost`
- `TC-backup-restore-drill`

## §12. Reviewer scope

Reviewer đọc `contracts/state/storage.yaml` (9 transition + HC-01…HC-04), fixture `c` và `j`. Câu hỏi bắt buộc: có đường nào ACK được phát khi `write_blocked` không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-storage-write-blocked-readiness`
- **Vị trí:** `evidence/runs/TC-storage-write-blocked-readiness/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
