---
contract_id: CT-reporting-selection
version: 0.1.0
status: draft
owner_role: reporting contract owner
source_refs:
  - "SRC-SPEC §3.4 D22, D46, D47, D48, D49, D59"
  - "SRC-SPEC §3.5 D17, D25, D29, D30, D52, D53, D54"
  - "SRC-SPEC §8.1 (ba lớp tách rời), §8.2"
  - "SRC-SPEC §10.1 (bốn tác vụ; chọn mục là truy vấn dữ liệu), §10.3, §10.4"
  - "SRC-SPEC §12 AC-05, AC-06, AC-09, AC-10"
  - "SRC-SPEC §3.8 A2, A4"
  - "SRC-PLAN §3 B01, B04, B14, B17"
  - "SRC-PLAN §7 I05, I06, I07, I12"
  - "SRC-PLAN §9.2, §9.3"
  - "SRC-PLAN §10 EMBEDDING_GENERATION_MISMATCH, TAG_VERSION_STALE, IDENTITY_CONFLICT"
  - "SRC-PLAN §11 PC04"
requirement_refs:
  [REQ-D22, REQ-D25, REQ-D29, REQ-D30, REQ-D46, REQ-D47, REQ-D48, REQ-D49, REQ-D52,
   REQ-D53, REQ-D54, REQ-D59, REQ-AC05, REQ-AC06, REQ-AC09, REQ-AC10, REQ-A2, REQ-A4,
   REQ-S1.4-01, REQ-S1.4-02, REQ-S8.1-01, REQ-S8.1-02, REQ-S10.1-04, REQ-S10.3-04,
   REQ-S10.4-03, REQ-OQ08, REQ-P0-02, REQ-P0-05, REQ-P0-07]
decision_refs: [B01, B04, B14, B15, B17, AMD-B01, AMD-B04, AMD-B17, ADR-0004]
invariant_refs: [I05, I06, I07, I12]
producers: [MOD-report-service]
consumers: [MOD-web-ui, MOD-backend-api, MOD-telegram-adapter, MOD-analysis-service, MOD-embedding-service, MOD-tag-service]
dependencies:
  - contracts/data/entities.yaml
  - contracts/data/identity.md
  - contracts/modules.yaml
  - contracts/ports.yaml
  - contracts/reporting/time-and-tags.md
  - contracts/schemas/report.schema.json
  - contracts/schemas/target.schema.json
  - contracts/state/report.yaml
  - acceptance/fixtures/reporting/
scope: >-
  Ngữ nghĩa **chọn nội dung** cho một kỳ báo cáo và ngữ nghĩa **mật độ vector** của khối "hướng
  đang nổi". Selection là một truy vấn dữ liệu tất định, không có AI trong vòng lặp. File này
  khóa: đầu vào, thứ tự ưu tiên alias/exclusion, phép đo tương đồng, chính sách ngưỡng, ghim
  embedding generation, tie-break, hạn mức mỗi kỳ, và thuật toán mật độ kèm ví dụ số tái lập
  được. Không định nghĩa prompt hay schema của task AI (PC06).
verification: >-
  E0 SELF_VALIDATION ở gói PC04: EV-PC04-01 (schema + fixture), EV-PC04-02 (tính lại ví dụ số
  §8.7 bằng script trong scratch dir và so với các con số ghi trong file này), EV-PC04-03
  (operation_id / entity được trích dẫn có tồn tại). E1–E4 `NOT_RUN`.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Chọn nội dung kỳ báo cáo và mật độ vector

> **Trạng thái quyết định.** B14 và B17 vẫn **OPEN**; mọi tham số số học trong file này là
> `PROVISIONAL` và **chưa được hiệu chỉnh**. Không mục nào ở đây được đọc là bằng chứng rằng
> ngưỡng hay thuật toán hoạt động tốt: đó là REQ-A2 (ngưỡng) và REQ-A4 (mật độ), cả hai đều
> `KC` và cần dữ liệu thật.

## 1. Selection là truy vấn dữ liệu, không phải việc của AI

SRC-SPEC §10.1 nói thẳng: "Việc **chọn** mục và **tính** hướng đang nổi là truy vấn dữ liệu,
không phải việc của AI. AI chỉ diễn đạt lại kết quả đã tính."

Ba lớp của SRC-SPEC §8.1 không được lẫn:

| Lớp | Là gì | Do ai quyết | Chạy khi nào | Bảng |
| --- | --- | --- | --- | --- |
| 1. Nhãn chủ đề | Bài này nói về cái gì | AI, mô tả mở (REQ-D22) | Một lần lúc thu thập | `work_label` |
| 2. Subscription | Tôi đang theo cái gì | Người dùng | Sửa bất cứ lúc nào | `tag`, `tag_alias`, `tag_exclusion` |
| 3. Chọn nội dung | Bài nào vào báo cáo | **Truy vấn embedding** | Lúc publish báo cáo | `report_item` |

Chính vì tách như vậy mà đổi tag **không** cần chạy lại AI (REQ-AC06, I04). Một triển khai gọi
model để hỏi "bài này có khớp tag không" vi phạm REQ-D22 và làm chi phí AI tỉ lệ với số bài ×
số tag.

