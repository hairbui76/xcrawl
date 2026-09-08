---
contract_id: CT-precode-owner-decisions
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260907-01
issuer: Owner (người dùng của phiên Claude Code này), được Coordinator phỏng vấn theo từng câu hỏi
issued_at: 2026-09-07
evidence_ref: "Claude Code session session_017QmDJtMqD9o1z79waqSB9W, 2026-09-07 (câu trả lời thu qua prompt có cấu trúc; transcript do nền tảng lưu giữ)"
authority_created: AUTH-OWNER-20260907-02
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260907.md (bản gốc của biên bản này)"
  - precode/owner-decision-request.md (bản yêu cầu 24 mục đã được trả lời)
  - SRC-SPEC v0.2, SRC-PLAN v0.1
requirement_refs: [precode/requirements.csv]
decision_refs: [B01..B17, AMD-B01..AMD-B17, ADR-0001..ADR-0010, PROV-PC00-01..06, PROV-PC04-01..09, PROV-PC08-01..05, PROV-PC01-03]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/decision-register.md, precode/owner-decision-request.md, precode/adr/, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-07, phê chuẩn 25 mục. Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó là căn cứ để B01-B17 chuyển từ PROVISIONAL sang
  RATIFIED và để các amendment/ADR tương ứng chuyển sang ACCEPTED.
verification: E0 - self-validation (EV-PC00-04, EV-PC00-08); không có E1-E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260907-01` — 2026-09-07

> **Biên bản tiếp theo.** Vòng hai nằm ở `precode/owner-decisions-02.md` — `OD-20260907-02` (2026-09-07, authority `AUTH-OWNER-20260907-03`): phê chuẩn `ADR-0011`, mở lối vào Giai đoạn 0 và Giai đoạn 1 của `docs/master-plan.md`. Vòng ba ở `precode/owner-decisions-03.md` — `OD-20260907-03`
> (authority `AUTH-OWNER-20260907-04`): phê chuẩn `AMD-ENT-owner-01` và `PROV-PC00-08`, mở lối vào Giai đoạn 2.
> Vòng bốn ở `precode/owner-decisions-04.md` — `OD-20260907-04` (authority `AUTH-OWNER-20260907-05`): đóng nốt
> hai mục mà vòng ba để mở — cổng probe `§6` mục 2–4, và một quyền mạng hẹp một lần để đọc tài liệu chính thức
> phục vụ `REQ-A6` (**không** giải `REQ-A6`).
> Vòng năm ở `precode/owner-decisions-05.md` — `OD-20260908-05` (authority `AUTH-OWNER-20260908-06`,
> 2026-09-08): **ủy quyền nghiên cứu** `REQ-OQ03` (không giải nó) và cấp quyền mạng hẹp chỉ-đọc-tài-liệu
> `core.telegram.org` cho `CR-PC07-04`. Lựa chọn model cụ thể là một biên bản **riêng**, `OD-20260908-06`.
> Vòng bảy và vòng tám ở `precode/owner-decisions-07.md` và `-08.md` — `OD-20260908-07`
> (authority `AUTH-OWNER-20260908-08`: nới quyền tìm dữ kiện Telegram sang WebSearch; chốt rằng **Owner tự
> ký** `REQ-A5`) và `OD-20260908-08` (authority `AUTH-OWNER-20260908-09`: Owner **đích thân ký** `REQ-A5`
> cho Anthropic, chấp nhận tường minh bảo đảm `TC-A5-01`). Hai file đó là **bản ghi song hành theo quy ước**;
> hiệu lực thực chất nằm ở `decision-register.md` §8.14.3 và §8.15.1.
> Vòng mười ở `precode/owner-decisions-10.md` — `OD-20260908-10` (authority `AUTH-OWNER-20260908-11`,
> 2026-09-08): ba câu hỏi do card Giai đoạn 5 nêu — lưu target **chưa phân tích** kèm nhãn cố định (`B16`
> **không** bị nới), giữ `/save <id>` làm trigger tạm, và nhắc ba lệnh **chỉ** cho chat đã liên kết (chat lạ
> **vẫn im lặng**).
> Vòng chín ở `precode/owner-decisions-09.md` — `OD-20260908-09` (authority `AUTH-OWNER-20260908-10`,
> 2026-09-08): **thay** điều kiện khởi động Giai đoạn 5 của vòng năm (từ *"năm dữ kiện land"* — chưa bao giờ
> thỏa — thành **khởi động có phạm vi, chỉ văn bản thuần**). Nó **không** giải ba dữ kiện Telegram còn lại.
> Biên bản này **không** bị chúng thay thế; các biên bản **cộng dồn** (`OD-20260907-01` … `OD-20260908-09`).

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260907-01` |
| Người ban hành | **Owner** — người dùng của phiên Claude Code này, được Coordinator phỏng vấn theo từng câu hỏi |
| `evidence_ref` | Claude Code session `session_017QmDJtMqD9o1z79waqSB9W`, 2026-09-07 (câu trả lời thu qua prompt có cấu trúc; transcript do nền tảng lưu giữ) |
| Authority phát sinh | **`AUTH-OWNER-20260907-02`** — phê chuẩn các mục dưới đây; chuyển các quyết định `PROVISIONAL` tương ứng thành amendment/ADR `ACCEPTED`; là parent của mọi Worker packet ghi lại chúng |
| Bản gốc | `evidence/coordination/` (bản sao nguyên văn của biên bản do Coordinator phát) |

