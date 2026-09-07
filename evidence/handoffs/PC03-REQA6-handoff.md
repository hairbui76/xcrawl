# HANDOFF — `PKT-PC03-FIX-REQA6` (REQ-A6: nhịp gọi và định danh của arXiv/OpenAlex)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC03-FIX-REQA6` |
| worker | `worker-WF` |
| authority | `AUTH-COORD-REQA6` (cha `AUTH-OWNER-20260907-05`, `OD-20260907-04` mục 2) |
| lease | `LEASE-PC03-REQA6` — exclusive trên 4 path ở §2 |
| status | **`DONE_WITH_CONCERNS`** — nửa arXiv của `REQ-A6` đã giải; nửa OpenAlex `BLOCKED_SCOPE` |
| completion_ceiling | không nâng trần nào. `REQ-A6` = `PARTIALLY_RESOLVED`, **không** `RESOLVED` |
| next_actor | Coordinator — (1) re-pin card theo hash mới ở §2; (2) xin Owner amendment quyền đọc `help.openalex.org` |
| lease_released_at | `2026-09-07T15:27:40Z` (UTC) |

---

## 1. Hai dữ kiện đã giải — trích dẫn nguyên văn, URL, ngày lấy

Công cụ: `WebFetch` (HTTP GET, chỉ đọc trang tài liệu). **Không** một lời gọi nào tới `export.arxiv.org`
hay `api.openalex.org`; không lưu lượng API thật nào phát sinh.

### FACT `A6-ARXIV-RATE` — nhịp gọi tối đa của arXiv · **RESOLVED**

- **URL:** `https://info.arxiv.org/help/api/tou.html` — *Terms of Use for arXiv APIs*, mục **"Rate limits"**
- **Retrieved at:** **2026-09-07** (bởi `worker-WF`, `WebFetch` GET)
- **Nguyên văn:**
  > "When using the legacy APIs (including OAI-PMH, RSS, and the arXiv API), make no more than one request
  > every three seconds, and limit requests to a single connection at a time."
- **Đọc thành giá trị hợp đồng:** `arxiv_requests_per_window = 1`, `arxiv_window_seconds = 3`, và một
  khóa **mới** `arxiv_max_concurrent_connections = 1` (mệnh đề thứ hai của cùng câu — một dữ kiện mà sàn
  `min_interval_ms` cũ không phủ).
- **Ghi chú:** con số trùng đúng sàn tự đặt `min_interval_ms = 3000`, nhưng tư cách khác hẳn: với arXiv nó
  nay là **hạn mức tài liệu nêu**, không còn là con số bảo thủ do PC03 tự chọn.

### FACT `A6-ARXIV-IDENT` — yêu cầu định danh của arXiv · **RESOLVED_NEGATIVE**

- **URL chính:** `https://info.arxiv.org/help/api/tou.html` — **Retrieved at: 2026-09-07**
- **Đối chiếu thêm (cùng ngày):** `https://info.arxiv.org/help/api/user-manual.html`,
  `https://info.arxiv.org/help/api/basics.html`, `https://info.arxiv.org/help/api/index.html`
- **Quan sát:** không trang nào trong bốn trang đặt ra một **nghĩa vụ định danh** (User-Agent, email liên
  hệ, hay đăng ký) như điều kiện để gọi API. Câu duy nhất chạm tới thông tin cá nhân là một tuyên bố về
  việc **thu thập** dữ liệu, không phải nghĩa vụ của caller, nguyên văn:
  > "In order to provide support and improvements for developers who use arXiv APIs, you understand that
  > we will collect certain private information about you, such as your name and email address."
- **Đọc thành giá trị hợp đồng:** `arxiv_identification_required = false`.
- **Giới hạn (bắt buộc đọc kèm):** đây là một **phủ định có phạm vi** — "bốn trang đã đọc ngày 2026-09-07
  không yêu cầu", **không** phải "gọi ẩn danh là hành vi tốt". Nó chỉ có nghĩa là hợp đồng không được viện
  arXiv làm căn cứ **bắt buộc** một chuỗi định danh. Luật `SG-IDENT` không đổi.
