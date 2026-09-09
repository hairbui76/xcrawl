# HANDOFF — `TC-saved-snapshot` (`MOD-saved-service`)

| Trường | Giá trị |
| --- | --- |
| packet | `PKT-TC-SAVED` (e1) + `PKT-TC-SAVED-FIX1` (e2) + **`PKT-TC-SAVED-FIX2`** (e3) · lease `LEASE-TC-SAVED-e3` · authority `AUTH-COORD-TC-SAVED` (dưới `AUTH-OWNER-20260908-10`) |
| worker | `worker-W5B` |
| card | `agent-tasks/TC-saved-snapshot.md` (§1–§13 ràng buộc) |
| pin epoch | `PC10-PIN-P3-20260908` — verify lại toàn bộ §0 trước dòng code đầu tiên: **32/32 file khớp, 0 lệch** |
| status | `DONE` · claim `IMPLEMENTATION_VERIFIED` cho đúng phạm vi card |
| audit_route | Coordinator quyết định; gói này **không** tự nhận đã qua review độc lập |
| evidence | **`evidence/runs/TC-saved-snapshot-E1-20260909T091000Z.json`** (validate sạch). Bản e1 `…T020500Z.json` và e2 `…T054000Z.json` nay **STALE** |
| next actor | Coordinator |
| `lease_released_at` | e1 2026-09-08T02:10Z · e2 2026-09-08T05:45Z · **e3 2026-09-09T09:15Z** |

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
| `server/app/saved/snapshot.py` | CREATE | `1b0257548947a101fb8520c53d35a13780b1c2ed02fe10dffaefda040d1c0b8d` | 16669 |
| `server/app/saved/service.py` | CREATE | `4fb58438dc2a277dbc5efca3655dc467a91e0223a5f3b3ba6feb15e3d4e89302` | 51730 |
| `server/app/saved/router.py` | CREATE | `18f7bcd5d88cd7f470431bfeae7529bd9544b2692cdc3e0c149111ae0c0450b2` | 19114 |
| `server/migrations/versions/0008_tc_saved_snapshot.py` | CREATE | `f1c5c6b42412d77098dc5d8af40be8586008f95c815684a122f392b6575f2fe0` | 9894 |
| `tests/contract/test_saved_snapshot_schema.py` | CREATE | `fd7e3fef3cf5b504e4448d79d1f945935c5f78ba80ae0b7efd4d783ed32bb5b5` | 20809 |
| `tests/integration/test_concurrent_save.py` | CREATE | `89a73368cdc7e8cb592830047191a399352c8fec797e85bdcfd9cb656fa1fd5c` | 27029 |
| `tests/integration/test_snapshot_survives_delete.py` | CREATE | `f5c11d768b9399746728debd8b883cd703e9135684b1d18bf27ee26e87b2836f` | 27339 |
| `server/app/main.py` | MODIFY (append 1 include block) | **không pin** (xem §9) — khối của card: `8639af05…38d9c`, 957 B | — |
| `evidence/runs/TC-saved-snapshot-E1-20260908T020500Z.json` | CREATE (e1, nay **STALE**) | (bản ghi bằng chứng) | 18146 |
| `evidence/runs/TC-saved-snapshot-E1-20260908T054000Z.json` | CREATE (e2, nay **STALE**) | (bản ghi bằng chứng) | 20405 |
| `evidence/runs/TC-saved-snapshot-E1-20260909T091000Z.json` | CREATE (e3) | (bản ghi bằng chứng thay thế) | 21199 |
| `evidence/handoffs/TC-saved-snapshot-handoff.md` | CREATE | (file này) | — |

`server/app/main.py` **không được pin ở bất kỳ đâu trong bản ghi này** (ruling P4, §9). Nó là
factory dùng chung: nhiều card nối thêm khối include của mình vào đó, nên mọi hash toàn-file
ghi ở đây sẽ cũ ngay lần land kế tiếp — e2 đã từng ghi một hash như vậy và nó đã cũ. Thứ
được pin là **khối có phân định của chính card** (957 byte, sha256 `8639af05…38d9c`), thứ
duy nhất card này viết trong file đó.

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
python -m pytest tests/contract/test_saved_snapshot_schema.py -q      → 20 passed
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

## 8. `PKT-TC-SAVED-FIX1` — `CR-TC-SAVED-04` đã đóng bằng `OD-20260908-10` mục 1

**Quyết định.** Lưu một target **chưa** có analysis nay được **PHÉP**; summary được đánh dấu
thiếu bằng một chuỗi cố định, không suy luận (B16); `content_hash` tính trên đúng bytes đã lưu;
analysis về sau gắn vào bằng reanalysis, **không** sửa snapshot cũ.

**Nhãn được biểu diễn thế nào — và vì sao không DỪNG.** Packet nói: nếu schema không có slot thì
dùng `summary = null` cộng một trường trạng thái schema đã cho; nếu không có cả hai thì DỪNG.
Kiểm tra trên bản schema **không đổi**:

- `summary` **là** `required` trong `snapshot_content`, `$ref` tới một object **không có nhánh
  null**, `additionalProperties: false`, và **không có** `summary_state`. ⇒ `summary = null`
  không biểu diễn được, và không có trường nhãn.
- Nhưng **trạng thái thì có slot đã khai**: `saved_snapshot.analysis_id_at_save` là nullable và
  mô tả của chính schema đọc là *"NULL **chỉ khi** target chưa có analysis valid nào"*. Đó đúng
  là trường trạng thái mà packet cho phép dùng.

