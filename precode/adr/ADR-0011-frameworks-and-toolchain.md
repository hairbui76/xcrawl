---
adr_id: ADR-0011
title: Framework và toolchain cho stack B
status: accepted
decision_owner: Coordinator (được Owner ủy quyền 2026-09-07); phê chuẩn bởi Owner tại OD-20260907-02
date: 2026-09-07
ratified_by: OD-20260907-02
ratified_at: 2026-09-07
evidence_ref: "Lựa chọn: Owner trả lời 'You pick, record as ADR' — Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07; ruling của Coordinator tại evidence/coordination/. Phê chuẩn: Owner trả lời 'accept ADR-0011, start phase 0 and 1' — Claude Code session session_0156UBBHDSeC9soECzSVUb3U, 2026-09-07 (biên bản OD-20260907-02, precode/owner-decisions-02.md)"
blocker_refs: []
source_refs: [SRC-SPEC §6.3, SRC-SPEC §6.4, SRC-SPEC:D07, SRC-SPEC:D09, SRC-SPEC:D48, SRC-SPEC:D49, SRC-SPEC:D50, SRC-SPEC:D59, SRC-SPEC §4]
requirement_refs: [REQ-D07, REQ-D09, REQ-D48, REQ-D49, REQ-D50, REQ-D59, REQ-S6.3-01, REQ-S6.4-01, REQ-S6.4-02, REQ-S6.4-03, REQ-S4-10, REQ-A3, REQ-OQ09]
invariant_refs: [I11, I15]
amendment_refs: [AMD-ADR0011-01]
decision_refs: [OD-20260907-01, OD-20260907-02, PROV-PC00-07, AMD-ADR0011-01, F-A3-P4-02, CR-PC00-35]
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
| Lint / format | `ruff` (kèm format), **`mypy --strict` trên MỌI cây mã sản phẩm Python** — `server/app`, `worker/app`, `collector/app`, `probe` — `eslint` + `prettier`, `PYTHONDONTWRITEBYTECODE` trong CI (`.gitignore` phủ `__pycache__/`) | Rẻ, tiêu chuẩn. **Sửa theo `F-A3-P4-02`**: bản đầu ghi "cho lõi server", và cấu hình theo đúng câu đó (`files = ["server/app"]`) để **23 file sản phẩm** ở `worker/app`, `collector/app`, `probe/` **không được thứ gì kiểm kiểu** |
| CI | GitHub Actions: job E0 (`e0_check` + trình kiểm pin của card), job Python (pytest E1), job web (vitest). **Không có job live** — E3/E4 là thủ công theo giao thức | Kỷ luật bằng chứng |
| Đóng gói / triển khai | Docker Compose cho server (web + api + embedding); collector và worker chạy như tiến trình trên máy (SRC-SPEC §6.4); secrets qua file mount, **không** dùng `.env` (theo PC08) | Đúng `REQ-S6.4-01` và `REQ-S6.4-02` |

**Bố cục repo — tám cây.** Đường dẫn §3 của từng card **giữ nguyên như đã pin**. Bảng dưới đây khớp
`agent-tasks/README.md` §5.3 tại epoch pin **`PC10-PIN-P1-20260907`**.

| Cây | Nội dung | Nguồn khai |
| --- | --- | --- |
| `server/` | Ứng dụng FastAPI, domain service đặt tên theo `MOD-*`, migration Alembic | `agent-tasks/README.md` §5.3 |
| `collector/` | Collector Playwright chạy trên máy cá nhân | `agent-tasks/README.md` §5.3 |
| `worker/` | Analysis worker và AI adapter, chạy trên máy cá nhân | `agent-tasks/README.md` §5.3 |
| `web/` | Ứng dụng Vite + React + TypeScript (`web/src/lib/`, `routes/`, `views/`, `web/tests/contract/`, `web/tests/integration/`) | `agent-tasks/README.md` §5.3 |
| **`shared/rr_contracts/`** | Model và hằng số **sinh ra** từ `contracts/` — dùng chung cho `server/`, `collector/`, `worker/` | **Giới thiệu ở ADR này**; `agent-tasks/README.md` §5.3 **đã được PC10 bổ sung** — xem ghi chú |
| `tests/` | **Đúng hai** thư mục: `tests/contract/` và `tests/integration/`. **Không có `tests/unit/`** | `agent-tasks/README.md` §5.3 (`CR-P0-03` mục 2) |
| `probe/` | Probe khả thi SP1 | `agent-tasks/README.md` §5.3 |
| **`tools/`** | CLI vận hành chạy **ngoài** tiến trình server — hiện đúng một file, `tools/backup_cli.py` (`MOD-backup-cli`, auth scope `backup_operator`, **không** phải session owner) | `agent-tasks/README.md` §5.3 (`CR-P0-03` mục 1); `agent-tasks/TC-backup-restore-drill.md` §3 |

