# Hồ sơ audit độc lập — Research Radar Pre-code

**Mười chín** AUDIT_REPORT của **ba** auditor độc lập (`auditor-A1` ×3, `auditor-A2` ×7, `auditor-A3` ×9) và
**mười tám** FROZEN_CANDIDATE manifest, được lưu lại nguyên văn để chúng không mất cùng phiên làm việc. Chuỗi
epoch: `FC-W1` 1 → `FC-W2` 2 → `FC-W3` 3 → `FC-W4` 4, 5, 6, 7, **8 (epoch phê chuẩn của Owner)**, **9 (epoch
cuối của baseline hợp đồng)** → **`FC-P1` 1, 2, 3 và 4 (Giai đoạn 0/1)** → **`FC-P2` (Giai đoạn 2)** →
**`FC-P3` 1 và 2 (Giai đoạn 3 + Giai đoạn 5 văn bản thuần)** → **`FC-P4` 1 và 2 (Giai đoạn 4 + Giai đoạn 6)**.

**`A2-R7` là ngoại lệ về hình dạng, không phải về hiệu lực.** Nó là báo cáo duy nhất **không có freeze
manifest**: Coordinator dispatch nó lúc 18 task card đang được re-pin đồng thời, nên thay vì một manifest,
`auditor-A2` hash hai văn bản trong phạm vi ở **đầu** và **cuối** vòng và ghi cả hai giá trị. Điều đó chứng
minh được cùng một thứ mà một manifest chứng minh cho một phạm vi hai file — không có drift trong lúc review —
nhưng nó **không** phải một epoch trong chuỗi trên, nên đừng tìm `FC-` tương ứng.

**Chín báo cáo `A3-*` khác mọi báo cáo trước chúng ở một điểm cần nói rõ:** mười báo cáo A1/A2 đều ở mức bằng
chứng **E0** — kiểm tính nhất quán tĩnh của văn bản hợp đồng, không có gì được chạy. Chín báo cáo A3 audit
**code đang chạy**: auditor tự cài từ lockfile, tự chạy toàn bộ bộ test, tự dựng lại cơ sở dữ liệu dưới bốn
thứ tự duyệt migration, và tự viết harness riêng thay vì tin bộ test của Worker. `A3-R3` đi thêm một bước:
nó **mutation-test** chính các phép kiểm mà Worker viết ra — bỏ một cột đã khai, thêm một cột chưa khai, khai
sai nullability — để xem guard có thật sự bắt hay không, thay vì tin rằng một test xanh nghĩa là test có tác
dụng. Verdict của chúng vì vậy nói về hành vi, không chỉ về văn bản — trong đúng phạm vi §5 của mỗi bản nêu.

## Vị trí của tập hồ sơ này trong chuỗi bằng chứng

**Những bản ghi này ra đời SAU lần freeze `FC-W4` epoch 9 mà `A2-R6` đã audit.** Vì vậy chúng **không** nằm trong
bất kỳ candidate manifest nào đã được audit, và **không** được coi là một phần của candidate đã đóng băng.

Đó không phải thiếu sót mà là ràng buộc của giao thức: `protocol.md` §6 nói rõ *"Persist audit report là new
evidence artifact trong packaging phase; không chèn report vào manifest mà report đang ký."* Một báo cáo không
thể nằm trong chính snapshot mà nó ký, và một manifest không thể chứa chính nó. Nếu về sau có một epoch mới,
epoch đó có thể bao gồm thư mục này như **bằng chứng** (role `EVIDENCE`), không phải như candidate.

Thư mục được bổ sung **sáu** lần: `PKT-PC00-FIX9` chép hồ sơ tới epoch 7, `PKT-PC00-FIX12` chép tiếp tới
epoch 9, `PKT-PC00-FIX18` chép `A2-R7`, `A3-R3` cùng ba manifest `FC-P1`, `PKT-PC00-FIX19` chép `A3-R4` cùng
manifest epoch 4, `PKT-PC00-FIX24` chép `A3-P2-R1` cùng manifest `FC-P2`, `PKT-PC00-FIX29` chép **hai**
báo cáo `A3-P3-*` cùng **hai** manifest `FC-P3`, và `PKT-PC00-FIX31` chép **hai** báo cáo `A3-P4-*` cùng **hai** manifest `FC-P4` (gói này chạy **hai
lượt**: lượt đầu khi mới có epoch 1, lượt sau khi `A3-P4-R2` land — xem "Cách đọc"). Mỗi lần chép đều
`cmp`-verified và hash được tính lại sau khi chép.

