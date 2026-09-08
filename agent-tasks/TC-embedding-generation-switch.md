---
card_id: TC-embedding-generation-switch
title_vi: Embedding generation: rebuild và chuyển active nguyên tử
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M3 → M5
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-embedding-service]
scenario_refs: [SC24, SC08, SC49, SC52]
invariant_refs: [I12]
evidence_manifest_id: EVM-TC-embedding-generation-switch
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-embedding-generation-switch — Embedding generation: rebuild và chuyển active nguyên tử

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
| `contracts/reporting/selection.md` | `781effb61be2865a07fa3be4373196229bb6bd89048abbb943d646ca95401fe4` | 37357 |
| `contracts/state/report.yaml` | `77969cb473c84a7df90e6b784ad1afa637313e813ccbb59d99b1ea329241245f` | 30187 |
| `contracts/http/openapi.yaml` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` | 231705 |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` | 19568 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
| `acceptance/fixtures/reporting/README.md` | `cdb2008913f53562ec41fe7ed179c3c17d3a568ee9d5dc8027e16405dcf2b54f` | 16228 |
| `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json` | `e911021ea43f8d9168ea64da6919735a58c41a379a7e926b566128030939a359` | 6580 |
| `acceptance/fixtures/reporting/m-density-worked-example.json` | `719f9c4da1b1bd9138a1cdc60a1d2d501a9abf3945c85e991aa72a828baa3347` | 29177 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json` | `98bb69cb1fba77b89a65ee500fdfe79e8d19ffef86eb435311c88e2c8786044f` | 19229 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-embedding-generation-switch`
- **Milestone:** M3 → M5 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-embedding-service`

**Mục tiêu.** Đổi model embedding sinh một generation mới; selection bị chặn thay vì trộn vector khác model/dimension; chuyển active generation là một thao tác nguyên tử sau khi đủ vector.

**Non-goals.**

- Không gọi provider API để thay embedding local (D48/D50).
- Không chốt model embedding cụ thể (REQ-OQ09, sau A3).
- Không viết thuật toán mật độ (card `TC-report-coverage-publish-cas` và `contracts/reporting/selection.md`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0001-topology-and-placement.md`.
3. Hợp đồng nghiệp vụ: `contracts/reporting/selection.md`, `contracts/state/report.yaml`, `contracts/http/openapi.yaml`, `contracts/ops/deployment.md`, `contracts/data/entities.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/reporting/README.md`, `acceptance/fixtures/reporting/l-embedding-generation-switch-blocked.json`, `acceptance/fixtures/reporting/m-density-worked-example.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/reporting/n-embedding-generation-switch-positive.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/embedding/service.py` | generate / get_active / start_rebuild / activate |
| `server/app/embedding/generation.py` | generation, model id, dimension, đếm phủ |
| `server/app/embedding/repository.py` | vector repository port |
| `tests/contract/test_embedding_generation_guard.py` | cosine giữa hai generation bị chặn |
| `tests/integration/test_generation_activation.py` | chuyển active nguyên tử, không trộn |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `embedding.generate_vectors`
- `embedding.get_active_generation`
- `embedding.start_generation_rebuild`
- `embedding.activate_generation`

**Consumes** (chỉ được gọi đúng những operation này):

- `storage.get_health`

**Schema:**

- không có JSON Schema riêng; hình dạng ở `ENT-embedding-generation` và `ENT-tag-vector` → `contracts/data/entities.yaml`