**Quy tắc chuyển ngữ.** File này ghi lại nguyên nội dung biên bản. Cột "Quyết định của Owner" là câu trả lời **nguyên văn**; cột "Hiệu lực" là hệ quả do biên bản tự nêu, không phải suy diễn của PC00. Ở đâu PC00 thêm ghi chú, ghi chú đó nằm ngoài bảng và được đánh dấu rõ.

## 2. Phạm vi **không** được quyết định

Biên bản nêu rõ ba giới hạn. Chúng **không** được nới bởi bất kỳ mục nào ở §3:

1. **`REQ-OQ03` (provider và model) vẫn `OWNER_DECISION_REQUIRED`.** Mốc **M3 vẫn bị chặn** vì lý do đó.
2. **Mọi mục mang trạng thái `KC` vẫn là `KC`.** Buổi phỏng vấn không tạo ra bằng chứng runtime nào.
3. Trần claim `CONTRACT_READY` chỉ được nâng trong **bốn phạm vi** mà `A2-R4` đã nêu là đủ điều kiện — ranh giới và quyền; dữ liệu và identity; workflow và trạng thái; báo cáo và thời gian — và **chỉ cho những file mà dependency còn lại không phải `KC`**.

## 3. Hai mươi lăm quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | B12 / D09 Chrome profile | **Profile riêng của dự án** | D09 ĐX → XN; `REQ-OQ01` đã được trả lời; M0/SP1 không còn bị chặn bởi quyết định này (probe vẫn `NOT_RUN`) |
| 2 | B12 topology | **Bỏ cạnh collector → analysis trực tiếp** | `AMD-B12` ACCEPTED; D08/D42/D50 ĐX → XN; `ADR-0001` accepted |
| 3 | Stack (`REQ-OQ02`) | **B — Python workers + TypeScript web** | `ADR-0006` viết lại: quyết định = B (thay thế phương án A đã đề xuất), status accepted; §3 đường dẫn và §8 lệnh build/test của **cả 18 task card** phải viết lại theo B; **hợp đồng không đổi** |
| 4 | B08 timezone | **(a) một IANA timezone; giá trị `Asia/Ho_Chi_Minh` được xác nhận** | `AMD-B08` ACCEPTED; `ADR-0007` accepted; fixture lịch giữ nguyên |
| 5 | B01 | (a) freeze tại publish | `AMD-B01` ACCEPTED; `ADR-0004` accepted |
| 6 | B02 | (a) bốn trường, delivery tách rời | `AMD-B02` ACCEPTED (gồm cả câu chữ AC-03); `ADR-0002` accepted |
| 7 | B03 | (a) `delivery.unknown`, không auto-retry | `AMD-B03` ACCEPTED (câu chữ AC-14); `ADR-0003` accepted |
| 8 | B04 | (a) sổ coverage/pending/backfill riêng | `AMD-B04` ACCEPTED |
| 9 | B05 | (a) không ingest trùng theo post ID | `AMD-B05` ACCEPTED (câu chữ AC-04) |
| 10 | B06 | (a) alias + phiên bản + target union | Bổ sung mô hình dữ liệu ACCEPTED; `ADR-0009` accepted |
| 11 | B07 | (a) analysis key + generation | `AMD-B07` ACCEPTED; `ADR-0008` accepted |
| 12 | B09 | (a) ngoại lệ hẹp cho mã liên kết | `AMD-B09` ACCEPTED |
| 13 | B10 | (a) resume chỉ trong app, 3 lệnh, hủy liên kết trong app | `AMD-B10` ACCEPTED; `F-PC00-01` được xác nhận |
| 14 | B11 | (a) snapshot nhất quán + manifest + restore drill | `AMD-B11` ACCEPTED (câu chữ D58); `ADR-0005` accepted; RPO/RTO theo mục 20 |
| 15 | B13 | (a) secret theo phạm vi, tool của CLI bị tắt, disabled-until-verified | `ADR-0010` accepted; **AC-16 vẫn `BLOCKED`** cho tới khi một probe đạt |
| 16 | B14 | (a) `insufficient_evidence` | ACCEPTED; D53 **vẫn ĐX-trong-P0** chỉ ở phần hiệu chỉnh tham số (A4) |
| 17 | B15 | (a) chỉ số có phạm vi + số đếm conflict | `AMD-B15` ACCEPTED |
| 18 | B16 | (a) ba loại phát biểu + comparator unknown | `AMD-B16` ACCEPTED (câu chữ AC-11) |
| 19 | B17 | (a) chỉ các mục được chọn, partial kèm danh sách pending | `AMD-B17` ACCEPTED |
| 20 | Bộ giá trị mặc định (OQ) | **Chấp nhận tất cả**: N = 7 ngày; 200 post hoặc 30 phút; 08:00/20:00 giờ địa phương; không có giờ yên lặng; ngưỡng và model chưa đặt cho tới khi đo được; export Saved hoãn sang P1 (`F-PC00-02` được xác nhận) | Các giá trị **vẫn PROVISIONAL theo bản chất** ở chỗ nào cần đo (OQ05 sau M0, OQ08 sau M3, OQ09 sau A3) nhưng **được Owner chấp nhận làm giá trị làm việc** |
| 21 | `REQ-OQ03` provider/model | **Quyết định sau** | Vẫn `OWNER_DECISION_REQUIRED`; **chỉ** chặn M3 |
| 22 | Tám tham số PC04 + kỳ rỗng | **Chấp nhận tất cả + phương án (b)** | `PROV-PC04-01..09` → giá trị làm việc được Owner chấp nhận; ngưỡng **vẫn `uncalibrated`** cho tới A2 |
| 23 | Tham số PC08 | **Chấp nhận tất cả** (RPO 24 h, RTO 2 h, backup 03:00, 14 ngày + 8 tuần + hằng tháng, Argon2id, idle 12 h / tuyệt đối 30 ngày, khóa 5 lần/15 phút, token 180 ngày, audit 365 ngày, bản ghi xóa giữ vĩnh viễn) | `PROV-PC08-01..05` → được Owner chấp nhận |
| 24 | Phạm vi `data.purge_all` | **(a) chỉ dữ liệu nghiên cứu**; **giữ** đăng nhập, secrets, liên kết Telegram, cấu hình provider, lịch; **backup KHÔNG bị xóa** | `PROV-PC00-01` / `PROV-PC01-03` đã giải; danh sách loại trừ của `TXN-purge-all` = đúng tập được giữ; `MOD-data-admin-service` được gỡ chặn |
| 25 | Hai thay đổi kỹ thuật | **Chấp nhận cả hai** (mã `CSRF_REJECTED`; resume-từ-`blocked` có lý do bắt buộc) | `PROV-PC00-02` / `PROV-PC00-04` accepted |

