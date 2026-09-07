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

Người viết: `worker-W6` (PC09, verification owner) · Ngày: 2026-09-07 (bản PC09-FIX2, sau đợt
FIX6 và audit A2-R1) · Claim: `DRAFT_FOR_REVIEW`

> **Mọi con số trong bản này được SINH RA, không được chép tay.** Bộ sinh là
> `derive_numbers.py` (đọc thẳng artefact và lần chạy E0 đã đăng ký) và `crtable.py` (quét toàn
> repo tìm CR id), chạy từ thư mục scratch của Worker.
>
> **Đầu ra của chúng nằm TRONG candidate**, cạnh lần chạy E0 mà chúng mô tả:
> `evidence/runs/numbers-20260907T023000Z.json` và
> `evidence/runs/cr_summary-20260907T023000Z.json`. Mỗi con số
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

Bộ hợp đồng đã đủ hình dạng để đọc và để phản biện — mọi con số sau đây kèm khóa nguồn trong
`numbers.json`: **246** yêu cầu nguyên tử (`requirements`), **85** operation (`operations`),
**99** cạnh được phép và **36** cạnh bị cấm (`allowed_edges`, `forbidden_edges`) — cả 36 nay có
mã lỗi đã pin VÀ một sự kiện quét khớp nội dung — **60** entity (`entities`), **67** transition
trên năm máy trạng thái (`transitions_counted`, khớp `E0-09.items_checked`), **28** mã lỗi
(`error_codes`), **86** fixture trên **9** thư mục (`fixtures`, `fixture_directories`, đếm từ
đĩa), **56** scenario có oracle (`scenarios`) và **0** scenario thiếu fixture
(`scenarios_missing_fixture`). Không yêu cầu P0 nào ở trạng thái XN hay UQ còn mồ côi
(`coverage.ORPHAN` = 0); mỗi invariant I01–I17 nay có một scenario được khai `positive` **và**
một được khai `negative` — `mixed` không còn được tính cho cực nào.

**Lần chạy E0 của bản này: 22 check, 22 PASS, 0 FAIL, 0 vi phạm** (`e0`, run
`evidence/runs/E0-20260907T023000Z.json`). Bộ check tăng 19 → 20 → **22**: `E0-04b` được thêm ở đợt FIX6 theo ruling F-A2R1-01, rồi **tách
làm ba** ở đợt FIX7 theo ruling "E0-04b design" — `E0-04b` (operation), `E0-04c` (cột),
`E0-04d` (mã lỗi). Cả ba nay PASS. Việc một check mới tìm ra lỗi ngay khi được bật là kết quả mong đợi, không phải
hồi quy — và việc nó trở về 0 sau khi các gói sở hữu sửa nội dung (chứ không sau khi ai đó nới
check) là cách một cửa kiểm nên kết thúc.

Nhưng nó vẫn **chưa** là một baseline có thể tuyên bố `CONTRACT_READY` ở bất kỳ phạm vi nào, vì
ba lý do độc lập nhau, không lý do nào là ý kiến, và **không lý do nào một Worker gỡ được**:

1. **B01–B17 vẫn `OPEN`** trong `agent_profile/registry.json`. Mọi phương án giải chúng mang nhãn
   `PROVISIONAL` và chờ Owner. 84 trong 246 dòng registry có văn bản cam kết sẽ đổi nếu Owner phê
   chuẩn amendment tương ứng.
2. **Chưa có xác minh độc lập trên epoch chứa các bản sửa FIX4 và FIX5.** A1 đã audit ba epoch;
   **A2 — auditor độc lập cuối — chưa chạy** (xem §4.1). Theo protocol §8, người viết bản sửa
   không được là người xác minh chính bản sửa đó, nên "19/19 PASS" ở đây là con số của phía sửa,
   không phải một verdict độc lập.
3. **Không có một byte bằng chứng runtime nào.** E1–E4 là `NOT_RUN` ở cả 53 scenario. Chưa có
   code, chưa gọi provider AI, chưa chạy collector, chưa gửi Telegram, chưa drill restore.
4. **Hai mục `KC` chặn cứng hai module:** `REQ-A6` (nhịp gọi arXiv/OpenAlex) và `CR-PC07-04`
   (giới hạn định dạng Telegram). Cả hai đòi đọc tài liệu bên ngoài mà phiên này không có mạng để
   đọc; không ruling nào thay thế được việc đó.

Điều **đã** đạt và đáng ghi: E0 nay **22/22 check PASS, 0 vi phạm, exit 0**, và mọi FAIL của ba
đợt trước đều được đóng bằng cách **sửa nội dung hợp đồng** — không lần nào bằng cách nới một
check. Đó là điều kiện cần cho G4, không phải điều kiện đủ.

Trạng thái dự án giữ nguyên `NOT_READY_FOR_PRODUCT_CODE`.

---

## 2. Độ phủ yêu cầu

`acceptance/traceability.csv` có **246 dòng**, đúng bằng `precode/requirements.csv`.

| coverage_status | Số dòng | Nghĩa |
| --- | ---: | --- |
| `COVERED` | 90 | Có ít nhất một hợp đồng trích dẫn VÀ ít nhất một scenario phủ |
| `PARTIAL` | 60 | Có hợp đồng nhưng chưa có scenario, hoặc ngược lại, hoặc chỉ được phủ bằng một cổng |
| `BLOCKED_B01..B17` | 84 | Văn bản cam kết đổi nếu Owner phê chuẩn amendment tương ứng |
| `DEFERRED_P1` | 6 | Hoãn sau MVP theo SRC-SPEC §2.2 |
| `OUT_OF_SCOPE` | 6 | Ngoài phạm vi theo SRC-SPEC §2.3 |
| **`ORPHAN`** | **0** | — |

Phân bố của 84 dòng `BLOCKED`: B01 8 · B02 8 · B03 7 · B04 6 · B05 6 · B07 7 · B08 7 · B09 5 ·
B10 6 · B11 6 · B12 4 · B15 6 · B16 3 · B17 5. Ba blocker **không** sinh amendment văn bản (B06,
B13, B14) nên các dòng của chúng giữ trạng thái độ phủ bình thường, với blocker ghi ở cột notes —
đúng như `precode/decision-register.md` §3 khai.

**37 dòng `PARTIAL` là P0 với status XN hoặc UQ** (`partial_p0_xn_uq`). Ruling R5-03 đóng đúng "nhóm
thật", và PC09-FIX1 bổ sung `requirement_refs` phía scenario cho phần còn lại của nhóm đó. Phân
loại 37 dòng còn lại (`partial_p0_breakdown`):

| Nhóm | Số dòng | Vì sao PARTIAL | Đề xuất |
| --- | ---: | --- | --- |
| Chỉ có cổng (`gate-only`) | 8 | Bảy dòng mốc `REQ-S13-01..08` cộng một chỉ tiêu thành công. Là mốc quy trình / chỉ tiêu nhiều tuần, không phải hành vi kiểm được bằng một scenario | **Giữ PARTIAL là đúng.** Chúng được phủ bằng cổng G5/G6/G7. Ép thành COVERED bằng một scenario giả sẽ là làm đẹp con số |
| Chỉ có hợp đồng (`contract-only`) | 19 | Hợp đồng mô tả, chưa scenario nào khẳng định. Gồm `REQ-S1.4-01`, `-02` (chỉ tiêu tuần, đo ở E4) và `REQ-S4-10` (màu sắc/visual design **cố ý chưa chốt** — một quyết định KHÔNG chốt thì không có gì để test) | Phần lớn hợp lý. Gói sở hữu có thể bổ sung scenario, nhưng đây **không** phải khiếm khuyết chặn cổng |
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

