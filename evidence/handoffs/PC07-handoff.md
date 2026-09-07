# HANDOFF — PKT-PC07 (app, Save và Telegram delivery)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC07` · authority `AUTH-COORD-PC07` (parent `AUTH-OWNER-20260906-01`) |
| worker principal | `worker-W3` · lease `LEASE-PC07-e1` (exclusive, fencing 1) |
| expires_at | 2026-09-07T08:00Z · mode `DOCUMENTARY_DRAFT` · audit_route `INDEPENDENT_REQUIRED` |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| next actor | Coordinator · `lease_released_at` | 2026-09-06T18:38Z |

`DONE_WITH_CONCERNS` vì: mọi deliverable đã tạo và cả năm gate E0 PASS, nhưng gói này mở 6 CR,
để 4 giá trị PROVISIONAL cần Owner, giữ giới hạn định dạng Telegram ở `KC` (không có mạng để
đọc tài liệu), và lấy scenario ID `SC45`–`SC48` trong khi không kiểm được PC05/PC06 đã lấy số nào.

## 2. Changes

| Path | Op | Before | After sha256 | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/ui/screens.yaml` | CREATE | ABSENT | `b73fb711e745e4d266f8ef7bdda1570df1ed397834c0b8985184ff3a44a9068e` | 44515 |
| `contracts/telegram/commands.yaml` | CREATE | ABSENT | `60677804a81ca855e6fa82b59d0ddebbc2d4678e5997193a7e3ddf229f4886a7` | 23598 |
| `contracts/telegram/delivery.md` | CREATE | ABSENT | `22e58c0df8a947b4129dc1989aac5bfc35f328d6a738905f7cc2d4937a76311b` | 16793 |
| `contracts/schemas/saved-snapshot.schema.json` | CREATE | ABSENT | `1818c0d898d666ae4962a6d563a761e39f842cdbe425c47bf3884165710e2fc0` | 16204 |
| `acceptance/fixtures/telegram/README.md` | CREATE | ABSENT | `a004805838b293439422a177791e7941a7c220980d7495745a7ec45e8b7aaa57` | 8541 |
| `…/a-multipart-part2-unknown-no-resend.json` | CREATE | ABSENT | `58d443a62e181e6bae29f841ea66d62561d776cd5e7da3965145a4611d8aae9f` | 7125 |
| `…/b-response-lost-unknown-operator-decides.json` | CREATE | ABSENT | `68453337f1d130677a9d17e6c78fc38392ac2247ac84cbde6c23f4569010415e` | 5046 |
| `…/c-permanent-failure-report-intact.json` | CREATE | ABSENT | `85b9b1c0f0033e27a5db29dc2090237767ae105bcf7681e90268f64e44ff6e8b` | 4936 |
| `…/d-unlink-before-send-cancelled.json` | CREATE | ABSENT | `7f5bff111202d87cfcee5cd41ab1829bd8eb1fe786287a398c45a461f568f1a0` | 4252 |
| `…/e-relink-old-generation-cancelled.json` | CREATE | ABSENT | `822833235987d0fe0152c05032ae2cf143202096e5716db8de886af9d5d6f03c` | 4718 |
| `…/f-stale-callback-no-save.json` | CREATE | ABSENT | `0a8398e787a79c5b70783b1c9101cccc00de7fa031963f522521ff94136c656a` | 3888 |
| `…/g-link-code-used-twice.json` | CREATE | ABSENT | `206519e15bdac724e7ac361cfcc1121c4661404d77926ae29f285c39cf100177` | 3693 |
| `…/h-unknown-chat-status-silent.json` | CREATE | ABSENT | `d7701589e3c847e8616aeb757ba9c36b65bb5f8fd22e6d68e36b5aa8b51e5e60` | 3292 |
| `…/i-unknown-chat-valid-code-format.json` | CREATE | ABSENT | `a1970b37acf92ada3f8e01df02431ac58950aff212524d914fb4f730f5b82eca` | 5769 |
| `…/j-concurrent-save-app-telegram.json` | CREATE | ABSENT | `e73498303b5c273ad30a1713d5904ca0cb74842fc1bf3f88ecffc567b61577c1` | 8093 |
| `…/k-save-then-source-deleted.json` | CREATE | ABSENT | `6061eb31b53db8a610383f919dab4146e46946563e78218580731ebab77c683c` | 7343 |
| `…/l-run-now-while-needs-user.json` | CREATE | ABSENT | `bd07b3decfb85849d9bdb6d639f05702412e19b0d43df03bd4eb7f53c1f1a16b` | 4270 |
| `…/m-three-run-states-distinct-text.json` | CREATE | ABSENT | `1acfca0950dde4be2940d53f041e7999432abfebb9ec01d85409d9560cafcb1b` | 4589 |
| `…/neg-saved-snapshot-missing-content-hash.json` | CREATE | ABSENT | `254528d628f9f5e855650ea15045ba9f8af8d28e48ee96b048399945d6f813de` | 3491 |
| `…/neg-saved-snapshot-item-without-snapshot.json` | CREATE | ABSENT | `76454f6e05984d307c91526b844f640bd4dd4ea8140024041ecb2a3ef3308acd` | 3553 |
| `…/neg-saved-snapshot-target-both-ids.json` | CREATE | ABSENT | `2cd134a69a7e83696c25541664cfb8a554b3fba14e5bec22ddda641a37c2c95d` | 3635 |
| `…/neg-saved-snapshot-summary-missing-limitation.json` | CREATE | ABSENT | `ff348f509d050cb27435d46203ea8bd77b43a6d8ab0e539bf0d5a474f0968df4` | 3570 |
| `…/neg-saved-snapshot-bad-hash-format.json` | CREATE | ABSENT | `2b02188603feda3f9050f74bf8345bc3fd2f28aff39dc2633825b4f80a5bb0ac` | 3505 |
| `evidence/handoffs/PC07-handoff.md` | CREATE | ABSENT | (file này) | — |

Directory tạo: `contracts/ui/`, `contracts/telegram/`, `acceptance/fixtures/telegram/`.
**Không** chạm file của gói khác. Không lệnh git mutation, không network, không `__pycache__`
(`PYTHONDONTWRITEBYTECODE=1`), helper chạy từ scratch dir.

Ghi chú số lượng: packet liệt kê fixture (a)–(m) = 13; gói này tạo 13 + **5 negative** cho
schema Saved (EV-01 đòi "negative fixture(s) fail"), tất cả trong directory được cấp.

## 3. Source và dependency baseline

| Ref | sha256 | Bytes | Trạng thái |
| --- | --- | --- | --- |
| SRC-PLAN | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 | khớp baseline §2 |
| SRC-SPEC | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 | khớp baseline §2 |

Dependency đã đóng băng mà kết luận của gói này phụ thuộc (hash đo TẠI lần chạy gate cuối,
2026-09-06T18:34:58Z):

| File | sha256 | Bytes |
| --- | --- | --- |
| `contracts/modules.yaml` | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` | 75088 |
| `contracts/ports.yaml` | `5afd368f68237183a029e4b97e427773c9282ec91da2a45541f149da3893cc0a` | 115359 |
| `contracts/errors.yaml` | `e236aaee44cb340bf58ab822ab3dc434847e3d777b46c5b97b3baf00bd0e1b37` | 53534 |
| `contracts/state/delivery.yaml` | `9fcccc25fed432a895b15e9b98787d7294dd298d9209e9b0f2c7f801e1579626` | 26652 |
| `contracts/state/run.yaml` | `8acb7bbf935ee6854fa41d52604972929f09843838c1c141d861d17f538f3468` | 80492 |
| `contracts/data/entities.yaml` (FC-W2 epoch 2) | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` | 192018 |
| `contracts/state/storage.yaml` | `608ceea67834be427013d252ea35e7798be9ae56586b7174004fe4f12078eb0b` | — |
| `contracts/state/report.yaml` | `e60ef74f438faa7119d56950f8ab7ac8170df2c9c70f0b8b3d956e0412e79ced` | — |
| `contracts/retry-policy.yaml` | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` | — |
| `contracts/reporting/time-and-tags.md` | `652854d8bc681c6296f0b098e5db5e108653ce2f21c4c728df75199a04bc9d0f` | — |
| `contracts/schemas/report.schema.json` | `a8662d5d27b03724c27cef2959cb0a978713746da7733304fba6047e0c12000d` | — |
| `contracts/schemas/target.schema.json` | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` | — |
| `contracts/capabilities.yaml` | `c54cdaaf85be339aff5823902c9cb27a2aa25ebea61c241f1b76d2999e6ea7ab` | — |

**Drift quan sát được:** `contracts/ports.yaml` đổi TRONG lúc gói này chạy —
`485213cb…` (111240 B, 82 op) lúc bắt đầu → `5afd368f…` (115359 B, 85 op) lúc chạy gate cuối,
nhất quán với PC01 FIX3 (thêm `data.delete_target`, `data.purge_all`, và các sửa của FIX3).
Mọi gate đọc bản **hiện hành** và PASS. Kết luận chỉ có hiệu lực với đúng các hash ở bảng trên;
nếu PC01 còn commit tiếp, phải chạy lại `verify_pc07.py` trước freeze. PC02 (`entities.yaml`)
giữ nguyên hash FC-W2 epoch 2 suốt gói.

## 4. Evidence

Một lệnh chạy cả năm gate: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 verify_pc07.py`
· runtime Python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3
· started/ended 2026-09-06T18:34:58Z / 18:35:01Z · **exit code 0** · `RESULT: PASS (0 fail)` ·
**31 dòng PASS** · type `SELF_VALIDATION` cho tất cả.

