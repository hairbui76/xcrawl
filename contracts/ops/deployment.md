---
contract_id: CT-ops-deployment
version: 0.1.0
status: draft
owner_role: architecture owner
source_refs:
  - SRC-SPEC §6.1
  - SRC-SPEC §6.4
  - SRC-SPEC §10.1
  - SRC-SPEC §11.2
  - SRC-PLAN §6
  - SRC-PLAN §8.4
  - SRC-PLAN §11 PC01
requirement_refs:
  - REQ-D04
  - REQ-D06
  - REQ-S6.1-01
  - REQ-D07
  - REQ-D08
  - REQ-D09
  - REQ-D11
  - REQ-D12
  - REQ-D42
  - REQ-D50
  - REQ-P0-03
  - REQ-P0-12
  - REQ-AC15
  - REQ-AC16
decision_refs: [B02, B08, B11, B12, B13, ADR-0001]
invariant_refs: [I01, I02, I10, I11, I13, I15]
producers: [MOD-backend-api, MOD-health-service]
consumers: [MOD-web-ui, MOD-x-collector, MOD-analysis-worker, MOD-backup-cli]
dependencies:
  - contracts/modules.yaml
  - contracts/capabilities.yaml
  - contracts/ports.yaml
scope: >
  Mô hình triển khai của Research Radar: nơi chạy từng module, Docker hay tiến trình trên máy, cổng và binding,
  chiều kết nối, định nghĩa readiness cho từng module, thứ tự khởi động, định nghĩa "collector online", luồng đăng
  ký capability và quy tắc tương thích phiên bản. Không định nghĩa lifecycle secret (PC08), không định nghĩa state
  machine (PC03), không định nghĩa wire schema (PC05).
verification: >
  E0 self-validation: đọc chéo với contracts/modules.yaml và contracts/ports.yaml (module, operation, network scope
  khớp nhau). Không có evidence E1–E4; mọi số PROVISIONAL chưa được đo trên hệ thống thật — NOT_RUN.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Triển khai, readiness và capability registration

## 1. Hai môi trường chạy

| Runtime | Nội dung | Hình thức | Chiều kết nối |
| --- | --- | --- | --- |
| `RT-server` | web + backend + queue + embedding + SQLite | **Docker**; SQLite là file trên volume (SRC-SPEC §6.4) | Nhận HTTPS từ Internet; gọi ra arXiv/OpenAlex/Telegram |
| `RT-personal-machine` | `MOD-x-collector`, `MOD-analysis-worker`, `MOD-ai-adapter` | **Tiến trình trên máy, không container** | **Chỉ outbound**; không mở cổng vào (SRC-SPEC §6.4) |
| `RT-browser` | `MOD-web-ui` | Tải từ server | Chỉ tới origin của app |

Lý do máy cá nhân không dùng container: Chrome phải hiện cửa sổ cho người dùng bấm xác minh (D09) và CLI/ACP cần
phiên đăng nhập của chính người dùng (D42). Đây là ràng buộc sản phẩm, không phải lựa chọn tiện tay.

## 2. Bố trí module

