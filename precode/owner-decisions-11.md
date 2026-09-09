---
contract_id: CT-precode-owner-decisions-11
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260909-11
issuer: Owner (người dùng của phiên Claude Code này), qua AskUserQuestion sau commit đợt nối dây tích hợp `81bcaf4`
issued_at: 2026-09-09
evidence_ref: "Claude Code session session_01JRCNWfwz19Kfq1EkCmqnmG, 2026-09-09"
authority_created: AUTH-OWNER-20260909-12
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260909-11.md (bản gốc của biên bản này)"
  - precode/owner-decisions-03.md (OD-20260907-03 — vòng cùng hình dạng, phê chuẩn AMD-ENT-owner-01)
  - precode/decision-register.md §8.16 (bản ghi hiệu lực, worker-W3n)
  - evidence/audits/A3-P5-R1-report.md, A3-P5-R2-report.md, A3-P5-R3-report.md
requirement_refs: [precode/requirements.csv]
decision_refs: [AMD-ENT-maintenance-01, AMD-ENT-owner-01, OD-20260907-03, CR-TC-storage-04, CR-TC-storage-06]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/decision-register.md, precode/baseline.json, precode/change-control.md]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-09, vòng mười một (một mục). Đây là văn bản CHUYỂN
  NGỮ nguyên nội dung, không diễn giải lại. Owner phê chuẩn AMD-ENT-maintenance-01. Hiệu lực
  thực chất đã được worker-W3n ghi ở decision-register §8.16; file này là bản ghi song hành
  theo quy ước và KHÔNG quyết lại điều gì.
