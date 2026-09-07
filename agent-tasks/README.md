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

**Pin hiện tại: `PC10-PIN-FCW4f-20260907`.** Hash tính lại trực tiếp trên repo sau mỗi wave FIX chạm file có
pin. Epoch cũ, theo thứ tự bị thay: `PC10-PIN-FCW4e-20260907` ← `PC10-PIN-FCW4d-20260907` ←
`PC10-PIN-FCW4c-20260907` ← `PC10-PIN-FCW4b-20260907` ← `PC10-PIN-FCW4-20260907` ← `PC10-PIN-20260907`.

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
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
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
