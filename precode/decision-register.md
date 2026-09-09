---
contract_id: CT-precode-decision-register
version: 0.1.4
status: draft
owner_role: requirements owner (PC00)
source_refs:
  - SRC-SPEC §1.4, §2, §3, §4, §5, §6, §7, §8, §9, §10, §11, §12, §13
  - SRC-PLAN §3, §3.1, §6, §7, §8, §9, §10, §11, §12
requirement_refs: [precode/requirements.csv — toàn bộ 246 dòng]
decision_refs: [OD-20260907-01, OD-20260907-02, OD-20260907-03, OD-20260907-04, OD-20260908-05, OD-20260908-06, B01..B17, AMD-B01, AMD-B02, AMD-B03, AMD-B04, AMD-B05, AMD-B07, AMD-B08, AMD-B09, AMD-B10, AMD-B11, AMD-B12, AMD-B15, AMD-B16, AMD-B17, ADR-0001..ADR-0011]
invariant_refs: [I01..I15]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies:
  - precode/baseline.json
  - precode/source/spec-v0.2.md
  - precode/source/pre-code-plan-v0.1.md
  - precode/requirements.csv
scope: >
  Sổ đăng ký các điểm chưa đóng của đặc tả (B01–B17), phương án xử lý tạm thời, các amendment
  làm thay đổi hành vi đã cam kết, các mục P0 còn ở trạng thái ĐX, và các phát hiện mâu thuẫn
  mới do PC00 tìm ra. Cập nhật 2026-09-07: Owner đã phê chuẩn qua OD-20260907-01
  (precode/owner-decisions.md) — B01-B17 nay RATIFIED và các amendment tương ứng ACCEPTED.
  REQ-OQ03 vẫn OWNER_DECISION_REQUIRED. Cập nhật vòng hai 2026-09-07: OD-20260907-02
  (precode/owner-decisions-02.md) phê chuẩn ADR-0011 và mở lối vào Giai đoạn 0 và 1 của
  docs/master-plan.md. Cập nhật vòng ba 2026-09-07: OD-20260907-03 (precode/owner-decisions-03.md)
  phe chuẩn AMD-ENT-owner-01 và PROV-PC00-08, và mở lối vào Giai đoạn 2. File này KHÔNG đóng bất kỳ
  finding audit nào. Cập nhật vòng bốn 2026-09-07: OD-20260907-04 (precode/owner-decisions-04.md)
  đóng cổng chấp nhận probe §6 mục 2-4 và cấp một quyền mạng hẹp một lần để đọc tài liệu chính thức
  phục vụ REQ-A6 — REQ-A6 VẪN KC, biên bản không cung cấp dữ kiện, chỉ cho phép đi lấy.
  Cập nhật vòng sáu 2026-09-08: OD-20260908-06 (precode/owner-decisions-06.md) TRẢ LỜI REQ-OQ03 —
  summary = claude-opus-5; label + direction_phrasing = claude-sonnet-5; cả hai họ api_key. Câu
  "REQ-OQ03 vẫn OWNER_DECISION_REQUIRED" ở trên đọc theo đúng thì của nó (vòng một, 2026-09-07) và
  nay đã bị §8.15 thay thế. Việc BẬT adapter thì KHÔNG được mở: cả hai enabled = false vì cô lập
  chưa kiểm chứng.
verification: E0 — self-validation bằng script kiểm đếm (EV-PC00-04); không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# Sổ đăng ký quyết định — Pre-code PC00

**Trạng thái phiên:** `DOCUMENTARY_DRAFT`, enforcement `NOT_IMPLEMENTED`, product status `NOT_READY_FOR_PRODUCT_CODE`.

## 0. Cách đọc file này

| Nhãn | Nghĩa trong phiên này |
| --- | --- |
| `OPEN` | Chưa có phương án nào được ghi nhận |
| `PROVISIONAL` | Coordinator đã ghi nhận phương án theo PC-ĐX của SRC-PLAN dưới `AUTH-OWNER-20260906-01`; **chưa** phải quyết định của Owner |
| `RATIFIED (OD-20260907-01)` | Owner đã phê chuẩn ngày 2026-09-07 — xem `precode/owner-decisions.md` |
| `ACCEPTED (OD-20260907-01)` | Amendment hoặc quyết định đã được Owner chấp nhận trong cùng biên bản |
| `ACCEPTED (OD-20260907-02)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng hai** — xem `precode/owner-decisions-02.md` |
| `ACCEPTED (OD-20260907-03)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng ba** — xem `precode/owner-decisions-03.md` |
| `ACCEPTED (OD-20260907-04)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng bốn** — xem `precode/owner-decisions-04.md` |
| `ACCEPTED (OD-20260908-06)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng sáu** — xem `precode/owner-decisions-06.md`. (Vòng **năm**, `OD-20260908-05`, không dùng nhãn này: nó giao việc nghiên cứu chứ không chấp nhận một phương án — xem §8.14) |
| `ACCEPTED (OD-20260908-08)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng tám** — xem `precode/owner-decisions-08.md` (bản ghi hiệu lực: §8.15.1) |
| `ACCEPTED (OD-20260908-09)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng chín** — xem `precode/owner-decisions-09.md` |
| `ACCEPTED (OD-20260908-10)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng mười** — xem `precode/owner-decisions-10.md` |
| `OWNER_DECISION_REQUIRED` | Không có phương án mặc định an toàn; phạm vi liên quan bị chặn tường minh |

**Cập nhật 2026-09-07.** Owner đã trả lời bản yêu cầu quyết định. Biên bản `OD-20260907-01` (`precode/owner-decisions.md`, authority `AUTH-OWNER-20260907-02`) phê chuẩn B01–B17 và các amendment tương ứng. `agent_profile/registry.json` nay có `open_product_blockers: []` và một danh sách `ratified_product_blockers` trích `evidence_ref`.

Ba điều **không** đổi theo biên bản: `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED` và vẫn chặn M3; mọi mục `KC` vẫn `KC` (buổi phỏng vấn không tạo bằng chứng runtime nào); và không finding audit nào bị đóng — chúng theo vòng đời riêng của `protocol.md` §8.

Trạng thái yêu cầu (`XN | UQ | ĐX | KC`) trong `precode/requirements.csv` giữ nguyên như đặc tả, **trừ bốn dòng** mà biên bản chuyển tường minh: D08, D09, D42, D50 (`ĐX` → `XN`). Amendment ở §3 nay là văn bản **đã được chấp nhận**; việc phát hành một đặc tả v0.3 áp dụng chúng là công việc riêng, chưa được giao.

**Cập nhật vòng hai 2026-09-07.** Biên bản thứ hai `OD-20260907-02` (`precode/owner-decisions-02.md`, authority `AUTH-OWNER-20260907-03`, evidence `session_0156UBBHDSeC9soECzSVUb3U`) làm **hai** việc: phê chuẩn `ADR-0011` (nên `PROV-PC00-07` ở §8 nay `ACCEPTED (OD-20260907-02)`) và mở lối vào Giai đoạn 0 và Giai đoạn 1 của `docs/master-plan.md` (§8.10). Nó **không** đổi trạng thái của một dòng nào trong `precode/requirements.csv`, **không** giải `REQ-OQ03`, **không** đổi một mục `KC` nào và **không** đóng finding nào. Chế độ vận hành cho việc ghi mã — hệ quả *hàm ý* của lối vào đó, do Coordinator ruling chứ không do Owner phát biểu — nằm ở `PROV-PC00-08` — **nay `ACCEPTED (OD-20260907-03)`**.

**Cập nhật vòng ba 2026-09-07.** Biên bản thứ ba `OD-20260907-03` (`precode/owner-decisions-03.md`, authority `AUTH-OWNER-20260907-04`, evidence `session_0156UBBHDSeC9soECzSVUb3U`) làm **ba** việc: phê chuẩn `AMD-ENT-owner-01` (§8.11), phê chuẩn `PROV-PC00-08` (§8), và mở lối vào Giai đoạn 2 (§8.12). Nó **không** mở quyền mạng, **không** gỡ cổng probe (`collector-probe.md` §6 mục 2–4), **không** cho phép đoán bốn dữ kiện `REQ-A6`, **không** phê chuẩn mục `PROVISIONAL` nào khác, và **không** giải `REQ-OQ03`.

**Cập nhật vòng bảy và vòng tám 2026-09-08.** Hai vòng này được `worker-WT` và `worker-WAI` ghi hiệu lực ngay khi chúng xảy ra (**§8.14.3** và **§8.15.1**); `PKT-PC00-FIX28` bổ sung **bản ghi song hành theo quy ước** để chúng có cùng hình dạng hồ sơ như các vòng khác — file độc lập, anchor `baseline.json`, authority trong `agent_profile/registry.json`. **Không** quyết lại điều gì; khi hai bên lệch thì **§8.14.3 / §8.15.1 thắng**. `OD-20260908-07` (`AUTH-OWNER-20260908-08`) **nới công cụ** tìm ba dữ kiện Telegram sang `WebSearch` — vẫn chỉ để **định vị nội dung của chính trang** `core.telegram.org/bots/api`, **không** để lấy một con số khác từ site khác; và chốt rằng người ký `REQ-A5` phải là **Owner đích thân**, nên `CR-PC06-OQ03-02` **giữ mở** qua hết vòng bảy. Nới quyền **không** tạo ra dữ kiện: vòng ba chạy dưới quyền mới và **cả ba dữ kiện vẫn `BLOCKED_DEPENDENCY`** (§8.14.3). `OD-20260908-08` (`AUTH-OWNER-20260908-09`) là **chữ ký `REQ-A5`** của Owner cho **riêng Anthropic**, trên **đúng ba trang có ngày hiệu lực**, kèm **chấp nhận tường minh** bảo đảm `TC-A5-01`; `CR-PC06-OQ03-02` **đóng**. Ba ranh giới phải giữ: chữ ký **hết hiệu lực** khi một trong ba trang đổi phiên bản (`ADR-0010`); **ký không phải bật** — `enabled = true` vẫn bị `B13` chặn (`ISO-03`/`ISO-05` chưa kiểm, `E3 NOT_RUN`, `REQ-AC16` vẫn `BLOCKED`); và câu hỏi **arXiv/OpenAlex/X có cho phép tái xử lý nội dung của họ hay không** vẫn **chưa ai trả lời** — Owner **gánh** bảo đảm ấy, không **giải** nó.

**Cập nhật vòng mười 2026-09-08.** Biên bản `OD-20260908-10` (`precode/owner-decisions-10.md`, authority `AUTH-OWNER-20260908-11`) trả lời **ba** câu hỏi mà các card Giai đoạn 5 nêu ra khi chạm phải một ràng buộc đã chốt. (1) `CR-TC-SAVED-04`: **cho phép** lưu một target chưa có analysis, kèm nhãn *"chưa phân tích"* là một **chuỗi cố định, không suy luận** — `AMD-B16` **không** bị nới, chỗ trống được **nói ra** chứ không được **lấp**. (2) `CR-TC-TGAUTH-02`: giữ `/save <id>` làm trigger văn bản thuần cho tới khi nút inline khả thi, ánh xạ vào `CMD-save` đã có — **không** lệnh Telegram thứ tư (`AMD-B10`, `F-PC00-01` giữ nguyên); đây là một đường vòng **có hạn**, tự hết vai khi `CR-PC07-04` được giải, và nó **không** giải `CR-PC07-04`. (3) `CR-TC-TGAUTH-04`: chat **đã liên kết** nhận một lời nhắc ba lệnh; chat **lạ vẫn im lặng, 0 outbound** — `AMD-B09` được bảo toàn nguyên vẹn. Hàng fixture quét biên **chưa** được sửa ở vòng này: nó thuộc **vòng hợp đồng kế tiếp**, một CR cho **PC08** (`CR-PC00-34`). Vòng mười **không** nâng trần claim của file nào và **không** đóng finding nào.

**Cập nhật 2026-09-08 (`PKT-PC00-FIX32`) — `CR-PC00-35` ĐÃ ĐƯỢC THI HÀNH.** `precode/adr/ADR-0011-frameworks-and-toolchain.md` nhận khối amendment **`AMD-ADR0011-01`** dưới `AUTH-OWNER-20260908-11` (chuỗi `OD-20260908-10` → ruling post-`A3-P4-R1`), sửa **ba** câu mô tả đã hết đúng: (a) phạm vi `mypy --strict` là **mọi cây mã sản phẩm Python** (`server/app`, `worker/app`, `collector/app`, `probe`) chứ không phải "lõi server" — `F-A3-P4-02` chỉ ra rằng cấu hình làm **đúng theo câu mơ hồ ấy** nên **23 file sản phẩm không được thứ gì kiểm kiểu**; (b) `tools/` **nay đã tồn tại** (`tools/backup_cli.py`), nên `CR-P0-03` mục 1 **đã được đáp ứng**; (c) `.gitignore` nay phủ `__pycache__/`. **Status của ADR giữ `accepted` và `ratified_by: OD-20260907-02` không đổi** — không lựa chọn kỹ thuật nào bị sửa, chỉ câu mô tả. Bản ghi CR đầy đủ theo định dạng §1 nằm ở `precode/change-control.md` §10. `ADR-0011` là file **card-pinned** ⇒ 19 card `STALE` theo `INV-06`, `worker-WP` re-pin epoch **P4b**. `F-A3-P4-02` **không** bị đóng ở đây.

**(Lịch sử) Sai lệch được phát hiện ở `PKT-PC00-FIX30`, khi đó ghi thành `CR-PC00-35`.** `tools/backup_cli.py` nay **đã tồn tại** trên đĩa (card `backup` của đợt Giai đoạn 4/6), trong khi `precode/adr/ADR-0011-frameworks-and-toolchain.md` vẫn còn câu *"`tools/` chưa được tạo"* — câu ấy đúng khi viết ở `PKT-PC00-FIX17` và **nay đã sai**. Phép kiểm hai chiều mà `FIX17` dựng ra (so câu trong ADR với thực tế trên đĩa) đã **bắt được** điều này thay vì để nó trôi. `ADR-0011` **không** nằm trong tập ghi của `PKT-PC00-FIX30`, nên PC00 **không** sửa nó ở đây; cần một packet nhỏ. Cho tới lúc đó, khi hai bên lệch thì **đĩa thắng**: cây thứ tám tồn tại, và `CR-P0-03` mục 1 nay đã được đáp ứng.

**Cập nhật vòng chín 2026-09-08.** Biên bản `OD-20260908-09` (`precode/owner-decisions-09.md`, authority `AUTH-OWNER-20260908-10`) **thay** điều kiện khởi động Giai đoạn 5 mà vòng năm đặt ra. Điều kiện cũ — *"một khi **năm** dữ kiện land"* — **chưa bao giờ thỏa** (2/5) và nay **không còn hiệu lực**; điều kiện mới là **khởi động có phạm vi**: các card Giai đoạn 5 được phép chạy **chỉ với tin nhắn văn bản thuần** — cắt tin theo giới hạn 4096 ký tự và điều tiết nhịp gửi, cả hai dựa trên **hai dữ kiện đã có trích dẫn nguyên văn** (§8.14.1). `parse_mode`, inline keyboard và nút mang `callback_data` **tường minh nằm ngoài phạm vi**, có `SG-01` canh, và **chưa được hiện thực** — **không** phải stub-rồi-giấu. `CR-PC07-04` **vẫn `PARTIALLY_RESOLVED`**, ba dữ kiện vẫn `BLOCKED_DEPENDENCY` (§8.14.3); vòng chín **không** giải chúng mà quyết định đi tiếp **mà không cần** chúng. Vì vậy `CR-PC00-31` được giải bằng cách **đổi điều kiện**, không phải bằng cách tuyên bố điều kiện cũ đã thỏa — ghi `condition_met: true` cho điều kiện cũ sẽ là một câu **sai kiểm được**, và `agent_profile/registry.json` vì thế lưu **cả hai** điều kiện kèm trạng thái của từng cái.

**Cập nhật vòng năm 2026-09-08.** Biên bản thứ năm `OD-20260908-05` (`precode/owner-decisions-05.md`, authority `AUTH-OWNER-20260908-06`, evidence `session_017CTbS7F4oTr4ZtFYkhdabD`) làm **hai** việc: **ủy quyền nghiên cứu** `REQ-OQ03` — Coordinator đề xuất, Owner phê duyệt ở một vòng sau — và cấp một quyền mạng **một lần, hẹp theo host, chỉ đọc tài liệu** dưới `core.telegram.org` cho `CR-PC07-04`, kèm lối vào Giai đoạn 5 **có điều kiện**: *"một khi **năm** dữ kiện land"*. Vòng này **không** mang nhãn `ACCEPTED (OD-20260908-05)` ở đâu cả — nó **giao việc**, không chấp nhận một phương án; nhãn `ACCEPTED` chỉ xuất hiện cho vòng **sáu** (§8.15). Nó **không** giải `REQ-OQ03` (vẫn `OWNER_DECISION_REQUIRED` tính đến vòng năm), **không** giải `REQ-A5` (cổng riêng, theo từng adapter, trước khi đặt `enabled = true`), **không** mở mạng nói chung (`api.telegram.org` bị cấm đích danh; không bot token; không gửi tin), **không** nâng trần claim của file nào và **không** đóng finding nào.

**Giai đoạn 5 CHƯA được gỡ chặn tính đến 2026-09-08.** Điều kiện Owner đặt là **năm** dữ kiện; sau **hai** vòng của `worker-WT` (§8.14.1, §8.14.2) mới có **hai** — ba dữ kiện còn lại (`callback_data`, parse mode + bảng escape, số nút mỗi hàng) vẫn `BLOCKED_DEPENDENCY`, nên `CR-PC07-04` là **`PARTIALLY_RESOLVED`**, không `CLOSED`. 2 ≠ 5, vì vậy PC00 **không** tuyên bố Giai đoạn 5 đủ điều kiện khởi động; kết luận ấy thuộc Coordinator/Owner (`CR-PC00-31`). Chi tiết dữ kiện, nguồn và lý do ba mục kia dừng nằm ở **§8.14** — nội dung của `worker-WT`, PC00 không chép lại.

## 1. Bảng tổng hợp B01–B17

| ID | Chủ đề | Status | decision_owner | Gói bị chặn | Gate bị chặn | Amendment | ADR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | Mốc freeze tag | RATIFIED (OD-20260907-01) | Owner | PC04, PC07 | G3 | AMD-B01 | ADR-0004 |
| B02 | Mô hình trạng thái run | RATIFIED (OD-20260907-01) | Owner | PC03 | G2 | AMD-B02 | ADR-0002 |
| B03 | Trạng thái gửi không xác định | RATIFIED (OD-20260907-01) | Owner | PC07 | G3 | AMD-B03 | ADR-0003 |
| B04 | Coverage, pending và backfill | RATIFIED (OD-20260907-01) | Owner | PC04 | G3 | AMD-B04 | ADR-0004 (liên đới) |
| B05 | Cam kết không lấy lại bài | RATIFIED (OD-20260907-01) | Owner | PC03, PC05 | G2 | AMD-B05 | ADR-0002 (liên đới) |
| B06 | Identity, alias, phiên bản, target | RATIFIED (OD-20260907-01) | Owner | PC02 | G2 | — (bổ sung, không sửa văn bản) | ADR-0009 |
| B07 | Khóa kết quả phân tích và generation | RATIFIED (OD-20260907-01) | Owner | PC02, PC06 | G2 | AMD-B07 | ADR-0008 |
| B08 | Timezone và timestamp | RATIFIED (OD-20260907-01) | Owner | PC03, PC04 | G2 | AMD-B08 | ADR-0007 |
| B09 | Ngoại lệ liên kết Telegram | RATIFIED (OD-20260907-01) | Owner | PC07 | G3 | AMD-B09 | — |
| B10 | Resume và tập lệnh Telegram | RATIFIED (OD-20260907-01) | Owner | PC03, PC07 | G3 | AMD-B10 | — |
| B11 | Backup và restore | RATIFIED (OD-20260907-01) | Owner | PC08 | G3 | AMD-B11 | ADR-0005 |
| B12 | Topology và Chrome profile | RATIFIED (OD-20260907-01) | Owner | PC01, PC05, PC06 | G1 | AMD-B12 | ADR-0001 |
| B13 | Phạm vi secret và cô lập CLI | RATIFIED (OD-20260907-01) | Owner | PC01, PC06, PC08 | G1 | — (bổ sung chính sách) | ADR-0010 |
| B14 | Mật độ vector | RATIFIED (OD-20260907-01) | Owner | PC04, PC09 | G3 | — (bổ sung định nghĩa) | — |
| B15 | Phạm vi bất biến 0 trùng | RATIFIED (OD-20260907-01) | Owner | PC02, PC09 | G2 | AMD-B15 | ADR-0009 |
| B16 | Tách tuyên bố và suy luận | RATIFIED (OD-20260907-01) | Owner | PC06 | G3 | AMD-B16 | — |
| B17 | Lúc enqueue summary | RATIFIED (OD-20260907-01) | Owner | PC04, PC06 | G3 | AMD-B17 | — |

## 2. Chi tiết từng blocker

### B01 — Mốc hiệu lực của bộ tag

- **Mâu thuẫn nguồn.** SRC-SPEC §3.4 hàng `C03/D-tag`: "Mốc hiệu lực tag theo **thời điểm gửi**: bộ tag lúc tạo báo cáo quyết định nội dung" — một hàng nêu hai mốc khác nhau (*gửi* và *tạo*). SRC-SPEC §9.2 lại ghi sau khi report được dựng thì "Không dựng lại; chỉ gửi lại". SRC-PLAN §3 B01 bổ sung: "tag có thể đổi khi Telegram đang retry".
- **PC-ĐX của kế hoạch.** "Chọn một thời điểm chốt: khuyên dùng transaction publish report; ghi `tag_config_version` bất biến."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Tag được đóng băng tại **transaction publish của báo cáo**. Report lưu `tag_config_version` bất biến. Delivery không bao giờ đổi nội dung đã publish. Cụm "thời điểm gửi" trong `C03/D-tag` được đọc lại là "thời điểm publish report".
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/schemas/report.schema.json`, `contracts/state/report.yaml`, `contracts/telegram/delivery.md`, `acceptance/fixtures/reporting/`.
- **Gate bị chặn.** G3 (PC04, PC07). Không chặn G0/G1.
- **Thay đổi oracle.** REQ-AC05 giữ nguyên kết quả nhưng mốc so sánh đổi từ "lúc gửi Telegram" sang "lúc commit publish"; thêm oracle mới: đổi tag sau publish nhưng trước delivery **không** làm đổi `report_item` và không làm đổi hash payload đã đóng.
- **Nếu Owner bác bỏ.** Nếu Owner thật sự muốn mốc theo lúc gửi thì PC04 và PC07 phải thiết kế thêm report revision và xử lý trường hợp đã gửi một phần; toàn bộ PC04/PC07 ở lại BLOCKED cho tới khi có thiết kế đó. Không có phương án nào cho phép giữ nguyên chữ "thời điểm gửi" mà vẫn giữ được I05.
- **Liên kết.** AMD-B01, ADR-0004, I05, REQ-CTAG, REQ-D23, REQ-D24, REQ-AC05, REQ-S8.1-03, REQ-S8.2-01, REQ-S8.2-02.

### B02 — Mô hình trạng thái của run

- **Mâu thuẫn nguồn.** SRC-SPEC §5.2 vẽ `reporting --> delivered` và `reporting --> delivered_partial` **bên trong** vòng đời run, trong khi SRC-SPEC §9.1 khẳng định "Trạng thái job và trạng thái gửi báo cáo là hai thứ độc lập". Ngoài ra `stopped_limit` (§9.1, REQ-AC03) vừa là điểm dừng vừa vẫn có thể sinh báo cáo.
- **PC-ĐX của kế hoạch.** "Tách phase/status/outcome của run; delivery độc lập. Ánh xạ rõ tên cũ sang trạng thái chuẩn." (SRC-PLAN §8.1)
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Áp dụng đúng mô hình SRC-PLAN §8.1: `phase` ∈ {collecting, enriching, analyzing, reporting}; `status` ∈ {queued, running, waiting_retry, needs_user, blocked, completed, failed, cancelled}; `outcome` ∈ {complete, partial, empty, failed, cancelled}; `stop_reason` là trường riêng. Delivery là vòng đời tách rời. Bảng ánh xạ enum cũ sang mới nằm ở AMD-B02.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/run.yaml`, `contracts/state/report.yaml`, `contracts/errors.yaml`, `contracts/ui/screens.yaml` (read model của Runs và Run detail).
- **Gate bị chặn.** G2 (PC03), kéo theo G3 cho PC07.
- **Thay đổi oracle.** REQ-AC03 đổi từ `run.status == stopped_limit` sang `status == completed AND stop_reason == limit_reached AND outcome ∈ {partial, complete}`. REQ-AC15 đổi từ so sánh ba enum sang so sánh ba cặp `(status, outcome, stop_reason)`; ràng buộc hiển thị của REQ-S8.3-01..03 không đổi.
- **Nếu Owner bác bỏ.** Giữ enum cũ thì `delivered` nằm trong run và I09 bị vi phạm ngay từ hợp đồng; PC03 và PC07 ở lại BLOCKED vì không có cách phân biệt "run xong nhưng chưa gửi" với "run xong và đã gửi".
- **Liên kết.** AMD-B02, ADR-0002, I09, I13, REQ-S5.2-01, REQ-S9.1-01, REQ-S9.1-02, REQ-AC03, REQ-AC15.

### B03 — Trạng thái gửi không xác định

- **Mâu thuẫn nguồn.** SRC-SPEC AC-14: "app vẫn giữ báo cáo đầy đủ và **không có tin nào bị gửi hai lần**", cùng §9.3 "`delivery` một hàng cho một (report, kênh)". SRC-PLAN §3.1 chỉ ra tài liệu Telegram Bot API `sendMessage` không có tham số idempotency key do client cung cấp, nên một hàng UNIQUE trong DB không chứng minh exactly-once ở mạng ngoài.
- **PC-ĐX của kế hoạch.** "Thêm `delivery.unknown`; dừng retry tự động khi không biết đã gửi chưa. Thay bảo đảm tuyệt đối bằng chính sách có thể kiểm chứng, cần người dùng duyệt amendment."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Thêm trạng thái `delivery.unknown`. Timeout hoặc mất kết nối sau điểm có thể đã gửi đưa delivery vào `unknown`; **không** retry tự động từ `unknown`; app hiển thị "chưa xác định" và Operator (Owner) quyết định có chấp nhận nguy cơ trùng. Digest nhiều phần dùng `delivery_part` với index, payload hash và receipt từng phần; phần `unknown` không được gửi lại chỉ vì tổng thể chưa `sent`.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/delivery.yaml`, `contracts/telegram/delivery.md`, `contracts/errors.yaml` (`TELEGRAM_SEND_UNCERTAIN`), `acceptance/fixtures/telegram/`.
- **Gate bị chặn.** G3 (PC07).
- **Thay đổi oracle.** REQ-AC14 đổi từ "không có tin nào bị gửi hai lần" (bảo đảm tuyệt đối, không kiểm chứng được) sang "không có lần gửi lặp **tự động**; mọi trạng thái không chắc chắn được hiện là `unknown` và cần thao tác tay của Owner". Thêm fixture: Telegram nhận tin rồi cắt response.
- **Nếu Owner bác bỏ.** Nếu Owner giữ nguyên chữ AC-14 thì PC07 không thể đạt `CONTRACT_READY`, vì không có bằng chứng nào chứng minh được exactly-once qua Telegram API; phạm vi delivery ở lại BLOCKED.
- **Liên kết.** AMD-B03, ADR-0003, I09, REQ-AC14, REQ-D38, REQ-S9.1-03, REQ-S9.2-05, REQ-S9.3-06.

