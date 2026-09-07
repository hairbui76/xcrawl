---
contract_id: CT-docs-master-plan
document_type: MASTER_PLAN
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs:
  - "SRC-SPEC research-radar-spec.md sha256:d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26 (41770 B)"
  - "SRC-PLAN research-radar-pre-code-plan.md sha256:f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40 (64915 B)"
  - "precode/owner-decisions.md sha256:c5d411e561d464cbb6a05b42938dd11b4925506b12b72736ab46b354ba9ad994 (12373 B)"
  - "precode/review.md sha256:1da31eb0559cc11fa1daafba258763975b86318bdc634fa31679cedc60a499bc (125319 B)"
  - "agent-tasks/README.md sha256:fadad4a385b4ef0f37c9103aa3066dc08bad76ba40760ea15893d648c343ff93 (20215 B)"
  - "precode/adr/ADR-0011 (framework + toolchain; W1 đang ghi song song — dẫn theo đường dẫn, KHÔNG pin hash)"
requirement_refs: [REQ-P0-01, REQ-P0-02, REQ-P0-03, REQ-P0-04, REQ-P0-05, REQ-P0-06, REQ-P0-07, REQ-P0-08, REQ-P0-09, REQ-P0-10, REQ-P0-11, REQ-P0-12, REQ-OQ03, REQ-A1, REQ-A2, REQ-A3, REQ-A4, REQ-A5, REQ-A6, REQ-A7]
decision_refs: [OD-20260907-01, ADR-0006, ADR-0011, "B01..B17 RATIFIED"]
invariant_refs: [I01, I02, I03, I04, I05, I06, I07, I08, I09, I10, I11, I12, I13, I14, I15, I16, I17]
producers: []
consumers: []
dependencies:
  - agent-tasks/README.md
  - precode/gates.yaml
  - acceptance/scenarios.yaml
  - acceptance/traceability.csv
scope: >-
  Kế hoạch tổng thể và lộ trình triển khai Research Radar sau khi Owner phê chuẩn OD-20260907-01.
  Mô tả vị trí hiện tại, stack và toolchain, bảy giai đoạn theo mốc M0–M8 và cổng G5–G7, ước lượng
  công sức tương đối, sổ rủi ro, các điểm Owner phải chạm tay, và cách chứng minh tiến độ.
verification: >-
  EV-PC10-07 (SELF_VALIDATION): prose-token gate — mọi operation ID, entity, mã lỗi, card ID, SC ID,
  REQ ID và invariant nêu trong file này phải giải được về hợp đồng sở hữu. Không có phép đo runtime
  nào trong file này; mọi mức bằng chứng E1–E4 đều là DỰ KIẾN.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Research Radar — Kế hoạch tổng thể và lộ trình

> **File này là kế hoạch, không phải bằng chứng.** Mọi mức bằng chứng nêu ở đây (E1–E4) là **dự
> kiến sẽ đạt được**, không phải đã đạt. Tại thời điểm viết: **chưa dòng code sản phẩm nào tồn
> tại**, E0 đã chạy thật (của PC09), **E1–E4 đều `NOT_RUN`**. Ước lượng công sức là **tương đối**,
> tính bằng ngày công, **không có ngày lịch** — chúng phụ thuộc nhịp làm việc thật của Owner.

---

## 1. Chúng ta đang ở đâu

### 1.1 Đã phê chuẩn

Ngày 2026-09-07 Owner trả lời từng câu hỏi và tạo `OD-20260907-01` (authority
`AUTH-OWNER-20260907-02`). Hệ quả:

- **17 blocker `B01`–`B17` → `RATIFIED`**; 14 amendment `ACCEPTED`; mười ADR `accepted`.
  `agent_profile/registry.json` có `open_product_blockers: []`.
- **Stack = Option B** — Python cho `server/`, `collector/`, `worker/`, `probe/`; TypeScript cho
  `web/`. Ranh giới hai ngôn ngữ là HTTP API đã có hợp đồng (`contracts/http/openapi.yaml`), nên
  ngôn ngữ thứ hai **không** sinh thêm cạnh quyền nào ngoài `contracts/modules.yaml`.
- **Timezone** `Asia/Ho_Chi_Minh` xác nhận; **D09** Chrome profile riêng của dự án xác nhận;
  **`data.purge_all`** chốt phạm vi (chỉ dữ liệu nghiên cứu; giữ đăng nhập, secrets, liên kết
  Telegram, cấu hình provider, lịch; **backup không bị xóa**).
- Bộ giá trị mặc định OQ, tám tham số PC04, gói tham số PC08 — tất cả thành **giá trị làm việc được
  Owner chấp nhận**.

Điều thay đổi về chất: trước phê chuẩn, danh sách chờ Owner chứa những mục mà **không Worker nào**
gỡ được và **mọi** module đều dính. Nay chỉ còn **một** mục chặn một mốc.

### 1.2 Bốn phạm vi `CONTRACT_READY`, bốn phạm vi vẫn `DRAFT`

| Phạm vi | Trạng thái | Vì sao |
| --- | --- | --- |
| Ranh giới và quyền (`modules.yaml`, `capabilities.yaml`, `ports.yaml`, `ops/deployment.md`) | **`CONTRACT_READY`** | 25 module, 99 cạnh cho phép, 36 cạnh cấm, bijection 36↔36 với denied case và sweep event |
| Dữ liệu và định danh (`data/*`, `schemas/target`, `ingest-batch`) | **`CONTRACT_READY`** | 60 entity, transaction map, 14 fixture `identity/` cũng đã lên `CONTRACT_READY` |
| Workflow và trạng thái (`state/*`, `errors.yaml`, `retry-policy.yaml`) | **`CONTRACT_READY`** | 5 máy trạng thái, 28 mã lỗi đủ 10 trường, 41 ngân sách có số |
| Báo cáo và thời gian (`reporting/*`, `schemas/report`) | **`CONTRACT_READY`** | coverage half-open, backfill ledger, **14** fixture `reporting/` cũng đã lên `CONTRACT_READY` |
| **Collector** (`ops/collector-probe.md`) | `DRAFT` | `REQ-A1`, `REQ-A7` — cần probe thật |
| **AI** (`ai/*`, `ops/cli-acp-probe.md`) | `DRAFT` | `REQ-A5` (điều khoản từng nhà), `REQ-OQ03` (provider chưa chọn), `REQ-A2`/`REQ-A3` (chưa đo) |
| **Telegram** (`telegram/*`) | `DRAFT` | `CR-PC07-04` — năm giới hạn định dạng còn `KC` |
| **Ops còn lại** (`secrets.md`, `backup-restore.md`, `internet-boundary.md`) | `DRAFT` | `REQ-A6` (nhịp gọi arXiv/OpenAlex), chưa drill restore nào chạy |

