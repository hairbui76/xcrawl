---
contract_id: CT-precode-owner-decision-request
version: 0.1.0
status: draft
owner_role: requirements owner (PC00)
document_type: OWNER_DECISION_REQUEST
grants_authority: false
source_refs: [SRC-SPEC v0.2 (sha256 d35e1f2d…), SRC-PLAN v0.1 (sha256 f65bb046…)]
requirement_refs: [precode/requirements.csv]
decision_refs: [B01..B17, AMD-B01..AMD-B17, ADR-0001..ADR-0010]
invariant_refs: [I01..I15]
producers: [PC00]
consumers: [Owner, PC01..PC10]
dependencies: [precode/baseline.json, precode/decision-register.md, precode/adr/]
scope: >
  Bản yêu cầu quyết định gửi Owner. Gồm 24 mục: B01-B17, lựa chọn stack, timezone, bộ giá trị
  mặc định cho các câu hỏi còn mở, phạm vi loại trừ của data.purge_all (ruling R-04), tham số báo cáo
  và mật độ của PC04, tham số vận hành và bảo mật của PC08, và hai thay đổi kỹ thuật của đợt FIX3. Mỗi mục nêu câu hỏi, lý do trọng yếu, nguồn, các phương án và đánh đổi, khuyến nghị,
  phạm vi bị chặn, phạm vi vẫn chạy được, và quyền cần được cấp.
verification: E0 - kiểm bằng script rằng mỗi B01..B17 có đúng một mục (EV-PC00-04).
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION_REQUEST — Research Radar Pre-code

> # ✅ ANSWERED 2026-09-07 — xem `precode/owner-decisions.md`
>
> Owner đã trả lời toàn bộ bản yêu cầu này bằng biên bản **`OD-20260907-01`** (authority
> `AUTH-OWNER-20260907-02`, evidence `session_017QmDJtMqD9o1z79waqSB9W`). B01–B17 nay `RATIFIED`;
> các amendment và ADR tương ứng `ACCEPTED`. **Một mục duy nhất chưa được trả lời:** `REQ-OQ03`
> (provider và model) vẫn `OWNER_DECISION_REQUIRED` và vẫn chặn M3.
>
> **Vòng hai (2026-09-07).** Biên bản `OD-20260907-02` (`precode/owner-decisions-02.md`, authority
> `AUTH-OWNER-20260907-03`, evidence `session_0156UBBHDSeC9soECzSVUb3U`) trả lời nốt dòng `ADR-0011` đang
> treo trong phiếu ở cuối file — **accept** — và mở lối vào Giai đoạn 0 và Giai đoạn 1 của
> `docs/master-plan.md`. Tại thời điểm đó `REQ-OQ03` vẫn là mục duy nhất chưa được trả lời.
>
> **Vòng ba (2026-09-07).** Biên bản `OD-20260907-03` (`precode/owner-decisions-03.md`, authority
> `AUTH-OWNER-20260907-04`, cùng phiên evidence) phê chuẩn `AMD-ENT-owner-01` và `PROV-PC00-08`, và mở lối
> vào Giai đoạn 2. Vòng này **mở thêm hai câu hỏi** thay vì đóng bớt: sau nó còn **ba** mục chưa được trả
> lời — `REQ-OQ03`, các mục cổng probe `contracts/ops/collector-probe.md` §6 mục 2–4, và bốn dữ kiện
> `REQ-A6` (hoặc quyền mạng để lấy chúng).
>
> **Vòng năm (2026-09-08).** Biên bản `OD-20260908-05` (`precode/owner-decisions-05.md`, authority
> `AUTH-OWNER-20260908-06`) **ủy quyền nghiên cứu** `REQ-OQ03` — không giải nó — và cấp một quyền mạng hẹp
> chỉ-đọc-tài-liệu `core.telegram.org` cho `CR-PC07-04`. Lựa chọn model cụ thể là một biên bản **riêng**,
> `OD-20260908-06`. Phiếu ở cuối file phản ánh cả hai vòng.
>
> **Vòng bốn (2026-09-07).** Biên bản `OD-20260907-04` (`precode/owner-decisions-04.md`, authority
> `AUTH-OWNER-20260907-05`) đóng **hai** trong ba mục đó: cổng probe §6 mục 2–4 được chấp nhận cả ba, và một
> quyền mạng **một lần, hẹp theo tên miền, chỉ đọc tài liệu** được cấp cho việc đi tìm bốn dữ kiện `REQ-A6`.
> **`REQ-A6` vẫn `KC`** — quyền đi lấy không phải là dữ kiện đã lấy. Sau vòng bốn còn **một** mục chưa được
> trả lời: `REQ-OQ03`. Câu "một mục duy nhất" ở đoạn trên **chỉ đúng cho thời điểm nó được viết**.
>
> File này được **giữ nguyên** làm bản ghi câu hỏi đã đặt ra; phiếu trả lời ở cuối file đã được điền.
> Nội dung các mục bên dưới **không** được viết lại — chúng phản ánh tình trạng lúc hỏi, không phải
> tình trạng hiện tại. Trạng thái hiện tại sống ở `precode/owner-decisions.md` và
> `precode/decision-register.md`.

> **Đây là một REQUEST, không phải một grant.** Tài liệu này không tạo authority, không tạo write lease
> và không hàm ý chấp nhận. Một quyết định của Owner chỉ có hiệu lực khi được ghi thành authority hoặc
> amendment riêng, có evidence ref thật. Chừng nào chưa có, B01–B17 vẫn là `OPEN` trong
> `agent_profile/registry.json` và các phương án dưới đây vẫn là `PROVISIONAL`.

## Cách đọc

Mỗi mục có tám phần: **Câu hỏi · Lý do trọng yếu · Nguồn · Phương án và đánh đổi · Khuyến nghị · Phạm vi bị chặn nếu chưa trả lời · Phạm vi vẫn chạy được · Quyền cần được cấp**.

Ba mức khẩn cấp:

| Mức | Nghĩa | Các mục |
| --- | --- | --- |
| **Chặn ngay** | Không trả lời thì một mốc triển khai không bắt đầu được | B12 (D09), Stack |
| **Chặn hợp đồng** | Không trả lời thì gói PC tương ứng không đạt `CONTRACT_READY` | B01, B02, B03, B04, B05, B06, B07, B08, B09, B10, B11, B13, B14, B15, B16, B17, Timezone |
| **Có mặc định tạm** | Đã có giá trị PROVISIONAL đủ để đi tiếp; xác nhận sau cũng được | Bộ giá trị mặc định (OQ) |
| **Không có mặc định** | Không có phương án nào an toàn để chọn tạm; phạm vi liên quan bị chặn tường minh | REQ-OQ03 (provider/model), phạm vi loại trừ của `data.purge_all` |
| **Đã có số tạm, cần xác nhận** | Gói sau đã phải chọn một con số để hợp đồng không rỗng; số đó chưa được đo trên hệ thật | Tham số báo cáo và mật độ (PC04), Vận hành và bảo mật (PC08) |

Không mục nào trong tài liệu này đòi Owner phải trả lời ngay lập tức. Nếu Owner chỉ trả lời được một phần, các gói không phụ thuộc mục còn lại vẫn tiếp tục được — cột "Phạm vi vẫn chạy được" nói rõ phần nào.

---

## B01 — Bộ tag được đóng băng lúc nào?

- **Câu hỏi.** Nội dung một báo cáo được quyết định bởi bộ tag tại **thời điểm publish báo cáo**, hay tại **thời điểm gửi tin Telegram**?
- **Lý do trọng yếu.** Hàng `C03/D-tag` nêu cả hai mốc trong một câu. Nếu chọn "lúc gửi" thì một lần retry Telegram sau khi bạn vừa bỏ một tag sẽ phải gửi nội dung khác với nội dung bạn đang đọc trong app — hoặc phải dựng lại báo cáo, mâu thuẫn với "không dựng lại, chỉ gửi lại" của §9.2.
- **Nguồn.** SRC-SPEC §3.4 (`C03/D-tag`, D23, D24), §5.5, §8.2 hàng 1–2, §9.2, AC-05. SRC-PLAN §3 hàng B01, §9.2.
- **Phương án và đánh đổi.**
  - **(a) Freeze tại publish.** Nội dung bất biến sau publish; app và Telegram luôn khớp. Đổi lại: tag thêm sau lúc publish không kịp vào kỳ đó, dù bạn thêm trước khi nhận tin.
  - **(b) Freeze tại lúc gửi.** Đúng nguyên văn nửa đầu của hàng nguồn. Đổi lại: cần thiết kế report revision, xử lý "đã gửi một phần", và chấp nhận app hiển thị khác Telegram.
- **Khuyến nghị.** (a). Xem ADR-0004 và AMD-B01.
- **Phạm vi bị chặn nếu chưa trả lời.** PC04 (`contracts/reporting/*`, `report.schema.json`) và PC07 (delivery) không đạt `CONTRACT_READY`; gate G3.
- **Phạm vi vẫn chạy được.** PC01, PC02, PC03, PC05, PC06 và phần lớn PC08.
- **Quyền cần được cấp.** Phê chuẩn AMD-B01 (sửa câu chữ của một quyết định XN).

## B02 — Mô hình trạng thái của một đợt chạy

