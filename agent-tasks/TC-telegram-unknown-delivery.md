---
card_id: TC-telegram-unknown-delivery
title_vi: Delivery: trạng thái unknown không tự gửi lại
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M6
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
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

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P5c-20260909`** (thay `PC10-PIN-P5b-20260908`; các epoch cũ hơn: `PC10-PIN-P5b`, `PC10-PIN-P4b`, `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. **`P4`** pin sau `PKT-PC00-FIX30` (`OD-20260908-10`) — lần ghi `precode/` cuối của vòng này. Đợt sửa Giai đoạn 4/6 chạy song song chỉ chạm code, test, handoff và manifest: **không** file nào trong số đó được card pin, nên chúng không tạo ra một lần pin lại. **`P4b`** pin sau `PKT-PC00-FIX32`: `precode/adr/ADR-0011-frameworks-and-toolchain.md` được sửa (phạm vi `mypy`, `CR-PC00-35`). `ADR-0011` nằm trong read set của **mọi** card, nên một mình nó đủ làm cả 19 card `STALE`. Gói song song chỉ chạm bộ file dựng gói (pyproject, uv lockfile), workflow CI, Makefile, .gitignore và một test smoke của server — **không** file nào trong số đó được card pin hay trích dẫn, đã kiểm trực tiếp. **`P5`** pin sau `AMD-ENT-maintenance-01` (`PKT-PC02-FIX16`): `contracts/data/entities.yaml` thêm entity `maintenance_window` và chia lại tập purge (37/22/2), kéo theo `precode/change-control.md` và `precode/decision-register.md`. Thư mục nay có **20 card** — `TC-secret-settings-service` (khoảng trống `G-6`) được thêm ở `PKT-PC10-FIX28`. Tên `P5` **không bao giờ được phát hành**: nó được pin trong lúc đợt propagate của `PKT-PC02-FIX17` còn đang ghi, nên tập byte của nó sai ngay khi vừa ghi xong và bị `P5b` thay trước khi có ai đọc. Ghi lại ở đây để không ai đi tìm một epoch `P5` hợp lệ. **`P5c` (2026-09-09)** pin sau `PKT-PC02-FIX19`: bản `E0-18` siết chặt của W6n bắt hai fixture `acceptance/fixtures/recovery/` vẫn ghi tập purge cũ (20/21) trong khi hợp đồng đã sang 37/22/2; W3n sửa chúng, và fixture **có** pin nên card phải pin lại. Tên epoch mang ngày pin, không phải ngày của thay đổi. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` | 27451 |
| `precode/baseline.json` | `e8cf3910c6f2351a2c7c4a8620121b0415a58c5c7ec86eee7ba5d33c343c1a70` | 127222 |
| `precode/decision-register.md` | `ab47a9adf997041655a0a571d62987d0f36e45cc04b2639d9f0d0c755e7fc7ed` | 188780 |
| `contracts/modules.yaml` | `7a4e19bdbb43e1339f305cd4715f1e7ac704b09720408ccf1db48a01b23c1e25` | 108912 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412` | 128872 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `7cd85e09431fa52555ee13bb5fb8f5a00932e38801677212e8baa18c14c27827` | 255475 |
| `contracts/state/delivery.yaml` | `318789179ec79a4e21939a82d4fb78bfb3cd257ed7c3af4c519bf2ab631ee807` | 29542 |
| `contracts/telegram/delivery.md` | `18dc7c175a56efbfd434b63aac603d8408030f5fe68b63046cd83c3c9db8a0e1` | 26044 |
| `contracts/state/report.yaml` | `77969cb473c84a7df90e6b784ad1afa637313e813ccbb59d99b1ea329241245f` | 30187 |
| `contracts/http/openapi.yaml` | `a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d` | 231727 |
| `contracts/ui/screens.yaml` | `464579a807e00e44c3215cf9fbf243df4a2bef8db6e137d71a2409fe6bc6b854` | 51212 |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | `567828c11049d26993cbeee0d0bd6c157d9938263ec69c5a05fa045da3ceb0e3` | 5549 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `4c02d39a2d6ef80f17db7f1aebbda1de39bacaa9b4d417a3c2721c10b6ccf21f` | 5903 |
| `acceptance/fixtures/telegram/README.md` | `dbb368afae93bd40530a153769106995643996669a57a26dd2e55fb1ef905863` | 10508 |
| `acceptance/fixtures/telegram/a-multipart-part2-unknown-no-resend.json` | `555bf7edf28f1d7b8b27718bf54d77f79046720cd47035db09a8d9a45846bed6` | 7129 |
| `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json` | `10d7c4deccdb95a7fcc1b02033ff90a785ce881d79e4f8ba6d0d648f109ef215` | 5047 |
| `acceptance/fixtures/telegram/c-permanent-failure-report-intact.json` | `2d15cca5df3249dc1d52f94648b617c7bf2cb2a702000f97a5ad5bd1b5631d2b` | 4938 |
| `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json` | `248cda9cfe131aa4f6f72d36289082895d9d4162e93c7c195f239059d38ece95` | 4259 |
| `acceptance/fixtures/telegram/e-relink-old-generation-cancelled.json` | `9289f962019f337d542fe0f044e2d99e1eeb42aa48e7b7605c013b1a2f48ab91` | 4729 |
| `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json` | `3b0d6f24a06ac907ce6c65b139d6124f09dd9ff89389e64d58256a844004a3fa` | 6023 |
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
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0003-delivery-unknown-state.md`, `precode/adr/ADR-0004-tag-freeze-point.md`.
3. Hợp đồng nghiệp vụ: `contracts/state/delivery.yaml`, `contracts/telegram/delivery.md`, `contracts/retry-policy.yaml`, `contracts/state/report.yaml`, `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/a-multipart-part2-unknown-no-resend.json`, `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json`, `acceptance/fixtures/telegram/c-permanent-failure-report-intact.json`, `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json`, `acceptance/fixtures/telegram/e-relink-old-generation-cancelled.json`, `acceptance/fixtures/reporting/c-tag-changed-after-publish-before-send.json`, `acceptance/fixtures/recovery/a-restore-old-outbox-nothing-sent.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/e2e/README.md`, `acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

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

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

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

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/telegram/delivery.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 3 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/http/openapi.yaml`, `contracts/telegram/delivery.md`, `contracts/ui/screens.yaml`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | **`CR-PC07-04` còn OPEN**: giới hạn định dạng/độ dài/rate limit của Telegram vẫn `KC` (không có URL tài liệu trong nguồn đã pin). Chia multipart theo số ký tự đoán là **cấm**; DỪNG và raise CR. |
| `SG-02` | Nếu retry budget cho delivery trong `contracts/retry-policy.yaml` là PROVISIONAL, ghi rõ trong evidence; không tự tăng để test pass. |
| `SG-03` | Không bao giờ tự động chuyển `unknown → pending`. Chỉ `delivery.decide_unknown` của owner làm được. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
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
