# HANDOFF — PKT-PC08

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC08` |
| worker principal | `worker-W2` |
| authority_id | `AUTH-COORD-PC08` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC08-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` — không có OS enforcement |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at (UTC) | 2026-09-06T18:03Z |
| finished_at (UTC) | 2026-09-06T18:26Z |
| next actor | `Coordinator` |
| lease_released_at (UTC) | 2026-09-06T18:26Z |

`DONE_WITH_CONCERNS`: mọi write target đã tạo và mọi verification đã chạy đạt, nhưng gói này phát sinh 5 change
request, một **deviation có chủ đích so với văn bản packet** (§6.2) và một mục `OWNER_DECISION_REQUIRED` kế thừa.

PC01 (`modules.yaml`, `capabilities.yaml`, `ports.yaml`, `ops/deployment.md`) **đóng băng** trong packet này —
không có MODIFY nào. Mọi nhu cầu sửa chúng đi qua `CR-PC08-nn`.

## 2. Changes

| Path | Op | Before | After sha256 | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/ops/secrets.md` | CREATE | ABSENT | `4ad6c26af9d14430f3fabd44b38bdc745d9d291ec9f2faf00b960c34ba38ab8d` | 23585 |
| `contracts/ops/internet-boundary.md` | CREATE | ABSENT | `657d9215436ecae4405fcb8bb4160492e9a6ba961ffe7a59178c401d15ef75a5` | 13296 |
| `contracts/ops/backup-restore.md` | CREATE | ABSENT | `412d852ee59e2a84c3b64380199ea3753a55d2533750f94e7447c93e41ef1318` | 22499 |
| `acceptance/fixtures/recovery/README.md` | CREATE | ABSENT | `cd3d243a29bbe3dc3c04d1130e5fc3170286b8e3ce46f2a8a4977d6d3c179c84` | 6157 |
| `acceptance/fixtures/recovery/a-restore-old-outbox-nothing-sent.json` | CREATE | ABSENT | `e7671e7d852f9b0564c5c269df95e598e3de88cdb94142df23a29ee38b543838` | 4194 |
| `acceptance/fixtures/recovery/b-post-restore-stale-lease-rejected.json` | CREATE | ABSENT | `4655e8d95fcc433bba5912c273b0642d4da21e8b730b1c3a046db956e693e88c` | 3455 |
| `acceptance/fixtures/recovery/c-disk-full-mid-ingest.json` | CREATE | ABSENT | `8f6379b4b0c633ca7d3b48be039671b17ece9da58c1f96067003bf2fb0194092` | 3532 |
| `acceptance/fixtures/recovery/d-wal-unsafe-copy-detected.json` | CREATE | ABSENT | `64d11f5541826f64888a29b4fcc97af020715370a3d5237bfc9d371b4367a804` | 3048 |
| `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json` | CREATE | ABSENT | `3630edc83719ada07cae9b39f5da7ad8d1894379509c96bb1128cf958ca6ea0b` | 3462 |
| `acceptance/fixtures/recovery/f-secret-canary-injection.json` | CREATE | ABSENT | `3f3a754bd3aed6b0ce56321584f3eadf17df69b0ff08d2cfaea8a13af6617d15` | 3759 |
| `acceptance/fixtures/recovery/g-ssrf-redirect-private.json` | CREATE | ABSENT | `d5973052f973b738a66c926d98d662e2bb821e7de7e938acbf040f5328dec2ec` | 3265 |
| `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json` | CREATE | ABSENT | `32883c7a2a12b36d964f7974c45952e731f2330cc1416b43c9e4895ae1ad5119` | 4024 |
| `acceptance/fixtures/recovery/i-collector-token-calls-save.json` | CREATE | ABSENT | `e70392d4f34e5bd33bd8e39aad283bdbe136247546fe3292147bc7e5119af6c7` | 4942 |
| `acceptance/fixtures/recovery/j-restore-verification-incomplete-dispatch-locked.json` | CREATE | ABSENT | `b518ea3ac66e00e2c117b6586eadb648746fe71947b0c37a17ab50f81cdf7e82` | 3665 |
| `evidence/handoffs/PC08-handoff.md` | CREATE | ABSENT | (chính file này) | — |

Directory tạo mới: `acceptance/fixtures/recovery/`. Không chạm file của PC00/PC01/PC02/PC03/PC04/PC05 — chúng chỉ
được **đọc**. Không lệnh git mutation. Helper script trong scratch dir, `PYTHONDONTWRITEBYTECODE=1`.

## 3. Baseline upstream đã dựa vào

Kiểm lúc bắt đầu (18:03Z) và lại trước handoff (18:24Z).

| Ref | Path | SHA-256 | Ghi chú |
| --- | --- | --- | --- |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | không đổi |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | không đổi |
| PC01 | `contracts/modules.yaml` | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` | post-FIX2, frozen |
| PC01 | `contracts/capabilities.yaml` | `c54cdaaf85be339aff5823902c9cb27a2aa25ebea61c241f1b76d2999e6ea7ab` | post-FIX2, frozen |
| PC01 | `contracts/ports.yaml` | `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` | post-FIX2, frozen |
| PC01 | `contracts/ops/deployment.md` | `4d879f2be6187623410bca378b34fc9aa38771b72e70ba309b8edef04a0f1295` | post-FIX2, frozen |
| PC02 | `contracts/data/entities.yaml` | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | 59 entity |
| PC03 | `contracts/state/storage.yaml` | `608ceea67834be427013d252ea35e7798be9ae56586b7174004fe4f12078eb0b` | |
| PC03 | `contracts/state/run.yaml` | `8acb7bbf935ee6854fa41d52604972929f09843838c1c141d861d17f538f3468` | |
| PC03 | `contracts/state/delivery.yaml` | `9fcccc25fed432a895b15e9b98787d7294dd298d9209e9b0f2c7f801e1579626` | |
| PC03 | `contracts/errors.yaml` | `e236aaee44cb340bf58ab822ab3dc434847e3d777b46c5b97b3baf00bd0e1b37` | 26 mã |
| PC03 | `contracts/retry-policy.yaml` | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` | |
| PC05 | `contracts/http/openapi.yaml` | `6d9a8c506d35fcec6b1e8746bf6ed1400e66723e89dde18fc54780f78acb2d86` | **xuất hiện giữa chừng**; EV-02 chạy được nhờ vậy |
| PC00 | `precode/adr/ADR-0005-backup-method.md`, `ADR-0010-secret-scoping-and-cli-isolation.md`, `precode/requirements.csv` | đọc, không ghi | REQ-ID lấy từ đây |

PC06 (`contracts/ai/providers.yaml`) và PC07 (`contracts/telegram/commands.yaml`) **chưa tồn tại** lúc viết; được
trích theo đường dẫn đã lên kế hoạch, đúng quy định của packet.

## 4. Evidence records

### EV-PC08-01 — Fixture + trích dẫn chéo (packet EV-01)

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC08-01` · producer `worker-W2` · type `SELF_VALIDATION` |
| command | `python3 …/scratchpad/w2/validate_pc08.py` |
| runtime | python3 3.12.3, PyYAML 6.0.1, `PYTHONDONTWRITEBYTECODE=1` |
| started/ended | 2026-09-06T18:24Z / 18:24Z |
| inputs | 10 fixture JSON + 4 markdown của PC08; upstream ở §3 |
| oracle | 8 khẳng định, 0 vi phạm |
| observed | **EV-01a** 10/10 fixture parse JSON · **EV-01b** 10/10 mang header baseline §3 (`x-contract`, đủ 14 trường, `claim_ceiling: DRAFT_FOR_REVIEW`) và đủ `given`/`events`/`expected`/`forbidden_effects`/`oracle_vi`/`scenario_refs`/`invariant_refs` · **EV-01c** README liệt kê đủ 10 file · **EV-01d** 33/33 event: `actor` là caller được khai của operation và bộ ba `(actor, owner_module, operation)` khớp `allowed_edges`, trong đó **2** event mang `edge_assertion: forbidden` và được xác nhận là **không** có trong `allowed_edges` · **EV-01e** 36 `operation_id` được trích đều tồn tại trong `ports.yaml` · **EV-01f** 11 mã lỗi được trích đều tồn tại trong `errors.yaml` · **EV-01g** 28 tên entity được trích đều tồn tại trong `entities.yaml` · **EV-01h** mọi giá trị `storage.health` được trích tồn tại trong `state/storage.yaml` |
| exit code | 0 |
| status | `PASS` |
| limitations | E0 tĩnh. Không fixture nào **được chạy**: không có code, không harness mạng, không DB. Việc một fixture nhất quán với registry **không** chứng minh guard nào chạy. |

