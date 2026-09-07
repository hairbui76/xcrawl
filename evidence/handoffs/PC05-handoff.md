---
contract_id: CT-handoff-PC05
version: 0.1.0
status: draft
owner_role: connector contract owner
source_refs: [SRC-PLAN §5.1, SRC-PLAN §6, SRC-PLAN §11 PC05, SRC-PLAN §12 SP1, SRC-SPEC §2.3, SRC-SPEC §3.2, SRC-SPEC §11.2, SRC-SPEC §13 M0, SRC-SPEC §13.2]
requirement_refs: [REQ-A1, REQ-A6, REQ-A7, REQ-D08, REQ-D09, REQ-D31, REQ-D32, REQ-D33, REQ-D34, REQ-AC01, REQ-AC03, REQ-AC04]
decision_refs: [B05, B12, AMD-B05, AMD-B12, "R-01 (A1-R1)", "R-02 (A1-R1)", "R-03 (A1-R1)", "R-04 (A1-R1)"]
invariant_refs: [I02, I10, I11]
producers: [worker-W4]
consumers: [Coordinator, PC06, PC07, PC08, PC09, PC10]
dependencies: [contracts/ports.yaml, contracts/modules.yaml, contracts/errors.yaml, contracts/data/entities.yaml, contracts/state/run.yaml]
scope: HANDOFF của PKT-PC05 — wire HTTP, hai schema collector, probe protocol, tám fixture thu thập.
verification: SELF_VALIDATION (EV-PC05-01..04) bằng script lint trong scratch dir của worker.
claim_ceiling: DRAFT_FOR_REVIEW
---

# HANDOFF — PKT-PC05

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC05` |
| worker principal | `worker-W4` (tiếp nối worker của PC03; packet mới, lease mới) |
| authority_id | `AUTH-COORD-PC05` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC05-e1` (exclusive, fencing 1) |
| enforcement_mode | `DOCUMENTARY_DRAFT` |
| status | **DONE_WITH_CONCERNS** |
| completion_claim | `DRAFT_FOR_REVIEW` |
| started_at (UTC) | 2026-09-06T18:09Z |
| lease_released_at (UTC) | 2026-09-06T18:31Z |
| next actor | Coordinator |

`DONE_WITH_CONCERNS` vì: (a) năm `CR-PC05-nn` cần định tuyến; (b) năm giá trị `KC` của arXiv/OpenAlex cố ý
để trống và chặn `CONTRACT_READY` của research connector; (c) probe **chưa chạy** — theo thiết kế.

## 2. Changes — mọi file đã tạo

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `contracts/http/openapi.yaml` | CREATE | ABSENT | `daaf5521635ab5b5fef57e1b1c77b4ac2b8e607a2776d21934a859c009809140` | 217807 |
| `contracts/schemas/worker-assignment.schema.json` | CREATE | ABSENT | `14efde6fdbff8a19ed2d931660a2752cc40ae96a2ecb1aa5594bdcba87fd5c18` | 19506 |
| `contracts/schemas/ingest-receipt.schema.json` | CREATE | ABSENT | `ff5232f46bb08369ea9af653d652d7782a42ea16798992f2507878c964ac537c` | 16970 |
| `contracts/ops/collector-probe.md` | CREATE | ABSENT | `35e31f7527023b4bd14f5ef62b45fc58522a6899cb96b440604b49c536f116be` | 24385 |
| `acceptance/fixtures/collection/README.md` | CREATE | ABSENT | `2c970915f960d695a90e1c397b386a5b0be76e03a4ae4c270258b3a6edd65629` | 6805 |
| `acceptance/fixtures/collection/a-feed-layout-changed.json` | CREATE | ABSENT | `d80935a9e4fc655af26971380e076585f08435fe7d3ac1f5768080147c7fae62` | 9026 |
| `acceptance/fixtures/collection/b-cursor-invalidated-reread-dedup.json` | CREATE | ABSENT | `73a0d3ccc76f97843b991bf308d29e972421e872dc4b7ca3fadb6f20563b00c0` | 12825 |
| `acceptance/fixtures/collection/c-challenge-mid-batch.json` | CREATE | ABSENT | `4e4b94a37321317b239b71640f26c607630cf57dc3d1bdbff46a818a5a6438a6` | 12117 |
| `acceptance/fixtures/collection/d-duplicate-ingest-replay.json` | CREATE | ABSENT | `f72fd95660ebc9dbd5c2c720ff9cf2bd435b6a77c995d4fe0a90e5b6066b3f4c` | 10429 |
| `acceptance/fixtures/collection/e-limit-reached-stop.json` | CREATE | ABSENT | `e80cbd1d6fcd2282424462ae4859f4e54248553fb780a60df1001c13f05e6843` | 7802 |
| `acceptance/fixtures/collection/f-two-workers-claim-same-assignment.json` | CREATE | ABSENT | `a67bf9f7276ee8952d7662481525a28ca15868feef1907b3c9650c5dcc0d976a` | 9393 |
| `acceptance/fixtures/collection/g-schedule-due-claim.json` | CREATE | ABSENT | `c254460460c5564d52078d43932374069cda85e6a1337c65a56bc1a504e95125` | 11857 |
| `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json` | CREATE | ABSENT | `54a4794c7ab19acbeefa7ee1ff2b8a42820a085eb624cdd79655cc05acda527c` | 7478 |
| `evidence/handoffs/PC05-handoff.md` | CREATE | ABSENT | (file này) | — |

Thư mục `contracts/http/` và `acceptance/fixtures/collection/` được tạo mới.
Không file nào ngoài danh sách trên bị chạm. Không lệnh git mutation nào được chạy. Không truy cập mạng.
`PYTHONDONTWRITEBYTECODE=1`; không có `__pycache__`. Ba script sinh/lint nằm ở
`…/scratchpad/w4/` (`gen_openapi.py`, `assemble_openapi.py`, `gen_fixtures.py`, `lint_pc05.py`), ngoài repo.

**Xác nhận không chạm file PC03** (lease PC03 đã trả; sửa chúng sẽ là vi phạm): hash của cả bảy file PC03
tại thời điểm handoff BẰNG ĐÚNG hash ghi trong `PC03-handoff.md` — `run.yaml 8acb7bbf…`, `analysis.yaml
73be908d…`, `report.yaml e60ef74f…`, `delivery.yaml 9fcccc25…`, `storage.yaml 608ceea6…`, `errors.yaml
e236aaee…`, `retry-policy.yaml 6369935c…`.

## 3. Source baselines

### 3.1 Nguồn pinned — khớp ở cả hai lần kiểm

| Ref | SHA-256 | Bắt đầu | Trước handoff |
| --- | --- | --- | --- |
| SRC-PLAN | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp | khớp |
| SRC-SPEC | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp | khớp |

### 3.2 Upstream đã dựa vào — **ổn định suốt gói này** (đọc và kiểm lại đều cùng hash)

| Path | SHA-256 |
| --- | --- |
| `contracts/ports.yaml` | `485213cb1f822a62cabf0994f05fb6a663c63fcefa489ef03d7a7ca86a817206` |
| `contracts/data/entities.yaml` | `2235564f2ea4ea50577ce9945b07bf04c6b5b0c83fca703efd759980013b2993` |
| `contracts/modules.yaml` | `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666` |
| `contracts/capabilities.yaml` | `c54cdaaf85be339aff5823902c9cb27a2aa25ebea61c241f1b76d2999e6ea7ab` |
| `contracts/ops/deployment.md` | `4d879f2be6187623410bca378b34fc9aa38771b72e70ba309b8edef04a0f1295` |
| `contracts/schemas/ingest-batch.schema.json` | `01c4d01346d32f165bc9c98060675adb524350ddf76507c888ffd3cd7bdf71f9` |
| `contracts/schemas/target.schema.json` | `436cb97bf04386595b72e0b4ca98034fe4d17256333ec3875a9892b583b44583` |
| `contracts/errors.yaml` (PC03) | `e236aaee44cb340bf58ab822ab3dc434847e3d777b46c5b97b3baf00bd0e1b37` |
| `contracts/retry-policy.yaml` (PC03) | `6369935ca96a5bb249764f0377753645844f9901af475048b6d3e2af1973b119` |
| `contracts/state/run.yaml` (PC03) | `8acb7bbf935ee6854fa41d52604972929f09843838c1c141d861d17f538f3468` |
| `precode/requirements.csv` | `1bf60a1c54721adeedc7bc13b0313fd409d064bb3d3f44283b24885f584b9dbb` |
| `precode/decision-register.md` | `0a64b05095a44ded2ab94ff405881ffe09e26d1277928503d49b1643d101f4c6` |

