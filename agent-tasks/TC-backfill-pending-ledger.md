---
card_id: TC-backfill-pending-ledger
title_vi: Backfill N ngày và sổ pending độc lập con trỏ kỳ
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-report-service, MOD-tag-service]
scenario_refs: [SC05, SC22, SC37, SC38, SC49]
invariant_refs: [I06, I07]
evidence_manifest_id: EVM-TC-backfill-pending-ledger
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-backfill-pending-ledger — Backfill N ngày và sổ pending độc lập con trỏ kỳ

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P3b-20260908`** (thay `PC10-PIN-P3-20260908`; các epoch cũ hơn: `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

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
| `contracts/reporting/time-and-tags.md` | `70f4bc57a0fa2733d92136194eb4d563fa5d9145726141ee30493fe3a2b1a66c` | 61837 |
| `contracts/reporting/selection.md` | `781effb61be2865a07fa3be4373196229bb6bd89048abbb943d646ca95401fe4` | 37357 |
| `contracts/state/report.yaml` | `77969cb473c84a7df90e6b784ad1afa637313e813ccbb59d99b1ea329241245f` | 30187 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `4c02d39a2d6ef80f17db7f1aebbda1de39bacaa9b4d417a3c2721c10b6ccf21f` | 5903 |
| `acceptance/fixtures/reporting/README.md` | `cdb2008913f53562ec41fe7ed179c3c17d3a568ee9d5dc8027e16405dcf2b54f` | 16228 |
| `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json` | `ed7395620db5bd1b569bd087590b02e9b7cd5dbd06add2822d64ddd24f5a83b4` | 10989 |
| `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json` | `b074e9f353e4b9646cdf58c88864e1677b86adccdff1b38ab049cbc5e9a4cd4a` | 6842 |
| `acceptance/fixtures/reporting/k-builder-crash-backfill-not-consumed.json` | `9fce157821143ef6d852a688e033424d8f4191dbedfb47caaa80d9ba9a3b6f82` | 5879 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-backfill-pending-ledger`
- **Milestone:** M4 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-report-service`, `MOD-tag-service`

**Mục tiêu.** Tag mới tiêu thụ backfill N ngày **đúng một lần** trên một subscription activation; mục thiếu analysis được ghi pending độc lập và xuất hiện ở kỳ sau với nhãn phát hiện muộn; builder crash **không** tiêu thụ backfill.

**Non-goals.**

- Không viết publish CAS (card 8).
- Không chốt N = 7 ngày như đã quyết định — đó là PROVISIONAL (REQ-OQ04).
- Không reset first-announcement khi quét lại kho.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0004-tag-freeze-point.md`.
3. Hợp đồng nghiệp vụ: `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/state/report.yaml`, `contracts/data/entities.yaml`, `contracts/http/openapi.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/e-late-analysis-pending-then-late-discovery.json`, `acceptance/fixtures/reporting/j-backfill-add-remove-readd.json`, `acceptance/fixtures/reporting/k-builder-crash-backfill-not-consumed.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/report/backfill.py` | `ENT-backfill-ledger`, entitlement, add–remove–readd |
| `server/app/report/pending.py` | `ENT-pending-item-ledger`, phát hiện muộn |
| `server/app/tags/rescan.py` | `tag.rescan_corpus` với `ENT-rescan-ledger` riêng |
| `tests/integration/test_backfill_once.py` | add → remove → re-add |
| `tests/integration/test_pending_survives_cursor.py` | con trỏ tiến, pending không mất |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `tag.create`
- `tag.update`
- `tag.delete`
- `tag.rescan_corpus`
- `tag.preview_matches`
- `tag.list`

**Consumes** (chỉ được gọi đúng những operation này):

- `report.build`
- `analysis.enqueue_tasks`
- `embedding.generate_vectors`
- `embedding.get_active_generation`

**Schema:**

- report items và nhãn phát hiện muộn → `contracts/schemas/report.schema.json`

**State effects.** `ENT-backfill-ledger` mang `subscription_identity_hash`, `entitlement`, `entitlement_reason` và `consumed_in_report_id` (`CR-PC04-02`, còn OPEN). `ENT-pending-item-ledger` độc lập với con trỏ kỳ. `tag.rescan_corpus` có ledger riêng, **không** reset first-announcement hay coverage chính.

**Cột thêm ở `PC10-PIN-FCW4d-20260907`** (giữ nguyên ở `FCW4e`) — oracle của card này chạm các entity sau, và `contracts/data/entities.yaml` đã thêm cột cho chúng ở wave FIX7: `ENT-report` (abort_reason, selection_version); `ENT-tag` (removed_at). Oracle ở §8 **không đổi** — không oracle nào của card đang gọi tên một cột bị đổi nghĩa; các cột mới là bổ sung (additive) và mở rộng phần chứng minh được, không thay phần đã có. Đọc bảng cột hiện hành trong `entities.yaml` trước khi viết assertion.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-web-ui` — owner_session + CSRF cho `tag.*` mutation
- `MOD-report-service` — internal cho tiêu thụ backfill

