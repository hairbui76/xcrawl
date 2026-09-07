---
contract_id: CT-precode-decision-register
version: 0.1.0
status: draft
owner_role: requirements owner (PC00)
source_refs:
  - SRC-SPEC §1.4, §2, §3, §4, §5, §6, §7, §8, §9, §10, §11, §12, §13
  - SRC-PLAN §3, §3.1, §6, §7, §8, §9, §10, §11, §12
requirement_refs: [precode/requirements.csv — toàn bộ 246 dòng]
decision_refs: [B01..B17, AMD-B01, AMD-B02, AMD-B03, AMD-B04, AMD-B05, AMD-B07, AMD-B08, AMD-B09, AMD-B10, AMD-B11, AMD-B12, AMD-B15, AMD-B16, AMD-B17, ADR-0001..ADR-0010]
invariant_refs: [I01..I15]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies:
  - precode/baseline.json
  - precode/source/spec-v0.2.md
  - precode/source/pre-code-plan-v0.1.md
  - precode/requirements.csv
scope: >
  Sổ đăng ký các điểm chưa đóng của đặc tả (B01–B17), phương án xử lý tạm thời, các amendment
  làm thay đổi hành vi đã cam kết, các mục P0 còn ở trạng thái ĐX, và các phát hiện mâu thuẫn
  mới do PC00 tìm ra. File này KHÔNG đóng bất kỳ blocker nào; mọi mục ở trạng thái PROVISIONAL
  hoặc OWNER_DECISION_REQUIRED và chờ Owner phê chuẩn qua precode/owner-decision-request.md.
verification: E0 — self-validation bằng script kiểm đếm (EV-PC00-04); không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Sổ đăng ký quyết định — Pre-code PC00

**Trạng thái phiên:** `DOCUMENTARY_DRAFT`, enforcement `NOT_IMPLEMENTED`, product status `NOT_READY_FOR_PRODUCT_CODE`.

## 0. Cách đọc file này

| Nhãn | Nghĩa trong phiên này |
| --- | --- |
| `OPEN` | Chưa có phương án nào được ghi nhận |
| `PROVISIONAL` | Coordinator đã ghi nhận phương án theo PC-ĐX của SRC-PLAN dưới `AUTH-OWNER-20260906-01`; **chưa** phải quyết định của Owner |
| `OWNER_DECISION_REQUIRED` | Không có phương án mặc định an toàn; phạm vi liên quan bị chặn tường minh |

Không mục nào trong file này được ghi `CLOSED`, `ACCEPTED` hay `XN`. `agent_profile/registry.json` vẫn liệt kê B01–B17 trong `open_product_blockers`; file này không sửa registry đó.

Trạng thái yêu cầu (`XN | UQ | ĐX | KC`) trong `precode/requirements.csv` **giữ nguyên như đặc tả**. Amendment ở §3 mô tả văn bản *đề xuất thay thế*, chưa được áp vào đặc tả; đặc tả v0.2 vẫn là nguồn chuẩn cho tới khi Owner phê chuẩn.

## 1. Bảng tổng hợp B01–B17

| ID | Chủ đề | Status | decision_owner | Gói bị chặn | Gate bị chặn | Amendment | ADR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | Mốc freeze tag | PROVISIONAL | Owner | PC04, PC07 | G3 | AMD-B01 | ADR-0004 |
| B02 | Mô hình trạng thái run | PROVISIONAL | Owner | PC03 | G2 | AMD-B02 | ADR-0002 |
| B03 | Trạng thái gửi không xác định | PROVISIONAL | Owner | PC07 | G3 | AMD-B03 | ADR-0003 |
| B04 | Coverage, pending và backfill | PROVISIONAL | Owner | PC04 | G3 | AMD-B04 | ADR-0004 (liên đới) |
| B05 | Cam kết không lấy lại bài | PROVISIONAL | Owner | PC03, PC05 | G2 | AMD-B05 | ADR-0002 (liên đới) |
| B06 | Identity, alias, phiên bản, target | PROVISIONAL | Owner | PC02 | G2 | — (bổ sung, không sửa văn bản) | ADR-0009 |
| B07 | Khóa kết quả phân tích và generation | PROVISIONAL | Owner | PC02, PC06 | G2 | AMD-B07 | ADR-0008 |
| B08 | Timezone và timestamp | PROVISIONAL | Owner | PC03, PC04 | G2 | AMD-B08 | ADR-0007 |
| B09 | Ngoại lệ liên kết Telegram | PROVISIONAL | Owner | PC07 | G3 | AMD-B09 | — |
| B10 | Resume và tập lệnh Telegram | PROVISIONAL | Owner | PC03, PC07 | G3 | AMD-B10 | — |
| B11 | Backup và restore | PROVISIONAL | Owner | PC08 | G3 | AMD-B11 | ADR-0005 |
| B12 | Topology và Chrome profile | PROVISIONAL | Owner | PC01, PC05, PC06 | G1 | AMD-B12 | ADR-0001 |
| B13 | Phạm vi secret và cô lập CLI | PROVISIONAL | Owner | PC01, PC06, PC08 | G1 | — (bổ sung chính sách) | ADR-0010 |
| B14 | Mật độ vector | PROVISIONAL | Owner | PC04, PC09 | G3 | — (bổ sung định nghĩa) | — |
| B15 | Phạm vi bất biến 0 trùng | PROVISIONAL | Owner | PC02, PC09 | G2 | AMD-B15 | ADR-0009 |
| B16 | Tách tuyên bố và suy luận | PROVISIONAL | Owner | PC06 | G3 | AMD-B16 | — |
| B17 | Lúc enqueue summary | PROVISIONAL | Owner | PC04, PC06 | G3 | AMD-B17 | — |

## 2. Chi tiết từng blocker

### B01 — Mốc hiệu lực của bộ tag

- **Mâu thuẫn nguồn.** SRC-SPEC §3.4 hàng `C03/D-tag`: "Mốc hiệu lực tag theo **thời điểm gửi**: bộ tag lúc tạo báo cáo quyết định nội dung" — một hàng nêu hai mốc khác nhau (*gửi* và *tạo*). SRC-SPEC §9.2 lại ghi sau khi report được dựng thì "Không dựng lại; chỉ gửi lại". SRC-PLAN §3 B01 bổ sung: "tag có thể đổi khi Telegram đang retry".
- **PC-ĐX của kế hoạch.** "Chọn một thời điểm chốt: khuyên dùng transaction publish report; ghi `tag_config_version` bất biến."
- **Quyết định tạm thời (PROVISIONAL).** Tag được đóng băng tại **transaction publish của báo cáo**. Report lưu `tag_config_version` bất biến. Delivery không bao giờ đổi nội dung đã publish. Cụm "thời điểm gửi" trong `C03/D-tag` được đọc lại là "thời điểm publish report".
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/schemas/report.schema.json`, `contracts/state/report.yaml`, `contracts/telegram/delivery.md`, `acceptance/fixtures/reporting/`.
- **Gate bị chặn.** G3 (PC04, PC07). Không chặn G0/G1.
- **Thay đổi oracle.** REQ-AC05 giữ nguyên kết quả nhưng mốc so sánh đổi từ "lúc gửi Telegram" sang "lúc commit publish"; thêm oracle mới: đổi tag sau publish nhưng trước delivery **không** làm đổi `report_item` và không làm đổi hash payload đã đóng.
- **Nếu Owner bác bỏ.** Nếu Owner thật sự muốn mốc theo lúc gửi thì PC04 và PC07 phải thiết kế thêm report revision và xử lý trường hợp đã gửi một phần; toàn bộ PC04/PC07 ở lại BLOCKED cho tới khi có thiết kế đó. Không có phương án nào cho phép giữ nguyên chữ "thời điểm gửi" mà vẫn giữ được I05.
- **Liên kết.** AMD-B01, ADR-0004, I05, REQ-CTAG, REQ-D23, REQ-D24, REQ-AC05, REQ-S8.1-03, REQ-S8.2-01, REQ-S8.2-02.

### B02 — Mô hình trạng thái của run

- **Mâu thuẫn nguồn.** SRC-SPEC §5.2 vẽ `reporting --> delivered` và `reporting --> delivered_partial` **bên trong** vòng đời run, trong khi SRC-SPEC §9.1 khẳng định "Trạng thái job và trạng thái gửi báo cáo là hai thứ độc lập". Ngoài ra `stopped_limit` (§9.1, REQ-AC03) vừa là điểm dừng vừa vẫn có thể sinh báo cáo.
- **PC-ĐX của kế hoạch.** "Tách phase/status/outcome của run; delivery độc lập. Ánh xạ rõ tên cũ sang trạng thái chuẩn." (SRC-PLAN §8.1)
- **Quyết định tạm thời (PROVISIONAL).** Áp dụng đúng mô hình SRC-PLAN §8.1: `phase` ∈ {collecting, enriching, analyzing, reporting}; `status` ∈ {queued, running, waiting_retry, needs_user, blocked, completed, failed, cancelled}; `outcome` ∈ {complete, partial, empty, failed, cancelled}; `stop_reason` là trường riêng. Delivery là vòng đời tách rời. Bảng ánh xạ enum cũ sang mới nằm ở AMD-B02.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/run.yaml`, `contracts/state/report.yaml`, `contracts/errors.yaml`, `contracts/ui/screens.yaml` (read model của Runs và Run detail).
- **Gate bị chặn.** G2 (PC03), kéo theo G3 cho PC07.
- **Thay đổi oracle.** REQ-AC03 đổi từ `run.status == stopped_limit` sang `status == completed AND stop_reason == limit_reached AND outcome ∈ {partial, complete}`. REQ-AC15 đổi từ so sánh ba enum sang so sánh ba cặp `(status, outcome, stop_reason)`; ràng buộc hiển thị của REQ-S8.3-01..03 không đổi.
- **Nếu Owner bác bỏ.** Giữ enum cũ thì `delivered` nằm trong run và I09 bị vi phạm ngay từ hợp đồng; PC03 và PC07 ở lại BLOCKED vì không có cách phân biệt "run xong nhưng chưa gửi" với "run xong và đã gửi".
- **Liên kết.** AMD-B02, ADR-0002, I09, I13, REQ-S5.2-01, REQ-S9.1-01, REQ-S9.1-02, REQ-AC03, REQ-AC15.

### B03 — Trạng thái gửi không xác định

- **Mâu thuẫn nguồn.** SRC-SPEC AC-14: "app vẫn giữ báo cáo đầy đủ và **không có tin nào bị gửi hai lần**", cùng §9.3 "`delivery` một hàng cho một (report, kênh)". SRC-PLAN §3.1 chỉ ra tài liệu Telegram Bot API `sendMessage` không có tham số idempotency key do client cung cấp, nên một hàng UNIQUE trong DB không chứng minh exactly-once ở mạng ngoài.
- **PC-ĐX của kế hoạch.** "Thêm `delivery.unknown`; dừng retry tự động khi không biết đã gửi chưa. Thay bảo đảm tuyệt đối bằng chính sách có thể kiểm chứng, cần người dùng duyệt amendment."
- **Quyết định tạm thời (PROVISIONAL).** Thêm trạng thái `delivery.unknown`. Timeout hoặc mất kết nối sau điểm có thể đã gửi đưa delivery vào `unknown`; **không** retry tự động từ `unknown`; app hiển thị "chưa xác định" và Operator (Owner) quyết định có chấp nhận nguy cơ trùng. Digest nhiều phần dùng `delivery_part` với index, payload hash và receipt từng phần; phần `unknown` không được gửi lại chỉ vì tổng thể chưa `sent`.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/delivery.yaml`, `contracts/telegram/delivery.md`, `contracts/errors.yaml` (`TELEGRAM_SEND_UNCERTAIN`), `acceptance/fixtures/telegram/`.
- **Gate bị chặn.** G3 (PC07).
- **Thay đổi oracle.** REQ-AC14 đổi từ "không có tin nào bị gửi hai lần" (bảo đảm tuyệt đối, không kiểm chứng được) sang "không có lần gửi lặp **tự động**; mọi trạng thái không chắc chắn được hiện là `unknown` và cần thao tác tay của Owner". Thêm fixture: Telegram nhận tin rồi cắt response.
- **Nếu Owner bác bỏ.** Nếu Owner giữ nguyên chữ AC-14 thì PC07 không thể đạt `CONTRACT_READY`, vì không có bằng chứng nào chứng minh được exactly-once qua Telegram API; phạm vi delivery ở lại BLOCKED.
- **Liên kết.** AMD-B03, ADR-0003, I09, REQ-AC14, REQ-D38, REQ-S9.1-03, REQ-S9.2-05, REQ-S9.3-06.

### B04 — Coverage, pending và backfill

- **Mâu thuẫn nguồn.** SRC-SPEC D27 yêu cầu kỳ nối liền theo ngày phát hiện; D57 cấm gửi báo cáo rỗng ("chỉ ghi vào trạng thái run"); §10.4 nói mục vượt giới hạn "chờ đợt sau chứ không bị bỏ". Ba điều này va nhau: nếu kỳ rỗng không tạo report thì con trỏ coverage lấy từ đâu, và backlog AI nằm ngoài kỳ đã đóng thì được tính vào kỳ nào.
- **PC-ĐX của kế hoạch.** "Dùng sổ coverage độc lập report hiển thị; pending item và backfill ledger độc lập con trỏ kỳ. Chốt khi nào coverage tiến."
- **Quyết định tạm thời (PROVISIONAL).** Coverage ledger là sổ authoritative, độc lập với việc có report hiển thị hay không. Sổ pending item và sổ backfill là hai sổ riêng, không phụ thuộc con trỏ kỳ. Coverage chỉ tiến tại **commit publish**, kể cả với kỳ rỗng (kỳ rỗng có coverage record nhưng không sinh digest). Backfill N ngày được tiêu thụ đúng một lần cho mỗi subscription activation đã định danh; crash của builder không tiêu thụ backfill.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/state/report.yaml`, `acceptance/fixtures/reporting/`.
- **Gate bị chặn.** G3 (PC04).
- **Thay đổi oracle.** REQ-AC08 thêm oracle: sau một kỳ rỗng, `coverage_from` của kỳ kế tiếp vẫn bằng `coverage_to` của kỳ rỗng (không hở). REQ-D57 giữ nguyên hành vi không gửi digest nhưng thêm hàng coverage.
- **Nếu Owner bác bỏ.** Nếu coverage buộc phải suy ra từ danh sách report hiển thị thì mọi kỳ rỗng tạo lỗ hổng; I06 không thể giữ và PC04 ở lại BLOCKED.
- **Liên kết.** AMD-B04, I06, REQ-D27, REQ-D28, REQ-D57, REQ-S10.4-03, REQ-AC08, REQ-OQ04.