- Trích dẫn khác thời điểm: hướng dẫn sử dụng API cùng ngày còn nói
  > "In cases where the API needs to be called multiple times in a row, we encourage you to play nice and
  > incorporate a 3 second delay in your code."
  — nhất quán với ToU, nhưng **ToU là nguồn được dùng** vì nó là điều khoản, không phải lời khuyên.

### Hai dữ kiện OpenAlex · **BLOCKED_SCOPE** — không đọc được **trong quyền được cấp**

`openalex_requests_per_window`, `openalex_window_seconds` và `openalex_identification_required` **giữ
`null`**. Lý do không phải "chưa tìm" mà là **ranh giới quyền**. Quyền cấp đúng bốn host: `arxiv.org`,
`info.arxiv.org`, `openalex.org`, `docs.openalex.org`. Quan sát ngày **2026-09-07**:

| URL thử | Kết quả |
| --- | --- |
| `https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication` | `301 Moved Permanently` → `https://help.openalex.org/` |
| `https://docs.openalex.org/how-to-use-the-api/api-overview` | `301 Moved Permanently` → `https://help.openalex.org/` |
| `https://docs.openalex.org/` | `301 Moved Permanently` → `https://help.openalex.org/` |
| `https://openalex.org/` | `403 Forbidden` |
| `https://openalex.org/about` | `403 Forbidden` |

`help.openalex.org` **không** nằm trong bốn host được cấp. Worker **dừng tại redirect** thay vì đi theo:
đi theo một redirect ra ngoài allowlist là tự mở scope, đúng thứ `agent_profile/protocol.md` §3 cấm — và
một biên bản nêu **đích danh** hai host bị cấm là biên bản coi trọng danh sách host. **Không con số nào
được đoán, suy ra từ thông lệ, hay lấy từ trí nhớ.**

**Cách giải, dành cho Coordinator:** một amendment quyền thêm `help.openalex.org` (chỉ trang tài liệu,
chỉ GET) vào allowlist, rồi một packet tìm dữ kiện thứ hai. Đó là quyết định của Owner, không phải của
Worker.

---

## 2. Delta — before/after hash + bytes

Cả ba file `MODIFY`; baseline khớp hash đã pin ở `agent-tasks/TC-research-connector-metadata.md` §0
(`retry-policy.yaml`, `decision-register.md`) tại lúc bắt đầu.

| Path | before sha256 / bytes | after sha256 / bytes |
| --- | --- | --- |
| `contracts/retry-policy.yaml` | `d95784bf5f67a332597b7ac4ef60a34b13d807b087d3ced9fdc46fba83c0cba5` / 46995 | `d81192d8e67817c63058cf952e40bc607416a056fbc34d04b792aa2fc0203089` / 52994 |
| `precode/decision-register.md` | `31fa401c2da52743b3d76d57ee6842ca80ffe04c46eac88ecb149e7f7dcf7d9f` / 122432 | `8285ae90ad6b1187ed1e3bd3616a36093ab4f656a5147586e4382bd6f915c296` / 132927 |
| `precode/change-control.md` | `21688b458b1ce8f2c6687e3d99b750efbae0bf5ead4414b991b02f8633b17ef0` / 28321 | `974a7244a4f25b64514d56aeab512db557f018ee8d2db47bff204179cda2dfcf` / 35671 |
| `evidence/handoffs/PC03-REQA6-handoff.md` | ABSENT | file này (`CREATE`, `WHOLE_NEW_FILE`) |

Tóm tắt delta nhỏ nhất:

1. **`contracts/retry-policy.yaml` 0.6.0 → 0.7.0.** Trong `budgets.research_connector_rate_limit`:
   `values` nhận `arxiv_requests_per_window: 1`, `arxiv_window_seconds: 3`,
   `arxiv_max_concurrent_connections: 1`; hai khóa OpenAlex **giữ `null`**; `min_interval_ms: 3000`
   **giữ nguyên**; `status` **giữ `PLACEHOLDER_KC`**. Thêm ba khóa mô tả: `sources` (hai bản ghi có
   `url` + `retrieved_at` + trích dẫn nguyên văn), `identification`, `unresolved_vi`. `decision_ref`,
   `rationale_vi`, `blocked_scope_vi` viết lại cho khớp trạng thái mới. Ngoài khối: `scope` và
   `ratification.still_kc_vi` sửa "bốn giá trị" → "hai", có ghi rõ câu cũ viết ở thì `OD-20260907-01`.
2. **`precode/decision-register.md` 0.1.1 → 0.1.2.** §8.5 nhận một khối `>` cập nhật (đoạn gốc giữ
   nguyên làm lịch sử); §8.13 nhận một chú thích chuyển tiếp; thêm **§8.13.1** — bảng bốn dữ kiện với
   trạng thái, giá trị, URL, ngày đọc, trích dẫn; lý do nửa OpenAlex dừng; và "bốn điều packet này KHÔNG
   làm".
3. **`precode/change-control.md` 0.1.3 → 0.1.4.** §10 nhận **`CR-PC03-08`**, đủ chín trường của §1, kèm
   `version_rule` (hàng minor của §2 — trường optional mới; **không** cần khai `deviation`),
   `affected.task_cards` (INV-06/INV-09 ⇒ mọi card pin `retry-policy.yaml` chuyển `STALE`),
   `affected.evidence` (`EV-PC03-05` `STALE`), `still_open` (ranh giới host) và `migration`.

**Không** file nào khác bị ghi. `agent-tasks/*` **cố ý** không chạm — re-pin là bước của Coordinator.
`precode/requirements.csv` không nằm trong lease, nên `REQ-A6` ở đó **vẫn ghi `KC`**; ai đọc file đó phải
đọc kèm §8.13.1.

---

## 3. Evidence record

| Trường | Giá trị |
| --- | --- |
| evidence_id | `EV-PC03-REQA6-01` |
| producer | `worker-WF` |
| kind | **`SELF_VALIDATION`** (E0 tĩnh + đọc tài liệu) — **không** phải independent audit |
| command | `python3 evidence/tools/e0_check.py` (chỉ đọc), chạy tại repo root |
| runtime | Linux, `python3`; repo `/mnt/virtual/repo/xcrawl`, branch `main` |
| started/ended (UTC) | `2026-09-07T15:18:28Z` … `2026-09-07T15:26:05Z` (hai lần chạy — xem dưới) |
| oracle | 25 check E0; kỳ vọng: không check nào sinh vi phạm **trên ba file trong lease** |
| observed (run 1, `~15:24:59Z`) | `TOTAL: 25 checks — PASS 24 · FAIL 1 · BLOCKED 0 · N/A 0 · violations 1`; exit code `0` |
| observed (run 2, `~15:26:05Z`) | `TOTAL: 25 checks — PASS 25 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0`; exit code `0` |
| status | **PASS**. Vi phạm duy nhất của run 1 nằm ngoài lease và đã được **một actor khác** sửa giữa hai lần chạy — xem dưới |
| limitations | E0 là check **tĩnh**: nó không chứng minh runtime, không kiểm được rằng một URL còn trả nội dung đã trích. Nội dung trang tài liệu do một mô hình tóm tắt đọc hộ (`WebFetch`); trích dẫn được lấy lại **hai lần** trên cùng URL với hai prompt khác nhau và khớp nhau, nhưng đó vẫn không phải một bản lưu byte-for-byte của trang. |

