---
contract_id: CT-precode-owner-decisions-06
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260908-06
issuer: Owner (người dùng của phiên Claude Code này), trả lời tiếp nối phiếu nghiên cứu do OD-20260908-05 mục 1 đặt ra
issued_at: 2026-09-08
evidence_ref: "Claude Code session session_017CTbS7F4oTr4ZtFYkhdabD, 2026-09-08"
authority_used: "AUTH-COORD-OQ03 (cha AUTH-OWNER-20260908-06)"
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-05.md mục 1 (vòng năm — 'Research and recommend; Owner gives final approval')"
  - "…/scratchpad/packets/PKT-PC06-FIX-OQ03.md (packet ghi lại câu trả lời tiếp nối)"
  - contracts/ai/providers.yaml §2, §4, §5, §7 (v0.2.0)
  - contracts/ai/tasks.yaml §2 (ba task, model_class, inference_timeout)
  - contracts/data/entities.yaml ENT-provider-config
  - precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md
  - docs/master-plan.md §3 (cổng vào Giai đoạn 3)
requirement_refs: [REQ-OQ03, REQ-A5, REQ-D39, REQ-D40, REQ-D41, REQ-D43, REQ-D44, REQ-D51, REQ-AC16]
decision_refs: [OD-20260907-01, OD-20260907-02, OD-20260907-03, OD-20260907-04, OD-20260908-05, B13, ADR-0010]
producers: [PC00]
consumers: [PC01, PC06, PC07, PC08, PC09]
dependencies: [contracts/ai/providers.yaml, contracts/ai/tasks.yaml, precode/decision-register.md]
scope: >
  Biên bản quyết định vòng sáu: Owner chọn provider và model cụ thể cho hai trong ba tác vụ AI,
  giải REQ-OQ03. Kèm theo là kết quả một lần ĐỌC tài liệu chính thức của Anthropic phục vụ REQ-A5
  (§3) — có URL, ngày đọc và trích dẫn nguyên văn. Biên bản này KHÔNG bật adapter nào:
  `enabled = false` cho cả hai mục, vì cô lập chưa kiểm chứng (§4).
verification: E0 — SELF_VALIDATION; evidence/tools/e0_check.py chạy chỉ đọc. Không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260908-06` — 2026-09-08 (vòng sáu)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260908-06` |
| Người ban hành | **Owner** — câu trả lời tiếp nối `OD-20260908-05` mục 1, mục đó đặt đúng thủ tục "Coordinator nghiên cứu và đề xuất, Owner duyệt" |
| `evidence_ref` | Claude Code session `session_017CTbS7F4oTr4ZtFYkhdabD`, 2026-09-08 |
| Authority của packet ghi nhận | `AUTH-COORD-OQ03` (cha `AUTH-OWNER-20260908-06`) |
| Worker ghi | `worker-WAI`, packet `PKT-PC06-FIX-OQ03`, lease `LEASE-PC06-OQ03` |
| Biên bản trước | `OD-20260907-01` … `OD-20260907-04`, `OD-20260908-05` |

**Hai ghi chú về đánh số, viết ra để không ai phải đoán.**

1. **Không có `precode/owner-decisions-05.md`.** Biên bản vòng năm (`OD-20260908-05`) hiện chỉ tồn tại ở thư
   mục scratch của Coordinator (`…/packets/OWNER-DECISIONS-20260908-05.md`), chưa được chuyển vào `precode/`.
   File này là vòng **sáu** và không lấp chỗ trống đó — xem `CR-PC06-OQ03-04`.
2. **Số của authority lệch số của biên bản.** `AUTH-OWNER-20260908-06` được sinh bởi `OD-20260908-05`, không
   phải bởi biên bản này. Đây là một lệch có thật trong chuỗi số, không phải lỗi chép.

## 2. Quyết định

**Câu trả lời nguyên văn của Owner:**

> sonnet 5 + opus 5 for summary

Đọc theo đúng câu chữ, và ánh xạ sang ba `task_type` có thẩm quyền của `contracts/data/entities.yaml`:

| `task_type` | Model | Adapter | Vì sao |
| --- | --- | --- | --- |
| `summary` | **Claude Opus 5** (`claude-opus-5`) | `anthropic@claude-opus-5` | Owner nói đích danh "opus 5 **for summary**" |
| `label` | **Claude Sonnet 5** (`claude-sonnet-5`) | `anthropic@claude-sonnet-5` | Vế "sonnet 5" của câu trả lời; Owner không nêu task nào khác cho nó |
| `direction_phrasing` | **Claude Sonnet 5** (`claude-sonnet-5`) | `anthropic@claude-sonnet-5` | Owner chỉ khoanh Opus 5 vào `summary`; phần còn lại rơi về vế "sonnet 5" |

Cả hai đều thuộc họ **`api_key`** (Anthropic), **không** phải đường `cli_acp`.

### 2.1 Kiểm cách đọc `direction_phrasing` — packet yêu cầu nói rõ, nên nói rõ

Packet dựng cách đọc trên: *"nhánh nghiên cứu xếp `direction_phrasing` cùng nhóm với `summary` vì cần model
mạnh"*. Đối chiếu `contracts/ai/tasks.yaml`:

- `direction_phrasing` khai `model_class: **strong**` — **cùng lớp** với `summary`, khác `label`
  (`model_class: cheap`).
- Nhưng nó cũng khai `volume_vi: "1 mỗi kỳ"`, `inference_timeout: 180 s`, và `hard_constraints_vi`: *"AI KHÔNG
  chọn thành viên… AI KHÔNG tính mật độ… Khối này KHÔNG phụ thuộc AI để tồn tại"*. Nó là task **diễn đạt**
  trên dữ liệu đã tính xong, không phải task suy luận mở.

**Kết luận: cách đọc đó ĐÚNG một nửa, và nửa đúng đủ để làm theo.** Đúng ở chỗ `direction_phrasing` thật sự là
`model_class: strong` — nên đặt nó lên **Sonnet 5 (model lớp mạnh) là hợp lệ**, không phải một sự hạ cấp. Sai
ở chỗ nếu "cùng nhóm với `summary`" được hiểu là *phải đi cùng Opus 5*, thì nó vượt quá câu trả lời của Owner:
Owner khoanh Opus 5 vào **đúng chữ `summary`**. Vì cả hai model đều thuộc lớp mạnh, hai cách đọc **không** mâu
thuẫn với `tasks.yaml`, và bản ghi này chọn cách sát câu chữ Owner nhất.

**Điểm lệch thật sự nằm ở chỗ khác, và nó là điểm về CHI PHÍ:** `label` — task có khối lượng **lớn nhất**
(mọi post/work, `tasks.yaml` `label.volume_vi`) và được `REQ-D40` khuyến nghị dùng **model rẻ** — nay chạy
trên model **mạnh**. `contracts/ai/providers.yaml` §7 `rules_vi` cho phép tường minh: *"REQ-D40 là khuyến nghị
mặc định (rẻ cho `label`, mạnh cho `summary`), không phải ràng buộc cứng: Owner được phép đặt khác."* Nên đây
**không** là vi phạm hợp đồng. Nó chỉ là dòng chi phí đáng chú ý nhất của lựa chọn này, và Owner nên biết mình
đã chọn nó: nếu về sau muốn hạ chi phí, chỗ đổi là `label`, không phải `summary`.

## 3. REQ-A5 — kết quả đọc tài liệu chính thức của Anthropic

**Ngày đọc: 2026-09-08 (giờ Owner, `Asia/Ho_Chi_Minh`) = `2026-09-07T18:0xZ` UTC.** Công cụ: `WebFetch`
(GET, chỉ đọc). **Không** có lời gọi nào tới `api.anthropic.com`, **không** dùng API key, **không** có một
lần inference nào. Câu hỏi được đặt đúng theo cách dùng THẬT của hệ này: *gắn nhãn và summary tự động, không
người trực, ở quy mô, trên văn bản nghiên cứu của bên thứ ba (metadata arXiv/OpenAlex và tương tự), kết quả
được lưu và dùng lại bên trong một công cụ tự vận hành.*

**Kết luận: `permitted_for_this_use`** — có điều kiện, và điều kiện thuộc về phía mình.

