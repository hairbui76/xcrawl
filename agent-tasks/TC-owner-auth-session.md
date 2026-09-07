---
card_id: TC-owner-auth-session
title_vi: Phiên owner: cookie AND CSRF, và từ chối token đi sai cạnh
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M1
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-auth-service]
scenario_refs: [SC17, SC40, SC41, SC39, SC49, SC51]
invariant_refs: [I01, I11]
evidence_manifest_id: EVM-TC-owner-auth-session
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-owner-auth-session — Phiên owner: cookie AND CSRF, và từ chối token đi sai cạnh

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P3b-20260908`** (thay `PC10-PIN-P3-20260908`; các epoch cũ hơn: `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

**`dispatch_status: DISPATCHED (OD-20260907-02, 2026-09-07)`** — Owner đã ra lệnh bắt đầu Giai đoạn 1 và cấp G5 entry cho bốn card M1 (`OD-20260907-02` mục 2: `TC-ingest-idempotent-ack-lost`, `TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness`). Dòng này chỉ ghi **trạng thái điều phối**. Nội dung nghĩa vụ của card **không đổi**: §1–§13 giữ nguyên từng chữ qua các lần pin lại `PC10-PIN-P1-20260907`, `PC10-PIN-P1b-20260907`, `PC10-PIN-P1c-20260907`, `PC10-PIN-P1d-20260907` `PC10-PIN-P2-20260907` `PC10-PIN-P2b-20260907` `PC10-PIN-P2c-20260907` `PC10-PIN-P2d-20260907` `PC10-PIN-P3-20260908` và `PC10-PIN-P3b-20260908`; thứ duy nhất đổi ở những lần pin đó là các hàng hash trong bảng dưới. Quyền thi công vẫn do TASK_PACKET của Coordinator mở (lease + write set), không do dòng này; mọi điểm dừng ở §10 vẫn nguyên hiệu lực và trần claim vẫn như front-matter khai.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `da5181b2888674134f6e3919ce401014015f223ea46a967d9fda3833c01a037b` | 22685 |
| `precode/baseline.json` | `52af62c8b11e6939a9a34798bd71b4a4e688d8ed85d9c579ee1858ed341037e9` | 124824 |
| `precode/decision-register.md` | `b26cf51a0d7c73661ab465e5a157aaad7a9ceb6f013926abd5117f6966764a7e` | 182028 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `ebcf460fa2e415cc6897cdbe7cee144bda9368e4a5af9cd514ec676224399936` | 241542 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `contracts/ops/secrets.md` | `14b3d8988a9de21bf70de076c2b85a21b3e87394c493f18082af51c191690ee9` | 25301 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/ui/screens.yaml` | `e1a57407c0733aa709b464b61da3313f0f6109f5696bd8b39b7e77fc5d5d9074` | 51212 |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | `aa91b92d087681b3df902091bbe5d875e644fee6b2e08e53025ba97136eb6317` | 6406 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
| `acceptance/fixtures/recovery/README.md` | `982311e721d8e9e740f51ae011c557c363ba3d0de8151dd0643755ecb926dac8` | 12235 |
| `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json` | `32883c7a2a12b36d964f7974c45952e731f2330cc1416b43c9e4895ae1ad5119` | 4024 |
| `acceptance/fixtures/recovery/i-collector-token-calls-save.json` | `78e6e6ee47008b5d9b44dbdf65994f93c7ce89ee33ef7f96e7699ee7e0372886` | 5229 |
| `acceptance/fixtures/recovery/g-ssrf-redirect-private.json` | `d5973052f973b738a66c926d98d662e2bb821e7de7e938acbf040f5328dec2ec` | 3265 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/ui/README.md` | `c7ac5d304c33ff48228f5256ac2e56e097eb20121a6648ee4cca431041670dce` | 6380 |
| `acceptance/fixtures/ui/sc51-first-time-setup.json` | `19820cec74bb3a73dd9945674ce3dd88fd9d18f1d15ae0b48ebef938b92f18d7` | 13282 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-owner-auth-session`
- **Milestone:** M1 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-auth-service`

**Mục tiêu.** Mọi mutation của owner cần **cả** cookie phiên **và** CSRF token; request thiếu xác thực bị từ chối trước khi chạm domain; token của collector/worker đi vào cạnh không được phép bị từ chối.

**Non-goals.**

- Không thiết kế lại security scheme — `contracts/http/openapi.yaml` (post-FIX1) là nguồn chuẩn.
- Không viết UI (card 16, 17).
- Không xử lý backup token (card 15).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md`, `precode/adr/ADR-0001-topology-and-placement.md`.
3. Hợp đồng nghiệp vụ: `contracts/http/openapi.yaml`, `contracts/ops/secrets.md`, `contracts/ops/internet-boundary.md`, `contracts/capabilities.yaml`, `contracts/ui/screens.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`, `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `acceptance/fixtures/recovery/g-ssrf-redirect-private.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc51-first-time-setup.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/auth/service.py` | login / logout / get_session |
| `server/app/auth/csrf.py` | double-submit: header `X-CSRF-Token` khớp cookie `rr_csrf` |
| `server/app/auth/middleware.py` | áp scheme theo `openapi.yaml`; deny mặc định |
| `server/app/auth/router.py` | HTTP handler `auth.*` |
| `tests/contract/test_auth_scheme_matrix.py` | mọi route mutation owner có cookie AND CSRF |
| `— (nửa trình duyệt của CSRF **không** thuộc card này)` | đọc cookie `rr_csrf` và gắn header `X-CSRF-Token` là việc của `web/src/lib/api.ts`, do card `TC-ui-runs-three-states` / `TC-ui-reports-detail` sở hữu (Stack B) |
| `tests/integration/test_denied_edges.py` | NC-01, NC-02: token đi sai cạnh |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `auth.login`
- `auth.logout`
- `auth.get_session`

