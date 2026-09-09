---
contract_id: CT-precode-change-control
version: 0.1.7
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

## 10. Sổ CR đã áp dụng

Mục này giữ CR **đã được thi hành**, viết đúng định dạng §1. Nó không thay `precode/review.md` §12
(sổ hợp nhất của 75 CR Pre-code); nó là nơi ghi những CR phát sinh **sau** khi một file đã
`CONTRACT_READY`, vì với chúng thì "đã áp dụng" và "đã được Owner phê chuẩn" là hai chuyện khác nhau
và phải đọc được tách bạch.

### CR-PC00-35 (gộp `F-A3-P4-02`) — `ADR-0011` nói sai về `tools/` và về phạm vi kiểm kiểu

Hai mục được xét như **một impact set** theo §6: cả hai chạm đúng một file (`precode/adr/ADR-0011-…`),
đều là **đính chính câu mô tả đã hết đúng**, và tách ra sẽ tạo hai vòng sửa cho cùng một phạm vi.

```yaml
cr_id: CR-PC00-35             # gộp F-A3-P4-02 (cùng impact set: một file, một loại sửa)
raised_by: >
  CR-PC00-35 do worker-W1n tự phát hiện tại PKT-PC00-FIX30 — phép kiểm hai chiều dựng ở PKT-PC00-FIX17
  (so câu trong ADR với thực tế trên đĩa) TỰ ĐỎ khi tools/backup_cli.py xuất hiện.
  F-A3-P4-02 do audit A3-P4-R1 nêu (MEDIUM).
addressed_to: PC00 (chủ precode/adr/ADR-0011-frameworks-and-toolchain.md)
status: APPLIED               # đã thi hành ở PKT-PC00-FIX32, 2026-09-08
authority: AUTH-OWNER-20260908-11 (OD-20260908-10) → ruling post-A3-P4-R1
source_of_change: >
  Hai câu trong ADR-0011 đúng khi viết và hết đúng về sau. (1) Hàng "Lint / format" ghi
  `mypy --strict` cho "lõi server"; cấu hình làm ĐÚNG THEO CÂU ẤY (files = ["server/app"]),
  nên 23 file sản phẩm ở worker/app, collector/app, probe/ không được thứ gì kiểm kiểu — một
  câu mơ hồ trong ADR trở thành một lỗ thật trong CI. (2) Ghi chú "Sự kiện Giai đoạn 0" nói
  "tools/ chưa được tạo"; card TC-backup-restore-drill đã tạo tools/backup_cli.py ngày 2026-09-08.
before: >
  "mypy --strict cho lõi server"; "tools/ chưa được tạo — nó nằm ngoài write set của gói đó".
after: >
  "mypy --strict trên MỌI cây mã sản phẩm Python — server/app, worker/app, collector/app, probe";
  ghi chú tools/ được đánh dấu đã hết đúng, trỏ tới khối Amendment AMD-ADR0011-01.
  Thêm: .gitignore nay phủ __pycache__/ (worker-WS).
impact: >
  ADR-0011 là file CARD-PINNED và nằm trong read set của mọi task card ⇒ 19 card chuyển STALE theo
  INV-06; worker-WP re-pin epoch P4b sau khi W1n nhả lease. KHÔNG file contracts/ hay acceptance/
  nào đổi. Status ADR giữ accepted; ratified_by: OD-20260907-02 KHÔNG đổi — không lựa chọn kỹ
  thuật nào bị sửa.
verification: >
  E0 (e0_check.py) chạy chỉ đọc sau khi sửa; assertion hai chiều tools/↔ADR trong validate.py của
  PC00 chuyển từ ĐỎ về XANH mà KHÔNG bị nới lỏng. Việc phạm vi mypy mới CHẠY SẠCH thì thuộc
  addendum P0-FIX4 của worker-WS và lượt xác minh A3-P4-R2 — KHÔNG được suy ra từ file này.
not_done_here: >
  Không đóng F-A3-P4-02 (vòng đời protocol.md §8); không sửa cấu hình mypy hay .gitignore (của WS);
  không nâng trần claim của file nào.
```

### CR-TC-AUTH-02 (gộp CR-TC-AUTH-03) — `ENT-owner` nhận cột credential và lockout

Hai CR được xét như **một impact set** theo §6: chúng chạm đúng một entity, đúng một file hợp đồng và
đúng một migration; tách ra sẽ tạo hai vòng xin phép cho cùng một phạm vi ảnh hưởng — đúng điều §6 cấm.

```yaml
cr_id: CR-TC-AUTH-02          # gộp CR-TC-AUTH-03 (cùng impact set)
raised_by: TC-owner-auth-session (Worker của card), xác nhận bởi audit A3-R1 (F-A3R1-02, F-A3R1-06)
addressed_to: PC02 (chủ hợp đồng contracts/data/entities.yaml)
status: ACCEPTED              # OD-20260907-03 mục 1 (vòng ba, 2026-09-07); trước đó PROVISIONAL từ PKT-PC02-FIX12
ratified_by: OD-20260907-03   # authority AUTH-OWNER-20260907-04; evidence session_0156UBBHDSeC9soECzSVUb3U
source_of_change: >
  Mâu thuẫn nội bộ giữa hai file đã đóng băng: contracts/ops/secrets.md §2.1-§2.3 bắt buộc một
  tài khoản owner có mật khẩu băm Argon2id và lockout 5 lần / 15 phút, còn
  contracts/data/entities.yaml ENT-owner không khai chỗ nào để lưu hai thứ đó. Audit A3-R1 xác
  nhận: password_hash và password_updated_at là HAI cột duy nhất trong toàn bộ database mà
  không entity nào khai.
before: >
  contracts/data/entities.yaml v0.1.0, ENT-owner, mục `fields` — đúng năm dòng:
  `{name: id ...}`, `{name: singleton_guard ...}`, `{name: display_name ...}`,
  `{name: timezone_iana ...}`, `{name: created_at, type: timestamp_utc_ms, nullable: false,
  constraints: "Giờ server."}`. Không có dòng nào cho credential hay lockout.
after: >
  Thêm đúng bốn trường vào cùng mục `fields`, sau `created_at`, không sửa một chữ nào của năm
  trường cũ: `password_hash` (string, nullable, chuỗi encoded Argon2id dạng PHC, NULL cho tới khi
  bootstrap, không read model nào được trả về); `password_updated_at` (timestamp_utc_ms, nullable);
  `failed_login_count` (integer, NOT NULL, DEFAULT 0); `locked_until` (timestamp_utc_ms, nullable).
  Version của file 0.1.0 -> 0.2.0. Amendment `AMD-ENT-owner-01` ghi tại mục 0b của chính file đó.
  Căn cứ bậc version: xem `version_rule` và `deviation` dưới đây — KHÔNG phải một hàng §2 duy nhất.
version_rule: >
  Sửa theo F-A3R2-01 (bản đầu của mục này dẫn một khóa quy tắc không tồn tại). Ba cột nullable
  rơi đúng hàng minor của §2, nguyên văn: "Thêm trường **optional**, thêm mã lỗi mới, thêm
  operation mới | minor (`0.1.0 → 0.2.0`)". Cột thứ tư, `failed_login_count`, là NOT NULL kèm
  DEFAULT hằng số và KHÔNG có hàng nào của §2 phủ nó: hàng major thứ nhất nguyên văn là
  "Đổi/xóa trường bắt buộc, đổi enum, đổi ngữ nghĩa, đổi `auth_scope`, đổi `idempotency` key,
  đổi commit point" — đây là THÊM một trường mới, không phải đổi hay xóa một trường bắt buộc đang
  tồn tại; hàng major thứ hai là "Đổi `transaction` / `commit_point` / invariant" — không đụng;
  hàng patch là "Sửa lỗi chính tả, làm rõ prose, không đổi hành vi" — quá nhẹ. Vậy §2 không cho
  phép và cũng không cấm: nó có một khoảng trống. Cột đó được xử lý là additive trên căn cứ
  `migration` dưới đây (DEFAULT hằng số, không backfill, đúng một hàng owner đang tồn tại), không
  trên căn cứ một hàng quy tắc.
deviation:
  deviation_from: "§2 của chính file này — khoảng trống: không có hàng nào cho việc thêm một cột NOT NULL có DEFAULT hằng số"
  authority: AUTH-COORD-PC02-FIX13            # cha AUTH-OWNER-20260907-03
  ruling: "GIỮ entities.yaml ở 0.2.0; KHÔNG bump lại. Bump lần nữa làm mọi card vừa re-pin STALE thêm một vòng để sửa một lỗi TRÍCH DẪN, trong khi thay đổi thực chất của schema không đổi."
  change_request: CR-PC10-13                  # xem khối CR thứ hai của mục này
reason: >
  `before` không đủ, không phải sai: entity duy nhất có thể giữ credential của một hệ một người
  dùng (REQ-D05: một tài khoản, không signup, không quên-mật-khẩu tự động) lại không có trường nào
  giữ nó. Hệ quả đo được: card đã ship hai cột mà hợp đồng không khai, nên entities.yaml thôi là
  thẩm quyền của schema đang chạy (F-A3R1-02); và lockout phải sống trong bộ nhớ tiến trình, nên
  khởi động lại server xóa sạch bộ đếm mà secrets.md §2.3 bắt buộc (F-A3R1-06).
affected:
  requirements: [REQ-D05, REQ-S11.1-01, REQ-P0-01]
  contracts:
    - contracts/data/entities.yaml   # 0.1.0 -> 0.2.0
    - contracts/ops/secrets.md       # không đổi; là nguồn của thay đổi này
  modules:      [MOD-auth-service, MOD-data-store]
  generated: []                      # sửa theo F-A3R2-04: entities.yaml KHÔNG phải nguồn của bộ sinh
  reaches_code_through:              # amendment với entity tới code bằng đúng hai đường, cả hai viết tay
    - server/migrations/versions/0002_base_entities.py            # DDL: nơi DUY NHẤT tạo owner
    - tests/contract/test_schema_matches_entities.py              # kiểm thường trực sau alembic upgrade head
  migrations:
    - server/migrations/versions/0002_tc_owner_auth_session.py   # bỏ CREATE TABLE owner, phụ thuộc 0002_base_entities
    - server/migrations/versions/0002_base_entities.py           # nơi DUY NHẤT tạo owner, gồm bốn cột mới (F-A3R1-01)
  fixtures: []                       # không fixture nào nêu tên cột của owner
  task_cards:
    rule: "§4 INV-06/INV-09 — mọi card pin hash contracts/data/entities.yaml chuyển STALE. Hash là hash."
    action: "PC10 (W7/WP) re-pin trong đợt pin kế tiếp; card STALE nghĩa là chạy lại, không phải FAIL."
  evidence: [EV-PC02-01, EV-PC02-03, EV-PC02-08]   # STALE: chạy lại trên epoch mới (đã chạy lại trong packet này)
migration: >
  Dữ liệu: không cần chuyển đổi. Ba cột nullable nhận NULL; failed_login_count là NOT NULL DEFAULT 0
  nên hàng owner đang có nhận 0 mà không cần backfill. Đường lùi: nếu Owner phản đối, gỡ bốn cột và
  chỉ định entity khác giữ credential — lúc đó là thay đổi major kèm migration thật, vì cột đã có dữ liệu.
```

