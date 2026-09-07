---
contract_id: CT-reporting-time-and-tags
version: 0.1.0
status: draft
owner_role: reporting contract owner
source_refs:
  - "SRC-SPEC §3.4 C03/D-tag, D23, D24"
  - "SRC-SPEC §3.5 D27, D28, D29, D57"
  - "SRC-SPEC §3.6 D55, D56"
  - "SRC-SPEC §5.5 (đổi tag)"
  - "SRC-SPEC §8.1, §8.2, §8.3"
  - "SRC-SPEC §9.2 (checkpoint), §10.4 (chi phí)"
  - "SRC-SPEC §12 AC-05, AC-06, AC-08, AC-09"
  - "SRC-PLAN §3 B01, B04, B08, B14, B17"
  - "SRC-PLAN §5.1 (wire rules), §6.1 (owner của dữ liệu)"
  - "SRC-PLAN §7 I05, I06, I07, I12"
  - "SRC-PLAN §8.2 (report building/published/aborted, quality complete/partial)"
  - "SRC-PLAN §9.2 (đóng kỳ báo cáo), §9.3 (embedding generation)"
  - "SRC-PLAN §10 TAG_VERSION_STALE, EMBEDDING_GENERATION_MISMATCH"
  - "SRC-PLAN §11 PC04"
requirement_refs:
  [REQ-CTAG, REQ-D12, REQ-D23, REQ-D24, REQ-D25, REQ-D27, REQ-D28, REQ-D29, REQ-D30,
   REQ-D53, REQ-D55, REQ-D56, REQ-D57, REQ-AC05, REQ-AC06, REQ-AC08, REQ-AC09,
   REQ-S8.1-03, REQ-S8.2-01, REQ-S8.2-02, REQ-S8.2-08, REQ-S8.2-09, REQ-S9.2-04,
   REQ-S10.3-05, REQ-S10.4-03, REQ-OQ04, REQ-P0-07]
decision_refs: [B01, B04, B08, B14, B17, AMD-B01, AMD-B04, AMD-B08, AMD-B17, ADR-0004, ADR-0007]
invariant_refs: [I05, I06, I07, I12]
producers: [MOD-report-service]
consumers: [MOD-web-ui, MOD-backend-api, MOD-telegram-adapter, MOD-delivery-service, MOD-tag-service, MOD-analysis-service, MOD-identity-service, MOD-saved-service]
dependencies:
  - contracts/data/entities.yaml
  - contracts/data/identity.md
  - contracts/data/invariants.md
  - contracts/modules.yaml
  - contracts/ports.yaml
  - contracts/reporting/selection.md
  - contracts/schemas/report.schema.json
  - contracts/schemas/target.schema.json
  - contracts/state/report.yaml
  - acceptance/fixtures/reporting/
scope: >-
  Ngữ nghĩa thời gian và tag của tầng báo cáo: chuẩn timestamp và thứ tự tổng, vai trò của
  timezone owner, điểm đóng băng `tag_config_version`, sổ coverage nửa mở nối liền, sổ pending
  item (phát hiện muộn), sổ backfill N ngày, lệnh quét lại kho, và chính sách first-announcement
  (kể cả sau identity merge). Không định nghĩa máy trạng thái (PC03), không định nghĩa schema
  task AI (PC06), không định nghĩa màn hình (PC07).
verification: >-
  E0 SELF_VALIDATION ở gói PC04: EV-PC04-01 (schema báo cáo + fixture), EV-PC04-03 (mọi
  operation_id/entity được trích dẫn có tồn tại), EV-PC04-04 (coverage nối liền, nửa mở).
  E1–E4 đều `NOT_RUN` — chưa có code, chưa có dữ liệu thật.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Thời gian, tag và coverage của tầng báo cáo

> **Trạng thái quyết định.** Mọi quyết định trong file này gắn nhãn `PROVISIONAL` theo
> baseline §5 (Coordinator ruling dưới `AUTH-OWNER-20260906-01`). B01, B04, B08, B14, B17 vẫn
> **OPEN** trong `agent_profile/registry.json`; phê chuẩn thuộc Owner qua OWNER_DECISION_REQUEST.
> Không mục nào trong file này được đọc là `CLOSED` hay `ACCEPTED`.

## 0. Cách đọc và cách một mục ở đây bị làm sai

Mỗi mục kết thúc bằng **oracle**: một phát biểu đo được, độc lập với log và độc lập với câu trả
lời của agent (SRC-PLAN §2). Ký hiệu theo `contracts/data/invariants.md` §0: `#<bảng>` là số
hàng, `#<bảng>[điều kiện]` là số hàng thỏa điều kiện.

Tên bảng và tên cột được trích **nguyên văn** từ `contracts/data/entities.yaml`. Tên
operation được trích nguyên văn từ `contracts/ports.yaml`. Mã lỗi trích từ
`contracts/errors.yaml`, ngân sách retry từ `contracts/retry-policy.yaml`, và bảng transition
của report từ `contracts/state/report.yaml` — cả ba là file của PC03, đọc ở phiên bản có mặt
lúc file này được viết.

> **Cảnh báo baseline — dependency đang biến động.** `contracts/data/entities.yaml` đã đổi
> **ít nhất hai lần** trong lúc gói PC04 chạy: `88b2482e…` (121662 byte, theo
> `audits/FC-W1-manifest.txt`, bản PC04 khởi động) → `921a5927…` (175145 byte) → `2235564f…`.
> `contracts/ports.yaml` và `contracts/modules.yaml` cũng đổi, và `contracts/errors.yaml`,
> `contracts/retry-policy.yaml`, `contracts/state/*` xuất hiện giữa chừng (PC03 chạy song song).
> Hai file **nguồn** (SRC-PLAN, SRC-SPEC) **không đổi**, nên stop gate baseline §2 không kích
> hoạt. File này đã được căn lại và các hình dạng bảng mà nó phụ thuộc
> (`coverage_window`, `pending_item_ledger`, `backfill_ledger`, `rescan_ledger`,
> `first_announced_ledger`, `report_item.selection_reason`) đã được kiểm lại lần cuối theo
> `2235564f…` và **không đổi**. Dù vậy Coordinator phải coi PC04 là **cần re-verify trước khi
> freeze**: xem `evidence/handoffs/PC04-handoff.md` §baseline drift.

Tên trạng thái lấy nguyên văn SRC-PLAN §8.2: `report.status` ∈ `building | published | aborted`;
`report.quality` ∈ `complete | partial`. `contracts/state/report.yaml` (PC03) là nguồn chuẩn của
bảng transition; file này chỉ mô tả **điều kiện dữ liệu** tại các điểm commit.

---

## 1. Timestamp và thứ tự tổng

### 1.1 Định dạng

Mọi timestamp **bền** (persisted) là UTC RFC 3339, hậu tố `Z`, độ chính xác **đúng ba chữ số
mili giây**, khớp biểu thức đã khóa ở `contracts/schemas/target.schema.json` → `$defs.timestamp_utc_ms`:

```text
^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$
```

