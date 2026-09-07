---
card_id: TC-research-connector-metadata
title_vi: Research connector: metadata arXiv/OpenAlex với nhịp gọi đọc từ cấu hình
status: draft
owner_role: implementation planning owner
template_ref: agent-tasks/TEMPLATE.md
milestone: M2
gate: G5
stack_decision: ADR-0006 (Option B — Python workers + TypeScript web) — ACCEPTED (OD-20260907-01)
claim_ceiling: IMPLEMENTATION_VERIFIED (E1 với response đã ghi sẵn; module **chưa** CONTRACT_READY — nhưng **không còn** vì REQ-A6, dữ kiện đó đã giải: lý do hiện hành là chưa hợp đồng nào nêu host/endpoint API của arXiv hay OpenAlex, cộng với E3 vẫn bị cấm ở card này; trần của card không nâng trần của module, và không có live claim nào)
owner_modules: [MOD-research-connector]
scenario_refs: [SC11, SC23, SC29, SC30, SC07, SC49]
invariant_refs: [I03, I11, I13]
evidence_manifest_id: EVM-TC-research-connector-metadata
source_refs: [SRC-SPEC §12, SRC-SPEC §13, SRC-PLAN §11 PC10, SRC-PLAN §12, SRC-PLAN §15]
baseline_pin_ref: "§0 của chính file này"
coding_precondition: "G5 pass + Owner go-ahead bằng văn bản; trước đó card chỉ được đọc"
---

# TC-research-connector-metadata — Research connector: metadata arXiv/OpenAlex với nhịp gọi đọc từ cấu hình

> **Chưa được phép code.** Card này là tài liệu giao việc ở trạng thái `DRAFT_FOR_REVIEW`. Nó chỉ trở thành lệnh thi công sau khi G5 pass và Owner ra lệnh bắt đầu. **Stack đã được Owner chốt: Option B — Python cho worker/server, TypeScript cho web UI** (`OD-20260907-01`, REQ-OQ02 đã trả lời). Phân chia ngôn ngữ là **ACCEPTED**; riêng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn `PROVISIONAL` cho tới khi có repo triển khai thật, và framework vẫn `PROVISIONAL` trừ khi ADR-0006 nêu tên.

## §0. Baseline pin

**Pin epoch: `PC10-PIN-P3b-20260908`** (thay `PC10-PIN-P3-20260908`; các epoch cũ hơn: `PC10-PIN-P3`, `PC10-PIN-P2d`, `PC10-PIN-P2c`, `PC10-PIN-P2b`, `PC10-PIN-P2`, `PC10-PIN-P1d`, `PC10-PIN-P1c`, `PC10-PIN-P1b`, `PC10-PIN-P1`, `PC10-PIN-OD01e`, `PC10-PIN-OD01d`, `PC10-PIN-OD01c`, `PC10-PIN-OD01b`, `PC10-PIN-OD01`, `PC10-PIN-FCW4f`…`PC10-PIN-FCW4-20260907`, `PC10-PIN-20260907`). **19 card.** Bản pin sau vòng quyết định `OD-20260907-04`: `REQ-A6` đã được giải bằng tài liệu chính thức — `contracts/retry-policy.yaml` lên `0.8.0` và `research_connector_rate_limit` **hết** `PLACEHOLDER_KC` (trạng thái nay là `DOCS_derived`); `contracts/ops/collector-probe.md` lên `0.5.0` — §6 ghi cổng probe đã đủ bốn xác nhận, §9.2 trỏ về `retry-policy.yaml` thay vì kể lại dữ kiện cũ. Cùng lượt: `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/owner-decisions.md`, `precode/baseline.json`, `precode/owner-decision-request.md`. **`P3` (2026-09-08)** pin thêm vòng `OD-20260907-05`…`-08`: `contracts/ai/providers.yaml` nay có adapter Anthropic thật (**cả hai `enabled: false`**, `terms_check` đã điền và Owner ký), `contracts/telegram/delivery.md` lên `0.2.1` (2/5 dữ kiện định dạng đã giải), `contracts/data/entities.yaml` sửa chữ trong một ghi chú (**không trường nào đổi**), cùng `precode/requirements.csv`, `precode/decision-register.md`, `precode/change-control.md`, `precode/baseline.json`. Bốn tên epoch trong hai ngày (`P2b`, `P2c`, `P2d`, `P3`) là hệ quả của việc file đã pin đổi byte ngay sau mỗi lần pin (`CR-PC10-15`); Coordinator nay đóng băng `precode/` **trước** mỗi lần pin. Hai tập byte khác nhau không được mang chung một tên epoch. **`P3b`** là lần pin sau `PKT-PC00-FIX28` — lần ghi `precode/` **cuối cùng** trước freeze (`precode/baseline.json` và `precode/decision-register.md`; `agent_profile/registry.json` đổi nhưng **không** card nào pin nó). Cùng lúc, đợt sáu card Giai đoạn 1/2 đã land. Quy tắc `STALE` đọc **byte**, không đọc ý định: mọi lần một file đã pin đổi byte đều kéo theo một lần pin lại toàn bộ. Hash tính lại trực tiếp trên repo. **Card là nguồn chuẩn của tên epoch** (`F-A2R1-03`). Lệch một dòng ⇒ card `STALE`, DỪNG.

