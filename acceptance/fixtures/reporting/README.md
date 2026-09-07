---
contract_id: CT-fixtures-reporting
version: 0.1.0
status: accepted
owner_role: reporting contract owner
source_refs:
  - "SRC-PLAN §11 PC04 (danh mục fixture bắt buộc)"
  - "SRC-PLAN §13 (ma trận truy vết AC → SC)"
  - "SRC-PLAN §9.2, §9.3"
  - "SRC-SPEC §8.2 (ví dụ thời gian cụ thể), §8.3, §10.1, §10.4"
  - "SRC-SPEC §12 AC-02, AC-05, AC-06, AC-08, AC-09, AC-10"
requirement_refs:
  [REQ-CTAG, REQ-D23, REQ-D24, REQ-D25, REQ-D27, REQ-D28, REQ-D29, REQ-D30, REQ-D48,
   REQ-D53, REQ-D54, REQ-D57, REQ-AC02, REQ-AC05, REQ-AC06, REQ-AC08, REQ-AC09, REQ-AC10,
   REQ-A2, REQ-A4, REQ-OQ04]
decision_refs: [B01, B04, B06, B07, B14, B15, B17, AMD-B01, AMD-B04, AMD-B08, AMD-B17, ADR-0004]
invariant_refs: [I04, I05, I06, I07, I09, I12, I13, I17]
producers: [MOD-report-service]
consumers: [MOD-web-ui, MOD-telegram-adapter, MOD-delivery-service, MOD-analysis-service, MOD-embedding-service, MOD-tag-service]
dependencies:
  - contracts/reporting/time-and-tags.md
  - contracts/reporting/selection.md
  - contracts/schemas/report.schema.json
  - contracts/schemas/target.schema.json
  - contracts/data/entities.yaml
  - contracts/data/identity.md
  - contracts/ports.yaml
scope: >-
  Bộ fixture cho tag freeze, coverage, pending/late, backfill, first-announcement và mật độ
  vector. Đây là DỮ LIỆU VÀO + ORACLE, **không phải test đã chạy**. Ở gói PC04 chỉ E0
  (validate tĩnh) được thực hiện; E1–E4 là `NOT_RUN`.
verification: "EV-PC04-01 (parse + report.schema.json), EV-PC04-02 (ví dụ mật độ), EV-PC04-03 (tham chiếu operation/entity), EV-PC04-04 (coverage nối liền)."
claim_ceiling: CONTRACT_READY
ratification_ref: OD-20260907-01
ratified_by: AUTH-OWNER-20260907-02
ratified_at: "2026-09-07"
ratification_scope: >-
  A2-R4 tuyên bố phạm vi "Reporting and time" đủ điều kiện `CONTRACT_READY`; Owner phê chuẩn
  B01–B17 và 8 tham số của PC04 cộng phương án kỳ rỗng (b) (OD-20260907-01 mục 22).
  PROV-PC04-01..09 nay là `ACCEPTED (OD-20260907-01)` với tư cách **giá trị làm việc**.
ratification_limits: >-
  Owner phê chuẩn GIÁ TRỊ LÀM VIỆC, KHÔNG phải kết quả hiệu chỉnh. Hai thứ vẫn chưa được đo và
  KHÔNG được đọc là đã kiểm chứng: (1) ngưỡng similarity giữ nguyên
  `threshold_calibration_state: uncalibrated` cho tới khi REQ-A2 chạy; (2) mọi tham số mật độ
  giữ nguyên cổng REQ-A4. `CONTRACT_READY` ở đây nghĩa là NGỮ NGHĨA và ORACLE đã đóng, không
  nghĩa là các con số đã được chứng minh là tốt.
---

# Fixture reporting — chỉ mục và cách dùng

> **Cảnh báo baseline.** `contracts/data/entities.yaml` đã đổi trong lúc gói PC04 chạy
> (`88b2482e…` → `921a5927…` → `2235564f…`), và `contracts/errors.yaml`, `contracts/retry-policy.yaml`,
> `contracts/state/*` xuất hiện giữa chừng. Bộ fixture này đã được căn lại theo bản mới
> (mã lỗi CAS là `CONFLICT`; kỳ rỗng để lại một hàng `report(status='aborted')`; sổ
> `first_announced_ledger` dùng cột `canonical_work_id` / `first_report_id` / `merge_audit_id`
> / `superseded_by_merge_id` nguyên văn). Chi tiết ở `evidence/handoffs/PC04-handoff.md`.
>
> **CR-PC03-06** (kỳ rỗng để lại hàng report hay không) đã được PC04 quyết ở
> `contracts/reporting/time-and-tags.md` §4.7.1: **có**, `status='aborted'` +
> `abort_reason='empty_period'`, vì `report_build_id` cần một mỏ neo bền cho replay. Đây là
> chỗ PC04 không theo khuyến nghị của Coordinator; lý do và cách đảo nằm ở §4.7.1.

