---
card_id: TC-ui-runs-three-states
title_vi: UI Runs: ba trạng thái rỗng / giới hạn / lỗi phải khác nhau
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4 → M7
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED cho read model. Đánh giá trải nghiệm là E4, ngoài phạm vi.
owner_modules: [MOD-web-ui]
scenario_refs: [SC03, SC04, SC15, SC20, SC26, SC49]
invariant_refs: [I13, I09]
evidence_manifest_id: EVM-TC-ui-runs-three-states
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-ui-runs-three-states — UI Runs: ba trạng thái rỗng / giới hạn / lỗi phải khác nhau

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
| `contracts/ui/screens.yaml` | `464579a807e00e44c3215cf9fbf243df4a2bef8db6e137d71a2409fe6bc6b854` | 51212 |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` | 95222 |
| `contracts/state/delivery.yaml` | `318789179ec79a4e21939a82d4fb78bfb3cd257ed7c3af4c519bf2ab631ee807` | 29542 |
| `contracts/state/storage.yaml` | `a77803f1690ee7749ccc79c9dbee538288a1e7797d318d206e900d50bbd52849` | 29908 |
| `contracts/http/openapi.yaml` | `a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d` | 231727 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `70fcac8f9c7fdcdce84889015d31f109d423d1d15d68116165e9e3d0612399f8` | 5368 |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | `567828c11049d26993cbeee0d0bd6c157d9938263ec69c5a05fa045da3ceb0e3` | 5549 |
| `acceptance/fixtures/collection/README.md` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 12636 |
| `acceptance/fixtures/collection/e-limit-reached-stop.json` | `ce13e459e9e82755ab6b25f01b1e5e77e76f9a4f073ee7b69e2ab5eb9364c34e` | 7892 |
| `acceptance/fixtures/collection/c-challenge-mid-batch.json` | `b4330c7e473779279ba545f0ecb6d9cd8f2a811beb0bae7310c62ff5dcf7e16b` | 12528 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | `2b3a6cd3ed2a3a5441a6854038020db17e6dbe736c941df6f1d7d5b1adb2c25e` | 8879 |
| `acceptance/fixtures/telegram/m-three-run-states-distinct-text.json` | `950b336ba3eb0dad18287ec273430235d8e125278fa332cabece5d7e19af33e2` | 4599 |
| `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json` | `10d7c4deccdb95a7fcc1b02033ff90a785ce881d79e4f8ba6d0d648f109ef215` | 5047 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-ui-runs-three-states`
- **Milestone:** M4 → M7 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-web-ui`

**Mục tiêu.** Màn hình Runs và Run detail hiển thị **khác nhau** cho: kỳ rỗng, dừng vì giới hạn, và thất bại thu thập; cộng thêm `needs_user`, `blocked` và delivery `unknown` — không gộp thiếu dữ liệu thành 'không có nghiên cứu'.

**Non-goals.**

- Không viết backend (card 3, 8, 12).
- Không thêm hành động ngoài `contracts/ui/screens.yaml`.
- Không gọi SQLite trực tiếp.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0002-run-state-model-split.md`, `precode/adr/ADR-0003-delivery-unknown-state.md`.
3. Hợp đồng nghiệp vụ: `contracts/ui/screens.yaml`, `contracts/state/run.yaml`, `contracts/state/delivery.yaml`, `contracts/state/storage.yaml`, `contracts/http/openapi.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/e-limit-reached-stop.json`, `acceptance/fixtures/collection/c-challenge-mid-batch.json`, `acceptance/fixtures/reporting/d-empty-period-coverage-only.json`, `acceptance/fixtures/telegram/m-three-run-states-distinct-text.json`, `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `web/src/lib/api.ts` | client HTTP sinh từ `contracts/http/openapi.yaml`; gắn cookie phiên + header `X-CSRF-Token` cho mọi mutation |
| `web/src/lib/runState.ts` | kiểu TypeScript cho bộ ba `(status, outcome, stop_reason)` và ánh xạ state → nhãn hiển thị |
| `web/src/routes/runs.ts` | read model cho `SCR-runs` |
| `web/src/routes/runDetail.ts` | read model cho `SCR-run-detail` |
| `web/src/views/RunsList.tsx` | ba trạng thái có văn bản khác nhau |
| `web/src/views/RunDetail.tsx` | needs_user / blocked / delivery unknown |
| `web/tests/contract/runReadModel.test.ts` | ánh xạ state → view |
| `web/tests/integration/threeStatesDistinct.test.ts` | ba chuỗi hiển thị khác nhau |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces:** không operation nào. Card này là **caller**, không sở hữu operation trong `contracts/ports.yaml`.

**Consumes** (chỉ được gọi đúng những operation này):

- `run.list`
- `run.get`
- `run.run_now`
- `run.resume`
- `run.cancel`
- `worker.get_status`
- `delivery.get_status`
- `delivery.decide_unknown`
- `health.get_readiness`

**Schema:**

- read model và action map → `contracts/ui/screens.yaml`

**State effects.** UI **không** ghi state ngoài các operation ở §4. `run.resume` là hành động app riêng (B10); `run.run_now` không ghi đè `needs_user`.

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-run` (observed_window_from, observed_window_to, posts_observed_total, posts_ingested_new, limit_hit, limit_kind, cursor_invalidated, x_coverage_note_vi, rate_limited_at); `ENT-delivery` (telegram_link_generation); `ENT-delivery-part` (provider_message_id); `ENT-worker-registration` (online_state, last_run_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được phép gọi:**

- MOD-job-service
- MOD-delivery-service
- MOD-health-service

**Đường bị cấm (denied paths):**

- Web UI **không** truy cập SQLite trực tiếp, không mở worker debug port, không gọi Telegram/AI bằng secret (SRC-PLAN §6).
- Không hiển thị 'không có nghiên cứu mới' khi thật ra là thiếu dữ liệu hoặc lỗi (I13).

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
| `I13` | incomplete / empty / failed / unknown hiển thị riêng |
| `I09` | Telegram thất bại không làm run thành thất bại thu thập |

**Transaction và commit point:**

- Không có transaction. Mọi mutation đi qua operation ở §4 với owner_session + CSRF.

**Race, replay và forbidden effects:**

- Trạng thái đổi giữa lúc render ⇒ hiển thị last-known có nhãn rõ ràng, không suy diễn.
- `storage.write_blocked` ⇒ UI phải phân biệt last-known với 'chưa lưu được' (SRC-PLAN §8.4).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `UNAUTHORIZED` | chuyển về `SCR-login` |
| `CSRF_REJECTED` | báo lỗi, **không** đăng xuất người dùng |
| `NOT_FOUND` | 404 view |
| `STORAGE_WRITE_FAILED` | banner 'chưa lưu được', không nói đã lưu |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC03
- SC04
- SC15
- SC20
- SC26
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `npm --prefix web run typecheck` (PROVISIONAL — TypeScript, Stack B)
- `npm --prefix web run test -- runReadModel` (PROVISIONAL)
- `npm --prefix web run test -- threeStatesDistinct` (PROVISIONAL)
- Render review trên desktop và mobile — thủ công, ghi vào evidence manifest

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Ba trạng thái (rỗng, giới hạn, thất bại) cho **ba chuỗi hiển thị khác nhau**; so sánh chuỗi, không so ảnh (fixture `m-three-run-states-distinct-text.json`).
- `needs_user` hiện hành động resume; `blocked` hiện điều kiện gỡ chặn, **không** hiện resume.
- Delivery `unknown` hiện là 'chưa xác định' và có hành động `delivery.decide_unknown`; không hiện là 'đã gửi' hay 'thất bại'.
- Mọi hành động trên màn hình đều có trong action map của `contracts/ui/screens.yaml`.

**Evidence artifacts:** log pytest; ảnh chụp render desktop/mobile; bảng state → chuỗi hiển thị.

**Yêu cầu live.** Render review là human review; ghi rõ ai review và khi nào (SRC-PLAN §14.1 `review_type`).

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED cho read model. Đánh giá trải nghiệm là E4, ngoài phạm vi.`.**

**Phạm vi đã phê chuẩn** (`OD-20260907-01`). Read set của card này nằm trong bốn phạm vi mà A2-R4 xác định đủ điều kiện — *ranh giới và quyền*, *dữ liệu và định danh*, *workflow và trạng thái*, *báo cáo và thời gian* — và không chạm `contracts/ai/`, `contracts/telegram/`, hay bất kỳ file `contracts/ops/` nào ngoài `deployment.md` (file này đã lên `CONTRACT_READY` ở PC01-FIX13). 17 blocker B01–B17 nay là `RATIFIED`, nên điểm dừng dạng *"B0x còn PROVISIONAL"* đã gỡ khỏi §10.

  **Nhưng nền hợp đồng CHƯA đồng nhất `CONTRACT_READY`.** 2 file hợp đồng trong read set của card này vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW` trong chính header của nó: `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml`. Vì vậy **không** được đọc mục này là "mọi hợp đồng đã sẵn sàng"; hãy đọc là "phạm vi nghiệp vụ đã được phê chuẩn, và 2 file còn lại phải lên `CONTRACT_READY` trước khi claim của card vượt quá `IMPLEMENTATION_VERIFIED`". Kiểm lại bằng `grep -h claim_ceiling <file>` — đừng tin dòng này.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Nếu `contracts/ui/screens.yaml` thiếu một trạng thái mà `contracts/state/run.yaml` có ⇒ DỪNG và raise CR; **không** tự đặt nhãn hiển thị. |
| `SG-02` | `SCR-settings` có phần `OWNER_DECISION_REQUIRED_SCOPE` (TXN-purge-all). Không hiện thực nút purge. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-scheduler-lease-claim`
- `TC-telegram-unknown-delivery`
- `TC-owner-auth-session`
- `TC-storage-write-blocked-readiness`

## §12. Reviewer scope

Reviewer đọc `contracts/ui/screens.yaml` `SCR-runs`/`SCR-run-detail`, `contracts/state/run.yaml` enum, fixture `m`. Câu hỏi bắt buộc: ba trạng thái có thật sự khác chuỗi hiển thị không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-ui-runs-three-states`
- **Vị trí:** `evidence/runs/TC-ui-runs-three-states/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
