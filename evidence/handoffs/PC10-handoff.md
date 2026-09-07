---
contract_id: CT-handoff-PC10
version: 0.1.0
status: draft
owner_role: implementation planning owner
source_refs: [SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15, SRC-PLAN §16, SRC-PLAN §17, SRC-SPEC §6.3, SRC-SPEC §13]
requirement_refs: [REQ-OQ01, REQ-OQ02, REQ-OQ03, REQ-A5, REQ-A6]
decision_refs: [ADR-0006, "baseline §5 hàng Stack (PROVISIONAL)"]
invariant_refs: []
producers: []
consumers: []
dependencies: [precode/baseline.json, contracts/ports.yaml, contracts/errors.yaml, contracts/modules.yaml]
scope: HANDOFF của gói PC10 theo baseline §4.
verification: EV-PC10-01..05, tất cả SELF_VALIDATION.
claim_ceiling: DRAFT_FOR_REVIEW
---

# HANDOFF — PKT-PC10

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-PC10` |
| `worker_principal` | `worker-W7` |
| `authority_id` | `AUTH-COORD-PC10` (parent `AUTH-OWNER-20260906-01`) |
| `lease_id` | `LEASE-PC10-e1` (exclusive, fencing 1) |
| `enforcement_mode` | `DOCUMENTARY_DRAFT` |
| **`status`** | **`DONE_WITH_CONCERNS`** |
| `completion_claim` | `DRAFT_FOR_REVIEW` |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T02:20Z |

**Vì sao `DONE_WITH_CONCERNS` chứ không phải `DONE`:** frozen candidate `FC-W3` epoch 3 đã lệch 48 file
trong lúc PC10 chạy (§6.1). Mọi write target đã hoàn thành và mọi verification đã PASS, nhưng pin của card
không phải pin của một frozen candidate hợp lệ. Chi tiết ở `CR-PC10-01`.

**Vì sao không phải `STALE_BASELINE`:** hai nguồn đã pin (`SRC-SPEC`, `SRC-PLAN`) **không đổi** — kiểm ở đầu
và cuối phiên, cả hai lần khớp. Stop gate baseline §6 hàng đầu ("Source hash mismatch") **không** trigger.
Drift nằm ở file dependency do PC09 (W6) đang chạy song song ghi, đúng như dispatch đã báo trước. PC10 vì
vậy đi tiếp và ghi lại drift tường minh thay vì im lặng chép hash đã sai.

## 2. Changes — mọi file đã tạo

Tất cả là `CREATE`, baseline `ABSENT`. Không file nào bị `MODIFY` hay `DELETE`.

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `agent-tasks/TEMPLATE.md` | CREATE | ABSENT | `035c13021683ddbf448c7491ce12abb25624a309c2f884eea34e584aa0a3e411` | 10424 |
| `agent-tasks/README.md` | CREATE | ABSENT | `74f5edd3539d98c3f5bac085fc147929243b57c3889a678a7c4cb0cf4c3731e4` | 9381 |
| `agent-tasks/WALKTHROUGH.md` | CREATE | ABSENT | `d9919c8e66a7010dd1ec9731ffa92c08eb5a3902cdc3da5d003b4d1ed7ad2a50` | 13750 |
| `agent-tasks/TC-analysis-adapter-validation.md` | CREATE | ABSENT | `e0caca68ff33a5bcf52cea8356d21010f5c87ef613c1e4c7ac3485528740bd98` | 19267 |
| `agent-tasks/TC-analysis-once-per-generation.md` | CREATE | ABSENT | `75173c9ac968fdf9c470f6f3f98e0afee1cc6efe8249e1129deb9a6189dd5989` | 17846 |
| `agent-tasks/TC-backfill-pending-ledger.md` | CREATE | ABSENT | `2475a7ba9d8290aec29b37174eacdec506f9e8dd737e92e0a1f1963fff35f447` | 16286 |
| `agent-tasks/TC-backup-restore-drill.md` | CREATE | ABSENT | `42e13d6e1949203d60385f199ed792fdb6b60a3f368f90992f37b113e99e0473` | 16976 |
| `agent-tasks/TC-canonical-identity-merge.md` | CREATE | ABSENT | `44dc9aebeeef60801ed32b486c9045985ca504f8c28361682ba17b41d456e36b` | 18295 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | CREATE | ABSENT | `1b210b4940327eb44152797cface778baf7078ca0df1b93a8c6c71268f23d70b` | 19515 |
| `agent-tasks/TC-embedding-generation-switch.md` | CREATE | ABSENT | `82dcb5f3016f9c11883ceb851145ae21ec080ab2105713b2eaf64a246ccef094` | 15830 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | CREATE | ABSENT | `70639e840a22360437865392b389398684501778dbcf9d1a2439557e48ed172f` | 21128 |
| `agent-tasks/TC-owner-auth-session.md` | CREATE | ABSENT | `02278e05ad901c5bd50804db2b9a7005b7c74ab368cfae47a3c4fada79570e46` | 16457 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | CREATE | ABSENT | `4342defaacfbfa8c6bfad2e72cdffd7872c5d8a5d9b22ff0b5351b159997b3c8` | 19498 |
| `agent-tasks/TC-saved-snapshot.md` | CREATE | ABSENT | `760411fada6ddf7641c5178bb35c3934a19f0be5a5ee0619ef9205621d1bda20` | 18030 |
| `agent-tasks/TC-scheduler-lease-claim.md` | CREATE | ABSENT | `275e2ae3651493c69c587ba5dfd6cf0251772676c97652fce9b1418e190419fe` | 18343 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | CREATE | ABSENT | `8dc15f46997aae1a264ec95c4194d8a7ffa07e8929d6a2b80dfbca8fadf13d7a` | 15936 |
| `agent-tasks/TC-telegram-linking-auth.md` | CREATE | ABSENT | `5ddd4187cf58ae27dd2d8f48ee4097ecd11aaa38848a01583c33700ccce66131` | 18795 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | CREATE | ABSENT | `5f5e943318014579b69ae44dfa9dfdfd92eb5ef1f1bf0274d36faa5232ee5fdc` | 19175 |
| `agent-tasks/TC-ui-reports-detail.md` | CREATE | ABSENT | `bab37008d830ceba2747ae4be2475abd2bbf7fbaec9bf135e125f67260e1cbec` | 17000 |
| `agent-tasks/TC-ui-runs-three-states.md` | CREATE | ABSENT | `6ab9d706b4854e5ce1f7a5d387563bc53fde62b2822aaf5e057bdcda480fcd41` | 16972 |
| `agent-tasks/TC-x-feasibility-probe.md` | CREATE | ABSENT | `2503bc9bbcf3d4de9c772a79afa2b5ad1252bd338d2c513afe5ebe9e7f207442` | 15564 |
| `precode/change-control.md` | CREATE | ABSENT | `baf10e0340d43696193b6bab74a4abb3c79a9e96aae79ee9db0dea046d329d9c` | 13696 |
| `precode/README.md` | CREATE | ABSENT | `7231737dc7cbb8812406580c0b38e7cf83912667b63afb780ad9d4654aee720a` | 12966 |
| `evidence/handoffs/PC10-handoff.md` | CREATE | ABSENT | *(file này)* | — |

**23 file, 381 130 byte.** Không có file nào được tạo ngoài directory grant `agent-tasks/` + hai write
target ở `precode/` + handoff. Không có `__pycache__` (`PYTHONDONTWRITEBYTECODE=1` cho mọi lần chạy);
mọi script chạy từ `…/scratchpad/w7/`, không từ repo. Không chạy lệnh git nào. Không truy cập mạng.

## 3. Source baselines

| Ref | Path | SHA-256 | Kiểm lúc bắt đầu | Kiểm trước handoff |
| --- | --- | --- | --- | --- |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp | **khớp** |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp | **khớp** |

Frozen candidate đọc: `FC-W3` epoch 3, manifest
`…/scratchpad/audits/FC-W3-manifest.txt`, `manifest_sha256:
da5c45a8fa0508373ee641e25297845931478e98de31bca8fd695e1babbc099f`, 151 entry. Xem §6.1 về drift.

## 4. Evidence records

Tất cả `SELF_VALIDATION`. Không có mục nào là independent audit.

### EV-PC10-01 — pin hash, path, operation ID, SC ID, error code, module, invariant

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` |
| `command` | `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T02:14Z / 2026-09-07T02:15Z |
| `input_hashes` | 18 card (bảng §2) + `contracts/ports.yaml` `100c94c1…` + `contracts/errors.yaml` `3201bbe8…` + `contracts/modules.yaml` `89b348aa…` |
| `oracle` | (a) mọi dòng hash trên card tính lại phải bằng file live; (b) mọi path repo được trích dẫn phải tồn tại hoặc được khai `pending PC09`; (c) mọi `operation_id` phải có trong `ports.yaml`; (d) mọi SC phải nằm trong dải SC01–SC48; (e) mọi mã lỗi ở §7 phải có trong `errors.yaml`; (f) mọi `MOD-*` phải có trong `modules.yaml`; (g) mọi `I<nn>` trong I01–I17 |
| `expected` | 0 sai lệch |
| `observed` | **426 dòng hash (128 file riêng) khớp 100 %**; 612 path citation hợp lệ; 142 operation citation hợp lệ; 87 SC citation trong dải; 99 error citation ở §7 hợp lệ; 0 module/invariant lạ |
| `exit_code` | 0 |
| `status` | **PASS** |
| `limitations` | Lượt chạy đầu báo 71 sai lệch; kiểm tay cho thấy **toàn bộ là false positive của oracle**, thuộc ba lớp: (1) key-path YAML viết dạng `file.key` (`contracts/modules.yaml.default_deny`) bị đọc nhầm là đường dẫn; (2) artifact tương lai do chính card đặt tên (`evidence/runs/<card>/manifest.json`, `evidence/handoffs/PC10-handoff.md`); (3) token trường/trạng thái dạng `a.b` (`run.status`, `storage.health`, `delivery.unknown`, `report.abort_reason`, `saved_snapshot.content_hash`, …) bị đọc nhầm là operation. Oracle được sửa để (1) và (2) bị loại trừ theo quy tắc, và (3) được **kiểm ngược** — mỗi token trường phải xuất hiện trong hợp đồng sở hữu nó. Không một dòng nội dung card nào bị sửa để làm check pass. |

### EV-PC10-02 — đủ 14 mục TEMPLATE trên mọi card

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` |
| `command` | như EV-PC10-01 (cùng script, phần đầu) |
| `oracle` | mỗi card phải có heading `## §0.` … `## §13.` và front-matter mở đầu bằng `card_id:` |
| `expected / observed` | 18/18 card đủ 14 mục; 18/18 có front-matter |
| `exit_code` | 0 · `status` | **PASS** |
| `limitations` | Kiểm sự **hiện diện** của heading, không kiểm chất lượng nội dung bên trong. |

### EV-PC10-03 — walkthrough card collector và card delivery

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` (đọc thủ công, không có script) |
| `procedure` | Đóng vai agent chỉ có card + file card trỏ tới; đi qua 12 bước của `TC-collector-checkpoint-resume` và 10 bước của `TC-telegram-unknown-delivery`; mỗi bước hỏi "trả lời được từ file đã cho, hay phải đoán?" |
| `oracle` | 0 chỗ phải đoán về giao tiếp hoặc state |
| `observed` | **Giao tiếp và state: 0 chỗ phải đoán** (22/22 bước trả lời được). **Ranh giới ra ngoài: 2 chỗ phải đoán** — nhịp gọi/rate limit của X (GAP-A1) và giới hạn định dạng Telegram (GAP-B1). Thêm 1 gap về capability của luồng gửi (GAP-B2) và 1 gap do PC09 chưa landing (GAP-C1) |
| `status` | **FAIL** theo oracle "0 chỗ phải đoán" — 4 gap, đều đã raise thành CR (§6.2) |
| `artifact` | `agent-tasks/WALKTHROUGH.md` |
| `limitations` | Self-review của chính người viết card. Không phải independent audit. |

### EV-PC10-04 — đối chiếu `precode/change-control.md` với SRC-PLAN §16

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` (đọc thủ công) |
| `oracle` | 7 gạch đầu dòng của SRC-PLAN §16 phải có mục tương ứng |
| `observed` | 7/7: CR format → §1; version bump → §2; tag/coverage/identity/analysis-key invalidation → §4; provider/model/embedding → §4; dispatcher/retry/linking → §4; baseline của task đang chạy → §5; Owner chấp nhận một lần → §6. Cộng thêm §7 (xử lý CR của Pre-code) và §8 (giữ bản cũ) |
| `status` | **PASS** |