**Bảy bản ghi mới nhất ra đời SAU epoch mà chính chúng audit** (`FC-P1` epoch 3 cho `A3-R3`, epoch 4 cho
`A3-R4`).** Chúng vì vậy nằm **ngoài
mọi manifest đã được audit**, kể cả manifest mới nhất. `A2-R7-report.md` là một trường hợp riêng: nó lẽ ra
phải được lưu ở vòng packaging trước (`CR-PC09-15`) và đã bị bỏ sót; nay đã có, nhưng việc nó đến muộn
**không** làm nó thuộc về epoch nào — nó vẫn là bằng chứng ngoài manifest như bốn file kia.

**Nội dung là bản sao nguyên văn, không sửa một byte.** Mọi file ở đây được `cp` từ scratchpad của phiên và
đã được `cmp` xác nhận byte-identical; SHA-256 dưới bảng được tính **sau khi chép**. Không file nào trong thư
mục này được biên tập, tóm tắt hay sửa lỗi chính tả — kể cả khi nội dung của chúng nói về công việc của chính
người chép. Đọc chúng như dữ liệu lịch sử, không như tài liệu đang sống.

## Danh mục

| File | Là gì | Candidate / epoch | SHA-256 | Bytes |
| --- | --- | --- | --- | --- |
| `A1-R1-report.md` | AUDIT_REPORT `PKT-A1-R1` — audit độc lập đầu tiên, phạm vi PC00–PC02 | `FC-W1` epoch 1 | `2bc67e273e9da7e552b03ae72e041ee48b5db326d31051c3f65394fa44fb5e70` | 42864 |
| `A1-R2-report.md` | AUDIT_REPORT `PKT-A1-R2` — kiểm lại F-A1R1-01..09 cộng PC03/PC04 | `FC-W2` epoch 2 | `0a185f0f1266e7cb995d2b7ff516cb35ff14eac56c25f06cee4f16d142ab6b33` | 37282 |
| `A1-R3-report.md` | AUDIT_REPORT `PKT-A1-R3` — kiểm lại F-A1R2, cộng PC05–PC07 | `FC-W3` epoch 3 | `7bfdc3189471bb543caa5261d239d736becf04ba6b80daef4440a10819011e37` | 28868 |
| `A2-R1-report.md` | AUDIT_REPORT `A2-R1` — audit độc lập cuối cùng của toàn bộ Pre-code baseline, reviewer thứ hai | `FC-W4` epoch 4 | `6c05b288e6878b0a6f858bc6166ea53b36160991a2baea5a940e2b2db411f898` | 54343 |
| `A2-R2-report.md` | AUDIT_REPORT `A2-R2` — xác minh F-A2R1-01..11 trên toàn bộ baseline | `FC-W4` epoch 5 | `3dee029a8db53a96e6349c54e901b6ad57bc433b4ffebd68b9792556c57c184b` | 31576 |
| `A2-R3-report.md` | AUDIT_REPORT `A2-R3` — re-review có phạm vi của F-A2R2-01..04 | `FC-W4` epoch 6 | `6fed67439f13c0a5c50c010ef666d885aca9e6f81f0152e67142b1b7aeb08cad` | 21834 |
| `A2-R4-report.md` | AUDIT_REPORT `A2-R4` — re-review có phạm vi của F-A2R3-01..03 | `FC-W4` epoch 7 | `a5d341952211aa9210c225defc0e1b299ac1bca06b054350d410a98c7d7827a1` | 10512 |
| `A2-R5-report.md` | AUDIT_REPORT `A2-R5` — xác minh các thay đổi do Owner phê chuẩn (`OD-20260907-01`) | `FC-W4` epoch 8 (epoch phê chuẩn) | `64058e72331d19d4353c7c8f46622cd860f7d00db643cf9ecd790811e0fcc0de` | 31201 |
| `A2-R6-report.md` | AUDIT_REPORT `A2-R6` — re-review có phạm vi của F-A2R5-01..07 | `FC-W4` epoch 9 | `305084491a439c6d526883317e18f4f7f24b71ff03f5295f760206ce7d401530` | 18894 |
| `A3-R1-report.md` | AUDIT_REPORT `A3-R1` — audit độc lập ĐẦU TIÊN của **code**: Giai đoạn 0 (skeleton) + bốn task card Giai đoạn 1. Verdict tổng **FAIL** trên hai finding HIGH | `FC-P1` epoch 1 | `02c9d541dfd1d8dbb7f56391a4fc5e1de9e7a81d310ce4ff08604717763ab498` | 32850 |
| `A3-R2-report.md` | AUDIT_REPORT `A3-R2` — re-review có phạm vi của `F-A3R1-01..15` cộng amendment `AMD-ENT-owner-01`. Verdict tổng **PASS** cho phạm vi review; bốn finding mới `F-A3R2-01..04` | `FC-P1` epoch 2 | `75f2ac45a1c35a09f3e93df63cbd7480fdd51189b94951b1983cb3de8db2089d` | 20114 |
| `A2-R7-report.md` | AUDIT_REPORT `A2-R7` — re-review có phạm vi hai văn bản (`docs/master-plan.md`, `ADR-0011`). **Không có freeze manifest**: hai file được hash đầu và cuối vòng thay cho manifest. Sinh ra `F-A2R7-04` và `F-A2R7-05`, hai finding đã được `PKT-PC00-FIX14` xử lý | *(không epoch — xem ghi chú ở trên)* | `12b0dbcc39919cc4c74bccaae24670ea480660ab1a945d06a0bc2ab28dd74880` | 17667 |
| `A3-R3-report.md` | AUDIT_REPORT `A3-R3` — xác minh có phạm vi `F-A3R2-01..04` cộng phần đăng ký của PC09. Verdict tổng **PASS**; `F-A3R2-02` được xác minh bằng **mutation test** trên chính guard của Worker; ba finding mới `F-A3R3-01..03`, trong đó `F-A3R3-01` là một lỗ thật trong phép kiểm E0-12 | `FC-P1` epoch 3 | `5d9a4ce609f24b785f7d2d5753602f5f52008e01bc01886e2667807adfce6284` | 14574 |
| `A3-R4-report.md` | AUDIT_REPORT `A3-R4` — xác minh có phạm vi `F-A3R3-01..03`. Verdict tổng **PASS**, cả ba VERIFIED bằng tái lập của chính auditor; **một** finding mới `F-A3R4-01` (LOW) | `FC-P1` epoch 4 | `1bb41470b4730a25e199be3f367da24b51d89856248f35a681cb61c9c66bf08e` | 8672 |
| `A3-P4-R1-report.md` | AUDIT_REPORT `A3-P4-R1` — audit độc lập **Giai đoạn 4 (M4/M5)** cộng **Giai đoạn 6 (M7/M8)**, sáu card. Verdict **PASS CÓ MỘT ĐIỀU KIỆN PHẠM VI** (`F-A3-P4-01`, MEDIUM): `TC-report-coverage-publish-cas` **không được** mang `REQ-D29`/`I07` là đã phủ trong khi `CR-TC-BACKFILL-09` chưa được xử lý và không được nêu trong handoff của chính nó — auditor gọi đó là **sửa disposition và phạm vi, không phải sự cố mã**. Hai oracle cấu trúc (lease exclusivity, publish CAS) được tái lập và **do ràng buộc CSDL thật** thi hành, không phải bằng kiểm ở tầng ứng dụng | `FC-P4` (635 entry) | `ce22118c7012c20b396011cb313587d426e36e62fbccd36ece4da3cc02f5a34d` | 11738 |
| `A3-P4-R2-report.md` | AUDIT_REPORT `A3-P4-R2` — xác minh có phạm vi `F-A3-P4-01..03`. Verdict **PASS**: cả ba VERIFIED bằng tái lập của chính auditor, điều kiện phạm vi của R1 **được giải**, và `CR-TC-AUTH-11` là một bug thật đã sửa đúng — auditor xác nhận bằng **fault injection**, không bằng đọc mã. **Hai** finding mới, cả hai `LOW`, **không** chạm hành vi đã ship | `FC-P4` epoch 2 (645 entry) | `99dc3c06eb7742faa768f126be429b8f8e775d8a862e682b6f5b88f56aded396` | 11125 |
| `A3-P3-R1-report.md` | AUDIT_REPORT `A3-P3-R1` — audit độc lập **Giai đoạn 3 (M3)** cộng **Giai đoạn 5 (M6, văn bản thuần)**. Verdict **PASS CÓ MỘT ĐIỀU KIỆN**: mọi phép đo tái lập đúng, **trừ** `ruff format --check` đỏ trên bốn file và sẽ làm CI fail (`F-A3-P3-01`); auditor viết thẳng *"tôi sẽ không ký một commit của những byte này cho tới khi formatter chạy"*. Ba finding mới `F-A3-P3-01..03` | `FC-P3` epoch 1 (540 entry) | `d6368b95f4a277abbf1c2e1a90c1bffce75b36b20adf6ee3454b0594b238420f` | 16371 |
| `A3-P3-R2-report.md` | AUDIT_REPORT `A3-P3-R2` — xác minh có phạm vi `F-A3-P3-01..03`. Verdict **PASS**, cả ba VERIFIED bằng tái lập của chính auditor; **điều kiện của R1 được giải**, `FC-P3` epoch 2 sạch với mọi cổng auditor chạy được. **0 finding mới**; auditor ghi rõ *"tôi không đóng gì cả"* | `FC-P3` epoch 2 (545 entry) | `a62a74b5839383566e65f2bdec3d46463b4fde389896247f5538bc1fe72c1a16` | 10479 |
| `A3-P2-R1-report.md` | AUDIT_REPORT `A3-P2-R1` — audit độc lập của **Giai đoạn 2**: probe, connector paper, và `REQ-A6`. Verdict tổng **PASS** cho phạm vi review. Bản **duy nhất** có dùng mạng: bốn GET trang tài liệu trong allowlist Owner cấp, không host API nào. **Giải `CR-PC09-18`** — xem "Cách đọc" | `FC-P2` | `96efd7b1461677d0de52fe13905e654439dc305da2921dab648ab9ced97ed1e1` | 16829 |
| `FC-W1-manifest.txt` | FROZEN_CANDIDATE manifest — thuật toán `sha256-path-role-hash-bytes-v1` | `FC-W1` epoch 1 | `6471df833d8d900cd8e92d67032927ca186756a56f69764279cbe2d3fe54e5f3` | 8059 |
| `FC-W2-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W2` epoch 2 | `0195d00a3b9ebb49053af9292eb3127cfa22c3591c76c20118050bbbe89d1ccd` | 12129 |
| `FC-W3-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W3` epoch 3 | `b379ca40a4d3b56c1c868baa746e345a8d44dbe57a2f1a5f11cabab5eaedaefc` | 23455 |
| `FC-W4-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 4 | `dd18ade54827023dd5d6192ef3c6ed80bd51760b720effcc067ed37baa2df1a9` | 30716 |
| `FC-W4e5-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 5 | `48b875493abbfda76c979f274e571acbe752e9329b844e6b6cae23975fa6c4e1` | 30720 |
| `FC-W4e6-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 6 | `d08181135412c1412dbd057d977dedee86ba9905e6a693adaf25457547ea7adb` | 31020 |
| `FC-W4e7-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 7 | `7cdf1e12bfce6d64b708178ca5e117e0dc9403b1b849dcd6209b83cd89c87968` | 31021 |
| `FC-W4e8-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 8 | `5a38f0ceef921047877b33dfa9579a3c9051f323c38f4847d323d662e1404a9c` | 36558 |
| `FC-W4e9-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 9 | `818b0297c76c52d3855a970b3ffde41661c32298f00f4480974a00d7d3953348` | 36969 |
| `FC-P1-manifest.txt` | FROZEN_CANDIDATE manifest — epoch đầu tiên **có code** | `FC-P1` epoch 1 | `9553f45aaab6087969eb8538421be1ed62cef076fbc104041b82af2115092985` | 56259 |
| `FC-P1e2-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-P1` epoch 2 | `0d172d4c394728f359996e66d773387d4180e8c96698912a03dc1e11fb282bb9` | 56885 |
| `FC-P1e3-manifest.txt` | FROZEN_CANDIDATE manifest — 395 entry, `manifest_sha256 = 5f5b8aa425219de2621ef0a75a18ff3c6ed00a09b685cf6c13deeceeb12362b4` theo `A3-R3` §1 | `FC-P1` epoch 3 | `1a736950d1244c6bfc74d224d31c72d92b94a84528627850f1f0c459d11912d9` | 58266 |
| `FC-P1e4-manifest.txt` | FROZEN_CANDIDATE manifest — 413 entry, `manifest_sha256 = 576a7572c8ac25852a5a44a200c1593c1f80887970755d5c6473e5105d40bd36` theo `A3-R4` §Reference | `FC-P1` epoch 4 | `736ca1ab7f061b05dd050bcf41e9dd8562db5b3a5920b35c94fd6b0dd3af241b` | 60916 |
| `FC-P4-manifest.txt` | FROZEN_CANDIDATE manifest — **635 entry**, `manifest_sha256 = 04d4215d36c153f41500e06489ed3c84f5b42f3049e19248979cecca51508a2a`, epoch pin `PC10-PIN-P4-20260908`; quiescence 635/635 hai đầu, `git status` 118 trước và sau, **0** thư mục `__pycache__` | `FC-P4` | `dee4d783c98e1d8c234cabbcb0ca3da63383edfd06f9febd656aedeea2ad7c02` | 94546 |
| `FC-P4e2-manifest.txt` | FROZEN_CANDIDATE manifest — **645 entry**, `manifest_sha256 = d6d507588c4c50aa05476dd03aa2e1656a256fc1e2b21d8ce7b760b3e73e8037`, epoch pin `PC10-PIN-P4b-20260908`; quiescence 645/645 hai đầu, `git status` 147 trước và sau | `FC-P4` epoch 2 | `e0e436cdd1be5d51a5e8fdd01001c25f7aa515ced54067b9024721cf5f768f23` | 96138 |
| `FC-P3-manifest.txt` | FROZEN_CANDIDATE manifest — **540 entry**, `manifest_sha256 = 1c43507bc84a5f627ad2df0d6ad89d99e1b90a4c8ab05228c046280a6fb53db3`, epoch pin `PC10-PIN-P3b-20260908`. Delta so với `FC-P2`: 74 thêm, 0 bỏ, 44 đổi | `FC-P3` epoch 1 | `2b211a8cedc7ee9aa550c7067300eee9525034a69f0463e5238ce499ea45c921` | 80046 |
| `FC-P3e2-manifest.txt` | FROZEN_CANDIDATE manifest — **545 entry**, `manifest_sha256 = 41c475065793ee4ca5993a5ab1f98657fc23d617212ca1452475a9c90f76556a`. Delta: 5 thêm (manifest phát lại), 0 bỏ, 21 đổi; **không** file `contracts/`, `acceptance/`, `precode/` hay `agent-tasks/` nào dịch chuyển | `FC-P3` epoch 2 | `f9da1bd6abb6573090ee04e0ac92fce8fc600ae1abb38e1f7d857031d65d8ca5` | 80919 |
| `FC-P2-manifest.txt` | FROZEN_CANDIDATE manifest — **466 entry**, `manifest_sha256 = dafc1c83ca2108d50ccc5cc700115849b9537be31ff0155f5dd37c7bc5e469f0` (giá trị này nằm ở dòng 2 của chính file; **khác** sha256 của file, xem "Cách đọc"). Delta so với `FC-P1e4`: 53 thêm, 0 bỏ, 42 đổi | `FC-P2` | `042fb77283ea423461e8020e8d581c1f73102de804f7600e20d42bc013ced0f9` | 68990 |