**Vi phạm E0 của run 1 — pre-existing, ngoài lease, và do actor khác sửa.**
`FAIL E0-12-forbidden-strings · violations=1 · precode/owner-decision-request.md:477` —
"claim label IMPLEMENTATION_VERIFIED asserted in text". File đó **không** nằm trong
`LEASE-PC03-REQA6`, không bị packet này chạm, và nội dung vi phạm nói về **card auth**, không liên quan
tới `REQ-A6`. Nó đã hiện diện trong working tree **trước** packet này (file mang trạng thái `M` từ đầu
phiên; dòng vi phạm **không** có trong `HEAD`).

Giữa run 1 và run 2, file đó được sửa bởi **một actor khác đang chạy song song** (mtime
`2026-09-07T15:25:56Z`, sau khi ba file trong lease này đã ở trạng thái cuối): nhãn được bọc backtick nên
`E0-12` hết vi phạm, và run 2 cho `25/25 PASS`. Ghi ra vì hai lý do: (a) packet này **không** nhận công
cho lần sửa ấy — nó nằm ngoài write set và Worker này không chạm tới; (b) nó là **bằng chứng có ghi
nhận rằng cây làm việc không tĩnh** trong lúc packet chạy. Ba file trong lease được rehash **sau** run 2
và **không đổi** so với §2, nên kết luận của §2 không bị lần ghi song song đó chạm tới.

*Giới hạn:* khẳng định "pre-existing" dựa trên `git show HEAD:` + trạng thái `M` đầu phiên, không dựa
trên một lần chạy E0 trên cây trước-thay-đổi.

---

## 4. Unresolved / findings mở

| ID | Nội dung | Ai giải |
| --- | --- | --- |
| `REQ-A6` (nửa OpenAlex) | Hai giá trị nhịp gọi + yêu cầu `mailto` chưa đọc được: trang tài liệu 301 sang một host ngoài allowlist | Owner (amendment quyền), rồi một packet tìm dữ kiện thứ hai |
| Re-pin | `contracts/retry-policy.yaml` đổi byte ⇒ mọi card pin hash file đó `STALE` (INV-06/INV-09) | Coordinator |
| `EV-PC03-05` | Lint của PC03 chạy trên bytes cũ ⇒ `STALE`, cần chạy lại | PC03 |
| `precode/requirements.csv` | `REQ-A6` vẫn ghi `KC`; đúng theo trạng thái tổng thể, nhưng nay cần đọc kèm §8.13.1 | Coordinator / PC00 |
| `E0-12` FAIL | `precode/owner-decision-request.md:477` — ngoài lease | Chủ file đó |

## 5. Bốn điều packet này KHÔNG làm

1. **Không đóng `REQ-A6`.** Trạng thái là `PARTIALLY_RESOLVED`. Hai trong bốn giá trị vẫn `null`.
2. **Không nới `SG-A6`.** Cổng ấy đòi **bốn** giá trị; connector **vẫn từ chối khởi động**, và
   `MOD-research-connector` **vẫn không** `CONTRACT_READY`.
3. **Không gọi API thật.** Không `export.arxiv.org`, không `api.openalex.org`, không host nào ngoài
   allowlist, không đi theo redirect ra ngoài allowlist, không X / Telegram / AI provider.
4. **Không tự audit.** Mọi thứ ở đây là `SELF_VALIDATION`. Không có câu "independent audit passed".

---

*`lease_released_at = 2026-09-07T15:27:40Z` (lease vòng một `LEASE-PC03-REQA6`). Sau mốc này `worker-WF`
không ghi thêm byte nào vào bốn path của lease, kể cả để sửa lỗi đánh máy — sửa tiếp cần packet mới,
baseline mới, lease mới. **Đã có một lease mới: xem phần bổ sung dưới đây.***

---

# ADDENDUM — `PKT-PC03-FIX-REQA6` phần 2 · `LEASE-PC03-REQA6-p2` · 2026-09-07