- **Câu hỏi.** Chấp nhận thay enum phẳng (`queued → collecting → … → done`, nhánh `stopped_limit`…) bằng bốn trường `phase / status / outcome / stop_reason`, và tách delivery ra khỏi vòng đời run?
- **Lý do trọng yếu.** §5.2 vẽ `delivered` **bên trong** run trong khi §9.1 nói hai vòng đời độc lập. Với enum phẳng, không biểu diễn được "đợt dừng sớm nhưng vẫn có báo cáo một phần" — chính là tình huống §8.3 bắt phải phân biệt.
- **Nguồn.** SRC-SPEC §5.2, §8.3, §9.1, AC-03, AC-15. SRC-PLAN §8.1.
- **Phương án và đánh đổi.**
  - **(a) Bốn trường + delivery tách rời.** Ba trạng thái của §8.3 hiển thị đúng; thêm được `blocked` và `empty`. Đổi lại: AC-03 phải viết lại, read model của UI phức tạp hơn.
  - **(b) Giữ enum phẳng.** Không phải sửa tài liệu. Đổi lại: `delivered` vẫn trong run, vi phạm nguyên tắc độc lập của chính §9.1; PC03 không đóng được bảng transition.
- **Khuyến nghị.** (a). Bảng ánh xạ enum cũ sang mới nằm trong AMD-B02, nên dữ liệu và tài liệu cũ vẫn đọc được. Xem ADR-0002.
- **Phạm vi bị chặn nếu chưa trả lời.** PC03 (toàn bộ `contracts/state/*`); kéo theo PC07; gate G2.
- **Phạm vi vẫn chạy được.** PC01, PC02, và phần identity của PC05.
- **Quyền cần được cấp.** Phê chuẩn AMD-B02, bao gồm sửa câu chữ AC-03.

## B03 — Bảo đảm "không gửi hai lần" của Telegram

- **Câu hỏi.** Chấp nhận thay bảo đảm "không có tin nào bị gửi hai lần" bằng "không có lần gửi lặp **tự động**; trường hợp không chắc chắn hiện là `unknown` để bạn quyết định"?
- **Lý do trọng yếu.** Telegram Bot API `sendMessage` không nhận idempotency key từ phía chúng ta. Khi request đã đi mà phản hồi mất, hệ thống **không thể biết** tin đã tới hay chưa. Giữ nguyên chữ AC-14 nghĩa là hứa một điều không kiểm chứng được.
- **Nguồn.** SRC-SPEC §9.1, §9.3, AC-14. SRC-PLAN §3.1 (Telegram Bot API), §8.3, §10.
- **Phương án và đánh đổi.**
  - **(a) Thêm `delivery.unknown`, không retry tự động từ đó.** Không bao giờ gửi trùng tự động. Đổi lại: đôi khi bạn phải tự bấm gửi lại, và chấp nhận rủi ro trùng ở lần bấm đó.
  - **(b) Retry tự động luôn.** Không mất tin. Đổi lại: có lúc nhận digest hai lần.
  - **(c) Không retry bao giờ.** Không bao giờ trùng. Đổi lại: mất tin khi lỗi mạng tạm thời.
- **Khuyến nghị.** (a). Xem ADR-0003 và AMD-B03.
- **Phạm vi bị chặn nếu chưa trả lời.** PC07 phần delivery; gate G3.
- **Phạm vi vẫn chạy được.** Toàn bộ phần app của PC07 (Save, màn hình), và PC01–PC06.
- **Quyền cần được cấp.** Phê chuẩn AMD-B03 (sửa câu chữ AC-14).

## B04 — Coverage tiến vào lúc nào; kỳ rỗng để lại gì

- **Câu hỏi.** Kỳ rỗng có ghi một hàng coverage (dù không gửi digest) không? Và sổ pending/backfill có độc lập với con trỏ kỳ không?
- **Lý do trọng yếu.** D27 yêu cầu kỳ nối liền không hở; D57 cấm gửi báo cáo rỗng. Nếu kỳ rỗng không để lại dấu vết nào thì `coverage_from` của kỳ sau lấy từ đâu — sẽ có lỗ hổng hoặc chồng lấn.
- **Nguồn.** SRC-SPEC §3.5 (D27, D28, D57), §8.2 hàng 4 và 9, §10.4, AC-08. SRC-PLAN §3 hàng B04, §9.2.
- **Phương án và đánh đổi.**
  - **(a) Sổ coverage authoritative riêng; kỳ rỗng vẫn ghi coverage; pending và backfill là hai sổ riêng.** Chuỗi kỳ luôn liền mạch. Đổi lại: thêm ba sổ so với chỉ có bảng `report`.
  - **(b) Suy coverage từ danh sách report hiển thị.** Ít bảng hơn. Đổi lại: mỗi kỳ rỗng là một lỗ hổng; D27 không giữ được.
- **Khuyến nghị.** (a). Xem AMD-B04 và ADR-0004 điểm 5–6.
- **Phạm vi bị chặn nếu chưa trả lời.** PC04; gate G3.
- **Phạm vi vẫn chạy được.** PC01, PC02, PC03, PC05, PC06.
- **Quyền cần được cấp.** Phê chuẩn AMD-B04 (bổ sung hành vi cho D57).

## B05 — Cam kết khi tiếp tục một đợt bị đứt

- **Câu hỏi.** Cam kết của hệ thống là "không bao giờ đọc lại trang đã đọc", hay "không bao giờ **ingest trùng** một bài đã có"?
- **Lý do trọng yếu.** Con trỏ của feed X là con trỏ động và có thể mất hiệu lực. Hứa "không đọc lại" là hứa một điều phụ thuộc hành vi của X, không kiểm chứng được. "Không ingest trùng" kiểm chứng được bằng số hàng trong DB.
- **Nguồn.** SRC-SPEC §9.2, AC-04, §5.4. SRC-PLAN §3 hàng B05, §8.1.
- **Phương án và đánh đổi.**
  - **(a) Cam kết không ingest trùng theo `x_post_id`; cho phép đọc lại theo recovery policy.** Kiểm chứng được; resume luôn an toàn. Đổi lại: đôi khi tải lại vài trang, tốn thêm thời gian và tăng nhẹ khả năng bị X để ý.
  - **(b) Giữ nguyên "không lấy lại bài đã có".** Đúng chữ AC-04. Đổi lại: phải chứng minh cursor của X ổn định — điều không kiểm chứng được trước; probe A1 mất tiêu chí pass.
- **Khuyến nghị.** (a). Xem AMD-B05.
- **Phạm vi bị chặn nếu chưa trả lời.** PC03 và PC05; gate G2.
- **Phạm vi vẫn chạy được.** PC02, PC04, PC06, PC07.
- **Quyền cần được cấp.** Phê chuẩn AMD-B05 (sửa câu chữ AC-04).

## B06 — Cách nhận ra hai bản ghi là cùng một công trình

- **Câu hỏi.** Chấp nhận thêm bảng alias, phiên bản của `work`, và một kiểu `target` chung cho cả work và post (thay cho hai cột nullable)?
- **Lý do trọng yếu.** Hai ràng buộc UNIQUE chặn được việc **ghi** trùng, nhưng không giải được trường hợp hai hàng đã tồn tại rồi mới biết là cùng công trình. Và mục "chỉ có post" (D33) hiện chưa có khóa duy nhất đúng cho Saved — AC-13 sẽ không có oracle.
- **Nguồn.** SRC-SPEC §3.2 (D33), §3.5 (D17), §7.1, §9.3, AC-07, AC-13. SRC-PLAN §3 hàng B06, §9.1.
- **Phương án và đánh đổi.**
  - **(a) Alias + version + target tagged union.** Merge có audit trail, post-only có khóa đúng. Đổi lại: thêm bảng, migration phức tạp hơn.
  - **(b) Giữ nguyên §7.1.** Không thêm gì. Đổi lại: AC-07 và AC-13 không có oracle ở trường hợp thực tế.
- **Khuyến nghị.** (a). Xem ADR-0009. Không có amendment: đây là bổ sung định nghĩa còn thiếu.
- **Phạm vi bị chặn nếu chưa trả lời.** PC02; gate G2, kéo theo PC04.
- **Phạm vi vẫn chạy được.** PC01, PC03 phần lease/scheduler, PC08.
- **Quyền cần được cấp.** Chấp nhận mô hình dữ liệu bổ sung (không sửa câu chữ đặc tả).

## B07 — "Phân tích một lần" nghĩa là một lần theo chiều nào

- **Câu hỏi.** "Một lần cho mỗi công trình" (D25) được hiểu là **một kết quả hợp lệ cho mỗi analysis key và mỗi generation**, để D26 (phân tích lại) và việc thử lại sau lỗi vẫn hợp lệ?
- **Lý do trọng yếu.** Đọc nghĩa đen, D25 loại trừ chính D26 nằm ngay bên dưới nó, và loại trừ cả cơ chế "thử lại một lần" của §9.3.
- **Nguồn.** SRC-SPEC §3.5 (D25, D26), §7.1, §9.2, §9.3, §10.4, AC-06. SRC-PLAN §3 hàng B07, §9.3.
- **Phương án và đánh đổi.**
  - **(a) Analysis key năm thành phần; reanalysis tạo generation mới.** Chi phí AI vẫn kiểm soát được; có đường reanalysis hợp lệ. Đổi lại: đổi phiên bản prompt sẽ sinh key mới cho toàn kho, phải cân nhắc trước mỗi lần sửa prompt.
  - **(b) Một hàng cho một `work_id`.** Đơn giản nhất. Đổi lại: D26 phải bị bỏ.
- **Khuyến nghị.** (a). Xem ADR-0008 và AMD-B07.
- **Phạm vi bị chặn nếu chưa trả lời.** PC02 (bảng `analysis`) và PC06; gate G2/G3.
- **Phạm vi vẫn chạy được.** PC01, PC03, PC05, PC07.
- **Quyền cần được cấp.** Phê chuẩn AMD-B07 (làm rõ câu chữ D25).

## B08 — Múi giờ nào là múi giờ của hệ thống

