---
contract_id: CT-precode-review
version: 0.1.0
status: draft
owner_role: verification owner (PC09)
source_refs:
  - "SRC-PLAN §11 PC09"
  - "SRC-PLAN §12 (cổng G0..G7, SP1)"
  - "SRC-PLAN §14 (chuẩn bằng chứng và cách tuyên bố hoàn thành)"
  - "SRC-PLAN §17 (Definition of Ready của toàn bộ Pre-code)"
  - "SRC-SPEC §1.4, §12, §13.1"
requirement_refs:
  - "precode/requirements.csv — cả 246 dòng, qua acceptance/traceability.csv"
decision_refs:
  - "B01"
  - "B02"
  - "B03"
  - "B04"
  - "B05"
  - "B06"
  - "B07"
  - "B08"
  - "B09"
  - "B10"
  - "B11"
  - "B12"
  - "B13"
  - "B14"
  - "B15"
  - "B16"
  - "B17"
invariant_refs:
  - "I01"
  - "I02"
  - "I03"
  - "I04"
  - "I05"
  - "I06"
  - "I07"
  - "I08"
  - "I09"
  - "I10"
  - "I11"
  - "I12"
  - "I13"
  - "I14"
  - "I15"
producers: ["MOD-none"]
consumers: ["MOD-none"]
dependencies:
  - "acceptance/scenarios.yaml"
  - "acceptance/traceability.csv"
  - "precode/gates.yaml"
  - "evidence/index.json"
  - "evidence/runs/"
  - "precode/decision-register.md"
  - "precode/owner-decision-request.md"
  - "evidence/handoffs/"
scope: >
  Báo cáo readiness của toàn bộ baseline Pre-code PC00–PC08 tại thời điểm PC09 bàn giao: module
  nào sẵn sàng nhận task card, module nào bị chặn và vì sao; số liệu độ phủ yêu cầu; kết quả E0
  thật; toàn bộ quyết định `PROVISIONAL` đang chờ Owner; toàn bộ change request của mọi gói kèm
  đề xuất xử lý; thiết kế đánh giá A2/A3/A4; rà soát lại B01–B17 và sổ ĐX/KC; và phát biểu tuyên
  bố có điều kiện.
verification: >
  Số liệu trong file này lấy từ một lần chạy THẬT của `evidence/tools/e0_check.py` được ghi ở
  `evidence/runs/` và đăng ký trong `evidence/index.json`. Không con số nào ở đây được ước lượng.
claim_ceiling: DRAFT_FOR_REVIEW

traceability_csv_contract_header:
  contract_id: CT-acceptance-traceability
  version: 0.1.0
  status: draft
  owner_role: verification owner (PC09)
  source_refs:
    - "SRC-PLAN §11 PC09"
    - "SRC-PLAN §2 (chuỗi yêu cầu → quyết định → invariant → hợp đồng → scenario → bằng chứng)"
  requirement_refs:
    - "precode/requirements.csv — một dòng cho mỗi dòng của registry"
  decision_refs: ["B01", "B02", "B03", "B04", "B05", "B07", "B08", "B09", "B10", "B11", "B12", "B15", "B16", "B17"]
  invariant_refs: ["I01", "I02", "I03", "I04", "I05", "I06", "I07", "I08", "I09", "I10", "I11", "I12", "I13", "I14", "I15"]
  producers: ["MOD-none"]
  consumers: ["MOD-none"]
  dependencies:
    - "precode/requirements.csv"
    - "acceptance/scenarios.yaml"
    - "contracts/"
  scope: >
    Ma trận truy vết: một dòng cho mỗi yêu cầu của registry, nối tới hợp đồng trích dẫn nó,
    invariant và scenario phủ nó, mã lỗi liên quan, cấp bằng chứng tối thiểu và trạng thái độ phủ.
  verification: "evidence/tools/e0_check.py check E0-11a-no-orphan"
  claim_ceiling: DRAFT_FOR_REVIEW
  file_format:
    encoding: UTF-8
    quoting: "mọi trường được bọc dấu nháy kép (csv.QUOTE_ALL)"
    list_separator: ";"
    columns:
      - "req_id — khóa, bằng đúng precode/requirements.csv"
      - "req_status — XN | UQ | ĐX | KC, sao nguyên từ registry"
      - "priority — P0 | P1 | OOS, sao nguyên từ registry"
      - "contract_refs — đường dẫn các file dưới contracts/ (và ba file precode/) trích dẫn req_id"
      - "invariant_refs — hợp của invariant_refs của mọi scenario phủ req_id"
      - "scenario_refs — các SC của acceptance/scenarios.yaml có req_id trong requirement_refs"
      - "error_refs — hợp của error_refs của mọi scenario phủ req_id"
      - "evidence_level — cấp cao nhất trong các scenario phủ nó; E0 nếu chỉ có hợp đồng; NONE nếu không có gì"
      - "coverage_status — COVERED | PARTIAL | ORPHAN | DEFERRED_P1 | OUT_OF_SCOPE | BLOCKED_B<nn>"
      - "notes — độ phủ nền khi dòng bị BLOCKED, cổng phủ thay scenario, fixture, và cảnh báo"
  coverage_status_rule_vi: >
    Quy tắc máy, áp đồng nhất cho cả 246 dòng, theo thứ tự: (1) priority OOS ⇒ OUT_OF_SCOPE;
    (2) priority P1 ⇒ DEFERRED_P1; (3) có cả scenario và contract ref ⇒ COVERED; (4) có một
    trong hai, hoặc chỉ được phủ bằng cổng của precode/gates.yaml ⇒ PARTIAL; (5) không gì cả ⇒
    ORPHAN. Sau đó GHI ĐÈ bằng BLOCKED_B<nn> khi dòng nằm trong danh sách "REQ ảnh hưởng" của
    AMD-B<nn> — nghĩa là chính VĂN BẢN CAM KẾT của dòng đó sẽ đổi nếu Owner phê chuẩn amendment,
    nên oracle chấp nhận của nó chưa đóng. Với các dòng bị ghi đè, cột notes vẫn ghi độ phủ nền
    ("coverage=COVERED", "coverage=PARTIAL") để người đọc không mất thông tin.
---

# Readiness review — baseline Pre-code Research Radar

Người viết: `worker-W6` (PC09, verification owner) · Ngày: 2026-09-07 (bản PC09-FIX7, **sau khi
Owner phê chuẩn `OD-20260907-01`**) · Claim: `DRAFT_FOR_REVIEW` cho bản review này;
**`CONTRACT_READY` cho bốn phạm vi hợp đồng** — xem §12

> **Mọi con số trong bản này được SINH RA, không được chép tay.** Bộ sinh là
> `derive_numbers.py` (đọc thẳng artefact và lần chạy E0 đã đăng ký) và `crtable.py` (quét toàn
> repo tìm CR id), chạy từ thư mục scratch của Worker.
>
> **Đầu ra của chúng nằm TRONG candidate**, cạnh lần chạy E0 mà chúng mô tả:
> hai artefact `numbers-…` và `cr_summary-…` trong `evidence/runs/`, đăng ký làm artefact của
> bản ghi `EV-PC09-01` trong `evidence/index.json` (trích **theo đăng ký**, không theo dấu thời
> gian: một tên file có dấu thời gian trong văn bản này sẽ tự làm chính nó cũ mỗi lần chạy lại —
> đúng vòng lặp mà `F-A2R5-02` mô tả). Mỗi con số
> dưới đây ghi kèm **khóa** của nó trong file thứ nhất — ví dụ `coverage.COVERED`,
> `partial_p0_breakdown`, `dor5` — nên người đọc candidate mở được đúng chỗ con số đến từ, thay
> vì phải tin một tên file không phân giải được (`F-A2R2-03`).
>
> Lý do có kỷ luật này: A2-R1 `F-A2R1-02` tìm thấy **bốn** con số headline mâu thuẫn với artefact,
> và cả bốn lệch theo hướng có lợi. Con số chép tay giữa các bản là cách chúng lệch. Từ
> `F-A2R2-01`, kỷ luật này áp cho cả **trạng thái**, không chỉ số: trạng thái audit nay chỉ được
> phát biểu ở §4.1.

Bản này **không** đóng finding nào, **không** phê chuẩn quyết định nào và **không** phải audit độc
lập. Nó tổng hợp và đối chiếu. Mọi con số đến từ một lần chạy thật của `evidence/tools/e0_check.py`
đăng ký trong `evidence/index.json`.

---

## 1. Kết luận một đoạn

**Owner đã phê chuẩn `OD-20260907-01` ngày 2026-09-07.** Cả 17 blocker B01–B17 chuyển từ
`PROVISIONAL` sang `RATIFIED`; stack được chọn (**phương án B — Python worker + TypeScript web**,
không phải phương án A mà kế hoạch khuyến nghị); phạm vi `data.purge_all` được chốt; timezone,
mốc freeze tag, mô hình trạng thái run, `delivery.unknown`, khóa analysis, ngoại lệ liên kết
Telegram, backup nhất quán, secret theo task và cả 8 tham số báo cáo đều được chấp nhận. Đây là
thay đổi lớn nhất kể từ khi gói này bắt đầu: nền của baseline không còn là đề xuất.

Bộ hợp đồng: **246** yêu cầu nguyên tử (`requirements`), **85** operation, **99** cạnh được phép và
**36** cạnh bị cấm, **60** entity, **67** transition, **28** mã lỗi, **86** fixture trên **9**
thư mục, **56** scenario có oracle, **0** thiếu fixture. Độ phủ: **`COVERED` 172**, `PARTIAL` 62,
`DEFERRED_P1` 6, `OUT_OF_SCOPE` 6, **`ORPHAN` 0** — và **không còn dòng `BLOCKED_B*` nào**
(`coverage`), vì phê chuẩn đã chốt văn bản cam kết của cả 84 dòng từng chờ nó.

**Lần chạy E0 của bản này: 24 check, 24 PASS, 0 FAIL, 0 vi phạm** (`e0`). Bộ check tăng lên 24:
`E0-12` được viết lại
thành một cửa **phạm vi** thay vì một lệnh cấm, và `E0-12b` mới kiểm rằng mọi file tuyên bố
`CONTRACT_READY` đều trích một phê chuẩn phân giải được (§3.6).

**21 file hợp đồng nay mang `claim_ceiling: CONTRACT_READY`** trong bốn phạm vi Owner đã phê
chuẩn; **110 file giữ `DRAFT_FOR_REVIEW`** (`contract_ready_count`, `draft_for_review_count`).

Điều **chưa** đạt, và không phê chuẩn nào thay thế được:

1. **15 yêu cầu vẫn `KC`** (`kc_count`) — chúng đòi dữ liệu từ thế giới bên ngoài: nhịp gọi
   arXiv/OpenAlex, giới hạn định dạng Telegram, điều khoản từng nhà AI, độ ổn định thu thập X,
   ngưỡng embedding, chất lượng mật độ vector. Owner phê chuẩn **văn bản**; phép đo vẫn phải chạy.
2. **`REQ-OQ03` (provider/model cụ thể) vẫn `OWNER_DECISION_REQUIRED`** — Owner chọn hoãn
   (mục 21). Chặn M3.
3. **Không có một byte bằng chứng runtime nào.** E1–E4 `NOT_RUN` ở cả 56 scenario. Chưa có code,
   chưa gọi provider, chưa chạy collector, chưa gửi Telegram, chưa drill restore.
4. **Chưa có repo triển khai.** Stack B đã chọn nhưng chưa có cây thư mục nào; card mô tả đường
   dẫn *sẽ* tồn tại.

Trạng thái dự án: **`NOT_READY_FOR_PRODUCT_CODE` cho toàn hệ thống**, nhưng bốn phạm vi hợp đồng
nay `CONTRACT_READY` — nghĩa là đủ để bắt đầu viết code trong đúng phạm vi đó khi Owner yêu cầu,
không phải đủ để tuyên bố sản phẩm chạy được.

## 2. Độ phủ yêu cầu

`acceptance/traceability.csv` có **246 dòng**, đúng bằng `precode/requirements.csv`.

| coverage_status | Số dòng | Nghĩa |
| --- | ---: | --- |
| `COVERED` | 172 | Có ít nhất một hợp đồng trích dẫn VÀ ít nhất một scenario phủ |
| `PARTIAL` | 62 | Có hợp đồng nhưng chưa có scenario, hoặc ngược lại, hoặc chỉ được phủ bằng một cổng |
| `BLOCKED_B01..B17` | 0 | **Không còn dòng nào**: `OD-20260907-01` phê chuẩn cả 17 blocker, nên không dòng nào còn chờ một quyết định để biết văn bản cam kết của mình |
| `DEFERRED_P1` | 6 | Hoãn sau MVP theo SRC-SPEC §2.2 |
| `OUT_OF_SCOPE` | 6 | Ngoài phạm vi theo SRC-SPEC §2.3 |
| **`ORPHAN`** | **0** | — |

84 dòng từng mang `BLOCKED_B*` nay trở về độ phủ đo được của chính chúng: phần lớn thành
`COVERED` (172, tăng từ 90), phần còn lại `PARTIAL` vì thiếu scenario hoặc thiếu trích dẫn hợp
đồng — **không phải** vì thiếu quyết định. Cột `notes` của mỗi dòng ghi blocker tương ứng là
`RATIFIED (OD-20260907-01)`, và dòng nào có status `KC` mang thêm một câu: *phê chuẩn không thay
thế được phép đo*.

**38 dòng `PARTIAL` là P0 với status XN hoặc UQ** (`partial_p0_xn_uq`). Ruling R5-03 đóng đúng "nhóm
thật", và PC09-FIX1 bổ sung `requirement_refs` phía scenario cho phần còn lại của nhóm đó. Phân
loại 38 dòng còn lại (`partial_p0_breakdown`):

| Nhóm | Số dòng | Vì sao PARTIAL | Đề xuất |
| --- | ---: | --- | --- |
| Chỉ có cổng (`gate-only`) | 8 | Bảy dòng mốc `REQ-S13-01..08` cộng một chỉ tiêu thành công. Là mốc quy trình / chỉ tiêu nhiều tuần, không phải hành vi kiểm được bằng một scenario | **Giữ PARTIAL là đúng.** Chúng được phủ bằng cổng G5/G6/G7. Ép thành COVERED bằng một scenario giả sẽ là làm đẹp con số |
| Chỉ có hợp đồng (`contract-only`) | 20 | Hợp đồng mô tả, chưa scenario nào khẳng định. Gồm `REQ-S1.4-01`, `-02` (chỉ tiêu tuần, đo ở E4) và `REQ-S4-10` (màu sắc/visual design **cố ý chưa chốt** — một quyết định KHÔNG chốt thì không có gì để test) | Phần lớn hợp lý. Gói sở hữu có thể bổ sung scenario, nhưng đây **không** phải khiếm khuyết chặn cổng |
| Chỉ có scenario (`scenario-only`) | 10 | Scenario khẳng định hành vi nhưng chưa file hợp đồng nào trích `REQ-` tương ứng — ví dụ `REQ-S5.5-01`/`-02` (hai ví dụ thời gian của SRC-SPEC §5.5) được SC05/SC06 phủ đầy đủ | Gói sở hữu thêm `requirement_refs`; rẻ và không đổi hành vi |

Nhóm đã đóng ở đợt này: `REQ-S4-01`, `-08`, `-09`, `REQ-S5.1-01..03`, `REQ-S5.3-01`, `-03`,
`REQ-S5.4-03`, `REQ-S6.1-01`, `REQ-S11.2-05`, `-06` — ruling R5-03 buộc `screens.yaml`,
`secrets.md`, `internet-boundary.md`, `deployment.md` và `run.yaml` trích chúng, còn PC09-FIX1 gắn
chúng vào SC10/SC17/SC49/SC50/SC51. Trong lúc làm việc đó tôi phát hiện và sửa một **trích dẫn
sai của chính mình**: SC49 dẫn `REQ-S11.2-05` (che secrets trong log) cho quy tắc cổng debug
Chrome bind loopback, mà quy tắc đó là `REQ-S11.2-06`.

Đáng ghi lại vì nó là lý do bốn scenario mới tồn tại: trước PC09, **51 yêu cầu không được bất kỳ
file nào dưới `contracts/` hay `acceptance/` trích dẫn**, trong đó có cả năm bước của luồng thiết
lập lần đầu (`REQ-S5.1-01..05`, bốn dòng XN). SC50–SC53 cộng ruling R5-03 đã đóng nhóm đó.

---

## 3. Kết quả E0 — chạy thật, FAIL còn lại được báo nguyên vẹn

Công cụ: `evidence/tools/e0_check.py` (**24 check**, quét 210 file trong bốn thư mục
`contracts`, `acceptance`, `precode`, `evidence` — `agent-tasks/` **không** nằm trong phạm vi quét,
xem §9.1). Lần chạy đóng gói được đăng ký ở
`evidence/index.json` bản ghi `EV-PC09-01`. `baseline_hashes` gồm các file quét được
(`evidence/runs/` đã bị loại khỏi phạm vi quét — xem §3.5).