`selection_version` = `0.1.0` = phiên bản của thuật toán trong file này. Nó được ghi bất biến
vào `report.selection_version`. Đổi bất kỳ quy tắc nào ở §3–§8 phải bump giá trị này; báo cáo
tạo bởi hai `selection_version` khác nhau **không so sánh trực tiếp được** (ảnh hưởng §8.5).

## 2. Đầu vào của một lần selection

| Đầu vào | Nguồn | Ghim ở đâu |
| --- | --- | --- |
| `tag_config_version` đã đóng băng | `tag.get_active_config_version` lúc build, `tag.freeze_config_version` lúc publish | `report.tag_config_version_id` |
| `embedding_generation` đang `active` | `embedding.get_active_generation` | `report.embedding_generation_id` |
| Vector của tag/alias/exclusion | `tag_vector` với đúng `embedding_generation_id` | — |
| Vector của nhãn | `work_label.vector` với đúng `embedding_generation_id`, `vector IS NOT NULL` | — |
| Cửa sổ ứng viên | `contracts/reporting/time-and-tags.md` §4.3 + §5.2 + §6.3 | `report.coverage_from/to` |
| Sổ first-announcement | `first_announced_ledger` | `report_item.item_type` |

Tập ứng viên của một kỳ:

```text
candidates = { target : ingest_sequence_from <= target.ingest_sequence < ingest_sequence_to }
           ∪ { target : có hàng pending_item_ledger state='pending' }
           ∪ { target : nằm trong phần nới backfill của một tag có backfill_ledger.entitlement = 'granted' }
```

`ingest_sequence_from` / `ingest_sequence_to` là cột thật của `coverage_window`, và
`backfill_ledger.entitlement` ∈ `granted | consumed | denied_already_consumed` — cả hai đã được
PC02-FIX3 khai (xem `contracts/reporting/time-and-tags.md` §4.3, §6.2).

Target là tagged union `work | post` theo `contracts/schemas/target.schema.json`. Chỉ
`work.identity_state = 'active'` và `post.identity_resolution = 'resolved_post_only'` là ứng
viên hợp lệ; `merged` phải được giải theo quy tắc tra cứu identity ở `contracts/data/identity.md` §3 ("Tra cứu: `identity_alias` là một hàm"), đi theo `work.merged_into_work_id` tới hàng `identity_state = 'active'`
và `pending` chưa phải target (identity.md §4).

**Work đang `quarantined`** (có `identity_conflict` mở): **vẫn được chọn** nếu khớp tag — dữ
liệu không bị chặn — nhưng bị loại khỏi phép đếm mật độ ở §8.4 và không được trình bày là hai
phát hiện độc lập (identity.md §5.3, SRC-PLAN §10 `IDENTITY_CONFLICT`). `report_item` của nó
mang `identity_state = 'quarantined'` để PC07 hiển thị cảnh báo.

## 3. Phép đo tương đồng

- Metric: **cosine similarity** giữa hai vector cùng `embedding_generation_id`.
- `embedding_generation.normalization`:
  - `l2` → vector đã chuẩn hóa, cosine = tích vô hướng. Đây là dạng khuyến nghị.
  - `none` → phải chia cho tích hai chuẩn L2 tại lúc so sánh. Nếu một vector có chuẩn `0` thì
    **không** so sánh được: mục đó bị loại khỏi selection với lý do `zero_norm_vector`, cấm coi
    là điểm `0` và cấm coi là khớp.
- MVP quét **tuyến tính** trong SQLite thuần (REQ-D49); không có vector index (REQ-P1-04).
- **Làm tròn.** Mọi giá trị similarity được làm tròn **half-up về 4 chữ số thập phân** trước
  khi so sánh với ngưỡng và trước khi ghi. Lý do: hai lần chạy trên hai máy phải cho cùng tập
  được chọn; so sánh số thực chưa làm tròn không tái lập được. Ngưỡng cũng được biểu diễn với
  đúng 4 chữ số thập phân.

**Cấm** so sánh vector khác `embedding_generation_id`, khác `dimension`, khác `model_name` hoặc
khác `model_version` — đó là I12, xem §5.

## 4. Alias và exclusion: thứ tự ưu tiên

### 4.1 Điểm khớp của một target với một tag

Với target `X` và tag `T`:

```text
subjects(T) = { vector của chính T }  ∪  { vector của mọi tag_alias của T có state='active' }
labels(X)   = { work_label.vector : target_key = X, embedding_generation_id = G, vector NOT NULL }

score(X, T)      = max over (l ∈ labels(X), s ∈ subjects(T)) of cosine(l, s)      [round 4dp]
matched_via(X,T) = 'tag' nếu cặp đạt max là (l, vector của T), ngược lại 'alias'
```

