---
contract_id: CT-data-invariants
version: 0.1.0
status: accepted
ratification_ref: OD-20260907-01
owner_role: data contract owner
source_refs:
  - "SRC-PLAN §7 (bảng invariant I01–I15)"
  - "SRC-PLAN §9.1, §9.3"
  - "SRC-PLAN §10 (ma trận lỗi và bằng chứng)"
  - "SRC-PLAN §11 PC02 ('Đạt khi: I02/I03/I04/I08 có oracle theo số hàng/hash/reference')"
  - "SRC-SPEC §7.3, §9.2, §9.3"
  - "SRC-SPEC §12 AC-04, AC-06, AC-07, AC-09, AC-12, AC-13"
requirement_refs: [REQ-D17, REQ-D25, REQ-D26, REQ-D38, REQ-D55, REQ-D58, REQ-AC04, REQ-AC06, REQ-AC07, REQ-AC12, REQ-AC13]
decision_refs: [B05, B06, B07, B15, AMD-B05]
invariant_refs: [I02, I03, I04, I08, I15, I16, I17]
producers: [MOD-ingest-service, MOD-identity-service, MOD-analysis-service, MOD-saved-service, MOD-report-service]
consumers: [MOD-backend-api, MOD-web-ui, MOD-report-service, MOD-analysis-worker, MOD-x-collector, MOD-telegram-adapter, MOD-delivery-service, MOD-backup-service]
dependencies:
  - contracts/data/entities.yaml
  - contracts/data/identity.md
  - acceptance/fixtures/identity/
scope: >-
  Phần **dữ liệu** của các invariant phải khóa trước khi coding: I02 (ingest/checkpoint),
  I03 (canonical identity), I04 (analysis theo generation — phần khóa dữ liệu), I08 (Saved
  snapshot), phần dữ liệu của I15 (restore), cùng hai invariant mới I16 và I17. Mỗi mục có:
  phát biểu, hợp đồng sở hữu, một positive scenario, ít nhất một counterexample **phải fail**,
  oracle đo được (số hàng/hash/tham chiếu) và loại bằng chứng.
verification: >-
  E0 (đã chạy trong gói này): fixture parse + target schema validation + kiểm tham chiếu
  entity. E1 (contract test bằng fixture), E2 (fault injection), E3/E4: NOT_RUN.
claim_ceiling: CONTRACT_READY
---

# Invariant dữ liệu

## 0. Cách đọc

Một invariant chỉ có giá trị khi nó **có thể fail quan sát được**. Vì vậy mỗi mục bên dưới có
một counterexample: một chuỗi thao tác mà nếu triển khai cho phép, invariant bị vi phạm và
gate tương ứng phải FAIL. Nếu một counterexample không thể diễn đạt được bằng oracle đo được
thì invariant đó chưa được khóa.

Nhãn bằng chứng theo SRC-PLAN §14.2: `E0` lint tĩnh, `E1` contract test bằng fixture, `E2`
integration + fault injection, `E3` live probe, `E4` review nội dung. Ở gói PC02 chỉ E0 được
chạy; mọi mục E1/E2 ghi `NOT_RUN`.

Ký hiệu: `#<tên bảng>` = số hàng của bảng đó; `#<tên bảng>[điều kiện]` = số hàng thỏa điều kiện.

---

## I02 — Receipt ingest chỉ ACK sau commit; checkpoint không đi trước dữ liệu bền

**Phát biểu.** Với mọi batch ingest: (a) không có ACK nào rời server trước khi transaction
COMMIT thành công; (b) không tồn tại thời điểm quan sát được trong đó `checkpoint` tiến
(`acked_through_ingest_sequence` tăng) mà các hàng `post` tương ứng chưa bền; (c) replay cùng
`idempotency_key` với cùng `payload_hash` trả lại đúng receipt cũ và không đổi bất kỳ số đếm
nào.

**Owner/hợp đồng.** `contracts/data/entities.yaml` → `transactions[TXN-ingest-batch]` và
`transactions[TXN-checkpoint-only]`; entity `ingest_receipt`, `checkpoint`, `post`. Chủ sở hữu
bảng `checkpoint` là **`MOD-ingest-service`**, duy nhất (ruling R-01). Nguồn: SRC-PLAN §7 I02, §9.1, §10
`INGEST_ACK_LOST`; SRC-SPEC §9.2.

