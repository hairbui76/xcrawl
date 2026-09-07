---
handoff_id: TC-owner-auth-session-handoff
packet_id: TC-owner-auth-session
worker_principal: worker-WA
authority_id: AUTH-COORD-TC-AUTH
parent_authority: AUTH-OWNER-20260907-03
lease_id: LEASE-TC-AUTH-e1
decision_refs: [OD-20260907-01, OD-20260907-02, ADR-0006, ADR-0011, ADR-0010, ADR-0001]
invariant_refs: [I01, I11]
scenario_refs: [SC17, SC39, SC40, SC41, SC49, SC51]
requirement_refs: [REQ-D01, REQ-D04, REQ-D05, REQ-P0-01, REQ-S11.1-01, REQ-S11.2-01, REQ-S11.2-02]
evidence_manifest_id: EVM-TC-owner-auth-session
next_actor: Coordinator
lease_released_at: 2026-09-07T10:20Z
---

# HANDOFF — TC-owner-auth-session (M1, G5): phiên owner cookie AND CSRF, và từ chối token đi sai cạnh

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| `card_id` | `TC-owner-auth-session` · pin epoch `PC10-PIN-OD01e-20260907` |
| `worker_principal` | `worker-WA` |
| `authority_id` | `AUTH-COORD-TC-AUTH` (parent `AUTH-OWNER-20260907-03`) |
| `lease_id` | `LEASE-TC-AUTH-e1` (exclusive; message-tracked, không có guard mức OS) |
| **`status`** | **`DONE_WITH_CONCERNS`** |
| `completion_claim` | `IMPLEMENTATION_VERIFIED` **chỉ cho phạm vi card này** và **chỉ ở mức E1** — xem mục 8 về những gì chưa được thiết lập. Tự kiểm là `SELF_VALIDATION`; **không** có audit độc lập nào được chạy. |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T10:20Z |

**Vì sao `DONE_WITH_CONCERNS` chứ không phải `DONE`.** Sáu change request mở (mục 7). Một
trong số đó — `CR-TC-AUTH-01` — là mâu thuẫn **thật** giữa một fixture đã pin và bốn nguồn
hợp đồng khác, và nó được ghi lại bằng một test `xfail(strict=True)` thay vì sửa fixture.
Hai CR khác (`CR-TC-AUTH-02`, `CR-TC-AUTH-03`) là chỗ hợp đồng entity **thiếu** một nơi để
lưu dữ liệu mà `contracts/ops/secrets.md` bắt buộc phải có.

## 2. Stop gate — kết quả từng cổng của §10

| Cổng | Kết quả |
| --- | --- |
| `SG-HASH` | **PASS.** Cả 25 dòng pin ở §0 khớp đĩa. `evidence/tools/verify_cards.py` chạy trước khi ghi dòng code đầu tiên: **13/13 check, 3 210 assertion, 0 violation**. (Ghi chú: ở đầu phiên ba file `ADR-0011`, `precode/baseline.json`, `precode/decision-register.md` **không** khớp bảng §0 — đúng drift mà `CR-P0-01` báo. Card đã được re-pin trên đĩa trong lúc gói này chạy và mọi hash nay khớp; tôi **không** sửa card.) |
| `SG-02` | **PASS.** `uv run openapi-spec-validator contracts/http/openapi.yaml` → `OK`, exit 0, trên đúng hash `28b3820e…` mà §0 pin. Không có sai lệch nào để raise. |
| `SG-PC09` | **PASS.** `acceptance/scenarios.yaml` (bản mới nhất, không pin hash) đọc trước khi code. SC40 `oracle_vi` nói **`CSRF_REJECTED`**, SC41 `oracle_vi` nói **`UNAUTHORIZED` 401** — cả hai **khớp** §8 của card. Không mâu thuẫn ⇒ không dừng. |
| `SG-01` | **Đã đóng.** Ba nguồn thượng nguồn (`modules.yaml` NC-01/NC-02 `expected_error_code`, oracle của `UNAUTHORIZED` trong `errors.yaml`, mô tả `collectorToken` trong `openapi.yaml`) **và** SC41 của PC09 đều nói `UNAUTHORIZED`. Code theo đó. |
| `SG-CSRF` | **Đã áp dụng.** Thiếu/lệch CSRF ⇒ **403 `CSRF_REJECTED`**, phiên **không** bị hủy — có test khẳng định request kế tiếp vẫn 200. `FORBIDDEN_EDGE` **không** được dùng cho ca này. |
| `SG-CONTRACT` | **TRIGGER (một phần).** `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json` seq4 pin `FORBIDDEN_EDGE` cho ca thiếu CSRF — mâu thuẫn với `openapi.yaml` (post-FIX1), `errors.yaml`, `scenarios.yaml` SC40 và ruling R5-01. **Không sửa fixture.** Xem `CR-TC-AUTH-01`. |
| `SG-DENY` | **PASS trong phạm vi lớp này.** 36 cạnh `forbidden_edges` được duyệt qua `boundary/a-default-deny-sweep-36-edges.json`; những cạnh có principal HTTP **và** `ENF-api-auth-test` được khẳng định trả đúng mã đã pin. 26 cạnh còn lại được **khẳng định là ngoài lớp này** (import rule / capability / storage health guard theo R5-01 hàng 2–3), không bị bỏ qua im lặng. |
| `SG-EDGE` | **TRIGGER.** `contracts/data/entities.yaml` không khai chỗ lưu credential của owner và không khai entity nào cho login attempt/lockout. Xem `CR-TC-AUTH-02` và `CR-TC-AUTH-03`; tôi **không** tạo entity mới. |
| `SG-03` | **PASS.** Không secret nào vào repo. `TokenRegistry` rỗng theo mặc định; test dùng chuỗi giả trong bộ nhớ; không có `.env`, không có key. |
| `SG-STACK`, `SG-G5` | Không trigger: stack đã chốt (Option B), G5 + lệnh Owner đã có qua dispatch của Coordinator. |

## 3. Changes — mọi file đã tạo hoặc sửa

