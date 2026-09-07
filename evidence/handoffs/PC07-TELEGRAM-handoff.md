# HANDOFF — `PKT-PC07-FIX-TELEGRAM` (`CR-PC07-04`: năm giới hạn định dạng Telegram Bot API)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC07-FIX-TELEGRAM` |
| worker | `worker-WT` |
| authority | `AUTH-COORD-TELEGRAM-FACTS` (cha `AUTH-OWNER-20260908-06`, `OD-20260908-05` mục 2) |
| lease | `LEASE-PC07-TELEGRAM` — exclusive trên 6 path ở §2 |
| status | **`DONE_WITH_CONCERNS`** — 2/5 dữ kiện đã giải; 3/5 `BLOCKED_DEPENDENCY` (thiếu tool capability) |
| completion_ceiling | không nâng trần nào. `CR-PC07-04` = `PARTIALLY_RESOLVED`, **không** `CLOSED`. `contracts/telegram/delivery.md` giữ `claim_ceiling: DRAFT_FOR_REVIEW`; `MOD-telegram-adapter` vẫn **BLOCKED (cứng)** |
| next_actor | Coordinator — (1) bump `version` + sửa `verification:` ở front matter `delivery.md` (ngoài lease); (2) sửa câu chữ "năm giới hạn `KC`" ở 8 card + 6 file khác; (3) trình Owner việc cấp một **cách đọc** lấy được cả trang `/bots/api`; (4) re-pin mọi card pin hash `delivery.md` |
| lease_released_at | `2026-09-07T18:18:00Z` (UTC) = `2026-09-08T01:18` giờ Owner (`Asia/Ho_Chi_Minh`) |

**Ghi chú đồng hồ, đọc trước khi đối chiếu mọi mốc thời gian bên dưới.** Packet nói ngày **2026-09-08**;
đồng hồ máy chạy **UTC** và trong suốt phiên này nó ở ngày **2026-09-07** (18:0xZ). Không có mâu thuẫn:
`Asia/Ho_Chi_Minh` = UTC+7, nên `2026-09-07T18:05Z` **là** `2026-09-08T01:05` theo giờ Owner. Mọi mốc UTC ở
đây ghi kèm `Z`; mọi lần viết "ngày lấy 2026-09-08" là ngày **theo giờ Owner**. Ghi cả hai thay vì chọn một,
vì một dữ kiện có ngày đọc mà ngày ấy mập mờ thì lần sau không kiểm lại được.

---

## 1. Năm dữ kiện — trạng thái, trích dẫn nguyên văn, URL, ngày lấy

Công cụ đọc: `WebFetch` (GET, chỉ đọc), host duy nhất `core.telegram.org`. **Không** một lời gọi nào tới
`api.telegram.org`, **không** bot token, **không** gì được gửi đi.

### FACT `TG-MSG-LEN` — độ dài tối đa một tin · **RESOLVED (nguồn thứ cấp)**

- Giá trị: **4096 ký tự** cho `sendMessage.text`.
- Nguồn: <https://core.telegram.org/bots/tutorial> §"Sending Messages", đọc `2026-09-07T18:03Z`
  (= 2026-09-08 giờ Owner).
- Nguyên văn: *"A `String` object containing the message text, 1-4096 characters."*
- **Ba giới hạn của câu trích này, phải đọc kèm.** (a) Nó **không** phải hàng `text` của
  `/bots/api#sendmessage` — trang chuẩn ấy không đọc được (§2 lý do), nên đây là **nguồn thứ cấp** của cùng
  nhà cung cấp, không phải trang tham chiếu chuẩn. (b) Vì vậy **ngữ nghĩa đếm** ("after entities parsing"
  hay không) chưa có câu trích. (c) **Đơn vị đếm** (ký tự Unicode hay đơn vị mã UTF-16) cũng chưa có câu
  trích; emoji và ký tự ngoài BMP có thể đếm đôi.
- Luật đã khóa ở `contracts/telegram/delivery.md` §3.4 để (b) không thành một giả định: đếm trên **chuỗi thô
  đã escape**. Escape chỉ **thêm** ký tự, nên "thô ≤ 4096" kéo theo "sau parse ≤ 4096" dưới **cả hai** cách
  đọc. Đây là suy luận về **quan hệ giữa hai phép đếm**, không phải suy ra con số — ranh giới ấy là chỗ
  "đọc tài liệu" khác "điền cho đủ ô".

### FACT `TG-RATE` — rate limit gửi · **RESOLVED**

- Giá trị: **1 tin/giây trong một chat**; **20 tin/phút trong một group**; **~30 tin/giây khi broadcast**.
- Nguồn: <https://core.telegram.org/bots/faq> §"My bot is hitting limits, how do I avoid this?", đọc
  `2026-09-07T17:56Z` (= 2026-09-08 giờ Owner).
- Nguyên văn (ba câu, theo đúng thứ tự trên trang):
  > *"In a single chat, avoid sending more than one message per second. We may allow short bursts that go
  > over this limit, but eventually you'll begin receiving 429 errors."*
  > *"In a group, bots are not be able to send more than 20 messages per minute."*
  > *"For bulk notifications, bots are not able to broadcast more than about 30 messages per second, unless
  > they enable paid broadcasts to increase the limit."*