Công cụ: `evidence/tools/e0_check.py` (**20 check**, tăng từ 19). Run:
`evidence/runs/E0-20260907T023000Z.json`, đăng ký ở `evidence/index.json` bản ghi `EV-PC09-01`.
`baseline_hashes` gồm 168 file quét được (`evidence/runs/` đã bị loại khỏi phạm vi quét —
xem §3.5).

**22 PASS · 0 FAIL · 0 vi phạm** (`e0` trong `numbers.json`).

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

---


## 4. Trạng thái audit

### 4.1 Trạng thái audit — **nguồn duy nhất của sự thật cho trạng thái này trong toàn bản**

Mọi mục khác của bản này trỏ về đây thay vì nhắc lại. `F-A2R2-01` xảy ra chính vì trạng thái audit
được viết ở bốn chỗ và ba chỗ không được quét lại khi nó đổi; kỷ luật `numbers.json` áp cho *số*
nay áp cho cả *trạng thái*.

**6 AUDIT_REPORT độc lập đã chạy** (`audit_reports`, `audit_reports_count` — đếm từ đĩa):
`A1-R1` (FAIL), `A1-R2` (FAIL), `A1-R3` (FAIL), `A2-R1` (FAIL cho PC09), `A2-R2` (PASS tổng thể), `A2-R3` (xác minh bản sửa FIX9).

| Vòng | Phạm vi | Verdict | Finding |
| --- | --- | --- | --- |
| `A1-R1` | FC-W1 epoch 1 (PC00–PC02) | FAIL | 9 (4 MAJOR, 5 MINOR) — tất cả **VERIFIED** ở R2 |
| `A1-R2` | FC-W2 epoch 2 (+PC03, PC04) | FAIL | 6 (3 MAJOR, 3 MINOR) — tất cả **VERIFIED** ở R3 |
| `A1-R3` | FC-W3 epoch 3 (+PC05–PC08) | FAIL | 5 (1 MAJOR, 4 MINOR) — `FIX_PROPOSED`, xác minh ở A2-R1 |
| `A2-R1` | FC-W4 epoch 4 | **FAIL cho PC09** | 11 (2 MAJOR, 3 MEDIUM, 4 LOW, 2 INFO) |
| `A2-R2` | epoch 5 | **PASS tổng thể** | 10 VERIFIED · 1 PARTIAL · 0 NOT_VERIFIED; **4 finding LOW mới**, cả bốn thuộc PC09 |
| `A2-R3` | epoch 6 (chỉ diff bản sửa) | xác minh bản sửa FIX9 | 3 VERIFIED · 2 PARTIAL · 0 NOT_VERIFIED; **3 finding LOW mới** (`F-A2R3-01..03`), cả ba thuộc PC09 và đã sửa ở đợt FIX10 |

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

**Lượt xác minh đang chờ:** bốn finding trên là `FIX_PROPOSED`; A2 chưa kiểm lại bản sửa của
chính đợt này. Theo protocol §8 tôi không được tự xác minh bản sửa của mình, nên "22/22 PASS,
0 vi phạm" ở §3 là **con số của phía sửa, chạy bằng công cụ do phía sửa viết** — bằng chứng cần
được kiểm, không phải một verdict.


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

## 5. Rà soát lại B01–B17

Cả 17 blocker **vẫn `OPEN`** trong `agent_profile/registry.json`. Bảng dưới ghi: phương án
`PROVISIONAL` đã được hiện thực hoá tới đâu trong hợp đồng, và điều gì còn thiếu.

| ID | Phương án PROVISIONAL đã hiện thực hoá ở đâu | Hiện thực hoá đầy đủ? | Điều còn thiếu |
| --- | --- | --- | --- |
| B01 | Freeze tag tại transaction publish; `report.tag_config_version_id` bất biến. `time-and-tags.md` §4, ADR-0004, AMD-B01, SC05/SC19 | **Đủ** | Owner phê chuẩn AMD-B01 (đọc lại "thời điểm gửi" của C03 thành "thời điểm publish") |
| B02 | Tách `phase/status/outcome/stop_reason`; bảng ánh xạ 13 dòng. `state/run.yaml`, ADR-0002, AMD-B02, SC03/SC15 | **Đủ** — A1 xác minh 13/13 dòng verbatim | Owner phê chuẩn AMD-B02 (AC-03 đọc lại) |
| B03 | Thêm `delivery.unknown`, không auto-retry. `state/delivery.yaml`, ADR-0003, AMD-B03, SC14 | **Đủ** | Owner phê chuẩn AMD-B03 (AC-14 đọc lại: "không có lần gửi lặp tự động" thay cho "không có tin nào bị gửi hai lần") |
| B04 | Coverage ledger độc lập; kỳ rỗng vẫn ghi coverage. `time-and-tags.md` §4.7, AMD-B04, SC08/SC22 | **Đủ, nhưng có một lựa chọn trái khuyến nghị** | PC04 chọn phương án (b) — giữ hàng `report(status='aborted', abort_reason='empty_period')` — thay cho khuyến nghị (a) của Coordinator, với lý do idempotency cụ thể (`coverage_window` không có khóa idempotency). Coordinator/Owner cần xác nhận hoặc bác; đường đảo đã được ghi |
| B05 | Cam kết là "không ingest trùng theo `x_post_id`", không phải "không đọc lại". AMD-B05, SC21 | **Đủ ở mức hợp đồng** | Độ ổn định thật của con trỏ feed chỉ đo được bằng probe SP1. REQ-A1 vẫn `KC` |
| B06 | Identity + alias + work version + target tagged union. `identity.md`, ADR-0009, SC07/SC23/SC29/SC30 | **Đủ** | Không có amendment văn bản; Owner vẫn cần phê chuẩn vì nó định nghĩa phần còn thiếu của D17 |
| B07 | Một kết quả hợp lệ mỗi `analysis_key` + generation. ADR-0008, AMD-B07, `state/analysis.yaml`, SC06/SC28 | **Đủ** | Owner phê chuẩn AMD-B07 (nghĩa của "một lần" trong D25) |
| B08 | Một IANA timezone trong Settings; UTC RFC 3339 mili giây + ingest sequence. ADR-0007, AMD-B08, SC02/SC34 | **Đủ ở mức cơ chế** | **Owner phải xác nhận múi giờ thật.** `Asia/Ho_Chi_Minh` là giá trị tạm; nó không có DST nên hai quy tắc DST-01/DST-02 chưa kích hoạt. Đổi múi giờ ⇒ dựng lại mọi fixture lịch của PC03 và PC04 (INV-10) |
| B09 | Ngoại lệ hẹp cho chuỗi khớp định dạng mã. AMD-B09, `commands.yaml`, SC18/SC47 | **Đủ** — bộ đếm rate-limit nay có bảng thật (`telegram_link_attempt`) | Owner phê chuẩn AMD-B09; ba con số (định dạng, hạn 15 phút, 5 lần/giờ) là PROVISIONAL |
| B10 | `status` chỉ đọc; `run-now` không vượt `needs_user`; resume trong app; không lệnh thứ tư. AMD-B10, SC45 | **Đủ**, và được mở rộng: `run.resume` nay cũng cho `blocked` với `unblock_reason` bắt buộc (`PROV-PC00-04`) | Owner phê chuẩn AMD-B10 và `PROV-PC00-04` (chạm câu §5.4 bước 5 Owner đã đọc) |
| B11 | Online Backup API / `VACUUM INTO` + manifest + restore drill có khóa side effect. ADR-0005, AMD-B11, SC27/SC42/SC43/SC53 | **Đủ ở mức runbook** | **Chưa drill nào chạy.** Runbook là thiết kế, không phải bằng chứng (`backup-restore.md` §5.7). RPO 24 h / RTO 2 h là PROVISIONAL |
| B12 | Topology chốt; cạnh `COL→AW` bị gỡ. ADR-0001, AMD-B12, FE-07/FE-08, SC49 | **Gần đủ** | FE-08 — cạnh bị gỡ — nằm trong 26 cạnh **không có oracle mã lỗi** (CR-PC09-02). Và **REQ-OQ01 (xác nhận D09) vẫn CHẶN M0** |
| B13 | Secret theo từng task, TTL ngắn; CLI không tool/file/network ngoài inference; không cô lập được thì không bật. ADR-0010, `providers.yaml`, SC16/SC17 | **Đủ ở mức chính sách** | Chưa adapter nào qua probe. REQ-A5 (`KC`) — điều khoản từng nhà — chưa đọc. Mọi adapter `enabled=false`. **AC-16 hiện là `BLOCKED`, không phải `FAIL`** |
| B14 | Thuật toán mật độ đầy đủ, có ví dụ số tái lập được. `selection.md` §8, SC08/SC50 | **Đủ ở mức thuật toán** | Bảy tham số đều PROVISIONAL và cổng là REQ-A4 (`KC`, cần 3–4 kỳ thật, hiện có 0 kỳ). Thiếu dữ liệu ⇒ `insufficient_evidence`, **không** được gọi là "hướng nổi" |
| B15 | "0 trùng" thu hẹp về canonical identity đã biết; `identity_conflict` đếm riêng. AMD-B15, SC07/SC23 | **Đủ** | Owner phê chuẩn AMD-B15 (thu hẹp một chỉ tiêu ở SRC-SPEC §1.4 mà Owner đã đọc) |
| B16 | Ba loại phát biểu `author_claim`/`source_verified`/`ai_inference`; `comparator: unknown`. AMD-B16, `grounding.md`, SC11 | **Đủ** | Owner phê chuẩn AMD-B16 (AC-11 đọc lại). Rubric groundedness chưa chạy (E4) |
| B17 | Summary cho mục **được builder chọn**; `quality: partial` + pending list. AMD-B17, SC22 | **Đủ** | Owner phê chuẩn AMD-B17 (thu hẹp "cho mọi mục" của §2.1 mục 6) |

