# `probe/` — probe khả thi SP1 cho nguồn X

Thư mục này thuộc card [`agent-tasks/TC-x-feasibility-probe.md`](../agent-tasks/TC-x-feasibility-probe.md)
(mốc **M0**, cổng **SP1**). Giao thức là
[`contracts/ops/collector-probe.md`](../contracts/ops/collector-probe.md); file này là
**runbook**: từng bước Owner làm trên máy của mình.

> ## Đọc trước: probe CHƯA CHẠY và CHƯA ĐƯỢC PHÉP CHẠY
>
> Code ở đây là **công cụ**, không phải bằng chứng. Không một đợt nào đã chạy; trạng thái
> bằng chứng về khả thi nguồn X là **`NOT_RUN`**, và
> [`evidence/runs/SP1-x-feasibility/`](../evidence/runs/SP1-x-feasibility/) trống.
>
> Hai điều còn chặn:
>
> 1. **Cổng Owner** — `collector-probe.md` §6 đòi **bốn** xác nhận bằng văn bản. Mục 1
>    (D09 — profile Chrome riêng) đã được trả lời ở `OD-20260907-01`. **Mục 2, 3, 4 vẫn
>    `OWNER_DECISION_REQUIRED`** (`OD-20260907-03`). Đây là **stop tuyệt đối** (card
>    `SG-02`), và `run_probe.py` từ chối mở trình duyệt khi chưa đủ bốn.
> 2. **Máy của Owner** — probe chạy trên Chrome thật, profile riêng của dự án, tài khoản X
>    thật. Không CI, không agent, không máy nào khác được chạy nó.
>
> Viết sẵn công cụ **không** mở cổng. Cổng mở bằng câu trả lời của Owner, không bằng việc
> có sẵn một lệnh chạy được.

---

## 1. Điều tuyệt đối không được làm

`collector-probe.md` §2 và `contracts/capabilities.yaml` `DC-COL-07`. Đây là **ràng buộc**,
không phải tham số — vi phạm là **hỏng probe**, không phải "tối ưu probe", và làm card
**FAIL ngay** bất kể con số thu được (`docs/master-plan.md` §3 Giai đoạn 2A):

- **Không né CAPTCHA** dưới bất kỳ hình thức nào: không giải tự động, không dịch vụ giải hộ,
  không giả lập thao tác xác minh.
- **Không giả fingerprint**, không đổi user-agent để trông như trình duyệt khác.
- **Không luân chuyển account hoặc proxy** để vượt chặn.
- **Bị chặn thì DỪNG và BÁO.** Không thử lại tự động, không "chờ rồi thử account khác".
- **Không dùng X API trả phí** như đường vòng khi probe thất bại — đó là quyết định của
  Owner, không phải của người chạy probe (SRC-PLAN §12).

Lý do những dòng này đứng ở đây, chứ không chỉ trong đặc tả: một probe đo *"lấy được bao
nhiêu bài"* tạo áp lực tự nhiên lên chính ranh giới của nó. **Con số đẹp đạt được bằng cách
vượt ranh giới là bằng chứng giả.**

Ba việc trên đều **vắng mặt trong code**, và
`tests/contract/test_x_probe_boundaries.py` khẳng định điều đó bằng máy: không có lời gọi
`click` nào (nên không có gì để lỡ trỏ vào nút xác minh), không đặt user-agent, không cấu
hình proxy, không tiêm init-script, không tên dịch vụ giải CAPTCHA nào, không đường nào tới
`api.x.com`. Chính `probe/x_feasibility/config.py` cũng **từ chối** một file cấu hình mang
các khóa đó.

## 2. Cái này chạy trên máy nào

Máy cá nhân của Owner, có Chrome thật. Không phải server, không phải CI. `ADR-0001` và
`REQ-S6.4-02` đặt collector ở đó; probe cùng chỗ vì nó dùng đúng profile ấy.

## 3. Chuẩn bị (làm một lần)

### 3.1 Môi trường Python

```bash
uv sync --all-packages     # Playwright (thư viện Python) đã nằm trong uv.lock
uv run playwright install chromium   # CHỈ trên máy Owner; repo không bao giờ chạy lệnh này
```

Bước thứ hai tải binary trình duyệt. Nó **không** phải bước cài của repo và **không** chạy
trong CI (`README.md` §1, `ADR-0011`: không có job live).

> Probe mặc định dùng `"chrome_channel": "chrome"` — Chrome **thật** đã cài trên máy, đúng
> tinh thần P1 ("Chrome thật trên máy cá nhân"). Nếu máy không có Chrome, đổi
> `chrome_channel` thành `"chromium"` và ghi lại điều đó trong `notes_vi` của đợt: nó là
> một khác biệt về điều kiện đo, không phải một chi tiết vặt.

### 3.2 Profile Chrome RIÊNG của dự án (REQ-D09)

