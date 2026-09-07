---
contract_id: CT-evidence-tools
version: 0.3.0
status: draft
owner_role: verification owner (PC09)
source_refs:
  - "SRC-PLAN §11 PC09 (mục 'Validate schema/examples, reference integrity, transition/error coverage và denied-edge scenarios bằng tooling tài liệu nhẹ')"
  - "SRC-PLAN §14.2 (E0 — lint schema/reference/traceability)"
  - "SRC-PLAN §17 (Definition of Ready: 'E0 đã chạy thật và có manifest')"
requirement_refs:
  - "REQ-S13.2-01"
  - "REQ-S13.2-02"
decision_refs:
  - "R-02"
  - "R-05"
  - "R4-01"
  - "R4-02"
  - "R4-04"
invariant_refs: []
producers: ["MOD-none"]
consumers: ["MOD-none"]
dependencies:
  - "contracts/"
  - "acceptance/"
  - "precode/"
  - "agent-tasks/"
  - "python3 ≥ 3.10, PyYAML, jsonschema"
scope: >
  Bộ công cụ kiểm tra tĩnh (E0) cho baseline hợp đồng Pre-code. **Hai** công cụ, cả hai chỉ đọc
  và cả hai chạy trong job CI `e0`: `e0_check.py` chạy **25 check** trên contracts/, acceptance/,
  precode/, evidence/ (§1–§7); `verify_cards.py` chạy **13 check** trên 18 task card của
  agent-tasks/ — dạng chạy được của EV-PC10-01 — cộng một self-test âm (§8). Mỗi công cụ xuất một
  báo cáo JSON máy đọc được và một bản tóm tắt cho người. Đây là tài liệu sử dụng, giới hạn và
  cách đếm của chúng.
verification: "Bản thân công cụ là phương tiện verification; kết quả của nó là SELF_VALIDATION."
claim_ceiling: DRAFT_FOR_REVIEW
---

# E0 static checks

*Hai công cụ: `e0_check.py` (§1–§7, 25 check) và `verify_cards.py` (§8, 13 check + self-test âm).*

## 1. Cái này chứng minh gì và KHÔNG chứng minh gì

E0 là cấp bằng chứng thấp nhất trong năm cấp của SRC-PLAN §14.2. Nó chứng minh **bộ hợp đồng tự
nhất quán ở phần đã kiểm**. Nó **không** chứng minh:

- rằng có code nào tồn tại, hay bất kỳ guard nào chạy;
- rằng X, Telegram, arXiv/OpenAlex hay một provider AI nào hoạt động như mô tả;
- rằng một con số `PROVISIONAL` là đúng;
- rằng một fixture parse được là một test đã pass.

Một `PASS` ở đây là bằng chứng về tính nhất quán nội bộ của tập con đã kiểm, không hơn. Mọi kết
quả mang nhãn `SELF_VALIDATION`: người viết công cụ cũng là người viết một phần các file mà nó
kiểm. Nó **không** thay thế audit độc lập.

## 2. Chạy

Chạy từ một thư mục scratch, **không bao giờ từ trong repo** — công cụ chỉ đọc, nhưng Python có
thể sinh `__pycache__` cạnh script nếu không tắt:

```
PYTHONDONTWRITEBYTECODE=1 python3 <repo>/evidence/tools/e0_check.py \
    --repo <repo> \
    --json-out <repo>/evidence/runs/E0-<UTCstamp>.json
```

Tuỳ chọn `--only <prefix>[,<prefix>...]` chạy một tập con, ví dụ `--only E0-14,E0-15`.

**`files_scanned` không tính `evidence/runs/`.** Một lần chạy ghi báo cáo của chính nó vào thư mục
đó, nên nếu tính nó thì lần chạy sau đếm ra một con số khác và một artefact đã đăng ký không tái
lập được chính số của mình (`F-A2R1-11`). Thư mục đó chứa đầu ra công cụ, không chứa nội dung
hợp đồng.

**Exit code:** `0` nếu không check nào ở trạng thái `FAIL`; `1` nếu có; `2` nếu chính công cụ lỗi.
Một `BLOCKED` (thiếu file đầu vào) **không** làm exit code khác 0 — nó được báo riêng, vì "không
đo được" khác "đo được và sai".

Phụ thuộc: python3 stdlib + PyYAML + jsonschema. Không có phụ thuộc nào khác và công cụ **không**
truy cập mạng.

## 3. Hai mươi lăm check

