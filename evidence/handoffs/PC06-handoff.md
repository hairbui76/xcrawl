# HANDOFF — PKT-PC06 (Khóa AI API/CLI/ACP và grounding)

## 1. Identity

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC06` |
| worker principal | `worker-W5` (tiếp nối worker của PC04; packet mới, lease mới) |
| authority_id | `AUTH-COORD-PC06` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC06-e1` (exclusive, fencing 1), `expires_at` 2026-09-07T08:00Z |
| enforcement_mode | `DOCUMENTARY_DRAFT` — chưa có OS enforcement; lease theo thông điệp |
| status | **`DONE_WITH_CONCERNS`** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| lý do không phải `DONE` | 6/80 mục của FC-W2 đổi trong lúc gói chạy (wave FIX3 của PC00/PC01 đang đáp). Mọi kiểm tra đã chạy lại và PASS trên bản mới, nhưng candidate cần re-verify khi freeze — §6. |
| next actor | `Coordinator` |
| lease_released_at | 2026-09-06T19:40Z |

## 2. Changes — mọi file đều `CREATE`, baseline `ABSENT`

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/ai/tasks.yaml` | CREATE | ABSENT | `9bc3a2529176988f2ffb6e6c561196fba2062b19cca7afa5088bef23921c5b50` | 31775 |
| `contracts/ai/providers.yaml` | CREATE | ABSENT | `462e5321543df781e53d62b54cdffc819765e56f4d2842c871b82fe068dc1bbc` | 19517 |
| `contracts/ai/grounding.md` | CREATE | ABSENT | `b54cec8b3f9f6a9cb2221daaafe8a61a149d0a6686d0d23dcbf7bf9f17995172` | 15293 |
| `contracts/ops/cli-acp-probe.md` | CREATE | ABSENT | `d78f546fdfbeff0388c4d89171179082da6477aea0bdfcd7c85e995fa3f0909b` | 11929 |
| `contracts/schemas/analysis-result.schema.json` | CREATE | ABSENT | `7a5e92db30a5f6766cb5ff472336e424aa09ec76b770acdd1e5527a4869a1bd1` | 17864 |
| `acceptance/fixtures/ai/README.md` | CREATE | ABSENT | `1fb992977b2a5a0e68a27abac814f4df1eca61508ad84426ebf933cda00f665c` | 11525 |
| `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json` | CREATE | ABSENT | `dc1defe222b82dfae97582216d2251fb35663ff177822b388334789a30c9ddea` | 5694 |
| `acceptance/fixtures/ai/b-instruction-injection-in-post.json` | CREATE | ABSENT | `94db889e48aac2a74c3e645d44143075309d33bbef6010593db64340fee6c05b` | 5590 |
| `acceptance/fixtures/ai/c-citation-to-unknown-source.json` | CREATE | ABSENT | `c91286d2106f8de49c0bfb0a158157321bb76de21cb03a29816933f886ba6a65` | 4760 |
| `acceptance/fixtures/ai/d-schema-valid-but-uncited.json` | CREATE | ABSENT | `cf4662a1713d11fd4c60698cc416b0637bd1cfbfb35dce3a86b298e26c52bcbe` | 6158 |
| `acceptance/fixtures/ai/e-transcript-secret-canary.json` | CREATE | ABSENT | `17c41531562ad41c9a869aa201df018e2973a7df319bff6009dfe7239e125ee1` | 5240 |
| `acceptance/fixtures/ai/f-tool-request-in-transcript.json` | CREATE | ABSENT | `dac72388abd272b69e62333aecf1b817923807a5726424d342e0b758a17fdedd` | 4622 |
| `acceptance/fixtures/ai/g-cli-json-embedded-in-prose.json` | CREATE | ABSENT | `d8136a15657e3032a2c1e1b58b4ab04df98c45ff3c6dd63c46d557a79bbf865d` | 4345 |
| `acceptance/fixtures/ai/h-provider-unavailable-no-fallback.json` | CREATE | ABSENT | `202895c3a8d9816878fc67962286e6da0d0a331b6d81cb1a8c541c48c881545e` | 5577 |
| `acceptance/fixtures/ai/i-crash-after-provider-completion.json` | CREATE | ABSENT | `0e7563734963fb71666f023d5d84b3a2d819afc3bb76cd9b1de9c3cc2c0dead0` | 4302 |
| `acceptance/fixtures/ai/j-same-key-resubmitted-one-result.json` | CREATE | ABSENT | `9bc1dc1b6404dd1892ce291dd23136f2291e8a40816c4cafbe8d4814516e76f9` | 4947 |
| `acceptance/fixtures/ai/k-zero-api-key-all-tasks-via-cli.json` | CREATE | ABSENT | `8f46b4c4205f82f72e2093b654b1972344746d6af84369020d4e75f2cef6912f` | 10599 |
| `evidence/handoffs/PC06-handoff.md` | CREATE | ABSENT | (file này) | — |

Thư mục tạo mới: `contracts/ai/`, `acceptance/fixtures/ai/`. **Không** file nào ngoài danh sách
trên bị ghi; không sửa file của gói khác. Không lệnh git mutate, không network.
`PYTHONDONTWRITEBYTECODE=1`; script chạy từ scratch dir `…/scratchpad/w5/`; không có
`__pycache__` hay artifact nào sinh trong repo.

## 3. Baseline

### 3.1 Sources — khớp baseline §2 ở cả hai lần kiểm

| Ref | SHA-256 | Kết quả |
| --- | --- | --- |
| SRC-PLAN | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | **khớp** |
| SRC-SPEC | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | **khớp** |

### 3.2 FC-W2 epoch 2 — xác minh đầu gói

Toàn bộ **80/80** mục của `audits/FC-W2-manifest.txt` được xác minh lại bằng script khi bắt đầu:
`ok=80 drift=0 missing=0`. Đây là lần đầu trong phiên một gói bắt đầu trên baseline sạch hoàn toàn.

### 3.3 Dependency đã dựa vào — giá trị tại handoff

| Path | SHA-256 tại handoff | Ghi chú |
| --- | --- | --- |
| `contracts/data/entities.yaml` | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | khớp FC-W2 |
| `contracts/state/analysis.yaml` | `73be908d0da32fb217dd45b1f296d4e10954ec7b2507c689c9e73693a9761254` | khớp FC-W2 |
| `contracts/retry-policy.yaml` | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` | khớp FC-W2 |
| `contracts/modules.yaml` | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` | khớp FC-W2 |
| `contracts/schemas/target.schema.json` | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` | khớp FC-W2 |
| `contracts/reporting/selection.md` | `fca9a9a55edf1b0e360ca29161d586ac1e35f04ffb020103bad8a992fc78215c` | khớp FC-W2 (PC04, frozen) |
| ADR-0008 | `c08f8670b19e8a0758062988570701ccb96f6d4beefac7b4d80ed6906b95c5f1` | khớp FC-W2 |
| ADR-0010 | `734766c889edbbb0dce94dca92b7da04a9c0b6721536addaeaac3ee6c783a291` | khớp FC-W2 |
| `contracts/ports.yaml` | `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a` | **đổi** trong lúc gói chạy (FIX3) — §6 |
| `contracts/errors.yaml` | `f503cbf17a8503a4c95b6eae94755c0fab5acd3fc9cb5ef6a088c584d1b3b5cf` | **đổi** (FIX1/FIX3) — §6 |
| `contracts/capabilities.yaml` | `ecba935c1fdec4dbf1b7f4539b47fb51bb3a8aa0d148e58b0fc432836f760c4a` | **đổi** (FIX3) — §6 |