## Cách đọc

- **Manifest** dùng thuật toán `sha256-path-role-hash-bytes-v1` của `agent_profile/protocol.md` §6: mỗi entry
  là `path|role|sha256|bytes\n`, sắp theo path, và `manifest_sha256` là SHA-256 của chuỗi nối. Manifest không
  chứa chính nó.
- **HAI con số hash của một manifest, đừng lẫn.** `manifest_sha256` (ghi ở dòng 2 trong chính file) là digest
  của **danh sách entry** theo thuật toán trên — đó là thứ báo cáo audit trích. Cột `SHA-256` trong bảng dưới
  là hash của **file trên đĩa**, gồm cả phần header bình luận. Với `FC-P2`: `dafc1c83…` là cái thứ nhất,
  `042fb772…` là cái thứ hai. Hai giá trị **phải** khác nhau; nếu ai đó thấy chúng bằng nhau thì có gì đó sai.
- **Verdict trong báo cáo có phạm vi.** Mỗi PASS/FAIL chỉ áp cho phần auditor thật sự kiểm, và không cái nào là
  product acceptance. **Mười** báo cáo `A1-*`/`A2-*` ở mức bằng chứng **E0** (kiểm tính nhất quán tĩnh của văn
  bản hợp đồng); không có gì được chạy trong chúng. **Ba** báo cáo `A3-*` ở mức **E1/E2** (contract test bằng
  fixture cộng fault injection) cho đúng bốn card và skeleton mà chúng kiểm — và **E3/E4 vẫn `NOT_RUN`** ở cả
  chín: không một lời gọi live nào, không X, không Telegram, không provider AI, không Chrome. **Hai** bản có
  dùng mạng, và chỉ để **đọc lại tài liệu** trong đúng allowlist Owner đã cấp — `A3-P2-R1` bốn lần GET
  (`info.arxiv.org`, `help.openalex.org`) và `A3-P3-R1` bốn lần GET (`core.telegram.org`,
  `www.anthropic.com`) — **không** host API nào được chạm ở cả hai.
