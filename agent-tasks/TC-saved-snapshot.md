---
card_id: TC-saved-snapshot
title_vi: Save là snapshot bất biến
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M1 → M6
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-saved-service]
scenario_refs: [SC12, SC13, SC48, SC32, SC49]
invariant_refs: [I08, I17]
evidence_manifest_id: EVM-TC-saved-snapshot
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-saved-snapshot — Save là snapshot bất biến

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
| `contracts/schemas/saved-snapshot.schema.json` | `1178d314deb8dfdfbe24a9bd4645fd0fd34424fa1db0c237971b3dba3705ce3c` | 16298 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `contracts/data/identity.md` | `71fedc7f6996f5eebace1a53ec42b19bb16f0df4489d93a906e5c895bbb4f4fd` | 20610 |
| `contracts/http/openapi.yaml` | `a3e7e42203bdb2c2b3c65a387a52eff62dc339fe198b9c8ca1c8ae22937a838d` | 231727 |
| `contracts/ui/screens.yaml` | `464579a807e00e44c3215cf9fbf243df4a2bef8db6e137d71a2409fe6bc6b854` | 51212 |
| `contracts/telegram/commands.yaml` | `fc1a18dac332ea51e63721536d6a47b1d5a3048ed408af24ae787a91874e3556` | 24834 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | `67844f12e4fe77a6a25b443a8fe84d053fbcfc9c30649296f55efc41befa4ee1` | 6145 |
| `acceptance/fixtures/identity/README.md` | `ce9ec21ec1cebe8a257a677e67097f1883a35c403b4421d3219862d185335e14` | 12611 |
| `acceptance/fixtures/identity/d-concurrent-save-app-telegram.json` | `2b5e250ee3c21cd62e3cd87b42939cc0ed00b7d5167ab43ab67958477432b4ae` | 9604 |
| `acceptance/fixtures/identity/e-source-deleted-snapshot-intact.json` | `c2fd418bf32e5870b304508443144e6637355b81526c393a2f0ead3f445900c5` | 10801 |
| `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json` | `3630edc83719ada07cae9b39f5da7ad8d1894379509c96bb1128cf958ca6ea0b` | 3462 |
| `acceptance/fixtures/telegram/j-concurrent-save-app-telegram.json` | `1df94cec7d7b44998cd07ebb5fd6d493f4d33327f7b3190aa6f0929137b8ff5b` | 8124 |
| `acceptance/fixtures/telegram/k-save-then-source-deleted.json` | `8a27e20ffb5611374b3ff566b78e95fe0e3f621fc05bd4787a2f29c94a82b434` | 7373 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-missing-content-hash.json` | `254528d628f9f5e855650ea15045ba9f8af8d28e48ee96b048399945d6f813de` | 3491 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-bad-hash-format.json` | `2b02188603feda3f9050f74bf8345bc3fd2f28aff39dc2633825b4f80a5bb0ac` | 3505 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-item-without-snapshot.json` | `76454f6e05984d307c91526b844f640bd4dd4ea8140024041ecb2a3ef3308acd` | 3553 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-target-both-ids.json` | `2cd134a69a7e83696c25541664cfb8a554b3fba14e5bec22ddda641a37c2c95d` | 3635 |
| `acceptance/fixtures/telegram/neg-saved-snapshot-summary-missing-limitation.json` | `ff348f509d050cb27435d46203ea8bd77b43a6d8ab0e539bf0d5a474f0968df4` | 3570 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/recovery/k-delete-target-preserves-saved.json` | `0a02102333a7701b92c2b1c5b22032940cc0710d8b5faf98d67181ac16606486` | 8045 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-saved-snapshot`
- **Milestone:** M1 → M6 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-saved-service`

**Mục tiêu.** Save tạo snapshot bất biến của target tại thời điểm lưu; một target có tối đa một Saved active; bỏ tag hoặc bài gốc bị xóa trên X **không** làm mất snapshot; Save từ app và từ Telegram đồng thời chỉ tạo một Saved.

**Non-goals.**

- Không làm export Saved — hoãn P1 (`F-PC00-02`, REQ-OQ10).
- Không viết Telegram adapter (card `TC-telegram-linking-auth`).
- Không xóa dữ liệu gốc (đó là `data.delete_target`, phạm vi riêng).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0009-identity-alias-target-union.md`.
3. Hợp đồng nghiệp vụ: `contracts/schemas/saved-snapshot.schema.json`, `contracts/data/invariants.md`, `contracts/data/identity.md`, `contracts/http/openapi.yaml`, `contracts/ui/screens.yaml`, `contracts/telegram/commands.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/identity/README.md`, `acceptance/fixtures/identity/d-concurrent-save-app-telegram.json`, `acceptance/fixtures/identity/e-source-deleted-snapshot-intact.json`, `acceptance/fixtures/recovery/e-saved-snapshot-hash-preserved.json`, `acceptance/fixtures/telegram/j-concurrent-save-app-telegram.json`, `acceptance/fixtures/telegram/k-save-then-source-deleted.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-missing-content-hash.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-bad-hash-format.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-item-without-snapshot.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-target-both-ids.json`, `acceptance/fixtures/telegram/neg-saved-snapshot-summary-missing-limitation.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/recovery/k-delete-target-preserves-saved.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/saved/service.py` | create / remove / list |
| `server/app/saved/snapshot.py` | canonical JSON + `content_hash` |
| `server/app/saved/router.py` | HTTP handler `save.*` |
| `tests/contract/test_saved_snapshot_schema.py` | 1 pos + 5 neg fixture |
| `tests/integration/test_concurrent_save.py` | app + Telegram đồng thời |
| `tests/integration/test_snapshot_survives_delete.py` | bài gốc bị xóa, restart, restore |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `save.create`
- `save.remove`
- `save.list`