Ngoài ra `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml` và bốn schema
(`ingest-receipt`, `worker-assignment`, `saved-snapshot`, `analysis-result`) vẫn khai
`claim_ceiling: DRAFT_FOR_REVIEW` trong header của chính chúng (`CR-PC10-07`).

### 1.3 Cổng

| Cổng | Trạng thái | Điều còn thiếu |
| --- | --- | --- |
| G0 Baseline | **MET** | — |
| G1 Boundaries | **MET** | — |
| G2 Data/workflow | **MET** | — |
| G3 Domain contracts | `PARTIALLY_MET` | các mục `KC` (§1.4) |
| G4 Auditable baseline | `PARTIALLY_MET` | G4-X7 và phần `KC` của G3 |
| **G5 Task ready** | **`NOT_MET`** | **`G5-X4`: chưa có bố cục repo triển khai** — card trỏ vào đường dẫn *sẽ* tồn tại, không phải *đang* tồn tại. G5-X1/X2/X3 đã đạt |
| G6 Integration/live | `NOT_APPLICABLE_YET` | — |
| G7 Product acceptance | `NOT_APPLICABLE_YET` | — |
| SP1 Feasibility probe | **`NOT_MET`** | Hai điều kiện khác nhau, đừng gộp: (a) cổng Owner ở `collector-probe.md` §6 chưa mở; (b) **bằng chứng probe là `NOT_RUN`**. `NOT_MET` là từ vựng của cổng; `NOT_RUN` là từ vựng của bằng chứng |

**`G5-X4` là việc đầu tiên của lộ trình này** — đó chính là Giai đoạn 0.

### 1.4 Mười lăm dòng `KC` — cái mà không lượng soạn thảo nào gỡ được

`REQ-A1` (X thu thập đều đặn), `REQ-A2` (ngưỡng embedding), `REQ-A3` (model đa ngôn ngữ),
`REQ-A4` (mật độ phát hiện hướng nổi), `REQ-A5` (điều khoản từng nhà AI), `REQ-A6` (nhịp gọi
arXiv/OpenAlex), `REQ-A7` (X có thể hạn chế tài khoản — **không kiểm chứng được trước**),
`REQ-D34`, `REQ-D47`, `REQ-OQ08`, `REQ-OQ09`, `REQ-S1.4-04`, `REQ-S10.2-06`, `REQ-S13.2-01`,
`REQ-S13.2-02`.

Phê chuẩn **không chạm** vào bảng này, và đó là kết quả đúng: Owner phê chuẩn được văn bản cam
kết, không phê chuẩn được nhịp gọi của arXiv hay chất lượng của một model. Bảy module còn chặn
cứng đều chặn vì một `KC` hoặc một phép đo chưa chạy — **không module nào còn chặn vì thiếu quyết
định**, trừ `MOD-settings-service` (Owner chọn hoãn `REQ-OQ03`).

### 1.5 Danh sách mục còn mở

| ID | Nội dung | Chặn |
| --- | --- | --- |
| `REQ-OQ03` | Provider và model AI cụ thể — Owner **chọn hoãn** | `MOD-settings-service`, **M3** |
| `CR-PC07-04` | Năm giới hạn định dạng Telegram còn `KC` | nhánh multipart của delivery, một phần `REQ-AC14` |
| `CR-PC05-03` | Nhịp gọi arXiv/OpenAlex — không nguồn nào chứa URL tài liệu | `CONTRACT_READY` của research connector |
| `CR-PC06-04` | Chưa adapter CLI/ACP nào qua probe | `REQ-AC16` báo **BLOCKED**, không phải FAIL |
| `CR-PC02-04`, `-05`, `-17`, `-22` | Giới hạn ingest/snapshot, ngưỡng merge, retention, và **số Owner duyệt theo gói mà chưa từng thấy** | vòng Owner kế tiếp |
| `CR-PC07-01`, `-05` | Tham số liên kết Telegram, `telegram_update_max_age` | vòng Owner kế tiếp |
| `CR-PC01-13`, `CR-PC10-07` | Ranh giới phạm vi phê chuẩn chỉ tồn tại trong danh sách đường dẫn của `E0-12`, không trong cây hợp đồng | vòng Owner kế tiếp |
| `CR-PC09-13`, `-14` | `requirements.csv` chưa cập nhật theo mục 1/3; `claim_ceiling` mang hai nghĩa | độ chính xác của chính sổ |
| `CR-PC10-05` | `precode/review.md` còn tên epoch cũ | — |
| **Validator OpenAPI 3.1** | **Chưa validator nào chạy** trên `contracts/http/openapi.yaml` trong toàn bộ Pre-code. File này là nguồn sinh ra model Pydantic và client TypeScript (§2.3), nên một lỗi cấu trúc trong nó lan thẳng vào code sinh của **cả hai** tầng | Sinh code ở Giai đoạn 0; `CONTRACT_READY` của chính `openapi.yaml` |
| `CR-PC10-08` | `REQ-S7.3-01` (`owner_id` mọi bảng) không là nghĩa vụ chứng minh của card nào | lỗ hổng phủ đã đo |
| `PROV-PC03-04` | `analysis_unknown_attempt_auto_rerun = 1` — PC03 tự xin soi kỹ | — |
| `PROV-PC01-01`…`-06` | Sáu quyết định kỹ thuật cấp gói | không chặn card |

