---
handoff_id: TC-canonical-identity-merge-handoff
packet_id: PKT-TC-CANONICAL-IDENTITY-MERGE
card_ref: agent-tasks/TC-canonical-identity-merge.md
worker_principal: worker-WM
authority_id: AUTH-COORD-TC-IDENTITY
parent_authority: AUTH-OWNER-20260907-03
lease_id: LEASE-TC-IDENTITY-e1
decision_refs: [OD-20260907-01, OD-20260907-02, B06, B15, ADR-0009, ADR-0011]
invariant_refs: [I03, I07, I08, I17]
scenario_refs: [SC07, SC09, SC23, SC29, SC30, SC49]
evidence_manifest_id: EVM-TC-canonical-identity-merge
next_actor: Coordinator
lease_released_at: 2026-09-07T10:30Z
---

# HANDOFF — TC-canonical-identity-merge (canonical identity, alias, merge có audit trail)

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| `card_id` | `TC-canonical-identity-merge` (M2, cổng G5) |
| `worker_principal` | `worker-WM` |
| `authority_id` | `AUTH-COORD-TC-IDENTITY` (parent `AUTH-OWNER-20260907-03`, bản ghi `OD-20260907-02`) |
| `lease_id` | `LEASE-TC-IDENTITY-e1` (exclusive, message-tracked; không có guard ở mức OS) |
| **`status`** | **`DONE_WITH_CONCERNS`** |
| `completion_claim` | `IMPLEMENTATION_VERIFIED` **chỉ cho phạm vi card này** và **chỉ với** hai ngoại lệ đã ghi bằng `xfail(strict=True)` ở §6 (CR-02, CR-03) |
| `review_type` | `SELF_VALIDATION` — không có audit độc lập nào được chạy |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T10:30Z |

**Vì sao `DONE_WITH_CONCERNS` chứ không phải `DONE`.** Ba lý do, không lý do nào là "code chưa
xong": (a) hai oracle của fixture mâu thuẫn với hợp đồng mới hơn và tôi **không** sửa fixture —
chúng nằm lại dưới dạng test `xfail(strict=True)` (CR-02, CR-03); (b) năm bảng mà merge move-set
bắt buộc phải ghi thuộc module khác nhưng phải được tạo trong migration của card này để
`TXN-identity-merge` chạy được và kiểm được (CR-04); (c) một test có sẵn của Giai đoạn 0
(`server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0`) đang FAIL trong lần chạy
toàn bộ — nguyên nhân nằm ở card storage/readiness, không ở card này (§5.4).

**Vì sao không phải `STALE_BASELINE`.** Toàn bộ 28 dòng pin ở §0 của card được tính lại ngay
trước handoff và **khớp cả 28**. Ghi chú trung thực: ở thời điểm tôi bắt đầu, ba dòng
(`ADR-0011`, `precode/baseline.json`, `precode/decision-register.md`) **lệch**; card đã được
re-pin trong lúc phiên chạy (các giá trị mới đúng bằng nội dung repo hiện tại, do
`OD-20260907-02` và ruling ADR-0011). Tôi không sửa card và không sửa ba file đó.

## 2. Changes — mọi file đã tạo hoặc sửa

**9 file `CREATE`, 1 file `MODIFY` (một khối include có giới hạn rõ).**

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/app/identity/__init__.py` | CREATE | ABSENT | `ad92e9d910fba1005d6acebff87e42ecd1619c4f1efd0fd6f99d8db7ca28d918` | 534 |
| `server/app/identity/normalization.py` | CREATE | ABSENT | `caab1700cd1312214fe4b6e45af041552a3c5233ade9690f8442ebb5e1e7d378` | 9725 |
| `server/app/identity/repository.py` | CREATE | ABSENT | `c49d4e34e9068c9ee06ca52e5059aff8a54f9d5008e4457b32385d9d26b4fdd7` | 27825 |
| `server/app/identity/service.py` | CREATE | ABSENT | `ff2562efdf3d4543b62f5835deb9fe0575d39c8db5455b620c91824222ab3a12` | 58971 |
| `server/app/identity/router.py` | CREATE | ABSENT | `e7fc19c4dbf935c17960e26f77bc984b8fdee0057cbcaf5511b1c3f535bf694a` | 9142 |
| `server/migrations/versions/0002_base_entities.py` | CREATE | ABSENT | `29d5b1bf3a60fd5a11ccbc55dba75513c9d39d9935bfdd3e7afba419ecafeb74` | 10391 |
| `server/migrations/versions/0003_tc_canonical_identity_merge.py` | CREATE | ABSENT | `7edff04702c2b29a90bde2298ac5029fdc16a0069f65ee479365bc3f9ede2779` | 18448 |
| `server/migrations/versions/0004_merge_phase1_heads.py` | CREATE | ABSENT | `4f98dbe9584acad7f6d45ae9d5db4766092b738acef988c01f857e5f7c5b2d3c` | 2444 |
| `tests/contract/test_identity_normalization.py` | CREATE | ABSENT | `0bc264a7e3929fa97b44e9c7bf05971de7f4c2509087bcc150b6af3ecad580c7` | 10898 |
| `tests/integration/test_identity_merge_audit.py` | CREATE | ABSENT | `628976c7abe4d9ebf19836fa33ae53d754394af722e59290b3c4f62561c0776e` | 63772 |
| `server/app/main.py` | MODIFY | *(file dùng chung, đã bị ba card khác sửa trong cùng phiên)* | `adfcde38ab8191ed54ad088a8c6d33550a009a2b06026371ce3838867db0bd44` | 8014 |
| `evidence/runs/TC-canonical-identity-merge-E1-20260907T102504Z.json` | CREATE | ABSENT | *(manifest, §7)* | 12764 |
| `evidence/handoffs/TC-canonical-identity-merge-handoff.md` | CREATE | ABSENT | *(chính file này)* | — |

**Ba ghi chú về write set.**

1. `server/app/identity/__init__.py` **không** có trong bảng §3 của card. Nó là điều kiện để
   bốn file kia thành một package `server.app.identity` (cây Python của repo dùng `__init__.py`
   tường minh, `pyproject.toml` mục `mypy`). Tôi ghi lại thay vì thêm im lặng.
2. `server/app/main.py` được sửa đúng **một khối** `# --- BEGIN include: TC-canonical-identity-merge`
   … `# --- END include`, theo quy tắc 2 của dispatch. Không dòng nào khác bị chạm.
