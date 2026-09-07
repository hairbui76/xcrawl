---
contract_id: CT-fixtures-ai
version: 0.1.0
status: draft
owner_role: AI contract owner
source_refs:
  - "SRC-PLAN §11 PC06 (danh mục fixture bắt buộc)"
  - "SRC-PLAN §13 (ma trận truy vết AC → SC)"
  - "SRC-PLAN §10 (ma trận lỗi)"
  - "SRC-SPEC §10.1, §10.2, §10.3, §10.4"
  - "SRC-SPEC §11.4"
  - "SRC-SPEC §12 AC-06, AC-10, AC-11, AC-16, AC-17"
requirement_refs:
  [REQ-D20, REQ-D21, REQ-D22, REQ-D25, REQ-D41, REQ-D43, REQ-D44, REQ-D51, REQ-D54,
   REQ-A5, REQ-AC06, REQ-AC10, REQ-AC11, REQ-AC16, REQ-AC17]
decision_refs: [B07, B13, B16, B17, AMD-B07, AMD-B16, AMD-B17, ADR-0008, ADR-0010]
invariant_refs: [I04, I11, I14, I16]
producers: [MOD-analysis-service]
consumers: [MOD-analysis-worker, MOD-ai-adapter, MOD-report-service, MOD-web-ui]
dependencies:
  - contracts/ai/tasks.yaml
  - contracts/ai/providers.yaml
  - contracts/ai/grounding.md
  - contracts/ops/cli-acp-probe.md
  - contracts/schemas/analysis-result.schema.json
  - contracts/state/analysis.yaml
  - contracts/errors.yaml
  - contracts/retry-policy.yaml
  - contracts/data/entities.yaml
  - contracts/ports.yaml
  - contracts/modules.yaml
scope: >-
  Fixture cho ba task AI, grounding, cô lập adapter và ngân sách thử lại. Đây là DỮ LIỆU VÀO +
  ORACLE, **không phải test đã chạy**. Ở gói PC06 chỉ E0 (validate tĩnh) được thực hiện;
  E1–E4 là `NOT_RUN`.
verification: "EV-PC06-01 (schema + dương/âm), EV-PC06-02 (tham chiếu), EV-PC06-04 (actor-edge), EV-PC06-05 (field existence)."
claim_ceiling: DRAFT_FOR_REVIEW
---

# Fixture AI — chỉ mục và cách dùng

## 1. Danh mục

| File | Fixture ID | Kiểm tra điều gì | Loại | Scenario | Invariant |
| --- | --- | --- | --- | --- | --- |
| `a-post-only-summary-inference-labelled.json` | FX-AI-A | Chỉ có post → `post_only`, mọi phát biểu tính mới là `ai_inference`, `comparator: unknown` | dương | SC11 | I11 |
| `b-instruction-injection-in-post.json` | FX-AI-B | Injection trong post → chỉ sinh nhãn; tool = 0, canary không lộ | dương | SC17 | I11 |
| `c-citation-to-unknown-source.json` | FX-AI-C | Citation trỏ `source_id` không được cấp → `AI_OUTPUT_INVALID` | âm (ngữ nghĩa SV-02) | SC11, SC17 | I11 |
| `d-schema-valid-but-uncited.json` | FX-AI-D | `source_verified` không citation (schema bắt) + biến thể chỉ SV-03 bắt được | âm (schema **và** ngữ nghĩa) | SC11 | I11 |
| `e-transcript-secret-canary.json` | FX-AI-E | Transcript chứa canary → từ chối, canary không vào log/details | âm (SV-02) + redaction | SC17 | I11 |
| `f-tool-request-in-transcript.json` | FX-AI-F | Yêu cầu gọi tool → không có tool để gọi | dương + đếm | SC17 | I11 |
| `g-cli-json-embedded-in-prose.json` | FX-AI-G | Bóc JSON khỏi transcript; hai ứng viên JSON → từ chối | dương + biến thể âm | SC16 | I11 |
| `h-provider-unavailable-no-fallback.json` | FX-AI-H | Provider lỗi, không fallback → `failed`, usage `unknown` | hành vi | SC16 | I14 |
| `i-crash-after-provider-completion.json` | FX-AI-I | Crash sau khi model chạy → `unknown_attempt`, `cost_uncertain` | hành vi | SC28 | I04, I14, I16 |
| `j-same-key-resubmitted-one-result.json` | FX-AI-J | Nộp lại cùng key → đúng một kết quả hợp lệ | dương + hành vi | SC28 | I04, I16 |
| `k-zero-api-key-all-tasks-via-cli.json` | FX-AI-K | Không API key nào, **cả ba** task qua CLI | dương | SC16 | I14 |

Bộ này **không** đề nghị scenario ID mới: mọi fixture gắn vào `SC11`, `SC16`, `SC17`, `SC28` đã
tồn tại. Bối cảnh đánh số ở thời điểm handoff: `SC33`–`SC44` thuộc PC03/PC04/PC08
(`SC44` = `data.purge_all`), `SC45`–`SC48` thuộc PC07. Nếu về sau PC06 cần ID mới thì lấy từ
**`SC49+`**. Vì PC06 không tạo ID nào nên **không có va chạm** và không có fixture nào cần
`scenario_id_provisional`.

