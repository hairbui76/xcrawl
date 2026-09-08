---
card_id: TC-ui-reports-detail
title_vi: UI Reports và Report detail: cùng revision phân tích, có provenance
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED cho read model và nhãn provenance. Chất lượng nội dung là E4.
owner_modules: [MOD-web-ui]
scenario_refs: [SC09, SC10, SC11, SC15, SC49]
invariant_refs: [I04, I05, I07, I13]
evidence_manifest_id: EVM-TC-ui-reports-detail
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-ui-reports-detail — UI Reports và Report detail: cùng revision phân tích, có provenance

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P4b-20260908`** (thay `PC10-PIN-P4-20260908`; các epoch cũ hơn: `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. **`P4`** pin sau `PKT-PC00-FIX30` (`OD-20260908-10`) — lần ghi `precode/` cuối của vòng này. Đợt sửa Giai đoạn 4/6 chạy song song chỉ chạm code, test, handoff và manifest: **không** file nào trong số đó được card pin, nên chúng không tạo ra một lần pin lại. **`P4b`** pin sau `PKT-PC00-FIX32`: `precode/adr/ADR-0011-frameworks-and-toolchain.md` được sửa (phạm vi `mypy`, `CR-PC00-35`). `ADR-0011` nằm trong read set của **mọi** card, nên một mình nó đủ làm cả 19 card `STALE`. Gói song song chỉ chạm bộ file dựng gói (pyproject, uv lockfile), workflow CI, Makefile, .gitignore và một test smoke của server — **không** file nào trong số đó được card pin hay trích dẫn, đã kiểm trực tiếp. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` | 27451 |
| `precode/baseline.json` | `e8cf3910c6f2351a2c7c4a8620121b0415a58c5c7ec86eee7ba5d33c343c1a70` | 127222 |
| `precode/decision-register.md` | `a38e2ce1a953279b7d1ca0ba6ae2ad52f97886a887f98e596b9ade0f4fdb211b` | 185553 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `ebcf460fa2e415cc6897cdbe7cee144bda9368e4a5af9cd514ec676224399936` | 241542 |
| `contracts/ui/screens.yaml` | `e1a57407c0733aa709b464b61da3313f0f6109f5696bd8b39b7e77fc5d5d9074` | 51212 |
| `contracts/schemas/report.schema.json` | `8bf6bc9ccd6040c06f4ba709ea638e647ab8349e1bac4f26cd6049df76b7ba60` | 32747 |
| `contracts/ai/grounding.md` | `b54cec8b3f9f6a9cb2221daaafe8a61a149d0a6686d0d23dcbf7bf9f17995172` | 15293 |
| `contracts/reporting/selection.md` | `781effb61be2865a07fa3be4373196229bb6bd89048abbb943d646ca95401fe4` | 37357 |
| `contracts/telegram/delivery.md` | `18dc7c175a56efbfd434b63aac603d8408030f5fe68b63046cd83c3c9db8a0e1` | 26044 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | `bbf649f5e9239d0de28c24255469ce0498f9f108bfdd45ada2ddeac859b8f1c5` | 5660 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `4c02d39a2d6ef80f17db7f1aebbda1de39bacaa9b4d417a3c2721c10b6ccf21f` | 5903 |
| `acceptance/fixtures/reporting/README.md` | `cdb2008913f53562ec41fe7ed179c3c17d3a568ee9d5dc8027e16405dcf2b54f` | 16228 |
| `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json` | `99ef5c790806becdf4a3386566d53690ef1d91a77ac416c2f9deacda93085874` | 9789 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | `207e38f9e1c12cca6111f249ebed230bd33993daa69a561210a93e425963d321` | 15344 |
| `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json` | `dc1defe222b82dfae97582216d2251fb35663ff177822b388334789a30c9ddea` | 5694 |
| `acceptance/fixtures/ai/d-schema-valid-but-uncited.json` | `cf4662a1713d11fd4c60698cc416b0637bd1cfbfb35dce3a86b298e26c52bcbe` | 6158 |
| `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json` | `7b588ca0ad1999bacdfa78ffb17ba6f0ad1336e399cb291502397f079168079b` | 7475 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/ui/README.md` | `c7ac5d304c33ff48228f5256ac2e56e097eb20121a6648ee4cca431041670dce` | 6380 |
| `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json` | `5b6e4f52b7558533b0555362fd38cad17ea23bb2349fe6600d08d311b9c5b8d8` | 10455 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-ui-reports-detail`
- **Milestone:** M4 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-web-ui`

**Mục tiêu.** Reports, Report detail và Work detail hiển thị đúng revision phân tích mà Telegram digest dùng, tách `author_claim` / `source_verified` / `ai_inference`, hiện `discovered_at` và `analyzed_at`, và đánh dấu reference lịch sử có ngày thay vì phát hiện mới.

**Non-goals.**