3. `server/migrations/versions/0004_merge_phase1_heads.py` được viết **theo chỉ đạo trực tiếp của
   Coordinator** (thông điệp 2026-09-07 ~10:20Z, mục 2). Nó là hiện vật điều phối, không thuộc
   riêng card nào, và **không tạo schema**.

## 3. Source baseline đã dựa vào

| Ref | Path | SHA-256 | Kiểm |
| --- | --- | --- | --- |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp đầu phiên **và** trước handoff |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp đầu phiên **và** trước handoff |

28/28 dòng pin ở card §0 khớp trước handoff (kiểm bằng script đọc chính bảng của card, không gõ
lại hash bằng tay). Ngoài read set của §0 tôi còn đọc — và **phụ thuộc vào** —
`contracts/reporting/time-and-tags.md` (sha256
`70f4bc57a0fa2733d92136194eb4d563fa5d9145726141ee30493fe3a2b1a66c`) vì §8.3 của nó **đóng**
`CR-PC02-06`, và `acceptance/scenarios.yaml` (sha256
`09099fad2fa0a5ed077e2d430c52e0a857aa212b4845d7c71120f91787b090d3`, cố ý không pin ở §0).

## 4. Cái gì đã được hiện thực

**Sáu operation, đặt tên đúng bằng operation id của `contracts/ports.yaml`** — chữ ký đầy đủ nằm
trong docstring của `server/app/identity/service.py` (tham số đầu là executor, phần còn lại
keyword-only):

| Operation | Hàm | Ghi chú |
| --- | --- | --- |
| `identity.resolve_target` | `resolve_target` | read-only đúng nghĩa: `|W| ≥ 2` ⇒ `IDENTITY_CONFLICT`, **không** ghi quarantine |
| `identity.record_alias` | `record_alias` | idempotent theo cặp alias; `work_id=None` là nhánh `|W| = 0` của identity.md §3 |
| `identity.quarantine_conflict` | `quarantine_conflict` | idempotent bằng fingerprint **tính lại** từ nội dung đã lưu (không có cột) |
| `identity.merge_works` | `merge_works` | `TXN-identity-merge`, một BEGIN…COMMIT, commit point ghi trong docstring |
| `identity.resolve_conflict` | `resolve_conflict` | đường merge **duy nhất** ra khỏi conflict; `performed_by = owner_manual` |
| `work.get_detail` | `get_detail` | theo con trỏ `merged` về work còn sống (I03d) |

**Chuẩn hóa** (`normalization.py`): DOI §2.1 (7 loại tiền tố, percent-decode **đúng một lần**,
cắt dấu câu cuối, hạ chữ thường, regex), arXiv §2.2 (kiểu mới + kiểu cũ, `.pdf`, query/fragment,
tách `vN`, archive thường / subject-class HOA), `openalex`/`pmid`/`landing_url` §2.3. Tất cả là
hàm thuần túy, không mạng, và có test idempotent + tất định.

**Migration.** `0002_base_entities` (owner, work, post, post_work — dùng chung) và
`0003_tc_canonical_identity_merge` (identity_alias, identity_conflict, identity_merge_audit,
work_version + năm bảng của move-set). Hai quyết định đáng nêu:

* `target_key` là **STORED generated column** (`entities.yaml` cho phép). Hệ quả: move-set không
  thể lệch — chuyển `target_work_id` là chuyển `target_key`, không có trạng thái nửa vời.
* Mọi cột `*_merge_id` trỏ `identity_merge_audit` là **`DEFERRABLE INITIALLY DEFERRED`**. Đó là
  cách biến "không có merge nào không có audit" thành ràng buộc của database: các con trỏ được
  ghi trước, hàng audit là commit point, và ràng buộc được kiểm **tại COMMIT**.

**`first_announced` sau merge** được hiện thực theo `contracts/reporting/time-and-tags.md` §8.3
(đóng `CR-PC02-06`, `ACCEPTED` bởi `OD-20260907-01`): work thắng kế thừa first-announcement
**sớm nhất**, hàng thua giữ lại làm bằng chứng với `superseded_by_merge_id`, và
`moved_counts.first_announced` ∈ {0, 1, 2} theo đúng bảng §8.3. Hook chạy **trong cùng
transaction** merge. Card §10 `SG-01` (để `null`) đã được thay bằng chỉ đạo của Coordinator và
bởi chính §8.3; xem CR-02.

**Default deny.** `ALLOWED_CALLERS` trong `service.py` được **so trực tiếp với
`contracts/modules.yaml.allowed_edges`** bằng một test; caller ngoài registry nhận
`FORBIDDEN_EDGE` (403), không phải `UNAUTHORIZED` (ruling R5-01). Không cạnh nào trong 36
`forbidden_edges` chạm `MOD-identity-service`, nên `SG-DENY` với card này quy về đúng nghĩa vụ
trên.

## 5. Evidence records — tất cả `SELF_VALIDATION`

Mọi lệnh chạy tại `/mnt/virtual/repo/xcrawl` với `PYTHONDONTWRITEBYTECODE=1`, không chạm mạng.

### EV-TC-IDENTITY-01 — E1 contract test (chuẩn hóa)

* command: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/contract/test_identity_normalization.py -p no:cacheprovider -p no:warnings`
* started 2026-09-07T10:24:54Z · ended 2026-09-07T10:24:55Z · **exit 0**
* observed: **75 passed, 0 failed** · oracle: bảng thuật toán của `identity.md` §2 +
  `normalization_cases` của fixture (h) + các cặp raw/normalized của fixture (a), (g)
* status: **PASS**

### EV-TC-IDENTITY-02 — E1/E2 integration test (TXN-identity-merge, audit, I17)

* command: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/integration/test_identity_merge_audit.py -p no:cacheprovider -p no:warnings`
* started 2026-09-07T10:24:55Z · ended 2026-09-07T10:25:04Z · **exit 0**
* observed: **39 passed, 2 xfailed(strict), 0 failed**
* oracle đo được (không phải đọc log): `COUNT(work)` không đổi (2) nhưng chỉ còn 1 `active`;
  alias map trỏ winner; `COUNT(identity_merge_audit)` +1; tập
  `{(id, target_key_at_save, content_hash)}` của `saved_snapshot` **trước = sau**;
  `sha256(JCS(payload)) == content_hash`; fixture (c) 0 merge / 1 conflict `open` / 0 alias
  openalex; fixture (h) 6 biến thể → 1 work + 1 alias + 6 nguồn dẫn; fixture (i)
  `moved_counts.first_announced = 2` và đúng 1 hàng ledger có hiệu lực cho winner.