### B04 — Coverage, pending và backfill

- **Mâu thuẫn nguồn.** SRC-SPEC D27 yêu cầu kỳ nối liền theo ngày phát hiện; D57 cấm gửi báo cáo rỗng ("chỉ ghi vào trạng thái run"); §10.4 nói mục vượt giới hạn "chờ đợt sau chứ không bị bỏ". Ba điều này va nhau: nếu kỳ rỗng không tạo report thì con trỏ coverage lấy từ đâu, và backlog AI nằm ngoài kỳ đã đóng thì được tính vào kỳ nào.
- **PC-ĐX của kế hoạch.** "Dùng sổ coverage độc lập report hiển thị; pending item và backfill ledger độc lập con trỏ kỳ. Chốt khi nào coverage tiến."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Coverage ledger là sổ authoritative, độc lập với việc có report hiển thị hay không. Sổ pending item và sổ backfill là hai sổ riêng, không phụ thuộc con trỏ kỳ. Coverage chỉ tiến tại **commit publish**, kể cả với kỳ rỗng (kỳ rỗng có coverage record nhưng không sinh digest). Backfill N ngày được tiêu thụ đúng một lần cho mỗi subscription activation đã định danh; crash của builder không tiêu thụ backfill.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/state/report.yaml`, `acceptance/fixtures/reporting/`.
- **Gate bị chặn.** G3 (PC04).
- **Thay đổi oracle.** REQ-AC08 thêm oracle: sau một kỳ rỗng, `coverage_from` của kỳ kế tiếp vẫn bằng `coverage_to` của kỳ rỗng (không hở). REQ-D57 giữ nguyên hành vi không gửi digest nhưng thêm hàng coverage.
- **Nếu Owner bác bỏ.** Nếu coverage buộc phải suy ra từ danh sách report hiển thị thì mọi kỳ rỗng tạo lỗ hổng; I06 không thể giữ và PC04 ở lại BLOCKED.
- **Liên kết.** AMD-B04, I06, REQ-D27, REQ-D28, REQ-D57, REQ-S10.4-03, REQ-AC08, REQ-OQ04.

### B05 — Cam kết "không lấy lại bài đã có"

- **Mâu thuẫn nguồn.** SRC-SPEC §9.2 và AC-04: "Tiếp từ con trỏ, không lấy lại bài đã có". SRC-PLAN §3 B05: "cursor của feed động chưa chứng minh ổn định"; SRC-PLAN §8.1: "Nếu con trỏ feed mất hiệu lực, cho phép đọc lại theo recovery policy và dedup ở ingest".
- **PC-ĐX của kế hoạch.** "Cam kết ingest không trùng; việc đọc lại có thể cần thiết. Checkpoint chỉ chứa dữ liệu server đã ACK; ghi rõ giới hạn bao phủ X."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Cam kết được phát biểu lại là **không ingest trùng theo `x_post_id`**, không phải "không bao giờ đọc lại trang". Việc đọc lại được phép theo recovery policy. Checkpoint chỉ chứa dữ liệu server đã ACK. Giới hạn bao phủ X được ghi vào metadata của run; `completed` không có nghĩa đã quét đủ toàn bộ X.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/run.yaml`, `contracts/http/openapi.yaml`, `contracts/schemas/ingest-batch.schema.json`, `contracts/schemas/ingest-receipt.schema.json`, `acceptance/fixtures/collection/`.
- **Gate bị chặn.** G2 (PC03), G3 (PC05).
- **Thay đổi oracle.** REQ-AC04 vế cuối đổi từ đếm số lần tải trang sang đếm số hàng `post` sau replay: sau resume, `COUNT(post)` không tăng cho các `x_post_id` đã có, và receipt cũ được trả lại nguyên vẹn. Bổ sung oracle âm: request count **không** phải oracle.
- **Nếu Owner bác bỏ.** Giữ nguyên chữ "không lấy lại bài đã có" thì phải chứng minh cursor của X ổn định — điều SRC-PLAN xếp vào loại không kiểm chứng được trước; PC05 ở lại BLOCKED và probe A1 không có tiêu chí pass rõ ràng.
- **Liên kết.** AMD-B05, I02, REQ-AC04, REQ-S9.2-01, REQ-S5.4-01, REQ-A1, REQ-A7.

### B06 — Identity, alias, phiên bản và target

- **Mâu thuẫn nguồn.** SRC-SPEC §7.1 định nghĩa `work` với `doi` UNIQUE và `arxiv_id` UNIQUE, nhưng hai bản ghi có thể đã tồn tại rồi mới biết là cùng công trình. D33 tạo mục "chỉ có post" mà §7.1 không có model analysis cho post-only; `saved_item` dùng `UNIQUE(owner, work/post)` mơ hồ.
- **PC-ĐX của kế hoạch.** "Chốt identity/alias merge, work version và target phân biệt work/post. Không coi hai UNIQUE là đủ giải mọi trùng lặp."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Mô hình identity gồm bảng alias và audit trail cho mỗi lần merge; `work` có phiên bản (arXiv vN là phiên bản, không phải công trình khác); `target` là tagged union `work | post`, dùng thống nhất cho Saved, analysis và report item.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/data/entities.yaml`, `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/schemas/target.schema.json`, `acceptance/fixtures/identity/`.
- **Gate bị chặn.** G2 (PC02).
- **Thay đổi oracle.** REQ-AC07 và REQ-AC13 thêm oracle: alias map sau merge, provenance list giữ đủ nguồn, và Saved của target post-only vẫn bị ràng buộc duy nhất. Không có văn bản đặc tả nào bị thay; đây là bổ sung định nghĩa.
- **Nếu Owner bác bỏ.** Không có phương án thay thế: nếu chỉ dựa vào hai cột UNIQUE thì mọi post-only mất khóa duy nhất và REQ-AC13 không có oracle. Phạm vi PC02 ở lại BLOCKED.
- **Liên kết.** ADR-0009, I03, I08, REQ-D17, REQ-D33, REQ-S9.2-02, REQ-S9.3-05, REQ-S9.3-09, REQ-AC07, REQ-AC13.

### B07 — Khóa kết quả phân tích và generation

- **Mâu thuẫn nguồn.** SRC-SPEC D25 "Phân tích và summary tạo **một lần** cho mỗi công trình rồi tái sử dụng" (XN) đứng cạnh D26 "Phân tích lại chỉ khi người dùng bấm tay, hoặc paper có phiên bản mới; giữ bản cũ" (ĐX). §7.1 `analysis` chỉ có "phiên bản" mà không có source fingerprint hay task key.
- **PC-ĐX của kế hoạch.** "Định nghĩa một kết quả hợp lệ mỗi target/version/task/input/prompt contract; reanalysis có generation mới. Attempt lỗi không tính là kết quả hoàn thành."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Analysis key gồm: canonical id của target, source version/fingerprint, task type, phiên bản prompt/schema và generation. Mỗi key có tối đa **một** kết quả hợp lệ. Reanalysis tạo generation mới. Attempt thất bại hoặc không xác định không phải kết quả. Đổi tag **không** đổi key. Đổi provider/model không tự invalidate; giữ kết quả cũ tới khi Owner yêu cầu reanalysis.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/data/entities.yaml`, `contracts/ai/tasks.yaml`, `contracts/schemas/analysis-result.schema.json`, `contracts/state/analysis.yaml`.
- **Gate bị chặn.** G2 (PC02), G3 (PC06).
- **Thay đổi oracle.** REQ-AC06 chuyển từ "không phát sinh lần gọi AI nào" sang "provider call counter delta bằng 0 **cho cùng analysis key và generation**"; reanalysis cố ý vẫn được phép tăng counter.
- **Nếu Owner bác bỏ.** Nếu giữ "một lần cho mỗi công trình" theo nghĩa đen thì D26 (phân tích lại) không thực hiện được và mọi retry sau lỗi cũng vi phạm; PC06 ở lại BLOCKED.
- **Liên kết.** AMD-B07, ADR-0008, I04, REQ-D25, REQ-D26, REQ-S7.3-02, REQ-S10.4-02, REQ-AC06.

### B08 — Timezone và timestamp

- **Mâu thuẫn nguồn.** SRC-SPEC D56 "Timezone lấy theo máy chạy app" (UQ). SRC-PLAN §3 B08: "mơ hồ vì browser, server, máy collector khác nhau". D13 và D15 phụ thuộc mốc giờ để tính "sớm nhất được chạy" và gộp đợt quá hạn.
- **PC-ĐX của kế hoạch.** "Lưu một IANA timezone do owner xác nhận; timestamps chuẩn UTC; chốt quy tắc DST và gộp lịch."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Một IANA timezone duy nhất lưu trong settings, do Owner xác nhận; mặc định tạm `Asia/Ho_Chi_Minh`. Mọi timestamp lưu ở UTC RFC 3339 với độ chính xác **mili giây**, tie-break bằng ingest sequence. Quy tắc DST và catch-up do PC03 viết thành bảng.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/state/run.yaml`, `contracts/reporting/time-and-tags.md`, `contracts/ui/screens.yaml` (Settings), `contracts/data/entities.yaml`.
- **Gate bị chặn.** G2 (PC03), G3 (PC04).
- **Thay đổi oracle.** REQ-AC02 cần một mốc giờ xác định để tính "quá hạn"; oracle đổi từ giờ máy sang giờ theo timezone đã cấu hình, với fake-clock cố định.
- **Nếu Owner bác bỏ.** `Asia/Ho_Chi_Minh` chỉ là giá trị tạm; nếu Owner ở múi khác thì mọi fixture lịch phải dựng lại. Bản thân quyết định "một timezone lưu trong settings" không có phương án thay thế nào giữ được tính xác định.
- **Liên kết.** AMD-B08, ADR-0007, REQ-D56, REQ-D13, REQ-D15, REQ-S8.2-08, REQ-AC02, REQ-OQ06.

### B09 — Ngoại lệ liên kết Telegram

- **Mâu thuẫn nguồn.** SRC-SPEC §11.3: "Tin từ chat ID chưa liên kết bị **bỏ im lặng** — không trả lời gì". SRC-SPEC §5.1 bước 4: "Sinh mã liên kết Telegram trong app, gửi mã cho bot" — tức bot **phải** xử lý một thông điệp từ chat chưa liên kết.
- **PC-ĐX của kế hoạch.** "Chốt ngoại lệ hẹp cho yêu cầu liên kết hợp lệ, kiểm mã trước; mọi lệnh khác từ chat lạ bỏ im lặng."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Một ngoại lệ hẹp duy nhất: thông điệp từ chat chưa liên kết **khớp đúng định dạng mã liên kết** được đối chiếu với các mã chưa hết hạn và chưa dùng. Mọi thứ khác từ chat chưa liên kết bị bỏ im lặng. Mã sai, hết hạn hoặc đã dùng cũng bị bỏ im lặng (không phản hồi lỗi).
- **Hợp đồng/file bị ảnh hưởng.** `contracts/telegram/commands.yaml`, `contracts/ops/secrets.md`, `acceptance/fixtures/telegram/`.
- **Gate bị chặn.** G3 (PC07).
- **Thay đổi oracle.** REQ-AC18 cần thêm case dương tính: thông điệp mang mã hợp lệ **được** xử lý. Oracle "outbound call count = 0" chỉ áp cho các thông điệp không phải mã liên kết hợp lệ.
- **Nếu Owner bác bỏ.** Không có phương án khác cho luồng thiết lập lần đầu ngoài việc nhập chat ID bằng tay trong app; nếu Owner chọn hướng đó thì §5.1 bước 4 phải viết lại và PC07 ở lại BLOCKED tới khi có văn bản mới.
- **Liên kết.** AMD-B09, REQ-D35, REQ-S5.1-04, REQ-S11.3-01, REQ-S11.3-02, REQ-S11.2-04, REQ-AC18.

### B10 — Resume và tập lệnh Telegram

- **Mâu thuẫn nguồn.** SRC-SPEC §5.4 bước 4: "Bấm 'tiếp tục' trong app **hoặc gửi lệnh trạng thái/chạy ngay**". SRC-SPEC §9 và §5.4 bước 5: run không tự tiếp tục khi hạn chế còn. SRC-SPEC §11.3: "chỉ chat ID đã liên kết ra được **3 lệnh** của D36", trong khi D37 lại yêu cầu "có lệnh hủy liên kết".
- **PC-ĐX của kế hoạch.** "`status` không mutation; `run-now` không vượt `needs_user`. Khuyên nút resume riêng trong app; không tự thêm lệnh Telegram thứ tư."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** `status` là lệnh chỉ đọc, không gây mutation. `run-now` không bao giờ ghi đè một run đang `needs_user`. Resume là hành động riêng trong app. Không thêm lệnh Telegram thứ tư; **hủy liên kết cũng là hành động trong app** (xem finding F-PC00-01).
- **Hợp đồng/file bị ảnh hưởng.** `contracts/telegram/commands.yaml`, `contracts/state/run.yaml`, `contracts/ui/screens.yaml` (Runs, Run detail, Settings).
- **Gate bị chặn.** G3 (PC07), G2 liên đới (PC03).
- **Thay đổi oracle.** REQ-AC04 thêm oracle âm: gửi `status` hoặc `run-now` khi run đang `needs_user` **không** làm đổi bất kỳ hàng nào; chỉ hành động resume trong app mới cấp lease mới.
- **Nếu Owner bác bỏ.** Nếu Owner muốn resume qua Telegram thì cần lệnh thứ tư và §11.3 ("3 lệnh") phải sửa; phạm vi lệnh Telegram ở lại BLOCKED tới khi có quyết định.
- **Liên kết.** AMD-B10, REQ-D36, REQ-D37, REQ-S5.4-04, REQ-S11.3-03, REQ-S11.3-04, REQ-AC04.

### B11 — Backup và restore

- **Mâu thuẫn nguồn.** SRC-SPEC D58 và §7.3: "Backup: copy file SQLite. Restore: đặt file về chỗ cũ". SRC-PLAN §3.1: "WAL là một phần trạng thái bền của DB; tách file DB khỏi WAL có thể mất transaction đã commit". Đặc tả cũng không nói gì về khôi phục queue và token.
- **PC-ĐX của kế hoạch.** "Chọn backup nhất quán và restore drill có khóa side effect. Không dùng copy file DB đang hoạt động làm bằng chứng đủ."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Backup dùng SQLite Online Backup API hoặc `VACUUM INTO` để tạo snapshot nhất quán (an toàn với WAL), kèm manifest chứa hash DB, phiên bản schema, artifact và cấu hình embedding. Restore phải qua drill vào môi trường sạch, có khóa side effect: dispatcher và worker claim bị dừng, outbox cũ không replay, `first_announced` không bị reset trước khi kiểm tra.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/ops/backup-restore.md`, `contracts/ops/deployment.md`, `contracts/state/storage.yaml`, `acceptance/fixtures/recovery/`.
- **Gate bị chặn.** G3 (PC08).
- **Thay đổi oracle.** REQ-AC12 thêm oracle sau restore: hash snapshot của Saved không đổi, và số hàng report/ledger khớp manifest. Thêm oracle âm cho `RESTORE_UNVERIFIED`: trước khi verify không có side effect nào chạy.
- **Nếu Owner bác bỏ.** Copy file DB đang ghi vẫn chạy được trong nhiều trường hợp nhưng không thể dùng làm bằng chứng khôi phục; nếu Owner giữ D58 nguyên văn thì PC08 chỉ đạt tối đa mức mô tả, không đạt `CONTRACT_READY` cho backup/restore.
- **Liên kết.** AMD-B11, ADR-0005, I15, REQ-D58, REQ-S7.3-04, REQ-S6.4-01, REQ-AC12, REQ-S13-09.

### B12 — Topology và Chrome profile

- **Mâu thuẫn nguồn.** SRC-SPEC D09 (profile riêng), D08 (collector đẩy qua API), D42 (LLM cùng máy collector) và D50 (embedding ở server) đều còn **ĐX**. Đồng thời sơ đồ §6.2 có cạnh `COL --> AW`, tức collector đưa dữ liệu **thẳng** cho analysis worker, mâu thuẫn với D08 và với I02.
- **PC-ĐX của kế hoạch.** "Chốt profile và topology. Khuyên analysis nhận task từ server sau ingest commit, không nhận dữ liệu chưa commit từ collector."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Giữ D09 (Chrome profile riêng của dự án), D08 (chỉ qua API có xác thực), D42 (analysis worker trên máy cá nhân), D50 (embedding ở server). Analysis worker nhận **task từ server sau ingest commit**, không nhận dữ liệu trực tiếp từ collector; cạnh `COL --> AW` của §6.2 bị xóa.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/ports.yaml`, `contracts/ops/deployment.md`, `contracts/http/openapi.yaml`.
- **Gate bị chặn.** G1 (PC01), kéo theo PC05 và PC06.
- **Thay đổi oracle.** Thêm negative case bắt buộc: collector gọi thẳng analysis worker bị từ chối bởi capability registry (default deny). REQ-AC01 và REQ-AC16 không đổi kết quả nhưng đường đi được kiểm bằng import/dependency rules và API auth tests.
- **Nếu Owner bác bỏ.** D09 vẫn là câu hỏi chặn M0 (REQ-OQ01): nếu Owner muốn dùng profile Chrome mặc định thì §11.2 (phiên X trong profile riêng) phải sửa và rủi ro tài khoản tăng; toàn bộ M0 ở lại BLOCKED tới khi Owner trả lời.
- **Liên kết.** AMD-B12, ADR-0001, I02, REQ-D08, REQ-D09, REQ-D42, REQ-D50, REQ-S6.1-02, REQ-S6.1-03, REQ-S6.2-01, REQ-OQ01.

### B13 — Phạm vi secret và cô lập CLI/ACP

- **Mâu thuẫn nguồn.** SRC-SPEC D41/D43/§10.2 mô tả hai họ provider nhưng không chốt worker được nhận key nào, trong bao lâu, và CLI được phép gọi tool gì. §11.4 lại yêu cầu "Nội dung ngoài không được ... gọi tool, đọc secrets".
- **PC-ĐX của kế hoạch.** "Chốt secret access theo task; CLI không tool/file/network action ngoài inference được phép; nếu adapter không cô lập được thì không bật."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Worker chỉ nhận credential của **đúng provider cho task được giao**, thời hạn ngắn. Adapter CLI/ACP phải chạy với tool, file và network bị tắt ngoài phần inference. Nếu không kiểm chứng được mức cô lập cho một provider thì adapter của provider đó **giữ trạng thái disabled**.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/capabilities.yaml`, `contracts/ai/providers.yaml`, `contracts/ops/secrets.md`, `acceptance/fixtures/ai/`.
- **Gate bị chặn.** G1 (PC01), G3 (PC06, PC08).
- **Thay đổi oracle.** REQ-AC16 (không có API key) chỉ pass nếu ít nhất một adapter CLI đã qua kiểm cô lập; nếu mọi adapter CLI bị disabled thì REQ-AC16 chuyển `BLOCKED`, không phải `FAIL`. REQ-AC17 thêm oracle: canary secret trong transcript và audit số lần gọi tool bằng 0.
- **Nếu Owner bác bỏ.** Nếu Owner yêu cầu bật adapter chưa kiểm cô lập thì I11 bị vi phạm; PC06 và PC08 phải ghi `ACCEPTED_RISK` có chữ ký của Owner, không được ghi là đã giải quyết.
- **Liên kết.** ADR-0010, I11, I14, REQ-D41, REQ-D43, REQ-D51, REQ-S10.2-02, REQ-S11.4-03, REQ-A5, REQ-AC16, REQ-AC17.

### B14 — Mật độ vector cho khối "hướng đang nổi"

- **Mâu thuẫn nguồn.** SRC-SPEC D53 đưa khối "hướng đang nổi" vào MVP nhưng trạng thái vẫn **ĐX**, và không có thuật toán, cửa sổ so sánh, ngưỡng hay cỡ mẫu tối thiểu. D54 yêu cầu nhãn "ứng viên để đọc sâu". A4 chưa được kiểm chứng.
- **PC-ĐX của kế hoạch.** "Định nghĩa phép đo và tập đánh giá. Thiếu dữ liệu → insufficient evidence, không tự gọi là 'hướng nổi'."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** PC04 định nghĩa thuật toán, cửa sổ so sánh, ngưỡng, cỡ mẫu tối thiểu, cold-start và tie-break. Dữ liệu không đủ thì kết quả là `insufficient_evidence`, tuyệt đối không gọi là "hướng đang nổi". Mọi tham số là PROVISIONAL cho tới khi đánh giá A4 có dữ liệu 3–4 kỳ.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/selection.md`, `contracts/schemas/report.schema.json`, `acceptance/scenarios.yaml`, `precode/gates.yaml`.
- **Gate bị chặn.** G3 (PC04), G4 (PC09).
- **Thay đổi oracle.** Không có AC nào bị sửa; bổ sung oracle mới: với fixture dưới cỡ mẫu tối thiểu, khối hướng nổi phải rỗng và mang nhãn `insufficient_evidence`.
- **Nếu Owner bác bỏ.** Nếu Owner muốn giữ khối hướng nổi mà không chấp nhận trạng thái `insufficient_evidence` thì D52/D54 không có oracle tái lập được; PC04 và PC09 ở lại BLOCKED cho phần này. Lưu ý D53 vẫn là mục P0 **còn ĐX** — xem §4.
- **Liên kết.** REQ-D53, REQ-D54, REQ-A4, REQ-S10.1-04, REQ-S10.3-04, REQ-S1.4-01, REQ-S1.4-02.

### B15 — Phạm vi của bất biến "0 trùng"

- **Mâu thuẫn nguồn.** SRC-SPEC §1.4 đặt chỉ số vận hành "0 trường hợp trùng" ở trạng thái **Đã xác nhận**; D17/D29/AC-07 giả định gộp được bằng DOI/arXiv ID. Nhưng metadata có thể thiếu hoặc mâu thuẫn (D33, §9.3 hàng arXiv/OpenAlex lỗi).
- **PC-ĐX của kế hoạch.** "Chốt phạm vi invariant 0 trùng theo canonical identity đã biết; xung đột đưa `identity_conflict` và giữ nguồn, không merge đoán."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Bất biến "0 trùng" chỉ có nghĩa trên phạm vi **canonical identity đã biết** (DOI, arXiv ID, hoặc dạng chuẩn hóa đã định nghĩa). Xung đột đưa vào trạng thái quarantine `identity_conflict`, giữ mọi nguồn, không merge đoán. Trùng khoa học chưa xác định ID được **đo và báo cáo**, không tuyên bố đã giải bằng ràng buộc UNIQUE.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/data/identity.md`, `contracts/data/invariants.md`, `acceptance/fixtures/identity/`, `acceptance/traceability.csv`.
- **Gate bị chặn.** G2 (PC02), G4 (PC09).
- **Thay đổi oracle.** REQ-S1.4-03 đổi từ "0 trường hợp trùng" (tuyệt đối) sang "0 trường hợp trùng **trong phạm vi canonical identity đã biết**, cộng một số đếm riêng cho `identity_conflict` đang chờ xử lý". REQ-AC07 thêm case: hai alias mâu thuẫn không được tính là hai hướng chắc chắn.
- **Nếu Owner bác bỏ.** Giữ chữ "0 trường hợp trùng" tuyệt đối thì chỉ số này không đo được và PC09 không thể lập traceability cho nó.
- **Liên kết.** AMD-B15, ADR-0009, I03, I07, REQ-S1.4-03, REQ-D17, REQ-D29, REQ-AC07, REQ-AC09.

### B16 — Tách tuyên bố của tác giả và suy luận của AI

- **Mâu thuẫn nguồn.** SRC-SPEC D20 yêu cầu "điểm khác với cái đã có" cho mọi mục, kể cả khi chỉ có một post. AC-11 gộp mọi phát biểu về tính mới thành "suy luận". §10.3 lại yêu cầu tách ba loại phát biểu.
- **PC-ĐX của kế hoạch.** "Phân biệt tuyên bố tính mới của tác giả và suy luận AI; thiếu nguồn so sánh thì ghi thiếu, không bịa baseline."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Đầu ra phân tích tách ba trường: `author_claim`, `source_verified`, `ai_inference`. Khi không có nguồn so sánh thì ghi `comparator: unknown`; tuyệt đối không bịa baseline.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/ai/grounding.md`, `contracts/schemas/analysis-result.schema.json`, `acceptance/fixtures/ai/`.
- **Gate bị chặn.** G3 (PC06).
- **Thay đổi oracle.** REQ-AC11 đổi từ "mọi phát biểu về tính mới được trình bày là suy luận" sang "mỗi phát biểu mang đúng một nhãn trong ba loại; phát biểu không có nguồn kiểm chứng được **phải** nằm ở `ai_inference`; thiếu comparator thì trường `comparator` bằng `unknown`".
- **Nếu Owner bác bỏ.** Giữ nguyên AC-11 thì tuyên bố của tác giả bị hạ cấp thành suy luận của AI, làm mất thông tin và mâu thuẫn với §10.3; PC06 ở lại BLOCKED cho phần grounding.
- **Liên kết.** AMD-B16, REQ-D20, REQ-AC11, REQ-S10.3-02, REQ-S10.3-06.

### B17 — Lúc enqueue summary và report partial

- **Mâu thuẫn nguồn.** SRC-SPEC §2.1 mục 6 yêu cầu summary "cho **mọi mục**"; §10.1 lại giới hạn "Mọi mục **vào báo cáo**". Vì tag đổi được nên report builder có thể chọn thêm target chưa có summary.
- **PC-ĐX của kế hoạch.** "Chốt lúc enqueue summary và cách report partial/pending; không báo completed nếu các mục còn thiếu bị mất khỏi hàng đợi."
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Task summary được enqueue cho các target **được report builder chọn tại thời điểm dựng báo cáo**. Report mang `quality: partial` kèm danh sách pending tường minh khi có mục thiếu summary; `complete` chỉ khi mọi mục được chọn đều đã có summary hoặc được đánh dấu pending một cách tường minh.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/reporting/selection.md`, `contracts/ai/tasks.yaml`, `contracts/state/report.yaml`, `contracts/schemas/report.schema.json`.
- **Gate bị chặn.** G3 (PC04, PC06).
- **Thay đổi oracle.** REQ-P0-06 được đọc lại theo §10.1 (mục vào báo cáo), không phải mọi post trong kho. REQ-AC10 thêm oracle âm: mục thiếu summary không bị ẩn khỏi report mà hiện ở danh sách pending.
- **Nếu Owner bác bỏ.** Nếu Owner muốn summary cho **mọi** mục trong kho thì chi phí AI tăng theo số bài chứ không theo số mục báo cáo, mâu thuẫn §10.4; phạm vi PC06 phải tính lại ngân sách trước khi tiếp tục.
- **Liên kết.** AMD-B17, REQ-P0-06, REQ-D19, REQ-S10.1-03, REQ-S10.4-03, REQ-AC10.