**Thẩm quyền và giới hạn của nó.** Thay đổi này được thi hành bằng **amendment kỹ thuật của
Coordinator** (`AUTH-COORD-PC02-FIX12`, cha `AUTH-OWNER-20260907-03`), không bằng một biên bản Owner.
Căn cứ: nó làm hợp đồng khớp với `contracts/ops/secrets.md` mà Owner **đã** chấp nhận
(`PROV-PC08-01`), nên nó không thêm quyết định sản phẩm mới — đúng loại mâu thuẫn nội bộ mà §7 nói
ruling của Coordinator đóng được. Ba điều nó **không** làm: nó không mang nhãn
`ACCEPTED (OD-20260907-01)` (biên bản đó không nhắc bốn cột này); nó không đóng `F-A3R1-02` hay
`F-A3R1-06`; và nó không tự chứng minh schema đang chạy đã khớp — điều đó do revision Alembic base
`0002_base_entities` và test hợp đồng `tests/contract/test_schema_matches_entities.py` chứng minh.
**Cập nhật `OD-20260907-03` (vòng ba, 2026-09-07): Owner đã phê chuẩn.** Mục 1 của biên bản
(`AUTH-OWNER-20260907-04`, evidence `session_0156UBBHDSeC9soECzSVUb3U`) phê chuẩn `AMD-ENT-owner-01`;
CR này chuyển `PROVISIONAL` → `ACCEPTED (OD-20260907-03)`. Hệ quả: bốn cột nay đứng trên quyết định của
Owner chứ không trên chữ ký kỹ thuật của Coordinator, và nhãn của card `TC-owner-auth-session` không
còn tựa vào một hợp đồng PROVISIONAL. Câu cũ — "Owner phải được trình mục này ở vòng quyết định kế
tiếp và **có thể phản đối**" — được giữ lại ở đây làm lịch sử: điều kiện ấy có thật từ
`PKT-PC02-FIX12` tới biên bản vòng ba, và nó hết hiệu lực vì Owner **đã trả lời**, không vì ai đó xóa
nó đi. `OD-20260907-01` vẫn không nhắc bốn cột này; thẩm quyền phê chuẩn chúng là `OD-20260907-03`.

**Hai điều biên bản vòng ba KHÔNG làm.** Nó không đóng `F-A3R1-02` hay `F-A3R1-06` (finding theo vòng
đời riêng của `protocol.md` §8), và nó không trả lời `CR-PC10-13` — khoảng trống của §2 vẫn còn, nên
khối `deviation` ở trên vẫn là căn cứ bậc version cho tới khi PC10 sửa §2.

**Sửa theo `F-A3R2-04`: không có bước "sinh lại" nào ở đây.** Bản đầu của mục này xếp
`shared/rr_contracts` vào `affected.generated` với ghi chú "PHẢI sinh lại". Sai:
`contracts/data/entities.yaml` **không** nằm trong manifest nguồn của `shared/rr_contracts`
(mười lăm nguồn: bảy schema JSON, năm state machine, `errors.yaml`, `ports.yaml`, `openapi.yaml`)
cũng không nằm trong manifest của `web/src/generated` (một nguồn: `openapi.yaml`).
`shared/rr_contracts/generate.py` nói thẳng rằng một amendment với entity "correctly produces no
diff here". Đó là chủ ý, đã ghi thành `CR-P0-06`: hình dạng bảng sống ở ba nơi — hợp đồng,
migration, test — và chỉ cặp migration ↔ test được máy so khớp, nên hợp đồng ↔ migration chỉ được
chứng minh **gián tiếp**. Ghi ra để người đọc sau không kết luận rằng cây model sinh bám theo
`entities.yaml`; nó không bám.

### CR-PC10-13 — §2 thiếu hàng cho cột NOT NULL có DEFAULT hằng số

```yaml
cr_id: CR-PC10-13
raised_by: worker-W3n (PKT-PC02-FIX13), theo finding F-A3R2-01 của audit A3-R2
addressed_to: PC10 (chủ file precode/change-control.md)
status: OPEN
source_of_change: >
  Mâu thuẫn nội bộ: một amendment có thật (AMD-ENT-owner-01) thêm một cột NOT NULL kèm DEFAULT
  hằng số, và §2 không có hàng nào phủ trường hợp đó. Người viết buộc phải hoặc dẫn sai một luật,
  hoặc khai deviation. Bản này khai deviation; lần sau sẽ có người dẫn sai.
before: >
  §2, hàng minor, nguyên văn: "| Thêm trường **optional**, thêm mã lỗi mới, thêm operation mới |
  minor (`0.1.0 → 0.2.0`) | cập nhật `consumers`, thêm scenario, thêm fixture |". Ba hàng còn lại
  nói về patch, về "Đổi/xóa trường bắt buộc..." và về "Đổi `transaction` / `commit_point` /
  invariant". Không hàng nào nói tới việc THÊM một trường bắt buộc.
after: >
  Thêm một hàng minor: "Thêm trường bắt buộc kèm DEFAULT hằng số (không cần backfill, consumer cũ
  không đọc cột chưa từng có)" — hoặc, nếu PC10 muốn chặt hơn, ghi thẳng rằng trường hợp này là
  major và nêu lý do; điều quan trọng là §2 phải TRẢ LỜI, không để trống.
reason: >
  Một quy trình version có khoảng trống ở đúng trường hợp phổ biến nhất của migration additive sẽ
  đẩy mọi người viết vào việc dẫn sai luật. F-A3R2-01 là ca đầu tiên; nó được phát hiện vì auditor
  grep khóa quy tắc, không phải vì quy trình tự bắt.
affected:
  requirements: []
  contracts: [precode/change-control.md]      # §2, bản kế tiếp
  modules:   []
  fixtures:  []
  evidence:  []                                # không bằng chứng nào phụ thuộc câu chữ §2
migration: >
  Không cần. Khi §2 có hàng mới, khối `deviation` của CR-TC-AUTH-02 ở trên được thay bằng một trích
  dẫn hàng đó; entities.yaml GIỮ NGUYÊN 0.2.0 — bậc version đã chọn không đổi, chỉ căn cứ đổi.
```

### CR-PC03-08 — `research_connector_rate_limit` nhận nửa arXiv của `REQ-A6` từ tài liệu chính thức