**Positive scenario.** Collector gửi batch 10 item (3 trùng `x_post_id`). Server chạy một
transaction: chèn 7 post, cấp `ingest_sequence` 101..107, chèn 1 checkpoint với
`acked_through_ingest_sequence = 107`, chèn 1 receipt trỏ checkpoint đó. COMMIT xong mới trả
200 kèm receipt. Fixture: `f-ingest-replay-idempotent.json`.

**Counterexample (phải FAIL).**

1. *ACK sớm.* Triển khai gửi 200 ngay sau khi ghi xong post nhưng trước COMMIT; tiến trình
   chết trước COMMIT. Collector coi như đã ACK và tiến cursor. Kết quả: server có 0 post,
   client tin là 7. → Gate FAIL.
2. *Checkpoint đi trước dữ liệu bền.* Ghi một hàng `checkpoint` tham chiếu hoặc tiến qua
   `ingest_sequence` của các post **chưa commit**, hoặc ghi checkpoint ở một transaction
   riêng **trước** transaction chứa các post đó. Crash giữa hai transaction để lại một con trỏ
   ACK trỏ vào dữ liệu không tồn tại; collector tiếp tục từ con trỏ đó và bỏ sót vĩnh viễn
   khoảng dữ liệu ở giữa. → Gate FAIL.

   **Cái này KHÔNG bị cấm:** `ingest.commit_checkpoint` — một transaction riêng **không có
   item nào**, chỉ tiến con trỏ vị trí trong khi `acked_through_ingest_sequence` GIỮ NGUYÊN
   (trang rỗng, hết feed, đóng segment). Đó là `TXN-checkpoint-only` trong
   `entities.yaml`, hợp lệ theo ruling R-01, và bị chặn bởi guard "con trỏ đề xuất chỉ được
   tham chiếu `ingest_sequence` đã commit". Ranh giới giữa hai điều này là: **một checkpoint
   không bao giờ được trỏ vượt qua post đã bền**, chứ không phải "checkpoint không bao giờ
   được nằm ở transaction riêng".
3. *Replay tạo hàng mới.* Gửi lại cùng `idempotency_key` sau khi ACK mất; triển khai chèn
   thêm checkpoint hoặc tăng `posts_inserted`. → Gate FAIL.

**Oracle.**

| Đo | Trước replay | Sau replay | Quan hệ bắt buộc |
| --- | --- | --- | --- |
| `#post[owner]` | `P` | `P` | bằng nhau |
| `#ingest_receipt[idempotency_key = K]` | 1 | 1 | luôn = 1 |
| `#checkpoint[run_id = R]` | `C` | `C` | bằng nhau |
| `ingest_receipt.receipt_hash` | `H` | `H` | bằng nhau |
| `ingest_receipt.posts_inserted` | `n` | `n` | bằng nhau |
| `MAX(post.ingest_sequence)` | `s` | `s` | bằng nhau |

Bổ sung: với mọi receipt, `posts_inserted + posts_duplicate + items_rejected = items_received`
và tồn tại `checkpoint` có `checkpoint.id` bằng `ingest_receipt.checkpoint_id`, với `checkpoint.created_at` bằng `ingest_receipt.committed_at`.
Và: không tồn tại `post` có `ingest_sequence <= checkpoint.acked_through_ingest_sequence` mà
`ingest_receipt_id` trỏ tới receipt chưa commit (bất khả thi theo cấu trúc FK — đó là điểm).

**Oracle bao trùm cả hai đường ghi checkpoint** (ruling R-01, finding F-A1R1-01). Sau BẤT KỲ
chuỗi xen kẽ nào của `ingest.submit_batch` và `ingest.commit_checkpoint`:

| Đo | Ràng buộc |
| --- | --- |
| `checkpoint.acked_through_ingest_sequence` | `<= MAX(ingest_receipt.max_ingest_sequence)` trên tập receipt ĐÃ COMMIT |
| `checkpoint.acked_through_ingest_sequence` | `<= MAX(post.ingest_sequence)` |
| Delta `#post` qua một lời gọi `ingest.commit_checkpoint` | `= 0` |
| Delta `acked_through_ingest_sequence` qua một lời gọi `ingest.commit_checkpoint` | `= 0` |
| Với mọi receipt có `receipt_kind = 'checkpoint_only'` | mọi count `= 0` |
| Tập `(id, sequence, acked_through_ingest_sequence)` của `checkpoint` | chỉ được thêm phần tử, không phần tử nào đổi giá trị (append-only) |

Đây là oracle mà finding F-A1R1-01 yêu cầu: nó nói checkpoint **không bao giờ trỏ vượt qua
post đã bền**, thay vì cấm mọi transaction checkpoint riêng lẻ.

**Bằng chứng.** E1 bằng fixture (f) — `NOT_RUN`. E2: crash injection sau COMMIT trước ACK —
`NOT_RUN`. E0 (đã chạy ở PC02): fixture parse và tham chiếu entity hợp lệ.

**Giới hạn đã biết.** I02 nói về phía server. Phía client, timeout là **không biết kết quả**,
không phải rollback (SRC-PLAN §5.1). Cam kết của AMD-B05 là **không ingest trùng** theo
`x_post_id`, không phải "không bao giờ đọc lại": cursor của X có thể mất hiệu lực và recovery
policy cho phép đọc lại.

---

## I03 — Một canonical identity đã xác định chỉ có một work; alias conflict không bị merge đoán

**Phát biểu.** (a) Với mọi `(id_scheme, id_value_normalized)` trong một owner, tồn tại tối đa
một hàng `identity_alias`, do đó tối đa một work. (b) Mọi work `active` có `canonical_doi`
không NULL là duy nhất theo DOI đó; tương tự `canonical_arxiv_id`. (c) Hai work chỉ được hợp
nhất khi có `linking_evidence` cụ thể không đến từ AI; mọi trường hợp mâu thuẫn tạo
`identity_conflict` và **không** merge. (d) Sau merge, không tồn tại alias trỏ tới work
`merged`, và chuỗi `merged_into_work_id` có độ sâu đúng 1.

**Owner/hợp đồng.** `contracts/data/identity.md` §2–§6; `entities.yaml`
`transactions[TXN-identity-merge]`; entity `work`, `identity_alias`, `identity_conflict`,
`identity_merge_audit`. Nguồn: SRC-PLAN §7 I03, §3 B06/B15, §9.1.

**Positive scenario.** Work W1 có `canonical_arxiv_id = 2501.01234` (08:00), work W2 có
`canonical_doi = 10.1000/xyz` (09:00). 10:00 OpenAlex trả bản ghi nối hai định danh đó.
Merge chạy: winner = W2 (`only_candidate_with_canonical_doi`), W1 → `merged`, alias của W1
trỏ W2, W2 nhận `canonical_arxiv_id`, `first_discovered_at` = MIN = 08:00. Fixture:
`a-merge-doi-arxiv.json`.

**Counterexample (phải FAIL).**

1. *Merge đoán.* Hai work có tiêu đề giống 95% và cùng tác giả; triển khai merge chúng.
   Không có hàng `identity_alias` chung và `linking_evidence` rỗng. → FAIL (B15).
2. *Merge khi canonical mâu thuẫn.* W1 `canonical_doi = 10.1000/aaa`, W2
   `canonical_doi = 10.1000/bbb`, một nguồn nói cả hai cùng arXiv ID. Triển khai chọn một DOI
   và bỏ cái kia. → FAIL: phải tạo `identity_conflict` `canonical_value_mismatch`. Fixture:
   `c-identity-conflict.json`.
3. *Hai work cho v1 và v2.* `arXiv:2501.01234v1` và `…v2` tạo hai hàng `work`. → FAIL:
   canonical là **base**, phiên bản ở `work_version`. Fixture: `g-arxiv-version-v1-v2.json`.
