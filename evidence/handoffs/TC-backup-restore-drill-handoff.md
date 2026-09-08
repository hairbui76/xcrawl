# HANDOFF — `TC-backup-restore-drill` (`MOD-backup-service`, `MOD-backup-cli`)

| Trường | Giá trị |
| --- | --- |
| packet | `PKT-TC-BACKUP` (e1) + `PKT-TC-BACKUP-FIX1` (e2) + **`PKT-TC-BACKUP-FIX2`** (e3) · lease `LEASE-TC-BACKUP-e3` · authority `AUTH-COORD-TC-BACKUP` (dưới `AUTH-OWNER-20260908-10`) |
| worker | `worker-W6B` (tái dùng `worker-W5B`) |
| card | `agent-tasks/TC-backup-restore-drill.md` (§1–§13 ràng buộc) |
| pin epoch | `PC10-PIN-P3b-20260908` — SG-HASH ngay trước dòng code đầu tiên: **26/26 file khớp, 0 lệch** |
| status | `DONE` · claim `IMPLEMENTATION_VERIFIED` cho phạm vi E1/E2 của card |
| evidence | **`evidence/runs/TC-backup-restore-drill-E1-20260908T064000Z.json`** (validate sạch). Bản e1 `…T042000Z.json` và e2 `…T061000Z.json` nay **STALE** |
| next actor | Coordinator |
| `lease_released_at` | e1 2026-09-08T04:25Z · e2 2026-09-08T06:10Z · **e3 2026-09-08T06:40Z** |

## 1. Cổng chờ

Bốn điều kiện, tất cả đã kiểm trực tiếp chứ không suy diễn:

1. `git log -1 --format=%s` trên `main` = `feat: Phase 3 (M3) + Phase 5 (M6, plain text) …`, commit `fb3944a`.
2. `agent-tasks/README.md` dòng 124 khai `PC10-PIN-P3b-20260908`; §0 của card mang đúng tên đó.
3. **SG-HASH**: tính lại `sha256` + byte count cho cả 26 dòng đã pin ở §0 — **0 lệch**.
4. `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md` (worker-W4A) tồn tại với
   `lease_released_at 2026-09-07T21:40Z`. Trong lúc chờ, gói này chỉ **đọc**.

`SG-PC09`: đọc `acceptance/scenarios.yaml` bản mới nhất — SC26/27/42/43/12/49/44/53 không mâu
thuẫn với §8.

## 2. `SG-01` **không** kích hoạt

Card §10 `SG-01` yêu cầu DỪNG nếu `ENT-restore-record` thiếu trường xác nhận của Operator mà
mệnh đề 7 của `reconciliation_complete` đòi. Trường **có mặt**: `entities.yaml` dòng 2108–2110
khai `operator_ack_at`, `operator_ack_principal`, `operator_ack_note`, dẫn thẳng `CR-PC08-05`.
Tên khác với phỏng đoán của card (`operator_acknowledged_at` / `operator_acknowledgement_ref`)
nhưng **trường tồn tại**, nên điều kiện dừng không thành lập và gói này dùng đúng ba tên của
`entities.yaml`. `CR-PC08-05` xem như đã đóng ở phía hợp đồng.

## 3. Trạng thái file

Mọi target `ABSENT` trước khi ghi; không file nào bị ghi đè.

