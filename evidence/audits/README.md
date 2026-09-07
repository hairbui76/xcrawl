# Hồ sơ audit độc lập — Research Radar Pre-code

**Mười bốn** AUDIT_REPORT của **ba** auditor độc lập (`auditor-A1` ×3, `auditor-A2` ×7, `auditor-A3` ×4) và
**mười ba** FROZEN_CANDIDATE manifest, được lưu lại nguyên văn để chúng không mất cùng phiên làm việc. Chuỗi
epoch: `FC-W1` 1 → `FC-W2` 2 → `FC-W3` 3 → `FC-W4` 4, 5, 6, 7, **8 (epoch phê chuẩn của Owner)**, **9 (epoch
cuối của baseline hợp đồng)** → **`FC-P1` 1, 2, 3 và 4 (bốn epoch đầu tiên CÓ CODE)**.

**`A2-R7` là ngoại lệ về hình dạng, không phải về hiệu lực.** Nó là báo cáo duy nhất **không có freeze
manifest**: Coordinator dispatch nó lúc 18 task card đang được re-pin đồng thời, nên thay vì một manifest,
`auditor-A2` hash hai văn bản trong phạm vi ở **đầu** và **cuối** vòng và ghi cả hai giá trị. Điều đó chứng
minh được cùng một thứ mà một manifest chứng minh cho một phạm vi hai file — không có drift trong lúc review —
nhưng nó **không** phải một epoch trong chuỗi trên, nên đừng tìm `FC-` tương ứng.

**Bốn báo cáo `A3-*` khác mọi báo cáo trước chúng ở một điểm cần nói rõ:** mười báo cáo A1/A2 đều ở mức bằng
chứng **E0** — kiểm tính nhất quán tĩnh của văn bản hợp đồng, không có gì được chạy. Bốn báo cáo A3 audit
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

Thư mục được bổ sung **bốn** lần: `PKT-PC00-FIX9` chép hồ sơ tới epoch 7, `PKT-PC00-FIX12` chép tiếp tới
epoch 9, `PKT-PC00-FIX18` chép `A2-R7`, `A3-R3` cùng ba manifest `FC-P1`, và `PKT-PC00-FIX19` chép `A3-R4`
cùng manifest epoch 4. Mỗi lần chép đều `cmp`-verified và hash được tính lại sau khi chép.

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

## Cách đọc

- **Manifest** dùng thuật toán `sha256-path-role-hash-bytes-v1` của `agent_profile/protocol.md` §6: mỗi entry
  là `path|role|sha256|bytes\n`, sắp theo path, và `manifest_sha256` là SHA-256 của chuỗi nối. Manifest không
  chứa chính nó.
- **Verdict trong báo cáo có phạm vi.** Mỗi PASS/FAIL chỉ áp cho phần auditor thật sự kiểm, và không cái nào là
  product acceptance. **Mười** báo cáo `A1-*`/`A2-*` ở mức bằng chứng **E0** (kiểm tính nhất quán tĩnh của văn
  bản hợp đồng); không có gì được chạy trong chúng. **Ba** báo cáo `A3-*` ở mức **E1/E2** (contract test bằng
  fixture cộng fault injection) cho đúng bốn card và skeleton mà chúng kiểm — và **E3/E4 vẫn `NOT_RUN`** ở cả
  bốn: không một lời gọi live nào, không X, không Telegram, không provider AI, không Chrome.
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
- **Finding không bị đóng ở đây.** Theo `protocol.md` §8, chuyển một finding sang `CLOSED` cần authority được
  chỉ định sau khi có xác minh độc lập trên một epoch mới, và người xác minh không được là người viết bản sửa.
  Trạng thái finding sống ở `precode/review.md` và trong các addendum của `evidence/handoffs/`.
- **Nguồn đối chiếu:** `evidence/coordination/` giữ các packet và ruling đã sinh ra những vòng audit này.