> **Ceiling của thư mục này.** README **và cả 14 fixture** đều mang
> `claim_ceiling: CONTRACT_READY` + `ratification_ref: OD-20260907-01` (F-A2R5-04: một index
> không được claim cao hơn file nó liệt kê). Header hợp đồng của một fixture là **khối khóa cấp
> cao nhất** của chính file JSON đó — đó là dạng header mà ruling R-05 cho phép fixture dùng, và
> là nơi `ratification_ref` được đọc.
>
> Ceiling này nói **dữ liệu vào và oracle đã đóng**. Nó **không** nói fixture đã chạy: cả 14 file
> vẫn mang `evidence_status: NOT_RUN`, và E1–E4 chưa chạy lần nào. Ngưỡng similarity vẫn
> `uncalibrated` (REQ-A2), tham số mật độ vẫn sau cổng REQ-A4.

## 1. Danh mục

| File | Fixture ID | Kiểm tra điều gì | Scenario | Invariant | Quyết định |
| --- | --- | --- | --- | --- | --- |
| `a-tag-removed-before-publish.json` | FX-RP-A | Bỏ tag trước publish → mục bị loại, dữ liệu vẫn ở kho | SC05 | I05 | B01, AMD-B01 |
| `b-tag-removed-then-readded-reuse-analysis.json` | FX-RP-B | Thêm lại tag → dùng lại analysis, provider call delta = 0 | SC06 | I04, I05 | B01, B07 |
| `c-tag-changed-after-publish-before-send.json` | FX-RP-C | Đổi tag sau publish trước khi Telegram gửi → nội dung không đổi | SC19 | I05, I09 | B01, B03 |
| `d-empty-period-coverage-only.json` | FX-RP-D | Kỳ rỗng → coverage record, không digest, không report hiển thị; quyết định CR-PC03-06 | SC08, SC15 | I06, I13 | B04, AMD-B04, CR-PC03-06 |
| `e-late-analysis-pending-then-late-discovery.json` | FX-RP-E | Analysis về muộn → pending rồi "phát hiện muộn" kỳ sau | SC22 | I06 | B04, B17 |
| `f-three-offline-periods-one-catchup.json` | FX-RP-F | Ba kỳ offline → một run bù, một cửa sổ coverage; tie-break cùng mili giây | SC02, SC08 | I06 | B04, B08 |
| `g-concurrent-publishers-cas.json` | FX-RP-G | Hai publisher → một thắng CAS, bên thua rebuild | SC08 | I05, I06 | B04 |
| `h-already-announced-work-becomes-reference.json` | FX-RP-H | Work đã công bố → tham chiếu có ngày | SC09 | I07, I05 | B04, B15 |
| `i-identity-merge-single-first-announced.json` | FX-RP-I | Merge sau công bố → một first-announcement, ngày sớm nhất | SC09, SC23 | I05, I07, I17 | B06, B15 |
| `j-backfill-add-remove-readd.json` | FX-RP-J | Backfill add → remove → re-add: không cấp lần hai | **SC37** | I06 | B04 |
| `k-builder-crash-backfill-not-consumed.json` | FX-RP-K | Crash giữa build → không tiêu thụ backfill, không report một phần | **SC38**, SC08 | I05, I06 | B04 |
| `l-embedding-generation-switch-blocked.json` | FX-RP-L | Đổi generation giữa chừng → selection bị chặn | SC24 | I12, I05 | B04 |
| `m-density-worked-example.json` | FX-RP-M | Mật độ vector: ví dụ số tái lập được + biến thể dưới cỡ mẫu | SC08 | I12 | B14 |
| `n-embedding-generation-switch-positive.json` | FX-RP-N | Đổi model embedding: dựng G2 → chặn khi thiếu vector → chuyển active nguyên tử → selection chỉ dùng G2 | **SC52** | I12, I05, I06 | B04 |

**SC37 và SC38 là scenario ID mới** do PC04 đề nghị. PC02 đã dùng `SC29`–`SC31` và PC03 đã dùng
tới `SC36`, nên PC04 lấy `SC37+`. Chuyển tới PC09 để đăng ký vào `acceptance/scenarios.yaml`:
**CR-PC04-06**. SC37 = backfill add–remove–re-add; SC38 = builder crash không tiêu thụ backfill.

## 2. Bao phủ invariant: mỗi invariant có mục dương và mục đối chứng

