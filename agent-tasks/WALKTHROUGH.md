---
contract_id: CT-tasks-walkthrough
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs: [SRC-PLAN §11 PC10 checklist mục 5, SRC-PLAN §15, SRC-PLAN §6, SRC-PLAN §8.3]
requirement_refs: [REQ-AC03, REQ-AC04, REQ-AC14, REQ-AC15]
decision_refs: [B02, B03, B05, AMD-B02, AMD-B03, AMD-B05, ADR-0002, ADR-0003, "CR-PC05-01", "CR-PC07-04", "CR-PC03-04", "CR-PC10-02 (đóng)", "CR-PC10-03 (đóng)", "R5-01", "R5-02"]
invariant_refs: [I02, I09, I10, I13, I15]
producers: []
consumers: []
dependencies:
  - agent-tasks/TC-collector-checkpoint-resume.md
  - agent-tasks/TC-telegram-unknown-delivery.md
  - agent-tasks/TEMPLATE.md
scope: >-
  Walkthrough bắt buộc của PKT-PC10 mục 5: đọc một card collector và một card delivery như thể mình là agent
  chỉ có card cộng các file card trỏ tới, rồi trả lời một câu hỏi duy nhất — có chỗ nào phải ĐOÁN về giao
  tiếp hoặc trạng thái không. Mọi chỗ phải đoán được ghi thành CR-PC10-nn.
verification: >-
  EV-PC10-03 (SELF_VALIDATION): walkthrough thủ công do chính PC10 thực hiện, đối chiếu từng bước với file
  hợp đồng đã pin. Đây là self-review, KHÔNG phải independent audit.
claim_ceiling: DRAFT_FOR_REVIEW
---

# WALKTHROUGH — Card có đủ để làm việc mà không phải đoán không?

Phương pháp: đóng vai một agent **không có ký ức cuộc trò chuyện nào**, chỉ có (a) một card, (b) những file
card trỏ tới ở §0/§2. Đi qua từng bước triển khai. Ở mỗi bước hỏi đúng một câu: *"Tôi có thể trả lời câu này
bằng file đã cho, hay tôi phải đoán?"* Mỗi lần phải đoán là một gap.

**Cập nhật sau FIX5 + PC10-FIX1.** Walkthrough gốc (epoch cũ `PC10-PIN-20260907`) tìm ra 4 gap. Ba trong bốn
cái đã được đóng bằng thay đổi hợp đồng thật, không phải bằng cách viết lại card:

| Gap gốc | Trạng thái | Đóng bằng gì |
| --- | --- | --- |
| GAP-A1 — collector gặp rate limit không có đường báo | **ĐÓNG** | `stop_reason = rate_limited` nay có trong `contracts/state/run.yaml`; `RATE_LIMITED` nay có trong `worker.report_stop.error_codes`; transition `T-RUN-25` đưa run về `running/enriching` với `outcome: partial` — **không** phải `blocked` |
| GAP-B1 — giới hạn định dạng Telegram `KC` | **VẪN MỞ** (`CR-PC07-04`) | không đóng được trong phiên không có mạng |
| GAP-B2 — không actor nào khai `telegram.send_payload` | **ĐÓNG** | `ACT-delivery-dispatcher` mới trong `contracts/capabilities.yaml`, `allowed_operations: [delivery.dispatch_next, delivery.record_receipt, delivery.mark_unknown, telegram.send_payload]`, `network_scope: [telegram_bot_api]` |
| GAP-C1 — file PC09 chưa landing | **ĐÓNG** | `scenarios.yaml` (SC01–SC53), `traceability.csv`, `gates.yaml`, `review.md`, `manifest.schema.json`, `index.json` đã có |
| GAP-C2 — baseline drift khỏi FC-W3 | **ĐÓNG** | card đã pin lại; epoch hiện hành `PC10-PIN-FCW4f-20260907` (đã thay các epoch cũ `PC10-PIN-FCW4e-20260907`, `PC10-PIN-FCW4d-20260907`, `PC10-PIN-FCW4c-20260907`, `PC10-PIN-FCW4b-20260907`, `PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`) |

