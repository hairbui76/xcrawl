---
contract_id: CT-ops-collector-probe
version: 0.3.0
status: draft
owner_role: connector contract owner
source_refs:
  - SRC-PLAN §3 B05
  - SRC-PLAN §3 B12
  - SRC-PLAN §6
  - SRC-PLAN §11 PC05
  - SRC-PLAN §12 SP1
  - SRC-SPEC §2.3
  - SRC-SPEC §3.2
  - SRC-SPEC §11.2
  - SRC-SPEC §13 M0
  - SRC-SPEC §13.2
requirement_refs:
  - REQ-A1
  - REQ-A6
  - REQ-A7
  - REQ-D09
  - REQ-D31
  - REQ-D32
  - REQ-D33
  - REQ-D34
  - REQ-OQ05
  - REQ-S13-01
  - REQ-S13.2-01
  - REQ-S13.2-04
  - REQ-AC01
  - REQ-AC03
  - REQ-AC04
decision_refs: [B05, B12, AMD-B05, AMD-B12, ADR-0001, CR-PC05-01, CR-PC10-02, "R-01 (A1-R1)", "FIX3 rulings (2026-09-06T19:05Z)"]
invariant_refs: [I02, I10, I11]
producers: [MOD-x-collector]
consumers: [MOD-ingest-service, MOD-job-service, MOD-research-connector]
dependencies:
  - contracts/ports.yaml
  - contracts/modules.yaml
  - contracts/http/openapi.yaml
  - contracts/schemas/worker-assignment.schema.json
  - contracts/schemas/ingest-receipt.schema.json
  - contracts/state/run.yaml
  - contracts/retry-policy.yaml
  - contracts/errors.yaml
scope: >-
  Giao thức probe khả thi SP1/M0 cho nguồn X, cộng bảng giới hạn nguồn và quy tắc connector nghiên cứu.
  File này KHÔNG phải một báo cáo kết quả: probe CHƯA CHẠY. Nó cũng KHÔNG định nghĩa wire (contracts/http/openapi.yaml),
  KHÔNG định nghĩa transition (contracts/state/run.yaml) và KHÔNG định nghĩa lifecycle secret (PC08).
verification: >-
  EV-PC05-04 (SELF_VALIDATION): file có đủ mục bắt buộc của PKT-PC05 và mọi ngưỡng có số + đơn vị + lý do.
  Bằng chứng thực tế của probe: NOT_RUN.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Giao thức probe khả thi cho collector X (SP1 / M0)

## 0. Trạng thái bằng chứng — đọc trước

> **Probe này CHƯA CHẠY.** Không có đợt chạy thật nào tồn tại tại thời điểm viết file này.
> Trạng thái bằng chứng của mọi con số trong tài liệu: **`NOT_RUN`**.
>
> SRC-SPEC §13 M0 nói thẳng: *"Không coi collector là đã hoạt động trước khi có kết quả thật."*
> SRC-PLAN §11 PC05 xếp "5–10 đợt thực tế" vào mục **Bằng chứng chưa có**.
> Vì vậy tài liệu này là một **giao thức**, không phải một kết luận. Bất kỳ ai đọc nó và tuyên bố
> "collector khả thi" là đang tuyên bố vượt bằng chứng.

Cổng liên quan: **SP1** (SRC-PLAN §12). Điều kiện của SP1: *"Profile/credential hợp lệ, protocol/stop/go-no-go
được chấp nhận; không bypass"*. Nghĩa là: **Owner phải chấp nhận tài liệu này TRƯỚC khi bất kỳ đợt nào chạy**
(§6 bên dưới). Chưa có chấp nhận thì chưa được chạy, kể cả "chạy thử một đợt cho biết".

Nếu probe thất bại: báo quyết định **blocked** cho nguồn X. **Không** tự chuyển sang X API trả phí
(SRC-PLAN §12; SRC-SPEC §2.3 xếp X API trả phí ra ngoài phạm vi).

---

## 1. Điều kiện tiên quyết

