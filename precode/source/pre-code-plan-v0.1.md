# Research Radar — Kế hoạch Pre-code và bộ hợp đồng kiểm toán

Ngày: **06/09/2026** · Phiên bản kế hoạch: **0.1**

**Mục tiêu:** tạo một bộ hợp đồng đủ cụ thể để agent biết phải xây gì, chỉ được giao tiếp qua đâu, phải phục hồi về trạng thái nào khi lỗi và phải xuất trình bằng chứng gì trước khi tuyên bố hoàn thành.

**Phạm vi của file này:** kế hoạch thực hiện Pre-code, có danh mục hợp đồng, mẫu cấu trúc, các quyết định cần chốt và cổng kiểm tra. Các file hợp đồng, schema, fixture và bằng chứng được liệt kê bên dưới là **đầu ra cần tạo khi thực hiện kế hoạch**, chưa được tạo hoặc kiểm chứng chỉ bằng việc viết tài liệu này. Không có production code hay thử nghiệm collector nào được thực hiện trong bước này.

**Trạng thái hiện tại: `NOT_READY_FOR_PRODUCT_CODE`.** Không đồng nghĩa mọi công việc phải dừng: chuẩn hóa yêu cầu, soạn hợp đồng, tạo fixture và lập giao thức thử nghiệm vẫn tiến hành được. Mỗi module chỉ được chuyển sang coding khi đủ điều kiện đầu vào của chính nó.

> **Dành cho agent thực hiện:** đọc đặc tả nguồn và kế hoạch này; làm theo từng gói PC bên dưới. Không dùng một task card để tự thay đổi hợp đồng chung. Nếu có Superpowers, dùng `executing-plans` khi được yêu cầu thực hiện; kế hoạch không tự yêu cầu hoặc cho phép chạy nhiều agent song song. Chưa triển khai sản phẩm ở giai đoạn soạn hợp đồng.

## 1. Baseline và thứ tự ưu tiên

Nguồn chuẩn là **`research-radar-spec(1).md`, v0.2, ngày 05/09/2026**, do người dùng đính kèm. Trong workspace hiện tại: `upload/research-radar-spec(1).md`.

SHA-256 của bản đã đọc:

```text
d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26
```

Thứ tự áp dụng: quyết định mới được người dùng xác nhận → amendment/ADR đã chấp nhận → đặc tả v0.2 → hợp đồng đã đóng phiên bản → task card. Một hợp đồng không được âm thầm sửa đặc tả để làm test dễ pass.

- Giữ phân biệt **XN** đã xác nhận, **UQ** được ủy quyền, **ĐX** đề xuất, **KC** cần kiểm chứng.
- Các sửa đổi được khuyên trong kế hoạch này mang nhãn **PC-ĐX**, chưa thay thế quyết định của đặc tả.
- Không dùng overview cũ để đảo lại các quyết định mới: MVP đã là **một người dùng**, server ở ngoài, collector trên máy cá nhân, có cả **API key và CLI/ACP**, embedding local và Saved snapshot.
- Stack ứng dụng chưa chốt. Hợp đồng nghiệp vụ và schema wire cần độc lập framework; SQLite, Chrome và các ràng buộc đã xác nhận vẫn giữ.
- Ghi baseline bằng hash/phiên bản; nếu sau này có repo thì thêm commit. Không yêu cầu một commit tưởng tượng cho tài liệu chưa nằm trong repo.

## 2. Hình dạng bộ hợp đồng cần đạt

Một yêu cầu có thể kiểm toán phải nối được chuỗi:

**Yêu cầu nguồn → quyết định → invariant → hợp đồng/module → scenario có oracle → bằng chứng → verdict.**

“Oracle” là kết quả mong đợi độc lập để xác định đúng/sai, ví dụ số hàng phải tồn tại, trạng thái chính xác, thông điệp không được gửi. Log đẹp hoặc câu trả lời của agent không phải oracle.

Mỗi kết luận phải phân biệt:

| Nhãn | Được phép tuyên bố khi |
| --- | --- |
| `CONTRACT_READY` | Hợp đồng đủ trường, không còn quyết định chặn, ví dụ hợp lệ và bất hợp lệ được kiểm tra |
| `IMPLEMENTATION_VERIFIED` | Có code và test đúng baseline, bao gồm lỗi và hành vi bị cấm |
| `INTEGRATION_VERIFIED` | Consumer và producer thực tế trao đổi đúng hợp đồng trong môi trường tích hợp |
| `LIVE_FEASIBILITY_VERIFIED` | Thử nghiệm thật có môi trường, mẫu thử, giới hạn và kết quả được ghi lại |
| `PRODUCT_ACCEPTED` | Đạt tiêu chí sản phẩm trên dữ liệu thực tế và được người dùng đánh giá |

Không nâng cấp nhãn bằng suy diễn: mock pass không chứng minh X chạy thật; schema JSON hợp lệ không chứng minh summary đúng; unit test không chứng minh Telegram đã nhận tin.

## 3. Audit đặc tả: các quyết định phải đóng trước khi đóng hợp đồng

Tất cả mục dưới đây bắt đầu ở trạng thái **OPEN**. Người thực hiện chuẩn bị phương án và bằng chứng; chỉ đưa người dùng quyết định những điểm thay đổi hành vi hoặc đánh đổi đã cam kết. Chi tiết thuần kỹ thuật có thể được chốt trong phạm vi ủy quyền, phải ghi lại căn cứ.

| ID | Điểm chưa đóng và nguồn | PC-ĐX / quyết định cần có | Chặn gói nào |
| --- | --- | --- | --- |
| B01 | C03/D-tag dùng cả “thời điểm gửi” và “lúc tạo”; tag có thể đổi khi Telegram đang retry | Chọn một thời điểm chốt: khuyên dùng transaction publish report; ghi `tag_config_version` bất biến. Nếu thật sự theo lúc gửi, phải thiết kế revision và xử lý đã gửi một phần | PC04, PC07 |
| B02 | §5.2 dùng `delivered` trong run, §9 tách delivery; `stopped_limit` vừa là điểm dừng vừa có thể tạo report | Tách phase/status/outcome của run; delivery độc lập. Ánh xạ rõ tên cũ sang trạng thái chuẩn | PC03 |
| B03 | AC-14 hứa retry không có tin trùng; một hàng delivery không giải quyết mất phản hồi sau khi phía Telegram đã nhận | Thêm `delivery.unknown`; dừng retry tự động khi không biết đã gửi chưa. Thay bảo đảm tuyệt đối bằng chính sách có thể kiểm chứng, cần người dùng duyệt amendment | PC07 |
| B04 | D27 kỳ nối liền; D57 không report rỗng; AI backlog nằm ngoài kỳ đã đóng | Dùng sổ coverage độc lập report hiển thị; pending item và backfill ledger độc lập con trỏ kỳ. Chốt khi nào coverage tiến | PC04 |
| B05 | §9 “không lấy lại bài” nhưng cursor của feed động chưa chứng minh ổn định | Cam kết ingest không trùng; việc đọc lại có thể cần thiết. Checkpoint chỉ chứa dữ liệu server đã ACK; ghi rõ giới hạn bao phủ X | PC03, PC05 |
| B06 | `work` có DOI/arXiv unique nhưng hai bản ghi đã tồn tại rồi mới biết cùng công trình; post-only chưa có model analysis rõ | Chốt identity/alias merge, work version và target phân biệt work/post. Không coi hai UNIQUE là đủ giải mọi trùng lặp | PC02 |
| B07 | D25 “một lần”, D26 có phân tích lại; summary theo work nhưng schema không đủ source fingerprint/task key | Định nghĩa một kết quả hợp lệ mỗi target/version/task/input/prompt contract; reanalysis có generation mới. Attempt lỗi không tính là kết quả hoàn thành | PC02, PC06 |
| B08 | D56 “timezone máy chạy app” mơ hồ vì browser, server, máy collector khác nhau | Lưu một IANA timezone do owner xác nhận; timestamps chuẩn UTC; chốt quy tắc DST và gộp lịch | PC03, PC04 |
| B09 | §11.3 bỏ im lặng chat chưa liên kết nhưng §5.1 cần nhận mã từ chat chưa liên kết | Chốt ngoại lệ hẹp cho yêu cầu liên kết hợp lệ, kiểm mã trước; mọi lệnh khác từ chat lạ bỏ im lặng | PC07 |
| B10 | §5.4 nói status/run-now có thể tiếp tục; §9 nói chỉ resume sau xác minh | `status` không mutation; `run-now` không vượt `needs_user`. Khuyên nút resume riêng trong app; không tự thêm lệnh Telegram thứ tư | PC03, PC07 |
| B11 | Backup = copy SQLite; không nói DB đang ghi/WAL hoặc khôi phục queue/token | Chọn backup nhất quán và restore drill có khóa side effect. Không dùng copy file DB đang hoạt động làm bằng chứng đủ | PC08 |
| B12 | D09 profile riêng, D08/D42/D50 bố trí module còn ĐX; sơ đồ cho collector đưa dữ liệu thẳng analysis | Chốt profile và topology. Khuyên analysis nhận task từ server sau ingest commit, không nhận dữ liệu chưa commit từ collector | PC01, PC05, PC06 |
| B13 | Có API/CLI/ACP nhưng chưa chốt capability, phạm vi key được gửi worker, quyền tool của CLI | Chốt secret access theo task; CLI không tool/file/network action ngoài inference được phép; nếu adapter không cô lập được thì không bật | PC01, PC06, PC08 |
| B14 | D53 vector density là ĐX trong P0; chưa có thuật toán, cửa sổ, ngưỡng, sample tối thiểu | Định nghĩa phép đo và tập đánh giá. Thiếu dữ liệu → insufficient evidence, không tự gọi là “hướng nổi” | PC04, PC09 |
| B15 | D17/D29/AC-07 mong 0 trùng; metadata có thể thiếu hoặc mâu thuẫn | Chốt phạm vi invariant 0 trùng theo canonical identity đã biết; xung đột đưa `identity_conflict` và giữ nguồn, không merge đoán | PC02, PC09 |
| B16 | D20 điểm khác với cái đã có; có thể chỉ có một post; AC-11 gộp mọi tính mới thành suy luận | Phân biệt tuyên bố tính mới của tác giả và suy luận AI; thiếu nguồn so sánh thì ghi thiếu, không bịa baseline | PC06 |
| B17 | Summary “mọi mục”, §10 chỉ summary mục vào report; tag có thể đổi và chọn thêm target chưa có summary | Chốt lúc enqueue summary và cách report partial/pending; không báo completed nếu các mục còn thiếu bị mất khỏi hàng đợi | PC04, PC06 |