| ID | Kiểm gì | Oracle |
| --- | --- | --- |
| `E0-01-parse` | Mọi `.yaml`/`.json` dưới `contracts/`, `acceptance/`, `precode/`, `evidence/` | `yaml.safe_load` / `json.load` không ném exception |
| `E0-02-metaschema` | Mọi `*.schema.json` | `Draft202012Validator.check_schema`; `$schema` đúng URI 2020-12; nếu dùng `allOf`+`if/then` thay `oneOf` thì phải có `x-contract.deviations` khai báo (R4-04) |
| `E0-03-fixture-schema` | Fixture có `validation_target` là một `*.schema.json` | `accept` ⇒ payload validate; `reject`/`reject_schema` ⇒ payload sinh ≥ 1 lỗi; `reject_semantic` ⇒ payload **qua** schema (từ chối là cửa semantic ở dưới); `not_applicable` ⇒ bỏ qua có ghi lý do |
| `E0-04-operation-refs` | Mọi operation id trong trường có cấu trúc | tồn tại trong `contracts/ports.yaml` |
| `E0-04b-prose-op-tokens` | Token operation trong **văn xuôi** dưới `contracts/` và `acceptance/` | Nguồn duy nhất của quy tắc: `contracts/ports.yaml` `conventions.prose_token_rule_vi`. Một `` `<a>.<b>` `` phải phân giải thành **operation của ports.yaml** HOẶC **`<entity>.<column>` của entities.yaml**; token có phân đoạn đầu không phải domain operation cũng không phải tên entity (đường dẫn file, khóa YAML cấu trúc, host, idiom thư viện) được bỏ qua. Check này báo **nửa operation** |
| `E0-04c-prose-column-tokens` | Token cột trong văn xuôi | Cùng quy tắc, báo **nửa cột**. Tách khỏi `E0-04b` (ruling FIX7) vì "gọi tên một operation không tồn tại" và "gọi tên một cột không tồn tại" có chủ sở hữu khác nhau và cách sửa khác nhau |
| `E0-04d-prose-error-tokens` | Token SCREAMING_SNAKE trong văn xuôi | phải là mã đã đăng ký trong `errors.yaml`, hoặc một từ trong `STATUS_VOCABULARY` — bộ này gồm từ vựng trạng thái/claim của baseline §3 **và** các message type của `protocol.md` (`TASK_PACKET`, `HANDOFF`, `AUDIT_REPORT`, …), theo ruling FIX7 |
| `E0-05-error-code-refs` | Mọi mã lỗi trong trường có cấu trúc | tồn tại trong `contracts/errors.yaml` |
| `E0-06-requirement-refs` | Mọi `REQ-*` trong `contracts/`, `acceptance/`, `precode/` | tồn tại trong `precode/requirements.csv`; token sai dạng cũng bị báo |
| `E0-07-id-refs` | Mọi `SC`/`I`/`B`/`ADR`/`AMD` | `SC` phân giải trong `acceptance/scenarios.yaml`; `I` trong SRC-PLAN §7 + `invariants.md`; `B01..B17`; `ADR` có file; `AMD` có mục trong `decision-register.md`. Range marker (`SC54+`) KHÔNG phải citation; `evidence/handoffs/` ngoài phạm vi quét văn xuôi — xem §5.7 |
| `E0-08-contract-header` | Header baseline §3 | YAML: 14 trường top-level (OpenAPI: `info.x-contract`); Markdown: front-matter; JSON Schema: `$id`/`title`/`description` + `x-contract`; fixture JSON: `x-contract` hoặc README thư mục liệt kê file **theo tên**; ADR: bộ 10 trường của ruling R-05 |
| `E0-09-state-lint` | `contracts/state/*.yaml` | enum trạng thái kín; mọi trạng thái reachable từ initial; terminal không có transition đi ra trừ khi `terminal_state_rule` **gọi tên** transition đó; ba danh sách terminal/non-terminal/quasi phân hoạch enum |
| `E0-10a-denied-edge-scenario` | `forbidden_edges` của `modules.yaml` | mỗi `FE-nn` được một scenario trích trong `forbidden_edge_refs` |
| `E0-10b-denied-edge-oracle` | `forbidden_edges` ↔ `denied_cases` ↔ fixture `boundary/` | **Song ánh khớp nội dung** (CR-PC01-11): mỗi `FE-nn` ↔ đúng một denied case có `attempted_edge` khớp caller/callee và `expected_error_code` đã đăng ký ↔ đúng một sự kiện quét có `actor`/`callee`/`denied_case_ref`/`expected_error_code`/`operation` khớp. Hai chiều ngược: không tham chiếu tới cạnh không tồn tại, không trỏ trùng. **Cộng (F-A2R1-05):** một operation được gọi tên phải do **chính callee sở hữu** khi callee là `MOD-*`; khi callee là `EXT-*` nó là port nội bộ mà kẻ vi phạm cố tạo ra hiệu ứng, theo quy ước đã khai trong `modules.yaml default_deny`. **Cộng (F-A2R2-04):** một case `operation: null` thiếu `event_type` hoặc `operation_absent_reason_vi` là **violation**, không phải note — quy tắc và cửa kiểm trích nó phải nói cùng một điều về cái gì là bắt buộc |
| `E0-11a-no-orphan` | `acceptance/traceability.csv` | số dòng bằng `requirements.csv`; không dòng P0 với status XN/UQ nào là `ORPHAN`; `coverage_status` nằm trong từ vựng |
| `E0-11b-invariant-polarity` | `acceptance/scenarios.yaml` | mỗi invariant có ≥ 1 scenario khai `positive` **và** ≥ 1 khai `negative`. **`mixed` tính cho KHÔNG cực nào** (F-A2R1-10): một ca hỗn hợp không phải một counterexample chuyên dụng, và tiêu đề của check không được hứa nhiều hơn oracle của nó |
| `E0-12-forbidden-strings` | Phạm vi quét (`contracts`, `acceptance`, `precode`, `evidence`) | **Viết lại ở đợt FIX10 theo `CR-PC01-13`.** Trước phê chuẩn nó là một lệnh cấm phẳng: không file nào vượt `DRAFT_FOR_REVIEW`. Sau `OD-20260907-01` nó là một **cửa phạm vi**: `ACCEPTED`/`RATIFIED`/`CONTRACT_READY` chỉ hợp lệ trong file có `ratification_ref: OD-20260907-01` (hoặc bất kỳ đâu dưới `precode/`, nơi phê chuẩn được ghi); `CONTRACT_READY` thêm điều kiện file phải nằm trong **bốn phạm vi đã phê chuẩn** — danh sách **không đủ điều kiện** viết cứng trong `CONTRACT_READY_INELIGIBLE_PREFIXES`/`_FILES`. Nhãn **trên** `CONTRACT_READY` vẫn bị cấm tuyệt đối trong phạm vi quét. `CLOSED` và `TBD` không đổi |
| `E0-12b-ratification-refs` | Mọi file `contracts/`, `acceptance/` khai `CONTRACT_READY` | file phải mang `ratification_ref` nêu `OD-20260907-01`, **và** `precode/owner-decisions.md` phải tồn tại và chứa id đó. Một trần claim được nâng dựa trên một trích dẫn không phân giải được là một claim không có thẩm quyền đứng sau |
| `E0-13-coverage-windows` | Fixture có `coverage_window` | `window_from < window_to`; `window_to[n] == window_from[n+1]` theo `sequence` |
| `E0-14-fixture-actor-edge` | `events[]` của mọi fixture | `actor` ∈ `caller_modules` VÀ `(actor, owner, operation)` ∈ `allowed_edges`; `performed_by` là service thực thi, **không** phải khẳng định caller; `edge_assertion: forbidden` đảo ngược kỳ vọng (R4-02); một sự kiện `operation: null` **phải** khai `event_type` ∈ {`local_observation`, `in_process_call`} |
| `E0-15-fixture-field-existence` | `given.rows` / `expected.rows` | mọi key là một cột của entity đó, HOẶC bắt đầu bằng `_`, HOẶC mang `pending_cr` (R4-01) |
| `E0-16-scenario-catalogue` | `acceptance/scenarios.yaml` | mỗi AC-01..18 có SC; mỗi mã lỗi có SC; id duy nhất và liên tục; mọi `fixture_refs`/`contract_refs` tồn tại trên đĩa; và mọi `status` hoặc là `NOT_RUN` hoặc là `PASS (E1)`/`PASS (E2)` **kèm bằng chứng**: `status_evidence_refs` không rỗng và mọi đường dẫn trong đó tồn tại trên đĩa, `status_scope_vi` không rỗng, và `evidence_level_required` không cao hơn cấp được khai. `PASS (E3)`/`PASS (E4)` bị từ chối thẳng — chưa lời gọi live nào và chưa kỳ review nội dung nào chạy. Đổi ở `PKT-PC09-P1`: vế cũ là lệnh cấm phẳng ("mọi status là NOT_RUN"), vế mới là **yêu cầu có bằng chứng**, vì bốn scenario thật sự đã chạy và được một auditor độc lập chạy lại |
| `E0-18-purge-set-agreement` | Ba tập bảng của `data.purge_all` trên tám artefact | `contracts/data/entities.yaml` `TXN-purge-all.tables` là **nguồn có thẩm quyền** (OD-20260907-01 mục 24). (a) Ba tập phải **rời nhau đôi một** và **phủ kín** `entities`: 37 + 21 + 2 = 60. (b) Không artefact nào trong cuộc hội thoại purge được còn gọi phạm vi là chưa quyết (`OWNER_DECISION_REQUIRED` / `PROV-PC00-01` / `PROV-PC01-03`) trừ khi dòng đó — hoặc dòng liền kề, vì YAML gấp dòng — đánh dấu **lịch sử** hoặc gọi tên phê chuẩn. (c) Một danh sách purge **có cấu trúc** ở artefact khác phải **bằng đúng** tập có thẩm quyền. Thêm ở FIX8 vì `F-A2R5-01`: sự vắng mặt của đúng check này là lý do quyết định có hậu quả lớn nhất của Owner được ghi vừa "đã chốt" vừa "còn treo" |
| `E0-17-declared-deviations` | `x-contract.deviations` và các ngoại lệ header | mỗi deviation có `rule`/`deviation`/`reason`/`evidence_refs`; ngoại lệ ADR (R-05) và ngoại lệ CSV được ghi ở nơi đọc được |
| `E0-19-generated-matches` | Hai manifest `GENERATED_FROM.json` (`shared/rr_contracts/rr_contracts/generated/`, `web/src/generated/`) | Mỗi manifest parse được, khai `generator` và một `sources` **không rỗng**, và mọi `sources[].path` tồn tại với `sha256` **bằng** hash của file trên đĩa hôm nay (và `bytes` khớp khi được khai). Đây là quy tắc "sinh, đừng sửa tay" của ADR-0011 ở dạng check tĩnh. Nó **KHÔNG** chứng minh đầu ra của bộ sinh đúng, và **KHÔNG** bắt được một file sinh bị sửa tay — chỉ chạy lại bộ sinh mới bắt được, và hai cửa đó (`pytest shared/rr_contracts/tests/test_generated_matches_contracts.py`, `node web/scripts/generate.mjs --check`) **vẫn ở nguyên**. `contracts/data/entities.yaml` **cố ý** không phải nguồn của bộ sinh nào (`CR-P0-06`, `F-A3R2-04`): hình dạng bảng đi vào code bằng tay qua Alembic và được canh bởi **pytest** `tests/contract/test_schema_matches_entities.py` — cổng schema sống trong pytest, không trong E0. Check in ra sự vắng mặt đó thành một note thay vì để người đọc suy ra |

