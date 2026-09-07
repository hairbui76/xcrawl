---
contract_id: CT-precode-readme
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs: [SRC-PLAN §1, SRC-PLAN §4, SRC-PLAN §11, SRC-PLAN §12, SRC-PLAN §14, SRC-PLAN §17, SRC-PLAN §18, SRC-SPEC §13]
requirement_refs: [REQ-OQ01, REQ-OQ02, REQ-OQ03]
decision_refs: [ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, ADR-0008, ADR-0009, ADR-0010]
invariant_refs: []
producers: []
consumers: []
dependencies:
  - precode/gates.yaml
  - precode/review.md
  - acceptance/scenarios.yaml
  - precode/baseline.json
  - precode/requirements.csv
  - precode/decision-register.md
  - precode/owner-decision-request.md
  - precode/change-control.md
  - agent-tasks/README.md
  - evidence/tools/e0_check.py
scope: >-
  Điểm vào của toàn bộ baseline Pre-code: baseline này là gì, trạng thái của nó, bản đồ thư mục theo bảng
  SRC-PLAN §4, cách chạy E0, nơi đọc quyết định còn chờ Owner, cách phát hành một task card, và những điều
  tuyệt đối không được làm.
verification: >-
  EV-PC10-05 (SELF_VALIDATION): kiểm mọi đường dẫn nêu trong bản đồ thư mục có tồn tại (hoặc được đánh dấu
  rõ là chưa tồn tại). PC10 KHÔNG chạy evidence/tools/e0_check.py — kết quả E0 là NOT_RUN với gói này.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Research Radar — Baseline Pre-code

> **Trạng thái: `NOT_READY_FOR_PRODUCT_CODE`. Claim tối đa của mọi file trong baseline này:
> `DRAFT_FOR_REVIEW`.**
>
> Chưa có hợp đồng nào được tuyên bố `accepted`. Chưa có bằng chứng E1–E4. Chưa chạy collector, chưa gọi
> provider AI, chưa gửi Telegram. Không được bắt đầu viết product code.

## 1. Baseline này là gì

Đây là kết quả của giai đoạn Pre-code trong `research-radar-pre-code-plan.md`: một bộ hợp đồng có thể kiểm
toán được, đủ chi tiết để một agent nhận việc mà **không phải đoán** về giao tiếp, trạng thái, transaction
hay điều kiện lỗi.

Nó **không** phải là code, không phải thiết kế chi tiết cho một framework, và không phải lời khẳng định rằng
sản phẩm sẽ hoạt động. SRC-PLAN §18 nói rõ kết quả đầu tiên cần có là *"một baseline yêu cầu có thể truy vết
và một danh sách quyết định chặn được diễn đạt đủ cụ thể để chấp nhận hoặc bác bỏ"*.

**Nguồn bất biến.** Hai file dưới đây là nguồn duy nhất; bản đã pin nằm ở `precode/source/`:

| Ref | File | SHA-256 | Bytes |
| --- | --- | --- | --- |
| SRC-SPEC | `research-radar-spec.md` = `precode/source/spec-v0.2.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| SRC-PLAN | `research-radar-pre-code-plan.md` = `precode/source/pre-code-plan-v0.1.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

`project-overview.md` và `master-interview-prompt.md` là **bối cảnh lịch sử**. SRC-PLAN §1 cấm dùng bản
overview cũ để mở lại quyết định mới hơn.

## 2. Bản đồ thư mục theo SRC-PLAN §4

