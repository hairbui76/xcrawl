---
contract_id: CT-ops-internet-boundary
version: 0.1.0
status: draft
owner_role: operations contract owner
source_refs:
  - SRC-SPEC §2.3
  - SRC-SPEC §6.1
  - SRC-SPEC §6.4
  - SRC-SPEC §10.1
  - SRC-SPEC §10.2
  - SRC-SPEC §11.2
  - SRC-SPEC §11.3
  - SRC-SPEC §11.4
  - SRC-SPEC §12 AC-17
  - SRC-SPEC §12 AC-18
  - SRC-SPEC §13.2
  - SRC-PLAN §3 B13
  - SRC-PLAN §6
  - SRC-PLAN §7 I11
  - SRC-PLAN §11 PC08
requirement_refs:
  - REQ-D31
  - REQ-D32
  - REQ-D33
  - REQ-D34
  - REQ-S6.4-03
  - REQ-S10.2-02
  - REQ-S11.2-05
  - REQ-S11.2-06
  - REQ-S11.3-02
  - REQ-S11.4-01
  - REQ-S11.4-02
  - REQ-S11.4-03
  - REQ-S11.4-04
  - REQ-S13.2-01
  - REQ-S13.2-02
  - REQ-S13.2-04
  - REQ-A5
  - REQ-A6
  - REQ-AC17
  - REQ-AC18
  - REQ-OOS-02
decision_refs: [B12, B13, ADR-0001, ADR-0010]
invariant_refs: [I01, I11]
producers: [MOD-backend-api, MOD-research-connector, MOD-telegram-adapter]
consumers: [MOD-x-collector, MOD-analysis-worker, MOD-ai-adapter, MOD-embedding-service, MOD-web-ui]
dependencies:
  - contracts/modules.yaml
  - contracts/capabilities.yaml
  - contracts/ports.yaml
  - contracts/ops/deployment.md
  - contracts/ops/secrets.md
  - contracts/errors.yaml
  - contracts/ai/providers.yaml (PC06, chưa tồn tại)
  - contracts/telegram/delivery.md (PC07, chưa tồn tại)
scope: >
  Ranh giới Internet của hệ thống: module nào được gọi ra host nào, quy tắc lấy URL từ nội dung nguồn (chống SSRF,
  chặn địa chỉ nội bộ và redirect tới chúng), quy tắc kết nối vào, quy tắc render nội dung không đáng tin cậy trong
  app và trên Telegram, và cấm truy cập tool từ nội dung nguồn. Kèm cơ chế thực thi và oracle kiểm được cho từng
  quy tắc. File này **không** định nghĩa operation, mã lỗi hay capability của adapter AI — nó chỉ ràng buộc mặt
  mạng và mặt nội dung của các ranh giới đã có.
verification: >
  E0 self-validation: mọi operation/mã lỗi/module được trích phải tồn tại trong ports.yaml / errors.yaml /
  modules.yaml (script EV-PC08-01). Các oracle trong §7 là **NOT_RUN**: chưa có code, chưa có harness mạng.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Ranh giới Internet

## 1. Nguyên tắc

| ID | Nguyên tắc |
| --- | --- |
| `NET-P1` | **Default deny cho egress.** Một module chỉ gọi ra các host trong `network_egress` của nó ở `contracts/modules.yaml`. Host không có trong danh sách là bị cấm, kể cả host "vô hại". |
| `NET-P2` | **Không có cổng vào máy cá nhân.** Mọi kết nối từ máy cá nhân là outbound (REQ-S6.4-03). Không có đường nào để server hay Internet gọi vào collector/worker. |
| `NET-P3` | **Nội dung nguồn không chọn đích đến.** Model, post, abstract hay toàn văn không được quyết định fetch URL nào, gửi tin cho ai, hay gọi tool gì (REQ-S11.4-03, I11). |
| `NET-P4` | **Không né chặn.** Không có cơ chế né CAPTCHA, giả fingerprint, luân chuyển account hay proxy (REQ-S13.2-04, REQ-OOS-02). Bị chặn thì dừng và báo `X_ACCESS_BLOCKED`. |
| `NET-P5` | **Nội dung ngoài là văn bản, không phải mã.** Không HTML, không script, không thực thi (REQ-S11.4-02). |