### B05 — Cam kết "không lấy lại bài đã có"

- **Mâu thuẫn nguồn.** SRC-SPEC §9.2 và AC-04: "Tiếp từ con trỏ, không lấy lại bài đã có". SRC-PLAN §3 B05: "cursor của feed động chưa chứng minh ổn định"; SRC-PLAN §8.1: "Nếu con trỏ feed mất hiệu lực, cho phép đọc lại theo recovery policy và dedup ở ingest".
- **PC-ĐX của kế hoạch.** "Cam kết ingest không trùng; việc đọc lại có thể cần thiết. Checkpoint chỉ chứa dữ liệu server đã ACK; ghi rõ giới hạn bao phủ X."
- **Quyết định tạm thời (PROVISIONAL).** Cam kết được phát biểu lại là **không ingest trùng theo `x_post_id`**, không phải "không bao giờ đọc lại trang". Việc đọc lại được phép theo recovery policy. Checkpoint chỉ chứa dữ liệu server đã ACK. Giới hạn bao phủ X được ghi vào metadata của run; `completed` không có nghĩa đã quét đủ toàn bộ X.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/run.yaml`, `contracts/http/openapi.yaml`, `contracts/schemas/ingest-batch.schema.json`, `contracts/schemas/ingest-receipt.schema.json`, `acceptance/fixtures/collection/`.
- **Gate bị chặn.** G2 (PC03), G3 (PC05).
- **Thay đổi oracle.** REQ-AC04 vế cuối đổi từ đếm số lần tải trang sang đếm số hàng `post` sau replay: sau resume, `COUNT(post)` không tăng cho các `x_post_id` đã có, và receipt cũ được trả lại nguyên vẹn. Bổ sung oracle âm: request count **không** phải oracle.
- **Nếu Owner bác bỏ.** Giữ nguyên chữ "không lấy lại bài đã có" thì phải chứng minh cursor của X ổn định — điều SRC-PLAN xếp vào loại không kiểm chứng được trước; PC05 ở lại BLOCKED và probe A1 không có tiêu chí pass rõ ràng.
- **Liên kết.** AMD-B05, I02, REQ-AC04, REQ-S9.2-01, REQ-S5.4-01, REQ-A1, REQ-A7.

### B06 — Identity, alias, phiên bản và target

- **Mâu thuẫn nguồn.** SRC-SPEC §7.1 định nghĩa `work` với `doi` UNIQUE và `arxiv_id` UNIQUE, nhưng hai bản ghi có thể đã tồn tại rồi mới biết là cùng công trình. D33 tạo mục "chỉ có post" mà §7.1 không có model analysis cho post-only; `saved_item` dùng `UNIQUE(owner, work/post)` mơ hồ.
- **PC-ĐX của kế hoạch.** "Chốt identity/alias merge, work version và target phân biệt work/post. Không coi hai UNIQUE là đủ giải mọi trùng lặp."
- **Quyết định tạm thời (PROVISIONAL).** Mô hình identity gồm bảng alias và audit trail cho mỗi lần merge; `work` có phiên bản (arXiv vN là phiên bản, không phải công trình khác); `target` là tagged union `work | post`, dùng thống nhất cho Saved, analysis và report item.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/data/entities.yaml`, `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/schemas/target.schema.json`, `acceptance/fixtures/identity/`.
- **Gate bị chặn.** G2 (PC02).
- **Thay đổi oracle.** REQ-AC07 và REQ-AC13 thêm oracle: alias map sau merge, provenance list giữ đủ nguồn, và Saved của target post-only vẫn bị ràng buộc duy nhất. Không có văn bản đặc tả nào bị thay; đây là bổ sung định nghĩa.
- **Nếu Owner bác bỏ.** Không có phương án thay thế: nếu chỉ dựa vào hai cột UNIQUE thì mọi post-only mất khóa duy nhất và REQ-AC13 không có oracle. Phạm vi PC02 ở lại BLOCKED.
- **Liên kết.** ADR-0009, I03, I08, REQ-D17, REQ-D33, REQ-S9.2-02, REQ-S9.3-05, REQ-S9.3-09, REQ-AC07, REQ-AC13.

### B07 — Khóa kết quả phân tích và generation

- **Mâu thuẫn nguồn.** SRC-SPEC D25 "Phân tích và summary tạo **một lần** cho mỗi công trình rồi tái sử dụng" (XN) đứng cạnh D26 "Phân tích lại chỉ khi người dùng bấm tay, hoặc paper có phiên bản mới; giữ bản cũ" (ĐX). §7.1 `analysis` chỉ có "phiên bản" mà không có source fingerprint hay task key.
- **PC-ĐX của kế hoạch.** "Định nghĩa một kết quả hợp lệ mỗi target/version/task/input/prompt contract; reanalysis có generation mới. Attempt lỗi không tính là kết quả hoàn thành."
- **Quyết định tạm thời (PROVISIONAL).** Analysis key gồm: canonical id của target, source version/fingerprint, task type, phiên bản prompt/schema và generation. Mỗi key có tối đa **một** kết quả hợp lệ. Reanalysis tạo generation mới. Attempt thất bại hoặc không xác định không phải kết quả. Đổi tag **không** đổi key. Đổi provider/model không tự invalidate; giữ kết quả cũ tới khi Owner yêu cầu reanalysis.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/data/entities.yaml`, `contracts/ai/tasks.yaml`, `contracts/schemas/analysis-result.schema.json`, `contracts/state/analysis.yaml`.
- **Gate bị chặn.** G2 (PC02), G3 (PC06).
- **Thay đổi oracle.** REQ-AC06 chuyển từ "không phát sinh lần gọi AI nào" sang "provider call counter delta bằng 0 **cho cùng analysis key và generation**"; reanalysis cố ý vẫn được phép tăng counter.
- **Nếu Owner bác bỏ.** Nếu giữ "một lần cho mỗi công trình" theo nghĩa đen thì D26 (phân tích lại) không thực hiện được và mọi retry sau lỗi cũng vi phạm; PC06 ở lại BLOCKED.
- **Liên kết.** AMD-B07, ADR-0008, I04, REQ-D25, REQ-D26, REQ-S7.3-02, REQ-S10.4-02, REQ-AC06.

### B08 — Timezone và timestamp

- **Mâu thuẫn nguồn.** SRC-SPEC D56 "Timezone lấy theo máy chạy app" (UQ). SRC-PLAN §3 B08: "mơ hồ vì browser, server, máy collector khác nhau". D13 và D15 phụ thuộc mốc giờ để tính "sớm nhất được chạy" và gộp đợt quá hạn.
- **PC-ĐX của kế hoạch.** "Lưu một IANA timezone do owner xác nhận; timestamps chuẩn UTC; chốt quy tắc DST và gộp lịch."
- **Quyết định tạm thời (PROVISIONAL).** Một IANA timezone duy nhất lưu trong settings, do Owner xác nhận; mặc định tạm `Asia/Ho_Chi_Minh`. Mọi timestamp lưu ở UTC RFC 3339 với độ chính xác **mili giây**, tie-break bằng ingest sequence. Quy tắc DST và catch-up do PC03 viết thành bảng.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/run.yaml`, `contracts/reporting/time-and-tags.md`, `contracts/ui/screens.yaml` (Settings), `contracts/data/entities.yaml`.
- **Gate bị chặn.** G2 (PC03), G3 (PC04).
- **Thay đổi oracle.** REQ-AC02 cần một mốc giờ xác định để tính "quá hạn"; oracle đổi từ giờ máy sang giờ theo timezone đã cấu hình, với fake-clock cố định.
- **Nếu Owner bác bỏ.** `Asia/Ho_Chi_Minh` chỉ là giá trị tạm; nếu Owner ở múi khác thì mọi fixture lịch phải dựng lại. Bản thân quyết định "một timezone lưu trong settings" không có phương án thay thế nào giữ được tính xác định.
- **Liên kết.** AMD-B08, ADR-0007, REQ-D56, REQ-D13, REQ-D15, REQ-S8.2-08, REQ-AC02, REQ-OQ06.

### B09 — Ngoại lệ liên kết Telegram

- **Mâu thuẫn nguồn.** SRC-SPEC §11.3: "Tin từ chat ID chưa liên kết bị **bỏ im lặng** — không trả lời gì". SRC-SPEC §5.1 bước 4: "Sinh mã liên kết Telegram trong app, gửi mã cho bot" — tức bot **phải** xử lý một thông điệp từ chat chưa liên kết.
- **PC-ĐX của kế hoạch.** "Chốt ngoại lệ hẹp cho yêu cầu liên kết hợp lệ, kiểm mã trước; mọi lệnh khác từ chat lạ bỏ im lặng."
- **Quyết định tạm thời (PROVISIONAL).** Một ngoại lệ hẹp duy nhất: thông điệp từ chat chưa liên kết **khớp đúng định dạng mã liên kết** được đối chiếu với các mã chưa hết hạn và chưa dùng. Mọi thứ khác từ chat chưa liên kết bị bỏ im lặng. Mã sai, hết hạn hoặc đã dùng cũng bị bỏ im lặng (không phản hồi lỗi).
- **Hợp đồng/file bị ảnh hưởng.** `contracts/telegram/commands.yaml`, `contracts/ops/secrets.md`, `acceptance/fixtures/telegram/`.
- **Gate bị chặn.** G3 (PC07).
- **Thay đổi oracle.** REQ-AC18 cần thêm case dương tính: thông điệp mang mã hợp lệ **được** xử lý. Oracle "outbound call count = 0" chỉ áp cho các thông điệp không phải mã liên kết hợp lệ.
- **Nếu Owner bác bỏ.** Không có phương án khác cho luồng thiết lập lần đầu ngoài việc nhập chat ID bằng tay trong app; nếu Owner chọn hướng đó thì §5.1 bước 4 phải viết lại và PC07 ở lại BLOCKED tới khi có văn bản mới.
- **Liên kết.** AMD-B09, REQ-D35, REQ-S5.1-04, REQ-S11.3-01, REQ-S11.3-02, REQ-S11.2-04, REQ-AC18.

### B10 — Resume và tập lệnh Telegram

- **Mâu thuẫn nguồn.** SRC-SPEC §5.4 bước 4: "Bấm 'tiếp tục' trong app **hoặc gửi lệnh trạng thái/chạy ngay**". SRC-SPEC §9 và §5.4 bước 5: run không tự tiếp tục khi hạn chế còn. SRC-SPEC §11.3: "chỉ chat ID đã liên kết ra được **3 lệnh** của D36", trong khi D37 lại yêu cầu "có lệnh hủy liên kết".
- **PC-ĐX của kế hoạch.** "`status` không mutation; `run-now` không vượt `needs_user`. Khuyên nút resume riêng trong app; không tự thêm lệnh Telegram thứ tư."
- **Quyết định tạm thời (PROVISIONAL).** `status` là lệnh chỉ đọc, không gây mutation. `run-now` không bao giờ ghi đè một run đang `needs_user`. Resume là hành động riêng trong app. Không thêm lệnh Telegram thứ tư; **hủy liên kết cũng là hành động trong app** (xem finding F-PC00-01).
- **Hợp đồng/file bị ảnh hưởng.** `contracts/telegram/commands.yaml`, `contracts/state/run.yaml`, `contracts/ui/screens.yaml` (Runs, Run detail, Settings).
- **Gate bị chặn.** G3 (PC07), G2 liên đới (PC03).
- **Thay đổi oracle.** REQ-AC04 thêm oracle âm: gửi `status` hoặc `run-now` khi run đang `needs_user` **không** làm đổi bất kỳ hàng nào; chỉ hành động resume trong app mới cấp lease mới.
- **Nếu Owner bác bỏ.** Nếu Owner muốn resume qua Telegram thì cần lệnh thứ tư và §11.3 ("3 lệnh") phải sửa; phạm vi lệnh Telegram ở lại BLOCKED tới khi có quyết định.
- **Liên kết.** AMD-B10, REQ-D36, REQ-D37, REQ-S5.4-04, REQ-S11.3-03, REQ-S11.3-04, REQ-AC04.

### B11 — Backup và restore

