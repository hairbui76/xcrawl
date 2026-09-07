# Hồ sơ điều phối — Research Radar Pre-code

Baseline điều phối, toàn bộ TASK_PACKET (PC00–PC10 và tám packet audit), các ruling của Coordinator sau mỗi
vòng audit, **biên bản quyết định của Owner**, và sổ tiến độ của Coordinator. Lưu nguyên văn để chuỗi thẩm
quyền của phiên còn kiểm lại được.

Chuỗi thẩm quyền có **hai** authority Owner: `AUTH-OWNER-20260906-01` (cho phép phiên soạn tài liệu) và
`AUTH-OWNER-20260907-02` (phê chuẩn 25 quyết định — xem `OWNER-DECISIONS-20260907.md`).

## Vị trí của tập hồ sơ này trong chuỗi bằng chứng

**Những bản ghi này ra đời SAU lần freeze `FC-W4` epoch 9 mà `A2-R6` đã audit.** Vì vậy chúng **không** nằm trong
bất kỳ candidate manifest nào đã được audit, và **không** được coi là một phần của candidate đã đóng băng.

Đó không phải thiếu sót mà là ràng buộc của giao thức: `protocol.md` §6 nói rõ *"Persist audit report là new
evidence artifact trong packaging phase; không chèn report vào manifest mà report đang ký."* Một báo cáo không
thể nằm trong chính snapshot mà nó ký, và một manifest không thể chứa chính nó. Nếu về sau có một epoch mới,
epoch đó có thể bao gồm thư mục này như **bằng chứng** (role `EVIDENCE`), không phải như candidate.

Thư mục được bổ sung hai lần: `PKT-PC00-FIX9` chép hồ sơ tới epoch 7, `PKT-PC00-FIX12` chép tiếp tới epoch 9
và **thay** bản `coordinator-ledger.md` cũ bằng bản mới hơn (bản cũ dừng ở epoch 7). Mỗi lần chép đều
`cmp`-verified và hash được tính lại sau khi chép.

**Nội dung là bản sao nguyên văn, không sửa một byte.** Mọi file ở đây được `cp` từ scratchpad của phiên và
đã được `cmp` xác nhận byte-identical; SHA-256 dưới bảng được tính **sau khi chép**. Không file nào trong thư
mục này được biên tập, tóm tắt hay sửa lỗi chính tả — kể cả khi nội dung của chúng nói về công việc của chính
người chép. Đọc chúng như dữ liệu lịch sử, không như tài liệu đang sống.

## Danh mục