| Nguồn | SHA-256 | Bytes |
| --- | --- | --- |
| `research-radar-spec.md` (= `precode/source/spec-v0.2.md`) | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | 41770 |
| `research-radar-pre-code-plan.md` (= `precode/source/pre-code-plan-v0.1.md`) | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | 64915 |

| Hợp đồng / fixture đã pin | SHA-256 | Bytes |
| --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `da5181b2888674134f6e3919ce401014015f223ea46a967d9fda3833c01a037b` | 22685 |
| `precode/baseline.json` | `52af62c8b11e6939a9a34798bd71b4a4e688d8ed85d9c579ee1858ed341037e9` | 124824 |
| `precode/decision-register.md` | `b26cf51a0d7c73661ab465e5a157aaad7a9ceb6f013926abd5117f6966764a7e` | 182028 |
| `contracts/modules.yaml` | `cf536acba6c02d377c5fc6c4e7ab0318dc88e0994ed998c926c3d65bdbda0457` | 108721 |
| `contracts/capabilities.yaml` | `17d7494fe38b2ab5d3778b9af5e2d82ad274bcafb792d90b94c8e614182097f7` | 47177 |
| `contracts/ports.yaml` | `c15b676b5619df7aee4f92afa35bdd7852c53333de7424e1423f702cf1e32684` | 128850 |
| `contracts/errors.yaml` | `640991c91ad046ebe513badad1a9baa0582be8269bf7696472322dd3e867599f` | 65180 |
| `contracts/retry-policy.yaml` | `f9505525ae438181326abef06974a0e0287bc685ee71df9710740672bd52a69a` | 61357 |
| `contracts/data/entities.yaml` | `ebcf460fa2e415cc6897cdbe7cee144bda9368e4a5af9cd514ec676224399936` | 241542 |
| `contracts/ops/collector-probe.md` | `9cf2b0185b100d0dc4fc8c69bc6d964c2b3853fb9814852444b56c8cdcbb0b79` | 32713 |
| `contracts/ops/internet-boundary.md` | `04ab315096336bc85ac170de4e4f819c6dd4aa85b3fc01b510bd709a4b8b27ff` | 13926 |
| `contracts/ops/deployment.md` | `dd7b10a961f00159068fc16d72456ffb4370e108c0c9ea060726e987a3240936` | 19568 |
| `contracts/data/identity.md` | `71fedc7f6996f5eebace1a53ec42b19bb16f0df4489d93a906e5c895bbb4f4fd` | 20610 |
| `contracts/data/invariants.md` | `7358f54bd2eff5e87c464b0a5f1657f21fa217a1024607316361976560011a9c` | 27816 |
| `contracts/state/run.yaml` | `479125cb0d927c690836b631d85804abdc0a9f6bd013dec3cb31f692ba1b4b27` | 95222 |
| `precode/adr/ADR-0001-topology-and-placement.md` | `9dd1aab43a0dbc8cefe83be997456b76bfc2595c7d20a0d69045b6c706319039` | 6161 |
| `precode/adr/ADR-0009-identity-alias-target-union.md` | `67844f12e4fe77a6a25b443a8fe84d053fbcfc9c30649296f55efc41befa4ee1` | 6145 |
| `acceptance/fixtures/identity/README.md` | `ce9ec21ec1cebe8a257a677e67097f1883a35c403b4421d3219862d185335e14` | 12611 |
| `acceptance/fixtures/identity/b-post-only-missing-ids.json` | `626f399ff54144d28f60418b14cfa58b54c41d8ba46c10b243428a0c1ba5e89e` | 6258 |
| `acceptance/fixtures/identity/g-arxiv-version-v1-v2.json` | `8e18ff69e9230b8d6d2ac7adac4e68b9e53c8998f5c784939d4c2b67158981c6` | 11420 |
| `acceptance/fixtures/identity/h-five-posts-thread-one-target.json` | `3ffe41c50d3829b88f54542cb283894f1c23ff2e7107ff90686e06b82ced944c` | 11326 |
| `acceptance/fixtures/collection/README.md` | `bcae6ae10961c353722d59f74b5941972f617341ee7d3b272cd686a5717c5ce1` | 12636 |
| `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json` | `7b588ca0ad1999bacdfa78ffb17ba6f0ad1336e399cb291502397f079168079b` | 7475 |
| `acceptance/fixtures/boundary/README.md` | `6a41b4e4fffc0febc9fb93aebae948d6a1ce3d91de45b57153ae9ce4aef42fba` | 10598 |
| `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json` | `5de06521eb250c1c4e1514d760b30f1f9fdf198a7f10f1342e7019ec68b3c4b0` | 31529 |

