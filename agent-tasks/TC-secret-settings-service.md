---
card_id: TC-secret-settings-service
title_vi: Secret service và settings service: nơi hợp lệ duy nhất của một secret
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M3
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED (E1 + E2 trên fixture; không có provider nào được bật, không live claim)
owner_modules: [MOD-secret-service, MOD-settings-service]
scenario_refs: [SC16, SC17, SC20, SC24, SC28, SC41, SC49]
invariant_refs: [I01, I11, I14]
evidence_manifest_id: EVM-TC-secret-settings-service
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-secret-settings-service — Secret service và settings service: nơi hợp lệ duy nhất của một secret

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P6-20260909`** (thay `PC10-PIN-P5c-20260909`; các epoch cũ hơn: `PC10-PIN-P5c`, `PC10-PIN-P5b`, `PC10-PIN-P4b`, `PC10-PIN-P4`, `PC10-PIN-P3b`, `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. **`P4`** pin sau `PKT-PC00-FIX30` (`OD-20260908-10`) — lần ghi `precode/` cuối của vòng này. Đợt sửa Giai đoạn 4/6 chạy song song chỉ chạm code, test, handoff và manifest: **không** file nào trong số đó được card pin, nên chúng không tạo ra một lần pin lại. **`P4b`** pin sau `PKT-PC00-FIX32`: `precode/adr/ADR-0011-frameworks-and-toolchain.md` được sửa (phạm vi `mypy`, `CR-PC00-35`). `ADR-0011` nằm trong read set của **mọi** card, nên một mình nó đủ làm cả 19 card `STALE`. Gói song song chỉ chạm bộ file dựng gói (pyproject, uv lockfile), workflow CI, Makefile, .gitignore và một test smoke của server — **không** file nào trong số đó được card pin hay trích dẫn, đã kiểm trực tiếp. **`P5`** pin sau `AMD-ENT-maintenance-01` (`PKT-PC02-FIX16`): `contracts/data/entities.yaml` thêm entity `maintenance_window` và chia lại tập purge (37/22/2), kéo theo `precode/change-control.md` và `precode/decision-register.md`. Thư mục nay có **20 card** — `TC-secret-settings-service` (khoảng trống `G-6`) được thêm ở `PKT-PC10-FIX28`. Tên `P5` **không bao giờ được phát hành**: nó được pin trong lúc đợt propagate của `PKT-PC02-FIX17` còn đang ghi, nên tập byte của nó sai ngay khi vừa ghi xong và bị `P5b` thay trước khi có ai đọc. Ghi lại ở đây để không ai đi tìm một epoch `P5` hợp lệ. **`P5c` (2026-09-09)** pin sau `PKT-PC02-FIX19`: bản `E0-18` siết chặt của W6n bắt hai fixture `acceptance/fixtures/recovery/` vẫn ghi tập purge cũ (20/21) trong khi hợp đồng đã sang 37/22/2; W3n sửa chúng, và fixture **có** pin nên card phải pin lại. Tên epoch mang ngày pin, không phải ngày của thay đổi. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