Nên điều kiện DỪNG **không** thành lập, và không có trường nào bị bịa:

| Thành phần | Giá trị | Nguồn hợp pháp |
| --- | --- | --- |
| **Trạng thái** (thứ consumer nên rẽ nhánh) | `snapshot.analysis_id_at_save = null` | Trường đã khai, mô tả nói đúng nghĩa này |
| **Nhãn** (thứ người đọc thấy) | cả ba dòng bắt buộc = hằng `SUMMARY_NOT_ANALYSED` = `"(chưa phân tích)"` | Ba chuỗi `minLength: 1` đã có sẵn |
| `summary.comparator` | `"unknown"` | Sự thật về dữ liệu: không có nguồn so sánh |
| `summary.claim_kinds` | **vắng mặt** | Không có phát biểu nào; mảng rỗng vẫn khẳng định "đây là các loại phát biểu có mặt" |
| `content.analysis_ref` | **vắng mặt** | Optional; không có analysis để truy vết |
| `content.evidence_level` | `"post_only"` | Bậc **thấp nhất**; `REQ-D21` cấm nâng mức chứng cứ |

Hằng nằm ở một chỗ và giống hệt nhau ở cả ba dòng, nên nó **không thể** trở thành suy luận — có
test khẳng định hai target khác nhau sinh ra summary block **byte-identical**.

**Ranh giới được giữ, không bị nới.** Một analysis **tồn tại** nhưng thiếu dòng của `REQ-D20`
**vẫn bị từ chối** `VALIDATION_ERROR`, 0 hàng. Marker nghĩa là "chưa ai phân tích"; dùng nó cho
một analysis hỏng sẽ là xếp lỗi dữ liệu dưới một nhãn nói điều ngược lại, và làm chính marker
mất nghĩa cho ca nó sinh ra. Năm fixture âm vì vậy **vẫn từ chối như cũ**.

**Không thêm cột.** `test_schema_matches_entities.py` vẫn xanh — thay đổi này hoàn toàn nằm
trong `saved_snapshot.payload`, không có DDL nào bị chạm và không có migration mới.

**CR mới:** `CR-TC-SAVED-10` — xin `saved-snapshot.schema.json` một trường trạng thái/nhãn thật
(ví dụ `summary` nullable + `summary_state: present | not_analysed`, hoặc một `content.notice`),
để consumer không phải so chuỗi với một hằng của code. Kèm theo: suy ra `evidence_level` bậc
`abstract` từ `work_version.abstract_text` khi có, thay vì luôn `post_only` — làm được nhưng
chưa làm, ghi `NOT_RUN`.

## 9. `PKT-TC-SAVED-FIX2` — manifest không được pin factory dùng chung

**Vấn đề.** Manifest e2 pin `server/app/main.py` như một artifact **ĐƯỢC SẢN XUẤT**. Đợt wiring
đã viết lại factory đó, nên pin ấy nay sai byte. Đó không chỉ là số cũ: một pin PRODUCED đã cũ
là **một chứng chỉ sai** — nó khẳng định gói này sinh ra những byte mà gói này không sinh ra.
`W6n` từ chối đăng ký card với một pin như vậy, và đúng ra phải từ chối.

Bản thân bảng file ở §3 đã ghi chú điều này từ e2 ("`main.py` đã đổi byte SAU e1 … hash ở bảng
trên là hash đúng tại thời điểm e1"), nhưng ghi chú trong handoff không sửa được một trường
`artifacts` trong manifest — công cụ đọc trường, không đọc văn xuôi.

**Sửa, theo ruling thường trực từ vòng P4** (tiền lệ: W5A,
`evidence/runs/TC-telegram-linking-auth-E1-20260908T015949Z.json`): manifest của card **không**
pin factory dùng chung. `server/app/main.py` đã được **gỡ khỏi `artifacts`**; thay vào đó
`implementation_revision` pin nội dung **khối có phân định của chính card** — thứ duy nhất card
này thực sự viết trong file đó:

| Thứ được pin | Giá trị |
| --- | --- |
| Khối `# >>> TC-saved-snapshot` … `# <<< TC-saved-snapshot <<<` | sha256 `8639af0538741a2f9716c270fe7be73781d6eadd0f6db1eeac4828b4b6638d9c`, 957 byte |
| `server/app/main.py` (cả file) | **không pin** — nhiều card nối thêm vào nó và nó sẽ còn đổi byte |

Bảy artifact còn lại được pin lại theo byte hiện tại. e1 và e2 → **STALE**, có ghi lý do ngay
trong bản ghi mới.

**Kiểm.** 49 test của card chạy lại: **20 + 17 + 12 = 49 passed, 0 failed** — không có gì khác
dịch chuyển. Gói này **không đổi một dòng mã sản phẩm nào** (lease chỉ gồm handoff + manifest),
nên không chạy lại toàn bộ suite; số gần nhất còn hiệu lực là 1145 passed, 4 xfailed, exit 0.


Mọi mục ở trên là `SELF_VALIDATION`. **Không** mục nào là independent audit.

---

*`PKT-TC-SAVED` (e1) + `PKT-TC-SAVED-FIX1` (e2) + `PKT-TC-SAVED-FIX2` (e3) · `worker-W5B` ·
`lease_released_at` 2026-09-09T09:15Z · ceiling `IMPLEMENTATION_VERIFIED` cho phạm vi card.*