verification: E0 — self-validation (EV-PC00-17) + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260909-11` — 2026-09-09 (vòng mười một)

> **Bản ghi hiệu lực là `precode/decision-register.md` §8.16** (`worker-W3n`, `PKT-PC02-FIX20`, lease
> `LEASE-PC02-e24`, nhả 2026-09-09T07:40Z). File này là **bản ghi SONG HÀNH THEO QUY ƯỚC** — file độc lập +
> anchor baseline + authority trong registry — và **không** quyết lại điều gì. Khi hai bên lệch: **§8.16
> thắng**.

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260909-11` |
| Người ban hành | **Owner** — qua `AskUserQuestion`, **sau** commit đợt nối dây tích hợp `81bcaf4` |
| `evidence_ref` | Claude Code session `session_01JRCNWfwz19Kfq1EkCmqnmG`, 2026-09-09 |
| Authority phát sinh | **`AUTH-OWNER-20260909-12`** |
| Vòng cùng hình dạng | **`OD-20260907-03`** — phê chuẩn `AMD-ENT-owner-01`, amendment kỹ thuật **thứ nhất** của Coordinator |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260909-11.md` |

## 2. Một quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | `AMD-ENT-maintenance-01` — amendment kỹ thuật của Coordinator thêm entity `maintenance_window` vào `contracts/data/entities.yaml` (0.3.0; tập purge 37/22/2 = 61), vì `contracts/state/storage.yaml` `T-ST-03` **đòi ghi một hàng maintenance-window mà không entity nào khai** (`CR-TC-storage-04`/`-06`); ghi `PROVISIONAL` bởi `worker-W3n` (`PKT-PC02-FIX16`), lan truyền sang **mười** artefact (`FIX17`/`FIX19`), hiện thực bởi `WR` (migration `0015`) và `W6B` (backup CLI), **xác minh ở mức tiến trình** bởi `A3-P5-R1`/`R2`/`R3` | **Ratified** | Trạng thái amendment `PROVISIONAL` → `ACCEPTED`, `ratified_by: OD-20260909-11`; claim "health được lưu bền" của card storage và "restore hai bước" của card backup **không còn đứng trên một hợp đồng provisional**. Hàng trong sổ đăng ký → `ACCEPTED (OD-20260909-11)`. Các card ghim `entities.yaml`/`change-control`/`decision-register` chuyển `STALE` → **một** lượt re-pin. |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này: **không có**. Cùng hình dạng với `OD-20260907-03` (phê chuẩn `AMD-ENT-owner-01`).

## 4. Điều phê chuẩn này **làm** — và điều nó **không** làm

Câu *"không quyết gì thêm"* ở §3 nói về **phạm vi câu hỏi**, không phải về phạm vi hệ quả. Ba ranh giới:

1. **Được gỡ: tính tạm thời của HỢP ĐỒNG.** Trước vòng này, hai claim đã được audit xác minh —
   `storage.health` sống qua tiến trình, và restore hai bước của backup — đứng trên một entity mà **Owner
   chưa từng được hỏi**. Nay chỗ dựa ấy là một quyết định của Owner. Đây đúng là điều `A3-P5-R1` §6 yêu cầu:
   *"nên được đưa lên vòng Owner kế tiếp thay vì mặc nhiên thành sự thật vì không ai phản đối"*.
2. **Không được gỡ: giới hạn của BẰNG CHỨNG.** Phê chuẩn một hợp đồng **không** phải một lượt xác minh. Ba
   verdict `A3-P5-*` giữ nguyên phạm vi của chúng, và mức bằng chứng của hai card ấy **không** đổi vì biên
   bản này. Cùng luật đã áp ở `OD-20260907-03` mục 1 với `AMD-ENT-owner-01`.
3. **Không đóng finding nào.** `protocol.md` §8 vẫn là luật: đóng một finding cần disposition authority sau
   xác minh độc lập, và một biên bản Owner **không** thay được điều đó.

## 5. Vì sao vòng này tồn tại — một quan sát về hình dạng lặp lại

Đây là **lần thứ hai** trong dự án một mâu thuẫn nội bộ giữa **hai file đã đóng băng** được xử lý theo đúng
chuỗi này:

| | `AMD-ENT-owner-01` | `AMD-ENT-maintenance-01` |
| --- | --- | --- |
| Mâu thuẫn | `secrets.md` đòi mật khẩu + lockout; `entities.yaml` không có cột nào | `storage.yaml` `T-ST-03` đòi hàng maintenance-window; `entities.yaml` không có entity nào |
| Ai dừng lại | Card auth, rồi audit `A3-R1` (`F-A3R1-02`/`-06`) | `worker-WR` **dừng ở `SG-EDGE`** thay vì tự bịa entity |
| Ai ký tạm | Coordinator (kỹ thuật), ghi `PROVISIONAL` | Coordinator (kỹ thuật), ghi `PROVISIONAL` |
| Ai phê chuẩn | Owner, `OD-20260907-03` | Owner, **biên bản này** |

**Điều đáng giữ từ hình dạng ấy.** Cả hai lần, thứ ngăn một Worker "sửa cho xong" là **một guard dừng lại**
(`SG-EDGE`) và một quy ước bắt buộc gọi tên trạng thái tạm (`PROVISIONAL`). Cả hai lần, amendment kỹ thuật
của Coordinator là **hợp lệ** — nó chỉ làm hai file đã đóng băng thôi mâu thuẫn — nhưng **không đủ**: nó vẫn
phải đi tới Owner, vì một entity mới là dữ liệu người dùng sẽ mang. Việc này lần này **không** bị bỏ quên là
nhờ `A3-P5-R1` §6 nêu đích danh nó trong phần residual, và `PKT-PC00-FIX33` chép nó vào danh mục lưu trữ với
nhãn `PROVISIONAL` thay vì để nó im lặng trôi qua.

## 6. Phần còn nợ **không** được vòng này chạm tới

Ghi ra để không ai đọc một `ACCEPTED` mới thành một bước tiến của sản phẩm:

- **Owner vẫn không tạo hay đọc được báo cáo** — `report_context` chưa nối (`CR-P0-07`: không có hiện thực
  `TagConfigVersionPort`, không có model embedding thật, `REQ-OQ09`). Nguyên văn `A3-P5-R2`: *"đầu ra của sản
  phẩm không tồn tại"*.
- **Tag** vẫn chưa có card (`MOD-tag-service`); **research connector** vẫn chưa nối (`SG-DOC` — không hợp
  đồng nào nêu host/endpoint của hai API — cộng `SG-LIVE`).
- **`E3`/`E4` vẫn `NOT_RUN` ở khắp nơi**: chưa một lời gọi live nào tới AI, Telegram hay X; chưa một drill
  restore thật; **`SP1` chưa bao giờ chạy**. Cả hai adapter AI vẫn `enabled: false` vì cô lập chưa kiểm.
- **`docs/owner-runbook.md` §9.4 vẫn mang chữ trước đợt nối dây** — `A3-P5-R1` §6 nêu; cần `WS2` xác minh lại
  trước khi một Owner làm theo.

**Một mục đã rời danh sách này, ghi vì nó rời đúng cách.** `F-A3-P5R3-01` (manifest backup ghim pin **đọc**
cũ) **đã đóng bằng phép đo**: `W6B` phát lại manifest (`PKT-TC-BACKUP-FIX6`,
`…-E1-20260909T104000Z.json`) và `worker-W6n` **tự băm lại** rồi đăng ký bản phát lại — **0 pin lệch ở cả hai
hạng** (`evidence/handoffs/PC09-handoff.md` §W2). Đúng con đường mà auditor đã nêu: **phát lại**, và **không**
sửa hash của các bản đã bị thay thế — độ trôi của chúng là sự thật lịch sử.

## 7. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/decision-register.md` §8.16 | **Bản ghi hiệu lực** (`worker-W3n`) — PC00 **không** chạm |
| `precode/decision-register.md` §0 | Nhãn `ACCEPTED (OD-20260909-11)` và đoạn "Cập nhật vòng mười một" |
| `precode/owner-decisions.md` | Dòng trỏ |
| `precode/baseline.json` | Anchor `OD-20260909-11` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260909-12` |
| `precode/owner-decision-request.md` | Câu hỏi phê chuẩn **rời** khối "VẪN CHỜ" |
| `contracts/data/entities.yaml` | **Không sửa** — thuộc PC02; entity đã có từ `PKT-PC02-FIX16` |
