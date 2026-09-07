---
contract_id: CT-tasks-template
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs: [SRC-PLAN §15, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §14.1, SRC-PLAN §14.3, SRC-PLAN §16, SRC-SPEC §13]
requirement_refs: [REQ-OQ02, REQ-S6.3-01]
decision_refs: [ADR-0006, "baseline §5 hàng Stack (PROVISIONAL)"]
invariant_refs: []
producers: []
consumers: []
dependencies:
  - contracts/ports.yaml
  - contracts/modules.yaml
  - contracts/errors.yaml
  - contracts/data/entities.yaml
  - acceptance/scenarios.yaml
  - evidence/manifest.schema.json
  - precode/gates.yaml
scope: >-
  Mẫu bắt buộc cho mọi task card giao cho agent coding. Định nghĩa mười mục của SRC-PLAN §15 cộng bốn
  mục vận hành (baseline pin, dependencies, reviewer scope, expected evidence manifest). Một card thiếu
  bất kỳ mục nào trong mười bốn mục này không được phát hành.
verification: >-
  Kiểm bằng script đếm heading (EV-PC10-02, SELF_VALIDATION). E0 lint của PC09 (evidence/tools/e0_check.py)
  chưa được PC10 chạy — NOT_RUN.
claim_ceiling: DRAFT_FOR_REVIEW
---

# TEMPLATE — Task card chuẩn cho agent coding

Mẫu này hiện thực SRC-PLAN §15 nguyên văn: mười mục bắt buộc, cộng bốn mục vận hành mà PKT-PC10 yêu cầu.
Mục tiêu duy nhất: **agent nhận card không phải nhớ cuộc trò chuyện nào và không phải đoán bất cứ điều gì
về giao tiếp hay trạng thái.**

Sao chép file này, thay mọi `<…>`, xóa mọi dòng hướng dẫn in nghiêng. Đặt tên `TC-<kebab-case>.md`.

## Điều kiện phát hành card

| Điều kiện | Vì sao |
| --- | --- |
| G4 đã pass cho phạm vi định giao | SRC-PLAN §11 PC10 "Đầu vào: G4 cho phạm vi định giao" |
| G5 đã pass **và** Owner ra lệnh bắt đầu | SRC-PLAN §12 G5: "Bắt đầu coding phạm vi được giao **khi user yêu cầu**" |
| ADR-0006 đã được Owner trả lời | Chưa chọn stack thì §3 và §8 không có đường dẫn/lệnh đúng |
| Mọi hash ở §0 kiểm lại còn khớp | Card pin baseline; lệch ⇒ `STALE` (`INV-06`/`INV-09` của `precode/gates.yaml`) |

Chưa đủ bốn điều kiện thì card tồn tại như tài liệu review, **không** phải lệnh thi công.

---

## §0. Baseline pin

*Bảng hash là hợp đồng của card. Không viết "latest", không viết "bản mới nhất".*

**Pin epoch:** `<ID epoch — hiện hành là PC10-PIN-P3b-20260908; epoch cũ ví dụ PC10-PIN-P3-20260908>`

*Card là nguồn chuẩn của tên epoch. File nào khác khẳng định pin hiện hành thì phải đọc tên từ card, không
chép tay — finding `F-A2R1-03`; EV-PC10-01 phép kiểm (k) ép điều này bằng máy.* — nói rõ hash được **tính lại trực tiếp** hay **chép từ
frozen candidate** nào; nếu có file lệch khỏi frozen candidate, liệt kê đúng những file đó.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `<sha256>` | `<bytes>` |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `<sha256>` | `<bytes>` |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `<path>` | `<sha256>` | `<bytes>` |

**`dispatch_status:`** *(tùy chọn — chỉ có trên card đã được Coordinator phát packet).* Một dòng ở §0,
dạng `dispatch_status: DISPATCHED (<decision id>, <ngày>)`. Nó là **trạng thái điều phối**, không phải một
mục nghĩa vụ: nó không được đổi §1–§13, không được nới điểm dừng ở §10, và **không** thay TASK_PACKET —
quyền ghi vẫn đến từ packet (lease + write set), không từ dòng này. Card chưa được phát packet thì bỏ dòng
này đi, đừng viết `dispatch_status: NOT_DISPATCHED`.

Liệt kê rõ file **cố ý không pin hash** và lý do. Hiện tại đó là sáu file của PC09 (`acceptance/scenarios.yaml`,
`acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`,
`evidence/index.json`) cộng `evidence/tools/e0_check.py`, vì PC09-FIX1 chạy song song — chúng được dẫn bằng
**đường dẫn + SC id**, và agent đọc bản mới nhất trước khi bắt đầu.

## §1. Task ID, mục tiêu và non-goals