## 2. Egress theo module

Bảng này là mặt vận hành của `network_egress` trong `contracts/modules.yaml`; nó không thêm quyền nào mới.

| Module | Được gọi ra | Không được gọi ra | Cơ chế |
| --- | --- | --- | --- |
| `MOD-x-collector` | X qua **Chrome profile riêng**; API của server | Telegram, provider AI, arXiv/OpenAlex, SQLite server | egress allowlist + capability tiến trình |
| `MOD-analysis-worker` | API của server; endpoint provider AI **đã cấu hình cho task đang chạy** | X, Telegram, arXiv/OpenAlex | egress allowlist |
| `MOD-ai-adapter` | Endpoint provider của đúng task | Mọi thứ khác, kể cả arXiv/OpenAlex "hợp lệ" (`FE-19`) | egress allowlist + tool bị khóa |
| `MOD-research-connector` | arXiv API, OpenAlex API | X/Chrome (`FE-20`), provider AI | egress allowlist + import rule |
| `MOD-telegram-adapter` | Telegram Bot API | Provider AI, arXiv/OpenAlex | egress allowlist |
| `MOD-embedding-service` | **Không gì cả** | Toàn bộ Internet (`FE-22`) | egress rỗng — đây là điều làm AC-16 đứng vững |
| `MOD-settings-service` | Endpoint provider khi `settings.test_provider` | Mọi thứ khác | egress allowlist |
| `MOD-backup-service` | Đích lưu backup đã cấu hình | Mọi thứ khác | egress allowlist |
| `MOD-web-ui` | Chỉ origin của app | Telegram, provider AI, SQLite (`FE-01…04`) | CSP + không có secret ở frontend |

**arXiv/OpenAlex:** nhịp gọi và yêu cầu định danh phải đọc từ tài liệu chính thức khi triển khai
(REQ-S13.2-01, REQ-A6, D34). Không gọi không giới hạn. OpenAlex yêu cầu một email liên hệ —
`ACT-research-connector` giữ đúng thứ đó và không giữ gì khác (`capabilities.yaml`).

## 3. Lấy URL từ nội dung nguồn

Đây là bề mặt SSRF duy nhất của hệ thống: post trên X chứa link do người lạ viết.

### 3.1 Ai được lấy URL

- **Collector** trích URL từ post và **chỉ gửi chuỗi URL về server** trong `ingest.submit_batch`. Nó không fetch
  URL đó để lấy metadata.
- **Research connector** nhận **DOI hoặc arXiv ID đã chuẩn hóa**, không nhận URL tùy ý (`ports.yaml`
  `research.fetch_work_metadata`, `DC-RC-02`). Đây là điểm mấu chốt: hệ thống không "mở link người lạ", nó tra ID
  trên hai API đã biết.
- **Model/AI adapter**: không bao giờ (`FE-19`, `DC-AI-02`). Một câu "hãy tải trang này" trong abstract không tạo
  ra request nào.

### 3.2 Quy tắc cho mọi lời gọi ra ngoài xuất phát từ dữ liệu

Áp dụng cho research connector và cho bất kỳ đường fetch nào phát sinh sau này.