Khác với PC03, gói này **không** gặp upstream drift: mọi hash đọc lúc bắt đầu vẫn đúng lúc handoff.

**Đã $ref tới các file do gói khác sở hữu, tất cả đều TỒN TẠI tại thời điểm handoff:**
`analysis-result.schema.json`, `report.schema.json`, `saved-snapshot.schema.json`, `target.schema.json`,
`ingest-batch.schema.json`. Chúng có thể còn thay đổi; `$ref` là theo đường dẫn nên không vỡ, nhưng
hình dạng thì Auditor nên kiểm lại ở lần freeze sau.

## 4. Evidence records

Mọi record là `SELF_VALIDATION`. Không có audit độc lập.
Runtime: `python3` + PyYAML 6.0.1 + jsonschema 4.10.3 (baseline §3 cho phép), chạy từ `…/scratchpad/w4/`.
Command chung: `cd <scratch>/w4 && PYTHONDONTWRITEBYTECODE=1 python3 lint_pc05.py`.
started/ended (UTC): 2026-09-06T18:30Z / 18:30Z (lần chạy cuối, sau khi sửa non-schema `$ref`). exit code 0.

### EV-PC05-01 — Cấu trúc OpenAPI
- oracle: `openapi` được pin đúng `3.1.0`; **mỗi** operation `transport: http` của ports.yaml có ĐÚNG MỘT
  `operationId` ở đây và ngược lại; **không** operation `internal` nào lộ ra HTTP; không `operationId` trùng;
  mọi `$ref` resolve được (nội bộ theo pointer, ngoài theo file tồn tại); mọi mutation có `x-idempotency`,
  có đủ status 401/403/422/500, có 503 + header `Retry-After` khi ports.yaml khai `STORAGE_WRITE_FAILED`;
  mọi operation có `x-scenario-refs`; ba mã `FORBIDDEN_EDGE`/`RATE_LIMITED`/`INTERNAL` có mặt (CR-PC03-04).
- observed: `paths=50 operations=54 == ports http ops=54; internal not exposed=31; refs checked=27`
- status: **PASS**
- limitations: **KHÔNG có validator OpenAPI 3.1 nào được cài, và tôi không cài thêm gì** (baseline §3, và
  packet cho phép rõ). Đây là kiểm **cấu trúc bằng script**, KHÔNG phải validate theo đặc tả OpenAPI 3.1.
  Nghĩa là: sai sót thuần cú pháp OpenAPI (ví dụ một keyword đặt sai chỗ mà vẫn là YAML hợp lệ) sẽ **không**
  bị bắt. Một validator thật nên chạy ở G3.

### EV-PC05-02 — Schema và fixture
- oracle: hai schema mới hợp lệ theo metaschema Draft 2020-12; `ErrorEnvelope` trong openapi có tập trường
  BẰNG ĐÚNG `error_envelope.fields` của errors.yaml và enum `code` BẰNG ĐÚNG tập mã của errors.yaml; mọi
  body fixture mang `validate_*_against` được validate bằng jsonschema; mọi `events[].actor` là caller hợp lệ
  theo `ports.yaml.caller_modules` (ruling R-02); mọi fixture có header `x-contract`.
- observed: `schemas OK; fixtures=8; bodies validated=23; ErrorEnvelope matches errors.yaml`
- status: **PASS**
- limitations: 23 body được validate; các body còn lại (ví dụ request của `worker.report_stop`,
  `worker.register_capabilities`) **không** được validate vì gói sở hữu chưa có schema đóng — chúng cố ý
  không mang `validate_*_against`. `accepted_items` trong fixture được rút gọn còn 1–2 mục đại diện.
  Validate schema **không** chứng minh một implementation hành xử đúng: fixture là `NOT_RUN`.

### EV-PC05-03 — Mã lỗi
- oracle: mọi mã lỗi xuất hiện trong openapi (mô tả response, `x-error-codes-reported-not-returned`) và trong
  fixture (`"code": "..."`) đều tồn tại trong `contracts/errors.yaml`.
- observed: `error codes used=23, all present in errors.yaml`; 0 mã lạ · status: **PASS**
- limitations: quét bằng regex; một mã nằm trong prose tự do có thể bị bỏ sót.

### EV-PC05-04 — Tài liệu probe
- oracle: có đủ mục bắt buộc của packet (`NOT_RUN`, go/no-go, điều kiện dừng, cổng chấp nhận của Owner, KC,
  5–10 đợt); mọi tham số số học ở §3 có đủ `value` + `unit` + `status` + lý do dài hơn 20 ký tự.
- observed: `probe doc present, 20588 bytes; numeric rows matched=8` — cả 8 đều có đơn vị và lý do đạt
  · status: **PASS**
- limitations: kiểm **sự có mặt** của lý do, không kiểm lý do có đúng không. Các ngưỡng go/no-go ở §7 là
  đề xuất của tôi và **chưa được Owner chấp nhận** — đó chính là cổng §6.

### Không chạy
- Probe X thật (5–10 đợt): **NOT_RUN** — và đúng theo thiết kế: SP1 đòi Owner chấp nhận trước.
- Fixture như test đã chạy: **NOT_RUN** — chưa có harness, chưa có implementation.
- Validator OpenAPI 3.1 chính thức: **NOT_RUN** (không cài thêm gói).
- Gọi arXiv/OpenAlex để đọc hạn mức: **NOT_RUN** (không có mạng, và đó là REQ-A6 `KC`).
- Audit độc lập: **NOT_RUN**.

## 5. Checklist của packet

| # | Mục | Trạng thái | Ở đâu |
| --- | --- | --- | --- |
| 1 | claim/heartbeat/ingest/stop/resume: payload size, provenance, auth — **mọi** http op được phủ (script check) | **DONE** | `contracts/http/openapi.yaml`; EV-PC05-01 khẳng định 54/54, không thiếu không thừa; `x-transport-limits` cho size; `security` + `x-auth-scope` cho auth |
| 2 | Giới hạn nguồn được ghi | **DONE** | `collector-probe.md` §8 (SL-1..SL-8) và `worker-assignment.schema.json` `$defs.source_limits` — gửi kèm mỗi assignment để collector không phải suy diễn |
| 3 | arXiv/OpenAlex pin dạng KC, không gọi không giới hạn | **PARTIAL** | `collector-probe.md` §9.2: bốn tham số để `KC` có chủ đích, sàn `min_interval_ms = 3000` đang có hiệu lực, tham chiếu `retry-policy §research_connector_rate_limit`. **PARTIAL vì không có URL tài liệu** — xem CR-PC05-03 |
| 4 | Probe 5–10 đợt, go/no-go, điều kiện dừng, cổng Owner, NOT_RUN | **DONE** | `collector-probe.md` §0 (NOT_RUN), §3 (5–10 đợt), §4 (ST-1..ST-8), §6 (cổng Owner), §7 (GO-1..GO-7) |
| 5 | Fixture (a)–(h); test nền tảng không cần X live | **DONE** | Tám file + README §"Vì sao các fixture này chạy offline được" |

### Invariant của packet

| ID | Thể hiện ở đâu |
| --- | --- |
| I02 | `ingest-receipt.schema.json` (`checkpoint_ack`, `x-contract.checkpoint_only_rule`); fixture (b), (d); openapi mô tả `ingest.submit_batch` là đường chính, `commit_checkpoint` chỉ tiến con trỏ |
| I10 (phần collector) | `worker-assignment.schema.json` `$defs.lease`; fixture (c), (f), (g); openapi `run.resume` ghi rõ cấp lease MỚI |
| I11 (connector) | `collector-probe.md` §9.1 CN-2/CN-3/CN-4; fixture (h) `forbidden_effects` |
| Timeout = unknown outcome | `info.description` wire rules; `ingest-receipt` `x-contract.ack_loss_procedure`; fixture (d) sự kiện 1 có `response_status: null` **có chủ đích** |
| Không network call trong DB transaction | `info.description` wire rules; openapi `report.publish` không tồn tại trên HTTP (internal) và outbox nằm trong transaction |

### Chỉ dẫn riêng của Coordinator