**Tên import (`PROV-P0-01`).** Gốc repo là import root; ba gói Python được nạp bằng **tên đầy đủ** —
`server.app.…` (không phải `app.…`), `collector.app.…`, `worker.app.…`; `shared/rr_contracts/` là package
thật, nạp bằng `rr_contracts.…` và cả ba cây đều import nó.

> **Ghi chú về nguồn khai (sửa theo `F-A2R7-04`).** Bản đầu của ADR này — và ruling sinh ra nó — viết rằng cả bảy thư mục "đã được `agent-tasks/README.md` §5.3 khai". Điều đó **sai tại thời điểm đóng băng mà `A2-R7` kiểm**: §5.3 khi đó khai **sáu** thư mục và chuỗi `rr_contracts` không xuất hiện ở đâu trong file. Thư mục thứ bảy `shared/rr_contracts/` được **giới thiệu lần đầu tại ADR này**, và nó chính là chỗ gánh quy tắc "mã sinh ra từ hợp đồng không được sửa tay" ở mục Hệ quả.
>
> **Trạng thái lúc viết bản sửa này (2026-09-07T07:20Z):** PC10 **đã bổ sung** `shared/rr_contracts/` vào §5.3 trong lượt viết lại card theo stack B — tôi đã kiểm trực tiếp: chuỗi xuất hiện hai lần trong `agent-tasks/README.md`, một ở khối layout và một ở quy tắc "là code SINH RA, không viết tay". Vậy quy kết nguồn nay **đúng cho cả bảy**. Ruling gốc trong `evidence/coordination/` vẫn mang câu sai và cần được sửa cùng lượt để hai văn bản không lệch lại — ADR này không sửa được file đó.