| Evidence | Oracle | Kết quả |
| --- | --- | --- |
| **EV-PC07-01** | parse screens/commands/delivery front-matter; `check_schema` Draft 2020-12 cho saved-snapshot; 19 fixture parse; object `saved` validate | **PASS** — 10 màn hình, 3 lệnh, **2 positive saved ACCEPT**, **5 negative REJECT** với lý do đúng, **2/2 `content_hash` tái lập đúng** theo `sha256(JCS(content))` |
| **EV-PC07-02** | mọi `operation_id` ∈ ports.yaml; `auth_scope` khớp ports.yaml; mọi error code ∈ errors.yaml; mọi delivery state/transition ∈ delivery.yaml | **PASS** — 34 action, 8 error code, 5 delivery state, 9 transition `T-DL-*`; mọi giá trị `state` trong fixture thuộc enum đã khai |
| **EV-PC07-03** (ruling FIX3 §Fixtures) | `actor` ∈ `ports.yaml.<op>.caller_modules` **và** `(actor, owner, op)` ∈ `modules.yaml.allowed_edges`; event không có `operation` phải có `event_type`; `performed_by` là MOD id hợp lệ | **PASS** — **35/35 event** |
| **EV-PC07-04** (ruling FIX3 §Fixtures) | mọi cột trong `given`/`expected.rows` tồn tại trong `entities.yaml`, hoặc có marker `pending_cr_fields` | **PASS** — **246 cột kiểm**, 1 marker `pending_cr` mở (xem §6) |
| **EV-PC07-05** | oracle đặc thù: fixture a `automatic_resend_of_unknown_part = 0`; fixture h outbound = 0 và `domain_rows_changed = 0`; fixture i 0 lần tra mã khi sai định dạng và im lặng khi sai mã; fixture j 1 Saved + 5 phản hồi; fixture m 3 nhãn phân biệt; cụm "Không có nghiên cứu mới" = 0 lần trong **giá trị copy hiển thị** | **PASS** |

**Hai defect do chính gate của tôi bắt được và đã sửa trước handoff:**

1. EV-PC07-04 bắt `telegram_link_code.code_format` — một cột tôi **bịa** trong fixture (e).
   Đã gỡ; định dạng mã thuộc `commands.yaml`, không phải một cột của bảng. Đây đúng là lớp lỗi
   mà audit lần hai tìm thấy ở PC04.
2. EV-PC07-05 phiên bản đầu dùng grep theo DÒNG nên báo dương tính giả trên chính các câu
   **cấm** dùng cụm từ. Đã thay bằng phép quét theo **giá trị của trường copy hiển thị**
   (16 khóa copy), tức đo đúng thứ cần đo: chuỗi người dùng đọc.

**NOT_RUN:** mọi E1 (contract test theo fixture), E2 (fault injection: timeout/mất phản hồi/
crash), E3 (Telegram thật), E4 (review nội dung). Không có independent audit ở gói này.

## 5. Checklist packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Mọi màn hình §4 có read model, action→operation, auth, mobile, loading/empty/partial/error | **DONE** | `screens.yaml` — 10 màn hình (8 hàng §4 + Tag matching preview từ sơ đồ IA + Đăng nhập), mỗi màn hình đủ **năm** trạng thái (thêm `stale_last_known` theo storage.yaml UI-01..03) |
| 2 | 3 lệnh; vị trí resume; vòng đời link/unlink; ngoại lệ liên kết | **DONE** | `commands.yaml` §3 (CMD-save / CMD-run-now / CMD-status), §2 (B09), resume chỉ ở `SCR-runs`/`SCR-run-detail` (NC-UI-04) |
| 3 | Snapshot từ analysis revision đang đọc; Save trùng; unsave/re-save | **DONE** | `saved-snapshot.schema.json` §`x-contract.unsave_resave_semantics`; fixture (j) khẳng định `analysis_id_at_save = AN1` chứ không phải AN2 mới hơn |
| 4 | Ingress auth/replay, kiểm callback, generation recipient, OTP hết hạn/một lần, im lặng | **DONE** | `commands.yaml` §1 (ING-01..09), §2, §3 `validation_order` 6 bước |
| 5 | Outbox + parts + receipts + unknown; chính sách AC-14; định dạng/escaping là KC kèm URL | **DONE** | `delivery.md` §2, §3.3–3.5, §4, §5 (văn bản AMD-B03) |
| 6 | Fixture (a)–(m) | **DONE** | 13 fixture + 5 negative |
| — | I08/I09/I13 có positive + counterexample | **DONE** | I08: (j)(k) + neg-1/-2; I09: (c) + `forbidden_effects`; I13: (a)(m) + nhãn `delivery_unknown` riêng |
| — | Report trong app độc lập delivery; `unknown` không bao giờ hiện thành sent/failed | **DONE** | `screens.yaml` §global_rules.delivery_status_labels; fixture (a)(c) |
| — | CR-PC02-03 (tự nêu ở PC02) | **DONE** | `saved-snapshot.schema.json` khớp `entities.yaml` `saved_item`/`saved_snapshot`, gồm `content_hash` + quy tắc canonical JSON (RFC 8785) giống hệt `entities.yaml §conventions.hashes` |
| — | CR-PC04-07 | **DONE** | `screens.yaml` `ACT-rescan-corpus`: **bắt buộc** hiện số mục ước tính trước khi xác nhận; thiếu ước tính ⇒ không được hiện nút (NC-UI-08) |
| — | CR-PC01-02 (unlink là app action) | **DONE** | `commands.yaml §linking.unlink` + `screens.yaml ACT-unlink-telegram`, ghi `PROVISIONAL`, nêu rõ XN(D36) thắng ĐX(D37) |
| — | Số delivery trích từ PC03, không đặt số mới | **DONE** | `delivery.md` §4.2 trích 6 budget từ `retry-policy.yaml` |

