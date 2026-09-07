# HANDOFF — PKT-PC01

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01` |
| worker principal | `worker-W2` |
| authority_id | `AUTH-COORD-PC01` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC01-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` — không có OS enforcement; lease theo dõi bằng thông điệp |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at (UTC) | 2026-09-06T16:54Z |
| finished_at (UTC) | 2026-09-06T17:16Z |
| next actor | `Coordinator` |
| lease_released_at (UTC) | 2026-09-06T17:16Z |

Lý do `DONE_WITH_CONCERNS`: mọi write target đã tạo và mọi verification đã chạy đạt, nhưng gói này phát sinh
4 unresolved refs và 2 change request tới gói khác (§6), trong đó `PROV-PC01-03` mang trạng thái
`OWNER_DECISION_REQUIRED`.

## 2. Changes

| Path | Operation | Before | After sha256 | Bytes |
| --- | --- | --- | --- | --- |
| `/mnt/virtual/repo/xcrawl/contracts/modules.yaml` | CREATE | ABSENT | `10757e27e8af4b212714c554a5e27a9938b39ea0c9584344f5fab1335781d941` | 66949 |
| `/mnt/virtual/repo/xcrawl/contracts/capabilities.yaml` | CREATE | ABSENT | `58956925fb28bb1b002c3bc620753b164c591686801b1c7c6d3bb943629331d4` | 33841 |
| `/mnt/virtual/repo/xcrawl/contracts/ports.yaml` | CREATE | ABSENT | `f935eef973fce15b7dab9491384ce38b8f18b487c827f6dac94d4b0a0a57d0c3` | 94773 |
| `/mnt/virtual/repo/xcrawl/contracts/ops/deployment.md` | CREATE | ABSENT | `d48b0c9d37ed150b187fb593dacc22b38f57754e309f557854ce1ecb2a15861b` | 16196 |
| `/mnt/virtual/repo/xcrawl/evidence/handoffs/PC01-handoff.md` | CREATE | ABSENT | (chính file này) | — |

Directory được tạo: `contracts/`, `contracts/ops/`, `evidence/`, `evidence/handoffs/`.
Ngoài phạm vi: `precode/` xuất hiện trong `git status` là sản phẩm của gói PC00 chạy song song — PC01 **không**
đọc, không ghi, không dựa vào nó. Không chạy lệnh git nào làm thay đổi repo. Không tạo file nào ngoài allowlist
(helper script nằm trong scratch dir `…/scratchpad/w2/`, chạy với `PYTHONDONTWRITEBYTECODE=1`, không sinh
`__pycache__`).

## 3. Source baselines

Kiểm trước khi bắt đầu (16:54Z) và lại trước handoff (17:15Z) — **khớp cả hai lần**:

| Ref | Path | SHA-256 | Bytes |
| --- | --- | --- | --- |
| SRC-PLAN | `/mnt/virtual/repo/xcrawl/research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |
| SRC-SPEC | `/mnt/virtual/repo/xcrawl/research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |

Đọc thêm (read-only, không phải baseline ghi): `agent_profile/worker.md`, `agent_profile/protocol.md`,
`agent_profile/registry.json`, baseline file và packet file trong scratchpad.

## 4. Evidence records

### EV-PC01-01 — YAML parse (EV-01 của packet)

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC01-01` |
| producer | `worker-W2` |
| type | `SELF_VALIDATION` |
| command | `python3 /tmp/…/scratchpad/w2/validate_pc01.py` (phần `yaml.safe_load` + parse front-matter) |
| runtime | python3 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3 (không dùng), Linux |
| started/ended (UTC) | 2026-09-06T17:14Z / 2026-09-06T17:14Z |
| inputs | 3 file YAML + front-matter của `contracts/ops/deployment.md` (hash ở §2) |
| oracle | `yaml.safe_load` trả về mapping không ném exception; front-matter có `contract_id: CT-ops-deployment` |
| expected | 4/4 parse thành công |
| observed | 4/4 parse thành công |
| exit code | 0 |
| status | `PASS` |
| limitations | Parse cú pháp, không kiểm ngữ nghĩa nghiệp vụ; không có JSON Schema cho các file này (chưa gói nào định nghĩa meta-schema cho contract file). |

### EV-PC01-02 — Kiểm chéo modules ↔ ports ↔ capabilities (EV-02 của packet)

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC01-02` |
| producer | `worker-W2` |
| type | `SELF_VALIDATION` |
| command | `python3 /tmp/…/scratchpad/w2/validate_pc01.py` |
| runtime | python3 3.12.3, PyYAML 6.0.1 |
| started/ended (UTC) | 2026-09-06T17:14Z / 2026-09-06T17:14Z |
| inputs | `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml` (hash ở §2) |
| oracle | 11 khẳng định EV-02a…EV-02k, xem cột observed |
| expected | 0 vi phạm |
| observed | 0 vi phạm; các khẳng định đạt: **a** không trùng `operation_id` (81 operation); **b** 81/81 đúng dạng `<domain>.<verb_noun>` snake_case; **c** mọi `owner_module`/`caller_modules` trong ports tồn tại trong modules (24 module + 7 external system); **d** `set(ports operations)` == hợp của mọi `inbound_operations`; **e** owner khai inbound và **mọi** caller nội bộ khai outbound, hai chiều; **f** `allowed_edges` (94 edge) bằng đúng tích caller × owner suy ra từ ports, transport khớp từng edge; **g** 36/36 `forbidden_edges` có `reason_vi` không rỗng và module hợp lệ; **h** không forbidden edge nào mâu thuẫn allowed edge mà thiếu `operation_scope`; **i** 10/10 `auth_scope` dùng trong ports được định nghĩa trong capabilities; **j** mọi operation được capabilities tham chiếu đều tồn tại; **k** 55 operation mutation, mỗi cái có **đúng một** owner scope và owner khớp `owner_module`. |
| exit code | 0 |
| status | `PASS` |
| limitations | Đây là kiểm tính nhất quán tĩnh (E0). Nó **không** chứng minh topology đúng nghiệp vụ, không chứng minh edge bị cấm thực sự bị chặn khi có code, và không thay cho independent audit. |

### EV-PC01-03 — Ma trận ca âm (EV-03 của packet)

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC01-03` |
| producer | `worker-W2` |
| type | `SELF_VALIDATION` |
| command | `python3 /tmp/…/scratchpad/w2/validate_pc01.py` (phần `denied_cases`) |
| runtime | python3 3.12.3, PyYAML 6.0.1 |
| started/ended (UTC) | 2026-09-06T17:14Z / 2026-09-06T17:14Z |
| inputs | `contracts/modules.yaml` khóa `denied_cases` |
| oracle | Đúng 10 case `NC-01`…`NC-10`, mỗi case chứa từ khóa của ca tương ứng trong packet và có đủ `expected_error_code`, `expected_state_vi`, `enforcement`, `enforcement_detail_vi` |
| expected | 10/10 đạt |
| observed | 10/10 đạt: NC-01 collector gọi Save · NC-02 worker đổi tag · NC-03 frontend đọc secret · NC-04 AI adapter gửi Telegram · NC-05 collector ghi SQLite · NC-06 Telegram adapter đổi cấu hình · NC-07 AI adapter fetch URL · NC-08 research connector điều khiển Chrome · NC-09 scheduler gửi digest · NC-10 backup operator tự resume dispatcher |
| exit code | 0 |
| status | `PASS` |
| limitations | Kiểm **sự tồn tại và đầy đủ trường** của ma trận, không phải kiểm hành vi. Hành vi bị cấm chưa được thử: trạng thái thi hành là `NOT_RUN` cho cả 10 ca. |

### Những gì KHÔNG chạy

| Hạng mục | Trạng thái | Ghi chú |
| --- | --- | --- |
| E1 contract tests | `NOT_RUN` | Chưa có code, chưa có fixture (PC09) |
| E2 integration/fault injection | `NOT_RUN` | — |
| E3 live probes (X, AI, CLI, Telegram) | `NOT_RUN` | SP1 chưa được cấp |
| E4 review nội dung nhiều kỳ | `NOT_RUN` | — |
| Independent audit | `NOT_RUN` | `audit_route: INDEPENDENT_REQUIRED`; PC01 tự kiểm là `SELF_VALIDATION`, **không** phải audit độc lập |
| Giá trị PROVISIONAL trong `deployment.md` §6 (30 s / 90 s / 900 s / 1800 s) | `NOT_RUN` | Chưa đo trên hệ thật; chờ probe A1 (SP1) |

## 5. Checklist của packet

| # | Mục | Trạng thái | Nằm ở đâu |
| --- | --- | --- | --- |
| 1 | Module ID, nơi chạy, data owner, inbound/outbound operation ID, forbidden edges; đủ mọi dòng SRC-PLAN §6 và SRC-SPEC §6.1, cộng embedding, scheduler, job service, secret service, repository port | `DONE` | `contracts/modules.yaml` → `modules` (24 module), `external_systems` (7), `allowed_edges` (94), `forbidden_edges` (36). Repository port: `MOD-data-store.repository_ports_vi` + `data_owner_of` của từng module. Mọi dòng §6 của plan có module tương ứng: Web UI, Scheduler, Local collector, Local analysis worker, AI adapter, Research connector, Embedding service, Report service, Telegram adapter, Backend domain services, Backup operator (`MOD-backup-cli` + `MOD-backup-service`). |
| 2 | Đóng D08/D42/D50 theo B12; analysis input = task từ server sau ingest commit; `decision_refs: [B12, ADR-0001]` | `DONE` | `contracts/modules.yaml` → `topology_decisions` TD-01…TD-06 (đều `status: PROVISIONAL`, `decision_owner: Owner`, `decision_refs: [B12, ADR-0001]` / `[B13]`). Đường input analysis: `analysis.enqueue_tasks` + `analysis.get_task_input`, cấm bằng FE-07/FE-08. Edge COL→AW của SRC-SPEC §6.2 được ghi rõ là **bị gỡ**. |
| 3 | Actor owner với auth scope khác nhau; không actor nào giữ hai vai owner cho một mutation | `DONE` | `contracts/capabilities.yaml` → `auth_scopes` (10 scope) và `actors` (12 actor: owner session, anonymous browser, anonymous probe, collector, analysis worker, AI adapter, Telegram ingress, Telegram linked chat, backup operator, scheduler, embedding, research connector, server domain services). Ràng buộc một-owner-một-mutation kiểm bằng EV-PC01-02 khẳng định **k**. |
| 4 | Readiness/capability registration cho local worker, gồm CLI provider `usable/unusable/unknown` + lý do | `DONE` | `contracts/capabilities.yaml` → `worker_capability_registration` (11 trường payload, enum `reason_code` 8 giá trị, 5 `server_rules`) và `zero_api_key_path`; `contracts/ops/deployment.md` §6–§7 (định nghĩa "collector online" + luồng đăng ký). |
| 5 | Ma trận 10 ca âm với mã lỗi và cơ chế thi hành | `DONE` | `contracts/modules.yaml` → `denied_cases` NC-01…NC-10; 6 cơ chế thi hành định nghĩa ở `default_deny.enforcement_mechanisms`; tham chiếu lại ở `contracts/ops/deployment.md` §10. |

### Invariants của packet

| Yêu cầu | Trạng thái | Bằng chứng |
| --- | --- | --- |
| Default deny được nêu rõ trong file | `DONE` | `contracts/modules.yaml` → `default_deny.rule_vi` (kèm cảnh báo rằng `forbidden_edges` **không** phải danh sách đầy đủ) |
| I01 truy được về edge/capability cụ thể | `DONE` | I01 gắn ở `MOD-web-ui`/FE-01/FE-02, NC-03, `CAP-P1`, và ở 20 operation trong `ports.yaml` |
| I11 truy được về edge/capability cụ thể | `DONE` | I11 gắn ở FE-16, FE-19, NC-04, NC-07, `ACT-ai-adapter.denied_capabilities` DC-AI-01…05, `CAP-P4` |
| Mỗi `operation_id` duy nhất | `DONE` | EV-PC01-02 khẳng định **a** (81 operation, 0 trùng) |
| Mỗi mutation có đúng một owner sở hữu dữ liệu nó sửa | `DONE` | EV-PC01-02 khẳng định **k** (55 mutation) |

## 6. Unresolved refs

### Quyết định PROVISIONAL do PC01 đưa ra

| ID | Nội dung | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| `PROV-PC01-01` | Thêm mã lỗi `CAPABILITY_DENIED` cho từ chối ở mức capability tiến trình/mạng/tool (khác `UNAUTHORIZED` vốn là lỗi ở API). Dùng trong NC-04, NC-05, NC-07, NC-08 và nhiều `denied_capabilities`. | `PROVISIONAL` | `ports.yaml → error_code_registry_note.codes_requested_provisional`; `modules.yaml → unresolved_refs` |
| `PROV-PC01-02` | Hủy liên kết Telegram là **hành động trong app** (`telegram.unlink`), không phải lệnh chat thứ tư. Dung hòa D37 (ĐX, "có lệnh hủy liên kết") với D36 (XN, đúng ba lệnh) và B10 ("không tự thêm lệnh Telegram thứ tư"). Chọn theo khuyến nghị của plan; Owner cần phê duyệt. | `PROVISIONAL` | `ports.yaml → telegram.unlink.provisional_note_vi`; `capabilities.yaml → ACT-telegram-linked-chat.note_vi` |
| `PROV-PC01-03` | "Xóa toàn bộ dữ liệu" (SRC-SPEC §7.3, thao tác thứ ba đòi xác nhận gõ tay) **chưa** có operation trong inventory. PC01 không tự tạo một mutation phá hủy khi P0 không liệt kê nó. | `OWNER_DECISION_REQUIRED` | `modules.yaml → unresolved_refs`; `capabilities.yaml → DC-OWN-04`; `ports.yaml → save.remove.state_effects_vi` |
| `PROV-PC01-04` | `MOD-backup-cli` được đặt ra để tách actor "backup operator" khỏi session owner; spec không mô tả giao diện backup. Nếu Owner muốn thao tác backup trong app thì cần edge và auth scope mới. | `PROVISIONAL` | `modules.yaml → unresolved_refs` |
| — | Ngưỡng readiness 30 s / 90 s / 900 s / 1800 s và các cổng 8080/8090/9222 | `PROVISIONAL` | `deployment.md` §3, §6 — mỗi số có đơn vị và một dòng lý do; chưa đo thật (`NOT_RUN`) |

### Change requests tới gói khác

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC01-01` | PC03 (`contracts/errors.yaml`) | Đăng ký mã lỗi `CAPABILITY_DENIED` với trạng thái đích và `retry_class`. PC01 dùng mã này ở 4 denied case nhưng **không được ghi** `contracts/errors.yaml`. Nếu PC03 từ chối, PC01 cần packet sửa để đổi 4 ca âm sang `UNAUTHORIZED` kèm ghi chú cơ chế. |
| `CR-PC01-02` | PC07 (`contracts/telegram/commands.yaml`) | Chốt allowlist đúng ba lệnh D36 và đặt hủy liên kết là hành động app (`telegram.unlink`), không phải lệnh chat. Nếu PC07/Owner quyết định giữ lệnh chat thứ tư, `ports.yaml` phải sửa (thêm caller `MOD-telegram-adapter` cho `telegram.unlink`) và FE-33 phải xem lại. |