- **Đây là trần LẬP KẾ HOẠCH, không phải ngân sách retry.** Chính nguồn viết có biên — *"avoid"*,
  *"about"*, *"may allow short bursts"* — và *"unless they enable paid broadcasts"* nói 30/giây là trần
  **mặc định**. `Retry-After` của Telegram trên một `429` thật **thắng** mọi số trên.
  `contracts/retry-policy.yaml` **không** bị đụng và **không** nhận số mới nào (ngoài lease).
- Dòng áp thẳng vào thiết kế là dòng **thứ nhất**: hệ này gửi cho **một** chat, và §3.5 gửi một digest nhiều
  part bằng nhiều lời gọi `sendMessage` liên tiếp ⇒ dispatcher phải chừa nhịp **1 tin/giây cho mỗi chat**.
  Hai dòng còn lại (group, broadcast) hiện **không** áp cho MVP một người dùng, nhưng ghi lại để lần sau
  không ai phải đọc lại trang.

### Ba dữ kiện còn lại · **`BLOCKED_DEPENDENCY`** — thiếu *tool capability*, không thiếu nguồn

| Dữ kiện | Trạng thái | Ghi chú |
| --- | --- | --- |
| Độ dài `callback_data` | `KC` | PROVISIONAL **64 byte** GIỮ NGUYÊN và **chưa kiểm**. `1:<ri>:<ii>:<lg>:<rv>` vẫn đứng trên một giả định |
| Parse mode + bảng escape | `KC` | Chưa chọn được chế độ ⇒ §3.3 chỉ còn nhánh an toàn "gửi plain text" là dùng được |
| Số nút mỗi hàng / mỗi bàn phím | `KC` | Bố cục bàn phím của §3.1 mục 3 chưa khóa được |

**Vì sao dừng, và vì sao đó KHÔNG phải "chưa tìm kỹ" — cũng KHÔNG phải `BLOCKED_SCOPE`.** Cả ba nằm trên
đúng một trang, <https://core.telegram.org/bots/api> (hàng `callback_data` của `InlineKeyboardButton`;
§Formatting options → MarkdownV2 style; `InlineKeyboardMarkup`), và trang ấy nằm **đúng trong** host được
cấp. Cái chặn là **độ dài**: `WebFetch` chuyển trang sang markdown rồi cắt, và điểm cắt rơi giữa
`MessageAutoDeleteTimerChanged` — **trước** cả mục `Available methods`. Một lần đọc thăm dò xác nhận đúng
điểm cắt ấy (câu hỏi: "phần cuối cùng bạn thực sự nhìn thấy là gì"), nên đây là quan sát, không phải suy
đoán. Fragment `#sendmessage` và `#inlinekeyboardbutton` **không** đổi phần bị cắt.

Khác `REQ-A6` (`precode/decision-register.md` §8.13.1): ở đó trang redirect ra một host **ngoài** allowlist
nên cái chặn là ranh giới **quyền** (`BLOCKED_SCOPE`) và cách giải là Owner mở host. Ở đây quyền đã đủ; cái
thiếu là một **khả năng đọc**. Phân biệt hai loại chặn không phải chuyện chữ nghĩa — chúng gọi **hai actor
khác nhau** ra làm **hai việc khác nhau**.

**Mười hai trang cùng host đã thử, không trang nào chứa ba dữ kiện ấy:**

| URL | Kết quả |
| --- | --- |
| `/bots/api` (và `#sendmessage`, `#inlinekeyboardbutton`) | Nội dung bị cắt trước `Available methods` |
| `/bots/faq` | Có `TG-RATE`; **không** có ba dữ kiện |
| `/bots/tutorial` | Có `TG-MSG-LEN`; callback data / bố cục nút / escaping: ABSENT |
| `/bots/features` | Chỉ trỏ ngược về `/bots/api#markdownv2-style`; không có bảng escape |
| `/bots/webhooks` | ABSENT cả bốn chủ đề |
| `/bots/inline` | ABSENT |
| `/bots/games` | ABSENT |
| `/bots/2-0-intro` | Mô tả inline keyboard nhưng **không** nêu giới hạn nào |
| `/bots/api-changelog` | Có nhắc `MarkdownV2`; **không** có danh sách ký tự phải escape |
| `/api/bots/buttons` | ABSENT |
| `/api/entities` | Có ví dụ Markdown/HTML; **không** có luật escape |
| `/constructor/keyboardButtonCallback` | `data` chỉ ghi *"Callback data"*, không nêu giới hạn byte |
| `/constructor/replyInlineMarkup` | `rows` chỉ ghi *"Bot or inline keyboard rows"*, không nêu số tối đa |

Một trang nữa, `/api/config`, có trả `message_length_max` nhưng đó là **client config của MTProto**, không
phải Bot API, và câu mô tả kèm theo nói về caption của tài khoản Premium — **cố ý không dùng** làm nguồn:
một con số đúng lấy từ sai chỗ vẫn là một trích dẫn sai.

**Cách giải đúng:** một khả năng đọc **lấy được cả trang** `core.telegram.org/bots/api` (fetch theo đoạn/
offset, hoặc tải trang rồi grep cục bộ) dưới **cùng** ranh giới host và cùng các điều cấm. Đó là amendment
về **công cụ**, không phải về host — và tuyệt đối không phải một con số nhớ được.

