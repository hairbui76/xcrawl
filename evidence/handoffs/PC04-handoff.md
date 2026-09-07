# HANDOFF — PKT-PC04 (Khóa thời gian, tag, coverage và chọn hướng nghiên cứu)

## 1. Identity

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04` |
| worker principal | `worker-W5` |
| authority_id | `AUTH-COORD-PC04` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC04-e1` (exclusive, fencing 1), `expires_at` 2026-09-07T04:00Z |
| enforcement_mode | `DOCUMENTARY_DRAFT` — chưa có OS enforcement; lease theo thông điệp |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| lý do không phải `DONE` | (1) Dependency baseline (`contracts/data/entities.yaml`, `ports.yaml`, `modules.yaml`) đổi **trong lúc** gói chạy — xem §6. Sources không đổi nên stop gate baseline §2 không kích hoạt, nhưng candidate cần re-verify trước khi freeze. (2) Quyết định CR-PC03-06 (§7.5) **không** theo khuyến nghị của Coordinator; cần Coordinator xác nhận hoặc bác. |
| next actor | `Coordinator` |
| lease_released_at | 2026-09-06T18:08Z |

## 2. Changes — mọi file đều `CREATE`, baseline `ABSENT`

| Path | Operation | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/reporting/time-and-tags.md` | CREATE | ABSENT | `652854d8bc681c6296f0b098e5db5e108653ce2f21c4c728df75199a04bc9d0f` | 56448 |
| `contracts/reporting/selection.md` | CREATE | ABSENT | `fca9a9a55edf1b0e360ca29161d586ac1e35f04ffb020103bad8a992fc78215c` | 32755 |
| `contracts/schemas/report.schema.json` | CREATE | ABSENT | `a8662d5d27b03724c27cef2959cb0a978713746da7733304fba6047e0c12000d` | 29805 |
| `acceptance/fixtures/reporting/README.md` | CREATE | ABSENT | `a536e16f014064e38e96e167f9c2f0b812f07ca29a326dba03dd37a3876c5e04` | 10923 |
| `acceptance/fixtures/reporting/a-tag-removed-before-publish.json` | CREATE | ABSENT | `e299df1809b789405618a9b71d791f46f864bb5d5d86e8b480b4794a197a3b57` | 14958 |
| `acceptance/fixtures/reporting/b-tag-removed-then-readded-reuse-analysis.json` | CREATE | ABSENT | `fd05b877ed22011f312eb89a40468b322351bf3c38ee5a573d2928284a61ab18` | 15411 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | CREATE | ABSENT | `72d056e7518159261ed6d53248ec9a602d6c3b3353b89141b2be08d9f9984f32` | 4810 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | CREATE | ABSENT | `d5b482071daec6c1ad8ba512645183c9cfa0647862dffc5867bc8b4797109d2f` | 6627 |
| `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` | CREATE | ABSENT | `2d084ee293a7e45f33f2a9275e20811b3f719d86221602687112b556f0f43458` | 9992 |
| `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json` | CREATE | ABSENT | `349ec81129cf00cb1d4dfccf148584fb70e2f548f621a73259bb6941af032788` | 12536 |
| `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json` | CREATE | ABSENT | `d0f5c946da6de5e61133b98e4b6e05bd6ea618e6c45f989c2f386e9db349fc1d` | 4981 |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | CREATE | ABSENT | `9b17869b772144ebc1a3177aa642d135287ad1c109062404bf10951b7fb19f5b` | 8910 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | CREATE | ABSENT | `9d260f0a198be9c092bc17ba04b3e491507c22abf1f35fe1d697a6af8527a9f9` | 14191 |
| `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json` | CREATE | ABSENT | `654014d57823a4e1510ebc97270d2577fb376e991e5b3717b4955efd218935c6` | 5737 |
| `acceptance/fixtures/reporting/k-builder-crash-backfill-not-consumed.json` | CREATE | ABSENT | `61d41043a347c75422c67a4f0160c8405ce8853585937e51b5c36e952305c7c9` | 5065 |
| `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json` | CREATE | ABSENT | `f53ec831634b17c3d74e74d988d6a865af2e55e2719a4448d745aec6d2441ddd` | 5803 |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | CREATE | ABSENT | `5f1183e7d256665e1110834ce6a64d056db0beedfb9c67d06428bc12e2751680` | 28211 |
| `evidence/handoffs/PC04-handoff.md` | CREATE | ABSENT | (file này) | — |

Hai thư mục được tạo: `contracts/reporting/`, `acceptance/fixtures/reporting/`.
**Không** file nào ngoài danh sách trên bị ghi. Không chạy lệnh git mutate. Không network.
`PYTHONDONTWRITEBYTECODE=1`; mọi script chạy từ scratch dir
`/tmp/claude-1001/-mnt-virtual-repo-xcrawl/f814fa10-fc35-4a28-8689-61e9f77408cd/scratchpad/w5/`;
không có `__pycache__` hay artifact nào sinh ra trong repo.

## 3. Source và dependency baseline đã dựa vào

### 3.1 Sources — khớp baseline §2 ở cả hai lần kiểm (trước khi bắt đầu và trước handoff)

| Ref | Path | SHA-256 | Kết quả |
| --- | --- | --- | --- |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | **khớp** |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | **khớp** |

### 3.2 Dependency — giá trị quan sát **tại thời điểm handoff**

| Path | SHA-256 tại handoff | Ghi chú |
| --- | --- | --- |
| `contracts/data/entities.yaml` | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | **đã đổi ≥2 lần trong lúc PC04 chạy** — §6 |
| `contracts/ports.yaml` | `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` | đã đổi |
| `contracts/modules.yaml` | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` | đã đổi |
| `contracts/data/identity.md` | `01976cabe4dae4e587cb0e555ca6a0176c5726c0815207bb04287cb5d1169571` | khớp manifest FC-W1 |
| `contracts/schemas/target.schema.json` | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` | khớp manifest FC-W1 |
| `contracts/errors.yaml` | `e236aaee44cb340bf58ab822ab3dc434847e3d777b46c5b97b3baf00bd0e1b37` | PC03, xuất hiện giữa chừng |
| `contracts/retry-policy.yaml` | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` | PC03, xuất hiện giữa chừng |
| `contracts/state/report.yaml` | `e60ef74f438faa7119d56950f8ab7ac8170df2c9c70f0b8b3d956e0412e79ced` | PC03, xuất hiện giữa chừng; nguồn của T-RP-01…07, `publish_cas`, ba vị từ PC04 phải cấp |
| `contracts/state/run.yaml` | `8acb7bbf935ee6854fa41d52604972929f09843838c1c141d861d17f538f3468` | PC03; `run.outcome = 'empty'` của kỳ rỗng |
| `contracts/state/analysis.yaml` | `73be908d0da32fb217dd45b1f296d4e10954ec7b2507c689c9e73693a9761254` | PC03; đọc để không mâu thuẫn với `pending_item_ledger.reason` |
| `precode/decision-register.md` | `0a64b05095a44ded2ab94ff405881ffe09e26d1277928503d49b1643d101f4c6` | đã đổi so với manifest FC-W1 (`9f212849…`) |
| `precode/requirements.csv` | `1bf60a1c54721adeedc7bc13b0313fd409d064bb3d3f44283b24885f584b9dbb` | đã đổi so với manifest FC-W1 (`e9876497…`) |

## 4. Evidence records

Tất cả là `SELF_VALIDATION` do `worker-W5` tạo. Runtime: Python 3.12.3, `jsonschema` 4.10.3
(Draft 2020-12 + `RefResolver`), `PyYAML` 6.0.1, Linux 7.0.0-30-generic. Không network.
Cấp bằng chứng: **E0** theo SRC-PLAN §14.2. **E1–E4 = `NOT_RUN`** (chưa có code, chưa có dữ liệu
thật, chưa gọi provider AI, chưa gửi Telegram).

### EV-PC04-01 — schema báo cáo + parse fixture + validate `expected.report`

- Command: `python3 <scratch>/w5/validate.py`
- Started/ended UTC: chạy lại nhiều lần trong quá trình căn chỉnh; lần cuối 2026-09-06T18:12Z (sau khi áp quyết định CR-PC03-06)
- Input: `contracts/schemas/report.schema.json` (`a8662d5d…`), `contracts/schemas/target.schema.json` (`436cb97b…`), 13 file fixture (hash ở §2)
- Oracle: (a) `Draft202012Validator.check_schema(report.schema.json)` không ném lỗi; (b) mọi fixture parse được thành JSON; (c) mọi object dưới khóa `report` trong `expected` (kể cả `expected.<variant>.report`) validate theo `report.schema.json`, với `target.schema.json` nạp vào `RefResolver` store để `$ref` theo `$id` giải được
- Expected: 0 lỗi; ≥ 8 report object được validate
- Observed: `PASS metaschema`; 13/13 fixture parse; **8/8** report object validate; `report objects validated: 8`
- Exit code: `0` · Status: **PASS**
- Limitations: chứng minh **hình dạng wire tự nhất quán**, không chứng minh ngữ nghĩa đúng, không chứng minh code chạy được. Không có bộ validate độc lập nào chạy — đây **không** phải independent audit.

### EV-PC04-02 — tính lại ví dụ mật độ và đối chiếu với `selection.md` §8.7

- Command: `python3 <scratch>/w5/density_check.py`
- Input: `acceptance/fixtures/reporting/m-density-worked-example.json` (`5f1183e7…`), `contracts/reporting/selection.md` (`fca9a9a5…`)
- Oracle: script tự tính lại từ **góc** của từng vector (không đọc số đã ghi): vector, cosine từng cặp, láng giềng bán kính `r = 0.8000`, gom nhóm tham lam tất định, centroid chuẩn hóa L2, đếm thành viên các kỳ trước, `density_now/prior/delta/ratio`; rồi so **bằng nhau tuyệt đối** với giá trị trong fixture, và kiểm các con số có mặt nguyên văn trong `selection.md` §8.7
- Expected: `member_target_keys` = 4 khóa `T1..T4`; `centroid = [0.9315, 0.3638, 0, 0]`; `density_now = 4`; `density_prior = 0.6667`; `density_delta = 3.3333`; `density_ratio = 4.0`; nhóm bị loại có `m_t = 2`; `evidence_state = sufficient`
- Observed: **trùng khớp toàn bộ**; 8/8 chuỗi số của §8.7 (`0.6667`, `3.3333`, `4.0000`, `0.9315`, `0.3638`, `0.9062`, `0.3539`, `0.9728`) có mặt trong `selection.md`
- Exit code: `0` · Status: **PASS**
- Limitations: chứng minh **tính tái lập của phép tính**, tuyệt đối **không** chứng minh thuật toán hữu ích. REQ-A4 vẫn `KC`; cần 3–4 kỳ dữ liệu thật và đánh giá của Owner.