* E2 (fault injection): lỗi tại điểm ghi `identity_merge_audit` ⇒ rollback toàn bộ (2 work vẫn
  `active`, alias/post_work chưa chuyển, snapshot nguyên vẹn). **PASS**
* status: **PASS**

### EV-TC-IDENTITY-03 — cổng chất lượng

* `python -m ruff check <write set>` → exit 0 · `ruff format --check` → exit 0 (9 file)
* `python -m mypy` (`--strict`, `files = server/app`) → exit 0, "no issues found in 24 source files"
* status: **PASS**

### EV-TC-IDENTITY-04 — chuỗi migration một head

* `ScriptDirectory.get_heads()` → `['0004_merge_phase1_heads']` (1 head)
* `alembic upgrade head` trên DB rỗng → tạo đủ 17 bảng của bốn card Giai đoạn 1, exit 0
* status: **PASS** (được khẳng định lại bằng hai test trong bộ integration)

### EV-TC-IDENTITY-05 — lần chạy toàn bộ

* command: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -p no:warnings`
* started 2026-09-07T10:25:04Z · ended 2026-09-07T10:25:39Z · **exit 1**
* observed: **261 passed, 1 failed, 4 xfailed**
* FAIL duy nhất: `server/tests/test_smoke.py::test_readiness_is_not_routed_in_phase_0` —
  `GET /v1/health/readiness` trả **401** trong khi test của Giai đoạn 0 kỳ vọng **404**. Route đó
  do `TC-storage-write-blocked-readiness` đăng ký và 401 do lớp auth; **không** liên quan tới
  card này (identity chỉ thêm `/v1/works/{work_id}` và
  `/v1/identity/conflicts/{id}/resolve`). Tôi **không** sửa vì cả hai file nằm ngoài write set.
* status: **FAIL (ngoài phạm vi card này)** — chuyển Coordinator.

### EV-TC-IDENTITY-06 — chữ ký port đối với card ingest

* `inspect.signature(service.resolve_target).bind(...)` với đúng call site của
  `server/app/ingest/service.py` (`resolve_target(connection, owner_id=…, identifiers=[…],
  caller_module="MOD-ingest-service")`) → **bind OK**; `service.Identifier` và `service.IdScheme`
  tồn tại đúng như `_identifiers_from_links` giả định.
* Lần chạy toàn bộ (EV-05) không còn lỗi nào liên quan tới identity ⇒ khớp signature mà
  Coordinator báo là đã tự khỏi (nó chỉ quan sát được khi `service.py` chưa tồn tại).
* status: **PASS**, và được khóa lại bằng test `test_ingest_call_site_binds_to_resolve_target`.

## 6. Change requests (không sửa hợp đồng, không sửa fixture)

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-TC-IDENTITY-01` | PC10 / Coordinator | Card §8 viết "Fixture `h`: **5 post** → 1 target, provenance liệt kê đủ 5". Fixture (h) mang **6** item (5 post độc lập + 1 post mở đầu thread của tác giả) và `expected.counts` khai `post = 6`, `post_work = 6`, `work_detail_source_posts = 6`. Code và test theo **fixture**; xin sửa văn xuôi của card. |
| `CR-TC-IDENTITY-02` | PC02 / PC04 | Fixture (a) khai `moved_counts.first_announced = null`; `contracts/reporting/time-and-tags.md` §8.3 (ACCEPTED, đóng `CR-PC02-06`) nói `null` chỉ là chỗ giữ tạm và giá trị hợp lệ nay là **số** (`0` khi không bên nào có hàng). Hiện thực theo §8.3; kỳ vọng nguyên văn của fixture được giữ bằng `xfail(strict=True)`. Xin cập nhật fixture (a). |
| `CR-TC-IDENTITY-03` | Coordinator | `preserved_counts.published_report_item` không đo được: `report` và `report_item` thuộc card báo cáo, chưa tồn tại ở M1. Fixture (i) kỳ vọng `2` → `xfail(strict=True)`. Khi card báo cáo chạy, bỏ marker và chạy lại. |
| `CR-TC-IDENTITY-04` | Coordinator | `TXN-identity-merge` bắt buộc ghi `work_label`, `analysis`, `saved_item` (và đọc `saved_snapshot`), cộng `first_announced_ledger` theo §8.3 — **năm bảng thuộc `MOD-analysis-service` / `MOD-saved-service` / `MOD-report-service`**. Không có chúng thì transaction không chạy và không kiểm được, nên migration của card này tạo chúng theo hình dạng `entities.yaml`. Xin phân định chủ sở hữu **trước khi** ba card kia chạy, để không có bảng nào được tạo hai lần. |
| `CR-TC-IDENTITY-05` | PC10 / PC02 | Mâu thuẫn mã lỗi khi vượt `identity_merge_max_moved_rows`: card §7 nói `CONFLICT`; `contracts/errors.yaml` (`IDENTITY_CONFLICT.forbidden_vi`) và `openapi.yaml` nói phải **thành `identity_conflict`**. Nhưng `identity_conflict.conflict_type` **không có** giá trị nào diễn tả "quá nhiều hàng". Hiện thực theo card §7 (`CONFLICT`, **không ghi gì**); tôi không tự chế enum mới. |
| `CR-TC-IDENTITY-06` | PC01 / PC10 | `work.get_detail`: `openapi.yaml` ghim response 200 vào `target.schema.json` (hai nhánh đều `additionalProperties: false`), trong khi `ports.yaml` mô tả read model rộng hơn (summary, nhãn, tag khớp, post dẫn, lịch sử phân tích). Router trả **đúng target object hợp lệ schema**; phần còn lại có sẵn trong `WorkDetail` nhưng chưa có wire schema. Xin một schema đóng. |
| `CR-TC-IDENTITY-07` | PC02 | `ports.yaml` đòi idempotency theo `request_id` cho `identity.resolve_conflict` và theo `conflict_fingerprint` cho `identity.quarantine_conflict`, nhưng `entities.yaml.identity_conflict` **không có cột nào** để lưu hai khóa đó. Hiện thực: fingerprint **tính lại** từ nội dung đã lưu; `resolve_conflict` idempotent theo **trạng thái** (quyết định khác trên conflict đã giải ⇒ `IDEMPOTENCY_CONFLICT`). Yêu cầu thực chất ("không merge hai lần") được giữ; xin quyết định có thêm cột hay không. |
| `CR-TC-IDENTITY-08` | PC02 | Move-set không nêu quy tắc va chạm cho `work_label` (`ux_work_label_owner_target_label_gen`), trong khi `analysis` và `saved_item` đều có. Hiện thực: hàng va chạm **ở lại** work thua (không xóa, không ép qua index) và không được tính vào `moved_counts`. Xin khóa quy tắc. |
| `CR-TC-IDENTITY-09` | PC10 | Card §7 gọi trường envelope là `retry_after`; `contracts/errors.yaml` gọi là `retry_after_ms`. Code theo hợp đồng. |
| `CR-TC-IDENTITY-10` | PC09 | Fixture (a) kỳ vọng alias `openalex` **được tạo trong** `TXN-identity-merge` (`_created_in_transaction`), nhưng `merge_move_set` của `entities.yaml` không liệt kê việc tạo alias. Hiện thực theo fixture (định danh đã chứng minh merge trở thành alias của winner, `confidence = confirmed_by_two_sources`); xin bổ sung vào move-set để hai nguồn nói cùng một điều. |

