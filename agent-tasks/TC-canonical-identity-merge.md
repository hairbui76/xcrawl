---
card_id: TC-canonical-identity-merge
title_vi: Canonical identity, alias và merge có audit trail
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M2
gate: G5
stack_decision: ADR-0006 (Option A / Python) — PROVISIONAL, status proposed
claim_ceiling: IMPLEMENTATION_VERIFIED
owner_modules: [MOD-identity-service]
scenario_refs: [SC07, SC09, SC23, SC29, SC30, SC49]
invariant_refs: [I03, I07, I08, I17]
evidence_manifest_id: EVM-TC-canonical-identity-merge
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-canonical-identity-merge — Canonical identity, alias và merge có audit trail

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
| `contracts/data/identity.md` | `62fd06635c5e29a955f40cc1d56bea9d4dde9d444607fe7c07da5164993468ce` | 20576 |
| `contracts/data/invariants.md` | `9def66cd6e918077a96a730327646c0040acd02a6a4c29135b28e5281e64b36d` | 27782 |
| `contracts/schemas/target.schema.json` | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` | 7283 |
| `contracts/schemas/ingest-receipt.schema.json` | `ff5232f46bb08369ea9af653d652d7782a42ea16798992f2507878c964ac537c` | 16970 |
| `contracts/http/openapi.yaml` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227691 |
| `contracts/reporting/selection.md` | `cc62af2bd476c51efa9b156bae66be6dae3a0bcd712eb79cd1d4ba3a3d5c2fc0` | 34622 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | `a8e57390663d6dc3778ff8036ca4032a91da25f0b85844bd094f393e34f6b5ef` | 5701 |
| `precode/adr/ADR-0004-tag-freeze-point.md` | `64c0793eeca31b6ac0606813adac96fa483e01eb4b81eaef950edfff16fd3194` | 5459 |
| `acceptance/fixtures/identity/README.md` | `a6beae39f431a06104ff797094c79d51b21736a74908271b355bdeb2cf8209e5` | 11369 |
| `acceptance/fixtures/identity/a-merge-doi-arxiv.json` | `32fc87478139d84a69e07a69343e16859e83c2719346e02a96bb63685600b851` | 17539 |
| `acceptance/fixtures/identity/b-post-only-missing-ids.json` | `479a3cf7154950e118896a3bf8c260fc42351e199206edacd11dc1145d2e02fb` | 4410 |
| `acceptance/fixtures/identity/c-identity-conflict.json` | `884c03534f3cbfec034fe859a2c947b788f0ea1be6efffb9ad281091f4d53b60` | 7472 |
| `acceptance/fixtures/identity/g-arxiv-version-v1-v2.json` | `3ce82f6d8b16a893978dc06ec998888b9c15baf095580e7d84e37e95b4017c38` | 9536 |
| `acceptance/fixtures/identity/h-five-posts-thread-one-target.json` | `f3167d8f45a59d992b6c679ec92a74b2acbbeaea9b966d7325ccc3e1e6aa878c` | 9442 |
| `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json` | `e2de531e3b5bbad92946b4f6b3ea5f960bbed7afb687df92252391095e24a624` | 14510 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-canonical-identity-merge`
- **Milestone:** M2 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-identity-service`

**Mục tiêu.** Hiện thực resolve/alias/merge để một canonical identity đã xác định chỉ có một work, xung đột alias đi vào quarantine thay vì merge đoán, và mọi merge để lại audit trail đảo ngược được.

**Non-goals.**

- Không quyết định policy `first_announced` sau merge — `CR-PC02-06` còn OPEN, thuộc PC04.
- Không viết ingest (card 1), không viết report (card 8).
- Không tự sinh DOI khi nguồn thiếu metadata; post-only là target hợp lệ.

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. ADR liên quan: `precode/adr/ADR-0009-identity-alias-target-union.md`, `precode/adr/ADR-0004-tag-freeze-point.md`.
3. Hợp đồng nghiệp vụ: `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/schemas/target.schema.json`, `contracts/schemas/ingest-receipt.schema.json`, `contracts/http/openapi.yaml`, `contracts/reporting/selection.md`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/identity/README.md`, `acceptance/fixtures/identity/a-merge-doi-arxiv.json`, `acceptance/fixtures/identity/b-post-only-missing-ids.json`, `acceptance/fixtures/identity/c-identity-conflict.json`, `acceptance/fixtures/identity/g-arxiv-version-v1-v2.json`, `acceptance/fixtures/identity/h-five-posts-thread-one-target.json`, `acceptance/fixtures/reporting/i-identity-merge-single-first-announced.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — PROVISIONAL (chỉ đúng nếu ADR-0006 được chấp nhận)

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/identity/service.py` | resolve/alias/quarantine/merge |
| `server/app/identity/normalization.py` | chuẩn hóa DOI, arXiv id, arXiv version |
| `server/app/identity/router.py` | HTTP handler cho `identity.resolve_conflict`, `work.get_detail` |
| `server/app/identity/repository.py` | repository port theo bảng của MOD-identity-service |
| `tests/contract/test_identity_normalization.py` | bảng chuẩn hóa từ `contracts/data/identity.md` |
| `tests/integration/test_identity_merge_audit.py` | TXN-identity-merge, audit trail, snapshot bất biến |