## 4. Evidence records

Tất cả `SELF_VALIDATION` do `worker-W5` tạo. Runtime: Python 3.12.3, `jsonschema` 4.10.3
(Draft 2020-12 + `RefResolver`), `PyYAML` 6.0.1, Linux 7.0.0-30-generic. Không network.
Cấp **E0** (SRC-PLAN §14.2). **E1–E4 = `NOT_RUN`**: chưa có code, chưa gọi provider AI nào, chưa
chạy probe nào, chưa có kỳ báo cáo thật để chấm rubric.

### EV-PC06-01 — metaschema + YAML parse + fixture dương/âm

- Command: `python3 <scratch>/w5/ai_validate.py` · ended 2026-09-06T19:35Z
- Input: `analysis-result.schema.json` (`7a5e92db…`), `target.schema.json` (`436cb97b…`),
  `tasks.yaml` (`9bc3a252…`), `providers.yaml` (`462e5321…`), 11 fixture
- Oracle: (a) `check_schema` Draft 2020-12 không ném lỗi; (b) YAML parse được; (c)
  `expected_validation: accept` ⇒ **0** lỗi schema; (d) `reject_schema` ⇒ ≥1 lỗi **và** đường
  dẫn lỗi khớp `expected_violation.json_pointer`; (e) `reject_semantic` ⇒ **0** lỗi schema (chứng
  minh tầng ngữ nghĩa là cần thiết) **và** `check_id` tồn tại trong `tasks.yaml` §4