### 1.6 Phủ P0 — đã đo

`EV-PC10-06` đối chiếu `acceptance/traceability.csv` (246 hàng) với 18 card:

- **12/12** mục phạm vi `REQ-P0-01`…`REQ-P0-12` phủ, và phủ **mạnh** (qua SC có oracle).
- Trên toàn bộ 234 hàng `priority = P0`: **192 mạnh**, 31 yếu (chỉ trùng file hợp đồng), 11 không
  card. Mười trong mười một là mốc/chỉ số/prose lỗi thời; một là lỗ hổng thật (`CR-PC10-08`).
- Con số trung thực để trích dẫn là **192/234 mạnh**, không phải 223 và không phải 234.

---

## 2. Stack, toolchain và bố cục repo

Nguồn: `precode/adr/ADR-0011` (`provisional-accepted`; Owner ủy quyền cho Coordinator chọn và **có
thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng**).

### 2.1 Bảng chọn

| Tầng | Lựa chọn |
| --- | --- |
| Python | 3.12, `uv` cho env + lock, `pyproject.toml` cho mỗi package |
| Server API | FastAPI + Pydantic v2, model **sinh từ** `contracts/schemas/*.json` và `contracts/http/openapi.yaml` |
| Persistence | SQLAlchemy 2 Core (không ORM magic) + Alembic, SQLite WAL, `PRAGMA foreign_keys=ON`, Online Backup API |
| Queue/scheduler | Bảng hàng đợi theo `contracts/data/entities.yaml` + vòng lặp scheduler in-process; **không broker ngoài** |
| Collector | Playwright for Python, persistent context trên Chrome profile riêng (D09), `httpx` tới server |
| Analysis worker | `httpx` + adapter: API qua SDK/httpx, CLI/ACP qua `subprocess` với cờ tool/network theo `contracts/ai/providers.yaml` |
| Embedding | `sentence-transformers` trên server, vector là BLOB, cosine quét tuyến tính (D49) |
| Telegram | Bot API trực tiếp qua `httpx`; **không** bot framework (retry của framework sẽ vi phạm B03) |
| Web UI | Vite + React 18 + TypeScript, TanStack Query, client sinh bằng `openapi-typescript` |
| Auth | Cookie phiên HttpOnly + CSRF double-submit, Argon2id qua `argon2-cffi` |
| Test | `pytest` (+`pytest-asyncio`) nạp thẳng fixture từ `acceptance/fixtures/**`; Vitest + Testing Library; Playwright Test cho E2E |
| Lint | `ruff`, `mypy --strict` trên server core, `eslint` + `prettier`, `PYTHONDONTWRITEBYTECODE=1` |

### 2.2 Bố cục repo

```
server/            Python  FastAPI app, domain service đặt tên theo MOD-*, migrations
collector/         Python  Playwright + client tới worker API
worker/            Python  analysis worker + AI adapter
probe/             Python  kịch bản SP1 (M0)
shared/rr_contracts/  Python  model + hằng số SINH RA từ contracts/
web/               TypeScript  src/{lib,routes,views}, tests/{contract,integration}
tests/             Python  contract, unit, integration
```

### 2.3 Hai quy tắc không thương lượng

1. **Sinh từ hợp đồng, không viết tay.** Model Pydantic, client TypeScript và hằng số enum sinh từ
   `contracts/`. File sinh ra **không bao giờ** được sửa tay; E0 sẽ có thêm một phép kiểm "file
   sinh khớp hash hợp đồng". Sửa hành vi ⇒ sửa hợp đồng ⇒ sinh lại ⇒ card `STALE` theo `INV-06`.
2. **Fixture là oracle duy nhất.** Test nạp thẳng `acceptance/fixtures/**`. **Không có bộ dữ liệu
   test thứ hai.** Sửa fixture để test pass là vi phạm SRC-PLAN §15.

### 2.4 CI

| Job | Chạy gì | Cấp |
| --- | --- | --- |
| `openapi` | Validate `contracts/http/openapi.yaml` bằng một validator **OpenAPI 3.1 thật**, chạy **trước** bước sinh code. Công cụ **PROVISIONAL**: `openapi-spec-validator` (Python) hoặc Redocly CLI (Node) — chốt ở bản sửa kế tiếp của ADR-0011. Job này fail ⇒ **không sinh code**, vì model Pydantic và client TypeScript đều sinh từ file đó | E0 |
| `e0` | `evidence/tools/e0_check.py` + card-pin verifier (501 dòng hash / 144 file) | E0 |
| `python` | `pytest` trên `tests/contract` và `tests/integration` | E1/E2 |
| `web` | `vitest` + `tsc --noEmit` | E1 |
| — | **Không job live.** E3/E4 là thủ công theo protocol; CI không được phép chạm X, provider AI hay Telegram | — |

---

## 3. Lộ trình

Ký hiệu: **DoD** = definition of done · **Trần** = claim ceiling đạt được · Thứ tự card theo đồ thị
phụ thuộc ở `agent-tasks/README.md` §3.

### Giai đoạn 0 — Bộ khung repo và CI

- **Cổng vào:** G4 cho phạm vi định giao; Owner ra lệnh bắt đầu.
- **Card:** không có. Đây là việc hạ tầng, **cố ý không phát card** — nó không có hành vi nghiệp vụ
  để kiểm.
- **Việc:** dựng bảy cây thư mục §2.2; `uv` lock; sinh `shared/rr_contracts/` từ `contracts/`; sinh
  client TS; ba job CI; `ruff`/`mypy`/`eslint` chạy sạch trên cây rỗng.