**Cố ý KHÔNG pin hash** (PC09 sở hữu; PC09-FIX1 chạy song song — dẫn bằng đường dẫn + SC id, theo ruling của Coordinator về `CR-PC10-01`): `acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`, và `evidence/tools/e0_check.py`. Đọc bản mới nhất của chúng ngay trước khi bắt đầu; PC10 **không** chạy `e0_check.py`.

## §1. Task ID, mục tiêu và non-goals

- **Task ID:** `TC-research-connector-metadata`
- **Milestone:** M2 (SRC-SPEC §13) · **Cổng:** G5 (SRC-PLAN §12)
- **Module sở hữu:** `MOD-research-connector`

**Mục tiêu.** Hiện thực `research.fetch_work_metadata` và `research.get_connector_health` đúng `contracts/ports.yaml`: tra bằng **ID đã chuẩn hóa** (DOI/arXiv id) trên host trong allowlist, ghi `source_fetch_log` làm provenance, và **đọc nhịp gọi từ settings** — connector từ chối khởi động khi bốn giá trị REQ-A6 còn `null`, thay vì chạy với một con số tự đặt.

**Non-goals.**

- **Không gọi mạng thật.** Card này dừng ở E1 với response đã ghi sẵn; E3 là gói riêng sau khi bốn dữ kiện REQ-A6 được đọc từ tài liệu chính thức.
- Không ghi `work` / `work_version` / `identity_alias` — `MOD-identity-service` sở hữu chúng (`DC-RC-03`: connector chỉ đọc). Card này trả metadata cho caller.
- Không đoán DOI/arXiv id từ văn bản chưa chuẩn hóa (CN-6, I03).
- Không điền bốn giá trị `PLACEHOLDER_KC` — đó là dữ kiện bên ngoài, không phải lựa chọn kỹ thuật.
- Không điều khiển Chrome, không chạm đường X (CN-3, `FE-20`).

## §2. Read set

Đọc đủ danh sách ở §0 (đó **là** read set, kèm hash). Thứ tự đề nghị:

1. `precode/README.md` và `precode/change-control.md` → hiểu baseline và điều cấm. (Hai file này do chính gói PC10 tạo trong cùng packet, nên không tự pin hash của mình ở §0; kiểm bằng `sha256sum` theo bảng trong `evidence/handoffs/PC10-handoff.md`.)
2. `precode/adr/ADR-0011-frameworks-and-toolchain.md` — framework và toolchain mà §8 giả định (`provisional-accepted`; Owner có thể bác bất kỳ dòng nào mà không ảnh hưởng hợp đồng). Rồi các ADR nghiệp vụ: `precode/adr/ADR-0001-topology-and-placement.md`, `precode/adr/ADR-0009-identity-alias-target-union.md`.
3. Hợp đồng nghiệp vụ: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`, `contracts/ops/deployment.md`, `contracts/data/identity.md`, `contracts/data/invariants.md`, `contracts/state/run.yaml`.
4. Hợp đồng nền: `contracts/ports.yaml`, `contracts/modules.yaml`, `contracts/capabilities.yaml`, `contracts/errors.yaml`, `contracts/retry-policy.yaml`, `contracts/data/entities.yaml`.
5. Fixture bắt buộc: `acceptance/fixtures/identity/README.md`, `acceptance/fixtures/identity/b-post-only-missing-ids.json`, `acceptance/fixtures/identity/g-arxiv-version-v1-v2.json`, `acceptance/fixtures/identity/h-five-posts-thread-one-target.json`, `acceptance/fixtures/collection/README.md`, `acceptance/fixtures/collection/h-metadata-unavailable-post-only.json`, `acceptance/fixtures/boundary/README.md`, `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §3. Write set — layout theo Stack B (ACCEPTED); đường dẫn cụ thể còn PROVISIONAL