**Được phép gọi:**

- MOD-embedding-service
- MOD-analysis-service
- MOD-data-store

**Đường bị cấm (denied paths):**

- Không tiêu thụ backfill chỉ vì builder crash hoặc model lỗi (SRC-PLAN §9.2).
- Không gộp ledger quét lại kho vào coverage chính.

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
| `I06` | pending item không mất khi con trỏ tiến |
| `I07` | không reset first-announcement |

**Transaction và commit point:**

- Tiêu thụ backfill nằm **trong** `TXN-report-publish`: chỉ đánh dấu consumed khi publish commit thành công.

**Race, replay và forbidden effects:**

- Add → remove → re-add: phải chốt đó có phải activation mới không; hiện là quy tắc trong `contracts/reporting/time-and-tags.md`, thực thi ở mức schema cần `CR-PC04-02`.
- Builder crash giữa build và publish ⇒ backfill vẫn `unconsumed` (fixture `k`).
- Analysis về muộn sau khi kỳ đã đóng ⇒ mục vào kỳ sau với nhãn phát hiện muộn (fixture `e`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `VALIDATION_ERROR` | 400 |
| `UNAUTHORIZED / CSRF_REJECTED` | 401/403 |
| `NOT_FOUND` | tag không tồn tại |
| `IDEMPOTENCY_CONFLICT` | rescan/tag trùng key |
| `EMBEDDING_GENERATION_MISMATCH` | `tag.create` chặn khi generation đang rebuild |
| `STORAGE_WRITE_FAILED` | không ghi ledger |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC05
- SC22
- SC37
- SC38
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/integration/test_backfill_once.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_pending_survives_cursor.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `j`: sau add → remove → re-add, `COUNT(backfill_ledger WHERE consumed_in_report_id IS NOT NULL)` đúng bằng số activation hợp lệ theo `time-and-tags.md` — không hơn.
- Fixture `k`: sau crash, backfill vẫn `unconsumed`; publish lần sau mới tiêu thụ.
- Fixture `e`: mục pending xuất hiện ở kỳ sau với `late_discovery = true`, **không** bị bỏ.
- `tag.rescan_corpus` không đổi bất kỳ hàng `first_announced_ledger` nào.

**Evidence artifacts:** log pytest; dump `backfill_ledger` + `pending_item_ledger`.

**Yêu cầu live.** Không cần live.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Phạm vi đã phê chuẩn** (`OD-20260907-01`). Read set của card này nằm trong bốn phạm vi mà A2-R4 xác định đủ điều kiện — *ranh giới và quyền*, *dữ liệu và định danh*, *workflow và trạng thái*, *báo cáo và thời gian* — và không chạm `contracts/ai/`, `contracts/telegram/`, hay bất kỳ file `contracts/ops/` nào ngoài `deployment.md` (file này đã lên `CONTRACT_READY` ở PC01-FIX13). 17 blocker B01–B17 nay là `RATIFIED`, nên điểm dừng dạng *"B0x còn PROVISIONAL"* đã gỡ khỏi §10.

  **Nhưng nền hợp đồng CHƯA đồng nhất `CONTRACT_READY`.** 1 file hợp đồng trong read set của card này vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW` trong chính header của nó: `contracts/http/openapi.yaml`. Vì vậy **không** được đọc mục này là "mọi hợp đồng đã sẵn sàng"; hãy đọc là "phạm vi nghiệp vụ đã được phê chuẩn, và 1 file còn lại phải lên `CONTRACT_READY` trước khi claim của card vượt quá `IMPLEMENTATION_VERIFIED`". Kiểm lại bằng `grep -h claim_ceiling <file>` — đừng tin dòng này.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC04-02` còn OPEN: `backfill_ledger` chưa có `subscription_identity_hash` / `entitlement` / UNIQUE tương ứng ⇒ quy tắc add–remove–readd **chưa thực thi được ở mức schema**. Không tự thêm cột; DỪNG. |
| `SG-02` | `CR-PC04-07` (UI hiện số mục ước tính trước `tag.rescan_corpus`) còn OPEN — không chặn card, nhưng không được bật rescan mặc định. |
| `SG-03` | N = 7 ngày nay là **giá trị làm việc được Owner chấp nhận** (`OD-20260907-01` mục 20). Vẫn đọc từ settings, không hard-code. |
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

## §12. Reviewer scope

Reviewer đọc `contracts/reporting/time-and-tags.md` phần backfill, fixture `e`/`j`/`k`. Câu hỏi bắt buộc: có đường nào backfill bị tiêu thụ hai lần, hoặc pending bị mất, không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-backfill-pending-ledger`
- **Vị trí:** `evidence/runs/TC-backfill-pending-ledger/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