| Đường dẫn | Thao tác | sha256 sau | bytes |
| --- | --- | --- | --- |
| `server/app/backup/snapshot.py` | CREATE | `6217b2a034ed6f8d58244475add7edbedea0504ec4840acd06edc43dad10d011` | 25402 |
| `server/app/backup/verify.py` | CREATE | `b370d83e905ad8323dfc26f5e5e4b6d2ef834bf1548e0dfe04c22bf466abf629` | 10630 |
| `server/app/backup/restore.py` | CREATE | `09b761d60ab876c9672936327b0a6a1dc7b714dbd85c168218eaee0069b6c664` | 16739 |
| `server/app/backup/reconcile.py` | CREATE | `a4c7872cd7e4a11c021dff4aa2b1d5b3cb542196868d6f50feab0417f7db632d` | 22376 |
| `tools/backup_cli.py` | CREATE | `d7fd1b206c253a06287aa981e6efd917dde6d730fe268748263138405c16a22c` | 13960 |
| `server/migrations/versions/0012_tc_backup_restore_drill.py` | CREATE | `4454be392837728303e55f97a2d071432cbd6c3fc3beca79cd2643cae4adefc1` | 9506 |
| `tests/integration/test_wal_unsafe_detected.py` | CREATE | `1b6c0cc0157903bd88180538653560931e1a3c5e2c206a730d403c8d1f9f400e` | 18323 |
| `tests/integration/test_restore_side_effect_lock.py` | CREATE | `2c5ace98cd476b2fc50bb3241711c24599f66ae78bfc2ece6b758ffed488c58a` | 42737 |
| `evidence/runs/TC-backup-restore-drill-E1-20260908T042000Z.json` | CREATE (e1, nay **STALE**) | (bản ghi bằng chứng) | 16653 |
| `evidence/runs/TC-backup-restore-drill-E1-20260908T061000Z.json` | CREATE (e2, nay **STALE**) | (bản ghi bằng chứng) | 17072 |
| `evidence/runs/TC-backup-restore-drill-E1-20260908T064000Z.json` | CREATE (e3) | (bản ghi bằng chứng thay thế) | 18181 |
| `evidence/handoffs/TC-backup-restore-drill-handoff.md` | CREATE | (file này) | — |

**`server/app/main.py` KHÔNG bị chạm** — card này không có router, nên không có include block.
Không có `server/app/backup/__init__.py` (namespace package, theo tiền lệ `server/app/research/`).
Không chạm `precode/`, `contracts/`, `acceptance/`, `agent-tasks/`. Không mutation git, không
lời gọi mạng, `PYTHONDONTWRITEBYTECODE=1` suốt phiên.

**Migration:** `0012_tc_backup_restore_drill` tạo mới `backup_snapshot`, `backup_manifest`,
`restore_record` (không bảng nào tồn tại trước; không có custodian để tiếp quản). Head sau khi
land: **1** (`0012_tc_backup_restore_drill`), kiểm bằng `len(heads) == 1` theo cấu trúc.

## 4. Điều đã chứng minh

```
python -m pytest tests/integration/test_wal_unsafe_detected.py -q       → 10 passed
python -m pytest tests/integration/test_restore_side_effect_lock.py -q  → 25 passed
python -m pytest tests/contract/test_schema_matches_entities.py -q      → 10 passed
```

`ruff check` + `ruff format --check` sạch; `mypy --strict` sạch trên 6 file nguồn.

**Toàn bộ suite (sau FIX2): 1025 passed, 7 xfailed, exit 0 — 0 FAILED, 0 ERROR.** Các lỗi setup
của W5C (`CR-TC-REPORT-09`) đã được chính họ sửa; cây test nay xanh hoàn toàn.

**Toàn bộ suite:** **990 passed, 9 xfailed, exit 0** khi loại trừ hai file
`tests/integration/test_delivery_unknown_no_retry.py` và `test_permanent_failure_report_intact.py`.
Chạy không loại trừ: exit 1 với **0 dòng FAILED** và đúng **18 setup ERROR**, toàn bộ nằm trong
hai file đó — đúng breakage mà W4A đã ghi là `CR-TC-REPORT-09`. Hai file thuộc write set của
W5C; gói này không chạm tới chúng.

**Oracle 1 — bản copy WAL-unsafe bị từ chối (fixture `d`).** Khuyết tật được **tạo thật**, không
mô phỏng: ghi rồi checkpoint 3 hàng, ghi tiếp 4 hàng (nằm trong `-wal`), rồi copy **chỉ** file
`.db`. Kết quả đúng như fixture nói: `sha256` khớp, `PRAGMA integrity_check` = `ok`, và
`counts` lệch đúng 4 hàng. ⇒ `RESTORE_UNVERIFIED`, `state != verified`, và `restore_snapshot`
từ chối luôn snapshot đó (0 hàng `restore_record`, storage không bị khóa). Đối chứng: **cả hai**
phương pháp hợp lệ (`VACUUM INTO` và Online Backup API) chụp đúng 7 hàng và verify sạch — nên
sự lệch là tính chất của *phương pháp copy*, không phải của bộ khung test.