### EV-PC10-05 — bản đồ thư mục của `precode/README.md`

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` |
| `command` | `find . -type f` + đối chiếu tay với bảng §2 của `precode/README.md` |
| `oracle` | mọi đường dẫn trong bản đồ tồn tại, hoặc được đánh dấu "chưa có" kèm chủ sở hữu |
| `observed` | 16/16 nhóm của SRC-PLAN §4 có mặt; 5 file được đánh dấu chưa có (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `evidence/manifest.schema.json`, `evidence/index.json`, `precode/gates.yaml`, `precode/review.md`) và tất cả thuộc PC09 |
| `status` | **PASS** |

### Những gì PC10 **không** chạy — `NOT_RUN`

- `evidence/tools/e0_check.py` (PC09 tạo trong lúc PC10 chạy). PC10 **không** chạy nó. E0 chính thức là của PC09.
- Bất kỳ validator OpenAPI 3.1 nào trên `contracts/http/openapi.yaml`.
- Bất kỳ test E1–E4 nào. Không có code sản phẩm nào tồn tại.
- Probe SP1, probe CLI/ACP, gọi provider AI, gửi Telegram, chạy collector.

## 5. Checklist của packet

| # | Mục (PKT-PC10 §Checklist) | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | Stack ghi PROVISIONAL qua ADR-0006; đường dẫn có điều kiện trên từng card | **DONE** | Front-matter `stack_decision` + banner đầu card + §3 mọi card; `agent-tasks/TEMPLATE.md` §3; `precode/change-control.md` §4 hàng cuối |
| 2 | Card tách theo deliverable kiểm được độc lập | **DONE** | 18 card; `agent-tasks/README.md` §5 (luật chia card); không card nào là "làm toàn bộ backend/UI" |
| 3 | Contract version/hash, allowed files, imports/edges, consumed/produced ops, proof obligations trên mọi card | **DONE** | §0 (426 dòng hash), §3, §4, §5, §8 của mọi card; EV-PC10-01 |
| 4 | Stop conditions, dependencies, reviewer scope, expected evidence, claim tối đa trên mọi card | **DONE** | §10 (2–4 stop riêng + 6 stop chung), §11, §12, §13, §9 của mọi card |
| 5 | Walkthrough một card collector và một card delivery; gap ghi thành CR | **DONE** | `agent-tasks/WALKTHROUGH.md`; 4 gap → `CR-PC10-01..04` + xác nhận `CR-PC07-04` |
| — | `agent-tasks/TEMPLATE.md` với 10 mục §15 + pin block + reviewer + deps + evidence manifest | **DONE** | `agent-tasks/TEMPLATE.md` |
| — | `agent-tasks/README.md`: cách phát hành, thứ tự M1–M8, đồ thị phụ thuộc, luật STALE | **DONE** | `agent-tasks/README.md` §1, §2, §3, §4 |
| — | `precode/change-control.md` theo SRC-PLAN §16 | **DONE** | EV-PC10-04 |
| — | `precode/README.md` là điểm vào | **DONE** | EV-PC10-05 |
| — | 18 card tối thiểu theo tên trong packet | **DONE** | 18/18 tên đúng như packet liệt kê |

## 6. Unresolved refs

### 6.1 Baseline drift — 48 file lệch khỏi `FC-W3` epoch 3

Lúc bắt đầu phiên, `sha256sum -c` trên 151 entry của manifest cho **151 OK**. Khoảng 15 phút sau, khi bắt đầu
sinh card, 48 entry đã **FAILED**. Repo ổn định trong suốt thời gian PC10 ghi file (kiểm hai lần, t1 và t2,
giống hệt nhau), nên hash pin trên card là nhất quán với nhau.

File lệch, theo nhóm:

- `precode/baseline.json` (`61fb00b7…` → `604e2c1c…`, 87560 → 89856 byte)
- `contracts/schemas/analysis-result.schema.json`
- 7 handoff: `PC00`, `PC02`, `PC04`, `PC05`, `PC06`, `PC07`, `PC08`
- 39 file dưới `acceptance/fixtures/` (5 README + 34 fixture, thuộc cả 6 nhóm)

Xuất hiện mới, không có trong FC-W3: `evidence/tools/e0_check.py` (80 109 byte), thư mục `evidence/runs/` (rỗng).

**Diễn giải.** Đây là PC09/W6 chạy song song, đúng như dispatch đã báo. Nhưng phạm vi ghi của PC09 rộng hơn
những gì dispatch mô tả (`scenarios.yaml`, `traceability.csv`, `gates.yaml`, `review.md`, e0 tool): nó đang
sửa fixture, handoff của gói khác, `precode/baseline.json` và một file trong `contracts/schemas/`.

**PC10 đã làm gì.** Không chép hash `FC-W3` (chúng đã sai với thực tế). Thay vào đó **tính lại hash trực tiếp**,
đặt tên pin epoch `PC10-PIN-20260907`, và ghi ở §0 của **từng** card đúng những file nào trong bảng của card
đó đã lệch khỏi FC-W3. Không có hash nào trên card là hash không kiểm được.

### 6.2 Change requests do PC10 phát sinh

| CR | Tới | Nội dung | Ảnh hưởng |
| --- | --- | --- | --- |
| `CR-PC10-01` | **Coordinator** | 48 file của `FC-W3` epoch 3 đã đổi trong lúc PC09 chạy (§6.1). Cần phát hành frozen candidate mới (`FC-W4`) **sau khi PC09 landing xong**, rồi pin lại §0 của cả 18 card. Cho tới lúc đó, không card nào được phát hành thi công. | **Chặn G5** |
| `CR-PC10-02` | **PC01** (`ports.yaml`) + **PC03** (`errors.yaml`, `run.yaml`) | Collector gặp rate limit của X không có đường báo hợp lệ. `collector-probe.md` §4 `ST-4` bảo dùng `RATE_LIMITED`; nhưng `worker.report_stop.error_codes` không có mã đó, `RATE_LIMITED.operations` không có operation nào của collector (file tự ghi *"Chưa được ports.yaml 0.1.0 tham chiếu … Xem CR-PC03-04"*), và `run.yaml` `stop_reason` không có giá trị nào cho rate limit. `RATE_LIMITED.target_states` đẩy về `stop_reason=source_blocked`, nhưng `errors.yaml` định nghĩa `source_blocked` là *"X không cho vào"* — rate limit thì X có cho vào. Ba cách hiểu cho ba hành vi UI khác nhau ở AC-15. | Chặn nhánh rate-limit của `TC-collector-checkpoint-resume` |
| `CR-PC10-03` | **PC01** (`capabilities.yaml`) | `telegram.send_payload` khai `CAPABILITY_DENIED` trong `error_codes`, nhưng **không actor nào** trong `contracts/capabilities.yaml` có `telegram.send_payload` hoặc `delivery.dispatch_next` trong `allowed_operations`. `ACT-server-domain-service` có `MOD-telegram-adapter` và `MOD-delivery-service` trong `module_refs` nhưng khai `network_scope: []` — mâu thuẫn với việc phải chạm `telegram_bot_api` để gửi. Không có bản ghi capability thì oracle của I11 (nội dung không đổi recipient) không đối chiếu được. | Chặn oracle `CAPABILITY_DENIED` của `TC-telegram-unknown-delivery` |
| `CR-PC10-04` | **PC09** | 5 file PC09 chưa landing (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `evidence/manifest.schema.json`, `precode/gates.yaml`, `precode/review.md`) và `evidence/index.json`. Hệ quả: §8 của mọi card chỉ trỏ tới **anchor** SC chứ không tới scenario đã viết; §13 phải mô tả manifest bằng 8 nhóm trường của SRC-PLAN §14.1 thay vì trỏ tới schema. Đề nghị PC09 xác nhận dải SC01–SC48 mà PC10 đã dùng và cấp SC mới cho phần còn thiếu. | Chặn G5 (cùng với CR-PC10-01) |

### 6.3 CR của gói khác mà PC10 xác nhận là **đang chặn card**

Những CR này không do PC10 tạo; PC10 chỉ ghi lại nơi chúng chặn, và đã đưa chúng thành stop condition tường
minh ở §10 của card liên quan.

| CR | Chặn card nào | Nội dung PC10 xác nhận |
| --- | --- | --- |
| `CR-PC07-04` | `TC-telegram-unknown-delivery`, `TC-telegram-linking-auth` | Giới hạn định dạng Telegram vẫn `KC`. `contracts/telegram/delivery.md` §3.5 yêu cầu tách `delivery_part` ở ranh giới mục, nhưng §3.4 khai độ dài tối đa một tin là `KC` và ghi *"Cấm suy ra giới hạn từ trí nhớ"*. **Không hiện thực được nhánh multipart.** Đây là gap chặn cứng lớn nhất PC10 tìm thấy. |
| `CR-PC05-03` | `TC-x-feasibility-probe` (§10 SG-04) | Nhịp gọi và yêu cầu định danh của arXiv/OpenAlex vẫn `KC`; **không nguồn đã pin nào chứa URL tài liệu**. |
| `CR-PC06-04` | `TC-analysis-adapter-validation` | Chưa adapter CLI/ACP nào qua probe ⇒ AC-16 báo **BLOCKED**, không phải FAIL. Card đặt trần claim đường CLI/ACP ở `CONTRACT_ONLY`. |
| `CR-PC08-04` | `TC-owner-auth-session` (§10 SG-01) | Chưa chốt **một** mã cho "token hợp lệ nhưng đi cạnh không được phép". |
| `CR-PC04-04` | `TC-report-coverage-publish-cas` (§10 SG-01) | `report.publish.error_codes` thiếu `CONFLICT` trong khi `errors.yaml` khai `CONFLICT.operations` có `report.publish`. |
| `CR-PC04-02`, `CR-PC04-08/09` | `TC-backfill-pending-ledger`, `TC-report-coverage-publish-cas` | `backfill_ledger` thiếu cột để ép add–remove–readd ở mức schema; `report.abort_reason` chưa có. |
| `CR-PC02-06` | `TC-canonical-identity-merge`, `TC-report-coverage-publish-cas` | Policy kế thừa `first_announced` sau merge chưa khóa ⇒ I07 còn lỗ hổng. |
| `CR-PC06-02`, `CR-PC06-01` | `TC-analysis-once-per-generation` | Enum `ENT-analysis-task` lệch `contracts/state/analysis.yaml`; timeout inference theo task chưa vào `retry-policy.yaml`. |
| `CR-PC08-05` | `TC-backup-restore-drill` | `ENT-restore-record` thiếu trường xác nhận của Operator mà `reconciliation_complete` đòi. |
| `CR-PC03-02` | `TC-scheduler-lease-claim` | Không operation nào đưa run rời `blocked` ngoài `run.cancel`. |
| `CR-PC02-12` | `TC-ingest-idempotent-ack-lost` | Diễn giải append-only của `TXN-checkpoint-only` chưa xác nhận. |
| `CR-PC07-01`, `-03`, `-05` | `TC-telegram-linking-auth` | Định dạng mã, hạn 15 phút, rate limit 5/chat/giờ, `telegram_update_max_age` 24 h, so sánh constant-time — đều PROVISIONAL hoặc chưa vào openapi. |

### 6.4 Giả định PROVISIONAL do PC10 đưa vào

PC10 **không** tạo quyết định sản phẩm mới. Ba giả định kỹ thuật, tất cả gắn nhãn PROVISIONAL trong file:

1. **Layout đường dẫn stack A** — `server/app/<domain>/…`, `collector/app/…`, `worker/app/…`,
   `server/app/web/…`, `probe/x_feasibility/…`, `tests/contract/…`, `tests/integration/…`. Đây là hệ quả
   của ADR-0006 chưa được Owner trả lời; nếu Owner chọn B/C thì chỉ §3 và §8 của card phải viết lại.
2. **Không gian ID mới:** `EVM-<Task ID>` cho evidence manifest của card, `SG-<nn>` cho stop condition trong
   card, `PC10-PIN-<ngày>` cho pin epoch. Chưa có ID nào trong baseline §3 phục vụ ba việc này. Nếu
   Coordinator muốn dạng khác, đổi được bằng một lần sửa generator.
3. **Trần claim `LIVE_FEASIBILITY_VERIFIED`** cho card SP1 (theo đúng chữ của packet) và `CONTRACT_ONLY` cho
   đường CLI/ACP của card adapter. Hai nhãn này chưa có trong bảng claim label của SRC-PLAN §2 mà packet chỉ
   định; ghi lại ở đây để Coordinator xác nhận.

### 6.5 Sai lệch định dạng có chủ đích

- **Card `TC-*.md` không mang contract header đầy đủ của baseline §3.** Chúng mang front-matter riêng của card
  (`card_id`, `milestone`, `gate`, `stack_decision`, `claim_ceiling`, `owner_modules`, `scenario_refs`,
  `invariant_refs`, `evidence_manifest_id`, `source_refs`, `baseline_pin_ref`, `coding_precondition`). Lý do:
  card không phải hợp đồng — nó là lệnh giao việc pin một hợp đồng. `producers`/`consumers`/`dependencies`
  của baseline §3 không có nghĩa với một card; thông tin tương đương nằm ở §4, §5 và §11. Bốn file "khung"
  (`TEMPLATE.md`, `README.md`, `WALKTHROUGH.md`, `precode/change-control.md`, `precode/README.md`) **có** mang
  contract header đầy đủ. Nếu Coordinator muốn card cũng mang header đầy đủ, đó là một lần sửa generator.
- **`precode/README.md` và `precode/change-control.md` không tự pin hash của chính mình** trong §0 của card
  (chicken-and-egg). Hash của chúng nằm ở bảng §2 của handoff này.

## 7. Điều PC10 **không** thiết lập được

Theo mẫu SRC-PLAN §14.3, phần "Not established":

- **Không** chứng minh bất kỳ card nào là đủ để một agent hoàn thành công việc. Walkthrough là self-review
  trên 2/18 card, và chính nó tìm ra 4 gap.
- **Không** chứng minh baseline hợp đồng tự nhất quán — đó là E0 của PC09, PC10 `NOT_RUN`.
- **Không** chứng minh stack Option A là lựa chọn đúng. ADR-0006 vẫn `proposed`.
- **Không** chứng minh 18 card là **đủ** để phủ P0. Traceability đầy đủ là của PC09
  (`acceptance/traceability.csv`, chưa tồn tại). Card được chọn theo danh sách của packet + SRC-PLAN §15;
  chưa ai kiểm ngược rằng mọi REQ-P0-01…12 đều có ít nhất một card.
- **Không** chứng minh giá trị PROVISIONAL nào (N=7 ngày, 200 post/30 phút, 08:00–20:00, `Asia/Ho_Chi_Minh`,
  15 phút cho mã liên kết, 24 h cho update age) là đúng.

## 8. Đề nghị cho Coordinator

1. Chờ PC09 landing, phát hành `FC-W4`, rồi pin lại 18 card (`CR-PC10-01`). Generator ở
   `…/scratchpad/w7/gen_cards.py` sinh lại toàn bộ từ hash live trong một lần chạy.
2. Định tuyến `CR-PC10-02` và `CR-PC10-03` tới PC01/PC03 — cả hai là mâu thuẫn nội bộ giữa các file đã đóng
   băng, sửa được trong phiên này.
3. Đưa `CR-PC07-04` và `CR-PC05-03` vào `precode/owner-decision-request.md` như **việc cần một bước có mạng**,
   không phải quyết định sản phẩm. Chúng không đóng được bằng cách viết thêm hợp đồng.
4. Xác nhận ba nhãn mới ở §6.4 mục 2 và 3.
5. Gửi card này cho một Auditor: `audit_route` của packet là `INDEPENDENT_REQUIRED`, và PC10 mới chỉ có
   self-validation.

---

*PKT-PC10 · worker-W7 · claim ceiling `DRAFT_FOR_REVIEW` · không có mục nào trong file này là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX1

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX1` · authority `AUTH-COORD-PC10-FIX1` · lease `LEASE-PC10-e2` (fencing 2) |
| expires_at | 2026-09-07T14:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | Rulings **R5-07** (FIX5 wave) + rulings của Coordinator trên PC10-handoff §6.4 |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T00:22Z / 2026-09-07T00:41Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T00:41Z |
| **pin epoch mới** | **`PC10-PIN-FCW4-20260907`** (thay `PC10-PIN-20260907`) |