### EV-PC04-03 — mọi operation_id / module / entity được trích dẫn đều tồn tại upstream

- Command: `python3 <scratch>/w5/refs.py`
- Input: 13 fixture; `contracts/ports.yaml`, `contracts/data/entities.yaml`, `contracts/modules.yaml` (hash §3.2); quét thêm token dạng `x.y` trong backtick của hai file markdown PC04
- Oracle: mọi `events[].operation` ∈ tập `operation_id` của `ports.yaml`; mọi `events[].actor` bắt đầu `MOD-` ∈ tập module của `modules.yaml`; mọi khóa của `given.rows` / `expected.*.rows` ∈ tập `entities[].name` của `entities.yaml`
- Expected: 0 MISS
- Observed: 16/16 operation OK; 11/11 module OK; 13/13 tên bảng OK (gồm `first_announced_ledger`, `rescan_ledger` — **đã có** trong `entities.yaml` bản mới)
- Exit code: `0` · Status: **PASS**
- Limitations: kiểm **sự tồn tại của tên**, không kiểm ngữ nghĩa của lời gọi, không kiểm auth scope hay chiều gọi (đó là PC01/PC09).

### EV-PC04-04 — coverage nửa mở và nối liền

- Command: `python3 <scratch>/w5/coverage_check.py`
- Input: 13 fixture
- Oracle: với mọi cửa sổ tìm thấy trong `given`/`expected`/`expected.report.coverage`: (a) `window_to > window_from` (nửa mở, chặt); (b) `ingest_sequence_from <= ingest_sequence_to`; (c) nếu `predecessor_window_id` trỏ tới một cửa sổ có trong cùng fixture thì `window_from = predecessor.window_to` **và** `ingest_sequence_from = predecessor.ingest_sequence_to`
- Expected: 0 FAIL
- Observed: **24 cửa sổ** kiểm, 0 FAIL; chuỗi liên tục qua kỳ rỗng (fixture `d`) và qua kỳ gộp chạy bù (fixture `f`) đều nối liền
- Exit code: `0` · Status: **PASS**
- Limitations: kiểm dữ liệu fixture, **không** kiểm một triển khai nào.

### Không chạy

| Hạng mục | Trạng thái | Lý do |
| --- | --- | --- |
| E1 contract test bằng fixture | `NOT_RUN` | Chưa có code (SRC-PLAN §7 `NOT_READY_FOR_PRODUCT_CODE`) |
| E2 integration + fault injection | `NOT_RUN` | Như trên |
| E3 live probe | `NOT_APPLICABLE` cho PC04 | Không fixture nào cần X/AI/Telegram thật |
| E4 review nội dung nhiều kỳ | `NOT_RUN` | REQ-A4 cần 3–4 kỳ dữ liệu thật (PC09) |
| Independent audit | **chưa xảy ra** | `audit_route: INDEPENDENT_REQUIRED`; Coordinator phải định tuyến Auditor |

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Tag freeze point, coverage boundary, `discovered_at`/sequence, backlog, single CAS publisher | **DONE** | `time-and-tags.md` §1 (timestamp + thứ tự tổng), §3 (freeze tại publish), §4.3 (biên theo watermark ingest sequence), §4.5 (transaction), §4.6 (CAS), §5 (backlog) |
| 2 | Alias/exclusion precedence, similarity metric, threshold policy, embedding generation | **DONE** | `selection.md` §3 (cosine + làm tròn), §4 (alias thừa hưởng ngưỡng; exclusion thắng; toàn cục vs phạm vi tag), §5 (ghim generation, I12), §6 (ngưỡng `PROVISIONAL_BOOTSTRAP` + cổng A2) |
| 3 | Backfill ledger + manual rescan, gồm add/remove/re-add và builder crash | **DONE** | `time-and-tags.md` §6 (định danh activation theo chữ tag chuẩn hóa; điều kiện tiêu thụ), §7 (rescan: sổ riêng, 5 ràng buộc âm); fixture `j`, `k` |
| 4 | First-announcement/reference sau merge, phiên bản paper mới, Saved độc lập | **DONE** | `time-and-tags.md` §8.1–§8.5; **đóng CR-PC02-06**; fixture `h`, `i` |
| 5 | Vector density: window, min sample, cold-start, tie-break, label; AI chỉ diễn đạt | **DONE** | `selection.md` §8 (thuật toán 10 bước, tham số có số + lý do, `insufficient_evidence` bắt buộc, ví dụ số §8.7); fixture `m` |
| 6 | Fixture (a)–(m) | **DONE** | 13/13 file trong `acceptance/fixtures/reporting/`, chỉ mục ở README §1 |
| + | CR-PC03-06 (Coordinator giao thêm giữa chừng) | **DONE** | `time-and-tags.md` §4.7.1; quyết định + oracle + cách đảo; §7.5 của handoff này |

### Invariant (yêu cầu packet: mỗi cái có owner section + fixture dương + counterexample)

| Invariant | Owner section | Fixture dương | Counterexample | Trạng thái |
| --- | --- | --- | --- | --- |
| I05 | `time-and-tags.md` §3 | `c` | `a` (O-3.3), `g`, `i` | **DONE** |
| I06 | `time-and-tags.md` §4, §5 | `d`, `f` | `e` (O-5.2), `g` | **DONE** |
| I07 | `time-and-tags.md` §8 | `h` | `i` | **DONE** |
| I12 | `selection.md` §5 | `m` | `l` | **DONE** |
| "Selection stale → rebuild/abort, không mutate report đã publish" | `time-and-tags.md` §3.2–§3.4, §4.6 | `c` | `a` (O-3.3), `l` | **DONE** |

## 6. Baseline drift — lý do status là `DONE_WITH_CONCERNS`

**Quan sát.** `contracts/data/entities.yaml` đổi **ít nhất hai lần** trong khoảng thời gian PC04
chạy:

| Thời điểm | SHA-256 | Bytes |
| --- | --- | --- |
| Lúc PC04 bắt đầu (khớp `audits/FC-W1-manifest.txt`) | `88b2482ede392e581b1d4eb0640bca0810ce94953bd8ada7c9b1e6b7f5ebb8fb` | 121662 |
| Quan sát giữa chừng | `921a5927aeb8cae6d61fda57d6354cd2970e27ef67669c5e1b728cc8fe500704` | 175145 |
| Tại handoff | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | — |

Cùng lúc, `contracts/ports.yaml`, `contracts/modules.yaml`, `precode/decision-register.md`,
`precode/requirements.csv` đổi so với manifest, và `contracts/errors.yaml`,
`contracts/retry-policy.yaml`, `contracts/state/*` xuất hiện (PC03 chạy song song).

**Vì sao không dừng.** Baseline §2 định nghĩa stop gate `STALE_BASELINE` trên **hai file
nguồn**; cả hai vẫn khớp ở cả hai lần kiểm. Baseline §6 chỉ có gate `BLOCKED_DEPENDENCY` cho
dependency **thiếu hoặc không đọc được** — mọi dependency đều đọc được. Vì vậy tôi đã **căn lại
nội dung theo bản upstream mới** thay vì ghi một candidate mâu thuẫn, và báo cáo đầy đủ ở đây.

**Những gì đã phải sửa vì drift** (tất cả đều theo hướng *dùng cái upstream đã có* thay vì tự
định nghĩa):

1. `first_announced_ledger` và `rescan_ledger` **đã tồn tại** trong `entities.yaml` bản mới.
   Tôi đã bỏ hình dạng tự đặt và dùng nguyên văn cột của PC02: `canonical_work_id`,
   `first_report_id`, `first_announced_at`, `merge_audit_id`, `superseded_by_merge_id`,
   `UNIQUE(owner_id, canonical_work_id)`. Policy merge ở §8.3 được viết lại cho khớp.
2. Mã lỗi CAS: bỏ đề xuất `COVERAGE_PREDECESSOR_STALE`; dùng **`CONFLICT`** đã đăng ký trong
   `contracts/errors.yaml` với `retry_budget_ref: cas_conflict_retries` (3).
3. Ngân sách rebuild: bỏ tên tự đặt; dùng `report_build_rebuild_attempts` (2) và
   `report_build_stale_after` của `contracts/retry-policy.yaml`; bỏ đề xuất
   `stop_reason = 'tag_version_churn'` vì `contracts/state/report.yaml` T-RP-03 đã quy định
   "hết ngân sách → run `outcome = partial` với lý do rõ".
4. Kỳ rỗng: `contracts/state/report.yaml` T-RP-07 quy định bản dựng để lại một hàng
   `report(status = 'aborted')`; fixture `d` đã sửa cho khớp (trước đó viết "không tạo hàng report").
5. Không cần cột mới trên `report_item`: mọi trường riêng của PC04 (`matched_tags`,
   `excluded_by`, `late_discovery`, `pending_since_window_sequence`, `selected_via_backfill`,
   `backfill_ledger_id`, `reference_reason`, `work_version_label`, `identity_state`) nằm trong
   cột `json` `report_item.selection_reason` mà `entities.yaml` đã giao cho PC04 khóa hình dạng.
6. Ba vị từ mà `contracts/state/report.yaml` yêu cầu PC04 cung cấp
   (`coverage_predecessor_matches`, `tag_config_version_matches`,
   `embedding_generation_matches`) đã được định nghĩa ở `time-and-tags.md` §4.5.

**Kiểm lại lần cuối.** Ngay trước handoff, các hình dạng bảng mà PC04 phụ thuộc
(`coverage_window`, `pending_item_ledger`, `backfill_ledger`, `rescan_ledger`,
`first_announced_ledger`, `report_item`) đã được đọc lại theo `2235564f…` và **không đổi** so
với lúc căn chỉnh; `report.publish.error_codes` trong `ports.yaml` vẫn **chưa** có `CONFLICT`
(→ CR-PC04-04). Bốn evidence record ở §4 đều chạy lại và PASS sau lần kiểm này.

**Đề nghị Coordinator.** Coi PC04 là candidate cần **re-verify khi freeze**: nếu
`entities.yaml`/`ports.yaml` đổi tiếp sau `2235564f…`/`485213cb…`, phải chạy lại EV-PC04-01 và
EV-PC04-03 trước khi phát hành `FROZEN_CANDIDATE`. Đề nghị thứ hai: quiesce PC02/PC01 trước khi
freeze bất kỳ gói hạ nguồn nào, vì hiện tại dependency của mọi Worker đang thay đổi trong lúc
họ đang viết.

