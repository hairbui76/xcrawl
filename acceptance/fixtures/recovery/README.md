---
contract_id: CT-fixture-recovery-index
version: 0.1.0
status: draft
owner_role: operations contract owner
source_refs: [SRC-PLAN §11 PC08, SRC-PLAN §13, SRC-PLAN §14.2, SRC-SPEC §11, SRC-SPEC §7.3, SRC-SPEC §9.3]
requirement_refs: [REQ-D58, REQ-S7.3-04, REQ-S7.3-06, REQ-S9.3-08, REQ-S11.2-05, REQ-S11.4-03, REQ-AC12, REQ-AC17, REQ-AC18, REQ-D05]
decision_refs: [B11, B13, AMD-B11, ADR-0005, ADR-0010]
invariant_refs: [I01, I02, I08, I09, I10, I11, I13, I15]
producers: [MOD-backup-service]
consumers: [MOD-backup-cli, MOD-delivery-service, MOD-job-service, MOD-x-collector, MOD-analysis-worker]
dependencies:
  - contracts/ops/backup-restore.md
  - contracts/ops/secrets.md
  - contracts/ops/internet-boundary.md
  - contracts/ports.yaml
  - contracts/modules.yaml
  - contracts/errors.yaml
  - contracts/state/storage.yaml
scope: >
  Chỉ mục fixture cho PC08: mười kịch bản về khôi phục, biên giới Internet và xác thực, mỗi cái có given, chuỗi
  event, kết quả mong đợi, danh sách hiệu ứng bị cấm và oracle kiểm được. Đây là **dữ liệu vào và oracle**, không
  phải kết quả chạy.
verification: >
  E0: mọi fixture parse JSON; mọi `operation`, mã lỗi, module và tên state được trích tồn tại ở upstream; mọi
  event có `edge_assertion` nhất quán với `contracts/modules.yaml.allowed_edges` (script EV-PC08-01).
  Không fixture nào đã được thực thi: **NOT_RUN**.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture khôi phục và biên giới (PC08)

## Danh mục

| File | Nội dung | Scenario | Invariant |
| --- | --- | --- | --- |
| `a-restore-old-outbox-nothing-sent.json` | Restore với outbox cũ `pending`/`unknown` → không gửi gì; `restore_generation` cũ chặn dispatcher | SC27 | I15, I09 |
| `b-post-restore-stale-lease-rejected.json` | Worker từ trước backup dùng lease cũ → `STALE_LEASE`; claim bị chặn bởi `RESTORE_UNVERIFIED` | SC27, SC20 | I15, I10, I02 |
| `c-disk-full-mid-ingest.json` | Hết ổ giữa ingest → không ACK, cursor không đổi, readiness đỏ, liveness `up` | SC26 | I02, I13 |
| `d-wal-unsafe-copy-detected.json` | Copy WAL-unsafe: sha256 khớp và `integrity_check ok` nhưng counts lệch → snapshot `invalid` | SC43 | I15 |
| `e-saved-snapshot-hash-preserved.json` | Hash `saved_snapshot` trước backup == sau restore; bài gốc bị xóa trên X vẫn đọc được | SC12 | I08, I15 |
| `f-secret-canary-injection.json` | Prompt injection đòi lộ secret và fetch metadata endpoint → canary không xuất hiện ở đâu | SC17 | I11 |
| `g-ssrf-redirect-private.json` | Link paper redirect về `127.0.0.1` → chặn ở bước redirect, `SOURCE_METADATA_UNAVAILABLE` | SC39 | I11 |
| `h-unauthenticated-owner-api.json` | Request không xác thực và request thiếu CSRF → `UNAUTHORIZED`, 0 mutation | SC40 | I01 |
| `i-collector-token-calls-save.json` | Collector token gọi Save và sửa tag → `UNAUTHORIZED`; đường ingest hợp lệ vẫn chạy | SC41 | I01, I08 |
| `j-restore-verification-incomplete-dispatch-locked.json` | Đối soát chưa xong → dispatch vẫn khóa, nêu rõ mệnh đề nào chưa đạt | SC42, SC27 | I15, I13 |
| `k-delete-target-preserves-saved.json` | `data.delete_target`: xóa dữ liệu gốc một target, **giữ** `saved_snapshot` + `first_announced_ledger` + report đã publish; ca âm thiếu cờ xác nhận | SC32 | I08, I01, I05, I07 |
| `l-purge-all-two-phase-and-negatives.json` | `data.purge_all`: hai pha xác nhận, chỉ trong `maintenance`, thu hồi lease trước khi xóa; bốn ca âm (cụm từ sai, sai trạng thái storage, sai principal, dùng lại challenge); **khẳng định cả 22 bảng retained còn nguyên và 37 bảng dữ liệu nghiên cứu về 0** | SC44 | I01, I15, I13 |
| `m-post-restore-reconciled-dispatch-reopens.json` | Đối soát **hoàn tất** → dispatcher mở lại, nhưng outbox generation cũ vẫn **không** tự phát lại — mặt dương của I15 | SC53, SC27 | I15, I09, I13 |