| Nhóm (SRC-PLAN §4) | File thực tế | Trạng thái |
| --- | --- | --- |
| Baseline | `precode/README.md` (file này), `precode/baseline.json`, `precode/source/spec-v0.2.md`, `precode/source/pre-code-plan-v0.1.md` | có |
| Yêu cầu | `precode/requirements.csv`, `precode/decision-register.md`, `precode/adr/` (ADR-0001…ADR-0010 + README) | có |
| Quyền giao tiếp | `contracts/modules.yaml`, `contracts/capabilities.yaml` | có |
| API | `contracts/http/openapi.yaml`, `contracts/ports.yaml` (85 operation) | có |
| Payload | `contracts/schemas/` — `ingest-batch`, `ingest-receipt`, `target`, `worker-assignment`, `analysis-result`, `report`, `saved-snapshot` | có |
| Trạng thái | `contracts/state/run.yaml`, `analysis.yaml`, `report.yaml`, `delivery.yaml`, `storage.yaml` | có |
| Lỗi | `contracts/errors.yaml` (28 mã), `contracts/retry-policy.yaml` | có |
| Dữ liệu | `contracts/data/entities.yaml`, `contracts/data/invariants.md`, `contracts/data/identity.md` | có |
| Thời gian | `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md` | có |
| AI | `contracts/ai/tasks.yaml`, `contracts/ai/providers.yaml`, `contracts/ai/grounding.md` | có |
| UI/Telegram | `contracts/ui/screens.yaml`, `contracts/telegram/commands.yaml`, `contracts/telegram/delivery.md` | có |
| Vận hành | `contracts/ops/deployment.md`, `secrets.md`, `backup-restore.md`, `internet-boundary.md`, `collector-probe.md`, `cli-acp-probe.md` | có |
| Fixture và scenario | `acceptance/fixtures/` — **9 nhóm**: `ai/`, `boundary/`, `collection/`, `e2e/`, `identity/`, `recovery/`, `reporting/`, `telegram/`, `ui/` · `acceptance/scenarios.yaml` (SC01–SC53) · `acceptance/traceability.csv` | **có đủ**. Ba nhóm mới ở FIX5: `boundary/` (SC49, quét default-deny 36 cạnh), `e2e/` (SC50, đường chạy thành công đầu-cuối), `ui/` (SC10 render app↔Telegram, SC51 thiết lập lần đầu) |
| Giao việc | `agent-tasks/README.md`, `agent-tasks/TEMPLATE.md`, `agent-tasks/WALKTHROUGH.md`, 18 card `TC-*.md` | có |
| Bằng chứng | `evidence/handoffs/` (PC00–PC10) · `evidence/tools/e0_check.py` · `evidence/manifest.schema.json` · `evidence/index.json` · `evidence/runs/` | **có đủ**; `evidence/runs/` chứa kết quả E0 thật của PC09 |
| Cổng kiểm tra | `precode/change-control.md` · `precode/gates.yaml` (G0–G7, SP1, và `INV-01`…`INV-10`) · `precode/review.md` | **có đủ** |
| Hồ sơ audit và điều phối | `evidence/audits/` (7 AUDIT_REPORT của `auditor-A1`/`auditor-A2` + 7 FROZEN_CANDIDATE manifest) · `evidence/coordination/` (baseline điều phối, packet PC00–PC10 và packet audit, các ruling, `coordinator-ledger.md`) | **có đủ**; bản sao nguyên văn, ra đời **sau** freeze `FC-W4` epoch 7 nên không nằm trong candidate manifest nào đã được audit (`protocol.md` §6) |

Danh sách hash đầy đủ nằm ở `precode/baseline.json`.

## 3. Chạy E0

E0 là mức bằng chứng thấp nhất trong SRC-PLAN §14.2: **lint schema/reference/traceability**. Nó chứng minh bộ
hợp đồng tự nhất quán ở phần đã kiểm — và **không** chứng minh code hoạt động.

Tool: `evidence/tools/e0_check.py` (do PC09 tạo).

```sh
# chạy từ thư mục scratch, KHÔNG chạy từ trong repo (tránh sinh file ngoài scope)
PYTHONDONTWRITEBYTECODE=1 python3 /mnt/virtual/repo/xcrawl/evidence/tools/e0_check.py \
    --repo /mnt/virtual/repo/xcrawl \
    --json-out /tmp/<scratch>/e0-report.json
```

- Exit `0` nếu không check nào `FAIL`; `1` nếu có; `2` nếu tool lỗi.
- Cần `python3` + PyYAML + jsonschema.
- `--only <prefix,...>` chạy một tập con.

**Kết quả E0 hiện tại: `NOT_RUN` đối với gói PC10.** PC10 không chạy tool này. Kết quả E0 chính thức thuộc
PC09: xem `evidence/runs/` (run gần nhất tại thời điểm viết: `E0-20260906T193716Z`), `evidence/index.json` và
`precode/review.md`. Đừng suy ra "E0 pass" từ việc file tool tồn tại, và đừng suy ra nó từ file này — đọc
chính bản ghi run.

## 4. Quyết định còn chờ Owner

| Cần gì | Đọc ở đâu |
| --- | --- |
| Danh sách quyết định trình Owner, kèm khuyến nghị và hệ quả | `precode/owner-decision-request.md` |
| B01–B17, amendment, và trạng thái từng quyết định | `precode/decision-register.md` |
| Lý do và phương án của từng quyết định kiến trúc | `precode/adr/README.md` + `precode/adr/ADR-000*.md` |

