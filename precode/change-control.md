---
contract_id: CT-precode-change-control
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs: [SRC-PLAN §16, SRC-PLAN §5, SRC-PLAN §12, SRC-PLAN §14, SRC-PLAN §17, SRC-SPEC §13.2]
requirement_refs: [REQ-A6, REQ-OQ02, REQ-OQ03, REQ-S7.3-05]
decision_refs: [B01, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11, B12, B13, B14, B15, B16, B17, ADR-0006]
invariant_refs: [I01, I02, I03, I04, I05, I06, I07, I08, I09, I10, I11, I12, I13, I14, I15, I16, I17]
invalidation_rule_refs: [INV-01, INV-02, INV-03, INV-04, INV-05, INV-06, INV-07, INV-08, INV-09, INV-10]  # định nghĩa ở precode/gates.yaml, KHÔNG lặp lại ở đây
producers: []
consumers: []
dependencies:
  - precode/README.md
  - precode/baseline.json
  - precode/decision-register.md
  - agent-tasks/TEMPLATE.md
  - precode/gates.yaml
  - evidence/manifest.schema.json
scope: >-
  Quy trình thay đổi của toàn bộ baseline Pre-code: định dạng change request, luật tăng version, ma trận
  vô hiệu hóa bằng chứng, cách Owner chấp nhận một lần cho cả phạm vi ảnh hưởng, cách task đang chạy nhận
  baseline mới, và cách các CR-* phát sinh trong Pre-code được xử lý. File này là quy trình đề xuất ở trạng
  thái draft — nó không tự cho phép ai sửa gì.
verification: >-
  EV-PC10-04 (SELF_VALIDATION): đối chiếu từng gạch đầu dòng của SRC-PLAN §16 với một mục trong file này.
  E0 lint của PC09 chưa chạy trên file này — NOT_RUN.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Quản lý thay đổi và bằng chứng hết hiệu lực

Hiện thực SRC-PLAN §16 thành quy trình dùng được. Một câu tóm tắt: **thay đổi không phải là sửa một chỗ; nó
là sửa một chỗ, tăng version, và tuyên bố những bằng chứng nào vừa chết theo.**

## 0. Phạm vi và giới hạn của chính file này

- File này ở trạng thái `draft` với claim ceiling `DRAFT_FOR_REVIEW`. Nó **mô tả** quy trình, không **cấp**
  quyền cho ai.
- Trong phiên Pre-code (`DOCUMENTARY_DRAFT`), không có runtime guard nào ép quy trình này. Nó được thực thi
  bằng kỷ luật của Coordinator qua TASK_PACKET, không bằng OS.
- Mọi CR do các gói PC00–PC10 phát sinh đều là **đề xuất**, không phải quyết định. Xem §7.

## 1. Định dạng change request

Mỗi CR là một khối có đủ chín trường. Thiếu một trường ⇒ CR không được xét.

```yaml
cr_id: CR-<PC>-<nn>            # ví dụ CR-PC07-04; PC10 dùng CR-PC10-01..
raised_by: <gói/vai trò>       # ai phát hiện
addressed_to: <gói/vai trò/Owner>   # ai có quyền sửa file đó
status: OPEN | PROVISIONAL | OWNER_DECISION_REQUIRED | CLOSED_BY_OWNER
source_of_change: >            # nguồn thay đổi: nguồn ngoài, mâu thuẫn nội bộ, quyết định Owner, kết quả probe
before: >                      # trạng thái hiện tại, trích nguyên văn + đường dẫn + dòng
after: >                       # đề xuất, đủ cụ thể để chấp nhận hoặc bác bỏ
reason: >                      # vì sao before sai hoặc không đủ
affected:
  requirements: [REQ-...]
  contracts:    [<đường dẫn>]  # kèm version hiện tại
  modules:      [MOD-...]
  fixtures:     [<đường dẫn>]
  evidence:     [EV-..., EVM-...]   # cái nào chuyển STALE — xem §4
migration: >                   # dữ liệu/hợp đồng cũ đi đâu; "không cần" cũng phải viết ra
```

Ba luật viết CR:

1. **`before` phải trích nguyên văn.** "File X nói sai" không phải CR; "File X dòng 812 viết `A`, phải là `B`"
   mới là CR.
2. **`after` phải đủ để bác bỏ.** Nếu Owner không thể trả lời có/không, CR chưa viết xong.
3. **Không CR nào tự đóng chính nó.** Người phát hiện không phải người phê duyệt.