**Kết quả hiện tại: 1 gap còn mở** (GAP-B1), chặn một nhánh của một card. Phần dưới giữ nguyên phân tích gốc
làm bản ghi audit, với trạng thái được đánh dấu tại chỗ.

---

## A. Card collector — `TC-collector-checkpoint-resume`

### A.1 Các bước đi được, không phải đoán

| # | Câu hỏi của agent | Trả lời được từ đâu | Kết luận |
| --- | --- | --- | --- |
| 1 | Tôi xác thực bằng gì? | `contracts/http/openapi.yaml` `securitySchemes.collectorToken` (bearer); `contracts/ops/secrets.md`; `contracts/ops/deployment.md` §7 bước 2 (file cấu hình quyền hạn chế trên máy cá nhân) | **Đủ** |
| 2 | Server ở đâu? | `openapi.yaml` `servers[0].url = https://{host}/api`, `host` do Owner cấu hình, `.invalid` là placeholder tường minh | **Đủ** — placeholder được khai là placeholder, không phải chỗ trống ngầm |
| 3 | Tôi được gọi những operation nào? | Card §4 liệt kê 9 operation; `contracts/capabilities.yaml` `ACT-collector.allowed_operations`; `network_scope: [server_api_origin, x_web]` | **Đủ** |
| 4 | Tôi bị cấm gì? | `ACT-collector.denied_capabilities`; denied case `NC-01` (`collectorToken` gọi `save.create` ⇒ 401); `contracts/modules.yaml` forbidden edges | **Đủ** |
| 5 | Lô gửi lên có hình dạng gì? | `contracts/schemas/ingest-batch.schema.json`; 6 fixture pos/neg | **Đủ** |
| 6 | Bao nhiêu item một lô? Retry mấy lần? | `contracts/retry-policy.yaml`: `ingest_batch_max_items`, `ingest_batch_attempts`, `ingest_batch_backoff`, `checkpoint_commit_cadence` | **Đủ** (giá trị PROVISIONAL nhưng có số, có đơn vị, có rationale) |
| 7 | Lease sống bao lâu? Heartbeat bao lâu một lần? | `retry-policy.yaml`: `lease_ttl_collector` = 120 s, `heartbeat_interval_collector` = 30 s, `heartbeat_grace`, `lease_epoch_rule` | **Đủ** |
| 8 | Khi nào tôi phải dừng, và dừng thì báo gì? | `contracts/ops/collector-probe.md` §4 bảng `ST-1`…`ST-8` ánh xạ thẳng sang `stop_reason` và transition `T-RUN-09/16/24` | **Đủ và tốt** — đây là phần được viết chặt nhất |
| 9 | Mất ACK thì làm gì? | `contracts/ports.yaml` `ingest.get_receipt` (*"đây là đường tra cứu bắt buộc trước retry"*) + `ingest.submit_batch.failure_timeline_vi` | **Đủ** |
| 10 | Con trỏ feed mất hiệu lực thì đọc lại có sai cam kết không? | B05/AMD-B05: cam kết là **không ingest trùng**, không phải "không bao giờ đọc lại"; fixture `b-cursor-invalidated-reread-dedup.json` | **Đủ** |
| 11 | Checkpoint ghi lúc nào? | `ingest.submit_batch.state_effects_vi` (đường chính, cùng `TXN-ingest-batch`) và `ingest.commit_checkpoint.scope_restriction_vi` (chỉ khi lô rỗng, ruling R-01) | **Đủ và rõ ràng** |
| 12 | Bố cục X đổi thì sao? | `SOURCE_LAYOUT_CHANGED` trong `contracts/errors.yaml` (đích `blocked` + `stop_reason=source_layout_changed`, `retry_class: none`, oracle 12/40 bài); `ST-7` | **Đủ** — `CR-PC05-01` đã được ruling FIX3 đóng lại trong file đã pin |

### A.2 Gap tìm được