## Hình dạng chung

```jsonc
{
  "x-contract": { /* header bắt buộc theo baseline §3 */ },
  "fixture_id": "a",
  "title_vi": "...",
  "scenario_refs": ["SC27"],
  "invariant_refs": ["I15"],
  "evidence_status": "NOT_RUN",
  "given":  { /* trạng thái ban đầu */ },
  "events": [ { "seq": 1, "actor": "MOD-...", "operation": "<domain>.<verb>", "edge_assertion": "allowed|forbidden", ... } ],
  "expected": { /* trạng thái và mã lỗi mong đợi */ },
  "forbidden_effects": [ "..." ],
  "oracle_vi": "phép đo độc lập quyết định đúng/sai"
}
```

## Quy ước chú thích trong khối `rows` của `given` và `expected` (R4-01, ràng buộc mọi thư mục fixture)

Nêu nguyên văn quy tắc đã ruling:

> Dưới khối `rows` của `given` và của `expected` — tức `rows[<entity>][]` — **mọi khóa** phải là một trong ba loại: (a) một cột
> **tồn tại** trong `contracts/data/entities.yaml` cho đúng entity đó; (b) một chú thích có khóa **bắt đầu bằng
> `_`** (`_note`, `_target`, `_note_vi`, `_save_channel_note`, `_created_in_transaction`, `_payload_contains`, …);
> hoặc (c) một cột mang **`pending_cr: CR-…`** ngay trong file. Không có allowlist riêng cho từng gói.

Lý do quy tắc tồn tại: một khóa trần trông y hệt một cột thật, nên một fixture nhắc tới cột không tồn tại vẫn đọc
như một oracle chạy được. Tiền tố `_` làm cho ý định "đây là chú thích, đừng tra schema" **kiểm được bằng máy**,
và `pending_cr` làm cho "cột này chưa có, đã báo rồi" hiện ngay trong file thay vì chỉ nằm trong handoff.

**Trạng thái của thư mục này:** các fixture recovery mô tả trạng thái bằng `given`/`expected` dạng tự do
(`storage_health`, `outbox_in_snapshot`, `seq1`, …) và **không** dùng cấu trúc `rows.<entity>[]`, nên không có
khóa nào thuộc phạm vi quy tắc trên: **0 cột được kiểm, 0 chưa giải quyết**. Nếu về sau một fixture recovery
chuyển sang dạng `rows`, quy tắc áp dụng ngay lập tức, không cần sửa README.

## Quy ước `actor` và `edge_assertion`

Theo ruling R-02 (`F-A1R1-02`), `events[].actor` là **một khẳng định về cạnh giao tiếp**, không phải "dịch vụ nào
đang thực thi transaction". Do đó:

- `actor` phải là một **caller được phép** của `operation` theo `contracts/ports.yaml.caller_modules`, và bộ ba
  `(actor, owner_module, operation)` phải có trong `contracts/modules.yaml.allowed_edges` — **khi**
  `edge_assertion` là `allowed`.
- `edge_assertion: "forbidden"` — **đã được ratify** ở R4-02 làm dấu chuẩn cho một event cố tình thử cạnh bị cấm.
  Gate `fixture-actor-edge` kiểm hai điều: bộ ba `(actor, owner_module, operation)` **không** có trong
  `allowed_edges`, **và** `expected` chứa một trong ba mã lỗi hợp lệ cho ca âm:
  **`UNAUTHORIZED`** (danh tính chưa xác lập hoặc sai lớp principal) · **`FORBIDDEN_EDGE`** (cạnh không có trong
  registry) · **`CAPABILITY_DENIED`** (capability tiến trình/mạng/tool bị chặn ở mức nền tảng).
  Nếu bộ ba lại **có** trong `allowed_edges` thì hoặc fixture sai hoặc registry sai — cả hai đều phải báo, không
  được lặng lẽ đổi marker cho qua gate.
- Khóa của event là **`operation`** (không phải `operation_id`) ở mọi fixture (R4-02).
- Mặc định khi thiếu trường: `allowed`.
- Khi cần diễn đạt "module nào đang thực hiện transaction" mà đó **không** phải khẳng định về caller, dùng khóa
  riêng `performed_by`. Trường này **không** được kiểm theo `allowed_edges`. Hiện chưa fixture nào cần tới nó.

Ví dụ đúng đã áp dụng: trong `g-ssrf-redirect-private.json`, `research.fetch_work_metadata` có
`actor: MOD-ingest-service` — vì `MOD-research-connector` **sở hữu** operation đó chứ không gọi nó.

