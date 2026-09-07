# Hồ sơ điều phối — Research Radar Pre-code

Baseline điều phối, toàn bộ TASK_PACKET (PC00–PC10, mười một packet audit, hai packet giai đoạn mã và một
template dispatch), các ruling của Coordinator sau mỗi vòng audit, **hai biên bản quyết định của Owner**, bảng
CR hợp nhất của Giai đoạn 1, và sổ tiến độ của Coordinator. Lưu nguyên văn để chuỗi thẩm quyền của phiên còn
kiểm lại được.

Chuỗi thẩm quyền có **năm** authority Owner: `AUTH-OWNER-20260906-01` (cho phép phiên soạn **tài liệu**),
`AUTH-OWNER-20260907-02` (phê chuẩn 25 quyết định — `OWNER-DECISIONS-20260907.md`),
`AUTH-OWNER-20260907-03` (phê chuẩn `ADR-0011` và mở lối vào Giai đoạn 0/1 —
`OWNER-DECISIONS-20260907-02.md`), `AUTH-OWNER-20260907-04` (phê chuẩn `AMD-ENT-owner-01` và
`PROV-PC00-08`, mở lối vào Giai đoạn 2 — `OWNER-DECISIONS-20260907-03.md`) và
`AUTH-OWNER-20260907-05` (đóng cổng chấp nhận probe `§6` mục 2–4 và cấp quyền mạng **hẹp, chỉ đọc tài
liệu** phục vụ `REQ-A6` — `OWNER-DECISIONS-20260907-04.md`). Bảng đầy đủ kèm phạm vi và evidence nằm ở
`agent_profile/registry.json` khóa `authorities` và ở `precode/owner-decisions-02.md` …`-04.md`.

**Một ranh giới cần đọc kỹ.** Grant đầu tiên cho **tài liệu**, không cho mã. Việc ghi mã ở Giai đoạn 0/1 chạy
dưới một ruling của Coordinator suy từ chỉ thị của Owner (`PROV-PC00-08`), **vẫn `PROVISIONAL`**, với rủi ro
còn lại đã ghi: lease trong hai thư mục này là **kỷ luật bằng thông điệp**, không có cưỡng chế ở mức hệ điều
hành.

## Vị trí của tập hồ sơ này trong chuỗi bằng chứng

**Những bản ghi này ra đời SAU lần freeze `FC-W4` epoch 9 mà `A2-R6` đã audit.** Vì vậy chúng **không** nằm trong
bất kỳ candidate manifest nào đã được audit, và **không** được coi là một phần của candidate đã đóng băng.

Đó không phải thiếu sót mà là ràng buộc của giao thức: `protocol.md` §6 nói rõ *"Persist audit report là new
evidence artifact trong packaging phase; không chèn report vào manifest mà report đang ký."* Một báo cáo không
thể nằm trong chính snapshot mà nó ký, và một manifest không thể chứa chính nó. Nếu về sau có một epoch mới,
epoch đó có thể bao gồm thư mục này như **bằng chứng** (role `EVIDENCE`), không phải như candidate.

Thư mục được bổ sung **sáu** lần: `PKT-PC00-FIX9` chép hồ sơ tới epoch 7, `PKT-PC00-FIX12` chép tiếp tới
epoch 9, `PKT-PC00-FIX18` chép mười file của giai đoạn mã, `PKT-PC00-FIX19` chép lại sổ tiến độ trước khi
commit, `PKT-PC00-FIX24` chép hai biên bản Owner của Giai đoạn 2, và `PKT-PC00-FIX25` chép **hai file dựng
lại từ transcript** để đóng `CR-PC00-30` (xem "Cách đọc"). **Ba lần giữa đều thay** bản
`coordinator-ledger.md` bằng bản mới hơn; hash mỗi bản bị thay được ghi ngay trong hàng của nó
(`PKT-PC00-FIX24` **không** chép lại sổ — xem "Cách đọc"). Mỗi lần chép đều `cmp`-verified và hash được tính
lại sau khi chép.

