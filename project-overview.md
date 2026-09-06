# Project Overview — Research Radar

Ngày: 05/09/2026 · Phiên bản: 0.1 · Tên dự án tạm thời

**Trạng thái:** tài liệu tổng hợp quá trình brainstorming, dùng làm đầu vào cho phỏng vấn và thiết kế. Đây chưa phải đặc tả kỹ thuật đã được duyệt toàn bộ. Các đề xuất bên dưới không tự trở thành yêu cầu đã chốt.

## 1. Sản phẩm muốn xây

Một hệ thống **tự đi đọc nghiên cứu rồi báo lại**, giúp người dùng phát hiện ý tưởng và hướng nghiên cứu đáng tìm hiểu từ X cùng các tài liệu nghiên cứu liên quan.

Người dùng chọn chủ đề bằng tag, nhận báo cáo trong application và qua Telegram, mở nguồn để đọc sâu, và Save những bài muốn giữ lại. Giá trị chính là giảm công sức tìm kiếm và kết nối các tín hiệu nghiên cứu; không yêu cầu người dùng phải chủ động lướt X mỗi lần hệ thống chạy.

Phạm vi khoa học rộng, không giới hạn ở AI/ML. Mỗi người dùng có thể theo dõi các chủ đề khác nhau. Chưa xác định bản đầu phục vụ một người, nhóm nhỏ hay nhiều tài khoản độc lập.

## 2. Các yêu cầu người dùng đã xác nhận

| ID | Yêu cầu | Ý nghĩa đối với thiết kế |
| --- | --- | --- |
| C01 | Theo dõi nghiên cứu đa ngành | Không cố định danh mục vào một ngành duy nhất |
| C02 | Cá nhân hóa bằng tag | Người dùng chọn và cập nhật chủ đề quan tâm |
| C03 | Tag thay đổi có hiệu lực từ lúc cập nhật trở đi | Nội dung gửi tiếp theo phải phù hợp cấu hình mới; mốc thời gian chính xác cần phỏng vấn |
| C04 | Kết hợp X với nguồn nghiên cứu/paper | Có khả năng đối chiếu thảo luận với tài liệu nguồn |
| C05 | Không muốn trả phí dữ liệu X | API X trả phí không phải phương án mặc định được chấp nhận |
| C06 | Muốn dùng account X có feed cá nhân hóa | Hướng mong muốn là thu thập bằng phiên account đăng nhập; tính khả thi vận hành chưa được kiểm chứng |
| C07 | Thu thập tự động; user giải CAPTCHA bằng tay | Khi cần xác minh phải dừng và để user xử lý trực tiếp |
| C08 | Mỗi đợt có điểm dừng | Có giới hạn lượng bài/thời gian và điều kiện kết thúc |
| C09 | Có Save bài trong application | Người dùng chủ động giữ bài để đọc lại |
| C10 | Giá trị chính là bot tự đọc rồi báo lại | Không chuyển sản phẩm thành extension chỉ hoạt động khi user lướt X |
| C11 | Có application và bot Telegram | Có hai kênh sử dụng cùng một hệ thống |
| C12 | Máy đủ dùng, đã có API key AI | Có key OpenAI, DeepSeek, GLM, Anthropic; không cần tiếp tục hỏi cấu hình phần cứng để bắt đầu thiết kế |

**Phân biệt ngân sách:** mong muốn miễn phí xuất phát từ chi phí thu thập dữ liệu X. Người dùng đã có API key AI và chấp nhận hướng dùng API; điều này không đồng nghĩa có hạn mức AI vô hạn hoặc yêu cầu chạy model local.

## 3. Những hướng đã xem xét và không chọn làm trải nghiệm chính

- X API trả phí: không phù hợp ràng buộc dữ liệu miễn phí hiện tại.
- Chỉ theo dõi paper, yêu cầu user dán nội dung X thủ công: không đáp ứng kỳ vọng tự động.
- Extension hỗ trợ đọc khi user lướt X: không phải giá trị chính người dùng chọn. Extension chỉ có thể là chi tiết kỹ thuật phụ nếu sau này cần, không thay thế bot tự chạy.
- Thu thập không giới hạn: đã thống nhất mỗi đợt có giới hạn.

## 4. Các đề xuất đang chờ xác nhận chi tiết