**Không có blocker nào được đóng.** B01–B17 ở trạng thái `PROVISIONAL`: mỗi cái đã có một phương án làm việc
tạm theo khuyến nghị của SRC-PLAN, nhưng phê chuẩn là của Owner. Không file nào trong baseline được ghi
`CLOSED` hay `ACCEPTED` cho chúng.

**Ba điểm không có mặc định an toàn** (`OWNER_DECISION_REQUIRED`):

1. **REQ-OQ02 — chọn stack.** ADR-0006 ghi Option A (Python toàn bộ) là PROVISIONAL, dùng **duy nhất** để
   viết đường dẫn/lệnh trong task card. Chặn M1.
2. **REQ-OQ03 — provider và model cụ thể.** Không có mặc định; phụ thuộc tài khoản và điều khoản của Owner.
   Chặn M3.
3. **Phạm vi loại trừ của `data.purge_all`.** Cụm "toàn bộ dữ liệu" không có nghĩa an toàn suy ra được
   (`PROV-PC00-01`).

Thêm vào đó, **REQ-OQ01 (xác nhận D09 — Chrome profile riêng của dự án) chặn M0** và chặn cả SP1.

## 5. Đọc gates và review

- `precode/gates.yaml` — điều kiện pass/fail của G0…G7 và SP1, cộng `invalidation_rules` `INV-01`…`INV-10`
  (quy tắc "thay đổi nào làm bằng chứng nào hết hiệu lực"). Đây là **nguồn chuẩn duy nhất** của các quy tắc
  đó; `precode/change-control.md` §4 chỉ dẫn chúng, không định nghĩa lại.
- `precode/review.md` — báo cáo audit, module nào READY / BLOCKED, và trạng thái các wave FIX.
- `acceptance/traceability.csv` — truy vết REQ ↔ contract ↔ scenario ↔ loại bằng chứng.
- SRC-PLAN §12 (bảng cổng) và §17 (Definition of Ready) vẫn là chuẩn đọc ở mức nguồn.

**Tổng quan cổng** (SRC-PLAN §12): G0 baseline → G1 boundaries → G2 data/workflow → G3 domain contracts →
G4 auditable baseline → **G5 task ready** → G6 integration/live → G7 product acceptance. `SP1` (probe khả thi
X) là nhánh riêng, nên chạy sớm sau G2/PC05 vì đó là rủi ro nguồn lớn nhất.

## 6. Phát hành một task card

Đọc `agent-tasks/README.md` §1. Tóm tắt:

1. Owner ra lệnh bắt đầu (sau G5).
2. Coordinator chọn card, **kiểm lại toàn bộ hash ở §0 của card**, phát TASK_PACKET với lease exclusive.
3. Worker — vai duy nhất ghi file — làm đúng write set §3.
4. Auditor review theo §12 nếu `audit_route: INDEPENDENT_REQUIRED`.
5. Worker viết handoff; Coordinator xác minh và phát hành frozen candidate.

Mẫu card: `agent-tasks/TEMPLATE.md` (14 mục bắt buộc). Kiểm chứng card có đủ thông tin không:
`agent-tasks/WALKTHROUGH.md`.

**Pin hiện tại: `PC10-PIN-FCW4f-20260907`.**

> **Đừng tin dòng trên — kiểm nó.** Nguồn chuẩn của tên epoch là **chính các card**, không phải file này
> (finding `F-A2R1-03`: trước đây file này chép tay tên epoch và bị bỏ lại sau một lần pin lại). Đọc tên
> epoch hiện hành bằng một lệnh:
>
> ```sh
> grep -ho 'Pin epoch: `PC10-PIN-[A-Za-z0-9-]*`' agent-tasks/TC-*.md | sort -u
> ```
>
> Kết quả phải là **đúng một** dòng, và phải khớp tên ở trên. Lệch ⇒ file này stale, tin card.
> `evidence/tools/e0_check.py` và EV-PC10-01 đều kiểm ràng buộc này; xem `agent-tasks/README.md` §4.

Epoch cũ, theo thứ tự bị thay: `PC10-PIN-FCW4e-20260907` ← `PC10-PIN-FCW4d-20260907` ←
`PC10-PIN-FCW4c-20260907` ← `PC10-PIN-FCW4b-20260907` ← `PC10-PIN-FCW4-20260907` ← `PC10-PIN-20260907`.