## 2. Bao phủ invariant: dương và đối chứng

| Invariant | Owner section | Fixture dương | Đối chứng (phải FAIL nếu triển khai sai) |
| --- | --- | --- | --- |
| I04 — một kết quả hợp lệ mỗi key; đổi tag không gọi lại AI | `tasks.yaml` §1 `analysis_key` | `j` (nộp lại → một hàng) | `j` biến thể payload khác → `IDEMPOTENCY_CONFLICT`; `i` (attempt không thành kết quả) |
| I11 — nguồn/AI không đọc secret, không gọi tool, không đổi recipient | `grounding.md` §5 | `b`, `f` (đếm tool = 0) | `c`, `e` (citation bịa / canary bị từ chối) |
| I14 — usage `unknown` không ghi thành 0 | `tasks.yaml` §1 `usage_recording` | `j` (`unknown: false` với token thật) | `h`, `k` (`unknown: true` ⇒ cả ba null; schema chặn giá trị 0) |
| I16 — attempt không bao giờ là kết quả | `contracts/state/analysis.yaml` | `j` (chỉ attempt `accepted` mới thành kết quả) | `i` (`unknown_attempt` → `valid` là transition bị cấm) |

## 3. Hình dạng chung của một fixture

```text
fixture_id, title, purpose
scenario_refs, invariant_refs, decision_refs, requirement_refs, source_refs
contract_refs, owner_id, claim_ceiling, evidence_status
validation_target      : schema/hợp đồng dùng để kiểm
expected_validation    : accept | reject_schema | reject_semantic | reject_extraction | not_applicable
expected_violation     : {check_id, json_pointer?, validation_failure_kind, error_code}
given                  : cấu hình task/provider/nguồn trước sự kiện
events[]               : {seq, at, actor, operation | event_type, performed_by?, description}
expected               : analysis_result* | rejected_payload | rows | counts | row_oracles
forbidden_effects      : những gì KHÔNG được xảy ra — phần bắt lỗi thật sự
```

### 3.1 `actor` so với `performed_by` — hai thứ khác nhau

| Khóa | Nghĩa | Ràng buộc kiểm tự động |
| --- | --- | --- |
| `actor` | Module **gọi** operation | PHẢI có trong `caller_modules` của operation đó ở `contracts/ports.yaml`, VÀ bộ ba (`actor`, `owner_module`, `operation`) phải có trong `contracts/modules.yaml` → `allowed_edges` |
| `performed_by` | Service **thực thi** transaction / công việc | Nếu có mặt thì phải bằng `owner_module` của operation. **Không** phải một khẳng định về quyền gọi |

Ví dụ cụ thể và là lỗi hay gặp: `ai.run_inference_task` có `owner_module = MOD-ai-adapter` và
`caller_modules = [MOD-analysis-worker]`. Vì vậy `actor` phải là `MOD-analysis-worker`;
`MOD-ai-adapter` chỉ được xuất hiện ở `performed_by`. Ba fixture của bộ này (`e`, `f`, `g`) ban
đầu viết sai đúng chỗ đó và đã được sửa sau khi `EV-PC06-04` bắt được — xem
`evidence/handoffs/PC06-handoff.md`.

Sự kiện không phải operation (crash tiến trình) dùng `event_type` thay cho `operation` và không
bị kiểm edge.

### 3.2 Tên cột trong `rows` — quy tắc R4-01

Quy tắc dưới đây là **ruling R4-01** (FIX4, sau F-A1R3-01), ràng buộc **cả sáu** thư mục fixture
và được chép nguyên văn:

> Under `given.rows.<entity>[]` and `expected.rows.<entity>[]`, every key is either (a) a column
> that exists in `contracts/data/entities.yaml` for that entity, (b) an annotation whose key
> **starts with `_`** (`_note`, `_target`, `_note_vi`, `_save_channel_note`,
> `_created_in_transaction`, `_payload_contains`, …), or (c) a column carrying an in-file
> `pending_cr: CR-…` marker. No per-package allowlist.

Hệ quả cho bộ này: **40 cột** được kiểm (bảng `analysis_attempt` ở fixture `h` và `i`),
**0** khóa chưa giải quyết và **0** marker `pending_cr` — audit A1-R3 xác nhận thư mục `ai/`
sạch từ đầu. Checker bỏ qua khóa `_…` theo quy tắc, không theo danh sách tên: một allowlist riêng
của từng gói là điều R4-01 cấm tường minh.

### 3.3 Ý nghĩa của `expected_validation`