| Module | Runtime | Tiến trình | Ghi chú |
| --- | --- | --- | --- |
| `MOD-web-ui` | RT-browser | — | Truy cập được từ ngoài mạng nhà, mở trên điện thoại (D04) |
| `MOD-backend-api` | RT-server | container `app` | Edge HTTP: TLS, xác thực, redaction, định tuyến |
| `MOD-auth-service` | RT-server | container `app` | Modular monolith được phép (SRC-PLAN §6) |
| `MOD-settings-service` | RT-server | container `app` | |
| `MOD-tag-service` | RT-server | container `app` | |
| `MOD-scheduler` | RT-server | container `app`, luồng riêng | Chỉ gọi job service |
| `MOD-job-service` | RT-server | container `app` | Sở hữu run/assignment/lease |
| `MOD-ingest-service` | RT-server | container `app` | Điểm vào duy nhất của dữ liệu thu thập |
| `MOD-identity-service` | RT-server | container `app` | |
| `MOD-research-connector` | RT-server | container `app` | Gọi arXiv/OpenAlex qua API (D32) |
| `MOD-analysis-service` | RT-server | container `app` | Task authority; worker chỉ đề xuất |
| `MOD-report-service` | RT-server | container `app` | |
| `MOD-saved-service` | RT-server | container `app` | |
| `MOD-delivery-service` | RT-server | container `app`, dispatcher là luồng riêng | Outbox |
| `MOD-telegram-adapter` | RT-server | container `app` | Ingress webhook + gửi ra |
| `MOD-secret-service` | RT-server | container `app` | Module duy nhất đọc giá trị key |
| `MOD-health-service` | RT-server | container `app`, đường xử lý tách khỏi DB | Phải trả lời được khi DB không ghi được |
| `MOD-embedding-service` | RT-server | container `embedding` **riêng** | Model local; tách container để giới hạn tài nguyên và để egress allowlist rỗng |
| `MOD-data-admin-service` | RT-server | container `app` | Sở hữu hai mutation phá hủy của §7.3; chỉ chạy `data.purge_all` khi `storage.health = maintenance` |
| `MOD-data-store` | RT-server | file trên volume | Không có cổng mạng; sở hữu `schema_migration` (ghi bởi migration lúc khởi động, không bởi operation nào) |
| `MOD-backup-service` | RT-server | container `app` | Có maintenance guard |
| `MOD-backup-cli` | RT-server | tiến trình CLI khi cần | Gọi qua loopback bằng `backup_operator` |
| `MOD-x-collector` | RT-personal-machine | tiến trình trên máy | Điều khiển Chrome profile riêng |
| `MOD-analysis-worker` | RT-personal-machine | tiến trình trên máy | Cùng máy với collector (D42) |
| `MOD-ai-adapter` | RT-personal-machine | trong tiến trình worker | Tool/file/network bị khóa ngoài inference (B13) |

Bảng trên hiện thực **REQ-S6.1-01** (SRC-SPEC §6.1: phân vai theo nơi chạy — web app, backend/API, job queue,
data store, embedding, report builder, Telegram adapter, research sources ở **server**; X collector, analysis
worker và AI adapter ở **máy cá nhân**). Mỗi dòng §6.1 của đặc tả có đúng một module ở đây, và cột "Runtime" là
nơi chạy mà đặc tả quy định.

**Modular monolith:** các module ghi "container `app`" chạy chung một tiến trình. Ranh giới của chúng vẫn là ranh
giới **quyền và ownership**: `allowed_edges` trong `contracts/modules.yaml` được thực thi bằng import/dependency
rules chứ không bằng ranh giới mạng (SRC-PLAN §6).

## 3. Cổng và binding

| Điểm | Binding | Giá trị | Lý do |
| --- | --- | --- | --- |
| App HTTPS | `0.0.0.0:443` (qua reverse proxy của server) | 443/TCP | D04 yêu cầu truy cập từ ngoài mạng nhà |
| App container | loopback của mạng Docker | `8080/TCP` (PROVISIONAL) | Chỉ reverse proxy chạm tới; không expose ra host |
| Embedding container | mạng nội bộ Docker | `8090/TCP` (PROVISIONAL) | Chỉ container `app` gọi; **egress ra Internet rỗng** (FE-22) |
| SQLite | file trên volume | — | Không có cổng; không tiến trình ngoài server mở được (NC-05) |
| Telegram ingress | đường dẫn webhook bí mật trên cùng 443 | — | Xác thực bằng `telegram_ingress_secret` |
| Chrome remote debugging | **`127.0.0.1` (loopback) duy nhất** | `9222/TCP` (PROVISIONAL) | SRC-SPEC §11.2: không bao giờ mở ra LAN hay reverse proxy |
| Collector / analysis worker | **không lắng nghe cổng nào** | — | Máy cá nhân không mở cổng vào (SRC-SPEC §6.4) |

