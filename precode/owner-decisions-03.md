---
contract_id: CT-precode-owner-decisions-03
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20260907-03
issuer: Owner (người dùng của phiên Claude Code này), chỉ thị bằng văn bản trực tiếp trong phiên
issued_at: 2026-09-07
evidence_ref: "Claude Code session session_0156UBBHDSeC9soECzSVUb3U, 2026-09-07"
authority_created: AUTH-OWNER-20260907-04
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/OWNER-DECISIONS-20260907-03.md (bản gốc của biên bản này)"
  - precode/owner-decisions.md (OD-20260907-01), precode/owner-decisions-02.md (OD-20260907-02)
  - docs/master-plan.md §Giai đoạn 2
  - evidence/audits/A3-R4-report.md
  - contracts/collector/collector-probe.md §6
requirement_refs: [precode/requirements.csv, REQ-A6, REQ-D05, REQ-D09]
decision_refs: [OD-20260907-01, OD-20260907-02, AMD-ENT-owner-01, PROV-PC00-08, PROV-PC08-01]
producers: [PC00]
consumers: [PC01, PC02, PC03, PC04, PC05, PC06, PC07, PC08, PC09, PC10]
dependencies: [precode/owner-decisions-02.md, precode/decision-register.md, precode/baseline.json, docs/master-plan.md]
scope: >
  Biên bản quyết định của Owner ngày 2026-09-07, vòng ba (ba mục). Đây là văn bản CHUYỂN NGỮ
  nguyên nội dung, không diễn giải lại. Nó phê chuẩn AMD-ENT-owner-01 và PROV-PC00-08, và mở
  lối vào Giai đoạn 2 (2A probe khả thi X, 2B paper connector) với hai cổng chặn còn nguyên.
verification: E0 — self-validation (EV-PC00-11); không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20260907-03` — 2026-09-07 (vòng ba)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20260907-03` |
| Người ban hành | **Owner** — chỉ thị bằng văn bản trực tiếp: *"accept both, start phase 2"*, sau một báo cáo Giai đoạn 0/1 nêu **đích danh đúng hai mục**: `AMD-ENT-owner-01` và `PROV-PC00-08` |
| `evidence_ref` | Claude Code session `session_0156UBBHDSeC9soECzSVUb3U`, 2026-09-07 |
| Authority phát sinh | **`AUTH-OWNER-20260907-04`** — parent của **mọi** Worker packet thuộc Giai đoạn 2 |
| Biên bản trước | `OD-20260907-01` (`precode/owner-decisions.md`) và `OD-20260907-02` (`precode/owner-decisions-02.md`) |
| Bản gốc | `…/scratchpad/packets/OWNER-DECISIONS-20260907-03.md` do Coordinator phát |

**Quy tắc chuyển ngữ.** File này ghi lại nguyên nội dung biên bản. Cột "Quyết định của Owner" là câu trả lời
**nguyên văn**; cột "Hiệu lực" là hệ quả do **chính biên bản** nêu, không phải suy diễn của PC00. Ở đâu PC00
thêm ghi chú, ghi chú đó nằm ngoài bảng và được đánh dấu rõ (§4, §5).

**"Both" là hai mục nào.** Chỉ thị dùng đại từ; biên bản khai rõ nó trỏ vào báo cáo Giai đoạn 0/1 đã nêu
**đích danh đúng hai mục**. PC00 chép đúng hai mục đó và **không** mở rộng sang bất kỳ mục `PROVISIONAL` nào
khác đang mở — xem §4 mục 4.

## 2. Ba quyết định

| # | Mục | Quyết định của Owner | Hiệu lực |
| --- | --- | --- | --- |
| 1 | `AMD-ENT-owner-01` — bốn trường credential/lockout trên `owner` (`entities.yaml` 0.2.0) | **Ratified** | Trạng thái amendment `PROVISIONAL` → `ACCEPTED (OD-20260907-03)`; `entities.yaml` **giữ** `CONTRACT_READY`; nhãn `IMPLEMENTATION_VERIFIED` của card auth **không còn** đứng trên một hợp đồng provisional |
| 2 | `PROV-PC00-08` — ghi mã dưới lease theo dõi bằng thông điệp, có review độc lập; **không** có cưỡng chế ở mức hệ điều hành | **Accepted** | Hàng trong sổ đăng ký → `ACCEPTED (OD-20260907-03)`; **rủi ro còn lại được Owner thừa nhận** |
| 3 | Bắt đầu Giai đoạn 2 theo `docs/master-plan.md`: **2A** = M0 probe khả thi X (card `TC-x-feasibility-probe`, `TC-collector-checkpoint-resume`); **2B** = M2 paper connector (operation `research.fetch_work_metadata` / `research.get_connector_health`; **phải viết card trước — hiện chưa có card nào**) | **Start** | Worker packet của Giai đoạn 2 được cấp phép; **các lần chạy live của probe vẫn bị chặn** bởi `contracts/collector/collector-probe.md` §6 mục 2–4 (mục 1, D09, đã được trả lời ở `OD-20260907-01`) và bởi việc phải chạy trên **máy của Owner**; connector vẫn bị **chặn cứng** khỏi `CONTRACT_READY` bởi `REQ-A6` cho tới khi bốn dữ kiện rate/identity được ghi lại từ **tài liệu chính thức** — **không con số nào được đoán** |

## 3. Không được quyết ở vòng này

Nguyên văn biên bản:

> Không quyết ở vòng này (đã hỏi riêng): các mục cổng probe 2–4; bốn dữ kiện `REQ-A6`, hoặc quyền cho một
> Worker tải tài liệu chính thức của arXiv/OpenAlex qua mạng.

