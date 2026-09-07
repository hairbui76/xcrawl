---
contract_id: CT-data-identity
version: 0.1.0
status: accepted
ratification_ref: OD-20260907-01
owner_role: data contract owner
source_refs:
  - "SRC-SPEC §3.5 D17, D26, D29"
  - "SRC-SPEC §3.2 D31, D33"
  - "SRC-SPEC §7.1, §7.2, §7.3"
  - "SRC-SPEC §9.3 (chống trùng)"
  - "SRC-SPEC §12 AC-07, AC-09"
  - "SRC-PLAN §3 B06, B15"
  - "SRC-PLAN §9.1"
  - "SRC-PLAN §10 IDENTITY_CONFLICT, SOURCE_METADATA_UNAVAILABLE"
  - "SRC-PLAN §11 PC02"
requirement_refs: [REQ-D17, REQ-D26, REQ-D29, REQ-D31, REQ-D33, REQ-AC07, REQ-AC09, REQ-S9.3-01]
decision_refs: [B06, B15, B07, AMD-B05]
invariant_refs: [I03, I07, I15, I17]
producers: [MOD-identity-service, MOD-ingest-service]
consumers: [MOD-report-service, MOD-web-ui, MOD-backend-api, MOD-research-connector, MOD-analysis-service, MOD-saved-service]
dependencies:
  - contracts/data/entities.yaml
  - contracts/schemas/target.schema.json
  - acceptance/fixtures/identity/
scope: >-
  Hợp đồng canonical identity: chuẩn hóa DOI và arXiv ID, phân biệt định danh canonical với
  alias, quy tắc target chỉ-có-post, lưu giữ bằng chứng/provenance, ngữ nghĩa quarantine
  `identity_conflict`, thuật toán merge (chọn winner, cái gì được chuyển, cái gì không),
  audit trail, và những gì cố ý KHÔNG làm ở MVP.
verification: "E0: fixture identity (acceptance/fixtures/identity/) + validate target objects theo target.schema.json. E1–E4: NOT_RUN."
claim_ceiling: CONTRACT_READY
---

# Canonical identity, alias và merge

## 1. Vì sao cần file này

SRC-SPEC §1.4 đặt chỉ tiêu vận hành "0 trường hợp trùng" và REQ-D17 gộp mục báo cáo theo
DOI/arXiv ID. SRC-PLAN §3 B06 chỉ ra rằng hai cột UNIQUE không đủ: hai hàng `work` có thể
đã tồn tại rồi hệ thống mới biết chúng là một công trình. B15 bổ sung rằng metadata có thể
thiếu hoặc mâu thuẫn, nên "0 trùng" chỉ có nghĩa **trong phạm vi canonical identity đã biết**.

Vì vậy identity ở đây là ba lớp tách rời:

| Lớp | Là gì | Cơ chế |
| --- | --- | --- |
| Chuẩn hóa | Đưa một chuỗi định danh về dạng so sánh được | Hàm thuần túy, tất định, §2 |
| Tra cứu | Định danh đã chuẩn hóa → work nào | Bảng `identity_alias`, UNIQUE, §3 |
| Hợp nhất | Hai work hóa ra là một | Transaction có bằng chứng và audit, §6 |

Không lớp nào được thay thế lớp khác. Cụ thể: UNIQUE (lớp 2) không giải được bài toán của
lớp 3, và không có thuật toán đoán nào được phép thay thế bằng chứng ở lớp 3.

## 2. Chuẩn hóa định danh

Chuẩn hóa là **hàm thuần túy, tất định, không gọi mạng**. Cùng đầu vào luôn cho cùng đầu ra.
Giá trị nguyên bản luôn được giữ ở `identity_alias.id_value_raw` để có thể tính lại nếu quy
tắc đổi (§8).

### 2.1 DOI

Đầu vào có thể là: `10.1000/xyz123`, `doi:10.1000/xyz123`, `DOI: 10.1000/XYZ123`,
`https://doi.org/10.1000/xyz123`, `http://dx.doi.org/10.1000/xyz123`, kèm khoảng trắng hoặc
dấu câu cuối câu do post cắt dán.