- **Mâu thuẫn nguồn.** SRC-SPEC D58 và §7.3: "Backup: copy file SQLite. Restore: đặt file về chỗ cũ". SRC-PLAN §3.1: "WAL là một phần trạng thái bền của DB; tách file DB khỏi WAL có thể mất transaction đã commit". Đặc tả cũng không nói gì về khôi phục queue và token.
- **PC-ĐX của kế hoạch.** "Chọn backup nhất quán và restore drill có khóa side effect. Không dùng copy file DB đang hoạt động làm bằng chứng đủ."
- **Quyết định tạm thời (PROVISIONAL).** Backup dùng SQLite Online Backup API hoặc `VACUUM INTO` để tạo snapshot nhất quán (an toàn với WAL), kèm manifest chứa hash DB, phiên bản schema, artifact và cấu hình embedding. Restore phải qua drill vào môi trường sạch, có khóa side effect: dispatcher và worker claim bị dừng, outbox cũ không replay, `first_announced` không bị reset trước khi kiểm tra.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/ops/backup-restore.md`, `contracts/ops/deployment.md`, `contracts/state/storage.yaml`, `acceptance/fixtures/recovery/`.
- **Gate bị chặn.** G3 (PC08).
- **Thay đổi oracle.** REQ-AC12 thêm oracle sau restore: hash snapshot của Saved không đổi, và số hàng report/ledger khớp manifest. Thêm oracle âm cho `RESTORE_UNVERIFIED`: trước khi verify không có side effect nào chạy.
- **Nếu Owner bác bỏ.** Copy file DB đang ghi vẫn chạy được trong nhiều trường hợp nhưng không thể dùng làm bằng chứng khôi phục; nếu Owner giữ D58 nguyên văn thì PC08 chỉ đạt tối đa mức mô tả, không đạt `CONTRACT_READY` cho backup/restore.
- **Liên kết.** AMD-B11, ADR-0005, I15, REQ-D58, REQ-S7.3-04, REQ-S6.4-01, REQ-AC12, REQ-S13-09.

### B12 — Topology và Chrome profile

- **Mâu thuẫn nguồn.** SRC-SPEC D09 (profile riêng), D08 (collector đẩy qua API), D42 (LLM cùng máy collector) và D50 (embedding ở server) đều còn **ĐX**. Đồng thời sơ đồ §6.2 có cạnh `COL --> AW`, tức collector đưa dữ liệu **thẳng** cho analysis worker, mâu thuẫn với D08 và với I02.
- **PC-ĐX của kế hoạch.** "Chốt profile và topology. Khuyên analysis nhận task từ server sau ingest commit, không nhận dữ liệu chưa commit từ collector."
- **Quyết định tạm thời (PROVISIONAL).** Giữ D09 (Chrome profile riêng của dự án), D08 (chỉ qua API có xác thực), D42 (analysis worker trên máy cá nhân), D50 (embedding ở server). Analysis worker nhận **task từ server sau ingest commit**, không nhận dữ liệu trực tiếp từ collector; cạnh `COL --> AW` của §6.2 bị xóa.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml`, `contracts/ops/deployment.md`, `contracts/http/openapi.yaml`.
- **Gate bị chặn.** G1 (PC01), kéo theo PC05 và PC06.
- **Thay đổi oracle.** Thêm negative case bắt buộc: collector gọi thẳng analysis worker bị từ chối bởi capability registry (default deny). REQ-AC01 và REQ-AC16 không đổi kết quả nhưng đường đi được kiểm bằng import/dependency rules và API auth tests.
- **Nếu Owner bác bỏ.** D09 vẫn là câu hỏi chặn M0 (REQ-OQ01): nếu Owner muốn dùng profile Chrome mặc định thì §11.2 (phiên X trong profile riêng) phải sửa và rủi ro tài khoản tăng; toàn bộ M0 ở lại BLOCKED tới khi Owner trả lời.
- **Liên kết.** AMD-B12, ADR-0001, I02, REQ-D08, REQ-D09, REQ-D42, REQ-D50, REQ-S6.1-02, REQ-S6.1-03, REQ-S6.2-01, REQ-OQ01.

### B13 — Phạm vi secret và cô lập CLI/ACP

- **Mâu thuẫn nguồn.** SRC-SPEC D41/D43/§10.2 mô tả hai họ provider nhưng không chốt worker được nhận key nào, trong bao lâu, và CLI được phép gọi tool gì. §11.4 lại yêu cầu "Nội dung ngoài không được ... gọi tool, đọc secrets".
- **PC-ĐX của kế hoạch.** "Chốt secret access theo task; CLI không tool/file/network action ngoài inference được phép; nếu adapter không cô lập được thì không bật."
- **Quyết định tạm thời (PROVISIONAL).** Worker chỉ nhận credential của **đúng provider cho task được giao**, thời hạn ngắn. Adapter CLI/ACP phải chạy với tool, file và network bị tắt ngoài phần inference. Nếu không kiểm chứng được mức cô lập cho một provider thì adapter của provider đó **giữ trạng thái disabled**.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/capabilities.yaml`, `contracts/ai/providers.yaml`, `contracts/ops/secrets.md`, `acceptance/fixtures/ai/`.
- **Gate bị chặn.** G1 (PC01), G3 (PC06, PC08).
- **Thay đổi oracle.** REQ-AC16 (không có API key) chỉ pass nếu ít nhất một adapter CLI đã qua kiểm cô lập; nếu mọi adapter CLI bị disabled thì REQ-AC16 chuyển `BLOCKED`, không phải `FAIL`. REQ-AC17 thêm oracle: canary secret trong transcript và audit số lần gọi tool bằng 0.
- **Nếu Owner bác bỏ.** Nếu Owner yêu cầu bật adapter chưa kiểm cô lập thì I11 bị vi phạm; PC06 và PC08 phải ghi `ACCEPTED_RISK` có chữ ký của Owner, không được ghi là đã giải quyết.
- **Liên kết.** ADR-0010, I11, I14, REQ-D41, REQ-D43, REQ-D51, REQ-S10.2-02, REQ-S11.4-03, REQ-A5, REQ-AC16, REQ-AC17.

### B14 — Mật độ vector cho khối "hướng đang nổi"

- **Mâu thuẫn nguồn.** SRC-SPEC D53 đưa khối "hướng đang nổi" vào MVP nhưng trạng thái vẫn **ĐX**, và không có thuật toán, cửa sổ so sánh, ngưỡng hay cỡ mẫu tối thiểu. D54 yêu cầu nhãn "ứng viên để đọc sâu". A4 chưa được kiểm chứng.
- **PC-ĐX của kế hoạch.** "Định nghĩa phép đo và tập đánh giá. Thiếu dữ liệu → insufficient evidence, không tự gọi là 'hướng nổi'."
- **Quyết định tạm thời (PROVISIONAL).** PC04 định nghĩa thuật toán, cửa sổ so sánh, ngưỡng, cỡ mẫu tối thiểu, cold-start và tie-break. Dữ liệu không đủ thì kết quả là `insufficient_evidence`, tuyệt đối không gọi là "hướng đang nổi". Mọi tham số là PROVISIONAL cho tới khi đánh giá A4 có dữ liệu 3–4 kỳ.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/selection.md`, `contracts/schemas/report.schema.json`, `acceptance/scenarios.yaml`, `precode/gates.yaml`.
- **Gate bị chặn.** G3 (PC04), G4 (PC09).
- **Thay đổi oracle.** Không có AC nào bị sửa; bổ sung oracle mới: với fixture dưới cỡ mẫu tối thiểu, khối hướng nổi phải rỗng và mang nhãn `insufficient_evidence`.
- **Nếu Owner bác bỏ.** Nếu Owner muốn giữ khối hướng nổi mà không chấp nhận trạng thái `insufficient_evidence` thì D52/D54 không có oracle tái lập được; PC04 và PC09 ở lại BLOCKED cho phần này. Lưu ý D53 vẫn là mục P0 **còn ĐX** — xem §4.
- **Liên kết.** REQ-D53, REQ-D54, REQ-A4, REQ-S10.1-04, REQ-S10.3-04, REQ-S1.4-01, REQ-S1.4-02.

### B15 — Phạm vi của bất biến "0 trùng"

- **Mâu thuẫn nguồn.** SRC-SPEC §1.4 đặt chỉ số vận hành "0 trường hợp trùng" ở trạng thái **Đã xác nhận**; D17/D29/AC-07 giả định gộp được bằng DOI/arXiv ID. Nhưng metadata có thể thiếu hoặc mâu thuẫn (D33, §9.3 hàng arXiv/OpenAlex lỗi).
- **PC-ĐX của kế hoạch.** "Chốt phạm vi invariant 0 trùng theo canonical identity đã biết; xung đột đưa `identity_conflict` và giữ nguồn, không merge đoán."
- **Quyết định tạm thời (PROVISIONAL).** Bất biến "0 trùng" chỉ có nghĩa trên phạm vi **canonical identity đã biết** (DOI, arXiv ID, hoặc dạng chuẩn hóa đã định nghĩa). Xung đột đưa vào trạng thái quarantine `identity_conflict`, giữ mọi nguồn, không merge đoán. Trùng khoa học chưa xác định ID được **đo và báo cáo**, không tuyên bố đã giải bằng ràng buộc UNIQUE.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/data/identity.md`, `contracts/data/invariants.md`, `acceptance/fixtures/identity/`, `acceptance/traceability.csv`.
- **Gate bị chặn.** G2 (PC02), G4 (PC09).
- **Thay đổi oracle.** REQ-S1.4-03 đổi từ "0 trường hợp trùng" (tuyệt đối) sang "0 trường hợp trùng **trong phạm vi canonical identity đã biết**, cộng một số đếm riêng cho `identity_conflict` đang chờ xử lý". REQ-AC07 thêm case: hai alias mâu thuẫn không được tính là hai hướng chắc chắn.
- **Nếu Owner bác bỏ.** Giữ chữ "0 trường hợp trùng" tuyệt đối thì chỉ số này không đo được và PC09 không thể lập traceability cho nó.
- **Liên kết.** AMD-B15, ADR-0009, I03, I07, REQ-S1.4-03, REQ-D17, REQ-D29, REQ-AC07, REQ-AC09.

### B16 — Tách tuyên bố của tác giả và suy luận của AI

- **Mâu thuẫn nguồn.** SRC-SPEC D20 yêu cầu "điểm khác với cái đã có" cho mọi mục, kể cả khi chỉ có một post. AC-11 gộp mọi phát biểu về tính mới thành "suy luận". §10.3 lại yêu cầu tách ba loại phát biểu.
- **PC-ĐX của kế hoạch.** "Phân biệt tuyên bố tính mới của tác giả và suy luận AI; thiếu nguồn so sánh thì ghi thiếu, không bịa baseline."
- **Quyết định tạm thời (PROVISIONAL).** Đầu ra phân tích tách ba trường: `author_claim`, `source_verified`, `ai_inference`. Khi không có nguồn so sánh thì ghi `comparator: unknown`; tuyệt đối không bịa baseline.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/ai/grounding.md`, `contracts/schemas/analysis-result.schema.json`, `acceptance/fixtures/ai/`.
- **Gate bị chặn.** G3 (PC06).
- **Thay đổi oracle.** REQ-AC11 đổi từ "mọi phát biểu về tính mới được trình bày là suy luận" sang "mỗi phát biểu mang đúng một nhãn trong ba loại; phát biểu không có nguồn kiểm chứng được **phải** nằm ở `ai_inference`; thiếu comparator thì trường `comparator` bằng `unknown`".
- **Nếu Owner bác bỏ.** Giữ nguyên AC-11 thì tuyên bố của tác giả bị hạ cấp thành suy luận của AI, làm mất thông tin và mâu thuẫn với §10.3; PC06 ở lại BLOCKED cho phần grounding.
- **Liên kết.** AMD-B16, REQ-D20, REQ-AC11, REQ-S10.3-02, REQ-S10.3-06.

### B17 — Lúc enqueue summary và report partial