- **`F-A3R4-01` (LOW) — `PARKED` theo ruling của Coordinator.** `A3-R4` chứng minh rằng nhãn claim trong
  **front-matter của file Markdown** dưới `evidence/coordination/` **không được quét** bởi `E0-12`: auditor đặt
  `claim_ceiling: PRODUCT_ACCEPTED` vào front-matter một file `.md` ở đó và phép kiểm **PASS**. Ghi chú của
  `e0_check.py` nói "structured fields are still checked" — đúng cho `.yaml`/`.json`, **không** đúng cho
  front-matter `.md`. Coordinator ruling: **PARKED**, không sửa trong vòng này; việc cải tiến công cụ giao cho
  vòng PC09 kế tiếp qua **`CR-PC09-18`**. Hai điều cần đọc kèm để `PARKED` không bị hiểu là "không sao":
  (a) hệ quả là `evidence/coordination/*.md` hiện **không có** một phép kiểm nhãn claim nào — prose sweep là
  cái duy nhất từng chạm tới nó, và exemption đã gỡ nó; (b) `A3-R4` nêu **ràng buộc remediation** rất cụ thể —
  hoặc mở rộng phép quét structured sang front-matter `.md`, **hoặc** sửa ghi chú thành "structured
  `.yaml`/`.json` fields"; để nguyên một ghi chú tự nhận một tầm với mà phép kiểm không có **chính là** loại
  lỗi mà `F-A3R3-01` đã phạt. `PARKED` **không** phải `CLOSED`, và không ai được coi nó đã được xử lý.