```bash
mkdir -p ~/rr-x-profile
```

Đây phải là một thư mục **mới**, **không** phải profile Chrome hằng ngày của bạn.
`run_probe.py` **từ chối chạy** nếu đường dẫn trỏ vào profile mặc định
(`~/.config/google-chrome`, `~/Library/Application Support/Google/Chrome`,
`AppData/Local/Google/Chrome/User Data`, …). Prerequisite P1 nói rõ profile mặc định
**không bị chạm**, và một lỗi gõ đường dẫn là đúng cách nó sẽ bị chạm.

### 3.3 Đăng nhập X trong profile đó — bằng tay

```bash
uv run python - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir="/home/<bạn>/rr-x-profile", channel="chrome", headless=False)
    ctx.new_page().goto("https://x.com/login")
    input("Đăng nhập X trong cửa sổ vừa mở, xong thì Enter ở đây để đóng...")
    ctx.close()
PY
```

Đăng nhập **bằng tay, bằng mắt bạn**. Probe không bao giờ nhập mật khẩu, không lưu
credential, không đọc cookie. Phiên nằm trong thư mục profile và ở nguyên đó — nó **không**
được đồng bộ lên server (`contracts/capabilities.yaml`, `ACT-collector.secret_items`).

### 3.4 Cổng debug chỉ nghe loopback (P4)

Probe không mở cổng debug. Nếu bạn tự mở, kiểm bằng `ss -ltnp | grep 9222`: không được
lắng nghe trên `0.0.0.0`, không qua reverse proxy (SRC-SPEC §11.2).

## 4. Cấu hình

Chép [`probe/probe-config.example.json`](probe-config.example.json) thành file của bạn
(ví dụ `~/rr-probe.json` — **để ngoài repo**, đừng commit) và sửa:

| Trường | Ý nghĩa |
| --- | --- |
| `chrome_user_data_dir` | thư mục profile ở §3.2, **đường dẫn tuyệt đối** |
| `search_terms` | từ khóa tìm trên X. Tag ở đây **chỉ để tìm kiếm** (REQ-D24) |
| `output_dir` | mặc định `evidence/runs/SP1-x-feasibility` |
| `max_posts_per_run` / `max_duration_s` | ngân sách §3.2 — **hạ được, không nâng được** |
| `request_min_interval_ms` | **sàn** 2000 ms giữa hai thao tác điều hướng |
| `owner_confirmations` | bốn xác nhận §6 — xem §5 dưới đây |
| `extra_markers` | chuỗi bổ sung cho bộ dò tín hiệu — xem §7 |

Kiểm cấu hình mà **không** mở trình duyệt:

```bash
uv run python probe/x_feasibility/run_probe.py --config ~/rr-probe.json --dry-run
```

`--dry-run` kiểm config, cổng §6 và cổng lịch §3.1 rồi thoát. Nó **không** mở Chrome và
**không** chạm X.

## 5. Cổng Owner §6 — bốn xác nhận, bằng văn bản

Probe không chạy cho tới khi bạn xác nhận **bằng văn bản** cả bốn điều, và ghi nơi chứa
văn bản ấy vào `evidence_ref` của từng mục:

| Khóa trong config | Điều cần xác nhận |
| --- | --- |
| `d09_project_chrome_profile` | dùng Chrome profile riêng của dự án — **đã trả lời**, `OD-20260907-01` mục 1 |
| `budget_and_stop_conditions` | ngân sách §3 và điều kiện dừng §4 chấp nhận được với tài khoản X của bạn |
| `go_no_go_criteria` | tiêu chí go/no-go §7 là tiêu chí bạn đồng ý dùng để kết luận |
| `account_risk_understood` | probe chạy trên **tài khoản X thật của bạn** và mang rủi ro bị hạn chế tài khoản (REQ-A7), rủi ro đó **không kiểm chứng được trước** |

`confirmed: true` với `evidence_ref` rỗng **không** tính là xác nhận: §6 đòi "bằng văn bản",
và một giá trị `true` do chính người chạy gõ vào là tự cấp phép cho mình. Ba mục cuối hiện
là `OWNER_DECISION_REQUIRED`; cho tới khi chúng có câu trả lời, `--dry-run` sẽ in đúng ba
mục còn thiếu và lệnh chạy thật trả mã thoát `2`.

**Về mục 4, nói thẳng.** REQ-A7 là `KC`: *"X có thể hạn chế tài khoản dù người dùng tự giải
CAPTCHA; không kiểm chứng được trước"*. Nghĩa là không ai — kể cả tài liệu này — nói được
xác suất tài khoản của bạn bị hạn chế. Probe hạ rủi ro bằng ngân sách nhỏ, nhịp chậm và điều
kiện dừng cứng; nó **không** loại bỏ rủi ro.

