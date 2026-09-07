---
contract_id: CT-tasks-index
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs: [SRC-PLAN §4, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15, SRC-PLAN §16, SRC-SPEC §13]
requirement_refs: [REQ-OQ01, REQ-OQ02, REQ-OQ03]
decision_refs: [ADR-0006, "baseline §5 hàng Stack (PROVISIONAL)"]
invariant_refs: []
producers: []
consumers: []
dependencies:
  - agent-tasks/TEMPLATE.md
  - precode/change-control.md
  - precode/gates.yaml
  - acceptance/scenarios.yaml
scope: >-
  Chỉ mục và luật vận hành của thư mục agent-tasks/: card được phát hành thế nào, xếp theo milestone và
  cổng ra sao, phụ thuộc nhau thế nào, và khi nào một card trở thành STALE.
verification: >-
  EV-PC10-01/02 (SELF_VALIDATION): script kiểm hash, operation ID, SC ID và đủ 14 mục của TEMPLATE trên
  mọi card. E0 lint của PC09 chưa chạy — NOT_RUN.
claim_ceiling: DRAFT_FOR_REVIEW
---

# agent-tasks/ — Giao việc cho agent coding

> **Chưa có card nào được phép thi hành.** Toàn bộ thư mục này ở trạng thái `DRAFT_FOR_REVIEW`. Coding chỉ
> bắt đầu sau khi **G5 pass** và **Owner ra lệnh bắt đầu** (SRC-PLAN §12: *"Bắt đầu coding phạm vi được giao
> khi user yêu cầu"*). SRC-PLAN §11 PC10 nói thẳng: *"Chưa tự chạy coding vì có task card."*

## 1. Card được phát hành thế nào

Không có agent nào tự nhận việc. Đường đi hợp lệ duy nhất:

1. **Owner** ra lệnh bắt đầu một phạm vi (sau G5).
2. **Coordinator** chọn card, kiểm lại toàn bộ hash ở §0 của card, rồi phát `TASK_PACKET` gắn card đó
   (`agent_profile/protocol.md`): `packet_id`, `authority_id`, `lease_id` exclusive với fencing,
   `expires_at`, `enforcement_mode`, `audit_route`, `completion_ceiling`.
3. **Worker** — vai duy nhất được ghi file — làm đúng write set §3 của card, không hơn.
4. **Auditor** (nếu `audit_route: INDEPENDENT_REQUIRED`) review theo §12 của card. Người xây được tự kiểm,
   nhưng phải ghi rõ đó là `SELF_VALIDATION` (SRC-PLAN §11).
5. **Worker** viết HANDOFF; Coordinator xác minh và phát hành frozen candidate. Worker **không** tự freeze.

Card là *nội dung* của packet, không thay packet. Card nói **làm gì và không được làm gì**; packet nói
**ai, khi nào, với lease nào**.

## 2. Thứ tự theo milestone và cổng

Milestone lấy từ SRC-SPEC §13 (xếp theo phụ thuộc và mức độ rủi ro, **không** theo mức độ dễ). Cổng lấy từ
SRC-PLAN §12.

| Thứ tự | Card | Milestone | Cổng | Claim tối đa |
| --- | --- | --- | --- | --- |
| 0 | [`TC-x-feasibility-probe`](TC-x-feasibility-probe.md) | M0 | **SP1** | `LIVE_FEASIBILITY_VERIFIED` |
| 1 | [`TC-owner-auth-session`](TC-owner-auth-session.md) | M1 | G5 | `IMPLEMENTATION_VERIFIED` |
| 2 | [`TC-ingest-idempotent-ack-lost`](TC-ingest-idempotent-ack-lost.md) | M1 | G5 | `IMPLEMENTATION_VERIFIED` |
| 3 | [`TC-storage-write-blocked-readiness`](TC-storage-write-blocked-readiness.md) | M1 → M8 | G5 | `IMPLEMENTATION_VERIFIED` |
| 4 | [`TC-collector-checkpoint-resume`](TC-collector-checkpoint-resume.md) | M0 → M1 | G5 (live cần SP1) | `IMPLEMENTATION_VERIFIED` |
| 5 | [`TC-canonical-identity-merge`](TC-canonical-identity-merge.md) | M2 | G5 | `IMPLEMENTATION_VERIFIED` |
| 6 | [`TC-analysis-adapter-validation`](TC-analysis-adapter-validation.md) | M3 | G5 | `IMPLEMENTATION_VERIFIED` (đường CLI/ACP dừng ở `CONTRACT_READY`) |
| 7 | [`TC-analysis-once-per-generation`](TC-analysis-once-per-generation.md) | M3 | G5 | `IMPLEMENTATION_VERIFIED` |
| 8 | [`TC-embedding-generation-switch`](TC-embedding-generation-switch.md) | M3 → M5 | G5 | `IMPLEMENTATION_VERIFIED` |
| 9 | [`TC-report-coverage-publish-cas`](TC-report-coverage-publish-cas.md) | M4 | G5 | `IMPLEMENTATION_VERIFIED` |
| 10 | [`TC-backfill-pending-ledger`](TC-backfill-pending-ledger.md) | M4 | G5 | `IMPLEMENTATION_VERIFIED` |
| 11 | [`TC-ui-reports-detail`](TC-ui-reports-detail.md) | M4 | G5 | `IMPLEMENTATION_VERIFIED` |
| 12 | [`TC-saved-snapshot`](TC-saved-snapshot.md) | M1 → M6 | G5 | `IMPLEMENTATION_VERIFIED` |
| 13 | [`TC-telegram-linking-auth`](TC-telegram-linking-auth.md) | M6 | G5 | `IMPLEMENTATION_VERIFIED` |
| 14 | [`TC-telegram-unknown-delivery`](TC-telegram-unknown-delivery.md) | M6 | G5 | `IMPLEMENTATION_VERIFIED` |
| 15 | [`TC-scheduler-lease-claim`](TC-scheduler-lease-claim.md) | M7 | G5 | `IMPLEMENTATION_VERIFIED` |
| 16 | [`TC-ui-runs-three-states`](TC-ui-runs-three-states.md) | M4 → M7 | G5 | `IMPLEMENTATION_VERIFIED` |
| 17 | [`TC-backup-restore-drill`](TC-backup-restore-drill.md) | M8 | G5 | `IMPLEMENTATION_VERIFIED` |

**SP1 chạy sớm.** SRC-PLAN §12: *"SP1 cho X nên chạy sớm sau G2 và PC05, vì rủi ro nguồn lớn nhất."*
`TC-x-feasibility-probe` đứng số 0 không phải vì dễ mà vì nếu nó no-go thì phần lớn phần còn lại đổi nghĩa.
Nhưng nó **không** chặn việc soạn hợp đồng, và nó có cổng riêng của Owner (`contracts/ops/collector-probe.md` §6).

## 3. Đồ thị phụ thuộc

```
TC-x-feasibility-probe ──(chỉ chặn claim live)──► TC-collector-checkpoint-resume
                                                          │
TC-owner-auth-session ──► (mọi card có auth_scope owner_session)
        │
        ├─► TC-scheduler-lease-claim ──► TC-collector-checkpoint-resume
        │            │
        │            └─► TC-ui-runs-three-states
        │
TC-ingest-idempotent-ack-lost ──► TC-canonical-identity-merge ──► TC-report-coverage-publish-cas
        │                                    │                              │
        │                                    └─► TC-saved-snapshot          ├─► TC-backfill-pending-ledger
        │                                                │                  ├─► TC-ui-reports-detail
        │                                                │                  └─► TC-telegram-unknown-delivery
        ├─► TC-analysis-once-per-generation ◄── TC-analysis-adapter-validation
        │            │
        │            └─► TC-ui-reports-detail
        │
        └─► TC-embedding-generation-switch ──► TC-report-coverage-publish-cas

TC-storage-write-blocked-readiness ◄──► TC-backup-restore-drill ──► TC-telegram-unknown-delivery (I15)

TC-telegram-linking-auth ──► TC-telegram-unknown-delivery
                        └──► TC-saved-snapshot (đường Save từ chat)
```

Đọc mũi tên là "phải xong trước". Một số phụ thuộc chỉ chặn **claim đầy đủ** chứ không chặn bắt đầu; §11
của từng card nói rõ cái nào là cái nào.

## 4. Card pin baseline và đi STALE khi hợp đồng đổi

Mỗi card mang §0 với SHA-256 và byte count của **mọi** file nó đọc. Đó không phải trang trí:

- Trước khi ghi dòng code đầu tiên, agent chạy lại `sha256sum` trên toàn bộ §0.
- **Lệch một dòng ⇒ card `STALE`.** Agent dừng, báo Coordinator, và chờ card được pin lại. Không tự cập nhật
  hash trong card của mình.
- SRC-PLAN §16: *"Spec mới không tự thay baseline của task đang chạy; task nhận baseline mới sau impact
  review. Bản cũ vẫn giữ để audit."*
- Ma trận vô hiệu hóa bằng chứng (thay đổi nào làm STALE bằng chứng nào) nằm ở `precode/change-control.md` §4.

**Pin hiện tại: `PC10-PIN-OD01c-20260907`.** Hash tính lại trực tiếp trên repo sau mỗi wave FIX chạm file có
pin. Epoch cũ, theo thứ tự bị thay: `PC10-PIN-OD01b-20260907` ←
`PC10-PIN-OD01-20260907` ← `PC10-PIN-FCW4f-20260907` ← `PC10-PIN-FCW4e-20260907` ← `PC10-PIN-FCW4d-20260907` ← `PC10-PIN-FCW4c-20260907` ← `PC10-PIN-FCW4b-20260907` ← `PC10-PIN-FCW4-20260907` ← `PC10-PIN-20260907`.

**Tên epoch được đọc từ card, không chép tay.** Finding `F-A2R1-03` cho thấy vì sao: hai file `precode/` từng
khẳng định một epoch đã bị thay, và một trong hai nằm ngay dưới tiêu đề "Pin hiện tại" — người đọc đi kiểm
card theo epoch đó sẽ hoặc không tìm thấy, hoặc kiểm nhầm vào byte đã cũ, đúng loại stale mà cơ chế pin sinh
ra để bắt. Kiểm bằng:

```sh
grep -ho 'Pin epoch: `PC10-PIN-[A-Za-z0-9-]*`' agent-tasks/TC-*.md | sort -u   # phải ra đúng 1 dòng
grep -ro 'PC10-PIN-[A-Za-z0-9-]*' agent-tasks precode | sort -u                 # đối chiếu mọi nơi khác
```

EV-PC10-01 có phép kiểm **(k)** làm đúng việc này bằng máy: nó lấy epoch từ §0 của 18 card (phải đồng thuận
đúng một giá trị), rồi bắt buộc `precode/README.md`, `agent-tasks/README.md`, `TEMPLATE.md` và
`WALKTHROUGH.md` phải nêu đúng epoch đó; một epoch cũ chỉ được xuất hiện khi trên cùng dòng có dấu hiệu kể
lịch sử ("thay", "trước đó", "epoch cũ", "gốc", "ví dụ"). Một quy tắc không được máy kiểm thì sẽ trôi — nó đã
trôi một lần rồi.

**Ngoại lệ có chủ đích:** sáu file của PC09 — `acceptance/scenarios.yaml`, `acceptance/traceability.csv`,
`precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json` — cùng
`evidence/tools/e0_check.py` **không được pin hash**, vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được
dẫn bằng **đường dẫn + SC id**. Agent phải đọc bản mới nhất của chúng ngay trước khi bắt đầu. Quy tắc STALE
của §4 vì vậy **không** áp dụng cho bảy file đó — nhưng `INV-06` và `INV-09` trong `precode/gates.yaml` vẫn áp
dụng cho mọi file có pin.

Bằng chứng vô hiệu hóa: card dùng thẳng `INV-01`…`INV-10` của `precode/gates.yaml`; `precode/change-control.md`
§4 dẫn chúng chứ không định nghĩa lại.

## 5. Luật chia card

- Một card = **một deliverable kiểm được độc lập** (SRC-PLAN §11 PC10). Không có card "làm toàn bộ backend"
  hay "làm toàn bộ UI" — SRC-PLAN §15 gọi thẳng đó là phản mẫu.
- Card đặt tên theo **hành vi phải chứng minh**, không theo tên file hay tên lớp: `ingest idempotent khi mất
  ACK`, chứ không phải `viết module ingest`.
- Một card không được sở hữu hai transaction ở hai module khác nhau. Nếu phải, tách card.
- Card UI tách theo màn hình + read model, không theo "làm giao diện".

## 5.1 Ngoại lệ loại bản ghi: front-matter của card

Ruling của Coordinator trên PC10-handoff §6.4 (FIX1): **card `TC-*.md` là một loại bản ghi riêng và không mang
contract header của baseline §3.** Card không phải hợp đồng — nó là lệnh giao việc *pin* một hợp đồng, nên
`producers` / `consumers` / `dependencies` của baseline §3 không có nghĩa với nó; thông tin tương đương nằm ở
§4 (consumes/produces), §5 (allowed communication) và §11 (dependencies).

Front-matter bắt buộc của một card, đúng 12 khóa:

```yaml
card_id: TC-<kebab>
title_vi: <tiêu đề>
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: <M0..M8>
gate: <G5 | SP1>
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: <nhãn SRC-PLAN §2>
owner_modules: [MOD-...]
scenario_refs: [SC...]
invariant_refs: [I...]
evidence_manifest_id: EVM-<Task ID>
source_refs: [...]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
```

Bốn file khung của thư mục này — `README.md`, `TEMPLATE.md`, `WALKTHROUGH.md` — **có** mang contract header
đầy đủ của baseline §3. Ngoại lệ chỉ áp dụng cho card.

**Nhãn `claim_ceiling` chỉ được lấy từ SRC-PLAN §2**: `DRAFT_FOR_REVIEW`, `CONTRACT_READY`,
`IMPLEMENTATION_VERIFIED`, `INTEGRATION_VERIFIED`, `LIVE_FEASIBILITY_VERIFIED`, `PRODUCT_ACCEPTED`. Không tự
đặt nhãn mới. Ba ID space do PC10 đưa vào đã được Coordinator chấp nhận: `EVM-<Task ID>` (evidence manifest),
`SG-<nn>` (stop condition trong card), `PC10-PIN-<epoch>` (pin epoch).

## 5.3 Layout hai ngôn ngữ — Stack B (ACCEPTED)

Owner chốt **Option B** ngày 2026-09-07 (`OD-20260907-01` mục 3; ADR-0006 nay `accepted`). Phân chia ngôn
ngữ là **ACCEPTED**; đường dẫn cụ thể vẫn `PROVISIONAL` cho tới khi có repo triển khai; **framework chưa
được chốt** — ADR-0006 cố ý không nêu tên, nên card nào cần chọn framework phải DỪNG và raise CR.

```
server/     Python   backend, domain services, scheduler, report, delivery, auth, storage
collector/  Python   collector chạy trên máy cá nhân (Playwright Python, Chrome profile riêng — D09)
worker/     Python   analysis worker + AI adapter trên máy cá nhân
probe/      Python   kịch bản probe SP1 (M0), đầu ra là bằng chứng
tests/      Python   tests/contract/… và tests/integration/… cho toàn bộ cây Python
web/        TypeScript
  web/src/lib/       api.ts (client sinh từ contracts/http/openapi.yaml), kiểu dùng chung
  web/src/routes/    read model cho từng SCR-*
  web/src/views/     component hiển thị
  web/tests/contract/      *.test.ts
  web/tests/integration/   *.test.ts
```

Quy tắc bắt buộc:

- **Không file `.py` nào dưới `web/`; không file `.ts`/`.tsx` nào dưới `server/`, `collector/`, `worker/`,
  `probe/`.** EV-PC10-01 phép kiểm **(m)** ép điều này bằng máy trên §3 của mọi card.
- Ranh giới giữa hai ngôn ngữ là **HTTP API đã có hợp đồng** (`contracts/http/openapi.yaml`). Web app
  TypeScript là một consumer của owner API; nó **không** chia sẻ tiến trình hay module với phần Python, nên
  ngôn ngữ thứ hai **không** tạo thêm cạnh quyền nào ngoài những cạnh đã có trong `contracts/modules.yaml`.
- `web/src/lib/api.ts` là nơi duy nhất giữ **nửa trình duyệt của CSRF**: đọc cookie `rr_csrf` và gắn header
  `X-CSRF-Token` cho mọi mutation. Card `TC-owner-auth-session` sở hữu nửa server; nó **không** ghi vào
  `web/`.
- Hai card UI (`TC-ui-runs-three-states`, `TC-ui-reports-detail`) cùng dùng `web/src/lib/api.ts`. Card nào
  chạy trước tạo file; card sau **mở rộng**, không viết lại.
- Đổi layout chỉ sửa **§3 và §8** của card. §2, §4, §5, §6, §7 không đổi — hợp đồng độc lập framework.

## 5.2 Scenario và nghĩa vụ default-deny

Dải scenario hiện tại là **SC01–SC53**, và sau FIX5 **mọi SC đều có ít nhất một fixture**
(`acceptance/scenarios.yaml`; ruling R5-02). Thư mục fixture: `ai/`, `boundary/`, `collection/`, `e2e/`,
`identity/`, `recovery/`, `reporting/`, `telegram/`, `ui/` — ba cái sau cùng là mới ở FIX5.

**`SC49` nằm trên mọi card**: quét default-deny trên toàn bộ 36 `forbidden_edges` của
`contracts/modules.yaml`. §5 của mỗi card mang bảng ranh giới mã lỗi R5-01 — `UNAUTHORIZED` cho principal sai
lớp qua HTTP, `FORBIDDEN_EDGE` cho cạnh không có trong `allowed_edges`, `CAPABILITY_DENIED` cho thiếu
capability tiến trình/mạng/file/tool, `CSRF_REJECTED` cho mutation owner thiếu CSRF. **Trả sai mã cũng là
FAIL**, không chỉ sai hành vi.

`SC50` (đường chạy thành công đầu-cuối) nằm trên bốn card của trục chính: ingest, collector, report và
delivery.

## 5.4 Phủ P0 — câu hỏi mở suốt mười một vòng, nay đã đo

`EV-PC10-06` chạy `acceptance/traceability.csv` (246 hàng) đối chiếu với 18 card. Ba đường phủ được tính
riêng, vì chúng **không** mạnh như nhau:

| Đường | Nghĩa | Sức nặng |
| --- | --- | --- |
| **direct** | card gọi đích danh REQ id | mạnh nhất |
| **via scenario** | `scenario_refs` của REQ giao với SC mà card mang | mạnh — SC có oracle và fixture |
| **via contract** | `contract_refs` của REQ giao với file card pin, **sau khi loại 9 file quá phổ biến** (`baseline.json`, `decision-register.md`, `requirements.csv`, `errors.yaml`, `modules.yaml`, `capabilities.yaml`, `ports.yaml`, `retry-policy.yaml`, `entities.yaml`) | **yếu** — chỉ nói "cùng đọc một file", không nói card chứng minh điều gì |

### Kết quả

| Tập | Có ít nhất một card | Mạnh (direct hoặc scenario) | Chỉ qua contract | Không card nào |
| --- | --- | --- | --- | --- |
| **12 mục phạm vi `REQ-P0-01…12`** (SRC-SPEC §2.1) | **12/12** | **12/12** | 0 | **0** |
| 234 hàng `priority = P0` | 223/234 | 192/234 | 31 | 11 |

**Mười hai mục phạm vi P0 phủ hết, và phủ mạnh** — mỗi mục nối tới card qua ít nhất một SC có oracle. Không
mục nào chỉ dựa vào "cùng đọc một file hợp đồng".

### Mười một hàng `priority = P0` không có card — và vì sao mười trong số đó là đúng

| Hàng | Là gì | Phán quyết |
| --- | --- | --- |
| `REQ-S13-02`…`-08` (7 hàng) | Định nghĩa mốc M1–M7 (SRC-SPEC §13) | **Không card-shaped.** Mốc được phủ bởi `precode/gates.yaml`, không bởi card triển khai — đúng như A2-R1 §7 mục 2 đã phán |
| `REQ-S1.4-04`, `-05` (2 hàng) | Chỉ số thành công vận hành; và một chỉ số **cố ý bị loại** vì không đo trung thực được | **Không card-shaped.** Đây là tiêu chí đánh giá E4, không phải nghĩa vụ code |
| `REQ-S6.3-01` | Khuyến nghị stack A của đặc tả | **Đã lỗi thời.** Owner chọn **B** (`OD-20260907-01` mục 3); hàng này giờ là bản ghi lịch sử |
| **`REQ-S7.3-01`** | *"Mọi bảng dữ liệu có `owner_id` dù chỉ có một owner"* | **Đây là lỗ hổng thật.** Nó là một bất biến dữ liệu **kiểm được**, không phải một cột mốc |

Về `REQ-S7.3-01`: hợp đồng **đã** thỏa — 58/60 entity trong `contracts/data/entities.yaml` có `owner_id`, và
hai ngoại lệ (`owner` và `schema_migration`) là chính đáng. Nhưng **không card nào mang nó như một nghĩa vụ
chứng minh**, nên khi code chạy sẽ không có ai kiểm. Xem `CR-PC10-08`.

### 31 hàng phủ "yếu"

Chúng chỉ nối với card qua một file hợp đồng dùng chung. Phần lớn là prose kiến trúc (`REQ-S13.2-*` —
"điểm không được bỏ qua"), tham số chờ đo (`REQ-A1`…`A4`, `REQ-OQ07`), hoặc mô tả màn hình. Chúng **chưa
phải** lỗ hổng, nhưng chúng cũng **chưa được chứng minh** bởi bất kỳ oracle nào — nếu ai đó cần con số
"P0 đã phủ", con số trung thực là **192/234 mạnh**, không phải 223 hay 234.

### Điều phép đo này **không** nói

Nó đo **khả năng với tới của card**, không đo implementation và không đo test. Một REQ "phủ mạnh" chỉ có
nghĩa là *có một card đáng lẽ phải chứng minh nó*. Chưa card nào chạy; E1–E4 vẫn `NOT_RUN`.

## 6. Đọc thêm

| Cần gì | Đọc ở đâu |
| --- | --- |
| Mẫu card và mười bốn mục bắt buộc | [`TEMPLATE.md`](TEMPLATE.md) |
| Kiểm chứng card có đủ thông tin không | [`WALKTHROUGH.md`](WALKTHROUGH.md) |
| Quy trình thay đổi và bằng chứng hết hiệu lực | `precode/change-control.md` |
| Điểm vào của toàn bộ baseline | `precode/README.md` |
| Điều kiện pass/fail của từng cổng, và `INV-01`…`INV-10` | `precode/gates.yaml` |
| Scenario và oracle (SC01–SC53) | `acceptance/scenarios.yaml` |
| Truy vết REQ ↔ contract ↔ scenario | `acceptance/traceability.csv` |
| Báo cáo audit, module READY/BLOCKED | `precode/review.md` |