## 7. Unresolved refs

### 7.1 Change request PC04 phát ra

| ID | Gửi tới | Nội dung | Chặn gì |
| --- | --- | --- | --- |
| `CR-PC04-01` | PC02 | (a) `coverage_window` cần `ingest_sequence_from` / `ingest_sequence_to` — vị từ thành viên thật sự của một kỳ; biên thời gian một mình không an toàn khi một transaction ingest commit muộn hơn snapshot. (b) Thu hẹp ràng buộc `first_announced_ledger.canonical_work_id` "phải là work active" xuống chỉ hàng có `superseded_by_merge_id IS NULL`. (c) `modules.yaml` gọi bảng coverage là `coverage_ledger`, `entities.yaml` gọi `coverage_window` — đề nghị thống nhất | Không chặn văn bản; chặn E1 |
| `CR-PC04-02` | PC02 | `backfill_ledger` cần `subscription_identity_hash`, `entitlement`, `entitlement_reason`, `UNIQUE(owner_id, subscription_identity_hash) WHERE consumed_in_report_id IS NOT NULL`. Không có chúng, quy tắc add–remove–re-add **không thực thi được** ở mức schema vì `ux_backfill_tag_activation` khóa theo `tag_id`, mà mỗi lần thêm lại sinh `tag.id` mới | Chặn oracle O-6.1 ở E1 |
| `CR-PC04-03` | PC02 | Ghi quy tắc kẹp đơn điệu giữa `discovered_at` và `ingest_sequence` vào `conventions.clock_trust` | Chặn oracle O-1.3 |
| `CR-PC04-04` | PC01 | `contracts/ports.yaml` → `report.publish.error_codes` **chưa** có `CONFLICT`, trong khi `contracts/errors.yaml` khai `CONFLICT.operations` **có** `report.publish`. Hai file lệch nhau | Chặn E0 của PC09 (reference integrity) |
| `CR-PC04-05` | PC06 | Task `direction_phrasing` chỉ **diễn đạt lại** object đã tính; cấm AI chọn thành viên, tính mật độ, hay đổi nhãn khỏi "ứng viên để đọc sâu". Khối phải hiển thị được khi task này lỗi | Chặn AC-16 nếu bật diễn đạt qua CLI |
| `CR-PC04-06` | PC09 | Đăng ký `SC37` (backfill add→remove→re-add) và `SC38` (builder crash không tiêu thụ backfill) vào `acceptance/scenarios.yaml`. PC02 đã dùng `SC29`–`SC31`, PC03 đã dùng tới `SC36`, nên PC04 lấy `SC37+` theo chỉ dẫn của Coordinator | Chặn traceability G4 |
| `CR-PC04-07` | PC07 | UI phải hiện số mục ước tính trước khi chạy `tag.rescan_corpus` — đây là đường duy nhất làm chi phí AI tỉ lệ với số bài trong kho thay vì số mục báo cáo (SRC-SPEC §10.4) | Không chặn |
| `CR-PC04-08` | PC03 | Kết quả CR-PC03-06 (§7.5): giữ hàng `report(status='aborted')` cho kỳ rỗng nhưng **bắt buộc** `abort_reason`. Đề nghị PC03 ghi `abort_reason` vào T-RP-03/04/05/06/07 để `aborted` không nhập nhằng giữa "kỳ rỗng hợp lệ" và "build hỏng" | Chặn oracle I13 ở E1 |
| `CR-PC04-09` | PC02 | Thêm cột `report.abort_reason` (enum `empty_period` \| `tag_version_stale` \| `embedding_generation_mismatch` \| `cas_lost` \| `builder_crash_or_stale`), `NOT NULL khi status='aborted'` | Chặn CR-PC04-08 |

### 7.2 CR đã đóng

`CR-PC02-06` (policy `first_announced` sau identity merge) — **đóng** bởi
`contracts/reporting/time-and-tags.md` §8.3. Quyết định `PROVISIONAL`: work thắng kế thừa
first-announcement **sớm nhất**; hàng của work thua được giữ với `superseded_by_merge_id` làm
bằng chứng; report đã publish **không** bị viết lại; `moved_counts.first_announced` nhận giá trị
`0` / `1` / `2` theo bảng §8.3, và `null` không còn hợp lệ. Đóng I07 cho AC-09.

### 7.3 Quyết định `PROVISIONAL` do PC04 đưa ra (cần Owner phê chuẩn qua OWNER_DECISION_REQUEST)

| # | Quyết định | Nguồn | Phương án bị bác và lý do |
| --- | --- | --- | --- |
| 1 | First-announcement sau merge = **sớm nhất**, có audit | Coordinator recommendation; I07, REQ-D29 | "Bắt đầu lại như chưa công bố" vi phạm REQ-D29; "lấy ngày muộn hơn" hiển thị sai sự thật; "xóa hàng work thua" mất bằng chứng (B15) |
| 2 | Backfill khóa theo **chữ tag đã chuẩn hóa** (`subscription_identity_hash`), re-add **không** cấp lại | SRC-SPEC §8.2 hàng 4 ("Muốn đào sâu hơn thì bấm quét lại kho") | Khóa theo `tag.id` tương đương "cấp lại mỗi lần re-add" vì partial index sinh `tag.id` mới |
| 3 | Backfill tiêu thụ khi publish commit **và** phần nới cho ≥ 1 ứng viên; phần nới rỗng thì entitlement ở lại | SRC-PLAN §9.2 | Tiêu thụ vô điều kiện sẽ đốt entitlement khi crash/khoảng rỗng |
| 4 | Phiên bản arXiv mới = `prior_reference` với `reference_reason = 'new_work_version'`, **không** phải phát hiện mới | identity.md §2.2, I07 | Coi v2 là phát hiện mới phá `UNIQUE` của I07 trên canonical identity |
| 5 | Target chỉ-có-post: "đã công bố" suy ra từ `report_item` của report đã publish (sổ ledger khóa theo `canonical_work_id`) | identity.md §4 | Thêm cột `post_id` vào ledger là một CR nặng hơn mà không thêm bảo đảm nào |
| 6 | Ngưỡng similarity `0.8000` là `PROVISIONAL_BOOTSTRAP` + `threshold_calibration_state = 'uncalibrated'` | REQ-OQ08 nói **không** đặt số như thể đã biết; baseline §3 cấm để "TBD" | Đây là cách duy nhất thỏa cả hai: có số để chạy được và để fixture tất định, nhưng gắn nhãn chưa hiệu chỉnh và cấm tuyên bố chỉ tiêu §1.4 khi còn `uncalibrated` |
| 7 | Tham số mật độ: `r = 0.8000`, `min_members = 3`, `K = 4`, `min_prior_windows = 2`, `min_delta = 2.0000`, `ε = 1.0000`, `max_emerging_directions = 3` | B14 giao PC04 định nghĩa | Mọi giá trị `PROVISIONAL`, cổng REQ-A4; không giá trị nào được coi là đã kiểm chứng |
| 8 | `max_items_per_period = 50` | SRC-SPEC §10.4; REQ-OQ05 chưa có số thật | Vượt hạn mức → `pending_item_ledger(budget_exceeded)`, **không** bị bỏ |

### 7.5 CR-PC03-06 — quyết định của PC04, **không** theo khuyến nghị của Coordinator

Coordinator giao PC04 (chủ sở hữu tầng báo cáo) chọn: kỳ rỗng để lại (a) **không** hàng `report`
nào, hay (b) một hàng `report(status='aborted')` + lý do `empty_period`. Coordinator khuyên (a).

**PC04 chọn (b), với `abort_reason` bắt buộc.** Lý do duy nhất và cụ thể: `report.publish` là
idempotent theo `report_build_id`, nhưng `coverage_window` **không có** cột khóa idempotency
(`id`, `owner_id`, `sequence`, `window_from`, `window_to`, `predecessor_window_id`, `report_id`,
`advanced_at`), và `report_id` của kỳ rỗng là `NULL`. Dưới (a) thì sau một lần mất ACK, replay
cùng `report_build_id` **không tra được receipt nào**, sẽ thử tiến coverage lần hai, thua CAS và
trả `CONFLICT` — đúng loại lỗi SRC-PLAN §5.1 cảnh báo. Dưới (b), hàng `report` mang
`report_build_id` từ T-RP-01 là mỏ neo để replay trả lại kết quả cũ.

Mối lo chính đáng của (a) — `aborted` nhập nhằng giữa "kỳ rỗng hợp lệ" và "build hỏng" — được
giải bằng `abort_reason`, chứ không cần bỏ hàng `report`. Cả (a) và (b) đều thỏa REQ-D57 và
AMD-B04 như nhau, vì `report.schema.json` khóa `status` là `const "published"` nên một hàng
`aborted` **không có** read model hiển thị. Khác biệt là chẩn đoán và idempotency, không phải
hành vi người dùng thấy.

**Cách đảo quyết định nếu Coordinator/Owner vẫn muốn (a):** điều kiện tiên quyết là thêm
`report_build_id` (hoặc idempotency key tương đương) vào `coverage_window` — một CR về phía PC02
cộng một sửa `publish_cas` về phía PC03. Không có bước đó, (a) đánh đổi một lỗi idempotency thật
lấy một lợi ích diễn đạt. Lập luận đầy đủ, bảng `abort_reason` và oracle (gồm **oracle âm** về
replay) nằm ở `contracts/reporting/time-and-tags.md` §4.7.1; fixture
`d-empty-period-coverage-only.json` mang `decision_note` tương ứng.

Phát sinh: **CR-PC04-08** (PC03) và **CR-PC04-09** (PC02).

### 7.4 Câu hỏi còn mở PC04 không tự giải

- **REQ-OQ04** (N ngày backfill): dùng 7 theo baseline §5, Owner chưa trả lời.
- **REQ-OQ08 / REQ-A2** (ngưỡng): chưa hiệu chỉnh; cần 50–100 bài gán nhãn tay, tập dò ngưỡng
  tách tập đánh giá, rubric khóa trước khi dò.
- **REQ-A4** (mật độ): cần 3–4 kỳ thật; hiện `KC`.
- **B08 timezone**: `Asia/Ho_Chi_Minh` vẫn cần Owner xác nhận.
- **REQ-D53** vẫn là mục P0 **còn `ĐX`** — PC04 **không** promote nó.