- **`A3-R3` PASS không có nghĩa là mọi thứ nó chạm đều sạch.** Cùng bản đó mở `F-A3R3-01`: phép kiểm `E0-12`
  bắt được nhãn claim đặt sai **ngoài** hai cây bằng chứng nhưng **không** bắt được nhãn đặt **trong**
  `evidence/runs/`, vì hàm phạm vi loại trừ thư mục đó — auditor chứng minh bằng bốn mutation, ba trong số đó
  lẽ ra phải FAIL mà lại PASS. Một verdict tổng PASS cho *phạm vi được giao* và một lỗ hổng trong *công cụ*
  cùng tồn tại được; đọc verdict mà bỏ bảng finding là đọc sai.
- **Bản ghi bằng chứng cho `A3-R1`/`A3-R2` nằm ở `evidence/index.json`** (`EV-A3-01`…`EV-A3-06`). Chúng là
  **bản chép** do `worker-W6n` viết dưới `PKT-PC09-P1`, không phải bản gốc của Auditor: mỗi bản ghi khai điều
  đó, ghim sha256 của hai file trong thư mục này, và nói rằng nếu bản chép lệch với báo cáo thì **báo cáo
  thắng**. `EV-A3-07-round3` đã được thêm cho vòng 3. **Mười** báo cáo A1/A2 và **`A3-R4`** vẫn **không** có
  bản ghi tương ứng — `A3-R4` ra đời sau lượt đăng ký gần nhất, nên việc đăng ký nó là việc của một vòng PC09
  sau (`CR-PC00-22`, nay trỏ vào `A3-R4`).