### EV-PC08-02 — Đối chiếu cơ chế xác thực với PC05 (packet EV-02)

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC08-02` · type `SELF_VALIDATION` |
| command | phần `EV-02` trong cùng script |
| inputs | `contracts/http/openapi.yaml` sha256 `6d9a8c50…`, `contracts/ops/secrets.md` |
| oracle | Sáu `components.securitySchemes` của PC05 phải có mặt **và** được `secrets.md` gọi đúng tên |
| observed | PC05 khai `ownerSessionCookie`, `ownerCsrfToken`, `collectorToken`, `analysisWorkerToken`, `telegramIngressSecret`, `backupOperatorToken`. Cơ chế **hội tụ** với lựa chọn của packet: cookie HttpOnly + CSRF double-submit cho UI, bearer cho collector/worker, header bí mật cho Telegram. `secrets.md` §2.3 dùng đúng sáu tên đó và đúng tên cookie `rr_session` / `rr_csrf`. |
| exit code | 0 · status `PASS` |
| limitations | Kiểm **tên và cơ chế**, không kiểm từng route có gắn đúng scheme. Một khác biệt về **mã lỗi** vẫn còn (§6.1 `CR-PC08-03`). Packet dự trù EV-02 có thể `NOT_RUN`; nó chạy được vì PC05 landing giữa chừng. |

### EV-PC08-03 — Đối chiếu thủ công trường manifest với entity (packet EV-03)

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC08-03` · type `SELF_VALIDATION` · thủ công, có hỗ trợ script in danh sách trường |
| inputs | `entities.yaml` `2235564f…`: `backup_manifest`, `backup_snapshot`, `restore_record`, `outbox_intent`, `embedding_generation` |
| status | `PASS_WITH_GAPS` (xem cột kết quả) |

| Trường manifest (backup-restore.md §3) | Chỗ chứa trong entity | Kết quả |
| --- | --- | --- |
| `artifact_sha256`, `method`, `started_at`, `completed_at`, `schema_migration_version` | `backup_snapshot.*` | khớp trực tiếp |
| `manifest_sha256`, `counts` | `backup_manifest.manifest_sha256`, `.counts` | khớp trực tiếp |
| `app_version`, `contract_versions`, bản xuất `settings` không secret, con trỏ kế hoạch khôi phục secret, phạm vi loại trừ | `backup_manifest.entries` (json) | **chứa được** trong `entries`; không có trường riêng — chấp nhận được vì `entries` là json có chủ đích |
| embedding: `model_name`, `model_version`, `dimension`, `normalization`, `expected_vector_count`, `built_vector_count`, `id` | `embedding_generation.*` | khớp **đủ 7/7** |
| embedding: **đường dẫn + sha256 của artifact model** | *không có trường entity nào* | **GAP** — chỉ nằm trong `backup_manifest.entries`. Không chặn, nhưng nghĩa là hệ thống không biết hash model đang chạy ngoài lúc backup → `CR-PC08-05` |
| `restore_record`: `new_restore_generation`, `integrity_check_outcome`, `counts_observed`, `leases_revoked`, `dispatcher_unlocked_at` | khớp trực tiếp | phủ mệnh đề 1, 2, 3 của `reconciliation_complete` |
| **xác nhận của Operator** (mệnh đề 7 của `reconciliation_complete`) | *không có trường entity nào* | **GAP** — `restore_record` không có `operator_acknowledged_at`/`by`. Mệnh đề 7 hiện không lưu được → `CR-PC08-05` |
| `outbox_intent.restore_generation` | khớp trực tiếp | là cơ sở của quy tắc §5.5 (CR-PC02-07) |

### Không chạy

| Hạng mục | Trạng thái |
| --- | --- |
| Restore drill thật (E2/E3) | `NOT_RUN` — packet cấm chạy; bằng chứng live thuộc giai đoạn triển khai |
| Backup thật, integrity check thật | `NOT_RUN` |
| Kiểm SSRF/egress bằng mạng thật | `NOT_RUN` |
| Mọi oracle `NB-01…NB-08` của `internet-boundary.md` §7 | `NOT_RUN` |
| Independent audit | `NOT_RUN` — `audit_route: INDEPENDENT_REQUIRED`; đây là `SELF_VALIDATION` |
| Các số PROVISIONAL (Argon2id, 12 h/30 d, 900 s, RPO 24 h, RTO 2 h, retention 14/8/∞, redirect 3, 10 MiB…) | `NOT_RUN` — chưa đo trên hệ thật |

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Một tài khoản, không signup; session expiry/revocation; bảo vệ owner API; CSRF nếu cookie; scope/rotation token collector | `DONE` | `secrets.md` §2.1–2.4 (Argon2id; cookie `rr_session` HttpOnly+Secure+SameSite=Lax; idle 12 h / absolute 30 d; CSRF double-submit; rate limit 5/15 phút, lockout 15 phút), §3 (hai token tách rời, `0600`, rotation 180 ngày, overlap 24 h, chống replay bằng `request_id`/`lease_epoch`); fixture `h`, `i` |
| 2 | Lưu trữ secret/key-at-rest, phân phối tới worker, Chrome debug loopback, profile ngoài backup server | `DONE` | `secrets.md` §4 (envelope AEAD 256-bit, master key ngoài DB), §5 (credential theo task, TTL 900 s = `lease_ttl_analysis`, chỉ trong RAM), §6 (loopback, profile ngoài backup); `backup-restore.md` §6 |
| 3 | Chính sách fetch URL, chặn redirect tới địa chỉ nội bộ, an toàn render, cấm tool access từ nội dung | `DONE` | `internet-boundary.md` §2 (egress theo module), §3 (scheme/host allowlist, chặn dải nội bộ theo **IP đã phân giải**, chống DNS rebinding, redirect ≤ 3 kiểm lại từng bước, timeout 10/30 s, 10 MiB), §5 (render), §6 (tool); fixture `f`, `g` |
| 4 | Backup khi DB hoạt động, nội dung manifest, artifact/cấu hình embedding, kế hoạch khôi phục secret, retention | `DONE` | `backup-restore.md` §1 (vì sao copy file không đủ, có trích SQLite WAL/Backup API), §2 (phương pháp + lịch + retention), §3 (manifest + **oracle 3 điều kiện**), §6 (những gì không nằm trong backup) |
| 5 | Runbook restore với integrity check, counts/hash, thu hồi lease, khóa dispatch tới khi đối soát xong | `DONE` | `backup-restore.md` §5.1–5.7, đặc biệt §5.2 (thứ tự 8 bước, lease thu hồi **trước** khi dispatcher mở) và §5.6 (vị từ `reconciliation_complete` 7 mệnh đề); fixture `a`, `b`, `j` |
| 6 | RPO/RTO, disk-full/readiness, audit retention; không suy diễn transaction phủ được lỗi phần cứng | `DONE` | `backup-restore.md` §4 (RPO 24 h, RPO Saved tách riêng, RTO 2 h, **không** có deadline tự động), §7 (disk-full), §9 (mất gì); `secrets.md` §8 (audit retention 365 ngày / vô thời hạn cho xóa). Câu "transaction không bảo vệ trước hỏng ổ đĩa" ghi rõ ở §4 |

