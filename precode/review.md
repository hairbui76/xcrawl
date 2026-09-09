---
contract_id: CT-precode-review
version: 0.2.0
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
  - "evidence/audits/A3-R1-report.md"
  - "evidence/audits/A3-R2-report.md"
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
  version: 0.2.0
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
      - "executed_evidence — thêm ở PKT-PC09-P1. Rỗng khi chưa scenario nào phủ dòng này đã CHẠY. `E1: <SC…>` / `E2: <SC…>` / `E1/E2: <SC…>` khi ít nhất một scenario phủ nó mang status `PASS (E1)`/`PASS (E2)` trong acceptance/scenarios.yaml. `PARTIAL_E1_E2: <SC…>` khi scenario phủ nó CHỈ có bằng chứng một phần (`partial_evidence_vi`) — đó KHÔNG phải độ phủ đã chạy, và cột nói vậy thay vì để trống hay tô xanh. Cột này KHÔNG đổi `coverage_status`: độ phủ hợp đồng và việc đã chạy là hai phép đo khác nhau, và trộn chúng là cách nhanh nhất để một baseline nghe có vẻ đã được kiểm."
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

Người viết: `worker-W6` (PC09, verification owner), bổ sung bởi `worker-W6n` ở `PKT-PC09-P1` ·
Ngày: 2026-09-07 (bản PKT-PC09-P1, **sau khi Owner phê chuẩn `OD-20260907-01`** và **sau hai lượt
audit code `A3-R1`/`A3-R2`**) · Claim: `DRAFT_FOR_REVIEW` cho bản review này;
**`CONTRACT_READY` cho bốn phạm vi hợp đồng** — xem §12; và cho **bốn card Giai đoạn 1 cộng
skeleton**, `IMPLEMENTATION_VERIFIED` **có phạm vi**, chống đỡ bởi bản ghi `INDEPENDENT_AUDIT`
chứ không bởi tự kiểm — xem **§14**

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

**Lần chạy E0 của bản này: 27 check, 27 PASS, 0 FAIL, 0 vi phạm** (`e0`, khóa `e0`). Bộ check tăng 24 → 25 ở `PKT-PC09-P1` và → 26 ở `PKT-PC09-P3`, → **27** ở `PKT-PC09-P4` (`E0-21-marker-reason-freshness`) với `E0-19-generated-matches` (mọi `sources[].sha256` của hai
`GENERATED_FROM.json` bằng hash trên đĩa hôm nay — quy tắc "sinh, đừng sửa tay" của ADR-0011 ở
dạng check tĩnh). Hai check **đổi oracle** cùng đợt: `E0-12` mở một ngoại lệ hẹp cho
`IMPLEMENTATION_VERIFIED` trong `evidence/handoffs/**` và `evidence/runs/**` **khi bản ghi trích
dẫn một báo cáo A3** (`CR-P0-02`), và `E0-16` thay lệnh cấm phẳng "mọi status là `NOT_RUN`" bằng
một **yêu cầu có bằng chứng** cho `PASS (E1)`/`PASS (E2)`. Cả ba đã được một self-test âm
**11/11 CAUGHT** chứng minh là cắn thật (`evidence/tools/README.md` §5j).

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

Công cụ: `evidence/tools/e0_check.py` (**27 check**, quét 302 file trong bốn thư mục
`contracts`, `acceptance`, `precode`, `evidence` — `agent-tasks/` **không** nằm trong phạm vi quét,
xem §9.1). Lần chạy đóng gói được đăng ký ở
`evidence/index.json` bản ghi `EV-PC09-01`. `baseline_hashes` gồm các file quét được
(`evidence/runs/` đã bị loại khỏi phạm vi quét — xem §3.5).

**Hai file nhất thiết đổi sau lần chạy mà chúng trích dẫn:** chính `precode/review.md` (nó phải
viết ra kết quả) và `evidence/index.json` (nó phải đăng ký artefact). `baseline_hashes` vì thế ghi
bytes của hai file đó **trước** bước cuối. Đây là vòng lặp không tránh được, không phải một khoảng
lệch bị giấu; mọi file hợp đồng, fixture và scenario khác trong bản ghi là bytes cuối cùng.

**27 PASS · 0 FAIL · 0 vi phạm** (`e0` trong `numbers.json`).

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

**22 AUDIT_REPORT độc lập đã chạy** (`audit_reports_count`, cập nhật ở `PKT-PC09-P5`):
`A1-R1..R3`, `A2-R1..R7` (baseline hợp đồng), rồi **mười hai lượt audit code** —
`A3-R1..R4` trên `FC-P1` epoch 1–4, `A3-P2-R1` trên `FC-P2`, `A3-P3-R1/R2`, `A3-P4-R1/R2`, và
**`A3-P5-R1/R2/R3`** trên `FC-P5` epoch 1–3.

**Cả 22 bản nay nằm trong repo** tại `evidence/audits/` (`audit_reports_in_repo_count`, ĐẾM
từ thư mục), **nguyên vẹn từng byte** so với bản gốc (`cmp`-verified — ba bản P5 được `cmp`
lại trong chính gói này). `CR-PC09-18` — bản `A3-P2-R1` từng thiếu vì `evidence/audits/` không
nằm trong write set của `PKT-PC09-P2` — nay **đã đóng**: bản đó có mặt và bản ghi
`EV-A3-11-p2-overall` ghim được sha256 của nó như mọi bản ghi khác.

**31 bản ghi `INDEPENDENT_AUDIT`, và điều chúng KHÔNG phải.** Mười hai lượt A3 có bản ghi
tương ứng (`EV-A3-01`…`EV-A3-31`, gồm verdict từng card và verdict từng lượt); mười báo cáo
`A1`/`A2` thì **không** — không ai được chỉ thị chép chúng, và một Worker không tự quyết định
việc đó. **Ba bản ghi mới nhất (`EV-A3-29/30/31`) là những bản ghi đầu tiên trong chỉ mục dựa
trên một lần chạy Ở MỨC TIẾN TRÌNH** — uvicorn thật, curl thật qua TCP — chứ không qua
`TestClient`. Điều đó **không** làm chúng thành bằng chứng live: không lời gọi mạng ra ngoài nào
đã xảy ra, và E3/E4 vẫn `NOT_RUN`.

**Một thay đổi về nguyên tắc, và lý do của nó.** Cho tới bản trước, các báo cáo này **không** được
đăng ký thành evidence record, với lập luận đúng rằng một Worker không được ghi bản ghi bằng chứng
thay cho Auditor; `evidence/index.json` vì thế nêu `independent_audit_records_in_repo` = 0. Ở
`PKT-PC09-P1`, Coordinator chỉ thị đăng ký verdict của `A3` thành **sáu** bản ghi
`INDEPENDENT_AUDIT` (`EV-A3-01`…`EV-A3-06`), vì trần claim của Giai đoạn 0/1 chỉ có thể được chống
đỡ bởi một bản ghi kiểu đó. Giới hạn cũ **vẫn đúng và vẫn được khai**: mỗi bản ghi nói thẳng trong
`limitations.not_checked_vi` rằng nó là một **BẢN CHÉP** do `worker-W6n` viết, ghim sha256 của cả
hai báo cáo trong `artifacts[]`, và tuyên bố rằng nếu bản chép lệch với báo cáo thì **báo cáo
thắng**. Hai con số trong `evidence/index.json` vì vậy nay là
`independent_audit_reports_archived_in_repo` = 22 và `independent_audit_records_in_repo` = 31 — vẫn
đo hai thứ khác nhau (một bản báo cáo có thể sinh nhiều bản ghi: một cho từng card, một cho
lượt), và vẫn cả hai được đếm từ đĩa.

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
| `A2-R6` | epoch 9 (`F-A2R5-01..07`) | **PASS** (scoped, ceiling `DRAFT_FOR_REVIEW`) | re-review có phạm vi của bảy finding A2-R5 |
| `A2-R7` | không có freeze manifest (card đang re-pin song song); hai tài liệu `docs/master-plan.md`, `ADR-0011` | **PASS with findings** cho cả hai tài liệu | 5 LOW (`F-A2R7-01..05`). **Báo cáo chưa được chép vào repo** — `CR-PC09-15` |
| `A3-R1` | **`FC-P1` epoch 1 — CODE**, Giai đoạn 0 + bốn card M1 | **FAIL** | 15 finding: 2 HIGH (`-01`, `-02`), 6 MEDIUM, 7 LOW. Theo card: 3 PASS, `TC-owner-auth-session` **FAIL** |
| `A3-R2` | `FC-P1` epoch 2 (bản sửa + `AMD-ENT-owner-01`) | **PASS** cho phạm vi review | `F-A3R1-01..15`: **13 VERIFIED · 1 PARTIAL · 1 DEFERRED · 0 NOT_VERIFIED**. 4 finding mới (`F-A3R2-01..04`): 3 MEDIUM, 1 LOW, **0 HIGH** — tất cả nằm trong *bằng chứng* của bản sửa. Cả bốn card PASS, nhãn đứng được **có phạm vi**. Chi tiết ở **§14** |
| `A3-R3` | `FC-P1` epoch 3 (`F-A3R2-01..04` + việc đăng ký bằng chứng của PC09) | **PASS** | **4/4 `F-A3R2-*` VERIFIED** (`-02` bằng mutation harness của chính auditor); `F-A3R1-03` **đóng** bởi việc đăng ký. Một mục PC09 **PARTIAL**. 3 finding mới (`F-A3R3-01..03`): 2 MEDIUM, 1 LOW, **0 HIGH** — **cả ba nhắm vào bản ghi bằng chứng của PC09**, không vào bốn card. Verdict từng card **không đổi** so với `A3-R2` §5.1 |
| `A3-R4` | `FC-P1` epoch 4 (`F-A3R3-01..03` — cả ba là bản ghi bằng chứng của PC09) | **PASS** | 3/3 **VERIFIED** bằng tái lập của chính auditor; hai phần mở rộng mà PC09 tự khai là vượt câu chữ packet đều được xét là hợp lý, **một trong hai làm mạnh thêm cổng**. 1 finding mới `F-A3R4-01` (LOW) |
| `A3-P2-R1` | **`FC-P2`, 466 entry** — Giai đoạn 2 (ba card, ranh giới mạng, bốn dữ kiện `REQ-A6`, cổng probe) | **PASS** | **HIGH 0 · MEDIUM 0 · LOW 2** (`F-A3-P2-01/-02`, cả hai **PARKED**). Hai kết quả mạnh nhất là phép đo chứ không phải đọc: suite xanh với **mọi socket và DNS bị chặn**, và bốn dữ kiện `REQ-A6` tái lập **nguyên văn** từ tài liệu auditor tự tải. Chi tiết ở **§15** |

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
được tự xác minh bản sửa của mình, nên "**27/27 PASS, 0 vi phạm**" ở §3 là **con số của phía sửa,
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
| `CR-PC09-15` | `A2-R7-report.md` đã chạy nhưng **không** nằm trong `evidence/audits/`; nó ngoài write set của `PKT-PC09-P1` | Coordinator định tuyến | **ĐÃ ĐÁP ỨNG** ở `PKT-PC09-P1-FIX1` bởi gói sở hữu `evidence/audits/`: `A2-R7` và `A3-R3` đều đã được chép, 13 = 13. Đây là **lời khai** của tôi về việc của gói khác, chưa được xác minh độc lập |
| `CR-PC09-17` | **`E0-12` nay đọc `evidence/index.json` ngoài hai cây mà `CR-P0-02` nêu tên.** Packet `PKT-PC09-P1-FIX1` bảo mở rộng sang `evidence/runs/**`; tôi mở rộng sang **ba** vị trí vì index nhúng nguyên văn từng bản ghi, nên một nhãn lọt vào đó là một nhãn trong một bản ghi. Đây là một Worker đọc quy tắc của Coordinator **rộng hơn câu chữ** | Coordinator | **OPEN** — xin phê chuẩn cách đọc này hoặc thu hẹp nó. Nó là một **siết chặt** so với trước (`supports_label` từng không được kiểm ở file nào) nhưng đồng thời **mở rộng quyền** `CR-P0-02` sang một đường dẫn thứ ba, và điều đó cần một ruling chứ không phải một quyết định của tôi |
| `CR-PC09-16` | **Mọi manifest E1 của card ghim `acceptance/scenarios.yaml` trong `baseline.contract_hashes`, và PC09 phải sửa chính file đó để ghi status scenario.** Vì vậy một lần đóng gói của PC09 **luôn** làm bốn manifest của card `STALE` ở lớp bytes-đã-đọc, kể cả khi không kết luận nào bị lật. Đây là lỗi thiết kế của thứ tự công việc, không phải lỗi của Worker nào | Coordinator (thứ tự packet) + PC09 | **OPEN**. Hai lối thoát khả dĩ, cả hai cần một ruling: (a) card ghim `acceptance/scenarios.yaml` **theo SC id** thay vì theo hash toàn file, như card đã làm cho ba file của PC09 ở §0; hoặc (b) PC09 ghi status scenario **trước** khi card chạy, không sau. Hiện tại: `TC-canonical-identity-merge` mang ba pin đã-đọc lệch, cả ba được truy nguyên đích danh ở §14.6 |

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
`CR-(PC\d\d|P0|TC-<CARD>)-\d\d`, rồi gán trạng thái theo một quy tắc duy nhất, áp đồng đều:

- **RULED → FIX_PROPOSED** — id xuất hiện trong một file ruling của Coordinator: bản sửa đã được
  lệnh, và nó là `FIX_PROPOSED` cho tới khi một auditor độc lập xác minh.
- **CLOSED_CLAIMED** — một dòng trong handoff vừa chứa id vừa nói đã đóng. Đây là **lời khai** của
  gói phát ra hoặc gói nhận, **không** phải một closure đã xác minh.
- **OWNER** — id xuất hiện trong `precode/owner-decision-request.md`.
- **OPEN** — mọi trường hợp còn lại.
- Hai id mang disposition tường minh của Coordinator và được ghi bằng chính disposition đó.

**Đợt PKT-PC09-P1 mở rộng cửa quét, và đó là điểm đáng đọc nhất của bảng này.** Mẫu cũ chỉ khớp
`CR-PC\d\d-\d\d`. Giai đoạn 0/1 phát ra CR ở **ba dạng khác** — `CR-P0-nn` (skeleton) và
`CR-TC-<CARD>-nn` (bốn card, hai cách viết hoa) — nên **41 CR** đã tồn tại trên đĩa mà không bảng
nào thấy. Đó cùng một lớp lỗi với `F-A2R1-04`, chỉ ở vòng sau: một CR không nằm trong sổ nào là
một quyết định có thể được ship như đã chốt mà không ai chốt nó. Danh sách hợp nhất mà Coordinator
trích trước đó (`…/scratchpad/phase1-cr-consolidated.txt`) đếm **32**; con số đúng khi gói này
chạy là **41**, vì đợt sửa sau `A3-R1` phát thêm chín id (`CR-TC-IDENTITY-11..15`,
`CR-TC-AUTH-07/-08`, `CR-TC-ingest-07`, `CR-P0-06`). Chênh lệch được nêu thay vì được làm tròn.

**Tổng: 319 CR** (artefact `cr_summary-…` của `EV-PC09-01`) — **157** dạng `CR-PC<nn>` (PC00–PC10),
**6** dạng `CR-P0-nn`, **156** dạng `CR-TC-<CARD>-nn`. Phân bố trạng thái: ACCEPTED_AS_LIMITATION 1 · ACCEPT_AS_LIMITATION 2 · APPROVED 1 · CLOSED_BY_PHASE1 1 · CLOSED_CLAIMED 46 · DEFERRED_TO_CARD 1 · DUPLICATE_CLOSED 1 · FIXED_THIS_PACKET 1 · HANDOFF_TO_CARD 3 · NEXT_CONTRACT_ROUND 18 · NEXT_ROUND 1 · OPEN 203 · PARTIALLY_CLOSED 1 · RESOLVED_BY_PROTOCOL 2 · RULED 36 · SUPERSEDED 1.

**12 trong số đó chạm một file `CONTRACT_READY`** và vì vậy — khi được áp dụng — cần một lần
**re-freeze cộng A2 xác minh**, không phải một lần sửa lặng lẽ: `CR-TC-AUTH-01`, `CR-TC-AUTH-04`, `CR-TC-IDENTITY-02`, `CR-TC-IDENTITY-05`, `CR-TC-IDENTITY-06`, `CR-TC-IDENTITY-07`, `CR-TC-IDENTITY-08`, `CR-TC-IDENTITY-10`, `CR-TC-ingest-02`, `CR-TC-ingest-03`, `CR-TC-ingest-05`, `CR-TC-storage-04`. Cột "Trạng thái / đề xuất xử
lý" đánh dấu chúng bằng `CONTRACT_TOUCH`.

**Cột "đề xuất xử lý" là ĐỀ XUẤT.** PC09 không đóng finding và không quyết định thay đổi hợp đồng
(protocol §8). Khi một CR vừa có ruling của Coordinator vừa có đề xuất của gói này, **cả hai** được
in, ngăn cách bởi dấu `+`.

Bảng thứ hai bên dưới liệt kê **finding của chín lượt audit A3** (`A3-R1..R4`, `A3-P2-R1`, `A3-P3-R1/R2`, `A3-P4-R1/R2`) (`A3-R1..R4` trên FC-P1, `A3-P2-R1` trên FC-P2, `A3-P3-R1`/`-R2` trên FC-P3) (`A3-R1..R4` trên FC-P1, `A3-P2-R1` trên FC-P2). Chúng không phải CR và không
thuộc gói nào: quyền disposition là của Coordinator. Trạng thái lấy nguyên từ bảng xác minh của
lượt SAU, không từ lời tự khai của gói sửa — `F-A3R1-01…15` từ `A3-R2` §2 (**13 VERIFIED · 1
PARTIAL · 1 DEFERRED · 0 NOT_VERIFIED**) và `F-A3R2-01…04` từ `A3-R3` §2 (**4/4 VERIFIED**).
`F-A3R3-01…03` ở `FIX_PROPOSED`: cả ba là của PC09, cả ba đã được sửa ở `PKT-PC09-P1-FIX1`, và
**không cái nào được tự xác minh** — bản sửa đến sau báo cáo và người viết bản sửa không được là
người kiểm nó (protocol §8).

Hai disposition của Coordinator, ghi rõ vì chúng là quyết định chứ không phải quan sát:

- **`CR-PC01-09` — APPROVED.** `UNAUTHORIZED_COMMAND` và `RESTORE_UNVERIFIED` (mã của SRC-PLAN §10)
  là mã hợp lệ cho denied case nằm **ngoài** bảng bốn dòng R5-01, khi đặc tả gọi tên chúng. Chữ
  "đang chờ phê chuẩn" trong `modules.yaml` và `boundary/README.md` phải đổi thành "đã duyệt
  (Coordinator, A2-R1)" — việc của W2.
- **`CR-PC02-18` — ACCEPTED_AS_LIMITATION.** Cửa kiểm cột R4-01 áp cho fixture dạng `rows[]`. Các
  fixture văn xuôi gốc giữ nguyên và được **khai** là `NOT_APPLICABLE_FREEFORM`, với danh sách
  từng thư mục ở §13. Điều này cũng giải `F-A2R1-08`.