- **Câu hỏi.** Xác nhận lưu **một** IANA timezone trong Settings thay cho "timezone của máy chạy app", và cho biết múi giờ đó là gì.
- **Lý do trọng yếu.** Có ba đồng hồ: browser, server, máy cá nhân. Lịch "08:00" phải có nghĩa xác định, nếu không thì chạy bù và ranh giới ngày của coverage đều không tái lập được.
- **Nguồn.** SRC-SPEC §3.3 (D13, D15), §3.6 (D56), §8.2 hàng 8, §13.1 hàng 6, AC-02. SRC-PLAN §3 hàng B08, §5.1.
- **Phương án và đánh đổi.**
  - **(a) Một IANA timezone trong Settings; timestamp lưu UTC mili giây; tie-break bằng ingest sequence.** Xác định và tái lập được. Đổi lại: lịch không tự đổi khi bạn đi múi giờ khác.
  - **(b) Theo timezone của browser mỗi lần.** Hiển thị luôn đúng nơi bạn đứng. Đổi lại: lịch chạy ở server trôi theo nơi mở app.
- **Khuyến nghị.** (a), với giá trị `Asia/Ho_Chi_Minh` **cần bạn xác nhận**. Xem ADR-0007 và AMD-B08.
- **Phạm vi bị chặn nếu chưa trả lời.** Fixture lịch của PC03 và ranh giới coverage của PC04; gate G2.
- **Phạm vi vẫn chạy được.** PC01, PC02, PC05, PC06, PC07 (trừ định dạng hiển thị giờ).
- **Quyền cần được cấp.** Phê chuẩn AMD-B08 **và** xác nhận giá trị timezone.

## B09 — Bot có được phép trả lời chat chưa liên kết không

- **Câu hỏi.** Chấp nhận một ngoại lệ hẹp: thông điệp từ chat chưa liên kết **khớp đúng định dạng mã liên kết** được kiểm; mọi thứ khác vẫn bị bỏ im lặng?
- **Lý do trọng yếu.** §11.3 nói bỏ im lặng mọi tin từ chat chưa liên kết, nhưng §5.1 bước 4 lại yêu cầu bạn **gửi mã cho bot** — tức bot phải xử lý một tin từ chat chưa liên kết. Nguyên văn hiện tại làm luồng thiết lập lần đầu không chạy được.
- **Nguồn.** SRC-SPEC §5.1 bước 4, §11.2, §11.3, AC-18. SRC-PLAN §3 hàng B09.
- **Phương án và đánh đổi.**
  - **(a) Ngoại lệ hẹp cho chuỗi khớp định dạng mã.** Luồng thiết lập chạy được; bề mặt mở rất nhỏ. Đổi lại: bot vẫn phải xử lý một loại tin từ chat lạ.
  - **(b) Không ngoại lệ; nhập chat ID bằng tay trong app.** Bot không bao giờ đụng tin từ chat lạ. Đổi lại: bạn phải tự tìm chat ID của mình, §5.1 phải viết lại.
- **Khuyến nghị.** (a). Mã sai, hết hạn hoặc đã dùng cũng bị bỏ im lặng, không trả lời lỗi. Xem AMD-B09.
- **Phạm vi bị chặn nếu chưa trả lời.** PC07 phần linking; gate G3.
- **Phạm vi vẫn chạy được.** Mọi gói khác.
- **Quyền cần được cấp.** Phê chuẩn AMD-B09 (thêm ngoại lệ vào §11.3).

## B10 — Tiếp tục một run đang chờ bạn xử lý bằng cách nào

- **Câu hỏi.** Resume chỉ bằng nút trong app, `status` là lệnh chỉ đọc, `run-now` không vượt được `needs_user`, và Telegram giữ đúng **3 lệnh**?
- **Lý do trọng yếu.** §5.4 bước 4 gợi ý rằng gửi lệnh `status` hoặc `run-now` cũng tiếp tục được run, nhưng §5.4 bước 5 và §9 lại nói run không tự tiếp tục khi hạn chế còn. Ngoài ra §11.3 giới hạn đúng 3 lệnh trong khi D37 yêu cầu thêm lệnh hủy liên kết — xem F-PC00-01.
- **Nguồn.** SRC-SPEC §3.6 (D36, D37), §5.4, §11.3, AC-04. SRC-PLAN §3 hàng B10.
- **Phương án và đánh đổi.**
  - **(a) Resume trong app; `status` read-only; hủy liên kết cũng trong app; Telegram đúng 3 lệnh.** Không có đường tắt vô tình resume một run đang bị chặn. Đổi lại: khi đang ở ngoài, bạn phải mở app để resume và để hủy liên kết.
  - **(b) Thêm lệnh Telegram thứ tư (unlink) và cho phép resume qua Telegram.** Tiện khi ở ngoài. Đổi lại: §11.3 phải sửa; bề mặt lệnh rộng hơn; rủi ro resume khi CAPTCHA vẫn còn.
- **Khuyến nghị.** (a). Xem AMD-B10.
- **Phạm vi bị chặn nếu chưa trả lời.** PC07 phần lệnh; PC03 phần resume; gate G3.
- **Phạm vi vẫn chạy được.** PC01, PC02, PC04, PC05, PC06.
- **Quyền cần được cấp.** Phê chuẩn AMD-B10 **và** quyết định về lệnh hủy liên kết (F-PC00-01).

## B11 — Backup bằng cách nào

- **Câu hỏi.** Chấp nhận thay "copy file SQLite" bằng snapshot nhất quán (Online Backup API hoặc `VACUUM INTO`) kèm manifest và một quy trình restore có khóa side effect?
- **Lý do trọng yếu.** WAL là một phần trạng thái bền của DB. Copy riêng file DB khi đang ghi có thể mất transaction đã commit — nghĩa là bản backup trông có vẻ ổn nhưng thiếu dữ liệu, và bạn chỉ phát hiện lúc cần khôi phục.
- **Nguồn.** SRC-SPEC §3.6 (D58), §7.3, §13 (M8), AC-12. SRC-PLAN §3.1 (SQLite WAL/Backup API), §10, §11 (PC08).
- **Phương án và đánh đổi.**
  - **(a) Snapshot nhất quán + manifest + restore drill có khóa side effect.** Khôi phục kiểm chứng được; không tự gửi lại outbox cũ. Đổi lại: backup chậm hơn `cp`, cần dung lượng tạm; restore là một quy trình chứ không phải một lệnh.
  - **(b) Giữ `cp` như D58.** Đơn giản. Đổi lại: không dùng làm bằng chứng khôi phục được; PC08 không đạt `CONTRACT_READY` cho phần này.
- **Khuyến nghị.** (a). Lưu ý: profile Chrome và token trên máy cá nhân **không** nằm trong backup server và phải thiết lập lại bằng tay. Xem ADR-0005 và AMD-B11.
- **Phạm vi bị chặn nếu chưa trả lời.** PC08 phần backup/restore; gate G3.
- **Phạm vi vẫn chạy được.** Mọi gói khác, kể cả phần secrets và Internet boundary của PC08.
- **Quyền cần được cấp.** Phê chuẩn AMD-B11 (sửa câu chữ D58) và chốt RPO/RTO mong muốn.

## B12 — Topology và Chrome profile · **CHẶN M0**

- **Câu hỏi.** Hai phần: (1) Xác nhận dùng **Chrome profile riêng của dự án** thay cho profile mặc định (đây chính là REQ-OQ01, chặn M0). (2) Chấp nhận xóa cạnh "collector đưa dữ liệu thẳng cho analysis worker" trong sơ đồ §6.2, để analysis worker nhận task từ server **sau ingest commit**?
- **Lý do trọng yếu.** Bốn quyết định bố trí module (D08, D09, D42, D50) đều còn **ĐX**, nên không lập được bảng ranh giới quyền với default deny — mà bảng đó là đầu vào của mọi gói còn lại. Riêng cạnh `COL → AW` cho phép phân tích chạy trên dữ liệu chưa commit, mâu thuẫn với chính D08.
- **Nguồn.** SRC-SPEC §3.1 (D06, D08, D42, D50), §3.2 (D09), §6.1, §6.2, §6.4, §11.2, §13.1 hàng 1. SRC-PLAN §3 hàng B12, §6.
- **Phương án và đánh đổi.**
  - **(a) Profile riêng + collector chỉ nói chuyện với backend API + analysis nhận task sau commit.** Phiên cá nhân tách khỏi phiên tự động; mọi input phân tích đều đã commit. Đổi lại: đăng nhập X thêm một lần; thêm một vòng mạng.
  - **(b) Dùng profile Chrome mặc định.** Không phải đăng nhập lại. Đổi lại: trộn phiên cá nhân với phiên tự động; rủi ro tài khoản cao hơn; trái tinh thần §11.2.
- **Khuyến nghị.** (a). Xem ADR-0001 và AMD-B12.
- **Phạm vi bị chặn nếu chưa trả lời.** **M0 không bắt đầu được.** PC01 không đóng được `modules.yaml`/`capabilities.yaml`; gate G1, kéo theo PC05 và PC06.
- **Phạm vi vẫn chạy được.** PC00 (đã xong), phần identity của PC02, phần state machine chung của PC03.
- **Quyền cần được cấp.** (1) Xác nhận D09 — quyết định sản phẩm. (2) Phê chuẩn AMD-B12.

## B13 — Worker được cầm những secret nào; CLI được làm gì