Mọi file **không** nằm trong bảng này là **read-only**. Toàn bộ `contracts/`, `acceptance/`, `precode/` là read-only với card này: phát hiện sai ⇒ change request, không tự sửa.

| Đường dẫn (PROVISIONAL) | Vai trò |
| --- | --- |
| `server/app/research/client_arxiv.py` | HTTP client arXiv: host trong allowlist, chỉ ID đã chuẩn hóa, tôn trọng `Retry-After` |
| `server/app/research/client_openalex.py` | HTTP client OpenAlex: như trên, kèm định danh liên hệ lấy từ settings (REQ-A6 — chưa có thì không gọi) |
| `server/app/research/service.py` | `research.fetch_work_metadata`, `research.get_connector_health`; cửa nhịp gọi; ánh xạ lỗi nguồn → mã hợp đồng |
| `server/app/research/router.py` | điểm vào **nội bộ** cho `research.*` (`transport: internal`) — **không** mở route HTTP công khai |
| `server/app/research/repository.py` | ghi `source_fetch_log` (entity duy nhất module này sở hữu) |
| `tests/contract/test_research_metadata_fixtures.py` | 4 fixture identity/collection + response đã ghi sẵn |
| `tests/integration/test_research_connector_health.py` | health `ok|degraded|unavailable`; khởi động bị từ chối khi giá trị REQ-A6 còn null |

**Quy ước ngôn ngữ (ACCEPTED, `OD-20260907-01`):** `server/`, `collector/`, `worker/`, `probe/` là **Python**; `web/` là **TypeScript**. Layout TypeScript dùng chung một quy ước cho mọi card có phần web — xem `agent-tasks/README.md` §5.3. Đường dẫn còn `PROVISIONAL` vì chưa có repo triển khai; đổi đường dẫn **chỉ** sửa bảng này và §8, không chạm §2/§4/§5/§6/§7 — hợp đồng độc lập framework.

## §4. Consumes / produces

**Produces** (operation card này hiện thực; ID lấy từ `contracts/ports.yaml`, không được đặt tên gần giống):

- `research.fetch_work_metadata`
- `research.get_connector_health`

**Consumes:** không operation nào của hệ thống.

**Schema:**

- nguồn schema request/response của `research.fetch_work_metadata` → `contracts/data/entities.yaml`
- nguồn schema response của `research.get_connector_health` → `contracts/ops/deployment.md`

**State effects.** Ghi **một** hàng `source_fetch_log` cho mỗi lời gọi ra ngoài (`source_type`, `endpoint` đã che tham số nhạy cảm, `requested_at`, `outcome`, `response_hash`, `work_id` nếu có). Ngoài hàng đó, **không ghi gì**: `research.fetch_work_metadata` là read-only với dữ liệu nghiệp vụ (`contracts/ports.yaml`: `mutation: false`). Nguồn lỗi ⇒ `SOURCE_METADATA_UNAVAILABLE` và target vẫn tồn tại ở mức `evidence_level = post_only` (CN-5, REQ-D33); **không** xóa abstract đã có. Bàn giao identity đi qua caller: `server.app.identity.service` là nơi `work`/`work_version`/alias được ghi, và khóa `response_hash` trong trường `evidence_ref` của `identity_alias` trỏ về cột cùng tên của `source_fetch_log` (`contracts/data/identity.md` §7) — đó là đường truy vết bằng chứng, không phải một cạnh mới.

## §5. Allowed communication

`contracts/modules.yaml` khai **default deny**: cạnh không có trong registry là bị cấm.

**Được gọi bởi:**