| ID | Đề xuất hiện tại | Điều còn mở |
| --- | --- | --- |
| P01 | Chạy trên máy của người dùng | OS/runtime, truy cập từ điện thoại, thời gian hoạt động và triển khai chưa chốt |
| P02 | For You kết hợp tìm kiếm theo chủ đề | Following/Lists có tham gia không; nguồn nào ưu tiên và phạm vi đọc |
| P03 | OpenAlex/arXiv hoặc nguồn gốc được dẫn | Nguồn nào có trong MVP; lấy paper độc lập hay chỉ theo link từ X |
| P04 | Thu thập hai lần mỗi ngày | Đây là mặc định được gợi ý, chưa phải lịch người dùng chọn; timezone chưa chốt |
| P05 | Báo cáo sau đợt có nội dung phù hợp | Có báo cáo tuần, giờ yên lặng, báo cáo rỗng hoặc báo cáo một phần không |
| P06 | Feed, Saved, Settings và trạng thái chạy | Danh sách màn hình, cấu trúc điều hướng và độ chi tiết chưa chốt |
| P07 | Save từ Telegram đồng bộ về app | User đã chốt Save trong app; nút Telegram và bỏ lưu cần xác nhận |
| P08 | Chọn provider/model AI trong Settings | Provider mặc định, tác vụ dùng model nào, retry và fallback chưa chốt |
| P09 | Saved không mất khi bỏ tag | Đã được đề xuất trong trao đổi, cần xác nhận quy tắc lưu giữ và xóa |
| P10 | Một kho dữ liệu chung cho app và Telegram | Cách phân quyền, số người dùng và quyền sở hữu dữ liệu chưa chốt |

Ví dụ 100 bài hoặc 10 phút mỗi đợt chỉ minh họa điểm dừng. Chúng không phải ngưỡng X cho phép, không bảo đảm tránh bị chặn và chưa phải cấu hình MVP đã chốt.

## 5. Hành trình sản phẩm dự kiến

### Thiết lập

Người dùng truy cập app, cấu hình chủ đề, nguồn, lịch chạy và giới hạn. Họ đăng nhập X trong trình duyệt do họ kiểm soát, cấu hình AI ở máy chạy hệ thống và liên kết Telegram bằng cơ chế xác minh quyền sở hữu cần thiết kế.

### Tự thu thập và phân tích

Đến lịch hoặc khi có lệnh chạy thủ công, hệ thống tạo một đợt thu thập. Bộ thu thập lấy nội dung X được phép truy cập trong phiên đăng nhập, ghi nguồn và thời điểm, nhận diện bài đã có và áp dụng điểm dừng.

Sau đó hệ thống phân loại chủ đề, truy tìm tài liệu liên quan, nhóm những bài cùng công trình/ý tưởng và tạo báo cáo. Một công trình được chia sẻ nhiều lần không nên thành nhiều phát hiện độc lập.

### Nhận báo cáo và Save

Application hiển thị bản đầy đủ. Telegram gửi bản ngắn và đường dẫn/nút hành động phù hợp. User mở nguồn hoặc Save bài. Bài được phát hiện tự động và bài người dùng chủ động Save phải được phân biệt trong dữ liệu và giao diện.

### Can thiệp khi gián đoạn

CAPTCHA, phiên hết hạn hoặc yêu cầu xác minh đưa đợt chạy sang trạng thái cần người dùng. User nhận thông báo, xử lý trong trình duyệt, rồi yêu cầu tiếp tục. Không giả định hệ thống có thể chạy tiếp nếu hạn chế truy cập vẫn còn.

## 6. Kiến trúc logic đề xuất

Đây là các ranh giới trách nhiệm, không yêu cầu mỗi phần phải là một microservice.

| Khối | Trách nhiệm | Dữ liệu vào/ra chính |
| --- | --- | --- |
| Application | Đọc báo cáo, quản lý chủ đề, Saved và cài đặt | Tương tác người dùng ↔ API ứng dụng |
| Backend và quyền truy cập | Điều phối nghiệp vụ, xác thực, bảo vệ secrets | Cấu hình, dữ liệu nghiên cứu, quyền thao tác |
| Scheduler và job runner | Lịch chạy, hàng đợi, điểm dừng, checkpoint, phục hồi | Cấu hình theo dõi → đợt chạy và tiến độ |
| X collector | Thu thập trong phiên được cấp quyền, phát hiện trạng thái bị chặn | Bài đăng, metadata nguồn, trạng thái truy cập |
| Research sources | Tìm và đọc nguồn paper/code được hỗ trợ | DOI, URL, abstract/toàn văn khi truy cập được |
| Research pipeline | Chuẩn hóa, loại trùng, gắn tag, nhóm ý tưởng, phân tích bằng AI | Nội dung nguồn → phân tích có dẫn nguồn |
| AI provider adapters | Cấu hình provider/model, xử lý lỗi, theo dõi usage | Tác vụ phân tích ↔ kết quả từ model |
| Data store | Lưu bài, phân tích, báo cáo, Saved và trạng thái | Dữ liệu có định danh và quyền sở hữu |
| Telegram adapter | Gửi báo cáo, thông báo, nhận hành động được xác thực | Báo cáo/sự kiện ↔ người dùng liên kết |