## 6. Unresolved refs

### 6.1 Change requests

| CR | Tới | Nội dung |
| --- | --- | --- |
| `CR-PC07-01` | Owner / PC08 | Xác nhận ba số PROVISIONAL của liên kết: định dạng mã `^RR-[0-9A-HJKMNP-TV-Z]{8}$`, hạn **15 phút**, rate limit **5 lần/chat/giờ**. |
| `CR-PC07-02` | **PC02** (FIX3 hoặc packet sau) | Thiếu cột lưu bộ đếm rate-limit của B09. `commands.yaml` đặt ngưỡng 5 lần/chat/giờ nhưng `entities.yaml` không có nơi lưu ⇒ ngưỡng chưa ép được ở mức dữ liệu. Đề xuất `telegram_link_code.format_match_attempt_count` (integer, NOT NULL, default 0) hoặc bảng đếm theo `chat_id_hash` + cửa sổ. **Đã đánh dấu `pending_cr` trong fixture (i)**. |
| `CR-PC07-03` | PC05 | `telegram.receive_update` cần khai secret token webhook và quy tắc so sánh constant-time trong openapi; PC07 chỉ khóa ngữ nghĩa (ING-01). |
| `CR-PC07-04` | PC09 / Owner | Giới hạn định dạng Telegram vẫn `KC` (không có mạng). Cần một bước đọc <https://core.telegram.org/bots/api#sendmessage> và ghi lại độ dài tin, độ dài callback data, parse mode, bảng escape, rate limit. Chặn `CONTRACT_READY` của `delivery.md` §3.4. |
| `CR-PC07-05` | PC08 | Xác nhận `telegram_update_max_age` PROVISIONAL 24 giờ (chống phát lại backlog webhook sau khi server offline lâu). |
| `CR-PC07-06` | PC09 | Phân xử scenario ID: PC07 lấy **SC45–SC48**; xem §6.3. |

### 6.2 Quyết định PROVISIONAL do PC07 đưa ra

| Mục | Giá trị | Ai chốt |
| --- | --- | --- |
| Định dạng / hạn / rate limit mã liên kết | `RR-` + 8 ký tự Crockford; 15 phút; 5 lần/giờ | Owner (CR-PC07-01) |
| Giờ yên lặng Telegram (REQ-OQ07) | **không có**; nếu bật thì HOÃN intent, không HỦY, không mất digest | Owner |
| `telegram_update_max_age` | 86400 giây | PC08 (CR-PC07-05) |
| Unlink là app action, không phải lệnh thứ tư | theo ruling CR-PC01-02; XN(D36) thắng ĐX(D37) | Owner có thể đảo ngược |
| Nút Export ở màn hình Saved | **ẩn** ở MVP (`save.export.lifecycle_status = deferred_p1`, REQ-OQ10, F-PC00-02) | Owner |
| `owner_session` = HttpOnly cookie + CSRF double-submit | theo chỉ dẫn Coordinator; PC05/PC08 hội tụ | PC08 |

### 6.3 Scenario ID và rủi ro trùng

PC07 lấy **SC45** (run-now bị chặn bởi `needs_user`), **SC46** (callback Telegram cũ),
**SC47** (vòng đời mã liên kết + ngoại lệ B09), **SC48** (schema Saved từ chối payload sai).

FIX3-rulings nói SC33–SC44 đã dùng và "PC05/PC06/PC07 take SC45+ if needed". Tại thời điểm
viết handoff này, `evidence/handoffs/PC06-handoff.md` **không tồn tại** (thư mục chỉ có PC00,
PC01, PC02, PC03, PC04, PC08), nên PC07 **không kiểm được** PC06 đã lấy số nào, và PC05 cũng
chưa có handoff. Rủi ro trùng SC45+ giữa PC05/PC06/PC07 là **thật và chưa loại trừ được** →
CR-PC07-06 đề nghị PC09 phân xử khi đủ ba handoff.

### 6.4 Sai lệch nhỏ trong packet (đã theo baseline, ghi lại để PC09 đối chiếu)

Packet mô tả fixture (e) là "relink → … (SC26)". Theo baseline §3, thứ tự plan §13 cho
**SC25 = Telegram relink** và **SC26 = disk full**. PC07 dùng **SC25**. Nếu Coordinator thực
sự muốn SC26 thì đó là mâu thuẫn với baseline và cần một ruling.

### 6.5 Mối lo còn lại

1. **`KC` của Telegram là mối lo lớn nhất.** Cấu trúc digest, cách tách phần và độ dài callback
   data đều dựa trên giả định chưa kiểm chứng. `delivery.md` §3.4 nói rõ điều này và cấm suy ra
   giới hạn từ trí nhớ, nhưng hợp đồng vẫn chưa thể `CONTRACT_READY` cho phần định dạng.
2. **`screens.yaml` chưa có fixture riêng.** Read model và action map được kiểm bằng script
   (operation tồn tại, auth khớp, cụm từ bị cấm), chưa có scenario render. Review giao diện
   thật là E1/E4 và là NOT_RUN.
3. **`TXN-checkpoint-only` / các gói song song:** PC05 (openapi) và PC06 (AI) chưa xong; mọi
   tham chiếu tới chúng trong file này là theo đường dẫn kế hoạch, chưa đối chiếu được.
4. **Không có independent audit.** `audit_route: INDEPENDENT_REQUIRED` chưa thực hiện; Worker
   không được tự audit candidate của mình.

## 7. Kết thúc

Sau khi ghi file này, `worker-W3` không ghi thêm file nào. Lease `LEASE-PC07-e1` nhả lúc
2026-09-06T18:38Z. Mọi sửa tiếp theo cần packet mới, baseline mới, lease mới với fencing cao hơn.
PC07 sẵn sàng nhận `PKT-PC02-FIX3` như Coordinator đã báo trước.

---

# ADDENDUM — PKT-PC07-FIX1 (đóng CR-PC07-02 sau khi PC02 thêm `telegram_link_attempt`)