- Expected: 0 FAIL; ≥ 8 payload dương, ≥ 4 payload âm
- Observed: `PASS metaschema`; 3 task + 2 family parse; **8 payload dương** validate;
  **4 payload âm** — 1 bị schema bắt tại `/result/statements/0/citation_refs`, 3 schema-valid và
  bị `SV-02`/`SV-03` bắt
- Exit code `0` · **PASS**
- Limitations: chứng minh hình dạng wire tự nhất quán và ranh giới schema/ngữ nghĩa có thật.
  KHÔNG chứng minh tầng ngữ nghĩa đã được triển khai — chưa có code.

### EV-PC06-02 — operation / entity / error code / budget / module được trích dẫn đều tồn tại

- Command: `python3 <scratch>/w5/ai_refs.py` · ended 2026-09-06T19:36Z
- Input: 6 file PC06 + `ports.yaml`, `entities.yaml`, `errors.yaml`, `modules.yaml`, `retry-policy.yaml`
- Oracle: mọi token dạng `x.y` khớp một `operation_id`; mọi `MOD-*` tồn tại trong modules.yaml;
  mọi mã SCREAMING_SNAKE khớp một `code` của errors.yaml (trừ allowlist từ vựng giao thức); mọi
  tên budget khớp retry-policy.yaml
- Expected: 0 FAIL, 0 module lạ
- Observed: 12 operation, 9 error code, 19 entity, 5 retry budget, 11 module — **tất cả tồn tại**;
  0 FAIL
- Exit code `0` · **PASS**
- Limitations: kiểm **sự tồn tại của tên**, không kiểm ngữ nghĩa lời gọi.

### EV-PC06-03 — analysis key khớp ADR-0008 và entities.yaml

- Command: `python3 <scratch>/w5/ai_key_check.py` · ended 2026-09-06T19:36Z
- Oracle: `tasks.yaml common.analysis_key.components` **bằng đúng thứ tự**
  `entities.yaml ENT-analysis.analysis_key.components`; `analysis-result.schema.json`
  `$defs.analysis_key.required` bằng cùng tập; 5 khái niệm của ADR-0008 đều ánh xạ được sang một cột
- Observed: cả ba nguồn cho cùng 7 thành phần
  `[owner_id, target_key, task_type, source_fingerprint, prompt_version, schema_version, generation_number]`;
  5/5 khái niệm ADR-0008 ánh xạ được; hai exclusion (tag, provider) đều được ghi
- Exit code `0` · **PASS**
- **Diff được ghi lại (theo yêu cầu packet EV-03):** ADR-0008 §Quyết định 1 nêu **5** thành phần
  *khái niệm*; entities.yaml và schema hiện thực bằng **7** *cột*. Chênh lệch là do (i) `owner_id`
  được thêm cho owner scoping (REQ-D01) và (ii) "phiên bản prompt/schema" của ADR được tách thành
  `prompt_version` + `schema_version`. Đây là **chi tiết hóa, không mâu thuẫn** — không cần CR.

