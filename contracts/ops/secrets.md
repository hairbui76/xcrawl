---
contract_id: CT-ops-secrets
version: 0.1.0
status: draft
owner_role: operations contract owner
source_refs:
  - SRC-SPEC §3.1 D05
  - SRC-SPEC §6.4
  - SRC-SPEC §10.2
  - SRC-SPEC §11.1
  - SRC-SPEC §11.2
  - SRC-SPEC §11.3
  - SRC-SPEC §11.4
  - SRC-SPEC §12 AC-16
  - SRC-SPEC §12 AC-17
  - SRC-SPEC §12 AC-18
  - SRC-PLAN §3 B13
  - SRC-PLAN §5.1
  - SRC-PLAN §6.1
  - SRC-PLAN §7 I01
  - SRC-PLAN §7 I11
  - SRC-PLAN §11 PC08
requirement_refs:
  - REQ-D04
  - REQ-D05
  - REQ-D06
  - REQ-D41
  - REQ-D51
  - REQ-S6.4-02
  - REQ-S6.4-03
  - REQ-S10.2-02
  - REQ-S11.1-01
  - REQ-S11.2-01
  - REQ-S11.2-02
  - REQ-S11.2-03
  - REQ-S11.2-04
  - REQ-S11.2-05
  - REQ-S11.2-06
  - REQ-S11.3-01
  - REQ-S11.4-03
  - REQ-S7.3-05
  - REQ-AC16
  - REQ-AC17
  - REQ-AC18
decision_refs: [B13, ADR-0010, ADR-0006]
invariant_refs: [I01, I11, I14]
producers: [MOD-secret-service, MOD-auth-service]
consumers: [MOD-backend-api, MOD-web-ui, MOD-x-collector, MOD-analysis-worker, MOD-ai-adapter, MOD-telegram-adapter, MOD-backup-service]
dependencies:
  - contracts/modules.yaml
  - contracts/capabilities.yaml
  - contracts/ports.yaml
  - contracts/ops/deployment.md
  - contracts/data/entities.yaml
  - contracts/errors.yaml
  - contracts/state/storage.yaml
  - contracts/http/openapi.yaml (PC05, bản đóng băng ở FC-W3 — xem §2.3 về vì sao không pin hash ở đây)
  - contracts/ai/providers.yaml (PC06, chưa tồn tại)
  - contracts/telegram/commands.yaml (PC07, chưa tồn tại)
scope: >
  Hợp đồng vận hành cho xác thực chủ sở hữu, token của worker, lưu trữ và phân phối secret, và audit log.
  Bao gồm: một tài khoản duy nhất không signup (D05), cơ chế session và CSRF, token collector/analysis worker,
  secret store phía server với mã hóa envelope, phân phối credential theo từng task cho analysis worker (B13),
  ranh giới của profile Chrome và phiên X, secret của Telegram, và chính sách che secret trong log.
  File này **không** định nghĩa operation mới (PC01 sở hữu `contracts/ports.yaml`), không định nghĩa mã lỗi
  (PC03 sở hữu `contracts/errors.yaml`), không định nghĩa wire HTTP (PC05).
verification: >
  E0 self-validation: mọi `operation_id`, mã lỗi, tên entity và tên state được trích trong file này phải tồn tại
  trong ports.yaml / errors.yaml / entities.yaml / state/storage.yaml (script EV-PC08-01). EV-PC08-02 đối chiếu
  cơ chế session ở §2.3 với `components.securitySchemes` của `contracts/http/openapi.yaml` — **đã chạy, PASS**:
  cả sáu tên scheme khớp và cơ chế hội tụ. Không có evidence E1–E4; không có backup/restore thật nào được chạy.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Secrets, xác thực và audit

> Mọi con số trong file này mang nhãn `PROVISIONAL` đều có đơn vị và một dòng lý do. Chúng là tham số cấu hình,
> không phải hằng số nghiệp vụ, và cần Owner xác nhận trước khi coi là đã chốt.

## 1. Nguyên tắc