- **Bên ngoài:** không.
- **Bằng chứng:** E0 — CI xanh trên một repo chưa có logic nghiệp vụ; manifest `EVM-phase0`.
- **DoD:** **`G5-X4` chuyển `met: true`** — mọi đường dẫn §3 của 18 card tồn tại trên đĩa. Đây là
  điều kiện duy nhất còn thiếu của G5.
- **Trần:** không có claim sản phẩm. G5 chuyển `MET`.
- **Dừng nếu:** Owner bác một dòng của ADR-0011 ⇒ dừng, ghi ADR mới, sinh lại; **không** tự đổi.
- **Ước lượng:** 3–5 ngày công.

### Giai đoạn 1 — M1 kho dữ liệu, ingest và auth

- **Cổng vào:** G5 `MET`.
- **Card, theo thứ tự:** `TC-owner-auth-session` → `TC-ingest-idempotent-ack-lost` →
  `TC-canonical-identity-merge` → `TC-storage-write-blocked-readiness`.
- **Operation:** `auth.login`, `auth.logout`, `auth.get_session`, `ingest.submit_batch`,
  `ingest.commit_checkpoint`, `ingest.get_receipt`, `ingest.get_checkpoint`,
  `identity.resolve_target`, `identity.record_alias`, `identity.quarantine_conflict`,
  `identity.merge_works`, `identity.resolve_conflict`, `work.get_detail`, `storage.get_health`,
  `health.get_liveness`, `health.get_readiness`.
- **Scenario:** `SC07`, `SC09`, `SC12`, `SC13`, `SC17`, `SC21`, `SC23`, `SC26`, `SC29`, `SC30`,
  `SC31`, `SC39`, `SC40`, `SC41`, `SC49`.
- **Invariant:** `I01`, `I02`, `I03`, `I07`, `I08`, `I13`, `I17`.
- **Bên ngoài:** không. Đây là lý do giai đoạn này đi trước — nó **không phụ thuộc X, AI hay
  Telegram** và kiểm được hoàn toàn bằng fixture.
- **Bằng chứng:** **E1** (contract test trên 6 fixture `identity/neg-*`+`pos-*`) và **E2** (crash
  sau commit trước ACK; disk-full giữa ingest; hai worker claim cùng assignment).
- **Artefact:** log `pytest` đã che secret; dump `COUNT(*)` trước/sau replay; hash receipt; dump
  alias map; diff tập `saved_snapshot.content_hash` (phải rỗng); readiness response.
- **DoD:** bốn card đạt oracle §8 của chúng; `SC49` (quét default-deny 36 cạnh) xanh cho mọi cạnh
  chạm bốn module này; `EVM-*` cho mỗi card có kết quả thật.
- **Trần:** **`IMPLEMENTATION_VERIFIED`** cho bốn card.
- **Dừng nếu:** `CR-PC02-12` (diễn giải append-only của `TXN-checkpoint-only`) cần UPDATE tại chỗ;
  `CR-PC02-06` (kế thừa `first_announced` sau merge) chặn nhánh `I07`; `CR-PC10-08` (`owner_id`)
  chưa có card mang.
- **Ước lượng:** 12–18 ngày công. **Đây là đường găng.**

### Giai đoạn 2 — M0 probe (song song với) M2 paper connector

Hai nhánh độc lập, chạy song song được vì không chia sẻ module nào.

**2A — SP1 probe collector (M0)**

- **Cổng vào:** cổng Owner ở `contracts/ops/collector-probe.md` §6 — bốn xác nhận, **trước khi
  probe chạy**.
- **Card:** `TC-x-feasibility-probe`, rồi `TC-collector-checkpoint-resume`.
- **Bên ngoài — cần máy của Owner:** 5–10 đợt chạy thật trên X bằng Chrome profile riêng; ghi mỗi
  đợt theo §5 (số bài, số lần bị đòi xác minh, lý do dừng, giới hạn quan sát).
- **Bằng chứng:** **E3** — `evidence/runs/SP1-x-feasibility/` với biểu mẫu JSONL mỗi đợt, log đã
  che danh tính, manifest.
- **DoD:** go/no-go theo `collector-probe.md` §7 **nguyên văn, không nới**. `REQ-A1` và
  `REQ-S1.4-04` có số thật.
- **Trần:** **`LIVE_FEASIBILITY_VERIFIED`**, và **chỉ trong điều kiện đã ghi**. Không suy ra "X sẽ
  không bao giờ chặn", không suy ra collector đã hoạt động.
- **Dừng nếu:** bị chặn ⇒ **dừng và báo**. Mọi hành vi né CAPTCHA hay che giấu danh tính làm card
  FAIL ngay, bất kể kết quả thu được. No-go ⇒ báo blocked cho nguồn X; **không** tự chuyển sang X
  API trả phí.
- **Ước lượng:** 2–3 ngày công của Owner (rải trên nhiều ngày, vì cần nhiều đợt), 5–8 ngày công
  code cho `TC-collector-checkpoint-resume`.

**2B — Paper connector (M2)**

- **Chặn cứng bởi `REQ-A6`.** Cần đọc tài liệu chính thức và ghi lại **bốn dữ kiện** hiện là
  `PLACEHOLDER_KC = null`: nhịp gọi tối đa của arXiv; yêu cầu định danh (User-Agent / email liên
  hệ) của arXiv; hạn mức của OpenAlex; yêu cầu định danh của OpenAlex. Sàn thận trọng hiện tại
  `min_interval_ms = 3000` là **giả định**, không phải dữ kiện.
- **Operation:** `research.fetch_work_metadata`, `research.get_connector_health`.
- **Bằng chứng:** E1 bằng fixture; E3 khi gọi thật với nhịp đã ghi.
- **DoD:** bốn `null` được điền bằng dữ kiện đọc từ tài liệu; `contracts/retry-policy.yaml`
  `research_connector_rate_limit` hết `PLACEHOLDER_KC`; research connector đủ điều kiện
  `CONTRACT_READY`.