- Không viết report builder (card 8).
- Không thêm nút export Saved (hoãn P1).
- Không tự diễn giải kết quả AI thành khẳng định đã kiểm chứng.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0008-analysis-key-and-generation.md`, `precode/adr/ADR-0004-tag-freeze-point.md`.
3. Hợp đồng nghiệp vụ: `contracts/ui/screens.yaml`, `contracts/schemas/report.schema.json`, `contracts/ai/grounding.md`, `contracts/reporting/selection.md`, `contracts/telegram/delivery.md`, `contracts/http/openapi.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/h-already-announced-work-becomes-reference.json`, `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `acceptance/fixtures/ai/a-post-only-summary-inference-labelled.json`, `acceptance/fixtures/ai/d-schema-valid-but-uncited.json`, `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/ui/README.md`, `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `web/src/lib/api.ts` | client HTTP sinh từ `contracts/http/openapi.yaml` (dùng chung với `TC-ui-runs-three-states`; chỉ một card được tạo file, card sau mở rộng) |
| `web/src/lib/provenance.ts` | kiểu cho ba loại phát biểu `author_claim | source_verified | ai_inference` và `comparator: unknown` |
| `web/src/routes/reports.ts` | read model `SCR-reports` |
| `web/src/routes/reportDetail.ts` | read model `SCR-report-detail` |
| `web/src/routes/workDetail.ts` | read model `SCR-work-detail` |
| `web/src/views/ReportDetail.tsx` | nhãn evidence level và provenance |
| `web/tests/contract/reportReadModel.test.ts` | cùng revision với payload Telegram |
| `web/tests/integration/provenanceLabels.test.ts` | author_claim / source_verified / ai_inference |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces:** không operation nào. Card này là **caller**, không sở hữu operation trong `contracts/ports.yaml`.

**Consumes** (chỉ được gọi đúng những operation này):

- `report.list`
- `report.get`
- `work.get_detail`
- `save.create`
- `save.remove`
- `save.list`
- `analysis.request_reanalysis`

**Schema:**

- report và item → `contracts/schemas/report.schema.json`
- read model → `contracts/ui/screens.yaml`

**State effects.** Chỉ đọc, trừ `save.create`/`save.remove`/`analysis.request_reanalysis` (owner_session + CSRF).

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-report` (abort_reason, selection_version). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được phép gọi:**

- MOD-report-service
- MOD-identity-service
- MOD-saved-service
- MOD-analysis-service

**Đường bị cấm (denied paths):**

- Không truy cập SQLite trực tiếp.
- Không hiển thị `ai_inference` như thể là `source_verified` (B16).
- Không bịa comparator: thiếu ⇒ `comparator: unknown` (B16).

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
| `I04` | analysis hợp lệ bất biến theo generation |
| `I05` | report giữ tag version và evidence references |
| `I07` | reference lịch sử có ngày, không tính là phát hiện mới |
| `I13` | phân biệt thiếu dữ liệu với không có kết quả |

**Transaction và commit point:**

- Không có transaction.

**Race, replay và forbidden effects:**

- Reanalysis chạy trong lúc đang xem ⇒ view hiện generation đang active, có nhãn thời điểm.
- Report đã publish **không** đổi nội dung dù tag đổi sau đó (B01).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `UNAUTHORIZED` | về `SCR-login` |
| `NOT_FOUND` | 404 view |
| `CSRF_REJECTED` | 403, không đăng xuất |
| `STORAGE_WRITE_FAILED` | banner 'chưa lưu được' |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC09
- SC10
- SC11
- SC15
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `npm --prefix web run typecheck` (PROVISIONAL — TypeScript, Stack B)
- `npm --prefix web run test -- reportReadModel` (PROVISIONAL)
- `npm --prefix web run test -- provenanceLabels` (PROVISIONAL)
- Render review desktop / mobile / Telegram — thủ công, ghi vào evidence manifest

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- AC-10: payload app và payload Telegram cùng `analysis_revision`; so sánh trường-với-trường, không so văn bản.
- AC-11: item chỉ có post ⇒ evidence level `post-only`; mọi claim có provenance; thiếu comparator ⇒ `comparator: unknown`.
- Fixture `h`/`i`: work đã announced hiện là **reference có ngày**, không nằm trong mục phát hiện mới.
- `analyzed_at` và `discovered_at` cùng hiển thị (`CR-PC06-05`).

**Evidence artifacts:** log pytest; diff payload app ↔ Telegram; ảnh chụp render; biên bản human groundedness review.

**Yêu cầu live.** Groundedness review là E4 theo rubric ở `contracts/ai/grounding.md` §6; cần người đánh giá thật.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED cho read model và nhãn provenance. Chất lượng nội dung là E4.`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ai/grounding.md`, `contracts/telegram/delivery.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 4 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ai/grounding.md`, `contracts/http/openapi.yaml`, `contracts/telegram/delivery.md`, `contracts/ui/screens.yaml`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC06-05` còn OPEN: Settings phải nói rõ đổi provider/model chỉ áp dụng cho phân tích **mới**. Nếu màn hình Settings chưa có câu đó ⇒ raise CR, không tự viết chính sách mới. |
| `SG-02` | `CR-PC04-05` còn OPEN: task `direction_phrasing` chỉ **diễn đạt lại** object đã tính; UI không được để AI chọn thành viên hay đổi nhãn. |
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
- `TC-analysis-once-per-generation`
- `TC-saved-snapshot`
- `TC-owner-auth-session`

## §12. Reviewer scope

Reviewer đọc `contracts/ai/grounding.md`, `contracts/schemas/report.schema.json`, `contracts/ui/screens.yaml` ba màn hình. Câu hỏi bắt buộc: người đọc có phân biệt được suy luận của AI với dữ kiện đã kiểm chứng không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-ui-reports-detail`
- **Vị trí:** `evidence/runs/TC-ui-reports-detail/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