| ID | Nguyên tắc |
| --- | --- |
| `SEC-P1` | App ra Internet nên **một người dùng không đồng nghĩa không cần bảo vệ** (REQ-S11.1-01). Mọi mutation dữ liệu authoritative đi qua domain port đã xác thực (I01). |
| `SEC-P2` | Secret **không bao giờ** rời khỏi nơi nó thuộc về: key AI ở secret store server; token collector ở file cấu hình máy cá nhân; phiên X trong profile Chrome; không thứ nào trong số đó đi ngược chiều (REQ-S11.2-01…03). |
| `SEC-P3` | Nội dung nguồn là **dữ liệu**. Không nội dung nào từ post/abstract/toàn văn được đọc secret, gọi tool hay đổi recipient (REQ-S11.4-03, I11). |
| `SEC-P4` | Quyền là **giao** của mọi tầng: auth scope ∩ capability tiến trình ∩ network egress ∩ filesystem scope (`capabilities.yaml` CAP-P2). Không nới một tầng để bù tầng khác. |
| `SEC-P5` | Không có secret nào là **bắt buộc**: nếu gắn nhãn và summary chạy hết qua CLI/ACP thì hệ thống chạy với không key nào (D51, AC-16). Thiết kế secret không được phá tính chất này. |
| `SEC-P6` | Che log **trước khi ghi**, không phải khi hiển thị (REQ-S11.2-05). Một secret đã vào file log là đã lộ. |

## 2. Xác thực chủ sở hữu

### 2.1 Tài khoản

Đúng **một** tài khoản (`owner`, entity của `MOD-auth-service`). **Không** có trang signup, **không** có
quên-mật-khẩu tự động (D05, REQ-S11.1-01). Khôi phục truy cập là thao tác vận hành tại chỗ: Operator đặt lại
credential bằng công cụ trên server, ghi vào `secret_audit`. Không có kênh email/SMS nào — thêm kênh khôi phục là
thêm bề mặt tấn công cho một hệ một người dùng.

### 2.2 Băm mật khẩu

| Tham số | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| Thuật toán | Argon2id | PROVISIONAL | Hàm băm mật khẩu có memory-hard, là lựa chọn mặc định hiện đại; chống GPU tốt hơn PBKDF2. |
| `memory_cost` | 64 | MiB · PROVISIONAL | Đủ nặng cho tấn công offline, đủ nhẹ để server nhỏ đăng nhập trong < 1 s. |
| `time_cost` | 3 | lượt · PROVISIONAL | Cân bằng với `memory_cost` ở trên theo khuyến nghị phổ biến. |
| `parallelism` | 1 | luồng · PROVISIONAL | Một người dùng, không có tải đăng nhập đồng thời. |
| `salt` | 16 | byte ngẫu nhiên · PROVISIONAL | Mỗi bản ghi một salt riêng. |

Không lưu mật khẩu gốc ở bất kỳ đâu. Đổi tham số băm là thay đổi hợp đồng (rehash lúc đăng nhập thành công kế tiếp).

### 2.3 Session

**Lựa chọn PROVISIONAL:** cookie **HttpOnly + Secure + SameSite=Lax** mang session token, cộng **CSRF
double-submit token** cho mọi request mutation.

Lý do chọn cookie thay vì bearer trong localStorage: bearer trong JavaScript-accessible storage bị đánh cắp bởi bất
kỳ lỗ XSS nào; HttpOnly cookie thì không. Đổi lại, cookie tự động đính kèm nên phải chống CSRF — do đó có
double-submit. Đây là đánh đổi có ý thức, không phải mặc định.

| Tham số | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| Độ dài token | 256 | bit ngẫu nhiên · PROVISIONAL | Không đoán được; lưu trong DB dưới dạng `sha256` (`session.token_hash`), không lưu bản rõ. |
| `idle_timeout` | 12 | giờ · PROVISIONAL | Đủ dài để dùng trên điện thoại trong ngày (D04), đủ ngắn để máy bỏ quên không mở phiên vô hạn. |
| `absolute_timeout` | 30 | ngày · PROVISIONAL | Trần tuyệt đối; hết hạn là phải đăng nhập lại dù vẫn hoạt động. |
| `csrf_token_length` | 128 | bit · PROVISIONAL | Sinh cùng session, gửi qua cookie `rr_csrf` (đọc được bằng JS) **và** header `X-CSRF-Token`; server so khớp hai giá trị (double-submit). |
| `login_fail_threshold` | 5 | lần / 15 phút · PROVISIONAL | Chặn dò mật khẩu mà không khóa nhầm chủ nhà. |
| `lockout_duration` | 15 | phút · PROVISIONAL | Trả `RATE_LIMITED` kèm `retry_after`; không tiết lộ tài khoản có tồn tại hay không. |