**Consumes** (chỉ được gọi đúng những operation này):

- `storage.get_health`

**Schema:**

- security schemes → `contracts/http/openapi.yaml`

**State effects.** `ENT-session`, `ENT-owner`. `CSRF_REJECTED` **không** hủy phiên (mô tả của scheme `ownerCsrfToken`).

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-web-ui` — owner_session; `auth.login` là `public_login`

**Được phép gọi:**

- MOD-data-store

**Đường bị cấm (denied paths):**

- `collectorToken` chỉ mở `worker.*` và `ingest.*`; gọi `save.create` ⇒ 401 (NC-01).
- `analysisWorkerToken` chỉ mở `analysis.*` và `secret.issue_task_credential`; không mở tag/report/Saved (NC-02).
- `backupOperatorToken` là scheme **duy nhất** cho mọi route `backup.*`; phiên trình duyệt **không** qua được (CR-PC08-02).
- Không có route nào của owner nhận cookie một mình cho mutation.

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
| `I01` | dữ liệu authoritative chỉ mutation qua domain port đã xác thực |
| `I11` | nội dung không đọc secret |

**Transaction và commit point:**

- Không có transaction nghiệp vụ; điểm kiểm là middleware trước khi vào domain.

**Race, replay và forbidden effects:**

- Phiên hết hạn giữa hai request ⇒ 401, không mutation một phần.
- CSRF lệch ⇒ 403 `CSRF_REJECTED`, phiên vẫn còn.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `UNAUTHORIZED` | 401 — thiếu/không hợp lệ xác thực; **cũng** là mã cho 'token hợp lệ nhưng đi cạnh không được phép' theo NC-01/NC-02 (xem stop condition SG-01) |
| `CSRF_REJECTED` | 403 — cạnh hợp lệ nhưng lời gọi không chứng minh được do trang của ứng dụng phát ra; **không** phải `FORBIDDEN_EDGE` |
| `FORBIDDEN_EDGE` | cạnh caller→callee không có trong `contracts/modules.yaml` |
| `VALIDATION_ERROR` | 400 |
| `STORAGE_WRITE_FAILED` | không ghi session |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC17
- SC40
- SC41
- SC39
- SC49
- SC51

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_auth_scheme_matrix.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_denied_edges.py -q` (PROVISIONAL)
- Validator OpenAPI 3.1 trên `contracts/http/openapi.yaml` — **NOT_RUN** (chưa có validator nào chạy ở Pre-code)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `h-unauthenticated-owner-api.json`: 0 hàng domain thay đổi; mã trả về đúng như hợp đồng.
- Fixture `i-collector-token-calls-save.json`: `save.create` bằng `collectorToken` ⇒ 401, `COUNT(saved_item)` không đổi.
- Ma trận scheme: **mọi** operation `mutation: true` với `auth_scope` owner có cả `ownerSessionCookie` và `ownerCsrfToken` trong **một** security requirement.
- Mọi route `backup.*` chỉ chấp nhận `backupOperatorToken`.

**Evidence artifacts:** log pytest; bảng ma trận scheme sinh từ openapi; đếm hàng domain trước/sau.

**Yêu cầu live.** Không cần live.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 4 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/http/openapi.yaml`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/ui/screens.yaml`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-CSRF` | **`CSRF_REJECTED` là 403 và KHÔNG hủy phiên** (ruling R5-01, hàng 4). Nó khác `FORBIDDEN_EDGE`: cạnh vẫn hợp lệ, chỉ lời gọi không chứng minh được là do trang của ứng dụng phát ra. Dùng `FORBIDDEN_EDGE` cho thiếu CSRF là FAIL. `CR-PC08-04` nay đã đóng bằng bảng R5-01: token đi sai cạnh qua HTTP là `UNAUTHORIZED` (401). |
| `SG-01` | **`CR-PC08-04` còn OPEN**: chưa chốt **một** mã cho 'token hợp lệ nhưng đi cạnh không được phép'. `contracts/modules.yaml` NC-01/NC-02 và oracle của `UNAUTHORIZED` nói `UNAUTHORIZED`; nếu `acceptance/scenarios.yaml` của PC09 nói khác ⇒ DỪNG, raise CR, không tự chọn. |
| `SG-02` | **Chưa validator OpenAPI 3.1 nào được chạy** trên `contracts/http/openapi.yaml` trong Pre-code. Trước khi code, chạy validator và báo mọi sai lệch như CR; không sửa openapi. |
| `SG-03` | Secret không bao giờ vào repo (SRC-SPEC §11.2). Nếu test cần secret thật ⇒ DỪNG. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- Không phụ thuộc card nào.
- Là dependency của mọi card có `auth_scope: owner_session`.

## §12. Reviewer scope

Reviewer đọc `contracts/http/openapi.yaml` `securitySchemes` + `contracts/modules.yaml` NC-01…NC-10, 3 fixture recovery/*. Câu hỏi bắt buộc: có route mutation nào của owner chấp nhận cookie một mình không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-owner-auth-session`
- **Vị trí:** `evidence/runs/TC-owner-auth-session/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
