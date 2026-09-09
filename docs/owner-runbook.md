# Owner runbook — chạy và tự kiểm Research Radar trên máy của bạn

> **Tài liệu này là gì.** Một hướng dẫn đầu-cuối để **Owner tự chạy** những gì repo này
> hiện có, theo đúng thứ tự. Nó không thay thế hợp đồng: mỗi bước dẫn ra file hợp đồng
> quyết định bước đó.
>
> **Tài liệu này KHÔNG nói sản phẩm chạy được.** Xem [§10](#10-điều-hệ-này-chưa-chứng-minh)
> trước khi kết luận bất cứ điều gì từ một lệnh chạy thành công.

Ngày viết: **2026-09-08**. Uỷ quyền: Owner 2026-09-08 (`AUTH-OWNER-20260908-11`).
Bối cảnh trạng thái: [`README.md`](../README.md) §6, [`docs/master-plan.md`](master-plan.md),
[`precode/review.md`](../precode/review.md) §17.5–§17.7.

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
một mảnh — nằm ở [§11](#11-bảng-khoảng-trống). Chúng được nhắc ngay tại bước liên quan, dưới
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
> Nay đã có CLI: `tools/rr_admin.py bootstrap-owner` (hoặc `make bootstrap`). Nó **hỏi mật khẩu
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
uv run python tools/rr_admin.py bootstrap-owner < /đường/dẫn/mật-khẩu-0600
```

**Kỳ vọng:** đúng một dòng — ULID của owner, ví dụ dạng `01M1ZH…` (26 ký tự Crockford base32).
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
> | Không nối | Lý do |
> | --- | --- |
> | `report_context` | `PublishContext` **bắt buộc** `tag_port` và `embedding_port`. `TagConfigVersionPort` **chưa có** hiện thực nào (`CR-TC-REPORT-01`), và `LocalEncoder` chỉ có hiện thực trong test vì model embedding còn là `REQ-OQ09`/`REQ-A3`. Cắm encoder băm của test vào một deployment thật sẽ ghi vector mà **không model nào** sinh ra. Xem `CR-P0-07` |
> | `delivery.transport`, `analysis.provider_config` | cần credential, mà `MOD-secret-service` chưa tồn tại (khoảng trống `G-6`, wave 2) |
> | `telegram_ingress_secret` | chưa đặt `RR_TELEGRAM_WEBHOOK_SECRET` ⇒ **mọi update bị từ chối**, đúng hướng default-deny |
> | `research_connector` | bốn dữ kiện `REQ-A6` còn `PLACEHOLDER_KC` |
>
> Hệ quả: §7 (Telegram) và §8 (AI) **vẫn bị chặn**, nhưng nay bị chặn vì **thiếu credential và
> thiếu một quyết định của Owner**, không còn vì thiếu composition root.

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

**`đã chạy ở đây`**:

```bash
uv run python -m worker.app.main --print-capabilities
```

**Kỳ vọng:** một object JSON —
`{"worker_kind":"analysis","agent_version":"0.1.0","schema_version":"0.3.0","tasks_supported":["label","summary","direction_phrasing"],"ai_providers":[]}`
— rồi thoát `0`.

**Chạy không tham số thì nó từ chối** — **`đã chạy ở đây`**:

```bash
uv run python -m worker.app.main
```

**Kỳ vọng:** `main.py: error: Phase 0 worker has no runnable behaviour; use --print-capabilities`,
thoát **`2`**. Đó là lời từ chối đúng, không phải lỗi cấu hình của bạn.

> **`KHOẢNG TRỐNG G-7`** — worker là **stub Giai đoạn 0**. Nó không đọc token, không gọi
> `worker.register_capabilities`, không gửi heartbeat, không claim task, không khởi động
> provider nào. `ai_providers` rỗng vì chưa adapter nào được bật ([§8](#8-ai)).
> Vì vậy **"collector online"** theo nghĩa `deployment.md` §6 (đăng ký hợp lệ **và** heartbeat
> trong `online_threshold` = 90 s **và** server ghi được) **chưa thể xảy ra**.

Cấu hình worker sẽ cần khi phần thật tồn tại (`secrets.md` §3, chưa có mã đọc nó): một file
**`0600`** trong thư mục cấu hình của user, **không bao giờ trong repo**, chứa
`analysis_worker_token`; worker phải **từ chối khởi động** nếu quyền file rộng hơn `0600`.

### 4.4 Collector

**`đã chạy ở đây`**:

```bash
uv run python -m collector.app.main --print-registration
```

**Kỳ vọng:** object JSON hình dạng payload `worker.register_capabilities`, với
`"collector_online": false`, `"chrome_profile_ready": false`, `"x_session_state": "unknown"`.
Ba giá trị đó là **cố ý**: `CAP-P5` cấm quy đổi `unknown` thành `ok`. Thoát `0`.

Không tham số → **`đã chạy ở đây`**: `error: Phase 0 collector has no runnable behaviour; use
--print-registration`, thoát **`2`**.

Collector **không** mở trình duyệt, **không** chạy `playwright install`, **không** gọi server,
**không** chạm Chrome profile (docstring `collector/app/main.py`). Token riêng của nó
(`collector_token`) tách khỏi token của analysis worker dù hai tiến trình cùng máy — bán kính
ảnh hưởng khác nhau (`secrets.md` §3).

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

### 6.3 Một cái bẫy đường dẫn — `KHOẢNG TRỐNG G-5`

> `output_dir` **tương đối** trong file config được giải theo **thư mục chứa file config**, chứ
> không theo thư mục làm việc (`probe/x_feasibility/config.py`: `out_path = (base_dir or
> Path.cwd()) / out_path`). Giá trị mặc định trong `probe/probe-config.example.json` là
> `evidence/runs/SP1-x-feasibility`, nên nếu bạn để config ở `~/rr-probe.json` thì bản ghi rơi
> vào `~/evidence/runs/SP1-x-feasibility/`, **không** vào repo.
>
> Đã quan sát: một lần `--dry-run` chạy thẳng với file mẫu trong repo đã tạo
> `probe/evidence/runs/SP1-x-feasibility/probe.log`.
>
> **Cách tránh:** đặt `output_dir` là **đường dẫn tuyệt đối** trỏ tới
> `<repo>/evidence/runs/SP1-x-feasibility`.

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
   → chặn bởi **`KHOẢNG TRỐNG G-6`**: chưa có `MOD-secret-service`.
3. Sinh một **webhook secret** ngẫu nhiên và đăng ký webhook với Telegram trỏ vào đường dẫn
   `POST /v1/telegram/webhook` của bạn qua **HTTPS 443**.

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

> ### `KHOẢNG TRỐNG G-6` — chưa có nơi để cất key
>
> `server/app/` **không có** thư mục `secret/` hay `settings/`. Ba operation của `ports.yaml`
> (`secret.store_provider_key`, `secret.issue_task_credential`, `secret.revoke_task_credential`)
> **chưa có mã**; chúng chỉ được **nhắc đến** trong docstring của `analysis/service.py`,
> `auth/middleware.py` và `worker/app/adapter/base.py`. Biến môi trường master key cũng chưa
> được đọc ở đâu.
>
> Nghĩa là: **hôm nay bạn không có chỗ hợp lệ nào để đặt API key.** Đừng đặt nó vào biến môi
> trường tuỳ tiện, đừng đặt vào file trong repo. Chờ card.

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
uv run python -m tools.backup_cli --database var/research-radar.db status --restore-id <ULID>
```

**Kỳ vọng:** JSON
`{"code":"UNAUTHORIZED","message_safe":"Thao tác này chỉ chấp nhận backup operator token.","required_auth_scope":"backup_operator"}`,
thoát **`3`**. Một `expected` chưa cấu hình là **từ chối**, không bao giờ là cho qua.

> **`KHOẢNG TRỐNG G-10`** — token "đúng" đến từ biến môi trường
> `RR_BACKUP_OPERATOR_TOKEN_EXPECTED` **do chính người gọi đặt**; không có nơi nào phía server
> lưu hay cấp phát nó. `secrets.md` §3 nói token phải nằm trong file `0600` trên server, nhưng
> chưa có mã nào đọc file đó ra thành `EXPECTED`. Trên một máy một người dùng đây là bất tiện;
> trên máy dùng chung nó có nghĩa là **ai chạy được CLI thì tự cấp quyền cho mình**.

### 9.2 Tạo snapshot

**`đã chạy ở đây`**:

```bash
export RR_BACKUP_OPERATOR_TOKEN=<token của bạn>
export RR_BACKUP_OPERATOR_TOKEN_EXPECTED="$RR_BACKUP_OPERATOR_TOKEN"
mkdir -p var/backups
uv run python -m tools.backup_cli --database var/research-radar.db \
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
uv run python -m tools.backup_cli --database var/research-radar.db verify --snapshot-id <ULID>
```

**Kỳ vọng:** `{"artifact_sha256_matches": true, "counts_match": true, "failed_conditions": [],
"mismatches": [], "pragma_integrity_check": "ok", "state": "verified"}`, thoát `0`.
Thoát `2` nếu bất kỳ điều kiện nào trượt.

### 9.4 Cửa sổ bảo trì — điều kiện tiên quyết của restore

`storage.yaml` `T-ST-05`: restore **bắt đầu từ `maintenance`** và **không tự mở** cửa sổ đó.
`restore.restore_snapshot()` **từ chối** khi store chưa ở `maintenance`; mở cửa sổ là một bước
CLI riêng, có chủ đích.

**`đã chạy ở đây`**:

```bash
uv run python -m tools.backup_cli --database var/research-radar.db maintenance --open
```

**Kỳ vọng:** `{"storage_health": "maintenance", "transition": "T-ST-03"}`, thoát `0`.

> ### `KHOẢNG TRỐNG G-3` — cửa sổ bảo trì **không sống qua hai lần gọi CLI**
>
> `StorageGuard` giữ `storage.health` **trong bộ nhớ tiến trình** ("One guard per process. It
> holds no connection and issues no SQL" — `server/app/storage/guard.py`). Không có bảng nào
> lưu nó. Vì vậy lần gọi `backup_cli` **tiếp theo** khởi động lại ở `healthy`, và
> `restore` bị chính điều kiện tiên quyết của nó từ chối.
>
> Đã quan sát, ngay sau lệnh `maintenance --open` ở trên:
>
> ```
> {"code": "VALIDATION_ERROR",
>  "details_safe": {"field_path": "storage_health",
>                   "operation_id": "backup.restore_snapshot",
>                   "violation_kind": "precondition_not_met"}}
> ```
> thoát `2`.
>
> Cùng nguyên nhân: sau một restore đưa store về `recovery_required`, lệnh `reconcile` ở tiến
> trình sau lại báo `"storage_health": "healthy"` — nó đọc guard mới, không đọc trạng thái
> thật.
>
> **Hệ quả:** **quy trình restore hai bước bằng CLI như tài liệu mô tả hiện không hoàn tất
> được.** Cơ chế restore *tự nó* đúng — chạy `enter_maintenance()` rồi `restore_snapshot()`
> **trong cùng một tiến trình** thì thành công (đã kiểm: trả `restore_id`,
> `new_restore_generation = 1`, `leases_revoked = 0`, `storage_health = recovery_required`).
> Cái thiếu là **chỗ lưu bền cho `storage.health`**.

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

Lệnh (**`đã chạy ở đây`** trên một DB nháp — xem cảnh báo dưới):

```bash
uv run python -m tools.backup_cli --database var/research-radar.db \
  restore --snapshot-id <ULID> --request-id <id của bạn> --confirm RESTORE \
  --target-database var/restored.db

uv run python -m tools.backup_cli --database var/research-radar.db status  --restore-id <ULID>
uv run python -m tools.backup_cli --database var/research-radar.db review  --restore-id <ULID> --intent-id <ULID> --decision hold
uv run python -m tools.backup_cli --database var/research-radar.db ack     --restore-id <ULID> --principal "ACT-backup-operator" --note "<ghi chú>"
uv run python -m tools.backup_cli --database var/research-radar.db reconcile --restore-id <ULID>
```

**Kỳ vọng đã quan sát:**

- `status` in bảy mệnh đề của `reconciliation_complete` dưới dạng `clauses_met` /
  `clauses_unmet` + `unmet_detail`. Trên drill nháp: `clauses_met [2,3,4,5,6]`,
  `clauses_unmet [1,7]` với `"1": "integrity_check_outcome = 'not_run'"` và
  `"7": "chưa có operator_ack_at/operator_ack_principal"`. Thoát `2` khi chưa đủ.
- `ack` trả `{"restore_id": …, "operator_ack_at": "<ISO-8601 UTC ms>"}`, thoát `0`. **Mệnh đề 7
  là lý do không có đường tự động: máy không thể tự xác nhận rằng con người đã nhìn.**
- `reconcile` khi chưa đủ trả
  `{"code": "RESTORE_UNVERIFIED", "message_safe": "Bản khôi phục chưa được đối soát; side effect vẫn khóa.", "unmet_clauses": [...]}`,
  thoát `2`. Đó là hành vi **đúng**: `I15`/`NC-10` cấm tự rời `recovery_required`.

`--confirm` phải là đúng chuỗi `RESTORE`.

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
| `e0` | `TOTAL: 27 checks — PASS 27 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0` (302 file quét) |
| `cards` | `TOTAL: 13 checks over 19 cards — 13 PASS, 0 FAIL, 0 BLOCKED, 3731 assertions, 0 violations` |
| `gen-check` | im lặng — nghĩa là sinh lại **không** tạo diff |
| `lint` | `All checks passed!` (eslint) và `All matched files use Prettier code style!` |
| `test` | `1042 passed, 3 xfailed` (pytest, ~111 s) rồi `Test Files 6 passed · Tests 126 passed` (vitest) |

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

## 11. Bảng khoảng trống

Mười khoảng trống ghi ở vòng đầu. **Ba đã đóng** ở `PKT-P0-FIX5` (`G-1`, `G-2`, `G-4`) và được
gạch dưới đây thay vì xoá, để bản ghi vẫn đọc được. Bảy mục còn lại chưa được "vá tạm" ở đâu
trong tài liệu này.

| # | Khoảng trống | Hệ quả với bạn | Mục |
| --- | --- | --- | --- |
| ~~`G-1`~~ **ĐÃ ĐÓNG** (`PKT-P0-FIX5`) | ~~Chưa có CLI bootstrap Owner~~ → `tools/rr_admin.py bootstrap-owner` / `make bootstrap`: hỏi mật khẩu, không hiện lại, không nhận qua tham số | — | [§3](#3-tạo-tài-khoản-owner-duy-nhất) |
| ~~`G-2`~~ **ĐÃ ĐÓNG** (`PKT-P0-FIX5`) | ~~Chưa có composition root~~ → `server/app/settings.py` + `server/app/wiring.py`, nối qua lifespan của `server.app.main:app`. `auth.login` **200**, readiness **200**, `/v1/runs` **200** trên uvicorn thật. Còn lại: `report_context`, transport Telegram và provider AI chưa nối vì thiếu credential/quyết định — xem §4.0 và `CR-P0-07` | §7/§8 vẫn chặn, nhưng vì `G-6`/`G-8`/`G-9`, không còn vì `G-2` | [§4.0](#40-điều-phải-đọc-trước--khoảng-trống-g-2--đã-đóng-pkt-p0-fix5) |
| `G-3` | **`storage.health` chỉ sống trong bộ nhớ tiến trình** | Quy trình restore hai bước bằng CLI **không hoàn tất được** | [§9.4](#94-cửa-sổ-bảo-trì--điều-kiện-tiên-quyết-của-restore) |
| ~~`G-4`~~ **ĐÃ ĐÓNG** (`PKT-P0-FIX5`) | ~~`alembic` chỉ chạy khi cwd = `server/`~~ → `tools/rr_admin.py migrate` / `make migrate` dựng config bằng đường dẫn tuyệt đối và chạy từ thư mục nào cũng được (`server/alembic.ini` và `env.py` **không** bị sửa) | — | [§2.2](#22-chạy-migration-từ-một-file-trắng) |
| `G-5` | **`output_dir` của probe giải theo thư mục file config**, không theo cwd | Bản ghi probe rơi cạnh file config; một lần `--dry-run` đã tạo `probe/evidence/runs/SP1-x-feasibility/probe.log` | [§6.3](#63-một-cái-bẫy-đường-dẫn--khoảng-trống-g-5) |
| `G-6` | **Chưa có `MOD-secret-service` / `MOD-settings-service`.** Ba operation `secret.*` chưa có mã; master key chưa được đọc ở đâu | **Không có chỗ hợp lệ nào để đặt API key**; và `ISO-05` không kiểm chứng được vì không có gì để chạy denied-case | [§8.4](#84-api-key-để-ở-đâu) |
| `G-7` | **Collector và analysis worker là stub Giai đoạn 0** | Không đăng ký, không heartbeat, không claim ⇒ **"collector online" chưa thể xảy ra** | [§4.3](#43-analysis-worker), [§4.4](#44-collector) |
| `G-8` | **Cô lập AI `ISO-01..05` = `unverified`**, E3 `NOT_RUN` | Cả hai adapter `enabled: false`; bật chúng cần một lần **chạy quan sát được**, không phải một công tắc | [§8.2](#82-hai-adapter-đã-đăng-ký--và-vì-sao-cả-hai-enabled-false) |
| `G-9` | **Ba dữ kiện Bot API vẫn `KC`** (`CR-PC07-04`) | Telegram bị khoá ở phạm vi **chỉ chữ, không nút**; `callback_data` chưa có bộ phân tích | [§7.3](#73-ba-lệnh--và-phạm-vi-chỉ-chữ-không-nút) |
| `G-10` | **`RR_BACKUP_OPERATOR_TOKEN_EXPECTED` do chính người gọi đặt**; không có nguồn phía server | Trên máy dùng chung, ai chạy được CLI thì tự cấp quyền | [§9.1](#91-xác-thực-backupoperatortoken-và-chỉ-nó) |

---

## 12. Điều hệ này **chưa** chứng minh

Mục này phản chiếu [`README.md`](../README.md) §6 và
[`precode/review.md`](../precode/review.md) §17.6–§17.7. **Đọc nó trước khi kết luận bất cứ điều
gì từ một lệnh xanh.**

### 12.1 Cửa kiểm xanh chứng minh cái gì — và không chứng minh cái gì

- **Không có hành vi nghiệp vụ nào tồn tại; `E1–E4` vẫn `NOT_RUN`** ở mọi nhóm scenario, qua cả
  sáu giai đoạn. Bộ khung boot được, lint sạch, test xanh — và không làm gì cả.
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