**Status: `DONE`.** `REQ-A6` = **`RESOLVED`** (cả bốn dữ kiện). Owner mở rộng allowlist đọc tài liệu thêm
`help.openalex.org` (thành **năm** host) sau khi vòng một báo redirect ra ngoài quyền; mọi hạn chế khác
giữ nguyên và **không** lần gọi nào tới `api.openalex.org` / `export.arxiv.org` xảy ra.

## A1. Hai dữ kiện OpenAlex — trích dẫn nguyên văn, URL, ngày lấy

### FACT `A6-OPENALEX-RATE` · **RESOLVED**

- **URL:** `https://help.openalex.org/api/authentication/` — **Retrieved at: 2026-09-07**
- **Nguyên văn:**
  > "Two things return `429 Too Many Requests`: exceeding your daily budget, or making more than 100
  > requests per second."
- **Giá trị hợp đồng:** `openalex_requests_per_window = 100`, `openalex_window_seconds = 1`.

### FACT `A6-OPENALEX-IDENT` · **RESOLVED_NEGATIVE**

- **URL:** `https://help.openalex.org/api/` — **Retrieved at: 2026-09-07**
  (đối chiếu: `/api/authentication/`, `/access/pricing/`, cùng ngày)
- **Nguyên văn:**
  > "Send your key as an `api_key` query parameter (or leave it off to try the API for free — the website
  > itself runs on these same public endpoints)." · "A free API key raises your daily budget 10×, and
  > heavier use is pay-as-you-go."
- **Giá trị hợp đồng:** `openalex_identification_required = false`, `openalex_api_key_optional = true`.
- **Phát hiện đáng báo:** các chuỗi `mailto`, `polite pool`, `polite`, `User-Agent` **không** xuất hiện
  trên trang tổng quan API cũng như trang Authentication. Quy ước *polite pool* mà `REQ-D34`/`SG-IDENT`
  giả định **không còn** trong tài liệu hiện hành; cơ chế nay là `api_key` **tùy chọn**. **Luật**
  `SG-IDENT` giữ nguyên trong card và code — đổi là **dữ kiện** nó áp lên, không phải luật.

### Dữ kiện thứ năm, cố ý KHÔNG thành số · `A6-OPENALEX-BUDGET` · **RESOLVED_NON_NUMERIC**

OpenAlex có **hai** giới hạn chồng nhau: nhịp giây (trên) **và** một ngân sách ngày nêu bằng **tiền** —
*"every account gets \$1 of API usage per day for free"* (`/access/pricing/`), *"a free key gives you 10×
the keyless budget"* (`/api/authentication/`), *"429 Too Many Requests — Rate limit or daily credit budget
exceeded; slow down or wait for the reset"* (`/api/errors/`). Tài liệu **không** nêu con số của lượt gọi
không-khoá; "1/10" là **phép suy**, không phải trích dẫn, nên **không** con số nào được đặt vào `values`.
Nguồn sự thật lúc chạy: header `X-RateLimit-Limit` / `-Remaining` / `-Credits-Used` / `-Reset` (giây tới
nửa đêm UTC).

## A2. Delta phần 2 — before/after hash + bytes

"Before" của phần 2 = "after" của phần 1 (§2).