**Hai file nhất thiết đổi sau lần chạy mà chúng trích dẫn:** chính `precode/review.md` (nó phải
viết ra kết quả) và `evidence/index.json` (nó phải đăng ký artefact). `baseline_hashes` vì thế ghi
bytes của hai file đó **trước** bước cuối. Đây là vòng lặp không tránh được, không phải một khoảng
lệch bị giấu; mọi file hợp đồng, fixture và scenario khác trong bản ghi là bytes cuối cùng.

**24 PASS · 0 FAIL · 0 vi phạm** (`e0` trong `numbers.json`).

### 3.1 Check mới: `E0-04b-prose-op-tokens` — lớp lỗi mà E0 trước đây không thấy

A2-R1 `F-A2R1-01` tìm thấy **chín** id operation không tồn tại nằm trong `event_order` của tám
scenario, cộng một bước gọi `post.mark_source_deleted` — một operation PC01 đã **bác bỏ** tường
minh. `E0-04` không thấy chúng vì `E0-04` chỉ đọc **trường có cấu trúc**, còn `event_order` là một
danh sách câu văn. Chính `review.md` §13 của bản trước đã ghi rủi ro này bằng chữ, sau khi
`CR-PC04-11` cho thấy nó là thật — nhưng lời cảnh báo đó không được chuyển thành một cửa kiểm, nên
lớp lỗi tiếp tục tồn tại ở tám scenario khác.

`E0-04b` đóng lớp đó: nó quét **mọi chuỗi** dưới `contracts/` và `acceptance/` (cả có cấu trúc lẫn
văn xuôi) tìm token dạng `` `<domain>.<verb_noun>` `` và token SCREAMING_SNAKE, rồi phân giải
chúng. Nó loại trừ có nguyên tắc, không loại trừ tùy tiện: tên file, `<entity>.<field>` đã khai
trong `entities.yaml`, `<máy trạng thái>.<field|giá trị enum>` đã khai trong `contracts/state/`,
và một danh sách từ vựng trạng thái được viết ra trong chính công cụ. Mọi thứ khác phải phân giải
được.

Chín id đã được sửa trong `acceptance/scenarios.yaml` theo tên authoritative của `ports.yaml`:
`job.enqueue_run`→`job.enqueue_scheduled_run` (SC01) · `backup.create`→`backup.create_snapshot`,
`backup.restore`→`backup.restore_snapshot` (SC12, SC27) ·
`backup.reconcile`→`backup.reconcile_after_restore` (SC27, SC42, SC53) ·
`backup.verify`→`backup.verify_snapshot` (SC43) ·
`embedding.start_generation`→`embedding.start_generation_rebuild`,
`embedding.switch_generation`→`embedding.activate_generation` (SC24). Bước 3 của SC12 được **viết
lại**, không đổi tên: quan sát "bài gốc đã bị xóa" đi kèm lô ingest dưới dạng trường
`source_deleted_observed_at` của `ingest.submit_batch`, đúng như PC01 đã chốt — không có operation
riêng cho nó.

**Ghi thẳng một điều về bản trước:** `CR-PC04-11` được ghi là "đóng" trong khi bản sửa khi đó chỉ
chạm SC52. SC24 vẫn mang cả hai tên sai và sáu tên `backup.*`/`job.*` sai khác chưa ai thấy. Một
CR không nên được ghi là đóng khi bản sửa chưa được quét lại trên toàn corpus; đó là bài học của
`F-A2R1-01` và là lý do `E0-04b` tồn tại thay cho một lời hứa.

### 3.2 Tách `E0-04b` làm ba — và cả ba nay sạch

Ruling FIX7 chốt quy tắc phân giải, và W2 viết nó vào `contracts/ports.yaml`
`conventions.prose_token_rule_vi` — **đó là nguồn duy nhất**, công cụ chỉ thực thi: một token
`` `<a>.<b>` `` phân giải được nếu là **operation của `ports.yaml`** HOẶC **cặp
`<entity>.<column>` của `entities.yaml`**; token có phân đoạn đầu không phải domain operation cũng
không phải tên entity (đường dẫn file, khóa YAML cấu trúc, host, idiom thư viện) được bỏ qua. Tách
ba vì hai chế độ hỏng có **chủ sở hữu khác nhau và cách sửa khác nhau**.

Kết quả cuối: `E0-04b` 284 kiểm / **0** vi phạm · `E0-04c` 215 / **0** · `E0-04d` 154 / **0**.

**Hai đợt residual đã đóng, và cả hai đóng bằng cách sửa nội dung.**

- **Đợt FIX6 → FIX7 (13 vi phạm).** Đếm lại từ chính file run `E0-20260907T012946Z`: **9 tham
  chiếu cột + 2 nhắc tên operation cũ + 2 nhắc mã lỗi chưa đăng ký**; theo *token phân biệt* là
  6 + 2 + 1. Dispatch của FIX7 mô tả là "7 + 3 + 1" — **không khớp artefact**; tôi ghi theo
  artefact, vì một con số headline không được lệch khỏi file nó trích (đó là `F-A2R1-02`). W3
  thêm sáu cột thật, W5 sửa hai đoạn prose, W2/W3 gỡ hai chỗ nhắc `SAVE_ALREADY_EXISTS`.
- **Đợt FIX7 → FIX8 (8 vi phạm, `CR-PC09-12`).** Các token mà bản tách soi tới lần đầu:
  `coverage_window.predecessor` ×2 (cột thật `predecessor_window_id`), `post.mark_source_deleted`
  ×2 (operation đã bị bác, viết như một cột), `*.does_not_guarantee` ×3 (câu tiếng Anh bị đặt
  backtick thành dạng đường dẫn), `telegram_link_code.format_match_attempt_count` ×1 (cột từng
  được đề xuất, chưa bao giờ tồn tại). W2, W3 và W4 đã sửa cả 8.

Một token là của tôi và đã sửa ở FIX7: SC07 dẫn `identity_alias.alias_value`; cột thật là
`id_value_normalized` (cộng `id_value_raw` giữ dạng gốc).

**Một phản biện đúng, ghi lại thay vì bỏ qua.** W3 nêu rằng gate coi *mọi* token `a.b` là một
khẳng định về operation hoặc cột, nên một phần các sửa đổi ở hai đợt trên là **thích nghi với hình
dạng của gate**, không phải sửa nội dung sai. Đó là chi phí thật. `CR-PC07-10` đề xuất namespace
được khai báo (`schema:`, `api:`, `§`) để diễn đạt ý định thay vì né dấu chấm. **Không thực hiện ở
đợt này** — nó chạm mọi file hợp đồng, ngay trước freeze, để đổi cách diễn đạt chứ không phải sửa
một khiếm khuyết đang tồn tại (ba check hiện 0 vi phạm). Đánh đổi đầy đủ ở
`evidence/tools/README.md` §5c; thời điểm đúng là **sau** khi A2 xác minh epoch này.

### 3.3 Hai check khác được siết ở đợt này

- **`E0-10b`** nay còn kiểm rằng một operation được gọi tên phải **do chính callee sở hữu** khi
  callee là một `MOD-*` (ruling F-A2R1-05). Trường hợp A2 tìm ra: `NC-28` / sự kiện 26 gọi
  `worker.claim_assignment` trên cạnh `MOD-scheduler → MOD-x-collector`, nhưng operation đó do
  `MOD-job-service` sở hữu và chạy **ngược chiều** — máy cá nhân không lắng nghe cổng nào, nên
  "gọi rồi khẳng định bị từ chối" là một oracle **không chạy được**. Khi callee là `EXT-*`, quy
  ước đã được W2 viết vào `modules.yaml default_deny.attempted_edge_operation_rule_vi` và check
  tôn trọng nó — một quy ước được viết ra thì kiểm được, một quy ước ngầm thì không.
- **`E0-11b`** nay tính `mixed` cho **không cực nào** (ruling F-A2R1-10). Trước đó nó tính `mixed`
  cho cả hai, nên nó báo mọi invariant đã đủ trong khi I04 và I16 không có scenario `negative` nào
  và I14 không có cực nào. Xem §3.4.

### 3.4 Ba scenario mới: SC54, SC55, SC56

SRC-PLAN §7 đòi mỗi invariant có "một counterexample làm gate fail". Sau khi `mixed` thôi được
tính cho cả hai cực, ba invariant lộ ra là không có: **I04** (không cực âm), **I14** (không cực
nào), **I16** (không cực âm).

A2 đã đọc SC16 và SC28 và kết luận rằng **nội dung** của SRC-PLAN §7 vẫn được thỏa — các phản
chứng có thật, chỉ nằm lẫn trong ca hỗn hợp. Tôi giữ nguyên đánh giá đó và **không** đổi nhãn
polarity của SC16/SC28 để làm con số đẹp lên: đổi nhãn cho hợp checker là đúng cái lỗi mà bản
trước đã mắc. Thay vào đó tôi tách phần phản chứng ra thành ba scenario đứng riêng, **không tạo
dữ liệu mới** — cả ba trỏ vào fixture đã có:

| SC | Cực | Invariant | Nội dung | Fixture |
| --- | --- | --- | --- | --- |
| `SC54` | negative | I04 | Hai kết quả `valid` cho cùng `(analysis_key, generation)` là không thể; biến thể gỡ UNIQUE một phần **phải** FAIL | `ai/j-same-key-resubmitted-one-result.json` |
| `SC55` | positive | I14 | Usage không biết ⇒ `unknown = true` với ba trường NULL, và kết quả vẫn được chấp nhận | `ai/k-zero-api-key-…`, `ai/g-cli-json-…` |
| `SC56` | negative | I14, I16 | Ghi 0 cho usage không biết · tự bật fallback chưa cấu hình · đếm một attempt là kết quả — cả ba phải FAIL | `ai/h-provider-unavailable-…`, `ai/i-crash-after-provider-…` |

Phân bố polarity sau đợt này: positive 12 · negative 21 · mixed 23
(`scenario_polarity`). Ba ID mới cần PC00 neo anchor — `CR-PC09-06` mở rộng.

### 3.5 Ba điểm về chính công cụ

- **`NOT_APPLICABLE_FREEFORM` không phải `PASS`, và nay có số kèm.** Theo ruling F-A2R1-08, `E0-15`
  báo `files_without_rows` cho từng thư mục, nên lời khai không thể lệch khỏi số đo. Bảng đầy đủ ở
  §13; điểm chính: **9/11 file trong `ai/`** và **10/13 trong `recovery/`** không dùng
  `rows[]`, nên cửa kiểm cột **không chạm tới chúng**. Bản trước chỉ khai `collection/` và
  `recovery/` — thiếu `ai/`, đúng thư mục chứa các fixture đối kháng prompt-injection.
- **`files_scanned` nay tái lập được.** `evidence/runs/` bị loại khỏi phạm vi quét: một lần chạy
  ghi báo cáo của chính nó vào đó, nên lần chạy sau đếm ra một con số khác (`F-A2R1-11`).
- **Không có validator OpenAPI 3.1** trong môi trường và packet cấm cài. `openapi.yaml` chỉ được
  kiểm như YAML cộng toàn vẹn tham chiếu; tuân thủ đặc tả là `NOT_RUN`.

### 3.6 `E0-12` viết lại: từ một lệnh cấm thành một cửa phạm vi

Trước phê chuẩn, `E0-12-forbidden-strings` làm một việc đơn giản: **không file nào** được mang
`claim_ceiling` cao hơn `DRAFT_FOR_REVIEW`. Nó đúng khi chưa có phê chuẩn nào, và sai ngay khi có
một phê chuẩn — vì lúc đó câu hỏi không còn là *có được tuyên bố cao hơn không* mà là *phạm vi nào
được, và dựa vào đâu*. Theo `CR-PC01-13`, check nay hỏi ba câu:

1. File có nằm trong một trong bốn phạm vi Owner đã phê chuẩn không? Danh sách **không đủ điều
   kiện** được viết cứng trong công cụ: `contracts/http/`, `contracts/ai/`, `contracts/ui/`,
   `contracts/telegram/`, bốn schema chưa phê chuẩn (`worker-assignment`, `ingest-receipt`,
   `analysis-result`, `saved-snapshot`), và các thư mục fixture tương ứng. `contracts/ops/` chỉ có
   `deployment.md` đủ điều kiện.
2. Nếu có: file có trích một `ratification_ref` không?
3. `ratification_ref` đó có **phân giải được** không — đúng `OD-20260907-01` **và**
   `precode/owner-decisions.md` phải tồn tại trên đĩa?

Câu 2 và 3 là check mới `E0-12b-ratification-refs`. Nó tồn tại vì một `claim_ceiling` cao hơn mà
không trỏ về biên bản nào là một lời tự phong; kiểm cả sự tồn tại của biên bản khiến một
`ratification_ref` chép sai hoặc trỏ tới file đã bị xóa **fail**, chứ không im lặng qua cửa.
Mọi claim cao hơn `CONTRACT_READY` (`IMPLEMENTATION_VERIFIED` trở lên) vẫn bị cấm tuyệt đối: chưa
có một dòng code nào.

Đã chạy **negative self-test** trên bản sao ở scratch, tiêm ba khuyết tật: `CONTRACT_READY` trong
phạm vi không đủ điều kiện (`contracts/ai/tasks.yaml`), `CONTRACT_READY` bị gỡ mất
`ratification_ref` (`contracts/state/run.yaml`), và một claim vượt trần (`contracts/errors.yaml`).
**Cả ba đều bị bắt.** Bản sạch cho 0 vi phạm.

Hai điều tôi đã phải nới rộng, ghi ở đây thay vì để im: `evidence/coordination/` được thêm vào
danh sách tiền tố "bản ghi điều phối" (các file đó *thuật lại* từ vựng claim nên không phải là
tuyên bố của chính chúng), và `ACCEPTED_WORKING_VALUE` / `RATIFIED` / `PROVISIONAL` được thêm vào
từ vựng trạng thái hợp lệ theo `owner-decisions.md` §4. Cả hai là nới rộng có chủ ý sau khi đọc
từng trường hợp một, không phải làm ngơ cho một FAIL.

### 3.7 `Check.finalize()` — một check qua cửa mà không kiểm gì thì không phải PASS

Khi viết lại `E0-10b` tôi làm `E0-10a` thoái hoá về `items_checked: 0` **trong khi vẫn báo PASS**.
Không có gì trong công cụ phát hiện điều đó. Nay mọi check chạy qua `Check.finalize()`: PASS với 0
mục kiểm được chuyển thành **`BLOCKED`**. Đây là cùng một lớp lỗi với mọi finding của audit trong
gói này — một phát biểu đúng nhưng không có gì bắt nó phải đúng.

### 3.8 `E0-18` mới — cửa kiểm mà sự vắng mặt của nó gây ra `F-A2R5-01`

Quyết định có hậu quả lớn nhất mà Owner đưa ra là phạm vi `data.purge_all`. Nó được áp đúng ở
`ports.yaml` và `entities.yaml`, và **không** được áp ở sáu artefact khác — trong đó có SC44, oracle
nghiệm thu của chính thao tác đó. Không check nào thấy, vì **không check nào so sánh những gì các
artefact nói về purge**. `E0-18-purge-set-agreement` làm hai việc:

1. **Toàn vẹn phân hoạch.** Ba tập trong `entities.yaml` `TXN-purge-all` phải **rời nhau đôi một**
   và **phủ kín** danh sách entity: 37 xóa + 21 giữ + 2 never_purged = **60 = tổng số entity**.
   Một bảng thêm vào sau này mà không được phân loại sẽ **FAIL ở đây**, thay vì lặng lẽ rơi vào
   nhóm "không được oracle nào khẳng định" — đó chính là cách fixture `l` từng chỉ nêu 8 trong 20
   bảng và tự nhận là không khẳng định gì.
2. **Không artefact nào còn gọi phạm vi purge là chưa quyết.** Mọi
   `OWNER_DECISION_REQUIRED` / `PROV-PC00-01` / `PROV-PC01-03` trong một đoạn có nhắc purge phải
   nằm trên một dòng (hoặc dòng liền kề, vì YAML gấp dòng theo độ rộng chứ không theo nghĩa) có
   đánh dấu **lịch sử** hoặc gọi tên phê chuẩn đã đóng nó. Đây là điều đã bắt được cả sáu artefact
   nếu nó tồn tại trước đó.
3. Cộng: một danh sách purge **có cấu trúc** ở bất kỳ artefact nào khác phải **bằng đúng** tập có
   thẩm quyền.

**Điều `E0-18` KHÔNG làm, ghi ra thay vì để một PASS ngụ ý.** Bản đầu tiên tôi viết có so **tập
hợp các liệt kê trong văn xuôi**: nó cho 24 vi phạm mà khoảng 20 là sai — bất kỳ đoạn nào nhắc
"purge" gần năm tên bảng đều dính, và `entities.yaml` dính chỉ vì nó tồn tại. Một check ồn còn tệ
hơn không có check: nó dạy người đọc bỏ qua đầu ra của chính nó. Tôi đã **gỡ** phần đó. Liệt kê
trong văn xuôi vì thế **vẫn chưa được đối chiếu tự động** — giới hạn này nằm ở §13, không nấp sau
một PASS.

