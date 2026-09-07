---
card_id: TC-ui-runs-three-states
title_vi: UI Runs: ba trạng thái rỗng / giới hạn / lỗi phải khác nhau
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M4 → M7
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
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
| `contracts/ui/screens.yaml` | `db78678cba7e46b33669596f02963e1eac5e65804c6f9a997bf22d72ba6bc296` | 47481 |
| `contracts/state/run.yaml` | `c92e7c4e6fc6dce8a0280e64a182c1463a1e7a4b07d3c26f8036e37fd34579ec` | 91779 |
| `contracts/state/delivery.yaml` | `9fcccc25fed432a895b15e9b98787d7294dd298d9209e9b0f2c7f801e1579626` | 26652 |
| `contracts/state/storage.yaml` | `f67e78f528a13b768b97ab72f55542ac9bac439b8f5472e8e03247b41dae72c2` | 27018 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `precode/adr/ADR-0002-run-state-model-split.md` | `5ed7b2c429ef7e060140f8b6bbaa71b761b482134aaac155ad32d64bef34b8c0` | 4924 |
| `precode/adr/ADR-0003-delivery-unknown-state.md` | `1cb86d8db85c4350dc1eaf6b0822908030219d326c65a8fbec321066d2aab2a0` | 5105 |
| `acceptance/fixtures/collection/README.md` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 12636 |
| `acceptance/fixtures/collection/e-limit-reached-stop.json` | `ce13e459e9e82755ab6b25f01b1e5e77e76f9a4f073ee7b69e2ab5eb9364c34e` | 7892 |
| `acceptance/fixtures/collection/c-challenge-mid-batch.json` | `b4330c7e473779279ba545f0ecb6d9cd8f2a811beb0bae7310c62ff5dcf7e16b` | 12528 |
| `acceptance/fixtures/reporting/d-empty-period-coverage-only.json` | `e619c514f35956db8d4454df4779eb5df56f4fab814acb4c9d3c55fdc790f7e3` | 8045 |
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
2. ADR liên quan: `precode/adr/ADR-0002-run-state-model-split.md`, `precode/adr/ADR-0003-delivery-unknown-state.md`.
3. Hợp đồng nghiệp vụ: `contracts/ui/screens.yaml`, `contracts/state/run.yaml`, `contracts/state/delivery.yaml`, `contracts/state/storage.yaml`, `contracts/http/openapi.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/e-limit-reached-stop.json`, `acceptance/fixtures/collection/c-challenge-mid-batch.json`, `acceptance/fixtures/reporting/d-empty-period-coverage-only.json`, `acceptance/fixtures/telegram/m-three-run-states-distinct-text.json`, `acceptance/fixtures/telegram/b-response-lost-unknown-operator-decides.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/web/views/runs.py` | read model cho `SCR-runs` |
| `server/app/web/views/run_detail.py` | read model cho `SCR-run-detail` |
| `server/app/web/templates/runs.html` | ba trạng thái có văn bản khác nhau |
| `server/app/web/templates/run_detail.html` | needs_user / blocked / delivery unknown |
| `tests/contract/test_run_read_model.py` | ánh xạ state → view |
| `tests/integration/test_three_states_distinct.py` | ba chuỗi hiển thị khác nhau |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

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

- `python -m pytest tests/contract/test_run_read_model.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_three_states_distinct.py -q` (PROVISIONAL)
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

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | Nếu `contracts/ui/screens.yaml` thiếu một trạng thái mà `contracts/state/run.yaml` có ⇒ DỪNG và raise CR; **không** tự đặt nhãn hiển thị. |
| `SG-02` | `SCR-settings` có phần `OWNER_DECISION_REQUIRED_SCOPE` (TXN-purge-all). Không hiện thực nút purge. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
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