> **Cập nhật `CR-PC10-09` (2026-09-07, `PKT-PC00-FIX17`) — đây là một đính chính SỰ KIỆN, không phải một quyết định mới.** Bảng trên trước đây khai **bảy** cây và ghi `tests/` = `contract/` + `unit/` + `integration/`. Cả hai điều đó nay lệch với `agent-tasks/README.md` §5.3 tại epoch `PC10-PIN-P1-20260907`, và PC10 **không được ghi ADR** nên đã mở `CR-PC10-09` thay vì tự sửa. Hai chỗ được sửa: (a) `tools/` là **cây thứ tám** — `agent-tasks/TC-backup-restore-drill.md` §3 vốn đã pin `tools/backup_cli.py` từ trước, nên đây là ADR **bắt kịp** card chứ không phải card đổi theo ADR; (b) **`tests/unit/` bị bỏ** — §3 của cả 18 card chỉ dùng `contract/` và `integration/`, nên khai một thư mục thứ ba mà không card nào ghi vào là mời người ta đặt test ở chỗ không ai kiểm (`CR-P0-03` mục 2). Card đầu tiên thực sự cần unit test cục bộ sẽ tạo `tests/unit/` **kèm một CR**, không tự thêm.
>
> **Amendment `AMD-ADR0011-01` (2026-09-08, `PKT-PC00-FIX32`) — ba đính chính SỰ KIỆN, không phải quyết định mới.** `decision_refs`: `F-A3-P4-02`, `CR-PC00-35`; chuỗi thẩm quyền `OD-20260908-10` → `AUTH-OWNER-20260908-11` → ruling `…/packets/FIX-A3P4R1-rulings.md`. **Status của ADR giữ nguyên `accepted`, `ratified_by: OD-20260907-02` không đổi**: không hàng nào trong bảng **Quyết định** đổi lựa chọn kỹ thuật — ba mục dưới đây sửa **câu mô tả đã hết đúng**, đúng loại như `AMD-SPEC-D34-01` ở `decision-register.md` §3.
>
> 1. **Phạm vi kiểm kiểu (`F-A3-P4-02`, MEDIUM).** Hàng `Lint / format` từng viết *"`mypy --strict` cho lõi server"*. Cấu hình làm **đúng theo câu ấy** — `files = ["server/app"]` — nên **23 file sản phẩm** dưới `worker/app`, `collector/app`, `probe/` **không được thứ gì kiểm kiểu**. Đây là chỗ một câu mơ hồ trong ADR **trở thành** một lỗ thật trong CI: cụm "lõi server" nghe như một sự nhấn mạnh, và nó bị đọc thành một **giới hạn**. Hàng nay ghi **mọi cây mã sản phẩm Python**, nêu đích danh bốn cây. Auditor ghi rõ đây **không** phải lỗi chặn CI (bar hôm nay đúng như đã khai) mà là **bar đặt sai**. `worker-WS` mở rộng `files`, thêm dev dep `types-PyYAML`/`types-jsonschema` (đóng `CR-TC-adapter-06`), xử lý typing của `server/tests/test_smoke.py`, **giữ `--strict`**, và cập nhật tên bước CI/Makefile — xem addendum **`P0-FIX4`** của `evidence/handoffs/P0-skeleton-handoff.md`. **PC00 trích addendum đó mà chưa đọc được nó**: gói này chạy song song với `WS` theo đúng thứ tự ruling, nên câu trên là **tham chiếu tới việc đã giao**, không phải một quan sát đã kiểm. → `CR-PC00-37`.
> 2. **`tools/` đã tồn tại (`CR-PC00-35`).** Ghi chú "Sự kiện Giai đoạn 0" ở trên nói *"`tools/` chưa được tạo"* — đúng khi viết ở `PKT-PC00-FIX17` (2026-09-07) và **sai từ 2026-09-08**, khi card `TC-backup-restore-drill` của đợt Giai đoạn 4/6 tạo `tools/backup_cli.py`. **Cây thứ tám nay tồn tại thật trên đĩa**, và `CR-P0-03` mục 1 — mở từ `PKT-P0-SKELETON` vì `tools/` được khai mà chưa có — **đã được đáp ứng**. Sai lệch này **không** do ai đọc lại phát hiện: phép kiểm hai chiều dựng ở `FIX17` (so câu trong ADR với thực tế trên đĩa) **tự đỏ** ở `PKT-PC00-FIX30`. Một ghi chú lịch sử đúng-lúc-viết vẫn phải được đánh dấu khi nó hết đúng, nếu không nó đọc như một tuyên bố hiện tại.
> 3. **`.gitignore` phủ `__pycache__/`.** `worker-WS` đã thêm; `A3-P4-R1` xác nhận **0** thư mục `__pycache__` trong lượt đóng băng `FC-P4`. Điều này biến quy tắc `PYTHONDONTWRITEBYTECODE=1` — vốn là **kỷ luật của từng Worker** — thành một lưới an toàn ở tầng repo. Nó **không** thay quy tắc kia: một Worker vẫn phải không sinh `.pyc`, vì `.gitignore` chỉ giấu file khỏi git, **không** ngăn file được tạo.
>
> **Ba điều amendment này KHÔNG làm.** (a) **Không** đổi một lựa chọn kỹ thuật nào — `mypy --strict` vẫn là `mypy --strict`, chỉ phạm vi được nói đúng. (b) **Không** tự chứng minh rằng phạm vi mới đã chạy sạch: điều đó thuộc addendum `P0-FIX4` của `WS` và lượt xác minh `A3-P4-R2`, **không** phải file này. (c) **Không** đóng finding nào — `F-A3-P4-02` theo vòng đời `protocol.md` §8, và `CR-PC00-35` chỉ được ghi là đã đáp ứng **trên thực tế**, disposition vẫn của Coordinator.
>
> **Vì sao đính chính này KHÔNG đụng tới `ratified_by`.** `OD-20260907-02` phê chuẩn **các lựa chọn kỹ thuật** ở bảng Quyết định (14 hàng: ngôn ngữ, framework, cách truy cập DB, hàng đợi, test runner, CI, đóng gói…). Bố cục repo là một **mô tả** đi kèm, không phải một trong 14 hàng đó; sửa nó cho khớp thực tế không đổi một lựa chọn nào Owner đã phê chuẩn. `status: accepted` và `ratified_by: OD-20260907-02` vì vậy **giữ nguyên**, và không cần một vòng quyết định mới. Nếu sau này một hàng trong bảng Quyết định phải đổi thì đó là chuyện khác — khi ấy ADR phải quay lại Owner.
>
> **Sự kiện Giai đoạn 0 (`evidence/handoffs/P0-skeleton-handoff.md`).** `PKT-P0-SKELETON` đã dựng bộ khung repo ngày 2026-09-07: **bảy** trong tám cây tồn tại thật trên đĩa (`server/`, `collector/`, `worker/`, `web/`, `shared/rr_contracts/`, `tests/` với đúng `contract/` + `integration/`, `probe/`). **`tools/` khi đó chưa được tạo** — nó nằm ngoài write set của gói đó (`CR-P0-03` mục 1) và sẽ do card M8 `TC-backup-restore-drill` tạo. **(Đã hết đúng từ 2026-09-08 — xem khối Amendment ở cuối mục này: `tools/backup_cli.py` nay tồn tại, `CR-P0-03` mục 1 đã được đáp ứng.)** Vì vậy câu "bố cục repo" trong ADR này nay mô tả **hai** thứ khác nhau và không được đọc lẫn: bảy cây là **sự kiện đã kiểm được trên đĩa**, cây thứ tám `tools/` là **cam kết đã khai** chưa thành file. Bộ khung không mang hành vi nghiệp vụ nào (chỉ `health.get_liveness`; `health.get_readiness` **cố ý** chưa route vì thuộc `TC-storage-write-blocked-readiness`), nên nó **không** là bằng chứng cho một card nào — E1–E4 vẫn `NOT_RUN`.