4. *Năm post thành năm mục.* 5 post + thread tác giả cùng dẫn `arXiv:2501.01234` tạo 5 work
   hoặc 5 mục báo cáo. → FAIL (REQ-AC07). Fixture: `h-five-posts-thread-one-target.json`.
5. *Xóa nguồn khi merge.* Merge xóa hàng work thua hoặc alias của nó. → FAIL: B15 yêu cầu
   giữ nguồn.

**Oracle.**

| Đo | Ràng buộc |
| --- | --- |
| `#identity_alias[owner, scheme, value]` | `<= 1` với mọi bộ ba |
| `#work[owner, identity_state='active', canonical_doi = D]` | `<= 1` với mọi `D` không NULL |
| `#work[owner, identity_state='active', canonical_arxiv_id = A]` | `<= 1` với mọi `A` không NULL |
| `#identity_alias[work_id ∈ work[identity_state='merged']]` | `= 0` sau khi merge commit |
| `#work[merged_into_work_id ∈ work[identity_state='merged']]` | `= 0` (path compression, độ sâu 1) |
| `#identity_merge_audit[loser_work_id = L]` | `<= 1` với mọi `L` |
| `identity_merge_audit.linking_evidence` | NOT NULL, và `performed_by ≠ 'ai_*'` (không tồn tại enum như vậy) |
| Với mọi merge | `#work` không đổi (không xóa, không tạo work); `#identity_alias` không đổi |
| Fixture (h) | `#work[canonical_arxiv_id='2501.01234'] = 1`; `#post_work[work_id=W] = 6`; `#report_item[report=R] = 1` |
| Fixture (c) | `#identity_merge_audit` không tăng; `#identity_conflict[state='open'] = 1`; cả hai work `identity_state='quarantined'` |

**Bằng chứng.** E1 bằng fixture (a), (c), (g), (h) — `NOT_RUN`. E0 đã chạy: mọi target object
trong các fixture đó validate theo `target.schema.json`.

**Giới hạn đã biết.** "0 trùng" chỉ đúng trên phạm vi canonical identity **đã biết**. Hai
công trình cùng nội dung mà không nguồn nào nối định danh sẽ tồn tại như hai work; đó không
phải vi phạm I03 mà là giới hạn đã công bố (B15, SRC-PLAN §7 ghi chú).

---

## I04 — Analysis hợp lệ bất biến theo generation; đổi tag không gọi lại AI; retry không tạo hai kết quả cùng key

**Phát biểu.** (a) Với mỗi analysis key `(owner, target_key, task_type, source_fingerprint,
prompt_version, schema_version, generation_number)` tồn tại tối đa một hàng `analysis` có
`status = 'valid'`. (b) Hàng `valid` bất biến: `payload` và `payload_hash` không đổi sau
commit. (c) Tag **không** thuộc analysis key, nên bỏ tag rồi thêm lại không sinh
`analysis_generation`, không sinh `analysis_attempt`, không gọi provider. (d) Phân tích lại
tạo generation mới và **giữ** bản cũ.

**Owner/hợp đồng.** Phần dữ liệu ở đây; ngữ nghĩa task/prompt/provider thuộc PC06
(`contracts/ai/tasks.yaml`). Entity `analysis`, `analysis_generation`, `analysis_attempt`;
`transactions[TXN-analysis-accept]`. Nguồn: SRC-PLAN §7 I04, §3 B07, §9.3; SRC-SPEC §3.5
D25/D26, §12 AC-06.

**Positive scenario.** Work W được summary lúc 08:00 (generation 1, valid). 19:00 owner bỏ
tag T. Tuần sau thêm lại T. Báo cáo kỳ sau chọn W và **dùng lại** hàng `analysis` cũ. Fixture
liên quan: `g-arxiv-version-v1-v2.json` (nhánh generation mới khi có v2).

**Counterexample (phải FAIL).**

1. *Tag trong key.* Triển khai đưa `tag_config_version_id` vào analysis key. Bỏ/thêm tag làm
   key đổi → sinh generation mới → gọi AI lại. → FAIL (REQ-AC06, REQ-D25).
2. *Retry tạo hai valid.* Worker submit hai lần do mất ACK; triển khai chèn hai hàng vì không
   có UNIQUE partial. → FAIL.