## 4. Cách đếm — một phương pháp duy nhất

Ruling của Coordinator (đợt FIX4, mục 3) chốt một cách đếm để các con số trong handoff so được
với nhau:

> **Cột fixture:** một đơn vị cho mỗi lần xuất hiện của một key dưới `rows.<entity>[]`, đếm **một
> lần cho mỗi hàng**. Key bắt đầu bằng `_` là annotation và **không** được đếm (chúng được báo
> riêng ở `annotations_skipped`).

Nghĩa là: một fixture có hai hàng `work`, mỗi hàng năm key, đóng góp **10** vào `columns_checked`.
Cùng một tên cột xuất hiện ở hai hàng được đếm hai lần. Đây là lý do con số của một lần chạy độc
lập phải trùng với con số trong handoff — nếu lệch thì một trong hai đang đếm khác.

`E0-15` báo thêm một bảng theo từng thư mục fixture, gồm `files`, **`files_with_rows`**,
**`files_without_rows`**, `columns_checked`, `unresolved`, `annotations_skipped` và một `verdict`.
Hai cột `files_with/without_rows` được thêm theo ruling F-A2R1-08: cửa kiểm cột chỉ với tới file
dùng `rows[]`, và con số đó phải nằm trong đầu ra để lời khai trong `review.md` không thể lệch
khỏi phép đo.

**Chín thư mục fixture** nằm trong phạm vi của mọi cửa kiểm fixture (`E0-03`, `E0-13`, `E0-14`,
`E0-15`): `ai`, `boundary`, `collection`, `e2e`, `identity`, `recovery`, `reporting`, `telegram`,
`ui`. Ba thư mục `boundary/`, `e2e/`, `ui/` được thêm ở đợt FIX5 (ruling R5-02). Các cửa khớp theo
tiền tố `acceptance/fixtures/` nên một thư mục mới được nhận **tự động**; danh sách
`EXPECTED_FIXTURE_DIRS` trong `e0_check.py` tồn tại để một thư mục **biến mất** bị báo lỗi thay vì
được đếm là 0 — cùng nguyên tắc với `NOT_APPLICABLE_FREEFORM`: không bao giờ trình bày "không đo
được" như "sạch".

## 5. Giới hạn đã biết của chính công cụ này

1. **`NOT_APPLICABLE_FREEFORM` không phải là sạch.** Hai thư mục — `collection/` và `recovery/` —
   nêu oracle bằng văn xuôi (`durable_rows_expected`, `expected_target_state`) thay vì bằng
   `rows.<entity>[]`. `E0-15` **không chạm tới chúng**, nên chúng báo `columns_checked = 0` và
   `unresolved = 0`. Đọc `0 unresolved` ở đó là **sai**: đúng phải đọc là "check này không đo được
   thư mục này". Đó là lý do verdict của chúng là `NOT_APPLICABLE_FREEFORM` chứ không phải `PASS`.
2. **Kiểm tham chiếu bắt được tham chiếu treo, không bắt được tham chiếu thiếu.** Công cụ chứng
   minh rằng những gì đã viết đều phân giải được; nó không thể chứng minh rằng một quan hệ lẽ ra
   phải được viết đã được viết. Đây chính là kẽ hở đã để lọt `F-A1R2-01` và `F-A1R2-03` ở epoch 2.
3. **Không có validator OpenAPI 3.1.** Môi trường này không cài, và packet cấm cài thêm bất cứ
   thứ gì. `contracts/http/openapi.yaml` chỉ được kiểm như YAML cộng tính toàn vẹn tham chiếu —
   **không** kiểm tuân thủ đặc tả OpenAPI. Đừng suy ra tuân thủ từ một `PASS` ở đây.
4. **Nửa văn xuôi của `E0-12` là heuristic.** Nó bỏ qua dòng có dấu hiệu phủ định hoặc trích dẫn
   (`không`, `chưa`, `trước khi`, `được coi là`, backtick, ngoặc kép). Nó có thể báo thừa và có
   thể bỏ sót; mọi hit phải được người đọc. Nửa có cấu trúc thì chính xác.
5. **Ngữ nghĩa fixture được ĐỌC, không được THỰC THI.** Chỗ nào tính lại được (hash, cửa sổ
   coverage, schema) thì con số được kiểm; chỗ nào fixture khẳng định một transition hay một kết
   quả transaction thì công cụ chỉ kiểm tính nhất quán tham chiếu.
6. **`E0-09` biết trước tên enum trạng thái chính** của năm file `contracts/state/*.yaml` qua bảng
   `PRIMARY_STATE_ENUM`. Thêm một máy trạng thái mới mà quên thêm dòng vào bảng đó thì check
   **fail loudly** ("cannot identify the primary state enum"), không im lặng bỏ qua.
7. **`evidence/handoffs/` nằm ngoài phạm vi quét văn xuôi của `E0-06` và `E0-07`.** Ghi lại vì
   đây là một lựa chọn, không phải điều hiển nhiên. Handoff là **bản ghi bằng chứng**, không phải
   hợp đồng: chúng trích dẫn hợp lệ các range marker (`SC54+`, "PC05/PC06/PC07 take SC45+"), các ID
   sai dạng mà chính chúng đang **báo cáo** (`REQ-S8.4-01` trong `CR-PC03-01`), và ID của scenario
   mà một gói sau sẽ viết. Coi văn xuôi đó là citation sinh ra false positive không tương ứng với
   khiếm khuyết nào. Cái **vẫn được kiểm**: mọi trường có cấu trúc (`scenario_refs`,
   `requirement_refs`, `decision_refs`…) bên trong handoff vẫn đi qua lượt kiểm theo khóa, nên một
   citation treo trong bảng vẫn bị bắt. **Giá của quyết định:** một ID sai chỉ nằm trong câu văn
   của handoff sẽ không bị bắt.