- **Mâu thuẫn nguồn.** SRC-SPEC §2.1 mục 6 yêu cầu summary "cho **mọi mục**"; §10.1 lại giới hạn "Mọi mục **vào báo cáo**". Vì tag đổi được nên report builder có thể chọn thêm target chưa có summary.
- **PC-ĐX của kế hoạch.** "Chốt lúc enqueue summary và cách report partial/pending; không báo completed nếu các mục còn thiếu bị mất khỏi hàng đợi."
- **Quyết định tạm thời (PROVISIONAL).** Task summary được enqueue cho các target **được report builder chọn tại thời điểm dựng báo cáo**. Report mang `quality: partial` kèm danh sách pending tường minh khi có mục thiếu summary; `complete` chỉ khi mọi mục được chọn đều đã có summary hoặc được đánh dấu pending một cách tường minh.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/selection.md`, `contracts/ai/tasks.yaml`, `contracts/state/report.yaml`, `contracts/schemas/report.schema.json`.
- **Gate bị chặn.** G3 (PC04, PC06).
- **Thay đổi oracle.** REQ-P0-06 được đọc lại theo §10.1 (mục vào báo cáo), không phải mọi post trong kho. REQ-AC10 thêm oracle âm: mục thiếu summary không bị ẩn khỏi report mà hiện ở danh sách pending.
- **Nếu Owner bác bỏ.** Nếu Owner muốn summary cho **mọi** mục trong kho thì chi phí AI tăng theo số bài chứ không theo số mục báo cáo, mâu thuẫn §10.4; phạm vi PC06 phải tính lại ngân sách trước khi tiếp tục.
- **Liên kết.** AMD-B17, REQ-P0-06, REQ-D19, REQ-S10.1-03, REQ-S10.4-03, REQ-AC10.

## 3. Amendment

Mỗi amendment ghi: **Trước** (trích nguyên văn nguồn), **Sau** (văn bản đề xuất), **Vì sao**, **Bảo đảm thay thế**, **Test/oracle chứng minh**, **REQ bị ảnh hưởng**. Tất cả ở trạng thái `PROVISIONAL`, `decision_owner: Owner`; chưa được áp vào `precode/source/spec-v0.2.md` (bản nguồn là bất biến).

### AMD-B01 — Mốc freeze tag

- **Trước** (SRC-SPEC §3.4, hàng `C03/D-tag`): "Mốc hiệu lực tag theo **thời điểm gửi**: bộ tag lúc tạo báo cáo quyết định nội dung".
- **Sau:** "Mốc hiệu lực tag theo **thời điểm publish báo cáo**: bộ tag đang hiệu lực tại transaction publish quyết định nội dung. Báo cáo lưu `tag_config_version` bất biến. Việc gửi (delivery) không bao giờ làm đổi nội dung đã publish."
- **Vì sao:** hàng gốc nêu hai mốc khác nhau trong cùng một câu; nếu lấy mốc "gửi" thì retry Telegram có thể rơi vào bộ tag khác và nội dung đã publish sẽ đổi.
- **Bảo đảm thay thế:** nội dung báo cáo bất biến sau publish (I05); mọi thay đổi tag sau publish chỉ ảnh hưởng kỳ sau.
- **Test/oracle:** đổi tag ngay trước CAS commit thì build bị abort/rebuild (`TAG_VERSION_STALE`); đổi tag sau publish trước delivery thì `report_item` và payload hash không đổi.
- **REQ ảnh hưởng:** REQ-CTAG, REQ-D23, REQ-D24, REQ-AC05, REQ-S8.1-03, REQ-S8.2-01, REQ-S8.2-02, REQ-S9.2-04.

### AMD-B02 — Mô hình trạng thái run

- **Trước** (SRC-SPEC §9.1): "Run | `queued` → `collecting` → `analyzing` → `reporting` → `done` · nhánh: `needs_user`, `stopped_limit`, `failed`, `failed_partial`"; và (SRC-SPEC AC-03): "run chuyển `stopped_limit`".
- **Sau:** run có bốn trường: `phase` ∈ {`collecting`, `enriching`, `analyzing`, `reporting`}; `status` ∈ {`queued`, `running`, `waiting_retry`, `needs_user`, `blocked`, `completed`, `failed`, `cancelled`}; `outcome` ∈ {`complete`, `partial`, `empty`, `failed`, `cancelled`}; `stop_reason` (ví dụ `limit_reached`, `captcha`, `session_expired`, `source_blocked`, `storage_unavailable`, `worker_lost`). AC-03 đọc lại: "run chuyển `status = completed`, `stop_reason = limit_reached`, checkpoint và tiến độ được lưu".
- **Bảng ánh xạ enum cũ sang mới:**

| Enum cũ (SRC-SPEC) | Mô hình mới |
| --- | --- |
| `queued` | `status = queued` |
| `collecting` | `status = running`, `phase = collecting` |
| `analyzing` | `status = running`, `phase = analyzing` |
| `reporting` | `status = running`, `phase = reporting` |
| `done` | `status = completed`, `outcome = complete` |
| `needs_user` | `status = needs_user` |
| `stopped_limit` | `status = completed`, `stop_reason = limit_reached`, `outcome ∈ {partial, complete}` |
| `failed` | `status = failed`, `outcome = failed` |
| `failed_partial` | `status = completed`, `outcome = partial` |
| `delivered` (§5.2) | **không thuộc run**; ánh xạ sang `delivery.status = sent` |
| `delivered_partial` (§5.2) | **không thuộc run**; ánh xạ sang `delivery.status ∈ {failed, unknown}` trong khi run giữ `outcome` của chính nó |
| *(không có)* | `status = blocked` (X chặn hoặc thiếu capability bắt buộc) |
| *(không có)* | `outcome = empty` (không có mục phù hợp, không có lỗi thiếu dữ liệu) |

- **Vì sao:** §5.2 đặt trạng thái gửi bên trong vòng đời run, mâu thuẫn trực tiếp với §9.1; `stopped_limit` trộn lẫn "đã dừng" với "kết quả ra sao".
- **Bảo đảm thay thế:** I09 (Telegram lỗi không làm run thất bại) và I13 (empty/incomplete/failed/unknown hiển thị riêng) trở nên kiểm chứng được.
- **Test/oracle:** transition lint trên `contracts/state/run.yaml`; ba run của REQ-AC15 cho ra ba bộ `(status, outcome, stop_reason)` khác nhau; không transition nào từ trạng thái terminal còn side effect.
- **REQ ảnh hưởng:** REQ-S5.2-01, REQ-S9.1-01, REQ-S9.1-02, REQ-AC03, REQ-AC15, REQ-D14, REQ-S8.3-01..03, REQ-S9.3-02, REQ-S9.3-07.

### AMD-B03 — Trạng thái delivery `unknown`

- **Trước** (SRC-SPEC AC-14): "Then app vẫn giữ báo cáo đầy đủ và **không có tin nào bị gửi hai lần**"; (SRC-SPEC §9.1): "Delivery | `pending` → `sent` · nhánh: `retrying`, `failed`".
- **Sau:** delivery có thêm trạng thái `unknown`. AC-14 đọc lại: "Then app vẫn giữ báo cáo đầy đủ, **không có lần gửi lặp tự động**, và mọi kết quả không xác định được hiện là `unknown` để Operator quyết định". Enum: `pending` → `sending` → `sent`; nhánh `retry_wait`, `failed`, `unknown`, `cancelled`.
- **Vì sao:** Telegram Bot API `sendMessage` không nhận idempotency key từ client (SRC-PLAN §3.1), nên ràng buộc UNIQUE trong SQLite không chứng minh exactly-once ở mạng ngoài.
- **Bảo đảm thay thế:** không retry tự động từ `unknown`; digest nhiều phần lưu `delivery_part` với receipt riêng; app luôn giữ báo cáo đầy đủ bất kể delivery.
- **Test/oracle:** mô phỏng Telegram nhận tin rồi cắt response → delivery vào `unknown`, số lần gọi mạng tiếp theo bằng 0; recipient bị revoke → `failed` mà report hash không đổi.
- **REQ ảnh hưởng:** REQ-AC14, REQ-D38, REQ-S9.1-03, REQ-S9.2-05, REQ-S9.3-06, REQ-S5.3-02, REQ-S5.4-02.

### AMD-B04 — Coverage record cho kỳ rỗng

- **Trước** (SRC-SPEC §3.5, D57): "Không gửi báo cáo rỗng; chỉ ghi vào trạng thái run".
- **Sau:** "Không gửi báo cáo rỗng. Kỳ rỗng vẫn ghi **một hàng coverage** trong sổ coverage authoritative và ghi vào trạng thái run; sổ pending item và sổ backfill độc lập với con trỏ kỳ."
- **Vì sao:** nếu kỳ rỗng không để lại dấu vết nào ngoài trạng thái run thì `coverage_from` của kỳ sau không có nguồn, tạo lỗ hổng hoặc chồng lấn, vi phạm D27 và I06.
- **Bảo đảm thay thế:** các cửa sổ coverage nối liền, nửa mở `[from, to)`; pending item không mất khi con trỏ tiến.
- **Test/oracle:** chuỗi kỳ có kỳ rỗng ở giữa → coverage ledger không hở, không chồng; publisher crash giữa chừng không tiêu thụ backfill.
- **REQ ảnh hưởng:** REQ-D57, REQ-D27, REQ-D28, REQ-AC08, REQ-S8.2-09, REQ-S10.4-03.

### AMD-B05 — Cam kết chống trùng khi resume

- **Trước** (SRC-SPEC §9.2 và AC-04): "Tiếp từ con trỏ, **không lấy lại bài đã có**".
- **Sau:** "Tiếp từ con trỏ khi con trỏ còn hiệu lực. Cam kết của hệ thống là **không ingest trùng** theo `x_post_id`; việc đọc lại một số trang được phép theo recovery policy khi con trỏ mất hiệu lực. Checkpoint chỉ chứa dữ liệu server đã ACK. Giới hạn bao phủ X được ghi trong metadata của run."
- **Vì sao:** cursor của feed động không chứng minh được là ổn định; hứa "không đọc lại" là một bảo đảm không kiểm chứng được, còn "không ingest trùng" thì kiểm chứng được bằng số hàng.
- **Bảo đảm thay thế:** I02 (receipt chỉ ACK sau commit; checkpoint không đi trước dữ liệu bền) và dedup theo `x_post_id`.
- **Test/oracle:** crash sau commit trước ACK rồi replay cùng `idempotency_key` → `COUNT(post)` và checkpoint không đổi; cursor bị vô hiệu → đọc lại nhưng không sinh hàng `post` mới.
- **REQ ảnh hưởng:** REQ-AC04, REQ-S9.2-01, REQ-S5.4-01, REQ-S9.3-01, REQ-S9.3-07, REQ-A1, REQ-A7.

### AMD-B07 — "Một lần" của D25

- **Trước** (SRC-SPEC §3.5, D25): "Phân tích và summary tạo **một lần** cho mỗi công trình rồi tái sử dụng".
- **Sau:** "Với mỗi analysis key — gồm canonical id của target, source version/fingerprint, task type, phiên bản prompt/schema và generation — hệ thống giữ **tối đa một kết quả hợp lệ**, rồi tái sử dụng. Đổi tag không đổi key. Phân tích lại theo D26 tạo generation mới; attempt lỗi hoặc không xác định không phải kết quả."
- **Vì sao:** nghĩa đen "một lần cho mỗi công trình" loại trừ chính D26 và loại trừ cả retry sau lỗi.
- **Bảo đảm thay thế:** I04 — retry không tạo hai kết quả hợp lệ cùng key; đổi tag không làm gọi AI lại.
- **Test/oracle:** bỏ rồi thêm lại tag → provider call counter delta bằng 0 cho cùng key và generation; hai worker cùng submit một key → chỉ một hàng hợp lệ, hàng thứ hai bị từ chối.
- **REQ ảnh hưởng:** REQ-D25, REQ-D26, REQ-AC06, REQ-S7.3-02, REQ-S9.2-03, REQ-S10.4-02, REQ-S8.1-04.

### AMD-B08 — Timezone

- **Trước** (SRC-SPEC §3.6, D56): "Timezone lấy theo máy chạy app".
- **Sau:** "Hệ thống lưu **một IANA timezone duy nhất** trong Settings, do Owner xác nhận (giá trị tạm: `Asia/Ho_Chi_Minh`). Mọi timestamp bền được lưu ở UTC theo RFC 3339 với độ chính xác mili giây, tie-break bằng ingest sequence. Timezone chỉ dùng để diễn giải lịch và để hiển thị."
- **Vì sao:** browser, server và máy collector là ba đồng hồ và ba múi giờ khác nhau; "máy chạy app" không xác định máy nào.
- **Bảo đảm thay thế:** lịch, chạy bù và ranh giới coverage tính được một cách xác định và tái lập.
- **Test/oracle:** fake-clock qua ranh giới DST → số run sinh ra đúng bảng đã chốt; hai bản ghi cùng mili giây → thứ tự theo ingest sequence là xác định.
- **REQ ảnh hưởng:** REQ-D56, REQ-D13, REQ-D15, REQ-D27, REQ-AC02, REQ-S8.2-08, REQ-S10.3-05, REQ-OQ06.

### AMD-B09 — Ngoại lệ liên kết Telegram

- **Trước** (SRC-SPEC §11.3): "Tin từ chat ID chưa liên kết bị **bỏ im lặng** — không trả lời gì, vì trả lời 'không có quyền' là tự xác nhận bot tồn tại".
- **Sau:** "Tin từ chat ID chưa liên kết bị bỏ im lặng, **trừ một ngoại lệ hẹp**: thông điệp khớp đúng định dạng mã liên kết được đối chiếu với các mã chưa hết hạn và chưa dùng. Mã hợp lệ thì thiết lập liên kết; mã sai, hết hạn hoặc đã dùng cũng bị bỏ im lặng, không trả lời lỗi."
- **Vì sao:** §5.1 bước 4 bắt buộc bot phải nhận được mã từ một chat chưa liên kết; nguyên văn §11.3 làm luồng thiết lập lần đầu không chạy được.
- **Bảo đảm thay thế:** bề mặt tấn công chỉ mở đúng cho chuỗi khớp định dạng mã; không rò rỉ sự tồn tại của bot cho mọi thông điệp khác.
- **Test/oracle:** fake update từ chat lạ với nội dung bất kỳ → outbound call count bằng 0, không mutation; cùng mã gửi hai lần → lần hai không tạo liên kết và không phản hồi.
- **REQ ảnh hưởng:** REQ-S11.3-02, REQ-D35, REQ-S5.1-04, REQ-S11.2-04, REQ-AC18.

### AMD-B10 — Resume và giới hạn lệnh Telegram

- **Trước** (SRC-SPEC §5.4 bước 4): "Bấm 'tiếp tục' trong app hoặc gửi lệnh trạng thái/chạy ngay".
- **Sau:** "Bấm 'tiếp tục' trong app. Lệnh `status` là chỉ đọc và không làm run rời khỏi `needs_user`; lệnh `run-now` không ghi đè một run đang `needs_user`. Không thêm lệnh Telegram thứ tư; hành động hủy liên kết cũng nằm trong app."
- **Vì sao:** câu gốc gợi ý hai lệnh Telegram có thể resume một run đang chờ can thiệp, mâu thuẫn với §5.4 bước 5 và với §9; đồng thời §11.3 giới hạn đúng 3 lệnh.
- **Bảo đảm thay thế:** resume chỉ xảy ra sau khi phiên được kiểm là không còn challenge, và luôn cấp lease mới (I10).
- **Test/oracle:** gửi `status` và `run-now` khi run đang `needs_user` → không hàng nào đổi, không lease mới; chỉ hành động resume trong app mới đưa run về `queued`.
- **REQ ảnh hưởng:** REQ-S5.4-04, REQ-D36, REQ-D37, REQ-S11.3-03, REQ-S11.3-04, REQ-AC04, REQ-S4-06.

### AMD-B11 — Backup và restore

- **Trước** (SRC-SPEC §3.6 D58 và §7.3): "Backup là copy file SQLite" / "Backup: copy file SQLite. Restore: đặt file về chỗ cũ".
- **Sau:** "Backup tạo snapshot nhất quán bằng SQLite Online Backup API hoặc `VACUUM INTO` (an toàn với WAL), kèm manifest ghi hash file DB, phiên bản schema, artifact và cấu hình embedding. Restore thực hiện vào môi trường sạch với khóa side effect: dispatcher và worker claim bị dừng, outbox cũ không replay, `first_announced` không bị reset trước khi kiểm tra toàn vẹn. Retention: giữ vô thời hạn."
- **Vì sao:** WAL là một phần trạng thái bền của DB; copy riêng file DB có thể mất transaction đã commit (SRC-PLAN §3.1).
- **Bảo đảm thay thế:** I15 — restore không tự gửi lại outbox cũ, không chạy lại job side effect, không reset `first_announced` mà không kiểm tra.
- **Test/oracle:** restore vào môi trường rỗng → trước khi verify không có side effect nào; count và hash của Saved, report và ledger khớp manifest.
- **REQ ảnh hưởng:** REQ-D58, REQ-S7.3-04, REQ-S6.4-01, REQ-AC12, REQ-S9.3-08, REQ-S13-09.

### AMD-B12 — Xóa cạnh collector → analysis worker

- **Trước** (SRC-SPEC §6.2, sơ đồ đường dữ liệu): dòng `COL --> AW` — "Collector - máy cá nhân" nối thẳng tới "Analysis worker - máy cá nhân".
- **Sau:** xóa cạnh `COL --> AW`. Analysis worker nhận **task từ server sau ingest commit** (`API --> AW` hoặc worker pull qua Analysis API). Collector chỉ có một đường ra duy nhất là Backend API.
- **Vì sao:** cạnh đó cho phép analysis chạy trên dữ liệu **chưa commit**, mâu thuẫn D08 ("collector không ghi trực tiếp, đẩy qua API có xác thực") và phá I02.
- **Bảo đảm thay thế:** mọi input của analysis đều đã qua commit và có canonical id; kết quả phân tích luôn gắn được vào dữ liệu authoritative.
- **Test/oracle:** negative case — collector cố gửi payload cho analysis worker bị từ chối bởi capability registry (default deny); import/dependency rule chặn edge này khi cùng tiến trình.
- **REQ ảnh hưởng:** REQ-S6.2-01, REQ-D08, REQ-D42, REQ-S6.1-03, REQ-AC16.

### AMD-B15 — Phạm vi chỉ số "0 trùng"

- **Trước** (SRC-SPEC §1.4): "| Vận hành | Công trình trùng không thành nhiều phát hiện | 0 trường hợp trùng | Đã xác nhận |".
- **Sau:** "| Vận hành | Công trình trùng không thành nhiều phát hiện | 0 trường hợp trùng **trong phạm vi canonical identity đã biết** (DOI, arXiv ID hoặc dạng chuẩn hóa đã định nghĩa); các trường hợp `identity_conflict` được đếm và báo cáo riêng | Đã xác nhận, phạm vi được thu hẹp bởi AMD-B15 |".
- **Vì sao:** metadata có thể thiếu hoặc mâu thuẫn; một ràng buộc UNIQUE không giải được trùng lặp khoa học chưa có ID.
- **Bảo đảm thay thế:** I03 — alias conflict không bị merge đoán, nguồn được giữ nguyên và có audit trail.
- **Test/oracle:** fixture DOI/arXiv mapping mâu thuẫn → target vào quarantine, không merge; report không tính hai alias nghi trùng là hai hướng chắc chắn.
- **REQ ảnh hưởng:** REQ-S1.4-03, REQ-D17, REQ-D29, REQ-AC07, REQ-AC09, REQ-S9.3-05.

### AMD-B16 — Ba loại phát biểu trong summary

- **Trước** (SRC-SPEC AC-11): "Then nhãn ghi 'chỉ có post', và **mọi phát biểu về tính mới được trình bày là suy luận**, không phải kết luận".
- **Sau:** "Then nhãn ghi 'chỉ có post'; mỗi phát biểu mang đúng một nhãn trong ba loại `author_claim`, `source_verified`, `ai_inference`; phát biểu về tính mới không có nguồn kiểm chứng được **phải** nằm ở `ai_inference`; khi không có nguồn so sánh thì trường `comparator` bằng `unknown` và không được bịa baseline."
- **Vì sao:** AC-11 nguyên văn gộp cả tuyên bố của tác giả vào "suy luận", làm mất thông tin và mâu thuẫn §10.3.
- **Bảo đảm thay thế:** grounding kiểm được bằng schema cộng kiểm tra citation, thay vì bằng cách hạ cấp mọi phát biểu.
- **Test/oracle:** fixture chỉ có post → mọi phát biểu tính mới nằm ở `ai_inference`, `comparator = unknown`; fixture có abstract nêu đóng góp → phát biểu đó ở `author_claim` kèm citation target.
- **REQ ảnh hưởng:** REQ-AC11, REQ-D20, REQ-S10.3-02, REQ-S10.3-01, REQ-S10.3-06.

### AMD-B17 — Phạm vi và thời điểm enqueue summary

- **Trước** (SRC-SPEC §2.1 mục 6): "Summary theo hình dạng 'nội dung + điểm khác + hạn chế' **cho mọi mục**".
- **Sau:** "Summary theo hình dạng 'nội dung + điểm khác + hạn chế' cho **mọi mục được report builder chọn tại thời điểm dựng báo cáo**. Báo cáo mang `quality: partial` kèm danh sách pending tường minh khi còn mục thiếu summary; `complete` chỉ khi mọi mục được chọn đều đã có summary hoặc được đánh dấu pending tường minh."
- **Vì sao:** §2.1 và §10.1 nêu hai phạm vi khác nhau ("mọi mục" và "mọi mục vào báo cáo"); phạm vi rộng làm chi phí AI tỉ lệ với số bài thu được, mâu thuẫn §10.4.
- **Bảo đảm thay thế:** không có mục nào bị mất khỏi hàng đợi mà báo cáo vẫn ghi `complete`.
- **Test/oracle:** late analysis → mục xuất hiện ở kỳ sau với nhãn phát hiện muộn; report có mục thiếu summary → `quality = partial` và pending list không rỗng.
- **REQ ảnh hưởng:** REQ-P0-06, REQ-D19, REQ-S10.1-03, REQ-S10.4-03, REQ-AC10, REQ-S9.3-03.

### Blocker không cần amendment văn bản

B06, B13 và B14 **không** sửa câu chữ nào của đặc tả: chúng bổ sung định nghĩa còn thiếu (identity/alias/target; chính sách secret và cô lập; phép đo mật độ vector). Chúng vẫn ở trạng thái `PROVISIONAL` và vẫn cần Owner phê chuẩn vì có thể làm một adapter bị tắt (B13) hoặc làm khối "hướng đang nổi" trả về `insufficient_evidence` (B14).

## 4. Các mục P0 hiện còn ĐX — **không được tự promote**

| REQ | Nội dung | Trạng thái nguồn | Vì sao vẫn ở P0 | Hệ quả nếu không được xác nhận |
| --- | --- | --- | --- | --- |
| REQ-D09 | Chrome profile riêng của dự án | ĐX | Cần cho REQ-P0-03 và bước §5.1-05 | Chặn M0; REQ-OQ01 ghi rõ "Chặn M0" |
| REQ-D53 | Khối "hướng đang nổi" tính từ mật độ vector, vào MVP | ĐX | Là nửa sau của REQ-P0-07 | Khối này rơi khỏi MVP; REQ-D52 mất phương tiện chính |
| REQ-D08 | Collector đẩy dữ liệu qua API có xác thực | ĐX | Nền tảng của REQ-P0-12 và I02 | PC01 không đóng được ranh giới |
| REQ-D42 | Bước LLM chạy cùng máy collector | ĐX | Nền tảng của REQ-P0-11 | PC01/PC06 không đóng được topology |
| REQ-D50 | Model embedding chạy ở server | ĐX | Nền tảng của REQ-P0-05 | PC01/PC04 không đóng được nơi chạy |
| REQ-D11 | Job xếp hàng ở server, collector kéo việc | ĐX | Nền tảng của REQ-P0-10 | PC03 không đóng được mô hình claim |
| REQ-D22 | AI gắn nhãn mở | ĐX | Nền tảng của REQ-P0-05 | Đổi tag sẽ phải gọi AI lại, phá REQ-AC06 |
| REQ-D33 | Post chỉ có ảnh chụp thành mục "chỉ có post" | ĐX | Bổ trợ REQ-P0-04 | Post-only không có model rõ |
| REQ-D21 | Nhãn mức độ đọc trên mỗi summary | ĐX | Bổ trợ REQ-P0-06 | Mất evidence level, phá REQ-AC11 |
| REQ-D26 | Phân tích lại khi bấm tay hoặc có phiên bản mới | ĐX | Bổ trợ REQ-P0-06 | Không có đường reanalysis hợp lệ |
| REQ-D37 | Có lệnh hủy liên kết | ĐX | Bổ trợ REQ-P0-09 | Xem F-PC00-01 |
| REQ-D38 | Nút Save Telegram và UNIQUE chống trùng | ĐX | Nền tảng của REQ-P0-08 | REQ-AC13 mất cơ chế |
| REQ-D43 | Giao ước adapter và bước bóc JSON của CLI | ĐX | Nền tảng của REQ-P0-11 | PC06 không có capability matrix |
| REQ-D44 | Usage chấp nhận "không rõ" | ĐX | Bổ trợ REQ-P0-11 | I14 không có chỗ dựa |
| REQ-D15 | Gộp đợt quá hạn thành một | ĐX | Nền tảng của REQ-P0-10 | REQ-AC02 mất oracle |
| REQ-D16 | Chạy bù không gửi bù báo cáo cũ | ĐX | Bổ trợ REQ-P0-10 | Rủi ro spam digest cũ |
| REQ-D12 | `last_run` chỉ để xem | ĐX | Bổ trợ REQ-P0-12 | Rủi ro dùng `last_run` làm mốc lọc |
| REQ-D18 | Idea cluster hoãn sau MVP | ĐX | Là quyết định hoãn, không phải hạng mục P0 | Nếu đảo lại thì phạm vi MVP tăng |

**Tuyên bố:** PC00 **không** promote bất kỳ mục nào ở trên lên `XN`. Trạng thái trong `precode/requirements.csv` giữ đúng như đặc tả. Việc promote chỉ xảy ra khi Owner trả lời `precode/owner-decision-request.md`.

## 5. Câu hỏi còn mở và giá trị mặc định tạm

| REQ | Câu hỏi | Giá trị PROVISIONAL của phiên này | Ai phải chốt | Chặn gì |
| --- | --- | --- | --- | --- |
| REQ-OQ01 | Chrome profile riêng? | Có, profile riêng của dự án | Owner | M0 |
| REQ-OQ02 | Stack? | Option A — Python toàn bộ | Owner | M1, PC10 |
| REQ-OQ03 | Provider và model cụ thể? | **Không có mặc định** — `OWNER_DECISION_REQUIRED` | Owner | M3, việc bật provider |
| REQ-OQ04 | N ngày backfill? | 7 ngày | Owner | — |
| REQ-OQ05 | Giới hạn mỗi đợt? | 200 post hoặc 30 phút, cái nào tới trước | Owner (sau M0) | — |
| REQ-OQ06 | Lịch cụ thể? | 08:00 và 20:00 theo timezone của Owner | Owner | — |
| REQ-OQ07 | Giờ yên lặng Telegram? | Không có ở MVP | Owner | — |
| REQ-OQ08 | Ngưỡng tương đồng? | **Không đặt số** — phải đo (REQ-A2) | Dữ liệu, sau M3 | — |
| REQ-OQ09 | Model embedding cụ thể? | **Không đặt tên** — ràng buộc: local, đa ngôn ngữ | Kỹ thuật, sau A3 | — |
| REQ-OQ10 | Export Saved ở MVP? | Hoãn sang P1 | Owner | — |
| — | Timezone của Owner | `Asia/Ho_Chi_Minh` | Owner | Fixture lịch |

Lý do cho từng con số PROVISIONAL: N = 7 lấy nguyên văn đề xuất của SRC-SPEC §13.1; lịch 08:00 và 20:00 lấy từ ví dụ §8.2 hàng 8 và AC-01/AC-02; giới hạn 200 post hoặc 30 phút là ước lượng tạm để hợp đồng không còn "TBD" — SRC-SPEC §13.1 nói rõ con số thật phải đến sau M0; giờ yên lặng "không có" là mặc định ít bất ngờ nhất vì đặc tả không mô tả cơ chế hoãn gửi.

## 6. Phát hiện mới của PC00 (không nằm trong B01–B17)

| ID | Phát hiện | Nguồn | Xử lý |
| --- | --- | --- | --- |
| F-PC00-01 | Số lệnh Telegram tự mâu thuẫn: D36 và §11.3 nói **đúng 3 lệnh** (Save, chạy ngay, xem trạng thái), nhưng D37 yêu cầu "có lệnh hủy liên kết" — tức lệnh thứ tư | SRC-SPEC:D36, SRC-SPEC:D37, SRC-SPEC§11.3 | Xếp vào phạm vi B10. PROVISIONAL: hủy liên kết là hành động trong app; Telegram giữ đúng 3 lệnh. Đưa vào owner-decision-request §B10 |
| F-PC00-02 | Màn hình Saved liệt kê hành động **export** ở SRC-SPEC §4, trong khi REQ-OQ10 vẫn hỏi "có cần export Saved ở MVP hay hoãn" | SRC-SPEC§4 (hàng Saved), SRC-SPEC§13.1 hàng 10 | PROVISIONAL: hoãn export sang P1, nút export không có ở MVP. Cần Owner chốt; ảnh hưởng REQ-S4-05 |
| F-PC00-03 | Phạm vi summary mâu thuẫn giữa §2.1 mục 6 ("cho mọi mục") và §10.1 ("Mọi mục vào báo cáo") | SRC-SPEC§2.1#row-06, SRC-SPEC§10.1#row-03 | Đã nằm trong B17; AMD-B17 chốt theo §10.1 |
| F-PC00-04 | SRC-SPEC §5.2 dùng `delivered`/`delivered_partial` như trạng thái của **run**, mâu thuẫn §9.1 | SRC-SPEC§5.2, SRC-SPEC§9.1 | Đã nằm trong B02; bảng ánh xạ trong AMD-B02 xử lý |
| F-PC00-05 | `saved_item` khóa `UNIQUE(owner, work/post)` là ký hiệu mơ hồ: hai cột nullable không cho ràng buộc duy nhất đúng với target post-only | SRC-SPEC§7.1 (hàng `saved_item`) | Đã nằm trong B06; PC02 phải dùng target tagged union |
| F-PC00-06 | REQ-D34 và REQ-A6 là cùng một yêu cầu được ghi hai lần ở hai chỗ (decision log và bảng giả định) | SRC-SPEC:D34, SRC-SPEC:A6 | Giữ cả hai dòng trong registry để không mất nguồn; ghi chú chéo trong cột notes. Không phải mâu thuẫn |

`F-PC00-01` và `F-PC00-02` là hai điểm PC00 **tự quyết theo khuyến nghị của kế hoạch** vì không có mục nào của §5 baseline phủ. Cả hai được ghi vào `unresolved refs` của HANDOFF và vào `precode/owner-decision-request.md`.

## 7. Chỉ mục ADR

Xem `precode/adr/README.md`. Tương ứng: ADR-0001 (B12), ADR-0002 (B02), ADR-0003 (B03), ADR-0004 (B01), ADR-0005 (B11), ADR-0006 (stack), ADR-0007 (B08), ADR-0008 (B07), ADR-0009 (B06/B15), ADR-0010 (B13).

## 8. Quyết định tạm thời phát sinh sau audit A1-R1

Mục này ghi các quyết định **không** thuộc B01–B17, phát sinh từ AUDIT_REPORT `PKT-A1-R1` và các ruling của
Coordinator ngày 2026-09-06T18:00Z. Chúng theo cùng luật với §2: `PROVISIONAL`, `decision_owner: Owner`,
không mục nào được ghi `CLOSED`.

### PROV-PC00-01 — Ba thao tác xóa của REQ-S7.3-05 và phạm vi loại trừ của `data.purge_all`

- **Nguồn yêu cầu.** SRC-SPEC §7.3: *"Bỏ lưu ≠ xóa dữ liệu gốc ≠ xóa toàn bộ dữ liệu. Ba thao tác riêng,
  thao tác thứ ba đòi xác nhận gõ tay."* — `REQ-S7.3-05`, trạng thái **XN**.
- **Điều audit phát hiện (`F-A1R1-04`, MAJOR).** Bộ 82 operation của `contracts/ports.yaml` chỉ có
  `save.remove`. Thao tác **thứ hai** ("xóa dữ liệu gốc") vắng mặt khỏi cả inventory lẫn mọi danh sách
  unresolved — bị bỏ sót im lặng; thao tác **thứ ba** chỉ được `PROV-PC01-03` nêu. Ngoài ra
  `save.remove.requirement_refs` trỏ nhầm sang `REQ-S7.3-01`.
- **Ruling R-04 của Coordinator.** PC01 thêm hai owner-only HTTP mutation:
  - `data.delete_target` — xóa dữ liệu gốc của **một** target (post/work); **giữ** `saved_snapshot` theo D55
    và giữ các ledger; cần cờ xác nhận tường minh; có transaction và error map; scenario `SC32`.
  - `data.purge_all` — xóa **toàn bộ** dữ liệu; cần trường xác nhận **gõ tay** khớp một challenge do server
    phát; chỉ chạy khi `storage.health = maintenance`; thu hồi mọi lease.
  - `save.remove.requirement_refs` sửa thành `REQ-S7.3-05`; `PROV-PC01-03` viết lại để nêu **cả hai**
    operation, không chỉ operation thứ ba.
- **Quyết định tạm thời (PROVISIONAL).** Chấp nhận cả hai operation ở mức khai báo hợp đồng cho PC01. PC00
  ghi nhận và trỏ `REQ-S7.3-05` sang chúng; PC00 **không** tự định nghĩa operation (không thuộc write target).
- **Phần vẫn chặn — `OWNER_DECISION_REQUIRED`.** Cụm *"toàn bộ dữ liệu"* của `data.purge_all` **không có
  mặc định an toàn**: không có câu nào trong SRC-SPEC nói settings, secret, liên kết Telegram, cấu hình
  provider hay chính tài khoản đăng nhập có bị xóa hay không. Đoán sai theo hướng rộng là mất khả năng đăng
  nhập lại; đoán sai theo hướng hẹp là để lại dữ liệu người dùng tưởng đã xóa. Vì vậy phạm vi loại trừ giữ
  `OWNER_DECISION_REQUIRED` cho tới khi Owner trả lời — xem `precode/owner-decision-request.md`, mục
  "Phạm vi của `data.purge_all`".
- **Hợp đồng/file bị ảnh hưởng.** `contracts/ports.yaml`, `contracts/modules.yaml` (`PROV-PC01-03`),
  `contracts/state/storage.yaml` (guard `maintenance`), `acceptance/scenarios.yaml` (`SC32`),
  `precode/requirements.csv` (`REQ-S7.3-05`).
- **Gate bị chặn.** G1 cho phần inventory (PC01); G3 cho phần semantics của `data.purge_all` (PC08 khóa
  maintenance và thu hồi lease).
- **Thay đổi oracle.** `REQ-S7.3-05` chuyển từ "có ba thao tác riêng" (kiểm bằng đọc) sang một kiểm tra truy
  vết requirement → operation: đúng ba operation trỏ về `REQ-S7.3-05`, mỗi cái có auth scope, ngữ nghĩa xác
  nhận và error map riêng. Thêm oracle âm: sau `data.delete_target`, số hàng `saved_snapshot` của target đó
  **không đổi** (D55), và `first_announced` **không** bị reset (I07).
- **Nếu Owner bác bỏ.** Nếu Owner không muốn có operation xóa nào ở MVP thì `REQ-S7.3-05` phải được ghi là
  **blocked scope tường minh** cho cả hai thao tác — không được để im lặng như tình trạng epoch 1 — và phần
  tương ứng của §7.3 rơi khỏi phạm vi MVP một cách có ghi chép.
- **Liên kết.** `REQ-S7.3-05`, `REQ-D55`, `REQ-D07`, I07, I08, `SC32`, `PROV-PC01-03`, `F-A1R1-04`, ruling R-04.

### Ghi chú về hai ngoại lệ header đã khai báo

`F-A1R1-05` (ADR thiếu 8 trường header của baseline §3) và `F-A1R1-06` (`requirements_csv_contract_header`
thiếu `requirement_refs`) là **defect tài liệu**, không phải quyết định sản phẩm, nên không có mục
`PROV-…` riêng. Chúng được xử lý tại chỗ: ngoại lệ ADR khai báo trong `precode/adr/README.md` (ruling R-05,
baseline §3 đã được Coordinator sửa tương ứng), và `requirement_refs` đã được thêm vào
`precode/baseline.json`. Chi tiết trước/sau nằm trong addendum `PKT-PC00-FIX1` của
`evidence/handoffs/PC00-handoff.md`.

### PROV-PC00-02 — Mã lỗi `CSRF_REJECTED`

- **Nguồn xung đột.** `contracts/http/openapi.yaml` (PC05) ánh xạ "thiếu hoặc sai CSRF token" sang **403 `FORBIDDEN_EDGE`**, nhưng `contracts/errors.yaml` (PC03) định nghĩa `FORBIDDEN_EDGE` là *"cạnh caller→callee không có trong `modules.yaml`"*. Một request thiếu CSRF đi qua **đúng** cạnh cho phép; cái sai là bằng chứng về ý định của người dùng, không phải topology. PC08 nêu ở `CR-PC08-03` và tạm theo PC05 để không tạo mâu thuẫn thứ hai.
- **Ruling FIX3 của Coordinator.** Đăng ký một mã riêng: `CSRF_REJECTED` — HTTP 403, `scope: request`, `retry_class: none`, **không đổi state**; áp dụng khi một owner-session mutation thiếu hoặc mang CSRF token không hợp lệ. `FORBIDDEN_EDGE` giữ nguyên nghĩa "cạnh không có trong registry"; `UNAUTHORIZED` giữ nguyên nghĩa "lớp principal không được phép / danh tính chưa thiết lập" — nên `CR-PC08-04` được chấp nhận đúng như PC08 lập luận: collector token gọi `save.create` là **`UNAUTHORIZED` 401**, không phải `FORBIDDEN_EDGE`.
- **Trạng thái.** `PROVISIONAL`, `decision_owner: Coordinator (delegated under AUTH-OWNER-20260906-01)` — đây là chi tiết kỹ thuật không đảo hành vi nào Owner đã chọn, cùng loại với ADR-0008. Owner vẫn có quyền đảo.
- **File bị ảnh hưởng.** `contracts/errors.yaml` (PC03 FIX1 đăng ký), `contracts/http/openapi.yaml` (PC05 ánh xạ), `acceptance/fixtures/recovery/` (fixture `SC40`).
- **Thay đổi oracle.** Oracle của `SC40` chuyển từ "trả 403 `FORBIDDEN_EDGE`" sang "trả 403 `CSRF_REJECTED` **và** không hàng nào đổi". Oracle của `FORBIDDEN_EDGE` thu hẹp về đúng các ca `NC-*` của `modules.yaml`. Thêm oracle âm: một request đúng cạnh, đúng principal, thiếu CSRF **không** được sinh mã nói về cạnh.
- **Nếu Owner/Coordinator bác bỏ.** Phải sửa **đồng thời** định nghĩa `FORBIDDEN_EDGE` trong `errors.yaml`, các ca `NC-01/NC-02` của `modules.yaml` và mô tả `collectorToken` trong `openapi.yaml` — không được sửa mỗi fixture, vì đó chính là lớp lỗi "một hành vi, nhiều mô tả" mà `F-A1R1-01` đã phạt.
- **Liên kết.** `CR-PC08-03`, `CR-PC08-04`, `CR-PC03-04`, `REQ-S11.1-01`, `REQ-D05`, `SC40`, `SC41`, I01, I11.

### PROV-PC00-03 — Hình dạng hai pha của `data.purge_all` và `SC44`

- **Bối cảnh.** `PROV-PC00-01` đã ghi nhận sự tồn tại của hai operation xóa; điểm còn lại là **cách** thực hiện "xác nhận gõ tay" của SRC-SPEC §7.3 mà không sinh ra operation thứ tư.
- **Quyết định tạm thời (PROVISIONAL).** `contracts/ports.yaml` khai `data.purge_all` là **một** operation với hai `phase`: (1) `request_challenge` — server sinh và lưu một `purge_challenge` có hạn, trả về cụm từ người dùng phải gõ lại, **không xóa gì**; (2) `execute` — đòi `purge_challenge_id` cộng `confirmation_phrase` khớp **chính xác**; sai hoặc hết hạn thì `VALIDATION_ERROR`, challenge bị hủy và phải xin lại. Idempotency key là `purge_challenge_id`, dùng đúng một lần; gọi lại sau khi đã thực thi trả bản ghi đã commit chứ **không** xóa lần hai. Chỉ chạy khi `storage.health = maintenance`; thu hồi mọi lease. `owner_module: MOD-data-admin-service`, `caller_modules: [MOD-web-ui]`, `auth_scope: owner_session`.
- **Scenario.** `SC44` — xác nhận hai pha, điều kiện tiên quyết `maintenance`, thu hồi lease, cộng các ca âm (cụm từ sai, challenge hết hạn, gọi lại phase 2 lần thứ hai, gọi khi không ở `maintenance`). Đã đăng ký anchor `SRC-PLAN:SC44` trong `precode/baseline.json`.
- **Hai hệ quả vận hành PC08 nêu, Owner phải biết trước khi trả lời `PROV-PC00-01`:**
  1. **Nếu purge xóa credential đăng nhập** thì phải có đường đặt lại tại chỗ, nếu không chủ nhà **tự khóa mình ra ngoài app** — D05 cấm trang signup và cấm quên-mật-khẩu tự động, nên không có đường vòng nào sẵn có.
  2. **Dữ liệu đã purge vẫn còn trong các artifact backup** cho tới khi chính những bản backup đó bị xóa. Muốn "xóa hẳn" phải xóa cả backup — một thao tác riêng (`contracts/ops/backup-restore.md` §8). Ai hiểu "xóa toàn bộ" là "không còn ở đâu nữa" sẽ hiểu sai.
- **Phần vẫn chặn.** Danh sách **loại trừ** vẫn `OWNER_DECISION_REQUIRED` (xem `PROV-PC00-01`); PC08 liệt kê ứng viên loại trừ là settings, secrets, credential đăng nhập, `telegram_link`, `schema_migration`.
- **Liên kết.** `REQ-S7.3-05`, `REQ-D05`, `REQ-D55`, `PROV-PC00-01`, `PROV-PC01-03`, `CR-PC08-01`, `SC44`, I08, I15.

### PROV-PC00-04 — `run.resume` được mở rộng cho trạng thái `blocked`

- **Nguồn xung đột.** `contracts/state/run.yaml` (PC03) có trạng thái `blocked` (X chặn hoặc thiếu capability bắt buộc, theo AMD-B02) nhưng `contracts/ports.yaml` chỉ khai `run.resume` cho `needs_user` (B10). Hệ quả: đường thoát duy nhất khỏi `blocked` là `run.cancel` — an toàn nhưng buộc Owner hủy run và tạo run mới, làm mất ngữ cảnh (`CR-PC03-02`).
- **Ruling FIX3.** Mở rộng guard của `run.resume`: cho phép từ `needs_user` (sau khi challenge đã được xử lý) **và** từ `blocked` (Owner tuyên bố điều kiện chặn đã hết, **bắt buộc** kèm `unblock_reason`); **không** từ trạng thái nào khác. PC01 ghi vào `ports.yaml`; PC03 FIX1 thêm hàng transition `blocked → queued`.
- **Trạng thái.** `PROVISIONAL`, `decision_owner: Owner` — vì nó chạm một ràng buộc Owner đã đọc: SRC-SPEC §5.4 bước 5 ("nếu hạn chế vẫn còn thì run **không** tự tiếp tục — dừng và báo").
- **Ranh giới phải giữ.** Quyết định này **không** tạo bất kỳ đường tự động nào: chỉ Owner, chỉ qua app, chỉ với `unblock_reason` ghi lại được, và luôn cấp lease mới. Không có lệnh Telegram tương ứng (B10, AMD-B10). Không có retry tự động từ `blocked` (`REQ-S9.3-02`, I10).
- **Thay đổi oracle.** `REQ-S5.4-05` giữ nguyên nghĩa "không tự tiếp tục" nhưng oracle thêm một ca dương tính: sau khi Owner gọi `run.resume` với `unblock_reason`, run về `queued` và một lease **mới** được cấp khi claim. Ca âm: mọi actor khác, và mọi đường không có `unblock_reason`, đều bị từ chối; `status` và `run-now` từ Telegram vẫn không đưa run rời `blocked` (AMD-B10).
- **Nếu Owner bác bỏ.** Giữ nguyên thì `blocked` chỉ thoát được bằng `run.cancel`; ghi rõ điều đó trong UI để Owner không chờ một nút "tiếp tục" không tồn tại.
- **Liên kết.** `CR-PC03-02`, `REQ-S5.4-04`, `REQ-S5.4-05`, `REQ-S9.3-02`, `REQ-AC04`, AMD-B02, AMD-B10, I10.

### 8.5 Đăng ký quyết định PROVISIONAL của các gói khác

PC00 là nơi tập trung quyết định; các gói dưới đây tự đưa quyết định trong phạm vi của mình, PC00 **ghi nhận** để chúng không rơi khỏi tầm nhìn của Owner và của PC09. PC00 **không** thẩm định lại nội dung kỹ thuật — chủ sở hữu vẫn là gói gốc.

| ID | Gói | Quyết định | Trạng thái | Đưa lên Owner ở mục |
| --- | --- | --- | --- | --- |
| `PROV-PC03-01` | PC03 | Quy tắc DST: giờ không tồn tại → chạy tại instant đầu tiên ≥ giờ danh nghĩa; giờ lặp → lấy lần xuất hiện đầu | PROVISIONAL | Timezone |
| `PROV-PC03-02` | PC03 | `run_now_active_run_policy = coalesce` (bấm lặp trả run đang có, không tạo run mới) | PROVISIONAL | — (kỹ thuật) |
| `PROV-PC03-03` | PC03 | Tách ngân sách `provider_unavailable_waits` khỏi `analysis_attempts_per_item` | PROVISIONAL | — (kỹ thuật) |
| `PROV-PC03-04` | PC03 | `analysis_unknown_attempt_auto_rerun = 1` — **khác** `delivery.unknown` (không bao giờ tự chạy lại). PC03 tự ghi rằng đây là chỗ họ diễn giải khác câu "never retry unknown outcome" của packet và **đề nghị Auditor soi kỹ** | PROVISIONAL | Tham số AI |
| `PROV-PC03-05` | PC03 | 41 giá trị lease/backoff/window trong `retry-policy.yaml`; `lease_ttl_collector = 120 s` neo vào `heartbeat 30 s` + `online_threshold 90 s` của PC01 | PROVISIONAL | Tham số vận hành |
| `PROV-PC03-06` | PC03 | `storage.maintenance` là trạng thái Operator mở có chủ đích; `T-ST-08` giữ nợ đối soát khi sự cố ổ đĩa xen vào sau restore | PROVISIONAL | — (kỹ thuật, bảo vệ I15) |
| `PROV-PC04-01` | PC04 | First-announcement sau merge = **sớm nhất**, có audit | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC04-02` | PC04 | Backfill khóa theo **chữ tag đã chuẩn hóa** (`subscription_identity_hash`); re-add **không** cấp lại quyền backfill | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC04-03` | PC04 | Backfill tiêu thụ khi publish commit **và** phần nới có ≥ 1 ứng viên; phần nới rỗng thì entitlement ở lại | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC04-04` | PC04 | arXiv phiên bản mới = `prior_reference` (`reference_reason = 'new_work_version'`), **không** phải phát hiện mới | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC04-05` | PC04 | Target chỉ-có-post: "đã công bố" suy từ `report_item` của report đã publish | PROVISIONAL | — (kỹ thuật) |
| `PROV-PC04-06` | PC04 | Ngưỡng similarity `0.8000` mang nhãn `PROVISIONAL_BOOTSTRAP` + `threshold_calibration_state = 'uncalibrated'`; **cấm** tuyên bố chỉ tiêu §1.4 khi còn `uncalibrated` | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC04-07` | PC04 | Tham số mật độ: `r = 0.8000`, `min_members = 3`, `K = 4`, `min_prior_windows = 2`, `min_delta = 2.0000`, `ε = 1.0000`, `max_emerging_directions = 3` | PROVISIONAL, cổng REQ-A4 | Báo cáo và mật độ |
| `PROV-PC04-08` | PC04 | `max_items_per_period = 50`; vượt hạn mức → `pending_item_ledger(budget_exceeded)`, **không** bị bỏ | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC04-09` | PC04 | Kỳ rỗng để lại **một** hàng `report(status='aborted', abort_reason='empty_period')` — phương án (b), **không** theo khuyến nghị (a) của Coordinator. Lý do: `coverage_window` không có khóa idempotency, nên dưới (a) một lần mất ACK sẽ thử tiến coverage lần hai và trả `CONFLICT` | PROVISIONAL | Báo cáo và mật độ |
| `PROV-PC08-01` | PC08 | Tham số xác thực: Argon2id (64 MiB / t=3 / p=1); session idle 12 h, absolute 30 d; CSRF 128 bit; login 5 lần/15 phút, lockout 15 phút | PROVISIONAL | Vận hành và bảo mật |
| `PROV-PC08-02` | PC08 | Token worker 256 bit, quyền `0600`, rotation 180 ngày, overlap 24 h; `task_credential_ttl = 900 s` **buộc bằng** `lease_ttl_analysis` của PC03 | PROVISIONAL | Vận hành và bảo mật |
| `PROV-PC08-03` | PC08 | Backup 03:00 hằng ngày, timeout 600 s, retention 14 daily / 8 weekly / monthly vô thời hạn; **RPO 24 h, RTO 2 h** | PROVISIONAL | Vận hành và bảo mật |
| `PROV-PC08-04` | PC08 | Audit retention 365 ngày; bản ghi thao tác xóa giữ **vô thời hạn**; AEAD 256-bit với master key ngoài DB | PROVISIONAL | Vận hành và bảo mật |
| `PROV-PC08-05` | PC08 | Giới hạn fetch ngoài: redirect ≤ 3, timeout 10 s / 30 s, body ≤ 10 MiB | PROVISIONAL | — (kỹ thuật) |

**Phạm vi cố ý để trống, có gate** (không phải quyết định, và không được lấp bằng số bịa): `research_connector_rate_limit` của PC03 giữ bốn giá trị `null` với `status: PLACEHOLDER_KC` và chỉ một sàn an toàn `min_interval_ms = 3000`, căn cứ `REQ-A6` vẫn ở trạng thái **KC**. PC05 phải điền từ tài liệu chính thức trước khi research connector được coi là `CONTRACT_READY`.

### 8.6 Câu hỏi Owner phát sinh trong đợt FIX3

| Câu hỏi | Gói nêu | Đã có mục trong `owner-decision-request.md` |
| --- | --- | --- |
| `schedule_timezone` thật (nếu khác `Asia/Ho_Chi_Minh` thì mọi fixture lịch của PC03/PC04 phải dựng lại) | PC03, PC04 | mục **Timezone** (đã có, nay ghi thêm hệ quả) |
| `per_run_post_limit` / `per_run_duration_limit` thật (`REQ-OQ05`) và mốc lịch thật (`REQ-OQ06`) | PC03 | mục **Bộ giá trị mặc định** (đã có) |
| Tám quyết định báo cáo/mật độ của PC04, gồm backfill khóa theo chữ tag chuẩn hóa, ngưỡng `PROVISIONAL_BOOTSTRAP` và kỳ rỗng phương án (b) | PC04 | mục **Tham số báo cáo và mật độ** (mới) |
| Hệ quả của việc purge xóa credential đăng nhập; dữ liệu purge vẫn nằm trong backup | PC08 | mục **Phạm vi của `data.purge_all`** (đã có, nay bổ sung hai hệ quả) |
| RPO 24 h / RTO 2 h, retention backup, cơ chế xác thực và các tham số session | PC08 | mục **Vận hành và bảo mật** (mới) |
| `CSRF_REJECTED` và `run.resume` từ `blocked` | Coordinator FIX3 | mục **Hai thay đổi kỹ thuật cần Owner biết** (mới) |

### 8.7 Đăng ký quyết định của PC09 và PC10 (đợt FIX5, ruling R5-06)

Tiếp nối §8.5. PC00 **ghi nhận, không thẩm định lại**; chủ sở hữu vẫn là gói gốc.

**PC09 — đã kiểm: không có quyết định sản phẩm nào, không có câu hỏi Owner nào.** Packet FIX4 dự đoán "PC09: none expected"; kiểm `evidence/handoffs/PC09-handoff.md` §6.2 xác nhận đúng — ba quyết định của PC09 đều mang tính **phương pháp**, nằm trong phạm vi ủy quyền của verification owner, và không đổi cam kết nào với Owner. Ghi lại để chúng không vô hình:

| ID | Quyết định | Trạng thái | Cần ai |
| --- | --- | --- | --- |
| `PROV-PC09-01` | Quy tắc `coverage_status` của `acceptance/traceability.csv`: một dòng nhận `BLOCKED_B<nn>` khi nó nằm trong danh sách "REQ ảnh hưởng" của `AMD-B<nn>` — tức **văn bản cam kết của chính dòng đó** sẽ đổi nếu Owner phê chuẩn amendment. **84 dòng** rơi vào diện này; cột `notes` vẫn giữ độ phủ nền để không mất thông tin | PROVISIONAL | Coordinator (nếu muốn quy tắc khác thì số ở `review.md` §2 phải tính lại) |
| `PROV-PC09-02` | Header của `traceability.csv` đặt ở front-matter `precode/review.md`, theo đúng tiền lệ đã chấp nhận cho `requirements.csv` (một dòng comment sẽ làm `csv.DictReader` đọc sai). `e0_check` `E0-17` kiểm sự tồn tại và đầy đủ của header thay thế | PROVISIONAL | Coordinator |
| `PROV-PC09-03` | `x-contract.deviations` chấp nhận **tên trường đồng nghĩa**: `analysis-result.schema.json` của PC06 dùng bộ tên dài hơn bộ `{rule, deviation, reason, evidence_refs}` của ruling FIX4; PC09 chấp nhận và ghi note nêu đích danh tên đã dùng, thay vì FAIL một deviation đã khai đầy đủ về nội dung | PROVISIONAL | Coordinator (ép đúng bốn tên là một sửa nhỏ ở PC06 cộng một dòng ở `e0_check`) |

Đáng ghi thêm — **PC09 từ chối nâng nhãn**: packet của nó viết "expect G0–G3 `MET_PROVISIONAL` at best", nhưng PC09 ghi `G0 = MET_PROVISIONAL` và **`G1, G2, G3 = PARTIALLY_MET`**, vì mỗi cổng còn ít nhất một điều kiện đo được và chưa đạt (G1-X5: 26 cạnh; G2-X3: TSR-A01; G3-X5: `REQ-A6` và `CR-PC07-04` còn **KC**). Đây là hành vi đúng theo SRC-PLAN §2 và §9 — không nâng nhãn bằng suy diễn — và PC00 ghi lại để không ai "sửa" nó thành `MET_PROVISIONAL` cho gọn.

**PC10 — ba giả định PROVISIONAL và một ngoại lệ định dạng.** PC10 tự khai **không** tạo quyết định sản phẩm nào.

| ID | Giả định | Trạng thái | Cần ai |
| --- | --- | --- | --- |
| `PROV-PC10-01` | Layout đường dẫn theo stack A: `server/app/<domain>/…`, `collector/app/…`, `worker/app/…`, `server/app/web/…`, `probe/x_feasibility/…`, `tests/contract/…`, `tests/integration/…` | PROVISIONAL | **Owner** — đây là hệ quả trực tiếp của `ADR-0006` chưa được trả lời. Nếu Owner chọn B/C thì **chỉ §3 và §8** của mỗi card phải viết lại, không phải hợp đồng |
| `PROV-PC10-02` | Ba không gian ID mới: `EVM-<Task ID>` (evidence manifest của card), `SG-<nn>` (stop condition trong card), `PC10-PIN-<ngày>` (pin epoch). Baseline §3 chưa có ID nào phục vụ ba việc này | PROVISIONAL | Coordinator — đổi được bằng một lần sửa generator |
| `PROV-PC10-03` | Trần claim `LIVE_FEASIBILITY_VERIFIED` cho card SP1 và `CONTRACT_ONLY` cho đường CLI/ACP của card adapter; hai nhãn này **không** có trong bảng claim label của SRC-PLAN §2 | **Đã có ruling** | Ruling `R5-07` đã chốt: thay `CONTRACT_ONLY` bằng nhãn của SRC-PLAN §2. PC10-FIX1 thực hiện. `LIVE_FEASIBILITY_VERIFIED` **có** trong SRC-PLAN §2 nên giữ nguyên |

**Ngoại lệ định dạng của PC10 (khai báo, không phải thiếu sót).** Card `TC-*.md` **không** mang contract header đầy đủ của baseline §3; chúng mang front-matter riêng của card (`card_id`, `milestone`, `gate`, `stack_decision`, `claim_ceiling`, `owner_modules`, `scenario_refs`, `invariant_refs`, `evidence_manifest_id`, `source_refs`, `baseline_pin_ref`, `coding_precondition`). Lý do PC10 nêu: card **không phải hợp đồng** — nó là lệnh giao việc pin một hợp đồng, nên `producers`/`consumers`/`dependencies` không có nghĩa; thông tin tương đương nằm ở §4, §5 và §11 của card. Bốn file khung (`TEMPLATE.md`, `agent-tasks/README.md`, `WALKTHROUGH.md`, `precode/change-control.md`, `precode/README.md`) **có** mang header đầy đủ.

Đây là ngoại lệ thứ **tư** cùng loại trong dự án, sau ADR (ruling R-05), `requirements.csv` và `traceability.csv` (`PROV-PC09-02`). Ruling `R5-07` yêu cầu PC10 khai báo nó trong `agent-tasks/README.md`. **Đề nghị của PC00:** khi Coordinator sửa baseline §3 lần tới, gom cả bốn thành một câu quy tắc chung — *"file không phải hợp đồng (decision record, registry dạng CSV, task card) mang header riêng đã khai báo, liệt kê tại …"* — thay vì bốn ngoại lệ rời rạc mà mỗi lượt audit lại phải đối chiếu lại. Xem `CR-PC00-10`.

Ngoại lệ phụ: `precode/README.md` và `precode/change-control.md` không tự pin hash của chính mình (chicken-and-egg); hash của chúng nằm ở bảng §2 của handoff PC10.

### 8.8 Invariant phát sinh I16 và I17 (finding `F-A2R1-07`, ruling FIX6 F-07)

Baseline §3 cho phép `I16+` **chỉ khi có decision record**. Hai invariant này đã được `contracts/data/invariants.md` định nghĩa và đang được `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `contracts/data/entities.yaml` và `precode/review.md` trích dẫn, nhưng decision record thì chưa tồn tại. Audit `A2-R1` nói đúng trọng tâm: *"Defining an invariant inside the contract that consumes it is what the rule exists to prevent."* Mục này lấp đúng chỗ đó. Lập luận kỹ thuật là của PC02 và tôi **không** viết lại; tôi ghi nhận, gắn trạng thái và nêu phần còn thiếu.