3. *Attempt lỗi thành kết quả.* Output sai schema được lưu vào `analysis` với ghi chú "một
   phần". → FAIL (SRC-PLAN §10 `AI_OUTPUT_INVALID`), và cũng vi phạm I16.
4. *Ghi đè bản cũ khi phân tích lại.* Reanalysis UPDATE hàng cũ thay vì tạo generation mới.
   → FAIL (REQ-D26 "giữ bản cũ").
5. *Usage unknown ghi 0.* Đường CLI không có token count nhưng ghi `usage_tokens_in = 0`.
   → FAIL (REQ-D44, I14).

**Oracle.**

| Đo | Ràng buộc |
| --- | --- |
| `#analysis[status='valid', key = K]` | `= 1` với mọi key đã hoàn tất; không bao giờ `>= 2` |
| Trước/sau chu kỳ bỏ-tag → thêm-lại-tag | `#analysis_generation` không đổi; `#analysis_attempt` không đổi; provider call counter delta `= 0` |
| Sau reanalysis | `#analysis_generation[target, task]` tăng đúng 1; hàng generation cũ vẫn tồn tại và `payload_hash` của nó không đổi |
| Với mọi hàng `analysis` valid | `accepted_from_attempt_id` NOT NULL và attempt đó có `outcome = 'accepted'` |
| Với mọi hàng `analysis` | `sha256(JCS(payload)) = payload_hash` |
| `analysis.usage_tokens_in/out` | NULL khi không biết; **không** tồn tại hàng đường CLI ghi 0 mà attempt không có token count thật |

**Bằng chứng.** E1 (fixture cache-reuse của PC06), E2 (crash sau provider completion) —
`NOT_RUN`. Provider call counter là oracle của PC06; PC02 chỉ khóa cấu trúc khóa.

**Giới hạn đã biết.** Hệ thống KHÔNG hứa inference bên ngoài chạy đúng một lần: worker chết
sau khi model đã chạy vẫn phát sinh phí (SRC-PLAN §8.2). Cái được bảo đảm là không có **hai
kết quả đã commit** cùng key.

---

## I08 — Save là snapshot bất biến; cùng target tối đa một Saved active; bỏ tag không xóa snapshot

**Phát biểu.** (a) Mọi `saved_item` có `saved_snapshot_id` NOT NULL. (b) Với mọi
`(owner, target_key)` tồn tại tối đa một `saved_item` có `state = 'active'`. (c)
`saved_snapshot.payload` và `content_hash` bất biến sau commit — không đổi khi bỏ lưu, khi bỏ
tag, khi post gốc bị xóa trên X, khi khởi động lại hệ thống, khi merge identity. (d) Snapshot
chụp từ **bản analysis đang được đọc**, không phải bản mới nhất.

**Owner/hợp đồng.** `entities.yaml` entity `saved_item`, `saved_snapshot`;
`transactions[TXN-save-target]`. Hình dạng `payload` thuộc PC07
(`contracts/schemas/saved-snapshot.schema.json`, CR-PC02-03). Nguồn: SRC-PLAN §7 I08;
SRC-SPEC §3.6 D38/D55, §7.3, §12 AC-12/AC-13.

**Positive scenario.** Người dùng mở Report detail và bấm Save; cùng lúc bấm nút Save trên
Telegram cho đúng mục đó. Một transaction thắng; transaction kia rollback (kể cả snapshot vừa
tạo) và trả `already_saved: true`. Kết quả: 1 `saved_item` active, 1 `saved_snapshot`. Bot
vẫn phản hồi trạng thái cho cả 5 lần bấm. Fixture: `d-concurrent-save-app-telegram.json`.

**Counterexample (phải FAIL).**

1. *UNIQUE trên hai cột nullable.* Dùng `UNIQUE(owner_id, target_work_id, target_post_id)`.
   Với post-only target, `target_work_id` là NULL ở cả hai hàng và SQL coi NULL ≠ NULL → hai
   hàng Saved cùng post cùng tồn tại. → FAIL. Đây chính xác là lý do khóa union
   `target_key` tồn tại (SRC-PLAN §9.1: "không dựa vào hai cột nullable với một UNIQUE mơ hồ").