| # | Dữ kiện | Nguồn (đọc 2026-09-08) | Trích dẫn nguyên văn |
| --- | --- | --- | --- |
| A5-1 | Điều khoản nào áp cho đường API key | `https://www.anthropic.com/legal/commercial-terms` (Commercial Terms of Service, effective **June 17, 2025**) | *"They govern Customer's use of Anthropic API keys and any other Anthropic offerings that references these Terms, as well as all related Anthropic tools, documentation and services (the 'Services')."* |
| A5-2 | Usage Policy được nhập vào hợp đồng | cùng trang | *"Customer and its Users may only use the Services in compliance with these Terms, including (a) the Usage Policy ('Usage Policy', which was previously referred to as the Acceptable Use Policy)…each of which is incorporated by reference into these Terms."* |
| A5-3 | Quyền với Output | cùng trang | *"Anthropic agrees that Customer (a) retains all rights to its Inputs, and (b) owns its Outputs."* |
| A5-4 | Phạm vi được phép dùng | cùng trang | *"Subject to these Terms, Anthropic gives Customer permission to use the Services…to power products and services Customer makes available to its own customers and end users."* |
| A5-5 | **Điều kiện thuộc về mình** — quyền đối với Input | cùng trang | *"Customer further represents and warrants that it has all rights and permissions required to submit Inputs to the Services."* |
| A5-6 | Hạn chế duy nhất gần với việc mình làm | `https://www.anthropic.com/legal/aup` (Usage Policy, effective **September 15, 2025**) | *"Utilization of inputs and outputs to train an AI model (e.g., 'model scraping' or 'model distillation') without prior authorization from Anthropic."* |
| A5-7 | Hai nghĩa vụ chung có chạm nội dung bên thứ ba | cùng trang | *"Infringe, misappropriate, or violate the intellectual property rights of a third party"*; *"Plagiarize or submit AI-assisted work without proper permission or attribution."* |
| A5-8 | Điều khoản riêng cho Developer Platform | `https://www.anthropic.com/legal/service-specific-terms` (effective **June 8, 2026**) | Không có mục nào hạn chế tự động hóa, khối lượng, lưu trữ output hay xử lý nội dung bên thứ ba. Mục duy nhất liên quan (Section F — Covered Models): *"Anthropic may retain and perform safety reviews on Inputs, Outputs, and other data regarding Customer's use of the Covered Models."* |

**Điều KHÔNG tìm thấy — và "không tìm thấy" ở đây là một dữ kiện, không phải một chỗ trống.** Toàn bộ danh
sách *Universal Usage Standards* của Usage Policy (82 gạch đầu dòng) đã được đọc hết. **Không** gạch nào cấm:
chạy tự động không người trực, chạy ở khối lượng lớn, gắn nhãn/tóm tắt nội dung của bên thứ ba, lưu output
vào cơ sở dữ liệu riêng, hay dùng lại output trong một công cụ tự vận hành. Commercial ToS cũng không đặt trần
tự động hóa; hạn mức nhịp gọi là cơ chế **kỹ thuật theo tài khoản**, không phải một điều cấm trong điều khoản.

**Hai điều kiện còn mở, ghi ra để không bị đọc thành "đã xong".**

1. **`TC-A5-01` — quyền đối với Input là nghĩa vụ của mình (A5-5).** Hệ này đưa văn bản của bên thứ ba
   (abstract, nội dung post) vào làm Input. Anthropic không cấm việc đó; Anthropic **chuyển trách nhiệm** về
   phía Owner. Cộng với A5-7, đây là chỗ REQ-A5 chạm sang chính sách nguồn của arXiv/OpenAlex/X — một câu hỏi
   khác, chưa được biên bản này trả lời.
2. **`TC-A5-02` — cấm dùng input/output để huấn luyện model (A5-6).** Hiện **không** kích hoạt: embedding là
   model local có sẵn (REQ-D48/D50), hệ không train gì. Nhưng nó chặn trước mọi ý định về sau dùng kho output
   đã lưu để huấn luyện.

**Ba giới hạn của chính lần đọc này.**

- Nội dung được đọc qua `WebFetch` (chuyển trang sang markdown rồi trích). Các câu trên là **trích dẫn do công
  cụ trả về**, không phải HTML thô do người đọc mắt. Đây là `SELF_VALIDATION`.