#### `PROV-PC00-05` — I16: Attempt không bao giờ là kết quả

- **Phát biểu** (nguyên văn `contracts/data/invariants.md` §I16). Không có đường đọc nào biến một hàng `analysis_attempt` thành kết quả phân tích: mọi truy vấn "kết quả của target X" chỉ đọc `analysis` với `status = 'valid'`. Attempt là append-only; `outcome` chỉ được ghi một lần từ trạng thái đang chạy sang trạng thái cuối.
- **Vì sao cần một invariant riêng, không phải một dòng phụ của I04.** SRC-PLAN §3 B07 yêu cầu "attempt lỗi không tính là kết quả hoàn thành" và §8.2 yêu cầu "không ghi output sai schema thành `valid`". Yêu cầu đó **cắt ngang** I04: I04 nói về tính **duy nhất theo key** của kết quả, không nói gì về việc một attempt có thể bị **đọc nhầm** thành kết quả. Vì PC02 tách hai bảng (`analysis`, `analysis_attempt`), ranh giới giữa chúng cần một phát biểu có oracle riêng.
- **Nguồn.** SRC-PLAN §3 hàng B07, §8.2; SRC-SPEC §9.3 (hàng "AI lỗi một mục"), §10.2. Qua `AMD-B07` và `ADR-0008` (analysis key và generation).
- **Owner/hợp đồng.** `contracts/data/entities.yaml` → entity `analysis_attempt`; `transactions[TXN-analysis-accept]`.
- **Counterexample (phải FAIL).** UI hoặc report builder đọc attempt cuối cùng để hiển thị summary khi chưa có hàng `valid` → mục đó **phải** hiện là thiếu summary và vào `pending_item_ledger`, report `quality = 'partial'` (B17, `AMD-B17`).
- **Oracle.** Với mọi target không có hàng `analysis` valid: view "summary của target" trả rỗng **và** `#pending_item_ledger[target_key = T, state='pending'] = 1`. Với mọi hàng `analysis` valid: tồn tại **đúng một** attempt `accepted` được trỏ bởi `accepted_from_attempt_id`. `#analysis_attempt[outcome='timeout_unknown' AND cost_uncertain = false] = 0`.
- **Scenario.** Dương: `SC10`, `SC50`. Âm: **`SC56`** — *"Ghi 0 cho usage không biết, tự bật fallback, hoặc đếm attempt là kết quả — ba phản chứng của I14 và I16"*, khai `polarity: negative`. Hỗn hợp: `SC28` (worker chết sau AI call) — trích I16 nhưng khai `mixed`, và theo `F-A2R1-10` thì `mixed` không tính cho cực nào, nên nó **không** thay thế được `SC56`.
- **Lịch sử của mục này.** Ở bản đầu (FIX5) I16 **không** có cực âm nào: chỉ có `SC28` khai `mixed`. PC00 ghi khoảng trống đó thành chữ và báo `CR-PC00-11` thay vì tự khai lại polarity của một scenario mình không sở hữu. PC09 cấp `SC56` ở đợt FIX7 và khoảng trống đã đóng; anchor trong `precode/baseline.json` mang `negative_scenarios: ["SC56"]`. Cùng đợt đó PC09 cũng lấp hai cực còn thiếu của các invariant khác: **`SC54`** (âm, phản chứng của I04 — hai kết quả hợp lệ cho cùng một `(analysis_key, generation)` là không thể) và **`SC55`** (dương, mặt dương của I14 — usage không biết được ghi là `unknown` với ba trường NULL). Ba ID đó đã có anchor riêng trong `baseline.json`.
- **Trạng thái.** `PROVISIONAL`, `decision_owner: Coordinator (provisional, technical)` — theo `CR-PC00-12`. Đây là một **data invariant kỹ thuật**: nó phát biểu ranh giới đọc giữa hai bảng (`analysis` và `analysis_attempt`) chứ không đổi cam kết nào Owner đã chọn. `REQ-D19` ("mỗi mục có summary hiển thị ngay tại mục") vẫn đúng nguyên văn; I16 chỉ nói rằng khi **chưa** có kết quả hợp lệ thì mục đó phải hiện là thiếu summary, đúng như `AMD-B17` đã chốt. Vì vậy **không cần** một mục riêng trong `precode/owner-decision-request.md`, trừ khi Owner phản đối.
- **Nếu bị bác bỏ.** Không có phương án thay thế trong cùng mô hình hai bảng: nếu không cấm đường đọc attempt thì `AI_OUTPUT_INVALID` và `AI_ATTEMPT_UNCERTAIN` không có oracle phân biệt được "chưa có kết quả" với "có kết quả kém". Khi đó PC06 phải quay lại mô hình một bảng, và `AMD-B07` phải viết lại.
- **Liên kết.** I04 (cực âm riêng: `SC54`), I14 (cực dương riêng: `SC55`), `REQ-D19`, `REQ-D25`, `REQ-D26`, `REQ-AC10`, `AMD-B07`, `AMD-B17`, `ADR-0008`, `SC10`, `SC28`, `SC50`, `SC56`.