| Quy tắc | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| Scheme allowlist | chỉ `https` | — | `http`, `file`, `ftp`, `gopher`, `data`, `blob` bị từ chối; `file`/`gopher` là vector SSRF kinh điển. |
| Host allowlist | host của arXiv và OpenAlex đã cấu hình | — | Không phải "chặn host xấu" mà là "chỉ cho host đã biết" — danh sách chặn luôn thiếu. |
| Chặn địa chỉ | loopback `127.0.0.0/8`, `::1`; private `10/8`, `172.16/12`, `192.168/16`, `fc00::/7`; link-local `169.254/16`, `fe80::/10`; metadata `169.254.169.254`; `0.0.0.0/8`; multicast | — | Chặn theo **địa chỉ IP đã phân giải**, không theo chuỗi tên miền — một tên miền công khai có thể trỏ về `127.0.0.1`. |
| Kiểm tại thời điểm kết nối | phân giải DNS → kiểm IP → kết nối tới **chính IP đó** | — | Chống DNS rebinding: kiểm rồi kết nối lại bằng tên là kiểm một địa chỉ, kết nối một địa chỉ khác. |
| Redirect | tối đa **3** bước · PROVISIONAL; **mỗi** bước kiểm lại toàn bộ quy tắc trên | PROVISIONAL | Redirect tới `127.0.0.1` là đường vòng phổ biến nhất; ba bước đủ cho DOI resolver thông thường. |
| `connect_timeout` | **10** giây | PROVISIONAL | Đủ cho một API công cộng ở xa; dài hơn thì một host treo giữ tài nguyên vô ích. |
| `total_timeout` | **30** giây | PROVISIONAL | Trần cho một lần lấy metadata; vượt ⇒ `SOURCE_METADATA_UNAVAILABLE`, không đoán dữ liệu. |
| `max_response_bytes` | **10** MiB | PROVISIONAL | Metadata/abstract không bao giờ lớn thế; chặn cả decompression bomb bằng cách đếm **byte đã giải nén**. |
| Xác thực | không gửi credential nào tới host nguồn | — | Không có credential nào thuộc về arXiv/OpenAlex ngoài email liên hệ. |

Vi phạm bất kỳ dòng nào ⇒ **không có request** (hoặc hủy giữa chừng) và `SOURCE_METADATA_UNAVAILABLE` cho item đó;
work vẫn tồn tại ở mức "chỉ có post" (REQ-S9.3-05, D33). Không đoán DOI, không xóa abstract cũ đã có.

## 4. Ingress

| Điểm vào | Ai được vào | Xác thực | Ghi chú |
| --- | --- | --- | --- |
| App HTTPS (443) | Internet | `ownerSessionCookie` + CSRF; `workerBearer` cho collector/worker | Xem `secrets.md` §2.3 |
| Telegram webhook | Telegram | Header secret (`telegramWebhookSecret`) | Sai header ⇒ `UNAUTHORIZED`, không xử lý, không trả lời |
| `health.get_liveness` | Bất kỳ | Không | Chỉ `up` + schema version |
| Máy cá nhân | **Không ai** | — | Không lắng nghe cổng nào (REQ-S6.4-03) |
| Chrome debug | Chỉ tiến trình cùng máy | Loopback | `127.0.0.1` duy nhất; không LAN, không reverse proxy (REQ-S11.2-06) |
| SQLite | Chỉ tiến trình server | — | File trên volume; không có cổng (`NC-05`) |

## 5. Render nội dung không đáng tin cậy

Nội dung X và paper đi vào ba nơi hiển thị: app, Telegram, và prompt của model.

| Nơi | Quy tắc |
| --- | --- |
| Web app | Render **như văn bản**. Không `innerHTML`, không `dangerouslySetInnerHTML`, không nhúng HTML từ nguồn. Nếu hiển thị markdown thì chỉ dùng tập con an toàn (đoạn văn, nhấn mạnh, danh sách, link) với sanitiser bật mặc-định-từ-chối; thẻ `script`/`style`/`iframe`/`object`/`svg` và mọi thuộc tính `on*` bị loại. |
| Link trong nội dung | Hiển thị **host thật** cạnh chữ hiển thị; `rel="noopener noreferrer"`, `target` mở tab mới. Không tự động fetch preview — preview là một lời gọi ra ngoài do nội dung nguồn quyết định (`NET-P3`). |
| CSP | `default-src 'self'`; `script-src 'self'` (không `unsafe-inline`, không `unsafe-eval`); `object-src 'none'`; `frame-ancestors 'none'`; `base-uri 'self'`; `form-action 'self'`. PROVISIONAL — PC05/PC10 chốt chi tiết khi có stack. |
| Telegram | Escape theo đúng chế độ parse đang dùng; độ dài và cách cắt tin thuộc `contracts/telegram/delivery.md` (PC07). Nội dung nguồn **không** được chứa markup điều khiển sống sót qua escape. |
| Prompt của model | Nội dung ngoài đi vào như **dữ liệu có ranh giới rõ**, đầu ra bị ràng buộc bằng schema (REQ-S11.4-04). Chi tiết ở PC06. |