Thuật toán `normalize_doi(raw) -> string | REJECT`:

1. Trim khoảng trắng hai đầu; chuẩn hóa Unicode về NFC.
2. Bỏ tiền tố không phân biệt hoa thường, theo đúng thứ tự và chỉ một lần mỗi loại:
   `https://doi.org/`, `http://doi.org/`, `https://dx.doi.org/`, `http://dx.doi.org/`,
   `doi.org/`, `dx.doi.org/`, `doi:`, `DOI:` (kèm khoảng trắng sau dấu hai chấm nếu có).
3. Percent-decode **đúng một lần**. Nếu sau khi decode chuỗi vẫn còn `%` theo sau hai ký tự
   hex, KHÔNG decode tiếp — DOI hợp lệ có thể chứa `%` thật.
4. Bỏ các ký tự câu ở cuối chuỗi thuộc tập `. , ; : ) ] } > " '` — lặp cho tới khi ký tự cuối
   không thuộc tập đó. Lý do: post thường viết `… doi.org/10.1000/xyz.` và dấu chấm cuối câu
   không thuộc DOI. **Rủi ro đã biết:** một số DOI kết thúc hợp lệ bằng dấu chấm; trường hợp
   đó chỉ phát hiện được khi tra nguồn chuẩn, và khi tra ra khác thì đây là
   `cross_scheme_disagreement` chứ không phải merge im lặng.
5. Chuyển toàn bộ về **chữ thường**. Căn cứ: cú pháp DOI không phân biệt hoa thường ở phần
   suffix theo thực tiễn của registry; hai biến thể hoa/thường là **một** DOI.
6. Kiểm dạng: phải khớp `^10\.[0-9]{4,9}/[\x21-\x7e]+$`. Không khớp → `REJECT`.

`REJECT` nghĩa là: KHÔNG tạo alias, KHÔNG tạo work, ghi lý do vào `post.identity_resolution`
tiến trình và để post đi tiếp theo nhánh chỉ-có-post nếu không còn định danh nào khác. Tuyệt
đối không "sửa" DOI cho hợp lệ.

### 2.2 arXiv ID

Hai kiểu tồn tại song song:

- **Kiểu mới** (từ 04/2007): `YYMM.NNNNN` với 4 hoặc 5 chữ số sau dấu chấm, tùy chọn hậu tố
  phiên bản `vN`. Ví dụ `2501.01234`, `2501.01234v2`, `0704.0001`.
- **Kiểu cũ** (trước 04/2007): `archive[.subject-class]/YYMMNNN`, ví dụ `math.GT/0309136`,
  `hep-th/9901001`, cũng có thể kèm `vN`.

Thuật toán `normalize_arxiv(raw) -> {base: string, version: string | null} | REJECT`:

1. Trim, NFC.
2. Bỏ tiền tố không phân biệt hoa thường: `https://arxiv.org/abs/`, `http://arxiv.org/abs/`,
   `https://arxiv.org/pdf/`, `http://arxiv.org/pdf/`, `arxiv.org/abs/`, `arxiv.org/pdf/`,
   `arXiv:`, `arxiv:`.
3. Bỏ hậu tố `.pdf` nếu có (link PDF).
4. Bỏ query string và fragment (`?...`, `#...`).
5. Bỏ ký tự câu ở cuối như §2.1 bước 4.
6. Tách hậu tố phiên bản: nếu chuỗi khớp `(?i)^(.*?)v([1-9][0-9]{0,2})$` thì `version` =
   `"v" + <số>`, phần còn lại là ứng viên base; ngược lại `version = null`.
7. Chuẩn hóa base theo kiểu:
   - Kiểu mới: khớp `^[0-9]{4}\.[0-9]{4,5}$` → giữ nguyên (chữ số, không có hoa thường).
   - Kiểu cũ: khớp `^[a-zA-Z-]+(\.[A-Za-z]{2})?/[0-9]{7}$` → **archive** về chữ thường,
     **subject-class** (hai chữ cái sau dấu chấm) về chữ HOA. Ví dụ `Math.gt/0309136` →
     `math.GT/0309136`. Căn cứ: đây là dạng arXiv công bố chính thức của kiểu cũ; chuẩn hóa
     tất định là điều kiện để `identity_alias` là một hàm.
   - Không khớp cả hai → `REJECT`.