```yaml
cr_id: CR-PC03-08
raised_by: worker-WF (PKT-PC03-FIX-REQA6), dưới AUTH-COORD-REQA6 (cha AUTH-OWNER-20260907-05)
addressed_to: PC03 (chủ hợp đồng contracts/retry-policy.yaml)
status: ACCEPTED              # OD-20260907-04 mục 2 cấp quyền ĐI LẤY dữ kiện; nội dung là dữ kiện ngoài, không phải quyết định sản phẩm
ratified_by: OD-20260907-04   # authority AUTH-OWNER-20260907-05; ghi ở precode/decision-register.md §8.13.1
source_of_change: >
  Nguồn ngoài. OD-20260907-04 mục 2 cấp một quyền mạng MỘT LẦN, HẸP, CHỈ ĐỌC trang tài liệu dưới
  arxiv.org / info.arxiv.org / openalex.org / docs.openalex.org, để đọc và trích nguyên văn chính
  sách nhịp gọi và định danh của hai nguồn. Không một lời gọi API thật nào được phép, và không một
  lời gọi nào đã xảy ra: công cụ duy nhất dùng là WebFetch (GET) trên trang tài liệu.
before: >
  contracts/retry-policy.yaml v0.6.0, budgets.research_connector_rate_limit, nguyên văn dòng values:
  `values: {arxiv_requests_per_window: null, arxiv_window_seconds: null, openalex_requests_per_window:
  null, openalex_window_seconds: null, min_interval_ms: 3000}` với `status: PLACEHOLDER_KC`. Bốn giá
  trị null; không có khối trích dẫn nguồn nào; yêu cầu định danh của cả hai nguồn không được ghi ở đâu
  trong file.
after: >
  Cùng khối, v0.7.0. HAI giá trị arXiv được điền từ tài liệu chính thức: `arxiv_requests_per_window: 1`,
  `arxiv_window_seconds: 3`, cộng một khóa MỚI `arxiv_max_concurrent_connections: 1` — dữ kiện thứ ba
  nằm trong cùng câu trích dẫn và sàn cũ không phủ. Hai giá trị OpenAlex GIỮ `null`. Thêm ba khóa mô tả:
  `sources` (hai bản ghi có url + retrieved_at 2026-09-07 + trích dẫn nguyên văn tiếng Anh),
  `identification` (`arxiv_identification_required: false`, `openalex_identification_required: null`,
  cùng luật "nguồn yêu cầu định danh mà chưa có chuỗi định danh ⇒ KHÔNG gọi"), và `unresolved_vi`
  (nêu chính xác hai giá trị còn thiếu và lý do). `status` GIỮ `PLACEHOLDER_KC`; `min_interval_ms = 3000`
  GIỮ NGUYÊN. Văn xuôi `scope` và `ratification.still_kc_vi` sửa "bốn giá trị" thành "hai", nêu rõ câu
  cũ viết ở thì của OD-20260907-01.
version_rule: >
  §2, hàng minor, nguyên văn: "Thêm trường **optional**, thêm mã lỗi mới, thêm operation mới | minor
  (`0.1.0 → 0.2.0`)". Ba khóa `sources` / `identification` / `unresolved_vi` là trường optional mới; việc
  điền hai giá trị đang `null` KHÔNG đổi enum, semantics, auth_scope, idempotency key hay commit point —
  không hàng major nào phủ nó — và nặng hơn "sửa lỗi chính tả, làm rõ prose, không đổi hành vi" của hàng
  patch, vì hành vi khởi động của connector với nguồn arXiv có đổi. Vậy: 0.6.0 -> 0.7.0. KHÔNG cần khai
  deviation ở đây (khác CR-TC-AUTH-02): khoảng trống CR-PC10-13 nói về cột NOT NULL có DEFAULT, không
  chạm trường hợp này.
reason: >
  `before` không sai, nó THIẾU — và nó thiếu đúng thứ chặn card connector rời DRAFT. Bốn giá trị null là
  trạng thái đúng khi chưa ai được phép đọc tài liệu; sau OD-20260907-04 mục 2 thì hai trong bốn đọc được,
  và giữ chúng null sẽ là bỏ phí một dữ kiện đã có trích dẫn. Ba lý do phải ghi kèm nguồn thay vì chỉ ghi
  số: (a) SRC-PLAN §14.1 đòi provenance; (b) một con số rate limit không có URL và ngày đọc thì lần sau
  không ai kiểm được nó còn đúng không; (c) chính điều SG-A6 cấm — đoán số — chỉ phân biệt được với đọc số
  bằng trích dẫn.
affected:
  requirements: [REQ-A6, REQ-D34]     # REQ-A6 chuyển KC -> PARTIALLY_RESOLVED; REQ-D34 (định danh) nửa arXiv đã có câu trả lời
  contracts:
    - contracts/retry-policy.yaml     # 0.6.0 -> 0.7.0
  modules: [MOD-research-connector]
  fixtures: []                        # không fixture nào nêu số nhịp gọi
  task_cards:
    rule: "§4 INV-06/INV-09 — mọi card pin hash contracts/retry-policy.yaml chuyển STALE. Hash là hash."
    action: >
      Coordinator re-pin trong đợt pin kế tiếp. Worker của packet này CỐ Ý KHÔNG chạm card nào
      (agent-tasks/* nằm ngoài lease LEASE-PC03-REQA6). Card STALE nghĩa là pin lại, không phải FAIL.
    still_blocking: >
      SG-A6 của agent-tasks/TC-research-connector-metadata.md KHÔNG được nới bởi CR này: nó đòi BỐN giá
      trị, và openalex_requests_per_window / openalex_window_seconds vẫn null. Connector vẫn từ chối
      khởi động, và MOD-research-connector vẫn KHÔNG CONTRACT_READY.
  evidence: [EV-PC03-05]              # STALE: lint của PC03 chạy trên bytes cũ; chạy lại trên epoch mới
still_open: >
  Nửa OpenAlex DỪNG ở BLOCKED_SCOPE, không phải ở "chưa tìm thấy". Ngày 2026-09-07 mọi đường dẫn thử dưới
  docs.openalex.org (rate-limits-and-authentication, api-overview, và trang gốc) trả 301 sang
  https://help.openalex.org/ — host KHÔNG có trong bốn host được cấp — và openalex.org trả 403. Đi theo
  redirect ra ngoài allowlist là tự mở scope (protocol.md §3). Cần một amendment quyền thêm
  help.openalex.org; cho tới lúc đó hai giá trị GIỮ null. Không con số nào được suy ra từ thông lệ.
migration: >
  Không cần chuyển đổi dữ liệu. Cấu hình runtime: `min_interval_ms = 3000` giữ nguyên nên hành vi mặc
  định của connector không đổi; ba khóa arXiv mới chỉ SIẾT thêm (thêm giới hạn một kết nối đồng thời).
  Đường lùi: nếu arXiv đổi chính sách, sửa đúng khối `sources` kèm ngày đọc mới — không xoá bản ghi cũ,
  vì nó là bằng chứng rằng một hạn mức từng đúng vào một ngày cụ thể (§8).
```

**Thẩm quyền và giới hạn.** CR này KHÔNG phải một quyết định sản phẩm: Owner cấp **quyền đi lấy** dữ kiện,
không cấp nội dung. Cái được chấp nhận ở `status: ACCEPTED` là *quy trình* (đọc tài liệu chính thức, ghi
kèm URL/ngày/trích dẫn), còn *nội dung* đứng trên chính trang tài liệu, không trên chữ ký của ai. Hệ quả
thực tế: nếu ai đó đọc lại `https://info.arxiv.org/help/api/tou.html` và thấy khác, đây là một CR mới, không
phải một lần "Owner đổi ý". Ba điều CR này **không** làm: không đóng `REQ-A6` (`precode/requirements.csv`
ngoài lease và vẫn ghi `KC`), không nới `SG-A6`, và không nâng trần claim của module research connector.
Dữ kiện `arxiv_identification_required = false` là một **phủ định có phạm vi** — "bốn trang đã đọc ngày
2026-09-07 không yêu cầu định danh" — chứ không phải "gọi ẩn danh là đúng"; luật `SG-IDENT` không đổi.

#### Bổ sung `CR-PC03-08.a` — nửa OpenAlex, sau khi Owner mở rộng allowlist (2026-09-07, cùng ngày)

Bổ sung **cộng thêm**, không viết lại khối trên: khối ấy ghi đúng trạng thái sau vòng một, và một sổ CR
mà mục cũ bị sửa cho khớp kết quả mới thì không còn là sổ. Đọc hai mục theo thứ tự.

```yaml
cr_id: CR-PC03-08.a           # bổ sung của CR-PC03-08; KHÔNG thay thế nó
raised_by: worker-WF (PKT-PC03-FIX-REQA6 phần 2), dưới AUTH-COORD-REQA6 / LEASE-PC03-REQA6-p2
addressed_to: PC03 (chủ hợp đồng contracts/retry-policy.yaml)
status: ACCEPTED
ratified_by: OD-20260907-04   # cùng biên bản; Owner MỞ RỘNG allowlist đọc tài liệu thêm help.openalex.org
source_of_change: >
  Nguồn ngoài, lần hai. CR-PC03-08 dừng nửa OpenAlex ở BLOCKED_SCOPE vì mọi trang tài liệu OpenAlex
  redirect sang help.openalex.org, một host ngoài bốn host được cấp. Coordinator trình Owner đúng sự
  kiện đó; Owner trả lời "thêm help.openalex.org vào allowlist". Quyền thành NĂM host, mọi hạn chế
  khác giữ nguyên: chỉ trang tài liệu, chỉ GET, và api.openalex.org / export.arxiv.org vẫn cấm.
before: >
  contracts/retry-policy.yaml v0.7.0, budgets.research_connector_rate_limit, nguyên văn:
  `status: PLACEHOLDER_KC`, `values: {... openalex_requests_per_window: null, openalex_window_seconds:
  null, min_interval_ms: 3000}`, `identification.openalex_identification_required: null`, cộng một khóa
  `unresolved_vi` nêu lý do hai giá trị còn trống.
after: >
  Cùng khối, v0.8.0. `openalex_requests_per_window: 100`, `openalex_window_seconds: 1`,
  `identification.openalex_identification_required: false` cộng `openalex_api_key_optional: true`.
  `status` chuyển PLACEHOLDER_KC -> `DOCS_derived` (token MỚI, giải thích tại `status_note_vi`).
  `sources` nhận ba bản ghi nữa: A6-OPENALEX-RATE, A6-OPENALEX-BUDGET (RESOLVED_NON_NUMERIC — ngân sách
  ngày nêu bằng TIỀN, cố ý không thành số), A6-OPENALEX-IDENT. `unresolved_vi` -> `resolved_vi`;
  `blocked_scope_vi` -> `scope_note_vi`; thêm `expiry_vi`. `min_interval_ms = 3000` GIỮ NGUYÊN.
  Ngoài khối: `scope`, `principles.RP-05` và `ratification.still_kc_vi` sửa cho khớp — RP-05 nay khai
  mức thứ TƯ (`DOCS_derived`) bên cạnh ba mức cũ.
version_rule: >
  §2, hàng minor, như CR-PC03-08: thêm trường optional (`status_note_vi`, `expiry_vi`, `scope_note_vi`,
  ba bản ghi `sources`) và điền giá trị đang null. KHÔNG đổi enum/semantics/auth_scope/idempotency/commit
  point ⇒ không phải major. 0.7.0 -> 0.8.0.
  LƯU Ý MỘT CÁI GIÁ ĐÃ CHỌN: hai lần sửa trong cùng một ngày ⇒ hai lần bump ⇒ hai vòng STALE cho mọi card
  pin file này. Gộp lại thành một bump sẽ rẻ hơn cho Coordinator nhưng sẽ xoá mất một sự thật kiểm toán
  được: nửa arXiv và nửa OpenAlex đứng trên HAI phạm vi quyền khác nhau, cách nhau bởi một câu trả lời
  của Owner. Sổ này chọn giữ sự thật đó.
reason: >
  `before` không sai, nó bị CHẶN — và cái chặn nó là ranh giới quyền, không phải thiếu nguồn. Khi Owner
  gỡ đúng cái ranh giới ấy, giữ hai giá trị null sẽ là để một cổng (SG-A6) chặn vì một lý do đã hết tồn
  tại. Ba điều đáng ghi từ lần đọc này: (a) hình dạng hạn mức của OpenAlex KHÁC arXiv — hai tầng, nhịp
  giây cộng ngân sách ngày; (b) ngân sách ngày nêu bằng tiền nên KHÔNG có con số lời gọi để điền, và ép
  nó thành số sẽ là bịa; (c) quy ước polite pool / mailto mà REQ-D34 giả định KHÔNG còn trong tài liệu
  hiện hành.
affected:
  requirements: [REQ-A6, REQ-D34]     # REQ-A6: PARTIALLY_RESOLVED -> RESOLVED. REQ-D34: giả định mailto của nó không còn khớp tài liệu
  contracts:
    - contracts/retry-policy.yaml     # 0.7.0 -> 0.8.0
  modules: [MOD-research-connector]
  fixtures: []
  task_cards:
    rule: "§4 INV-06/INV-09 — vòng STALE thứ hai cho mọi card pin contracts/retry-policy.yaml."
    action: "Coordinator pin lại MỘT lần trên bytes cuối (0.8.0), không cần pin trung gian 0.7.0."
    sg_a6: >
      Điều kiện của SG-A6 — "bốn giá trị PLACEHOLDER_KC còn null" — KHÔNG CÒN ĐÚNG. Đây là một phát
      biểu về ĐIỀU KIỆN của cổng, KHÔNG phải một tuyên bố rằng MOD-research-connector đã
      CONTRACT_READY: trần claim của module do PC05/Coordinator xét trên toàn bộ cổng của nó. Worker
      của packet này không chạm card nào và không tuyên bố điều đó.
    sg_ident: >
      SG-IDENT GIỮ NGUYÊN trong card và trong code. Đổi là DỮ KIỆN nó áp lên (không nguồn nào đòi định
      danh tính tới 2026-09-07), không phải luật. Xoá luật vì hôm nay nó không kích hoạt là đúng thứ
      §9 cấm.
  evidence: [EV-PC03-05]              # STALE lần nữa; chạy lại trên bytes 0.8.0
migration: >
  Không cần chuyển đổi dữ liệu. Hành vi mặc định không đổi: min_interval_ms = 3000 vẫn là ràng buộc chặt
  nhất — chậm hơn hạn mức OpenAlex (100 req/s) khoảng 300 lần, và điều đó là CÓ CHỦ ĐÍCH cho một hệ một
  người dùng. Đường lùi: nếu một nguồn đổi chính sách, sửa đúng bản ghi trong `sources` kèm ngày đọc mới
  và mở CR; KHÔNG chỉnh con số tại chỗ, và KHÔNG xoá bản ghi cũ (§8).
```