## 6. Chạy một đợt

Một lệnh, một đợt:

```bash
uv run python probe/x_feasibility/run_probe.py --config ~/rr-probe.json
```

Thêm ghi chú của bạn về phần feed bạn biết là không quan sát được:

```bash
uv run python probe/x_feasibility/run_probe.py --config ~/rr-probe.json \
  --note "Hôm nay chỉ chạy một từ khóa; nhánh 'graph neural networks' chưa quét."
```

Cửa sổ Chrome mở ra và bạn **nhìn thấy** nó cuộn. Đó là cố ý: `headless=False` để bạn quan
sát được, và để nếu X đòi xác minh thì **bạn** là người xử lý, không phải một dòng code.

### Lịch (§3.1, probe tự ép)

| Ràng buộc | Giá trị | Probe làm gì |
| --- | --- | --- |
| tổng số đợt | 5–10 | từ chối đợt thứ 11 |
| đợt mỗi ngày | ≤ 4 | từ chối đợt thứ 5 trong cùng ngày UTC |
| khoảng cách hai đợt | ≥ 60 phút | từ chối nếu đợt trước kết thúc chưa đủ 60 phút |
| trải qua | ≥ 3 ngày khác nhau | không tự ép được; **bạn** giữ, và §7 GO-1 chỉ có nghĩa nếu bạn giữ |

Card §8 nêu ví dụ `--runs 5`. Lệnh đó **bị từ chối**, kèm lý do: 5 đợt trong một lần gọi
vượt `probe_runs_per_day_max = 4` của §3.1. Nhịp đúng là **`--runs 1`, hai lần mỗi ngày,
trong 3–5 ngày** — cũng chính là nhịp vận hành 08:00/20:00 mà probe cần đo.

### Mã thoát

| Mã | Nghĩa |
| --- | --- |
| `0` | đợt xong và đã ghi bản ghi |
| `2` | một cổng từ chối (cổng Owner §6, cổng lịch §3.1, hoặc config sai) — **chưa mở trình duyệt** |
| `3` | đợt dừng vì tình huống nguồn (§4) — **vẫn đã ghi bản ghi** |
| `4` | sai cách dùng / lỗi đọc ghi file |

## 7. Khi đợt dừng giữa chừng

Probe dừng **ngay** ở mọi tình huống §4. Không có tình huống nào cho phép "thử lại rồi tiếp"
— `I10` cấm tự retry sau CAPTCHA, và §2 cấm mọi hình thức lách.

| `stop_reason` | Chuyện gì đã xảy ra | Bạn làm gì |
| --- | --- | --- |
| `limit_reached` | chạy hết ngân sách bài hoặc thời gian | **không phải lỗi** (AMD-B02). Đây là kết cục mong muốn của một đợt lành |
| `captcha` | X đòi xác minh | **Bạn** tự xử lý trong Chrome nếu muốn, **sau khi probe đã thoát**. Không chạy lại ngay: chờ hết 60 phút |
| `session_expired` | phiên hết hạn | đăng nhập lại bằng tay theo §3.3, rồi chạy đợt sau |
| `source_blocked` | X chặn truy cập | **DỪNG HẲN probe** và báo Coordinator. Không đổi gì để thử lại. Một lần bị chặn thật là no-go (§7 GO-3) |
| `rate_limited` | X vẫn cho vào nhưng bảo chậm lại | không thử lại trong đợt. Đợt theo lịch kế tiếp chạy bình thường — rate limit tự hết |
| `source_layout_changed` | vào được nhưng **không đọc được** | báo Coordinator: cần **người phát triển** sửa bộ đọc (`probe/x_feasibility/dom.py`), rồi **chạy lại từ đầu** (§7 GO-6) |
| `operator_stop` | bạn bấm Ctrl-C | bản ghi vẫn được ghi với phần đã quan sát |

**Nếu `source_layout_changed`: đừng gửi bản chụp trang.** Một trang X đã đăng nhập chứa
thông tin phiên. Gửi bản ghi JSONL và `probe.log` — cả hai đã được che — và mô tả bằng lời
điều bạn nhìn thấy.

`data-testid` mà bộ đọc dựa vào (`probe/x_feasibility/dom.py`) là **PROVISIONAL**: gói này
được viết **không có mạng**, chưa một selector nào được đối chiếu với trang X thật. Nếu
chúng sai, đợt đầu tiên sẽ dừng bằng `source_layout_changed` — đó là hành vi **đúng**
(`contracts/errors.yaml`: "vào được nhưng không đọc được"), không phải một đợt rỗng im lặng.
Chữ hiển thị mà bộ dò tìm (`probe/x_feasibility/signals.py`) cũng vậy: nếu tài khoản bạn
thấy chữ khác, thêm vào `extra_markers` trong config — **thêm được, không xóa được**.