### EV-PC06-04 — fixture-actor-edge check (quy tắc FIX3)

- Command: `python3 <scratch>/w5/ai_actor_edge.py` · ended 2026-09-06T19:36Z
- Oracle: mỗi `events[].actor` ∈ `caller_modules` của operation ở `ports.yaml`; bộ ba
  (`actor`, `owner_module`, `operation`) ∈ `modules.yaml.allowed_edges`; nếu có `performed_by`
  thì `performed_by == owner_module`; sự kiện `event_type` được bỏ qua
- Expected: 0 FAIL
- Observed lần đầu: **3 FAIL** — fixture `e`, `f`, `g` đặt `actor: MOD-ai-adapter` cho
  `ai.run_inference_task`, nhưng đó là `owner_module`, còn caller hợp lệ duy nhất là
  `MOD-analysis-worker`. **Đúng lớp lỗi mà audit A1-R2 đã nêu.** Đã sửa: `actor` →
  `MOD-analysis-worker`, thêm `performed_by: MOD-ai-adapter`
- Observed lần cuối: **26/26 event PASS**, exit code `0` · **PASS**
- Limitations: kiểm quyền gọi ở mức registry, không kiểm auth scope thực thi.

### EV-PC06-05 — field-level existence check (quy tắc FIX3)

- Command: `python3 <scratch>/w5/ai_fields.py` · ended 2026-09-06T19:36Z
- Oracle: mọi tên bảng trong `expected.rows` tồn tại trong entities.yaml; mọi tên cột tồn tại
  trong bảng đó; cột không tồn tại phải có marker `pending_cr` trong file, nếu không thì FAIL
- Observed: **40 cột** kiểm (bảng `analysis_attempt` ở fixture `h`, `i`), **0 FAIL**,
  **0 cột cần `pending_cr`**
- Exit code `0` · **PASS**

### Không chạy

| Hạng mục | Trạng thái | Lý do |
| --- | --- | --- |
| E1 contract test | `NOT_RUN` | Chưa có code |
| E2 fault injection | `NOT_RUN` | Chưa có code |
| E3 probe CLI/ACP thật | `NOT_RUN` | `contracts/ops/cli-acp-probe.md` — chưa provider nào được dò |
| E4 rubric groundedness | `NOT_RUN` | Chưa có kỳ báo cáo thật (REQ-A4) |
| Independent audit | **chưa xảy ra** | `audit_route: INDEPENDENT_REQUIRED` |

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Task schema tách riêng; input mang source id/hash/evidence level | **DONE** | `tasks.yaml` §2 (ba task, mỗi task có `input.fields` với `source_id`/`source_hash`), §3 (trần evidence) |
| 2 | Enum: claim kind, citation target, unknown comparator, unsupported field, max evidence level | **DONE** | `analysis-result.schema.json` `$defs.statement_kind`, `$defs.source_id`, `$defs.comparator`, `additionalProperties:false` ở mọi object, `$defs.evidence_level` + `tasks.yaml` §3 |
| 3 | Adapter capability theo họ; usage unknown | **DONE** | `providers.yaml` §1–§2, §7; `usage` trong schema ép `unknown ⇒ null` |
| 4 | Retry budget xuyên worker/adapter; fallback allowlist + thứ tự | **DONE** | `tasks.yaml` §1 `retry_budget` (adapter = 0, trích số của PC03), `providers.yaml` §6 |
| 5 | Once-per-generation, trigger reanalysis, đổi provider, ghi cost trung thực | **DONE** | `tasks.yaml` §1 `analysis_key` / `reanalysis_triggers` / `provider_switch_policy` / `usage_recording` |
| 6 | Giao thức probe CLI/ACP | **DONE** | `contracts/ops/cli-acp-probe.md` (6 nhóm kiểm, tiêu chí pass, bằng chứng phải giữ) |
| 7 | Fixture đối kháng (a)–(k) | **DONE** | 11/11 file, chỉ mục ở `acceptance/fixtures/ai/README.md` §1 |
| + | CR-PC04-05 (của chính tôi ở PC04) | **DONE** | `tasks.yaml` task `direction_phrasing` (`satisfies_cr`), `hard_constraints_vi`, kiểm `SV-05`/`SV-06`; schema `$defs.result_direction_phrasing` với `label` là const |
| + | Quy tắc fixture FIX3 (actor-edge + field existence) | **DONE** | EV-PC06-04, EV-PC06-05; định nghĩa `actor` vs `performed_by` ở README §3.1 |