**Oracle 2 — 0 tin gửi trước khi đối soát xong (fixture `a`, `j`).** Đo bằng
`DispatchOutcome.outbound_calls` của **chính dispatcher W5C** cộng một transport ghi lại mọi lời
gọi (nó raise nếu bị gọi). Sau restore: `dispatch_next` ⇒ `RESTORE_UNVERIFIED`, 0 lời gọi;
`worker.claim_assignment`, `analysis.claim_task`, `delivery.dispatch_next` đều bị guard chặn
bằng `RESTORE_UNVERIFIED`.

**Oracle 3 — hash Saved không đổi (fixture `e`).** `saved_snapshot.content_hash` trước backup =
sau restore = sau reconcile, và được **tính lại** từ payload trên đĩa bằng
`server.app.saved.snapshot.hash_matches` (không chỉ so với chính nó).

**Oracle 4 — lease cũ (fixture `b`).** Mọi `assignment_lease` `held` bị chuyển `revoked` trước
khi bất cứ thứ gì mở ra; `lease_epoch` của hàng đó **không** đổi (đó là epoch mà worker sống sót
sẽ trình ra), và claim bị chặn độc lập bằng `RESTORE_UNVERIFIED`.

**Mệnh đề 4 và 7 (fixture `j`) — điểm sắc nhất của gói.** Với `integrity_check_outcome = passed`
và mọi count khớp manifest, `reconciliation_complete` **vẫn false**, ở đúng hai mệnh đề fixture
pin: `unmet == (4, 7)`, `met == {1,2,3,5,6}`, `dispatcher_unlocked_at` vẫn NULL, 0 tin gửi. Có
thêm một test cho "ack một mình không đủ" (mệnh đề 7 đạt, 4 chưa) để chặn cách hiểu coi chữ ký
của Operator là chìa khóa vạn năng.

**Mặt dương (fixture `m`).** Sau `verify` → `review_intent(hold)` → `acknowledge`, cả bảy mệnh đề
đạt ⇒ `storage.health = healthy`, `dispatcher_unlocked_at` được ghi, claim chạy lại được — **và**
intent generation cũ vẫn **không** được gửi (0 outbound), `restore_generation` của nó không đổi.
`delivery_part` `unknown` vẫn `unknown` qua toàn bộ chu trình.

**`SG-DENY` / `CR-PC08-02`.** 0 route nào trên app mang `operation_id` bắt đầu bằng `backup.`;
caller ngoài `MOD-backup-cli` ⇒ `FORBIDDEN_EDGE`; CLI từ chối khi token sai, thiếu, hoặc khi
`expected` chưa cấu hình (default deny). Restore đòi cụm từ gõ tay, so sánh constant-time.

## 5. Ba điều hợp đồng bắt được mà thiết kế đầu tiên đã bỏ sót

Ghi lại vì cả ba là lỗi thật, không phải chi tiết:

1. **Restore chỉ chạy trong `maintenance`.** `T-ST-05` là `maintenance → recovery_required`;
   **không có** cạnh từ `healthy`. Bản đầu gọi thẳng `mark_recovery_required` từ `healthy` và
   máy trạng thái của WR từ chối. Cửa sổ maintenance **chính là** cái khóa side effect mà tiêu
   đề card nói tới, và `storage.yaml` cấm vào nó mà không có thao tác explicit của Operator —
   nên `restore_snapshot` **từ chối** thay vì tự mở, và việc mở là một lệnh CLI riêng.
2. **`new_restore_generation` phải lớn hơn mọi generation đang tồn tại**, không chỉ hơn
   `MAX(restore_record)`. Lấy một maximum thì lần restore **đầu tiên** sinh generation 1, và
   mọi `outbox_intent` khôi phục từ snapshot vốn mang generation 1 sẽ ra khỏi restore ở trạng
   thái **đủ điều kiện gửi** — đúng thất bại mà I15 tồn tại để chặn, và chỉ xuất hiện ở lần
   restore đầu tiên, tức lần chưa ai diễn tập. Nay lấy max của cả `restore_record` lẫn
   `outbox_intent`.
