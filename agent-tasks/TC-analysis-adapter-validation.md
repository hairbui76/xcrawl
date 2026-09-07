---
card_id: TC-analysis-adapter-validation
title_vi: AI adapter: validation, grounding và cô lập tool
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M3
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED cho đường API và đường bóc JSON. Đường CLI/ACP dừng ở `CONTRACT_READY` cho tới khi probe pass — nhãn lấy từ SRC-PLAN §2, không tự đặt nhãn mới.
owner_modules: [MOD-ai-adapter]
scenario_refs: [SC11, SC16, SC17, SC28, SC49, SC51]
invariant_refs: [I11, I14, I16]
evidence_manifest_id: EVM-TC-analysis-adapter-validation
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-analysis-adapter-validation — AI adapter: validation, grounding và cô lập tool

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P2d-20260907`** (thay `PC10-PIN-P2c-20260907`; các epoch cũ hơn: `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **Ba lần pin lại cùng ngày** — `P2b`, `P2c`, `P2d` — vì `precode/decision-register.md` rồi `precode/baseline.json` lần lượt đổi byte ngay sau mỗi lần pin (`CR-PC10-15`; Coordinator nay đã đóng băng `precode/`). Hai tập byte khác nhau không được mang chung một tên epoch, nên mỗi lần là một tên mới. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `da5181b2888674134f6e3919ce401014015f223ea46a967d9fda3833c01a037b` | 22685 |
| `precode/baseline.json` | `ffd1efb3588f87504f61c037b4a242b29a6afb0ddd0f1fd1780c677b22a8bf64` | 112871 |
| `precode/decision-register.md` | `058621d0649b798cb8882f718c450d548df1f4672bdee512e330bee77d46e8b0` | 144860 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `c61be0a4f8dc5884e82bf1ed79c86f0c38da3d0f6aa41e96205c1089f900a4fc` | 240224 |
| `contracts/ai/tasks.yaml` | `0048bbdd3185fc4b7719014e7d70238c50720766f19e2968cb8e25101bbc05e7` | 31787 |
| `contracts/ai/providers.yaml` | `462e5321543df781e53d62b54cdffc819765e56f4d2842c871b82fe068dc1bbc` | 19517 |
| `contracts/ai/grounding.md` | `b54cec8b3f9f6a9cb2221daaafe8a61a149d0a6686d0d23dcbf7bf9f17995172` | 15293 |
| `contracts/ops/cli-acp-probe.md` | `d78f546fdfbeff0388c4d89171179082da6477aea0bdfcd7c85e995fa3f0909b` | 11929 |
| `contracts/ops/secrets.md` | `14b3d8988a9de21bf70de076c2b85a21b3e87394c493f18082af51c191690ee9` | 25301 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/schemas/analysis-result.schema.json` | `f26720ee04852161b4e71b4ab61c0f11c0187fcbfd25759e05245cfdb7ac172d` | 24391 |
| `contracts/state/analysis.yaml` | `06b18de42c3bbffff9a74b2e990025361cf2b179736f1994a5558f5eef3618ce` | 34958 |
| `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md` | `aa91b92d087681b3df902091bbe5d875e644fee6b2e08e53025ba97136eb6317` | 6406 |
| `precode/adr/ADR-0008-analysis-key-and-generation.md` | `bbf649f5e9239d0de28c24255469ce0498f9f108bfdd45ada2ddeac859b8f1c5` | 5660 |
| `acceptance/fixtures/ai/README.md` | `6b7ede2bc9866eed00ecdd45d52009fe7c3b895ed3c64764694b42c1f577c6a0` | 12646 |
| `acceptance/fixtures/ai/b-instruction-injection-in-post.json` | `94db889e48aac2a74c3e645d44143075309d33bbef6010593db64340fee6c05b` | 5590 |
| `acceptance/fixtures/ai/c-citation-to-unknown-source.json` | `c91286d2106f8de49c0bfb0a158157321bb76de21cb03a29816933f886ba6a65` | 4760 |
| `acceptance/fixtures/ai/d-schema-valid-but-uncited.json` | `cf4662a1713d11fd4c60698cc416b0637bd1cfbfb35dce3a86b298e26c52bcbe` | 6158 |
| `acceptance/fixtures/ai/e-transcript-secret-canary.json` | `17c41531562ad41c9a869aa201df018e2973a7df319bff6009dfe7239e125ee1` | 5240 |
| `acceptance/fixtures/ai/f-tool-request-in-transcript.json` | `dac72388abd272b69e62333aecf1b817923807a5726424d342e0b758a17fdedd` | 4622 |
| `acceptance/fixtures/ai/g-cli-json-embedded-in-prose.json` | `d8136a15657e3032a2c1e1b58b4ab04df98c45ff3c6dd63c46d557a79bbf865d` | 4345 |
| `acceptance/fixtures/ai/h-provider-unavailable-no-fallback.json` | `202895c3a8d9816878fc67962286e6da0d0a331b6d81cb1a8c541c48c881545e` | 5577 |
| `acceptance/fixtures/ai/k-zero-api-key-all-tasks-via-cli.json` | `8f46b4c4205f82f72e2093b654b1972344746d6af84369020d4e75f2cef6912f` | 10599 |
| `acceptance/fixtures/recovery/f-secret-canary-injection.json` | `3f3a754bd3aed6b0ce56321584f3eadf17df69b0ff08d2cfaea8a13af6617d15` | 3759 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |
| `acceptance/fixtures/ui/sc51-first-time-setup.json` | `19820cec74bb3a73dd9945674ce3dd88fd9d18f1d15ae0b48ebef938b92f18d7` | 13282 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-analysis-adapter-validation`
- **Milestone:** M3 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-ai-adapter`

**Mục tiêu.** Adapter gọi provider/CLI đã cấu hình cho đúng một task, ép output qua schema của task, từ chối output schema-valid nhưng thiếu citation, và không bao giờ để nội dung nguồn kích hoạt tool, đọc secret hay đổi recipient.

**Non-goals.**

- Không quyết định provider/model cụ thể — REQ-OQ03 là `OWNER_DECISION_REQUIRED`.
- Không bật fallback provider chưa được owner cấu hình.
- Không viết vòng đời task (card `TC-analysis-once-per-generation`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md`, `precode/adr/ADR-0008-analysis-key-and-generation.md`.
3. Hợp đồng nghiệp vụ: `contracts/ai/tasks.yaml`, `contracts/ai/providers.yaml`, `contracts/ai/grounding.md`, `contracts/ops/cli-acp-probe.md`, `contracts/ops/secrets.md`, `contracts/ops/internet-boundary.md`, `contracts/schemas/analysis-result.schema.json`, `contracts/state/analysis.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/ai/README.md`, `acceptance/fixtures/ai/b-instruction-injection-in-post.json`, `acceptance/fixtures/ai/c-citation-to-unknown-source.json`, `acceptance/fixtures/ai/d-schema-valid-but-uncited.json`, `acceptance/fixtures/ai/e-transcript-secret-canary.json`, `acceptance/fixtures/ai/f-tool-request-in-transcript.json`, `acceptance/fixtures/ai/g-cli-json-embedded-in-prose.json`, `acceptance/fixtures/ai/h-provider-unavailable-no-fallback.json`, `acceptance/fixtures/ai/k-zero-api-key-all-tasks-via-cli.json`, `acceptance/fixtures/recovery/f-secret-canary-injection.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`, `acceptance/fixtures/ui/sc51-first-time-setup.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `worker/app/adapter/base.py` | giao diện adapter chung; `tool_definitions_registered = 0` |
| `worker/app/adapter/api_provider.py` | đường API, nhận credential per-task ngắn hạn |
| `worker/app/adapter/cli_acp.py` | đường CLI/ACP, chạy với tool/file/network bị tắt ngoài inference (B13) |
| `worker/app/adapter/extract_json.py` | bóc JSON khỏi prose; từ chối JSON lồng transcript |
| `worker/app/adapter/validate.py` | validate theo `analysis-result.schema.json` + kiểm citation |
| `tests/contract/test_analysis_result_schema.py` | 9 fixture ai/* |
| `tests/integration/test_injection_canary.py` | canary secret, tool audit, network audit |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `ai.run_inference_task`
- `ai.probe_provider_capability`

**Consumes** (chỉ được gọi đúng những operation này):

- `secret.issue_task_credential`

**Schema:**

- kết quả phân tích → `contracts/schemas/analysis-result.schema.json`
- định nghĩa task và schema theo task → `contracts/ai/tasks.yaml`

**State effects.** Adapter **không** ghi state. Nó trả kết quả cho worker; worker mới gọi `analysis.submit_result`. `usage` không biết ⇒ ghi `unknown`, **không** ghi 0 (I14).

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-analysis-worker` — internal (cùng tiến trình worker trên máy cá nhân)