| File | Là gì | SHA-256 | Bytes |
| --- | --- | --- | --- |
| `00-coordination-baseline.md` | Baseline điều phối của phiên: chuỗi thẩm quyền, nguồn đã pin, quy ước ID, quyết định PROVISIONAL của Coordinator (§5), hợp đồng handoff, stop gate. **Ràng buộc với mọi packet.** | `0759ff6422158611af7850f9f475a0732a82998f35d13107ae009fba2ccb9e78` | 14132 |
| `A1-audit-1-packet.md` | TASK_PACKET cho `auditor-A1`, vòng 1 (FC-W1) | `31c98616307c818e174f018c0faff26d72646bb7b48f6d72e850087570443cfb` | 4773 |
| `A1-audit-2-packet.md` | TASK_PACKET cho `auditor-A1`, vòng 2 (FC-W2) | `fd5c135e9232154df43f0675e08d95f88dec50370a7078fe905341bb9ee6a2bb` | 4690 |
| `A1-audit-3-packet.md` | TASK_PACKET cho `auditor-A1`, vòng 3 (FC-W3) | `1c03d56eb00702e87357949ac6890e712d943c6f5c3e1ff01cf36b5ce2e3ceef` | 5988 |
| `A2-final-audit-packet.md` | TASK_PACKET cho `auditor-A2`, audit cuối (FC-W4 epoch 4) | `fd97c28794b8b32240b6de92c52534276c89a88d24e68a6d34c103f92f8510a3` | 6190 |
| `A2-r6-packet.md` | TASK_PACKET cho `auditor-A2` — re-review có phạm vi (epoch 9) | `d6cc9f20c2800dd21ccab35c14facebb71992760c663c7e2242bcd32dbca39f6` | 2553 |
| `A2-ratification-verify-packet.md` | TASK_PACKET cho `auditor-A2` — xác minh phần ratification (epoch 8) | `ad93f96eaf5f4488bb16376d61e9c097cf60e0a4fb08a27282d2b06f3b23c693` | 3981 |
| `A2-rereview-packet.md` | TASK_PACKET cho `auditor-A2`, re-review có phạm vi (epoch 6/7) | `0731599209e4c61c4d7d07d2b5d37dcd88bdae9cb507f707b03a0480d71641ae` | 2005 |
| `A2-verify-packet.md` | TASK_PACKET cho `auditor-A2`, xác minh remedy (epoch 5) | `a6a222d569afd1eb647fefcbbb12cd5ae58ae2483fd8043a4b24b8758e503054` | 2733 |
| `FIX-A1R1-rulings.md` | Ruling R-01..R-09 sau AUDIT_REPORT A1-R1 | `94cdf17b1922dbff89273a316bb9e71e218f50d9f253a5f87cbae4769d1e1ff4` | 6380 |
| `FIX-R5-rulings.md` | Ruling sau AUDIT_REPORT `A2-R5` | `e2a0e26eb6686112aa8de5bed9c2a04adf1732555b005a3d8c4d98e7b0f12beb` | 3680 |
| `FIX3-rulings.md` | Ruling đợt FIX3 (sau A1-R2 và các CR của PC03/PC04/PC08) | `8e3bc78ba76562d11731a590fd516d3df781f191f4a6f39b3bb71fd1d5072f14` | 4977 |
| `FIX4-rulings.md` | Ruling R4-01..R4-04 sau A1-R3 | `66fa366bcea8b4a1d3746a40957dddad133f64cb147e2802950905821fdc11ee` | 2689 |
| `FIX5-rulings.md` | Ruling R5-01..R5-08 | `077451e71db38d160f6be4fc484d3856d7a90f321755eae2d702717268e62d24` | 4425 |
| `FIX6-rulings.md` | Ruling sau A2-R1 (F-01..F-11) | `5efa475ff24a0f2dc035baaf9b10932c8eb71b9dc8fc767984714412ac9f69d0` | 4069 |
| `FIX7-rulings.md` | Ruling đợt FIX7 | `0a4960a4ba9819ec400eb8e4023b2c04f5910e8868812036ddac8fc825e0861a` | 2183 |
| `OWNER-DECISIONS-20260907.md` | **Biên bản quyết định của Owner** ngày 2026-09-07 (`OD-20260907-01`, authority `AUTH-OWNER-20260907-02`) — bản gốc do Coordinator phát; bản chuyển ngữ đầy đủ ở `precode/owner-decisions.md` | `31d496a04dc221b030b51f64da2e18a5231f219cbcd011467cf329d1208572c4` | 4750 |
| `PC00-packet.md` | TASK_PACKET PC00 — khóa nguồn, nguyên tử hóa yêu cầu, xử lý mâu thuẫn | `0b474a977901722c649bea154b61689af6d967b59dbbe952d942a426af7f0aa9` | 6273 |
| `PC01-packet.md` | TASK_PACKET PC01 — topology, ownership, capability | `cbe6da783a6492510fa7af567e034746d4cfb63245fea8a759ad201a0957c54f` | 6309 |
| `PC02-packet.md` | TASK_PACKET PC02 — identity, entity, transaction | `e51760b57aae6b25e096613e02fecd088fa1b48e4b53ae80941c1b2ab9b3c52e` | 6318 |
| `PC03-packet.md` | TASK_PACKET PC03 — scheduler, lease, checkpoint, state machine | `fc357687b62de5572572b90c57493a80e2a15d523a0e0964631c8d8b3eb981f0` | 8586 |
| `PC04-packet.md` | TASK_PACKET PC04 — thời gian, tag, coverage, chọn hướng nghiên cứu | `b266757fc8d4fb449138c4db5af992cc6d51027e48ca33bb0c00e4109a76d48d` | 8489 |
| `PC05-packet.md` | TASK_PACKET PC05 — collector và paper connector, probe khả thi | `6c4bf2c340b4f6d139d774ae5790319ec1b4eaab4be92bd611d23e4a4398c8c3` | 7744 |
| `PC06-packet.md` | TASK_PACKET PC06 — AI API/CLI/ACP và grounding | `e7cb509af24f4dc4c1fc5714eec04cd2607da92c9b49c6a463ac205b334af3f1` | 8182 |
| `PC07-packet.md` | TASK_PACKET PC07 — app, Save, Telegram delivery | `2d0690a81b9889c751cbc4decf459548111e7a83fb27dac9a9befa0a1d445138` | 8269 |
| `PC08-packet.md` | TASK_PACKET PC08 — secrets, Internet boundary, backup, recovery | `6845425e14d5b99fa391ce666fe33dc99eb5c4a08f10f88a5dde5672934769a7` | 7982 |
| `PC09-packet.md` | TASK_PACKET PC09 — oracle, traceability, evidence, readiness | `a8eff8c99df5238e96a70bd9aee30400204df07ed15612cec4d6960f6d37ed43` | 6895 |
| `PC10-packet.md` | TASK_PACKET PC10 — task card cho coding, bàn giao bộ hợp đồng | `ebb5cee9c6c61acc07be033092c4257056592e553fe8df6c9e89880b245cac32` | 5642 |
| `PURGE-LIST-ruling.md` | Ruling chốt danh sách loại trừ của `data.purge_all` (theo mục 24 của biên bản Owner) | `6c320e312efb9ba9f68b3480f01052cb47f9c01852a6baf0af001c30854fe5b2` | 2520 |
| `coordinator-ledger.md` | Sổ tiến độ của Coordinator (bản gốc `progress.md` trong scratchpad): dòng thời gian dispatch, freeze, audit và ruling của toàn phiên. **Bản 2026-09-07T12:33Z, thay thế bản chép ở PKT-PC00-FIX9** (`a8a7d319…`) — bản cũ dừng ở epoch 7, bản này chạy tới epoch 9 | `0369031b73e7550ec4fe7d63e8d206049a560528d3b97d8a5eca6e4eb6db4ac5` | 39468 |