### Quan sát về mâu thuẫn nguồn (không tự sửa)

1. **SRC-SPEC §6.2 vs B12.** Sơ đồ đường dữ liệu của spec có cạnh `COL → AW` (collector đưa dữ liệu thẳng cho
   analysis worker). Baseline §5 B12 gỡ cạnh này. PC01 ghi nhận việc gỡ ở FE-07/FE-08 và TD-05, gắn nhãn
   `PROVISIONAL`; đây là thay đổi so với hình vẽ trong spec và cần nằm trong bản amendment mà PC00/PC09 trình Owner.
2. **D36 vs D37** (đã nêu ở `PROV-PC01-02`).
3. **REQ-OQ01 chặn M0.** D09 (Chrome profile riêng) vẫn là ĐX và là câu hỏi mở số 1 chặn M0. PC01 mô tả topology
   theo D09 nhưng **không** promote nó sang XN (TD-04).

### Phụ thuộc PC01 giả định nhưng không kiểm được

- ID `ADR-0001` (quyết định topology) do PC00 viết song song; PC01 chỉ trích dẫn theo quy ước baseline §3 và
  **không** đọc/ghi `precode/`. Nếu PC00 đánh số ADR khác cho quyết định topology, Coordinator cần phát packet sửa
  `decision_refs` trong 3 file YAML của PC01.
- Các ID `REQ-…` được trích theo quy ước baseline §3 (`REQ-D…`, `REQ-P0-…`, `REQ-AC…`, `REQ-OQ…`, `REQ-A…`,
  `REQ-S<section>-<nn>`, `REQ-CTAG`). PC01 tự đặt một số `REQ-S…` cho yêu cầu prose (`REQ-S7.3-01`, `REQ-S7.3-02`,
  `REQ-S8.4-01`, `REQ-S11.2-01`, `REQ-S11.3-01`, `REQ-S11.4-01`, `REQ-S1.4-01`); nếu registry của PC00 đánh số khác
  cho cùng câu, cần một packet sửa để đồng bộ. Đây là rủi ro đã biết của việc chạy song song.

## 7. Trạng thái partial

Không có partial write. Cả 4 write target được tạo trọn vẹn và đã hash sau khi ghi (§2). Không rollback gì.

## 8. Giới hạn của bàn giao này

- Claim tối đa là `DRAFT_FOR_REVIEW`. Không tuyên bố `CONTRACT_READY`: B01–B17 vẫn `OPEN` trong
  `agent_profile/registry.json`, và các quyết định trong file này mang nhãn `PROVISIONAL` chờ Owner phê chuẩn.
- Bằng chứng duy nhất là `SELF_VALIDATION` mức E0. Không có independent audit, không có E1–E4.
- `contracts/ports.yaml` là danh mục operation dùng chung cho PC03–PC08. Sau khi Coordinator freeze, mọi thay đổi
  tên operation là change request theo SRC-PLAN §16, không phải sửa tại chỗ.

---

# ADDENDUM — PKT-PC01-FIX1

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX1` |
| worker principal | `worker-W2` |
| authority_id | `AUTH-COORD-PC01-FIX1` |
| lease_id | `LEASE-PC01-e2` (exclusive, fencing 2 — thay thế `LEASE-PC01-e1` đã released) |
| expires_at | 2026-09-07T02:00Z |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at (UTC) | 2026-09-06T17:26Z |
| finished_at (UTC) | 2026-09-06T17:27Z |
| next actor | `Coordinator` |
| lease_released_at (UTC) | 2026-09-06T17:27Z |

## A.1 Changes (MODIFY, whole-file grant)

| Path | Operation | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `/mnt/virtual/repo/xcrawl/contracts/ports.yaml` | MODIFY | `f935eef973fce15b7dab9491384ce38b8f18b487c827f6dac94d4b0a0a57d0c3` / 94773 | `bde5f133297c1aa381f2db8f5b861a54f9df593adc8c6fb9b7606a8f37dd4470` / 98442 |
| `/mnt/virtual/repo/xcrawl/contracts/modules.yaml` | MODIFY | `10757e27e8af4b212714c554a5e27a9938b39ea0c9584344f5fab1335781d941` / 66949 | `389487f809e2f69140414d71f72ce249ff612b4b72824d50c46041a4520367c8` / 67993 |
| `/mnt/virtual/repo/xcrawl/evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `80a887a265ff7a3e28b3017625ebcb1314697b24ad33877d3fd7b583a0bd8e0d` / 16069 | ghi ở thông điệp bàn giao (file tự tham chiếu) |

Baseline trước khi sửa khớp đúng hash trong §2 của handoff gốc. Source baselines kiểm lại lúc 17:26Z và 17:27Z —
`f65bb046…` và `d35e1f2d…`, **không đổi**. Không file nào khác được chạm; không lệnh git nào làm thay đổi repo.

## A.2 Delta nội dung

**`contracts/ports.yaml`**

1. Thêm operation `identity.merge_works` (đặt ngay trước `identity.resolve_conflict` trong khối domain `identity`):
   `transport: internal`, `owner_module: MOD-identity-service`,
   `caller_modules: [MOD-ingest-service, MOD-identity-service]`, `mutation: true`,
   idempotency key `loser_work_id + winner_work_id + alias_evidence_hash`.
   Effects: chuyển tham chiếu `post_work` / `saved_item` / `analysis` theo `contracts/data/identity.md` (PC02), ghi
   `identity_merge_audit`, snapshot Saved không bị sửa (I08); xử lý `first_announced` **delegate cho policy PC04**
   (`CR-PC02-06`). Errors: `VALIDATION_ERROR`, `NOT_FOUND`, `IDENTITY_CONFLICT`, `CONFLICT`,
   `IDEMPOTENCY_CONFLICT`, `STORAGE_WRITE_FAILED`; thêm `error_note_vi` nêu rõ `STALE_LEASE` **không áp dụng** vì
   đây là port nội bộ, không do worker giữ lease gọi. `scenario_refs: [SC07, SC09, SC23]`.
   `invariant_refs: [I03, I07, I08]`.
2. `identity.resolve_conflict.state_effects_vi`: nêu rõ quyết định `merge` được thực thi **bằng cách gọi**
   `identity.merge_works` — đường merge duy nhất; `keep_separate` đóng conflict và giữ hai canonical id.
3. `ingest.submit_batch.request_summary_vi`: thêm ghi chú rằng quan sát "nguồn đã bị xóa trên X" đến dưới dạng
   **trường của item** `source_deleted_observed_at` (RFC 3339 UTC, nullable) trong lô ingest, **không** phải một
   operation riêng — ruling của Coordinator thay cho `post.mark_source_deleted` của PC02. Ghi kèm ràng buộc: trường
   này không xóa dữ liệu và không đụng Saved (D55, AC-12).
4. `error_code_registry_note.codes_requested_provisional`: thêm `CONFLICT` (status `PROVISIONAL`,
   `change_request: CR-PC01-03`, `introduced_by: PKT-PC01-FIX1`), kèm lý do phân biệt với `IDEMPOTENCY_CONFLICT`
   (cùng key khác payload ở tầng wire) và `IDENTITY_CONFLICT` (hai identity mâu thuẫn chưa giải, đi vào cách ly).

**`contracts/modules.yaml`**

5. `MOD-identity-service`: `inbound_operations` += `identity.merge_works`; `outbound_operations` = `[identity.merge_works]`
   (trước đó rỗng) + `outbound_note_vi` giải thích self-call từ `identity.resolve_conflict`.
6. `MOD-ingest-service`: `outbound_operations` += `identity.merge_works` + `outbound_note_vi` mô tả đường phát hiện
   liên kết DOI↔arXiv và nêu rõ vì sao `MOD-research-connector` **không** phải caller.
7. `allowed_edges`: thêm 2 edge — `MOD-ingest-service → MOD-identity-service` và
   `MOD-identity-service → MOD-identity-service`, cả hai cho `identity.merge_works`, `transport: internal`
   (94 → 96 edge, vẫn bằng đúng tích caller × owner suy ra từ ports.yaml).
8. `mutation_ownership`: scope `work / alias / identity conflict` đổi tên thành
   `work / alias / identity conflict / merge audit` và thêm `identity.merge_works` vào `mutating_operations`
   (một owner cho một mutation vẫn giữ nguyên).

## A.3 Evidence

### EV-PC01-04 — Re-run kiểm chéo sau FIX1

| Trường | Giá trị |
| --- | --- |
| id | `EV-PC01-04` |
| producer | `worker-W2` |
| type | `SELF_VALIDATION` |
| command | `python3 /tmp/…/scratchpad/w2/validate_pc01.py` (script không đổi so với EV-PC01-02) |
| runtime | python3 3.12.3, PyYAML 6.0.1, `PYTHONDONTWRITEBYTECODE=1` |
| started/ended (UTC) | 2026-09-06T17:27Z / 2026-09-06T17:27Z |
| inputs | `contracts/ports.yaml` `bde5f133…`, `contracts/modules.yaml` `389487f8…`, `contracts/capabilities.yaml` `58956925…` (không đổi), `contracts/ops/deployment.md` `d48b0c9d…` (không đổi) |
| oracle | 14 khẳng định như EV-PC01-01/02/03, 0 vi phạm |
| expected | exit code 0 |
| observed | exit code 0, `== NO FAILURES ==`. Thay đổi so với lần chạy trước: **82** operation (81 → 82, 0 trùng); **96** allowed_edges (94 → 96) vẫn bằng đúng tích caller × owner; **56** mutating operation (55 → 56) mỗi cái đúng một owner scope. Các khẳng định còn lại giữ nguyên: ports↔modules nhất quán hai chiều, 36 forbidden_edges có lý do, 10 denied case đủ trường, 10 auth scope đều được định nghĩa. |
| exit code | 0 |
| status | `PASS` |
| limitations | Vẫn là kiểm nhất quán tĩnh E0. Không chứng minh hành vi merge đúng nghiệp vụ; ngữ nghĩa merge do PC02 (`contracts/data/identity.md`) và policy `first_announced` do PC04 chốt. E1–E4 và independent audit: `NOT_RUN`. |

## A.4 Concerns của FIX1

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `CR-PC01-03` (mới, → PC03) | Đăng ký mã lỗi `CONFLICT` trong `contracts/errors.yaml` với trạng thái đích và `retry_class`, phân biệt rõ với `IDEMPOTENCY_CONFLICT` và `IDENTITY_CONFLICT`. PC01 dùng mã này ở `identity.merge_works` nhưng không được ghi file của PC03. | `PROVISIONAL` |
| `PROV-PC01-05` (mới) | Packet ghi caller là "MOD-ingest-service / MOD-research-connector path". PC01 đặt caller = `[MOD-ingest-service, MOD-identity-service]` và **không** thêm `MOD-research-connector` làm caller, vì module đó là connector chỉ-đọc, không ghi dữ liệu authoritative (DC-RC-03) và hiện có `outbound_operations: []`. Nếu Coordinator thật sự muốn một edge `MOD-research-connector → MOD-identity-service`, cần packet sửa: nó thay đổi vai trò của connector và phải xem lại `capabilities.yaml`. | `PROVISIONAL` |
| `CR-PC02-06` (nhắc lại, không do PC01 sở hữu) | Xử lý `first_announced` sau merge được delegate cho policy PC04; `identity.merge_works` chỉ trả `first_announced_resolution` chứ không tự định nghĩa quy tắc. Nếu PC04 không chốt, I07 còn lỗ hổng. | `OPEN` |
| Ghi chú | `source_deleted_observed_at` mới chỉ là **tên trường + ngữ nghĩa** trong `ports.yaml`. Schema thật thuộc `contracts/schemas/ingest-batch.schema.json` (PC02/PC05); PC01 không tạo file đó. | — |

Các unresolved refs của handoff gốc (`PROV-PC01-01` … `PROV-PC01-04`, `CR-PC01-01`, `CR-PC01-02`) vẫn còn nguyên,
không mục nào bị FIX1 giải quyết.

---