- **Câu hỏi.** Chấp nhận: worker chỉ nhận credential của đúng provider cho task được giao (ngắn hạn); adapter CLI/ACP chạy với tool/file/network bị tắt ngoài inference; và **adapter không kiểm chứng được mức cô lập thì giữ trạng thái disabled**?
- **Lý do trọng yếu.** Nội dung X và paper là dữ liệu không tin cậy và nó đi thẳng vào prompt. CLI của các nhà cung cấp thường có khả năng đọc file và gọi tool. Nếu không khóa, một post được soạn khéo có thể khiến CLI làm việc ngoài ý muốn — đúng tình huống AC-17 mô tả.
- **Nguồn.** SRC-SPEC §3.7 (D41, D43, D51), §10.2, §11.2, §11.4, §13.2, AC-16, AC-17, A5. SRC-PLAN §3 hàng B13, §6, §11 (PC06).
- **Phương án và đánh đổi.**
  - **(a) Secret theo task + khóa tool + mặc định disabled khi chưa kiểm được.** Bán kính thiệt hại nhỏ; AC-17 có oracle thật. Đổi lại: **nếu không adapter CLI nào qua được kiểm cô lập thì AC-16 (chạy không cần API key) phải ghi `BLOCKED`, không phải `FAIL`** — tức lời hứa D51 tạm thời không chứng minh được.
  - **(b) Bật mọi adapter, tin cấu hình mặc định của nhà cung cấp.** Nhiều lựa chọn provider ngay. Đổi lại: không có bằng chứng tool bị khóa; trái §11.4.
- **Khuyến nghị.** (a). Xem ADR-0010.
- **Phạm vi bị chặn nếu chưa trả lời.** PC06 (`providers.yaml`), PC01 (`capabilities.yaml`), PC08 (`secrets.md`); gate G1/G3.
- **Phạm vi vẫn chạy được.** PC02, PC03, PC04, PC05, PC07.
- **Quyền cần được cấp.** Chấp nhận chính sách cô lập, **và** chấp nhận rằng một họ provider có thể tạm thời không bật được.

## B14 — "Hướng đang nổi" được tính thế nào và khi nào thì không đủ dữ liệu

- **Câu hỏi.** Chấp nhận rằng khi dữ liệu chưa đủ, khối "hướng đang nổi" trả về `insufficient_evidence` và **không** hiển thị hướng nào?
- **Lý do trọng yếu.** D53 đưa khối này vào MVP nhưng chưa có thuật toán, cửa sổ so sánh, ngưỡng hay cỡ mẫu tối thiểu; A4 chưa được kiểm chứng. Nếu không có trạng thái "chưa đủ bằng chứng" thì hệ thống sẽ buộc phải gọi nhiễu là hướng nổi — đúng thứ tiêu chí "tỷ lệ nhiễu" của §1.4 muốn tránh.
- **Nguồn.** SRC-SPEC §1.4, §3.5 (D52, D53, D54), §10.1, §10.3, A4. SRC-PLAN §3 hàng B14, §11 (PC04, PC09).
- **Phương án và đánh đổi.**
  - **(a) Định nghĩa phép đo đầy đủ + trạng thái `insufficient_evidence`.** Không bao giờ dán nhãn sai. Đổi lại: vài kỳ đầu khối này sẽ trống, và điều đó có thể gây cảm giác hệ thống chưa làm gì.
  - **(b) Luôn hiển thị top-N hướng bất kể cỡ mẫu.** Khối luôn có nội dung. Đổi lại: nhiễu cao ở giai đoạn đầu; A4 không đánh giá được.
- **Khuyến nghị.** (a). Mọi tham số (cửa sổ, ngưỡng, cỡ mẫu) là PROVISIONAL cho tới khi có 3–4 kỳ dữ liệu thật.
- **Phạm vi bị chặn nếu chưa trả lời.** Phần selection của PC04 và rubric đánh giá của PC09; gate G3/G4.
- **Phạm vi vẫn chạy được.** Toàn bộ phần coverage/tag của PC04 và mọi gói khác.
- **Quyền cần được cấp.** Chấp nhận trạng thái `insufficient_evidence` và chấp nhận rằng D53 hiện vẫn là **ĐX** trong một mục P0.

## B15 — Chỉ số "0 trường hợp trùng" áp cho phạm vi nào

- **Câu hỏi.** Chấp nhận đọc lại chỉ số thành "0 trường hợp trùng **trong phạm vi canonical identity đã biết**", kèm một số đếm riêng cho các trường hợp `identity_conflict` đang chờ?
- **Lý do trọng yếu.** Chỉ số hiện ở trạng thái "Đã xác nhận" và là một trong bốn tiêu chí thành công. Nhưng metadata có thể thiếu hoặc mâu thuẫn, nên một con số tuyệt đối trên một tập không xác định thì không đo được và không kiểm toán được.
- **Nguồn.** SRC-SPEC §1.4, §3.5 (D17, D29), §9.3, AC-07, AC-09. SRC-PLAN §3 hàng B15, §7.
- **Phương án và đánh đổi.**
  - **(a) Thu hẹp phạm vi + đếm conflict riêng.** Đo được, và phần chưa giải quyết hiện ra thay vì bị giấu. Đổi lại: chỉ số không còn là một con số duy nhất.
  - **(b) Giữ tuyệt đối.** Nghe mạnh hơn. Đổi lại: không lập được traceability; PC09 không đóng được.
- **Khuyến nghị.** (a). Xem ADR-0009 và AMD-B15.
- **Phạm vi bị chặn nếu chưa trả lời.** PC02 phần invariant và PC09 phần traceability; gate G2/G4.
- **Phạm vi vẫn chạy được.** PC01, PC03, PC05, PC06, PC07, PC08.
- **Quyền cần được cấp.** Phê chuẩn AMD-B15 (sửa một chỉ số ở trạng thái Đã xác nhận).

## B16 — Phân biệt tác giả nói gì với AI suy luận gì

- **Câu hỏi.** Chấp nhận tách đầu ra phân tích thành ba loại phát biểu (`author_claim`, `source_verified`, `ai_inference`) và ghi `comparator: unknown` khi không có nguồn so sánh — thay cho cách AC-11 gộp mọi phát biểu tính mới thành "suy luận"?
- **Lý do trọng yếu.** D20 yêu cầu "điểm khác với cái đã có" cho mọi mục, kể cả mục chỉ có một post và không có gì để so sánh. Nếu không có chỗ ghi "không có comparator", AI sẽ có động cơ bịa một baseline.
- **Nguồn.** SRC-SPEC §3.5 (D20), §10.3, AC-11. SRC-PLAN §3 hàng B16, §11 (PC06).
- **Phương án và đánh đổi.**
  - **(a) Ba trường riêng + `comparator: unknown`.** Giữ được thông tin tác giả nói gì; kiểm được bằng schema. Đổi lại: schema kết quả phức tạp hơn; UI phải hiển thị ba loại khác nhau.
  - **(b) Giữ AC-11 nguyên văn.** Không phải sửa tài liệu. Đổi lại: tuyên bố của tác giả bị hạ cấp thành suy luận của AI, mâu thuẫn §10.3 vốn yêu cầu tách ba loại.
- **Khuyến nghị.** (a). Xem AMD-B16.
- **Phạm vi bị chặn nếu chưa trả lời.** PC06 phần grounding; gate G3.
- **Phạm vi vẫn chạy được.** Mọi gói khác.
- **Quyền cần được cấp.** Phê chuẩn AMD-B16 (sửa câu chữ AC-11).

## B17 — Summary cho "mọi mục" là mọi mục nào

- **Câu hỏi.** Summary được tạo cho **mọi mục được report builder chọn tại thời điểm dựng báo cáo** (theo §10.1), chứ không phải cho mọi bài thu được (theo §2.1 mục 6)?
- **Lý do trọng yếu.** Hai chỗ trong đặc tả nêu hai phạm vi khác nhau. Phạm vi rộng làm chi phí AI tỉ lệ với **số bài thu được** thay vì **số mục báo cáo** — mâu thuẫn với chính §10.4 về kiểm soát chi phí.
- **Nguồn.** SRC-SPEC §2.1 mục 6, §3.5 (D19), §10.1, §10.4, AC-10. SRC-PLAN §3 hàng B17.
- **Phương án và đánh đổi.**
  - **(a) Theo §10.1: chỉ mục được chọn.** Chi phí tỉ lệ số mục báo cáo. Đổi lại: một mục vừa được chọn lần đầu ở kỳ này sẽ cần summary ngay lúc dựng, nên có thể xuất hiện `quality: partial` với danh sách pending.
  - **(b) Theo §2.1: mọi mục trong kho.** Mục nào cũng có sẵn summary. Đổi lại: chi phí AI tăng nhiều lần; nhiều summary không bao giờ được đọc.
- **Khuyến nghị.** (a). Report mang `quality: partial` kèm danh sách pending tường minh; `complete` chỉ khi mọi mục được chọn đã có summary hoặc được đánh dấu pending. Xem AMD-B17.
- **Phạm vi bị chặn nếu chưa trả lời.** PC04 phần selection và PC06 phần enqueue; gate G3.
- **Phạm vi vẫn chạy được.** PC01, PC02, PC03, PC05, PC07, PC08.
- **Quyền cần được cấp.** Phê chuẩn AMD-B17 (làm rõ phạm vi của một hạng mục P0).

## Stack — Chọn ngôn ngữ và nền tảng · **CHẶN M1 và PC10**

- **Câu hỏi.** Chọn A (Python toàn bộ), B (Python worker + TypeScript web) hay C (TypeScript toàn bộ)?
- **Lý do trọng yếu.** SRC-SPEC §13.1 xếp câu hỏi này là **chặn M1**. Không có câu trả lời thì task card không viết được đường dẫn, lệnh build và lệnh test thật.
- **Nguồn.** SRC-SPEC §6.3 (bảng so sánh và khuyến nghị), §13.1 hàng 2. SRC-PLAN §12 (G5).
- **Phương án và đánh đổi.**
  - **(a) A — Python toàn bộ.** Collector (Playwright Python) và embedding local mạnh nhất; một ngôn ngữ; công sức MVP thấp nhất. Đổi lại: web app chỉ ở mức "khá" theo chính bảng của đặc tả.
  - **(b) B — Python worker + TS web.** Web app tốt nhất, worker vẫn mạnh. Đổi lại: hai ngôn ngữ phải bảo trì.
  - **(c) C — TypeScript toàn bộ.** Web app tốt nhất; một ngôn ngữ. Đổi lại: embedding local yếu hơn và ít lựa chọn model, ảnh hưởng D59 và A3.