> **GAP-A1 → `CR-PC10-02` — ĐÃ ĐÓNG ở FIX5.** *Collector gặp 429 / rate limit của X thì báo bằng đường nào?*
>
> **Kết luận hiện tại:** `worker.report_stop` nhận `stop_reason = rate_limited` và mã `RATE_LIMITED`;
> `T-RUN-25` đưa run về `running/enriching`, đóng collection segment, run kết thúc `outcome: partial`.
> `run.rate_limited_at` NOT NULL và `run.x_coverage_note_vi` **bắt buộc** nhắc mốc đó. `blocked` bị cấm tường
> minh cho tình huống này — nó biến một tình huống tự hết thành việc phải làm tay. Card
> `TC-collector-checkpoint-resume` §10 `SG-RATE` mang nguyên quy tắc này.
>
> Phân tích gốc, giữ lại làm bản ghi audit:
>
> - `contracts/ops/collector-probe.md` §4 `ST-4` bảo ghi `RATE_LIMITED`, và nếu kéo dài quá ngân sách thì
>   chuyển `blocked`.
> - Nhưng `contracts/ports.yaml` `worker.report_stop.error_codes` = `[VALIDATION_ERROR, UNAUTHORIZED,
>   STALE_LEASE, X_CHALLENGE_REQUIRED, X_ACCESS_BLOCKED, SOURCE_LAYOUT_CHANGED, IDEMPOTENCY_CONFLICT,
>   STORAGE_WRITE_FAILED]` — **không có `RATE_LIMITED`**.
> - `contracts/errors.yaml` `RATE_LIMITED.operations` = `[research.fetch_work_metadata, ai.run_inference_task,
>   telegram.send_payload]` — **không có operation nào của collector**, và chính file đó ghi
>   *"Chưa được ports.yaml 0.1.0 tham chiếu … Xem CR-PC03-04."*
> - `contracts/state/run.yaml` `stop_reason` không có giá trị nào cho rate limit; `RATE_LIMITED.target_states`
>   đẩy run về `stop_reason = source_blocked`, trong khi `errors.yaml` định nghĩa `source_blocked` là
>   *"X không cho vào"* — rate limit thì X **có** cho vào.
>
> **Agent phải đoán.** Ba lựa chọn khả dĩ (báo `X_ACCESS_BLOCKED`; im lặng backoff rồi tiếp; thêm `stop_reason`
> mới) cho ba hành vi khác nhau ở UI và ở AC-15. Không được tự chọn.
> **Ảnh hưởng khi đó:** chặn nhánh rate-limit của `TC-collector-checkpoint-resume`.
> **Cách đóng:** phương án thứ ba, cộng một luật mới — rate limit là `partial`, không phải `blocked`.

### A.3 Kết luận card collector

**Làm được, không còn chỗ nào phải đoán.** Với `X_CHALLENGE_REQUIRED`, `X_ACCESS_BLOCKED`,
`SOURCE_LAYOUT_CHANGED`, `RATE_LIMITED`, `limit_reached`, mất ACK, cursor mất hiệu lực và lease hết hạn, agent
có đủ ID operation, đủ schema, đủ transition và đủ oracle đếm được. Nhánh rate limit — chỗ duy nhất từng phải
đoán — nay có `T-RUN-25` và `SC50` (`acceptance/fixtures/e2e/a-happy-path-schedule-to-delivered.json`) cho
đường thành công đầu-cuối.

---

## B. Card delivery — `TC-telegram-unknown-delivery`

### B.1 Các bước đi được, không phải đoán