### CR-PC02-07 (được giao cho gói này)

| Phần | Đáp ứng ở đâu |
| --- | --- |
| `outbox_intent.restore_generation` | `backup-restore.md` §5.5: dispatcher **chỉ** gửi intent có `restore_generation == generation hiện tại`; intent khôi phục từ snapshot luôn mang generation cũ hơn ⇒ I15 trở thành một phép so sánh số, không phải một lời hứa. Nâng generation cho một intent cũ là quyết định của Operator, từng cái một. Fixture `a` kiểm điều này. |
| Thu hồi lease **trước** khi dispatcher mở | `backup-restore.md` §5.2: thứ tự 8 bước bắt buộc, `restore_record.leases_revoked`, tăng `lease_epoch`, worker cũ nhận `STALE_LEASE`. Fixture `b`. |
| Oracle của snapshot manifest | `backup-restore.md` §3: ba điều kiện (sha256 artifact, `PRAGMA integrity_check`, **counts khớp từng khóa**). Điều kiện thứ ba là thứ phát hiện bản copy WAL-unsafe mà hai điều kiện đầu bỏ lọt. Fixture `d`. |

### Interface PC03 yêu cầu

`storage.yaml.post_restore_reconciliation_gate.interface_contract_vi` đòi một vị từ boolean không side effect.
Đã cung cấp: `backup-restore.md` §5.6 `reconciliation_complete(restore_id)` với 7 mệnh đề, chỉ đọc;
`backup.reconcile_after_restore` chỉ chuyển `storage.health = healthy` khi vị từ đúng, sai thì trả
`RESTORE_UNVERIFIED` **kèm mệnh đề nào chưa đạt** (fixture `j` kiểm điều này).

### Invariants

| Invariant | Positive | Counterexample |
| --- | --- | --- |
| I01 | fixture `i` seq3 (đường ingest hợp lệ commit bình thường) | fixture `h` (không xác thực, thiếu CSRF), `i` seq1/seq2 (token đúng, cạnh sai) |
| I11 | `internet-boundary.md` §2 (egress đúng module) | fixture `f` (canary + injection), `g` (SSRF redirect) |
| I15 | fixture `e` (hash Saved giữ nguyên qua backup→restore→reconcile) | fixture `a` (outbox cũ không gửi), `b` (lease cũ bị từ chối), `j` (đối soát dở dang) |

## 6. Unresolved refs

### 6.1 Change requests

| ID | Gửi tới | Nội dung | Trạng thái |
| --- | --- | --- | --- |
| `CR-PC08-01` | PC00 / PC09 | Đăng ký anchor cho `SC39` (SSRF redirect nội bộ), `SC40` (request không xác thực / thiếu CSRF), `SC41` (token hợp lệ đi sai cạnh), `SC42` (đối soát chưa xong ⇒ dispatch khóa), `SC43` (backup WAL-unsafe bị phát hiện). PC08 lấy dải SC39+ vì PC03 dùng tới SC36 và PC04 tới SC38. | OPEN |
| `CR-PC08-02` | PC05 | Đã **hết hiệu lực một phần**: openapi landing và hội tụ. Còn lại: xác nhận mọi route mutation của owner gắn **cả** `ownerSessionCookie` **và** `ownerCsrfToken`, và route `backup.*` gắn `backupOperatorToken` — PC08 chỉ kiểm tên scheme, không kiểm từng route. | OPEN |
| `CR-PC08-03` | PC03 + PC05 | `openapi.yaml` ánh xạ **thiếu/lệch CSRF ⇒ 403 `FORBIDDEN_EDGE`**, nhưng `errors.yaml` định nghĩa `FORBIDDEN_EDGE` là "cạnh caller→callee không có trong `modules.yaml`". Request thiếu CSRF đi qua **đúng** cạnh; cái sai là bằng chứng ý định của người dùng. Đề nghị: mở rộng định nghĩa, hoặc dùng mã khác cho CSRF. PC08 tạm theo PC05 để không tạo mâu thuẫn thứ hai. | OPEN |
| `CR-PC08-04` | Coordinator | Chọn **một** mã cho "token hợp lệ nhưng đi cạnh không được phép" (collector gọi `save.create`). Ba nguồn đã đóng băng nói `UNAUTHORIZED` (`modules.yaml` NC-01/NC-02; oracle của `UNAUTHORIZED` trong `errors.yaml` nêu đích danh NC-01; mô tả `collectorToken` trong `openapi.yaml` nói 401); văn bản packet PC08 nói `403 FORBIDDEN_EDGE`. Xem §6.2. | OPEN |
| `CR-PC08-05` | PC02 | Hai gap của EV-PC08-03: (a) `restore_record` **không có** trường lưu xác nhận của Operator, trong khi mệnh đề 7 của `reconciliation_complete` đòi nó — đề nghị thêm `operator_acknowledged_at` + `operator_acknowledgement_ref`; (b) không entity nào lưu **hash artifact model embedding** đang chạy (chỉ có trong `backup_manifest.entries`) — đề nghị thêm vào `embedding_generation` để đối chiếu được ngoài lúc backup. | OPEN |

### 6.2 Deviation có chủ đích so với văn bản packet

Packet mô tả fixture (i) là "collector token used to call Save → **403 FORBIDDEN_EDGE**". Fixture
`i-collector-token-calls-save.json` khẳng định **`UNAUTHORIZED`**.

Lý do: ba file upstream đã đóng băng và **thống nhất** ở `UNAUTHORIZED` — `modules.yaml` NC-01/NC-02
(`expected_error_code: UNAUTHORIZED`), `errors.yaml` (oracle của `UNAUTHORIZED` nêu đích danh NC-01/NC-02/NC-03/NC-09),
và `openapi.yaml` (mô tả `collectorToken`: gọi `save.create` bằng token này ⇒ 401). PC08 không được sửa ba file đó;
tạo một oracle mâu thuẫn với chúng sẽ nhân bản đúng lớp lỗi mà `F-A1R1-01` đã phạt ở vòng audit trước (một hành vi,
nhiều mô tả). Thêm nữa `errors.yaml` tự ghi rằng `FORBIDDEN_EDGE` **chưa** được `ports.yaml`/`modules.yaml` tham
chiếu ở bản 0.1.0 (`CR-PC03-04`).

Deviation được ghi **trong chính fixture** (khối `packet_deviation`) kèm kỳ vọng thay thế nếu Coordinator chọn
`FORBIDDEN_EDGE`. Ca này thỏa **cả hai** mô tả (token sai scope **và** cạnh không có trong `allowed_edges`); chọn
mã nào là quyết định của Coordinator, và nếu chọn `FORBIDDEN_EDGE` thì NC-01/NC-02 và oracle của `errors.yaml`
phải đổi theo — không phải chỉ fixture này.

### 6.3 Quyết định PROVISIONAL do PC08 đưa ra

Toàn bộ mang nhãn `PROVISIONAL`, có đơn vị và một dòng lý do tại chỗ; chưa cái nào được đo trên hệ thật:
Argon2id (64 MiB / t=3 / p=1); session idle 12 h, absolute 30 d, CSRF 128 bit; login 5 lần/15 phút, lockout
15 phút; token worker 256 bit, `0600`, rotation 180 ngày, overlap 24 h; `task_credential_ttl` 900 s (buộc bằng
`lease_ttl_analysis` của PC03 — nếu PC03 đổi số đó, số này phải đổi theo); AEAD 256-bit + master key ngoài DB;
audit retention 365 ngày / vô thời hạn cho bản ghi xóa; backup 03:00 hằng ngày, timeout 600 s, retention 14 daily
/ 8 weekly / monthly vô thời hạn; RPO 24 h, RTO 2 h; redirect ≤ 3, timeout 10 s/30 s, body ≤ 10 MiB.