Ngoài ra, hai việc thuộc Coordinator, không phải CR:

* `evidence/index.json` **chưa** đăng ký run này (file thuộc PC09, ngoài write set của mọi card
  Giai đoạn 1; hai card đã hoàn thành trước cũng chưa đăng ký).
* Mẫu `unresolved_issue_refs` của `evidence/manifest.schema.json` chỉ nhận `CR-PC<nn>-<nn>`, nên
  mười CR ở trên **không khai được** trong manifest (đã ghi trong `uncertainty_vi`; liên quan
  `CR-PC09-02`).

## 7. Evidence manifest

* Đường dẫn: `evidence/runs/TC-canonical-identity-merge-E1-20260907T102504Z.json` (12 764 byte)
* `evidence_id`: `EV-E1-01-tc-canonical-identity-merge` · `result`: `PASS` · `review_type`:
  `SELF_VALIDATION` · `evidence_level`: `E1`
* Validate: `jsonschema.Draft202012Validator` với `evidence/manifest.schema.json` → **0 lỗi**
* `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`;
  `contract_hashes` chép nguyên văn 28 dòng pin của card §0 (cộng `time-and-tags.md`,
  `scenarios.yaml`, `manifest.schema.json`).
* Vị trí khác với `evidence/runs/TC-canonical-identity-merge/manifest.json` mà card §13 đề nghị
  (PROVISIONAL): dispatch của Coordinator chỉ định `evidence/runs/<card>-E1-<UTC>.json`, và hai
  card Giai đoạn 1 trước đã dùng đúng dạng đó.

## 8. Checklist của card

| Mục | Trạng thái | Ở đâu |
| --- | --- | --- |
| §3 `server/app/identity/service.py` | DONE | resolve/alias/quarantine/merge/resolve_conflict/get_detail |
| §3 `server/app/identity/normalization.py` | DONE | DOI, arXiv (base + version), 3 scheme alias |
| §3 `server/app/identity/router.py` | DONE | `POST /v1/identity/conflicts/{id}/resolve`, `GET /v1/works/{work_id}` |
| §3 `server/app/identity/repository.py` | DONE | mọi SQL của module, không mở transaction |
| §3 `tests/contract/test_identity_normalization.py` | DONE | 75 test |
| §3 `tests/integration/test_identity_merge_audit.py` | DONE | 39 test + 2 xfail |
| §4 produces (6 operation) | DONE | §4 bảng trên |
| §4 consumes (`research.fetch_work_metadata`, `storage.get_health`) | NOT_DONE (cố ý) | Không gọi: bằng chứng metadata đến **qua tham số** `linking_evidence`; card không có nghĩa vụ tự lấy metadata, và `storage.get_health` là cửa của card storage |
| §6 `TXN-identity-merge` một commit | DONE | `merge_works`, commit point ghi trong docstring |
| §6 race/replay/forbidden effects | DONE | CAS đọc lại, replay idempotent, v1/v2 hai `work_version` |
| §7 nghĩa vụ mã lỗi | DONE (1 khác biệt) | xem CR-05 |
| §8 hai lệnh pytest | DONE | EV-01, EV-02 |
| §8 `evidence/tools/e0_check.py` | NOT_RUN | card ghi rõ PC10 không chạy E0 |
| §13 evidence manifest | DONE | §7 |
| SC49 / default deny | DONE | test so `ALLOWED_CALLERS` với `modules.yaml` |

## 9. Cái card này **không** chứng minh

* Không chứng minh identity đúng với dữ liệu thật: mọi bằng chứng liên kết đến từ fixture, không
  từ arXiv/OpenAlex thật (E3 `NOT_RUN`).
* Không chứng minh "0 trùng" ở mức khoa học — chỉ trong phạm vi canonical identity **đã biết**
  (B15). Hai công trình giống nhau mà không nguồn nào nối định danh vẫn là hai work.
* Không chứng minh ngưỡng `identity_merge_max_moved_rows = 100000` là đúng: nó vẫn PROVISIONAL
  (`CR-PC02-05`); chỉ nhánh mã được kiểm, không dựng 100 000 hàng.
* Không chứng minh phiên owner thật: authenticator trong test là stub; TLS, cookie `Secure`,
  CSRF thật thuộc `TC-owner-auth-session`.
* Không có audit độc lập. Nhãn `IMPLEMENTATION_VERIFIED` cần Coordinator/Auditor xác nhận —
  đây là `SELF_VALIDATION`.

## 10. Next actor

`Coordinator`. Ba việc cần quyết trước khi card khác chạy: (1) chủ sở hữu năm bảng của move-set
(CR-04); (2) hai fixture cần cập nhật (CR-02, CR-03) — **không** ai được sửa để test xanh mà
không có quyết định; (3) FAIL của `test_readiness_is_not_routed_in_phase_0` thuộc card
storage/readiness.

`lease_released_at`: 2026-09-07T10:30Z. Sau dòng này tôi không ghi thêm file nào.

---

# ADDENDUM — PKT-TC-IDENTITY-FIX1 (F-A3R1-01, -04, -09, -14; phối hợp -05)

