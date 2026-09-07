---
contract_id: CT-precode-owner-decisions-02
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260907-02
issuer: Owner (người dùng của phiên Claude Code này), chỉ thị bằng văn bản trực tiếp trong phiên
issued_at: 2026-09-07
evidence_ref: "Claude Code session session_0156UBBHDSeC9soECzSVUb3U (tiếp nối session_017QmDJtMqD9o1z79waqSB9W), 2026-09-07"
authority_created: AUTH-OWNER-20260907-03
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260907-02.md (bản gốc của biên bản này)"
  - precode/owner-decisions.md (OD-20260907-01 — biên bản vòng một)
  - precode/adr/ADR-0011-frameworks-and-toolchain.md
  - docs/master-plan.md §Giai đoạn 0, §Giai đoạn 1
  - agent_profile/protocol.md §2
requirement_refs: [precode/requirements.csv]
decision_refs: [OD-20260907-01, ADR-0011, ADR-0006, PROV-PC00-07, PROV-PC00-08]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions.md, precode/decision-register.md, precode/adr/, precode/baseline.json, docs/master-plan.md]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-07, vòng hai (năm mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó phê chuẩn ADR-0011, mở cổng vào Giai đoạn 0 và
  Giai đoạn 1 của docs/master-plan.md, và ghi lại chế độ vận hành cho việc ghi mã cùng rủi ro
  còn lại của chế độ đó.
verification: E0 — self-validation (EV-PC00-08); không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260907-02` — 2026-09-07 (vòng hai)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260907-02` |
| Người ban hành | **Owner** — người dùng của phiên Claude Code này; chỉ thị bằng văn bản trực tiếp: *"accept ADR-0011, start phase 0 and 1"* và *"I accept, continue but you can spawn up to 10 subagents Opus high effort"* |
| `evidence_ref` | Claude Code session `session_0156UBBHDSeC9soECzSVUb3U` (tiếp nối `session_017QmDJtMqD9o1z79waqSB9W`), 2026-09-07 |
| Authority phát sinh | **`AUTH-OWNER-20260907-03`** — parent của **mọi** Worker packet thuộc Giai đoạn 0 và Giai đoạn 1 |
| Biên bản trước | `OD-20260907-01` — `precode/owner-decisions.md` (25 mục, authority `AUTH-OWNER-20260907-02`) |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260907-02.md` do Coordinator phát |

### Chuỗi authority tính đến biên bản này

Ba grant của Owner cộng dồn; không grant nào thay thế grant trước, và không grant nào nới rộng grant cha.
Bảng này trùng khớp `agent_profile/registry.json` khóa `authorities` (đăng ký ở `PKT-PC00-FIX16`).

| Authority | Người ban hành · ngày | Phạm vi | Biên bản | Evidence |
| --- | --- | --- | --- | --- |
| `AUTH-OWNER-20260906-01` | Owner · 2026-09-06 | Phiên soạn **tài liệu** cho toàn bộ deliverable Pre-code `PC00`–`PC10` (SRC-PLAN §4); parent của mọi packet Coordinator→Worker/Auditor của giai đoạn đó. **Chỉ tài liệu**: không mã sản phẩm, không external effect | — (chỉ thị trực tiếp) | Claude Code session `session-01BAnmhQcMCXY2V66NH6c1PY`, 2026-09-06 (nguyên văn trích ở coordination baseline §1) |
| `AUTH-OWNER-20260907-02` | Owner · 2026-09-07 | Phê chuẩn `OD-20260907-01` (25 mục): B01–B17 `RATIFIED`, `AMD-B01..B17` và `ADR-0001..ADR-0010` `ACCEPTED`, stack **B**; **ủy quyền** lựa chọn framework cho Coordinator ("You pick, record as ADR") → `ADR-0011`. **Không** quyết `REQ-OQ03`, **không** tạo bằng chứng runtime | `precode/owner-decisions.md` | Claude Code session `session_017QmDJtMqD9o1z79waqSB9W`, 2026-09-07 |
| `AUTH-OWNER-20260907-03` | Owner · 2026-09-07 | Phê chuẩn `OD-20260907-02` (5 mục): `ADR-0011` `accepted`; **lối vào** Giai đoạn 0 và Giai đoạn 1 của `docs/master-plan.md`; parent của **mọi** Worker packet thuộc hai giai đoạn đó. Trần claim của đầu ra là `IMPLEMENTATION_VERIFIED`, **không bao giờ** INTEGRATION/LIVE. **Không** quyết `REQ-OQ03`, **không** đổi `product_status`, **không** đóng finding nào | `precode/owner-decisions-02.md` (file này) | Claude Code session `session_0156UBBHDSeC9soECzSVUb3U`, 2026-09-07 |

**Điều bảng này không nói.** Không grant nào trong ba grant trên bật `ENFORCED`. `agent_profile/registry.json`
giữ `operational_enforcement_status: NOT_IMPLEMENTED`, và khóa mới `coding_phase.enforcement` cũng là
`NOT_IMPLEMENTED` — lease ở giai đoạn mã vẫn là kỷ luật bằng thông điệp (`PROV-PC00-08`), không phải khoá thật.

**Quy tắc chuyển ngữ.** File này ghi lại nguyên nội dung biên bản. Cột "Quyết định của Owner" là câu
trả lời **nguyên văn**; cột "Hiệu lực" là hệ quả do **chính biên bản** nêu, không phải suy diễn của PC00.
Ở đâu PC00 thêm ghi chú, ghi chú đó nằm ngoài bảng và được đánh dấu rõ (§4, §5).

## 2. Năm quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | `ADR-0011` framework và toolchain | **Accepted** | `ADR-0011` status `provisional-accepted` → `accepted`, `ratified_by: OD-20260907-02`; dòng trong phiếu trả lời được điền |
| 2 | Bắt đầu ghi mã: Giai đoạn 0 (bố cục repo + CI) và Giai đoạn 1 (M1: kho dữ liệu, ingest, auth, storage readiness) theo `docs/master-plan.md` | **Start** | Cổng G5 được cấp lối vào cho các card Giai đoạn 1: `TC-ingest-idempotent-ack-lost`, `TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness`; Giai đoạn 0 đóng `G5-X4` (bố cục repo) |
| 3 | Chế độ vận hành cho mã | Hàm ý bởi mục 2 (ruling của Coordinator, đã khai báo): `agent_profile/protocol.md` §2 giới hạn `DOCUMENTARY_DRAFT` cho tài liệu và đòi runtime guard cho chế độ `ENFORCED`, những guard đó **không tồn tại**; chỉ thị tường minh của Owner đứng trên hồ sơ đã pin (`instruction_precedence` của registry). Vì vậy việc ghi mã tiến hành dưới **đúng** cơ chế đã dùng cho tài liệu: lease độc quyền theo dõi bằng thông điệp, tập ghi chính xác, và review độc lập; **rủi ro còn lại (không có cưỡng chế ở mức hệ điều hành)** được ghi tại đây và trong sổ đăng ký quyết định | Ghi thành `PROV-PC00-08` (ruling của Coordinator dưới chỉ thị của Owner; **Owner có thể phản đối**) |
| 4 | Tải phụ thuộc | Hàm ý bởi mục 2: cài các gói đã khai báo từ PyPI/npm được phép cho Worker (đó là một phần của việc build, không phải side effect sản phẩm); **không** dùng mạng cho việc khác; **không** secret; **không** gọi thật X/Telegram/AI (E3 vẫn `NOT_RUN`) | Ghi trong dòng capability của các packet giai đoạn |
| 5 | Ngân sách subagent | **Tối đa 10** subagent Opus, high effort, cho giai đoạn này | Sổ của Coordinator |

## 3. Trần claim của Giai đoạn 0 và 1

Nguyên văn biên bản:

> Trần claim cho đầu ra Giai đoạn 0/1: **`IMPLEMENTATION_VERIFIED`** là mức cao nhất (E1 contract test trên
> fixture + E2 fault injection ở đâu card đòi), **không bao giờ** INTEGRATION/LIVE. Trạng thái sản phẩm giữ
> `NOT_READY_FOR_PRODUCT_CODE` cho tới khi G5 đạt đầy đủ và bằng chứng Giai đoạn 1 được đăng ký.

## 4. Những gì quyết định này **không** làm

Bốn điều dưới đây do PC00 ghi thêm để không ai đọc rộng hơn văn bản. Chúng đều suy trực tiếp từ §2 và §3
của chính biên bản, không thêm ràng buộc mới.

1. **Không nâng trần claim của bộ hợp đồng.** `OD-20260907-01` §4 vẫn là luật cho `precode/`, `contracts/`
   và `acceptance/`: chỉ bốn phạm vi mà `A2-R4` nêu mới đủ điều kiện `CONTRACT_READY`, và chỉ ở mức E0.
   Mục 2 mở lối vào **viết mã**, không đổi nhãn của một file hợp đồng nào.
2. **Không tạo bằng chứng runtime.** Mọi mục `KC` vẫn `KC`. `REQ-AC16` vẫn `BLOCKED` cho tới khi một probe
   CLI/ACP đạt. E3 và E4 vẫn `NOT_RUN` — biên bản nói thẳng điều đó ở mục 4.
3. **Không giải `REQ-OQ03`.** Provider và model vẫn `OWNER_DECISION_REQUIRED`, vẫn chặn M3. Biên bản vòng
   hai không nhắc tới mục này, và im lặng **không** phải là một quyết định.
4. **Không đóng finding nào.** Các finding của A1/A2 sống theo vòng đời riêng (`protocol.md` §8) và cần xác
   minh độc lập trên epoch mới. Cấp lối vào một giai đoạn không phải là disposition của một finding audit.

## 5. Ghi chú của PC00 về hai mục có sắc thái

Hai mục dễ bị đọc thành nhiều hơn điều biên bản nói:

- **Mục 1 (`ADR-0011`).** Owner phê chuẩn **nội dung** của ADR, không chỉ việc đã ghi nó. Điều đó đổi
  `PROV-PC00-07` từ `PROVISIONAL` (ruling của Coordinator dưới ủy quyền) sang `ACCEPTED (OD-20260907-02)`.
  Nhưng điều khoản "Owner có thể phản đối" trong `ADR-0011` **không** vì thế mà mất nghĩa lịch sử: bốn hàng
  `Test`, `Lint / format`, `CI`, `Đóng gói / triển khai` được ADR ghi rõ là **chưa từng cân nhắc phương án
  nào** (`F-A2R7-05`). Một phê chuẩn trọn gói không biến bốn hàng đó thành đã-được-cân-nhắc; nó chỉ nói
  Owner chấp nhận chúng làm mặc định. Đảo bất kỳ hàng nào trong bốn hàng ấy vẫn **không tốn gì ở phía hợp
  đồng** — vẫn chỉ sửa card và mã.
- **Mục 3 (chế độ vận hành).** Đây là chỗ duy nhất trong biên bản mà một điều **không** được Owner phát biểu
  thành lời: biên bản tự khai nó là *"hàm ý bởi mục 2"* và là *"ruling của Coordinator"*. Vì vậy nó được ghi
  là `PROV-PC00-08` (`PROVISIONAL`), **không** phải `ACCEPTED (OD-20260907-02)` — dù nó nằm trong cùng một
  biên bản với bốn mục kia. Rủi ro còn lại phải đọc đúng: `DOCUMENTARY_DRAFT` không tạo bảo đảm ở mức hệ điều
  hành (`protocol.md` §2), nên "lease độc quyền" ở giai đoạn mã vẫn là **kỷ luật bằng thông điệp**, không phải
  một khoá thật. Một agent đi chệch tập ghi của mình sẽ **không** bị nền tảng chặn; nó chỉ bị phát hiện ở
  handoff và audit.

## 6. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/owner-decisions.md` | Dòng trỏ tới biên bản vòng hai này |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `status: accepted`, `ratified_by: OD-20260907-02`, `ratified_at`, `evidence_ref`; banner ở mục "Trạng thái" |
| `precode/adr/README.md` | Hàng chỉ mục `ADR-0011` → `accepted`; đoạn "ngoại lệ về thẩm quyền" được cập nhật |
| `precode/decision-register.md` §8 | `PROV-PC00-07` → `ACCEPTED (OD-20260907-02)`; `PROV-PC00-08` mới |
| `precode/decision-register.md` §8.10 | Hàng quyết định cho lối vào Giai đoạn 0 và Giai đoạn 1 |
| `precode/owner-decision-request.md` | Dòng `ADR-0011 frameworks` trong phiếu trả lời được điền **accept** |
| `precode/baseline.json` | Anchor `OD-20260907-02`; anchor `ADR-0011` cập nhật trạng thái |
| `precode/gates.yaml`, `precode/review.md` | **Chưa làm** ở gói này — thuộc PC09 (`CR-PC00-20`) |
| `agent_profile/registry.json` | `ratification_evidence_02`, bảng `authorities` (ba grant) và `coding_phase` (`PHASE_0_1_IN_PROGRESS`, `enforcement: NOT_IMPLEMENTED`) — thêm ở `PKT-PC00-FIX16` (`CR-PC00-21` đã giải) |
| `agent-tasks/` (PC10) | Bốn card Giai đoạn 1 được nêu đích danh ở mục 2; nội dung card không đổi vì quyết định này |