| # | Điều kiện | Căn cứ | Kiểm thế nào |
| --- | --- | --- | --- |
| P1 | Chrome **thật** trên máy cá nhân, dùng **profile riêng của dự án**, không phải profile mặc định | REQ-D09 (ĐX) | Đường dẫn profile trỏ tới thư mục riêng; profile mặc định của người dùng không bị chạm |
| P2 | Phiên X đã đăng nhập trong profile đó, `x_session_state = ok` | SRC-SPEC §13 M0 | `worker.register_capabilities` khai `chrome_profile_ready: true` và `x_session_state: ok` |
| P3 | Owner đã xác nhận D09 | SRC-SPEC §13.1 câu hỏi 1 — **chặn M0** | Ghi nhận bằng văn bản của Owner; xem §6 |
| P4 | Cổng debug của Chrome chỉ bind **loopback** | SRC-SPEC §11.2 | Kiểm bằng `ss`/`netstat`: không lắng nghe trên 0.0.0.0, không qua reverse proxy |
| P5 | Không có cơ chế né tránh nào được cài | SRC-SPEC §2.3, REQ-S13.2-04 | Xem §2 |
| P6 | M0 **không** cần DB và **không** cần AI | SRC-SPEC §13 M0 | Probe ghi ra file; không gọi `ingest.submit_batch`, không gọi provider |

**P6 quan trọng và dễ bị bỏ qua.** M0 là *"Chỉ collector: … Ghi ra file, chưa có DB, chưa có AI"*. Probe chạy
ở chế độ **dry-run**: nó thu thập và đếm, rồi ghi ra file JSONL (§5). Nó **không** đẩy dữ liệu vào server.
Hệ quả: probe **không** kiểm chứng đường ingest — đường đó được kiểm offline bằng fixture
(`acceptance/fixtures/collection/`), không cần X live.

---

## 2. Ranh giới đạo đức và kỹ thuật — không thương lượng

Những điều dưới đây **không phải** tham số cấu hình. Chúng là ràng buộc; vi phạm là hỏng probe, không phải
"tối ưu probe".

- **Không né CAPTCHA** dưới bất kỳ hình thức nào: không giải tự động, không dịch vụ giải hộ, không giả lập
  thao tác xác minh (SRC-SPEC §2.3).
- **Không giả fingerprint**, không đổi user-agent để trông như trình duyệt khác (SRC-SPEC §2.3).
- **Không luân chuyển account hoặc proxy** để vượt chặn (SRC-SPEC §2.3, REQ-S9.3-02).
- **Bị chặn thì DỪNG và BÁO** (REQ-S13.2-04). Không thử lại tự động, không "chờ rồi thử account khác".
- **Không dùng X API trả phí** như đường vòng khi probe thất bại (SRC-SPEC §2.3).

Lý do những điều này nằm ở đây chứ không chỉ ở đặc tả: một probe đo "lấy được bao nhiêu bài" tạo áp lực
tự nhiên lên chính những ranh giới này. Con số đẹp đạt được bằng cách vượt ranh giới là **bằng chứng giả**.

REQ-A7 (KC) nói rõ giới hạn của cái probe này đo được: *"X có thể hạn chế tài khoản dù người dùng tự giải
CAPTCHA; không kiểm chứng được trước nên phải thiết kế điều kiện dừng rõ ràng."* Nghĩa là: kể cả một probe
thành công cũng **không** chứng minh nguồn X ổn định lâu dài.

---

## 3. Lịch chạy và ngân sách

### 3.1 Số đợt

