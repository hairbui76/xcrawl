# Owner runbook — chạy và tự kiểm Research Radar trên máy của bạn

> **Tài liệu này là gì.** Một hướng dẫn đầu-cuối để **Owner tự chạy** những gì repo này
> hiện có, theo đúng thứ tự. Nó không thay thế hợp đồng: mỗi bước dẫn ra file hợp đồng
> quyết định bước đó.
>
> **Tài liệu này KHÔNG nói sản phẩm chạy được.** Xem [§12](#12-điều-hệ-này-chưa-chứng-minh)
> trước khi kết luận bất cứ điều gì từ một lệnh chạy thành công.

Ngày viết: **2026-09-08**. Chạy lại và cập nhật: **2026-09-09**, đối chiếu commit
`feat: integration wiring` — mọi lệnh trong bản này được chạy lại trên đúng cây đã commit đó.
Uỷ quyền: Owner (`AUTH-OWNER-20260908-11`).
Bối cảnh trạng thái: [`README.md`](../README.md) §6, [`docs/master-plan.md`](master-plan.md),
[`precode/review.md`](../precode/review.md) §17.5–§17.7, và ba báo cáo audit
[`A3-P5-R1..R3`](../evidence/audits/).

---

## 0. Cách đọc tài liệu này

Mỗi lệnh trong tài liệu mang **một trong hai nhãn**:

| Nhãn | Nghĩa |
| --- | --- |
| **`đã chạy ở đây`** | Lệnh đã được chạy thật khi soạn tài liệu này, trên Linux, và dòng **`Kỳ vọng:`** ngay dưới nó mô tả **hình dạng output đã quan sát được**, không phải output tưởng tượng. |
| **`chưa chạy ở đây`** | Lệnh **không** được chạy khi soạn tài liệu, kèm lý do. Đó là những việc chạm mạng ngoài (X, Telegram, provider AI, registry gói) hoặc đòi một môi trường thật. Với những lệnh này, output mô tả là **suy ra từ mã nguồn**, và bạn là người đầu tiên quan sát nó thật. |

Máy dùng để kiểm: `uv 0.12.9`, `node v22.23.2`, `npm 10.9.8`, `Python 3.12.3`, môi trường
`.venv` đã cài sẵn (nên mọi lệnh Python dưới đây chạy được ở chế độ `--offline`).

**Chín khoảng trống** phát hiện trong lúc kiểm — những việc bạn **chưa làm được** vì thiếu
một mảnh — nằm ở [§11](#11-bảng-khoảng-trống--đã-đóng-và-còn-mở). Chúng được nhắc ngay tại bước liên quan, dưới
nhãn `KHOẢNG TRỐNG G-n`.

---

## 1. Chuẩn bị và cài đặt

Yêu cầu (`README.md` §1, [`precode/adr/ADR-0011`](../precode/adr/ADR-0011-frameworks-and-toolchain.md)):
**Python 3.12**, **[`uv`](https://docs.astral.sh/uv/)**, **Node 22**.

```bash
make setup
```

`Makefile` mở gói đó ra thành đúng hai lệnh: `uv sync --all-packages` rồi `cd web && npm ci`.

> **`chưa chạy ở đây`** — hai lệnh này gọi ra registry gói (PyPI, npm), là mạng ngoài; phạm vi
> soạn tài liệu không cho phép gọi. Môi trường trên máy kiểm **đã được cài từ trước**, và mọi
> lệnh `uv run --offline` ở các mục sau chạy được, nên phần *kết quả* của `make setup` là có
> thật; chỉ *lệnh cài* là chưa chạy trong phiên này.

Hai điều repo **cố tình không cài** (`README.md` §1):

- **Trình duyệt Playwright.** `uv run playwright install chromium` là việc trên **máy bạn**,
  chỉ cần cho probe X ở [§6](#6-probe-khả-thi-nguồn-x-sp1). Repo và CI không bao giờ chạy nó.
- **Model embedding** (`sentence-transformers`). Đó là extra khai sẵn ở `server/pyproject.toml`
  nhóm `embedding`, **không** được `uv sync --all-packages` cài, vì model cụ thể còn là
  `REQ-OQ09` chưa chốt.

Kiểm nhanh phiên bản — **`đã chạy ở đây`**:

```bash
uv --version && node --version && npm --version
```

**Kỳ vọng:** ba dòng phiên bản; `node` phải là `v22.x`.

---

## 2. Khởi tạo cơ sở dữ liệu

### 2.1 Nơi đặt file dữ liệu

`contracts/ops/deployment.md` §1 và §3: kho dữ liệu là **một file SQLite trên volume**, không
có cổng mạng, không tiến trình nào ngoài server mở được (`NC-05`). Trên máy cá nhân, chỗ quy
ước là `var/` trong repo — `.gitignore` đã loại `*.db`, `*.db-wal`, `*.db-shm` và `var/`, nên
dữ liệu máy **không bao giờ** thành nội dung repo.

`server/alembic.ini` **cố tình không ghi URL** vào repo: `server/migrations/env.py` đọc biến
môi trường `RR_DATABASE_URL` và **từ chối đoán** nếu biến đó trống.

### 2.2 Chạy migration từ một file trắng

> **`KHOẢNG TRỐNG G-4` — ĐÃ ĐÓNG** (`PKT-P0-FIX5`). `script_location = migrations` trong
> `server/alembic.ini` vẫn là đường dẫn **tương đối theo thư mục làm việc**, nên gọi `alembic`
> trần từ gốc repo vẫn trả `alembic.util.exc.CommandError: Path doesn't exist: migrations.`
> Điều đã đổi: có một lệnh **không** phụ thuộc cwd. `tools/rr_admin.py migrate` dựng config
> bằng đường dẫn tuyệt đối và đặt `RR_DATABASE_URL` quanh lần upgrade — đúng cách bộ test đã
> làm (`tests/integration/test_denied_edges.py::_migrate`). `server/alembic.ini` và
> `server/migrations/env.py` **không** bị sửa: việc `env.py` từ chối đoán vị trí database là
> đúng và được giữ nguyên.

Lệnh đúng — **`đã chạy ở đây`**, từ **gốc repo** (hoặc bất kỳ thư mục nào):

```bash
make migrate
# tương đương: uv run python tools/rr_admin.py migrate
```

Đường cũ vẫn dùng được nếu bạn muốn gọi thẳng alembic — **`đã chạy ở đây`**:

```bash
mkdir -p var
cd server && RR_DATABASE_URL=../var/research-radar.db uv run alembic upgrade head
```

**Kỳ vọng:** một chuỗi dòng `INFO [alembic.runtime.migration] Running upgrade …`, bắt đầu ở
`-> 0001, Initial empty baseline.` và kết thúc ở
`0012_tc_backup_restore_drill -> 0013_tc_backfill_pending_ledger`. Đúng **một** head; nếu
alembic báo "ambiguous head" thì đó là lỗi thật, không phải cấu hình sai của bạn
(`server/migrations/versions/0004`, `0007`, `0011` tồn tại chính là để giữ một head duy nhất —
xem `tests/contract/test_schema_matches_entities.py::test_alembic_has_exactly_one_head`).
Sau lệnh, file `var/research-radar.db` xuất hiện (khoảng 800 KB cho schema trống).

Kiểm lại — **`đã chạy ở đây`**:

```bash
cd server && RR_DATABASE_URL=../var/research-radar.db uv run alembic current
```

**Kỳ vọng:** một dòng revision, kết thúc bằng `(head)`.

*(Trên máy kiểm, lệnh được chạy với một đường dẫn tạm ngoài repo thay cho `var/…`; ngoài đường
dẫn, lệnh và output giống hệt.)*

---

## 3. Tạo tài khoản Owner duy nhất

`contracts/ops/secrets.md` §2.1 và `REQ-D05`: đúng **một** tài khoản, **không** trang signup,
**không** quên-mật-khẩu tự động. Đặt credential là "một thao tác vận hành tại chỗ".

Trong mã, việc đó là `AuthService.bootstrap_owner()` (`server/app/auth/service.py`), và
docstring của chính nó nói đây là **"CLI/console call"**, không có đường HTTP nào tới nó.

> ### `KHOẢNG TRỐNG G-1` — **ĐÃ ĐÓNG** (`PKT-P0-FIX5`)
>
> Bản trước của tài liệu này ghi: *"**Không tồn tại** một lệnh nào đặt `owner.password_hash`"*,
> và đường duy nhất đã kiểm là gọi thẳng phương thức bằng `python -c` **với mật khẩu nằm trên
> dòng lệnh** — thứ mà mọi tiến trình khác trên máy đọc được.
>
> Nay đã có CLI: `rr-admin bootstrap-owner` (hoặc `make bootstrap`). Nó **hỏi mật khẩu
> hai lần và không hiện lại** (`getpass`), đọc được từ stdin để bạn pipe từ một file `0600`, và
> **không có tham số `--password`** — cố ý, vì tham số tiến trình là thứ ai cũng đọc được. Nó in
> **đúng một dòng: ULID của owner**, không in mật khẩu, không in hash, không in tham số Argon2.

Đường đúng — **`đã chạy ở đây`**:

```bash
make migrate      # nếu bạn chưa chạy ở §2
make bootstrap
```

hoặc trực tiếp, khi bạn muốn đọc mật khẩu từ file:

```bash
uv run rr-admin bootstrap-owner < /đường/dẫn/mật-khẩu-0600
```

**Kỳ vọng:** đúng một dòng — ULID của owner, ví dụ dạng `01M22R…` (26 ký tự Crockford base32).

> **Tên đăng nhập của bạn là `--display-name`, mặc định `Owner`** — `auth.login` so `username`
> với `owner.display_name` (`server/app/auth/service.py`: *"``username`` is matched against
> ``owner.display_name``"*). Nó **phân biệt hoa thường**: đăng nhập bằng `owner` trả `401`
> `UNAUTHORIZED`, bằng `Owner` trả `200` — **`đã chạy ở đây`**, cả hai. Nếu bạn đặt
> `--display-name` khác, đó mới là tên đăng nhập.
Gọi lại lần nữa **không** tạo hàng thứ hai: `owner.singleton_guard` khiến điều đó là lỗi
database, và hàm chuyển sang nhánh đặt lại mật khẩu, đồng thời **thu hồi mọi session** đang mở
(`secrets.md` §2.3).

**Đừng gõ mật khẩu thẳng vào dòng lệnh** trên máy dùng chung: tham số tiến trình đọc được bởi
người khác. `bootstrap-owner` vì vậy **không nhận** mật khẩu qua tham số; hãy để nó hỏi, hoặc
pipe từ một file `0600` mà bạn xoá sau đó. Mật khẩu ngắn hơn **8 ký tự** bị từ chối ngay tại
console và **không ghi gì** vào database.

Tham số băm là Argon2id với `memory_cost` 64 MiB, `time_cost` 3, `parallelism` 1
(`secrets.md` §2.2, khai lại thành hằng số ở `server/app/auth/service.py`). Cả năm tham số vẫn
mang nhãn `PROVISIONAL` trong hợp đồng.

---

## 4. Khởi động các tiến trình

### 4.0 Điều phải đọc trước — `KHOẢNG TRỐNG G-2` — **ĐÃ ĐÓNG** (`PKT-P0-FIX5`)

> **Bản trước ghi:** *"Chưa có composition root … `RR_DATABASE_URL` chỉ được Alembic đọc, ứng
> dụng không đọc nó … `POST /v1/auth/login` trả **500** kèm `AttributeError: 'State' object has
> no attribute 'auth_service'`."*
>
> **Nay không còn đúng.** `server/app/settings.py` đọc môi trường, `server/app/wiring.py` dựng
> engine → service → `app.state.*_context` đúng như test của từng card dựng, và
> `server.app.main:app` tự nối bằng **lifespan lúc khởi động**. Đo lại trên một tiến trình
> uvicorn thật, database trắng, sau `make migrate` + `make bootstrap`:
>
> | Lệnh | Trước | Nay |
> | --- | --- | --- |
> | `POST /v1/auth/login` | **500** `AttributeError` | **200**, đặt cookie `rr_session` + `rr_csrf` |
> | `GET /v1/health/readiness` (có phiên) | 401 mãi mãi | **200**, `storage_health: healthy` |
> | `GET /v1/runs` (có phiên) | 500 | **200** `{"runs":[]}` |
>
> `create_app()` **gọi trần vẫn là app rỗng** — không database, không service — vì hàng chục
> test của các card dựa vào đúng điều đó. Chỉ `server.app.main:app` (thứ `make serve` và
> uvicorn dùng) mới tự nối. Import module **không** tạo file database.

> ### Cái vẫn **chưa** nối, và vì sao
>
> `make status` in đúng danh sách này kèm lý do. Không thứ nào bị "cắm tạm" cho có:
>
> Bảy dòng dưới đây là **nguyên văn** những gì `uv run rr-admin status` in ra trên máy kiểm —
> **`đã chạy ở đây`**. Không thứ nào bị "cắm tạm" cho có, và mỗi dòng tự nêu lý do:
>
> | Không nối | Lý do `status` in ra |
> | --- | --- |
> | `collector_token` | `RR_COLLECTOR_TOKEN` chưa đặt ⇒ collector gọi ingest nhận `401` |
> | `telegram_ingress_secret` | `RR_TELEGRAM_WEBHOOK_SECRET` chưa đặt ⇒ **mọi update bị từ chối**, đúng hướng default-deny |
> | `delivery_context.transport` | chưa cấu hình bot token Telegram. `status` nói thẳng: *"MOD-secret-service exists now, so this is a missing credential, not a missing module"* |
> | `analysis_context.provider_config` | chưa provider AI nào được bật: `REQ-OQ03` đã trả lời nhưng cả hai adapter giữ `enabled=false` cho tới khi có bằng chứng cô lập (`REQ-A5`, `ADR-0010`) |
> | `secret_store` | `RR_SECRET_MASTER_KEY` chưa đặt ⇒ `secret.*` từ chối. *"No key is ever generated or defaulted"* — xem §7.1 và §8.4 |
> | `report_context` | `CR-P0-07`: `TagConfigVersionPort` chưa có hiện thực, và chưa có model embedding thật (`REQ-OQ09`) |
> | `research_connector` | `SG-DOC`: **không hợp đồng nào** nêu host hay endpoint của arXiv/OpenAlex (`endpoint_template` là `None`, `CR-PC05-03`); `SG-LIVE`: một lời gọi thật là E3, cần packet riêng |
>
> Hệ quả: §7 (Telegram) và §8 (AI) **vẫn bị chặn**, nhưng nay bị chặn vì **thiếu credential và
> thiếu bằng chứng cô lập**, không còn vì thiếu composition root hay thiếu module.
>
> *(Bản trước của bảng này ghi `research_connector` bị chặn vì *"bốn dữ kiện `REQ-A6` còn
> `PLACEHOLDER_KC`"*. Điều đó **đã sai từ Giai đoạn 2** — `REQ-A6` ở trạng thái `XN` và
> `retry-policy.yaml` mang `DOCS_derived`. Lý do thật là `SG-DOC`/`SG-LIVE`; audit
> `A3-P5-R1` bắt lỗi này là `F-A3-P5-02` và `status` nay in đúng.)*

### 4.1 Server

`contracts/ops/deployment.md` §3: container `app` nghe `8080/TCP` (mặc định cấu hình, đổi
được), và ra Internet qua reverse proxy ở `443` với **TLS bắt buộc** (`secrets.md` §2.4 — cookie
phiên có cờ `Secure`, nên đăng nhập **không** hoạt động qua HTTP thường; đó là kết quả mong
muốn). Trên máy cá nhân bạn chỉ chạy tiến trình trần, nghe loopback.

Chuỗi import đúng là `server.app.main:app` (`README.md` §2.1) — **`đã chạy ở đây`**. Chạy
`make migrate` và `make bootstrap` **trước**, nếu không server vẫn khởi động nhưng mọi route cần
owner sẽ từ chối và `make status` sẽ nói thẳng còn thiếu bước nào:

```bash
make serve
# tương đương: uv run uvicorn server.app.main:app --host 127.0.0.1 --port 8080
```

**Kỳ vọng:**

```
INFO:     Started server process [<pid>]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```

*(Trên máy kiểm, cổng `8080` đã bị một dịch vụ khác chiếm, nên lệnh được chạy với
`--port 8099`; ngoài số cổng, output giống hệt. Nếu bạn thấy HTML lạ trả về thay vì JSON, kiểm
xem cổng có bị chiếm không.)*

Thêm `--reload` khi bạn muốn sửa mã và server tự nạp lại (`README.md` §2).

Ba phép thử — **`đã chạy ở đây`**, ở một terminal khác:

```bash
curl -i http://127.0.0.1:8080/healthz
curl -i http://127.0.0.1:8080/v1/health/readiness
```

**Kỳ vọng:**

| Lệnh | Quan sát được |
| --- | --- |
| `/healthz` | `HTTP/1.1 200 OK`, header `x-schema-version: 0.3.0`, thân `{"status":"up","schema_version":"0.3.0"}`. **Không** lộ cấu hình, tên provider hay chat id — đúng `contracts/state/storage.yaml` `HC-01`/`HC-03` và `secrets.md` §2.4. Đây là endpoint **duy nhất** không cần xác thực. |
| `/v1/health/readiness` **chưa đăng nhập** | `HTTP 401` + phong bì lỗi `{"code":"UNAUTHORIZED", …, "details_safe":{"required_auth_scope":"owner_session"}}`. Đúng hướng default-deny. **Sau khi đăng nhập** (gửi kèm cookie phiên) route này trả **200** với khối `modules` — **`đã chạy ở đây`**. |

Về `auth.login`, hai header **bắt buộc** trên mọi request (quan sát được bằng chính lỗi trả
về): `X-Schema-Version` và `X-Request-Id`. Thiếu header nào thì server trả `422` kèm
`details_safe.field_path` chỉ đúng header còn thiếu — **`đã chạy ở đây`**:

```bash
curl -i -X POST http://127.0.0.1:8080/v1/auth/login \
  -H 'Content-Type: application/json' \
  -H 'X-Schema-Version: 0.3.0' \
  -H 'X-Request-Id: <ULID của bạn>' \
  -d '{"username":"owner","password":"<mật-khẩu>"}'
```

**Kỳ vọng — `đã chạy ở đây` trên tiến trình uvicorn thật:** `HTTP 200` và thân
`{"authenticated":true,"csrf_token":"…","expires_at":"…","schema_version":"0.3.0"}`, kèm hai
cookie `rr_session` (HttpOnly) và `rr_csrf` (không HttpOnly, cho double-submit). `username` là
`display_name` bạn đã đặt ở §3 (mặc định `Owner`).

Mật khẩu ngắn hơn 8 ký tự vẫn bị chặn ở tầng validate: `422` với
`"String should have at least 8 characters"`. Sai mật khẩu 5 lần trong 15 phút thì khoá tài
khoản 15 phút (`RATE_LIMITED`) — `owner.failed_login_count`/`locked_until`, nên khoá **sống sót
qua restart**.

Sau khi có cookie, hai phép thử còn lại — **`đã chạy ở đây`**:

```bash
curl -i http://127.0.0.1:8080/v1/health/readiness -b cookies.txt \
  -H 'X-Schema-Version: 0.3.0' -H 'X-Request-Id: <ULID>'
curl -i http://127.0.0.1:8080/v1/runs -b cookies.txt \
  -H 'X-Schema-Version: 0.3.0' -H 'X-Request-Id: <ULID>'
```

**Kỳ vọng:** readiness `200` với `{"modules":{...},"storage_health":"healthy",...}`; `/v1/runs`
`200` với `{"runs":[]}` trên một database trắng. `/v1/runs` là phép thử đáng giá nhất trong ba:
nó đọc `app.state.job_context`, thứ chỉ tồn tại khi engine, owner id và lịch đều đã được nối.

#### Toàn bộ ma trận route sau khi đăng nhập

Năm route dưới đây đã được gọi **trên một tiến trình uvicorn thật, qua TCP** — **`đã chạy ở
đây`**, cùng một phiên:

| Route | Mã | Thân (rút gọn) |
| --- | --- | --- |
| `GET /v1/health/readiness` | **200** | `{"modules":{"storage":"ok","job_dispatch":"ok","delivery_dispatcher":"ok","scheduler":null,…},"storage_health":"healthy","dispatcher_locked_for_recovery":false}` |
| `GET /v1/runs` | **200** | `{"runs":[]}` |
| `GET /v1/settings` | **200** | `{"settings":{},"timezone_iana":null,"providers":[],"source_connections":[]}` |
| `GET /v1/saved` | **200** | `{"schema_version":"0.3.0","items":[],"count":0}` |
| `GET /v1/reports` | **500** | xem ngay dưới |

Trong khối `modules` của readiness, những mục chưa nối trả **`null`**, không trả `ok`. Đó là
`I13` và `CAP-P5` được tôn trọng đúng chỗ dễ vi phạm nhất: *"không có dữ liệu"* phải phân biệt
được với *"khoẻ"*.

> #### `GET /v1/reports` trả `500` — và vì sao bạn **không** cần lo
>
> Đây là route owner-facing **duy nhất** chưa hoạt động. Thân trả về — **`đã chạy ở đây`**:
>
> ```json
> {"code":"INTERNAL","scope":"request","retry_class":"unknown_outcome",
>  "message_safe":"Dịch vụ báo cáo chưa được cấu hình trong bản triển khai này (CR-P0-07):
>                  chưa có cổng tag-service và cổng embedding. Yêu cầu của bạn hợp lệ và
>                  không có dữ liệu nào bị đọc hay ghi.",
>  "details_safe":{"operation_id":"report.list"}}
> ```
>
> Ba điều đáng ghi nhận: mã `500` **đúng hợp đồng** (`openapi.yaml` khai `500` cho đường này),
> phong bì là `ErrorEnvelope` hợp lệ **không rò traceback**, và `message_safe` **nói thẳng
> nguyên nhân, mã CR, và rằng không dữ liệu nào bị đọc hay ghi**.
>
> Audit `A3-P5-R1` nêu đúng điểm yếu còn lại (`F-A3-P5-03`): mã vẫn là `INTERNAL` — nghĩa là
> *"bất ngờ"* — cho một tình huống **hoàn toàn được dự đoán. `retry_class` là
> `unknown_outcome`, nên đừng đọc nó như "thử lại sẽ được": sẽ không, cho tới khi `CR-P0-07`
> đóng. Điều đã cải thiện so với vòng trước là `message_safe`: nó không còn chỉ nói *"Có lỗi
> không mong đợi"*.

`GET /openapi.json` trả `404` — có chủ đích: `create_app()` đặt `openapi_url=None`,
`docs_url=None`, `redoc_url=None`. Hợp đồng HTTP là `contracts/http/openapi.yaml`, không phải
một trang tự sinh.

### 4.2 Web UI

**`đã chạy ở đây`** — chế độ dev:

```bash
npm --prefix web run dev
```

**Kỳ vọng:** `VITE v7.3.6 ready in <…> ms` và một dòng `➜ Local: http://localhost:5173/`.
`GET /` trả `200`. (Trên máy kiểm chạy với `-- --port 5199` để tránh đụng cổng.)

**`đã chạy ở đây`** — bản build:

```bash
npm --prefix web run build
```

**Kỳ vọng:** `tsc --noEmit` im lặng, rồi `✓ 83 modules transformed.` và một bảng
`dist/index.html` + `dist/assets/index-<hash>.js` (~207 kB, ~68 kB gzip). Đầu ra ở `web/dist/`,
đã nằm trong `.gitignore`; `make clean` xoá nó.

Giao diện gọi API của server. Server **nay đã nối database** (§4.0), nên các màn hình đọc được
dữ liệu thật ngay khi có dữ liệu; trên một database trắng chúng hiển thị trạng thái rỗng.

### 4.3 Analysis worker

`deployment.md` §1–§2: worker chạy **trên máy cá nhân, không container**, **không lắng nghe
cổng nào**, mọi kết nối là outbound.

Ba lệnh, cả ba **`đã chạy ở đây`**:

```bash
uv run rr-worker --print-capabilities   # khai báo năng lực, không chạm mạng
uv run rr-worker --print-adapters       # adapter AI nào bật, adapter nào không, vì sao
uv run rr-worker --run                  # vòng chạy thật
```

**Kỳ vọng `--print-capabilities`:**
`{"worker_kind":"analysis","agent_version":"0.1.0","schema_version":"0.3.0","tasks_supported":["label","summary","direction_phrasing"],"ai_providers":[]}`,
thoát `0`. `ai_providers` rỗng vì chưa adapter nào được bật ([§8](#8-ai)).

**Kỳ vọng `--print-adapters`:** hai mục Anthropic, **cả hai** `"enabled": false` với
`"reason_code": "isolation_unverified"` và `"probe_outcome": "unknown"`, rồi
`"ac16": "BLOCKED"` ở cuối. Đây là §8.2 nhìn từ phía tiến trình sẽ dùng chúng.

**Kỳ vọng `--run` khi chưa cấu hình:**

```json
{"started": false, "reason": "server_url_not_configured",
 "detail": "set RR_SERVER_URL to the base URL of the Research Radar server"}
```

thoát **`2`**. Nó **không** đoán một địa chỉ server, **không** ghi hàng nào, và nói đúng biến
môi trường bạn còn thiếu. Đó là lời từ chối đúng, không phải lỗi của bạn.

> **`KHOẢNG TRỐNG G-7` — ĐÃ ĐÓNG một nửa.** Worker **không còn là stub**: `--run` là một vòng
> chạy thật, biết đăng ký, heartbeat và claim khi có `RR_SERVER_URL` cùng token. Cái **chưa**
> chứng minh được ở đây là vòng chạy đó **nói chuyện với một server thật** — điều đó cần cả
> hai tiến trình cùng cấu hình, và audit `A3-P5-R1` ghi rõ nó **không** chạy được vòng backoff
> của adapter bị tắt trong đợt kiểm đó. Vì vậy **"collector online"** theo `deployment.md` §6
> (đăng ký hợp lệ **và** heartbeat trong `online_threshold` = 90 s **và** server ghi được)
> vẫn **chưa từng được quan sát**.

Cấu hình worker cần (`secrets.md` §3): `RR_SERVER_URL`, và `analysis_worker_token` trong một
file **`0600`** ở thư mục cấu hình của user — **không bao giờ trong repo**.

### 4.4 Collector

Kiểm cấu hình **trước** khi chạy — **`đã chạy ở đây`**:

```bash
uv run rr-collector --check-config
```

**Kỳ vọng khi chưa cấu hình:**

```json
{"status": "refused_to_start",
 "reason": "missing_server_url",
 "message": "RR_SERVER_URL is not set; the collector has no default server address"}
```

thoát **`3`**. Giống worker: **không đoán** địa chỉ server, **không** mở trình duyệt, **không**
chạm Chrome profile, **không** ghi hàng nào.

Collector cần hai thứ trước khi `--check-config` xanh: `RR_SERVER_URL`, và `collector_token`
trong file `0600` của user. Token này **tách rời** token của analysis worker dù hai tiến trình
chạy cùng máy — bán kính ảnh hưởng khác nhau (`secrets.md` §3): collector chạm dữ liệu thô X,
analysis worker chạm credential provider.

Repo **không bao giờ** chạy `playwright install`; trình duyệt là bước trên máy bạn ([§1](#1-chuẩn-bị-và-cài-đặt)).

---

## 5. Thứ tự khởi động (khi hệ thật tồn tại)

`deployment.md` §8, ghi ở đây để bạn biết trật tự đúng, **không** phải để bạn chạy hôm nay:

1. Kho dữ liệu mở được (integrity check nhanh) — không được thì `storage.health ≠ healthy`, dừng.
2. `MOD-health-service` (phải sống trước để báo lỗi các bước sau).
3. Secret service, auth, các domain service, backend API.
4. Embedding container; kiểm có `active_generation`.
5. **Cuối cùng**: scheduler và delivery dispatcher — hai module tạo side effect.

Quy tắc dừng: nếu `storage.health = recovery_required` (sau restore), bước 5 **không** được
khởi động cho tới khi `backup.reconcile_after_restore` thành công (`I15`, `NC-10`).

---

## 6. Probe khả thi nguồn X (SP1)

**Runbook đầy đủ là [`probe/README.md`](../probe/README.md)** — đọc nó, đừng đọc mục này thay
nó. Giao thức là [`contracts/ops/collector-probe.md`](../contracts/ops/collector-probe.md);
card là [`agent-tasks/TC-x-feasibility-probe.md`](../agent-tasks/TC-x-feasibility-probe.md).

Mục này chỉ nêu ba điều bạn cần biết trước khi mở file đó.

### 6.1 Cổng Owner — bốn xác nhận, bằng văn bản

`collector-probe.md` §6. Probe **từ chối mở trình duyệt** cho tới khi cả bốn có
`confirmed: true` **và** một `evidence_ref` trỏ tới câu trả lời **bằng văn bản** của bạn:

| Khoá trong config | Điều xác nhận | Trạng thái |
| --- | --- | --- |
| `d09_project_chrome_profile` | dùng Chrome profile **riêng của dự án** | **đã trả lời** — `OD-20260907-01` mục 1 |
| `budget_and_stop_conditions` | ngân sách §3 và điều kiện dừng §4 chấp nhận được với tài khoản X của bạn | `OWNER_DECISION_REQUIRED` |
| `go_no_go_criteria` | tiêu chí go/no-go §7 là tiêu chí bạn đồng ý dùng để kết luận | `OWNER_DECISION_REQUIRED` |
| `account_risk_understood` | probe chạy trên **tài khoản X thật của bạn**, mang rủi ro bị hạn chế tài khoản (`REQ-A7`), rủi ro đó **không kiểm chứng được trước** | `OWNER_DECISION_REQUIRED` |

`confirmed: true` với `evidence_ref` rỗng **không** tính là xác nhận.

### 6.2 Hai lệnh

Kiểm cấu hình **mà không mở trình duyệt** — **`đã chạy ở đây`**:

```bash
uv run python probe/x_feasibility/run_probe.py --config ~/rr-probe.json --dry-run
```

**Kỳ vọng hôm nay:** thoát **`2`**, kèm đúng ba mục còn thiếu:

```
ERROR OWNER_DECISION_REQUIRED — chưa đủ bốn xác nhận của contracts/ops/collector-probe.md §6;
probe KHÔNG được chạy (card SG-02).
Còn thiếu:
  - budget_and_stop_conditions: …
  - go_no_go_criteria: …
  - account_risk_understood: …
```

Chạy một đợt thật:

```bash
uv run python probe/x_feasibility/run_probe.py --config ~/rr-probe.json
```

> **`chưa chạy ở đây`** — lệnh này mở Chrome thật và chạm x.com. Nó chỉ chạy trên **máy của
> bạn**, sau khi bốn xác nhận đủ. Không CI, không agent, không máy nào khác. Bằng chứng khả thi
> nguồn X hiện là **`NOT_RUN`** và `evidence/runs/SP1-x-feasibility/runs.jsonl` **vắng mặt** —
> đúng thiết kế.

Tính go/no-go sau **≥ 5 đợt** trải **≥ 3 ngày**: `uv run python probe/go_no_go.py
evidence/runs/SP1-x-feasibility/runs.jsonl` (**`chưa chạy ở đây`** — không có dữ liệu để chạy).

### 6.3 Đường dẫn đầu ra — `KHOẢNG TRỐNG G-5` **ĐÃ ĐÓNG**

> **Bản trước ghi:** `output_dir` tương đối được giải theo **thư mục chứa file config**, nên
> bản ghi rơi cạnh config thay vì vào repo; một lần `--dry-run` với file mẫu đã thật sự tạo
> `probe/evidence/runs/SP1-x-feasibility/probe.log` bên trong cây nguồn.
>
> **Nay đã sửa.** `output_dir` tương đối được giải theo **thư mục làm việc**, và probe **in ra
> đường dẫn nó đã chọn** ngay dòng đầu — nên quy tắc không còn phải đoán:
>
> ```
> INFO output_dir: /<cwd>/evidence/runs/SP1-x-feasibility
> ```
>
> Và `--dry-run` nay **không ghi gì cả**. Kiểm bằng cách chạy từ một thư mục tạm rồi liệt kê
> lại thư mục đó — **`đã chạy ở đây`**: sau lệnh chỉ còn đúng `cfg.json` và thư mục profile;
> **không** có cây `evidence/`, **không** có `probe.log`.

Vẫn nên đặt `output_dir` **tuyệt đối** nếu bạn hay đổi thư mục giữa các đợt: quy tắc đã rõ,
nhưng một đường dẫn tuyệt đối thì không phụ thuộc vào việc bạn đứng ở đâu khi gõ lệnh.

### 6.4 Ranh giới — không thương lượng

`collector-probe.md` §2 và `capabilities.yaml` `DC-COL-07`. Đọc nguyên văn ở
`probe/README.md` §1. Tóm tắt: **không lách bất kỳ biện pháp xác minh nào, không giả
fingerprint, không luân chuyển account/proxy, bị chặn thì DỪNG và BÁO, không dùng X API trả phí
làm đường vòng.** Vi phạm là **hỏng probe**, làm card FAIL ngay bất kể con số thu được. Ba việc
đó **vắng mặt trong mã**, và `tests/contract/test_x_probe_boundaries.py` khẳng định điều đó
bằng máy.

---

## 7. Telegram

Hợp đồng: [`contracts/telegram/commands.yaml`](../contracts/telegram/commands.yaml),
[`contracts/telegram/delivery.md`](../contracts/telegram/delivery.md),
[`contracts/ops/secrets.md`](../contracts/ops/secrets.md) §7. Mã:
`server/app/telegram/{router,ingress,linking,commands}.py`.

### 7.1 Tạo bot và đặt webhook

> **`chưa chạy ở đây`** — mọi bước dưới đây chạm `api.telegram.org`. **Chưa một lần gọi Bot API
> nào được thực hiện ở bất kỳ giai đoạn nào của dự án** (`precode/review.md` §17.6 mục 3).

1. Tạo bot với @BotFather trên Telegram, nhận **bot token**.
2. Bot token vào **secret store phía server**, `secret_ref.purpose = telegram_bot`
   (`secrets.md` §7). Nó **không** vào repo, **không** vào log, **không** vào tin nhắn.
   Nơi cất này **nay đã tồn tại** — xem [§8.4](#84-api-key-để-ở-đâu); nó cần
   `RR_SECRET_MASTER_KEY`.
3. Sinh một **webhook secret** ngẫu nhiên, đặt vào biến môi trường
   **`RR_TELEGRAM_WEBHOOK_SECRET`** của tiến trình server, rồi đăng ký webhook với Telegram trỏ
   vào `POST /v1/telegram/webhook` qua **HTTPS 443**.

Chưa đặt `RR_TELEGRAM_WEBHOOK_SECRET` thì `rr-admin status` in
`not wired : telegram_ingress_secret — RR_TELEGRAM_WEBHOOK_SECRET is not set; updates denied`
— **`đã chạy ở đây`** — và **mọi** update bị từ chối. Đó là default-deny đúng chỗ: ingress là
điểm duy nhất một caller chưa xác thực chạm tới được.

Hai lớp bảo vệ, **cả hai đều bắt buộc** (`secrets.md` §7): đường dẫn ingress khó đoán **và**
kiểm header bí mật `X-Telegram-Bot-Api-Secret-Token` (security scheme `telegramIngressSecret`).
"Đường dẫn khó đoán" một mình **không phải** xác thực. Sai secret ⇒ `UNAUTHORIZED`, không xử lý
gì.

Mã đã theo hướng an toàn: `TelegramContext.webhook_secret` mặc định `None`, và
`ingress.verify_webhook_secret` **từ chối mọi update** khi secret chưa cấu hình — default-deny
đúng ở chỗ duy nhất mà một caller chưa xác thực chạm tới được.

### 7.2 Liên kết chat — không có lệnh `/link`

Đây là điểm dễ hiểu nhầm. **Không tồn tại lệnh `/link`.** Quy trình là:

1. Trong ứng dụng (owner session + CSRF), gọi `POST /v1/telegram/link-codes`
   (`telegram.issue_link_code`) để **đúc một mã liên kết**. Mã có dạng `RR-XXXXXXXX` —
   regex `^RR-[0-9A-HJKMNP-TV-Z]{8}$` (Crockford base32, `server/app/telegram/linking.py`).
2. **Gõ nguyên mã đó** vào chat với bot. Toàn bộ nội dung tin nhắn (sau trim) phải khớp regex.
3. Khớp và mã còn hiệu lực ⇒ liên kết thành công + một tin xác nhận. Sai, hết hạn, đã dùng, bị
   rate-limit ⇒ **im lặng hoàn toàn**, không phân biệt được từ bên ngoài.

Mã **dùng một lần, có hạn** (`REQ-S11.2-04`, `REQ-S11.3-01`). Tin từ chat **chưa liên kết** bị
**bỏ im lặng** (`REQ-S11.3-02`, `AC-18`); ngoại lệ hẹp duy nhất là chuỗi đúng định dạng mã liên
kết (`B09`). Huỷ liên kết: `DELETE /v1/telegram/link` — **hành động trong ứng dụng**, không phải
lệnh chat.

### 7.3 Ba lệnh — và phạm vi "chỉ chữ, không nút"

`commands.yaml` §3: **đúng ba lệnh, không có lệnh thứ tư (`AMD-B10`)**. Danh sách là
**allowlist, không phải blocklist** — một chuỗi không nằm trong danh sách bị từ chối vì *không
có trong danh sách*, nên không lệnh mới nào xuất hiện được do bị quên trong một bộ lọc.

| Bạn gõ | Command id | Operation | Trả lời (nguyên văn `reply_templates_vi`) |
| --- | --- | --- | --- |
| `/status` | `CMD-status` | `run.list` | ví dụ: `Đợt gần nhất: không có nội dung phù hợp (đã thu thập xong, không bài nào khớp tag).` — cụm `Không có nghiên cứu mới` bị **cấm** (`ST-02`) |
| `/run_now` | `CMD-run-now` | `run.run_now` | `Đã xếp hàng một đợt chạy.` / `Đang có một đợt chạy. Trạng thái: …` / `Đợt đang chờ xác minh trên máy cá nhân. Mở ứng dụng, vào Runs và bấm Tiếp tục sau khi xử lý xong.` |
| `/save <target>` | `CMD-save` | `save.create` | `Đã lưu.` / `Mục này đã có trong Saved.` / thiếu tham số: `Cần mục để lưu. Ví dụ: /save work:<ID>.` |

**Chú ý dấu gạch dưới:** trigger thật là **`/run_now`**, không phải `/run-now`
(`TRIGGERS` trong `server/app/telegram/commands.py`).

**"Phạm vi chỉ chữ" nghĩa là gì.** Ba trong năm dữ kiện định dạng của Bot API vẫn là `KC`
(`delivery.md` §3.4: độ dài `callback_data`, bảng escape parse-mode, số nút mỗi hàng), và chúng
đang `BLOCKED_DEPENDENCY` dưới `CR-PC07-04`. Vì vậy adapter:

- gửi **thuần văn bản**: không `parse_mode`, không `reply_markup`, **không nút inline nào**;
- nhận `CMD-save` như một lệnh **gõ tay**, không phải nút bấm;
- **không** hiện thực bộ phân tích `callback_data` nào.

Tin dài bị cắt theo giới hạn `1..4096` ký tự đếm trên chuỗi **thô** (`delivery.md` §3.5).

`run.resume` **không** với tới được từ Telegram: `modules.yaml` `FE-33` cấm cạnh
`MOD-telegram-adapter → MOD-job-service` phạm vi `run.resume`, và
`commands.py::assert_no_resume_path()` khẳng định sự vắng mặt đó bằng cấu trúc, không bằng
review.

Việc còn lại của bạn ở mục 7 của `precode/review.md` §17.6: **đọc tài liệu Bot API** cho ba dữ
kiện `KC` nói trên, để gỡ `CR-PC07-04`.

---

## 8. AI

Hợp đồng: [`contracts/ai/providers.yaml`](../contracts/ai/providers.yaml),
[`contracts/ai/tasks.yaml`](../contracts/ai/tasks.yaml),
[`contracts/ops/cli-acp-probe.md`](../contracts/ops/cli-acp-probe.md), `ADR-0010`, `B13`.

### 8.1 Hai họ provider

| Họ | Xác thực | Song song | Nơi secret ở |
| --- | --- | --- | --- |
| `api_key` | key trong **secret store phía server**; worker nhận credential theo **từng task** (`B13`) | provider tự khai | server; worker chỉ giữ trong **bộ nhớ tiến trình**, TTL **900 s** |
| `cli_acp` | **phiên đăng nhập của bạn** trên máy cá nhân | **1** — hằng số hợp đồng | không rời máy; `secret_ref = NULL` |

Đường `cli_acp` là con đường làm `AC-16` đúng: nếu `label`, `summary` **và**
`direction_phrasing` đều chạy qua CLI thì hệ hoàn tất một đợt **không cần API key nào** — vì
embedding là model local ở server (`REQ-D48`/`REQ-D50`). `SEC-P5`: **không secret nào là bắt
buộc**.

### 8.2 Hai adapter đã đăng ký — và vì sao **cả hai** `enabled: false`

`providers.yaml` §2.1 ghi hai mục của một nhà cung cấp thật (Anthropic), theo `REQ-OQ03` /
`OD-20260908-06`:

| `adapter_id` | Tác vụ | `enabled` |
| --- | --- | --- |
| `anthropic@claude-sonnet-5` | `label`, `direction_phrasing` | **`false`** |
| `anthropic@claude-opus-5` | `summary` | **`false`** |

**Cái đang chặn là *cô lập*, không phải điều khoản.** `REQ-A5` (điều khoản Anthropic) đã được
**Owner ký xác nhận** — `OD-20260908-08`, `AUTH-OWNER-20260908-09`, 2026-09-08. Cái giữ
`enabled = false` là hai tính chất chưa kiểm chứng được:

- **`ISO-03`** — *network egress*: phải **ghi lại tập đích thật** của một lần chạy adapter và
  thấy nó nằm trong allowlist.
- **`ISO-05`** — *credential đúng provider, đúng task đang giữ lease*: phải gọi
  `secret.issue_task_credential` cho một worker **không** giữ lease và **thấy nó bị từ chối**.

`providers.yaml` §4 nói thẳng vì sao hai mục này **không** được mang `not_applicable` để đi
vòng: `not_applicable` chỉ dành cho tính chất mà **kiến trúc đã loại bỏ**, còn `ISO-03`/`ISO-05`
là hai tính chất mà chính đường `api_key` **tạo ra** — nó là đường **duy nhất** gọi mạng ra
endpoint nhà cung cấp và là đường **duy nhất** nhận `secret_ref`. Nguyên tắc gốc (`ADR-0010`
điểm 3): **"Không kiểm chứng được thì không bật."** Và: *"Một lời hứa trong tài liệu của nhà
cung cấp KHÔNG phải bằng chứng cô lập."*

### 8.3 Bạn phải làm gì để bật một adapter

Đây là **bằng chứng hợp đồng đòi**, không phải một công tắc:

1. Chạy **probe cô lập E3** theo `contracts/ops/cli-acp-probe.md`, quan sát được egress của
   adapter, ghi `isolation.network_egress` và `verification_method` bằng kết quả **đo được**.
2. Chạy một **denied-case thật** cho `secret.issue_task_credential`: worker không giữ lease →
   phải bị từ chối. (→ chặn bởi **`KHOẢNG TRỐNG G-6`**: operation này **chưa có mã**.)
3. Chỉ khi cả năm `ISO-01..05` thoát khỏi `unverified` thì `enabled` mới được đặt `true`, và
   `disabled_reason` mới được xoá.
4. `isolation_verified: false` ⇒ adapter giữ `disabled` và worker khai `usable: unusable` với
   `reason_code: isolation_unverified` — **không bật "để thử"** (`deployment.md` §7).

Bằng chứng E3 hiện là **`NOT_RUN`**. Trước đó, `enabled: true` là *"một tuyên bố không có
oracle"* (`providers.yaml` §2.1).

### 8.4 API key để ở đâu

`secrets.md` §4: **secret store phía server**, mã hoá **envelope** (mỗi secret một data key;
data key mã hoá bằng **master key**). Master key đến từ **biến môi trường của container** hoặc
một **file `0400`** mount vào container — **không** trong DB, **không** trong repo.

Chỉ `MOD-secret-service` đọc được giá trị. Không operation nào **trả về** key cho frontend:
`settings.get_config` chỉ trả tham chiếu và trạng thái *"đã cấu hình hay chưa"*.

**Hệ quả phải nói thẳng** (`secrets.md` §4.1): master key nằm ngoài DB, nên **backup file DB
không chứa key**; mất master key là mất mọi secret dù backup còn nguyên. Đó là lý do
`backup-restore.md` §6 đòi một **kế hoạch khôi phục secret riêng**, giữ ở nơi bạn chọn, ngoài
server và ngoài backup.

> ### `KHOẢNG TRỐNG G-6` — **ĐÃ ĐÓNG** (`TC-secret-settings-service`, card thứ 20)
>
> **Bản trước ghi:** *"hôm nay bạn không có chỗ hợp lệ nào để đặt API key"* — `server/app/`
> không có `secret/` hay `settings/`, ba operation `secret.*` chưa có mã.
>
> **Nay đã có.** `server/app/secret/` và `server/app/settings_service/` tồn tại, migration
> `0014` tạo sáu bảng (`secret_ref`, `task_credential`, `secret_audit`, `provider_config`,
> `provider_test_result`, `source_connection`), và cipher là **AES-256-GCM** thật — chọn từ hai
> lựa chọn của `secrets.md` §4.1 vì `cryptography` không hiện thực cái kia
> (XChaCha20-Poly1305). Kèm theo: `ISO-05` **cuối cùng đã có thứ để chạy denied-case**.

### Master key: đặt thế nào, và hai hướng hỏng

Biến môi trường là **`RR_SECRET_MASTER_KEY`**, phải giải mã ra **đúng 32 byte** base64url hoặc
hex (`server/app/secret/store.py`). Repo **không** sinh key, **không** commit key, **không**
đặt mặc định — `SG-MASTER-KEY` của card cấm cả ba.

Hai hướng hỏng, **cả hai `đã chạy ở đây`**:

| Tình huống | Hệ thống làm gì |
| --- | --- |
| **Không đặt** | Server **vẫn chạy** — bạn đăng nhập, thu thập, báo cáo được, vì `REQ-D51` nói không key nào là bắt buộc. `rr-admin status` in `not wired : secret_store — RR_SECRET_MASTER_KEY is not set; secret.* operations refuse … No key is ever generated or defaulted.` |
| **Đặt nhưng sai định dạng** | Tiến trình **từ chối khởi động**: `RuntimeError: RR_SECRET_MASTER_KEY is set but unusable: … must decode to 32 bytes of base64url or hex. Refusing to start rather than run with no envelope encryption (contracts/ops/secrets.md §4.1)` |

Hướng thứ hai là điều bạn muốn: một store tự sinh key khi khởi động sẽ **mất sạch** secret ở
lần restart kế tiếp với key khác, mà không báo gì.

Đặt key hợp lệ rồi thì `secret_store` xuất hiện trong dòng `wired` của `status` — **`đã chạy ở
đây`**. Sinh một key mới:

```bash
uv run python -c "import base64,os;print(base64.b64encode(os.urandom(32)).decode())"
```

Cất nó **ngoài repo và ngoài backup** — file `0400` mount vào container, hoặc biến môi trường
của container (`secrets.md` §4.1). Ciphertext nằm sau `SecretMaterialStore`; mặc định là
`FileMaterialStore` với file `0600` dưới `RR_SECRET_MATERIAL_DIR` (mặc định
`<RR_DATA_DIR>/secret-material`), **không** trong database — nên `CR-TC-SECRET-01` ghi nhận
rằng `entities.yaml` chưa khai bảng nào cho phần material này.

**API key của provider** đi vào qua `settings.update_config` / `secret.store_provider_key`, và
**không đường nào trả nó ra**: read model chỉ có `key_configured: true|false` cộng một
`secret_ref` id — không có trường nào để một giá trị nằm vào.

### 8.5 Ba việc không bao giờ được làm

`SEC-P3` / `I11`: nội dung nguồn là **dữ liệu**. Không nội dung nào từ post/abstract/toàn văn
được đọc secret, gọi tool, hay đổi recipient. `secrets.md` §4.3: **transcript CLI/ACP không
được ghi ở mức mặc định** — chỉ ghi JSON đã bóc và phân loại lỗi.

---

## 9. Backup và restore

Hợp đồng: [`contracts/ops/backup-restore.md`](../contracts/ops/backup-restore.md). Mã:
`tools/backup_cli.py` + `server/app/backup/{snapshot,verify,restore,reconcile}.py`.

### 9.1 Xác thực: `backupOperatorToken`, và chỉ nó

`openapi.yaml` và `secrets.md` §2.3 đồng ý: mọi `backup.*` nhận **`backupOperatorToken`** và
**không gì khác**. Một session trình duyệt của owner **không được** khởi động restore — restore
là thao tác khoá side effect trên toàn bộ database, và cookie phiên đúng là credential mà kẻ
tấn công mượn được.

Thực tế mạnh hơn hợp đồng đòi: **không có router HTTP nào** cho `backup.*`.
`tests/integration/test_restore_side_effect_lock.py` khẳng định không route nào trên app mang
`operation_id` bắt đầu bằng `backup.` — nên đường đó không chỉ trượt xác thực, nó **không tồn
tại**.

CLI đọc token từ `RR_BACKUP_OPERATOR_TOKEN` (hoặc `--token-file`, một file `0600` theo
`secrets.md` §3) và so **constant-time** với `RR_BACKUP_OPERATOR_TOKEN_EXPECTED`.
**`--token` cố tình không tồn tại**: tham số tiến trình đọc được bởi mọi user trên máy dùng
chung.

**`đã chạy ở đây`** — không token:

```bash
uv run rr-backup --database var/research-radar.db status --restore-id <ULID>
```

**Kỳ vọng:** JSON
`{"code":"UNAUTHORIZED","message_safe":"Thao tác này chỉ chấp nhận backup operator token.","required_auth_scope":"backup_operator"}`,
thoát **`3`**. Một `expected` chưa cấu hình là **từ chối**, không bao giờ là cho qua.

> **`KHOẢNG TRỐNG G-10` — VẪN MỞ.** Token "đúng" vẫn đến từ biến môi trường
> `RR_BACKUP_OPERATOR_TOKEN_EXPECTED` **do chính người gọi đặt**: `tools/backup_cli.py` đọc
> `os.environ.get(EXPECTED_TOKEN_ENV)` và so hằng-thời-gian với thứ bạn cung cấp.
>
> Đợt nối dây **có** thêm `backup_operator_token_sha256` vào `Settings`
> (`server/app/settings.py`, từ `RR_BACKUP_OPERATOR_TOKEN_SHA256`) — nhưng **CLI chưa dùng
> nó**. Nên khoảng trống thu hẹp chứ chưa đóng: cơ chế đã có chỗ đứng, chỉ chưa được nối vào.
>
> Trên một máy một người dùng đây là bất tiện; trên máy dùng chung nó có nghĩa là **ai chạy
> được CLI thì tự cấp quyền cho mình**. Cho tới khi có card nối `Settings` vào CLI: giữ token
> trong một file `0600` và dùng `--token-file`, đừng để nó trong shell history.

### 9.2 Tạo snapshot

**`đã chạy ở đây`**:

```bash
export RR_BACKUP_OPERATOR_TOKEN=<token của bạn>
export RR_BACKUP_OPERATOR_TOKEN_EXPECTED="$RR_BACKUP_OPERATOR_TOKEN"
mkdir -p var/backups
uv run rr-backup --database var/research-radar.db \
  snapshot --artifact var/backups/2026-09-08.db
```

**Kỳ vọng:** một object JSON gồm `backup_snapshot_id` (ULID), `artifact_sha256`,
`manifest_sha256` (cả hai tiền tố `sha256:`), `"state": "completed"`, `"replayed": false`, và
một map `counts` với 11 khoá (`work`, `post`, `report`, `report_item`, `saved_item`,
`saved_snapshot`, `coverage_window`, `first_announced_ledger`, `backfill_ledger`,
`pending_item_ledger`, `analysis.valid`). Trên DB trống mọi count bằng `0`. Thoát `0`.

Hai phương pháp — `vacuum_into` (mặc định) và `sqlite_online_backup_api` — **đều WAL-safe**;
copy file **không được cung cấp** (`AMD-B11`). `backup-restore.md` §1 giải thích vì sao "copy
file SQLite" không phải backup.

### 9.3 Kiểm snapshot

**`đã chạy ở đây`**:

```bash
uv run rr-backup --database var/research-radar.db verify --snapshot-id <ULID>
```

**Kỳ vọng:** `{"artifact_sha256_matches": true, "counts_match": true, "failed_conditions": [],
"mismatches": [], "pragma_integrity_check": "ok", "state": "verified"}`, thoát `0`.
Thoát `2` nếu bất kỳ điều kiện nào trượt.

### 9.4 Cửa sổ bảo trì — điều kiện tiên quyết của restore

`storage.yaml` `T-ST-05`: restore **bắt đầu từ `maintenance`** và **không tự mở** cửa sổ đó.
`restore.restore_snapshot()` **từ chối** khi store chưa ở `maintenance`; mở cửa sổ là một bước
CLI riêng, có chủ đích — *"một restore tự mở cửa sổ của chính nó"* sẽ là đúng cái
`storage.yaml` liệt vào transition bị cấm, và sẽ bỏ con người ra khỏi vòng ở đúng thao tác cần
họ nhất.

**`--reason` là bắt buộc** khi `--open`. Nó là một cột `NOT NULL` của `ENT-maintenance-window`,
nên không có giá trị mặc định nào hợp lệ: một mặc định sẽ **bịa ra một giá trị audit**.

**`đã chạy ở đây`** — quên `--reason`:

```bash
uv run rr-backup --database var/research-radar.db maintenance --open
```

**Kỳ vọng:** một phong bì lỗi, **không phải traceback**, thoát **`2`**:

```json
{"code": "VALIDATION_ERROR",
 "details_safe": {"field_path": "--reason", "violation_kind": "required_field_missing"},
 "message_safe": "Mở cửa sổ bảo trì cần --reason."}
```

**`đã chạy ở đây`** — đúng cách:

```bash
uv run rr-backup --database var/research-radar.db maintenance --open --reason restore
```

**Kỳ vọng:** `{"storage_health": "maintenance", "transition": "T-ST-03", "window_id": "01M22R…"}`,
thoát `0`. Một hàng thật xuất hiện trong `maintenance_window` với
`opened_by = ACT-backup-operator`, `reason = restore`, `closed_at = NULL` — **`đã chạy ở đây`**,
đọc lại bằng một tiến trình khác.

> ### `KHOẢNG TRỐNG G-3` — **ĐÃ ĐÓNG** (migration `0015_tc_storage_maintenance_window`)
>
> **Bản trước ghi:** `StorageGuard` giữ `storage.health` **trong bộ nhớ tiến trình**, không
> bảng nào lưu nó, nên lần gọi CLI kế tiếp khởi động lại ở `healthy` và `restore` bị chính
> điều kiện tiên quyết của nó từ chối — *"quy trình restore hai bước bằng CLI như tài liệu mô
> tả hiện không hoàn tất được"*.
>
> **Nay cửa sổ sống qua các tiến trình.** Đã kiểm bằng **các lần gọi hoàn toàn tách rời** —
> mỗi dòng dưới đây là một tiến trình mới:
>
> | # | Lệnh | Kết quả |
> | --- | --- | --- |
> | 1 | `snapshot --artifact …` | `state: completed`, `artifact_sha256`, `manifest_sha256` — thoát `0` |
> | 2 | `maintenance --open --reason restore` | `storage_health: maintenance`, `window_id` — thoát `0` |
> | 3 | `verify --snapshot-id …` | `state: verified`, `counts_match: true`, `pragma_integrity_check: ok` — thoát `0` |
> | 4 | `restore --snapshot-id … --confirm RESTORE` | **qua được** điều kiện `maintenance` — `storage_health: recovery_required`, `new_restore_generation: 1` — thoát `0` |
> | 5 | `status --restore-id …` | `storage_health: recovery_required` — **không** còn `healthy` như vòng trước |
>
> Bước 4 là bằng chứng: ở vòng trước nó chết ngay tại `precondition_not_met`. Và bước 5 là nửa
> còn lại — trạng thái **sau** restore cũng bền, nên `recovery_required` thật sự khoá side
> effect thay vì bốc hơi cùng tiến trình.
>
> Một chi tiết đáng biết: chạy `restore` trên một snapshot **chưa** `verify` thì bị từ chối
> bằng `RESTORE_UNVERIFIED` — **`đã chạy ở đây`**. Nó **không** phải lỗi cửa sổ bảo trì; nó
> nghĩa là bạn đã qua cửa đó rồi và đang vướng cửa kế tiếp. Thứ tự đúng là **snapshot → open →
> verify → restore**.

### 9.5 Restore, đối soát, mở lại dispatch

Thứ tự **bắt buộc, không được đảo** (`backup-restore.md` §5.2):

```
1. restore artifact              → storage.health = recovery_required
2. thu hồi TOÀN BỘ assignment_lease có trong snapshot
3. tăng lease_epoch cho mọi run non-terminal   (worker cũ ⇒ STALE_LEASE)
4. ghi restore_record.leases_revoked
5. verify + counts                             (§5.3, §5.4)
6. quyết định với outbox cũ, từng intent một   (§5.5)
7. reconciliation_complete(restore_id) == true
8. CHỈ KHI ĐÓ: backup.reconcile_after_restore → healthy
```

Lệnh — mỗi dòng là **một tiến trình riêng**, và toàn bộ chuỗi **`đã chạy ở đây`** trên một DB
nháp (xem cảnh báo ở §9.6 về việc điều đó **không** phải một drill):

```bash
uv run rr-backup --database var/research-radar.db snapshot --artifact var/backups/<ngày>.db
uv run rr-backup --database var/research-radar.db maintenance --open --reason restore
uv run rr-backup --database var/research-radar.db verify  --snapshot-id <ULID>

uv run rr-backup --database var/research-radar.db \
  restore --snapshot-id <ULID> --request-id <id của bạn> --confirm RESTORE \
  --target-database var/restored.db

uv run rr-backup --database var/research-radar.db status  --restore-id <ULID>
uv run rr-backup --database var/research-radar.db review  --restore-id <ULID> --intent-id <ULID> --decision hold
uv run rr-backup --database var/research-radar.db ack     --restore-id <ULID> --principal "ACT-backup-operator" --note "<ghi chú>"
uv run rr-backup --database var/research-radar.db reconcile --restore-id <ULID>
```

**Kỳ vọng đã quan sát:**

- `restore` trả `{"restore_id": …, "new_restore_generation": 1, "leases_revoked": 0,
  "storage_health": "recovery_required", "integrity_check_outcome": "not_run",
  "dispatcher_unlocked_at": null}`, thoát `0`. `dispatcher_unlocked_at` là `null` **có chủ
  đích**: không đường nào ở đây mở lại side effect.
- `status` in bảy mệnh đề của `reconciliation_complete` dưới dạng `clauses_met` /
  `clauses_unmet` + `unmet_detail`. Ngay sau restore: `clauses_met [2,3,4,5,6]`,
  `clauses_unmet [1,7]` với `"1": "integrity_check_outcome = 'not_run'"` và
  `"7": "chưa có operator_ack_at/operator_ack_principal"`. Thoát `2` khi chưa đủ.
- `ack` trả `{"restore_id": …, "operator_ack_at": "<ISO-8601 UTC ms>"}`, thoát `0`. **Mệnh đề 7
  là lý do không có đường tự động: máy không thể tự xác nhận rằng con người đã nhìn.**
- `reconcile` khi chưa đủ trả
  `{"code": "RESTORE_UNVERIFIED", "message_safe": "Bản khôi phục chưa được đối soát; side effect vẫn khóa.", "details_safe": {"storage_health": "recovery_required"}, "unmet_clauses": [1]}`,
  thoát `2`. Đó là hành vi **đúng**: `I15`/`NC-10` cấm tự rời `recovery_required`. Ở vòng
  trước, cùng lệnh này báo `"storage_health": "healthy"` vì nó đọc một guard mới trong bộ nhớ;
  nay nó đọc trạng thái bền, nên con số bạn thấy là trạng thái **thật**.

`--confirm` phải là đúng chuỗi `RESTORE`.

> **Một thông báo đáng khen, đáng biết trước.** Nếu bạn chạy `rr-backup` trên một database đã
> `migrate` nhưng **chưa** `bootstrap-owner`, nó **không** nói "không tìm thấy snapshot" nữa mà
> nói đúng thứ đang thiếu và cách sửa:
> `{"code":"NOT_FOUND","details_safe":{"resource_kind":"owner"},"message_safe":"Chưa có hàng `owner` nào: cơ sở dữ liệu đã migrate nhưng chưa bootstrap. Chạy `uv run rr-admin bootstrap-owner` rồi thử lại."}`
> (`F-A3-P5R2-01`, đã sửa và đã được audit `A3-P5-R3` kiểm cả hai chiều — hỏi một snapshot
> không tồn tại **vẫn** nói *snapshot*, nên thông báo được phân biệt theo `resource_kind` chứ
> không bị thay trọn gói.)

### 9.6 Drill bạn nên chạy, và đo cái gì

`backup-restore.md` §4 đặt **`RPO` 24 giờ**, **`RPO` cho Saved 24 giờ**, **`RTO` 2 giờ** — cả
ba đều `PROVISIONAL`. Chúng là **mục tiêu**, không phải phép đo. Một drill đúng nghĩa
(`§5.7`) phải thu:

`restore_id`, `backup_snapshot_id`, `manifest_sha256`, `artifact_sha256`, kết quả
`integrity_check`, **bảng counts kỳ vọng/quan sát**, số lease thu hồi, **danh sách intent
generation cũ và quyết định cho từng cái**, **số outbound send trước khi mở dispatch (oracle:
0)**, thời điểm `dispatcher_unlocked_at`, **tổng thời gian** (đối chiếu `RTO`), và **mọi bước
phải làm bằng tay**.

> **`chưa chạy ở đây`** — drill vào **môi trường thật, sạch**. Cái đã chạy trong lúc soạn tài
> liệu là một lần dựng lại trên một file SQLite nháp, mức E2, để quan sát **hình dạng output**.
> Nó **không** đo `RPO`/`RTO`, **không** dùng dữ liệu thật, **không** thay thế drill.
> `backup-restore.md` §5.7: **"Trạng thái hiện tại: `NOT_RUN`. Chưa có drill nào được thực
> hiện."** Đây là mục 4 trong danh sách việc-chỉ-Owner-làm-được (`review.md` §17.6).

### 9.7 Cái **không** nằm trong backup

`backup-restore.md` §6 và `secrets.md` §6:

| Mục | Khôi phục thế nào |
| --- | --- |
| Profile Chrome + phiên X | **Đăng nhập X lại bằng tay** trong profile riêng của dự án. Lần đầu X thường đòi xác minh thiết bị mới. Đây là việc thủ công **đã biết trước**, không phải sự cố. |
| Token collector / analysis worker | Sinh token mới trong app, cập nhật file `0600`, khởi động lại worker. |
| Master key của secret store | **Kế hoạch khôi phục secret riêng** của bạn. Mất master key ⇒ ciphertext trong backup vô dụng ⇒ phải nhập lại API key. |

Và một điều dễ quên (`secrets.md` §9): `data.purge_all` **không** chạm tới backup artifact đã
tạo. Dữ liệu bạn vừa xoá **vẫn còn trong các bản backup** cho tới khi chúng hết hạn hoặc bị xoá
bằng tay. Hộp thoại xác nhận **phải nói rõ** điều đó.

---

## 10. Các cửa kiểm bạn chạy được ngay hôm nay

**`đã chạy ở đây`**:

```bash
make ci
```

`Makefile`: `ci: openapi e0 cards gen-check lint test` — **đúng những gì CI chạy, theo thứ tự
của CI**. Không target nào chạm X, provider AI hay Telegram.

**Kỳ vọng (đã quan sát, thoát `0`, ~3 phút):**

| Bước | Dòng kết luận |
| --- | --- |
| `openapi` | `contracts/http/openapi.yaml: OK` |
| `e0` | `TOTAL: 27 checks — PASS 27 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0` |
| `cards` | `TOTAL: 13 checks over 20 cards — 13 PASS, 0 FAIL, 0 BLOCKED, 3963 assertions, 0 violations` |
| `gen-check` | `generated tree matches a fresh run of the generator` |
| `lint` | `All checks passed!` (eslint), `188 files already formatted` (ruff), `Success: no issues found in 101 source files` (mypy) |
| `test` | `1179 passed, 3 xfailed` (pytest, ~188 s) rồi `Test Files 6 passed · Tests 126 passed` (vitest) |

*(Con số của vòng trước — 19 card, 3731 assertion, 1042 test — đã cũ: đợt nối dây thêm card thứ
20 `TC-secret-settings-service` và các test của nó.)*

Các target lẻ khi bạn chỉ muốn một phần: `make openapi`, `make e0`, `make cards`,
`make gen-check`, `make lint`, `make test`. `make clean` xoá cache công cụ và `web/dist`, và
**không bao giờ** chạm `contracts/` hay `evidence/`.

Đặt `PYTHONDONTWRITEBYTECODE=1` — `Makefile` đã export sẵn, nên `__pycache__` không rơi vào cây
nguồn.

**Hai cửa "không sửa tay"** (`README.md` §3.1) đáng biết vì chúng sẽ chặn bạn nếu bạn sửa nhầm
chỗ: model Pydantic, hằng số enum và client TypeScript đều **sinh từ `contracts/`**. Muốn đổi
hành vi: **sửa hợp đồng → `make gen` → card thành `STALE` theo `INV-06`.** Và fixture ở
`acceptance/fixtures/**` **là oracle duy nhất** — sửa fixture để test pass là vi phạm
`SRC-PLAN §15`, phải đi qua `precode/change-control.md`.

---

## 11. Bảng khoảng trống — đã đóng và còn mở

Mười khoảng trống ghi ở vòng đầu. **Sáu đã đóng** qua hai đợt (`PKT-P0-FIX5` và đợt nối dây
`feat: integration wiring`), **bốn còn mở**. Mục đã đóng được gạch chứ **không xoá**, để bản ghi
vẫn đọc được — và để bạn thấy điều gì đã thay đổi, không chỉ trạng thái hôm nay.

Nguồn cho cột "quan sát được": ba báo cáo audit độc lập
[`A3-P5-R1`](../evidence/audits/A3-P5-R1-report.md),
[`A3-P5-R2`](../evidence/audits/A3-P5-R2-report.md),
[`A3-P5-R3`](../evidence/audits/A3-P5-R3-report.md), cộng lần chạy lại toàn bộ khi soạn bản này.

### 11.1 Sáu khoảng trống **đã đóng**

| # | Đã đóng bằng gì | Quan sát được |
| --- | --- | --- |
| ~~`G-1`~~ | `rr-admin bootstrap-owner` / `make bootstrap` | Hỏi mật khẩu, **không hiện lại**, **không** có `--password`; in đúng một ULID. [§3](#3-tạo-tài-khoản-owner-duy-nhất) |
| ~~`G-2`~~ | `server/app/settings.py` + `server/app/wiring.py`, nối qua **lifespan** của `server.app.main:app` | `auth.login` **200** + cookie đúng cờ; readiness / `/v1/runs` / `/v1/settings` / `/v1/saved` đều **200** trên uvicorn thật. [§4.0](#40-điều-phải-đọc-trước--khoảng-trống-g-2--đã-đóng-pkt-p0-fix5) |
| ~~`G-3`~~ | migration `0015_tc_storage_maintenance_window` — `storage.health` **bền** | `maintenance --open --reason` ở tiến trình 1, `restore` **qua được** ở tiến trình 2; `recovery_required` đọc lại đúng ở tiến trình 3. [§9.4](#94-cửa-sổ-bảo-trì--điều-kiện-tiên-quyết-của-restore) |
| ~~`G-4`~~ | `rr-admin migrate` / `make migrate` dựng config bằng đường dẫn tuyệt đối | Chạy từ **thư mục tạm ngoài repo**, lên tới `0015`, in `done`. `alembic.ini` và `env.py` **không** bị sửa. [§2.2](#22-chạy-migration-từ-một-file-trắng) |
| ~~`G-5`~~ | probe giải `output_dir` theo **cwd** và in đường dẫn đã chọn | `--dry-run` từ thư mục tạm: **không ghi gì** — kiểm lại bằng `find`, chỉ còn `cfg.json`. [§6.3](#63-đường-dẫn-đầu-ra--khoảng-trống-g-5-đã-đóng) |
| ~~`G-6`~~ | card thứ 20 `TC-secret-settings-service`: `server/app/secret/` + `settings_service/`, migration `0014`, AES-256-GCM | Master key **không đặt** ⇒ chạy được, `secret.*` từ chối; **đặt sai** ⇒ **từ chối khởi động**. [§8.4](#84-api-key-để-ở-đâu) |

### 11.2 Bốn khoảng trống **còn mở** — và ba trong bốn chỉ **bạn** đóng được

| # | Khoảng trống | Hệ quả với bạn | Ai đóng được |
| --- | --- | --- | --- |
| `G-7` | **Vòng chạy collector/worker chưa từng nói chuyện với một server thật.** Cả hai nay là tiến trình thật và **từ chối có lý do** khi thiếu `RR_SERVER_URL`; nhưng đăng ký + heartbeat + claim **chưa từng được quan sát** đầu-cuối. Audit `A3-P5-R1` ghi rõ vòng backoff của adapter bị tắt cũng chưa chạy như một tiến trình | **"collector online"** (`deployment.md` §6) vẫn chưa từng xảy ra | **Bạn** — cấu hình hai tiến trình và chạy chúng cùng server |
| `G-8` | **Cô lập AI `ISO-01..05` = `unverified`**, E3 `NOT_RUN`. `MOD-secret-service` nay tồn tại nên `ISO-05` **đã có thứ để chạy denied-case**, nhưng lần chạy đó chưa diễn ra | Cả hai adapter `enabled: false`; `--print-adapters` in `"ac16": "BLOCKED"` | **Bạn** — chạy probe cô lập E3 ([§8.3](#83-bạn-phải-làm-gì-để-bật-một-adapter)) |
| `G-9` | **Ba dữ kiện Bot API vẫn `KC`** (`CR-PC07-04`) | Telegram khoá ở phạm vi **chỉ chữ, không nút** | **Bạn** — đọc tài liệu Bot API ([§12.2](#122-mười-việc-chỉ-bạn-làm-được) mục 7) |
| `G-10` | **`rr-backup` vẫn so token với `RR_BACKUP_OPERATOR_TOKEN_EXPECTED` do chính người gọi đặt.** `Settings` nay có `backup_operator_token_sha256`, nhưng CLI **chưa dùng** nó (`tools/backup_cli.py` vẫn đọc `os.environ`) | Trên máy dùng chung, ai chạy được CLI thì tự cấp quyền | **Một card** — chưa ai được giao |

### 11.3 Bốn phát hiện audit còn `OPEN` mà bạn nên biết

Không phải khoảng trống của runbook, nhưng chúng chạm đúng những gì bạn sắp làm:

| ID | Nội dung | Trạng thái |
| --- | --- | --- |
| `F-A3-P5-03` | `GET /v1/reports` trả `500 INTERNAL` cho một tình huống **hoàn toàn dự đoán được**. `message_safe` nay nói rõ nguyên nhân và `CR-P0-07`, nhưng mã lỗi vẫn là "bất ngờ" | `OPEN` — [§4.1](#41-server) |
| `F-A3-P5-04` | `python tools/backup_cli.py` chết bằng `ModuleNotFoundError`, trong khi `python tools/rr_admin.py` chạy được | `OPEN` — tài liệu này vì vậy dùng **console script** (`rr-backup`, `rr-admin`) ở mọi chỗ |
| `CR-P0-07` | `TagConfigVersionPort` chưa có hiện thực; không model embedding thật (`REQ-OQ09`) | `OPEN` — chặn `report_context` |
| `CR-TC-SECRET-01` | `entities.yaml` chưa khai bảng nào cho **material** của secret store; nó nằm sau `SecretMaterialStore` ngoài database | `OPEN` — [§8.4](#84-api-key-để-ở-đâu) |

---

## 12. Điều hệ này **chưa** chứng minh

Mục này phản chiếu [`README.md`](../README.md) §6 và
[`precode/review.md`](../precode/review.md) §17.6–§17.7. **Đọc nó trước khi kết luận bất cứ điều
gì từ một lệnh xanh.**

### 12.1 Cửa kiểm xanh chứng minh cái gì — và không chứng minh cái gì

- **Hệ thống nay khởi động và chạy như những tiến trình thật** — đó là điều đợt nối dây đổi, và
  §§2–4 của tài liệu này là bằng chứng. Nhưng **`E3` và `E4` vẫn bằng 0 ở mọi nhóm scenario**:
  chưa một lời gọi thật nào tới X, Telegram hay một provider AI, ở bất kỳ giai đoạn nào.
  *(Bản trước của dòng này ghi "không có hành vi nghiệp vụ nào tồn tại"; điều đó đúng vào
  2026-09-08 và **không còn đúng** sau commit `feat: integration wiring`.)*
- **Một route owner-facing vẫn hỏng**: `GET /v1/reports` trả `500` (`CR-P0-07`) — [§4.1](#41-server).
- **`make e0` xanh chỉ chứng minh tính nhất quán nội bộ của tập con đã kiểm.** Xem
  `evidence/tools/README.md` §1 và §5 về giới hạn đã biết của chính công cụ đó.
- **`make cards` xanh chỉ nói card khớp với hợp đồng mà nó pin.** Nó **không đọc nội dung
  card**.
- **`make test` xanh chứng minh mã khớp fixture**, mà fixture là oracle **viết tay**. Chưa lần
  gọi X, Telegram hay provider AI nào ở bất kỳ giai đoạn nào.
- **Chưa có race test đa tiến trình** — an toàn đồng thời ở mức nhiều tiến trình chưa được
  chứng minh.
- **`E0-20` / `E0-21` chưa được kiểm độc lập**: cả hai do PC09 viết và tự kiểm bằng công cụ PC09
  vừa sửa.

### 12.2 Mười việc chỉ **bạn** làm được

`review.md` §17.6, nguyên danh sách — không Worker nào được phép thay bạn làm:

| # | Việc | Mở khoá |
| --- | --- | --- |
| 1 | **Chạy probe X** (`SP1`): cài Playwright, đăng nhập tay vào Chrome profile riêng, ký bốn `owner_confirmations` kèm `evidence_ref`, chạy 5–10 đợt | `SP1`, `REQ-A1`, `REQ-A7`, `REQ-AC16`, `SC51`, và giới hạn thật `REQ-OQ05` |
| 2 | **Bật một adapter AI và chạy thật** (E3) — cả hai `enabled: false` vì **cô lập** (`ISO-03`/`ISO-05`), **không** vì điều khoản | `SC16`, `SC17`; `REQ-AC16` thoát `BLOCKED` |
| 3 | **Gửi thật một tin Telegram** (E3) | `SC14` |
| 4 | **Chạy một drill restore thật** vào môi trường sạch, **đo** `RPO`/`RTO` | `SC43`, `G6-X3` |
| 5 | **Đọc và review giao diện thật** trên desktop và điện thoại (E4) | `SC10`, `SC11`, `SC15` |
| 6 | **Đọc 3–4 kỳ báo cáo thật** để hiệu chỉnh `REQ-A2`/`REQ-A4` | `G7`, rubric mật độ |
| 7 | **Đọc tài liệu Bot API** cho ba dữ kiện `delivery.md` §3.4 | `CR-PC07-04`, `SC46` |
| 8 | **Chốt các giá trị `PROVISIONAL`**: N backfill (`REQ-OQ04`), model embedding (`REQ-OQ09`), ba số của link code (`CR-PC07-01`) | các dòng `KC` tương ứng |
| 9 | **Trả lời chính sách nguồn**: arXiv/OpenAlex/X có cho phép xử lý lại nội dung của họ không | một câu hỏi pháp lý còn mở — `TC-A5-01` chỉ phủ điều khoản **Anthropic** |
| 10 | **Quyết định `MOD-tag-service`** — chưa card nào viết nó | `CR-TC-BACKFILL-07` |

Mục 5 đáng nói thêm: 126 test Vitest chứng minh ba trạng thái sinh ra **ba chuỗi khác nhau**.
*"Khác nhau ở mức người dùng hiểu được"* là **phán đoán của người** — của bạn.

### 12.3 Một câu để nhớ

Tài liệu này chứng minh rằng **các tiến trình khởi động được và các cửa kiểm tĩnh xanh**. Nó
không chứng minh — và không được đọc như thể chứng minh — rằng hệ thống **hoạt động**. Mọi
khẳng định về runtime cần một lần **chạy** với bằng chứng, và những lần chạy đó nằm ở §12.2,
trong tay bạn.