Sáu file của PC09 cộng `evidence/tools/e0_check.py` **cố ý không được pin hash** vì PC09-FIX1 chạy song song;
chúng được dẫn bằng đường dẫn + SC id, và agent phải đọc bản mới nhất trước khi bắt đầu. Chi tiết ở
`agent-tasks/README.md` §4 và các ADDENDUM `PKT-PC10-FIX1`…`-FIX6` của
`evidence/handoffs/PC10-handoff.md`.

## 7. Những điều tuyệt đối không được làm

1. **Không sửa nguồn.** `research-radar-spec.md` và `research-radar-pre-code-plan.md` bất biến. Đổi câu chữ
   đã cam kết ⇒ tạo `AMD-B<nn>` trong `decision-register.md`.
2. **Không đóng blocker khi Owner chưa trả lời.** Không ghi `CLOSED`/`ACCEPTED`/`XN` cho B01–B17.
3. **Không bắt đầu coding trước G5 và trước khi Owner ra lệnh.** SRC-PLAN §11 PC10: *"Chưa tự chạy coding vì
   có task card."*
4. **Không sửa fixture, oracle hay test expectation để implementation pass.** Phát hiện hợp đồng sai ⇒ change
   request có bằng chứng (`precode/change-control.md`).
5. **Không thêm cạnh giao tiếp ngoài `contracts/modules.yaml`.** Default deny.
6. **Không bịa bằng chứng.** Chưa chạy ⇒ `NOT_RUN`. Tự kiểm ⇒ `SELF_VALIDATION`. Tuyệt đối không viết
   "independent audit passed".
7. **Không đoán dữ kiện bên ngoài.** Giới hạn định dạng Telegram, nhịp gọi arXiv/OpenAlex, điều khoản nhà
   cung cấp AI đều đang ở `KC` vì phiên Pre-code không có mạng. `contracts/telegram/delivery.md` §3.4:
   *"Cấm suy ra giới hạn từ trí nhớ."*
8. **Không thêm cơ chế né CAPTCHA hay che giấu danh tính.** SRC-SPEC §13.2 — không thương lượng. Bị chặn thì
   dừng và báo.
9. **Không cập nhật hash trong card của một task đang chạy.** Baseline mới đi qua impact review
   (`change-control.md` §5).

## 8. Rủi ro còn mở lớn nhất

Bốn điểm dưới đây xuất hiện như stop condition tường minh trên các card liên quan. Chúng **không** sửa được
bằng cách viết thêm hợp đồng.

| Rủi ro | Trạng thái | Chặn gì |
| --- | --- | --- |
| Probe khả thi X (SP1) chưa chạy; REQ-OQ01/D09 chưa được Owner xác nhận | `NOT_RUN` + `OWNER_DECISION_REQUIRED` | M0; mọi khẳng định live của collector; AC-01, AC-04 ở mức E3 |
| Nhịp gọi và yêu cầu định danh của arXiv/OpenAlex | `KC` — SRC-SPEC không chứa URL tài liệu (`CR-PC05-03`) | `CONTRACT_READY` của research connector |
| Giới hạn định dạng Telegram (độ dài tin, callback data, parse mode, escape, rate limit) | `KC` (`CR-PC07-04`) | nhánh multipart của delivery; một phần AC-14 |
| Chưa adapter CLI/ACP nào được probe | `BLOCKED` (`CR-PC06-04`) | AC-16 báo **BLOCKED**, không phải FAIL; đường CLI/ACP dừng ở `CONTRACT_READY`. Cổng dữ liệu: `provider_config.enabled = true` đòi `terms_check_at IS NOT NULL` (`CR-PC07-07`) |

Ngoài ra: **chưa validator OpenAPI 3.1 nào được chạy** trên `contracts/http/openapi.yaml` trong phiên
Pre-code; và phạm vi loại trừ của `data.purge_all` vẫn `OWNER_DECISION_REQUIRED`.

## 9. Bảo mật — chốt hiện tại

| Đối tượng | Scheme |
| --- | --- |
| Owner, mutation | `ownerSessionCookie` **AND** `ownerCsrfToken` trong một security requirement — cookie một mình **không** đủ |
| Owner, read-only | `ownerSessionCookie` một mình |
| Collector | bearer `collectorToken` — chỉ `worker.*` và `ingest.*` |
| Analysis worker | bearer `analysisWorkerToken` — chỉ `analysis.*` và `secret.issue_task_credential` |
| Telegram ingress | header `X-Telegram-Bot-Api-Secret-Token`; biết chat ID **không** phải là quyền |
| Backup | bearer `backupOperatorToken` — scheme **duy nhất** cho mọi route `backup.*` |

Secret không bao giờ vào repo (SRC-SPEC §11.2).
