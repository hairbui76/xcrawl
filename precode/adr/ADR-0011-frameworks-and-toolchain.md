---
adr_id: ADR-0011
title: Framework và toolchain cho stack B
status: provisional-accepted
decision_owner: Coordinator (được Owner ủy quyền 2026-09-07; Owner có thể phản đối)
date: 2026-09-07
ratified_by: null
evidence_ref: "Owner trả lời 'You pick, record as ADR' — Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07; ruling của Coordinator tại evidence/coordination/"
blocker_refs: []
source_refs: [SRC-SPEC §6.3, SRC-SPEC §6.4, SRC-SPEC:D07, SRC-SPEC:D09, SRC-SPEC:D48, SRC-SPEC:D49, SRC-SPEC:D50, SRC-SPEC:D59, SRC-SPEC §4]
requirement_refs: [REQ-D07, REQ-D09, REQ-D48, REQ-D49, REQ-D50, REQ-D59, REQ-S6.3-01, REQ-S6.4-01, REQ-S6.4-02, REQ-S6.4-03, REQ-S4-10, REQ-A3, REQ-OQ09]
invariant_refs: [I11, I15]
amendment_refs: []
decision_refs: [OD-20260907-01, PROV-PC00-07]
consumers: [PC10]
affected_packages: [PC10]
supersedes: []
depends_on: [ADR-0006]
claim_ceiling: DRAFT_FOR_REVIEW
---

# ADR-0011 — Framework và toolchain cho stack B

> **Phụ thuộc `ADR-0006`.** Toàn bộ ADR này chỉ có nghĩa với **stack B** (Python workers + TypeScript web) mà Owner đã chọn ở `OD-20260907-01` mục 3. Nếu lựa chọn stack đảo, ADR này phải viết lại.

## Bối cảnh

Owner đã chốt **B** ở mức ngôn ngữ: Python cho collector, worker, embedding và backend; TypeScript cho web app. Nhưng "Python + TypeScript" chưa đủ để một task card ghi được lệnh build và đường dẫn thật — vẫn còn phải chọn framework API, cách truy cập SQLite, cơ chế hàng đợi, thư viện Playwright, cách gọi Telegram, bộ test và CI.

Khi được hỏi, Owner trả lời **"You pick, record as ADR"** — tức ủy quyền lựa chọn kỹ thuật cho Coordinator, với điều kiện nó được ghi thành một ADR để Owner đọc lại và phản đối nếu muốn. Đó là lý do ADR này ở trạng thái `provisional-accepted` chứ không phải `accepted`: nó **không** phải một quyết định của Owner.

Ràng buộc đã có từ trước và **không** được lựa chọn nào ở đây đụng tới: SQLite là data store chuẩn (`REQ-D07`, XN); Chrome thật với profile riêng của dự án trên máy cá nhân (`REQ-D09`, nay XN); embedding chạy local ở server, không cần API key (`REQ-D48`/`REQ-D50`); tính tương đồng bằng quét tuyến tính ở MVP (`REQ-D49`); model embedding đa ngôn ngữ (`REQ-D59`); collector và worker chạy như tiến trình trên máy, không trong container (`REQ-S6.4-02`); **không có broker ngoài**; mỗi tầng một ngôn ngữ.

## Quyết định

Nguyên tắc xuyên suốt: **chọn mặc định bảo thủ**, và ở mỗi chỗ hợp đồng đã định nghĩa hành vi thì **không** thêm một framework tự định nghĩa lại hành vi đó.