#### `PROV-PC00-06` — I17: Merge identity không làm đổi bất kỳ snapshot lịch sử nào

- **Phát biểu** (nguyên văn `contracts/data/invariants.md` §I17). Một transaction merge chỉ được ghi các cột nằm trong merge move-set (`entities.yaml` → `transactions[TXN-identity-merge].merge_move_set`). Cụ thể, sau merge: `saved_snapshot` (mọi cột, kể cả `target_key_at_save`), `ingest_receipt`, `analysis_attempt`, `identity_merge_audit` cũ, và `report_item` thuộc report `published` đều **byte-identical** với trước merge.
- **Vì sao cần một invariant riêng.** SRC-PLAN §11 PC02 yêu cầu tường minh "cách không làm đổi historical snapshot sau merge". I03 chỉ nói về **tính đúng của identity**; I08 chỉ nói về **Saved**. Không invariant nào của SRC-PLAN §7 phát biểu ràng buộc **chéo** giữa thao tác merge và các bảng lịch sử khác (report đã publish, receipt, attempt). I17 lấp đúng khoảng trống đó và cho merge một oracle **đếm được**.
- **Nguồn.** SRC-PLAN §11 PC02, §9.1; SRC-SPEC §7.3, §3.5 (D29), §3.6 (D55). Qua `AMD-B15` và `ADR-0009` (identity, alias, target tagged union).
- **Owner/hợp đồng.** `contracts/data/entities.yaml` → `transactions[TXN-identity-merge]`; `referential_integrity.historical_snapshot_rule`; `contracts/data/identity.md` §6.4.
- **Positive scenario** (nguyên văn nguồn). Owner đã Save work W1 lúc 10:00 (snapshot S1); 11:00 W1 bị merge vào W2. Con trỏ `saved_item.target_work_id` chuyển sang W2 và `moved_by_merge_id` được ghi; **S1 không đổi một byte**, `target_key_at_save` vẫn là `work:<W1>`. Fixture `a-merge-doi-arxiv.json`.
- **Scenario.** Dương: `SC07`, `SC12`. Âm: `SC23` (identity conflict). Hỗn hợp: `SC09`, `SC13`, `SC32`. I17 đã có đủ một cực dương và một cực âm khai tường minh **ngay từ đầu**; I16 đạt điều đó sau khi PC09 cấp `SC56` ở đợt FIX7.
- **Trạng thái.** `PROVISIONAL`, `decision_owner: Coordinator (provisional, technical)` — theo `CR-PC00-12`. Đây là một **data invariant kỹ thuật**: nó là cơ chế **thực thi** của `REQ-D29` (XN), `REQ-D55` (UQ) và `AMD-B15` sau khi merge, không phải một lựa chọn sản phẩm mới. Owner đã chọn "không báo lại" và "Saved là snapshot"; I17 chỉ nói merge không được phép âm thầm làm hai điều đó sai. Vì vậy **không cần** một mục riêng trong `precode/owner-decision-request.md`, trừ khi Owner phản đối.
- **Nếu bị bác bỏ.** Không có cách nào khác giữ `REQ-AC12` ("Save bền", snapshot không đổi) đúng qua một lần merge: nếu merge được phép ghi ngoài move-set thì snapshot đã lưu có thể đổi và `REQ-AC09` mất mốc `first_announced`.
- **Liên kết.** I03, I07, I08, `REQ-D29`, `REQ-D55`, `REQ-AC07`, `REQ-AC09`, `REQ-AC12`, `AMD-B15`, `ADR-0009`, `SC07`, `SC12`, `SC23`.

