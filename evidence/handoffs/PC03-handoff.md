---
contract_id: CT-handoff-PC03
version: 0.1.0
status: draft
owner_role: workflow contract owner
source_refs: [SRC-PLAN §8, SRC-PLAN §9, SRC-PLAN §10, SRC-PLAN §11 PC03, SRC-SPEC §3.3, SRC-SPEC §5.2, SRC-SPEC §5.4, SRC-SPEC §8.2, SRC-SPEC §8.3, SRC-SPEC §9, SRC-SPEC §12]
requirement_refs: [REQ-AC01, REQ-AC02, REQ-AC03, REQ-AC04, REQ-AC14, REQ-AC15]
decision_refs: [B02, B05, B08, B10, AMD-B02, AMD-B05, AMD-B08, AMD-B10, ADR-0002, ADR-0007, "R-01 (A1-R1)", "R-03 (A1-R1)", "R-04 (A1-R1)"]
invariant_refs: [I02, I09, I10, I13, I15]
producers: [worker-W4]
consumers: [Coordinator, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [contracts/ports.yaml, contracts/modules.yaml, contracts/data/entities.yaml, precode/decision-register.md, precode/requirements.csv]
scope: HANDOFF của PKT-PC03 — năm state machine, catalogue lỗi, chính sách retry/budget.
verification: SELF_VALIDATION (EV-PC03-01..05) bằng script lint trong scratch dir của worker.
claim_ceiling: DRAFT_FOR_REVIEW
---

# HANDOFF — PKT-PC03

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03` |
| worker principal | `worker-W4` |
| authority_id | `AUTH-COORD-PC03` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC03-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` |
| status | **DONE_WITH_CONCERNS** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at (UTC) | 2026-09-06T17:41Z |
| lease_released_at (UTC) | 2026-09-06T18:08Z |
| next actor | Coordinator |

`DONE_WITH_CONCERNS` chứ không phải `DONE` vì: (a) bảy `CR-PC03-nn` cần Coordinator định tuyến; (b) một
placeholder `PLACEHOLDER_KC` cố ý còn bốn giá trị `null` (rate limit arXiv/OpenAlex, REQ-A6 là KC); (c) các file
upstream PC01/PC02 đã đổi hash trong lúc gói này chạy (mục 3).

## 2. Changes — mọi file đã tạo

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/state/run.yaml` | CREATE | ABSENT | `8acb7bbf935ee6854fa41d52604972929f09843838c1c141d861d17f538f3468` | 80492 |
| `contracts/state/analysis.yaml` | CREATE | ABSENT | `73be908d0da32fb217dd45b1f296d4e10954ec7b2507c689c9e73693a9761254` | 28648 |
| `contracts/state/report.yaml` | CREATE | ABSENT | `e60ef74f438faa7119d56950f8ab7ac8170df2c9c70f0b8b3d956e0412e79ced` | 21731 |
| `contracts/state/delivery.yaml` | CREATE | ABSENT | `9fcccc25fed432a895b15e9b98787d7294dd298d9209e9b0f2c7f801e1579626` | 26652 |
| `contracts/state/storage.yaml` | CREATE | ABSENT | `608ceea67834be427013d252ea35e7798be9ae56586b7174004fe4f12078eb0b` | 27011 |
| `contracts/errors.yaml` | CREATE | ABSENT | `e236aaee44cb340bf58ab822ab3dc434847e3d777b46c5b97b3baf00bd0e1b37` | 53534 |
| `contracts/retry-policy.yaml` | CREATE | ABSENT | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` | 35285 |
| `evidence/handoffs/PC03-handoff.md` | CREATE | ABSENT | (file này) | — |

Thư mục `contracts/state/` được tạo mới. Không file nào ngoài danh sách trên bị chạm.
Không chạy lệnh git nào. `PYTHONDONTWRITEBYTECODE=1` được đặt; không có `__pycache__`. Script lint nằm ở
`…/scratchpad/w4/lint_pc03.py`, ngoài repo.

## 3. Source baselines đã dựa vào

### 3.1 Nguồn pinned (baseline §2) — KHỚP ở cả hai lần kiểm

| Ref | Path | SHA-256 | Kiểm lúc bắt đầu | Kiểm trước handoff |
| --- | --- | --- | --- | --- |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp | khớp |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp | khớp |

Stop gate `STALE_BASELINE` KHÔNG kích hoạt: nó áp cho hai nguồn pinned ở trên, và cả hai không đổi.

### 3.2 Upstream đã đọc (hash lúc đọc, khớp `audits/FC-W1-manifest.txt`)

| Path | SHA-256 lúc tôi đọc |
| --- | --- |
| `contracts/ports.yaml` | `bde5f133297c1aa381f2db8f5b861a54f9df593adc8c6fb9b7606a8f37dd4470` |
| `contracts/data/entities.yaml` | `88b2482ede392e581b1d4eb0640bca0810ce94953bd8ada7c9b1e6b7f5ebb8fb` |
| `contracts/modules.yaml` | `389487f809e2f69140414d71f72ce249ff612b4b72824d50c46041a4520367c8` |
| `contracts/capabilities.yaml` | `58956925fb28bb1b002c3bc620753b164c591686801b1c7c6d3bb943629331d4` |
| `contracts/ops/deployment.md` | `d48b0c9d37ed150b187fb593dacc22b38f57754e309f557854ce1ecb2a15861b` |
| `contracts/data/identity.md` | `01976cabe4dae4e587cb0e555ca6a0176c5726c0815207bb04287cb5d1169571` |
| `contracts/data/invariants.md` | `844576bc39024ba66186db4cf0f461a8bc636ccb86fb70b07b2feac7ec40fbbd` |
| `precode/decision-register.md` | `9f212849d6da284bf288353720a7e93bd5898610c7e66b07ac7240f359796480` |
| `precode/requirements.csv` | `e98764972845bd9fc19608ba2e2428e1ed33d37145000e77129570865fb7a0a5` |
| `precode/adr/ADR-0002…0010` | như manifest FC-W1 |
| `agent_profile/worker.md` | `51d75b4cc9a7ea4d4975e1725dad7ac9d9773e4835e43532d30eea361c0d0c60` |

### 3.3 UPSTREAM DRIFT quan sát được trước handoff (không phải stop gate)

Coordinator đã báo trước rằng `PKT-PC01-FIX2` và `PKT-PC02-FIX2` chạy song song. Hash MỚI lúc 18:06Z:

| Path | SHA-256 mới | Thay đổi ảnh hưởng tôi? |
| --- | --- | --- |
| `contracts/ports.yaml` | `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` | Không phá: 85 operation, mọi ID tôi trích dẫn vẫn tồn tại; thêm `data.delete_target`, `data.purge_all` (R-04) — tôi đã cập nhật `storage.yaml` để trích dẫn đúng bản mới. |
| `contracts/data/entities.yaml` | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | Không phá: `TXN-checkpoint-only` và `ingest_receipt.receipt_kind` đã được PC02 thêm, KHỚP với `CP-07` của tôi; `identity_merge_max_moved_rows` vẫn 100000; `ENT-run` vẫn `owned_by_package: PC03`. |
| `contracts/modules.yaml` | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` | Không phá: EV-03 vẫn PASS trên bản mới. |
| `contracts/capabilities.yaml` | `c54cdaaf85be339aff5823902c9cb27a2aa25ebea61c241f1b76d2999e6ea7ab` | Không dùng trực tiếp. |
| `contracts/ops/deployment.md` | `4d879f2be6187623410bca378b34fc9aa38771b72e70ba309b8edef04a0f1295` | **CẦN A ĐỐI CHIẾU**: tôi lấy `heartbeat_interval = 30 s` và `online_threshold = 90 s` từ bản CŨ để chốt `lease_ttl_collector = 120 s` (ràng buộc RPC-01/RPC-02). Nếu FIX2 đổi hai số này thì `consistency_constraints` của `retry-policy.yaml` phải tính lại. |
| `contracts/data/invariants.md` | `134bf9f27b36ab624416809af76bf6059aa05db83cdcdb254a7277d41705fb64` | Tôi trích I02/I16/I17 theo bản cũ; Auditor nên đối chiếu câu chữ I02 counterexample 2 (R-01 yêu cầu PC02 viết lại). |
| `precode/decision-register.md` | `0a64b05095a44ded2ab94ff405881ffe09e26d1277928503d49b1643d101f4c6` | **CẦN ĐỐI CHIẾU**: AMD-B02 (13 hàng mapping) và AMD-B08 được tôi chép NGUYÊN VĂN từ bản cũ. Nếu FIX2 sửa hai amendment này thì `run.yaml §legacy_enum_mapping` và `§schedule_model` phải cập nhật. |
| `precode/requirements.csv` | `1bf60a1c54721adeedc7bc13b0313fd409d064bb3d3f44283b24885f584b9dbb` | REQ-S8.4-01 vẫn KHÔNG tồn tại (xem CR-PC03-01). |

Đánh giá của tôi: không có drift nào làm sai một hàng transition. Lint EV-01..EV-05 được CHẠY LẠI trên bản
upstream mới và PASS. Nhưng ba dòng đánh dấu **CẦN ĐỐI CHIẾU** phải do Auditor xác nhận, không phải tôi.

## 4. Evidence records

Mọi record là `SELF_VALIDATION`. Không có audit độc lập nào được chạy. Runtime: `python3` với PyYAML,
chạy từ `…/scratchpad/w4/` (ngoài repo). Script: `lint_pc03.py`.

### EV-PC03-01 — YAML parse cả 7 file
- type: SELF_VALIDATION
- command: `cd <scratch>/w4 && PYTHONDONTWRITEBYTECODE=1 python3 lint_pc03.py`
- started/ended (UTC): 2026-09-06T18:05Z / 18:05Z (lần chạy thứ hai, trên upstream mới)
- input hashes: bảy file ở mục 2 (hash sau cùng)
- oracle: `yaml.safe_load` không ném ngoại lệ cho cả 7 file
- expected: 7/7 · observed: `EV-01 parsed 7/7 files` · exit code: 0
- status: **PASS**
- limitations: parse ≠ đúng nghiệp vụ. Không kiểm schema (chưa có meta-schema cho contract header).

### EV-PC03-02 — Transition lint + reachability
- oracle: (a) mọi `from`/`to` thuộc enum đã khai; (b) mọi event có ≥1 hàng; (c) mọi trạng thái non-terminal có
  ≥1 hàng đi ra; (d) trạng thái terminal không có hàng đi ra, trừ ngoại lệ khai báo `T-AN-12`/`T-AN-13`
  (“retry via new generation” theo SRC-PLAN §11 PC03); (e) reachability từ initial state tới mọi trạng thái.
- observed:
  - `run`: 8 states, 24 rows, 22 events, reachable 8/8
  - `analysis`: 6 states, 13 rows, 13 events, reachable 6/6
  - `report`: 3 states, 7 rows, 7 events, reachable 3/3
  - `delivery`: 7 states, 10 rows, 10 events, reachable 7/7
  - `storage`: 4 states, 9 rows, 9 events, reachable 4/4
- exit code: 0 · status: **PASS**
- limitations: `run` có trạng thái ghép (status × phase); lint chỉ kiểm chiều `status`. Các ô `phase` mang giá
  trị mô tả (“không đổi”, “phase đã lưu”) được bỏ qua có chủ đích. `storage` có tập terminal RỖNG nên tiêu chí
  (d) không áp dụng — đã ghi rõ trong `storage.yaml §note_on_terminality_vi`.

### EV-PC03-03 — Đối chiếu mã lỗi
- oracle: (a) đủ 16 mã của SRC-PLAN §10; (b) đủ 10 mã wire chung mà PKT-PC03 liệt kê; (c) mọi mã được 5 file
  state tham chiếu đều tồn tại trong `errors.yaml`; (d) mọi mã xuất hiện trong `contracts/ports.yaml` và
  `contracts/modules.yaml` (`error_codes:`, `expected_error_code:`) đều tồn tại; (e) mọi mã có ≥1 `target_states`.
- observed: `codes=26 refd_by_state=25 refd_by_upstream=23`; 0 mã thiếu · exit code: 0 · status: **PASS**
- limitations: (c)/(d) dùng regex trên văn bản, không parse ngữ cảnh — có thể bỏ sót mã nằm trong prose.
  Điều kiện (e) được thỏa với quy ước `machine: request, to_state: unchanged` cho 8 mã wire không đổi trạng
  thái nghiệp vụ; quy ước này được khai tường minh ở `errors.yaml §vocabulary.target_states_semantics_vi`.
  Đây là DIỄN GIẢI của tôi về tiêu chí “maps to ≥1 target state” trong packet — Auditor nên xác nhận.

### EV-PC03-04 — Đối chiếu operation ID với ports.yaml
- oracle: mọi `operation_id` tôi trích dẫn tồn tại trong `contracts/ports.yaml`
- observed: ports có 85 operation; 60 operation ID được trích và HỢP LỆ; 12 token dạng `x.y` còn lại đã được
  tôi rà tay và đều KHÔNG phải operation: `analysis.task_type`, `delivery.status`, `delivery.unknown`,
  `delivery.telegram_link_generation`, `run.unblock_condition_vi`, `report.schema`, và 6 tên file
  (`*.yaml`, `delivery.md`) · exit code: 0 · status: **PASS**
- limitations: chạy hai lần, trên ports.yaml bản cũ (`bde5f1…`) và bản mới (`485213…`); PASS ở cả hai.
  Không có operation nào tôi phải bịa; không dùng `pending_cr:` cho operation nào.

### EV-PC03-05 — Budget đủ số/đơn vị/lý do
- oracle: mọi mục trong `retry-policy.yaml §budgets` có `value` hoặc `values`, `unit`, `status`,
  `rationale_vi`, `retried_by`; mọi `retry_budget_ref`/`budget` được các file khác trích đều tồn tại.
- observed: `budgets=41 refs=21`, 0 thiếu trường, 0 tham chiếu treo · exit code: 0 · status: **PASS**
- limitations: lint kiểm SỰ CÓ MẶT của lý do, không kiểm lý do có đúng không. Mục
  `research_connector_rate_limit` có `status: PLACEHOLDER_KC` và bốn giá trị `null` CÓ CHỦ ĐÍCH (REQ-A6 là KC);
  nó vượt qua lint nhờ khóa `values`, và điều này được ghi rõ trong `blocked_scope_vi`. Không được đọc PASS
  của EV-05 là “mọi con số đã đóng”.

### Không chạy
- Fixture/scenario thật: `NOT_RUN` (PC03 không sở hữu thư mục fixture nào).
- Fake-clock, DST, disk-full, crash injection: `NOT_RUN` — đây là các oracle được VIẾT, chưa được CHẠY.
- Audit độc lập: `NOT_RUN`.

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Transition table from/event/guard/to/transaction/effect/oracle; ánh xạ enum cũ | **DONE** | `run.yaml §4` (24 hàng, phủ đủ 14 hàng SRC-PLAN §8.1 + run-now/cancel/lease-expiry/worker-lost/write_blocked), `§2` (13 hàng AMD-B02 nguyên văn); `analysis.yaml §3`; `report.yaml §2`; `delivery.yaml §4`; `storage.yaml §3` |
| 2 | Claim/lease TTL/heartbeat/epoch, `STALE_LEASE`, cancel, resume (chỉ từ needs_user, lease mới) | **DONE** | `run.yaml §6` (LM-01..LM-08), `T-RUN-10/11/14/15/17`, `retry-policy.yaml §budgets` (lease_ttl_collector 120 s, lease_ttl_analysis 900 s, heartbeat_grace 30 s, sweep 15 s, claim_request_timeout 10 s, lease_epoch_rule) + `§consistency_constraints` RPC-01..08 |
| 3 | Lịch/timezone/DST/earliest-run/catch-up/manual khi đang chạy | **DONE** | `run.yaml §7` (DST-01 gap → instant đầu tiên ≥ giờ danh nghĩa; DST-02 lặp → lần xuất hiện ĐẦU; DST-03 đổi tz; CU-01..CU-05), `T-RUN-21` (coalesce), `retry-policy.yaml` (schedule_catch_up_lookback_max 7 ngày, run_now_debounce 60 s, run_now_active_run_policy) |
| 4 | Checkpoint chỉ trên dữ liệu ACK, `INGEST_ACK_LOST`, stale cursor, worker chết sau external call | **DONE** | `run.yaml §8` (CP-01..CP-08, đã căn theo ruling R-01), `§9 FT-INGEST`, `FT-CHECKPOINT-ONLY`, `FT-CHECKPOINT-CAPTCHA`; `analysis.yaml §6` |
| 5 | Failure timeline theo ranh giới commit + danh sách transition bị cấm | **DONE** | `run.yaml §9` (5 timeline: INGEST, CHECKPOINT-ONLY, CHECKPOINT-CAPTCHA, ANALYSIS-ACCEPT, PUBLISH, SEND) và `§5` (9 hàng cấm); `analysis.yaml §4` (5), `report.yaml §4` (6), `delivery.yaml §5` (8), `storage.yaml §4` (5) |

### Ràng buộc “Đạt khi” của SRC-PLAN §11 PC03

| Điều kiện | Trạng thái | Bằng chứng |
| --- | --- | --- |
| Mọi lỗi §10 map tới trạng thái | DONE | EV-PC03-03; `errors.yaml §index_by_machine` |
| Không terminal nào âm thầm chạy side effect | DONE | `run.yaml §TSR-01`, `analysis.yaml §TSR-A01`, `delivery.yaml §TSR-D01`, `report.yaml §forbidden_transitions`; `storage.yaml` khai tập terminal rỗng có lý do |
| Không chỗ nào persist error vào DB đang không ghi được mà thiếu fallback health | DONE | `errors.yaml §4 EPR-01`; `run.yaml T-RUN-19` (hàng CỐ Ý không ghi); `storage.yaml §5 HC-01..HC-04` |

### Invariant (I02, I09, I10, I13, I15) — owner transition + counterexample

| ID | Owner transition | Counterexample | Ở đâu |
| --- | --- | --- | --- |
| I02 | T-RUN-02/13/19, CP-01, FT-INGEST t3/t4 | checkpoint tiến trước COMMIT của post | `run.yaml §10`, `storage.yaml §8` |
| I09 | T-RUN-06/07/17c, T-DL-04/07/08 | `run.status = failed` khi `delivery.state = failed` | `run.yaml §10`, `delivery.yaml §7` |
| I10 | T-RUN-09/10/11/14/17b, LM-04, LM-07 | `run-now` qua Telegram resume một `needs_user`; worker epoch cũ commit | `run.yaml §10` |
| I13 (phần state) | T-RUN-07/08/16/18/19, DP-03, UI-01..UI-04 | gộp `empty` với `failed`; aggregate `sent` khi còn part `unknown` | `run.yaml §10`, `delivery.yaml §7`, `storage.yaml §6, §8` |
| I15 (dispatch lock sau restore) | T-RUN-01 guard, LM-08, T-DL-09, T-ST-05..T-ST-08 | về `healthy` không qua `backup.reconcile_after_restore` | `run.yaml §10`, `delivery.yaml §7`, `storage.yaml §8` |

## 6. Unresolved — CR, PROVISIONAL, và câu hỏi mở

### 6.1 Change requests (Coordinator định tuyến)

| ID | Với gói | Nội dung |
| --- | --- | --- |
| `CR-PC03-01` | PC00 hoặc PC01 | `contracts/ports.yaml` (cả bản cũ và mới) tham chiếu `REQ-S8.4-01` ở `health.get_liveness`, `health.get_readiness`, `storage.get_health`, nhưng ID này KHÔNG tồn tại trong `precode/requirements.csv` (SRC-SPEC không có §8.4; §8.4 là của SRC-PLAN). Đề nghị: PC00 thêm một REQ mới cho “kênh health độc lập DB”, hoặc PC01 đổi tham chiếu sang `REQ-S9.3-08`. Tôi KHÔNG dùng `REQ-S8.4-01` ở bất kỳ file nào của mình. |
| `CR-PC03-02` | PC01 (`ports.yaml`) | Không có operation nào đưa một run rời `blocked`. `run.resume` chỉ khai cho `needs_user` (B10). Hiện `blocked` chỉ thoát được qua `run.cancel` (T-RUN-17c) — điều này đúng về an toàn (cấm retry tự động, REQ-S9.3-02) nhưng buộc Owner phải hủy và tạo run mới. Đề nghị: mở rộng `run.resume` cho `blocked` với guard “Owner xác nhận điều kiện gỡ chặn đã hết”, hoặc thêm `run.unblock`. Tôi KHÔNG bịa operation; `run.yaml` nói rõ đường thoát hiện có. |
| `CR-PC03-03` | PC02 (`entities.yaml`) | `ENT-run` cần các cột additive do PC03 sở hữu: `schedule_occurrence_ids`, `catch_up_window_from/to`, `current_lease_epoch`, `attempt_count`, `next_attempt_at`, `last_error_code`, `unblock_condition_vi`, `alert_intent_id`, và 8 cột coverage metadata. Định nghĩa đầy đủ ở `run.yaml §3`. `ENT-run` đã ghi `owned_by_package: PC03` nên đây là bổ sung, không phải tranh chấp. |
| `CR-PC03-04` | PC05 (`openapi.yaml`) | Ba mã `FORBIDDEN_EDGE`, `RATE_LIMITED`, `INTERNAL` được đăng ký theo yêu cầu PKT-PC03 nhưng CHƯA được `ports.yaml`/`modules.yaml` tham chiếu (modules.yaml diễn đạt cạnh cấm bằng `FE-*` + `expected_error_code` của `NC-*`). PC05 nên nối chúng vào wire, hoặc Coordinator xác nhận chúng chỉ là mã runtime. Đã ghi `note_vi` trên cả ba. |
| `CR-PC03-05` | PC01 hoặc PC06 | Tên `task_type` lệch: `ports.yaml analysis.enqueue_tasks` viết `open_labeling` \| `summary` \| `emerging_direction_phrasing`; `entities.yaml` (4 chỗ) viết `label` \| `summary` \| `direction_phrasing`. Theo ruling R-03 (tên PC02 có thẩm quyền) tôi dùng bộ của entities.yaml và ghi chú lệch trong `analysis.yaml §2`. Cần một bên sửa. |
| `CR-PC03-06` | PC04 | `report.yaml T-RP-07` dùng `status = aborted` cho kỳ RỖNG (sự thật nghiệp vụ nằm ở `coverage_window(report_id = NULL)` + `run.outcome = empty`, đúng nơi AMD-B04 đặt). Nếu PC04 cần phân biệt “aborted vì rỗng” với “aborted vì lỗi” ngay trên bảng `report`, cần thêm một cột lý do — không phải trạng thái thứ tư (SRC-PLAN §8.2 khai đúng ba). PROVISIONAL. |
| `CR-PC03-07` | PC02 (`entities.yaml`) | `ENT-delivery-part.state` khai 4 giá trị `pending \| sent \| unknown \| failed`. PC03 thêm `sending` để trạng thái “đã commit attempt, chưa có kết quả” quan sát được — đó chính là trạng thái mà crash biến thành `unknown` (SRC-PLAN §8.3 yêu cầu ghi attempt TRƯỚC network call). Bổ sung additive; ghi rõ ở `delivery.yaml §1`. |

### 6.2 Quyết định PROVISIONAL do PC03 đưa ra (không có trong baseline §5)

Không có stop gate §6 nào kích hoạt; mọi mục dưới đây theo khuyến nghị của SRC-PLAN, gắn nhãn `PROVISIONAL`.

1. **DST-01 / DST-02** (`run.yaml §7`). SRC-PLAN và ADR-0007 giao việc cho PC03 mà không nêu quy tắc. Chọn:
   giờ không tồn tại → chạy tại instant đầu tiên ≥ giờ danh nghĩa (không bỏ occurrence, tránh lỗ hổng bao
   phủ); giờ lặp lại → lấy lần xuất hiện ĐẦU (không sinh hai đợt). `Asia/Ho_Chi_Minh` hiện không có DST nên
   hai quy tắc chưa kích hoạt với giá trị mặc định, nhưng Owner chưa xác nhận timezone (B08).
2. **`run_now_active_run_policy = coalesce`** thay vì reject (`retry-policy.yaml`, `T-RUN-21`). Căn cứ:
   `ports.yaml run.run_now` đã cam kết “bấm lặp trả run đang có”.
3. **Tách ngân sách `provider_unavailable_waits` khỏi `analysis_attempts_per_item`**
   (`retry-policy.yaml`). Lý do: `AI_PROVIDER_UNAVAILABLE` nghĩa là chưa có inference nào chạy; trộn chung sẽ
   đốt hết quyền “thử lại một lần” của D43 chỉ vì CLI không khởi động được.
4. **`analysis_unknown_attempt_auto_rerun = 1`** — cho phép tự chạy lại MỘT lần từ `unknown_attempt`, khác hẳn
   `delivery.unknown` (không bao giờ tự chạy lại). Căn cứ: SRC-PLAN §10 nói AI_ATTEMPT_UNCERTAIN “tái chạy
   theo policy ghi attempt mới”; hậu quả xấu nhất là TỐN PHÍ, còn ở delivery là người nhận thấy tin trùng —
   không quan sát được và không hoàn tác được. **Đây là chỗ tôi diễn giải khác câu “never retry unknown
   outcome” trong packet; lý do được viết đầy đủ tại `retry-policy.yaml §budgets` và `analysis.yaml T-AN-09`.
   Đề nghị Auditor soi kỹ mục này.**
5. **Mọi con số lease/backoff/window** trong `retry-policy.yaml` (41 budget). `lease_ttl_collector = 120 s`
   được neo vào `heartbeat_interval = 30 s` và `online_threshold = 90 s` của `contracts/ops/deployment.md`
   (PC01) — xem cảnh báo drift ở mục 3.3.
6. **`storage.maintenance` là trạng thái do Operator mở CÓ CHỦ ĐÍCH**, và `T-ST-08` (từ `write_blocked` quay
   về `recovery_required` khi còn `restore_record` chưa reconcile). SRC-PLAN §8.4 không nêu tương tác giữa hai
   sự cố chồng nhau; nếu thiếu hàng này thì một sự cố ổ đĩa xen vào sau restore sẽ “rửa sạch” nợ đối soát và
   phá I15.

### 6.3 Phạm vi cố ý để trống, có gate

- `research_connector_rate_limit`: bốn giá trị `null`, `status: PLACEHOLDER_KC`, chỉ có một sàn an toàn
  `min_interval_ms = 3000` (PROVISIONAL, bảo thủ). Căn cứ REQ-A6 trạng thái KC (“đọc tài liệu chính thức khi
  triển khai”). **Không bịa hạn mức.** PC05 phải điền trước khi research connector được coi là CONTRACT_READY.
- Semantic validation của output AI: `analysis.yaml T-AN-03` khóa RÀNG BUỘC (`valid` chỉ đạt sau CẢ HAI cửa
  schema + semantic) và giao nội dung cho PC06, kèm câu “PC06 không được nới điều kiện này, chỉ được làm chặt
  hơn”.
- Nội dung coverage/selection/first-announcement: `report.yaml §1 ownership_boundary` liệt kê rõ hai cột
  “PC03 sở hữu” / “PC04 sở hữu”, cộng một `interface_contract_vi` nêu đúng ba vị từ boolean PC04 phải cung cấp.
- Quy trình backup/restore chi tiết: `storage.yaml §7` giao PC08, kèm vị từ
  `reconciliation_complete(restore_id)`.

### 6.4 Câu hỏi cần Owner (chuyển tiếp, PC03 không tự quyết)

- `schedule_timezone` thật (B08 — `Asia/Ho_Chi_Minh` là giá trị tạm; nếu Owner ở múi khác thì mọi fixture lịch
  của PC03/PC04 phải dựng lại).
- `per_run_post_limit` / `per_run_duration_limit` thật (REQ-OQ05) và các mốc lịch thật (REQ-OQ06).

## 7. Trạng thái sau handoff

Không file nào bị chạm sau thời điểm này. Sửa tiếp cần packet mới, baseline mới, lease mới.
Worker KHÔNG tự chứng nhận freeze; `FROZEN_CANDIDATE` do Coordinator phát hành.

- next actor: **Coordinator**
- audit route: `INDEPENDENT_REQUIRED` (chưa chạy — `NOT_RUN`)
- `lease_released_at`: 2026-09-06T18:08Z

---

# ADDENDUM — PKT-PC03-FIX1

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03-FIX1` |
| authority_id | `AUTH-COORD-PC03-FIX1` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC03-e2` (exclusive, **fencing 2** — thay cho `LEASE-PC03-e1` đã trả) |
| worker principal | `worker-W4` |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-06T18:32Z / 2026-09-06T18:39Z |
| next actor | Coordinator |

## A1. Changes (MODIFY, baseline = hash trong bảng §2 của handoff gốc)

| Path | Op | Before (sha256) | After (sha256) | Bytes trước → sau |
| --- | --- | --- | --- | --- |
| `contracts/state/run.yaml` | MODIFY | `8acb7bbf935ee6854fa41d52604972929f09843838c1c141d861d17f538f3468` | `fcad82589aaee43fb15735b10fc7fd7d25c7e94af6e32295aca40a4b0d88999d` | 80492 → 86734 |
| `contracts/state/report.yaml` | MODIFY | `e60ef74f438faa7119d56950f8ab7ac8170df2c9c70f0b8b3d956e0412e79ced` | `5e2ce6cf7f990dc34e033c7b5fc7a56394ddd3afcc190c0a988b6c75dea5cf61` | 21731 → 27115 |
| `contracts/errors.yaml` | MODIFY | `e236aaee44cb340bf58ab822ab3dc434847e3d777b46c5b97b3baf00bd0e1b37` | `3201bbe86a3ef373a4fb35c265cd9f27ed60f6ce2af3fd65a76c0dcfb032d86b` | 53534 → 59570 |
| `contracts/retry-policy.yaml` | MODIFY | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` | `638a86bda631eedda5d980bfb5fdef5e07bf65a4214041a9f5d8dd1da933fc69` | 35285 → 35514 |

**Không đổi** (nằm trong MODIFY grant nhưng không cần sửa; hash bằng đúng bản gốc):
`contracts/state/analysis.yaml` `73be908d…`, `contracts/state/delivery.yaml` `9fcccc25…`,
`contracts/state/storage.yaml` `608ceea6…`.
Bốn file trên nâng `version: 0.1.0 → 0.2.0`; `status` vẫn `draft`; `claim_ceiling` vẫn `DRAFT_FOR_REVIEW`.

## A2. Delta theo từng mục của packet

| # | Yêu cầu | Đã làm gì | Ở đâu |
| --- | --- | --- | --- |
| 1 | Đăng ký `CSRF_REJECTED` (403, scope `request`, retry_class `none`) | Mã mới, kèm mục `distinct_from_vi` phân định ba mã 401/403 theo ruling CR-PC08-04: `UNAUTHORIZED` = danh tính/lớp principal; `FORBIDDEN_EDGE` = cạnh không có trong registry; `CSRF_REJECTED` = danh tính và cạnh đều hợp lệ nhưng không chứng minh được lời gọi do trang của ứng dụng phát ra. Liệt kê 18 operation áp dụng. Cấm hủy phiên khi gặp mã này. | `errors.yaml §3` |
| 2 | Đăng ký `SOURCE_LAYOUT_CHANGED` (CR-PC05-01) | Mã mới: run → `blocked`, `stop_reason = source_layout_changed`, `retry_class: none`, **một** alert intent mỗi run, oracle trỏ tới fixture (a). Kèm `distinct_from_x_access_blocked_vi`. | `errors.yaml §3` |
| 3 | `stop_reason: source_layout_changed` + hàng transition | Enum `stop_reason` += giá trị mới (7 giá trị); hàng **T-RUN-24** với guard phân biệt rõ "vào được nhưng không đọc được" khỏi "không cho vào" | `run.yaml §1`, `§4` |
| 4 | `run.resume` từ `blocked` (CR-PC03-02) | Hàng **T-RUN-23**: guard đòi `unblock_reason` bắt buộc; thu hồi lease, epoch +1; oracle gồm cả ca âm (thiếu `unblock_reason` ⇒ `VALIDATION_ERROR`). Hàng `forbidden_transitions` cho `blocked → running` được viết lại để nêu đường thoát hợp lệ DUY NHẤT | `run.yaml §4`, `§5` |
| 5 | CP-07 wording (F-A1R2-04, cite CR-PC02-12) | `transaction_vi` đổi từ "**cập nhật** MỘT hàng `checkpoint`" thành "**APPEND** MỘT HÀNG `checkpoint` MỚI (với `sequence` kế tiếp)" + hàng `ingest_receipt` mang `receipt_kind='checkpoint_only'`. Thêm `wording_correction_vi` ghi rõ vì sao câu cũ sai: nó mô tả như transaction hợp lệ đúng thứ CP-04 cấm và `TXN-checkpoint-only.forbidden_effects` liệt kê là cấm | `run.yaml §8 CP-07` |
| 6 | `abort_reason` trên T-RP-03…07 (CR-PC04-08) | Enum `abort_reason` (6 giá trị, nullable, CHECK NOT NULL iff `status='aborted'`) + gán giá trị cho từng hàng: T-RP-03 `tag_version_stale`, T-RP-04 `embedding_generation_mismatch`, T-RP-05 `cas_conflict`, T-RP-06 `builder_failure`, T-RP-07 `empty_period`; T-RP-02 (`published`) khai `abort_reason: null` | `report.yaml §1`, `§2` |
| 7 | `publish_cas` trích `report.report_build_id` + quy tắc replay (F-A1R2-01) | Khối `idempotency_anchor` nêu cột đã persist (`report.report_build_id`, UUIDv4, NOT NULL, `UNIQUE(owner_id, report_build_id)`) và giải thích vì sao một khóa idempotency không được persist thì không chống được replay. `idempotency_rule_vi` viết lại thành **bốn nhánh** theo trạng thái hàng tìm được, cộng `replay_oracle_vi` | `report.yaml §3` |

### Ngoài phạm vi tối thiểu, trong grant — hai việc thêm

- **T-RP-08** (`building → aborted`, `abort_reason: cancelled`). Ruling khai enum 6 giá trị nhưng năm hàng
  T-RP-03…07 chỉ phủ 5; `cancelled` không có đường tới. `run.yaml` T-RUN-17b đã cam kết "chặn publish mới" khi
  Owner hủy — T-RP-08 là mặt report của cam kết đó. Sau khi thêm, **mọi giá trị enum đều reachable** (kiểm
  bằng script, xem A3).
- **Hai tham chiếu chéo cũ tới `CR-PC03-02` đã lỗi thời** (CR nay đã giải) được cập nhật để nêu đường thoát
  thật: `retry-policy.yaml §never_retry` (mục `blocked`) và `errors.yaml` → `X_ACCESS_BLOCKED.forbidden_vi`.
  Nếu để nguyên, hai file sẽ nói "không có đường thoát" trong khi `run.yaml` vừa định nghĩa một đường.

## A3. Evidence

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC03-06` | `cd <scratch>/w4 && PYTHONDONTWRITEBYTECODE=1 python3 lint_pc03.py` | **PASS** — `run`: 8 states / **26 rows** (24 → 26) / 24 events / reachable 8/8; `report`: 3 states / **8 rows** (7 → 8) / reachable 3/3; `analysis` 13 rows; `delivery` 10 rows; `storage` 9 rows; `codes=28` (26 → 28); refd_by_state=27; refd_by_upstream=25; budgets=41 | **0** |
| `EV-PC03-07` | script kiểm phủ enum `abort_reason` (inline python, cùng scratch dir) | **PASS** — tập `abort_reason` dùng bởi các hàng `to: aborted` BẰNG ĐÚNG tập enum 6 giá trị | 0 |

- type: `SELF_VALIDATION`. started/ended UTC: 2026-09-06T18:37Z / 18:38Z.
- **ports.yaml đã validate ngược lại:** `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a`
  (hash được đo NGAY TRƯỚC và NGAY SAU lần lint cuối — giống nhau, nên kết quả lint tương ứng đúng bản này).
  `contracts/data/entities.yaml`: `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993`.
- Nguồn pinned khớp ở cả hai lần kiểm: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.
- Giới hạn: như handoff gốc §4 — EV-04 vẫn báo 14 token dạng `x.y` không phải operation; ba token mới
  (`report.report_build_id`, `storage.maintenance`, và các tên file) đã rà tay và đều là field/state/tên file.

## A4. Concerns

1. **W2 đang sửa `ports.yaml` song song.** Hash đổi hai lần trong lúc tôi làm (`5afd368f…` → `100c94c1…`).
   Tại `100c94c1…`, `run.resume` ĐÃ có `allowed_from_states_vi` cho `blocked` + `unblock_reason`, khớp T-RUN-23.
   Nhưng `SOURCE_LAYOUT_CHANGED` **chưa** xuất hiện trong `worker.report_stop.error_codes` và chưa có
   `stop_reason` tương ứng ở ports.yaml. Mã đã đăng ký ở `errors.yaml` (tôi sở hữu) và hàng T-RUN-24 đã có;
   phần ports.yaml thuộc PKT-PC01-FIX3. **Auditor nên kiểm lại cặp này ở lần freeze sau.**
2. **`report.report_build_id` và `report.abort_reason` là cột do PC02 FIX3 khai.** Tại
   `entities.yaml 2235564f…` (bản tôi đọc), **cả hai đều CHƯA có**. `report.yaml` của tôi trích dẫn chúng theo
   bảng field-level của ruling FIX3 — đúng như packet yêu cầu — nhưng cho tới khi PC02 FIX3 land thì
   `publish_cas.idempotency_anchor` và `abort_reason` vẫn trỏ tới cột chưa tồn tại. Đây chính là hình dạng của
   F-A1R2-01; nó chưa đóng cho tới khi PC02 land.
3. **Không CR mới.** `CR-PC03-02` (đường thoát của `blocked`) và `CR-PC05-01` (mã layout) coi như đã được
   ruling FIX3 giải quyết và đã hiện thực hoá ở gói này.

---

# ADDENDUM — PKT-PC03-FIX2

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03-FIX2` (Coordinator amendment cho `CR-PC06-01`) |
| authority_id | `AUTH-COORD-PC03-FIX2` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC03-e3` (exclusive, **fencing 3**) |
| worker principal | `worker-W4` |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-06T18:44Z / 2026-09-06T18:47Z |
| next actor | Coordinator |

Chọn FIX2 (không nhét vào FIX1) vì lease `LEASE-PC03-e2` đã được TRẢ trước khi amendment tới — worker.md cấm
ghi tiếp sau release, kể cả sửa nhỏ.

## C1. Changes (MODIFY, baseline = hash sau FIX1)

| Path | Op | Before (sha256) | After (sha256) | Bytes trước → sau |
| --- | --- | --- | --- | --- |
| `contracts/retry-policy.yaml` | MODIFY | `638a86bda631eedda5d980bfb5fdef5e07bf65a4214041a9f5d8dd1da933fc69` | `8e2bd87a61b4a8f79429d1ca9662adc4cbe07a0299ef343b0a23a18a5bc39f37` | 35514 → 39738 |
| `contracts/state/analysis.yaml` | MODIFY | `73be908d0da32fb217dd45b1f296d4e10954ec7b2507c689c9e73693a9761254` | `d20df15250cc262d20abb5ae8283c0b9656494b9fce69696114f830eb3f4492b` | 28648 → 30405 |

`retry-policy.yaml` → `version: 0.3.0`; `analysis.yaml` → `version: 0.2.0`. Không file nào khác bị chạm.

## C2. Delta

**`contracts/retry-policy.yaml` — bốn mục mới trong `budgets` (41 → 45):**

| Budget | Giá trị | retried_by | Lý do đã ghi |
| --- | --- | --- | --- |
| `ai_inference_timeout_label` | 120 s | worker | Gắn nhãn mở là tác vụ ngắn; 120 s phủ cả chi phí khởi động tiến trình CLI mà vẫn cắt sớm một lần treo |
| `ai_inference_timeout_summary` | 300 s | worker | Đầu vào và đầu ra lớn nhất trong ba tác vụ nên ngân sách lớn nhất; vẫn nhỏ hơn nhiều `lease_ttl_analysis` |
| `ai_inference_timeout_direction_phrasing` | 180 s | worker | Đầu vào ĐÃ TÍNH SẴN (mật độ vector do PC04 tính; AI chỉ diễn đạt lại — SRC-SPEC §2.3) nhưng đầu ra là văn xuôi ⇒ nằm giữa hai cái kia |
| `ai_inference_timeout_semantics` | (quy tắc) | worker | Timeout transport = KHÔNG BIẾT KẾT QUẢ (SRC-PLAN §5.1) ⇒ `unknown_attempt`, **không** `failed`; TIÊU THỤ một đơn vị của `analysis_attempts_per_item`, **không** mở ngân sách mới |

Cả bốn đều `PROVISIONAL`, `decision_ref: CR-PC06-01`, và tên `task_type` theo `entities.yaml`
(`label` / `summary` / `direction_phrasing` — không dùng cách viết của ports.yaml, theo thẩm quyền đặt tên
entity).

**Hai ràng buộc nhất quán mới** (`consistency_constraints`, 8 → 10):

- `RPC-09`: `max(ai_inference_timeout_*) < lease_ttl_analysis` — giữ `300 < 900`. Đây là ràng buộc **mang
  nghĩa**, không phải trang trí: nếu lease hết TRƯỚC timeout thì task bị thu hồi với
  `cancelled_stale_lease`, và ta mất hẳn tín hiệu `unknown_attempt` / `cost_uncertain` — tức mất luôn thông
  tin rằng chi phí CÓ THỂ đã phát sinh.
- `RPC-10`: `label ≤ direction_phrasing ≤ summary` — giữ `120 ≤ 180 ≤ 300`.

**`contracts/state/analysis.yaml`:**

- `T-AN-08` (`running → unknown_attempt`): guard nay nêu rõ **hết giờ inference cũng vào đây**, kèm ba con số
  và trích SRC-PLAN §5.1.
- `forbidden_vi` của T-AN-08 thêm ba mục: cấm tuyên bố chưa phát sinh phí *kể cả khi nguyên nhân là hết giờ*;
  cấm coi timeout là `failed` (`failed` = ĐÃ BIẾT và sai; timeout = KHÔNG BIẾT); cấm đặt timeout ≥
  `lease_ttl_analysis`.
- `retry_budget_refs.entries`: 5 → 9, thêm bốn budget mới.
- `crash_after_provider_completion_timeline`: t1 nay ghi "đồng hồ deadline theo task_type bắt đầu chạy",
  t2 ghi "HOẶC deadline hết trước khi response về — hết giờ cho cùng kết luận: KHÔNG BIẾT".

## C3. Evidence

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC03-08` | `PYTHONDONTWRITEBYTECODE=1 python3 <scratch>/w4/lint_pc03.py` | **PASS** — `budgets=45` (41 → 45), `refs=25` (21 → 25), mọi budget đủ value/unit/status/rationale/retried_by, mọi `retry_budget_ref` resolve; năm state machine không đổi số hàng; `codes=28` | **0** |

type `SELF_VALIDATION`; started/ended UTC 2026-09-06T18:45Z / 18:46Z.
Đã validate ngược lại: `contracts/ports.yaml` `100c94c1…`, `contracts/errors.yaml` `3201bbe8…`.
Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.
Giới hạn: lint kiểm SỰ CÓ MẶT của lý do và các ràng buộc số học, không kiểm ba con số 120/300/180 có đúng với
model thật — chúng là `PROVISIONAL` và cần số thật sau M3 (REQ-A5 vẫn `KC`).

## C4. Concerns

1. **PC06 sở hữu ngữ nghĩa task; PC03 chỉ sở hữu ngân sách.** Ba timeout được đặt theo `task_type` của
   `entities.yaml`. Nếu PC06 thêm task type thứ tư, nó cần một budget tương ứng, nếu không
   `ai_inference_timeout_semantics` không có giá trị áp dụng cho task đó.
2. **Ba con số là PROVISIONAL và chưa có dữ liệu thật.** REQ-A5 (điều khoản/hành vi từng nhà AI) vẫn `KC`.
   Chúng nên được hiệu chỉnh sau M3 cùng lúc với ngưỡng của REQ-A2/A3.

---

# ADDENDUM — PKT-PC03-FIX3

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03-FIX3` (CR-PC10-02) |
| authority_id | `AUTH-COORD-PC03-FIX3` · lease `LEASE-PC03-e4` (**fencing 4**) |
| worker principal | `worker-W4` |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-06T19:10Z / 2026-09-06T19:23Z |
| next actor | Coordinator |

## E1. Changes (MODIFY, baseline = hash sau FIX2)

| Path | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `contracts/state/run.yaml` | `fcad82589aaee43fb15735b10fc7fd7d25c7e94af6e32295aca40a4b0d88999d` | `9b7366495f32580b34aa1880e8f671fbb9bef1770c3246e743037db1fee35abe` | 86734 → 91146 |
| `contracts/errors.yaml` | `3201bbe86a3ef373a4fb35c265cd9f27ed60f6ce2af3fd65a76c0dcfb032d86b` | `b63eef7abd4cee328581e5e06cbc8314e60e52e03468dbe6acea42a0a843ad26` | 59570 → 62269 |
| `contracts/retry-policy.yaml` | `8e2bd87a61b4a8f79429d1ca9662adc4cbe07a0299ef343b0a23a18a5bc39f37` | `75230a2d86d594e2324c008828b09b3ab267fea0b352921fb52c1fd92b15538d` | 39738 → 41612 |

Versions → `run.yaml 0.3.0`, `errors.yaml 0.3.0`, `retry-policy.yaml 0.4.0`.

## E2. Delta

1. **`stop_reason: rate_limited`** thêm vào enum (8 giá trị), kèm đoạn giải thích vì sao nó KHÔNG được gộp
   vào `source_blocked`: rate limit nghĩa là X **có** cho vào nhưng bảo chậm lại; `source_blocked` nghĩa là X
   **không** cho vào. Đây chính là mâu thuẫn ba-cách-hiểu mà CR-PC10-02 nêu.
2. **`T-RUN-25`** — `running/collecting` → `running/enriching`, `stop_reason = rate_limited`. Đóng collection
   segment, giữ checkpoint đã ACK, **đi tiếp** với dữ liệu đã có, outcome dự kiến `partial`. **Không** alert
   intent (khác T-RUN-09 và T-RUN-24 — đây là tình huống vận hành thường gặp, không cần người xử lý ngay).
   Đợt theo lịch kế tiếp chạy bình thường.
3. **`run.rate_limited_at`** (timestamp_utc_ms, nullable) thêm vào `coverage_metadata`; NOT NULL khi
   `stop_reason = rate_limited`, và `x_coverage_note_vi` **bắt buộc** nhắc mốc đó — đúng dạng
   "rate limited at &lt;ts&gt;" mà ruling yêu cầu.
4. **`RATE_LIMITED` trong `errors.yaml`**: `operations` nay có **`worker.report_stop`** và
   `research.get_connector_health` (cùng ba op cũ). Target state cho machine `run` đổi từ
   `status=blocked, stop_reason=source_blocked` → `status=running, phase=enriching, stop_reason=rate_limited,
   outcome dự kiến=partial`. Thêm khối **`retry_class_by_source`**: `retryable_with_budget` áp cho nguồn do
   **server** gọi (research connector, provider AI); với **collector/X** lớp hiệu lực là **`none` trong phạm vi
   đợt** — "retry" là đợt theo lịch kế tiếp. Ghi rõ vì sao tách: gộp lại sẽ hoặc cho collector thử lại trong
   đợt (lách giới hạn), hoặc bắt connector từ bỏ ngay lần đầu.
5. **`retry-policy.yaml`**: budget mới `x_rate_limit_in_run_retries = 0`, trạng thái **`XN_derived`** chứ
   không PROVISIONAL — SRC-SPEC §9.3 đã chốt (XN). Thêm một hàng `never_retry` cho `rate_limited` với
   escape hatch là đợt kế tiếp, và cấm "rút ngắn khoảng cách tới đợt kế tiếp" như một retry trá hình.
6. **Sửa mâu thuẫn phát sinh: `T-RUN-16`.** Guard cũ nhận cả "rate limit kéo dài quá budget" → `blocked`.
   Sau khi thêm T-RUN-25, hai hàng sẽ cùng nhận một sự kiện với hai kết quả khác nhau. Nhánh rate-limit đã
   được **bỏ khỏi T-RUN-16** và `RATE_LIMITED` bỏ khỏi `error_codes` của hàng đó; lý do ghi tại chỗ. Thêm một
   hàng `forbidden_transitions`: `running → blocked` chỉ vì rate limit là **cấm**.

## E3. Evidence

`PYTHONDONTWRITEBYTECODE=1 python3 <scratch>/w4/lint_pc03.py` · **exit 0** · **RESULT: PASS**
`SELF_VALIDATION`, 2026-09-06T19:20Z–19:21Z. `run`: 8 states / **27 rows** (26 → 27) / 25 events /
reachable 8/8; `report` 8; `analysis` 13; `delivery` 10; `storage` 9; `codes=28`;
`refd_by_upstream=26`; `budgets=46` (45 → 46), refs 25.
Validate ngược lại: `contracts/ports.yaml` `87c95da4…` (W2 đang land PKT-PC01-FIX6).
Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.

## E4. Concerns

1. **`collector-probe.md` ST-4 KHÔNG khớp — file của PC05, ngoài MODIFY grant của packet này.**
   ST-4 hiện ghi: *"`RATE_LIMITED`; kéo dài quá ngân sách ⇒ `blocked`"* — đúng hành vi **cũ**, nay đã bị
   ruling bãi bỏ. Đúng phải là: đóng segment, `stop_reason = rate_limited`, run **đi tiếp**, outcome `partial`,
   không `blocked`. Ngoài ra bảng ghi nhận §5 của probe khai enum `stop_reason` cục bộ gồm
   `limit_reached | captcha | session_expired | source_blocked | parser_degraded | operator_stop` — **thiếu
   `rate_limited`**, và còn dùng `parser_degraded` trong khi ST-7 của chính nó đã chuyển sang
   `source_layout_changed` ở FIX1. Cả hai cần một packet PC05 để sửa; **tôi không sửa vì ngoài grant.**
2. **`ports.yaml` chưa có mã/stop_reason tại `87c95da4…`** — W2 đang land PKT-PC01-FIX6. Cặp
   `worker.report_stop.error_codes ∋ RATE_LIMITED` và `stop_reason ∋ rate_limited` cần Auditor kiểm ở lần
   freeze sau.
3. **Đây là thay đổi HÀNH VI, không phải làm rõ.** Trước FIX3, rate limit kéo dài đưa run về `blocked` (cần
   Owner gỡ tay); nay run tự đi tiếp và đợt sau chạy bình thường. Fixture hay card nào đang khẳng định hành vi
   cũ cần được rà lại — tôi không tìm thấy fixture nào trong `acceptance/fixtures/collection/` khẳng định điều
   đó (không fixture nào phủ nhánh rate limit), nhưng **tôi không rà năm thư mục fixture còn lại**.
4. **Không CR mới.**

---

# ADDENDUM — PKT-PC03-FIX4

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03-FIX4` (R5-04 / CR-PC09-04; R5-03 / CR-PC09-03) |
| authority_id | `AUTH-COORD-PC03-FIX4` · lease `LEASE-PC03-e5` (**fencing 5**) |
| worker principal | `worker-W4` · status **DONE** · claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-07T00:16Z / 2026-09-07T00:26Z |
| next actor | Coordinator |

**Ghi chú tiếp nối.** Lượt trước bị cắt bởi rate limit của API **trước khi có write nào**. Tôi đã xác minh lại
trước khi làm: hai file mục tiêu còn nguyên hash sau FIX3 (`analysis.yaml d20df152…`, `run.yaml 9b736649…`),
`acceptance/fixtures/e2e/` chưa tồn tại, không addendum nào đã ghi. Nguồn pinned kiểm lại: khớp.

## G1. Changes (MODIFY, baseline = hash sau FIX3)

| Path | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `contracts/state/analysis.yaml` | `d20df15250cc262d20abb5ae8283c0b9656494b9fce69696114f830eb3f4492b` | `978004cd0bc4781d9e4c08160e9d93dbd2ad4c28c0a0b9fcc1f1e2d5457d7744` | 30405 → 31962 |
| `contracts/state/run.yaml` | `9b7366495f32580b34aa1880e8f671fbb9bef1770c3246e743037db1fee35abe` | `852da496e72aada16853dffd52115f54d22507e022c923ed35f903f5619133eb` | 91146 → 91724 |

`analysis.yaml` → `0.3.0`; `run.yaml` → `0.4.0`.

## G2. Delta

**R5-04 — `TSR-A01` (contracts/state/analysis.yaml).** Câu cũ khẳng định *"Từ `valid` KHÔNG CÓ transition đi
ra"* trong khi bảng transition của **chính file đó** có `T-AN-12` và `T-AN-13` đi ra từ `valid`. Nay:
`valid` là terminal **trong phạm vi một generation**, và hai transition duy nhất rời khỏi nó là T-AN-12
(reanalysis / paper có phiên bản mới → generation MỚI, giữ bản cũ) và T-AN-13 (merge identity → một hàng
thành `superseded_by_merge`). Thêm `wording_correction_vi` nói rõ vì sao câu cũ sai và rằng SRC-PLAN §11 PC03
đã lường trước bằng cụm *"trừ comment retry via new generation"*; thêm `generation_scope_vi` định nghĩa
"trong phạm vi một generation" bằng `analysis_key` để phát biểu kiểm được. `oracle_vi` mở rộng: counter
KHÔNG tăng cho cùng `(analysis_key, generation)`, nhưng reanalysis **được phép** làm nó tăng dưới một
`generation_number` mới — REQ-AC06 chỉ cấm gọi lại khi **đổi tag**, không cấm reanalysis có chủ đích.

**R5-03 — `REQ-S5.4-03` (contracts/state/run.yaml).** Thêm vào `requirement_refs` của file và của hàng
`T-RUN-10`, và vào `guard_vi` của hàng đó: guard chỉ thoả được **sau khi** bước 3 của luồng can thiệp đã xảy
ra NGOÀI hệ thống — người dùng ngồi trước máy cá nhân, xử lý trong cửa sổ Chrome đang mở. Đó chính là lý do
resume là hành động của người chứ không phải một retry theo thời gian: hệ thống không quan sát được cửa sổ
Chrome đó. Trích dẫn này biến REQ-S5.4-03 từ PARTIAL thành COVERED bởi một hàng transition thật, không phải
bởi một dòng tham chiếu trống.

## G3. Evidence

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC03-09` | `PYTHONDONTWRITEBYTECODE=1 python3 <scratch>/w4/lint_pc03.py` | **PASS** — run 27 rows / 25 events / reachable 8/8; analysis 13 rows / 6/6; report 8; delivery 10; storage 9; codes 28; budgets 46 | **0** |
| `EV-PC03-10` | `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py` (read-only, công cụ của PC09) | **`E0-09-state-lint`: checked=67, violations=0, PASS** — "closed state enums, reachability, terminal states have no outgoing rows". Đây là kiểm ĐỘC LẬP VỚI script của tôi và nó xác nhận TSR-A01 sau khi sửa không còn mâu thuẫn với bảng transition | 0 |

`SELF_VALIDATION` (E0). 2026-09-07T00:24Z–00:25Z.
Toàn bộ e0_check: 19 check, **PASS 18 · FAIL 1**. FAIL duy nhất là `E0-10b-denied-edge-oracle` (26 forbidden
edge chưa có `denied_cases[]` với `expected_error_code`) — **thuộc `contracts/modules.yaml` của W2, đang land
song song**, không thuộc file nào của tôi.
Nguồn pinned khớp hai đầu: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.

## G4. Concerns

1. **`E0-09-state-lint` trước FIX4 cũng PASS**, dù TSR-A01 khi đó mâu thuẫn với bảng transition. Lý do:
   check đọc bảng `transitions` và tập `terminal_states`, còn `TSR-A01` là **prose**. Mâu thuẫn nằm đúng ở
   chỗ gate không nhìn tới — cùng loại với `parser_degraded` sống sót hai vòng ở PC05. Đây là giới hạn của E0
   nói chung, không phải lỗi của e0_check.
2. **`valid` vẫn nằm trong `terminal_states` của analysis.yaml** và lint của tôi vẫn cho phép T-AN-12/T-AN-13
   đi ra khỏi nó bằng một ngoại lệ khai tường minh trong script. Sau FIX4, prose và ngoại lệ đó đã nói cùng
   một điều. Nếu Coordinator muốn chặt hơn, cách đúng là một trường `terminal_scope: per_generation` thay cho
   một ngoại lệ trong checker — **ngoài scope packet này**.
3. **Không CR mới.**

---

# ADDENDUM — PKT-PC03-FIX5

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03-FIX5` (E0-04c, run `E0-20260907T014517Z`, phát hiện (a)) |
| authority_id | `AUTH-COORD-PC03-FIX5` · lease `LEASE-PC03-e6` (**fencing 6**) |
| worker principal | `worker-W4` · status **DONE_WITH_CONCERNS** · claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-07T01:48Z / 2026-09-07T01:55Z |
| next actor | Coordinator |

## I1. Changes (MODIFY, baseline = hash sau FIX4)

| Path | Before | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `contracts/state/run.yaml` | `852da496…` | `c92e7c4e6fc6dce8a0280e64a182c1463a1e7a4b07d3c26f8036e37fd34579ec` | 91724 → 91779 |
| `contracts/state/report.yaml` | `5e2ce6cf…` | `2b22c27df302c7fbf733b352ad41390a1d407ac98cfa7b1a816cf3580349aba0` | 27115 → 27154 |
| `contracts/state/analysis.yaml` | `978004cd…` | `bf961c0fdb36d98613791ac537370b5ca07746b18e8a27f7cf79c0eb953b9f3f` | 31962 → 31981 |
| `contracts/state/storage.yaml` | `608ceea6…` | `f67e78f528a13b768b97ab72f55542ac9bac439b8f5472e8e03247b41dae72c2` | 27011 → 27018 |
| `contracts/retry-policy.yaml` | `5e083230`(trước: `75230a2d…`) | `5e083230e2cc5db481736adcf189a6cf8e302ebdf45cad614582731698cf06d5` | 41612 → 41620 |

`contracts/state/delivery.yaml` (`9fcccc25…`) và `contracts/errors.yaml` (`b63eef7a…`) **không đổi** — nằm
trong grant nhưng không có token nào cần sửa. Versions: run `0.5.0`, report `0.3.0`, analysis `0.4.0`,
storage `0.2.0`, retry-policy `0.5.0`.

## I2. Delta — chín token, không phải một

Packet nêu (a) `coverage_window.predecessor`. Chạy gate đầy đủ theo
`contracts/ports.yaml conventions.prose_token_rule_vi` trên cả bảy file PC03 cho **13 token không giải được**,
trong đó **9 là lỗi thật** cùng loại và 4 là khóa YAML hợp lệ:

| Token cũ | Sửa thành | Vì sao sai |
| --- | --- | --- |
| `coverage_window.predecessor` (run ×2, report ×1) | `coverage_window.predecessor_window_id` | Cột thật có hậu tố `_window_id`. **Đây là (a) của packet.** |
| `predecessor.window_to` (run, report) | `` `coverage_window.window_to` của kỳ predecessor `` | `predecessor` không phải entity; đây là một HÀNG của `coverage_window` |
| `delivery.status` (run ×2) | `delivery.state` | Cột thật là `state`. AMD-B02 viết `delivery.status`; bảng ánh xạ trích amendment nhưng phải dùng TÊN CỘT THẬT, nếu không một người triển khai sẽ đi tìm một cột không tồn tại |
| `delivery.unknown` (run, analysis, retry-policy) | `delivery.state = unknown` | `unknown` là một GIÁ TRỊ của `state`, không phải một cột |
| `lease.expires_at` (analysis) | `assignment_lease.expires_at` | Entity thật là `assignment_lease` (ruling R-03); `lease` là token cũ của PC01 |
| `storage.maintenance` (storage) | `storage.health = maintenance` | `maintenance` là giá trị của kênh `storage.health`, không phải một cột |

Bốn token còn lại — `budgets.schedule_slots_default`, `legacy_enum_mapping.ui_three_states_vi`,
`sender_lease.storage_guard_vi`, và `storage.health` — là **khóa YAML trong chính file hợp đồng** (loại 2) và
**ngoại lệ có tên** của ruling. Chúng được khai vào danh sách ngoại lệ của gate **kèm căn cứ**, không được sửa.

## I3. Evidence

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC03-11` | `<scratch>/w4/prose_token_gate_w4.py` | **PASS** — PC03 (7 file): **440** token giải thành operation, **169** thành `entity.column`, **38** ngoại lệ có căn cứ, **UNRESOLVED = 0** | **0** |
| `EV-PC03-12` | `<scratch>/w3/prose_token_gate.py` (gate của W3, đọc-only) trên cùng 7 file | **440 / 169 — TRÙNG KHÍT** với gate của tôi. 38 token W3 báo "không giải được" đúng bằng 38 ngoại lệ của tôi (`storage.health` ×6, ba khóa YAML, `author.handle`), vì bản của W3 chưa hiện thực bốn lớp ngoại lệ và ngoại lệ có tên mà ruling FIX7 cho phép | 1 (do W3 chưa có lớp ngoại lệ) |
| `EV-PC03-13` | `<scratch>/w4/lint_pc03.py` | **PASS** — không hồi quy | 0 |
| `EV-PC03-14` | `evidence/tools/e0_check.py` | **22 check, PASS 22, FAIL 0, violations 0** — toàn corpus xanh | 0 |

Gate của tôi có **negative self-test kế thừa từ W3**: hai token đột biến
(`ingest.submit_batch_MUTATED`, `post.x_post_id_MUTATED`) đều BỊ BẮT, nên `UNRESOLVED = 0` không phải do gate
mù. Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`. Nguồn phân giải:
`ports.yaml 93ba1598…`, `entities.yaml c2ceeafd…` — đúng hai bản packet chỉ định.

## I4. Concerns

1. **18/18 card của PC10 nay có pin hash cũ** cho các file tôi vừa sửa. Cụ thể: `retry-policy.yaml` xuất hiện
   trong **18** card; `openapi.yaml` 15; `run.yaml` 6; `report.yaml` 4; `storage.yaml` 4; `analysis.yaml` 2.
   `CR-PC10-01` đã yêu cầu re-pin toàn bộ sau `FC-W4`; đợt sửa này làm việc đó **bắt buộc**, không còn tùy chọn.
2. **`delivery.status` đến từ AMD-B02 nguyên văn.** Tôi đã đổi sang `delivery.state` trong bảng ánh xạ của
   `run.yaml` để token giải được. `precode/decision-register.md` vẫn giữ câu chữ gốc — đó là văn bản lịch sử và
   không thuộc grant của tôi; nếu Coordinator muốn hai nơi khớp nhau thì cần một packet PC00.
3. **Không CR mới.**