| # | Câu hỏi của agent | Trả lời được từ đâu | Kết luận |
| --- | --- | --- | --- |
| 1 | Vòng đời delivery có những trạng thái nào? | `contracts/state/delivery.yaml`: `pending | sending | sent | retry_wait | unknown | failed | cancelled`, 10 transition `T-DL-00`…`T-DL-09` | **Đủ** |
| 2 | Ghi attempt trước hay sau khi gọi mạng? | `contracts/telegram/delivery.md` §4.1 "Ghi attempt trước network call"; `T-DL-01` | **Đủ, và kiểm được bằng thứ tự trace** |
| 3 | Timeout thì về trạng thái nào? | `TELEGRAM_SEND_UNCERTAIN` → `delivery.unknown`; `unknown` là quasi-terminal, **không** retry tự động (B03/AMD-B03/ADR-0003) | **Đủ** |
| 4 | Ai được đưa `unknown` đi tiếp? | Chỉ `delivery.decide_unknown` (`auth_scope: owner_session`); `delivery.md` §5.2 | **Đủ** |
| 5 | Digest nhiều phần thì receipt thế nào? | `delivery.yaml` `delivery_part_semantics` `DP-01`…`DP-05`; part `unknown` **không** được gửi lại vì aggregate chưa `sent` | **Đủ** |
| 6 | Retry budget là bao nhiêu? | `retry-policy.yaml`: `telegram_send_attempts`, `telegram_send_backoff`, `telegram_send_max_window`, `telegram_attempt_before_send`, `delivery_sender_lease_ttl`, `delivery_alert_per_run` | **Đủ** |
| 7 | Unlink / relink giữa chừng thì sao? | `T-DL-08/09` → `cancelled`; fixture `d` và `e`; link generation trong `ENT-telegram-link` | **Đủ** |
| 8 | Sau restore thì được gửi không? | `RESTORE_UNVERIFIED` → dispatcher khóa; I15; fixture `a-restore-old-outbox-nothing-sent.json` | **Đủ** |
| 9 | Telegram chết thì report có sao không? | I09 + `TELEGRAM_PERMANENT_FAILURE.data_kept_vi`; fixture `c-permanent-failure-report-intact.json` | **Đủ** |
| 10 | Tag đổi sau publish trước khi gửi? | B01/AMD-B01 + fixture `c-tag-changed-after-publish-before-send.json`: payload là bản đã publish | **Đủ** |

### B.2 Gap tìm được

> **GAP-B1 → `CR-PC07-04` (đã mở từ PC07; PC10 xác nhận nó chặn card này).** *Digest dài hơn một tin thì cắt ở đâu?*
>
> `contracts/telegram/delivery.md` §3.5 yêu cầu tách `delivery_part` **ở ranh giới mục**, "khối hướng đang nổi
> nằm trọn trong part 0", "một mục vượt giới hạn một tin ⇒ cắt phần summary và thêm deep link". Cả ba luật đó
> đều cần **giới hạn độ dài một tin**. §3.4 khai thẳng: độ dài tối đa một tin `KC`, parse mode `KC`, bảng escape
> `KC`, số nút mỗi hàng `KC`, rate limit gửi `KC`, và *"Cấm suy ra giới hạn từ trí nhớ."*
>
> **Agent không thể hiện thực §3.5 mà không đoán một con số.** Đây là stop tuyệt đối, không phải cảnh báo.
> **Ảnh hưởng:** chặn toàn bộ nhánh multipart của `TC-telegram-unknown-delivery`, tức chặn fixture
> `a-multipart-part2-unknown-no-resend.json` và một phần AC-14. Phần `unknown` một-tin vẫn làm được.

> **GAP-B2 → `CR-PC10-03` — ĐÃ ĐÓNG ở FIX5/FIX6.** *`telegram.send_payload` trả `CAPABILITY_DENIED` — capability nào bị từ chối?*
>
> **Kết luận hiện tại:** `contracts/capabilities.yaml` có actor mới `ACT-delivery-dispatcher` với
> `allowed_operations: [delivery.dispatch_next, delivery.record_receipt, delivery.mark_unknown,
> telegram.send_payload]` và `network_scope: [telegram_bot_api]`. `CAPABILITY_DENIED` trên
> `telegram.send_payload` nay bảo vệ đúng một capability: mở kết nối ra host class Telegram. Dispatcher
> **không** giữ bot token — nó gọi adapter, adapter giữ token. Oracle của I11 vì vậy đối chiếu được.
>
> Phân tích gốc, giữ lại làm bản ghi audit:
>
> - `contracts/ports.yaml` khai `telegram.send_payload.error_codes` có `CAPABILITY_DENIED`.
> - Nhưng `contracts/capabilities.yaml` **không actor nào** có `telegram.send_payload` hay
>   `delivery.dispatch_next` trong `allowed_operations`. `ACT-telegram-ingress` chỉ có `telegram.receive_update`;
>   `ACT-telegram-linked-chat` chỉ có `save.create, run.run_now, run.list`.
> - `ACT-server-domain-service` **có** `MOD-telegram-adapter` và `MOD-delivery-service` trong `module_refs`,
>   nhưng khai `network_scope: []` — trong khi việc gửi digest bắt buộc phải chạm `telegram_bot_api`.
>
> **Agent phải đoán** danh tính capability của luồng gửi ra và đoán `network_scope` nào cho phép nó. Điều này
> quan trọng vì I11 (nội dung nguồn không đổi được recipient) chỉ kiểm được khi có một bản ghi capability để
> đối chiếu.
> **Ảnh hưởng khi đó:** chặn oracle của `CAPABILITY_DENIED` trên card delivery.