8. **Công cụ này do người viết một phần corpus viết ra.** Nó là `SELF_VALIDATION`. Một check được
   thiết kế để chỉ nhìn nơi tác giả nghĩ tới; đó là lý do A1-R3 tìm ra `F-A1R3-01` bằng một
   checker rộng hơn checker của chính gói bị kiểm.

## 5b. Self-test âm — bằng chứng rằng một check thật sự bắt được lỗi

Một `PASS` chỉ đáng tin khi check bắt được lỗi mà nó tuyên bố bắt. Với ba check tham chiếu quan
trọng nhất, tôi chạy một **self-test âm** trên một bản sao corpus trong thư mục scratch (không bao
giờ trong repo): tiêm một khiếm khuyết đã biết, xác nhận check báo đúng nó, rồi xóa bản sao.

| Check | Đột biến đã tiêm | Kết quả |
| --- | --- | --- |
| `E0-04b` | `` `worker.claim_assignment` `` → `` `worker.grab_assignment` `` trong `state/run.yaml` | Bắt được, nêu đúng file và liệt kê các operation thật của domain |
| `E0-12` (M5) | `claim_ceiling: CONTRACT_READY` đặt vào `contracts/ai/tasks.yaml` — phạm vi **không** có trong allowlist | Bắt được |
| `E0-12b` (**M6b**) | `ratification_ref` **chuyển ra khỏi header**, để lại một dòng văn xuôi nhắc chuỗi đó, trong `contracts/state/storage.yaml` | Bắt được — **ở FIX7 thì KHÔNG**; xem §5g |
| `E0-12b` (M6c) | gỡ hẳn `ratification_ref` khỏi `contracts/state/report.yaml` | Bắt được |
| `E0-12` (M7) | một claim **vượt** `CONTRACT_READY` đặt vào `contracts/errors.yaml` | Bắt được |
| `E0-12` + `E0-12b` (**M8**, lượt riêng) | allowlist trong `precode/gates.yaml` không còn trích `OD-20260907-01` | **Cả hai chuyển `BLOCKED`**, không PASS |
| `E0-04c` | `` `saved_snapshot.content_hash` `` → `` `saved_snapshot.body_digest` `` trong `scenarios.yaml` | Bắt được, nêu đúng entity |
| `E0-04d` | `` `TELEGRAM_SEND_UNCERTAIN` `` → `` `TELEGRAM_TOTALLY_MADE_UP` `` trong `state/delivery.yaml` | Bắt được |
| `E0-10b` | ba đột biến: đổi `expected_error_code` của `NC-01`; `denied_case_ref` trỏ `NC-99`; đổi `actor` một sự kiện | Bắt cả ba |

**Một bài học từ chính lần chạy self-test đầu tiên.** Lần đầu tôi tiêm đột biến bằng một phép
`str.replace` **không kiểm** kết quả. Hai trong ba token đích không tồn tại ở dạng tôi giả định
(`IDENTITY_CONFLICT` không được đặt trong backtick ở `errors.yaml`), nên đột biến **không hề được
tiêm** — và check báo `PASS`. Một self-test không xác nhận rằng đột biến của nó đã landing thì
chứng minh **không gì cả**, và nó chứng minh không gì cả theo đúng cách trông giống như thành
công. Script self-test nay in ra từng lần tiêm và thoát khác 0 nếu một token đích vắng mặt.

Chọn đột biến ở namespace **không nhập nhằng**. `report.publish_immediately` là một đột biến tồi
để chứng minh `E0-04b`: `report` vừa là domain operation vừa là tên entity, nên token rơi vào
nhánh "cả hai" và được báo bởi `E0-04c`. `worker.*` không phải tên entity, nên nó chứng minh đúng
thứ cần chứng minh.

## 5g. `F-A2R5-03` — self-test của tôi thiếu đúng đột biến quan trọng nhất

Ở FIX7 tôi dựng `E0-12`/`E0-12b`, chạy ba đột biến, và báo "cả ba đều bị bắt". Auditor thử một
đột biến thứ tư: **M6b** — chuyển `ratification_ref` ra khỏi header và để lại một câu văn xuôi
nhắc chuỗi đó. Cả hai check **PASS**. Nguyên nhân: `ratification_ref_of()` có một regex dự phòng
quét toàn văn bản, nên file "có ref" theo nghĩa *chuỗi xuất hiện đâu đó*. Tệ hơn PASS: `E0-12b`
chỉ **đếm ít đi một mục** — file **rời khỏi tập được kiểm** thay vì bị báo, nên ngay cả người đọc
kỹ đầu ra cũng không thấy gì bất thường.

Bài học không phải "thêm M6b". Là: **một cửa kiểm mới chưa bị tấn công thì chưa phải bằng chứng**,
và người dựng cửa là người tệ nhất trong việc nghĩ ra cách phá nó. Ba đột biến tôi chọn ở FIX7 đều
là *xoá* hoặc *đặt sai chỗ*; không cái nào là *giữ nguyên bề mặt, đổi chỗ chứa* — đúng loại mà một
oracle "chuỗi có mặt" bỏ lọt. `CR-PC01-11` và `F-A2R1-05` trước đó cũng cùng lớp: **có mặt không
đủ, phải khớp**.

Nay: `ratification_ref` **chỉ** đọc từ header đã parse, không còn regex dự phòng; eligibility là
allowlist dữ liệu; và self-test chạy năm đột biến qua hai lượt.

## 5h. Điều `E0-18` KHÔNG kiểm

Bản đầu của `E0-18` so **tập hợp của các liệt kê trong văn xuôi** giữa các artefact. Nó cho 24 vi
phạm, khoảng 20 trong đó là **sai**: bất kỳ đoạn văn nào nhắc "purge" gần năm tên bảng đều dính,
và `entities.yaml` dính chỉ vì nó chứa mọi tên bảng. Tôi đã gỡ phần đó thay vì nới ngưỡng cho tới
khi nó im — một check ồn dạy người đọc bỏ qua đầu ra của chính nó, và đó là thiệt hại lâu dài hơn
một lỗ hổng đã được ghi ra.

Nên: **liệt kê purge trong văn xuôi chưa được đối chiếu tự động.** Cái được kiểm là toàn vẹn phân
hoạch, sự vắng mặt của marker "chưa quyết", và các danh sách **có cấu trúc**. Một artefact viết
sai một tên bảng giữa một câu văn vẫn lọt. Đó là một CR mở, không phải một điều bản này ngụ ý đã
xong.

## 5f. Phạm vi của `E0-12` — điều nó **không** với tới, đo và in ra

`SCAN_DIRS` là `contracts`, `acceptance`, `precode`, `evidence`. **`agent-tasks/` không nằm trong
đó.** Vì thế câu "nhãn vượt `CONTRACT_READY` bị cấm ở mọi nơi" từng đúng về ý định và sai về phạm
vi: 18 task card khai `claim_ceiling: IMPLEMENTATION_VERIFIED` (một card khai
`LIVE_FEASIBILITY_VERIFIED`) mà không check nào nhìn thấy.