## 8. Probe này KHÔNG làm gì

- **Không** gọi server: không `ingest.submit_batch`, không `worker.report_stop`, không DB,
  không outbox, không job. M0 chạy dry-run (§1 P6) và đầu ra là file.
- **Không** gọi AI, không gửi Telegram.
- **Không** mở arXiv/OpenAlex hay bất cứ host nào ngoài X (`SL-4 chrome_scope: x_only`);
  config từ chối một `x_base_url` không phải X.
- **Không** mở thread, không mở reply, không mở trang tác giả. `author_threads_opened` vì
  vậy luôn `0`, và mỗi bản ghi nói điều đó trong `unobservable_scope_vi`. Không tiêu chí
  go/no-go nào dùng trường này; mở thread sẽ đốt ngân sách và kéo theo nghĩa vụ `SL-1`
  (chỉ thread của chính tác giả) mà probe không cần để trả lời REQ-A1.
- **Không** ghi nội dung bài, cookie, token, ảnh chụp màn hình, đường dẫn có tên người dùng,
  hay `@handle` nào — kể cả của tác giả quan sát được. Mọi dòng log đi qua bộ che, và
  `record.py` **từ chối ghi** một bản ghi còn sót chuỗi nhạy cảm.

## 9. Tính go/no-go

Sau **ít nhất 5 đợt** (§3.1), trải qua **ít nhất 3 ngày**:

```bash
uv run python probe/go_no_go.py evidence/runs/SP1-x-feasibility/runs.jsonl
```

Nó áp `collector-probe.md` §7 **nguyên văn** — bảy tiêu chí GO-1…GO-7, không cờ nào nới
ngưỡng. Mã thoát: `0` GO · `1` NO-GO · `2` KHÔNG KẾT LUẬN · `3` không đọc được file.

- **GO** — nghĩa là *"nguồn X khả thi ở mức ngân sách đã thử, trong cửa sổ đã đo"*. **Không**
  nghĩa là X ổn định lâu dài (REQ-A7 vẫn `KC`), **không** nghĩa collector đã hoạt động,
  **không** nghĩa AC-01/AC-04 đã pass. Xem §10 của giao thức cho danh sách đầy đủ những điều
  probe này không chứng minh. Sau GO, bạn dùng chính số liệu này để chốt REQ-OQ05 (giới hạn
  thật mỗi đợt).
- **NO-GO** — báo quyết định **blocked** cho nguồn X kèm số liệu. **Không** chuyển sang X API
  trả phí, **không** nới ranh giới §2 rồi chạy lại.
- **KHÔNG KẾT LUẬN** — N < 5, hoặc N > 10, hoặc GO-6 trượt. Sửa nguyên nhân, chạy lại; không
  suy diễn từ dữ liệu thiếu.

## 10. Gửi lại những gì

Sau đủ số đợt, gửi Coordinator **ba** thứ:

1. `evidence/runs/SP1-x-feasibility/runs.jsonl` — một dòng mỗi đợt (đã che sẵn);
2. `evidence/runs/SP1-x-feasibility/probe.log` — log đã che;
3. đầu ra của `probe/go_no_go.py` (thêm `--json` nếu tiện dán).

Kèm một câu cho mỗi đợt bị dừng sớm: **bạn nhìn thấy gì trên màn hình**. Đó là thứ duy nhất
trong toàn bộ quy trình mà công cụ không ghi lại được, và nó thường là thứ giải thích con số.

**Đừng gửi**: ảnh chụp màn hình, thư mục profile, file cookie, hay cấu hình có đường dẫn đầy
đủ của bạn.

## 11. Bố cục thư mục

| Đường dẫn | Vai trò |
| --- | --- |
| `probe/x_feasibility/config.py` | cấu hình + cổng Owner §6 + cổng profile REQ-D09 |
| `probe/x_feasibility/signals.py` | bộ dò tín hiệu §4, thuần, không I/O — dừng an toàn khi không nhận ra trang |
| `probe/x_feasibility/dom.py` | selector của X (PROVISIONAL) + bộ đọc HTML ngoại tuyến |
| `probe/x_feasibility/record.py` | biểu mẫu §5, ULID, JSONL, che danh tính |
| `probe/x_feasibility/run_probe.py` | vòng chạy một đợt + CLI + driver Playwright |
| `probe/x_feasibility/go_no_go.py` | §7, nguyên văn |
| `probe/go_no_go.py` | lối vào ngắn cho lệnh ở §9 |
| `probe/probe-config.example.json` | mẫu cấu hình |
| `tests/contract/test_x_probe_*.py` | test ngoại tuyến; **không** cài, **không** mở trình duyệt |
| `tests/contract/x_probe_synthetic_pages/` | trang HTML **viết tay** làm đầu vào test |

Ngôn ngữ: Python (`agent-tasks/README.md` §5.3).