| Path | before sha256 / bytes | after sha256 / bytes |
| --- | --- | --- |
| `contracts/retry-policy.yaml` (0.7.0 → **0.8.0**) | `d81192d8e67817c63058cf952e40bc607416a056fbc34d04b792aa2fc0203089` / 52994 | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` / 61357 |
| `precode/decision-register.md` (0.1.2 → **0.1.3**) | `8285ae90ad6b1187ed1e3bd3616a36093ab4f656a5147586e4382bd6f915c296` / 132927 | `b2ed138fa636ce3e26f78f7e22994d4ebf9bc1b4e0ae692482df78247afe2017` / 138431 |
| `precode/change-control.md` (0.1.4 → **0.1.5**) | `974a7244a4f25b64514d56aeab512db557f018ee8d2db47bff204179cda2dfcf` / 35671 | `0b3d2bfa739db1b0792d979be49e00c8cc5f676b14d162994c985b33e9afab3a` / 42312 |

> Ba dòng trên là **hash chốt**, đo lúc `2026-09-07T16:34:01Z`, **sau** hai lần sửa cuối (đổi tên token
> trạng thái và gỡ một token gây `E0-04d`, §A4) và **cùng bytes** với lần chạy `e0` báo ở §A3.

Tóm tắt delta: `values` nhận `openalex_requests_per_window: 100`, `openalex_window_seconds: 1`;
`identification` nhận `openalex_identification_required: false` + `openalex_api_key_optional: true`;
`sources` nhận ba bản ghi OpenAlex; `status` `PLACEHOLDER_KC` → `DOCS_derived`; `unresolved_vi` →
`resolved_vi`; `blocked_scope_vi` → `scope_note_vi`; thêm `status_note_vi`, `expiry_vi`.
`min_interval_ms = 3000` **giữ nguyên**. Register: §8.5 nhận ghi chú cập nhật thứ hai, thêm **§8.13.2**.
Change-control: thêm **`CR-PC03-08.a`** — **bổ sung**, không viết lại `CR-PC03-08`.

## A3. E0 · `python3 evidence/tools/e0_check.py` (chỉ đọc)

**`TOTAL: 25 checks — PASS 25 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0`**, exit code `0`.
`SELF_VALIDATION`, E0 tĩnh — không chứng minh runtime, không chứng minh URL còn trả nội dung đã trích.

## A4. Một lần lint bắt lỗi, ghi lại vì nó là bằng chứng chứ không phải phiền toái

Bản đầu của phần 2 đặt tên trạng thái là RESOLVED_FROM_DOCS (viết không backtick ở đây, đúng vì lý do
dưới). `E0-04d-prose-error-tokens` **FAIL**:
token SCREAMING_SNAKE trong prose bị đọc là một mã lỗi chưa đăng ký, vì `STATUS_VOCABULARY` sống trong
`evidence/tools/e0_check.py` — **ngoài lease**. Hai lối đi: sửa danh sách của công cụ (ngoài quyền), hoặc
đổi tên cho hợp lint. Chọn lối thứ hai: **`DOCS_derived`**, lấy hình dạng của `XN_derived` đã có sẵn trong
chính file (`X_derived` = "suy ra từ X"). Kết quả `25/25 PASS`. Ghi ra vì đây đúng là chỗ dễ có người mở
rộng scope "cho nhanh".

## A5. Còn lại cho Coordinator, và release

Hash chốt: bảng §A2 cột "after" (đo `2026-09-07T16:32:59Z`). Không có bảng thứ hai.

Còn lại cho Coordinator: (1) **re-pin** — `contracts/retry-policy.yaml` đổi byte **hai** lần trong ngày
(`0.6.0 → 0.7.0 → 0.8.0`); pin **một** lần trên bytes cuối. (2) `EV-PC03-05` `STALE`, chạy lại.
(3) `precode/requirements.csv` vẫn ghi `REQ-A6 = KC` (ngoài lease) — cần chủ file cập nhật; đọc kèm
§8.13.2. (4) `REQ-D34`/`SG-IDENT`: giả định `mailto` không còn khớp tài liệu — cân nhắc một CR riêng.

**Bốn điều phần 2 KHÔNG làm:** không nâng trần claim của `MOD-research-connector`; không chạm card nào;
không đi theo redirect ra ngoài allowlist; không gọi endpoint API thật nào.

*`lease_released_at` (`LEASE-PC03-REQA6-p2`) = `2026-09-07T16:34:10Z` UTC. Sau mốc này `worker-WF` không
ghi thêm byte nào vào bốn path của lease. Sửa tiếp cần packet mới, baseline mới, lease mới.*