**Vì sao đây vẫn không phải một quyết định sản phẩm.** Owner quyết **phạm vi quyền đọc**, không quyết con
số. Cái `status: ACCEPTED` ở trên nói rằng *quy trình* được chấp nhận, còn nội dung đứng trên trang tài
liệu của arXiv và OpenAlex. `DOCS_derived` được đặt ra chính để giữ sự khác biệt ấy đọc được: nó
mang một **ngày hết hạn ngầm**, và ai đọc lại nguồn thấy khác thì mở CR mới — không phải "Owner đổi ý".
Hai giới hạn phải đọc kèm: dữ kiện định danh của cả hai nguồn là **phủ định có phạm vi** (các trang đã
đọc trong ngày 2026-09-07, không phải toàn bộ site), và ngân sách ngày của OpenAlex **không** có con số
trong hợp đồng vì tài liệu không nêu con số — nó chỉ quan sát được lúc chạy qua header `X-RateLimit-*`.

### CR-PC07-04 — `telegram/delivery.md` §3.4 nhận HAI trong NĂM giới hạn từ tài liệu chính thức

Mục này ghi **một lần áp dụng một phần**, không phải một lần đóng. `CR-PC07-04` do PC07 phát ra
(`evidence/handoffs/PC07-handoff.md` §"CR"), và nó **vẫn mở**.

```yaml
cr_id: CR-PC07-04             # lần áp dụng thứ nhất; CR KHÔNG đóng
raised_by: PC07 (nguyên bản); lần áp dụng này do worker-WT (PKT-PC07-FIX-TELEGRAM), dưới AUTH-COORD-TELEGRAM-FACTS (cha AUTH-OWNER-20260908-06)
addressed_to: PC07 (chủ hợp đồng contracts/telegram/delivery.md) và Coordinator (các file ngoài lease ở "still_open")
status: PROVISIONAL           # hai dữ kiện có nguồn; ba dữ kiện BLOCKED_DEPENDENCY. KHÔNG phải CLOSED_BY_OWNER
ratified_by: OD-20260908-05   # authority AUTH-OWNER-20260908-06, mục 2; ghi ở precode/decision-register.md §8.14
source_of_change: >
  Nguồn ngoài. OD-20260908-05 mục 2 cấp một quyền mạng MỘT LẦN, HẸP, CHỈ ĐỌC trang tài liệu dưới
  core.telegram.org, để đọc và trích nguyên văn năm giới hạn định dạng của Bot API. Cấm gọi
  api.telegram.org, cấm dùng bot token, cấm gửi bất cứ thứ gì. Công cụ duy nhất dùng là WebFetch (GET).
  Không một lời gọi API thật nào được phép, và không một lời gọi nào đã xảy ra.
before: >
  contracts/telegram/delivery.md §3.4, tiêu đề nguyên văn "### 3.4 Giới hạn định dạng — `KC`", bảng năm
  hàng với cột Trạng thái ghi `KC` cho cả năm ("Độ dài tối đa một tin", "Độ dài callback data" kèm
  "(PROVISIONAL 64 byte)", "Parse mode và tập ký tự phải escape", "Số nút mỗi hàng / mỗi bàn phím",
  "Rate limit gửi"), và đoạn kết nguyên văn: "**Chưa đọc trong gói này** — không có mạng (baseline §3).
  Mọi số ở trên là giả định cho tới khi có người đọc tài liệu thật và ghi lại". Không URL nào có ngày đọc,
  không câu trích nào.
after: >
  Cùng mục, tiêu đề đổi thành "### 3.4 Giới hạn định dạng — hai dòng ĐÃ ĐỌC, ba dòng còn `KC`". Bảng nhận
  hai cột mới (Giá trị, Nguồn) và hai hàng rời `KC`: "Độ dài tối đa một tin" -> `DOCS_derived`, 4096 ký tự,
  trích `/bots/tutorial`; "Rate limit gửi" -> `DOCS_derived`, 1 tin/giây trong một chat + 20 tin/phút trong
  một group + ~30 tin/giây khi broadcast, trích `/bots/faq`. BA hàng còn lại GIỮ `KC` và nhận nhãn
  BLOCKED_DEPENDENCY. Thêm bốn khối văn xuôi: ba câu rate limit nguyên văn kèm câu "đây là trần lập kế hoạch,
  Retry-After thắng"; "Ba điều con số 4096 KHÔNG nói" (nguồn thứ cấp; đếm trên chuỗi thô đã escape; đơn vị
  đếm chưa có nguồn); "Ba dòng còn KC — BLOCKED_DEPENDENCY" kèm 12 URL đã thử; và một đoạn hệ quả giữ nguyên
  điều cấm suy ra từ trí nhớ cho ba dòng ấy.
reason: >
  `before` không sai, nó THIẾU — và nó thiếu đúng thứ chặn cứng MOD-telegram-adapter cùng nhánh multipart
  của §3.5. Câu "không có mạng (baseline §3)" mô tả đúng phiên Pre-code, và OD-20260908-05 mục 2 đã gỡ
  đúng điều kiện ấy; giữ nguyên năm dòng `KC` sau khi hai dòng đã có câu trích sẽ là bỏ phí dữ kiện. Ba lý
  do phải ghi kèm URL + ngày + trích dẫn thay vì chỉ ghi số, giống CR-PC03-08: (a) SRC-PLAN §14.1 đòi
  provenance; (b) một giới hạn không có URL và ngày đọc thì lần sau không ai kiểm được nó còn đúng không;
  (c) chính điều §9 hàng 12 cấm — suy ra giới hạn từ trí nhớ — chỉ phân biệt được với đọc số bằng trích dẫn.
version_rule: >
  §2 hàng minor phủ thay đổi này (thêm thông tin, không đổi enum/semantics/auth_scope/idempotency/commit
  point): contracts/telegram/delivery.md 0.1.0 -> 0.2.0. BUMP NÀY CHƯA ĐƯỢC ÁP DỤNG. Trường `version` nằm
  ở front matter, NGOÀI vùng §3.4 được cấp trong LEASE-PC07-TELEGRAM; Worker không ghi ngoài vùng chỉ vì
  luật version tiện hơn (worker.md điều 1). Đây là một việc còn lại của chủ file, ghi ở "still_open".
  Bytes của file ĐÃ đổi, nên §5 vẫn áp: mọi card pin hash file này chuyển STALE bất kể version chưa bump.
affected:
  requirements: [REQ-AC14, REQ-S5.3-02]   # nhánh multipart; REQ-A6 áp cho Telegram = PARTIALLY_RESOLVED
  contracts:
    - contracts/telegram/delivery.md      # 0.1.0 (bump 0.2.0 CHƯA áp dụng — xem version_rule)
  modules: [MOD-telegram-adapter, MOD-delivery-service]
  fixtures: []                            # không fixture nào nêu một giới hạn định dạng bằng số
  task_cards:
    rule: "§5 — mọi card pin hash contracts/telegram/delivery.md chuyển STALE. Hash là hash."
    action: >
      Coordinator re-pin trong đợt pin kế tiếp. Worker của packet này CỐ Ý KHÔNG chạm card nào
      (agent-tasks/* nằm ngoài LEASE-PC07-TELEGRAM). Card STALE nghĩa là pin lại, không phải FAIL.
    still_blocking: >
      SG-01 của agent-tasks/TC-telegram-unknown-delivery.md và của TC-telegram-linking-auth.md KHÔNG
      được nới bởi CR này. Nhánh multipart cần CHỖ CẮT; chỗ cắt cần parse mode (để đếm ký tự escape) và
      bố cục nút — hai thứ vẫn KC. 4096 một mình không đủ để cắt.
  evidence: []                            # E0 chạy lại sau khi sửa: PASS 25 / violations 0
still_open: >
  BA việc, tất cả NGOÀI lease của packet này và tất cả cần một packet khác:
  (1) contracts/telegram/delivery.md front matter — `version: 0.1.0` chưa bump, và `verification:` vẫn viết
  "Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có mạng)", nay SAI MỘT PHẦN.
  (2) Câu chữ "năm giới hạn KC" ở contracts/telegram/commands.yaml (§CMD-save size_note_vi, response_rules
  length_vi, EDGE-02), acceptance/scenarios.yaml, precode/README.md, precode/gates.yaml G3-X5,
  precode/review.md, docs/master-plan.md và 8 card agent-tasks/* — nay phải đọc là "ba".
  (3) Ba dữ kiện còn thiếu cần một khả năng đọc lấy được CẢ TRANG core.telegram.org/bots/api (fetch theo
  đoạn, hoặc tải rồi grep cục bộ) dưới CÙNG ranh giới host — amendment về CÔNG CỤ, không phải về host.
migration: >
  Không cần chuyển đổi dữ liệu; chưa có mã. Hành vi lập kế hoạch có đổi một chiều: §3.5 nay đếm trên chuỗi
  thô đã escape với trần 4096, và dispatcher phải chừa nhịp 1 tin/giây cho mỗi chat khi gửi nhiều part.
  Đường lùi: nếu Telegram đổi chính sách, sửa đúng hàng trong bảng §3.4 kèm URL và ngày đọc mới và mở CR
  mới; KHÔNG chỉnh con số tại chỗ và KHÔNG xoá câu trích cũ, vì nó là bằng chứng rằng một giới hạn từng
  đúng vào một ngày cụ thể (§8).
```