## 8. Những gì gói này KHÔNG chứng minh

- Không chứng minh code chạy đúng: chưa có code. Trạng thái dự án vẫn `NOT_READY_FOR_PRODUCT_CODE`.
- Không chứng minh ngưỡng hay thuật toán mật độ hữu ích (REQ-A2, REQ-A4 đều `KC`).
- Không chứng minh coverage phản ánh đủ những gì có trên X (B05; đó là lý do
  `coverage_note.observed_data_only` tồn tại).
- Không có **independent audit**: mọi bằng chứng ở §4 là `SELF_VALIDATION` do chính người viết
  candidate chạy. `audit_route` của packet là `INDEPENDENT_REQUIRED` và chưa được thực hiện.
- B01, B04, B08, B14, B17 vẫn **OPEN** trong `agent_profile/registry.json`.

## 9. Next actor

`Coordinator`. Việc tiếp theo đề nghị: (1) rehash độc lập 17 file ở §2; (2) quyết định về drift
ở §6 trước khi freeze; (3) **xác nhận hoặc bác quyết định CR-PC03-06 ở §7.5** — PC04 chọn (b)
trái khuyến nghị (a) của Coordinator, có lý do idempotency cụ thể và có đường đảo; (4) định
tuyến Auditor độc lập; (5) chuyển 9 CR ở §7.1 tới PC01/PC02/PC03/PC06/PC07/PC09; (6) đưa 8
quyết định `PROVISIONAL` ở §7.3 vào OWNER_DECISION_REQUEST của PC09.

`lease_released_at`: 2026-09-06T18:08Z. Sau file này `worker-W5` **không ghi thêm bất kỳ file
nào**, kể cả sửa lỗi đánh máy; sửa tiếp cần packet mới, baseline mới và lease mới.


---

# ADDENDUM — PKT-PC04-FIX1 (remediation của AUDIT_REPORT PKT-A1-R2)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04-FIX1` |
| worker principal | `worker-W5` |
| authority_id | `AUTH-COORD-PC04-FIX1` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC04-e2` (exclusive, **fencing 2**), `expires_at` 2026-09-07T06:00Z |
| status | **`DONE_WITH_CONCERNS`** · completion_claim `DRAFT_FOR_REVIEW` |
| findings xử lý | `F-A1R2-01` (MAJOR), `F-A1R2-02` (MAJOR), `F-A1R2-03` (MAJOR) |
| không thuộc phạm vi | `F-A1R2-04` (PC03), `F-A1R2-05`/`F-A1R2-06` (PC00/PC01), `CR-PC06-04`/`CR-PC07-06` (PC09) |
| lease_released_at | 2026-09-06T20:35Z |

## A1. Delta theo file

| Path | Op | Before (sha256, rút gọn) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/reporting/time-and-tags.md` | **MODIFY** | `652854d8bc681c62…` | `779333071c6b10c2971266a254299b835616cc49e053981f870e1930d8c3ad52` | 59360 |
| `contracts/reporting/selection.md` | **MODIFY** | `fca9a9a55edf1b0e…` | `6bc8ab07a886be08de2f19d070e6cb74f26d78d138bd9fc36d350d81fbaff343` | 33048 |
| `contracts/schemas/report.schema.json` | **MODIFY** | `a8662d5d27b03724…` | `a7c7255a5bae703b0bdcd1ba761153dbce686b5766b05dfbaa1606392338d07b` | 31129 |
| `acceptance/fixtures/reporting/README.md` | **MODIFY** | `a536e16f014064e3…` | `bf2395e68b930d7ff7a8978f0ec4e837e23b6a199a8c54fcfb19899aa41d5a47` | 13268 |
| `acceptance/fixtures/reporting/a-tag-removed-before-publish.json` | **MODIFY** | `e299df1809b78940…` | `14722ddc96ec124d44d48330b569b66404128f71144d429a879e2e890524af5d` | 15287 |
| `acceptance/fixtures/reporting/b-tag-removed-then-readded-reuse-analysis.json` | **MODIFY** | `fd05b877ed22011f…` | `ae933def10b59a79447200c97f6eeec115a2eb19d20cc7cbca216980d2ffd4d9` | 15706 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | **MODIFY** | `72d056e751815926…` | `21d48a90998c32a4e339b7634efae1e32f50562c69ac4c832dbf2615d2645eff` | 5189 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | **MODIFY** | `d5b482071daec6c1…` | `2a170a4b688793c6d249427c116eea2a17187918cb830077210bb353474f2269` | 8044 |
| `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` | **MODIFY** | `2d084ee293a7e45f…` | `4a18b08dfcc576a5767a665157de1a18150874605d0e7107c07e5e32029a7b66` | 10155 |
| `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json` | **MODIFY** | `349ec81129cf00cb…` | `15e53f60f741a88e9f0eb7e707d5fabd73acd7eee19cc2f2c472ce90372f6a71` | 12840 |
| `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json` | **MODIFY** | `d0f5c946da6de5e6…` | `a9df835a3d2a77b5f26b412d9b7b900da64569d98f517bf1a0306780adabb90f` | 4961 |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | **MODIFY** | `9b17869b772144eb…` | `70f347bc693195beca34c69b182085c10c70bea8481a0d39f1afb71e7d551d06` | 8955 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | **MODIFY** | `9d260f0a198be9c0…` | `d199fd02598d106a5749ddbd2db6e3f8e87065e5e6f4ab068d2e81c4573c784f` | 14508 |
| `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json` | **MODIFY** | `654014d57823a4e1…` | `8421739a69401b793cc44ca1812f352c74c844187f84b3cf105e9ec4408eede4` | 6008 |
| `acceptance/fixtures/reporting/k-builder-crash-backfill-not-consumed.json` | **MODIFY** | `61d41043a347c754…` | `f3126544eff18fdcfd913d6952dc486cdd871275c04ba2a35cdde2613bae47ab` | 5045 |
| `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json` | **MODIFY** | `f53ec831634b17c3…` | `ab1ef46fdbbe39e4ec19e8c38caf06007776fd726e2c182563a8b08a3aaa365e` | 5744 |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | **MODIFY** | `5f1183e7d256665e…` | `39ef6a819b4f09b041d6d2b3e4b9338023a46c20b7e11da0871546f7e5c8e231` | 28343 |

17/17 file thay đổi. Không file nào ngoài MODIFY grant bị ghi; không tạo file mới.

## A2. F-A1R2-01 — `report_build_id` nay là một cột thật

Audit đúng: khi PC04 viết lần đầu, `report_build_id` xuất hiện 11× trong `time-and-tags.md`
nhưng **0×** trong `entities.yaml`, và PC04 **không** mở CR cho nó — trong khi lập luận §4.7.1
(chọn phương án (b) cho kỳ rỗng, trái khuyến nghị Coordinator) dựa hẳn vào cột đó. Tiền đề trống,
kết luận chưa được chứng minh bằng bytes đã đóng băng.

Sau PC02-FIX3, `report.report_build_id` tồn tại (UUIDv4, NOT NULL,
`ux_report_owner_build_id = UNIQUE(owner_id, report_build_id)`). Đã sửa:

- `time-and-tags.md` §4.7.1: thêm khối **"Trạng thái tiền đề (sửa theo F-A1R2-01)"** ghi rõ lịch
  sử — lập luận từng dựa trên một cột không tồn tại, nay dựa trên cột đã khai — và trích
  `ux_report_owner_build_id`.
- `report.schema.json`: thêm `report_build_id` (string, `format: uuid`, pattern UUIDv4,
  **required**) ngay sau `report_id`; thêm `x-contract.not_in_read_model` giải thích vì sao
  `abort_reason` **không** có trong read model (status là `const "published"`, mà `abort_reason`
  NOT NULL **iff** `status='aborted'`, nên nó sẽ luôn null ở đây) trong khi `report_build_id`
  thì **có** (tồn tại trên mọi hàng report bất kể status).
- 8 object `expected.report` của fixture được cấp `report_build_id` UUIDv4 tất định.
- Mở **`CR-PC04-10`** (đã đáp) để ghi lại rằng CR này lẽ ra phải được PC04 mở từ đầu — chuỗi
  truy vết không còn lỗ hổng.

*Lưu ý cho Coordinator:* nếu Owner vẫn muốn phương án (a) cho kỳ rỗng, PC02-FIX3 đặt
`report_build_id` trên `report` chứ **không** trên `coverage_window`, nên dưới (a) một kỳ rỗng
vẫn không có receipt nào. §4.7.1 đã nói rõ điều đó.

## A3. F-A1R2-02 — 10 sự kiện fixture dùng caller không hợp lệ

Kiểm `EV-PC04-05` tái lập đúng 10 vi phạm audit nêu. Đã sửa toàn bộ theo mẫu
`actor` = caller hợp lệ, `performed_by` = service thực thi:

| Fixture#seq | operation | actor trước → sau | performed_by |
| --- | --- | --- | --- |
| `a`#1, `f`#3 | `ingest.submit_batch` | `MOD-ingest-service` → **`MOD-x-collector`** | `MOD-ingest-service` |
| `a`#2, `e`#3 | `analysis.submit_result` | `MOD-analysis-service` → **`MOD-analysis-worker`** | `MOD-analysis-service` |
| `b`#3 | `analysis.enqueue_tasks` | `MOD-analysis-service` → **`MOD-report-service`** | `MOD-analysis-service` |
| `c`#2 | `delivery.create_intent` | `MOD-delivery-service` → **`MOD-report-service`** | `MOD-delivery-service` |
| `c`#3, `c`#5 | `telegram.send_payload` | `MOD-telegram-adapter` → **`MOD-delivery-service`** | `MOD-telegram-adapter` |
| `f`#2 | `job.coalesce_overdue` | `MOD-job-service` → **`MOD-scheduler`** | `MOD-job-service` |
| `i`#1 | `identity.record_alias` | `MOD-research-connector` → **`MOD-ingest-service`** | `MOD-identity-service` |

`performed_by` được dùng ở **10/51** sự kiện (trước: 0) và được **định nghĩa** ở
`acceptance/fixtures/reporting/README.md` §3.1 — nguyên văn khớp README của PC06 và PC07: nó là
service thực thi, **không** phải một khẳng định về quyền gọi.

Audit nhấn mạnh điều quan trọng hơn 10 lần sửa: quy tắc phải ràng buộc file MỚI, không chỉ sửa
file cũ. PC06 (viết sau ruling) đã chạy chính kiểm tra này trước handoff và tự bắt được 3 vi phạm
của mình — cơ chế đã hoạt động ở gói kế tiếp.