Trong card, `claim_ceiling` mang **nghĩa khác**: trần mà công việc được giao có thể đạt tới, lấy
từ SRC-PLAN §2 — không phải một tuyên bố về chính card. Nên đây không phải một vi phạm cần fail.
Nhưng một khóa mang hai nghĩa là đúng lớp rủi ro mà mọi finding của audit trong gói này đã có, nên
xử lý là:

1. Oracle của `E0-12` nay nói **đúng phạm vi nó quét**, và nêu tên `agent-tasks/` là ngoài phạm vi.
2. `E0-12` **đếm và in ra** mọi `claim_ceiling` vượt trần trong `agent-tasks/` như một note trong
   bản ghi chạy — có mặt trong bằng chứng, không phải vắng mặt im lặng.
3. `CR-PC09-14` (→ Coordinator): hoặc đổi tên khóa trong card, hoặc mở rộng `SCAN_DIRS`. Tôi
   **không** tự mở rộng `SCAN_DIRS` ở đợt đóng gói: nó sẽ đổi nghĩa của mọi lần chạy trước đó và
   đưa một thư mục do gói khác sở hữu vào phạm vi mà không có ruling.

Đây là lần thứ hai trong gói này một check có **tiêu đề rộng hơn phép đo** (lần đầu: `E0-11b`,
`F-A2R1-10`). Cách sửa cả hai lần giống nhau — thu tiêu đề về đúng phép đo, rồi đo phần chênh và
in nó ra — và §5 nên được đọc với giả định rằng còn những chỗ như thế chưa ai tìm ra.

## 5i. `CR-P0-02` — `E0-12` từng dựa trên một mệnh đề nay đã sai

Oracle cũ của `E0-12` cấm **tuyệt đối** mọi nhãn trên `CONTRACT_READY` trong toàn bộ phạm vi quét,
và nêu lý do ngay trong chính oracle: *"no code exists, so nothing above it is establishable"*.
Mệnh đề đó đúng cho tới khi Giai đoạn 0/1 ship code mà một auditor độc lập chạy lại được.

Người viết `P0-skeleton-handoff.md` gặp hậu quả cụ thể của nó: để đi qua cửa, họ phải đặt trần
hoàn thành của mình vào một **bảng văn xuôi trong backtick** thay vì vào một trường có cấu trúc
của front-matter, vì trường có cấu trúc sẽ FAIL. Đó là một cách viết vòng để lách một cửa đã lỗi
thời — và một cửa buộc người trung thực phải viết vòng là một cửa đang dạy sai thói quen.

Quy tắc nay được **thu hẹp, không bị bỏ**:

| Ở đâu | `IMPLEMENTATION_VERIFIED` | `INTEGRATION_VERIFIED` và cao hơn |
| --- | --- | --- |
| `evidence/handoffs/**`, `evidence/runs/**` **có trích dẫn một báo cáo A3** | **được phép** | cấm |
| `evidence/handoffs/**`, `evidence/runs/**` **không** trích dẫn | cấm | cấm |
| `contracts/**`, `acceptance/**`, `precode/**` | cấm (không đổi) | cấm (không đổi) |

Trích dẫn là điều biến nhãn thành một **tham chiếu bằng chứng** thay vì một lời tự phong: một
Worker không được tự nâng trần của chính mình, và `evidence/manifest.schema.json` vẫn chặn một bản
ghi `SELF_VALIDATION` ở `CONTRACT_READY` — cái chặn đó **không** được nới, và nó chính là câu trả
lời cho `CR-TC-ingest-06` và `CR-TC-storage-02`.

**Độ mịn, nói ra thay vì để suy:** trích dẫn được kiểm **theo FILE**, không theo từng bản ghi. Một
handoff trích dẫn A3 ở đâu đó vì thế có thể mang nhãn trên một bản ghi mà báo cáo không phán tới.
`E0-12` in ra danh sách file đã dùng ngoại lệ này trong note của nó, để phạm vi thật của ngoại lệ
nằm trong bằng chứng chứ không nằm trong trí nhớ ai đó. Nghĩa vụ theo từng bản ghi do
`evidence/manifest.schema.json` và `precode/review.md` §14.3 gánh.

## 5k. `F-A3R3-01` — quy tắc nói nó canh một cây mà vòng lặp chưa bao giờ đọc

`A3-R3` tìm thấy đúng lớp lỗi mà §5f và §5h đã cảnh báo hai lần, lần này trong bản sửa của chính
tôi: oracle của `E0-12` viết rằng ngoại lệ `CR-P0-02` áp cho `evidence/handoffs/**` **và
`evidence/runs/**`**, nhưng `in_scope_for_refs()` loại `evidence/runs/` khỏi phạm vi (đúng theo
`F-A2R1-11`, để `files_scanned` tái lập được), và vòng lặp của `E0-12` bắt đầu bằng chính vị từ
đó. Auditor tiêm ba khiếm khuyết vào cây đó và cả ba **PASS**; `checked` thậm chí không nhúc nhích.

Auditor cũng tìm ra cái thứ hai, sâu hơn: `evidence/manifest.schema.json` chặn
`IMPLEMENTATION_VERIFIED` trên một bản ghi `SELF_VALIDATION` — cửa chặn thật sự — nhưng trên một
bản ghi **tự khai** `review_type: INDEPENDENT_AUDIT` nó chấp nhận **mọi** nhãn, tới tận nhãn cao
nhất. Nghĩa là ở đúng loại bản ghi dễ tự phong nhất, không cửa máy nào ràng buộc nhãn: không
`E0-12` (cây bị loại), không schema (trần bị nới).

Bản sửa ở `PKT-PC09-P1-FIX1`, hai phần:

1. **`E0-12` nay thật sự đọc cây đó.** `evidence/runs/**` được duyệt **riêng** trong chính check
   (hàm `run_record_files`), nên `files_scanned` **không đổi** và `F-A2R1-11` vẫn được tôn trọng;
   số file/trường đọc thêm được in ra trong một note. Ở cây này chỉ **trường có cấu trúc** được
   kiểm — kể cả `claim.supports_label`. Lý do phải nói ra: một báo cáo E0 **cũng là** một file
   trong `evidence/runs/`, và nó nhúng chính oracle này, vốn nêu tên mọi nhãn bị cấm; quét văn
   xuôi ở đó sẽ làm công cụ fail trên đầu ra của chính nó.
2. **Schema có trần theo loại review.** `x-maximum-claim-by-review-type` + hai nhánh `allOf` mới:
   `INDEPENDENT_AUDIT` tối đa `IMPLEMENTATION_VERIFIED`, `COORDINATOR_CHECK` tối đa
   `CONTRACT_READY`. Ba nhãn trên đó cần G6-X1 / SP1-X2 / G7, và chưa cổng nào mở.

**Một mở rộng vượt câu chữ của packet, khai ra thay vì làm lặng.** Packet bảo mở rộng sang
`evidence/runs/**`. Tôi mở sang **ba** vị trí, thêm `evidence/index.json`, vì index nhúng nguyên
văn từng bản ghi — một nhãn lọt vào đó là một nhãn trong một bản ghi, và trước đợt này
`supports_label` **không được kiểm ở file nào cả**. Đây vừa là siết chặt vừa là nới quyền, nên nó
là `CR-PC09-17` gửi Coordinator, không phải một quyết định của Worker.

