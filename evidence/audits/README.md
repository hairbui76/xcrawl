# Hồ sơ audit độc lập — Research Radar Pre-code

Bảy AUDIT_REPORT của hai auditor độc lập (`auditor-A1`, `auditor-A2`) và bảy FROZEN_CANDIDATE manifest
tương ứng, được lưu lại nguyên văn để chúng không mất cùng phiên làm việc.

## Vị trí của tập hồ sơ này trong chuỗi bằng chứng

**Những bản ghi này ra đời SAU lần freeze `FC-W4` epoch 7 mà `A2-R4` đã audit.** Vì vậy chúng **không** nằm trong
bất kỳ candidate manifest nào đã được audit, và **không** được coi là một phần của candidate đã đóng băng.

Đó không phải thiếu sót mà là ràng buộc của giao thức: `protocol.md` §6 nói rõ *"Persist audit report là new
evidence artifact trong packaging phase; không chèn report vào manifest mà report đang ký."* Một báo cáo không
thể nằm trong chính snapshot mà nó ký, và một manifest không thể chứa chính nó. Nếu về sau có một epoch mới,
epoch đó có thể bao gồm thư mục này như **bằng chứng** (role `EVIDENCE`), không phải như candidate.

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
| `FC-W1-manifest.txt` | FROZEN_CANDIDATE manifest — thuật toán `sha256-path-role-hash-bytes-v1` | `FC-W1` epoch 1 | `6471df833d8d900cd8e92d67032927ca186756a56f69764279cbe2d3fe54e5f3` | 8059 |
| `FC-W2-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W2` epoch 2 | `0195d00a3b9ebb49053af9292eb3127cfa22c3591c76c20118050bbbe89d1ccd` | 12129 |
| `FC-W3-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W3` epoch 3 | `b379ca40a4d3b56c1c868baa746e345a8d44dbe57a2f1a5f11cabab5eaedaefc` | 23455 |
| `FC-W4-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 4 | `dd18ade54827023dd5d6192ef3c6ed80bd51760b720effcc067ed37baa2df1a9` | 30716 |
| `FC-W4e5-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 5 | `48b875493abbfda76c979f274e571acbe752e9329b844e6b6cae23975fa6c4e1` | 30720 |
| `FC-W4e6-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 6 | `d08181135412c1412dbd057d977dedee86ba9905e6a693adaf25457547ea7adb` | 31020 |
| `FC-W4e7-manifest.txt` | FROZEN_CANDIDATE manifest | `FC-W4` epoch 7 | `7cdf1e12bfce6d64b708178ca5e117e0dc9403b1b849dcd6209b83cd89c87968` | 31021 |

## Cách đọc

- **Manifest** dùng thuật toán `sha256-path-role-hash-bytes-v1` của `agent_profile/protocol.md` §6: mỗi entry
  là `path|role|sha256|bytes\n`, sắp theo path, và `manifest_sha256` là SHA-256 của chuỗi nối. Manifest không
  chứa chính nó.
- **Verdict trong báo cáo có phạm vi.** Mỗi PASS/FAIL chỉ áp cho phần auditor thật sự kiểm, và không cái nào là
  product acceptance. Cả bảy báo cáo đều ở mức bằng chứng **E0** (kiểm tính nhất quán tĩnh của văn bản hợp đồng);
  không có E1–E4, không có gì được chạy.
- **Finding không bị đóng ở đây.** Theo `protocol.md` §8, chuyển một finding sang `CLOSED` cần authority được
  chỉ định sau khi có xác minh độc lập trên một epoch mới, và người xác minh không được là người viết bản sửa.
  Trạng thái finding sống ở `precode/review.md` và trong các addendum của `evidence/handoffs/`.
- **Nguồn đối chiếu:** `evidence/coordination/` giữ các packet và ruling đã sinh ra những vòng audit này.