### B.3 Kết luận card delivery

**Vòng đời trạng thái đủ tốt; phần rendering thì vẫn không.** Mọi câu hỏi về trạng thái, commit point,
receipt, lease, capability và điều cấm đều trả lời được bằng file đã pin. Còn đúng **một** chỗ phải đoán:
giới hạn định dạng của Telegram (GAP-B1). Nó nằm ở ranh giới ra ngoài hệ thống và không sửa được bằng cách
viết thêm hợp đồng.

---

## C. Gap chung cho mọi card

> **GAP-C1 → `CR-PC10-04` — ĐÃ ĐÓNG.** Cả sáu file của PC09 nay tồn tại: `acceptance/scenarios.yaml`
> (SC01–SC53, mọi SC có ít nhất một fixture), `acceptance/traceability.csv`, `precode/gates.yaml`
> (G0–G7, SP1, `INV-01`…`INV-10`), `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`.
> §8 của card nay trỏ tới scenario đã viết, không còn chỉ là anchor. Chúng **cố ý không được pin hash** vì
> PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id.

> **GAP-C2 → `CR-PC10-01` — ĐÃ ĐÓNG.** 18 card đã được pin lại; epoch hiện hành là
> **`PC10-PIN-FCW4f-20260907`** (các epoch cũ hơn `PC10-PIN-FCW4e-20260907`, `PC10-PIN-FCW4d-20260907`, `PC10-PIN-FCW4c-20260907`, `PC10-PIN-FCW4b-20260907`, `PC10-PIN-FCW4-20260907`,
> `PC10-PIN-20260907` đã bị thay). Mỗi wave FIX chạm file có pin đều kéo theo một lần pin lại toàn bộ.
> EV-PC10-01 chạy lại sau mỗi lần: 0 sai lệch hash.

---

## D. Trả lời câu hỏi của SRC-PLAN §11 PC10

> *"Walkthrough một card collector và một card delivery: agent chỉ đọc card + references có đủ làm việc mà
> không đoán giao tiếp/state không?"*

**Về giao tiếp và state: có.** Cả hai card cho agent biết chính xác operation ID nào được gọi, bằng token nào,
qua cạnh nào, ghi hàng nào, ở transition nào, và commit ở đâu. Không có chỗ nào agent phải suy ra một endpoint,
một enum trạng thái hay một điểm commit.

**Về ranh giới ra thế giới ngoài: gần đủ, còn một chỗ.** Sau FIX5, gap duy nhất còn lại là giới hạn định dạng
của Telegram (GAP-B1, `CR-PC07-04`). Đó là hệ quả trực tiếp của REQ-A6 / SRC-SPEC §13.2 và **không sửa được
bằng cách viết thêm hợp đồng** — phải có người đọc
<https://core.telegram.org/bots/api#sendmessage> và ghi lại. `contracts/telegram/delivery.md` §3.4 vẫn ghi
"Cấm suy ra giới hạn từ trí nhớ".

**Kết luận cho G5.** Card collector nay đủ điều kiện về mặt nội dung. Card delivery đủ trừ nhánh multipart:
`CR-PC07-04` còn chặn, và nó cần một bước có mạng chứ không cần thêm hợp đồng. Một quan sát chung: cả ba gap
đã đóng đều được đóng bằng cách **sửa hợp đồng**, không phải bằng cách nới lỏng card — đó là dấu hiệu
walkthrough làm đúng việc của nó.