## A1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC07-FIX1` · authority `AUTH-COORD-PC07-FIX1` · lease `LEASE-PC07-e2` (fencing 2) |
| worker principal | `worker-W3` · expires_at 2026-09-07T06:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| next actor | Coordinator · `lease_released_at` | 2026-09-06T18:47Z |

`DONE` chứ không phải `DONE_WITH_CONCERNS`: phạm vi hẹp, đã hoàn tất trọn vẹn, năm gate PASS,
không CR mới, không quyết định PROVISIONAL mới.

## A2. Delta

### A2.1 Gỡ marker `pending_cr` (mục 1 của packet)

`acceptance/fixtures/telegram/i-unknown-chat-valid-code-format.json`:

- Xóa khối `pending_cr_fields` và cột giả định `telegram_link_code.format_match_attempt_count`.
- Thêm `closed_cr` ghi rõ CR-PC07-02 được đóng bởi `ENT-telegram-link-attempt` (PKT-PC02-FIX3).
- Oracle rate limit nay trỏ vào **bảng thật** với đúng các cột đã khóa ở
  `entities.yaml` `209cf03e…`: `chat_id_hash`, `attempted_at`, `outcome`, `link_code_id`.

Ba mốc oracle mới, phản chiếu đúng quy tắc "chỉ ghi khi khớp định dạng":

| Sự kiện | `telegram_link_attempt` | Vì sao |
| --- | --- | --- |
| 1 — văn bản thường ("xin chào") | **0 hàng** | Không khớp định dạng ⇒ KHÔNG ghi. Nếu ghi, bảng thành nhật ký mọi tin nhắn của người lạ — điều `entities.yaml` cấm tường minh |
| 2 — `RR-ZZZZZZZZ` (đúng định dạng, sai mã) | 1 hàng, `outcome = format_match_code_invalid`, `link_code_id = NULL` | Được đối chiếu rồi im lặng |
| 3 — đúng mã | 2 hàng; hàng thứ hai `outcome = format_match_code_valid`, `link_code_id` trỏ mã | Liên kết thành công |

Thêm `expected.rate_limit` với `counter_source`, `counter_query_vi`, hành vi khi vượt ngưỡng
(**vẫn im lặng**, ghi `rate_limited_not_checked`, không bao giờ trả `RATE_LIMITED` cho chat
chưa liên kết) và ghi chú retention 30 ngày PROVISIONAL (CR-PC02-17). Thêm hai
`forbidden_effects`: không ghi hàng cho tin không khớp định dạng; không lưu chat ID thô.

### A2.2 `commands.yaml` dẫn nguồn đếm (mục 2 của packet)

`§linking.rate_limit` thêm `counter_source` (entity, file, 4 cột, câu truy vấn) và ghi rõ bảng
này do PC02 thêm ở FIX3 theo CR-PC07-02 mà chính PC07 nêu. Thêm `write_rule_vi` (chỉ ghi khi
khớp định dạng; lưu hash, không lưu chat ID thô) và `retention_vi`. `§ingress.silent_drop_summary`
hàng "đúng định dạng mã" thêm `counter_row_vi`. `dependencies` thêm `contracts/data/entities.yaml`.

## A3. Hash trước/sau

| Path | Before (PKT-PC07) | Bytes | After (FIX1) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/telegram/commands.yaml` | `60677804a81ca855e6fa82b59d0ddebbc2d4678e5997193a7e3ddf229f4886a7` | 23598 | `7d77cf34ca178601838777d8c8d21ef240a2f72cf772ce6894a315e95cddf11c` | 24727 |
| `…/i-unknown-chat-valid-code-format.json` | `a1970b37acf92ada3f8e01df02431ac58950aff212524d914fb4f730f5b82eca` | 5769 | `19b977a4ff9bc46b0528ec9bf1d0aef9e8d6fc02541de6d6a07aed07c9abb90c` | 6961 |

**Không đổi** (trong grant, không cần sửa): `contracts/ui/screens.yaml` `b73fb711…` 44515 ·
`contracts/telegram/delivery.md` `22e58c0d…` 16793 ·
`contracts/schemas/saved-snapshot.schema.json` `1818c0d8…` 16204 · 17 fixture telegram còn lại
và `acceptance/fixtures/telegram/README.md` `a0048058…` (README vẫn mô tả cơ chế `pending_cr`
đúng như hợp đồng chung; chỉ ví dụ cụ thể là đã đóng — xem §A6).

`evidence/handoffs/PC07-handoff.md`: before `f21f71af09cfcdd5ca0199b925bbc02c2a0ae70b659e00eb52ef8e1e590c8c2e` / 17398 bytes; after = file này (APPEND).

## A4. Evidence — năm gate chạy lại (mục 3 của packet)

- command: `cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 verify_pc07.py`
- runtime: Python 3.12.3, PyYAML 6.0.1, jsonschema 4.10.3 · type `SELF_VALIDATION`
- started/ended UTC: 2026-09-06T18:45:22Z / 18:45:24Z · **exit code 0** · `RESULT: PASS (0 fail)` · **31 PASS**

| Evidence | Kết quả |
| --- | --- |
| EV-PC07-01 | PASS — 10 màn hình, 3 lệnh, metaschema OK, 19 fixture parse, 2 saved ACCEPT / 5 REJECT, 2/2 `content_hash` tái lập |
| EV-PC07-02 | PASS — 34 action → operation tồn tại, auth khớp, 8 error code, 5 delivery state, 9 transition `T-DL-*` |
| EV-PC07-03 | PASS — **35/35** event hợp lệ về caller và `allowed_edges` |
| EV-PC07-04 | PASS — **252 cột** kiểm (tăng từ 246), **0 marker `pending_cr` còn mở** |
| EV-PC07-05 | PASS — fixture a resend=0; h outbound=0; i 0 lần tra khi sai định dạng và im lặng khi sai mã; j 1 Saved/5 phản hồi; m 3 nhãn phân biệt; cụm bị cấm vắng mặt ở 16 trường copy |

### Hash upstream tại lần chạy

| File | sha256 | Bytes | So với PKT-PC07 |
| --- | --- | --- | --- |
| `contracts/ports.yaml` | `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a` | 121958 | **đổi** (từ `5afd368f…`/115359) |
| `contracts/modules.yaml` | `89b348aa8d3f89d38c945a7f15a8fe2c46e2619a1226649e4633bf30367264f5` | 75794 | **đổi** (từ `bd44d734…`/75088) |
| `contracts/data/entities.yaml` | `209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece` | 214203 | **đổi** (từ `2235564f…`/192018 — chính là PKT-PC02-FIX3) |
| `contracts/errors.yaml` | `3201bbe86a3ef373a4fb35c265cd9f27ed60f6ce2af3fd65a76c0dcfb032d86b` | 59570 | **đổi** (từ `e236aaee…`/53534 — PC03 FIX1, thêm `CSRF_REJECTED`) |
| `contracts/state/run.yaml` | `fcad82589aaee43fb15735b10fc7fd7d25c7e94af6e32295aca40a4b0d88999d` | 86734 | **đổi** (từ `8acb7bbf…`/80492 — PC03 FIX1) |
| `contracts/state/delivery.yaml` | `9fcccc25fed432a895b15e9b98787d7294dd298d9209e9b0f2c7f801e1579626` | 26652 | không đổi |
| `contracts/state/storage.yaml` | `608ceea67834be427013d252ea35e7798be9ae56586b7174004fe4f12078eb0b` | — | không đổi |

**Drift KHÔNG gây failure nào.** Năm file upstream đã đổi kể từ PKT-PC07 (PC01 FIX3, PC02 FIX3,
PC03 FIX1) và cả năm gate vẫn PASS trên bản hiện hành: mọi `operation_id`, error code, delivery
state và tên cột mà PC07 tham chiếu đều còn tồn tại sau các thay đổi đó. Không có CR nào phải
mở vì drift — đúng như packet yêu cầu (báo cáo, không sửa upstream).

Nguồn SRC-PLAN `f65bb046…` / SRC-SPEC `d35e1f2d…`: khớp baseline §2.

## A5. CR

| ID | Trạng thái |
| --- | --- |
| `CR-PC07-02` | **ĐÓNG** — `ENT-telegram-link-attempt` tồn tại trong `entities.yaml` `209cf03e…`, `commands.yaml` dẫn nguồn, fixture (i) khẳng định oracle trên bảng thật, EV-PC07-04 báo 0 marker còn mở |
| `CR-PC07-01`, `-03`, `-04`, `-05`, `-06` | Vẫn mở như PKT-PC07 §6.1. `CR-PC07-04` (giới hạn định dạng Telegram vẫn `KC`) vẫn là mối lo lớn nhất của gói |
| — | Không CR mới trong FIX1 |

## A6. Ghi chú nhỏ

`acceptance/fixtures/telegram/README.md` §6 vẫn mô tả cơ chế `pending_cr` và nêu fixture (i)
làm ví dụ đang mở. Ví dụ đó nay đã đóng. Tôi **không** sửa README trong packet này vì mô tả cơ
chế vẫn đúng và packet chỉ cấp phạm vi cho hai việc cụ thể; ghi lại ở đây để lần chạm README
kế tiếp cập nhật một dòng. Không ảnh hưởng gate nào (EV-PC07-04 đọc fixture, không đọc README).

## A7. Kết thúc

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC07-e2` nhả lúc
2026-09-06T18:47Z. Không lệnh git mutation, không network, không file ngoài grant, không
`__pycache__`, không chạm file upstream.