**State effects.** `ENT-embedding-generation` có `model_id`, `dimension`, `state`, số vector đã phủ. Trong lúc rebuild: dùng generation cũ **hoặc** chặn selection có lý do; không trộn.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-ingest-service` — internal
- `MOD-tag-service` — internal
- `MOD-report-service` — internal
- `MOD-settings-service` — internal cho `embedding.start_generation_rebuild`

**Được phép gọi:**

- Model embedding local trên server
- MOD-data-store (vector repository port)

**Đường bị cấm (denied paths):**

- Không gọi provider API/CLI (SRC-PLAN §6: 'Embedding service … Đường bị cấm: Provider API/CLI').
- Không đổi subscription; không âm thầm thay embedding local bằng API.

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
| `I12` | vector khác model/generation/dimension không được so sánh trong cùng một lần selection |

**Transaction và commit point:**

- `embedding.activate_generation` là một CAS: chỉ đổi con trỏ active khi generation mới đã đủ phủ theo ngưỡng PROVISIONAL trong `contracts/reporting/selection.md`.

**Race, replay và forbidden effects:**

- Report build đang chạy khi generation đổi ⇒ `EMBEDDING_GENERATION_MISMATCH`, build abort/rebuild, report đã publish **không** bị mutate.
- Hai lệnh rebuild đồng thời ⇒ một thắng.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `EMBEDDING_GENERATION_MISMATCH` | selection blocked; giữ vector; không cosine giữa khác dimension/model |
| `VALIDATION_ERROR` | 400 |
| `IDEMPOTENCY_CONFLICT` | rebuild trùng |
| `NOT_FOUND` | generation không tồn tại |
| `STORAGE_WRITE_FAILED` | không ghi vector, không đổi active |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC24
- SC08
- SC49
- SC52

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_embedding_generation_guard.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_generation_activation.py -q` (PROVISIONAL)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `l-embedding-generation-switch-blocked.json`: hai generation xen kẽ ⇒ selection bị chặn **trước** report commit, 0 phép cosine chéo generation.
- Sau `activate_generation`: mọi vector dùng trong một lần selection có cùng `(model_id, generation, dimension)`.
- Trong lúc rebuild: `report.build` hoặc dùng generation cũ, hoặc trả `EMBEDDING_GENERATION_MISMATCH` — không có đường thứ ba.

**Evidence artifacts:** log pytest; dump `embedding_generation`; đếm phép so sánh chéo generation (phải = 0).

**Yêu cầu live.** Chất lượng ngưỡng tương đồng (REQ-OQ08, A3) cần dữ liệu thật; ngoài phạm vi card.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

**Phạm vi đã phê chuẩn** (`OD-20260907-01`). Read set của card này nằm trong bốn phạm vi mà A2-R4 xác định đủ điều kiện — *ranh giới và quyền*, *dữ liệu và định danh*, *workflow và trạng thái*, *báo cáo và thời gian* — và không chạm `contracts/ai/`, `contracts/telegram/`, hay bất kỳ file `contracts/ops/` nào ngoài `deployment.md` (file này đã lên `CONTRACT_READY` ở PC01-FIX13). 17 blocker B01–B17 nay là `RATIFIED`, nên điểm dừng dạng *"B0x còn PROVISIONAL"* đã gỡ khỏi §10.

  **Nhưng nền hợp đồng CHƯA đồng nhất `CONTRACT_READY`.** 1 file hợp đồng trong read set của card này vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW` trong chính header của nó: `contracts/http/openapi.yaml`. Vì vậy **không** được đọc mục này là "mọi hợp đồng đã sẵn sàng"; hãy đọc là "phạm vi nghiệp vụ đã được phê chuẩn, và 1 file còn lại phải lên `CONTRACT_READY` trước khi claim của card vượt quá `IMPLEMENTATION_VERIFIED`". Kiểm lại bằng `grep -h claim_ceiling <file>` — đừng tin dòng này.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Ngưỡng tương đồng và ngưỡng phủ đều PROVISIONAL (`contracts/reporting/selection.md`). Không chỉnh số để test pass (SRC-PLAN §14.2). |
| `SG-02` | Nếu thiếu dữ liệu để đánh giá mật độ ⇒ `insufficient_evidence`, **không** gọi là 'đang nổi' (B14). |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-report-coverage-publish-cas` để chứng minh chặn xảy ra trước publish commit.

## §12. Reviewer scope

Reviewer đọc `contracts/reporting/selection.md`, fixture `l` và `m`. Câu hỏi bắt buộc: có phép so sánh nào giữa hai generation lọt qua không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-embedding-generation-switch`
- **Vị trí:** `evidence/runs/TC-embedding-generation-switch/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