## A4. F-A1R2-03 — tên cột trong `expected.rows`

`EV-PC04-06` (mới) kiểm **từng cột** của **mọi** `rows`, và sau khi mở rộng sang `given.rows`
đã bắt thêm các lỗi audit chưa liệt kê:

| Lỗi | Số chỗ | Sửa |
| --- | --- | --- |
| `rows.coverage_window` dùng tên **read model** (`coverage_window_id`, `coverage_from`, `coverage_to`) thay vì tên cột (`id`, `window_from`, `window_to`) | 16 hàng / 11 file | Đổi sang tên cột |
| `work.discovered_at` (cột thật là `first_discovered_at`) | 11 | Đổi tên |
| `delivery.attempt` (cột thật là `attempt_count`) | 1 | Đổi tên |
| `embedding_generation.embedding_generation_id` (PK là `id`) | 2 | Đổi tên |
| `work.target`, `work_label.vector_present` — **không phải cột**, là chú thích của fixture | 20 | Đổi thành `_target` / `_vector_present`; checker bỏ qua khóa `_…` **theo quy tắc**, không theo danh sách |

Giá trị enum cũng được căn theo PC02-FIX3: `backfill_ledger.entitlement` nay là
`granted｜consumed｜denied_already_consumed` (trước PC04 tự đặt `granted｜none`),
`entitlement_reason` là văn bản tự do, và ràng buộc được gọi đúng tên
`ux_backfill_subscription_consumed`. `time-and-tags.md` §6.2 đổi định nghĩa
`subscription_identity_hash` sang dạng đã ruled — **sha256 hex của
`owner_id + "\n" + văn bản tag đã chuẩn hóa`** — thay cho `sha256(JCS(...))` PC04 đề nghị ban đầu.

**`pending_cr` markers: 0.** Mọi cột được trích dẫn đã tồn tại; xác minh theo
`contracts/data/entities.yaml` sha256
`209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece`, ghi lại trong
`d-empty-period-coverage-only.json` → `field_names_verified_against`.

## A5. Evidence — sáu kiểm tra, tất cả exit 0

| ID | Kiểm | Kết quả |
| --- | --- | --- |
| `EV-PC04-01` | metaschema + 13 fixture parse + 8 `expected.report` validate | exit 0 · **PASS** |
| `EV-PC04-02` | tính lại ví dụ mật độ, đối chiếu fixture và `selection.md` §8.7 | exit 0 · **PASS** |
| `EV-PC04-03` | operation / module / entity được trích dẫn tồn tại | exit 0 · **PASS** |
| `EV-PC04-04` | 24 coverage window nửa mở và nối liền | exit 0 · **PASS** |
| `EV-PC04-05` **(mới)** | fixture-actor-edge — **51/51** sự kiện | exit 0 · **PASS** (trước fix: 10 FAIL) |
| `EV-PC04-06` **(mới)** | field-level existence, `given.rows` + `expected.rows` | exit 0 · **PASS** (trước fix: 42 FAIL) |

Tất cả `SELF_VALIDATION`, cấp E0. E1–E4 vẫn `NOT_RUN`. Chưa có independent audit cho epoch này.

## A6. Concerns

1. **`entities.yaml` đổi hai lần trong lúc gói fix chạy** (`d6c583c1…` → `209cf03e…`) vì PC02-FIX3
   vẫn đang ghi. Đã kiểm lại toàn bộ 7 cột phụ thuộc ở hash cuối và chạy lại cả sáu kiểm tra.
   Coordinator nên re-verify `EV-PC04-03/05/06` khi PC02-FIX3 đóng.
2. **Quy ước `_`-prefix là mới.** Nó giải quyết một vấn đề thật (fixture cần mang object target
   và cờ "vector tồn tại" mà không có cột tương ứng) nhưng chưa được ruling. Nếu Coordinator muốn
   một cơ chế khác, đây là chỗ đổi — đề nghị đưa vào ruling để PC05/PC07/PC09 dùng chung.
3. **Kiểm tra `given.rows`.** Packet chỉ yêu cầu `expected.rows`; tôi mở rộng sang `given.rows` và
   nó bắt thêm 33 lỗi thật. Đề nghị quy tắc chung của PC09 cũng kiểm `given`.
4. Quyết định kỳ rỗng vẫn là **phương án (b)**, nay có tiền đề thật. Nó vẫn trái khuyến nghị ban
   đầu của Coordinator và vẫn cần xác nhận hoặc bác — xem §7.5 của handoff gốc.


---

# ADDENDUM — PKT-PC04-FIX2 (R4-01, remediation của F-A1R3-01)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04-FIX2` · authority `AUTH-COORD-PC04-FIX2` · lease `LEASE-PC04-e3` (**fencing 3**) |
| status | **`DONE`** · completion_claim `DRAFT_FOR_REVIEW` · lease_released_at 2026-09-06T21:10Z |
| finding | `F-A1R3-01` (MAJOR), phần thuộc `reporting/` |
| ngoài phạm vi | `identity/` (PC02) và `telegram/` (PC07) — chỉ báo cáo số, không sửa |

## B1. Delta

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `acceptance/fixtures/reporting/README.md` | MODIFY | `a0d0be015f19f67ec01b0ce28bcdf942279305c9d42f016033a7ae85bcfe3845` | 13756 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | MODIFY | `e619c514f35956db8d4454df4779eb5df56f4fab814acb4c9d3c55fdc790f7e3` | 8045 |
| `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json` | MODIFY | `6584abee3fdb83ff04be11f9e4992e8650e60095a7fc7d058d5c5177e4dfdfa9` | 12841 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | MODIFY | `ee4f9f18a4692c0a6c9a647bbb3736ea8812f8582b29767f9dec7b280add032a` | 14510 |
| `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json` | MODIFY | `c1035509a76e42802859138297ee9ac0d575538e3d1a3ce95ad1336c072543f2` | 5746 |

## B2. Sáu khóa đã đổi

Đúng 6 khóa chú thích trần trong 4 file mà audit nêu, đổi sang dạng `_`:
`report.note_vi` → `report._note_vi`; `work.note` → `work._note`;
`work_label.note` → `work_label._note`; `first_announced_ledger.note` →
`first_announced_ledger._note`.

Việc đổi tên do script thực hiện **theo quy tắc R4-01**, không theo danh sách: mọi khóa không
phải cột, không bắt đầu bằng `_`, và không có marker `pending_cr` đều được thêm tiền tố. Nhờ vậy
kết quả không phụ thuộc vào việc tôi có liệt kê đủ 6 tên hay không.

`README.md` §3.2 nay **chép nguyên văn** đoạn R4-01 (kể cả câu "No per-package allowlist") thay
cho cách diễn đạt riêng mà PC04-FIX1 đã dùng, và §1 liệt kê đủ **13/13** file của thư mục.

## B3. Gate `EV-PC04-06` chạy trên **cả sáu** thư mục

Checker được viết lại để thực thi R4-01 **đúng nguyên văn**: khóa hợp lệ ⟺ là cột của entity đó,
hoặc bắt đầu bằng `_`, hoặc hàng mang `pending_cr`. Danh sách bỏ qua theo tên
(`note`/`note_vi`/`pending_cr`) mà PC04-FIX1 còn dùng **đã bị xóa** — chính nó là "silent
per-package allowlist" mà F-A1R3-01 tuyên bố không chấp nhận được.

| directory | files | columns | unresolved |
| --- | --- | --- | --- |
| `ai` | 11 | 40 | **0** |
| `collection` | 8 | 0 | **0** |
| `identity` | 14 | 424 | **0** |
| `recovery` | 10 | 0 | **0** |
| `reporting` | 13 | 416 | **0** |
| `telegram` | 18 | 281 | **0** |
| **TOTAL** | **74** | **1161** | **0** |

Exit code `0`. Baseline: `contracts/data/entities.yaml` sha256
`209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece`.

**Lần chạy đầu của gói này** (trước khi tôi sửa) cho: identity 52, reporting 6, telegram 29 —
tổng **87**, khớp con số 89 của audit trong sai số 2 ở `telegram/` (khác biệt nằm ở cách đếm lần
xuất hiện lồng nhau, không ở tập file). Sau khi tôi sửa 6 khóa của `reporting/`, hai thư mục kia
cũng về 0 vì PC02 và PC07 áp bản sửa của họ **đồng thời** trong cùng cửa sổ thời gian. Tôi
**không** sửa file của họ; số 0 của `identity/` và `telegram/` là kết quả quan sát được, không
phải công của gói này.

`collection` và `recovery` báo 0 cột vì fixture của chúng không dùng `given/expected.rows` —
đó là 0 "không có gì để kiểm", không phải 0 "đã kiểm và sạch". Ghi rõ để không ai đọc nhầm.

## B4. Bốn gate còn lại vẫn xanh

`EV-PC04-01` (schema + 13 fixture + 8 `expected.report`), `EV-PC04-02` (ví dụ mật độ),
`EV-PC04-03` (tham chiếu), `EV-PC04-04` (24 coverage window), `EV-PC04-05` (actor-edge 51/51) —
tất cả exit `0` sau khi đổi tên.

## B5. Concerns

1. `collection`/`recovery` = 0 cột: gate không nói gì về hai thư mục đó. Nếu PC09 muốn con số có
   nghĩa, `e0_check.py` nên phân biệt "0 vì sạch" với "0 vì không có `rows`".
2. Số của tôi (87) lệch 2 so với audit (89) ở `telegram/`. Không ảnh hưởng kết luận (cả hai nay
   là 0) nhưng PC09 nên chốt một cách đếm duy nhất để các handoff so được với nhau.


---