---

# ADDENDUM — PKT-PC07-FIX2 (quy ước annotation R4-01 + README đầy đủ)

## B1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC07-FIX2` · authority `AUTH-COORD-PC07-FIX2` · lease `LEASE-PC07-e3` (fencing 3) |
| worker principal | `worker-W3` · expires_at 2026-09-07T08:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| findings | F-A1R3-01, F-A1R3-04 → `FIX_PROPOSED` |
| next actor | Coordinator · `lease_released_at` | 2026-09-06T19:05Z |

`DONE_WITH_CONCERNS` vì hai con số của packet không khớp thực tế đếm được (§B6); công việc
hoàn tất nhưng Coordinator cần biết chênh lệch.

## B2. Delta

### B2.1 Đổi tên khóa annotation (R4-01)

**29 khóa** trong **13 file**:

| File | Số khóa | | File | Số khóa |
| --- | --- | --- | --- | --- |
| `a-multipart-part2-unknown-no-resend.json` | 4 | | `h-unknown-chat-status-silent.json` | 1 |
| `b-response-lost-unknown-operator-decides.json` | 1 | | `i-unknown-chat-valid-code-format.json` | 1 |
| `c-permanent-failure-report-intact.json` | 2 | | `j-concurrent-save-app-telegram.json` | 5 |
| `d-unlink-before-send-cancelled.json` | 2 | | `k-save-then-source-deleted.json` | 2 |
| `e-relink-old-generation-cancelled.json` | 1 | | `l-run-now-while-needs-user.json` | 3 |
| `f-stale-callback-no-save.json` | 2 | | `m-three-run-states-distinct-text.json` | 3 |
| `g-link-code-used-twice.json` | 2 | | **Tổng** | **29** |

Khóa đổi: `note` → `_note` (26), `target` → `_target` (2), `save_channel_note` →
`_save_channel_note` (1). Năm file `neg-saved-snapshot-*` không có `rows` nên không đổi.

### B2.2 README (F-A1R3-04)

- Thêm **§0** phát biểu nguyên văn quy tắc R4-01 (ba nhánh a/b/c, không allowlist theo gói).
- Bảng danh mục nay liệt kê **từng file một**: năm `neg-saved-snapshot-*` được tách thành năm
  hàng riêng (trước đây gộp một hàng), cộng hàng `README.md` → đủ **19 file** của thư mục.
- **Gỡ** ghi chú §6 "một marker đang mở" đã lỗi thời; thay bằng câu nói rõ hiện **không còn
  marker `pending_cr` nào mở** trong thư mục, và marker cũ (`CR-PC07-02`) đã gỡ ở PKT-PC07-FIX1
  sau khi PC02 thêm entity `telegram_link_attempt`.
- §6 nay mô tả gate chạy trên **cả sáu** thư mục, không riêng thư mục này.

## B3. Hash

| Path | Before | Bytes | After | Bytes |
| --- | --- | --- | --- | --- |
| `acceptance/fixtures/telegram/README.md` | `a004805838b293439422a177791e7941a7c220980d7495745a7ec45e8b7aaa57` | 8541 | `7ac9c511072bfc335e3e6eff92515b2e371274a9f4841c3b5a573cb9059fa331` | 10178 |

13 file JSON đã đổi (a–m); hash sau lấy bằng `sha256sum acceptance/fixtures/telegram/*.json`.
Năm `neg-saved-snapshot-*` giữ nguyên hash của PKT-PC07. Ngoài thư mục fixture: không file nào
bị chạm (grant của packet này chỉ có `acceptance/fixtures/telegram/*`).

## B4. Gate `fixture-field-existence` (R4-01) — cả sáu thư mục

**Lệnh chính xác, tái lập được độc lập** (cùng script mà addendum PKT-PC02-FIX4 dùng, nên hai
handoff phải cho cùng số):

```text
cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 fixture_field_gate.py
```

Chạy 2026-09-06T19:02:08Z → 19:02:13Z · entities.yaml
`209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece` (60 entity) · **exit 0**:

| directory | files | columns | unresolved |
| --- | --- | --- | --- |
| identity | 14 | 372 | **0** |
| reporting | 13 | 390 | **0** |
| collection | 8 | 0 | **0** |
| ai | 11 | 40 | **0** |
| telegram | 18 | 252 | **0** |
| recovery | 10 | 0 | **0** |
| **TOTAL** | **74** | **1054** | **0** |

Trước khi sửa: identity 52, telegram 29, reporting 6 (tổng 87).

**EV-PC07-04 nay CHÍNH LÀ gate này.** Trước FIX2 nó dùng một allowlist nội bộ
(`{note, note_vi, target, rows, counts}` + hậu tố `*_note`) — đúng loại allowlist mà R4-01
cấm, và là lý do 29 khóa trần của tôi lọt qua ở PKT-PC07. Nay `verify_pc07.py` gọi
`fixture_field_gate.py` như subprocess và exit code hợp vào kết quả, nên con số trong handoff
này tái lập được bằng lệnh trên mà không cần chạy `verify_pc07.py`.