- **Khuyến nghị.** (a), theo đúng khuyến nghị của đặc tả. Xem ADR-0006.
- **Phạm vi bị chặn nếu chưa trả lời.** PC10 và gate G5; M1. Cập nhật sau FIX5: PC10 đã bàn giao **18 task card** dựng trên giả định stack A (`PROV-PC10-01`) — `server/app/…`, `collector/app/…`, `worker/app/…`, `tests/contract/…`. Nếu bạn chọn B hoặc C thì **chỉ mục §3 (đường dẫn) và §8 (lệnh build/test) của mỗi card phải viết lại**; hợp đồng, schema, scenario và fixture **không** đổi — đó chính là điều kế hoạch thiết kế để tránh. Nói cách khác: trả lời muộn không làm hỏng gì, chỉ tốn một lượt sửa 18 card.
- **Phạm vi vẫn chạy được.** PC01–PC09: hợp đồng và schema được viết độc lập framework, đúng như SRC-PLAN §12 yêu cầu.
- **Quyền cần được cấp.** Chọn một trong ba phương án (đây là câu hỏi mở REQ-OQ02, đặc tả đã nói rõ cần người dùng chọn).

## Timezone — Xác nhận giá trị

- **Câu hỏi.** Múi giờ IANA của bạn là gì? (Giá trị đang dùng tạm: `Asia/Ho_Chi_Minh`.)
- **Lý do trọng yếu.** Đây là phần **giá trị** của B08. Cơ chế thì đã có khuyến nghị, nhưng con số thật phải do bạn cho biết, nếu không mọi fixture lịch đều dựa trên một giả định.
- **Nguồn.** SRC-SPEC §3.6 (D56), §3.3 (D13, D15), AC-02.
- **Phương án và đánh đổi.** Không có phương án thay thế; chỉ cần một giá trị. Nếu bạn thường xuyên đổi múi giờ, hãy nói rõ — khi đó PC03 phải thiết kế thêm cách bạn đổi timezone mà không làm chạy dồn các đợt.
- **Khuyến nghị.** Xác nhận `Asia/Ho_Chi_Minh` hoặc cho một giá trị khác.
- **Phạm vi bị chặn nếu chưa trả lời.** Fixture lịch của PC03 và PC04 phải giữ nhãn PROVISIONAL. Cập nhật sau FIX3: cả hai gói đã dựng fixture lịch trên giá trị tạm và đều nói rõ rằng **nếu bạn ở múi giờ khác thì toàn bộ fixture lịch của hai gói phải dựng lại**. PC03 cũng đã chốt tạm hai quy tắc DST (giờ không tồn tại → chạy tại instant đầu tiên sau khoảng nhảy; giờ lặp → lấy lần đầu); `Asia/Ho_Chi_Minh` không có DST nên hai quy tắc đó chưa từng kích hoạt — chúng chỉ quan trọng nếu bạn chọn một múi giờ có DST.
- **Phạm vi vẫn chạy được.** Toàn bộ phần cơ chế của PC03/PC04.
- **Quyền cần được cấp.** Xác nhận một giá trị.

## Bộ giá trị mặc định cho các câu hỏi còn mở

- **Câu hỏi.** Xác nhận hoặc sửa các giá trị PROVISIONAL dưới đây. Đây là mức "có mặc định tạm": không trả lời cũng không chặn gói nào, nhưng mọi hợp đồng sẽ mang nhãn PROVISIONAL cho tới khi có xác nhận.
- **Lý do trọng yếu.** SRC-PLAN cấm để "TBD" trong hợp đồng: mọi timeout, budget và giới hạn phải có số, đơn vị và lý do. Các số dưới đây tồn tại để hợp đồng không rỗng, **không phải** vì chúng đã được kiểm chứng.
- **Nguồn.** SRC-SPEC §13.1 (10 câu hỏi mở), §8.2 hàng 8, §10.4, §4 (hàng Saved).

| REQ | Câu hỏi | Giá trị đang dùng tạm | Lý do chọn giá trị này | Khi nào nên đặt số thật |
| --- | --- | --- | --- | --- |
| REQ-OQ03 | Provider và model cụ thể | **Không có mặc định** | Không có lựa chọn an toàn; phụ thuộc tài khoản và điều khoản của bạn | Trước M3; là `OWNER_DECISION_REQUIRED` |
| REQ-OQ04 | N ngày backfill cho tag mới | 7 ngày | Lấy nguyên văn đề xuất của SRC-SPEC §13.1 | Bất cứ lúc nào |
| REQ-OQ05 | Giới hạn mỗi đợt | 200 post **hoặc** 30 phút, cái nào tới trước | Ước lượng tạm để hợp đồng có số; đặc tả nói rõ con số thật đến sau M0 | Sau M0, khi có số liệu thật |
| REQ-OQ06 | Lịch cụ thể | 08:00 và 20:00 theo timezone của bạn | Lấy từ ví dụ §8.2 hàng 8 và AC-01/AC-02 | Trước M7 |
| REQ-OQ07 | Giờ yên lặng Telegram | Không có ở MVP | Đặc tả không mô tả cơ chế hoãn gửi; "không có" là mặc định ít bất ngờ nhất | Bất cứ lúc nào |
| REQ-OQ08 | Ngưỡng tương đồng embedding | **Không đặt số** | Phải đo bằng dữ liệu thật (A2); đặt số bây giờ là bịa | Sau M3 |
| REQ-OQ09 | Model embedding cụ thể | **Không đặt tên** | Ràng buộc đã rõ: local, đa ngôn ngữ, lưu tên và phiên bản kèm vector | Sau A3 |
| REQ-OQ10 | Export Saved ở MVP | Hoãn sang P1 | Xem F-PC00-02: §4 liệt kê nút export cho màn hình Saved trong khi §13.1 vẫn hỏi có làm hay không | Bất cứ lúc nào |

- **Khuyến nghị.** Xác nhận cả bảng, hoặc sửa từng dòng. REQ-OQ03 cần một câu trả lời thật trước M3.
- **Phạm vi bị chặn nếu chưa trả lời.** Không gói nào bị chặn; các giá trị giữ nhãn PROVISIONAL.
- **Phạm vi vẫn chạy được.** Tất cả.
- **Quyền cần được cấp.** Xác nhận hoặc thay thế từng giá trị.

## Phạm vi của `data.purge_all` — "xóa toàn bộ dữ liệu" loại trừ những gì?

- **Câu hỏi.** Khi bạn dùng thao tác xóa toàn bộ dữ liệu, những thứ nào **không** bị xóa? Cụ thể: tài khoản đăng nhập, secret và API key, liên kết Telegram, cấu hình provider/model, lịch chạy và các thiết lập khác trong Settings — giữ lại hay xóa cùng?
- **Lý do trọng yếu.** SRC-SPEC §7.3 nói rõ có **ba** thao tác riêng: bỏ lưu, xóa dữ liệu gốc, và xóa toàn bộ dữ liệu — trong đó thao tác thứ ba "đòi xác nhận gõ tay". Nhưng đặc tả không nói "toàn bộ" gồm những gì. Đây là thao tác không đảo được, nên đoán sai theo cả hai hướng đều tệ: xóa cả secret và tài khoản thì bạn có thể mất luôn đường đăng nhập lại và phải dựng lại từ đầu; giữ lại quá nhiều thì có dữ liệu bạn tưởng đã xóa mà vẫn còn. Không có mặc định nào an toàn, nên PC00 **không chọn thay bạn**.
- **Nguồn.** SRC-SPEC §7.3 (`REQ-S7.3-05`, trạng thái **XN**), §11.2 (nơi lưu secret), §3.6 (D58 retention). AUDIT_REPORT `PKT-A1-R1` finding `F-A1R1-04`; ruling R-04 của Coordinator; `PROV-PC00-01` trong `precode/decision-register.md` §8.
- **Phương án và đánh đổi.**
  - **(a) Chỉ xóa dữ liệu nghiên cứu.** Xóa post, work, analysis, report, Saved, vector, ledger. **Giữ** tài khoản đăng nhập, secret/API key, liên kết Telegram, cấu hình provider và lịch. Bạn vẫn đăng nhập được và hệ thống chạy tiếp ngay. Đổi lại: secret và chat ID vẫn nằm trên máy chủ sau một thao tác mang tên "xóa toàn bộ".
  - **(b) Xóa tất cả trừ tài khoản đăng nhập.** Như (a) nhưng xóa cả secret, liên kết Telegram và cấu hình provider. Bạn còn đăng nhập được nhưng phải cấu hình lại từ đầu. Đổi lại: mất cấu hình đã hiệu chỉnh, phải sinh lại mã liên kết Telegram.
  - **(c) Xóa mọi thứ, kể cả tài khoản.** Đúng nghĩa đen nhất. Đổi lại: cần một đường khôi phục quyền truy cập ngoài ứng dụng, mà D05 lại cấm trang signup và cấm quên-mật-khẩu tự động — nên phương án này đòi một cơ chế bootstrap mới chưa có trong đặc tả.