- **Dừng nếu:** không đọc được tài liệu ⇒ **không đoán một con số nào**.
- **Ước lượng:** 0.5 ngày đọc tài liệu + 5–8 ngày công code.

### Giai đoạn 3 — M3 nhãn và embedding

- **Cổng vào:** **`REQ-OQ03` phải được Owner trả lời.** Đây là mục duy nhất còn chặn một mốc.
- **Card:** `TC-analysis-adapter-validation` → `TC-analysis-once-per-generation` →
  `TC-embedding-generation-switch`.
- **Operation:** `analysis.enqueue_tasks`, `analysis.claim_task`, `analysis.get_task_input`,
  `analysis.heartbeat`, `analysis.submit_result`, `analysis.report_attempt_unknown`,
  `analysis.request_reanalysis`, `ai.run_inference_task`, `ai.probe_provider_capability`,
  `secret.issue_task_credential`, `secret.revoke_task_credential`,
  `embedding.generate_vectors`, `embedding.get_active_generation`,
  `embedding.start_generation_rebuild`, `embedding.activate_generation`.
- **Scenario:** `SC06`, `SC10`, `SC11`, `SC16`, `SC17`, `SC22`, `SC24`, `SC28`, `SC52`.
- **Invariant:** `I04`, `I11`, `I12`, `I14`, `I16`.
- **Bên ngoài:**
  1. **`REQ-OQ03`** — Owner chọn provider và model.
  2. **`REQ-A5`** — đọc điều khoản của **từng** nhà trước khi bật đường CLI/ACP cho nhà đó. Cổng
     dữ liệu đã có: `provider_config.enabled = true` đòi `terms_check_at IS NOT NULL`.
  3. **Probe CLI/ACP** theo `contracts/ops/cli-acp-probe.md` §3 — sáu nhóm `T-ISO`, `T-JSON`,
     `T-TIME`, `T-CONC`, `T-USAGE`, `T-TASK`.
  4. **Tập calibration và tập đánh giá tách rời** cho `REQ-A2`/`REQ-A3`; rubric khóa **trước** khi
     tuning (SRC-PLAN §14.2).
- **Bằng chứng:** E1 (9 fixture `ai/*`), E2 (canary secret, tool/network audit), **E3** (live
  capability run cho `REQ-AC16`), **E4** (groundedness review theo rubric `ai/grounding.md` §6).
- **DoD:** `AI_OUTPUT_INVALID` không bao giờ commit `valid`; đổi tag ⇒ **provider call counter
  delta = 0**; `usage` không biết ghi `unknown`, không ghi 0.
- **Trần:** `IMPLEMENTATION_VERIFIED` cho đường API. **Đường CLI/ACP dừng ở `CONTRACT_READY`** cho
  tới khi một probe đạt; `REQ-AC16` báo **BLOCKED**, không phải FAIL.
- **Dừng nếu:** không xác minh được cô lập của một provider ⇒ adapter đó **giữ nguyên
  `enabled=false`** (B13). Thiếu dữ liệu đánh giá ⇒ ghi "chưa đủ bằng chứng", **không chỉnh số để
  pass**.
- **Ước lượng:** 10–15 ngày công + thời gian chờ Owner.

### Giai đoạn 4 — M4 báo cáo và M5 hướng đang nổi

- **Cổng vào:** Giai đoạn 1 và 3 xong.
- **Card:** `TC-report-coverage-publish-cas` → `TC-backfill-pending-ledger` →
  `TC-ui-runs-three-states` ∥ `TC-ui-reports-detail`.
- **Operation:** `report.build`, `report.publish`, `report.list`, `report.get`,
  `tag.get_active_config_version`, `tag.freeze_config_version`, `tag.create`, `tag.update`,
  `tag.delete`, `tag.rescan_corpus`, `tag.preview_matches`, `run.list`, `run.get`, `run.run_now`,
  `run.resume`, `run.cancel`, `delivery.get_status`, `delivery.decide_unknown`.
- **Scenario:** `SC05`, `SC08`, `SC09`, `SC15`, `SC19`, `SC20`, `SC22`, `SC24`, `SC37`, `SC38`,
  `SC50`.
- **Invariant:** `I05`, `I06`, `I07`, `I12`, `I13`.
- **Bên ngoài:** không, trừ **render review** trên desktop và mobile (người thật xem).
- **Bằng chứng:** E1, **E2** (hai publisher đồng thời tranh CAS; builder crash không tiêu thụ
  backfill), E4 (render review).
- **DoD:** cửa sổ coverage **nối liền, không chồng, không hở** kể cả kỳ rỗng và kỳ sau crash; ba
  trạng thái rỗng/giới hạn/thất bại cho **ba chuỗi hiển thị khác nhau** (so chuỗi, không so ảnh);
  report đã publish không bị mutate.
- **Trần:** `IMPLEMENTATION_VERIFIED`; **`INTEGRATION_VERIFIED`** khi `SC50` (đường chạy thành công
  đầu-cuối) xanh.
- **Dừng nếu:** `CR-PC04-02` (`backfill_ledger` thiếu cột ép add–remove–readd) chưa đóng.
- **Ước lượng:** 15–20 ngày công (Python + TypeScript).

### Giai đoạn 5 — M6 Telegram

- **Cổng vào:** **`CR-PC07-04` phải đóng.** Cần đọc <https://core.telegram.org/bots/api#sendmessage>
  và ghi lại **năm dữ kiện**: độ dài tối đa một tin; độ dài callback data; parse mode và bảng
  escape của đúng chế độ đó; số nút mỗi hàng; rate limit gửi. `contracts/telegram/delivery.md` §3.4
  ghi thẳng: *"Cấm suy ra giới hạn từ trí nhớ."*