*SRC-PLAN §15.1: "một kết quả nghiệp vụ có thể kiểm riêng". Không có card "làm toàn bộ backend" hay
"làm toàn bộ UI".*

- **Task ID:** `TC-<kebab>`
- **Milestone:** `<M0…M8>` (SRC-SPEC §13) · **Cổng:** `<G5 | SP1>` (SRC-PLAN §12)
- **Module sở hữu:** `<MOD-…>` (tên lấy từ `contracts/modules.yaml`)

**Mục tiêu.** `<một đoạn: kết quả nghiệp vụ nào được coi là đạt, đo bằng gì>`

**Non-goals.** `<liệt kê; mỗi mục chỉ tới card khác hoặc tới quyết định còn mở>`

## §2. Read set

*SRC-PLAN §15.2: spec refs, ADR, contract versions/hash và fixture bắt buộc.*

Bảng ở §0 **là** read set kèm hash. Ở đây chỉ ghi thứ tự đọc đề nghị và lý do từng nhóm:
ADR → hợp đồng nghiệp vụ → hợp đồng nền (`ports.yaml`, `modules.yaml`, `capabilities.yaml`,
`errors.yaml`, `retry-policy.yaml`, `entities.yaml`) → fixture.

## §3. Write set

*SRC-PLAN §15.3: đường dẫn source/test cụ thể **sau khi chọn stack**; file contract dùng chung mặc định
read-only.*

> **Stack đã chốt: Option B** — Python cho `server/`, `collector/`, `worker/`, `probe/`; TypeScript cho
> `web/` (`OD-20260907-01` mục 3; ADR-0006 `accepted`). Phân chia ngôn ngữ là **ACCEPTED**. Vẫn
> `PROVISIONAL`: **đường dẫn cụ thể** (chưa có repo triển khai) và **framework** (ADR-0006 không nêu tên —
> cần chọn thì DỪNG và raise CR). Layout đầy đủ ở `agent-tasks/README.md` §5.3. Đổi layout chỉ sửa §3 và §8.

| Đường dẫn | Vai trò |
| --- | --- |
| `<path>` | `<vai trò>` |

Câu bắt buộc: *"Mọi file không nằm trong bảng này là read-only. Toàn bộ `contracts/`, `acceptance/`,
`precode/` là read-only với card này."*

## §4. Consumes / produces

*SRC-PLAN §15.4: exact operation IDs, schema và state effects; **không tự tạo endpoint gần giống**.*

- **Produces:** operation card này hiện thực — ID lấy nguyên văn từ `contracts/ports.yaml`.
- **Consumes:** operation card này được phép gọi — cũng lấy nguyên văn.
- **Schema:** trỏ tới file trong `contracts/schemas/` hoặc tới hợp đồng khai hình dạng.
- **State effects:** transition ID cụ thể trong `contracts/state/*.yaml` (`T-RUN-…`, `T-AN-…`, `T-RP-…`,
  `T-DL-…`, `T-ST-…`), không mô tả bằng lời chung chung.

## §5. Allowed communication

*SRC-PLAN §15.5: module/capability allowlist và denied paths. `contracts/modules.yaml` khai default deny.*

- **Được gọi bởi:** `<MOD-… — auth_scope>`
- **Được phép gọi:** `<MOD-… / hệ thống ngoài>`
- **Đường bị cấm:** trích denied case (`NC-…`) và forbidden edge (`FE-…`) áp dụng cho card.
- **Bảng ranh giới mã lỗi (ruling R5-01) là bắt buộc trên mọi card:** `UNAUTHORIZED` cho principal sai lớp qua
  HTTP · `FORBIDDEN_EDGE` cho cạnh không có trong `allowed_edges` · `CAPABILITY_DENIED` cho thiếu capability
  tiến trình/mạng/filesystem/tool · `CSRF_REJECTED` (403, không hủy phiên) cho mutation owner thiếu CSRF.
  Trả **sai mã** cũng là FAIL. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.
- **Bảo mật:** `owner_session` cho mutation = `ownerSessionCookie` **AND** `ownerCsrfToken` trong một
  security requirement; collector/analysis worker dùng bearer riêng; mọi route `backup.*` chỉ nhận
  `backupOperatorToken`.

## §6. Invariants và transaction

*SRC-PLAN §15.6: điểm commit, replay, race và forbidden effects.*

| Invariant | Nội dung |
| --- | --- |
| `I…` | `<phát biểu>` |

- **Transaction và commit point:** `TXN-…`, những hàng nào cùng commit, ACK phát sau điểm nào.
- **Race / replay / forbidden effects:** mỗi mục là một tình huống cụ thể có oracle đếm được.

## §7. Error obligations