Nếu `labels(X)` rỗng (chưa gắn nhãn, hoặc generation đang build và `vector IS NULL`) thì `X`
**không** được chọn ở kỳ này và được ghi `pending_item_ledger` với
`reason = 'missing_summary'` chỉ khi nó đã từng được chọn vì lý do khác; nhãn thiếu **không**
tự tạo pending, vì gắn nhãn thuộc pipeline ingest chứ không thuộc report builder.

Khi có nhiều cặp đạt cùng giá trị max sau làm tròn, `matched_via` ưu tiên `'tag'` rồi mới
`'alias'`, và alias được chọn là alias có `id` nhỏ nhất theo thứ tự byte. Quy tắc phải toàn phần
để `report_item.selection_reason.matched_tags` tái lập được.

### 4.2 Ngưỡng: alias thừa hưởng, không có ngưỡng riêng

```text
θ(T) = tag.similarity_threshold nếu NOT NULL
       ngược lại settings['reporting.default_similarity_threshold']
```

**Alias không có ngưỡng riêng**: nó dùng đúng `θ(T)` của tag cha (entities.yaml: `tag_alias`
không có cột `similarity_threshold`, đây là ràng buộc có chủ ý). Lý do: từ đồng nghĩa là cách
diễn đạt khác của cùng một mối quan tâm; cho nó một ngưỡng riêng tạo một tham số chưa hiệu
chỉnh thứ hai cho cùng một khái niệm.

Khớp khi `score(X, T) >= θ(T)`.

### 4.3 Exclusion thắng

`tag_exclusion` có hai phạm vi (entities.yaml):

| `tag_id` | Phạm vi | Hiệu lực |
| --- | --- | --- |
| `NULL` | **Toàn cục** | Loại `X` khỏi **toàn bộ** selection của kỳ, dù `X` khớp bao nhiêu tag |
| `= T` | **Trong phạm vi tag T** | Bỏ riêng cặp khớp `(X, T)`; các tag khác của `X` vẫn sống |

```text
excl_score(X, E) = max over (l ∈ labels(X)) of cosine(l, vector của E)             [round 4dp]
θ_excl(E)        = θ(E.tag_id) nếu E.tag_id NOT NULL
                   ngược lại settings['reporting.default_similarity_threshold']
E kích hoạt khi   excl_score(X, E) >= θ_excl(E)
```

Ngưỡng loại trừ dùng lại ngưỡng của phạm vi tương ứng thay vì một tham số thứ ba
(`PROVISIONAL`, gắn REQ-A2): exclusion sống trong cùng không gian vector và cùng thang điểm;
thêm một núm chưa hiệu chỉnh nữa làm A2 không đánh giá được.

**Thứ tự áp dụng — và vì sao thứ tự không quan trọng.**

1. Tính toàn bộ `score(X, T)` cho mọi cặp (X, T). Không loại gì ở bước này.
2. Áp mọi exclusion phạm vi tag: bỏ các cặp bị kích hoạt.
3. Áp mọi exclusion toàn cục: bỏ toàn bộ X bị kích hoạt.
4. `X` được chọn khi còn **ít nhất một** cặp khớp sống sót.

Vì exclusion **chỉ xóa** và không bao giờ thêm, kết quả không phụ thuộc thứ tự duyệt exclusion.
Đó là điều làm selection tái lập được. Một triển khai "dừng ở exclusion đầu tiên khớp" cho cùng
kết quả cho bước 3 nhưng **sai** ở bước 2 — nên phải áp đủ.