| Tham số | Giá trị | Đơn vị | Trạng thái | Lý do |
| --- | --- | --- | --- | --- |
| `probe_run_count_min` | 5 | đợt | XN_derived | SRC-SPEC §13 M0 và SRC-PLAN §11 PC05 đều nói "5–10 đợt". Dưới 5 thì không tách được một lần xui khỏi một xu hướng. |
| `probe_run_count_max` | 10 | đợt | XN_derived | Cùng nguồn. Trần tồn tại để probe không biến thành "dùng thật mà chưa có hợp đồng". |
| `probe_span_days_min` | 3 | ngày | PROVISIONAL (PC05) | Các đợt phải trải qua ít nhất 3 ngày khác nhau. Chạy 10 đợt trong một buổi đo hành vi rate-limit ngắn hạn, không đo được điều REQ-A1 hỏi ("thu thập được đều đặn"). |
| `probe_runs_per_day_max` | 4 | đợt/ngày | PROVISIONAL (PC05) | Gấp đôi nhịp vận hành dự kiến (2 đợt/ngày theo `schedule_slots_default` 08:00 và 20:00). Cao hơn nữa là tự tạo tín hiệu bất thường cho X. |
| `probe_min_gap_minutes` | 60 | phút | PROVISIONAL (PC05) | Khoảng cách tối thiểu giữa hai đợt liên tiếp. Chạy sát nhau làm nhiễu phép đo challenge rate. |

### 3.2 Ngân sách mỗi đợt

| Tham số | Giá trị | Đơn vị | Trạng thái | Lý do |
| --- | --- | --- | --- | --- |
| `probe_max_posts_per_run` | 200 | bài | PROVISIONAL | Bằng `per_run_post_limit` của `contracts/retry-policy.yaml` (baseline §5 OQ defaults). Probe phải đo **đúng ngân sách vận hành dự kiến**, không phải một ngân sách riêng, nếu không kết quả không suy ra được. REQ-OQ05: Owner chốt số thật **sau** M0. |
| `probe_max_duration_s` | 1800 | giây | PROVISIONAL | Bằng `per_run_duration_limit`. Điều kiện dừng là OR: chạm ngưỡng nào trước thì dừng theo ngưỡng đó. |
| `probe_request_min_interval_ms` | 2000 | mili giây | PROVISIONAL (PC05) | Nhịp tối thiểu giữa hai thao tác điều hướng trên X. Không có tài liệu công khai nào về hạn mức của giao diện web X mà tôi đã đọc, nên đây là một **sàn thận trọng tự đặt**, không phải một hạn mức đã biết. Nó tồn tại để probe không chạy không giới hạn (SRC-PLAN §11 PC05). |

---

## 4. Điều kiện dừng

Probe dừng **ngay** khi gặp bất kỳ điều nào sau đây. Không có điều kiện nào cho phép "thử lại rồi tiếp".

| ID | Điều kiện | Ghi lại gì | Ánh xạ sang vận hành |
| --- | --- | --- | --- |
| ST-1 | Gặp CAPTCHA / thử thách xác minh | `challenge_count += 1`, thời điểm, số bài đã thấy tới lúc đó | `run.status = needs_user`, `stop_reason = captcha` (`contracts/state/run.yaml` T-RUN-09); đúng **một** alert intent mỗi run |
| ST-2 | Phiên hết hạn / bị đăng xuất | `session_expired_count += 1` | `stop_reason = session_expired`, cũng vào `needs_user` |
| ST-3 | Bị chặn truy cập (403, trang chặn, giới hạn tài khoản) | `blocked_count += 1`, mô tả quan sát được | `run.status = blocked`, `stop_reason = source_blocked` (T-RUN-16). **Không luân chuyển gì.** |
| ST-4 | Dấu hiệu rate limit (429, trang yêu cầu chậm lại) | `rate_limited_count += 1`, `rate_limited_at` | `stop_reason = rate_limited`, mã `RATE_LIMITED`. Đóng collection segment, **run ĐI TIẾP** sang `enriching`/`reporting` với `outcome = partial` (`contracts/state/run.yaml` T-RUN-25). **KHÔNG** `blocked`, **không** retry trong đợt; đợt theo lịch kế tiếp chạy bình thường |
| ST-5 | Chạm `probe_max_posts_per_run` | `limit_kind = posts` | `stop_reason = limit_reached`, **không phải lỗi** (AMD-B02) |
| ST-6 | Chạm `probe_max_duration_s` | `limit_kind = duration` | `stop_reason = limit_reached` |
| ST-7 | Bố cục feed đổi tới mức không bóc được trường bắt buộc | `parser_degraded_count += 1`, tên trường nào thiếu | `run.status = blocked`, `stop_reason = source_layout_changed`, mã `SOURCE_LAYOUT_CHANGED` (`contracts/state/run.yaml` T-RUN-24). Tạo **một** alert intent |
| ST-8 | Owner bấm dừng | — | — |