2. *Check-then-insert.* Đọc trước rồi chèn, không dựa vào UNIQUE. Hai request đồng thời cùng
   đọc "chưa có" rồi cùng chèn. → FAIL.
3. *Snapshot mồ côi.* Transaction thua để lại `saved_snapshot` đã chèn. → FAIL: oracle đếm
   snapshot sẽ ra 2.
4. *Bỏ lưu xóa snapshot.* Unsave thực hiện DELETE. → FAIL (SRC-SPEC §7.3: ba thao tác riêng).
5. *Snapshot rỗng khi nguồn bị xóa.* Post bị xóa trên X và UI hiển thị Saved trống. → FAIL
   (REQ-AC12). Fixture: `e-source-deleted-snapshot-intact.json`.
6. *Snapshot lấy bản analysis mới hơn.* Giữa lúc đọc và lúc bấm Save có analysis generation
   mới; snapshot chụp bản mới. → FAIL (PC07 rule, `analysis_id_at_save` phải bằng
   `report_item.analysis_id` của mục đang đọc).

**Oracle.**

| Đo | Ràng buộc |
| --- | --- |
| `#saved_item[owner, target_key = T, state='active']` | `<= 1` với mọi `T` |
| `#saved_item[saved_snapshot_id IS NULL]` | `= 0` |
| Sau hai request Save đồng thời | `#saved_item[T, active] = 1` **và** `#saved_snapshot[target_key_at_save = T] = 1` |
| Sau 5 lần bấm Save Telegram cùng `idempotency_key` | `#saved_item[T] = 1`, số phản hồi bot `= 5` |
| Sau unsave | `#saved_snapshot` không đổi; `saved_item.state = 'unsaved'`; hàng vẫn tồn tại |
| Sau restart hệ thống | `saved_snapshot.content_hash` bằng giá trị trước restart |
| Sau khi post gốc bị xóa | `saved_snapshot.content_hash` không đổi; `post.source_deleted_observed_at` NOT NULL; `#post` không đổi |
| Với mọi snapshot, mọi thời điểm | `sha256(JCS(payload)) = content_hash` |
| `saved_snapshot.analysis_id_at_save` | bằng `report_item.analysis_id` của mục đã đọc khi `source_report_item_id` NOT NULL |

**Bằng chứng.** E1 bằng fixture (d), (e) — `NOT_RUN`. E2: restart + concurrent save —
`NOT_RUN`. E0 đã chạy: fixture parse, target validate.

---

## I15 (phần dữ liệu) — Restore không tự phát lại outbox cũ hoặc reset first_announced

**Phát biểu (giới hạn ở phần PC02 sở hữu).** Sau restore: (a) `outbox_intent` có
`restore_generation` nhỏ hơn generation hiện hành **không** được dispatch tự động; (b) không
thao tác restore nào được UPDATE `saved_snapshot`, `ingest_receipt`, `identity_merge_audit`
hay `report_item` đã publish; (c) mọi `assignment_lease` đang `held` trước restore phải được
chuyển `revoked` trước khi cho phép claim mới.

**Owner/hợp đồng.** PC08 sở hữu runbook backup/restore
(`contracts/ops/backup-restore.md`); PC02 sở hữu cột `outbox_intent.restore_generation` và
tính bất biến của các bảng lịch sử. Nguồn: SRC-PLAN §7 I15, §10 `RESTORE_UNVERIFIED`, §3.1
(SQLite WAL).

**Positive scenario.** Restore từ snapshot nhất quán; `restore_generation` tăng; dispatcher
bị khóa cho tới khi reconciliation xong; Saved đếm và hash khớp manifest.

**Counterexample (phải FAIL).** Restore xong, dispatcher tự chạy và gửi lại digest của kỳ đã
gửi trước khi backup. → FAIL. Hoặc: restore ghi đè `content_hash` của snapshot bằng giá trị
tính lại theo canonical rule mới. → FAIL (đổi quy tắc hash là amendment, không phải bước
restore).