### 3.1 Hai amendment cần xử lý đặc biệt

**Telegram:** tài liệu `sendMessage` mô tả kết quả Message khi thành công nhưng không có trường idempotency key do client cung cấp trong danh sách tham số. Từ đó, kế hoạch không coi lưu UNIQUE ở DB là bằng chứng cho exactly-once ở mạng ngoài. Nếu request có thể đã đến Telegram nhưng phản hồi mất, trạng thái phải thể hiện sự không chắc chắn. [Telegram Bot API](https://core.telegram.org/bots/api#sendmessage).

**SQLite:** WAL là một phần trạng thái bền của DB; tách file DB khỏi WAL có thể mất transaction đã commit. Kế hoạch yêu cầu Online Backup API hoặc phương thức snapshot nhất quán đã kiểm chứng, rồi thử restore. [SQLite WAL](https://www.sqlite.org/wal.html), [SQLite Backup API](https://www.sqlite.org/backup.html).

Đây là phát hiện cần sửa hợp đồng, không phải lý do để âm thầm bỏ yêu cầu của người dùng. Từng amendment phải ghi điều gì thay đổi, vì sao, điều được bảo đảm thay thế và test nào chứng minh.

## 4. Danh mục file đầu ra của Pre-code

Các đường dẫn dưới đây là **đích trong repository tương lai**. Không phải danh sách file đã tồn tại.

| Nhóm | File cần tạo | Trách nhiệm |
| --- | --- | --- |
| Baseline | `precode/README.md`, `precode/baseline.json`, `precode/source/spec-v0.2.md` | Điểm bắt đầu, bản nguồn bất biến, hash và phạm vi |
| Yêu cầu | `precode/requirements.csv`, `precode/decision-register.md`, `precode/adr/` | Registry nguyên tử, B01–B17, amendments và trạng thái |
| Quyền giao tiếp | `contracts/modules.yaml`, `contracts/capabilities.yaml` | Module owner, port, caller/callee, denied edge, secret/network scope |
| API | `contracts/http/openapi.yaml`, `contracts/ports.yaml` | Wire HTTP và port trong tiến trình; chọn/pin phiên bản định dạng |
| Payload | `contracts/schemas/` | JSON Schema cho request/result/event/error; schema chỉ ở một nguồn chuẩn |
| Trạng thái | `contracts/state/run.yaml`, `contracts/state/analysis.yaml`, `contracts/state/report.yaml`, `contracts/state/delivery.yaml`, `contracts/state/storage.yaml` | Enum, transition, guard, commit, effect và resume |
| Lỗi | `contracts/errors.yaml`, `contracts/retry-policy.yaml` | Mã lỗi có kiểu, phạm vi retry, budget, terminal/recoverable |
| Dữ liệu | `contracts/data/entities.yaml`, `contracts/data/invariants.md`, `contracts/data/identity.md` | Target identity, ownership, transaction, migration |
| Thời gian | `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md` | Coverage, tag snapshot, backfill, no-reannounce, pending |
| AI | `contracts/ai/tasks.yaml`, `contracts/ai/providers.yaml`, `contracts/ai/grounding.md` | Task-specific schema, capabilities, evidence level, version, tool restriction |
| UI/Telegram | `contracts/ui/screens.yaml`, `contracts/telegram/commands.yaml`, `contracts/telegram/delivery.md` | Read model, action map, linking, Save và rendering |
| Vận hành | `contracts/ops/deployment.md`, `contracts/ops/secrets.md`, `contracts/ops/backup-restore.md` | Nơi chạy, readiness, secret lifecycle, restore |
| Fixture và scenario | `acceptance/scenarios.yaml`, `acceptance/fixtures/`, `acceptance/traceability.csv` | Dữ liệu vào, oracle, AC, invariant và error coverage |
| Giao việc | `agent-tasks/`, `agent-tasks/TEMPLATE.md` | Phạm vi thay đổi, contracts đọc/ghi, bằng chứng và điểm dừng |
| Bằng chứng | `evidence/manifest.schema.json`, `evidence/index.json`, `evidence/runs/` | Mô hình bằng chứng và kết quả thực tế khi có |
| Cổng kiểm tra | `precode/gates.yaml`, `precode/change-control.md`, `precode/review.md` | Điều kiện pass/fail, invalidation và báo cáo audit |

Một file hợp đồng phải có ID ổn định, version, status, owner theo vai trò, nguồn yêu cầu, consumers/producers, dependencies, phạm vi và phương pháp kiểm chứng. Owner là trách nhiệm trong quy trình, không phải lời khẳng định đã có một người khác review.

## 5. Mẫu hợp đồng: những trường bắt buộc

| Trường | Phải đủ rõ đến mức nào |
| --- | --- |
| `contract_id`, `version`, `status` | ID ổn định; draft/accepted/deprecated; không dùng “latest” |
| `source_refs`, `invariant_refs`, `decision_refs` | Truy ngược được về §/D/AC và amendment |
| `owner`, `producer`, `consumers` | Ai sở hữu nghiệp vụ, ai gọi, ai trả; một owner cho một mutation |
| `operation_id`, `transport`, `auth_scope` | Tên operation dùng chung; HTTP hoặc internal port; quyền tối thiểu |
| `request_schema`, `response_schema` | Kiểu, enum, nullability, trường bắt buộc, giới hạn size, encoding, thời gian |
| `preconditions`, `postconditions` | Trước/sau phải đúng điều gì; có điều kiện cấm cụ thể |
| `idempotency`, `concurrency` | Key, phạm vi, payload hash, conflict và stale writer |
| `transaction`, `commit_point` | Những hàng nào cùng commit; ACK chỉ sau điểm nào |
| `state_transitions`, `error_map` | Mỗi lỗi đưa thành phần nào về trạng thái nào; phần nào giữ nguyên |
| `timeouts`, `retry_policy` | Deadline, số attempt, ai retry, khi nào không retry; giá trị phải đóng trước Ready |
| `observability`, `redaction` | Event/log/metric cần có, correlation và những gì bị cấm ghi |
| `compatibility` | Request/schema version lệch xử lý ra sao; migration và consumer impact |
| `examples`, `scenario_refs` | Tối thiểu happy, invalid, unauthorized, duplicate, timeout/stale nếu áp dụng |
| `completion_evidence` | Test ID, artifact và oracle cần có để chấp nhận implementation |

Không dùng “xử lý lỗi phù hợp”, “retry khi cần”, “JSON đúng schema” làm toàn bộ hợp đồng. Phải biết chính xác schema nào và lỗi nào.

### 5.1 Quy tắc wire chung đề xuất

- ID truyền dưới dạng string; timestamp UTC RFC 3339; lịch có IANA timezone riêng. Phải chốt độ chính xác timestamp và tie-break bằng ingest sequence trước PC04.
- Mutation từ worker có `request_id`, `schema_version`, `idempotency_key`, `payload_hash`; mutation đang giữ job có thêm `job_id`, `lease_id`, `lease_epoch`.
- Cùng idempotency key + cùng payload trả lại receipt đã commit; cùng key + payload khác trả `IDEMPOTENCY_CONFLICT`, không ghi đè.
- Lease cũ trả `STALE_LEASE`, không làm thay đổi dữ liệu authoritative.
- Error envelope gồm `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có; không lộ transcript/key/cookie.
- Timeout transport là **không biết kết quả**, không mặc định là rollback. Trước retry mutation phải tra receipt hoặc replay theo hợp đồng idempotent.
- Network call không nằm trong transaction SQLite dài. External side effect dùng intent/outbox đã commit và receipt sau đó; không giả định transaction DB bao phủ dịch vụ ngoài.

## 6. Ranh giới module và giao tiếp được phép

Topology sau là PC-ĐX để đóng D08/D42/D50. Có thể triển khai modular monolith ở server; bảng là ranh giới quyền và ownership, không bắt buộc microservices.

| Caller | Callee/port được phép | Mục đích | Đường bị cấm |
| --- | --- | --- | --- |
| Web UI | Backend owner API | Xem/sửa Settings, tag, Save, run commands | SQLite trực tiếp; worker debug port; gọi Telegram/AI bằng secrets |
| Scheduler | Job service | Tạo/gộp lịch đến hạn | Gọi Chrome, gửi digest, đánh dấu report đã giao |
| Local collector | Worker API; project Chrome profile | Claim/heartbeat/ingest/checkpoint; đọc X | SQLite server; Telegram; secret AI; queue analysis trực tiếp |
| Local analysis worker | Analysis API; AI adapter | Claim input đã commit; submit kết quả theo schema | Sửa tag/report/Saved; tự publish hoặc lấy toàn bộ secrets |
| AI adapter | Provider đã cấu hình hoặc CLI/ACP được kiểm chứng | Inference cho task được cấp | Browser X; SQLite; Telegram; tool tùy ý từ nội dung nguồn |
| Research connector | API arXiv/OpenAlex được duyệt; repository port của domain source | Metadata, abstract và provenance | Điều khiển Chrome; nhận chỉ dẫn fetch URL tùy ý từ model |
| Embedding service | Model local; vector repository port | Sinh vector có generation/model/dimension | Provider API/CLI; thay đổi subscription |
| Report service | Selection port, repository transaction, task service, outbox | Chọn nội dung, đóng kỳ, tạo intent giao | Gửi Telegram trực tiếp; sửa phân tích đã commit |
| Telegram adapter | Telegram API; link/command API; delivery port | Xác thực update, gọi lệnh cho phép, gửi payload đã đóng | Sửa SQLite trực tiếp; sửa tag/config; lấy AI key |
| Backend domain services | Repository theo quyền bảng; secret service có scope | Nghiệp vụ authoritative | Worker tự chọn bảng/path/query tùy ý |
| Backup operator | Backup/restore port có maintenance guard | Tạo snapshot/khôi phục được kiểm chứng | Resume dispatcher tự động ngay sau restore |

**Default deny:** edge không có trong registry bị cấm cho đến khi hợp đồng được sửa và review. Kiểm tra bằng import/dependency rules khi cùng tiến trình, API auth tests khi qua mạng, và network/process capabilities cho worker. Chỉ có sơ đồ là chưa đủ bằng chứng.

### 6.1 Owner của dữ liệu và side effect

- Backend domain sở hữu post/work identity, tag version, Saved, report và state transition; local worker chỉ đề xuất kết quả qua port.
- Analysis worker chịu trách nhiệm thực hiện task, không được tự quyết “work này đã báo cáo”.
- Report service sở hữu `first_announced` và coverage; delivery không thay đổi nội dung report đã publish theo phương án B01 đề xuất.
- Telegram adapter sở hữu hành vi mạng Telegram nhưng chỉ được gửi một intent hợp lệ tới linked owner; nội dung nguồn không định nghĩa recipient.
- Secret service có quyền đọc key lưu ở server; worker chỉ nhận provider credential cần cho assignment nếu chính sách B13 chấp nhận. Phiên X và CLI giữ trên máy cá nhân.

## 7. Invariant phải khóa trước coding

Mỗi invariant có một owner, một positive scenario và ít nhất một counterexample làm gate fail.

| ID | Invariant | Owner/hợp đồng |
| --- | --- | --- |
| I01 | Dữ liệu authoritative chỉ được mutation qua domain port đã xác thực; một owner không có nghĩa bỏ auth | PC01/PC08 |
| I02 | Receipt ingest chỉ ACK sau commit; checkpoint không đi trước dữ liệu bền | PC02/PC03 |
| I03 | Một canonical identity đã xác định chỉ có một work; alias conflict không bị merge đoán | PC02 |
| I04 | Analysis hợp lệ bất biến theo generation; đổi tag không làm gọi AI lại; retry không tạo hai kết quả hợp lệ cùng key | PC06 |
| I05 | Report lưu tag version, selection version và evidence references; không thay nội dung âm thầm sau publish | PC04 |
| I06 | Các coverage window đóng nối liền, half-open; pending item không mất khi con trỏ tiến | PC04 |
| I07 | Một canonical work chỉ có một first-announcement; tham chiếu lịch sử có ngày và không tính là phát hiện mới | PC04 |
| I08 | Save là snapshot bất biến; cùng target có tối đa một Saved active; bỏ tag không xóa snapshot | PC02/PC07 |
| I09 | Telegram thất bại không làm report biến mất hoặc run đổi sang thất bại thu thập | PC03/PC07 |
| I10 | CAPTCHA không tự retry/resume; worker stale/cancelled không commit kết quả mới | PC03/PC05 |
| I11 | Bài nguồn/AI output không có quyền đọc secrets, gọi tool hay đổi recipient | PC06/PC08 |
| I12 | Vector khác model/generation/dimension không được so sánh trong cùng lần selection | PC04 |
| I13 | Incomplete, empty, failed và unknown được hiển thị riêng; không gọi thiếu dữ liệu là không có nghiên cứu | PC03/PC07 |
| I14 | Usage không biết là `unknown`, không ghi thành 0; fallback chỉ theo policy được owner cấu hình | PC06 |
| I15 | Restore không tự gửi lại outbox cũ, chạy lại job side effect hoặc reset `first_announced` mà không kiểm tra | PC08 |

“0 trùng” chỉ có ý nghĩa trên phạm vi identity/oracle đã định nghĩa; trùng khoa học chưa xác định ID phải đo và xử lý xung đột, không tuyên bố đã giải bằng unique constraint.

## 8. Mô hình trạng thái chuẩn đề xuất

Đây là thiết kế để giải B02, cần đóng thành bảng transition trước khi thay enum trong đặc tả.

### 8.1 Run: tách trạng thái thực thi và chất lượng kết quả

- `phase`: `collecting | enriching | analyzing | reporting`.
- `status`: `queued | running | waiting_retry | needs_user | blocked | completed | failed | cancelled`.
- `outcome` khi kết thúc: `complete | partial | empty | failed | cancelled`.
- `stop_reason`: ví dụ `limit_reached`, `captcha`, `session_expired`, `source_blocked`, `storage_unavailable`, `worker_lost`.
- Coverage đã biết và độ thiếu hụt nguồn là metadata riêng; `completed` không có nghĩa quét đủ toàn bộ X.

| From | Event/guard | To | Commit/effect bắt buộc |
| --- | --- | --- | --- |
| queued | Claim hợp lệ, capability đúng | running + phase cần làm tiếp | Cấp lease/epoch; lưu owner của assignment |
| running/collecting | Đạt điểm dừng, đã ACK mọi lô dùng tiếp | running/enriching | Ghi `limit_reached`, đóng collection segment, giữ checkpoint |
| running/collecting | CAPTCHA/phiên hết hạn | needs_user | Checkpoint đã ACK; tạo tối đa một alert intent/run; không tự claim lại |
| needs_user | Resume do owner + kiểm tra phiên không còn challenge | queued | Giữ checkpoint, cấp lease mới khi claim; không tiếp tục bằng lease cũ |
| needs_user | Status hoặc run-now | needs_user | Status chỉ đọc; run-now không thay blocked run |
| running | Lỗi retryable có budget và side effect đã xác định | waiting_retry | Lưu error/attempt/next_attempt_at; không vòng lặp nóng |
| waiting_retry | Đến hạn, dependency ready | queued | Tiếp phần chưa commit, không chạy lại phần đã ACK |
| running | Lease hết hạn | queued hoặc needs_user/blocked đã lưu | Tăng epoch; worker cũ bị từ chối; giữ uncertainty của external attempt |
| running | X chặn hoặc thiếu capability bắt buộc | blocked | Ghi điều kiện gỡ chặn; không đổi account/proxy để chạy tiếp |
| running/analyzing | Một số target lỗi hết budget | running/reporting | Lưu pending/failed item; outcome dự kiến partial |
| running/reporting | Publish commit thành công | completed | Coverage/item ledger/report/outbox theo PC04 cùng commit cần thiết |
| running/reporting | Không có item phù hợp và không có lỗi thiếu dữ liệu | completed, outcome empty | Đóng coverage theo policy; không tạo digest rỗng |
| nonterminal | Owner cancel | cancelled | Thu hồi lease, chặn publish mới; dữ liệu đã commit không bị xóa |
| nonterminal | Lỗi không thể phục hồi trong budget | failed | Giữ mọi commit hợp lệ; hiện lỗi và khả năng retry bằng generation mới |

Nếu CAPTCHA xuất hiện giữa khi dữ liệu đã tải nhưng chưa ingest, không gọi đó là checkpoint bền. Nếu con trỏ feed mất hiệu lực, cho phép đọc lại theo recovery policy và dedup ở ingest.

### 8.2 Analysis item và report

`analysis.status`: `pending → running → valid`; nhánh `retry_wait`, `failed`, `unknown_attempt`. Không ghi output sai schema thành valid. Nếu worker chết sau khi model đã chạy, có thể mất phản hồi và phát sinh lại phí; chỉ bảo đảm không tạo hai **kết quả đã commit** cùng key, không hứa inference bên ngoài chạy đúng một lần.

`report.status`: `building → published`; nhánh `aborted`. `quality`: `complete | partial` là trường riêng. Report không có nội dung không publish thành report hiển thị; ghi coverage ledger. Selection stale do tag/model version đổi trước commit phải rebuild hoặc abort theo B01, không tự sửa report đã publish.

### 8.3 Delivery

| From | Event | To | Quy tắc |
| --- | --- | --- | --- |
| pending | Payload/revision/link generation hợp lệ; có sender lease | sending | Ghi attempt trước network call |
| sending | Nhận success và message ID | sent | Persist receipt; retry sau đó chỉ trả receipt |
| sending | Chắc chắn chưa được nhận hoặc nhận lỗi retryable có nghĩa rõ | retry_wait | Retry có budget/backoff đã đóng |
| sending | Timeout/mất kết nối/crash sau điểm có thể đã gửi | unknown | Không retry tự động; app nêu chưa xác định; operator quyết định có chấp nhận nguy cơ trùng |
| retry_wait | Đến hạn, linked recipient còn hiệu lực | pending | Giữ cùng logical delivery key |
| sending/retry_wait | Lỗi vĩnh viễn hoặc hết budget | failed | App giữ report; không đổi run thành collection failure |
| pending/retry_wait | Hủy liên kết hoặc link generation đã đổi | cancelled | Không gửi tới recipient cũ; không chuyển payload cũ sang recipient mới âm thầm |

Nếu digest có nhiều message, lưu `delivery_part` với index, payload hash và receipt từng phần. Phần unknown không được gửi lại chỉ vì aggregate chưa sent. Unique key nội bộ là điều kiện cần, không phải bằng chứng exactly-once ngoài hệ thống.

### 8.4 Storage và trạng thái không ghi được

`storage.health`: `healthy | write_blocked | maintenance | recovery_required`.

Khi hết ổ/DB unavailable: process chuyển `write_blocked`, ngừng nhận job mới và không ACK mutation. Nếu không thể ghi trạng thái lỗi vào DB, không tuyên bố đã persist lỗi; readiness/health channel độc lập báo không ghi được. Sau phục hồi, transaction receipt và lease epoch quyết định phần nào đã commit. UI phải phân biệt last-known state với trạng thái mới chưa lưu được.

## 9. Các transaction và quy tắc thời gian cần viết thành hợp đồng

### 9.1 Ingest và canonical identity

- Một lô ingest commit dữ liệu post, receipt dedup và checkpoint server cùng transaction phù hợp. Replay do ACK mất trả receipt cũ.
- `discovered_at` dùng thời gian server chấp nhận lần đầu, không tin clock worker; thêm sequence để định thứ tự các mục cùng timestamp. `published_at` của X là trường khác.
- DOI/arXiv normalization, arXiv version và alias được định nghĩa bằng fixture. Identity merge phải chuyển reference/first-announcement/Saved có quy tắc conflict, giữ audit trail.
- Target là tagged union `work` hoặc `post`; không dựa vào hai cột nullable với một UNIQUE mơ hồ để đảm bảo Save/analysis của post-only.

### 9.2 Đóng kỳ báo cáo

PC-ĐX: coverage là khoảng `[from, to)`, lấy từ sổ kỳ authoritative. Chọn `to` và ingest boundary ổn định; report builder dùng snapshot input có version. Transaction publish kiểm tra expected coverage predecessor và tag/model version rồi ghi report items, first-announcement ledger, backfill consumption và delivery intent. Concurrent publisher thua CAS phải đọc lại, không publish kỳ chồng.

- Kỳ rỗng vẫn có coverage record, không gửi digest.
- Mục đã phát hiện trong kỳ nhưng thiếu analysis được ghi pending độc lập; khi ready được xem xét ở kỳ sau với nhãn phát hiện muộn.
- Job thất bại thu thập không tự biến thành một kỳ rỗng thành công. Khi publish partial, coverage phải nêu phạm vi **dữ liệu đã quan sát**, không hứa bao phủ toàn bộ thời gian trên X.
- Backfill N ngày tiêu thụ đúng một lần trên một subscription activation/version đã định danh; chốt add–remove–readd có phải activation mới. Không tiêu thụ backfill chỉ vì builder bị crash hoặc model lỗi.
- “Quét lại kho” là command riêng với ledger riêng; không reset first-announcement hoặc coverage chính.

### 9.3 Cache AI và embedding generation

Analysis key có target canonical ID, source version/fingerprint, task type, prompt/schema version và generation. Chỉ thay tag không đổi key. Đổi provider/model có tự invalidate không phải quyết định bắt buộc trong PC06; đề xuất giữ kết quả cũ đến khi user yêu cầu reanalysis.

Đổi embedding model xây generation mới, kiểm đủ vector và chất lượng trước khi chuyển active generation nguyên tử. Trong lúc rebuild, dùng generation cũ hoặc chặn selection có lý do; không trộn vector mới/cũ, không gọi API để thay local embedding âm thầm.

## 10. Ma trận lỗi và bằng chứng bắt buộc

Các budget có tên nhưng chưa có số là đầu việc phải đóng trong `retry-policy.yaml`; module có policy chưa chốt không được `CONTRACT_READY`.

| Error code đề xuất | Trạng thái đích / phạm vi | Dữ liệu giữ và hành vi cấm | Bằng chứng/oracle |
| --- | --- | --- | --- |
| X_CHALLENGE_REQUIRED | run.needs_user | Giữ checkpoint ACK; không auto retry, không giả click xác minh | Inject challenge sau batch; đúng 1 alert intent/run; không có collect mới trước resume |
| X_ACCESS_BLOCKED | run.blocked | Giữ nguồn đã thu; không luân chuyển account | Trace không có request tiếp; lý do UI khác empty |
| WORKER_LEASE_EXPIRED | assignment revoked; run queued theo guard | Stale worker không commit; không reset needs_user đã lưu | Hai worker claim cùng việc; epoch cũ bị reject |
| INGEST_ACK_LOST | client uncertain, authoritative DB giữ receipt nếu đã commit | Replay cùng key không tăng post/checkpoint | Crash sau commit trước ACK; count và checkpoint không đổi sau replay |
| SOURCE_METADATA_UNAVAILABLE | source degraded; item post-only nếu có post | Không đoán DOI, không xóa abstract cũ đã có | Có/không dữ liệu cache tạo evidence level đúng |
| IDENTITY_CONFLICT | target unresolved/quarantined | Không merge đoán; report không tính hai alias nghi trùng là hai hướng chắc chắn | Fixture DOI/arXiv mapping mâu thuẫn và audit record |
| AI_OUTPUT_INVALID | item retry_wait rồi failed khi hết budget | Không commit valid; không lấy JSON bất kỳ rồi bỏ field kiểm chứng | Sai schema, thiếu citation, JSON lồng transcript; outcome và attempt đúng |
| AI_PROVIDER_UNAVAILABLE | item retry/fallback theo policy, run partial/blocked | Giữ input; fallback không tự bật; usage unknown không ghi 0 | Provider failure với/không fallback cấu hình |
| AI_ATTEMPT_UNCERTAIN | item unknown_attempt | Không cam kết chưa phát sinh phí; tái chạy theo policy ghi attempt mới | Crash sau provider completion trước submit |
| EMBEDDING_GENERATION_MISMATCH | selection blocked | Giữ vector; không cosine giữa khác dimension/model | Hai generation xen kẽ bị chặn trước report commit |
| TAG_VERSION_STALE | report build abort/rebuild | Report publish cũ không bị mutate | Tag change ngay trước CAS commit |
| TELEGRAM_SEND_UNCERTAIN | delivery.unknown | Giữ app report; không auto resend | Mô phỏng Telegram nhận tin rồi cắt response |
| TELEGRAM_PERMANENT_FAILURE | delivery.failed | Không thay run result; không xóa report | Recipient invalid/revoked, DB report hash không đổi |
| UNAUTHORIZED_COMMAND | Không đổi domain state | Chat lạ im lặng; ngoại lệ linking theo B09 | Fake update, callback target sai, mã expired/reused |
| STORAGE_WRITE_FAILED | storage.write_blocked; job không được ACK | Không tiến cursor; không hứa đã persist error | Disk-full/failing write; receipt absent và readiness red |
| RESTORE_UNVERIFIED | storage.recovery_required | Dispatcher/worker claim dừng; outbox không replay | Restore vào môi trường rỗng, trước verify không side effect |

## 11. Kế hoạch thực hiện theo gói

Mỗi gói tạo một deliverable có thể review riêng. “Owner” là vai trò cần chịu trách nhiệm; không yêu cầu phải có nhiều người hoặc nhiều agent. Người xây có thể tự kiểm tra, nhưng phải ghi đó là self-review.

### PC00 — Khóa nguồn, nguyên tử hóa yêu cầu và xử lý mâu thuẫn

**Đầu vào:** spec v0.2 và B01–B17. **Owner:** requirements owner. **Phụ thuộc:** không.

**File:** `precode/baseline.json`, `precode/source/spec-v0.2.md`, `precode/requirements.csv`, `precode/decision-register.md`, `precode/adr/`.

- [ ] Lưu bản nguồn không sửa, hash và metadata; gán source anchor cho từng §/D/AC.
- [ ] Tách mỗi yêu cầu thành một dòng với ID, trạng thái XN/UQ/ĐX/KC, priority và scope.
- [ ] Dựng B01–B17 với recommendation, impacted contracts, decision owner và gate bị chặn.
- [ ] Chuẩn bị các amendment gồm before/after và thay đổi oracle; gom những quyết định sản phẩm cần user chọn thành một bản review cụ thể.
- [ ] Ghi rõ các mục P0 hiện còn ĐX; không tự promote D09/D53 hay chọn stack.

**Đạt khi:** không yêu cầu nào mất nguồn; mọi mâu thuẫn có decision record; mục chưa giải được vẫn chặn đúng phạm vi. **Bằng chứng:** source hash check, requirement count/coverage, decision review. **Cổng:** G0.

### PC01 — Khóa topology, ownership và capability

**Đầu vào:** requirements, B12/B13 và ranh giới §6. **Owner:** architecture owner. **Phụ thuộc:** PC00 đủ dữ liệu liên quan.

**File:** `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml`, `contracts/ops/deployment.md`.

- [ ] Ghi module ID, vị trí chạy, data owner, inbound/outbound operation ID và forbidden edges.
- [ ] Đóng D08/D42/D50 và đường input analysis sau ingest commit; nếu chọn khác, ghi ADR.
- [ ] Xác định actor owner browser, collector, analysis worker, Telegram dispatcher và backup operator với auth scope khác nhau.
- [ ] Định nghĩa readiness/capability registration cho local worker, kể cả CLI provider đang usable hay không.
- [ ] Chuẩn bị negative cases: collector gọi Save, worker đổi tag, frontend đọc secret, adapter gửi Telegram.

**Đạt khi:** mọi edge có hợp đồng hoặc bị deny; mỗi mutation có đúng owner. **Bằng chứng:** topology review và case matrix positive/negative. **Cổng:** G1.

### PC02 — Khóa identity, entity và transaction

**Đầu vào:** PC00/PC01, B06/B07/B15. **Owner:** data contract owner.

**File:** `contracts/data/entities.yaml`, `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/schemas/target.schema.json`, `contracts/schemas/ingest-batch.schema.json`, `acceptance/fixtures/identity/`.

- [ ] Định nghĩa post/work/post-only, identity alias, paper version, analysis generation, Saved target và snapshot.
- [ ] Chốt một owner ở schema: giữ owner_id nếu theo spec nhưng không dựng tenant/multi-user feature.
- [ ] Viết transaction map cho ingest+receipt+checkpoint, identity merge, Save và analysis accept.
- [ ] Tạo fixture merge DOI/arXiv sau ingest, thiếu ID, ID mâu thuẫn, Save đồng thời app/Telegram, nguồn bị xóa.
- [ ] Chốt migration/versioning, referential integrity và cách không làm đổi historical snapshot sau merge.

**Đạt khi:** I02/I03/I04/I08 có oracle theo số hàng/hash/reference và conflict không mất nguồn. **Bằng chứng:** schema fixture validation + transaction walkthrough trước/giữa/sau commit. **Cổng:** G2.

### PC03 — Khóa scheduler, lease, checkpoint và state machines

**Đầu vào:** PC01/PC02, B02/B05/B08/B10. **Owner:** workflow contract owner.

**File:** `contracts/state/run.yaml`, `contracts/state/analysis.yaml`, `contracts/state/report.yaml`, `contracts/state/delivery.yaml`, `contracts/state/storage.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`.

- [ ] Lập transition table theo mẫu from/event/guard/to/transaction/effect/oracle; ánh xạ enum cũ trong spec.
- [ ] Chốt claim/lease TTL/heartbeat/epoch, stale writer, cancel và resume; mọi số timeout/budget có đơn vị và lý do.
- [ ] Chốt lịch/timezone, earliest-run, catch-up coalescing và xử lý manual request khi đang có active run.
- [ ] Định nghĩa checkpoint chỉ trên dữ liệu đã ACK, replay, stale cursor và khi worker chết sau external call.
- [ ] Tạo failure timeline cho từng ranh giới commit và kiểm tra transition bị cấm.

**Đạt khi:** mọi lỗi §10 map tới trạng thái; không terminal nào vẫn âm thầm chạy side effect; không chỗ nào yêu cầu persist error trong DB đang không ghi được mà thiếu fallback health. **Bằng chứng:** transition lint, reachability review và fault matrix. **Cổng:** G2.

### PC04 — Khóa thời gian, tag, coverage và chọn hướng nghiên cứu

**Đầu vào:** PC02/PC03, B01/B04/B08/B14/B17. **Owner:** reporting contract owner.

**File:** `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/schemas/report.schema.json`, `acceptance/fixtures/reporting/`.

- [ ] Đóng thời điểm tag freeze, coverage boundary, discovered_at/sequence, reporting backlog và một publisher thắng CAS.
- [ ] Chốt alias/exclusion precedence, similarity metric, threshold policy và embedding generation.
- [ ] Viết one-time backfill ledger và manual rescan, gồm thêm/bỏ/thêm lại tag và crash giữa builder.
- [ ] Chốt first-announcement/reference logic sau merge identity, paper version mới và Saved không liên quan subscription.
- [ ] Định nghĩa vector density, cửa sổ so sánh, min sample, cold-start, tie-break và label “ứng viên để đọc sâu”; AI chỉ diễn đạt kết quả đã tính.
- [ ] Tạo fixture tag đổi trước publish, sau publish trước Telegram, report rỗng, late analysis, ba đợt offline và concurrent report.

**Đạt khi:** D27/D28/D29/D46/D54 có phép tính/oracle tái lập; tham số chưa đủ dữ liệu có gate thí nghiệm, không tự đánh dấu đạt. **Bằng chứng:** timeline tables, expected selected IDs, coverage/backfill state trước-sau. **Cổng:** G3.

### PC05 — Khóa collector và paper connector; thiết kế probe khả thi

**Đầu vào:** PC01/PC02/PC03, B05/B12. **Owner:** connector contract owner.

**File:** `contracts/http/openapi.yaml`, `contracts/schemas/worker-assignment.schema.json`, `contracts/schemas/ingest-receipt.schema.json`, `contracts/ops/collector-probe.md`, `acceptance/fixtures/collection/`.

- [ ] Chốt operation claim/heartbeat/ingest/stop/resume, payload size, source provenance và auth.
- [ ] Ghi giới hạn nguồn: thread chính tác giả, không replies ngoài, ảnh không đoán ID, Chrome chỉ X và metadata server qua API.
- [ ] Pin phiên bản tài liệu nguồn, rate/identity requirements của arXiv/OpenAlex khi thực hiện, không gọi không giới hạn.
- [ ] Viết protocol probe 5–10 đợt theo A1: profile, lịch, budget, stop conditions, bài mới, blocked rate và phạm vi không quan sát được.
- [ ] Tạo fixture static/recorded cho feed chuyển layout, cursor mất hiệu lực, challenge, duplicate ingest; không để test nền tảng bắt buộc có X live.

**Đạt khi:** collector contract kiểm chứng được offline; probe có tiêu chí go/no-go và điều kiện dừng được chấp nhận trước chạy. **Bằng chứng Pre-code:** protocol + fixtures. **Bằng chứng chưa có:** 5–10 đợt thực tế. **Cổng:** G3; quyền chạy spike là SP1, không tự coi đã có.

### PC06 — Khóa AI API/CLI/ACP và grounding

**Đầu vào:** PC01/PC02/PC03/PC04, B07/B13/B16/B17. **Owner:** AI contract owner.

**File:** `contracts/ai/tasks.yaml`, `contracts/ai/providers.yaml`, `contracts/ai/grounding.md`, `contracts/schemas/analysis-result.schema.json`, `acceptance/fixtures/ai/`.

- [ ] Tách task schema cho labels, summary và diễn đạt hướng nổi; dữ liệu vào có source ID/hash/evidence level, không chỉ một prompt string chung.
- [ ] Chốt enum claim kind, citation target, unknown comparator, unsupported field và maximum evidence level theo tài liệu đã đọc thật.
- [ ] Định nghĩa capability cho từng adapter: auth family, task support, concurrency, timeout, cancellation, JSON extraction và usage unknown.
- [ ] Chốt retry budget qua cả worker/adapter để không nhân retry; fallback có allowlist và thứ tự, không do model chọn.
- [ ] Đóng phân tích once-per-generation, reanalysis trigger, provider model switch và log token/cost không giả dữ liệu.
- [ ] Viết probe CLI/ACP theo từng provider/version, đủ cả policy check và khả năng khóa tool/side effect; không dùng tên ACP để suy ra mọi CLI tương thích.
- [ ] Tạo adversarial fixture: instruction trong post, citation không tồn tại, JSON đúng schema nhưng không có nguồn, transcript chứa secret canary, tool request.

**Đạt khi:** không adapter nào chỉ cam kết “JSON”; task output và quyền đều kiểm được. Luồng zero-API-key phải gồm cả diễn đạt hướng nổi nếu bật, không chỉ labels/summary. **Bằng chứng:** golden fixtures, capability matrix, groundedness rubric và probe protocol. **Cổng:** G3.

### PC07 — Khóa app, Save và Telegram delivery

**Đầu vào:** PC02/PC03/PC04/PC06, B01/B03/B09/B10. **Owner:** interaction contract owner.

**File:** `contracts/ui/screens.yaml`, `contracts/telegram/commands.yaml`, `contracts/telegram/delivery.md`, `contracts/schemas/saved-snapshot.schema.json`, `acceptance/fixtures/telegram/`.

- [ ] Với từng màn hình §4 spec, map read model, action operation, auth, mobile capability, loading/empty/partial/error.
- [ ] Chốt 3 lệnh Save/run-now/status; resume ở đâu, link/unlink lifecycle và ngoại lệ linking trước khi có owner chat.
- [ ] Snapshot lấy từ report analysis revision đang đọc, không lấy bản analysis mới hơn vừa xuất hiện; define Save duplicate và unsave/re-save.
- [ ] Chốt ingress auth/update replay, callback target validation, linked recipient generation, OTP expiry/one-use, rejection im lặng.
- [ ] Đóng outbox+part receipts+unknown delivery và chính sách sửa AC-14; payload formatting/length và escape source text theo API đã kiểm tra.
- [ ] Tạo fixture multi-part digest, response mất, unlink trước send, callback stale, mã dùng hai lần và chat lạ.

**Đạt khi:** mọi nút/lệnh chỉ gọi operation được cho phép; unknown không bị che thành sent/failed; report app độc lập delivery. **Bằng chứng:** screen/action map, Save hash oracle, delivery timeline và forbidden-action cases. **Cổng:** G3.

### PC08 — Khóa secrets, Internet boundary, backup và recovery

**Đầu vào:** PC01–PC03, PC06/PC07 liên quan, B11/B13. **Owner:** operations contract owner.

**File:** `contracts/ops/secrets.md`, `contracts/ops/backup-restore.md`, `contracts/ops/deployment.md`, `acceptance/fixtures/recovery/`.

- [ ] Chốt một account không signup; session expiry/revocation, owner API protection, CSRF nếu cookie auth, collector token scope/rotation.
- [ ] Chốt secret storage/key-at-rest và distribution tới worker; Chrome debug loopback; tách browser profile khỏi backup server.
- [ ] Chặn URL fetch ngoài policy, redirect tới private/internal address, nội dung render gây script execution và CLI tool access từ nguồn.
- [ ] Định nghĩa backup khi DB hoạt động, bản manifest chứa DB/schema/hash, embedding artifacts/config, secret recovery plan và retention.
- [ ] Viết restore drill vào môi trường sạch, integrity check, count/hash Saved/report/ledger, revoke stale leases và khóa dispatch cho tới reconciliation.
- [ ] Chốt RPO/RTO theo nhu cầu, disk-full/readiness và audit retention; không suy diễn transaction bảo vệ được mọi lỗi phần cứng.

**Đạt khi:** một người khác đọc runbook có thể biết phục hồi tới mốc nào, phần nào thiếu và side effect nào chưa được bật. **Bằng chứng Pre-code:** drill recipe/oracle; live restore evidence phải tạo ở giai đoạn triển khai. **Cổng:** G3.

### PC09 — Khóa oracle, traceability, evidence và readiness

**Đầu vào:** PC00–PC08. **Owner:** verification owner.

**File:** `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `evidence/manifest.schema.json`, `precode/gates.yaml`, `precode/review.md`.

- [ ] Map mọi P0 và AC-01–AC-18 tới contract, invariant, scenario và loại bằng chứng.
- [ ] Chọn fixture có dữ liệu đúng/sai độc lập; chỉ rõ những gì mock được và điều gì buộc cần live/human review.
- [ ] Validate schema/examples, reference integrity, transition/error coverage và denied-edge scenarios bằng tooling tài liệu nhẹ khi thực hiện Pre-code.
- [ ] Tạo evidence manifest và baseline invalidation rules; mọi chưa chạy ghi `NOT_RUN`, không tạo log pass giả.
- [ ] Thiết kế đánh giá A2/A3/A4 và tiêu chí thành công theo tuần, có tập calibration và tập đánh giá tách biệt; khóa rubric trước tuning.
- [ ] Review lại B01–B17, registry ĐX/KC, quyết định và phạm vi code-ready theo module.

**Đạt khi:** không orphan requirement, không invariant thiếu negative case, không assertion “done” không có evidence reference. **Bằng chứng:** coverage report, validation result và blocker register. **Cổng:** G4.

### PC10 — Tạo task card cho coding và giao bộ hợp đồng

**Đầu vào:** G4 cho phạm vi định giao. **Owner:** implementation planning owner.

**File:** `agent-tasks/TEMPLATE.md`, các card theo module trong `agent-tasks/`, `precode/change-control.md`, `precode/README.md`.

- [ ] Chọn stack sau khi ranh giới và ràng buộc đã rõ; ghi ADR. Khai đường dẫn implementation/test thật trong từng card sau quyết định stack.
- [ ] Tách card theo deliverable có thể kiểm độc lập, không theo “làm toàn backend” hay “làm toàn UI”.
- [ ] Gắn contract versions/hash, allowed files, imports/edges, consumed/produced operations và proof obligations.
- [ ] Ghi stop conditions, dependencies, reviewer scope, expected evidence và claim tối đa được phép.
- [ ] Walkthrough một card collector và một card delivery: agent chỉ đọc card+references có đủ làm việc mà không đoán giao tiếp/state không?

**Đạt khi:** người nhận card biết mình không được sửa gì, khi nào phải báo blocked và bằng chứng nào đủ chấp nhận. **Cổng:** G5. Chưa tự chạy coding vì có task card.

## 12. Thứ tự và cổng chuyển giai đoạn

| Gate | Điều kiện bắt buộc | Cho phép tiếp theo |
| --- | --- | --- |
| G0 — Baseline | Nguồn/hash, registry, B-register đầy đủ; XN/UQ không bị đổi ngầm | Soạn topology và từng hợp đồng; chưa product coding |
| G1 — Boundaries | Ownership/capability/edge registry nhất quán; topology proposal liên quan đã đóng | Soạn schema/state độc lập framework |
| G2 — Data/workflow | Identity, transaction, state, checkpoint có oracle; B tương ứng đã giải | Soạn report/collector/AI/UI trên interface ổn định |
| G3 — Domain contracts | PC04–PC08 đủ semantics/schema/errors và fixture; mọi policy bắt buộc có giá trị cụ thể | Tích hợp contract review; soạn card |
| G4 — Auditable baseline | Traceability đầy đủ, static checks đạt, B liên quan đóng, KC có scope và probe gate | Gọi baseline là CONTRACT_READY trong đúng phạm vi |
| G5 — Task ready | Card pin baseline, stack/path đã chọn, dependency và evidence rõ | Bắt đầu coding phạm vi được giao khi user yêu cầu |
| SP1 — Feasibility probe | Profile/credential hợp lệ, protocol/stop/go-no-go được chấp nhận; không bypass | Viết/chạy spike tối thiểu khi được phép; output vẫn là evidence probe |
| G6 — Integration/live | Code và contracts đúng baseline; fault tests và live proof theo claim | Gọi integration/live verified; chưa suy ra product accepted |
| G7 — Product acceptance | Quan sát đủ kỳ/tuần theo rubric đã chốt; user đánh giá kết quả | Gọi product accepted với giới hạn đo đã công bố |

Thứ tự chính: PC00 → PC01 → PC02 → PC03 → PC04 → PC05/PC06 → PC07/PC08 → PC09 → PC10. Các nhánh có thể được soạn độc lập khi dependency đã đóng; kế hoạch không yêu cầu tự khởi tạo sub-agent.

SP1 cho X nên chạy sớm sau G2 và PC05, vì rủi ro nguồn lớn nhất. Hợp đồng các phần còn lại vẫn có thể được soạn bằng fixture; không đầu tư hoàn thiện sản phẩm trên giả định collector đã ổn. Nếu probe thất bại, báo quyết định blocked cho nguồn X, không tự chuyển sang X API trả phí.

“Chưa chọn stack” không cản soạn invariant và wire schema; nó cản card triển khai có đường dẫn/build/test chính xác. “Chưa có 3–4 kỳ thật” không cản viết thuật toán density contract; nó cản tuyên bố thuật toán hữu ích.

## 13. Ma trận truy vết khởi đầu cho AC-01–AC-18

Các mã SC dưới đây là scenario phải tạo, **chưa phải test đã chạy**. Registry đầy đủ phải bổ sung toàn bộ D/P0, không chỉ 18 AC.

| Yêu cầu nguồn | Contract/gói | Scenario và oracle chính | Bằng chứng để chấp nhận code |
| --- | --- | --- | --- |
| AC-01 | PC03/PC05 | SC01 lịch tới hạn khi worker online → assignment tự claim | Fake-clock integration; live collector run có timestamp |
| AC-02 | PC03 | SC02 offline nhiều kỳ → một catch-up theo policy | Queue rows + interval expected + resume trace |
| AC-03 | PC03/PC05 | SC03 budget đạt → ngừng collect, checkpoint ACK và phase/outcome đúng amendment B02 | Request count, checkpoint hash, transition log |
| AC-04 | PC03/PC05/PC07 | SC04 CAPTCHA → needs_user, một alert intent, resume hợp lệ mới chạy | Fault trace; delivery alert receipt/unknown riêng; live observation |
| AC-05 | PC04 | SC05 bỏ tag trước freeze → target không được chọn | Expected selected IDs + tag version + DB snapshot |
| AC-06 | PC04/PC06 | SC06 bỏ/thêm tag → cache analysis dùng lại | Provider call counter delta = 0 cho analysis cùng generation |
| AC-07 | PC02 | SC07 nhiều post/author thread + ID cùng work → một target | Canonical work count, alias map, provenance list |
| AC-08 | PC04 | SC08 nhiều kỳ, empty, crash publisher → windows nối liền | Coverage ledger assertions, CAS conflict trace |
| AC-09 | PC02/PC04 | SC09 work đã announced/alias merge → reference có ngày | First-announced uniqueness + report item type |
| AC-10 | PC06/PC07 | SC10 app/Telegram dùng cùng analysis revision đủ trường | Contract payload + render review trên desktop/mobile/Telegram |
| AC-11 | PC06 | SC11 chỉ có post → evidence level post-only, claims có provenance | Schema+semantic validation và human groundedness review |
| AC-12 | PC02/PC08 | SC12 Save/restart/source deleted → snapshot còn nguyên | Snapshot hash trước/sau restart và restore |
| AC-13 | PC02/PC07 | SC13 app/Telegram Save đồng thời, callback lặp → một Saved | DB constraint outcome + responses + snapshot revision |
| AC-14 | PC07 | SC14 send failure/unknown/multipart theo amendment B03 | Fault at commit/send/ACK; receipts; không retry unknown |
| AC-15 | PC03/PC07 | SC15 empty/limit/failure → ba read model/UI khác nhau | State-to-view assertions + ảnh/render review |
| AC-16 | PC06 | SC16 không API key, mọi task cần AI qua CLI; embedding local | Live capability run, không secret/API route phát sinh ngoài cấu hình |
| AC-17 | PC06/PC08 | SC17 prompt injection/schema-valid attack → không secret/tool/send | Canary + tool/network audit + rejection record |
| AC-18 | PC07/PC08 | SC18 chat lạ → không domain mutation, không reply; linking exception riêng | Verified fake-update fixtures, outbound call count = 0 |

Bổ sung tối thiểu SC19–SC28: tag đổi sau publish trước delivery; stale lease; ingest ACK mất; late analysis/backfill crash; identity conflict; embedding generation switch; Telegram relink; disk full; restore với outbox cũ; worker chết sau AI call. Mỗi SC có input, event order, expected state, durable rows, forbidden effects và evidence paths.

## 14. Chuẩn bằng chứng và cách tuyên bố hoàn thành

### 14.1 Evidence manifest

Mỗi lần kiểm tra có một manifest chứa đủ:

| Nhóm | Trường bắt buộc |
| --- | --- |
| Danh tính | `evidence_id`, `created_at`, `producer_role`, `review_type` (self/independent) |
| Baseline | `spec_sha256`, `contract_versions`, `contract_hashes`, `implementation_revision` nếu có |
| Môi trường | OS/runtime/dependency versions liên quan, config đã che secrets, provider/model/embedding generation |
| Đầu vào | Scenario IDs, fixture/dataset hash, seed/clock nếu cần, protocol version |
| Thực thi | Command hoặc manual procedure chính xác, start/end, exit status, attempt/error classification |
| Kết quả | `PASS | FAIL | BLOCKED | NOT_RUN | STALE | NOT_APPLICABLE`, expected vs observed |
| Artifacts | Đường dẫn và SHA-256 của logs đã che secrets, DB assertions, traces, screenshots/receipts |
| Giới hạn | Mock/live, mẫu thử, những gì không kiểm tra, uncertainty và unresolved issue refs |

`NOT_APPLICABLE` phải có lý do và decision ref; không dùng để bỏ một AC khó. Không có ngày chạy/kết quả thật thì phải ghi NOT_RUN. Hash giúp phát hiện artifact bị đổi, không tự chứng minh artifact là thật; cần provenance thực thi và review.

### 14.2 Evidence theo cấp

| Cấp | Bằng chứng | Chứng minh được | Không chứng minh được |
| --- | --- | --- | --- |
| E0 | Lint schema/reference/traceability | Bộ hợp đồng tự nhất quán ở phần đã kiểm | Code hoạt động |
| E1 | Contract tests bằng fixture | Producer/consumer đáp ứng trường hợp đã định nghĩa | Dịch vụ thật ổn định |
| E2 | Integration + crash/fault injection | Transaction, retry, auth, state và tương tác module | Chất lượng khoa học dài hạn |
| E3 | Live probes có giới hạn | X/AI/CLI/Telegram hoạt động trong điều kiện đã ghi | Không bao giờ bị chặn hoặc không bao giờ trùng |
| E4 | Review nội dung qua nhiều kỳ/tuần | Tiêu chí hữu ích/độ nhiễu trên mẫu thực tế | Tính mới khoa học tuyệt đối |

Định nghĩa rubric trước đo: thế nào là hướng dùng được, sai nhãn, duplicate, “mỗi tuần”; denominator nào và ai đánh giá. Với A2/A3 dùng dữ liệu có nhãn độc lập và tập đánh giá tách khỏi tập dò ngưỡng. Với A4 thiếu 3–4 kỳ thì ghi chưa đủ bằng chứng, không chỉnh số để pass.

### 14.3 Mẫu completion claim

```text
Claim: IMPLEMENTATION_VERIFIED trong phạm vi task ID được giao.
Baseline: spec hash + contract version/hash + implementation revision.
Requirements covered: danh sách REQ/AC/INV cụ thể.
Evidence: manifest IDs và artifact paths có kết quả thực.
Observed result: trạng thái/hàng dữ liệu/side effect đúng oracle.
Not established: live X stability, product usefulness hoặc mục chưa được kiểm.
Open issues: ID + mức ảnh hưởng; nếu chặn claim thì status = BLOCKED.
Review: self-review hoặc người/vai trò review thực tế; không khai review không xảy ra.
```

Chỉ có “tests pass” không đủ. Một assertion fail, test bị skip cho P0, manifest stale hoặc missing negative case khiến claim tương ứng không được pass.

## 15. Task card chuẩn cho agent

Mỗi card cần đủ để agent không phụ thuộc trí nhớ cuộc trò chuyện:

1. **Task ID, goal và non-goals:** một kết quả nghiệp vụ có thể kiểm riêng.
2. **Read set:** spec refs, ADR, contract versions/hash và fixture bắt buộc.
3. **Write set:** đường dẫn source/test cụ thể sau chọn stack; file contract dùng chung mặc định read-only.
4. **Consumes/produces:** exact operation IDs, schema và state effects; không tự tạo endpoint gần giống.
5. **Allowed communication:** module/capability allowlist và denied paths.
6. **Invariants và transaction:** điểm commit, replay, race và forbidden effects.
7. **Error obligations:** từng error code và đích trạng thái; ai retry; khi nào phải dừng.
8. **Verification:** scenario IDs, command sẽ chạy, oracle, evidence artifacts và yêu cầu live nếu có.
9. **Completion ceiling:** claim tối đa là contract/implementation/integration/live, không nói rộng hơn.
10. **Stop-and-report:** thiếu contract, B chưa đóng, API khác tài liệu, need capability ngoài phạm vi, test oracle mâu thuẫn.

Ví dụ card cần tạo: ingest idempotent với ACK mất; canonical merge; scheduler lease; analysis adapter validation; report coverage; Saved snapshot; Telegram unknown delivery. Không giao một card chung “làm bot từ đầu tới cuối”.

Agent không được sửa test expectation để hợp thức hóa implementation, thêm edge giao tiếp ngoài registry, ghi DB qua đường tắt hoặc bật fallback provider chưa cấu hình. Phát hiện hợp đồng sai → change request có bằng chứng và đề xuất, không tự rewrite nguồn chuẩn.

## 16. Quản lý thay đổi và bằng chứng hết hiệu lực

- Mỗi change request ghi nguồn thay đổi, trước/sau, lý do, affected requirements/contracts/modules/fixtures/evidence và migration nếu có.
- Sửa schema/enum/semantics/auth scope phải cập nhật version, consumer compatibility và traceability. Không chỉ sửa prose một nơi.
- Sửa tag freeze/coverage/identity/analysis key → vô hiệu bằng chứng liên quan report/Save/cache, không cần chạy lại test không bị ảnh hưởng.
- Sửa provider/model/prompt hoặc embedding generation → bằng chứng chất lượng và schema behavior tương ứng chuyển STALE cho đến recheck.
- Sửa dispatcher/retry/linking → recheck unknown delivery, replay, unlink và unauthorized commands.
- Spec mới không tự thay baseline của task đang chạy; task nhận baseline mới sau impact review. Bản cũ vẫn giữ để audit.
- Thay đổi có thể được chủ dự án chấp nhận một lần cho toàn phạm vi ảnh hưởng; không tạo vòng xin phép lặp cho từng file.

## 17. Definition of Ready của toàn bộ Pre-code

- [ ] Spec snapshot/hash và registry nguyên tử tồn tại.
- [ ] Tất cả XN/UQ/P0 có mapping; mọi ĐX/KC còn lại có trạng thái và gate rõ.
- [ ] B01–B17 được giải hoặc explicit scoped block; không còn blocker của module định coding.
- [ ] Mỗi module có ownership, port và denied edges; negative cases đủ.
- [ ] Mỗi operation có schema, auth, transaction, idempotency, concurrency, error và evidence.
- [ ] Mỗi error code có trạng thái đích, điều kiện phục hồi và hành vi bị cấm.
- [ ] Coverage/backfill/pending/tag version và identity/analysis/Saved có oracle cho race/crash.
- [ ] Telegram unknown, CLI capability, backup WAL/restore và secrets không còn mô tả mơ hồ.
- [ ] AC-01–AC-18 và các SC bổ sung có fixtures/oracles, loại bằng chứng và amended AC đúng nguồn.
- [ ] E0 đã chạy thật và có manifest; E1–E4 chưa chạy ghi NOT_RUN.
- [ ] Card triển khai pin baseline, paths/stack, contracts và proof obligations.
- [ ] Readiness report liệt kê module nào READY/BLOCKED, không chỉ một badge “xong”.

## 18. Hành động tiếp theo cụ thể

**Bắt đầu bằng PC00.** Tạo source baseline và requirement/decision registry, rồi chuẩn bị một bản review gọn cho các điểm làm thay đổi cam kết: thời điểm tag freeze (B01), giới hạn bảo đảm giao Telegram (B03), coverage/backlog (B04), resume (B10), backup (B11) và profile/topology (B12). Các hợp đồng ít phụ thuộc có thể được soạn trong lúc những điểm này chờ quyết định.

Không bắt đầu bằng cài framework hoặc scaffold UI. Kết quả đầu tiên cần có là **một baseline yêu cầu có thể truy vết và một danh sách quyết định chặn được diễn đạt đủ cụ thể để chấp nhận hoặc bác bỏ**.

### Bàn giao hiện tại

File kế hoạch này đã được soạn dựa trên toàn bộ đặc tả đính kèm. Chưa có hợp đồng nào được tuyên bố accepted, chưa có evidence E1–E4, chưa chạy collector, chưa gọi provider AI và chưa gửi Telegram. Phần thực hiện PC00–PC10 là công việc tiếp theo của giai đoạn Pre-code.
