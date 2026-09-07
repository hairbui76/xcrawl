# HANDOFF — `TC-saved-snapshot` (`MOD-saved-service`)

| Trường | Giá trị |
| --- | --- |
| packet | `PKT-TC-SAVED` · lease `LEASE-TC-SAVED-e1` · authority `AUTH-COORD-TC-SAVED` (dưới `AUTH-OWNER-20260908-10`) |
| worker | `worker-W5B` |
| card | `agent-tasks/TC-saved-snapshot.md` (§1–§13 ràng buộc) |
| pin epoch | `PC10-PIN-P3-20260908` — verify lại toàn bộ §0 trước dòng code đầu tiên: **32/32 file khớp, 0 lệch** |
| status | `DONE` · claim `IMPLEMENTATION_VERIFIED` cho đúng phạm vi card |
| audit_route | Coordinator quyết định; gói này **không** tự nhận đã qua review độc lập |
| evidence | `evidence/runs/TC-saved-snapshot-E1-20260908T020500Z.json` (validate sạch với `evidence/manifest.schema.json`) |
| next actor | Coordinator |
| `lease_released_at` | 2026-09-08T02:10Z |

## 1. Cổng chờ và baseline

Cổng chờ mở đúng hai vế: `agent-tasks/README.md` §pin khai `PC10-PIN-P3-20260908`, và
`evidence/handoffs/PC10-handoff.md` mang addendum `PKT-PC10-FIX24` với
`lease_released_at 2026-09-08T00:45Z`. Trong lúc chờ, gói này chỉ **đọc** (hợp đồng, fixture,
mã đã land của Giai đoạn 0–2).

`SG-HASH` chạy ngay trước lần ghi đầu tiên: tính lại `sha256` + byte count cho cả 32 dòng đã
pin ở §0 (2 nguồn + 30 hợp đồng/fixture). **0 lệch.** `SG-PC09`: đọc bản mới nhất của
`acceptance/scenarios.yaml` — SC12, SC13, SC48, SC32, SC49 **không** mâu thuẫn với §8; SC48 nói
"hai ca dương" trong khi §3 viết "1 pos + 5 neg", nên gói này kiểm **cả hai** ca dương (xem
`CR-TC-SAVED-03`).

## 2. Trạng thái file

Baseline của mọi target là `ABSENT` trừ `server/app/main.py` (MODIFY, chỉ một khối include có
phân định) — không file nào bị ghi đè ngoài ý muốn.

| Đường dẫn | Thao tác | sha256 sau | bytes |
| --- | --- | --- | --- |
| `server/app/saved/snapshot.py` | CREATE | `baed87d3b2e20a639c128c45e51f58ac97d73b8fb112b71453c05e0d1b418bd7` | 13529 |
| `server/app/saved/service.py` | CREATE | `c9830c23dec47288ac3b34a5f4f3a524a1059816c99a6537338ef3d78b0bbb44` | 50758 |
| `server/app/saved/router.py` | CREATE | `18f7bcd5d88cd7f470431bfeae7529bd9544b2692cdc3e0c149111ae0c0450b2` | 19114 |
| `server/migrations/versions/0008_tc_saved_snapshot.py` | CREATE | `f1c5c6b42412d77098dc5d8af40be8586008f95c815684a122f392b6575f2fe0` | 9894 |
| `tests/contract/test_saved_snapshot_schema.py` | CREATE | `b106112fb00e0d9fccd2a35b1321533ecc2d6e565f6e11a6d924d036ac683c58` | 16549 |
| `tests/integration/test_concurrent_save.py` | CREATE | `89a73368cdc7e8cb592830047191a399352c8fec797e85bdcfd9cb656fa1fd5c` | 27029 |
| `tests/integration/test_snapshot_survives_delete.py` | CREATE | `f5c11d768b9399746728debd8b883cd703e9135684b1d18bf27ee26e87b2836f` | 27339 |
| `server/app/main.py` | MODIFY (append 1 include block) | `8d534ebea326038a2633e07449a06bb5d71bd3828e9413850936320447cfcb59` | 11088 |
| `evidence/runs/TC-saved-snapshot-E1-20260908T020500Z.json` | CREATE | (bản ghi bằng chứng) | 18146 |
| `evidence/handoffs/TC-saved-snapshot-handoff.md` | CREATE | (file này) | — |