*SRC-PLAN §15.7: từng error code và đích trạng thái; ai retry; khi nào phải dừng.*

| Mã lỗi | Nghĩa vụ |
| --- | --- |
| `<CODE>` | `<trạng thái đích, ai retry, dữ liệu giữ, hành vi bị cấm>` |

Mã lỗi lấy từ `contracts/errors.yaml`. **Không tạo mã mới trong code.** Error envelope: `code`, `scope`,
`retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có; không lộ
transcript/key/cookie.

## §8. Verification

*SRC-PLAN §15.8: scenario IDs, command sẽ chạy, oracle, evidence artifacts và yêu cầu live nếu có.*

- **Scenario:** SC ID từ `acceptance/scenarios.yaml`. Dải hiện tại là **SC01–SC53** và mọi SC đều có ít nhất
  một fixture (ruling R5-02). `SC49` (quét default-deny 36 cạnh) là **bắt buộc trên mọi card**.
- **Lệnh sẽ chạy:** PROVISIONAL theo ADR-0006.
- **Oracle:** phải đo được bằng **đếm hàng, hash hoặc so chuỗi** — không phải bằng đọc log.
- **Evidence artifacts:** log đã che secret, DB assertion, trace, ảnh chụp/receipt.
- **Yêu cầu live:** nói rõ điều gì chỉ chứng minh được bằng E3/E4 và **không** thuộc card.
- Mục nào chưa chạy ghi **`NOT_RUN`**. Không tạo log pass giả (SRC-PLAN §14.1).

## §9. Completion ceiling

*SRC-PLAN §15.9: claim tối đa là contract/implementation/integration/live, không nói rộng hơn.*

**Tối đa: `<một nhãn của SRC-PLAN §2>`.** Tập nhãn hợp lệ, không được mở rộng: `DRAFT_FOR_REVIEW`,
`CONTRACT_READY`, `IMPLEMENTATION_VERIFIED`, `INTEGRATION_VERIFIED`, `LIVE_FEASIBILITY_VERIFIED`,
`PRODUCT_ACCEPTED`. Card code thường dừng ở `IMPLEMENTATION_VERIFIED`; card probe ở
`LIVE_FEASIBILITY_VERIFIED`; một nhánh chưa có đường chứng minh dừng ở `CONTRACT_READY`.

Mẫu claim bắt buộc theo SRC-PLAN §14.3: claim + baseline + requirements covered + evidence manifest IDs +
observed result + **not established** + open issues + review type. Tự kiểm là `SELF_VALIDATION`; tuyệt đối
không viết "independent audit passed".

## §10. Stop-and-report

*SRC-PLAN §15.10: thiếu contract, B chưa đóng, API khác tài liệu, cần capability ngoài phạm vi, test oracle
mâu thuẫn.*

| ID | Điều kiện dừng |
| --- | --- |
| `SG-…` | `<điều kiện>` |

Mọi card **phải** mang đủ các stop chung: stack còn PROVISIONAL, chưa qua G5, file PC09 chưa tồn tại,
hash lệch, hợp đồng mâu thuẫn, cần cạnh giao tiếp ngoài registry. Khi dừng: báo Coordinator với trạng thái
(`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng.
**Không** sửa hợp đồng, fixture hay test expectation để đi tiếp.

## §11. Dependencies

Card nào phải xong trước, và card này là dependency của card nào. Nói rõ cái nào chặn *bắt đầu* và cái nào
chỉ chặn *claim đầy đủ*.

## §12. Reviewer scope

Reviewer phải đọc chính xác những file nào, và **câu hỏi review bắt buộc** — một câu hỏi có/không mà nếu
trả lời sai thì card FAIL. Reviewer không cần đọc phần còn lại của hệ thống.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-<Task ID>`
- **Vị trí:** `evidence/runs/<Task ID>/manifest.json`
- **Schema:** `evidence/manifest.schema.json` (PC09; không pin hash). Nó hiện thực 8 nhóm trường của
  SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn.
  Đăng ký run vào `evidence/index.json`.
- **Bắt buộc:** `spec_sha256`, `contract_hashes` copy nguyên văn từ §0, `review_type` (self/independent),
  mọi mục chưa chạy ghi `NOT_RUN`.

---

## Những điều agent nhận card không bao giờ được làm

Trích SRC-PLAN §15 đoạn cuối, áp dụng cho mọi card:

- Sửa test expectation để hợp thức hóa implementation.
- Thêm edge giao tiếp ngoài registry.
- Ghi DB qua đường tắt.
- Bật fallback provider chưa được cấu hình.
- Rewrite nguồn chuẩn khi phát hiện hợp đồng sai — đúng cách là **change request có bằng chứng và đề xuất**
  (`precode/change-control.md`).