**8 file mới (102 175 byte) + 1 file sửa bằng một khối include có ranh giới.**

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/auth/__init__.py` | CREATE | ABSENT | `ada49396b07d0b2373a146d5536446fb41cea43fa6a30a0621e6b3ee68053e1c` | 933 |
| `server/app/auth/csrf.py` | CREATE | ABSENT | `1e96b5976126d0c3feb8778407c2f030d954baf99c509eb63c7721f2233093d5` | 2369 |
| `server/app/auth/service.py` | CREATE | ABSENT | `1580d2bc73641134995cb4325582c00db19be995c543e614173a185a2664f52f` | 27491 |
| `server/app/auth/middleware.py` | CREATE | ABSENT | `2c52c3ecf43ccdd97a8c706771c543333945b474b2aae581e817e3a97e4af390` | 15533 |
| `server/app/auth/router.py` | CREATE | ABSENT | `591345bf626cd639544b3bef98d9623194742ba28924db61a63d3d61b7f1c1b0` | 9968 |
| `server/migrations/versions/0002_tc_owner_auth_session.py` | CREATE | ABSENT | `e9143f2082a34d073db17271b907b1f83806eb10e0087258a4a2cf4440d85808` | 4634 |
| `tests/contract/test_auth_scheme_matrix.py` | CREATE | ABSENT | `dfb04a7977fb8c9ce1da49b161b900759b8ced597b1e8986c153327f568a6f7e` | 14271 |
| `tests/integration/test_denied_edges.py` | CREATE | ABSENT | `1d71746c095568b74e5e3c0628fb4538751e464a814b6252a634f86cbaa53683` | 27556 |
| `evidence/runs/TC-owner-auth-session-E1-20260907T101529Z.json` | CREATE | ABSENT | `70fee184a929665c45ef0d91a1b91c27798d188eedf134945d484b01423cf1a3` | 10797 |
| `evidence/handoffs/TC-owner-auth-session-handoff.md` | CREATE | ABSENT | *(chính file này)* | — |
| `server/app/main.py` | MODIFY | *(xem ghi chú)* | `adfcde38ab8191ed54ad088a8c6d33550a009a2b06026371ce3838867db0bd44` | 8014 |

### 3.1 `server/app/auth/__init__.py` nằm ngoài chữ của §3

§3 liệt kê bốn file `.py` dưới `server/app/auth/`; nó không liệt kê `__init__.py`. Không có
file đó thì `server.app.auth` là một namespace package và `mypy --strict` với
`explicit_package_bases` không nhận nó. File chỉ có docstring và bốn dòng re-export — không
có logic nào. Tôi ghi lại đây thay vì thêm lặng lẽ.

### 3.2 Ghi chú về `server/app/main.py`

File này ở trạng thái đang được **hai** card sửa song song. Khối của tôi được thêm đúng một
lần, có ranh giới `--- BEGIN/END include: TC-owner-auth-session ---`, và gồm **một** dòng
gọi `install_auth(app)` cộng một import. Khối của
`TC-storage-write-blocked-readiness` nằm ngay sau và **không** bị tôi chạm vào. Hash
"before" không được khai vì tôi không có bản chụp ngay trước lần ghi của mình: file đã bị
gói kia sửa giữa lúc tôi đọc và lúc tôi ghi. Tôi không khai một con số mình không đo được.

## 4. Baseline đã dựa vào

| Ref | Path | SHA-256 | Kiểm |
| --- | --- | --- | --- |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp ở đầu phiên **và** trước handoff |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp ở đầu phiên **và** trước handoff |

25 file hợp đồng/fixture ở §0 của card: mọi hash khớp, chép nguyên văn vào
`baseline.contract_hashes` của evidence manifest. `acceptance/scenarios.yaml` và
`evidence/manifest.schema.json` (PC09, cố ý không pin) đọc bản mới nhất; hash tại thời điểm
chạy cũng nằm trong manifest.

## 5. Cái đã được xây

### 5.1 `server/app/auth/middleware.py` — bề mặt các card khác dùng

Đúng năm tên Coordinator yêu cầu, cộng hàm quyết định mà test dùng:

| Tên | Scheme của `openapi.yaml` |
| --- | --- |
| `require_owner_session` | `ownerSessionCookie` |
| `require_csrf` | `ownerCsrfToken` |
| `require_collector_token` | `collectorToken` |
| `require_worker_token` | `analysisWorkerToken` |
| `require_backup_operator_token` | `backupOperatorToken` |

Sáu hằng tên scheme được **kiểm ở thời điểm import** với
`rr_contracts.generated.constants.SECURITY_SCHEMES` (sinh từ chính `openapi.yaml`): đổi tên
một scheme làm module **không import được**, chứ không phải làm nó lặng lẽ canh gác nhầm.

`classify_denial(scope, mutation, principal, csrf_ok)` trả **đúng một** mã theo bảng R5-01,
hoặc `None` khi lời gọi được nhận. Nó tách hai nhánh mà card gọi là FAIL nếu lẫn: một
principal **không được nhận** ⇒ `UNAUTHORIZED`; principal **được nhận** nhưng thiếu
double-submit ⇒ `CSRF_REJECTED`.

`SCHEME_REQUIREMENTS` ánh xạ `(auth_scope, mutation)` → các requirement thay thế; mỗi
`frozenset` là một requirement (quan hệ **AND**), tuple các frozenset là quan hệ **OR** —
đúng ngữ nghĩa `security` của OpenAPI. Bảng này **sinh lại từ tài liệu và so bằng** trong
`test_scheme_requirements_table_equals_the_contract` trên cả 54 operation HTTP.

### 5.2 Ba điểm thiết kế đáng soi

- **Thứ tự dependency.** `logout` khai `Depends(require_owner_session)` **rồi**
  `Depends(require_csrf)`. Nhờ thứ tự đó, một request không mang gì cả trả `UNAUTHORIZED`
  (không phải `CSRF_REJECTED`) — đúng phân biệt seq3/seq4 của `recovery/h`.
- **CSRF không lưu ở server.** Double-submit chỉ so *header với cookie*; cả hai đến từ trình
  duyệt. Vì vậy `ENT-session` **không** cần thêm cột, và không có secret thừa nào nằm trong
  DB. `SessionInfo.csrf_token` trả giá trị vừa sinh ở `auth.login`.
- **Idle 12 h và absolute 30 d trên đúng các cột đã khai.** `ENT-session` không có
  `last_seen_at`, nên `expires_at` được trượt tới `min(now + 12 h, issued_at + 30 d)` ở mỗi
  lần xác thực thành công, và chỉ ghi khi hạn dịch hơn 60 s (giá trị kỹ thuật, không phải số
  hợp đồng) để một request đọc không biến thành một request ghi.

### 5.3 Bootstrap tài khoản duy nhất

`AuthService.bootstrap_owner(display_name=…, password=…)` là **thao tác vận hành/CLI**.
Không có route HTTP nào gọi tới nó và không được có: `test_no_signup_or_password_reset_endpoint_exists`
quét toàn bộ `openapi.yaml`, và `test_mounted_app_exposes_exactly_the_three_auth_routes`
quét app thật. Đổi mật khẩu **thu hồi mọi session** (secrets.md §2.3).

## 6. Evidence — tất cả `SELF_VALIDATION`

Mọi lệnh chạy ở `/mnt/virtual/repo/xcrawl` với `PYTHONDONTWRITEBYTECODE=1`, **không lệnh nào
chạm mạng**. Manifest: `evidence/runs/TC-owner-auth-session-E1-20260907T101529Z.json`
(`EV-E1-01-tc-owner-auth-session`), validate sạch với `evidence/manifest.schema.json` bằng
`jsonschema.Draft202012Validator`.

### EV-AUTH-01 — E1: ma trận scheme + cạnh bị từ chối

| Trường | Giá trị |
| --- | --- |
| `command` | `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/contract/test_auth_scheme_matrix.py tests/integration/test_denied_edges.py -p no:warnings -q` |
| `started / ended` | 2026-09-07T10:15:14Z / 2026-09-07T10:15:29Z (15 s) |
| `oracle` | fixture `recovery/h`, `recovery/i`, `boundary/a`, `ui/sc51` + `openapi.yaml` + `ports.yaml` + `errors.yaml` |
| `observed` | **43 passed, 0 failed, 2 xfailed** |
| `exit_code` | **0** · `status` **PASS** |

Con số đo được, không phải mô tả:

| Oracle | Kỳ vọng | Quan sát |
| --- | --- | --- |
| Operation `owner_session` + `mutation: true` đòi **cả** cookie và CSRF | 17 | **17** |
| Route owner mutation nhận cookie **một mình** | 0 | **0** |
| Route `backup.*` nhận bất kỳ scheme nào khác `backupOperatorToken` | 0 | **0** |
| Operation `auth.*` phơi qua HTTP | `login`, `logout`, `get_session` | **đúng ba** |
| Endpoint signup / reset mật khẩu | 0 | **0** |
| Hàng `session` sau `auth.login` (SC51) | 1 | **1** |
| Mã cho ca thiếu CSRF | `CSRF_REJECTED` 403 | **`CSRF_REJECTED` 403**, phiên vẫn dùng được |
| Mã cho collector token gọi `save.create`/`tag.update` | `UNAUTHORIZED` 401 | **`UNAUTHORIZED` 401** |
| `ingest.submit_batch` bằng cùng token đó | vẫn mở | **vẫn mở** |
| App trần (không `auth_service`) trên route được bảo vệ | 401 | **401**, không 500 |

### EV-AUTH-02 — E0: validator OpenAPI 3.1 (`SG-02`)

`uv run openapi-spec-validator contracts/http/openapi.yaml` → `contracts/http/openapi.yaml: OK`,
exit **0**, trên input hash `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92`.
**Không có sai lệch nào ⇒ không CR nào được raise cho PC05.**

### EV-AUTH-03 — E0: pin của card (`SG-HASH`)

`uv run python evidence/tools/verify_cards.py --repo .` → **13 check trên 18 card, 3 210
assertion, 0 violation**, exit **0**. Chạy trước khi ghi code và lại trước handoff.

### EV-AUTH-04 — E0: lint và kiểu

| Lệnh | Exit |
| --- | --- |
| `uv run ruff check server/app/auth tests/contract/test_auth_scheme_matrix.py tests/integration/test_denied_edges.py server/migrations/versions/0002_tc_owner_auth_session.py server/app/main.py` | **0** |
| `uv run ruff format --check` (cùng tập file) | **0** |
| `uv run mypy` (`--strict` trên `server/app`, 24 file) | **0** |

### EV-AUTH-05 — E2 nhẹ: migration sống được với nhánh song song

`test_the_migration_survives_the_parallel_owner_branch` chạy Alembic thật theo **cả hai** thứ
tự nhánh (`0002_base_entities` trước rồi `0002_tc_owner_auth_session`, và ngược lại) và
khẳng định `owner` có đủ hai cột credential còn `session` tồn tại đúng một lần. Exit 0.

### Những gì **không** chạy — `NOT_RUN`

- **E2 fault injection SQLite** cho đường `STORAGE_WRITE_FAILED` của `auth.login`/`auth.logout`.
  Đường code tồn tại (bắt `SQLAlchemyError` → `STORAGE_WRITE_FAILED` 503) nhưng chưa có test
  bơm lỗi ổ đĩa. Card §8 không yêu cầu, nhưng ghi lại vì §7 có nghĩa vụ với mã này.
- **E3/E4**: không TLS thật, không trình duyệt thật, không reverse proxy. Cờ `Secure` được
  khẳng định trên **chuỗi `Set-Cookie`**, không phải trên một kết nối HTTPS thật.
- Cửa `storage.get_health = write_blocked` trước khi ghi session: `StorageHealthPort` mới là
  một Protocol, chưa nối kênh health thật ⇒ test đánh dấu `xfail`.
- `alembic upgrade head` trên cây đầy đủ: **ba** card đã nhánh khỏi `0001` song song nên
  `head` đang nhập nhằng (`CR-TC-AUTH-06`). Test của tôi nhắm đúng revision của card.

## 7. Change request — 6 mục, không mục nào tự sửa

| ID | Nội dung |
| --- | --- |
| `CR-TC-AUTH-01` | **`acceptance/fixtures/recovery/h-unauthenticated-owner-api.json` seq4 đã cũ.** Nó pin `expected.seq4.error_code = FORBIDDEN_EDGE` cho ca "phiên hợp lệ, thiếu CSRF", và trích một câu mô tả `ownerCsrfToken` **không còn tồn tại** trong `openapi.yaml`. Bốn nguồn hiện hành đều nói `CSRF_REJECTED`: `openapi.yaml` post-FIX1, `contracts/errors.yaml` (mã `CSRF_REJECTED`, `distinct_from_vi`), `acceptance/scenarios.yaml` SC40 (`forbidden_effects_vi`: "Dùng `FORBIDDEN_EDGE` cho ca thiếu CSRF"), và ruling R5-01 của chính card. `open_question` `CR-PC08-03` bên trong fixture chính là yêu cầu sửa này. **Đề nghị:** PC08 đổi `seq4.error_code` thành `CSRF_REJECTED` và cập nhật `reason_vi`. Code theo R5-01; drift được ghi bằng `test_fixture_h_seq4_literal_expectation` (`xfail(strict=True)`). `http_status: 403` và `rows_changed: 0` của seq4 **không** tranh cãi và được khẳng định bằng một test PASS riêng. |
| `CR-TC-AUTH-02` | **`ENT-owner` không có chỗ lưu credential.** `contracts/data/entities.yaml` khai `owner` với đúng năm trường (`id`, `singleton_guard`, `display_name`, `timezone_iana`, `created_at`) và **không** trường nào lưu mật khẩu, trong khi `contracts/ops/secrets.md` §2.2 bắt buộc Argon2id cho tài khoản duy nhất và `openapi.yaml` phơi `auth.login` với một mật khẩu. Không entity nào khác trong file giữ nó. **Đã làm:** migration thêm hai cột NULLable `password_hash`, `password_updated_at` vào `owner` — thay đổi nhỏ nhất nằm **trong** state effect mà §4 khai (`ENT-owner`), thay vì phát minh một bảng. **Đề nghị:** PC02 khai hai trường này trong `entities.yaml`, hoặc chỉ ra entity đúng. |
| `CR-TC-AUTH-03` | **Không có entity cho login attempt / lockout.** `secrets.md` §2.3 chốt "5 lần / 15 phút ⇒ khóa 15 phút, trả `RATE_LIMITED` kèm `retry_after`", nhưng `entities.yaml` không khai bảng nào để đếm. **Đã làm:** `LoginThrottle` là bộ đếm **trong tiến trình** (không bảng mới, `SG-EDGE` không bị vi phạm). **Hệ quả được nêu chứ không giấu:** khởi động lại server xóa bộ đếm. **Đề nghị:** PC02 khai một entity, hoặc PC08 ghi rõ rằng lockout là trạng thái tiến trình. |
| `CR-TC-AUTH-04` | **`ports.yaml` và `errors.yaml` không liệt kê `RATE_LIMITED` cho `auth.login`.** `openapi.yaml` khai response `429 RATE_LIMITED` (kèm header `Retry-After`) cho `/v1/auth/login` và `secrets.md` §2.3 bắt buộc nó, nhưng `ports.yaml.auth.login.error_codes` chỉ có `[VALIDATION_ERROR, UNAUTHORIZED, STORAGE_WRITE_FAILED]` và `errors.yaml.RATE_LIMITED.operations` không nhắc `auth.login`. Code theo `openapi.yaml`. **Đề nghị:** PC01/PC03 thêm `auth.login` vào cả hai. |
| `CR-TC-AUTH-05` | **Bộ sinh chưa phơi bốn thứ mà code cần.** `rr_contracts.generated` có `ErrorCode`, `SCOPE`, `RETRY_CLASS`, `OWNER_MODULE`, `TRANSPORT`, `MUTATION`, `SECURITY_SCHEMES` — nhưng **không** có (a) `auth_scope` của từng operation, (b) `message_safe_template_vi`, (c) `details_safe_keys`, (d) model Pydantic cho các component inline của `openapi.yaml` (`LoginRequest`, `SessionInfo`). Bốn thứ đó phải viết tay trong card này. **Bù lại:** mỗi bảng viết tay có một test sinh lại nó từ hợp đồng và so bằng, nên drift là một test đỏ chứ không phải một phân kỳ im lặng. **Đề nghị:** mở rộng `shared/rr_contracts/generate.py`. |
| `CR-TC-AUTH-06` | **Va chạm revision Alembic giữa ba card chạy song song.** Ba file cùng nhánh khỏi `0001`: `0002_base_entities` (khai `revision = "0002_base_entities"`), `0002_tc_ingest_idempotent_ack_lost` (khai `revision = "0002"`) và của tôi. Ngoài ra `0002_base_entities` **cũng** `CREATE TABLE owner`, dù `entities.yaml` ghi `owner_module: MOD-auth-service` cho `ENT-owner` và §4 của card này khai nó là state effect của tôi. **Đã làm:** revision id của tôi đổi thành `0002_tc_owner_auth_session` (duy nhất), migration dùng `CREATE TABLE IF NOT EXISTS` + `ALTER TABLE ADD COLUMN` có kiểm `PRAGMA table_info`, `downgrade` **không** drop `owner`, và có test chạy cả hai thứ tự nhánh. **Đề nghị:** Coordinator gộp định nghĩa `owner` về đúng một revision và ép quy ước "revision id = tên card". |

### Ghi chú cho Coordinator (không phải CR)

- **CR-03 của card storage đã được xử lý.** `create_app()` không dựng `AuthService` — factory
  trần không có URL database và dựng một cái sẽ là phát minh một chỗ lưu. Thay vào đó
  `_auth_service()` trả `None` và mọi dependency owner-session trả **401 `UNAUTHORIZED`**
  (default deny), **không** RuntimeError. `install_auth(app, service)` là hook để deployment
  hoặc test cấp backend. Hai test khẳng định: `/v1/auth/session` **và**
  `/v1/health/readiness` của card storage đều trả 401 (không 500) trên app trần.
- **`server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0` đang FAIL**, và nó
  fail vì `TC-storage-write-blocked-readiness` đã đăng ký `/v1/health/readiness` — test
  Giai đoạn 0 đó khẳng định 404. Không phải file của tôi và không nằm trong write set của
  tôi. Trước thay đổi của tôi nó cũng đã fail (route trả 200 chứ không 404); sau thay đổi
  của tôi nó trả 401. Cần một quyết định về chủ sở hữu test đó.
- **`tests/contract/test_ingest_*.py` báo lỗi khi chạy toàn cây** nhưng **xanh khi chạy
  riêng** (`26 passed`). Nguyên nhân nằm ở chữ ký `identity.resolve_target` giữa card ingest
  và card identity (`TypeError: resolve_target() got an unexpected keyword argument
  'x_post_id'`), không liên quan tới auth.

## 8. Điều claim này **không** thiết lập

Mẫu claim SRC-PLAN §14.3:

- **Claim:** `IMPLEMENTATION_VERIFIED` cho phạm vi `MOD-auth-service` của card này.
- **Baseline:** spec `d35e1f2d…`, plan `f65bb046…`, 25 hash hợp đồng ở §0 (khớp), revision
  `da886f8` + working tree.
- **Requirements covered:** REQ-D05, REQ-P0-01, REQ-S11.1-01, REQ-S11.2-01/02, REQ-D01, REQ-D04.
- **Evidence manifest:** `EV-E1-01-tc-owner-auth-session`.
- **Observed:** 43 passed / 0 failed / 2 xfailed, exit 0.
- **NOT established:**
  1. Không có audit độc lập. Đây là `SELF_VALIDATION`; `evidence/manifest.schema.json` nhánh
     thứ bảy **cấm** một bản ghi `SELF_VALIDATION` chống đỡ nhãn từ `IMPLEMENTATION_VERIFIED`
     trở lên, nên trường `claim` được **bỏ trống** trong manifest thay vì khai một nhãn mà
     schema từ chối. Nâng nhãn là việc của Coordinator/Auditor.
  2. Không có token bearer thật nào tồn tại; `TokenRegistry` rỗng theo mặc định. Việc phát,
     lưu và xoay token collector / analysis worker / backup operator thuộc card khác.
  3. 26 trong 36 cạnh của `boundary/a` **không** do lớp này quyết định.
  4. Mọi tham số phiên và băm vẫn `PROVISIONAL` trong `contracts/ops/secrets.md` và **cần
     Owner xác nhận**. Test khẳng định code **khớp** hợp đồng; nó không khẳng định con số là
     đúng.
  5. Bốn file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`
     (`openapi.yaml`, `internet-boundary.md`, `secrets.md`, `screens.yaml`); các điểm dừng KC
     ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**.