## A.0 Wait gate

Poll `evidence/handoffs/PC08-handoff.md` mỗi 60 s. **`GATE_OPEN` ở poll 2 (00:29:36Z)**: ADDENDUM
`PKT-PC08-FIX2` tồn tại (dòng 322) với `lease_released_at 2026-09-07T00:28Z`. Không phải timeout, không phải
pin-anyway — không file nào "ở trạng thái rủi ro". Generator chỉ chạy **sau** khi cổng mở.

Bốn hash Coordinator khai là ổn định đều được xác nhận trước khi pin: `entities.yaml` `4d93232f…`,
`modules.yaml` `fa7af494…`, `run.yaml` `852da496…`, `analysis.yaml` `978004cd…`, `ports.yaml` `87c95da4…`.

## A.1 Rulings đã thi hành

| Ruling | Đã làm gì |
| --- | --- |
| (a) ID space `EVM-`, `SG-`, `PC10-PIN-` | Giữ nguyên; nay được khai tường minh ở `agent-tasks/README.md` §5.1 |
| (b) `CONTRACT_ONLY` **không** hợp lệ | Gỡ khỏi toàn bộ baseline. `TC-analysis-adapter-validation` nay: API `IMPLEMENTATION_VERIFIED`, đường CLI/ACP dừng ở **`CONTRACT_READY`**. `TEMPLATE.md` §9 liệt kê đúng 6 nhãn SRC-PLAN §2. EV-PC10-01 có check mới (i) fail mọi nhãn ngoài tập đó. `LIVE_FEASIBILITY_VERIFIED` giữ cho card SP1 |
| (c) Ngoại lệ front-matter của card | Khai ở `agent-tasks/README.md` §5.1 với đủ 12 khóa bắt buộc và lý do (card không phải hợp đồng, nó *pin* hợp đồng); nêu rõ 4 file khung **có** mang contract header |
| (d) `CR-PC09-07` | `precode/change-control.md` §4 viết lại: **dẫn** `INV-01`…`INV-10` của `precode/gates.yaml`, không định nghĩa lại. Bảng mới là bảng tra "sửa gì → đọc quy tắc nào" + tóm tắt một dòng. Front-matter thêm `invalidation_rule_refs` |
| (e) `CR-PC10-01` re-pin | 18 card pin lại bằng generator. **483 dòng hash / 143 file riêng** (trước: 426 / 128). File PC09 **không** pin hash — dẫn bằng path + SC id, có check (j) trong EV-PC10-01 để fail nếu ai đó pin nhầm |
| (e) SC01–SC53 | `GROUNDED_SC` mở tới SC53; `SC49` thêm vào **cả 18 card**; `SC50` (e2e) trên 4 card trục chính — ingest, collector, report, delivery; `SC33`–`SC36`, `SC32`, `SC44`, `SC52`, `SC53`, `SC10`, `SC51` gắn vào card sở hữu hành vi |
| (f) stop conditions mới | `SG-RATE` (collector), `SG-TERMS` (adapter), `SG-CSRF` (auth), `SG-DENY` (mọi card) — xem A.3 |
| (g) `precode/README.md` | Bản đồ thư mục cập nhật 9 nhóm fixture (3 nhóm mới), 6 file PC09 chuyển "chưa có" → "có đủ", lệnh E0 kèm run thật `E0-20260906T193716Z` |

## A.2 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `precode/README.md` | MODIFY | `7231737d…` / 12966 | `8eb263718eb2b949e06c10784bee212a49af3c8ed04b699d46b5f3809c72e3b3` / 14078 |
| `precode/change-control.md` | MODIFY | `baf10e03…` / 13696 | `5cc1e461ed7bd11aa14664681120557d4a2774e09f6b2ad2cb358433df976468` / 15847 |
| `agent-tasks/README.md` | MODIFY | `74f5edd3…` / 9381 | `184d051c35d9e68848152cdd8a8452ad8534bb9384b8920284f094b28696bf7c` / 12992 |
| `agent-tasks/TEMPLATE.md` | MODIFY | `035c1302…` / 10424 | `750d8f2eff258719c9a943848634ba88f3fb9f7ac8afb935e4eedb4512f3e4ff` / 11675 |
| `agent-tasks/WALKTHROUGH.md` | MODIFY | `d9919c8e…` / 13750 | `396141f190e5002a8792cba7ba0a05b5e5f69b916d86de2b025e76bc897918f5` / 16780 |
| `agent-tasks/TC-analysis-adapter-validation.md` | MODIFY | `e0caca68…` / 19267 | `db492dfb2d18f435eeeb23054bb805c213dd761d012e4d1c5fea81a4e469e872` / 21887 |
| `agent-tasks/TC-analysis-once-per-generation.md` | MODIFY | `75173c9a…` / 17846 | `ffd618aec6bca906b2b113953fc06cd31d9570d0cdf52531b7fa81f32383caaa` / 19587 |
| `agent-tasks/TC-backfill-pending-ledger.md` | MODIFY | `2475a7ba…` / 16286 | `25c66514fd2bd97429e30dd57df5547c1cf2c3128e18b89e75285f2a58d5d8de` / 18069 |
| `agent-tasks/TC-backup-restore-drill.md` | MODIFY | `42e13d6e…` / 16976 | `a7ac4fc8bae27fe4abdb20246d1b1de45e7e9d080584581f83f8c13368323a79` / 19251 |
| `agent-tasks/TC-canonical-identity-merge.md` | MODIFY | `44dc9aeb…` / 18295 | `ae87f10603f6b6256e3579cb70bfe129802fd71a9b4e881773c95e4e86a862c1` / 19701 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | MODIFY | `1b210b49…` / 19515 | `f2dab8bb032ebd068ffdb5b5b215a4f5086a25d63cec300199a50066eb1afe1f` / 21885 |
| `agent-tasks/TC-embedding-generation-switch.md` | MODIFY | `82dcb5f3…` / 15830 | `7e957d02dcf69199cb1786bbb8e4f4f66d2da9b0166b12696d0cc083aed5a748` / 17784 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | MODIFY | `70639e84…` / 21128 | `d4766bed665fc3f5dc228ea3a203dd6f7fc6c0109ba9ab44366e42c5e03711a4` / 23090 |
| `agent-tasks/TC-owner-auth-session.md` | MODIFY | `02278e05…` / 16457 | `ee41f7c5eae486103b9306b08934c1b065f57a0672fff0013d9e32496ad1c6f3` / 18983 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | MODIFY | `4342defa…` / 19498 | `cd59b43488a7cc4f204c6539ae41f43f87895e619a9a4c400425b9d4c788e829` / 21403 |
| `agent-tasks/TC-saved-snapshot.md` | MODIFY | `760411fa…` / 18030 | `4f888f9107daf912a9708050db7b49ce39dfcbc69129e0d633c2a25bcb8d871f` / 19722 |
| `agent-tasks/TC-scheduler-lease-claim.md` | MODIFY | `275e2ae3…` / 18343 | `0fbdfd3ca92e887929f5830d4c2c06a023466e90a84f838d810c61fd5d375928` / 20541 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | MODIFY | `8dc15f46…` / 15936 | `5b16d886c07b1b267a1e123d0aeae2ee5a8cd92be13f250f70eb57d8b5cbea41` / 17903 |
| `agent-tasks/TC-telegram-linking-auth.md` | MODIFY | `5ddd4187…` / 18795 | `0d654a6a8faf9de0aafab761f728f81fb23e00cf155b9204338bd29a6b3dc194` / 20118 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | MODIFY | `5f5e9433…` / 19175 | `baef2075cfa30ff10b82e74299da20e3050e75df2bd42399099189130f018401` / 20978 |
| `agent-tasks/TC-ui-reports-detail.md` | MODIFY | `bab37008…` / 17000 | `f3cda5620f1519299267b372b96e30bc634721fb2e4015277bfe5847385d2515` / 19016 |
| `agent-tasks/TC-ui-runs-three-states.md` | MODIFY | `6ab9d706…` / 16972 | `85e18606722231d8e5b77f41d7744bb3d99b1f70aecfe2fca14d1af31aa25597` / 18418 |
| `agent-tasks/TC-x-feasibility-probe.md` | MODIFY | `2503bc9b…` / 15564 | `29e942d3305edfbe31eb1eb1ab36f3710ff01fb69fc6d7ec11be68bf57f4c26c` / 17346 |

**23 file MODIFY. 0 CREATE, 0 DELETE.** Không ghi ngoài grant (`agent-tasks/*`, `precode/change-control.md`,
`precode/README.md`, handoff này). Không `__pycache__`; script chạy từ `…/scratchpad/w7/`; không lệnh git;
không mạng.

## A.3 Stop condition mới trên card

| ID | Card | Nội dung |
| --- | --- | --- |
| `SG-RATE` | `TC-collector-checkpoint-resume` | Rate limit của X là **`partial`, không phải `blocked`**. `stop_reason = rate_limited`, mã `RATE_LIMITED`, transition `T-RUN-25` → `running/enriching`. Cấm: đưa về `blocked`, thử lại trong cùng đợt, để `run.x_coverage_note_vi` trống (nó bắt buộc nhắc mốc `run.rate_limited_at`) |
| `SG-TERMS` | `TC-analysis-adapter-validation` | Cổng `provider_config.terms_check_at` (`CR-PC07-07`): ràng buộc `ck_provider_config_terms_before_enable` — `enabled = 0 OR terms_check_at IS NOT NULL`. Không bật đường CLI/ACP của một nhà trước khi owner xác nhận đã đọc điều khoản của **chính nhà đó** (REQ-A5, ADR-0010). Đây là mốc ghi nhận, không phải bằng chứng về nội dung |
| `SG-CSRF` | `TC-owner-auth-session` | `CSRF_REJECTED` là 403 và **không** hủy phiên; khác `FORBIDDEN_EDGE` (cạnh vẫn hợp lệ). `CR-PC08-04` nay đóng bằng bảng R5-01: token đi sai cạnh qua HTTP là `UNAUTHORIZED` (401) |
| `SG-DENY` | **cả 18 card** | Nghĩa vụ default-deny: mọi cạnh trong 36 `forbidden_edges` chạm module của card phải bị từ chối bằng **đúng** mã của bảng R5-01. Sai mã cũng là FAIL. Oracle `SC49` + `boundary/a-default-deny-sweep-36-edges.json` |

§5 của mọi card nay mang nguyên bảng ranh giới R5-01 bốn hàng.

## A.4 Evidence (chạy lại)

### EV-PC10-01 (lần 2) — pin hash, path, ref, nhãn claim, ngoại lệ PC09

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T00:38Z / 2026-09-07T00:39Z |
| `oracle` | (a) mọi dòng hash tính lại = file live; (b) mọi path tồn tại; (c) operation ID ∈ `ports.yaml`; (d) SC ∈ SC01–SC53 **và** mỗi SC được ít nhất một fixture định nghĩa; (e) mã lỗi §7 ∈ `errors.yaml`; (f) `MOD-*` ∈ `modules.yaml`; (g) `I<nn>` ∈ I01–I17; **(h) mới:** mọi card có `SC49` + đủ 4 hàng bảng R5-01 ở §5 + tham chiếu fixture boundary; **(i) mới:** mọi nhãn claim ∈ SRC-PLAN §2; **(j) mới:** không file PC09 nào bị pin hash |
| `observed` | **483 dòng hash (143 file) khớp 100 %**; 687 path; 155 operation; 116 SC (mọi SC có fixture); 99 mã lỗi §7; 18/18 card có SC49 + bảng R5-01 + fixture boundary; 0 nhãn ngoài §2; 0 file PC09 bị pin |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Ba token trường mới (`run.rate_limited_at`, `run.x_coverage_note_vi`, `provider_config.terms_check_at`) ban đầu bị oracle đọc nhầm là operation ID. Đã thêm vào bảng `FIELD_TOKENS` — nơi mỗi token được **kiểm ngược** phải xuất hiện trong hợp đồng sở hữu nó (`run.yaml`, `entities.yaml`), chứ không phải bị bỏ qua. Không dòng nội dung card nào bị sửa để làm check pass. |

### EV-PC10-02 (lần 2) — 14 mục TEMPLATE

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Nguồn — kiểm trước và sau