### 3.9 `F-A2R5-03`: cửa phê chuẩn của tôi vượt được bằng một câu văn

Ở FIX7 tôi dựng `E0-12`/`E0-12b` để canh ranh giới phê chuẩn, chạy self-test âm với ba đột biến,
và báo "cả ba đều bị bắt". Auditor thử một đột biến thứ tư mà tôi đã không nghĩ tới — **M6b**:
chuyển `ratification_ref` **ra khỏi** header và để lại một dòng văn xuôi nhắc chuỗi đó. Cả hai
check **PASS**, và `E0-12b` chỉ đơn giản đếm ít đi một mục: file **rời khỏi tập được kiểm** thay vì
bị báo. Oracle thật của tôi hoá ra là *"chuỗi xuất hiện ở đâu đó và phân giải được"*, không phải
*"header hợp đồng mang nó"*.

Đã sửa ở hai chỗ: `ratification_ref_of()` nay **chỉ** đọc header đã parse (front-matter, khóa
YAML top-level, `x-contract`, `info.x-contract`) và **không còn regex dự phòng** trên văn bản; và
eligibility chuyển từ **denylist trong mã** sang **allowlist tường minh trong dữ liệu**
(`precode/gates.yaml` → `ratified_contract_scopes`, trích `OD-20260907-01`). Polarity cũ mặc định
*đủ điều kiện* cho mọi file mới dưới `contracts/` hay `acceptance/` — đó là nguyên nhân trực tiếp
của `F-A2R5-04`. Nay mặc định là **không đủ điều kiện**, và mở rộng phạm vi phê chuẩn là một lần
sửa hợp đồng, không phải một lần sửa công cụ.

Self-test âm nay có **năm** đột biến, chạy hai lượt (§5b của `evidence/tools/README.md`): M5, M6b,
M6c, M7 ở lượt A — **cả bốn bị bắt**; M8 (allowlist không còn trích phê chuẩn) ở lượt B — **cả hai
check chuyển `BLOCKED`**, không PASS. M8 phải tách riêng: một check đã `BLOCKED` không báo vi phạm
nào, nên nếu chạy chung nó sẽ **che** cả bốn đột biến kia và lượt chạy trông như bốn lần trượt.
Tôi biết điều đó vì lần chạy đầu đúng như vậy.

---


## 4. Trạng thái audit

### 4.1 Trạng thái audit — **nguồn duy nhất của sự thật cho trạng thái này trong toàn bản**

Mọi mục khác của bản này trỏ về đây thay vì nhắc lại. `F-A2R2-01` xảy ra chính vì trạng thái audit
được viết ở bốn chỗ và ba chỗ không được quét lại khi nó đổi; kỷ luật `numbers.json` áp cho *số*
nay áp cho cả *trạng thái*.

**8 AUDIT_REPORT độc lập đã chạy**: `A1-R1`, `A1-R2`, `A1-R3`, `A2-R1`, `A2-R2`, `A2-R3`,
`A2-R4`, `A2-R5`. Bảy bản đầu đã được lưu vào repo tại `evidence/audits/`, **nguyên vẹn từng
byte** so với bản gốc (đã kiểm bằng sha256 từng file); `A2-R5` còn ở thư mục scratch của
Coordinator tại thời điểm bản này. Chúng **không** được đăng ký thành evidence record — một
Worker không được ghi bản ghi bằng chứng thay cho Auditor — nên `evidence/index.json` nêu **hai**
con số: `independent_audit_reports_archived_in_repo` = 7 và `independent_audit_records_in_repo`
= 0 (`F-A2R5-06`: câu cũ nói "ba báo cáo, NGOÀI repo, không đăng ký" và đã sai ở hai mệnh đề đầu).

Cột **Verdict** dưới đây chép **đúng từ verdict** của mục "Overall verdict" trong chính bản
AUDIT_REPORT tương ứng — không tóm tắt, không diễn giải. `F-A2R4-01` phát ra vì dòng `A2-R3` từng
để một mô tả *phạm vi* vào ô *verdict*; sửa bằng cách lấy từ nguồn, cùng kỷ luật đã áp cho tên
epoch và cho số đã render.

| Vòng | Phạm vi | Verdict (chép từ report) | Finding |
| --- | --- | --- | --- |
| `A1-R1` | FC-W1 epoch 1 (PC00–PC02) | FAIL | 9 (4 MAJOR, 5 MINOR) — tất cả **VERIFIED** ở R2 |
| `A1-R2` | FC-W2 epoch 2 (+PC03, PC04) | FAIL | 6 (3 MAJOR, 3 MINOR) — tất cả **VERIFIED** ở R3 |
| `A1-R3` | FC-W3 epoch 3 (+PC05–PC08) | FAIL | 5 (1 MAJOR, 4 MINOR) — `FIX_PROPOSED`, xác minh ở A2-R1 |
| `A2-R1` | FC-W4 epoch 4 | **FAIL cho PC09** | 11 (2 MAJOR, 3 MEDIUM, 4 LOW, 2 INFO) |
| `A2-R2` | epoch 5 | **PASS tổng thể** | 10 VERIFIED · 1 PARTIAL · 0 NOT_VERIFIED; **4 finding LOW mới**, cả bốn thuộc PC09 |
| `A2-R3` | epoch 6 (chỉ diff bản sửa FIX9) | **PASS** (scoped, ceiling `DRAFT_FOR_REVIEW`) | 3 VERIFIED · 2 PARTIAL · 0 NOT_VERIFIED; **3 finding LOW mới** (`F-A2R3-01..03`), cả ba thuộc PC09 và đã sửa ở đợt FIX10 |
| `A2-R4` | epoch 7 (`F-A2R3-01..03` + fix diff) | **PASS** (scoped, ceiling `DRAFT_FOR_REVIEW`) | 4/4 VERIFIED · 0 PARTIAL · 0 NOT_VERIFIED; **1 finding LOW mới** (`F-A2R4-01`), thuộc PC09 |
| `A2-R5` | epoch 8 — toàn bộ đợt phê chuẩn | **FAIL** (scoped, ceiling `DRAFT_FOR_REVIEW`) | 7 finding mới: 1 MAJOR (`-01`), 3 MEDIUM (`-02`, `-03`, `-04`), 3 LOW (`-05`, `-06`, `-07`). Verdict theo gói: 10 gói PASS, **PC09 FAIL** |

**Hai MAJOR của A2-R1 đều là lỗi của tôi và cùng một hình dạng:** một điều đúng được viết ra rồi
không được biến thành thứ tự động kiểm được. `F-A2R1-01` — chín id operation không tồn tại trong
`event_order` của tám scenario, đúng lớp lỗi mà §13 của bản trước đã cảnh báo bằng chữ.
`F-A2R1-02` — bốn con số headline mâu thuẫn với artefact, hai trong số đó mâu thuẫn với bảng ngay
bên dưới chúng, và cả bốn lệch theo hướng có lợi.

A2-R2 xác nhận cả hai đã được đóng **theo cách bền**: mỗi cái nay được canh bởi một cửa kiểm máy
(`E0-04b`/`E0-04c`/`E0-04d`; script sinh số) chứ không bởi một câu đã sửa. A2 cũng tự tiêm một
khiếm khuyết mỗi loại vào bản sao và xác nhận ba check mới không phải đồ trang trí.

**Bốn finding LOW của A2-R2 (`F-A2R2-01…04`) — trạng thái tại bản này:**

| Finding | Nội dung | Đã làm ở đợt FIX9 |
| --- | --- | --- |
| `F-A2R2-01` | Ba câu cũ trong `review.md` mâu thuẫn với các mục khác của chính nó: DoR dòng 11 ghi epoch `FCW4c`, §9 và §13 còn nói "A2 chưa chạy" | Epoch ở dòng 11 nay đọc từ card (`card_pin_current`, cùng nguồn với §9.1); trạng thái audit gom về **một chỗ duy nhất** là mục này; §13 mục 9 đếm số report từ đĩa |
| `F-A2R2-02` | DoR dòng 5 vẫn liệt kê năm ngoại lệ đã được vá | Dòng 5 quay lại ✅, và danh sách ngoại lệ nay **sinh từ `ports.yaml`** (`dor5`), nên một lỗ hổng được vá sẽ tự đóng dòng |
| `F-A2R2-03` | `numbers.json` / `cr_summary.json` được trích dẫn nhưng nằm ngoài candidate | Cả hai nay được sao vào `evidence/runs/` kèm dấu thời gian của lần chạy và được trích **theo đường dẫn** |
| `F-A2R2-04` | Quy tắc null-operation bị năm trên sáu case vi phạm, và check ghi nó là *note* | `E0-10b` nay coi đó là **violation**; W2 đã bổ sung `event_type` cho cả năm case (`PKT-PC01-FIX12`) |

**Ba finding LOW của A2-R3 (`F-A2R3-01…03`) — đã sửa ở đợt FIX10:**

| Finding | Nội dung | Đã làm |
| --- | --- | --- |
| `F-A2R3-01` | DoR dòng 11 vẫn in một epoch cũ **trong khi tự khai là "đọc từ card"** — một khẳng định provenance sai, mạnh hơn một giá trị cũ trần | Dòng 11 **không còn nhắc lại epoch**; nó trỏ về §9.1, nơi duy nhất giá trị này được in. Một sự thật, một nguồn, in một lần |
| `F-A2R3-02` | Lệnh `grep` được công bố làm nguồn thật ra trả **bảy** tên epoch, không phải một | Lệnh công bố nay là chính quy tắc mà bộ sinh áp dụng (`card_pin_command`), và nó trả **đúng một** giá trị — đã chạy để kiểm |
| `F-A2R3-03` | Hai placeholder định dạng chưa được thay thế ngay ở câu mở đầu §4.1 — một dòng "được sinh" mà vẫn ship kèm placeholder thì chưa thật sự được sinh | Đã render từ `audit_reports`; và cổng tự kiểm nay **quét placeholder chưa thay** trên toàn file, nên lớp lỗi này không thể lặp im lặng |

### A2-R5 — verdict FAIL, và cả bốn finding nặng là của PC09

`A2-R5` là vòng audit đầu tiên soi **toàn bộ** đợt phê chuẩn. Kết luận: phê chuẩn được chép lại
trung thành và áp dụng đúng **ở nơi nó được định tuyến tới**, nhưng không được quét cho **mọi nơi
nó chạm tới**. Mười gói PASS; **PC09 FAIL** — và cả bốn finding nặng đều nằm trong deliverable của
tôi. Trạng thái xử lý ở đợt FIX8 này:

| Finding | Sev | Nội dung | Đã làm ở FIX8 |
| --- | --- | --- | --- |
| `F-A2R5-01` | **MAJOR** | Phạm vi `data.purge_all` đã phê chuẩn được áp ở hai hợp đồng và **không** được áp ở sáu artefact — một trong số đó là **SC44, chính oracle nghiệm thu** của thao tác này. Corpus đồng thời báo quyết định *đã chốt* và *còn treo* | SC44 viết lại: oracle nay khẳng định **đủ ba tập** (37 xóa · 21 giữ · 2 never_purged) thay vì né tránh, cộng oracle công bố về backup và một phép kiểm Owner vẫn đăng nhập được. **`E0-18` mới** biến quy tắc chung thành cửa kiểm máy (§3.8) |
| `F-A2R5-02` | MEDIUM | Lần chạy E0 đóng gói **không pin đúng bytes nó chứng nhận**: 2 trong 136 hash lệch, vì `PKT-PC00-FIX11` land sau khi tôi chạy | Lần chạy đóng gói của FIX8 đặt **sau** cổng chờ mọi packet nội dung của đợt (`PKT-PC02-FIX11`, `PKT-PC10-FIX11`), và tôi so `baseline_hashes` với bytes trên đĩa trước khi bàn giao |
| `F-A2R5-03` | MEDIUM | Cửa phê chuẩn **thoả mãn được bằng một câu văn**: M6b chuyển `ratification_ref` ra khỏi header, để lại một dòng prose — cả hai check vẫn PASS, file chỉ **rời khỏi tập được kiểm**. Và eligibility là **denylist** trong khi ruling nói allowlist | `ratification_ref` nay **chỉ** đọc từ header đã parse (front-matter / khóa top-level / `x-contract`), không còn regex trên văn bản. Eligibility thành **allowlist tường minh** nằm trong `precode/gates.yaml` `ratified_contract_scopes`, không nằm trong mã. M6b thêm vào self-test và **bắt được** (§3.9) |
| `F-A2R5-04` | MEDIUM | Ba file `CONTRACT_READY` nằm ngoài bốn phạm vi — hệ quả trực tiếp của polarity denylist | Ruling đưa `ops/deployment.md` và hai thư mục fixture `identity/`, `reporting/` vào phạm vi; allowlist nêu **đích danh** từng file/thư mục, kèm lý do. Một file mới nay **không đủ điều kiện** cho tới khi có người cố ý thêm |
| `F-A2R5-06` | LOW | `honesty_note_vi` của `evidence/index.json` đã thành sai: "ba báo cáo, ngoài repo" | Sửa; số báo cáo **đếm từ thư mục**, và hai con số (7 lưu trữ / 0 đăng ký) được nêu tách bạch cùng lý do |
| `F-A2R5-05`, `-07` | LOW | Ba schema thiếu câu NOT_RUN; manifest bỏ sót `agent_profile/` | Không thuộc grant của tôi — W3/W5 và Coordinator |

**Điều tôi muốn người đọc thấy rõ nhất về vòng này.** Cả bốn finding nặng có **cùng một hình
dạng**, và đó là hình dạng đã lặp lại suốt gói này: *một điều đúng được viết ra, rồi không có gì
bắt nó phải tiếp tục đúng.* `F-A2R5-01` là bản nặng nhất của nó — không phải vì ai viết sai, mà vì
**không tồn tại cửa kiểm nào so sánh những gì các artefact NÓI về purge**. `E0-18` được thêm chính
xác để lấp chỗ đó. `F-A2R5-03` thì chỉ ra rằng cửa kiểm tôi vừa dựng ở FIX7 để canh phê chuẩn có
thể vượt qua bằng một câu văn — nghĩa là ở FIX7 tôi đã báo "23/23 sạch" bằng một cửa mà chính tôi
chưa thử phá đúng cách. Bài học không phải "sửa M6b" mà là: **một cửa kiểm mới chưa bị tấn công
thì chưa phải bằng chứng.**

**`F-A2R4-01` — LOW, của tôi — đã sửa ở đợt trước.** Nội dung: cột *Verdict* của bảng trên mang một
mô tả phạm vi ("xác minh bản sửa FIX9") ở dòng `A2-R3` thay vì verdict thật, trong khi A2-R3 kết
luận **PASS**. Đây là mục §4.1 — chính chỗ bản này khai là nguồn duy nhất cho trạng thái audit —
nên một ô không phải verdict ở đây tệ hơn ở nơi khác. Đã sửa bằng cách **chép từ report**, và ghi
rõ trong tiêu đề cột rằng đó là điều đang xảy ra. `F-A2R4-01` là `FIX_PROPOSED`; tôi không đóng nó.

**Lượt xác minh đang chờ.** A2 chưa kiểm lại bản sửa của chính đợt này — bao gồm `E0-12`/`E0-12b`,
bảng module viết lại sau phê chuẩn, và tuyên bố theo phạm vi ở §12. Theo protocol §8 tôi không
được tự xác minh bản sửa của mình, nên "**24/24 PASS, 0 vi phạm**" ở §3 là **con số của phía sửa,
chạy bằng công cụ do phía sửa viết** — bằng chứng cần được kiểm, không phải một verdict. Điều này
áp **đặc biệt** cho `E0-12b`: một check do tôi viết, tự xác nhận rằng các `ratification_ref` do
các gói khác viết là hợp lệ, chưa từng được ai ngoài tôi chạy.


### 4.2 Hai mươi finding của A1 — trạng thái

PC09 **không đóng cái nào**: chỉ designated disposition authority mới ký CLOSED.