| Chỉ dẫn | Trạng thái |
| --- | --- |
| (a) CR-PC03-04: openapi phải tham chiếu `FORBIDDEN_EDGE`, `RATE_LIMITED`, `INTERNAL` | **DONE** — cả ba là response mặc định của mọi operation (`INTERNAL` 500, `FORBIDDEN_EDGE` 403 mọi op; `RATE_LIMITED` 429 mọi mutation). EV-PC05-01 kiểm sự có mặt. CR-PC03-04 coi như đã thỏa |
| (b) Chọn security scheme PROVISIONAL, nêu ở `info.x-contract` | **DONE** — `info.x-contract.security_scheme_decision`: cookie HttpOnly + CSRF double-submit cho UI, bearer cho collector/worker, header bí mật cho Telegram webhook. Đúng như chỉ dẫn; PC08 (W2) sở hữu quyết định cuối |
| (c) Checkpoint theo R-01 phải hiện ra trong description của ingest endpoints | **DONE** — `ingest.submit_batch` mô tả là ĐƯỜNG CHÍNH; `ingest.commit_checkpoint` mô tả guard và oracle của R-01 nguyên văn |
| (d) `task_type` theo entities.yaml | **DONE** — không có enum `task_type` nào trong file của tôi; PC05 không định nghĩa lại. Lệch tên vẫn tồn tại giữa ports.yaml và entities.yaml, đã raise ở CR-PC03-05 (PC03) và nhắc lại tại CR-PC05-05 |

## 6. Unresolved

### 6.1 Change requests

| ID | Với gói | Nội dung |
| --- | --- | --- |
| `CR-PC05-01` | PC03 (`errors.yaml`) + PC01 (`ports.yaml`) | Không có mã lỗi cho "nguồn đổi bố cục" và không có `stop_reason` tương ứng ở `worker.report_stop`. Giá trị gần đúng nhất (`source_blocked`) **sai nghĩa**: bố cục đổi không phải bị chặn, và cách xử lý đúng khác hẳn (sửa parser vs. chờ gỡ chặn). Đề nghị: mã `SOURCE_LAYOUT_CHANGED` + `stop_reason: parser_degraded`. Fixture (a) dùng `source_blocked` + cờ `parser_degraded: true` và mang khối `pending_cr`. Tôi **không** tự đặt mã mới (baseline §6). |
| `CR-PC05-02` | PC08 | Security scheme trong `info.x-contract.security_scheme_decision` là PROVISIONAL do Coordinator chỉ định. PC08 sở hữu quyết định cuối (thời hạn phiên, xoay token, lưu at-rest, thu hồi). Nếu PC08 chọn khác (ví dụ bearer thay cookie cho UI), `openapi.yaml` `components.securitySchemes` và mọi `CsrfTokenHeader` phải cập nhật. |
| `CR-PC05-03` | PC00 / Owner | Packet yêu cầu ghi "the exact doc URL from the sources" cho arXiv/OpenAlex. Tôi đã tra cả hai nguồn pinned: **không nguồn nào chứa URL** — SRC-SPEC D34 và §13.2 chỉ nói "đọc tài liệu chính thức". Tôi ghi **định danh tài liệu** thay cho URL và **không bịa URL**. Cần Owner hoặc PC00 cung cấp URL chính xác, hoặc chấp nhận rằng nó được xác định tại thời điểm triển khai. |
| `CR-PC05-04` | PC01 (`ports.yaml`) | `auth.logout`, `worker.release_assignment`, `analysis.heartbeat` là mutation nhưng `error_codes` không có `VALIDATION_ERROR`, dù cả ba đều mang header bắt buộc (`X-Schema-Version`, `X-Request-Id`) và hai trong ba có body. PC05 **đã bổ sung 422 ở tầng wire** thay vì nới lỏng phép kiểm; ports.yaml nên đồng bộ. |
| `CR-PC05-05` | PC01 (`ports.yaml`) | Sáu giá trị `response_schema_planned` trỏ tới hợp đồng **không phải JSON Schema** (`contracts/state/run.yaml`, `state/analysis.yaml`, `state/delivery.yaml`, `data/identity.md`, `ops/secrets.md`, `ops/backup-restore.md`). Một `$ref` OpenAPI tới đó **không dereference được**. PC05 dùng `GenericObject` + `x-schema-source` cho chúng. Đề nghị ports.yaml phân biệt rõ "schema" với "hợp đồng mô tả hình dạng". Nhắc lại `CR-PC03-05` (lệch tên `task_type`) vẫn mở. |

### 6.2 PROVISIONAL do PC05 đưa ra

1. **Thiết kế URL và phương thức** cho cả 50 path. ports.yaml không quy định path; tôi chọn `/v1/<domain>/...`
   REST-ish, giữ `operationId` làm nguồn định danh ổn định.
2. **Ánh xạ mã lỗi → HTTP status** (`errors.yaml` không quy định status; đó là việc của PC05). Điểm đáng soi:
   `WORKER_LEASE_EXPIRED` → **412** (lease là một precondition) trong khi `STALE_LEASE` → 409;
   `STORAGE_WRITE_FAILED` → 503 kèm `Retry-After`; `AI_PROVIDER_UNAVAILABLE` → 502.
3. **Năm mã KHÔNG bao giờ là error envelope** của chính lời gọi đó, ghi ở `x-error-codes-reported-not-returned`:
   `INGEST_ACK_LOST` (tình trạng phía client), `IDENTITY_CONFLICT` và `SOURCE_METADATA_UNAVAILABLE`
   (nằm trong `warnings` của 2xx — lô vẫn commit), `X_ACCESS_BLOCKED` và `X_CHALLENGE_REQUIRED` trên
   `worker.report_stop` (được BÁO CÁO, không phải lỗi của lời gọi). Đây là diễn giải của tôi về errors.yaml;
   nếu Auditor đọc khác thì đây là chỗ cần sửa.
4. **`telegram.receive_update` luôn trả 204**, kể cả khi update bị bỏ im lặng — vì một status phân biệt được
   sẽ tự xác nhận bot tồn tại (REQ-S11.3-02). `UNAUTHORIZED_COMMAND` được ghi audit, không gửi ra.
5. **`x-transport-limits`**: body 8 MiB, URL 2048 byte, request timeout 30 s, TLS bắt buộc.
6. **Ngưỡng probe §3 và go/no-go §7** — đặc biệt GO-2 (challenge ≤ 1 mỗi 5 đợt) là ngưỡng về **trải nghiệm**
   chứ không phải kỹ thuật: tần suất cao hơn biến sản phẩm "tự chạy" thành sản phẩm "gọi người".
7. **`delivery_part.state` thêm `sending`** — đã raise ở `CR-PC03-07`, nhắc lại vì openapi phản ánh nó.

### 6.3 Phạm vi cố ý để trống

- Năm giá trị `KC` của arXiv/OpenAlex (§9.2). Cho tới khi được điền, research connector **không được** coi là
  `CONTRACT_READY` (SRC-PLAN §10). Sàn `min_interval_ms = 3000` là **sàn tự đặt thận trọng**, không phải một
  hạn mức đã biết — tôi ghi rõ điều đó tại chỗ.
- `probe_request_min_interval_ms = 2000` cho X: cũng là sàn tự đặt; tôi **không** tìm thấy tài liệu công khai
  nào về hạn mức giao diện web của X và **không** bịa một con số có vẻ chính thức.
- Body của các operation mà gói khác sở hữu schema: `GenericObject` + `x-schema-source`, kèm câu
  "KHÔNG phải giấy phép chấp nhận trường tùy ý: gói sở hữu phải thay bằng schema đóng với
  `additionalProperties: false` trước G3".

### 6.4 Câu hỏi cần Owner

- Xác nhận **D09** (Chrome profile riêng của dự án) — SRC-SPEC §13.1 câu hỏi 1, **chặn M0**.
- Chấp nhận ngân sách §3, điều kiện dừng §4 và tiêu chí go/no-go §7 **trước khi** probe chạy (cổng SP1).
- Hiểu và chấp nhận rủi ro tài khoản X bị hạn chế (REQ-A7, `KC`, không kiểm chứng được trước).
- REQ-OQ05 (giới hạn thật mỗi đợt) — chốt **sau** M0, dùng chính số liệu probe.

## 7. Trạng thái sau handoff

Không file nào bị chạm sau thời điểm này. Sửa tiếp cần packet mới, baseline mới, lease mới.
Worker không tự chứng nhận freeze; `FROZEN_CANDIDATE` do Coordinator phát hành.

- next actor: **Coordinator**
- audit route: `INDEPENDENT_REQUIRED` (chưa chạy — `NOT_RUN`)
- `lease_released_at`: 2026-09-06T18:31Z

---