## 2. Luật tăng version

SRC-PLAN §16: *"Sửa schema/enum/semantics/auth scope phải cập nhật version, consumer compatibility và
traceability. Không chỉ sửa prose một nơi."*

| Loại thay đổi | Version | Bắt buộc kèm theo |
| --- | --- | --- |
| Sửa lỗi chính tả, làm rõ prose, không đổi hành vi | patch (`0.1.0 → 0.1.1`) | ghi trong CR là "no behaviour change" và nói vì sao |
| Thêm trường **optional**, thêm mã lỗi mới, thêm operation mới | minor (`0.1.0 → 0.2.0`) | cập nhật `consumers`, thêm scenario, thêm fixture |
| Đổi/xóa trường bắt buộc, đổi enum, đổi ngữ nghĩa, đổi `auth_scope`, đổi `idempotency` key, đổi commit point | **major** (`0.1.0 → 1.0.0`) | migration plan + consumer impact + amendment nếu đụng câu chữ đặc tả |
| Đổi `transaction` / `commit_point` / invariant | **major** | phải có counterexample mới làm gate fail (SRC-PLAN §7) |

Quy tắc kèm theo:

- **Không dùng "latest".** SRC-PLAN §5 cấm; card pin hash, không pin nhãn.
- **Đổi enum là major kể cả khi chỉ thêm giá trị**, vì consumer đã viết `match` đầy đủ sẽ vỡ. Ngoại lệ duy
  nhất: enum được khai `open` ngay từ đầu và consumer bắt buộc có nhánh `unknown`.
- **Đổi `auth_scope` luôn là major**, kể cả nới lỏng. Nới lỏng auth là thay đổi bề mặt tấn công.
- Đổi một hợp đồng ⇒ **mọi card pin file đó thành `STALE`** (§5), không cần biết nội dung đổi có liên quan
  tới card hay không. Hash là hash.

## 3. Amendment và đặc tả nguồn

`research-radar-spec.md` và `research-radar-pre-code-plan.md` là **bất biến** trong phiên này; bản sao đã pin
nằm ở `precode/source/`. Không sửa nguồn. Khi một quyết định làm đổi câu chữ đã cam kết của đặc tả, tạo một
`AMD-B<nn>` trong `precode/decision-register.md` với: câu gốc, câu đọc lại, blocker liên quan, và AC nào bị
sửa. Ví dụ đã có: AMD-B01 (thời điểm freeze tag), AMD-B02 (AC-03), AMD-B03 (AC-14), AMD-B05 (AC-04),
AMD-B10 (§5.4 bước 4), AMD-B11 (D58 "copy file").

## 4. Ma trận vô hiệu hóa bằng chứng

**Nguồn chuẩn là `precode/gates.yaml` khóa `invalidation_rules`, `INV-01`…`INV-10`.** File này **không** định
nghĩa lại chúng (ruling `CR-PC09-07`): một quy tắc vô hiệu hóa chỉ được sống ở một chỗ, nếu không hai bản sẽ
trôi khỏi nhau đúng vào lúc cần chúng nhất. Ở đây chỉ có bảng tra "thay đổi gì → đọc quy tắc nào".

| Bạn vừa sửa | Đọc quy tắc | Quy tắc đó nói gì (tóm tắt — bản đầy đủ ở `gates.yaml`) |
| --- | --- | --- |
| `contracts/reporting/time-and-tags.md` — freeze tag, ranh giới coverage, backfill | `INV-01` | STALE mọi bằng chứng report/selection/coverage/Save gắn với kỳ; hạ G3, G4 |
| `contracts/data/identity.md`, quy tắc chuẩn hóa DOI/arXiv | `INV-02` | STALE identity, merge, first-announcement, dedup; hạ G2, G4 |
| `analysis_key`, `prompt_version`, `schema_version` của một task AI | `INV-03` | STALE **toàn bộ** cache analysis — đây là thay đổi **tốn tiền**, không chỉ tốn công chạy lại; hạ G2, G3, G4 |
| Provider, model, hoặc embedding generation | `INV-04` | STALE bằng chứng chất lượng (E4) và hành vi schema; đổi embedding model buộc tính lại toàn kho; hạ G3, G4, G7 |
| Dispatcher, retry policy, vòng đời liên kết Telegram | `INV-05` | STALE unknown delivery, replay, unlink, lệnh không được phép; hạ G3, G4 |
| Schema / enum / ngữ nghĩa / `auth_scope` của **bất kỳ** operation nào | `INV-06` | STALE bằng chứng của mọi consumer; phải cập nhật version **và** consumer compatibility **và** traceability; hạ G1–G4; máy kiểm được bằng `e0_check` E0-04/05/07 |
| Owner phê chuẩn hoặc **bác** một trong B01–B17 | `INV-07` | Phê chuẩn ⇒ gỡ nhãn `PROVISIONAL`; **bác** ⇒ STALE mọi hợp đồng dựng trên phương án đó, kèm fixture và scenario; hạ G0–G4 |
| Nguồn (spec hoặc plan) đổi hash | `INV-08` | `STALE_BASELINE` cho **mọi thứ**; hạ toàn bộ cổng kể cả SP1, G6, G7 |
| Một fixture bị sửa hoặc đổi tên | `INV-09` | STALE mọi bằng chứng E1+ đã dùng fixture đó; hash trong evidence manifest không còn khớp; hạ G3, G4 |
| Timezone của owner (B08) hoặc lịch chạy | `INV-10` | Dựng lại mọi fixture lịch và biên coverage theo giờ owner; hạ G2, G3, G4 |