**Không** có `server/app/saved/__init__.py`: `server/app/research/` đã đặt tiền lệ dùng
namespace package, và §3 không cấp file đó.

`server/app/main.py` chỉ nhận đúng một khối `# >>> TC-saved-snapshot … # <<< TC-saved-snapshot`
đặt sau khối của `TC-telegram-linking-auth`; import nằm **trong** khối (F-A3R1-13). Không byte
nào ngoài khối bị đổi.

**Không** chạm `precode/`, `contracts/`, `acceptance/`, `agent-tasks/`. Không mutation git.
Không lời gọi mạng nào. `PYTHONDONTWRITEBYTECODE=1` suốt phiên.

## 3. Migration — nhận bàn giao, không tạo lại

`0002b_shared_move_set_tables` đã tạo `saved_snapshot` và `saved_item` **thay mặt module này**
và header của nó yêu cầu card tiếp quản phải **mở rộng** chứ không `CREATE TABLE` lần hai
(`CR-TC-IDENTITY-11..13`). Gói này làm đúng vậy.

Đối chiếu từng cột với `entities.yaml`: `saved_item` đã đầy đủ — 14 cột, `ux_saved_active_owner_target`,
`ux_saved_idempotency`, FK `saved_snapshot_id` RESTRICT, hai CHECK. **Không đụng đến nó.**
`saved_snapshot` thiếu **đúng một** thứ: `analysis_id_at_save` được khai là *"FK → analysis.id"*
nhưng 0002b để nó trần (0002b tạo `saved_snapshot` **trước** `analysis`, nên nó không thể làm
khác). Thiếu khóa ngoại đó thì oracle của `TXN-delete-target` — *"không tồn tại hàng `analysis`
bị xóa mà vẫn được `saved_snapshot` trỏ tới — kiểm bằng FK, phải là 0 vi phạm"* — không có gì để
kiểm. `0008_tc_saved_snapshot` thêm đúng khóa ngoại đó (`ON DELETE RESTRICT`) bằng rebuild
rename/copy/drop, đổi tên bảng con **trước** bảng cha để schema luôn parse được, drop/tạo lại hai
index theo đúng định nghĩa của 0002b, và bỏ cột generated `target_key` khỏi INSERT để SQLite tự
tính. `downgrade()` khôi phục đúng định nghĩa cũ. Diff hai định nghĩa `saved_snapshot` là **một dòng**.

**Một head:** `alembic heads` = `['0009_tc_telegram_unknown_delivery']` (W5C nối tiếp
`0008_tc_saved_snapshot`). Kiểm bằng `len(heads) == 1` theo cấu trúc, không so với một tên cụ thể.

## 4. Điều đã chứng minh (E1 + E2)

Ba lệnh của §8, exit 0 mỗi lệnh:

```
python -m pytest tests/contract/test_saved_snapshot_schema.py -q      → 18 passed
python -m pytest tests/integration/test_concurrent_save.py -q         → 17 passed
python -m pytest tests/integration/test_snapshot_survives_delete.py -q → 12 passed
```

Toàn bộ testpaths của repo: exit 0, 0 failed, 11 xfailed (không cái nào thuộc gói này).
`ruff check` + `ruff format --check` sạch; `mypy --strict` sạch trên 4 file nguồn.

Bốn oracle của §8, đo bằng đếm hàng và so hash:

1. **`COUNT(saved_item active WHERE target=T) ≤ 1`.** Hai luồng chạy `save.create` đồng thời
   (app + Telegram) trên một database ⇒ `saved_item__total = 1`, `active = 1`,
   `saved_snapshot = 1`, `orphan_saved_snapshot = 0`, hai bên nhận **cùng một** `saved_item_id`,
   một bên `created` một bên `already_saved`. Năm lần bấm Telegram ⇒ 1 hàng, 5 phản hồi.
   Và bài kiểm nghiêm nhất: **bịt mắt** cả hai phép đọc "đã lưu chưa" rồi gọi lại — vẫn không có
   hàng thứ hai, vì UNIQUE partial là trọng tài chứ không phải một phép đọc trước khi ghi
   (`entities.yaml` liệt kê check-then-insert là cách hiện thực **bị cấm**).
2. **`content_hash` không đổi.** Một khẳng định gộp bốn mốc: sau khi lưu → sau khi
   `post.source_deleted_observed_at` được ghi → sau khi khởi động lại (engine mới trên cùng file)
   → sau `VACUUM INTO` + copy sang đường dẫn sạch. `len(set(...)) == 1`. Tại mỗi mốc hash được
   **tính lại** từ chính bytes `payload` trên đĩa, nên "bằng chính nó" không đủ để pass.
   Rằng phép tính đó khớp **hợp đồng** được chứng minh riêng: hai fixture dương mang chuỗi hex
   thật (`sha256:8e3ca77f…`, `sha256:17f5b053…`) tính bên ngoài repo, và
   `compute_content_hash` tái lập **đúng cả hai**.
3. **Năm fixture âm ⇒ `VALIDATION_ERROR`, 0 hàng ghi.** Cả năm bị schema Draft 2020-12 từ chối;
   ngoài ra mỗi khuyết tật còn bị chặn ở tầng thật với số hàng không đổi: summary thiếu dòng hạn
   chế ⇒ `VALIDATION_ERROR` từ service; target đặt cả hai id ⇒ `VALIDATION_ERROR` ở biên **và**
   CHECK của bảng; `saved_snapshot_id` NULL, `content_hash` NULL, `content_hash = 'deadbeef'` ⇒
   NOT NULL / `GLOB 'sha256:*'` của bảng.
4. **Sau `save.remove` và sau khi bài gốc bị xóa: snapshot vẫn đọc được.** `save.remove` đổi
   `state` → `unsaved` và ghi `unsaved_at`, không đụng snapshot; lặp lại là idempotent
   (`removed: false`); lưu lại tạo hàng **mới** với snapshot **mới** và giữ hàng cũ làm lịch sử.
   Xóa `post_work` + `post` phía dưới ⇒ snapshot y nguyên và vẫn trả nội dung post.

Thêm, ngoài bốn oracle:

- **I17 với merge thật.** Chạy `identity.merge_works` của `MOD-identity-service` (không mô phỏng):
  `saved_item.target_work_id` theo work thắng, `saved_snapshot` **byte-identical**,
  `target_key_at_save` vẫn trỏ target lúc lưu.
- **`SG-DENY`.** NC-01 (collector token), NC-20 (analysis worker token), NC-36 (không credential)
  ⇒ `UNAUTHORIZED` 401 với **0 thay đổi hàng**; chat Telegram chưa liên kết ⇒
  `UNAUTHORIZED_COMMAND` 403, 0 thay đổi hàng; caller module ngoài registry gọi thẳng service ⇒
  `FORBIDDEN_EDGE` kèm `forbidden_edge_ref: FE-14`. Bốn mã khác nhau cho bốn tình huống khác
  nhau, đúng bảng R5-01.
- **`SG-01`.** Không route nào mang `operation_id = save.export`; có test khẳng định điều đó.
- **E2.** Bơm lỗi ổ đĩa giữa transaction ⇒ 0 `saved_item`, 0 `saved_snapshot`, không trạng thái
  nửa vời. Guard từ chối ⇒ `STORAGE_WRITE_FAILED` 503 với `writes_attempted == 0`, tức là hỏi
  **trước khi** mở transaction (I02), không phải thử rồi bắt lỗi.