Luồng dữ liệu cơ bản: cấu hình theo dõi tạo job; collector tạo bản ghi nguồn; pipeline tạo phân tích; bộ tạo báo cáo chọn kết quả phù hợp; app và Telegram trình bày cùng bản báo cáo. Save là thao tác riêng trên bản ghi bài.

## 7. Các thực thể dữ liệu để phỏng vấn

Danh sách dưới đây là khởi điểm, chưa phải schema database cuối cùng.

| Thực thể | Nội dung cần quản lý |
| --- | --- |
| User/Workspace | Chủ sở hữu dữ liệu, quyền và phạm vi cá nhân hóa |
| Topic/Tag subscription | Chủ đề, từ đồng nghĩa, loại trừ, phiên bản và thời điểm hiệu lực |
| Source connection | Account X, nguồn paper, trạng thái và tham chiếu phiên/secrets |
| Collection run | Trigger, cấu hình áp dụng, tiến độ, checkpoint, kết quả và lỗi |
| Post/Source item | ID nguồn, tác giả, nội dung đã lấy, URL, ngày đăng, ngày phát hiện |
| Research work | DOI/arXiv ID nếu có, phiên bản paper, liên kết code/tài liệu |
| Analysis/Idea cluster | Tóm tắt, nhóm ý tưởng, bằng chứng, hạn chế, provider/model và phiên bản |
| Report/Report item | Kỳ báo cáo, người nhận, lựa chọn nội dung, trạng thái đầy đủ/một phần |
| Saved item | Người lưu, bài tham chiếu, ngày lưu, snapshot hay bản cập nhật cần chốt |
| Delivery/Telegram link | Quyền nhận tin, trạng thái gửi, chống gửi lặp và hành động người dùng |

Không lưu mật khẩu/API key ở frontend, tin nhắn hay log. Cách bảo vệ secrets và phiên X cần được xác định ở thiết kế triển khai.

## 8. Quy tắc nghiệp vụ cần làm rõ nhất

### Tag và thời gian

- “Từ lúc update tag” dựa vào ngày bài được đăng, ngày được hệ thống phát hiện, hay thời điểm phân phối báo cáo?
- Job đang chạy xử lý thế nào nếu tag đổi? Đề xuất trước đó là kiểm tra bộ tag mới trước khi phân phối; chưa chốt cách xử lý toàn bộ job.
- Bài phù hợp bất kỳ tag hay phải thỏa nhiều tag? Có chủ đề bị loại trừ, tag cha/con, nhập tự do không?
- Một tag mới không có nội dung trong For You cần tìm thêm ở đâu? Khi thiếu dữ liệu, không tự diễn giải thành “không có nghiên cứu mới”.

### Nội dung và độ tin cậy

- Một mục báo cáo là post, thread, paper hay cụm ý tưởng?
- Phân biệt mức độ phổ biến, mới với người dùng và tính mới khoa học; không dùng tương tác X làm bằng chứng khoa học.
- Tách tuyên bố của tác giả, nội dung có thể kiểm tra từ nguồn và suy luận của AI.
- Ghi rõ chỉ có post, abstract hoặc đã đọc toàn văn. Một nguồn chưa peer review vẫn cần nhãn phù hợp.
- Định nghĩa thế nào là “area mới”: nhãn ứng viên để đọc sâu hay kết luận đã được kiểm chứng?

### Saved và lịch sử

- Lưu bản chụp lúc Save hay liên kết tới nội dung luôn cập nhật?
- Xóa/bỏ lưu, tag cũ, bài nguồn bị sửa/xóa và nhu cầu xuất dữ liệu xử lý thế nào?
- Nếu Save từ Telegram được chọn, thao tác lặp phải không tạo bản ghi trùng và phải gắn đúng user.

### Telegram và vận hành

- Gửi cá nhân, nhóm hay cả hai; liên kết danh tính và quyền quản trị như thế nào?
- App đặt trên máy nhà được mở từ điện thoại bằng cách nào? Link app local không mặc nhiên truy cập được từ bên ngoài.
- Khi Telegram gửi thất bại, app vẫn giữ báo cáo; retry cần tránh gửi trùng.
- Máy tắt/lỡ lịch, AI lỗi, mạng mất, CAPTCHA, nguồn không truy cập được: quy định thử lại và báo cáo một phần.

## 9. Ràng buộc và các giới hạn đã biết

