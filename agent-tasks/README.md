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
| 18 | [`TC-research-connector-metadata`](TC-research-connector-metadata.md) | M2 | G5 | `IMPLEMENTATION_VERIFIED` (E1 với response ghi sẵn; module **chưa** `CONTRACT_READY` — `REQ-A6`) |
| 19 | [`TC-secret-settings-service`](TC-secret-settings-service.md) | M3 | G5 | `IMPLEMENTATION_VERIFIED` (E1+E2 trên fixture; **không** provider nào được bật) |

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

TC-canonical-identity-merge ──► TC-research-connector-metadata ◄── TC-ingest-idempotent-ack-lost
        (connector trả metadata; identity vẫn là nơi duy nhất ghi work/alias)

TC-owner-auth-session ──► TC-secret-settings-service ──► TC-analysis-adapter-validation
        ▲                            │
        └── settings.* đi qua owner   └──► credential ngắn hạn cho task đang giữ lease
            session + CSRF                 (TC-analysis-once-per-generation sở hữu lease đó)
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

**Pin hiện tại: `PC10-PIN-P5c-20260909`.** Hash tính lại trực tiếp trên repo sau mỗi wave FIX chạm file có
pin. Lần pin này chạy sau `PKT-PC02-FIX13` (release 11:44Z): `contracts/data/entities.yaml` được sửa **chỉ ở
phần văn xuôi** của khối amendment `AMD-ENT-owner-01` — **không trường nào đổi**. Card vẫn phải pin lại, và
đó là điểm mấu chốt: quy tắc `STALE` đọc **byte**, không đọc ý định. Một ngoại lệ "chỉ là văn xuôi" sẽ biến
cửa pin thành thứ phải phán đoán mới dùng được, và phán đoán là thứ cơ chế này tồn tại để khỏi cần. Epoch cũ,
theo thứ tự bị thay: `PC10-PIN-P5b-20260908` ← `PC10-PIN-P4b-20260908` ← `PC10-PIN-P4-20260908` ← `PC10-PIN-P3b-20260908` ← `PC10-PIN-P3-20260908` ← `PC10-PIN-P2d-20260907` ← `PC10-PIN-P2c-20260907` ← `PC10-PIN-P2b-20260907` ← `PC10-PIN-P2-20260907` ← `PC10-PIN-P1d-20260907` ← `PC10-PIN-P1c-20260907` ← `PC10-PIN-P1b-20260907` ← `PC10-PIN-P1-20260907` ←
`PC10-PIN-OD01e-20260907` ← `PC10-PIN-OD01d-20260907` ←
`PC10-PIN-OD01c-20260907` ← `PC10-PIN-OD01b-20260907` ← `PC10-PIN-OD01-20260907` ← `PC10-PIN-FCW4f-20260907` ← `PC10-PIN-FCW4e-20260907` ← `PC10-PIN-FCW4d-20260907` ← `PC10-PIN-FCW4c-20260907` ← `PC10-PIN-FCW4b-20260907` ← `PC10-PIN-FCW4-20260907` ← `PC10-PIN-20260907`.

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

## 5.3 Layout hai ngôn ngữ, tám cây — Stack B (ACCEPTED)

Owner chốt **Option B** ngày 2026-09-07 (`OD-20260907-01` mục 3; ADR-0006 nay `accepted`). Phân chia ngôn
ngữ là **ACCEPTED**; đường dẫn cụ thể vẫn `PROVISIONAL` cho tới khi có repo triển khai; **framework chưa
được chốt** — ADR-0006 cố ý không nêu tên, nên card nào cần chọn framework phải DỪNG và raise CR.