| Invariant | Owner section | Fixture dương | Fixture đối chứng (phải FAIL nếu triển khai sai) |
| --- | --- | --- | --- |
| I05 — report không đổi âm thầm sau publish | time-and-tags.md §3 | `c` (hash không đổi qua retry) | `a` §O-3.3 (build stale không được publish); `i` (merge không viết lại kỳ cũ); `g` (bên thua không để lại item) |
| I06 — coverage nối liền, pending không mất | time-and-tags.md §4, §5 | `d` (kỳ rỗng vẫn nối); `f` (một cửa sổ bao trùm) | `e` §O-5.2 (xóa pending khi con trỏ tiến); `g` (hai cửa sổ cùng predecessor) |
| I07 — một first-announcement cho một canonical work | time-and-tags.md §8 | `h` (tham chiếu có ngày) | `i` (merge tạo hàng thứ hai hoặc reset ngày) |
| I12 — không trộn generation trong một lần selection | selection.md §5 | **`n`** (mặt DƯƠNG: rebuild → chuyển active nguyên tử → chỉ G2); `m` (mọi vector cùng generation) | `l` (mặt ÂM: generation đổi giữa chừng; tag thiếu vector ở generation mới) |

## 3. Hình dạng chung của một fixture

```text
fixture_id, title, purpose
scenario_refs, invariant_refs, decision_refs, requirement_refs, source_refs
contract_refs, owner_id, claim_ceiling, evidence_status
given            : ảnh chụp hàng trước sự kiện, theo tên bảng của entities.yaml
                   (+ settings, embedding_generation, counters_before khi cần)
events[]         : chuỗi có thứ tự {seq, at, actor, operation | event_type, transaction?, description}
expected         : report / rows / counts / row_oracles / hash_oracles / display_oracles
                   (+ after_event_N, variant_* cho fixture nhiều mốc hoặc nhiều nhánh)
forbidden_effects: những gì KHÔNG được xảy ra — là phần bắt lỗi thật sự
```

`at` luôn là UTC RFC 3339 mili giây. Sự kiện không phải operation (crash tiến trình, mất ACK)
dùng khóa `event_type` và không bị kiểm edge.

### 3.1 `actor` so với `performed_by` — hai thứ khác nhau

| Khóa | Nghĩa | Ràng buộc kiểm tự động |
| --- | --- | --- |
| `actor` | Module **gọi** operation | PHẢI có trong `caller_modules` của operation đó ở `contracts/ports.yaml`, VÀ bộ ba (`actor`, `owner_module`, `operation`) phải có trong `contracts/modules.yaml` → `allowed_edges` |
| `performed_by` | Service **thực thi** transaction / công việc | Nếu có mặt thì phải bằng `owner_module` của operation. **Không** phải một khẳng định về quyền gọi |

Định nghĩa này khớp `acceptance/fixtures/ai/README.md` §3.1 và README của PC07.

Ví dụ: `ingest.submit_batch` có `owner_module = MOD-ingest-service` và
`caller_modules = [MOD-x-collector]`. Vì vậy `actor` phải là `MOD-x-collector`;
`MOD-ingest-service` chỉ được xuất hiện ở `performed_by`.

**Mười sự kiện của bộ này ban đầu viết sai đúng chỗ đó** (audit A1-R2 → F-A1R2-02) và đã được
sửa trong `PKT-PC04-FIX1`: `a`#1, `a`#2, `b`#3, `c`#2, `c`#3, `c`#5, `e`#3, `f`#2, `f`#3, `i`#1.
Kiểm tự động: `EV-PC04-05` (fixture-actor-edge) — 51/51 sự kiện PASS.

### 3.2 Tên cột trong `rows` — quy tắc R4-01

Quy tắc dưới đây là **ruling R4-01** (FIX4, sau F-A1R3-01), ràng buộc **cả sáu** thư mục fixture
và được chép nguyên văn:

> Under `given.rows.<entity>[]` and `expected.rows.<entity>[]`, every key is either (a) a column
> that exists in `contracts/data/entities.yaml` for that entity, (b) an annotation whose key
> **starts with `_`** (`_note`, `_target`, `_note_vi`, `_save_channel_note`,
> `_created_in_transaction`, `_payload_contains`, …), or (c) a column carrying an in-file
> `pending_cr: CR-…` marker. No per-package allowlist.

Hệ quả cho bộ này:

- **0** khóa chưa giải quyết (`EV-PC04-06`, chạy trên cả sáu thư mục). Mọi cột đã tồn tại tại
  `contracts/data/entities.yaml` sha256
  `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece`.
- **0** marker `pending_cr`.
- Chú thích của fixture mang tiền tố `_`: `_target` (object target để validate theo
  `target.schema.json`), `_vector_present` (fixture văn bản không mang được blob vector thật),
  `_note` / `_note_vi` (giải thích cho người đọc).
- Checker bỏ qua khóa `_…` **theo quy tắc**, không theo một danh sách tên. Một allowlist riêng
  của từng gói là điều R4-01 cấm tường minh — chính nó đã làm gate của PC07 báo PASS trong khi
  89 khóa còn chưa giải quyết (F-A1R3-01).