Các giá trị cổng ghi PROVISIONAL là mặc định cấu hình được, không phải hằng số nghiệp vụ; đổi chúng không cần
amendment, nhưng **binding loopback của Chrome là ràng buộc bảo mật, không được đổi** mà không có quyết định của
Owner.

## 4. Chiều kết nối

```
Internet ──HTTPS 443──> [reverse proxy] ──> app container
Telegram ──HTTPS 443 (webhook path bí mật)──> telegram ingress
app container ──HTTPS──> api.telegram.org, arXiv, OpenAlex
personal machine ──HTTPS (outbound)──> app container
personal machine ──HTTPS (outbound)──> endpoint provider AI đã cấu hình
personal machine ──loopback──> Chrome debug 127.0.0.1
(không có mũi tên nào đi VÀO personal machine)
```

Hệ quả kiểm chứng được: mọi việc đến với collector đều do collector **kéo** (`worker.claim_assignment`, D11).
Scheduler không có đường đẩy việc xuống máy cá nhân (FE-26).

## 5. Định nghĩa readiness theo từng module

`health.get_readiness` trả trạng thái của từng mục dưới đây. Ba trạng thái `ok | degraded | down` phải phân biệt
được với "không có dữ liệu" trên giao diện (I13).

| Mục readiness | `ok` khi | `degraded` khi | `down` khi |
| --- | --- | --- | --- |
| `storage` | `storage.get_health` = `healthy` | `maintenance` | `write_blocked` hoặc `recovery_required` |
| `scheduler` | tick gần nhất ≤ 2× chu kỳ tick | trễ 2–5× chu kỳ | trễ > 5× chu kỳ hoặc luồng chết |
| `job_dispatch` | cấp assignment được | có worker nhưng thiếu capability | `storage` không `healthy` |
| `delivery_dispatcher` | chạy và `storage` = `healthy` | có part `unknown` chờ quyết định của operator | bị khóa vì `recovery_required` (I15) |
| `embedding` | có `active_generation` và service trả lời | đang `building` generation mới | không có generation active |
| `research_sources` | `research.get_connector_health` = `ok` cho ít nhất một nguồn | một nguồn `degraded` | mọi nguồn `unavailable` |
| `telegram_link` | có một liên kết hiệu lực | chưa liên kết (chưa cấu hình xong) | ingress không xác thực được |
| `collector` | xem §6 | `x_session_state` ∈ {`challenge_required`, `expired`} | offline theo §6 |
| `analysis_worker` | online và có ít nhất một provider `usable` cho mỗi task đang bật | mọi provider `unknown` | offline hoặc mọi provider `unusable` |

**Ràng buộc bắt buộc (SRC-PLAN §8.4):** `health.get_liveness` phải trả lời được **kể cả khi SQLite không ghi được**.
Vì vậy `MOD-health-service` giữ ảnh chụp readiness trong bộ nhớ và không cần ghi DB để trả lời. Nếu không ghi được
trạng thái lỗi vào DB thì hệ thống **không** được tuyên bố đã persist lỗi; kênh health là nơi duy nhất báo điều đó.

## 6. "Collector online" nghĩa là gì

Trạng thái hiển thị ở màn hình Runs (D11) do **server** tính, không lấy trực tiếp từ lời khai của worker.

| Tham số | Giá trị | Đơn vị | Lý do |
| --- | --- | --- | --- |
| `heartbeat_interval` | 30 | giây | PROVISIONAL. Đủ nhỏ để phát hiện máy tắt trong vòng vài chục giây, đủ lớn để không tạo tải vô ích cho một hệ một người dùng. |
| `online_threshold` | 90 | giây | PROVISIONAL. Bằng 3 × `heartbeat_interval`: chịu được hai lần lỡ nhịp do mạng nhà chập chờn trước khi báo offline. |
| `registration_refresh_interval` | 900 | giây | PROVISIONAL. Đăng ký lại capability định kỳ để trạng thái provider CLI không bị cũ quá 15 phút. |
| `registration_stale_after` | 1800 | giây | PROVISIONAL. Bằng 2 × `registration_refresh_interval`; quá hạn thì capability chuyển `unknown`, không giữ giá trị cũ. |