- **Card:** `TC-telegram-linking-auth` → `TC-saved-snapshot` → `TC-telegram-unknown-delivery`.
- **Operation:** `telegram.receive_update`, `telegram.execute_command`,
  `telegram.issue_link_code`, `telegram.consume_link_code`, `telegram.unlink`,
  `telegram.send_payload`, `delivery.create_intent`, `delivery.dispatch_next`,
  `delivery.record_receipt`, `delivery.mark_unknown`, `save.create`, `save.remove`, `save.list`.
- **Scenario:** `SC12`, `SC13`, `SC14`, `SC18`, `SC25`, `SC32`, `SC45`, `SC46`, `SC47`, `SC48`.
- **Invariant:** `I08`, `I09`, `I15`, `I17`.
- **Bên ngoài:** đọc tài liệu Bot API (dữ kiện mạng); tạo bot và webhook secret; một lần gửi thật
  để lấy E3.
- **Bằng chứng:** E1, **E2** (timeout sau điểm có thể đã gửi ⇒ `unknown`, **0** lần gửi lại tự
  động; multipart part 2 `unknown` không kéo theo resend), E3 (gửi thật).
- **DoD:** chat lạ ⇒ **outbound call count = 0**, 0 mutation, 0 reply; `TELEGRAM_PERMANENT_FAILURE`
  ⇒ hash report trong DB **không đổi**; `unknown` chỉ rời trạng thái qua `delivery.decide_unknown`
  của owner.
- **Trần:** `IMPLEMENTATION_VERIFIED`; `INTEGRATION_VERIFIED` sau E2 đầy đủ.
- **Dừng nếu:** năm dữ kiện định dạng chưa có ⇒ **không hiện thực nhánh multipart**. Chia tin theo
  số ký tự đoán là **cấm**.
- **Ước lượng:** 0.5 ngày đọc tài liệu + 10–14 ngày công.

### Giai đoạn 6 — M7 lịch chạy bù và M8 đóng gói, backup

- **Cổng vào:** Giai đoạn 1, 4, 5 xong.
- **Card:** `TC-scheduler-lease-claim` → `TC-backup-restore-drill`.
- **Operation:** `scheduler.evaluate_due`, `job.enqueue_scheduled_run`, `job.coalesce_overdue`,
  `worker.register_capabilities`, `worker.claim_assignment`, `worker.heartbeat`,
  `worker.report_stop`, `worker.release_assignment`, `worker.get_status`,
  `backup.create_snapshot`, `backup.verify_snapshot`, `backup.restore_snapshot`,
  `backup.reconcile_after_restore`.
- **Scenario:** `SC01`, `SC02`, `SC20`, `SC26`, `SC27`, `SC33`, `SC34`, `SC35`, `SC36`, `SC42`,
  `SC43`, `SC53`.
- **Invariant:** `I01`, `I10`, `I15`.
- **Bên ngoài:** **diễn tập restore thật** — cần Owner cho phép và một môi trường có khóa side
  effect. Đây là **khoảng cách lớn nhất còn lại của B11**: runbook là thiết kế, không phải bằng
  chứng.
- **Bằng chứng:** E1, **E2** (fake clock: ba kỳ offline ⇒ **đúng một** đợt bù; hai claimant ⇒
  `COUNT(assignment_lease active) = 1`; bản copy WAL-unsafe bị **từ chối**), **E3** (drill thật:
  sau restore, `COUNT(telegram outbound) = 0` cho tới khi đối soát xong).
- **DoD:** RPO 24 h và RTO 2 h đo được trên drill thật, không phải trên giấy;
  `saved_snapshot.content_hash` trước = sau restore.
- **Trần:** `INTEGRATION_VERIFIED`.
- **Dừng nếu:** `CR-PC08-05` (`restore_record` thiếu trường xác nhận Operator) chưa đóng;
  `CR-PC03-02` (không operation nào đưa run rời `blocked` ngoài `run.cancel`) chặn một nhánh.
- **Ước lượng:** 12–16 ngày công.

### Giai đoạn 7 — Chấp nhận sản phẩm

- **Cổng vào:** G6 đạt; hệ thống chạy thật.
- **Card:** không có. Đây là **quan sát**, không phải xây.
- **Bên ngoài:** **3–4 kỳ báo cáo thật** với dữ liệu thật. `REQ-A4` (mật độ phát hiện hướng nổi)
  không đánh giá được với ít hơn thế — hiện có **0 kỳ**.
- **Bằng chứng:** **E4** — review nội dung nhiều kỳ theo rubric đã khóa **trước** khi đo; tập đánh
  giá tách khỏi tập dò ngưỡng.
- **DoD:** `REQ-A2`, `REQ-A3`, `REQ-A4` có số thật; `REQ-OQ08` (ngưỡng tương đồng) và `REQ-OQ09`
  (model embedding) chốt bằng dữ liệu, không bằng phán đoán; `threshold_calibration_state` rời
  `uncalibrated`.
- **Trần:** **`PRODUCT_ACCEPTED`** — và chỉ **trong giới hạn đo đã công bố**.
- **Dừng nếu:** thiếu kỳ ⇒ ghi "chưa đủ bằng chứng". **Không chỉnh ngưỡng để pass** (SRC-PLAN
  §14.2).
- **Ước lượng:** 3–4 kỳ theo lịch thật + 3–5 ngày công đánh giá.

---

## 4. Công sức, đường găng, song song

**Giả định của ước lượng** — nếu sai thì con số sai theo:

1. Một người làm, quen Python và TypeScript, **không** quen Playwright hay Telegram Bot API.
2. Hợp đồng **không đổi** trong lúc code. Mỗi lần hợp đồng đổi, card `STALE` và phải pin lại.
3. Fixture dùng được ngay làm test data (đúng thiết kế, nhưng chưa ai thử).
4. Owner trả lời trong vòng vài ngày làm việc, không phải vài tuần.
5. **Không có** thời gian cho việc gỡ lỗi hạ tầng lạ (Docker, Chrome profile trên máy Owner).

