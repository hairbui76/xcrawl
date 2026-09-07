---
card_id: TC-telegram-unknown-delivery
title_vi: Delivery: trạng thái unknown không tự gửi lại
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M6
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-delivery-service]
scenario_refs: [SC14, SC15, SC19, SC25, SC27, SC49, SC50]
invariant_refs: [I05, I09, I13, I15]
evidence_manifest_id: EVM-TC-telegram-unknown-delivery
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-telegram-unknown-delivery — Delivery: trạng thái unknown không tự gửi lại

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. Stack (Option A / Python) là **PROVISIONAL** theo `precode/adr/ADR-0006-stack-option-a.md`; mọi đường dẫn ở §3 và mọi lệnh ở §8 có điều kiện *"nếu ADR-0006 được chấp nhận"*.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-FCW4f-20260907`** (thay `PC10-PIN-FCW4e-20260907`; các epoch cũ hơn: `PC10-PIN-FCW4d-20260907`, `PC10-PIN-FCW4c-20260907`, `PC10-PIN-FCW4b-20260907`, `PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). Hash dưới đây được **tính lại trực tiếp trên repo**; thay đổi duy nhất so với `FCW4e` là `contracts/modules.yaml` (năm denied case thêm `event_type`; không oracle nào của card bị ảnh hưởng). **Card là nguồn chuẩn của tên epoch**; mọi file khác khẳng định pin hiện hành phải đọc tên từ đây, không chép tay (finding `F-A2R1-03`). Trước khi bắt đầu, chạy `sha256sum` trên **mọi** dòng dưới đây. Lệch một dòng ⇒ card `STALE`, DỪNG (`precode/change-control.md` §5, quy tắc `INV-06`/`INV-09` của `precode/gates.yaml`).

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/baseline.json` | `e4c3f4563e04293c319bf746b371bc67857115b7070d14a9771de3238e8683a7` | 97620 |
| `precode/decision-register.md` | `212441a429420d1cc11cdc4a9c79a11648e45e1b92278a08f77a9779943ad15d` | 97899 |
| `contracts/modules.yaml` | `11af00fd97a03d5357fc1a72d0e4e61293164f449c3a50e700c03a202e1166c7` | 105642 |
| `contracts/capabilities.yaml` | `fae5891cff5ff25757f168d8182111fa4fc6b49f6b851ac7cc07105fef952cf7` | 45672 |
| `contracts/ports.yaml` | `93ba159856a4821ad46d1d05199987f475c8ae5603d8f9200e1418b0e2eab42e` | 126182 |
| `contracts/errors.yaml` | `b63eef7abd4cee328581e5e06cbc8314e60e52e03468dbe6acea42a0a843ad26` | 62269 |
| `contracts/retry-policy.yaml` | `5e083230e2cc5db481736adcf189a6cf8e302ebdf45cad614582731698cf06d5` | 41620 |
| `contracts/data/entities.yaml` | `c2ceeafd1b78705941f368bfe73f67cf097ffad8179c7455b2d4eeda571b5a1e` | 221041 |
| `contracts/state/delivery.yaml` | `9fcccc25fed432a895b15e9b98787d7294dd298d9209e9b0f2c7f801e1579626` | 26652 |
| `contracts/telegram/delivery.md` | `cb3a4b30a26f2a5ca5cf9d11359b84ce5612c003dfe51c3acbdbba5d7fde226c` | 16807 |
| `contracts/state/report.yaml` | `2b22c27df302c7fbf733b352ad41390a1d407ac98cfa7b1a816cf3580349aba0` | 27154 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `contracts/ui/screens.yaml` | `db78678cba7e46b33669596f02963e1eac5e65804c6f9a997bf22d72ba6bc296` | 47481 |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | `1cb86d8db85c4350dc1eaf6b0822908030219d326c65a8fbec321066d2aab2a0` | 5105 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `64c0793eeca31b6ac0606813adac96fa483e01eb4b81eaef950edfff16fd3194` | 5459 |
| `acceptance/fixtures/telegram/README.md` | `dbb368afae93bd40530a153769106995643996669a57a26dd2e55fb1ef905863` | 10508 |
| `acceptance/fixtures/telegram/a-multipart-part2-unknown-no-resend.json` | `555bf7edf28f1d7b8b27718bf54d77f79046720cd47035db09a8d9a45846bed6` | 7129 |
| `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json` | `10d7c4deccdb95a7fcc1b02033ff90a785ce881d79e4f8ba6d0d648f109ef215` | 5047 |
| `acceptance/fixtures/telegram/c-permanent-failure-report-intact.json` | `2d15cca5df3249dc1d52f94648b617c7bf2cb2a702000f97a5ad5bd1b5631d2b` | 4938 |
| `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json` | `248cda9cfe131aa4f6f72d36289082895d9d4162e93c7c195f239059d38ece95` | 4259 |
| `acceptance/fixtures/telegram/e-relink-old-generation-cancelled.json` | `9289f962019f337d542fe0f044e2d99e1eeb42aa48e7b7605c013b1a2f48ab91` | 4729 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | `4d5f14c423c1764e9e866df55becd63e6ee6d828e788abc79b17d39db3b6f089` | 5189 |
| `acceptance/fixtures/recovery/a-restore-old-outbox-nothing-sent.json` | `e7671e7d852f9b0564c5c269df95e598e3de88cdb94142df23a29ee38b543838` | 4194 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/e2e/README.md` | `74790ee8435791e5dbc360cf84a0737f660e2bebcbdb0749cdc1528a669d9ca8` | 6013 |
| `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json` | `a925781ecf2d36e3cd02a3d666819bc5186c8d809e7865e51bac77d387678c00` | 30745 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-telegram-unknown-delivery`
- **Milestone:** M6 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-delivery-service`