Định nghĩa:

- **online** — có `worker.register_capabilities` hợp lệ **và** heartbeat gần nhất trong vòng `online_threshold`
  **và** `storage` của server đang nhận được mutation. Chỉ khi online thì worker mới được cấp assignment.
- **offline** — không thỏa điều kiện trên. Offline **không** phải lỗi: máy tắt là tình huống bình thường, các đợt
  quá hạn sẽ được gộp khi máy thức (D15, AC-02).
- **needs_user** là trạng thái của **run**, không phải của worker: worker có thể online trong khi run đang chờ
  người xử lý CAPTCHA (B02/AMD-B02).

`last_run` chỉ để xem, **không** dùng làm mốc lọc dữ liệu (D12). Ngưỡng ở trên là PROVISIONAL cho tới khi có số
thật từ probe A1 (SP1); chúng là tham số cấu hình, đổi không cần amendment.

## 7. Luồng đăng ký capability

```
1. Worker khởi động
2. Worker đọc file cấu hình token (quyền hạn chế) trên máy cá nhân
3. Worker tự kiểm cục bộ:
     collector : profile Chrome riêng mở được?  phiên X ở trạng thái nào?
     analysis  : ai.probe_provider_capability cho từng provider đã cấu hình
4. Worker gọi worker.register_capabilities (outbound, HTTPS)
     - khai embedding_supported = false (luôn luôn)
     - khai từng provider: usable | unusable | unknown + reason_code
5. Server ghi bản đăng ký, trả về heartbeat_interval yêu cầu
6. Worker gọi worker.claim_assignment / analysis.claim_task khi muốn nhận việc
     - đăng ký KHÔNG cấp lease; lease chỉ đến từ claim (I10)
7. Worker gửi heartbeat theo chu kỳ; mất heartbeat quá online_threshold ⇒ offline
8. Lặp lại bước 3–4 mỗi registration_refresh_interval, hoặc ngay khi trạng thái đổi
   (ví dụ phiên X chuyển challenge_required)
```

Điểm bắt buộc:

- Server **từ chối** bản đăng ký khai `embedding_supported: true` bằng `VALIDATION_ERROR`. Đây là guard cho D50/B12:
  embedding không bao giờ chạy trên máy cá nhân.
- `usable: unknown` được đối xử như **không dùng được** khi quyết định giao việc, nhưng hiển thị khác `unusable`
  (I13). Không quy đổi `unknown` thành `usable`.
- Đường CLI/ACP là **nguồn sự thật duy nhất từ máy cá nhân**: `settings.test_provider` chạy ở server nên chỉ thử
  được đường API key.
- `isolation_verified: false` ⇒ adapter của provider đó giữ trạng thái `disabled`; không bật "để thử" (B13).

## 8. Thứ tự khởi động

Trên server:

1. `MOD-data-store` sẵn sàng (file DB mở được, integrity check nhanh) → nếu không: `storage.health` ≠ `healthy`,
   dừng ở bước này.
2. `MOD-health-service` (phải sống trước, để báo được các lỗi ở bước sau).
3. `MOD-secret-service`, `MOD-auth-service`, các domain service, `MOD-backend-api`.
4. `MOD-embedding-service`; kiểm có `active_generation`.
5. `MOD-scheduler` và `MOD-delivery-service` dispatcher — **hai module cuối cùng**, vì chúng tạo side effect.