| Vòng | Finding | Sev | Trạng thái tại 2026-09-07 | Ghi chú |
| --- | --- | --- | --- | --- |
| R1 | F-A1R1-01 … -09 (9) | 4 MAJOR, 5 MINOR | **VERIFIED** bởi A1-R2 | Verification verdict, không phải closure |
| R2 | F-A1R2-01 … -06 (6) | 3 MAJOR, 3 MINOR | **VERIFIED** bởi A1-R3 | Như trên |
| R3 | F-A1R3-01 | MAJOR | **FIX_PROPOSED** | Ruling R4-01 đã ra; các gói fixture đã land; lần chạy E0 của PC09 cho **0 unresolved** trên tám thư mục đo được. Chờ A2 |
| R3 | F-A1R3-02 | MINOR | **FIX_PROPOSED** | Khóa `operation` thống nhất và `edge_assertion: forbidden` ratify bởi R4-02; `E0-14` thực hiện cả hai và **fail loudly** khi gặp key không nhận ra. Chờ A2 |
| R3 | F-A1R3-03 | MINOR | **FIX_PROPOSED** | PC00 neo SC45–SC48; ruling R5-06 giao PC00 neo tiếp SC49–SC53 từ `subject_vi` của `acceptance/scenarios.yaml`. Chờ A2 |
| R3 | F-A1R3-04 | MINOR | **FIX_PROPOSED** | README của `telegram/` liệt kê đủ file theo tên; `E0-08` báo riêng trường hợp README chỉ liệt kê bằng glob. Chờ A2 |
| R3 | F-A1R3-05 | MINOR | **FIX_PROPOSED** | Ratify bởi R4-04; `E0-02` chấp nhận `allOf`+`if/then` **khi và chỉ khi** có `x-contract.deviations` khai báo. Chờ A2 |

### 4.3 Bảy CR của PC09 — trạng thái

| CR | Trạng thái | Cách xử lý |
| --- | --- | --- |
| `CR-PC09-01` (12 scenario thiếu fixture) | **FIX_PROPOSED** | Ruling R5-02; 12 fixture đã tồn tại, `fixture_refs` đã điền, `E0-16` PASS |
| `CR-PC09-02` (26 cạnh thiếu mã lỗi) | **FIX_PROPOSED** | Ruling R5-01; 36/36 cạnh có mã, `E0-10b` PASS |
| `CR-PC09-03` (50 dòng PARTIAL) | **FIX_PROPOSED một phần** | Ruling R5-03 đóng nhóm "thật"; còn 38 dòng, phần lớn là gate-only hoặc contract-only hợp lý (§2) |
| `CR-PC09-04` (TSR-A01 mâu thuẫn) | **FIX_PROPOSED** | Ruling R5-04; `E0-09` PASS |
| `CR-PC09-05` (README/fixture (i) nói FORBIDDEN_EDGE) | **FIX_PROPOSED** | Ruling R5-05 giao W2 |
| `CR-PC09-06` (anchor SC49–SC53) | **OPEN** | Ruling R5-06 giao W1; PC00 chưa neo SC49–SC53 tại thời điểm bản này |
| `CR-PC09-07` (change-control vs INV-01..10) | **OPEN** | Ruling R5-07 giao W7 ở PC10-FIX1, sau khi FIX5 land |
| `CR-PC09-08` (kiểm "mỗi hạng mục P0 có ≥ 1 card" chưa thành check thường trực) | **OPEN** | Mới, phát ra ở bản này — xem §9.1 |

Không CR nào ở trên được PC09 tự đóng. Trạng thái đúng của tất cả là `FIX_PROPOSED` hoặc `OPEN`
cho tới khi A2 xác minh.

---

## 5. Rà soát lại B01–B17 — sau phê chuẩn

Cả 17 blocker nay **`RATIFIED (OD-20260907-01)`** trong `precode/decision-register.md` §1–§2, và
`agent_profile/registry.json` có `open_product_blockers: []`. Bảng dưới ghi điều **còn lại** sau
phê chuẩn — vì phê chuẩn chốt *văn bản cam kết*, không tạo ra *bằng chứng*.

| ID | Mục trong `OD-20260907-01` | Còn lại sau phê chuẩn |
| --- | --- | --- |
| B01 | 5 — freeze tại publish | Không còn gì ở mức hợp đồng. Bằng chứng chạy thật: `NOT_RUN` (SC05/SC19) |
| B02 | 6 — bốn trường trạng thái, câu chữ AC-03 | Không còn gì ở mức hợp đồng. 13/13 dòng ánh xạ đã được A1 xác minh verbatim |
| B03 | 7 — `delivery.unknown`, câu chữ AC-14 | Không còn gì ở mức hợp đồng. SC14 `NOT_RUN` |
| B04 | 8 + 22 — sổ coverage riêng, **phương án (b)** cho kỳ rỗng | Owner chấp nhận đúng lựa chọn trái khuyến nghị mà PC04 đã ghi đường đảo. Ngưỡng vẫn `uncalibrated` cho tới A2 |
| B05 | 9 — không ingest trùng theo post ID, câu chữ AC-04 | **REQ-A1 vẫn `KC`**: độ ổn định con trỏ feed chỉ đo được bằng probe SP1, chưa chạy |
| B06 | 10 — alias + phiên bản + target union | Không có amendment văn bản; mô hình dữ liệu bổ sung ACCEPTED. `ADR-0009` accepted |
| B07 | 11 — analysis key + generation | Không còn gì ở mức hợp đồng |
| B08 | 4 — một IANA timezone, **`Asia/Ho_Chi_Minh` được xác nhận** | Rủi ro lớn nhất của bản trước đã tắt: fixture lịch của PC03/PC04 **giữ nguyên**, không phải dựng lại (INV-10 không kích hoạt) |
| B09 | 12 — ngoại lệ hẹp cho mã liên kết | Ba con số (định dạng, hạn 15 phút, 5 lần/giờ) nay là **giá trị làm việc được chấp nhận**, không còn `PROVISIONAL` chờ ai |
| B10 | 13 + 25 — ba lệnh, resume trong app, resume-từ-`blocked` có lý do bắt buộc | `PROV-PC00-02` và `PROV-PC00-04` accepted. Không còn gì ở mức hợp đồng |
| B11 | 14 + 23 — snapshot nhất quán + manifest + drill; RPO 24 h / RTO 2 h | **Chưa drill nào chạy.** Runbook là thiết kế, không phải bằng chứng. Đây là khoảng cách lớn nhất còn lại của B11 |
| B12 | 1 + 2 — profile Chrome riêng; bỏ cạnh `COL→AW` | **`REQ-OQ01` đã được trả lời; D09 không còn chặn M0/SP1.** Probe SP1 vẫn `NOT_RUN` — đó là điều duy nhất còn lại |
| B13 | 15 — secret theo phạm vi, tool CLI tắt, disabled-until-verified | **AC-16 vẫn `BLOCKED`** theo đúng lời phê chuẩn, cho tới khi một probe đạt. **REQ-A5 (`KC`)** — điều khoản từng nhà — chưa đọc. Mọi adapter `enabled=false` |
| B14 | 16 — `insufficient_evidence` khi thiếu dữ liệu | **D53 vẫn `ĐX`-trong-P0 ở phần hiệu chỉnh tham số.** Cổng là **REQ-A4 (`KC`)**: cần 3–4 kỳ thật, hiện có 0 kỳ |
| B15 | 17 — chỉ số có phạm vi + đếm `identity_conflict` | Không còn gì ở mức hợp đồng |
| B16 | 18 — ba loại phát biểu + `comparator: unknown`, câu chữ AC-11 | Rubric groundedness chưa chạy (E4) |
| B17 | 19 — chỉ mục được chọn, `partial` kèm pending list | Không còn gì ở mức hợp đồng |

**Đánh giá tổng.** Trước phê chuẩn, cột "điều còn thiếu" của mười bốn dòng là *một chữ ký*. Nay
không dòng nào chờ chữ ký. Điều còn lại rơi đúng vào hai loại: **phép đo chưa chạy** (B05, B11,
B12, B13, B14, B16) và **hiệu chỉnh tham số cần dữ liệu thật** (B04, B14). Không loại nào phê
chuẩn giải quyết được, và tôi ghi rõ điều đó ở đây để bản này không bị đọc thành "đã xong".

Một điểm cần nói thẳng: **Owner chọn stack B, trái với phương án A mà `ADR-0006` đã khuyến nghị.**
Quyết định đó hợp lệ và tôi không đánh giá lại nó, nhưng nó có giá: §3 (đường dẫn) và §8 (lệnh
build/test) của **cả 18 task card** phải viết lại, và trước khi việc đó xong thì không có mô tả
đúng nào về nơi code sẽ nằm. Hợp đồng **không** đổi theo stack — đó là lý do bốn phạm vi vẫn có
thể lên `CONTRACT_READY`.

---

## 6. Sổ ĐX / KC — rà soát

### 6.1 Các mục P0 còn `ĐX` — và một mâu thuẫn tôi tìm thấy khi đo lại

**42** trong 234 dòng P0 mang status `ĐX` (giảm từ 46: D08, D09, D42, D50 đã lên `XN` với ghi chú
`Ratified OD-20260907-01`). Phân bố P0 hiện tại, đếm từ `precode/requirements.csv`:
**XN 140 · ĐX 42 · UQ 37 · KC 15**.

- **`REQ-D09` nay là `XN`.** Đây là thay đổi có ảnh hưởng lớn nhất trong mục này: D09 từng **chặn
  M0**, và bản review trước liệt kê nó đứng đầu. Owner chọn **profile riêng của dự án**
  (`OD-20260907-01` mục 1), nên `collector-probe.md` và `deployment.md` **không** phải viết lại.