**Đánh giá tổng:** không blocker nào bị bỏ quên và không blocker nào bị tự đóng. 14 blocker có
amendment văn bản đã soạn đủ sáu trường; ba blocker (B06, B13, B14) bổ sung định nghĩa còn thiếu
mà không sửa câu chữ nào. Điểm cần chú ý nhất khi Owner đọc: **B08** (chọn sai múi giờ thì phải
dựng lại toàn bộ fixture lịch), **B12** (D09 chặn M0), **B13** (có thể làm một adapter bị tắt hẳn)
và **B14** (có thể làm khối "hướng đang nổi" trả `insufficient_evidence` thay vì một danh sách).

---

## 6. Sổ ĐX / KC — rà soát

### 6.1 Các mục P0 còn `ĐX` — không được tự promote

46 trong 234 dòng P0 mang status `ĐX` (đề xuất của người phỏng vấn, người dùng chưa chọn). Hai
dòng đáng chú ý vì chúng nằm trong danh mục MVP mà vẫn chưa được xác nhận:

- **`REQ-D09`** (Chrome profile riêng của dự án). Là câu hỏi mở số 1 của SRC-SPEC §13.1 và **chặn
  M0**. Toàn bộ topology của PC01 và protocol probe của PC05 mô tả theo D09 nhưng **không** promote
  nó. Nếu Owner từ chối, `collector-probe.md` và một phần `deployment.md` phải viết lại.
- **`REQ-D53`** (khối "hướng đang nổi" tính từ mật độ vector, vào MVP). Là mục P0 số 7 nhưng status
  `ĐX`. PC04 định nghĩa đầy đủ thuật toán nhưng **không** promote. Nếu Owner bỏ khối này khỏi MVP,
  `selection.md` §8 và SC08/SC50 thu hẹp đáng kể.

Các dòng `ĐX` khác (D08, D11, D12, D15, D16, D18, D21, D22, D23, D26, D33, D37, D38, D40, D42,
D43, D44, D50, D53…) đều đã được hiện thực hoá trong hợp đồng với nhãn giữ nguyên. **PC09 không
promote dòng nào.**

### 6.2 Các mục `KC` — cần kiểm chứng, có cổng

15 dòng mang status `KC`. Từng dòng có một cổng thật, không dòng nào bị coi là đã giải:

| REQ | Nội dung | Cổng | Trạng thái |
| --- | --- | --- | --- |
| `REQ-A1` | Phiên Chrome thu thập đều đặn ở mức đủ dùng | SP1 (5–10 đợt thật) | `NOT_RUN` |
| `REQ-A2` | Ngưỡng embedding tách được bài khớp tag | G7-X5 + §7.1 dưới đây | `NOT_RUN`; ngưỡng `0.8000` mang nhãn `PROVISIONAL_BOOTSTRAP` và `threshold_calibration_state='uncalibrated'` |
| `REQ-A3` | Model đa ngôn ngữ đủ tốt trên thuật ngữ khoa học | §7.2 | `NOT_RUN` |
| `REQ-A4` | Mật độ vector phát hiện được hướng nổi thật | G7 + §7.3 | `NOT_RUN`; cần 3–4 kỳ, hiện 0 |
| `REQ-A5` | Điều khoản từng nhà AI cho đường CLI/ACP | `cli-acp-probe.md` §6 | `NOT_RUN`; mọi adapter `enabled=false` |
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
fixture) — W5 viết lại ghi chú. Cả ba là `FIX_PROPOSED`, chờ A2 xác minh.

**Một CR mới: `CR-PC09-12`** — 8 tham chiếu cột không phân giải được mà bản tách `E0-04c` soi tới
lần đầu (§3.2); chủ sở hữu là W2, W3 và W4 theo từng file.

Bối cảnh, ba CR của đợt trước: **`CR-PC09-09`**
(`SAVE_ALREADY_EXISTS` chưa đăng ký, → W3/W2), **`CR-PC09-10`** (sáu tên cột không tồn tại được
gọi trong văn xuôi của tám file hợp đồng, → gói sở hữu từng file), **`CR-PC09-11`** (ghi chú
fixture `reporting/n-…` viết hai tên operation cũ dưới dạng token, → W5).

Một CR bị **mở lại**: **`CR-PC04-11`** — `event_order` của SC52 nay trích hai
operation authoritative `embedding.start_generation_rebuild` và `embedding.activate_generation`
(xem §3.3).

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