## A1. Định danh

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-IDENTITY-FIX1` · authority `AUTH-COORD-TC-IDENTITY-FIX1` (parent `AUTH-OWNER-20260907-03`) · lease `LEASE-TC-IDENTITY-e2` (fencing 2), hết hạn 2026-09-08T16:00Z |
| worker principal | `worker-WM` · mode: code mutation dưới lease theo `OD-20260907-02` mục 3 |
| **status** | **`DONE`** · completion_claim `IMPLEMENTATION_VERIFIED` cho phạm vi card, vẫn kèm hai `xfail(strict)` ở §6 |
| ruling nguồn | `FIX-A3R1-rulings.md` hàng `F-A3R1-01`, `-04`, `-09`, `-14`; phối hợp `-05` |
| next actor | `Coordinator` (rồi WA cho nửa còn lại của F-01, WI cho F-05) · `lease_released_at` 2026-09-07T11:15Z |

`date -u` bắt đầu 2026-09-07T11:00Z, kết thúc 2026-09-07T11:15Z. Nguồn khớp baseline:
plan `f65bb046…40`, spec `d35e1f2d…6e` (kiểm lại ngay trước addendum này).

## A2. Delta

| Path | Op | After (sha256) | Bytes |
| --- | --- | --- | --- |
| `server/migrations/versions/0002_base_entities.py` | MODIFY | `e6690f6a70743d625ed65bcad740214a5ed3aedf21535d6ab60d54f1be2ad109` | 12954 |
| `server/migrations/versions/0002b_shared_move_set_tables.py` | CREATE | `9ec48efdff1f702f1a3c3fe926238156aff639a359e9d8ce0a600406fd85ffaa` | 13354 |
| `server/migrations/versions/0003_tc_canonical_identity_merge.py` | MODIFY | `be55f9befa1c28beb2756693f1687c64c87ce1dc3daa5b84bad4a4ac484c4903` | 10994 |
| `tests/integration/test_identity_merge_audit.py` | MODIFY | `0c1e6f4a49965644a193151a7c94ca03f9d0571741e59e35ed15fd73a089edc4` | 67446 |
| `evidence/runs/TC-canonical-identity-merge-E1-20260907T111124Z.json` | CREATE | *(manifest FIX1, §A7)* | 13380 |

Không đổi: `0004_merge_phase1_heads.py`, cả năm file `server/app/identity/*`,
`tests/contract/test_identity_normalization.py`, `server/app/main.py`. **Không** file nào của
card khác bị chạm.

## A3. F-A3R1-01 — `owner` chỉ còn một định nghĩa

`0002_base_entities` nay là `CREATE TABLE owner` **duy nhất** (bỏ `IF NOT EXISTS`), mang trọn bộ
`ENT-owner` sau `AMD-ENT-owner-01`: `CHECK (singleton_guard = 1)` + `UNIQUE`,
`CHECK (length(display_name) BETWEEN 1 AND 120)`, `created_at` GLOB mili-giây (đó là `F-A3R1-14`),
và **bốn cột credential**: `password_hash TEXT NULL`, `password_updated_at TEXT NULL`,
`failed_login_count INTEGER NOT NULL DEFAULT 0 CHECK (>= 0)`, `locked_until TEXT NULL`, mỗi cột
timestamp kèm CHECK GLOB. Thêm một CHECK không có trong hợp đồng nhưng suy ra trực tiếp từ nó:
`(password_hash IS NULL) = (password_updated_at IS NULL)` — `entities.yaml` nói "NULL khi
`password_hash` còn NULL", nên hai cột phải rỗng cùng lúc.

**Nguồn:** `contracts/data/entities.yaml` **0.2.0**, sha256
`f5ea0511f885159fedbb48bf939a9bd1436707f12007403c57808c9f5026c77e`, `ENT-owner.amendment_refs =
[AMD-ENT-owner-01]`. Tôi đã poll theo đúng chỉ dẫn của packet: ở lần đọc đầu (11:00Z) bốn cột
**chưa** có; tôi làm F-04 trước, poll lại (11:07Z) thì đã có; addendum `PKT-PC02-FIX12` của
`worker-W3n` xuất hiện trong `evidence/handoffs/PC02-handoff.md` lúc 11:12Z và khai đúng bốn
trường đó. DDL được viết theo bản 0.2.0, **không** theo trí nhớ về packet.

**Nửa còn lại thuộc WA, và tôi đo được nó chưa xong.** `0002_tc_owner_auth_session` vẫn còn
`CREATE TABLE IF NOT EXISTS owner` của nó trên một nhánh song song. Hệ quả **đã đo**:

* `alembic upgrade head` từ DB rỗng: **OK** — Alembic đi nhánh base trước, `owner` trong DB là
  đúng định nghĩa ở trên (kiểm bằng `sqlite_master`), 17 bảng.
* Ép **thứ tự ngược** (`upgrade 0002_tc_owner_auth_session` rồi `upgrade head`): **FAIL**
  (`table owner already exists`). Đây chính là dấu hiệu F-01 muốn: sau khi WA bỏ `CREATE` của
  họ và đổi `down_revision` sang `0002_base_entities`, thứ tự ngược **không còn tồn tại** vì
  nhánh song song biến mất. Tôi **không** che nó bằng `IF NOT EXISTS` — làm vậy là dựng lại đúng
  cái lỗi vừa bị bắt.

Test mới: `test_owner_table_has_one_definition_with_the_full_contract_set` so tập cột đọc bằng
`PRAGMA table_info(owner)` với **tập trường của `entities.yaml`** (bằng nhau, không phải "chứa"),
và `test_timestamp_check_rejects_a_second_precision_value` chứng minh timestamp thiếu mili-giây bị
chính database từ chối.

## A4. F-A3R1-04 — năm bảng move-set ra khỏi revision identity

Revision mới `0002b_shared_move_set_tables` (down `0002_base_entities`) tạo `saved_snapshot`,
`analysis`, `saved_item`, `work_label`, `first_announced_ledger`. Header của nó nói rõ
`owner_module` của từng bảng, custodian là `MOD-data-store`, và **card nào sẽ tiếp quản**.
`0003_tc_canonical_identity_merge` nay chỉ tạo bốn bảng của chính nó (`work_version`,
`identity_merge_audit`, `identity_alias`, `identity_conflict`) và chuyển `down_revision` sang
`0002b_shared_move_set_tables`. Đồ thị revision vẫn **một head** (`0004_merge_phase1_heads`).

Nhân dịp tách, năm bảng được siết đúng theo `entities.yaml`: CHECK GLOB cho mọi cột
`timestamp_utc_ms`, `sha256:*` cho `content_hash`/`payload_hash`, độ dài `label_text` 1..120,
`generation_number >= 1`. Bốn bảng identity cũng nhận CHECK GLOB timestamp (cùng lớp `F-A3R1-14`).
Cố ý **không** thêm CHECK cho `work_version.content_fingerprint` và `analysis.source_fingerprint`:
fixture (a) và (g) dùng giá trị tượng trưng (`F_W1_v1`, `F_2503.03333_v1`) cho chúng, và siết cột
đó sẽ là sửa dữ liệu oracle bằng schema.

## A5. F-A3R1-09 — kiểm kê fixture của §2/§8

| Fixture (card §2 mục 5) | Trạng thái | Ở đâu / vì sao |
| --- | --- | --- |
| `identity/README.md` | ĐỌC | quy ước khóa `_`, quy ước hash tượng trưng — cả hai được hiện thực trong loader của test |
| `identity/a-merge-doi-arxiv.json` | **EXERCISED** | 8 test (rows, counts, hash oracle, forbidden_effects, replay, CAS, E2) |
| `identity/b-post-only-missing-ids.json` | **EXERCISED** | target post-only, 0 work |
| `identity/c-identity-conflict.json` | **EXERCISED** | quarantine, 0 merge, idempotent, không tự hết hạn |
| `identity/g-arxiv-version-v1-v2.json` | **EXERCISED** | 1 work / 2 version / 1 is_current |
| `identity/h-five-posts-thread-one-target.json` | **EXERCISED** | 6 biến thể → 1 work + 1 alias + 6 nguồn dẫn |
| `reporting/i-identity-merge-single-first-announced.json` | **EXERCISED** (một phần) | hook §8.3; `preserved_counts.published_report_item` là `xfail(strict)` — CR-03 |
| `boundary/README.md` | ĐỌC | quy ước `edge_assertion`, bảng mã lỗi R5-01 |
| `boundary/a-default-deny-sweep-36-edges.json` | **EXERCISED** (mới ở FIX1) | `test_boundary_sweep_names_no_edge_of_this_module`: 36 event, **0** event chạm `MOD-identity-service`, và `modules.yaml.forbidden_edges` cũng vậy. Nghĩa vụ SG-DENY của card này vì thế **thu về** đúng "từ chối caller ngoài `allowed_edges`", điều đã có 4 test `FORBIDDEN_EDGE`. Nếu ai đó thêm một cạnh chạm module này, test **fail** và nghĩa vụ mọc lại |

Không còn fixture nào trong read set ở trạng thái im lặng. Sáu fixture khác của thư mục
`identity/` (`d`, `e`, `f`, `pos-*`, `neg-*`) **không** nằm trong §2 của card này và thuộc card
Saved / ingest — `NOT_RUN` ở đây theo thiết kế, không phải bỏ sót.

## A6. F-A3R1-05 — `post.ingest_receipt_id`

Không có addendum nào của `worker-WI` tồn tại ở thời điểm tôi làm việc (tôi đọc
`evidence/handoffs/TC-ingest-idempotent-ack-lost-handoff.md` lúc 11:05Z: chỉ có `CR-TC-ingest-01`
mô tả đúng vấn đề). Tôi **không** đơn phương quyết cho card khác; tôi ghi lựa chọn và lý do vào
header của `0002_base_entities` và chuyển yêu cầu bằng `CR-TC-IDENTITY-14`:

> **Lựa chọn: revision của ingest dựng lại `post` để thêm khóa ngoại**, không kéo
> `ingest_receipt` vào revision base.

Lý do đo được, không phải sở thích: kéo `ingest_receipt` (và `checkpoint` mà nó tham chiếu) vào
base sẽ **lặp lại đúng lỗi `F-A3R1-04`** vừa được sửa ở A4 — một revision tạo bảng của module
khác. Dựng lại bảng nằm trong revision **sở hữu bảng được tham chiếu**, chạy trên bảng rỗng, một
chỗ duy nhất. Phương án còn lại — khai `REFERENCES ingest_receipt (id)` ngay trong base — bị loại
vì SQLite phân giải khóa ngoại lúc DML: mọi INSERT vào `post` giữa `0002_base_entities` và
revision của ingest sẽ lỗi, và packet chỉ cho hai lựa chọn ở trên. WI cần ghi đoạn đối xứng của
đoạn này trong migration của họ.

## A7. Evidence của đợt FIX1

| ID | Nội dung | Kết quả |
| --- | --- | --- |
| `EV-TC-IDENTITY-07` | `pytest tests/contract/test_identity_normalization.py tests/integration/test_identity_merge_audit.py -p no:cacheprovider -p no:warnings`, 11:11:14Z→11:11:24Z | **117 passed, 2 xfailed(strict), 0 failed**, exit 0 |
| `EV-TC-IDENTITY-08` | `alembic heads` / `upgrade head` trên DB rỗng | **1 head** (`0004_merge_phase1_heads`), upgrade OK, **17 bảng** |
| `EV-TC-IDENTITY-09` | thứ tự nhánh ngược (auth trước) | **FAIL** (`table owner already exists`) — thuộc WA, xem A3 |
| `EV-TC-IDENTITY-10` | `ruff check .` · `ruff format --check .` · `mypy` | exit 0 · 60 file đã format · "no issues found in 25 source files" |
| `EV-TC-IDENTITY-11` | **toàn bộ** `pytest`, 11:11:24Z→11:12:00Z | **291 passed, 4 xfailed, 0 failed**, exit 0 — lỗi `test_readiness_is_not_routed_in_phase_0` báo ở §5.4 nay **đã hết** (card khác đã sửa) |

Manifest: `evidence/runs/TC-canonical-identity-merge-E1-20260907T111124Z.json`
(`EV-E1-02-tc-canonical-identity-merge`, 13 380 byte), validate với
`evidence/manifest.schema.json` → **0 lỗi**. Manifest cũ (`…102504Z.json`) giữ nguyên: nó mô tả
lần chạy trước và `contract_hashes` của nó ghim `entities.yaml` **0.1.0**.

## A8. Change request mới

| ID | Gửi tới | Nội dung |
| --- | --- | --- |
| `CR-TC-IDENTITY-11` | `TC-saved-snapshot` | `saved_snapshot` và `saved_item` được tạo sẵn ở `0002b_shared_move_set_tables` theo `entities.yaml`. Card của bạn **mở rộng** (revision sau, hoặc dựng lại bảng) — **không** phát `CREATE TABLE` thứ hai: hai định nghĩa cho một bảng chính là `F-A3R1-01`. |
| `CR-TC-IDENTITY-12` | `TC-analysis-once-per-generation` | Như trên cho `analysis` và `work_label`; chú ý `ux_analysis_valid_key` (partial UNIQUE `WHERE status = 'valid'`) và `target_key` là **generated STORED** — merge move-set dựa vào cả hai. |
| `CR-TC-IDENTITY-13` | `TC-report-coverage-publish-cas` | Như trên cho `first_announced_ledger`; `first_report_id` hiện **chưa** có `REFERENCES report(id)` vì `report` chưa tồn tại — card của bạn thêm khi tạo `report`. `ux_first_announced_canonical_work` là I07 ở mức schema; hook §8.3 của merge phụ thuộc vào nó. |
| `CR-TC-IDENTITY-14` | `TC-ingest-idempotent-ack-lost` (WI) | Xin dựng lại `post` trong revision của ingest để `post.ingest_receipt_id` có `REFERENCES ingest_receipt (id)` thật (F-A3R1-05), và ghi đoạn đối xứng của A6 vào migration đó. Base revision giữ cột đúng tên/kiểu/NOT NULL. Nếu WI muốn phương án ngược lại (`ingest_receipt` vào base), cần một ruling của Coordinator vì nó xung đột với `F-A3R1-04`. |
| `CR-TC-IDENTITY-15` | WA (`TC-owner-auth-session`) | Bỏ `CREATE TABLE IF NOT EXISTS owner` và hai `ALTER` bù cột trong `0002_tc_owner_auth_session`, đổi `down_revision` sang `0002_base_entities`. Chừng nào còn, thứ tự nhánh ngược vẫn FAIL (đo ở `EV-TC-IDENTITY-09`) và `0004_merge_phase1_heads` phải giữ nhánh auth trong danh sách `down_revision`; sau khi bỏ, revision merge có thể rút xuống hai nhánh. |

Mười CR của đợt trước (§6) **không** thay đổi trạng thái, trừ `CR-TC-IDENTITY-04`: nó được thay
bằng A4 + `CR-TC-IDENTITY-11..13`, tức lý do vẫn còn nhưng quyền sở hữu nay được ghi ở đúng chỗ.

## A9. `CR-TC-ingest-07` — hai dòng dài trong `0002b`

`worker-WI` báo `ruff check .` đỏ vì hai vi phạm E501 trong
`server/migrations/versions/0002b_shared_move_set_tables.py`. Đúng: bảng RST trong docstring của
bản nháp đầu tiên có hai dòng 101 ký tự. Chúng đã được sửa **trước** khi tôi chạy các cổng ở §A7
(bảng được viết lại hẹp hơn, tên card chuyển xuống một dòng riêng); WI quan sát trúng trạng thái
trung gian. Kiểm lại ngay trước khi giải phóng lease:

* `ruff check .` → `All checks passed!`, **exit 0**
* `ruff format --check .` → 60 file đã format, exit 0
* `awk 'length > 100'` trên chính file đó → **không dòng nào**
* file ở trạng thái cuối: sha256 `9ec48efdff1f702f1a3c3fe926238156aff639a359e9d8ce0a600406fd85ffaa`,
  13 354 byte — **đúng** giá trị đã ghi ở §A2, nên bảng delta không cần sửa
* chạy lại toàn bộ sau khi kiểm: **291 passed, 4 xfailed, 0 failed**; `alembic heads` = 1;
  `upgrade head` trên DB rỗng OK

`lease_released_at`: 2026-09-07T11:15Z. Sau dòng này tôi không ghi thêm file nào.

---

# ADDENDUM — PKT-TC-IDENTITY-FIX2 (`CR-TC-research-01`: khẳng định head phải là cấu trúc, không phải tên)

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-IDENTITY-FIX2` · authority `AUTH-COORD-TC-IDENTITY-FIX2` (parent `AUTH-OWNER-20260907-04`) · lease `LEASE-TC-IDENTITY-e2` **chỉ trên** `tests/integration/test_identity_merge_audit.py` |
| worker principal | `worker-WM` · **status `DONE`** · completion_claim **không đổi**: `IMPLEMENTATION_VERIFIED` |
| next actor | `Coordinator` · `lease_released_at` 2026-09-07T15:19Z |

## B1. Lỗi và cách sửa

`test_migration_chain_resolves_to_a_single_head` khẳng định
`heads == ["0004_merge_phase1_heads"]` — tên **một** revision cụ thể. Đúng ở thời điểm viết, sai
ngay khi card kế tiếp thêm migration: `server/migrations/versions/0005_tc_research_connector_metadata.py`
(Phase 2B, **ngoài** lease của tôi) đẩy head sang `0005_…` và test của tôi sẽ làm đỏ toàn bộ suite
cho **mọi** card, không riêng card này. Đó là một tripwire, không phải một oracle.

Sửa: khẳng định **số lượng** head, không phải danh tính của nó —
`assert len(heads) == 1, heads` — lấy heads đúng bằng cách cũ (`ScriptDirectory.from_config`).
Bất biến thật sự là "`alembic upgrade head` không mơ hồ"; *head là revision nào* thay đổi theo mỗi
card và **đó là đúng**. Docstring ghi lại lý do để không ai "sửa lại" thành so tên.
Không dòng nào khác trong file bị chạm.

## B2. Hash và kết quả

| Trường | Giá trị |
| --- | --- |
| `tests/integration/test_identity_merge_audit.py` **trước** | `0c1e6f4a49965644a193151a7c94ca03f9d0571741e59e35ed15fd73a089edc4` (67 446 B) |
| `tests/integration/test_identity_merge_audit.py` **sau** | `4c8c957d7cfd8a42b30d43beb28102487b148216e02d851adef28bf6e3b68130` (67 718 B) |
| File test này | **42 passed, 2 xfailed, 0 failed** (11:17:29Z→11:17:41Z UTC theo đồng hồ phiên) |
| Toàn bộ suite | **572 passed, 4 xfailed, 0 failed**, exit 0 |
| `ruff check` + `ruff format --check` trên file | exit 0 |

Không file nào của card khác đang đỏ ở lần chạy này: **0 failed** trên toàn bộ suite. Hai `xfail`
của card này vẫn là `CR-TC-IDENTITY-02` và `-03` (không đổi); hai `xfail` còn lại thuộc card khác.

Manifest **không** phát hành lại: thay đổi là một khẳng định trong test, không đụng tới code sản
phẩm, migration hay oracle của fixture; `EV-E1-02-tc-canonical-identity-merge` vẫn mô tả đúng
hành vi đã đo. Số đếm mới ghi ở bảng trên.

`lease_released_at`: 2026-09-07T15:19Z. Sau dòng này tôi không ghi thêm file nào.

---

# ADDENDUM — PKT-TC-IDENTITY-FIX3 (`F-A3-P4-03`: một xfail sống lâu hơn lý do của nó)

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-TC-IDENTITY-FIX3` · authority `AUTH-COORD-TC-IDENTITY-FIX3` · lease `LEASE-TC-IDENTITY-e3` trên `tests/integration/test_identity_merge_audit.py`, addendum này và manifest |
| worker principal | `worker-WM` · **status `DONE`** · completion_claim **không đổi**: `IMPLEMENTATION_VERIFIED` |
| next actor | `Coordinator` · `lease_released_at` 2026-09-08T01:33Z |

## C1. Cái gì sai và sửa thế nào

`test_fixture_i_preserved_published_report_items` vẫn mang lý do *"needs the `report` and
`report_item` tables, owned by the reporting card (not in Phase 1 M1)"*. Hai bảng đó **đã tồn
tại** (`0010_tc_report_coverage_publish_cas`, `server/app/report/publisher.py`). Marker
`strict=True, run=True` nên không có gì bị giấu — test **thật sự** vẫn fail — nhưng fail vì một lý
do mà văn bản của nó không còn mô tả. Đó là lỗi: một `xfail` là một lời hứa sẽ quay lại, và lời
hứa này đã đến hạn.

Nay nó **chạy thật**, và chạy qua đường thật:

1. DB ở `alembic upgrade head` (toàn bộ migration của mọi card, đúng thứ tự một deployment chạy).
2. Hai work của fixture (i) được gieo kèm summary + label vector: `A` mang DOI, `B` mang arXiv ID
   và được phát hiện sớm hơn — đúng hình dạng fixture pin.
3. Một kỳ báo cáo được **phát hành bằng `report.publish`** (`build_report` → `record_build` →
   `publish_report`), không phải bằng `INSERT` mô phỏng. Chỉ một report do publisher thật ghi mới
   chứng minh được rằng merge để yên nó.
4. Merge chạy trên đúng hai work đó.

Ba khẳng định, tất cả đo được:

* `preserved_counts.published_report_item` **= 2** — đúng con số fixture (i) pin.
* Mọi hàng `report_item` và `report` **giống nhau từng cột** trước và sau merge, **kể cả**
  `target_key` vẫn trỏ work **thua**. Đó không phải dữ liệu cũ: kỳ đã publish là phát biểu về
  ngày hôm đó (I05, I17). Một merge viết lại nó sẽ làm kho lưu trữ mâu thuẫn với thứ owner đã đọc.
* Test thứ hai (`test_first_announced_after_a_real_publish_inherits_the_earlier_date`) chạy §8.3
  trên hàng `first_announced_ledger` **do chính transaction publish ghi**: sau merge còn đúng
  **một** hàng có hiệu lực, mang ngày **sớm hơn**, hàng kia nhận `superseded_by_merge_id`;
  `moved_counts.first_announced` = 2 (I07).

Trước đây khối tương ứng chỉ nạp `given.rows` của fixture bằng loader — nay cả `report_item` lẫn
ledger đều là sản phẩm của code sản phẩm. `CR-TC-IDENTITY-03` (§6) do đó **ĐÓNG**.

## C2. `xfail` còn lại — đã rà, không lỗi thời

Chỉ còn **một**: `test_fixture_a_first_announced_literal_null` (`strict=True`, `run=True`). Lý do
của nó nêu một **hợp đồng**, không nêu một card chưa tồn tại: fixture (a) vẫn khai
`moved_counts.first_announced = null` trong khi `contracts/reporting/time-and-tags.md` §8.3 đã
thay bằng một con số. Không card nào đóng được nó — chỉ một lần cập nhật fixture qua change
control (`CR-TC-IDENTITY-02`) mới đóng. Giữ nguyên, và giữ `strict=True` để ngày fixture được sửa
thì test này **fail** và bắt người ta gỡ marker.

Không có `skip` nào trong hai file test của card.

## C3. Hash và kết quả

| Trường | Giá trị |
| --- | --- |
| `tests/integration/test_identity_merge_audit.py` **trước** | `4c8c957d7cfd8a42b30d43beb28102487b148216e02d851adef28bf6e3b68130` (67 718 B) |
| `tests/integration/test_identity_merge_audit.py` **sau** | `30f1b1818ad0667b7e54237fbea8287a9e0995976620c2a53fae5e4bc22c50eb` (80 791 B) |
| Test của card | **119 passed, 1 xfailed, 0 failed** (trước: 117 passed / 2 xfailed) · 01:29:04Z→01:29:16Z |
| Toàn bộ suite | **1 032 passed, 4 xfailed, 1 failed** — lỗi duy nhất **không phải của card này**, xem C4 |
| `ruff check .` · `ruff format` · `mypy` | exit 0 · sạch · "no issues found in 87 source files" |

## C4. Một file đang đỏ, không phải của tôi

`tests/integration/test_pending_survives_cursor.py::test_fixture_e_the_late_discovery_is_still_a_new_discovery`
(card `TC-backfill-pending-ledger`) fail với **`[XPASS(strict)] CR-TC-BACKFILL-09`**: một
`xfail(strict=True)` của họ nay **đậu**, nên marker biến nó thành lỗi. Cùng đúng một lớp với
`F-A3-P4-03` mà addendum này sửa, chỉ ở hướng ngược lại. Nó chạy trên
`server/app/report/publisher.py` — file tôi **không** chạm — và fail y hệt khi chạy riêng, tức
không do thay đổi của tôi. Tôi **không sửa**: ngoài lease. Chuyển Coordinator.

## C5. Manifest

* **Mới:** `evidence/runs/TC-canonical-identity-merge-E1-20260908T012916Z.json`
  (`EV-E1-03-tc-canonical-identity-merge`, 14 448 B, `result: PASS`), validate với
  `evidence/manifest.schema.json` → **0 lỗi**. Có `invalidation.invalidated_by_paths` để lần sau
  không phải đoán bản ghi này hết hiệu lực khi file nào đổi — trong đó có
  `server/app/report/publisher.py`, vì kết luận nay phụ thuộc vào code của card báo cáo.
* **Cũ → STALE:** `…-E1-20260907T102504Z.json` và `…-E1-20260907T111124Z.json` đổi
  `result` sang `STALE` kèm `stale_reason` trỏ tới bản kế nhiệm. Số đếm và danh sách xfail của
  chúng không còn mô tả lần chạy hiện hành; nội dung còn lại giữ nguyên để đọc lại được lịch sử.

`lease_released_at`: 2026-09-08T01:33Z. Sau dòng này tôi không ghi thêm file nào.