## 3. Amendment

Mỗi amendment ghi: **Trước** (trích nguyên văn nguồn), **Sau** (văn bản đề xuất), **Vì sao**, **Bảo đảm thay thế**, **Test/oracle chứng minh**, **REQ bị ảnh hưởng**. Tất cả nay ở trạng thái **`ACCEPTED (OD-20260907-01)`** — Owner đã phê chuẩn ngày 2026-09-07 (`precode/owner-decisions.md`). Chúng vẫn **chưa** được áp vào `precode/source/spec-v0.2.md`: bản nguồn là bất biến, và việc phát hành đặc tả v0.3 là công việc riêng chưa được giao.

**Mục này chứa HAI loại bản ghi, và chúng không được lẫn nhau.**

| Loại | Tiền tố | Nó nói gì | Có văn bản "Sau" không |
| --- | --- | --- | --- |
| **Amendment** | `AMD-B<nn>` | Câu chữ đặc tả **cần được thay** vì nó mâu thuẫn, thiếu hoặc sai phạm vi. Đề xuất một văn bản thay thế. | **Có** |
| **Đính chính tiền đề** | `AMD-SPEC-<REQ>-<nn>` | Câu chữ đặc tả **đúng như một bản ghi lịch sử** nhưng **tiền đề thực tế** của nó nay đã được biết là sai, do một dữ kiện bên ngoài. Không đề xuất thay thế câu nào. | **Không** — xem ô "Sau" của từng mục |

Cả hai loại đều **không** sửa `precode/source/spec-v0.2.md` hay `research-radar-spec.md`. Khác biệt là ở chỗ:
với `AMD-B<nn>`, một đặc tả v0.3 tương lai **sẽ** viết lại câu đó; với `AMD-SPEC-…`, câu đó có thể được giữ
nguyên và **đọc theo nghĩa lịch sử** — nó ghi đúng điều người viết tin tại thời điểm viết.

### AMD-B01 — Mốc freeze tag

- **Trước** (SRC-SPEC §3.4, hàng `C03/D-tag`): "Mốc hiệu lực tag theo **thời điểm gửi**: bộ tag lúc tạo báo cáo quyết định nội dung".
- **Sau:** "Mốc hiệu lực tag theo **thời điểm publish báo cáo**: bộ tag đang hiệu lực tại transaction publish quyết định nội dung. Báo cáo lưu `tag_config_version` bất biến. Việc gửi (delivery) không bao giờ làm đổi nội dung đã publish."
- **Vì sao:** hàng gốc nêu hai mốc khác nhau trong cùng một câu; nếu lấy mốc "gửi" thì retry Telegram có thể rơi vào bộ tag khác và nội dung đã publish sẽ đổi.
- **Bảo đảm thay thế:** nội dung báo cáo bất biến sau publish (I05); mọi thay đổi tag sau publish chỉ ảnh hưởng kỳ sau.
- **Test/oracle:** đổi tag ngay trước CAS commit thì build bị abort/rebuild (`TAG_VERSION_STALE`); đổi tag sau publish trước delivery thì `report_item` và payload hash không đổi.
- **REQ ảnh hưởng:** REQ-CTAG, REQ-D23, REQ-D24, REQ-AC05, REQ-S8.1-03, REQ-S8.2-01, REQ-S8.2-02, REQ-S9.2-04.

### AMD-B02 — Mô hình trạng thái run

- **Trước** (SRC-SPEC §9.1): "Run | `queued` → `collecting` → `analyzing` → `reporting` → `done` · nhánh: `needs_user`, `stopped_limit`, `failed`, `failed_partial`"; và (SRC-SPEC AC-03): "run chuyển `stopped_limit`".
- **Sau:** run có bốn trường: `phase` ∈ {`collecting`, `enriching`, `analyzing`, `reporting`}; `status` ∈ {`queued`, `running`, `waiting_retry`, `needs_user`, `blocked`, `completed`, `failed`, `cancelled`}; `outcome` ∈ {`complete`, `partial`, `empty`, `failed`, `cancelled`}; `stop_reason` (ví dụ `limit_reached`, `captcha`, `session_expired`, `source_blocked`, `storage_unavailable`, `worker_lost`). AC-03 đọc lại: "run chuyển `status = completed`, `stop_reason = limit_reached`, checkpoint và tiến độ được lưu".
- **Bảng ánh xạ enum cũ sang mới:**

| Enum cũ (SRC-SPEC) | Mô hình mới |
| --- | --- |
| `queued` | `status = queued` |
| `collecting` | `status = running`, `phase = collecting` |
| `analyzing` | `status = running`, `phase = analyzing` |
| `reporting` | `status = running`, `phase = reporting` |
| `done` | `status = completed`, `outcome = complete` |
| `needs_user` | `status = needs_user` |
| `stopped_limit` | `status = completed`, `stop_reason = limit_reached`, `outcome ∈ {partial, complete}` |
| `failed` | `status = failed`, `outcome = failed` |
| `failed_partial` | `status = completed`, `outcome = partial` |
| `delivered` (§5.2) | **không thuộc run**; ánh xạ sang `delivery.status = sent` |
| `delivered_partial` (§5.2) | **không thuộc run**; ánh xạ sang `delivery.status ∈ {failed, unknown}` trong khi run giữ `outcome` của chính nó |
| *(không có)* | `status = blocked` (X chặn hoặc thiếu capability bắt buộc) |
| *(không có)* | `outcome = empty` (không có mục phù hợp, không có lỗi thiếu dữ liệu) |

- **Vì sao:** §5.2 đặt trạng thái gửi bên trong vòng đời run, mâu thuẫn trực tiếp với §9.1; `stopped_limit` trộn lẫn "đã dừng" với "kết quả ra sao".
- **Bảo đảm thay thế:** I09 (Telegram lỗi không làm run thất bại) và I13 (empty/incomplete/failed/unknown hiển thị riêng) trở nên kiểm chứng được.
- **Test/oracle:** transition lint trên `contracts/state/run.yaml`; ba run của REQ-AC15 cho ra ba bộ `(status, outcome, stop_reason)` khác nhau; không transition nào từ trạng thái terminal còn side effect.
- **REQ ảnh hưởng:** REQ-S5.2-01, REQ-S9.1-01, REQ-S9.1-02, REQ-AC03, REQ-AC15, REQ-D14, REQ-S8.3-01..03, REQ-S9.3-02, REQ-S9.3-07.

### AMD-B03 — Trạng thái delivery `unknown`

- **Trước** (SRC-SPEC AC-14): "Then app vẫn giữ báo cáo đầy đủ và **không có tin nào bị gửi hai lần**"; (SRC-SPEC §9.1): "Delivery | `pending` → `sent` · nhánh: `retrying`, `failed`".
- **Sau:** delivery có thêm trạng thái `unknown`. AC-14 đọc lại: "Then app vẫn giữ báo cáo đầy đủ, **không có lần gửi lặp tự động**, và mọi kết quả không xác định được hiện là `unknown` để Operator quyết định". Enum: `pending` → `sending` → `sent`; nhánh `retry_wait`, `failed`, `unknown`, `cancelled`.
- **Vì sao:** Telegram Bot API `sendMessage` không nhận idempotency key từ client (SRC-PLAN §3.1), nên ràng buộc UNIQUE trong SQLite không chứng minh exactly-once ở mạng ngoài.
- **Bảo đảm thay thế:** không retry tự động từ `unknown`; digest nhiều phần lưu `delivery_part` với receipt riêng; app luôn giữ báo cáo đầy đủ bất kể delivery.
- **Test/oracle:** mô phỏng Telegram nhận tin rồi cắt response → delivery vào `unknown`, số lần gọi mạng tiếp theo bằng 0; recipient bị revoke → `failed` mà report hash không đổi.
- **REQ ảnh hưởng:** REQ-AC14, REQ-D38, REQ-S9.1-03, REQ-S9.2-05, REQ-S9.3-06, REQ-S5.3-02, REQ-S5.4-02.

### AMD-B04 — Coverage record cho kỳ rỗng

- **Trước** (SRC-SPEC §3.5, D57): "Không gửi báo cáo rỗng; chỉ ghi vào trạng thái run".
- **Sau:** "Không gửi báo cáo rỗng. Kỳ rỗng vẫn ghi **một hàng coverage** trong sổ coverage authoritative và ghi vào trạng thái run; sổ pending item và sổ backfill độc lập với con trỏ kỳ."
- **Vì sao:** nếu kỳ rỗng không để lại dấu vết nào ngoài trạng thái run thì `coverage_from` của kỳ sau không có nguồn, tạo lỗ hổng hoặc chồng lấn, vi phạm D27 và I06.
- **Bảo đảm thay thế:** các cửa sổ coverage nối liền, nửa mở `[from, to)`; pending item không mất khi con trỏ tiến.
- **Test/oracle:** chuỗi kỳ có kỳ rỗng ở giữa → coverage ledger không hở, không chồng; publisher crash giữa chừng không tiêu thụ backfill.
- **REQ ảnh hưởng:** REQ-D57, REQ-D27, REQ-D28, REQ-AC08, REQ-S8.2-09, REQ-S10.4-03.

### AMD-B05 — Cam kết chống trùng khi resume

- **Trước** (SRC-SPEC §9.2 và AC-04): "Tiếp từ con trỏ, **không lấy lại bài đã có**".
- **Sau:** "Tiếp từ con trỏ khi con trỏ còn hiệu lực. Cam kết của hệ thống là **không ingest trùng** theo `x_post_id`; việc đọc lại một số trang được phép theo recovery policy khi con trỏ mất hiệu lực. Checkpoint chỉ chứa dữ liệu server đã ACK. Giới hạn bao phủ X được ghi trong metadata của run."
- **Vì sao:** cursor của feed động không chứng minh được là ổn định; hứa "không đọc lại" là một bảo đảm không kiểm chứng được, còn "không ingest trùng" thì kiểm chứng được bằng số hàng.
- **Bảo đảm thay thế:** I02 (receipt chỉ ACK sau commit; checkpoint không đi trước dữ liệu bền) và dedup theo `x_post_id`.
- **Test/oracle:** crash sau commit trước ACK rồi replay cùng `idempotency_key` → `COUNT(post)` và checkpoint không đổi; cursor bị vô hiệu → đọc lại nhưng không sinh hàng `post` mới.
- **REQ ảnh hưởng:** REQ-AC04, REQ-S9.2-01, REQ-S5.4-01, REQ-S9.3-01, REQ-S9.3-07, REQ-A1, REQ-A7.

### AMD-B07 — "Một lần" của D25

- **Trước** (SRC-SPEC §3.5, D25): "Phân tích và summary tạo **một lần** cho mỗi công trình rồi tái sử dụng".
- **Sau:** "Với mỗi analysis key — gồm canonical id của target, source version/fingerprint, task type, phiên bản prompt/schema và generation — hệ thống giữ **tối đa một kết quả hợp lệ**, rồi tái sử dụng. Đổi tag không đổi key. Phân tích lại theo D26 tạo generation mới; attempt lỗi hoặc không xác định không phải kết quả."
- **Vì sao:** nghĩa đen "một lần cho mỗi công trình" loại trừ chính D26 và loại trừ cả retry sau lỗi.
- **Bảo đảm thay thế:** I04 — retry không tạo hai kết quả hợp lệ cùng key; đổi tag không làm gọi AI lại.
- **Test/oracle:** bỏ rồi thêm lại tag → provider call counter delta bằng 0 cho cùng key và generation; hai worker cùng submit một key → chỉ một hàng hợp lệ, hàng thứ hai bị từ chối.
- **REQ ảnh hưởng:** REQ-D25, REQ-D26, REQ-AC06, REQ-S7.3-02, REQ-S9.2-03, REQ-S10.4-02, REQ-S8.1-04.

### AMD-B08 — Timezone

- **Trước** (SRC-SPEC §3.6, D56): "Timezone lấy theo máy chạy app".
- **Sau:** "Hệ thống lưu **một IANA timezone duy nhất** trong Settings, do Owner xác nhận (giá trị tạm: `Asia/Ho_Chi_Minh`). Mọi timestamp bền được lưu ở UTC theo RFC 3339 với độ chính xác mili giây, tie-break bằng ingest sequence. Timezone chỉ dùng để diễn giải lịch và để hiển thị."
- **Vì sao:** browser, server và máy collector là ba đồng hồ và ba múi giờ khác nhau; "máy chạy app" không xác định máy nào.
- **Bảo đảm thay thế:** lịch, chạy bù và ranh giới coverage tính được một cách xác định và tái lập.
- **Test/oracle:** fake-clock qua ranh giới DST → số run sinh ra đúng bảng đã chốt; hai bản ghi cùng mili giây → thứ tự theo ingest sequence là xác định.
- **REQ ảnh hưởng:** REQ-D56, REQ-D13, REQ-D15, REQ-D27, REQ-AC02, REQ-S8.2-08, REQ-S10.3-05, REQ-OQ06.

### AMD-B09 — Ngoại lệ liên kết Telegram

- **Trước** (SRC-SPEC §11.3): "Tin từ chat ID chưa liên kết bị **bỏ im lặng** — không trả lời gì, vì trả lời 'không có quyền' là tự xác nhận bot tồn tại".
- **Sau:** "Tin từ chat ID chưa liên kết bị bỏ im lặng, **trừ một ngoại lệ hẹp**: thông điệp khớp đúng định dạng mã liên kết được đối chiếu với các mã chưa hết hạn và chưa dùng. Mã hợp lệ thì thiết lập liên kết; mã sai, hết hạn hoặc đã dùng cũng bị bỏ im lặng, không trả lời lỗi."
- **Vì sao:** §5.1 bước 4 bắt buộc bot phải nhận được mã từ một chat chưa liên kết; nguyên văn §11.3 làm luồng thiết lập lần đầu không chạy được.
- **Bảo đảm thay thế:** bề mặt tấn công chỉ mở đúng cho chuỗi khớp định dạng mã; không rò rỉ sự tồn tại của bot cho mọi thông điệp khác.
- **Test/oracle:** fake update từ chat lạ với nội dung bất kỳ → outbound call count bằng 0, không mutation; cùng mã gửi hai lần → lần hai không tạo liên kết và không phản hồi.
- **REQ ảnh hưởng:** REQ-S11.3-02, REQ-D35, REQ-S5.1-04, REQ-S11.2-04, REQ-AC18.

### AMD-B10 — Resume và giới hạn lệnh Telegram

- **Trước** (SRC-SPEC §5.4 bước 4): "Bấm 'tiếp tục' trong app hoặc gửi lệnh trạng thái/chạy ngay".
- **Sau:** "Bấm 'tiếp tục' trong app. Lệnh `status` là chỉ đọc và không làm run rời khỏi `needs_user`; lệnh `run-now` không ghi đè một run đang `needs_user`. Không thêm lệnh Telegram thứ tư; hành động hủy liên kết cũng nằm trong app."
- **Vì sao:** câu gốc gợi ý hai lệnh Telegram có thể resume một run đang chờ can thiệp, mâu thuẫn với §5.4 bước 5 và với §9; đồng thời §11.3 giới hạn đúng 3 lệnh.
- **Bảo đảm thay thế:** resume chỉ xảy ra sau khi phiên được kiểm là không còn challenge, và luôn cấp lease mới (I10).
- **Test/oracle:** gửi `status` và `run-now` khi run đang `needs_user` → không hàng nào đổi, không lease mới; chỉ hành động resume trong app mới đưa run về `queued`.
- **REQ ảnh hưởng:** REQ-S5.4-04, REQ-D36, REQ-D37, REQ-S11.3-03, REQ-S11.3-04, REQ-AC04, REQ-S4-06.

### AMD-B11 — Backup và restore

- **Trước** (SRC-SPEC §3.6 D58 và §7.3): "Backup là copy file SQLite" / "Backup: copy file SQLite. Restore: đặt file về chỗ cũ".
- **Sau:** "Backup tạo snapshot nhất quán bằng SQLite Online Backup API hoặc `VACUUM INTO` (an toàn với WAL), kèm manifest ghi hash file DB, phiên bản schema, artifact và cấu hình embedding. Restore thực hiện vào môi trường sạch với khóa side effect: dispatcher và worker claim bị dừng, outbox cũ không replay, `first_announced` không bị reset trước khi kiểm tra toàn vẹn. Retention: giữ vô thời hạn."
- **Vì sao:** WAL là một phần trạng thái bền của DB; copy riêng file DB có thể mất transaction đã commit (SRC-PLAN §3.1).
- **Bảo đảm thay thế:** I15 — restore không tự gửi lại outbox cũ, không chạy lại job side effect, không reset `first_announced` mà không kiểm tra.
- **Test/oracle:** restore vào môi trường rỗng → trước khi verify không có side effect nào; count và hash của Saved, report và ledger khớp manifest.
- **REQ ảnh hưởng:** REQ-D58, REQ-S7.3-04, REQ-S6.4-01, REQ-AC12, REQ-S9.3-08, REQ-S13-09.

### AMD-B12 — Xóa cạnh collector → analysis worker

- **Trước** (SRC-SPEC §6.2, sơ đồ đường dữ liệu): dòng `COL --> AW` — "Collector - máy cá nhân" nối thẳng tới "Analysis worker - máy cá nhân".
- **Sau:** xóa cạnh `COL --> AW`. Analysis worker nhận **task từ server sau ingest commit** (`API --> AW` hoặc worker pull qua Analysis API). Collector chỉ có một đường ra duy nhất là Backend API.
- **Vì sao:** cạnh đó cho phép analysis chạy trên dữ liệu **chưa commit**, mâu thuẫn D08 ("collector không ghi trực tiếp, đẩy qua API có xác thực") và phá I02.
- **Bảo đảm thay thế:** mọi input của analysis đều đã qua commit và có canonical id; kết quả phân tích luôn gắn được vào dữ liệu authoritative.
- **Test/oracle:** negative case — collector cố gửi payload cho analysis worker bị từ chối bởi capability registry (default deny); import/dependency rule chặn edge này khi cùng tiến trình.
- **REQ ảnh hưởng:** REQ-S6.2-01, REQ-D08, REQ-D42, REQ-S6.1-03, REQ-AC16.

### AMD-B15 — Phạm vi chỉ số "0 trùng"

- **Trước** (SRC-SPEC §1.4): "| Vận hành | Công trình trùng không thành nhiều phát hiện | 0 trường hợp trùng | Đã xác nhận |".
- **Sau:** "| Vận hành | Công trình trùng không thành nhiều phát hiện | 0 trường hợp trùng **trong phạm vi canonical identity đã biết** (DOI, arXiv ID hoặc dạng chuẩn hóa đã định nghĩa); các trường hợp `identity_conflict` được đếm và báo cáo riêng | Đã xác nhận, phạm vi được thu hẹp bởi AMD-B15 |".
- **Vì sao:** metadata có thể thiếu hoặc mâu thuẫn; một ràng buộc UNIQUE không giải được trùng lặp khoa học chưa có ID.
- **Bảo đảm thay thế:** I03 — alias conflict không bị merge đoán, nguồn được giữ nguyên và có audit trail.
- **Test/oracle:** fixture DOI/arXiv mapping mâu thuẫn → target vào quarantine, không merge; report không tính hai alias nghi trùng là hai hướng chắc chắn.
- **REQ ảnh hưởng:** REQ-S1.4-03, REQ-D17, REQ-D29, REQ-AC07, REQ-AC09, REQ-S9.3-05.

### AMD-B16 — Ba loại phát biểu trong summary

- **Trước** (SRC-SPEC AC-11): "Then nhãn ghi 'chỉ có post', và **mọi phát biểu về tính mới được trình bày là suy luận**, không phải kết luận".
- **Sau:** "Then nhãn ghi 'chỉ có post'; mỗi phát biểu mang đúng một nhãn trong ba loại `author_claim`, `source_verified`, `ai_inference`; phát biểu về tính mới không có nguồn kiểm chứng được **phải** nằm ở `ai_inference`; khi không có nguồn so sánh thì trường `comparator` bằng `unknown` và không được bịa baseline."
- **Vì sao:** AC-11 nguyên văn gộp cả tuyên bố của tác giả vào "suy luận", làm mất thông tin và mâu thuẫn §10.3.
- **Bảo đảm thay thế:** grounding kiểm được bằng schema cộng kiểm tra citation, thay vì bằng cách hạ cấp mọi phát biểu.
- **Test/oracle:** fixture chỉ có post → mọi phát biểu tính mới nằm ở `ai_inference`, `comparator = unknown`; fixture có abstract nêu đóng góp → phát biểu đó ở `author_claim` kèm citation target.
- **REQ ảnh hưởng:** REQ-AC11, REQ-D20, REQ-S10.3-02, REQ-S10.3-01, REQ-S10.3-06.

### AMD-B17 — Phạm vi và thời điểm enqueue summary

- **Trước** (SRC-SPEC §2.1 mục 6): "Summary theo hình dạng 'nội dung + điểm khác + hạn chế' **cho mọi mục**".
- **Sau:** "Summary theo hình dạng 'nội dung + điểm khác + hạn chế' cho **mọi mục được report builder chọn tại thời điểm dựng báo cáo**. Báo cáo mang `quality: partial` kèm danh sách pending tường minh khi còn mục thiếu summary; `complete` chỉ khi mọi mục được chọn đều đã có summary hoặc được đánh dấu pending tường minh."
- **Vì sao:** §2.1 và §10.1 nêu hai phạm vi khác nhau ("mọi mục" và "mọi mục vào báo cáo"); phạm vi rộng làm chi phí AI tỉ lệ với số bài thu được, mâu thuẫn §10.4.
- **Bảo đảm thay thế:** không có mục nào bị mất khỏi hàng đợi mà báo cáo vẫn ghi `complete`.
- **Test/oracle:** late analysis → mục xuất hiện ở kỳ sau với nhãn phát hiện muộn; report có mục thiếu summary → `quality = partial` và pending list không rỗng.
- **REQ ảnh hưởng:** REQ-P0-06, REQ-D19, REQ-S10.1-03, REQ-S10.4-03, REQ-AC10, REQ-S9.3-03.

### Blocker không cần amendment văn bản

B06, B13 và B14 **không** sửa câu chữ nào của đặc tả: chúng bổ sung định nghĩa còn thiếu (identity/alias/target; chính sách secret và cô lập; phép đo mật độ vector). Owner đã phê chuẩn cả ba ở `OD-20260907-01` mục 10, 15 và 16 — nay `ACCEPTED (OD-20260907-01)`. Hai hệ quả Owner đã biết khi chấp nhận: một adapter **có thể bị tắt** cho tới khi kiểm được cô lập (B13, và `REQ-AC16` vì thế vẫn `BLOCKED`), và khối "hướng đang nổi" **sẽ trả `insufficient_evidence`** khi thiếu dữ liệu (B14, D53 vẫn ĐX ở phần hiệu chỉnh tham số).

### `AMD-SPEC-D34-01` — Tiền đề "OpenAlex yêu cầu email liên hệ" đã bị dữ kiện thay thế

**Đây là một đính chính tiền đề, KHÔNG phải một amendment câu chữ.** Nó được ghi ở đây theo ruling của
Coordinator sau khi `worker-W3n` **đúng đắn từ chối** tự quyết mục này trong phạm vi thẩm quyền của họ.

- **Trước** (trích nguyên văn `research-radar-spec.md:101`, hàng `D34` của bảng nhật ký quyết định):
  "Nhịp gọi arXiv và yêu cầu email liên hệ của OpenAlex: đọc tài liệu chính thức khi triển khai".
- **Sau:** **không có văn bản thay thế, và không cần một văn bản thay thế.** Câu trên **đứng nguyên, không
  sửa một byte**. Nó được đọc theo **nghĩa lịch sử**: nó ghi đúng giả định đang có hiệu lực lúc viết, và
  giả định đó nay đã biết là sai. Nghĩa vụ mà câu này đặt ra — *"đọc tài liệu chính thức khi triển khai"* —
  **đã được thực hiện đầy đủ**, và chính việc thực hiện nó là thứ chứng minh tiền đề sai.
- **Vì sao:** ngày **2026-09-07**, dưới quyền mạng hẹp của `OD-20260907-04` mục 2 (mở rộng thêm
  `help.openalex.org`), `worker-WF` đọc tài liệu OpenAlex hiện hành và ghi lại nguyên văn: **không** có yêu
  cầu email liên hệ, **không** còn quy ước `mailto` / `polite pool` / `User-Agent`; `api_key` là **tùy
  chọn** (nó chỉ nâng ngân sách ngày). Chi tiết, trích dẫn và URL ở **§8.13.2**.
- **Bảo đảm thay thế:** ràng buộc thật của OpenAlex **không** biến mất, nó chỉ **khác** với điều D34 giả
  định — `100` request/giây cộng một **ngân sách ngày nêu bằng tiền, không bằng số lời gọi**. Vì vậy
  `SG-IDENT` (không gọi nguồn khi nguồn đòi định danh mà cấu hình chưa có) **vẫn giữ nguyên như một luật**;
  điều đổi là với OpenAlex nó **không kích hoạt**, vì tiền đề "nguồn này đòi định danh" không đúng. Luật
  không bị nới; chỉ có một trong các đầu vào của nó được đo đúng.