---

## 2. Delta — before/after hash + bytes

Baseline lấy `2026-09-07T17:50Z`, kiểm lại ngay trước lần ghi cuối. Không path nào ngoài sáu path này bị
chạm. `evidence/tools/e0_check.py` chạy **chỉ đọc**, `--json-out` trỏ ra scratch ngoài repo, và
`PYTHONDONTWRITEBYTECODE=1` để không sinh `__pycache__` trong repo.

| Path | Op | before sha256 / bytes | after sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/telegram/delivery.md` | MODIFY (§3.4) | `cb3a4b30a26f2a5ca5cf9d11359b84ce5612c003dfe51c3acbdbba5d7fde226c` / 16807 | `917031ea03b5416c63ee5bcb266bb64de26ad57587f8828abfa5faa7ed5da6fe` / 22221 |
| `precode/decision-register.md` | MODIFY (thêm §8.14) | `058621d0649b798cb8882f718c450d548df1f4672bdee512e330bee77d46e8b0` / 144860 | `d98f017485f15ad558b644131e4e5acae33162f856ca7dce6eefee85417abbf5` / 152722 |
| `precode/change-control.md` | MODIFY (thêm §10 `CR-PC07-04`) | `0b3d2bfa739db1b0792d979be49e00c8cc5f676b14d162994c985b33e9afab3a` / 42312 | `b22a92831d6bbacffb3a86cb3797f13e62f8055feaf59fb890d3a1e13e2fbed0` / 51183 |
| `precode/requirements.csv` | MODIFY (2 hàng: `REQ-AC14`, `REQ-S5.3-02`) | `d3e150e364a51e6f4962e9cba1e13ed06e59282377ae5d2684746f91f5da6bd6` / 73921 | `36138c9f67dcf93c73c8e7b06ecc753cf76f585e41ab32b1ed0a7a7c9468869f` / 76415 |
| `acceptance/traceability.csv` | MODIFY (2 hàng: `REQ-AC14`, `REQ-S5.3-02`) | `d752061da3f454fe2c68062bfb03ace7d43e0957f5d0063055779318845c1bbe` / 94909 | `ff7bb430b592dc4782a3a56b9bd4f0017af6188908b99f15dfbd644ca75f7caf` / 96122 |
| `evidence/handoffs/PC07-TELEGRAM-handoff.md` | CREATE | ABSENT | file này (`WHOLE_NEW_FILE`) |

**Delta nhỏ nhất, theo từng file.**

1. `delivery.md`: **chỉ** khối §3.4 (từ tiêu đề `### 3.4` tới hết đoạn cuối của mục ấy). Front matter, §3.3,
   §3.5, §4, §8 và §9 **không** đổi một byte. Tiêu đề đổi từ "Giới hạn định dạng — `KC`" sang "Giới hạn định
   dạng — hai dòng ĐÃ ĐỌC, ba dòng còn `KC`"; bảng nhận hai cột (Giá trị, Nguồn); hai hàng rời `KC` sang
   `DOCS_derived`; thêm bốn khối văn xuôi (ba câu rate limit nguyên văn; "Ba điều con số 4096 KHÔNG nói";
   "Ba dòng còn `KC`" kèm 12 URL; hệ quả + điều cấm giữ nguyên cho ba dòng).
2. `decision-register.md`: **thêm** §8.14 và §8.14.1 ở cuối; không sửa một dòng cũ nào.
3. `change-control.md`: **thêm** một mục `CR-PC07-04` vào cuối §10 theo đúng khuôn `CR-PC03-08`; không viết
   lại mục cũ nào.
4. + 5. Hai CSV: **chỉ** cột `notes` của hai hàng mỗi file, nối thêm; không đổi `status`/`req_status`,
   không đổi `coverage_status`, không thêm/bớt hàng. Kiểm lại bằng `csv` của Python: 247 hàng, đúng 10/11
   cột, 0 hàng lệch.

---

## 3. Evidence record

| Trường | Giá trị |
| --- | --- |
| evidence_id | `EV-PC07-TELEGRAM-01` |
| producer | `worker-WT` |
| kind | **`SELF_VALIDATION`** (E0 tĩnh + đọc tài liệu) — **không** phải `INDEPENDENT_AUDIT` |
| command | `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py --repo /mnt/virtual/repo/xcrawl --json-out <scratch>.json` (chỉ đọc), chạy từ scratch ngoài repo |
| runtime | Linux, `python3`; repo `/mnt/virtual/repo/xcrawl`, branch `main`; TZ máy = UTC, TZ Owner = `Asia/Ho_Chi_Minh` |
| started/ended (UTC) | `2026-09-07T18:07:47Z` … `2026-09-07T18:13:42Z` (ba lần chạy — xem dưới) |
| oracle | 25 check E0; kỳ vọng: không check nào sinh vi phạm trên sáu file trong lease |
| observed (run 0, baseline `18:07:52Z`) | `TOTAL: 25 checks — PASS 25 · FAIL 0 · violations 0`; exit `0` |
| observed (run 1, sau sửa `18:12:55Z`) | `TOTAL: 25 checks — PASS 24 · FAIL 1 · violations 1`; exit `0` |
| observed (run 2, sau sửa lần hai `18:13:42Z`) | `TOTAL: 25 checks — PASS 25 · FAIL 0 · violations 0`; exit `0` |
| status | **PASS** — trên bytes cuối cùng |
| limitations | (1) E0 là check **tĩnh**: nó không chứng minh runtime, không kiểm được một URL còn trả nội dung đã trích. (2) Nội dung trang tài liệu do một mô hình đọc hộ trong `WebFetch`; **không** có bản lưu byte-for-byte của trang nào, nên "nguyên văn" ở đây là nguyên văn **như công cụ trả về**. Đây là giới hạn thật, không phải câu rào đón: nếu một câu trích sai một chữ, E0 không bắt được. (3) Ba dữ kiện `KC` **không** được kiểm bởi bất cứ thứ gì ở đây. |