## 4. Từ vựng trạng thái kể từ đây

Nguyên văn biên bản:

> Một mục đã được phê chuẩn mang nhãn `ACCEPTED (OD-20260907-01)`; các blocker B01–B17 chuyển từ `PROVISIONAL` sang `RATIFIED` trong decision register, và `open_product_blockers` của registry trở thành rỗng cùng một danh sách `ratified_product_blockers` có trích `evidence_ref`. `claim_ceiling` của hợp đồng chỉ được nâng lên `CONTRACT_READY` trong bốn phạm vi mà `A2-R4` nêu là đủ điều kiện (ranh giới và quyền; dữ liệu và identity; workflow và trạng thái; báo cáo và thời gian) và chỉ với những file mà dependency còn lại không phải `KC`.

## 5. Những gì quyết định này **không** làm

Bốn điều dưới đây do PC00 ghi thêm để không ai đọc rộng hơn văn bản. Chúng đều suy trực tiếp từ §2 và §4 của chính biên bản, không thêm ràng buộc mới.

1. **Không đóng finding nào.** Các finding của A1/A2 sống theo vòng đời riêng (`protocol.md` §8) và cần xác minh độc lập trên epoch mới. Phê chuẩn một quyết định sản phẩm không phải là disposition của một finding audit.
2. **Không tạo bằng chứng runtime.** Mọi mục `KC` vẫn `KC`. `REQ-A1`, `REQ-A2`, `REQ-A3`, `REQ-A4`, `REQ-A5`, `REQ-A6`, `REQ-A7` không đổi trạng thái. `REQ-AC16` vẫn `BLOCKED` cho tới khi một probe CLI/ACP đạt (mục 15). E1–E4 vẫn `NOT_RUN`.
3. **Không nâng trần claim của cả bộ.** Chỉ bốn phạm vi được `A2-R4` nêu mới đủ điều kiện, và chỉ với file có dependency không phải `KC`. Ba mục còn `KC` chặn nâng nhãn ở đúng phạm vi của chúng: `REQ-A6` (nhịp gọi arXiv/OpenAlex), `REQ-A5` (điều khoản CLI/ACP), `REQ-OQ03`.
4. **Không tự sửa đặc tả nguồn.** `precode/source/spec-v0.2.md` và `precode/source/pre-code-plan-v0.1.md` là bản sao bất biến. Các amendment mô tả văn bản thay thế **đã được chấp nhận**; việc phát hành một đặc tả v0.3 áp dụng chúng là công việc riêng, chưa được giao.