**ST-4 đổi hành vi ở FIX3 (ruling CR-PC10-02).** Bản trước của tài liệu này viết *"kéo dài quá ngân sách ⇒
`blocked`"*. Điều đó nay **sai**: `blocked` đòi Owner gỡ tay bằng `run.resume` với `unblock_reason`, trong khi
rate limit là tình huống **tự hết** — đợt sau chạy được mà không cần ai làm gì. Hành vi đúng là đóng segment,
giữ checkpoint đã ACK, đi tiếp với phần dữ liệu đã có, và ghi `outcome = partial` cùng một coverage note nhắc
mốc `rate_limited_at`.

Vì sao `rate_limited` KHÔNG gộp vào `source_blocked` (ST-3): rate limit nghĩa là X **vẫn cho vào** nhưng bảo
chờ; `source_blocked` nghĩa là X **không cho vào**. Hai tình huống dẫn tới hai trạng thái run khác nhau và hai
màn hình khác nhau ở REQ-AC15. SRC-SPEC §9.3 (XN) chốt cách xử lý: *"Rate limit / bị chặn → dừng đợt, ghi lý
do, không luân chuyển gì để lách"* — dừng **đợt**, không phải khoá **hệ thống**.

**ST-7 có mã riêng kể từ FIX1.** `CR-PC05-01` đã được ruling FIX3 chấp nhận: `SOURCE_LAYOUT_CHANGED` nay là
một mã trong `contracts/errors.yaml` và `source_layout_changed` là một giá trị `stop_reason` trong
`contracts/state/run.yaml`. Lý do nó **không** được gộp vào `source_blocked`: bố cục đổi nghĩa là *vào được
nhưng không đọc được*, còn bị chặn nghĩa là *không cho vào* — và hành động gỡ khác hẳn. Cái đầu cần người phát
triển sửa bộ đọc; cái sau thì không ai làm gì được ngay. Gộp chúng sẽ để một lỗi **sửa được** nằm chờ như một
lỗi không sửa được. Vì cần người chú ý ngay, `SOURCE_LAYOUT_CHANGED` **tạo một alert intent** (khác
`X_ACCESS_BLOCKED`, vốn không tạo). `parser_degraded_count` vẫn được ghi vì probe M0 chạy dry-run và không gọi
`worker.report_stop`.

---

## 5. Ghi nhận mỗi đợt

Định dạng: một file **JSONL**, mỗi dòng một đợt, ghi vào thư mục do Owner chỉ định trên máy cá nhân.
**Không** ghi vào DB (M0 chưa có DB). **Không** gửi lên server.

