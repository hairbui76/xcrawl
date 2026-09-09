# HANDOFF — PKT-PC02 (identity, entity và transaction)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02` |
| worker principal | `worker-W3` |
| authority_id | `AUTH-COORD-PC02` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC02-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` — không có OS enforcement; lease được theo dõi bằng thông điệp |
| status | **DONE_WITH_CONCERNS** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| next actor | Coordinator |
| lease_released_at | 2026-09-06T17:25Z |

Trạng thái `DONE_WITH_CONCERNS` chứ không phải `DONE` vì: (a) mọi deliverable đã tạo và E0
đã chạy PASS, nhưng (b) gói này phát sinh 8 change request tới các gói chạy song song
(PC01/PC04/PC06/PC07/PC08/PC09) và 5 giá trị PROVISIONAL cần Owner/gói khác chốt (mục 6).

## 2. Changes

| Path | Op | Before | After sha256 | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | CREATE | ABSENT | `24a83d8ab4e8238b9cd9f68f9da91d3fe804e3a9a2db489a20dfe35708137d3b` | 120129 |
| `contracts/data/identity.md` | CREATE | ABSENT | `d128589438226d109cb3e44d49b16f2d5f9d893f138e1138f22226005c94918f` | 20438 |
| `contracts/data/invariants.md` | CREATE | ABSENT | `417dfcdd8b30cb1e514d1c4d2a14fda1a571e73e93c47255269895f63a14b300` | 25377 |
| `contracts/schemas/target.schema.json` | CREATE | ABSENT | `035ada0d94a4fe473de271a1ed9c1349e6942e3a53971419d0e7a845e2292dd0` | 7192 |
| `contracts/schemas/ingest-batch.schema.json` | CREATE | ABSENT | `a974ce8c555d63a3a1a02412660bc0411d5f2f300e997ace09856d8a8e925716` | 12260 |
| `acceptance/fixtures/identity/README.md` | CREATE | ABSENT | `1e43fa06f75bd2ac3077a502c074b049f3ecf5504b380b4cb18e635914443165` | 7776 |
| `acceptance/fixtures/identity/a-merge-doi-arxiv.json` | CREATE | ABSENT | `a5e7e06957a21e9b7425d514b94730e1a2d7dc13f9d9164b323dbe8c0c606f69` | 17423 |
| `acceptance/fixtures/identity/b-post-only-missing-ids.json` | CREATE | ABSENT | `1a3b21d3621a6ad3faf6f3121ce2d7266edd1cf0d465a7890e42a568341da9bd` | 4308 |
| `acceptance/fixtures/identity/c-identity-conflict.json` | CREATE | ABSENT | `b0d58468b842bfb473c09b6efebf87bdc507aa567b057884e6d9692cfe35a117` | 7368 |
| `acceptance/fixtures/identity/d-concurrent-save-app-telegram.json` | CREATE | ABSENT | `3e4cc52cfd21222f5b9c0afa1abc35802e41ef14f873a92a775d64c5f4693193` | 7601 |
| `acceptance/fixtures/identity/e-source-deleted-snapshot-intact.json` | CREATE | ABSENT | `c9bccb3117e2376495915e55b6b6be030b9934155fd331f58b426e6335447753` | 6837 |
| `acceptance/fixtures/identity/f-ingest-replay-idempotent.json` | CREATE | ABSENT | `790a2c286bbf6c089328c69d99c3b6ee589ced5a725b1d6f37205de27a628bf7` | 12333 |
| `acceptance/fixtures/identity/g-arxiv-version-v1-v2.json` | CREATE | ABSENT | `2d564f67fb10bc788453b2720d20d74e4aeee07aa2d40d6d336c8853e2e9515e` | 9289 |
| `acceptance/fixtures/identity/h-five-posts-thread-one-target.json` | CREATE | ABSENT | `b891ba75f6c0d58455a65e309d3dd2f133483ae338b72293841adfd66665c966` | 9295 |
| `acceptance/fixtures/identity/pos-ingest-batch-valid.json` | CREATE | ABSENT | `c4ad116eaa0434fbdb0cc573b31639e1a66fc963d6a26669e375ae1dae7a3644` | 2237 |
| `acceptance/fixtures/identity/neg-ingest-batch-missing-idempotency-key.json` | CREATE | ABSENT | `95967e6004574b840029a611323eb9c4d6a5ebaf8df472fb799da68e01b6a405` | 2358 |
| `acceptance/fixtures/identity/neg-ingest-batch-bad-payload-hash.json` | CREATE | ABSENT | `5a6f14986261f606e84b85cdbb0d7eb1c7e4d872a37c0a03117dce5a32f10261` | 2311 |
| `acceptance/fixtures/identity/neg-ingest-batch-empty-items.json` | CREATE | ABSENT | `f95cd4a2f67f2389abfedb27585b5afe41cd49700d82f0d0b7ac06646148e11f` | 1778 |
| `acceptance/fixtures/identity/neg-ingest-batch-unknown-field.json` | CREATE | ABSENT | `10ff2e91f754538f82faf395ca6339a2db81e6397d4d03169bb9ebfd3364d97a` | 2518 |
| `acceptance/fixtures/identity/neg-ingest-batch-timestamp-precision.json` | CREATE | ABSENT | `5675c24e751ebf70c11f90a7acd2608716e00d7fd3f2dfa7c64b44c87e93567f` | 2408 |
| `evidence/handoffs/PC02-handoff.md` | CREATE | ABSENT | (file này) | — |

Directory được tạo: `contracts/data/`, `contracts/schemas/`, `acceptance/fixtures/identity/`,
`evidence/handoffs/`. Không có file nào ngoài write targets của packet. Không chạy lệnh git
nào. Không có network. Helper script chạy từ scratch dir với `PYTHONDONTWRITEBYTECODE=1`;
không có `__pycache__` trong repo.

Vượt write target đã khai trong packet: 3 file fixture negative/positive bổ sung
(`pos-ingest-batch-valid.json`, `neg-ingest-batch-unknown-field.json`,
`neg-ingest-batch-timestamp-precision.json`). Cả ba nằm trong directory-scoped grant
`acceptance/fixtures/identity/` và được packet yêu cầu tường minh ở EV-02 ("include the
negatives as fixtures too"); packet chỉ đòi ≥ 3 negative, gói này tạo 5.

## 3. Source baselines

| Ref | Path | SHA-256 (kiểm trước khi bắt đầu VÀ trước handoff) | Bytes |
| --- | --- | --- | --- |
| SRC-PLAN | `/mnt/virtual/repo/xcrawl/research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |
| SRC-SPEC | `/mnt/virtual/repo/xcrawl/research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |

Cả hai khớp baseline §2 ở cả hai lần kiểm. Không STALE_BASELINE.

Read-only dependency đã đọc: `agent_profile/worker.md`, `agent_profile/protocol.md`,
`scratchpad/packets/00-coordination-baseline.md`, `scratchpad/packets/PC02-packet.md`.
Dependency **không tồn tại** tại thời điểm soạn: `contracts/modules.yaml`,
`contracts/ports.yaml` (PC01 chạy song song) — xử lý theo mục 6 (CR-PC02-01, CR-PC02-02),
không phải BLOCKED_DEPENDENCY vì packet §Non-goals cho phép tham chiếu theo baseline §3.

## 4. Evidence records

### EV-PC02-01 — parse và metaschema

- type: `SELF_VALIDATION`
- command: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 verify_pc02.py` (phần `=== EV-PC02-01 ===`)
- runtime: Python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3, Linux
- started/ended UTC: 2026-09-06T17:22:19Z / 2026-09-06T17:22:20Z
- input hashes: xem mục 2 (toàn bộ file đã tạo)
- oracle: `yaml.safe_load` không ném lỗi; front-matter của hai file .md parse được và
  `claim_ceiling == DRAFT_FOR_REVIEW`; `jsonschema.Draft202012Validator.check_schema` không
  ném lỗi cho cả hai schema; `json.load` thành công cho 14 fixture
- expected/observed: expected PASS / observed PASS — 37 entity, 4 transaction, 2 schema hợp lệ, 14 fixture parse
- exit code: 0 · status: **PASS**
- limitations: E0 tĩnh. Không chứng minh code hoạt động, không chứng minh SQLite thực thi được
  các ràng buộc mô tả (partial index, generated column) — cần E1/E2 sau khi chọn stack.

### EV-PC02-02 — target objects + wire schema (positive/negative)

- type: `SELF_VALIDATION`
- command: cùng script, phần `=== EV-PC02-02 ===`
- oracle:
  1. Mọi object trong `given`/`expected` của mọi fixture có `kind ∈ {work, post}` phải validate
     theo `contracts/schemas/target.schema.json`.
  2. Fixture có `expected_validation = "accept"` phải validate theo
     `contracts/schemas/ingest-batch.schema.json`; fixture `"reject"` phải bị từ chối.
  3. `payload_hash` của mọi batch positive phải tái lập được bằng
     `sha256(JCS({schema_version, items, client_checkpoint_proposal}))`.
- expected/observed: **37 target object hợp lệ / 0 lỗi**; **3 positive ACCEPT**, **5 negative
  REJECT** với lý do đúng (`required property`, `pattern sha256`, `too short`,
  `additionalProperties`, `pattern timestamp`); **3/3 payload_hash tái lập đúng**
- exit code: 0 · status: **PASS**
- limitations: schema validation không chứng minh ngữ nghĩa transaction; `max_payload_bytes`
  và giới hạn byte UTF-8 không biểu diễn được bằng JSON Schema và phải ép ở tầng transport (PC05).

### EV-PC02-03 — tính toàn vẹn tham chiếu entity

- type: `SELF_VALIDATION`
- command: cùng script, phần `=== EV-PC02-03 ===`
- oracle: mọi tên bảng xuất hiện trong `transactions` (`rows_written_together`,
  `merge_move_set.moves`, `tables_with_zero_delta`), trong `unique_constraint_semantics`,
  trong `invariants.md` (ký hiệu `#<tên bảng>[…]`) và trong `given`/`expected.rows` của fixture
  phải tồn tại trong `entities.yaml`; `owner_id` phải có trên mọi entity trừ hai ngoại lệ đã khai
- expected/observed: **20 tên bảng tham chiếu đều tồn tại**; **16 bảng dùng trong fixture đều
  tồn tại**; entity không có `owner_id` = `['owner', 'schema_migration']`, khớp đúng khai báo
- exit code: 0 · status: **PASS**
- limitations: kiểm tra dựa trên regex trên văn bản hợp đồng; nó bắt được tham chiếu treo,
  không bắt được tham chiếu **thiếu** (một quan hệ đáng lẽ phải khai mà không ai viết ra).

Tổng: `RESULT: PASS (0 fail)`, 30 dòng PASS, exit 0.

**Chưa chạy (NOT_RUN):** mọi bằng chứng E1 (contract test bằng fixture), E2 (fault injection
theo `failure_timeline`), E3 (live), E4 (review nội dung). Không có independent audit ở gói
này — mọi kết quả trên là `SELF_VALIDATION` của chính Worker đã viết file.

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | post / work / post-only / alias / paper version / analysis generation / Saved target / snapshot | **DONE** | `entities.yaml` §5 (37 entity: `post`, `work`, `identity_alias`, `identity_conflict`, `identity_merge_audit`, `work_version`, `analysis_generation`, `analysis`, `analysis_attempt`, `saved_item`, `saved_snapshot`, …); post-only ở `identity.md` §4 và `target.schema.json` nhánh `post_target` |
| 2 | Một owner ở schema, giữ `owner_id`, không tenant feature | **DONE** | `entities.yaml` `conventions.owner_scoping` + entity `owner` (singleton guard); EV-PC02-03 kiểm tự động; non-goals ghi tường minh |
| 3 | Transaction map: ingest+receipt+checkpoint, identity merge, Save, analysis accept | **DONE** | `entities.yaml` `transactions` — 4 transaction, mỗi cái có `rows_written_together`, `commit_point`, `external_observer` (before/after/never_observable), `failure_timeline`, `forbidden_effects` |
| 4 | Fixture (a)–(h) | **DONE** | `acceptance/fixtures/identity/` — 8 fixture kịch bản + 6 fixture wire; chỉ mục ở README |
| 5 | Migration/versioning, referential integrity, snapshot lịch sử không đổi sau merge | **DONE** | `entities.yaml` `schema_versioning` (additive-only + danh sách cấm), `referential_integrity` (`merge_pointer_rewrite`, `historical_snapshot_rule` kèm oracle), invariant **I17** |
| — | I02/I03/I04/I08 có oracle + counterexample | **DONE** | `invariants.md` — mỗi mục có phát biểu, owner, positive, ≥3 counterexample, bảng oracle, loại bằng chứng |
| — | Hai cột UNIQUE không đủ (B06) nêu tường minh | **DONE** | `entities.yaml` `unique_constraint_semantics.b06_explicit_statement` + `invariants.md` Phụ lục A |
| — | Không merge đoán (B15) | **DONE** | `identity.md` §5, §6.1, §9; `identity_merge_audit.linking_evidence` NOT NULL; enum `performed_by` không có giá trị AI |
| — | Invariant mới I16, I17 có justification | **DONE** | `invariants.md` §I16, §I17 |

## 6. Unresolved refs

### 6.1 Change requests (gói khác sở hữu file)