- **Review type:** `SELF_VALIDATION`. Tuyệt đối **không** phải "independent audit passed".

## 9. Checklist §8 của card

| Mục | Trạng thái | Ở đâu |
| --- | --- | --- |
| `pytest tests/contract/test_auth_scheme_matrix.py -q` | **DONE** exit 0 (17 passed) | EV-AUTH-01 |
| `pytest tests/integration/test_denied_edges.py -q` | **DONE** exit 0 (26 passed, 2 xfailed) | EV-AUTH-01 |
| Validator OpenAPI 3.1 (card ghi `NOT_RUN`) | **DONE** exit 0 — nay đã chạy | EV-AUTH-02 |
| Oracle fixture `h`: 0 hàng đổi, mã đúng hợp đồng | **PARTIAL** — seq1–3 PASS; seq4 xem `CR-TC-AUTH-01` | EV-AUTH-01 |
| Oracle fixture `i`: `save.create` bằng collector token ⇒ 401, `COUNT(saved_item)` không đổi | **DONE** | EV-AUTH-01 |
| Ma trận scheme: mọi mutation owner có cả hai scheme trong một requirement | **DONE** 17/17 | EV-AUTH-01 |
| Mọi route `backup.*` chỉ nhận `backupOperatorToken` | **DONE** | EV-AUTH-01 |
| Bảng ma trận scheme sinh từ openapi | **DONE** — sinh trong test và so bằng | `test_scheme_requirements_table_equals_the_contract` |
| Đếm hàng domain trước/sau | **DONE** cho `session`, `owner` | EV-AUTH-01 |