- **Khuyến nghị.** **Không có khuyến nghị.** Đây là điểm PC00 giữ ở `OWNER_DECISION_REQUIRED` thay vì chọn một giá trị PROVISIONAL, vì cả ba phương án đều làm mất một thứ mà đặc tả không cho phép suy ra. Nếu buộc phải đi tiếp trước khi bạn trả lời, phương án (a) là hẹp nhất và đảo được nhiều nhất — nhưng nó vẫn cần bạn xác nhận, không phải mặc định.
- **Hai hệ quả PC08 phát hiện, cần biết trước khi chọn.** (1) **Nếu purge xóa credential đăng nhập** thì phải có một đường đặt lại tại chỗ — D05 cấm trang signup và cấm quên-mật-khẩu tự động, nên nếu không chuẩn bị trước, bạn có thể **tự khóa mình ra ngoài app** và chỉ vào lại được bằng thao tác thủ công trên máy chủ. (2) **Dữ liệu đã purge vẫn còn trong các bản backup** cho tới khi chính những bản đó bị xóa; muốn xóa hẳn thì phải xóa cả backup, và đó là một thao tác riêng. Nếu bạn hiểu "xóa toàn bộ" là "không còn ở bất kỳ đâu", hãy nói rõ — khi đó thao tác này phải kéo theo việc xóa backup.
- **Hình dạng đã chốt tạm (không cần bạn quyết, chỉ để biết).** `data.purge_all` chạy hai pha: pha 1 server phát một cụm từ xác nhận có hạn, pha 2 bạn gõ lại đúng cụm đó. Chỉ chạy khi hệ thống ở trạng thái bảo trì; thu hồi mọi lease; gọi lại lần hai không xóa lần hai. Xem `PROV-PC00-03` và scenario `SC44`.
- **Phạm vi bị chặn nếu chưa trả lời.** Ngữ nghĩa của `data.purge_all` trong `contracts/ports.yaml` (PC01) và phần khóa maintenance cùng thu hồi lease trong PC08; gate G1 và G3 cho riêng operation này. Thao tác `data.delete_target` (xóa dữ liệu gốc **một** target) **không** bị chặn: phạm vi của nó đã rõ từ D55 — giữ `saved_snapshot`, giữ ledger.
- **Phạm vi vẫn chạy được.** Toàn bộ phần còn lại của PC01 và PC08, và mọi gói khác. `save.remove` (bỏ lưu) đã có và không phụ thuộc câu trả lời này.
- **Quyền cần được cấp.** Chọn một trong ba phương án, hoặc liệt kê thẳng danh sách những gì phải giữ lại. Kèm theo: xác nhận rằng thao tác này chỉ chạy khi hệ thống ở trạng thái bảo trì và cần gõ đúng một cụm xác nhận do máy chủ phát.

## Tham số báo cáo và mật độ — tám lựa chọn của PC04

- **Câu hỏi.** Xác nhận hoặc sửa tám quyết định dưới đây. Chúng quyết định **bài nào vào báo cáo**, **khối "hướng đang nổi" hiện gì**, và **tag mới được với ngược bao nhiêu lần** — tức là phần bạn nhìn thấy mỗi kỳ.
- **Lý do trọng yếu.** Không quyết định nào trong số này có sẵn trong đặc tả: B14 giao PC04 tự định nghĩa phép đo mật độ, còn `REQ-OQ08` nói rõ **không** được đặt ngưỡng như thể đã biết. Nhưng baseline cũng cấm để "TBD" trong hợp đồng. PC04 giải quyết bằng cách đặt số **kèm nhãn chưa hiệu chỉnh** và cấm tuyên bố đạt chỉ tiêu §1.4 khi nhãn đó còn — chứ không giả vờ đã đo.
- **Nguồn.** `evidence/handoffs/PC04-handoff.md` §7.3 (tám mục) và §7.5; `contracts/reporting/selection.md`, `contracts/reporting/time-and-tags.md`; SRC-SPEC §8.2 hàng 4, §10.4, §1.4; B14, `REQ-A2`, `REQ-A4`, `REQ-OQ04`, `REQ-OQ05`, `REQ-OQ08`. Đăng ký tại `precode/decision-register.md` §8.5 (`PROV-PC04-01`…`PROV-PC04-09`).
- **Phương án và đánh đổi.**

  | # | Quyết định tạm | Nghĩa với bạn | Nếu bạn muốn khác |
  | --- | --- | --- | --- |
  | 1 | First-announcement sau khi gộp hai bản ghi = **ngày sớm nhất**, có audit | Một công trình chỉ "mới" đúng một lần, tính từ lần đầu bạn thấy nó | "Coi như chưa công bố" vi phạm D29; "lấy ngày muộn hơn" hiển thị sai sự thật |
  | 2 | Backfill khóa theo **chữ tag đã chuẩn hóa**; xóa tag rồi thêm lại **không** được với ngược lần nữa | Không thể vô tình lấy lại N ngày cũ bằng cách gõ lại đúng chữ tag | Muốn cấp lại mỗi lần thêm lại thì nói rõ; hiện "đào sâu hơn" dùng nút quét lại kho (D28) |
  | 3 | Backfill chỉ bị tiêu thụ khi publish thành công **và** phần nới có ít nhất một ứng viên | Builder crash hoặc khoảng rỗng không đốt mất quyền backfill | Tiêu thụ vô điều kiện thì đơn giản hơn nhưng mất quyền một cách âm thầm |
  | 4 | arXiv **phiên bản mới** = tham chiếu "đã báo cáo ngày…", không phải phát hiện mới | v2 của một paper đã báo cáo không xuất hiện lại như tin mới | Coi v2 là phát hiện mới sẽ phá bảo đảm "không báo lại" (D29) |
  | 5 | Mục chỉ-có-post: "đã công bố" suy từ report đã publish | Post-only cũng không bị báo lại hai lần | — |
  | 6 | Ngưỡng khớp tag **0.8000**, gắn nhãn `PROVISIONAL_BOOTSTRAP`, trạng thái `uncalibrated` | Hệ thống chạy được ngay, nhưng **không** được tuyên bố đạt chỉ tiêu "tỷ lệ nhiễu" của §1.4 khi còn nhãn này | Con số thật phải đến từ 50–100 bài bạn gán nhãn tay (`REQ-A2`) |
  | 7 | Tham số mật độ: bán kính `0.8`, tối thiểu **3** thành viên một cụm, cửa sổ so sánh **4** kỳ, cần ≥ **2** kỳ trước, chênh lệch tối thiểu **2.0**, tối đa **3** hướng nổi mỗi kỳ | Vài kỳ đầu khối "hướng đang nổi" nhiều khả năng **trống** — đúng như B14 yêu cầu (`insufficient_evidence`) | Nới lỏng để khối luôn có nội dung sẽ làm tăng nhiễu, đúng thứ §1.4 muốn tránh |
  | 8 | Tối đa **50** mục mỗi kỳ; vượt thì mục còn lại vào sổ chờ, **không** bị bỏ | Kỳ đông bài vẫn có báo cáo đọc được, phần dư sang kỳ sau | Số thật nên đặt sau M0 cùng `REQ-OQ05` |

- **Riêng "kỳ rỗng":** Coordinator khuyên phương án (a) — không để lại hàng `report` nào. **PC04 chọn (b)** — một hàng `report(status='aborted', abort_reason='empty_period')` — và nêu lý do kỹ thuật cụ thể: `coverage_window` không có khóa idempotency, nên dưới (a), một lần mất phản hồi sẽ khiến hệ thống thử tiến coverage lần hai và báo xung đột. Cả hai phương án đều **không** hiển thị gì cho bạn (kỳ rỗng không có read model), nên khác biệt nằm ở chẩn đoán, không ở trải nghiệm.
- **Khuyến nghị.** Xác nhận cả tám, kèm phương án (b) cho kỳ rỗng. Hai mục đáng bạn để ý nhất là **#2** (thêm lại tag không được với ngược lần nữa) và **#6** (ngưỡng chưa hiệu chỉnh, nên đừng đọc chỉ số nhiễu của vài kỳ đầu như một kết luận).
- **Phạm vi bị chặn nếu chưa trả lời.** Không gói nào bị chặn: mọi giá trị đều có nhãn PROVISIONAL và fixture tất định. Nhưng **`REQ-D52` và chỉ tiêu §1.4 không được tuyên bố đạt** khi ngưỡng còn `uncalibrated`, và `REQ-A4` (mật độ có thật hay không) vẫn cần 3–4 kỳ dữ liệu thật.
- **Phạm vi vẫn chạy được.** Toàn bộ PC04 và các gói phụ thuộc; các con số đã đủ để viết hợp đồng và fixture.
- **Quyền cần được cấp.** Xác nhận cả bảng, hoặc sửa từng dòng; kèm quyết định (a)/(b) cho kỳ rỗng.

## Vận hành và bảo mật — tham số của PC08

- **Câu hỏi.** Xác nhận hoặc sửa: **RPO 24 giờ / RTO 2 giờ**, lịch và retention backup, các tham số phiên đăng nhập, và vòng đời token của collector.
- **Lý do trọng yếu.** RPO là "chấp nhận mất tối đa bao nhiêu dữ liệu"; RTO là "chấp nhận hỏng bao lâu trước khi khôi phục xong". Hai con số này không suy ra được từ đặc tả — chúng phụ thuộc việc bạn khó chịu đến mức nào khi mất một ngày dữ liệu thu thập. Mọi thiết kế backup phía dưới đều bám theo chúng.
- **Nguồn.** `evidence/handoffs/PC08-handoff.md` §6.3; `contracts/ops/backup-restore.md`, `contracts/ops/secrets.md`; SRC-SPEC §3.6 (D58), §11.1, §11.2; AMD-B11, ADR-0005. Đăng ký tại `precode/decision-register.md` §8.5 (`PROV-PC08-01`…`PROV-PC08-05`).
- **Phương án và đánh đổi.**
  - **Khôi phục.** RPO 24 h / RTO 2 h, backup 03:00 hằng ngày, giữ 14 bản ngày + 8 bản tuần + bản tháng vô thời hạn. Nghĩa là: sự cố tệ nhất làm mất **một ngày** thu thập. Muốn RPO ngắn hơn thì phải backup nhiều lần trong ngày — tốn dung lượng và thời gian, không tốn tiền dịch vụ.
  - **Đăng nhập.** Argon2id (64 MiB, t=3, p=1); phiên nghỉ 12 giờ thì hết hạn, tối đa 30 ngày; sai mật khẩu 5 lần trong 15 phút thì khóa 15 phút. Phiên 12 giờ nghĩa là mở app buổi sáng và buổi tối thường phải đăng nhập lại — nới lên 7 ngày thì tiện hơn nhưng một thiết bị bị mất sẽ mở được app lâu hơn.
  - **Token collector.** 256 bit, quyền file `0600`, xoay 180 ngày với 24 giờ chồng lấn. Xoay ngắn hơn thì an toàn hơn nhưng bạn phải thao tác trên máy cá nhân thường xuyên hơn.
  - **Nhật ký.** Audit giữ 365 ngày; riêng **bản ghi các thao tác xóa giữ vô thời hạn** — để sau này còn trả lời được câu "cái đó biến mất lúc nào".