**`work.canonical_arxiv_id` LUÔN là base, không kèm `vN`.** Phiên bản sống ở `work_version`
(REQ-D26: paper có phiên bản mới thì phân tích lại, **giữ bản cũ**). Hệ quả trực tiếp:
`arXiv:2501.01234v1` và `arXiv:2501.01234v2` là **một** work với **hai** `work_version`, không
phải hai work. Đây là fixture (g).

### 2.3 Các scheme khác

| Scheme | Canonical? | Chuẩn hóa | Ghi chú |
| --- | --- | --- | --- |
| `doi` | **Có** | §2.1 | Định danh bền nhất; thắng khi chọn winner (entities.yaml `winner_selection`) |
| `arxiv` | **Có** | §2.2, base | Preprint; một work có thể có cả DOI và arXiv |
| `openalex` | Không — alias | `^W[0-9]+$`, chữ W hoa | ID của một dịch vụ, có thể đổi; dùng để **bắc cầu** DOI↔arXiv |
| `pmid` | Không — alias | `^[0-9]{1,9}$` | |
| `landing_url` | Không — alias | Chuẩn hóa URL: hạ scheme+host về chữ thường, bỏ `www.`, bỏ fragment, bỏ tham số tracking (`utm_*`, `ref`, `s`), giữ path nguyên trạng | Bằng chứng yếu nhất |

"Canonical" nghĩa là: giá trị được phép ghi vào cột `work.canonical_doi` /
`work.canonical_arxiv_id` và do đó được ép bởi UNIQUE. "Alias" nghĩa là: chỉ tồn tại trong
`identity_alias`, dùng để tra cứu và bắc cầu, **không** tự mình định nghĩa work.

Một alias `openalex` trỏ tới work A và cùng lúc bằng chứng nói nó ứng với DOI của work B
chính là bằng chứng liên kết hợp lệ cho merge (§6) — đây là cách fixture (a) hoạt động.

## 3. Tra cứu: identity_alias là một hàm

`UNIQUE(owner_id, id_scheme, id_value_normalized)` biến bảng thành hàm:
`(scheme, value) → tối đa một work` (I03).

Thứ tự tra cứu khi ingest một item có tập định danh `S`:

1. Chuẩn hóa mọi phần tử của `S`; loại các phần tử `REJECT`.
2. Tra `identity_alias` cho từng phần tử → tập work `W`.
3. Ba trường hợp:
   - `|W| = 0`: tạo work mới, ghi mọi định danh của `S` thành alias, ghi giá trị canonical
     tương ứng vào cột canonical.
   - `|W| = 1`: dùng work đó; ghi các định danh trong `S` chưa có thành alias mới.
   - `|W| ≥ 2`: **không** tự nối. Đây là ứng viên merge: chuyển sang §6 (đủ điều kiện) hoặc
     §5 (mâu thuẫn).
4. `S = ∅` sau bước 1: post trở thành target chỉ-có-post (§4).

Bước 3 không bao giờ được rút gọn thành "lấy work đầu tiên tìm thấy".

## 4. Target chỉ-có-post

REQ-D33: post chỉ có ảnh chụp paper, không có link → **không đoán ID**, thành mục "chỉ có
post". Điều đó có nghĩa cụ thể:

- `post.identity_resolution = 'resolved_post_only'`; không có hàng `work` nào được tạo.
- Target là `{"kind": "post", "post_id": …}` — nhánh `post` của tagged union
  (contracts/schemas/target.schema.json).
- Post-only target được Save được, được gắn nhãn và summary được (`analysis.target_kind =
  'post'`), với `evidence_level = 'post_only'` (REQ-D21, REQ-AC11).
