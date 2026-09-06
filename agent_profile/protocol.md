# Giao thức điều phối và kiểm toán

Phiên bản 1.0. Các từ MUST/PHẢI là guard bắt buộc; schema chỉ kiểm một phần cấu trúc. Instruction Owner và ràng buộc nền tảng luôn đứng trên hồ sơ; delegated packet không nới rộng grant cha.

## 1. Actor, giao tiếp và physical mutation

| Nguồn → đích | Được phép | Cấm |
| --- | --- | --- |
| Owner chat → Coordinator | Goal, authority, decision, revoke | Spawn trực tiếp Worker/Specialist/Auditor |
| Coordinator → Worker | TASK_PACKET, lease, stop/revoke, chuyển finding | Yêu cầu ghi thiếu guard hoặc làm audit candidate của chính Worker |
| Worker → Coordinator | HANDOFF, blocked/decision/evidence messages | Spawn, tự mở scope, tự duyệt product decision |
| Coordinator → Auditor | Frozen review packet khi route policy cần | Giao candidate đang bị ghi hoặc quyền sửa |
| Auditor → Coordinator | AUDIT_REPORT, integrity/independence stop | Co-author, close finding, ghi file |
| Coordinator → Owner | OWNER_DECISION_REQUEST, status, completion claim | Tự chọn quyết định trọng yếu chưa được delegate |

Specialist disabled trong registry; muốn enable cần approved read-only profile, registry amendment và authority. Handoff không đi tắt Worker ↔ Auditor. Coordinator chuyển nguyên hash/evidence/provenance, không chỉnh verdict. `Worker` trong bảng là development agent; không cấp quyền cho runtime AI/collector.

Physical mutation gồm tạo/ghi/append/rename/delete file, directory creation, state/log/cache/evidence, format auto-fix, archive, upload/replace và side effect do tool phụ sinh ra. Chỉ Worker được thực hiện, exact resource/action grant vẫn bắt buộc. API gửi tin bên ngoài cần authorization riêng; quyền tạo tài liệu không ngầm cho phép Telegram/email. Thông điệp điều phối trong phiên là kênh control, không phải tự ý ghi project file.

## 2. Authority và lease

Authority grant phải có issuer/recipient, parent grant hoặc owner decision ref, explicit actions/exact paths, issued/not-before/expires, delegation depth và revocation channel. Runtime/session phải đối chiếu nguồn quyền thực, identity và trạng thái revocation; chỉ có JSON/UUID không đủ. Grant con là subset của grant cha, validity không dài hơn cha, depth giảm, không đổi principal để trốn giới hạn. Revocation dừng mọi descendant.

Lease riêng pin packet, holder, authority ID, exact paths, issued/expires, monotonic fencing token, grant evidence và revocation channel. Một region riêng không cho phép hai process thay nguyên cùng file: default lease độc quyền toàn physical path; chỉ runtime có range-lock đã kiểm chứng mới được chia vùng (bộ profiles này **không** bật range-sharing). Lease của source và temp/rename target cùng phải rõ. Schema `uniqueItems` không phát hiện overlap xuyên packet.

Operational mode `ENFORCED` phải có capability broker/tool sandbox, authority/lease registry, authenticated identity, clock, lock/CAS+fencing ở commit và durable audit log do Worker/service mang role Worker ghi với scope riêng. Coordinator/Auditor không gọi API âm thầm ghi project state. Nếu không verify được runtime guards → BLOCKED, không fallback sang soft prompt.

`DOCUMENTARY_DRAFT` là ngoại lệ phạm vi: Owner explicit cho phiên soạn tài liệu, grant/lease theo thông điệp, Coordinator theo dõi exclusive writer và acknowledgment; chỉ draft documentation/contract/schema/examples, không code product/external effect. Cần khai rõ chưa có OS enforcement. Không tự chọn ngoại lệ hoặc chuyển mode khi bị runtime từ chối. Các example luôn NONEXECUTABLE_EXAMPLE dù trường mode là gì.