- **Tích hợp thật với hai card anh em**: `CommandPorts.save_create` của
  `TC-telegram-linking-auth` (`/save` plain-text, 5 lần bấm → 1 hàng, 5 reply, không
  `parse_mode`/keyboard/`callback_data`) và `identity.merge_works`. Cả hai đã land nên **không**
  phải xfail; hai `importorskip` vẫn ở đó để test tự khai lý do nếu gói kia biến mất.

## 5. Ranh giới module — hai đường **không** đi

- **`identity.resolve_target`.** Card §4 liệt kê nó là consumes, nhưng `contracts/modules.yaml`
  cho `MOD-saved-service` `outbound_operations: []` và **không có** dòng `allowed_edges` nào với
  module này làm caller. Dưới `default_deny`, gọi nó là `FORBIDDEN_EDGE`. Registry thắng văn xuôi
  của card (chính §5 nói vậy), nên module này phân giải target bằng cách đọc hàng `work`/`post`
  được trỏ tới. → `CR-TC-SAVED-01`.
- **`storage.get_health`.** Cũng chỉ có hai caller được cấp (`MOD-health-service`,
  `MOD-job-service`). Cái được dùng là `StorageGuard.assert_writable` trong tiến trình — cùng cửa
  mà `MOD-ingest-service` dùng — không phải một lời gọi qua cạnh `MOD-data-store`.

## 6. Change requests

| ID | Nội dung | Đề nghị |
| --- | --- | --- |
| `CR-TC-SAVED-01` | Card §4/§5 cho `MOD-saved-service` gọi `identity.resolve_target` và `storage.get_health`; `contracts/modules.yaml` khai `outbound_operations: []` và không có cạnh nào. Hai hợp đồng trả lời khác nhau cho cùng câu hỏi. | Coordinator phán quyết: hoặc thêm hai dòng `allowed_edges`, hoặc sửa §4/§5 của card. Gói này đi theo registry (không gọi) và ghi rõ. |
| `CR-TC-SAVED-02` | `ports.yaml` `save.create.error_note_vi` nói transaction thua "trả `CONFLICT`"; fixture `identity/d` và `telegram/j` nói bên thua nhận body `already_saved: true`; `entities.yaml` nói `already_saved` là **trường phản hồi, không phải mã lỗi** và bắt buộc đọc-rồi-trả. SC13 chấp nhận "trả lại receipt đã commit". | Đọc hòa: `CONFLICT` là mã đã đăng ký cho **lớp va chạm**, còn phản hồi của operation là `already_saved`. Gói này theo fixture. Đề nghị làm rõ một câu trong `ports.yaml`. |
| `CR-TC-SAVED-03` | (a) §3 viết "1 pos + 5 neg" nhưng SC48 viết "hai ca dương" và liệt kê cả `j` lẫn `k`. (b) `acceptance/fixtures/recovery/k-delete-target-preserves-saved.json` dùng `saved_item.state = "saved"`, **không** thuộc enum của `entities.yaml` (`active`/`unsaved`/`superseded_by_merge`). | (a) sửa §3 thành 2 pos. (b) sửa fixture về `active`. Gói này kiểm cả hai ca dương và dùng `active`; **không** sửa fixture. |
| `CR-TC-SAVED-04` | `snapshot_content.summary` là `required` với ba trường `minLength: 1`, nhưng `saved_snapshot.analysis_id_at_save` được phép NULL "khi target chưa có analysis valid nào". Hai điều đó không thể cùng đúng trừ khi có chữ cho **nhãn thiếu** của B16 — không hợp đồng nào cấp chữ đó. | Owner quyết định câu chữ của nhãn thiếu, hoặc chốt rằng không lưu được target chưa phân tích. Hiện tại: `VALIDATION_ERROR`, **0 hàng ghi** — hướng an toàn, không bịa nội dung vào một hàng bất biến. |
| `CR-TC-SAVED-05` | `openapi.yaml` cho `save.list` (200) `$ref` tới `saved-snapshot.schema.json`, tức schema của **một** mục, trong khi operation trả một danh sách có phân trang (`limit` + `cursor`). | Cấp một schema bao (`items[]` + `next_cursor`). Gói này trả `{schema_version, items[], count, next_cursor?}`, mỗi phần tử validate đúng schema một-mục. |
| `CR-TC-SAVED-06` | `IdempotencyKeyHeader` là `required: true` cho `save.create`, nhưng `ENT-saved-item.idempotency_key` là **NULL cho Save trong app**. | Làm rõ. Gói này yêu cầu header (theo openapi) nhưng chỉ **lưu** giá trị cho kênh `telegram` (theo entities); với kênh app, UNIQUE partial trên hàng active là trọng tài. |
| `CR-TC-SAVED-07` | `SaveCreatePort.create_save` của `TC-telegram-linking-auth` khai tham số `report_item_id`; chưa có bảng `report_item` để phân giải sang target. | Khi `TC-report-coverage-publish-cas` land: đổi `TelegramSaveAdapter` (một chỗ duy nhất) để tra `report_item.analysis_id`. Hiện tại tham số được đọc như một target reference — đúng thứ `x-idempotency.key_scope: owner_id + target_ref` khóa lên. |
| `CR-TC-SAVED-08` | `recovery/k` kỳ vọng `data.delete_target` xóa hàng `work` **và** giữ `saved_item` trỏ tới nó; nhưng `saved_item.target_work_id → work(id)` là `ON DELETE RESTRICT` (0002b). Hai điều đó không thể cùng đúng. | Thuộc `TC-*-data-admin`, không phải card này. Cần một phán quyết: hoặc `saved_item` chuyển sang `superseded_*`/nới FK, hoặc `data.delete_target` không xóa `work` còn Saved trỏ tới. Ghi lại ở đây vì nó chạm bảng của module này. |
| `CR-TC-SAVED-09` | `openapi.yaml` khai 503 `STORAGE_WRITE_FAILED` cho `save.create` với chữ "`write_blocked` hoặc `maintenance`: mutation KHÔNG được ACK và KHÔNG có gì được ghi", nhưng `contracts/state/storage.yaml` **không** liệt kê `save.create` trong `write_blocked.refuses`/`maintenance.refuses`. | Thêm `save.create` (và `save.remove`) vào danh sách `refuses`. Gói này gọi `guard.assert_writable` trên đường bình thường nên nó tự có hiệu lực khi hợp đồng bổ sung; có một test **pin đúng sự lệch này** để việc đóng CR làm test đỏ và buộc xem lại. |