- **Khuyến nghị.** Xác nhận cả bộ. Nếu chỉ muốn đổi một thứ, đổi **phiên đăng nhập 12 giờ** — đó là con số bạn sẽ va vào hằng ngày, và nới nó không ảnh hưởng gói nào khác.
- **Phạm vi bị chặn nếu chưa trả lời.** Không gói nào bị chặn; mọi số đã có nhãn PROVISIONAL và một dòng lý do tại chỗ. Nhưng **chưa có drill restore nào chạy** — PC08 ghi rõ `backup-restore.md` là thiết kế, không phải bằng chứng khôi phục được.
- **Phạm vi vẫn chạy được.** Toàn bộ PC08 và các gói phụ thuộc.
- **Quyền cần được cấp.** Xác nhận hoặc thay thế từng giá trị; đặc biệt là RPO và RTO.

## Hai thay đổi kỹ thuật cần Owner biết

- **Câu hỏi.** Bạn có phản đối hai thay đổi dưới đây không? Cả hai đã được Coordinator chốt tạm trong phạm vi ủy quyền; mục này để bạn biết chứ không bắt bạn quyết.
- **Lý do trọng yếu.** Thay đổi thứ hai chạm một câu bạn đã đọc trong đặc tả (§5.4 bước 5: *"nếu hạn chế vẫn còn, run **không** tự tiếp tục — dừng và báo"*), nên nó không được lặng lẽ trôi qua.
- **Nguồn.** `precode/decision-register.md` §8 (`PROV-PC00-02`, `PROV-PC00-04`); `CR-PC08-03`, `CR-PC08-04`, `CR-PC03-02`; SRC-SPEC §5.4, §9.3, §11.1; AMD-B02, AMD-B10.
- **Phương án và đánh đổi.**
  1. **Mã lỗi `CSRF_REJECTED` riêng.** Trước đây một request thiếu token chống giả mạo bị trả về cùng mã với "đường đi không được phép" — hai chuyện khác hẳn nhau bị gộp làm một, khiến chẩn đoán sai. Nay tách thành mã riêng. Không thay đổi gì bạn thấy; chỉ làm thông báo lỗi và bản ghi kiểm toán nói đúng chuyện đã xảy ra.
  2. **Nút "tiếp tục" dùng được cho cả run bị chặn.** Trước đây khi X chặn, đường thoát duy nhất là **hủy** run và tạo run mới — mất ngữ cảnh. Nay bạn có thể bấm tiếp tục, **bắt buộc** kèm một dòng lý do ("điều kiện chặn đã hết"). Ranh giới không đổi: **không có** bất kỳ đường tự động nào, không có lệnh Telegram tương ứng, và hệ thống vẫn không bao giờ tự thử lại sau khi bị chặn. Chỉ bạn, chỉ trong app, và luôn ghi lại lý do.
- **Khuyến nghị.** Chấp nhận cả hai. Thay đổi 2 làm đúng điều §5.4 muốn — không tự tiếp tục — nhưng thêm một đường để **bạn** tiếp tục mà không phải vứt bỏ tiến độ đã thu.
- **Phạm vi bị chặn nếu chưa trả lời.** Không gì bị chặn; cả hai đã ở trạng thái PROVISIONAL và các gói đang triển khai theo.
- **Phạm vi vẫn chạy được.** Tất cả.
- **Quyền cần được cấp.** Chỉ cần một lời xác nhận, hoặc một lời phản đối kèm hướng bạn muốn.

---

## Hai điểm PC00 tự quyết theo khuyến nghị của kế hoạch

Hai mâu thuẫn dưới đây **không** nằm trong B01–B17. PC00 đã chọn phương án mà kế hoạch khuyến nghị, gắn nhãn PROVISIONAL và báo lên đây thay vì tự coi là đã giải quyết.

| ID | Mâu thuẫn | Lựa chọn tạm | Cần Owner làm gì |
| --- | --- | --- | --- |
| F-PC00-01 | D36 và §11.3 nói **đúng 3 lệnh** Telegram, nhưng D37 yêu cầu "có lệnh hủy liên kết" — tức lệnh thứ tư | Hủy liên kết là hành động **trong app**; Telegram giữ đúng 3 lệnh | Xác nhận, hoặc cho phép thêm lệnh thứ tư và sửa §11.3 |
| F-PC00-02 | §4 liệt kê hành động **export** cho màn hình Saved, trong khi REQ-OQ10 vẫn hỏi có cần export ở MVP không | Hoãn export sang P1; MVP không có nút export ở màn hình Saved | Xác nhận, hoặc yêu cầu giữ export ở MVP và sửa REQ-OQ10 |

## Phiếu trả lời gợi ý