| CR | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC02-01` | PC01 | Xác nhận cách viết module ID đã dùng: `MOD-backend-api`, `MOD-web-ui`, `MOD-x-collector`, `MOD-analysis-worker`, `MOD-report-builder`, `MOD-telegram-adapter`, `MOD-embedding-service`, `MOD-research-connector`, `MOD-backup-operator`. Nếu PC01 đặt tên khác, PC09 phải reconcile `owner_module`/`producers`/`consumers` trong cả 3 file `contracts/data/*`. |
| `CR-PC02-02` | PC01 | Xác nhận operation ID đã tham chiếu: `ingest.submit_batch`, `identity.merge_works`, `identity.resolve_conflict`, `saved.create`, `analysis.submit_result`, `analysis.request_generation`, `post.mark_source_deleted`, `source.fetch_metadata`, `report.publish`. Đăng ký vào `contracts/ports.yaml`. |
| `CR-PC02-03` | PC07 | `saved_snapshot.payload` cần schema riêng (`contracts/schemas/saved-snapshot.schema.json`). PC02 chỉ khóa tính bất biến, `content_hash` và quy tắc canonical JSON. |
| `CR-PC02-04` | Owner / PC05 | Xác nhận các giới hạn PROVISIONAL của ingest batch (mục 6.2). |
| `CR-PC02-05` | PC03 | Ngưỡng `identity_merge_max_moved_rows = 100000` (PROVISIONAL) và hành vi khi vượt (chuyển thành `identity_conflict`) cần khớp với budget/timeout của PC03. |
| `CR-PC02-06` | PC04 | **Quan trọng.** Chốt policy `first_announced` sau identity merge (work thắng có kế thừa first-announcement của work thua không). PC02 để `moved_counts.first_announced = null` và cung cấp điểm móc trong cùng transaction merge. Ảnh hưởng trực tiếp I07, REQ-D29, REQ-AC09. |
| `CR-PC02-07` | PC08 | Phần dữ liệu của I15: `outbox_intent.restore_generation`, revoke lease trước khi mở dispatcher, và oracle so manifest cho `saved_snapshot`. |
| `CR-PC02-08` | PC09 | Đăng ký 3 scenario ID mới: **SC29** (target chỉ-có-post), **SC30** (phiên bản arXiv mới), **SC31** (wire schema ingest batch từ chối payload sai). |

### 6.2 Quyết định PROVISIONAL do PC02 đưa ra (không có trong baseline §5)

| Mục | Giá trị | Căn cứ | Ai chốt |
| --- | --- | --- | --- |
| `ingest_item_max_text_bytes` | 65536 byte UTF-8 | Đủ cho post dài của X, dưới ngưỡng phình transaction. Vượt ngưỡng → `items_rejected`, không cắt cụt | Owner sau M0 (CR-PC02-04) |
| `ingest_batch_max_payload_bytes` | 8 MiB | Batch nằm gọn trong một transaction ngắn | Owner/PC05 |
| `ingest_item_max_media_refs` / `max_referenced_links` / `thread_context_max_posts` | 8 / 32 / 50 | Giới hạn quan sát được của X + REQ-D31 | Owner sau M0 |
| `identity_merge_max_moved_rows` | 100000 hàng | Merge quá lớn nhiều khả năng là lỗi quy tắc chuẩn hóa, không phải trùng thật | PC03/Owner |
| `saved_snapshot_max_payload_bytes` | 1 MiB | Snapshot là văn bản; vượt ngưỡng nghĩa là đang chụp nhị phân | PC07 |
| Chuẩn hóa DOI: bỏ dấu câu ở cuối | Quy tắc §2.1 bước 4 | Post thường dán DOI kèm dấu chấm cuối câu. **Rủi ro đã ghi:** một số DOI kết thúc hợp lệ bằng dấu chấm; trường hợp đó thành `cross_scheme_disagreement`, không merge im lặng | PC09 review |
| Chuẩn hóa arXiv kiểu cũ: archive chữ thường + subject-class chữ HOA | §2.2 bước 7 | Cần một dạng tất định để `identity_alias` là hàm | PC09 review |
| `analysis` key **không** gồm provider/model | `entities.yaml` `analysis.analysis_key.excluded_deliberately` | SRC-PLAN §9.3 đề xuất giữ kết quả cũ tới khi owner yêu cầu reanalysis | **PC06 sở hữu quyết định cuối** |

### 6.3 Không có `OWNER_DECISION_REQUIRED` mới

Mọi điểm cần quyết định đều có khuyến nghị trong SRC-PLAN hoặc baseline §5, nên được ghi
`PROVISIONAL` theo baseline §6 dòng "A product decision outside §5". Không có phạm vi nào bị
chặn cứng. Ngoại lệ gần nhất là `first_announced` sau merge (CR-PC02-06): PC02 **không** đoán,
để `null` và ghi rõ mục đó chưa khóa — nhưng đây là quyết định của PC04, không phải của Owner.

### 6.4 Rủi ro và giới hạn đã biết

1. **Chưa kiểm chứng trên SQLite thật.** Hợp đồng dựa vào partial UNIQUE index và STORED
   generated column (`target_key`). Cả hai có yêu cầu phiên bản SQLite; `entities.yaml`
   `target_union.representation.union_key.storage` đã ghi phương án dự phòng (domain layer ghi
   cột thường trong cùng transaction) nhưng chưa ai chạy thử. Cần E1 sau khi chốt stack.
2. **`PRAGMA foreign_keys = ON` là giả định.** Nếu runtime tắt FK, mọi oracle tham chiếu ở
   `invariants.md` mất hiệu lực. Đã ghi trong `schema_versioning.sqlite_notes`.
3. **Kiểm tra EV-PC02-03 bắt được tham chiếu treo, không bắt được tham chiếu thiếu.**
4. **Fixture chưa được chạy như test.** Chúng là dữ liệu + oracle; mọi kết luận về hành vi là
   `NOT_RUN`.
5. **Không có independent audit.** `audit_route: INDEPENDENT_REQUIRED` của packet chưa được
   thực hiện; Worker không được tự audit candidate của mình.

## 7. Kết thúc

Sau khi ghi file này, Worker `worker-W3` không ghi thêm bất kỳ file nào. Lease
`LEASE-PC02-e1` được nhả. Mọi sửa đổi tiếp theo cần packet mới, baseline mới và lease mới với
fencing cao hơn.

---

# ADDENDUM — PKT-PC02-FIX1 (căn chỉnh theo PC01)

## A1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX1` |
| worker principal | `worker-W3` |
| authority_id | `AUTH-COORD-PC02-FIX1` |
| lease_id | `LEASE-PC02-e2` (exclusive, fencing 2) |
| expires_at | 2026-09-07T02:00Z |
| status | **DONE_WITH_CONCERNS** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| next actor | Coordinator |
| lease_released_at | 2026-09-06T17:34Z |

Phạm vi: MODIFY toàn file trên các file do PKT-PC02 tạo, cộng addendum này. **Không** chạm
`contracts/modules.yaml`, `contracts/ports.yaml`, `contracts/capabilities.yaml`,
`contracts/ops/`, `precode/` — hash của hai file PC01 được kiểm lại ở A5.

## A2. Delta

### A2.1 Module ID (ruling CR-PC02-01)

- `MOD-report-builder` → `MOD-report-service` (toàn bộ file).
- `MOD-backup-operator` → **`MOD-backup-service`**. Căn cứ: trong `modules.yaml`,
  `MOD-backup-service.data_owner_of = [backup_snapshot, backup_manifest, restore_record]`
  còn `MOD-backup-cli.data_owner_of = []`. Vì các file PC02 chỉ nói về **hành động trên dữ
  liệu** backup/restore (I15, `outbox_intent.restore_generation`), owner đúng là
  `MOD-backup-service`; `MOD-backup-cli` là bề mặt người vận hành gọi vào và không sở hữu
  bảng nào, nên không xuất hiện trong hợp đồng dữ liệu.
- Đã kiểm 19 MOD id còn dùng đều tồn tại trong `modules.yaml` (EV-PC02-04).

### A2.2 Quyền sở hữu dữ liệu theo `data_owner_of` của PC01

`owner_module` được căn lại cho **34/37 entity** (trước đây phần lớn ghi `MOD-backend-api`):

| owner_module mới | Entity |
| --- | --- |
| `MOD-auth-service` | `owner` |
| `MOD-settings-service` | `settings`, `source_connection` (xem A4) |
| `MOD-tag-service` | `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version` |
| `MOD-job-service` | `run`, `assignment_lease` |
| `MOD-ingest-service` | `post`, `post_work`, `ingest_receipt`, `checkpoint` |
| `MOD-identity-service` | `work`, `identity_alias`, `identity_conflict`, `identity_merge_audit`, `work_version` |
| `MOD-analysis-service` | `analysis`, `analysis_generation`, `analysis_attempt`, `work_label` |
| `MOD-embedding-service` | `embedding_generation`, `tag_vector` |
| `MOD-report-service` | `report`, `report_item`, `emerging_direction`, `coverage_window`, `pending_item_ledger`, `backfill_ledger` |
| `MOD-saved-service` | `saved_item`, `saved_snapshot` |
| `MOD-delivery-service` | `delivery`, `delivery_part`, `outbox_intent` |
| `MOD-telegram-adapter` | `telegram_link` |
| `MOD-data-store` | `schema_migration` |

`performed_by` của 4 transaction cũng chuyển từ `MOD-backend-api` sang service sở hữu tương
ứng (`MOD-ingest-service`, `MOD-identity-service`, `MOD-saved-service`,
`MOD-analysis-service`). `producers`/`consumers` ở header của cả 5 file hợp đồng được viết lại
theo cùng nguyên tắc. `MOD-backend-api` vẫn còn trong `consumers` vì `modules.yaml` mô tả nó
là bề mặt API/transit, không phải data owner.

### A2.3 Operation ID (ruling CR-PC02-02)

| Cũ | Mới | Ghi chú |
| --- | --- | --- |
| `saved.create` | `save.create` | 4 chỗ (entities.yaml `operation_id`, identity.md, fixture d) |
| `analysis.request_generation` | `analysis.request_reanalysis` | fixture g |
| `source.fetch_metadata` | `research.fetch_work_metadata` | fixture a, c, g |
| `identity.resolve` | `identity.resolve_target` | fixture b, g, h — PC02 đã dùng một tên rút gọn không tồn tại; nay khớp `ports.yaml` |
| `identity.merge_works` | *(giữ)* | đã có trong `ports.yaml` (W2 đã thêm) |
| `identity.resolve_conflict` | *(giữ)* | đã có trong `ports.yaml` |
| `post.mark_source_deleted` | **bỏ hẳn** | xem A2.4 |

Các giá trị không phải operation nhưng trước đây bị đặt vào khóa `operation` của fixture đã
được đổi sang khóa `event_type`: `ack_lost` (fixture f), `system_restart` (fixture e).

### A2.4 Xóa nguồn đi qua `ingest.submit_batch` (ruling Coordinator)

- `contracts/schemas/ingest-batch.schema.json`: thêm `$defs.ingest_item.source_deleted_observed_at`
  — `oneOf [timestamp_utc_ms, null]`, tùy chọn; kèm mô tả nói rõ **không có operation riêng**,
  server ghi theo quy tắc đơn điệu, và `null`/vắng mặt nghĩa là "không có quan sát", **không**
  phải "post còn sống". Thêm `x-contract.source_deletion_note`.
- `contracts/data/entities.yaml`: `post.source_deleted_observed_at` đổi mô tả sang đường đi mới;
  thêm `entities[post].immutability.monotonic_fields` khai rằng đây là **cột duy nhất** của một
  hàng post đã tồn tại mà một item ingest trùng `x_post_id` được phép ghi, và chỉ khi đang NULL;
  `transactions[TXN-ingest-batch].rows_written_together` thêm dòng cập nhật đơn điệu này;
  `forbidden_effects` thêm "ghi đè giá trị đã NOT NULL".
- `acceptance/fixtures/identity/e-source-deleted-snapshot-intact.json`: viết lại chuỗi sự kiện.
  Fixture nay mang một `batch` thật (`validation_target` + `expected_validation: accept`,
  `payload_hash` tính thật bằng `sha256(JCS(payload_core))`), oracle thêm
  `posts_inserted_in_batch = 0`, `posts_duplicate_in_batch = 1`, và hai `forbidden_effects` mới.
  Nhờ vậy fixture (e) giờ kiểm cả I02 lẫn I08/I17.
- `acceptance/fixtures/identity/README.md`: cập nhật bảng danh mục và thêm quy tắc "mọi
  `operation` trong `events` phải tồn tại trong `ports.yaml`; sự kiện không phải operation dùng
  `event_type`".

## A3. Before/after hash

| Path | Before sha256 (PKT-PC02) | Before bytes | After sha256 | After bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `24a83d8ab4e8238b9cd9f68f9da91d3fe804e3a9a2db489a20dfe35708137d3b` | 120129 | `88b2482ede392e581b1d4eb0640bca0810ce94953bd8ada7c9b1e6b7f5ebb8fb` | 121662 |
| `contracts/data/identity.md` | `d128589438226d109cb3e44d49b16f2d5f9d893f138e1138f22226005c94918f` | 20438 | `01976cabe4dae4e587cb0e555ca6a0176c5726c0815207bb04287cb5d1169571` | 20518 |
| `contracts/data/invariants.md` | `417dfcdd8b30cb1e514d1c4d2a14fda1a571e73e93c47255269895f63a14b300` | 25377 | `844576bc39024ba66186db4cf0f461a8bc636ccb86fb70b07b2feac7ec40fbbd` | 25513 |
| `contracts/schemas/target.schema.json` | `035ada0d94a4fe473de271a1ed9c1349e6942e3a53971419d0e7a845e2292dd0` | 7192 | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` | 7283 |
| `contracts/schemas/ingest-batch.schema.json` | `a974ce8c555d63a3a1a02412660bc0411d5f2f300e997ace09856d8a8e925716` | 12260 | `01c4d01346d32f165bc9c98060675adb524350ddf76507c888ffd3cd7bdf71f9` | 13564 |
| `acceptance/fixtures/identity/README.md` | `1e43fa06f75bd2ac3077a502c074b049f3ecf5504b380b4cb18e635914443165` | 7776 | `404ce1012c319a6db8362a65c85c581b32f0599f7503dd00be3105d1cb99e0b3` | 8056 |
| `…/a-merge-doi-arxiv.json` | `a5e7e06957a21e9b7425d514b94730e1a2d7dc13f9d9164b323dbe8c0c606f69` | 17423 | `6bcd88606ad3330126e7e01e4fa4d91050c93df4ccbd21943d11335c7a42298d` | 17430 |
| `…/b-post-only-missing-ids.json` | `1a3b21d3621a6ad3faf6f3121ce2d7266edd1cf0d465a7890e42a568341da9bd` | 4308 | `ff2e50728f35299f6d93eb599887a72b57eab5f3f2117d0a338b6cd8d05d73e7` | 4315 |
| `…/c-identity-conflict.json` | `b0d58468b842bfb473c09b6efebf87bdc507aa567b057884e6d9692cfe35a117` | 7368 | `44c614b2e71fa6b0410cd0e36930ebfefc0827e64ddc51ddbc77cfb8e0f6446b` | 7375 |
| `…/d-concurrent-save-app-telegram.json` | `3e4cc52cfd21222f5b9c0afa1abc35802e41ef14f873a92a775d64c5f4693193` | 7601 | `5dfc730ac2366516b54fc4c9a529e7c40a75c619a2c9ce5024ca25e0c8c87c04` | 7598 |
| `…/e-source-deleted-snapshot-intact.json` | `c9bccb3117e2376495915e55b6b6be030b9934155fd331f58b426e6335447753` | 6837 | `7774550efe44f81e526f65e0dd59f1c18c3e470d694a728c4a8d4c7821ec9816` | 8849 |
| `…/f-ingest-replay-idempotent.json` | `790a2c286bbf6c089328c69d99c3b6ee589ced5a725b1d6f37205de27a628bf7` | 12333 | `89989748fdc2ba9a7aca759fafac3b462f04b31bc287331bb0e32dfee4bef026` | 12334 |
| `…/g-arxiv-version-v1-v2.json` | `2d564f67fb10bc788453b2720d20d74e4aeee07aa2d40d6d336c8853e2e9515e` | 9289 | `5addc48d4ff22221b259276cdd8b8cc1e762437b1899fca725fe682126fee1a9` | 9303 |
| `…/h-five-posts-thread-one-target.json` | `b891ba75f6c0d58455a65e309d3dd2f133483ae338b72293841adfd66665c966` | 9295 | `fd8d28f835db6ae819a90d777dced438fcedb2f3a71f02e5f09dc35f9954aa90` | 9302 |

**Không đổi** (hash sau = hash trước, đã kiểm): `neg-ingest-batch-bad-payload-hash.json`
(`5a6f1498…`, 2311), `neg-ingest-batch-empty-items.json` (`f95cd4a2…`, 1778),
`neg-ingest-batch-missing-idempotency-key.json` (`95967e60…`, 2358),
`neg-ingest-batch-timestamp-precision.json` (`5675c24e…`, 2408),
`neg-ingest-batch-unknown-field.json` (`10ff2e91…`, 2518),
`pos-ingest-batch-valid.json` (`c4ad116e…`, 2237).

`evidence/handoffs/PC02-handoff.md`: before `607ede0ed44940cf5348e140e955c51988ac7d3c19ae933e2847ddf9ece2ed9f` / 17155 bytes; after = file này (APPEND, nội dung PKT-PC02 giữ nguyên byte-for-byte).

## A4. Evidence records

### EV-PC02-01/02/03 (chạy lại sau khi sửa)

- type: `SELF_VALIDATION`
- command: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 verify_pc02.py`
- runtime: Python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3
- started/ended UTC: 2026-09-06T17:31:08Z / 2026-09-06T17:31:09Z
- **exit code 0**, `RESULT: PASS (0 fail)`, **32 dòng PASS** (trước sửa: 30)
- observed: 37 entity / 4 transaction; 2 schema hợp lệ Draft 2020-12; 14 fixture parse;
  **37 target object** validate; **4 positive batch ACCEPT** (thêm fixture e) và **5 negative
  REJECT** với lý do đúng; **4/4 payload_hash tái lập đúng**; 20 tên bảng tham chiếu tồn tại;
  16 bảng fixture tồn tại; ngoại lệ `owner_id` vẫn đúng (`owner`, `schema_migration`)
- status: **PASS**

### EV-PC02-04 (mới) — kiểm tồn tại MOD id và operation id theo PC01

- type: `SELF_VALIDATION`
- command: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 check_refs_pc01.py`
- started/ended UTC: 2026-09-06T17:31:09Z / 2026-09-06T17:31:10Z (và chạy lại lúc 17:33Z)
- input: 5 file hợp đồng PC02 + 14 fixture + `contracts/modules.yaml` + `contracts/ports.yaml`
- oracle:
  1. mọi token `MOD-…` xuất hiện trong file PC02 phải có trong `modules.yaml.modules[].id`;
  2. mọi token `<domain>.<verb_noun>` với `domain` thuộc tập tiền tố operation của
     `ports.yaml` phải có trong `ports.yaml.operations[].operation_id` — loại trừ tường minh
     token dạng `<entity>.<field>` (tra theo `entities.yaml`) và tên file (`.md`, `.json`, `.yaml`);
  3. mọi `events[].operation` trong fixture phải có trong `ports.yaml`;
  4. không còn `MOD-report-builder`, `MOD-backup-operator`, `saved.create`,
     `analysis.request_generation`, `source.fetch_metadata`; `post.mark_source_deleted` chỉ
     được xuất hiện trong câu phủ định tường minh.
- expected/observed: PASS / **PASS**. 19 MOD id dùng, tất cả tồn tại. 12 operation id dùng,
  tất cả tồn tại: `analysis.request_reanalysis`, `analysis.submit_result`,
  `backup.reconcile_after_restore`, `delivery.create_intent`, `delivery.dispatch_next`,
  `identity.merge_works`, `identity.resolve_conflict`, `identity.resolve_target`,
  `ingest.submit_batch`, `report.publish`, `research.fetch_work_metadata`, `save.create`.
- exit code: 0 · status: **PASS**
- limitations: kiểm **tồn tại tên**, không kiểm ngữ nghĩa — không chứng minh rằng operation
  được tham chiếu thực sự có request/response schema phù hợp với transaction mô tả ở PC02, và
  không kiểm `allowed_edges` của `modules.yaml` (caller nào được gọi callee nào). Cần một pass
  của PC09 để kiểm cặp edge/operation.

## A5. Baseline nguồn và dependency

SRC-PLAN `f65bb046…70f40` (64915) và SRC-SPEC `d35e1f2d…e0e26` (41770): **khớp**, kiểm lại lúc
17:31Z. Không STALE_BASELINE với nguồn.

**Cảnh báo drift ở dependency PC01.** Khi bắt đầu packet này (17:26Z) hai file PC01 có hash:

| File | Lúc đọc (17:26Z) | Lúc chạy EV-PC02-04 và lúc handoff (17:31–17:34Z) | Bytes cuối |
| --- | --- | --- | --- |
| `contracts/modules.yaml` | `10757e27e8af4b212714c554a5e27a9938b39ea0c9584344f5fab1335781d941` | `389487f809e2f69140414d71f72ce249ff612b4b72824d50c46041a4520367c8` | 67993 |
| `contracts/ports.yaml` | `f935eef973fce15b7dab9491384ce38b8f18b487c827f6dac94d4b0a0a57d0c3` | `bde5f133297c1aa381f2db8f5b861a54f9df593adc8c6fb9b7606a8f37dd4470` | 98442 |

Cả hai đã đổi **trong lúc packet này chạy** (nhất quán với thông tin của Coordinator rằng W2
đang thêm `identity.merge_works` vào `ports.yaml`). Xử lý: EV-PC02-04 đọc bản **hiện hành** và
PASS; hash được đo ngay trước và ngay sau lần chạy cuối và **ổn định** (`389487f8…` /
`bde5f133…`). Bản hiện hành có 24 module và 82 operation, và ánh xạ `data_owner_of` mà PC02
dựa vào không đổi. Vì vậy **không** báo STALE_BASELINE, nhưng ghi rõ: kết luận của EV-PC02-04
chỉ có hiệu lực với đúng hai hash ở cột thứ ba. Nếu PC01 còn đổi tiếp, phải chạy lại
`check_refs_pc01.py`.

## A6. Mismatch còn lại (không giải trong packet này)

| # | Mismatch | Vì sao chưa sửa | Đề xuất |
| --- | --- | --- | --- |
| M1 | **Tên entity**: PC01 `data_owner_of` gọi là `work_alias`, PC02 gọi là `identity_alias` | Packet chỉ cấp ruling cho **module id** và **operation id**. Đổi tên entity sẽ lan sang identity.md, invariants.md, 8 fixture và các tham chiếu tương lai của PC03/PC04 | **CR-PC02-10** → Coordinator ra ruling một tên; PC02 sẵn sàng đổi trong packet FIX2 |
| M2 | `ingest_checkpoint` (PC01) vs `checkpoint` (PC02); `lease`/`assignment` (PC01) vs `assignment_lease` (PC02); `coverage_ledger` (PC01) vs `coverage_window` (PC02); `vector` (PC01) vs `tag_vector` + `work_label.vector` (PC02) | Cùng lý do M1 | Gộp vào **CR-PC02-10** |
| M3 | `source_connection` **không có owner** trong `data_owner_of` của bất kỳ module nào | Không có nguồn chuẩn để chọn | Tạm gán `MOD-settings-service` (tương tự `provider_config`), đánh dấu PROVISIONAL. **CR-PC02-09** → PC01 bổ sung owner |
| M4 | `outbox_intent` không có trong `data_owner_of`; PC01 chỉ có `delivery*` | Suy ra từ `MOD-delivery-service.inbound_operations` có `delivery.create_intent` và `delivery.dispatch_next` | Gán `MOD-delivery-service`, PROVISIONAL. Gộp vào **CR-PC02-09** |
| M5 | `schema_migration` không có owner; PC01 `MOD-data-store` sở hữu `sqlite_database_file`, `wal` | Suy ra hợp lý | Gán `MOD-data-store`, PROVISIONAL. Gộp vào **CR-PC02-09** |
| M6 | EV-PC02-04 không kiểm `allowed_edges`: chưa chứng minh caller trong PC02 được phép gọi callee | Ngoài phạm vi packet | **CR-PC02-11** → PC09 thêm pass kiểm cặp (caller, operation) theo `modules.yaml.allowed_edges` |

CR cũ vẫn mở, không đổi: CR-PC02-03 (PC07), CR-PC02-04 (Owner/PC05), CR-PC02-05 (PC03),
**CR-PC02-06 (PC04, `first_announced` sau merge — nay xác nhận thêm: PC01 giao
`first_announced_ledger` cho `MOD-report-service`, đúng như PC02 giả định)**,
CR-PC02-07 (PC08), CR-PC02-08 (PC09). CR-PC02-01 và CR-PC02-02 **đã đóng** bằng packet này.

## A7. Kết thúc

Sau addendum này, `worker-W3` không ghi thêm file nào. Lease `LEASE-PC02-e2` được nhả lúc
2026-09-06T17:34Z. Không chạy lệnh git mutation, không network, không file ngoài write target,
không `__pycache__` trong repo (`PYTHONDONTWRITEBYTECODE=1`).

---

# ADDENDUM — PKT-PC02-FIX2 (khắc phục finding của AUDIT_REPORT PKT-A1-R1)

## B1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX2` · authority `AUTH-COORD-PC02-FIX2` · lease `LEASE-PC02-e3` (fencing 3) |
| worker principal | `worker-W3` · expires_at 2026-09-07T04:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| findings addressed | F-A1R1-01 (R-01), F-A1R1-02 (R-02), F-A1R1-03 (R-03), hook SC32 từ R-04 |
| finding state | `FIX_PROPOSED` — **không** finding nào được đóng ở đây; auditor-A1 xác minh ở freeze FC-W1 epoch 2 |
| next actor | Coordinator · lease_released_at | 2026-09-06T18:05Z |

## B2. F-A1R1-01 — checkpoint (ruling R-01)

**Đã đổi**

1. `invariants.md` I02 **counterexample 2 viết lại**. Trước: *"Checkpoint ở transaction riêng.
   Ghi post ở T1, ghi checkpoint ở T2 … → Gate FAIL"* — câu này kết án chính đường mà PC01 đã
   đóng băng. Sau: kết án **"checkpoint tham chiếu hoặc tiến qua `ingest_sequence` của post
   chưa commit, hoặc ghi checkpoint ở transaction riêng TRƯỚC transaction chứa post đó"**, kèm
   một khối *"Cái này KHÔNG bị cấm"* nêu đích danh `ingest.commit_checkpoint`. Ranh giới được
   phát biểu thành một câu kiểm được: *một checkpoint không bao giờ được trỏ vượt qua post đã
   bền*, chứ không phải *checkpoint không bao giờ được ở transaction riêng*.
2. `entities.yaml` — thêm **`TXN-checkpoint-only`** (transaction thứ năm), `operation_id:
   ingest.commit_checkpoint`, với: hạn chế cứng (0 item), guard
   (`proposed_acked_through <= acked_through hiện hành` → vượt là `VALIDATION_ERROR`, không ghi
   một phần), `rows_written_together` (1 checkpoint + 1 receipt), commit point, external
   observer (before/after/never), idempotency (`assignment_id + checkpoint_seq` theo PC01),
   failure timeline 5 mốc, và `forbidden_effects`.
3. **Oracle** (yêu cầu trung tâm của finding), có ở cả hai file:
   `checkpoint.acked_through_ingest_sequence <= MAX(ingest_receipt.max_ingest_sequence)` trên
   tập receipt đã commit; phụ trợ: `<= MAX(post.ingest_sequence)`, delta `#post` = 0 và delta
   `acked_through` = 0 qua mỗi lời gọi, mọi count = 0 với receipt `checkpoint_only`, và tập
   `(id, sequence, acked_through)` chỉ được thêm phần tử.
4. `ingest_receipt` thêm cột **`receipt_kind`** (`batch_ingest` | `checkpoint_only`) để 0 item
   của một checkpoint-only không bị đọc nhầm thành một batch bị từ chối.
5. `entities[checkpoint]` thêm `write_paths`: đúng **hai** đường ghi hợp lệ, đường thứ ba bị
   cấm tường minh. `owner_module` = `MOD-ingest-service` (một module duy nhất, như R-01 yêu
   cầu; giá trị này đã đúng từ FIX1, nay được khẳng định lại trong I02).

**Diễn giải cần Coordinator biết.** R-01 viết *"single row update of `checkpoint` + receipt"*.
PC02 giữ `checkpoint` **append-only** (đã khóa ở PKT-PC02: `sequence` UNIQUE, không UPDATE),
nên hiện thực bằng **một hàng checkpoint mới** với `acked_through` không đổi, thay vì UPDATE
tại chỗ. Ngữ nghĩa tương đương (một mốc con trỏ mới) và giữ được lịch sử con trỏ để chẩn đoán
khi cursor mất hiệu lực. Ghi trong `TXN-checkpoint-only.append_only_note`. Nếu Coordinator
thực sự muốn UPDATE tại chỗ thì đó là đổi mô hình bảng → **CR-PC02-12**, cần packet mới.

## B3. F-A1R1-02 — actor của fixture (ruling R-02)

**Đã sửa đúng 10 event** mà auditor liệt kê (không nhiều hơn, không ít hơn):

| Fixture | seq | operation | actor trước | actor sau | performed_by |
| --- | --- | --- | --- | --- | --- |
| `a` | 1 | `research.fetch_work_metadata` | MOD-research-connector | **MOD-ingest-service** | MOD-research-connector |
| `a` | 2 | `identity.merge_works` | MOD-backend-api | **MOD-ingest-service** | MOD-identity-service |
| `c` | 1 | `research.fetch_work_metadata` | MOD-research-connector | **MOD-ingest-service** | MOD-research-connector |
| `c` | 2 | `identity.merge_works` | MOD-backend-api | **MOD-ingest-service** | MOD-identity-service |
| `b` | 2 | `identity.resolve_target` | MOD-backend-api | **MOD-ingest-service** | MOD-identity-service |
| `g` | 2 | `identity.resolve_target` | MOD-backend-api | **MOD-ingest-service** | MOD-identity-service |
| `h` | 2 | `identity.resolve_target` | MOD-backend-api | **MOD-ingest-service** | MOD-identity-service |
| `g` | 3 | `research.fetch_work_metadata` | MOD-research-connector | **MOD-ingest-service** | MOD-research-connector |
| `g` | 4 | `analysis.request_reanalysis` | MOD-backend-api | **MOD-web-ui** | MOD-analysis-service |
| `e` | 2 | `ingest.submit_batch` | MOD-ingest-service | **MOD-x-collector** | MOD-ingest-service |

Ngoài ra mọi event có `operation` được bổ sung `performed_by = owner_module` của operation đó,
để fixture nói được "ai ghi dữ liệu" mà không ngụ ý "ai gọi".

`acceptance/fixtures/identity/README.md` thêm mục **"`actor`, `performed_by`, `event_type` —
ba khóa khác nhau"**, định nghĩa tường minh rằng **`performed_by` KHÔNG phải một khẳng định về
caller và không tạo ra cạnh giao tiếp nào**, kèm nguồn gốc F-A1R1-02 và một câu cấm: không
được đặt vào `actor` một module chỉ vì nó là nơi dữ liệu được ghi.

**Gate tự động** (yêu cầu "phải trở thành gate, không phải sửa một lần):
`check_actor_edges.py` → `EV-PC02-05` kiểm mọi event: `actor ∈ ports.yaml.<op>.caller_modules`
**và** `(actor, owner_module, operation) ∈ modules.yaml.allowed_edges`; event không có
`operation` bắt buộc phải có `event_type`. Gate này được gọi từ `verify_pc02.py` nên nó chạy
cùng bộ E0, không phải một lần chạy rời.

## B4. F-A1R1-03 — quyền sở hữu và tên (ruling R-03)

1. **22 entity contract mức `declared_only` được thêm** (20 theo bảng R-03 + 2 token mà
   PC01-FIX2 tạo ra theo R-04): `session`, `provider_config`, `provider_test_result`,
   `rescan_ledger`, `schedule_occurrence`, `assignment`, `worker_registration`,
   `source_fetch_log`, `analysis_task`, `first_announced_ledger`, `delivery_attempt`,
   `delivery_receipt`, `telegram_link_code`, `telegram_update_log`, `secret_ref`,
   `task_credential`, `secret_audit`, `backup_snapshot`, `backup_manifest`, `restore_record`,
   `data_deletion_audit`, `purge_challenge`. Mỗi contract có purpose, fields (type +
   nullability + ràng buộc), keys/UNIQUE **kèm `guarantees` và `does_not_guarantee`**,
   `owner_module` = owner của PC01, `origin: pc01_data_owner_of`, `finding_ref`, refs, và
   `owned_by_package` chỉ đích danh gói sẽ hoàn thiện. Entity của PC02 đi từ 37 → **59**.
2. **`first_announced_ledger` phơi bày giao diện I07** như R-03 đòi:
   `UNIQUE(owner_id, canonical_work_id)` (đúng một first-announcement cho một canonical work),
   `first_report_id`, `first_announced_at`, `merge_audit_id` (FK → `identity_merge_audit`),
   `superseded_by_merge_id`, cộng khối `i07_interface` nói rõ cái PC02 cung cấp và cái vẫn là
   quyết định của PC04 (CR-PC02-06), cùng câu cấm reset khi restore hoặc khi quét lại kho.
3. **`owner_module` của chín entity trước đây không có owner** khớp đúng R-03:
   `identity_alias`/`identity_merge_audit` → MOD-identity-service, `checkpoint` →
   MOD-ingest-service, `assignment_lease` → MOD-job-service, `coverage_window` →
   MOD-report-service, `tag_vector` → MOD-embedding-service, `source_connection` →
   MOD-settings-service, `outbox_intent` → MOD-delivery-service, `schema_migration` →
   MOD-data-store. (Tám giá trị đã đúng từ FIX1; nay được khẳng định bằng script hai chiều.)
4. `entities.yaml` thêm mục **`pc01_token_alignment`**: bảng ánh xạ đổi tên (5), token bị gỡ
   (`run_checkpoint_pointer`, kèm lý do R-01), 3 token `kind: artifact` bị loại khỏi phép so
   sánh, 9 entity được giao owner, 22 token được thêm contract. Script `EV-PC02-06` đọc **chính
   mục này**, nên ánh xạ là dữ liệu có phiên bản, không phải tri thức nằm trong đầu người viết.

## B5. Hook SC32 (từ R-04, "chỉ nếu trivial")

Thêm ở mức hook, không phải hợp đồng đầy đủ: `entities[saved_snapshot].survives_data_deletion`
và `entities[data_deletion_audit].pc02_constraint` — sau `data.delete_target`,
`#saved_snapshot` không đổi, mọi `content_hash` không đổi, `#first_announced_ledger` không đổi
(REQ-D55, REQ-AC12). Fixture SC32 đầy đủ cần ngữ nghĩa xóa của PC01/PC08 nên **để lại PC09** →
**CR-PC02-13**. README ghi rõ điều này để không ai tưởng SC32 đã có fixture.

## B6. Before/after hash

| Path | Before (FIX1) | Bytes | After (FIX2) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `88b2482ede392e58…` | 121662 | `6b7705fed971f12600c64aee55beca403283f352c7baca22c939d193a1c2810d` | 175295 |
| `contracts/data/invariants.md` | `844576bc39024ba6…` | 25513 | `134bf9f27b36ab624416809af76bf6059aa05db83cdcdb254a7277d41705fb64` | 27693 |
| `acceptance/fixtures/identity/README.md` | `404ce1012c319a6d…` | 8056 | `3f84196278ca1076bd60ec52f7315c9616d6f553ad9d543e48c1f702af15d182` | 10132 |
| `…/a-merge-doi-arxiv.json` | `6bcd88606ad33301…` | 17430 | `59cd4bdb35b9d118e9cd91a2fbb45f7dd407af0f1c6d3b833af12cb3e5ca07d7` | 17523 |
| `…/b-post-only-missing-ids.json` | `ff2e50728f35299f…` | 4315 | `4178fae5ec87a128dacf052306ac7fd8c692506527e6b220abd00459e5ca63a0` | 4408 |
| `…/c-identity-conflict.json` | `44c614b2e71fa6b0…` | 7375 | `efc5792f3216c01dec9012d787e06dc987a548fb35baed85f9a654a0487e8c97` | 7468 |
| `…/d-concurrent-save-app-telegram.json` | `5dfc730ac2366516…` | 7598 | `d83e1b7b5927d8cb206ba5a567caaedf9fff1a506a23de6e2daf4102b51a31c2` | 7727 |
| `…/e-source-deleted-snapshot-intact.json` | `7774550efe44f81e…` | 8849 | `241ca20d98f59c801957f59d8f6abcceaf1813cd0e08bce51aaab7948521ac34` | 8934 |
| `…/f-ingest-replay-idempotent.json` | `89989748fdc2ba9a…` | 12334 | `6d296af290a9bf263d662597b9638145d4807d82dc12a4b3aa9629db42d1bcf0` | 12466 |
| `…/g-arxiv-version-v1-v2.json` | `5addc48d4ff22221…` | 9303 | `2f2553965a36b8d2b2cb1d5074dcc8f0de64c1d638b774421fce28ccbca1bc3d` | 9527 |
| `…/h-five-posts-thread-one-target.json` | `fd8d28f835db6ae8…` | 9302 | `c8cde1658938d981819ba8c720c55a1d16eb78ab2ad4a5d858374631f66ec7af` | 9439 |

**Không đổi trong FIX2** (hash giữ nguyên từ FIX1): `contracts/data/identity.md`
`01976cab…` 20518 · `contracts/schemas/target.schema.json` `436cb97b…` 7283 ·
`contracts/schemas/ingest-batch.schema.json` `01c4d013…` 13564 · năm fixture `neg-*` và
`pos-ingest-batch-valid.json`.

`evidence/handoffs/PC02-handoff.md`: before `b6ff00c2653696be61da8be4790e82ff44f5c285d518bb06d36a0fedc4c77eec` / 33085 bytes; after = file này (APPEND; nội dung PKT-PC02 và PKT-PC02-FIX1 giữ nguyên byte-for-byte).

## B7. Evidence — sáu gate, một lệnh

- command: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 verify_pc02.py`
  (script này nay gọi tiếp `check_refs_pc01.py` và `check_actor_edges.py` như subprocess, nên
  một lệnh chạy cả sáu gate và exit code là hợp của cả ba)
- runtime: Python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3
- started/ended UTC: 2026-09-06T18:01:01Z / 2026-09-06T18:01:04Z
- **exit code 0**, `RESULT: PASS (0 fail)`, **39 dòng PASS** (FIX1: 32)

| Evidence | Nội dung | Kết quả |
| --- | --- | --- |
| EV-PC02-01 | parse YAML/JSON/front-matter, metaschema Draft 2020-12 | PASS — 59 entity, **5 transaction**, 2 schema, 14 fixture |
| EV-PC02-02 | target object + wire schema + payload_hash | PASS — 37 target hợp lệ; 4 positive ACCEPT, 5 negative REJECT; 4/4 payload_hash tái lập |
| EV-PC02-03 | tham chiếu entity + ngoại lệ `owner_id` | PASS — 20 tên bảng, 16 bảng fixture; ngoại lệ vẫn là `owner`, `schema_migration` |
| EV-PC02-04 | mọi MOD id / operation id tồn tại trong PC01 | PASS — exit 0 |
| **EV-PC02-05** (mới) | `fixture-actor-edge`: `actor ∈ caller_modules` và `(actor, owner, op) ∈ allowed_edges` | PASS — **22/22 event** |
| **EV-PC02-06** (mới) | so sánh tập entity ↔ `data_owner_of`, **hai chiều**, loại artifact | PASS — **59 token ↔ 59 entity, diff rỗng cả hai chiều**, owner_module khớp trên mọi entity chung |

**`modules.yaml` dùng cho EV-PC02-05/06:** sha256
`bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666`, 75088 bytes.
**`ports.yaml`:** sha256 `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206`,
111240 bytes, 85 operation. Nguồn SRC-PLAN `f65bb046…` và SRC-SPEC `d35e1f2d…`: khớp baseline.

**Residual diff: KHÔNG CÒN.** Cả hai chiều rỗng sau khi áp `pc01_token_alignment`.

**Giới hạn.** EV-PC02-05/06 là E0 tĩnh: chúng chứng minh hợp đồng tự nhất quán với registry
đã đóng băng, **không** chứng minh code, không chứng minh `allowed_edges` là đúng về mặt bảo
mật, và không kiểm request/response schema của operation khớp với transaction PC02 mô tả.
Tất cả vẫn `SELF_VALIDATION` — không có independent audit trong packet này.

## B8. Cảnh báo về PC01 đang thay đổi song song

Packet đã báo trước W2 đang sửa `modules.yaml`/`ports.yaml` dưới PKT-PC01-FIX2. Trong lúc
packet này chạy tôi quan sát **ba** trạng thái khác nhau của `modules.yaml`:

| Thời điểm | modules.yaml | ports.yaml | Khác biệt tôi phải thích ứng |
| --- | --- | --- | --- |
| 18:00 (lần chạy đầu) | `20dd3793…` (74902) | `485213cb…` (111240) | artifact token chuyển sang dạng `{token, kind}`; xuất hiện `data_deletion_audit`, `purge_challenge` |
| 18:01–18:05 (lần chạy cuối, ổn định) | `bd44d734…` (75088) | `485213cb…` (111240) | — |

Hai lần thích ứng đã thực hiện: (a) parser của EV-PC02-06 nay đọc được token dạng dict và tự
lấy `kind: artifact` từ PC01 hợp với danh sách artifact khai trong `pc01_token_alignment`;
(b) thêm entity contract cho hai token R-04 mới để không token nào mồ côi. Kết luận PASS chỉ
có hiệu lực với đúng hai hash ở hàng cuối. **Nếu W2 còn commit thêm, phải chạy lại
`verify_pc02.py` trước khi freeze FC-W1 epoch 2** — đây là điều kiện tôi không kiểm soát được.

## B9. CR và mối lo còn lại

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC02-12` | Coordinator | Xác nhận diễn giải append-only của `TXN-checkpoint-only` (B2). Nếu muốn UPDATE tại chỗ thì cần packet mới vì đó là đổi mô hình bảng. |
| `CR-PC02-13` | PC09 | Fixture SC32 đầy đủ (xóa dữ liệu gốc). PC02 chỉ để lại oracle bất biến. |
| `CR-PC02-06` | PC04 | **Vẫn mở và nay quan trọng hơn**: `first_announced_ledger` đã có hình dạng và `merge_audit_id`, nhưng policy "work thắng có kế thừa first-announcement không" vẫn chưa khóa. |
| `CR-PC02-03`, `-04`, `-05`, `-07`, `-08` | PC07 / Owner-PC05 / PC03 / PC08 / PC09 | Không đổi từ FIX1. |
| `CR-PC02-09`, `-10`, `-11` | — | **Đóng** bằng ruling R-03 (09, 10) và bằng EV-PC02-05 (11, gate actor-edge nay đã tồn tại và đã chạy). |

Mối lo còn lại: (1) 22 entity mới đều ở mức `declared_only` — chúng khóa tên, owner và khóa
UNIQUE, **không** khóa state machine hay ngữ nghĩa; gói sở hữu phải hoàn thiện và có thể phát
hiện trường thiếu. (2) `TXN-checkpoint-only` chưa có fixture riêng; oracle của nó mới chỉ là
văn bản trong hợp đồng, chưa có dữ liệu vào/ra — nếu Coordinator muốn một fixture cho
`ingest.commit_checkpoint` thì đó là việc còn thiếu và nên vào PC05 hoặc PC09. (3) Không
finding nào được đóng ở đây; trạng thái đúng là `FIX_PROPOSED`.

## B10. Kết thúc

`worker-W3` không ghi thêm file nào sau addendum này. Lease `LEASE-PC02-e3` nhả lúc
2026-09-06T18:05Z. Không lệnh git mutation, không network, không file ngoài write target,
không `__pycache__`, không chạm file PC01.

---

## B11. Sửa đổi packet PKT-PC02-FIX2 (amendment của Coordinator, cùng lease `LEASE-PC02-e3`)

Amendment tới **trước** khi lease được nhả; mục B10 ở trên nói "không ghi thêm file nào" là
phát biểu tại thời điểm đó và **được thay thế bởi mục này**. Phạm vi ghi không đổi (chỉ file
PC02). Lease thực sự nhả ở B12.

### B11.1 CR-PC01-06 — `data_deletion_audit` và `purge_challenge`

**Đã có sẵn trước khi amendment tới.** Trong lần chạy EV-PC02-06 lúc 18:00, `modules.yaml`
(khi đó `20dd3793…`) đã xuất hiện hai token này và phép so sánh hai chiều đã bắt chúng là
"PC01 token không có entity contract". Tôi đã thêm hai hợp đồng `declared_only` ngay lúc đó
với `owner_module: MOD-data-admin-service` (mục B4.1, tổng 22 token). Amendment vì vậy không
đòi hỏi thay đổi mới; nó xác nhận lựa chọn đã làm. Đây là ví dụ cho thấy gate hai chiều có
tác dụng: nó phát hiện token mới của PC01 mà không cần ai báo.

### B11.2 CR-PC01-05 — hai transaction xóa

Thêm vào bản đồ transaction (nay **7** transaction):

**`TXN-delete-target`** (`data.delete_target`, `MOD-data-admin-service` thực thi, `MOD-web-ui`
gọi). Nguyên tắc trung tâm: **xóa NỘI DUNG, giữ KHUNG**.

- `deleted_rows`: `post_work`, `work_label`, `analysis_task`, `analysis_generation` rỗng, và
  `analysis` **chỉ những hàng không được `saved_snapshot.analysis_id_at_save` hoặc
  `report_item.analysis_id` (report đã publish) trỏ tới**.
- `redacted_rows`: `post` (xóa `text`, `media_refs`, `referenced_links`, `url`,
  `author_display_name`, `author_x_user_id`, `lang`, `source_snapshot_hash`; giữ `x_post_id`,
  `discovered_at`, `ingest_sequence`, receipt/run refs), `work` (xóa `title`, `paper_url`,
  `code_url`; giữ canonical ids), `work_version` (xóa `abstract_text`; giữ
  `content_fingerprint` vì đó là hash và là thành phần analysis key B07).
- `untouched` (13 bảng): `saved_snapshot`, `saved_item`, `identity_merge_audit`,
  `identity_alias`, `ingest_receipt`, `checkpoint`, `analysis_attempt`,
  `first_announced_ledger`, `coverage_window`, `pending_item_ledger`, `backfill_ledger`,
  `report`, `report_item`.
- **Vì sao redact chứ không xóa hàng `post`/`work`:** nếu xóa hàng, dedup mất khóa
  (`x_post_id` / canonical id) và đợt thu thập kế tiếp sẽ ingest lại **đúng nội dung vừa
  xóa** — thao tác tự vô hiệu hóa chính nó. Do đó thêm cột `content_state`
  (`present` | `redacted_by_owner_deletion`) trên `post` và `work` (thay đổi additive), và
  oracle re-ingest: `posts_inserted = 0`, `posts_duplicate = 1`, nội dung không được ghi lại.
- **Toàn vẹn tham chiếu:** FK giữ `ON DELETE RESTRICT`, xóa theo thứ tự lá → gốc, **cấm tắt
  `PRAGMA foreign_keys`**, và **cấm NULL hóa** `saved_snapshot.analysis_id_at_save` /
  `report_item.analysis_id` — chính ràng buộc đó là lý do tập `analysis` bị xóa phải thu hẹp.
  Đây là chỗ I08/I17 (snapshot bất biến) quyết định thiết kế xóa, chứ không phải ngược lại.
- Oracle: `#saved_snapshot` và tập `content_hash` không đổi; `#first_announced_ledger`,
  `#coverage_window`, `#backfill_ledger`, `#identity_merge_audit`, `#ingest_receipt` không
  đổi; `#post`/`#work` **không đổi**; 0 vi phạm FK; idempotent khi gọi lại.
- **PROVISIONAL (CR-PC02-14):** bản `analysis` được snapshot trỏ tới có phải "dữ liệu gốc"
  không? PC02 chọn **giữ**, vì nội dung tương đương đã nằm trong snapshot mà REQ-D55 buộc phải
  giữ. Nếu Owner muốn xóa cả summary thì phải sửa I08/I17 — đó là amendment, không phải tùy chọn.

**`TXN-purge-all`** (`data.purge_all`).

- Preconditions: kho ở `maintenance` (PC03), cụm từ gõ tay khớp `purge_challenge` do **server**
  phát (còn `active`, chưa hết hạn, dùng một lần), mọi `assignment_lease` `held` đã thu hồi.
- `tables.purged`: 39 bảng dữ liệu nghiên cứu + vận hành, liệt kê tường minh.
- `excluded_pending_owner_decision`: **19 bảng để `OWNER_DECISION_REQUIRED`**, mỗi bảng kèm câu
  hỏi cụ thể — `owner`, `settings`, `provider_config`, `provider_test_result`, `secret_ref`,
  `task_credential`, `secret_audit`, `session`, `tag`, `tag_alias`, `tag_exclusion`,
  `tag_config_version`, `telegram_link`, `telegram_link_code`, `source_connection`,
  `backup_snapshot`, `backup_manifest`, `restore_record`, `purge_challenge`. PC02 **không** tự
  quyết định, đúng như R-04 yêu cầu; phạm vi này bị chặn tường minh trong `forbidden_effects`.
- `never_purged`: `schema_migration` (mô tả cấu trúc kho, không phải dữ liệu của owner).
- Commit point một transaction; nếu engine không giữ nổi thì phải chạy theo lô với
  `data_deletion_audit` ghi trước ở trạng thái `running` → thiết kế lô thuộc PC08
  (**CR-PC02-15**), và **cấm coi kho là sạch khi audit còn `running`**.

### B11.3 Chạy lại toàn bộ gate sau amendment

- command: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 verify_pc02.py`
- started/ended UTC: 2026-09-06T18:05:37Z / 2026-09-06T18:05:40Z · **exit code 0** ·
  `RESULT: PASS (0 fail)` · 39 dòng PASS
- EV-PC02-01: 59 entity, **7 transaction**, 2 schema, 14 fixture — PASS
- EV-PC02-02: 37 target object; 4 positive / 5 negative batch; 4/4 payload_hash — PASS
- EV-PC02-03: **46** tên bảng được tham chiếu đều tồn tại (tăng từ 20 nhờ hai transaction mới
  liệt kê bảng tường minh) — PASS
- EV-PC02-04: MOD id + operation id tồn tại trong PC01 — PASS (exit 0)
- EV-PC02-05: **22/22** event, `(actor, owner, operation)` ∈ `allowed_edges` — PASS
- EV-PC02-06: **59 token ↔ 59 entity, diff rỗng cả hai chiều** — PASS

**Hash dùng cho phép so sánh (đúng bản Coordinator chỉ định):**
`contracts/modules.yaml` = `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666`
(75088 bytes); `contracts/ports.yaml` =
`485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` (111240 bytes, 85 operation).
Hai file này ổn định suốt các lần chạy 18:01–18:05 (khác với giai đoạn 18:00 khi
`modules.yaml` còn ở `20dd3793…`).

**RESIDUAL DIFF: RỖNG** cả hai chiều — 0 token PC01 thiếu entity contract, 0 entity PC02 thiếu
owner token, 0 lệch `owner_module`, 3 artifact token (`sqlite_database_file`, `wal`,
`readiness_snapshot_in_memory`) được loại đúng và không lẫn vào tập entity.

### B11.4 Hash sau amendment

| Path | Trước amendment (B6) | Sau amendment | Bytes |
| --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `6b7705fed971f126…` (175295) | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | 192018 |

Các file khác **không đổi** so với mục B6: `invariants.md` `134bf9f2…` 27693 ·
`identity.md` `01976cab…` 20518 · `target.schema.json` `436cb97b…` 7283 ·
`ingest-batch.schema.json` `01c4d013…` 13564 · `fixtures/README.md` `3f841962…` 10132 ·
8 fixture kịch bản và 6 fixture wire giữ nguyên hash của mục B6.

## B12. Kết thúc (thay thế B10)

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC02-e3` nhả lúc
**2026-09-06T18:07Z**. Không lệnh git mutation, không network, không file ngoài write target,
không `__pycache__`, không chạm file PC01. Mọi finding vẫn ở `FIX_PROPOSED`; việc xác minh
thuộc auditor-A1 ở freeze FC-W1 epoch 2.

---

# ADDENDUM — PKT-PC02-FIX3 (field-level convergence sau A1-R2)

## C1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX3` · authority `AUTH-COORD-PC02-FIX3` · lease `LEASE-PC02-e4` (fencing 4) |
| worker principal | `worker-W3` · expires_at 2026-09-07T06:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| findings | F-A1R2-01, F-A1R2-03 → `FIX_PROPOSED` (không đóng) |
| next actor | Coordinator · `lease_released_at` | 2026-09-06T18:45Z |

Scope: **chỉ** `contracts/data/entities.yaml` bị sửa. Bốn file PC02 khác nằm trong grant nhưng
không cần đổi (không hàng nào của bảng field-level chạm tới chúng) — hash giữ nguyên, xem §C4.

## C2. Delta theo từng hàng của bảng ruling FIX3

| # | Ruling | Đã làm |
| --- | --- | --- |
| 1 | `report.report_build_id` | Thêm cột (string UUIDv4, NOT NULL) + `ux_report_owner_build_id` UNIQUE(owner_id, report_build_id) kèm `guarantees`/`does_not_guarantee`. Ghi rõ cấp tại **T-RP-01 (build)**, không phải tại publish — đó là điều làm replay tra được mỏ neo sau khi mất ACK (F-A1R2-01) |
| 2 | `report.abort_reason` | Enum 6 giá trị `empty_period \| tag_version_stale \| embedding_generation_mismatch \| cas_conflict \| builder_failure \| cancelled`, nullable, + CHECK `ck_report_abort_reason` (NOT NULL ⟺ `status='aborted'`) (F-A1R2-03, CR-PC04-08/-09) |
| 3 | `coverage_window.ingest_sequence_from/to` | Hai cột integer, nửa mở, + `contiguity_oracle_vi`: cửa sổ phải nối liền trên **cả hai trục** (thời gian và ingest sequence). Lý do ghi tại chỗ: hai post cùng `discovered_at` chỉ phân biệt được bằng sequence (CR-PC04-01) |
| 4 | `backfill_ledger` | `subscription_identity_hash` (sha256 của `owner_id + "\n" + tag đã chuẩn hóa`), `entitlement` enum 3 giá trị, `entitlement_reason`; + partial `ux_backfill_subscription_consumed` UNIQUE(owner_id, subscription_identity_hash) WHERE `consumed_in_report_id IS NOT NULL` (CR-PC04-02) |
| 5 | `run` — "16 additive columns" | Thêm **17** cột đúng như `contracts/state/run.yaml §fields`: 9 ở `added_by_pc03` + 8 ở `coverage_metadata`. **Ruling ghi 16; run.yaml có 17.** Tôi thêm cả 17 và ghi lại chênh lệch thay vì tự chọn bỏ một cột — xem §C6 |
| 6 | `delivery_part.state += sending` | Enum thành `pending \| sending \| sent \| unknown \| failed`, kèm giải thích `sending` là trạng thái mà crash biến thành `unknown` (CR-PC03-07) |
| 7 | `restore_record.operator_ack_*` | `operator_ack_at`, `operator_ack_principal` (NOT NULL khi ack), `operator_ack_note` (CR-PC08-05) |
| 8 | `backup_manifest.embedding_model_artifact_sha256` | Nullable; NULL nghĩa là restore PHẢI nêu rõ vector không tái lập được bằng manifest này (liên hệ REQ-D48/I12) |
| 9 | TXN-ingest-batch clock clamp | Thêm khối `clock_clamp` với rule/why/oracle/forbidden. `discovered_at` được KẸP về `max(discovered_at)+1 ms` khi đồng hồ server lùi. Lý do viết tại chỗ: đồng hồ lùi tạo post nằm TRƯỚC biên trái của cửa sổ đã đóng ⇒ mất dữ liệu im lặng, đúng thứ I06 phải chặn (CR-PC04-03) |
| 10 | `telegram_link_attempt` (CR-PC07-02) | Entity mới, `status: specified`, owner `MOD-telegram-adapter`; `chat_id_hash` (sha256, **không** lưu chat ID thô của người lạ), `attempted_at`, `outcome` enum 5 giá trị, `link_code_id`, index không-UNIQUE cho cửa sổ trượt; `rate_limit_rule` (vượt ngưỡng ⇒ **vẫn im lặng**, không bao giờ trả `RATE_LIMITED` cho chat chưa liên kết); `retention` **30 ngày PROVISIONAL** — ngoại lệ có chủ ý của REQ-D58 vì bảng chứa dấu vết của người KHÔNG phải owner |
| 11 | Transaction map | Thêm **`TXN-report-publish`** (transaction thứ 8): rows_written_together (9 bảng), `idempotency.anchor = report_build_id` kèm lập luận vì sao KHÔNG dùng `coverage_window` làm mỏ neo, `cas` (guard + ba guard phụ ánh xạ sang `abort_reason`), oracle 6 dòng, failure timeline 4 mốc, forbidden 6 dòng. Bao trùm cả ba yêu cầu của packet: publish CAS trên `report_build_id`, tiêu thụ backfill, coverage advance |
| 12 | **Amendment: CR-PC06-02** | `analysis_task.state` căn lại theo `contracts/state/analysis.yaml §enums.item_state` (nguồn có thẩm quyền): `pending \| running \| retry_wait \| valid \| failed \| unknown_attempt`. `claimed` bị **gỡ khỏi enum** và thay bằng ba cột con trỏ `claimed_by_worker_identity` / `claimed_lease_id` / `claimed_at` (NOT NULL ⟺ `state='running'`). `partial_index` đổi thành `WHERE state NOT IN ('valid','failed')`. Thêm khối `state_authority` ghi ánh xạ |

### C2.1 Ánh xạ enum `analysis_task.state` (CR-PC06-02)

| PC02 (cũ) | analysis.yaml (chuẩn) | Ghi chú |
| --- | --- | --- |
| `pending` | `pending` | không đổi |
| `claimed` | `running` + 3 cột `claimed_*` | claim là **chuyển trạng thái**, không phải trạng thái riêng; giữ ai-đang-giữ dưới dạng con trỏ |
| `running` | `running` | không đổi |
| `retry_wait` | `retry_wait` | không đổi |
| `done` | `valid` | terminal |
| `failed` | `failed` | terminal |
| `abandoned` | `failed` | analysis.yaml không có trạng thái bỏ dở riêng; hết budget là `failed` (T-AN-07/T-AN-10) |
| — | `unknown_attempt` | **mới với PC02**: quasi-terminal, không tự rời trạng thái ngoài chính sách rerun (T-AN-08/09/10) |

Lưu ý phân biệt đã ghi trong file: `analysis_task.state = 'valid'` là trạng thái của **task**;
`analysis.status = 'valid'` là **kết quả**. Ranh giới attempt/kết quả vẫn là I16.

## C3. Hash trước/sau

| Path | Before (FIX2) | Bytes | After (FIX3) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | 192018 | `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece` | 214203 |

**Không đổi trong FIX3** (nằm trong grant nhưng không có hàng ruling nào chạm tới):
`contracts/data/invariants.md` `134bf9f2…` 27693 · `contracts/data/identity.md` `01976cab…` 20518 ·
`contracts/schemas/target.schema.json` `436cb97b…` 7283 ·
`contracts/schemas/ingest-batch.schema.json` `01c4d013…` 13564 · toàn bộ 14 fixture identity.

`evidence/handoffs/PC02-handoff.md`: before `d00b555a5a7f48d1f32de67238efd680d9399893551d833781de26ddb471c27d` / 57585 bytes; after = file này (APPEND; ba phần trước giữ nguyên byte-for-byte).

## C4. Evidence

Ba script, chạy 2026-09-06T18:42:19Z → 18:42:23Z, runtime Python 3.12.3 / PyYAML 6.0.1 /
jsonschema 4.10.3, type `SELF_VALIDATION`:

| Script | Nội dung | Exit | Kết quả |
| --- | --- | --- | --- |
| `verify_pc02.py` (gộp 6 gate EV-PC02-01…06) | parse, metaschema, target objects, wire batch, tham chiếu entity, owner_id, + gọi hai script dưới | **0** | `RESULT: PASS (0 fail)`, **39 PASS** — **60 entity, 8 transaction**; 37 target object; 4 positive / 5 negative batch; **47** tên bảng tham chiếu đều tồn tại (tăng từ 46 nhờ TXN-report-publish); ngoại lệ `owner_id` vẫn đúng |
| `check_refs_pc01.py` (EV-PC02-04) | mọi MOD id / operation id tồn tại trong PC01 | **0** | `RESULT: PASS (0 fail)` |
| `check_actor_edges.py` (EV-PC02-05/06) | fixture-actor-edge + so sánh tập hai chiều | **0** | `RESULT: PASS (0 fail)` — 22/22 event; **60 token ↔ 60 entity** |

Hash PC01 dùng cho phép so sánh (đo tại lần chạy):
`contracts/modules.yaml` = `89b348aa8d3f89d38c945a7f15a8fe2c46e2619a1226649e4633bf30367264f5` (75794 B);
`contracts/ports.yaml` = `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a` (121958 B).
Dependency đọc để lấy tên trường: `contracts/state/run.yaml` = `fcad82589aaee43fb157…`;
`contracts/state/analysis.yaml` = `73be908d0da32fb217dd45b1f296d4e10954ec7b2507c689c9e73693a9761254`.
Nguồn SRC-PLAN `f65bb046…` / SRC-SPEC `d35e1f2d…`: khớp baseline.

### RESIDUAL DIFF: **RỖNG cả hai chiều** — khác kỳ vọng của packet

Packet dự đoán "1 reverse residual cho `telegram_link_attempt` cho tới khi PC01 thêm".
Thực tế PC01 **đã thêm** trước khi tôi chạy gate: `modules.yaml` (bản `89b348aa…`) khai
`telegram_link_attempt` thuộc `MOD-telegram-adapter.data_owner_of`, khớp đúng `owner_module`
tôi đặt. Vì vậy so sánh ra **60 ↔ 60, diff rỗng**, không phải 1 residual.
**CR-PC02-16 do đó đã được PC01 đáp ứng trước khi được nêu** — tôi vẫn ghi nó ở §C5 để
Coordinator đối chiếu, nhưng nó không còn là việc phải làm.

## C5. CR và quyết định

| ID | Tới | Trạng thái |
| --- | --- | --- |
| `CR-PC02-16` | PC01 | **Đã được đáp ứng trước** — `telegram_link_attempt` đã có trong `data_owner_of` của `MOD-telegram-adapter` |
| `CR-PC02-17` | Owner / PC08 | Retention **30 ngày PROVISIONAL** cho `telegram_link_attempt`. Đây là ngoại lệ có chủ ý của REQ-D58 ("giữ vô thời hạn") vì bảng chứa dấu vết của người không phải owner. Cần Owner chốt |
| `CR-PC07-02` | — | **Đóng** bởi entity `telegram_link_attempt`. Marker `pending_cr` trong `acceptance/fixtures/telegram/i-*.json` nay có thể gỡ ở packet PC07 kế tiếp (fixture đó ngoài grant của packet này) |
| `CR-PC02-12` | Coordinator | Vẫn mở (diễn giải append-only của `TXN-checkpoint-only`) |
| `CR-PC02-13`, `-14`, `-15` | PC09 / Owner / PC08 | Vẫn mở như FIX2 |

## C6. Mối lo

1. **Ruling ghi "16 additive columns", `run.yaml §fields` có 17** (9 `added_by_pc03` + 8
   `coverage_metadata`). Tôi thêm **cả 17** và ghi chênh lệch ở đây, thay vì tự chọn bỏ một
   cột. Nếu Coordinator thực sự muốn 16, cần nói rõ cột nào bị loại — tôi không đoán.
2. **`analysis_task.state` mất giá trị `abandoned`.** analysis.yaml không có trạng thái "bỏ
   dở" riêng, nên tôi ánh xạ `abandoned → failed`. Nếu PC06 cần phân biệt "hết budget" với
   "owner bỏ", đó là một giá trị enum mới trong analysis.yaml (PC03 sở hữu), không phải trong
   entities.yaml.
3. **`TXN-report-publish` mô tả điểm commit mà PC04 sở hữu ngữ nghĩa.** Tôi khóa phần dữ liệu
   (hàng nào cùng commit, CAS trên cột nào, oracle) và ghi rõ ranh giới trong `scope_note_vi`.
   Nếu PC04 thấy lệch với `time-and-tags.md §4.7.1`, đó là CR về phía tôi.
4. **PC01 đang thay đổi nhanh** (`modules.yaml` và `ports.yaml` đều đổi so với FIX2). Kết luận
   PASS chỉ có hiệu lực với đúng hai hash ở §C4; phải chạy lại trước freeze kế tiếp.
5. Không finding nào được đóng ở đây; trạng thái đúng là `FIX_PROPOSED`.

## C7. Kết thúc

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC02-e4` nhả lúc
2026-09-06T18:45Z. Không lệnh git mutation, không network, không file ngoài grant, không
`__pycache__`, không chạm file PC01/PC03/PC04.

---

# ADDENDUM — PKT-PC02-FIX4 (quy ước annotation trong fixture, ruling R4-01)

## D1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX4` · authority `AUTH-COORD-PC02-FIX4` · lease `LEASE-PC02-e5` (fencing 5) |
| worker principal | `worker-W3` · expires_at 2026-09-07T08:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` · finding F-A1R3-01 → `FIX_PROPOSED` |
| next actor | Coordinator · `lease_released_at` | 2026-09-06T19:05Z |

## D2. Delta

Đổi tên **52 khóa annotation trần** thành dạng `_` dưới `given.rows.<entity>[]` và
`expected.rows.<entity>[]`, đúng **8 file** như audit đếm:

| File | Số khóa |
| --- | --- |
| `a-merge-doi-arxiv.json` | 16 |
| `b-post-only-missing-ids.json` | 2 |
| `c-identity-conflict.json` | 4 |
| `d-concurrent-save-app-telegram.json` | 6 |
| `e-source-deleted-snapshot-intact.json` | 9 |
| `f-ingest-replay-idempotent.json` | 3 |
| `g-arxiv-version-v1-v2.json` | 9 |
| `h-five-posts-thread-one-target.json` | 3 |
| **Tổng** | **52** |

Khóa được đổi: `target` → `_target` (30), `note` → `_note` (7 trong danh sách hiển thị; tổng
theo file ở bảng trên), `save_channel_note` → `_save_channel_note`,
`payload_contains` → `_payload_contains`, `created_in_transaction` → `_created_in_transaction`.
Sáu file còn lại (`pos-*`, năm `neg-*`) không có `rows` nên không đổi.

`acceptance/fixtures/identity/README.md`: thêm **§0** phát biểu nguyên văn quy tắc R4-01 (ba
nhánh a/b/c, "không có allowlist riêng theo gói") kèm lý do; và ghi rõ rằng phép duyệt tìm
target object của EV-PC02-02 đi theo **giá trị** (`kind`), không theo tên khóa, nên
`target` → `_target` không ảnh hưởng.

## D3. Hash

| Path | Before | Bytes | After | Bytes |
| --- | --- | --- | --- | --- |
| `acceptance/fixtures/identity/README.md` | `3f84196278ca1076bd60ec52f7315c9616d6f553ad9d543e48c1f702af15d182` | 10132 | `a6beae39f431a06104ff797094c79d51b21736a74908271b355bdeb2cf8209e5` | 11369 |

Tám file JSON đã đổi (hash sau, `after`): `a-merge-doi-arxiv.json`, `b-post-only-missing-ids.json`,
`c-identity-conflict.json`, `d-concurrent-save-app-telegram.json`,
`e-source-deleted-snapshot-intact.json`, `f-ingest-replay-idempotent.json`,
`g-arxiv-version-v1-v2.json`, `h-five-posts-thread-one-target.json` — hash đầy đủ lấy được bằng
`sha256sum acceptance/fixtures/identity/*.json`; sáu file không có `rows` giữ nguyên hash của
FIX2/PKT-PC02.

## D4. Gate `fixture-field-existence` (R4-01) — cả sáu thư mục

**Lệnh chính xác, tái lập được độc lập:**

```text
cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 fixture_field_gate.py
```

Script hiện thực đúng ba nhánh của R4-01 và **không có allowlist theo gói**. Nó đọc
`contracts/data/entities.yaml` (in hash ở dòng đầu để đối chiếu) và duyệt
`given.rows` / `expected.rows` cùng mọi `*.rows` lồng một cấp (`after_event_N.rows`).

Chạy 2026-09-06T19:02:08Z → 19:02:13Z · entities.yaml
`209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece` (60 entity) · **exit 0**:

| directory | files | columns | unresolved |
| --- | --- | --- | --- |
| identity | 14 | 372 | **0** |
| reporting | 13 | 390 | **0** |
| collection | 8 | 0 | **0** |
| ai | 11 | 40 | **0** |
| telegram | 18 | 252 | **0** |
| recovery | 10 | 0 | **0** |
| **TOTAL** | **74** | **1054** | **0** |

Trước khi sửa, cùng lệnh đó cho: identity **52**, telegram **29**, reporting **6**, tổng **87**.
`collection` và `recovery` báo 0 cột vì fixture của hai thư mục đó không dùng khóa `rows`
(W4/W2 dùng cấu trúc khác) — **0 cột kiểm không có nghĩa là đã kiểm sạch**, chỉ có nghĩa quy
tắc này không áp dụng được ở đó; nêu rõ để không ai đọc nhầm là bằng chứng.

Ngoài ra: `verify_pc02.py` (nay gọi gate trên như **EV-PC02-07**) **exit 0**,
`RESULT: PASS (0 fail)`; `check_refs_pc01.py` exit 0; `check_actor_edges.py` exit 0.

## D5. Mối lo

1. `reporting` đã về 0 khi tôi chạy — W5 sửa 6 khóa của mình **đồng thời**. Con số của tôi
   đúng tại thời điểm chạy; nếu W5 còn commit tiếp thì phải chạy lại.
2. `collection`/`recovery` cho 0 cột kiểm (xem §D4). R4-01 chỉ ràng buộc khóa dưới `rows`;
   fixture không dùng `rows` nằm ngoài tầm của gate này — **CR-PC02-18** đề nghị PC09 quyết
   định có mở rộng R4-01 sang cấu trúc khác hay không.
3. Không CR nào khác, không quyết định PROVISIONAL mới.

---

# ADDENDUM — PKT-PC02-FIX5 (CR-PC07-07: ghi nhận kiểm tra điều khoản provider)

## E1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX5` · authority `AUTH-COORD-PC02-FIX5` · lease `LEASE-PC02-e6` (fencing 6) |
| worker principal | `worker-W3` · expires_at 2026-09-07T12:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T00:27Z |

Kiểm trước khi ghi: `date -u` = 2026-09-07T00:23:56Z (trong hạn), SRC-SPEC `d35e1f2d…` và
SRC-PLAN `f65bb046…` khớp baseline §2.

## E2. Delta

`entities.yaml` → `provider_config` (`ENT-provider-config`) thêm **ba cột** và **hai CHECK**:

| Cột | Kiểu | Nullable | Ý nghĩa |
| --- | --- | --- | --- |
| `terms_check_at` | timestamp_utc_ms (RFC 3339 ms) | có | Thời điểm owner xác nhận ĐÃ ĐỌC điều khoản của nhà đó. NULL = chưa đọc ⇒ không được bật |
| `terms_check_by` | string | có | Principal đã xác nhận. NOT NULL khi `terms_check_at` NOT NULL |
| `terms_doc_ref` | string | có | Định danh tài liệu điều khoản: URL + ngày truy cập, hoặc phiên bản/hash. **`KC` theo REQ-A5** |

| CHECK | Biểu thức |
| --- | --- |
| `ck_provider_config_terms_before_enable` | `enabled = 0 OR terms_check_at IS NOT NULL` |
| `ck_provider_config_terms_by` | `terms_check_at IS NULL OR terms_check_by IS NOT NULL` |

Ràng buộc thứ nhất là điểm của gói này: REQ-A5 và ADR-0010 đòi đọc điều khoản của **từng** nhà
trước khi bật đường CLI/ACP cho nhà đó; trước FIX5 đó chỉ là văn xuôi, nay là ràng buộc kiểm
được. `terms_check_note_vi` ghi rõ ba cột này ghi nhận **việc đã đọc**, không thay thế việc
đọc, và `terms_doc_ref` khóa **chỗ để ghi** chứ không khẳng định đã đọc — Pre-code không có
mạng nên chưa nhà nào được đọc; cấm điền giá trị suy đoán.

Grant thứ hai (file PC07): gỡ **2** marker `pending_cr: CR-PC07-07` khỏi
`acceptance/fixtures/ui/sc51-first-time-setup.json` cùng map `pending_cr_fields`, thêm
`terms_check_by`/`terms_doc_ref` = NULL vào hai hàng, và **nâng oracle SC51 lên dạng mạnh**:
`COUNT(provider_config WHERE enabled = true AND terms_check_at IS NULL) = 0` (bỏ
`stronger_form_pending`). `acceptance/fixtures/ui/README.md` §3 đổi tiêu đề thành "hiện KHÔNG
còn cái nào", kể lại lý do marker từng tồn tại và nêu `terms_doc_ref` vẫn `KC`.

## E3. Hash

| Path | Before | Bytes | After | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece` | 214203 | `4d93232f02adcf7d74747f758e74af2c90e703909ea19072c5f2c3ee0031176b` | 216429 |
| `acceptance/fixtures/ui/sc51-first-time-setup.json` | `4671d87f7bf7efa062d89c23cc5a8b1e7586f27656ffa506b1150e37132c3b7b` | 15420 | `19820cec74bb3a73dd9945674ce3dd88fd9d18f1d15ae0b48ebef938b92f18d7` | 13282 |
| `acceptance/fixtures/ui/README.md` | `f77845849187ce9036fecabb2ab9f6035ec3e58230d93a5778e6bdefd84b3591` | 5973 | `81bf7d7bf7666f0ba5dc7bf9cbc610836e5a5f5a30e0d1daebe906df04faeac7` | 6326 |

## E4. Evidence

Chạy 2026-09-07T00:24:49Z → 00:24:53Z:

| Script | Exit | Kết quả |
| --- | --- | --- |
| `verify_pc02.py` (6 gate) | **0** | `RESULT: PASS (0 fail)` — 60 entity, 8 transaction, 47 tên bảng tham chiếu tồn tại |
| `check_actor_edges.py` (set-comparison) | **0** | **60 token ↔ 60 entity**, diff rỗng hai chiều |
| `fixture_field_gate.py` (R4-01, 7 thư mục) | **0** | **0 unresolved**; `ui` 2 file / **121 cột** (tăng từ 117 nhờ hai cột `terms_*` mới được khẳng định) |

`grep -c pending_cr acceptance/fixtures/ui/*.json` = **0** ở cả hai file.

Hash upstream tại lần chạy: `contracts/ports.yaml`
`87c95da46c607c977a7f0421cc4110745575efc47581952d3d619a4147f1f305` (122712 B);
`contracts/modules.yaml` `fa7af49490a2e6da625e8282df0dee400078a099a6cf6b71352439d3dbe833d0`
(98983 B) — lại đổi so với `e63181eb…` của PKT-PC07-FIX3 (W2 vẫn đang sửa `denied_cases`);
`allowed_edges` không đổi nên so sánh tập không bị ảnh hưởng.

## E5. Hash sau (đo lúc kết thúc gói)

| Path | sha256 | Bytes |
| --- | --- | --- |
| `contracts/data/entities.yaml` | `4d93232f02adcf7d74747f758e74af2c90e703909ea19072c5f2c3ee0031176b` | 216429 |
| `acceptance/fixtures/ui/sc51-first-time-setup.json` | `19820cec74bb3a73dd9945674ce3dd88fd9d18f1d15ae0b48ebef938b92f18d7` | 13282 |
| `acceptance/fixtures/ui/README.md` | `81bf7d7bf7666f0ba5dc7bf9cbc610836e5a5f5a30e0d1daebe906df04faeac7` | 6326 |

`CR-PC07-07` **ĐÓNG**. Không CR mới. `terms_doc_ref` giữ trạng thái `KC` (REQ-A5) — đó là điều
kiện chưa giải được trong Pre-code, không phải thiếu sót của hợp đồng.

---

# ADDENDUM — PKT-PC02-FIX6 (F-A2R1-06: mã lỗi chưa đăng ký trong văn xuôi)

## F1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX6` · authority `AUTH-COORD-PC02-FIX6` · lease `LEASE-PC02-e7` (fencing 7) |
| worker principal | `worker-W3` · expires_at 2026-09-07T16:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` · finding F-A2R1-06 → `FIX_PROPOSED` |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T01:16Z |

`date -u` = 2026-09-07T01:11:59Z (trong hạn); SRC-SPEC `d35e1f2d…`, SRC-PLAN `f65bb046…` khớp baseline §2.

## F2. Delta

Theo ruling F-06: dùng mã **đã đăng ký** `CONFLICT`, không đăng ký thêm mã mới.

1. `entities.yaml` `saved_item` → `keys.unique[ux_saved_active_owner_target].guarantees[1]`:
   `SAVE_ALREADY_EXISTS` → `CONFLICT`, kèm câu nói rõ mã nằm trong `contracts/errors.yaml`
   và `save.create.error_codes` liệt kê nó (W2 thêm song song).
2. `entities.yaml` `saved_item.concurrency` thêm hai trường có cấu trúc — `error_code: CONFLICT`
   và `error_code_note_vi` — để lần sau gate đọc được mã ở **trường có cấu trúc**, không chỉ
   trong văn xuôi. Đây chính là điểm mù mà F-A2R1-06 nêu (giống F-A2R1-01). Ghi chú cũng phân
   biệt rõ: `already_saved: true` là **trường phản hồi**, không phải mã lỗi.

## F3. Quét toàn bộ file PC02

Quét mọi token SCREAMING_SNAKE trong `entities.yaml`, `identity.md`, `invariants.md` và 15 file
`acceptance/fixtures/identity/*`, đối chiếu 28 mã của `contracts/errors.yaml`:

| Token | Ở đâu | Kết luận |
| --- | --- | --- |
| `SAVE_ALREADY_EXISTS` | entities.yaml | **Mã lỗi chưa đăng ký — ĐÃ SỬA** thành `CONFLICT` |
| `SCREAMING_SNAKE` | entities.yaml `conventions.enum_style` | Không phải mã: đó là tên quy ước đặt tên ("SCREAMING_SNAKE cho error code") |
| `H_S1`, `H_AN1`, `H_AN2` | fixture a, README | Không phải mã: tên **hash tượng trưng** theo quy ước `{symbolic, computed_by}` |
| `F_2503` | fixture g | Không phải mã: `source_fingerprint` tượng trưng của `work_version` |

**Đúng một** mã lỗi chưa đăng ký trong toàn bộ phạm vi PC02, và nó đã được thay. Không mã nào
khác cần đăng ký thêm.

## F4. I16 / I17

Kiểm theo yêu cầu packet: văn bản I16 ("Attempt không bao giờ là kết quả") và I17 ("Merge
identity không làm đổi bất kỳ snapshot lịch sử nào") trong `invariants.md` **không thay đổi**
và nhất quán với mọi `invariant_refs` trong `entities.yaml` (I16 ở `analysis_attempt` và
`TXN-analysis-accept`; I17 ở `TXN-identity-merge`, `TXN-save-target`,
`referential_integrity.historical_snapshot_rule`). **Không sửa gì.**

Một quan sát để Coordinator biết: `precode/baseline.json` ghi "I16+ chỉ khi có decision
record". `invariants.md` mang một khối `**Justification**` cho mỗi invariant mới, đúng vai trò
đó, nhưng **chưa có mục I16/I17 trong `precode/decision-register.md`**. Việc đăng ký thuộc W1;
đây là ghi nhận, không phải defect của PC02 — **CR-PC02-19** đề nghị W1 xác nhận.

## F5. Hash

| Path | Before | Bytes | After | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `4d93232f02adcf7d74747f758e74af2c90e703909ea19072c5f2c3ee0031176b` | 216429 | `bdce5fc122d69cd35b8635cfdfab0066b01ff1aa90b4834896c68bf806fc7891` | 217143 |

`identity.md`, `invariants.md` và 15 fixture identity: **không đổi** (quét không tìm thấy mã
nào cần sửa ở đó).

⚠️ **`entities.yaml` ĐANG ĐƯỢC PIN BỞI TASK CARD.** `agent-tasks/` có **18** card pin hash
`4d93232f…`: TC-analysis-adapter-validation, TC-analysis-once-per-generation,
TC-backfill-pending-ledger, TC-backup-restore-drill, TC-canonical-identity-merge,
TC-collector-checkpoint-resume, TC-embedding-generation-switch, TC-ingest-idempotent-ack-lost,
TC-owner-auth-session, TC-report-coverage-publish-cas, TC-saved-snapshot,
TC-scheduler-lease-claim, TC-storage-write-blocked-readiness, TC-telegram-linking-auth,
TC-telegram-unknown-delivery, TC-ui-reports-detail, TC-ui-runs-three-states,
TC-x-feasibility-probe. Hash mới `bdce5fc122d69cd35b8635cfdfab0066b01ff1aa90b4834896c68bf806fc7891` làm **mọi pin đó lệch**. PC10 (chủ sở hữu
`agent-tasks/`) phải cập nhật — **CR-PC02-20**. Thay đổi là thuần văn xuôi + hai trường
metadata, không đổi cột/khóa/enum nào, nên không consumer nào phải sửa logic; nhưng pin là pin.

## F6. Evidence

Chạy 2026-09-07T01:13:01Z → 01:13:07Z:

| Script | Exit | Kết quả |
| --- | --- | --- |
| `verify_pc02.py` (6 gate) | **0** | `PASS (0 fail)` — 60 entity, 8 transaction, 37 target object, 47 tên bảng tham chiếu |
| `check_actor_edges.py` | **0** | 60 token ↔ 60 entity, diff rỗng hai chiều |
| `fixture_field_gate.py` (R4-01, 7 thư mục) | **0** | 0 unresolved; recovery nay 13 file/151 cột (W2 đã thêm rows) |
| `check_refs_pc01.py` | **0** | mọi MOD id / operation id tồn tại |

## F7. Kết thúc

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC02-e7` nhả lúc
2026-09-07T01:16Z. Không lệnh git mutation, không network, không file ngoài grant, không `__pycache__`.

---

# ADDENDUM — PKT-PC02-FIX7 (cột còn thiếu + chuẩn hóa token văn xuôi)

## G1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX7` · authority `AUTH-COORD-PC02-FIX7` · lease `LEASE-PC02-e8` (fencing 8) |
| worker principal | `worker-W3` · expires_at 2026-09-07T18:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T01:40Z |

`date -u` = 2026-09-07T01:33:42Z (trong hạn). SRC-SPEC `d35e1f2d…`, SRC-PLAN `f65bb046…` khớp
baseline §2. `contracts/ports.yaml` = `d4dd6e34…` đúng bản packet nêu.

## G2. Cột đã thêm (8)

| Entity | Cột | Kiểu / nullable | Căn cứ |
| --- | --- | --- | --- |
| `run` | `rate_limited_at` | timestamp_utc_ms, nullable | Đặt tại **T-RUN-25** (`running/collecting` --source_rate_limited--> `running/enriching`, `stop_reason = rate_limited`) của `contracts/state/run.yaml` (PC03-FIX3). Mốc chẩn đoán, KHÔNG phải trạng thái |
| `report` | `selection_version` | string, nullable + CHECK | NOT NULL khi `status = 'published'` (`ck_report_selection_version_published`). Nguồn: `contracts/reporting/selection.md`, có mặt trong `contracts/schemas/report.schema.json` |
| `report` | `created_at`, `updated_at` | timestamp_utc_ms, NOT NULL | `created_at` cấp tại T-RP-01 cùng `report_build_id`; `updated_at` của report đã publish bằng `published_at` (I05) |
| `delivery` | `created_at`, `updated_at` | timestamp_utc_ms, NOT NULL | `created_at` là **mốc gốc** của `telegram_send_max_window` (21600 s) trong `contracts/retry-policy.yaml` — thiếu cột này thì budget đó không tính được |
| `delivery_part` | `created_at`, `updated_at` | timestamp_utc_ms, NOT NULL | Backoff theo `retry-policy.yaml` cần mốc lần đổi trạng thái |
| `tag` | `updated_at` | timestamp_utc_ms, NOT NULL | `contracts/ui/screens.yaml` §UC-02: gửi kèm khi sửa, lệch ⇒ `CONFLICT`, hiện diff. (`tag.created_at` đã có từ PKT-PC02) |
| `worker_registration` | `last_run_at` | timestamp_utc_ms, nullable | Giá trị **hiển thị** "last run" của REQ-D11/REQ-D12. Ghi rõ tại chỗ: **chỉ để xem, KHÔNG dùng làm mốc lọc dữ liệu**; coverage authoritative là `coverage_window` (B04). Đây là cột của WORKER, không phải của `run` — đúng ruling |

Cũng thêm một CHECK: `ck_report_selection_version_published`.

## G3. Gỡ nhắc lịch sử `SAVE_ALREADY_EXISTS`

Ghi chú `saved_item.concurrency.error_code_note_vi` viết lại thành nguyên tắc chung ("cấm tạo
mã cục bộ chỉ tồn tại trong văn xuôi của một file") mà **không nêu tên mã cũ**. Lịch sử ở
addendum PKT-PC02-FIX6 §F2–F3. Đếm `SAVE_ALREADY_EXISTS` trong toàn bộ file PC02: **0**.

## G4. E0-04b / E0-04c — quét token `<a>.<b>` trong văn xuôi

Lệnh tái lập được: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 prose_token_gate.py`

Kết quả cuối: **47** token giải thành operation (E0-04b), **178** token giải thành
`entity.column` (E0-04c), **0 không giải được**. Negative self-test (bắt buộc theo ruling):
hai token đột biến `ingest.submit_batch_MUTATED` và `post.x_post_id_MUTATED` đều **BỊ BẮT**.

Lần chạy đầu có 24 token không giải được. Phân loại và xử lý:

| Loại | Ví dụ | Xử lý |
| --- | --- | --- |
| Alias văn xuôi của một cột | `predecessor.window_to`, `winner.id`, `receipt.checkpoint_id` | **Viết lại thành dạng đủ điều kiện**: `coverage_window.window_to` của cửa sổ liền trước, `work.id` của work thắng, `ingest_receipt.checkpoint_id` |
| Đường dẫn mục trong file | `limits.max_text_bytes`, `tables.purged`, `moved_counts.first_announced`, `enums.item_state` | **Viết lại** thành "mục X → khóa Y" hoặc gắn tên entity: `identity_merge_audit.moved_counts` khóa `first_announced` |
| Artifact của regex | `service.data_owner_of` (đuôi của `MOD-identity-service`), `target.schema` (trong `target.schema.json`), `dx.doi` (trong URL) | **Tinh chỉnh gate**: bỏ qua token đứng sau `-` `/` `.` hoặc theo sau bởi `.` |
| Tên operation đã bị bãi bỏ | `post.mark_source_deleted` | **Viết lại** không dùng token; tên nằm trong handoff, không nằm trong hợp đồng |

Cùng lớp lỗi đó lộ ra một điểm mù trong `check_refs_pc01.py`: nó coi `report.schema` (tiền tố
của `contracts/schemas/report.schema.json`) là một operation vì `report` là một domain hợp lệ.
Đã thêm quy tắc "token là tiền tố của đường dẫn dài hơn thì không phải operation" — sửa gate,
không sửa nội dung.

## G5. Hash

| Path | Before | Bytes | After | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `bdce5fc122d69cd35b8635cfdfab0066b01ff1aa90b4834896c68bf806fc7891` | 217143 | `c2ceeafd1b78705941f368bfe73f67cf097ffad8179c7455b2d4eeda571b5a1e` | 221041 |
| `contracts/data/identity.md` | `01976cabe4dae4e587cb0e555ca6a0176c5726c0815207bb04287cb5d1169571` | 20518 | `62fd06635c5e29a955f40cc1d56bea9d4dde9d444607fe7c07da5164993468ce` | 20576 |
| `contracts/data/invariants.md` | `134bf9f27b36ab624416809af76bf6059aa05db83cdcdb254a7277d41705fb64` | 27693 | `9def66cd6e918077a96a730327646c0040acd02a6a4c29135b28e5281e64b36d` | 27782 |

⚠️ **`entities.yaml` CARD-PINNED — hash mới `c2ceeafd1b78705941f368bfe73f67cf097ffad8179c7455b2d4eeda571b5a1e`.** Hiện có **18** card trong
`agent-tasks/` pin hash cũ `bdce5fc1…`. Ruling FIX7 đã dự liệu: W7 re-pin thành
`PC10-PIN-FCW4d-20260907` sau khi W2/W3/W5 land. Thay đổi lần này **có thêm cột**, khác FIX6
(thuần văn xuôi): consumer đọc `report`, `run`, `delivery`, `delivery_part`, `tag`,
`worker_registration` nên đọc lại. Không cột nào bị đổi tên hay xóa — thuần additive.

## G6. Evidence

Chạy 2026-09-07T01:37:09Z → 01:37:15Z:

| Script | Exit | Kết quả |
| --- | --- | --- |
| `verify_pc02.py` (6 gate) | **0** | `PASS (0 fail)` — 60 entity, 8 transaction, 47 tên bảng tham chiếu |
| `check_actor_edges.py` | **0** | 60 token ↔ 60 entity, diff rỗng hai chiều |
| `fixture_field_gate.py` (R4-01, 7 thư mục) | **0** | 0 unresolved |
| `check_refs_pc01.py` | **0** | 17 operation id dùng, tất cả tồn tại trong ports.yaml `d4dd6e34…` |
| `prose_token_gate.py` (E0-04b/04c) | **0** | 47 op + 178 column giải được, 0 vi phạm, 2/2 negative self-test bị bắt |

## G7. Kết thúc

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC02-e8` nhả lúc
2026-09-07T01:40Z. Không lệnh git mutation, không network, không file ngoài grant, không `__pycache__`.

---

# ADDENDUM — PKT-PC02-FIX8 (E0-04c: tên operation đã bãi bỏ trong văn xuôi schema)

## H1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX8` · authority `AUTH-COORD-PC02-FIX8` · lease `LEASE-PC02-e9` (fencing 9) |
| worker principal | `worker-W3` · expires_at 2026-09-07T18:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T01:52Z |

`date -u` = 2026-09-07T01:48:51Z (trong hạn); SRC-SPEC `d35e1f2d…`, SRC-PLAN `f65bb046…` khớp baseline §2.

## H2. Delta

E0-04c (run E0-20260907T014517Z) bắt `post.mark_source_deleted` trong
`contracts/schemas/ingest-batch.schema.json` → `x-contract.source_deletion_note`. Đây là tên
một operation **đã bị bãi bỏ** ở PKT-PC02-FIX1, viết dưới dạng token `<a>.<b>` nên gate đọc
thành `entity.column` và không giải được.

Viết lại `source_deletion_note` để nói **điều được phép** thay vì nhắc **điều đã bị bỏ**:
quan sát xóa nguồn đi qua `ingest.submit_batch` dưới dạng trường `source_deleted_observed_at`
của item (§defs/ingest_item); item trùng `x_post_id` vào `posts_duplicate` và cập nhật đơn
điệu `post.source_deleted_observed_at`; trỏ tới
`contracts/data/entities.yaml` §entities/post/immutability/monotonic_fields và
§transactions/TXN-ingest-batch. Câu cuối ghi rõ tên operation từng được cân nhắc rồi bãi bỏ
**nằm trong handoff, không nằm trong hợp đồng** — cùng nguyên tắc FIX6/FIX7 đã áp cho
`SAVE_ALREADY_EXISTS`. Mô tả của chính trường `source_deleted_observed_at` cũng được chỉnh
cho nhất quán. Đếm `post.mark_source_deleted` trong file: **0**.

Trong lần chạy gate ngay sau đó, chính câu mới của tôi lại sinh một token `.ingest_item`;
đã đổi sang `§defs/ingest_item` cho khớp kiểu đường dẫn dùng ở FIX7. Gate bắt được lỗi tôi vừa
tạo — đó là lý do nó tồn tại.

## H3. Hash

| Path | Before | Bytes | After | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/schemas/ingest-batch.schema.json` | `01c4d01346d32f165bc9c98060675adb524350ddf76507c888ffd3cd7bdf71f9` | 13564 | `3c00a33a20da6600e9db10f971d3b646390107201b1800678247e2b7a85d90fc` | 15400 |

`contracts/data/*` và `contracts/schemas/target.schema.json`: **không đổi** (nằm trong grant
nhưng gate không tìm thấy vi phạm nào ở đó).

⚠️ Card-pin: `agent-tasks/` có **2** card pin hash cũ của `ingest-batch.schema.json`.
Thay đổi thuần văn xuôi trong `x-contract` — không đổi `properties`, `required`, `$defs` hay
bất kỳ ràng buộc validate nào — nên không consumer nào phải sửa logic; nhưng pin vẫn cần
refresh cùng đợt `PC10-PIN-FCW4d-20260907` của W7.

## H4. Evidence

| Script | Exit | Kết quả |
| --- | --- | --- |
| `prose_token_gate.py` trên **5 file PC02** (`contracts/data/*` + hai schema) | **0** | **50** token → operation, **180** token → `entity.column`, **0 không giải được**; 2/2 negative self-test bị bắt |
| `verify_pc02.py` (6 gate) | **0** | `PASS (0 fail)` |
| `jsonschema.Draft202012Validator.check_schema` | — | ingest-batch.schema.json hợp lệ sau khi sửa |

Lệnh tái lập được:
`cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 prose_token_gate.py contracts/data/entities.yaml contracts/data/identity.md contracts/data/invariants.md contracts/schemas/target.schema.json contracts/schemas/ingest-batch.schema.json`

## H5. Kết thúc

Lease `LEASE-PC02-e9` nhả lúc 2026-09-07T01:52Z. Không lệnh git mutation, không network, không
file ngoài grant, không `__pycache__`.

---

# ADDENDUM — PKT-PC02-FIX9 (Owner ratification → CONTRACT_READY)

## I1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX9` · authority `AUTH-COORD-PC02-FIX9` (parent **`AUTH-OWNER-20260907-02`**) · lease `LEASE-PC02-e10` (fencing 10) |
| worker principal | `worker-W3` · expires_at 2026-09-08T00:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE_WITH_CONCERNS** · completion_claim **`CONTRACT_READY`** trong phạm vi "Data and identity" |
| ratification | `OD-20260907-01`, evidence_ref: Claude Code session `session_017QmDJtMqD9o1z79waqSB9W`, 2026-09-07 |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T04:22Z |

`date -u` = 2026-09-07T04:15:18Z (trong hạn); SRC-SPEC `d35e1f2d…`, SRC-PLAN `f65bb046…` khớp baseline §2.

Đây là lần đầu một file của PC02 vượt `DRAFT_FOR_REVIEW`. Căn cứ: A2-R4 tuyên bố phạm vi
"Data and identity" đủ điều kiện, và Owner đã phê chuẩn B01–B17 từng mục.

## I2. Delta

**1. Header trên 6 file** → `status: accepted`, `ratification_ref: OD-20260907-01`,
`claim_ceiling: CONTRACT_READY`. YAML top-level cho `entities.yaml`; front-matter cho
`identity.md`, `invariants.md`, `acceptance/fixtures/identity/README.md`; `x-contract` cho hai
JSON schema.

**2. Mục `ratification` mới trong `entities.yaml`** ghi lại: 8 mục đã được phê chuẩn (B08 timezone
`Asia/Ho_Chi_Minh`, B01 tag freeze, B05, B06, B07, B15, backfill N=7, phạm vi purge), 1 giá trị
`ACCEPTED_WORKING_VALUE`, 8 mục vẫn `PROVISIONAL`, 2 mục vẫn `KC`.

**3. `TXN-purge-all`: danh sách loại trừ đã được quyết định.** Mục
`excluded_pending_owner_decision` (19 bảng, `OWNER_DECISION_REQUIRED`) được thay bằng
`retained_by_owner_decision` (**20 bảng**, `status: ACCEPTED`, `decision_ref: OD-20260907-01`),
mỗi bảng có lý do riêng: `owner`, `session`, `secret_ref`, `task_credential`, `secret_audit`,
`telegram_link`, `telegram_link_code`, `provider_config`, `provider_test_result`, `settings`,
`schedule_occurrence`, `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version`,
`source_connection`, `backup_snapshot`, `backup_manifest`, `restore_record`, `purge_challenge`.
Thêm `backup_artifacts_rule`: artifact backup KHÔNG bị đụng, và hộp thoại xác nhận **phải nói
thẳng** rằng dữ liệu vừa xóa vẫn còn trong backup — xóa khỏi backup là thao tác riêng của PC08.
Oracle bổ sung: mọi bảng trong danh sách giữ lại có số hàng KHÔNG đổi; `#session` không đổi ⇒
owner vẫn đăng nhập được ngay sau khi xóa. `OWNER_DECISION_REQUIRED` không còn xuất hiện như
một trạng thái mở trong file.

**4. PROVISIONAL → ACCEPTED**, nhưng **chỉ ở nơi Owner thực sự đã quyết định**:

| Mục | Trạng thái mới | Căn cứ |
| --- | --- | --- |
| B08 timezone `Asia/Ho_Chi_Minh` | **ACCEPTED** | OD mục 4 |
| B01 tag freeze tại publish transaction | **ACCEPTED** | OD mục 5, AMD-B01 |
| backfill N = 7 ngày | **ACCEPTED** | OD mục 20, REQ-OQ04 |
| analysis key không gồm provider/model | **ACCEPTED** | OD mục 11, AMD-B07 |
| `limits.ingest_batch_max_items` = 200 | **ACCEPTED_WORKING_VALUE** | OD mục 20 (REQ-OQ05) — Owner chấp nhận làm giá trị làm việc, còn phải đo lại sau M0 |

## I3. Điều tôi KHÔNG nâng lên ACCEPTED (và vì sao)

Bảy giới hạn còn lại (`ingest_item_max_text_bytes`, `ingest_batch_max_payload_bytes`,
`ingest_item_max_media_refs`, `ingest_item_max_referenced_links`,
`ingest_thread_context_max_posts`, `identity_merge_max_moved_rows`,
`saved_snapshot_max_payload_bytes`) và retention 30 ngày của `telegram_link_attempt` **giữ
`PROVISIONAL`**, mỗi mục mang `ratification_note_vi` nói rõ lý do.

Chúng do PC02 tự đề xuất (CR-PC02-04, -05, -17) và **không nằm trong buổi phê chuẩn** — bản ghi
OD-20260907-01 liệt kê những gì Owner được hỏi, và bảy con số này không có trong đó. Đánh dấu
chúng ACCEPTED chỉ vì packet nói "PROV wording → ACCEPTED where it appears" sẽ là khai rằng
Owner đã duyệt một con số họ chưa từng thấy. **CR-PC02-22** đề nghị đưa chúng vào lần hỏi kế
tiếp; chúng không chặn `CONTRACT_READY` vì đều có giá trị, đơn vị và lý do (baseline §3 "no vagueness").

## I4. Mục còn `KC` trong phạm vi (packet yêu cầu nêu từng mục)

| Mục | Vì sao vẫn KC | Có chặn CONTRACT_READY không |
| --- | --- | --- |
| `entities[provider_config].terms_doc_ref` | REQ-A5: điều khoản của từng nhà AI chưa được đọc (Pre-code không có mạng) | **Không.** Đây là điều kiện RUNTIME, không phải khoảng trống hợp đồng: CHECK `ck_provider_config_terms_before_enable` giữ mọi adapter ở `enabled = false` cho tới khi có người đọc thật |
| `identity.md` §9 non-goals (fuzzy title merge, author+year merge, OCR, undo merge) | KC **theo thiết kế**: cần dữ liệu có nhãn để đánh giá | **Không.** Chúng là non-goal đã tuyên bố, không phải quyết định còn thiếu |

## I5. Hash sau

| Path | sha256 | Bytes |
| --- | --- | --- |
| `contracts/data/entities.yaml` | `2bc84950415b7f9813194d2cad4e8abe8759903690be708292d173eb6d019d36` | 227851 |
| `contracts/data/identity.md` | `71fedc7f6996f5eebace1a53ec42b19bb16f0df4489d93a906e5c895bbb4f4fd` | 20610 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `contracts/schemas/target.schema.json` | `e6bdcf9e4dc4c6217ab0f79ffa0cf0664084bce012b92e6c8fcc2d6731a0c235` | 8372 |
| `contracts/schemas/ingest-batch.schema.json` | `872cc3b4a6326b1016da995c92d5a13e88cfdc86efa1e57be25a164d9ff5abc7` | 15443 |
| `acceptance/fixtures/identity/README.md` | `015ad8695d0df6cede410585fb4061d2d065ad1207b6af9a19ab6e880a49e785` | 11403 |

⚠️ **Card-pin: 18 card** trong `agent-tasks/` pin hash cũ của `entities.yaml` /
`ingest-batch.schema.json` / `target.schema.json`. Lần này thay đổi **không thêm/bớt cột nào** —
chỉ header, mục `ratification`, và danh sách purge đã quyết định — nhưng card cũng pin
`claim_ceiling`, nên W7 cần re-pin trong đợt `PC10-PIN-FCW4d-20260907`. Đáng chú ý: OD mục 3
đổi stack sang **B (Python worker + TypeScript web)**, nên 18 card còn phải viết lại §3 paths và
§8 build/test — việc đó thuộc W7, không thuộc packet này.

## I6. Evidence

Chạy 2026-09-07T04:18:19Z → 04:18:26Z:

| Script | Exit | Kết quả |
| --- | --- | --- |
| `verify_pc02.py` (6 gate) | **0** | `RESULT: PASS (0 fail)` — 60 entity, 8 transaction |
| `check_actor_edges.py` | **0** | 60 token ↔ 60 entity, diff rỗng hai chiều |
| `fixture_field_gate.py` (R4-01, 7 thư mục) | **0** | 0 unresolved |
| `check_refs_pc01.py` | **0** | mọi MOD id / operation id tồn tại |
| `prose_token_gate.py` (5 file PC02) | **0** | 51 op + 180 column, 0 vi phạm, 2/2 negative self-test bị bắt |

Hai lần sửa gate trong gói này, cả hai là sửa **gate**, không phải nội dung: (a)
`verify_pc02.py` hard-code `claim_ceiling == "DRAFT_FOR_REVIEW"` nên chính việc nâng ceiling làm
nó fail — nay chấp nhận cả `CONTRACT_READY`; (b) mục `ratification` mới của tôi sinh token
`limits.ingest_*` mà E0-04c đọc thành `entity.column` — đã viết lại thành `limits → …`.

## I7. Điều `CONTRACT_READY` này KHÔNG khẳng định

Theo SRC-PLAN §2: nhãn chỉ nói **bộ hợp đồng đủ trường, không còn quyết định chặn, ví dụ hợp lệ
và bất hợp lệ đã được kiểm**. Nó **không** nói code chạy được, không nói SQLite thực thi được
các ràng buộc mô tả (partial index, generated column, CHECK — vẫn chưa ai chạy thử), và không
nói "0 trùng" đúng ngoài phạm vi canonical identity đã biết (B15). Mọi bằng chứng vẫn là E0
`SELF_VALIDATION`; E1–E4 vẫn `NOT_RUN`.

## I8. Kết thúc

Lease `LEASE-PC02-e10` nhả lúc 2026-09-07T04:22Z. Không lệnh git mutation, không network, không
file ngoài grant, không `__pycache__`.

---

# ADDENDUM — PKT-PC02-FIX10 (F-A2R5-04/-05: ceiling của fixture và tuyên bố NOT_RUN)

## J1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX10` · authority `AUTH-OWNER-20260907-02` (OD-20260907-01) · lease `LEASE-PC02-e11` (fencing 11) |
| worker principal | `worker-W3` · expires_at 2026-09-08T04:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `CONTRACT_READY` (phạm vi "Data and identity") |
| findings | F-A2R5-04, F-A2R5-05 → `FIX_PROPOSED` |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T05:12Z |

`date -u` = 2026-09-07T05:05:13Z (trong hạn); nguồn khớp baseline §2.

## J2. Delta (a) — 14 fixture identity lên CONTRACT_READY

Trước gói này README của thư mục claim `CONTRACT_READY` còn 14 file nó lập chỉ mục vẫn ở
`DRAFT_FOR_REVIEW` — đúng chỗ F-A2R5-04 gọi là "hai file đứng trên mọi file chúng lập chỉ mục".
Ruling: fixture của hai thư mục đã phê chuẩn là **oracle chấp nhận** của chính phạm vi đó.

Mỗi file nay mang một khối **`x-contract`** (không phải khóa rời rạc) gồm:
`status: accepted` · `ratification_ref: OD-20260907-01` · `claim_ceiling: CONTRACT_READY` ·
`eligibility_scope` · `runtime_evidence: NOT_RUN` · `runtime_evidence_note_vi`.

Khóa `claim_ceiling` rời ở cấp gốc đã được **gỡ** và chuyển vào `x-contract`. Lý do: F-A2R5-03
đòi `ratification_ref` phải đọc được từ **header hợp đồng đã khai** chứ không phải từ văn xuôi
hay một khóa rải rác; giữ hai chỗ cùng nói về ceiling là mời gọi chúng lệch nhau. README §2 và
§1b được cập nhật theo hình dạng mới.

## J3. Delta (b) — tuyên bố NOT_RUN trên hai schema

`target.schema.json` và `ingest-batch.schema.json` nhận `x-contract.runtime_evidence: NOT_RUN`
cùng câu giải thích: E1–E4 chưa chạy, chưa có code, **SQLite chưa từng được yêu cầu ép** các
ràng buộc mô tả (partial index, generated column, CHECK); `CONTRACT_READY` chỉ nói bộ hợp đồng
đủ trường và đã kiểm ví dụ hợp lệ/bất hợp lệ ở mức E0. Cùng câu đó nằm trong 14 fixture.

## J4. Delta phát sinh — quét E0-04c lần đầu trên fixture identity

Các lần chạy prose gate trước chỉ phủ 5 file hợp đồng, chưa phủ fixture. Lần này phủ cả 20
file và tìm thấy **23** token `<a>.<b>` chưa giải được, cùng lớp với F-A2R5 — không cái nào là
cột bịa: `given.rows` / `expected.rows` / `expected.hash_oracles` /
`expected_violation.json_pointer` (cấu trúc fixture), `conventions.hashes` (đường dẫn mục), và
một `post.mark_source_deleted` sót lại trong `forbidden_effects` của fixture (e). Tất cả đã
viết lại thành dạng không mơ hồ; **0 còn lại**.

## J5. Hash sau

| Path | sha256 | Bytes |
| --- | --- | --- |
| `acceptance/fixtures/identity/README.md` | `ce9ec21ec1cebe8a257a677e67097f1883a35c403b4421d3219862d185335e14` | 12611 |
| `contracts/schemas/target.schema.json` | `d1ce487d2e4ba24b094f702b38a5fcac517443981fe8faea36472089124dc0fd` | 8915 |
| `contracts/schemas/ingest-batch.schema.json` | `8ab444f557645ee85dbd0951af7261ac4355d3a0b8ca6b96d8450c9e1a5ae690` | 15986 |

14 file JSON trong `acceptance/fixtures/identity/` đều đổi; hash đầy đủ lấy bằng
`sha256sum acceptance/fixtures/identity/*.json`. Kiểm tự động: cả 14 file có `x-contract` với
đủ ba trường `claim_ceiling=CONTRACT_READY`, `ratification_ref=OD-20260907-01`,
`runtime_evidence=NOT_RUN`.

⚠️ Card-pin: **9** card trong `agent-tasks/` pin hash cũ của hai schema. W7 re-pin trong đợt
`PC10-PIN-OD01c-20260907`.

## J6. Evidence

Chạy 2026-09-07T05:08:00Z → 05:08:08Z: `verify_pc02.py` **0** · `fixture_field_gate.py` **0**
(7 thư mục, 0 unresolved) · `check_actor_edges.py` **0** (60 ↔ 60) · `check_refs_pc01.py` **0** ·
`prose_token_gate.py` trên **20 file PC02** **0** (78 op + 198 column, 0 vi phạm, 2/2 negative
self-test bị bắt).

## J7. Kết thúc

Lease `LEASE-PC02-e11` nhả lúc 2026-09-07T05:12Z. Không lệnh git mutation, không network, không
file ngoài grant, không `__pycache__`.

---

# ADDENDUM — PKT-PC02-FIX11 (tập bảng purge có thẩm quyền + header fixture)

## K1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX11` · authority `AUTH-COORD-PC02-FIX11` (parent `AUTH-OWNER-20260907-02`) · lease `LEASE-PC02-e12` (fencing 12) |
| worker principal | `worker-W3` · expires_at 2026-09-08T04:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `CONTRACT_READY` (data and identity) |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T05:16Z |

`date -u` = 2026-09-07T05:09:44Z (trong hạn); nguồn khớp baseline §2.

## K2. (1) Ba tập bảng của `TXN-purge-all`

Defect CR-PC05-06: `schedule_occurrence` từng nằm ở **cả hai** tập, còn
`worker_registration` và `data_deletion_audit` bị xếp vào purged — mâu thuẫn với mục 20/23 đã
phê chuẩn (giữ lịch; bản ghi xóa giữ vĩnh viễn).

Mục `tables` được viết lại thành ba tập có thẩm quyền, kèm `set_authority_vi` và `counts`:

| Tập | Số bảng | Ghi chú |
| --- | --- | --- |
| `purged` | **37** | 36 bảng của ruling **+ `telegram_link_attempt`** — ruling nêu nó purged trong văn xuôi nhưng thiếu trong danh sách; correction 06:05Z của Coordinator (CR-PC05-07) xác nhận 37. Tôi đã dùng 37 từ đầu vì văn xuôi ruling nói rõ, và ghi `telegram_link_attempt_note_vi` tại chỗ |
| `retained_by_owner_decision` | **21** | 20 bảng cũ **+ `worker_registration`** với lý do được nêu: đăng ký collector và ràng buộc token là **cấu hình**, không chứa dữ liệu nghiên cứu; xóa sẽ buộc đăng ký lại collector |
| `never_purged` | **2** | `schema_migration` và **`data_deletion_audit`** (bản ghi xóa giữ vĩnh viễn theo tham số PC08 đã phê chuẩn; chính thao tác purge ghi một hàng audit vào đây) |

`schedule_occurrence` nay chỉ nằm ở `retained`. Tổng **37 + 21 + 2 = 60 = toàn bộ entity**.

Đối chiếu tự động với file ruling đã sửa: tập `purged` của entities.yaml **khớp từng phần tử**
(`ruling − mine = ∅`, `mine − ruling = ∅`).

## K3. EV-PC02-08 — phủ kín và rời nhau

Thêm vào `verify_pc02.py` một assertion đọc thẳng ba tập từ entities.yaml:

```text
INFO  purged=37 retained=21 never=2 tổng=60 | entities=60
PASS  phủ kín: mọi entity thuộc đúng một trong ba tập
PASS  không có tên lạ trong ba tập
PASS  purged ∩ retained = ∅
PASS  purged ∩ never_purged = ∅
PASS  retained ∩ never_purged = ∅
PASS  tổng ba tập = số entity = 60
```

Đây là oracle bắt được đúng lớp lỗi CR-PC05-06: một bảng nằm ở hai tập, hoặc một entity không
nằm ở tập nào, đều làm gate FAIL. Trước gói này không gate nào kiểm điều đó.

## K4. (2) Header của 14 fixture identity

Coordinator cho chọn: hoàn thiện `x-contract` hoặc chuyển lên top-level, oracle ràng buộc là
`E0-08 = 0` và E0-12b giải được ref. Tôi **hoàn thiện `x-contract`** với đủ **14 trường bắt
buộc** của baseline §3 (`contract_id`, `version`, `status`, `owner_role`, `source_refs`,
`requirement_refs`, `decision_refs`, `invariant_refs`, `producers`, `consumers`,
`dependencies`, `scope`, `verification`, `claim_ceiling`) cộng `ratification_ref`,
`eligibility_scope`, `runtime_evidence`.

Lý do chọn nhánh này: trước đó 14 fixture chỉ pass E0-08 nhờ **fallback "README có liệt kê
file"**. Nay mỗi file tự mang header đầy đủ, nên nó pass **bằng chính nội dung của nó** —
không phụ thuộc một file khác vẫn liệt kê đúng tên nó.

## K5. (3) `screens.yaml` trích tập đã sửa

`ACT-purge-all.scope_authority` nay nêu **37 / 21 / 2** và nói rõ ba tập rời nhau, phủ kín 60
entity, kiểm bởi EV-PC02-08. `confirmation_dialog` lên **bốn khối nội dung**: thêm
`never_purged_vi` (phiên bản schema + nhật ký xóa giữ vĩnh viễn). `retained_vi` nêu đích danh
`schedule_occurrence` và `worker_registration` kèm hệ quả "xóa sẽ buộc đăng ký lại collector".
`deleted_vi` ghi "37 bảng" và bổ sung sổ quét lại kho, nhật ký gọi nguồn. `forbidden_vi` đổi
"ba khối" → "bốn khối".

## K6. Hash sau

| Path | sha256 | Bytes |
| --- | --- | --- |
| `contracts/data/entities.yaml` | `766fe760bf487781a0b75f070d21960d84d52bccff0465fdaac65dd6ad140ce7` | `228394` |
| `contracts/ui/screens.yaml` | `e1a57407c0733aa709b464b61da3313f0f6109f5696bd8b39b7e77fc5d5d9074` | `51212` |
| `acceptance/fixtures/identity/README.md` | `ce9ec21ec1cebe8a257a677e67097f1883a35c403b4421d3219862d185335e14` | `12611` |

14 file JSON identity đều đổi (header đầy đủ); hash lấy bằng
`sha256sum acceptance/fixtures/identity/*.json`.

⚠️ Card-pin: **18** card pin hash cũ của `entities.yaml` / `screens.yaml`; W7 re-pin trong
đợt `PC10-PIN-OD01c-20260907`.

## K7. Evidence

Chạy 2026-09-07T05:12:37Z → 05:12:49Z, tất cả **exit 0**:

| Gate | Kết quả |
| --- | --- |
| `verify_pc02.py` (7 gate, gồm **EV-PC02-08** mới) | `PASS (0 fail)` |
| `verify_pc07.py` (5 gate) | `PASS (0 fail)` |
| `fixture_field_gate.py` (R4-01, 7 thư mục) | 0 unresolved |
| `check_actor_edges_all.py` | PASS |
| `check_refs_pc01.py` | PASS |
| `prose_token_gate.py` (20 file PC02 + screens.yaml) | 135 op + 229 column, 0 vi phạm |
| **`evidence/tools/e0_check.py`** (gate chính thức) | **23/23 PASS, 0 FAIL** — gồm `E0-08-contract-header` 142/0, `E0-12b-ratification-refs` 50/0, `E0-12-forbidden-strings` 713/0, `E0-04c` 215/0, `E0-14` 455/0 |

## K8. Kết thúc

Lease `LEASE-PC02-e12` nhả lúc 2026-09-07T05:16Z. Không lệnh git mutation, không network, không
file ngoài grant, không `__pycache__`.

---

# ADDENDUM — PKT-PC02-FIX12 (F-A3R1-02/-06: `ENT-owner` nhận cột credential và lockout)

## L1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX12` · authority `AUTH-COORD-PC02-FIX12` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-PC02-e13` (fencing 13) |
| worker principal | `worker-W3n` (kế nhiệm `worker-W3`) · expires_at 2026-09-08T16:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `CONTRACT_READY` (data and identity) — **cần A3-R2 xác minh lại** |
| ruling nguồn | `FIX-A3R1-rulings.md` hàng `F-A3R1-02` (HIGH); phục vụ cả `F-A3R1-06` (MEDIUM) và dọn đường cho `F-A3R1-01` |
| next actor | Coordinator → WS (sinh lại `shared/rr_contracts`) → WA (migration + test) · `lease_released_at` 2026-09-07T11:12Z |

`date -u` lúc bắt đầu = 2026-09-07T11:04:29Z, lúc kết thúc = 2026-09-07T11:09:25Z (trong hạn lease).
Nguồn khớp baseline §2: plan `f65bb046…40`, spec `d35e1f2d…6e`.

## L2. Delta (1) — `contracts/data/entities.yaml`

`ENT-owner` nhận **đúng bốn** trường, chèn sau `created_at`; **không một byte nào** của năm trường cũ,
của `keys`, hay của `unique_constraint_semantics` bị đụng tới:

| Trường | Kiểu | Nullable | Điểm cốt lõi của `constraints` |
| --- | --- | --- | --- |
| `password_hash` | `string` | có | Chuỗi encoded Argon2id (dạng PHC, đã gồm salt + tham số) theo `secrets.md` §2.2. NULL = **chưa** bootstrap, không phải mật khẩu rỗng ⇒ `auth.login` trả `UNAUTHORIZED`. **KHÔNG BAO GIỜ** được trả bởi bất kỳ read model nào |
| `password_updated_at` | `timestamp_utc_ms` | có | Mốc đổi mật khẩu gần nhất; đổi mật khẩu thu hồi MỌI session (`secrets.md` §2.3) |
| `failed_login_count` | `integer` | **không** | `DEFAULT 0`; đăng nhập đúng đặt lại 0; ngưỡng 5 lần / 15 phút |
| `locked_until` | `timestamp_utc_ms` | có | NULL = không khóa; khóa 15 phút ⇒ `RATE_LIMITED` kèm `retry_after`, không tiết lộ tài khoản tồn tại hay không |

Ba thay đổi đi kèm trong cùng file:

1. `version` **0.1.0 → 0.2.0**. Luật: `change-control.md` §2 hàng "thêm trường optional" = minor; và
   mục 4 của chính file này liệt kê "cột nullable, hoặc cột NOT NULL kèm DEFAULT hằng số" là additive.
   Không cột nào đổi ngữ nghĩa cột cũ, thu hẹp enum hay đổi khóa ⇒ **không** phải major.
2. Mục mới **`0b. Amendment sau phê chuẩn`** với khối `AMD-ENT-owner-01`: before/after nguyên văn,
   `decision_refs: [CR-TC-AUTH-02, CR-TC-AUTH-03]`, `finding_refs: [F-A3R1-02, F-A3R1-06]`,
   `status: PROVISIONAL`, khối `ratification` ghi rõ đây là **amendment kỹ thuật của Coordinator**
   (`AUTH-COORD-PC02-FIX12`, cha `AUTH-OWNER-20260907-03`) và Owner **có thể phản đối**.
3. `decision_refs` của header thêm `AMD-ENT-owner-01`, `CR-TC-AUTH-02`, `CR-TC-AUTH-03`.
   `ENT-owner` thêm `amendment_refs: [AMD-ENT-owner-01]` và hai dòng `non_goals` mới.

**`claim_ceiling` giữ nguyên `CONTRACT_READY`** — phạm vi "Data and identity" mà `OD-20260907-01` §4
phê chuẩn không bị thu hẹp. Nhưng khối amendment ghi thẳng rằng nội dung đã đổi **sau** lượt xác minh
A2-R4, nên **A3-R2 PHẢI xác minh lại `ENT-owner` trên epoch mới**: nhãn hiện hành được cấp bởi một lượt
audit chưa từng thấy bốn cột này.

## L3. Delta (2) — `precode/change-control.md`

Thêm §10 "Sổ CR đã áp dụng" với một khối CR đúng **chín trường** của §1
(`cr_id`, `raised_by`, `addressed_to`, `status`, `source_of_change`, `before`, `after`, `reason`,
`affected`, `migration`). `CR-TC-AUTH-02` và `CR-TC-AUTH-03` được xét như **một impact set** theo §6 —
cùng một entity, cùng một file hợp đồng, cùng một migration; tách ra là tạo hai vòng xin phép cho cùng
một phạm vi, đúng điều §6 cấm. `before` trích nguyên văn năm trường cũ (luật 1 của §1); `after` đủ cụ
thể để Owner trả lời có/không (luật 2). `affected` liệt kê: `entities.yaml` (0.1.0 → 0.2.0),
`shared/rr_contracts` (sinh lại), hai revision migration, và luật card: **mọi card pin hash
`entities.yaml` ⇒ `STALE`** (§4, INV-06/INV-09). Version file 0.1.0 → **0.1.1** (patch — thêm bản ghi,
không đổi quy trình; đây là luật §2 của chính file, packet không yêu cầu, tôi ghi ra để không lặng lẽ
đổi nội dung mà giữ nguyên version).

## L4. Delta (3) — `precode/decision-register.md`

Thêm §8.11 "Amendment kỹ thuật của Coordinator sau audit A3-R1", một bảng **một dòng** cho
`AMD-ENT-owner-01`, dùng đúng năm cột của §8.5 (`ID | Gói | Quyết định | Trạng thái | Đưa lên Owner ở
mục`). Trạng thái ghi **`PROVISIONAL`**, đưa lên Owner ở mục **Vận hành và bảo mật**. Hai đoạn kèm theo
nói rõ vì sao Coordinator ký được (amendment làm hợp đồng khớp với `secrets.md` mà Owner **đã** chấp
nhận qua `PROV-PC08-01` — không thêm quyết định sản phẩm mới, đúng loại việc mà `change-control.md` §7
giao cho ruling của Coordinator) và **ba điều nó không làm**: không mang nhãn `ACCEPTED (OD-20260907-01)`,
không đóng `F-A3R1-02`/`F-A3R1-06`, không nâng trần claim. Version 0.1.0 → **0.1.1** (cùng lý do §L3).

Vì sao đặt ở §8 chứ không ở §3: §3 chỉ chứa `AMD-B<nn>` sửa **câu chữ của đặc tả nguồn**, và cả mười
sáu mục ở đó đã `ACCEPTED (OD-20260907-01)`. `AMD-ENT-owner-01` không sửa một câu nào của spec — nó vá
một khoảng trống của hợp đồng — và nó **chưa** được Owner phê chuẩn. Trộn nó vào §3 sẽ làm một dòng
`PROVISIONAL` trông như đã được phê chuẩn cùng mười sáu dòng kia.

## L5. Điều tôi KHÔNG chạm (packet cấm, và tôi đã kiểm)

`server/migrations/**`, `server/app/**`, `shared/rr_contracts/**`, `agent-tasks/**`,
`acceptance/fixtures/**` — không file nào bị ghi. `git status --porcelain` sau khi làm chỉ khác trước
khi làm ở đúng ba đường dẫn của packet cộng file handoff này. Không lệnh git mutation, không network,
`PYTHONDONTWRITEBYTECODE=1`, không `__pycache__` nào ngoài `.venv/` (đã kiểm bằng `find … -not -path
"*/.venv/*"` → rỗng). Mọi script chạy từ `…/scratchpad/w3n/`, không script nào nằm trong repo.

## L6. Hash sau

| Path | sha256 | Bytes | Trước |
| --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `f5ea0511f885159fedbb48bf939a9bd1436707f12007403c57808c9f5026c77e` | `235547` | `766fe760…0ce7` / 228394 |
| `precode/change-control.md` | `f0634166dd0c192063ffeb08a65329cc28b2d22655e42e1cadc49f69cbe29fcb` | `21545` | `5cc1e461…6468` / 15847 |
| `precode/decision-register.md` | `56cd624f3d6a429888018abea9fb67e9dbe26aa6d202630c50ff8f989102c06d` | `117150` | `4d1a5d6e…7244` / 114327 |

Nguồn không đổi: `research-radar-pre-code-plan.md` `f65bb046…7f40`, `research-radar-spec.md`
`d35e1f2d…e0e26`.

⚠️ **Card-pin.** `entities.yaml` bị pin bởi **18** task card và `decision-register.md` bởi **18** card;
cả hai hash cũ cũng nằm trong `evidence/index.json`, `precode/baseline.json` và bốn evidence run E1 của
đợt Giai đoạn 1. Theo `change-control.md` §4, **các card đó nay `STALE`** — chạy lại, không phải FAIL.
Re-pin là việc của WP/PC10 (`PC10-PIN-…`), không phải của tôi. ⚠️ `entities.yaml` còn là **nguồn của bộ
sinh**: `shared/rr_contracts` phải được WS sinh lại trước khi WA dùng bốn cột này.

## L7. Evidence — `EV-PC02-09` (SELF_VALIDATION)

Chạy 2026-09-07T11:08Z–11:09Z từ `…/scratchpad/w3n/`, `PYTHONDONTWRITEBYTECODE=1`:

| Gate | Lệnh | Kết quả | exit |
| --- | --- | --- | --- |
| `verify_pc02.py` (EV-PC02-01…08) | `python3 verify_pc02.py` | **PASS (0 fail)** — YAML parse 60 entity, target schema, tập purge 37/21/2 phủ kín 60 | 0 |
| fixture-field (R4-01) | `python3 fixture_field_gate.py` | **PASS** — 7 thư mục, 1667 cột kiểm, 0 chưa giải | 0 |
| actor-edge | `python3 check_actor_edges_all.py` | **PASS (0 fail)** — 300 sự kiện | 0 |
| prose-token (E0-04b/04c) | `python3 prose_token_gate.py` | **PASS** — 52 operation + 178 entity.column giải được, **0 chưa giải**; negative self-test bắt đúng 2 token đột biến | 0 |
| ref PC01 | `python3 check_refs_pc01.py` | **PASS (0 fail)** | 0 |
| **`evidence/tools/e0_check.py`** (gate chính thức, read-only) | `python3 /mnt/virtual/repo/xcrawl/evidence/tools/e0_check.py` | **24/24 PASS · FAIL 0 · BLOCKED 0 · violations 0** | 0 |

Chi tiết đáng ghi của lượt E0: `E0-04c-prose-column-tokens` 215/0 (bốn cột mới nay là đích hợp lệ cho
token dạng `owner.password_hash`), `E0-08-contract-header` 143/0, `E0-12-forbidden-strings` 743/0 (khối
amendment mang `PROVISIONAL`, **không** mang từ vựng đã phê chuẩn), `E0-12b-ratification-refs` 50/0,
`E0-15-fixture-field-existence` 1964/0.

**Một lỗi thật do gate bắt được, đã sửa trước khi kết thúc.** Bản nháp đầu của khối amendment viết
`additive_only_rules.allowed_without_major_bump` trong văn xuôi; gate prose-token đọc nó như
`entity.column` và không giải được ⇒ FAIL. Tôi **không** nới gate: tôi viết lại câu thành "danh sách
`allowed_without_major_bump` (mục 4, khóa `additive_only_rules`)". Gate xanh lại vì văn bản đúng, không
vì oracle bị hạ.

**`E0-19-generated-matches`: KHÔNG TỒN TẠI.** Packet dự liệu rằng nếu có, nó sẽ FAIL cho tới khi WS sinh
lại `shared/rr_contracts`. `grep -n "E0-19" evidence/tools/e0_check.py` trả về **0 dòng** và tổng số
check là 24, không phải 25. Vậy nên: **không** có FAIL nào để báo, và cũng **không** có gate máy nào
hiện đang canh việc model sinh khớp `entities.yaml`. Tôi ghi điều đó ra như một khoảng trống, không như
một lượt PASS: nghĩa vụ sinh lại của WS lúc này chỉ được canh bằng ruling và bằng test hợp đồng
`tests/contract/test_schema_matches_entities.py` mà WA sẽ viết, chứ chưa có E0 nào bắt được nếu ai đó
quên. Tôi **không** tự sinh lại — ngoài write set của packet.

## L8. Chưa giải quyết và giới hạn

- `AMD-ENT-owner-01` là **PROVISIONAL**. Owner phải được trình ở vòng kế tiếp (mục **Vận hành và bảo
  mật**) và có thể phản đối; nếu phản đối, bốn cột bị gỡ và đó sẽ là thay đổi **major** kèm migration
  thật, vì cột đã mang dữ liệu.
- Gói này **không** đóng `F-A3R1-02` hay `F-A3R1-06`. Nó chỉ dựng chỗ chứa ở tầng hợp đồng. `F-A3R1-06`
  chỉ thực sự hết khi WA ghi `failed_login_count`/`locked_until` **trong cùng transaction** đăng nhập và
  chứng minh bằng test sống sót qua restart. `F-A3R1-01` cần WM + WA hội tụ `CREATE TABLE owner`.
- `entities.yaml` vẫn **không** khai entity nào cho *lịch sử* từng lần đăng nhập. Ruling chỉ yêu cầu
  trạng thái lockout hiện hành; tôi không phát minh bảng mới. Nếu sau này cần nhật ký đăng nhập, đó là
  một CR khác.
- Tự kiểm, không phải audit độc lập: mọi kết quả ở §L7 mang nhãn `SELF_VALIDATION`. Không có E1–E4 nào
  trong gói này.

## L9. Kết thúc

Lease `LEASE-PC02-e13` (fencing 13) nhả lúc **2026-09-07T11:12Z**. Sau dòng này tôi không ghi thêm file
nào, kể cả sửa lỗi đánh máy — sửa tiếp cần packet mới, baseline mới, lease mới.

---

# ADDENDUM — PKT-PC02-FIX13 (F-A3R2-01/-04: sửa căn cứ version và đường xuống code)

## M1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX13` · authority `AUTH-COORD-PC02-FIX13` (cha `AUTH-OWNER-20260907-03`) · lease `LEASE-PC02-e14` (fencing 14) |
| worker principal | `worker-W3n` · expires_at 2026-09-08T16:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `CONTRACT_READY` (data and identity) |
| trigger | `A3-R2-report.md` `F-A3R2-01` (MEDIUM) và `F-A3R2-04` (LOW) — cả hai nhắm vào **văn xuôi** của bản sửa FIX12, không vào bốn cột |
| MODIFY grant | `contracts/data/entities.yaml` (chỉ văn xuôi trong khối amendment), `precode/change-control.md` |
| next actor | Coordinator (→ WP re-pin: hash hai file đã đổi) · `lease_released_at` 2026-09-07T11:44Z |

`date -u` 11:36Z → 11:40Z, trong hạn. Nguồn khớp baseline §2 (`f65bb046…`, `d35e1f2d…`).

## M2. Điều KHÔNG đổi (kiểm bằng máy, không bằng lời)

`version: 0.2.0` của `entities.yaml` **giữ nguyên** theo ruling; **không** trường nào của `ENT-owner`
bị thêm, bớt hay sửa. Xác nhận sau khi sửa: `yaml.safe_load` cho `version = 0.2.0`, 60 entity, và
danh sách trường của `owner` vẫn đúng chín tên theo thứ tự cũ. Chỉ văn xuôi trong `amendments[0]` đổi.
Vì sao ruling giữ 0.2.0 mà tôi không tự nâng lên 1.0.0: bump lần nữa làm mọi card **vừa** re-pin
`STALE` thêm một vòng, để sửa một **lỗi trích dẫn** — thay đổi thực chất của schema không đổi một byte.

## M3. `F-A3R2-01` — căn cứ bậc version, viết lại theo luật CÓ THẬT

Auditor đúng và tôi đã kiểm lại độc lập: `grep -rn "allowed_without_major_bump\|additive_only_rules"
precode/` trả về **0 dòng**. Hai tên đó là khóa của **mục 4 trong chính `entities.yaml`**; câu cũ viết
"(mục 4, khóa …)" ngay sau khi dẫn `precode/change-control.md` §2, nên đọc ra thành một luật của file
quy trình — một luật không tồn tại. Đó là lỗi của tôi, không phải cách đọc khắt khe.

`version_rule_vi` nay dẫn **nguyên văn** cả bốn hàng của §2 và nói rõ hàng nào phủ cái gì:

| Cột | Hàng §2 phủ nó | Kết luận |
| --- | --- | --- |
| `password_hash`, `password_updated_at`, `locked_until` (nullable) | "Thêm trường **optional**, thêm mã lỗi mới, thêm operation mới \| minor" | minor, đúng nguyên văn |
| `failed_login_count` (NOT NULL, DEFAULT 0) | **không hàng nào** | khoảng trống |

Ba hàng còn lại được kiểm từng cái chứ không bỏ qua: major thứ nhất là "Đổi/**xóa** trường bắt buộc,
đổi enum, đổi ngữ nghĩa, đổi `auth_scope`, đổi `idempotency` key, đổi commit point" — đây là **thêm**
một trường mới, không phải đổi hay xóa một trường bắt buộc đang tồn tại; major thứ hai là "Đổi
`transaction` / `commit_point` / invariant" — không mục nào bị đụng; patch là "sửa lỗi chính tả, làm rõ
prose, không đổi hành vi" — quá nhẹ cho một cột mới.

Vậy §2 **không cho phép và cũng không cấm**: nó có một khoảng trống. Tôi chọn nhánh thứ hai của ruling
và khai thẳng, ở CẢ HAI file:

- `entities.yaml` `amendments[0]`: `deviation_from` (§2, nêu đúng khoảng trống), `deviation_authority`
  `AUTH-COORD-PC02-FIX13`, `deviation_parent_authority` `AUTH-OWNER-20260907-03`,
  `deviation_change_request` `CR-PC10-13`, cộng `deviation_note_vi` nói vì sao không bump lại.
- `change-control.md` §10: khối `version_rule` (bốn hàng nguyên văn) và khối `deviation` cùng nội dung.

Cột NOT NULL được xử lý là additive **trên căn cứ `migration`, không trên căn cứ một hàng quy tắc**:
DEFAULT hằng số, không backfill, đúng một hàng `owner` đang tồn tại nhận 0, không consumer nào đang đọc
một cột chưa từng có. Mục 4 của `entities.yaml` nói đúng điều đó ở tầng schema — nhưng nó là luật của
file đó, và trong bản mới tôi ghi thẳng rằng nó **không** tự cấp quyền chọn bậc version.

**`CR-PC10-13` (mới, `OPEN`)** ghi ở §10 của `change-control.md` theo đúng định dạng chín trường của §1:
PC10 thêm cho §2 một hàng cho "thêm trường bắt buộc kèm DEFAULT hằng số" — hoặc tuyên bố nó là major và
nói lý do; điều quan trọng là §2 phải **trả lời**. Id `CR-PC10-13` còn trống (`CR-PC10-01…12` đã dùng).
`migration` của CR ghi rõ: khi §2 có hàng mới, khối `deviation` được thay bằng trích dẫn hàng đó, và
`entities.yaml` **giữ nguyên** 0.2.0 — bậc version không đổi, chỉ căn cứ đổi.

## M4. `F-A3R2-04` — `entities.yaml` KHÔNG phải nguồn của bộ sinh

Kiểm lại độc lập, không tin lời ai: `contracts/data/entities.yaml` xuất hiện **0 lần** trong
`shared/rr_contracts/rr_contracts/generated/GENERATED_FROM.json` (15 nguồn: bảy schema JSON, năm state
machine, `errors.yaml`, `ports.yaml`, `openapi.yaml`) và **0 lần** trong `web/src/generated/GENERATED_FROM.json`
(một nguồn: `openapi.yaml`). `shared/rr_contracts/generate.py` dòng ~44–49 nói thẳng rằng một amendment
với entity — **gọi đích danh `AMD-ENT-owner-01`** — "correctly produces **no diff** here", và ghi rằng
việc mở rộng bộ sinh là `CR-P0-06`, ngoài phạm vi.

Vậy câu "phải sinh lại" của tôi ở FIX12 mô tả một bước **không tồn tại**. Đã sửa ở hai chỗ:

| Chỗ | Trước | Sau |
| --- | --- | --- |
| `entities.yaml` `amendments[0].downstream_vi` | "`shared/rr_contracts` (model sinh) phải sinh lại; …" | đường xuống code là **đúng hai** nhánh viết tay: DDL trong revision Alembic base `0002_base_entities` (nơi DUY NHẤT tạo `owner`) và `tests/contract/test_schema_matches_entities.py`; nêu `CR-P0-06` và hệ quả "hợp đồng ↔ migration chỉ được chứng minh **gián tiếp**" |
| `change-control.md` §10 `affected` | `generated: [shared/rr_contracts]` "PHẢI sinh lại (chủ: WS)" | `generated: []` + khóa mới `reaches_code_through` liệt kê đúng hai file trên; đoạn kết viết lại và thêm một đoạn nêu số nguồn của cả hai manifest |
| `entities.yaml` `not_claimed_vi[0]` | "… đó là việc của WS (sinh lại) và WA (test)" | "… do revision Alembic base và test hợp đồng chứng minh; sinh lại KHÔNG phải một bước ở đây (F-A3R2-04, CR-P0-06)" |

Điều đáng ghi cho người đọc sau, và là lý do finding này không "vô hại": nếu hai file hợp đồng cứ khai
một phụ thuộc mà manifest bộ sinh phủ nhận, thì một ngày nào đó ai đó sẽ tin rằng cây model sinh bám
theo `entities.yaml` và bỏ qua test hợp đồng — đúng cái test đang gánh toàn bộ chứng minh.

## M5. Hash sau

| Path | sha256 | Bytes | Trước (FIX12) |
| --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `df5e023124a910d7c6c022d3b69d190e7534db8f64b8d2f1dfdde2b1db7d142f` | `239261` | `f5ea0511…6c77e` / 235547 |
| `precode/change-control.md` | `0427d5620500e0209cf3a9bbe383f65deba641266cad54e8b21c628b069b8270` | `26992` | `f0634166…9fcb` / 21545 |

`precode/decision-register.md` **không** nằm trong grant lần này và **không** bị chạm: vẫn
`56cd624f…2c06d`. Version: `entities.yaml` giữ **0.2.0** (ruling); `change-control.md` 0.1.1 → **0.1.2**
(hàng patch của §2 nguyên văn "Sửa lỗi chính tả, làm rõ prose, không đổi hành vi" — mục §10 là bản ghi,
sửa nó không đổi một quy tắc nào; ghi ra để không lặng lẽ đổi nội dung mà giữ version).

⚠️ **Card re-pin lần nữa.** Hash `entities.yaml` đã đổi so với bản mà WP vừa pin sau FIX12. 18 card
pin file này ⇒ `STALE` thêm một vòng. Packet đã lường trước ("hash will move, card re-pin will follow").

## M6. Evidence — `EV-PC02-10` (SELF_VALIDATION)

Chạy 2026-09-07T11:38Z–11:40Z từ `…/scratchpad/w3n/`, `PYTHONDONTWRITEBYTECODE=1`, tất cả exit 0:

| Gate | Kết quả |
| --- | --- |
| `verify_pc02.py` (EV-PC02-01…08) | **PASS (0 fail)** — 60 entity, tập purge 37/21/2 phủ kín |
| fixture-field / actor-edge / ref PC01 (chạy trong `verify_pc02.py`) | **PASS (0 fail)** |
| `prose_token_gate.py` | **PASS** — 0 token chưa giải; negative self-test bắt đúng 2 token đột biến |
| **`evidence/tools/e0_check.py`** | **25/25 PASS · FAIL 0 · BLOCKED 0 · violations 0** |

**`E0-19-generated-matches` NAY ĐÃ TỒN TẠI và PASS (18 kiểm, 0 vi phạm).** Ở FIX12 tôi báo nó không tồn
tại (24 check) và ghi đó là một khoảng trống. Chủ skeleton đã thêm nó; tổng nay là 25. Điều nó khẳng
định lại đúng là điều `F-A3R2-04` nói: `entities.yaml` **cố ý** vắng mặt khỏi cả hai manifest bộ sinh
(`CR-P0-06`), nên không có gì để sinh lại và không có diff nào để chờ. Nói cách khác, gate chính thức
nay đứng về phía bản sửa này chứ không phải bản FIX12.

## M7. Chưa giải quyết

- `CR-PC10-13` **OPEN** — PC10 phải trả lời khoảng trống của §2. Tới lúc đó bậc version của
  `AMD-ENT-owner-01` là một **deviation có thẩm quyền**, không phải một suy diễn từ luật.
- `AMD-ENT-owner-01` vẫn **PROVISIONAL**; Owner có thể phản đối, và khi đó card `TC-owner-auth-session`
  cùng verdict A3-R2 của nó mở lại (chính auditor đã viết điều này).
- Gói này **không** đóng `F-A3R2-01` hay `F-A3R2-04`, cũng không đụng `F-A3R2-02` (guard dùng
  `table_info` bỏ sót cột generated — của WA) và `F-A3R2-03` (ba manifest E1 cũ — của các card).
- Tự kiểm, không phải audit độc lập: mọi kết quả §M6 mang nhãn `SELF_VALIDATION`.

## M8. Kết thúc

Lease `LEASE-PC02-e14` (fencing 14) nhả lúc **2026-09-07T11:44Z**. Không lệnh git mutation, không
network, không file ngoài grant, không `__pycache__` ngoài `.venv/`. Sau dòng này tôi không ghi thêm.

---

# ADDENDUM — PKT-PC02-FIX14 (`OD-20260907-03`: AMD-ENT-owner-01 PROVISIONAL → ACCEPTED)

## N1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX14` · authority `AUTH-COORD-PC02-FIX14` (cha **`AUTH-OWNER-20260907-04`**) · lease `LEASE-PC02-e15` (fencing 15) |
| worker principal | `worker-W3n` · expires_at 2026-09-08T20:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `CONTRACT_READY` (data and identity) |
| trigger | Biên bản Owner `OD-20260907-03` mục 1 — phê chuẩn `AMD-ENT-owner-01` |
| MODIFY grant | `contracts/data/entities.yaml` (chỉ khối amendment), `precode/change-control.md` |
| next actor | Coordinator · `lease_released_at` 2026-09-07T13:27Z |

`date -u` = 2026-09-07T13:24:00Z, trong hạn. Nguồn khớp baseline §2 (`f65bb046…`, `d35e1f2d…`).

## N2. Tôi đã kiểm biên bản trước khi viết `ACCEPTED`

Không nhận nhãn phê chuẩn từ lời của packet. Đọc thẳng
`…/scratchpad/packets/OWNER-DECISIONS-20260907-03.md`: `decision_id: OD-20260907-03`, issuer là Owner
(chỉ thị nguyên văn "accept both, start phase 2" sau một báo cáo nêu **đích danh hai mục**
`AMD-ENT-owner-01` và `PROV-PC00-08`), evidence `session_0156UBBHDSeC9soECzSVUb3U`, authority mới
`AUTH-OWNER-20260907-04`. Hàng 1 của biên bản nói đúng điều packet giao: PROVISIONAL → ACCEPTED, và
`entities.yaml` **giữ** `CONTRACT_READY`. Nếu biên bản không nêu đích danh amendment này, tôi đã dừng —
viết `ACCEPTED` cho một mục Owner chưa từng thấy là khai man, và luật đó không đổi khi packet nói ngược.

## N3. Delta (1) — `contracts/data/entities.yaml`, chỉ khối `amendments[0]`

| Trước | Sau |
| --- | --- |
| `status: PROVISIONAL` | `status: ACCEPTED` + `ratified_by: OD-20260907-03` + `ratified_at: "2026-09-07"` |
| `ratification.owner_disclosure_vi` — "Phải trình Owner ở vòng quyết định kế tiếp. Owner CÓ THỂ phản đối; nếu phản đối thì bốn cột bị gỡ…" | `ratification.owner_decision_vi` — ĐÃ trình, ĐÃ phê chuẩn: biên bản, authority, evidence, và hệ quả (bốn cột đứng trên quyết định của Owner; nhãn của card `TC-owner-auth-session` không còn tựa vào hợp đồng PROVISIONAL) |
| — | `ratification.history_vi` (mới) — giữ nguyên văn điều kiện cũ và mốc thời gian nó có hiệu lực |

**Không** trường nào của `ENT-owner` bị thêm/bớt/sửa; `version` giữ **0.2.0**; `claim_ceiling` giữ
`CONTRACT_READY`; **`ratification_ref` top-level giữ `OD-20260907-01`** — nó là căn cứ của trần claim
cho phạm vi "Data and identity", không phải của amendment này, và đổi nó sẽ làm `E0-12b` mất neo.
Kiểm sau khi sửa bằng `yaml.safe_load`: `version 0.2.0`, 60 entity, `owner` vẫn đúng chín trường theo
thứ tự cũ, `amendments[0].status = ACCEPTED`, `ratified_by = OD-20260907-03`.

**Vì sao giữ lịch sử thay vì xóa mệnh đề "có thể phản đối".** Packet nói "drop the clause (keep
history)" và tôi hiểu đúng nghĩa đó: mệnh đề ấy **có thật** từ 11:12Z tới biên bản vòng ba; nó hết
hiệu lực vì Owner **đã trả lời**, không vì nó bất tiện. Một sổ hợp đồng mà điều kiện biến mất khi được
thỏa mãn thì không đọc được ngược. `history_vi` cũng ghi rõ `OD-20260907-01` **vẫn** không nhắc bốn cột
— thẩm quyền là `OD-20260907-03` — để không ai sau này gán nhầm cho biên bản vòng một.

## N4. Delta (2) — `precode/change-control.md` §10

`status: PROVISIONAL` → `status: ACCEPTED` kèm `ratified_by: OD-20260907-03` trong khối CR
`CR-TC-AUTH-02`; đoạn "Thẩm quyền và giới hạn" nhận một đoạn cập nhật ghi biên bản, authority, evidence
và **giữ nguyên văn câu cũ** làm lịch sử. Thêm một đoạn "hai điều biên bản vòng ba KHÔNG làm": nó
**không** đóng `F-A3R1-02`/`F-A3R1-06`, và nó **không** trả lời `CR-PC10-13` — khoảng trống §2 vẫn còn
nên khối `deviation` vẫn là căn cứ bậc version. Version file 0.1.2 → **0.1.3** (hàng patch §2 nguyên
văn "Sửa lỗi chính tả, làm rõ prose, không đổi hành vi"; ghi ra để không lặng lẽ đổi nội dung).

## N5. Hash sau

| Path | sha256 | Bytes | Trước (FIX13) |
| --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `c61be0a4f8dc5884e82bf1ed79c86f0c38da3d0f6aa41e96205c1089f900a4fc` | `240224` | `df5e0231…d142f` / 239261 |
| `precode/change-control.md` | `21688b458b1ce8f2c6687e3d99b750efbae0bf5ead4414b991b02f8633b17ef0` | `28321` | `0427d562…8270` / 26992 |

⚠️ Card-pin: hash `entities.yaml` đổi lần thứ ba; 18 card pin file này ⇒ `STALE`. Packet đã lường
trước (WP re-pin sau khi card Giai đoạn 2 được viết).

## N6. Evidence — `EV-PC02-11` (SELF_VALIDATION)

Chạy 2026-09-07T13:22Z–13:24Z từ `…/scratchpad/w3n/`, `PYTHONDONTWRITEBYTECODE=1`, exit 0:

| Gate | Kết quả |
| --- | --- |
| `verify_pc02.py` (EV-PC02-01…08, gồm fixture-field / actor-edge / ref PC01) | **PASS (0 fail)** |
| `prose_token_gate.py` | **PASS** — 0 token chưa giải |
| **`evidence/tools/e0_check.py`** (read-only) | **25/25 PASS · FAIL 0 · BLOCKED 0 · violations 0** |

Hai check đáng nêu đích danh vì chúng là thứ canh đúng lớp sai sót của gói này:
`E0-12-forbidden-strings` **1047 kiểm / 0 vi phạm** — từ vựng đã phê chuẩn chỉ được dùng ở nơi có
quyền dùng, và `status: ACCEPTED` mới của tôi nằm trong một file mang `ratification_ref` hợp lệ;
`E0-12b-ratification-refs` **50 / 0** — trần `CONTRACT_READY` vẫn neo vào `OD-20260907-01`, không bị
tôi vô tình chuyển sang biên bản vòng ba.

## N7. Kiểm chéo với PC00 — đã khớp, không còn mâu thuẫn

Trước khi nhả lease tôi kiểm `precode/decision-register.md` (ngoài grant, chỉ ĐỌC) vì §8.11 của nó là
nơi thứ hai ghi trạng thái của amendment này. Hash file đã đổi trong lúc tôi làm
(`56cd624f…2c06d` → `31fa401c2da52743b3d76d57ee6842ca80ffe04c46eac88ecb149e7f7dcf7d9f`): PC00 đã cập
nhật song song. Đọc nội dung: §8.11 nay ghi **`ACCEPTED (OD-20260907-03)`** kèm dòng lịch sử "trước đó
là `PROVISIONAL` dưới `AUTH-COORD-PC02-FIX12`", và §8 ghi `PROV-PC00-08` cũng `ACCEPTED (OD-20260907-03)`
— đúng cả hai mục của biên bản. Biên bản cũng đã có bản trong repo: `precode/owner-decisions-03.md`.
Vậy ba nơi (`entities.yaml`, `change-control.md` §10, `decision-register.md` §8.11) nay nói cùng một
trạng thái, và không cần CR nào. Tôi ghi lại việc kiểm này chứ không giả định: không gate nào so ba nơi
đó với nhau, nên "khớp" ở đây là kết quả của một lần đọc, không của một lần chạy máy.

Còn mở, không đổi bởi gói này: `CR-PC10-13` (khoảng trống §2) vẫn `OPEN`; `F-A3R1-02`, `F-A3R1-06`,
`F-A3R2-01…04` không mục nào bị đóng ở đây. Mọi kết quả §N6 là `SELF_VALIDATION`, không phải audit độc lập.

## N8. Kết thúc

Lease `LEASE-PC02-e15` (fencing 15) nhả lúc **2026-09-07T13:27Z**. Không lệnh git mutation, không
network, không file ngoài grant, không `__pycache__` ngoài `.venv/`. Sau dòng này tôi không ghi thêm.

---

# ADDENDUM — PKT-PC02-FIX16 + FIX17 (`AMD-ENT-maintenance-01` và lan truyền tập purge)

## O1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX16` (`AUTH-COORD-PC02-FIX16`, lease `LEASE-PC02-e20`) → `PKT-PC02-FIX17` (lease `LEASE-PC02-e21`) |
| worker principal | `worker-W3n` — chủ ghi duy nhất của `precode/` và `contracts/` ở đợt này |
| status | **DONE_WITH_CONCERNS** — hai gate FAIL có chủ đích, nêu ở §O6; không gate nào bị nới |
| trigger | `WIRING-wave-1.md` mục cuối (ruling G-3) + `CR-TC-storage-06` của WR |
| next actor | WR (migration tạo bảng) · PC01 (`CR-PC02-24`) · WS (sinh lại `shared/rr_contracts` + `web/src/generated`) · `lease_released_at` 2026-09-08T06:53Z |

## O2. FIX16 — entity `maintenance_window`

`contracts/state/storage.yaml` T-ST-03/-04/-09 nói ba lần rằng một hàng maintenance window ĐƯỢC
GHI; `entities.yaml` không khai bảng nào để ghi. WR dừng đúng ở `SG-EDGE` thay vì bịa bảng. Thêm
đúng một entity, `status: specified`, `owner_module: MOD-data-store`, 10 trường.

**Mỗi trường có một transition đứng sau — không trường nào "cho đủ":** `opened_at`/`opened_by` từ
T-ST-03 guard (hành động explicit của `backup_operator`); `reason` từ bốn mục đích của
T-ST-03/-04/-05 **cộng** `disk_cleanup` mà T-ST-09 guard nói đích danh ("dọn ổ, migrate,
restore"); `storage_health_at_open` từ chỗ T-ST-09 CẤM lách sang `healthy`; `closed_at`/`closed_by`
từ T-ST-04; `snapshot_verified_at` từ điều cấm "đóng cửa sổ khi verify chưa pass" — không có cột
đó, điều cấm chỉ ép được TRONG một tiến trình; `restore_record_id` từ T-ST-05.

**Danh sách trường là HỢP của hai đề xuất, và tôi nói rõ vì sao.** Ruling nêu bảy tên
(`closed_by`, `storage_health_at_open`, `restore_record_id` …); `CR-TC-storage-06` của WR nêu bảy
tên khác, trong đó có `snapshot_verified_at` mà ruling không nhắc. Tôi lấy HỢP chứ không lấy một
bên: mỗi trường của cả hai danh sách đều có một transition đòi nó, và bỏ `snapshot_verified_at`
sẽ để lại đúng lỗ hổng mà WR đã chỉ ra. Đây là chỗ tôi đi RỘNG hơn văn bản packet, nên ghi ra
thành một dòng thay vì để người đọc tự phát hiện.

Kèm theo: partial unique `ux_maintenance_window_open` trên `(owner_id) WHERE closed_at IS NULL`
("nhiều nhất một cửa sổ mở" — giả định mà T-ST-03/-09 dùng khi nói về *the* window) và ba CHECK,
trong đó `ck_maintenance_window_verify_before_close` ép điều cấm của T-ST-04 xuống tầng kho, chỉ
áp cho `reason = 'snapshot'` vì T-ST-04 guard nói rõ nhánh kia là "hoặc migration hoàn tất".

**Ba thứ entity này cố ý KHÔNG làm** (ghi trong `what_it_is_not_vi` và `non_goals`): không lưu
trạng thái storage health nói chung; không persist `write_blocked` (T-ST-01 và
`forbidden_transitions` hàng 4 cấm — nó phải suy ra từ một lần ghi hỏng thật, không đọc từ hàng
cũ); không thay `restore_record` cho `recovery_required` (một `restore_record` có
`dispatcher_unlocked_at IS NULL` ĐÃ là trạng thái đó trên đĩa).

Version `0.2.0 → 0.3.0`, `AMD-ENT-maintenance-01` `PROVISIONAL`, `deviation_from` §2 (khoảng
trống "thêm bảng mới" — **tái dùng `CR-PC10-13`**, cố ý không mở CR mới cho cùng một lỗ hổng).

## O3. FIX17 — lan truyền 21 → 22 và 60 → 61

Chín artefact, chỉ các dòng đếm / liệt kê tập, không một chữ nào khác:

| File | Sửa gì |
| --- | --- |
| `contracts/ports.yaml` | "60 entity" → 61; "giữ lại — 21 bảng" → 22 + thêm tên; "(37 xóa / 21 giữ / 2)" → 22 |
| `contracts/modules.yaml` | như trên (ba chỗ) |
| `contracts/http/openapi.yaml` | "GIỮ LẠI (21 bảng)" → 22 + thêm tên; "(37 xóa / 21 giữ / 2)" → 22 |
| `contracts/ops/secrets.md` | "60 entity" → 61; "giữ 21" → 22 + thêm tên |
| `contracts/ops/backup-restore.md` | như trên |
| `contracts/ui/screens.yaml` | "21 bảng giữ lại" → 22 (hai chỗ), "tổng 60" → 61 |
| `acceptance/scenarios.yaml` | năm chỗ đếm + danh sách liệt kê retained |
| `acceptance/fixtures/recovery/README.md` | "60 entity" → 61; "21 bảng retained" → 22 |
| `acceptance/fixtures/recovery/l-…json` | sáu chuỗi đếm **và** mảng `_retained_tables` (21 → 22 phần tử) |

**Một defect có sẵn, sửa nhân thể vì nó là đúng loại dòng:** `confirmation_dialog_must_state_vi`
của fixture `l` viết "**20** bảng cấu hình… được giữ" trong khi tập retained lúc đó là 21 — sai
từ trước đợt này, không phải do tôi. Nay là 22. Ghi ra để không ai đọc diff thành "W3n đổi 20
thành 22 cho khớp".

**Tôi KHÔNG bump version của chín file này.** Packet nói "change only the counts/set membership
lines and the sentence that enumerates retained tables — no other wording", và `openapi.yaml`
`info.version` là **phiên bản API mà consumer pin**, không phải một con số hành chính. §2 của
`change-control.md` đòi bump khi hợp đồng đổi; hai điều đó căng nhau ở đây. Tôi chọn theo packet
và báo cáo, thay vì tự quyết định bậc version cho sáu gói khác trong một packet chỉ để đồng bộ
con số. Coordinator ra phán quyết.

## O4. Hash sau (trước = bản tại `HEAD`; cả chín file FIX17 đều SẠCH tại `HEAD` trước khi tôi sửa, kiểm bằng `git diff --numstat` khớp đúng số dòng tôi đổi)

| Path | Trước | Sau | Bytes |
| --- | --- | --- | --- |
| `contracts/data/entities.yaml` | `ebcf460f…` | `7cd85e09431fa52555ee13bb5fb8f5a00932e38801677212e8baa18c14c27827` | 255475 |
| `precode/change-control.md` | `1203de29…` | `996471a02eda87c24a14069a7a5318f2d3fa672598359d8547a7d8a671261eb5` | 82441 |
| `precode/decision-register.md` | `a38e2ce1…` | `ab47a9adf997041655a0a571d62987d0f36e45cc04b2639d9f0d0c755e7fc7ed` | 188780 |
| `contracts/ports.yaml` | `c15b676b…` | `c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412` | 128872 |
| `contracts/modules.yaml` | `cf536acb…` | `d4434aaf632388457aacae512de3cf800af20ee1a015dcb290fcb04b857d9b02` | 108743 |
| `contracts/http/openapi.yaml` | `28b3820e…` | `a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d` | 231727 |
| `contracts/ops/secrets.md` | `14b3d898…` | `22f7a0075ada77c69dfce6b8b7d6e6b0af625317f2fc4c1be726abf5c3c391a5` | 25323 |
| `contracts/ops/backup-restore.md` | `826655da…` | `0e5f726fb4f5d381093763ccce9627849534a6009c2510ef43905f579d271c28` | 25880 |
| `contracts/ui/screens.yaml` | `e1a57407…` | `464579a807e00e44c3215cf9fbf243df4a2bef8db6e137d71a2409fe6bc6b854` | 51212 |
| `acceptance/scenarios.yaml` | `2eec5567…` | `cdef72be2a4fe38b2d989f4f3e8628e80d6d19b0547143a8a2a300ef9d6ae442` | 216794 |
| `acceptance/fixtures/recovery/README.md` | `982311e7…` | `f1de7368db67e6380b3c75d981edfeaddb4045f95b4d696c5a3b90f86e6298da` | 12235 |
| `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` | `9cd382e2…` | `321e56af0bea131276d193dc718b72f46fc118af8f3ff8406f3e08efb8aa0271` | 20814 |

## O5. Evidence — `EV-PC02-12` (SELF_VALIDATION)

| Gate | Kết quả |
| --- | --- |
| `verify_pc02.py` (EV-PC02-01…08) | **PASS (0 fail)** sau khi sửa token; EV-PC02-08 đọc ba tập mới: 37 / 22 / 2, phủ kín 61 |
| `prose_token_gate.py` | **PASS** — 0 token chưa giải |
| `check_actor_edges.py` (EV-PC02-06) | **FAIL (1)** — có chủ đích, xem §O6 |
| `evidence/tools/e0_check.py` | **26/27 PASS · FAIL 1 · violations 3** — `E0-19` có chủ đích, xem §O6. `E0-18-purge-set-agreement` **PASS**, ghi "purged 37 · retained 22 · never_purged 2 · union 61 of 61" |

**Một lỗi thật do gate bắt, đã sửa chứ không nới gate.** Bản nháp đầu viết token `storage.health`
sáu lần trong văn xuôi; gate đọc nó như `<entity>.<column>` hoặc một operation và không giải
được (`storage.get_health` mới là operation có thật). Tôi viết lại thành "trạng thái storage
health" ở cả sáu chỗ. Gate xanh lại vì văn bản đúng, không vì oracle bị hạ.

## O6. Hai FAIL có chủ đích — và một kỳ vọng của packet KHÔNG đúng

**(a) `E0-19-generated-matches`, 3 vi phạm.** `contracts/ports.yaml` và `contracts/http/openapi.yaml`
**là** nguồn của bộ sinh, nên sửa chúng làm `shared/rr_contracts/…/GENERATED_FROM.json` và
`web/src/generated/GENERATED_FROM.json` lệch hash. Sinh lại là việc của WS; `shared/` và `web/`
không nằm trong lease của tôi và tôi KHÔNG tự sinh. Đây là gate làm đúng việc của nó. (Khác với
`entities.yaml`, vốn cố ý không phải nguồn của bộ sinh — `CR-P0-06`.)

**(b) `check_actor_edges.py`: `['maintenance_window']` không có owner token trong `modules.yaml`.**
Ruling R-03 chia đôi việc này: PC02 đặt `owner_module` (đã làm, cộng một dòng ở mục 4b
`newly_owned_entities`), PC01 thêm token vào `data_owner_of`. `contracts/modules.yaml` **có**
trong lease FIX17 — nhưng chỉ cho "counts/set membership lines" của tập purge; `data_owner_of`
là một tập KHÁC. Tôi không lấn. `CR-PC02-24` ghi đầy đủ trong `change-control.md` §10.

**(c) Kỳ vọng "E0-18 sẽ flag các artefact" là SAI, và điều đó quan trọng.** `E0-18` **cố ý không**
so sánh liệt kê trong văn xuôi: comment trong `e0_check.py` ngay tại chỗ nói tác giả đã viết bản
đó trước, nó cho 24 vi phạm mà ~20 là dương tính giả, và "a noisy check is worse than no check";
giới hạn ấy được ghi ở `evidence/tools/README.md` §5g. `E0-18` chỉ kiểm (a) ba tập phân hoạch
đúng tập entity, và (b) không artefact nào còn đánh dấu phạm vi purge là chưa quyết. Nghĩa là
**`E0-18` sẽ PASS dù chín artefact kia còn ghi 21** — nó đã PASS như thế trước khi tôi sửa chúng.
Tôi tìm chín artefact bằng `grep` các chuỗi đếm ("21 bảng", "giữ 21", "60 entity", "(37 xóa / 21
giữ / 2)"), không bằng đầu ra của gate. Ai dựa vào `E0-18` để biết đã đồng bộ xong sẽ tin nhầm.

## O7. Chưa giải quyết

- `AMD-ENT-maintenance-01` là **PROVISIONAL**; Owner có thể phản đối.
- **`tests/contract/test_schema_matches_entities.py` sẽ ĐỎ** cho tới khi WR tạo bảng: entity đã
  khai, migration chưa có. Gate so hai chiều nên chiều này đỏ **đúng như mong muốn** — đó là thứ
  ép bảng được tạo thật thay vì để hợp đồng và kho nói hai chuyện khác nhau.
- `CR-TC-storage-04` (thiếu entity `storage_probe` cho `write_blocked → healthy`) **vẫn mở** —
  gói này không chạm.
- `CR-PC10-13` (khoảng trống §2) vẫn `OPEN`, nay đỡ hai amendment thay vì một.
- Bump version của chín artefact FIX17: **chưa làm**, chờ phán quyết (§O3).
- Mọi card pin `entities.yaml`, `ports.yaml`, `openapi.yaml`, `modules.yaml`, `screens.yaml`,
  `scenarios.yaml` hoặc fixture `l` nay `STALE`; WP re-pin sau khi WS sinh lại.

## O8. Kết thúc

Lease `LEASE-PC02-e20` và `LEASE-PC02-e21` nhả lúc **2026-09-08T06:53Z**. Không lệnh git
mutation, không network, không file ngoài grant, không `__pycache__` ngoài `.venv/`.

---

# ADDENDUM — PKT-PC02-FIX18 (ba ruling của Coordinator + `CR-PC02-24` đóng)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX18` · authority `AUTH-COORD-PC02-FIX18` · lease `LEASE-PC02-e22` |
| worker | `worker-W3n` · status **DONE_WITH_CONCERNS** (một FAIL còn lại, có chủ đích) |
| next actor | WS (sinh lại bộ model) → WP (re-pin) · `lease_released_at` 2026-09-08T07:05Z |

**Ruling 1 — tập trường rộng hơn: CHẤP NHẬN, và không phải deviation.** `snapshot_verified_at`
truy về `T-ST-04` `forbidden_vi`, `disk_cleanup` truy về `T-ST-09` guard; cả hai là phái sinh
đúng của state contract. Ghi ở `change-control.md` §10 ngay trong khối `CR-TC-storage-06`.
`entities.yaml` KHÔNG cần sửa: nó đã ghi việc này ở `fields_derivation_vi` và chưa từng gọi nó là
deviation — nên không có nhãn nào phải gỡ, và tôi không mở file đó ở lease này.

**Ruling 2 — không bump version chín artefact FIX17: CHẤP NHẬN, ghi thành deviation.**
`DEV-PC02-FIX17-01` trong `change-control.md`: chín file SAO CHÉP một tập đã có thẩm quyền ở
`entities.yaml`, và chính file đó đã mang bậc version của amendment; `openapi.yaml` `info.version`
là phiên bản wire mà consumer pin, và hình dạng wire không đổi. Deviation ghi rõ **giới hạn**: nó
chỉ áp cho lan truyền con số của một amendment đã version ở nguồn, KHÔNG phải tiền lệ cho việc
sửa nội dung hợp đồng mà giữ version; và hash chín file vẫn đổi nên §4 vẫn chạy — card vẫn STALE,
WP vẫn re-pin.

**Ruling 3 — `E0-18` không so sánh con số trong văn xuôi.** Ghi lại ở đây vì nó là bài học về
CÁCH ĐỌC một PASS, không chỉ một CR: `E0-18-purge-set-agreement` kiểm (a) ba tập phân hoạch đúng
tập entity và (b) không artefact nào còn đánh dấu phạm vi purge là chưa quyết. Nó **cố ý** không
so liệt kê trong văn xuôi — comment trong `e0_check.py` ghi rằng bản làm việc đó cho 24 vi phạm,
~20 dương tính giả, "a noisy check is worse than no check", và giới hạn nằm ở
`evidence/tools/README.md` §5g. Hệ quả thực tế ở FIX17: **E0-18 PASS trong suốt thời gian chín
artefact còn ghi "21 bảng giữ lại" và "60 entity"**. Chín file đó được tìm bằng `grep` các chuỗi
đếm ("21 bảng", "giữ 21", "60 entity", "(37 xóa / 21 giữ / 2)"), **không** bằng đầu ra của gate.
`CR-PC02-25` (mới, `OPEN`, gửi W6n/PC09) đề nghị mở rộng E0-18 sang chuỗi đếm — bài toán hẹp hơn
so-khớp-danh-sách nên không mang theo lớp dương tính giả cũ — và, rẻ hơn nhiều, in một dòng note
"prose counts NOT compared" ngay trong output của check để một PASS không bị đọc quá nghĩa.

**`CR-PC02-24` — ĐÓNG.** `contracts/modules.yaml` `MOD-data-store.data_owner_of` nay có
`maintenance_window`. `check_actor_edges.py` (EV-PC02-06): **PASS (0 fail)** — "owner_module khớp
trên mọi entity chung", "3 artifact token bị loại đúng". `verify_pc02.py`: **PASS (0 fail)** cả
bốn phần.

**Hash sau.** `contracts/modules.yaml` `d4434aaf…9b02` → `7a4e19bdbb43e1339f305cd4715f1e7ac704b09720408ccf1db48a01b23c1e25` (108912 B).
`precode/change-control.md` `996471a0…1eb5` → `7f755960cd3021a8675b7f645bfa7542fc1c931fd965589badad674f6bd915b2` (87870 B, 0.1.6 → 0.1.7).
`contracts/data/entities.yaml` **không đổi** (`7cd85e09…7827`) — ngoài lease này.

**Còn lại một FAIL, có chủ đích: `E0-19-generated-matches`, 3 vi phạm.** `contracts/ports.yaml`
và `contracts/http/openapi.yaml` là nguồn của bộ sinh; sửa chúng ở FIX17 làm hai
`GENERATED_FROM.json` lệch hash. Sinh lại là việc của WS — `shared/` và `web/` chưa bao giờ nằm
trong lease của tôi và tôi KHÔNG tự sinh. Gate đang làm đúng việc của nó, và nó sẽ còn đỏ cho tới
khi WS chạy. `modules.yaml` (sửa ở packet này) **không** phải nguồn của bộ sinh nên không thêm vi
phạm nào.

Lease `LEASE-PC02-e22` nhả 2026-09-08T07:05Z. Không git mutation, không network, không file ngoài
grant.

---

# ADDENDUM — PKT-PC02-FIX19 (`E0-18` leg đếm mới bắt sáu con số cũ)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC02-FIX19` · lease `LEASE-PC02-e23` · worker `worker-W3n` |
| status | **DONE** — `E0-18` từ 6 vi phạm về **0**; không vi phạm nào là dương tính giả |
| next actor | WP (re-pin) · `lease_released_at` 2026-09-09T07:26Z |

**Sáu vi phạm, sáu lỗi thật.** Không cái nào cần route sang W6n:

| # | Chỗ | Trước | Sau | Vì sao nó thoát khỏi FIX17 |
| --- | --- | --- | --- | --- |
| 1–2 | `l-…json` `expected._retained_source_vi` | "Danh sách **20** bảng giữ lại" | 22 | Con số này đã sai **từ trước** đợt PURGE-LIST (retained lúc đó là 21). FIX17 grep chuỗi "21"/"60"; một dòng ghi "20" thì không khớp mẫu nào. |
| 3 | `l-…json` `expected.retained_table_count` | `21` | `22` | Trường **có cấu trúc**, anh em của mảng `_retained_tables` mà tôi ĐÃ sửa ở FIX17 (21 → 22 phần tử). Sửa mảng mà quên con số cạnh nó — đúng loại lệch mà leg mới sinh ra để bắt. |
| 4–6 | `recovery/README.md` bảng fixture, hàng `l-…` | "khẳng định cả **20** bảng retained còn nguyên và **39** bảng dữ liệu nghiên cứu về 0" | 22 và **37** | Cùng lý do: cả hai số đều không phải "21"/"60". Số **39** không khớp bất kỳ giá trị lịch sử nào của tập purged (36 rồi 37) — nó là một lần đếm sai từ đầu, và không gate nào từng đọc nó. |

Đối chiếu sau khi sửa, đọc bằng `json.load` chứ không bằng mắt: `retained_table_count = 22` khớp
`len(_retained_tables) = 22`; `purged_table_count = 37` khớp `len(purged_table_counts_after) = 37`;
`never_purged_table_count = 2` khớp `len(_never_purged_tables) = 2`.

**`CR-PC02-25` đã trả đúng thứ nó hứa.** Leg đếm của W6n đọc **74 khẳng định số** trên **10
artefact** và so với 37 / 22 / 2 / 61. Ở FIX17 tôi tìm chín artefact bằng `grep` các chuỗi tôi
đoán trước ("21 bảng", "giữ 21", "60 entity") — và đúng như một phương pháp dựa trên phỏng đoán
sẽ hỏng, nó bỏ sót mọi chỗ ghi **20**, **39** hoặc một khóa JSON có cấu trúc. Máy tìm được cái
người đoán trượt. Đây là lý do tôi báo cáo giới hạn của `E0-18` ở FIX17 thay vì để nó im lặng.

**Giới hạn CÒN LẠI, do chính check tự khai và đáng nhắc lại:** `E0-18` vẫn **không** đọc liệt kê
tên trong văn xuôi. Một artefact kể ra sai 21 cái TÊN mà không viết một con số nào thì vẫn vô
hình. Chỉ danh sách có cấu trúc (leg c) và số học (leg d/e) được kiểm.

**Hash sau.** `acceptance/fixtures/recovery/README.md` `f1de7368…98da` →
`fa733add0f408dee3f1d870b1ca6f6da977337f2d940e0e13afe74ec4efccc79` (12235 B).
`acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json` `321e56af…0271` →
`1027d03e10f8c1cefdfe0b0d629d9e0a87f16336d3759221a779db4d55f54a22` (20814 B). Byte count không
đổi ở cả hai file vì mọi thay đổi là một chữ số đổi một chữ số.

**e0: 26/27 PASS, 1 FAIL, 1 vi phạm — FAIL còn lại KHÔNG phải của tôi.**
`E0-20-card-fixture-accounting`: `agent-tasks/TC-secret-settings-service.md` đã implemented nhưng
`evidence/handoffs/TC-secret-settings-service-handoff.md` **không tồn tại trên đĩa** (kiểm bằng
`ls`), nên không fixture nào của card đó hạch toán được. Card của WAI, đang bay; ngoài lease của
tôi và tôi không chạm. Hai FAIL của lượt trước đã tự hết trong lúc tôi làm: `E0-12` (run record
của cùng card đó) và **`E0-19-generated-matches` — WS đã sinh lại**, nên ba vi phạm
`GENERATED_FROM.json` từ FIX17 nay sạch.

Lease `LEASE-PC02-e23` nhả 2026-09-09T07:26Z. Không git mutation, không network, không file ngoài grant.