`report_item.selection_reason.matched_tags` ghi **các cặp sống sót** kèm `score` và
`matched_via`; các cặp bị exclusion loại được ghi ở `report_item.selection_reason.excluded_by`
để màn hình Topics giải thích được vì sao một bài không xuất hiện (REQ-D46 "xem nhãn đang
khớp"). `entities.yaml` giao cho PC04 quyền khóa hình dạng của cột `selection_reason`; hình
dạng đầy đủ ở `contracts/reporting/time-and-tags.md` §5.3.

### 4.4 Oracle

- **O-4.1.** Target khớp tag `T1` (score 0.9) và bị exclusion toàn cục kích hoạt (score 0.85 ≥
  θ 0.80) → **không** có trong `report_item`, dù `score(X,T1)` cao hơn.
- **O-4.2.** Target khớp `T1` và `T2`, exclusion phạm vi `T1` kích hoạt → có trong
  `report_item` với `matched_tags` chỉ chứa `T2`.
- **O-4.3.** Đảo thứ tự các hàng `tag_exclusion` trong truy vấn → tập `report_item.target_key`
  và `report.content_hash` không đổi.

## 5. Ghim embedding generation (I12)

Toàn bộ một lần selection dùng **đúng một** `embedding_generation_id` `G`:

1. `G` = generation `state = 'active'` đọc bằng `embedding.get_active_generation` tại **build
   snapshot**, và được ghi vào `report.embedding_generation_id`.
2. Mọi `tag_vector` và mọi `work_label.vector` được dùng phải có `embedding_generation_id = G`.
3. Nếu **bất kỳ** subject vector nào của một tag/alias/exclusion đang có hiệu lực còn thiếu ở
   `G` → selection bị **chặn** với `EMBEDDING_GENERATION_MISMATCH`. **Cấm** rơi về generation
   cũ, **cấm** bỏ qua tag đó, **cấm** trộn.
4. Nếu generation active đổi giữa build snapshot và commit publish → transaction publish thất
   bại với `EMBEDDING_GENERATION_MISMATCH`; builder rebuild hoặc abort. Report đã publish
   **không bao giờ** bị sửa (I05). Vị từ mà PC04 cung cấp cho CAS của PC03 là
   `embedding_generation_matches(expected_embedding_generation_id)` — xem
   `contracts/reporting/time-and-tags.md` §4.5.
5. Trong lúc `embedding.start_generation_rebuild` đang chạy, generation mới ở `state='building'`
   và **không** được dùng cho selection; generation cũ vẫn `active` cho tới
   `embedding.activate_generation` (SRC-PLAN §9.3). `work_label.vector IS NULL` (đang tính) bị
   loại khỏi `labels(X)` — mục đó không được chọn ở kỳ này chứ **không** được coi là không khớp
   vĩnh viễn.

**Oracle O-5a — mặt ÂM (SC24).** Chèn một `work_label` thuộc generation khác vào tập ứng viên:
build phải trả `EMBEDDING_GENERATION_MISMATCH`, `#report[status='published']` không tăng,
`#report_item` không tăng, và **không** có phép cosine nào được thực hiện giữa hai generation.
Fixture `l-embedding-generation-switch-blocked.json`.

**Oracle O-5b — mặt DƯƠNG (SC52).** Đường đi ĐÚNG của một lần đổi model phải chạy được đầu tới
cuối: `embedding.start_generation_rebuild` tạo G2 ở `state='building'` trong khi G1 vẫn `active`
→ `embedding.generate_vectors` (model LOCAL ở server, REQ-D50) dựng đủ vector →
`embedding.activate_generation` **bị từ chối** khi `built_vector_count < expected_vector_count`
→ sau khi đủ, chuyển `active` trong MỘT transaction (`ux_embedding_generation_active` ép đúng một
hàng `active` tại mọi thời điểm quan sát được) → kỳ sau selection chỉ dùng G2, và G1 được **giữ
lại** ở `state='retired'` cùng toàn bộ vector cũ (REQ-D48 "giữ bản cũ").

Oracle đếm được: số phép cosine giữa hai generation khác nhau **= 0** trong toàn bộ chuỗi; một
kỳ báo cáo dựng GIỮA lúc rebuild vẫn mang `embedding_generation_id = G1`; kỳ sau mang `G2`;
không kỳ nào mang cả hai. Kỳ đầu sau khi chuyển mang
`insufficient_reason = 'generation_reset'` theo §8.5. Fixture
`n-embedding-generation-switch-positive.json`.

Hai oracle này là hai mặt của cùng một invariant: O-5a chứng minh việc trộn **bị chặn**, O-5b
chứng minh việc **không trộn** vẫn cho phép đổi model — một mình O-5a không loại trừ được một
triển khai chặn mọi thứ và không bao giờ đổi được generation.

## 6. Chính sách ngưỡng: chưa hiệu chỉnh, và phải nói rõ là chưa

REQ-D47 (`KC`) và REQ-A2 (`KC`) nói ngưỡng phải hiệu chỉnh bằng dữ liệu thật (gán nhãn tay
50–100 bài rồi dò ngưỡng). REQ-OQ08 ghi rõ: **không đặt một con số PROVISIONAL như thể đã biết**,
vì phải đo.

Cách file này giải quyết mâu thuẫn giữa "phải có số" (baseline §3 cấm để "TBD") và "không được
giả vờ đã biết":

| Khóa | Giá trị | Trạng thái | Ý nghĩa |
| --- | --- | --- | --- |
| `settings['reporting.default_similarity_threshold']` | `0.8000` | `PROVISIONAL_BOOTSTRAP` | Giá trị khởi động để hệ thống chạy được và để fixture tất định. **Không** phải kết quả đo |
| `settings['reporting.threshold_calibration_state']` | `uncalibrated` | bắt buộc | `uncalibrated` \| `calibrated`. Do quy trình A2 đặt, không do người dùng gõ |
| `settings['reporting.threshold_calibration_evidence_ref']` | `null` | bắt buộc | Con trỏ tới evidence record của A2 khi đã hiệu chỉnh |
| `tag.similarity_threshold` | `NULL` mặc định | — | Ghi đè cho từng tag; `NULL` = dùng giá trị mặc định |

Cổng thí nghiệm (chuyển PC09, `precode/gates.yaml`):

- Chừng nào `threshold_calibration_state = 'uncalibrated'`, mọi report mang
  `coverage_note.threshold_calibration_state = 'uncalibrated'` và UI phải nói rõ ngưỡng chưa
  được hiệu chỉnh. **Cấm** tuyên bố bất kỳ chỉ tiêu chất lượng nào của SRC-SPEC §1.4 khi ở
  trạng thái này.
- Tập dò ngưỡng và tập đánh giá phải **tách rời** (SRC-PLAN §14.2); rubric khóa **trước** khi
  dò. Sửa `0.8000` sau khi nhìn kết quả mà không có hai tập tách rời là hành vi bị cấm.

Lý do chọn `0.8000` làm giá trị khởi động: nó nằm giữa dải mà cosine của các model câu
đa ngôn ngữ thường coi là "cùng chủ đề", đủ chặt để fixture §8.7 có ranh giới rõ, và **đủ dễ
nhận ra là một giá trị tròn do người đặt** chứ không phải kết quả đo. Đây là lý do vận hành,
không phải bằng chứng.

## 7. Thứ tự, tie-break và hạn mức mỗi kỳ

### 7.1 Sắp xếp `report_item`

Khóa sắp xếp, áp theo đúng thứ tự này (tất cả tất định):

1. `item_type`: `new_discovery` trước `prior_reference` (khối "có gì mới" đứng trước phần
   tham chiếu).
2. `best_score` giảm dần — giá trị max của `matched_tags[*].score` sau làm tròn 4dp.
3. `discovered_at` tăng dần.
4. `ingest_sequence` tăng dần.
5. `target_key` tăng dần theo thứ tự byte UTF-8.

Khóa 4 và 5 làm cho thứ tự **toàn phần**: không tồn tại hai mục không phân biệt được.

### 7.2 Hạn mức

| Tham số | Giá trị | Đơn vị | Trạng thái | Lý do |
| --- | --- | --- | --- | --- |
| `settings['reporting.max_items_per_period']` | 50 | mục | `PROVISIONAL` (REQ-OQ05 chưa có số thật) | SRC-SPEC §10.4 yêu cầu có hạn mức vì mỗi mục vào báo cáo tốn một summary; 50 là mức một người đọc được trong một kỳ mà vẫn đủ rộng để §8 có mẫu |
| `settings['reporting.max_emerging_directions']` | 3 | hướng | `PROVISIONAL` | Khối đầu báo cáo phải đọc được trong vài giây; SRC-SPEC §1.4 đặt mục tiêu "≥ 1 hướng mỗi tuần", không phải danh sách dài |

Vượt hạn mức: các mục xếp sau vị trí thứ `max_items_per_period` **không bị bỏ**. Chúng được ghi
`pending_item_ledger` với `reason = 'budget_exceeded'` trong cùng transaction publish, và là ứng
viên ở kỳ sau (SRC-SPEC §10.4: "vượt thì mục còn lại chờ đợt sau chứ không bị bỏ";
time-and-tags.md §5).

### 7.3 Enqueue summary (B17 / AMD-B17)

Task summary được xếp hàng qua `analysis.enqueue_tasks` cho các target **đã được chọn tại thời
điểm build**, không phải cho mọi bài trong kho. `contracts/state/report.yaml` T-RP-01 ghi điều
này thành một `forbidden_vi`: xếp hàng summary cho target KHÔNG được chọn là vi phạm B17. Target được chọn mà chưa có
`analysis[status='valid', task_type='summary']` khớp analysis key:

- vẫn vào `report_item` (mục **không bị ẩn**),
- được ghi `pending_item_ledger` với `reason='missing_summary'`,
- làm `report.quality = 'partial'`.

`report.quality = 'complete'` chỉ khi mọi mục được chọn của kỳ đó đều có summary hợp lệ hoặc đã
được đánh dấu pending tường minh và pending list của kỳ đó rỗng (time-and-tags.md §5.4 O-5.3).

**Oracle O-7.** Kỳ có 60 mục khớp và `max_items_per_period = 50`:
`#report_item` = 50, `#pending_item_ledger[reason='budget_exceeded', state='pending']` = 10, và
ở kỳ sau 10 mục đó là ứng viên bất kể `discovered_at` nằm ngoài cửa sổ mới.

## 8. Mật độ vector và khối "hướng đang nổi" (B14)

### 8.1 Nhãn và ranh giới ngữ nghĩa

Nhãn hiển thị **luôn** là **"ứng viên để đọc sâu"** (REQ-D54, SRC-SPEC §10.3). Bị cấm tuyệt đối:
"phát hiện mới", "hướng nghiên cứu mới", "đột phá", hay bất kỳ câu chữ nào khẳng định tính mới
khoa học. "Mới" trong D54 = mới **với người dùng** (truy vấn) + **đang tụ lại** (mật độ vector);
AI **không** được dùng để đánh giá tính mới khoa học (SRC-SPEC §2.3).

AI chỉ có một việc trong khối này: **diễn đạt lại** object đã tính (task
`direction_phrasing`, PC06). Nếu task đó lỗi hoặc không có provider, khối vẫn hiển thị được với
danh sách thành viên và số liệu — chỉ thiếu câu văn. Khối **không bao giờ** phụ thuộc AI để tồn
tại.

### 8.2 Tham số (tất cả `PROVISIONAL`, cổng REQ-A4)

| Tham số | Giá trị | Đơn vị | Lý do |
| --- | --- | --- | --- |
| `metric` | `cosine` | — | Cùng phép đo với selection (§3); dùng hai phép đo khác nhau trong một báo cáo là không giải thích được |
| `radius` (`r`) | `0.8000` | cosine | Bằng ngưỡng khởi động của §6 để hai phần của báo cáo nói cùng một ngôn ngữ. `PROVISIONAL_BOOTSTRAP`, kèm A4 |
| `min_members` | `3` | target riêng biệt | Hai bài không phải một "hướng"; ba là số nhỏ nhất mà từ "tụ lại" còn có nghĩa ở quy mô một người dùng |
| `comparison_window_k` (`K`) | `4` | kỳ liền trước | REQ-A4 đánh giá trên 3–4 kỳ; K = 4 khớp đúng cửa sổ đánh giá đó |
| `min_prior_windows` | `2` | kỳ | Dưới hai kỳ nền thì "tăng" không có ý nghĩa thống kê nào ở mức này |
| `min_delta` | `2.0000` | target | Mức tăng tuyệt đối tối thiểu; nhỏ hơn thì một bài lẻ cũng thành "hướng" |
| `prior_floor` (`ε`) | `1.0000` | target | Mẫu số sàn khi tính `density_ratio`, để `3 / 0` không thành vô hạn |
| `rounding` | half-up, 4 chữ số thập phân | — | Tái lập được giữa các lần chạy và giữa các máy |

Không tham số nào ở trên đã được kiểm chứng. REQ-A4 là `KC`: "Đọc lại 3–4 kỳ báo cáo, đối chiếu
với đánh giá của người dùng". Trước khi có đánh giá đó, mọi giá trị ở đây chỉ là điểm khởi động
tất định.

### 8.3 Thuật toán (tất định, không AI, không ngẫu nhiên)

Đầu vào: `G` (embedding generation của kỳ), `S_t` = tập **nhãn** của các target được chọn ở kỳ
`t` (sau exclusion, §4), và các kỳ liền trước `t−1 … t−K` đã `published` **cùng** `G`.

```text
BƯỚC 1  Với mỗi target X ∈ selected(t), lấy mọi vector l ∈ labels(X). Mỗi vector mang theo
        target_key của X. (Một target có nhiều nhãn góp nhiều vector.)

BƯỚC 2  Láng giềng cố định bán kính, tính MỘT LẦN trên toàn bộ S_t:
            N(v) = { w ∈ S_t : cosine(v, w) >= r }          [round 4dp]

BƯỚC 3  Gom nhóm tham lam tất định:
            order = sắp xếp seed theo (|N(v)| giảm dần, target_key tăng dần, label_text tăng dần)
            assigned = ∅
            với mỗi seed v theo order:
                nếu v ∈ assigned: bỏ qua
                members = N(v) \ assigned
                nếu members ≠ ∅:  tạo nhóm(members);  assigned := assigned ∪ members

BƯỚC 4  m_t(nhóm) = số target_key RIÊNG BIỆT trong nhóm.
        Target có work.identity_state = 'quarantined' KHÔNG được đếm (identity.md §5.3);
        chúng được liệt kê ở excluded_quarantined_target_keys.

BƯỚC 5  Loại nhóm có m_t < min_members.

BƯỚC 6  Với mỗi nhóm còn lại, centroid c = trung bình cộng các vector thành viên, chuẩn hóa L2.
        c được ghi bất biến vào emerging_direction.

BƯỚC 7  Với mỗi kỳ trước p ∈ {t−1 … t−K} đã published và cùng G:
            m_p = số target_key riêng biệt được chọn ở kỳ p có ít nhất một nhãn l với
                  cosine(l, c) >= r
        density_prior = trung bình cộng của m_p trên các kỳ TỒN TẠI (không đệm 0 cho kỳ
        không tồn tại).

BƯỚC 8  density_now   = m_t
        density_delta = density_now − density_prior                         [round 4dp]
        density_ratio = density_now / max(density_prior, ε)                 [round 4dp]

BƯỚC 9  Nhóm được công bố là một hướng khi:
            (a) m_t >= min_members,  VÀ
            (b) density_delta >= min_delta,  VÀ
            (c) số kỳ trước tồn tại cùng G >= min_prior_windows

BƯỚC 10 Sắp xếp hướng: density_delta giảm dần, rồi m_t giảm dần, rồi target_key nhỏ nhất tăng
        dần. Cắt ở max_emerging_directions.
```

Vì sao **không** dùng k-means hay clustering có khởi tạo ngẫu nhiên: kết quả phải tái lập được
từ cùng dữ liệu (SRC-PLAN §2 "oracle độc lập"). Gom nhóm bán kính cố định + thứ tự seed toàn
phần cho đúng một kết quả cho mỗi đầu vào.

### 8.4 `insufficient_evidence`: bắt buộc, không phải trường hợp lỗi

`emerging_direction.evidence_state` ∈ `sufficient` | `insufficient_evidence` (entities.yaml).
Khi không có nhóm nào qua BƯỚC 9, kỳ đó ghi **một** hàng `emerging_direction` với
`evidence_state = 'insufficient_evidence'`, `member_target_keys = []` và
`insufficient_reason` ∈:

| `insufficient_reason` | Điều kiện |
| --- | --- |
| `below_min_sample` | Không nhóm nào đạt `m_t >= min_members` |
| `cold_start_insufficient_history` | Số kỳ trước tồn tại cùng `G` < `min_prior_windows` |
| `delta_below_threshold` | Có nhóm đủ lớn nhưng `density_delta < min_delta` |
| `generation_reset` | `G` vừa đổi nên không có kỳ trước nào so sánh được (I12) |

**Cold-start.** Kỳ đầu tiên của hệ thống, và kỳ đầu tiên sau khi
`embedding.activate_generation` đổi `G`, luôn cho `insufficient_evidence` — vì không có nền để
so. Đây là hành vi đúng, không phải lỗi: B14 nói "Thiếu dữ liệu → insufficient evidence, không
tự gọi là 'hướng nổi'".

UI và Telegram phải hiển thị trạng thái này **khác** với "không có nội dung phù hợp" và khác với
"đợt thất bại" (SRC-SPEC §8.3, I13).

### 8.5 Cái gì làm mật độ mất hiệu lực

- Đổi `embedding_generation` → mọi kỳ trước thuộc generation khác **không** được dùng làm nền
  (I12). `insufficient_reason = 'generation_reset'`.
- Đổi `selection_version` hoặc bất kỳ tham số nào ở §8.2 → các kỳ trước vẫn dùng được **về mặt
  dữ liệu** nhưng số liệu không so sánh trực tiếp; `emerging_direction.density_metric` ghi lại
  bộ tham số đã dùng, nên một người đọc sau này biết hai kỳ được tính bằng hai bộ tham số.
- Đổi `tag_config_version` **không** làm mất hiệu lực: mật độ tính trên nhãn (lớp 1), không trên
  tag (lớp 2). Đây là hệ quả trực tiếp của SRC-SPEC §8.1.

### 8.6 Object đầu ra

Xem `contracts/schemas/report.schema.json` → `$defs.emerging_direction`. Các trường bắt buộc:
`direction_id`, `evidence_state`, `label` (const `"ứng viên để đọc sâu"`), `member_target_keys`,
`centroid`, `density` (`density_now`, `density_prior`, `density_delta`, `density_ratio`,
`comparison_windows_used`), `parameters`, `embedding_generation_id`,
`excluded_quarantined_target_keys`. `phrasing_analysis_id` là nullable — khối tồn tại được khi
không có AI.

### 8.7 Ví dụ số có thể tính lại

Cấu hình: `dimension = 4`, `normalization = l2`, `r = 0.8000`, `min_members = 3`, `K = 4`,
`min_prior_windows = 2`, `min_delta = 2.0000`, `ε = 1.0000`, làm tròn half-up 4dp.

Sáu target được chọn ở kỳ `t`, mỗi target một nhãn. Vector nằm trong mặt phẳng hai chiều đầu để
kiểm tay được (`v(θ) = (cos θ, sin θ, 0, 0)`, đã làm tròn 4dp).

`work:01JT1` … `work:01JT6` dưới đây là **cách viết tắt cho dễ đọc**; `target_key` đầy đủ (ULID
26 ký tự) nằm ở `acceptance/fixtures/reporting/m-density-worked-example.json` →
`given` → `target_key_map`. Thứ tự byte của khóa viết tắt và khóa đầy đủ giống nhau, nên tie-break
ở BƯỚC 3 cho cùng kết quả. Phần được kiểm lại bằng script (`EV-PC04-02`) là **các con số**.

| target_key | θ | vector |
| --- | --- | --- |
| `work:01JT1` | 0° | `(1.0000, 0.0000, 0, 0)` |
| `work:01JT2` | 20° | `(0.9397, 0.3420, 0, 0)` |
| `work:01JT3` | 30° | `(0.8660, 0.5000, 0, 0)` |
| `work:01JT4` | 35° | `(0.8192, 0.5736, 0, 0)` |
| `work:01JT5` | 90° | `(0.0000, 1.0000, 0, 0)` |
| `work:01JT6` | 120° | `(−0.5000, 0.8660, 0, 0)` |

Cosine từng cặp (làm tròn 4dp):

| | T2 | T3 | T4 | T5 | T6 |
| --- | --- | --- | --- | --- | --- |
| **T1** | 0.9397 | 0.8660 | 0.8192 | 0.0000 | −0.5000 |
| **T2** | — | 0.9848 | 0.9659 | 0.3420 | −0.1737 |
| **T3** | — | — | 0.9962 | 0.5000 | 0.0000 |
| **T4** | — | — | — | 0.5736 | 0.0871 |
| **T5** | — | — | — | — | 0.8660 |

BƯỚC 2 (`r = 0.8000`): `|N(T1)| = |N(T2)| = |N(T3)| = |N(T4)| = 4` (đều là `{T1,T2,T3,T4}`);
`|N(T5)| = |N(T6)| = 2` (`{T5,T6}`).

BƯỚC 3: thứ tự seed = `T1, T2, T3, T4, T5, T6`. Nhóm **A** = `{T1,T2,T3,T4}`; sau đó nhóm
**B** = `{T5,T6}`.

BƯỚC 4–5: `m_t(A) = 4` ≥ 3 → giữ. `m_t(B) = 2` < 3 → **loại**.

BƯỚC 6: trung bình của A = `(0.9062, 0.3539)`; chuẩn L2 = `0.9728`; centroid
`c = (0.9315, 0.3638, 0, 0)` (góc ≈ `21.3333°`).

BƯỚC 7 — ba kỳ trước tồn tại cùng `G` (kỳ `t−4` chưa tồn tại):

| Kỳ | target | cosine với `c` | Trong bán kính? | `m_p` |
| --- | --- | --- | --- | --- |
| `t−1` | `work:01JP1` (25°) | `0.9980` | có | 1 |
| `t−1` | `work:01JP2` (100°) | `0.1966` | không | |
| `t−2` | `work:01JP3` (40°) | `0.9474` | có | 1 |
| `t−3` | `work:01JP4` (150°) | `−0.6248` | không | 0 |

`density_prior = (1 + 1 + 0) / 3 = 0.6667`.

BƯỚC 8: `density_now = 4`; `density_delta = 4 − 0.6667 = 3.3333`;
`density_ratio = 4 / max(0.6667, 1.0000) = 4.0000`.

BƯỚC 9: `m_t = 4 ≥ 3` ✔; `3.3333 ≥ 2.0000` ✔; số kỳ trước tồn tại `= 3 ≥ 2` ✔ →
**một** hướng, `evidence_state = 'sufficient'`, thành viên `{work:01JT1, work:01JT2,
work:01JT3, work:01JT4}`, nhãn "ứng viên để đọc sâu".

**Biến thể đối chứng.** Bỏ `T1…T4` khỏi tập, chỉ còn `T5, T6`: nhóm duy nhất có `m_t = 2 < 3` →
`evidence_state = 'insufficient_evidence'`, `insufficient_reason = 'below_min_sample'`,
`member_target_keys = []`. Câu chữ hiển thị **không** được chứa từ "đang nổi".

Cả hai nhánh là fixture `m-density-worked-example.json`, và các con số trên được tính lại bằng
script trong evidence record `EV-PC04-02`.

### 8.8 Oracle

- **O-8.1.** Với đầu vào §8.7, tập `member_target_keys` bằng đúng
  `["work:01JT1","work:01JT2","work:01JT3","work:01JT4"]` và
  `density = {now: 4, prior: 0.6667, delta: 3.3333, ratio: 4.0000}`.
- **O-8.2.** Với biến thể đối chứng, `#emerging_direction[evidence_state='sufficient']` = 0 và
  `#emerging_direction[evidence_state='insufficient_evidence']` = 1.
- **O-8.3.** Chạy lại thuật toán hai lần trên cùng dữ liệu với thứ tự hàng đảo ngược → cùng
  `member_target_keys` theo cùng thứ tự và cùng số liệu density.
- **O-8.4 (cấm AI).** Trace của một lần build: số lần gọi provider AI cho task
  `direction_phrasing` ≤ số hướng có `evidence_state='sufficient'`, và **bằng 0** cho việc
  chọn thành viên hay tính mật độ.

## 9. Ràng buộc âm tóm tắt

| Cấm | Căn cứ |
| --- | --- |
| Gọi AI để quyết định một bài có khớp tag không | REQ-D22, SRC-SPEC §10.1 |
| Gọi AI để chọn thành viên hoặc tính mật độ | REQ-D53, REQ-D54, SRC-SPEC §10.1 |
| Dùng AI để liên kết mục cùng hướng đã báo cáo | REQ-D30 (ràng buộc âm tường minh) |
| Dùng tương tác trên X làm bằng chứng khoa học | SRC-SPEC §10.3 |
| So sánh vector khác generation/model/dimension | I12, `EMBEDDING_GENERATION_MISMATCH` |
| Sửa report đã publish khi selection stale | I05, `TAG_VERSION_STALE` |
| Bỏ mục vượt hạn mức | SRC-SPEC §10.4, I06 |
| Gọi khối hướng nổi là "phát hiện mới" | REQ-D54, B14 |
| Đặt `evidence_state='sufficient'` khi dưới `min_members` | B14 |
| Coi hai alias đang `identity_conflict` là hai hướng chắc chắn | B15, identity.md §5.3 |

## 10. Những gì file này KHÔNG chứng minh

- Không chứng minh `0.8000` tách được bài khớp khỏi bài không khớp — đó là REQ-A2, `KC`, cần
  50–100 bài gán nhãn tay.
- Không chứng minh thuật toán §8 phát hiện được hướng thật thay vì nhiễu — đó là REQ-A4, `KC`,
  cần 3–4 kỳ dữ liệu thật và đánh giá của Owner.
- Không chứng minh model embedding đa ngôn ngữ đủ tốt trên thuật ngữ khoa học — REQ-A3, `KC`.
- Không chứng minh code chạy đúng: chưa có code (cấp E0).