`research-radar-spec.md` `d35e1f2d…` và `research-radar-pre-code-plan.md` `f65bb046…`: **khớp cả hai lần**.
`INV-08` không trigger.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py` (PC10 không chạy; E0 chính thức là của PC09), validator OpenAPI 3.1, mọi test
E1–E4, probe SP1, probe CLI/ACP.

## A.5 CR đã đóng ở vòng này

| CR | Đóng bằng | Bằng chứng |
| --- | --- | --- |
| `CR-PC10-01` (drift khỏi FC-W3) | Pin lại 18 card ở `PC10-PIN-FCW4-20260907` sau khi cổng PKT-PC08-FIX2 mở | EV-PC10-01 lần 2: 0 sai lệch trên 483 dòng |
| `CR-PC10-02` (rate limit không có đường báo) | Hợp đồng đã sửa: `stop_reason = rate_limited`, `RATE_LIMITED` trong `worker.report_stop.error_codes`, `T-RUN-25`, `run.rate_limited_at` | `contracts/state/run.yaml`, `contracts/ports.yaml`; card `SG-RATE` |
| `CR-PC10-03` (không actor nào khai `telegram.send_payload`) | `ACT-delivery-dispatcher` mới, `network_scope: [telegram_bot_api]` | `contracts/capabilities.yaml` |
| `CR-PC10-04` (file PC09 chưa landing) | Cả 6 file đã có; SC01–SC53 đều có fixture | `acceptance/scenarios.yaml`, `precode/gates.yaml`, … |
| `CR-PC08-04` (mã cho token đi sai cạnh) | Bảng ranh giới R5-01 | card `SG-CSRF` |

Cả bốn CR của PC10 đóng bằng **sửa hợp đồng**, không phải bằng nới lỏng card.

## A.6 CR còn lại

| CR | Trạng thái | Vì sao chưa đóng |
| --- | --- | --- |
| **`CR-PC07-04`** | **OPEN — chặn** | Giới hạn định dạng Telegram vẫn `KC`. `delivery.md` §3.5 đòi tách `delivery_part` ở ranh giới mục, §3.4 để độ dài tối đa một tin là `KC` và ghi "Cấm suy ra giới hạn từ trí nhớ". **Chặn nhánh multipart của `TC-telegram-unknown-delivery` và một phần AC-14.** Cần một bước **có mạng** đọc <https://core.telegram.org/bots/api#sendmessage> — không sửa được bằng cách viết thêm hợp đồng |
| `CR-PC05-03` | OPEN | Nhịp gọi arXiv/OpenAlex `KC`; không nguồn đã pin nào chứa URL. Cùng loại: cần bước có mạng |
| `CR-PC06-04` | OPEN | Chưa adapter CLI/ACP nào qua probe ⇒ AC-16 **BLOCKED**, đường CLI/ACP dừng ở `CONTRACT_READY` |
| REQ-OQ01 / SP1 | `OWNER_DECISION_REQUIRED` | D09 chưa xác nhận ⇒ chặn M0 và chặn probe |
| REQ-OQ02 (ADR-0006) | `proposed` | §3 và §8 của mọi card vẫn PROVISIONAL |
| REQ-OQ03 | `OWNER_DECISION_REQUIRED` | Không có provider/model mặc định an toàn |
| `data.purge_all` loại trừ | `OWNER_DECISION_REQUIRED` | Cụm "toàn bộ dữ liệu" không suy ra được |
| Validator OpenAPI 3.1 | `NOT_RUN` | Chưa ai chạy trong Pre-code |

**Không CR mới nào phát sinh ở vòng này.**

## A.7 Điều vẫn **không** thiết lập được

Mục §7 của bản gốc giữ nguyên giá trị, trừ hai điểm nay đã cải thiện: file PC09 đã tồn tại nên §8 của card trỏ
tới scenario **đã viết**; và `acceptance/traceability.csv` nay cho phép kiểm ngược "mọi REQ-P0 có card chưa" —
**PC10 chưa chạy phép kiểm đó**, nên câu hỏi "18 card có đủ phủ P0 không" vẫn **chưa được trả lời**.

`status` là `DONE_WITH_CONCERNS` chứ không `DONE` vì `CR-PC07-04` còn chặn một nhánh, và vì PC10 mới chỉ có
self-validation trong khi `audit_route` là `INDEPENDENT_REQUIRED`.

---

*PKT-PC10-FIX1 · worker-W7 · `lease_released_at` 2026-09-07T00:41Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX2

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX2` · authority `AUTH-COORD-PC10-FIX2` · lease `LEASE-PC10-e3` (fencing 3) |
| expires_at | 2026-09-07T14:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | PC01-FIX8/FIX9 đã đổi hai file có pin trên card sau lần re-pin FIX1 |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T00:48Z / 2026-09-07T00:56Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T00:56Z |
| **pin epoch mới** | **`PC10-PIN-FCW4b-20260907`** (thay `PC10-PIN-FCW4-20260907`) |

## B.1 Xác nhận đầu vào trước khi pin

Ba file Coordinator nêu, kiểm bằng `sha256sum` — **khớp chính xác cả hash lẫn byte count**:

| Path | SHA-256 | Bytes |
| --- | --- | --- |
| `contracts/modules.yaml` | `9846a2be3d5497f50b43d9e001e8dde609a8eb31ed9b281cad0d8c4175524757` | 100130 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `ffab4679078e8d93227bb2751743482b44981ec6a84de1f404a389f59ec0213e` | 29904 |
| `acceptance/fixtures/boundary/README.md` | `201b2e2c3d77f2d70e3e263d45d8dfb440bc266c8fbaac76260e151bb09dc583` | 8582 |

Nguồn không đổi: `research-radar-spec.md` `d35e1f2d…`, `research-radar-pre-code-plan.md` `f65bb046…`.
`INV-08` không trigger.

**Kiểm tính nhất quán nội dung sau khi `modules.yaml` đổi** (không chỉ hash): số `forbidden_edges` vẫn là
**36** và số `MOD-*` vẫn là **25**, nên khẳng định "36 `forbidden_edges`" mà mọi card mang ở §5 và `SG-DENY`
vẫn đúng. Số `denied_cases` `NC-*` tăng từ 10 lên **36** — đúng như ruling R5-01 yêu cầu (mỗi cạnh bị cấm có
một `denied_cases[]` với `expected_error_code`), nên đây là thay đổi **củng cố** nghĩa vụ default-deny của
card chứ không mâu thuẫn với nó.

## B.2 Drift — trả lời câu hỏi của packet

Generator tính lại **toàn bộ** 483 dòng hash trên 143 file riêng, không chỉ ba file được nêu. So bảng pin
trước (`PC10-PIN-FCW4-20260907`) với bảng pin sau:

**Đúng 3 file đổi, không hơn.** Ba file đó chính là ba file Coordinator đã nêu. **Không có drift nào ngoài
phạm vi đã báo** — 140/143 file còn lại giữ nguyên hash và byte count.

## B.3 Changes

18 card `MODIFY`. Không file nào khác bị chạm: `TEMPLATE.md`, `README.md`, `WALKTHROUGH.md`,
`precode/change-control.md`, `precode/README.md` **không đổi** ở vòng này (nội dung của chúng không phụ thuộc
ba file trên; `agent-tasks/README.md` dẫn pin epoch qua tên epoch trong card, và mục §4 của nó đã nói epoch
hiện hành được ghi ở §0 của card).

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `agent-tasks/TC-analysis-adapter-validation.md` | MODIFY | `db492dfb…` / 21887 | `93fb7f96dd2468d514ce82740ef81d79b1bdf201798a39d2dca7a58623d4ef6b` / 21970 |
| `agent-tasks/TC-analysis-once-per-generation.md` | MODIFY | `ffd618ae…` / 19587 | `78f7be54cb8888b22662513ebaed0d181ec1c05c5f77aa6d3d82a0b7aedc1317` / 19670 |
| `agent-tasks/TC-backfill-pending-ledger.md` | MODIFY | `25c66514…` / 18069 | `26f0db6bb60fc4dc339897fead783d074135e13d4a04c66fdbfc543ae3d2340c` / 18152 |
| `agent-tasks/TC-backup-restore-drill.md` | MODIFY | `a7ac4fc8…` / 19251 | `c5c5f82201901332167cfa72450363fd212d0f971a6b818662796c060b97eb6e` / 19334 |
| `agent-tasks/TC-canonical-identity-merge.md` | MODIFY | `ae87f106…` / 19701 | `ddf20208b931bf031c77f877a0940431d6cf7c4b584a4a47e999d7eea908d369` / 19784 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | MODIFY | `f2dab8bb…` / 21885 | `29b04b3601c05e95191966750feca1fb85505287098b51342f6af10099c5fbb2` / 21968 |
| `agent-tasks/TC-embedding-generation-switch.md` | MODIFY | `7e957d02…` / 17784 | `4bc71033a163fa4c129a40a9a0bc6026814355462bdc620e1f2a8cc1418a4af3` / 17867 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | MODIFY | `d4766bed…` / 23090 | `6cdf59523a46b53289abf284ae6c6bd6b4cb8f27b14a283d6d565c2c6349d3f1` / 23173 |
| `agent-tasks/TC-owner-auth-session.md` | MODIFY | `ee41f7c5…` / 18983 | `4f6d77b84fd3f25ecb80ad77d1b1abd9a3ccd92aebe177d3fa4568a386069bc9` / 19066 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | MODIFY | `cd59b434…` / 21403 | `9faa115604868f07b97332161dfd916c19db563c3ba1d0913dcc3de77b1742e9` / 21486 |
| `agent-tasks/TC-saved-snapshot.md` | MODIFY | `4f888f91…` / 19722 | `ee8ba2832b20f8ca57c1ce974c4c09e8704d8a7cdd13308d733393985fe1f2d4` / 19805 |
| `agent-tasks/TC-scheduler-lease-claim.md` | MODIFY | `0fbdfd3c…` / 20541 | `ad08f45026644bf9a3d751234405678938d64bfc561cc804202c71819e36f30c` / 20624 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | MODIFY | `5b16d886…` / 17903 | `84b2c7c064f1c81385066110672071adfdd9ea22f87951871bb9d8d261eea71f` / 17986 |
| `agent-tasks/TC-telegram-linking-auth.md` | MODIFY | `0d654a6a…` / 20118 | `71ca88ca69e112b47c93d01222560cae54ff3249464e5c81f1cb43d253719020` / 20201 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | MODIFY | `baef2075…` / 20978 | `8bada8403a3a151c8d0b41e3322886a04b043247007d9c3dee45963bf7a86f16` / 21061 |
| `agent-tasks/TC-ui-reports-detail.md` | MODIFY | `f3cda562…` / 19016 | `fb91365cdc994981c66d4d544e7d283333becaa2b4dc52435cd998cd35319687` / 19099 |
| `agent-tasks/TC-ui-runs-three-states.md` | MODIFY | `85e18606…` / 18418 | `17b22632ea6f4d52e508774e44846f59a091e435fef835328cc86f45eabc06bd` / 18501 |
| `agent-tasks/TC-x-feasibility-probe.md` | MODIFY | `29e942d3…` / 17346 | `7dad6b03d9b1628fac67b6f906798ebb946a5606abc09ec6eefa71178e21fd5b` / 17429 |

**18 file MODIFY. 0 CREATE, 0 DELETE.** Không ghi ngoài grant `agent-tasks/*` + handoff này. Không
`__pycache__`; generator và verifier chạy từ `…/scratchpad/w7/`; không lệnh git; không mạng.

Chênh lệch byte của mỗi card là **+83**, đúng bằng độ dài phần văn bản epoch mới ở §0 — dấu hiệu nhất quán
rằng ngoài epoch và ba dòng hash, nội dung card không đổi.

## B.4 Evidence (chạy lại lần 3)

### EV-PC10-01 (lần 3)

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T00:54Z / 2026-09-07T00:55Z |
| `oracle` | Không đổi so với FIX1: mười phép kiểm (a)…(j) |
| `observed` | **483 dòng hash / 143 file khớp 100 %**; 669 path; 155 operation ID; 116 SC (mọi SC có fixture); 99 mã lỗi §7; 18/18 card có `SC49` + đủ 4 hàng bảng R5-01 ở §5 + tham chiếu fixture boundary; 0 nhãn claim ngoài SRC-PLAN §2; 0 file PC09 bị pin hash |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Vẫn là self-validation. Verifier không đổi ở vòng này — không thêm luật, không nới luật nào. |

### EV-PC10-02 (lần 3)

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py` (E0 chính thức là của PC09), validator OpenAPI 3.1, mọi test E1–E4, probe SP1,
probe CLI/ACP.

## B.5 CR — không đổi

Không CR mới. Không CR nào đóng ở vòng này. Danh sách còn lại y như ADDENDUM PKT-PC10-FIX1 §A.6, trong đó
**`CR-PC07-04` vẫn OPEN và vẫn chặn** nhánh multipart của `TC-telegram-unknown-delivery` — giới hạn định dạng
Telegram còn `KC` và cần một bước có mạng.

`status` là `DONE_WITH_CONCERNS` chứ không `DONE`, vì hai lý do không đổi: `CR-PC07-04` còn chặn, và
`audit_route` là `INDEPENDENT_REQUIRED` trong khi PC10 mới chỉ có self-validation. Thêm một điểm đã nêu ở
§A.7 và vẫn đúng: **PC10 chưa chạy phép kiểm ngược "mọi `REQ-P0-*` có ít nhất một card"** trên
`acceptance/traceability.csv`, nên câu hỏi "18 card có phủ đủ P0 không" vẫn chưa được trả lời.

---

*PKT-PC10-FIX2 · worker-W7 · `lease_released_at` 2026-09-07T00:56Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX3

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX3` · authority `AUTH-COORD-PC10-FIX3` · lease `LEASE-PC10-e4` (fencing 4) |
| expires_at | 2026-09-07T16:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | Finding **`F-A2R1-03`** (A2-R1 audit) + PC01-FIX10/FIX11 và PKT-PC00-FIX6 đổi file có pin |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T01:02Z / 2026-09-07T01:26Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T01:26Z |
| **pin epoch mới** | **`PC10-PIN-FCW4c-20260907`** (thay `PC10-PIN-FCW4b-20260907`) |

## C.0 Wait gate

Poll `evidence/handoffs/PC00-handoff.md`. **`GATE_OPEN` lúc 01:20:01Z** (poll 3): ADDENDUM `PKT-PC00-FIX6`
(dòng 736, worker-W1, lease `LEASE-PC00-e7` fencing 7) với `lease_released_at 2026-09-07T01:19Z`. Không
timeout; generator chỉ chạy **sau** khi cổng mở, nên `precode/decision-register.md` được pin ở trạng thái W1
đã hoàn tất. Hai hash Coordinator xác nhận sau đó khớp đúng cái generator đã pin: `precode/baseline.json`
`a6c52229…`, `precode/decision-register.md` `43d41b04…`.

Nguồn không đổi trước và sau: `research-radar-spec.md` `d35e1f2d…`, `research-radar-pre-code-plan.md`
`f65bb046…`. `INV-08` không trigger.

## C.1 `F-A2R1-03` — sửa nguyên nhân, không chỉ sửa triệu chứng

Finding: `precode/README.md` §6 (dưới đúng tiêu đề "**Pin hiện tại**") và `precode/review.md` §9.1 khẳng định
epoch `PC10-PIN-FCW4-20260907` trong khi 18/18 card đã mang `PC10-PIN-FCW4b-20260907`. Ràng buộc khắc phục mà
audit đặt ra: *"tên epoch phải được lấy từ card, không chép tay, để một lần pin lại sau này không bỏ hai file
này ở lại."*

Triệu chứng thì sửa một dòng là xong. Nguyên nhân là **một quy tắc không được máy kiểm**. Đã làm cả hai:

1. **Sửa nội dung.** `precode/README.md` và `agent-tasks/README.md` nay nêu `PC10-PIN-FCW4c-20260907`, liệt kê
   chuỗi epoch bị thay theo thứ tự, và **kèm lệnh đọc tên epoch từ chính card**:
   `grep -ho 'Pin epoch: \`PC10-PIN-[A-Za-z0-9-]*\`' agent-tasks/TC-*.md | sort -u` — phải ra đúng một dòng.
   `precode/README.md` nói thẳng với người đọc: *"Đừng tin dòng trên — kiểm nó."*