**Một exemption mới, cũng được đếm.** `evidence/coordination/**` (packet, ruling, ledger) được
miễn khỏi **quét văn xuôi** nhãn: một packet hỏi "nhãn X có đứng được cho bốn card không?" đang
**trích** nhãn nó dispatch, giống hệt `claim_ceiling` trong một card `agent-tasks/`. Trường có
cấu trúc của chúng vẫn bị kiểm, và số lần trích được **đếm và in ra** trong note của `E0-12` —
cùng cách xử lý §5f đã dùng, vì cùng một rủi ro.

## 5j. Self-test âm cho ba quy tắc của `PKT-PC09-P1`

Cùng kỷ luật §5b: một quy tắc chưa ai thấy **cắn** là một quy tắc không nên tin. Script
`selftest_p1.py` (thư mục scratch của Worker) tiêm từng khiếm khuyết một vào một **bản sao** của
repo và khẳng định đúng check bắt được nó ở đúng đường dẫn. **11/11 CAUGHT**, gồm một *positive
control*:

| # | Tiêm gì | Check phải bắt |
| --- | --- | --- |
| N1 | `IMPLEMENTATION_VERIFIED` trần trụi trong một handoff **không** trích A3 | `E0-12` |
| N2 | `INTEGRATION_VERIFIED` trong một handoff **có** trích A3 | `E0-12` (ngoại lệ chỉ mở cho một nhãn) |
| N3 | `IMPLEMENTATION_VERIFIED` trong một file `contracts/` | `E0-12` (quy tắc cũ không đổi) |
| P1 | *(đối chứng dương)* handoff thật có trích A3 | `E0-12` **KHÔNG** được báo |
| N4 | `status: "PASS (E3)"` | `E0-16` (ngoài từ vựng) |
| N5 | scenario đòi E2 mà khai `PASS (E1)` | `E0-16` (không pass dưới cấp mình đòi) |
| N6 | `status_evidence_refs` trỏ file không tồn tại | `E0-16` |
| N7 | `status_scope_vi` bị làm rỗng | `E0-16` |
| N8 | thêm một byte vào một nguồn đã khai của bộ sinh | `E0-19` |
| N9 | xóa một `GENERATED_FROM.json` | `E0-19` |
| N10 | `GENERATED_FROM.json` với `sources: []` | `E0-19` (không được pass rỗng) |

### Bảng đột biến thứ hai — `PKT-PC09-P1-FIX1`, chính bảng của `A3-R3` đảo ngược

`selftest_fix1.py` chạy lại từng dòng auditor báo là "PASS khi lẽ ra phải FAIL", cộng hai đối
chứng và năm đột biến schema. **12/12 hành xử đúng đặc tả**:

| # | Đột biến | Kỳ vọng | Quan sát |
| --- | --- | --- | --- |
| — | repo không đột biến (đối chứng nền) | PASS | PASS, 0 vi phạm |
| 1 | `IMPLEMENTATION_VERIFIED` vào `precode/gates.yaml` | FAIL | FAIL, 1 vi phạm |
| 2 | `evidence/runs/*.json` `claim_ceiling` nhãn đó, **không** trích A3 | FAIL | FAIL |
| 3 | `evidence/runs/*.json` `claim.supports_label` nhãn đó, không trích | FAIL | FAIL |
| 4 | `evidence/runs/*.json` `INTEGRATION_VERIFIED`, **có** trích A3 | FAIL | FAIL |
| 5 | `evidence/runs/*.json` `IMPLEMENTATION_VERIFIED` **có** trích (đối chứng dương) | PASS | PASS |
| 6 | `evidence/index.json` bản ghi `supports_label` → `INTEGRATION_VERIFIED` | FAIL | FAIL |
| S1 | schema: `IMPLEMENTATION_VERIFIED` trên `INDEPENDENT_AUDIT` | ACCEPT | ACCEPT |
| S2 | schema: `INTEGRATION_VERIFIED` trên `INDEPENDENT_AUDIT` | REJECT | REJECT |
| S3 | schema: `PRODUCT_ACCEPTED` trên `INDEPENDENT_AUDIT` | REJECT | REJECT |
| S4 | schema: `IMPLEMENTATION_VERIFIED` trên `SELF_VALIDATION` | REJECT | REJECT |
| S5 | schema: `IMPLEMENTATION_VERIFIED` trên `COORDINATOR_CHECK` | REJECT | REJECT |

Dòng 5 và S1 là lý do bảng này có giá trị: một quy tắc chỉ biết từ chối, không biết cho qua
trường hợp hợp lệ, cũng vô dụng như một quy tắc không bắt được gì.

N10 và đối chứng P1 là hai ca đáng nói. N10 kiểm rằng một manifest **không khẳng định gì** bị coi
là hỏng thay vì được coi là sạch — cùng lớp lỗi với `items_checked: 0` mà `finalize()` canh. P1
kiểm chiều ngược lại: một quy tắc chỉ bắt được lỗi mà không cho phép trường hợp hợp lệ thì cũng
vô dụng như một quy tắc không bắt được gì.

## 5c. Cải tiến được khuyến nghị tiếp theo — `CR-PC07-10` (KHÔNG thực hiện ở đợt này)

W3 nêu một phản biện đúng về `E0-04b`/`E0-04c` và nó nên được ghi lại thay vì bị quên:

> Gate coi **mọi** token `a.b` là một khẳng định về operation hoặc cột. Nhiều tham chiếu hợp lệ
> không thuộc hai loại đó — đường mục lục, thuộc tính read model, trường của API bên ngoài, đường
> dẫn cấu trúc trong fixture. Việc viết lại chúng thành dạng không mơ hồ là **thích nghi với hình
> dạng của gate**, không phải sửa lỗi nội dung.

Đó là một chi phí thật và nó đã được trả một lần: một phần các sửa đổi ở đợt FIX7/FIX8 là đổi cách
viết chứ không phải sửa nội dung sai.

**Đề xuất của `CR-PC07-10`:** một danh mục **namespace được khai báo** cho tham chiếu trong prose,
ví dụ `` `schema:report.items[]` ``, `` `api:sendMessage.parse_mode` ``, `` `§9.2` `` — người viết
nói rõ mình đang trỏ vào đâu, và gate phân giải theo đúng danh mục đó thay vì đoán từ dấu chấm.

**Đánh đổi, cả hai chiều:**

| Được | Mất |
| --- | --- |
| Ý định được diễn đạt tường minh; hết false positive cho tham chiếu ngoài hợp đồng | Phải sửa **toàn bộ** prose hiện có một lần nữa — chi phí lớn hơn 8 token vừa sửa |
| Gate phân giải được nhiều loại tham chiếu hơn (schema pointer, API ngoài, mục lục), không chỉ hai | Thêm một quy ước mà mọi gói phải học và mọi người viết phải nhớ |
| Một tham chiếu tới API ngoài (Telegram) trở nên kiểm được thay vì bị bỏ qua | Prefix sai hoặc thiếu trở thành một lớp lỗi **mới**, và nó cần gate riêng |