- **Test/oracle:** `contracts/retry-policy.yaml` `research_connector_rate_limit` nay `DOCS_derived`
  (v0.8.0) với `openalex_requests_per_window = 100`, `openalex_window_seconds = 1`, và
  `openalex_identification_required` mang giá trị **phủ định có nguồn** thay vì `null`. Ngân sách ngày
  **cố ý không** được biến thành một con số (`RESOLVED_NON_NUMERIC`): tài liệu nêu nó bằng tiền, nên nguồn
  sự thật lúc chạy là các header `X-RateLimit-*`. Oracle âm: không file nào được ghi một con số ngân sách
  ngày suy ra từ "1/10".
- **REQ ảnh hưởng:** `REQ-D34` (`research-radar-spec.md:101`), `REQ-A6`, `REQ-S13.2-01`, `REQ-P0-04`.

**Bằng chứng.** `precode/decision-register.md` §8.13.2; `evidence/handoffs/PC03-REQA6-handoff.md`;
`OD-20260907-04` mục 2 (`precode/owner-decisions-04.md`, authority `AUTH-OWNER-20260907-05`), cộng phần mở
rộng allowlist thêm `help.openalex.org` được ghi tại §8.13.2.

**Quan hệ với các file đã mang ghi chú.** `precode/requirements.csv` hàng `REQ-D34` và
`acceptance/traceability.csv` hàng `REQ-D34` **đã** mang cảnh báo tiền đề sai — do `worker-W3n` viết. Mục
này là **bản ghi chuẩn** mà hai ghi chú đó trỏ về; nếu ba nơi lệch nhau thì **mục này thắng**. `worker-W3n`
không tự tạo nó vì tạo một `AMD-…` là việc của PC00 dưới ruling của Coordinator, không phải của gói đang
sửa ghi chú — đó là một lần từ chối đúng, và nó được ghi lại ở đây thay vì bị bỏ qua.

**Ba điều mục này KHÔNG làm.**

1. **Không sửa đặc tả.** `research-radar-spec.md` và `precode/source/spec-v0.2.md` là **nguồn bất biến**;
   không byte nào của chúng bị chạm bởi mục này hay bởi bất kỳ gói nào. Một đặc tả v0.3 tương lai **có thể**
   giữ nguyên câu D34 và chỉ thêm một chú thích lịch sử — khác hẳn các `AMD-B<nn>`, vốn *đòi* viết lại.
2. **Không đổi trạng thái yêu cầu vì lý do này.** `REQ-D34` chuyển `KC → XN` là vì **nghĩa vụ đọc tài liệu
   đã hoàn thành** (§8.13.2), **không** phải vì tiền đề của nó đúng. Ghi chú trong `requirements.csv` nói
   thẳng điều đó và phải giữ nguyên cách nói ấy.
3. **Không nâng trần claim của module nào.** `MOD-research-connector` đạt `CONTRACT_READY` hay không là kết
   luận của PC05/Coordinator trên toàn bộ cổng của nó, không phải hệ quả của một khối hợp đồng đã hết `KC`.

**Hiệu lực của chính đính chính này có điều kiện.** Nó đúng với tài liệu OpenAlex **đọc ngày 2026-09-07**.
Nhà cung cấp đổi chính sách thì nhãn `DOCS_derived` hết hiệu lực và mục này phải được đọc lại — cùng luật
đã ghi ở `contracts/retry-policy.yaml`. Một dữ kiện bên ngoài không bao giờ "đóng" vĩnh viễn theo cách một
quyết định sản phẩm đóng.

## 4. Các mục P0 hiện còn ĐX — **không được tự promote**

| REQ | Nội dung | Trạng thái nguồn | Vì sao vẫn ở P0 | Hệ quả nếu không được xác nhận |
| --- | --- | --- | --- | --- |
| REQ-D09 | Chrome profile riêng của dự án | **XN** (ratified) | Cần cho REQ-P0-03 và bước §5.1-05 | Chặn M0; REQ-OQ01 ghi rõ "Chặn M0" |
| REQ-D53 | Khối "hướng đang nổi" tính từ mật độ vector, vào MVP | ĐX | Là nửa sau của REQ-P0-07 | Khối này rơi khỏi MVP; REQ-D52 mất phương tiện chính |
| REQ-D08 | Collector đẩy dữ liệu qua API có xác thực | **XN** (ratified) | Nền tảng của REQ-P0-12 và I02 | PC01 không đóng được ranh giới |
| REQ-D42 | Bước LLM chạy cùng máy collector | **XN** (ratified) | Nền tảng của REQ-P0-11 | PC01/PC06 không đóng được topology |
| REQ-D50 | Model embedding chạy ở server | **XN** (ratified) | Nền tảng của REQ-P0-05 | PC01/PC04 không đóng được nơi chạy |
| REQ-D11 | Job xếp hàng ở server, collector kéo việc | ĐX | Nền tảng của REQ-P0-10 | PC03 không đóng được mô hình claim |
| REQ-D22 | AI gắn nhãn mở | ĐX | Nền tảng của REQ-P0-05 | Đổi tag sẽ phải gọi AI lại, phá REQ-AC06 |
| REQ-D33 | Post chỉ có ảnh chụp thành mục "chỉ có post" | ĐX | Bổ trợ REQ-P0-04 | Post-only không có model rõ |
| REQ-D21 | Nhãn mức độ đọc trên mỗi summary | ĐX | Bổ trợ REQ-P0-06 | Mất evidence level, phá REQ-AC11 |
| REQ-D26 | Phân tích lại khi bấm tay hoặc có phiên bản mới | ĐX | Bổ trợ REQ-P0-06 | Không có đường reanalysis hợp lệ |
| REQ-D37 | Có lệnh hủy liên kết | ĐX | Bổ trợ REQ-P0-09 | Xem F-PC00-01 |
| REQ-D38 | Nút Save Telegram và UNIQUE chống trùng | ĐX | Nền tảng của REQ-P0-08 | REQ-AC13 mất cơ chế |
| REQ-D43 | Giao ước adapter và bước bóc JSON của CLI | ĐX | Nền tảng của REQ-P0-11 | PC06 không có capability matrix |
| REQ-D44 | Usage chấp nhận "không rõ" | ĐX | Bổ trợ REQ-P0-11 | I14 không có chỗ dựa |
| REQ-D15 | Gộp đợt quá hạn thành một | ĐX | Nền tảng của REQ-P0-10 | REQ-AC02 mất oracle |
| REQ-D16 | Chạy bù không gửi bù báo cáo cũ | ĐX | Bổ trợ REQ-P0-10 | Rủi ro spam digest cũ |
| REQ-D12 | `last_run` chỉ để xem | ĐX | Bổ trợ REQ-P0-12 | Rủi ro dùng `last_run` làm mốc lọc |
| REQ-D18 | Idea cluster hoãn sau MVP | ĐX | Là quyết định hoãn, không phải hạng mục P0 | Nếu đảo lại thì phạm vi MVP tăng |

**Cập nhật 2026-09-07 — bốn dòng đã được promote, phần còn lại thì không.** Owner đã trả lời (`OD-20260907-01`). Bốn mục sau chuyển `ĐX` → `XN` trong `precode/requirements.csv`, mỗi dòng mang ghi chú `Ratified OD-20260907-01`:

| REQ | Mục biên bản | Trạng thái mới |
| --- | --- | --- |
| `REQ-D09` | 1 — profile riêng của dự án | **XN** |
| `REQ-D08` | 2 — bỏ cạnh collector → analysis | **XN** |
| `REQ-D42` | 2 | **XN** |
| `REQ-D50` | 2 | **XN** |

**Mười bốn dòng còn lại trong bảng trên vẫn `ĐX`** — biên bản không nêu tên chúng, và PC00 không suy rộng. Đáng chú ý: `REQ-D53` (khối "hướng đang nổi") **vẫn là ĐX trong một hạng mục P0**; biên bản mục 16 nói rõ điều được chốt là *cách xử lý khi thiếu dữ liệu* (`insufficient_evidence`), không phải rằng thuật toán đã được hiệu chỉnh — việc đó chờ `REQ-A4`.

## 5. Câu hỏi còn mở và giá trị mặc định tạm

| REQ | Câu hỏi | Giá trị (Owner đã chấp nhận ở OD-20260907-01 mục 20, trừ REQ-OQ03) | Ai phải chốt | Chặn gì |
| --- | --- | --- | --- | --- |
| REQ-OQ01 | Chrome profile riêng? | **ĐÃ TRẢ LỜI** — có, profile riêng của dự án (mục 1) | Owner ✅ | — (M0 không còn bị chặn bởi câu hỏi này) |
| REQ-OQ02 | Stack? | **ĐÃ TRẢ LỜI** — **B: Python workers + TypeScript web** (mục 3); khuyến nghị A của đặc tả bị bác | Owner ✅ | — (M1 không còn bị chặn; 18 card cần viết lại §3/§8) |
| REQ-OQ03 | Provider và model cụ thể? | **ĐÃ TRẢ LỜI** (`OD-20260908-06`, vòng sáu) — `summary` = Claude Opus 5 (`claude-opus-5`); `label` và `direction_phrasing` = Claude Sonnet 5 (`claude-sonnet-5`); cả hai họ `api_key` | Owner ✅ | — (cổng vào M3 được thỏa). **Việc bật provider vẫn bị chặn** bởi cô lập chưa kiểm chứng — §8.15 |
| REQ-OQ04 | N ngày backfill? | 7 ngày | Owner | — |
| REQ-OQ05 | Giới hạn mỗi đợt? | 200 post hoặc 30 phút, cái nào tới trước | Owner (sau M0) | — |
| REQ-OQ06 | Lịch cụ thể? | 08:00 và 20:00 theo timezone của Owner | Owner | — |
| REQ-OQ07 | Giờ yên lặng Telegram? | Không có ở MVP | Owner | — |
| REQ-OQ08 | Ngưỡng tương đồng? | **Không đặt số** — phải đo (REQ-A2) | Dữ liệu, sau M3 | — |
| REQ-OQ09 | Model embedding cụ thể? | **Không đặt tên** — ràng buộc: local, đa ngôn ngữ | Kỹ thuật, sau A3 | — |
| REQ-OQ10 | Export Saved ở MVP? | Hoãn sang P1 | Owner | — |
| — | Timezone của Owner | `Asia/Ho_Chi_Minh` | Owner | Fixture lịch |

**Cập nhật 2026-09-08:** dòng `REQ-OQ03` của bảng trên đã đổi; đoạn "Kết quả 2026-09-07" ngay dưới giữ nguyên câu chữ của **ngày nó được viết** và không được đọc như trạng thái hiện hành — trạng thái hiện hành ở §8.15.

**Kết quả 2026-09-07:** Owner chấp nhận toàn bộ bảng trên (mục 20), **trừ `REQ-OQ03`** vẫn `OWNER_DECISION_REQUIRED` và vẫn chặn M3 (mục 21). Các giá trị cần đo — `REQ-OQ05` (sau M0), `REQ-OQ08` (sau M3), `REQ-OQ09` (sau A3) — được chấp nhận làm **giá trị làm việc**, không phải giá trị đã đo.

Lý do cho từng con số: N = 7 lấy nguyên văn đề xuất của SRC-SPEC §13.1; lịch 08:00 và 20:00 lấy từ ví dụ §8.2 hàng 8 và AC-01/AC-02; giới hạn 200 post hoặc 30 phút là ước lượng tạm để hợp đồng không còn "TBD" — SRC-SPEC §13.1 nói rõ con số thật phải đến sau M0; giờ yên lặng "không có" là mặc định ít bất ngờ nhất vì đặc tả không mô tả cơ chế hoãn gửi.

## 6. Phát hiện mới của PC00 (không nằm trong B01–B17)

| ID | Phát hiện | Nguồn | Xử lý |
| --- | --- | --- | --- |
| F-PC00-01 | Số lệnh Telegram tự mâu thuẫn: D36 và §11.3 nói **đúng 3 lệnh** (Save, chạy ngay, xem trạng thái), nhưng D37 yêu cầu "có lệnh hủy liên kết" — tức lệnh thứ tư | SRC-SPEC:D36, SRC-SPEC:D37, SRC-SPEC§11.3 | Xếp vào phạm vi B10. **ACCEPTED (OD-20260907-01)** (mục 13): hủy liên kết là hành động trong app; Telegram giữ đúng 3 lệnh |
| F-PC00-02 | Màn hình Saved liệt kê hành động **export** ở SRC-SPEC §4, trong khi REQ-OQ10 vẫn hỏi "có cần export Saved ở MVP hay hoãn" | SRC-SPEC§4 (hàng Saved), SRC-SPEC§13.1 hàng 10 | **ACCEPTED (OD-20260907-01)** (mục 20): hoãn export sang P1, nút export không có ở MVP; ảnh hưởng REQ-S4-05 |
| F-PC00-03 | Phạm vi summary mâu thuẫn giữa §2.1 mục 6 ("cho mọi mục") và §10.1 ("Mọi mục vào báo cáo") | SRC-SPEC§2.1#row-06, SRC-SPEC§10.1#row-03 | Đã nằm trong B17; AMD-B17 chốt theo §10.1 |
| F-PC00-04 | SRC-SPEC §5.2 dùng `delivered`/`delivered_partial` như trạng thái của **run**, mâu thuẫn §9.1 | SRC-SPEC§5.2, SRC-SPEC§9.1 | Đã nằm trong B02; bảng ánh xạ trong AMD-B02 xử lý |
| F-PC00-05 | `saved_item` khóa `UNIQUE(owner, work/post)` là ký hiệu mơ hồ: hai cột nullable không cho ràng buộc duy nhất đúng với target post-only | SRC-SPEC§7.1 (hàng `saved_item`) | Đã nằm trong B06; PC02 phải dùng target tagged union |
| F-PC00-06 | REQ-D34 và REQ-A6 là cùng một yêu cầu được ghi hai lần ở hai chỗ (decision log và bảng giả định) | SRC-SPEC:D34, SRC-SPEC:A6 | Giữ cả hai dòng trong registry để không mất nguồn; ghi chú chéo trong cột notes. Không phải mâu thuẫn |

`F-PC00-01` và `F-PC00-02` là hai điểm PC00 **tự quyết theo khuyến nghị của kế hoạch** vì không có mục nào của §5 baseline phủ; Owner đã xác nhận cả hai ở `OD-20260907-01` (mục 13 và 20). Cả hai được ghi vào `unresolved refs` của HANDOFF và vào `precode/owner-decision-request.md`.

## 7. Chỉ mục ADR

Xem `precode/adr/README.md`. Tương ứng: ADR-0001 (B12), ADR-0002 (B02), ADR-0003 (B03), ADR-0004 (B01), ADR-0005 (B11), ADR-0006 (stack), ADR-0007 (B08), ADR-0008 (B07), ADR-0009 (B06/B15), ADR-0010 (B13), ADR-0011 (framework và toolchain cho stack B — `ACCEPTED (OD-20260907-02)`).

## 8. Quyết định tạm thời phát sinh sau audit A1-R1

Mục này ghi các quyết định **không** thuộc B01–B17, phát sinh từ AUDIT_REPORT `PKT-A1-R1` và các ruling của
Coordinator ngày 2026-09-06T18:00Z. Chúng theo cùng luật với §2. Mục nào được `OD-20260907-01` nêu tên thì nay là `ACCEPTED (OD-20260907-01)`;
mục nào được `OD-20260907-02` nêu tên thì là `ACCEPTED (OD-20260907-02)`; mục nào không được nêu ở biên bản nào
thì **vẫn `PROVISIONAL`** — không suy rộng. Không mục nào được ghi `CLOSED`.

### PROV-PC00-01 — Ba thao tác xóa của REQ-S7.3-05 và phạm vi loại trừ của `data.purge_all`

- **Nguồn yêu cầu.** SRC-SPEC §7.3: *"Bỏ lưu ≠ xóa dữ liệu gốc ≠ xóa toàn bộ dữ liệu. Ba thao tác riêng,
  thao tác thứ ba đòi xác nhận gõ tay."* — `REQ-S7.3-05`, trạng thái **XN**.
- **Điều audit phát hiện (`F-A1R1-04`, MAJOR).** Bộ 82 operation của `contracts/ports.yaml` chỉ có
  `save.remove`. Thao tác **thứ hai** ("xóa dữ liệu gốc") vắng mặt khỏi cả inventory lẫn mọi danh sách
  unresolved — bị bỏ sót im lặng; thao tác **thứ ba** chỉ được `PROV-PC01-03` nêu. Ngoài ra
  `save.remove.requirement_refs` trỏ nhầm sang `REQ-S7.3-01`.
- **Ruling R-04 của Coordinator.** PC01 thêm hai owner-only HTTP mutation:
  - `data.delete_target` — xóa dữ liệu gốc của **một** target (post/work); **giữ** `saved_snapshot` theo D55
    và giữ các ledger; cần cờ xác nhận tường minh; có transaction và error map; scenario `SC32`.
  - `data.purge_all` — xóa **toàn bộ** dữ liệu; cần trường xác nhận **gõ tay** khớp một challenge do server
    phát; chỉ chạy khi `storage.health = maintenance`; thu hồi mọi lease.
  - `save.remove.requirement_refs` sửa thành `REQ-S7.3-05`; `PROV-PC01-03` viết lại để nêu **cả hai**
    operation, không chỉ operation thứ ba.
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** Chấp nhận cả hai operation ở mức khai báo hợp đồng cho PC01. PC00
  ghi nhận và trỏ `REQ-S7.3-05` sang chúng; PC00 **không** tự định nghĩa operation (không thuộc write target).
- **ĐÃ GIẢI — `ACCEPTED (OD-20260907-01)` mục 24.** Owner chốt: `data.purge_all` xóa **chỉ dữ liệu nghiên cứu**;
  **giữ** credential đăng nhập, secrets, liên kết Telegram, cấu hình provider và lịch; **backup KHÔNG bị xóa**.
  Danh sách loại trừ của `TXN-purge-all` chính là tập được giữ đó, và `MOD-data-admin-service` được gỡ chặn.
  Đoạn dưới đây là lập luận lúc câu hỏi còn mở, giữ lại để truy vết.
- **(Lịch sử) Phần từng bị chặn.** Cụm *"toàn bộ dữ liệu"* của `data.purge_all` khi đó **không có
  mặc định an toàn**: không có câu nào trong SRC-SPEC nói settings, secret, liên kết Telegram, cấu hình
  provider hay chính tài khoản đăng nhập có bị xóa hay không. Đoán sai theo hướng rộng là mất khả năng đăng
  nhập lại; đoán sai theo hướng hẹp là để lại dữ liệu người dùng tưởng đã xóa. Vì vậy phạm vi loại trừ giữ
  `OWNER_DECISION_REQUIRED` cho tới khi Owner trả lời. Owner đã trả lời ngày 2026-09-07 (mục 24) — xem
  `precode/owner-decisions.md`.
- **Hợp đồng/file bị ảnh hưởng.** `contracts/ports.yaml`, `contracts/modules.yaml` (`PROV-PC01-03`),
  `contracts/state/storage.yaml` (guard `maintenance`), `acceptance/scenarios.yaml` (`SC32`),
  `precode/requirements.csv` (`REQ-S7.3-05`).
- **Gate bị chặn.** G1 cho phần inventory (PC01); G3 cho phần semantics của `data.purge_all` (PC08 khóa
  maintenance và thu hồi lease).
- **Thay đổi oracle.** `REQ-S7.3-05` chuyển từ "có ba thao tác riêng" (kiểm bằng đọc) sang một kiểm tra truy
  vết requirement → operation: đúng ba operation trỏ về `REQ-S7.3-05`, mỗi cái có auth scope, ngữ nghĩa xác
  nhận và error map riêng. Thêm oracle âm: sau `data.delete_target`, số hàng `saved_snapshot` của target đó
  **không đổi** (D55), và `first_announced` **không** bị reset (I07).
- **Nếu Owner bác bỏ.** Nếu Owner không muốn có operation xóa nào ở MVP thì `REQ-S7.3-05` phải được ghi là
  **blocked scope tường minh** cho cả hai thao tác — không được để im lặng như tình trạng epoch 1 — và phần
  tương ứng của §7.3 rơi khỏi phạm vi MVP một cách có ghi chép.
- **Liên kết.** `REQ-S7.3-05`, `REQ-D55`, `REQ-D07`, I07, I08, `SC32`, `PROV-PC01-03`, `F-A1R1-04`, ruling R-04.

### Ghi chú về hai ngoại lệ header đã khai báo

`F-A1R1-05` (ADR thiếu 8 trường header của baseline §3) và `F-A1R1-06` (`requirements_csv_contract_header`
thiếu `requirement_refs`) là **defect tài liệu**, không phải quyết định sản phẩm, nên không có mục
`PROV-…` riêng. Chúng được xử lý tại chỗ: ngoại lệ ADR khai báo trong `precode/adr/README.md` (ruling R-05,
baseline §3 đã được Coordinator sửa tương ứng), và `requirement_refs` đã được thêm vào
`precode/baseline.json`. Chi tiết trước/sau nằm trong addendum `PKT-PC00-FIX1` của
`evidence/handoffs/PC00-handoff.md`.

### PROV-PC00-02 — Mã lỗi `CSRF_REJECTED`

- **Nguồn xung đột.** `contracts/http/openapi.yaml` (PC05) ánh xạ "thiếu hoặc sai CSRF token" sang **403 `FORBIDDEN_EDGE`**, nhưng `contracts/errors.yaml` (PC03) định nghĩa `FORBIDDEN_EDGE` là *"cạnh caller→callee không có trong `modules.yaml`"*. Một request thiếu CSRF đi qua **đúng** cạnh cho phép; cái sai là bằng chứng về ý định của người dùng, không phải topology. PC08 nêu ở `CR-PC08-03` và tạm theo PC05 để không tạo mâu thuẫn thứ hai.
- **Ruling FIX3 của Coordinator.** Đăng ký một mã riêng: `CSRF_REJECTED` — HTTP 403, `scope: request`, `retry_class: none`, **không đổi state**; áp dụng khi một owner-session mutation thiếu hoặc mang CSRF token không hợp lệ. `FORBIDDEN_EDGE` giữ nguyên nghĩa "cạnh không có trong registry"; `UNAUTHORIZED` giữ nguyên nghĩa "lớp principal không được phép / danh tính chưa thiết lập" — nên `CR-PC08-04` được chấp nhận đúng như PC08 lập luận: collector token gọi `save.create` là **`UNAUTHORIZED` 401**, không phải `FORBIDDEN_EDGE`.
- **Trạng thái.** **`ACCEPTED (OD-20260907-01)`** (mục 25 — Owner chấp nhận cả hai thay đổi kỹ thuật). Trước đó là `PROVISIONAL` dưới quyền ủy nhiệm của Coordinator.
- **File bị ảnh hưởng.** `contracts/errors.yaml` (PC03 FIX1 đăng ký), `contracts/http/openapi.yaml` (PC05 ánh xạ), `acceptance/fixtures/recovery/` (fixture `SC40`).
- **Thay đổi oracle.** Oracle của `SC40` chuyển từ "trả 403 `FORBIDDEN_EDGE`" sang "trả 403 `CSRF_REJECTED` **và** không hàng nào đổi". Oracle của `FORBIDDEN_EDGE` thu hẹp về đúng các ca `NC-*` của `modules.yaml`. Thêm oracle âm: một request đúng cạnh, đúng principal, thiếu CSRF **không** được sinh mã nói về cạnh.
- **Nếu Owner/Coordinator bác bỏ.** Phải sửa **đồng thời** định nghĩa `FORBIDDEN_EDGE` trong `errors.yaml`, các ca `NC-01/NC-02` của `modules.yaml` và mô tả `collectorToken` trong `openapi.yaml` — không được sửa mỗi fixture, vì đó chính là lớp lỗi "một hành vi, nhiều mô tả" mà `F-A1R1-01` đã phạt.
- **Liên kết.** `CR-PC08-03`, `CR-PC08-04`, `CR-PC03-04`, `REQ-S11.1-01`, `REQ-D05`, `SC40`, `SC41`, I01, I11.

### PROV-PC00-03 — Hình dạng hai pha của `data.purge_all` và `SC44`

- **Bối cảnh.** `PROV-PC00-01` đã ghi nhận sự tồn tại của hai operation xóa; điểm còn lại là **cách** thực hiện "xác nhận gõ tay" của SRC-SPEC §7.3 mà không sinh ra operation thứ tư.
- **Quyết định đã phê chuẩn — `RATIFIED (OD-20260907-01)`.** `contracts/ports.yaml` khai `data.purge_all` là **một** operation với hai `phase`: (1) `request_challenge` — server sinh và lưu một `purge_challenge` có hạn, trả về cụm từ người dùng phải gõ lại, **không xóa gì**; (2) `execute` — đòi `purge_challenge_id` cộng `confirmation_phrase` khớp **chính xác**; sai hoặc hết hạn thì `VALIDATION_ERROR`, challenge bị hủy và phải xin lại. Idempotency key là `purge_challenge_id`, dùng đúng một lần; gọi lại sau khi đã thực thi trả bản ghi đã commit chứ **không** xóa lần hai. Chỉ chạy khi `storage.health = maintenance`; thu hồi mọi lease. `owner_module: MOD-data-admin-service`, `caller_modules: [MOD-web-ui]`, `auth_scope: owner_session`.
- **Scenario.** `SC44` — xác nhận hai pha, điều kiện tiên quyết `maintenance`, thu hồi lease, cộng các ca âm (cụm từ sai, challenge hết hạn, gọi lại phase 2 lần thứ hai, gọi khi không ở `maintenance`). Đã đăng ký anchor `SRC-PLAN:SC44` trong `precode/baseline.json`.
- **Hai hệ quả vận hành PC08 nêu, Owner phải biết trước khi trả lời `PROV-PC00-01`:**
  1. **Nếu purge xóa credential đăng nhập** thì phải có đường đặt lại tại chỗ, nếu không chủ nhà **tự khóa mình ra ngoài app** — D05 cấm trang signup và cấm quên-mật-khẩu tự động, nên không có đường vòng nào sẵn có.
  2. **Dữ liệu đã purge vẫn còn trong các artifact backup** cho tới khi chính những bản backup đó bị xóa. Muốn "xóa hẳn" phải xóa cả backup — một thao tác riêng (`contracts/ops/backup-restore.md` §8). Ai hiểu "xóa toàn bộ" là "không còn ở đâu nữa" sẽ hiểu sai.