- OCR ảnh để đoán arXiv ID là **ngoài phạm vi** MVP. Nếu sau này bật, nó phải là một
  `evidence_source` mới với `confidence` riêng, không được ghi thẳng vào cột canonical.

### Post-only promotion

Nếu về sau post đó được liên kết tới một work (owner nhập tay, hoặc một post khác cùng thread
dẫn link):

- Tạo `post_work` như bình thường; `post.identity_resolution` → `resolved_linked`.
- Các tham chiếu tới `post:<id>` **đã tồn tại** (Saved, analysis, report_item đã publish)
  **không** bị viết lại tự động. Lý do: `saved_snapshot` là bằng chứng lịch sử (I17) và
  report đã publish là bất biến (I05).
- Nếu owner muốn Saved trỏ sang work, đó là một hành động tường minh tạo Saved mới cho
  `work:<id>` qua `save.create`; Saved cũ ở lại. Việc này được ghi như một identity merge có
  `performed_by = 'owner_manual'` để có audit trail.

## 5. `identity_conflict`: quarantine, không đoán

Conflict được tạo khi bằng chứng mâu thuẫn. Bốn loại (`identity_conflict.conflict_type`):

| conflict_type | Khi nào | Ví dụ |
| --- | --- | --- |
| `cross_scheme_disagreement` | Bằng chứng nói DOI D ứng arXiv A, nhưng D đã thuộc work W1 và A đã thuộc W2, và W1, W2 có canonical value xung đột | OpenAlex trả DOI khác với DOI mà arXiv khai |
| `alias_points_to_two_works` | Tập work tra cứu được có từ hai phần tử trở lên (§3 bước 3) mà không có bằng chứng đủ mạnh để chọn | Hai work cùng có `landing_url` chuẩn hóa giống nhau |
| `canonical_value_mismatch` | Hai ứng viên merge đều có `canonical_doi` nhưng khác nhau (hoặc đều có `canonical_arxiv_id` khác nhau) | Metadata sai ở một nguồn |
| `merge_cycle_detected` | Chuỗi `merged_into_work_id` sẽ tạo chu trình | Lỗi dữ liệu/lỗi triển khai |

Ngữ nghĩa quarantine:

1. Hàng `identity_conflict` được ghi với **toàn bộ** định danh liên quan (`involved_identifiers`)
   ở cả dạng raw và normalized, kèm `evidence_source` và `evidence_ref`. Không nguồn nào bị
   mất (B15).
2. Mọi work trong `involved_work_ids` chuyển `identity_state = 'quarantined'`.
3. Trong khi `state = 'open'`:
   - Các work đó **không** được merge tự động.
   - Chúng **không** được tính là hai hướng nghiên cứu chắc chắn trong khối "hướng đang nổi"
     và không được trình bày là hai phát hiện độc lập (SRC-PLAN §10 IDENTITY_CONFLICT). Cách
     hiển thị cụ thể do PC04 khóa; cờ `quarantined` là giao diện PC02 cung cấp.
   - Dữ liệu vẫn đọc được, Saved vẫn còn, analysis đã có vẫn hợp lệ. Quarantine chặn **suy
     luận identity**, không chặn dữ liệu.
4. Thoát `open` chỉ bằng hành động của owner (`identity.resolve_conflict`), với ba kết cục:
   `resolved_merged` (kèm `resolution_merge_id`), `resolved_distinct` (hai công trình khác
   nhau thật), `resolved_data_error` (một nguồn sai; alias sai bị đánh dấu, không xóa).
5. Không có timeout tự giải. Conflict không tự hết hạn thành merge.

## 6. Thuật toán merge

Điều kiện tiên quyết, quy tắc chọn winner, danh sách cột được chuyển (merge move-set) và
timeline lỗi nằm ở `contracts/data/entities.yaml` → `transactions[TXN-identity-merge]`, để
oracle và schema ở cùng một nguồn chuẩn. Phần dưới đây giải thích ý nghĩa nghiệp vụ.

### 6.1 Bằng chứng bắt buộc