2. **Thêm phép kiểm bằng máy — EV-PC10-01 check (k).** Nó lấy epoch từ §0 của 18 card (18 card phải đồng
   thuận **đúng một** giá trị; bất đồng là FAIL), rồi bắt buộc `precode/README.md`, `agent-tasks/README.md`,
   `agent-tasks/TEMPLATE.md` và `agent-tasks/WALKTHROUGH.md` phải nêu đúng epoch đó. Một epoch cũ chỉ hợp lệ
   khi cùng đoạn văn có dấu hiệu kể lịch sử. **Epoch là dữ liệu dẫn xuất từ card, không phải hằng số chép
   tay.**
3. **Card tự khai vai trò nguồn chuẩn.** §0 của mọi card nay có câu: *"Card là nguồn chuẩn của tên epoch; mọi
   file khác khẳng định pin hiện hành phải đọc tên từ đây, không chép tay (finding `F-A2R1-03`)."*

**Check (k) bắt được một lỗi thật ngay lần chạy đầu**, ngoài hai file mà audit đã nêu:
`agent-tasks/WALKTHROUGH.md` dòng 41 (bảng tóm tắt GAP-C2) vẫn khẳng định `PC10-PIN-FCW4-20260907`. Audit
không nêu file này. Đã sửa. Đó chính là lý do ràng buộc "phải kiểm bằng máy" đúng: sửa tay theo danh sách của
audit sẽ bỏ sót đúng file thứ ba.

Lần chạy đầu của check (k) còn cho 7 hit nữa, **đều là false positive** do oracle đọc theo **dòng** trong khi
Markdown ngắt câu qua nhiều dòng. Đã sửa oracle sang đọc theo **đoạn văn** và mở rộng tập dấu hiệu lịch sử.
Không dòng nội dung nào bị sửa để làm check pass — ngược lại, một nội dung sai đã bị check phát hiện và sửa.

### Ngoài phạm vi grant — CR mới

> **`CR-PC10-05` → PC09 (`precode/review.md`).** Nửa còn lại của `F-A2R1-03` nằm ở `precode/review.md` §9.1,
> file PC10 **không** có quyền ghi. Nó vẫn khẳng định 18 card "được pin lại theo epoch
> `PC10-PIN-FCW4-20260907`" — nay sai hai thế hệ (`FCW4` → `FCW4b` → `FCW4c`). Đề nghị PC09 đọc tên epoch
> bằng lệnh ở `agent-tasks/README.md` §4 thay vì chép, và cân nhắc đưa `precode/review.md` vào tập
> `ASSERTING_FILES` của check (k). PC10 đã cố ý **không** chạm file đó (baseline §6: ngoài allowlist ⇒
> BLOCKED_SCOPE, không tự ghi).

## C.2 Drift — trả lời câu hỏi của packet

Generator tính lại **toàn bộ** 483 dòng hash trên 143 file, không chỉ file được nêu. So bảng pin `FCW4b` với
`FCW4c`: **đúng 7 file đổi**, và cả 7 nằm trong danh sách packet đã nêu.

| File có pin đã đổi | Bytes mới |
| --- | --- |
| `contracts/modules.yaml` | 103511 |
| `contracts/ports.yaml` | 124906 |
| `contracts/data/entities.yaml` | 217143 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | 31529 |
| `acceptance/fixtures/boundary/README.md` | 10598 |
| `precode/baseline.json` | 95611 |
| `precode/decision-register.md` | 97034 |

**Không có drift nào ngoài danh sách** — 136/143 file còn lại giữ nguyên hash và byte count.

## C.3 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `precode/README.md` | MODIFY | `8eb26371…` / 14078 | `4e8e1ce05fc900be029fa40e387bb8360ccc434f3db50e01db69a5c1fb77d9a6` / 14771 |
| `agent-tasks/README.md` | MODIFY | `184d051c…` / 12992 | `0db71dec926cc90b750049fe508b7b0c96d111ebf23e7c1a1f730ae55370f349` / 14079 |
| `agent-tasks/TEMPLATE.md` | MODIFY | `750d8f2e…` / 11675 | `92629c77c105e6989e041e9a2cb37d64fc4b19dcdd8cb84bf9d4416abde9fcb1` / 11961 |
| `agent-tasks/WALKTHROUGH.md` | MODIFY | `396141f1…` / 16780 | `171d01da11f9b746a4c8efb660f7061526321d94eb8a70b6ddab5cbc1a02a2ad` / 17048 |
| `agent-tasks/TC-analysis-adapter-validation.md` | MODIFY | `93fb7f96…` / 21970 | `e324d6bf11e8def6cd3300025a5968fe968e883a27d4122a99c6d229fe460049` / 22023 |
| `agent-tasks/TC-analysis-once-per-generation.md` | MODIFY | `78f7be54…` / 19670 | `91a908ab2f0dd0d81798868216d2570257a2bc2b1f9f91f6c2125bf79de38c59` / 19723 |
| `agent-tasks/TC-backfill-pending-ledger.md` | MODIFY | `26f0db6b…` / 18152 | `18b11aca9aa52e5cbe519a3fbe6a3eca6bc57064fee161f0b2a109e61a347e33` / 18205 |
| `agent-tasks/TC-backup-restore-drill.md` | MODIFY | `c5c5f822…` / 19334 | `b3e5a3d7221f08425ef17ec86c746268d141971a1b00e92725cf7a3c6f06498d` / 19387 |
| `agent-tasks/TC-canonical-identity-merge.md` | MODIFY | `ddf20208…` / 19784 | `e1d2956a8b96930addc78b49bff42f7c8192cd8f26a01536ef9390fe8e0937fc` / 19837 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | MODIFY | `29b04b36…` / 21968 | `a6fd14dedca984b0c9e9bc07eca548309943bf08759d8115d6bfdd8283f39511` / 22021 |
| `agent-tasks/TC-embedding-generation-switch.md` | MODIFY | `4bc71033…` / 17867 | `c196a5c2c92a7457a2cf3c38e938f318499f68ee18bdbcacab13956afed21497` / 17920 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | MODIFY | `6cdf5952…` / 23173 | `1d55bd56e0330f157dfa3006ccb4359003b21efeab1488f81f1799fc97654fda` / 23226 |
| `agent-tasks/TC-owner-auth-session.md` | MODIFY | `4f6d77b8…` / 19066 | `bc2ca583b461b819558a4b6669705860a978c3837997f2afb0ddd5e05c146890` / 19119 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | MODIFY | `9faa1156…` / 21486 | `ecab8beca4884b5223c3228853f74b02aaccb7e95fdbddf0672053de42aa9c46` / 21539 |
| `agent-tasks/TC-saved-snapshot.md` | MODIFY | `ee8ba283…` / 19805 | `c6657dea32b887f1236ac469557f52a0e761f816b710f372fd69a6f56e1253fe` / 19858 |
| `agent-tasks/TC-scheduler-lease-claim.md` | MODIFY | `ad08f450…` / 20624 | `475d4a506f72cd2d231248de85ca7704413673a6ad83158dc4a9e9eeceaab5bf` / 20677 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | MODIFY | `84b2c7c0…` / 17986 | `72ebe3ab4700fa6e9d2c57dd1dc532f0e1f5e4f38ad97ede0bbc144fd725d6cd` / 18039 |
| `agent-tasks/TC-telegram-linking-auth.md` | MODIFY | `71ca88ca…` / 20201 | `b93ac74a9474a1f23758d71e7a9104be99376d07abbd9505902e4d267e5e2976` / 20254 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | MODIFY | `8bada840…` / 21061 | `f0875c106d0be5a5d11226bf634ee470c34dc52795516f45802a1cbadd735dfa` / 21114 |
| `agent-tasks/TC-ui-reports-detail.md` | MODIFY | `fb91365c…` / 19099 | `238d55262a1be032f47f6ff70f4450491a24873a3580f4eeb2b7fb93aee728d8` / 19152 |
| `agent-tasks/TC-ui-runs-three-states.md` | MODIFY | `17b22632…` / 18501 | `b3eade777a62296628d634f9614231eced839ace281b2619a524064e7fd87002` / 18554 |
| `agent-tasks/TC-x-feasibility-probe.md` | MODIFY | `7dad6b03…` / 17429 | `f09e154cffaabb3ad4d7be845198fb6e58b72285ab5c5b803e94431015613a95` / 17482 |

**22 file MODIFY. 0 CREATE, 0 DELETE.** Đúng grant (`agent-tasks/*`, `precode/README.md`, handoff này).
`precode/change-control.md` **không** nằm trong grant lần này và **không** bị chạm. Không `__pycache__`;
script chạy từ `…/scratchpad/w7/`; không lệnh git; không mạng.

Mỗi card chênh **+53 byte**, đúng bằng phần văn bản epoch mới ở §0 — nhất quán với việc ngoài epoch và bảy
dòng hash, nội dung card không đổi.

## C.4 Evidence (chạy lại lần 4)

### EV-PC10-01 (lần 4)

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T01:23Z / 2026-09-07T01:24Z |
| `oracle` | Mười phép kiểm (a)…(j) như trước, **cộng (k) mới**: epoch lấy từ §0 của 18 card phải đồng thuận đúng một giá trị, và 4 file khẳng định pin phải nêu đúng epoch đó; epoch cũ chỉ hợp lệ trong đoạn văn có dấu hiệu lịch sử |
| `observed` | epoch hiện hành đọc từ card: **`PC10-PIN-FCW4c-20260907`**; **483 dòng hash / 143 file khớp 100 %**; 669 path; 155 operation ID; 116 SC; 99 mã lỗi §7; 18/18 card có `SC49` + bảng R5-01 + fixture boundary; 0 nhãn claim ngoài SRC-PLAN §2; 0 file PC09 bị pin hash; **0 epoch stale** |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Check (k) chỉ phủ 4 file trong grant của PC10. `precode/review.md` **không** được phủ vì ngoài grant — xem `CR-PC10-05`. Vẫn là self-validation. |