## Cách đọc

- **`00-coordination-baseline.md` là văn bản ràng buộc**, không phải ghi chú: nó khai chuỗi thẩm quyền
  (`AUTH-OWNER-20260906-01`), hai file nguồn đã pin kèm SHA-256, quy ước ID, các quyết định `PROVISIONAL` của
  Coordinator cho B01–B17 (§5), hợp đồng handoff (§4) và stop gate (§6). Mọi packet đều là con của nó.
- **Packet không phải là quyền ghi filesystem.** Chúng chỉ mô tả grant; ở chế độ `DOCUMENTARY_DRAFT` không có
  enforcement ở mức hệ điều hành, và điều đó được khai rõ trong chính baseline.
- **Ruling không đóng finding.** Mỗi file `FIX*-rulings.md` chuyển finding từ `OPEN` sang `FIX_PROPOSED` và giao
  việc; việc xác minh thuộc auditor ở epoch kế tiếp.
- **`coordinator-ledger.md`** là bản sao của `progress.md`: dòng thời gian dispatch → freeze → audit → ruling của
  cả phiên. Đây là bản ghi *do Coordinator viết*, nên nó là lời tự thuật của một bên, không phải bằng chứng
  độc lập. Bản hiện tại chép ở `PKT-PC00-FIX12` và **thay thế** bản chép ở `PKT-PC00-FIX9` (`a8a7d319…`,
  dừng ở epoch 7).
- **`OWNER-DECISIONS-20260907.md` là văn bản ràng buộc**, không phải một ruling: nó là biên bản của Owner.
  `precode/owner-decisions.md` chép lại đầy đủ 25 mục kèm phần PC00 ghi rõ những gì quyết định này **không**
  làm (`REQ-OQ03` vẫn mở; mọi mục `KC` vẫn `KC`; không finding audit nào bị đóng).
- **Nguồn đối chiếu:** `evidence/audits/` giữ báo cáo và manifest mà các ruling này phản hồi;
  `evidence/handoffs/` giữ HANDOFF của từng Worker.