**Mười bản ghi mới nhất ra đời SAU `FC-P1` epoch 3 — epoch mà `A3-R3` audit; sổ tiến độ hiện tại còn muộn hơn
`FC-P1` epoch 4.** Chúng nằm **ngoài mọi manifest đã được audit**, kể cả manifest mới nhất, đúng như chín bản
trước đó nằm ngoài `FC-W4` epoch 9.

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
| `A3-code-review-packet.md` | TASK_PACKET cho `auditor-A3`, vòng 1 — audit **code** đầu tiên (`FC-P1` epoch 1) | `670da439c78156c3af4a48de2e382a1f14d1cf3b4f2f3f66f74e8e28bef5f218` | 3951 |
| `A3-r2-packet.md` | TASK_PACKET cho `auditor-A3`, vòng 2 — xác minh `F-A3R1-*` (`FC-P1` epoch 2) | `e55841a9b22b56fefbca24bebdab5bd532ac063125c41f90148e538097a69670` | 3309 |
| `A3-r3-packet.md` | TASK_PACKET cho `auditor-A3`, vòng 3 — xác minh `F-A3R2-*` + đăng ký của PC09 (`FC-P1` epoch 3) | `8f2fe8e7f0b3b41fdfae4a90c74d8ead9d43fb93ba625a2fac1b64920e72bd82` | 2444 |
| `A3-p2-r1-packet.md` ⚠ | TASK_PACKET cho `auditor-A3`, vòng Giai đoạn 2 (`FC-P2`) — **DỰNG LẠI TỪ TRANSCRIPT**, không phải bản soạn trước khi dispatch; xem "Cách đọc" | `0994854f2c50ecd793db6d266516a0e85dac7a3e5906e7ced105e4d4a2e5ed09` | 3700 |
| `ADR-0011-frameworks-ruling.md` | Ruling của Coordinator chọn framework và toolchain cho stack B, dưới ủy quyền của Owner ("You pick, record as ADR") — bản gốc sinh ra `ADR-0011`. **Xem erratum ở "Cách đọc"** | `09050e65a0c1d6f16fb5463fe8fde1a567cefc9792b1c665ed8c04b2c660555f` | 4487 |
| `FIX-A1R1-rulings.md` | Ruling R-01..R-09 sau AUDIT_REPORT A1-R1 | `94cdf17b1922dbff89273a316bb9e71e218f50d9f253a5f87cbae4769d1e1ff4` | 6380 |
| `FIX-A3R1-rulings.md` | Ruling sau AUDIT_REPORT `A3-R1` — vòng ruling **đầu tiên về code**, gồm cả amendment `AMD-ENT-owner-01` | `ec3805a9682fe16784671258721a7337f386d82279e5a75426ebefaac004997d` | 4678 |
| `FIX-R5-rulings.md` | Ruling sau AUDIT_REPORT `A2-R5` | `e2a0e26eb6686112aa8de5bed9c2a04adf1732555b005a3d8c4d98e7b0f12beb` | 3680 |
| `FIX3-rulings.md` | Ruling đợt FIX3 (sau A1-R2 và các CR của PC03/PC04/PC08) | `8e3bc78ba76562d11731a590fd516d3df781f191f4a6f39b3bb71fd1d5072f14` | 4977 |
| `FIX4-rulings.md` | Ruling R4-01..R4-04 sau A1-R3 | `66fa366bcea8b4a1d3746a40957dddad133f64cb147e2802950905821fdc11ee` | 2689 |
| `FIX5-rulings.md` | Ruling R5-01..R5-08 | `077451e71db38d160f6be4fc484d3856d7a90f321755eae2d702717268e62d24` | 4425 |
| `FIX6-rulings.md` | Ruling sau A2-R1 (F-01..F-11) | `5efa475ff24a0f2dc035baaf9b10932c8eb71b9dc8fc767984714412ac9f69d0` | 4069 |
| `FIX7-rulings.md` | Ruling đợt FIX7 | `0a4960a4ba9819ec400eb8e4023b2c04f5910e8868812036ddac8fc825e0861a` | 2183 |
| `OWNER-DECISIONS-20260907.md` | **Biên bản quyết định của Owner** ngày 2026-09-07 (`OD-20260907-01`, authority `AUTH-OWNER-20260907-02`) — bản gốc do Coordinator phát; bản chuyển ngữ đầy đủ ở `precode/owner-decisions.md` | `31d496a04dc221b030b51f64da2e18a5231f219cbcd011467cf329d1208572c4` | 4750 |
| `OWNER-DECISIONS-20260907-02.md` | **Biên bản quyết định của Owner, vòng hai** (`OD-20260907-02`, authority `AUTH-OWNER-20260907-03`): phê chuẩn `ADR-0011` và mở lối vào Giai đoạn 0/1 — bản gốc do Coordinator phát; bản chuyển ngữ đầy đủ ở `precode/owner-decisions-02.md` | `599d8427870ebdfc921d1ad105e7bf9e45b1f5b62eeb5f66f0dd31e31477245f` | 2455 |
| `OWNER-DECISIONS-20260907-03.md` | **Biên bản quyết định của Owner, vòng ba** (`OD-20260907-03`, authority `AUTH-OWNER-20260907-04`): phê chuẩn `AMD-ENT-owner-01` và `PROV-PC00-08`, mở lối vào **Giai đoạn 2** — bản gốc; bản chuyển ngữ ở `precode/owner-decisions-03.md` | `d3cee88806ad9e5b615dc39ce0e215eefdeda2945c4e2d488c02f818f6e6fb20` | 1844 |
| `OWNER-DECISIONS-20260907-04.md` | **Biên bản quyết định của Owner, vòng bốn** (`OD-20260907-04`, authority `AUTH-OWNER-20260907-05`): đóng cổng chấp nhận probe `§6` mục 2–4 và cấp quyền mạng **một lần, hẹp theo tên miền, chỉ đọc tài liệu** cho `REQ-A6` — bản gốc; bản chuyển ngữ ở `precode/owner-decisions-04.md` | `74dfe407f9ae2136b3108edf2ccc5ef1498c873cba5cc75096c032040bba92e7` | 1971 |
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
| `PC09-PHASE1-packet.md` | TASK_PACKET `PKT-PC09-P1` — đăng ký bằng chứng Giai đoạn 0/1, cập nhật gate và luật E0 | `38cbf318942e056d934ed1231497b78ab1934a09c27d26f39e108d32f6fad51f` | 3933 |
| `PC10-packet.md` | TASK_PACKET PC10 — task card cho coding, bàn giao bộ hợp đồng | `ebb5cee9c6c61acc07be033092c4257056592e553fe8df6c9e89880b245cac32` | 5642 |
| `PHASE0-skeleton-packet.md` | TASK_PACKET `PKT-P0-SKELETON` — dựng bộ khung repo của Giai đoạn 0 (bảy trong tám cây; `tools/` nằm ngoài write set) | `ad76109b3130d3035ea3522c89ead65988314132a903e9c858dcc9a43303a513` | 8193 |
| `PHASE1-card-dispatch-template.md` | Template dispatch dùng chung cho bốn card Giai đoạn 1 | `70630dfc6ab4718da09c5763dc0ec3803578836cb81b8cd71e9ff42cb3a1cc5f` | 3988 |
| `PHASE2-dispatch-log.md` ⚠ | **Nhật ký dispatch của Giai đoạn 2** — mọi packet đã phát trong phase, theo thứ tự thời gian, kèm ghi chú của Coordinator về khoảng trống và vì sao bản dựng lại này đóng nó. **DỰNG LẠI TỪ TRANSCRIPT**, không phải bản soạn trước khi dispatch; xem "Cách đọc" | `2c23d63f7f2c196bc8a367ea97bedca9d2d7ac43093bbb19754338e476633640` | 22150 |
| `PURGE-LIST-ruling.md` | Ruling chốt danh sách loại trừ của `data.purge_all` (theo mục 24 của biên bản Owner) | `6c320e312efb9ba9f68b3480f01052cb47f9c01852a6baf0af001c30854fe5b2` | 2520 |
| `phase1-cr-consolidated.txt` | Bảng hợp nhất các CR do Giai đoạn 0 và bốn card Giai đoạn 1 phát ra, gom từ các handoff | `3c6433db66e10a510820c29d37dfbdac82d934564e12280eb387619666bea4a3` | 4452 |
| `coordinator-ledger.md` | Sổ tiến độ của Coordinator (bản gốc `progress.md` trong scratchpad): dòng thời gian dispatch, freeze, audit và ruling của toàn phiên. **Bản chép ở `PKT-PC00-FIX19`, thay thế bản của `PKT-PC00-FIX18`** (`0a1187c5ac1725ad316ef78d65c56349df985d3adb9da4f061212fc01d9dc30a`, 52809 byte — bản đó dừng trước `A3-R4`, bản này chạy tới `FC-P1` epoch 4). Chuỗi bản bị thay: `PKT-PC00-FIX12` (`0369031b…`, 39468, dừng ở `FC-W4` epoch 9) và `PKT-PC00-FIX9` (`a8a7d319…`, dừng ở epoch 7) | `4e540086e1928ca315c727c247ff2f77e30a98525a2926730f2bd634268e8232` | 53839 |

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
  độc lập. Bản hiện tại chép ở `PKT-PC00-FIX19` và **thay thế** bản của `PKT-PC00-FIX18` (`0a1187c5…`, 52809),
  bản đó thay bản của `PKT-PC00-FIX12` (`0369031b…`, dừng ở `FC-W4` epoch 9), bản đó lại thay bản của
  `PKT-PC00-FIX9` (`a8a7d319…`, dừng ở epoch 7). Chỉ **một** bản được giữ mỗi lần; lịch sử các bản cũ nằm
  trong git và trong hash ghi ở đây.