| Giá trị | Nghĩa | `EV-PC06-01` khẳng định |
| --- | --- | --- |
| `accept` | Payload hợp lệ | 0 lỗi schema |
| `reject_schema` | JSON Schema tự bắt được | ≥ 1 lỗi, và đường dẫn lỗi khớp `expected_violation` → `json_pointer` |
| `reject_semantic` | Schema **chấp nhận**, chỉ tầng ngữ nghĩa bắt được | **0 lỗi schema** (chứng minh tầng ngữ nghĩa là cần thiết) và `check_id` phải tồn tại trong `tasks.yaml` §4 |
| `reject_extraction` | Bị chặn ở bước bóc JSON, trước cả schema | Kiểm bằng tay/E1; `providers.yaml` §3 |
| `not_applicable` | Fixture hành vi, không có payload để validate | — |

Phân biệt `reject_schema` với `reject_semantic` là điểm quan trọng nhất của bộ này: nó chứng
minh bằng máy rằng **"JSON đúng schema" không phải toàn bộ hợp đồng** (REQ-D43, SRC-PLAN §5).
Nếu một fixture khai `reject_semantic` mà schema đã bắt được thì `EV-PC06-01` **FAIL** — vì khi
đó fixture đang phóng đại vai trò của tầng ngữ nghĩa.

## 4. Quy ước về secret và canary

**Quy ước ký hiệu tượng trưng.** Tên tượng trưng trong `row_oracles` / `hash_oracles` (ví dụ `h_c`, `rp_early`, `tag_v1`) viết **chữ thường** để không bao giờ bị đọc nhầm là một error code (vốn viết hoa toàn bộ) của `contracts/errors.yaml`. Chúng trỏ tới giá trị được định nghĩa trong `given` của chính fixture đó, không phải một định danh hợp đồng.


Fixture **không bao giờ** chứa một secret hay canary thật. `e-transcript-secret-canary.json`
dùng placeholder `<CANARY_TOKEN_NOT_STORED_IN_FIXTURE>`; ghi một canary thật vào repo sẽ tự tạo
ra chính lỗ hổng mà fixture đang kiểm. Oracle là **số lần xuất hiện = 0** ở các nơi bền, không
phải so sánh với một chuỗi nằm trong file.

Tương tự, không fixture nào chứa transcript thô: `errors.yaml` cấm đưa transcript vào
message/details, và cấm đó áp dụng cả cho tài liệu kiểm thử.

## 5. Ngân sách: trích dẫn, không định nghĩa lại

Fixture `h` và `i` có khóa `budgets_cited` trỏ tới `contracts/retry-policy.yaml`. Con số
(`analysis_attempts_per_item` = 2, `provider_unavailable_waits` = 3,
`analysis_unknown_attempt_auto_rerun` = 1) thuộc PC03. PC06 **không** phát biểu số khác; nếu một
fixture cần một số khác thì đó là một CR tới PC03, không phải một giá trị mới viết ở đây.

## 6. Cách dùng ở từng cấp bằng chứng

| Cấp | Dùng thế nào | Trạng thái ở PC06 |
| --- | --- | --- |
| E0 | Parse; validate payload dương/âm theo `analysis-result.schema.json`; kiểm actor-edge; kiểm tên cột; kiểm operation/entity/error code tồn tại | **ĐÃ CHẠY** (EV-PC06-01…05, `SELF_VALIDATION`) |
| E1 | Nạp `given`, phát `events` qua đúng operation, so `expected`, khẳng định `forbidden_effects` không xảy ra | `NOT_RUN` — cần code |
| E2 | Fault injection tại các mốc của `contracts/state/analysis.yaml` `crash_after_provider_completion_timeline` | `NOT_RUN` |
| E3 | Chạy thật với một provider — thuộc `contracts/ops/cli-acp-probe.md` | `NOT_RUN` |
| E4 | Chấm groundedness theo rubric `contracts/ai/grounding.md` §6 | `NOT_RUN` — chưa có kỳ báo cáo thật |

## 7. Cái các fixture này KHÔNG chứng minh

- Không chứng minh code chạy đúng: chưa có code (SRC-PLAN §14.2, cấp E0).
- Không chứng minh bất kỳ adapter nào thật sự bị cô lập — đó là E3 và mọi probe đang `NOT_RUN`.
  Fixture `k` mô tả nhánh **pass** của AC-16; trạng thái thực tế hôm nay là **`BLOCKED`** vì chưa
  adapter nào qua `cli-acp-probe.md` §4 (ADR-0010).
- Không chứng minh chất lượng summary (E4).
- Không chứng minh hệ thống chống được mọi prompt injection — cái được chứng minh là bán kính
  thiệt hại bị giới hạn và đo được (`grounding.md` §5.3).
- Không chứng minh điều khoản của nhà cung cấp nào (REQ-A5 luôn `KC`).

## 8. Bất biến khi sửa fixture

Sửa một `expected` để triển khai pass là vi phạm hợp đồng (SRC-PLAN §15,
`agent_profile/worker.md`). Nếu một oracle sai, mở change request có bằng chứng. Đặc biệt: không
được hạ một `reject_semantic` thành `accept` để tránh phải viết tầng kiểm ngữ nghĩa.