# ADDENDUM — PKT-PC04-FIX3 (R5-02 / CR-PC09-01: fixture cho SC52)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04-FIX3` · authority `AUTH-COORD-PC04-FIX3` · lease `LEASE-PC04-e4` (**fencing 4**) |
| status | **`DONE_WITH_CONCERNS`** · completion_claim `DRAFT_FOR_REVIEW` · lease_released_at 2026-09-07T00:45Z |
| ruling | `R5-02` — SC52 (mặt dương của I12) giao cho W5 → `acceptance/fixtures/reporting/` |
| clock tại lúc bắt đầu | `2026-09-07T00:16:24Z`; lease hết hạn `2026-09-07T12:00Z` — còn hạn |
| nguồn | SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…` — **khớp**; `entities.yaml` `209cf03e…` |

Ghi chú tiếp nối: lượt trước của gói này bị API rate limit cắt **trước mọi thao tác ghi**; đã tự
kiểm lại (`grep -c PKT-PC04-FIX3` = 0, thư mục có 14 mục) trước khi bắt đầu lại, nên không có
trạng thái ghi dở nào phải dọn.

## D1. Delta

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json` | **CREATE** | `dee4f914874d106757e5040004c78d18fbbe574d3a78e519f8c7987877dd4bf6` | 18222 |
| `acceptance/fixtures/reporting/README.md` | MODIFY | `ff57f2f0575d70aa3f6d175b35a0e26a81d0f1773641159fefe91678586d00cb` | 14068 |
| `contracts/reporting/selection.md` | MODIFY | `d704738f540c4f1adca8836c2021ccce11e1934bc1ae450b63bfd2619fcbafff` | 34531 |

## D2. Fixture `FX-RP-N` — mặt dương của I12

Trước gói này, I12 chỉ có **mặt âm**: fixture `l` chứng minh việc trộn generation **bị chặn**.
Một mình nó không loại trừ được một triển khai chặn mọi thứ và **không bao giờ đổi được model** —
mà REQ-D48 lại yêu cầu đổi model phải tính lại toàn kho. `FX-RP-N` khóa đường đi đúng, 11 sự kiện:

1. `settings.update_config` (Owner đổi model) → 2. `embedding.start_generation_rebuild` tạo G2
`state='building'`, G1 vẫn `active` → 3–4. `embedding.generate_vectors` (model **local** ở server)
→ 5–6. một kỳ báo cáo dựng **giữa lúc rebuild** vẫn publish với `embedding_generation_id = G1`
→ 7. `embedding.activate_generation` **bị từ chối** vì `built_vector_count` (2) <
`expected_vector_count` (4) → 8. dựng nốt vector → 9. chuyển `active` trong **một** transaction,
G1 → `retired` → 10–11. kỳ sau chỉ dùng G2.

Oracle chính (nguyên văn SC52): **số phép cosine giữa hai generation khác nhau = 0** trong toàn bộ
chuỗi, đo bằng một bộ đếm bọc quanh hàm similarity (`given.instrumentation_vi`). Kèm theo: đúng
một hàng `state='active'` tại mọi thời điểm quan sát được (`ux_embedding_generation_active`);
G1 và toàn bộ vector của nó **được giữ**, không xóa; report cũ mang G1 **không bị sửa** (I05);
coverage nối liền qua lần chuyển (I06); kỳ đầu sau khi chuyển mang
`insufficient_reason = 'generation_reset'` theo `selection.md` §8.5.

Tuân thủ R4-01/R4-02: `rows` có cấu trúc theo entity thật (`embedding_generation`, `tag_vector`,
`work_label`, `report`, `coverage_window`), chú thích mang tiền tố `_`, khóa sự kiện là
`operation`, và mọi `actor` là caller hợp lệ với `performed_by` là service thực thi.

`selection.md` §5 nay có **O-5a (mặt âm, SC24)** và **O-5b (mặt dương, SC52)** cạnh nhau, kèm câu
giải thích vì sao một mình mặt âm là chưa đủ.

## D3. Gate

| Gate | Kết quả |
| --- | --- |
| `EV-PC04-01` schema + fixture | **9** `expected.report` validate (trước: 8) · exit 0 |
| `EV-PC04-02` ví dụ mật độ | exit 0 |
| `EV-PC04-03` tham chiếu | exit 0 |
| `EV-PC04-04` coverage nửa mở/nối liền | exit 0 |
| `EV-PC04-05` actor-edge | **62/62** sự kiện (trước: 51) · exit 0 |
| `EV-PC04-06` field gate R4-01 | xem bảng dưới |

| directory | files | columns | unresolved |
| --- | --- | --- | --- |
| `ai` | 11 | 40 | 0 |
| `collection` | 8 | 0 | 0 |
| `identity` | 14 | 424 | 0 |
| `recovery` | 10 | 0 | 0 |
| `reporting` | **14** | **504** | **0** |
| `telegram` | 18 | 281 | 0 |
| `ui` | 2 | 130 | **2** |
| **TOTAL** | **77** | **1379** | **2** |

README của `reporting/` liệt kê **14/14** file.

## D4. Concerns

1. **Hai khóa chưa giải quyết nằm ở `ui/sc51-first-time-setup.json`** (`provider_config.terms_check_at`
   ×2) — thư mục của W3, viết song song, **ngoài** write grant của tôi. Tôi báo số chứ không sửa.
   Cột `terms_check_at` không có trong `ENT-provider-config`; hoặc PC02 thêm cột, hoặc W3 đổi sang
   `_terms_check_at`, hoặc gắn `pending_cr`. Chuyển Coordinator.
2. **`acceptance/scenarios.yaml` SC52 dùng hai tên operation không tồn tại** —
   `embedding.start_generation` và `embedding.switch_generation`. Tên có thẩm quyền trong
   `contracts/ports.yaml` là `embedding.start_generation_rebuild` và
   `embedding.activate_generation`. Fixture dùng tên đúng và ghi lại sai lệch ở
   `operation_name_note_vi`. → **CR-PC04-11** gửi PC09: sửa `event_order` của SC52, và cân nhắc
   một check tĩnh xác thực mọi tên operation xuất hiện trong `scenarios.yaml`.
3. `collection` và `recovery` vẫn báo 0 cột vì fixture của chúng không dùng `given/expected.rows`
   — "không có gì để kiểm", không phải "đã kiểm và sạch". Lặp lại từ addendum FIX2.
4. SC52 khai `evidence_level_required: E2`; fixture này là **E0** (dữ liệu + oracle tĩnh). Bộ đếm
   phép cosine phải tồn tại thật ở tầng triển khai thì oracle chính mới đo được — hiện `NOT_RUN`.


---