Nếu Owner chọn Option B hoặc C ở ADR-0006, **chỉ bảng này và §8 phải viết lại**; §2, §4, §5, §6, §7 không đổi vì hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `identity.resolve_target`
- `identity.record_alias`
- `identity.quarantine_conflict`
- `identity.merge_works`
- `identity.resolve_conflict`
- `work.get_detail`

**Consumes** (chỉ được gọi đúng những operation này):

- `research.fetch_work_metadata`
- `storage.get_health`

**Schema:**

- target tagged union `work | post` → `contracts/schemas/target.schema.json`

**State effects.** `ENT-identity-alias`, `ENT-identity-conflict`, `ENT-identity-merge-audit`, `ENT-work`, `ENT-work-version`, `ENT-post-work` theo `contracts/data/entities.yaml`. Merge chuyển reference, Saved và first-announcement trong **cùng** transaction `TXN-identity-merge`, ghi `merge_audit_id`.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-ingest-service` — internal_only
- `MOD-report-service` — internal_only (chỉ `identity.resolve_target`)
- `MOD-web-ui` — owner_session + CSRF cho `identity.resolve_conflict`

**Được phép gọi:**

- MOD-research-connector (internal)
- MOD-data-store (repository port)

**Đường bị cấm (denied paths):**

- Không gọi AI để đoán identity: `AI output` không được quyền quyết định canonical id (I11).
- Không đổi `saved_snapshot` khi merge (I08/I17): snapshot lịch sử bất biến.
- Không xóa nguồn của alias thua; giữ provenance.

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
| `I03` | một canonical identity → một work |
| `I07` | một canonical work chỉ có một first-announcement |
| `I08` | Save là snapshot bất biến |
| `I17` | merge không đổi bất kỳ snapshot lịch sử nào |

**Transaction và commit point:**

- `TXN-identity-merge` — chuyển reference + Saved + first-announced hook + audit record trong một commit. Vượt `identity_merge_max_moved_rows = 100000` (PROVISIONAL, `CR-PC02-05`) ⇒ chuyển thành `identity_conflict`.

**Race, replay và forbidden effects:**

- Hai lô ingest cùng đề xuất merge ngược chiều ⇒ CAS thua phải đọc lại.
- Merge đồng thời với Save ⇒ Saved active vẫn đúng một, snapshot hash không đổi.
- arXiv v1 rồi v2 ⇒ hai `work_version`, một `work`.

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `VALIDATION_ERROR` | 400, không ghi |
| `NOT_FOUND` | 404 khi work/alias không tồn tại |
| `IDENTITY_CONFLICT` | quarantine, giữ cả hai nguồn, không đoán |
| `CONFLICT` | merge thua CAS hoặc vượt ngưỡng dòng; đọc lại, không ghi đè |
| `IDEMPOTENCY_CONFLICT` | cùng key khác payload |
| `UNAUTHORIZED / CSRF_REJECTED` | `identity.resolve_conflict` là mutation của owner: cookie **AND** CSRF |
| `STORAGE_WRITE_FAILED` | không commit, không tuyên bố đã persist |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC07
- SC09
- SC23
- SC29
- SC30
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `python -m pytest tests/contract/test_identity_normalization.py -q` (PROVISIONAL)
- `python -m pytest tests/integration/test_identity_merge_audit.py -q` (PROVISIONAL)
- `python3 evidence/tools/e0_check.py` — E0 lint do PC09 cung cấp; PC10 **NOT_RUN**

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- `COUNT(work)` sau merge giảm đúng 1; alias map trỏ về work thắng; `COUNT(identity_merge_audit)` tăng đúng 1.
- Tập `saved_snapshot.content_hash` trước và sau merge **bằng nhau** (I17).
- Fixture `c-identity-conflict.json`: 0 merge, đúng 1 hàng `identity_conflict`.
- Fixture `h-five-posts-thread-one-target.json`: 5 post → 1 target, provenance liệt kê đủ 5.

**Evidence artifacts:** log pytest; dump alias map trước/sau; diff tập snapshot hash (phải rỗng).

**Yêu cầu live.** Không cần live.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED`.**

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-01` | `CR-PC02-06` (kế thừa `first_announced` sau merge) còn OPEN. Card này chỉ được cung cấp **điểm móc** trong `TXN-identity-merge` và để `moved_counts.first_announced = null`. Tự chọn policy ⇒ vi phạm scope. |
| `SG-02` | Ngưỡng `identity_merge_max_moved_rows` là PROVISIONAL; nếu dữ liệu thật vượt ngưỡng thường xuyên ⇒ DỪNG và raise CR thay vì nâng ngưỡng. |
| `SG-STACK` | ADR-0006 (Option A / Python) vẫn `proposed`. Mọi đường dẫn ở §3 và mọi lệnh ở §8 là **PROVISIONAL**. Nếu Owner chọn B hoặc C, DỪNG và trả card về Coordinator để viết lại §3/§8; hợp đồng ở §2 không đổi. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-ingest-idempotent-ack-lost` (nguồn gọi chính).
- PC04 đóng `CR-PC02-06` trước khi claim phủ I07.

## §12. Reviewer scope

Reviewer đọc `contracts/data/identity.md`, `contracts/data/invariants.md` §I03/§I17, 6 fixture ở §2. Câu hỏi bắt buộc: có chỗ nào code merge khi thiếu ID chắc chắn không, và snapshot có bị đụng không.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-canonical-identity-merge`
- **Vị trí:** `evidence/runs/TC-canonical-identity-merge/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