- **Hai báo cáo `A3-P3-*` cũng CHƯA có bản ghi trong `evidence/index.json` tại thời điểm chép**
  (2026-09-07T20:43Z): `EV-A3-*` dừng ở `EV-A3-11-p2-overall`, và `evidence/handoffs/PC09-handoff.md`
  chưa có addendum A3-P3. Packet `PC09-P3` của `worker-W6n` chạy **song song** và sẽ ghim hash. Vì vậy lần
  chép này **không đối chiếu** được với một giá trị đã đăng ký — nó **cung cấp** giá trị đầu tiên, đúng như
  `A3-P2-R1` ở `PKT-PC00-FIX24`. Bảo đảm ở đây là `cmp` byte-identical với bản gốc trong scratchpad, **không**
  phải một lần khớp hash hai chiều. → `CR-PC00-33`.
  **`A3-P4-R1` cũng vậy** tại thời điểm chép (2026-09-08T01:24Z): `grep 'A3-P4'` trên `evidence/index.json`
  trả **0**. Ba vòng liên tiếp (`A3-P2-R1`, `A3-P3-*`, `A3-P4-R1`) rơi vào cùng một tình huống, nên đây không
  còn là một sự trùng hợp mà là **thứ tự công việc**: gói đóng gói của PC00 chạy **trước** gói đăng ký của
  PC09. Không sai, nhưng nên được biết: hash trong thư mục này là **nguồn**, `evidence/index.json` là **bên
  ghim sau**. → `CR-PC00-33` (mở rộng). **Lượt `A3-P4-R2` (2026-09-08T01:33Z) cũng vậy: `grep 'A3-P4'` trên
  `evidence/index.json` vẫn trả 0** — `worker-W6n` đăng ký song song và sẽ ghim sau.
