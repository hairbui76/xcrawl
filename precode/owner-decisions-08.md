---
contract_id: CT-precode-owner-decisions-08
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260908-08
issuer: Owner (người dùng của phiên Claude Code này), qua AskUserQuestion, tự đọc bản tóm tắt REQ-A5 do Worker chuẩn bị
issued_at: 2026-09-08
evidence_ref: "Claude Code session session_017CTbS7F4oTr4ZtFYkhdabD, 2026-09-08"
authority_created: AUTH-OWNER-20260908-09
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-08.md (bản gốc của biên bản này)"
  - precode/owner-decisions-06.md §3 (bảng trích dẫn A5-1…A5-8 và hai điều kiện còn mở)
  - precode/owner-decisions-07.md (OD-20260908-07 mục 2 — chốt rằng Owner tự ký)
  - precode/decision-register.md §8.15, §8.15.1
  - contracts/ai/providers.yaml §2.1, §5
requirement_refs: [precode/requirements.csv, REQ-A5, REQ-AC16]
decision_refs: [OD-20260908-06, OD-20260908-07, CR-PC06-OQ03-02, ADR-0010, B13]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-06.md, precode/owner-decisions-07.md, precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-08, vòng tám (một mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Owner đích thân ký REQ-A5 cho Anthropic trên đúng ba
  trang có ngày hiệu lực, và chấp nhận tường minh bảo đảm TC-A5-01. Nó KHÔNG bật adapter nào.
  Hiệu lực thực chất đã được worker-WAI ghi ở §8.15.1; file này là bản ghi song hành theo quy ước.
verification: E0 — self-validation (EV-PC00-15) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260908-08` — 2026-09-08 (vòng tám)

> **File này là bản ghi SONG HÀNH THEO QUY ƯỚC, không phải nơi quyết định.** Hiệu lực thực chất của vòng tám
> — gồm cả việc điền `terms_check.reviewer` trong `contracts/ai/providers.yaml` §2.1 — đã được `worker-WAI`
> ghi ở `precode/decision-register.md` **§8.15.1**. `PKT-PC00-FIX28` tạo file này để vòng tám có cùng hình
> dạng hồ sơ như các vòng khác (file độc lập + anchor baseline + authority trong registry) — **không** để
> quyết lại điều gì. Khi hai bên lệch: **§8.15.1 thắng**.

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260908-08` |
| Người ban hành | **Owner** — qua `AskUserQuestion`, **tự đọc** bản tóm tắt `REQ-A5` do Worker chuẩn bị, trình **trực tiếp** trong phiên |
| Cái đã đọc | Anthropic **Commercial ToS** (eff. **2025-06-17**), **Usage Policy** (eff. **2025-09-15**), **Service Specific Terms** (eff. **2026-06-08**) — trích dẫn đầy đủ ở `precode/owner-decisions-06.md` §3 |
| `evidence_ref` | Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08 |
| Authority phát sinh | **`AUTH-OWNER-20260908-09`** |
| Bản ghi hiệu lực | `precode/decision-register.md` **§8.15.1** (`worker-WAI`) |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260908-08.md` |

## 2. Một quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | Ký xác nhận `REQ-A5` cho **Anthropic** (Claude Sonnet 5 / Claude Opus 5, họ `api_key`) | **Có, ký** — **chấp nhận tường minh** bảo đảm `TC-A5-01` về quyền đối với dữ liệu đầu vào (chính **Owner**, không phải Anthropic, là bên tuyên bố rằng hệ thống này **có quyền** gửi văn bản nghiên cứu của bên thứ ba — abstract arXiv/OpenAlex và tương tự — làm Input) | Quy ước `reviewer = Owner` của `contracts/ai/providers.yaml` §5 nay **đã thỏa** cho **riêng Anthropic**, ở **đúng bản đọc này** (ba trang có ngày ở trên). `CR-PC06-OQ03-02` **đóng**. Việc này **không** đặt `enabled = true` cho adapter nào — điều đó vẫn bị chặn bởi việc xác minh cô lập `B13` (`ISO-03`/`ISO-05` chưa kiểm, `E3 NOT_RUN`), **không liên quan** tới chữ ký này. Kết luận **hết hiệu lực** nếu bất kỳ trang nào trong ba trang được dẫn đổi phiên bản (theo chính luật của `ADR-0010`, Worker đã ghi). |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này: liệu chính sách của **arXiv/OpenAlex/X** có cho phép hệ thống này tái xử lý nội
> dung của họ theo cách ấy hay không (câu hỏi nền của `TC-A5-01`, **khác** với điều khoản của Anthropic) —
> Worker đã nêu như một câu hỏi **riêng, chưa được trả lời**, và chữ ký này **không** giải nó.

## 4. Ghi chú của PC00 — ba ranh giới của chữ ký này

Chữ ký `REQ-A5` là loại quyết định dễ bị đọc rộng nhất trong cả chuỗi, nên ba ranh giới được viết ra:

1. **Hẹp theo nhà cung cấp và theo BẢN ĐỌC.** Chữ ký áp cho **Anthropic**, và cho **đúng ba trang có ngày
   hiệu lực** đã dẫn. Nó **không** nói gì về một nhà cung cấp khác, và **hết hiệu lực** khi một trong ba
   trang đổi phiên bản. `REQ-A5` vì vậy vẫn là một **cổng theo từng adapter**, không phải một ô đã tích một
   lần cho mọi lần sau.
2. **Ký KHÔNG phải bật.** `enabled = true` bị chặn bởi `B13` — xác minh cô lập tiến trình (`ISO-03`,
   `ISO-05`) chưa chạy, `E3` vẫn `NOT_RUN`, và `REQ-AC16` vẫn `BLOCKED`. Hai cổng này **độc lập**: qua cổng
   điều khoản không mở cổng cô lập. Ai đọc "REQ-A5 đã ký" thành "adapter dùng được" là đọc sai đúng chỗ nguy
   hiểm nhất.
3. **Bảo đảm được Owner GÁNH, không phải được giải.** `TC-A5-01` chuyển rủi ro về quyền đối với dữ liệu đầu
   vào sang phía **người dùng dịch vụ**. Owner chấp nhận tường minh — nghĩa là **Owner** tuyên bố có quyền
   gửi abstract của bên thứ ba làm Input. Nhưng **liệu arXiv/OpenAlex/X có cho phép điều đó không** vẫn là
   một câu hỏi **chưa ai trả lời**, và biên bản nói thẳng như vậy. Chấp nhận một bảo đảm không làm cho điều
   được bảo đảm trở thành đúng; nó chỉ định ai chịu trách nhiệm nếu nó sai.

**Vì sao vòng tám tồn tại tách khỏi vòng bảy.** `OD-20260908-07` mục 2 chốt rằng **Owner** phải ký, không
phải một Worker được ủy quyền; nó **cố ý không** ký. Chữ ký là một hành động riêng, ở một biên bản riêng, sau
khi Owner tự đọc. Giữ hai vòng tách nhau là điều khiến trường `reviewer` nói đúng sự thật.

## 5. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/decision-register.md` §8.15.1 | **Bản ghi hiệu lực** (`worker-WAI`) — PC00 **không** chạm |
| `contracts/ai/providers.yaml` §2.1 | `terms_check.reviewer` của **cả hai** mục — do `worker-WAI` điền |
| `precode/decision-register.md` §0 | Đoạn "Cập nhật vòng bảy và vòng tám" |
| `precode/owner-decisions.md` | Dòng trỏ |
| `precode/baseline.json` | Anchor `OD-20260908-08` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260908-09` |
| `precode/requirements.csv` | **Không sửa** — `REQ-AC16` vẫn `BLOCKED`, cổng `B13` không đổi |