| Tầng | Lựa chọn | Vì sao |
| --- | --- | --- |
| Python / packaging | **Python 3.12**, `uv` cho env và lock, một `pyproject.toml` cho mỗi package (`server`, `collector`, `worker`, và `rr_contracts` dùng chung) | Tái lập được, nhanh, một lock duy nhất; khớp kỷ luật `schema_version` của hợp đồng |
| Server API | **FastAPI + Pydantic v2**; model request/response **sinh từ** `contracts/schemas/*.json` và `contracts/http/openapi.yaml`, **không gõ tay** | OpenAPI-native, validate đúng wire contract, async được cho webhook Telegram |
| Persistence | **SQLAlchemy 2 Core** (không dùng ORM magic) + **Alembic**; `sqlite3` với WAL, `PRAGMA foreign_keys=ON`; backup qua **Online Backup API** (`sqlite3.Connection.backup`) | SQL tường minh để viết đúng các `TXN-*`; partial index và generated column cần kiểm soát ở mức Core; backup khớp `AMD-B11`/`ADR-0005` |
| Job queue / scheduler | **Bảng hàng đợi trong DB** đúng theo `contracts/data/entities.yaml` (`assignment`, `assignment_lease`, `schedule_occurrence`), chạy bằng một vòng lặp scheduler in-process theo quy tắc lease/epoch. Không cần APScheduler | Hợp đồng **đã** định nghĩa hàng đợi; thêm một broker là thêm một chủ sở hữu trạng thái thứ hai |
| Collector | **Playwright for Python**, persistent context trên profile Chrome riêng của dự án (`REQ-D09`); `httpx` gọi server API bằng bearer token | Đúng khuyến nghị SRC-SPEC §6.3; giữ cô lập profile |
| Analysis worker | `httpx` tới server; adapter provider: họ API dùng SDK/`httpx`, họ **CLI/ACP dùng `subprocess`** với cờ tool/network theo `contracts/ai/providers.yaml` | Yêu cầu cô lập của `ADR-0010` là **mức tiến trình** — chỉ `subprocess` mới thực thi được nó |
| Embedding | **`sentence-transformers`** ở server (model chọn sau `REQ-A3`); vector lưu dạng BLOB; cosine tính bằng Python (quét tuyến tính theo `REQ-D49`) | Local, không cần key; đáp ứng `REQ-D59` đa ngôn ngữ |
| Telegram | **Bot API trực tiếp qua `httpx`** (`sendMessage`/webhook), **không** dùng bot framework | Ngữ nghĩa outbox và receipt là của chúng ta; cơ chế retry của một framework sẽ **vi phạm `AMD-B03`** (không tự gửi lại khi `unknown`) |
| Web UI | **Vite + React 18 + TypeScript**, TanStack Query cho read model, API client **sinh từ** `openapi.yaml` (`openapi-typescript`); **không** bắt buộc UI kit | Thông dụng; client sinh tự động giữ đúng wire. Không chốt UI kit vì SRC-SPEC §4 cố ý để ngỏ phần visual design |
| Auth | Cookie session `HttpOnly` + CSRF double-submit (đã chốt ở PC05/PC08), Argon2id qua `argon2-cffi` | Đã có trong hợp đồng; không phát minh lại |
| Test | Python: `pytest` + fixture **nạp thẳng từ `acceptance/fixtures/**`** (E1), `pytest-asyncio`; fault injection SQLite bằng wrapper. Web: Vitest + Testing Library. E2E: Playwright Test. Contract lint: `evidence/tools/e0_check.py` trong CI | Fixture **là** oracle; tuyệt đối không dựng một bộ dữ liệu test thứ hai |
| Lint / format | `ruff` (kèm format), `mypy --strict` cho lõi server, `eslint` + `prettier`, `PYTHONDONTWRITEBYTECODE` trong CI | Rẻ, tiêu chuẩn |
| CI | GitHub Actions: job E0 (`e0_check` + trình kiểm pin của card), job Python (pytest E1), job web (vitest). **Không có job live** — E3/E4 là thủ công theo giao thức | Kỷ luật bằng chứng |
| Đóng gói / triển khai | Docker Compose cho server (web + api + embedding); collector và worker chạy như tiến trình trên máy (SRC-SPEC §6.4); secrets qua file mount, **không** dùng `.env` (theo PC08) | Đúng `REQ-S6.4-01` và `REQ-S6.4-02` |

**Bố cục repo — bảy thư mục.** Đường dẫn §3 của từng card **giữ nguyên như đã pin**.

| Thư mục | Nội dung | Nguồn khai |
| --- | --- | --- |
| `server/` | Ứng dụng FastAPI, domain service đặt tên theo `MOD-*`, migration Alembic | `agent-tasks/README.md` §5.3 |
| `collector/` | Collector Playwright chạy trên máy cá nhân | `agent-tasks/README.md` §5.3 |
| `worker/` | Analysis worker và AI adapter, chạy trên máy cá nhân | `agent-tasks/README.md` §5.3 |
| `web/` | Ứng dụng Vite + React + TypeScript | `agent-tasks/README.md` §5.3 |
| `tests/` | `contract/`, `unit/`, `integration/` | `agent-tasks/README.md` §5.3 |
| `probe/` | Probe khả thi SP1 | `agent-tasks/README.md` §5.3 |
| **`shared/rr_contracts/`** | Model và hằng số **sinh ra** từ `contracts/` — dùng chung cho `server/`, `collector/`, `worker/` | **Giới thiệu ở ADR này**; `agent-tasks/README.md` §5.3 **đã được PC10 bổ sung** — xem ghi chú |