**Oracle.** `#saved_snapshot` và tập `content_hash` sau restore bằng manifest của backup;
`#outbox_intent[dispatch_state='ready' AND restore_generation < current]` = 0 được dispatch;
`#assignment_lease[state='held']` = 0 tại thời điểm mở khóa dispatcher.

**Bằng chứng.** E2 restore drill — `NOT_RUN` (PC08). Chuyển tiếp là **CR-PC02-07** tới PC08.

---

## I16 (mới) — Attempt không bao giờ là kết quả

**Justification.** SRC-PLAN §3 B07 yêu cầu "attempt lỗi không tính là kết quả hoàn thành" và
§8.2 yêu cầu "không ghi output sai schema thành valid". Yêu cầu này **cắt ngang** I04: I04 nói
về tính duy nhất theo key của kết quả, không nói gì về việc một attempt có thể bị đọc nhầm
thành kết quả. Vì PC02 tạo hai bảng riêng (`analysis`, `analysis_attempt`), cần một invariant
phát biểu ranh giới giữa chúng, có oracle riêng. Do đó I16, không phải một dòng phụ của I04.

**Phát biểu.** Không có đường đọc nào biến một hàng `analysis_attempt` thành kết quả phân
tích: mọi truy vấn "kết quả của target X" chỉ đọc `analysis` với `status = 'valid'`. Attempt
là append-only; `outcome` chỉ được ghi một lần từ trạng thái đang chạy sang trạng thái cuối.

**Owner/hợp đồng.** `entities.yaml` entity `analysis_attempt`;
`transactions[TXN-analysis-accept]`.

**Counterexample (phải FAIL).** UI hoặc report builder đọc attempt cuối cùng để hiển thị
summary khi chưa có hàng `valid`. → FAIL: mục đó phải hiện là thiếu summary và vào
`pending_item_ledger`, report `quality = 'partial'` (B17).

**Oracle.** Với mọi target không có hàng `analysis` valid: view "summary của target" trả
rỗng, và `#pending_item_ledger[target_key = T, state='pending'] = 1`. Với mọi hàng `analysis`
valid: tồn tại đúng một attempt `accepted` được trỏ bởi `accepted_from_attempt_id`.
`#analysis_attempt[outcome='timeout_unknown' AND cost_uncertain = false] = 0`.

**Bằng chứng.** E1 — `NOT_RUN`.

---

## I17 (mới) — Merge identity không làm đổi bất kỳ snapshot lịch sử nào

**Justification.** SRC-PLAN §11 PC02 yêu cầu tường minh "cách không làm đổi historical
snapshot sau merge". I03 chỉ nói về tính đúng của identity; I08 chỉ nói về Saved. Không
invariant nào trong SRC-PLAN §7 phát biểu ràng buộc **chéo** giữa thao tác merge và các bảng
lịch sử khác (report đã publish, receipt, attempt). I17 lấp đúng khoảng trống đó và cho merge
một oracle đếm được.

**Phát biểu.** Một transaction merge chỉ được ghi các cột nằm trong merge move-set
(`entities.yaml` → `transactions[TXN-identity-merge].merge_move_set`). Cụ thể, sau merge:
`saved_snapshot` (mọi cột, kể cả `target_key_at_save`), `ingest_receipt`, `analysis_attempt`,
`identity_merge_audit` cũ, và `report_item` thuộc report `published` đều **byte-identical**
với trước merge.

**Owner/hợp đồng.** `entities.yaml` `transactions[TXN-identity-merge]`;
mục `referential_integrity` → `historical_snapshot_rule`; `identity.md` §6.4.

**Positive scenario.** Owner đã Save work W1 lúc 10:00 (snapshot S1). 11:00 W1 bị merge vào
W2. Con trỏ `saved_item.target_work_id` chuyển sang W2 và `moved_by_merge_id` được ghi; S1
không đổi một byte, `target_key_at_save` vẫn là `work:<W1>`. Fixture:
`a-merge-doi-arxiv.json`.

**Counterexample (phải FAIL).**

1. Merge chạy `UPDATE saved_snapshot SET target_key_at_save = 'work:W2'` để "cho nhất quán".
   → FAIL.