**Run 1 FAIL là một lần E0 bắt đúng việc, đáng ghi lại.** Vi phạm duy nhất: `E0-04d-prose-error-tokens` —
*"contracts/telegram/delivery.md: prose names 'BLOCKED_TOOL', which is neither a registered error code nor a
listed vocabulary word"*. Worker đã tự đặt ra token `BLOCKED_TOOL` cho tình huống "trang nằm trong quyền
nhưng công cụ không đọc nổi". Cách sửa **không** phải thêm từ ấy vào `STATUS_VOCABULARY` của
`evidence/tools/e0_check.py` (file đó ngoài lease, và nới oracle để câu mình viết được pass là đúng thứ
`worker.md` cấm), mà là dùng **từ đã đăng ký đúng nghĩa**: `protocol.md` §5 xếp "nguồn/dependency/oracle
thiếu" và `worker.md` điều 5 xếp "thiếu **tool capability**" vào cùng một trạng thái —
**`BLOCKED_DEPENDENCY`**. Đổi tên trong cả năm file; sắc thái "thiếu công cụ, không thiếu nguồn" được giữ
bằng một mệnh đề giải thích ngay tại chỗ, không bằng một token mới.

---

## 4. Unresolved / findings mở

| ID | Nội dung | Ai giải |
| --- | --- | --- |
| `CR-PC07-04` (ba dòng) | `callback_data`, parse mode + bảng escape, số nút mỗi hàng/bàn phím. Cần khả năng đọc cả trang `/bots/api` dưới cùng ranh giới host | Coordinator → Owner (amendment **công cụ**), rồi một packet tìm dữ kiện thứ hai |
| `delivery.md` front matter | `version: 0.1.0` chưa bump (§2 đòi minor → `0.2.0`); `verification:` vẫn viết *"Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có mạng)"*, nay **sai một phần**. Cả hai **ngoài** vùng §3.4 được cấp | Chủ file (PC07) với một packet mới |
| Câu chữ "năm giới hạn `KC`" | `contracts/telegram/commands.yaml` (§CMD-save `size_note_vi`, `response_rules.length_vi`, `EDGE-02`), `acceptance/scenarios.yaml`, `precode/README.md`, `precode/gates.yaml` G3-X5, `precode/review.md`, `docs/master-plan.md`, `acceptance/fixtures/ui/README.md` và 8 card `agent-tasks/*` — nay phải đọc là **ba** | Coordinator |
| `precode/review.md` dòng 1001 | Ghi `CR-PC07-04` = `CLOSED_CLAIMED`, *"gói liên quan tự khai đã đóng; chưa xác minh độc lập"*. Nhãn ấy sinh từ heuristic quét file, **không** từ một lần đọc tài liệu nào — nó sai **cả trước lẫn sau** lần đọc này. Trạng thái đúng hôm nay: `PARTIALLY_RESOLVED`, còn mở | PC09 / Coordinator |
| Re-pin | `contracts/telegram/delivery.md` đổi byte ⇒ mọi card pin hash file đó **`STALE`** (§5 change-control) | Coordinator |
| Cổng Phase 5 | `OD-20260908-05` mục 2 viết *"Phase 5 … is authorised to start once the five facts land"*. **Hai** đáp, **ba** không ⇒ điều kiện, đọc theo nguyên văn, **chưa** thỏa | Owner (chỉ Owner mới nới được câu ấy) |
| `SG-01` | `TC-telegram-unknown-delivery`, `TC-telegram-linking-auth`: **KHÔNG** được nới. Nhánh multipart cần **chỗ cắt**; chỗ cắt cần parse mode + bố cục nút. 4096 một mình không đủ | Giữ nguyên tới khi ba dòng có nguồn |

---

## 5. Bảy điều packet này KHÔNG làm

1. **Không** đóng `CR-PC07-04`. Ba trong năm dữ kiện còn thiếu ⇒ `PARTIALLY_RESOLVED`. §1 luật 3 của
   `change-control.md`: người phát hiện không phải người phê duyệt.
2. **Không** nâng trần claim nào: `delivery.md` giữ `DRAFT_FOR_REVIEW`; `MOD-telegram-adapter` vẫn
   **BLOCKED (cứng)**; không tuyên bố `CONTRACT_READY` cho §3.4.
