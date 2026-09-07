---
contract_id: CT-precode-owner-decisions-04
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260907-04
issuer: Owner (người dùng của phiên Claude Code này), qua phỏng vấn AskUserQuestion do Coordinator thực hiện
issued_at: 2026-09-07
evidence_ref: "Claude Code session (Coordinator), 2026-09-07"
authority_created: AUTH-OWNER-20260907-05
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260907-04.md (bản gốc của biên bản này)"
  - precode/owner-decisions-03.md (OD-20260907-03 — hai mục còn mở mà vòng này đóng)
  - contracts/ops/collector-probe.md §3, §4, §6, §7
  - contracts/retry-policy.yaml (research_connector_rate_limit)
  - evidence/handoffs/TC-x-feasibility-probe-handoff.md §"Owner must do"
requirement_refs: [precode/requirements.csv, REQ-A6, REQ-A7, REQ-AC16, REQ-OQ05]
decision_refs: [OD-20260907-01, OD-20260907-02, OD-20260907-03, PROV-PC03-05]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-03.md, precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-07, vòng bốn (hai mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó đóng nốt hai mục mà OD-20260907-03 để mở: ba mục còn
  lại của cổng chấp nhận probe, và một quyền mạng hẹp một lần để đọc tài liệu chính thức phục vụ
  REQ-A6. Nó KHÔNG giải REQ-A6 — chỉ cho phép đi lấy dữ kiện.
verification: E0 — self-validation (EV-PC00-12) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260907-04` — 2026-09-07 (vòng bốn)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260907-04` |
| Người ban hành | **Owner** — qua phỏng vấn `AskUserQuestion` do Coordinator thực hiện, trên **đúng hai mục** mà `OD-20260907-03` để mở |
| `evidence_ref` | Claude Code session (Coordinator), 2026-09-07 |
| Authority phát sinh | **`AUTH-OWNER-20260907-05`** — parent của packet đi tìm dữ kiện `REQ-A6` **và** của bản ghi cổng probe |
| Biên bản trước | `OD-20260907-01`, `OD-20260907-02`, `OD-20260907-03` |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260907-04.md` do Coordinator phát |

**Quy tắc chuyển ngữ.** File này ghi lại nguyên nội dung biên bản. Cột "Quyết định của Owner" là câu trả lời
**nguyên văn**; cột "Hiệu lực" là hệ quả do **chính biên bản** nêu, không phải suy diễn của PC00. Ở đâu PC00
thêm ghi chú, ghi chú đó nằm ngoài bảng và được đánh dấu rõ (§4, §5).

## 2. Hai quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | `contracts/ops/collector-probe.md` §6 mục **2–4**: ngân sách/điều kiện dừng mỗi đợt (§3/§4 — `PROVISIONAL` 200 post hoặc 30 phút, dừng khi gặp challenge/block/rate-limit/hết phiên, **không bao giờ** bấm xác minh); tiêu chí go/no-go (§7); rủi ro tài khoản thật (`REQ-A7`) | **Chấp nhận cả ba** | §6 mục **1–4 nay đều thỏa** (mục 1 — D09 — đã được phê chuẩn ở `OD-20260907-01`). Việc **chạy live** của probe vẫn bị chặn **vật lý** trên máy của chính Owner (cài Playwright, tự đăng nhập tay vào một Chrome profile riêng của dự án, điền `probe-config.json`, bốn `owner_confirmations` kèm `evidence_ref` trỏ tới quyết định này) — xem `evidence/handoffs/TC-x-feasibility-probe-handoff.md` §"Owner must do". **Không Worker nào được chạy nó.** |
| 2 | `REQ-A6` — nhịp gọi tối đa và yêu cầu định danh của arXiv; hạn mức và yêu cầu định danh/`mailto` của OpenAlex — **bốn** dữ kiện hiện `PLACEHOLDER_KC` trong `contracts/retry-policy.yaml`, cần có trước khi card connector rời `DRAFT` | **Để một Worker đọc tài liệu chính thức** | Quyền mạng **một lần, phạm vi hẹp**: một Worker được tải **chỉ các trang tài liệu** dưới `arxiv.org` / `info.arxiv.org` và `openalex.org` / `docs.openalex.org` để đọc và trích chính sách rate-limit và định danh hiện hành. **Không** được gọi `export.arxiv.org` hay `api.openalex.org` (hay bất kỳ endpoint live nào) — chỉ đọc tài liệu, **không** lưu lượng API thật. Mỗi dữ kiện ghi kèm **URL nguồn, ngày lấy và một trích dẫn nguyên văn ngắn**. |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này: không có — vòng này đóng mọi mục mà `OD-20260907-03` để mở.

## 4. Những gì quyết định này **không** làm

Sáu điều dưới đây do PC00 ghi thêm để không ai đọc rộng hơn văn bản. Chúng đều suy trực tiếp từ §2 của chính
biên bản, không thêm ràng buộc mới.

1. **Không cho phép chạy probe.** Cổng §6 nay mở về mặt **hành chính**; điều kiện **vật lý** thì không. Probe
   vẫn phải chạy trên tài khoản X thật và máy thật của Owner, sau khi Owner tự cài Playwright, tự đăng nhập
   tay, tự điền `probe-config.json` và tự ký bốn `owner_confirmations`. Biên bản nói thẳng: **không Worker nào
   được chạy nó.** Vì vậy `REQ-AC16` và mọi mục `KC` liên quan tới probe **không** đổi trạng thái, và
   `SP1`/M0 vẫn chưa có bằng chứng nào.
2. **Không giải `REQ-A6`.** Đây là điểm dễ đọc nhầm nhất của cả biên bản. Owner cho phép **đi lấy** dữ kiện,
   không cung cấp dữ kiện. `REQ-A6` giữ nguyên `KC` cho tới khi Worker tìm dữ kiện thực sự land **đủ** các
   con số kèm nguồn. Tại **thời điểm biên bản được ban hành**, `research_connector_rate_limit` mang bốn giá
   trị `null` với `status: PLACEHOLDER_KC` và sàn `min_interval_ms = 3000` — xem §7 cho trạng thái đã đổi
   sau đó.
3. **Không mở mạng nói chung.** Quyền là **một lần** và **hẹp theo tên miền**: chỉ `arxiv.org`,
   `info.arxiv.org`, `openalex.org`, `docs.openalex.org`, và chỉ **trang tài liệu**. `export.arxiv.org` và
   `api.openalex.org` bị **cấm tên** trong chính biên bản. Quyền mạng nền vẫn là quyền của `OD-20260907-02`
   mục 4 — cài gói đã khai báo từ PyPI/npm — và không có gì khác.
4. **Không cho phép đoán số.** Ràng buộc "mỗi dữ kiện kèm URL, ngày lấy và trích dẫn nguyên văn" là một
   **yêu cầu về bằng chứng**, không phải một gợi ý định dạng. Một con số không có ba thứ đó thì chưa phải là
   dữ kiện đã lấy.
5. **Không nâng trần claim của file nào.** `contracts/retry-policy.yaml` và card connector giữ nguyên nhãn
   hiện có; `contracts/ops/collector-probe.md` không được nâng vì cổng §6 đã mở.
6. **Không giải `REQ-OQ03` và không đóng finding nào.** `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED` và vẫn chặn
   M3; finding của A1/A2/A3 vẫn theo vòng đời riêng của `protocol.md` §8.

## 5. Ghi chú của PC00 về hai mục có sắc thái

- **Mục 1 — "cổng mở" và "chạy được" là hai chuyện.** Trước vòng này, probe bị chặn bởi **hai** lớp: một lớp
  quyết định (§6 mục 2–4 chưa có câu trả lời) và một lớp vật lý (máy, tài khoản, đăng nhập tay của Owner).
  Vòng này gỡ **lớp thứ nhất**. Lớp thứ hai không phải thứ Owner có thể gỡ bằng một câu trả lời — nó là công
  việc Owner phải **làm**. Một handoff sau này viết "cổng probe đã mở" mà không nói tiếp sẽ bị đọc thành
  "probe đã chạy được"; đó là lý do đoạn này tồn tại. Đồng thời, ba mục vừa được chấp nhận đều là **ngưỡng
  `PROVISIONAL` do PC05 đề xuất** (§3 ngân sách, §7 bảy tiêu chí GO-1..GO-7); "chấp nhận" nghĩa là Owner đồng
  ý dùng chúng làm tiêu chí kết luận, **không** nghĩa là chúng đã được hiệu chỉnh bằng dữ liệu.
- **Mục 2 — một quyền mạng viết bằng danh sách cấm, không chỉ danh sách cho phép.** Biên bản nêu **tên** hai
  endpoint bị cấm (`export.arxiv.org`, `api.openalex.org`) chứ không dừng ở "chỉ trang tài liệu". Đó là khác
  biệt có ý nghĩa: `arxiv.org` và `export.arxiv.org` là hai host của **cùng một tổ chức**, và một grant chỉ
  nói "đọc tài liệu arXiv" sẽ để ngỏ chỗ lách. Worker nhận packet đó phải hiểu ranh giới là **không có lưu
  lượng API thật**, không phải "cố gắng chỉ đọc tài liệu". Packet tìm dữ kiện chạy **song song** dưới
  `AUTH-OWNER-20260907-05`. Kết quả **một phần** của nó đã land trước khi tôi đóng gói xong — xem §7, ghi
  lại như một sự kiện quan sát được, không phải như một phần của biên bản.

## 6. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/owner-decisions.md` | Dòng trỏ tới biên bản vòng bốn này |
| `precode/decision-register.md` §8.13 | Hai hàng quyết định; cổng probe §6 mục 2–4 → đã trả lời; `REQ-A6` → **vẫn mở**, chỉ ghi nhận quyền đi lấy dữ kiện |
| `precode/owner-decision-request.md` | Hai dòng phiếu trả lời vòng bốn được điền; khối "VẪN CHỜ" rút còn `REQ-OQ03` |
| `precode/baseline.json` | Anchor `OD-20260907-04` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260907-05` |
| `contracts/retry-policy.yaml` | **Không sửa ở gói này** — bốn giá trị chỉ được điền bởi Worker tìm dữ kiện, kèm URL/ngày/trích dẫn |
| `contracts/ops/collector-probe.md` | **Không sửa ở gói này** — thuộc PC05; §6 nên ghi rằng bốn mục đã thỏa (`CR-PC00-26`) |
| `precode/requirements.csv` | **Không sửa** — `REQ-A6` vẫn `KC`, `REQ-A7` không đổi |
| `precode/gates.yaml`, `precode/review.md` | **Chưa làm** — thuộc PC09 (`CR-PC00-20`) |

## 7. Trạng thái `REQ-A6` sau biên bản — quan sát của PC00, không phải nội dung biên bản

Mục này **không** thuộc biên bản. Nó ghi lại điều PC00 **đọc được trên đĩa** sau khi biên bản được ban hành,
vì packet đi tìm dữ kiện chạy **song song**. Mỗi phát biểu dưới đây mang mốc thời gian của nó.

### 7.1 Trạng thái hiện hành (cập nhật 2026-09-07T17:00Z) — **`REQ-A6` = `RESOLVED`**

**Cả bốn dữ kiện đã có nguồn.** `PKT-PC03-FIX-REQA6` (worker `worker-WF`, dưới `AUTH-OWNER-20260907-05` do
**`OD-20260907-04` mục 2** — không phải `OD-20260907-03` — sinh ra) chạy **hai** phần và hoàn tất cả hai.
Bản ghi chuẩn: **`precode/decision-register.md` §8.13.2**, cộng `evidence/handoffs/PC03-REQA6-handoff.md`.

| Dữ kiện | Trạng thái | Giá trị |
| --- | --- | --- |
| arXiv — nhịp gọi | `RESOLVED` | `1` request / `3` giây; `1` kết nối đồng thời |
| arXiv — định danh | `RESOLVED_NEGATIVE` | không yêu cầu |
| OpenAlex — nhịp gọi | `RESOLVED` | `openalex_requests_per_window = 100`, `openalex_window_seconds = 1` |
| OpenAlex — định danh | `RESOLVED_NEGATIVE` | không yêu cầu; `api_key` **tùy chọn** (chỉ nâng ngân sách ngày 10×) |

`contracts/retry-policy.yaml` `research_connector_rate_limit` nay mang `status: DOCS_derived` — **không còn**
`PLACEHOLDER_KC`; mỗi giá trị đi kèm URL, ngày đọc và trích dẫn nguyên văn. `precode/requirements.csv` ghi
`REQ-A6` và `REQ-D34` là **`XN`**.

**Điều đã gỡ chốt cho nửa OpenAlex là một quyết định, không phải một lần tìm kỹ hơn.** Owner được trình đúng
một câu hỏi — *"`docs.openalex.org` redirect sang `help.openalex.org`, ngoài quyền được cấp"* — và trả lời:
**thêm `help.openalex.org` vào allowlist**. Quyền mạng thành **năm** host; mọi hạn chế khác giữ nguyên (chỉ
trang tài liệu, chỉ `GET`; `api.openalex.org` và `export.arxiv.org` vẫn **cấm**). Đó chính là `CR-PC00-27`,
nay đã giải.

**Bốn điều `RESOLVED` này KHÔNG kéo theo.**

1. **`XN` nghĩa là nghĩa vụ ĐỌC đã xong, không phải tiền đề của đặc tả đúng.** Câu `D34` của
   `research-radar-spec.md:101` giả định OpenAlex đòi email liên hệ; tài liệu hiện hành nói ngược lại. Đặc
   tả **không** bị sửa (nguồn bất biến) và được đọc theo nghĩa lịch sử — bản ghi chuẩn của việc đó là
   **`AMD-SPEC-D34-01`** ở `precode/decision-register.md` §3.
2. **Ngân sách ngày của OpenAlex cố ý KHÔNG thành một con số** (`RESOLVED_NON_NUMERIC`): tài liệu nêu nó
   bằng **tiền**, nên nguồn sự thật lúc chạy là các header `X-RateLimit-*`. Suy ra một con số từ "1/10" là
   một **phép suy**, không phải một câu trích — và biên bản cấm đoán.
3. **Không nâng trần claim của module nào.** `MOD-research-connector` đạt `CONTRACT_READY` hay không là kết
   luận của PC05/Coordinator trên **toàn bộ** cổng của nó, không phải hệ quả của một khối hợp đồng hết `KC`.
4. **Hiệu lực có điều kiện.** Các giá trị đúng với **tài liệu đọc ngày 2026-09-07**. Nhà cung cấp đổi chính
   sách thì nhãn `DOCS_derived` hết hiệu lực. Một dữ kiện bên ngoài không "đóng" vĩnh viễn theo cách một
   quyết định sản phẩm đóng.

### 7.2 (Lịch sử) Trạng thái lúc 2026-09-07T15:23Z, khi bản ghi này được đóng gói lần đầu

Giữ lại nguyên vẹn để truy vết — **nay đã bị §7.1 và §8.13.2 thay thế**, và không được đọc như trạng thái
hiện hành:

> - **Nửa arXiv đã giải, có trích dẫn.** `worker-WF` đọc `https://info.arxiv.org/help/api/tou.html` và điền
>   `arxiv_requests_per_window = 1`, `arxiv_window_seconds = 3`, cộng `arxiv_max_concurrent_connections = 1`;
>   yêu cầu định danh của arXiv là `RESOLVED_NEGATIVE`.
> - **Nửa OpenAlex CHƯA giải**, và lý do là **ranh giới quyền** — không phải "chưa tìm": mọi đường dẫn dưới
>   `docs.openalex.org` trả `301` sang `help.openalex.org`, ngoài bốn host được cấp; `openalex.org` trả `403`.
>   Worker **dừng lại** thay vì đi theo redirect — hành vi đúng.
> - Vì vậy `REQ-A6` khi đó **vẫn `KC`**, khối vẫn `PLACEHOLDER_KC`, hai giá trị OpenAlex còn `null`.
> - Giải nốt đòi **mở rộng quyền** thêm `help.openalex.org` → `CR-PC00-27`. Không được thay bằng một con số
>   "nhớ được".

**Vì sao đoạn lịch sử này được giữ.** Nó ghi đúng một điều: một Worker gặp một redirect ra ngoài allowlist và
**dừng** thay vì lách. Đó là hành vi mà giao thức đòi, và nó là lý do câu hỏi tới được Owner thay vì bị một
con số phỏng đoán lấp đi. Xoá đoạn này sẽ xoá luôn bằng chứng rằng ranh giới đã được tôn trọng.

**PC00 không sửa `contracts/retry-policy.yaml`** — nó ngoài write set của mọi gói PC00 và do Worker khác giữ.
Mục này chỉ **đọc** nó (`sha256 f9505525…` lúc 2026-09-07T17:00Z; giá trị ở §7.2 đọc bản `d81192d8…` lúc
15:23Z).