2. Merge tính lại `content_hash` của snapshot. → FAIL.
3. Merge ghi lại `report_item.target_key` của một kỳ đã publish để mục cũ trỏ work thắng.
   → FAIL (cũng vi phạm I05: không thay nội dung âm thầm sau publish).
4. Merge xóa `saved_item` của work thua thay vì chuyển `state = 'superseded_by_merge'`.
   → FAIL: mất lịch sử.

**Oracle.**

| Đo | Trước merge | Sau merge | Quan hệ |
| --- | --- | --- | --- |
| `#saved_snapshot` | `n` | `n` | bằng nhau |
| Tập `{(id, content_hash)}` của `saved_snapshot` | `Σ` | `Σ` | bằng nhau theo tập hợp |
| Tập `{(id, target_key)}` của `report_item` thuộc report `published` | `Ρ` | `Ρ` | bằng nhau |
| `#ingest_receipt`, tập `receipt_hash` | `R` | `R` | bằng nhau |
| `#work` | `w` | `w` | bằng nhau (merge không xóa work) |
| `#saved_item[state='active', target_key = winner]` | — | `<= 1` | UNIQUE partial |
| `identity_merge_audit.preserved_counts` | — | `{saved_snapshot: n, ingest_receipt: card(R), published_report_item: card(Ρ)}` | khớp số đo thực tế |
| `identity_merge_audit.moved_counts` | — | tổng khớp số hàng thực sự đổi | mọi bảng ngoài move-set có delta `= 0` |

**Bằng chứng.** E1 bằng fixture (a) — `NOT_RUN`. E0 đã chạy: fixture khai báo đủ
`forbidden_effects` và mục `expected` → `preserved`.

---

## Phụ lục A — Vì sao hai cột UNIQUE không đủ (B06), phát biểu tường minh

`work.canonical_doi` và `work.canonical_arxiv_id` cùng UNIQUE **không** giải được bài toán
trùng lặp, vì UNIQUE chỉ phát hiện xung đột khi hai hàng có **cùng giá trị ở cùng cột**.

Ba tình huống mà cả hai UNIQUE đều "hài lòng" trong khi dữ liệu vẫn trùng:

1. **Bổ sung nhau.** W1 chỉ có arXiv ID; W2 chỉ có DOI. Không cột nào trùng. → Cần
   `identity_alias` + merge.
2. **Cùng NULL.** Hai post-only work (nếu triển khai lỡ tạo work không định danh) có cả hai
   cột NULL; NULL ≠ NULL trong SQL nên UNIQUE không chặn. → Đây là lý do post không định danh
   **không** tạo work mà thành target `post` (identity.md §4).
3. **Chuẩn hóa khác nhau.** `10.1000/XYZ` và `10.1000/xyz` là hai giá trị khác nhau nếu không
   chuẩn hóa. → Đây là lý do chuẩn hóa (identity.md §2) là điều kiện tiên quyết của UNIQUE,
   không phải bước làm đẹp.

Kết luận hợp đồng: mọi tuyên bố "0 trùng" phải kèm phạm vi "trong canonical identity đã biết",
và mọi trường hợp nghi ngờ đi vào `identity_conflict` chứ không vào một heuristic merge.

## Phụ lục B — Bảng tổng hợp oracle

| Invariant | Loại oracle | Fixture | Bằng chứng cao nhất đã có |
| --- | --- | --- | --- |
| I02 | Số hàng + hash receipt + bất đẳng thức con trỏ ≤ post bền | `f-ingest-replay-idempotent.json`, `e-source-deleted-snapshot-intact.json` | E0 |
| I03 | Số hàng + tham chiếu + audit | `a`, `c`, `g`, `h` | E0 |
| I04 | Số hàng + counter gọi provider | (PC06 sở hữu fixture cache) | E0 (cấu trúc khóa) |
| I08 | Số hàng + hash snapshot | `d`, `e` | E0 |
| I15 (dữ liệu) | Số hàng + manifest hash | (PC08) | NOT_RUN |
| I16 | Số hàng + view rỗng | (PC06) | E0 (cấu trúc bảng) |
| I17 | Tập hash bất biến trước/sau | `a` | E0 |