3. **Không** ghi ngoài sáu path của lease — kể cả `evidence/tools/e0_check.py` (nơi một dòng thêm vào
   `STATUS_VOCABULARY` sẽ làm run 1 pass), kể cả front matter của chính file mình vừa sửa.
4. **Không** đặt một con số nào không có câu trích: không biên an toàn cho UTF-16, không số nút, không byte
   callback data, không ngưỡng multipart.
5. **Không** đụng `contracts/retry-policy.yaml`: ba câu rate limit là **trần lập kế hoạch**, không phải ngân
   sách retry mới, và `Retry-After` thật vẫn thắng.
6. **Không** gọi `api.telegram.org`, **không** dùng bot token, **không** gửi một tin nào, **không** đi theo
   một redirect nào ra ngoài `core.telegram.org`.
7. **Không** tự chứng nhận freeze và **không** viết "independent audit passed": bằng chứng ở §3 là
   `SELF_VALIDATION`. Coordinator rehash độc lập trước khi freeze.

---

# ADDENDUM — `PKT-PC07-FIX-TELEGRAM-2` · `LEASE-PC07-TELEGRAM-p2` · cùng ngày (2026-09-08 giờ Owner)

Coordinator mở lại lease, **mở rộng vùng ghi của `delivery.md` từ §3.4 sang cả file** (front matter mô tả
đúng cái §3.4 vừa đổi), kèm ba hướng thử cụ thể cho ba dữ kiện còn `KC`.
**Status vòng hai: `DONE_WITH_CONCERNS`.** Front matter đã sửa; **ba dữ kiện GIỮ `BLOCKED_DEPENDENCY`**.
`lease_released_at` (p2): `2026-09-07T18:25:00Z` = `2026-09-08T01:25` giờ Owner. Sau mốc này Worker không
ghi thêm, kể cả sửa lỗi đánh máy — muốn sửa tiếp cần packet mới, baseline mới, lease mới.

## A1. Ba hướng thử — kết quả

| # | Hướng được giao | Đã làm | Kết quả |
| --- | --- | --- | --- |
| 1 | Parse mode + escape: thử `#formatting-options`, rồi `#markdownv2-style` / `#html-style` | Cả ba, `WebFetch` | **TRUNCATED** cả ba. Điểm dừng lần lượt `date-time entity formatting`, `WebAppData`, `InputChecklist` |
| 2 | `callback_data`: thử `#inlinekeyboardbutton` | Có (lần thứ hai, cache đã hết hạn) | **TRUNCATED**, dừng ở `MessageAutoDeleteTimerChanged` |
| 3 | Số nút: thử `#inlinekeyboardmarkup`, và một `WebSearch` | `#inlinekeyboardmarkup` **và** `#replykeyboardmarkup`: TRUNCATED (`InputChecklist`). `WebSearch`: **KHÔNG chạy** | Xem A2 |

Tổng cộng **bảy anchor / tám lần gọi**, hai vòng, cùng một trang. **Cả tám bị cắt trước `Available
methods`.** Điểm cắt **xê dịch** giữa các lần (`MessageAutoDeleteTimerChanged`, `date-time entity
formatting`, `WebAppData`, `InputChecklist`) nên cửa sổ đọc không tất định — nhưng lần đi xa nhất vẫn nằm
trong `Available types` và vẫn **trước** `InlineKeyboardMarkup`, `InlineKeyboardButton` và `Formatting
options`. Giả thuyết "anchor dời được cửa sổ đọc" đã được **thử thật** và **sai**; nó không còn là một
hướng chưa kiểm.

## A2. `WebSearch` — KHÔNG chạy, `BLOCKED_SCOPE`. Lý do là quyền, không phải kỹ thuật.

`OD-20260908-05` mục 2 (`AUTH-OWNER-20260908-06`) nguyên văn: *"a Worker may fetch documentation pages only
under `core.telegram.org`"*, kèm *"No live Bot API calls …, no bot token used, no message sent."* Một truy
vấn tìm kiếm đi tới **một host khác** và **mang theo nội dung truy vấn** — nó không phải "fetch a
documentation page under core.telegram.org", và `site:` chỉ lọc kết quả chứ không đổi nơi nhận request.
`protocol.md` §2: grant con là **subset** của grant cha; Coordinator **không** nới được grant của Owner.
`worker.md`: không dùng live network ngoài capability/authority explicit.

Đây là chỗ dễ nhất để trôi: một câu trong packet, một truy vấn trông vô hại, và ranh giới host mà Owner đã
viết ra biến mất. Worker dừng và trả `BLOCKED_SCOPE` cho **riêng** bước ấy. Muốn đi hướng này thì cần một
**amendment của Owner** thêm một nguồn tìm kiếm vào allowlist — hệt như `help.openalex.org` ở §8.13.2 của
`precode/decision-register.md`. Việc còn lại của vòng hai vẫn chạy bình thường; chỉ bước này dừng.

## A3. Vì sao dòng "số nút mỗi hàng" vẫn KHÔNG đóng được bằng một câu phủ định