> **Ghi chú về nguồn khai (sửa theo `F-A2R7-04`).** Bản đầu của ADR này — và ruling sinh ra nó — viết rằng cả bảy thư mục "đã được `agent-tasks/README.md` §5.3 khai". Điều đó **sai tại thời điểm đóng băng mà `A2-R7` kiểm**: §5.3 khi đó khai **sáu** thư mục và chuỗi `rr_contracts` không xuất hiện ở đâu trong file. Thư mục thứ bảy `shared/rr_contracts/` được **giới thiệu lần đầu tại ADR này**, và nó chính là chỗ gánh quy tắc "mã sinh ra từ hợp đồng không được sửa tay" ở mục Hệ quả.
>
> **Trạng thái lúc viết bản sửa này (2026-09-07T07:20Z):** PC10 **đã bổ sung** `shared/rr_contracts/` vào §5.3 trong lượt viết lại card theo stack B — tôi đã kiểm trực tiếp: chuỗi xuất hiện hai lần trong `agent-tasks/README.md`, một ở khối layout và một ở quy tắc "là code SINH RA, không viết tay". Vậy quy kết nguồn nay **đúng cho cả bảy**. Ruling gốc trong `evidence/coordination/` vẫn mang câu sai và cần được sửa cùng lượt để hai văn bản không lệch lại — ADR này không sửa được file đó.

## Trạng thái

**`provisional-accepted`** — `decision_owner: Coordinator`, dưới quyền ủy nhiệm của `AUTH-OWNER-20260907-02`.

**Điều khoản Owner có thể phản đối.** Owner đã ủy quyền lựa chọn này ("You pick, record as ADR") và **có thể phản đối bất kỳ hàng nào** ở vòng quyết định tiếp theo. Phản đối một hàng **không** ảnh hưởng hợp đồng: mọi lựa chọn ở đây nằm dưới lớp hợp đồng, không có lựa chọn nào định nghĩa lại một hành vi mà `contracts/` đã khóa. Chi phí của một lần đảo là sửa card và mã, không phải sửa `contracts/`, `acceptance/` hay `precode/`.

ADR này **không** được ghi `accepted`: không có quyết định nào của Owner phê chuẩn nội dung của nó. Xem `PROV-PC00-07` trong `precode/decision-register.md` §8.

## Hệ quả

### Tích cực

- Card triển khai viết được lệnh build và test thật, thay vì mô tả chung chung — đây là điều kiện còn thiếu cuối cùng của cổng G5.
- Ba chỗ hợp đồng dễ bị một framework "giúp" sai đều được bảo vệ bằng lựa chọn tối giản: **queue** (bảng DB thay vì broker), **Telegram** (gọi thẳng API thay vì bot framework có retry riêng), **CLI/ACP** (`subprocess` thay vì một lớp orchestration giấu tool call).
- Model sinh từ `contracts/` ở cả hai phía (Pydantic và TypeScript) khiến độ trôi giữa hai ngôn ngữ trở thành lỗi build, không phải lỗi runtime — đây là rủi ro lớn nhất mà `ADR-0006` đã nêu khi chọn B.

### Tiêu cực và chi phí

- **Mã sinh ra từ hợp đồng tuyệt đối không được sửa tay.** Cần thêm một kiểm tra E0: file sinh ra phải khớp hash của hợp đồng. Chưa có kiểm tra đó — xem §Nguồn.
- Tự viết vòng lặp scheduler nghĩa là tự chịu trách nhiệm về lease, epoch và catch-up; đổi lại là không có chủ sở hữu trạng thái thứ hai. Quy tắc đã có sẵn ở `contracts/state/run.yaml`, nhưng phải hiện thực đúng.
- Hai chuỗi công cụ (`uv`/`ruff`/`mypy` và `vite`/`eslint`/`prettier`) phải bảo trì song song — cái giá đã biết của stack B.
- `sentence-transformers` kéo theo PyTorch, nặng cho image server; nếu thành vấn đề thì chuyển sang ONNX runtime là một ADR mới, không phải một lần sửa lặng lẽ.

### Bất biến được giữ

`I11` (nội dung nguồn không đọc được secret, không gọi tool): lựa chọn `subprocess` cho CLI/ACP là cách duy nhất trong danh sách thực thi được yêu cầu cô lập ở mức tiến trình của `ADR-0010`. `I15` (restore không tự phát lại outbox): gọi Telegram trực tiếp giữ toàn quyền quyết định gửi lại ở phía chúng ta.

## Phương án đã cân nhắc