**Vì sao ba dòng còn lại là `BLOCKED_DEPENDENCY` chứ không `BLOCKED_SCOPE`.** Khác `CR-PC03-08` — ở đó trang tài
liệu redirect ra một host **ngoài** allowlist, nên cái chặn là ranh giới **quyền** — ở đây trang mang cả ba
dữ kiện (`https://core.telegram.org/bots/api`) nằm **đúng trong** host được cấp. Cái chặn là độ dài: bản
markdown của trang bị cắt **trước** mục `Available methods`, nên `sendMessage`, `InlineKeyboardButton` và
bảng escape MarkdownV2 không vào được tầm đọc; fragment `#sendmessage` / `#inlinekeyboardbutton` không đổi
điều đó. Mười hai trang cùng host đã thử (liệt kê ở `precode/decision-register.md` §8.14.1) và không trang
nào chứa ba dữ kiện ấy. Ghi đúng loại chặn là có ích thật: `BLOCKED_SCOPE` gọi Owner ra mở host, còn
`BLOCKED_DEPENDENCY` gọi Coordinator ra cấp một cách đọc khác — hai hành động khác nhau.

#### Bổ sung `CR-PC07-04.a` — bump version + sửa `verification:`, sau ba hướng thử của vòng hai (cùng ngày)

Bổ sung **cộng thêm**, không viết lại khối trên: khối ấy ghi đúng trạng thái sau vòng một — kể cả câu
"BUMP NÀY CHƯA ĐƯỢC ÁP DỤNG", đúng vào lúc nó được viết. Đọc hai mục theo thứ tự.

```yaml
cr_id: CR-PC07-04.a           # bổ sung của CR-PC07-04; KHÔNG thay thế nó; CR gốc VẪN mở
raised_by: worker-WT (PKT-PC07-FIX-TELEGRAM-2), dưới AUTH-COORD-TELEGRAM-FACTS / LEASE-PC07-TELEGRAM-p2
addressed_to: PC07 (chủ hợp đồng contracts/telegram/delivery.md)
status: PROVISIONAL           # ba dữ kiện vẫn BLOCKED_DEPENDENCY sau khi đã thử đúng ba hướng được giao
ratified_by: OD-20260908-05   # cùng biên bản; Coordinator MỞ RỘNG vùng ghi từ §3.4 sang CẢ FILE
source_of_change: >
  Nội bộ: vòng một cố ý không sửa front matter vì nó nằm ngoài vùng §3.4 được cấp, và đã báo việc còn lại
  ở "still_open" mục (1). Coordinator mở rộng lease sang cả file đúng vì lý do ấy — front matter mô tả
  chính cái §3.4 vừa đổi. Cộng thêm ba hướng thử mới cho ba dữ kiện còn KC; không hướng nào đổi được
  ranh giới quyền, và một hướng bị từ chối vì lý do quyền (xem still_open).
before: >
  contracts/telegram/delivery.md front matter, nguyên văn: `version: 0.1.0`, và dòng cuối của
  `verification:`: "E1–E4: NOT_RUN. Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có
  mạng)." Câu ấy đúng khi PC07 viết nó và SAI MỘT PHẦN sau vòng một: hai trong năm giới hạn đã có nguồn,
  và lý do "không có mạng" đã hết tồn tại từ OD-20260908-05 mục 2.
after: >
  `version: 0.2.0`. Dòng cuối `verification:` thay bằng phát biểu đếm được: HAI dữ kiện đã đọc từ tài liệu
  chính thức core.telegram.org ngày 2026-09-08 (4096 ký tự; rate limit gửi) mang nhãn DOCS_derived kèm hạn
  dùng; BA dữ kiện còn KC ở BLOCKED_DEPENDENCY, gọi tên đích danh (callback_data, parse mode + bảng escape,
  số nút mỗi hàng/bàn phím) và nói rõ chúng thiếu TOOL CAPABILITY chứ không thiếu nguồn; kết luận rằng nhánh
  multipart của §3.5 vẫn chưa hiện thực được và MOD-telegram-adapter vẫn bị chặn cứng. Trong §3.4: danh sách
  anchor đã thử nâng lên BẢY (tám lần gọi, hai vòng) kèm bốn điểm cắt quan sát được, cộng một đoạn mới ghi
  phủ định CÓ PHẠM VI cho dòng "số nút" và lý do bước tìm kiếm web không được chạy.
  claim_ceiling GIỮ DRAFT_FOR_REVIEW.
version_rule: >
  §2 hàng minor, như đã phân tích ở CR-PC07-04: thêm thông tin, không đổi enum/semantics/auth_scope/
  idempotency/commit point. 0.1.0 -> 0.2.0, áp dụng MỘT LẦN cho cả hai vòng — vòng một không bump được
  (ngoài vùng cấp) nên không có bump trung gian nào để giữ. Khác CR-PC03-08/-08.a ở điểm này: ở đó hai lần
  sửa đứng trên HAI phạm vi quyền khác nhau nên sổ cố ý giữ hai lần bump; ở đây cùng một quyền, cùng một
  ngày, một lần bump là đủ và không xoá sự thật nào.
affected:
  requirements: [REQ-AC14, REQ-S5.3-02]   # không đổi so với CR-PC07-04; hai CSV đã ghi đúng ở vòng một
  contracts:
    - contracts/telegram/delivery.md      # 0.1.0 -> 0.2.0 (ÁP DỤNG)
  modules: [MOD-telegram-adapter, MOD-delivery-service]
  fixtures: []
  task_cards:
    rule: "§5 — vòng STALE thứ hai cho mọi card pin contracts/telegram/delivery.md."
    action: "Coordinator pin lại MỘT lần trên bytes cuối (0.2.0); không cần pin bytes trung gian của vòng một."
  evidence: []                            # E0 chạy lại sau khi sửa: PASS 25 / violations 0
still_open: >
  BA dữ kiện vẫn thiếu, sau khi đã thử ĐÚNG ba hướng được giao. (1) Anchor: bảy anchor / tám lần gọi, cả
  tám bị cắt trước Available methods; điểm cắt xê dịch (MessageAutoDeleteTimerChanged, date-time entity
  formatting, WebAppData, InputChecklist) nhưng lần xa nhất vẫn chưa tới InlineKeyboardMarkup. Giả thuyết
  "anchor dời được cửa sổ đọc" đã được thử và đã sai. (2) Tìm kiếm web: KHÔNG chạy — BLOCKED_SCOPE. Quyền
  của OD-20260908-05 mục 2 chỉ có core.telegram.org kèm "no message sent"; một truy vấn tìm kiếm đi tới
  host khác và mang theo nội dung truy vấn, và protocol.md §2 nói Coordinator không nới được grant của
  Owner. Chỉ Owner mở được. (3) Vì (2), dòng "số nút mỗi hàng" chỉ ghi được một PHỦ ĐỊNH CÓ PHẠM VI —
  "không tìm thấy trên 12 trang đã đọc được ngày 2026-09-08" — chứ KHÔNG phải "Telegram không công bố con
  số nào": trang có khả năng nêu nó nhất chính là trang không đọc được, nên tập đã đọc có lỗ thủng đúng
  chỗ cần. Dòng ấy GIỮ KC. Cách giải vẫn là một khả năng đọc lấy được cả trang /bots/api.
migration: >
  Không cần chuyển đổi dữ liệu. Consumer đọc version: mọi card và mọi file trỏ "delivery.md 0.1.0" nay
  phải đọc 0.2.0; đây là lần bump đầu tiên của file này. Đường lùi không đổi so với CR-PC07-04.
```

#### Bổ sung `CR-PC07-04.b` — vòng ba: quyền đã nới sang tìm kiếm web, ba dữ kiện vẫn không đọc được

Bổ sung **cộng thêm**, không viết lại hai khối trên. Đọc ba mục theo thứ tự: `-04` (vòng một, hai dữ kiện),
`-04.a` (vòng hai, front matter + anchor), `-04.b` (vòng ba, bản lưu trữ).