## 10. Next actor

`Coordinator`. Sáu CR cần phán quyết; `CR-TC-AUTH-01`, `CR-TC-AUTH-02` và `CR-TC-AUTH-06`
chạm file của gói khác nên chỉ Coordinator mới định tuyến được. `lease_released_at`
2026-09-07T10:20Z — sau mốc này tôi không ghi thêm file nào.

---

# ADDENDUM — `PKT-TC-AUTH-FIX1` (fix wave sau A3-R1)

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-AUTH-FIX1` · authority `AUTH-COORD-TC-AUTH-FIX1` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-TC-AUTH-e2` (fencing 2), hết hạn 2026-09-08T16:00Z |
| `worker_principal` | `worker-WA` |
| **`status`** | **`DONE`** |
| `completion_claim` | `IMPLEMENTATION_VERIFIED` cho phạm vi card, mức E1 — vẫn là `SELF_VALIDATION`; A3-R2 xác minh. |
| Findings đã xử lý | `F-A3R1-01`, `-02`, `-06`, `-08`, `-09`, `-12`, và `-13` (khối include của chính card này) |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T11:30Z |

## A.1 WAIT GATE

Poller chạy 11 vòng 60 s. Cả ba điều kiện mở trước khi tôi chạm migration hoặc schema test:
`evidence/handoffs/PC02-handoff.md` mang `PKT-PC02-FIX12`, `evidence/handoffs/P0-skeleton-handoff.md`
mang `PKT-P0-FIX2`, `evidence/handoffs/TC-canonical-identity-merge-handoff.md` mang
`PKT-TC-IDENTITY-FIX1`, mỗi cái kèm `lease_released`. `F-08`, `F-12`, `F-09` làm trước gate
như packet cho phép.