- **Phần từng bị chặn — nay đã giải.** Danh sách **loại trừ** đã được chốt ở `OD-20260907-01` mục 24: giữ đăng nhập, secrets, liên kết Telegram, cấu hình provider và lịch; backup không bị xóa. Ứng viên PC08 từng nêu (settings, secrets, credential đăng nhập, `telegram_link`, `schema_migration`) nay được xác nhận là **thuộc tập giữ lại**.
- **Liên kết.** `REQ-S7.3-05`, `REQ-D05`, `REQ-D55`, `PROV-PC00-01`, `PROV-PC01-03`, `CR-PC08-01`, `SC44`, I08, I15.

### PROV-PC00-04 — `run.resume` được mở rộng cho trạng thái `blocked`

- **Nguồn xung đột.** `contracts/state/run.yaml` (PC03) có trạng thái `blocked` (X chặn hoặc thiếu capability bắt buộc, theo AMD-B02) nhưng `contracts/ports.yaml` chỉ khai `run.resume` cho `needs_user` (B10). Hệ quả: đường thoát duy nhất khỏi `blocked` là `run.cancel` — an toàn nhưng buộc Owner hủy run và tạo run mới, làm mất ngữ cảnh (`CR-PC03-02`).
- **Ruling FIX3.** Mở rộng guard của `run.resume`: cho phép từ `needs_user` (sau khi challenge đã được xử lý) **và** từ `blocked` (Owner tuyên bố điều kiện chặn đã hết, **bắt buộc** kèm `unblock_reason`); **không** từ trạng thái nào khác. PC01 ghi vào `ports.yaml`; PC03 FIX1 thêm hàng transition `blocked → queued`.
- **Trạng thái.** **`ACCEPTED (OD-20260907-01)`** (mục 25). Owner đã đọc đúng ràng buộc mà nó chạm — SRC-SPEC §5.4 bước 5 ("nếu hạn chế vẫn còn thì run **không** tự tiếp tục — dừng và báo") — và chấp nhận: mở chặn chỉ do Owner, chỉ trong app, và **bắt buộc** kèm lý do.
- **Ranh giới phải giữ.** Quyết định này **không** tạo bất kỳ đường tự động nào: chỉ Owner, chỉ qua app, chỉ với `unblock_reason` ghi lại được, và luôn cấp lease mới. Không có lệnh Telegram tương ứng (B10, AMD-B10). Không có retry tự động từ `blocked` (`REQ-S9.3-02`, I10).
- **Thay đổi oracle.** `REQ-S5.4-05` giữ nguyên nghĩa "không tự tiếp tục" nhưng oracle thêm một ca dương tính: sau khi Owner gọi `run.resume` với `unblock_reason`, run về `queued` và một lease **mới** được cấp khi claim. Ca âm: mọi actor khác, và mọi đường không có `unblock_reason`, đều bị từ chối; `status` và `run-now` từ Telegram vẫn không đưa run rời `blocked` (AMD-B10).
- **Nếu Owner bác bỏ.** Giữ nguyên thì `blocked` chỉ thoát được bằng `run.cancel`; ghi rõ điều đó trong UI để Owner không chờ một nút "tiếp tục" không tồn tại.
- **Liên kết.** `CR-PC03-02`, `REQ-S5.4-04`, `REQ-S5.4-05`, `REQ-S9.3-02`, `REQ-AC04`, AMD-B02, AMD-B10, I10.

### `PROV-PC00-07` — Framework và toolchain cho stack B (`ADR-0011`)

- **Bối cảnh.** `OD-20260907-01` mục 3 chốt stack **B** ở mức ngôn ngữ, nhưng chưa chốt framework. Khi được hỏi, Owner trả lời **"You pick, record as ADR"** — ủy quyền lựa chọn kỹ thuật cho Coordinator với điều kiện nó được ghi thành một ADR.
- **Quyết định.** `ADR-0011` chốt 14 tầng: Python 3.12 + `uv`; FastAPI + Pydantic v2 với model **sinh từ** `contracts/`; SQLAlchemy 2 Core + Alembic, WAL, Online Backup API; hàng đợi **bằng bảng DB** theo `entities.yaml` với vòng lặp scheduler in-process (không broker); Playwright for Python trên profile riêng; `subprocess` cho CLI/ACP; `sentence-transformers` ở server; **Bot API trực tiếp** cho Telegram; Vite + React + TS với client sinh từ `openapi.yaml`; cookie session + CSRF; `pytest` nạp fixture thẳng từ `acceptance/fixtures/**`; `ruff`/`mypy`/`eslint`; GitHub Actions không có job live; Docker Compose cho server.
- **Trạng thái.** **`ACCEPTED (OD-20260907-02)`** — Owner phê chuẩn ngày 2026-09-07 bằng câu *"accept ADR-0011, start phase 0 and 1"* (`precode/owner-decisions-02.md`, authority `AUTH-OWNER-20260907-03`, evidence `session_0156UBBHDSeC9soECzSVUb3U`). `ADR-0011` chuyển `provisional-accepted` → `accepted`, `ratified_by: OD-20260907-02`. `decision_owner` **giữ nguyên** là `Coordinator`: người *chọn* vẫn là Coordinator dưới ủy quyền; điều mới là có một quyết định của Owner phê chuẩn **nội dung** đã chọn.
- **(Lịch sử) Trạng thái trước 2026-09-07 vòng hai.** **`PROVISIONAL`**, `decision_owner: Coordinator` dưới quyền ủy nhiệm của `AUTH-OWNER-20260907-02`; **Owner có thể phản đối**, đưa vào vòng quyết định tiếp theo qua `precode/owner-decision-request.md`. Khi đó đây **không** phải một mục `ACCEPTED (OD-20260907-01)`: biên bản vòng một không phê chuẩn nội dung này, nó chỉ ủy quyền việc chọn. Đoạn này giữ lại để truy vết.
- **Phê chuẩn không xoá được bốn ô trống.** Bốn hàng `Test`, `Lint / format`, `CI`, `Đóng gói / triển khai` của `ADR-0011` được chính ADR ghi là **chưa từng cân nhắc phương án nào** (`F-A2R7-05`). Một phê chuẩn trọn gói **không** biến chúng thành đã-được-cân-nhắc; nó nói Owner chấp nhận chúng làm mặc định. Nếu Owner đảo một trong bốn hàng đó sau này, chi phí vẫn đúng như dòng dưới: chỉ card và mã.
- **Vì sao ba lựa chọn đáng chú ý lại tối giản.** Ở đúng ba chỗ mà một framework thông dụng sẽ tự định nghĩa lại hành vi đã khóa trong hợp đồng, ADR chọn cách tối giản: **queue** dùng bảng DB thay vì broker (tránh chủ sở hữu trạng thái thứ hai); **Telegram** gọi thẳng API thay vì bot framework (retry của framework sẽ vi phạm `AMD-B03` — không tự gửi lại khi `unknown`); **CLI/ACP** dùng `subprocess` thay vì một lớp orchestration giấu tool call (LangChain bị loại thẳng vì lý do này — `ADR-0010` đòi chứng minh được tool bị khóa).
- **Phạm vi ảnh hưởng nếu Owner đảo.** Chỉ card và mã. **Không** `contracts/`, không `acceptance/`, không `precode/`. Mọi lựa chọn nằm dưới lớp hợp đồng.
- **Liên kết.** `ADR-0011`, `ADR-0006` (phụ thuộc), `ADR-0005`, `ADR-0010`, `AMD-B03`, `AMD-B11`, `REQ-D07`, `REQ-D09`, `REQ-D48`, `REQ-D49`, `REQ-D50`, `REQ-D59`, `REQ-S6.4-01..03`, I11, I15.

### `PROV-PC00-08` — Chế độ vận hành khi bắt đầu ghi mã

- **Bối cảnh.** `OD-20260907-02` mục 2 cho phép bắt đầu Giai đoạn 0 và Giai đoạn 1 của `docs/master-plan.md`. Owner **không** phát biểu gì về chế độ vận hành; biên bản tự khai mục này là *"hàm ý bởi mục 2"* và là một **ruling của Coordinator**, đã khai báo tường minh.
- **Vấn đề.** `agent_profile/protocol.md` §2 giới hạn `DOCUMENTARY_DRAFT` cho *"draft documentation/contract/schema/examples, không code product"*, và đòi chế độ `ENFORCED` phải có capability broker, tool sandbox, authority/lease registry, danh tính đã xác thực, đồng hồ, lock/CAS + fencing tại commit và audit log bền vững. **Không guard nào trong số đó tồn tại** trong phiên này. Đọc nguyên văn hồ sơ thì việc ghi mã sản phẩm phải `BLOCKED`.
- **Ruling.** Chỉ thị tường minh của Owner **đứng trên** hồ sơ đã pin — đó là `instruction_precedence` mà `agent_profile/registry.json` khai và là câu mở đầu của `protocol.md` ("Instruction Owner và ràng buộc nền tảng luôn đứng trên hồ sơ"). Vì vậy việc ghi mã tiến hành dưới **đúng** cơ chế đã dùng cho tài liệu: lease độc quyền theo dõi bằng thông điệp, tập ghi chính xác (exact write set) trong từng TASK_PACKET, và review độc lập theo route của `protocol.md` §7.
- **Trạng thái.** **`ACCEPTED (OD-20260907-03)`** — Owner phê chuẩn ngày 2026-09-07 bằng câu *"accept both, start phase 2"*, trong đó "both" trỏ đích danh mục này và `AMD-ENT-owner-01` (`precode/owner-decisions-03.md`, authority `AUTH-OWNER-20260907-04`). **Rủi ro còn lại được Owner thừa nhận, không phải được xoá:** ba chế độ hỏng ở gạch đầu dòng dưới vẫn nguyên, `enforcement` trong `agent_profile/registry.json` vẫn `NOT_IMPLEMENTED`, và phải giữ như vậy cho tới khi có runtime guard thật. `ACCEPTED` ở đây nghĩa là Owner chấp nhận **vận hành với** rủi ro đó.
- **(Lịch sử) Trạng thái trước vòng ba.** **`PROVISIONAL`**, `decision_owner: Coordinator` dưới chỉ thị của Owner (`AUTH-OWNER-20260907-03`); **Owner có thể phản đối**. Khi đó đây **không** phải `ACCEPTED (OD-20260907-02)`: bốn mục kia trong biên bản vòng hai là câu trả lời của Owner, mục này là suy luận của Coordinator từ một câu trả lời khác. Sự khác biệt đó đã được giữ đúng cho tới khi Owner trả lời tường minh — đoạn này giữ lại để truy vết.
- **Rủi ro còn lại — phải đọc đúng.** "Lease độc quyền" ở giai đoạn mã vẫn là **kỷ luật bằng thông điệp**, không phải một khoá thật. Cụ thể: (a) một agent ghi ra ngoài tập ghi của mình sẽ **không** bị nền tảng chặn — chỉ bị phát hiện ở handoff hoặc audit, tức **sau** khi byte đã lên đĩa; (b) hai Worker chạy song song trên cùng một file không có fencing thực, nên "ghi đè im lặng" là một chế độ hỏng có thật, được giảm bằng cách Coordinator **không** cấp hai packet chồng path chứ không phải bằng cưỡng chế; (c) không có audit log bền vững do một service ghi — bằng chứng nằm ở handoff do chính Worker viết, nên nó chứng minh được *cái gì đã đổi* (hash trước/sau) nhưng **không** chứng minh được *không có gì khác đã đổi* ngoài phạm vi rehash. Ba điều này áp cho mã đúng như đã áp cho tài liệu; điều mới là **hậu quả** của một lần ghi sai giờ có thể là mã chạy được chứ không chỉ một câu văn sai.
- **Ranh giới không được nới bởi ruling này.** Không secret; không gọi thật X/Telegram/AI (E3 vẫn `NOT_RUN`); mạng **chỉ** để cài gói đã khai báo từ PyPI/npm (mục 4 của biên bản), không cho mục đích nào khác. Trần claim của đầu ra Giai đoạn 0/1 là `IMPLEMENTATION_VERIFIED`, không bao giờ INTEGRATION/LIVE; `product_status` giữ `NOT_READY_FOR_PRODUCT_CODE` cho tới khi G5 đạt đầy đủ và bằng chứng Giai đoạn 1 được đăng ký.
- **Nếu Owner phản đối.** Phương án thay thế duy nhất nhất quán với hồ sơ là dừng ghi mã cho tới khi có runtime guard thật (capability broker + lease service + fencing), tức hoãn Giai đoạn 0 và 1 vô thời hạn. Không có phương án trung gian nào: `protocol.md` §2 nói rõ *"Nếu không verify được runtime guards → BLOCKED, không fallback sang soft prompt"*, và ruling này **chính là** một fallback sang soft prompt — được biện minh bằng chỉ thị Owner, không bằng hồ sơ.
- **Liên kết.** `OD-20260907-02` mục 3 và mục 4, `agent_profile/protocol.md` §2 và §7, `agent_profile/worker.md` §"Sáu điều kiện", `docs/master-plan.md` Giai đoạn 0 và 1, `PROV-PC00-07`, `ADR-0011`.

### 8.5 Đăng ký quyết định PROVISIONAL của các gói khác

PC00 là nơi tập trung quyết định; các gói dưới đây tự đưa quyết định trong phạm vi của mình, PC00 **ghi nhận** để chúng không rơi khỏi tầm nhìn của Owner và của PC09. PC00 **không** thẩm định lại nội dung kỹ thuật — chủ sở hữu vẫn là gói gốc.

| ID | Gói | Quyết định | Trạng thái | Đưa lên Owner ở mục |
| --- | --- | --- | --- | --- |
| `PROV-PC03-01` | PC03 | Quy tắc DST: giờ không tồn tại → chạy tại instant đầu tiên ≥ giờ danh nghĩa; giờ lặp → lấy lần xuất hiện đầu | PROVISIONAL | Timezone |
| `PROV-PC03-02` | PC03 | `run_now_active_run_policy = coalesce` (bấm lặp trả run đang có, không tạo run mới) | PROVISIONAL | — (kỹ thuật) |
| `PROV-PC03-03` | PC03 | Tách ngân sách `provider_unavailable_waits` khỏi `analysis_attempts_per_item` | PROVISIONAL | — (kỹ thuật) |
| `PROV-PC03-04` | PC03 | `analysis_unknown_attempt_auto_rerun = 1` — **khác** `delivery.unknown` (không bao giờ tự chạy lại). PC03 tự ghi rằng đây là chỗ họ diễn giải khác câu "never retry unknown outcome" của packet và **đề nghị Auditor soi kỹ** | PROVISIONAL | Tham số AI |
| `PROV-PC03-05` | PC03 | 41 giá trị lease/backoff/window trong `retry-policy.yaml`; `lease_ttl_collector = 120 s` neo vào `heartbeat 30 s` + `online_threshold 90 s` của PC01 | PROVISIONAL | Tham số vận hành |
| `PROV-PC03-06` | PC03 | `storage.maintenance` là trạng thái Operator mở có chủ đích; `T-ST-08` giữ nợ đối soát khi sự cố ổ đĩa xen vào sau restore | PROVISIONAL | — (kỹ thuật, bảo vệ I15) |
| `PROV-PC04-01` | PC04 | First-announcement sau merge = **sớm nhất**, có audit | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC04-02` | PC04 | Backfill khóa theo **chữ tag đã chuẩn hóa** (`subscription_identity_hash`); re-add **không** cấp lại quyền backfill | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC04-03` | PC04 | Backfill tiêu thụ khi publish commit **và** phần nới có ≥ 1 ứng viên; phần nới rỗng thì entitlement ở lại | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC04-04` | PC04 | arXiv phiên bản mới = `prior_reference` (`reference_reason = 'new_work_version'`), **không** phải phát hiện mới | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC04-05` | PC04 | Target chỉ-có-post: "đã công bố" suy từ `report_item` của report đã publish | ACCEPTED (OD-20260907-01) | — (kỹ thuật) |
| `PROV-PC04-06` | PC04 | Ngưỡng similarity `0.8000` mang nhãn `PROVISIONAL_BOOTSTRAP` + `threshold_calibration_state = 'uncalibrated'`; **cấm** tuyên bố chỉ tiêu §1.4 khi còn `uncalibrated` | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC04-07` | PC04 | Tham số mật độ: `r = 0.8000`, `min_members = 3`, `K = 4`, `min_prior_windows = 2`, `min_delta = 2.0000`, `ε = 1.0000`, `max_emerging_directions = 3` | ACCEPTED (OD-20260907-01), cổng REQ-A4 | Báo cáo và mật độ |
| `PROV-PC04-08` | PC04 | `max_items_per_period = 50`; vượt hạn mức → `pending_item_ledger(budget_exceeded)`, **không** bị bỏ | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC04-09` | PC04 | Kỳ rỗng để lại **một** hàng `report(status='aborted', abort_reason='empty_period')` — phương án (b), **không** theo khuyến nghị (a) của Coordinator. Lý do: `coverage_window` không có khóa idempotency, nên dưới (a) một lần mất ACK sẽ thử tiến coverage lần hai và trả `CONFLICT` | ACCEPTED (OD-20260907-01) | Báo cáo và mật độ |
| `PROV-PC08-01` | PC08 | Tham số xác thực: Argon2id (64 MiB / t=3 / p=1); session idle 12 h, absolute 30 d; CSRF 128 bit; login 5 lần/15 phút, lockout 15 phút | ACCEPTED (OD-20260907-01) | Vận hành và bảo mật |
| `PROV-PC08-02` | PC08 | Token worker 256 bit, quyền `0600`, rotation 180 ngày, overlap 24 h; `task_credential_ttl = 900 s` **buộc bằng** `lease_ttl_analysis` của PC03 | ACCEPTED (OD-20260907-01) | Vận hành và bảo mật |
| `PROV-PC08-03` | PC08 | Backup 03:00 hằng ngày, timeout 600 s, retention 14 daily / 8 weekly / monthly vô thời hạn; **RPO 24 h, RTO 2 h** | ACCEPTED (OD-20260907-01) | Vận hành và bảo mật |
| `PROV-PC08-04` | PC08 | Audit retention 365 ngày; bản ghi thao tác xóa giữ **vô thời hạn**; AEAD 256-bit với master key ngoài DB | ACCEPTED (OD-20260907-01) | Vận hành và bảo mật |
| `PROV-PC08-05` | PC08 | Giới hạn fetch ngoài: redirect ≤ 3, timeout 10 s / 30 s, body ≤ 10 MiB | ACCEPTED (OD-20260907-01) | — (kỹ thuật) |

**Phạm vi cố ý để trống, có gate** (không phải quyết định, và không được lấp bằng số bịa): `research_connector_rate_limit` của PC03 giữ bốn giá trị `null` với `status: PLACEHOLDER_KC` và chỉ một sàn an toàn `min_interval_ms = 3000`, căn cứ `REQ-A6` vẫn ở trạng thái **KC**. PC05 phải điền từ tài liệu chính thức trước khi research connector được coi là `CONTRACT_READY`.

> **Cập nhật 2026-09-07 (`OD-20260907-04` mục 2, thi hành bởi `AUTH-COORD-REQA6` / `PKT-PC03-FIX-REQA6`).** Đoạn trên giữ nguyên làm lịch sử; trạng thái hiện hành của `REQ-A6` là **`PARTIALLY_RESOLVED`**, chi tiết ở **§8.13**. Tóm tắt: nửa **arXiv** đã giải từ tài liệu chính thức (1 request / 3 giây, một kết nối đồng thời — `https://info.arxiv.org/help/api/tou.html`, đọc ngày 2026-09-07; cùng trang, cùng ngày: tài liệu **không** đặt yêu cầu định danh cho caller); nửa **OpenAlex** **chưa** giải và `research_connector_rate_limit` vẫn `status: PLACEHOLDER_KC` với hai giá trị `null`. `SG-A6` của `agent-tasks/TC-research-connector-metadata.md` **không** được nới, và research connector **vẫn không** `CONTRACT_READY`.
>
> **Cập nhật thứ hai, cùng ngày 2026-09-07 (phần 2 của cùng packet, sau khi Owner mở rộng allowlist thêm `help.openalex.org`).** Trạng thái hiện hành của `REQ-A6` là **`RESOLVED`** — **cả bốn** dữ kiện đã đọc từ tài liệu chính thức, chi tiết ở **§8.13.2**. `contracts/retry-policy.yaml` `research_connector_rate_limit` **không còn** `PLACEHOLDER_KC` (nay `DOCS_derived`, v0.8.0), và điều kiện của `SG-A6` — "bốn giá trị còn `null`" — **không còn đúng**. Điều **vẫn đúng**: việc này **không** tự nâng trần claim của `MOD-research-connector`; `CONTRACT_READY` của module là kết luận của PC05/Coordinator trên toàn bộ cổng của nó, không phải hệ quả của một khối hợp đồng.

### 8.6 Câu hỏi Owner phát sinh trong đợt FIX3

| Câu hỏi | Gói nêu | Đã có mục trong `owner-decision-request.md` |
| --- | --- | --- |
| `schedule_timezone` thật (nếu khác `Asia/Ho_Chi_Minh` thì mọi fixture lịch của PC03/PC04 phải dựng lại) | PC03, PC04 | mục **Timezone** (đã có, nay ghi thêm hệ quả) |
| `per_run_post_limit` / `per_run_duration_limit` thật (`REQ-OQ05`) và mốc lịch thật (`REQ-OQ06`) | PC03 | mục **Bộ giá trị mặc định** (đã có) |
| Tám quyết định báo cáo/mật độ của PC04, gồm backfill khóa theo chữ tag chuẩn hóa, ngưỡng `PROVISIONAL_BOOTSTRAP` và kỳ rỗng phương án (b) | PC04 | mục **Tham số báo cáo và mật độ** (mới) |
| Hệ quả của việc purge xóa credential đăng nhập; dữ liệu purge vẫn nằm trong backup | PC08 | mục **Phạm vi của `data.purge_all`** (đã có, nay bổ sung hai hệ quả) |
| RPO 24 h / RTO 2 h, retention backup, cơ chế xác thực và các tham số session | PC08 | mục **Vận hành và bảo mật** (mới) |
| `CSRF_REJECTED` và `run.resume` từ `blocked` | Coordinator FIX3 | mục **Hai thay đổi kỹ thuật cần Owner biết** (mới) |

### 8.7 Đăng ký quyết định của PC09 và PC10 (đợt FIX5, ruling R5-06)

Tiếp nối §8.5. PC00 **ghi nhận, không thẩm định lại**; chủ sở hữu vẫn là gói gốc.

**PC09 — đã kiểm: không có quyết định sản phẩm nào, không có câu hỏi Owner nào.** Packet FIX4 dự đoán "PC09: none expected"; kiểm `evidence/handoffs/PC09-handoff.md` §6.2 xác nhận đúng — ba quyết định của PC09 đều mang tính **phương pháp**, nằm trong phạm vi ủy quyền của verification owner, và không đổi cam kết nào với Owner. Ghi lại để chúng không vô hình:

| ID | Quyết định | Trạng thái | Cần ai |
| --- | --- | --- | --- |
| `PROV-PC09-01` | Quy tắc `coverage_status` của `acceptance/traceability.csv`: một dòng nhận `BLOCKED_B<nn>` khi nó nằm trong danh sách "REQ ảnh hưởng" của `AMD-B<nn>` — tức **văn bản cam kết của chính dòng đó** sẽ đổi nếu Owner phê chuẩn amendment. **84 dòng** rơi vào diện này; cột `notes` vẫn giữ độ phủ nền để không mất thông tin | PROVISIONAL | Coordinator (nếu muốn quy tắc khác thì số ở `review.md` §2 phải tính lại) |
| `PROV-PC09-02` | Header của `traceability.csv` đặt ở front-matter `precode/review.md`, theo đúng tiền lệ đã chấp nhận cho `requirements.csv` (một dòng comment sẽ làm `csv.DictReader` đọc sai). `e0_check` `E0-17` kiểm sự tồn tại và đầy đủ của header thay thế | PROVISIONAL | Coordinator |
| `PROV-PC09-03` | `x-contract.deviations` chấp nhận **tên trường đồng nghĩa**: `analysis-result.schema.json` của PC06 dùng bộ tên dài hơn bộ `{rule, deviation, reason, evidence_refs}` của ruling FIX4; PC09 chấp nhận và ghi note nêu đích danh tên đã dùng, thay vì FAIL một deviation đã khai đầy đủ về nội dung | PROVISIONAL | Coordinator (ép đúng bốn tên là một sửa nhỏ ở PC06 cộng một dòng ở `e0_check`) |

Đáng ghi thêm — **PC09 từ chối nâng nhãn**: packet của nó viết "expect G0–G3 `MET_PROVISIONAL` at best", nhưng PC09 ghi `G0 = MET_PROVISIONAL` và **`G1, G2, G3 = PARTIALLY_MET`**, vì mỗi cổng còn ít nhất một điều kiện đo được và chưa đạt (G1-X5: 26 cạnh; G2-X3: TSR-A01; G3-X5: `REQ-A6` và `CR-PC07-04` còn **KC**). Đây là hành vi đúng theo SRC-PLAN §2 và §9 — không nâng nhãn bằng suy diễn — và PC00 ghi lại để không ai "sửa" nó thành `MET_PROVISIONAL` cho gọn.

**PC10 — ba giả định PROVISIONAL và một ngoại lệ định dạng.** PC10 tự khai **không** tạo quyết định sản phẩm nào.

| ID | Giả định | Trạng thái | Cần ai |
| --- | --- | --- | --- |
| `PROV-PC10-01` | Layout đường dẫn theo stack A: `server/app/<domain>/…`, `collector/app/…`, `worker/app/…`, `server/app/web/…`, `probe/x_feasibility/…`, `tests/contract/…`, `tests/integration/…` | PROVISIONAL | **Owner** — đây là hệ quả trực tiếp của `ADR-0006` chưa được trả lời. Nếu Owner chọn B/C thì **chỉ §3 và §8** của mỗi card phải viết lại, không phải hợp đồng |
| `PROV-PC10-02` | Ba không gian ID mới: `EVM-<Task ID>` (evidence manifest của card), `SG-<nn>` (stop condition trong card), `PC10-PIN-<ngày>` (pin epoch). Baseline §3 chưa có ID nào phục vụ ba việc này | PROVISIONAL | Coordinator — đổi được bằng một lần sửa generator |
| `PROV-PC10-03` | Trần claim `LIVE_FEASIBILITY_VERIFIED` cho card SP1 và `CONTRACT_ONLY` cho đường CLI/ACP của card adapter; hai nhãn này **không** có trong bảng claim label của SRC-PLAN §2 | **Đã có ruling** | Ruling `R5-07` đã chốt: thay `CONTRACT_ONLY` bằng nhãn của SRC-PLAN §2. PC10-FIX1 thực hiện. `LIVE_FEASIBILITY_VERIFIED` **có** trong SRC-PLAN §2 nên giữ nguyên |