Cấu trúc `session` (PC02): `token_hash`, `issued_at`, `expires_at`, `revoked_at`, `user_agent_redacted`.
`user_agent_redacted` là chuỗi **đã cắt** (họ trình duyệt + hệ điều hành), không lưu chuỗi UA đầy đủ — nó không
phục vụ mục đích nào ở đây ngoài chẩn đoán.

**Thu hồi.** `auth.logout` đặt `revoked_at`. Đổi mật khẩu thu hồi **mọi** session. Server kiểm `revoked_at` và
`expires_at` ở **mỗi** request, không tin hạn ghi trong cookie.

**Ghép với PC05 — đã đối chiếu.** `contracts/http/openapi.yaml` khai **cùng một** lựa chọn cơ chế. Tên chuẩn là
của PC05; file này dùng đúng các tên đó:

| Security scheme (PC05) | Cơ chế | Dùng cho |
| --- | --- | --- |
| `ownerSessionCookie` | cookie `rr_session`, HttpOnly + Secure + SameSite=Lax | Phiên của owner |
| `ownerCsrfToken` | header `X-CSRF-Token`, phải khớp cookie `rr_csrf` (không-HttpOnly) | **Mọi** mutation của owner session |
| `collectorToken` | bearer | `worker.*`, `ingest.*` |
| `analysisWorkerToken` | bearer | `analysis.*`, `secret.issue_task_credential` |
| `telegramIngressSecret` | header `X-Telegram-Bot-Api-Secret-Token` | Ingress webhook |
| `backupOperatorToken` | bearer | `backup.*` |

**Cách trích dẫn PC05 (cập nhật ở PKT-PC01-FIX4, `CR-PC01-08`).** Bản đầu của mục này pin một sha256 của
`openapi.yaml`; hash đó **đã cũ** ngay trong phiên vì PC05 tiếp tục nhận packet sửa. Một hash trỏ vào file đang
được viết song song tạo ra một trích dẫn tự-hỏng: nó sai ngay khi upstream đúng. Vì vậy mục này trích **bản
`contracts/http/openapi.yaml` được đóng băng ở candidate FC-W3** cùng **tên** các security scheme ở bảng trên —
tên scheme là thứ ổn định qua các bản sửa của PC05, còn hash thì không. Manifest của FC-W3 mang hash chính xác;
đó mới là nơi hash thuộc về.

**Đã được giải quyết:** khác biệt về mã lỗi cho CSRF. Ruling FIX3 đăng ký mã riêng **`CSRF_REJECTED`** (HTTP 403,
`scope: request`, `retry_class: none`, không đổi trạng thái) cho trường hợp thiếu hoặc lệch CSRF double-submit.
`FORBIDDEN_EDGE` giữ nguyên nghĩa "cạnh không có trong registry" và `UNAUTHORIZED` giữ nguyên nghĩa "danh tính chưa
được xác lập hoặc sai lớp principal". `CR-PC08-03` khép lại; PC03 đăng ký mã trong `contracts/errors.yaml` và
`contracts/ports.yaml` mang nó ở 19 operation mutation của owner session.

### 2.4 Phơi ra Internet

- **TLS bắt buộc.** Không phục vụ HTTP thường; cookie có cờ `Secure`, nên phiên đăng nhập không hoạt động qua
  HTTP — đó là kết quả mong muốn.
- Reverse proxy đứng trước container `app` (xem `contracts/ops/deployment.md` §3). Proxy phải đặt
  `X-Forwarded-Proto` và **không** được chuyển tiếp header xác thực do client tự đặt.
- `health.get_liveness` là endpoint duy nhất không cần xác thực và chỉ trả `up` + schema version — không lộ cấu
  hình, tên provider hay chat ID (`ports.yaml`).