- Điều khoản **có ngày hiệu lực**: 2025-06-17 (ToS), 2025-09-15 (Usage Policy), 2026-06-08 (Service Specific
  Terms). ADR-0010 §Hệ quả: *"Việc đọc điều khoản là công việc tay… phải làm lại khi provider đổi phiên bản."*
  Kết luận `permitted_for_this_use` hết hiệu lực khi một trong ba trang đổi.
- **`reviewer` không phải Owner.** `contracts/ai/providers.yaml` §5 ghi *"Ở MVP một người dùng, đây là Owner"*
  và *"PC06 KHÔNG đọc thay và KHÔNG đoán"*, trong khi `OD-20260908-05` mục 1 lại giao việc đọc REQ-A5 cho
  *"a Worker… separately"*. Lần đọc này theo vế thứ hai. Hai câu đó lệch nhau — `CR-PC06-OQ03-02`. Vì cả hai
  adapter `enabled = false`, không cổng nào bị đi vòng bởi sự lệch này.

## 4. Cái mà biên bản này **không** làm

1. **Không bật adapter nào.** Cả hai mục `enabled: false`. Cái chặn là **cô lập**, không phải điều khoản:
   `isolation.network_egress` (ISO-03) và tính chất credential-theo-task (ISO-05) là hai tính chất mà đường
   `api_key` **tạo ra** nên không đủ điều kiện mang `not_applicable` theo `providers.yaml` §4 `status_values`
   (*"các tính chất mà kiến trúc đã loại bỏ"*); cách kiểm cả hai đều đòi một lần chạy quan sát được, mà
   E3 = `NOT_RUN` và `secret.issue_task_credential` chưa có mã. Lập luận đầy đủ nằm ở
   `contracts/ai/providers.yaml` §2.1 `isolation_determination_vi`.
2. **Không tạo hàng `ENT-provider-config` nào**, không đặt `secret_ref`, không chạm secret store.
3. **Không mở allowlist fallback.** §6 chỉ nhận adapter `enabled = true`; hiện không có adapter nào như vậy.
4. **Không đổi REQ-AC16.** Hai adapter này là `api_key`; đường không-API-key vẫn phụ thuộc adapter `cli_acp`,
   và luật báo cáo `BLOCKED` (không phải `FAIL`) của §4 giữ nguyên.
5. **Không nâng trần claim của file nào.** `contracts/ai/providers.yaml` v0.2.0 vẫn `DRAFT_FOR_REVIEW`.
6. **Không đóng finding nào**, và không tự nhận đã cập nhật `precode/requirements.csv` /
   `precode/decision-register.md` — xem §6.

## 5. Cổng Giai đoạn 3

`docs/master-plan.md` §3 viết: *"Cổng vào: **`REQ-OQ03` phải được Owner trả lời.**"* Cổng ấy đòi câu trả lời,
**không** đòi một adapter đã bật. Câu trả lời nay đã có (§2), nên cổng vào **được thỏa về mặt quyết định**.
Việc thực sự **gọi được model** vẫn cần: (a) một lần kiểm chứng cô lập (E3), (b) một `secret_ref` thật, và
(c) hai điều kiện §3. Ba thứ đó không thuộc phạm vi cổng vào M3, nhưng chúng chặn việc bật adapter.

## 6. Truy vết — và ba nơi **chưa** được ghi

| Nơi ghi nhận | Trạng thái |
| --- | --- |
| `contracts/ai/providers.yaml` §2.1 (v0.1.0 → 0.2.0) | ✅ **đã ghi** — hai mục adapter, `enabled: false` |
| `precode/owner-decisions-06.md` (file này) | ✅ **đã ghi** |
| `precode/decision-register.md` §8.15 + §0 legend + §5 hàng `REQ-OQ03` | ❌ **CHƯA** — `BLOCKED_LEASE`, xem dưới |
| `precode/requirements.csv` hàng `REQ-OQ03` (`ĐX` → `XN`, notes) | ❌ **CHƯA** — `BLOCKED_LEASE` |
| `precode/change-control.md` §10 `CR-PC06-OQ03-*` | ❌ **CHƯA** — `BLOCKED_LEASE` |
| `agent_profile/registry.json`, `precode/baseline.json`, `precode/gates.yaml`, `acceptance/traceability.csv` | ❌ **ngoài lease** của packet này; cần packet khác |