| Giai đoạn | Ngày công | Ghi chú |
| --- | --- | --- |
| 0 — repo + CI | 3–5 | mở khóa G5 |
| 1 — M1 | **12–18** | đường găng |
| 2A — SP1 probe | 5–8 code + 2–3 Owner | song song với 2B |
| 2B — M2 connector | 5–8 | chặn bởi `REQ-A6` |
| 3 — M3 | 10–15 | chặn bởi `REQ-OQ03` |
| 4 — M4 + M5 | 15–20 | Python + TS |
| 5 — M6 Telegram | 10–14 | chặn bởi `CR-PC07-04` |
| 6 — M7 + M8 | 12–16 | gồm drill restore |
| 7 — chấp nhận | 3–5 + 3–4 kỳ | không rút ngắn được |
| **Tổng** | **≈75–109 ngày công** | chưa tính thời gian chờ Owner và chờ kỳ |

**Đường găng:** Giai đoạn 0 → 1 → 3 → 4 → 5 → 6 → 7. Giai đoạn 3 nằm trên đường găng **và** chặn
bởi một quyết định của Owner (`REQ-OQ03`) — đó là chỗ đáng rút ngắn nhất bằng cách hỏi sớm.

**Chạy song song được:**

- 2A (probe) ∥ 2B (connector) ∥ phần đầu của 1 — ba nhánh không chia sẻ module.
- Trong Giai đoạn 4, hai card UI ∥ hai card report, miễn là `web/src/lib/api.ts` được một card tạo
  trước rồi card sau mở rộng (`agent-tasks/README.md` §5.3).
- Việc **đọc dữ kiện bên ngoài** (Telegram, arXiv/OpenAlex, điều khoản AI) chạy song song với
  **mọi** giai đoạn và nên làm **sớm nhất có thể** — chúng rẻ, chặn nhiều, và không cần code.

---

## 5. Sổ rủi ro

| # | Rủi ro | Trigger quan sát được | Giảm thiểu | Chủ |
| --- | --- | --- | --- | --- |
| 1 | **X chặn tài khoản** dù người dùng tự giải CAPTCHA (`REQ-A7`) | `X_ACCESS_BLOCKED`; `challenge_count` tăng qua nhiều đợt | Điều kiện dừng rõ (`SC04`); **không** né, không đổi account, không proxy. No-go ⇒ báo blocked, không tự chuyển X API trả phí | Owner |
| 2 | **SP1 no-go** ⇒ nguồn X không dùng được | Tiêu chí §7 của `collector-probe.md` không đạt | Chạy SP1 **sớm** (Giai đoạn 2A, không đợi). Phần còn lại của hệ thống vẫn kiểm được bằng fixture | Coordinator |
| 3 | **Giới hạn định dạng Telegram** còn `KC` | Không có số cho độ dài tin | Đọc tài liệu — 0.5 ngày, rẻ nhất trong sổ này. Cho tới đó **không** hiện thực multipart | Owner |
| 4 | **`REQ-OQ03` hoãn lâu** ⇒ M3 đứng, kéo theo M4–M7 | Giai đoạn 3 không bắt đầu được | Hỏi sớm; nó nằm trên đường găng. Có thể làm Giai đoạn 2 trước để không phí thời gian | Owner |
| 5 | **Không adapter CLI/ACP nào qua probe** ⇒ `REQ-AC16` BLOCKED vĩnh viễn | `cli-acp-probe.md` §6 không đạt | Đường API vẫn chạy; `REQ-AC16` báo **BLOCKED**, không FAIL. Adapter không xác minh được cô lập **giữ `enabled=false`** | Coordinator |
| 6 | **Ngưỡng embedding không tách được tín hiệu** (`REQ-A2`) | Precision/recall không đạt trên tập đánh giá | Rubric khóa **trước** khi tuning; tập calibration tách tập đánh giá. Thiếu dữ liệu ⇒ `insufficient_evidence`, **không** gọi là "đang nổi" | Coordinator |
| 7 | **`REQ-A4` không đủ kỳ** ⇒ không kết luận được về hướng nổi | Sau M5 vẫn < 3 kỳ | Ghi "chưa đủ bằng chứng". **Không** chỉnh số để pass | Owner |
| 8 | **Drill restore chưa từng chạy** (B11) | Không có bản ghi drill | Đưa drill vào Giai đoạn 6 như DoD, không như "nice to have". RPO/RTO phải đo, không phải khai | Coordinator |
| 9 | **Hợp đồng đổi giữa lúc code** ⇒ card `STALE` hàng loạt | Hash §0 lệch | `INV-06`/`INV-09`; task đang chạy **giữ** baseline cũ, nhận baseline mới sau impact review (`change-control.md` §5) | Coordinator |
| 10 | **Code sinh ra bị sửa tay** ⇒ code và hợp đồng trôi khỏi nhau | Diff giữa file sinh và hợp đồng | E0 check "file sinh khớp hash hợp đồng"; quy tắc §2.3 | Coordinator |

Hai rủi ro **đã hết**, ghi lại để không ai lo lại: `data.purge_all` không động tới credential đăng
nhập (Owner không tự khóa mình ra ngoài), và dữ liệu đã purge **vẫn còn trong backup** cho tới khi
bản backup hết hạn — hành vi này nay đã chốt và hộp thoại xác nhận phải nói rõ.

---

## 6. Owner phải chạm tay vào đâu