### 6.4 Kế thừa, không giải quyết trong gói này

- `PROV-PC01-03`: danh sách **loại trừ** của `data.purge_all` (settings, secrets, credential đăng nhập,
  `telegram_link`, `schema_migration`) vẫn `OWNER_DECISION_REQUIRED`. `secrets.md` §9 và `backup-restore.md` §8 chỉ
  ghi **hệ quả vận hành** — trong đó điểm cần Owner biết: nếu purge xóa credential đăng nhập thì phải có đường đặt
  lại tại chỗ, nếu không chủ nhà tự khóa mình ra ngoài app.
- Dữ liệu đã purge **vẫn còn** trong artifact backup cho tới khi những bản đó bị xóa; muốn "xóa hẳn" phải xóa cả
  backup — một thao tác riêng (`backup-restore.md` §8).
- PC06/PC07 chưa tồn tại: `internet-boundary.md` §5–6 và `secrets.md` §7 trích theo đường dẫn kế hoạch. Khi hai gói
  đó landing, cần một lượt đối chiếu (không thuộc packet này).

## 7. Trạng thái partial

Không có partial write. 14 file được tạo trọn vẹn và đã hash sau khi ghi (§2). Không rollback.

## 8. Giới hạn của bàn giao

- Claim tối đa `DRAFT_FOR_REVIEW`. Bằng chứng duy nhất là `SELF_VALIDATION` mức E0.
- **Không có drill restore nào đã chạy.** `backup-restore.md` là thiết kế đã viết ra, không phải bằng chứng rằng
  restore hoạt động — điều này được ghi ngay trong file (§5.7, §9) để người đọc runbook không hiểu nhầm.
- Hash của một artifact backup **không** chứng minh nó khôi phục được; chỉ một drill thật mới chứng minh.
- Fixture nhất quán với registry **không** chứng minh guard nào chạy; 10 fixture đều `NOT_RUN`.

---

**Addendum PKT-PC01-FIX4 (một dòng, `CR-PC01-08`):** `contracts/ops/secrets.md` được sửa dưới lease
`LEASE-PC01-e5` — `4ad6c26af9d14430f3fabd44b38bdc745d9d291ec9f2faf00b960c34ba38ab8d` / 23585 B →
`774a1130fa398602b4f0eb02334212cc2c762eaee95d172dd804a8b099344802` / 24343 B: bỏ sha256 đã cũ của
`contracts/http/openapi.yaml` (W4 đang sửa file đó song song), thay bằng trích dẫn "bản đóng băng ở FC-W3" + tên
sáu security scheme kèm lý do; đồng thời ghi nhận `CR-PC08-03` đã đóng nhờ mã `CSRF_REJECTED` được đăng ký trong
`contracts/errors.yaml` (`f503cbf17a8503a4c95b6eae94755c0fab5acd3fc9cb5ef6a088c584d1b3b5cf`, 28 mã).
`python3 …/w2/validate_pc08.py` chạy lại sau thay đổi: **exit 0**. Chi tiết ở addendum PKT-PC01-FIX4 của
`evidence/handoffs/PC01-handoff.md`.

---