### Invariant (packet yêu cầu dương + đối chứng)

| Invariant | Owner section | Dương | Đối chứng | Trạng thái |
| --- | --- | --- | --- | --- |
| I04 | `tasks.yaml` §1 `analysis_key` | `j` | `j` (payload khác → `IDEMPOTENCY_CONFLICT`), `i` | **DONE** |
| I11 | `grounding.md` §5 | `b`, `f` | `c`, `e` | **DONE** |
| I14 | `tasks.yaml` §1 `usage_recording` | `j` (`unknown:false`) | `h`, `k` (`unknown:true` ⇒ null; schema chặn 0) | **DONE** |
| "Không adapter nào chỉ hứa JSON" | `tasks.yaml` §4 (4 bước, SV-01…07) | `g` | `c`, `d`, `e` (schema pass, ngữ nghĩa từ chối) | **DONE** |

## 6. Baseline drift trong lúc gói chạy

Gói bắt đầu trên FC-W2 sạch (80/80). Tại handoff, **6/80** mục đã đổi vì wave FIX3 đang đáp:
`contracts/ports.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`,
`contracts/ops/deployment.md`, `precode/decision-register.md`, `precode/baseline.json`,
`evidence/handoffs/PC01-handoff.md`.

**Ảnh hưởng tới PC06 — đều theo hướng hội tụ:**

1. **CR-PC03-05 đã đáp.** `ports.yaml` nay viết `label | summary | direction_phrasing`, khớp
   entities.yaml. Lựa chọn đặt tên của PC06 (theo ruling R-03 và chỉ dẫn (a) của Coordinator) nay
   được upstream xác nhận. Tôi đã cập nhật `tasks.yaml` §0 để nói rằng CR-PC03-05 **đã** áp, thay
   vì "sẽ áp" — `alias_map` giữ tên cũ dưới khóa `ports_yaml_before_fix3` để đọc bản cũ vẫn hiểu.
2. **CR-PC04-04 đã đáp.** `report.publish.error_codes` nay có `CONFLICT`. Đây là CR tôi mở ở
   PC04; nó đã đóng, không còn là unresolved ref.
3. Mọi kiểm tra EV-PC06-01…05 đã **chạy lại trên bản upstream mới** và đều PASS.

**Đề nghị Coordinator:** re-verify EV-PC06-02 và EV-PC06-04 trước khi freeze nếu `ports.yaml`,
`modules.yaml` hoặc `capabilities.yaml` đổi tiếp sau các hash ở §3.3.

## 7. Unresolved refs

### 7.1 Change request PC06 phát ra