- **`REQ-D53` vẫn `ĐX`** — đúng như phê chuẩn nói (mục 16: "D53 vẫn ĐX-trong-P0 chỉ ở phần hiệu
  chỉnh tham số"). Khối "hướng đang nổi" vẫn trong MVP về mặt thuật toán, nhưng bảy tham số của
  nó chỉ chốt được sau khi REQ-A4 có dữ liệu. **PC09 không promote nó.**

**Mâu thuẫn cần một CR, không phải một lần sửa lén.** `REQ-OQ01` và `REQ-OQ02` vẫn mang status
`ĐX` trong `precode/requirements.csv`, với ghi chú `PROVISIONAL: … cần Owner xác nhận`. Nhưng
`OD-20260907-01` mục 1 trả lời đúng OQ01 (profile riêng) và mục 3 trả lời đúng OQ02 (stack **B**,
không phải Option A mà ghi chú của OQ02 đang nói). Hai dòng này nay **nói sai về thực tế**.
`precode/requirements.csv` không nằm trong grant ghi của PC09, nên tôi **không sửa** — phát ra
**`CR-PC09-13`** (chủ sở hữu: W1/PC00): cập nhật status và ghi chú của `REQ-OQ01`, `REQ-OQ02` theo
mục 1 và mục 3, và kiểm lại xem còn dòng `PROVISIONAL` nào khác đã bị phê chuẩn vượt qua. Cho tới
khi CR đó đóng, các con số P0 ở trên là số **đo được trên đĩa**, không phải số **đúng theo phê
chuẩn** — và tôi báo số đo được.

### 6.2 Các mục `KC` — cần kiểm chứng, có cổng

15 dòng mang status `KC`. Từng dòng có một cổng thật, không dòng nào bị coi là đã giải:

| REQ | Nội dung | Cổng | Trạng thái |
| --- | --- | --- | --- |
| `REQ-A1` | Phiên Chrome thu thập đều đặn ở mức đủ dùng | SP1 (5–10 đợt thật) | `NOT_RUN` |
| `REQ-A2` | Ngưỡng embedding tách được bài khớp tag | G7-X5 + §7.1 dưới đây | `NOT_RUN`; ngưỡng `0.8000` mang nhãn `PROVISIONAL_BOOTSTRAP` và `threshold_calibration_state='uncalibrated'` |
| `REQ-A3` | Model đa ngôn ngữ đủ tốt trên thuật ngữ khoa học | §7.2 | `NOT_RUN` |
| `REQ-A4` | Mật độ vector phát hiện được hướng nổi thật | G7 + §7.3 | `NOT_RUN`; cần 3–4 kỳ, hiện 0 |
| `REQ-A5` | Điều khoản từng nhà AI cho đường CLI/ACP | `cli-acp-probe.md` §6 | `NOT_RUN`; mọi adapter `enabled=false`. Phê chuẩn mục 15 **giữ nguyên** `AC-16 BLOCKED` cho tới khi một probe đạt |
| `REQ-A6` | Nhịp gọi arXiv và yêu cầu của OpenAlex | G3-X5 | `NOT_RUN`; bốn giá trị `PLACEHOLDER_KC` = null, sàn thận trọng `min_interval_ms = 3000` |
| `REQ-A7` | X có thể hạn chế tài khoản dù người dùng tự giải CAPTCHA | — | **Không kiểm chứng được trước.** Xử lý bằng điều kiện dừng rõ ràng (SC04), không bằng một lời hứa |
| `REQ-D34` | Nhịp gọi arXiv/OpenAlex — đọc tài liệu chính thức | như REQ-A6 | `NOT_RUN` |
| `REQ-D47` | Ngưỡng tương đồng hiệu chỉnh bằng dữ liệu thật | như REQ-A2 | `NOT_RUN` |
| `REQ-OQ08` | Ngưỡng tương đồng embedding | G7-X5 | Chờ dữ liệu sau M3 |
| `REQ-OQ09` | Model embedding cụ thể | sau A3 | Chờ |
| `REQ-S1.4-04` | Số lần người dùng phải can thiệp xác minh X | SP1 | `NOT_RUN` |
| `REQ-S10.2-06` | Điều khoản provider trước khi bật CLI/ACP | như REQ-A5 | `NOT_RUN` |
| `REQ-S13.2-01` | Đọc tài liệu arXiv/OpenAlex khi triển khai | như REQ-A6 | `NOT_RUN` |
| `REQ-S13.2-02` | Đọc điều khoản từng nhà AI trước khi bật CLI/ACP | như REQ-A5 | `NOT_RUN` |

**Phê chuẩn không chạm vào bảng này.** Cả 15 dòng vẫn `KC` sau `OD-20260907-01`, và đó là kết
quả đúng: Owner phê chuẩn được văn bản cam kết, không phê chuẩn được nhịp gọi của arXiv hay chất
lượng của một model embedding. Mọi dòng `KC` trong `acceptance/traceability.csv` nay mang thêm một
câu ở cột `notes`: *phê chuẩn không thay thế được phép đo*.

**Không giá trị `KC` nào bị bịa.** `research_connector_rate_limit` giữ bốn `null` với
`status: PLACEHOLDER_KC`; PC05 tự ghi rằng research connector **không được** coi là `CONTRACT_READY`
cho tới khi chúng được điền. Cách xử lý này là đúng và nên giữ.

---

## 7. Thiết kế đánh giá A2 / A3 / A4 — rubric khóa TRƯỚC khi đo

Nguyên tắc chung của SRC-PLAN §14.2, áp cho cả ba: **định nghĩa rubric trước khi đo**; dùng dữ liệu
có nhãn độc lập; **tập dò ngưỡng tách khỏi tập đánh giá**; nêu rõ denominator và ai đánh giá; thiếu
dữ liệu thì ghi `insufficient_evidence`, **không chỉnh số để pass**.

Cả ba thiết kế dưới đây là `NOT_RUN`. Chúng cần Owner khóa (cổng G7-X1) trước khi bất kỳ số liệu
nào được thu.

### 7.1 A2 — ngưỡng tương đồng embedding tách được bài khớp tag khỏi bài không khớp

- **Câu hỏi:** với một tag T và một nhãn chủ đề L, ngưỡng cosine nào tách được "khớp" khỏi "không
  khớp" ở mức chấp nhận được cho một người dùng duy nhất?
- **Đơn vị đo:** một cặp `(tag, work_label)`. **Denominator:** tổng số cặp trong tập đánh giá.
- **Tập dữ liệu:** 50–100 bài được **gán nhãn tay** bởi Owner (SRC-SPEC §3.8 A2), lấy từ kho thật
  sau M0–M2. Chia **ngẫu nhiên có seed ghi lại** thành **tập hiệu chỉnh 60 %** và **tập đánh giá
  40 %**. Ngưỡng CHỈ được dò trên tập hiệu chỉnh; tập đánh giá được mở đúng một lần cho mỗi lần
  báo cáo kết quả.
- **Rubric nhãn (khóa trước):** mỗi cặp được Owner gán một trong ba: `match` (bài này thuộc mối
  quan tâm của tag), `not_match`, `ambiguous`. Cặp `ambiguous` **bị loại khỏi denominator** và số
  lượng của chúng được báo cáo riêng — tỷ lệ `ambiguous` cao là một kết quả, không phải một phiền
  toái cần giấu.
- **Tiêu chí thành công:** trên tập đánh giá, tồn tại một ngưỡng cho **precision ≥ 0.80** với
  **recall ≥ 0.60**. Nếu không tồn tại, kết luận là "ngưỡng đơn không tách được" — một kết quả hợp
  lệ dẫn tới thiết kế khác (ngưỡng theo từng tag, hoặc mô hình khác), **không** phải lý do để hạ
  ngưỡng cho tới khi con số đẹp.
- **Ai đánh giá:** Owner, vì "khớp tag" là một phán đoán về mối quan tâm của chính Owner. Không có
  người thứ hai (D01), nên không đo được inter-rater agreement; **giới hạn này phải được ghi trong
  mọi manifest** của A2.
- **Cho tới khi chạy:** ngưỡng giữ `0.8000` với nhãn `PROVISIONAL_BOOTSTRAP` và
  `threshold_calibration_state = 'uncalibrated'`; mọi báo cáo mang `coverage_note` nói rõ; và
  **cấm tuyên bố đạt bất kỳ chỉ tiêu chất lượng nào của SRC-SPEC §1.4** khi còn `uncalibrated`.

### 7.2 A3 — model embedding đa ngôn ngữ đủ tốt trên thuật ngữ khoa học

- **Câu hỏi:** một model đa ngôn ngữ (để gõ tag tiếng Việt khớp nhãn tiếng Anh, REQ-D59) có kém hơn
  một model chỉ tiếng Anh trên thuật ngữ khoa học không, và kém bao nhiêu?
- **Thiết kế:** **so sánh cặp trên CÙNG tập thử** của A2 — cùng 50–100 bài, cùng tập đánh giá,
  cùng rubric. Chỉ đổi một biến: model embedding.
- **Denominator:** cùng denominator của A2 (loại cặp `ambiguous`).
- **Tiêu chí:** model đa ngôn ngữ được chấp nhận nếu precision/recall của nó **không thấp hơn model
  chỉ tiếng Anh quá 0.05 tuyệt đối** ở ngưỡng tốt nhất của mỗi model, VÀ nó xử lý được ít nhất một
  truy vấn tag tiếng Việt mà model chỉ tiếng Anh bỏ sót. Điều kiện thứ hai quan trọng: nếu model
  đa ngôn ngữ không mang lại lợi ích nào bằng tiếng Việt thì lý do tồn tại của nó biến mất.
- **Ràng buộc bắt buộc:** đổi model embedding buộc **tính lại toàn kho** (REQ-D48) và mọi bằng
  chứng chất lượng chuyển `STALE` (INV-04). So sánh phải chạy trên hai generation riêng biệt,
  **không** trộn vector (I12, SC24/SC52).
- **Ai đánh giá:** kỹ thuật, sau A3; model cụ thể (REQ-OQ09) là quyết định kỹ thuật, không phải
  quyết định sản phẩm.

### 7.3 A4 — mật độ vector phát hiện được "hướng đang nổi" thật, không phải nhiễu

Đây là đánh giá khó nhất và là cái dễ tự lừa nhất, vì tham số do chính người thiết kế chọn.

- **Câu hỏi:** trong các khối "hướng đang nổi" mà hệ thống xuất ra, bao nhiêu phần là hướng Owner
  thấy đáng đọc sâu, và bao nhiêu là nhiễu?
- **Mẫu tối thiểu:** **3–4 kỳ báo cáo thật liên tiếp** (SRC-SPEC §3.8 A4). Hiện có **0 kỳ**.
- **Đơn vị đo:** một `emerging_direction` trong một kỳ. **Denominator:** tổng số hướng được xuất ra
  trong các kỳ được đánh giá — **không phải** tổng số hướng "đúng", để tỷ lệ nhiễu không bị pha
  loãng bằng cách xuất ít đi.
- **Rubric (khóa trước khi nhìn kết quả kỳ đầu tiên):** Owner gán mỗi hướng một trong bốn:
  - `useful` — đáng đọc sâu, Owner sẽ mở ít nhất một mục trong đó;
  - `known` — đúng nhưng Owner đã biết, không thêm giá trị;
  - `noise` — gắn nhãn sai, phải bỏ qua;
  - `insufficient` — hệ thống tự khai `insufficient_evidence`, không tính vào tử số lẫn mẫu số.
- **Tiêu chí thành công theo tuần (SRC-SPEC §1.4):**
  - chỉ tiêu chính 1: **≥ 1 hướng `useful` mỗi tuần**, đo trên **≥ 4 tuần liên tiếp**;
  - chỉ tiêu chính 2: **`count(noise) ≤ count(useful)`** trên cùng cửa sổ đó.
  - "Mỗi tuần" nghĩa là tuần lịch theo timezone owner đã xác nhận (B08), không phải "trung bình một
    tuần" — một tuần có 3 hướng và ba tuần có 0 hướng **không** đạt.
- **Ai đánh giá:** Owner. Đánh giá phải được ghi **trước khi** xem tham số mật độ của kỳ đó, để
  không hiệu chỉnh ngược.
- **Điều bị cấm tường minh:** chỉnh `r`, `min_members`, `K`, `min_prior_windows`, `min_delta`, `ε`
  hay `max_emerging_directions` **sau khi** đã nhìn nhãn của Owner cho cùng kỳ đó. Muốn chỉnh thì
  chu kỳ đánh giá bắt đầu lại từ kỳ kế tiếp, và số kỳ đếm lại từ đầu.
- **Thiếu dữ liệu:** dưới 3 kỳ ⇒ kết luận là `insufficient_evidence` cho REQ-A4. Không được ghi
  "đạt" và cũng không được ghi "không đạt" — cả hai đều là tuyên bố vượt quá dữ liệu.
- **Nhãn hiển thị không đổi bất kể kết quả:** khối luôn mang nhãn **"ứng viên để đọc sâu"**, không
  bao giờ là "phát hiện mới" (REQ-D54), và AI chỉ **diễn đạt lại** kết quả đã tính (REQ-S10.1-05).

### 7.4 Điều KHÔNG đo

`REQ-S1.4-05` là một điều kiện **âm** phải giữ: chỉ số "tiết kiệm thời gian đọc" **không** được đưa
vào, vì không đo được một cách trung thực ở bản một người dùng. Nếu về sau có ai muốn thêm nó, đó
là một thay đổi phạm vi cần quyết định của Owner, không phải một cải tiến báo cáo.

---

## 8. Change request — hợp nhất, kèm đề xuất xử lý (KHÔNG phải quyết định)

### 8.1 CR do PC09 phát ra — trạng thái sau đợt FIX5

Bảng đầy đủ nằm ở **§4.3**. Tóm tắt: năm trong bảy CR chuyển `FIX_PROPOSED` nhờ ruling R5-01…R5-05
(mã lỗi cạnh bị cấm, 12 fixture, `requirement_refs` của nhóm thật, TSR-A01, README/fixture (i));
hai CR còn `OPEN` và thuộc gói khác:

| CR | Còn lại gì | Ai |
| --- | --- | --- |
| `CR-PC09-06` | Neo anchor `SC49`–`SC53` vào `precode/baseline.json`, `subject_vi` lấy từ `acceptance/scenarios.yaml`. Phân xử dải đã xong: PC05/PC06 không lấy ID nào, PC07 lấy SC45–SC48 hợp lệ, PC09 cấp SC49–SC53, **không va chạm** | W1 (PC00), ruling R5-06 |
| `CR-PC09-07` | `precode/change-control.md` phải TRÍCH `INV-01`…`INV-10` của `precode/gates.yaml` thay vì định nghĩa lại. Nếu không, lớp lỗi "một hành vi, hai mô tả" lặp lần thứ tư | W7 (PC10-FIX1), ruling R5-07 |
| `CR-PC09-08` | Đưa kiểm tra "mỗi hạng mục P0 (`REQ-P0-01` … `REQ-P0-12`) có ≥ 1 card, trực tiếp hoặc bắc cầu qua scenario" thành một check E0 thường trực, sau khi `agent-tasks/` ổn định. Lần chạy thủ công ở §9.1 cho 12/12 bắc cầu và 0/12 trực tiếp, nhưng một lần chạy tay không ngăn được hồi quy | Coordinator định tuyến (PC09 hoặc PC10 ở lượt sau) |

**Ba CR của đợt FIX6 đã được xử lý ở FIX7:** `CR-PC09-09` (`SAVE_ALREADY_EXISTS`) — W2/W3 gỡ hai
chỗ nhắc trong prose hợp đồng, lịch sử ở lại handoff; `CR-PC09-10` (sáu tên cột không tồn tại) —
W3 thêm sáu cột thật và W5 sửa hai đoạn prose; `CR-PC09-11` (tên operation cũ trong ghi chú
fixture) — W5 viết lại ghi chú. `CR-PC09-12` (8 tham chiếu cột mà `E0-04c` soi tới lần đầu, §3.2)
cũng đã được các gói sở hữu đóng. Cả bốn là `FIX_PROPOSED`, chờ A2 xác minh.

**CR mới của đợt này:**

| CR | Nội dung | Ai | Trạng thái |
| --- | --- | --- | --- |
| `CR-PC09-13` | `REQ-OQ01` và `REQ-OQ02` vẫn `ĐX` với ghi chú `PROVISIONAL` trong `precode/requirements.csv`, trong khi `OD-20260907-01` mục 1 và mục 3 đã trả lời cả hai | W1 (PC00) | **ĐÃ ĐÓNG bởi `PKT-PC00-FIX11`** — A2-R5 xác nhận D08/D09/D42/D50 → XN và sổ yêu cầu khớp phê chuẩn |
| `CR-PC09-14` | Khóa `claim_ceiling` mang hai nghĩa (file tự tuyên bố / trần của công việc được giao); `agent-tasks/` ngoài `SCAN_DIRS` nên 18 card khai nhãn vượt trần mà không check nào thấy | Coordinator | **PARKED** — `E0-12` nay khai đúng phạm vi quét và **đếm + in ra** phần chênh; mở rộng `SCAN_DIRS` cần một ruling, không phải một quyết định của Worker |
| `CR-PC01-13` | `E0-12` phải thành cửa **phạm vi** thay vì lệnh cấm phẳng, kèm kiểm `ratification_ref` phân giải được | W6 — làm ở FIX7 (§3.6), **siết lại ở FIX8** sau `F-A2R5-03` (§3.9) | **FIX_PROPOSED** |
| `CR-PC05-06` / `CR-PC05-07` | `TXN-purge-all` từng xếp `schedule_occurrence` vào **cả hai** tập và xóa `worker_registration`/`data_deletion_audit`, trái mục 20/23; và bản ruling đầu đếm "purged (36)" trong khi văn xuôi của chính nó nêu thêm `telegram_link_attempt` | Coordinator + W3 | **ĐÃ ĐÓNG** — tập đúng là **37 · 21 · 2 = 60**, rời nhau và phủ kín; `E0-18` kiểm điều đó mỗi lần chạy |
| `CR-PC02-22` | Bốn schema chưa phê chuẩn (`worker-assignment`, `ingest-receipt`, `analysis-result`, `saved-snapshot`) nằm cạnh ba schema đã phê chuẩn trong cùng thư mục; ranh giới không nằm trong cấu trúc thư mục | W2 | **OPEN** → vòng Owner kế tiếp. Đã **giảm nhẹ** ở FIX8: ranh giới nay là allowlist tường minh trong `precode/gates.yaml`, không còn là danh sách viết cứng trong công cụ |

`CR-PC01-13` và `CR-PC02-22` cùng chỉ về một chỗ yếu: **phạm vi phê chuẩn không nằm trong cây hợp
đồng.** Ở FIX8 nó ít nhất đã rời khỏi mã nguồn: allowlist nay là dữ liệu trong `precode/gates.yaml`
trích `OD-20260907-01`, mặc định là **không đủ điều kiện**, và `E0-12`/`E0-12b` **`BLOCKED`** nếu
không đọc được nó — chứ không báo một PASS sạch trên một luật không thi hành được. Nhưng một file
mới vẫn cần người thêm tay vào allowlist, nên cả hai vẫn nên lên vòng Owner kế tiếp cùng nhau.

Một CR bị **mở lại**: **`CR-PC04-11`** — `event_order` của SC52 nay trích hai operation
authoritative `embedding.start_generation_rebuild` và `embedding.activate_generation` (§3.3).

Không CR nào ở trên được PC09 tự đóng; trạng thái đúng là `FIX_PROPOSED` hoặc `OPEN` cho tới khi
A2 xác minh.

### 8.2 Sổ change request đầy đủ — sinh bằng quét cơ học

Bản trước viết "70 CR đã được phát ra bởi PC00–PC08" và gộp theo trạng thái, bỏ sót **15** id —
trong đó `CR-PC01-09` nằm **bên trong một hợp đồng đã đóng băng** với dòng chữ "xin Coordinator
phê chuẩn" (`F-A2R1-04`). Một CR xin phê chuẩn mà không nằm trong sổ nào là một quyết định có thể
được ship như đã chốt mà không ai chốt nó.

Bảng dưới **được sinh** bởi `crtable.py`: quét mọi file `.md`/`.yaml`/`.json`/`.csv` trong repo tìm
`CR-PC\d\d-\d\d`, rồi gán trạng thái theo một quy tắc duy nhất, áp đồng đều:

- **RULED → FIX_PROPOSED** — id xuất hiện trong một file ruling của Coordinator: bản sửa đã được
  lệnh, và nó là `FIX_PROPOSED` cho tới khi một auditor độc lập xác minh.
- **CLOSED_CLAIMED** — một dòng trong handoff vừa chứa id vừa nói đã đóng. Đây là **lời khai** của
  gói phát ra hoặc gói nhận, **không** phải một closure đã xác minh.
- **OWNER** — id xuất hiện trong `precode/owner-decision-request.md`.
- **OPEN** — mọi trường hợp còn lại.
- Hai id mang disposition tường minh của Coordinator và được ghi bằng chính disposition đó.

**Tổng: 115 CR** (artefact `cr_summary-…` của `EV-PC09-01`) — 95 từ PC00–PC08, 13 từ PC09,
7 từ PC10. Phân bố trạng thái: ACCEPTED_AS_LIMITATION 1 · APPROVED 1 · CLOSED_CLAIMED 22 · OPEN 68 · RULED 23.

Hai disposition của Coordinator, ghi rõ vì chúng là quyết định chứ không phải quan sát:

- **`CR-PC01-09` — APPROVED.** `UNAUTHORIZED_COMMAND` và `RESTORE_UNVERIFIED` (mã của SRC-PLAN §10)
  là mã hợp lệ cho denied case nằm **ngoài** bảng bốn dòng R5-01, khi đặc tả gọi tên chúng. Chữ
  "đang chờ phê chuẩn" trong `modules.yaml` và `boundary/README.md` phải đổi thành "đã duyệt
  (Coordinator, A2-R1)" — việc của W2.
- **`CR-PC02-18` — ACCEPTED_AS_LIMITATION.** Cửa kiểm cột R4-01 áp cho fixture dạng `rows[]`. Các
  fixture văn xuôi gốc giữ nguyên và được **khai** là `NOT_APPLICABLE_FREEFORM`, với danh sách
  từng thư mục ở §13. Điều này cũng giải `F-A2R1-08`.

| CR | Trạng thái | Ghi chú | Xuất hiện ở |
| --- | --- | --- | --- |
| `CR-PC00-01` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/A2-R1-report.md`, `evidence/handoffs/PC00-handoff.md`, `precode/change-control.md` (+2 file) |
| `CR-PC00-02` | OPEN |  | `evidence/audits/A1-R1-report.md`, `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-03` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-04` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-05` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-06` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-07` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-08` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-09` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-10` | OPEN |  | `evidence/coordination/00-coordination-baseline.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md` (+2 file) |
| `CR-PC00-11` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-12` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/baseline.json` (+2 file) |
| `CR-PC00-13` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/review.md` |
| `CR-PC00-14` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `precode/baseline.json` (+1 file) |
| `CR-PC00-15` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/review.md` |
| `CR-PC00-16` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/adr/ADR-0006-stack-option-a.md`, `precode/adr/README.md` |
| `CR-PC00-17` | OPEN |  | `evidence/handoffs/PC00-handoff.md` |
| `CR-PC00-18` | OPEN |  | `evidence/handoffs/PC00-handoff.md` |
| `CR-PC01-01` | OPEN |  | `contracts/errors.yaml`, `contracts/modules.yaml`, `contracts/ports.yaml` (+5 file) |
| `CR-PC01-02` | OPEN |  | `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json`, `agent-tasks/TC-scheduler-lease-claim.md` (+11 file) |
| `CR-PC01-03` | OPEN |  | `contracts/errors.yaml`, `contracts/ports.yaml`, `evidence/audits/A1-R1-report.md` (+3 file) |
| `CR-PC01-05` | OPEN |  | `acceptance/scenarios.yaml`, `contracts/data/entities.yaml`, `contracts/http/openapi.yaml` (+9 file) |
| `CR-PC01-06` | OPEN |  | `contracts/modules.yaml`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC01-07` | OPEN |  | `contracts/ports.yaml`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+1 file) |
| `CR-PC01-08` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/ops/secrets.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+2 file) |
| `CR-PC01-09` | **APPROVED** (Coordinator, A2-R1) | UNAUTHORIZED_COMMAND và RESTORE_UNVERIFIED là mã hợp lệ cho denied case nằm ngoài bảng bốn dòng R5-01 khi đặc tả gọi tên chúng | `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `contracts/modules.yaml` (+8 file) |
| `CR-PC01-10` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `contracts/modules.yaml` (+3 file) |
| `CR-PC01-11` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+4 file) |
| `CR-PC01-12` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC01-handoff.md` (+2 file) |
| `CR-PC01-13` | OPEN |  | `evidence/handoffs/PC01-handoff.md`, `precode/review.md` |
| `CR-PC02-01` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-02` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-03` | OPEN |  | `contracts/data/entities.yaml`, `contracts/data/invariants.md`, `contracts/schemas/saved-snapshot.schema.json` (+3 file) |
| `CR-PC02-04` | OPEN |  | `contracts/data/entities.yaml`, `contracts/http/openapi.yaml`, `contracts/schemas/ingest-batch.schema.json` (+2 file) |
| `CR-PC02-05` | OPEN |  | `agent-tasks/TC-canonical-identity-merge.md`, `contracts/data/entities.yaml`, `contracts/errors.yaml` (+3 file) |
| `CR-PC02-06` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `agent-tasks/TC-canonical-identity-merge.md`, `agent-tasks/TC-report-coverage-publish-cas.md` (+13 file) |
| `CR-PC02-07` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/invariants.md`, `contracts/ops/backup-restore.md`, `evidence/audits/A2-R1-report.md` (+4 file) |
| `CR-PC02-08` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/identity/README.md`, `evidence/audits/A1-R1-report.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-09` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/A1-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-10` | OPEN |  | `evidence/audits/A1-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-11` | OPEN |  | `evidence/audits/A1-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-12` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-ingest-idempotent-ack-lost.md`, `contracts/data/entities.yaml`, `contracts/state/run.yaml` (+8 file) |
| `CR-PC02-13` | OPEN |  | `acceptance/fixtures/identity/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-14` | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-15` | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-16` | OPEN |  | `contracts/data/entities.yaml`, `contracts/modules.yaml`, `evidence/coordination/coordinator-ledger.md` (+3 file) |
| `CR-PC02-17` | OPEN |  | `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `contracts/data/entities.yaml`, `contracts/telegram/commands.yaml` (+4 file) |
| `CR-PC02-18` | **ACCEPTED_AS_LIMITATION** (Coordinator, A2-R1) | cửa kiểm cột R4-01 áp cho fixture dạng `rows[]`; các fixture văn xuôi giữ nguyên và được khai là NOT_APPLICABLE_FREEFORM | `evidence/audits/A2-R1-report.md`, `evidence/audits/A2-R2-report.md`, `evidence/audits/A2-R3-report.md` (+7 file) |
| `CR-PC02-19` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-20` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-21` | OPEN |  | `contracts/data/entities.yaml`, `precode/review.md` |
| `CR-PC02-22` | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `evidence/handoffs/PC10-handoff.md` (+2 file) |
| `CR-PC03-01` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/ports.yaml`, `evidence/coordination/FIX3-rulings.md`, `evidence/coordination/coordinator-ledger.md` (+6 file) |
| `CR-PC03-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-scheduler-lease-claim.md`, `contracts/errors.yaml`, `contracts/ports.yaml` (+11 file) |
| `CR-PC03-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/state/run.yaml`, `evidence/coordination/FIX3-rulings.md` (+3 file) |
| `CR-PC03-04` | OPEN |  | `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `agent-tasks/WALKTHROUGH.md`, `contracts/errors.yaml` (+8 file) |
| `CR-PC03-05` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/ai/tasks.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml` (+9 file) |
| `CR-PC03-06` | OPEN |  | `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/d-empty-period-coverage-only.json`, `contracts/reporting/time-and-tags.md` (+7 file) |
| `CR-PC03-07` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/state/delivery.yaml`, `evidence/coordination/FIX3-rulings.md` (+4 file) |
| `CR-PC04-01` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `evidence/coordination/FIX3-rulings.md` (+4 file) |
| `CR-PC04-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-backfill-pending-ledger.md`, `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md` (+6 file) |
| `CR-PC04-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `evidence/coordination/FIX3-rulings.md` (+3 file) |
| `CR-PC04-04` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json`, `agent-tasks/TC-report-coverage-publish-cas.md`, `contracts/ports.yaml` (+8 file) |
| `CR-PC04-05` | OPEN |  | `agent-tasks/TC-ui-reports-detail.md`, `contracts/ai/grounding.md`, `contracts/ai/tasks.yaml` (+5 file) |
| `CR-PC04-06` | OPEN |  | `acceptance/fixtures/reporting/README.md`, `acceptance/scenarios.yaml`, `contracts/reporting/time-and-tags.md` (+3 file) |
| `CR-PC04-07` | OPEN |  | `agent-tasks/TC-backfill-pending-ledger.md`, `contracts/reporting/time-and-tags.md`, `contracts/ui/screens.yaml` (+3 file) |
| `CR-PC04-08` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-report-coverage-publish-cas.md`, `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md` (+8 file) |
| `CR-PC04-09` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `contracts/state/report.yaml` (+5 file) |
| `CR-PC04-10` | OPEN |  | `contracts/reporting/time-and-tags.md`, `evidence/audits/A2-R1-report.md`, `evidence/handoffs/PC04-handoff.md` (+1 file) |
| `CR-PC04-11` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json`, `acceptance/scenarios.yaml`, `evidence/audits/A2-R1-report.md` (+4 file) |
| `CR-PC05-01` | OPEN |  | `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/a-feed-layout-changed.json`, `agent-tasks/TC-collector-checkpoint-resume.md` (+11 file) |
| `CR-PC05-02` | OPEN |  | `contracts/http/openapi.yaml`, `evidence/handoffs/PC05-handoff.md`, `precode/review.md` |
| `CR-PC05-03` | OPEN |  | `agent-tasks/TC-x-feasibility-probe.md`, `contracts/ops/collector-probe.md`, `evidence/audits/A2-R2-report.md` (+10 file) |
| `CR-PC05-04` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC05-handoff.md` (+1 file) |
| `CR-PC05-05` | OPEN |  | `contracts/ports.yaml`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+2 file) |
| `CR-PC06-01` | OPEN |  | `agent-tasks/TC-analysis-once-per-generation.md`, `contracts/retry-policy.yaml`, `contracts/state/analysis.yaml` (+5 file) |
| `CR-PC06-02` | OPEN |  | `agent-tasks/TC-analysis-once-per-generation.md`, `contracts/data/entities.yaml`, `evidence/coordination/coordinator-ledger.md` (+4 file) |
| `CR-PC06-03` | OPEN |  | `agent-tasks/TC-analysis-adapter-validation.md`, `contracts/capabilities.yaml`, `evidence/coordination/coordinator-ledger.md` (+3 file) |
| `CR-PC06-04` | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-analysis-adapter-validation.md`, `evidence/handoffs/PC04-handoff.md` (+4 file) |
| `CR-PC06-05` | OPEN |  | `agent-tasks/TC-ui-reports-detail.md`, `evidence/handoffs/PC06-handoff.md`, `precode/review.md` |
| `CR-PC07-01` | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-telegram-linking-auth.md`, `contracts/telegram/commands.yaml` (+4 file) |
| `CR-PC07-02` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `contracts/data/entities.yaml` (+6 file) |
| `CR-PC07-03` | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-telegram-linking-auth.md`, `evidence/handoffs/PC07-handoff.md` (+1 file) |
| `CR-PC07-04` | OPEN |  | `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json`, `acceptance/scenarios.yaml` (+25 file) |
| `CR-PC07-05` | OPEN |  | `agent-tasks/TC-telegram-linking-auth.md`, `contracts/telegram/commands.yaml`, `evidence/handoffs/PC07-handoff.md` (+1 file) |
| `CR-PC07-06` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/telegram/README.md`, `acceptance/scenarios.yaml`, `evidence/audits/A1-R3-report.md` (+4 file) |
| `CR-PC07-07` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc51-first-time-setup.json`, `agent-tasks/TC-analysis-adapter-validation.md` (+8 file) |
| `CR-PC07-08` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC07-handoff.md`, `precode/review.md` |
| `CR-PC07-09` | OPEN |  | `evidence/handoffs/PC07-handoff.md`, `precode/review.md` |
| `CR-PC07-10` | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC07-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+2 file) |
| `CR-PC08-01` | OPEN |  | `acceptance/fixtures/recovery/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC00-handoff.md` (+3 file) |
| `CR-PC08-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-backup-restore-drill.md`, `agent-tasks/TC-owner-auth-session.md`, `contracts/capabilities.yaml` (+7 file) |
| `CR-PC08-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`, `acceptance/scenarios.yaml`, `contracts/capabilities.yaml` (+14 file) |
| `CR-PC08-04` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `acceptance/scenarios.yaml` (+13 file) |
| `CR-PC08-05` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `agent-tasks/TC-backup-restore-drill.md`, `contracts/data/entities.yaml` (+5 file) |
| `CR-PC09-01` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/coordination/coordinator-ledger.md` (+4 file) |
| `CR-PC09-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC09-handoff.md` (+2 file) |
| `CR-PC09-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/state/run.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC03-handoff.md` (+3 file) |
| `CR-PC09-04` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/state/analysis.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC03-handoff.md` (+3 file) |
| `CR-PC09-05` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC09-handoff.md` (+1 file) |
| `CR-PC09-06` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX5-rulings.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md` (+1 file) |
| `CR-PC09-07` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/handoffs/PC10-handoff.md` (+2 file) |
| `CR-PC09-08` | OPEN |  | `evidence/audits/A2-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md` (+1 file) |
| `CR-PC09-09` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/gates.yaml`, `precode/review.md` |
| `CR-PC09-10` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-11` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-12` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC09-handoff.md`, `precode/gates.yaml`, `precode/review.md` |
| `CR-PC09-13` | OPEN |  | `precode/review.md` |
| `CR-PC10-01` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-analysis-adapter-validation.md`, `agent-tasks/TC-analysis-once-per-generation.md`, `agent-tasks/TC-backfill-pending-ledger.md` (+22 file) |
| `CR-PC10-02` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-collector-checkpoint-resume.md`, `agent-tasks/WALKTHROUGH.md`, `contracts/errors.yaml` (+11 file) |
| `CR-PC10-03` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/WALKTHROUGH.md`, `contracts/capabilities.yaml`, `evidence/coordination/coordinator-ledger.md` (+3 file) |
| `CR-PC10-04` | OPEN |  | `agent-tasks/WALKTHROUGH.md`, `evidence/handoffs/PC10-handoff.md`, `precode/change-control.md` (+1 file) |
| `CR-PC10-05` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC10-handoff.md`, `precode/review.md` |
| `CR-PC10-06` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC10-handoff.md` |
| `CR-PC10-07` | OPEN |  | `evidence/handoffs/PC10-handoff.md`, `precode/review.md` |