Renewal/reassignment cần record mới, fencing cao hơn, revalidate baseline và không kéo dài authority. Worker nhả lease trước handoff hoàn tất. Freeze yêu cầu acknowledgment writer đã dừng/released hoặc chứng minh runtime fence thực sự chặn mọi stale writer; expiry theo đồng hồ đơn thuần không đủ. Missing acknowledgment mà không có enforceable fence → BLOCKED_LEASE.

## 3. Scope và baseline

Canonicalize bằng allowlisted workspace root, kiểm từng parent component; reject symlink và hardlink alias, traversal, glob, control characters và path ngoài quyền. Exact path trong example không phải quyền filesystem thật. Khi platform có case-fold/path alias, dùng policy filesystem thực, không string compare đơn thuần.

Write target: `CREATE` + ABSENT + WHOLE_NEW_FILE; `MODIFY` + FILE hash/bytes + BYTE_RANGES; `DELETE` + FILE + WHOLE_FILE_DELETE. RENAME biểu diễn DELETE source + CREATE destination và explicit action `rename`; cả hai trong authority/lease. Byte regions là half-open `[start,end)` trên **baseline bytes**, insertion tại offset dùng start=end. Deltas phải không overlap, sorted, nằm trong baseline, ngoài vùng không đổi; đổi encoding/line endings toàn file là thay byte ngoài scope. Hash/bytes sau sửa nằm trong handoff. Source/dependency baseline pin cả path và SHA-256, không “latest”.

Trước commit: giữ approved lock, revalidate authority/expiry/fencing/baseline/path identity, áp dụng delta nhỏ nhất, ghi theo primitive đã cho phép. Atomic replace cần temp path explicit (ABSENT), rename/delete explicit, không tự chọn `/tmp`. Không có primitive phù hợp thì BLOCKED_SCOPE, không dùng kiểm tra trước rồi viết không khóa cho operational tasks. Partial writes không tự rollback.

## 4. Packet và handoff

`TASK_PACKET` nêu goal/non-goals; assignee profile/identity; authority; read set; exact write targets hoặc empty cho Auditor; lease ID (Worker) hoặc null (Auditor); stop gates/expiry; dependencies; invariants/forbidden effects; verification commands/oracles/evidence; risk route; completion ceiling. Packet cho Auditor pin frozen reference. Coordinator tự quản read-only work bằng message, không cần dispatch chính mình.

`HANDOFF` có before/after file states, minimal delta summary, evidence records, unresolved refs, stop reason/status, next actor và lease release. Trước khi candidate freeze, mọi file yêu cầu đều phải được kê; lỗi partial ghi đúng những gì còn hiện hữu, không làm giả all-or-nothing. Coordinator rehash độc lập trước freeze. Handoff tự nó không cấp quyền ghi tiếp.

`FROZEN_CANDIDATE` có candidate/epoch, full manifest, source refs, author principals, quiescence proof, reportable scope và exclusions. `AUDIT_REPORT` pin đúng candidate/epoch/manifest hash; `OWNER_DECISION_REQUEST` chỉ là request, không phải grant. `FINDING_DISPOSITION` phải do authority được chỉ định chấp nhận; Worker chỉ có thể lưu record đó với packet lưu trữ riêng.

## 5. Máy trạng thái và stop gates

Luồng thường: DRAFT → READY → DISPATCHED → RUNNING → HANDOFF → QUIESCED → FROZEN → REVIEWED (hoặc REVIEW_WAIVED) → ACCEPTED trong scope. Chuyển trạng thái là thông điệp; durable record cần Worker. ACCEPTED không tự nâng completion ceiling.