**Vì sao không làm bây giờ:** nó chạm mọi file hợp đồng, ngay trước một freeze, để đổi *cách diễn
đạt* chứ không phải để sửa một khiếm khuyết đang tồn tại — `E0-04b/c/d` hiện 0 vi phạm. Thời điểm
đúng là **sau** khi A2 xác minh epoch này, và nên đi kèm một lần rà toàn corpus chứ không làm dần.
Ghi ở đây để lựa chọn "chưa làm" là một quyết định có lý do, không phải một chỗ bị bỏ sót.

## 5d. Quy tắc đọc epoch pin của card — lệnh công bố phải là lệnh được áp dụng

Card là **nguồn chuẩn** của tên epoch pin; mọi file khác khẳng định pin hiện hành phải đọc từ đó.
Nhưng dòng pin của mỗi card nêu **cả** epoch hiện hành **lẫn mọi epoch đã bị thay**, nên một lệnh
`grep` ngây thơ trả về bảy tên và không cho biết cái nào là hiện hành. Quy tắc đúng:

> Epoch hiện hành là token trong cặp backtick **đầu tiên** của dòng bắt đầu bằng `**Pin epoch: `.

Lệnh công bố — và là **chính lệnh bộ sinh áp dụng** (khóa `card_pin_command` trong
`numbers-<stamp>.json`):

```
sed -n 's/^\*\*Pin epoch: `\([A-Za-z0-9-]*\)`.*/\1/p' agent-tasks/TC-*.md | sort -u
```

Nó phải trả **đúng một** giá trị. Cổng tự kiểm của `review.md` **chạy lệnh này** và so kết quả với
`card_pin_current`; nếu lệnh công bố và quy tắc được áp dụng tách nhau ra thì cổng fail. Đó là
`F-A2R3-02`: trước đó lệnh in trong tài liệu trả bảy tên trong khi bộ sinh dùng một quy tắc chặt
hơn — "hãy chạy lệnh này thay vì tin bản chép" chỉ có giá trị khi lệnh thật sự trả lời được câu hỏi.

## 5e. Cổng tự kiểm của `review.md`

`gate.py` chạy sau **mỗi** lần sửa `review.md` và kiểm tám điều: bốn dòng tổng khớp bảng của chính
chúng (DoR, module, hai dòng E0), số AUDIT_REPORT khớp `audit_reports_count`, lệnh pin trả đúng
một giá trị bằng `card_pin_current`, **không còn placeholder định dạng chưa thay** ở bất kỳ đâu, và
**không có tên epoch cũ nào ngoài dòng lịch sử đã khai**.

Ba trong tám kiểm đó được thêm sau khi chúng bắt được lỗi thật:
- dòng tổng vs bảng — sau `F-A2R1-02` (bốn số headline sai), và nó bắt lại đúng lớp đó khi tôi sửa
  DoR dòng 5 mà quên dòng tổng;
- placeholder chưa thay — sau `F-A2R3-03`: **một dòng "được sinh" mà vẫn ship kèm placeholder thì
  chưa thật sự được sinh**, và không có gì phát hiện điều đó ngoài một lần đọc bằng mắt;
- epoch cũ ngoài dòng lịch sử — sau `F-A2R3-01`, khi cùng một dòng DoR sai epoch ở **ba** epoch
  liên tiếp dù có mang câu "đọc từ card, không chép tay". Một khẳng định provenance sai còn tệ hơn
  một giá trị cũ trần, vì nó bảo người đọc đừng kiểm.

## 6. Đầu ra

- **JSON** (`--json-out`): `summary` (pass/fail/blocked + tổng số vi phạm), `checks[]` với
  `check_id`, `oracle`, `status`, `items_checked`, `violations[]`, `declared_deviations[]`,
  `notes[]` và `detail` (bảng theo thư mục của `E0-15`), `baseline_hashes` (sha256 của mọi file
  dưới `contracts/` và `acceptance/` cộng hai nguồn, tại thời điểm chạy) và `limitations`.
- **Artefact provenance của `review.md`**: `derive_numbers.py` và `crtable.py` được chạy từ thư
  mục scratch, nhưng đầu ra của chúng được **sao vào `evidence/runs/`** kèm dấu thời gian của lần
  chạy (`numbers-<stamp>.json`, `cr_summary-<stamp>.json`) và được đăng ký làm artefact của
  `EV-PC09-01`. Lý do: `review.md` trích khóa của chúng ở ~30 chỗ, và một khóa provenance chỉ hữu
  ích khi thứ nó trỏ tới mở được **từ bên trong candidate đã đóng băng** (`F-A2R2-03`).
- **Tóm tắt cho người** ra stdout: một dòng mỗi check, tối đa 12 vi phạm đầu tiên, phần còn lại
  nằm trong JSON.

`baseline_hashes` là thứ khiến kết quả có thể ghim: một kết luận chỉ có hiệu lực với đúng những
byte đó. Đổi một file trong danh sách thì bản ghi bằng chứng tương ứng chuyển `STALE` theo quy tắc
của `precode/gates.yaml` §`invalidation_rules`.

## 7. Thêm một check

Thêm một hàm `check_*(repo, idx)`, gọi `new_check(id, title, oracle)` ở đầu, gọi `c.fail(...)` cho
từng vi phạm, rồi gọi hàm đó trong `main()`. Ba quy tắc:

1. **Đừng thu hẹp một check để nó pass.** Nếu một check báo đúng một vấn đề thật, cách xử lý là
   một change request, không phải một điều kiện lọc thêm.
2. **Đừng ghi một vi phạm quy tắc thành `note`.** Note là để đo lường và ngữ cảnh (bảng theo thư
   mục, deviation đã khai, mục `NOT_APPLICABLE` có lý do). Nếu một quy tắc trong hợp đồng nói
   "phải", thì cửa kiểm trích quy tắc đó phải `fail`. `F-A2R2-04` tồn tại vì `E0-10b` ghi "5 trên
   6 case thiếu `event_type`" thành note trong khi vẫn báo `violations: 0` — và không ai phải làm
   gì với một note.
3. **Một check kiểm 0 mục sẽ tự chuyển thành `BLOCKED`, không phải `PASS`.** `Check.finalize()`
   ép điều này. Nó tồn tại vì `E0-10a` đã âm thầm tụt xuống `items_checked: 0` mà vẫn báo `PASS`
   khi vòng lặp của nó bị mất trong một lần sửa `E0-10b` — đúng lớp lỗi "0 kiểm được đọc thành
   sạch" mà chính tài liệu này cảnh báo ở chỗ khác. Dùng `exempt_from_zero_guard` chỉ khi đối
   tượng của check có thể rỗng một cách hợp lệ.
4. **Đừng im lặng bỏ qua.** Nếu một check không hiểu một hình dạng dữ liệu, nó phải `fail` hoặc
   ghi `note` — không được đếm là 0 và báo sạch. `F-A1R3-02` tồn tại vì một gate im lặng bỏ qua
   cả một thư mục.
5. **Ghi oracle bằng chữ.** Trường `oracle` được in ra và được sao vào `evidence/index.json`; nó
   là thứ người đọc dùng để biết `PASS` nghĩa là gì.


---

## 8. `verify_cards.py` — cửa pin của 18 task card