---

## 9. Readiness theo module — đánh giá lại sau phê chuẩn

Tiêu chí `READY_FOR_CARD` giữ nguyên: (a) module có owner, port vào/ra và cạnh bị cấm đã khai;
(b) mọi operation nó sở hữu có schema, auth, transaction, idempotency, lỗi và scenario; (c) không
blocker nào còn mở **chạm trực tiếp** vào hành vi của nó; (d) không finding audit nào đang mở
trong file của nó; (e) mọi tham số bắt buộc có giá trị (không `PLACEHOLDER_KC`); (f) scenario của
nó có fixture.

`OD-20260907-01` thay đổi bảng này nhiều hơn bất kỳ đợt nào trước, vì điều kiện **(c)** trước đây
sai với *mọi* module chỉ vì B01–B17 đều `OPEN`. Nay chúng `RATIFIED`, nên (c) chỉ còn sai ở những
module bị chặn bởi một `KC` hoặc một quyết định Owner **hoãn** lại. Điều kiện (d) vẫn phụ thuộc
§4.1 và không dòng nào dưới đây được đọc là closure.

| Module | Chạy ở | Trạng thái | Chặn bởi (sau phê chuẩn) |
| --- | --- | --- | --- |
| `MOD-web-ui` | browser | READY_FOR_CARD *(có điều kiện)* | B10 ratified (mục 13). Còn: §3/§8 của card phải viết lại theo stack B |
| `MOD-backend-api` | server | READY_FOR_CARD *(có điều kiện)* | Không còn blocker. 54 operation HTTP có wire contract 1:1, `ErrorEnvelope` set-equal `errors.yaml` |
| `MOD-auth-service` | server | READY_FOR_CARD *(có điều kiện)* | Tham số phiên được Owner chấp nhận (mục 23) |
| `MOD-settings-service` | server | **BLOCKED** | B08 ratified, nhưng **`REQ-OQ03` Owner hoãn** (mục 21) — provider/model cụ thể vẫn `OWNER_DECISION_REQUIRED`. Chặn M3 |
| `MOD-tag-service` | server | READY_FOR_CARD *(có điều kiện)* | B01/B04 ratified; `REQ-OQ04` N = 7 ngày được chấp nhận (mục 20) |
| `MOD-scheduler` | server | READY_FOR_CARD *(có điều kiện)* | B08 ratified với `Asia/Ho_Chi_Minh`; `REQ-OQ06` 08:00/20:00 chấp nhận. Múi giờ không DST ⇒ DST-01/DST-02 chưa kích hoạt |
| `MOD-job-service` | server | READY_FOR_CARD *(có điều kiện)* | B02/B10 ratified |
| `MOD-ingest-service` | server | READY_FOR_CARD *(có điều kiện)* | B05 ratified (câu chữ AC-04) |
| `MOD-identity-service` | server | READY_FOR_CARD *(có điều kiện)* | B06/B15 ratified |
| `MOD-research-connector` | server | **BLOCKED (cứng)** | `REQ-A6` `KC`: bốn giá trị rate-limit vẫn `null`/`PLACEHOLDER_KC`. Phê chuẩn không đọc hộ tài liệu arXiv/OpenAlex |
| `MOD-embedding-service` | server | **BLOCKED (cứng)** | `REQ-A3` `KC` và `REQ-OQ09`; mục 20 nói rõ **model chưa đặt cho tới khi đo được** |
| `MOD-analysis-service` | server | READY_FOR_CARD *(có điều kiện)* | B07 ratified. Còn `PROV-PC03-04` (tự chạy lại một lần từ `unknown_attempt`) — **không** nằm trong 25 mục, vẫn `PROVISIONAL` |
| `MOD-report-service` | server | **BLOCKED** | B01/B04/B14/B17 ratified, nhưng bảy tham số mật độ có cổng `REQ-A4` (`KC`, 0/3–4 kỳ) và `REQ-D53` vẫn `ĐX` ở phần hiệu chỉnh |
| `MOD-saved-service` | server | READY_FOR_CARD *(có điều kiện)* | `F-PC00-02` (hoãn export sang P1) được Owner xác nhận (mục 20) |
| `MOD-delivery-service` | server | READY_FOR_CARD *(có điều kiện)* | B03 ratified (câu chữ AC-14) |
| `MOD-telegram-adapter` | server | **BLOCKED (cứng)** | `CR-PC07-04`: giới hạn định dạng Telegram vẫn `KC`. B03/B09/B10 đã hết chặn |
| `MOD-secret-service` | server | **BLOCKED (cứng)** | B13 ratified nhưng `REQ-A5` `KC` — điều khoản từng nhà AI chưa đọc |
| `MOD-data-admin-service` | server | READY_FOR_CARD *(có điều kiện)* | **Gỡ chặn cứng.** Mục 24 chốt phạm vi `data.purge_all`: chỉ dữ liệu nghiên cứu, giữ đăng nhập/secret/liên kết Telegram/cấu hình provider/lịch, **backup không bị xóa**. Còn `CR-PC01-05` (cascade) mở |
| `MOD-data-store` | server | READY_FOR_CARD *(có điều kiện)* | Partial UNIQUE index và STORED generated column vẫn là **giả định chưa kiểm trên SQLite thật** — E1 sau khi có repo stack B |
| `MOD-backup-service` | server | READY_FOR_CARD *(có điều kiện)* | B11 ratified, RPO 24 h / RTO 2 h chấp nhận (mục 23). **Chưa drill nào chạy** — đó là E1+, không phải điều kiện card |
| `MOD-backup-cli` | server | READY_FOR_CARD *(có điều kiện)* | như trên; `PROV-PC01-04` vẫn `PROVISIONAL` |
| `MOD-health-service` | server | READY_FOR_CARD *(có điều kiện)* | Ngưỡng readiness 30/90/900/1800 s vẫn PROVISIONAL, chưa đo thật |
| `MOD-x-collector` | máy cá nhân | **BLOCKED (cứng)** | `REQ-OQ01` **đã được trả lời** (mục 1) — D09 không còn chặn. Còn lại: `REQ-A1` và `REQ-A7` `KC`, SP1 `NOT_RUN` |
| `MOD-analysis-worker` | máy cá nhân | **BLOCKED (cứng)** | B13 ratified; `REQ-A5` `KC`; mọi adapter `enabled=false` |
| `MOD-ai-adapter` | máy cá nhân | **BLOCKED (cứng)** | Mục 15 phê chuẩn chính sách **và giữ nguyên `AC-16 BLOCKED`** cho tới khi một probe đạt. Chưa probe nào chạy |

**Tổng, đếm từ chính bảng trên (25 dòng): 16 module `READY_FOR_CARD` có điều kiện, 9 `BLOCKED`,
trong đó 7 bị chặn cứng** (`module_table_rows`, `module_ready`, `module_blocked`,
`module_hard_blocked` — parse cơ học từ bảng, không viết cạnh bảng).