**Card thứ 20, pin tại cùng epoch `PC10-PIN-P4b-20260908`.** Nó được thêm ở `PKT-PC10-FIX28` sau khi 19 card kia đã pin ở epoch này; **không** file đã pin nào đổi byte giữa hai thời điểm, nên 19 card kia **không** được sinh lại và giữ nguyên byte. Cùng epoch ở đây nghĩa là **cùng tập byte nguồn**, đúng nghĩa mà tên epoch mang — không phải một ngoại lệ.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `defbe74ef6a4953adb25e9a31e07f010856f05a142e6973f14cbb7c5b2e3f8b7` | 27451 |
| `precode/baseline.json` | `cf59b2c937c334ce21d2cebc7e10dcc84c872f83432fc59d86a1477bd2311875` | 130132 |
| `precode/decision-register.md` | `24e6765f86a88c77ca3efa3af10c600345f3a462ad6abe2d8e06aeceb01eb8c1` | 190995 |
| `contracts/modules.yaml` | `7a4e19bdbb43e1339f305cd4715f1e7ac704b09720408ccf1db48a01b23c1e25` | 108912 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c7c7734001b98f2516aff9a36b5a6f947cee0cb4485be2e64fca55c264b8b412` | 128872 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `0ec6bc91eccca0588075c385060f8095d640819ce03910f64d1397ef1e4d4c4c` | 256458 |
| `contracts/ops/secrets.md` | `22f7a0075ada77c69dfce6b8b7d6e6b0af625317f2fc4c1be726abf5c3c391a5` | 25323 |
| `contracts/ai/providers.yaml` | `b3b27bcc55fe32c55d5232215c6ea9629af014f65c20915f0d9e90e2486418f1` | 37688 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/state/analysis.yaml` | `06b18de42c3bbffff9a74b2e990025361cf2b179736f1994a5558f5eef3618ce` | 34958 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | `aa91b92d087681b3df902091bbe5d875e644fee6b2e08e53025ba97136eb6317` | 6406 |
| `acceptance/fixtures/recovery/README.md` | `fa733add0f408dee3f1d870b1ca6f6da977337f2d940e0e13afe74ec4efccc79` | 12235 |
| `acceptance/fixtures/recovery/f-secret-canary-injection.json` | `3f3a754bd3aed6b0ce56321584f3eadf17df69b0ff08d2cfaea8a13af6617d15` | 3759 |
| `acceptance/fixtures/recovery/i-collector-token-calls-save.json` | `78e6e6ee47008b5d9b44dbdf65994f93c7ce89ee33ef7f96e7699ee7e0372886` | 5229 |
| `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json` | `32883c7a2a12b36d964f7974c45952e731f2330cc1416b43c9e4895ae1ad5119` | 4024 |
| `acceptance/fixtures/ai/README.md` | `6b7ede2bc9866eed00ecdd45d52009fe7c3b895ed3c64764694b42c1f577c6a0` | 12646 |
| `acceptance/fixtures/ai/k-zero-api-key-all-tasks-via-cli.json` | `8f46b4c4205f82f72e2093b654b1972344746d6af84369020d4e75f2cef6912f` | 10599 |
| `acceptance/fixtures/ai/e-transcript-secret-canary.json` | `17c41531562ad41c9a869aa201df018e2973a7df319bff6009dfe7239e125ee1` | 5240 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-secret-settings-service`
- **Milestone:** M3 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-secret-service`, `MOD-settings-service`

**Mục tiêu.** Hiện thực sáu operation `secret.*` và `settings.*` của `contracts/ports.yaml` để hệ thống **có** một chỗ hợp lệ để cất API key, webhook secret Telegram và credential ngắn hạn theo từng task: secret store phía server theo `contracts/ops/secrets.md` §4, cấp credential **chỉ** cho worker đang giữ lease của đúng task (B13/ADR-0010), và `provider_config` chỉ được `enabled = true` khi `terms_check_at` đã có.

**Non-goals.**