3. **Không được tự thêm cột.** Bản đầu thêm `snapshot_request_id` và `restore_request_id` để
   hiện thực idempotency mà `ports.yaml` đòi. `entities.yaml` không khai hai cột đó, và
   `tests/contract/test_schema_matches_entities.py` — một test của card khác, kiểm **cả hai
   chiều** giữa DDL và hợp đồng — đỏ ngay. Đó đúng là hành vi mong muốn của test đó, nên hai
   cột đã bị gỡ và idempotency được làm bằng những gì hợp đồng thực sự cấp (`CR-TC-BACKUP-07`).
   Không sửa test của người khác, không nới hợp đồng.

## 6. Change requests

| ID | Nội dung | Đề nghị |
| --- | --- | --- |
| `CR-TC-BACKUP-01` | §3 không cấp `server/app/backup/router.py`, nhưng `openapi.yaml` khai bốn route HTTP cho `backup.*`. | Coordinator đã ruling: CLI-only, ghi lại divergence. Hệ quả **mạnh hơn** yêu cầu: không có bề mặt HTTP nào, nên đường "phiên trình duyệt kích hoạt restore" (`CR-PC08-02`) không tồn tại chứ không chỉ bị từ chối. Nếu muốn HTTP thì cần amend write set. |
| `CR-TC-BACKUP-02` | Fixture `d` khai `backup_snapshot.state = 'invalid'` và `integrity_check_outcome = 'mismatch'`; `backup-restore.md` §5.6 mệnh đề 1 khai `'ok'`. `entities.yaml` không có cả ba giá trị (`running/completed/failed/verified`, `passed/failed/not_run`). | Theo ruling, entity thắng: ghi `failed` và `passed`. Ánh xạ được **pin bằng test**, nên mở rộng enum sẽ làm test đỏ thay vì để hai bên trôi ra xa nhau. Đề nghị sửa fixture + §5.6. |
| `CR-TC-BACKUP-03` | §5.6 mệnh đề 4 và fixture `a`/`j`/`m` dùng từ vựng của `delivery_part` cho `outbox_intent.dispatch_state` (`pending`, `retry_wait`, `sent`) và `intent_type: report_digest`; enum thật là `ready/claimed/done/held_for_review` và `telegram_digest/telegram_alert`. | Theo ruling, entity thắng: mệnh đề 4 đọc `ready`. Cũng được pin bằng test. Đề nghị sửa văn bản §5.6 và ba fixture. |
| `CR-TC-BACKUP-04` | `ENT-schema-migration` chưa được card nào hiện thực, nên `MAX(schema_migration.version)` không tính được và `backup_snapshot.schema_migration_version` phải là NULL. | Theo ruling: NULL + ghi alembic head vào manifest; `verify` đọc lại revision từ trong artifact nên bước 3 của §5.3 vẫn có thứ thật để so. Đề nghị hoặc cấp bảng cho `MOD-data-store`, hoặc đổi hợp đồng sang revision string. |
| `CR-TC-BACKUP-05` | **Mới.** `ports.yaml` `backup.restore_snapshot` không có mã nào cho "sai `storage.health`", trong khi `data.purge_all` dùng `CONFLICT` cho **đúng** tiền điều kiện đó (`chỉ chạy khi maintenance`). | Thêm `CONFLICT` vào `error_codes` của `backup.restore_snapshot`. Hiện tại tiền điều kiện trả `VALIDATION_ERROR` với `field_path = storage_health`; hành vi đúng, mã là thứ duy nhất cần đổi. |
| `CR-TC-BACKUP-07` | **Mới, và đã gây một lỗi thật ở gói này.** `ports.yaml` bắt `backup.create_snapshot` idempotent theo `snapshot_request_id` và `backup.restore_snapshot` theo `restore_request_id`, nhưng `entities.yaml` **không khai cột nào** trên hai bảng để giữ chúng. Bản đầu của gói này tự thêm hai cột, và `tests/contract/test_schema_matches_entities.py` (của card khác) bắt được ngay: "ships but entities.yaml does not declare it". | Thêm hai cột vào `ENT-backup-snapshot` và `ENT-restore-record`. Trong lúc chờ: **đã gỡ** hai cột; snapshot replay theo `artifact_path` (cột đã khai), còn restore lần hai bị chặn bởi chính tiền điều kiện `maintenance` (sau restore, health là `recovery_required`). Giới hạn được ghi rõ trong docstring và test, không giả vờ là idempotency đầy đủ. |
| `CR-TC-BACKUP-06` | `backup-restore.md` §5.6 mệnh đề 3 đòi so `leases_revoked` với "số assignment_lease non-terminal **có trong snapshot**", nhưng sau restore không còn cách đọc snapshot để đếm — DB hiện hành đã là bản khôi phục. | Đo bằng phép đo kiểm được: "không còn lease nào ở `held`". Đề nghị §5.6 nói bằng phép đo đó, hoặc `backup_manifest.counts` thêm khóa `assignment_lease.held`. |