**Mục tiêu.** Vòng đời giao digest tách hẳn khỏi vòng đời run: ghi attempt **trước** network call, timeout/mất kết nối ⇒ `unknown` và **không** retry tự động, multipart giữ receipt từng phần, thất bại Telegram không làm report biến mất hay run thành thất bại thu thập.

**Non-goals.**

- Không đổi nội dung report đã publish (B01).
- Không viết linking (card 11).
- Không tự quyết chấp nhận nguy cơ trùng — đó là quyết định của operator qua `delivery.decide_unknown`.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0003-delivery-unknown-state.md`, `precode/adr/ADR-0004-tag-freeze-point.md`.
3. Hợp đồng nghiệp vụ: `contracts/state/delivery.yaml`, `contracts/telegram/delivery.md`, `contracts/retry-policy.yaml`, `contracts/state/report.yaml`, `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/a-multipart-part2-unknown-no-resend.json`, `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json`, `acceptance/fixtures/telegram/c-permanent-failure-report-intact.json`, `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json`, `acceptance/fixtures/telegram/e-relink-old-generation-cancelled.json`, `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json`, `acceptance/fixtures/recovery/a-restore-old-outbox-nothing-sent.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/e2e/README.md`, `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/delivery/service.py` | create_intent / dispatch_next / record_receipt / mark_unknown / decide_unknown |
| `server/app/delivery/parts.py` | `ENT-delivery-part` với index, payload hash, receipt từng phần |
| `server/app/delivery/outbox.py` | outbox intent đã commit; sender lease |
| `server/app/delivery/router.py` | HTTP handler `delivery.get_status`, `delivery.decide_unknown` |
| `tests/integration/test_delivery_unknown_no_retry.py` | timeout sau khi có thể đã gửi |
| `tests/integration/test_multipart_partial_receipt.py` | phần 2 unknown, phần 1 sent |
| `tests/integration/test_permanent_failure_report_intact.py` | hash report không đổi |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `delivery.create_intent`
- `delivery.dispatch_next`
- `delivery.record_receipt`
- `delivery.mark_unknown`
- `delivery.get_status`
- `delivery.decide_unknown`

**Consumes** (chỉ được gọi đúng những operation này):

- `telegram.send_payload`
- `storage.get_health`

**Schema:**

- payload digest và rendering → `contracts/telegram/delivery.md`
- nội dung report được đóng gói → `contracts/schemas/report.schema.json`

**State effects.** `contracts/state/delivery.yaml` — `T-DL-00`…`T-DL-09`: `pending → sending → sent`, nhánh `retry_wait`, `unknown`, `failed`, `cancelled`. Ghi attempt **trước** network call (`T-DL-01`). `unknown` là quasi-terminal: **không** retry tự động (B03/AMD-B03/ADR-0003).

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-delivery` (telegram_link_generation); `ENT-delivery-part` (provider_message_id); `ENT-report` (abort_reason, selection_version). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-report-service` — internal cho `delivery.create_intent`
- `MOD-job-service` — internal cho alert intent của run
- `MOD-web-ui` — owner_session (+CSRF) cho `delivery.decide_unknown`

**Được phép gọi:**

- MOD-telegram-adapter (`telegram.send_payload`)
- MOD-data-store

**Đường bị cấm (denied paths):**

- Delivery **không** sửa nội dung report đã publish (B01, I05).
- Không gửi tới recipient cũ sau unlink/relink (`cancelled`).
- Không chuyển payload cũ sang recipient mới âm thầm.
- Sau restore chưa đối soát: `RESTORE_UNVERIFIED`, outbox **không** replay (I15).

Bảo mật (chốt post-FIX1 trong `contracts/http/openapi.yaml`): `owner_session` cho mutation nghĩa là `ownerSessionCookie` **AND** `ownerCsrfToken` trong **một** security requirement; collector và analysis worker dùng bearer riêng; mọi route `backup.*` chỉ nhận `backupOperatorToken`.

**Ranh giới mã lỗi khi bị từ chối (ruling R5-01, bắt buộc — chọn sai mã là FAIL):**

| Tình huống | Mã |
| --- | --- |
| Request HTTP từ một lớp principal không được phép cho operation đó (ví dụ token collector gọi `save.create`) | `UNAUTHORIZED` (401) |
| Lời gọi/import trong tiến trình đi qua một cạnh **không** có trong `allowed_edges` (ví dụ FE-08 collector → analysis worker, scheduler → Telegram) | `FORBIDDEN_EDGE` |
| Actor thiếu capability tiến trình/mạng/filesystem/tool (adapter mở socket, connector điều khiển Chrome) | `CAPABILITY_DENIED` |
| Mutation dùng phiên owner mà thiếu/sai CSRF token | `CSRF_REJECTED` (403; **không** hủy phiên) |

Mỗi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` có `denied_cases[]` với `expected_error_code` theo bảng trên và `scenario_refs: [SC49]`. Oracle chung: `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §6. Invariants và transaction

| Invariant | Nội dung |
| --- | --- |
| `I05` | không đổi nội dung report sau publish |
| `I09` | Telegram thất bại không làm report biến mất hoặc run thành thất bại thu thập |
| `I13` | unknown hiển thị riêng, không gộp vào failed |
| `I15` | restore không tự phát lại outbox cũ |

**Transaction và commit point:**

- Outbox intent commit trước, network call sau; receipt ghi sau. Không có network call trong transaction SQLite.

**Race, replay và forbidden effects:**

- Timeout sau điểm có thể đã gửi ⇒ `unknown`; app nêu 'chưa xác định'; operator quyết định (fixture `b`).
- Multipart: phần 2 `unknown` **không** được gửi lại chỉ vì aggregate chưa `sent` (fixture `a`).
- Unlink giữa `pending` và `sending` ⇒ `cancelled` (fixture `d`).
- Restore môi trường cũ ⇒ 0 tin được gửi trước khi đối soát xong (fixture `a` ở recovery).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `TELEGRAM_SEND_UNCERTAIN` | `delivery.unknown`; giữ report; **không** auto resend |
| `TELEGRAM_PERMANENT_FAILURE` | `delivery.failed`; report giữ nguyên; run **không** đổi kết quả |
| `RESTORE_UNVERIFIED` | dispatcher khóa; outbox không replay |
| `STALE_LEASE` | sender lease cũ không gửi được |
| `VALIDATION_ERROR / IDEMPOTENCY_CONFLICT` | 400 / conflict |
| `CAPABILITY_DENIED` | `telegram.send_payload` thiếu capability |
| `STORAGE_WRITE_FAILED` | không ghi attempt ⇒ **không** gọi mạng |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC14
- SC15
- SC19
- SC25
- SC27
- SC49
- SC50

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/integration/test_delivery_unknown_no_retry.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_multipart_partial_receipt.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_permanent_failure_report_intact.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `b`: sau timeout ⇒ `delivery.state = unknown`, **0** lời gọi gửi lại tự động.
- Fixture `a`: `delivery_part[1].state = sent` với receipt; `delivery_part[2].state = unknown`; 0 resend.
- Fixture `c`: `TELEGRAM_PERMANENT_FAILURE` ⇒ hash report trong DB **không đổi**, `run.outcome` không đổi.
- Fixture `c` (reporting): tag đổi sau publish trước gửi ⇒ payload vẫn là bản đã publish.
- Attempt row tồn tại **trước** mọi lời gọi mạng (đếm thứ tự trong trace).

**Evidence artifacts:** log pytest; trace thứ tự attempt/network; hash report trước/sau; dump `delivery_part`.

**Yêu cầu live.** Gửi thật tới Telegram (AC-14 mức E3) không thuộc card này.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | **`CR-PC07-04` còn OPEN**: giới hạn định dạng/độ dài/rate limit của Telegram vẫn `KC` (không có URL tài liệu trong nguồn đã pin). Chia multipart theo số ký tự đoán là **cấm**; DỪNG và raise CR. |
| `SG-02` | Nếu retry budget cho delivery trong `contracts/retry-policy.yaml` là PROVISIONAL, ghi rõ trong evidence; không tự tăng để test pass. |
| `SG-03` | Không bao giờ tự động chuyển `unknown → pending`. Chỉ `delivery.decide_unknown` của owner làm được. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-report-coverage-publish-cas`
- `TC-telegram-linking-auth`
- `TC-backup-restore-drill`(I15)

## §12. Reviewer scope

Reviewer đọc `contracts/state/delivery.yaml` (10 transition + `delivery_part_semantics`), `contracts/telegram/delivery.md`, 7 fixture ở §2. Câu hỏi bắt buộc: có đường nào `unknown` biến thành một lần gửi lại tự động không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-telegram-unknown-delivery`
- **Vị trí:** `evidence/runs/TC-telegram-unknown-delivery/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