**Ngoại lệ định dạng của PC10 (khai báo, không phải thiếu sót).** Card `TC-*.md` **không** mang contract header đầy đủ của baseline §3; chúng mang front-matter riêng của card (`card_id`, `milestone`, `gate`, `stack_decision`, `claim_ceiling`, `owner_modules`, `scenario_refs`, `invariant_refs`, `evidence_manifest_id`, `source_refs`, `baseline_pin_ref`, `coding_precondition`). Lý do PC10 nêu: card **không phải hợp đồng** — nó là lệnh giao việc pin một hợp đồng, nên `producers`/`consumers`/`dependencies` không có nghĩa; thông tin tương đương nằm ở §4, §5 và §11 của card. Bốn file khung (`TEMPLATE.md`, `agent-tasks/README.md`, `WALKTHROUGH.md`, `precode/change-control.md`, `precode/README.md`) **có** mang header đầy đủ.

Đây là ngoại lệ thứ **tư** cùng loại trong dự án, sau ADR (ruling R-05), `requirements.csv` và `traceability.csv` (`PROV-PC09-02`). Ruling `R5-07` yêu cầu PC10 khai báo nó trong `agent-tasks/README.md`. **Đề nghị của PC00:** khi Coordinator sửa baseline §3 lần tới, gom cả bốn thành một câu quy tắc chung — *"file không phải hợp đồng (decision record, registry dạng CSV, task card) mang header riêng đã khai báo, liệt kê tại …"* — thay vì bốn ngoại lệ rời rạc mà mỗi lượt audit lại phải đối chiếu lại. Xem `CR-PC00-10`.

Ngoại lệ phụ: `precode/README.md` và `precode/change-control.md` không tự pin hash của chính mình (chicken-and-egg); hash của chúng nằm ở bảng §2 của handoff PC10.

### 8.8 Invariant phát sinh I16 và I17 (finding `F-A2R1-07`, ruling FIX6 F-07)

Baseline §3 cho phép `I16+` **chỉ khi có decision record**. Hai invariant này đã được `contracts/data/invariants.md` định nghĩa và đang được `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `contracts/data/entities.yaml` và `precode/review.md` trích dẫn, nhưng decision record thì chưa tồn tại. Audit `A2-R1` nói đúng trọng tâm: *"Defining an invariant inside the contract that consumes it is what the rule exists to prevent."* Mục này lấp đúng chỗ đó. Lập luận kỹ thuật là của PC02 và tôi **không** viết lại; tôi ghi nhận, gắn trạng thái và nêu phần còn thiếu.

#### `PROV-PC00-05` — I16: Attempt không bao giờ là kết quả

- **Phát biểu** (nguyên văn `contracts/data/invariants.md` §I16). Không có đường đọc nào biến một hàng `analysis_attempt` thành kết quả phân tích: mọi truy vấn "kết quả của target X" chỉ đọc `analysis` với `status = 'valid'`. Attempt là append-only; `outcome` chỉ được ghi một lần từ trạng thái đang chạy sang trạng thái cuối.
- **Vì sao cần một invariant riêng, không phải một dòng phụ của I04.** SRC-PLAN §3 B07 yêu cầu "attempt lỗi không tính là kết quả hoàn thành" và §8.2 yêu cầu "không ghi output sai schema thành `valid`". Yêu cầu đó **cắt ngang** I04: I04 nói về tính **duy nhất theo key** của kết quả, không nói gì về việc một attempt có thể bị **đọc nhầm** thành kết quả. Vì PC02 tách hai bảng (`analysis`, `analysis_attempt`), ranh giới giữa chúng cần một phát biểu có oracle riêng.
- **Nguồn.** SRC-PLAN §3 hàng B07, §8.2; SRC-SPEC §9.3 (hàng "AI lỗi một mục"), §10.2. Qua `AMD-B07` và `ADR-0008` (analysis key và generation).
- **Owner/hợp đồng.** `contracts/data/entities.yaml` → entity `analysis_attempt`; `transactions[TXN-analysis-accept]`.
- **Counterexample (phải FAIL).** UI hoặc report builder đọc attempt cuối cùng để hiển thị summary khi chưa có hàng `valid` → mục đó **phải** hiện là thiếu summary và vào `pending_item_ledger`, report `quality = 'partial'` (B17, `AMD-B17`).
- **Oracle.** Với mọi target không có hàng `analysis` valid: view "summary của target" trả rỗng **và** `#pending_item_ledger[target_key = T, state='pending'] = 1`. Với mọi hàng `analysis` valid: tồn tại **đúng một** attempt `accepted` được trỏ bởi `accepted_from_attempt_id`. `#analysis_attempt[outcome='timeout_unknown' AND cost_uncertain = false] = 0`.
- **Scenario.** Dương: `SC10`, `SC50`. Âm: **`SC56`** — *"Ghi 0 cho usage không biết, tự bật fallback, hoặc đếm attempt là kết quả — ba phản chứng của I14 và I16"*, khai `polarity: negative`. Hỗn hợp: `SC28` (worker chết sau AI call) — trích I16 nhưng khai `mixed`, và theo `F-A2R1-10` thì `mixed` không tính cho cực nào, nên nó **không** thay thế được `SC56`.
- **Lịch sử của mục này.** Ở bản đầu (FIX5) I16 **không** có cực âm nào: chỉ có `SC28` khai `mixed`. PC00 ghi khoảng trống đó thành chữ và báo `CR-PC00-11` thay vì tự khai lại polarity của một scenario mình không sở hữu. PC09 cấp `SC56` ở đợt FIX7 và khoảng trống đã đóng; anchor trong `precode/baseline.json` mang `negative_scenarios: ["SC56"]`. Cùng đợt đó PC09 cũng lấp hai cực còn thiếu của các invariant khác: **`SC54`** (âm, phản chứng của I04 — hai kết quả hợp lệ cho cùng một `(analysis_key, generation)` là không thể) và **`SC55`** (dương, mặt dương của I14 — usage không biết được ghi là `unknown` với ba trường NULL). Ba ID đó đã có anchor riêng trong `baseline.json`.
- **Trạng thái.** `PROVISIONAL`, `decision_owner: Coordinator (provisional, technical)` — theo `CR-PC00-12`. Đây là một **data invariant kỹ thuật**: nó phát biểu ranh giới đọc giữa hai bảng (`analysis` và `analysis_attempt`) chứ không đổi cam kết nào Owner đã chọn. `REQ-D19` ("mỗi mục có summary hiển thị ngay tại mục") vẫn đúng nguyên văn; I16 chỉ nói rằng khi **chưa** có kết quả hợp lệ thì mục đó phải hiện là thiếu summary, đúng như `AMD-B17` đã chốt. Vì vậy **không cần** một mục riêng trong `precode/owner-decision-request.md`, trừ khi Owner phản đối.
- **Nếu bị bác bỏ.** Không có phương án thay thế trong cùng mô hình hai bảng: nếu không cấm đường đọc attempt thì `AI_OUTPUT_INVALID` và `AI_ATTEMPT_UNCERTAIN` không có oracle phân biệt được "chưa có kết quả" với "có kết quả kém". Khi đó PC06 phải quay lại mô hình một bảng, và `AMD-B07` phải viết lại.
- **Liên kết.** I04 (cực âm riêng: `SC54`), I14 (cực dương riêng: `SC55`), `REQ-D19`, `REQ-D25`, `REQ-D26`, `REQ-AC10`, `AMD-B07`, `AMD-B17`, `ADR-0008`, `SC10`, `SC28`, `SC50`, `SC56`.

#### `PROV-PC00-06` — I17: Merge identity không làm đổi bất kỳ snapshot lịch sử nào

- **Phát biểu** (nguyên văn `contracts/data/invariants.md` §I17). Một transaction merge chỉ được ghi các cột nằm trong merge move-set (`entities.yaml` → `transactions[TXN-identity-merge].merge_move_set`). Cụ thể, sau merge: `saved_snapshot` (mọi cột, kể cả `target_key_at_save`), `ingest_receipt`, `analysis_attempt`, `identity_merge_audit` cũ, và `report_item` thuộc report `published` đều **byte-identical** với trước merge.
- **Vì sao cần một invariant riêng.** SRC-PLAN §11 PC02 yêu cầu tường minh "cách không làm đổi historical snapshot sau merge". I03 chỉ nói về **tính đúng của identity**; I08 chỉ nói về **Saved**. Không invariant nào của SRC-PLAN §7 phát biểu ràng buộc **chéo** giữa thao tác merge và các bảng lịch sử khác (report đã publish, receipt, attempt). I17 lấp đúng khoảng trống đó và cho merge một oracle **đếm được**.
- **Nguồn.** SRC-PLAN §11 PC02, §9.1; SRC-SPEC §7.3, §3.5 (D29), §3.6 (D55). Qua `AMD-B15` và `ADR-0009` (identity, alias, target tagged union).
- **Owner/hợp đồng.** `contracts/data/entities.yaml` → `transactions[TXN-identity-merge]`; `referential_integrity.historical_snapshot_rule`; `contracts/data/identity.md` §6.4.
- **Positive scenario** (nguyên văn nguồn). Owner đã Save work W1 lúc 10:00 (snapshot S1); 11:00 W1 bị merge vào W2. Con trỏ `saved_item.target_work_id` chuyển sang W2 và `moved_by_merge_id` được ghi; **S1 không đổi một byte**, `target_key_at_save` vẫn là `work:<W1>`. Fixture `a-merge-doi-arxiv.json`.
- **Scenario.** Dương: `SC07`, `SC12`. Âm: `SC23` (identity conflict). Hỗn hợp: `SC09`, `SC13`, `SC32`. I17 đã có đủ một cực dương và một cực âm khai tường minh **ngay từ đầu**; I16 đạt điều đó sau khi PC09 cấp `SC56` ở đợt FIX7.
- **Trạng thái.** `PROVISIONAL`, `decision_owner: Coordinator (provisional, technical)` — theo `CR-PC00-12`. Đây là một **data invariant kỹ thuật**: nó là cơ chế **thực thi** của `REQ-D29` (XN), `REQ-D55` (UQ) và `AMD-B15` sau khi merge, không phải một lựa chọn sản phẩm mới. Owner đã chọn "không báo lại" và "Saved là snapshot"; I17 chỉ nói merge không được phép âm thầm làm hai điều đó sai. Vì vậy **không cần** một mục riêng trong `precode/owner-decision-request.md`, trừ khi Owner phản đối.
- **Nếu bị bác bỏ.** Không có cách nào khác giữ `REQ-AC12` ("Save bền", snapshot không đổi) đúng qua một lần merge: nếu merge được phép ghi ngoài move-set thì snapshot đã lưu có thể đổi và `REQ-AC09` mất mốc `first_announced`.
- **Liên kết.** I03, I07, I08, `REQ-D29`, `REQ-D55`, `REQ-AC07`, `REQ-AC09`, `REQ-AC12`, `AMD-B15`, `ADR-0009`, `SC07`, `SC12`, `SC23`.

**Đã cập nhật `precode/baseline.json`:** `id_conventions.invariant.form` từ `I01..I15` thành `I01..I17`, kèm ghi chú rằng I16/I17 được nhận vào **đúng theo** điều kiện "chỉ khi có decision record" và trỏ về mục này; `I18+` vẫn phải có decision record mới. Anchor của chúng nằm ở nhóm mới `source_anchors.PROJECT.invariants` — **không** đặt trong nhóm `SRC-PLAN`, vì chúng không có trong văn bản SRC-PLAN và một anchor giả nguồn sẽ là chính lớp lỗi mà finding này phạt.

### 8.9 Trạng thái các change request do PC00 phát ra

`precode/review.md` §12 hợp nhất toàn bộ 75 CR của dự án; bảng dưới đây chỉ là **phần của PC00**, dùng đúng trạng thái đó để hai file không lệch nhau. Bốn dòng `CR-PC00-01`, `-03`, `-09`, `-10` trước đây không có trạng thái ở đâu (`F-A2R1-04`) — nay có.

| CR | Nội dung tóm tắt | Trạng thái | Căn cứ |
| --- | --- | --- | --- |
| `CR-PC00-01` | Đối chiếu `requirement_refs`/`decision_refs` của PC01 và PC02 với registry và ADR của PC00 | **Đã giải** | Lượt hòa giải FIX1: PC01/PC02 đã pin lại tham chiếu theo `precode/requirements.csv` và `precode/adr/`; củng cố bởi `F-A1R1-03` đã VERIFIED |
| `CR-PC00-02` | PC09 theo dõi `F-PC00-01`/`F-PC00-02` ở G0 | Còn mở, **đã xử lý** ở `precode/gates.yaml` G0 | `review.md` §12 |
| `CR-PC00-03` | AMD-B02 (ánh xạ enum) và AMD-B08 (timestamp mili giây + ingest sequence) là đầu vào bắt buộc của `run.yaml` và `time-and-tags.md` | **Đã giải** | PC03 và PC04 đã land đúng hai giá trị này; cần một lượt xác minh độc lập trên epoch mới |
| `CR-PC00-04` | PC01 dùng đúng tên operation xóa và `SC32` | **Đã được đáp ứng ngược dòng** | `review.md` §12 |
| `CR-PC00-05` | Đưa `EV-PC00-06` và anchor SC vào tập E0 / traceability | Còn mở, **đã xử lý** | `review.md` §12 |
| `CR-PC00-06` | Đối chiếu `scenarios.yaml` với anchor; anchor ≠ scenario đã viết | Còn mở, **đã xử lý một phần** | `review.md` §12; `R5-08` giao PC09 điền `fixture_refs` cho 12 scenario |
| `CR-PC00-07` | `ports.yaml` trích một REQ id **không tồn tại** trong registry (SRC-SPEC không có §8.4; §8.4 là của SRC-PLAN) → phải trỏ sang `REQ-S9.3-08`; `run.resume` mở guard cho `blocked`; `data.purge_all.scenario_refs: [SC44]` | **Đã được đáp ứng ngược dòng** | `review.md` §12; PC01-FIX3 đã gỡ id sai |
| `CR-PC00-08` | Đăng ký `CSRF_REJECTED` ở `errors.yaml`; thu hẹp `FORBIDDEN_EDGE` | **Đã được đáp ứng ngược dòng** | `review.md` §12; `CR-PC08-03` cùng nhóm |
| `CR-PC00-09` | Chủ đề SC45–SC48 trong ruling R4-03 khác `acceptance/fixtures/telegram/README.md` | **Đã giải** | `PKT-PC00-FIX3`: PC00 lấy chủ đề từ README (nguồn packet chỉ đích danh); bốn chủ đề trong ruling tương ứng fixture a/b/d/e vốn đã trích `SC14`/`SC25` |
| `CR-PC00-10` | Gom bốn ngoại lệ header rời rạc thành một quy tắc chung ở baseline §3 | **Đã giải** | Coordinator đã ban hành quy tắc header chung; bốn ngoại lệ (ADR, `requirements.csv`, `traceability.csv`, task card) nay nằm dưới cùng một câu quy tắc |

**Lưu ý về cách diễn đạt hàng `CR-PC00-07`.** Hàng đó cố ý **không** viết ra id sai: id ấy đã bị PC01-FIX3 gỡ khỏi `ports.yaml` và không tồn tại trong `precode/requirements.csv`, nên nhắc lại nguyên văn sẽ tạo một token trông như trích dẫn hợp lệ và làm gate quét id báo động (`CR-PC01-12`). Nội dung của CR được giữ nguyên: id sai là gì (một REQ thuộc một mục §8.4 mà SRC-SPEC không có) và id đúng là `REQ-S9.3-08`. Đừng "khôi phục" id cũ vào file này.

**Lưu ý về mức bằng chứng.** "Đã được đáp ứng ngược dòng" trong bảng này là **lời tự khai của gói nhận**, đúng như `review.md` ghi: PC09 ghi nhận chứ không tự xác minh từng cái. Không dòng nào ở đây là `CLOSED`; đóng một finding hay một CR cần authority được chỉ định sau khi có xác minh độc lập trên epoch mới, và người xác minh không được là người viết bản sửa.

### 8.10 Quyết định của `OD-20260907-02` (vòng hai, 2026-09-07)

Biên bản vòng hai — `precode/owner-decisions-02.md`, authority `AUTH-OWNER-20260907-03`, evidence
`session_0156UBBHDSeC9soECzSVUb3U` — có **năm** mục. Bảng dưới đây ghi chúng đúng như biên bản phân loại:
mục nào là câu trả lời của Owner thì mang `ACCEPTED (OD-20260907-02)`, mục nào biên bản tự khai là *"hàm ý"*
hoặc *"ruling của Coordinator"* thì **không** được mang nhãn đó.

| # | Quyết định | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| 1 | Phê chuẩn `ADR-0011` (framework và toolchain cho stack B, 14 tầng) | `ACCEPTED (OD-20260907-02)` | §8 `PROV-PC00-07`; `precode/adr/ADR-0011-frameworks-and-toolchain.md`; `precode/adr/README.md` |
| 2 | **Lối vào Giai đoạn 0 và Giai đoạn 1** — bắt đầu ghi mã theo `docs/master-plan.md`: Giai đoạn 0 (bố cục repo + CI) đóng `G5-X4`; Giai đoạn 1 (M1: kho dữ liệu, ingest, auth, storage readiness) được cấp lối vào cổng G5 cho bốn card `TC-ingest-idempotent-ack-lost`, `TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness` | `ACCEPTED (OD-20260907-02)` | Hàng này; `docs/master-plan.md`; `precode/gates.yaml` G5 **chưa** được cập nhật — `CR-PC00-20` |
| 3 | Chế độ vận hành cho mã (lease theo thông điệp, không có cưỡng chế OS) | `PROVISIONAL` | §8 `PROV-PC00-08` |
| 4 | Tải phụ thuộc từ PyPI/npm được phép; không mạng cho việc khác, không secret, không gọi thật | `PROVISIONAL` (hàm ý, ghi kèm `PROV-PC00-08`) | §8 `PROV-PC00-08` mục "Ranh giới" |
| 5 | Ngân sách tối đa 10 subagent Opus cho giai đoạn này | — (điều phối, không phải quyết định sản phẩm) | Sổ của Coordinator |

**Ba điều hàng số 2 KHÔNG làm.** (a) Nó **không** tự chuyển `G5-X4` sang `met: true` — đó là kết quả của việc
Giai đoạn 0 chạy xong và được xác minh, không phải của việc cấp phép bắt đầu; `precode/gates.yaml` thuộc PC09
và không nằm trong tập ghi của gói này (`CR-PC00-20`). (b) Nó **không** nâng trần claim của một file hợp đồng
nào: `OD-20260907-01` §4 vẫn là luật cho `precode/`, `contracts/` và `acceptance/`. (c) Nó **không** giải
`REQ-OQ03` — provider và model vẫn `OWNER_DECISION_REQUIRED` và vẫn chặn M3, nên Giai đoạn 3 vẫn bị chặn
đúng như trước.

### 8.11 Amendment kỹ thuật của Coordinator sau audit A3-R1

Tiếp nối §8.5 và §3. Khác với §3 — nơi mọi `AMD-B<nn>` đã `ACCEPTED (OD-20260907-01)` — mục này ghi
amendment thực hiện **sau** khi một file hợp đồng đã `CONTRACT_READY`, dưới thẩm quyền kỹ thuật của
Coordinator, và **chưa** có câu trả lời của Owner. PC00 **ghi nhận, không thẩm định lại** nội dung kỹ
thuật; chủ sở hữu vẫn là gói gốc (PC02).

| ID | Gói | Quyết định | Trạng thái | Đưa lên Owner ở mục |
| --- | --- | --- | --- | --- |
| `AMD-ENT-owner-01` | PC02 | `ENT-owner` (`contracts/data/entities.yaml`, 0.1.0 → 0.2.0) nhận đúng bốn trường: `password_hash` (chuỗi Argon2id encoded, nullable tới khi bootstrap, không read model nào trả về), `password_updated_at` (nullable), `failed_login_count` (NOT NULL DEFAULT 0), `locked_until` (nullable). Căn cứ `contracts/ops/secrets.md` §2.1–§2.3 (Argon2id; lockout 5 lần / 15 phút) và `REQ-D05`; thi hành qua `CR-TC-AUTH-02` + `CR-TC-AUTH-03` (`precode/change-control.md` §10); vá khoảng trống hợp đồng mà `F-A3R1-02` và `F-A3R1-06` chỉ ra | **`ACCEPTED (OD-20260907-03)`** — Owner phê chuẩn 2026-09-07 ("accept both"); trước đó là `PROVISIONAL` dưới `AUTH-COORD-PC02-FIX12` (cha `AUTH-OWNER-20260907-03`) | mục **Vận hành và bảo mật** (đã có — bổ sung hệ quả: `owner` nay giữ credential và trạng thái lockout) |

**Vì sao Coordinator ký được, và ký được tới đâu.** Amendment này làm hợp đồng dữ liệu khớp với một
file Owner **đã** chấp nhận (`PROV-PC08-01`: Argon2id, login 5 lần/15 phút, lockout 15 phút); nó không
đưa thêm một quyết định sản phẩm nào. Đó đúng là loại mâu thuẫn nội bộ giữa hai file đã đóng băng mà
`precode/change-control.md` §7 nói ruling của Coordinator đóng được. Nó **không** vượt qua ba giới hạn:
nó không mang nhãn `ACCEPTED (OD-20260907-01)` — biên bản ấy không hề nhắc bốn cột; nó **không** đóng
`F-A3R1-02` hay `F-A3R1-06` (finding theo vòng đời riêng của `protocol.md` §8); và nó **không** nâng
trần claim của `contracts/data/entities.yaml`, vốn giữ nguyên `CONTRACT_READY` — nhưng nội dung đã đổi
sau lượt xác minh A2-R4, nên **A3-R2 phải xác minh lại `ENT-owner` trên epoch mới**.

**Hệ quả đã biết.** `shared/rr_contracts` phải sinh lại; `owner` phải hội tụ về đúng một
`CREATE TABLE` (`F-A3R1-01`); và mọi task card pin hash `contracts/data/entities.yaml` **và file này**
chuyển `STALE` theo `precode/change-control.md` §4 (INV-06/INV-09) — chạy lại, không phải FAIL.

**Cập nhật vòng ba (`OD-20260907-03` mục 1).** Owner đã phê chuẩn amendment này. Điều được gỡ là **tính tạm
thời của hợp đồng**: nhãn `IMPLEMENTATION_VERIFIED` của card auth không còn đứng trên một amendment do
Coordinator ký. `contracts/data/entities.yaml` **giữ nguyên** `CONTRACT_READY` — biên bản không nâng nó.
Hai điều **không** đổi theo phê chuẩn này: (a) verdict của auditor giữ nguyên — `A3-R4` §6 ghi per-card claim
"unchanged", và một biên bản của Owner **không** phải một lượt xác minh độc lập; (b) `F-A3R1-02` và
`F-A3R1-06` **không** bị đóng — finding theo vòng đời riêng của `protocol.md` §8. Khối amendment trong chính
`contracts/data/entities.yaml` do `worker-W3n` cập nhật ở một packet song song, **không** phải ở đây.

### 8.12 Quyết định của `OD-20260907-03` (vòng ba, 2026-09-07)

Biên bản vòng ba — `precode/owner-decisions-03.md`, authority `AUTH-OWNER-20260907-04`, evidence
`session_0156UBBHDSeC9soECzSVUb3U` — có **ba** mục. Cả ba đều là câu trả lời tường minh của Owner (khác vòng
hai, nơi hai trong năm mục là suy luận của Coordinator), nên cả ba mang `ACCEPTED (OD-20260907-03)`.

| # | Quyết định | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| 1 | `AMD-ENT-owner-01` — bốn trường credential/lockout trên `owner` | `ACCEPTED (OD-20260907-03)` | §8.11 |
| 2 | `PROV-PC00-08` — ghi mã dưới lease theo dõi bằng thông điệp, không cưỡng chế OS | `ACCEPTED (OD-20260907-03)` | §8 `PROV-PC00-08` |
| 3 | **Lối vào Giai đoạn 2** — **2A** M0 probe khả thi X (card `TC-x-feasibility-probe`, `TC-collector-checkpoint-resume`); **2B** M2 paper connector (`research.fetch_work_metadata`, `research.get_connector_health` — **chưa có card, phải viết trước**) | `ACCEPTED (OD-20260907-03)` | Hàng này; `docs/master-plan.md`; `precode/gates.yaml` **chưa** cập nhật (`CR-PC00-20`) |

**Hai cổng vẫn chặn — biên bản nêu chúng trong cùng một câu với chữ "Start".**

1. **Probe 2A không được chạy live.** `contracts/ops/collector-probe.md` §6 mục **2–4** vẫn chặn, và
   probe phải chạy trên **máy của Owner**. (Mục 1 — D09, profile Chrome riêng — đã được `OD-20260907-01`
   trả lời.) "Start" cấp phép **viết** card và mã của 2A; nó **không** cấp phép một lần chạy thật.
   `REQ-AC16` và mọi mục `KC` không đổi.
2. **Connector 2B không được `CONTRACT_READY`.** `REQ-A6` chặn cứng cho tới khi **bốn** dữ kiện rate/identity
   được ghi từ **tài liệu chính thức**. Biên bản nói thẳng: **không con số nào được đoán**. Cho tới lúc đó
   `research_connector_rate_limit` giữ bốn `null` với `status: PLACEHOLDER_KC` và sàn `min_interval_ms = 3000`
   (§8.5). Quyền tải tài liệu đó qua mạng **chưa được cấp** — biên bản liệt kê nó ở phần "không quyết".

**Ba điều hàng số 3 KHÔNG làm.** (a) Nó **không** mở quyền mạng: quyền duy nhất vẫn là cài gói đã khai báo từ
PyPI/npm (`OD-20260907-02` mục 4). (b) Nó **không** tự chuyển một gate nào sang `MET` — `precode/gates.yaml`
thuộc PC09 và cấp phép bắt đầu không phải là kết quả đã xác minh. (c) Nó **không** giải `REQ-OQ03`; Giai đoạn
3 vẫn bị chặn đúng như trước.