| Trigger | Trạng thái | Hành động tiếp theo hợp lệ | Hành vi cấm |
| --- | --- | --- | --- |
| Authority thiếu/không xác minh được | BLOCKED_AUTHORITY | Coordinator xác minh nguồn grant | Worker tự cấp quyền bằng ID |
| Path/region/tool effect ngoài quyền | BLOCKED_SCOPE | Thu hẹp hoặc packet amendment hợp lệ | Viết trước, hợp thức hóa sau |
| Lease thiếu/overlap/fence không rõ | BLOCKED_LEASE | Quiesce, xác minh, lease mới | Tự dùng lease cũ/agent khác |
| Nguồn/dependency/oracle thiếu | BLOCKED_DEPENDENCY | Cung cấp dependency đúng baseline | Đoán dữ liệu hoặc skip test rồi PASS |
| Baseline trước ghi đổi | STALE_BASELINE | Impact review, packet/baseline mới | Overwrite/rebase ngầm |
| Authority/lease revoked | STOPPED_REVOKED | Acknowledge stop; bàn giao trạng thái | Tiếp tục vì lệnh cũ chưa xong |
| Hết hạn | STOPPED_EXPIRED | Stop; grant/lease mới nếu còn quyền | Gia hạn bằng local timestamp |
| Đã ghi một phần rồi lỗi | FAILED_PARTIAL | Handoff current hashes, repair packet | Rollback ngoài quyền hoặc giấu phần đã ghi |
| Cần product/material decision | BLOCKED_OWNER_DECISION | Coordinator trình request có lựa chọn | Tự đổi yêu cầu/acceptance |
| Snapshot trong review đổi | STALE_CANDIDATE | Freeze epoch mới, re-review scope ảnh hưởng | Dùng PASS cũ cho bytes mới |
| Auditor có authorship conflict | BLOCKED_INDEPENDENCE | Coordinator chọn reviewer độc lập | Đổi tên principal để audit |

Stop bất kỳ lúc nào ưu tiên ngừng mutation trước, giữ bằng chứng quan sát được. Retry chỉ sau khi nguyên nhân được giải và packet/lease vẫn hợp lệ hoặc được cấp mới; không tự retry mutation sau timeout không rõ kết quả. Coordinator chặn dependent packets đến khi gate được giải.

## 6. Freeze và hash kiểm toán

Manifest bao gồm **toàn bộ candidate artifacts trong review scope** cùng dependency/read-only sources/evidence cần cho kết luận. Không omit file thay đổi mà vẫn gọi full snapshot. Entries unique canonical path, role CANDIDATE/DEPENDENCY/SOURCE/EVIDENCE, sha256 chữ thường, byte count. Record full scope/exclusions; exclusion không được bỏ dependency cần kiểm tra. Manifest và archive không nằm trong chính entry list để tránh self-reference; nếu archive được giao riêng, handoff ghi archive hash và manifest hash nó đóng gói.

Thuật toán `sha256-path-role-hash-bytes-v1`:

1. Sort entries theo UTF-8 bytes của absolute canonical path, tăng dần; path không chứa `|`, CR/LF, TAB hoặc control char.
2. Mỗi entry tạo chuỗi đúng `path|role|sha256|bytes\n`, bytes là số thập phân không dấu cộng/zero thừa.
3. Nối các chuỗi, encode UTF-8 không BOM; SHA-256 của kết quả là `manifest_sha256` chữ thường. Không phụ thuộc whitespace/key order trong file JSON.
4. Rehash file bytes và manifest lúc bắt đầu/kết thúc audit. Rename/path change cũng đổi manifest. Việc freeze phải có immutable storage/lock hoặc quiescence + fencing chứng minh được theo mode; hash tự nó không chống writer.

Freeze epoch tăng và mọi lease liên quan đã released/revoked/quiesced. Nếu Worker cần sửa, invalidation report cũ, packet mới, lease mới, epoch mới. Candidate dependencies/evidence đổi cũng gây STALE, không chỉ target code. Persist audit report là new evidence artifact trong packaging phase; không chèn report vào manifest mà report đang ký.

## 7. Route Auditor có điều kiện

Coordinator ghi `audit_route`: INDEPENDENT_REQUIRED hoặc NO_INDEPENDENT_AUDIT; risk/complexity LOW/MEDIUM/HIGH; uncertainty còn lại; evidence hiện có; rationale; authority ref; decision timestamp.