- **Sổ này là một file ĐANG SỐNG ở phía nguồn.** Coordinator vẫn ghi tiếp `progress.md` trong lúc các gói
  packaging chạy, và điều đó **đã xảy ra thật**: ở `PKT-PC00-FIX18`, bản chép đầu (`fd0116d3…`, 52444 byte)
  lỗi thời trong vòng vài phút và phải chép lại (`0a1187c5…`, 52809) — rồi chính bản đó cũng lỗi thời trước
  `PKT-PC00-FIX19`. Bản hiện tại được chép lúc **2026-09-07T12:45Z**, `cmp`-verified ngay sau đó, với hash
  nguồn giống nhau **trước và sau** lần chép. Nó là một **ảnh chụp tại một thời điểm**, không phải bản mới
  nhất, và gần như chắc chắn đã tụt lại ngay khi bạn đọc dòng này. Muốn bản mới nhất thì đọc nguồn, không đọc
  bản chép. Điều bản chép bảo đảm là: **byte ở đây đúng bằng byte của nguồn tại 12:45Z**, không hơn.
  **`PKT-PC00-FIX24` cố ý KHÔNG chép lại sổ**: lease của gói đó chỉ cho **tạo file mới** trong hai thư mục
  này, và thay `coordinator-ledger.md` là sửa một file đã có. Vì vậy bản sổ hiện tại vẫn dừng ở `FC-P1`
  epoch 4 và **không** chứa dòng thời gian của Giai đoạn 2.