| ID | Gửi tới | Nội dung | Chặn gì |
| --- | --- | --- | --- |
| `CR-PC06-01` | PC03 | `contracts/retry-policy.yaml` chưa có ngân sách **timeout inference theo task**. PC06 định nghĩa trong `tasks.yaml` (`label` 120 s, `summary` 300 s, `direction_phrasing` 180 s, đều `PROVISIONAL`, đều < `lease_ttl_analysis` = 900 s). Đề nghị PC03 đăng ký chúng để mọi số timeout nằm một chỗ | Không chặn văn bản; chặn E1 |
| `CR-PC06-02` | PC02 | `ENT-analysis-task` có `state` gồm `pending｜claimed｜running｜retry_wait｜done｜failed｜abandoned`, còn `contracts/state/analysis.yaml` dùng `pending｜running｜retry_wait｜valid｜failed｜unknown_attempt`. Hai enum lệch nhau ở `claimed`/`done`/`abandoned` so với `valid`/`unknown_attempt`. Đề nghị PC02+PC03 thống nhất; PC06 dùng enum của `state/analysis.yaml` vì đó là nguồn chuẩn của transition | Chặn E1 của hàng đợi task |
| `CR-PC06-03` | PC01 | `capabilities.yaml` ACT-ai-adapter chưa khai tường minh rằng adapter **không đăng ký tool nào** (`tool_definitions_registered = 0`) — hiện chỉ có `tool_scope: [inference_only]` ở ACT-analysis-worker. Fixture `f` dùng con số này làm oracle | Chặn oracle ISO-01 |
| `CR-PC06-04` | PC09 | Đăng ký rubric groundedness (`grounding.md` §6) và bảng probe (`cli-acp-probe.md` §6) vào kế hoạch đánh giá A4/A5; ghi rõ AC-16 báo **`BLOCKED`** (không phải `FAIL`) khi mọi adapter CLI chưa qua probe | Chặn traceability G4 |
| `CR-PC06-05` | PC07 | Màn hình Settings phải nói rõ: đổi provider/model chỉ áp dụng cho phân tích **mới**, không chạy lại kho (`tasks.yaml` §1 `provider_switch_policy.ui_obligation_vi`); và phải hiển thị `analysis.analyzed_at` cùng `discovered_at` (`grounding.md` §4.5) | Không chặn |

### 7.2 CR đã đóng bởi upstream trong lúc gói chạy

`CR-PC03-05` (đặt tên task_type) và `CR-PC04-04` (`CONFLICT` cho `report.publish`) — cả hai đã
được áp; xem §6.

### 7.3 Quyết định `PROVISIONAL` do PC06 đưa ra (cần Owner phê chuẩn)

| # | Quyết định | Căn cứ | Phương án bị bác |
| --- | --- | --- | --- |
| 1 | `confidence` của nhãn là enum **rời rạc** `low｜medium｜high`, không phải số | Cùng lý do identity.md §7: MVP không có cách hiệu chỉnh thang liên tục | Điểm xác suất 0..1 — tạo độ chính xác giả |
| 2 | `usage.unknown = true` ⇒ **cả ba** trường null, ép ở mức schema | I14, REQ-D44 | Cho phép 0 — chính là điều I14 cấm |
| 3 | `source_verified` yêu cầu `evidence_level >= abstract` (SV-03) | REQ-AC11: chỉ có post thì không thể "kiểm được từ nguồn" | Cho phép ở `post_only` — làm nhãn evidence level vô nghĩa |
| 4 | Timeout inference theo task: 120 / 300 / 180 s | Ràng buộc trên là `lease_ttl_analysis` = 900 s | Một timeout chung — không phản ánh chênh lệch độ dài input |
| 5 | `SV-06` chặn một **danh sách cụm từ** khẳng định tính mới | REQ-D54; hàng rào cuối, cố ý thô | Dựa hoàn toàn vào prompt — không kiểm chứng được |
| 6 | Ngưỡng rubric: G1/G2 phải đạt **1.00**, G3–G5 đạt 0.80, mẫu 10 mục/kỳ, ≥ 3 kỳ | G1/G2 là tính trung thực, không phải chất lượng: một lỗi là lỗi hợp đồng | Một ngưỡng chung 0.8 cho cả năm — dung thứ cho citation bịa |
| 7 | `full_text` giữ trong enum nhưng **không đạt được** ở MVP; output khai `full_text` phải FAIL | SRC-SPEC §6.1 không có bước tải toàn văn | Bỏ khỏi enum — sẽ phải migrate khi thêm nguồn |
| 8 | Mọi adapter mặc định `enabled = false`, kể cả họ `api_key`, tới khi `terms_check` xong | ADR-0010 §3, §4 | Mặc định bật cho api_key — REQ-A5 áp cho mọi họ |

### 7.4 Câu hỏi còn mở PC06 không tự giải

- **REQ-A5** (`KC`): điều khoản từng nhà cung cấp. PC06 **không** đọc thay và không đoán; mọi
  adapter ở `enabled = false` cho tới khi Owner đọc và xác nhận.