- Không có CORS cho origin lạ: web app cùng origin với API.

## 3. Token của collector và analysis worker

Hai token **tách rời** dù hai tiến trình chạy trên cùng một máy (`capabilities.yaml`: `collector_token` và
`analysis_worker_token`). Lý do: bán kính ảnh hưởng khác nhau — collector chạm dữ liệu thô X, analysis worker
chạm credential provider.

| Tham số | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| Độ dài | 256 | bit ngẫu nhiên · PROVISIONAL | Như session token; server lưu `sha256`, không lưu bản rõ. |
| Quyền file | `0600`, chủ sở hữu là user chạy worker | — | REQ-S11.2-02: "file cấu hình trên máy cá nhân với quyền hạn chế". Worker **từ chối khởi động** nếu quyền rộng hơn `0600` — một cảnh báo im lặng là vô dụng. |
| Vị trí | thư mục cấu hình của user trên máy cá nhân | — | **Không bao giờ trong repo** (REQ-S11.2-02). |
| `rotation_interval` | 180 | ngày · PROVISIONAL | Đủ dài để không phiền chủ máy; đủ ngắn để một token rò rỉ không sống mãi. |
| `rotation_overlap` | 24 | giờ · PROVISIONAL | Token cũ và mới cùng hiệu lực trong 24 h để xoay vòng không làm gãy một run đang chạy. |

**Quy trình xoay vòng:** (1) Owner sinh token mới trong app; (2) cả hai token hiệu lực trong `rotation_overlap`;
(3) Operator cập nhật file cấu hình trên máy cá nhân và khởi động lại worker; (4) token cũ bị thu hồi ngay khi
worker đăng ký lại thành công bằng token mới, hoặc tự hết hiệu lực khi hết overlap. Mọi bước ghi `secret_audit`.

**Thu hồi tức thì** dùng khi nghi ngờ lộ: token vô hiệu ngay, `worker.claim_assignment` trả `UNAUTHORIZED`, run
đang chạy chuyển theo `run.yaml` khi lease hết hạn. Thu hồi token **không** xóa dữ liệu đã ingest.

**Chống replay.** Mọi mutation từ worker mang `request_id`, `idempotency_key`, `payload_hash`, và khi đang giữ job
thì thêm `job_id`, `lease_id`, `lease_epoch` (SRC-PLAN §5.1). Server từ chối `lease_epoch` cũ bằng `STALE_LEASE`.
Token bị bắt lại và phát lại vẫn không commit được dữ liệu hai lần vì `idempotency_key` đã có receipt.

## 4. Secret store phía server

### 4.1 Lưu trữ

Mã hóa **envelope**: mỗi secret được mã hóa bằng một data key riêng; data key được mã hóa bằng **master key**.

| Tham số | Giá trị | Trạng thái | Lý do |
| --- | --- | --- | --- |
| Thuật toán | AEAD 256-bit (AES-256-GCM hoặc XChaCha20-Poly1305) | PROVISIONAL | AEAD cho cả bí mật lẫn toàn vẹn; chọn cụ thể khi chốt stack (ADR-0006, Option A Python). |
| Nguồn master key | biến môi trường của container, hoặc file `0400` mount vào container | PROVISIONAL | Không nằm trong DB (nếu nằm cùng DB thì mã hóa vô nghĩa khi mất file DB), không nằm trong repo. |
| Nơi lưu ciphertext | bảng của `MOD-secret-service`, trỏ bằng `secret_ref.store_locator` | — | `secret_ref` chỉ giữ **tham chiếu + trạng thái**, không giữ giá trị (PC02). |

**Hệ quả phải nói thẳng:** master key nằm ngoài DB nên **backup file DB không chứa key**; mất master key là mất
mọi secret dù backup còn nguyên. Đó là lý do §5 của `backup-restore.md` yêu cầu một *secret recovery plan* riêng.

### 4.2 Truy cập

Chỉ `MOD-secret-service` đọc được giá trị. Đường vào duy nhất là ba operation của `ports.yaml`:
`secret.store_provider_key` (nội bộ, từ `MOD-settings-service`), `secret.issue_task_credential` (http, từ analysis
worker), `secret.revoke_task_credential` (nội bộ). Không operation nào **trả về** giá trị key cho frontend:
`settings.get_config` chỉ trả tham chiếu và trạng thái đã cấu hình.