- **`OWNER-DECISIONS-20260907.md` là văn bản ràng buộc**, không phải một ruling: nó là biên bản của Owner.
  `precode/owner-decisions.md` chép lại đầy đủ 25 mục kèm phần PC00 ghi rõ những gì quyết định này **không**
  làm (`REQ-OQ03` vẫn mở; mọi mục `KC` vẫn `KC`; không finding audit nào bị đóng).
- **ERRATUM — `ADR-0011-frameworks-ruling.md` (`CR-PC00-19`).** Bản ruling này khai rằng **cả bảy** thư mục
  của bố cục repo "đã được `agent-tasks/README.md` §5.3 khai". Điều đó **sai** tại thời điểm ruling được viết:
  §5.3 khi ấy khai **sáu**, và `shared/rr_contracts/` được giới thiệu lần đầu tại chính `ADR-0011`. Bố cục
  cũng đã đổi từ đó: nay là **tám** cây (thêm `tools/`) và `tests/` không có `unit/`. Quy kết nguồn đã được
  sửa ở `precode/adr/ADR-0011-frameworks-and-toolchain.md` qua `PKT-PC00-FIX14` (`F-A2R7-04`) và
  `PKT-PC00-FIX17` (`CR-PC10-09`).
  **File trong thư mục này KHÔNG được sửa, và đó là chủ ý:** nó là bản sao nguyên văn `cmp`-verified của một
  văn bản lịch sử. Sửa một bản lưu trữ để nó "đúng hơn" là phá đúng thứ làm cho bản lưu trữ có giá trị. Erratum
  vì vậy sống ở đây, cạnh bản gốc, chứ không nằm trong nó. Khi hai văn bản lệch nhau: **ADR hiện hành thắng**;
  ruling chỉ nói ruling đã nói gì.