| Trường | Kiểu | Bắt buộc | Ý nghĩa |
| --- | --- | --- | --- |
| `probe_run_id` | string (ULID) | ✓ | Định danh đợt |
| `started_at`, `ended_at` | string, UTC RFC 3339 ms | ✓ | Giờ máy cá nhân; ghi rõ đây **không** phải giờ server (AMD-B08) |
| `duration_s` | integer | ✓ | |
| `search_terms` | array[string] | ✓ | Từ khóa đã dùng. Tag ở đây **chỉ để tìm kiếm** (REQ-D24) |
| `posts_seen` | integer | ✓ | Số post **nhìn thấy** trên feed |
| `posts_parsed_ok` | integer | ✓ | Số post bóc được đủ trường bắt buộc |
| `posts_new_vs_previous_runs` | integer | ✓ | Số `x_post_id` chưa xuất hiện ở các đợt trước. **Đây là con số trả lời REQ-A1**, không phải `posts_seen` |
| `posts_with_paper_link` | integer | ✓ | Post có link paper |
| `posts_image_only` | integer | ✓ | Post chỉ có ảnh, không link ⇒ "chỉ có post", **không đoán ID** (REQ-D33) |
| `author_threads_opened` | integer | ✓ | Thread mở ra; **chỉ** thread của chính tác giả (REQ-D31) |
| `challenge_count` | integer | ✓ | ST-1 |
| `session_expired_count` | integer | ✓ | ST-2 |
| `blocked_count` | integer | ✓ | ST-3 |
| `rate_limited_count` | integer | ✓ | ST-4. Số lần nguồn báo giới hạn nhịp trong đợt |
| `rate_limited_at` | string, UTC RFC 3339 ms \| null | ✓ | ST-4. Mốc lần báo giới hạn ĐẦU TIÊN trong đợt; NOT NULL khi `stop_reason = rate_limited`. Vận hành thật ghi mốc này vào `run.rate_limited_at` và nhắc lại trong coverage note (ruling CR-PC10-02) |
| `parser_degraded_count` | integer | ✓ | ST-7. Giữ tên `parser_degraded_count` cho TRƯỜNG ĐẾM của probe; `stop_reason` tương ứng là `source_layout_changed` (đổi ở FIX1) |
| `stop_reason` | enum | ✓ | `limit_reached` \| `captcha` \| `session_expired` \| `source_blocked` \| `rate_limited` \| `source_layout_changed` \| `operator_stop`. Sáu giá trị đầu khớp `contracts/state/run.yaml` §1; `operator_stop` là giá trị RIÊNG của probe (ST-8) vì vận hành thật không có nút dừng tay cho collector |
| `limit_kind` | enum \| null | ✓ | `posts` \| `duration` \| null. NOT NULL khi `stop_reason = limit_reached` (REQ-A7: điều kiện dừng phải rõ) |
| `cursor_invalidated` | boolean | ✓ | Con trỏ feed mất hiệu lực giữa chừng (B05) |
| `unobservable_scope_vi` | string | ✓ | **Bắt buộc không rỗng.** Câu mô tả phần feed **không** quan sát được: khoảng thời gian bị bỏ, tài khoản không thấy, phần bị cắt vì ngân sách. Đây là chỗ duy nhất trong probe ghi giới hạn bao phủ (AMD-B05) |
| `notes_vi` | string | | Quan sát định tính |

**Không ghi vào file:** nội dung post nguyên văn, cookie, token, ảnh chụp màn hình có thông tin phiên,
đường dẫn tuyệt đối chứa tên người dùng. Log phải che secrets trước khi ghi (SRC-SPEC §11.2).

---

## 6. Cổng chấp nhận của Owner (trước khi chạy)

SP1 yêu cầu protocol/stop/go-no-go **được chấp nhận** trước. Owner cần xác nhận bốn điều, bằng văn bản:

1. **D09** — dùng Chrome profile riêng của dự án (SRC-SPEC §13.1 câu hỏi 1, **chặn M0**).
2. Ngân sách §3 và điều kiện dừng §4 là chấp nhận được với tài khoản X của Owner.
3. Tiêu chí go/no-go §7 là tiêu chí Owner đồng ý dùng để kết luận.
4. Hiểu rằng probe chạy trên **tài khoản X thật của Owner** và mang rủi ro bị hạn chế tài khoản (REQ-A7),
   và rủi ro đó **không kiểm chứng được trước**.

Chưa có đủ bốn xác nhận ⇒ trạng thái là `OWNER_DECISION_REQUIRED` và probe **không được chạy**.

---

## 7. Tiêu chí go / no-go

Tính trên toàn bộ N đợt đã chạy (5 ≤ N ≤ 10). Mọi ngưỡng dưới đây là **PROVISIONAL do PC05 đề xuất**;
Owner chốt ở §6 mục 3.