**Consumes** (chỉ được gọi đúng những operation này):

- `identity.resolve_target`
- `storage.get_health`

**Schema:**

- snapshot đã lưu → `contracts/schemas/saved-snapshot.schema.json`
- target union → `contracts/schemas/target.schema.json`

**State effects.** `ENT-saved-item` + `ENT-saved-snapshot`. Snapshot bất biến; `content_hash` tính trên canonical JSON. `save.remove` gỡ Saved active nhưng **không** xóa snapshot (D55, AC-12).

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-web-ui` — owner_session + CSRF
- `MOD-telegram-adapter` — owner_session_or_linked_chat cho `save.create`

**Được phép gọi:**

- MOD-identity-service
- MOD-data-store

**Đường bị cấm (denied paths):**

- `collectorToken` gọi `save.create` ⇒ 401 (denied case NC-01).
- `analysisWorkerToken` **không** mở đường tới Saved (denied case NC-02).
- Identity merge **không** đổi snapshot đã lưu (I17).

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
| `I08` | Save là snapshot bất biến; một target tối đa một Saved active; bỏ tag không xóa snapshot |
| `I17` | merge không đổi snapshot lịch sử |

**Transaction và commit point:**

- `TXN-save-target` — tạo `saved_item` + `saved_snapshot` trong một commit; UNIQUE trên (owner, target) khi active.

**Race, replay và forbidden effects:**

- Save từ app và từ Telegram cùng lúc ⇒ đúng một Saved, cả hai đường nhận phản hồi nhất quán (fixture `d`, `j`).
- Callback Telegram lặp ⇒ không tạo Saved thứ hai (fixture `f-stale-callback-no-save.json`, card 11).
- Restart / restore ⇒ `content_hash` không đổi (fixture `e` ở recovery).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `VALIDATION_ERROR` | 400 — 5 fixture `neg-saved-snapshot-*` phải rơi vào đây |
| `UNAUTHORIZED / CSRF_REJECTED` | 401/403 |
| `UNAUTHORIZED_COMMAND` | Save từ chat chưa liên kết ⇒ im lặng, không đổi state |
| `NOT_FOUND` | target không tồn tại |
| `IDEMPOTENCY_CONFLICT` | save trùng key |
| `STORAGE_WRITE_FAILED` | không commit |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC12
- SC13
- SC48
- SC32
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_saved_snapshot_schema.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_concurrent_save.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_snapshot_survives_delete.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- `COUNT(saved_item active WHERE target=T) ≤ 1` sau mọi dãy thao tác.
- `saved_snapshot.content_hash` trước restart = sau restart = sau restore.
- 5 fixture `neg-saved-snapshot-*` ⇒ `VALIDATION_ERROR`, 0 hàng ghi.
- Sau `save.remove` và sau khi bài gốc bị xóa trên X: snapshot vẫn đọc được.

**Evidence artifacts:** log pytest; hash snapshot trước/sau; dump `saved_item`.

**Yêu cầu live.** Không cần live.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/telegram/commands.yaml` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 4 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/http/openapi.yaml`, `contracts/schemas/saved-snapshot.schema.json`, `contracts/telegram/commands.yaml`, `contracts/ui/screens.yaml`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `save.export` tồn tại trong `contracts/ports.yaml` nhưng MVP **hoãn** export (`F-PC00-02`). Không hiện nút export; nếu packet yêu cầu, DỪNG và hỏi. |
| `SG-02` | `data.purge_all` **đã được Owner chốt** (`OD-20260907-01` mục 24): xóa **chỉ dữ liệu nghiên cứu**; giữ đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch; **backup KHÔNG bị xóa**. `PROV-PC00-01`/`PROV-PC01-03` đã giải. Card này vẫn **không** hiện thực `data.purge_all` (ngoài scope), nhưng nếu chạm tới thì phải theo đúng danh sách giữ lại đó. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-canonical-identity-merge` (I17).
- `TC-telegram-linking-auth` cho đường Save từ Telegram.

## §12. Reviewer scope

Reviewer đọc `contracts/schemas/saved-snapshot.schema.json`, `contracts/data/invariants.md` §I08/§I17, 11 fixture ở §2. Câu hỏi bắt buộc: có đường nào snapshot bị sửa hoặc bị xóa theo tag không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-saved-snapshot`
- **Vị trí:** `evidence/runs/TC-saved-snapshot/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