- **Nhãn claim trong file `.md` của thư mục này KHÔNG được phép kiểm nào quét (`F-A3R4-01`, LOW, `PARKED`).**
  `A3-R4` chứng minh: `claim_ceiling: PRODUCT_ACCEPTED` đặt trong front-matter một `.md` ở đây thì `E0-12`
  vẫn **PASS**. Ghi chú của `e0_check.py` nói "structured fields are still checked" — đúng cho `.yaml`/`.json`,
  **không** đúng cho front-matter Markdown. Coordinator đã `PARKED` finding này; cải tiến công cụ thuộc
  `CR-PC09-18` ở vòng PC09 kế tiếp. Hệ quả thực tế cho người đọc thư mục này: **đừng tin một nhãn claim nào
  xuất hiện trong các file ở đây** — không có gì kiểm nó. Điều đó ít nguy hiểm hơn vẻ ngoài vì các file này là
  dispatch artefact, nhãn của chúng không mang hiệu lực bằng chứng; nhưng "không mang hiệu lực" là lý do để
  bỏ qua nhãn, **không** phải lý do để tin nó.
- **⚠ HAI file của Giai đoạn 2 là bản DỰNG LẠI TỪ TRANSCRIPT, không phải bản gốc — và khác biệt đó có ý
  nghĩa.** `PHASE2-dispatch-log.md` và `A3-p2-r1-packet.md` được Coordinator viết ra **sau khi** phase kết
  thúc, chép lại từ transcript của phiên. Mọi file khác trong thư mục này được soạn **trước khi** dispatch và
  chép nguyên văn từ đúng bản đã dùng.

  **Chuyện đã xảy ra (`CR-PC00-30`).** Trong Giai đoạn 2, packet được phát bằng `SendMessage` thẳng tới các
  Worker **đang chạy**, không viết ra scratchpad trước — khác mọi vòng của Giai đoạn 0/1. Lượt đóng gói
  `PKT-PC00-FIX24` phát hiện khoảng trống ấy khi tìm file để chép và **không tìm thấy gì**; nó báo cáo thay
  vì dựng lại. `PKT-PC00-FIX25` chép bản dựng lại do Coordinator cung cấp.

  **Bản dựng lại chứng minh được gì, và không chứng minh được gì.** Nó **là** bản ghi tốt nhất hiện có về
  điều đã được phát, và nó khôi phục khả năng đọc lại nội dung packet. Nó **không** chứng minh rằng văn bản
  ấy tồn tại **trước** lúc dispatch, vì nó không tồn tại — không có dấu thời gian độc lập nào ràng buộc nó
  vào thời điểm phát. Với các file khác, thứ tự "soạn → phát → chép" tự nó là một bảo đảm; với hai file này
  thì không. Vì vậy: dùng chúng để **hiểu** Giai đoạn 2 đã được điều phối thế nào; **đừng** dùng chúng làm
  bằng chứng rằng một grant cụ thể đã tồn tại ở một thời điểm cụ thể. Cho việc đó, nguồn mạnh hơn là **biên
  bản Owner** (soạn trước, đã chép) và **những gì handoff của từng Worker trích dẫn lại** — hai thứ độc lập
  với bản dựng lại này.

  **Vì sao khoảng trống xảy ra.** Đây là hệ quả trực tiếp của `PROV-PC00-08`: lease theo dõi bằng thông điệp,
  không có cưỡng chế ở mức hệ điều hành, nên "ghi packet ra đĩa" là một **thói quen** chứ không phải một
  ràng buộc — và một thói quen thì bỏ được mà không có gì báo động. Nếu muốn nó không tái diễn, cách sửa là
  một **guard**, không phải một lời nhắc.
- **Hai file không phải packet cũng không phải ruling.** `phase1-cr-consolidated.txt` là bảng gom CR từ các
  handoff — một công cụ làm việc, không phải văn bản có thẩm quyền; trạng thái CR chuẩn sống ở
  `precode/review.md` §12. `PHASE1-card-dispatch-template.md` là **template**, không phải một packet đã phát:
  nó không có lease, không có tập ghi cụ thể, và không cấp quyền cho ai.
- **Nguồn đối chiếu:** `evidence/audits/` giữ báo cáo và manifest mà các ruling này phản hồi;
  `evidence/handoffs/` giữ HANDOFF của từng Worker.