- `MOD-ingest-service` — internal (`research.fetch_work_metadata`)
- `MOD-health-service` — internal (`research.get_connector_health`)

**Được phép gọi:**

- API công khai của arXiv và OpenAlex — **chỉ** hai host trong allowlist (`contracts/modules.yaml` `network_egress: [arxiv_api, openalex_api]`)

**Đường bị cấm (denied paths):**

- **Không** nhận chỉ dẫn fetch URL tùy ý từ model hay từ nội dung bài (CN-2, I11, denied case NC-07). Đầu vào hợp lệ duy nhất là DOI/arXiv id đã chuẩn hóa (CN-4).
- **Không** điều khiển Chrome và không chạm đường X (CN-3, NC-08, `FE-20`).
- Scheme allowlist chỉ `https`; host allowlist là danh sách **cho phép**, không phải danh sách chặn (`contracts/ops/internet-boundary.md` §3).
- Không giữ key AI; secret scope chỉ là định danh liên hệ mà OpenAlex yêu cầu.
- Không ghi dữ liệu authoritative của identity (`DC-RC-03`).

Bảo mật (chốt post-FIX1 trong `contracts/http/openapi.yaml`): `owner_session` cho mutation nghĩa là `ownerSessionCookie` **AND** `ownerCsrfToken` trong **một** security requirement; collector và analysis worker dùng bearer riêng; mọi route `backup.*` chỉ nhận `backupOperatorToken`.

**Ranh giới mã lỗi khi bị từ chối (ruling R5-01, bắt buộc — chọn sai mã là FAIL):**

| Tình huống | Mã |
| --- | --- |
| Request HTTP từ một lớp principal không được phép cho operation đó (ví dụ token collector gọi `save.create`) | `UNAUTHORIZED` (401) |
| Lời gọi/import trong tiến trình đi qua một cạnh **không** có trong `allowed_edges` (ví dụ FE-08 collector → analysis worker, scheduler → Telegram) | `FORBIDDEN_EDGE` |
| Actor thiếu capability tiến trình/mạng/filesystem/tool (adapter mở socket, connector điều khiển Chrome) | `CAPABILITY_DENIED` |
| Mutation dùng phiên owner mà thiếu/sai CSRF token | `CSRF_REJECTED` (403; **không** hủy phiên) |