| ID | Tiêu chí | Ngưỡng | Đơn vị | Lý do chọn ngưỡng này |
| --- | --- | --- | --- | --- |
| GO-1 | Số đợt kết thúc bằng `limit_reached` (tức chạy hết ngân sách mà không bị cắt) | ≥ 60% của N | tỉ lệ | Dưới 60% nghĩa là **đa số** đợt bị nguồn cắt ngang; khi đó lịch 2 đợt/ngày không cho kết quả dự đoán được. Không đặt 100% vì một hai lần bị cắt là bình thường. |
| GO-2 | `challenge_count` cộng dồn | ≤ 1 trên mỗi 5 đợt | lần/đợt | Mỗi challenge cần **người ngồi trước máy** xử lý (SRC-SPEC §5.4). Tần suất cao hơn biến sản phẩm "tự chạy" thành sản phẩm "gọi người". Đây là ngưỡng về trải nghiệm, không phải về kỹ thuật. |
| GO-3 | `blocked_count` cộng dồn | = 0 | lần | Một lần bị chặn thật là tín hiệu định tính, không phải nhiễu thống kê (REQ-A7). Bất kỳ giá trị > 0 ⇒ **no-go**, dừng và báo. |
| GO-4 | Trung vị `posts_new_vs_previous_runs` ở các đợt sau đợt đầu | ≥ 5 | bài/đợt | Nếu mỗi đợt chỉ mang về vài bài mới thì báo cáo hai lần một ngày không có nội dung. Dùng **trung vị** chứ không phải trung bình để một đợt bội thu không che các đợt rỗng. |
| GO-5 | `posts_parsed_ok / posts_seen` | ≥ 0.90 | tỉ lệ | Parser bóc được ít nhất 90% số bài nhìn thấy. Thấp hơn nghĩa là hợp đồng ingest sẽ nhận dữ liệu thiếu trường một cách hệ thống. |
| GO-6 | `parser_degraded_count` | = 0 | lần | Bố cục đổi giữa probe ⇒ kết quả không kết luận được; sửa parser rồi chạy lại từ đầu. |
| GO-7 | `unobservable_scope_vi` được điền ở **mọi** đợt | 100% | tỉ lệ | Không phải phép đo mà là kỷ luật ghi chép: một probe không ghi phần mình **không** thấy sẽ bị đọc thành "đã quét đủ" (AMD-B05). |

**Kết luận:**

- **GO** — tất cả GO-1..GO-7 đạt. Nghĩa là: *"nguồn X khả thi ở mức ngân sách đã thử, trong cửa sổ đã đo"*.
  Không có nghĩa nguồn X ổn định lâu dài (REQ-A7 vẫn là KC).
- **NO-GO** — bất kỳ tiêu chí nào trượt. Báo quyết định **blocked** cho nguồn X kèm số liệu. **Không**
  chuyển sang X API trả phí, **không** nới ranh giới §2 rồi chạy lại.
- **KHÔNG KẾT LUẬN** — N < 5, hoặc GO-6 trượt. Chạy lại sau khi sửa nguyên nhân; không suy diễn từ dữ liệu thiếu.

Sau GO, Owner dùng chính số liệu này để chốt REQ-OQ05 (giới hạn thật mỗi đợt).

---

## 8. Giới hạn nguồn (ràng buộc thu thập)

Những giới hạn này được gửi kèm mỗi assignment trong `search_config.source_limits`
(`contracts/schemas/worker-assignment.schema.json`), để collector không phải suy diễn.

