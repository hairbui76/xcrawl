# Research Radar

Repo này chứa **hợp đồng** của hệ thống (`contracts/`, `acceptance/`, `precode/`,
`agent-tasks/`) và **bộ khung triển khai** dựng ở Giai đoạn 0 (`server/`, `collector/`,
`worker/`, `probe/`, `shared/rr_contracts/`, `tests/`, `web/`).

> **Chưa có hành vi nghiệp vụ nào.** Bộ khung boot được, lint sạch, test xanh — và không
> làm gì cả. Mọi hành vi được giao bằng card ở `agent-tasks/`, và card chỉ chạy sau khi
> cổng **G5** đạt và Owner ra lệnh. Xem [`docs/master-plan.md`](docs/master-plan.md).

Điểm vào để đọc: [`precode/README.md`](precode/README.md) (toàn bộ baseline) và
[`docs/master-plan.md`](docs/master-plan.md) (lộ trình bảy giai đoạn).
Toolchain: [`precode/adr/ADR-0011`](precode/adr/ADR-0011-frameworks-and-toolchain.md).

---

## 1. Cài đặt

Cần: **Python 3.12**, [`uv`](https://docs.astral.sh/uv/), **Node 22**.

```bash
uv sync --all-packages     # môi trường Python từ uv.lock
cd web && npm ci && cd ..  # phụ thuộc web từ package-lock.json
# hoặc: make setup
```

**Không có bước nào tải model hay trình duyệt.** `playwright install` là việc trên máy của
Owner, không phải bước cài của repo; `sentence-transformers` là extra khai báo sẵn
(`server/pyproject.toml`, nhóm `embedding`) và **không** được cài bởi `uv sync --all-packages`, vì model
embedding cụ thể còn là `REQ-OQ09`/`REQ-A3` chưa chốt.

## 2. Chạy

### 2.1 Khởi động thật (theo thứ tự — `docs/owner-runbook.md` §§2–4)

Ba lệnh, đúng thứ tự này. Bỏ lệnh nào cũng hỏng theo cách nói rõ nó thiếu gì.

```bash
make migrate      # tạo/nâng cấp database (alembic upgrade head, chạy từ thư mục nào cũng được)
make bootstrap    # tạo tài khoản Owner duy nhất — hỏi mật khẩu, KHÔNG hiện lại, KHÔNG nhận qua tham số
make serve        # uvicorn server.app.main:app trên 127.0.0.1:8080
```

Năm **console script** làm đúng việc đó mà **không cần đứng ở gốc repo** — đây là đường được
hỗ trợ khi bạn chạy từ thư mục khác:

| Lệnh | Là gì |
| --- | --- |
| `uv run rr-admin {migrate,bootstrap-owner,status}` | ba lệnh vận hành ở trên |
| `uv run rr-backup …` | CLI backup/restore (`tools/backup_cli.py`) |
| `uv run rr-collector --print-registration` | collector trên máy cá nhân |
| `uv run rr-worker --print-capabilities` | analysis worker trên máy cá nhân |
| `uv run rr-probe --config … [--dry-run]` | probe khả thi SP1 |

Từ một thư mục bất kỳ, thêm `--project <đường-dẫn-repo>`:
`uv run --project /path/to/xcrawl rr-admin status`. Gọi thẳng file
(`uv run python tools/rr_admin.py …`) vẫn chạy, nhưng chỉ từ gốc repo.

`make status` cho biết đang ở bước nào (`absent` → `unmigrated` → `no owner row` → `ready`) và
**liệt kê chính xác** những gì một tiến trình server sẽ nối và những gì **không**, kèm lý do.

Cấu hình lấy từ biến môi trường (`server/app/settings.py`), tất cả đều có mặc định an toàn trừ
secret:

| Biến | Mặc định | Ghi chú |
| --- | --- | --- |
| `RR_DATABASE_URL` | `<RR_DATA_DIR>/research-radar.db` | nhận cả đường dẫn trần lẫn URL `sqlite+pysqlite:///` |
| `RR_DATA_DIR` | `./var` | đã nằm trong `.gitignore` |
| `RR_TIMEZONE` | `Asia/Ho_Chi_Minh` | giá trị Owner đã chấp nhận (`OD-20260907-01` mục 4) |
| `RR_SCHEDULE_SLOTS` | `08:00,20:00` | giá trị Owner đã chấp nhận (mục 20); `REQ-OQ05` sẽ đo lại |
| `RR_TELEGRAM_WEBHOOK_SECRET` | **không có** | thiếu ⇒ mọi update Telegram bị từ chối |
| `RR_{COLLECTOR,ANALYSIS_WORKER,BACKUP_OPERATOR}_TOKEN_SHA256` | **không có** | cấu hình bằng **hash**, không bao giờ bằng token |

Server đọc database qua **lifespan lúc khởi động**: `create_app()` gọi trần vẫn là app rỗng
không cấu hình (mọi test của card dựa vào điều đó), còn `server.app.main:app` — chuỗi import mà
`make serve` và runbook dùng — tự nối khi tiến trình bắt đầu phục vụ. Import module **không**
tạo file database.

Web dev: `cd web && npm run dev`. Server dev có reload: `uv run uvicorn server.app.main:app --reload`.

### 2.2 Kiểm tra và cửa

| Lệnh | Làm gì |
| --- | --- |
| `make test` | `pytest` toàn cây Python, rồi `vitest` |
| `make lint` | `ruff` + `ruff format --check` + `mypy --strict` (`server/app`, `worker/app`, `collector/app`, `probe`) + `eslint` + `prettier` + `tsc` |
| `make gen` | sinh lại **toàn bộ** code sinh từ `contracts/` |
| `make gen-check` | fail nếu sinh lại tạo ra khác biệt — đây là cửa "không sửa tay" |
| `make e0` | 24 phép kiểm tĩnh E0 trên baseline hợp đồng (chỉ đọc) |
| `make cards` | kiểm hash đã pin của 18 card + quy tắc hai ngôn ngữ |
| `make openapi` | validate `contracts/http/openapi.yaml` bằng validator OpenAPI 3.1 thật |
| `make ci` | đúng những gì CI chạy, theo thứ tự của CI |

## 3. Hai quy tắc không thương lượng

`docs/master-plan.md` §2.3. Chúng không phải lời khuyên; cả hai đều có cửa kiểm.

### 3.1 Sinh từ hợp đồng, **không viết tay**

Model Pydantic, hằng số enum và client TypeScript đều sinh từ `contracts/`:

| Sinh ra | Từ | Bằng | Cửa kiểm |
| --- | --- | --- | --- |
| `shared/rr_contracts/rr_contracts/generated/` | `contracts/schemas/*.json`, `state/*.yaml`, `errors.yaml`, `ports.yaml`, `http/openapi.yaml` | `shared/rr_contracts/generate.py` | `shared/rr_contracts/tests/test_generated_matches_contracts.py` |
| `web/src/generated/openapi.d.ts` | `contracts/http/openapi.yaml` | `web/scripts/generate.mjs` | `web/tests/contract/generatedClient.test.ts` |

Mỗi file sinh ra mở đầu bằng `GENERATED — do not edit; source sha256 …`, và mỗi thư mục
sinh ra có `GENERATED_FROM.json` ghi hash của từng nguồn. Hai bộ test trên fail khi
**(a)** hash nguồn lệch khỏi bản ghi, hoặc **(b)** sinh lại tạo ra diff — tức có người sửa
tay.

Muốn đổi hành vi: **sửa hợp đồng → sinh lại → card thành `STALE` theo `INV-06`.**

### 3.2 Fixture **là** oracle duy nhất

Test nạp thẳng `acceptance/fixtures/**` qua loader ở `tests/conftest.py`
(xem [`tests/README.md`](tests/README.md)). **Không có bộ dữ liệu test thứ hai.** Sửa
fixture để test pass là vi phạm SRC-PLAN §15 — nó là change request theo
`precode/change-control.md`.

## 4. Bố cục

```
server/     Python      FastAPI app; server/app/<domain>/… đặt tên theo MOD-*; migrations Alembic
collector/  Python      collector Playwright, chạy trên máy cá nhân (D09)
worker/     Python      analysis worker + adapter AI (API qua httpx, CLI/ACP qua subprocess)
probe/      Python      kịch bản probe SP1 — trống cho tới khi cổng Owner mở
shared/rr_contracts/    model + hằng số SINH RA từ contracts/
tests/      Python      tests/contract/, tests/integration/ — dùng fixture làm oracle
web/        TypeScript  Vite + React 18; src/{lib,routes,views}, tests/{contract,integration}
```

Import root là **gốc repo**: `server/app/…` import là `server.app.…`, `collector/app/…` là
`collector.app.…`. Nhờ vậy ba gói `app` không đụng nhau trên cùng một `sys.path`, và
**đường dẫn file mà card đã pin ở §3 không đổi**.

**Quy tắc hai ngôn ngữ** (`agent-tasks/README.md` §5.3): không file `.py` nào dưới `web/`;
không file `.ts`/`.tsx` nào dưới `server/`, `collector/`, `worker/`, `probe/`.
`evidence/tools/verify_cards.py` ép điều này bằng máy, trên cả card lẫn cây file thật.

## 5. CI

Bốn job, **không job nào chạm mạng ngoài registry gói**.

| Job | Chạy gì |
| --- | --- |
| `openapi` | validator OpenAPI 3.1 trên `contracts/http/openapi.yaml` — chạy **trước** mọi bước sinh code |
| `e0` | `evidence/tools/e0_check.py` + `evidence/tools/verify_cards.py`, rồi khẳng định repo không bị ghi |
| `python` | `uv sync --all-packages --frozen`, ruff, mypy, cửa "sinh lại không diff", `pytest` |
| `web` | `npm ci`, eslint + prettier, `tsc`, cửa "sinh lại không diff", `vitest` |

**Không có job live.** E3 (chạy thật) và E4 (đánh giá) là thủ công theo giao thức; CI không
được phép chạm X, provider AI hay Telegram.

## 6. Điều repo này **chưa** chứng minh

- Không có hành vi nghiệp vụ nào tồn tại; E1–E4 vẫn `NOT_RUN`.
- `make e0` xanh chỉ chứng minh **tính nhất quán nội bộ của tập con đã kiểm** — xem
  `evidence/tools/README.md` §1 và §5 về những giới hạn đã biết của chính công cụ đó.
- `make cards` xanh chỉ nói rằng card **khớp với hợp đồng mà nó pin**. Nó không đọc nội
  dung card.