## Trạng thái

**`accepted`** — phê chuẩn bởi **Owner** tại `OD-20260907-02` ngày 2026-09-07
(`precode/owner-decisions-02.md`, authority `AUTH-OWNER-20260907-03`, evidence
`session_0156UBBHDSeC9soECzSVUb3U`). Owner trả lời nguyên văn **"accept ADR-0011, start phase 0 and 1"**.
`decision_owner` giữ nguyên là **Coordinator** — người *chọn* vẫn là Coordinator dưới ủy quyền; điều đổi là
nay có một quyết định của Owner phê chuẩn **nội dung** đã chọn. Xem `PROV-PC00-07` trong
`precode/decision-register.md` §8, nay `ACCEPTED (OD-20260907-02)`.

**Điều được phê chuẩn, và điều không.** Phê chuẩn áp cho **cả mười bốn hàng** của bảng quyết định. Nhưng bốn
hàng — `Test`, `Lint / format`, `CI`, `Đóng gói / triển khai` — được ghi rõ ở mục "Phương án đã cân nhắc" là
**chưa từng cân nhắc phương án nào** (`F-A2R7-05`). Một phê chuẩn trọn gói **không** biến bốn hàng đó thành
đã-được-cân-nhắc; nó nói Owner chấp nhận chúng làm mặc định. Chi phí đảo bất kỳ hàng nào vẫn không đổi: **chỉ
sửa card và mã**, không sửa `contracts/`, `acceptance/` hay `precode/`.

### Lập luận lúc còn `provisional-accepted` (giữ nguyên để truy vết)

> **`provisional-accepted`** — `decision_owner: Coordinator`, dưới quyền ủy nhiệm của `AUTH-OWNER-20260907-02`.
>
> **Điều khoản Owner có thể phản đối.** Owner đã ủy quyền lựa chọn này ("You pick, record as ADR") và **có thể phản đối bất kỳ hàng nào** ở vòng quyết định tiếp theo. Phản đối một hàng **không** ảnh hưởng hợp đồng: mọi lựa chọn ở đây nằm dưới lớp hợp đồng, không có lựa chọn nào định nghĩa lại một hành vi mà `contracts/` đã khóa. Chi phí của một lần đảo là sửa card và mã, không phải sửa `contracts/`, `acceptance/` hay `precode/`.
>
> ADR này **không** được ghi `accepted`: không có quyết định nào của Owner phê chuẩn nội dung của nó. Xem `PROV-PC00-07` trong `precode/decision-register.md` §8.

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
- **Phê chuẩn:** `OD-20260907-02` ngày 2026-09-07 (`precode/owner-decisions-02.md`, authority `AUTH-OWNER-20260907-03`, evidence `session_0156UBBHDSeC9soECzSVUb3U`) — Owner trả lời "accept ADR-0011, start phase 0 and 1". Cùng biên bản đó mở lối vào Giai đoạn 0 và Giai đoạn 1 của `docs/master-plan.md`.
- **Amendment:** `AMD-ADR0011-01` (2026-09-08, `PKT-PC00-FIX32`) — phạm vi `mypy --strict` = mọi cây mã sản phẩm Python; `tools/` đã tồn tại; `.gitignore` phủ `__pycache__/`. Căn cứ `F-A3-P4-02`, `CR-PC00-35`, ruling post-`A3-P4-R1` dưới `AUTH-OWNER-20260908-11`. Status ADR **không** đổi.
- **Việc còn lại, chưa làm ở gói này:** (a) PC10 viết lại §3 và §8 của 18 card theo bố cục trên; (b) thêm kiểm tra E0 "mã sinh ra khớp hash hợp đồng" vào `evidence/tools/e0_check.py`; (c) chọn model embedding cụ thể sau `REQ-A3` (`REQ-OQ09`). ADR này **không** sửa `contracts/` hay card nào.