```yaml
cr_id: CR-PC07-04.b           # bổ sung của CR-PC07-04; CR gốc VẪN mở
raised_by: worker-WT (PKT-PC07-FIX-TELEGRAM-3), dưới AUTH-COORD-TELEGRAM-FACTS / LEASE-PC07-TELEGRAM-p3
addressed_to: Coordinator và Owner (việc còn lại là một amendment CÔNG CỤ, không phải nội dung hợp đồng)
status: PROVISIONAL           # không dữ kiện nào đổi trạng thái; chỉ hồ sơ về đường đã thử được bổ sung
ratified_by: OD-20260908-07   # authority AUTH-OWNER-20260908-08, mục 1; ghi ở precode/decision-register.md §8.14.3
source_of_change: >
  Owner nới quyền đúng chỗ vòng hai dừng: cho dùng WebSearch để tìm ĐƯỜNG ĐỌC chính trang
  core.telegram.org/bots/api (bản lưu trữ, cache, hoặc cách lấy lát nhỏ hơn). Cấm cũ giữ nguyên:
  api.telegram.org, bot token, gửi bất cứ thứ gì. Owner nói rõ tìm kiếm là để ĐỊNH VỊ nội dung trang ấy,
  không phải để lấy một con số từ site khác.
before: >
  contracts/telegram/delivery.md §3.4 sau vòng hai: ba hàng callback_data / parse mode + bảng escape /
  số nút mỗi hàng mang trạng thái KC kèm BLOCKED_DEPENDENCY, với hồ sơ 12 trang cùng host và 7 anchor.
after: >
  Cùng ba hàng, CÙNG trạng thái KC và BLOCKED_DEPENDENCY — không giá trị nào đổi. §3.4 nhận thêm một đoạn
  ghi vòng ba: hai lần tìm kiếm (một lần allowed_domains = core.telegram.org), hai URL Wayback, archive.ph,
  corefork.telegram.org; kết quả từng đường; câu kết rằng mọi thất bại đến từ KÍCH THƯỚC trang chứ không từ
  host, và đường đi còn lại là một cách đọc THEO LÁT trên đúng URL chính thức.
version_rule: >
  §2 hàng patch: làm rõ prose, KHÔNG đổi hành vi — không giá trị nào vào, không hàng nào rời KC.
  contracts/telegram/delivery.md 0.2.0 -> 0.2.1. Bytes vẫn đổi ⇒ §5 vẫn áp: card pin hash file này STALE.
reason: >
  `before` không sai và không thiếu dữ kiện — nó thiếu HỒ SƠ. Một CR nói "không đọc được" mà không kê đường
  đã thử thì lần sau người khác thử lại đúng những đường ấy. Ba đường của vòng ba (Wayback 2020, Wayback
  2016, archive.ph) đều thất bại vì một lý do KHÔNG liên quan tới Telegram: nền tảng chặn cứng host lưu trữ.
  Ghi lại điều đó biến một câu "chưa đọc được" thành một yêu cầu cụ thể mà Coordinator hành động được.
affected:
  requirements: [REQ-AC14, REQ-S5.3-02]   # không đổi; hai CSV giữ nguyên bytes
  contracts:
    - contracts/telegram/delivery.md      # 0.2.0 -> 0.2.1
  modules: [MOD-telegram-adapter, MOD-delivery-service]
  fixtures: []
  task_cards:
    rule: "§5 — vòng STALE thứ ba cho mọi card pin contracts/telegram/delivery.md."
    action: "Coordinator pin lại MỘT lần trên bytes cuối (0.2.1)."
  evidence: []                            # E0 chạy lại sau khi sửa: PASS 25 / violations 0
still_open: >
  BA dữ kiện vẫn thiếu. Nguyên nhân nay đã khoanh chính xác: trang ~1.5 MB, dữ kiện nằm ở nửa sau, và
  MỌI đường đã thử thất bại vì KÍCH THƯỚC, không vì host — 7 anchor (vòng hai), 12 trang cùng host (vòng
  một), 3 host lưu trữ (vòng ba, hai trong ba bị nền tảng chặn cứng), 1 host mirror của chính Telegram
  (corefork, cùng cỡ trang nên cắt y hệt). Thứ giải được là một cách đọc THEO LÁT trên đúng URL chính thức:
  HTTP Range, hoặc một công cụ fetch có offset/phân trang. Đó là amendment về CÔNG CỤ — không mở thêm host,
  không đổi một điều cấm nào, không cần thêm quyền mạng nào ngoài cái đã có.
  CẢNH BÁO CÓ CHỦ ĐÍCH: tìm kiếm vòng ba CÓ trả về các con số (trang thứ ba nêu 4096 after entities parsing,
  giới hạn UTF-16, và luật escape MarkdownV2) và chúng CÓ vẻ khớp giả định 64 byte đang dùng. Không một chữ
  nào được đưa vào hợp đồng: OD-20260908-07 mục 1 cấm thay lời Telegram bằng lời người khác kể lại. Ghi ra
  đây để lần sau không ai tưởng "chưa tìm thấy gì" và tự tiện điền.
migration: >
  Không cần chuyển đổi dữ liệu; không hành vi nào đổi. Consumer đọc version: delivery.md 0.2.0 -> 0.2.1.
```

**Và vì sao CR này KHÔNG tự đóng.** §1 luật 3: người phát hiện không phải người phê duyệt. Thêm nữa,
`precode/review.md` dòng 1001 hiện ghi `CR-PC07-04` là `CLOSED_CLAIMED` — *"gói liên quan tự khai đã đóng;
chưa xác minh độc lập"* — một trạng thái sinh ra bằng heuristic quét file, **không** bằng một lần đọc tài
liệu nào. Mục này là lần đầu tiên CR ấy chạm vào nguồn thật, và kết quả là `PARTIALLY_RESOLVED`: nhãn
`CLOSED_CLAIMED` kia luôn luôn sai, cả trước lẫn sau lần đọc này. `precode/review.md` nằm ngoài lease.

### CR-PC06-OQ03-01…03 — ba CR chạm hợp đồng, phát sinh khi điền hai mục adapter thật đầu tiên (`REQ-OQ03`)

Ba khối dưới đây do `worker-WAI` (`PKT-PC06-FIX-OQ03`, lease `LEASE-PC06-OQ03` / `-p2`, authority
`AUTH-COORD-OQ03`, cha `AUTH-OWNER-20260908-06`) phát ra ngày 2026-09-08, khi `OD-20260908-06` trả lời
`REQ-OQ03` và `contracts/ai/providers.yaml` lần đầu mang tên một nhà cung cấp thật (§2.1, `0.1.0 → 0.2.0`).
**Không CR nào ở đây tự đóng** (§1 luật 3). Bốn CR còn lại của cùng packet — `-04` (thiếu
`precode/owner-decisions-05.md`), `-05` (quyền mạng: `docs.anthropic.com` **301 →** `platform.claude.com`,
`www.anthropic.com/pricing` **301 →** `claude.com`, nên chỉ `/legal/*` đọc được), `-06` (hai lease chồng
nhau trên ba file), `-07` (`entities.yaml` `terms_check_note_vi` nay sai một phần) — gửi
Coordinator/Owner chứ không sửa hợp đồng; bản ghi một dòng ở `precode/owner-decisions-06.md` §7.

```yaml
cr_id: CR-PC06-OQ03-01
raised_by: worker-WAI (PKT-PC06-FIX-OQ03), dưới AUTH-COORD-OQ03 (cha AUTH-OWNER-20260908-06)
addressed_to: PC06 (chủ hợp đồng contracts/ai/providers.yaml)
status: OPEN
source_of_change: >
  Mâu thuẫn nội bộ, phát hiện khi điền hai mục adapter thật đầu tiên theo template §2.
before: >
  contracts/ai/providers.yaml §4 isolation.required_properties liệt kê NĂM tính chất ISO-01..ISO-05, trong
  đó ISO-04 "Không gửi Telegram, không đổi recipient" và ISO-05 "Chỉ nhận credential của ĐÚNG provider cho
  task đang giữ lease, thời hạn ngắn". Nhưng §2 example_entry.isolation chỉ có bốn khoá:
  {tools_disabled, filesystem_scope, network_egress, verification_method} — trong khi §2 required_fields
  ghi nguyên văn `{field: isolation, type: object, note_vi: "§4 — mọi trường con bắt buộc."}`.
after: >
  Thêm hai khoá trạng thái vào object isolation của template VÀ của mọi mục đã đăng ký: `telegram_egress`
  (ISO-04) và `credential_scope` (ISO-05), miền giá trị verified | unverified | not_applicable. Hai mục ở
  §2.1 hiện giữ đúng hình dạng bốn khoá của template và ghi khoảng trống ở
  isolation_determination_vi.template_gap_vi; khi template đổi, cả hai phải được điền `unverified`.
reason: >
  "Mọi trường con bắt buộc" không thể thoả cho hai tính chất KHÔNG CÓ Ô ĐỂ GHI. Với họ api_key, ISO-05
  chính là tính chất quyết định (ADR-0010 điểm 1: credential theo từng task) — để nó không có chỗ ghi
  nghĩa là cái đang chặn `enabled` phải sống trong prose thay vì trong một trường kiểm được bằng máy.
affected:
  requirements: [REQ-A5, REQ-AC17]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0 — thêm khoá bắt buộc vào một object đã có ví dụ chuẩn ⇒ major khi áp
  modules: [MOD-ai-adapter, MOD-settings-service]
  fixtures: []
  evidence: []
migration: >
  Chưa có mã và chưa có hàng dữ liệu nào; không cần chuyển đổi. Hai mục §2.1 đang enabled=false nên thêm
  hai ô không mở cổng nào.
```

```yaml
cr_id: CR-PC06-OQ03-02
raised_by: worker-WAI (PKT-PC06-FIX-OQ03)
addressed_to: PC06 + Owner
status: OWNER_DECISION_REQUIRED
source_of_change: >
  Quyết định của Owner (OD-20260908-05 mục 1) lệch với câu chữ hợp đồng.
before: >
  contracts/ai/providers.yaml §5 terms_check.fields ghi `{field: reviewer, … note_vi: "Ai đã đọc. Ở MVP một
  người dùng, đây là Owner."}` và §5 what_pc06_must_not_do_vi: "PC06 KHÔNG đọc thay và KHÔNG đoán. Việc này
  là công việc tay, không tự động hoá được, và phải làm LẠI khi provider đổi version."
after: >
  Chốt một trong hai. (a) `reviewer` được phép là một Worker chạy dưới authority của Owner, và §5 ghi thêm
  rằng bản ghi ấy cần Owner ký xác nhận TRƯỚC khi bất kỳ adapter nào enabled = true. (b) Giữ nguyên §5, và
  lần đọc ở precode/owner-decisions-06.md §3 chỉ là TÀI LIỆU CHUẨN BỊ: terms_check.outcome của hai mục §2.1
  hạ về `not_read` cho tới khi chính Owner đọc.
reason: >
  OD-20260908-05 mục 1 nói nguyên văn "a Worker still does that, separately, before any adapter is set
  enabled = true". Hai câu không thể cùng đúng. Hiện enabled = false nên không cổng nào bị đi vòng, nhưng
  câu trả lời phải có TRƯỚC lần bật đầu tiên, vì contracts/data/entities.yaml
  ck_provider_config_terms_before_enable ("enabled = 0 OR terms_check_at IS NOT NULL") cộng
  ck_provider_config_terms_by biến nó thành một CHECK chạy được, không phải một lời khuyên.
affected:
  requirements: [REQ-A5]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0
    - contracts/data/entities.yaml    # ENT-provider-config.terms_check_by / terms_doc_ref
  modules: [MOD-settings-service]
  fixtures: []
  evidence: []
migration: "Không cần; chưa có hàng provider_config nào tồn tại."
```

```yaml
cr_id: CR-PC06-OQ03-03
raised_by: worker-WAI (PKT-PC06-FIX-OQ03)
addressed_to: PC06 + PC01
status: OPEN
source_of_change: "Nguồn ngoài KHÔNG đọc được trong quyền mạng đã cấp (redirect ra ngoài allowlist)."
before: >
  contracts/ai/providers.yaml §1 api_key.usage_reporting: exact, chú thích "Token count thật (SRC-SPEC
  §10.2). Nếu một provider vẫn không báo, adapter khai `unknown` chứ không ghi 0 (I14)". Hai mục §2.1 khai
  usage_reporting: exact.