- **Không** đọc điều khoản nhà cung cấp thay người (`REQ-A5` là việc tay, ADR-0010 §Hệ quả). Card chỉ dựng **cửa** kiểm `terms_check_at`, không tự điền nó.
- Không bật adapter nào: cột `enabled` của mọi `provider_config` vẫn `false` sau card này.
- Không gọi provider AI thật; `settings.test_provider` được hiện thực nhưng **không** chạy live ở đây.
- Không viết vòng đời task phân tích (`TC-analysis-once-per-generation`) và không viết adapter (`TC-analysis-adapter-validation`).
- Không đụng phiên X hay phiên CLI trên máy cá nhân — chúng **không** đồng bộ lên server (`secrets.md` §6).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md`.
3. Hợp đồng nghiệp vụ: `contracts/ops/secrets.md`, `contracts/ai/providers.yaml`, `contracts/ops/internet-boundary.md`, `contracts/state/analysis.yaml`, `contracts/data/invariants.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/recovery/README.md`, `acceptance/fixtures/recovery/f-secret-canary-injection.json`, `acceptance/fixtures/recovery/i-collector-token-calls-save.json`, `acceptance/fixtures/recovery/h-unauthenticated-owner-api.json`, `acceptance/fixtures/ai/README.md`, `acceptance/fixtures/ai/k-zero-api-key-all-tasks-via-cli.json`, `acceptance/fixtures/ai/e-transcript-secret-canary.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/secret/store.py` | secret store phía server: envelope encryption, mỗi secret một data key (`secrets.md` §4); **module duy nhất** đọc được giá trị |
| `server/app/secret/service.py` | `secret.store_provider_key`, `secret.issue_task_credential`, `secret.revoke_task_credential`; cửa lease của ISO-05 |
| `server/app/secret/router.py` | điểm vào cho `analysis_worker_token` và `internal_only` |
| `server/app/secret/repository.py` | `secret_ref`, `task_credential`, `secret_audit` — ba entity module này sở hữu |
| `server/app/settings_service/service.py` | `settings.get_config`, `settings.update_config`, `settings.test_provider`; chuyển key cho secret service và **không** đọc lại |
| `server/app/settings_service/router.py` | HTTP handler `owner_session` + CSRF |
| `server/app/settings_service/repository.py` | `settings`, `provider_config`, `provider_test_result`, `source_connection` |
| `tests/contract/test_secret_scope_matrix.py` | ma trận scope: ai gọi được operation nào, và mã lỗi đúng |
| `tests/integration/test_task_credential_lease.py` | ISO-05: worker không giữ lease bị từ chối; canary không rời hệ thống; `terms_check_at` chặn `enabled` |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `secret.store_provider_key`
- `secret.issue_task_credential`
- `secret.revoke_task_credential`
- `settings.get_config`
- `settings.update_config`
- `settings.test_provider`

**Consumes** (chỉ được gọi đúng những operation này):

- `embedding.start_generation_rebuild`

**Schema:**

- nguồn schema của settings/provider_config → `contracts/data/entities.yaml`
- quy tắc secret store, scope và audit → `contracts/ops/secrets.md`
- cửa `terms_check` trước khi `enabled = true` → `contracts/ai/providers.yaml`

**State effects.** `secret.store_provider_key` ghi vào secret store (idempotent theo `provider_id + key_version`). `secret.issue_task_credential` ghi audit đã che secret và cấp credential **ngắn hạn** cho đúng task đang giữ lease; cùng `task_id + attempt_id` trả lại credential còn hạn, **không** cấp cái thứ hai. `secret.revoke_task_credential` vô hiệu credential và ghi audit; thu hồi lại lần nữa **không** đổi trạng thái. `settings.update_config` idempotent theo `request_id`. `settings.test_provider` ghi một `provider_test_result` mới mỗi lần và **không** đổi cấu hình. Giá trị secret **không bao giờ** rời module: `settings.get_config` chỉ trả tham chiếu và trạng thái *đã cấu hình hay chưa* (`docs/owner-runbook.md` §8).

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-web-ui` — HTTP qua `owner_session` + CSRF cho `settings.*`
- `MOD-analysis-worker` — `analysis_worker_token` cho `secret.issue_task_credential`
- `MOD-analysis-service` — internal cho `secret.revoke_task_credential`
- `MOD-settings-service` — internal cho `secret.store_provider_key`

**Được phép gọi:**

- MOD-data-store (SQLite)
- MOD-embedding-service (`embedding.start_generation_rebuild` khi owner đổi model)

**Đường bị cấm (denied paths):**