| Chỗ | Phương án khác | Vì sao không chọn |
| --- | --- | --- |
| Packaging | pip-tools, poetry | `uv` cho lock nhanh và một cơ chế duy nhất; hai cái kia không sai, chỉ chậm hơn |
| Server API | Flask, Django | Không OpenAPI-native; Django kéo theo ORM và admin không dùng đến |
| Persistence | `sqlite3` thuần, Peewee | Thuần thì thiếu công cụ migration; Peewee giấu SQL, mà các `TXN-*` cần SQL tường minh |
| Queue | Celery + Redis, APScheduler | Thêm một chủ sở hữu trạng thái thứ hai bên cạnh bảng hàng đợi mà hợp đồng đã định nghĩa; và một broker ngoài trái ràng buộc "không broker" |
| Collector | Selenium | SRC-SPEC §6.3 khuyến nghị Playwright; persistent context hợp với yêu cầu profile riêng |
| Analysis worker | LangChain | **Bị loại thẳng: nó giấu tool call.** `ADR-0010` yêu cầu chứng minh được tool bị khóa; một lớp giấu tool call làm yêu cầu đó không kiểm được |
| Embedding | ONNX runtime | Để dành khi cần; `sentence-transformers` đơn giản hơn cho MVP |
| Telegram | python-telegram-bot | Cơ chế retry của framework sẽ tự gửi lại — **vi phạm `AMD-B03`**, thứ Owner vừa phê chuẩn |
| Web | SvelteKit, Next.js | React + Vite thông dụng hơn; Next.js kéo theo SSR không cần cho một app một người dùng |
| Auth | JWT | Cookie session + CSRF đã nằm trong hợp đồng PC05/PC08; JWT sẽ phải sửa hợp đồng |
| **Test** | *Không cân nhắc phương án nào — mặc định thông dụng* | `pytest` và Vitest là mặc định của hai hệ sinh thái; điều **thực sự** được quyết ở hàng này không phải tên thư viện mà là **fixture nạp thẳng từ `acceptance/fixtures/**`**, và điều đó không có phương án thay thế: một bộ dữ liệu test thứ hai sẽ tách oracle khỏi hợp đồng. Đảo tên thư viện: **không tốn gì ở phía hợp đồng** |
| **Lint / format** | *Không cân nhắc phương án nào — mặc định thông dụng* | `ruff` gộp lint và format trong một công cụ; `black` + `flake8` + `isort` là lựa chọn tương đương và **không được cân nhắc riêng**. Đảo: **không tốn gì ở phía hợp đồng** |
| **CI** | *Không cân nhắc phương án nào — mặc định thông dụng* | GitHub Actions được chọn vì repo đã ở git; GitLab CI, Woodpecker hay chỉ chạy tay đều khả thi và **không được cân nhắc riêng**. Điều được quyết ở hàng này là **không có job live** (E3/E4 thủ công theo giao thức) — vế đó **không** phải mặc định mà là một ràng buộc bằng chứng, và nó giữ nguyên dù đổi nhà cung cấp CI |
| **Đóng gói / triển khai** | *Không cân nhắc phương án nào — mặc định thông dụng.* Các phương án **chưa được cân nhắc**: systemd unit thuần cho server, Podman, Kubernetes, hoặc chạy thẳng không container | Docker Compose là cách ít bất ngờ nhất cho ba tiến trình server; vế "collector và worker chạy như tiến trình trên máy, không trong container" **không** phải lựa chọn mà là ràng buộc của `REQ-S6.4-02`. **Hàng này chạm trực tiếp máy của Owner** (`REQ-S6.4-02`, `REQ-S6.4-03`) nên đáng để Owner xem kỹ; đảo nó **không tốn gì ở phía hợp đồng** |

> **Ghi chú về bốn hàng "không cân nhắc" (sửa theo `F-A2R7-05`).** Ruling gốc để trống bốn ô này bằng dấu `—`; bản đầu của ADR bỏ luôn dấu đó, khiến người đọc không phân biệt được "đã cân nhắc rồi loại" với "chưa từng xem xét". Bốn hàng trên nay nói thẳng: **chưa từng xem xét phương án nào**, chúng là mặc định thông dụng, và mỗi hàng đều **đảo được mà không tốn gì ở phía hợp đồng**. Nhờ vậy quyền phản đối của Owner ở mục Trạng thái áp **đồng đều cho cả mười bốn hàng**, không phải chỉ mười.

## Nguồn và truy vết

- **Nguồn ràng buộc:** SRC-SPEC §6.3 (khuyến nghị Playwright, so sánh stack), §6.4 (Docker cho server, tiến trình trên máy cho collector/worker), §4 (visual design cố ý để ngỏ), `D07`, `D09`, `D48`, `D49`, `D50`, `D59`.
- **Phụ thuộc:** `ADR-0006` (stack B). **Ràng buộc:** `ADR-0005` (backup nhất quán), `ADR-0010` (cô lập CLI/ACP), `AMD-B03` (không tự gửi lại khi `unknown`), `AMD-B11`.
- **Quyết định gốc:** Owner trả lời "You pick, record as ADR" ngày 2026-09-07 dưới `AUTH-OWNER-20260907-02`; ruling của Coordinator lưu ở `evidence/coordination/`.
- **Việc còn lại, chưa làm ở gói này:** (a) PC10 viết lại §3 và §8 của 18 card theo bố cục trên; (b) thêm kiểm tra E0 "mã sinh ra khớp hash hợp đồng" vào `evidence/tools/e0_check.py`; (c) chọn model embedding cụ thể sau `REQ-A3` (`REQ-OQ09`). ADR này **không** sửa `contracts/` hay card nào.