> **Cập nhật sau vòng bốn.** Hai cổng nêu ở mục này đã được `OD-20260907-04` xử lý — xem §8.13. Cổng probe nay
> mở về **hành chính**; `REQ-A6` **vẫn `KC`**, chỉ có quyền đi lấy dữ kiện. Điểm (a) ở trên vì vậy được nới
> đúng một chỗ và chỉ một chỗ: một quyền mạng **một lần, hẹp theo tên miền, chỉ đọc tài liệu**.

### 8.13 Quyết định của `OD-20260907-04` (vòng bốn, 2026-09-07)

Biên bản vòng bốn — `precode/owner-decisions-04.md`, authority `AUTH-OWNER-20260907-05` — có **hai** mục, và
cả hai là câu trả lời tường minh của Owner qua phỏng vấn `AskUserQuestion` trên đúng hai mục mà
`OD-20260907-03` để mở. Biên bản tự khai: *"không quyết ở vòng này: không có"*.

| # | Quyết định | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| 1 | Cổng chấp nhận probe `contracts/ops/collector-probe.md` §6 mục **2–4** (ngân sách §3 / điều kiện dừng §4; tiêu chí go/no-go §7; rủi ro tài khoản thật `REQ-A7`) | `ACCEPTED (OD-20260907-04)` — §6 mục **1–4 nay đều thỏa** | Hàng này; `contracts/ops/collector-probe.md` §6 **chưa** được PC05 cập nhật (`CR-PC00-26`) |
| 2 | Quyền mạng **một lần, hẹp** để đọc tài liệu chính thức arXiv/OpenAlex phục vụ `REQ-A6` | `ACCEPTED (OD-20260907-04)` — **quyền** được cấp | Hàng này; packet tìm dữ kiện chạy song song dưới `AUTH-OWNER-20260907-05` |

**`REQ-A6` VẪN `KC` — đây không phải một mục đã giải.** Owner cho phép **đi lấy** dữ kiện, **không** cung cấp
dữ kiện. `precode/requirements.csv` giữ `REQ-A6` ở `KC`; module research connector **không** được coi là
`CONTRACT_READY`; §8.5 ("phạm vi cố ý để trống, có gate") **không đổi** vì vòng này.

**Trạng thái thực tế lúc 2026-09-07T15:23Z (quan sát của PC00, không phải nội dung biên bản).** Packet tìm dữ
kiện chạy song song và đã land **một nửa**: `worker-WF` (`PKT-PC03-FIX-REQA6`) điền
`arxiv_requests_per_window = 1`, `arxiv_window_seconds = 3` và một dữ kiện mới
`arxiv_max_concurrent_connections = 1` từ `https://info.arxiv.org/help/api/tou.html`, mỗi cái kèm URL, ngày
lấy và trích dẫn nguyên văn; yêu cầu định danh của arXiv là `RESOLVED_NEGATIVE`. Nửa **OpenAlex chưa giải**,
và lý do là **ranh giới quyền**: `docs.openalex.org` `301` sang `help.openalex.org` — **ngoài** bốn host được
cấp — và `openalex.org` trả `403`; Worker **dừng** thay vì đi theo redirect, đúng như `protocol.md` §3 đòi.
Vì vậy `research_connector_rate_limit` **vẫn** `PLACEHOLDER_KC`, hai giá trị OpenAlex cộng
`openalex_identification_required` **vẫn** `null`, và sàn `min_interval_ms = 3000` giữ nguyên. Giải nốt phần
này cần **mở rộng quyền** thêm `help.openalex.org` — một amendment của grant, thuộc thẩm quyền Owner
(`CR-PC00-27`) — **không** cần và **không** được thay bằng một con số nhớ được. *(Đoạn này viết tại thời điểm biên bản, trước khi packet tìm dữ kiện chạy. Kết quả của
packet ấy ở **§8.13.1** ngay dưới; nó land **hai** trong bốn con số, nên câu "giữ bốn giá trị `null`" nay
đọc là **hai**. Mọi kết luận còn lại của đoạn — `REQ-A6` chưa giải hết, `PLACEHOLDER_KC`, connector không
`CONTRACT_READY` — vẫn đúng.)*

**Ranh giới của quyền mạng — viết bằng cả hai chiều.** Được: **chỉ trang tài liệu** dưới `arxiv.org`,
`info.arxiv.org`, `openalex.org`, `docs.openalex.org`. **Không** được: `export.arxiv.org`,
`api.openalex.org`, hay bất kỳ endpoint live nào — **không lưu lượng API thật**. Biên bản nêu **đích danh**
hai host bị cấm chứ không dừng ở mô tả, vì hai trong số đó thuộc cùng tổ chức với host được phép. Quyền mạng
nền không đổi: cài gói đã khai báo từ PyPI/npm (`OD-20260907-02` mục 4).

**Cổng probe mở về hành chính, KHÔNG mở về vật lý.** Probe vẫn chạy trên tài khoản X thật và máy thật của
Owner, sau khi **Owner tự** cài Playwright, đăng nhập tay vào Chrome profile riêng, điền `probe-config.json`
và ký bốn `owner_confirmations` kèm `evidence_ref` trỏ tới `OD-20260907-04`
(`evidence/handoffs/TC-x-feasibility-probe-handoff.md` §"Owner must do"). **Không Worker nào được chạy nó.**
Vì vậy `REQ-AC16` và các mục `KC` liên quan **không** đổi, và `SP1`/M0 vẫn chưa có bằng chứng. Thêm nữa: ba
mục vừa được chấp nhận đều là **ngưỡng `PROVISIONAL` do PC05 đề xuất** (§3 ngân sách; §7 bảy tiêu chí
`GO-1`..`GO-7`) — "chấp nhận" nghĩa là Owner đồng ý dùng chúng làm tiêu chí kết luận, **không** nghĩa là
chúng đã được hiệu chỉnh bằng dữ liệu.

**Ba điều vòng bốn KHÔNG làm.** (a) **Không** nâng trần claim của file nào —
`contracts/ops/collector-probe.md`, `contracts/retry-policy.yaml` và card connector giữ nhãn hiện có.
(b) **Không** giải `REQ-OQ03`; M3 vẫn bị chặn. (c) **Không** đóng finding nào.

#### 8.13.1 Kết quả packet tìm dữ kiện `REQ-A6` (`PKT-PC03-FIX-REQA6`, 2026-09-07)

Packet chạy dưới `AUTH-COORD-REQA6` (cha `AUTH-OWNER-20260907-05`), worker `worker-WF`, lease
`LEASE-PC03-REQA6`. Trạng thái kết quả: **`REQ-A6 = PARTIALLY_RESOLVED`** — **không** phải `RESOLVED`.
Bằng chứng là `SELF_VALIDATION`; công cụ đọc là `WebFetch` (GET, chỉ đọc), không có lưu lượng API nào tới
`export.arxiv.org` hay `api.openalex.org`.

| Dữ kiện | Trạng thái | Giá trị | Nguồn (đọc ngày **2026-09-07**) |
| --- | --- | --- | --- |
| arXiv — nhịp gọi tối đa | **RESOLVED** | `arxiv_requests_per_window = 1`, `arxiv_window_seconds = 3`, `arxiv_max_concurrent_connections = 1` | `https://info.arxiv.org/help/api/tou.html` §"Rate limits" — nguyên văn: *"When using the legacy APIs (including OAI-PMH, RSS, and the arXiv API), make no more than one request every three seconds, and limit requests to a single connection at a time."* |
| arXiv — yêu cầu định danh | **RESOLVED_NEGATIVE** | `arxiv_identification_required = false` | Cùng trang, cùng ngày; đối chiếu thêm `/help/api/user-manual.html`, `/help/api/basics.html`, `/help/api/index.html`. Không trang nào đặt nghĩa vụ User-Agent/email/đăng ký cho caller. Câu duy nhất chạm thông tin cá nhân là tuyên bố **thu thập**, không phải nghĩa vụ: *"In order to provide support and improvements for developers who use arXiv APIs, you understand that we will collect certain private information about you, such as your name and email address."* |
| OpenAlex — nhịp gọi / hạn mức | **BLOCKED_SCOPE** | `openalex_requests_per_window = null`, `openalex_window_seconds = null` | Không đọc được **trong quyền được cấp** — xem đoạn dưới |
| OpenAlex — yêu cầu định danh (`mailto`, polite pool) | **BLOCKED_SCOPE** | `openalex_identification_required = null` | Như trên |

**Vì sao nửa OpenAlex dừng, và vì sao đó KHÔNG phải "chưa tìm kỹ".** Quyền được cấp liệt kê đúng bốn host
(§8.13 ở trên). Ngày 2026-09-07, **mọi** đường dẫn thử dưới `docs.openalex.org` —
`/how-to-use-the-api/rate-limits-and-authentication`, `/how-to-use-the-api/api-overview`, và trang gốc `/` —
trả `301 Moved Permanently` sang `https://help.openalex.org/`, một host **không** nằm trong danh sách được
cấp; `https://openalex.org/` và `https://openalex.org/about` trả `403 Forbidden`. Worker **dừng tại
redirect** thay vì đi theo: đi theo một redirect ra ngoài allowlist là tự mở scope (`protocol.md` §3,
`BLOCKED_SCOPE`), và một biên bản nêu **đích danh** hai host bị cấm là biên bản coi trọng danh sách host.
Cách giải là một **amendment quyền** thêm `help.openalex.org` vào allowlist đọc-tài-liệu — không phải một
con số nhớ được, và không phải một lần suy ra từ "thông lệ".

**Bốn điều packet này KHÔNG làm.** (a) **Không** đóng `REQ-A6`: `precode/requirements.csv` giữ `REQ-A6` ở
`KC` (file đó ngoài lease của packet). (b) **Không** nới `SG-A6` của
`agent-tasks/TC-research-connector-metadata.md`: cổng ấy đòi **bốn** giá trị, hai vẫn `null`, nên connector
vẫn **từ chối khởi động**. (c) **Không** nâng trần claim của module research connector — vẫn **không**
`CONTRACT_READY`. (d) **Không** chạm một card đã pin nào; `contracts/retry-policy.yaml` đổi byte
(`0.6.0 → 0.7.0`) nên mọi card pin hash file đó chuyển **`STALE`** và phải được Coordinator pin lại
(`precode/change-control.md` §4 INV-06/INV-09, §10 `CR-PC03-08`).

#### 8.13.2 Phần 2 của `PKT-PC03-FIX-REQA6` — `REQ-A6` **RESOLVED** (2026-09-07)

Sau §8.13.1, Owner được trình đúng một câu hỏi — *"`docs.openalex.org` redirect sang `help.openalex.org`,
ngoài quyền được cấp"* — và trả lời: **thêm `help.openalex.org` vào allowlist**. Quyền mạng mở rộng thành
**năm** host, mọi hạn chế khác giữ nguyên (chỉ trang tài liệu, chỉ GET; `api.openalex.org` và
`export.arxiv.org` vẫn **cấm**). Packet chạy tiếp dưới `LEASE-PC03-REQA6-p2`, worker `worker-WF`.
Trạng thái kết quả: **`REQ-A6 = RESOLVED`** — cả bốn dữ kiện có nguồn.

| Dữ kiện | Trạng thái | Giá trị | Nguồn (đọc ngày **2026-09-07**) |
| --- | --- | --- | --- |
| arXiv — nhịp gọi | **RESOLVED** | `1` request / `3` giây; `1` kết nối đồng thời | `https://info.arxiv.org/help/api/tou.html` (§8.13.1) |
| arXiv — định danh | **RESOLVED_NEGATIVE** | không yêu cầu | như trên (§8.13.1) |
| OpenAlex — nhịp gọi | **RESOLVED** | `openalex_requests_per_window = 100`, `openalex_window_seconds = 1` | `https://help.openalex.org/api/authentication/` — nguyên văn: *"Two things return `429 Too Many Requests`: exceeding your daily budget, or making more than 100 requests per second."* |
| OpenAlex — định danh | **RESOLVED_NEGATIVE** | không yêu cầu; `api_key` **tùy chọn** | `https://help.openalex.org/api/` — nguyên văn: *"Send your key as an `api_key` query parameter (or leave it off to try the API for free — the website itself runs on these same public endpoints)."* và *"A free API key raises your daily budget 10×, and heavier use is pay-as-you-go."* |

**Một dữ kiện thứ năm, cố ý KHÔNG biến thành số.** OpenAlex có **hai** giới hạn chồng lên nhau: nhịp tức
thời (100 req/s) **và** một **ngân sách ngày**. Ngân sách ngày được nêu bằng **tiền**, không bằng số lời
gọi — *"every account gets \$1 of API usage per day for free"* (`/access/pricing/`) và *"a free key gives
you 10× the keyless budget"* (`/api/authentication/`) — và tài liệu **không** nêu con số của lượt gọi
không-khoá. Suy ra "1/10" là một **phép suy**, không phải một câu trích, nên hợp đồng ghi nó là
`RESOLVED_NON_NUMERIC` và **không** đặt một con số vào `values`. Nguồn sự thật lúc chạy là các header
`X-RateLimit-Limit` / `-Remaining` / `-Credits-Used` / `-Reset` (`/api/errors/`). Đây chính là chỗ mà "đọc
tài liệu" khác "điền cho đủ ô".

**Quy ước `polite pool` / `mailto` KHÔNG còn trong tài liệu hiện hành.** `REQ-D34` và `SG-IDENT` được viết
khi giả định OpenAlex đòi một `mailto`. Ngày 2026-09-07, các chuỗi `mailto`, `polite pool`, `polite`,
`User-Agent` **không** xuất hiện trên trang tổng quan API cũng như trang Authentication; cơ chế hiện hành
là `api_key` **tùy chọn**. Hệ quả: **luật** `SG-IDENT` giữ nguyên trong code (nếu một nguồn đòi định danh
mà ta chưa có, **không gọi**), nhưng **dữ kiện** mà luật ấy áp lên nay là "không nguồn nào đòi". Không
được xoá luật chỉ vì hôm nay nó không kích hoạt.

**Nhãn mới `DOCS_derived`.** `contracts/retry-policy.yaml` v0.8.0 dùng một token trạng thái **mới**
cho khối này, cố ý không tái dùng ba token cũ: nó không phải `ACCEPTED (OD-...)` (Owner không chấp nhận
hạn mức của bên thứ ba, Owner chỉ cấp quyền đi đọc), không phải `PROVISIONAL` (không phải tham số ta tự
chọn), không phải `XN_derived` (nguồn là tài liệu ngoài, không phải đặc tả). Nó mang một hạn dùng: nó
đúng với tài liệu **đọc ngày 2026-09-07** và hết hiệu lực khi nguồn đổi chính sách — mà OpenAlex vừa đổi
cấu trúc tài liệu (`docs.openalex.org` → `help.openalex.org`) ngay trong năm nay.

**Bốn điều phần 2 KHÔNG làm.** (a) **Không** nâng trần claim của `MOD-research-connector`:
`CONTRACT_READY` là kết luận của PC05/Coordinator trên toàn bộ cổng của module. (b) **Không** chạm
`precode/requirements.csv` (ngoài lease) — `REQ-A6` ở đó vẫn ghi `KC` cho tới khi chủ file cập nhật; đọc
kèm mục này. (c) **Không** chạm một card đã pin nào; `contracts/retry-policy.yaml` `0.7.0 → 0.8.0` nên
mọi card pin hash file đó **`STALE`** và chờ Coordinator pin lại. (d) **Không** đi theo một redirect nào
ra ngoài allowlist, và **không** gọi `api.openalex.org` hay `export.arxiv.org`.

### 8.14 Quyết định của `OD-20260908-05` và kết quả packet tìm dữ kiện `CR-PC07-04`

`OD-20260908-05` (2026-09-08, `AUTH-OWNER-20260908-06`) có hai mục. Mục 1 giao Coordinator **nghiên cứu và
đề xuất** nhà cung cấp/model cho `REQ-OQ03`; `REQ-OQ03` **vẫn** `OWNER_DECISION_REQUIRED` cho tới khi Owner
duyệt một đề xuất cụ thể, và nó **không** giải `REQ-A5` (đọc điều khoản thật của chính nhà đó trước khi bật
adapter là một cổng riêng). Mục 2 cấp một **quyền mạng một lần, hẹp, chỉ đọc** cho `CR-PC07-04`: chỉ trang
tài liệu dưới `core.telegram.org`, không gọi `api.telegram.org`, không dùng token, không gửi gì.

#### 8.14.1 `PKT-PC07-FIX-TELEGRAM` — `CR-PC07-04` = `PARTIALLY_RESOLVED` (2026-09-08)

Worker `worker-WT`, authority `AUTH-COORD-TELEGRAM-FACTS` (cha `AUTH-OWNER-20260908-06`), lease
`LEASE-PC07-TELEGRAM`. Công cụ đọc: `WebFetch` (GET, chỉ đọc); **không** một lời gọi nào tới
`api.telegram.org`. Ngày lấy **2026-09-08** theo giờ Owner (`Asia/Ho_Chi_Minh`) = UTC
`2026-09-07T17:52Z`…`2026-09-07T18:06Z` — hai cách viết một lúc; ghi cả hai vì đồng hồ máy chạy UTC còn
packet nói theo ngày của Owner. Kết quả: **hai** trong năm dữ kiện có nguồn, **ba** dừng ở `BLOCKED_DEPENDENCY`.

| Dữ kiện | Trạng thái | Giá trị | Nguồn (đọc 2026-09-08) |
| --- | --- | --- | --- |
| Độ dài tối đa một tin | **`RESOLVED`** (nguồn thứ cấp) | `4096` ký tự cho `sendMessage.text` | `https://core.telegram.org/bots/tutorial` §"Sending Messages" — nguyên văn: *"A `String` object containing the message text, 1-4096 characters."* |
| Rate limit gửi | **`RESOLVED`** | 1 tin/giây trong một chat; 20 tin/phút trong một group; ~30 tin/giây khi broadcast | `https://core.telegram.org/bots/faq` §"My bot is hitting limits, how do I avoid this?" — nguyên văn: *"In a single chat, avoid sending more than one message per second. We may allow short bursts that go over this limit, but eventually you'll begin receiving 429 errors."* · *"In a group, bots are not be able to send more than 20 messages per minute."* · *"For bulk notifications, bots are not able to broadcast more than about 30 messages per second, unless they enable paid broadcasts to increase the limit."* |
| Độ dài `callback_data` | **`BLOCKED_DEPENDENCY`** | vẫn PROVISIONAL 64 byte, **chưa kiểm** | `https://core.telegram.org/bots/api` — trong host được cấp, ngoài tầm công cụ (dưới) |
| Parse mode + bảng escape | **`BLOCKED_DEPENDENCY`** | — | như trên |
| Số nút mỗi hàng / mỗi bàn phím | **`BLOCKED_DEPENDENCY`** | — | như trên |

**Vì sao ba dòng dừng, và vì sao đó KHÔNG phải "chưa tìm kỹ" — cũng KHÔNG phải `BLOCKED_SCOPE`.** Khác
`REQ-A6` §8.13.1 (ở đó trang tài liệu redirect sang một host **ngoài** allowlist, nên cái chặn là ranh giới
**quyền**), ở đây trang mang cả ba dữ kiện — `https://core.telegram.org/bots/api` — nằm **đúng trong** host
được cấp. Cái chặn là **trần công cụ**: `WebFetch` chuyển trang sang markdown rồi cắt theo độ dài, và điểm
cắt rơi giữa `MessageAutoDeleteTimerChanged`, tức **trước** cả mục `Available methods`. `sendMessage`,
`InlineKeyboardButton` và bảng escape MarkdownV2 nằm sau điểm cắt và không lần đọc nào chạm tới được —
đã thử cả `#sendmessage` và `#inlinekeyboardbutton` (fragment không đổi phần được cắt). Mười hai trang
cùng host đã thử và **không** trang nào chứa ba dữ kiện ấy: `/bots/features`, `/bots/faq`, `/bots/tutorial`,
`/bots/webhooks`, `/bots/inline`, `/bots/games`, `/bots/2-0-intro`, `/bots/api-changelog`,
`/api/bots/buttons`, `/api/entities`, `/constructor/keyboardButtonCallback`, `/constructor/replyInlineMarkup`.
Cách giải là một **khả năng đọc lấy được cả trang** (fetch theo đoạn, hoặc tải rồi grep cục bộ) dưới **cùng**
ranh giới host — một amendment về **công cụ**, không phải về host, và tuyệt đối không phải một con số nhớ được.

**Con số 4096 đứng trên một nguồn THỨ CẤP, và điều đó phải đọc được.** Nó lấy từ `/bots/tutorial`, không
phải từ hàng `text` của `/bots/api#sendmessage`. Hệ quả: **ngữ nghĩa đếm** ("after entities parsing" hay
không) và **đơn vị đếm** (ký tự Unicode hay đơn vị mã UTF-16) **chưa** có câu trích. `contracts/telegram/delivery.md`
§3.4 vì vậy khóa một luật **an toàn một chiều** thay vì một giả định: đếm trên **chuỗi thô đã escape**, vì
escape chỉ **thêm** ký tự nên "thô ≤ 4096" kéo theo "sau parse ≤ 4096" dưới cả hai cách đọc. Đó là suy luận
về **quan hệ** giữa hai phép đếm, không phải suy luận ra con số — ranh giới ấy là chỗ "đọc tài liệu" khác
"điền cho đủ ô", đúng như §8.13.2 đã ghi cho ngân sách ngày của OpenAlex.

**Rate limit là trần LẬP KẾ HOẠCH, không phải ngân sách retry.** Chính nguồn viết có biên — *"avoid"*,
*"about"*, *"may allow short bursts"* — và mệnh đề *"unless they enable paid broadcasts"* nói 30/giây là trần
**mặc định**. `Retry-After` của Telegram trên một `429` thật **thắng** mọi số ở trên; `contracts/retry-policy.yaml`
**không** bị đụng bởi packet này (ngoài lease) và không nhận số mới nào. Ràng buộc thực tế cho hệ này là dòng
thứ nhất — **1 tin/giây trong một chat** — vì §3.5 gửi một digest nhiều part bằng nhiều lời gọi liên tiếp.

**Nhãn `DOCS_derived` dùng lại đúng nghĩa của §8.13.2:** giá trị đứng trên trang tài liệu, không trên chữ ký
của ai; nó mang hạn dùng và hết hiệu lực khi Telegram đổi chính sách. Owner cấp **quyền đi lấy**, không cấp
nội dung — nên đây **không** phải một quyết định sản phẩm, và ai đọc lại thấy khác thì mở CR mới.

**Sáu điều packet này KHÔNG làm.** (a) **Không** đóng `CR-PC07-04`: ba trong năm dữ kiện còn thiếu, nên nó
là `PARTIALLY_RESOLVED`, không `CLOSED`. (b) **Không** nâng trần claim của `contracts/telegram/delivery.md`
(vẫn `DRAFT_FOR_REVIEW`) và **không** gỡ `BLOCKED (cứng)` của `MOD-telegram-adapter`. (c) **Không** chạm
`contracts/telegram/commands.yaml`, `contracts/retry-policy.yaml`, `acceptance/scenarios.yaml`,
`precode/review.md`, `precode/gates.yaml`, `docs/master-plan.md` hay một card `agent-tasks/*` nào — tất cả
ngoài lease, và tất cả còn câu chữ mô tả **năm** dòng `KC` cần Coordinator sửa bằng một packet khác.
(d) **Không** sửa `verification:` ở front matter `delivery.md` (ngoài vùng §3.4 được cấp) — dòng ấy vẫn viết
"Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có mạng)", nay **sai một phần**. (e) **Không**
nới `SG-01` của `TC-telegram-unknown-delivery`/`TC-telegram-linking-auth`: nhánh multipart cần chỗ cắt, và
chỗ cắt cần bố cục nút + parse mode. (f) **Không** gọi `api.telegram.org`, **không** dùng token, **không**
gửi một tin nào.

**Điều kiện Phase 5 của `OD-20260908-05` mục 2 CHƯA đạt như đã viết.** Câu ấy là *"Phase 5 … is authorised to
start once the five facts land"*; **hai** dữ kiện đáp, **ba** không. Nới câu ấy là quyết định của Owner —
Worker chỉ ghi nhận rằng điều kiện, đọc theo nguyên văn, chưa được thỏa.

#### 8.14.2 Vòng hai (`PKT-PC07-FIX-TELEGRAM-2`, `LEASE-PC07-TELEGRAM-p2`, cùng ngày)

Coordinator mở lại lease với ba hướng thử cụ thể cho ba dữ kiện còn `KC`, cộng việc sửa front matter của
`contracts/telegram/delivery.md`. Kết quả: **ba dữ kiện GIỮ NGUYÊN `BLOCKED_DEPENDENCY`**; front matter đã sửa.

**Hướng 1 và 2 — anchor khác.** Giả thuyết: `#formatting-options` / `#inlinekeyboardbutton` /
`#markdownv2-style` / `#html-style` / `#inlinekeyboardmarkup` / `#replykeyboardmarkup` có thể rơi vào một
cửa sổ đọc khác `#sendmessage`. **Bác bỏ bằng quan sát**: bảy anchor, tám lần gọi, **cả tám** đều bị cắt.
Điểm dừng có xê dịch giữa các lần — `MessageAutoDeleteTimerChanged`, `date-time entity formatting`,
`WebAppData`, `InputChecklist` — nên cửa sổ đọc **không** hoàn toàn tất định; nhưng lần xa nhất
(`InputChecklist`) vẫn nằm **trong** `Available types` và vẫn **trước** `InlineKeyboardMarkup`,
`InlineKeyboardButton`, `Formatting options` và toàn bộ `Available methods`. Anchor không dời được cửa sổ;
giả thuyết ấy đã được thử thật và đã sai.

**Hướng 3 — tìm kiếm web: KHÔNG chạy, `BLOCKED_SCOPE`.** Packet vòng hai đề nghị một `WebSearch` dạng
`site:core.telegram.org …` cho dòng "số nút mỗi hàng". Worker **từ chối** và dừng ở đó. Lý do là quyền, không
phải kỹ thuật: `OD-20260908-05` mục 2 cho phép *"fetch documentation pages only under `core.telegram.org`"*
kèm *"no message sent"*; một truy vấn tìm kiếm là một lời gọi tới **một host khác**, mang theo nội dung truy
vấn. `protocol.md` §2 nói grant con là **subset** của grant cha và Coordinator không mở rộng được grant của
Owner; `worker.md` cấm dùng live network ngoài capability/authority explicit. Một Worker tự nới host vì
Coordinator gợi ý là đúng cái `BLOCKED_SCOPE` sinh ra để chặn — và nó sẽ làm hỏng chính điều khiến hai dữ
kiện kia đáng tin. Muốn đi hướng ấy: một amendment của **Owner**, không phải một câu trong packet.