# ADDENDUM — PKT-PC05-FIX1

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC05-FIX1` |
| authority_id | `AUTH-COORD-PC05-FIX1` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC05-e2` (exclusive, **fencing 2** — thay cho `LEASE-PC05-e1` đã trả) |
| worker principal | `worker-W4` |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-06T18:39Z / 2026-09-06T18:44Z |
| next actor | Coordinator |

## B1. Changes (MODIFY, baseline = hash trong bảng §2 của handoff gốc)

| Path | Op | Before (sha256) | After (sha256) | Bytes trước → sau |
| --- | --- | --- | --- | --- |
| `contracts/http/openapi.yaml` | MODIFY | `daaf5521635ab5b5fef57e1b1c77b4ac2b8e607a2776d21934a859c009809140` | `cda2d5bba01db7a3d58481ffec2b8911088c1a31291a817bebf751130d4e5886` | 217807 → 221777 |
| `contracts/ops/collector-probe.md` | MODIFY | `35e31f7527023b4bd14f5ef62b45fc58522a6899cb96b440604b49c536f116be` | `91a161c8db42c595949682ac73a0b2eccc5c8a11871bb35ffd4ef9c6fb55f122` | 24385 → 24763 |
| `acceptance/fixtures/collection/README.md` | MODIFY | `2c970915f960d695a90e1c397b386a5b0be76e03a4ae4c270258b3a6edd65629` | `11696638789a2a89d0b26deeaad5fca568c69c630e2b79071bd858487caa9d62` | 6805 → 7175 |
| `acceptance/fixtures/collection/a-feed-layout-changed.json` | MODIFY | `d80935a9e4fc655af26971380e076585f08435fe7d3ac1f5768080147c7fae62` | `113f60bda039aeba4ebb7ab18c6180ec52e872b647744a0975c6c5ed2c2aecac` | 9026 → 13428 |

**Không đổi** (trong grant, không cần sửa): `worker-assignment.schema.json` `14efde6f…`,
`ingest-receipt.schema.json` `ff5232f4…`, và bảy fixture `b`–`h` (hash bằng đúng bản gốc).
`openapi.yaml` nâng `info.version` và `x-contract.version` `0.1.0 → 0.2.0`; probe doc và fixture README cũng `0.2.0`.

## B2. Delta theo từng mục của packet

| # | Yêu cầu | Đã làm gì |
| --- | --- | --- |
| 1 | Map `CSRF_REJECTED` (403) trên mọi owner-session mutation | **19/19** owner-session mutation có response 403 `CSRF_REJECTED`; script khẳng định danh sách thiếu là RỖNG. Bearer token và webhook secret KHÔNG được map (không có bề mặt CSRF) — ghi rõ ở `info.x-contract.security_scheme_decision.csrf_scope_vi` |
| 2 | Xác nhận owner mutation mang cookie+CSRF; `backup.*` mang `backupOperatorToken` | **Đã tìm ra một lỗi thật và sửa** (xem B3). Bốn route `backup.*` nay khai DUY NHẤT `[{backupOperatorToken: []}]` |
| 3 | Fixture (a) chuyển sang `SOURCE_LAYOUT_CHANGED`, bỏ `pending_cr` | `stop_reason` → `source_layout_changed`; bỏ cờ `parser_degraded`; khối `pending_cr` bị xóa; response đổi thành 409 với error envelope đầy đủ; **thêm sự kiện 3** (báo lại cùng `stop_report_id` ⇒ `alert_intent_created: false`) để oracle "một alert intent mỗi run" kiểm được; `forbidden_effects` thêm mục cấm dùng `X_ACCESS_BLOCKED` cho tình huống này |
| 4 | Report read bodies trích `report_build_id` và `abort_reason` | `report.list` và `report.get` mang chú thích nêu cả hai cột theo bảng field-level FIX3, kèm câu `abort_reason='empty_period'` là kỳ RỖNG HỢP LỆ và UI **không** được gộp nó với `builder_failure` (I13). `report.publish` là `transport: internal` nên không có path HTTP — nó nằm trong `x-internal-operations-not-exposed` |
| 5 | ErrorEnvelope enum đồng bộ lại theo errors.yaml | Enum sinh trực tiếp từ `contracts/errors.yaml` lúc build ⇒ **28 mã** (26 → 28), gồm `CSRF_REJECTED` và `SOURCE_LAYOUT_CHANGED`. EV-PC05-02 so khớp cả tập trường và tập enum |
| — | Cập nhật kèm theo | `collector-probe.md` ST-7 bỏ đoạn "chưa có mã riêng, dùng tạm `source_blocked`" và nêu mã thật + lý do tách mã; fixture README bỏ mục giới hạn số 2 đã lỗi thời |

## B3. Lỗi thật tìm ra trong lúc làm FIX1 — security requirement bị OR thay vì AND

`openapi.yaml` 0.1.0 khai:

```yaml
security: [{ownerSessionCookie: []}, {ownerCsrfToken: []}]     # SAI
```

Trong OpenAPI, **danh sách** security requirement là **OR**; các khóa **trong cùng một dict** mới là **AND**.
Cách khai cũ vì thế có nghĩa *"cookie MỘT MÌNH là đủ, hoặc CSRF token một mình là đủ"* — tức bảo vệ CSRF mà
`info.x-contract.security_scheme_decision` mô tả **trên thực tế không tồn tại**, và một request giả mạo từ site
khác (trình duyệt tự gửi kèm cookie) sẽ qua được mọi mutation của owner. Nay:

```yaml
security: [{ownerSessionCookie: [], ownerCsrfToken: []}]        # ĐÚNG — AND
```

Hai chỉnh kèm theo, có chủ đích:
- **Read-only chỉ cần cookie.** CSRF bảo vệ thao tác đổi trạng thái; bắt buộc nó trên `GET` chỉ tạo nghi thức
  thừa mà không thêm bảo đảm nào.
- **`backup.*` bỏ đường phiên trình duyệt.** Bản cũ cho phép `[cookie+csrf]` HOẶC `[backupOperatorToken]`,
  nghĩa là một tab đang mở có thể kích hoạt `backup.restore_snapshot`. Điều đó mâu thuẫn với chính mô tả
  scheme mà tôi đã viết ("tách khỏi phiên owner vì restore là thao tác có khóa side effect", AMD-B11).