**Vì sao ba dòng đỏ là `BLOCKED_LEASE` chứ không phải "quên làm".** `LEASE-PC06-OQ03` và
`LEASE-PC07-TELEGRAM` (worker-WT, `PKT-PC07-FIX-TELEGRAM`, dispatch 01:01 so với 01:06 của packet này) **cùng
liệt kê** ba file đó. `protocol.md` §2 nói thẳng: *"default lease độc quyền toàn physical path; chỉ runtime có
range-lock đã kiểm chứng mới được chia vùng (bộ profiles này **không** bật range-sharing)"* — nên một lease
"chỉ một hàng" vẫn là lease toàn file, và hai lease chồng nhau. Quan sát trong phiên (`sha256`, giờ UTC):

| File | 18:02Z | 18:12Z | 18:15Z |
| --- | --- | --- | --- |
| `precode/decision-register.md` | `058621d0…` | `aaaff446…` | `d98f0174…` |
| `precode/change-control.md` | `0b3d2bfa…` | `0293be59…` | `b22a9283…` |
| `precode/requirements.csv` | `d3e150e3…` | `d3e150e3…` | `36138c9f…` |

Ba file đổi bytes **hai lần trong mười ba phút** và `evidence/handoffs/PC07-TELEGRAM-handoff.md` chưa tồn tại
⇒ writer kia **đang chạy**, chưa quiesce. Ghi đè lên đó là đúng công thức của một lost update.
`worker.md` (*"Baseline drift → giữ nguyên quan sát, trả `STALE_BASELINE`, chờ packet mới"*) và `protocol.md`
§5 (*lease overlap ⇒ `BLOCKED_LEASE`; cấm "tự dùng lease của agent khác"*) đều dẫn tới cùng một hành động:
**dừng trước khi ghi**. Văn bản đúng-để-dán cho cả ba file nằm trong `evidence/handoffs/PC06-OQ03-handoff.md`
§5, để packet kế tiếp không phải làm lại việc này.

## 7. Change request phát sinh

| CR | Gửi tới | Nội dung một dòng |
| --- | --- | --- |
| `CR-PC06-OQ03-01` | PC06 | `isolation` trong `example_entry` chỉ có 3 ô trạng thái, trong khi §4 đòi **5** tính chất: ISO-04 (Telegram) và ISO-05 (phạm vi credential) không có chỗ ghi |
| `CR-PC06-OQ03-02` | PC06 + Owner | §5 nói *"PC06 KHÔNG đọc thay"* và `reviewer` *"đây là Owner"*, nhưng `OD-20260908-05` mục 1 giao việc đọc cho **Worker**; cần chốt ai là `reviewer` hợp lệ, và Owner có ký xác nhận lần đọc §3 hay không |
| `CR-PC06-OQ03-03` | PC06 + PC01 | `usage_reporting: exact` đúng cho **token**, nhưng `cost_micro_usd` không do API trả và bảng giá nằm sau redirect ngoài allowlist ⇒ phải đi đường `unknown`, cấm ghi `0` (I14) |
| `CR-PC06-OQ03-04` | Coordinator | `precode/owner-decisions-05.md` không tồn tại; `OD-20260908-05` chỉ sống trong scratch của Coordinator |
| `CR-PC06-OQ03-05` | Coordinator + Owner | Quyền mạng: `docs.anthropic.com` **301 → `platform.claude.com`** và `www.anthropic.com/pricing` **301 → `claude.com`**; chỉ `www.anthropic.com/legal/*` đọc được. Muốn pin `anthropic-version`, chuỗi model id và bảng giá từ nguồn chính thức thì phải mở thêm host — đúng hình dạng `CR-PC00-27` (`help.openalex.org`) |
| `CR-PC06-OQ03-06` | Coordinator | Hai lease chồng nhau trên 3 file (§6). Cần một packet mới với baseline mới sau khi `worker-WT` handoff |
| `CR-PC06-OQ03-07` | PC02 | `entities.yaml` `ENT-provider-config.terms_check_note_vi` viết *"giai đoạn Pre-code không có mạng nên chưa nhà nào được đọc"* — nay **sai một phần**: Anthropic đã được đọc dưới một quyền mạng hẹp |