| Ai | Được gì | Mã lỗi khi vượt |
| --- | --- | --- |
| `ACT-owner-session` | Ghi key mới, xem *đã cấu hình hay chưa* | `UNAUTHORIZED` (denied case `NC-03`) |
| `ACT-analysis-worker` | Credential ngắn hạn của **một** provider cho task đang giữ lease | `UNAUTHORIZED` |
| `ACT-collector` | Không gì cả | `UNAUTHORIZED` (`FE-09`) |
| `ACT-telegram-ingress` | Chỉ bot token của chính nó | `UNAUTHORIZED` (`FE-32`) |
| Mọi domain service khác | Không gì cả | `CAPABILITY_DENIED` (`DC-SRV-02`) |

### 4.3 Che secret trong log

Che **trước khi ghi**. Bộ lọc chạy trên mọi đường ghi log, kể cả log lỗi và transcript của adapter CLI.

| Lớp | Mẫu | Thay bằng |
| --- | --- | --- |
| Giá trị đã biết | mọi plaintext secret đang nạp trong tiến trình | `[REDACTED:<purpose>]` |
| Header | `Authorization`, `Cookie`, `Set-Cookie`, `X-CSRF-Token`, `X-Telegram-Bot-Api-Secret-Token` | `[REDACTED:header]` |
| Dạng token | chuỗi ≥ 24 ký tự trong tập base64url/hex không có khoảng trắng | `[REDACTED:token-like]` |
| Tiền tố nhà cung cấp | ví dụ `sk-`, `xoxb-`, `ghp_` theo cấu hình provider | `[REDACTED:provider-key]` |
| Transcript CLI/ACP | toàn bộ transcript **không** được ghi ở mức mặc định | chỉ ghi JSON đã bóc + phân loại lỗi |

Bộ lọc theo mẫu là **lưới an toàn thứ hai**, không phải hàng phòng thủ chính: hàng phòng thủ chính là không đưa
secret vào chuỗi log ngay từ đầu. Không dùng "đã có redaction" để biện minh cho việc log một cấu trúc chứa key.

Điều **không bao giờ** được ghi: giá trị key, session/CSRF token, bot token, mã liên kết Telegram, nội dung cookie,
đường dẫn tuyệt đối tới profile Chrome kèm dữ liệu phiên.

## 5. Phân phối secret theo từng task (B13 / ADR-0010)

Analysis worker chạy trên máy cá nhân và **không** nhận secret store. Nó nhận một `task_credential` gắn với một
assignment (PC02: `assignment_id`, `secret_ref_id`, `issued_to_worker_identity`, `expires_at`, `revoked_at`).

| Ràng buộc | Nội dung |
| --- | --- |
| Phạm vi | Đúng **một** `secret_ref`, của đúng provider mà task đó cần. Không cấp cho provider khác, không cấp gói. |
| Điều kiện cấp | Worker phải đang giữ lease hợp lệ của chính task đó; `lease_epoch` cũ ⇒ `STALE_LEASE`. |
| `task_credential_ttl` | **900 giây** (PROVISIONAL) — bằng `lease_ttl_analysis` của `contracts/retry-policy.yaml`. Lý do: credential không được sống lâu hơn quyền làm việc mà nó phục vụ; dài hơn thì lease đã mất mà credential vẫn dùng được, ngắn hơn thì một lần gọi model dài sẽ đứt giữa chừng. |
| Thu hồi | Tại `analysis.submit_result`, `analysis.report_attempt_unknown`, khi lease hết hạn, khi run bị cancel, hoặc khi Owner thu hồi provider — qua `secret.revoke_task_credential`. |
| Lưu trữ ở worker | **Chỉ trong bộ nhớ tiến trình.** Không ghi ra đĩa, không vào biến môi trường của tiến trình con dùng chung, không vào log, không vào file tạm. |
| Sau khi dùng | Xóa khỏi bộ nhớ ngay khi lời gọi inference kết thúc. |