Chế độ `maintenance`: `data.purge_all` chỉ chạy khi `storage.health = maintenance` — scheduler và dispatcher đã dừng,
mọi `assignment_lease` bị thu hồi trước khi xóa, và sau khi xóa hệ thống **ở lại** `maintenance` cho tới khi owner
mở lại; không tự resume (cùng nguyên tắc NC-10).

Quy tắc dừng: nếu `storage.health` = `recovery_required` (sau restore), bước 5 **không** được khởi động cho tới khi
`backup.reconcile_after_restore` thành công (I15, NC-10). Dispatcher và cấp assignment đều đọc `storage.get_health`
trước mỗi lần hành động, không chỉ lúc khởi động.

Trên máy cá nhân: collector và analysis worker độc lập nhau; cả hai chỉ cần server ở trạng thái nhận được
`worker.register_capabilities`. Thứ tự giữa chúng không quan trọng vì không có edge trực tiếp giữa hai tiến trình
(FE-08).

## 9. Tương thích phiên bản

- **Security scheme trên wire** (PC05 sở hữu tên; ghi ở đây để vận hành đối chiếu được):
  `ownerSessionCookie` + `ownerCsrfToken` cho mọi mutation của owner session — thiếu CSRF ⇒ `CSRF_REJECTED` (403);
  `collectorToken` / `analysisWorkerToken` (bearer) cho máy cá nhân; `telegramIngressSecret` cho ingress webhook;
  `backupOperatorToken` cho cả bốn `backup.*`. Xem `contracts/ports.yaml` §`conventions.auth_scope_to_wire_scheme_vi`
  và `contracts/ops/secrets.md` §2.3.
- Mọi mutation từ worker mang `schema_version` (SRC-PLAN §5.1). Server chấp nhận `schema_version` trong tập nó hỗ
  trợ; lệch phiên bản trả `VALIDATION_ERROR` với `details_safe` nêu phiên bản được hỗ trợ, **không** tự đoán và
  **không** im lặng bỏ trường lạ.
- `agent_version` của worker được ghi lại để chẩn đoán, nhưng quyết định tương thích dựa trên `schema_version`.
- Nâng cấp server trước, worker sau: server phải chấp nhận `schema_version` cũ trong ít nhất một thế hệ để máy cá
  nhân có thể đang tắt lúc nâng cấp. Chính sách deprecate cụ thể do PC05 chốt cùng `contracts/http/openapi.yaml`.
- Đổi `schema_version` của một operation là thay đổi hợp đồng: phải cập nhật `contracts/ports.yaml`, version của
  file liên quan và traceability (SRC-PLAN §16).

## 10. Ma trận ca âm (tham chiếu)

Mười ca âm bắt buộc của PC01 nằm trong `contracts/modules.yaml` khóa `denied_cases` (NC-01 … NC-10), mỗi ca có
edge bị thử, mã lỗi mong đợi, trạng thái mong đợi và cơ chế thực thi. Ở giai đoạn Pre-code chúng **chưa được chạy**:
trạng thái bằng chứng là `NOT_RUN`. Cơ chế thực thi được phân loại thành import rule, API auth test, process
capability, network egress allowlist, command allowlist và storage-health guard; PC09 gắn chúng vào scenario có
oracle.

## 11. Những gì file này **không** quyết định

| Chủ đề | Gói sở hữu |
| --- | --- |
| Lease TTL, heartbeat budget, retry budget, timeout từng operation | PC03 (`contracts/retry-policy.yaml`, `contracts/state/*.yaml`) |
| Wire HTTP, đường dẫn, mã trạng thái HTTP | PC05 (`contracts/http/openapi.yaml`) |
| Lifecycle secret, mã hóa at-rest, xoay vòng token, CSRF | PC08 (`contracts/ops/secrets.md`) |
| Quy trình backup/restore chi tiết, RPO/RTO | PC08 (`contracts/ops/backup-restore.md`) |
| Ngôn ngữ/stack và đường dẫn build | PC10 (stack là Option A PROVISIONAL, cần ADR + lựa chọn của Owner) |