**Tổng: 107 CR** (`evidence/runs/cr_summary-20260907T023000Z.json`) — 90 từ PC00–PC08 (`cr_pc00_pc08_count`), 12 từ PC09, 5 từ
PC10. Phân bố trạng thái: ACCEPTED_AS_LIMITATION 1 · APPROVED 1 · CLOSED_CLAIMED 21 · OPEN 61 · RULED 23.

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
| `CR-PC00-01` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `precode/change-control.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-02` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-03` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-04` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-05` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-06` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-07` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-08` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-09` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-10` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-11` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `precode/decision-register.md`, `precode/review.md` |
| `CR-PC00-12` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/baseline.json`, `precode/decision-register.md` (+1 file) |
| `CR-PC00-13` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/review.md` |
| `CR-PC00-14` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/baseline.json`, `precode/review.md` |
| `CR-PC00-15` | OPEN |  | `evidence/handoffs/PC00-handoff.md`, `precode/review.md` |
| `CR-PC01-01` | OPEN |  | `contracts/errors.yaml`, `contracts/modules.yaml`, `contracts/ports.yaml` (+2 file) |
| `CR-PC01-02` | OPEN |  | `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json`, `agent-tasks/TC-scheduler-lease-claim.md` (+7 file) |
| `CR-PC01-03` | OPEN |  | `contracts/errors.yaml`, `contracts/ports.yaml`, `evidence/handoffs/PC01-handoff.md` (+1 file) |
| `CR-PC01-05` | OPEN |  | `acceptance/scenarios.yaml`, `contracts/data/entities.yaml`, `contracts/http/openapi.yaml` (+5 file) |
| `CR-PC01-06` | OPEN |  | `contracts/modules.yaml`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC01-07` | OPEN |  | `contracts/ports.yaml`, `evidence/handoffs/PC01-handoff.md`, `precode/review.md` |
| `CR-PC01-08` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/ops/secrets.md`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC08-handoff.md` (+1 file) |
| `CR-PC01-09` | **APPROVED** (Coordinator, A2-R1) | UNAUTHORIZED_COMMAND và RESTORE_UNVERIFIED là mã hợp lệ cho denied case nằm ngoài bảng bốn dòng R5-01 khi đặc tả gọi tên chúng | `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `contracts/modules.yaml` (+3 file) |
| `CR-PC01-10` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `contracts/modules.yaml` (+2 file) |
| `CR-PC01-11` | OPEN |  | `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/index.json` (+3 file) |
| `CR-PC01-12` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC01-handoff.md`, `precode/decision-register.md` (+1 file) |
| `CR-PC02-01` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-02` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-03` | OPEN |  | `contracts/data/entities.yaml`, `contracts/data/invariants.md`, `contracts/schemas/saved-snapshot.schema.json` (+3 file) |
| `CR-PC02-04` | OPEN |  | `contracts/data/entities.yaml`, `contracts/http/openapi.yaml`, `contracts/schemas/ingest-batch.schema.json` (+2 file) |
| `CR-PC02-05` | OPEN |  | `agent-tasks/TC-canonical-identity-merge.md`, `contracts/data/entities.yaml`, `contracts/errors.yaml` (+3 file) |
| `CR-PC02-06` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `agent-tasks/TC-canonical-identity-merge.md`, `agent-tasks/TC-report-coverage-publish-cas.md` (+9 file) |
| `CR-PC02-07` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `contracts/data/invariants.md`, `contracts/ops/backup-restore.md`, `evidence/handoffs/PC02-handoff.md` (+2 file) |
| `CR-PC02-08` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/identity/README.md`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-09` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-10` | OPEN |  | `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-11` | OPEN |  | `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-12` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-ingest-idempotent-ack-lost.md`, `contracts/data/entities.yaml`, `contracts/state/run.yaml` (+4 file) |
| `CR-PC02-13` | OPEN |  | `acceptance/fixtures/identity/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC02-handoff.md` (+1 file) |
| `CR-PC02-14` | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-15` | OPEN |  | `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-16` | OPEN |  | `contracts/data/entities.yaml`, `contracts/modules.yaml`, `evidence/handoffs/PC01-handoff.md` (+2 file) |
| `CR-PC02-17` | OPEN |  | `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `contracts/data/entities.yaml`, `contracts/telegram/commands.yaml` (+4 file) |
| `CR-PC02-18` | **ACCEPTED_AS_LIMITATION** (Coordinator, A2-R1) | cửa kiểm cột R4-01 áp cho fixture dạng `rows[]`; các fixture văn xuôi giữ nguyên và được khai là NOT_APPLICABLE_FREEFORM | `evidence/handoffs/PC02-handoff.md`, `evidence/handoffs/PC07-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+1 file) |
| `CR-PC02-19` | OPEN |  | `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-20` | OPEN |  | `evidence/handoffs/PC02-handoff.md`, `precode/review.md` |
| `CR-PC02-21` | OPEN |  | `contracts/data/entities.yaml`, `precode/review.md` |
| `CR-PC03-01` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/ports.yaml`, `evidence/handoffs/PC00-handoff.md`, `evidence/handoffs/PC01-handoff.md` (+4 file) |
| `CR-PC03-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-scheduler-lease-claim.md`, `contracts/errors.yaml`, `contracts/ports.yaml` (+9 file) |
| `CR-PC03-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/state/run.yaml`, `evidence/handoffs/PC03-handoff.md` (+1 file) |
| `CR-PC03-04` | OPEN |  | `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `agent-tasks/WALKTHROUGH.md`, `contracts/errors.yaml` (+6 file) |
| `CR-PC03-05` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/ai/tasks.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml` (+7 file) |
| `CR-PC03-06` | OPEN |  | `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/d-empty-period-coverage-only.json`, `contracts/reporting/time-and-tags.md` (+4 file) |
| `CR-PC03-07` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/state/delivery.yaml`, `evidence/handoffs/PC02-handoff.md` (+3 file) |
| `CR-PC04-01` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `evidence/handoffs/PC02-handoff.md` (+2 file) |
| `CR-PC04-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-backfill-pending-ledger.md`, `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md` (+4 file) |
| `CR-PC04-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `evidence/handoffs/PC02-handoff.md` (+2 file) |
| `CR-PC04-04` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/reporting/g-concurrent-publishers-cas.json`, `agent-tasks/TC-report-coverage-publish-cas.md`, `contracts/ports.yaml` (+6 file) |
| `CR-PC04-05` | OPEN |  | `agent-tasks/TC-ui-reports-detail.md`, `contracts/ai/grounding.md`, `contracts/ai/tasks.yaml` (+5 file) |
| `CR-PC04-06` | OPEN |  | `acceptance/fixtures/reporting/README.md`, `acceptance/scenarios.yaml`, `contracts/reporting/time-and-tags.md` (+3 file) |
| `CR-PC04-07` | OPEN |  | `agent-tasks/TC-backfill-pending-ledger.md`, `contracts/reporting/time-and-tags.md`, `contracts/ui/screens.yaml` (+3 file) |
| `CR-PC04-08` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-report-coverage-publish-cas.md`, `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md` (+6 file) |
| `CR-PC04-09` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/data/entities.yaml`, `contracts/reporting/time-and-tags.md`, `contracts/state/report.yaml` (+3 file) |
| `CR-PC04-10` | OPEN |  | `contracts/reporting/time-and-tags.md`, `evidence/handoffs/PC04-handoff.md`, `precode/review.md` |
| `CR-PC04-11` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC04-handoff.md` (+2 file) |
| `CR-PC05-01` | OPEN |  | `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/a-feed-layout-changed.json`, `agent-tasks/TC-collector-checkpoint-resume.md` (+10 file) |
| `CR-PC05-02` | OPEN |  | `contracts/http/openapi.yaml`, `evidence/handoffs/PC05-handoff.md`, `precode/review.md` |
| `CR-PC05-03` | OPEN |  | `agent-tasks/TC-x-feasibility-probe.md`, `contracts/ops/collector-probe.md`, `evidence/handoffs/PC05-handoff.md` (+5 file) |
| `CR-PC05-04` | OPEN |  | `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC05-handoff.md`, `precode/review.md` |
| `CR-PC05-05` | OPEN |  | `contracts/ports.yaml`, `evidence/handoffs/PC01-handoff.md`, `evidence/handoffs/PC05-handoff.md` (+1 file) |
| `CR-PC06-01` | OPEN |  | `agent-tasks/TC-analysis-once-per-generation.md`, `contracts/retry-policy.yaml`, `contracts/state/analysis.yaml` (+4 file) |
| `CR-PC06-02` | OPEN |  | `agent-tasks/TC-analysis-once-per-generation.md`, `contracts/data/entities.yaml`, `evidence/handoffs/PC02-handoff.md` (+3 file) |
| `CR-PC06-03` | OPEN |  | `agent-tasks/TC-analysis-adapter-validation.md`, `contracts/capabilities.yaml`, `evidence/handoffs/PC01-handoff.md` (+2 file) |
| `CR-PC06-04` | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-analysis-adapter-validation.md`, `evidence/handoffs/PC04-handoff.md` (+4 file) |
| `CR-PC06-05` | OPEN |  | `agent-tasks/TC-ui-reports-detail.md`, `evidence/handoffs/PC06-handoff.md`, `precode/review.md` |
| `CR-PC07-01` | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-telegram-linking-auth.md`, `contracts/telegram/commands.yaml` (+4 file) |
| `CR-PC07-02` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `contracts/data/entities.yaml` (+5 file) |
| `CR-PC07-03` | OPEN |  | `acceptance/scenarios.yaml`, `agent-tasks/TC-telegram-linking-auth.md`, `evidence/handoffs/PC07-handoff.md` (+1 file) |
| `CR-PC07-04` | OPEN |  | `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json`, `acceptance/scenarios.yaml` (+12 file) |
| `CR-PC07-05` | OPEN |  | `agent-tasks/TC-telegram-linking-auth.md`, `contracts/telegram/commands.yaml`, `evidence/handoffs/PC07-handoff.md` (+1 file) |
| `CR-PC07-06` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/telegram/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC04-handoff.md` (+3 file) |
| `CR-PC07-07` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc51-first-time-setup.json`, `agent-tasks/TC-analysis-adapter-validation.md` (+6 file) |
| `CR-PC07-08` | OPEN |  | `evidence/handoffs/PC07-handoff.md`, `precode/review.md` |
| `CR-PC07-09` | OPEN |  | `evidence/handoffs/PC07-handoff.md`, `precode/review.md` |
| `CR-PC07-10` | OPEN |  | `evidence/handoffs/PC07-handoff.md`, `evidence/handoffs/PC09-handoff.md`, `evidence/tools/README.md` (+1 file) |
| `CR-PC08-01` | OPEN |  | `acceptance/fixtures/recovery/README.md`, `acceptance/scenarios.yaml`, `evidence/handoffs/PC00-handoff.md` (+3 file) |
| `CR-PC08-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `agent-tasks/TC-backup-restore-drill.md`, `agent-tasks/TC-owner-auth-session.md`, `contracts/capabilities.yaml` (+6 file) |
| `CR-PC08-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`, `acceptance/scenarios.yaml`, `contracts/capabilities.yaml` (+12 file) |
| `CR-PC08-04` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `acceptance/scenarios.yaml` (+11 file) |
| `CR-PC08-05` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `agent-tasks/TC-backup-restore-drill.md`, `contracts/data/entities.yaml` (+4 file) |
| `CR-PC09-01` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/handoffs/PC04-handoff.md`, `evidence/handoffs/PC05-handoff.md` (+2 file) |
| `CR-PC09-02` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/handoffs/PC09-handoff.md`, `evidence/index.json` (+1 file) |
| `CR-PC09-03` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/state/run.yaml`, `evidence/handoffs/PC03-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+2 file) |
| `CR-PC09-04` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `contracts/state/analysis.yaml`, `evidence/handoffs/PC03-handoff.md`, `evidence/handoffs/PC09-handoff.md` (+2 file) |
| `CR-PC09-05` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `acceptance/scenarios.yaml`, `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-06` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-07` | RULED → FIX_PROPOSED | có ruling của Coordinator; chờ A2 xác minh | `evidence/handoffs/PC09-handoff.md`, `evidence/handoffs/PC10-handoff.md`, `precode/change-control.md` (+1 file) |
| `CR-PC09-08` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-09` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/gates.yaml`, `precode/review.md` |
| `CR-PC09-10` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-11` | OPEN |  | `evidence/handoffs/PC09-handoff.md`, `precode/review.md` |
| `CR-PC09-12` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC09-handoff.md`, `precode/gates.yaml`, `precode/review.md` |
| `CR-PC10-01` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-analysis-adapter-validation.md`, `agent-tasks/TC-analysis-once-per-generation.md`, `agent-tasks/TC-backfill-pending-ledger.md` (+21 file) |
| `CR-PC10-02` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/TC-collector-checkpoint-resume.md`, `agent-tasks/WALKTHROUGH.md`, `contracts/errors.yaml` (+10 file) |
| `CR-PC10-03` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `agent-tasks/WALKTHROUGH.md`, `contracts/capabilities.yaml`, `evidence/handoffs/PC01-handoff.md` (+2 file) |
| `CR-PC10-04` | OPEN |  | `agent-tasks/WALKTHROUGH.md`, `evidence/handoffs/PC10-handoff.md`, `precode/change-control.md` (+1 file) |
| `CR-PC10-05` | CLOSED_CLAIMED | gói liên quan tự khai đã đóng; chưa xác minh độc lập | `evidence/handoffs/PC10-handoff.md`, `precode/review.md` |

## 9. Readiness theo module

Tiêu chí `READY_FOR_CARD`: (a) module có owner, port vào/ra và cạnh bị cấm đã khai; (b) mọi
operation nó sở hữu có schema, auth, transaction, idempotency, lỗi và scenario; (c) không blocker
nào còn mở **chạm trực tiếp** vào hành vi của nó; (d) không finding audit nào đang mở trong file
của nó; (e) mọi tham số bắt buộc có giá trị (không `PLACEHOLDER_KC`); (f) scenario của nó có
fixture.

Sau đợt FIX5, điều kiện (f) đúng với **mọi** module — không scenario nào còn thiếu fixture — và
điều kiện (a)/(b) đúng với mọi module. Nhưng điều kiện (c) vẫn **sai với mọi module** vì B01–B17
đều `OPEN`, và điều kiện (d) vẫn sai — không phải vì A2 chưa chạy, mà vì bốn finding
`F-A2R2-01…04` của A2-R2 còn `OPEN` và bản sửa cho chúng chưa được xác minh lại (§4.1). Nên
**không module nào đạt
`READY_FOR_CARD` vô điều kiện**. Bảng dưới ghi trạng thái **có điều kiện**: mỗi module đạt được gì
và còn chờ đúng cái gì.

| Module | Chạy ở | Trạng thái | Chặn bởi |
| --- | --- | --- | --- |
| `MOD-web-ui` | browser | READY_FOR_CARD *(có điều kiện)* | Nâng từ BLOCKED: `ui/sc10-…` và `ui/sc51-…` cấp fixture render, `screens.yaml` nay trích `REQ-S4-01`, `-08`, `-09`, `-10` và `REQ-S5.1-01..03`. Còn chờ B10 (resume) |
| `MOD-backend-api` | server | READY_FOR_CARD *(có điều kiện)* | Chỉ chờ phê chuẩn B-chung. 54 operation HTTP có wire contract 1:1, `ErrorEnvelope` set-equal `errors.yaml`, CSRF trên mọi owner mutation |
| `MOD-auth-service` | server | READY_FOR_CARD *(có điều kiện)* | Tham số phiên (Argon2id, idle 12 h, absolute 30 d) là PROVISIONAL, cần Owner |
| `MOD-settings-service` | server | BLOCKED | B08 (timezone thật), `REQ-OQ03` (provider/model cụ thể — **không có giá trị mặc định**, `OWNER_DECISION_REQUIRED`) |
| `MOD-tag-service` | server | BLOCKED | B01 (mốc freeze tag), B04 (backfill keyed theo chữ chuẩn hóa), `REQ-OQ04` (N ngày) |
| `MOD-scheduler` | server | BLOCKED | B08 (timezone quyết định mọi mốc), `REQ-OQ06` (lịch thật). SC34 nay có fixture (`collection/j-…`) nhưng chỉ thực sự kích hoạt nếu Owner chọn múi giờ CÓ DST |
| `MOD-job-service` | server | BLOCKED | B02 (mô hình trạng thái run), B10 (resume). SC33/SC35 nay có fixture |
| `MOD-ingest-service` | server | READY_FOR_CARD *(có điều kiện)* | B05 đã có phương án đủ; chờ phê chuẩn AMD-B05 |
| `MOD-identity-service` | server | READY_FOR_CARD *(có điều kiện)* | B06 và B15 chưa phê chuẩn nhưng đã hiện thực hoá đầy đủ với fixture và oracle |
| `MOD-research-connector` | server | **BLOCKED (cứng)** | `REQ-A6` `KC`: bốn giá trị rate-limit là `null`/`PLACEHOLDER_KC`. PC05 tự ghi module này **không** được coi là `CONTRACT_READY` cho tới khi chúng được điền. Cần đọc tài liệu ngoài — phiên này không có mạng |
| `MOD-embedding-service` | server | BLOCKED | `REQ-OQ09` (model cụ thể), `REQ-A3` `KC`. SC52 nay có mặt dương với fixture (`reporting/n-…`) và trích đúng hai operation authoritative |
| `MOD-analysis-service` | server | READY_FOR_CARD *(có điều kiện)* | B07 chưa phê chuẩn; `PROV-PC03-04` (tự chạy lại một lần từ `unknown_attempt`) cần Owner soi |
| `MOD-report-service` | server | BLOCKED | B01, B04, B14, B17 đều chạm trực tiếp; tham số mật độ đều PROVISIONAL với cổng `REQ-A4` |
| `MOD-saved-service` | server | READY_FOR_CARD *(có điều kiện)* | `F-PC00-02` (hoãn export) chờ Owner |
| `MOD-delivery-service` | server | BLOCKED | B03 (`delivery.unknown` sửa AC-14 — cần Owner duyệt amendment) |
| `MOD-telegram-adapter` | server | **BLOCKED (cứng)** | `CR-PC07-04`: giới hạn định dạng Telegram vẫn `KC` (không có mạng để đọc Bot API). Chặn `CONTRACT_READY` của `telegram/delivery.md` §3.4. Cộng B03, B09, B10 |
| `MOD-secret-service` | server | BLOCKED | B13 chưa phê chuẩn; `REQ-A5` `KC` |
| `MOD-data-admin-service` | server | **BLOCKED (cứng)** | `PROV-PC00-01`/`PROV-PC01-03`: phạm vi **loại trừ** của `data.purge_all` là `OWNER_DECISION_REQUIRED`. SC32/SC44 nay có fixture (`recovery/k-…`, `l-…`) nên CƠ CHẾ đã khóa được — nhưng fixture không khóa được DANH SÁCH LOẠI TRỪ. `CR-PC01-05` (cascade) vẫn mở |
| `MOD-data-store` | server | READY_FOR_CARD *(có điều kiện)* | Partial UNIQUE index và STORED generated column vẫn là **giả định chưa kiểm trên SQLite thật**; cần E1 sau khi chốt stack |
| `MOD-backup-service` | server | BLOCKED | B11 chưa phê chuẩn; RPO/RTO PROVISIONAL; **chưa drill nào chạy**. SC53 nay có mặt dương với fixture (`recovery/m-…`) |
| `MOD-backup-cli` | server | BLOCKED | như trên; `PROV-PC01-04` |
| `MOD-health-service` | server | READY_FOR_CARD *(có điều kiện)* | Ngưỡng readiness 30/90/900/1800 s là PROVISIONAL, chưa đo thật |
| `MOD-x-collector` | máy cá nhân | **BLOCKED (cứng)** | `REQ-OQ01` (xác nhận D09) **CHẶN M0**; `REQ-A1` và `REQ-A7` đều `KC`; SP1 chưa chạy |
| `MOD-analysis-worker` | máy cá nhân | BLOCKED | B13; `REQ-A5` `KC`; mọi adapter `enabled=false` |
| `MOD-ai-adapter` | máy cá nhân | **BLOCKED (cứng)** | B13: không chứng minh được cô lập tool/file/network thì adapter **không được bật**. Chưa probe nào chạy. **AC-16 là `BLOCKED`, không phải `FAIL`** |

**Tổng, đếm từ chính bảng trên (25 dòng): 9 module `READY_FOR_CARD` có điều kiện, 16 `BLOCKED`,
trong đó 5 bị chặn cứng** (`module_table_rows`, `module_ready`, `module_blocked`,
`module_hard_blocked` — parse cơ học từ bảng, không viết cạnh bảng). Bản trước ghi "10 ready / 15
blocked" trong khi bảng của chính nó nói 9 / 16 (`F-A2R1-02`). Hai thay đổi so với bản FIX1:

- `MOD-web-ui` **BLOCKED → READY_FOR_CARD (có điều kiện)**: lý do chặn của bản trước là thiếu
  fixture render và bốn dòng `REQ-S4-01`/`-08`/`-09`/`-10` mồ côi; ruling R5-02 và R5-03
  đóng cả hai.
- `MOD-data-admin-service` **vẫn chặn cứng** dù nay có đủ fixture — vì cái chặn nó không bao giờ là
  fixture, mà là một câu hỏi chỉ Owner trả lời được: purge xóa những gì và **không** xóa những gì.

Bốn module chặn cứng còn lại đều chặn vì cùng một loại nguyên nhân — một `KC` cần dữ liệu từ thế
giới bên ngoài (`REQ-A6`, `CR-PC07-04`, `REQ-A5`+B13, `REQ-OQ01`+`REQ-A1`) — chứ không vì thiếu
hợp đồng. Không lượng công việc soạn thảo nào gỡ được chúng.

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

Tại thời điểm chạy bản này lệnh đó trả **`PC10-PIN-FCW4f-20260907`**, và **18/18 card khai cùng một epoch**
(`card_pin_current`, `card_pin_declared`, `card_pin_unanimous`). Bản trước ghi
`PC10-PIN-FCW4-20260907`, đã bị thay lần lượt bởi `FCW4b`, `FCW4c`, `FCW4d`, `FCW4e` rồi `FCW4f` — `F-A2R1-03` bắt đúng điểm đó, và
lý do nó lệch được là vì nó được chép chứ không được đọc. Card trích các file của PC09 **theo
đường dẫn và SC id, không theo hash** (ruling R5-07) — cách pin đúng, vì `acceptance/scenarios.yaml`
đổi ở chính đợt này và một hash được pin sẽ lệch ngay. **W7 sẽ re-pin một lần nữa sau gói này**,
nên giá trị ở trên là giá trị tại thời điểm chạy — lệnh `grep` bên trên luôn là nguồn đúng.

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
- **53 / 53 scenario được ít nhất một card trích dẫn.** Không scenario nào mồ côi phía card.
- Kiểm tra này **nên trở thành một check E0 thường trực** khi `agent-tasks/` ổn định. Tôi không
  thêm nó vào `e0_check.py` ở đợt này vì `agent-tasks/` nằm ngoài read set của packet PC09 gốc và
  PC10 vẫn đang thay đổi; đề nghị Coordinator giao nó cho lượt sau. Đây là `CR-PC09-08`.


## 10. Quyết định `PROVISIONAL` đang chờ Owner — danh sách hợp nhất

`precode/owner-decision-request.md` là phiếu trả lời chính thức (24 mục). Bản này **không nhân
bản** nó; nó chỉ đối chiếu và chỉ ra mục nào chặn cái gì. Nếu hai bản lệch nhau,
`owner-decision-request.md` thắng.

| Nhóm | ID | Chặn |
| --- | --- | --- |
| **`OWNER_DECISION_REQUIRED` — không có giá trị tạm** | `PROV-PC00-01` / `PROV-PC01-03` (phạm vi loại trừ của `data.purge_all`) | `MOD-data-admin-service`, SC44 |
| | `REQ-OQ03` (provider và model cụ thể) | `MOD-settings-service`, M3 |
| **Chặn mốc triển khai** | `REQ-OQ01` (xác nhận D09 — Chrome profile riêng) | **M0**, SP1, `MOD-x-collector` |
| | `REQ-OQ02` (chọn stack; khuyến nghị A) | **M1**, G5, mọi task card của PC10 |
| **14 amendment cần phê chuẩn** | `AMD-B01`, `-B02`, `-B03`, `-B04`, `-B05`, `-B07`, `-B08`, `-B09`, `-B10`, `-B11`, `-B12`, `-B15`, `-B16`, `-B17` | 84 dòng registry, G0–G4 |
| **Ba blocker không có amendment** | B06, B13, B14 | identity model; bật/tắt adapter; khối "hướng đang nổi" |
| **Quyết định kỹ thuật do PC00 chốt tạm** | `PROV-PC00-02` (`CSRF_REJECTED`), `PROV-PC00-03` (`data.purge_all` hai pha + SC44), `PROV-PC00-04` (`run.resume` từ `blocked`) | `PROV-PC00-04` chạm câu §5.4 bước 5 Owner đã đọc |
| **Quyết định của PC01** | `PROV-PC01-01` (`CAPABILITY_DENIED`), `-02` (unlink là app action), `-04` (`MOD-backup-cli`), `-05` (caller của `identity.record_alias`), `-06` (`MOD-data-admin-service`) | |
| **Quyết định của PC02** | 8 giới hạn ingest/snapshot, hai quy tắc chuẩn hóa DOI/arXiv, `analysis_key` không gồm provider/model | `CR-PC02-04`, `CR-PC02-05`, `CR-PC02-17` |
| **Quyết định của PC03** | `PROV-PC03-01` (DST-01/DST-02), `-04` (`analysis_unknown_attempt_auto_rerun = 1`), 41 ngân sách, `run_now_active_run_policy = coalesce`, `storage.maintenance` | `PROV-PC03-04` là chỗ chính PC03 **xin Auditor soi kỹ**; A1-R2 đã đánh giá là hợp lý nhưng đó là đánh giá kỹ thuật, không phải phê chuẩn của Owner |
| **Quyết định của PC04** | 8 mục ở handoff §7.3, gồm `PROV-PC04-06` (ngưỡng `0.8000` `PROVISIONAL_BOOTSTRAP`) và `PROV-PC04-09` (kỳ rỗng phương án (b)) | `PROV-PC04-09` **trái khuyến nghị (a) của Coordinator** và cần xác nhận hoặc bác |
| **Quyết định của PC05** | Thiết kế URL 50 path, ánh xạ mã lỗi → HTTP status, `x-transport-limits`, ngưỡng probe và go/no-go | Ngưỡng GO-2 (challenge ≤ 1 mỗi 5 đợt) là ngưỡng về **trải nghiệm**: cao hơn thì sản phẩm "tự chạy" thành sản phẩm "gọi người" |
| **Quyết định của PC06** | 8 mục ở handoff §7.3, gồm `confidence` là enum rời rạc, `usage.unknown ⇒ ba trường null`, ngưỡng rubric G1/G2 = 1.00 | |
| **Quyết định của PC07** | Định dạng/hạn/rate-limit mã liên kết, giờ yên lặng (không có), `telegram_update_max_age` | `CR-PC07-01`, `CR-PC07-05` |
| **Quyết định của PC08** | Argon2id, phiên 12 h/30 d, token 256 bit, rotation 180 ngày, RPO 24 h / RTO 2 h, retention backup | PC08 khuyến nghị hẹp: "nếu chỉ đổi một thứ thì đổi phiên đăng nhập 12 giờ" |

**Hai hệ quả Owner phải biết TRƯỚC khi trả lời `PROV-PC00-01`:** (1) nếu purge xóa credential đăng
nhập thì Owner có thể tự khóa mình ra ngoài app, vì D05 cấm signup và cấm quên-mật-khẩu tự động;
(2) dữ liệu đã purge **vẫn còn trong backup** cho tới khi các bản backup đó bị xóa — "xóa toàn bộ"
không đồng nghĩa "không còn ở đâu nữa".

---

## 11. Definition of Ready của SRC-PLAN §17 — đối chiếu từng dòng

| # | Điều kiện | Đạt? | Bằng chứng / thiếu gì |
| --- | --- | --- | --- |
| 1 | Spec snapshot/hash và registry nguyên tử tồn tại | ✅ | `precode/source/*` byte-identical; 246 dòng registry |
| 2 | Tất cả XN/UQ/P0 có mapping; ĐX/KC còn lại có trạng thái và gate rõ | ✅ | `acceptance/traceability.csv`, 0 ORPHAN; §6 bảng KC |
| 3 | B01–B17 được giải hoặc explicit scoped block | ❌ | Cả 17 `OPEN`; phương án đều `PROVISIONAL`. **Không Worker nào gỡ được** |
| 4 | Mỗi module có ownership, port và denied edges; negative cases đủ | ✅ | **36 / 36 cạnh** có denied case với mã lỗi đã pin (ruling R5-01) và một fixture 36 sự kiện |
| 5 | Mỗi operation có schema, auth, transaction, idempotency, concurrency, error và evidence | ✅ | 85 operation; **0 thiếu `scenario_refs`, 0 thiếu `error_codes`, 0 mutation thiếu khai báo idempotency** (`dor5`, sinh từ `ports.yaml` cùng lượt với các số khác); 54 operation HTTP có wire contract. Năm ngoại lệ mà `F-A2R1-09` nêu tên đã được **đóng** ở FIX6/FIX7: `auth.logout` và `auth.get_session` → SC40/SC51, `save.export` → SC12, `research.get_connector_health` và `health.get_liveness` → `INTERNAL` |
| 6 | Mỗi mã lỗi có trạng thái đích, điều kiện phục hồi và hành vi bị cấm | ✅ | 28 mã, mỗi mã đủ 10 trường; 28/28 có scenario |
| 7 | Coverage/backfill/pending/tag version và identity/analysis/Saved có oracle cho race/crash | ✅ | SC08, SC13, SC21, SC22, SC28, SC37, SC38 |
| 8 | Telegram unknown, CLI capability, backup WAL/restore và secrets không còn mô tả mơ hồ | ⚠️ | Ba trong bốn đủ. **Giới hạn định dạng Telegram vẫn `KC`** (CR-PC07-04) |
| 9 | AC-01–AC-18 và các SC bổ sung có fixtures/oracles, loại bằng chứng và amended AC đúng nguồn | ✅ | 56 scenario, mỗi cái có oracle, cấp bằng chứng và **ít nhất một fixture**; 86 fixture trên 9 thư mục (`scenarios`, `fixtures`, `fixture_directories`) |
| 10 | E0 đã chạy thật và có manifest; E1–E4 chưa chạy ghi NOT_RUN | ✅ | `evidence/index.json`; **22/22 PASS, 0 vi phạm, exit 0**; E1–E4 `NOT_RUN` với 32 placeholder tường minh |
| 11 | Card triển khai pin baseline, paths/stack, contracts và proof obligations | ❌ | 18 card đều pin cùng một epoch — **tên epoch được in ở §9.1 và chỉ ở đó** (`F-A2R3-01`: dòng này từng nhắc lại nó và đã sai ba epoch liên tiếp); **stack vẫn chưa chọn** (`REQ-OQ02`), nên đường dẫn build/test trong card chưa thể đúng |
| 12 | Readiness report liệt kê module nào READY/BLOCKED | ✅ | §9 |

**Đếm từ chính bảng trên: 9 ✅, 1 ⚠️, 2 ❌** trên 12 dòng (`dor`, parse cơ học). Bản trước ghi
"10 đạt, 0 đạt một phần" trong khi bảng của chính nó có một ⚠️ và câu ngay sau đó thừa nhận điều
đó — `F-A2R1-02`. Dòng #5 quay lại ✅ ở bản này: năm ngoại lệ mà `F-A2R1-09` nêu đã được đóng ở FIX6/FIX7, và danh
sách ngoại lệ của dòng nay được **sinh từ `ports.yaml`** cùng lượt với các con số khác — nên một
lỗ hổng được vá sẽ tự đóng dòng, thay vì để lại một cảnh báo cũ (`F-A2R2-02`).

Hai dòng ❌ (#3 và #11) **không phải việc của một Worker**: một cần Owner phê chuẩn B01–B17, một
cần Owner chọn stack (`REQ-OQ02`). Dòng ⚠️ duy nhất còn lại (#8) cần đọc tài liệu Bot API — việc
cần mạng, không cần thêm soạn thảo.

Con số này đi 7/3/2 → 10/0/2 (sai) → 8/2/2 → **9/1/2**, và mỗi lần nó đổi là vì một dòng của
bảng đổi. Cổng tự kiểm so dòng tổng với bảng chạy sau **mỗi** lần sửa; nó bắt được đúng lần lệch
này khi tôi sửa dòng #5 mà quên dòng tổng.

---

## 12. Tuyên bố

**Claim của bản này: `DRAFT_FOR_REVIEW`.** Không hơn.

Cụ thể **không** được thiết lập:

- `CONTRACT_READY` cho bất kỳ phạm vi nào — B01–B17 `OPEN`; **A2-R2 PASS tổng thể** nhưng để lại
  bốn finding LOW `FIX_PROPOSED` mà chưa ai xác minh bản sửa (§4.1); hai module tự khai là chưa
  sẵn sàng (research connector vì `REQ-A6`, Telegram vì `CR-PC07-04`); . Việc E0 nay đạt **22/22, 0 vi phạm** **không** thay thế được
  những điều đó: một bộ hợp đồng tự nhất quán vẫn là một bộ hợp đồng chưa được ai độc lập kiểm và
  chưa chạy dòng code nào;
- bất kỳ nhãn nào từ `IMPLEMENTATION_VERIFIED` trở lên — chưa có một dòng code nào;
- bất kỳ khẳng định nào về X, Telegram, provider AI, CLI/ACP hay hành vi SQLite thật — chưa thực
  thi gì;
- rằng bản này là một audit độc lập — nó là `SELF_VALIDATION` của chính người viết một phần corpus.

### 12.1 Phát biểu có điều kiện: phạm vi nào thành `CONTRACT_READY`, khi nào

Không phải một lời hứa, mà một danh sách điều kiện đo được. Mỗi dòng chỉ có hiệu lực khi **mọi**
điều kiện của chính nó đúng.

| Phạm vi | Sẽ đạt `CONTRACT_READY` khi tất cả những điều sau đúng |
| --- | --- |
| **Ranh giới và quyền** (`modules.yaml`, `capabilities.yaml`, `ports.yaml`) | (a) ~~`CR-PC09-02`~~ **đã đóng** — cả 36 cạnh có mã lỗi đã pin theo bảng R5-01; (b) Owner phê chuẩn AMD-B12 và B13; (c) `REQ-OQ01` (D09) có câu trả lời; (d) A2 xác nhận trên epoch mới |
| **Dữ liệu và identity** (`entities.yaml`, `identity.md`, `invariants.md`, `target`/`ingest-batch` schema) | (a) Owner phê chuẩn AMD-B05, AMD-B15 và B06; (b) `CR-PC01-05` đóng (danh sách cascade cho hai thao tác xóa); (c) ~~SC32 có fixture~~ **đã có**; (d) partial UNIQUE index và STORED generated column được kiểm trên SQLite thật (E1) |
| **Workflow và trạng thái** (`state/*.yaml`, `errors.yaml`, `retry-policy.yaml`) | (a) ~~`CR-PC09-04`~~ **đã đóng** (R5-04); (b) Owner phê chuẩn AMD-B02, AMD-B10 và `PROV-PC03-04`; (c) ~~SC33–SC36 có fixture~~ **đã có** |
| **Báo cáo và thời gian** (`time-and-tags.md`, `selection.md`, `report.schema.json`) | (a) Owner phê chuẩn AMD-B01, AMD-B04, AMD-B17 và B14; (b) Coordinator/Owner xác nhận hoặc bác `PROV-PC04-09` (kỳ rỗng phương án (b)); (c) `REQ-OQ04` (N ngày) có câu trả lời. **Ghi chú:** phạm vi này đạt `CONTRACT_READY` được ngay cả khi ngưỡng còn `uncalibrated` — hợp đồng đóng không đòi tham số đã hiệu chỉnh; cái bị cấm là **tuyên bố đạt chỉ tiêu §1.4** khi còn `uncalibrated` |
| **Collector và paper connector** (`openapi.yaml`, `collector-probe.md`, worker/receipt schema) | (a) bốn giá trị `research_connector_rate_limit` được điền từ tài liệu chính thức (`REQ-A6`); (b) `REQ-OQ01` có câu trả lời; (c) Owner chấp nhận ngân sách/stop/go-no-go của SP1; (d) một validator OpenAPI 3.1 chạy sạch trên `openapi.yaml` |
| **AI và grounding** (`tasks.yaml`, `providers.yaml`, `grounding.md`, `analysis-result.schema.json`) | (a) Owner phê chuẩn AMD-B07, AMD-B16 và B13; (b) `REQ-A5` được giải cho **ít nhất một** provider (đọc điều khoản, ghi lại); (c) ít nhất một adapter qua probe cô lập của `cli-acp-probe.md`. Cho tới đó **AC-16 là `BLOCKED`, không phải `FAIL`** |
| **App, Save và Telegram** (`screens.yaml`, `commands.yaml`, `telegram/delivery.md`, `saved-snapshot.schema.json`) | (a) `CR-PC07-04` đóng — giới hạn định dạng Telegram được đọc từ tài liệu Bot API và ghi lại (**vẫn mở, cần mạng**); (b) Owner phê chuẩn AMD-B03, AMD-B09, AMD-B10; (c) ~~SC10 có fixture render~~ **đã có**; (d) `CR-PC07-01` có câu trả lời |
| **Vận hành: secrets, boundary, backup** (`secrets.md`, `internet-boundary.md`, `backup-restore.md`) | (a) Owner trả lời `PROV-PC00-01` (phạm vi loại trừ của purge); (b) Owner chốt RPO/RTO và retention; (c) ~~`CR-PC09-05`~~ **đã đóng** (R5-05); (d) ~~SC44 và SC53 có fixture~~ **đã có**. Một drill restore thật **không** phải điều kiện của `CONTRACT_READY` — nó là điều kiện của G6 |

### 12.2 Điều kiện chung cho MỌI dòng trên

Không phạm vi nào ở trên đạt `CONTRACT_READY` chừng nào:

1. bất kỳ blocker nào trong B01–B17 **chạm vào phạm vi đó** còn `OPEN` trong
   `agent_profile/registry.json`;
2. `evidence/tools/e0_check.py` còn thoát với mã khác 0;
3. còn một finding audit độc lập `OPEN` hoặc `FIX_PROPOSED` trong file thuộc phạm vi đó;
4. lượt xác minh độc lập trên epoch chứa các bản sửa **chưa** diễn ra — và người xác minh **không
   được** là người viết bản sửa (protocol §8). **Tại bản này điều kiện 4 sai với MỌI phạm vi:** A2
   đã chạy trên epoch 4 và kết luận PC09 **FAIL**; bản sửa cho 11 finding của nó chưa được ai độc
   lập kiểm. Không dòng nào của bảng §12.1 được coi là đã đạt, bất kể các điều kiện riêng của nó.

---

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
9. **5 AUDIT_REPORT độc lập nằm ngoài repo** (thư mục scratch của Coordinator: `A1-R1-report.md`, `A1-R2-report.md`, `A1-R3-report.md`, `A2-R1-report.md`, `A2-R2-report.md` —
   `audit_reports`, đếm từ đĩa). Bản này trích kết luận của chúng; nó không sao chép chúng vào
   repo và không thay thế chúng. Trạng thái audit được nêu ở **một chỗ duy nhất, §4.1**; mọi mục
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
13. **Thiết kế đánh giá ở §7 chưa được Owner khóa.** Cho tới khi khóa, nó là một đề xuất; một rubric
   chưa khóa không ngăn được việc chỉnh số sau khi nhìn kết quả — đó chính là điều nó tồn tại để
   ngăn.