Merge chỉ hợp lệ khi có **một định danh đã chuẩn hóa xuất hiện ở cả hai work**, hoặc một
nguồn có thẩm quyền (arXiv/OpenAlex) khai báo tường minh ánh xạ giữa hai định danh canonical.
`identity_merge_audit.linking_evidence` là NOT NULL, và `performed_by` chỉ nhận
`system_automatic_on_evidence` hoặc `owner_manual`. **AI không bao giờ là nguồn bằng chứng
identity** (B15, SRC-SPEC §11.4: nội dung ngoài là dữ liệu, không phải lệnh).

### 6.2 Chọn winner

Thứ tự tất định: `owner_choice` → `only_candidate_with_canonical_doi` →
`earliest_first_discovered_at` (tie-break `ingest_sequence`, rồi `id` theo thứ tự byte).
Quy tắc phải toàn phần và tất định vì oracle của fixture (a) so sánh chính xác work nào sống
sót; một quy tắc phụ thuộc thứ tự truy vấn sẽ làm fixture không tái lập được.

### 6.3 Cái gì được chuyển

`identity_alias`, `post_work`, `work_version`, `work_label`, `analysis`, `saved_item` (con
trỏ), và các cột canonical còn thiếu của winner. Chi tiết va chạm khóa cho từng bảng ở
entities.yaml.

### 6.4 Cái gì KHÔNG được chuyển và KHÔNG được đổi

- `saved_snapshot` — mọi cột, kể cả `target_key_at_save`. Đây là I17.
- `report_item` của report đã `published` — kỳ cũ giữ nguyên nội dung đã công bố (I05).
- `ingest_receipt`, `analysis_attempt`, `identity_merge_audit` — bất biến.
- `post.discovered_at`, `post.ingest_sequence`.
- Hàng `work` thua **không bị xóa**: nó giữ `canonical_doi`/`canonical_arxiv_id` cũ làm bằng
  chứng, được loại khỏi UNIQUE nhờ partial index `WHERE identity_state <> 'merged'`.

### 6.5 `first_announced`: giao diện, không phải quyết định

Sau merge, câu hỏi "work thắng có được coi là đã-báo-cáo từ ngày mà work thua được báo cáo
không" quyết định kỳ sau hiển thị `new_discovery` hay `prior_reference` (REQ-D29, REQ-AC09,
I07). Đó là **quyết định của PC04**, không phải của PC02.

PC02 cung cấp giao diện sau, và cam kết không đổi tên:

| Cái PC02 bảo đảm | Dùng để làm gì |
| --- | --- |
| `identity_merge_audit` được ghi TRONG cùng transaction merge | PC04 móc logic first-announced vào cùng commit point |
| `identity_merge_audit.moved_counts` khóa `first_announced` là ô đã dành sẵn | PC04 ghi số hàng nó xử lý; là oracle đếm được |
| `winner_work_id`, `loser_work_id`, `merged_at` | Đầu vào của bất kỳ policy nào PC04 chọn |
| `report_item` đã publish không bị PC02 đụng tới | PC04 phải diễn đạt lịch sử bằng ledger mới, không sửa kỳ cũ |

Ghi nhận là **CR-PC02-06** gửi PC04: khóa policy first-announced sau merge và ghi vào
`contracts/reporting/selection.md`. Cho tới khi PC04 khóa, triển khai không được đoán: merge
vẫn chạy, `identity_merge_audit.moved_counts` khóa `first_announced` ghi `null`, và mục đó được đánh dấu là chưa khóa.

## 7. Bằng chứng và provenance

Mọi hàng `identity_alias` mang:

- `id_value_raw` — nguyên bản quan sát được, giữ vĩnh viễn.
- `evidence_source` ∈ {`post_link`, `arxiv_api`, `openalex_api`, `manual_owner`}. **Không có
  giá trị `ai_inference`.**
- `evidence_ref` — `{post_id?, api_endpoint?, retrieved_at, response_hash?}`; bắt buộc.
- `confidence` ∈ {`asserted_by_source`, `confirmed_by_two_sources`, `owner_confirmed`}. Đây là
  ba mức rời rạc, **không phải điểm số xác suất**: MVP không đoán, nên không có thang liên tục.

