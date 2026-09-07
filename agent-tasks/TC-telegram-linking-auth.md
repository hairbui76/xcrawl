---
card_id: TC-telegram-linking-auth
title_vi: Telegram: liên kết bằng mã một lần và từ chối chat lạ
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M6
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-telegram-adapter]
scenario_refs: [SC13, SC18, SC25, SC45, SC46, SC47, SC49]
invariant_refs: [I01, I11]
evidence_manifest_id: EVM-TC-telegram-linking-auth
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-telegram-linking-auth — Telegram: liên kết bằng mã một lần và từ chối chat lạ

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
| `contracts/telegram/commands.yaml` | `fc1a18dac332ea51e63721536d6a47b1d5a3048ed408af24ae787a91874e3556` | 24834 |
| `contracts/telegram/delivery.md` | `cb3a4b30a26f2a5ca5cf9d11359b84ce5612c003dfe51c3acbdbba5d7fde226c` | 16807 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `contracts/ops/secrets.md` | `2ed96d93ecdbb74fd825e952abd85541ddecfe25cfd1c08efd739d708c165d48` | 24387 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | `1cb86d8db85c4350dc1eaf6b0822908030219d326c65a8fbec321066d2aab2a0` | 5105 |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | `734766c889edbbb0dce94dca92b7da04a9c0b6721536addaeaac3ee6c783a291` | 5962 |
| `acceptance/fixtures/telegram/README.md` | `dbb368afae93bd40530a153769106995643996669a57a26dd2e55fb1ef905863` | 10508 |
| `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json` | `248cda9cfe131aa4f6f72d36289082895d9d4162e93c7c195f239059d38ece95` | 4259 |
| `acceptance/fixtures/telegram/e-relink-old-generation-cancelled.json` | `9289f962019f337d542fe0f044e2d99e1eeb42aa48e7b7605c013b1a2f48ab91` | 4729 |
| `acceptance/fixtures/telegram/f-stale-callback-no-save.json` | `c364bd77a60ac71f2c534714e77329a019756c8198ff353c6ed5052189b4f495` | 3890 |
| `acceptance/fixtures/telegram/g-link-code-used-twice.json` | `db813e76477f1be7d940d30205be25409d4e4b345bc4cc77e28e3b718506ae7b` | 3700 |
| `acceptance/fixtures/telegram/h-unknown-chat-status-silent.json` | `1e368114fb976d708aa131518afe36db932c4df5e42c6dad17c2aa6078032ed2` | 3293 |
| `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json` | `8fa94e8db3007272fd7888e29778a383d354f8ba79380eaf3fc1186422e0d253` | 6967 |
| `acceptance/fixtures/telegram/l-run-now-while-needs-user.json` | `504781a5e21794e0774f9efaae0bbafb5eff92e7945b94e399d36ff5dd1e5350` | 4273 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-telegram-linking-auth`
- **Milestone:** M6 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-telegram-adapter`

**Mục tiêu.** Chỉ chat đã liên kết mới chạy được đúng ba lệnh; chat lạ bị bỏ im lặng không phản hồi; ngoại lệ duy nhất là một tin nhắn **đúng định dạng mã liên kết** được đối chiếu với mã chưa hết hạn, chưa dùng.

**Non-goals.**