```
server/     Python   backend, domain services, scheduler, report, delivery, auth, storage
collector/  Python   collector chạy trên máy cá nhân (Playwright Python, Chrome profile riêng — D09)
worker/     Python   analysis worker + AI adapter trên máy cá nhân
probe/      Python   kịch bản probe SP1 (M0), đầu ra là bằng chứng
shared/rr_contracts/  Python  model và hằng số **SINH RA** từ contracts/ (Pydantic + enum)
tools/      Python   CLI vận hành chạy ngoài tiến trình server — hiện đúng một file: tools/backup_cli.py
tests/      Python   đúng hai thư mục: tests/contract/… và tests/integration/… cho toàn bộ cây Python
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
- **`shared/rr_contracts/` là code SINH RA, không viết tay.** Model Pydantic, hằng số enum và client
  TypeScript (`web/src/lib/api.ts`) đều sinh từ `contracts/`. Sửa tay một file sinh ra là làm code
  và hợp đồng trôi khỏi nhau **âm thầm** — E0 sẽ có thêm phép kiểm "file sinh khớp hash hợp đồng".
  Muốn đổi hành vi ⇒ sửa hợp đồng ⇒ sinh lại ⇒ card `STALE` theo `INV-06`. Xem `precode/adr/ADR-0011`.
- **`tools/` là cây thứ tám, và nó phải là một cây riêng** (`CR-P0-03` mục 1). `TC-backup-restore-drill` §3
  pin `tools/backup_cli.py`; đó là `MOD-backup-cli`, thứ mà `contracts/modules.yaml` khai là **một tiến
  trình CLI riêng** gọi `backup.create_snapshot`, `backup.verify_snapshot`, `backup.restore_snapshot`,
  `backup.reconcile_after_restore` qua loopback với auth scope `backup_operator` — **không** phải session
  owner. Một principal khác và một tiến trình khác thì không nằm trong gói ứng dụng server: đặt file này
  dưới `server/` sẽ làm ranh giới ấy mờ đi ngay ở tầng đường dẫn. Không đường dẫn nào ở §3 của card đổi;
  đổi là §5.3 nay khai đúng cây mà card đã pin. `evidence/tools/verify_cards.py` đã tính `tools/` là cây
  Python, nên phép kiểm (m) không báo động sai.
- **Không có `tests/unit/`** (`CR-P0-03` mục 2 — mâu thuẫn đã gỡ theo hướng **bỏ**). §3 của cả 18 card chỉ
  dùng `tests/contract/` và `tests/integration/`; Giai đoạn 0 chỉ tạo hai thư mục đó (`tests/README.md`).
  Khai một thư mục thứ ba mà không card nào ghi vào là mời người ta đặt test ở chỗ không ai kiểm. Card đầu
  tiên thực sự cần unit test cục bộ sẽ tạo `tests/unit/` **kèm một CR** sửa §5.3, không tự thêm. Lưu ý:
  `precode/adr/ADR-0011-frameworks-and-toolchain.md` bảng bố cục còn ghi `tests/` = `contract/`, `unit/`,
  `integration/` và quy nguồn cho §5.3 này — nay lệch. PC10 không được ghi ADR ⇒ `CR-PC10-09`.
- **Quy chủ `web/src/lib/api.ts` — xác nhận, không đổi** (`CR-P0-04`). File này do **hai card UI**
  (`TC-ui-runs-three-states`, `TC-ui-reports-detail`) sở hữu, đúng như hai gạch đầu dòng trên. §3 của
  `TC-owner-auth-session` **ghi server side only** — bảng write set của nó chỉ có `server/app/auth/*` và
  `tests/*`, kèm một hàng nói thẳng *"nửa trình duyệt của CSRF **không** thuộc card này"*. Card và §5.3
  **không** mâu thuẫn nhau, nên PC10-FIX15 **không sửa** card đó; thứ lệch là amendment giữa phiên của
  Coordinator, và văn bản có pin thắng. Nửa server (đặt cookie `rr_csrf`, kiểm header `X-CSRF-Token`) là
  của `TC-owner-auth-session`; nửa trình duyệt (đọc cookie, gắn header) là của hai card UI.
- Đổi layout chỉ sửa **§3 và §8** của card. §2, §4, §5, §6, §7 không đổi — hợp đồng độc lập framework.
- **Card thứ 19, `TC-research-connector-metadata` (M2, Giai đoạn 2B), ghi dưới `server/app/research/`** —
  `client_arxiv.py`, `client_openalex.py`, `service.py`, `router.py`, `repository.py`, cộng hai file test.
  Không cây mới nào được thêm cho nó. `router.py` ở đây **không** mở route HTTP công khai: hai operation
  `research.*` là `transport: internal` trong `contracts/ports.yaml`.
- **Bốn card M1 nay đã có code thật dưới `server/` và `tests/`** — `TC-ingest-idempotent-ack-lost`,
  `TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness`; handoff ở
  `evidence/handoffs/TC-*-handoff.md`, cả bốn `DONE_WITH_CONCERNS` và `SELF_VALIDATION`, **đang chờ audit
  độc lập A3-R2**. Bố cục ở trên vì vậy không còn hoàn toàn là dự định: đường dẫn §3 của bốn card đó nay
  là file có thật, và đổi chúng là đổi code, không chỉ đổi giấy.

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

`EV-PC10-06` chạy `acceptance/traceability.csv` (246 hàng) đối chiếu với 18 card. **Phép đo này chưa được chạy lại sau khi card thứ 19 (`TC-research-connector-metadata`) ra đời** — mọi con số dưới đây là của 18 card, và card mới chỉ có thể làm phủ tăng, không thể làm giảm. Ba đường phủ được tính
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
nghĩa là *có một card đáng lẽ phải chứng minh nó*. Phép đo này chạy khi **chưa card nào chạy**, và nó
không được cập nhật theo tiến độ code.

**Cập nhật tiến độ (2026-09-07).** Bốn card M1 — `TC-ingest-idempotent-ack-lost`,
`TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness` — **đã được
thi công** (`OD-20260907-02`; handoff ở `evidence/handoffs/TC-*-handoff.md`) và **đang chờ A3-R2**. Cả bốn
handoff tự khai `DONE_WITH_CONCERNS` với `review_type: SELF_VALIDATION`; **chưa có audit độc lập nào**,
nên không con số nào ở §5.4 được nâng lên vì việc này. E1 đã chạy thật trong phạm vi bốn card đó; E2–E4
vẫn `NOT_RUN`. Mười bốn card còn lại chưa bắt đầu.

**Giai đoạn 2 (`OD-20260907-03`, 2026-09-07).** Owner ra lệnh bắt đầu Giai đoạn 2. **2A** phát hai card đã có
sẵn — `TC-x-feasibility-probe` và `TC-collector-checkpoint-resume` (§0 của chúng nay mang `dispatch_status`);
khẳng định **live** của probe vẫn bị chặn bởi cổng Owner ở `contracts/ops/collector-probe.md` §6 mục 2–4.
**2B** cần một card chưa tồn tại, nên gói này viết nó: `TC-research-connector-metadata` (M2). Thư mục nay có
**20 card**. Card thứ 19 **chưa được thi công** và trần của nó **không** nâng trần của `MOD-research-connector`:
module đó vẫn không đủ điều kiện `CONTRACT_READY` cho tới khi bốn giá trị `PLACEHOLDER_KC` của
`contracts/retry-policy.yaml` `research_connector_rate_limit` được điền bằng **dữ kiện đọc từ tài liệu chính
thức** (`REQ-A6`). Không con số nào được đoán, và card ghi điều đó thành một điểm dừng (`SG-A6`).

**Card thứ 20 — `TC-secret-settings-service` (M3, `PKT-PC10-FIX28`).** Nó lấp khoảng trống `G-6`: sáu
operation `secret.*` / `settings.*` có trong `contracts/ports.yaml` nhưng **không module nào hiện thực**, nên
hiện **không có chỗ hợp lệ** để cất một API key, webhook secret Telegram, hay credential ngắn hạn theo task —
và ca âm `ISO-05` của `contracts/ai/providers.yaml` §4 (*gọi `secret.issue_task_credential` cho một worker
**không** giữ lease và thấy nó bị từ chối*) **không chạy được**, vì operation đó chưa có mã. Card **chưa được
thi công**; nó được pin tại **cùng epoch** với 19 card kia — tên epoch đọc ở §4, file này **không** chép tay
tên đó lần thứ hai (`F-A2R1-03`) — và 19 card kia **không** bị sinh lại vì không file đã pin nào đổi byte.

## 5.5 Bộ khung Giai đoạn 0 đã tồn tại — và tên module để import

**Repo triển khai không còn rỗng.** Owner ra lệnh bắt đầu Giai đoạn 0 và 1 (`OD-20260907-02` mục 2); gói
`PKT-P0-SKELETON` đã dựng bộ khung của tám cây ở §5.3 (`evidence/handoffs/P0-skeleton-handoff.md`). Điều
này đổi **hai** thứ cho người đọc card, và không đổi gì khác:

1. Câu "chưa có repo triển khai" trong §3 của card nay **đã hết đúng** cho phần bộ khung. Đường dẫn ở §3
   vẫn được giữ nguyên chữ như đã pin — chúng vẫn `PROVISIONAL` theo nghĩa *chưa file nghiệp vụ nào tồn
   tại*, nhưng **thư mục gốc và cách gói được nạp thì đã cố định** và card không được tự đổi.
2. Hành vi nghiệp vụ vẫn bằng không. Bộ khung chỉ có `health.get_liveness`; `health.get_readiness` **cố ý
   không được route** vì nó thuộc `TC-storage-write-blocked-readiness`. Không card nào đã chạy; E1–E4 vẫn
   `NOT_RUN`.

**Tên import (`PROV-P0-01`).** Gốc repo là import root. Ba gói Python được nạp bằng **tên đầy đủ**:

| Cây | Import như thế nào | Không phải |
| --- | --- | --- |
| `server/app/…` | `server.app.auth.service`, `server.app.ingest.router`, … | `app.auth.service` |
| `collector/app/…` | `collector.app.reader`, … | `app.reader` |
| `worker/app/…` | `worker.app.…` | `app.…` |
| `shared/rr_contracts/` | `rr_contracts.…` (package thật, cả ba cây đều import) | — |

Lý do là một lỗi thật, không phải khẩu vị: nếu ba cây cùng khai một package top-level tên `app` thì chúng
**đè lên nhau** trên cùng `sys.path`, và `tests/contract/` cần hai trong ba cùng lúc — `pytest` đã báo
`import file mismatch` ngay lượt chạy đầu của Giai đoạn 0. `server`, `collector`, `worker` vì vậy là
workspace member **ảo** (không build/cài), còn `shared/rr_contracts` là package thật.

**Không đường dẫn file nào ở §3 của bất kỳ card nào bị đổi vì điều này.** Thứ bị ràng buộc là **lệnh và
tên module ở §8**, đúng chỗ card đã khai là `PROVISIONAL`. Card nào cần một tên import khác thì DỪNG và
raise CR; sửa ngầm sẽ làm hai cây test không cùng nạp được.

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