Thư mục này dùng `edge_assertion: forbidden` ở **hai** event, cả hai trong
`i-collector-token-calls-save.json`:

| Event | Cạnh bị thử | Mã lỗi mong đợi |
| --- | --- | --- |
| seq 1 | `MOD-x-collector` → `save.create` (owner `MOD-saved-service`) | `UNAUTHORIZED` — ca âm `NC-01` |
| seq 2 | `MOD-x-collector` → `tag.update` (owner `MOD-tag-service`) | `UNAUTHORIZED` — ca âm `NC-02` |

Cả hai chọn `UNAUTHORIZED` chứ không phải `FORBIDDEN_EDGE`: `contracts/modules.yaml` (`NC-01`/`NC-02`),
oracle của `UNAUTHORIZED` trong `contracts/errors.yaml` và mô tả `collectorToken` trong
`contracts/http/openapi.yaml` đều đã đóng băng ở mã đó. Khối `packet_deviation` trong chính fixture ghi lại rằng
văn bản packet PC08 từng nói `FORBIDDEN_EDGE`, kèm kỳ vọng thay thế nếu Coordinator đổi ý (`CR-PC08-04`).

## Scenario mới do PC08 giới thiệu

`SC01`–`SC28` từ SRC-PLAN §13; `SC29`–`SC32` do PC00 đăng ký; `SC33`–`SC36` PC03; `SC37`–`SC38` PC04.
PC08 lấy tiếp:

| ID | Chủ đề |
| --- | --- |
| `SC39` | SSRF: URL nguồn redirect về địa chỉ nội bộ, bị chặn ở từng bước |
| `SC40` | Request không xác thực (và request thiếu CSRF) tới owner API |
| `SC41` | Token hợp lệ đi sai cạnh: collector gọi Save / sửa tag → `UNAUTHORIZED` (mã đã thống nhất với NC-01/NC-02, errors.yaml và openapi.yaml) |
| `SC42` | Đối soát sau restore chưa hoàn tất → dispatch vẫn khóa |
| `SC43` | Backup WAL-unsafe bị phát hiện bằng đối chiếu counts |

Các ID này **chưa có anchor** trong `precode/baseline.json` — xem `CR-PC08-01`.

## Ba fixture dạng `rows.<entity>[]` (R5-02)

`k`, `l`, `m` dùng cấu trúc **`rows[<entity>][]` trong `given` và `expected`** thay vì mô tả tự do, để field
gate **không rỗng**: mọi khóa trong các hàng đó là cột thật của `contracts/data/entities.yaml`, hoặc chú thích có
tiền tố `_`. Nhờ vậy ba fixture này đóng góp cột thật vào phép kiểm, khác bảy fixture cũ (`a`–`j`) vốn khẳng định
về trạng thái hệ thống và mã lỗi chứ không về hàng.

**Phạm vi purge đã chốt** (OD-20260907-01 mục 24), với ba tập bảng theo ruling **CR-PC05-06 + CR-PC05-07**
(`PURGE-LIST-ruling.md`) — bản `TXN-purge-all` đầu tiên tự mâu thuẫn và **không** được dùng. Ba tập phủ đúng
61 entity, không chồng lấn, và `l` khẳng định cả ba:

- **22 bảng retained** — `owner`, `session`, `secret_ref`, `task_credential`, `secret_audit`, `telegram_link`,
  `telegram_link_code`, `provider_config`, `provider_test_result`, `settings`, `schedule_occurrence`, `tag`,
  `tag_alias`, `tag_exclusion`, `tag_config_version`, `source_connection`, `backup_snapshot`, `backup_manifest`,
  `restore_record`, `purge_challenge`, `worker_registration` — mỗi bảng có một hàng trong khối `rows` của `given`
  và hàng tương ứng trong khối `rows` của `expected`, nên field gate kiểm được từng cột.
- **2 bảng never_purged** — `schema_migration`, `data_deletion_audit`; bảng thứ hai còn **tăng đúng một hàng**
  vì chính lần purge ghi audit của nó.
- **37 bảng bị xóa** — dữ liệu nghiên cứu và vận hành, gồm `telegram_link_attempt` (CR-PC05-07); khẳng định
  `COUNT(*) = 0` sau ca hợp lệ, qua khóa `purged_table_counts_after` trong `expected`.

`l` cũng khẳng định **backup không bị chạm** và hộp thoại xác nhận **phải nói** rằng dữ liệu đã xóa vẫn còn trong
các bản backup: nếu không nói, người dùng tin sai rằng dữ liệu đã biến mất hoàn toàn.

## Trạng thái bằng chứng

Mọi fixture ở đây là `NOT_RUN`. Chưa có code, chưa có harness mạng, chưa có drill restore nào được thực hiện.
Một fixture parse được **không** chứng minh guard nào chạy (SRC-PLAN §14.2, E0).