- **`PKT-PC00-FIX31` chạy hai lượt, và điều đó được ghi thay vì làm phẳng.** Lượt đầu (2026-09-08T01:24Z)
  chép `A3-P4-R1` cùng manifest epoch 1 khi cổng còn đặt ở R1; Coordinator sau đó **dời cổng sang R2** vì một
  vòng sửa đang chạy. Bốn file của lượt đầu là bản sao byte-identical của artifact **thật** ở epoch 1 nên
  chúng ở lại; lượt sau bổ sung epoch 2. Vì vậy danh mục mang **cả hai** verdict — R1 *PASS có điều kiện* và
  R2 *PASS* — chứ không chỉ cái mới hơn: điều kiện của R1 là một phần của hồ sơ, không phải một trạng thái
  trung gian đáng xoá.
- **`A3-P4-R2` giải điều kiện của R1 — và mở ra một lỗ trong CHÍNH công cụ vừa được thêm.** `F-A3-P4R2-01`
  (`LOW`): phép kiểm `E0-21` mà ruling `F-A3-P4-03` yêu cầu dựng **không nhìn thấy** dạng `reason=` viết trên
  **một dòng** — regex kết thúc dùng `$` dưới `re.S` nên chỉ neo ở cuối chuỗi, khiến một `reason` cũ mèm nằm
  giữa file **lọt qua**. Auditor mutation-test cả hai chiều rồi kết luận: ba marker hiện tại đều dùng dạng
  nhiều dòng, nên con số **`0 violations` hôm nay là trung thực** — nhưng phép kiểm **yếu hơn vẻ ngoài**.
  Đây là lần thứ hai một công cụ bằng chứng tự nó có lỗ (`F-A3R4-01` là lần đầu), và cả hai lần đều do
  auditor **thử phá** công cụ chứ không đọc nó.
- **`A3-P4-R1` cũng là PASS *có điều kiện*, và điều kiện là một vấn đề PHẠM VI CLAIM, không phải một bug.**
  `F-A3-P4-01` (MEDIUM): `CR-TC-BACKFILL-09` là một defect **đã biết** trong publisher —
  `_write_first_announcements` ghi hàng ledger cho **mọi** mục `new_discovery` kể cả khi `summary_state` còn
  `pending`, nên một phát hiện muộn thật sự quay lại thành `prior_reference`. Vấn đề auditor nêu **không** phải
  defect ấy mà là: card `TC-report-coverage-publish-cas` **mang claim phủ** đúng requirement mà defect ấy phá
  (`REQ-D29`/`REQ-AC09`/`I07`), trong khi CR chưa được xử lý và **không** được nêu trong handoff của chính card.
  Đây là chỗ một nhãn "đã phủ" nói nhiều hơn bằng chứng đỡ được — và nó chỉ lộ ra vì auditor **đọc chéo** CR
  với claim thay vì đọc từng cái riêng.