Retention: không xóa alias, không xóa `identity_merge_audit`, không xóa `identity_conflict`
kể cả sau khi giải (REQ-D58 giữ vô thời hạn). Merge chỉ ghi lại `work_id` và đặt
`superseded_by_merge_id`.

Khi nguồn metadata lỗi (`SOURCE_METADATA_UNAVAILABLE`): `work.metadata_state = 'unavailable'`,
KHÔNG đoán DOI, KHÔNG xóa abstract đã có từ lần lấy trước (SRC-PLAN §10). Post vẫn tồn tại và
mục có thể là chỉ-có-post cho tới khi metadata về.

## 8. Đổi quy tắc chuẩn hóa

Đổi thuật toán §2 là **đổi khóa của dữ liệu đã ghi**, không phải sửa prose. Quy trình bắt buộc:

1. Amendment + bump `version` của file này và của `contracts/data/entities.yaml`.
2. Migration tính lại `id_value_normalized` từ `id_value_raw` cho toàn bộ `identity_alias`.
3. Nếu việc tính lại làm hai alias trùng nhau mà chúng đang trỏ hai work khác nhau →
   **không** merge tự động: tạo `identity_conflict` `alias_points_to_two_works` cho từng cặp.
4. Bằng chứng liên quan tới report/Saved/cache chuyển `STALE` theo SRC-PLAN §16.

## 9. Non-goals (cố ý không làm ở MVP)

| Không làm | Trạng thái | Lý do |
| --- | --- | --- |
| Gộp theo tiêu đề gần giống (fuzzy title match) | `KC` | Không có oracle khách quan ở quy mô một người dùng; sai một lần là mất niềm tin vào chỉ tiêu "0 trùng". Cần dữ liệu có nhãn để đánh giá (như REQ-A2 làm với ngưỡng tag). |
| Gộp theo trùng tác giả + năm | `KC` | Cùng lý do; tỷ lệ dương tính giả cao ở lĩnh vực có nhiều bản preprint. |
| OCR ảnh chụp paper để đoán ID | `KC` | REQ-D33 nói rõ: không đoán ID. |
| Undo một merge đã commit | `KC` | Cần lưu trạng thái trước merge của mọi bảng bị đụng; ở MVP thay bằng: merge chỉ chạy khi có bằng chứng, và mọi trường hợp nghi ngờ đi vào `identity_conflict` thay vì merge. |
| Dùng AI để quyết định hai bản ghi có phải một công trình | Bị cấm | B15 + SRC-SPEC §11.4. AI không có `evidence_source` hợp lệ. |
| Nhiều owner / phân tách identity theo tenant | Ngoài phạm vi | REQ-D01. `owner_id` có mặt nhưng không có tính năng nào dùng nó để phân tách. |

## 10. Bảng đối chiếu fixture

| Fixture | Kiểm tra điều gì | Invariant |
| --- | --- | --- |
| `a-merge-doi-arxiv.json` | Hai work rời rạc được nối bởi bằng chứng DOI↔arXiv; winner tất định; move-set đúng | I03, I17 |
| `b-post-only-missing-ids.json` | Không định danh → target `post`, không tạo work, không đoán | I03 |
| `c-identity-conflict.json` | DOI mâu thuẫn → quarantine, không merge, nguồn giữ nguyên | I03 |
| `d-concurrent-save-app-telegram.json` | Save đồng thời hai kênh → một Saved active | I08 |
| `e-source-deleted-snapshot-intact.json` | Post bị xóa trên X → snapshot không đổi | I08, I17 |
| `f-ingest-replay-idempotent.json` | Replay cùng idempotency key → cùng receipt, số đếm không đổi | I02 |
| `g-arxiv-version-v1-v2.json` | v1→v2 là một work hai `work_version`, generation mới, bản cũ giữ nguyên | I03, I04 |
| `h-five-posts-thread-one-target.json` | 5 post + thread tác giả cùng arXiv ID → một target (REQ-AC07) | I03 |