## 7. Còn mở / `NOT_RUN`

- E3 (live) và E4 (review nội dung): `NOT_RUN`. Card §8 ghi "không cần live".
- `data.delete_target`, `data.purge_all`, `save.export`: **không** hiện thực (§1 non-goals, `SG-01`).
- Nhánh `report_ref` của snapshot: `NOT_RUN` — `report_item` chưa tồn tại
  (`TC-report-coverage-publish-cas`, Giai đoạn 4).
- Drill backup/restore thật và bước reconcile sau restore (I15): `NOT_RUN` — thuộc
  `TC-backup-restore-drill`, Giai đoạn 6. Ở đây chỉ có `VACUUM INTO` + copy.
- `matched_tags` chưa được kiểm end-to-end với `MOD-tag-service` (chưa tồn tại).
- Đồng thời được kiểm bằng hai **luồng** trong một tiến trình; hai **tiến trình** là `NOT_RUN`.
- `evidence/index.json` thuộc PC09 và **không** nằm trong write set của gói này, nên bản ghi run
  chưa được đăng ký ở đó — việc của Coordinator.

Mọi mục ở trên là `SELF_VALIDATION`. **Không** mục nào là independent audit.

---

*`PKT-TC-SAVED` · `worker-W5B` · `lease_released_at` 2026-09-08T02:10Z · ceiling
`IMPLEMENTATION_VERIFIED` cho phạm vi card.*