Packet vòng hai đề nghị: nếu tìm kỹ mà không thấy gì chính thức thì ghi *"no official maximum found on
core.telegram.org as of 2026-09-08"* thay vì để `KC` mãi — và nói rõ **chỉ sau khi đã thử thật**. Đã thử
thật, và câu ấy vẫn **chưa** ghi được ở dạng mạnh. Lý do đo được: 12 trang đọc được không nêu con số, nhưng
trang có nhiều khả năng nêu nó nhất — `InlineKeyboardMarkup` trên `/bots/api` — **chính là** trang không đọc
được. Một phủ định chỉ có giá trị khi tập đã đọc **bao được** chỗ dữ kiện có thể nằm; tập này có một lỗ
thủng đúng ngay giữa. Câu ghi vào `delivery.md` §3.4 vì vậy là **phủ định có phạm vi** — *"không tìm thấy
con số chính thức trên 12 trang đã đọc được dưới `core.telegram.org` ngày 2026-09-08"* — cùng loại với
`arxiv_identification_required = false` ở §8.13.1, và nó **không** nâng dòng ấy ra khỏi `KC`.

## A4. Front matter — đã sửa

| Trường | Before (nguyên văn) | After |
| --- | --- | --- |
| `version` | `0.1.0` | `0.2.0` (§2 change-control, hàng minor; một lần bump cho cả hai vòng) |
| `verification:` câu cuối | *"E1–E4: NOT_RUN. Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có mạng)."* | `E1–E4: NOT_RUN` giữ nguyên; phần còn lại thay bằng: **hai** dữ kiện `DOCS_derived` kèm hạn dùng (4096 ký tự; rate limit gửi, đọc 2026-09-08), **ba** dữ kiện `KC`/`BLOCKED_DEPENDENCY` gọi tên đích danh và nói rõ là thiếu **tool capability** chứ không thiếu nguồn, cộng kết luận rằng nhánh multipart của §3.5 vẫn chưa hiện thực được và `MOD-telegram-adapter` vẫn bị chặn cứng |
| `claim_ceiling` | `DRAFT_FOR_REVIEW` | **KHÔNG đổi.** Đọc được hai giới hạn không làm hợp đồng sẵn sàng; bump version không phải một lần nâng trần claim |

Mục "still_open (1)" ở §4 bên trên — front matter chưa sửa — **đã đóng bởi addendum này**. Hai mục còn lại
của §4 (câu chữ "năm giới hạn `KC`" ở 14 file/card; `precode/review.md`:1001 `CLOSED_CLAIMED`) **vẫn mở** và
vẫn ngoài lease. Cổng Phase 5 của `OD-20260908-05` mục 2 **vẫn** chưa thỏa như đã viết: 2/5.

## A5. Delta vòng hai — before/after hash + bytes

`before` của vòng hai = `after` của vòng một (§2), đã kiểm lại ngay trước khi ghi.

| Path | Op | before sha256 / bytes | after sha256 / bytes |
| --- | --- | --- | --- |
| `contracts/telegram/delivery.md` | MODIFY (front matter + §3.4) | `917031ea03b5416c63ee5bcb266bb64de26ad57587f8828abfa5faa7ed5da6fe` / 22221 | `SEE-A6` |
| `precode/decision-register.md` | MODIFY (thêm §8.14.2) | `d98f017485f15ad558b644131e4e5acae33162f856ca7dce6eefee85417abbf5` / 152722 | `SEE-A6` |
| `precode/change-control.md` | MODIFY (thêm `CR-PC07-04.a`) | `b22a92831d6bbacffb3a86cb3797f13e62f8055feaf59fb890d3a1e13e2fbed0` / 51183 | `SEE-A6` |
| `evidence/handoffs/PC07-TELEGRAM-handoff.md` | MODIFY (addendum này) | `e721b14a73b496d2c45bb5654ba57756142e5c05f02700269356f5911ce35040` / 18117 | file này |
| `precode/requirements.csv` | **KHÔNG chạm** | `36138c9f67dcf93c73c8e7b06ecc753cf76f585e41ab32b1ed0a7a7c9468869f` / 76415 | không đổi |
| `acceptance/traceability.csv` | **KHÔNG chạm** | `ff7bb430b592dc4782a3a56b9bd4f0017af6188908b99f15dfbd644ca75f7caf` / 96122 | không đổi |

Hai CSV **cố ý không chạm ở vòng hai**: ghi chú vòng một của chúng nói "ba giới hạn còn `KC`,
`BLOCKED_DEPENDENCY`" — vẫn đúng từng chữ sau vòng hai. Sửa một file chỉ để nó trông "mới" là ghi thừa.

## A6. Evidence record vòng hai

| Trường | Giá trị |
| --- | --- |
| evidence_id | `EV-PC07-TELEGRAM-02` |
| producer | `worker-WT` · kind **`SELF_VALIDATION`** |
| command | `PYTHONDONTWRITEBYTECODE=1 python3 evidence/tools/e0_check.py --repo /mnt/virtual/repo/xcrawl --json-out <scratch>.json` (chỉ đọc, json ra ngoài repo) |
| oracle | 25 check E0; kỳ vọng: 0 vi phạm trên các file trong lease |
| observed | `TOTAL: 25 checks — PASS 25 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0`; exit `0` |
| status | **PASS** trên bytes cuối cùng của vòng hai |
| limitations | Như §3: E0 tĩnh, không chứng minh runtime; nội dung trang do một mô hình đọc hộ trong `WebFetch`, không có bản lưu byte-for-byte. Thêm một giới hạn riêng của vòng hai: kết luận "anchor không dời được cửa sổ đọc" dựa trên **tám lần gọi**, và cửa sổ ấy **không tất định** — một lần gọi khác có thể đi xa hơn `InputChecklist`. Nó **không** chứng minh trang ấy vĩnh viễn không đọc được; nó chứng minh tám lần thử đều không tới. |