## A.2 `F-A3R1-01` + `F-A3R1-02` — một định nghĩa `owner`, và một cửa vĩnh viễn

`server/migrations/versions/0002_tc_owner_auth_session.py` **viết lại**: bỏ hoàn toàn
`CREATE TABLE owner` và hai lệnh `ALTER TABLE owner ADD COLUMN`; `down_revision` đổi từ
`"0001"` sang **`"0002_base_entities"`**. Revision nay tạo **một** bảng — `session` — cộng
`ux_session_token_hash` (tên của chính hợp đồng) và một index tra cứu theo `token_hash`. Bốn
cột credential/lockout đến từ `AMD-ENT-owner-01` trong `0002_base_entities`, và tôi **dùng**
chúng chứ không tự thêm. `alembic heads` = **1** (`0004_merge_phase1_heads`).

`tests/contract/test_schema_matches_entities.py` (mới, 8 test) là cửa vĩnh viễn. Sau
`alembic upgrade head` trên DB trắng nó khẳng định, trên **16 bảng** đang tồn tại:

| Phép kiểm | Kết quả |
| --- | --- |
| mọi bảng có entity cùng tên; mọi cột giải được về một field của `entities.yaml` | **PASS**, 0 cột lạ |
| `nullable` khớp **hai chiều** (contract NOT NULL ⇒ đĩa NOT NULL, và ngược lại) | **PASS**, 0 vi phạm |
| `keys.primary` khớp PK thật | **PASS** |
| mọi `keys.unique` (kể cả partial index) có mặt đúng tên hợp đồng | **PASS** |
| mọi `CHECK (...)` viết trong `constraints` có mặt trong DDL | **PASS** |
| bộ ràng buộc của `owner` đầy đủ (singleton CHECK + UNIQUE, `display_name` 1..120, `created_at` GLOB, 9 cột) | **PASS** |
| DDL **giống hệt** khi ép thứ tự duyệt nhánh ngược lại | **PASS**, 0 bảng khác nhau |
| `alembic heads` == 1 | **PASS** |

Đây chính là lớp khẳng định mà `F-A3R1-01` chỉ ra là vắng mặt: hai định nghĩa `owner` cũ chỉ
khác nhau **một CHECK**, nên một phép so cột sẽ không bắt được.

Bổ sung trong `tests/integration/test_denied_edges.py`:
`test_the_auth_revision_creates_only_its_own_table` đọc **mã nguồn** revision và khẳng định
không còn `CREATE TABLE owner` / `ALTER TABLE owner`, và `down_revision` đúng — nửa "quyền sở
hữu bảng" của cùng finding.

## A.3 `F-A3R1-06` — lockout bền, ghi trong cùng transaction đăng nhập

`LoginThrottle` (deque trong bộ nhớ) **bị gỡ**. Thay bằng `LockoutState`, đọc/ghi thẳng
`owner.failed_login_count` và `owner.locked_until`.

`AuthService.login` được cấu trúc lại quanh một điểm mà bản cũ làm sai: **mọi kết cục đều
ghi**, nên `AuthError` được **raise sau khi transaction commit**, không phải bên trong nó.
Raise bên trong `with self._engine.begin()` sẽ rollback đúng cái lần thất bại mà nó vừa định
đếm — đó là lý do bộ đếm cũ không thể bền dù có cột.

| Nhánh | Ghi gì | Commit point |
| --- | --- | --- |
| thành công | reset `failed_login_count = 0`, `locked_until = NULL`, INSERT `session` | cuối transaction |
| sai mật khẩu / không có tài khoản | `failed_login_count + 1`; chạm ngưỡng ⇒ `locked_until = now + 15 phút` | cuối transaction |
| đang bị khóa | **không ghi gì**; lần thử không được cộng thêm vào một lock đang hiệu lực | — |

Năm test mới, trong đó `test_the_lockout_counter_survives_a_process_restart` mô hình hoá
restart theo cách duy nhất chứng minh được điều gì đó: **vứt bỏ** `AuthService` cũ và dựng
một cái mới từ cùng file DB giữa lần thất bại thứ 4 và thứ 5. Một deque trên object cũ sẽ
biến mất; cột trên hàng `owner` thì không. Kèm: lock hết hạn thì mật khẩu đúng lại vào được;
đăng nhập đúng đặt bộ đếm về 0; tài khoản đang khoá không tích luỹ thêm.