- **Cả `A3-P4-R1` cũng để lại danh sách nợ dài hơn phần nó xác nhận.** Ngoài `F-A3-P4-01..03`: `F-A3R4-01`,
  `F-A3-P2-01/02` vẫn mở; **~50 CR của đợt sáu card** chưa được Coordinator xử lý (auditor **chỉ** xem xét cái
  chạm vào một requirement đã được claim); một `run=False` xfail; ba dữ kiện `delivery.md` §3.4 vẫn
  `BLOCKED_DEPENDENCY` và `MOD-telegram-adapter` **vẫn bị chặn cứng**; **cả hai adapter AI vẫn
  `enabled: false`** vì cô lập; `MOD-tag-service` **chưa có card**; `REQ-A2`/`REQ-A4` vẫn `uncalibrated`.
  Và câu quan trọng nhất, nguyên văn: **`E3`/`E4` vẫn bằng 0 ở khắp nơi** — không một lời gọi AI, Telegram
  hay X thật nào, không drill restore thật, không lượt review UI render, **`SP1` chưa bao giờ chạy**.
  **`A3-P4-R2` lặp lại đúng câu ấy ở epoch 2** — sau khi mọi finding của R1 đã được xác minh: `E3`/`E4` vẫn
  bằng **0** ở khắp nơi, cả hai adapter AI vẫn `enabled: false`, `MOD-tag-service` vẫn chưa có card,
  `REQ-A2`/`REQ-A4` vẫn `uncalibrated`, ba strict xfail còn lại đều là **phân kỳ hợp đồng/fixture đã khai**.
  Một chuỗi `PASS` liên tiếp **không** rút ngắn danh sách này; nó chỉ nói rằng cái đã đo thì đo đúng.
- **`A3-P3-R1` PASS *có điều kiện*, và điều kiện ấy không được nuốt vào chữ "PASS".** R1 nói: hành vi đúng,
  **cổng thì không** — `ruff format --check` đỏ trên bốn file. Auditor từ chối ký commit của những byte đó.
  Điều kiện được giải ở **epoch 2**, và `A3-P3-R2` xác minh bằng tái lập của chính họ. Đọc R1 mà bỏ vế điều
  kiện là đọc ngược lại điều auditor cố ý viết ra. `A3-P3-R2` cũng ghi thẳng *"tôi không đóng gì cả —
  disposition vẫn là của Coordinator"*, đúng `protocol.md` §8: một verdict `VERIFIED` **không** phải một
  finding đã `CLOSED`.
- **Cả hai bản `A3-P3-*` đều để lại phần còn nợ.** Ba trong năm dữ kiện `contracts/telegram/delivery.md`
  §3.4 vẫn `KC`/`BLOCKED_DEPENDENCY` và `MOD-telegram-adapter` **vẫn bị chặn cứng**; bước tiếp là một
  **range/offset fetch** trên chính URL chính thức — theo lời auditor, đó là **một amendment công cụ, không
  phải một quyền mạng mới**. Cùng với `F-A3R4-01`, `F-A3-P2-01/02` và `F-A3-P3-01..03`, đây là danh sách
  residual mà một lượt đọc "PASS" đơn thuần sẽ bỏ sót.
- **`CR-PC09-18` được GIẢI bằng chính lần chép này, và đây là lý do nó tồn tại.** `evidence/index.json` bản
  ghi `EV-A3-11-p2-overall` **trích** `evidence/audits/A3-P2-R1-report.md` chín lần nhưng `artifacts[]`
  **không ghim được** sha256 của nó, và bản ghi tự khai đúng như vậy: *"Báo cáo gốc chưa nằm trong repo, nên
  `artifacts[]` KHÔNG ghim được hash của nó và việc đối chiếu bản chép này hiện phụ thuộc vào lời tôi."*
  Nay báo cáo **đã** ở trong repo với hash `96efd7b1…` (16829 byte), nên PC09 ghim được và sự phụ thuộc ấy
  chấm dứt. **Lưu ý về thứ tự:** vì chưa có hash nào được đăng ký trước, lần chép này **không thể** đối chiếu
  với một giá trị có sẵn — nó **cung cấp** giá trị đầu tiên. Bảo đảm duy nhất ở đây là `cmp` byte-identical
  với bản gốc trong scratchpad, không phải một lần khớp hash hai chiều.
- **Finding không bị đóng ở đây.** Theo `protocol.md` §8, chuyển một finding sang `CLOSED` cần authority được
  chỉ định sau khi có xác minh độc lập trên một epoch mới, và người xác minh không được là người viết bản sửa.
  Trạng thái finding sống ở `precode/review.md` và trong các addendum của `evidence/handoffs/`.
- **Nguồn đối chiếu:** `evidence/coordination/` giữ các packet và ruling đã sinh ra những vòng audit này.