| CR | Chủ sở hữu (gói) | Trạng thái / đề xuất xử lý | Ghi chú | Xuất hiện ở |
| --- | --- | --- | --- | --- |
| `CR-PC00-01` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/A2-R1-report.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+14 file) |
| `CR-PC00-02` | — | OPEN |  | `evidence/audits/A1-R1-report.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC00-03` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+12 file) |
| `CR-PC00-04` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC00-05` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+12 file) |
| `CR-PC00-06` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC00-07` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC00-08` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+12 file) |
| `CR-PC00-09` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+12 file) |
| `CR-PC00-10` | — | OPEN |  | `evidence/coordination/00-coordination-baseline.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md` (+14 file) |
| `CR-PC00-11` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC00-12` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+14 file) |
| `CR-PC00-13` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC00-14` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC00-15` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC00-16` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+14 file) |
| `CR-PC00-17` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC00-18` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+14 file) |
| `CR-PC00-19` | — | OPEN |  | `evidence/coordination/README.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md` (+11 file) |
| `CR-PC00-20` | — | OPEN |  | `evidence/coordination/PC09-PHASE1-packet.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md` (+15 file) |
| `CR-PC00-21` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC00-22` | — | OPEN |  | `evidence/audits/README.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md` (+11 file) |
| `CR-PC00-23` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T123537Z.json` (+8 file) |
| `CR-PC00-24` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+5 file) |
| `CR-PC00-25` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+5 file) |
| `CR-PC00-26` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+7 file) |
| `CR-PC00-27` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+9 file) |
| `CR-PC00-28` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+5 file) |
| `CR-PC00-29` | — | OPEN |  | `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC10-handoff.md` (+7 file) |
| `CR-PC00-30` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/coordination/PHASE3-5-card-dispatch.md`, `evidence/coordination/README.md` (+6 file) |
| `CR-PC00-31` | — | OPEN |  | `agent_profile/registry.json`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json` (+9 file) |
| `CR-PC00-32` | — | OPEN |  | `agent_profile/registry.json`, `evidence/audits/A3-P3-R1-report.md`, `evidence/coordination/A3-p3-r1-packet.md` (+8 file) |
| `CR-PC00-33` | — | OPEN |  | `evidence/audits/README.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json` (+4 file) |
| `CR-PC00-34` | — | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `evidence/runs/numbers-20260908T021143Z.json` (+4 file) |
| `CR-PC00-35` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-analysis-adapter-validation.md`, `agent-tasks/TC-analysis-once-per-generation.md`, `agent-tasks/TC-backfill-pending-ledger.md` (+28 file) |
| `CR-PC00-36` | — | OPEN |  | `evidence/coordination/WIRING-wave-1.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json` (+2 file) |
| `CR-PC00-37` | — | OPEN |  | `evidence/coordination/A3-p4-r2-packet.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `evidence/runs/numbers-20260908T021143Z.json` (+2 file) |
| `CR-PC01-01` | — | OPEN |  | `contracts/errors.yaml`, `contracts/modules.yaml`, `contracts/ports.yaml` (+17 file) |
| `CR-PC01-02` | — | OPEN |  | `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json`, `agent-tasks/TC-scheduler-lease-claim.md` (+23 file) |
| `CR-PC01-03` | — | OPEN |  | `contracts/errors.yaml`, `contracts/ports.yaml`, `evidence/audits/A1-R1-report.md` (+15 file) |
| `CR-PC01-05` | — | OPEN |  | `acceptance/scenarios.yaml`, `contracts/data/entities.yaml`, `contracts/http/openapi.yaml` (+21 file) |
| `CR-PC01-06` | — | OPEN |  | `contracts/modules.yaml`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC01-07` | — | OPEN |  | `contracts/ports.yaml`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+13 file) |
| `CR-PC01-08` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/ops/secrets.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+14 file) |
| `CR-PC01-09` | — | **APPROVED** (Coordinator, A2-R1) | UNAUTHORIZED_COMMAND và RESTORE_UNVERIFIED là mã hợp lệ cho denied case nằm ngoài bảng bốn dòng R5-01 khi đặc tả gọi tên chúng | `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `contracts/modules.yaml` (+20 file) |
| `CR-PC01-10` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `contracts/modules.yaml` (+15 file) |
| `CR-PC01-11` | — | OPEN |  | `evidence/audits/A2-R5-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+24 file) |
| `CR-PC01-12` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC01-handoff.md` (+14 file) |
| `CR-PC01-13` | — | OPEN |  | `docs/master-plan.md`, `evidence/coordination/A2-ratification-verify-packet.md`, `evidence/coordination/coordinator-ledger.md` (+16 file) |
| `CR-PC02-01` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC02-02` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC02-03` | — | OPEN |  | `contracts/data/entities.yaml`, `contracts/data/invariants.md`, `contracts/schemas/saved-snapshot.schema.json` (+15 file) |
| `CR-PC02-04` | — | OPEN |  | `contracts/data/entities.yaml`, `contracts/http/openapi.yaml`, `contracts/schemas/ingest-batch.schema.json` (+15 file) |
| `CR-PC02-05` | — | OPEN |  | `agent-tasks/TC-canonical-identity-merge.md`, `contracts/data/entities.yaml`, `contracts/errors.yaml` (+20 file) |
| `CR-PC02-06` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `agent-tasks/TC-canonical-identity-merge.md`, `agent-tasks/TC-report-coverage-publish-cas.md` (+31 file) |
| `CR-PC02-07` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/invariants.md`, `contracts/ops/backup-restore.md`, `evidence/audits/A2-R1-report.md` (+16 file) |
| `CR-PC02-08` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/identity/README.md`, `evidence/audits/A1-R1-report.md`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC02-09` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/A1-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC02-10` | — | OPEN |  | `evidence/audits/A1-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC02-11` | — | OPEN |  | `evidence/audits/A1-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC02-12` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-ingest-idempotent-ack-lost.md`, `contracts/data/entities.yaml`, `contracts/state/run.yaml` (+22 file) |
| `CR-PC02-13` | — | OPEN |  | `acceptance/fixtures/identity/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC02-handoff.md` (+13 file) |
| `CR-PC02-14` | — | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC02-15` | — | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC02-16` | — | OPEN |  | `contracts/data/entities.yaml`, `contracts/modules.yaml`, `evidence/coordination/coordinator-ledger.md` (+15 file) |
| `CR-PC02-17` | — | OPEN |  | `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `contracts/data/entities.yaml`, `contracts/telegram/commands.yaml` (+16 file) |
| `CR-PC02-18` | — | **ACCEPTED_AS_LIMITATION** (Coordinator, A2-R1) | cửa kiểm cột R4-01 áp cho fixture dạng `rows[]`; các fixture văn xuôi giữ nguyên và được khai là NOT_APPLICABLE_FREEFORM | `evidence/audits/A2-R1-report.md`, `evidence/audits/A2-R2-report.md`, `evidence/audits/A2-R3-report.md` (+19 file) |
| `CR-PC02-19` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC02-20` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC02-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC02-21` | — | OPEN |  | `contracts/data/entities.yaml`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC02-22` | — | OPEN |  | `contracts/data/entities.yaml`, `docs/master-plan.md`, `evidence/audits/A2-R7-report.md` (+19 file) |
| `CR-PC02-23` | — | OPEN |  | `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+3 file) |
| `CR-PC02-24` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `contracts/modules.yaml`, `evidence/handoffs/PC02-handoff.md` (+2 file) |
| `CR-PC02-25` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/handoffs/PC02-handoff.md`, `evidence/index.json` (+3 file) |
| `CR-PC03-01` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/ports.yaml`, `evidence/coordination/FIX3-rulings.md`, `evidence/coordination/coordinator-ledger.md` (+18 file) |
| `CR-PC03-02` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-scheduler-lease-claim.md`, `contracts/errors.yaml`, `contracts/ports.yaml` (+25 file) |
| `CR-PC03-03` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/state/run.yaml`, `evidence/coordination/FIX3-rulings.md` (+15 file) |
| `CR-PC03-04` | — | OPEN |  | `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `agent-tasks/WALKTHROUGH.md`, `contracts/errors.yaml` (+20 file) |
| `CR-PC03-05` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/ai/tasks.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml` (+23 file) |
| `CR-PC03-06` | — | OPEN |  | `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/d-empty-period-coverage-only.json`, `contracts/reporting/time-and-tags.md` (+19 file) |
| `CR-PC03-07` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/state/delivery.yaml`, `evidence/coordination/FIX3-rulings.md` (+16 file) |
| `CR-PC03-08` | — | OPEN |  | `evidence/handoffs/PC03-REQA6-handoff.md`, `evidence/handoffs/PC07-TELEGRAM-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json` (+8 file) |
| `CR-PC04-01` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `evidence/coordination/FIX3-rulings.md` (+16 file) |
| `CR-PC04-02` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-backfill-pending-ledger.md`, `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md` (+21 file) |
| `CR-PC04-03` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `evidence/coordination/FIX3-rulings.md` (+16 file) |
| `CR-PC04-04` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json`, `agent-tasks/TC-report-coverage-publish-cas.md`, `contracts/ports.yaml` (+20 file) |
| `CR-PC04-05` | — | OPEN |  | `agent-tasks/TC-ui-reports-detail.md`, `contracts/ai/grounding.md`, `contracts/ai/tasks.yaml` (+18 file) |
| `CR-PC04-06` | — | OPEN |  | `acceptance/fixtures/reporting/README.md`, `acceptance/scenarios.yaml`, `contracts/reporting/time-and-tags.md` (+15 file) |
| `CR-PC04-07` | — | OPEN |  | `agent-tasks/TC-backfill-pending-ledger.md`, `contracts/reporting/time-and-tags.md`, `contracts/ui/screens.yaml` (+15 file) |
| `CR-PC04-08` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-report-coverage-publish-cas.md`, `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md` (+20 file) |
| `CR-PC04-09` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `contracts/state/report.yaml` (+17 file) |
| `CR-PC04-10` | — | OPEN |  | `contracts/reporting/time-and-tags.md`, `evidence/audits/A2-R1-report.md`, `evidence/handoffs/PC04-handoff.md` (+13 file) |
| `CR-PC04-11` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json`, `acceptance/scenarios.yaml`, `evidence/audits/A2-R1-report.md` (+16 file) |
| `CR-PC05-01` | — | OPEN |  | `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/a-feed-layout-changed.json`, `agent-tasks/TC-collector-checkpoint-resume.md` (+25 file) |
| `CR-PC05-02` | — | OPEN |  | `contracts/http/openapi.yaml`, `evidence/handoffs/PC05-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC05-03` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-research-connector-metadata.md`, `agent-tasks/TC-x-feasibility-probe.md`, `contracts/ops/collector-probe.md` (+31 file) |
| `CR-PC05-04` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC05-handoff.md` (+13 file) |
| `CR-PC05-05` | — | OPEN |  | `contracts/ports.yaml`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC01-handoff.md` (+14 file) |
| `CR-PC05-06` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json`, `contracts/http/openapi.yaml` (+23 file) |
| `CR-PC05-07` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/l-purge-all-two-phase-and-negatives.json`, `acceptance/scenarios.yaml` (+26 file) |
| `CR-PC06-01` | — | OPEN |  | `agent-tasks/TC-analysis-once-per-generation.md`, `contracts/retry-policy.yaml`, `contracts/state/analysis.yaml` (+17 file) |
| `CR-PC06-02` | — | OPEN |  | `agent-tasks/TC-analysis-once-per-generation.md`, `contracts/data/entities.yaml`, `evidence/coordination/coordinator-ledger.md` (+16 file) |
| `CR-PC06-03` | — | OPEN |  | `agent-tasks/TC-analysis-adapter-validation.md`, `contracts/capabilities.yaml`, `evidence/coordination/coordinator-ledger.md` (+15 file) |
| `CR-PC06-04` | — | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-analysis-adapter-validation.md`, `docs/master-plan.md` (+17 file) |
| `CR-PC06-05` | — | OPEN |  | `agent-tasks/TC-ui-reports-detail.md`, `evidence/handoffs/PC06-handoff.md`, `evidence/handoffs/TC-ui-reports-detail-handoff.md` (+16 file) |
| `CR-PC07-01` | — | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-telegram-linking-auth.md`, `contracts/telegram/commands.yaml` (+24 file) |
| `CR-PC07-02` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `contracts/data/entities.yaml` (+18 file) |
| `CR-PC07-03` | — | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-telegram-linking-auth.md`, `evidence/handoffs/PC07-handoff.md` (+19 file) |
| `CR-PC07-04` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json`, `acceptance/scenarios.yaml` (+88 file) |
| `CR-PC07-05` | — | OPEN |  | `agent-tasks/TC-telegram-linking-auth.md`, `contracts/telegram/commands.yaml`, `evidence/handoffs/PC07-handoff.md` (+19 file) |
| `CR-PC07-06` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/telegram/README.md`, `acceptance/scenarios.yaml`, `evidence/audits/A1-R3-report.md` (+16 file) |
| `CR-PC07-07` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc51-first-time-setup.json`, `agent-tasks/TC-analysis-adapter-validation.md` (+20 file) |
| `CR-PC07-08` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC07-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC07-09` | — | OPEN |  | `evidence/handoffs/PC07-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC07-10` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC07-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+14 file) |
| `CR-PC08-01` | — | OPEN |  | `acceptance/fixtures/recovery/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC00-handoff.md` (+15 file) |
| `CR-PC08-02` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-backup-restore-drill.md`, `agent-tasks/TC-owner-auth-session.md`, `contracts/capabilities.yaml` (+20 file) |
| `CR-PC08-03` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`, `acceptance/scenarios.yaml`, `contracts/capabilities.yaml` (+32 file) |
| `CR-PC08-04` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `acceptance/scenarios.yaml` (+30 file) |
| `CR-PC08-05` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `agent-tasks/TC-backup-restore-drill.md`, `contracts/data/entities.yaml` (+20 file) |
| `CR-PC09-01` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/coordination/coordinator-ledger.md` (+16 file) |
| `CR-PC09-02` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC09-handoff.md` (+22 file) |
| `CR-PC09-03` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/state/run.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC03-handoff.md` (+15 file) |
| `CR-PC09-04` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/state/analysis.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC03-handoff.md` (+15 file) |
| `CR-PC09-05` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC09-handoff.md` (+13 file) |
| `CR-PC09-06` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX5-rulings.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md` (+13 file) |
| `CR-PC09-07` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX5-rulings.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/handoffs/PC10-handoff.md` (+14 file) |
| `CR-PC09-08` | — | OPEN |  | `evidence/audits/A2-R1-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md` (+13 file) |
| `CR-PC09-09` | — | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+12 file) |
| `CR-PC09-10` | — | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC09-11` | — | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC09-12` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+12 file) |
| `CR-PC09-13` | — | OPEN |  | `docs/master-plan.md`, `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+13 file) |
| `CR-PC09-14` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC09-15` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/README.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC00-handoff.md` (+12 file) |
| `CR-PC09-16` | — | OPEN |  | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json` (+10 file) |
| `CR-PC09-17` | — | OPEN |  | `evidence/audits/A3-R4-report.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC09-handoff.md` (+10 file) |
| `CR-PC09-18` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/README.md`, `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/coordination/README.md` (+11 file) |
| `CR-PC09-19` | — | OPEN |  | `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/index.json` (+7 file) |
| `CR-PC09-20` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json` (+6 file) |
| `CR-PC09-21` | — | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+6 file) |
| `CR-PC09-22` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json` (+3 file) |
| `CR-PC09-23` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json` (+3 file) |
| `CR-PC09-24` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/handoffs/PC09-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json` (+3 file) |
| `CR-PC10-01` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-analysis-adapter-validation.md`, `agent-tasks/TC-analysis-once-per-generation.md`, `agent-tasks/TC-backfill-pending-ledger.md` (+38 file) |
| `CR-PC10-02` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-collector-checkpoint-resume.md`, `agent-tasks/WALKTHROUGH.md`, `contracts/errors.yaml` (+25 file) |
| `CR-PC10-03` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/WALKTHROUGH.md`, `contracts/capabilities.yaml`, `evidence/coordination/coordinator-ledger.md` (+15 file) |
| `CR-PC10-04` | — | OPEN |  | `agent-tasks/WALKTHROUGH.md`, `evidence/handoffs/PC10-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+13 file) |
| `CR-PC10-05` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `docs/master-plan.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC10-handoff.md` (+13 file) |
| `CR-PC10-06` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC10-handoff.md`, `evidence/runs/cr_summary-20260907T052513Z.json` (+12 file) |
| `CR-PC10-07` | — | OPEN |  | `docs/master-plan.md`, `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/P0-skeleton-handoff.md` (+15 file) |
| `CR-PC10-08` | — | OPEN |  | `agent-tasks/README.md`, `docs/master-plan.md`, `evidence/coordination/coordinator-ledger.md` (+14 file) |
| `CR-PC10-09` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/README.md`, `evidence/coordination/README.md`, `evidence/coordination/coordinator-ledger.md` (+15 file) |
| `CR-PC10-10` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/PC10-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json` (+11 file) |
| `CR-PC10-11` | — | OPEN |  | `evidence/handoffs/PC10-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+9 file) |
| `CR-PC10-12` | — | OPEN |  | `evidence/handoffs/PC10-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+9 file) |
| `CR-PC10-13` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-R3-report.md` (+16 file) |
| `CR-PC10-14` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/A3-P2-R1-report.md`, `evidence/coordination/A3-p2-r1-packet.md`, `evidence/coordination/PHASE2-dispatch-log.md` (+8 file) |
| `CR-PC10-15` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-analysis-adapter-validation.md`, `agent-tasks/TC-analysis-once-per-generation.md`, `agent-tasks/TC-backfill-pending-ledger.md` (+28 file) |
| `CR-PC10-16` | — | OPEN |  | `evidence/handoffs/PC10-handoff.md`, `evidence/tools/README.md` |
| `CR-P0-01` | PC10 / Coordinator | DUPLICATE_CLOSED | gói liên quan tự khai đã đóng; chưa xác minh độc lập · card da duoc re-pin sang epoch hien hanh (ten epoch chi in o review.md §9.1); khong con lech | `evidence/coordination/PC09-PHASE1-packet.md`, `evidence/coordination/PHASE0-skeleton-packet.md`, `evidence/handoffs/P0-skeleton-handoff.md` (+9 file) |
| `CR-P0-02` | PC09 | FIXED_THIS_PACKET | E0-12 nay cho `IMPLEMENTATION_VERIFIED` trong evidence/handoffs va evidence/runs khi ban ghi trich dan mot bao cao A3; contracts/ acceptance/ precode/ khong doi | `evidence/audits/A3-R3-report.md`, `evidence/coordination/PC09-PHASE1-packet.md`, `evidence/handoffs/P0-skeleton-handoff.md` (+17 file) |
| `CR-P0-03` | PC10 | NEXT_CONTRACT_ROUND | gói liên quan tự khai đã đóng; chưa xác minh độc lập · tools/ la cay top-level thu tam; §5.3 phai khai no hoac file phai chuyen vao server/ | `agent-tasks/README.md`, `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/PC00-handoff.md` (+9 file) |
| `CR-P0-04` | Coordinator / PC10 | ACCEPT_AS_LIMITATION | card la van ban da pin va da duoc theo; xin xac nhan lai de hai van ban khong lech tiep | `agent-tasks/README.md`, `evidence/coordination/PHASE4-6-card-dispatch.md`, `evidence/coordination/coordinator-ledger.md` (+9 file) |
| `CR-P0-05` | PC09 | CLOSED_BY_PHASE1 | gói liên quan tự khai đã đóng; chưa xác minh độc lập · loader nay co cua hoi quy that: 8 file test cua bon card doc qua fixture_loader | `evidence/coordination/PC09-PHASE1-packet.md`, `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+7 file) |
| `CR-P0-06` | Coordinator / WS | NEXT_CONTRACT_ROUND | sinh entity registry tu entities.yaml; can packet rieng, chi phi khong nho | `contracts/data/entities.yaml`, `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-R3-report.md` (+21 file) |
| `CR-P0-07` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `docs/owner-runbook.md`, `evidence/audits/A3-P5-R1-report.md`, `evidence/audits/A3-P5-R2-report.md` (+10 file) |
| `CR-P0-08` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md` |
| `CR-P0-09` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md` |
| `CR-P0-10` | — | OPEN |  | `evidence/audits/A3-P5-R2-report.md`, `evidence/audits/README.md`, `evidence/coordination/A3-p5-r2-packet.md` (+2 file) |
| `CR-TC-ANALYSIS-01` | — | OPEN |  | `evidence/coordination/PHASE4-6-card-dispatch.md`, `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` (+9 file) |
| `CR-TC-ANALYSIS-02` | — | OPEN |  | `evidence/coordination/PHASE4-6-card-dispatch.md`, `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` (+9 file) |
| `CR-TC-ANALYSIS-03` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-once-per-generation-E1-20260907T194257Z.json` (+7 file) |
| `CR-TC-ANALYSIS-04` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/handoffs/TC-secret-settings-service-handoff.md` (+9 file) |
| `CR-TC-ANALYSIS-05` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-once-per-generation-E1-20260907T194257Z.json` (+7 file) |
| `CR-TC-ANALYSIS-06` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-once-per-generation-E1-20260907T194257Z.json` (+7 file) |
| `CR-TC-ANALYSIS-07` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json` (+10 file) |
| `CR-TC-ANALYSIS-08` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json` (+2 file) |
| `CR-TC-ANALYSIS-10` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-once-per-generation-E1-20260908T064438Z.json` |
| `CR-TC-AUTH-01` | PC08 / PC10 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | fixture recovery/h seq4 pin FORBIDDEN_EDGE; bon nguon noi CSRF_REJECTED | `acceptance/scenarios.yaml`, `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-P4-R2-report.md` (+18 file) |
| `CR-TC-AUTH-02` | PC02 | RULED → FIX_PROPOSED + CLOSED_BY_AMENDMENT | có ruling của Coordinator; chờ A2 xác minh · AMD-ENT-owner-01 (PROVISIONAL) them password_hash/password_updated_at | `contracts/data/entities.yaml`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+12 file) |
| `CR-TC-AUTH-03` | PC02 | RULED → FIX_PROPOSED + CLOSED_BY_AMENDMENT | có ruling của Coordinator; chờ A2 xác minh · AMD-ENT-owner-01 them failed_login_count/locked_until | `contracts/data/entities.yaml`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+12 file) |
| `CR-TC-AUTH-04` | PC01 / PC08 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | ports.yaml va errors.yaml khong liet ke RATE_LIMITED cho auth.login | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-AUTH-05` | WS / PC01 | NEXT_CONTRACT_ROUND | bo sinh chua pho auth_scope, message_safe_template_vi, details_safe_keys, model inline | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-AUTH-06` | Coordinator | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập · chuoi revision tuyen tinh sau 0002_base_entities; mot head | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-AUTH-07` | PC08 / PC02 | ACCEPT_AS_LIMITATION | cua so 15 phut khong bieu dien duoc bang bon cot; ban cai dat la tap cha dem-lien-tiep | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/index.json`, `evidence/runs/TC-owner-auth-session-E1-20260907T114030Z.json` (+8 file) |
| `CR-TC-AUTH-08` | WM (TC-canonical-identity-merge) | NEXT_ROUND | docstring cua 0004_merge_phase1_heads nay sai; file thuoc card khac | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-AUTH-09` | — | OPEN |  | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/index.json`, `evidence/runs/TC-owner-auth-session-E1-20260908T013458Z.json` (+3 file) |
| `CR-TC-AUTH-10` | — | OPEN |  | `evidence/handoffs/TC-owner-auth-session-handoff.md`, `evidence/index.json`, `evidence/runs/TC-owner-auth-session-E1-20260908T013458Z.json` (+3 file) |
| `CR-TC-AUTH-11` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/README.md`, `evidence/coordination/A3-p4-r2-packet.md` (+6 file) |
| `CR-TC-BACKFILL-01` | — | OPEN |  | `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKFILL-02` | — | OPEN |  | `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/index.json` (+8 file) |
| `CR-TC-BACKFILL-03` | — | OPEN |  | `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backfill-pending-ledger-E1-20260907T220221Z.json` (+4 file) |
| `CR-TC-BACKFILL-04` | — | OPEN |  | `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backfill-pending-ledger-E1-20260907T220221Z.json` (+4 file) |
| `CR-TC-BACKFILL-05` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/audits/A3-P4-R1-report.md`, `evidence/coordination/A3-p4-r1-packet.md`, `evidence/coordination/FIX-P4-wave-rulings.md` (+9 file) |
| `CR-TC-BACKFILL-06` | — | OPEN |  | `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKFILL-07` | — | OPEN |  | `acceptance/scenarios.yaml`, `docs/owner-runbook.md`, `evidence/audits/A3-P4-R1-report.md` (+11 file) |
| `CR-TC-BACKFILL-08` | — | OPEN |  | `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKFILL-09` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/audits/A3-P4-R1-report.md`, `evidence/audits/A3-P4-R2-report.md` (+16 file) |
| `CR-TC-BACKFILL-10` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX-P4-wave-rulings.md`, `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/index.json` (+5 file) |
| `CR-TC-BACKFILL-11` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX-P4-wave-rulings.md`, `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/index.json` (+5 file) |
| `CR-TC-BACKFILL-12` | — | OPEN |  | `evidence/handoffs/TC-backfill-pending-ledger-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKUP-01` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backup-restore-drill-E1-20260908T042000Z.json` (+8 file) |
| `CR-TC-BACKUP-02` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKUP-03` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKUP-04` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backup-restore-drill-E1-20260908T042000Z.json` (+8 file) |
| `CR-TC-BACKUP-05` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backup-restore-drill-E1-20260908T042000Z.json` (+8 file) |
| `CR-TC-BACKUP-06` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-BACKUP-07` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backup-restore-drill-E1-20260908T042000Z.json` (+8 file) |
| `CR-TC-BACKUP-08` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/index.json`, `evidence/runs/TC-backup-restore-drill-E1-20260909T100500Z.json` (+1 file) |
| `CR-TC-COLLECTOR-01` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T132623Z.json`, `evidence/runs/cr_summary-20260907T174152Z.json` (+3 file) |
| `CR-TC-COLLECTOR-02` | — | OPEN |  | `evidence/audits/A3-P2-R1-report.md`, `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/index.json` (+9 file) |
| `CR-TC-COLLECTOR-03` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/index.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T132623Z.json` (+8 file) |
| `CR-TC-COLLECTOR-04` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/index.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json` (+6 file) |
| `CR-TC-COLLECTOR-05` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/index.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T135609Z.json` (+7 file) |
| `CR-TC-COLLECTOR-06` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/index.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T135609Z.json` (+7 file) |
| `CR-TC-COLLECTOR-07` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260907T135609Z.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json` (+4 file) |
| `CR-TC-COLLECTOR-08` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/index.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json` (+2 file) |
| `CR-TC-COLLECTOR-09` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json` (+1 file) |
| `CR-TC-COLLECTOR-10` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260908T063000Z.json` |
| `CR-TC-COLLECTOR-11` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md` (+8 file) |
| `CR-TC-COLLECTOR-12` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json` (+5 file) |
| `CR-TC-COLLECTOR-13` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260909T071605Z.json` |
| `CR-TC-COLLECTOR-14` | — | OPEN |  | `evidence/index.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260909T071605Z.json`, `evidence/runs/TC-collector-checkpoint-resume-E1-20260909T074631Z.json` |
| `CR-TC-COLLECTOR-15` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/handoffs/TC-scheduler-lease-claim-handoff.md` (+4 file) |
| `CR-TC-COLLECTOR-16` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json` (+3 file) |
| `CR-TC-DELIVERY-01` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` (+5 file) |
| `CR-TC-DELIVERY-02` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` (+5 file) |
| `CR-TC-DELIVERY-03` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` (+5 file) |
| `CR-TC-DELIVERY-04` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` (+5 file) |
| `CR-TC-DELIVERY-05` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` (+5 file) |
| `CR-TC-DELIVERY-06` | — | OPEN |  | `evidence/coordination/PHASE4-6-card-dispatch.md`, `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json` (+6 file) |
| `CR-TC-DELIVERY-07` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T193653Z.json` (+5 file) |
| `CR-TC-DELIVERY-08` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json` (+6 file) |
| `CR-TC-DELIVERY-09` | — | OPEN |  | `evidence/handoffs/TC-telegram-linking-auth-handoff.md`, `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json` (+10 file) |
| `CR-TC-DELIVERY-10` | — | OPEN |  | `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-unknown-delivery-E1-20260907T202901Z.json` (+4 file) |
| `CR-TC-DELIVERY-11` | — | OPEN |  | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/handoffs/TC-telegram-unknown-delivery-handoff.md`, `evidence/index.json` (+3 file) |
| `CR-TC-IDENTITY-01` | PC10 / Coordinator | NEXT_CONTRACT_ROUND | card §8 viet 5 post; fixture (h) mang 6 item — code theo fixture | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-02` | PC02 / PC04 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | gói liên quan tự khai đã đóng; chưa xác minh độc lập · fixture (a) moved_counts.first_announced=null vs §8.3 (so); giu bang xfail(strict) | `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/A3-P5-R1-report.md` (+17 file) |
| `CR-TC-IDENTITY-03` | Coordinator | DEFERRED_TO_CARD | gói liên quan tự khai đã đóng; chưa xác minh độc lập · preserved_counts.published_report_item chi do duoc khi card bao cao ton tai | `evidence/audits/A3-R1-report.md`, `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/index.json` (+9 file) |
| `CR-TC-IDENTITY-04` | Coordinator | SUPERSEDED | thay bang CR-TC-IDENTITY-11..13 (quyen so huu ghi o dung cho) | `evidence/audits/A3-R1-report.md`, `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/TC-canonical-identity-merge-E1-20260907T102504Z.json` (+6 file) |
| `CR-TC-IDENTITY-05` | PC10 / PC02 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | ma loi khi vuot identity_merge_max_moved_rows: card noi CONFLICT, errors.yaml noi identity_conflict | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-06` | PC01 / PC10 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | gói liên quan tự khai đã đóng; chưa xác minh độc lập · work.get_detail: openapi ghim 200 vao target.schema.json, ports.yaml mo ta read model rong hon | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/index.json`, `evidence/runs/TC-canonical-identity-merge-E1-20260907T102504Z.json` (+8 file) |
| `CR-TC-IDENTITY-07` | PC02 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | entities.identity_conflict thieu cot luu request_id / conflict_fingerprint | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-08` | PC02 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | move-set khong neu quy tac va cham cho work_label | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-09` | PC10 | NEXT_CONTRACT_ROUND | card §7 goi retry_after; errors.yaml goi retry_after_ms — code theo hop dong | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-10` | PC09 / PC02 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | merge_move_set khong liet ke viec tao alias ma fixture (a) ky vong | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-11` | TC-saved-snapshot | HANDOFF_TO_CARD | saved_snapshot/saved_item da ton tai o 0002b; card sau MO RONG, khong CREATE lan hai | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/index.json` (+8 file) |
| `CR-TC-IDENTITY-12` | TC-analysis-once-per-generation | HANDOFF_TO_CARD | nhu tren cho analysis va work_label | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-13` | TC-report-coverage-publish-cas | HANDOFF_TO_CARD | nhu tren cho first_announced_ledger; them FK khi tao report | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json` (+5 file) |
| `CR-TC-IDENTITY-14` | TC-ingest-idempotent-ack-lost | CLOSED_CLAIMED | WI da dung lai post trong revision ingest; FK post→ingest_receipt nay duoc ep | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-IDENTITY-15` | TC-owner-auth-session | CLOSED_CLAIMED | WA da bo CREATE TABLE owner khoi revision auth; mot dinh nghia duy nhat | `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-PROBE-01` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/index.json`, `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` (+5 file) |
| `CR-TC-PROBE-02` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/index.json`, `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` (+5 file) |
| `CR-TC-PROBE-03` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/index.json`, `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` (+5 file) |
| `CR-TC-PROBE-04` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/index.json`, `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` (+5 file) |
| `CR-TC-PROBE-05` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/index.json`, `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` (+5 file) |
| `CR-TC-PROBE-06` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/index.json`, `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` (+5 file) |
| `CR-TC-PROBE-07` | — | OPEN |  | `evidence/handoffs/TC-x-feasibility-probe-handoff.md`, `evidence/runs/cr_summary-20260907T174152Z.json`, `evidence/runs/cr_summary-20260907T210004Z.json` (+2 file) |
| `CR-TC-REPORT-01` | — | OPEN |  | `docs/owner-runbook.md`, `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-backfill-pending-ledger-handoff.md` (+10 file) |
| `CR-TC-REPORT-02` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json`, `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` (+5 file) |
| `CR-TC-REPORT-03` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json`, `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` (+5 file) |
| `CR-TC-REPORT-04` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/audits/A3-P4-R1-report.md`, `evidence/coordination/FIX-P4-wave-rulings.md`, `evidence/handoffs/TC-embedding-generation-switch-handoff.md` (+10 file) |
| `CR-TC-REPORT-05` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json`, `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` (+5 file) |
| `CR-TC-REPORT-06` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json`, `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` (+5 file) |
| `CR-TC-REPORT-07` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json`, `evidence/runs/TC-report-coverage-publish-cas-E1-20260907T212434Z.json` (+5 file) |
| `CR-TC-REPORT-08` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/A3-p4-r1-packet.md`, `evidence/coordination/FIX-P4-wave-rulings.md`, `evidence/handoffs/TC-embedding-generation-switch-handoff.md` (+10 file) |
| `CR-TC-REPORT-09` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/A3-p4-r1-packet.md`, `evidence/coordination/FIX-P4-wave-rulings.md`, `evidence/handoffs/TC-backfill-pending-ledger-handoff.md` (+16 file) |
| `CR-TC-REPORT-10` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/runs/cr_summary-20260908T021143Z.json`, `precode/review.md` |
| `CR-TC-REPORT-11` | — | OPEN |  | `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json`, `evidence/runs/TC-report-coverage-publish-cas-E1-20260909T081653Z.json` |
| `CR-TC-SAVED-01` | — | OPEN |  | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/index.json`, `evidence/runs/TC-saved-snapshot-E1-20260908T020500Z.json` (+5 file) |
| `CR-TC-SAVED-02` | — | OPEN |  | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+1 file) |
| `CR-TC-SAVED-03` | — | OPEN |  | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/index.json`, `evidence/runs/TC-saved-snapshot-E1-20260908T020500Z.json` (+5 file) |
| `CR-TC-SAVED-04` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent_profile/registry.json`, `evidence/coordination/OWNER-DECISIONS-20260908-10.md`, `evidence/handoffs/PC09-handoff.md` (+12 file) |
| `CR-TC-SAVED-05` | — | OPEN |  | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+1 file) |
| `CR-TC-SAVED-06` | — | OPEN |  | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+1 file) |
| `CR-TC-SAVED-07` | — | OPEN |  | `evidence/coordination/PHASE4-6-card-dispatch.md`, `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/handoffs/TC-telegram-linking-auth-handoff.md` (+10 file) |
| `CR-TC-SAVED-08` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json` (+2 file) |
| `CR-TC-SAVED-09` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/index.json`, `evidence/runs/TC-saved-snapshot-E1-20260908T020500Z.json` (+5 file) |
| `CR-TC-SAVED-10` | — | OPEN |  | `evidence/handoffs/TC-saved-snapshot-handoff.md`, `evidence/index.json`, `evidence/runs/TC-saved-snapshot-E1-20260908T054000Z.json` (+3 file) |
| `CR-TC-SCHED-01` | — | OPEN |  | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json`, `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` (+4 file) |
| `CR-TC-SCHED-02` | — | OPEN |  | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json`, `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` (+4 file) |
| `CR-TC-SCHED-03` | — | OPEN |  | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json`, `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` (+4 file) |
| `CR-TC-SCHED-04` | — | OPEN |  | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json`, `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` (+4 file) |
| `CR-TC-SCHED-05` | — | OPEN |  | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json`, `evidence/runs/TC-scheduler-lease-claim-E1-20260907T212330Z.json` (+4 file) |
| `CR-TC-SCHED-06` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/audits/A3-P5-R1-report.md`, `evidence/coordination/A3-p5-r1-packet.md` (+4 file) |
| `CR-TC-SCHED-07` | — | OPEN |  | `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json`, `evidence/runs/TC-scheduler-lease-claim-E1-20260909T073930Z.json` |
| `CR-TC-SCHED-08` | — | OPEN |  | `evidence/handoffs/TC-collector-checkpoint-resume-handoff.md`, `evidence/handoffs/TC-scheduler-lease-claim-handoff.md`, `evidence/index.json` (+2 file) |
| `CR-TC-SECRET-01` | — | OPEN |  | `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json`, `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json` (+1 file) |
| `CR-TC-SECRET-02` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json` (+2 file) |
| `CR-TC-SECRET-03` | — | OPEN |  | `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json`, `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json` (+1 file) |
| `CR-TC-SECRET-04` | — | OPEN |  | `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json`, `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json` (+1 file) |
| `CR-TC-SECRET-05` | — | OPEN |  | `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json`, `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json` (+1 file) |
| `CR-TC-SECRET-06` | — | OPEN |  | `evidence/handoffs/P0-skeleton-handoff.md`, `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json` (+2 file) |
| `CR-TC-SECRET-07` | — | OPEN |  | `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json`, `evidence/runs/TC-secret-settings-service-E1-20260909T072101Z.json` (+1 file) |
| `CR-TC-SECRET-08` | — | OPEN |  | `evidence/handoffs/TC-secret-settings-service-handoff.md`, `evidence/index.json`, `evidence/runs/TC-secret-settings-service-E1-20260909T075131Z.json` |
| `CR-TC-TGAUTH-01` | — | OPEN |  | `evidence/handoffs/TC-telegram-linking-auth-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+1 file) |
| `CR-TC-TGAUTH-02` | — | OPEN |  | `agent_profile/registry.json`, `evidence/coordination/OWNER-DECISIONS-20260908-10.md`, `evidence/handoffs/PC09-handoff.md` (+13 file) |
| `CR-TC-TGAUTH-03` | — | OPEN |  | `evidence/handoffs/TC-telegram-linking-auth-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+1 file) |
| `CR-TC-TGAUTH-04` | — | OPEN |  | `agent_profile/registry.json`, `evidence/coordination/OWNER-DECISIONS-20260908-10.md`, `evidence/handoffs/PC09-handoff.md` (+8 file) |
| `CR-TC-TGAUTH-05` | — | OPEN |  | `evidence/handoffs/TC-telegram-linking-auth-handoff.md`, `evidence/runs/cr_summary-20260907T210004Z.json`, `evidence/runs/cr_summary-20260908T021143Z.json` (+1 file) |
| `CR-TC-TGAUTH-06` | — | OPEN |  | `evidence/handoffs/TC-telegram-linking-auth-handoff.md`, `evidence/index.json`, `evidence/runs/TC-telegram-linking-auth-E1-20260907T202140Z.json` (+5 file) |
| `CR-TC-UIREPORTS-01` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-02` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-03` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-04` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-05` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-06` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-07` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-08` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-09` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T210916Z.json` (+3 file) |
| `CR-TC-UIREPORTS-10` | — | OPEN |  | `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-reports-detail-E1-20260907T220500Z.json` (+2 file) |
| `CR-TC-adapter-01` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-adapter-validation-E1-20260907T193158Z.json` (+6 file) |
| `CR-TC-adapter-02` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-adapter-validation-E1-20260907T193158Z.json` (+6 file) |
| `CR-TC-adapter-03` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-adapter-validation-E1-20260907T193158Z.json` (+6 file) |
| `CR-TC-adapter-04` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-adapter-validation-E1-20260907T193158Z.json` (+6 file) |
| `CR-TC-adapter-05` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json` (+6 file) |
| `CR-TC-adapter-06` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/audits/A3-P4-R1-report.md`, `evidence/audits/A3-P4-R2-report.md`, `evidence/coordination/A3-p4-r1-packet.md` (+13 file) |
| `CR-TC-adapter-07` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-adapter-validation-E1-20260907T201840Z.json` (+5 file) |
| `CR-TC-adapter-08` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/index.json` (+3 file) |
| `CR-TC-adapter-09` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/index.json`, `evidence/runs/TC-analysis-adapter-validation-E1-20260908T062924Z.json` (+1 file) |
| `CR-TC-adapter-10` | — | OPEN |  | `evidence/handoffs/TC-analysis-adapter-validation-handoff.md`, `evidence/handoffs/TC-analysis-once-per-generation-handoff.md`, `evidence/index.json` (+4 file) |
| `CR-TC-embedding-01` | — | OPEN |  | `evidence/coordination/PHASE4-6-card-dispatch.md`, `evidence/handoffs/TC-embedding-generation-switch-handoff.md`, `evidence/index.json` (+6 file) |
| `CR-TC-embedding-02` | — | OPEN |  | `evidence/handoffs/TC-embedding-generation-switch-handoff.md`, `evidence/handoffs/TC-report-coverage-publish-cas-handoff.md`, `evidence/index.json` (+6 file) |
| `CR-TC-embedding-03` | — | OPEN |  | `evidence/handoffs/TC-embedding-generation-switch-handoff.md`, `evidence/index.json`, `evidence/runs/TC-embedding-generation-switch-E1-20260907T192842Z.json` (+5 file) |
| `CR-TC-embedding-04` | — | OPEN |  | `acceptance/scenarios.yaml`, `evidence/handoffs/TC-embedding-generation-switch-handoff.md`, `evidence/index.json` (+6 file) |
| `CR-TC-ingest-01` | PC02 / TC-scheduler-lease-claim | PARTIALLY_CLOSED | gói liên quan tự khai đã đóng; chưa xác minh độc lập · post.ingest_receipt_id da co FK; run va assignment_lease chua ton tai | `evidence/audits/A3-R1-report.md`, `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md` (+9 file) |
| `CR-TC-ingest-02` | PC02 / PC09 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | fixture f-ingest-replay-idempotent khai mot trang thai FK khong the ton tai | `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json` (+7 file) |
| `CR-TC-ingest-03` | PC01 / PC02 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | ports.yaml bat buoc item_count:0; ingest-receipt.schema.json cam no | `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json` (+7 file) |
| `CR-TC-ingest-04` | PC10 / PC01 | NEXT_CONTRACT_ROUND | card §7 noi 400; openapi noi 422 cho /v1/ingest/* — code theo openapi | `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T103000Z.json` (+7 file) |
| `CR-TC-ingest-05` | PC02 / PC01 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | counts.quarantined co trong wire schema, khong co cot tren ENT-ingest-receipt | `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+12 file) |
| `CR-TC-ingest-06` | PC09 | RESOLVED_BY_PROTOCOL | tran cua card chi len duoc qua ban ghi INDEPENDENT_AUDIT — dung viec da lam o goi nay | `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ingest-idempotent-ack-lost-E1-20260907T113827Z.json` (+7 file) |
| `CR-TC-ingest-07` | TC-canonical-identity-merge | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập · hai dong E501 trong 0002b da duoc sua | `evidence/coordination/coordinator-ledger.md`, `evidence/handoffs/TC-canonical-identity-merge-handoff.md`, `evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md` (+6 file) |
| `CR-TC-research-01` | — | OPEN |  | `evidence/audits/A3-P2-R1-report.md`, `evidence/coordination/A3-p2-r1-packet.md`, `evidence/coordination/PHASE2-dispatch-log.md` (+9 file) |
| `CR-TC-research-02` | — | OPEN |  | `evidence/handoffs/TC-research-connector-metadata-handoff.md`, `evidence/index.json`, `evidence/runs/TC-research-connector-metadata-E1-20260907T135805Z.json` (+5 file) |
| `CR-TC-research-03` | — | OPEN |  | `evidence/handoffs/TC-research-connector-metadata-handoff.md`, `evidence/index.json`, `evidence/runs/TC-research-connector-metadata-E1-20260907T135805Z.json` (+5 file) |
| `CR-TC-research-04` | — | OPEN |  | `evidence/handoffs/TC-research-connector-metadata-handoff.md`, `evidence/index.json`, `evidence/runs/TC-research-connector-metadata-E1-20260907T135805Z.json` (+5 file) |
| `CR-TC-research-05` | — | OPEN |  | `evidence/handoffs/TC-research-connector-metadata-handoff.md`, `evidence/index.json`, `evidence/runs/TC-research-connector-metadata-E1-20260907T164354Z.json` (+4 file) |
| `CR-TC-research-06` | — | OPEN |  | `contracts/ops/collector-probe.md`, `evidence/coordination/PHASE2-dispatch-log.md`, `evidence/handoffs/TC-research-connector-metadata-handoff.md` (+6 file) |
| `CR-TC-storage-01` | P0-skeleton | CLOSED_CLAIMED | tripwire Giai doan 0 da duoc dao chieu boi chu so huu file | `evidence/handoffs/TC-storage-write-blocked-readiness-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-storage-02` | PC09 | RESOLVED_BY_PROTOCOL | nhu CR-TC-ingest-06: SELF_VALIDATION bi chan o CONTRACT_READY la DUNG; nhan len qua A3 | `evidence/handoffs/TC-storage-write-blocked-readiness-handoff.md`, `evidence/index.json`, `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T100943Z.json` (+10 file) |
| `CR-TC-storage-03` | P0-skeleton / WR | CLOSED_CLAIMED | install_auth(app) nay chay trong factory | `evidence/handoffs/TC-storage-write-blocked-readiness-handoff.md`, `evidence/runs/TC-storage-write-blocked-readiness-E1-20260907T100943Z.json`, `evidence/runs/cr_summary-20260907T120836Z.json` (+5 file) |
| `CR-TC-storage-04` | PC02 / PC03 | NEXT_CONTRACT_ROUND · CONTRACT_TOUCH | khong co entity storage_probe; write_blocked→healthy khong the chay that | `acceptance/scenarios.yaml`, `contracts/data/entities.yaml`, `evidence/audits/A3-P2-R1-report.md` (+22 file) |
| `CR-TC-storage-05` | PC10 | CLOSED_CLAIMED | re-pin §0 da chay; card nay pin epoch hien hanh nhu 17 card con lai | `evidence/handoffs/TC-storage-write-blocked-readiness-handoff.md`, `evidence/runs/cr_summary-20260907T120836Z.json`, `evidence/runs/cr_summary-20260907T123537Z.json` (+4 file) |
| `CR-TC-storage-06` | — | OPEN |  | `contracts/data/entities.yaml`, `evidence/coordination/README.md`, `evidence/coordination/WIRING-wave-1.md` (+5 file) |
| `CR-TC-storage-07` | — | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/TC-backup-restore-drill-handoff.md`, `evidence/handoffs/TC-storage-write-blocked-readiness-handoff.md`, `evidence/index.json` (+5 file) |
| `CR-TC-uiruns-01` | — | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/coordination/FIX-P4-wave-rulings.md`, `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json` (+5 file) |
| `CR-TC-uiruns-02` | — | OPEN |  | `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` (+4 file) |
| `CR-TC-uiruns-03` | — | OPEN |  | `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` (+4 file) |
| `CR-TC-uiruns-04` | — | OPEN |  | `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` (+4 file) |
| `CR-TC-uiruns-05` | — | OPEN |  | `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` (+4 file) |
| `CR-TC-uiruns-06` | — | OPEN |  | `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-runs-three-states-E1-20260907T210259Z.json` (+4 file) |
| `CR-TC-uiruns-07` | — | OPEN |  | `evidence/handoffs/TC-ui-runs-three-states-handoff.md`, `evidence/index.json`, `evidence/runs/TC-ui-runs-three-states-E1-20260908T005122Z.json` (+3 file) |
| `CR-TC-uiruns-08` | — | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `evidence/handoffs/TC-ui-reports-detail-handoff.md`, `evidence/handoffs/TC-ui-runs-three-states-handoff.md` (+8 file) |

| Finding (A3) | Chủ sở hữu | Trạng thái | Ghi chú | Xuất hiện ở |
| --- | --- | --- | --- | --- |
| `F-A3-P2-01` | PC05 / PC00 | PARKED (ruling Coordinator) | hai tham chieu cheo "REQ-A6 chua giai" con sot; chi la van ban — trang thai that o decision-register §8.13.2 va retry-policy 0.8.0 moi la tham quyen | `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-P3-R2-report.md` (+16 file) |
| `F-A3-P2-02` | TC-collector-checkpoint-resume (WC) | PARKED (ruling Coordinator) -> CR-TC-COLLECTOR-02 | RecordedSource ship trong collector/app/reader.py: duoc khai, co ly do, va tro; don o mot dot sau | `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-P3-R2-report.md` (+7 file) |
| `F-A3-P3-01` | TC-analysis-adapter-validation (W3A) | VERIFIED (A3-P3-R2 §2) | ruff format --check nay rc=0 tren 134 file; lenh duoc them vao DANH SACH lenh cua card nen no khong tai dien | `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-P3-R2-report.md`, `evidence/audits/README.md` (+14 file) |
| `F-A3-P3-02` | W5A -> W5C | VERIFIED (A3-P3-R2 §2) | hai xfail thanh test that; mot residual duoc khai: xfail(run=False) cho fixture callback — Coordinator CHAP NHAN nguyen trang, no neu mot KC cua hop dong chu khong phai mot card vang mat | `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-P3-R2-report.md`, `evidence/audits/A3-P4-R1-report.md` (+12 file) |
| `F-A3-P3-03` | W3A, W3B, W3C; W6n (rule) | VERIFIED (A3-P3-R2 §2) + quy tac thuong truc | bon fixture da duoc xu ly; va PKT-PC09-P3 bien no thanh E0-20-card-fixture-accounting, mutation 5/5 — lan thu ba cung mot hinh dang thi no thoi lam finding tung vong | `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-P3-R2-report.md`, `evidence/coordination/A3-p3-r2-packet.md` (+25 file) |
| `F-A3-P4-01` | Coordinator | OPEN |  | `evidence/audits/A3-P4-R1-report.md`, `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/README.md` (+12 file) |
| `F-A3-P4-02` | Coordinator | OPEN |  | `evidence/audits/A3-P4-R1-report.md`, `evidence/audits/A3-P4-R2-report.md`, `evidence/coordination/A3-p4-r2-packet.md` (+10 file) |
| `F-A3-P4-03` | Coordinator | OPEN |  | `evidence/audits/A3-P4-R1-report.md`, `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/README.md` (+14 file) |
| `F-A3-P4R2-01` | PC09 (W6n) | FIX_PROPOSED | E0-21 doc reason= mot dong bang ast thay vi regex; mutation 8/8 o PKT-PC09-P4. CHUA duoc ai doc lap kiem — va no chi xuat hien trong bang nay tu PKT-PC09-P5, vi mau nhan dien finding khong thay dang id -P4R2- (loi cua bang, khong phai cua finding) | `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/A3-P5-R1-report.md`, `evidence/audits/A3-P5-R2-report.md` (+6 file) |
| `F-A3-P4R2-02` | W5A (tgauth) | VERIFIED (A3-P5-R1/R2 khong tai nen) | manifest tgauth da duoc phat lai; PC09 bam lai 9 pin: 0 lech | `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/A3-P5-R2-report.md`, `evidence/audits/A3-P5-R3-report.md` (+6 file) |
| `F-A3-P5-01` | W6B (backup_cli) | VERIFIED (A3-P5-R2 §2) | --reason bat buoc khi --open; ngoai le cua guard ra ENVELOPE + exit code thay vi traceback | `evidence/audits/A3-P5-R1-report.md`, `evidence/audits/A3-P5-R2-report.md`, `evidence/audits/README.md` (+9 file) |
| `F-A3-P5-02` | WS (wiring/status) | VERIFIED (A3-P5-R2 §2) | ly do that (SG-DOC/SG-LIVE) va doc tu contracts/retry-policy.yaml luc chay, khong con literal | `evidence/audits/A3-P5-R1-report.md`, `evidence/audits/A3-P5-R2-report.md`, `evidence/audits/README.md` (+4 file) |
| `F-A3-P5-03` | W4A (router) + WS (status) | VERIFIED (A3-P5-R2 §2) | /v1/reports tra mot ma DA KHAI thay vi 500 INTERNAL, neu dich danh CR-P0-07 | `evidence/audits/A3-P5-R1-report.md`, `evidence/audits/A3-P5-R2-report.md`, `evidence/coordination/A3-p5-r2-packet.md` (+6 file) |
| `F-A3-P5-04` | WS (pyproject) | VERIFIED (A3-P5-R2 §2) | [project.scripts]: rr-admin / rr-backup / rr-collector / rr-worker / rr-probe chay tu bat ky cwd nao | `evidence/audits/A3-P5-R1-report.md`, `evidence/audits/A3-P5-R2-report.md`, `evidence/coordination/A3-p5-r2-packet.md` (+3 file) |
| `F-A3-P5R2-01` | W6B (backup_cli) | VERIFIED (A3-P5-R3 §1, ca hai chieu) | NOT_FOUND nay neu dung resource_kind: owner kem lenh sua; snapshot khong ton tai VAN noi snapshot | `evidence/audits/A3-P5-R2-report.md`, `evidence/audits/A3-P5-R3-report.md`, `evidence/audits/README.md` (+7 file) |
| `F-A3-P5R3-01` | W6B (manifest) | VERIFIED (PKT-TC-BACKUP-FIX6 + PC09 bam lai) | manifest phat lai luc 20260909T104000Z: 0 pin SAN XUAT lech va 0 pin DOC lech. Ban duoc dang ky trong evidence/index.json la ban phat lai nay | `evidence/audits/A3-P5-R3-report.md`, `evidence/audits/README.md`, `evidence/handoffs/TC-backup-restore-drill-handoff.md` (+2 file) |
| `F-A3R1-01` | WM / WA | VERIFIED (A3-R2 §2) | mot dinh nghia owner; bon thu tu duyet cho mot chu ky sqlite_master | `contracts/data/entities.yaml`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+21 file) |
| `F-A3R1-02` | W3n / WS / WA | VERIFIED (A3-R2 §2) | AMD-ENT-owner-01 khai bon cot; 0 khac biet cot hai chieu — nhung xem F-A3R2-02 | `contracts/data/entities.yaml`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+18 file) |
| `F-A3R1-03` | PC09 (W6n) | FIX_PROPOSED | dong boi PKT-PC09-P1: bon manifest E1/E2 + sau ban ghi A3 nay nam trong evidence/index.json | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/audits/A3-R3-report.md` (+12 file) |
| `F-A3R1-04` | WM | VERIFIED (A3-R2 §2) | nam bang move-set chuyen sang 0002b_shared_move_set_tables | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+9 file) |
| `F-A3R1-05` | WI / WM | VERIFIED (A3-R2 §2) | FK owner_id va post→ingest_receipt duoc ep that | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+10 file) |
| `F-A3R1-06` | WA | VERIFIED (A3-R2 §2) | lockout ben qua restart, auditor tu chay harness rieng | `contracts/data/entities.yaml`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+14 file) |
| `F-A3R1-07` | WS | VERIFIED (A3-R2 §2) | faults.py duoc nhan vao write set Giai doan 0 kem hash | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+12 file) |
| `F-A3R1-08` | WA | VERIFIED (A3-R2 §2) | phan hoach 12/10/14 = 36 duoc khang dinh; san >=5 da bo | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+9 file) |
| `F-A3R1-09` | WI, WM, WA, WR | VERIFIED (A3-R2 §2) | moi fixture §2/§8 hoac duoc chay hoac NOT_RUN kem ly do | `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+18 file) |
| `F-A3R1-10` | WI | VERIFIED (A3-R2 §2) | server/app/ingest/__init__.py da co | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+7 file) |
| `F-A3R1-11` | WR / WI | PARTIAL (A3-R2 §2) | nua wiring da sua; nua hoi phuc write_blocked→healthy VAN chua — CR-TC-storage-04 | `acceptance/scenarios.yaml`, `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md` (+14 file) |
| `F-A3R1-12` | WA | VERIFIED (A3-R2 §2) | token bam va so bang hmac.compare_digest khong thoat som | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+7 file) |
| `F-A3R1-13` | WR + cac card | VERIFIED (A3-R2 §2) | bon khoi include deu trong delimiter cua rieng no | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+15 file) |
| `F-A3R1-14` | WM | VERIFIED (A3-R2 §2) | owner.created_at co GLOB check mili giay | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+9 file) |
| `F-A3R1-15` | WS | VERIFIED (A3-R2 §2) | ca ba cho deu la uv sync --all-packages | `evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, `evidence/coordination/FIX-A3R1-rulings.md` (+8 file) |
| `F-A3R2-01` | PC02 (W3n) | VERIFIED (A3-R3 §2) | version_rule_vi khai thang khoang trong cua §2 thay vi bia mot luat; CR-PC10-13 mang no sang vong sau | `contracts/data/entities.yaml`, `evidence/audits/A3-R2-report.md`, `evidence/audits/A3-R3-report.md` (+13 file) |
| `F-A3R2-02` | TC-owner-auth-session (WA) | VERIFIED (A3-R3 §2, mutation-tested) | table_xinfo o moi call site, 10 test, so bang hai chieu; auditor tu chay ba dot bien va ca ba bi bat | `evidence/audits/A3-R2-report.md`, `evidence/audits/A3-R3-report.md`, `evidence/audits/A3-R4-report.md` (+13 file) |
| `F-A3R2-03` | WI, WA, WR | VERIFIED (A3-R3 §2) | bon manifest moi nhat deu 0 pin lech; bon ban cu nam o superseded_card_runs | `evidence/audits/A3-P4-R2-report.md`, `evidence/audits/A3-P5-R3-report.md`, `evidence/audits/A3-R2-report.md` (+21 file) |
| `F-A3R2-04` | PC02 (W3n) | VERIFIED (A3-R3 §2) | downstream_vi noi thang cau cu la SAI va nêu 15 nguon sinh that | `contracts/data/entities.yaml`, `evidence/audits/A3-R2-report.md`, `evidence/audits/A3-R3-report.md` (+18 file) |
| `F-A3R3-01` | PC09 (W6n) | FIX_PROPOSED | E0-12 nay doc ca evidence/runs/** va evidence/index.json cho quy tac claim; schema chan INDEPENDENT_AUDIT o IMPLEMENTATION_VERIFIED; 12/12 mutation. CHUA duoc ai doc lap kiem | `evidence/audits/A3-R3-report.md`, `evidence/audits/A3-R4-report.md`, `evidence/audits/README.md` (+16 file) |
| `F-A3R3-02` | PC09 (W6n) | FIX_PROPOSED | sau ban ghi EV-A3 nay khai producer_principal la worker-W6n (transcription), execution kind manual_procedure, exit_code null; lenh va so do cua auditor duoc TRICH trong oracle.observed | `evidence/audits/A3-R3-report.md`, `evidence/audits/A3-R4-report.md`, `evidence/handoffs/PC09-handoff.md` (+6 file) |
| `F-A3R3-03` | PC09 (W6n) | FIX_PROPOSED | review.md §14 nay dung 305/4/0 va 10 test cong schema; F-A3R2-02 khong con trong unresolved_issue_refs | `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-P4-R1-report.md`, `evidence/audits/A3-R3-report.md` (+12 file) |
| `F-A3R4-01` | PC09 (W6n) | FIX_PROPOSED | quy tac claim nay doc ca front matter cua Markdown (claim_fields); E0-12 checked 976 -> 1157; mutation 6/6. Ban sua den SAU bao cao, CHUA duoc ai doc lap kiem | `evidence/audits/A3-P2-R1-report.md`, `evidence/audits/A3-P3-R1-report.md`, `evidence/audits/A3-P3-R2-report.md` (+21 file) |

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
| `MOD-auth-service` | server | READY_FOR_CARD *(có điều kiện)* | Tham số phiên được Owner chấp nhận (mục 23). **CODE TỒN TẠI (M1):** `TC-owner-auth-session` chạy xong, A3-R2 §5.1 PASS, nhãn `IMPLEMENTATION_VERIFIED` đứng được **có phạm vi** — nhưng nhãn nằm trên `AMD-ENT-owner-01` vẫn `PROVISIONAL`, nên nếu Owner phản đối thì cả schema lẫn verdict mở lại |
| `MOD-settings-service` | server | **BLOCKED** | B08 ratified, nhưng **`REQ-OQ03` Owner hoãn** (mục 21) — provider/model cụ thể vẫn `OWNER_DECISION_REQUIRED`. Chặn M3 |
| `MOD-tag-service` | server | READY_FOR_CARD *(có điều kiện)* | B01/B04 ratified; `REQ-OQ04` N = 7 ngày được chấp nhận (mục 20) |
| `MOD-scheduler` | server | READY_FOR_CARD *(có điều kiện)* | B08 ratified với `Asia/Ho_Chi_Minh`; `REQ-OQ06` 08:00/20:00 chấp nhận. Múi giờ không DST ⇒ DST-01/DST-02 chưa kích hoạt |
| `MOD-job-service` | server | READY_FOR_CARD *(có điều kiện)* | B02/B10 ratified |
| `MOD-ingest-service` | server | READY_FOR_CARD *(có điều kiện)* | B05 ratified (câu chữ AC-04). **CODE TỒN TẠI (M1):** `TC-ingest-idempotent-ack-lost` chạy xong, A3-R2 §5.1 PASS. Nhãn chỉ phủ **bốn operation card SẢN XUẤT**; năm operation tiêu thụ chưa được gọi và `works_linked` luôn 0 |
| `MOD-identity-service` | server | READY_FOR_CARD *(có điều kiện)* | B06/B15 ratified. **CODE TỒN TẠI (M1):** `TC-canonical-identity-merge` chạy xong, A3-R2 §5.1 PASS với **hai `xfail(strict=True)`** (`CR-TC-IDENTITY-02/03`) |
| `MOD-research-connector` | server | **BLOCKED (cứng)** | `REQ-A6` `KC`: bốn giá trị rate-limit vẫn `null`/`PLACEHOLDER_KC`. Phê chuẩn không đọc hộ tài liệu arXiv/OpenAlex |
| `MOD-embedding-service` | server | **BLOCKED (cứng)** | `REQ-A3` `KC` và `REQ-OQ09`; mục 20 nói rõ **model chưa đặt cho tới khi đo được** |
| `MOD-analysis-service` | server | READY_FOR_CARD *(có điều kiện)* | B07 ratified. Còn `PROV-PC03-04` (tự chạy lại một lần từ `unknown_attempt`) — **không** nằm trong 25 mục, vẫn `PROVISIONAL` |
| `MOD-report-service` | server | **BLOCKED** | B01/B04/B14/B17 ratified, nhưng bảy tham số mật độ có cổng `REQ-A4` (`KC`, 0/3–4 kỳ) và `REQ-D53` vẫn `ĐX` ở phần hiệu chỉnh |
| `MOD-saved-service` | server | READY_FOR_CARD *(có điều kiện)* | `F-PC00-02` (hoãn export sang P1) được Owner xác nhận (mục 20) |
| `MOD-delivery-service` | server | READY_FOR_CARD *(có điều kiện)* | B03 ratified (câu chữ AC-14) |
| `MOD-telegram-adapter` | server | **BLOCKED (cứng)** | `CR-PC07-04`: giới hạn định dạng Telegram vẫn `KC`. B03/B09/B10 đã hết chặn |
| `MOD-secret-service` | server | **BLOCKED (cứng)** | B13 ratified nhưng `REQ-A5` `KC` — điều khoản từng nhà AI chưa đọc |
| `MOD-data-admin-service` | server | READY_FOR_CARD *(có điều kiện)* | **Gỡ chặn cứng.** Mục 24 chốt phạm vi `data.purge_all`: chỉ dữ liệu nghiên cứu, giữ đăng nhập/secret/liên kết Telegram/cấu hình provider/lịch, **backup không bị xóa**. Còn `CR-PC01-05` (cascade) mở |
| `MOD-data-store` | server | READY_FOR_CARD *(có điều kiện)* | **Giả định đã được KIỂM, không còn là giả định:** partial UNIQUE index và STORED generated column nay chạy trên SQLite thật trong `0002b`/`0003` và được `tests/contract/test_schema_matches_entities.py` cùng bộ test của hai card đọc lại sau `alembic upgrade head`. **CODE TỒN TẠI (M1):** `TC-storage-write-blocked-readiness` chạy xong, A3-R2 §5.1 PASS **đã thu hẹp** — loại trừ bước chuyển `write_blocked → healthy` (`CR-TC-storage-04`) |
| `MOD-backup-service` | server | READY_FOR_CARD *(có điều kiện)* | B11 ratified, RPO 24 h / RTO 2 h chấp nhận (mục 23). **Chưa drill nào chạy** — đó là E1+, không phải điều kiện card |
| `MOD-backup-cli` | server | READY_FOR_CARD *(có điều kiện)* | như trên; `PROV-PC01-04` vẫn `PROVISIONAL` |
| `MOD-health-service` | server | READY_FOR_CARD *(có điều kiện)* | Ngưỡng readiness 30/90/900/1800 s vẫn PROVISIONAL, chưa đo thật. **Kênh health độc lập DB đã chạy thật** (HC-01..HC-04, `SC26` PASS (E2)): liveness `up` trong khi readiness đỏ, không chạm DB |
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

Tại thời điểm chạy bản này lệnh đó trả **`PC10-PIN-P5c-20260909`**, và **20/20 card khai cùng
một epoch** (`card_pin_current`, `card_pin_declared`, `card_pin_unanimous`) — con số card đổi vì
đợt nối dây thêm `TC-secret-settings-service`. `A3-P5-R2` §1 và `A3-P5-R3` §2 kiểm điều mạnh hơn
một bậc: epoch **không đổi** qua cả ba lần freeze của đợt, tức **không file nào được card ghim bị
động**. Chuỗi epoch từ đầu
gói: `FCW4` → `FCW4b` → `FCW4c` → `FCW4d` → `FCW4e` → `FCW4f` → `OD01` → `OD01c` → `P1` → `P1b`
→ `P1c` → `P1d` → `P2` … → `P2d` → `P3` → `P3b` → `P4` → `P4b` → `P5c`; những cái đã bị thay lần lượt như vậy. Bốn
lần re-pin cuối thuộc Giai đoạn 2 (ba card mới, card thứ 19, và bản viết lại §9/§10 của card
connector theo `CR-PC10-14`). `F-A2R1-03` bắt đúng điểm này, và
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
| 10 | E0 đã chạy thật và có manifest; E1–E4 chưa chạy ghi NOT_RUN | ✅ | `evidence/index.json`; **27/27 PASS, 0 vi phạm, exit 0**; **E1/E2 nay đã chạy** cho bốn card (10 bản ghi có `evidence_level` E1/E2 với `result` khác `NOT_RUN`), **E3/E4 vẫn `NOT_RUN` ở mọi nhóm** với 32 placeholder tường minh — xem §14 |
| 11 | Card triển khai pin baseline, paths/stack, contracts và proof obligations | ✅ | **Stack đã chốt (Option B, mục 3)** và 18 card đều pin cùng một epoch — **tên epoch được in ở §9.1 và chỉ ở đó** (`F-A2R3-01`). Điều từng thiếu — "chưa có repo triển khai" — **không còn thiếu**: Giai đoạn 0 dựng bảy cây thư mục thật và `verify_cards.py` cho **13/13, 0 violation**, nghĩa là mọi đường dẫn §3 mà card pin phân giải được trên đĩa (`G5-X4` nay `met: true`). `ADR-0011` nêu tên framework. Xem §14.1 |
| 12 | Readiness report liệt kê module nào READY/BLOCKED | ✅ | §9 |

**Đếm từ chính bảng trên: 11 ✅, 1 ⚠️, 0 ❌** trên 12 dòng (`dor`, parse cơ học).

**Không còn dòng ❌ nào**, và ở đợt `PKT-PC09-P1` dòng #11 chuyển ⚠️ → ✅. Lý do được nêu rõ vì
bản trước **cố ý** giữ nó ở ⚠️: khi đó card mô tả đường dẫn *sẽ* tồn tại, và một DoR nói "paths đã
pin" trong khi paths tự khai `PROVISIONAL` là đúng loại phát biểu mà mọi finding của audit trong
gói này đã bắt. Điều kiện đó nay đã đạt bằng phép đo chứ không bằng lập luận: Giai đoạn 0 dựng bảy
cây thư mục thật, `verify_cards.py` cho **13/13 check, 0 violation** trên 18 card, và một auditor
độc lập chạy lại cùng cửa đó từ bytes đã đóng băng ở cả hai lượt A3. `G5-X4` chuyển `met: true`
cùng lý do và cùng bằng chứng.

Dòng ⚠️ còn lại là #8: giới hạn định dạng Telegram vẫn `KC` (`CR-PC07-04`) — nó cần đọc tài liệu
Bot API, tức cần mạng, và không gỡ được bằng soạn thảo thêm.

Con số này đi 7/3/2 → 10/0/2 (sai) → 8/2/2 → 9/1/2 → 10/2/0 → **11/1/0**, và mỗi lần nó đổi là vì
một dòng của bảng đổi. Cổng tự kiểm so dòng tổng với bảng chạy sau **mỗi** lần sửa; nó bắt được
đúng lần lệch khi tôi sửa dòng #5 mà quên dòng tổng — và lại bắt được ở đợt này khi tôi sửa dòng
#11 mà quên dòng tổng.

---

## 12. Tuyên bố — theo phạm vi, không còn một giá trị chung

**Claim của chính bản review này: `DRAFT_FOR_REVIEW`.** Nó là `SELF_VALIDATION` của người đã viết
một phần corpus mà nó đánh giá; không lượng phê chuẩn nào đổi được điều đó.

Trần claim của **hợp đồng** thì nay là một object theo phạm vi (`precode/baseline.json`
`claim_ceiling.by_scope`), theo `OD-20260907-01` §4. Bốn phạm vi được W1 đặt là
**`CONTRACT_READY_PENDING_E0`** — nghĩa là đủ điều kiện *về quyết định*, còn chờ một lần chạy E0
sạch trên epoch mới. **Lần chạy đóng gói của tôi ở đợt này chính là điều kiện đó**, và nó cho
**27/27 PASS, 0 vi phạm**. Giá trị `CONTRACT_READY_PENDING_E0` → `CONTRACT_READY` là việc của W1:
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

*Phạm vi của mục này bao gồm cả **§14** (Giai đoạn 0/1), **§15** (Giai đoạn 2) và **§16** (Giai đoạn 3/5) và **§17** (Giai đoạn 4/6 + trạng thái sản phẩm), được thêm sau bởi `PKT-PC09-P1`…`-P4`; cả bốn đứng sau §13 để mọi trích dẫn `review.md §13` đã tồn tại vẫn phân giải đúng.*

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

---

## 14. Giai đoạn 0/1 — cái gì tồn tại, cái gì A3 đã xác minh, cái gì vẫn `NOT_RUN`

*Mục này được thêm bởi `PKT-PC09-P1`. Mọi con số dưới đây do `derive_numbers.py` và `crtable.py` sinh; khóa nguồn được nêu trong ngoặc để có thể dẫn xuất lại.*

### 14.1 Cái gì tồn tại

Trước đợt này, câu đúng là *"chưa có code"*. Nó không còn đúng, và mọi cổng phụ thuộc vào nó đã được đo lại thay vì được giữ nguyên nhãn cũ.

| Thứ | Số lượng | Nguồn (khóa của `numbers-….json`) |
| --- | --- | --- |
| Cây thư mục triển khai stack B | 7 (`server/`, `worker/`, `collector/`, `shared/`, `web/`, `tests/`, `probe/`) | Giai đoạn 0, `evidence/handoffs/P0-skeleton-handoff.md` |
| Revision Alembic | 7, một head (`0004_merge_phase1_heads`) | `migration_revisions` |
| File test Python | 10 | `test_files_count` |
| Hàm `test_*` | 215 | `test_defs` |
| File test đọc fixture qua loader | 8 | `test_files_using_the_fixture_loader` |
| Manifest `GENERATED_FROM.json` | 2 | `generated_from_manifests` |
| Lần chạy E1/E2 của card trên đĩa | 8 (đăng ký 4, thay thế 4) | `card_runs_on_disk_count` |
| Báo cáo audit trong repo | 13 | `audit_reports_in_repo_count` |

**Giả định "fixture là dữ liệu test" của bản kế hoạch nay được XÁC NHẬN, không phải bác bỏ.** Loader nằm ở `tests/conftest.py` (`load_fixture` / `load_directory` / fixture pytest `fixture_loader`), đọc thẳng `acceptance/fixtures/<dir>/<name>.json` và **không** có tập dữ liệu test thứ hai ở đâu cả. 8 trong 10 file test dùng nó: `tests/contract/test_auth_scheme_matrix.py`, `tests/contract/test_ingest_batch_schema.py`, `tests/contract/test_ingest_idempotency.py`, `tests/integration/test_denied_edges.py`, `tests/integration/test_disk_full_no_ack.py`, `tests/integration/test_identity_merge_audit.py`, `tests/integration/test_ingest_ack_lost.py`, `tests/integration/test_readiness_independent_channel.py`. Đó cũng là câu trả lời cho `CR-P0-05` (loader chưa có cửa hồi quy): nay nó có — nếu loader hồi quy, tám file này vỡ. Điều loader vẫn **chưa** có là test của riêng nó cho các nhánh âm (`FixtureBlockMissing`, tên fixture không phân giải được); PC09 không được phép ghi vào `tests/`, nên điều đó được ghi lại chứ không được lặng lẽ coi là xong.

### 14.2 A3 đã xác minh cái gì

Hai lượt audit độc lập, cả hai nay nằm trong repo nguyên văn từng byte (`evidence/audits/A3-R1-report.md`, `evidence/audits/A3-R2-report.md`, cmp-verified):

- **`A3-R1`** trên `FC-P1` epoch 1: **FAIL tổng thể** trên hai finding HIGH (`F-A3R1-01` hai định nghĩa `owner`, `F-A3R1-02` cột credential không được hợp đồng khai). Ba card PASS, `TC-owner-auth-session` FAIL.
- **`A3-R2`** trên `FC-P1` epoch 2 sau đợt sửa: **PASS** cho phạm vi review. Bảng xác minh §2: **13 VERIFIED · 1 PARTIAL (`F-A3R1-11`) · 1 DEFERRED (`F-A3R1-03`, chuyển cho gói này) · 0 NOT_VERIFIED**. Bốn finding mới, tất cả nằm trong **bằng chứng của bản sửa**, không trong hành vi đã sửa: MEDIUM 3 · LOW 1 · HIGH 0.
- **`A3-R3`** trên `FC-P1` epoch 3: **PASS**. Cả bốn `F-A3R2-01..04` **VERIFIED** — `-02` bằng mutation harness của chính auditor, ba đột biến trên đúng các hàm test thật và cả ba bị bắt. `F-A3R1-03` (đăng ký bằng chứng) **đóng** bởi việc đăng ký của gói này. Một mục của PC09 **PARTIAL**: quy tắc `CR-P0-02` của `E0-12` nói nó canh `evidence/runs/**` nhưng vòng lặp chưa bao giờ đọc cây đó (`F-A3R3-01`). Ba finding mới: MEDIUM 2 · LOW 1 · HIGH 0, **cả ba nhắm vào bản ghi bằng chứng của PC09**, không vào bốn card.

**Ba finding của `A3-R3` là của tôi, và cả ba đã được sửa ở `PKT-PC09-P1-FIX1`** — nhưng bản sửa đó đến SAU báo cáo, nên nó `FIX_PROPOSED` chứ không `VERIFIED`, và người viết bản sửa không được tự xác minh nó (protocol §8). Tóm tắt: `F-A3R3-01` — `E0-12` nay thật sự đọc `evidence/runs/**` **và** `evidence/index.json` cho quy tắc claim, và `evidence/manifest.schema.json` nay chặn một bản ghi `INDEPENDENT_AUDIT` ở `IMPLEMENTATION_VERIFIED`; 12/12 đột biến hành xử đúng đặc tả. `F-A3R3-02` — sáu bản ghi `EV-A3` từng mang một khối `execution` đọc như nhật ký chạy của auditor (một chuỗi lệnh `uv sync … && pytest && mypy` với `exit_code: 0` trong bốn giây, ký tên `auditor-A3`); nay chúng khai `producer_principal: worker-W6n (transcription of auditor-A3)`, `execution.kind: manual_procedure` mô tả **việc chép**, `exit_code: null`, và lệnh cùng số đo của chính auditor được **TRÍCH** trong `oracle.observed.auditor_reported` kèm mục báo cáo. `F-A3R3-03` — hai con số của epoch 2 nay được cập nhật (§14.4).

Điều đáng ghi rõ: `A3-R2` **tự tái dẫn xuất** những khẳng định chịu lực thay vì tin bộ test — dựng DB dưới **bốn thứ tự duyệt** Alembic và băm `sqlite_master` (một chữ ký cho cả bốn), quét `PRAGMA table_xinfo` toàn bộ 16 bảng nghiệp vụ đối chiếu `entities.yaml` (**0 khác biệt cột ở cả hai chiều**), và dựng một `Engine` cùng `AuthService` **mới toanh** để chứng minh lockout sống qua restart.

### 14.3 Nhãn theo từng card — đúng như `A3-R2` §5.1 phán

Nhãn dưới đây **không phải** lời tự khai của gói viết code. Bốn manifest `SELF_VALIDATION` của bốn Worker đều **cố ý bỏ trống hoặc để `DRAFT_FOR_REVIEW`** ở `claim.supports_label`, vì `evidence/manifest.schema.json` chặn một bản ghi tự kiểm ở `CONTRACT_READY` — và cái chặn đó **đúng**. Nhãn `IMPLEMENTATION_VERIFIED` chỉ tồn tại ở các bản ghi `INDEPENDENT_AUDIT` (`EV-A3-01`…`EV-A3-06` trong `evidence/index.json`), và mỗi bản ghi đó khai thẳng rằng nó là một **bản chép** của báo cáo, ghim sha256 của báo cáo, và nói rằng nếu bản chép lệch với báo cáo thì báo cáo thắng. Đó là câu trả lời cho `CR-TC-ingest-06` và `CR-TC-storage-02`.

| Card | Module | Verdict `A3-R2` | Nhãn được ĐĂNG KÝ | Phạm vi nhãn phủ | Nhãn KHÔNG phủ |
| --- | --- | --- | --- | --- | --- |
| `TC-ingest-idempotent-ack-lost` | `MOD-ingest-service` | **PASS** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | chỉ **bốn operation card SẢN XUẤT** (`ingest.submit_batch`, `ingest.commit_checkpoint`, `ingest.get_receipt`, `ingest.get_checkpoint`) trên SQLite | `PARTIAL` §4 của chính card (năm operation tiêu thụ không được gọi, `works_linked` luôn 0); `CR-TC-ingest-05` còn mở; hai lần submit **đồng thời** cùng một `idempotency_key` là **không thiết lập** — A3 không chạy race test nào |
| `TC-canonical-identity-merge` | `MOD-identity-service` | **PASS** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | `TXN-identity-merge` là một commit, `_require_edge` thật sự ném `FORBIDDEN_EDGE`, trần 100 000 hàng được ép, năm bảng move-set khớp `entities.yaml` từng trường | hai `xfail(strict=True)`: `CR-TC-IDENTITY-02` (`moved_counts.first_announced` null vs số) và `CR-TC-IDENTITY-03` (`published_report_item` không đo được — bảng `report` chưa tồn tại); `F-A3R1-04` đính kèm |
| `TC-owner-auth-session` | `MOD-auth-service` | **PASS (lượt trước FAIL)** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | Argon2id theo `secrets.md`, cookie flag đúng, CSRF so bằng `compare_digest`, session token băm, tài khoản không tồn tại trả lời trong thời gian bằng nhau, lockout **bền qua restart** (auditor tự dựng harness restart), 36 cạnh được phân hoạch 12/10/14 | **nhãn nằm trên `AMD-ENT-owner-01`, vẫn `PROVISIONAL`** — Owner chưa phát biểu; nếu Owner phản đối thì schema của card này và verdict này cùng mở lại. 14 cạnh `CAPABILITY_DENIED` là `NOT_TESTABLE_AT_THIS_LAYER`, không tính là pass. `CR-TC-AUTH-01` còn mở |
| `TC-storage-write-blocked-readiness` | `MOD-data-store + MOD-health-service` | **PASS** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | máy trạng thái storage, guard từ chối mutation trước khi mở transaction, và kênh health **độc lập DB** (HC-01..HC-04) | **đã thu hẹp**: loại trừ bước chuyển `write_blocked → healthy` — không có bảng probe nào tồn tại (`CR-TC-storage-04`, `F-A3R1-11` PARTIAL ở cả hai lượt). Không chứng minh SQLite an toàn trên ổ đầy THẬT; không có drill restore thật |
| *(skeleton Giai đoạn 0)* | — | **PASS** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | bố cục bảy cây, lockfile, CI, hai bộ sinh có cửa diff-on-regenerate, `verify_cards.py` 13/13 với self-test âm 14/14 | **không nghiệp vụ sản phẩm nào** |

**Verdict tổng của `A3-R2` là PASS cho PHẠM VI REVIEW — không phải cho sản phẩm.** Bốn card M1 cộng skeleton. `G6` (integration/live) `NOT_MET`, `G7` (product acceptance) chưa áp dụng được.

### 14.4 Số test — đếm, không ước lượng

Bộ test đầy đủ tại **epoch 3**, trích từ `A3-R3` §1: **305 passed / 4 xfailed / 0 failed** (45,5 s), một head Alembic (`0004_merge_phase1_heads`), cổng schema-vs-entities **10 test**. Hai con số này thay `303 / 4 / 0` và `8/8` của epoch 2 (`F-A3R3-03`): +2 test là đúng hai test mà đợt sửa `F-A3R2-02` thêm vào cổng schema. Bốn `xfail` đều `strict=True` và mỗi cái ghi một drift hợp đồng/fixture đã khai hoặc một phụ thuộc vào card ngoài M1 — `CR-TC-AUTH-01`, `CR-TC-IDENTITY-02`, `CR-TC-IDENTITY-03`, và một phụ thuộc `TC-storage-…`. **Không test nào bị skip ở đâu cả** (`A3-R1` §1 kiểm điều này độc lập). Mỗi literal bị `xfail` đều có một assertion **đang pass** cho phần không tranh chấp: `xfail` ở đây thu hẹp phạm vi, không làm im lặng một scenario.

Trên đĩa hôm nay: **10** file test, **215** hàm `test_*` (khóa `test_files_count`, `test_defs`). Con số này **lớn hơn** 303 vì nhiều hàm được parametrize thành nhiều case, và **không** được dùng thay cho số test đã chạy.

### 14.5 Cái gì vẫn `NOT_RUN` — và cái gì chỉ chạy một nửa

| Phép đo | Giá trị | Khóa |
| --- | --- | --- |
| Scenario tổng | 56 | `scenarios` |
| `NOT_RUN` | **52** | `scenario_status` |
| `PASS (E1)` | **2** (`SC29`, `SC31`) | `scenario_status` |
| `PASS (E2)` | **2** (`SC21`, `SC26`) | `scenario_status` |
| Scenario yêu cầu cấp ≤ E2 | 48 | `scenarios_le_e2` |
| …trong đó đã PASS | **4 / 48** | `scenarios_le_e2_passed` |
| Scenario cấp E3 đã có probe | **0 / 5** | `precode/gates.yaml` G6-X2 |
| Drill restore thật | **0 / 2** | `precode/gates.yaml` G6-X3 |
| Scenario có bằng chứng MỘT PHẦN (vẫn `NOT_RUN`) | **12** (`SC03`, `SC07`, `SC09`, `SC23`, `SC30`, `SC36`, `SC40`, `SC41`, `SC42`, `SC49`, `SC50`, `SC51`) | `scenarios_with_partial_evidence` |

**Quy tắc chuyển nhãn, viết ra để có thể phản bác.** Một scenario chỉ rời `NOT_RUN` khi cả ba điều kiện đồng thời đúng: (1) `evidence_level_required` của nó là E1 hoặc E2; (2) một bộ test Giai đoạn 1 chạy **toàn bộ** oracle của nó trong phạm vi một card, không phải một mảnh; (3) `A3` đã chạy lại chính file test đó từ bytes đã đóng băng. `E0-16` **ép** quy tắc này: một status `PASS (…)` không có `status_evidence_refs` phân giải được trên đĩa, không có `status_scope_vi`, hoặc khai một cấp thấp hơn cấp scenario đòi, đều FAIL; `PASS (E3)`/`PASS (E4)` bị từ chối thẳng.

**Vì sao 12 scenario ở lại `NOT_RUN` dù có code chạm tới.** Mỗi dòng mang `partial_evidence_vi` nói phần nào đã chạy và phần nào không đo được. Ba lý do lặp lại: (a) oracle đếm một bảng thuộc card chưa tồn tại (`report`, `report_item`, `tag`, `assignment_lease`, `analysis` ở nghĩa nghiệp vụ) — `SC07`, `SC09`, `SC23`, `SC30`, `SC40`, `SC41`, `SC42`; (b) oracle đòi cả ba cơ chế ép buộc trong khi chỉ hai chạm được ở tầng HTTP/service — `SC49`, 22/36 cạnh; (c) oracle đòi một bước con người hoặc một dịch vụ thật — `SC42` mệnh đề 7, `SC51` bước 5, `SC36` nhánh hồi phục. Một phần **không** phải một PASS; nhưng điều đã đo cũng không được phép biến mất chỉ vì nó chưa đủ.

`acceptance/traceability.csv` mang cột mới `executed_evidence` nói cùng điều đó ở mức yêu cầu: nó **không** đổi `coverage_status`, vì độ phủ hợp đồng và việc đã chạy là hai phép đo khác nhau và trộn chúng là cách nhanh nhất để một baseline nghe có vẻ đã được kiểm.

### 14.6 Manifest bằng chứng — và một finding vẫn đang mở về chính chúng

`F-A3R2-03` nói ba trong bốn card không phát lại manifest sau đợt sửa, và một manifest (`TC-storage-…-E1-20260907T100943Z.json`) ghim **bốn file đã SẢN XUẤT mà bytes không còn khớp**. Gói này không tin lời ai: nó băm lại **từng cặp `{path, sha256}`** trong mọi manifest trên đĩa và phân loại làm hai lớp — pin **bytes-đã-sản-xuất** (`artifacts[]`: lệch nghĩa là manifest chứng nhận một cây không còn tồn tại) và pin **bytes-đã-đọc** (`baseline.contract_hashes`: lệch nghĩa là corpus đã đổi SAU lần chạy).

| Card | Manifest được ĐĂNG KÝ | pin sản-xuất lệch | pin đã-đọc lệch |
| --- | --- | --- | --- |
| `TC-canonical-identity-merge` | `TC-canonical-identity-merge-E1-20260907T111124Z.json` | **0** | 4 |
| `TC-ingest-idempotent-ack-lost` | `TC-ingest-idempotent-ack-lost-E1-20260907T113827Z.json` | **0** | 0 |
| `TC-owner-auth-session` | `TC-owner-auth-session-E1-20260907T114030Z.json` | **0** | 2 |
| `TC-storage-write-blocked-readiness` | `TC-storage-write-blocked-readiness-E1-20260907T113817Z.json` | **0** | 0 |

**Bốn manifest được đăng ký đều có 0 pin sản-xuất lệch.** Bốn manifest cũ hơn KHÔNG được đăng ký làm record; chúng được liệt kê ở khóa `superseded_card_runs` của `evidence/index.json` kèm đích danh pin nào lệch, để bằng chứng bị thay thế không biến mất mà cũng không chống đỡ nhãn nào.

**Pin đã-đọc còn lệch, và phần lớn là do chính gói này.** 4 đường dẫn mà manifest được đăng ký ghim nay khác bytes trên đĩa. Nguyên nhân được **truy**, không được đoán:

| Đường dẫn | Manifest bị ảnh hưởng | Ai đổi nó, và đổi cái gì |
| --- | --- | --- |
| `acceptance/scenarios.yaml` | `TC-canonical-identity-merge`, `TC-owner-auth-session` | **chính `PKT-PC09-P1`** — ghi `status`, `status_evidence_refs`, `status_scope_vi` cho bốn scenario và `partial_evidence_vi` cho 12 scenario khác |
| `contracts/data/entities.yaml` | `TC-canonical-identity-merge` | `PKT-PC02-FIX13` sửa **văn xuôi** trong khối `amendments[0]` cho `F-A3R2-01`/`-04`; `version: 0.2.0` giữ nguyên và **không trường nào của `ENT-owner` bị đụng** |
| `evidence/manifest.schema.json` | `TC-canonical-identity-merge`, `TC-owner-auth-session` | **chính `PKT-PC09-P1`** — mở rộng mẫu `unresolved_issue_refs`, vốn chỉ nhận `F-A1R<n>` nên từ chối một bản ghi trung thực trích `F-A3R2-03` |
| `precode/decision-register.md` | `TC-canonical-identity-merge` | cùng đợt `PKT-PC02-FIX13` |

Không thay đổi nào trong bảng trên chạm một **trường entity** hay một **dòng code**, nên không kết luận nào của bốn card bị lật. Nhưng theo `INV-06`/`INV-08` bản ghi vẫn phải **khai** điều này thay vì để người đọc tự băm lại, và nó khai — trong `limitations.not_checked_vi` của chính bản ghi, với đích danh từng pin.

Điều đáng nói hơn con số: **hai trong bốn nguyên nhân là gói này**, và đó không phải tai nạn mà là hệ quả của thứ tự công việc. Card ghim `acceptance/scenarios.yaml` theo hash toàn file; PC09 **buộc phải** sửa đúng file đó để ghi status scenario; nên một lần đóng gói của PC09 sẽ **luôn** làm manifest của card `STALE` ở lớp bytes-đã-đọc, mãi mãi, kể cả khi không có gì thực chất đổi. `CR-PC09-16` (§8.1) ghi lỗi thiết kế đó và nêu hai lối thoát, không tự chọn một.

### 14.7 CR và finding của Giai đoạn 0/1

Chi tiết đầy đủ ở **§8.2** (bảng sinh bằng máy, nay phủ cả ba dạng id). Tóm tắt:

- **41 CR mới** do Giai đoạn 0/1 phát ra: 6 dạng `CR-P0-nn`, 35 dạng `CR-TC-<CARD>-nn`.
- **12 trong tổng 172 CR chạm một file `CONTRACT_READY`** và cần re-freeze + A2 xác minh khi được áp dụng: `CR-TC-AUTH-01`, `CR-TC-AUTH-04`, `CR-TC-IDENTITY-02`, `CR-TC-IDENTITY-05`, `CR-TC-IDENTITY-06`, `CR-TC-IDENTITY-07`, `CR-TC-IDENTITY-08`, `CR-TC-IDENTITY-10`, `CR-TC-ingest-02`, `CR-TC-ingest-03`, `CR-TC-ingest-05`, `CR-TC-storage-04`.
- **Bốn ruling của Coordinator đã có** và được ghi trong bảng: trần manifest schema là ĐÚNG (nhãn `IMPLEMENTATION_VERIFIED` chỉ lên được qua bản ghi `INDEPENDENT_AUDIT`); bảng probe storage vắng mặt → CR cho PC02/PC03; bộ đếm lockout trong tiến trình → CR cho PC02 (entity) kèm giới hạn "restart xóa sạch" được khai — nay đã đóng bởi `AMD-ENT-owner-01`; ép FK xuyên card → CR cho PC02/PC10 (card dựng lại có phối hợp).
- **`F-A3R2-01…04` nay đều `VERIFIED`** bởi `A3-R3` §2 — kể cả `-02`, cửa `test_schema_matches_entities.py`, mà auditor tự mutation-test. Chúng **không** được đóng ở đây: PC09 không có quyền disposition (protocol §8); bảng §8.2 chép nguyên trạng thái xác minh của báo cáo.
- **`F-A3R3-01…03` đăng ký `FIX_PROPOSED`** — cả ba là của PC09, cả ba đã được sửa ở `PKT-PC09-P1-FIX1`, và **không cái nào được tự xác minh**.

### 14.8 Điều mục này KHÔNG nói

- **Không** nói baseline hợp đồng đã được kiểm bằng code. `E0` vẫn là lint tài liệu; bốn card chỉ chạm bốn module trong 25.
- **Không** nói `G5` đã đạt. Bốn điều kiện ra của `G5` nay `met: true`, nhưng điều kiện **vào** (G4) chưa đạt và `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED` — cổng là `PARTIALLY_MET`.
- **Không** nói `AMD-ENT-owner-01` đã được phê chuẩn. Nó `PROVISIONAL`; Owner chưa phát biểu; và nhãn của `TC-owner-auth-session` nằm trên nó.
- **Không** nói bất kỳ dịch vụ ngoài nào hoạt động. 0 lời gọi live ở cả hai lượt A3.
- **Không** phải một security assessment: A3 đọc code auth và đối chiếu `secrets.md`, nhưng không tấn công, không fuzzing, không quét lỗ hổng phụ thuộc ngoài những gì `npm ci` tự báo.
- **Không** nói ba bản sửa của `PKT-PC09-P1-FIX1` là đúng. Chúng có 12/12 mutation của chính tôi đứng sau, chạy bằng công cụ tôi vừa sửa. Đó là `SELF_VALIDATION`, và `F-A3R3-01…03` ở lại `FIX_PROPOSED` cho tới khi một auditor độc lập chạy lượt sau.

---

## 15. Giai đoạn 2 — collector, research connector, và một bộ công cụ probe chưa chạy

*Mục này được thêm bởi `PKT-PC09-P2`. Cùng kỷ luật §14: con số do `derive_numbers.py` sinh và ghi kèm khóa; con số TRÍCH từ báo cáo audit được ghi rõ là trích, kèm mục.*

### 15.1 Cái gì tồn tại thêm

| Phép đo | Sau Giai đoạn 1 | Sau Giai đoạn 2 | Khóa |
| --- | --- | --- | --- |
| File test Python | 10 | **18** | `test_files_count` |
| Hàm `test_*` | 215 | **443** | `test_defs` |
| Revision Alembic | 7 | **8**, một head (`0005_tc_research_connector_metadata`) | `migration_revisions` |
| Task card | 18 | **19** | `cards` |
| Lần chạy card trên đĩa | 8 | **13** (đăng ký 7, thay thế 6) | `card_runs_on_disk_count` |
| Module có code | 4 | **7** | `precode/gates.yaml` G6 |
| Báo cáo audit trong repo | 13 | **14** | `audit_reports_in_repo_count` |

**Số trích từ `A3-P2-R1` §1** (auditor tự chạy, không phải tôi; đây là số của **epoch P2d**, đã bị thay lần lượt bởi Giai đoạn 3/5 — xem §16.1): **582 passed / 4 xfailed / 0 failed** (49,4 s) — tức **586 collected**, đúng như handoff viết; `ruff` sạch; `ruff format` **88 file**; `mypy --strict` **30 file** sạch; `e0_check.py` **25/25, 0 vi phạm**; `verify_cards.py` **13/13 check trên 19 card, 3 571 assertion, 0 vi phạm**, epoch `PC10-PIN-P2d-20260907`; `alembic heads` một head. **Không test nào bị skip ở đâu cả.**

Auditor cũng sửa một chỗ paraphrase của Coordinator ("~586 passed") thành con số đúng (582 passed + 4 xfailed = 586 collected). Ghi lại vì đó chính là lớp lỗi `F-A2R1-02`: một con số đi qua tay người rồi lệch.

### 15.2 Hai kết quả không thể có được bằng cách đọc

`A3-P2-R1` §2 và §3 là phần đáng đọc nhất của lượt này, vì cả hai đều là **phép đo**, không phải review văn bản:

- **Ranh giới mạng.** Auditor chạy **toàn bộ** bộ test với **mọi socket và mọi truy vấn DNS bị chặn**, và nó xanh. Đó là bằng chứng rằng không đường chạy nào của Giai đoạn 2 chạm mạng — khác hẳn với việc đọc `network_egress` trong `modules.yaml` và tin nó.
- **Bốn dữ kiện `REQ-A6`.** Auditor **tự tải** tài liệu chính thức của arXiv và OpenAlex (bốn GET, đúng trong allowlist đã cấp) và tái lập cả bốn dữ kiện **nguyên văn**, thay vì chấp nhận bảng của Worker.

### 15.3 Nhãn theo từng card — đúng như `A3-P2-R1` §4/§7

| Card | Verdict | Nhãn được ĐĂNG KÝ | Phạm vi nhãn phủ | Nhãn KHÔNG phủ |
| --- | --- | --- | --- | --- |
| `TC-collector-checkpoint-resume` | **PASS** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | **phía collector**, cấp E1/E2: claim/heartbeat mang lease epoch, gom lô với `payload_hash`, trả receipt trước mọi retry, đề xuất checkpoint chỉ cho dữ liệu **đã ACK**, resume từ checkpoint của **server**, không tự retry sau challenge | **không khẳng định gì về X thật**; `CR-TC-COLLECTOR-02` mở (`F-A3-P2-02`); hai độ lệch write-set được khai trong handoff §6 |
| `TC-research-connector-metadata` | **PASS** | `IMPLEMENTATION_VERIFIED` (có phạm vi) | **E1 với response đã ghi sẵn**; năm fixture đều chạy; migration `0005` là con tuyến tính sạch của `0004`; năm mệnh đề §9/§10 viết lại đều được kiểm bằng **hành vi** | **`MOD-research-connector` KHÔNG `CONTRACT_READY`** — không hợp đồng nào nêu host/endpoint (`SG-DOC`), E3 chưa chạy (`SG-LIVE`); xóa `PLACEHOLDER_KC` **không** tự cấp `CONTRACT_READY`; dữ kiện `REQ-A6` có hạn (đọc 2026-09-07, không tự gia hạn) |
| `TC-x-feasibility-probe` | **tooling được chấp nhận** | `DRAFT_FOR_REVIEW` — **không** nhãn nào cao hơn | bộ công cụ probe và runbook tồn tại, lint/type sạch, 156 test ngoại tuyến của chính công cụ pass | **KHÔNG `LIVE_FEASIBILITY_VERIFIED` và không được suy ra một kết luận feasibility nào** — nguyên văn auditor. `runs.jsonl` **vắng mặt**, và sự vắng mặt đó là ĐÚNG |

**Card probe cố ý KHÔNG có bản ghi `INDEPENDENT_AUDIT` riêng.** Auditor chấp nhận *bộ công cụ* và nói thẳng rằng không tồn tại khẳng định feasibility nào "và không được suy ra một cái nào". Đúc một bản ghi audit cho card đó sẽ tạo ra chính suy luận vừa bị cấm; nên manifest `SELF_VALIDATION` của nó (`result: NOT_RUN`, `DRAFT_FOR_REVIEW`) được đăng ký một mình, và câu chữ của báo cáo được trích trong bản ghi tổng `EV-A3-11-p2-overall`.

**Một tiết lộ của auditor đáng đọc nguyên văn.** Khi kiểm cổng probe bằng cách chạy `run_probe` trên ba config nháp, cấu hình thứ ba (bốn xác nhận **kèm** `evidence_ref`) đi tới tận `launch_persistent_context` và chỉ dừng vì đường dẫn profile mẫu không ghi được. Không trình duyệt nào khởi động, không mạng, không gì được tạo. Auditor báo nó vì *"một auditor nên nói khi một phép kiểm đi cách ranh giới nó đang thử một bước"* — và vì nó cho thấy **cổng của Owner là thứ DUY NHẤT** giữa một config đã thỏa và một trình duyệt chạy thật. Đó là thiết kế có chủ ý (Owner là người chạy), không phải một lỗ hổng.

### 15.4 Cổng — không cổng nào chuyển, và vì sao đó là câu trả lời đúng

| Cổng | Trước | Sau | Vì sao |
| --- | --- | --- | --- |
| `G5` | `PARTIALLY_MET` | `PARTIALLY_MET` | `G5-X1..X4` đã đủ từ Giai đoạn 0. Cái chặn là điều kiện **VÀO** (G4) và `REQ-OQ03` — không phải thứ thêm code giải được |
| `SP1` | `NOT_MET` | `NOT_MET` | **Cổng nay mở về mặt HÀNH CHÍNH** (`OD-20260907-04` chấp nhận ngân sách/điều kiện dừng/go-no-go/rủi ro `REQ-A7`; D09 đã có từ `OD-20260907-01`). `SP1-X2` đo **đợt chạy**, và số đợt là **0/5–10** |
| `G6` | `NOT_MET` | `NOT_MET` | **4/48** · 0/5 · 0/2. Không nhãn nào đổi — nhưng mẫu số được sửa (51 → 48) và Giai đoạn 2 **đã được đánh giá** ở `PKT-PC09-P2-FIX1` thay vì để trống |

**Đây là chỗ dễ đọc sai nhất của cả Giai đoạn 2, nên nó được viết ra hai lần** (ở đây và trong `gates.yaml` `SP1.administrative_vs_operational_note_vi`): *cổng mở* và *đợt chạy* là hai chuyện. Biên bản của Owner nói thẳng — probe chỉ chạy trên máy của Owner, sau khi Owner tự cài Playwright, tự đăng nhập tay, tự điền `probe-config.json` và tự ký bốn `owner_confirmations`; **không Worker nào được chạy nó**. Vì vậy `REQ-AC16`, `REQ-A1`, `REQ-A7` **không đổi trạng thái**, và mọi con số probe vẫn `NOT_RUN`.

`SP1-X3` ("không cơ chế né tránh nào được thêm") là điều kiện DUY NHẤT mà Giai đoạn 2 làm **mạnh thêm**: trước đây nó đạt "ở mức hợp đồng — chưa có code nên chưa có gì để vi phạm"; nay **có** code để vi phạm, và một auditor độc lập đã đi tìm và không thấy.

### 15.5 Scenario — 13 dòng được đánh giá, 0 dòng chuyển nhãn (`CR-PC09-20` đóng)

Ba card Giai đoạn 2 khai chạm 13 scenario: `SC01`, `SC03`, `SC04`, `SC07`, `SC11`, `SC20`,
`SC21`, `SC23`, `SC29`, `SC30`, `SC39`, `SC49`, `SC50`. `PKT-PC09-P2-FIX1` xét **từng dòng**
theo đúng quy tắc ba điều kiện ở §14.5, và kết quả là:

| SC | Cấp đòi | Trạng thái sau khi xét | Vì sao |
| --- | --- | --- | --- |
| `SC01` | E2 | `NOT_RUN` | `no_work` và "đăng ký không cấp lease" đã chạy phía collector; `run` và `assignment_lease` **chưa tồn tại** |
| `SC03` | E2 | `NOT_RUN` | báo cáo dừng-vì-giới-hạn và resume-từ-checkpoint-server đã chạy; bộ ba `(status, outcome, stop_reason)` là trạng thái server, `run` chưa tồn tại |
| `SC04` | E2 | `NOT_RUN` | "không tự retry sau challenge" và `STALE_LEASE` đã chạy; `COUNT(outbox_intent …) = 1` không đo được — bảng chưa tồn tại |
| `SC07` | E1 | `NOT_RUN` | sáu cách viết ⇒ **một** lời gọi metadata đã chạy (mới ở Giai đoạn 2); `COUNT(report_item) = 1` vẫn không đo được |
| `SC11` | **E4** | `NOT_RUN` | cấp đòi là E4; điều kiện thứ nhất của §14.5 chặn nó bất kể code |
| `SC20` | E2 | `NOT_RUN` | `STALE_LEASE` + heartbeat epoch cũ đã chạy phía client; bất biến `COUNT(assignment_lease WHERE state='held') = 1` không đo được |
| `SC21` | E2 | **`PASS (E2)`** *(giữ nguyên)* | đã PASS từ Giai đoạn 1; Giai đoạn 2 **củng cố** bằng vế đối diện: collector tra receipt **trước** khi gửi lại |
| `SC23` | E1 | `NOT_RUN` | không đổi; selection bỏ qua quarantine và đếm theo AMD-B15 thuộc card báo cáo |
| `SC29` | E1 | **`PASS (E1)`** *(giữ nguyên)* | đã PASS từ Giai đoạn 1; Giai đoạn 2 **củng cố** bằng vế mạnh hơn: không định danh ⇒ **0 lời gọi mạng** |
| `SC30` | E1 | `NOT_RUN` | v1/v2 ⇒ một work nay đúng ở cả tầng metadata; generation phân tích vẫn thuộc card chưa chạy |
| `SC39` | E2 | `NOT_RUN` | **dòng gần nhất** — xem bên dưới |
| `SC49` | E2 | `NOT_RUN` | phân hoạch 12/10/14 cộng hai cạnh module nghiên cứu; oracle vẫn đòi **cả ba** cơ chế ép buộc |
| `SC50` | E2 | `NOT_RUN` | thêm chặng thu thập và làm giàu, nhưng không chặng nào được nối vào một đường chạy duy nhất |

**Không dòng nào chuyển nhãn, và đó là kết quả chứ không phải sự thiếu sót.** Lý do lặp lại 11
lần và nó là **cấu trúc**: oracle của các dòng này đếm trạng thái bền trong những bảng mà chưa
card nào tạo — `run`, `assignment_lease`, `outbox_intent`, `report`/`report_item`. Code Giai
đoạn 2 là code **phía client**: nó chứng minh collector và connector cư xử đúng, không chứng
minh trạng thái server sau đó. Một scenario đo hệ thống, không đo một nửa của nó.

**`SC39` đáng đọc riêng, vì nó dừng lại ở một vế.** Mọi thứ đo được đã chạy thật: chặn được áp
lại **ở từng hop** (redirect theo tay), DNS rebinding bị chặn theo **địa chỉ** chứ không theo
tên, một câu trả lời DNS pha trộn bị từ chối **cả cụm** thay vì lọc, bảy dải mà
`internet-boundary.md` nêu tên đều bị chặn, credential trong URL bị từ chối, vượt trần redirect
bị từ chối, và trên fixture `recovery/g-ssrf-redirect-private` số kết nối tới loopback và tới
dải riêng đều bằng **0**, hop bị chặn đúng ở bước **3**. Vế duy nhất không đo được:
`COUNT(work_label)` và abstract đã có không đổi sau khi bị chặn. Đường chạy bị chặn không ghi
gì — fixture nói vậy bằng **văn xuôi** (`work_state_vi`) — nhưng không assertion nào đếm hàng,
và trong test đó `ctx.repository` là `None`. Tôi giữ `NOT_RUN`: **"không đo được" khác "đã
sạch"**, và đó là cùng một tiêu chuẩn đã giữ `SC36` và `SC49` ở `NOT_RUN` từ Giai đoạn 1.

**Một con số sai đã được sửa cùng lúc.** `G6-X1` từng đọc **4/51**; mẫu số đúng là **48**
(56 scenario − 5 dòng E3 − 3 dòng E4). Sai số do `PKT-PC09-P1` viết ra, và nó làm cổng trông
xa đích hơn thực tế ba dòng — lệch theo hướng bi quan, nhưng một con số sai theo hướng nào
cũng là con số sai. Nay: **4/48 PASS · 44 `NOT_RUN`, trong đó 17 dòng mang
`partial_evidence_vi`** (tăng từ 12 — mười một ghi chú mới viết ở lượt này).

`acceptance/traceability.csv` **không được ghi** ở cả hai lượt Giai đoạn 2: cột
`executed_evidence` được dẫn xuất từ `scenarios.yaml`, và vì không nhãn nào đổi, một lần chạy
dẫn xuất trên trạng thái đĩa hiện tại cho **0/246 dòng đổi**. Ba dòng mà `W3n` sửa được giữ
nguyên từng byte.

### 15.6 Finding và CR

`A3-P2-R1` §6: **HIGH 0 · MEDIUM 0 · LOW 2**. Coordinator đã phán cả hai là **PARKED** — được khai, có lý do, không chặn, và không mở một vòng sửa nữa:

- **`F-A3-P2-01`** (LOW) — hai tham chiếu chéo *"REQ-A6 chưa giải"* còn sót trong `evidence/handoffs/TC-research-connector-metadata-handoff.md` và một ghi chú trên dòng `REQ-P0-04` của `requirements.csv`. **Chỉ là văn bản**: trạng thái thực của `REQ-A6` ở `decision-register.md` §8.13.2 và `retry-policy.yaml` 0.8.0 mới là thẩm quyền, và nó không bị ảnh hưởng. Hoãn sang vòng hợp đồng sau thay vì mở lại một freeze đã đóng cho một dòng chữ.
- **`F-A3-P2-02`** (LOW) — `RecordedSource` (một test double) ship trong module sản xuất `collector/app/reader.py`: **được khai, có lý do, và trơ** (không đường chạy runtime nào chạm tới nó ngoài test). PARKED thành **`CR-TC-COLLECTOR-02`** cho một đợt dọn sau.

**`F-A3R4-01` (LOW, từ lượt trước) ĐÃ ĐƯỢC SỬA ở lượt này** — nó là của tôi. Note của `E0-12` khẳng định *"structured fields are still checked"*, đúng với `.yaml`/`.json` và **sai** với front matter của Markdown, mà không phép quét claim nào chạm tới. Nay `claim_fields()` đọc cả front matter, nên câu chữ đúng với **mọi** loại file vòng lặp đi qua; `checked` của `E0-12` đi **976 → 1 157**. Mutation-test **6/6** — bảng đầy đủ ở addendum `PKT-PC09-P2` của `evidence/handoffs/PC09-handoff.md`, **không** ở `evidence/tools/README.md`: file đó nằm ngoài write set của gói này, nên §5k của nó vẫn mô tả tầm với **cũ** của `E0-12` và nay đã lạc hậu theo hướng khiêm tốn hơn thực tế (`CR-PC09-21`). Nó ở `FIX_PROPOSED`, không `VERIFIED`: bản sửa đến sau báo cáo và tôi không được tự xác minh nó.

Ba CR mới của gói này, tất cả đều là **giới hạn của chính tôi**, không phải của người khác:

| CR | Nội dung |
| --- | --- |
| `CR-PC09-18` | `evidence/audits/A3-P2-R1-report.md` **chưa nằm trong repo** khi gói này chạy; `evidence/audits/` ngoài write set của `PKT-PC09-P2`. Bản ghi `EV-A3-11-p2-overall` vì vậy **không ghim được sha256** của báo cáo nó chép, nên việc đối chiếu hiện **phụ thuộc vào lời tôi** — đúng thứ mọi bản ghi A3 khác tránh được |
| `CR-PC09-19` | **QUYẾT: giữ workaround đã khai.** `evidence/manifest.schema.json` KHÔNG nằm trong write set của `PKT-PC09-P2-FIX1` (lease chỉ thêm `acceptance/scenarios.yaml`), nên tôi không sửa mẫu id. Hai id `F-A3-P2-01`/`-02` tiếp tục được nêu nguyên văn trong `limitations.not_checked_vi` của `EV-A3-11-p2-overall` — chúng **có mặt và đọc được**, chỉ không nằm ở trường có cấu trúc. CR ở lại `OPEN` cho gói nào sở hữu schema |
| `CR-PC09-20` | **ĐÓNG** ở `PKT-PC09-P2-FIX1`: lease mở rộng thêm đúng 13 dòng của `scenarios.yaml`; cả 13 được xét từng dòng, **0 chuyển nhãn**, và mẫu số sai 51 → 48 được sửa cùng lúc. Xem §15.5 |
| `CR-PC09-21` | **ĐÓNG** ở `PKT-PC09-P3`: `evidence/tools/README.md` nằm trong write set lần này; §5m ghi bản sửa `F-A3R4-01` và §5n ghi bảng đột biến của `E0-20`. Trước đó: `evidence/tools/README.md` cũng KHÔNG nằm trong write set của `PKT-PC09-P2-FIX1`, nên §5k vẫn mô tả tầm với **cũ** của `E0-12`. Lệch theo hướng an toàn (tài liệu hứa ÍT hơn công cụ làm) nhưng vẫn là tài liệu không khớp công cụ — đúng lớp lỗi `F-A3R3-01`/`F-A3R4-01` đã bắt hai lần. Bảng đột biến đầy đủ nằm ở addendum `PKT-PC09-P2` của `evidence/handoffs/PC09-handoff.md` để bằng chứng không mất |

### 15.7 Điều mục này KHÔNG nói

- **Không** nói probe đã chạy, hay rằng X là khả thi. `SP1` `NOT_MET`, `runs.jsonl` vắng mặt, và auditor cấm suy ra kết luận feasibility.
- **Không** nói `MOD-research-connector` sẵn sàng: nó có code và **không** `CONTRACT_READY`.
- **Không** nói bốn dữ kiện `REQ-A6` đúng mãi mãi: chúng đúng với tài liệu đọc ngày 2026-09-07 và **không tự gia hạn**; hai dữ kiện `IDENT` là dữ kiện **âm** trên vài trang, yếu hơn dữ kiện dương — chính hợp đồng nói vậy.
- **Không** nói ba epoch `P2`, `P2b`, `P2c` đã được kiểm: bytes của chúng không còn ở đâu đọc được. Chỉ nhịp tổng `P1d → P2d` được kiểm.
- **Không** nói bản sửa `F-A3R4-01` của tôi là đúng: 6/6 mutation là `SELF_VALIDATION` chạy bằng công cụ tôi vừa sửa.
- **Không** có lời gọi API live nào. **E3 và E4 vẫn bằng 0 ở mọi nhóm scenario.**

---

## 16. Giai đoạn 3 (M3) + Giai đoạn 5 (M6 plain text) — sáu card, và lần đầu con số scenario nhúc nhích

*Thêm bởi `PKT-PC09-P3`. Con số do `derive_numbers.py` sinh và ghi kèm khóa; con số TRÍCH từ báo cáo audit được ghi rõ là trích, kèm mục.*

### 16.1 Cái gì tồn tại thêm

| Phép đo | Sau Giai đoạn 2 | Sau Giai đoạn 3/5 | Khóa |
| --- | --- | --- | --- |
| File test Python | 18 | **34** | `test_files_count` |
| Hàm `test_*` | 443 | **669** | `test_defs` |
| Revision Alembic | 8 | **14**, một head (`0009_tc_telegram_unknown_delivery`) | `migration_revisions` |
| Lần chạy card trên đĩa | 13 | **24** (đăng ký 13, thay thế 11) | `card_runs_on_disk_count` |
| Module có code | 7 | **13** | `precode/gates.yaml` G6 |
| Báo cáo audit trong repo | 13 | **17** | `audit_reports_in_repo_count` |

**Số trích từ `A3-P3-R2` §1** (số của **epoch P3b**, đã bị thay lần lượt bởi Giai đoạn 4/6 — xem §17.1; auditor tự chạy trên FC-P3 epoch 2, 545 entry, `manifest_sha256 41c47506…`): **827 passed / 9 xfailed / 0 failed**; `ruff check` sạch; **`ruff format --check` 134 file, rc=0**; `mypy --strict` 49 file sạch; `verify_cards.py` **13/13, 3 685 assertion**, epoch `PC10-PIN-P3b-20260908`; `e0_check.py` 25/25 (tại thời điểm đó — gói này thêm check thứ 26); một Alembic head.

### 16.2 Hai phán quyết phạm vi, cả hai được CHỨNG MINH chứ không được đọc

- **AI tắt mặc định — VERIFIED.** `contracts/ai/providers.yaml` đăng ký đúng hai adapter, cả hai `enabled: false`, và **không file nào trong repo** đặt `true`. Auditor không tin code: họ **tự nạp registry thật** và xác minh rằng việc từ chối xảy ra **trước khi chạm transport** (`A3-P3-R1` §2).
- **Telegram chỉ plain text — VERIFIED.** Auditor grep **toàn bộ diff**, không phải handoff, cho `parse_mode`, `reply_markup`, `inline_keyboard`, `MarkdownV2`, `callback_data`: mọi hit là tài liệu, phủ định, hoặc **kiểu** của update đến. Bề mặt không có chỗ để dùng sai vì tham số không tồn tại (`A3-P3-R1` §3). Ở lượt R2, auditor **chạy lại** phép kiểm này vì `ingress.py` đã đổi — và chạy lại toàn bộ suite dưới **chặn socket/DNS toàn phần**: rc=0, **không một lần thử mạng nào**.

### 16.3 Nhãn theo từng card — đúng như `A3-P3-R2` §4

| Card | Verdict | Nhãn được ĐĂNG KÝ | Nhãn KHÔNG phủ |
| --- | --- | --- | --- |
| `TC-analysis-adapter-validation` | **PASS**, điều kiện R1 **đã giải trừ** | `IMPLEMENTATION_VERIFIED` cho đường **API + trích JSON**; `CONTRACT_READY` cho CLI/ACP | `REQ-AC16` **BLOCKED**; cả hai adapter `enabled: false` vì **cô lập** (ISO-03/ISO-05), không phải vì điều khoản; E3 `NOT_RUN` |
| `TC-analysis-once-per-generation` | **PASS**, có phạm vi | `IMPLEMENTATION_VERIFIED` | nghĩa vụ `pending_item_ledger` (B04/B17) là `xfail(strict)` chờ card báo cáo |
| `TC-embedding-generation-switch` | **PASS**, có phạm vi | `IMPLEMENTATION_VERIFIED` | vế "chặn xảy ra trước publish" là `xfail(strict, run=True)` chờ card báo cáo; `REQ-OQ09` mở |
| `TC-telegram-linking-auth` | **PASS**, có phạm vi | `IMPLEMENTATION_VERIFIED` (plain text) | ba dữ kiện `delivery.md` §3.4 vẫn `KC`; `SC46` và mọi đường callback `NOT_RUN` |
| `TC-saved-snapshot` | **PASS**, có phạm vi | `IMPLEMENTATION_VERIFIED` | `data.delete_target` / `purge_all` / `save.export` **không hiện thực**; nhánh `report_ref` `NOT_RUN`; đồng thời chỉ ở mức hai luồng, không hai tiến trình |
| `TC-telegram-unknown-delivery` | **PASS**, có phạm vi | `IMPLEMENTATION_VERIFIED` | chạy trên **bảng `report` giả ba cột** và một bảng `run` giả — khai thẳng trong handoff §3; E3 `NOT_RUN` |

**Một giới hạn auditor tự nêu, đáng chép lại vì nó là mẫu mực.** Packet yêu cầu A3 xác nhận bốn file của `F-A3-P3-01` **chỉ** đổi định dạng. Auditor **từ chối tự khẳng định**: họ chưa bao giờ giữ bytes trước khi sửa (chúng là file untracked), nên không diff được và **không** khẳng định tương đương ngữ nghĩa trên thẩm quyền của mình. Cái họ **có** thiết lập: `mypy --strict` sạch, suite xanh ở số test lớn hơn hẳn, và 49 test khớp `sample_size: 49` của manifest phát lại. Mệnh đề "chỉ đổi định dạng" vì vậy được **chứng thực gián tiếp** và phần AST vẫn dựa vào lời khai của Worker — nói ra, thay vì để một PASS che nó.

### 16.4 Scenario — 25 dòng được xét, **6 chuyển nhãn**

Sáu card khai chạm 25 scenario. Cả 25 được xét từng dòng theo quy tắc ba điều kiện ở §14.5.

| Chuyển nhãn | Cấp | Vì sao chuyển được |
| --- | --- | --- |
| `SC48` | E1 | Schema Saved: hai ca dương sạch, năm ca âm lỗi tại đúng con trỏ, và mỗi khuyết tật bị chặn **lần thứ hai** ở tầng bảng. REQ-D20 được ép ở mức **schema**, không bằng lời khuyên |
| `SC12` | E2 | `content_hash` **tính lại từ bytes trên đĩa** ở bốn mốc (lưu → nguồn bị xóa → khởi động lại → `VACUUM INTO`), và khớp hai chuỗi hex tính **bên ngoài repo** |
| `SC13` | E2 | Hai card thật nối vào nhau; năm lần bấm ⇒ **1 hàng, 5 phản hồi**; và phép kiểm nghiêm nhất — **bịt mắt** cả hai phép đọc "đã lưu chưa" — vẫn không sinh hàng thứ hai |
| `SC18` | E2 | 0 outbound, 0 hàng đổi, và **204 kể cả khi im lặng**, có test riêng cho đúng mệnh đề đó (một status phân biệt được sẽ tự xác nhận bot tồn tại) |
| `SC28` | E2 | Worker chết sau provider ⇒ `unknown_attempt`; submit muộn **không** ghi kết quả; ≤ 2 lời gọi model; `usage.unknown` với **ba trường NULL**, không phải 0 |
| `SC47` | E2 | Bốn ca vòng đời mã, `telegram_link_attempt` tăng đúng 6, outbound 0 ở các ca không-thành-công |

**19 dòng giữ `NOT_RUN`, và bốn lý do khác nhau — không gộp lại làm một:**

1. **Cấp bằng chứng chưa mở** (6): `SC10`, `SC11`, `SC15` đòi E4; `SC14`, `SC16`, `SC17` đòi E3. Không lời gọi live nào đã xảy ra. `SC14` đáng ghi riêng: rất nhiều đã chạy (unknown không gửi lại, multipart nhận receipt từng phần, lỗi vĩnh viễn giữ report) — nhưng cấp mà scenario đòi thì chưa đạt.
2. **Bảng chưa tồn tại** (8): `SC06`, `SC08`, `SC19`, `SC22`, `SC24`, `SC25`, `SC50`, `SC52` — `report`, `report_item`, `coverage_window`, `pending_item_ledger`. Card delivery chạy trên **bảng `report` giả ba cột** và khai thẳng; một hash tính trên bảng thay thế không chứng minh bất biến của bảng thật.
3. **Cố ý không hiện thực** (3): `SC32` (`data.delete_target` là non-goal, `SG-01`), `SC27` (drill restore, Giai đoạn 6), `SC45` (nửa server thuộc `TC-scheduler-lease-claim`).
4. **Hợp đồng còn `KC` hoặc đang tranh chấp** (2): `SC46` là `NOT_RUN (BLOCKED_DEPENDENCY CR-PC07-04)` — khai đích danh, không im lặng; `SC49` thêm một mâu thuẫn chưa giải (`CR-TC-TGAUTH-04`).

Sau lượt này: **NOT_RUN 46 · PASS (E1) 3 · PASS (E2) 7** — tức **10/48** ở cấp ≤ E2 đã PASS, và **33** dòng mang `partial_evidence_vi`.

### 16.5 Cổng — vẫn không cổng nào chuyển

`G5` `PARTIALLY_MET`, `SP1` `NOT_MET`, `G6` `NOT_MET`. **`REQ-OQ03` nay đã được Owner trả lời** (`OD-20260908-05…09`) và không còn chặn `G5` — nhưng nó được thay bằng một lý do khác chứ không phải bằng không có lý do: cả hai adapter AI ship `enabled: false` trên căn cứ **cô lập** (ISO-03/ISO-05), không phải điều khoản. **Một provider đã được chọn không phải là một provider đã được chứng minh chạy được**, và `REQ-AC16` vì vậy vẫn **`BLOCKED`** — không phải `FAIL`: nó chờ một probe với binary thật, không chờ một bản sửa.

Mười ba module nay có code. **Có code không phải là đạt cổng**: `MOD-ai-adapter` tắt, `MOD-telegram-adapter` vẫn **chặn cứng** trên ba dữ kiện `KC` của `delivery.md` §3.4, và `MOD-research-connector` vẫn không `CONTRACT_READY`.

### 16.6 Ba finding, và một quy tắc thường trực thay cho lần thứ tư

`A3-P3-R1` §6: **HIGH 0 · MEDIUM 1 · LOW 2**; `A3-P3-R2` xác minh **cả ba** và tìm **0 finding mới**.

- **`F-A3-P3-01`** (MEDIUM) — `ruff format --check` đỏ trên bốn file: candidate sẽ **trượt CI** như đã đóng băng. Auditor viết thẳng: *"I would not sign a commit of these bytes until the formatter runs; the behaviour is sound, the gate is not."* **VERIFIED** ở R2 — và phần đáng giá của bản sửa là `ruff format --check` được thêm vào **danh sách lệnh** của card, nên nó không tái diễn.
- **`F-A3-P3-02`** (LOW) — hai `xfail` không phải cross-phase. **VERIFIED**, một residual được khai: `xfail(run=False)` còn lại cho fixture callback. Coordinator **chấp nhận nguyên trạng**, và lý do đáng ghi: nó nêu một `KC` của **hợp đồng**, không phải một card vắng mặt, nên nó **không thể tự hết im lặng** — giải nó làm dịch bytes của `delivery.md` và làm trượt mọi pin.
- **`F-A3-P3-03`** (LOW) — bốn fixture §2 không được chạy cũng không được ghi `NOT_RUN`. **VERIFIED**. Đây là **lần thứ ba** cùng một hình dạng (`F-A3R1-09` Giai đoạn 1, `F-A3-P2-01` Giai đoạn 2), và ba lần một auditor tìm ra bằng tay là tín hiệu rằng nó nên thôi làm finding từng vòng.

**Nên `PKT-PC09-P3` biến nó thành `E0-20-card-fixture-accounting`**, check thứ **26**: một card được coi là ĐÃ HIỆN THỰC khi `evidence/runs/<card>-E1-*.json` tồn tại; với mỗi card như vậy, mọi fixture `acceptance/fixtures/**.json` mà `§2. Read set` nêu tên phải **hoặc** được một file dưới `tests/` tham chiếu, **hoặc** được nêu trong handoff của chính card **trong một đoạn cũng chứa `NOT_RUN`**. Card chưa ai xây thì ngoài phạm vi — fixture của chúng không thể được chạy, và nói điều đó mỗi lượt là nhiễu chứ không phải tín hiệu.

Điều check này **không** chứng minh, và oracle của nó nói ra: một tham chiếu là **sự có mặt**, không phải độ phủ. Nó không biết test nhắc tên một fixture có khẳng định gì với nó hay không, nên một kết quả sạch **không** được đọc là "mọi fixture đã được phủ". Mutation-test **5/5** (bảng ở addendum `PKT-PC09-P3` của `evidence/handoffs/PC09-handoff.md`), gồm hai đối chứng dương: handoff nêu tên **kèm** `NOT_RUN` phải qua, và một card **chưa** hiện thực phải nằm ngoài phạm vi.

### 16.7 Điều mục này KHÔNG nói

- **Không** nói AI chạy được. Cả hai adapter tắt vì cô lập; **chưa lần gọi model live nào đã xảy ra**; `REQ-AC16` `BLOCKED`.
- **Không** nói Telegram gửi được. Không lần gọi Bot API nào; ba dữ kiện định dạng vẫn `KC`; `MOD-telegram-adapter` chặn cứng.
- **Không** nói `TC-A5-01` phủ mọi điều khoản: nó phủ điều khoản **Anthropic**; chính sách của arXiv/OpenAlex/X về việc xử lý lại nội dung của họ là một câu hỏi **riêng và chưa trả lời** (`OD-20260908-08` nói vậy).
- **Không** nói bốn file của `F-A3-P3-01` chỉ đổi định dạng — auditor từ chối khẳng định điều đó và tôi không khẳng định thay họ.
- **Không** có lời gọi live nào. **E3 và E4 vẫn bằng 0 ở mọi nhóm scenario**; SP1 chưa chạy.

---

## 17. Giai đoạn 4 (M4/M5) + Giai đoạn 6 (M7/M8) — và trạng thái sản phẩm sau sáu giai đoạn

*Thêm bởi `PKT-PC09-P4`, trên FC-P4 **epoch 2**. Con số do `derive_numbers.py` sinh; con số trích từ báo cáo audit ghi rõ là trích.*

### 17.1 Cái gì tồn tại thêm

| Phép đo | Sau Giai đoạn 3/5 | Sau Giai đoạn 4/6 | Khóa |
| --- | --- | --- | --- |
| File test Python | 34 | **44** | `test_files_count` |
| Hàm `test_*` | 669 | **865** | `test_defs` |
| Revision Alembic | 14 | **19**, một head (`0013`) | `migration_revisions` |
| Bảng | 33 | **48**, khớp `entities.yaml` **hai chiều, 0 khác biệt** | `A3-P4-R1` §1 |
| Card đã hiện thực | 13 | **19 / 19** | `card_runs_registered` |
| Báo cáo audit trong repo | 17 | **19** | `audit_reports_in_repo_count` |

**Số trích từ `A3-P4-R2` §1** (FC-P4 epoch 2, 645 entry, `d6d50758…`): **1028+ passed / 0 failed**; `ruff format --check` sạch; **`mypy --strict` nay phủ 87 file** (từ 64 — xem `F-A3-P4-02`); web Vitest **126/126**, `tsc` và eslint sạch; `verify_cards.py` **13/13, 3 730 assertion**; `e0_check.py` 26/26 tại thời điểm đó; một Alembic head; và **toàn bộ suite dưới chặn socket+DNS: rc=0, 0 lần thử mạng**.

### 17.2 Hai bất biến được ép bằng cơ sở dữ liệu, không bằng code

`A3-P4-R1` §2 không đọc mà **tái dẫn xuất**, và đây là kết quả mạnh nhất của cả giai đoạn:

- **Lease độc quyền** — `ux_assignment_lease_one_held`, `UNIQUE (owner_id, job_id) WHERE state = 'held'`. Auditor chèn hàng `held` thứ hai **bằng SQL thô** và cơ sở dữ liệu từ chối. Không phải một phép đọc-rồi-ghi mà một ứng dụng có thể quên.
- **CAS publish** — `ux_coverage_window_predecessor`. Bên thua bắt `IntegrityError`, roll back, và bị hủy với `cas_conflict` trong một transaction **riêng**. Docstring của publisher nêu đúng lý do: *"một phép kiểm đọc-rồi-ghi là một race"*.

### 17.3 Nhãn theo từng card — `A3-P4-R2` §6

Sáu card đều **may stand, scoped**. Hai điều đáng đọc:

- **Điều kiện của R1 đã được gỡ bỏ.** R1 loại REQ-D29/I07 khỏi phạm vi của `TC-report-coverage-publish-cas` vì `CR-TC-BACKFILL-09` — publisher công bố cả mục còn `pending`, nên một phát hiện muộn thật quay lại thành `prior_reference`. R2 xác minh bản sửa **và kiểm đúng chỗ đáng lo nhất**: điều kiện được dẫn từ `time-and-tags.md` §5.3 + §8.2, và **hợp đồng không bị sửa để code pass** — file đó nguyên vẹn từng byte. Phần disposition cũng được sửa: handoff nay nêu tên CR và có mục sửa lại lời khai độ phủ của chính nó.
- **`TC-backup-restore-drill` là "narrowed", không phải "scoped".** Cái đã chứng minh là hệ thống **TỪ CHỐI đúng chỗ**: một bản copy WAL-unsafe bị bắt bằng khuyết tật **tạo thật** (hash khớp, `integrity_check` ok, counts lệch đúng 4 hàng), 0 tin gửi trước khi đối soát xong, và ba cách một lần đối soát có thể *giả vờ* hoàn tất đều bị bác. **Không tồn tại một khẳng định nào rằng một restore đã từng được thực hiện.**

### 17.4 Scenario — 27 dòng được xét, **11 chuyển nhãn**

Sáu card khai chạm 27 scenario; cả 27 được xét theo quy tắc §14.5, rồi **xét lại trên epoch 2** sau khi R2 xác minh ba bản sửa. Chuyển: `SC05` (E1); `SC08`, `SC20`, `SC24`, `SC27`, `SC33`, `SC34`, `SC37`, `SC38`, `SC42`, `SC53` (E2).

Sau lượt này: **NOT_RUN 35 · PASS (E1) 4 · PASS (E2) 17** — **21/48** ở cấp ≤ E2 đã PASS, và **32** dòng mang `partial_evidence_vi`.

**Hai dòng bị chặn bởi khuyết tật ORACLE, không bởi thiếu code** — và chúng không thể PASS bằng bất kỳ lượng code nào:

| CR | Dòng | Khuyết tật |
| --- | --- | --- |
| `CR-PC09-22` | `SC09` | oracle đòi `report_item.reference_date`; `ENT-report-item` **không khai** trường đó. Card ship `item_type = 'prior_reference'` và không có cột nào mang ngày |
| `CR-PC09-23` | `SC22` | oracle đếm `pending_item_ledger.report_id` và `.consumed_at` — **cả hai không tồn tại** (card ship `first_pending_window_id` / `resolved_in_report_id`) — và kỳ vọng **2** mục trong khi fixture `e` mang **1**. W4B dừng đúng chỗ (`SG-PC09`) thay vì tự thêm cột |
| `CR-PC09-24` | `SC49` | không phải khuyết tật oracle mà là **giới hạn tầng đo**: oracle đòi cả ba cơ chế ép buộc, và cơ chế thứ ba là 14 cạnh `CAPABILITY_DENIED` chỉ đo được trên máy có Chrome thật và một tiến trình worker thật. `SC49` **sẽ không** chuyển bằng thêm test ở tầng này, dù thêm bao nhiêu cạnh |

### 17.5 Trạng thái sản phẩm

> **`NOT_READY_FOR_PRODUCT_CODE` giữ nguyên** — nhưng lý do đã đổi hoàn toàn, và điều đó đáng nói rõ. Ở Giai đoạn 0 nó có nghĩa *"chưa có code"*. Nay nó có nghĩa: **code đã có, đã được audit độc lập bảy lượt, và chưa từng chạy một lần nào trong thế giới thật.**

| Cổng | Trạng thái | Vì sao |
| --- | --- | --- |
| `G0`–`G2` | MET | không đổi |
| `G3`, `G4` | PARTIALLY_MET | các mục `KC` và `G4-X7` |
| `G5` | PARTIALLY_MET | bốn điều kiện ra đủ; điều kiện **VÀO** (G4) chưa |
| `SP1` | NOT_MET | **0/5–10 đợt probe.** Rào chắn là **vật lý và thuộc Owner** |
| `G6` | NOT_MET | **21/48 · 0/5 · 0/2** |
| `G7` | NOT_APPLICABLE_YET | G6 chưa đạt |

**Điều quan trọng nhất trong bảng trên: `G6-X2` và `G6-X3` không chờ thêm code.** Chúng chờ những việc chỉ Owner làm được. Viết thêm bao nhiêu test cũng không chuyển được chúng.

### 17.6 Danh sách còn lại cho Owner — mọi việc chỉ Owner làm được

Đây là danh sách đầy đủ, không rút gọn. Mỗi dòng là một việc **không Worker nào được phép thực hiện**, kèm cái nó sẽ mở khóa.

| # | Việc của Owner | Mở khóa | Hiện trạng |
| --- | --- | --- | --- |
| 1 | **Chạy probe X** (`SP1`): cài Playwright trên máy Owner, đăng nhập tay vào một Chrome profile riêng, điền `probe-config.json`, ký bốn `owner_confirmations` kèm `evidence_ref`, chạy 5–10 đợt | `SP1`, `REQ-A1`, `REQ-A7`, `REQ-AC16`, `SC51`; và con số giới hạn thật `REQ-OQ05` | Cổng mở **hành chính** (`OD-20260907-04`); bộ công cụ đã có và đã được audit; `runs.jsonl` **vắng mặt** — đúng thiết kế |
| 2 | **Bật một adapter AI và chạy thật** (E3): cả hai ship `enabled: false` vì **cô lập** (ISO-03/ISO-05), không vì điều khoản | `SC16`, `SC17`; `REQ-AC16` từ `BLOCKED` | Code đã có, từ chối đúng thứ tự **trước khi chạm transport** (auditor tự nạp registry thật) |
| 3 | **Gửi thật một tin Telegram** (E3) | `SC14` | Chưa lần gọi Bot API nào ở bất kỳ giai đoạn nào |
| 4 | **Chạy một drill restore thật** vào môi trường sạch, đo RPO/RTO | `SC43`, `G6-X3` | `SC27`/`SC53` đã PASS (E2) trên restore vào DB sạch; drill môi trường thật `NOT_RUN` |
| 5 | **Đọc và review giao diện thật** trên desktop và điện thoại (E4) | `SC10`, `SC11`, `SC15` | 126/126 Vitest chứng minh ba trạng thái sinh **ba chuỗi khác nhau**; "khác nhau ở mức người dùng hiểu được" là phán đoán của người |
| 6 | **Đọc 3–4 kỳ báo cáo thật** để hiệu chỉnh `REQ-A2`/`REQ-A4` | `G7`, rubric mật độ | `uncalibrated`; 0 kỳ thật |
| 7 | **Đọc tài liệu Bot API** cho ba dữ kiện `delivery.md` §3.4 (độ dài `callback_data`, bảng escape, số nút mỗi hàng) | `CR-PC07-04`, `SC46`, và `MOD-telegram-adapter` khỏi chặn cứng | Cần một range/offset fetch trên URL chính thức — **một sửa đổi công cụ, không phải một quyền mạng mới** (`A3-P3-R1`) |
| 8 | **Chốt các giá trị PROVISIONAL**: N backfill (`REQ-OQ04`), model embedding (`REQ-OQ09`), ba số của link code (`CR-PC07-01`) | các dòng `KC` tương ứng | Đang dùng giá trị làm việc Owner đã chấp nhận, **không phải** giá trị chốt |
| 9 | **Trả lời chính sách nguồn**: arXiv/OpenAlex/X có cho phép xử lý lại nội dung của họ không | một câu hỏi pháp lý còn mở | `TC-A5-01` chỉ phủ điều khoản **Anthropic**; `OD-20260908-08` nói thẳng đây là câu hỏi riêng |
| 10 | **Quyết định `MOD-tag-service`** — chưa có card nào viết nó | `CR-TC-BACKFILL-07` | `tag` là bảng do card khác tạo hộ; không module nào sở hữu nó |

### 17.7 Điều mục này KHÔNG nói

- **Không** nói sản phẩm chạy được. Chưa một lần gọi X, Telegram, hay provider AI nào. **E3 và E4 bằng 0 ở mọi nhóm scenario**, qua cả sáu giai đoạn.
- **Không** nói một restore đã từng được thực hiện.
- **Không** nói giao diện dùng được — chỉ nói nó sinh ra đúng chuỗi.
- **Không** nói `E0-20`/`E0-21` là đúng: cả hai do PC09 viết, tự kiểm bằng công cụ PC09 vừa sửa, và `F-A3-P4R2-01` là bằng chứng rằng một cửa kiểm mới có thể có lỗ ngay khi ra đời.
- **Không** nói đồng thời an toàn ở mức nhiều tiến trình: vẫn chưa có race test đa tiến trình.

## 18. Đợt nối dây (FC-P5) — hệ thống **khởi động được**, và vì sao không con số nào nhúc nhích

*Thêm bởi `PKT-PC09-P5`, trên FC-P5 **epoch 3** (705 entry, `manifest_sha256 = ed0bbf6c74d0…`). Con số do `derive_numbers.py` sinh; con số trích từ báo cáo audit ghi rõ là trích.*

### 18.1 Đợt này tồn tại vì một câu hỏi mà không cửa kiểm nào của tôi từng hỏi

`docs/owner-runbook.md` (WS2) phát hiện một điều mà **cả sáu giai đoạn, mười một lượt audit, 3 963 assertion của `verify_cards` và 27 check `E0` đều không phát hiện**: 19 card đã được dựng và kiểm **đối chiếu với port và harness**, nhưng **không tồn tại một ứng dụng chạy được**. `create_app()` không dựng service nào; `auth.login` trả 500 ngoài test; không có CLI bootstrap owner; `alembic` chỉ chạy từ `server/`; `storage.health` chỉ sống trong bộ nhớ tiến trình; `main.py` của collector và worker là stub Giai đoạn 0; ba operation `secret.*` **không có code**.

Đây là bài học đắt nhất của gói này và nó thuộc về tôi cũng như mọi người khác: **mọi cửa kiểm tôi viết đều kiểm tài liệu và kiểm quan hệ giữa các tài liệu.** Không cửa nào hỏi "khởi động nó lên xem". Mười gap `G-1…G-10` của runbook được tìm ra bằng cách một người ngồi làm theo tài liệu của chính dự án.

### 18.2 Cái gì tồn tại thêm

| Phép đo | Sau Giai đoạn 4/6 | Sau đợt nối dây | Khóa |
| --- | --- | --- | --- |
| File test Python | 44 | **48** | `test_files_count` |
| Hàm `test_*` | 865 | **982** | `test_defs` |
| Revision Alembic | 19, head `0013` | **21**, một head **`0015_tc_storage_maintenance_window`** | `migration_revisions` |
| Card đã hiện thực | 19 / 19 | **20 / 20** (`TC-secret-settings-service`) | `card_runs_registered` |
| Báo cáo audit trong repo | 19 | **22** | `audit_reports_in_repo_count` |
| Bản ghi trong `evidence/index.json` | 109 | **114** | `records_total` |
| Entity khai trong `entities.yaml` | — | **61**, ba tập purge **37 / 22 / 2** | `entities` |

Mới về chất, không chỉ về lượng: một **composition root** (`server/app/settings.py` + `wiring.py`), một CLI quản trị (`rr-admin migrate | bootstrap-owner | status`), năm console script (`rr-admin`, `rr-backup`, `rr-collector`, `rr-worker`, `rr-probe`) chạy từ bất kỳ thư mục nào, `storage.health` **bền qua tiến trình** trên entity mới `maintenance_window` (`AMD-ENT-maintenance-01`, migration `0015`), probe giải `output_dir` theo cwd với `--dry-run` **thật sự không ghi gì**, hai vòng lặp tiến trình (collector, worker), và card thứ 20 — dịch vụ secret/settings với mã hóa envelope AES-256-GCM.

### 18.3 Lần đầu tiên bằng chứng đến từ một **tiến trình**, không từ `TestClient`

Đây là điều đáng đọc nhất của cả đợt. `A3-P5-R1` §2 chạy hệ thống như một **tiến trình hệ điều hành** — `uvicorn` thật, `curl` thật qua TCP, các lần gọi CLI riêng biệt — và trích nguyên văn:

| Yêu cầu | Kết quả (trích `A3-P5-R1` §2) |
| --- | --- |
| `GET /healthz` | **200** `{"status":"up","schema_version":"0.3.0"}` |
| `POST /v1/auth/login` (thiếu header) | **422**, `ErrorEnvelope` đúng, `violation_kind: required_header_missing` |
| `POST /v1/auth/login` (đúng) | **200**; `rr_session` **HttpOnly / Secure / SameSite=lax / Max-Age=43200** và `rr_csrf` **không** HttpOnly |
| `GET /v1/health/readiness`, `/v1/runs`, `/v1/settings`, `/v1/saved` | **200** |
| `GET /v1/reports` | **500 `INTERNAL`** ⇒ `F-A3-P5-03`, đã sửa và xác minh ở R2 |

Cờ cookie của `secrets.md` §2.3 — thứ tôi mới chỉ kiểm **cấu trúc** từ Giai đoạn 1 — nay đã được nhìn thấy **trên dây**. Và `backup_cli maintenance --open` ở một tiến trình để lại một hàng `maintenance_window` mà **một tiến trình khác** đọc được: `G-3` đóng bằng quan sát, không bằng lập luận.

### 18.4 Ba lượt audit, và mỗi lượt tìm ra thứ lượt trước bỏ sót

| Lượt | Candidate | Verdict | Finding mới |
| --- | --- | --- | --- |
| `A3-P5-R1` | FC-P5, 692 entry, `d4d7f219…` | **PASS có finding** | 3 MEDIUM (`F-A3-P5-01/-02/-03`) + 1 LOW (`-04`) |
| `A3-P5-R2` | FC-P5 e2, 700 entry, `81389284…` | **PASS** — cả bốn **VERIFIED** | 1 LOW (`F-A3-P5R2-01`) |
| `A3-P5-R3` | FC-P5 e3, 705 entry, `ed0bbf6c…` | **PASS** — VERIFIED **cả hai chiều** | 1 LOW (`F-A3-P5R3-01`) |

Hai chi tiết đáng giữ lại:

- **`F-A3-P5-02` là một lời khai đã sai suốt ba giai đoạn.** `rr_admin status` — đúng cái màn hình đợt này dựng cho Owner học xem cái gì đã nối — in ra rằng research connector bị chặn vì *"REQ-A6 facts still PLACEHOLDER_KC"*. Điều đó sai từ Giai đoạn 2: `retry-policy.yaml` mang `DOCS_derived` với đủ sáu giá trị và `REQ-A6` ở `XN`. Bản sửa không chỉ đổi câu chữ mà **đọc trạng thái từ contract lúc chạy** — vì một chuỗi hard-code chính là thứ đã mòn.
- **`A3-P5-R3` §2 ghi lại một lần suýt sai của chính auditor**: lần đọc log đầu tiên trả về số của một epoch **cũ** vì họ dùng lại tiền tố log `r3-` từ vòng `A3-R3`; họ tự bắt bằng `mtime`, xóa sentinel, đợi lượt chạy mới và đọc lại. Đúng hạng lỗi mà chính họ đã nêu với người khác bốn lần. Một auditor ghi lại lỗi của chính mình đáng tin hơn một auditor chưa từng có lỗi nào.

### 18.5 Scenario — **bảy dòng được xét, 0 chuyển nhãn**, và đó là con số đúng

Bảy dòng đợt này chạm (`SC04`, `SC16`, `SC17`, `SC36`, `SC41`, `SC44`, `SC49`) đều được xét theo quy tắc ba điều kiện §14.5. **Không dòng nào đủ điều kiện.** Sau lượt này: **NOT_RUN 35 · PASS (E1) 4 · PASS (E2) 17** — vẫn **21/48** ở cấp ≤ E2, y hệt sau Giai đoạn 4/6.

`SC36` là ví dụ rõ nhất về khoảng cách giữa "chạy được" và "đã đo": `AMD-ENT-maintenance-01` cộng bản sửa của WR đóng `G-3`, và A3 chứng minh cửa sổ maintenance sống qua **hai tiến trình OS riêng biệt** — nhưng oracle của `SC36` đòi nhánh `write_blocked → healthy` qua **một lần ghi thật**, và nhánh đó vẫn là một probe **tiêm** (`CR-TC-storage-04`). Một nửa khác của cùng vấn đề đã đóng; nửa oracle hỏi thì chưa.

**Một thiếu sót của chính tôi, khai ra thay vì để im.** Trong 35 dòng `NOT_RUN` có **32** dòng mang `partial_evidence_vi`; ba dòng **không** — `SC54`, `SC55`, `SC56`. Chưa gói PC09 nào xét từng dòng cho chúng, nên hôm nay không ai đọc được từ danh mục là chúng thiếu gì. Đó là một lỗ **tài liệu của PC09**, không phải của một card, và nó nằm ở đây chứ không nằm im.

### 18.6 Hai lỗ trong chính bộ công cụ của tôi, tìm ra trong gói này

1. **`E0-18` không đọc con số** (`CR-PC02-25`). `AMD-ENT-maintenance-01` đổi ba tập purge thành **37 / 22 / 2**; **chín artefact** vẫn khẳng định con số cũ; `E0-18` **PASS suốt** vì nhánh (b) đọc marker và nhánh (c) đọc danh sách **có cấu trúc**, không nhánh nào đọc một chữ số. Chúng được tìm bằng `grep`. Nhánh mới đọc bốn dạng khẳng định **theo nghĩa đen** trên mười artefact được gọi tên: `items_checked` **17 → 91**, mutation **11/11** (tám đột biến bị bắt, hai đối chứng âm giữ sạch — trong đó một đối chứng là **liệt kê văn xuôi 21 tên bảng sai**, cố ý **không** bị bắt vì đó là giới hạn đã ghi ở §5g/§5h của `evidence/tools/README.md`). Trên bytes lúc viết, nhánh mới **FAIL với 6 vi phạm thật** trên hai file ngoài write set của tôi; W3n sửa chúng trong lúc self-test đang được viết.
2. **Bảng finding của tôi không nhìn thấy bốn finding đang sống.** Mẫu nhận diện `F-A3…` không khớp dạng id `F-A3-P4R2-01` / `F-A3-P5R3-01` (đoạn giai đoạn dính liền số vòng, không có gạch nối). Hệ quả: `F-A3-P4R2-01` và `-02` **chưa từng xuất hiện** trong bảng §8.2 kể từ khi chúng ra đời ở Giai đoạn 4/6. Đây là **lần thứ ba** mẫu này phải nới vì một vòng phát minh ra một dạng id mới, và lần này nó được ghi ngay trong mã nguồn của `crtable.py` — một bảng chỉ tốt bằng cái lưới của nó.

### 18.7 Cổng — **không cổng nào chuyển**, và nói chính xác cái đã đổi

| Cổng | Trạng thái | Đợt này đổi gì |
| --- | --- | --- |
| `G0`–`G2` | MET | không đổi |
| `G3` | PARTIALLY_MET | không đổi (`G3-X5`, các mục `KC`) |
| `G4` | PARTIALLY_MET | `G4-X7` **vẫn `met: false`**, nhưng lý do được viết lại cho đúng: ba lượt P5 khép kín trong đợt (bốn finding → VERIFIED; một → VERIFIED; một → đóng bằng phát lại manifest), trong khi `F-A3R4-01`, `F-A3-P2-01/-02`, `F-A3-P4R2-01/-02` còn mở |
| `G5` | PARTIALLY_MET | không đổi |
| `SP1` | NOT_MET | **0/5–10 đợt**, không đổi |
| `G6` | NOT_MET | **21/48 · 0/5 · 0/2 — không đổi một chữ số** |
| `G7` | NOT_APPLICABLE_YET | không đổi |

**Cái đã đổi và không nằm trong bảng nào**: hệ thống khởi động được, và một auditor độc lập đã chạy nó như một tiến trình. Đó là điều kiện **cần** để bất kỳ E3/E4 nào từng xảy ra — nhưng nó **không phải** một điều kiện ra của cổng nào, và gói này không giả vờ ngược lại.

### 18.8 Trạng thái sản phẩm

> **`NOT_READY_FOR_PRODUCT_CODE` giữ nguyên.** Lý do lại đổi một lần nữa, và lần này theo hướng tốt: ở Giai đoạn 0 nó nghĩa là *"chưa có code"*; sau Giai đoạn 4/6 nó nghĩa là *"có code, đã audit, chưa từng chạy"*; nay nó nghĩa là **"chạy được, đã được chạy như một tiến trình bởi một auditor độc lập, và vẫn chưa làm được việc gì đầu-cuối"**.

`A3-P5-R1` §5 trả lời thẳng câu hỏi của đợt — *Owner chạy được đầu-cuối chưa?* — bằng **KHÔNG**, kèm danh sách. Tôi chép nguyên vẹn thay vì tóm tắt:

1. **Report — không dựng được gì cả.** `report_context` chưa nối (`CR-P0-07`). Đây là **đầu ra của sản phẩm**.
2. **`maintenance --open` như tài liệu viết** — đã sửa ở R2, nhưng `docs/owner-runbook.md` §9.4 **vẫn mang câu lệnh cũ** cho tới khi WS2 kiểm lại sau commit.
3. **Tag** — `MOD-tag-service` chưa có card nào (`CR-TC-SCHED-06`, `CR-TC-BACKFILL-07`).
4. **Research connector** — chưa nối; lý do thật là `SG-DOC` / `SG-LIVE`.
5. **Mọi đường live** — collector cần `RR_SERVER_URL`, token và một phiên X thật; Telegram cần bot token và `RR_TELEGRAM_WEBHOOK_SECRET`; cả hai adapter AI `enabled: false` vì cô lập chưa xác minh. **E3/E4 `NOT_RUN` ở mọi nơi.**

### 18.9 Danh sách còn lại cho Owner — cập nhật sau đợt nối dây

Mười một dòng. Mười dòng đầu là bảng §17.6, cập nhật hiện trạng; dòng 11 là mới và là một **câu hỏi phê chuẩn**, không phải một việc kỹ thuật.

| # | Việc của Owner | Mở khóa | Hiện trạng sau đợt nối dây |
| --- | --- | --- | --- |
| 1 | **Chạy probe X** (`SP1`): Playwright trên máy Owner, đăng nhập tay vào Chrome profile riêng, `probe-config.json`, bốn `owner_confirmations`, 5–10 đợt | `SP1`, `REQ-A1`, `REQ-A7`, `REQ-AC16`, `SC51`, `REQ-OQ05` | **Dễ chạy hơn trước**: `--dry-run` nay giải `output_dir` theo **cwd** và A3 xác minh trên hệ thống tệp là nó **không ghi gì**; `uv run rr-probe` chạy từ bất kỳ đâu. `runs.jsonl` vẫn **vắng mặt** — đúng thiết kế |
| 2 | **Bật một adapter AI và chạy thật** (E3) | `SC16`, `SC17`; `REQ-AC16` từ `BLOCKED` | Card thứ 20 nay cấp một **chỗ hợp lệ để đặt API key** (envelope AES-256-GCM, khóa chủ **chỉ từ env**, không sinh, không mặc định, không log). Cả hai adapter vẫn `enabled: false` vì **cô lập**, không vì điều khoản |
| 3 | **Gửi thật một tin Telegram** (E3) | `SC14` | Chưa lần gọi Bot API nào; nay có chỗ hợp lệ cho `RR_TELEGRAM_WEBHOOK_SECRET` |
| 4 | **Drill restore thật** vào môi trường sạch, đo RPO/RTO | `SC43`, `G6-X3` | `rr-backup maintenance --open --reason …` nay **bền qua tiến trình** và báo lỗi bằng envelope + exit code thay vì traceback |
| 5 | **Review giao diện thật** trên desktop và điện thoại (E4) | `SC10`, `SC11`, `SC15` | Không đổi |
| 6 | **Đọc 3–4 kỳ báo cáo thật** để hiệu chỉnh `REQ-A2`/`REQ-A4` | `G7`, rubric mật độ | **Chặn cứng**: `/v1/reports` chưa dựng được report nào (`CR-P0-07`) — đây là mục chặn nhiều nhất trong danh sách |
| 7 | **Đọc tài liệu Bot API** cho ba dữ kiện `delivery.md` §3.4 | `CR-PC07-04`, `SC46` | Không đổi |
| 8 | **Chốt các giá trị PROVISIONAL** (`REQ-OQ04`, `REQ-OQ09`, `CR-PC07-01`) | các dòng `KC` | Không đổi; `rr-admin status` nay in ra cái gì đã nối và cái gì chưa, kèm lý do |
| 9 | **Trả lời chính sách nguồn** (arXiv / OpenAlex / X) | câu hỏi pháp lý còn mở | Không đổi |
| 10 | **Quyết định `MOD-tag-service`** — chưa có card nào viết nó | `CR-TC-BACKFILL-07` | Không đổi; A3 liệt kê "tags" là một trong năm thứ Owner chưa dùng được |
| 11 | **Phê chuẩn hoặc bác `AMD-ENT-maintenance-01`** — sửa đổi **kỹ thuật của Coordinator** thêm entity `maintenance_window` và đổi tập purge thành 37/22/2 | tính hợp lệ của `0015` và của toàn bộ đường storage-health bền | **Owner chưa được hỏi.** Cùng hình dạng với `AMD-ENT-owner-01` — cái Owner **đã** phê chuẩn sau đó — nhưng `A3-P5-R3` §4 nói đúng: nó nên được đưa ra hỏi, **không nên tự chốt bằng im lặng** |

### 18.10 Điều mục này KHÔNG nói

- **Không** nói sản phẩm chạy được đầu-cuối. Nó nói sản phẩm **khởi động** được, và một auditor độc lập đã khởi động nó.
- **Không** nói một lời gọi live nào đã xảy ra. **E3 và E4 bằng 0 ở mọi nhóm scenario, qua cả bảy đợt.**
- **Không** nói `/v1/reports` đã hoạt động: nó nay trả **đúng mã lỗi đã khai** thay vì `INTERNAL`. Một mã lỗi đúng không phải một tính năng.
- **Không** nói `E0-18` nay bắt được mọi thứ: liệt kê **văn xuôi** vẫn không được so, và câu đó nay được in ra trong chính đầu ra của `E0-18` để một `PASS` không bị đọc quá.
- **Không** nói `AMD-ENT-maintenance-01` đã được phê chuẩn. Nó là một sửa đổi kỹ thuật của Coordinator và **Owner chưa được hỏi**.