**`CR-TC-AUTH-07` (mới, LOW).** Hợp đồng phát biểu ngưỡng là "5 lần / **15 phút**", nhưng bốn
cột của `AMD-ENT-owner-01` **không có mốc bắt đầu cửa sổ**, nên không biểu diễn được cửa sổ
trượt. Bản cài đặt đếm **liên tiếp** (đúng chữ của chính `failed_login_count`: "số lần đăng
nhập sai **liên tiếp**") và xoá khi thành công hoặc khi lock hết hạn. Đây là **tập cha** của
quy tắc hợp đồng: không bao giờ khoá muộn hơn hợp đồng đòi, nhưng có thể khoá với các lần
thất bại rải rộng hơn 15 phút. Thu hẹp lại cần một cột `failed_login_window_started_at` —
việc của change control, không phải của code. Ghi ở đây thay vì để im lặng.

## A.4 `F-A3R1-08` — quét default-deny nay là **toàn bộ 36 cạnh**, không còn sàn `>= 5`

`assert checked >= 5` bị gỡ. Cả 36 event của `boundary/a-default-deny-sweep-36-edges.json`
nay được **phân hoạch** và mỗi nhóm được khẳng định riêng. Với 5 dòng hai tầng, mã ở
**mức cạnh** (`expected_error_code_edge_class`) là mã lớp này phải sinh ra — đúng
`two_level_note_vi` của chính fixture.

| Nhóm | Số | Cách chứng minh |
| --- | --- | --- |
| `UNAUTHORIZED` ở mức cạnh | **12** | `classify_denial` trên `auth_scope` + `mutation` thật của operation, principal của actor. **Không loại trừ dòng nào.** |
| `FORBIDDEN_EDGE` ở mức cạnh | **10** | `require_edge` (8 dòng có operation) và `require_module_edge` (2 dòng `in_process_call`: `FE-08`, `FE-26`) — **mã thật**, cùng hàm mà service tầng trên gọi, không phải bản dựng lại trong test |
| `CAPABILITY_DENIED` | **14** | ghi `NOT_TESTABLE_AT_THIS_LAYER`, mỗi dòng nêu cơ chế thực thi; **không** đếm là pass |
| Tổng | **36** | một test riêng khẳng định ba nhóm phân hoạch đúng: giao rỗng, hợp đủ, `12 + 10 + 14 = 36` |

Danh sách loại trừ **không** được tin theo lời khai của tôi: test đọc `enforcement` từ chính
fixture và đòi nó là tập con của ba cơ chế phi-HTTP (`ENF-process-capability`,
`ENF-network-egress-allowlist`, `ENF-import-rule`), **và** đòi `ENF-api-auth-test` vắng mặt —
nếu một dòng khai `ENF-api-auth-test` thì nó với tới được ở đây và phải bị khẳng định, không
được biện hộ.

### Hai thứ mới trong `server/app/auth/middleware.py`

`ALLOWED_CALLERS` (85 operation, từ `ports.yaml.caller_modules`) và `ALLOWED_MODULE_EDGES`
(51 cặp, từ `modules.yaml.allowed_edges`), cộng `require_edge` / `require_module_edge`. Cần
**cả hai** dạng: hai cạnh bị cấm (`FE-28` report→analysis, `FE-33` telegram→job) nằm giữa các
cặp module **được phép** cho operation khác, nên một phép kiểm ở mức cặp sẽ cho chúng đi qua.
Ba test contract mới gác: hai test dựng lại bảng từ hợp đồng và so bằng, một test khẳng định
không cạnh nào trong 36 `forbidden_edges` với tới được qua bất kỳ registry nào — lấy oracle
từ `modules.yaml` chứ không từ fixture, nên hai oracle buộc phải đồng ý với nhau.

**Một lỗi thật do việc quét toàn bộ phát hiện ra.** `classify_denial` trước đây trả
`FORBIDDEN_EDGE` cho `auth_scope: internal_only`. Sai: một port `internal` **không có đường
HTTP nào**, nên không lớp principal nào từ dây có thể thoả nó — đó là hàng 1 của R5-01 (sai
lớp principal) và mã là `UNAUTHORIZED`, đúng như fixture pin cho `FE-07` và `FE-13`.
`FORBIDDEN_EDGE` là câu trả lời cho câu hỏi **khác** (lời gọi trong tiến trình qua cạnh không
có trong registry) và nay là `require_edge`. Sàn `>= 5` cũ đã che đúng lỗi này.

## A.5 `F-A3R1-12` — token bearer lưu và so bằng hash

`TokenRegistry` rút mọi token về `sha256:<hex>` khi nhận và **không giữ bản rõ** (secrets.md
§3: "server lưu `sha256`, không lưu bản rõ"), so bằng `hmac.compare_digest` trên **mọi** mục
thay vì trả về ở lần khớp đầu — nên cả giá trị lẫn vị trí khớp đều không suy ra được từ thời
gian. Thêm `TokenRegistry.from_hashes()` cho đường vận hành thật: server được cấu hình bằng
digest, token chỉ tồn tại trên máy trình nó. Hai test, trong đó một test `repr` toàn bộ trạng
thái nội bộ và khẳng định chuỗi bản rõ **không** xuất hiện.

## A.6 `F-A3R1-09` — kiểm kê fixture của §2

`CARD_FIXTURES` trong `tests/contract/test_auth_scheme_matrix.py` liệt kê cả **năm** fixture
mà §2 mục 5 nêu tên; mỗi mục hoặc `EXERCISED` (kèm nơi) hoặc `NOT_RUN` (kèm lý do), và một
test khẳng định điều đó.

| Fixture | Trạng thái |
| --- | --- |
| `recovery/h-unauthenticated-owner-api` | EXERCISED — SC40 |
| `recovery/i-collector-token-calls-save` | EXERCISED — SC41 |
| `boundary/a-default-deny-sweep-36-edges` | EXERCISED — SC49, cả 36 dòng |
| `ui/sc51-first-time-setup` | EXERCISED — SC51, bước đăng nhập |
| `recovery/g-ssrf-redirect-private` | **NOT_RUN** — SC39 là ca SSRF trên `research.fetch_work_metadata`, thuộc `MOD-research-connector`. Nó không chạm đường code auth nào: ranh giới nó kiểm là egress **theo từng hop redirect** (`CAPABILITY_DENIED` / `SOURCE_METADATA_UNAVAILABLE`), không phải một security scheme. Không có card connector nào trong M1. |

`test_the_not_run_fixture_is_out_of_this_cards_reach` đọc fixture và **chỉ ra** vì sao nó
không phải của card này (operation thuộc module khác; không mã lỗi nào của card này xuất hiện
trong đó) thay vì chỉ khai một nhãn.

## A.7 `F-A3R1-13` — khối include của card này

`server/app/main.py`: khối đổi sang delimiter `# >>> TC-owner-auth-session … >>>` /
`# <<< TC-owner-auth-session <<<`, và `from server.app.auth.router import install_auth`
chuyển **vào trong** delimiter (trước đây nó ở mức module, ngoài khối — đúng như audit nêu).
Không dòng nào của ba khối card khác bị chạm.

## A.8 Changes

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `server/app/auth/service.py` | MODIFY | `2d9af830548fdc582aa1199ad65b7b3f93c3a58d763bd79eb101fecd202a1eb9` | 31176 |
| `server/app/auth/middleware.py` | MODIFY | `004ae8676b5fdb931a25b1d344ef3aa6085dbc482e6f876aff097b5528d2238c` | 29623 |
| `server/migrations/versions/0002_tc_owner_auth_session.py` | MODIFY | `a315cbf4c8c4e933675f3f6decf1f100b1c55d1d68497bec15f3312226fd850f` | 4232 |
| `tests/contract/test_auth_scheme_matrix.py` | MODIFY | `9ac6dd0870fbbb694e71caa556a5ee887cbf7c850ab0ca2977edb9c2a1867dae` | 18395 |
| `tests/contract/test_schema_matches_entities.py` | **CREATE** | `82dae292a0aa3625f36316fb5bcabde8e83ee3e39ed8a2871dcbf4e63b9cd6fd` | 11761 |
| `tests/integration/test_denied_edges.py` | MODIFY | `e96cf662c9b64325446f1a023591d4e77abf2619739b02d42f2c02ea52980944` | 40016 |
| `server/app/main.py` | MODIFY (chỉ khối của card này) | `2adbf75efb49964f1906feb5334c52d5f6b40ea78daff7eefb1d9f48eb4cde35` | 7696 |

`server/app/auth/csrf.py`, `server/app/auth/router.py`, `server/app/auth/__init__.py`: **không đổi**.

## A.9 Evidence — `SELF_VALIDATION`, E1

| Lệnh | Kết quả |
| --- | --- |
| `uv run pytest` (toàn cây) | **303 passed, 0 failed, 4 xfailed**, exit **0**, 41 s (2026-09-07T11:25:05Z→11:25:47Z) |
| `uv run pytest tests/contract/test_schema_matches_entities.py` | **8 passed**, exit 0 |
| `uv run pytest tests/contract/test_auth_scheme_matrix.py` | **21 passed**, exit 0 |
| `uv run pytest tests/integration/test_denied_edges.py` | **36 passed, 2 xfailed**, exit 0 |
| `alembic heads` | **`0004_merge_phase1_heads` — đúng 1 head** |
| `uv run ruff check .` · `ruff format --check .` | exit **0** · 61 file đã format |
| `uv run mypy` (`--strict` trên `server/app`) | exit **0**, 25 file |
| `uv run python evidence/tools/verify_cards.py --repo .` | **13/13 check, 3 214 assertion, 0 violation** |
| SRC-SPEC / SRC-PLAN sha256 | khớp §4 ở đầu và trước addendum |

Hai `xfail` của card này giữ nguyên và giữ nguyên lý do: `CR-TC-AUTH-01` (fixture
`recovery/h` seq4 còn pin `FORBIDDEN_EDGE` cho ca thiếu CSRF) và cửa `storage.get_health =
write_blocked` chờ `TC-storage-write-blocked-readiness`.

## A.10 CR sau đợt này

| ID | Trạng thái |
| --- | --- |
| `CR-TC-AUTH-02`, `CR-TC-AUTH-03` | **ĐÓNG** bởi `AMD-ENT-owner-01`. Bốn cột nay trong `entities.yaml`, `0002_base_entities` tạo chúng, card này dùng chúng. |
| `CR-TC-AUTH-06` | **ĐÓNG** cho phần của tôi: revision id duy nhất, chuỗi tuyến tính sau `0002_base_entities`, một head. |
| `CR-TC-AUTH-01` | **CÒN MỞ.** Fixture `recovery/h` seq4 chưa sửa; test `xfail(strict=True)` vẫn là bản ghi. |
| `CR-TC-AUTH-04` | **CÒN MỞ.** `ports.yaml.auth.login.error_codes` và `errors.yaml.RATE_LIMITED.operations` vẫn không nêu `auth.login`, dù `openapi.yaml` khai 429 và secrets.md §2.3 bắt buộc. |
| `CR-TC-AUTH-05` | **CÒN MỞ, và nay lớn hơn.** `generate.py` chưa phơi `caller_modules` (nay là **hai** bảng viết tay: của tôi và `ALLOWED_CALLERS` trong `server/app/identity/service.py`), `message_safe_template_vi`, `details_safe_keys`, và model Pydantic cho component inline của `openapi.yaml`. Cả hai bản đều có test so bằng với hợp đồng nên không thể phân kỳ im lặng, nhưng chúng nên gộp làm một. |
| `CR-TC-AUTH-07` | **MỚI (LOW).** Cửa sổ 15 phút của lockout không biểu diễn được bằng bốn cột đã sửa; bản cài đặt là tập cha đếm-liên-tiếp. Xem A.3. |
| `CR-TC-AUTH-08` | **MỚI (LOW).** Docstring của `server/migrations/versions/0004_merge_phase1_heads.py` nay **sai**: nó vẫn viết rằng auth revision `CREATE TABLE IF NOT EXISTS owner` rồi thêm hai cột credential, và rằng "either order produces the same schema". File thuộc `TC-canonical-identity-merge`; tôi không sửa. |
| Ghi chú về "use the generated owner model" | `contracts/data/entities.yaml` **không** phải nguồn của `shared/rr_contracts/generate.py` (nguồn là `schemas/`, `state/`, `errors.yaml`, `ports.yaml`, `openapi.yaml`), nên **không tồn tại** model owner sinh ra để dùng. `tests/contract/test_schema_matches_entities.py` lấy oracle **trực tiếp từ `entities.yaml`**, mạnh hơn: nó so schema thật với hợp đồng thật, không qua một lớp sinh trung gian. |

`next_actor`: `Coordinator`. `lease_released_at`: 2026-09-07T11:30Z — sau mốc này tôi không
ghi thêm file nào.

---

# ADDENDUM — `PKT-TC-AUTH-FIX2` (A3-R2: `F-A3R2-02`, `F-A3R2-03`)

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-AUTH-FIX2` · authority `AUTH-COORD-TC-AUTH-FIX2` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-TC-AUTH-e3` (fencing 3), hết hạn 2026-09-08T16:00Z |
| **`status`** | **`DONE`** |
| Findings | `F-A3R2-02` (schema test mù với generated column, và chỉ so một chiều), `F-A3R2-03` (manifest E1 cũ trỏ vào byte không còn tồn tại) |
| `next_actor` | `Coordinator` · `lease_released_at` 2026-09-07T11:45Z |

## B.1 `F-A3R2-02` — `table_xinfo`, hai chiều, bốn thứ tự duyệt

`tests/contract/test_schema_matches_entities.py` viết lại. Ba thay đổi thực chất:

**(a) `PRAGMA table_info` → `PRAGMA table_xinfo`.** `table_info` **bỏ qua STORED generated
column**. Hôm nay có đúng ba: `analysis.target_key`, `saved_item.target_key`,
`work_label.target_key` — và chúng mang ngữ nghĩa duy nhất của cả target union, nên lớp cột
đáng kiểm nhất lại chính là lớp cột mà phép kiểm không nhìn thấy. Đo được: `xinfo` trả
**198** cột, `table_info` chỉ trả **195**.

Không chỉ đổi pragma rồi tin: `test_generated_columns_are_visible_to_this_check` khẳng định
đúng ba cột đó có `hidden ∈ {2, 3}` **và** khẳng định `table_info` vẫn thật sự giấu chúng.
Nếu SQLite đổi hành vi, test tự nói tiền đề của nó đã dịch chuyển thay vì im lặng.

**(b) Bao hàm **hai chiều**.** Bản cũ chỉ khẳng định `shipped ⊆ contract`: nó bắt được một
cột xuất hiện mà hợp đồng không khai, nhưng **không nói gì** về một field hợp đồng khai mà
migration chưa bao giờ tạo — một cột thiếu đọc ra là pass. Nay là đẳng thức trên từng bảng đã
ship.

| Chiều | Đo được |
| --- | --- |
| cột đã ship → field của `entities.yaml` | **198 / 198**, 0 cột không khai |
| field của `entities.yaml` → cột đã ship | **198 / 198**, 0 field thiếu |

**(c) Generated column và `nullable: false`.** Ba cột `target_key` khai `nullable: false`
nhưng SQLite không cho generated column mang `NOT NULL` trực tiếp — audit A3-R1 xếp nó vào
lớp `F-A3R1-14` "ghi nhận, không phải defect". Bản này **không miễn trừ** chúng: nó đọc biểu
thức `GENERATED ALWAYS AS (...)` ra khỏi DDL, lấy các cột nguồn, và đòi mỗi cột nguồn hoặc
`NOT NULL`, hoặc được một `CHECK ... IS NOT NULL` trong cùng bảng bảo đảm. Với `target_key`
điều đó đúng qua `target_kind` (NOT NULL) và CHECK `exactly_one` trên
`target_work_id`/`target_post_id`. Non-null **bởi cấu tạo**, được chứng minh chứ không được
bỏ qua.

**(d) Bốn thứ tự duyệt.** Ba nhánh mọc từ `0002_base_entities`, nên có bốn đường
`upgrade` mà một deployment thật có thể đi. Cả bốn được dựng và so **chữ ký schema**:

| Thứ tự | Targets |
| --- | --- |
| `default` | `head` |
| `auth_branch_first` | `0002_tc_owner_auth_session` → `head` |
| `ingest_branch_first` | `0003_tc_ingest_idempotent_ack_lost` → `head` |
| `identity_branch_first` | `0003_tc_canonical_identity_merge` → `head` |

Chữ ký gồm DDL đã chuẩn hoá của mọi object **cộng** danh sách cột đọc bằng `xinfo` kèm
`notnull`/`pk`/`hidden` — vì một generated column vô hình với `table_info` có thể khác nhau
giữa hai DB mà văn bản `sqlite_master` sau chuẩn hoá lại trùng. Kết quả: **0 khác biệt** trên
cả bốn.

**Kết quả:** `10 passed`, exit 0 (trước: 8). 16 bảng · 198 cột hai chiều · 3 generated column
mà `table_info` bỏ sót · 18 unique key · 4 thứ tự duyệt · `alembic heads` = 1.

## B.2 `F-A3R2-03` — phát hành lại manifest E1

| | |
| --- | --- |
| **Mới** | `evidence/runs/TC-owner-auth-session-E1-20260907T114030Z.json` · `EV-E1-02-tc-owner-auth-session` · sha256 `f567e1757a732762f39f59f1c12ebc70b0987fdf58209ecb524d62ff5d20a1c7` · 11 768 B |
| **Cũ** | `evidence/runs/TC-owner-auth-session-E1-20260907T101529Z.json` · `EV-E1-01-…` · nay `result: STALE` · sha256 `9bd2d591b6afb8656520d3f8e0a47f1443c0281818d6bf30d82f9afcfaca5146` |

Bản mới lấy hash hợp đồng từ **byte hiện hành** (`contracts/data/entities.yaml` đã đổi theo
`AMD-ENT-owner-01`, và nó là một `invalidated_by_path` của bản cũ) và ghi một lượt chạy
**mới**: `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:warnings`, 2026-09-07T11:39:48Z →
11:40:30Z, exit **0**, **305 passed / 0 failed / 4 xfailed**. `oracle.expected` và
`oracle.observed` mang 19 con số đo được (bảng, cột hai chiều, generated column, unique key,
thứ tự duyệt, ba nhóm của sweep 12/10/14, 17 owner mutation, 0 endpoint signup, số test).

Bản cũ **không bị xoá và không bị viết lại**: nó chuyển sang `result: STALE` với
`stale_reason` nêu đích danh bản thay thế và từng thay đổi làm nó hết hiệu lực. Đây là điều
SRC-PLAN §16 quy định cho bằng chứng ghim vào byte đã bị thay: nó `STALE`, không phải `FAIL`
— không quan sát nào trong đó sai vào lúc nó được quan sát, nó chỉ không còn mô tả cây hiện
tại. Cả hai file validate sạch với `evidence/manifest.schema.json`
(`jsonschema.Draft202012Validator`).

## B.3 Changes

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `tests/contract/test_schema_matches_entities.py` | MODIFY | `8aa010591d73fbbb7e0b488359281568ca8f09885a9711bf9f78b43214e2be5f` | 18739 |
| `evidence/runs/TC-owner-auth-session-E1-20260907T114030Z.json` | **CREATE** | `f567e1757a732762f39f59f1c12ebc70b0987fdf58209ecb524d62ff5d20a1c7` | 11768 |
| `evidence/runs/TC-owner-auth-session-E1-20260907T101529Z.json` | MODIFY (→ STALE) | `9bd2d591b6afb8656520d3f8e0a47f1443c0281818d6bf30d82f9afcfaca5146` | 11886 |

Không file nào khác bị chạm. `server/app/**` không đổi trong đợt này.

## B.4 Evidence

| Lệnh | Kết quả |
| --- | --- |
| `uv run pytest -p no:warnings` | **305 passed, 0 failed, 4 xfailed**, exit **0**, 41 s |
| `uv run pytest tests/contract/test_schema_matches_entities.py` | **10 passed**, exit 0 |
| `uv run pytest tests/contract/test_auth_scheme_matrix.py` | **21 passed**, exit 0 |
| `uv run pytest tests/integration/test_denied_edges.py` | **36 passed, 2 xfailed**, exit 0 |
| `uv run ruff check .` · `uv run mypy` | exit **0** · exit **0**, 25 file |
| `alembic heads` | 1 (`0004_merge_phase1_heads`) |
| SRC-SPEC / SRC-PLAN sha256 | khớp §4 |

Không CR mới. `CR-TC-AUTH-01`, `-04`, `-05`, `-07`, `-08` vẫn mở như addendum trước.

`lease_released_at`: 2026-09-07T11:45Z — sau mốc này tôi không ghi thêm file nào.