Thay đổi so với bản trước: **9 ready → 16**. Bảy module lên ready vì blocker của chúng được phê
chuẩn (`tag`, `scheduler`, `job`, `delivery`, `backup-service`, `backup-cli`, và
**`data-admin-service`** — module duy nhất trước đây chặn cứng vì một câu hỏi phạm vi, nay có câu
trả lời). Một module đi ngược: **`MOD-settings-service` và `MOD-embedding-service` chuyển từ
BLOCKED thường sang lý do rõ ràng hơn** — OQ03 bị hoãn, model embedding chờ đo.

Điều đáng đọc kỹ nhất: **cả 7 module chặn cứng đều chặn vì một `KC` hoặc một phép đo chưa chạy**
(`REQ-A6`, `REQ-A3`+`REQ-OQ09`, `CR-PC07-04`, `REQ-A5`×2, `REQ-A1`/`REQ-A7`). Không còn module nào
chặn vì thiếu quyết định — trừ `MOD-settings-service`, chặn vì Owner **chọn hoãn**. Không lượng
công việc soạn thảo nào gỡ được nhóm còn lại; chúng cần mạng, tài khoản thật, và thời gian chạy.

### 9.1 Task card — độ phủ, đo thật

PC10 đã re-pin nhiều lần. Epoch **hiện tại** không được chép tay ở đây mà đọc từ chính các card:

```
sed -n 's/^\*\*Pin epoch: `\([A-Za-z0-9-]*\)`.*/\1/p' agent-tasks/TC-*.md | sort -u
```

Lệnh này là **chính quy tắc bộ sinh áp dụng** (khóa `card_pin_command`), và nó trả **đúng một**
giá trị. Lệnh cũ (`grep -ho "PC10-PIN-[A-Za-z0-9-]*"`) trả **bảy** tên, vì mỗi dòng pin của card
nêu cả epoch hiện hành lẫn mọi epoch đã bị thay — đọc nó không cho biết cái nào là hiện hành
(`F-A2R3-02`). Quy tắc đúng: epoch hiện hành là token trong cặp backtick **đầu tiên** của dòng bắt
đầu bằng `**Pin epoch: `.

Tại thời điểm chạy bản này lệnh đó trả **`PC10-PIN-OD01c-20260907`**, và **18/18 card khai cùng
một epoch** (`card_pin_current`, `card_pin_declared`, `card_pin_unanimous`). Chuỗi epoch từ đầu
gói: `FCW4` → `FCW4b` → `FCW4c` → `FCW4d` → `FCW4e` → `FCW4f` → `OD01` → `OD01c`; hai lần re-pin
cuối là do phê chuẩn (chuyển toàn bộ card sang stack B) và do đợt sửa `F-A2R5-01`. `F-A2R1-03` bắt đúng điểm này, và
lý do nó lệch được là vì nó được chép chứ không được đọc. Card trích các file của PC09 **theo
đường dẫn và SC id, không theo hash** (ruling R5-07) — cách pin đúng, vì `acceptance/scenarios.yaml`
đổi ở chính đợt này và một hash được pin sẽ lệch ngay.

**Đủ điều kiện phạm vi phê chuẩn — số tôi *đo được* sau khi `PKT-PC10-FIX9` land.** Đếm trên đĩa:
**8/18 card khai "Phạm vi đã phê chuẩn", 10/18 khai "Ngoài phạm vi đã phê chuẩn" với điểm dừng
`KC` giữ nguyên**. Mười card kia bị chặn bởi cùng một nhóm file: `contracts/ai/`,
`contracts/telegram/`, `contracts/ui/screens.yaml`, `contracts/http/openapi.yaml`, ba file
`contracts/ops/` mang `KC`, và bốn schema chưa phê chuẩn.

**Cần đọc kỹ con số 8 này.** W7 báo cáo rằng tiêu chí **nguyên văn** — *mọi* file trong read set
mang `claim_ceiling: CONTRACT_READY` — cho ra **0**, không phải 8: trong 143 file có pin chỉ 21
file đạt, mọi fixture và mọi ADR vẫn `DRAFT_FOR_REVIEW`, và `openapi.yaml` (nằm trong read set của
15/18 card) cũng vậy. Con số 8 đến từ một tiêu chí **thay thế** — *read set không chạm
`contracts/ai/`, `contracts/telegram/`, hay file `contracts/ops/` nào ngoài `deployment.md`* — do
W7 hiện thực để khớp danh sách Coordinator nêu đích danh, và W7 đã ghi rõ sự khác biệt thay vì im
lặng chọn một trong hai. Tôi lặp lại điều đó ở đây vì §9.1 là chỗ người đọc tra con số này:
**"8 card trong phạm vi phê chuẩn" không có nghĩa là nền hợp đồng của 8 card đó đã
`CONTRACT_READY`.** `CR-PC10-07` (→ Coordinator) nêu đúng bước còn thiếu để hai tiêu chí trùng
nhau. Mỗi card, cả 18, nay tự liệt kê đích danh những file trong read set của nó còn
`DRAFT_FOR_REVIEW` — nên lời khai của card không thể rộng hơn phép đo của chính nó.

**Một điều tôi tìm thấy khi đọc header card, và không im lặng bỏ qua.** 18 card khai
`claim_ceiling: IMPLEMENTATION_VERIFIED` (một card khai `LIVE_FEASIBILITY_VERIFIED`) — những nhãn
mà `E0-12` cấm tuyệt đối. Chúng **không** bị bắt, vì `agent-tasks/` **nằm ngoài `SCAN_DIRS`** của
`e0_check.py` (`contracts`, `acceptance`, `precode`, `evidence`). Đọc kỹ thì đây không phải một vi
phạm: trong một card, `claim_ceiling` nghĩa là *trần mà công việc được giao có thể đạt tới*, lấy
từ SRC-PLAN §2 — không phải một tuyên bố về chính card. Nhưng **một khóa mang hai nghĩa** là đúng
lớp rủi ro gói này đã gặp bốn lần. Tôi đã làm hai việc: sửa oracle của `E0-12` để nó nói đúng
phạm vi nó quét thay vì nói "everywhere", và cho `E0-12` **đếm và in ra** các nhãn vượt trần trong
`agent-tasks/` như một note — có mặt trong bản ghi chạy, không phải vắng mặt im lặng. Đây là
**`CR-PC09-14`** (→ Coordinator): hoặc đổi tên khóa trong card, hoặc mở rộng `SCAN_DIRS`.

PC10 **không chạy** kiểm tra "mỗi hạng mục P0 (`REQ-P0-01` … `REQ-P0-12`) có ít nhất một card".
Coordinator giao tôi chạy nó.
Kết quả, báo đúng như đo được — hai con số khác nhau và cả hai đều thật:

| Cách đo | Kết quả |
| --- | --- |
| **Trực tiếp:** card trích chính id của hạng mục P0 | **0 / 12.** Không card nào trích một id hạng mục P0; 18 card cùng nhau chỉ trích 7 id yêu cầu |
| **Bắc cầu:** card trích một `SC` mà `traceability.csv` ánh xạ về hạng mục P0 đó | **12 / 12** |

Đọc kết quả này thế nào: card **không** tham chiếu requirement trực tiếp — chúng tham chiếu
scenario, và scenario mang `requirement_refs`. Đó là một thiết kế hợp lệ và nhất quán với
SRC-PLAN §15 (card pin "scenario IDs, command sẽ chạy, oracle"). Nên "0/12" **không** phải một
khiếm khuyết; nó là hệ quả của việc chuỗi truy vết đi qua scenario.