- **REQ-AC16**: hiện là **`BLOCKED`**, không phải `FAIL` — chưa adapter CLI nào qua probe.
- **REQ-A4** / rubric §6: `NOT_RUN`, cần ≥ 3 kỳ thật.
- **REQ-D40** (model rẻ/mạnh) là khuyến nghị mặc định, Owner được đặt khác.
- `prompt_version` khởi đầu `1.0.0` cho cả ba task; **cảnh báo chi phí** đã ghi: đổi
  `prompt_version` sinh analysis key mới cho **toàn kho** (ADR-0008).

### 7.5 Scenario ID

PC06 **không** đề nghị ID mới, nên **không có va chạm** với bất kỳ gói nào và **không** fixture
nào cần `scenario_id_provisional: true`. Mọi fixture của gói này gắn vào `SC11`, `SC16`, `SC17`,
`SC28` — đều đã tồn tại.

Bối cảnh đánh số tại thời điểm handoff, theo hai chỉ dẫn liên tiếp của Coordinator:
`SC33`–`SC44` thuộc PC03/PC04/PC08 (`SC44` = `data.purge_all`), `SC45`–`SC48` vừa được PC07 đăng
ký. Nếu về sau PC06 cần ID mới thì lấy từ **`SC49+`**. Đã kiểm bằng script:
`grep` trên toàn bộ file PC06 không thấy tham chiếu `SC45`–`SC48` nào ngoài chính câu ghi chú
bối cảnh này ở `acceptance/fixtures/ai/README.md` §1.

## 8. Những gì gói này KHÔNG chứng minh

- Không chứng minh code chạy đúng: chưa có code. Dự án vẫn `NOT_READY_FOR_PRODUCT_CODE`.
- Không chứng minh bất kỳ adapter nào bị cô lập thật (E3 `NOT_RUN`); không kết luận gì về điều
  khoản của nhà cung cấp nào.
- Không chứng minh chất lượng summary (E4 `NOT_RUN`).
- Không tuyên bố hệ thống miễn nhiễm prompt injection — cái được tuyên bố là **bán kính thiệt hại
  bị giới hạn và đo được** (`grounding.md` §5.3).
- Không có independent audit: mọi bằng chứng §4 là `SELF_VALIDATION` do chính người viết
  candidate chạy.
- B07, B13, B16, B17 vẫn **OPEN** trong `agent_profile/registry.json`.

## 9. Next actor

`Coordinator`. Đề nghị: (1) rehash độc lập 17 file ở §2; (2) re-verify EV-PC06-02/04 nếu
`ports.yaml`/`modules.yaml`/`capabilities.yaml` đổi tiếp; (3) định tuyến Auditor độc lập;
(4) chuyển 5 CR ở §7.1; (5) đưa 8 quyết định `PROVISIONAL` ở §7.3 vào OWNER_DECISION_REQUEST;
(6) lưu ý Owner rằng REQ-AC16 hiện `BLOCKED` và điều đó là trạng thái đúng, không phải lỗi.

`lease_released_at`: 2026-09-06T19:40Z. Sau file này `worker-W5` **không ghi thêm file nào**;
sửa tiếp cần packet mới, baseline mới, lease mới.


---

# ADDENDUM — PKT-PC06-FIX1 (R4-04, remediation của F-A1R3-05)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC06-FIX1` · authority `AUTH-COORD-PC06-FIX1` · lease `LEASE-PC06-e2` (**fencing 2**) |
| status | **`DONE`** · completion_claim `DRAFT_FOR_REVIEW` · lease_released_at 2026-09-06T21:10Z |
| finding | `F-A1R3-05` (MINOR) · ruling `R4-04` |

## C1. Delta

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `contracts/schemas/analysis-result.schema.json` | MODIFY | `f26720ee04852161b4e71b4ab61c0f11c0187fcbfd25759e05245cfdb7ac172d` | 24391 |
| `acceptance/fixtures/ai/README.md` | MODIFY | `4992d20574e8d5b52b620ce7ff4291b9e38f9dac0e946936822fc2e8186bdc5a` | 12204 |