## 4. Những gì quyết định này **không** làm

Năm điều dưới đây do PC00 ghi thêm để không ai đọc rộng hơn văn bản. Chúng đều suy trực tiếp từ §2 và §3 của
chính biên bản, không thêm ràng buộc mới.

1. **Không mở mạng.** Mục 3 của biên bản **và** dòng "không quyết" cùng nói một điều: quyền tải tài liệu
   chính thức của arXiv/OpenAlex **chưa** được cấp. Quyền mạng duy nhất đang có vẫn là quyền của
   `OD-20260907-02` mục 4 — cài gói đã khai báo từ PyPI/npm, không gì khác.
2. **Không gỡ cổng probe.** `collector-probe.md` §6 mục **2–4** vẫn chặn mọi lần chạy live, và probe vẫn
   phải chạy trên máy của Owner. "Start phase 2" cấp phép **viết** card và mã của 2A; nó **không** cấp phép
   chạy probe thật. `REQ-AC16` và các mục `KC` không đổi trạng thái.
3. **Không cho phép đoán số cho connector.** `REQ-A6` vẫn `KC`; bốn dữ kiện rate/identity phải đến từ tài
   liệu chính thức. Cho tới lúc đó `research_connector_rate_limit` giữ bốn giá trị `null` với
   `status: PLACEHOLDER_KC` và sàn an toàn `min_interval_ms = 3000` (§8.5 của sổ đăng ký), và 2B **không**
   được tuyên bố `CONTRACT_READY`.
4. **Không phê chuẩn mục `PROVISIONAL` nào khác.** "Both" = đúng hai mục mà báo cáo nêu tên. Mọi
   `PROV-PC03-*`, `PROV-PC04-*` chưa được nêu, `PROV-PC00-05`, `PROV-PC00-06`, `PROV-PC10-*` và
   `PROV-P0-01` **vẫn `PROVISIONAL`**. Một đại từ không phê chuẩn những thứ nó không trỏ tới.
5. **Không đóng finding nào và không giải `REQ-OQ03`.** Finding của A1/A2/A3 sống theo `protocol.md` §8;
   `REQ-OQ03` vẫn `OWNER_DECISION_REQUIRED` và vẫn chặn M3, nên Giai đoạn 3 vẫn bị chặn.

## 5. Ghi chú của PC00 về ba mục có sắc thái

- **Mục 1 — điều nó sửa là một chỗ dựa, không phải một con số.** Bốn cột đã tồn tại trong `entities.yaml`
  và trong mã từ trước; điều đổi là **thẩm quyền** dưới chúng. Trước biên bản này, nhãn
  `IMPLEMENTATION_VERIFIED` của card auth đứng trên một amendment `PROVISIONAL` do Coordinator ký — đúng
  chỗ mà `A3-R2`, `A3-R3` và `A3-R4` đều ghi là điểm yếu còn lại của card đó. Nay chỗ dựa ấy là một quyết
  định của Owner. **Nhưng verdict của auditor không tự đổi vì thế**: `A3-R4` §6 nói per-card claim "unchanged",
  và một biên bản của Owner **không** phải một lượt xác minh độc lập. Điều được gỡ là *tính tạm thời của hợp
  đồng*, không phải *giới hạn của bằng chứng*.
- **Mục 2 — Owner đã thừa nhận rủi ro, không phải xoá nó.** `PROV-PC00-08` mô tả ba chế độ hỏng cụ thể: ghi
  ra ngoài tập ghi **không** bị chặn (chỉ bị phát hiện sau khi byte đã lên đĩa); hai Worker song song trên
  cùng file không có fencing thật; không có audit log bền vững do service ghi. `ACCEPTED` nghĩa là Owner
  chấp nhận **vận hành với** ba điều đó, không phải chúng đã được sửa. `enforcement` trong
  `agent_profile/registry.json` vẫn là `NOT_IMPLEMENTED` — và phải giữ nguyên như vậy cho tới khi có guard thật.
- **Mục 3 — 2B chưa có card, và biên bản tự nói vậy.** Biên bản ghi thẳng *"a card must be written first —
  none exists"*. Vậy "start phase 2" cho 2B là cấp phép cho **việc viết card**, không phải cho việc triển
  khai một card. Bất kỳ ai đọc dòng này thành "được viết connector" là đọc trước một bước mà chính biên bản
  đã đánh dấu là còn thiếu.

## 6. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/owner-decisions.md` | Dòng trỏ tới biên bản vòng ba này |
| `precode/decision-register.md` §8.11 | `AMD-ENT-owner-01` → `ACCEPTED (OD-20260907-03)` |
| `precode/decision-register.md` §8 | `PROV-PC00-08` → `ACCEPTED (OD-20260907-03)` |
| `precode/decision-register.md` §8.12 | Hàng quyết định cho lối vào Giai đoạn 2 (2A và 2B) kèm hai cổng còn chặn |
| `precode/owner-decision-request.md` | Ba dòng phiếu trả lời vòng ba được điền |
| `precode/baseline.json` | Anchor `OD-20260907-03` |
| `agent_profile/registry.json` | `AUTH-OWNER-20260907-04`; `coding_phase.status: PHASE_2_IN_PROGRESS`; Giai đoạn 0/1 ghi là hoàn tất kèm tham chiếu `A3-R4` |
| `contracts/data/entities.yaml` | **Không sửa ở gói này** — `worker-W3n` đang cập nhật khối amendment song song |
| `precode/gates.yaml`, `precode/review.md` | **Chưa làm** — thuộc PC09 (`CR-PC00-20`, nay gồm cả vòng ba) |
| `agent-tasks/` | 2B **chưa có card**; viết card là việc đầu tiên của 2B |