`verify_pc07.py` (năm gate) **exit 0**, `RESULT: PASS (0 fail)`; `verify_pc02.py` **exit 0**.

## B5. Ghi chú về `collection` và `recovery`

Hai thư mục báo **0 cột kiểm** vì fixture ở đó không dùng khóa `rows` (W4 dùng cấu trúc event,
W2 dùng cấu trúc drill). **0 cột kiểm không phải bằng chứng đã sạch** — nó chỉ có nghĩa quy tắc
R4-01 không áp dụng được ở đó. Ghi rõ để không ai đọc bảng trên thành "sáu thư mục đều đã
kiểm". Đề nghị PC09 quyết định có mở rộng R4-01 sang cấu trúc khác không (CR-PC02-18).

## B6. Chênh lệch so với packet

| Packet nói | Đếm được | Ghi chú |
| --- | --- | --- |
| telegram **31** occurrences | **29** | Gate liệt kê từng lần xuất hiện dưới `rows`; tôi đổi tên cho tới khi unresolved = 0 và kết quả là 29. Không tìm được 2 khóa còn lại; có thể audit đếm thêm khóa ngoài `rows` (ví dụ trong `expected.responses` hay `log`) mà R4-01 không ràng buộc |
| README liệt kê **23** file | **19** | Thư mục có 18 JSON (13 kịch bản + 5 negative) + README. Tôi liệt kê đủ 19 và ghi số thật vào README thay vì tạo bốn hàng không có file tương ứng |

Cả hai chênh lệch đều theo hướng **ít hơn** con số packet; tôi không bịa thêm để khớp. Nếu
audit thật sự thấy 31/23, xin chỉ ra hai khóa và bốn file còn lại.

## B7. Kết thúc

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC07-e3` nhả lúc
2026-09-06T19:05Z. Không lệnh git mutation, không network, không file ngoài grant, không
`__pycache__`.

---

# ADDENDUM — PKT-PC07-FIX3 (fixture SC10 + SC51, requirement_refs R5-03)

## C1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC07-FIX3` · authority `AUTH-COORD-PC07-FIX3` · lease `LEASE-PC07-e4` (fencing 4) |
| worker principal | `worker-W3` · expires_at 2026-09-07T12:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| rulings | R5-02 (fixture SC10, SC51), R5-03 (requirement_refs), amendment CR-PC07-07 |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T00:25Z |

Gói này bị ngắt bởi rate limit ở lần chạy trước. Khi tiếp tục tôi đã kiểm lại:
`date -u` = 2026-09-07T00:16:18Z (trong hạn lease), SRC-SPEC `d35e1f2d…` và SRC-PLAN
`f65bb046…` khớp baseline §2, `acceptance/fixtures/ui/` **chưa tồn tại** và
`PC07-handoff.md` **chưa có** mục PKT-PC07-FIX3 — xác nhận không có write dở dang.

## C2. Delta

### C2.1 Fixture mới (R5-02)

| Path | sha256 | Bytes |
| --- | --- | --- |
| `acceptance/fixtures/ui/README.md` | `f77845849187ce9036fecabb2ab9f6035ec3e58230d93a5778e6bdefd84b3591` | 5973 |
| `acceptance/fixtures/ui/sc10-same-analysis-revision-app-and-telegram.json` | `6a1602366e1de51cf6eb4a3fb7f843761e54e89716a2533e7b41fb390097dc15` | 10407 |
| `acceptance/fixtures/ui/sc51-first-time-setup.json` | `4671d87f7bf7efa062d89c23cc5a8b1e7586f27656ffa506b1150e37132c3b7b` | 15420 |

**SC10.** Cả năm trường REQ-D20 (`content`, `difference_from_prior`, `limitation_vi`,
`evidence_level`, `matched_tags[]`) được khẳng định trên **cả hai** kênh, cùng oracle bằng nhau
`app.analysis_id == telegram.analysis_id`. `given` cố ý chứa một `analysis` thứ hai
(generation 2) xuất hiện **sau** `report.published_at`: bất kỳ kênh nào tham chiếu nó là vi
phạm I05, và điều đó được ghi thành `forbidden_effects` chứ không để ngầm. Events: `report.get`
(actor `MOD-web-ui`), `delivery.create_intent` (actor `MOD-report-service`), và một
`event_type: human_read` cho phần E4 không mock được.

**SC51.** Năm bước §5.1 thành 10 event, mỗi event mang `step_ref`. Actor đúng caller theo
`ports.yaml`: `auth.login`/`tag.create`/`tag.preview_matches`/`settings.update_config`/
`settings.test_provider`/`telegram.issue_link_code` ← `MOD-web-ui`; `telegram.receive_update`
← `EXT-telegram-api`; `telegram.consume_link_code` ← `MOD-telegram-adapter`;
`worker.register_capabilities` ← `MOD-x-collector`. Bước 5 là `event_type:
human_x_device_verification` vì nó không phải operation của hệ thống. `expected.rows` phủ 10
bảng; bốn oracle âm gồm **không có endpoint signup**, **không adapter nào `enabled=true`**, và
câu empty state của Topics **không được** là "Không có nghiên cứu mới".

### C2.2 `contracts/ui/screens.yaml` (R5-03)

`b73fb711e745e4d266f8ef7bdda1570df1ed397834c0b8985184ff3a44a9068e` (44515) →
`f841172bf5b54ca08ca0bd2751fc7413923fc59aaeba70e06cc69bd9a16b5f60` (47290).

`requirement_refs` được gắn **tại nơi màn hình/action thực sự hiện thực yêu cầu**, không rải
đều: `REQ-S5.1-01` → `SCR-login` + `ACT-login`; `REQ-S5.1-02` → `SCR-topics` +
`ACT-create-tag` + `ACT-preview-matches` + `SCR-tag-matching-preview`; `REQ-S5.1-03` →
`SCR-settings` + `ACT-update-settings` + `ACT-test-provider`; `REQ-S5.1-04` →
`ACT-issue-telegram-code`; `REQ-S5.1-05` → `SCR-runs` (đăng nhập X làm ngoài app; Runs chỉ
hiện trạng thái collector); `REQ-S5.3-01` → `SCR-reports` + `SCR-report-detail` +
`ACT-save-item`; `REQ-S5.3-03` → `SCR-report-detail` (deep link, mobile `read_and_save`);
`REQ-S4-01/-08` đã có sẵn; `REQ-S4-09` → `global_rules.navigation`; `REQ-S4-10` →
`global_rules.visual_design`. `coverage_matrix` thêm hai khối
`spec_section_5_1_setup_steps` (5 hàng) và `spec_section_5_3_read_and_save` (2 hàng).

### C2.3 Amendment CR-PC07-07 (marker mỗi lần xuất hiện)

Gate của W5 báo 2 cột chưa giải trong `sc51-first-time-setup.json`
(`provider_config.terms_check_at` ×2) trong khi gate của tôi báo 0. Nguyên nhân: tôi dùng map
**cấp file** `pending_cr_fields`, gate của W5 tìm marker **cấp hàng**. Theo ruling tôi đã thêm
`"pending_cr": "CR-PC07-07"` vào **cả hai** hàng `provider_config` kèm câu giải thích, giữ
nguyên map cấp file, và dạy gate dùng chung chấp nhận **cả hai** dạng (khóa `pending_cr` là
khóa bảo lưu, không bị coi là cột trần).