**Che secret trước khi ghi log (REQ-S11.2-05)** áp cho mọi đường ghi nhật ký nhắc tới ở file này: log của
research connector (URL, redirect chain, mã lỗi), log của adapter AI (không ghi transcript đầy đủ), và log của
adapter Telegram (không ghi token, không ghi mã liên kết). Mẫu che và danh sách trường cấm ghi nằm ở
`contracts/ops/secrets.md` §4.3; file này chỉ ràng buộc rằng **không đường ra Internet nào được ghi log thô**.
Cổng debug của Chrome bind loopback (**REQ-S11.2-06**) là dòng tương ứng ở §4 bảng ingress.

## 6. Tool access từ nội dung nguồn

Cấm tuyệt đối (REQ-S11.4-03, I11, ADR-0010):

- Adapter CLI/ACP chạy với **tool, truy cập file và mạng bị khóa** ngoài phần inference.
- Không có cơ chế nào cho phép model yêu cầu fetch URL, đọc file, chạy lệnh, hay gửi Telegram.
- Provider không kiểm chứng được cô lập ⇒ adapter `disabled`; worker khai `usable: unusable`,
  `reason_code: isolation_unverified` (`capabilities.yaml`).
- Một yêu cầu gọi tool xuất hiện trong đầu ra của model là **sự kiện cần ghi lại** (audit), không phải thứ để bỏ
  qua im lặng; item đó đi theo `AI_OUTPUT_INVALID`.

## 7. Cơ chế thực thi và oracle

Mọi oracle dưới đây là **NOT_RUN** ở giai đoạn Pre-code: chưa có code và chưa có harness mạng.

| ID | Quy tắc | Cơ chế | Oracle |
| --- | --- | --- | --- |
| `NB-01` | Egress allowlist theo module | `ENF-network-egress-allowlist` | Đếm outbound connection theo host trong một lần chạy fixture; host ngoài allowlist ⇒ 0 |
| `NB-02` | Embedding không gọi mạng | `ENF-network-egress-allowlist` + import rule | Chạy luồng AC-16 không cấu hình key nào: 0 request ra ngoài từ container `embedding` |
| `NB-03` | Redirect tới địa chỉ nội bộ bị chặn | Hook kiểm IP tại mỗi bước redirect | Fixture `g-ssrf-redirect-private.json`: 0 kết nối tới `127.0.0.1`; item nhận `SOURCE_METADATA_UNAVAILABLE` |
| `NB-04` | Model không gây ra fetch | Không có tool nào được cấp | Fixture `f-secret-canary-injection.json`: 0 request ngoài endpoint provider |
| `NB-05` | Canary secret không rò rỉ | Redaction trước khi ghi + không cấp secret cho task CLI | Chuỗi canary **không** xuất hiện trong output, log hay bất kỳ artifact nào |
| `NB-06` | Chat lạ bị bỏ im lặng | `ENF-command-allowlist` | 0 outbound message tới chat chưa liên kết; 0 mutation (AC-18) |
| `NB-07` | Không có cổng vào máy cá nhân | Cấu hình tiến trình | Quét cổng trên máy cá nhân: 0 cổng lắng nghe của collector/worker; Chrome debug chỉ bind `127.0.0.1` |
| `NB-08` | Không né chặn | Rà soát mã nguồn + hành vi | Khi bị chặn: run chuyển `blocked`, `X_ACCESS_BLOCKED`, **0** request tiếp theo tới X trong run đó |

## 8. Những gì file này **không** quyết định

| Chủ đề | Sở hữu |
| --- | --- |
| Tên header, security scheme, mã HTTP | PC05 |
| Capability và probe cô lập từng provider AI | PC06 |
| Định dạng/escape/cắt tin Telegram | PC07 |
| Danh sách host cụ thể của arXiv/OpenAlex và nhịp gọi thật | PC05 + đọc tài liệu chính thức khi triển khai (A6) |
| Mã lỗi và trạng thái đích | PC03 |