Luật đọc bảng:

- Một thay đổi rơi vào nhiều hàng ⇒ lấy **union** của các tập `scenarios_stale`, và cổng bị hạ là cổng **thấp
  nhất** trong các hàng đó.
- `INV-06` và `INV-09` là hai quy tắc chạm tới task card: **đổi bất kỳ file nào có pin ở §0 của một card ⇒
  card đó `STALE`**, bất kể nội dung đổi có liên quan tới card hay không. Hash là hash.
- Ngoại lệ duy nhất: bảy file mà card **cố ý không pin** — sáu file của PC09
  (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`,
  `evidence/manifest.schema.json`, `evidence/index.json`) và `evidence/tools/e0_check.py`. Chúng được dẫn bằng
  đường dẫn + SC id vì PC09-FIX1 chạy song song. Đổi chúng **không** làm card STALE về mặt hash, nhưng nếu
  oracle trong `acceptance/scenarios.yaml` mâu thuẫn với §8 của card thì agent phải DỪNG và raise CR.
- Đổi stack (ADR-0006 sang Option B hoặc C) không có `INV-*` riêng vì nó không đụng hợp đồng: nó làm STALE
  **§3 và §8 của mọi card** (đường dẫn, lệnh, test path) và **không** làm STALE §2, §4, §5, §6, §7 — hợp đồng
  độc lập framework.

**STALE nghĩa là phải chạy lại, không phải FAIL.** Bằng chứng không bị ảnh hưởng thì không phải chạy lại; mỗi
`INV-*` có trường `not_invalidated_vi` nói rõ cái gì được giữ. Đó là điểm của toàn bộ cơ chế này.

## 5. Baseline của task đang chạy

SRC-PLAN §16: *"Spec mới không tự thay baseline của task đang chạy; task nhận baseline mới sau impact review.
Bản cũ vẫn giữ để audit."*

Quy trình:

1. Task đang chạy **giữ nguyên** baseline đã pin ở §0 của card. Không ai được sửa hash trong card của một
   task đang chạy.
2. Coordinator làm **impact review**: thay đổi này có chạm file nào trong §0 của card đang chạy không?
   - **Không chạm** ⇒ task chạy tiếp, ghi CR vào sổ, không làm gì thêm.
   - **Có chạm** ⇒ card chuyển `STALE`. Task dừng ở điểm an toàn gần nhất, viết handoff với những gì đã có.
3. Coordinator phát hành **card đã pin lại** (version mới của card) và một packet mới với lease mới.
4. **Bản card cũ được giữ lại** — không xóa, không ghi đè. Audit cần thấy agent đã làm việc trên baseline nào.
5. Agent nhận card mới **không** được giả định phần việc cũ vẫn đúng; §8 của card mới nói rõ bằng chứng nào
   phải chạy lại theo §4.

Agent tự phát hiện hash lệch giữa chừng: dừng, báo `STALE_BASELINE` với **cả hai** hash (đã pin và quan sát
được), **không** tự rollback — rollback cũng là một mutation cần packet mới.

## 6. Owner chấp nhận một lần cho cả phạm vi ảnh hưởng

SRC-PLAN §16: *"Thay đổi có thể được chủ dự án chấp nhận một lần cho toàn phạm vi ảnh hưởng; không tạo vòng
xin phép lặp cho từng file."*

Vì vậy đơn vị trình Owner là **impact set**, không phải file:

- Coordinator gom các CR liên quan thành một khối trong `precode/owner-decision-request.md`, kèm cột
  `affected` đã hợp nhất và bảng STALE đã tính theo §4.
- Owner trả lời **một lần** cho cả khối. Câu trả lời đó là authority cho mọi file trong `affected`.
- Không hỏi lại từng file. Nếu trong lúc thi hành phát hiện file thứ N không nằm trong `affected` đã trình,
  đó là CR mới, không phải "mở rộng nhẹ" của cái cũ.
- Owner **không** đóng blocker bằng im lặng. Trạng thái mặc định của mọi B01–B17 vẫn là `PROVISIONAL` cho tới
  khi có câu trả lời tường minh (`precode/decision-register.md`).

## 7. CR phát sinh trong Pre-code được xử lý thế nào

Các gói PC00–PC10 đã phát sinh khoảng 80 CR (`CR-PC00-01` … `CR-PC10-04`). Chúng **là đề xuất**, không phải
thay đổi đã áp dụng. Phân loại:

| Loại | Nghĩa | Ai đóng |
| --- | --- | --- |
| CR nội bộ giữa hai gói | một gói cần gói khác sửa file mà nó không được ghi | Coordinator, bằng packet FIX cho gói sở hữu |
| CR cần dữ kiện bên ngoài | phải đọc tài liệu nhà cung cấp (`CR-PC05-03` arXiv/OpenAlex, `CR-PC07-04` Telegram) | không ai đóng được trong phiên này — cần một bước có mạng; giữ `KC` |
| CR cần quyết định sản phẩm | không có mặc định an toàn (`CR-PC02-17` retention, `CR-PC07-01` tham số liên kết, loại trừ của `data.purge_all`) | **Owner**, qua `precode/owner-decision-request.md` |
| CR về chính baseline | frozen candidate lệch (`CR-PC10-01`) | Coordinator, bằng cách phát hành frozen candidate mới |

Luật bắt buộc:

- Một CR `OPEN` chạm tới card nào thì phải xuất hiện ở **§10 stop-and-report** của card đó. Không có CR nào
  được để agent phát hiện lúc đang code.
- CR loại "cần dữ kiện bên ngoài" **không** được đóng bằng cách đoán. `contracts/telegram/delivery.md` §3.4
  ghi thẳng *"Cấm suy ra giới hạn từ trí nhớ"* — đó là luật, không phải lời khuyên.
- CR đã đóng vẫn giữ trong sổ với trạng thái `CLOSED_BY_OWNER` và ngày; không xóa dòng.
- Một CR đóng bằng **ruling của Coordinator** (ví dụ wave FIX5: R5-01…R5-08) được ghi nguồn ruling ngay trong
  dòng đó. Ruling của Coordinator đóng được mâu thuẫn nội bộ giữa hai file đã đóng băng; nó **không** đóng
  được quyết định sản phẩm hay dữ kiện bên ngoài — hai loại đó vẫn phải qua Owner hoặc qua một bước có mạng.

## 8. Giữ bản cũ để audit

- Bản đã pin của nguồn nằm ở `precode/source/` và **không bao giờ** bị sửa.
- `precode/baseline.json` giữ hash của mọi file trong baseline; mỗi lần re-freeze là một bản ghi mới, không
  phải một lần ghi đè.
- Card cũ, handoff cũ và evidence manifest cũ được giữ nguyên. Bằng chứng `STALE` **không** bị xóa: nó là bằng
  chứng rằng một thứ từng đúng trên một baseline cụ thể.
- Hash phát hiện artifact bị đổi; nó **không** tự chứng minh artifact là thật (SRC-PLAN §14.1). Provenance
  thực thi và review vẫn cần thiết.

## 9. Điều tuyệt đối không làm

- Sửa `research-radar-spec.md` hoặc `research-radar-pre-code-plan.md`.
- Sửa fixture, test expectation hay oracle để implementation pass (SRC-PLAN §15).
- Ghi `CLOSED` / `ACCEPTED` cho B01–B17 khi Owner chưa trả lời.
- Cập nhật hash trong card của một task đang chạy.
- Đóng một CR `KC` bằng một con số nhớ được.
- Gọi một thay đổi là "chỉ sửa prose" khi nó đổi hành vi quan sát được.