- Không thêm lệnh Telegram thứ tư: hủy liên kết là hành động trong app (`F-PC00-01`, B10).
- Không viết delivery (card `TC-telegram-unknown-delivery`).
- Không tự chốt định dạng/hạn/rate limit của mã — cả ba là PROVISIONAL (`CR-PC07-01`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0003-delivery-unknown-state.md`, `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md`.
3. Hợp đồng nghiệp vụ: `contracts/telegram/commands.yaml`, `contracts/telegram/delivery.md`, `contracts/http/openapi.yaml`, `contracts/ops/secrets.md`, `contracts/ops/internet-boundary.md`, `contracts/data/entities.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/telegram/README.md`, `acceptance/fixtures/telegram/d-unlink-before-send-cancelled.json`, `acceptance/fixtures/telegram/e-relink-old-generation-cancelled.json`, `acceptance/fixtures/telegram/f-stale-callback-no-save.json`, `acceptance/fixtures/telegram/g-link-code-used-twice.json`, `acceptance/fixtures/telegram/h-unknown-chat-status-silent.json`, `acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`, `acceptance/fixtures/telegram/l-run-now-while-needs-user.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/telegram/ingress.py` | xác thực `X-Telegram-Bot-Api-Secret-Token` bằng so sánh constant-time |
| `server/app/telegram/commands.py` | allowlist đúng ba lệnh `CMD-status`, `CMD-run-now`, `CMD-save` |
| `server/app/telegram/linking.py` | phát/tiêu thụ mã một lần, rate limit theo chat |
| `server/app/telegram/router.py` | HTTP handler `telegram.*` |
| `tests/contract/test_telegram_command_allowlist.py` | chat lạ, callback giả, mã hết hạn |
| `tests/integration/test_link_code_once.py` | mã dùng hai lần |
| `tests/integration/test_unknown_chat_silent.py` | outbound call count = 0 |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `telegram.receive_update`
- `telegram.execute_command`
- `telegram.issue_link_code`
- `telegram.consume_link_code`
- `telegram.unlink`

**Consumes** (chỉ được gọi đúng những operation này):

- `run.list`
- `run.run_now`
- `save.create`

**Schema:**

- hình dạng update và command → `contracts/telegram/commands.yaml`
- payload gửi đi → `contracts/telegram/delivery.md`

**State effects.** `ENT-telegram-link`, `ENT-telegram-link-code`, `ENT-telegram-link-attempt`, `ENT-telegram-update-log`. Relink tạo **link generation** mới; intent của generation cũ bị `cancelled` (fixture `e`).

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `EXT-telegram-api` — telegram_ingress_secret (header `X-Telegram-Bot-Api-Secret-Token`)
- `MOD-web-ui` — owner_session + CSRF cho `telegram.issue_link_code` và `telegram.unlink`

**Được phép gọi:**

- MOD-job-service (`run.list`, `run.run_now`)
- MOD-saved-service (`save.create`)
- MOD-data-store

**Đường bị cấm (denied paths):**

- Adapter **không** sửa SQLite trực tiếp, không sửa tag/config, không lấy AI key (SRC-PLAN §6).
- Biết chat ID **không** phải là quyền (SRC-SPEC §11.3).
- Nội dung nguồn **không** được định nghĩa recipient (I11).
- `run.status` là read-only; `run.run_now` không ghi đè `needs_user` (B10).

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
| `I01` | mutation qua port đã xác thực |
| `I11` | nội dung không đổi recipient |

**Transaction và commit point:**

- Tiêu thụ mã liên kết là CAS trên `telegram_link_code`: một mã chỉ dùng được một lần.

**Race, replay và forbidden effects:**

- Mã dùng hai lần ⇒ lần hai bị từ chối (fixture `g`).
- Callback cũ sau khi unlink ⇒ không tạo Saved (fixture `f`).
- Relink rồi mới gửi ⇒ intent generation cũ `cancelled`, không gửi cho recipient cũ (fixture `e`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `UNAUTHORIZED` | webhook secret sai/thiếu ⇒ 401, **không** xử lý update |
| `UNAUTHORIZED_COMMAND` | chat lạ ⇒ im lặng, 0 outbound call, không đổi domain state; ngoại lệ linking theo B09 |
| `VALIDATION_ERROR` | 400 |
| `CSRF_REJECTED` | 403 cho mutation của owner session |
| `IDEMPOTENCY_CONFLICT` | update trùng `update_id` |
| `STORAGE_WRITE_FAILED` | không ghi link |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC13
- SC18
- SC25
- SC45
- SC46
- SC47
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_telegram_command_allowlist.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_link_code_once.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_unknown_chat_silent.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `h`: chat lạ gửi `/status` ⇒ **outbound call count = 0**, 0 mutation, 0 reply.
- Fixture `i`: chat lạ gửi chuỗi đúng định dạng mã ⇒ chỉ đối chiếu với mã chưa hết hạn/chưa dùng; sai ⇒ im lặng.
- Fixture `g`: mã dùng lần hai ⇒ từ chối, `COUNT(telegram_link active) = 1`.
- Fixture `l`: `/run-now` khi run `needs_user` ⇒ transition log rỗng.
- Đúng ba lệnh trong allowlist; lệnh thứ tư không tồn tại.

**Evidence artifacts:** log pytest; đếm outbound call; dump `telegram_link_attempt`.

**Yêu cầu live.** Gửi thật tới Telegram là E3, không thuộc card này.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | **`CR-PC07-04` còn OPEN và là rủi ro lớn nhất của gói Telegram**: giới hạn định dạng của Telegram (độ dài tin, độ dài callback data, parse mode, bảng escape, rate limit) vẫn ở trạng thái `KC` — chưa ai đọc <https://core.telegram.org/bots/api#sendmessage> vì phiên Pre-code không có mạng. Không đoán giới hạn; DỪNG nếu implementation cần một con số cụ thể. |
| `SG-02` | `CR-PC07-01` còn OPEN: định dạng mã `^RR-[0-9A-HJKMNP-TV-Z]{8}$`, hạn 15 phút, rate limit 5 lần/chat/giờ đều PROVISIONAL. Đọc từ settings/hợp đồng, không hard-code như đã chốt. |
| `SG-03` | `CR-PC07-05` còn OPEN: `telegram_update_max_age` PROVISIONAL 24 giờ. |
| `SG-04` | `CR-PC07-03` còn OPEN: quy tắc so sánh constant-time cho webhook secret chưa nằm trong openapi. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-owner-auth-session`
- `TC-saved-snapshot`
- `TC-scheduler-lease-claim`

## §12. Reviewer scope

Reviewer đọc `contracts/telegram/commands.yaml` (allowlist + EDGE-01…07), 7 fixture telegram/*. Câu hỏi bắt buộc: có đường nào một chat chưa liên kết gây ra mutation hoặc nhận phản hồi không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-telegram-linking-auth`
- **Vị trí:** `evidence/runs/TC-telegram-linking-auth/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