- **Không operation nào trả giá trị secret ra ngoài module.** `settings.get_config` trả tham chiếu và cờ *đã cấu hình*, không trả key (`secrets.md` §4).
- Worker **không** nhận credential của provider khác, của task khác, hay khi **không giữ lease** (`STALE_LEASE`) — đó là ISO-05, và nó là tính chất đường `api_key` **tạo ra**, không phải loại bỏ.
- Master key **không** nằm trong repo, log, tin nhắn hay response (`secrets.md` §4, §8).
- Đường `cli_acp` có `secret_ref = NULL` (REQ-D51): card này **không** cấp secret cho nó.
- Không adapter nào được bật: `enabled = true` mà thiếu `terms_check_at` bị **DB CHECK** `ck_provider_config_terms_before_enable` từ chối.

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
| `I01` | mọi bảng có `owner_id`; secret và audit không ngoại lệ |
| `I11` | nội dung nguồn/AI output không đọc được secret, không đổi được recipient |
| `I14` | `usage` không biết ghi `unknown`; `provider_test_result` không bịa số |

**Transaction và commit point:**

- `TXN-issue-credential`: kiểm lease → cấp credential → ghi audit trong **một** transaction. Không có đường nào ghi audit mà không cấp, hoặc cấp mà không ghi audit.
- `TXN-settings-update`: cập nhật `settings`/`provider_config` + bản ghi idempotency trong một transaction; DB CHECK chạy **bên trong** transaction đó, nên `enabled = true` thiếu `terms_check_at` làm rollback cả lô.

**Race, replay và forbidden effects:**

- Hai lời gọi cùng `task_id + attempt_id`: lời gọi thứ hai trả **cùng** credential còn hạn, không cấp mới.
- Lease hết hạn **giữa** lúc kiểm và lúc cấp ⇒ phải từ chối; kiểm lease trong cùng transaction với cấp, không kiểm trước rồi cấp sau.
- Owner đổi provider trong lúc một task đang chạy: credential đã cấp vẫn còn hạn của nó; thu hồi là hành động tường minh (`secret.revoke_task_credential`), không phải hệ quả ngầm của một lần đổi cấu hình.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `UNAUTHORIZED` | principal sai lớp gọi `settings.*` hoặc `secret.issue_task_credential` |
| `STALE_LEASE` | worker **không** giữ lease của task xin credential — ca âm của ISO-05 |
| `CSRF_REJECTED` | mutation `settings.*` qua owner session thiếu header `X-CSRF-Token` |
| `IDEMPOTENCY_CONFLICT` | cùng khóa, payload khác |
| `VALIDATION_ERROR` | payload sai hợp đồng; gồm cả `enabled = true` khi thiếu `terms_check_at` |
| `NOT_FOUND` | provider hoặc task không tồn tại |
| `STORAGE_WRITE_FAILED` | ghi thất bại; không cấp credential nửa vời |
| `AI_PROVIDER_UNAVAILABLE` | `settings.test_provider` không tới được endpoint đã cấu hình |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC16
- SC17
- SC20
- SC24
- SC28
- SC41
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `uv run pytest tests/contract/test_secret_scope_matrix.py -q` (PROVISIONAL)
- `uv run pytest tests/integration/test_task_credential_lease.py -q` (PROVISIONAL)
- `uv run python evidence/tools/e0_check.py` — E0 lint (PC09)

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `recovery/f-secret-canary-injection.json` (SC17): canary **không** xuất hiện trong log, response, audit hay bất kỳ artefact nào. Đếm số lần canary xuất hiện = 0, không phải 'không thấy'.
- ISO-05: gọi `secret.issue_task_credential` bằng token của một worker **không** giữ lease ⇒ `STALE_LEASE`, và **0** credential được ghi. Đây là ca âm mà `providers.yaml` §4 nêu đích danh.
- Fixture `ai/k-zero-api-key-all-tasks-via-cli.json` (SC16): không cấu hình key nào ⇒ **0** lời gọi tới secret store cho đường `cli_acp` (`secret_ref = NULL`, REQ-D51).
- Ghi thật vào `provider_config`: đặt cột `enabled` sang bật khi `terms_check_at IS NULL` bị **DB** từ chối (`ck_provider_config_terms_before_enable`) — kiểm bằng một lần ghi thật, không bằng validation ở tầng ứng dụng.
- `settings.get_config` sau khi lưu key: response chứa tham chiếu và cờ *đã cấu hình*, và **không** chứa chuỗi key ở bất kỳ trường nào.