**Vì sao dòng "số nút" KHÔNG được đóng bằng câu "Telegram không công bố".** Packet vòng hai gợi ý, nếu tìm kỹ
mà không thấy, thì ghi *"no official maximum found on core.telegram.org as of 2026-09-08"* thay vì để `KC`
mãi. Ghi nhận tinh thần ấy, nhưng **chưa** đủ điều kiện: 12 trang đã đọc không nêu con số, song trang có
nhiều khả năng nêu nó nhất — `InlineKeyboardMarkup` trên `/bots/api` — **chính là** trang không đọc được.
Một phủ định chỉ có giá trị khi **tập đã đọc bao được chỗ dữ kiện có thể nằm**; ở đây tập ấy có một lỗ thủng
đúng ngay giữa. Câu ghi được hôm nay là *"không tìm thấy trên 12 trang đã đọc được"* — một **phủ định có
phạm vi**, cùng loại với `arxiv_identification_required = false` ở §8.13.1 — và nó **không** nâng dòng ấy ra
khỏi `KC`. Viết câu mạnh hơn sẽ là suy diễn từ một lần đọc thiếu, đúng thứ SRC-SPEC §13.2 cấm.

**Front matter `delivery.md` đã sửa** (vòng một cố ý không đụng vì ngoài vùng §3.4; vòng hai được cấp cả file):
`version` `0.1.0 → 0.2.0` theo `precode/change-control.md` §2 hàng minor, và `verification:` bỏ câu
*"Giới hạn định dạng Telegram là `KC` — chưa đọc tài liệu (không có mạng)"* — nay sai một phần — thay bằng
phát biểu **đếm được**: hai dữ kiện `DOCS_derived` (kèm hạn dùng), ba dữ kiện `KC`/`BLOCKED_DEPENDENCY` nêu
đích danh, và câu kết luận rằng nhánh multipart của §3.5 vẫn chưa hiện thực được. `claim_ceiling` **giữ**
`DRAFT_FOR_REVIEW`: đọc được hai giới hạn không làm một hợp đồng sẵn sàng, và bump version **không** phải
một lần nâng trần claim.

#### 8.14.3 Vòng ba — `OD-20260908-07` mục 1 nới quyền sang tìm kiếm web; ba dữ kiện vẫn `BLOCKED_DEPENDENCY`

`OD-20260908-07` (`AUTH-OWNER-20260908-08`) mục 1 mở đúng cái ranh giới mà vòng hai dừng lại: Worker được
dùng **WebSearch** để tìm **đường đọc** chính trang `core.telegram.org/bots/api` — bản lưu trữ, bản cache,
hoặc một cách lấy lát nhỏ hơn. Mọi hạn chế khác giữ nguyên, và Owner nói rõ: tìm kiếm để **định vị nội dung
của trang ấy**, **không** phải để lấy một con số từ một site khác. Packet vòng ba (`LEASE-PC07-TELEGRAM-p3`)
thi hành đúng như vậy. **Kết quả: cả ba dữ kiện vẫn `BLOCKED_DEPENDENCY`.**

| Đường đã thử | Kết quả |
| --- | --- |
| WebSearch (tự do) — tìm bản lưu trữ của chính trang ấy | Xác nhận Wayback có snapshot; trỏ tới `web.archive.org/web/*/core.telegram.org/bots/api` |
| WebSearch giới hạn `allowed_domains = core.telegram.org` — `callback_data "1-64 bytes"` | Trả về danh sách URL của chính host, **không** có câu cần trích trong snippet |
| `web.archive.org/web/20200215000000id_/…/bots/api` (bản 2020, sau Bot API 4.5 nên CÓ MarkdownV2, và nhỏ hơn bản hiện tại) | **Bị chặn ở tầng công cụ**: *"Claude Code is unable to fetch from web.archive.org"* — không phải 404, không phải quyền |
| `web.archive.org/web/20160801000000id_/…/bots/api` (bản 2016, nhỏ hơn nữa) | Cùng lỗi chặn |
| `archive.ph/newest/…` | *"unable to fetch from archive.ph"* |
| `corefork.telegram.org/bots/api` (host mirror của **chính Telegram**) | Tải được nhưng **cùng cỡ trang** ⇒ cắt y hệt, dừng trong `Message` |

**Giả thuyết của vòng ba, và vì sao nó đúng nhưng không dùng được.** Suy luận là: trang Bot API **lớn dần
theo năm**, nên một snapshot 2020 (đã có MarkdownV2 từ Bot API 4.5, tháng 12/2019) sẽ nhỏ hơn bản 2026 đủ để
lọt vào cửa sổ đọc. Suy luận ấy vẫn hợp lý; nó chết vì một lý do **không liên quan gì tới Telegram**: nền
tảng chặn cứng mọi host lưu trữ. Đây là **loại chặn thứ ba** trong hồ sơ này, và đáng gọi đúng tên — không
phải `BLOCKED_SCOPE` (quyền đã đủ, Owner vừa nới), không phải thiếu nguồn (trang tồn tại, snapshot tồn tại),
mà vẫn là `BLOCKED_DEPENDENCY`: thiếu **tool capability**, lần này ở một chỗ khác của cùng bức tường.

**Điều vòng ba KHÔNG làm, và đây là chỗ dễ trượt nhất.** Tìm kiếm **có** trả về con số: các trang thứ ba
(n8n docs, grammY, một blog) nêu *"4096 characters after entities parsing"*, *"UTF-16 length limit of
4096"*, và mô tả luật escape của MarkdownV2. **Không** một chữ nào trong số đó được đưa vào hợp đồng.
`OD-20260908-07` mục 1 viết thẳng: *"not substituting a third-party's restatement of the numbers as if it
were the source"*. Một con số đúng lấy từ người kể lại vẫn là một trích dẫn sai — và trớ trêu là những trang
ấy **đồng ý** với giả định 64 byte đang nằm trong `1:<ri>:<ii>:<lg>:<rv>`, tức là cám dỗ lớn nhất chính là
lúc câu trả lời "trông đã đúng rồi". Ghi lại ở đây rằng chúng tồn tại và cố ý bị bỏ qua, để lần sau không ai
tưởng là chưa ai tìm thấy gì.

**Việc cần xin ở vòng sau, cụ thể và duy nhất.** Cả ba vòng thất bại vì **kích thước**, không vì host: trang
nặng ~1.5 MB và dữ kiện nằm ở nửa sau. Thứ giải được là một cách đọc **theo lát** trên **đúng URL chính
thức** — HTTP `Range`, hoặc một công cụ fetch có offset/phân trang. Đó là một amendment về **công cụ**
(không mở thêm host, không đổi điều cấm nào), và nó **không** cần Owner cấp thêm quyền mạng nào ngoài cái
đã có. Nếu cả cách ấy cũng không có, ba dòng ở lại `KC` — và `MOD-telegram-adapter` ở lại **BLOCKED (cứng)**,
đúng như ba vòng qua đã ghi.

### 8.15 Quyết định của `OD-20260908-06` (vòng sáu, 2026-09-08) — `REQ-OQ03` **đã được trả lời**

Mục này trả lời đúng điều **§8.14 để mở**: câu ở §8.14 (*"`REQ-OQ03` **vẫn** `OWNER_DECISION_REQUIRED` cho
tới khi Owner duyệt một đề xuất cụ thể"*) đúng ở thời điểm nó được viết và **nay đã được thoả** — Owner đã
duyệt. Biên bản: `precode/owner-decisions-06.md`, ghi bởi `worker-WAI` (`PKT-PC06-FIX-OQ03`) dưới
`AUTH-COORD-OQ03` (cha `AUTH-OWNER-20260908-06`), evidence `session_017CTbS7F4oTr4ZtFYkhdabD`. Câu trả lời
**nguyên văn** của Owner: **"sonnet 5 + opus 5 for summary"**.

| # | Quyết định | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| 1 | `summary` → Claude **Opus 5** (`claude-opus-5`); `label` và `direction_phrasing` → Claude **Sonnet 5** (`claude-sonnet-5`); cả hai họ `api_key`, **không** phải `cli_acp` | `ACCEPTED (OD-20260908-06)` | `contracts/ai/providers.yaml` §2.1 (v0.1.0 → 0.2.0); `precode/owner-decisions-06.md` §2; `precode/requirements.csv` hàng `REQ-OQ03` (`ĐX` → `XN`) |

**Cổng vào Giai đoạn 3 đòi một CÂU TRẢ LỜI, không đòi một adapter đã bật.** `docs/master-plan.md` §3 viết
*"Cổng vào: `REQ-OQ03` phải được Owner trả lời."* Câu trả lời đã có, nên cổng ấy được thoả. Việc **gọi được
model** thì chưa: cả hai mục adapter mang `enabled: false`. Hai chuyện đó tách nhau, và trộn chúng lại là
cách dễ nhất để đọc mục này rộng hơn nó là.

**`REQ-A5` cho Anthropic: `permitted_for_this_use`, có điều kiện — và có nguồn.** Một **Worker** (không phải
Owner — xem dưới) đã đọc `www.anthropic.com/legal/commercial-terms` (eff. **2025-06-17**), `/legal/aup`
(Usage Policy, eff. **2025-09-15**) và `/legal/service-specific-terms` (eff. **2026-06-08**) ngày
**2026-09-08** (giờ Owner) = `2026-09-07T18:0xZ` UTC; công cụ `WebFetch` GET, chỉ đọc; **không** một lời gọi
nào tới `api.anthropic.com`, **không** dùng API key, **không** một lần inference nào. Bảy trích dẫn nguyên
văn ở `precode/owner-decisions-06.md` §3. Kết quả: ToS áp cho *"Customer's use of Anthropic API keys"*, nhập
Usage Policy vào hợp đồng, cho *"Customer… owns its Outputs"* và cho dùng Services để *"power products and
services"*; **toàn bộ 82 gạch** của *Universal Usage Standards* đã đọc hết và **không** gạch nào cấm chạy tự
động không người trực, chạy khối lượng lớn, gắn nhãn/tóm tắt văn bản của bên thứ ba, hay lưu và dùng lại
output. Hai điều kiện còn mở **thuộc về phía mình**, không phải hạn chế do Anthropic đặt lên cách dùng:
(a) quyền đối với Input — *"Customer further represents and warrants that it has all rights and permissions
required to submit Inputs to the Services."*, và ta gửi abstract/post của bên thứ ba; (b) cấm dùng
input/output để **train** model — hiện không kích hoạt vì embedding là model local (REQ-D48/D50), nhưng nó
chặn trước mọi ý định về sau.

**Vì sao cả hai adapter vẫn `enabled: false` — và vì sao đó là kết luận của VĂN BẢN, không phải của sự thận
trọng.** `providers.yaml` §4 `status_values` chỉ cho `not_applicable` với *"các tính chất mà **kiến trúc đã
loại bỏ**"*. `ISO-03` (network egress) và `ISO-05` (credential đúng provider, đúng task đang giữ lease) là
những tính chất mà đường `api_key` **tạo ra**: nó là đường **duy nhất** gọi mạng tới endpoint nhà cung cấp
(§1 `api_key`) và là đường **duy nhất** nhận credential (`cli_acp` có `secret_ref = NULL`, REQ-D51; ADR-0010
điểm 1 đặt secret theo từng task). Chúng nằm **ngoài** tập mà `not_applicable` phủ, với bất kỳ cách đọc nào
của câu đó ⇒ `unverified` ⇒ `enabled = false` **theo chính §4**. `ISO-01`/`02`/`04` cũng `unverified` theo §4
`current_status_vi` (*"Không có ngoại lệ, vì chưa có probe nào chạy (E3 = `NOT_RUN`)"*), cộng một lý do độc
lập: `not_applicable` giả định một **kiến trúc đã tồn tại** để loại bỏ được một tính chất, mà `MOD-ai-adapter`
chưa có một dòng mã nào — nên cái "đã loại bỏ" mới là **dự định**, và §4 `principle_vi` nói thẳng *"Một lời
hứa… KHÔNG phải bằng chứng cô lập"*. Cách kiểm hai mục quyết định đều đòi một lần **chạy**: ghi tập đích của
một lần chạy (`ISO-03`), và gọi `secret.issue_task_credential` cho một worker **không** giữ lease rồi thấy nó
bị từ chối (`ISO-05`) — E3 = `NOT_RUN` và operation đó chưa có mã.

**Chỗ văn bản thật sự mơ hồ, ghi ra thay vì giấu.** Với `ISO-01`/`ISO-02`, ADR-0010 điểm 2 khoanh yêu cầu
"tắt tool, tắt file, tắt mạng" cho **đường CLI/ACP**, và §1 chỉ đặt `isolation_required: true` dưới `cli_acp`
— nên có thể lập luận rằng một adapter `api_key` không có bề mặt tool thì hai mục ấy là `not_applicable`.
Bản ghi này **không** đi theo lập luận đó (hai lý do ở đoạn trên), và quan trọng hơn: nó **không đổi được kết
quả**, vì `ISO-03`/`ISO-05` vẫn `unverified`. Muốn chốt khác cho `ISO-01`/`ISO-02` thì đó là một **quyết định
hợp đồng** (`CR-PC06-OQ03-01` chạm cùng vùng), không phải một cách đọc Worker được tự chọn.

**Một điểm CHI PHÍ Owner nên thấy, vì nó không tự lộ ra.** `label` là task khối lượng **lớn nhất** (mọi
post/work — `contracts/ai/tasks.yaml` `label.volume_vi`) và `REQ-D40` khuyến nghị **model rẻ** cho nó; lựa
chọn này đặt nó lên model **mạnh**. `providers.yaml` §7 `rules_vi` cho phép tường minh (*"REQ-D40 là khuyến
nghị mặc định… không phải ràng buộc cứng: Owner được phép đặt khác"*), nên đây **không** phải vi phạm hợp
đồng — nó là một chi phí **đã được chọn**. Chỗ để hạ chi phí về sau là `label`, không phải `summary`.
`direction_phrasing` thì khớp thẳng: `tasks.yaml` khai `model_class: strong` cho nó (1 lần mỗi kỳ) và
Sonnet 5 là model lớp mạnh — Owner khoanh Opus 5 vào **đúng chữ `summary`**, nên phần còn lại rơi về Sonnet 5
mà không mâu thuẫn với `tasks.yaml`.

**Năm điều vòng sáu KHÔNG làm.** (a) **Không** bật adapter nào. (b) **Không** tạo hàng `ENT-provider-config`,
không đặt `secret_ref`, không chạm secret store. (c) **Không** mở allowlist fallback — `providers.yaml` §6
chỉ nhận adapter `enabled = true`, và hiện không có adapter nào như vậy. (d) **Không** đổi `REQ-AC16`: hai
adapter này thuộc họ `api_key`, đường không-API-key vẫn phụ thuộc adapter `cli_acp`, và luật báo cáo
`BLOCKED` (**không** phải `FAIL`) của §4 giữ nguyên. (e) **Không** nâng trần claim của file nào và **không**
đóng finding nào — `contracts/ai/providers.yaml` v0.2.0 vẫn `DRAFT_FOR_REVIEW`.

**Bảy CR phát sinh** — bản ghi một dòng ở `precode/owner-decisions-06.md` §7; ba cái chạm hợp đồng
(`CR-PC06-OQ03-01`, `-02`, `-03`) có khối YAML đầy đủ ở `precode/change-control.md` §10. Đáng chú ý nhất:
`-02` (§5 ghi `reviewer` *"đây là Owner"* và *"PC06 KHÔNG đọc thay"*, trong khi `OD-20260908-05` mục 1 giao
việc đọc `REQ-A5` cho một **Worker** — hai câu không thể cùng đúng, và phải chốt **trước** lần bật đầu tiên
vì `entities.yaml` `ck_provider_config_terms_before_enable` biến nó thành một CHECK chạy được) và `-05`
(quyền mạng thực tế chỉ đọc được `www.anthropic.com/legal/*`: `docs.anthropic.com` **301 →**
`platform.claude.com` và `www.anthropic.com/pricing` **301 →** `claude.com`; Worker **dừng tại redirect**,
đúng tiền lệ `docs.openalex.org` ở §8.13.1 — nên `anthropic-version`, chuỗi model id và bảng giá **chưa** có
nguồn chính thức đọc được).

**Ghi chú lease — vì sao mục này land sau `§8.14` một nhịp.** `PKT-PC06-FIX-OQ03` và `PKT-PC07-FIX-TELEGRAM`
được dispatch **cùng lúc** với write set **chồng nhau** trên đúng ba file (`decision-register.md`,
`change-control.md`, `requirements.csv`). `protocol.md` §2 không bật range-sharing, nên hai lease "chỉ một
hàng" vẫn là hai lease **toàn file**. `worker-WAI` quan sát ba file đổi bytes hai lần trong 13 phút khi
`worker-WT` chưa handoff, nên **dừng trước khi ghi** (`BLOCKED_LEASE`) thay vì ghi đè — rồi land phần này
dưới `LEASE-PC06-OQ03-p2` sau khi `LEASE-PC07-TELEGRAM` được nhả và baseline được đọc lại. Nội dung của
`worker-WT` ở §8.14 **không** bị chạm một byte.

#### 8.15.1 `OD-20260908-08` — Owner **ký xác nhận** `REQ-A5` cho Anthropic; `CR-PC06-OQ03-02` đóng (2026-09-08)

Biên bản vòng tám — `…/packets/OWNER-DECISIONS-20260908-08.md`, authority **`AUTH-OWNER-20260908-09`**,
evidence `session_017CTbS7F4oTr4ZtFYkhdabD` — có **một** mục, và mục đó đóng đúng khoảng lệch mà §8.15 nêu:
Owner **tự đọc** bản tóm tắt `REQ-A5` (bảng trích dẫn `A5-1`…`A5-8` cộng hai điều kiện còn mở ở
`precode/owner-decisions-06.md` §3) rồi **ký**.

| # | Quyết định | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| 1 | `REQ-A5` cho Anthropic (Claude Sonnet 5 / Claude Opus 5, họ `api_key`) — **ký xác nhận**, **chấp nhận tường minh** bảo đảm `TC-A5-01` | `ACCEPTED (OD-20260908-08)` | Hàng này; `contracts/ai/providers.yaml` §2.1 → `terms_check.reviewer` của **cả hai** mục |

**Cái được ký, viết hẹp đúng bằng cái Owner đọc.** Chữ ký áp cho **đúng Anthropic** và **đúng ba trang có
ngày hiệu lực** đã dẫn ở `source_urls`: Commercial ToS (eff. 2025-06-17), Usage Policy (eff. 2025-09-15),
Service Specific Terms (eff. 2026-06-08). Chính biên bản nhắc lại luật hết hạn của `ADR-0010`: *"The
conclusion expires if any of the three cited pages changes version"*. Nó **không** là một chữ ký cho "nhà
cung cấp Anthropic nói chung", cũng **không** cho một model hay một version khác.

**`TC-A5-01`: Owner nhận phần của mình — và phần còn lại vẫn để ngỏ.** Điều Owner chấp nhận là **bảo đảm với
Anthropic**: *"Customer further represents and warrants that it has all rights and permissions required to
submit Inputs to the Services."* — tức Owner (không phải Anthropic) là bên đứng ra bảo đảm rằng hệ này có
quyền đưa văn bản nghiên cứu của bên thứ ba vào làm Input. Điều **KHÔNG** được quyết ở vòng này, nguyên văn
biên bản: *"whether arXiv/OpenAlex/X's own policies permit this system reprocessing their content this way
(`TC-A5-01`'s underlying question, distinct from Anthropic's terms) — flagged by the Worker as a separate,
unanswered question, not resolved by this sign-off."* Hai câu hỏi ấy **khác nhau** và trộn chúng là cách dễ
nhất để đọc chữ ký này rộng hơn nó là: nhận bảo đảm với Anthropic **không** trả lời được câu hỏi chính sách
của arXiv/OpenAlex/X. Câu đó vẫn **chưa có ai trả lời**, và không packet nào tới giờ được giao đi hỏi nó.

**`CR-PC06-OQ03-02` đóng — và đóng đúng cách.** CR ấy hỏi: `reviewer` phải là Owner (§5) hay được là một
Worker (`OD-20260908-05` mục 1)? Biên bản chọn phương án **(a)** của CR: lần đọc do Worker thực hiện được
Owner **ký xác nhận**, và chữ ký ấy là thứ làm §5 `reviewer = Owner` thoả. `protocol.md` §8: disposition do
authority được chỉ định ký — ở đây là chính Owner — nên đây là một lần đóng hợp lệ, không phải Worker tự khai.
`entities.yaml` `ck_provider_config_terms_before_enable` (`enabled = 0 OR terms_check_at IS NOT NULL`) nay có
một mốc thật để trỏ vào, khi nào có hàng `provider_config` đầu tiên.

**Chữ ký này KHÔNG bật adapter nào — và đó là điều dễ đọc nhầm nhất ở đây.** Biên bản nói thẳng: *"This does
**not** set `enabled = true` on either adapter — that remains gated on `B13` isolation verification
(`ISO-03`/`ISO-05` unverified, `E3 NOT_RUN`), unrelated to this sign-off."* Hai cổng vẫn **tách nhau** đúng
như §8.15 mô tả: cổng điều khoản (`REQ-A5`) nay **đã qua**; cổng cô lập (`B13`/`ADR-0010`) **vẫn đóng**, và
chỉ một lần chạy E3 mở được nó. `enabled: false` **không bị chạm** ở vòng này.

**Ba câu chữ nay đã cũ, ghi ra thay vì im lặng sửa.** Lease `LEASE-PC06-OQ03-p3` cấp **đúng** object
`terms_check` của hai mục adapter, nên hai câu sau trong `contracts/ai/providers.yaml` §2.1 — viết **trước**
chữ ký — **không** được chạm và nay đọc sai: (1) `terms_conditions_vi.reviewer_caveat_vi` (*"Owner **chưa** ký
xác nhận nội dung đã đọc"*); (2) mệnh đề cuối của `disabled_reason` mục `anthropic@claude-sonnet-5` (*"hai
điều kiện còn mở là TC-A5-01… **và chữ ký xác nhận của Owner**"* — nay chỉ còn **một**, và bản thân
`TC-A5-01` đã đổi hình: phần bảo đảm với Anthropic được Owner nhận, phần chính sách nguồn vẫn mở). Trường
`terms_check.reviewer` của cả hai mục mang câu đính chính và trỏ tới `CR-PC06-OQ03-08`. Sửa hai câu ấy cần
một packet khác — viết trước rồi hợp thức hoá sau chính là thứ `BLOCKED_SCOPE` sinh ra để chặn.

### 8.16 Amendment kỹ thuật thứ hai của Coordinator — `AMD-ENT-maintenance-01` (2026-09-08)

Cùng dạng với §8.11: một amendment thực hiện **sau** khi `contracts/data/entities.yaml` đã
`CONTRACT_READY`, dưới thẩm quyền kỹ thuật của Coordinator, và **chưa** có câu trả lời của Owner.
PC00 **ghi nhận, không thẩm định lại** nội dung kỹ thuật; chủ sở hữu vẫn là PC02.

| ID | Gói | Quyết định | Trạng thái | Đưa lên Owner ở mục |
| --- | --- | --- | --- | --- |
| `AMD-ENT-maintenance-01` | PC02 | `contracts/data/entities.yaml` (0.2.0 → 0.3.0) thêm entity `maintenance_window` (`ENT-maintenance-window`, `owner_module: MOD-data-store`; 10 trường: `id`, `owner_id`, `opened_at`, `opened_by`, `reason`, `storage_health_at_open`, `closed_at`, `closed_by`, `snapshot_verified_at`, `restore_record_id`; partial unique "nhiều nhất một cửa sổ đang mở"; ba CHECK) — chỗ ghi mà `contracts/state/storage.yaml` T-ST-03/T-ST-04/T-ST-09 đã đòi từ đầu nhưng hợp đồng entity không khai. Tập `retained_by_owner_decision` của `TXN-purge-all`: 21 → 22, tổng 60 → 61. Thi hành qua `CR-TC-storage-06` (cùng gốc `CR-TC-storage-04`), ghi ở `precode/change-control.md` §10 | **PROVISIONAL** — amendment kỹ thuật dưới `AUTH-COORD-PC02-FIX16`; Owner phê chuẩn ở vòng kế tiếp và **có thể phản đối** | mục **Vận hành và bảo mật** (đã có — bổ sung hệ quả: cửa sổ bảo trì nay là một hàng bền, và nó nằm trong tập GIỮ LẠI khi `data.purge_all` chạy) |

**Vì sao Coordinator ký được.** Amendment hòa giải hai hợp đồng mà Owner **đã** phê chuẩn — state
contract nói một hàng được ghi, entity contract không khai bảng nào để ghi — nên nó không thêm một
quyết định sản phẩm mới. Đúng loại mâu thuẫn nội bộ mà `precode/change-control.md` §7 giao cho
ruling của Coordinator đóng.

**Bốn điều nó KHÔNG làm.** Nó không mang nhãn `ACCEPTED`; nó **không** đóng `CR-TC-storage-06`;
nó **không** giải `CR-TC-storage-04` (thiếu `storage_probe` cho đường `write_blocked → healthy` —
một khoảng trống khác, vẫn mở); và nó **không** khẳng định bảng đã tồn tại trong schema đang chạy.
Chưa migration nào tạo nó — đó là việc của WR trên lease kế tiếp — nên
`tests/contract/test_schema_matches_entities.py` sẽ **ĐỎ** cho tới lúc đó. Gate ấy so khớp hai
chiều, và ở đây chiều "entity đã khai nhưng bảng chưa có" đỏ **đúng như mong muốn**: nó là thứ ép
WR tạo bảng thật thay vì để hợp đồng và kho tiếp tục nói hai chuyện khác nhau.

**Hệ quả đã biết.** Mọi task card pin hash `entities.yaml` chuyển `STALE`; `contracts/modules.yaml`
`data_owner_of` của MOD-data-store chưa có token `maintenance_window` (`CR-PC02-24`, PC01 sửa —
phép so hai chiều EV-PC02-06 đang FAIL đúng một phần tử vì việc này); và mọi artefact nêu
"37 / 21 / 2" hoặc "60 entity" nay sai — cập nhật trong `PKT-PC02-FIX17`.