**Đã cập nhật `precode/baseline.json`:** `id_conventions.invariant.form` từ `I01..I15` thành `I01..I17`, kèm ghi chú rằng I16/I17 được nhận vào **đúng theo** điều kiện "chỉ khi có decision record" và trỏ về mục này; `I18+` vẫn phải có decision record mới. Anchor của chúng nằm ở nhóm mới `source_anchors.PROJECT.invariants` — **không** đặt trong nhóm `SRC-PLAN`, vì chúng không có trong văn bản SRC-PLAN và một anchor giả nguồn sẽ là chính lớp lỗi mà finding này phạt.

### 8.9 Trạng thái các change request do PC00 phát ra

`precode/review.md` §12 hợp nhất toàn bộ 75 CR của dự án; bảng dưới đây chỉ là **phần của PC00**, dùng đúng trạng thái đó để hai file không lệch nhau. Bốn dòng `CR-PC00-01`, `-03`, `-09`, `-10` trước đây không có trạng thái ở đâu (`F-A2R1-04`) — nay có.

| CR | Nội dung tóm tắt | Trạng thái | Căn cứ |
| --- | --- | --- | --- |
| `CR-PC00-01` | Đối chiếu `requirement_refs`/`decision_refs` của PC01 và PC02 với registry và ADR của PC00 | **Đã giải** | Lượt hòa giải FIX1: PC01/PC02 đã pin lại tham chiếu theo `precode/requirements.csv` và `precode/adr/`; củng cố bởi `F-A1R1-03` đã VERIFIED |
| `CR-PC00-02` | PC09 theo dõi `F-PC00-01`/`F-PC00-02` ở G0 | Còn mở, **đã xử lý** ở `precode/gates.yaml` G0 | `review.md` §12 |
| `CR-PC00-03` | AMD-B02 (ánh xạ enum) và AMD-B08 (timestamp mili giây + ingest sequence) là đầu vào bắt buộc của `run.yaml` và `time-and-tags.md` | **Đã giải** | PC03 và PC04 đã land đúng hai giá trị này; cần một lượt xác minh độc lập trên epoch mới |
| `CR-PC00-04` | PC01 dùng đúng tên operation xóa và `SC32` | **Đã được đáp ứng ngược dòng** | `review.md` §12 |
| `CR-PC00-05` | Đưa `EV-PC00-06` và anchor SC vào tập E0 / traceability | Còn mở, **đã xử lý** | `review.md` §12 |
| `CR-PC00-06` | Đối chiếu `scenarios.yaml` với anchor; anchor ≠ scenario đã viết | Còn mở, **đã xử lý một phần** | `review.md` §12; `R5-08` giao PC09 điền `fixture_refs` cho 12 scenario |
| `CR-PC00-07` | `ports.yaml` trích một REQ id **không tồn tại** trong registry (SRC-SPEC không có §8.4; §8.4 là của SRC-PLAN) → phải trỏ sang `REQ-S9.3-08`; `run.resume` mở guard cho `blocked`; `data.purge_all.scenario_refs: [SC44]` | **Đã được đáp ứng ngược dòng** | `review.md` §12; PC01-FIX3 đã gỡ id sai |
| `CR-PC00-08` | Đăng ký `CSRF_REJECTED` ở `errors.yaml`; thu hẹp `FORBIDDEN_EDGE` | **Đã được đáp ứng ngược dòng** | `review.md` §12; `CR-PC08-03` cùng nhóm |
| `CR-PC00-09` | Chủ đề SC45–SC48 trong ruling R4-03 khác `acceptance/fixtures/telegram/README.md` | **Đã giải** | `PKT-PC00-FIX3`: PC00 lấy chủ đề từ README (nguồn packet chỉ đích danh); bốn chủ đề trong ruling tương ứng fixture a/b/d/e vốn đã trích `SC14`/`SC25` |
| `CR-PC00-10` | Gom bốn ngoại lệ header rời rạc thành một quy tắc chung ở baseline §3 | **Đã giải** | Coordinator đã ban hành quy tắc header chung; bốn ngoại lệ (ADR, `requirements.csv`, `traceability.csv`, task card) nay nằm dưới cùng một câu quy tắc |

**Lưu ý về cách diễn đạt hàng `CR-PC00-07`.** Hàng đó cố ý **không** viết ra id sai: id ấy đã bị PC01-FIX3 gỡ khỏi `ports.yaml` và không tồn tại trong `precode/requirements.csv`, nên nhắc lại nguyên văn sẽ tạo một token trông như trích dẫn hợp lệ và làm gate quét id báo động (`CR-PC01-12`). Nội dung của CR được giữ nguyên: id sai là gì (một REQ thuộc một mục §8.4 mà SRC-SPEC không có) và id đúng là `REQ-S9.3-08`. Đừng "khôi phục" id cũ vào file này.

**Lưu ý về mức bằng chứng.** "Đã được đáp ứng ngược dòng" trong bảng này là **lời tự khai của gói nhận**, đúng như `review.md` ghi: PC09 ghi nhận chứ không tự xác minh từng cái. Không dòng nào ở đây là `CLOSED`; đóng một finding hay một CR cần authority được chỉ định sau khi có xác minh độc lập trên epoch mới, và người xác minh không được là người viết bản sửa.