# ADDENDUM — PKT-PC08-FIX1

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC08-FIX1` · authority `AUTH-COORD-PC08-FIX1` · lease `LEASE-PC08-e2` (fencing 2) |
| expires_at | 2026-09-07T08:00Z |
| trigger | Rulings FIX4 **R4-01** (quy ước chú thích fixture) và **R4-02** (khóa event + marker cạnh âm) |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-06T18:55Z / 2026-09-06T19:02Z |
| next actor | `Coordinator` · lease_released_at 2026-09-06T19:02Z |

## F.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `acceptance/fixtures/recovery/README.md` | MODIFY | `cd3d243a29bbe3dc3c04d1130e5fc3170286b8e3ce46f2a8a4977d6d3c179c84` / 6157 | `968e90643a03e5684184323d390c48c14aa085f5f1ea8d1c2e67731157254f7b` / 9199 |
| `acceptance/fixtures/recovery/*.json` (10 file) | **NO CHANGE** | — | hash không đổi so với PC08 gốc (§2 của handoff này) |

Không file nào của gói khác bị chạm; chỉ **đọc** để chạy gate. Sources `f65bb046…`/`d35e1f2d…` không đổi.

## F.2 Nội dung

**R4-01 — README nêu nguyên văn quy tắc.** Thêm một mục nêu **nguyên văn** quy tắc ba loại khóa hợp lệ dưới
`given.rows.<entity>[]` / `expected.rows.<entity>[]`: (a) cột tồn tại trong `entities.yaml`, (b) chú thích có tiền
tố `_`, (c) cột mang `pending_cr: CR-…` trong file; không allowlist theo gói. Kèm một câu **vì sao**: khóa trần
trông y hệt cột thật, nên một fixture nhắc tới cột không tồn tại vẫn đọc như oracle chạy được; tiền tố `_` làm ý
định "đừng tra schema" kiểm được bằng máy.
Ghi rõ **trạng thái của thư mục recovery**: các fixture ở đây mô tả trạng thái bằng `given`/`expected` **dạng tự
do**, không dùng cấu trúc `rows.<entity>[]`, nên **0 cột thuộc phạm vi quy tắc và 0 chưa giải quyết** — khớp đúng
điều audit đã quan sát. README nói thêm rằng quy tắc áp dụng ngay nếu về sau có fixture chuyển sang dạng `rows`,
để không ai hiểu nhầm đây là miễn trừ.

**R4-02 — marker cạnh âm được ratify.** README nay mô tả `edge_assertion: forbidden` là dấu chuẩn, và nêu **cả
hai** điều kiện mà gate `fixture-actor-edge` kiểm: bộ ba `(actor, owner_module, operation)` **không** có trong
`allowed_edges`, **và** `expected` chứa một trong ba mã hợp lệ cho ca âm — `UNAUTHORIZED`, `FORBIDDEN_EDGE`,
`CAPABILITY_DENIED`. Thêm câu cấm lối thoát dễ dãi: nếu bộ ba lại **có** trong `allowed_edges` thì phải báo, không
được lặng lẽ đổi marker cho qua gate. Khóa event là `operation` (không phải `operation_id`) được nêu thành một
dòng riêng.
Thêm bảng liệt kê **hai** event `forbidden` của thư mục này (cả hai trong `i-collector-token-calls-save.json`:
`save.create` và `tag.update` từ `MOD-x-collector`), mã mong đợi `UNAUTHORIZED` cho cả hai, kèm lý do ba nguồn
upstream đã đóng băng ở mã đó và con trỏ tới khối `packet_deviation` / `CR-PC08-04`.

**Kiểm khóa event:** cả 33 event của 10 fixture recovery dùng khóa `operation`; **0** chỗ dùng `operation_id`.
Không cần rename gì — xác nhận bằng script, không bằng đọc.

## F.3 Gate

`python3 …/scratchpad/w2/gate_fixtures.py` — cài đặt đúng R4-01 + R4-02 trên **cả sáu** thư mục fixture,
chạy 2026-09-06T19:01Z, đối chiếu `contracts/data/entities.yaml`
sha256 `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece`. **Exit code 0.**

| Thư mục | Files | Events | Columns kiểm | Chú thích `_` | `pending_cr` | Event `forbidden` |
| --- | --- | --- | --- | --- | --- | --- |
| `ai` | 11 | 27 | 40 | 0 | 0 | 0 |
| `collection` | 8 | 27 | 0 | 0 | 0 | 0 |
| `identity` | 14 | 24 | 404 | 52 | 0 | 0 |
| **`recovery`** | **10** | **33** | **0** | **0** | **0** | **2** |
| `reporting` | 13 | 52 | 388 | 24 | 0 | 0 |
| `telegram` | 18 | 40 | 238 | 24 | 0 | 0 |
| **TOTAL** | **74** | **203** | **1070** | **100** | **0** | **2** |

**Unresolved columns: 0. Event/edge problems: 0.**

Ghi trung thực về thời điểm: lần chạy **đầu** của gate (18:56Z) báo **80** cột chưa giải quyết trong `identity` và
`telegram`, và 27 event dùng `operation_id` trong `collection`. Đó là công việc R4-01/R4-02 của PC02/PC05/PC07,
**không** phải của PC08, và nó đã landing trong khoảng 18:56–19:01Z; lần chạy cuối cho 0/0. Con số trong bảng gắn
với hash `entities.yaml` nêu trên; nếu gói khác còn sửa tiếp thì phải đo lại. PC09 `e0_check.py` chạy độc lập phải
ra cùng bộ số này — nếu lệch, một trong hai cài đặt sai và cần đối chiếu.

`python3 …/scratchpad/w2/validate_pc08.py` (gate riêng của PC08) chạy lại sau khi sửa README: **exit 0** — 10
fixture vẫn parse, header đầy đủ, README vẫn liệt kê đủ 10 file, 33/33 event khớp `allowed_edges`, mọi trích dẫn
operation/mã lỗi/entity/state vẫn resolve.

## F.4 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| Fixture recovery không dùng cấu trúc `rows.<entity>[]` nên gate R4-01 kiểm **0 cột** ở đây. Đó là lý do thư mục này sạch, **không** phải bằng chứng rằng nó đã được kiểm ở mức cột. Nếu Coordinator muốn recovery cũng chịu kiểm cột thì phải chuyển `given`/`expected` sang dạng `rows` — một packet riêng, và sẽ đụng tới oracle của cả 10 fixture. | OPEN |
| `CR-PC08-04` (mã lỗi cho "token hợp lệ, cạnh sai") vẫn chờ ruling. README nay mô tả trạng thái hiện tại (`UNAUTHORIZED`) và nơi ghi deviation; nếu ruling đổi sang `FORBIDDEN_EDGE` thì sửa cả README lẫn fixture `i`. | OPEN |
| Mọi fixture vẫn `NOT_RUN`. Gate chứng minh **tính nhất quán của mô tả**, không chứng minh guard nào chạy. | — |

---

# ADDENDUM — PKT-PC08-FIX2

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC08-FIX2` · authority `AUTH-COORD-PC08-FIX2` · lease `LEASE-PC08-e3` (fencing 3) |
| expires_at | 2026-09-07T12:00Z |
| trigger | Rulings FIX5 **R5-05** (mã lỗi nhất quán), **R5-02** (fixture SC32/SC44/SC53), **R5-03** (REQ-S11.2-05/-06) |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T00:24Z / 2026-09-07T00:28Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T00:28Z |

## G.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `acceptance/fixtures/recovery/README.md` | MODIFY | `968e90643a03e5684184323d390c48c14aa085f5f1ea8d1c2e67731157254f7b` / 9199 | `8c260b2e6a40602079397319c5c9058fb496306c3cc2f55e473b7ce6c9b72e1a` / 10906 |
| `acceptance/fixtures/recovery/i-collector-token-calls-save.json` | MODIFY | `e70392d4f34e5bd33bd8e39aad283bdbe136247546fe3292147bc7e5119af6c7` / 4942 | `78e6e6ee47008b5d9b44dbdf65994f93c7ce89ee33ef7f96e7699ee7e0372886` / 5229 |
| `contracts/ops/internet-boundary.md` | MODIFY | `657d9215436ecae4405fcb8bb4160492e9a6ba961ffe7a59178c401d15ef75a5` / 13296 | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` / 13926 |
| `acceptance/fixtures/recovery/k-delete-target-preserves-saved.json` | CREATE (ABSENT) | — | `0a02102333a7701b92c2b1c5b22032940cc0710d8b5faf98d67181ac16606486` / 8045 |
| `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` | CREATE (ABSENT) | — | `e144d0ce7b26f45825c8b1c72621d925336dd5b0ac8acbee77a48d05e1fd8bed` / 7790 |
| `acceptance/fixtures/recovery/m-post-restore-reconciled-dispatch-reopens.json` | CREATE (ABSENT) | — | `90934af96aa37ea8917dbd581247afa05655be3e23fc77b4004c1c9227b4be94` / 7808 |
| `contracts/ops/secrets.md` | **NO CHANGE** | `774a1130fa398602b4f0eb02334212cc2c762eaee95d172dd804a8b099344802` | đã cite `REQ-S11.2-05` và `-06` từ bản gốc PC08; grant không cần dùng |
| `evidence/handoffs/PC08-handoff.md` | MODIFY (append) | `d6f5c8ccd7e9853e2a0da1e9ba6bbfb96f54b0f8283952a86e5803518056e564` / 29113 | ghi ở thông điệp bàn giao |

Sources không đổi (00:24Z và 00:27Z). Không chạm file của gói khác.

## G.2 R5-05 — mã lỗi nhất quán

Ba chỗ còn nói `FORBIDDEN_EDGE` cho ca "collector token gọi Save / sửa tag" đã đổi sang **`UNAUTHORIZED`**:
`oracle_vi` của fixture `i` (chỗ nguy hiểm nhất — một harness đọc `oracle_vi` sẽ khẳng định sai mã), dòng bảng
danh mục của README, và dòng `SC41` trong bảng scenario. `expected` của fixture `i` **đã** là `UNAUTHORIZED` từ
FIX1, nên trước FIX2 file tự mâu thuẫn giữa `expected` và `oracle_vi`. Nay ba nguồn nói cùng một mã, và cả ba dẫn
về `NC-01`/`NC-02`, oracle của `UNAUTHORIZED` trong `errors.yaml`, và mô tả `collectorToken` trong `openapi.yaml`.
Khối `packet_deviation` giữ nguyên để `CR-PC08-04` vẫn truy được.

## G.3 R5-02 — ba fixture mới, dạng `rows.<entity>[]`

| File | SC | Nội dung |
| --- | --- | --- |
| `k-delete-target-preserves-saved.json` | SC32 | Ca âm thiếu cờ xác nhận (`VALIDATION_ERROR`, 0 hàng bị xóa) rồi ca hợp lệ: `work`/`post_work`/`analysis` bị xóa; `saved_item`, `saved_snapshot` (hash **không đổi**), `first_announced_ledger` và `report_item` **giữ nguyên**; một hàng `data_deletion_audit` với `deleted_counts` và `preserved_counts` |
| `l-purge-all-two-phase-and-negatives.json` | SC44 | Pha 1 phát challenge (lưu `phrase_hash`, không bản rõ); **bốn ca âm** — cụm từ sai (`VALIDATION_ERROR`), `storage.health = healthy` (`CONFLICT`), principal không phải owner (`UNAUTHORIZED`, `edge_assertion: forbidden`), dùng lại challenge đã `consumed` (`CONFLICT`) — và ca hợp lệ trong `maintenance`: `assignment_lease` chuyển `revoked` **trước** khi xóa, hệ thống **ở lại** `maintenance` |
| `m-post-restore-reconciled-dispatch-reopens.json` | SC53 | Mặt **dương** của I15: cả bảy mệnh đề đạt (gồm `operator_ack_at`/`_principal`/`_note` mà PC02 đã thêm theo `CR-PC08-05`) → `storage.health = healthy`, claim chạy lại, nhưng `outbox_intent` mang `restore_generation = 6 < 7` vẫn **không** được gửi |

Cả ba dùng `given.rows.<entity>[]` / `expected.rows.<entity>[]` nên field gate **không rỗng**: recovery đóng góp
**175 cột thật** (trước FIX2 là 0) và **28 chú thích `_`**. Gate bắt được một lỗi thật khi tôi viết: hàng `analysis`
dùng `state` trong khi entity có `status` — đúng lớp lỗi mà `F-A1R2-03` phạt ở vòng trước. Đã sửa thành `status`
cộng `target_kind`/`target_work_id`.

**Một điều cố ý không khẳng định:** trong `l`, `deleted_counts` cho `settings`, `secret_ref`, credential đăng nhập,
`telegram_link` và `schema_migration` bị **bỏ trống**, vì danh sách loại trừ của `data.purge_all` vẫn
`OWNER_DECISION_REQUIRED` (`PROV-PC01-03`). Điền số vào đó là tự quyết thay Owner. README nói rõ điều này.

## G.4 R5-03 — requirement refs

`contracts/ops/internet-boundary.md` thêm `REQ-S11.2-05` vào `requirement_refs` và một đoạn ở §5 nói che secret
trước khi ghi log áp cho cả ba đường ra Internet mà file này quản (research connector, AI adapter, Telegram
adapter), trỏ mẫu che sang `secrets.md` §4.3, và nhắc `REQ-S11.2-06` (Chrome debug loopback) đã có ở bảng ingress
§4. `secrets.md` **không cần sửa**: cả hai id đã nằm trong `requirement_refs` từ bản gốc.

## G.5 Gate

| Gate | Kết quả |
| --- | --- |
| `validate_pc08.py` | **exit 0** — 13 fixture parse, đủ header, README liệt kê **13/13**, **48/48** event khớp `allowed_edges` (3 event `forbidden` có chủ đích), 37 operation id, 13 mã lỗi, 28 entity name, mọi `storage.health` state đều resolve |
| `gate_fixtures.py` (tám thư mục, R4-01 + R4-02) | **exit 0** — 86 file · 318 event · **1939 cột** · 179 chú thích `_` · 0 `pending_cr` · 34 event `forbidden` · **unresolved 0** · **event/edge problem 0**. Riêng `recovery`: 13 file, 48 event, **175 cột**, 28 chú thích, 3 forbidden |
| `evidence/tools/e0_check.py` (copy read-only) | `E0-03-fixture-schema` PASS 28/0 · `E0-08-contract-header` PASS 142/0 · `E0-14-fixture-actor-edge` **PASS 449/0**. Tổng 19 check: PASS 18, FAIL 1 |

Hai lỗi do chính tôi tạo ra và tự bắt được trước khi bàn giao, ghi lại vì chúng cho thấy gate đang làm việc:
(1) hàng `analysis` dùng cột `state` không tồn tại — field gate bắt; (2) placeholder `<HASH_PHRASE>`, `<H_MODEL>`…
bị bộ dò mã lỗi của tôi hiểu nhầm là mã lỗi chưa đăng ký. Sửa placeholder thành chữ thường **và** dạy script bỏ
qua `<...>` — sửa cả hai phía vì chỉ sửa một phía sẽ để lớp lỗi này quay lại.

## G.6 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `E0-07-id-refs` FAIL (2 vi phạm) | `SC54` chưa định nghĩa trong `acceptance/scenarios.yaml`, bị trích ở `PC00-handoff.md` **và** ở `PC01-handoff.md` — chỗ thứ hai là do addendum FIX7 của tôi **báo cáo** khiếm khuyết đó. Bộ kiểm coi mọi lần nhắc là một citation, nên **việc báo lỗi tự tạo ra lỗi**. Đề nghị: hoặc W1 định nghĩa SC54, hoặc `E0-07` bỏ qua văn bản trong handoff nói *về* một id chưa định nghĩa. Tôi không sửa được: `PC01-handoff.md` ngoài grant của packet này và lease FIX7 đã released. | OPEN |
| `PROV-PC01-03` | Danh sách loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`; fixture `l` cố ý để trống phần đó. Khi Owner trả lời, `l` phải được bổ sung. | OPEN |
| `CR-PC08-04` | Mã cho "token hợp lệ, cạnh sai" vẫn chờ ruling; nay ba nguồn của tôi đã thống nhất ở `UNAUTHORIZED`. | OPEN |
| `CR-PC08-05` | **Đóng.** PC02 đã thêm `operator_ack_at`/`_principal`/`_note` vào `restore_record` và `embedding_model_artifact_sha256` vào `backup_manifest`; fixture `m` dùng đúng các cột đó. | CLOSED (chờ xác nhận) |
| Mọi fixture vẫn `NOT_RUN` | 13 fixture recovery là dữ liệu vào và oracle. Không drill restore nào đã chạy; `backup-restore.md` §5.7/§9 vẫn là thiết kế, không phải bằng chứng. | — |

---

# ADDENDUM — PKT-PC08-FIX3

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC08-FIX3` · authority `AUTH-COORD-PC08-FIX3` · lease `LEASE-PC08-e4` (fencing 4) |
| expires_at | 2026-09-07T18:00Z |
| trigger | `E0-04c-prose-column-tokens` (run `E0-20260907T014517Z`) |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T01:48Z / 2026-09-07T01:50Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T01:50Z |

## H.1 Hash mới

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ops/secrets.md` | MODIFY | `774a1130fa398602b4f0eb02334212cc2c762eaee95d172dd804a8b099344802` / 23585 | **`2ed96d93ecdbb74fd825e952abd85541ddecfe25cfd1c08efd739d708c165d48`** / 24387 |
| `contracts/ops/backup-restore.md` | MODIFY | `412d852ee59e2a84c3b64380199ea3753a55d2533750f94e7447c93e41ef1318` / 22499 | **`8737f483da5b776b506853dbbab5d2938bd08ba1a09481d2bd129c86e64ef7c3`** / 22659 |
| `acceptance/fixtures/recovery/README.md` | MODIFY | `8c260b2e6a40602079397319c5c9058fb496306c3cc2f55e473b7ce6c9b72e1a` / 10906 | **`799728748dcc40f5a79ed727cb491c446f8ce5e9eb0b40465d5aad891fbc1f6c`** / 10939 |
| `contracts/ops/internet-boundary.md` | **NO CHANGE** | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | gate không tìm thấy token nào cần sửa |
| `evidence/handoffs/PC08-handoff.md` | MODIFY (append) | `3704d6acdf620eb78eb9812d6b039f66031be21dc7ffbbfd8955dc517a60a5a5` / 37697 | ghi ở thông điệp bàn giao |

`acceptance/fixtures/recovery/README.md` nằm ngoài danh sách MODIFY của packet nhưng gate chạy trên toàn bộ file
PC08 và bắt hai token ở đó; nó thuộc thư mục `acceptance/fixtures/recovery/*` mà `PKT-PC08-FIX2` đã cấp và
`PKT-PC08` gốc tạo ra — tôi coi đó là trong phạm vi PC08 và **ghi rõ ở đây** để Coordinator bác nếu thấy khác.
Sources không đổi. Đối chiếu `contracts/data/entities.yaml` sha256
`c2ceeafd1b78705941f368bfe73f67cf097ffad8179c7455b2d4eeda571b5a1e`.

## H.2 Bảy token, ba loại nguyên nhân

Gate ban đầu báo **14 lần / 7 token duy nhất** không giải được.

**(a) Cụm tiếng Anh bị backtick thành dạng `entity.column` — 3 chỗ, đúng thứ E0-04c nhắm tới.**
`does_not_guarantee` là **tên một khóa trong `entities.yaml` của PC02**, không phải một cột; viết
`backup_snapshot.does_not_guarantee` khiến nó đọc như một cột thật. Viết lại thành văn xuôi nêu **nội dung** thay
vì đường dẫn: "điều mà bảng `backup_snapshot` của PC02 ghi rõ là **không** được bảo đảm"; tương tự cho
`data_deletion_audit` (hai chỗ: `backup-restore.md` §8 và `secrets.md` §9) và cho phần "không bảo đảm" của
`task_credential` trong `secrets.md` §5.

**(b) Hai token trỏ sai bảng — lỗi thật, không phải nhiễu.**
`manifest.artifact_sha256` → `artifact_sha256` thuộc **`backup_snapshot`**, không thuộc manifest;
`manifest.counts` → cột đúng là **`backup_manifest.counts`**. Cả hai nằm trong checklist toàn vẹn §5.3 và trong vị
từ `reconciliation_complete` §5.6 — tức trong chính oracle mà một drill sẽ chạy theo. Nay chúng trỏ đúng bảng và
**giải được** thành `entity.column` (số token giải được tăng 13 → 15).

**(c) Hai token là đường dẫn khóa YAML/JSON — viết lại cho khỏi giống tham chiếu cột.**
`post_restore_reconciliation_gate.interface_contract_vi` → "khóa `post_restore_reconciliation_gate` của
`contracts/state/storage.yaml`, trường `interface_contract_vi`"; `given.rows` / `expected.rows` trong README →
"khối `rows` của `given` và của `expected`", và `given.rows.<entity>[]` → `rows[<entity>][]`.

**Còn lại đúng một token được giữ:** `storage.health` — **ngoại lệ có tên** đã khai trong
`contracts/ports.yaml` `conventions.prose_token_rule_vi` (tên kênh trạng thái do `contracts/state/storage.yaml`
định nghĩa; không phải operation, không phải cột). Tôi hiện thực đúng ngoại lệ đó trong bản chạy gate thay vì viết
lại — viết lại sẽ làm văn bản sai, vì đó **là** tên đúng của thứ đang được nói tới.

## H.3 Gate

Dùng **gate của W3** (`…/scratchpad/w3/prose_token_gate.py`), copy sang scratch của tôi và chỉ đổi danh sách
`FILES` sang bốn file PC08; **logic không đổi**, cộng ngoại lệ có tên lấy từ `prose_token_rule_vi`.

| Kết quả | Trước | Sau |
| --- | --- | --- |
| `E0-04b` token giải được thành operation | 49 | **49** |
| `E0-04c` token giải được thành `entity.column` | 13 | **15** |
| **Không giải được** | **14** | **0** |
| Negative self-test (đột biến `ingest.submit_batch`, `post.x_post_id`) | — | **cả hai BỊ BẮT** |
| RESULT | FAIL | **PASS**, exit 0 |

Gate khác chạy lại sau khi sửa: `…/w2/validate_pc08.py` **exit 0** (13 fixture, README vẫn liệt kê đủ);
`…/w2/gate_fixtures.py` **exit 0**; `evidence/tools/e0_check.py` — `E0-04` PASS 895/0, tổng 19 check PASS 18,
FAIL 1. FAIL đó là `E0-07` với **`SC57`** trích trong `precode/handoff` của W1 mà chưa định nghĩa — ngoài phạm vi
PC08, và là cùng lớp với `SC54` trước đây.

## H.4 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| **PC10 re-pin**: `secrets.md`, `backup-restore.md`, `recovery/README.md` đổi hash (§H.1). | OPEN |
| Hai token sai bảng ở §H.2(b) nằm trong oracle của §5.3/§5.6 — chúng **sống sót bốn vòng audit** vì mọi check trước chỉ nhìn trường cấu trúc, không nhìn văn xuôi. Đây là lần thứ hai một lỗi cột lọt qua theo đúng cách đó (lần trước: `ingest_receipt.sequence` trong PC01). Giá trị của `E0-04c` là ở chỗ đó, không phải ở việc dọn dấu backtick. | — |
| `E0-07` / `SC57` | Ngoài phạm vi; cần W1/PC09. | OPEN |
| Mọi fixture và drill vẫn `NOT_RUN`. | — |

---

# ADDENDUM — PKT-PC08-FIX4

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC08-FIX4` · authority `AUTH-OWNER-20260907-02` · lease `LEASE-PC08-e5` (fencing 5) |
| expires_at | 2026-09-08T04:00Z |
| trigger | `F-A2R5-01` (phạm vi purge chưa lan tới các artefact) + hai correction giữa packet: `CR-PC05-06`, `CR-PC05-07` |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T05:05Z / 2026-09-07T05:13Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T05:13Z |

## I.1 Hash mới

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ops/secrets.md` | MODIFY | `2ed96d93ecdbb74fd825e952abd85541ddecfe25cfd1c08efd739d708c165d48` / 24387 | **`14b3d8988a9de21bf70de076c2b85a21b3e87394c493f18082af51c191690ee9`** / 25301 |
| `contracts/ops/backup-restore.md` | MODIFY | `8737f483da5b776b506853dbbab5d2938bd08ba1a09481d2bd129c86e64ef7c3` / 22659 | **`826655daa469e3e8e2fbd54263f13be78f4e9a17fd490524a3b07f894989ad4f`** / 25858 |
| `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` | MODIFY | `e144d0ce7b26f45825c8b1c72621d925336dd5b0ac8acbee77a48d05e1fd8bed` / 7790 | **`0f6237668132297cfe9cddfce019d2ec34dde865c72b1b3a6b856985ea158377`** / 19571 |
| `acceptance/fixtures/recovery/README.md` | MODIFY | `799728748dcc40f5a79ed727cb491c446f8ce5e9eb0b40465d5aad891fbc1f6c` / 10939 | **`982311e721d8e9e740f51ae011c557c363ba3d0de8151dd0643755ecb926dac8`** / 12235 |
| `evidence/handoffs/PC08-handoff.md` | MODIFY (append) | `db7493aacbb3e0b142e0a498869bf29c1174d42be3ae4590d7d732a998d657d6` / 43840 | ghi ở thông điệp bàn giao |

Sources không đổi. Không chạm file của gói khác.

## I.2 Ba tập bảng — và vì sao chúng đổi hai lần trong một packet

Packet ban đầu nói: sao chép `TXN-purge-all` của `entities.yaml` (20 giữ), **không** suy diễn lại. Tôi làm đúng
thế, và ngay khi đối chiếu bằng script đã thấy tập đó **tự mâu thuẫn**: `schedule_occurrence` nằm ở **cả**
`purged` lẫn `retained`, và hai bảng (`schema_migration`, `telegram_link_attempt`) không nằm ở tập nào — tức 60
entity không được phủ. Coordinator xác nhận và ra `CR-PC05-06`; rồi `CR-PC05-07` bổ sung `telegram_link_attempt`
vào tập xóa cho đủ 37. Bản cuối dùng trong cả năm artefact:

| Tập | Số | Nội dung |
| --- | --- | --- |
| **purged** | **37** | post/work và liên kết, identity alias/conflict/merge audit, work_label, analysis + các bảng phụ thuộc, embedding_generation, tag_vector, report/report_item, emerging_direction, coverage/pending/backfill/first_announced/rescan ledger, Saved, delivery + outbox, run/assignment/assignment_lease/checkpoint/ingest_receipt, source_fetch_log, telegram_update_log, **telegram_link_attempt** |
| **retained** | **21** | `owner`, `session`, `secret_ref`, `task_credential`, `secret_audit`, `telegram_link`, `telegram_link_code`, `provider_config`, `provider_test_result`, `settings`, `schedule_occurrence`, `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version`, `source_connection`, `backup_snapshot`, `backup_manifest`, `restore_record`, `purge_challenge`, **`worker_registration`** |
| **never_purged** | **2** | `schema_migration` (cấu trúc kho), `data_deletion_audit` (giữ vĩnh viễn; lần purge **ghi thêm** một hàng vào đây) |

**37 + 21 + 2 = 60**, đúng bằng số entity, không chồng lấn — tôi kiểm bằng script chứ không bằng đọc.

## I.3 Nội dung đã viết

`secrets.md` §9 và `backup-restore.md` §8.1 nay nêu cả ba tập, lý do Owner giữ từng nhóm (xóa credential đăng nhập
sẽ khóa chủ nhà ra ngoài app theo REQ-D05; tag là **subscription** chứ không phải dữ liệu nghiên cứu; xóa
`worker_registration` buộc đăng ký lại collector dù bảng đó không chứa dữ liệu nghiên cứu), và **câu bắt buộc cho
hộp thoại xác nhận**: dữ liệu vừa xóa **vẫn còn trong các bản backup** cho tới khi chúng hết hạn hoặc bị xóa bằng
tay. Không nói câu đó là để người dùng tin sai rằng dữ liệu đã biến mất hoàn toàn.
`OWNER_DECISION_REQUIRED` / `PROV-PC01-03` chỉ còn xuất hiện **một lần**, trong mục "Lịch sử" của
`backup-restore.md` §8.1 — đúng như ruling cho phép.

Fixture `l` nay khẳng định cả ba tập ở dạng `rows` có cấu trúc: 21 + 2 bảng giữ có hàng trong `given` **và**
`expected` (nên field gate kiểm từng cột — recovery tăng từ 175 lên **231 cột kiểm**), 37 bảng xóa khẳng định
`COUNT(*) = 0`, và `data_deletion_audit` **tăng đúng một hàng** vì chính lần purge ghi audit của nó.

## I.4 Gate

| Gate | Kết quả |
| --- | --- |
| `…/w2/validate_pc08.py` | **exit 0** |
| `…/w2/prose_gate_pc08.py` (gate của W3, trỏ vào file PC08) | **exit 0** — 0 token không giải được; negative self-test bắt được cả hai id đột biến |
| `…/w2/gate_fixtures.py` | **exit 0** — unresolved 0, event/edge problem 0 |
| `…/w3/fixture_field_gate.py` | **exit 0** — recovery 13 file, **231 cột**, 0 chưa giải; TOTAL unresolved 0 |
| `…/w3/check_actor_edges_all.py` | **exit 0** |
| `evidence/tools/e0_check.py` | `E0-10b` 36/0, `E0-14` 448/0 |

## I.5 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| **PC10 re-pin**: bốn file đổi hash (§I.1). | OPEN |
| Nguồn chuẩn tạm thời **không** phải `entities.yaml` mà là `PURGE-LIST-ruling.md` — W3 đang ghi ba tập vào `entities.yaml` dưới `PKT-PC02-FIX11`. Cho tới khi việc đó land, artefact của tôi và `entities.yaml` sẽ **lệch**, và lệch một cách có chủ đích: tôi chép bản đã sửa. Sau khi W3 land, nên chạy lại một phép so tập giữa hai nơi. | OPEN |
| Bài học | Chỉ thị "copy, do not re-derive" là đúng, nhưng nguồn được chỉ định lại sai. Việc đối chiếu bằng script (phủ đủ 60 entity, không chồng lấn) là thứ phát hiện ra — không phải việc đọc kỹ. Một danh sách "copy nguyên văn" vẫn cần một bất biến kiểm được. | — |
| Fixture vẫn `NOT_RUN` | 13 fixture recovery là dữ liệu vào và oracle; chưa drill nào chạy. | — |

---

# ADDENDUM — PKT-PC08-FIX5

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC08-FIX5` · authority `AUTH-COORD-PC08-FIX5` (parent `AUTH-OWNER-20260907-02`) · lease `LEASE-PC08-e6` (fencing 6) |
| expires_at | 2026-09-08T04:00Z |
| trigger | `E0-18-purge-set-agreement` (check mới của W6) báo 3 vi phạm, tất cả trong fixture `l` |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T05:18Z / 2026-09-07T05:21Z |
| next actor | `Coordinator` (W7 đang chờ pin) · lease_released_at 2026-09-07T05:21Z |

## J.1 Hash mới

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` | MODIFY | `0f6237668132297cfe9cddfce019d2ec34dde865c72b1b3a6b856985ea158377` / 19571 | **`9cd382e270e581b1b4ea69ac78f9ddb7730d215d34fadf6ce537a4e1f0dc053a`** / 20786 |
| `acceptance/fixtures/recovery/README.md` | **NO CHANGE** | `982311e721d8e9e740f51ae011c557c363ba3d0de8151dd0643755ecb926dac8` | đã nêu đúng ba tập ở FIX4; `E0-18` không báo vi phạm nào ở đây |

Sources không đổi.

## J.2 Ba tàn dư — và một cái thứ tư mà chính lần sửa tạo ra

`E0-18` bắt ba dòng còn nói phạm vi purge **chưa được quyết**, trong khi phần thân của fixture đã khẳng định đủ ba
tập từ FIX4. Chúng là tàn dư của bản trước ratification:

1. `given._exclusions_vi` — "Danh sách LOẠI TRỪ vẫn OWNER_DECISION_REQUIRED (PROV-PC01-03)". Thay bằng
   `given._purge_scope_vi` nêu đúng ba tập (37 / 21 / 2, phủ 60 entity, không chồng lấn).
2. `blocked_scope_vi` — nói "không còn phạm vi bị chặn" nhưng vẫn nhắc hai id chưa đóng trong cùng câu. Gỡ; nội
   dung lịch sử chuyển vào khối `_history` có nhãn rõ ràng, cộng `scope_status: "RATIFIED (OD-20260907-01)"`.
3. `x-contract.decision_refs` vẫn liệt kê `PROV-PC01-03`. Đổi thành `[R5-02, OD-20260907-01, CR-PC05-06,
   CR-PC05-07]` — tức các quyết định **đang** chi phối fixture — và thêm `ratification_ref`.

Sửa xong ba cái thì `E0-18` còn **2** vi phạm mới: tôi đã chuyển hai id vào `_history.superseded_decision_refs`
dưới dạng **danh sách**, nên mỗi id nằm một dòng riêng không mang dấu hiệu lịch sử nào — check đọc theo **dòng**,
không theo cấu trúc. Sửa lại thành một chuỗi trên một dòng, có cả chữ "Lịch sử" lẫn id ratification:

> `"superseded_decision_refs_vi": "Lịch sử: PROV-PC01-03 và PROV-PC00-01 đã được OD-20260907-01 đóng; chúng không còn nằm trong decision_refs của fixture này."`

Đáng ghi lại: một khối `_history` **đúng về mặt cấu trúc** vẫn trượt check vì check làm việc trên dòng văn bản.
Không phải lỗi của check — nó bắt đúng thứ nó nhắm: một người đọc `grep` sẽ thấy `PROV-PC01-03` trần trụi và
không biết nó đã đóng.

## J.3 Gate

| Gate | Kết quả |
| --- | --- |
| `evidence/tools/e0_check.py` (copy read-only trong scratch, `--repo`) | **`E0-18-purge-set-agreement` PASS — checked 17, violations 0**; dòng ghi chú của chính check xác nhận "purged 37 · retained 21 · never_purged 2 · union 60 of 60 entities" |
| `…/w2/validate_pc08.py` | **exit 0** |
| `…/w2/prose_gate_pc08.py` | **exit 0** |
| `…/w2/gate_fixtures.py` | **exit 0** |
| `…/w3/fixture_field_gate.py` · `…/w3/check_actor_edges_all.py` | **exit 0** cả hai |

## J.4 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| **W7 pin**: chỉ `l-purge-all-two-phase-and-negatives.json` đổi hash (§J.1); README không đổi. | OPEN |
| `E0-18` kiểm theo **dòng**, nên một cấu trúc `_history` hợp lệ vẫn có thể trượt nếu id nằm một mình trên dòng. Đây là hành vi đúng cho mục đích của check, nhưng đáng ghi vào `evidence/tools/README.md` để gói khác không mất một vòng như tôi. | OPEN |
| Fixture vẫn `NOT_RUN`. | — |