# ADDENDUM — PKT-PC01-FIX2

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX2` |
| worker principal | `worker-W2` |
| authority_id | `AUTH-COORD-PC01-FIX2` |
| lease_id | `LEASE-PC01-e3` (exclusive, fencing 3) |
| expires_at | 2026-09-07T04:00Z |
| trigger | AUDIT_REPORT `PKT-A1-R1` (auditor-A1), verdict **FAIL** cho PC01 |
| findings in scope | `F-A1R1-01`, `F-A1R1-03`, `F-A1R1-04`, `F-A1R1-07` → tất cả `FIX_PROPOSED` |
| status | `DONE_WITH_CONCERNS` |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-06T17:30Z / 2026-09-06T18:01Z |
| next actor | `Coordinator` (rồi `auditor-A1` verify ở FC-W1 epoch 2) |
| lease_released_at (UTC) | 2026-09-06T18:01Z |

PC01 **không** tự đóng finding nào. Theo protocol §8, disposition `CLOSED` cần independent verification trên một
epoch mới, và người verify không được là người viết fix.

## B.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ports.yaml` | MODIFY | `bde5f133297c1aa381f2db8f5b861a54f9df593adc8c6fb9b7606a8f37dd4470` / 98442 | `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` / 111240 |
| `contracts/modules.yaml` | MODIFY | `389487f809e2f69140414d71f72ce249ff612b4b72824d50c46041a4520367c8` / 67993 | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` / 75088 |
| `contracts/capabilities.yaml` | MODIFY | `58956925fb28bb1b002c3bc620753b164c591686801b1c7c6d3bb943629331d4` / 33841 | `c54cdaaf85be339aff5823902c9cb27a2aa25ebea61c241f1b76d2999e6ea7ab` / 36423 |
| `contracts/ops/deployment.md` | MODIFY | `d48b0c9d37ed150b187fb593dacc22b38f57754e309f557854ce1ecb2a15861b` / 16196 | `4d879f2be6187623410bca378b34fc9aa38771b72e70ba309b8edef04a0f1295` / 16795 |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `1a615c76957bfebcc24a39f94fac19af21b2a416c1b3851a643f12c0129d3f66` / 23964 | ghi ở thông điệp bàn giao |

Baseline trước khi sửa khớp đúng hash trong addendum FIX1. Sources `f65bb046…` / `d35e1f2d…` kiểm lại lúc 18:01Z —
**không đổi**. Không chạm file PC00/PC02 (`precode/*`, `contracts/data/*`, `contracts/schemas/*`,
`acceptance/*`): `contracts/data/entities.yaml` chỉ được **đọc** để so khớp. Không lệnh git mutation.

## B.2 Theo từng finding

### F-A1R1-01 (MAJOR, checkpoint) — ruling R-01, phương án (b)

| Thay đổi | Ở đâu |
| --- | --- |
| Một entity duy nhất `checkpoint`, owner `MOD-ingest-service`. Token `ingest_checkpoint` → `checkpoint`; `run_checkpoint_pointer` **gỡ** khỏi `MOD-job-service` | `modules.yaml → data_owner_of` (ingest, job) |
| `ingest.submit_batch` là **đường chính**: `client_checkpoint_proposal` commit cùng transaction với post + receipt (`TXN-ingest-batch`); nêu rõ không có đường ghi checkpoint ở transaction riêng trước commit lô | `ports.yaml → ingest.submit_batch.state_effects_vi` |
| `ingest.commit_checkpoint` **giữ lại nhưng thu hẹp** thành cursor-only advance, `item_count` bắt buộc = 0, `reason ∈ {empty_page, end_of_feed, segment_close}` | `ports.yaml → ingest.commit_checkpoint.scope_restriction_vi`, `request_summary_vi` |
| **Guard**: `proposed_acked_through_ingest_sequence ≤ max(committed ingest_receipt.sequence)` của run; vượt → `VALIDATION_ERROR`, no partial write | `…guard_vi` |
| **Transaction** `TXN-checkpoint-only`: một transaction ghi đúng một hàng `checkpoint` + receipt, không có `post` | `…transaction_vi`, `…commit_point_vi` |
| **Failure timeline** 4 nhánh: lỗi trước commit / crash sau commit trước ACK / lease hết hạn / `write_blocked` | `…failure_timeline_vi` |
| **Oracle**: sau bất kỳ dãy `commit_checkpoint` + `submit_batch` nào, `checkpoint.acked_through ≤ max(committed ingest_receipt.sequence)` — đếm hàng, không đọc log | `…oracle_vi` |
| Thêm port đọc `ingest.get_checkpoint` (internal, owner ingest, caller job-service) để job-service dựng payload `worker.claim_assignment` mà **không** sở hữu/chạm bảng `checkpoint` | `ports.yaml` (op mới), `modules.yaml` inbound/outbound + 1 allowed_edge |

Phụ thuộc còn mở: PC02 phải viết lại I02 counterexample 2 và thêm `TXN-checkpoint-only` vào transaction map
(ruling R-01, phần của PC02). PC01 không ghi file PC02.

### F-A1R1-03 (MAJOR, naming/ownership) — ruling R-03 áp dụng nguyên bảng

Rename: `work_alias`→`identity_alias`, `ingest_checkpoint`→`checkpoint`, `lease`→`assignment_lease`,
`coverage_ledger`→`coverage_window`, `vector`→`tag_vector`. Gỡ: `run_checkpoint_pointer`.
Đánh dấu `kind: artifact` (loại khỏi phép so khớp): `sqlite_database_file`, `wal`, `readiness_snapshot_in_memory`.
Thêm owner cho 9 entity trước đây vô chủ — `identity_alias`, `identity_merge_audit` → MOD-identity-service;
`checkpoint` → MOD-ingest-service; `assignment_lease` → MOD-job-service; `coverage_window` → MOD-report-service;
`tag_vector` → MOD-embedding-service; `source_connection` → MOD-settings-service; `outbox_intent` →
MOD-delivery-service; `schema_migration` → MOD-data-store.
Thêm khối `data_owner_of_conventions` (thẩm quyền đặt tên, hai dạng phần tử, danh sách chờ, trạng thái đo được) và
ghi chú `entity_without_operation_vi` cho `schema_migration` (có owner, không có operation nào ghi — migration là
hoạt động triển khai).

### F-A1R1-04 (MAJOR, ba thao tác xóa) — ruling R-04

Thêm hai operation http owner-only, owner là module mới `MOD-data-admin-service` (để mutation phá hủy có đúng một
owner): `data.delete_target` (cờ xác nhận bắt buộc; transaction; **giữ lại** `saved_snapshot` + mọi ledger +
report đã publish; forbidden effects; error map 6 mã; `scenario_refs: [SC32]`) và `data.purge_all` (hai phase
`request_challenge` / `execute` với cụm từ xác nhận do server phát — giữ ngữ nghĩa "gõ tay" mà không cần operation
thứ ba; chỉ chạy ở `storage.health = maintenance`; thu hồi lease trước khi xóa; không tự resume dispatcher;
`exclusions_status: OWNER_DECISION_REQUIRED` **chỉ** cho danh sách loại trừ).
`save.remove.requirement_refs`: `REQ-S7.3-01` → `REQ-S7.3-05`, và `state_effects_vi` nêu rõ nó là thao tác thứ nhất
trong ba. `PROV-PC01-03` viết lại, **nêu tên cả ba** thao tác và thu hẹp phần `OWNER_DECISION_REQUIRED` xuống đúng
danh sách loại trừ. `capabilities.yaml`: thêm hai op vào `ACT-owner-session.allowed_operations`; `DC-OWN-04` viết
lại; thêm `DC-OWN-05` (guard `maintenance`/cụm từ sai) và `DC-OWN-06` (không được xóa `saved_snapshot`).
`deployment.md`: thêm dòng module và đoạn chế độ `maintenance`.

### F-A1R1-07 (MINOR, item_fields) — ruling R-07

`worker_capability_registration.payload_fields[].item_fields` chuyển thành list có cấu trúc
`{name, type, values, required, note_vi}` (8 phần tử); ba mục trước đây bị YAML đọc thành mapping vì dấu `(enum:`
không còn tồn tại. Oracle được siết: thêm **EV-02l** (shape assertion) và **EV-02m** (quét toàn bộ 3 file YAML tìm
list item parse thành mapping một khóa — chính lớp lỗi mà auditor đã phát hiện).

## B.3 Evidence

### EV-PC01-05 — script nhất quán (v1, không đổi) chạy lại

`python3 …/scratchpad/w2/validate_pc01.py` · 2026-09-06T18:00Z · **exit code 0**, `== NO FAILURES ==`.
Script v1 giữ nguyên bytes so với EV-PC01-02/04 để lần chạy cũ vẫn tái lập được.

### EV-PC01-06 — script mở rộng v2

`python3 …/scratchpad/w2/validate_pc01_v2.py` · 2026-09-06T18:01Z · **exit code 0**, `== NO FAILURES ==`.
Kết quả: **85** operation (82 → 85: `+ingest.get_checkpoint`, `+data.delete_target`, `+data.purge_all`), 0 trùng,
100% đúng dạng ID; **99** allowed_edges (96 → 99) bằng đúng tích caller × owner; ports↔modules nhất quán hai chiều;
**58** mutating operation, mỗi cái đúng một owner scope; 36 forbidden_edges có lý do; 10 denied case đủ trường;
10 auth scope đều được định nghĩa; **EV-02l** 8/8 `item_fields` đúng shape `{name,type,values,required}`;
**EV-02m** 0 list item parse thành mapping một khóa trong cả 3 file.
Giới hạn: vẫn là E0 tĩnh. Guard/transaction/oracle của R-01 và R-04 là **văn bản hợp đồng**, chưa có gì chạy —
`NOT_RUN`; oracle checkpoint chỉ trở thành bằng chứng khi PC09 dựng scenario và có code.

### EV-PC01-07 — set-comparison `data_owner_of` ↔ `entities.yaml`, hai chiều

Chạy trong v2. `contracts/data/entities.yaml` **được đọc, không ghi**. PC02 vẫn đang landing trong lúc đo, nên ghi
lại **hai** lần đo:

| Lần | entities.yaml sha256 | n entity | entities→PC01 (forward) | owner mismatch | PC01→entities (reverse) |
| --- | --- | --- | --- | --- | --- |
| 1 (17:5xZ) | `321fed5fad3961a5e7543c70776b903472da991526441e7cb034cca77f3cc101` | 57 | **0** | **0** | 2 |
| 2 (17:59Z, dùng cho kết luận) | `d91c433e749b8db00d5f6cc0e103e92983caaf9c9e62a6207ab8da2fb31bcc29` | 57 | **0** | **0** | 2 |

Artifact loại trừ khỏi phép so khớp: `sqlite_database_file`, `wal`, `readiness_snapshot_in_memory`.

**Residual diff (chiều PC01 → entities): đúng 2 token, cả hai do FIX2 tạo ra** —
`data_deletion_audit`, `purge_challenge` (owner `MOD-data-admin-service`). 20 token trong danh sách chờ của R-03
đã có entity contract ở cả hai lần đo, nên chúng **không** còn nằm trong residual.
Chiều forward bằng 0 và owner mismatch bằng 0 ở cả hai hash: mọi entity của PC02 có đúng một owner PC01 và hai bên
đồng ý về owner nào.
Cảnh báo tái lập: `entities.yaml` đổi hash giữa hai lần đo; con số trên gắn với đúng hash ghi ở đây, không phải
tuyên bố vĩnh viễn. Auditor nên đo lại trên bytes của epoch 2.

## B.4 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `CR-PC01-05` (mới → PC02) | Danh sách bảng cascade cho `data.delete_target` / `data.purge_all` và ràng buộc referential integrity khi xóa. PC01 chốt owner + phạm vi giữ lại + cờ xác nhận; **không** chốt danh sách bảng. | OPEN |
| `CR-PC01-06` (mới → PC02) | Entity contract cho `data_deletion_audit` và `purge_challenge` — đúng hai token còn dư trong EV-PC01-07. | OPEN |
| `CR-PC01-07` (mới → PC09) | `data.purge_all` chưa có scenario anchor: ruling F-08 chỉ đăng ký SC32 cho `data.delete_target`. Cần một SC riêng cho purge (blast radius khác hẳn). | OPEN |
| `PROV-PC01-03` (viết lại) | Phần còn `OWNER_DECISION_REQUIRED` **chỉ** là danh sách loại trừ của `data.purge_all` (settings, secrets, credential đăng nhập, telegram_link, schema_migration). Hai operation không bị chặn. | OWNER_DECISION_REQUIRED |
| `PROV-PC01-06` (mới) | `MOD-data-admin-service` là module mới và mang ngoại lệ duy nhất với repository-port-theo-bảng (DC-SRV-01), giới hạn ở thao tác xóa. Nếu Coordinator muốn đặt hai op vào module có sẵn thì cần packet sửa. | PROVISIONAL |
| Phụ thuộc R-01 | PC02 phải viết lại I02 counterexample 2 và thêm `TXN-checkpoint-only`. Cho tới lúc đó, mô tả checkpoint vẫn còn **hai** nguồn (PC01 đã sửa, PC02 chưa) và `F-A1R1-01` không thể verify trọn vẹn. | OPEN |
| Ngoài phạm vi | `F-A1R1-02` (fixture actor) thuộc PC02; `F-A1R1-05/06/08/09` thuộc PC00. PC01 không chạm. | — |

Các unresolved refs cũ `PROV-PC01-01`, `-02`, `-04`, `-05` và `CR-PC01-01`, `-02`, `-03` vẫn OPEN, không mục nào
được FIX2 giải quyết.

---

# ADDENDUM — PKT-PC01-FIX3

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX3` · authority `AUTH-COORD-PC01-FIX3` · lease `LEASE-PC01-e4` (fencing 4) |
| expires_at | 2026-09-07T06:00Z |
| trigger | Rulings FIX3 §"Operations (PC01 FIX3)" + §error-code; AUDIT_REPORT `PKT-A1-R2` (PC01 epoch 2 = **PASS**, một MINOR `F-A1R2-06`) |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-06T18:28Z / 2026-09-06T18:34Z |
| next actor | `Coordinator` · lease_released_at 2026-09-06T18:34Z |

## C.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ports.yaml` | MODIFY | `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` / 111240 | `5afd368f68237183a029e4b97e427773c9282ec91da2a45541f149da3893cc0a` / 115359 |
| `contracts/capabilities.yaml` | MODIFY | `c54cdaaf85be339aff5823902c9cb27a2aa25ebea61c241f1b76d2999e6ea7ab` / 36423 | `ecba935c1fdec4dbf1b7f4539b47fb51bb3a8aa0d148e58b0fc432836f760c4a` / 37648 |
| `contracts/ops/deployment.md` | MODIFY | `4d879f2be6187623410bca378b34fc9aa38771b72e70ba309b8edef04a0f1295` / 16196 | `39b1a7103f29895c079e08e732a10f7d380e665c4498f1bc83faeadb09e6a17c` / 17314 |
| `contracts/modules.yaml` | **NO CHANGE** | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` / 75088 | *(bằng before — không mục nào của FIX3 chạm tới file này)* |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `644271bb083e861b4dec63459da84af3cb078512baee3c5fb7763812022ef10e` / 35880 | ghi ở thông điệp bàn giao |

Upstream đã đọc (không ghi): `precode/requirements.csv`, `contracts/data/entities.yaml` `2235564f…` (59 entity),
`contracts/state/run.yaml` `8acb7bbf…`, `contracts/errors.yaml` `e236aaee…`, `contracts/http/openapi.yaml`
`daaf5521…`, `…/audits/A1-R2-report.md`, `…/packets/FIX3-rulings.md`. Sources `f65bb046…`/`d35e1f2d…` không đổi
(kiểm 18:28Z và 18:33Z). Không chạm file của gói khác; không lệnh git mutation.

## C.2 Theo từng mục ruling

| Ruling | Thay đổi | Ở đâu |
| --- | --- | --- |
| **CR-PC03-01** — `REQ-S8.4-01` không tồn tại | Spec chỉ có tới §8.3; không có §8.4. Thay bằng id thật: `health.get_liveness` → `REQ-S9.3-08`, `REQ-S8.3-03`; `health.get_readiness` → `REQ-S9.3-08`, `REQ-S8.3-01/02/03`, `REQ-AC15`, `REQ-P0-12`; `storage.get_health` → `REQ-S9.3-08`. Nguồn văn bản của quy tắc "kênh health độc lập DB" vẫn là SRC-PLAN §8.4 và được giữ trong `source_refs`; chỉ **requirement id** là sai. | `ports.yaml` ×3 operation |
| **CR-PC03-02** — guard của `run.resume` | Thêm `allowed_from_states_vi`: đúng hai trạng thái nguồn — `needs_user` (guard: phiên X không còn challenge, `T-RUN-10`) và `blocked` (guard: owner cung cấp `unblock_reason` **bắt buộc**; hệ thống không tự phán đoán và không thử lại để dò, REQ-S13.2-04). Mọi trạng thái khác ⇒ `CONFLICT`. `request_summary_vi` mang `unblock_reason`; `error_codes` += `CONFLICT`, `X_ACCESS_BLOCKED`, `CSRF_REJECTED`. | `ports.yaml` `run.resume` |
| **CR-PC03-05** — chính tả `task_type` | `open_labeling` → `label`, `emerging_direction_phrasing` → `direction_phrasing` (giữ `summary`), lấy từ `entities.yaml` `analysis_task.task_type`. Đổi ở `ports.yaml` `analysis.enqueue_tasks` và `capabilities.yaml` `tasks_supported.values` + đoạn `zero_api_key_path`. Chính tả cũ **chỉ** còn trong một `note_vi` giải thích lịch sử. | `ports.yaml`, `capabilities.yaml` |
| **CR-PC04-04** | `report.publish.error_codes` += `CONFLICT`, kèm `error_note_vi`: publisher thua CAS phải đọc lại và dựng lại, không publish kỳ chồng. | `ports.yaml` |
| **F-A1R2-06** | `data.purge_all.scenario_refs: [SC44]`; `scenario_note_vi` liệt kê những gì SC44 phải phủ: hai phase xác nhận, tiên quyết `storage.health = maintenance`, thu hồi lease, và bốn ca âm (cụm từ sai, challenge hết hạn, challenge dùng lại, sai storage state). `CR-PC01-07` khép lại nhờ ruling này. | `ports.yaml` |
| **CR-PC08-02** | Thêm `conventions.auth_scope_to_wire_scheme_vi`: ánh xạ đầy đủ auth_scope → security scheme của PC05, trong đó `backup_operator` ⇒ `backupOperatorToken` cho **cả bốn** `backup.*`, và owner session ⇒ `ownerSessionCookie` + `ownerCsrfToken` cho **mọi** mutation. Nhắc lại trong `deployment.md` §9 và trong mô tả hai auth scope của `capabilities.yaml`. | `ports.yaml`, `capabilities.yaml`, `deployment.md` |
| **Error code `CSRF_REJECTED`** | Thêm vào `error_codes` của **19/19** operation http mutation thuộc owner session. Thêm `conventions.csrf_rule_vi` (403, không đổi trạng thái) và mục `codes_from_fix3_ruling` nêu rõ ranh giới ba mã: `CSRF_REJECTED` (thiếu/lệch CSRF) ≠ `UNAUTHORIZED` (danh tính chưa xác lập / sai lớp principal) ≠ `FORBIDDEN_EDGE` (cạnh không có trong registry). Thêm `DC-OWN-07` vào `capabilities.yaml`. Giải quyết `CR-PC08-03`. | `ports.yaml`, `capabilities.yaml` |

Danh mục vẫn **85 operation** và **99 allowed_edges**: FIX3 không thêm/bớt operation nào, chỉ sửa metadata.

## C.3 Evidence

### EV-PC01-08 — script v1 (không đổi) chạy lại
`python3 …/w2/validate_pc01.py` · 18:33Z · **exit 0**, `== NO FAILURES ==`. Giữ nguyên bytes để lần chạy epoch 1/2 vẫn tái lập.

### EV-PC01-09 — script v2 mở rộng
`python3 …/w2/validate_pc01_v2.py` · 18:33Z · **exit 0**, `== NO FAILURES ==`, 1 WARN có chủ đích.
Khẳng định cũ giữ nguyên (85 op, 0 trùng, 99 edge = tích caller×owner, ports↔modules hai chiều, 58 mutation một
owner, 36 forbidden edge có lý do, 10 denied case, 10 auth scope, item_fields đúng shape, không list item nào parse
thành mapping). **Bốn khẳng định mới của FIX3:**

| Check | Kết quả |
| --- | --- |
| `EV-02n` mọi REQ id được trích tồn tại trong `precode/requirements.csv` | **97/97 PASS** — đây là check bắt được `REQ-S8.4-01`; trước FIX3 nó sẽ FAIL |
| `EV-02o` mọi mã lỗi dùng trong `ports.yaml` tồn tại trong `errors.yaml` | 24 mã; **23 có mặt**, `CSRF_REJECTED` **WARN — chờ PC03 FIX1 đăng ký** (đúng theo ruling) |
| `EV-02p` mọi mutation owner-session mang `CSRF_REJECTED` | **19/19 PASS** |
| `EV-02q` mọi `backup.*` dùng `auth_scope: backup_operator` | **4/4 PASS** |
| `EV-02r` enum `tasks_supported` == `entities.yaml analysis_task.task_type` | **PASS** — `['direction_phrasing','label','summary']` |
| `EV-02s` chính tả cũ chỉ còn trong `note_vi` giải thích | **PASS** |

### EV-PC01-10 — set-comparison entity ↔ owner
Chạy trong v2, đối chiếu với `contracts/data/entities.yaml` sha256
`2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993`, **59 entity**:

| Chiều | Kết quả |
| --- | --- |
| entities → PC01 owner | **0** |
| owner_module mismatch | **0** |
| PC01 token → entities (residual) | **0** — PC02 FIX2 đã bổ sung `data_deletion_audit` và `purge_challenge`; residual của FIX2 (2 token) nay bằng 0 |
| Artifact loại trừ | `sqlite_database_file`, `wal`, `readiness_snapshot_in_memory` |

Ghi chú tái lập: PC02 FIX3 sẽ landing sau và **có thể thêm trường, không thêm entity** (theo packet). Nếu nó thêm
entity thì con số trên phải đo lại; kết luận này gắn với đúng hash nêu trên.

### Không chạy
E1–E4, independent audit, và mọi guard trong hợp đồng: `NOT_RUN`. Ranh giới ba mã lỗi ở C.2 là **văn bản hợp
đồng**; chưa có gì thực thi nó.

## C.4 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `CSRF_REJECTED` chờ upstream | `ports.yaml` dùng mã này ở 19 operation nhưng `contracts/errors.yaml` (`e236aaee…`) **chưa** có nó; ruling giao PC03 FIX1 đăng ký. Cho tới lúc đó EV-02o còn một WARN có chủ đích. Nếu PC03 đăng ký với `http_status` hoặc `retry_class` khác những gì `ports.yaml` ghi (403 / `none` / không đổi trạng thái) thì phải đồng bộ lại. | OPEN |
| `CR-PC01-08` (mới → PC08 packet riêng) | `contracts/http/openapi.yaml` đã đổi hash trong lúc FIX3 chạy: `6d9a8c50…` → `daaf5521…`. `contracts/ops/secrets.md` §2.3 (file của PC08) **trích hash cũ**. PC01-FIX3 không có quyền ghi file đó; cần một packet để cập nhật trích dẫn và xác nhận sáu tên scheme không đổi. | OPEN |
| `CR-PC03-02` phía PC03 | PC01 đã ghi guard `blocked → queued`; hàng transition tương ứng do **PC03 FIX1** thêm vào `run.yaml`. Hiện `run.yaml` (`8acb7bbf…`) chỉ có `T-RUN-10` từ `needs_user`. Cho tới khi PC03 landing, hai file mô tả `run.resume` ở mức chi tiết khác nhau. | OPEN |
| `SC44` | `data.purge_all` nay trích `SC44`, nhưng anchor do **PC00 FIX2** ghi và scenario do **PC09** viết. Trích dẫn hiện chưa có đích. | OPEN |
| Kế thừa | `PROV-PC01-01/-02/-04/-05/-06`, `PROV-PC01-03` (`OWNER_DECISION_REQUIRED`, danh sách loại trừ của `data.purge_all`), `CR-PC01-05/-06` vẫn OPEN. `CR-PC01-01`, `-03` đã được `errors.yaml` giải quyết (`CAPABILITY_DENIED`, `CONFLICT` đều có mặt); `CR-PC01-07` khép lại nhờ ruling F-A1R2-06. | — |

---

# ADDENDUM — PKT-PC01-FIX4

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX4` · authority `AUTH-COORD-PC01-FIX4` · lease `LEASE-PC01-e5` (fencing 5) |
| expires_at | 2026-09-07T06:00Z |
| trigger | Amendment của Coordinator: `CR-PC05-04`, `CR-PC05-05`, `CR-PC05-01` (từ handoff PC05) + `CR-PC01-08` |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-06T18:35Z / 2026-09-06T18:38Z |
| next actor | `Coordinator` · lease_released_at 2026-09-06T18:38Z |

## D.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ports.yaml` | MODIFY | `5afd368f68237183a029e4b97e427773c9282ec91da2a45541f149da3893cc0a` / 115359 | `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a` / 121958 |
| `contracts/ops/secrets.md` | MODIFY | `4ad6c26af9d14430f3fabd44b38bdc745d9d291ec9f2faf00b960c34ba38ab8d` / 23585 | `774a1130fa398602b4f0eb02334212cc2c762eaee95d172dd804a8b099344802` / 24343 |
| `contracts/capabilities.yaml` | **NO CHANGE** | `ecba935c1fdec4dbf1b7f4539b47fb51bb3a8aa0d148e58b0fc432836f760c4a` | không có `stop_reason` nào được liệt kê trong file này — grant không dùng tới |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `b5bc0fd443db30d9b2a0042b59895dd3dac92aeb827f6852be59be94b8347ad6` / 45379 | ghi ở thông điệp bàn giao |

Upstream đọc lúc chạy: `contracts/errors.yaml` **`f503cbf17a8503a4c95b6eae94755c0fab5acd3fc9cb5ef6a088c584d1b3b5cf`
(28 mã)** — PC03 FIX1 đã landing giữa chừng và **đã đăng ký cả `CSRF_REJECTED` lẫn `SOURCE_LAYOUT_CHANGED`**;
`contracts/http/openapi.yaml` `daaf5521…` (W4 đang sửa tiếp — xem D.2 mục 4). Sources không đổi.

## D.2 Theo từng mục

**1. `CR-PC05-04`** — `VALIDATION_ERROR` thêm vào `error_codes` của `auth.logout`, `worker.release_assignment`,
`analysis.heartbeat`. Cả ba là mutation mang header bắt buộc (`X-Schema-Version`, `X-Request-Id`) và hai trong ba
có body; PC05 đã trả 422 ở tầng wire, nay hai file khớp nhau.

**2. `CR-PC05-05`** — tách **JSON Schema** khỏi **hợp đồng mô tả hình dạng**. Một trường
`request_schema_planned` / `response_schema_planned` nay chỉ mang đường dẫn khi đó là file
`contracts/schemas/*.schema.json` thật (thứ `$ref` của OpenAPI dereference được); mọi trường hợp khác là **`null`**
kèm `x-schema-source-request` / `x-schema-source-response` nêu tên hợp đồng mô tả hình dạng.
Áp dụng **toàn diện**, không chỉ sáu giá trị PC05 gặp: **143** trường được chuyển, còn lại **0** con trỏ
không-JSON-Schema; bảy đường dẫn `.schema.json` (đều đã tồn tại) giữ nguyên. Quy tắc ghi ở
`conventions.schema_reference_rule_vi`, kèm câu cảnh báo `null` **không** nghĩa là "không có hợp đồng".
Phạm vi rộng hơn văn bản CR là có chủ đích: sửa đúng sáu chỗ sẽ để lại 137 chỗ cùng lớp lỗi cho vòng audit sau.

**3. `CR-PC05-01`** — `stop_reason` của `worker.report_stop` thêm giá trị **`source_layout_changed`**, và
`error_codes` thêm **`SOURCE_LAYOUT_CHANGED`**. Ghi rõ vì sao nó **không** phải `source_blocked`: bố cục đổi nghĩa là
parser không đọc được, cách gỡ là **sửa parser** chứ không phải chờ hết hạn chế, và **không** được tự thử lại để dò.
Coordinator chọn tên `source_layout_changed`; PC05 đề nghị `parser_degraded` — tên của Coordinator được dùng.
Đây là điểm duy nhất PC01 enumerate stop reason; `capabilities.yaml` không liệt kê chúng nên không phải sửa.

**4. `CR-PC01-08`** — `contracts/ops/secrets.md` §2.3 và front-matter bỏ sha256 của `openapi.yaml`, thay bằng
trích dẫn **"bản đóng băng ở candidate FC-W3"** cộng **tên** sáu security scheme, kèm lý do: một hash trỏ vào file
đang được viết song song là trích dẫn tự-hỏng — nó sai ngay khi upstream đúng; tên scheme ổn định qua các bản sửa
của PC05, còn hash thì không, và manifest của FC-W3 mới là nơi hash thuộc về.
Nhân tiện, đoạn "khác biệt còn mở" về mã lỗi CSRF được thay bằng ghi nhận **đã giải quyết**: ruling FIX3 đăng ký
`CSRF_REJECTED` (403, `scope: request`, `retry_class: none`, không đổi trạng thái); `CR-PC08-03` khép lại.

## D.3 Evidence

`python3 …/w2/validate_pc01_v2.py` · 2026-09-06T18:37Z · **exit code 0**, `== NO FAILURES ==`, **0 WARN**
(cảnh báo `CSRF_REJECTED` của FIX3 tự hết khi PC03 FIX1 landing).
`python3 …/w2/validate_pc01.py` (v1, không đổi) · **exit 0**.
`python3 …/w2/validate_pc08.py` · **exit 0** — chạy lại vì `secrets.md` bị sửa; 10 fixture và mọi trích dẫn chéo
vẫn nhất quán.

Khẳng định mới của FIX4, tất cả PASS:

| Check | Kết quả |
| --- | --- |
| `EV-02t` mọi con trỏ schema là `.schema.json` hoặc `null` + `x-schema-source` | **PASS** — 143 `x-schema-source`, 0 con trỏ sai loại, 0 `null` thiếu nguồn |
| `EV-02u` `stop_reason` có `source_layout_changed`; `worker.report_stop` mang `SOURCE_LAYOUT_CHANGED` | **PASS** |
| `EV-02v` ba operation của CR-PC05-04 mang `VALIDATION_ERROR` | **PASS** |
| `EV-02o` mã lỗi tồn tại trong `errors.yaml` | **25/25 PASS** — cả `CSRF_REJECTED` và `SOURCE_LAYOUT_CHANGED` nay đã có trong `errors.yaml` `f503cbf1…` |

Khẳng định cũ giữ nguyên: 85 operation, 0 trùng, 99 allowed_edges = tích caller×owner, ports↔modules hai chiều,
58 mutation một owner, 19/19 CSRF, 4/4 `backup.*`, entity set-comparison 0/0/0 với `entities.yaml` `2235564f…`.
Danh mục vẫn **85 operation** và **99 edge**: FIX4 không thêm/bớt operation nào.

## D.4 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `CR-PC01-08` | **Đóng.** `secrets.md` không còn pin hash của `openapi.yaml`. | CLOSED (chờ Coordinator xác nhận) |
| `CR-PC08-03` | **Đóng** nhờ `CSRF_REJECTED` đã có trong `errors.yaml`. | CLOSED (chờ xác nhận) |
| `x-schema-source` là trường mở rộng | Tên trường do PC01 đặt (`x-` prefix theo thông lệ OpenAPI). Nếu PC05/PC09 muốn tên khác thì đổi ở đây một chỗ; 143 trường sinh bằng script nên đổi lại rẻ. | OPEN |
| Bảy `.schema.json` | Tất cả đã tồn tại dưới `contracts/schemas/`. PC01 **không** kiểm nội dung chúng có mô tả đúng payload của operation hay không — đó là việc của PC09. | OPEN |
| Kế thừa | `PROV-PC01-01/-02/-03/-04/-05/-06`, `CR-PC01-05/-06` vẫn OPEN. `SC44` vẫn chờ anchor (PC00 FIX2) và scenario (PC09). Guard `blocked → queued` vẫn chờ hàng transition của PC03. | — |

---

# ADDENDUM — PKT-PC01-FIX5

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX5` · authority `AUTH-COORD-PC01-FIX5` · lease `LEASE-PC01-e6` (fencing 6) |
| expires_at | 2026-09-07T06:00Z |
| trigger | `CR-PC02-16` (PC02) và `CR-PC06-03` (PC06) |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-06T18:39Z / 2026-09-06T18:42Z |
| next actor | `Coordinator` · lease_released_at 2026-09-06T18:42Z |

## E.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/modules.yaml` | MODIFY | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` / 75088 | `89b348aa8d3f89d38c945a7f15a8fe2c46e2619a1226649e4633bf30367264f5` / 75794 |
| `contracts/capabilities.yaml` | MODIFY | `ecba935c1fdec4dbf1b7f4539b47fb51bb3a8aa0d148e58b0fc432836f760c4a` / 37648 | `26764a24ffe3704b38b55880cca8cde603358a84ff644018b77e6c6b060f7078` / 39793 |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `6d90d6cd9a5991dc59e89cf41092a5c1bd17d03d861cadd82830712d150497ea` / 52289 | ghi ở thông điệp bàn giao |

`contracts/ports.yaml` và `contracts/ops/*` **không** thay đổi trong packet này. Sources không đổi (kiểm 18:39Z và
18:42Z).

## E.2 Theo từng mục

**1. `CR-PC02-16` — `telegram_link_attempt`.** Thêm vào `MOD-telegram-adapter.data_owner_of`, kèm
`data_owner_of_note_vi` nói vì sao nó tồn tại: ngoại lệ liên kết hẹp B09 cho phép một chuỗi **đúng định dạng mã**
từ chat **chưa** liên kết được đối chiếu với các mã chưa hết hạn/chưa dùng; không có bộ đếm giới hạn thì chính
ngoại lệ đó thành một oracle dò mã miễn phí. Chủ sở hữu là `MOD-telegram-adapter` vì nó xử lý ingress và biết chat
nào đã thử. Ghi rõ ràng buộc không được nới: việc bị từ chối vẫn **bỏ im lặng** phía chat (REQ-S11.3-02) — đếm để
**chặn**, không phải để trả lời.

**Trạng thái entity khi đo:** `contracts/data/entities.yaml` đổi hash **hai lần** trong lúc packet chạy —
`5e0b119236be61344518e05cf7bd2039471ab03310ef486c9d7eaa249af05b4e` lúc bắt đầu (18:39Z) rồi
`d6c583c11233d343a6198d386234adffbbd5819815e2f726359628f1bdb575b7` lúc kết thúc (18:42Z), **60 entity** ở cả hai
lần. `telegram_link_attempt` **đã có mặt** ngay từ lần đo đầu với `owner_module: MOD-telegram-adapter` — PC02-FIX3
landing trước khi PC01-FIX5 bắt đầu, nên không có cửa sổ nào mà PC01 khai một owner cho entity chưa tồn tại.

**2. `CR-PC06-03` — oracle khai báo cho AI adapter.** Thêm khối `declared_oracle` vào `ACT-ai-adapter`:
`tool_definitions_registered: 0`, `tool_calls_permitted: false`, `network_egress: inference_endpoint_only`, mỗi
giá trị kèm một dòng **phép đo** (đếm mục tool trong payload gửi provider; đếm số lần thực thi tool; đếm kết nối
tới host khác) để fixture (f) của PC06 và SC17 có oracle đo được thay vì một câu mô tả.
Ghi rõ giới hạn của khẳng định: đây là khẳng định về **cấu hình adapter**, không phải về hành vi model — model vẫn
có thể sinh văn bản đòi gọi tool; cái được bảo đảm là **không có tool nào tồn tại để gọi**, và yêu cầu đó bị ghi
audit rồi item đi theo `AI_OUTPUT_INVALID`. Áp cho **cả hai** họ provider; với CLI/ACP,
`isolation_verified: false` ⇒ adapter giữ `disabled` (B13, ADR-0010).
Hình dạng `item_fields` có cấu trúc của `worker_capability_registration` **không bị đụng tới** (EV-02l vẫn PASS).

## E.3 Evidence

`python3 …/w2/validate_pc01_v2.py` · 2026-09-06T18:42Z · **exit 0**, `== NO FAILURES ==`, 0 WARN.
`python3 …/w2/validate_pc01.py` (v1) · **exit 0**.

| Check | Kết quả |
| --- | --- |
| `EV-02w` (mới) `ACT-ai-adapter.declared_oracle` có đúng ba giá trị đã ruling | **PASS** |
| `EV-02l` `item_fields` vẫn đúng shape `{name,type,values,required}` | **PASS** (8 entry) |
| `EV-02m` không list item nào parse thành mapping một khóa | **PASS** |
| `EV-05` set-comparison với `entities.yaml` `d6c583c1…` (60 entity) | forward **0**, owner mismatch **0**, reverse residual **0** |

Khẳng định cũ giữ nguyên: 85 operation, 99 allowed_edges, ports↔modules hai chiều, 58 mutation một owner,
19/19 CSRF, 143 con trỏ schema hợp lệ, 97 REQ id resolve.

## E.4 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| `entities.yaml` đang thay đổi liên tục (ba hash quan sát được trong hai packet gần nhau). Kết luận set-comparison gắn với đúng hash ghi ở E.3; Auditor nên đo lại trên bytes của epoch kế tiếp. | OPEN |
| `declared_oracle` là cấu trúc do PC01 đặt ra để PC06 có chỗ trỏ tới. Nếu PC06 muốn hình dạng khác (ví dụ đặt trong `contracts/ai/providers.yaml` thay vì ở đây) thì nên hợp nhất một chỗ — hiện chưa có xung đột vì `providers.yaml` chưa tồn tại lúc viết. | OPEN |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06`, `SC44` chờ anchor + scenario, guard `blocked → queued` chờ hàng transition của PC03. |

---

# ADDENDUM — PKT-PC01-FIX6

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX6` · authority `AUTH-COORD-PC01-FIX6` · lease `LEASE-PC01-e7` (fencing 7) |
| expires_at | 2026-09-07T10:00Z |
| trigger | `CR-PC10-02` và `CR-PC10-03` (từ `evidence/handoffs/PC10-handoff.md`) |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-06T19:12Z / 2026-09-06T19:21Z |
| next actor | `Coordinator` · lease_released_at 2026-09-06T19:21Z |

## G.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ports.yaml` | MODIFY | `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a` / 121958 | `87c95da46c607c977a7f0421cc4110745575efc47581952d3d619a4147f1f305` / 122712 |
| `contracts/capabilities.yaml` | MODIFY | `26764a24ffe3704b38b55880cca8cde603358a84ff644018b77e6c6b060f7078` / 39793 | `cb1f8b68df3523a1d14578b3f83556b4addd61f4640d6dae624a498d551db499` / 45652 |
| `contracts/modules.yaml` | **NO CHANGE** | `89b348aa8d3f89d38c945a7f15a8fe2c46e2619a1226649e4633bf30367264f5` | ánh xạ actor↔module sống ở `capabilities.yaml` (`module_refs`), không ở đây — grant không dùng tới |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `ce17142d542ea6b66ded5794556fc9d8d4296b6eaa50f898b1a9442e9e288e94` / 57621 | ghi ở thông điệp bàn giao |

Upstream đọc lúc chạy: `contracts/data/entities.yaml` `209cf03e…` (60 entity), `contracts/errors.yaml`
`3201bbe86a3ef373a4fb35c265cd9f27ed60f6ce2af3fd65a76c0dcfb032d86b`. Sources không đổi.

## G.2 CR-PC10-02 — rate limit có đường báo riêng

Thêm giá trị `rate_limited` vào enum `stop_reason` của `worker.report_stop` và `RATE_LIMITED` vào `error_codes`.
Ngữ nghĩa ghi theo ruling và SRC-SPEC §9.3 ("dừng đợt, ghi lý do, không luân chuyển gì để lách"): đóng collection
segment, run kết thúc **`outcome: partial`**, **không** retry trong cùng run, đợt theo lịch kế tiếp chạy bình
thường; giữ checkpoint đã ACK; **không** luân chuyển account/proxy và **không** dò lại để tìm giới hạn.

Ghi rõ vì sao đây không phải `source_blocked`: rate limit nghĩa là X **vẫn cho vào** nhưng bảo chờ;
`source_blocked` nghĩa là X **không cho vào**. Gộp hai thứ làm một sẽ cho hai hành vi UI khác nhau ở AC-15 và làm
người dùng hiểu sai chuyện gì đang xảy ra với tài khoản của mình. PC03 thêm hàng transition tương ứng trong
`run.yaml`; PC01 chỉ khai enum và mã lỗi.

## G.3 CR-PC10-03 — principal cho việc gửi ra ngoài

Thêm actor mới **`ACT-delivery-dispatcher`** (`internal_process`, `module_refs: [MOD-delivery-service,
MOD-telegram-adapter]`, `auth_scope: internal_only`) với
`allowed_operations: [delivery.dispatch_next, delivery.record_receipt, delivery.mark_unknown, telegram.send_payload]`
và `network_scope: [telegram_bot_api]`.

**Vì sao là actor riêng chứ không phải nới `ACT-server-domain-service`:** gộp vào actor domain chung buộc actor
chung khai `network_scope: [telegram_bot_api]`, tức cấp quyền chạm Internet cho **mọi** domain service — đúng thứ
`NET-P1` cấm. `ACT-server-domain-service.network_scope` do đó **vẫn rỗng**, và nay có một dòng khẳng định rằng
rỗng là có chủ đích, kèm liệt kê hai đường ra ngoài duy nhất của server. Mọi actor khác giữ nguyên `network_scope`.

Khối `network_scope_declared_value` cung cấp **giá trị khai báo** mà `CR-PC10-03` cần:

| Trường | Nội dung |
| --- | --- |
| `host_class` | `telegram_bot_api` — một lớp host, không phải danh sách IP |
| `capability_guarded_by_capability_denied_vi` | `CAPABILITY_DENIED` trên `telegram.send_payload` bảo vệ đúng một capability: mở kết nối tới `telegram_bot_api` và gửi payload tới một recipient. Bị từ chối khi (a) người gọi không phải dispatcher, (b) recipient không phải chat đã liên kết ở generation hiện tại, (c) payload không truy được về một `outbox_intent` đã commit |
| `i11_oracle_vi` | Ba phép đếm: outbound tới `telegram_bot_api` từ tiến trình **không phải** dispatcher = 0; recipient khác chat đã liên kết = 0; `telegram.send_payload` không truy được về intent đã commit = 0 |
| `restore_guard_vi` | Ở `recovery_required` mã trả là `RESTORE_UNVERIFIED`, **không** phải `CAPABILITY_DENIED` — "chưa được phép lúc này" khác "đường đi không tồn tại" |

Bốn `denied_capabilities` mới (`DC-DSP-01…04`): recipient sai ⇒ `CAPABILITY_DENIED`; storage không `healthy` ⇒
`STORAGE_WRITE_FAILED`; tự gửi lại part `unknown` ⇒ `TELEGRAM_SEND_UNCERTAIN`; replay outbox generation cũ ⇒
`RESTORE_UNVERIFIED`.
Dispatcher khai `secret_scope: none`: nó **không** giữ bot token mà gọi `telegram.send_payload` của adapter, nơi
duy nhất đọc token — để một lỗi trong logic dispatch không biến thành lộ token.

## G.4 Evidence

`python3 …/w2/validate_pc01_v2.py` · 2026-09-06T19:20Z · **exit 0**, `== NO FAILURES ==`, 0 WARN.
`validate_pc01.py` (v1) **exit 0** · `validate_pc08.py` **exit 0** · `gate_fixtures.py` (sáu thư mục fixture)
**exit 0** — chạy cả ba vì actor và enum mới có thể ảnh hưởng chéo.

| Check mới | Kết quả |
| --- | --- |
| `EV-02x` mọi operation trả `CAPABILITY_DENIED` đều có actor khai nó | **3/3 PASS** — trước FIX6 `telegram.send_payload` là orphan, đúng như `CR-PC10-03` mô tả |
| `EV-02y` dispatcher khai đủ hai operation + `telegram_bot_api` + oracle I11 | **PASS** |
| `EV-02z` `telegram_bot_api` chỉ xuất hiện ở ba actor Telegram | **PASS** — `['ACT-delivery-dispatcher','ACT-telegram-ingress','ACT-telegram-linked-chat']`; không actor nào khác bị nới |
| `EV-03a` `stop_reason` có `rate_limited`; `worker.report_stop` mang `RATE_LIMITED` | **PASS** |
| `EV-05` set-comparison với `entities.yaml` `209cf03e…` (60 entity) | forward **0**, mismatch **0**, reverse **0** |

Vẫn **85 operation** và **99 allowed_edges**: FIX6 không thêm/bớt operation hay cạnh nào — actor không phải module.

## G.5 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| `ACT-delivery-dispatcher` là **actor**, không phải module: `modules.yaml` không đổi và `MOD-delivery-service` vẫn là chủ sở hữu `delivery.dispatch_next`. Nếu PC09 muốn một `MOD-*` riêng cho dispatcher thì đó là thay đổi topology, cần packet khác. | OPEN |
| `RATE_LIMITED` đã có trong `errors.yaml`; nhưng `RATE_LIMITED.operations` ở phía PC03 có liệt kê `worker.report_stop` hay không thì **PC03 sở hữu** — nếu chưa, hai file mô tả cùng mã ở mức chi tiết khác nhau. | OPEN |
| `rate_limited` là giá trị `stop_reason` thứ bảy; hàng transition trong `run.yaml` do PC03 thêm song song. Cho tới lúc đó `outcome: partial` cho nhánh này mới chỉ được khai ở PC01. | OPEN |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06`, `SC44` chờ anchor + scenario, guard `blocked → queued` chờ PC03. |

---

# ADDENDUM — PKT-PC01-FIX7

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX7` · authority `AUTH-COORD-PC01-FIX7` · lease `LEASE-PC01-e8` (fencing 8) |
| expires_at | 2026-09-07T12:00Z |
| trigger | Rulings FIX5 **R5-01** (bảng mã lỗi cho cạnh bị cấm), **R5-02** (fixture SC49), **R5-03** (REQ-S6.1-01) |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T00:16Z / 2026-09-07T00:23Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T00:23Z |

Ghi chú tiếp nối: lượt trước bị API rate limit cắt **trước khi ghi bất kỳ byte nào**. Kiểm lại lúc 00:16Z xác nhận
đúng như Coordinator nói — không file nào đổi, không có `acceptance/fixtures/boundary/`, không addendum. Baseline
của lượt này là bytes sau FIX6, không phải một trạng thái dở dang.

## H.1 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/modules.yaml` | MODIFY | `89b348aa8d3f89d38c945a7f15a8fe2c46e2619a1226649e4633bf30367264f5` / 75794 | `fa7af49490a2e6da625e8282df0dee400078a099a6cf6b71352439d3dbe833d0` / 98983 |
| `contracts/ops/deployment.md` | MODIFY | `39b1a7103f29895c079e08e732a10f7d380e665c4498f1bc83faeadb09e6a17c` / 17314 | `3fb309fb29a4bd7773b101085021942ef647133887c6f064d87730203a356c48` / 17750 |
| `acceptance/fixtures/boundary/README.md` | CREATE (ABSENT) | — | `81d8d2fa3de8f9f4982f21fb4904b244c52018f94d6ada069af2239d74f79c17` / 6437 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | CREATE (ABSENT) | — | `533f12d54b0b2c280af555735ce0d6f135d60a3c413fc8a713a39a137d6bf021` / 27304 |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `525119ea71b75560cb3f383dd931934d771c1d004e2b25eeeee48f04b1ffa663` / 64904 | ghi ở thông điệp bàn giao |

Directory mới: `acceptance/fixtures/boundary/`. Không ghi vào `evidence/tools/`; `e0_check.py` được **copy sang
scratch dir** và chạy read-only từ đó. Sources không đổi (00:16Z và 00:22Z).

## H.2 R5-01 — 36/36 cạnh bị cấm có oracle mã lỗi

Trước FIX7: 10 `denied_cases` cho 36 `forbidden_edges` ⇒ `E0-10b-denied-edge-oracle` FAIL với 26 vi phạm.
Sau FIX7: **36 `denied_cases`**, khớp 1–1 với 36 `forbidden_edges`. `NC-11` … `NC-36` là mới; mỗi cái có
`attempted_edge`, `expected_error_code`, `expected_state_vi` (không hàng nào đổi, có audit, 0 outbound),
`enforcement`, `enforcement_detail_vi`, `forbidden_edge_ref`, `invariant_refs` và **`scenario_refs: [SC49]`**.
`SC49` cũng được thêm vào `scenario_refs` của 10 case cũ.

Phân bố mã: `CAPABILITY_DENIED` 15 · `UNAUTHORIZED` 9 · `FORBIDDEN_EDGE` 7 · `UNAUTHORIZED_COMMAND` 3 ·
`RESTORE_UNVERIFIED` 2.

**Một case cũ bị sửa:** `NC-09` (scheduler → delivery) đổi từ `UNAUTHORIZED` sang **`FORBIDDEN_EDGE`**. Bảng R5-01
nêu đích danh "scheduler → Telegram" làm ví dụ của `FORBIDDEN_EDGE`: đây là lời gọi **trong cùng tiến trình** qua
cạnh không có trong `allowed_edges`, không phải request HTTP sai lớp principal. Lý do đổi ghi tại chỗ trong
`error_code_changed_vi`.

**Phân biệt được áp dụng nhất quán:** cùng một callee `MOD-data-store` cho ba mã khác nhau tùy **vì sao** không đi
được — `FE-05`/`FE-15` (máy cá nhân: không driver, không tuyến) ⇒ `CAPABILITY_DENIED`; `FE-29` (adapter cùng tiến
trình server: vi phạm import/repository-scope) ⇒ `FORBIDDEN_EDGE`. Nếu gộp cả hai thành một mã thì người vận hành
mất đúng thông tin cần để sửa.

**Hai mã ngoài bảng bốn dòng**, ghi rõ trong `default_deny.error_code_refinement_vi` và gửi kèm `CR-PC01-09`:
`UNAUTHORIZED_COMMAND` (FE-30/31/33 — ingress Telegram bắt buộc **bỏ im lặng**, trả `UNAUTHORIZED` cho chat là tự
xác nhận bot tồn tại) và `RESTORE_UNVERIFIED` (FE-34/35 — chặn bởi **guard trạng thái**, cùng caller **được phép**
sau khi đối soát xong; "chưa được phép lúc này" khác "đường đi không tồn tại").

## H.3 R5-02 — fixture SC49

`acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`: **36 event**, một cho mỗi `FE-nn`, mỗi cái mang
`edge_assertion: forbidden`, `denied_case_ref`, `expected_error_code`, `enforcement`, và ghi rõ caller dùng
**credential hợp lệ** — ca này kiểm ranh giới **quyền**, không kiểm xác thực. Oracle: tổng `COUNT(*)` mọi bảng
trước/sau bằng nhau, outbound ngoài chính lời gọi = 0, mã lỗi bằng giá trị đã pin.

**Năm event mang hai mã** (`expected_error_code_edge_class` + `expected_error_code`): FE-30/31/33 và FE-34/35.
Gate `fixture-actor-edge` đọc mã **lớp**; oracle nghiệp vụ đọc mã **chính xác**. Ghi cả hai thay vì chọn một, vì
ép năm ca này về đúng ba mã sẽ nói dối về hành vi quan sát được, còn bỏ mã lớp sẽ để gate không đọc được.

**Năm event có `operation: null`** — cạnh tới tài nguyên/tiến trình không tương ứng operation nào của
`ports.yaml`; mỗi cái mang `operation_absent_reason_vi`. Đáng chú ý `FE-03`: lần dựng đầu tôi gán
`settings.test_provider`, gate bắt được vì đó là cạnh **hợp lệ** (`MOD-web-ui → MOD-settings-service`). Cái bị cấm
là trang web tự mở socket tới provider, không phải operation đó. Sửa ở **cả** fixture lẫn `NC-13`.

README nêu nguyên văn quy tắc R4-01, bảng R5-01, hai mã tinh chỉnh, và nói thẳng rằng thư mục này khẳng định về
**cạnh và mã lỗi** chứ không về hàng dữ liệu (nên 0 cột thuộc phạm vi field gate — sạch vì không có gì để kiểm,
không phải vì đã kiểm).

## H.4 R5-03 — REQ-S6.1-01

`contracts/ops/deployment.md` thêm `REQ-S6.1-01` vào `requirement_refs` và một đoạn nói bảng §2 hiện thực nó: mỗi
dòng phân vai của SRC-SPEC §6.1 có đúng một module, cột "Runtime" là nơi chạy mà đặc tả quy định.

## H.5 Evidence

| Gate | Kết quả |
| --- | --- |
| `validate_pc01_v2.py` | **exit 0**, `== NO FAILURES ==`, 0 WARN. Ba check mới: `EV-03b` 36/36 cạnh có denied case pinned; `EV-03c` 36/36 mang `SC49` + enforcement; `EV-03d` mọi mã thuộc bảng R5-01 hoặc là tinh chỉnh đã ghi |
| `validate_pc01.py` (v1) | **exit 0** |
| `gate_fixtures.py` (tám thư mục) | **exit 0** — 82 file, 285 event, 1455 cột, 141 chú thích `_`, 4 `pending_cr`, **33 event forbidden**, unresolved **0**, event/edge problem **0** |
| `evidence/tools/e0_check.py` (copy read-only, `--repo`) | `E0-10a` **PASS** 36/0 · `E0-10b-denied-edge-oracle` **PASS 36/0** (trước FIX7 là FAIL 26) · `E0-14-fixture-actor-edge` **PASS** 398/0. Tổng: 19 check, PASS 18, FAIL 1 |

Một FAIL còn lại là `E0-07-id-refs`: `SC54` được trích trong `evidence/handoffs/PC00-handoff.md` mà chưa định nghĩa
trong `acceptance/scenarios.yaml` — **file của W1**, không thuộc packet này.

Ghi trung thực về thứ tự chạy: lần chạy `e0_check` đầu báo `E0-14` FAIL 5 vi phạm, đúng năm event hai mã ở H.3;
tôi sửa bằng cách **thêm mã lớp**, không bằng cách đổi mã quan sát được. Lần chạy sau: 0.

## H.6 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `CR-PC01-09` (mới → Coordinator) | Phê chuẩn hai mã ngoài bảng R5-01 (`UNAUTHORIZED_COMMAND` cho ingress Telegram, `RESTORE_UNVERIFIED` cho guard trạng thái) và quy ước **hai mã** trong fixture SC49. Nếu Coordinator muốn đúng bốn mã, năm `denied_cases` và năm event phải đổi — và `NC-06`/`NC-10` đã qua hai vòng audit với mã hiện tại. | OPEN |
| Mã lỗi cho 26 cạnh mới là **suy luận của PC01** từ bảng R5-01, không phải quan sát | Chúng chưa từng được thực thi. `E0-10b` chứng minh **có** một mã được pin, không chứng minh mã đó **đúng**. | OPEN |
| `E0-07` FAIL (SC54, PC00-handoff) | Ngoài phạm vi; báo để W1 xử lý. | OPEN |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06`, guard `blocked → queued` chờ PC03. |

---

# ADDENDUM — PKT-PC01-FIX8

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX8` · authority `AUTH-COORD-PC01-FIX8` · lease `LEASE-PC01-e9` (fencing 9) |
| expires_at | 2026-09-07T14:00Z |
| trigger | Ruling R4-02 mở rộng: event có `operation: null` **phải** mang `event_type`; gate dùng chung thực thi |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T00:38Z / 2026-09-07T00:40Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T00:40Z |

## I.1 Hash mới của fixture boundary — **PC10 phải re-pin**

> `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`
> **sha256 `795d19a6ff080817487ed470208f3ec4905372a28c1eb2b66e53d3ae55eda8ee` · 29283 bytes**
> (trước FIX8: `533f12d54b0b2c280af555735ce0d6f135d60a3c413fc8a713a39a137d6bf021` · 27304 bytes)
>
> 18 task card của PC10 pin hash cũ. Không card nào có thể pass kiểm baseline cho tới khi được re-pin sang hash
> trên. Nội dung **nghiệp vụ** không đổi — vẫn 36 event, cùng caller, cùng mã lỗi; chỉ thêm khóa `event_type` cho
> năm event và một đoạn README.

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | MODIFY | `533f12d54b0b2c280af555735ce0d6f135d60a3c413fc8a713a39a137d6bf021` / 27304 | `795d19a6ff080817487ed470208f3ec4905372a28c1eb2b66e53d3ae55eda8ee` / 29283 |
| `acceptance/fixtures/boundary/README.md` | MODIFY | `81d8d2fa3de8f9f4982f21fb4904b244c52018f94d6ada069af2239d74f79c17` / 6437 | `5c8fc315a4998402bf2d7fe8740221d9671f785c63efe7f18391fc889419e1b9` / 7293 |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `3debe3ed3971968ebda793c7d2d662fc7801500c4b47fd3733cda55d65acd8d7` / 73257 | ghi ở thông điệp bàn giao |

Sources không đổi (00:38Z và 00:39Z). Không file nào khác bị chạm — packet nói rõ "nothing else changes".

## I.2 Nội dung

Năm event có `operation: null` nay mang `event_type` cùng `event_type_reason_vi`:

| seq | Cạnh | `event_type` | Vì sao |
| --- | --- | --- | --- |
| 8 | FE-08 `MOD-x-collector → MOD-analysis-worker` | **`in_process_call`** | Lời gọi mã/IPC cục bộ trên cùng máy, không qua API server, qua một cạnh không có trong `allowed_edges`. Oracle là import/dependency rule + phân tích tĩnh. |
| 3 | FE-03 `MOD-web-ui → EXT-ai-provider-api` | `local_observation` | Trang web tự mở socket tới endpoint provider; quan sát tại ranh giới tiến trình/mạng của trình duyệt. |
| 17 | FE-17 `MOD-ai-adapter → EXT-x-web` | `local_observation` | Adapter cố điều khiển trình duyệt; quan sát bằng process capability và đếm kết nối. |
| 20 | FE-20 `MOD-research-connector → …` | `local_observation` | Server không cài Chrome; quan sát bằng phân tích tĩnh import + process capability. |
| 21 | FE-21 `MOD-research-connector → EXT-chrome-profile` | `local_observation` | Profile Chrome là tài nguyên trên máy cá nhân; server không có đường tới. |

Hai giá trị **khớp với cách bảng R5-01 phân loại mã lỗi**: `in_process_call` đi cùng `FORBIDDEN_EDGE`,
`local_observation` đi cùng `CAPABILITY_DENIED`. Không phải trùng hợp — cùng một câu hỏi ("cái gì thiếu: một cạnh
hay một capability?") quyết định cả hai trường, nên nếu về sau hai trường lệch nhau thì đó là dấu hiệu một trong hai
sai.

README nêu bảng hai giá trị, oracle tương ứng và quy tắc "31 event còn lại có `operation` thật nên không mang khóa
này". Fixture cũng mang `event_type_convention_vi` ở cấp tài liệu để người đọc chỉ mở file JSON vẫn hiểu quy ước.

## I.3 Gate

| Gate | Kết quả |
| --- | --- |
| `…/scratchpad/w3/check_actor_edges_all.py` (gate dùng chung của W3, tám thư mục) | **RESULT: PASS (0 fail)**, exit 0 — `boundary` 31 event có operation được kiểm cạnh, 5 event `null` được chấp nhận nhờ `event_type`; tổng 301 event |
| `…/scratchpad/w3/fixture_field_gate.py` (field gate của W3) | **TOTAL unresolved = 0**, exit 0 |
| `…/scratchpad/w2/gate_fixtures.py` (gate của tôi, R4-01 + R4-02) | **exit 0** — 86 file · 318 event · 1939 cột · 179 chú thích `_` · 34 event forbidden · unresolved **0** · event/edge problem **0** |
| `evidence/tools/e0_check.py` (copy read-only) | `E0-14-fixture-actor-edge` **PASS 449/0** · `E0-08-contract-header` **PASS 142/0**; tổng 19 check: PASS 18, FAIL 1 |

## I.4 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| **PC10 re-pin** | 18 task card pin hash cũ của fixture boundary. Hash mới ở §I.1. | OPEN |
| `CR-PC01-10` (mới) | **Phát hiện ngoài phạm vi, không sửa.** `NC-08` có `forbidden_edge_ref: FE-20` (`MOD-research-connector → EXT-x-web`) nhưng `attempted_edge.callee` của nó là `EXT-chrome-profile` — tức là nó mô tả **FE-21**. Hệ quả: trong fixture, seq 20 và seq 21 hiện cùng một callee, nên FE-20 (chạm X) **không có** event mô tả đúng cạnh của nó, dù `E0-10b` vẫn PASS vì nó chỉ kiểm *có* một case được pin. Sửa cần đụng `contracts/modules.yaml` — ngoài grant của packet này ("nothing else changes"). Đề nghị một packet nhỏ: đổi `NC-08.attempted_edge.callee` thành `EXT-x-web`, hoặc trỏ `NC-08` sang `FE-21` và viết case mới cho `FE-20`. | OPEN |
| `E0-07-id-refs` FAIL | `SC54` nay bị trích ở **năm** nơi (`PC00`, `PC01`, `PC05`, `PC08` handoff và `precode/review.md`) mà vẫn chưa định nghĩa trong `acceptance/scenarios.yaml`. Con số tăng vì mỗi gói **báo cáo** khiếm khuyết đó, và bộ kiểm coi mọi lần nhắc là một citation. Cần W1/PC09 hoặc định nghĩa SC54, hoặc cho `E0-07` bỏ qua văn xuôi trong handoff nói *về* một id chưa định nghĩa. | OPEN |

---

# ADDENDUM — PKT-PC01-FIX9

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX9` · authority `AUTH-COORD-PC01-FIX9` · lease `LEASE-PC01-e10` (fencing 10) |
| expires_at | 2026-09-07T14:00Z |
| trigger | `CR-PC01-10` (do chính PC01 nêu ở addendum FIX8) |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T00:41Z / 2026-09-07T00:43Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T00:43Z |

## J.1 Hash mới — **hai file đều bị card pin, PC10 phải re-pin**

> `contracts/modules.yaml` → **`9846a2be3d5497f50b43d9e001e8dde609a8eb31ed9b281cad0d8c4175524757`** · 100130 bytes
> `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` →
> **`ffab4679078e8d93227bb2751743482b44981ec6a84de1f404a389f59ec0213e`** · 29904 bytes
> (fixture đã đổi hash hai lần liên tiếp: FIX8 `795d19a6…`, FIX9 `ffab4679…` — re-pin **một lần** sang giá trị FIX9.)

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/modules.yaml` | MODIFY | `fa7af49490a2e6da625e8282df0dee400078a099a6cf6b71352439d3dbe833d0` / 98983 | `9846a2be3d5497f50b43d9e001e8dde609a8eb31ed9b281cad0d8c4175524757` / 100130 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | MODIFY | `795d19a6ff080817487ed470208f3ec4905372a28c1eb2b66e53d3ae55eda8ee` / 29283 | `ffab4679078e8d93227bb2751743482b44981ec6a84de1f404a389f59ec0213e` / 29904 |
| `acceptance/fixtures/boundary/README.md` | MODIFY | `5c8fc315a4998402bf2d7fe8740221d9671f785c63efe7f18391fc889419e1b9` / 7293 | `201b2e2c3d77f2d70e3e263d45d8dfb440bc266c8fbaac76260e151bb09dc583` / 8582 |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `5ffbe3d47dcd44cacd9770577494e1bcaa2e4eb453aa1a5c260b1c53157e162c` / 79325 | ghi ở thông điệp bàn giao |

Sources không đổi (00:40Z và 00:42Z). Số operation (85), số allowed_edges (99), số forbidden_edges (36) và số
denied_cases (36) **không đổi** — FIX9 chỉ sửa việc case nào mô tả cạnh nào.

## J.2 Sửa gì

`NC-08` luôn mang `attempted_edge.callee: EXT-chrome-profile` nhưng lại trỏ `forbidden_edge_ref: FE-20`
(`MOD-research-connector → EXT-x-web`), trong khi `NC-24` mô tả **cùng** cạnh Chrome lần thứ hai. Hệ quả: `FE-20`
không có case nào mô tả đúng cạnh của nó, và trong fixture hai event seq 20/21 trỏ cùng một callee.

| Sau FIX9 | Cạnh | Nội dung | Mã | Oracle |
| --- | --- | --- | --- | --- |
| `NC-08` | **FE-21** `→ EXT-chrome-profile` | Connector mở profile Chrome — tài nguyên trên **máy cá nhân** | `CAPABILITY_DENIED` | Process capability; image server không cài Chrome |
| `NC-24` | **FE-20** `→ EXT-x-web` | Connector chạm thẳng **nguồn X trên mạng** | `CAPABILITY_DENIED` | Đếm kết nối tới host của X từ container server = 0; `network_egress` chỉ có arXiv + OpenAlex |

Hai cách thất bại khác nhau nên cần hai case, không phải hai bản sao của một case. Lý do đổi được ghi tại chỗ
(`forbidden_edge_ref_corrected_vi` trên NC-08, `repurposed_vi` trên NC-24) để người đọc sau không tưởng là lỗi
đánh máy. Không ID nào bị thêm hay xoá — tránh làm gãy tham chiếu đang có.

Fixture: seq 20 nay là `FE-20` (`EXT-x-web`, `denied_case_ref: NC-24`), seq 21 giữ `FE-21`
(`EXT-chrome-profile`, `denied_case_ref: NC-08`); cả hai giữ `event_type: local_observation` với lý do riêng.

## J.3 Phép kiểm mới: song ánh cạnh ↔ case ↔ event

Thêm vào `…/w2/gate_fixtures.py`. Nó kiểm **nội dung**, không chỉ **số lượng**:

1. mỗi `forbidden_edges[].id` có **đúng một** `denied_cases[]` (không 0, không 2);
2. `attempted_edge.(caller, callee)` của case **bằng** định nghĩa cạnh;
3. mỗi cạnh có **đúng một** event trong fixture sweep, không event thừa cho cạnh lạ;
4. `(actor, callee)` của event bằng định nghĩa cạnh;
5. `denied_case_ref` và `expected_error_code` của event bằng của case;
6. event có `operation: null` phải có `event_type`.

Kết quả: **forbidden edges 36 · denied cases 36 · boundary events 36 · violations 0.**

Đây là lỗ hổng mà `E0-10b` để lọt theo thiết kế: nó hỏi "có một case được pin hay không", không hỏi "case có mô tả
đúng cạnh hay không". Cả hai check đều cần; cái mới không thay cái cũ. Đề nghị PC09 đưa mục (2) và (4) vào
`e0_check.py` như một check riêng — `CR-PC01-11`.

## J.4 Gate

| Gate | Kết quả |
| --- | --- |
| `…/w2/gate_fixtures.py` | **exit 0** — bijection 36/36/36, violations 0; 86 file · 318 event · 1939 cột · 179 chú thích `_` · 34 forbidden · unresolved 0 · event/edge problem 0 |
| `…/w2/validate_pc01_v2.py` | **exit 0**, `== NO FAILURES ==`, 0 WARN |
| `…/w3/check_actor_edges_all.py` | **RESULT: PASS (0 fail)**, exit 0 |
| `…/w3/fixture_field_gate.py` | **TOTAL unresolved = 0**, exit 0 |
| `evidence/tools/e0_check.py` (copy read-only) | `E0-10a` **PASS 36/0** · `E0-10b` **PASS 36/0** · `E0-14` **PASS 449/0**; tổng 19 check: PASS 18, FAIL 1 |

FAIL còn lại vẫn là `E0-07-id-refs` (`SC54` chưa định nghĩa, bị trích ở nhiều handoff) — ngoài phạm vi PC01.

## J.5 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| **PC10 re-pin** | `contracts/modules.yaml` và fixture boundary đều đổi hash; giá trị mới ở §J.1. | OPEN |
| `CR-PC01-11` (mới → PC09) | Đưa phép so **nội dung** cạnh↔case↔event vào `e0_check.py`. Không có nó, một case trỏ sai cạnh vẫn PASS mọi check hiện hành — đúng như `CR-PC01-10` đã chứng minh. | OPEN |
| `CR-PC01-10` | **Đóng** bởi packet này. | CLOSED (chờ xác nhận) |
| `E0-07` / `SC54` | Ngoài phạm vi; cần W1/PC09. | OPEN |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06/-09`. Mọi fixture vẫn `NOT_RUN`. | — |

---

# ADDENDUM — PKT-PC01-FIX10

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX10` · authority `AUTH-COORD-PC01-FIX10` · lease `LEASE-PC01-e11` (fencing 11) |
| expires_at | 2026-09-07T16:00Z |
| trigger | AUDIT_REPORT `PKT-A2-R1` findings **F-A2R1-04/-05/-06/-09** + rulings FIX6 |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T01:11Z / 2026-09-07T01:16Z |
| next actor | `Coordinator` (verify: `auditor-A2`, PKT-A2-R2, epoch 5) · lease_released_at 2026-09-07T01:16Z |

## K.1 Hash mới — **cả bốn file đều bị card pin**

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/modules.yaml` | MODIFY | `9846a2be3d5497f50b43d9e001e8dde609a8eb31ed9b281cad0d8c4175524757` / 100130 | **`5137a0d2b4030886115e649aa12378282f15ffb4268cc5bfe42a002f7d03ee43`** / 103511 |
| `contracts/ports.yaml` | MODIFY | `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a` (FIX4) → `87c95da4…` (FIX6) | **`d4dd6e34695d810d2bd6818712077e2f943892491fff57bfb1feef9cd723f8ee`** / 124906 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | MODIFY | `ffab4679078e8d93227bb2751743482b44981ec6a84de1f404a389f59ec0213e` / 29904 | **`5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0`** / 31529 |
| `acceptance/fixtures/boundary/README.md` | MODIFY | `201b2e2c3d77f2d70e3e263d45d8dfb440bc266c8fbaac76260e151bb09dc583` / 8582 | **`6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba`** / 10598 |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `41495ee9050b0ad90bb0be962d19b24fa04d0c434d7ffff79307d84abd55f9dc` / 85390 | ghi ở thông điệp bàn giao |

Sources không đổi (01:11Z và 01:15Z). Số operation vẫn **85**, allowed_edges **99**, forbidden_edges **36**,
denied_cases **36**.

## K.2 F-A2R1-05 — operation không thể phục vụ được

`FE-26` là `MOD-scheduler → MOD-x-collector`. `NC-28` và event seq 26 ghi `operation: worker.claim_assignment` —
operation đó do **`MOD-job-service`** sở hữu và caller duy nhất là **`MOD-x-collector`**, tức nó chạy **ngược
chiều**. Máy cá nhân không lắng nghe cổng nào, nên oracle "gọi nó rồi khẳng định lỗi" **không chạy được** cho đúng
cạnh bảo vệ "không gì gọi vào máy cá nhân". Chính `enforcement_detail_vi` của case đã nói "không có đích để gọi
tới" trong khi trường bên cạnh vẫn ghi một đích.

Sau FIX10: `operation: null`, `event_type: in_process_call`, `attempted_action_vi` ("scheduler **đẩy** một
assignment xuống collector"), `operation_absent_reason_vi`, và `expected_error_code` đổi
`CAPABILITY_DENIED` → **`FORBIDDEN_EDGE`** — cái vắng mặt là **cạnh** (collector **kéo** việc theo D11), không
phải một capability của scheduler. Lý do đổi ghi tại chỗ.

**Quy tắc được viết ra và được kiểm** (`default_deny.attempted_edge_operation_rule_vi`, mới):
(a) callee `MOD-*` ⇒ `operation` chỉ được mang tên khi **chính callee sở hữu** nó; (b) callee `EXT-*` ⇒ tên là
**port nội bộ mà kẻ vi phạm đang cố tạo ra hiệu ứng của nó** (sáu case: NC-04, NC-07, NC-13, NC-17, NC-25, NC-29);
(c) còn lại ⇒ `null` + `event_type` + `operation_absent_reason_vi`. Quy ước (b) trước FIX10 **không được ghi ở
đâu** — auditor nói đúng; nay nó nằm trong hợp đồng chứ không trong đầu người viết.
Thêm `operation_absent_reason_vi` cho **NC-08, NC-15, NC-22, NC-24** (auditor nêu), nên cả sáu case `null` nay
đồng dạng.

**Gate mở rộng** (`…/w2/gate_fixtures.py`): với mỗi cạnh, nếu case **hoặc** event mang tên operation và callee là
`MOD-*` thì owner của operation phải **bằng** callee; callee `EXT-*` thì tên phải tồn tại trong `ports.yaml`;
`operation: null` phải kèm `event_type` **và** `operation_absent_reason_vi`, ở **cả** case lẫn event. Đây là lần
thứ ba lớp lỗi "đếm đủ, nội dung sai" xuất hiện (FE-20/21 ở FIX9, rồi cái này), nên phép kiểm nhắm vào **nội
dung**, không vào số lượng.

## K.3 F-A2R1-04 — CR-PC01-09 APPROVED

Từ "xin Coordinator phê chuẩn / đang chờ phê chuẩn" đổi thành **"đã được Coordinator phê chuẩn (ruling FIX6,
A2-R1)"** ở `contracts/modules.yaml` `default_deny.error_code_refinement_vi` và ở
`acceptance/fixtures/boundary/README.md`. `UNAUTHORIZED_COMMAND` và `RESTORE_UNVERIFIED` nay là mã hợp lệ cho
denied case ngoài bảng bốn dòng R5-01 khi đặc tả gọi tên chúng.

## K.4 F-A2R1-06 — `save.create.error_codes` += `CONFLICT`

`CONFLICT` (đã đăng ký) là mã cho va chạm Save đồng thời từ hai kênh: transaction thua trả `CONFLICT` **và** hàng
đã tồn tại, không tạo bản thứ hai (`UNIQUE(owner, target)`; AC-13/SC13/I08). Thay cho `SAVE_ALREADY_EXISTS` —
một mã chưa bao giờ có trong `contracts/errors.yaml`. PC02 chỉnh prose của `entities.yaml` song song.

## K.5 F-A2R1-09 — năm operation thiếu trường

| Operation | Thiếu | Điền |
| --- | --- | --- |
| `auth.logout` | `scenario_refs` | `[SC40, SC51]` — SC51 mặt dương (đăng nhập trong thiết lập), SC40 mặt âm (sau logout, request mang session đã thu hồi phải rơi vào nhánh của SC40) |
| `auth.get_session` | `scenario_refs` | `[SC40, SC51]`, cùng lý do |
| `save.export` | `scenario_refs` | `[SC12]` — export đọc chính `saved_snapshot` mà SC12 khẳng định bất biến. Ghi rõ: **không** có SC riêng vì operation `deferred_p1` theo REQ-OQ10; đó là có chủ đích, không phải thiếu sót |
| `research.get_connector_health` | `error_codes` | `[INTERNAL]` + lý do: `UNAUTHORIZED` không áp dụng (port `internal_only`), `VALIDATION_ERROR` không áp dụng (không tham số), và trạng thái nguồn suy giảm là **giá trị trả về** `ok\|degraded\|unavailable`, không phải lỗi của lời gọi |
| `health.get_liveness` | `error_codes` | `[INTERNAL]` + lý do: scope `public_minimal` theo thiết kế; không body/tham số; và `STORAGE_WRITE_FAILED` **không** phải mã của nó — endpoint này phải trả lời được kể cả khi DB không ghi được (SRC-PLAN §8.4), đó chính là điểm của kênh health độc lập |

Đo lại: **0** operation thiếu `scenario_refs`, **0** thiếu `error_codes` (trên 85 operation).

## K.6 Gate

| Gate | Kết quả |
| --- | --- |
| `…/w2/gate_fixtures.py` | **exit 0** — bijection + callee-ownership: forbidden edges 36 · denied cases 36 · boundary events 36 · **violations 0**; corpus: 86 file · 318 event · unresolved 0 · event/edge problem 0 |
| `…/w2/validate_pc01_v2.py` | **exit 0**, `== NO FAILURES ==`, 0 WARN |
| `…/w3/check_actor_edges_all.py` | **RESULT: PASS (0 fail)**, exit 0 |
| `…/w3/fixture_field_gate.py` | **TOTAL unresolved = 0**, exit 0 |
| `evidence/tools/e0_check.py` (copy read-only) | `E0-10a` **PASS 36/0** · `E0-10b` **PASS 36/0** · `E0-14` **PASS 448/0** (448 thay vì 449 vì seq 26 không còn mang operation — đúng như mong đợi) |

Hai FAIL còn lại của `e0_check` đều **ngoài phạm vi PC01**: `E0-06` (`precode/decision-register.md` trích
`REQ-S8.4-01`, id mà chính PC01 đã bỏ ở FIX3 — W1 cần cập nhật) và `E0-07` (`SC54` chưa định nghĩa, bị trích ở bốn
handoff).

## K.7 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| **PC10 re-pin** | Bốn file đổi hash; giá trị mới ở §K.1. `ports.yaml` đổi lần đầu kể từ FIX6. | OPEN |
| `CR-PC01-12` (mới → W1/PC00) | `precode/decision-register.md` vẫn trích `REQ-S8.4-01` — id không tồn tại, đã được PC01 thay bằng `REQ-S9.3-08`/`REQ-S8.3-0x` từ FIX3 theo `CR-PC03-01`. Đang làm `E0-06` FAIL. | OPEN |
| `CR-PC01-11` | Vẫn mở: đưa phép so **nội dung** (callee-ownership + caller/callee equality) vào `e0_check.py`. Ruling FIX6 giao W6 làm trong `E0-10b`; gate của W2 đã có. | OPEN |
| `SC54` / `E0-07` | Ngoài phạm vi; cần W1/PC09. | OPEN |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06`. Mọi fixture vẫn `NOT_RUN`: gate chứng minh mô tả nhất quán, không chứng minh guard chạy. | — |

---

# ADDENDUM — PKT-PC01-FIX11

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX11` · authority `AUTH-COORD-PC01-FIX11` · lease `LEASE-PC01-e12` (fencing 12) |
| expires_at | 2026-09-07T18:00Z |
| trigger | Ruling FIX7 hàng `SAVE_ALREADY_EXISTS` + thiết kế `E0-04b`/`E0-04c` |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T01:33Z / 2026-09-07T01:36Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T01:36Z |

## L.1 Hash mới — **ba file card-pinned đổi**

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/ports.yaml` | MODIFY | `d4dd6e34695d810d2bd6818712077e2f943892491fff57bfb1feef9cd723f8ee` / 124906 | **`93ba159856a4821ad46d1d05199987f475c8ae5603d8f9200e1418b0e2eab42e`** / 126182 |
| `contracts/capabilities.yaml` | MODIFY | `cb1f8b68df3523a1d14578b3f83556b4addd61f4640d6dae624a498d551db499` / 45652 | **`fae5891cff5ff25757f168d8182111fa4fc6b49f6b851ac7cc07105fef952cf7`** / 45672 |
| `contracts/ops/deployment.md` | MODIFY | `3fb309fb29a4bd7773b101085021942ef647133887c6f064d87730203a356c48` / 17750 | **`7e1c03776b4c8be20f596a0317ea1c79429cf4ecaa78fadc1f0ec3e5158088f5`** / 17759 |
| `contracts/modules.yaml` | **NO CHANGE** | `5137a0d2b4030886115e649aa12378282f15ffb4268cc5bfe42a002f7d03ee43` | quét không tìm thấy token nào cần sửa trong file này |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `c347b139ee79dcf90bc55d192fc46d84c83ff89033364328e592dbc2be8051f8` / 93840 | ghi ở thông điệp bàn giao |

Sources không đổi. Đối chiếu với `contracts/data/entities.yaml` sha256
**`79a746f18d3536ee4d34e4e7a6931df5d77ed6ad163f394a157dec6db1f348f5`** (60 entity) — W3 đang mở rộng file này song
song và nó đã đổi hash **một lần** giữa hai lần quét của tôi (`bdce5fc1…` → `79a746f1…`); kết quả quét dưới đây
gắn với hash sau.

## L.2 Token tìm thấy và xử lý

Quét **prose string** (không phải khóa cấu trúc) của bốn file PC01 bằng `…/w2/scan_tokens.py`.

**SCREAMING_SNAKE không phân giải được: 1 → sửa 1, còn 0.**

| Token | Ở đâu | Xử lý |
| --- | --- | --- |
| `SAVE_ALREADY_EXISTS` | `ports.yaml` `save.create.error_note_vi` | **Bỏ.** Câu được viết lại thành "`CONFLICT` là mã duy nhất cho tình huống này và nó đã có trong `contracts/errors.yaml`". Lịch sử (rằng PC02 từng dùng một mã chưa đăng ký) ở lại addendum FIX10 §K.4 — đúng nguyên tắc ruling FIX7: prose hợp đồng nói **luật hiện hành**, handoff nói **lịch sử**. |

**`<a>.<b>` không phân giải được: 66 lần / 30 token duy nhất → sửa 6, allowlist 24, còn 0.**

Ba token là **lỗi thật**, không phải nhiễu của bộ quét:

| Token | Ở đâu | Xử lý |
| --- | --- | --- |
| `post.mark_source_deleted` | `ports.yaml` `ingest.submit_batch.request_summary_vi` | **Bỏ.** Đây là tên operation **đã bị bác bỏ**, cùng lớp với `SAVE_ALREADY_EXISTS`. Câu vẫn nói đủ luật (quan sát nguồn bị xóa đến như trường `source_deleted_observed_at`), chỉ không còn nêu tên cái đã chết. |
| `ingest_receipt.sequence` ×2 | `ports.yaml` `ingest.commit_checkpoint` `guard_vi` **và** `oracle_vi` | **Sửa cột.** Entity `ingest_receipt` không có cột `sequence`; cột đúng là **`max_ingest_sequence`**. Đây là **column drift trong chính guard và oracle của R-01** — đúng lớp lỗi mà `F-A2R1-03` phạt ở PC04. Hai câu nay đọc `MAX(ingest_receipt.max_ingest_sequence đã commit)`. |
| `storage.maintenance` | `deployment.md` bảng module | **Sửa** thành `storage.health = maintenance` — `maintenance` là **giá trị** của trường `health`, không phải một trường của `storage`. |

Ba token còn lại là **đuôi của một tên dài hơn** mà bộ quét cắt nhầm, nhưng vẫn sửa vì chúng gây hiểu nhầm khi đọc:
`ACT-telegram-ingress.secret_items` → "`secret_items` của actor `ACT-telegram-ingress`";
`MOD-settings-service.network_egress` → "`network_egress` của module `MOD-settings-service`";
`entity.column` trong chính văn bản quy tắc mới → `<entity>` + `<column>`.

**24 token còn lại là hợp lệ theo thiết kế** và nay được **khai báo thành luật** thay vì để ngầm — thêm
`conventions.prose_token_rule_vi` vào `ports.yaml`: ngoài operation và cặp `<entity>`+`<column>`, chỉ bốn dạng
được phép xuất hiện — (1) đường dẫn file (`contracts/schemas/target.schema.json`), (2) khóa YAML trong chính bộ
hợp đồng (`attempted_edge.callee`, `capabilities.ai_providers`), (3) host hoặc hàm thư viện
(`api.telegram.org`, `yaml.safe_load`), (4) trường của **payload request** định nghĩa ngay trong cùng operation
(`confirmation.acknowledged`) — cộng một ngoại lệ có tên: **`storage.health`**, tên kênh trạng thái do
`contracts/state/storage.yaml` định nghĩa. Bộ quét được sửa để thực thi đúng danh sách này, nên lần sau nó sẽ chỉ
kêu về token thật.

## L.3 Gate

| Gate | Kết quả |
| --- | --- |
| `…/w2/scan_tokens.py` (mới) | **exit 0** — SCREAMING_SNAKE unresolved **0**, `<a>.<b>` unresolved **0** trên bốn file PC01 |
| `…/w2/validate_pc01_v2.py` | **exit 0**, `== NO FAILURES ==`, 0 WARN |
| `…/w2/gate_fixtures.py` | **exit 0** — bijection + callee-ownership 36/36/36, violations 0 |
| `evidence/tools/e0_check.py` (copy read-only) | **TOTAL: 19 checks — PASS 19 · FAIL 0 · violations 0**. `E0-10a` 36/0, `E0-10b` 36/0, `E0-14` 448/0 |

Lần đầu toàn bộ 19 check E0 xanh: hai FAIL tôi báo ở FIX10 (`E0-06` `REQ-S8.4-01` trong
`precode/decision-register.md` và `E0-07` `SC54`) đã được W1 xử lý song song. `CR-PC01-12` khép lại nhờ đó.

## L.4 Concerns

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| **PC10 re-pin** | `ports.yaml`, `capabilities.yaml`, `deployment.md` đổi hash (§L.1); `modules.yaml` **không** đổi. Ruling FIX7 nói W7 re-pin thành `PC10-PIN-FCW4d-20260907` sau khi W2/W3/W5 land. | OPEN |
| `CR-PC01-12` | **Đóng** — `E0-06` đã xanh. | CLOSED (chờ xác nhận) |
| Bộ quét là của W2, không phải của corpus | `E0-04b`/`E0-04c` do W6 hiện thực trong `e0_check.py`. Nếu bản của W6 dùng allowlist khác bốn dạng ở §L.2 thì hai bộ sẽ bất đồng — nên `conventions.prose_token_rule_vi` được viết vào hợp đồng để W6 có một nguồn để trỏ tới, thay vì hai bộ quét đoán độc lập. | OPEN |
| Giới hạn của phép quét | Nó kiểm **hình dạng token**, không kiểm **ngữ nghĩa câu**. Một câu có thể trỏ đúng tên cột mà vẫn mô tả sai hành vi; chỉ đọc mới bắt được. `ingest_receipt.sequence` sống sót bốn vòng audit vì mọi check trước chỉ nhìn trường cấu trúc. | OPEN |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06/-11`. Mọi fixture vẫn `NOT_RUN`. | — |

---

# ADDENDUM — PKT-PC01-FIX12

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC01-FIX12` · authority `AUTH-COORD-PC01-FIX12` · lease `LEASE-PC01-e13` (fencing 13) |
| expires_at | 2026-09-07T20:00Z |
| trigger | `F-A2R2-04` (PARTIAL của `F-A2R1-05`) — ruling: **option 1** |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started/finished (UTC) | 2026-09-07T02:13Z / 2026-09-07T02:15Z |
| next actor | `Coordinator` · lease_released_at 2026-09-07T02:15Z |

## M.1 Hash mới

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/modules.yaml` **(card-pinned)** | MODIFY | `5137a0d2b4030886115e649aa12378282f15ffb4268cc5bfe42a002f7d03ee43` / 103511 | **`11af00fd97a03d5357fc1a72d0e4e61293164f449c3a50e700c03a202e1166c7`** / 105642 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | **NO CHANGE** | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | cả sáu event `null` **đã** có `event_type` từ FIX8/FIX10; không event nào thiếu giá trị để phải sửa |
| `evidence/handoffs/PC01-handoff.md` | MODIFY (append) | `143b0469d68f0fecf37f18f167fddf3bffd0b7a11e94b55663ce10c04b9963dc` / 101031 | ghi ở thông điệp bàn giao |

Sources không đổi (02:13Z và 02:14Z).

## M.2 Sửa gì

Nhánh (a) của `default_deny.attempted_edge_operation_rule_vi` — do chính PC01 viết ở FIX10 — đòi
`operation: null` phải kèm `event_type` **và** `operation_absent_reason_vi`. Sáu case thoả điều kiện `null`, nhưng
chỉ **NC-28** có `event_type`; năm case còn lại chỉ có `operation_absent_reason_vi`. Tức quy tắc đúng, việc áp dụng
thiếu — auditor gọi đúng tên: một quy tắc tự viết ra mà chính nó không tuân.

Năm case nay có `event_type` **lấy đúng giá trị của event tương ứng** trong sweep, kèm `event_type_reason_vi`:

| Case | Cạnh | `event_type` |
| --- | --- | --- |
| `NC-12` | FE-03 `MOD-web-ui → EXT-ai-provider-api` | `local_observation` |
| `NC-15` | FE-08 `MOD-x-collector → MOD-analysis-worker` | `in_process_call` |
| `NC-22` | FE-17 `MOD-ai-adapter → EXT-x-web` | `local_observation` |
| `NC-24` | FE-20 `MOD-research-connector → EXT-x-web` | `local_observation` |
| `NC-08` | FE-21 `MOD-research-connector → EXT-chrome-profile` | `local_observation` |
| `NC-28` | FE-26 `MOD-scheduler → MOD-x-collector` | `in_process_call` *(đã có từ FIX10)* |

Nhánh (a) nay đúng **6/6**. Fixture không phải sửa: giá trị của nó đã là nguồn để điền vào case, không phải ngược
lại — nên hai bên khớp theo xây dựng, và nay khớp theo **kiểm chứng**.

## M.3 Gate

Bổ sung vào `…/w2/gate_fixtures.py`: với mỗi cặp case/event có `operation: null`, khẳng định case **có**
`event_type` và `case.event_type == event.event_type`.

| Gate | Kết quả |
| --- | --- |
| `…/w2/gate_fixtures.py` (bijection + callee-ownership + event_type) | **exit 0** — forbidden edges 36 · denied cases 36 · boundary events 36 · **violations 0** |
| **Negative self-test** của phép kiểm mới | Đổi `event_type` của **một** case thành giá trị sai → gate **BẮT** (`event_type mismatch`), exit 1; khôi phục → exit 0. Phép kiểm thực sự phân biệt được, không phải luôn xanh |
| `…/w2/validate_pc01_v2.py` | **exit 0**, `== NO FAILURES ==` |
| `…/w2/scan_tokens.py` | **exit 0** — 0 token không giải được |
| `evidence/tools/e0_check.py` (copy read-only) | `E0-10b` **PASS 36/0**; tổng 19 check: PASS 18, FAIL 1 |

FAIL còn lại là `E0-07`: **`SC57`** trích ở `PC00-handoff.md` và `PC08-handoff.md` mà chưa định nghĩa trong
`acceptance/scenarios.yaml`. Lần nhắc trong `PC08-handoff.md` là **báo cáo của chính tôi** ở addendum PC08-FIX3
về khiếm khuyết đó — cùng cơ chế đã xảy ra với `SC54`: bộ kiểm coi mọi lần nhắc là citation, nên **việc báo lỗi
tạo thêm một vi phạm**. Cần W1 định nghĩa `SC57`, hoặc `E0-07` bỏ qua văn xuôi trong handoff nói *về* một id chưa
định nghĩa.

## M.4 Concerns

| Nội dung | Trạng thái |
| --- | --- |
| **PC10 re-pin**: `contracts/modules.yaml` đổi hash (§M.1); fixture boundary **không** đổi. | OPEN |
| `E0-07` / `SC57` — ngoài phạm vi PC01; và cơ chế "báo lỗi tạo thêm lỗi" đã lặp lại lần thứ hai. Đề nghị `E0-07` loại trừ `evidence/handoffs/**` khỏi tập quét citation, hoặc yêu cầu handoff trích id chưa định nghĩa dưới dạng không-token. | OPEN |
| Bài học lặp lại | Đây là lần thứ ba một quy tắc do PC01 tự viết bị chính PC01 áp dụng thiếu (`FE-20`/`FE-21`, `NC-28`, nay `event_type`). Cả ba lần, cách phát hiện là **một phép kiểm so nội dung giữa hai artefact**, không phải đọc lại. Gate nay kiểm cả ba mặt: cạnh↔case↔event, callee-ownership, và event_type. | — |
| Kế thừa | `PROV-PC01-01…-06`, `CR-PC01-05/-06/-11`. Mọi fixture vẫn `NOT_RUN`. | — |