Đây không nằm trong danh sách yêu cầu của packet; nó lộ ra khi tôi kiểm mục 2 ("confirm every owner mutation
carries cookie+CSRF") thay vì chỉ ghi nhận là đã có.

## B4. Evidence

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC05-01` | `cd <scratch>/w4 && PYTHONDONTWRITEBYTECODE=1 python3 lint_pc05.py` | **PASS** — openapi 3.1.0; paths=50, operations=**54 == 54** ops http của ports.yaml; 0/31 internal bị lộ; 27 `$ref` resolve; mọi mutation có idempotency + 401/403/422/500 (+503/Retry-After) | **0** |
| `EV-PC05-02` | (cùng lệnh) | **PASS** — hai schema hợp lệ Draft 2020-12; 8 fixture; **23 body** validate; `ErrorEnvelope` khớp `errors.yaml` cả tập trường lẫn **enum 28 mã** | 0 |
| `EV-PC05-03` | (cùng lệnh) | **PASS** — 25 mã lỗi được dùng (23 → 25), tất cả có trong `errors.yaml` | 0 |
| `EV-PC05-04` | (cùng lệnh) | **PASS** — probe doc 20920 bytes; 8 tham số số học đều đủ value+unit+status+lý do | 0 |
| `EV-PC05-05` | script inline cùng scratch dir | **PASS** — 19/19 owner-session mutation có 403 `CSRF_REJECTED` (danh sách thiếu rỗng); 4/4 route `backup.*` khai đúng `[{backupOperatorToken: []}]` | 0 |

**Phép kiểm được siết ở FIX1.** Theo luật fixture ràng buộc trong ruling FIX3, EV-PC05-02 nay kiểm thêm
`(caller, owner_module, operation) ∈ contracts/modules.yaml.allowed_edges`, chứ không chỉ
`actor ∈ caller_modules`. **108 bộ ba** `allowed_edges` được nạp; cả 8 fixture qua. Phép kiểm này KHÔNG rỗng:
nếu tập cạnh rỗng thì mọi sự kiện sẽ fail.

- type: `SELF_VALIDATION`. started/ended UTC: 2026-09-06T18:42Z / 18:43Z.
- **Đã validate ngược lại:** `contracts/ports.yaml` `100c94c1ffbaa7cc0bc418b83fd6a9672ff3ee1f60c5426b7fa1e9f2ee3ac81a`;
  `contracts/errors.yaml` `3201bbe86a3ef373a4fb35c265cd9f27ed60f6ce2af3fd65a76c0dcfb032d86b`
  (chính bản do PKT-PC03-FIX1 tạo ra ngay trước gói này);
  `contracts/modules.yaml` `bd44d7340aabbab324afdebb5452c4941d1c6f0623452d239360e31738d4b666`.
- Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.
- Giới hạn giữ nguyên như handoff gốc §4: **vẫn không có validator OpenAPI 3.1** và tôi không cài thêm gì —
  EV-01 là kiểm cấu trúc bằng script, không phải validate theo đặc tả. Fixture vẫn `NOT_RUN`.

## B5. Concerns

1. **`CR-PC05-04` đã được W2 giải quyết ngược dòng.** Tại `ports.yaml 100c94c1…`, cả ba operation đã có
   `VALIDATION_ERROR` (`auth.logout` còn có sẵn `CSRF_REJECTED`). Bản sinh lần này báo `422 added: []` — tức
   phần bù đắp tạm thời của PC05 không còn cần. Không còn khác biệt giữa openapi và ports.yaml ở điểm này.
2. **`SOURCE_LAYOUT_CHANGED` chưa có ở `worker.report_stop` của ports.yaml.** Tại `100c94c1…`, `stop_reason`
   của operation đó vẫn chưa có `source_layout_changed` và `error_codes` chưa có mã này. Fixture (a) và
   `run.yaml` T-RUN-24 đã dùng mã thật; phần ports.yaml thuộc PKT-PC01-FIX3 và có thể land sau khi tôi trả
   lease. **Cặp này cần Auditor kiểm lại ở lần freeze sau** — nếu W2 chọn tên khác thì fixture (a) và
   `errors.yaml` phải theo `ports.yaml` (thẩm quyền đặt tên operation) hoặc ngược lại theo `errors.yaml`
   (thẩm quyền đặt tên mã).
3. **`report_build_id` và `abort_reason` vẫn chưa có trong `entities.yaml`** (bản `2235564f…` mà tôi đọc).
   `report.list`/`report.get` nay trích dẫn chúng theo bảng field-level của ruling FIX3, nhưng
   `contracts/schemas/report.schema.json` do PC04 sở hữu — tôi **không** sửa nó (ngoài grant). Nếu PC04 không
   thêm hai trường vào schema đó, chú thích của tôi sẽ mô tả những trường mà schema không khai. Đây là mặt
   PC05 của F-A1R2-01 và nó **chưa đóng**.
4. **Không CR mới.** `CR-PC05-01` (mã layout) và `CR-PC08-02`/`CR-PC08-03` (auth) đã được ruling FIX3 giải và
   hiện thực hoá ở đây. `CR-PC05-02`, `-03`, `-05` vẫn mở như handoff gốc §6.1.
5. **Không dùng SC45+.** Fixture (a) chỉ thêm một sự kiện vào scenario đã có (`SC03`/`SC15`), không cần
   scenario ID mới.

---

# ADDENDUM — PKT-PC05-FIX2

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC05-FIX2` |
| authority_id | `AUTH-COORD-PC05-FIX2` (parent `AUTH-OWNER-20260906-01`) |
| lease_id | `LEASE-PC05-e3` (exclusive, **fencing 3**) |
| worker principal | `worker-W4` |
| status | **DONE_WITH_CONCERNS** · completion_claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-06T18:52Z / 2026-09-06T19:03Z |
| next actor | Coordinator |

## D1. Changes (MODIFY, baseline = hash sau FIX1)

| Path | Op | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `acceptance/fixtures/collection/README.md` | MODIFY | `11696638789a2a89d0b26deeaad5fca568c69c630e2b79071bd858487caa9d62` | `7cea261ffa70f25896cf23fd835f49f1a221ed003d83b96ef27d49f06c0fdf34` | 7175 → 10833 |
| `…/a-feed-layout-changed.json` | MODIFY | `113f60bda039aeba4ebb7ab18c6180ec52e872b647744a0975c6c5ed2c2aecac` | `570d8c3853ac7724c666c151079b613ca6b6983ca81308164d81ab797585b0fc` | 13428 → 13419 |
| `…/b-cursor-invalidated-reread-dedup.json` | MODIFY | `73a0d3ccc76f97843b991bf308d29e972421e872dc4b7ca3fadb6f20563b00c0` | `6ea2b75b3690af3a85b218ee8b3b32c9f339f285a86ca0a3a683c206628ec775` | 12825 → 12816 |
| `…/c-challenge-mid-batch.json` | MODIFY | `4e4b94a37321317b239b71640f26c607630cf57dc3d1bdbff46a818a5a6438a6` | `1011138ee01675c7fb9aabaf2fc49fcb24d8a59b1a8d823f785697ff57793ccf` | 12117 → 12096 |
| `…/d-duplicate-ingest-replay.json` | MODIFY | `f72fd95660ebc9dbd5c2c720ff9cf2bd435b6a77c995d4fe0a90e5b6066b3f4c` | `1dc4318167004f3d085fff0b402c9c7bf6c220854db3130c51eb5900d85120fe` | 10429 → 10417 |
| `…/e-limit-reached-stop.json` | MODIFY | `e80cbd1d6fcd2282424462ae4859f4e54248553fb780a60df1001c13f05e6843` | `d00983c5738f84008fbaf928651ab5636494a20426cfe4261430c91c26ac0b04` | 7802 → 7796 |
| `…/f-two-workers-claim-same-assignment.json` | MODIFY | `a67bf9f7276ee8952d7662481525a28ca15868feef1907b3c9650c5dcc0d976a` | `92939afbb6896caae0510ea2d34e638ba5a8d74ea94be89bd9755de33dbe0518` | 9393 → 9384 |
| `…/g-schedule-due-claim.json` | MODIFY | `c254460460c5564d52078d43932374069cda85e6a1337c65a56bc1a504e95125` | `32a9defa30bbbbe334b6e28378b8bcf09f2bc1d002a2fc2275886b6df5ca60ba` | 11857 → 11845 |
| `…/h-metadata-unavailable-post-only.json` | MODIFY | `54a4794c7ab19acbeefa7ee1ff2b8a42820a085eb624cdd79655cc05acda527c` | `7b588ca0ad1999bacdfa78ffb17ba6f0ad1336e399cb291502397f079168079b` | 7478 → 7475 |

**9 file** đổi (8 fixture + README). README → `version: 0.3.0`. Không file nào ngoài
`acceptance/fixtures/collection/*` bị chạm.

## D2. Delta

1. **R4-02 — đổi khóa `operation_id` → `operation`** trong **27 event** trên **8 file**. Kiểm lại: **0 khóa
   `operation_id` còn sót**. Chỉ đổi TÊN KHÓA, thứ tự khóa được giữ (dùng `OrderedDict`), không giá trị nào đổi.
2. **README nêu quy tắc R4-01 nguyên vẹn một đoạn** (ba loại khóa hợp lệ: cột thật trong `entities.yaml`,
   khóa `_`-prefix, hoặc cột mang `pending_cr`), kèm lý do quy ước tồn tại và **trạng thái thật của thư mục này**.
3. **README định nghĩa `edge_assertion: forbidden`** (R4-02): gate ĐẢO kỳ vọng — bộ ba phải VẮNG khỏi
   `allowed_edges` và lỗi mong đợi là `UNAUTHORIZED` / `FORBIDDEN_EDGE` / `CAPABILITY_DENIED`.
4. **Bảng khóa của README** thêm dòng `events[].operation` và siết dòng `events[].actor` để nêu cả điều kiện
   `allowed_edges`.
5. **Gate được siết theo đúng khuyến nghị của F-A1R3-02:** nay **FAIL TO** khi gặp một event dùng khóa cũ
   `operation_id`, khi thiếu hẳn khóa `operation`, hoặc khi `edge_assertion` mang giá trị khác `forbidden`.
   Chế độ hỏng trước đây là *im lặng bỏ qua*; nay là *ồn ào*.

## D3. Evidence — EV-PC05-01..05, một lần chạy

`cd <scratch>/w4 && PYTHONDONTWRITEBYTECODE=1 python3 lint_pc05.py` · **exit 0** · **RESULT: PASS**
type `SELF_VALIDATION`; started/ended UTC 2026-09-06T19:01Z / 19:02Z.

| Gate | Con số |
| --- | --- |
| EV-01 wire | openapi 3.1.0; 50 path; **54 operation == 54** op `transport: http`; 0/31 internal bị lộ; 27 `$ref` resolve |
| EV-02 fixture | 8 fixture; **27 event, khóa `operation`, 0 khóa cũ**; `edge_assertion: forbidden` = **0**; **actor-edge sạch 26/26**; 23 body validate; `ErrorEnvelope` khớp `errors.yaml` (28 mã) |
| EV-05 field-level (R4-01) | 60 entity nạp từ `entities.yaml`; **0 cột kiểm; 0 chưa resolve** |
| EV-03 mã lỗi | 25 mã dùng, tất cả có trong `errors.yaml` |
| EV-04 probe | 20920 bytes; 8 tham số số học đủ value+unit+status+lý do |

**Vì sao 27 event nhưng 26 sạch actor-edge.** Một event là sự kiện CỤC BỘ không có lời gọi HTTP
(`c-challenge-mid-batch.json` ev2: collector đã tải 7 bài nhưng chưa gửi thì gặp CAPTCHA) và mang
`operation: null` một cách có chủ đích. Gate bỏ qua nó khi kiểm cạnh nhưng VẪN kiểm khóa. Con số 26 khớp đúng
với `EV-A1R3-04` của A1 ("PC05's 26 events clean").

**Đã validate ngược lại** (đo NGAY TRƯỚC và NGAY SAU lần chạy, giống nhau):
`contracts/ports.yaml` `100c94c1…`, `contracts/modules.yaml` `89b348aa…`,
`contracts/data/entities.yaml` `209cf03e…`. Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.

## D4. Concerns

1. **Gate field-level là RỖNG trên thư mục này, và con số 0 KHÔNG có nghĩa "đã kiểm và sạch".**
   Tám fixture thu thập không dùng hình dạng `given.rows` / `expected.rows`; chúng ghi kỳ vọng bằng
   `durable_rows_expected` (câu văn) và `expected_target_state`. Gate R4-01 vì thế kiểm **0 cột**. Đây chính là
   dạng hỏng mà F-A1R3-02 cảnh báo — một gate không thấy gì trông giống hệt một gate thấy mọi thứ đều sạch.
   Tôi đã ghi rõ điều này ở README (mục quy ước R4-01 và `Giới hạn đã biết` mục 5) để người đọc fixture không
   hiểu nhầm, nhưng **nếu Coordinator muốn thư mục này thực sự nằm dưới gate, các fixture cần chuyển sang hình
   dạng `rows` có cấu trúc** — đó là một thay đổi thiết kế, không phải một sửa lỗi, nên tôi không tự làm.
2. **Không fixture nào ở đây dùng `edge_assertion`.** Quy ước vẫn được ghi vào README vì R4-02 nêu đích danh
   `collection`. Ca âm gần nhất — `f-two-workers-claim-same-assignment.json` — là **stale lease**: một cạnh
   HỢP LỆ bị từ chối vì epoch cũ, KHÔNG phải cạnh bị cấm; nó đúng khi không mang marker. Nếu Coordinator muốn
   `collection` có một ca cạnh-bị-cấm thật (ví dụ collector gọi `save.create`, denied case NC-01), đó là một
   fixture MỚI, ngoài scope packet này.
3. **Packet nói 26 event, thực tế 27.** Chênh một vì `PKT-PC05-FIX1` đã thêm một event vào fixture (a) sau khi
   A1 đếm ở epoch 3. Không mất event nào; 27 là con số đúng sau FIX1.
4. **Upstream đang chuyển trong lúc chạy.** `modules.yaml` (`bd44d734…` → `89b348aa…`) và `entities.yaml`
   (`2235564f…` → `209cf03e…`) đã đổi so với FIX1 — các gói FIX4 khác đang land. Gate chạy lại và PASS trên
   đúng bản mới; hash được ghim hai đầu ở D3.
5. **Không CR mới.**

---

# ADDENDUM — PKT-PC05-FIX3

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC05-FIX3` (đồng bộ với `PKT-PC03-FIX3` / CR-PC10-02) |
| authority_id | `AUTH-COORD-PC05-FIX3` · lease `LEASE-PC05-e4` (**fencing 4**) |
| worker principal | `worker-W4` |
| status | **DONE** · completion_claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-06T19:26Z / 2026-09-06T19:36Z |
| next actor | Coordinator |

## F1. Changes (MODIFY, baseline = hash sau FIX1/FIX2)

| Path | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `contracts/http/openapi.yaml` | `cda2d5bba01db7a3d58481ffec2b8911088c1a31291a817bebf751130d4e5886` | `258fce244764299ceae5efd53902bf22d0bdf5017e4fa528527a5d9606c4de1b` | 221777 → 227676 |
| `contracts/ops/collector-probe.md` | `91a161c8db42c595949682ac73a0b2eccc5c8a11871bb35ffd4ef9c6fb55f122` | `03e88010ce8d9a8e7ed7afbb5ab01caf4099ac77cde1298fb155731dddd55ca1` | 24763 → 26780 |

`openapi.yaml` → `0.3.0`; `collector-probe.md` → `0.3.0`.

## F2. Xác minh ports.yaml (theo yêu cầu packet)

`sha256 = 87c95da46c607c977a7f…`. `grep -c 'rate_limited'` → **2**; `grep -c 'RATE_LIMITED'` → **2**.
`worker.report_stop.request_summary_vi` liệt kê đủ **tám** `stop_reason` gồm `rate_limited`, và
`state_effects_vi` mô tả đúng hành vi mới (đóng segment, `outcome: partial`, không retry trong run, đợt kế
tiếp chạy bình thường, khác `source_blocked`). **W2 đã land; khớp với PC03-FIX3.**

## F3. Delta

1. **`collector-probe.md` ST-4** viết lại: `stop_reason = rate_limited`, đóng segment, **run ĐI TIẾP** với
   `outcome = partial`, **không** `blocked`, **không** retry trong đợt, đợt kế tiếp bình thường. Thêm một đoạn
   giải thích vì sao bản trước (*"kéo dài quá ngân sách ⇒ `blocked`"*) là **sai**: `blocked` đòi Owner gỡ tay,
   còn rate limit tự hết — và vì sao `rate_limited` không gộp vào `source_blocked` (X vẫn cho vào vs. không
   cho vào ⇒ hai màn hình khác nhau ở REQ-AC15).
2. **§5 enum `stop_reason` của probe** nay là `limit_reached | captcha | session_expired | source_blocked |
   rate_limited | source_layout_changed | operator_stop` — thêm `rate_limited`, thay `parser_degraded` bằng
   `source_layout_changed` (nợ còn lại từ FIX1), và ghi rõ `operator_stop` là giá trị RIÊNG của probe.
3. **Trường ghi nhận mới `rate_limited_at`** (UTC ms, NOT NULL khi `stop_reason = rate_limited`);
   `rate_limited_count` được mô tả rõ hơn. `parser_degraded_count` giữ tên (nó là trường ĐẾM của probe) kèm
   ghi chú rằng `stop_reason` tương ứng là `source_layout_changed`.
4. **`openapi.yaml`: `worker.report_stop` không còn dùng `GenericObject`.** Thêm component **`StopReport`** —
   schema ĐÓNG (`additionalProperties: false`) với enum tám giá trị lấy đúng từ ports.yaml, và một bảng trong
   `description` ánh xạ từng giá trị sang transition của `run.yaml` (T-RUN-02/09/16/24/25). Đây là thay đổi
   vượt mức tối thiểu nhưng nằm trong grant: một operation mà chính packet này yêu cầu "re-check the request
   enum" thì không nên tiếp tục khai bằng một object mở.
5. `ErrorEnvelope` sinh lại từ `errors.yaml` `b63eef7a…` — vẫn set-equal 28 mã (`RATE_LIMITED` đã có sẵn từ
   trước, không đổi số).

## F4. Evidence

`cd <scratch>/w4 && PYTHONDONTWRITEBYTECODE=1 python3 lint_pc05.py` · **exit 0** · **RESULT: PASS**
`SELF_VALIDATION`, 2026-09-06T19:34Z–19:35Z.

| Gate | Con số |
| --- | --- |
| EV-PC05-01 | openapi 3.1.0; 50 path; **54 == 54** op http; 0/31 internal bị lộ; **28 `$ref`** resolve (27 → 28 vì `StopReport`) |
| EV-PC05-02 | 8 fixture; 27 event khóa `operation`, 0 khóa cũ; actor-edge sạch 26/26; 23 body validate; ErrorEnvelope khớp 28 mã |
| EV-PC05-03 | 25 mã lỗi dùng, tất cả có trong `errors.yaml` |
| EV-PC05-04 | probe 22644 bytes; 8 tham số số học đủ value+unit+status+lý do |
| EV-PC05-06 (mới) | **5/5** body `worker.report_stop` trong fixture đã đóng băng validate ĐƯỢC theo `StopReport` |

**EV-PC05-06 là phép kiểm tôi thêm vì schema mới có thể làm hỏng fixture cũ.** Lần chạy đầu cho thấy hai khóa
mà fixture đang gửi nhưng schema chưa khai — `posts_observed_total` (fixture e) và
`posts_downloaded_not_ingested` (fixture c). Cả hai là quan sát hợp lệ của collector, nên tôi **mở rộng
`StopReport`** để nhận chúng, thay vì để một schema đóng mâu thuẫn với fixture đã đóng băng — và fixture nằm
ngoài MODIFY grant của packet này nên sửa chúng không phải lựa chọn.

Validate ngược lại: `contracts/ports.yaml` `87c95da4…`, `contracts/errors.yaml` `b63eef7a…`.
Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.
Giới hạn: vẫn **không có validator OpenAPI 3.1**; EV-01 là kiểm cấu trúc. Probe vẫn `NOT_RUN`.

## F5. Concerns

1. **Nợ FIX1 vừa được trả.** `parser_degraded` trong §5 của probe lẽ ra đã phải đổi ở FIX1 khi ST-7 chuyển
   sang `source_layout_changed`; nó sống sót hai vòng vì không gate nào đọc enum trong prose. Đây là loại lỗi
   mà chỉ người đọc mới bắt được.
2. **`StopReport` nay là nguồn sự thật hình dạng cho `worker.report_stop`, nhưng fixture chưa trỏ tới nó.**
   Năm body đã được kiểm thủ công ở EV-PC05-06 và đều pass; để gate tự chạy mỗi lần, các fixture cần thêm
   `validate_request_against: "contracts/http/openapi.yaml#/components/schemas/StopReport"` — **ngoài grant**,
   đề nghị gộp vào packet PC05 kế tiếp.
3. **Không CR mới.**

---

# ADDENDUM — PKT-PC05-FIX4

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC05-FIX4` (R5-02 / CR-PC09-01) |
| authority_id | `AUTH-COORD-PC05-FIX4` · lease `LEASE-PC05-e5` (**fencing 5**) |
| worker principal | `worker-W4` · status **DONE_WITH_CONCERNS** · claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-07T00:26Z / 2026-09-07T00:34Z |
| next actor | Coordinator |

**Tiếp nối.** Lượt trước bị cắt bởi rate limit **trước khi có write nào**; xác minh lại trước khi làm:
`acceptance/fixtures/e2e/` chưa tồn tại, không fixture nào đổi, không addendum nào ghi. Nguồn pinned khớp.

## H1. Changes

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `…/collection/i-run-now-while-active.json` | CREATE | ABSENT | `b2b809e1e3fb4ca5553d29ab4eeb3400cdf5af9056e3f96d73eaff1dc64a074e` | 7470 |
| `…/collection/j-dst-boundary-occurrences.json` | CREATE | ABSENT | `d709a547e557842d021e1b65d5a63f4c009e71e06578d3daae2dfff96b5983de` | 6372 |
| `…/collection/k-cancel-from-every-non-terminal.json` | CREATE | ABSENT | `4c7a46b976baac02a2fbe95064f5620c22ac8ae04b84a2fd1f36321a3cb06d76` | 12397 |
| `…/collection/l-storage-write-blocked-mid-run.json` | CREATE | ABSENT | `821668e010fb6ad77c5f013b67f944a602ac69164b7bc71148fee5d62e6299b5` | 9214 |
| `…/e2e/README.md` | CREATE | ABSENT | `74790ee8435791e5dbc360cf84a0737f660e2bebcbdb0749cdc1528a669d9ca8` | 6013 |
| `…/e2e/a-happy-path-schedule-to-delivered.json` | CREATE | ABSENT | `a925781ecf2d36e3cd02a3d666819bc5186c8d809e7865e51bac77d387678c00` | 30745 |
| `…/collection/README.md` | MODIFY | `7cea261f…` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 10833 → 12636 |
| `…/collection/a-feed-layout-changed.json` | MODIFY | `570d8c38…` | `2cf0fd00657c63883ae69d42a81d31cdb02d51d2e3d7c4c36a82dd5818506b70` | 13419 → 13611 |
| `…/collection/c-challenge-mid-batch.json` | MODIFY | `1011138e…` | `b4330c7e473779279ba545f0ecb6d9cd8f2a811beb0bae7310c62ff5dcf7e16b` | 12096 → 12528 |
| `…/collection/e-limit-reached-stop.json` | MODIFY | `d00983c5…` | `ce13e459e9e82755ab6b25f01b1e5e77e76f9a4f073ee7b69e2ab5eb9364c34e` | 7796 → 7892 |

Thư mục `acceptance/fixtures/e2e/` được tạo mới. `collection/README.md` → `0.4.0`.

## H2. Delta

1. **Bốn fixture SC33–SC36** trong `collection/`, dữ liệu lấy từ `contracts/state/run.yaml`
   §`scenario_definitions` và `acceptance/scenarios.yaml`. Cả bốn dùng `given.rows` / `expected.rows` **có
   cấu trúc** — nên `E0-15` trên thư mục này chuyển từ `NOT_APPLICABLE_FREEFORM` sang **PASS với 176 cột**.
   Đây chính là điều tôi nêu là concern ở FIX2 và FIX3; nay nó đã đóng cho phần mới.
2. **`e2e/` + fixture SC50** — đối chứng DƯƠNG đầu-cuối. 18 sự kiện gắn nhãn `_commit_boundary` B1…B11;
   `expected.rows` phủ **18 entity**; `expected.counts` 15 con số; `expected.equalities_vi` sáu đẳng thức bất
   biến (I02 checkpoint == MAX receipt sequence; I05 content_hash bất biến; I06 coverage nối liền;
   I07 first_announced duy nhất; I04/I16 attempt != accepted bằng 0; I09 outcome độc lập delivery).
   README nêu vì sao thư mục tồn tại: 48 scenario trước đều là nhánh lỗi hoặc một lát cắt, và **một bộ hợp
   đồng chỉ có ca âm không chứng minh được ca dương nào**.
3. **Năm con trỏ `validate_request_against` → `StopReport`** (nợ tự nêu ở FIX3 §F5 mục 2). Cả năm body
   validate; phép kiểm nay tự chạy trong gate thay vì làm tay.
4. **`c-challenge-mid-batch.json` seq=2** (theo yêu cầu Coordinator giữa gói): sự kiện cục bộ `operation: null`
   nay mang **`event_type: "local_observation"`**, đúng hình dạng R4-02. Gate actor-edge bỏ qua nó **theo quy
   tắc**, không phải vì đoán. `collection/README.md` khai khóa này trong bảng hình dạng.

## H3. Evidence — hai gate độc lập, số khớp nhau

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC05-07` | `<scratch>/w4/lint_pc05.py` | **PASS** — 13 fixture; **67 event**, khóa `operation`, 0 khóa cũ; actor-edge sạch **66/66** (event thứ 67 là `local_observation`); **29 body** validate (24 + 5 StopReport); ErrorEnvelope khớp 28 mã; wire 54/54, 28 `$ref`; **field-level: 473 cột, 37 annotation, 0 chưa resolve** | **0** |
| `EV-PC05-08` | `evidence/tools/e0_check.py` (công cụ PC09, đọc-only) | `E0-14-fixture-actor-edge` **434 checked, 0 violations**; `E0-15-fixture-field-existence` **1733 checked, 0 violations** — `dir collection files=12 columns_checked=176 annotations_skipped=25 → PASS`; `dir e2e files=1 columns_checked=297 annotations_skipped=12 → PASS`; `E0-03-fixture-schema` 28, 0 vi phạm | 0 |

**Hai con số PHẢI khớp và nay đã khớp.** Lần chạy đầu, gate của tôi báo `columns checked=0` trong khi e0_check
báo 473 — vì bộ đếm của tôi tìm `rows` bên trong từng event, còn `rows` nằm ở **top-level** của fixture. Tôi đã
sửa bộ đếm, rồi sửa tiếp cách đếm để **bỏ qua annotation `_` giống hệt e0_check**: 176 + 297 = **473 cột** và
25 + 12 = **37 annotation**, trùng khít. R4-01 đòi "the numbers in handoffs must match an independent run" —
một con số 0 do bộ đếm nhìn sai chỗ sẽ là đúng loại sai mà F-A1R3-01 đã phạt.

Toàn bộ e0_check: 19 check, **PASS 18 · FAIL 1**. FAIL duy nhất là `E0-07-id-refs` với **2 vi phạm**:
`SC54` được trích trong `evidence/handoffs/PC00-handoff.md` và `PC01-handoff.md` nhưng chưa có trong
`acceptance/scenarios.yaml`. **Không thuộc file nào của tôi**; thuộc W1/W2.

`SELF_VALIDATION` (E0), 2026-09-07T00:32Z–00:33Z. Nguồn pinned khớp hai đầu: SRC-PLAN `f65bb046…`,
SRC-SPEC `d35e1f2d…`.

## H4. Concerns

1. **Tám fixture gốc (a)–(h) vẫn ở dạng câu văn** và không đóng góp cột nào cho gate; 176 cột của thư mục
   `collection/` đến từ bốn file mới. Chuyển tám file cũ sang `rows` là **thay đổi thiết kế**, không phải sửa
   lỗi, nên tôi không tự làm.
2. **Fixture e2e dùng `report.report_build_id` và `report.abort_reason`.** Gate `E0-15` PASS ⇒ hai cột đã có
   trong `entities.yaml` sau PC02-FIX3. Điều này cũng đóng phần còn lại của F-A1R2-01 về phía tôi.
3. **SC50 chứng minh HÌNH DẠNG DỮ LIỆU, không chứng minh chất lượng.** Một đợt chạy thật đầu-cuối là E3
   (SP1 + triển khai); giá trị khối "hướng đang nổi" là E4 và cần 3–4 kỳ thật (REQ-A4). Số hàng trong fixture
   là tối thiểu (2 post / 2 work / 2 analysis) — đủ để mọi đẳng thức có nghĩa, không đại diện cho tải thật.
4. **Không dùng SC45+.** Bốn fixture mới dùng đúng SC33–SC36; e2e dùng SC50.
5. **Không CR mới.**

---

# ADDENDUM — PKT-PC05-FIX5

| Trường | Giá trị |
| --- | --- |
| packet_id | `PKT-PC05-FIX5` (E0-04c, run `E0-20260907T014517Z`, phát hiện (b)) |
| authority_id | `AUTH-COORD-PC05-FIX5` · lease `LEASE-PC05-e6` (**fencing 6**) |
| worker principal | `worker-W4` · status **DONE_WITH_CONCERNS** · claim `DRAFT_FOR_REVIEW` |
| started / lease_released (UTC) | 2026-09-07T01:48Z / 2026-09-07T01:56Z |
| next actor | Coordinator |

## J1. Changes (MODIFY, baseline = hash sau FIX4)

| Path | Before | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `contracts/http/openapi.yaml` | `258fce24…` | `a7f284b97816a4a37a53256bdea00b0affa26bd18d152faf4f80dec7223c8499` | 227676 → 227691 |
| `…/collection/l-storage-write-blocked-mid-run.json` | `821668e0…` | `7f5f751e9f23ea48ddb0623ce38a168967e621a014f2ca954b5852add193aeaf` | 9214 → 9225 |

`worker-assignment.schema.json` (`14efde6f…`), `ingest-receipt.schema.json` (`ff5232f4…`),
`collector-probe.md` (`03e88010…`) và 11 fixture còn lại **không đổi** — trong grant, không có token cần sửa.
`openapi.yaml` giữ `0.3.0` (nội dung sinh lại, không đổi hợp đồng).

## J2. Delta

| Token cũ | Sửa thành | Vì sao sai |
| --- | --- | --- |
| `post.mark_source_deleted` (openapi) | **biến mất** | **Đây là (b) của packet.** Một operation ĐÃ BỊ BÁC BỎ (PKT-PC01-FIX1), nay lại xuất hiện dưới dạng token có hình dạng cột. Cơ chế được duyệt là trường item `source_deleted_observed_at` đi qua `ingest.submit_batch`. Câu này được SINH RA từ `ports.yaml.request_summary_vi`; W2 đã scrub nó khỏi `ports.yaml` (`grep -c` = **0** tại `93ba1598…`), nên **sinh lại openapi từ bản ports.yaml hiện hành là đủ** — tôi không viết tay đè lên văn bản do PC01 sở hữu. |
| `checkpoint.acked_through` (openapi) | `checkpoint.acked_through_ingest_sequence` | Tên cột bị CẮT CỤT trong câu oracle của `ingest.commit_checkpoint`. Một oracle trỏ tới cột không tồn tại thì không chạy được. |
| `storage.write_blocked` (fixture (l), tiêu đề) | `` `storage.health = write_blocked` `` | `write_blocked` là giá trị của kênh `storage.health`, không phải một cột. |

15 token còn lại mà gate liệt kê ban đầu đều thuộc **bốn lớp ngoại lệ** của
`conventions.prose_token_rule_vi`: khóa YAML trong chính bộ hợp đồng (`info.x-contract`, `given.rows`,
`expected.rows`, `expected.counts`, `expected.equalities_vi`, `limits.*`), trường payload/response định nghĩa
tại chỗ (`search_config.*`, `counts.*`, `receipt.warnings`, `details_safe.violation_kind`,
`confirmation.acknowledged`, `author.handle`, `author.id`), và ngoại lệ có tên `storage.health`. Chúng được
khai vào danh sách ngoại lệ của gate **kèm căn cứ từng mục**, không bị sửa.

## J3. Evidence

| ID | Command | Kết quả | Exit |
| --- | --- | --- | --- |
| `EV-PC05-09` | `<scratch>/w4/prose_token_gate_w4.py` | **PASS** — PC05 (19 file: openapi + 2 schema + probe + 12 fixture collection + 2 file e2e): **195** token giải thành operation, **50** thành `entity.column`, **71** ngoại lệ có căn cứ, **UNRESOLVED = 0**; mã lỗi lạ trong prose = **0** | **0** |
| `EV-PC05-10` | `<scratch>/w3/prose_token_gate.py` (gate của W3, đọc-only) trên cùng 19 file | **195 / 50 — TRÙNG KHÍT**. 71 token W3 báo "không giải được" đúng bằng 71 ngoại lệ của tôi, vì bản W3 chưa hiện thực bốn lớp ngoại lệ của ruling FIX7 | 1 (do W3 chưa có lớp ngoại lệ) |
| `EV-PC05-11` | `<scratch>/w4/lint_pc05.py` | **PASS** — 13 fixture; 67 event; actor-edge 66/66; **29 body** validate; field-level **473 cột / 37 annotation / 0 chưa resolve**; wire 54/54 | 0 |
| `EV-PC05-12` | `evidence/tools/e0_check.py` | **22 check, PASS 22, FAIL 0, violations 0** | 0 |

Negative self-test của gate (kế thừa từ W3): hai token đột biến đều BỊ BẮT ⇒ `UNRESOLVED = 0` không phải do
gate mù. Nguồn phân giải đúng bản packet chỉ định: `ports.yaml 93ba1598…`, `entities.yaml c2ceeafd…`.
Nguồn pinned khớp: SRC-PLAN `f65bb046…`, SRC-SPEC `d35e1f2d…`.

## J4. Concerns

1. **Card-pinned hashes.** `contracts/http/openapi.yaml` được pin trong **15/18** card của PC10; hash nay đổi.
   Cùng với các file PC03 ở addendum PKT-PC03-FIX5, **cả 18 card đều có ít nhất một pin cũ**. `CR-PC10-01` đã
   yêu cầu re-pin sau `FC-W4`; đợt này khiến việc đó thành bắt buộc.
2. **`openapi.yaml` là file SINH RA.** Nó thừa hưởng văn xuôi từ `ports.yaml`, nên một token hỏng ở PC01 sẽ
   tự động xuất hiện ở đây một vòng sau. Đó chính xác là điều đã xảy ra với `post.mark_source_deleted`: PC01
   sửa ở FIX-trước, nhưng openapi của tôi vẫn giữ bản cũ cho tới lần sinh lại này. **Đề nghị:** mỗi lần
   `ports.yaml` đổi, openapi nên được sinh lại — hoặc gate prose-token nên chạy trên openapi ngay sau mỗi
   packet PC01. Tôi không tự đặt quy trình đó; nêu để Coordinator quyết.
3. **Không CR mới.**