**Evidence artifacts:** log pytest đã che secret; dump `secret_audit` (đã che giá trị); đếm canary trong mọi artefact; bản ghi từ chối `STALE_LEASE` kèm 0 hàng `task_credential`.

**Yêu cầu live.** E3 **NOT_RUN** và ngoài phạm vi: `settings.test_provider` chạm endpoint nhà cung cấp thật, và không provider nào được bật (`terms_check` là `KC` cho tới khi Owner đọc điều khoản). Card dừng ở E1/E2 với fixture và fake endpoint.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED (E1 + E2 trên fixture; không có provider nào được bật, không live claim)`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ai/providers.yaml`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 3 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ai/providers.yaml`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-TERMS` | **Không đọc điều khoản thay Owner.** `REQ-A5` là việc tay và phải làm lại khi provider đổi version (ADR-0010). Card dựng **cửa** (`terms_check_at` NOT NULL trước `enabled = true`), không tự điền dữ kiện. Điền một giá trị để test pass là bịa bằng chứng. |
| `SG-MASTER-KEY` | `contracts/ops/secrets.md` §4 nói master key ở đâu và được bảo vệ thế nào, nhưng **nơi vận hành thật** của nó là cấu hình triển khai. Chưa có cấu hình ⇒ DỪNG và hỏi; **không** sinh một key mặc định, không commit key, không đặt key trong biến môi trường của repo. |
| `SG-ISO05` | ISO-05 chỉ được coi là chứng minh khi ca âm **chạy thật** và bị từ chối. Một test khẳng định 'đường này không tồn tại' **không** phải bằng chứng cho ISO-05 (`providers.yaml` §4). |
| `SG-NAME` | Gói tên `server/app/settings_service/`, **không** phải `server/app/settings/`: bộ khung Giai đoạn 0 mang một module cấu hình `server/app/settings.py`, và một package cùng tên trong cùng package cha sẽ **va nhau khi import** — cùng lớp lỗi `import file mismatch` mà `PROV-P0-01` đã gặp một lần. Muốn đổi tên ⇒ CR, không tự đổi. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-owner-auth-session` — đã thi công; `settings.*` đi qua owner session + CSRF.
- `TC-analysis-once-per-generation` — chủ của vòng đời task và lease mà ISO-05 kiểm; card này cấp credential cho **task đang giữ lease** của nó.
- `TC-analysis-adapter-validation` — người tiêu thụ credential; **không** phụ thuộc ngược lại.

## §12. Reviewer scope

Reviewer đọc `contracts/ops/secrets.md` §4, §5, §7, §8, `contracts/ai/providers.yaml` §1 và §5, `contracts/data/entities.yaml` (`provider_config` checks, `secret_ref`, `task_credential`, `secret_audit`), và ba fixture canary. Ba câu hỏi bắt buộc: (1) có đường nào một giá trị secret đi ra ngoài module — log, response, audit, thông báo lỗi — không; (2) ca âm ISO-05 có **chạy thật** và bị từ chối, hay chỉ được khẳng định; (3) `enabled = true` thiếu `terms_check_at` bị chặn ở **DB** hay chỉ ở tầng ứng dụng.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-secret-settings-service`
- **Vị trí:** `evidence/runs/TC-secret-settings-service/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