Nhưng nó có một hệ quả thật cần nói: **chuỗi bắc cầu chỉ bền khi mọi hạng mục P0 có scenario.**
Khi tôi chạy kiểm tra này lần đầu, `REQ-P0-08` ("Save trong app và qua Telegram, snapshot lúc
lưu", XN/P0) có **0 card theo cả hai cách đo**, vì nó không được scenario nào trích — dù SC12 và
SC13 phủ đúng hành vi đó. Tôi đã thêm `REQ-P0-08` vào `requirement_refs` của SC12 và SC13 (chính
xác, không phải độn số), và con số bắc cầu trở thành 12/12.

Hai quan sát phụ, cùng một lần chạy:
- **53 / 56 scenario được ít nhất một card trích dẫn.** Ba scenario chưa card nào trích là
  **SC54, SC55, SC56** — chính ba scenario tôi thêm ở đợt FIX6 để cấp cực dương riêng cho I04, I14
  và I16. Chúng ra đời sau lần pin gần nhất của PC10, nên đây là độ trễ chứ không phải bỏ sót; tôi
  ghi nó ở đây thay vì làm tròn con số lên 56/56. Việc neo ba scenario này vào card thuộc PC10.
- Kiểm tra này **nên trở thành một check E0 thường trực** khi `agent-tasks/` ổn định. Tôi không
  thêm nó vào `e0_check.py` ở đợt này vì `agent-tasks/` nằm ngoài read set của packet PC09 gốc và
  PC10 vẫn đang thay đổi; đề nghị Coordinator giao nó cho lượt sau. Đây là `CR-PC09-08`.

---

## 10. Sau phê chuẩn: cái gì đã chốt, cái gì còn chờ Owner

`precode/owner-decision-request.md` nay mang banner `ANSWERED 2026-09-07` và phiếu trả lời đã
điền. `OD-20260907-01` giải **25 mục**. Bản này không nhân bản biên bản; nếu hai bản lệch nhau,
`precode/owner-decisions.md` thắng.

### 10.1 Đã chốt

| Nhóm | Mục | Hiệu lực |
| --- | --- | --- |
| 17 blocker | 1–2, 4–19 | B01–B17 → `RATIFIED`; 14 amendment → `ACCEPTED`; `ADR-0001..0005`, `0007..0010` → accepted |
| Stack | 3 | **Option B** — Python worker/server + TypeScript web. `ADR-0006` viết lại; **hợp đồng không đổi** |
| Chrome profile | 1 | `REQ-OQ01` đã trả lời; **D09 không còn chặn M0/SP1** |
| Timezone | 4 | `Asia/Ho_Chi_Minh` **được xác nhận** — fixture lịch của PC03/PC04 giữ nguyên |
| Bộ mặc định OQ | 20 | N = 7 ngày; 200 post / 30 phút; 08:00 và 20:00; không có giờ yên lặng; export Saved hoãn P1 |
| 8 tham số PC04 + kỳ rỗng | 22 | `PROV-PC04-01..09` → giá trị làm việc; **phương án (b)** cho kỳ rỗng được chấp nhận |
| Tham số PC08 | 23 | RPO 24 h, RTO 2 h, Argon2id, idle 12 h / tuyệt đối 30 ngày, token 180 ngày, audit 365 ngày |
| Phạm vi `data.purge_all` | 24 | **Chỉ dữ liệu nghiên cứu**; giữ đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch; **backup KHÔNG bị xóa** |
| Hai thay đổi kỹ thuật | 25 | `CSRF_REJECTED`; `run.resume` từ `blocked` với lý do bắt buộc |

Hai hệ quả tôi đã cảnh báo trước khi Owner trả lời mục 24 vẫn đúng và nay là **hành vi đã chốt**,
không còn là rủi ro: purge **không** động tới credential đăng nhập (nên Owner không tự khóa mình
ra ngoài), và dữ liệu đã purge **vẫn còn trong backup** cho tới khi các bản backup đó hết hạn
lưu — "xóa toàn bộ" vẫn không đồng nghĩa "không còn ở đâu nữa".

### 10.2 Còn chờ Owner — danh sách đầy đủ, ngắn hơn nhiều

| ID | Nội dung | Chặn |
| --- | --- | --- |
| `REQ-OQ03` | Provider và model AI cụ thể — Owner **chọn hoãn** (mục 21) | `MOD-settings-service`, **M3** |
| `PROV-PC03-04` | `analysis_unknown_attempt_auto_rerun = 1` — PC03 tự xin Auditor soi kỹ; **không** nằm trong 25 mục | `MOD-analysis-service` (không chặn card) |
| `PROV-PC01-01`, `-02`, `-04`, `-05`, `-06` | `CAPABILITY_DENIED`, unlink là app action, `MOD-backup-cli`, caller của `identity.record_alias`, `MOD-data-admin-service` | Không mục nào chặn card |
| Quyết định PC02 | 8 giới hạn ingest/snapshot, hai quy tắc chuẩn hóa DOI/arXiv, `analysis_key` không gồm provider/model | `CR-PC02-04`, `-05`, `-17` |
| Quyết định PC05 | Thiết kế URL 50 path, ánh xạ mã lỗi → HTTP status, `x-transport-limits`, ngưỡng go/no-go của probe | Ngưỡng GO-2 (challenge ≤ 1 mỗi 5 đợt) là ngưỡng **trải nghiệm**: cao hơn thì sản phẩm "tự chạy" thành sản phẩm "gọi người" |
| Quyết định PC06 | `confidence` enum rời rạc, `usage.unknown ⇒ ba trường null`, ngưỡng rubric G1/G2 = 1.00 | |
| Quyết định PC07 | `telegram_update_max_age` và các tham số còn lại | `CR-PC07-01`, `-05` |
| `CR-PC09-13` | `REQ-OQ01`/`REQ-OQ02` trong `requirements.csv` chưa cập nhật theo mục 1 và mục 3 (§6.1) | Độ chính xác của chính sổ yêu cầu |
| `CR-PC09-14` | Khóa `claim_ceiling` mang hai nghĩa; `agent-tasks/` ngoài `SCAN_DIRS` của E0 (§9.1) | Độ phủ của chính cửa kiểm claim |
| `CR-PC01-13`, `CR-PC02-22`, `CR-PC10-07` | Ranh giới phạm vi phê chuẩn hiện chỉ tồn tại trong danh sách đường dẫn của `E0-12`, không trong cây hợp đồng (§8.1) | Nên đưa lên **vòng Owner kế tiếp** |

**Điều thay đổi về chất:** trước phê chuẩn, danh sách này chứa những mục mà **không Worker nào**
gỡ được và **mọi** module đều dính. Nay chỉ còn **một** mục chặn một mốc — `REQ-OQ03` chặn M3 — và
phần còn lại là tham số cấp gói mà một vòng Owner ngắn sẽ đóng. Cái chặn dự án hôm nay không còn
là quyết định; là **phép đo** (§6.2) và **code chưa tồn tại**.

---

## 11. Definition of Ready của SRC-PLAN §17 — đối chiếu từng dòng

| # | Điều kiện | Đạt? | Bằng chứng / thiếu gì |
| --- | --- | --- | --- |
| 1 | Spec snapshot/hash và registry nguyên tử tồn tại | ✅ | `precode/source/*` byte-identical; 246 dòng registry |
| 2 | Tất cả XN/UQ/P0 có mapping; ĐX/KC còn lại có trạng thái và gate rõ | ✅ | `acceptance/traceability.csv`, 0 ORPHAN; §6 bảng KC |
| 3 | B01–B17 được giải hoặc explicit scoped block | ✅ | **Cả 17 `RATIFIED` bởi `OD-20260907-01`**; `agent_profile/registry.json` có `open_product_blockers: []`; 14 amendment `ACCEPTED`. Đây là dòng đổi lớn nhất của bản này |
| 4 | Mỗi module có ownership, port và denied edges; negative cases đủ | ✅ | **36 / 36 cạnh** có denied case với mã lỗi đã pin (ruling R5-01) và một fixture 36 sự kiện |
| 5 | Mỗi operation có schema, auth, transaction, idempotency, concurrency, error và evidence | ✅ | 85 operation; **0 thiếu `scenario_refs`, 0 thiếu `error_codes`, 0 mutation thiếu khai báo idempotency** (`dor5`, sinh từ `ports.yaml` cùng lượt với các số khác); 54 operation HTTP có wire contract. Năm ngoại lệ mà `F-A2R1-09` nêu tên đã được **đóng** ở FIX6/FIX7: `auth.logout` và `auth.get_session` → SC40/SC51, `save.export` → SC12, `research.get_connector_health` và `health.get_liveness` → `INTERNAL` |
| 6 | Mỗi mã lỗi có trạng thái đích, điều kiện phục hồi và hành vi bị cấm | ✅ | 28 mã, mỗi mã đủ 10 trường; 28/28 có scenario |
| 7 | Coverage/backfill/pending/tag version và identity/analysis/Saved có oracle cho race/crash | ✅ | SC08, SC13, SC21, SC22, SC28, SC37, SC38 |
| 8 | Telegram unknown, CLI capability, backup WAL/restore và secrets không còn mô tả mơ hồ | ⚠️ | Ba trong bốn đủ. **Giới hạn định dạng Telegram vẫn `KC`** (CR-PC07-04) |
| 9 | AC-01–AC-18 và các SC bổ sung có fixtures/oracles, loại bằng chứng và amended AC đúng nguồn | ✅ | 56 scenario, mỗi cái có oracle, cấp bằng chứng và **ít nhất một fixture**; 86 fixture trên 9 thư mục (`scenarios`, `fixtures`, `fixture_directories`) |
| 10 | E0 đã chạy thật và có manifest; E1–E4 chưa chạy ghi NOT_RUN | ✅ | `evidence/index.json`; **24/24 PASS, 0 vi phạm, exit 0**; E1–E4 `NOT_RUN` với 32 placeholder tường minh |
| 11 | Card triển khai pin baseline, paths/stack, contracts và proof obligations | ⚠️ | **Stack đã chốt (Option B, mục 3)** và 18 card đều pin cùng một epoch — **tên epoch được in ở §9.1 và chỉ ở đó** (`F-A2R3-01`: dòng này từng nhắc lại nó và đã sai ba epoch liên tiếp). Còn thiếu: **chưa có repo triển khai**, nên §3 (đường dẫn) và §8 (lệnh) của card vẫn tự khai `PROVISIONAL`, và framework chưa được `ADR-0006` nêu tên |
| 12 | Readiness report liệt kê module nào READY/BLOCKED | ✅ | §9 |

**Đếm từ chính bảng trên: 10 ✅, 2 ⚠️, 0 ❌** trên 12 dòng (`dor`, parse cơ học).

**Không còn dòng ❌ nào** — lần đầu tiên kể từ khi gói này bắt đầu. Cả hai dòng ❌ cũ đều do phê
chuẩn đóng: #3 (B01–B17) hoàn toàn, #11 (stack) một nửa.

Hai dòng ⚠️ còn lại nói đúng cùng một điều bằng hai cách: **cái thiếu không phải là quyết định
nữa.** #8 cần đọc tài liệu Bot API — cần mạng. #11 cần một repo triển khai tồn tại — cần code.
Không dòng nào gỡ được bằng soạn thảo thêm, và tôi cố ý **không** nâng #11 lên ✅: card mô tả
đường dẫn *sẽ* tồn tại, và một DoR nói "paths đã pin" trong khi paths tự khai `PROVISIONAL` là
đúng loại phát biểu mà mọi finding của audit trong gói này đã bắt.

Con số này đi 7/3/2 → 10/0/2 (sai) → 8/2/2 → 9/1/2 → **10/2/0**, và mỗi lần nó đổi là vì một dòng
của bảng đổi. Cổng tự kiểm so dòng tổng với bảng chạy sau **mỗi** lần sửa; nó bắt được đúng lần
lệch khi tôi sửa dòng #5 mà quên dòng tổng.

---

## 12. Tuyên bố — theo phạm vi, không còn một giá trị chung

**Claim của chính bản review này: `DRAFT_FOR_REVIEW`.** Nó là `SELF_VALIDATION` của người đã viết
một phần corpus mà nó đánh giá; không lượng phê chuẩn nào đổi được điều đó.

Trần claim của **hợp đồng** thì nay là một object theo phạm vi (`precode/baseline.json`
`claim_ceiling.by_scope`), theo `OD-20260907-01` §4. Bốn phạm vi được W1 đặt là
**`CONTRACT_READY_PENDING_E0`** — nghĩa là đủ điều kiện *về quyết định*, còn chờ một lần chạy E0
sạch trên epoch mới. **Lần chạy đóng gói của tôi ở đợt này chính là điều kiện đó**, và nó cho
**24/24 PASS, 0 vi phạm**. Giá trị `CONTRACT_READY_PENDING_E0` → `CONTRACT_READY` là việc của W1:
`precode/baseline.json` không nằm trong grant ghi của PC09, nên **tôi không sửa nó** — tôi báo
rằng điều kiện đã đạt và để W1 chốt (CR tới W1 nếu giá trị cần đổi khác đi).

### 12.1 Bốn phạm vi `CONTRACT_READY`

**21 file** khai `claim_ceiling: CONTRACT_READY` với `ratification_ref: OD-20260907-01`
(`contract_ready_count`), và `E0-12b` xác nhận cả 21 tham chiếu đó **phân giải được** tới một
`precode/owner-decisions.md` có thật.

| Phạm vi | File | Vì sao đủ điều kiện |
| --- | --- | --- |
| **Ranh giới và quyền** | `modules.yaml`, `capabilities.yaml`, `ports.yaml`, `errors.yaml`, `retry-policy.yaml`, `ops/deployment.md` | B12/B13 ratified; `REQ-OQ01` đã trả lời; 36/36 cạnh bị cấm có mã lỗi đã pin; 85 operation đủ trường |
| **Dữ liệu và định danh** | `data/entities.yaml`, `data/identity.md`, `data/invariants.md`, `schemas/target`, `schemas/ingest-batch`, `fixtures/identity/README.md` | B05/B06/B15 ratified; SC07/SC23/SC29/SC30 có fixture và oracle |
| **Workflow và trạng thái** | `state/run.yaml`, `state/analysis.yaml`, `state/delivery.yaml`, `state/report.yaml`, `state/storage.yaml` | B01/B02/B03/B07/B10 ratified; 13/13 dòng ánh xạ trạng thái được A1 xác minh verbatim; `E0-09` PASS |
| **Báo cáo và thời gian** | `reporting/time-and-tags.md`, `reporting/selection.md`, `schemas/report`, `fixtures/reporting/README.md` | B01/B04/B14/B17 ratified; timezone đã xác nhận nên fixture lịch giữ nguyên; 8 tham số PC04 được chấp nhận |

**Điều `CONTRACT_READY` ở đây KHÔNG có nghĩa là.** Nó không nói tham số đã được hiệu chỉnh:
ngưỡng `0.8000` vẫn `PROVISIONAL_BOOTSTRAP` với `threshold_calibration_state='uncalibrated'`, và
bảy tham số mật độ vẫn chờ `REQ-A4`. Hợp đồng đóng **không** đòi tham số đã hiệu chỉnh; cái bị cấm
là tuyên bố **đạt chỉ tiêu §1.4** khi còn `uncalibrated`. Nó cũng không nói code sẽ đúng — nó nói
bốn phạm vi này đã đủ chặt để bắt đầu viết code trong đúng phạm vi đó, khi Owner ra lệnh.

### 12.2 Bốn phạm vi giữ `DRAFT_FOR_REVIEW` — và lý do của từng phạm vi

**110 file** vẫn `DRAFT_FOR_REVIEW` (`draft_for_review_count`). Lý do **không** phải là thiếu
quyết định nữa:

| Phạm vi | File chính | Điều còn thiếu — và nó là loại gì |
| --- | --- | --- |
| **Collector và nguồn** | `openapi.yaml`, `ops/collector-probe.md`, `schemas/worker-assignment`, `schemas/ingest-receipt` | Bốn giá trị `research_connector_rate_limit` vẫn `null`/`PLACEHOLDER_KC` (`REQ-A6`) — **cần đọc tài liệu arXiv/OpenAlex, cần mạng**. Cộng: chưa có validator OpenAPI 3.1 nào chạy trên 221 KB `openapi.yaml` |
| **AI và grounding** | `ai/tasks.yaml`, `ai/providers.yaml`, `ai/grounding.md`, `ops/cli-acp-probe.md`, `ops/secrets.md`, `schemas/analysis-result` | `REQ-A5` (`KC`) chưa giải cho **một** provider nào; chưa adapter nào qua probe cô lập; `REQ-OQ03` Owner hoãn. **AC-16 là `BLOCKED`, không phải `FAIL`** |
| **App, Save và Telegram** | `ui/screens.yaml`, `telegram/commands.yaml`, `telegram/delivery.md`, `schemas/saved-snapshot` | `CR-PC07-04`: giới hạn định dạng Telegram vẫn `KC` — **cần đọc Bot API, cần mạng** |
| **Vận hành và phục hồi** | `ops/internet-boundary.md`, `ops/backup-restore.md` | Cơ chế đã chốt và RPO/RTO được chấp nhận (mục 23), nhưng **chưa drill restore nào chạy**. Một runbook chưa từng được thực hiện là thiết kế, không phải bằng chứng |
| **Xác minh và bằng chứng** | `acceptance/*`, `evidence/*`, `precode/*` | Bao gồm chính bản này: `SELF_VALIDATION`, và E1–E4 `NOT_RUN` toàn bộ |

Bốn dòng đầu có cùng một hình dạng: **mỗi phạm vi bị chặn bởi đúng một thứ không thể soạn ra
được** — một con số phải đọc từ tài liệu bên ngoài, một điều khoản phải đọc từ nhà cung cấp, một
giới hạn phải đọc từ Bot API, một drill phải chạy. Đó là lý do tôi tin danh sách này đúng: nếu nó
sai theo hướng dễ dãi, ta sẽ thấy một phạm vi bị chặn bởi thứ gì đó mà thêm vài trang tài liệu là
gỡ được.

### 12.3 Điều `CONTRACT_READY` không thiết lập, ở bất kỳ phạm vi nào

- Bất kỳ nhãn nào từ `IMPLEMENTATION_VERIFIED` trở lên — **chưa có một dòng code nào**. `E0-12`
  cấm tuyệt đối bốn nhãn đó và sẽ fail nếu file nào khai chúng.
- Bất kỳ khẳng định nào về X, Telegram, provider AI, CLI/ACP hay hành vi SQLite thật — chưa thực
  thi gì. Partial UNIQUE index và STORED generated column vẫn là **giả định chưa kiểm**.
- Rằng bốn phạm vi kia đã được ai độc lập xác minh **sau** đợt sửa này. A2-R3 xác minh bản FIX9;
  các thay đổi của FIX10 và của đợt này chưa qua auditor. Theo protocol §8 tôi **không** được tự
  xác minh chúng, và §4.1 là nơi duy nhất nói trạng thái audit thật.

## 13. Giới hạn của chính bản review này

1. **Đây là `SELF_VALIDATION`.** Người viết bản này cũng viết `scenarios.yaml`, `traceability.csv`,
   `gates.yaml`, `manifest.schema.json` và `e0_check.py`. Một công cụ chỉ nhìn nơi tác giả của nó
   nghĩ tới. `F-A1R3-01` tồn tại đúng vì lý do đó.
2. **PC09 không thẩm định lại nội dung kỹ thuật của PC00–PC08.** Bản này đối chiếu tham chiếu,
   chạy check và tổng hợp lời tự khai. Khi nó ghi "CR đã được đáp ứng ngược dòng", đó là lời của
   gói phát ra CR, không phải kết luận độc lập của PC09.
3. **Kiểm tham chiếu bắt được tham chiếu treo, không bắt được tham chiếu thiếu.** Một quan hệ lẽ ra
   phải được viết mà không ai viết thì không check nào ở đây thấy.
4. **Số liệu ghim vào đúng các byte của lần chạy.** Các gói khác sửa fixture và hợp đồng song song
   trong cùng phiên; `baseline_hashes` trong `evidence/runs/` là bản ghi chính xác của những gì đã
   được đọc. Bất kỳ file nào đổi sau đó làm bản ghi tương ứng `STALE` theo INV-06/INV-09.
   Ở đợt này tôi chờ W2 nhả lease `PKT-PC08-FIX2` trước lần chạy cuối, chính vì lý do đó.
5. **Cửa kiểm cột chỉ với tới fixture dùng `rows[]`, và bảng dưới nói chính xác bao nhiêu.** Bản
   trước chỉ khai `collection/` và `recovery/` — thiếu `ai/`, đúng thư mục chứa các fixture đối
   kháng prompt-injection và grounding (`F-A2R1-08`). Số lấy từ `E0-15` (`files_without_rows` mỗi
   thư mục), không lấy từ trí nhớ:

   | Thư mục | Tổng file | Có `rows[]` (được đo) | Không có `rows[]` (**ngoài tầm với**) |
   | --- | ---: | ---: | ---: |
   | `ai/` | 11 | 2 | 9 |
   | `boundary/` | 1 | 0 | 1 |
   | `collection/` | 12 | 4 | 8 |
   | `e2e/` | 1 | 1 | 0 |
   | `identity/` | 14 | 8 | 6 |
   | `recovery/` | 13 | 3 | 10 |
   | `reporting/` | 14 | 13 | 1 |
   | `telegram/` | 18 | 13 | 5 |
   | `ui/` | 2 | 2 | 0 |

   "0 unresolved" của một thư mục **chỉ nói về cột trong các file có `rows[]`**. Với `ai/` nó phủ
   2 trong 11 file; với `recovery/` 3 trong 13; với `boundary/` không file nào — oracle của nó là
   "không hàng nào đổi", không phải một tập hàng. Việc có mở rộng cửa kiểm sang fixture văn xuôi
   hay không là `CR-PC02-18`, và Coordinator đã trả lời: **ACCEPTED_AS_LIMITATION** (§8.2).
6. **`E0-06` và `E0-07` không quét văn xuôi trong `evidence/handoffs/`.** Đây là lựa chọn của đợt
   này (§3.4). Một ID sai chỉ nằm trong câu văn của một handoff sẽ không bị bắt.
7. **`CR-PC04-11` là bằng chứng rằng cửa kiểm tham chiếu của tôi có lỗ.** Hai tên operation không
   tồn tại nằm trong `event_order` của SC52 suốt bản trước và `E0-04` không thấy, vì `E0-04` chỉ
   đọc trường có cấu trúc. Mọi danh sách câu văn trong `scenarios.yaml` đều có cùng rủi ro đó.
8. **Không có validator OpenAPI 3.1**, và packet cấm cài thêm. 221 KB của `openapi.yaml` chưa được
   kiểm tuân thủ đặc tả; một `PASS` ở đây không nói gì về điều đó.
9. **7 AUDIT_REPORT độc lập** (`A1-R1`, `A1-R2`, `A1-R3`, `A2-R1`, `A2-R2`, `A2-R3`, `A2-R4` —
   `audit_reports`, `audit_reports_count`, đếm từ đĩa ở `evidence/audits/`). Bản này trích **verdict
   nguyên văn** của chúng; nó không diễn giải lại và không thay thế chúng. Trạng thái audit được nêu ở **một chỗ duy nhất, §4.1**; mọi mục
   khác trỏ về đó thay vì nhắc lại — đó là kỷ luật `numbers.json` áp cho *trạng thái* chứ không
   chỉ cho *số*, theo ràng buộc của `F-A2R2-01`.
10. **Bốn mục `KC` không giải được trong phiên này vì không có mạng:** `REQ-A5` (điều khoản từng
   nhà AI), `REQ-A6` / `REQ-D34` (nhịp gọi arXiv/OpenAlex), `CR-PC07-04` (giới hạn định dạng
   Telegram), `CR-PC05-03` (URL tài liệu chính thức). Không giá trị nào bị bịa để lấp chỗ trống.
11. **Hai MAJOR của A2 đều là lỗi của tôi và cùng một hình dạng.** `F-A2R1-01` (chín id operation
   không tồn tại) và `F-A2R1-02` (bốn con số headline sai) đều là *một điều đúng đã được viết ra
   rồi không được biến thành thứ tự động kiểm được*: §13 của bản trước cảnh báo đúng lớp lỗi thứ
   nhất bằng chữ, và câu mở đầu của bản trước hứa mọi số đến từ E0. Bài học đã được chuyển thành
   hai cửa kiểm (`E0-04b`, `numbers.py`), nhưng **một cửa kiểm mới chỉ chứng minh được chính nó
   sau khi một người độc lập chạy nó**.
12. **`E0-11b` trước đây tuyên bố nhiều hơn oracle của nó.** Nó tính `mixed` cho cả hai cực và vì
   thế báo mọi invariant đã đủ, trong khi ba invariant không có counterexample chuyên dụng. Bất kỳ
   check nào khác trong bộ này cũng có thể mang cùng khuyết tật — tiêu đề rộng hơn phép đo — và
   tôi không có cách phát hiện nó ngoài việc có người đọc từng oracle.
13. **Phạm vi phê chuẩn được mã hoá bằng một danh sách đường dẫn viết cứng trong `e0_check.py`,
   không bằng cây hợp đồng.** `CONTRACT_READY_INELIGIBLE_PREFIXES` và
   `CONTRACT_READY_INELIGIBLE_FILES` đúng hôm nay và sẽ **sai im lặng** vào lần đầu ai đó thêm một
   file mới vào `contracts/schemas/` — file mới sẽ mặc định *đủ điều kiện*. Đây là `CR-PC01-13` +
   `CR-PC02-22` và tôi để nó mở thay vì vá tạm.
14. **Phê chuẩn là thẩm quyền, không phải bằng chứng.** `OD-20260907-01` làm 84 dòng độ phủ đổi
   trạng thái và bảy module lên `READY_FOR_CARD` mà **không một byte hành vi nào được quan sát**.
   Nếu bản này bị đọc nhanh, đó là chỗ dễ hiểu sai nhất: cái đổi là *ai đã cam kết điều gì*, không
   phải *điều gì đã được chứng minh*. Mọi dòng E1–E4 vẫn `NOT_RUN`.
15. **Thiết kế đánh giá ở §7 chưa được Owner khóa.** Cho tới khi khóa, nó là một đề xuất; một rubric
   chưa khóa không ngăn được việc chỉnh số sau khi nhìn kết quả — đó chính là điều nó tồn tại để
   ngăn.