## 7. Còn mở / `NOT_RUN`

- **Diễn tập restore thật, RPO/RTO đo được: `NOT_RUN` (E3).** Cần môi trường của Owner
  (`SG-03`, card §8, `backup-restore.md` §5.7). Cái đã chạy chứng minh hệ thống **từ chối** đúng
  chỗ; **không** chứng minh nó khôi phục được một hệ thống thật trong 2 giờ. Hash của artifact
  không phải bằng chứng khôi phục được — `entities.yaml` nói vậy và lần chạy này không phản bác.
- `data.purge_all`: không hiện thực (`SG-02`, §1 non-goal). Fixture `recovery/l` chỉ được đọc.
- Bốn route HTTP `backup.*`: `NOT_RUN` (không tồn tại — `CR-TC-BACKUP-01`).
- Artifact model embedding: không có file thật để hash; mệnh đề 6 kiểm qua bảng
  `embedding_generation`, không qua file.
- Hành vi của collector thật mang epoch cũ (fixture `b` seq1/seq2): thuộc
  `TC-scheduler-lease-claim` / `TC-ingest-*`, `NOT_RUN` ở đây.
- Retention và `backup_schedule` (PROVISIONAL trong hợp đồng): không hiện thực.
- `evidence/index.json` thuộc PC09, ngoài write set — đăng ký run là việc của Coordinator.
- Ghi nhận (không phải của gói này): `CR-TC-REPORT-09` của W4A làm hỏng 18 test setup trong hai
  file của W5C. Gói này không chạm hai file đó; số liệu toàn bộ suite ở bản ghi bằng chứng nêu
  rõ phần nào là của ai.

## 8. `PKT-TC-BACKUP-FIX1` — kế toán fixture §2 (`E0-20-card-fixture-accounting`)

Kiểm tra mới báo một fixture của §2 không được test nào chạm và không được handoff nào nêu tên:
`acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json`.

**Phần ĐÃ chạy.** Fixture này khẳng định một điều thuộc đúng card này:

> `backup_snapshot` / `backup_manifest` / `restore_record` còn nguyên hàng, và artifact backup
> trên đĩa **không bị chạm**.

`tests/integration/test_restore_side_effect_lock.py::test_purge_all_keeps_every_backup_table_and_artifact`
nạp fixture **theo tên** qua loader của `tests/conftest.py` và khẳng định ba đường độc lập,
không cần purge tồn tại: (a) ba bảng nằm trong `_retained_tables` của chính fixture và **không**
nằm trong `_purged_tables` hay `_never_purged_tables`; (b) `TXN-purge-all` trong
`contracts/data/entities.yaml` nói y hệt — bản sao trong fixture không được trôi khỏi nguồn;
(c) toàn bộ mã của `server/app/backup/` không chứa câu nào có thể xóa một hàng backup hay một
artifact (`DELETE FROM backup_*`, `DROP TABLE backup_*`, `unlink`, `rmtree`), và các hàng do
chính lần chạy này tạo vẫn còn sau trọn chu trình restore.

Điều đó đáng kiểm chứ không chỉ là kế toán: nó là lý do hộp thoại xác nhận **phải** nói với chủ
nhà rằng dữ liệu vừa purge **vẫn còn** trong backup (`backup-restore.md` §8). Nếu ba bảng này
trôi sang tập bị xóa thì "xóa hẳn" và "xóa dữ liệu nghiên cứu" âm thầm thành một.