# ADDENDUM — PKT-PC04-FIX4 (FIX7: token prose sweep)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04-FIX4` · authority `AUTH-COORD-PC04-FIX4` · lease `LEASE-PC04-e5` (**fencing 5**) |
| status | **`DONE_WITH_CONCERNS`** · claim `DRAFT_FOR_REVIEW` · lease_released_at 2026-09-07T02:05Z |
| clock bắt đầu | `2026-09-07T01:34:03Z`; hết hạn `2026-09-07T18:00Z` — còn hạn |
| nguồn | SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…` — **khớp** đầu và cuối |
| entities.yaml | `bdce5fc122d69cd35b8635cfdfab0066b01ff1aa90b4834896c68bf806fc7891` (đã đổi so với FIX3) |

## E1. Delta

| Path | After (sha256) | Bytes |
| --- | --- | --- |
| `contracts/reporting/time-and-tags.md` | `7a3a3845707e6160c52601f25baf16190be1ecee3933b94755acb808e6f075e0` | 59747 |
| `contracts/reporting/selection.md` | `cc62af2bd476c51efa9b156bae66be6dae3a0bcd712eb79cd1d4ba3a3d5c2fc0` | 34622 |
| `contracts/ai/tasks.yaml` | `0048bbdd3185fc4b7719014e7d70238c50720766f19e2968cb8e25101bbc05e7` | 31787 |
| `acceptance/fixtures/reporting/README.md` | `2c7974e82c4f7ac6e2554050cc1ffda79bfd926faef2c01ed0d4070b8cc45663` | 14516 |
| `acceptance/fixtures/ai/README.md` | `6b7ede2bc9866eed00ecdd45d52009fe7c3b895ed3c64764694b42c1f577c6a0` | 12646 |
| `…/reporting/n-embedding-generation-switch-positive.json` | `a526022dfba75c7ee06eb6ba58697d4ea849a844ef4b0f49707a651c25e75d34` | 18395 |
| `…/reporting/a-tag-removed-before-publish.json` | `1a88edc26f5e48cd77b12cb0745045e6e421dac29b52635ddcb6db2960a0e7b5` | 15287 |
| `…/reporting/c-tag-changed-after-publish-before-send.json` | `4d5f14c423c1764e9e866df55becd63e6ee6d828e788abc79b17d39db3b6f089` | 5189 |
| `…/reporting/g-concurrent-publishers-cas.json` | `4427374d434a82a0aeeb1841c15200e58628b37dae62f8c63ec2892d0331a0b2` | 4961 |
| `…/reporting/h-already-announced-work-becomes-reference.json` | `0d4d98c87000e19c886fc65748d101f07df79b4e2711f805726c18cc78fbce96` | 8955 |
| `…/reporting/i-identity-merge-single-first-announced.json` | `e2de531e3b5bbad92946b4f6b3ea5f960bbed7afb687df92252391095e24a624` | 14510 |
| `…/reporting/j-backfill-add-remove-readd.json` | `7005bdd937beec466e99bfab5491060c7b59bafedab9cdebf412e1d75d0ed1d1` | 6008 |

**⚠ Card-pinned hashes.** 12 file trên đổi hash. Mọi task card hay manifest đang ghim bản trước
(kể cả `PC10-PIN-FCW4d-20260907` nếu đã pin trước lúc này) là **STALE** và phải re-pin sau khi
W2/W3/W5 land, đúng như FIX7 §"Card pins" đã dự liệu.

## E2. Ba sửa được chỉ định

1. **Fixture `n`** — ghi chú trong file được viết lại; hai token đã chết không còn xuất hiện
   (`grep` = 0). Ghi chú nay chỉ nói tên có thẩm quyền và trỏ về addendum FIX3 cho lịch sử.
2. **`selection.md`** — `work.resolution_rule` (không phải cột) → trích quy tắc tra cứu identity ở
   `contracts/data/identity.md` §3 "Tra cứu: `identity_alias` là một hàm", đi theo
   `work.merged_into_work_id` tới hàng `identity_state = 'active'`. `report.selection_version`
   giữ nguyên theo ruling (W3 đang thêm cột).
3. **`time-and-tags.md`** — `run.last_run` → `worker_registration.last_run_at`, kèm một câu giải
   thích D12 nói về **giá trị hiển thị của worker**, không phải một cột của `run`.

## E3. Quét token — 38 phát hiện, 38 xử lý, còn 0

| Nhóm | Tìm thấy | Cách xử lý |
| --- | --- | --- |
| Đường dẫn cấu trúc YAML/JSON bị hiểu nhầm là operation (`conventions.clock_trust`, `publish_cas.idempotency_rule_vi`, `ownership_boundary.interface_contract_vi`, `cas_conflict_retries.precondition_vi`, `moved_counts.first_announced`, `coverage_note.observed_data_only`, `first_announced_ledger.i07_interface`, `work_version.reanalysis_rule`, `expected_violation.json_pointer`, `rows.coverage_window`, `given.target_key_map`, `analysis_key.schema_version`, `comparator.source_ref`) | 15 | Viết lại dạng `A` → `B`; token `<a>.<b>` biến mất, nghĩa không đổi |
| `density.*` (8 tham số) | 8 | **Sửa cho đúng**: thuộc tính trong `report.schema.json` vốn tên trần (`radius`, `min_members`, …); tiền tố `density.` là cách viết tắt của tôi và đã sai |
| `settings` key | 1 | `settings['reporting.backfill_days']`, khớp cách viết đã dùng ở `selection.md` |
| Cột nằm trong JSON `selection_reason` bị viết như cột của bảng (`report_item.matched_tags`, `report_item.backfill_ledger_id`) | 2 | → `report_item.selection_reason.*` — **chính xác hơn** và không còn khớp mẫu hai thành phần |
| Trường dẫn xuất của read model bị viết như cột của sổ (`first_announced_ledger.target_key_at_announcement`) | 1 | Viết lại thành trường của `first_announced_ref` trong `report.schema.json`, nói rõ là DẪN XUẤT |
| Ký hiệu tượng trưng trong fixture (`H_C`, `RP_EARLY`, `TAG_V1`, `GW_A`, `W_H1`, …) | 11 | **Đổi sang chữ thường** (`h_c`, `rp_early`, …) để không bao giờ đọc nhầm là error code; quy ước được ghi vào README của cả hai thư mục |
| Từ vựng giao thức (`OWNER_DECISION_REQUEST`) | 1 | Giữ nguyên — là message type có thật trong `agent_profile/protocol.md` §4, không phải error code. Xem E5.1 |

`TOTAL unresolved tokens: 0` (exit 0).

## E4. Gate

`EV-PC04-01` (9 report validate) · `EV-PC04-02` · `EV-PC04-03` · `EV-PC04-04` ·
`EV-PC04-05` actor-edge 62/62 · `EV-PC06-01` · `EV-PC06-02` · `EV-PC06-03` · `EV-PC06-04` —
**tất cả exit 0**.

`EV-PC04-06` field gate R4-01 trên **chín** thư mục (ba thư mục mới xuất hiện từ FIX3):

| dir | files | cols | unresolved |
| --- | --- | --- | --- |
| `ai` | 11 | 40 | 0 |
| `boundary` | 1 | 0 | 0 |
| `collection` | 12 | 201 | 0 |
| `e2e` | 1 | 309 | 0 |
| `identity` | 14 | 424 | 0 |
| `recovery` | 13 | 180 | 0 |
| `reporting` | 14 | 504 | 0 |
| `telegram` | 18 | 281 | 0 |
| `ui` | 2 | 134 | 0 |
| **TOTAL** | **86** | **2073** | **0** |

`ui/provider_config.terms_check_at` (2 token tôi báo ở FIX3) đã được W3 xử lý.

## E5. Concerns

1. **`OWNER_DECISION_REQUEST` không phải error code** và không nên bị E0-04b/04c coi là vi phạm.
   Đề nghị W6 đưa **message type của `protocol.md`** (`OWNER_DECISION_REQUEST`, `AUDIT_REPORT`,
   `FROZEN_CANDIDATE`, `TASK_PACKET`, `HANDOFF`) vào từ vựng của check, cạnh error code và claim
   label — nếu không, mọi gói trích dẫn giao thức sẽ báo đỏ giả.
2. **Đề nghị bổ sung cho thiết kế E0-04b (W6):** một token `<a>.<b>` trong backtick còn có thể là
   **đường dẫn cấu trúc** vào một file YAML/JSON. Tôi đã né bằng cách viết `A` → `B`, nhưng nếu
   check không phân biệt được thì mọi gói sẽ phải né như vậy, và prose sẽ xấu dần. Cân nhắc: chỉ
   coi là vi phạm khi tiền tố trùng tên một entity hoặc một domain operation đã biết.
3. **`report.selection_version` và `worker_registration.last_run_at` chưa tồn tại** trong
   `entities.yaml` tại hash `bdce5fc1…`. Tôi trích dẫn chúng theo đúng ruling FIX7 (W3 đang thêm).
   Nếu W3 không land trước FC-W4 thì hai token này sẽ là vi phạm E0-04c của **tôi**, không phải
   của W3 — cần W3 xác nhận đã land trước khi freeze.
4. `boundary` và `e2e`/`collection` nay có cột thật để kiểm (khác FIX2 khi chúng rỗng); nhận xét
   "0 vì không có `rows`" ở addendum FIX2 chỉ còn đúng với `boundary`.


---

# ADDENDUM — PKT-PC04-FIX5 (phê chuẩn Owner OD-20260907-01 → CONTRACT_READY)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04-FIX5` · authority `AUTH-COORD-PC04-FIX5` (parent **`AUTH-OWNER-20260907-02`**) · lease `LEASE-PC04-e6` (**fencing 6**) |
| status | **`DONE`** · completion_claim **`CONTRACT_READY`** (nâng từ `DRAFT_FOR_REVIEW`) |
| clock bắt đầu | `2026-09-07T04:15:37Z`; hết hạn `2026-09-08T00:00Z` — còn hạn |
| lease_released_at | 2026-09-07T04:40Z |
| căn cứ | `OD-20260907-01` mục 22 (8 tham số PC04 + kỳ rỗng (b)), mục 20 (OQ defaults, N = 7), mục 4 (timezone), mục 5/8/16/19 (B01/B04/B14/B17); A2-R4 tuyên bố phạm vi "Reporting and time" đủ điều kiện |
| nguồn | SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…` — **khớp** đầu và cuối |

## F1. Delta

| Path | After (sha256) | Bytes |
| --- | --- | --- |
| `contracts/reporting/time-and-tags.md` | `70f4bc57a0fa2733d92136194eb4d563fa5d9145726141ee30493fe3a2b1a66c` | 61837 |
| `contracts/reporting/selection.md` | `781effb61be2865a07fa3be4373196229bb6bd89048abbb943d646ca95401fe4` | 37357 |
| `contracts/schemas/report.schema.json` | `d2e43686032e36c2932253abe69f37b09f6d695b8d09c96db1eaefe05b65b471` | 32004 |
| `acceptance/fixtures/reporting/README.md` | `3eaab904623d9e498515de84146934179670b4924541763789b99b87d40abafa` | 15469 |

**⚠ Card-pinned hashes.** Cả bốn file đổi hash. Mọi task card, manifest hoặc pin
(`PC10-PIN-FCW4d-20260907` nếu đã lập) trỏ bản trước là **STALE** và phải re-pin.

## F2. Header

Bốn file nay mang `status: accepted`, `claim_ceiling: CONTRACT_READY`,
`ratification_ref: OD-20260907-01`, `ratified_by: AUTH-OWNER-20260907-02`, `ratified_at: 2026-09-07`,
cộng hai trường mới `ratification_scope` và **`ratification_limits`**.

`ratification_limits` là trường quan trọng nhất của gói này. Nó nói rõ điều mà một người đọc
nhãn `CONTRACT_READY` rất dễ hiểu sai:

> Owner phê chuẩn **giá trị làm việc**, không phải kết quả hiệu chỉnh. `CONTRACT_READY` nghĩa là
> **ngữ nghĩa và oracle đã đóng**, không nghĩa là các con số đã được chứng minh là tốt.

## F3. Nhãn PROVISIONAL → ACCEPTED: 17 chỗ, và 6 chỗ **cố ý giữ nguyên**

Đã đổi **13** nhãn trong `time-and-tags.md` và **4** trong `selection.md` sang
`ACCEPTED (OD-20260907-01)`: mốc freeze tag (B01), sổ coverage (B04), kỳ rỗng phương án (b),
N = 7 và trần backfill 30 ngày, quy tắc add→remove→re-add, first-announcement sớm nhất sau merge,
đọc hiểu phiên bản paper mới, `max_items_per_period` = 50, `max_emerging_directions` = 3, ngưỡng
exclusion dùng lại ngưỡng phạm vi, quy tắc kẹp đồng hồ, và timezone `Asia/Ho_Chi_Minh` (Owner
**đã xác nhận**, mục 4 — trước đây file ghi "Owner phải xác nhận").

**Sáu chỗ giữ nguyên `PROVISIONAL`, có chủ ý:**

| Chỗ | Vì sao KHÔNG đổi |
| --- | --- |
| `settings['reporting.default_similarity_threshold']` = `0.8000` | `PROVISIONAL_BOOTSTRAP` + `threshold_calibration_state: uncalibrated` cho tới khi REQ-A2 chạy — packet yêu cầu tường minh |
| Toàn bộ tham số mật độ §8.2 | Cổng REQ-A4 còn nguyên; chưa có 3–4 kỳ thật nào được đọc lại |
| `report_build_rebuild_attempts`, `report_build_stale_after`, `cas_conflict_retries` | **PC03 sở hữu**. PC04 chỉ trích dẫn; đổi trạng thái số của gói khác trong file của mình là vượt quyền. Nay ghi rõ "PC03 sở hữu" |
| Câu trích REQ-OQ08 ("không đặt một con số PROVISIONAL như thể đã biết") | Là trích dẫn yêu cầu, không phải nhãn trạng thái |

Banner đầu `selection.md` được viết lại thành một cảnh báo tường minh: Owner chấp nhận giá trị
làm việc **và** ngưỡng vẫn `uncalibrated` — "cả hai điều cùng đúng, và trình bày thiếu một trong
hai là sai". Đây là chỗ dễ bị đọc thành "Owner đã duyệt nên ngưỡng ổn rồi" nhất.

## F4. Gate — tất cả exit 0

`EV-PC04-01` (9 `expected.report` validate) · `EV-PC04-02` (ví dụ mật độ) · `EV-PC04-03` (tham
chiếu) · `EV-PC04-04` (24 coverage window) · `EV-PC04-05` (actor-edge 62/62) ·
`EV-PC04-06` (field gate R4-01: **86 file / 2073 cột / 0 chưa giải quyết** trên 9 thư mục) ·
token sweep E0-04b/04c (**0 token**).

## F5. PC06 KHÔNG bị đụng

Xác minh bằng hash: `contracts/ai/tasks.yaml` `0048bbdd…`, `providers.yaml` `462e5321…`,
`grounding.md` `b54cec8b…`, `analysis-result.schema.json` `f26720ee…`,
`acceptance/fixtures/ai/README.md` `6b7ede2b…` — **không đổi** so với addendum FIX4.
`analysis-result.schema.json` → `x-contract` vẫn `status: draft`,
`claim_ceiling: DRAFT_FOR_REVIEW`. Phạm vi AI ở lại `DRAFT_FOR_REVIEW` đúng như packet yêu cầu:
REQ-A5 vẫn `KC`, REQ-AC16 vẫn `BLOCKED` cho tới khi một probe CLI/ACP chạy được.

## F6. Concerns

1. **Đọc nhãn `CONTRACT_READY` cho đúng.** Bốn file này đạt ceiling vì ngữ nghĩa, oracle và
   fixture đã đóng — **không** vì các tham số đã được đo. Ngưỡng similarity và tham số mật độ
   vẫn chưa có một điểm dữ liệu thật nào. Nếu một báo cáo hạ nguồn trích `CONTRACT_READY` để suy
   ra chất lượng chọn nội dung, đó là suy diễn sai nhãn (SRC-PLAN §2 "Không nâng cấp nhãn bằng
   suy diễn").
2. **REQ-A2 / REQ-A4 / REQ-A3 vẫn `KC`.** Chừng nào `threshold_calibration_state` còn
   `uncalibrated`, mọi report mang cờ đó và **cấm** tuyên bố chỉ tiêu SRC-SPEC §1.4.
3. **Ba ngân sách PC03 vẫn `PROVISIONAL`** trong file của tôi. Nếu Coordinator muốn toàn bộ
   phạm vi "Reporting and time" nhất quán nhãn, PC03 phải tự đổi trong `retry-policy.yaml` —
   tôi không đổi hộ.
4. `PROV-PC04-01..09`: tôi ánh xạ 9 mục = 8 tham số §7.3 + phương án kỳ rỗng §7.5 của handoff
   gốc. Nếu Coordinator đánh số khác, xin đối chiếu lại trước khi freeze.


---

# ADDENDUM — PKT-PC04-FIX6 (F-A2R5-04 / F-A2R5-05)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC04-FIX6` · authority `AUTH-COORD-PC04-FIX6` (parent `AUTH-OWNER-20260907-02`) · lease `LEASE-PC04-e7` (**fencing 7**) |
| status | **`DONE`** · completion_claim `CONTRACT_READY` |
| clock bắt đầu | `2026-09-07T05:05:30Z`; hết hạn `2026-09-08T04:00Z` — còn hạn |
| lease_released_at | 2026-09-07T05:35Z |
| nguồn | SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…` — **khớp** |

## G1. Delta — 16 file

| `acceptance/fixtures/reporting/README.md` | `cdb2008913f53562ec41fe7ed179c3c17d3a568ee9d5dc8027e16405dcf2b54f` | 16228 |
| `contracts/schemas/report.schema.json` | `8bf6bc9ccd6040c06f4ba709ea638e647ab8349e1bac4f26cd6049df76b7ba60` | 32747 |
| `acceptance/fixtures/reporting/a-tag-removed-before-publish.json` | `cd543ec22a34fbf18b923b1e4fb4d733e54075a6586f810175bf28767f691d44` | 16121 |
| `acceptance/fixtures/reporting/b-tag-removed-then-readded-reuse-analysis.json` | `57d26a0a8381b1b76c0c3109358e132a40bd3a2b5873c515bb5c5dcc828bc1c3` | 16540 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | `3b0d6f24a06ac907ce6c65b139d6124f09dd9ff89389e64d58256a844004a3fa` | 6023 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | `2b3a6cd3ed2a3a5441a6854038020db17e6dbe736c941df6f1d7d5b1adb2c25e` | 8879 |
| `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` | `ed7395620db5bd1b569bd087590b02e9b7cd5dbd06add2822d64ddd24f5a83b4` | 10989 |
| `acceptance/fixtures/reporting/f-three-offline-periods-one-catchup.json` | `e9f9d893a954f92c1918ea2fbb79f7ac0d65a31a60bbf009f7786be25612a1f1` | 13675 |
| `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json` | `825a383b20576864f45a8d9fb9be23bc01d04fe8103f9cf0e8275cff8052980e` | 5795 |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | `99ef5c790806becdf4a3386566d53690ef1d91a77ac416c2f9deacda93085874` | 9789 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | `207e38f9e1c12cca6111f249ebed230bd33993daa69a561210a93e425963d321` | 15344 |
| `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json` | `b074e9f353e4b9646cdf58c88864e1677b86adccdff1b38ab049cbc5e9a4cd4a` | 6842 |
| `acceptance/fixtures/reporting/k-builder-crash-backfill-not-consumed.json` | `9fce157821143ef6d852a688e033424d8f4191dbedfb47caaa80d9ba9a3b6f82` | 5879 |
| `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json` | `e911021ea43f8d9168ea64da6919735a58c41a379a7e926b566128030939a359` | 6580 |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | `719f9c4da1b1bd9138a1cdc60a1d2d501a9abf3945c85e991aa72a828baa3347` | 29177 |
| `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json` | `98bb69cb1fba77b89a65ee500fdfe79e8d19ffef86eb435311c88e2c8786044f` | 19229 |

**⚠ Card-pinned hashes.** Cả 16 file đổi hash. `PC10-PIN-OD01c-20260907` (W7 sắp lập) phải được
lập **sau** gói này, không phải trước.

## G2. (a) F-A2R5-04 — 14 fixture lên `CONTRACT_READY`

Cả 14 file trong `acceptance/fixtures/reporting/` nay mang `claim_ceiling: CONTRACT_READY`,
`ratification_ref: OD-20260907-01`, `ratified_by: AUTH-OWNER-20260907-02`, `ratified_at`,
`ratification_scope`, `ratification_limits`. README có thêm một khối nói rõ ceiling của thư mục.
Nghịch lý mà audit nêu — index claim cao hơn 14 file nó liệt kê — đã hết.

**Chỗ đặt `ratification_ref`: khối khóa cấp cao nhất của file JSON, KHÔNG phải một object
`x-contract` mới.** Lý do cụ thể, và nó vừa được chứng minh bằng dữ liệu:

- `ratification_ref_of()` trong `evidence/tools/e0_check.py` đọc theo thứ tự *top-level dict* →
  `x-contract` → `info.x-contract` → regex. Khóa cấp cao nhất **resolve được**, và ruling
  F-A2R5-03 liệt kê "top-level key" là một trong ba dạng hợp lệ.
- `claim_ceiling` của các fixture này vốn đã nằm ở cấp cao nhất từ PC04 gốc; đặt
  `ratification_ref` cạnh nó giữ **một** nguồn sự thật thay vì hai.
- **Bằng chứng rằng lựa chọn này đúng:** `acceptance/fixtures/identity/` (W3) đã tạo một object
  `x-contract` **chỉ chứa** các trường phê chuẩn. `E0-08-contract-header` lập tức đòi đủ header
  baseline §3 **bên trong** object đó và báo **14 violation** cho 14 file identity. Nếu tôi làm
  y hệt, 14 fixture reporting cũng sẽ đỏ. Với cách đặt ở cấp cao nhất, **0** file reporting nằm
  trong danh sách violation của E0-08.

Nếu Coordinator muốn dạng `x-contract` theo nghĩa đen, việc đó phải đi kèm **đủ** header baseline
§3 trong mỗi fixture — đó là một gói riêng, và nên làm cùng lúc cho cả identity lẫn reporting.

## G3. (b) F-A2R5-05 — `report.schema.json` khai runtime NOT_RUN

`x-contract` nay có `runtime_evidence`: `level_reached: E0`, và bốn khóa
`e1_contract_tests` / `e2_integration_fault_injection` / `e3_live_probe` / `e4_content_review`
đều `NOT_RUN`, kèm `statement_vi` nói thẳng: hợp đồng đã phê chuẩn và đạt `CONTRACT_READY`,
nhưng **chưa có code, chưa có contract test, chưa có fault injection, chưa có live probe, chưa có
review nội dung**. Bốn khóa là dữ liệu máy đọc được, đúng yêu cầu "in a field a checker can read"
của remediation constraint.

Caveat hiệu chỉnh giữ nguyên: `coverage_note` → `threshold_calibration_state` vẫn có thể là
`uncalibrated`, và `$defs.density_parameters` → `parameters_status` vẫn `PROVISIONAL_BOOTSTRAP`.
Ceiling **không** đụng tới hai thứ đó, và `ratification_limits` đã nói vậy từ FIX5.

## G4. Gate

Bộ gate của tôi: `EV-PC04-01` (9 `expected.report` validate) · `-02` · `-03` · `-04` ·
`-05` (actor-edge 62/62) · `-06` (field gate R4-01: 86 file / 2073 cột / 0 chưa giải quyết) ·
token sweep E0-04b/04c (0 token) — **tất cả exit 0**.

`evidence/tools/e0_check.py` (bộ chung của W6) sau thay đổi này:
**22/23 PASS**, `E0-12b-ratification-refs` **PASS** (checked = 50, violations = 0).
Một FAIL duy nhất là `E0-08-contract-header` với **14 violation, toàn bộ thuộc
`acceptance/fixtures/identity/`** — xem G2. **0** violation thuộc phạm vi của tôi.

## G5. Concerns

1. **W3 cần biết ngay:** 14 fixture identity đang FAIL `E0-08` vì object `x-contract` thiếu header
   baseline §3. Hai cách sửa: điền đủ header vào mỗi file, hoặc chuyển các trường phê chuẩn lên
   cấp cao nhất như reporting đã làm. Cách thứ hai rẻ hơn và đã được chứng minh là xanh.
2. **Đề nghị W6:** `E0-08` và `E0-12b` hiện phạt hai cách đặt header khác nhau theo hai hướng
   ngược nhau — tạo `x-contract` một phần thì E0-08 đỏ, không tạo thì vẫn xanh. Nên nói rõ trong
   mô tả check rằng với fixture JSON, khối khóa cấp cao nhất **là** header hợp đồng (ruling R-05),
   để gói sau không phải suy ra điều đó từ việc thử.
3. Ceiling của 14 fixture là `CONTRACT_READY` trong khi `evidence_status` của chúng vẫn `NOT_RUN`.
   Hai điều này cùng đúng và không mâu thuẫn — nhưng đó chính là chỗ dễ đọc nhầm nhất, nên cả
   README lẫn `ratification_limits` của từng file đều nói thẳng.