Căn cứ: SRC-PLAN §5.1 ("timestamp UTC RFC 3339 … phải chốt độ chính xác timestamp và tie-break
bằng ingest sequence trước PC04") và AMD-B08. Micro giây, offset khác `Z`, hay timestamp thiếu
phần mili giây bị **từ chối ở biên**, không được làm tròn âm thầm.

### 1.2 Bốn mốc thời gian khác nhau, không được lẫn

| Trường | Nguồn giá trị | Ai ghi | Dùng cho | **Cấm dùng cho** |
| --- | --- | --- | --- | --- |
| `post.published_at` | X khai báo | `MOD-ingest-service` | Hiển thị "ngày đăng" | Coverage, sắp xếp kỳ, chọn nội dung |
| `post.discovered_at` / `work.first_discovered_at` | Giờ **server** lúc chấp nhận lần đầu | `MOD-ingest-service` | **Biên coverage** (REQ-D27), thứ tự | Không |
| `analysis.analyzed_at` | Giờ server lúc commit kết quả | `MOD-analysis-service` | Hiển thị cùng `discovered_at` (SRC-SPEC §10.3) | Coverage |
| `report.published_at` | Giờ server tại **commit publish** | `MOD-report-service` | Mốc freeze tag (§3), mốc first-announcement (§8) | Biên coverage |

`post.collected_at_client` là đồng hồ của máy cá nhân và **không đáng tin** (entities.yaml:
"cấm dùng cho coverage/sắp xếp"). `worker_registration.last_run_at` chỉ để **hiển thị** trạng thái worker, không làm mốc lọc dữ liệu (REQ-D12). D12 nói "`last_run` chỉ để xem": đó là một giá trị hiển thị của worker, không phải một cột của `run` (ruling FIX7).

SRC-SPEC §8.2 hàng 1 nói rõ hệ quả: post đăng **thứ Hai** nhưng được phát hiện ở đợt 20h thứ Ba
vẫn vào kỳ của thứ Ba, vì **ngày đăng không quyết định** — `discovered_at` quyết định.

### 1.3 Thứ tự tổng: cặp `(discovered_at, ingest_sequence)`

`ingest_sequence` là số nguyên đơn điệu tăng trong phạm vi một owner, do server cấp **trong cùng
transaction ingest** (entities.yaml → `post.ingest_sequence`, `work.ingest_sequence`). Nó là
**thứ tự tổng có thẩm quyền**; `discovered_at` là nhãn thời gian đọc được của thứ tự đó.

Quy tắc ghép bắt buộc (`PROVISIONAL`, **CR-PC04-03** gửi PC02 để ghi vào entities.yaml):

> Server cấp `ingest_sequence` và `discovered_at` từ **cùng một lần đọc đồng hồ** dưới cùng một
> khóa cấp phát, và **kẹp đơn điệu** (`monotonic clamp`): nếu đồng hồ tường trả về giá trị nhỏ
> hơn `discovered_at` của sequence liền trước thì ghi lại đúng giá trị của sequence liền trước.
> Hệ quả: sắp theo `ingest_sequence` tăng thì `discovered_at` **không giảm**.

Không có quy tắc này thì hai mục cùng mili giây có thể nằm hai phía của một biên kỳ tùy theo
thứ tự truy vấn, và §4 mất tính tái lập.

**Oracle O-1.3.**
`SELECT COUNT(*) FROM post p JOIN post q ON q.ingest_sequence = p.ingest_sequence + 1
 WHERE q.discovered_at < p.discovered_at` = 0, với mọi owner. Tương tự cho `work`.
Fixture đối chứng: `f-three-offline-periods-one-catchup.json` (hai mục cùng mili giây, thứ tự
theo sequence là xác định).

---

## 2. Timezone của owner: chỉ để dán nhãn, không để tính

`owner.timezone_iana` là **một** IANA timezone do Owner xác nhận; giá trị tạm `Asia/Ho_Chi_Minh`
(`PROVISIONAL`, B08 / AMD-B08 / ADR-0007; Owner phải xác nhận).

Được phép dùng timezone owner cho:

1. **Nhãn kỳ** hiển thị trên màn hình Reports và trong digest Telegram ("Kỳ 19/03", "sáng 20/03").
2. Diễn giải **lịch chạy** (giờ 08:00 và 20:00 là giờ owner) — thuộc PC03,
   `contracts/state/run.yaml`.
3. Định dạng ngày trong câu chữ của item tham chiếu ("đã báo cáo 12/03") — §8.

Bị cấm dùng timezone owner cho:

- Tính `coverage_from` / `coverage_to` hoặc bất kỳ so sánh biên nào (§4). Biên là UTC.
- Sinh khóa, hash, hoặc bất kỳ giá trị bền nào ngoài cột hiển thị.
- Suy ra "ngày" của một mục: một mục thuộc kỳ nào là do `(discovered_at, ingest_sequence)` và
  biên kỳ quyết định, **không** do ngày lịch địa phương quyết định.

Đổi `owner.timezone_iana` **không** làm đổi nội dung của bất kỳ report đã publish nào; nó chỉ
đổi cách render nhãn. Đây là hệ quả trực tiếp của I05.

**Oracle O-2.**
Chạy lại việc dựng cùng một kỳ với hai giá trị `owner.timezone_iana` khác nhau
(`Asia/Ho_Chi_Minh` và `UTC`): `report.coverage_from`, `report.coverage_to`, tập
`report_item.target_key` và `report.content_hash` **giống hệt nhau**. Chỉ chuỗi nhãn hiển thị
khác. Khác một byte trong `content_hash` là FAIL.

---

## 3. Đóng băng tag tại transaction publish (B01)

### 3.1 Quyết định

`PROVISIONAL` theo AMD-B01 / ADR-0004: **bộ tag đang hiệu lực tại transaction publish của báo
cáo quyết định nội dung báo cáo.** Cụm "thời điểm gửi" trong SRC-SPEC §3.4 hàng `C03/D-tag`
được đọc lại là "thời điểm publish report". Delivery (gửi Telegram) **không bao giờ** làm đổi
nội dung đã publish.

Cơ chế: `report.tag_config_version_id` là FK tới `tag_config_version`, một ảnh chụp **bất biến**
gồm toàn bộ `tag` / `tag_alias` / `tag_exclusion` đang `state = 'active'` cùng `content_hash` =
`sha256(JCS(payload))`.

### 3.2 Ba mốc và hành vi tương ứng

| Đổi tag lúc nào | Hành vi | Căn cứ |
| --- | --- | --- |
| **Trước** khi build snapshot | Bộ tag mới được dùng bình thường; không có gì đặc biệt | REQ-D24 |
| **Giữa** build snapshot và commit publish | `tag.freeze_config_version` trả `TAG_VERSION_STALE` → builder **rebuild** hoặc **abort**. Không publish trộn hai phiên bản | SRC-PLAN §10, ports.yaml `tag.freeze_config_version` |
| **Sau** commit publish | Không ảnh hưởng kỳ đã publish. `report_item`, `report.content_hash` và payload delivery **không đổi**. Chỉ kỳ sau chịu ảnh hưởng | I05, AMD-B01 |

Đổi tag **trong lúc collector đang chạy** không ảnh hưởng việc lọc: collector chỉ dùng tag để
tìm kiếm, còn việc chọn nội dung xảy ra ở thời điểm publish (REQ-D24, SRC-SPEC §8.2 hàng 6).

### 3.3 Giao thức freeze (chuỗi gọi chính xác)

1. `MOD-job-service` gọi `report.build` (internal). Builder đọc phiên bản tag hiện hành bằng
   `tag.get_active_config_version` → `(tag_config_version_id_at_build, content_hash_at_build)`.
   Builder chạy selection theo `contracts/reporting/selection.md` với **đúng** phiên bản đó.
2. `MOD-report-service` mở transaction publish và gọi `tag.freeze_config_version` với
   `report_build_id` + `expected_tag_config_version_id = tag_config_version_id_at_build`.
3. Nếu phiên bản hiện hành đã khác → `TAG_VERSION_STALE`. Transaction **rollback**; không hàng
   `report` nào ở `status = 'published'` được tạo.
4. Nếu khớp → `report.tag_config_version_id` được ghi bất biến trong cùng transaction với
   `report`, `report_item`, coverage, first-announcement, backfill và delivery intent (§4.5).

`tag.freeze_config_version` là idempotent theo `report_build_id`: gọi lại trong cùng build trả
đúng một `tag_config_version_id` (ports.yaml). Hai lần publish không đổi tag dùng lại **cùng
một** hàng `tag_config_version` nhờ `ux_tag_config_version_owner_hash`.

### 3.4 Chính sách rebuild sau `TAG_VERSION_STALE`

Ngân sách do PC03 sở hữu; PC04 **dùng lại**, không đặt tên riêng:

| Tham số (`contracts/retry-policy.yaml`) | Giá trị | Đơn vị | Trạng thái |
| --- | --- | --- | --- |
| `report_build_rebuild_attempts` | 2 | rebuilds_total_per_run | `PROVISIONAL` |
| `report_build_stale_after` | xem retry-policy.yaml | — | `PROVISIONAL` |

Hành vi theo `contracts/state/report.yaml` T-RP-03: build chuyển `status = 'aborted'`, rebuild
là một `report_build_id` **mới** với version tag mới. Hết ngân sách → run kết thúc với
`outcome = 'partial'` và lý do rõ, **không** dựng vô hạn. **Không** có nhánh nào publish một
report bằng phiên bản tag khác phiên bản đã dùng để chọn.

Abort **không** tạo hàng coverage: coverage chỉ tiến tại commit publish (§4.4).

### 3.5 Oracle

- **O-3.1 (AC-05).** Bỏ tag T lúc `19:00Z`, publish lúc `20:00Z`: với 4 target chỉ khớp T,
  `#report_item[report_id = R AND target_key IN {4 target đó}]` = 0, đồng thời
  `#work[...]` và `#analysis[status='valid' AND target_key IN {...}]` **không đổi** trước/sau
  (dữ liệu vẫn ở kho). Fixture `a-tag-removed-before-publish.json`.
- **O-3.2 (SC19, AMD-B01).** Đổi tag sau `report.published_at` nhưng trước
  `delivery.record_receipt`: `report.content_hash` và tập `(report_item.target_key,
  report_item.item_type, report_item.analysis_id)` **bằng nhau từng byte** trước và sau.
  Fixture `c-tag-changed-after-publish-before-send.json`.
- **O-3.3 (TAG_VERSION_STALE).** Đổi tag ngay trước CAS commit:
  `#report[status='published' AND id = R]` = 0 và `#report[status IN ('building','aborted')
  AND id = R]` = 1; không hàng `coverage_window` nào được tạo.
- **O-3.4 (I05).** Với mọi report đã `published`: `sha256(JCS(nội dung đã publish))` bằng
  `report.content_hash` tại **mọi thời điểm sau đó**, kể cả sau khi tag đổi, sau identity merge
  và sau restore.

---

## 4. Coverage: cửa sổ nửa mở, nối liền, sổ độc lập (B04)

### 4.1 Quyết định

`PROVISIONAL` theo AMD-B04: **sổ coverage (`coverage_window`) là nguồn chuẩn, độc lập với danh
sách report hiển thị.** Kỳ rỗng vẫn ghi một hàng coverage nhưng **không** sinh digest (REQ-D57).
Sổ `pending_item_ledger` và sổ `backfill_ledger` độc lập với con trỏ kỳ.

Một cửa sổ là khoảng **nửa mở** `[window_from, window_to)`: biên trái inclusive, biên phải
exclusive (entities.yaml → `coverage_window`, `CHECK (window_to > window_from)`).

### 4.2 Chuỗi nối liền

- Cửa sổ đầu tiên: `predecessor_window_id IS NULL`.
- Mọi cửa sổ khác: `window_from = predecessor.window_to`. Không hở, không chồng lấn (REQ-AC08).
- `sequence` đơn điệu tăng, `UNIQUE(owner_id, sequence)`.
- `UNIQUE(owner_id, predecessor_window_id)` là **CAS**: hai kỳ không thể cùng nối sau một kỳ.

### 4.3 Biên `window_to` được chọn thế nào: watermark của ingest sequence

Biên thời gian một mình không đủ, vì một transaction ingest bắt đầu trước snapshot có thể commit
sau snapshot với `discovered_at` sớm hơn. Vì vậy mỗi cửa sổ mang **hai trục** và tính thành viên
dùng trục sequence:

| Cột | Ý nghĩa | Trạng thái |
| --- | --- | --- |
| `window_from`, `window_to` | Nhãn thời gian nửa mở, hiển thị và diễn đạt D27 | đã có ở entities.yaml |
| `ingest_sequence_from` (inclusive), `ingest_sequence_to` (exclusive) | **Vị từ thành viên thật sự** | cột mới → **CR-PC04-01** gửi PC02 |

Định nghĩa:

1. **Watermark liền mạch.** `W` = số nguyên lớn nhất sao cho **mọi** `ingest_sequence` trong
   `[1, W]` đã commit tại thời điểm build snapshot. Sequence đã cấp nhưng transaction chưa
   commit chặn watermark tại đó — đây là điều làm biên an toàn.
2. `ingest_sequence_to := W + 1` (exclusive). `ingest_sequence_from := predecessor.ingest_sequence_to`,
   hoặc `0` cho cửa sổ đầu tiên.
3. `window_to := discovered_at` của mục có `ingest_sequence = W`, hoặc `snapshot_taken_at` nếu
   cửa sổ rỗng (`ingest_sequence_from = ingest_sequence_to`).
4. Vị từ thành viên của một target trong cửa sổ:
   `ingest_sequence_from <= target.ingest_sequence < ingest_sequence_to`.
   Vị từ theo timestamp (`window_from <= discovered_at < window_to`) là **hệ quả** nhờ quy tắc
   kẹp đơn điệu §1.3, không phải một định nghĩa thứ hai.

Mục ingest **sau** khi snapshot đã chốt luôn có `ingest_sequence >= ingest_sequence_to`, nên nó
thuộc kỳ sau, không bao giờ rơi vào lỗ hổng.

### 4.4 Coverage chỉ tiến tại commit publish

`coverage_window.advanced_at` được ghi **trong transaction publish**, không sớm hơn. Hệ quả:

- Build bị abort (`TAG_VERSION_STALE`, `EMBEDDING_GENERATION_MISMATCH`, crash) → **không** hàng
  coverage nào, con trỏ không tiến, dữ liệu được xét lại ở lần build sau.
- Run thất bại thu thập **không** tự biến thành một kỳ rỗng thành công (SRC-PLAN §9.2). Kỳ rỗng
  chỉ hợp lệ khi run kết thúc `status = 'completed'` với `outcome = 'empty'` (SRC-PLAN §8.1) —
  tức "thu thập xong, không mục nào khớp tag", không phải "không thu thập được".
- SRC-SPEC §8.3 phân biệt ba trạng thái; §4.7 dưới đây ghi vào `coverage_note` để UI (PC07)
  không hiển thị thiếu dữ liệu thành "không có nghiên cứu mới" (I13).

### 4.5 Transaction publish: những gì cùng commit

`report.publish` (ports.yaml, idempotent theo `report_build_id`) ghi **một** transaction gồm:

1. `report` (`status = 'published'`, `published_at`, `quality`, `content_hash`).
2. `report_item` cho mọi mục được chọn.
3. `emerging_direction` (kể cả hàng `evidence_state = 'insufficient_evidence'`).
4. `coverage_window` mới, với guard CAS `predecessor_window_id = expected_predecessor_window_id`.
5. `first_announced_ledger` cho mọi item `item_type = 'new_discovery'` (§8).
6. `pending_item_ledger`: tạo hàng mới cho mục thiếu summary/vượt hạn mức, và đóng hàng đã được
   giải quyết ở kỳ này (§5).
7. `backfill_ledger.consumed_in_report_id` khi điều kiện tiêu thụ ở §6.4 thỏa.
8. `report.tag_config_version_id` qua `tag.freeze_config_version` (§3.3).
9. `outbox_intent` / `delivery.create_intent` — **chỉ khi** kỳ không rỗng (REQ-D57).
10. `run.status` / `run.outcome` (PC03).

Danh sách trên khớp `rows_written_together_vi` của `contracts/state/report.yaml` → `publish_cas`.

**Ba vị từ PC04 phải cung cấp cho PC03.** `contracts/state/report.yaml` →
`ownership_boundary` → `interface_contract_vi` yêu cầu ba hàm boolean, tính được **trước** CAS và
**không có side effect**:

| Vị từ | Đúng khi | Sai → |
| --- | --- | --- |
| `coverage_predecessor_matches(expected_predecessor_id)` | Con trỏ coverage hiện hành vẫn là `expected_predecessor_id`, và `window_from` của kỳ mới bằng `window_to` của nó (§4.2) | `CONFLICT` |
| `tag_config_version_matches(expected_tag_config_version_id)` | Phiên bản tag hiện hành bằng phiên bản đã dùng để chọn (§3.3) | `TAG_VERSION_STALE` |
| `embedding_generation_matches(expected_embedding_generation_id)` | Generation active bằng generation đã dùng để tính similarity, và `dimension` khớp (`selection.md` §5) | `EMBEDDING_GENERATION_MISMATCH` |

Cả ba là **hàm thuần túy trên trạng thái đã commit**: chúng đọc, không ghi, và không được gọi
mạng. Cần thêm vị từ là một CR về phía PC04, không phải sửa `contracts/state/report.yaml`.

Không có bước nào trong danh sách trên được commit riêng lẻ. Gọi mạng ngoài (Telegram) **không**
nằm trong transaction này (SRC-PLAN §5.1: external side effect dùng intent/outbox đã commit).

### 4.6 CAS: đúng một publisher thắng

Hai builder cùng chạy cho cùng predecessor:

1. Cả hai đọc `expected_predecessor_window_id = P`.
2. Cả hai chèn `coverage_window` với `predecessor_window_id = P`.
3. `ux_coverage_window_predecessor` cho **đúng một** transaction commit.
4. Bên thua nhận vi phạm UNIQUE → **phải** rollback toàn bộ, đọc lại con trỏ và **rebuild**.
   Cấm: retry chèn với predecessor khác mà giữ nguyên tập item đã chọn; cấm publish kỳ chồng.

Mã lỗi: **`CONFLICT`** — đã đăng ký trong `contracts/errors.yaml` với
`operations: [report.publish, embedding.activate_generation, tag.freeze_config_version]` và
`retry_budget_ref: cas_conflict_retries` (giá trị 3, `PROVISIONAL`). Ngân sách này thuộc PC03;
PC04 dùng lại. Không dùng `IDEMPOTENCY_CONFLICT`: đó là "cùng key khác payload", còn đây là
"predecessor đã bị chiếm". Bên thua bắt buộc **đọc lại predecessor mới** trước mỗi lần thử lại
(`retry-policy.yaml` → `cas_conflict_retries` → `precondition_vi`).

### 4.7 Kỳ rỗng, kỳ một phần và câu chữ bắt buộc

| Tình huống | `report` | `coverage_window` | `delivery` | Câu chữ |
| --- | --- | --- | --- | --- |
| Không mục nào khớp tag | bản dựng chuyển `status='aborted'` + `abort_reason='empty_period'`; **không** có report `published` để hiển thị (§4.7.1, `contracts/state/report.yaml` T-RP-07) | có, `report_id = NULL` | không tạo intent | "không có nội dung phù hợp" — **cấm** "không có nghiên cứu mới" (SRC-SPEC §8.3) |
| Có mục nhưng thiếu summary | `status='published'`, `quality='partial'` | có, `report_id = R` | có intent | Danh sách pending tường minh (B17/AMD-B17) |
| Run dừng sớm (limit/CAPTCHA) | có thể publish `quality='partial'` | có | có intent | `coverage_note.observed_data_only = true`: coverage nêu phạm vi **dữ liệu đã quan sát**, **không** hứa bao phủ toàn bộ thời gian trên X |
| Run thất bại thu thập | không publish | **không** tạo | không | "đợt thất bại" — khác "không có nội dung phù hợp" |

Sự thật nghiệp vụ "kỳ này rỗng" nằm ở `coverage_window(report_id = NULL)` + `run.outcome = 'empty'`,
**không** ở một trạng thái report thứ tư (`contracts/state/report.yaml` T-RP-07 `note_vi`).

#### 4.7.1 Kỳ rỗng có để lại hàng `report` hay không — quyết định CR-PC03-06

PC03 hỏi PC04 (chủ sở hữu tầng báo cáo) chọn giữa hai phương án:

| | Phương án | Hệ quả |
| --- | --- | --- |
| (a) | **Không** có hàng `report` nào; chỉ `coverage_window(report_id = NULL)` + `run.outcome = 'empty'` | `aborted` chỉ còn nghĩa "build thất bại" |
| (b) | Có hàng `report(status = 'aborted')` kèm **lý do tường minh** `abort_reason = 'empty_period'` | `aborted` mang hai nghĩa, phân biệt bằng `abort_reason` |

**Quyết định (`PROVISIONAL`): (b), với `abort_reason` bắt buộc.** Đây là chỗ PC04 **không**
theo khuyến nghị của Coordinator (Coordinator khuyên (a)); lý do kỹ thuật cụ thể như sau, và
quyết định này dễ đảo — xem cuối mục.

**Lý do quyết định: idempotency của `report_build_id` cần một mỏ neo bền.**
`report.publish` là idempotent theo `report_build_id` (`ports.yaml`;
`contracts/state/report.yaml` → `publish_cas` → `idempotency_rule_vi`).

> **Trạng thái tiền đề (sửa theo F-A1R2-01).** Khi PC04 viết lần đầu, `report_build_id` xuất
> hiện ở `ports.yaml`, `state/report.yaml` và file này nhưng **không** phải một cột của thực thể
> nào — audit A1-R2 chỉ đúng rằng lập luận dưới đây khi đó dựa trên một cột không tồn tại, và
> PC04 đã không mở CR cho nó. PC02-FIX3 nay đã khai
> **`report.report_build_id`** (UUIDv4, NOT NULL, `UNIQUE(owner_id, report_build_id)` =
> `ux_report_owner_build_id`) trong `contracts/data/entities.yaml`
> (sha256 `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece`). Từ đây lập luận
> dựa trên bytes đã đóng băng, không phải trên một giả định.

Nếu một kỳ rỗng **không** để lại hàng `report` nào thì trong toàn bộ kho **không có** bản ghi nào
ánh xạ `report_build_id → "build này đã đóng một kỳ rỗng"`:

- `coverage_window` không có cột `report_build_id` (xem `entities.yaml`: `id`, `owner_id`,
  `sequence`, `window_from`, `window_to`, `predecessor_window_id`, `report_id`, `advanced_at`),
  và `report_id` của kỳ rỗng là `NULL`.
- Vì vậy một lần `report.publish` **replay sau khi mất ACK** không thể tra ra receipt cũ. Nó sẽ
  thử tiến coverage lần thứ hai, thua CAS, trả `CONFLICT`, và kích hoạt một vòng
  rebuild vô ích — đúng loại lỗi mà SRC-PLAN §5.1 cảnh báo ("Timeout transport là **không biết
  kết quả** … Trước retry mutation phải tra receipt hoặc replay theo hợp đồng idempotent").

Phương án (b) giữ đúng mỏ neo đó: hàng `report` mang cột `report.report_build_id` đã tồn tại từ
`T-RP-01`, và `ux_report_owner_build_id` ép "một publish cho một build", nên replay tra được và
trả lại kết quả cũ mà không đụng coverage.

**Mối lo của phương án (a) vẫn được giải quyết.** Điều Coordinator muốn tránh là `aborted` bị
nhập nhằng giữa "kỳ rỗng hợp lệ" và "build hỏng". `abort_reason` giải quyết đúng điểm đó:

| `report.abort_reason` | Nghĩa | Transition PC03 |
| --- | --- | --- |
| `empty_period` | Kỳ rỗng hợp lệ: thu thập xong, không mục nào khớp tag | T-RP-07 |
| `tag_version_stale` | Bộ tag đổi giữa build và CAS | T-RP-03 |
| `embedding_generation_mismatch` | Generation đổi giữa build và CAS | T-RP-04 |
| `cas_conflict` | Thua CAS trên predecessor | T-RP-05 |
| `builder_failure` | Builder chết hoặc bản dựng treo | T-RP-06 |
| `cancelled` | Owner hủy run trước khi publish | T-RUN cancel |

`abort_reason` **đã tồn tại** trên `report` sau PC02-FIX3 (CR-PC04-09 đã được đáp): enum
`empty_period | tag_version_stale | embedding_generation_mismatch | cas_conflict |
builder_failure | cancelled`, `CHECK: NOT NULL khi và chỉ khi status = 'aborted'`. Tên giá trị
lấy nguyên văn entities.yaml — hai giá trị PC04 đề nghị ban đầu (`cas_lost`,
`builder_crash_or_stale`) đã được ruling đổi thành `cas_conflict`, `builder_failure`.

**Cả hai phương án đều thỏa REQ-D57 và AMD-B04**, vì `aborted` **không phải** report hiển thị:
`contracts/schemas/report.schema.json` khóa `status` là `const "published"`, nên không tồn tại
read model cho một hàng `aborted`. Khác biệt duy nhất giữa (a) và (b) là chẩn đoán và
idempotency, không phải hành vi người dùng nhìn thấy.

**Nếu Coordinator/Owner vẫn muốn (a).** Điều kiện tiên quyết vẫn là thêm một khóa idempotency
vào `coverage_window` để replay tra được receipt — PC02-FIX3 đặt `report_build_id` trên `report`,
**không** trên `coverage_window`, nên dưới (a) vẫn không có receipt nào cho một kỳ rỗng. Đó sẽ là
một CR mới về phía PC02 cộng một sửa đổi `publish_cas` về phía PC03. Ghi ở unresolved refs của
`evidence/handoffs/PC04-handoff.md`.

**Oracle O-4.7.1.** Với một kỳ rỗng:
`#report[status='published']` không tăng; `#report[status='aborted' AND abort_reason='empty_period']`
tăng đúng 1; `#coverage_window` tăng đúng 1 với `report_id IS NULL`;
`#outbox_intent[type='report_digest']` không tăng; `run.status='completed'` và
`run.outcome='empty'`. **Oracle âm:** gọi lại `report.publish` với **cùng** `report_build_id`
sau đó không được tạo cửa sổ coverage thứ hai và không được trả `CONFLICT` — nó phải trả lại
kết quả cũ. Fixture `d-empty-period-coverage-only.json`.
Nếu Owner chọn (a), oracle đổi thành `#report` không tăng, và oracle âm về replay **chỉ** giữ
được sau khi `coverage_window` có khóa idempotency.

`coverage_note` là object bắt buộc trên report (xem `contracts/schemas/report.schema.json`), gồm
`observed_data_only`, `run_stop_reason`, `source_coverage_limits_note`, `empty_period`.

### 4.8 Bootstrap cửa sổ đầu tiên

- `predecessor_window_id = NULL`, `sequence = 1`, `ingest_sequence_from = 0`.
- `window_from = MIN(discovered_at)` trên toàn bộ mục đã commit tại snapshot; nếu kho rỗng thì
  `window_from = snapshot_taken_at − 1 ms` (giá trị suy biến nhưng thỏa `CHECK (window_to >
  window_from)`).
- Nếu có backfill entitlement đang mở (§6), `window_from` được kéo lùi theo §6.3 **trước khi**
  hàng coverage được ghi; không có cửa sổ thứ hai nào được tạo cho phần backfill.

### 4.9 Oracle

- **O-4.1 (AC-08, I06).** Với mọi owner, sắp `coverage_window` theo `sequence`:
  `window_from[n] = window_to[n-1]` và `ingest_sequence_from[n] = ingest_sequence_to[n-1]` với
  mọi `n >= 2`; và `#coverage_window[predecessor_window_id IS NULL]` = 1.
  Kiểm bằng script — EV-PC04-04.
- **O-4.2 (kỳ rỗng).** Sau một kỳ rỗng: `#coverage_window` tăng đúng 1,
  `#report[status='published']` **không đổi** (bản dựng ở `aborted`), `#outbox_intent`
  **không đổi**, và `coverage_from` của kỳ kế tiếp bằng `window_to` của kỳ rỗng.
  Fixture `d-empty-period-coverage-only.json`.
- **O-4.3 (CAS).** Hai publisher đồng thời: `#coverage_window[predecessor_window_id = P]` = 1
  và `#report[status='published' AND coverage_from = P.window_to]` = 1. Bên thua để lại
  `#report[status='aborted']` >= 1 và **không** để lại `report_item` nào.
  Fixture `g-concurrent-publishers-cas.json`.
- **O-4.4 (không hở khi offline nhiều kỳ).** Ba kỳ lịch bị bỏ lỡ, một run chạy bù: `#coverage_window`
  tăng đúng **1**, và cửa sổ đó bao trùm toàn bộ khoảng của ba kỳ.
  Fixture `f-three-offline-periods-one-catchup.json`.

---

## 5. Sổ pending item: phát hiện muộn không bao giờ mất (I06, B17)

### 5.1 Khi nào một hàng pending được tạo

Trong transaction publish, mọi target **đã được chọn** (theo `selection.md`) mà không có một
hàng `analysis[status='valid', task_type='summary']` khớp analysis key hiện hành sẽ có một hàng
`pending_item_ledger`:

| `reason` | Nghĩa |
| --- | --- |
| `missing_summary` | Task summary đã được xếp hàng (`analysis.enqueue_tasks`) nhưng chưa có kết quả tại thời điểm publish |
| `analysis_failed` | Attempt hết budget, `AI_OUTPUT_INVALID` hoặc `AI_PROVIDER_UNAVAILABLE` |
| `analysis_unknown` | `AI_ATTEMPT_UNCERTAIN` — chưa kết luận, **cấm** ghi thành failed |
| `budget_exceeded` | Vượt `max_items_per_period` (selection.md §7) — mục **chờ đợt sau**, không bị bỏ (SRC-SPEC §10.4) |

`ux_pending_owner_target_open` (`UNIQUE(owner_id, target_key) WHERE state = 'pending'`) đảm bảo
một target chỉ có một hàng pending mở.

### 5.2 Vì sao sổ này độc lập con trỏ kỳ

Sổ pending **không** mang biên thời gian của kỳ; nó chỉ ghi `first_pending_window_id`. Ở kỳ sau,
tập ứng viên = (mục trong cửa sổ mới) **∪** (mọi target có hàng pending đang mở), bất kể
`discovered_at` của chúng nằm ngoài cửa sổ mới. Đây chính là phát biểu "pending item không mất
khi con trỏ tiến" của I06.

### 5.3 Nhãn "phát hiện muộn"

Khi một target pending cuối cùng có summary và vào được báo cáo:

- `report_item.selection_reason.late_discovery = true`; UI/Telegram hiển thị nhãn
  **"phát hiện muộn"**.
- `pending_item_ledger.state` → `resolved_reported_late`, **trong cùng transaction publish**.
- `item_type` **không** đổi vì việc này: một mục phát hiện muộn chưa từng được công bố vẫn là
  `new_discovery` (§8). "Phát hiện muộn" là nhãn hiển thị, không phải loại mục.
- `report_item.selection_reason.pending_since_window_sequence` ghi `sequence` của
  `first_pending_window_id` để câu chữ hiển thị được ("phát hiện muộn, thuộc kỳ #12").

**Không cần cột mới.** `entities.yaml` giao cho PC04 quyền khóa hình dạng của
`report_item.selection_reason` (kiểu `json`, "Tag nào khớp, điểm tương đồng. PC04 khóa hình
dạng"). Mọi trường riêng của PC04 sống trong object đó:

```text
report_item.selection_reason = {
  matched_tags[]                      # selection.md §4.1, cặp SỐNG SÓT sau exclusion
  excluded_by[]                       # cặp bị exclusion loại, để giải thích trên Topics
  late_discovery                      # boolean, §5.3
  pending_since_window_sequence       # integer | null
  selected_via_backfill               # boolean, §6.3
  backfill_ledger_id                  # ulid | null
  reference_reason                    # chỉ có nghĩa khi item_type = 'prior_reference', §8
  work_version_label                  # chỉ khi reference_reason = 'new_work_version', §8.4
  identity_state                      # 'active' | 'quarantined' (selection.md §2)
}
```

`contracts/schemas/report.schema.json` trải các trường này ra ở mức read model cho tiện đọc;
ở mức bảng chúng là các khóa của một cột `json` đã tồn tại.

Owner có thể bỏ một mục pending bằng hành động tường minh → `state = 'abandoned_by_owner'`. Hệ
thống **không** tự bỏ; không có timeout nào biến pending thành abandoned.

### 5.4 Oracle

- **O-5.1 (I06).** Sau một commit publish tiến con trỏ:
  `#pending_item_ledger[state='pending']` sau = `#pending_item_ledger[state='pending']` trước
  − (số hàng chuyển `resolved_reported_late` hoặc `abandoned_by_owner` **trong chính commit
  đó**) + (số hàng pending mới tạo trong commit đó). Không có hàng nào biến mất khỏi sổ.
- **O-5.2 (đối chứng, phải FAIL).** Một triển khai xóa hàng pending khi coverage tiến, hoặc chỉ
  xét mục trong cửa sổ mới: mục thiếu summary ở kỳ N không bao giờ xuất hiện lại → FAIL.
  Fixture `e-late-analysis-pending-then-late-discovery.json`.
- **O-5.3 (B17/AMD-B17).** `report.quality = 'complete'` **chỉ khi**
  `#pending_item_ledger[state='pending' AND first_pending_window_id = cửa sổ của report này]` = 0.
  Có mục pending mà `quality = 'complete'` là FAIL.

---

## 6. Sổ backfill N ngày: đúng một lần cho một subscription (D28, B04)

### 6.1 Tham số

| Tham số | Giá trị | Đơn vị | Trạng thái | Lý do |
| --- | --- | --- | --- | --- |
| `backfill_days` (N) | 7 | ngày | `PROVISIONAL` (REQ-OQ04, baseline §5 OQ defaults) | Con số đề xuất trong SRC-SPEC §13.1 hàng 4; Owner trả lời, không chặn |
| `backfill_max_extension` | 30 | ngày | `PROVISIONAL` | Trần cứng để một giá trị N nhập nhầm không kéo lùi biên coverage vô hạn |

N được lưu trong `settings['reporting.backfill_days']` và **sao chép** vào
`backfill_ledger.backfill_days` tại lúc tạo hàng entitlement, để đổi N về sau không viết lại
lịch sử.

### 6.2 Định danh activation: khóa theo **chữ tag đã chuẩn hóa**, không theo `tag.id`

`normalize_tag_text(s)` = NFC → trim hai đầu → casefold → gộp mọi chuỗi khoảng trắng liên tiếp
thành một dấu cách. Hàm thuần túy, tất định, không gọi mạng (cùng tinh thần với
`contracts/data/identity.md` §2).

`subscription_identity_hash` = **sha256 hex của `owner_id + "\n" + văn bản tag đã chuẩn hóa`**
(định nghĩa nguyên văn theo PC02-FIX3 / `entities.yaml`; quy tắc chuẩn hóa là hàm
`normalize_tag_text` ở ngay trên). Lưu ý đây **không** phải `sha256(JCS(...))` như PC04 đề nghị
ban đầu — ruling chọn dạng nối chuỗi đơn giản hơn và PC04 dùng đúng dạng đã ruled.

`activation_sequence` tăng mỗi lần một tag mang chính `normalized_text` đó chuyển sang
`state = 'active'` (tạo mới hoặc thêm lại).

**Quy tắc add → remove → re-add (`PROVISIONAL`):** thêm lại một tag đã bỏ **là một activation
mới** (`activation_sequence` tăng) nhưng **không** cấp entitlement backfill mới nếu
`subscription_identity_hash` đó đã tiêu thụ backfill ở một activation trước.

Ba cột dưới đây **đã tồn tại** trên `backfill_ledger` sau PC02-FIX3 (CR-PC04-02 đã được đáp);
tên và enum lấy nguyên văn `entities.yaml`:

| Cột | Giá trị |
| --- | --- |
| `subscription_identity_hash` | như trên; NOT NULL |
| `entitlement` | `granted` \| `consumed` \| `denied_already_consumed` |
| `entitlement_reason` | văn bản tự do; bắt buộc có nội dung khi `entitlement = 'denied_already_consumed'` |

Ràng buộc: **`ux_backfill_subscription_consumed`** =
`UNIQUE(owner_id, subscription_identity_hash) WHERE consumed_in_report_id IS NOT NULL`
— **đúng một** lần tiêu thụ cho mỗi subscription identity trong toàn bộ đời sống hệ thống. Đây
là điều làm quy tắc "đúng một lần" của D28 thực thi được ở mức schema, thay vì chỉ là câu chữ:
`ux_backfill_tag_activation` khóa theo `tag_id`, mà mỗi lần thêm lại sinh một `tag.id` mới.

**Vì sao không cấp lại.** SRC-SPEC §8.2 hàng 4 nói entitlement là "đúng một lần" và đưa sẵn lối
thoát cho nhu cầu đào sâu: "Muốn đào sâu hơn thì bấm **quét lại kho**" (§7). Nếu re-add cấp lại
backfill thì một chuỗi bỏ–thêm lại sẽ kéo lùi biên coverage nhiều lần và làm "đúng một lần" mất
nghĩa. *Phương án bị bác:* khóa theo `tag.id` — vì `ux_tag_owner_text_active` là partial index
trên `state='active'`, mỗi lần thêm lại sinh một `tag.id` mới, nên khóa theo `tag.id` tương
đương "cấp lại mỗi lần re-add".

Đổi **chữ** của tag (ví dụ "graph neural networks" → "graph neural nets") tạo một
`subscription_identity_hash` khác và **được** cấp entitlement mới. Đây là hệ quả có chủ ý và
được ghi lại: hệ thống không đoán hai chuỗi khác nhau là cùng một mối quan tâm.

### 6.3 Backfill áp dụng thế nào vào biên

Backfill **không** tạo cửa sổ coverage riêng và **không** lùi `coverage_window.window_from`.
Nó chỉ nới **tập ứng viên** của tag đang được cấp:

```text
candidate_range(tag T) =
    nếu T có entitlement 'granted' chưa tiêu thụ:
        [ max(coverage_from − backfill_days, coverage_from − backfill_max_extension),
          coverage_to )
    ngược lại:
        [ coverage_from, coverage_to )
```

Cửa sổ coverage ghi vào sổ vẫn là `[coverage_from, coverage_to)`. Lý do: coverage là phát biểu
về **tiến độ của con trỏ**, còn backfill là một lần nới truy vấn cho một tag; trộn hai thứ sẽ làm
chuỗi cửa sổ chồng lấn và phá I06.

Mục được chọn nhờ backfill mang `report_item.selected_via_backfill = true` và
`report_item.selection_reason.backfill_ledger_id`. Nó vẫn là `new_discovery` nếu chưa từng được công bố (§8).

### 6.4 Điều kiện tiêu thụ

`backfill_ledger.consumed_in_report_id` và `consumed_at` được ghi **chỉ khi cả ba** điều kiện
đúng, và **chỉ trong** transaction publish:

1. Transaction publish commit thành công (`report.status = 'published'`).
2. Việc nới thực sự được áp: `candidate_range` rộng hơn `[coverage_from, coverage_to)`.
3. Phần nới sinh ra **ít nhất một** ứng viên, được ghi ra ở `report_item` **hoặc**
   `pending_item_ledger` trong cùng commit.

Hệ quả có chủ ý:

- **Builder crash / rollback** → không commit → không tiêu thụ (SRC-PLAN §9.2).
- **`TAG_VERSION_STALE` / `EMBEDDING_GENERATION_MISMATCH`** → abort → không tiêu thụ.
- **Model lỗi** (không có summary nào) → vẫn commit được với `quality = 'partial'`; entitlement
  **được** tiêu thụ **vì** mọi ứng viên tìm thấy đã nằm trong `pending_item_ledger` và chắc
  chắn xuất hiện lại ở kỳ sau (§5.2). Nếu phần nới **không** tìm thấy ứng viên nào thì điều
  kiện 3 sai và entitlement **ở lại chưa tiêu thụ** — quét lại một khoảng rỗng là truy vấn dữ
  liệu thuần túy, không tốn AI, nên không có lý do gì để đốt entitlement.

### 6.5 Oracle

- **O-6.1 (D28).** Với mọi owner:
  `#backfill_ledger[consumed_in_report_id IS NOT NULL]` nhóm theo
  `subscription_identity_hash` không có nhóm nào có số hàng > 1.
- **O-6.2 (add→remove→re-add).** Thêm tag T (activation 1) → publish tiêu thụ backfill → bỏ T →
  thêm lại T: hàng activation 2 có `entitlement = 'none'`,
  `entitlement_reason = 'already_consumed_for_subscription_identity'`, và
  `report.coverage_from` của kỳ kế tiếp **không** bị kéo lùi.
  Fixture `j-backfill-add-remove-readd.json`.
- **O-6.3 (crash).** Crash giữa build: `#report[status='published']` không đổi,
  `#report_item` không đổi, `#coverage_window` không đổi, và
  `backfill_ledger.consumed_in_report_id IS NULL` vẫn đúng.
  Fixture `k-builder-crash-backfill-not-consumed.json`.
- **O-6.4 (AC-06 kèm theo).** Ở kỳ tái xuất hiện của các mục cũ, provider call counter delta = 0
  cho cùng analysis key và generation; `#analysis_generation` và `#analysis_attempt` không đổi.
  Fixture `b-tag-removed-then-readded-reuse-analysis.json`.

---

## 7. Quét lại kho: lệnh riêng, sổ riêng

`tag.rescan_corpus` (ports.yaml) là lệnh của owner từ màn hình Topics, idempotent theo
`request_id`. Nó dùng `rescan_ledger` (bảng do `contracts/modules.yaml` giao cho
`MOD-tag-service`; hình dạng đề xuất ở §9 → **CR-PC04-01**).

Ràng buộc âm, tất cả đều là điều kiện FAIL nếu vi phạm:

1. **Không** ghi `coverage_window`; **không** đổi `predecessor_window_id` của bất kỳ cửa sổ nào.
2. **Không** ghi hay đổi `first_announced_ledger`. Mục đã công bố vẫn hiện dạng tham chiếu có
   ngày (§8).
3. **Không** đọc và **không** ghi `backfill_ledger`; rescan không tiêu thụ và không cấp
   entitlement.
4. **Không** tạo `report` hay `outbox_intent`. Kết quả rescan là một read model gắn với tag
   (`rescan_ledger` + danh sách target khớp), **không** phải một kỳ báo cáo và **không** gửi
   digest. Lý do: chỉ report mới được publish, và chỉ publish mới được tiến coverage (§4.4);
   cho rescan tạo report sẽ mở một đường thứ hai làm con trỏ tiến.
5. **Được phép** xếp hàng `analysis.enqueue_tasks` cho target khớp mà chưa có summary — đó là
   ý nghĩa của "đào sâu". Chi phí AI vì thế tỉ lệ với số mục rescan; UI phải hiện con số ước
   tính trước khi chạy (yêu cầu chuyển PC07).

**Oracle O-7.** Trước/sau một `tag.rescan_corpus`: `#coverage_window`, `#report`,
`#first_announced_ledger`, `#backfill_ledger[consumed_in_report_id IS NOT NULL]` và
`#outbox_intent` **đều không đổi**; `#rescan_ledger` tăng đúng 1.

---

## 8. First-announcement và tham chiếu (I07, REQ-D29, REQ-AC09) — đóng CR-PC02-06

### 8.1 Sổ `first_announced_ledger` (bảng đã có ở entities.yaml)

PC02 đã khóa hình dạng. PC04 dùng **nguyên văn**, không đổi tên cột:

| Cột | Ý nghĩa PC04 dùng |
| --- | --- |
| `id`, `owner_id` | — |
| `canonical_work_id` | FK → `work.id`; **phải là work đã resolve** (`identity_state = 'active'`) |
| `first_report_id` | FK → `report.id` của kỳ công bố lần đầu |
| `first_announced_at` | `= report.published_at` của kỳ đó; là "ngày D" của REQ-AC09 |
| `merge_audit_id` | FK → `identity_merge_audit.id`; NOT NULL khi hàng này là kết quả của một merge |
| `superseded_by_merge_id` | FK → `identity_merge_audit.id` nếu hàng bị thay bởi một merge sau đó |
| — | `UNIQUE(owner_id, canonical_work_id)` ← **thực thi I07** ở mức schema |

Hàng **có hiệu lực** của một work là hàng có `superseded_by_merge_id IS NULL`. Hàng có
`superseded_by_merge_id NOT NULL` là **bằng chứng lịch sử**: nó tiếp tục trỏ tới work đã bị
`merged`, nên ràng buộc "canonical_work_id phải là work active" chỉ áp cho hàng đang có hiệu
lực. Đây là một **thu hẹp phạm vi ràng buộc**, không phải cột mới → **CR-PC04-01** gửi PC02.

**Target chỉ-có-post không có hàng ở sổ này**: khóa của sổ là `canonical_work_id`, còn post-only
không có canonical identity (identity.md §4). Với chúng, "đã công bố" được suy ra từ lịch sử
bất biến:

```text
already_announced(post_target P) :=
    EXISTS report_item ri
      JOIN report r ON r.id = ri.report_id
     WHERE r.status = 'published'
       AND ri.target_key = P.target_key
       AND ri.item_type = 'new_discovery'
```

Truy vấn này tất định và không cần bảng mới, vì `report_item` của report đã publish là bất biến
(I05) và `merge identity` không viết lại `target_key` của chúng. Nếu post-only về sau được liên
kết tới một work (identity.md §4 "post-only promotion"), tham chiếu cũ **không** bị viết lại;
work mới đi theo đường `first_announced_ledger` bình thường.

### 8.2 Quy tắc cơ bản

1. Hàng được ghi **chỉ trong transaction publish** (§4.5), **chỉ cho** item có
   `item_type = 'new_discovery'`.
2. Tại selection, một ứng viên đã có hàng `active` → bắt buộc `item_type = 'prior_reference'`,
   kèm `first_announced_report_id` và ngày `first_announced_at` để hiển thị "đã báo cáo 12/03"
   (SRC-SPEC §8.2 hàng 5). **Không có nhánh nào** cho phép công bố lại như phát hiện mới.
3. Một mục `prior_reference` vẫn có `analysis_id` của bản phân tích đang được đọc và vẫn Save
   được; nó chỉ khác ở loại mục và ở câu chữ.
4. Việc liên kết mục cùng hướng đã báo cáo trước dựa trên **tag chung và paper cùng được dẫn**,
   **không dùng AI** (REQ-D30, ràng buộc âm).

### 8.3 Sau identity merge — quyết định đóng CR-PC02-06

`PROVISIONAL`. **Work thắng kế thừa first-announcement sớm nhất trong các work bị hợp nhất; mọi
hàng còn lại được giữ dưới dạng bằng chứng có audit; một report về sau chỉ được hiện work đó
dưới dạng tham chiếu có ngày, không bao giờ là phát hiện mới.**

Thuật toán, chạy **trong cùng transaction** `TXN-identity-merge` (điểm móc do PC02 cam kết ở
`contracts/data/identity.md` §6.5 và `entities.yaml` → `first_announced_ledger` → `i07_interface`),
với `Rw` = hàng có hiệu lực của `winner_work_id` và `Rl` = hàng có hiệu lực của `loser_work_id`:

| Trường hợp | Hành động | `identity_merge_audit.moved_counts` → khóa `first_announced` |
| --- | --- | --- |
| Không bên nào có hàng | Không làm gì | `0` |
| Chỉ `Rw` tồn tại | Không làm gì (winner đã có ngày công bố của chính nó) | `0` |
| Chỉ `Rl` tồn tại | `Rl.canonical_work_id := winner_work_id`; `Rl.merge_audit_id := audit.id`. **Giữ nguyên** `first_report_id` và `first_announced_at` | `1` |
| Cả hai tồn tại | Chọn cặp `(first_report_id, first_announced_at)` **sớm hơn** theo thứ tự tất định `(first_announced_at, first_report_id theo thứ tự byte)`. Ghi cặp đó vào `Rw` và đặt `Rw.merge_audit_id := audit.id`. `Rl` **không bị xóa**: giữ `canonical_work_id = loser_work_id` và nhận `Rl.superseded_by_merge_id := audit.id` | `2` |

Trường hợp cuối là cách duy nhất thỏa đồng thời ba ràng buộc đã khóa:
`UNIQUE(owner_id, canonical_work_id)` (không thể có hai hàng cùng trỏ winner), "không xóa bằng
chứng" (B15), và "một canonical work chỉ có một first-announcement" (I07). Hàng `Rl` sau đó
không còn hiệu lực nhưng vẫn đọc được để truy vết.

Quy tắc chọn phải **toàn phần và tất định** vì oracle của fixture so sánh chính xác ngày nào
được kế thừa — cùng lý do PC02 đưa ra cho `winner_selection` (identity.md §6.2).

Ràng buộc kèm theo:

- `report_item` của report đã `published` **không** bị viết lại (I05, I17, entities.yaml
  `explicitly_not_moved`). Kỳ cũ vẫn ghi `target_key` cũ; cầu nối là
  `identity_merge_audit` + trường `target_key_at_announcement` của `first_announced_ref` — DẪN XUẤT ở read model (`report.schema.json`), không phải cột của sổ.
- `UNIQUE(owner_id, canonical_work_id)` giữ I07 sau merge: đúng **một** hàng có hiệu lực trỏ
  `winner_work_id`.
- Merge **không** bị chặn khi không bên nào có hàng: `moved_counts.first_announced = 0` là kết
  quả hợp lệ, **khác** với `null` mà PC02 để tạm khi policy chưa khóa.
- `performed_by` của merge vẫn chỉ nhận `system_automatic_on_evidence` | `owner_manual`; AI
  không bao giờ là nguồn bằng chứng (B15).

*Phương án bị bác và lý do.* (i) "Work thắng bắt đầu lại như chưa công bố" — vi phạm REQ-D29
trực tiếp: cùng một công trình được báo hai lần. (ii) "Lấy ngày công bố **muộn hơn**" — mất
thông tin: người dùng đã đọc mục đó từ ngày sớm hơn, hiển thị ngày muộn là sai sự thật. (iii)
"Xóa hàng của loser" — mất bằng chứng, trái tinh thần B15 ("giữ nguồn").

### 8.4 Phiên bản mới của paper

arXiv `v1` và `v2` là **một** work với hai `work_version` (identity.md §2.2), nên:

- Phiên bản mới **không** tạo first-announcement mới; hàng ledger cũ giữ nguyên.
- Work xuất hiện lại dưới dạng `item_type = 'prior_reference'` với
  `reference_reason = 'new_work_version'` và `work_version_label` của phiên bản mới.
- Phân tích lại là hợp lệ và tạo `analysis_generation` mới với `reason = 'new_work_version'`
  (entities.yaml `work_version` → `reanalysis_rule`); bản cũ được giữ (REQ-D26).

*Đây là một đọc hiểu `PROVISIONAL`*: SRC-SPEC không nói phiên bản mới có được báo lại như phát
hiện mới hay không. Phương án ngược lại (coi v2 là phát hiện mới) phá `UNIQUE` của I07 trên
canonical identity, nên bị bác.

### 8.5 Saved độc lập với subscription

- Bỏ tag **không** đụng `saved_item` và **không** đụng `saved_snapshot` (SRC-SPEC §8.2 hàng 7,
  REQ-D55, I08). Saved vẫn đọc được kể cả khi bài gốc bị xóa trên X (REQ-AC12).
- Save **không** ghi `first_announced_ledger`, **không** ghi `coverage_window`, **không** làm
  một target được chọn ở bất kỳ kỳ nào.
- Backfill và rescan **không** đọc và **không** ghi Saved.
- Merge identity dời **con trỏ** `saved_item` theo move-set của PC02 nhưng **không** đụng
  `saved_snapshot` (I17).

### 8.6 Oracle

- **O-8.1 (AC-09, I07).** `#first_announced_ledger` nhóm theo `(owner_id, canonical_work_id)`
  không có nhóm nào > 1. Với work W đã công bố ở kỳ ngày D: mọi `report_item` ở kỳ sau trỏ W có
  `item_type = 'prior_reference'` và `first_announced_report_id` = report của ngày D.
  Fixture `h-already-announced-work-becomes-reference.json`.
- **O-8.2 (sau merge).** Sau `identity.merge_works`:
  `#first_announced_ledger[superseded_by_merge_id IS NULL AND canonical_work_id = winner_work_id]` = 1;
  `first_announced_at` của hàng đó = `MIN` của các giá trị trước merge;
  `identity_merge_audit.moved_counts.first_announced` khớp bảng §8.3; và tập
  `report_item.target_key` của **mọi** report `published` **không đổi**.
  Fixture `i-identity-merge-single-first-announced.json`.
- **O-8.3 (đối chứng, phải FAIL).** Triển khai reset first-announcement khi merge, hoặc viết
  lại `report_item.target_key` của kỳ đã publish → FAIL cả I05 lẫn I07.
- **O-8.4 (Saved).** Bỏ tag T rồi đọc Saved: `#saved_item[state='active']` không đổi và tập
  `saved_snapshot.content_hash` không đổi.

---

## 9. Những gì file này yêu cầu ở gói khác (change requests)

> **Cập nhật PKT-PC04-FIX1.** `CR-PC04-01(a,c)`, `CR-PC04-02`, `CR-PC04-04`, `CR-PC04-09` và
> `CR-PC04-10` đã được đáp bởi PC02-FIX3 / PC01-FIX3. Các cột được kiểm lại theo
> `contracts/data/entities.yaml` sha256
> `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece`; **không** fixture nào của
> gói này còn cần marker `pending_cr`.

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-PC04-01` | PC02 | **ĐÃ ĐÁP bởi PC02-FIX3 cho (a) và (c).** (a) `coverage_window` cần hai cột `ingest_sequence_from` (inclusive) và `ingest_sequence_to` (exclusive) — vị từ thành viên thật sự của một kỳ (§4.3); biên thời gian một mình không an toàn với transaction ingest commit muộn. (b) Thu hẹp phạm vi ràng buộc `first_announced_ledger.canonical_work_id` "phải là work active" xuống chỉ các hàng có `superseded_by_merge_id IS NULL` (§8.1). (c) `contracts/modules.yaml` gọi bảng coverage là `coverage_ledger` trong `MOD-report-service.data_owner_of`, còn `entities.yaml` đặt tên `coverage_window`; đề nghị PC01/PC02 thống nhất về `coverage_window`. |
| `CR-PC04-02` | PC02 | **ĐÃ ĐÁP bởi PC02-FIX3** (`ux_backfill_subscription_consumed`). `backfill_ledger` cần `subscription_identity_hash`, `entitlement`, `entitlement_reason` và partial UNIQUE (§6.2). Không có chúng, quy tắc add–remove–re-add không thực thi được ở mức schema: `ux_backfill_tag_activation` khóa theo `tag_id`, mà mỗi lần thêm lại sinh một `tag.id` mới. |
| `CR-PC04-10` | PC02 | **MỚI, do F-A1R2-01.** PC04 lẽ ra phải mở CR cho `report.report_build_id` ngay từ đầu nhưng đã không làm — audit A1-R2 bắt được. PC02-FIX3 đã khai cột này (`UNIQUE ux_report_owner_build_id`); CR này ghi lại để chuỗi truy vết không có lỗ hổng. **Đã đáp.** |
| `CR-PC04-03` | PC02 | Ghi quy tắc kẹp đơn điệu giữa `discovered_at` và `ingest_sequence` (§1.3) vào `entities.yaml` → `conventions` → `clock_trust`. |
| `CR-PC04-04` | PC03 | Không còn cần mã lỗi mới: CAS thua đã có `CONFLICT` trong `contracts/errors.yaml` với `operations` gồm `report.publish`. CR này thu lại chỉ còn một điểm: `contracts/ports.yaml` (PC01) liệt kê `error_codes` của `report.publish` **chưa có** `CONFLICT`; đề nghị bổ sung để ports và errors khớp nhau. |
| `CR-PC04-05` | PC06 | Task `direction_phrasing` chỉ được **diễn đạt lại** object đã tính ở `selection.md` §8; cấm AI tự chọn thành viên, tự tính mật độ, hoặc đổi nhãn khỏi "ứng viên để đọc sâu". Khối phải hiển thị được khi task này lỗi hoặc không có provider. |
| `CR-PC04-06` | PC09 | Đăng ký scenario mới `SC37` (backfill add→remove→re-add) và `SC38` (builder crash không tiêu thụ backfill) vào `acceptance/scenarios.yaml`. PC03 đã dùng tới `SC36`, nên PC04 lấy `SC37+`. |
| `CR-PC04-08` | PC03 | Kết quả CR-PC03-06 (§4.7.1): giữ hàng `report(status='aborted')` cho kỳ rỗng nhưng **bắt buộc** `abort_reason`. Đề nghị PC03 ghi `abort_reason` vào T-RP-03 / T-RP-04 / T-RP-05 / T-RP-06 / T-RP-07 để `aborted` không còn nhập nhằng. |
| `CR-PC04-09` | PC02 | **ĐÃ ĐÁP bởi PC02-FIX3** (enum dùng `cas_conflict`/`builder_failure`). Thêm cột `report.abort_reason` (enum `empty_period` \| `tag_version_stale` \| `embedding_generation_mismatch` \| `cas_lost` \| `builder_crash_or_stale`), `NOT NULL khi status='aborted'`. |
| `CR-PC04-07` | PC07 | Trước khi chạy `tag.rescan_corpus`, UI phải hiện số mục ước tính sẽ phải gọi summary (§7 mục 5) — rescan là đường duy nhất làm chi phí AI tỉ lệ với số bài trong kho thay vì số mục báo cáo. |

`CR-PC02-06` được **đóng** bằng §8.3 của file này (policy first-announcement sau merge). PC02
để `moved_counts.first_announced = null` khi policy chưa khóa; từ đây giá trị hợp lệ là một số
nguyên `0`, `1` hoặc `2` theo bảng §8.3, và `null` không còn là giá trị hợp lệ.

---

## 10. Những gì file này KHÔNG chứng minh

- Không chứng minh code chạy đúng: chưa có code (SRC-PLAN §14.2, cấp E0).
- Không chứng minh cửa sổ coverage phản ánh đúng những gì có trên X: giới hạn bao phủ nguồn là
  vấn đề của B05/PC05, và `coverage_note` → `observed_data_only` tồn tại chính vì điều đó.
- Không chứng minh tham số của §6 (N = 7) là đúng với nhu cầu Owner: REQ-OQ04 vẫn mở.
- Không thay thế `contracts/state/report.yaml` (PC03): bảng transition, guard và effect của
  `building → published | aborted` thuộc PC03.
- Không định nghĩa cách hiển thị (PC07) hay schema task AI (PC06).