| ID | Giới hạn | Giá trị | Căn cứ | Oracle |
| --- | --- | --- | --- | --- |
| SL-1 | Chỉ mở thread khi đó là thread **do chính tác giả viết** | `author_thread_only: true` | REQ-D31 (XN) | `thread_context` trong lô chỉ chứa post cùng `author.id` với post gốc |
| SL-2 | **Không** ingest replies của người ngoài | `external_replies: excluded` | REQ-D31 — replies hoãn sang P1 | `COUNT(post WHERE author != post gốc AND nguồn = thread) = 0` |
| SL-3 | Post chỉ có ảnh chụp paper, không có link ⇒ **không đoán ID**, thành mục "chỉ có post" | `image_only_post_policy: post_only_no_id_guess` | REQ-D33 (ĐX), I03 | Fixture `h-metadata-unavailable-post-only.json`: `doi` và `arxiv_id` đều null, target `kind: post` |
| SL-4 | Chrome của collector **chỉ** lo X | `chrome_scope: x_only` | REQ-D32 (XN), denied case NC-08 | Trace mạng của tiến trình collector không có host nào ngoài X |
| SL-5 | Metadata paper lấy qua **API từ server** | `paper_metadata_source: server_api` | REQ-D32 (XN) | `research.fetch_work_metadata` do `MOD-ingest-service` gọi, không phải collector |
| SL-6 | Số post ngữ cảnh thread tối đa | 50 | `contracts/data/entities.yaml §limits` (PROVISIONAL) | Vượt ⇒ item vào `counts.rejected`, **không cắt cụt âm thầm** |
| SL-7 | Collector **không** ghi SQLite; mọi dữ liệu đi qua API có xác thực | — | REQ-D08 (ĐX), denied case NC-05 | Tiến trình collector không có driver DB và không có đường mạng tới volume |
| SL-8 | Collector **không** xếp hàng task phân tích trực tiếp | — | AMD-B12 (cạnh `COL → AW` đã bị xóa) | Không có cạnh nào từ `MOD-x-collector` tới `MOD-analysis-worker` trong `contracts/modules.yaml` |

---

## 9. Quy tắc connector nghiên cứu (arXiv / OpenAlex)

### 9.1 Ranh giới

| ID | Quy tắc | Căn cứ |
| --- | --- | --- |
| CN-1 | Chỉ gọi host trong **allowlist** đã cấu hình | SRC-PLAN §6; `contracts/modules.yaml` `network_egress` |
| CN-2 | **Không** nhận chỉ dẫn fetch URL tùy ý từ model | I11, denied case NC-07, SRC-SPEC §11.4 |
| CN-3 | **Không** điều khiển Chrome | denied case NC-08 |
| CN-4 | Chỉ tra bằng **ID đã chuẩn hóa** (DOI/arXiv id), không tra bằng chuỗi tự do do model sinh | I03, NC-07 |
| CN-5 | Metadata thiếu **không** chặn đợt chạy: target tồn tại ở mức `evidence_level = post_only` | REQ-D33; `contracts/state/run.yaml` T-RUN-03 |
| CN-6 | **Không** đoán DOI/arXiv id từ văn bản chưa chuẩn hóa | REQ-D33, I03 |

### 9.2 Nhịp gọi và định danh — **KC, chưa đọc tài liệu**

REQ-A6 (KC) và REQ-D34 (KC) đều nói cùng một điều: *"Nhịp gọi arXiv và yêu cầu email liên hệ của OpenAlex:
đọc tài liệu chính thức khi triển khai."* SRC-SPEC §13.2 nhắc lại như một điểm không được bỏ qua.

**Tôi chưa đọc hai tài liệu đó** (gói này chạy không có mạng). Vì vậy các giá trị dưới đây **cố ý để trống**,
và trạng thái là `KC`. Điền số bịa vào đây sẽ là bằng chứng giả.

| Tham số | Giá trị | Trạng thái | Tài liệu phải đọc | Ai đọc, khi nào |
| --- | --- | --- | --- | --- |
| `arxiv_requests_per_window` | *(chưa xác định)* | **KC** | Trang điều khoản/hướng dẫn API công khai của arXiv | Người triển khai, tại thời điểm triển khai (REQ-S13.2-01) |
| `arxiv_window_seconds` | *(chưa xác định)* | **KC** | như trên | như trên |
| `openalex_requests_per_window` | *(chưa xác định)* | **KC** | Tài liệu API công khai của OpenAlex | như trên |
| `openalex_window_seconds` | *(chưa xác định)* | **KC** | như trên | như trên |
| `openalex_contact_identity` | *(chưa xác định)* | **KC** | OpenAlex yêu cầu một định danh liên hệ (REQ-D34 gọi là "yêu cầu email liên hệ") — hình thức chính xác phải đọc từ tài liệu | như trên |
| `min_interval_ms` | 3000 | **PROVISIONAL** | — | Sàn an toàn duy nhất đang có hiệu lực; xem `contracts/retry-policy.yaml §research_connector_rate_limit` |

