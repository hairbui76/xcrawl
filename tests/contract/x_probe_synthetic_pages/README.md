# Trang HTML tổng hợp cho bộ dò tín hiệu của probe SP1

**Mọi file `.html` trong thư mục này do người viết tay, KHÔNG phải bản chụp từ X.**
Không có byte nào ở đây đến từ một phiên X thật; không có cookie, không có token, không có
tên tài khoản, không có nội dung bài đăng thật. Mỗi file mở đầu bằng một comment
`SYNTHETIC` nói đúng điều đó, và `test_x_probe_signals.py` khẳng định comment ấy tồn tại ở
mọi file — nên một bản chụp thật lỡ rơi vào đây sẽ làm đỏ test, không nằm im.

## Vì sao chúng nằm ở đây chứ không ở `acceptance/fixtures/`

`acceptance/fixtures/**` là **oracle** của dự án (README gốc §3.2: "không có bộ dữ liệu test
thứ hai"), do change control sở hữu, và card này chỉ được đọc nó. Các file dưới đây không
phải oracle của một scenario: chúng là **đầu vào** của một unit test cho một hàm thuần
(`probe.x_feasibility.signals.detect`). Oracle của bài test đó vẫn là hợp đồng —
`contracts/ops/collector-probe.md` §4 và §5, `contracts/state/run.yaml`,
`contracts/errors.yaml` và bốn fixture `acceptance/fixtures/collection/{a,c,e,g}` — và
`test_x_probe_signals.py` đọc thẳng những file ấy để kiểm bảng ánh xạ.

Nói cách khác: HTML ở đây trả lời câu "trang trông thế này thì bộ dò nói gì", còn câu "bộ dò
nói thế thì hợp đồng có đồng ý không" vẫn do `contracts/` và `acceptance/` trả lời.

## Vì sao selector trong các file này là `PROVISIONAL`

Gói này được viết **không có mạng**: chưa một `data-testid` nào ở đây được đối chiếu với
trang X thật. Các file mô phỏng cấu trúc mà `probe/x_feasibility/dom.py` mong đợi. Nếu X
thật khác, đợt probe sẽ dừng bằng `SOURCE_LAYOUT_CHANGED` (§4 ST-7) — đúng hành vi mà
`contracts/errors.yaml` mô tả, chứ không phải một đợt rỗng im lặng. Khi đó việc phải làm là
sửa `dom.py` **và** các file này cùng lúc, rồi chạy lại probe từ đầu (§7 GO-6).

## Danh sách

| File | Trạng thái §4 mong đợi | Ghi chú |
| --- | --- | --- |
| `healthy-feed.html` | `CONTINUE` | 3 bài đủ trường: 1 có link paper, 1 chỉ ảnh, 1 thường |
| `challenge-verify.html` | `ST-1` → `captcha` | trang đòi xác minh, có widget challenge |
| `challenge-arkose-iframe.html` | `ST-1` → `captcha` | không có chữ nào khớp marker; chỉ có iframe challenge |
| `session-expired-login.html` | `ST-2` → `session_expired` | URL đăng nhập, mất marker đã-đăng-nhập |
| `access-blocked.html` | `ST-3` → `source_blocked` | trang chặn / tài khoản bị khóa |
| `rate-limited.html` | `ST-4` → `rate_limited` | trang báo vượt giới hạn nhịp |
| `layout-changed-missing-fields.html` | `ST-7` → `source_layout_changed` | có container nhưng mất `time` và `User-Name` |
| `layout-changed-no-containers.html` | `ST-7` → `source_layout_changed` | trang feed nhưng không có container nào |