- Phiên đăng nhập/cơ chế cá nhân hóa X là hướng người dùng muốn thử, chưa được kiểm chứng bằng một đợt thu thập thực tế.
- Người dùng từng đề xuất hành vi giống con người. Đây không phải tiêu chí bảo đảm tránh phát hiện; không đưa các cơ chế né CAPTCHA, che giấu danh tính hoặc vượt giới hạn truy cập vào phạm vi sản phẩm.
- X có quy tắc hạn chế tự động hóa website. Việc user giải CAPTCHA không loại bỏ nguy cơ tài khoản bị hạn chế; cần điều kiện dừng rõ ràng.
- Một feed X không bảo đảm bao phủ khoa học đa ngành. Cần cơ chế nguồn bổ sung và báo cáo độ thiếu hụt dữ liệu.
- Khả năng có máy đủ mạnh không trả lời các câu hỏi về truy cập từ xa, số người dùng hoặc vận hành liên tục; chỉ hỏi những điểm đó khi ảnh hưởng kiến trúc.
- Có API key không bảo đảm mọi provider hỗ trợ cùng giao thức hoặc model. Khi triển khai, kiểm tra tài liệu chính thức thay vì mặc định mọi API tương thích.
- Nội dung X/paper là dữ liệu không đáng tin cậy đối với lệnh điều khiển: pipeline không thực thi chỉ dẫn nhúng trong tài liệu hoặc để chúng gọi công cụ hay lấy secrets.

## 10. Tiêu chí nghiệm thu đề xuất

1. Đến lịch đã cấu hình, hệ thống tự bắt đầu mà user không cần lướt X để kích hoạt.
2. Đợt chạy dừng ở giới hạn hoặc khi cần xác minh; trạng thái và tiến độ được lưu.
3. Cập nhật tag áp dụng đúng mốc hiệu lực đã thống nhất; kiểm tra cả job đang chạy và báo cáo đang chờ gửi.
4. Bài trùng không thành nhiều phát hiện; nhiều nguồn hỗ trợ cùng ý tưởng vẫn giữ được liên kết nguồn.
5. Báo cáo có dẫn nguồn, chỉ rõ mức độ tài liệu đã đọc và tách suy luận AI khỏi bằng chứng.
6. Save trong app tồn tại sau khi khởi động lại; nếu chọn Save Telegram thì hai kênh cùng một trạng thái.
7. Retry AI/Telegram hoặc khởi động lại job không làm mất dữ liệu đã hoàn thành và không chủ động tạo báo cáo trùng.
8. Thiếu nguồn, kết quả rỗng và đợt thất bại có trạng thái khác nhau, người dùng nhận ra dữ liệu có mới hay không.
9. Nội dung bên ngoài không thể yêu cầu hệ thống tiết lộ secrets hoặc thay đổi quyền gửi Telegram.

Các chỉ số định lượng cần phỏng vấn: tỷ lệ bài hữu ích, số ý tưởng đáng Save mỗi tuần, thời gian đọc tiết kiệm được, độ trễ báo cáo và mức can thiệp xác minh chấp nhận được.

## 11. Thứ tự phỏng vấn tiếp theo

1. Phạm vi người dùng và quyền sở hữu account X.
2. Truy cập app từ đâu và mô hình chạy tự động.
3. Hình dạng báo cáo và tiêu chí hữu ích.
4. Tag, thời điểm hiệu lực, nguồn và chiến lược khám phá.
5. Save, Telegram và các hành động hai chiều.
6. Job lifecycle, AI routing, dữ liệu và bảo mật.
7. Phạm vi MVP, acceptance criteria và lựa chọn stack sau khi đủ ràng buộc.

## 12. Tài liệu tham chiếu đã dùng trong trao đổi

Các trang dưới đây đã được tra cứu trong phiên ngày 05/09/2026. Chính sách, giá và khả năng API cần kiểm tra lại khi thiết kế tích hợp; overview không cam kết chúng giữ nguyên.

- [X — For You timeline](https://help.x.com/en/using-x/x-timeline)
- [X — Recommendations](https://help.x.com/en/rules-and-policies/recommendations)
- [X — Automation rules](https://help.x.com/en/rules-and-policies/x-automation)
- [X — Locked and limited accounts](https://help.x.com/en/managing-your-account/locked-and-limited-accounts)
- [X API — Pricing](https://docs.x.com/x-api/getting-started/pricing)
- [OpenAlex — Pricing](https://help.openalex.org/access/pricing/)
- [arXiv — API basics](https://info.arxiv.org/help/api/basics.html)

## 13. Cách sử dụng overview

Đưa file này cùng `master-interview-prompt.md` cho AI thực hiện phỏng vấn. Xem các mục C là bối cảnh đã xác nhận; dùng mục P và câu hỏi mở để dẫn dắt phần còn lại. Nếu người dùng đưa quyết định mới mâu thuẫn với tài liệu, ghi nhận thay đổi và cập nhật quyết định; không tự coi một đề xuất cũ là yêu cầu bắt buộc.