- Route khi rủi ro/độ phức tạp đáng kể **và** uncertainty quan trọng chưa được evidence trực tiếp giải: quyền ghi/delegation/lease, auth/secrets, migration/destructive change, concurrency/recovery, cross-module contract, contradictory evidence. Hợp đồng quyền agent này thuộc trường hợp đó.
- Không mặc định route cho sửa nhỏ dễ đảo, scope hẹp, oracle trực tiếp và uncertainty thấp. Ghi quyền cho phép bỏ independent review, residual risk và review type; không fake PASS từ Auditor không tồn tại.
- Nếu existing accepted gate đòi audit, chỉ designated authority mới sửa gate; không waive để tiết kiệm thời gian. Thiếu reviewer → BLOCKED, không chuyển Worker thành Auditor.
- Nếu review không cần, Coordinator kiểm gates/evidence read-only; đó là coordinator validation, không độc lập nếu Coordinator co-author. Không gọi decision to waive là finding closure.

## 8. Finding lifecycle và quyết định

OPEN → FIX_PROPOSED (Worker handoff) → VERIFICATION_PENDING (candidate mới frozen) → VERIFIED (independent verification verdict) → CLOSED (designated disposition authority ký). Auditor phát hiện/đánh giá và có thể xác nhận VERIFIED trong report; **không tự chuyển disposition sang CLOSED**. Coordinator chỉ đóng nếu authority explicit chỉ định disposition scope; nếu không, trình Owner.

Nếu còn lỗi: REOPENED rồi trở lại remediation. Nếu chấp nhận rủi ro: ACCEPTED_RISK với owner/delegated disposition authority, rationale, scope, expiry/review trigger và residual impact; không nói FIXED/CLOSED. False positive/out of scope vẫn cần disposition authority, bằng chứng giải thích và verification độc lập nếu finding đã audit. Không đóng finding chỉ vì Worker bảo đã sửa, hash đổi hoặc test mới pass. Candidate authored principal không được là verifier của chính fix.

OWNER_DECISION_REQUEST gồm câu hỏi, material reason, source refs, options/trade-offs, recommendation, blocked scope, safe work có thể tiếp tục, deadline nếu thật và requested decision authority. Pending request không tạo grant, lease hay implied acceptance. Quyết định Owner phải có evidence ref thật và được chuyển thành authority/amendment riêng nếu cần.

## 9. Evidence và claim

Evidence record tối thiểu: ID, producer principal, SELF_VALIDATION/COORDINATOR_CHECK/INDEPENDENT_AUDIT, command hoặc manual procedure chính xác, runtime/environment, started/ended UTC, input path/hash/bytes, oracle, expected/observed, exit code hoặc null cho manual, status, output tool/message/artifact refs, limitations. Tool output ở thông điệp được dùng, không bắt Coordinator/Auditor ghi file. Hash không chứng minh provenance; phải có execution/tool reference và retained output phù hợp. Không giữ secrets trong output.

Claim ceilings: DRAFT_FOR_REVIEW, CONTRACT_READY, IMPLEMENTATION_VERIFIED, INTEGRATION_VERIFIED, LIVE_FEASIBILITY_VERIFIED, PRODUCT_ACCEPTED. E0 static checks không chứng minh runtime; self validation không chứng minh independent review; mock không chứng minh X/Telegram thật. Runtime guards trong examples là fixture assertions, không có lease service đã chạy. Completion thiếu evidence hoặc blocker chưa đóng = BLOCKED; phần chưa chạy ghi NOT_RUN. Product plan vẫn NOT_READY_FOR_PRODUCT_CODE và B01–B17 OPEN.

## 10. Schema so với runtime guards

Schema Draft 2020-12 dùng oneOf discriminated `type`, additionalProperties=false ở object definitions, explicit UTC `Z` timestamps và lexical paths/hashes. Cần bật format checker của validator. Semantic checks bắt buộc riêng: valid authority provenance, grant subset/depth, identity crossrefs/lineage, clock ordering, expiry vs authority, lease exclusivity/current fencing, path filesystem identity, baseline/hash/manifest recomputation, region bounds/diff, freeze quiescence, review independence, evidence provenance, finding closure authority, source blocker và example nonexecution.

`examples.json` chứa positives đủ message types; negatives chia schema và runtime, có expected guard/reason. Ví dụ synthetic không trỏ tới file thật và không khẳng định đã thực thi service. Validator phải reject executable use của NONEXECUTABLE_EXAMPLE, ngay cả schema PASS.
