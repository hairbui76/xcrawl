---
contract_id: CT-ops-backup-restore
version: 0.1.0
status: draft
owner_role: operations contract owner
source_refs:
  - SRC-SPEC §6.4
  - SRC-SPEC §7.3
  - SRC-SPEC §9.3
  - SRC-SPEC §12 AC-12
  - SRC-SPEC §13 M8
  - SRC-PLAN §3 B11
  - SRC-PLAN §3.1
  - SRC-PLAN §7 I15
  - SRC-PLAN §8.4
  - SRC-PLAN §10 STORAGE_WRITE_FAILED
  - SRC-PLAN §10 RESTORE_UNVERIFIED
  - SRC-PLAN §11 PC08
  - SRC-PLAN §13 SC27
requirement_refs:
  - REQ-D58
  - REQ-S6.4-01
  - REQ-S7.3-04
  - REQ-S7.3-05
  - REQ-S7.3-06
  - REQ-S9.3-08
  - REQ-S11.2-02
  - REQ-S11.2-03
  - REQ-AC12
  - REQ-S13-09
decision_refs: [B11, AMD-B11, ADR-0005]
invariant_refs: [I02, I08, I13, I15]
producers: [MOD-backup-service]
consumers: [MOD-backup-cli, MOD-delivery-service, MOD-job-service, MOD-report-service, MOD-health-service, MOD-data-store]
dependencies:
  - contracts/ports.yaml
  - contracts/modules.yaml
  - contracts/capabilities.yaml
  - contracts/data/entities.yaml
  - contracts/state/storage.yaml
  - contracts/state/delivery.yaml
  - contracts/state/run.yaml
  - contracts/errors.yaml
  - contracts/ops/secrets.md
  - contracts/ops/deployment.md
scope: >
  Hợp đồng backup và restore: cách tạo snapshot nhất quán khi DB đang hoạt động (Online Backup API hoặc
  `VACUUM INTO`), vì sao copy file của một DB dùng WAL là không đủ, nội dung manifest, chính sách retention,
  RPO/RTO, và runbook restore có khóa side effect với đối soát bắt buộc trước khi mở lại dispatch.
  File này hiện thực phần `owned_by_pc08_vi` của `contracts/state/storage.yaml.post_restore_reconciliation_gate`
  và cung cấp vị từ `reconciliation_complete(restore_id)` mà PC03 yêu cầu. Nó **không** định nghĩa transition của
  `storage.health` (PC03), không định nghĩa operation (PC01), không định nghĩa entity (PC02).
verification: >
  E0 self-validation: mọi operation, mã lỗi, tên entity, tên state được trích tồn tại ở upstream (EV-PC08-01);
  đối chiếu thủ công danh sách trường manifest với `entities.yaml` (EV-PC08-03). Restore drill thật là **E2/E3 và
  chưa chạy**: mọi kết quả ghi `NOT_RUN`. Hash của một artifact **không** chứng minh nó khôi phục được — chỉ một
  drill thật mới chứng minh.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Backup và restore

## 1. Vì sao không phải "copy file SQLite"

D58 và §7.3 của đặc tả mô tả backup là "copy file SQLite" và restore là "đặt file về chỗ cũ" (REQ-D58,
REQ-S7.3-04, trạng thái **UQ**). Kỹ thuật không cho phép giữ nguyên câu đó:

- Với chế độ WAL, các transaction đã commit có thể **đang nằm trong file `-wal`**, chưa checkpoint vào file DB
  chính (SRC-PLAN §3.1, <https://www.sqlite.org/wal.html>). Copy riêng file `.db` sẽ mất chúng — im lặng.
- Copy trong lúc DB đang ghi có thể bắt được **trạng thái giữa chừng** của một transaction: file "có vẻ đúng",
  `PRAGMA integrity_check` có thể vẫn `ok`, nhưng nội dung nghiệp vụ đã mất một phần commit.

**AMD-B11 / ADR-0005 điểm 1:** backup phải dùng **SQLite Online Backup API**
(<https://www.sqlite.org/backup.html>) hoặc **`VACUUM INTO`** — cả hai an toàn với WAL vì chúng đọc qua chính engine
SQLite. Không dùng `cp`/`rsync` trên file DB đang hoạt động.

Đây là **sửa hợp đồng, không phải bỏ yêu cầu của người dùng**: yêu cầu "có backup và restore được" vẫn nguyên;
chỉ phương pháp đổi vì phương pháp cũ không đạt được chính mục tiêu đó. Owner phải phê chuẩn AMD-B11.

## 2. Tạo snapshot

`backup.create_snapshot` (`ports.yaml`, actor `ACT-backup-operator`, module `MOD-backup-service`).

| Mục | Quy định |
| --- | --- |
| Phương pháp | `sqlite_online_backup_api` hoặc `vacuum_into` — ghi vào `backup_snapshot.method` (PC02) |
| Trạng thái storage | Chạy được ở `healthy`; **nên** chạy trong `maintenance` cho snapshot lớn để không có publish/dispatch xen giữa (`storage.yaml`) |
| Kết quả | `backup_snapshot`: `artifact_path`, `artifact_sha256`, `schema_migration_version`, `started_at`, `completed_at`, `state` |
| Không được | Copy file DB đang hoạt động; coi hash artifact là bằng chứng khôi phục được — điều mà bảng `backup_snapshot` của PC02 ghi rõ là **không** được bảo đảm |

| Tham số | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| `backup_schedule` | mỗi ngày một lần, 03:00 giờ IANA của owner | PROVISIONAL | Ngoài hai mốc lịch chạy đợt (08:00/20:00 PROVISIONAL, baseline §5) nên không tranh chấp với `report.publish`. |
| `backup_timeout` | 600 giây | PROVISIONAL | Một DB một-người-dùng vài trăm MB snapshot trong vài giây; 10 phút là trần rộng để phát hiện treo, không phải mục tiêu. |
| `retention_daily` | giữ 14 bản gần nhất | PROVISIONAL | Đủ để phát hiện một hỏng hóc âm thầm trong hai tuần. |
| `retention_weekly` | giữ 8 bản | PROVISIONAL | Hai tháng lịch sử thưa hơn. |
| `retention_monthly` | giữ **vô thời hạn** | PROVISIONAL | Khớp tinh thần D58 (retention vô thời hạn) mà không giữ 365 bản đầy đủ mỗi năm. |

Retention của **dữ liệu** vẫn là vô thời hạn (D58); dòng trên là retention của **artifact backup**, một thứ khác.

## 3. Manifest

`backup_manifest` (PC02: `backup_snapshot_id`, `entries`, `manifest_sha256`, `counts`). Nội dung bắt buộc:

| Nhóm | Trường | Nguồn |
| --- | --- | --- |
| Snapshot | `artifact_sha256`, `artifact_bytes`, `method`, `created_at` (UTC ms), `completed_at` | ADR-0005 điểm 2 |
| Schema | `schema_migration_version` | `backup_snapshot.schema_migration_version`; entity `schema_migration` (MOD-data-store) |
| Ứng dụng | `app_version`, `contract_versions` (các file hợp đồng đang hiệu lực) | Để biết snapshot thuộc thế hệ nào |
| Embedding | `embedding_generation.id` đang `active`, `model_name`, `model_version`, `dimension`, `normalization`, `expected_vector_count`, `built_vector_count`; đường dẫn + sha256 của **artifact model** | ADR-0005 điểm 2; `entities.yaml` `embedding_generation` |
| Cấu hình | Bản xuất `settings` **đã bỏ mọi secret** (chỉ tham chiếu `secret_ref.purpose` + `state`) | `secrets.md` §4 |
| Secret | **Con trỏ tới kế hoạch khôi phục secret**, không phải secret | §6 dưới đây |
| Đếm | `counts` cho: `saved_item`, `saved_snapshot`, `report`, `report_item`, `coverage_window`, `first_announced_ledger`, `backfill_ledger`, `pending_item_ledger`, `outbox_intent` theo `dispatch_state`, `delivery_part` theo state, `post`, `work`, `analysis` (valid) | Dùng làm oracle ở §5.4 |
| Phạm vi | Danh sách những gì **không** nằm trong backup (§6) | ADR-0005 điểm 3 |
| Toàn vẹn | `manifest_sha256` tính trên nội dung manifest đã chuẩn hóa | PC02 `ux_backup_manifest_snapshot` |

**Oracle của manifest (CR-PC02-07, phần 3):** một manifest hợp lệ phải thỏa **cả ba** điều kiện, kiểm được bằng máy:

1. `sha256(artifact tại artifact_path) == artifact_sha256`;
2. `PRAGMA integrity_check` trên **bản sao** của artifact trả `ok`;
3. với **mỗi** khóa trong `counts`, số đếm truy vấn được từ artifact **bằng đúng** giá trị ghi trong manifest.

Thiếu bất kỳ điều kiện nào ⇒ snapshot ở trạng thái `invalid`, **không** được dùng để restore, và
`backup.verify_snapshot` trả `RESTORE_UNVERIFIED`. Điều kiện (3) là thứ phát hiện được bản copy WAL-unsafe:
file có thể `integrity_check ok` mà vẫn thiếu các hàng đã commit — xem fixture `d-wal-unsafe-copy-detected.json`.

## 4. RPO / RTO

| Chỉ tiêu | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| **RPO** | 24 giờ | PROVISIONAL | Bằng `backup_schedule`. Mất tối đa một ngày phát hiện. Chấp nhận được vì dữ liệu là **có thể thu lại**: post cũ có thể được ingest lại từ X (nếu còn), metadata lấy lại từ arXiv/OpenAlex. |
| **RPO cho Saved** | 24 giờ | PROVISIONAL | Đây là phần **không** thu lại được (snapshot của bài có thể đã bị xóa trên X — D55/AC-12). Nếu Owner thấy 24 h là quá nhiều, tăng tần suất backup là cách sửa, không phải đổi thiết kế. |
| **RTO** | 2 giờ | PROVISIONAL | Gồm: khôi phục artifact (phút), integrity check + counts (phút), đối soát §5.4 (thủ công, phần lớn thời gian), đăng nhập X lại bằng tay (§6). |
| `restore_verification_deadline` | không có deadline tự động | — | Dispatch **không** tự mở theo thời gian. Không có timeout nào thay thế được thao tác của Operator (`storage.yaml`: cấm "mở khóa theo thời gian"). |

**Không được suy diễn:** transaction của SQLite bảo vệ tính nguyên tử của một lần ghi; nó **không** bảo vệ trước
hỏng ổ đĩa, mất máy hay xóa nhầm. Đó là lý do backup tồn tại, và là lý do RPO khác 0.

## 5. Runbook restore

### 5.1 Điều kiện bắt đầu

Restore chạy vào **môi trường sạch** (`backup.restore_snapshot`). Ngay khi restore xong,
`storage.health = recovery_required` (PC03 `T-ST-05`). Ở trạng thái đó, `storage.yaml` đã quy định:

- `worker.claim_assignment` và `analysis.claim_task` ⇒ `RESTORE_UNVERIFIED`;
- `delivery.dispatch_next` ⇒ `RESTORE_UNVERIFIED` — **outbox cũ không replay**;
- `report.build` / `report.publish` ⇒ `RESTORE_UNVERIFIED`;
- `job.enqueue_scheduled_run` / `job.coalesce_overdue` ⇒ `RESTORE_UNVERIFIED`;
- `first_announced` **không** bị reset;
- **không có** đường tự động rời trạng thái này (NC-10).

### 5.2 Thu hồi lease **trước** khi dispatcher mở (CR-PC02-07, phần 2)

Mọi `assignment_lease` có trong snapshot là **stale theo định nghĩa**: thế giới đã đi tiếp kể từ lúc snapshot được
tạo. Thứ tự bắt buộc, không được đảo:

```
1. restore artifact  →  storage.health = recovery_required
2. thu hồi TOÀN BỘ assignment_lease trong snapshot  (state → revoked)
3. tăng lease_epoch cho mọi run non-terminal        (worker cũ mang epoch cũ ⇒ STALE_LEASE)
4. ghi restore_record.leases_revoked = số lease đã thu hồi
5. verify + counts (§5.3, §5.4)
6. quyết định với outbox cũ (§5.5)
7. reconciliation_complete(restore_id) == true
8. CHỈ KHI ĐÓ: backup.reconcile_after_restore → storage.health = healthy,
   restore_record.dispatcher_unlocked_at được ghi
```

Một worker từ trước backup mà còn sống sẽ mang `lease_epoch` cũ và bị từ chối bằng `STALE_LEASE` — nó không commit
được gì vào DB vừa khôi phục (fixture `b-post-restore-stale-lease-rejected.json`).

### 5.3 Kiểm toàn vẹn

| Bước | Kiểm | Hỏng thì |
| --- | --- | --- |
| 1 | `sha256(artifact)` bằng `backup_snapshot.artifact_sha256` ghi trong manifest | Dừng; snapshot `invalid` |
| 2 | `PRAGMA integrity_check` = `ok` | Dừng; snapshot `invalid` |
| 3 | `schema_migration_version` khớp phiên bản ứng dụng sẽ chạy | Dừng; chạy migration có chủ đích trước, không tự động |
| 4 | Mọi `counts` khớp manifest | Dừng; ghi `integrity_check_outcome = mismatch` |
| 5 | Artifact model embedding tồn tại và `sha256` khớp; `embedding_generation` active có `built_vector_count == expected_vector_count` | Selection bị chặn cho tới khi dựng lại generation (`EMBEDDING_GENERATION_MISMATCH`, I12) |

Kết quả ghi vào `restore_record.integrity_check_outcome` và `counts_observed` (PC02).

### 5.4 Đối soát nội dung

| Đối tượng | Oracle |
| --- | --- |
| Saved | `COUNT(saved_item)` và `COUNT(saved_snapshot)` khớp manifest; **hash của từng `saved_snapshot` trước backup == sau restore** (AC-12/SC12, I08) |
| Report | `COUNT(report)`, `COUNT(report_item)` khớp; nội dung report đã publish **không đổi** (I05) |
| Coverage | `coverage_window` nối liền, half-open, không hở không chồng (I06) |
| First-announced | `COUNT(first_announced_ledger)` khớp; **không** hàng nào bị reset (I15) |
| Backfill / pending | Số hàng khớp; backfill đã tiêu thụ vẫn ở trạng thái đã tiêu thụ (không "được tiêu thụ lại") |
| Delivery | Số `delivery_part` theo từng state khớp; đặc biệt số part `unknown` |

### 5.5 Đối soát công việc đang bay và `restore_generation` (CR-PC02-07, phần 1)

`outbox_intent.restore_generation` (PC02) và `restore_record.new_restore_generation` là cặp khóa của quy tắc này.

- Mỗi lần restore sinh một `new_restore_generation` **tăng đơn điệu** (PC02 `ux_restore_record_generation`).
- Mọi `outbox_intent` khôi phục từ snapshot mang `restore_generation` **cũ hơn** generation hiện tại.
- **Dispatcher chỉ gửi intent có `restore_generation == generation hiện tại`.** Intent generation cũ **không bao
  giờ** được gửi tự động — đây là cơ chế làm cho I15 ("restore không tự gửi lại outbox cũ") kiểm được bằng một
  phép so sánh số, chứ không phải bằng một lời hứa trong tài liệu.
- Đưa một intent cũ sang generation hiện tại là **quyết định của Operator**, ghi lý do, từng intent một.

Quyết định cho từng loại:

| Loại | Quy tắc |
| --- | --- |
| `delivery_part` = `sent` trong snapshot | Đã gửi trước snapshot; **không** gửi lại. Giữ receipt. |
| `delivery_part` = `unknown` | **Vẫn là `unknown` sau restore.** Restore không tạo ra thông tin mới về việc Telegram đã nhận hay chưa. Chỉ `delivery.decide_unknown` (Owner) mới đưa nó ra khỏi trạng thái đó (B03/AMD-B03). |
| `delivery_part` = `pending`/`retry_wait` | Mang `restore_generation` cũ ⇒ không tự gửi. Operator quyết định huỷ hay nâng generation. |
| Run `running` trong snapshot | Lease đã thu hồi (§5.2); run theo `run.yaml` về `queued` hoặc trạng thái đã lưu; tiếp từ `checkpoint` đã ACK, không lấy lại bài đã ingest |
| `analysis` đang `running` | Task về `pending`; kết quả từ worker cũ bị từ chối bằng `STALE_LEASE` |

### 5.6 Vị từ `reconciliation_complete(restore_id)`

PC03 yêu cầu một vị từ boolean **không có side effect** (khóa `post_restore_reconciliation_gate` của
`contracts/state/storage.yaml`, trường `interface_contract_vi`).
Định nghĩa:

```
reconciliation_complete(restore_id) := TẤT CẢ các mệnh đề sau đúng
  1. restore_record[restore_id].integrity_check_outcome == 'ok'          (§5.3 bước 1–4)
  2. mọi khóa trong counts_observed khớp backup_manifest.counts          (§5.4)
  3. restore_record[restore_id].leases_revoked == số assignment_lease
     non-terminal có trong snapshot, và không còn lease active nào
     mang lease_epoch cũ                                                 (§5.2)
  4. không tồn tại outbox_intent có dispatch_state ∈ {pending, retry_wait}
     mang restore_generation == new_restore_generation mà chưa được
     Operator xét                                                        (§5.5)
  5. số delivery_part ở trạng thái 'unknown' bằng đúng số trong manifest
     (không cái nào bị tự động chuyển sang sent hay failed)               (§5.4, I13)
  6. embedding: hoặc generation active hợp lệ, hoặc selection đang bị
     chặn có lý do đã ghi                                                (§5.3 bước 5)
  7. có một bản ghi xác nhận của Operator gắn với restore_id             (không tự động)
```

Vị từ này **chỉ đọc**. `backup.reconcile_after_restore` gọi nó và chỉ chuyển `storage.health = healthy` khi nó
đúng; sai thì trả `RESTORE_UNVERIFIED` và ghi mệnh đề nào chưa đạt. Mệnh đề 7 là lý do không có đường tự động:
máy không thể tự xác nhận rằng con người đã nhìn.

### 5.7 Bằng chứng phải thu thập trong một drill

`restore_id`, `backup_snapshot_id`, `manifest_sha256`, `artifact_sha256`, kết quả `integrity_check`, bảng
counts kỳ vọng/quan sát, số lease thu hồi, danh sách intent generation cũ và quyết định cho từng cái, số outbound
send **trước** khi mở dispatch (oracle: **0**), thời điểm `dispatcher_unlocked_at`, tổng thời gian (đối chiếu RTO),
và mọi bước phải làm bằng tay.

**Trạng thái hiện tại: `NOT_RUN`.** Chưa có drill nào được thực hiện. Không được coi tài liệu này là bằng chứng
rằng restore hoạt động (SRC-PLAN §14.2: E0 không chứng minh runtime).

## 6. Những gì **không** nằm trong backup

| Mục | Vì sao | Khôi phục thế nào |
| --- | --- | --- |
| Profile Chrome + phiên X | Ở máy cá nhân; không bao giờ đồng bộ lên server (REQ-S11.2-03) | Chủ máy **đăng nhập X lại bằng tay** trong profile riêng của dự án; lần đầu X thường đòi xác minh thiết bị mới |
| Token collector / analysis worker | File cấu hình trên máy cá nhân, không trong repo (REQ-S11.2-02) | Sinh token mới trong app, cập nhật file `0600`, khởi động lại worker (`secrets.md` §3) |
| Master key của secret store | Ngoài DB theo thiết kế (`secrets.md` §4.1) | **Kế hoạch khôi phục secret** riêng: master key được giữ ở nơi Owner chọn, ngoài server và ngoài backup. Mất master key ⇒ ciphertext trong backup vô dụng ⇒ phải nhập lại API key. Manifest chỉ chứa **con trỏ** tới kế hoạch này, không chứa key |
| Giá trị API key AI | Là secret; không nằm trong bản xuất settings | Nhập lại trong Settings sau restore |
| Artifact model embedding | Có thể lớn; manifest ghi tên/phiên bản/hash | Tải lại đúng phiên bản ghi trong manifest, đối chiếu sha256 |

Nếu một mục ở đây thiếu sau restore, hệ thống **không** giả vờ chạy được: worker khai capability tương ứng
`unusable`/`unknown` với `reason_code`, và readiness hiển thị đúng lý do (I13).

## 7. Disk-full và readiness

Thuộc PC03 (`storage.yaml` `T-ST-01`/`T-ST-02`); phần vận hành liên quan tới backup:

- Ở `write_blocked`: **không** ACK mutation, **không** tiến cursor, `health.get_readiness` đỏ,
  `health.get_liveness` vẫn `up` (kênh độc lập DB). Không tuyên bố đã persist lỗi vào một DB đang không ghi được
  (SRC-PLAN §8.4).
- **Không** chạy `backup.create_snapshot` khi `write_blocked`: snapshot cần ghi ra artifact và cần DB ổn định.
- Rời `write_blocked` cần 3 probe liên tiếp thành công cách nhau 30 s (PC03) — không rời sau một lần đọc được.
- Dọn chỗ bằng cách xóa artifact backup cũ theo retention §2 là thao tác vận hành hợp lệ; xóa dữ liệu nghiệp vụ để
  lấy chỗ thì **không** (đó là `data.delete_target`/`data.purge_all`, có xác nhận riêng).

## 8. Backup, xóa dữ liệu và purge

- `data.delete_target` và `data.purge_all` xóa dữ liệu trong DB **đang chạy**. Chúng **không** chạm tới artifact
  backup đã tạo — bảng `data_deletion_audit` của PC02 ghi rõ đây là điều nó **không** bảo đảm.
- Hệ quả phải nói với Owner: sau khi purge, dữ liệu vẫn tồn tại trong các bản backup cho tới khi những bản đó bị
  xóa theo retention hoặc bị xóa thủ công. Nếu ý định của Owner là "xóa hẳn", phải xóa cả artifact backup — đó là
  một thao tác riêng, có chủ đích, ghi vào `secret_audit`/vận hành.
- Danh sách **loại trừ** của `data.purge_all` vẫn là **`OWNER_DECISION_REQUIRED`** (`PROV-PC01-03`). File này
  không giải quyết nó.
- `data.purge_all` chỉ chạy ở `storage.health = maintenance`; `maintenance` cũng là cửa sổ khuyến nghị để tạo
  snapshot **trước** khi purge — nhưng đó là lựa chọn của Operator, không phải bước tự động (một snapshot tự động
  trước purge sẽ mâu thuẫn với ý định "xóa hẳn").

## 9. "Tôi khôi phục về được thời điểm nào, và mất gì?"

Phần này viết cho người đọc runbook lúc đang có sự cố.

**Khôi phục về được:** thời điểm của bản snapshot gần nhất đã `verified`. Với `backup_schedule` PROVISIONAL hiện
tại, tệ nhất là **24 giờ trước sự cố**.

**Mất gì trong 24 giờ đó:**

| Mất | Có lấy lại được không |
| --- | --- |
| Post đã ingest sau snapshot | Phần lớn **có** — chạy lại một đợt thu thập; giới hạn là bài đã bị xóa trên X hoặc đã trôi khỏi tầm với của feed |
| Metadata paper | **Có** — gọi lại arXiv/OpenAlex bằng ID |
| Kết quả `analysis` | **Có, nhưng tốn tiền/thời gian AI** — chạy lại theo `analysis_key`; đây là chi phí thật, không phải mất mát vĩnh viễn |
| Report đã publish sau snapshot | **Dựng lại được** nhưng `first_announced` và coverage sẽ khác lịch sử đã gửi; nếu digest đã gửi cho kỳ đó thì báo cáo trong app và tin đã gửi sẽ lệch nhau — ghi rõ cho Owner, không tự sửa |
| **Saved sau snapshot** | **Không** — nếu bài gốc đã bị xóa trên X thì snapshot đó mất vĩnh viễn (D55/AC-12). Đây là mất mát nghiêm trọng nhất và là lý do RPO của Saved được tách riêng ở §4 |
| Delivery đã gửi sau snapshot | Không lấy lại; và **không** gửi lại — người nhận đã thấy tin rồi |
| Phiên X, token worker, API key | Không nằm trong backup theo thiết kế — thiết lập lại theo §6 |

**Điều tài liệu này không hứa:** rằng restore sẽ chạy được. Không drill nào đã chạy (`NOT_RUN`). Cho tới khi có một
drill thật với bằng chứng theo §5.7, mức tin cậy của toàn bộ chương này là "thiết kế đã viết ra", không hơn.