**Ghi chú về URL tài liệu.** PKT-PC05 yêu cầu ghi "the exact doc URL from the sources". Tôi đã tra cả hai
nguồn: `research-radar-spec.md` (D34, §13.2) và `research-radar-pre-code-plan.md` **không chứa URL nào** cho
arXiv hay OpenAlex — chúng chỉ nói "đọc tài liệu chính thức". Vì vậy tôi ghi **định danh tài liệu** thay cho
URL, và **không** bịa URL. Đây là một khoảng trống có chủ đích, ghi lại ở `CR-PC05-03`.

**Cho tới khi bốn giá trị KC được điền:**

- Connector chạy dưới sàn `min_interval_ms = 3000` (≤ 1 request mỗi 3 giây cho mỗi nguồn).
- `Retry-After` do nguồn trả về **luôn thắng** mọi giá trị cấu hình.
- Module research connector **không được** coi là `CONTRACT_READY` (SRC-PLAN §10: *"module có policy chưa chốt
  không được CONTRACT_READY"*).

### 9.3 Điều khoản nhà cung cấp AI — cùng loại vấn đề

REQ-A5 (KC) và SRC-SPEC §13.2: *"Đọc điều khoản của từng nhà AI trước khi bật đường CLI/ACP cho nhà đó."*
Không thuộc phạm vi PC05 (PC06 sở hữu), ghi ở đây để danh sách KC của gói này đầy đủ: **chưa đọc**, và
`contracts/modules.yaml` đã quy định adapter nào không kiểm chứng được cô lập thì **giữ trạng thái disabled**
(B13/ADR-0010).

---

## 10. Điều gì probe này **không** chứng minh

Danh sách này tồn tại để kết quả probe không bị đọc rộng hơn nó đo được.

1. **Không** chứng minh nguồn X ổn định lâu dài — REQ-A7 vẫn là `KC` sau khi probe GO.
2. **Không** chứng minh đường ingest đúng — M0 chạy dry-run, không gọi `ingest.submit_batch`. Đường ingest
   được kiểm **offline** bằng `acceptance/fixtures/collection/`.
3. **Không** chứng minh dedup hoạt động — dedup theo `x_post_id` xảy ra ở server, ngoài phạm vi M0.
4. **Không** chứng minh coverage đầy đủ — `unobservable_scope_vi` tồn tại chính vì phần không quan sát được
   là có thật (AMD-B05).
5. **Không** chứng minh chất lượng nội dung — bài lấy được có khớp chủ đề hay không thuộc REQ-A2/A3, đo ở M3.
6. **Không** thay thế cho `SC01`–`SC04` — các scenario đó có oracle riêng và chạy được bằng fixture.

---

## 11. Truy vết

| Mục | Scenario | Invariant | Yêu cầu |
| --- | --- | --- | --- |
| §3 lịch và ngân sách | SC01, SC03 | — | REQ-A1, REQ-OQ05, REQ-AC01, REQ-AC03 |
| §4 điều kiện dừng | SC03, SC04 | I10 | REQ-A7, REQ-AC03, REQ-AC04 |
| §5 ghi nhận | — | I02 (gián tiếp: probe không ACK gì) | REQ-A1 |
| §8 giới hạn nguồn | SC07, SC11 | I03, I11 | REQ-D31, REQ-D32, REQ-D33, REQ-D08 |
| §9 connector | SC11 | I11 | REQ-A6, REQ-D34, REQ-S13.2-01 |