## 6. Ghi chú của PC00 về ba mục có sắc thái

Ba mục dễ bị đọc thành "đã xong" trong khi biên bản nói ít hơn thế:

- **Mục 16 (B14).** `insufficient_evidence` được chấp nhận, nhưng **D53 vẫn là ĐX trong một hạng mục P0** ở phần hiệu chỉnh tham số. `REQ-D53` **không** đổi trạng thái trong `requirements.csv`. Điều được chốt là *cách xử lý khi thiếu dữ liệu*, không phải *thuật toán đã được kiểm chứng*.
- **Mục 20 và 22.** "Chấp nhận tất cả" nghĩa là các con số trở thành **giá trị làm việc được Owner chấp nhận**, không phải giá trị đã đo. Biên bản tự nói chúng "vẫn PROVISIONAL theo bản chất" ở chỗ cần đo, và ngưỡng similarity **vẫn mang nhãn `uncalibrated`**. Vì vậy chỉ tiêu §1.4 vẫn chưa được phép tuyên bố đạt.
- **Mục 3 (stack B).** Owner chọn **B**, không phải A như kế hoạch khuyến nghị và như `ADR-0006` từng ghi. Hệ quả nằm gọn ở task card: §3 đường dẫn và §8 lệnh build/test của 18 card phải viết lại. **Hợp đồng, schema, scenario và fixture không đổi** — đúng như thiết kế của kế hoạch đã dự liệu để việc chọn stack muộn không gây thiệt hại.

## 7. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/decision-register.md` §1, §2 | B01–B17 → `RATIFIED (OD-20260907-01)` |
| `precode/decision-register.md` §3 | 14 amendment → `ACCEPTED (OD-20260907-01)` |
| `precode/decision-register.md` §8 | `PROV-PC00-01..06` và các `PROV-PC0x-nn` được nêu tên → `ACCEPTED (OD-20260907-01)` |
| `precode/adr/` | `ADR-0001..0005`, `0007..0010` → `accepted`; `ADR-0006` viết lại theo phương án **B**, `accepted` |
| `precode/requirements.csv` | D08, D09, D42, D50: `ĐX` → `XN`, ghi chú `ratified OD-20260907-01` |
| `precode/owner-decision-request.md` | Banner `ANSWERED 2026-09-07` và phiếu trả lời đã điền |
| `agent_profile/registry.json` | `open_product_blockers: []`, `ratified_product_blockers`, `ratification_evidence` |
| `precode/baseline.json` | Anchor của biên bản này; `claim_ceiling` thành object theo phạm vi |
| `agent-tasks/` (PC10) | **Chưa làm** — 18 card cần viết lại §3 và §8 theo stack B |