**Được phép gọi:**

- Provider API đã cấu hình, hoặc CLI/ACP đã qua probe (`contracts/ops/cli-acp-probe.md`)

**Đường bị cấm (denied paths):**

- Adapter **không** điều khiển Chrome, không chạm SQLite, không gọi Telegram (SRC-PLAN §6).
- Không đăng ký tool nào: `tool_definitions_registered = 0` (`CR-PC06-03`).
- Nội dung bài nguồn và output của model **không** có quyền chọn URL để fetch, đọc secret hay đổi recipient (I11).
- Fallback provider chỉ bật khi owner đã cấu hình; không tự bật (I14).

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
| `I11` | bài nguồn/AI output không đọc secret, không gọi tool, không đổi recipient |
| `I14` | usage không biết là `unknown`, không phải 0 |
| `I16` | attempt không bao giờ là kết quả |

**Transaction và commit point:**

- Không có transaction. Ranh giới quan trọng là: provider đã chạy ≠ kết quả đã commit.

**Race, replay và forbidden effects:**

- Crash sau khi provider hoàn tất, trước khi submit ⇒ `AI_ATTEMPT_UNCERTAIN`; không hứa chưa phát sinh phí.
- Timeout inference theo task (`label` 120 s, `summary` 300 s, `direction_phrasing` 180 s — PROVISIONAL, `contracts/ai/tasks.yaml`, đều nhỏ hơn `lease_ttl_analysis`).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `AI_OUTPUT_INVALID` | item `retry_wait` rồi `failed` khi hết budget; **không** commit `valid` |
| `AI_PROVIDER_UNAVAILABLE` | giữ input; fallback chỉ theo policy đã cấu hình; run có thể `partial` |
| `AI_ATTEMPT_UNCERTAIN` | item `unknown_attempt`; ghi attempt mới khi chạy lại |
| `CAPABILITY_DENIED` | adapter chưa qua probe hoặc thiếu capability ⇒ tắt adapter đó, không hạ tiêu chuẩn |
| `VALIDATION_ERROR` | input task sai hợp đồng |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC11
- SC16
- SC17
- SC28
- SC49
- SC51

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_analysis_result_schema.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_injection_canary.py -q` (PROVISIONAL)
- Probe CLI/ACP: `contracts/ops/cli-acp-probe.md` §3 (T-ISO, T-JSON, T-TIME, T-CONC, T-USAGE, T-TASK) — **NOT_RUN**

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `d-schema-valid-but-uncited.json`: schema pass nhưng bị từ chối vì thiếu citation ⇒ `AI_OUTPUT_INVALID`.
- Fixture `e-transcript-secret-canary.json`: canary **không** xuất hiện trong bất kỳ log/output nào.
- Fixture `f-tool-request-in-transcript.json`: số tool được đăng ký = 0, số lời gọi tool = 0.
- Fixture `h-provider-unavailable-no-fallback.json`: 0 lời gọi tới provider thứ hai; `usage = unknown`.

**Evidence artifacts:** log pytest đã che secret; tool/network audit log; bản ghi từ chối kèm lý do.

**Yêu cầu live.** AC-16 (không API key, mọi task qua CLI) cần live capability run. Hiện **chưa adapter CLI/ACP nào được probe** ⇒ AC-16 báo **BLOCKED**, không phải FAIL (`CR-PC06-04`).

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED cho đường API và đường bóc JSON. Đường CLI/ACP dừng ở `CONTRACT_READY` cho tới khi probe pass — nhãn lấy từ SRC-PLAN §2, không tự đặt nhãn mới.`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ai/grounding.md`, `contracts/ai/providers.yaml`, `contracts/ai/tasks.yaml`, `contracts/ops/cli-acp-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 7 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ai/grounding.md`, `contracts/ai/providers.yaml`, `contracts/ai/tasks.yaml`, `contracts/ops/cli-acp-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/secrets.md`, `contracts/schemas/analysis-result.schema.json`.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-TERMS` | **Cổng `provider_config.terms_check_at` (`CR-PC07-07`).** `contracts/data/entities.yaml` ràng buộc `ck_provider_config_terms_before_enable`: `enabled = 0 OR terms_check_at IS NOT NULL`. Không được bật đường CLI/ACP của một nhà cung cấp trước khi owner xác nhận đã đọc điều khoản của **chính nhà đó** (REQ-A5, ADR-0010). `terms_check_at` là mốc ghi nhận, **không** phải bằng chứng về nội dung điều khoản. `terms_check_by` NOT NULL khi `terms_check_at` NOT NULL. |
| `SG-01` | REQ-OQ03 (provider và model cụ thể) là `OWNER_DECISION_REQUIRED`, không có mặc định. Không tự chọn. |
| `SG-02` | Chưa adapter CLI/ACP nào qua probe (`contracts/ops/cli-acp-probe.md` §6). Không bật đường CLI cho provider chưa đọc điều khoản (A5, SRC-SPEC §13.2). |
| `SG-03` | Nếu isolation của một provider không xác minh được ⇒ adapter đó **giữ nguyên trạng thái disabled** (B13). |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-analysis-once-per-generation` (vòng đời task).
- `TC-owner-auth-session` (secret service scope).

## §12. Reviewer scope

Reviewer đọc `contracts/ai/grounding.md`, `contracts/ai/providers.yaml` ISO-01…05, `contracts/ops/cli-acp-probe.md` §3, 9 fixture ai/*. Câu hỏi bắt buộc: có đường nào nội dung bài viết ảnh hưởng tới tool, secret hay recipient không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-analysis-adapter-validation`
- **Vị trí:** `evidence/runs/TC-analysis-adapter-validation/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