Hash của `sc51-first-time-setup.json` do đó đổi **hai lần** trong gói này: bản sinh lần đầu
`648424492f506a9a15d8a7bcb76c58486860fbb1b82a4eac27669d4ab57cbbaa` (13829 B) → bản sau
amendment `4671d87f7bf7efa062d89c23cc5a8b1e7586f27656ffa506b1150e37132c3b7b` (15420 B).
Bảng §C2.1 ghi giá trị **cuối**; đây là giá trị dùng cho mọi đối chiếu.

## C3. Gate

Lệnh tái lập được độc lập:

```text
cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 fixture_field_gate.py
cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 check_actor_edges_all.py
```

Chạy 2026-09-07T00:21:09Z → 00:21:12Z. `contracts/data/entities.yaml`
`209cf03e169aeffb4e1a95d74ca852186a391e65f1825c7ce0e81e8ae5eb5ece` (60 entity);
`contracts/ports.yaml` `87c95da46c607c977a7f0421cc4110745575efc47581952d3d619a4147f1f305`
(122712 B) — đúng bản packet nêu; `contracts/modules.yaml`
`e63181eb4bebaad32cc5e3f73abfb6eba36572988360aec042fdcbe484b4c73f` (98589 B) — **đã đổi** so
với `89b348aa…` lúc tôi bắt đầu, nhất quán với việc W2 đang sửa `denied_cases`;
`allowed_edges` không đổi nên kết quả actor-edge không bị ảnh hưởng.

**fixture-field-existence (R4-01) — exit 0:**

| directory | files | columns | unresolved |
| --- | --- | --- | --- |
| identity | 14 | 372 | 0 |
| reporting | 14 | 475 | 0 |
| collection | 12 | 176 | 0 |
| ai | 11 | 40 | 0 |
| telegram | 18 | 252 | 0 |
| recovery | 10 | 0 | 0 |
| **ui (mới)** | **2** | **117** | **0** |
| **TOTAL** | **81** | **1432** | **0** |

**fixture-actor-edge (mọi thư mục) — exit 1, 6 fail, KHÔNG cái nào thuộc `ui/`:**

| directory | events | ok | forbidden |
| --- | --- | --- | --- |
| ai | 26 | 26 | 0 |
| boundary | 32 | 0 | 32 |
| collection | 26 | 26 | 0 |
| identity | 22 | 22 | 0 |
| recovery | 33 | 31 | 2 |
| reporting | 62 | 62 | 0 |
| telegram | 35 | 35 | 0 |
| **ui** | **11** | **11** | **0** |

`verify_pc07.py` (năm gate PC07) **exit 0**, `RESULT: PASS (0 fail)`.

## C4. CR

| ID | Tới | Nội dung |
| --- | --- | --- |
| `CR-PC07-07` | **PC02** | Thêm `provider_config.terms_check_at` (timestamp_utc_ms RFC 3339, nullable) **và** `provider_config.terms_check_by` (string, nullable — ai đã xác nhận), kèm CHECK `enabled = true ⇒ terms_check_at IS NOT NULL`. Căn cứ: REQ-A5 và ADR-0010 đòi ghi nhận việc đã đọc điều khoản TRƯỚC khi bật một adapter; oracle mạnh của SC51 hiện chỉ khẳng định được dạng yếu `COUNT(enabled=true) = 0`. Hai hàng trong `sc51-first-time-setup.json` mang marker `pending_cr: CR-PC07-07` cho tới khi cột tồn tại |
| `CR-PC07-08` | **W2 (PC08/boundary)** | `boundary/a-default-deny-sweep-36-edges.json`: seq=3 đánh dấu `edge_assertion: forbidden` nhưng bộ ba (caller, owner, operation) **CÓ** trong `allowed_edges` — hoặc marker sai, hoặc `modules.yaml` đã cho phép cạnh mà sweep coi là cấm; seq=8/17/20/21 thiếu **cả** `operation` lẫn `event_type` (vi phạm R4-02) |
| `CR-PC07-09` | **W4 (PC05/collection)** | `collection/c-challenge-mid-batch.json` seq=2 thiếu cả `operation` lẫn `event_type` |
| `CR-PC07-04` | — | Vẫn mở: giới hạn định dạng Telegram còn `KC`; nó chặn phần render Telegram của SC10 |

CR-PC07-08/-09 là **báo cáo, không sửa**: hai file đó nằm ngoài write grant của packet này.

## C5. Mối lo

1. SC10 chỉ đạt E1 (sự hiện diện năm trường + bằng nhau `analysis_id`). **E4 vẫn cần**: phán
   đoán "không cần mở nguồn để quyết định" là của người đọc, theo rubric
   `contracts/ai/grounding.md` §6, trên desktop/điện thoại/Telegram thật.
2. SC51 bước 5 cần **E3** và **REQ-OQ01 vẫn CHẶN M0**: REQ-D09 (profile Chrome riêng của dự án)
   còn ở trạng thái `ĐX` trong một hạng mục P0. Fixture **không** promote nó; nó chỉ neo yêu cầu.
3. `recovery` và `boundary` báo 0 cột kiểm hoặc 0 event hợp lệ ở gate field — không phải bằng
   chứng đã sạch, chỉ là quy tắc không áp dụng được ở cấu trúc đó (xem CR-PC02-18).
4. `modules.yaml` đổi giữa lúc chạy (W2). `allowed_edges` không đổi nên kết luận giữ nguyên;
   phải chạy lại nếu W2 chạm `allowed_edges`.

## C6. Kết thúc

`worker-W3` không ghi thêm file nào sau mục này. Lease `LEASE-PC07-e4` nhả lúc
2026-09-07T00:25Z. Không lệnh git mutation, không network, không file ngoài grant, không
`__pycache__`.

---

**Ghi chú PKT-PC02-FIX5 (một dòng, lease `LEASE-PC02-e6`):** `CR-PC07-07` đã **đóng** — PC02 thêm `provider_config.terms_check_at` / `terms_check_by` / `terms_doc_ref` cùng CHECK `enabled ⇒ terms_check_at IS NOT NULL`; hai marker `pending_cr` trong `acceptance/fixtures/ui/sc51-first-time-setup.json` đã gỡ và oracle SC51 nâng lên dạng mạnh `COUNT(provider_config WHERE enabled = true AND terms_check_at IS NULL) = 0`; chi tiết ở addendum PKT-PC02-FIX5 của `evidence/handoffs/PC02-handoff.md`.

---

# ADDENDUM — PKT-PC07-FIX4 (E0-04c: cột chỉ từng được đề xuất, trong README)

## D1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC07-FIX4` · authority `AUTH-COORD-PC07-FIX4` · lease `LEASE-PC07-e5` (fencing 5) |
| worker principal | `worker-W3` · expires_at 2026-09-07T18:00Z · mode DOCUMENTARY_DRAFT |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| next actor | Coordinator · `lease_released_at` | 2026-09-07T01:55Z |