**Điều hợp đồng này KHÔNG bảo đảm** (nói thẳng, khớp với phần "không bảo đảm" mà PC02 ghi cho bảng
`task_credential`): nó không
ngăn được một worker đã bị chiếm quyền sao chép credential trong thời gian nó hợp lệ. Cái nó bảo đảm là **bán kính
thiệt hại**: một provider, một task, 900 giây.

### 5.1 Đường CLI/ACP

Đường này **không nhận secret nào từ server** (REQ-S10.2-02): xác thực là phiên đăng nhập của owner trên máy cá
nhân. Do đó:

- `secret.issue_task_credential` **không** được gọi cho task chạy qua CLI — không có gì để cấp.
- Adapter chạy với tool/file/network **bị khóa** ngoài phần inference (ADR-0010, `DC-AI-01…05`).
- Provider nào không kiểm chứng được cô lập (`isolation_verified: false`) thì adapter giữ trạng thái `disabled`
  và worker khai `usable: unusable` với `reason_code: isolation_unverified` — **không** bật "để thử".
- Điều khoản của từng nhà phải được đọc trước khi bật (REQ-S13.2-02, A5); `policy_reviewed: false` ⇒ không bật.

Đây là điều làm cho luồng **không có API key nào** (AC-16) vẫn an toàn: không phải vì không có secret, mà vì đường
không có secret cũng bị khóa quyền y hệt.

## 6. Máy cá nhân: Chrome và phiên X

| Mục | Quy tắc | Nguồn |
| --- | --- | --- |
| Profile | Profile **riêng của dự án**, không dùng profile mặc định của người dùng | D09, REQ-S11.2-03 |
| Cổng debug | Chỉ bind `127.0.0.1`; **không bao giờ** mở ra LAN hay đặt sau reverse proxy | REQ-S11.2-06 |
| Phiên X | Ở lại trong profile trên máy cá nhân; **không bao giờ** đồng bộ lên server | REQ-S11.2-03 |
| Backup | Profile **không** nằm trong backup của server; xem `backup-restore.md` §6 | ADR-0005 điểm 3 |
| Cổng vào | Máy cá nhân **không lắng nghe** cổng nào; mọi kết nối là outbound | REQ-S6.4-03 |

Hệ quả khi khôi phục: sau restore, chủ máy phải **đăng nhập X lại bằng tay** trong profile của dự án. Đó là công
việc thủ công đã biết trước, không phải sự cố.

## 7. Telegram

| Secret | Nơi lưu | Quy tắc |
| --- | --- | --- |
| Bot token | Secret store server, `secret_ref.purpose = telegram_bot` | Chỉ `MOD-telegram-adapter` dùng; không xuất hiện trong log hay tin nhắn |
| Webhook secret | Secret store server | Gửi trong header bí mật của mỗi update; sai ⇒ `UNAUTHORIZED`, không xử lý gì |
| Mã liên kết | `telegram_link_code` | **Dùng một lần, có hạn** (REQ-S11.2-04, REQ-S11.3-01). Dùng lại ⇒ `UNAUTHORIZED_COMMAND` và im lặng phía chat |

Endpoint ingress đặt ở đường dẫn khó đoán **và** kiểm header bí mật — đường dẫn khó đoán một mình không phải xác
thực. Tin từ chat chưa liên kết bị **bỏ im lặng** (REQ-S11.3-02, AC-18); ngoại lệ hẹp duy nhất là chuỗi đúng định
dạng mã liên kết (B09). Chi tiết lệnh và liên kết thuộc `contracts/telegram/commands.yaml` (PC07, chưa tồn tại).

## 8. Audit log

