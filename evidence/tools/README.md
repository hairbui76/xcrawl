---
contract_id: CT-evidence-tools
version: 0.1.0
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
  - "python3 ≥ 3.10, PyYAML, jsonschema"
scope: >
  Bộ công cụ kiểm tra tĩnh (E0) cho baseline hợp đồng Pre-code. Một file duy nhất,
  `e0_check.py`, chạy 19 check và xuất một báo cáo JSON máy đọc được cộng một bản tóm tắt cho
  người. Đây là tài liệu sử dụng, giới hạn và cách đếm của nó.
verification: "Bản thân công cụ là phương tiện verification; kết quả của nó là SELF_VALIDATION."
claim_ceiling: DRAFT_FOR_REVIEW
---

# E0 static checks

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

## 3. Mười chín check

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
| `E0-12-forbidden-strings` | Toàn corpus | trường có cấu trúc: `status`/`claim_ceiling`/… không bao giờ là `CLOSED`, `ACCEPTED`, `TBD`, và không nhãn nào vượt `DRAFT_FOR_REVIEW`. Văn xuôi: báo dòng để người đọc (heuristic, xem §5) |
| `E0-13-coverage-windows` | Fixture có `coverage_window` | `window_from < window_to`; `window_to[n] == window_from[n+1]` theo `sequence` |
| `E0-14-fixture-actor-edge` | `events[]` của mọi fixture | `actor` ∈ `caller_modules` VÀ `(actor, owner, operation)` ∈ `allowed_edges`; `performed_by` là service thực thi, **không** phải khẳng định caller; `edge_assertion: forbidden` đảo ngược kỳ vọng (R4-02); một sự kiện `operation: null` **phải** khai `event_type` ∈ {`local_observation`, `in_process_call`} |
| `E0-15-fixture-field-existence` | `given.rows` / `expected.rows` | mọi key là một cột của entity đó, HOẶC bắt đầu bằng `_`, HOẶC mang `pending_cr` (R4-01) |
| `E0-16-scenario-catalogue` | `acceptance/scenarios.yaml` | mỗi AC-01..18 có SC; mỗi mã lỗi có SC; id duy nhất và liên tục; mọi `fixture_refs`/`contract_refs` tồn tại trên đĩa; mọi `status` là `NOT_RUN` |
| `E0-17-declared-deviations` | `x-contract.deviations` và các ngoại lệ header | mỗi deviation có `rule`/`deviation`/`reason`/`evidence_refs`; ngoại lệ ADR (R-05) và ngoại lệ CSV được ghi ở nơi đọc được |

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