## C2. Sai lệch được khai báo — `DEV-PC06-01`

Audit đúng: PC06 dùng `allOf` + ba nhánh `if/then` trên `task_type` thay cho `oneOf` mà cả
TASK_PACKET lẫn `agent_profile/protocol.md` §10 nêu, và **không khai báo ở đâu cả**. Nay khai ở
`x-contract.deviations` với bốn phần:

**Lý do.** Ba task dùng chung một envelope và chỉ khác ở `result`. Với `oneOf` toàn envelope,
mỗi biến thể phải lặp lại toàn bộ `required` của envelope — ba lần, và mọi lần sửa envelope phải
sửa ba chỗ. Quan trọng hơn: khi payload sai ở envelope, `oneOf` báo lỗi ở **cả ba** nhánh và
validator không nói được nhánh nào đáng lẽ áp dụng, nên thông điệp lỗi mất giá trị chẩn đoán —
đúng thứ mà một fixture âm cần.

**Lập luận tương đương.** Đóng kín vì bốn điều kiện cùng đúng: `task_type` là enum ba giá trị nên
đúng một nhánh `if` khớp (loại trừ lẫn nhau theo **cấu trúc**, không theo quy ước);
`additionalProperties: false` ở cấp gốc; mọi `$defs.result_*` và mọi object con
(`analysis_key`, `provider_ref`, `usage`, `statement`, `comparator`) đều
`additionalProperties: false`; `result` là `required`. Auditor đã tự xác minh cùng bốn điểm này.

**Fixture chứng minh tính loại trừ.** `d-schema-valid-but-uncited.json` là bằng chứng mạnh nhất:
payload `task_type='summary'` bị từ chối tại `/result/statements/0/citation_refs` — nếu `if/then`
**không** kích hoạt thì `result` sẽ không bị ràng buộc và payload đó sẽ PASS. Cộng thêm
`c-citation-to-unknown-source.json` (biên schema/ngữ nghĩa đúng chỗ) và
`k-zero-api-key-all-tasks-via-cli.json` (ba payload ba task cùng validate, mỗi payload chỉ thỏa
nhánh của mình).

**Thẩm quyền.** Việc protocol §10 có admit `allOf`+`if/then` hay không là quyết định của authority
sở hữu §10, không phải của PC06 — R4-04 đã chấp nhận và khai báo này tồn tại để PC09 hoặc một
validator tĩnh về sau không vấp phải một sai lệch không được ghi.

## C3. R4-01 trong README của `ai/`

`acceptance/fixtures/ai/README.md` §3.2 nay chép **nguyên văn** đoạn R4-01 (kể cả "No
per-package allowlist"), thay cho cách diễn đạt riêng của PC06. Thư mục `ai/` được audit xác nhận
sạch từ đầu; gate độc lập chạy lại trong `PKT-PC04-FIX2` cho `ai`: **11 file, 40 cột, 0 chưa giải
quyết**.

## C4. `EV-PC06-01` chạy lại

`python3 <scratch>/w5/ai_validate.py` — metaschema PASS, 11 fixture parse, **8 payload dương**
validate, **4 payload âm** fail đúng chỗ đã khai (1 schema tại
`/result/statements/0/citation_refs`, 3 schema-valid bị `SV-02`/`SV-03`). Exit code `0` · **PASS**.

## C5. Concerns

1. `x-contract.deviations` là trường mới do PC06 đặt ra; nó chưa nằm trong danh sách trường bắt
   buộc của baseline §3. Nếu Coordinator muốn cơ chế khai báo sai lệch dùng chung cho mọi gói,
   đây là chỗ để chuẩn hóa tên trường.
2. Sai lệch đã được khai nhưng **chưa** được protocol §10 sửa. Nếu PC09 viết một static check
   khẳng định `oneOf`, nó vẫn sẽ đỏ ở schema này — cần R4-04 được phản ánh vào §10 hoặc vào
   chính static check đó.