Công cụ thứ hai trong thư mục này. Nó **không** thuộc `e0_check.py`; nó là dạng chạy được của
`EV-PC10-01`, phép kiểm mà PC10 vốn chỉ chạy bằng một script trong thư mục scratch. Job `e0`
chạy cả hai (`.github/workflows/e0.yml`).

```
PYTHONDONTWRITEBYTECODE=1 uv run python evidence/tools/verify_cards.py \
    --repo . --json-out "$RUNNER_TEMP/cards.json"
```

Cờ: `--only <id,id>` chạy một tập con; `--json` in báo cáo ra stdout (`--json-out` ghi ra file);
`--self-test` chạy self-test âm ở §8.2; `--self-test-dir` chỉ định thư mục scratch cho nó (mặc
định là một thư mục tạm, và **không bao giờ** được nằm trong repo — công cụ từ chối).

Thoát 0 chỉ khi **mọi** check `PASS`. `FAIL` và `BLOCKED` đều thoát 1; 2 là công cụ không chạy
được. Một check đọc 0 mục tự chuyển `BLOCKED` — cùng quy tắc §7.3 ở trên, vì cùng một lý do.

### 8.1 Mười ba check — bằng đúng oracle của `EV-PC10-01`

Tới `PKT-PC10-FIX15` bản port này chỉ chạy **chín** check; bốn check còn lại sống trong script
scratch của PC10 và sẽ biến mất cùng thư mục đó. `CR-PC10-10` ghi lại khoảng trống ấy, và
`PKT-PC10-FIX16` đóng nó. Nay hai bản **bằng nhau**.

| Check | Oracle | Nguồn |
| --- | --- | --- |
| `pins` (a) | mọi sha256 + byte count ở §0 khớp file trên đĩa | `INV-06` |
| `epoch` (k) | 18 card đồng thuận **một** epoch, **và** bốn file khẳng định pin hiện hành (`precode/README.md`, `agent-tasks/README.md`, `TEMPLATE.md`, `WALKTHROUGH.md`) nêu đúng epoch đó; epoch cũ chỉ được xuất hiện trong đoạn văn có dấu hiệu kể lịch sử | `F-A2R1-03` |
| `paths` (b) | mọi đường dẫn tài liệu card trích dẫn đều tồn tại | — |
| `operations` (c) | mọi operation ID ở §4 có trong `contracts/ports.yaml` | — |
| `scenarios` (d) | mọi `SC..` giải được trong `acceptance/scenarios.yaml` | — |
| `errors` (e) | mọi mã ở §7 có trong `contracts/errors.yaml` | — |
| `modules` (f) | mọi `MOD-*` có trong `contracts/modules.yaml` | — |
| `invariants` (g) | mọi `I<nn>` có trong sổ bất biến | — |
| **`obligations` (h)** | mọi card mang `SC49`, bảng ranh giới R5-01 ở §5 (`UNAUTHORIZED`, `FORBIDDEN_EDGE`, `CAPABILITY_DENIED`, `CSRF_REJECTED`) và fixture default-deny | ruling R5-01 |
| **`claim_labels` (i)** | nhãn claim chỉ lấy từ SRC-PLAN §2 | SRC-PLAN §2 |
| **`pc09_unpinned` (j)** | sáu file PC09 + `e0_check.py` **không** được pin hash ở §0 | ruling về `CR-PC10-01` |
| **`stack` (l)** | không card nào trình bày Stack A như stack được chọn; mọi card nêu Option B và trích `OD-20260907-01` | `OD-20260907-01` |
| `layout` (m) | luật hai ngôn ngữ của `agent-tasks/README.md` §5.3 — kiểm **cả** trên chữ của card **và** trên file thật trên đĩa | §5.3 |

Bốn check mới không phải trang trí. `(j)` là thứ ngăn một lần pin "cho đủ" biến sáu file mà card
được lệnh **đọc bản mới nhất** thành sáu file làm card `STALE`. `(k)` bản đầy đủ đã bắt lỗi thật
**hai lần** (`F-A2R1-03`, và `PKT-PC10-FIX14` §N.3 — nơi một script cập nhật prose chạy sai thư
mục làm việc, để 18 card ở epoch mới còn bốn file điểm vào ở epoch cũ).

### 8.2 Self-test âm — `--self-test`

Cùng nguyên tắc §5b: một `PASS` chỉ đáng tin khi check bắt được lỗi mà nó tuyên bố bắt. Công cụ
dựng một **shadow tree** trong thư mục scratch — `agent-tasks/` và `precode/` được **sao thật**,
mọi thứ khác ở gốc repo là **symlink**, nên cái bóng tốn vài trăm KB chứ không phải một checkout
— rồi tiêm đúng **một** khiếm khuyết cho mỗi check và đòi check sở hữu nó phải báo:

| Check | Đột biến |
| --- | --- |
| `pins` | đổi một sha256 đã pin thành `000…` |
| `epoch` | (1) một card bị pin lại **một mình** sang epoch khác; (2) `agent-tasks/README.md` bị bỏ lại ở một epoch đã bị thay |
| `paths` | card trích một hợp đồng không tồn tại |
| `operations` | §4 nêu `bogus.operation_id` |
| `scenarios` | card trích `SC97` |
| `errors` | §7 nêu `NOT_A_REGISTERED_CODE` |
| `modules` | card nêu `MOD-not-a-real-module` |
| `invariants` | card trích `I97` |
| `obligations` | gỡ `SC49` và đổi tên `CSRF_REJECTED` **ở mọi chỗ** |
| `claim_labels` | card tự đặt nhãn `PRODUCTION_VERIFIED` |
| `pc09_unpinned` | card pin `acceptance/scenarios.yaml` bằng hash |
| `stack` | card trình bày `Option A` không kèm dấu hiệu bị thay |
| `layout` | card đặt `web/src/lib/handler.py` |

Hai điều kiện làm self-test này khác một self-test trang trí:

1. **Mọi lần tiêm đều được xác nhận đã landing.** `_mutate()` thoát khác 0 nếu chuỗi đích vắng
   mặt. §5b ghi lại chuyện gì xảy ra khi không có điều này: đột biến không landing, check báo
   `PASS`, và self-test chứng minh **không gì cả** theo đúng cách trông giống thành công.
2. **So sánh theo số vi phạm, không theo trạng thái.** Baseline được đo **cho từng check** trên
   cái bóng sạch; một đột biến được tính là "CAUGHT" khi nó làm **tăng** số vi phạm. Nhờ vậy
   self-test vẫn chứng minh được `pins` cắn ngay cả khi cây thật đang có pin lệch — một điều
   kiện "phải sạch trước đã" sẽ tắt self-test đúng lúc cần nó nhất. Khi baseline không sạch,
   đầu ra nói thẳng điều đó và nhắc rằng self-test **không** nói repo đang PASS.

Thoát 0 chỉ khi **mọi** đột biến bị bắt. Cái bóng bị xóa sau khi chạy; không byte nào được ghi
vào repo.

### 8.3 Điều công cụ này KHÔNG chứng minh

Nó đọc lại **khai báo**, không đọc **nghĩa**. Một card có thể qua cả mười ba check và vẫn giao
sai việc. `pins` `PASS` chỉ nói byte hôm nay khớp byte đã pin — không nói hợp đồng đúng. Mọi kết
quả là `SELF_VALIDATION` theo SRC-PLAN §11.