| # | Việc | Khi nào | Mở khóa gì | Loại |
| --- | --- | --- | --- | --- |
| 1 | Ra lệnh bắt đầu coding | Sau G5 | Toàn bộ lộ trình | Quyết định |
| 2 | Bác hoặc chấp nhận ADR-0011 (framework) | Trước Giai đoạn 0 | Bố cục repo | Quyết định |
| 3 | **Trả lời `REQ-OQ03`** (provider + model) | Trước Giai đoạn 3 | **M3**, `MOD-settings-service` | Quyết định |
| 4 | Bốn xác nhận cổng probe (`collector-probe.md` §6) | Trước Giai đoạn 2A | SP1 chạy | Quyết định |
| 5 | **Chạy 5–10 đợt probe trên máy cá nhân** | Giai đoạn 2A | `REQ-A1`, `REQ-S1.4-04`, M0 | **Thao tác tay** |
| 6 | Đăng nhập X vào Chrome profile riêng của dự án | Giai đoạn 2A | Probe và collector | **Thao tác tay** |
| 7 | Đọc tài liệu Bot API, ghi năm giới hạn | Trước Giai đoạn 5 | `CR-PC07-04`, nhánh multipart | **Dữ kiện mạng** |
| 8 | Đọc tài liệu arXiv/OpenAlex, ghi bốn dữ kiện | Trước Giai đoạn 2B | `REQ-A6`, `CONTRACT_READY` của connector | **Dữ kiện mạng** |
| 9 | Đọc điều khoản **từng** nhà AI, đặt `terms_check_at` | Trước khi bật mỗi adapter CLI | `REQ-A5`, `REQ-AC16` | **Dữ kiện + quyết định** |
| 10 | Tạo bot Telegram và webhook secret | Giai đoạn 5 | M6 | **Thao tác tay** |
| 11 | Cho phép diễn tập restore | Giai đoạn 6 | B11, RPO/RTO thật | Quyết định |
| 12 | Đánh giá nội dung 3–4 kỳ | Giai đoạn 7 | `REQ-A4`, `PRODUCT_ACCEPTED` | **Thao tác tay** |
| 13 | **Vòng hỏi kế tiếp** — xem dưới | Bất cứ lúc nào | Nhiều tham số cấp gói | Quyết định |

**Vòng hỏi Owner kế tiếp** nên gom đúng hai nhóm (chi tiết ở `agent-tasks/README.md` và
`precode/README.md` §4.3):

1. **`CR-PC02-22`** — những con số Owner đã duyệt **theo gói** mà chưa từng nhìn thấy từng cái.
   Trình lại dưới dạng *"giá trị này ảnh hưởng điều gì bạn sẽ nhìn thấy"*, không phải bảng tham số.
2. **`PROV-PC03-01`…`-06`**, đặc biệt **`PROV-PC03-04`** (`analysis_unknown_attempt_auto_rerun = 1`)
   — chỗ chính PC03 tự ghi rằng họ diễn giải **khác** câu "không bao giờ tự chạy lại unknown" và
   **xin Auditor soi kỹ**. Nó khác hẳn `delivery.unknown`, vốn không bao giờ tự gửi lại.

---

## 7. Chứng minh tiến độ bằng gì

### 7.1 Evidence manifest cho mỗi card

Mỗi card sinh một manifest `EVM-<Task ID>` tại `evidence/runs/<Task ID>/manifest.json`, theo
`evidence/manifest.schema.json` và tám nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi
trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Bắt buộc: `spec_sha256`,
`contract_hashes` chép nguyên văn từ §0 của card, `review_type` (self hay independent), và **mọi
mục chưa chạy ghi `NOT_RUN`**.

### 7.2 Cập nhật cổng

Mỗi giai đoạn kết thúc thì `precode/gates.yaml` được cập nhật: `current_status`, `evidence_refs`,
và `met` của từng mục `G<n>-X<m>`. **Cổng chỉ được nâng bằng bằng chứng có manifest**, không bằng
tuyên bố. Giai đoạn 0 nâng `G5-X4`; Giai đoạn 4 và 6 là hai chỗ đầu tiên chạm G6.

### 7.3 Vòng audit mỗi lần freeze

Mỗi lần baseline được freeze lại (mọi lần hợp đồng đổi), Coordinator phát hành frozen candidate mới
và một vòng audit độc lập (`A2-R<n>`) chạy trước khi commit. Card được pin lại theo epoch mới; epoch
hiện hành **đọc từ chính card**, không chép tay:

```sh
sed -n 's/^\*\*Pin epoch: `\([A-Za-z0-9-]*\)`.*/\1/p' agent-tasks/TC-*.md | sort -u   # phải trả đúng 1 giá trị
```

### 7.4 Mẫu tuyên bố hoàn thành

Theo SRC-PLAN §14.3, mỗi claim gồm: claim + baseline (spec hash + contract version/hash +
implementation revision) + requirements covered + evidence manifest IDs + observed result +
**not established** + open issues + review type. Tự kiểm ghi `SELF_VALIDATION`. **Tuyệt đối không
viết "independent audit passed"** khi không có audit độc lập.

### 7.5 Điều kế hoạch này **không** thiết lập

- Không chứng minh 18 card là đủ để xây xong sản phẩm — chỉ chứng minh **12/12 mục phạm vi P0** có
  card đáng lẽ phải chứng minh chúng.
- Không chứng minh ước lượng công sức đúng. Chúng dựa trên năm giả định ở §4, và giả định thứ ba
  (fixture dùng được ngay làm test data) **chưa ai thử**.
- **Không chứng minh `contracts/http/openapi.yaml` hợp lệ theo OpenAPI 3.1.** Chưa validator nào
  chạy trên nó trong toàn bộ Pre-code. Vì nó là nguồn sinh model Pydantic và client TypeScript, một
  lỗi cấu trúc ở đó lan vào code của cả hai tầng — đó là lý do job `openapi` ở §2.4 chạy **trước**
  bước sinh code, chứ không sau.
- Không chứng minh bất kỳ dòng `KC` nào. Bảy trong mười lăm dòng cần mạng hoặc tài khoản thật;
  `REQ-A7` **không kiểm chứng được trước** bằng bất kỳ cách nào.
- Không thay thế `precode/README.md` (điểm vào baseline), `agent-tasks/README.md` (luật phát hành
  card) hay `precode/gates.yaml` (điều kiện cổng). Khi file này mâu thuẫn với chúng, **chúng
  thắng**.