```text
── ĐÃ TRẢ LỜI 2026-09-07 · OD-20260907-01 · AUTH-OWNER-20260907-02 ──
B01: (a) publish                                    ✅
B02: (a) bốn trường                                 ✅
B03: (a) unknown, không auto-retry                  ✅
B04: (a) sổ coverage riêng                          ✅
B05: (a) không ingest trùng                         ✅
B06: (a) alias + target union                       ✅
B07: (a) analysis key + generation                  ✅
B08: (a) một IANA timezone     Giá trị: Asia/Ho_Chi_Minh   ✅
B09: (a) ngoại lệ hẹp cho mã                        ✅
B10: (a) resume trong app, 3 lệnh                   ✅
B11: (a) snapshot nhất quán    RPO: 24 h  RTO: 2 h  ✅
B12: D09 profile riêng? CÓ     ·  Xóa cạnh COL→AW? CÓ      ✅
B13: (a) secret theo task + mặc định disabled       ✅  (AC-16 vẫn BLOCKED tới khi probe đạt)
B14: (a) insufficient_evidence                      ✅  (D53 vẫn ĐX ở phần hiệu chỉnh tham số)
B15: (a) thu hẹp phạm vi                            ✅
B16: (a) ba loại phát biểu                          ✅
B17: (a) theo §10.1                                 ✅
Stack: B  (Python workers + TypeScript web)         ✅  ← KHÔNG phải A như khuyến nghị
OQ mặc định: xác nhận cả bảng? CÓ
   OQ03 provider+model: CHƯA QUYẾT ĐỊNH — vẫn OWNER_DECISION_REQUIRED, chặn M3
F-PC00-01: hủy liên kết trong app? CÓ               ✅
F-PC00-02: hoãn export Saved sang P1? CÓ            ✅
data.purge_all: (a) chỉ dữ liệu nghiên cứu          ✅
   Giữ lại cụ thể: đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch
   Có xóa cả backup không? KHÔNG
PC04 tham số báo cáo: xác nhận cả 8 mục? CÓ  ·  sửa mục nào: (không)
   Kỳ rỗng: (b) giữ hàng aborted                    ✅
PC08 vận hành: RPO 24 h · RTO 2 h · phiên đăng nhập 12 h
   retention backup: 14 ngày + 8 tuần + hằng tháng vô thời hạn
CSRF_REJECTED là mã lỗi riêng: CÓ                   ✅
run.resume từ blocked (bắt buộc ghi lý do): CÓ      ✅

── VÒNG HAI · ĐÃ TRẢ LỜI 2026-09-07 · OD-20260907-02 · AUTH-OWNER-20260907-03 ──
ADR-0011 frameworks: accept                                 ✅
   (Owner trả lời "accept ADR-0011, start phase 0 and 1".
    Chi tiết 14 tầng ở precode/adr/ADR-0011-frameworks-and-toolchain.md;
    ADR nay status accepted, ratified_by OD-20260907-02.
    Bốn hàng Test / Lint / CI / Đóng gói vẫn là "chưa từng cân nhắc
    phương án nào" — phê chuẩn không đổi điều đó; đảo vẫn chỉ sửa card và mã.)
Bắt đầu Giai đoạn 0 và Giai đoạn 1 (docs/master-plan.md): CÓ  ✅
   (Giai đoạn 0 đóng G5-X4; Giai đoạn 1 = M1 kho dữ liệu, ingest, auth,
    storage readiness. Trần claim `IMPLEMENTATION_VERIFIED`, không bao giờ
    INTEGRATION/LIVE; product_status giữ NOT_READY_FOR_PRODUCT_CODE.)

── VÒNG BA · ĐÃ TRẢ LỜI 2026-09-07 · OD-20260907-03 · AUTH-OWNER-20260907-04 ──
AMD-ENT-owner-01 (4 cột credential/lockout trên owner): ratify ✅
   (entities.yaml GIỮ CONTRACT_READY — không được nâng. Nhãn
    `IMPLEMENTATION_VERIFIED` của card auth nay đứng trên quyết định của
    Owner thay vì một amendment do Coordinator ký; verdict của auditor
    KHÔNG đổi vì thế, và F-A3R1-02 / F-A3R1-06 KHÔNG bị đóng.)
PROV-PC00-08 (ghi mã dưới lease theo thông điệp, không cưỡng chế OS): accept ✅
   (Rủi ro còn lại được THỪA NHẬN, không phải được xoá:
    ghi ngoài tập ghi không bị chặn; hai Worker song song không có
    fencing thật; không có audit log bền vững do service ghi.
    enforcement vẫn NOT_IMPLEMENTED.)
Bắt đầu Giai đoạn 2 (docs/master-plan.md): CÓ                ✅
   2A = M0 probe khả thi X — cấp phép VIẾT card và mã.
        CHẠY LIVE VẪN BỊ CHẶN: collector-probe.md §6 mục 2–4,
        và probe phải chạy trên máy của Owner.
   2B = M2 paper connector — CHƯA CÓ CARD, phải viết card trước.
        CONTRACT_READY VẪN BỊ CHẶN CỨNG bởi REQ-A6 tới khi bốn dữ kiện
        rate/identity được ghi từ tài liệu chính thức. KHÔNG ĐOÁN SỐ.

── VÒNG BỐN · ĐÃ TRẢ LỜI 2026-09-07 · OD-20260907-04 · AUTH-OWNER-20260907-05 ──
Cổng probe contracts/ops/collector-probe.md §6 mục 2–4: chấp nhận cả ba ✅
   (§6 mục 1–4 NAY ĐỀU THỎA. Cổng mở về HÀNH CHÍNH.
    Điều kiện VẬT LÝ không đổi: probe chạy trên tài khoản X thật và máy
    thật của Owner, sau khi Owner tự cài Playwright, đăng nhập tay vào
    Chrome profile riêng, điền probe-config.json và ký bốn
    owner_confirmations. KHÔNG WORKER NÀO ĐƯỢC CHẠY NÓ.
    Ba mục vừa chấp nhận đều là ngưỡng PROVISIONAL do PC05 đề xuất —
    chấp nhận = đồng ý dùng làm tiêu chí, KHÔNG phải đã hiệu chỉnh.)
REQ-A6: cho một Worker đọc tài liệu chính thức                ✅
   ĐƯỢC: chỉ trang tài liệu dưới arxiv.org, info.arxiv.org,
         openalex.org, docs.openalex.org — mỗi dữ kiện kèm URL nguồn,
         ngày lấy và một trích dẫn nguyên văn ngắn.
   KHÔNG ĐƯỢC: export.arxiv.org, api.openalex.org, hay bất kỳ endpoint
         live nào — KHÔNG lưu lượng API thật.
   >>> REQ-A6 VẪN KC. Owner cho phép ĐI LẤY dữ kiện, KHÔNG cung cấp
       dữ kiện. retry-policy.yaml giữ bốn null + PLACEHOLDER_KC +
       min_interval_ms = 3000 tới khi bốn con số land kèm nguồn.

── VÒNG NĂM · ĐÃ TRẢ LỜI 2026-09-08 · OD-20260908-05 · AUTH-OWNER-20260908-06 ──
OQ03 provider + model: "nghiên cứu và đề xuất, tôi phê duyệt"    ✅ (ỦY QUYỀN)
   >>> ĐÂY KHÔNG PHẢI CÂU TRẢ LỜI CHO OQ03. Owner giao việc NGHIÊN CỨU;
       OQ03 VẪN OWNER_DECISION_REQUIRED tính đến vòng năm, và REQ-A5
       (đọc điều khoản của từng nhà cung cấp) là một CỔNG RIÊNG phải
       xong TRƯỚC khi đặt adapter enabled = true.
       Lựa chọn model cụ thể nằm ở biên bản RIÊNG: OD-20260908-06
       (precode/owner-decisions-06.md) — đừng đọc nó từ dòng này.
CR-PC07-04 (5 dữ kiện giới hạn định dạng Telegram):
   Lấy tài liệu ngay + khởi động Giai đoạn 5 song song            ✅
   ĐƯỢC: chỉ trang tài liệu dưới core.telegram.org
         (cụ thể core.telegram.org/bots/api)
   KHÔNG ĐƯỢC: api.telegram.org, bất kỳ lời gọi Bot API thật nào,
         bot token, hay gửi một tin nhắn nào.
   ĐIỀU KIỆN Owner đặt cho Giai đoạn 5: "một khi NĂM dữ kiện land".
   >>> TÍNH ĐẾN 2026-09-08 ĐIỀU KIỆN CHƯA THỎA: mới HAI/năm dữ kiện
       có nguồn sau hai vòng của worker-WT; ba dữ kiện còn lại
       (callback_data, parse mode + bảng escape, số nút mỗi hàng)
       vẫn BLOCKED_DEPENDENCY. CR-PC07-04 = PARTIALLY_RESOLVED,
       KHÔNG phải CLOSED. Giai đoạn 5 CHƯA được gỡ chặn (CR-PC00-31).

── VÒNG BẢY · ĐÃ TRẢ LỜI 2026-09-08 · OD-20260908-07 · AUTH-OWNER-20260908-08 ──
Ba dữ kiện Telegram — nới quyền? CÓ: thêm WebSearch            ✅
   CHỈ để định vị nội dung của CHÍNH trang core.telegram.org/bots/api
   (bản cache/lưu trữ của chính trang ấy). KHÔNG để lấy một con số
   KHÁC từ site khác. Vẫn cấm api.telegram.org / bot token / gửi tin.
   >>> NỚI QUYỀN KHÔNG TẠO RA DỮ KIỆN: vòng ba chạy dưới quyền mới,
       cả ba dữ kiện VẪN BLOCKED_DEPENDENCY (§8.14.3).
Người ký REQ-A5: OWNER ĐÍCH THÂN, không phải Worker             ✅
   (CR-PC06-OQ03-02 GIỮ MỞ qua hết vòng bảy; trường reviewer KHÔNG
    được điền tên một Worker.)

── VÒNG TÁM · ĐÃ TRẢ LỜI 2026-09-08 · OD-20260908-08 · AUTH-OWNER-20260908-09 ──
REQ-A5 cho Anthropic: KÝ                                        ✅
   Đã đọc: Commercial ToS (eff. 2025-06-17), Usage Policy
   (eff. 2025-09-15), Service Specific Terms (eff. 2026-06-08).
   CHẤP NHẬN TƯỜNG MINH bảo đảm TC-A5-01 — Owner (không phải
   Anthropic) tuyên bố hệ thống CÓ QUYỀN gửi abstract của bên thứ ba
   làm Input.  → CR-PC06-OQ03-02 ĐÓNG.
   >>> BA RANH GIỚI: (a) chỉ Anthropic, chỉ BẢN ĐỌC này — hết hiệu
       lực khi một trong ba trang đổi phiên bản; (b) KÝ ≠ BẬT —
       enabled = true vẫn bị B13 chặn (ISO-03/ISO-05 chưa kiểm,
       E3 NOT_RUN, REQ-AC16 vẫn BLOCKED); (c) arXiv/OpenAlex/X có
       cho phép tái xử lý hay không VẪN CHƯA AI TRẢ LỜI — Owner
       GÁNH bảo đảm đó, không GIẢI nó.

── VÒNG CHÍN · ĐÃ TRẢ LỜI 2026-09-08 · OD-20260908-09 · AUTH-OWNER-20260908-10 ──
Phạm vi Giai đoạn 5: "bắt đầu với văn bản thuần ngay,
   thêm định dạng sau"                                          ✅
   TRONG PHẠM VI: cắt tin theo 4096 ký tự; điều tiết nhịp gửi.
        Cả hai dựa trên dữ kiện ĐÃ GIẢI, có trích dẫn nguyên văn.
   NGOÀI PHẠM VI, CHƯA HIỆN THỰC, CÓ SG-01 CANH:
        parse_mode (Markdown/HTML), inline keyboard,
        nút mang callback_data.
        >>> KHÔNG phải stub-rồi-giấu. Ba đường mã đó KHÔNG TỒN TẠI.
   >>> ĐIỀU KIỆN CŨ CỦA VÒNG NĂM ("năm dữ kiện land") ĐƯỢC **THAY**,
       KHÔNG phải được THỎA — nó vẫn là 2/5 và chưa bao giờ đạt.
       CR-PC07-04 VẪN PARTIALLY_RESOLVED.

── VẪN CHỜ ─────────────────────────────────────────────────
Ba dữ kiện Telegram còn lại — GIẢI BẰNG CÁCH NÀO: _______________
   (amendment công cụ cho fetch phân trang, hay Owner tự đọc trang?
    Vòng chín hoãn câu này. Chúng bị chặn bởi GIỚI HẠN CÔNG CỤ ĐỌC,
    không phải bởi một khoảng trống chính sách — xem §8.14.3.)
REQ-A5 cho các nhà cung cấp KHÁC Anthropic: ____________________
   (Anthropic đã được Owner ký ở OD-20260908-08; cổng này vẫn là
    RIÊNG cho TỪNG adapter, trước khi đặt enabled = true)
Chính sách của arXiv/OpenAlex/X về tái xử lý nội dung: __________
   (câu hỏi nền của TC-A5-01 — KHÁC với điều khoản của Anthropic.
    Chữ ký vòng tám KHÔNG giải nó; Owner đang GÁNH bảo đảm ấy.)
```

**Ba điều biên bản KHÔNG làm** (chép lại để không ai đọc rộng hơn): `REQ-OQ03` vẫn mở và vẫn chặn M3; mọi mục `KC` vẫn `KC` vì buổi phỏng vấn không tạo bằng chứng runtime nào; và không finding audit nào bị đóng.

Trả lời một phần vẫn hữu ích: mỗi mục được chốt sẽ gỡ đúng phạm vi ghi ở dòng "Phạm vi bị chặn" của mục đó.