`date -u` = 2026-09-07T01:48:51Z (trong hạn); nguồn khớp baseline §2.

## D2. Delta yêu cầu (b)

`acceptance/fixtures/telegram/README.md` §6 nhắc
`telegram_link_code.format_match_attempt_count` — một cột **chỉ từng được ĐỀ XUẤT** trong
`CR-PC07-02`, chưa bao giờ tồn tại. Bộ đếm thật là entity `telegram_link_attempt`. Viết lại
đoạn đó bằng **các cột thật**: `telegram_link_attempt.chat_id_hash`,
`telegram_link_attempt.attempted_at`, `telegram_link_attempt.outcome`,
`telegram_link_attempt.link_code_id`, kèm truy vấn đếm và hành vi khi vượt ngưỡng (ghi một hàng
`outcome = 'rate_limited_not_checked'` và **vẫn im lặng**). Đếm `format_match_attempt_count`
trong thư mục: **0**.

## D3. Delta phát sinh: quét E0-04c trên toàn bộ file PC07

Packet yêu cầu chạy gate trên **mọi** file PC07 → 0. Lần chạy đầu cho **48** token `<a>.<b>`
không giải được. Không cái nào là cột bịa; tất cả là tham chiếu tới **namespace khác** viết
dưới dạng dễ nhầm với `entity.column`. Bốn nhóm, và cách xử lý:

| Nhóm | Ví dụ | Viết lại thành |
| --- | --- | --- |
| Đường dẫn mục trong chính file | `global_rules.run_status_labels`, `§linking.one_use`, `code_format.regex` | `§ global_rules → run_status_labels`, `§ linking → one_use`, … |
| Thuộc tính của **read model** (report.schema.json) | `report.items`, `report.coverage`, `report_item.target` | `items` của report.schema.json; `target` trong `$defs/report_item` của report.schema.json |
| Đối tượng **wire** của saved-snapshot vs cột bảng | `snapshot.content`, `snapshot.content_hash` | `saved_snapshot.payload` (object `content` trên wire), `saved_snapshot.content_hash` |
| Namespace ngoài / giá trị enum / cấu trúc fixture | `callback_query.id`, `from.id`, `delivery.unknown`, `storage.health`, `given.rows`, `app.analysis_id` | trường `callback_query` → `id` của update Telegram; `delivery.state = 'unknown'`; trạng thái kho; `given` → `rows`; "analysis_id ở kênh app bằng … kênh Telegram" |

Điểm đáng ghi: `snapshot.content` vs `saved_snapshot.payload` không chỉ là chuyện đặt tên —
tên **wire** và tên **cột** khác nhau, và viết `snapshot.content_hash` trong một oracle làm
người đọc tưởng đó là cột. Nay mọi oracle hash đều nói `sha256(JCS(saved_snapshot.payload))`
bằng `saved_snapshot.content_hash`, khớp đúng `entities.yaml`.

Tổng 42 lần thay trên 12 file. **Không** thay đổi ngữ nghĩa nào: không cột, khóa, enum,
operation hay oracle nào bị đổi giá trị — chỉ đổi cách viết tham chiếu.

## D4. Hash sau

| Path | sha256 | Bytes |
| --- | --- | --- |
| `contracts/ui/screens.yaml` | `db78678cba7e46b33669596f02963e1eac5e65804c6f9a997bf22d72ba6bc296` | 47481 |
| `contracts/telegram/commands.yaml` | `fc1a18dac332ea51e63721536d6a47b1d5a3048ed408af24ae787a91874e3556` | 24834 |
| `contracts/telegram/delivery.md` | `cb3a4b30a26f2a5ca5cf9d11359b84ce5612c003dfe51c3acbdbba5d7fde226c` | 16807 |
| `contracts/schemas/saved-snapshot.schema.json` | `1178d314deb8dfdfbe24a9bd4645fd0fd34424fa1db0c237971b3dba3705ce3c` | 16298 |
| `acceptance/fixtures/telegram/README.md` | `dbb368afae93bd40530a153769106995643996669a57a26dd2e55fb1ef905863` | 10508 |
| `acceptance/fixtures/ui/README.md` | `c7ac5d304c33ff48228f5256ac2e56e097eb20121a6648ee4cca431041670dce` | 6380 |

Fixture đã đổi (hash rút gọn 16 ký tự đầu): `d-unlink…` `248cda9cfe131aa4` · `e-relink…`
`9289f962019f337d` · `g-link-code…` `db813e76477f1be7` · `i-unknown-chat…` `8fa94e8db3007272` ·
`j-concurrent-save…` `1df94cec7d7b4499` · `k-save-then-source-deleted…` `8a27e20ffb561137` ·
`m-three-run-states…` `950b336ba3eb0dad` · `sc10-same-analysis…` `5b6e4f52b7558533`.
Hash đầy đủ lấy bằng `sha256sum acceptance/fixtures/telegram/*.json acceptance/fixtures/ui/*.json`.

⚠️ Card-pin: **7** card trong `agent-tasks/` pin hash cũ của `screens.yaml` / `commands.yaml`.
Thay đổi thuần cách viết tham chiếu, không đổi hợp đồng — nhưng pin cần refresh cùng đợt
`PC10-PIN-FCW4d-20260907` của W7.

## D5. Evidence

| Script | Exit | Kết quả |
| --- | --- | --- |
| `prose_token_gate.py` trên **26 file PC07** | **0** | **121** token → operation, **80** → `entity.column`, **0 không giải được**; 2/2 negative self-test bị bắt |
| `verify_pc07.py` (5 gate) | **0** | `RESULT: PASS (0 fail)` |
| `fixture_field_gate.py` (R4-01, 7 thư mục) | **0** | 0 unresolved; `ui` 2 file / 121 cột |
| `check_actor_edges_all.py` | **0** | **PASS** — trước đây 6 fail ở boundary/collection, nay W2/W4 đã sửa; `ui` 11/11 |

Lệnh tái lập được:
`cd <scratch>/w3 && PYTHONDONTWRITEBYTECODE=1 python3 prose_token_gate.py contracts/ui/screens.yaml contracts/telegram/commands.yaml contracts/telegram/delivery.md contracts/schemas/saved-snapshot.schema.json 'acceptance/fixtures/telegram/*' 'acceptance/fixtures/ui/*'`

## D6. Mối lo

Gate E0-04c coi **mọi** token `a.b` là một khẳng định về operation hoặc cột. Nhiều tham chiếu
hợp lệ không thuộc hai loại đó (đường dẫn mục, thuộc tính read model, trường API ngoài, cấu
trúc fixture). Tôi đã viết lại chúng thành dạng không mơ hồ, nhưng đó là **thích nghi với hình
dạng của gate**, không phải sửa lỗi nội dung. Nếu W6 muốn, một danh mục namespace được khai
báo (`schema:`, `api:`, `§`) sẽ diễn đạt ý định tốt hơn cách né dấu chấm — **CR-PC07-10** gửi
PC09/W6.

## D7. Kết thúc

Lease `LEASE-PC07-e5` nhả lúc 2026-09-07T01:55Z. Không lệnh git mutation, không network, không
file ngoài grant, không `__pycache__`.