Một cạm bẫy riêng của thư mục này: **read model khác hàng bảng.**
`expected.report.coverage` dùng tên của `report.schema.json` (`coverage_window_id`,
`coverage_from`, `coverage_to`), còn `rows` → `coverage_window` phải dùng tên cột (`id`,
`window_from`, `window_to`). `PKT-PC04-FIX1` đã sửa 16 hàng bị lẫn hai hệ tên này.

Kiểm tự động ở `EV-PC04-03` (operation/entity tồn tại), `EV-PC04-05` (actor-edge),
`EV-PC04-06` (field existence theo R4-01).

## 4. Quy ước về hash và về số

**Quy ước ký hiệu tượng trưng.** Tên tượng trưng trong `row_oracles` / `hash_oracles` (ví dụ `h_c`, `rp_early`, `tag_v1`) viết **chữ thường** để không bao giờ bị đọc nhầm là một error code (vốn viết hoa toàn bộ) của `contracts/errors.yaml`. Chúng trỏ tới giá trị được định nghĩa trong `given` của chính fixture đó, không phải một định danh hợp đồng.


Giống `acceptance/fixtures/identity/README.md` §3: fixture khẳng định **quan hệ**, không khẳng
định một chuỗi hex bịa. `content_hash` và `payload_hash` trong các file này là giá trị dẫn
xuất tất định từ một nhãn (`sha256(<nhãn>)`) chỉ để có một chuỗi hợp lệ về hình dạng; **oracle
thật nằm ở `hash_oracles`** ("H sau bằng H trước"), không nằm ở giá trị cụ thể.

**Ngoại lệ có chủ ý:** mọi con số trong `m-density-worked-example.json`
(`computation.*`, `density_*`, `centroid`) là giá trị **tính được**, không phải giá trị bịa.
`EV-PC04-02` tính lại toàn bộ bằng script và so với cả fixture lẫn
`contracts/reporting/selection.md` §8.7. Sai một chữ số là FAIL.

Làm tròn: half-up, 4 chữ số thập phân (selection.md §3).

## 5. Cách dùng ở từng cấp bằng chứng

| Cấp | Dùng fixture thế nào | Trạng thái ở PC04 |
| --- | --- | --- |
| E0 | Parse JSON; validate mọi `expected.*.report` theo `report.schema.json`; kiểm mọi `operation` tồn tại trong `ports.yaml` và mọi tên bảng tồn tại trong `entities.yaml`; tính lại ví dụ mật độ; kiểm coverage nối liền và nửa mở | **ĐÃ CHẠY** (EV-PC04-01..04, `SELF_VALIDATION`) |
| E1 | Nạp `given` vào kho trống, phát `events` qua đúng operation, so `expected`, và khẳng định mọi mục `forbidden_effects` KHÔNG xảy ra | `NOT_RUN` — cần code |
| E2 | Thêm fault injection tại các mốc commit (crash trước/sau COMMIT của publish, CAS thua, generation đổi giữa build và commit) | `NOT_RUN` |
| E3 | Không áp dụng: không fixture nào ở đây cần X/AI/Telegram thật | `NOT_APPLICABLE` |
| E4 | Chỉ liên quan tới chất lượng nội dung khối hướng nổi (REQ-A4) — cần 3–4 kỳ thật, thuộc PC09 | `NOT_RUN` |

## 6. Cái các fixture này KHÔNG chứng minh

- Không chứng minh code chạy đúng: chưa có code (SRC-PLAN §14.2, cấp E0).
- Không chứng minh ngưỡng `0.8000` tách được bài khớp khỏi bài không khớp (REQ-A2, `KC`).
- Không chứng minh thuật toán mật độ phát hiện hướng thật thay vì nhiễu (REQ-A4, `KC`). Ví dụ số
  ở `m` chứng minh **tính tái lập của phép tính**, không chứng minh **tính hữu ích của kết quả**.
- Không chứng minh coverage phản ánh đủ những gì có trên X (B05; `coverage_note` → `observed_data_only`
  tồn tại chính vì điều đó).
- Không thay thế fixture của gói khác: identity (PC02), collection (PC05), AI (PC06),
  telegram (PC07), recovery (PC08).

## 7. Bất biến khi sửa fixture

Sửa một `expected` để cho triển khai pass là vi phạm hợp đồng (SRC-PLAN §15,
`agent_profile/worker.md`). Nếu một oracle sai, mở change request có bằng chứng, đừng sửa
fixture. Điều này áp dụng đặc biệt cho `m`: chỉnh một tham số để một nhóm vượt ngưỡng chính là
hành vi mà SRC-PLAN §14.2 cấm ("Với A4 thiếu 3–4 kỳ thì ghi chưa đủ bằng chứng, không chỉnh số
để pass").