Mỗi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` có `denied_cases[]` với `expected_error_code` theo bảng trên và `scenario_refs: [SC49]`. Oracle chung: `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`.

## §6. Invariants và transaction

| Invariant | Nội dung |
| --- | --- |
| `I03` | không đoán định danh; ID chưa chuẩn hóa thì không tra |
| `I11` | nội dung nguồn/AI output không chọn được URL để fetch |
| `I13` | trạng thái suy giảm là **giá trị trả về**, không phải lỗi bị nuốt |

**Transaction và commit point:**

- Không có transaction nghiệp vụ. Hàng `source_fetch_log` được ghi cho **cả** lời gọi thất bại — một lời gọi không để lại dấu vết là một lời gọi không kiểm được nhịp.

**Race, replay và forbidden effects:**

- Hai lời gọi song song cùng một ID: không có khóa; kết quả trùng nhau vô hại vì operation read-only. Cửa nhịp gọi là **theo nguồn**, không theo lời gọi, nên song song không được lách sàn.
- Timeout transport ⇒ `outcome = timeout_unknown` trong `source_fetch_log`; **không** kết luận nguồn không có dữ liệu (RP-01).

## §7. Error obligations

Mã lỗi lấy từ `contracts/errors.yaml` (28 mã). Không tạo mã mới trong code.

| Mã lỗi | Nghĩa vụ: trạng thái đích, ai retry, khi nào dừng |
| --- | --- |
| `SOURCE_METADATA_UNAVAILABLE` | nguồn lỗi/không trả; target giữ `post_only`; không xóa dữ liệu cũ |
| `RATE_LIMITED` | nguồn báo giới hạn nhịp; `Retry-After` của nguồn **thắng** mọi số trong cấu hình |
| `CAPABILITY_DENIED` | thiếu capability mạng, host ngoài allowlist, hoặc cấu hình nhịp gọi còn `null` |
| `VALIDATION_ERROR` | ID chưa chuẩn hóa hoặc sai định dạng |
| `NOT_FOUND` | nguồn trả rỗng cho một ID hợp lệ |
| `INTERNAL` | mã duy nhất của `research.get_connector_health` (ruling F-A2R1-09) |

Error envelope bắt buộc: `code`, `scope`, `retry_class`, `message_safe`, `correlation_id`, `details_safe`, `retry_after` nếu có. **Không** lộ transcript, key hay cookie (SRC-PLAN §5.1).

## §8. Verification

**Scenario.** `acceptance/scenarios.yaml` **chưa tồn tại** (PC09). Các SC ID dưới đây là anchor đã cấp phát; cái nào chưa có fixture được đánh dấu rõ.

- SC11
- SC23
- SC29
- SC30
- SC07
- SC49

**Lệnh sẽ chạy** (PROVISIONAL theo ADR-0006):

- `uv run pytest tests/contract/test_research_metadata_fixtures.py -q` (PROVISIONAL)
- `uv run pytest tests/integration/test_research_connector_health.py -q` (PROVISIONAL)
- `uv run python evidence/tools/e0_check.py` — E0 lint (PC09)
- **Không** có lệnh gọi mạng trong card này. E3 là gói riêng.

**Oracle** (đo được bằng đếm hàng, hash hoặc so chuỗi — không phải bằng đọc log):

- Fixture `collection/h-metadata-unavailable-post-only.json` (SC11): nguồn không trả metadata ⇒ `SOURCE_METADATA_UNAVAILABLE`, target vẫn tồn tại ở `post_only`, đợt chạy **không** bị chặn (CN-5).
- Fixture `identity/g-arxiv-version-v1-v2.json` (SC30): v1 và v2 là hai `work_version` của cùng một `work`, không phải hai công trình.
- Fixture `identity/b-post-only-missing-ids.json` (SC29): không có DOI/arXiv id ⇒ **không gọi nguồn**, không đoán id; số request ra ngoài = 0.
- Cấu hình nhịp gọi còn `null` ⇒ connector **từ chối khởi động** và `research.get_connector_health` trả `unavailable` kèm lý do; số request ra ngoài = 0.
- Đếm host: mọi outbound connection trong lần chạy fixture đều nằm trong allowlist; ngoài allowlist = 0 (`NB-01`).

**Evidence artifacts:** log pytest; bản ghi response đã dùng (đã che tham số nhạy cảm); dump `source_fetch_log`; đếm outbound connection theo host.

**Yêu cầu live.** E3 (gọi thật arXiv/OpenAlex theo nhịp đã ghi) **NOT_RUN** và cố ý nằm ngoài card này: nó bị chặn cứng bởi `REQ-A6` cho tới khi bốn dữ kiện được đọc từ tài liệu chính thức. Không có live claim nào ở đây.

**Trạng thái hiện tại của mọi mục ở trên: `NOT_RUN`.** Không có test nào đã chạy ở Pre-code (SRC-PLAN §17: E1–E4 chưa chạy ghi NOT_RUN).

## §9. Completion ceiling

**Tối đa: `IMPLEMENTATION_VERIFIED (E1 với response đã ghi sẵn; module **chưa** CONTRACT_READY — nhưng **không còn** vì REQ-A6, dữ kiện đó đã giải: lý do hiện hành là chưa hợp đồng nào nêu host/endpoint API của arXiv hay OpenAlex, cộng với E3 vẫn bị cấm ở card này; trần của card không nâng trần của module, và không có live claim nào)`.**

**Ngoài phạm vi đã phê chuẩn.** Read set của card này chạm `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md` — phạm vi còn mang KC. Card **không** đủ điều kiện nâng lý do trần claim; các điểm dừng KC ở §10 (REQ-A5/REQ-A6, `CR-PC07-04`, SP1, REQ-OQ03) **giữ nguyên**. Ngoài ra 2 file hợp đồng trong read set vẫn khai `claim_ceiling: DRAFT_FOR_REVIEW`: `contracts/ops/collector-probe.md`, `contracts/ops/internet-boundary.md`.

**Đọc lại danh sách KC ngay trên cho đúng ngày hôm nay.** Câu boilerplate đó liệt kê `REQ-A6` như một điểm dừng còn hiệu lực; với **card này** điều đó **không còn đúng**: `OD-20260907-04` đã giải cả bốn dữ kiện nhịp gọi cộng câu hỏi định danh, và `contracts/retry-policy.yaml` `0.8.0` không còn mục `PLACEHOLDER_KC` nào (xem `SG-A6` và `SG-IDENT` ở §10, cả hai đã viết lại). Thứ **thật sự** giữ `MOD-research-connector` ở dưới `CONTRACT_READY` là hai điều khác: (1) **chưa hợp đồng nào nêu host/endpoint API** của arXiv hay OpenAlex — đó là cấu hình triển khai và vẫn là một điều kiện từ chối (`SG-DOC`); (2) **E3 (gọi thật) chưa chạy và bị card này cấm** (`SG-LIVE`). Và phán quyết `CONTRACT_READY` không thuộc về card hay Worker: `retry-policy.yaml` `scope_note_vi` nói thẳng rằng hết `PLACEHOLDER_KC` **không** tự trao nhãn đó — nó là việc của PC05 và Coordinator, xét trên toàn bề mặt port của module.

Mẫu claim bắt buộc (SRC-PLAN §14.3): claim + baseline (spec hash + contract version/hash + implementation revision) + requirements covered + evidence manifest IDs + observed result + **not established** + open issues + review type. Không được viết "independent audit passed"; tự kiểm là `SELF_VALIDATION`.

## §10. Stop-and-report

| ID | Điều kiện dừng |
| --- | --- |
| `SG-A6` | **REQ-A6 đã được giải** (`OD-20260907-04`; `contracts/retry-policy.yaml` `0.8.0`, `research_connector_rate_limit.status = DOCS_derived`, mỗi dữ kiện có URL, ngày đọc và trích dẫn nguyên văn). Điều kiện dừng cũ — *"bốn giá trị còn `null`"* — **không còn hiệu lực**, và mặc định của connector nay mang đúng nhịp đã ghi trong hợp đồng. Hai điều **vẫn** là điểm dừng: (a) nếu bất kỳ giá trị nào bị cấu hình tường minh thành `null` hoặc không hợp lệ, connector **từ chối khởi động** thay vì tự chọn một con số — cơ chế được giữ và có test hồi quy; (b) **không ai được đoán một hạn mức**: đổi số đi qua hợp đồng rồi mới tới code, không bao giờ ngược lại. `min_interval_ms = 3000` vẫn chỉ là sàn an toàn, không phải hạn mức thật. |
| `SG-IDENT` | **Đã giải, và câu trả lời là "không có"** (REQ-D34): theo tài liệu hiện hành đã đọc (`contracts/retry-policy.yaml` `0.8.0`, khối `sources`), **không nguồn nào** trong hai nguồn đòi một định danh liên hệ, nên `requires_contact_identity` mặc định `False` — giá trị suy ra từ hợp đồng, không phải một lựa chọn của code. Cơ chế **vẫn nằm trong code** theo đúng hợp đồng: nếu một nguồn được khai là **có** yêu cầu định danh mà cấu hình chưa có, connector **không gọi** nguồn đó — gọi ẩn danh khi nguồn đòi định danh là vi phạm điều khoản, không phải một lựa chọn kỹ thuật. Điểm dừng này hiện **không kích hoạt**; nguồn đổi chính sách ⇒ sửa hợp đồng trước, code sau. |
| `SG-LIVE` | Card này **không** được gọi mạng thật. Mọi test dùng response đã ghi sẵn. Cần một lời gọi thật ⇒ DỪNG và xin packet E3 riêng. |
| `SG-DOC` | Không có URL tài liệu nào trong hai nguồn đã pin (`CR-PC05-03`). Không bịa URL, và không coi một trang tìm được bằng suy đoán là 'tài liệu chính thức'. |
| `SG-STACK` | Stack đã chốt: **Option B** (`OD-20260907-01`) — `server/`, `collector/`, `worker/`, `probe/` là Python; `web/` là TypeScript. Phân chia ngôn ngữ **không** còn là điểm dừng. Nhưng **đường dẫn cụ thể** ở §3 và **lệnh** ở §8 vẫn PROVISIONAL cho tới khi có repo triển khai, và **framework chưa được chốt** trừ khi ADR-0006 nêu tên. Cần chọn framework/thư viện ⇒ DỪNG và raise CR; không tự chọn. |
| `SG-G5` | Card này chưa được phép code. Chỉ bắt đầu sau khi G5 pass **và** Owner ra lệnh bắt đầu bằng văn bản (SRC-PLAN §12; `precode/README.md` §7). |
| `SG-PC09` | File của PC09 (`acceptance/scenarios.yaml`, `acceptance/traceability.csv`, `precode/gates.yaml`, `precode/review.md`, `evidence/manifest.schema.json`, `evidence/index.json`) **cố ý không được pin hash** ở §0 vì PC09-FIX1 chạy song song với PC10-FIX1. Chúng được dẫn bằng **đường dẫn + SC id**. Trước khi code, đọc bản mới nhất của `acceptance/scenarios.yaml`; nếu oracle ở đó mâu thuẫn với §8 → DỪNG, raise CR, **không** sửa oracle. |
| `SG-DENY` | Nghĩa vụ default-deny áp dụng cho **mọi** card: mọi cạnh trong 36 `forbidden_edges` của `contracts/modules.yaml` chạm tới module của card phải bị từ chối bằng đúng mã của bảng ranh giới R5-01 (§5). Sai mã cũng là FAIL, không chỉ sai hành vi. Oracle: `SC49` + `acceptance/fixtures/boundary/a-default-deny-sweep-36-edges.json`. |
| `SG-HASH` | Trước khi ghi dòng code đầu tiên, chạy lại `sha256sum` trên mọi file ở §0. Lệch một hash ⇒ card `STALE`, DỪNG và xin baseline mới (`precode/change-control.md` §5). |
| `SG-CONTRACT` | Thiếu hợp đồng, hợp đồng mâu thuẫn nhau, hoặc oracle của fixture mâu thuẫn với hợp đồng ⇒ DỪNG và raise CR. **Không** sửa fixture, expectation hay hợp đồng để code pass (SRC-PLAN §15). |
| `SG-EDGE` | Cần một cạnh giao tiếp, bảng, secret hoặc capability không có trong §5 ⇒ DỪNG. Default deny (`contracts/modules.yaml.default_deny`); thêm cạnh là việc của change control, không phải của card. |

Khi dừng: báo Coordinator với trạng thái (`BLOCKED` / `BLOCKED_SCOPE` / `BLOCKED_DEPENDENCY` / `STALE_BASELINE`), đường dẫn chính xác và bằng chứng. **Không** sửa hợp đồng, fixture hay expectation để đi tiếp.

## §11. Dependencies

- `TC-canonical-identity-merge` — đã thi công (`evidence/handoffs/TC-canonical-identity-merge-handoff.md`), đang chờ audit độc lập; card này bàn giao metadata cho `server.app.identity.service`.
- `TC-ingest-idempotent-ack-lost` — đã thi công; `MOD-ingest-service` là caller của `research.fetch_work_metadata`.

## §12. Reviewer scope

Reviewer đọc `contracts/ops/collector-probe.md` §9 (CN-1…CN-6 và bảng KC §9.2), `contracts/ops/internet-boundary.md` §2–§3, `contracts/retry-policy.yaml` `research_connector_rate_limit`, và `contracts/ports.yaml` hai operation `research.*`. Ba câu hỏi bắt buộc: (1) có đường nào một chuỗi chưa chuẩn hóa hoặc do model sinh trở thành một lời gọi mạng không; (2) có con số nhịp gọi nào được viết cứng trong code thay vì đọc từ settings không; (3) khi cấu hình còn `null`, connector có thật sự từ chối khởi động, hay chỉ ghi log rồi chạy tiếp.

## §13. Expected evidence manifest

- **Manifest ID:** `EVM-TC-research-connector-metadata`
- **Vị trí:** `evidence/runs/TC-research-connector-metadata/manifest.json` (PROVISIONAL)
- **Schema:** `evidence/manifest.schema.json` — **đã tồn tại** (PC09). Không pin hash ở §0 vì PC09-FIX1 chạy song song; đọc bản mới nhất. Nó hiện thực 8 nhóm trường của SRC-PLAN §14.1: danh tính, baseline, môi trường, đầu vào, thực thi, kết quả, artifacts, giới hạn. Đăng ký run vào `evidence/index.json`.
- **Bắt buộc có:** `spec_sha256` = `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26`; `contract_hashes` copy nguyên văn từ §0; `review_type` ghi đúng self hay independent; mọi mục chưa chạy ghi `NOT_RUN`.

---

*Card sinh bởi PC10 (`PKT-PC10`, worker-W7) trên baseline FC-W3 epoch 3. Claim ceiling của chính card này: `DRAFT_FOR_REVIEW`.*
