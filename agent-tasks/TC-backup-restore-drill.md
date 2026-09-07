---
card_id: TC-backup-restore-drill
title_vi: Backup nhất quán WAL-safe và diễn tập restore có khóa side effect
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M8
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-backup-service, MOD-backup-cli]
scenario_refs: [SC26, SC27, SC42, SC43, SC12, SC49, SC44, SC53]
invariant_refs: [I15, I08]
evidence_manifest_id: EVM-TC-backup-restore-drill
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-backup-restore-drill — Backup nhất quán WAL-safe và diễn tập restore có khóa side effect

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P1d-20260907`** (thay `PC10-PIN-P1c-20260907`; các epoch cũ hơn: `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). Bản pin sau `PKT-PC02-FIX13`: `contracts/data/entities.yaml` được sửa **chỉ ở phần văn xuôi** của khối amendment `AMD-ENT-owner-01` — **không trường nào đổi**. Card vẫn phải pin lại: quy tắc `STALE` đọc **byte**, không đọc ý định, và một ngoại lệ "chỉ là văn xuôi" sẽ biến cửa pin thành thứ phải phán đoán mới dùng được. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `da5181b2888674134f6e3919ce401014015f223ea46a967d9fda3833c01a037b` | 22685 |
| `precode/baseline.json` | `d25e2edd05437dc475797f16e96e874d53ae0cd336cd162dd4b5a4131292c7bd` | 104398 |
| `precode/decision-register.md` | `56cd624f3d6a429888018abea9fb67e9dbe26aa6d202630c50ff8f989102c06d` | 117150 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `d95784bf5f67a332597b7ac4ef60a34b13d807b087d3ced9fdc46fba83c0cba5` | 46995 |
| `contracts/data/entities.yaml` | `df5e023124a910d7c6c022d3b69d190e7534db8f64b8d2f1dfdde2b1db7d142f` | 239261 |
| `contracts/ops/backup-restore.md` | `826655daa469e3e8e2fbd54263f13be78f4e9a17fd490524a3b07f894989ad4f` | 25858 |
| `contracts/state/storage.yaml` | `a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849` | 29908 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` | 19568 |
| `precode/adr/ADR-0005-backup-method.md` | `889de2812a8736e328eb7823a82e2b5dab1f46aee13257bfcfedd08d4668bd5c` | 5457 |
| `acceptance/fixtures/recovery/README.md` | `982311e721d8e9e740f51ae011c557c363ba3d0de8151dd0643755ecb926dac8` | 12235 |
| `acceptance/fixtures/recovery/a-restore-old-outbox-nothing-sent.json` | `e7671e7d852f9b0564c5c269df95e598e3de88cdb94142df23a29ee38b543838` | 4194 |
| `acceptance/fixtures/recovery/b-post-restore-stale-lease-rejected.json` | `4655e8d95fcc433bba5912c273b0642d4da21e8b730b1c3a046db956e693e88c` | 3455 |
| `acceptance/fixtures/recovery/d-wal-unsafe-copy-detected.json` | `64d11f5541826f64888a29b4fcc97af020715370a3d5237bfc9d371b4367a804` | 3048 |
| `acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json` | `b518ea3ac66e00e2c117b6586eadb648746fe71947b0c37a17ab50f81cdf7e82` | 3665 |
| `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json` | `3630edc83719ada07cae9b39f5da7ad8d1894379509c96bb1128cf958ca6ea0b` | 3462 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` | `9cd382e270e581b1b4ea69ac78f9ddb7730d215d34fadf6ce537a4e1f0dc053a` | 20786 |
| `acceptance/fixtures/recovery/m-post-restore-reconciled-dispatch-reopens.json` | `90934af96aa37ea8917dbd581247afa05655be3e23fc77b4004c1c9227b4be94` | 7808 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-backup-restore-drill`
- **Milestone:** M8 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-backup-service`, `MOD-backup-cli`

**Mục tiêu.** Snapshot bằng SQLite Online Backup API hoặc `VACUUM INTO` (WAL-safe) kèm manifest; restore vào môi trường có khóa side effect; trước khi đối soát xong thì outbox không phát lại, job không chạy lại, `first_announced` không bị reset.

**Non-goals.**