| Trường | Nội dung |
| --- | --- |
| Ghi cái gì | Đăng nhập thành công/thất bại; thu hồi session; ghi/xoay/thu hồi secret (`secret_audit`); cấp và thu hồi `task_credential`; đăng ký và thu hồi token worker; sinh/dùng/hủy mã liên kết Telegram; `data.delete_target` và `data.purge_all` (`data_deletion_audit`); mọi thao tác `backup.*`; mỗi lần từ chối vì `UNAUTHORIZED` / `CAPABILITY_DENIED` / `FORBIDDEN_EDGE`. |
| Ghi cái gì **không** | Giá trị secret; nội dung post/abstract; transcript CLI; UA đầy đủ. |
| Trường bắt buộc | `at` (UTC ms), `actor_module`, `action`, tham chiếu đối tượng, `outcome_detail_safe`, `correlation_id`. |
| Retention | **365 ngày** cho `secret_audit` (PROVISIONAL — đủ để điều tra một sự cố phát hiện muộn, không giữ vô hạn một bản ghi chỉ có giá trị chẩn đoán). `data_deletion_audit` giữ **vô thời hạn** (PROVISIONAL) vì nó là bằng chứng cho biết dữ liệu đã mất là do chủ ý, đồng thời khớp D58 (retention vô thời hạn). |
| Khi DB không ghi được | Không tuyên bố đã persist audit. `storage.health = write_blocked` ⇒ từ chối mutation, báo qua kênh health độc lập (SRC-PLAN §8.4, `errors.yaml` §EPR-01). |

## 9. Quan hệ với `data.purge_all`

`data.purge_all` chỉ chạy trong `storage.health = maintenance` (`contracts/state/storage.yaml`; `ports.yaml`).
Phần thuộc file này:

- Cụm từ xác nhận được lưu dưới dạng **hash** (`purge_challenge.phrase_hash`), không lưu bản rõ; tối đa một
  challenge hiệu lực tại một thời điểm (PC02 `ux_purge_challenge_active`).
- Phạm vi **đã chốt** (OD-20260907-01 mục 24). Ba tập bảng theo ruling CR-PC05-06 + CR-PC05-07 (`PURGE-LIST-ruling.md`),
  phủ đúng 60 entity và không chồng lấn: **xóa 37** bảng dữ liệu nghiên cứu và vận hành;
  **giữ 21**: `owner`, `session`, `secret_ref`, `task_credential`, `secret_audit`, `telegram_link`, `telegram_link_code`, `provider_config`, `provider_test_result`, `settings`, `schedule_occurrence`, `tag`, `tag_alias`, `tag_exclusion`, `tag_config_version`, `source_connection`, `backup_snapshot`, `backup_manifest`, `restore_record`, `purge_challenge`, `worker_registration`; **không bao giờ xóa 2**: `schema_migration`, `data_deletion_audit`.
  Nhóm secret nằm trong nhóm giữ: `secret_ref`, `task_credential`, `secret_audit` **được giữ** — purge **không**
  làm mất API key, và `owner` + `session` cũng được giữ nên chủ nhà **không** tự khóa mình ra ngoài app. Đây chính
  là rủi ro mà bản trước của mục này nêu ra; Owner đã chọn phương án loại bỏ nó.
- Nhật ký `secret_audit` được giữ **có chủ đích**: xóa audit cùng lúc với xóa dữ liệu sẽ làm mất bằng chứng kiểm
  toán về việc ai đã chạm secret (I11).
- Purge **không** chạm tới backup artifact đã tạo (`backup_snapshot`, `backup_manifest`, `restore_record` đều
  nằm trong nhóm giữ lại). Hộp thoại xác nhận **phải nói rõ** rằng dữ liệu vừa xóa **vẫn còn trong các bản
  backup** cho tới khi chúng hết hạn theo retention hoặc bị xóa bằng tay; xóa hẳn là một thao tác riêng — xem
  `backup-restore.md` §8 và §8.1.

## 10. Những gì file này **không** quyết định

| Chủ đề | Sở hữu |
| --- | --- |
| Wire HTTP, tên header, mã trạng thái, security scheme cụ thể | PC05 `contracts/http/openapi.yaml` |
| Capability của từng adapter AI, probe cô lập theo provider | PC06 `contracts/ai/providers.yaml` |
| Lệnh Telegram, lifecycle liên kết, validate callback | PC07 `contracts/telegram/commands.yaml` |
| Bảng transition của `storage.health`, mã lỗi | PC03 |
| Danh mục operation, module, capability theo actor | PC01 (đóng băng với packet này) |
| Ngôn ngữ/thư viện cụ thể để hiện thực băm và AEAD | PC10 sau khi chốt stack (ADR-0006 PROVISIONAL) |