**Phần `NOT_RUN`, kèm lý do cụ thể.** Mọi phần còn lại của fixture `l` —
`data.purge_all` hai pha (`request_challenge` → `execute`), cụm từ gõ tay, tiền điều kiện
`storage.health = maintenance`, thu hồi lease trước khi xóa, bốn ca âm (cụm từ sai, sai trạng
thái storage, sai principal, dùng lại challenge), và phép đếm 37 bảng về 0 / 20 bảng giữ lại —
là **`NOT_RUN`**. Lý do không phải thiếu thời gian mà là phạm vi: `data.purge_all` thuộc
`MOD-data-admin-service`, card §1 liệt kê nó là **non-goal**, và `SG-02` cấm card này hiện thực
purge. Không có operation nào để gọi và không có bảng `purge_challenge` nào tồn tại; viết một
purge ở đây để làm xanh một phép kiểm sẽ đúng là thứ `SG-02` cấm. Fixture chờ card của
`MOD-data-admin-service`.

## 9. `PKT-TC-BACKUP-FIX2` — `CR-TC-DELIVERY-11`: `expected_vector_count` NULL

**Lỗi thật, do W5C tìm ra.** `_embedding_ok` gọi `int()` thẳng lên `expected_vector_count`.
`entities.yaml` khai cột đó **nullable**, nên với một hàng NULL mệnh đề 6 ném `TypeError` thay
vì trả một phán quyết — W5C phải seed cột đó để test của họ đi qua được, và đã đánh dấu chỗ đó
trong test của mình. Đúng là một lỗi, không phải chuyện phong cách: một mệnh đề của
`reconciliation_complete` mà *sập* thì không từ chối cũng không chấp nhận, nó chỉ làm hỏng cả
phép đối soát.

**Ngữ nghĩa NULL đã chọn: `UNMET`, kèm lý do được nêu tên.** Trích `backup-restore.md` §5.3
bước 5 ("`embedding_generation` active có `built_vector_count == expected_vector_count`") và
§5.6 mệnh đề 6 ("generation active hợp lệ, **hoặc** selection đang bị chặn có lý do đã ghi").
`entities.yaml` định nghĩa `expected_vector_count` là "số vector **phải có trước khi** được phép
chuyển sang `active`". Vậy NULL trên một hàng **đang active** nghĩa là tiền điều kiện đã gác
việc kích hoạt **chưa từng được ghi**, và bản khôi phục không có cách nào chứng minh index là
đầy đủ. Trả "met" ở đó là biến *chưa xác định* thành *tốt* — đúng thứ `I13`/`CAP-P5` cấm — và sẽ
mở lại selection trên một index không ai chứng minh được là nguyên vẹn (`I12`).

Ba đầu vào, ba phán quyết khác nhau, mỗi cái có test riêng:

| Trạng thái | Mệnh đề 6 | Lý do trả về |
| --- | --- | --- |
| Không có generation `active` | **met** | Không có index để selection chạy lên; không có gì để bảo vệ |
| `active`, `expected_vector_count` NULL | **unmet** | "không có mốc nào để kiểm generation đã dựng đủ chưa" |
| `active`, `built != expected` | **unmet** | Nêu đích danh hai con số |
| `active`, `built == expected` | **met** | — |

`_embedding_ok` nay trả `(met, reason)` và `evaluate` đưa `reason` vào report, nên người vận
hành biết mình đang ở ca nào chứ không chỉ biết "mệnh đề 6 trượt". Test mới cũng khẳng định lỗi
đi ra ngoài dưới dạng `RESTORE_UNVERIFIED` với mệnh đề 6 trong `unmet_clauses`, và storage vẫn ở
`recovery_required` — không có ngoại lệ nào thoát khỏi operation.

Mọi mục ở trên là `SELF_VALIDATION`. **Không** mục nào là independent audit.

---

*`PKT-TC-BACKUP` (e1) + `PKT-TC-BACKUP-FIX1` (e2) + `PKT-TC-BACKUP-FIX2` (e3) · `worker-W6B` · `lease_released_at` 2026-09-08T06:40Z · ceiling
`IMPLEMENTATION_VERIFIED` cho phạm vi E1/E2 của card; diễn tập thật `NOT_RUN`.*