Hash cuối cùng của bốn file (kể cả file này) do Coordinator tính lại độc lập trước khi freeze — Worker
không tự chứng nhận, và một hash tự ghi trong chính file mình vừa ghi thì không tự kiểm được.

---

# ADDENDUM 2 — `PKT-PC07-FIX-TELEGRAM-3` · `LEASE-PC07-TELEGRAM-p3` · `OD-20260908-07` mục 1

Owner nới quyền **đúng chỗ vòng hai dừng lại**: được dùng **WebSearch** để tìm **đường đọc** chính trang
`core.telegram.org/bots/api` (bản lưu trữ / cache / cách lấy lát nhỏ hơn). Mọi cấm cũ giữ nguyên.
**Status vòng ba: `DONE_WITH_CONCERNS`. Không dữ kiện nào đổi trạng thái — cả ba vẫn `BLOCKED_DEPENDENCY`.**
`lease_released_at` (p3): `2026-09-07T18:36:00Z` = `2026-09-08T01:36` giờ Owner.

## B1. Sáu đường đã thử dưới quyền mới

| Đường | Kết quả |
| --- | --- |
| WebSearch — tìm bản lưu trữ của chính trang ấy | Xác nhận Wayback **có** snapshot (`web.archive.org/web/*/core.telegram.org/bots/api`) |
| WebSearch, `allowed_domains = core.telegram.org` — `callback_data "1-64 bytes"` | Trả URL của chính host; snippet **không** mang câu cần trích |
| `web.archive.org/web/20200215000000id_/…/bots/api` | **Chặn ở tầng nền tảng**: *"Claude Code is unable to fetch from web.archive.org"* |
| `web.archive.org/web/20160801000000id_/…/bots/api` | Cùng lỗi chặn |
| `archive.ph/newest/…` | *"unable to fetch from archive.ph"* |
| `corefork.telegram.org/bots/api` (mirror của **chính Telegram**) | Tải được, **cùng cỡ trang** ⇒ cắt y hệt, dừng trong `Message` |

**Giả thuyết đã dùng, và vì sao nó chết.** Trang Bot API **lớn dần theo năm**; một snapshot 2020 (đã có
MarkdownV2 từ Bot API 4.5, 12/2019) hẳn nhỏ hơn bản 2026 đủ để lọt cửa sổ đọc — nên hai URL Wayback được
chọn có chủ đích (2020 cho bảng escape, 2016 cho `callback_data`, nhỏ hơn nữa). Suy luận ấy vẫn đúng; nó
chết vì một lý do **không liên quan tới Telegram**: nền tảng chặn cứng host lưu trữ. Đây là **loại chặn thứ
ba** trong hồ sơ — không phải `BLOCKED_SCOPE` (quyền vừa được nới, đã đủ), không phải thiếu nguồn (trang và
snapshot đều tồn tại) — vẫn là `BLOCKED_DEPENDENCY`, thiếu **tool capability**, ở một chỗ khác của cùng bức
tường.

## B2. Điều vòng ba KHÔNG làm — chỗ dễ trượt nhất của cả ba vòng

Tìm kiếm **có** trả về con số: trang thứ ba (n8n docs, grammY, blog) nêu *"4096 characters after entities
parsing"*, *"UTF-16 length limit of 4096"*, và mô tả luật escape MarkdownV2 — và chúng **có vẻ khớp** giả
định 64 byte đang nằm trong `1:<ri>:<ii>:<lg>:<rv>`. **Không một chữ nào vào hợp đồng.**
`OD-20260908-07` mục 1: *"not substituting a third-party's restatement of the numbers as if it were the
source"*. Cám dỗ lớn nhất luôn là lúc câu trả lời **trông đã đúng rồi**; ghi ra đây rằng chúng tồn tại và
cố ý bị bỏ qua, để lần sau không ai tưởng là chưa tìm thấy gì rồi tự điền.

## B3. Việc cần xin ở vòng sau — cụ thể, và là việc duy nhất còn lại

Cả ba vòng thất bại vì **kích thước**, không vì host: trang ~1.5 MB, dữ kiện ở nửa sau. Tổng cộng đã thử
**12 trang cùng host**, **7 anchor / 8 lần gọi**, **3 host lưu trữ**, **1 mirror của chính Telegram**.
Thứ giải được là một cách đọc **theo lát** trên **đúng URL chính thức**: HTTP `Range`, hoặc một công cụ
fetch có offset/phân trang. Đó là amendment về **công cụ** — không mở thêm host, không đổi một điều cấm
nào, không cần thêm quyền mạng nào ngoài cái đã có. Nếu cả cách ấy cũng không có, ba dòng ở lại `KC` và
`MOD-telegram-adapter` ở lại **BLOCKED (cứng)**.