after: >
  Ghi rõ (ở §1 hoặc §2.1) rằng `exact` áp cho SỐ TOKEN, còn cost_micro_usd là giá trị SUY RA từ bảng giá
  công bố của nhà cung cấp: khi chưa có bảng giá có nguồn, cost_micro_usd phải đi đường `unknown` — cấm ghi
  0 (I14) — kể cả khi tokens_in/tokens_out đã chính xác.
reason: >
  API trả usage.input_tokens / output_tokens nhưng KHÔNG trả tiền. Bảng giá nằm sau một redirect ra ngoài
  allowlist (www.anthropic.com/pricing → claude.com/pricing, 301), nên hiện KHÔNG có con số giá nào có
  nguồn. Một adapter khai `exact` rồi ghi cost_micro_usd = 0 sẽ vi phạm I14 trong khi vẫn "đúng" theo câu
  chữ hiện tại — đó là loại lỗ hổng mà I14 sinh ra để chặn.
affected:
  requirements: [REQ-D44]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0
    - contracts/data/entities.yaml    # usage của analysis_attempt
  modules: [MOD-ai-adapter]
  fixtures: []
  evidence: []
migration: "Không cần; chưa có mã."
```

**Ghi chú version cho `contracts/ai/providers.yaml` `0.1.0 → 0.2.0`.** §2 hàng **minor**, nguyên văn: *"Thêm
trường **optional**, thêm mã lỗi mới, thêm operation mới"*. Khối `registered_adapters` (§2.1) là một khoá
**optional mới**; nó **không** đổi enum, semantics, auth_scope, idempotency key hay commit point (không hàng
`major` nào phủ), và nặng hơn hàng `patch` ("sửa lỗi chính tả, làm rõ prose, không đổi hành vi") vì nó thêm
hai mục adapter có thật cùng một kết luận `terms_check`. Câu `scope` cũ **không bị xoá**, chỉ được đọc lại
(§8 "giữ bản cũ để audit"). Hệ quả §5: **mọi card pin hash `contracts/ai/providers.yaml` chuyển `STALE`** —
ít nhất `agent-tasks/TC-analysis-adapter-validation.md`; Coordinator pin lại, `STALE` nghĩa là pin lại chứ
không phải `FAIL`. `worker-WAI` **cố ý không chạm** card nào (`agent-tasks/*` ngoài lease).

**Một dòng còn nợ, ngoài lease của packet này.** `precode/requirements.csv` hàng `REQ-D40` vẫn ghi trong cột
notes: *"Model cụ thể là REQ-OQ03, cần Owner chọn"* — nay đã chọn (`OD-20260908-06`). Lease
`LEASE-PC06-OQ03-p2` chỉ cấp **hàng `REQ-OQ03`**, nên hàng `REQ-D40` **không** bị chạm; nó cần một packet
khác. Cùng loại: `acceptance/traceability.csv` hàng `REQ-OQ03` (hiện `ĐX` / `PARTIAL`), `precode/gates.yaml`,
`precode/README.md`, `precode/owner-decision-request.md` (khối "VẪN CHỜ" nay rỗng), `precode/baseline.json`,
`agent_profile/registry.json`, `docs/master-plan.md` §3.

### CR-PC06-OQ03-08 — hai câu prose của `providers.yaml` §2.1 cũ đi sau chữ ký `OD-20260908-08`

```yaml
cr_id: CR-PC06-OQ03-08
raised_by: worker-WAI (PKT-PC06-FIX-OQ03-3), dưới AUTH-OWNER-20260908-09 (OD-20260908-08)
addressed_to: PC06 (chủ hợp đồng contracts/ai/providers.yaml)
status: OPEN
source_of_change: >
  Quyết định của Owner. OD-20260908-08 ký xác nhận REQ-A5 cho Anthropic và chấp nhận tường minh bảo đảm
  TC-A5-01; lease LEASE-PC06-OQ03-p3 chỉ cấp object terms_check, nên hai câu prose kể cùng một sự việc
  KHÔNG được cập nhật cùng lúc và nay lệch với trường authoritative.
before: >
  (1) contracts/ai/providers.yaml §2.1 registered_adapters.terms_conditions_vi.reviewer_caveat_vi, nguyên
  văn: "Owner **chưa** ký xác nhận nội dung đã đọc; vì `enabled = false`, không cổng nào bị đi vòng."
  (2) Cùng file, mục anthropic@claude-sonnet-5, mệnh đề cuối của disabled_reason, nguyên văn: "hai điều kiện
  còn mở là TC-A5-01 (quyền đối với Input của bên thứ ba) và chữ ký xác nhận của Owner cho lần đọc REQ-A5."
after: >
  (1) reviewer_caveat_vi đọc lại: §5 reviewer = Owner ĐÃ THOẢ cho đúng Anthropic và đúng ba trang ở
  source_urls, bằng OD-20260908-08 (AUTH-OWNER-20260908-09, 2026-09-08); lần đọc gốc do worker-WAI thực
  hiện và được Owner ký xác nhận; hết hiệu lực khi một trong ba trang đổi phiên bản (ADR-0010). Giữ nguyên
  câu lịch sử kèm mốc thời gian của nó (§8 "giữ bản cũ để audit").
  (2) disabled_reason còn ĐÚNG MỘT điều kiện thuộc phía mình, và nó đã đổi hình: phần bảo đảm với Anthropic
  của TC-A5-01 được Owner NHẬN (OD-20260908-08), phần chính sách nguồn — arXiv/OpenAlex/X có cho phép hệ
  này tái xử lý nội dung của họ hay không — VẪN MỞ và chưa ai được giao đi hỏi. Chữ ký xác nhận của Owner
  KHÔNG còn là điều kiện mở.
reason: >
  Trường terms_check.reviewer (authoritative, đã cập nhật) nay mâu thuẫn với hai câu prose trong cùng file.
  Một hợp đồng tự mâu thuẫn thì người đọc sau không biết câu nào đang có hiệu lực — và ở đây câu cũ đọc theo
  hướng NGHIÊM HƠN thực tế, nên nó không tạo rủi ro bật nhầm; nhưng nó khiến CR-PC06-OQ03-02 trông như còn
  mở trong khi Owner đã đóng. Đây cũng là lý do CR này tồn tại thay vì một lần sửa lặng lẽ ngoài lease:
  protocol.md §5 cấm "viết trước, hợp thức hoá sau".
affected:
  requirements: [REQ-A5]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0 — chỉ prose; khi áp, patch (không đổi hành vi) theo §2 hàng patch
  modules: [MOD-ai-adapter, MOD-settings-service]
  fixtures: []
  evidence: []
migration: >
  Không cần. enabled = false KHÔNG đổi ở cả trước lẫn sau: cổng đang chặn là cô lập (B13/ADR-0010,
  ISO-03/ISO-05 unverified, E3 NOT_RUN), không phải điều khoản.
```

**`CR-PC06-OQ03-02` — đóng bởi `OD-20260908-08`.** CR ấy hỏi `reviewer` phải là Owner hay được là Worker;
Owner chọn phương án (a) của chính CR: Worker đọc, **Owner ký xác nhận**, và chữ ký là thứ làm §5 thoả.
Người đóng là **Owner**, không phải người phát hiện (§1 luật 3 được tôn trọng). Bản ghi: `precode/
decision-register.md` §8.15.1.

### CR-TC-storage-06 (cùng gốc `CR-TC-storage-04`) — `maintenance_window`: chỗ ghi mà state contract đã đòi

```yaml
cr_id: CR-TC-storage-06
raised_by: WR (card TC-storage-write-blocked-readiness) — DỪNG ở SG-EDGE thay vì bịa một bảng
addressed_to: PC02 (chủ hợp đồng contracts/data/entities.yaml)
status: PROVISIONAL           # thi hành dưới amendment kỹ thuật AMD-ENT-maintenance-01; Owner chưa phát biểu
source_of_change: >
  Mâu thuẫn nội bộ giữa hai hợp đồng đã đóng băng. contracts/state/storage.yaml T-ST-03 khai
  transaction "Ghi một hàng maintenance window", T-ST-04 "Ghi kết thúc maintenance window",
  T-ST-09 "hàng maintenance window được ghi khi ghi được lại". contracts/data/entities.yaml
  không khai bảng nào để ghi ba hàng đó.
before: >
  contracts/data/entities.yaml v0.2.0: 60 entity, không entity nào tên maintenance_window hay
  storage_health; không trường nào trong 60 entity chứa "maintenance"; 49 bảng sau
  `alembic upgrade head` cũng không có. Mọi lần nhắc "maintenance" trong file trỏ RA NGOÀI, sang
  contracts/state/storage.yaml.
after: >
  Thêm đúng MỘT entity `maintenance_window` (ENT-maintenance-window, status specified,
  owner_module MOD-data-store) với 10 trường (id, owner_id, opened_at, opened_by, reason,
  storage_health_at_open, closed_at, closed_by, snapshot_verified_at, restore_record_id),
  partial unique ux_maintenance_window_open trên (owner_id) WHERE closed_at IS NULL, và ba CHECK.
  Version 0.2.0 -> 0.3.0. Amendment AMD-ENT-maintenance-01 tại mục 0b của chính file đó.
  Tập retained_by_owner_decision của TXN-purge-all nhận thêm maintenance_window: 21 -> 22,
  tổng 60 -> 61.
reason: >
  "before" không đủ, không sai. Hệ quả đo được (gap G-3): trạng thái maintenance chỉ sống trong
  bộ nhớ tiến trình, nên backup_cli maintenance --open không sống nổi tới lần gọi sau, và
  T-ST-05 (restore) không tới được vì nó đòi maintenance trước. WR dừng đúng: hai lối tắt đều
  sai — bảng `settings` thuộc MOD-settings-service (FORBIDDEN_EDGE trong mọi thứ trừ tên gọi),
  còn bịa một bảng không khai sẽ bị tests/contract/test_schema_matches_entities.py bắt ở chiều
  "mọi bảng phải có entity cùng tên".
version_rule: >
  §2 KHÔNG có hàng nào cho "thêm một bảng mới" — cùng khoảng trống mà CR-PC10-13 đã mở cho
  AMD-ENT-owner-01. Mục 4 của entities.yaml liệt kê "Thêm bảng mới" là additive và đó là căn cứ
  thực chất: không cột nào của 60 bảng cũ đổi, không consumer nào đang đọc một bảng chưa tồn tại.
deviation:
  deviation_from: "§2 của chính file này — khoảng trống: không có hàng nào cho việc thêm một bảng mới"
  authority: AUTH-COORD-PC02-FIX16
  change_request: CR-PC10-13    # cùng khoảng trống, cố ý KHÔNG mở một CR mới
affected:
  requirements: [REQ-D58, REQ-AC12, REQ-S7.3-01]
  contracts:
    - contracts/data/entities.yaml     # 0.2.0 -> 0.3.0
    - contracts/state/storage.yaml     # không đổi; là NGUỒN của thay đổi này (T-ST-03/-04/-05/-09)
  modules:      [MOD-data-store]
  generated: []                        # entities.yaml không phải nguồn của bộ sinh (CR-P0-06)
  reaches_code_through:
    - "một revision Alembic tạo bảng (WR, lease kế tiếp)"
    - tests/contract/test_schema_matches_entities.py
  purge_sets: >
    retained 21 -> 22, tổng 60 -> 61. Mọi artefact khác nêu con số cũ phải được cập nhật
    (PKT-PC02-FIX17); entities.yaml là nguồn có thẩm quyền, artefact khác COPY nguyên văn.
  task_cards:
    rule: "§4 INV-06/INV-09 — mọi card pin hash contracts/data/entities.yaml chuyển STALE."
  evidence: [EV-PC02-01, EV-PC02-03, EV-PC02-06, EV-PC02-08]
migration: >
  Dữ liệu: không cần. Bảng mới, rỗng, không backfill. Đường lùi: nếu Owner phản đối, gỡ entity và
  G-3 quay lại trạng thái chưa hiện thực được — KHÔNG được thay bằng cách ghi vào `settings`.
```

**Ruling 2026-09-08 (`AUTH-COORD-PC02-FIX18`) — tập trường RỘNG HƠN được CHẤP NHẬN, và nó không
phải một deviation.** `AMD-ENT-maintenance-01` khai HỢP của hai danh sách: bảy tên trong ruling
`WIRING-wave-1.md` cộng `snapshot_verified_at` mà `CR-TC-storage-06` của WR nêu, và giá trị enum
thứ năm `disk_cleanup`. Coordinator phán: cả hai truy được về câu chữ của state contract —
`snapshot_verified_at` về `T-ST-04` `forbidden_vi` ("Đóng cửa sổ khi verify chưa pass", chỉ ép
được across-process nếu có cột), `disk_cleanup` về `T-ST-09` guard ("dọn ổ, migrate, restore").
Vì vậy nó là **phái sinh đúng của nguồn**, ghi ở `fields_derivation_vi` của amendment, **không**
ghi thành `deviation_from`. Không có khoảng trống quy tắc nào bị bắc cầu ở đây.

**Ba điều amendment này KHÔNG làm.** Nó **không** giải `CR-TC-storage-04` (thiếu entity
`storage_probe` cho đường `write_blocked → healthy`) — một khoảng trống KHÁC, vẫn mở. Nó
**không** persist `write_blocked` hay `recovery_required`: cái đầu bị `T-ST-01` và
`forbidden_transitions` hàng 4 cấm, cái sau đã đọc được từ `restore_record` đang có
(`dispatcher_unlocked_at IS NULL`). Và nó **không** khẳng định bảng đã tồn tại trong schema đang
chạy — chưa có migration nào tạo nó.

### CR-PC02-24 — `contracts/modules.yaml` chưa có token `maintenance_window`

```yaml
cr_id: CR-PC02-24
raised_by: worker-W3n (PKT-PC02-FIX16)
addressed_to: PC01 (chủ contracts/modules.yaml)
status: OPEN
source_of_change: "Entity mới được thêm SAU khi modules.yaml đã đóng băng."
before: >
  contracts/modules.yaml, MOD-data-store.data_owner_of = [sqlite_database_file (artifact),
  wal (artifact), schema_migration].
after: "Thêm `maintenance_window` vào data_owner_of của MOD-data-store."
reason: >
  Ruling R-03: tên entity trong entities.yaml là thẩm quyền, và modules.yaml data_owner_of dùng
  đúng các tên đó. Phép so hai chiều (EV-PC02-06) hiện FAIL đúng một phần tử:
  "PC02 entity KHÔNG có owner token trong modules.yaml: ['maintenance_window']". PC02 đã làm
  nửa của mình (owner_module trên entity + một dòng ở mục 4b newly_owned_entities); nửa còn lại
  thuộc PC01. Ghi ra thay vì để phép so im lặng FAIL.
affected:
  requirements: []
  contracts: [contracts/modules.yaml]
  modules:   [MOD-data-store]
  fixtures:  []
  evidence:  [EV-PC02-06]
migration: "Không cần."
```

### Deviation ghi nhận — `PKT-PC02-FIX17` không bump version của chín artefact lan truyền

```yaml
deviation_id: DEV-PC02-FIX17-01
deviation_from: "§2 của chính file này — luật 'đổi một hợp đồng ⇒ tăng version'"
authority: AUTH-COORD-PC02-FIX18      # ruling 2026-09-08; parent AUTH-OWNER-20260907-05
status: ACCEPTED
scope:
  - contracts/ports.yaml
  - contracts/modules.yaml
  - contracts/http/openapi.yaml
  - contracts/ops/secrets.md
  - contracts/ops/backup-restore.md
  - contracts/ui/screens.yaml
  - acceptance/scenarios.yaml
  - acceptance/fixtures/recovery/README.md
  - acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json
what_changed_in_them: >
  CHỈ các dòng đếm và dòng liệt kê tập của `data.purge_all`: retained 21 -> 22, tổng 60 -> 61,
  và thêm tên `maintenance_window` vào câu liệt kê. Không một chữ nào khác.
reason_vi: >
  Chín file này KHÔNG tự thay đổi hợp đồng — chúng SAO CHÉP một tập đã có thẩm quyền ở
  `contracts/data/entities.yaml` `TXN-purge-all`, và chính file đó ĐÃ mang bậc version của thay
  đổi (0.2.0 -> 0.3.0 cùng `AMD-ENT-maintenance-01`). Bump thêm chín lần nữa cho cùng một
  amendment sẽ ghi chín thay đổi hợp đồng vào sổ ở nơi chỉ có một, và làm chín vòng re-pin card
  cho một sự kiện.
openapi_specific_vi: >
  `contracts/http/openapi.yaml` `info.version` là phiên bản API mà consumer PIN. Nó nói về hình
  dạng wire, và hình dạng wire không đổi ở đây — chỉ một câu mô tả trong `description` đổi con
  số. Bump nó sẽ báo cho consumer một thay đổi API không tồn tại. Giữ nguyên là lựa chọn CÓ CHỦ
  ĐÍCH, không phải bỏ sót.
limits_vi: >
  Deviation này CHỈ áp cho lan truyền con số của một amendment đã được version ở nguồn. Nó KHÔNG
  là tiền lệ cho việc sửa nội dung hợp đồng mà không bump version. Hash của cả chín file vẫn đổi,
  nên §4 (INV-06/INV-09) vẫn chạy: mọi card pin chúng vẫn `STALE` và WP vẫn phải re-pin.
change_request: CR-PC10-13            # cùng chỗ §2 cần viết lại; không mở CR mới
```

### CR-PC02-25 — `E0-18` không so sánh con số trong văn xuôi

```yaml
cr_id: CR-PC02-25
raised_by: worker-W3n (PKT-PC02-FIX17), theo yêu cầu của Coordinator ở PKT-PC02-FIX18
addressed_to: W6n / PC09 (chủ evidence/tools/e0_check.py)
status: OPEN
source_of_change: >
  Ở PKT-PC02-FIX17, chín artefact còn ghi "21 bảng giữ lại" và "60 entity" sau khi entities.yaml
  đã đổi sang 22/61. `E0-18-purge-set-agreement` PASS suốt thời gian đó.
before: >
  E0-18 kiểm hai điều: (a) ba tập phân hoạch đúng tập entity, và (b) không artefact nào còn đánh
  dấu phạm vi purge là chưa quyết. Nó CỐ Ý không so sánh liệt kê trong văn xuôi — comment ngay
  trong e0_check.py ghi rằng bản làm việc đó cho 24 vi phạm, khoảng 20 là dương tính giả, và
  "a noisy check is worse than no check"; giới hạn được ghi ở evidence/tools/README.md §5g.
after: >
  Mở rộng E0-18 (hoặc thêm E0-18b) để bắt CHUỖI ĐẾM thay vì liệt kê tự do: quét trong ngữ cảnh
  purge các mẫu có cấu trúc đủ hẹp để không nhiễu — ví dụ "<n> bảng giữ lại", "giữ <n>",
  "GIỮ LẠI (<n> bảng)", "(37 xóa / <n> giữ / <n>)", "<n> entity", "retained <n>" — và so ba con
  số đó với `len()` của ba tập trong entities.yaml. Đây là bài toán KHÁC với so khớp danh sách
  tên và không mang theo lớp dương tính giả đã làm bản trước bị bỏ.
reason: >
  Giới hạn đã được ghi trung thực, nhưng nó nằm ở §5g của README công cụ, không ở nơi người đọc
  kết quả nhìn. Trong một wave thật, một PASS của E0-18 đã được hiểu là "các con số đã đồng bộ",
  và chín artefact chỉ được tìm ra bằng `grep` thủ công. Một dòng note trong output của chính
  check ("prose counts NOT compared — see CR-PC02-25") đã đủ chặn cách hiểu sai đó, kể cả trước
  khi có ai viết phép kiểm mới.
affected:
  requirements: []
  contracts: []
  modules:   []
  fixtures:  []
  evidence:  [evidence/tools/e0_check.py, evidence/tools/README.md]
migration: "Không cần. Đây là mở rộng phép kiểm, không đổi hợp đồng."
```