- Không copy file DB đang chạy (D58 đã được AMD-B11 sửa).
- Không tự resume dispatcher ngay sau restore.
- Không hiện thực `data.purge_all` (loại trừ còn `OWNER_DECISION_REQUIRED`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0005-backup-method.md`.
3. Hợp đồng nghiệp vụ: `contracts/ops/backup-restore.md`, `contracts/state/storage.yaml`, `contracts/http/openapi.yaml`, `contracts/data/entities.yaml`, `contracts/ops/deployment.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/a-restore-old-outbox-nothing-sent.json`, `acceptance/fixtures/recovery/b-post-restore-stale-lease-rejected.json`, `acceptance/fixtures/recovery/d-wal-unsafe-copy-detected.json`, `acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json`, `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json`, `acceptance/fixtures/recovery/m-post-restore-reconciled-dispatch-reopens.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/backup/snapshot.py` | Online Backup API / `VACUUM INTO` + manifest |
| `server/app/backup/verify.py` | kiểm manifest, phát hiện bản copy WAL-unsafe |
| `server/app/backup/restore.py` | restore + maintenance guard + thu hồi lease |
| `server/app/backup/reconcile.py` | đối soát: outbox, lease epoch, `first_announced` |
| `tools/backup_cli.py` | MOD-backup-cli, chỉ dùng `backupOperatorToken` |
| `tests/integration/test_wal_unsafe_detected.py` | bản copy không WAL-safe bị từ chối |
| `tests/integration/test_restore_side_effect_lock.py` | 0 tin gửi trước khi đối soát xong |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `backup.create_snapshot`
- `backup.verify_snapshot`
- `backup.restore_snapshot`
- `backup.reconcile_after_restore`

**Consumes** (chỉ được gọi đúng những operation này):

- `storage.get_health`

**Schema:**

- manifest và restore record → `contracts/data/entities.yaml`
- thủ tục và điều kiện → `contracts/ops/backup-restore.md`

**State effects.** `ENT-backup-snapshot`, `ENT-backup-manifest`, `ENT-restore-record`. `storage.health` đi qua `maintenance` và `recovery_required` (`contracts/state/storage.yaml`). Dispatcher chỉ mở lại sau khi `reconciliation_complete` đủ mệnh đề.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-backup-cli` — backup_operator (bearer `backupOperatorToken`) — **scheme duy nhất** cho `backup.*`

**Được phép gọi:**

- MOD-data-store

**Đường bị cấm (denied paths):**

- Phiên trình duyệt owner **không** kích hoạt được restore (CR-PC08-02).
- Không resume dispatcher tự động ngay sau restore (I15).
- Không reset `first_announced` mà không kiểm tra.
- Không copy file DB đang chạy (AMD-B11).

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
| `I15` | restore không tự gửi lại outbox cũ, không chạy lại job side effect, không reset first_announced |
| `I08` | snapshot Saved bất biến qua restore |

**Transaction và commit point:**

- Restore là thao tác có **maintenance guard**: thu hồi mọi lease trước, mở dispatcher sau đối soát.

**Race, replay và forbidden effects:**

- Lease cũ dùng lại sau restore ⇒ bị từ chối (fixture `b`).
- Outbox cũ trong snapshot ⇒ **0 tin** được gửi (fixture `a`).
- Đối soát chưa xong ⇒ dispatch khóa (fixture `j`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `RESTORE_UNVERIFIED` | `storage.recovery_required`; dispatcher/worker claim dừng; outbox không replay |
| `VALIDATION_ERROR` | 400 |
| `UNAUTHORIZED` | 401 — sai scheme |
| `NOT_FOUND` | snapshot không tồn tại |
| `STORAGE_WRITE_FAILED` | không ghi restore record |
| `IDEMPOTENCY_CONFLICT` | tạo snapshot trùng key |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC26
- SC27
- SC42
- SC43
- SC12
- SC49
- SC44
- SC53

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/integration/test_wal_unsafe_detected.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_restore_side_effect_lock.py -q` (PROVISIONAL)
- Diễn tập restore thật theo `contracts/ops/backup-restore.md` — **NOT_RUN**

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `a`: sau restore, `COUNT(telegram outbound) = 0` cho tới khi đối soát xong.
- Fixture `d`: bản copy WAL-unsafe bị phát hiện và **từ chối**, không được đánh dấu verified.
- Fixture `e`: `saved_snapshot.content_hash` trước = sau restore.
- Fixture `b`: lease epoch cũ sau restore ⇒ `STALE_LEASE`, 0 commit.

**Evidence artifacts:** log pytest; manifest hash; đếm outbound trước/sau đối soát; dump `restore_record`.

**Yêu cầu live.** Diễn tập restore trên môi trường thật là E2/E3 và cần Owner cho phép; hiện `NOT_RUN`.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ops/backup-restore.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 2 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/http/openapi.yaml`, `contracts/ops/backup-restore.md`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC08-05` còn OPEN: `ENT-restore-record` **không có** trường xác nhận của Operator (`operator_acknowledged_at` / `operator_acknowledgement_ref`) trong khi mệnh đề 7 của `reconciliation_complete` đòi nó. Không tự thêm cột; DỪNG và raise CR. |
| `SG-02` | `data.purge_all` **đã được Owner chốt** (`OD-20260907-01` mục 24): chỉ dữ liệu nghiên cứu; giữ đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch; **backup KHÔNG bị xóa** — điều này trực tiếp chạm card backup. Vẫn không hiện thực purge trong card này. |
| `SG-03` | Không chạy restore trên dữ liệu thật khi chưa có Owner go-ahead và chưa có khóa side effect. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-storage-write-blocked-readiness`
- `TC-telegram-unknown-delivery`
- `TC-saved-snapshot`

## §12. Reviewer scope

Reviewer đọc `contracts/ops/backup-restore.md` (đặc biệt `reconciliation_complete`), `contracts/state/storage.yaml`, 5 fixture recovery/*. Câu hỏi bắt buộc: có đường nào side effect chạy trước khi đối soát xong không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-backup-restore-drill`
- **Vị trí:** `evidence/runs/TC-backup-restore-drill/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