## B4. Delta vòng ba + evidence

`before` vòng ba = `after` vòng hai (§A5). Hai CSV **không chạm** (bytes không đổi qua cả vòng hai và ba).

| Path | Op | before sha256 / bytes | after |
| --- | --- | --- | --- |
| `contracts/telegram/delivery.md` | MODIFY (`version` `0.2.0→0.2.1`, §3.4 thêm đoạn vòng ba) | `3c64a2ecfa8e81fc2953d65934d421dfd8689f6d58f71f476d76b9f6aba1b002` / 24619 | Coordinator rehash |
| `precode/decision-register.md` | MODIFY (thêm §8.14.3) | `74962d0bd779d76f0702ac5e436f0fd256263c6903b9cd008ca45bf6f7495bfc` / 156845 | Coordinator rehash |
| `precode/change-control.md` | MODIFY (thêm `CR-PC07-04.b`) | `b35897538048aa7d94f7f2de5ca33c0e80ab107236516cb846dc492f26e80a08` / 56787 | Coordinator rehash |
| `evidence/handoffs/PC07-TELEGRAM-handoff.md` | MODIFY (addendum này) | `785bf0deb627897faf87bb07c74184587511ce8263cf921f74d0ed4d7a805a4b` / 26794 | file này |

## B5. `BLOCKED_LEASE` — hai Worker cùng ghi ba file trong lease này (phát hiện lúc chốt hash)

Lúc tính hash cuối vòng ba, ba file lệch xa hơn delta của chính packet này:
`precode/decision-register.md` +16.6 KB (§8.14.3 của tôi ~4 KB), `precode/change-control.md` +13.2 KB
(`CR-PC07-04.b` ~5 KB), và `precode/requirements.csv` đổi hash **dù vòng ba không chạm nó**. Nguyên nhân:
`worker-WAI` (`PKT-PC06-FIX-OQ03`, lease `LEASE-PC06-OQ03-p2`) đang ghi **cùng ba file** — thấy được tại
`precode/change-control.md` dòng ~818 (`cr_id: CR-PC06-OQ03-03`, `raised_by: worker-WAI`).

`protocol.md` §2: lease mặc định **độc quyền toàn physical path**, và bộ profile này **không** bật
range-sharing — "một region riêng không cho phép hai process thay nguyên cùng file". Hai lease độc quyền
trên cùng ba path là **overlap**, và §5 xếp nó vào `BLOCKED_LEASE`: quiesce, xác minh, cấp lease mới.
`uniqueItems` trong schema **không** bắt được overlap xuyên packet — đúng cảnh báo của §2.

**Điều quan sát được, không suy đoán:** cả hai phần nội dung đều còn nguyên trên đĩa — `CR-PC06-OQ03-03`
của WAI và `CR-PC07-04.b` của tôi cùng tồn tại; các mốc của tôi (`§8.14.3`, `corefork`) đều còn. Mọi thao
tác ghi của tôi là thay chuỗi có neo trên bytes **đang có**, nên không ghi đè vùng của ai. **Điều KHÔNG
kiểm được:** liệu WAI có ghi đè vùng của tôi ở một thời điểm giữa hay không, và trật tự hai luồng ghi.
Không có fencing token, không có lock — nên đây là *quan sát*, **không** phải một bằng chứng "không mất mát".

**Hệ quả cho bảng B4:** cột `before` của `decision-register.md` và `change-control.md` là hash **vòng hai
của tôi**, và đó **không** phải bytes trên đĩa ngay trước khi tôi ghi vòng ba (bytes ấy đã gồm phần của
WAI). Ghi đúng như vậy thay vì sửa số cho khớp: một baseline sai mà đẹp thì tệ hơn một baseline lệch mà
khai. Trạng thái đúng của hai hàng đó là **`STALE_BASELINE`**. Coordinator rehash cả ba file trước freeze,
và **nên xác minh với WAI** rằng không delta nào bị mất giữa hai luồng.

**Đề nghị:** tuần tự hóa hai packet trên ba file dùng chung (`precode/decision-register.md`,
`precode/change-control.md`, `precode/requirements.csv`, và `acceptance/traceability.csv` — cả bốn đều nằm
trong cả hai lease), hoặc cấp cho mỗi Worker một file phụ lục riêng rồi Coordinator gộp. Tôi **không** tự
sửa gì thêm sau khi phát hiện: sửa tiếp dưới một lease đang tranh chấp là làm hỏng thêm bằng chứng.

`EV-PC07-TELEGRAM-03` · `worker-WT` · **`SELF_VALIDATION`** · `PYTHONDONTWRITEBYTECODE=1 python3
evidence/tools/e0_check.py --repo … --json-out <scratch>.json` (chỉ đọc) · oracle: 25 check, 0 vi phạm ·
observed: `TOTAL: 25 checks — PASS 25 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0`, exit `0` · **PASS**.
Giới hạn: như §3 và §A6; thêm một điều của vòng ba — *"web.archive.org bị chặn"* là quan sát về **nền tảng
này, hôm nay**, không phải một phát biểu rằng bản lưu trữ ấy không tồn tại hay không đọc được ở nơi khác.