### EV-PC10-02 (lần 4)

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py` (E0 chính thức là của PC09), validator OpenAPI 3.1, mọi test E1–E4, probe SP1,
probe CLI/ACP.

## C.5 CR

**Mới:** `CR-PC10-05` (§C.1) — `precode/review.md` §9.1 còn tên epoch cũ; ngoài grant của PC10.

**Đóng:** `F-A2R1-03` đóng **một phần** — phần thuộc `precode/README.md` và `agent-tasks/*` đã xong và nay có
phép kiểm máy chống tái phát; phần `precode/review.md` chuyển thành `CR-PC10-05`.

**Không đổi:** `CR-PC07-04` **vẫn OPEN và vẫn chặn** nhánh multipart của `TC-telegram-unknown-delivery`
(giới hạn định dạng Telegram còn `KC`, cần một bước có mạng). `CR-PC05-03`, `CR-PC06-04`, REQ-OQ01/SP1,
REQ-OQ02 (ADR-0006 `proposed`), REQ-OQ03, loại trừ `data.purge_all`, validator OpenAPI 3.1 `NOT_RUN` — y như
ADDENDUM `PKT-PC10-FIX1` §A.6.

`status` là `DONE_WITH_CONCERNS` vì: `CR-PC07-04` còn chặn; `CR-PC10-05` mở và nằm ngoài tay PC10;
`audit_route` là `INDEPENDENT_REQUIRED` trong khi PC10 chỉ có self-validation; và **PC10 vẫn chưa chạy phép
kiểm ngược "mọi `REQ-P0-*` có ít nhất một card"** trên `acceptance/traceability.csv` — câu hỏi "18 card có phủ
đủ P0 không" vẫn chưa được trả lời, đúng như A2-R1 §7 mục 11 ghi `NOT_MET` cho hàng card.

---

*PKT-PC10-FIX3 · worker-W7 · `lease_released_at` 2026-09-07T01:26Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX4

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX4` · authority `AUTH-COORD-PC10-FIX4` · lease `LEASE-PC10-e5` (fencing 5) |
| expires_at | 2026-09-07T18:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | Toàn bộ gói nội dung FIX7 landing; `contracts/data/entities.yaml` thêm cột trên sáu entity |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T01:31Z / 2026-09-07T01:48Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T01:48Z |
| **pin epoch mới** | **`PC10-PIN-FCW4d-20260907`** (thay `PC10-PIN-FCW4c-20260907`) |

Không có wait gate ở packet này. Nguồn không đổi trước và sau: `research-radar-spec.md` `d35e1f2d…`,
`research-radar-pre-code-plan.md` `f65bb046…`. `INV-08` không trigger.

## D.1 Drift — trả lời câu hỏi của packet

Generator tính lại **toàn bộ** 483 dòng hash trên 143 file. So bảng pin `FCW4c` với `FCW4d`: **đúng 20 file
đổi**, và cả 20 nằm trong danh sách packet đã nêu — 8 file được nêu đích danh cộng 12 file PC04/PC06:

| Nhóm | File |
| --- | --- |
| 8 file nêu đích danh | `contracts/data/entities.yaml` (221041), `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/ports.yaml`, `contracts/capabilities.yaml`, `contracts/ops/deployment.md`, `precode/baseline.json`, `precode/decision-register.md` |
| 12 file PC04/PC06 | `contracts/reporting/time-and-tags.md`, `contracts/reporting/selection.md`, `contracts/ai/tasks.yaml`, `acceptance/fixtures/ai/README.md`, `acceptance/fixtures/reporting/README.md`, và 7 fixture `reporting/`: `a-tag-removed-before-publish`, `c-tag-changed-after-publish-before-send`, `g-concurrent-publishers-cas`, `h-already-announced-work-becomes-reference`, `i-identity-merge-single-first-announced`, `j-backfill-add-remove-readd`, `n-embedding-generation-switch-positive` |

**Không có drift nào ngoài danh sách** — 123/143 file còn lại giữ nguyên hash và byte count. Tám hash
Coordinator nêu đích danh đều được xác nhận trước khi pin.

## D.2 Cột mới trên sáu entity — đã làm gì và **không** làm gì

Mười card có oracle chạm sáu entity đó nay mang một dòng ghi chú trong §4, ngay sau **State effects**:

| Entity | Cột được nêu trong ghi chú | Card mang ghi chú |
| --- | --- | --- |
| `ENT-run` | `observed_window_from`, `observed_window_to`, `posts_observed_total`, `posts_ingested_new`, `limit_hit`, `limit_kind`, `cursor_invalidated`, `x_coverage_note_vi`, `rate_limited_at` | scheduler-lease-claim, collector-checkpoint-resume, storage-write-blocked-readiness, ui-runs-three-states, report-coverage-publish-cas, ingest-idempotent-ack-lost, analysis-once-per-generation |
| `ENT-report` | `abort_reason`, `selection_version` | report-coverage-publish-cas, backfill-pending-ledger, ui-reports-detail, telegram-unknown-delivery |
| `ENT-delivery` | `telegram_link_generation` | ui-runs-three-states, telegram-unknown-delivery |
| `ENT-delivery-part` | `provider_message_id` | ui-runs-three-states, telegram-unknown-delivery |
| `ENT-tag` | `removed_at` | report-coverage-publish-cas, backfill-pending-ledger |
| `ENT-worker-registration` | `online_state`, `last_run_at` | scheduler-lease-claim, collector-checkpoint-resume, ui-runs-three-states |

**Oracle ở §8 không đổi trên bất kỳ card nào**, đúng ràng buộc của packet. Cơ sở: tôi đã quét mọi token dạng
`` `<entity>.<column>` `` mà 18 card đang gọi tên trên sáu entity này và đối chiếu từng cái với
`entities.yaml` hiện hành. Tất cả vẫn tồn tại với đúng nghĩa cũ: `run.status`, `run.outcome`,
`run.rate_limited_at`, `run.x_coverage_note_vi`, `report.tag_config_version` (khớp
`contracts/schemas/report.schema.json`; ở tầng entity là `tag_config_version_id`), `delivery.unknown`,
`delivery.failed`. Cột mới là **additive**.

### Một ngoại lệ — có một oracle **đã** đổi nghĩa, và nó được sửa

`report.abort_reason` **nay tồn tại** với enum sáu giá trị `empty_period | tag_version_stale |
embedding_generation_mismatch | cas_conflict | builder_failure | cancelled`, CHECK NOT NULL khi và chỉ khi
`status = 'aborted'`. Bản card trước viết stop condition `SG-02` của `TC-report-coverage-publish-cas` là
*"`CR-PC04-08/09` còn OPEN; nếu enum chưa có, không tự đặt tên giá trị"* — nay sai. Quan trọng hơn: hai giá
trị mà `CR-PC04-09` **đề xuất** và bản card trước nhắc lại (`cas_lost`, `builder_crash_or_stale`) **không**
phải tên được chọn cuối cùng; enum đã đóng dùng `cas_conflict` và `builder_failure`, và thêm `cancelled`.
Một agent viết assertion theo tên cũ sẽ fail ở CHECK constraint.

Đã sửa cả hai chỗ trong `TC-report-coverage-publish-cas`: **State effects** §4 nay ghi `CR-PC04-08/09` **đã
đóng** kèm enum đúng, và `SG-02` nay bắt buộc dùng đúng sáu giá trị, nêu đích danh hai tên cũ là **không tồn
tại**, và yêu cầu DỪNG + raise CR nếu cần giá trị thứ bảy. Đây là loại thay đổi mà packet cho phép:
*"no oracle changes unless an existing oracle named a column that changed meaning"*.

### Điều tôi **không** khẳng định

Packet nói "8 columns added". Tôi **không** xác minh được đó là đúng tám cột nào: bản `FCW4c` của
`entities.yaml` không được giữ lại ở đâu (repo untracked trong git, và card chỉ pin hash chứ không pin nội
dung), nên tôi **không có bytes cũ để diff**. Vì vậy ghi chú trên card **không** tuyên bố "tám cột này là
mới"; nó nêu **tập cột hiện hành** của entity mà card chạm, gắn nhãn epoch `FCW4d`, và bảo người đọc đọc bảng
cột trong `entities.yaml` trước khi viết assertion. Nếu Coordinator muốn ghi chú nêu đích danh tám cột mới,
hãy gửi kèm danh sách hoặc bytes `FCW4c` — tôi sẽ không đoán.

## D.3 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `precode/README.md` | MODIFY | `4e8e1ce0…` / 14771 | `7edb016c82c9c307b391fae6c5cd297d0437eb171684084b101c22a0a4831e75` / 14795 |
| `agent-tasks/README.md` | MODIFY | `0db71dec…` / 14079 | `d61cb6fc6a529eb5378d66969093c30062d6d9d3ac5f745b300f06e3abfe0b0d` / 14109 |
| `agent-tasks/TEMPLATE.md` | MODIFY | `92629c77…` / 11961 | `1977ae28c71e6f96fc6bd6bdd595697ecf8222d686de4ac46eaa9b9c6a11e6b6` / 11961 |
| `agent-tasks/WALKTHROUGH.md` | MODIFY | `171d01da…` / 17048 | `b982f08df3323fb282f8e38968aae50ca5d5697a4ffbffac78fc026d217cf02a` / 17102 |
| `agent-tasks/TC-analysis-adapter-validation.md` | MODIFY | `e324d6bf…` / 22023 | `1c255e0fc08e53964e90c7c701b70786ad720bc91f186cfbad592f9124b2d052` / 22047 |
| `agent-tasks/TC-analysis-once-per-generation.md` | MODIFY | `91a908ab…` / 19723 | `112921ff29faa041b7bee9d137e7fdeb0bc75e021221bb0015eadec12577c523` / 20418 |
| `agent-tasks/TC-backfill-pending-ledger.md` | MODIFY | `18b11aca…` / 18205 | `4ee374563cf3a93974e61a1d2f892c0f654004148b067bc61aaf61f7fce50cc0` / 18796 |
| `agent-tasks/TC-backup-restore-drill.md` | MODIFY | `b3e5a3d7…` / 19387 | `e6db99bc4d7624cb0c2abf705a5bb231284dc3cef3fa9f2957abcf377c3d9966` / 19411 |
| `agent-tasks/TC-canonical-identity-merge.md` | MODIFY | `e1d2956a…` / 19837 | `2501dc2db9a5228b1685c23d53ce55df2061fd69f2324df1d0c9dd235f542f69` / 19861 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | MODIFY | `a6fd14de…` / 22021 | `4996b5a157ef86cd23c7074e5f118ef1b2d883bf5aae480c5570f9d0bbf65ca6` / 22771 |
| `agent-tasks/TC-embedding-generation-switch.md` | MODIFY | `c196a5c2…` / 17920 | `c18fa1e63a72165ba3ee34e1a2721a14e3a5bf670e095963f915abc97b7e4c9f` / 17944 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | MODIFY | `1d55bd56…` / 23226 | `ea09d1e0867d0b9f72d3c43a5cfc66ebc8deb2d395fa5d3ab1c30e8547d2c0fb` / 23921 |
| `agent-tasks/TC-owner-auth-session.md` | MODIFY | `bc2ca583…` / 19119 | `57c7441b38e46129b1ddb1aa58743fad026ed03f41c631056ebf2629f026ff17` / 19143 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | MODIFY | `ecab8bec…` / 21539 | `2df36f49020e0d455b41aefd3cc1fcf6eb68599f97b0b65c3623547ec9414054` / 22877 |
| `agent-tasks/TC-saved-snapshot.md` | MODIFY | `c6657dea…` / 19858 | `3fc7332e8993d9acbb8edf0ecfeb8b73f9aad2ec78211b63685b25d4cb337d11` / 19882 |
| `agent-tasks/TC-scheduler-lease-claim.md` | MODIFY | `475d4a50…` / 20677 | `adb96eb9bcb800af979a0e803d2c8a82134a1ef0ad79fc4d066a475c94151409` / 21427 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | MODIFY | `72ebe3ab…` / 18039 | `8d7091eab650707ecfc52870b4a3a598fdfbfbc09bcc8ed938e15d5862366fe9` / 18734 |
| `agent-tasks/TC-telegram-linking-auth.md` | MODIFY | `b93ac74a…` / 20254 | `00c9a76ece9f79e1c0515bc20bd3a1f0c3923a55e3c7c7a9614709b8c5fa5c24` / 20278 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | MODIFY | `f0875c10…` / 21114 | `5a3fde1fdc59efac223a714ca0b6be87489fd1825747ca823a5ccb0f769fc8d0` / 21767 |
| `agent-tasks/TC-ui-reports-detail.md` | MODIFY | `238d5526…` / 19152 | `d6e0ef8d6dcbdbf3530febd9ff114e44106049c562903125d4e470390a0a2f70` / 19719 |
| `agent-tasks/TC-ui-runs-three-states.md` | MODIFY | `b3eade77…` / 18554 | `182e391983b56610784a1298492bc6abd2930edb5d50a7be4643935a13ef1ce0` / 19390 |
| `agent-tasks/TC-x-feasibility-probe.md` | MODIFY | `f09e154c…` / 17482 | `4ae52a67b960a4f2776ac939b3c2420d320d1c5624624be167d81e175385d9f8` / 17506 |

**22 file MODIFY. 0 CREATE, 0 DELETE.** Đúng grant (`agent-tasks/*`, `precode/README.md`, handoff này).
`precode/change-control.md` không nằm trong grant và không bị chạm. Không `__pycache__`; script chạy từ
`…/scratchpad/w7/`; không lệnh git; không mạng.

`TEMPLATE.md` giữ nguyên **11961 byte** vì tên epoch cũ và mới dài bằng nhau — hash đổi, byte count không.
Tám card không mang ghi chú cột chênh đúng **+24 byte** (chỉ epoch). Mười card mang ghi chú chênh nhiều hơn.

## D.4 Evidence (chạy lại lần 5)

### EV-PC10-01 (lần 5)

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T01:45Z / 2026-09-07T01:46Z |
| `oracle` | Mười một phép kiểm (a)…(k), không đổi so với FIX3 |
| `observed` | epoch đọc từ card: **`PC10-PIN-FCW4d-20260907`** (18/18 đồng thuận); **483 dòng hash / 143 file khớp 100 %**; 669 path; 155 operation ID; 116 SC; 99 mã lỗi §7; 18/18 có `SC49` + bảng R5-01 + fixture boundary; 0 nhãn claim ngoài SRC-PLAN §2; 0 file PC09 bị pin hash; **0 epoch stale** trong 4 file khẳng định |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Check (k) vẫn không phủ `precode/review.md` (ngoài grant — `CR-PC10-05`). Không phép kiểm nào xác minh "cột nào là mới" — xem §D.2. Vẫn là self-validation. |

### EV-PC10-02 (lần 5)

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py`, validator OpenAPI 3.1, mọi test E1–E4, probe SP1, probe CLI/ACP.

## D.5 CR

**Đóng ở vòng này:** `CR-PC04-08` và `CR-PC04-09` — `report.abort_reason` nay tồn tại với enum đóng và CHECK
constraint; card đã cập nhật (§D.2).

**Không đổi:** `CR-PC10-05` (→ PC09, `precode/review.md` còn epoch cũ — nay lệch **ba** thế hệ: `FCW4` so với
`FCW4d`); `CR-PC07-04` **vẫn OPEN và vẫn chặn** nhánh multipart của `TC-telegram-unknown-delivery`;
`CR-PC05-03`; `CR-PC06-04`; REQ-OQ01/SP1; REQ-OQ02 (ADR-0006 `proposed`); REQ-OQ03; loại trừ
`data.purge_all`; validator OpenAPI 3.1 `NOT_RUN`.

**Mới:** không.

`status` là `DONE_WITH_CONCERNS` vì `CR-PC07-04` còn chặn; `CR-PC10-05` mở và ngoài tay PC10; `audit_route`
là `INDEPENDENT_REQUIRED` trong khi PC10 chỉ có self-validation; và **PC10 vẫn chưa chạy phép kiểm ngược
"mọi `REQ-P0-*` có ít nhất một card"** trên `acceptance/traceability.csv`.

---

*PKT-PC10-FIX4 · worker-W7 · `lease_released_at` 2026-09-07T01:48Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX5 (lần pin cuối)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX5` · authority `AUTH-COORD-PC10-FIX5` · lease `LEASE-PC10-e6` (fencing 6) |
| expires_at | 2026-09-07T18:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | Wave nội dung FIX8 landing (W2 01:50Z, W3 01:55Z, W4 ~02:00Z); Coordinator xác nhận **không còn thay đổi nội dung nào được lên lịch** |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T02:03Z / 2026-09-07T02:18Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T02:18Z |
| **pin epoch mới** | **`PC10-PIN-FCW4e-20260907`** (thay `PC10-PIN-FCW4d-20260907`) — **lần pin cuối của Pre-code** |

Không wait gate. Nguồn không đổi trước và sau: `research-radar-spec.md` `d35e1f2d…`,
`research-radar-pre-code-plan.md` `f65bb046…`. `INV-08` không trigger. Mười bảy hash Coordinator nêu đích
danh đều được xác nhận **trước** khi pin.

## E.1 Kiểm tra thêm — vì bốn state machine cùng đổi ở wave này

`run.yaml`, `report.yaml`, `analysis.yaml` và `storage.yaml` đổi cùng lúc, và card trích **transition ID** từ
cả bốn. Hash khớp chỉ chứng minh "file này đúng bản đó", **không** chứng minh "ID card đang trích vẫn tồn
tại". Nên trước khi pin, tôi quét mọi định danh mà 18 card gọi tên và giải chúng về file sở hữu:

| Loại | Số card trích | Không giải được |
| --- | --- | --- |
| Transition `T-RUN-*`, `T-AN-*`, `T-RP-*`, `T-DL-*`, `T-ST-*` | 14 | **0** |
| Màn hình `SCR-*` (`contracts/ui/screens.yaml`) | 7 | **0** |
| Lệnh `CMD-*` (`contracts/telegram/commands.yaml`) | 3 | **0** |
| Transaction `TXN-*` (`contracts/data/entities.yaml`) | 7 | **0** |
| Denied case `NC-*`, forbidden edge `FE-*` (`contracts/modules.yaml`) | 4 | **0** |
| Quy tắc `INV-*` (`precode/gates.yaml`) | 2 | **0** |
| Ngân sách retry (`contracts/retry-policy.yaml`) | 1 | **0** |
| Operation ID (`contracts/ports.yaml`) | 155 | **0** |
| Mã lỗi §7 (`contracts/errors.yaml`) | 99 | **0** |

`T-RUN-25` (rate limit → `partial`) vẫn tồn tại sau khi `run.yaml` đổi, nên `SG-RATE` trên card collector vẫn
đúng. Không oracle nào phải sửa ở vòng này.

## E.2 Drift — trả lời câu hỏi của packet

Generator tính lại **toàn bộ** 483 dòng hash trên 143 file. So `FCW4d` với `FCW4e`: **25 file có pin đã đổi**;
118/143 giữ nguyên. Phân loại đối chiếu với danh sách packet:

| Nhóm | Số | File |
| --- | --- | --- |
| Nêu đích danh trong packet | 15 | `ops/secrets.md`, `ops/backup-restore.md`, `fixtures/recovery/README.md`, `schemas/ingest-batch.schema.json`, `ui/screens.yaml`, `telegram/commands.yaml`, `telegram/delivery.md`, `schemas/saved-snapshot.schema.json`, `state/run.yaml`, `state/report.yaml`, `state/analysis.yaml`, `state/storage.yaml`, `retry-policy.yaml`, `http/openapi.yaml`, `fixtures/collection/l-storage-write-blocked-mid-run.json` |
| "telegram + ui READMEs" | 2 | `fixtures/telegram/README.md`, `fixtures/ui/README.md` |
| Fixture `telegram/` | 7 | `d-unlink-before-send-cancelled`, `e-relink-old-generation-cancelled`, `g-link-code-used-twice`, `i-unknown-chat-valid-code-format`, `j-concurrent-save-app-telegram`, `k-save-then-source-deleted`, `m-three-run-states-distinct-text` |
| Fixture `ui/` | 1 | `sc10-same-analysis-revision-app-and-telegram.json` |

**Không có drift ngoài wave đã báo.** Một khác biệt về **cách đếm**, không phải drift: packet viết "8 telegram
fixtures"; trong tập card pin, tôi đếm **7** fixture `telegram/` cộng **1** fixture `ui/`
(`sc10-same-analysis-revision-app-and-telegram.json`). Fixture đó thuộc thư mục `ui/` nhưng chính là SC10
("cùng analysis revision hiển thị ở app **và** Telegram"), nên nó đi cùng đợt W3 — chỉ là được xếp vào `ui/`
chứ không phải `telegram/`. Card pin đủ cả 18 fixture `telegram/`; 11 cái còn lại không đổi.

## E.3 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `precode/README.md` | MODIFY | `7edb016c…` / 14795 | `4f1f40ee6c62b628fff16c39b70d008f97a722d503fe4b5e7c56cfc1fa325553` / 14825 |
| `agent-tasks/README.md` | MODIFY | `d61cb6fc…` / 14109 | `ad0544ca9d8deae1f56c9c8ccb745f3081d990933089a7575a82029bdc964781` / 14139 |
| `agent-tasks/TEMPLATE.md` | MODIFY | `1977ae28…` / 11961 | `f446f97647961cd6b9a98b50c641756d12711fb756da5cb5ae5d72349e43be4c` / 11961 |
| `agent-tasks/WALKTHROUGH.md` | MODIFY | `b982f08d…` / 17102 | `53b7d45c8e7ea5f3c6600d800ff22485ef82d3c7125e83c92b916e6f900a8b3c` / 17156 |
| `agent-tasks/TC-analysis-adapter-validation.md` | MODIFY | `1c255e0f…` / 22047 | `0cc9e9fe0a9a09060fb09d4b858bee6da253ad70bd93b6085b88c8d7d7fdc8ac` / 22217 |
| `agent-tasks/TC-analysis-once-per-generation.md` | MODIFY | `112921ff…` / 20418 | `3b7840a84e1d9c17016465b6167292cf23a5e242274baef26e8a3e617e993ecd` / 20616 |
| `agent-tasks/TC-backfill-pending-ledger.md` | MODIFY | `4ee37456…` / 18796 | `d52e43ff3d035077c3c65e2c8c412cee9f8440e2057a1d9a35c52b02cb71f918` / 18994 |
| `agent-tasks/TC-backup-restore-drill.md` | MODIFY | `e6db99bc…` / 19411 | `693bdc755ed9d9ae9bac92a568b5a488a4723b4fe1bcef13f5fc70fa40a348d0` / 19581 |
| `agent-tasks/TC-canonical-identity-merge.md` | MODIFY | `2501dc2d…` / 19861 | `dc918ce3085ce52cfbe7e7f3eda1c9bd0834a66c1d87c506b421f8f0cac3c117` / 20031 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | MODIFY | `4996b5a1…` / 22771 | `93cef47a5b6312e8ed0744b2c656c354dced262a61e2fe3169092c8a149957cf` / 22969 |
| `agent-tasks/TC-embedding-generation-switch.md` | MODIFY | `c18fa1e6…` / 17944 | `f8ee0cf227b566246b48efc07dd25773feb61a4f48737749fd14cf5d59f9127e` / 18114 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | MODIFY | `ea09d1e0…` / 23921 | `fa7c33ab4f7cf5ca2dc00acfd20a8c8e893ea7d55257bf41825e1ad53b942ba3` / 24119 |
| `agent-tasks/TC-owner-auth-session.md` | MODIFY | `57c7441b…` / 19143 | `2ed2f281771cb05fb79e959c1c8896fdd2c4aeff6ead3e182481e673942fad95` / 19313 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | MODIFY | `2df36f49…` / 22877 | `eadcfa46504cfc5292858d739e7f4768a3da57bcd5dd53aab28caa739bcf1c3b` / 23075 |
| `agent-tasks/TC-saved-snapshot.md` | MODIFY | `3fc7332e…` / 19882 | `0707b72b333c0a25410c233bcb1b1c61711f2605487d52d4a90279d56825f7ca` / 20052 |
| `agent-tasks/TC-scheduler-lease-claim.md` | MODIFY | `adb96eb9…` / 21427 | `c7607ba7254eb87befb00a4616efae52bcab4b84a9604ed93adb3abab4b98a7e` / 21625 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | MODIFY | `8d7091ea…` / 18734 | `086e59af4b85049bd068bfd6356b10d75d758faca9e8759e4efa470d1c2e23c5` / 18932 |
| `agent-tasks/TC-telegram-linking-auth.md` | MODIFY | `00c9a76e…` / 20278 | `5239c64580f0cc3d2b0d9497fe449a4a35972dc99801af9cbad29e80f225cbfe` / 20448 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | MODIFY | `5a3fde1f…` / 21767 | `7acd92673367c70651dc1d1d2a12e5e64f055de487d40f098955351f79674ece` / 21965 |
| `agent-tasks/TC-ui-reports-detail.md` | MODIFY | `d6e0ef8d…` / 19719 | `08fbebb3a774cc340656b2585323232f6684b3874c624045492a6802984559d8` / 19917 |
| `agent-tasks/TC-ui-runs-three-states.md` | MODIFY | `182e3919…` / 19390 | `9e02ee5c90b851f3a150295de373528713200d5c206d8b5bb8095624288da368` / 19588 |
| `agent-tasks/TC-x-feasibility-probe.md` | MODIFY | `4ae52a67…` / 17482 | `92bbadafab59922b28a24160084c4b0f49b0865dada4e1fb4444f0bbc04c4d06` / 17676 |

**22 file MODIFY. 0 CREATE, 0 DELETE.** Đúng grant (`agent-tasks/*`, `precode/README.md`, handoff này).
`precode/change-control.md` không nằm trong grant và không bị chạm. Không `__pycache__`; script chạy từ
`…/scratchpad/w7/`; không lệnh git; không mạng. `TEMPLATE.md` giữ nguyên 11961 byte (tên epoch cũ và mới dài
bằng nhau); ghi chú cột `FCW4d` được đánh dấu "giữ nguyên ở `FCW4e`" thay vì viết lại.

## E.4 Evidence (chạy lại lần 6 — lần cuối)

### EV-PC10-01 (lần 6)

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T02:15Z / 2026-09-07T02:16Z |
| `oracle` | Mười một phép kiểm (a)…(k), không đổi; cộng phần quét định danh ở §E.1 |
| `observed` | epoch đọc từ card **`PC10-PIN-FCW4e-20260907`** (18/18 đồng thuận); **483 dòng hash / 143 file khớp 100 %**; 669 path; 155 operation ID; 116 SC; 99 mã lỗi §7; 18/18 có `SC49` + bảng R5-01 + fixture boundary; 0 nhãn claim ngoài SRC-PLAN §2; 0 file PC09 bị pin hash; 0 epoch stale; **0 định danh không giải được** trên 9 loại ở §E.1 |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Check (k) vẫn không phủ `precode/review.md` (ngoài grant — `CR-PC10-05`). Vẫn là self-validation; `audit_route` của packet là `INDEPENDENT_REQUIRED`. |

### EV-PC10-02 (lần 6)

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py` (E0 chính thức là của PC09), validator OpenAPI 3.1, mọi test E1–E4, probe SP1,
probe CLI/ACP. Không có code sản phẩm nào tồn tại.

## E.5 Trạng thái cuối của PC10

Đây là lần pin cuối, nên ghi lại đủ để Coordinator không phải đọc ngược năm addendum:

- **18 card**, mỗi card đủ 14 mục, pin `PC10-PIN-FCW4e-20260907`, tổng **483 dòng hash trên 143 file**, tất cả
  tính lại khớp. Sáu file PC09 cộng `evidence/tools/e0_check.py` **cố ý không pin hash** (dẫn bằng đường dẫn +
  SC id), có phép kiểm (j) chặn việc vô tình pin chúng.
- **Trần claim** đúng nhãn SRC-PLAN §2: 16 card `IMPLEMENTATION_VERIFIED`, card SP1
  `LIVE_FEASIBILITY_VERIFIED`, nhánh CLI/ACP của card adapter dừng ở `CONTRACT_READY`.
- **`SC49`** (quét default-deny 36 cạnh) và bảng ranh giới mã lỗi R5-01 nằm trên **cả 18 card**.
- **CR do PC10 phát sinh:** `CR-PC10-01`…`-04` **đã đóng**, cả bốn bằng cách sửa hợp đồng chứ không nới card.
  `CR-PC10-05` (→ PC09, `precode/review.md` còn epoch cũ — nay lệch **bốn** thế hệ) **còn mở**, ngoài grant.
- **Vẫn chặn G5:** `CR-PC07-04` (giới hạn định dạng Telegram còn `KC` ⇒ nhánh multipart của
  `TC-telegram-unknown-delivery` không hiện thực được; cần một bước **có mạng**, không sửa được bằng hợp
  đồng). Kèm theo: `CR-PC05-03`, `CR-PC06-04` (AC-16 `BLOCKED`), REQ-OQ01/SP1, REQ-OQ02 (ADR-0006 vẫn
  `proposed` ⇒ **mọi** đường dẫn §3 và lệnh §8 còn PROVISIONAL), REQ-OQ03, loại trừ `data.purge_all`,
  validator OpenAPI 3.1 `NOT_RUN`.
- **Chưa trả lời:** PC10 **chưa** chạy phép kiểm ngược "mọi `REQ-P0-*` có ít nhất một card" trên
  `acceptance/traceability.csv`. Câu hỏi "18 card có phủ đủ P0 không" vẫn để ngỏ, khớp với A2-R1 §7 mục 11
  (`NOT_MET` cho hàng card). Nếu Coordinator muốn đóng nốt, đó là một packet nhỏ và tôi có sẵn công cụ.

`status` là `DONE_WITH_CONCERNS`, không phải `DONE`: `CR-PC07-04` còn chặn, `CR-PC10-05` mở, phủ P0 chưa
kiểm, và PC10 chỉ có self-validation trong khi `audit_route` là `INDEPENDENT_REQUIRED`.

---

*PKT-PC10-FIX5 · worker-W7 · `lease_released_at` 2026-09-07T02:18Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX6

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX6` · authority `AUTH-COORD-PC10-FIX6` · lease `LEASE-PC10-e7` (fencing 7) |
| expires_at | 2026-09-07T20:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | `contracts/modules.yaml` đổi sau `FCW4e` — năm denied case thêm `event_type` |
| status | `DONE_WITH_CONCERNS` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T02:22Z / 2026-09-07T02:31Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T02:31Z |
| **pin epoch mới** | **`PC10-PIN-FCW4f-20260907`** (thay `PC10-PIN-FCW4e-20260907`) |

Không wait gate. Nguồn không đổi trước và sau: `research-radar-spec.md` `d35e1f2d…`,
`research-radar-pre-code-plan.md` `f65bb046…`. `INV-08` không trigger. Hash Coordinator nêu được xác nhận
trước khi pin: `contracts/modules.yaml` `11af00fd…`, 105642 byte.

## F.1 Drift

Generator tính lại **toàn bộ** 483 dòng hash trên 143 file. So `FCW4e` với `FCW4f`: **đúng một file có pin đã
đổi** — `contracts/modules.yaml` — như packet dự báo. **142/143 file còn lại giữ nguyên** hash và byte count.
Không có drift ngoài `modules.yaml`.

## F.2 Kiểm khẳng định mà card đưa ra về `modules.yaml`

Packet nói "no card oracle affected". Tôi không nhận điều đó làm mặc định: card khẳng định vài **con số** lấy
từ chính file này, và một thay đổi thêm trường vẫn có thể làm đổi số. Đã đếm lại trên bản mới:

| Khẳng định trên card | Bản `FCW4f` | Kết luận |
| --- | --- | --- |
| "36 `forbidden_edges`" (§5 và `SG-DENY` của cả 18 card) | `FE-*` = **36** | đúng |
| Mỗi cạnh cấm có một `denied_cases[]` | `NC-*` = **36** | đúng, bijection 36↔36 giữ nguyên |
| 25 module (`MOD-*` dùng trong §4/§5) | **25** | đúng |
| Bảng ranh giới mã lỗi R5-01 bốn hàng | 4 mã vẫn đủ trong §5 của 18/18 card | đúng |

`event_type` là trường **thêm mới** trên năm denied case; nó mở rộng phần mô tả cách quan sát một ca bị từ
chối (dạng `local_observation` mà `NC-12`/`NC-24` đã dùng), **không** đổi `expected_error_code` hay
`attempted_edge` của ca nào. Vì vậy **không oracle nào của card phải sửa** — xác nhận độc lập, không chỉ chép
lại lời packet.

## F.3 Changes

| Path | Op | Before sha256 / bytes | After sha256 / bytes |
| --- | --- | --- | --- |
| `precode/README.md` | MODIFY | `4f1f40ee…` / 14825 | `1b0c736e1c96d9f957da00665f66ffcac3079604bc9e2cfe33f09f64c368ae3f` / 14855 |
| `agent-tasks/README.md` | MODIFY | `ad0544ca…` / 14139 | `704c970add284fa6c8c116407534d5f2d20595e3b11ef91d70464fb2d4b5e785` / 14169 |
| `agent-tasks/TEMPLATE.md` | MODIFY | `f446f976…` / 11961 | `714701c1355dd6cb6194d54131503b9ac2348827e88a00f9c79c54b4bba22c8d` / 11961 |
| `agent-tasks/WALKTHROUGH.md` | MODIFY | `53b7d45c…` / 17156 | `13ff42158c234e2e9fe44e8292769a113f829337615832f1fb366412a0ce5baa` / 17210 |
| `agent-tasks/TC-analysis-adapter-validation.md` | MODIFY | `0cc9e9fe…` / 22217 | `48eaf792d6457282dd6c45b3e25c870997a00f2a6612b63414f337bf5f94ab70` / 22212 |
| `agent-tasks/TC-analysis-once-per-generation.md` | MODIFY | `3b7840a8…` / 20616 | `9e434e65801abfe80a777693f0b5912960762d2c8d606e8b1ea0c94b15979883` / 20611 |
| `agent-tasks/TC-backfill-pending-ledger.md` | MODIFY | `d52e43ff…` / 18994 | `fdeb6e6bdf502feb1a99bd684d34c91fedb4f604392dca167095ac3dcc26e0c4` / 18989 |
| `agent-tasks/TC-backup-restore-drill.md` | MODIFY | `693bdc75…` / 19581 | `3c3d6ab9d6fef1c018e74fd7d9e24cd60c919bf5d378c6f1880cac7dcfb92193` / 19576 |
| `agent-tasks/TC-canonical-identity-merge.md` | MODIFY | `dc918ce3…` / 20031 | `e618c5b0ad6a6c40fb9e508b2753e958c103ed09ac4007cbf007e21ef1ef63e6` / 20026 |
| `agent-tasks/TC-collector-checkpoint-resume.md` | MODIFY | `93cef47a…` / 22969 | `bd2940a4cb34920cc78a049bfbd0fce12f9db6871c1bfd1519cc8d8c13239628` / 22964 |
| `agent-tasks/TC-embedding-generation-switch.md` | MODIFY | `f8ee0cf2…` / 18114 | `ec15da047b549fcb6e9fc613fa094f92e6c72b5ec9e4372079c7c6826692cb88` / 18109 |
| `agent-tasks/TC-ingest-idempotent-ack-lost.md` | MODIFY | `fa7c33ab…` / 24119 | `ed0a2c5e04d6ec8d3d1fe23d6d16ca30bb2163ebf54dea72389706441b49a3ee` / 24114 |
| `agent-tasks/TC-owner-auth-session.md` | MODIFY | `2ed2f281…` / 19313 | `10f043bdd2a89582d0ca31e236aa9a394e26270dc4f2d97392a1607af8bdce8b` / 19308 |
| `agent-tasks/TC-report-coverage-publish-cas.md` | MODIFY | `eadcfa46…` / 23075 | `a4645e343a6827e41b547e88feb8a52b4db0f9c8f3114ad46b80546eb09d9aeb` / 23070 |
| `agent-tasks/TC-saved-snapshot.md` | MODIFY | `0707b72b…` / 20052 | `6958076af5cd0349713b247a2e165e374f924e9679dc0442a3aef28ec731d7af` / 20047 |
| `agent-tasks/TC-scheduler-lease-claim.md` | MODIFY | `c7607ba7…` / 21625 | `d7cceea6419e31dac788600210d94ff10dcfd67508c54b027c19857c0dbb4f1a` / 21620 |
| `agent-tasks/TC-storage-write-blocked-readiness.md` | MODIFY | `086e59af…` / 18932 | `fc3b4b49bc111224da68e3671ec367e656be98a3f90e89dbf5171e48437b4a42` / 18927 |
| `agent-tasks/TC-telegram-linking-auth.md` | MODIFY | `5239c645…` / 20448 | `21596c62243ac56519f5a9494479f8a2370c12f81e58d62626e9b391dd8852e9` / 20443 |
| `agent-tasks/TC-telegram-unknown-delivery.md` | MODIFY | `7acd9267…` / 21965 | `982aea9408c900c26bf8a8d5ad07b0addd229d995a631cea2071ca19a2ab3093` / 21960 |
| `agent-tasks/TC-ui-reports-detail.md` | MODIFY | `08fbebb3…` / 19917 | `07a653731bc9b755d536866dd86c56dde6e4711bd77f323fd87f368248937b50` / 19912 |
| `agent-tasks/TC-ui-runs-three-states.md` | MODIFY | `9e02ee5c…` / 19588 | `ed82a272277f92f84a492ee06ca48b7f6af77755c2c46de49294c38de97a656d` / 19583 |
| `agent-tasks/TC-x-feasibility-probe.md` | MODIFY | `92bbadaf…` / 17676 | `6eb5305c2b284c441fe3b68b7c8fd7045287798b4fada9d73415dcc3b549a6ba` / 17671 |

**22 file MODIFY. 0 CREATE, 0 DELETE.** Đúng grant (`agent-tasks/*`, `precode/README.md`, handoff này).
`precode/change-control.md` ngoài grant, không bị chạm. Không `__pycache__`; script chạy từ `…/scratchpad/w7/`;
không lệnh git; không mạng.

`TEMPLATE.md` giữ nguyên 11961 byte (tên epoch cũ và mới dài bằng nhau). Card chênh **−5 byte** mỗi cái: dòng
epoch mới dài hơn dòng cũ nhưng câu giải thích ngắn hơn (một file đổi thay vì cả wave FIX8) — chênh lệch nhất
quán trên cả 18 card, đúng như kỳ vọng khi ngoài epoch và một dòng hash thì nội dung không đổi.

## F.4 Evidence (chạy lại lần 7)

### EV-PC10-01 (lần 7)

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T02:28Z / 2026-09-07T02:29Z |
| `oracle` | Mười một phép kiểm (a)…(k), không đổi; cộng phần đếm lại ở §F.2 |
| `observed` | epoch đọc từ card **`PC10-PIN-FCW4f-20260907`** (18/18 đồng thuận); **483 dòng hash / 143 file khớp 100 %**; 669 path; 155 operation ID; 116 SC; 99 mã lỗi §7; 18/18 có `SC49` + bảng R5-01 + fixture boundary; 0 nhãn claim ngoài SRC-PLAN §2; 0 file PC09 bị pin hash; 0 epoch stale |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Check (k) vẫn không phủ `precode/review.md` (ngoài grant — `CR-PC10-05`). Vẫn là self-validation; `audit_route` của packet là `INDEPENDENT_REQUIRED`. |

### EV-PC10-02 (lần 7)

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py`, validator OpenAPI 3.1, mọi test E1–E4, probe SP1, probe CLI/ACP.

## F.5 CR — không đổi

Không CR mới, không CR nào đóng ở vòng này. `CR-PC10-05` (→ PC09, `precode/review.md` còn epoch cũ — nay lệch
**năm** thế hệ so với `FCW4f`) vẫn mở và vẫn ngoài grant của PC10. `CR-PC07-04` **vẫn OPEN và vẫn chặn**
nhánh multipart của `TC-telegram-unknown-delivery`. Phần còn lại y như ADDENDUM `PKT-PC10-FIX5` §E.5.

`status` là `DONE_WITH_CONCERNS` vì: `CR-PC07-04` còn chặn; `CR-PC10-05` mở; ADR-0006 vẫn `proposed` nên mọi
đường dẫn §3 và lệnh §8 còn PROVISIONAL; **phủ `REQ-P0-*` vẫn chưa được kiểm**; và PC10 chỉ có
self-validation.

---

*PKT-PC10-FIX6 · worker-W7 · `lease_released_at` 2026-09-07T02:31Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*

---

# ADDENDUM — PKT-PC10-FIX7 (không re-pin: điều kiện của packet không thỏa)

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC10-FIX7` · authority `AUTH-COORD-PC10-FIX7` · lease `LEASE-PC10-e8` (fencing 8) |
| expires_at | 2026-09-07T20:00Z · enforcement `DOCUMENTARY_DRAFT` · ceiling `DRAFT_FOR_REVIEW` |
| trigger | PC00-FIX9 đổi `precode/README.md` và thêm `evidence/audits/`, `evidence/coordination/` |
| status | `DONE` · completion_claim `DRAFT_FOR_REVIEW` |
| started / finished (UTC) | 2026-09-07T02:35Z / 2026-09-07T02:40Z |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T02:40Z |
| **pin epoch** | **`PC10-PIN-FCW4f-20260907` — KHÔNG đổi.** `PC10-PIN-FCW4g-20260907` **không** được cấp phát |

## G.1 Câu hỏi điều kiện của packet: `precode/README.md` có được pin trên card nào không?

**Không.** Đây là câu trả lời kiểm được, không phải phán đoán:

| Phép kiểm | Kết quả |
| --- | --- |
| Số dòng hash `precode/README.md` trong bảng pin hợp nhất của 18 card | **0** |
| Số card có dòng `\| \`precode/README.md\` \| \`<sha256>\` \| <bytes> \|` trong §0 | **0 / 18** |
| File `precode/*` **thực sự** được pin | `precode/baseline.json`, `precode/decision-register.md`, và 9 file `precode/adr/ADR-000*.md` — **không có** `README.md` |

Đây là **loại trừ có chủ đích từ packet gốc `PKT-PC10`**, không phải sót. `precode/README.md` do chính gói
PC10 tạo ra, nên nó không thể tự pin hash của mình ở §0 của card mà card lại là thứ nó mô tả — vòng lặp
chicken-and-egg. Mọi card đã nói thẳng điều đó ở §2 dòng 91:

> *"`precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói
> PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong
> `evidence/handoffs/PC10-handoff.md`.)"*

Vì `precode/README.md` không nằm trong tập pin, thay đổi của PC00-FIX9 **không** kích hoạt `INV-09` với bất kỳ
card nào, và không card nào trở thành `STALE`. Theo đúng nhánh thứ hai của packet: **không đổi gì, nêu rõ,
và trả lease.**

`evidence/audits/` và `evidence/coordination/` cũng không được pin (packet đã ghi), nên không ảnh hưởng.

## G.2 Một kiểm tra mà packet không yêu cầu nhưng cần làm

PC00-FIX9 ghi vào `precode/README.md` — một file nằm trong write target của PC10. Ghi đè chéo như vậy có thể
làm hỏng **dòng khẳng định epoch** mà `PKT-PC10-FIX3` vừa dựng lên để đóng finding `F-A2R1-03`. Đã kiểm:

| Dòng | Nội dung hiện tại | Trạng thái |
| --- | --- | --- |
| 157 | `**Pin hiện tại: \`PC10-PIN-FCW4f-20260907\`.**` | **đúng** — khớp epoch mà 18/18 card đang khai |
| 164 | lệnh `grep -ho 'Pin epoch: …' agent-tasks/TC-*.md \| sort -u` | **còn nguyên** |
| 170–171 | chuỗi epoch cũ theo thứ tự bị thay | **còn nguyên** |

Phép kiểm **(k)** của EV-PC10-01 chạy trên bản mới và **PASS**: epoch lấy từ card
(`PC10-PIN-FCW4f-20260907`, 18/18 đồng thuận) khớp với cái `precode/README.md` khẳng định, và không epoch cũ
nào bị khẳng định mà thiếu dấu hiệu lịch sử. PC00-FIX9 sửa đúng một hàng và không chạm khối epoch — nên
**grant "epoch line only" của packet này không cần dùng đến.**

## G.3 Changes

**Không file nào bị sửa ngoài handoff này.** 0 card đổi, 0 file `agent-tasks/*` đổi, `precode/README.md`
**không** bị PC10 chạm ở vòng này (giá trị hiện hành `44c36fba4f2c9ad254c10a165113309db171abf42106e80815bfae8054747e01`
/ 15292 byte là của PC00-FIX9, khớp hash Coordinator nêu).

18 card giữ nguyên hash của `PKT-PC10-FIX6`; epoch vẫn là `PC10-PIN-FCW4f-20260907`.

## G.4 Evidence (chạy lại lần 8)

### EV-PC10-01 (lần 8)

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` · `command` `PYTHONDONTWRITEBYTECODE=1 python3 …/scratchpad/w7/verify.py` |
| `started / ended` | 2026-09-07T02:37Z / 2026-09-07T02:38Z |
| `oracle` | Mười một phép kiểm (a)…(k), không đổi |
| `observed` | epoch đọc từ card **`PC10-PIN-FCW4f-20260907`**; **483 dòng hash / 143 file khớp 100 %**; 669 path; 155 operation ID; 116 SC; 99 mã lỗi §7; 18/18 có `SC49` + bảng R5-01 + fixture boundary; 0 nhãn claim ngoài SRC-PLAN §2; 0 file PC09 bị pin hash; **0 epoch stale** kể cả sau khi PC00-FIX9 ghi vào `precode/README.md` |
| `exit_code` | 0 · `status` **PASS** |
| `limitations` | Check (k) vẫn không phủ `precode/review.md` (ngoài grant — `CR-PC10-05`). Vẫn là self-validation. |

### EV-PC10-02 (lần 8)

18/18 card đủ `## §0.`…`## §13.` + front-matter. `exit_code` 0 · **PASS**.

### Nguồn

`research-radar-spec.md` `d35e1f2d…`, `research-radar-pre-code-plan.md` `f65bb046…` — khớp. `INV-08` không
trigger.

### Vẫn `NOT_RUN`

`evidence/tools/e0_check.py`, validator OpenAPI 3.1, mọi test E1–E4, probe SP1, probe CLI/ACP.

## G.5 CR

Không CR mới, không CR nào đóng. `status` của vòng này là **`DONE`** (không phải `DONE_WITH_CONCERNS`) vì
packet này chỉ hỏi một câu điều kiện và câu trả lời là kiểm được, dứt khoát, không để lại việc dở dang.

Trạng thái tổng của gói PC10 thì **không** đổi và vẫn là `DONE_WITH_CONCERNS` như `PKT-PC10-FIX6` §F.5:
`CR-PC07-04` còn chặn nhánh multipart; `CR-PC10-05` (→ PC09, `precode/review.md` còn epoch cũ — nay lệch
**năm** thế hệ) còn mở và ngoài grant; ADR-0006 vẫn `proposed` nên mọi đường dẫn §3 và lệnh §8 còn
PROVISIONAL; **phủ `REQ-P0-*` vẫn chưa được kiểm**; và PC10 chỉ có self-validation trong khi `audit_route`
là `INDEPENDENT_REQUIRED`.

---

*PKT-PC10-FIX7 · worker-W7 · `lease_released_at` 2026-09-07T02:40Z · ceiling `DRAFT_FOR_REVIEW` · không mục nào là independent audit.*
