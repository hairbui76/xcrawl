---
contract_id: CT-handoff-PC06-OQ03
version: 1.0.0
status: draft
document_type: HANDOFF
packet_id: PKT-PC06-FIX-OQ03
worker: worker-WAI
authority: "AUTH-COORD-OQ03 (cha AUTH-OWNER-20260908-06)"
lease: LEASE-PC06-OQ03
owner_role: requirements owner (PC00)
source_refs:
  - "…/scratchpad/packets/PKT-PC06-FIX-OQ03.md"
  - "…/scratchpad/packets/OWNER-DECISIONS-20260908-05.md mục 1"
  - "…/scratchpad/packets/PKT-PC07-FIX-TELEGRAM.md (lease chồng — §4)"
  - contracts/ai/providers.yaml §2, §4, §5, §6, §7
  - contracts/ai/tasks.yaml §2
  - contracts/data/entities.yaml ENT-provider-config
  - precode/adr/ADR-0010-secret-scoping-and-cli-isolation.md
requirement_refs: [REQ-OQ03, REQ-A5, REQ-D39, REQ-D40, REQ-D41, REQ-D43, REQ-D44, REQ-AC16]
decision_refs: [OD-20260908-05, OD-20260908-06, B13, ADR-0010]
producers: [worker-WAI]
consumers: [Coordinator, PC00, PC06]
dependencies: [precode/owner-decisions-06.md, contracts/ai/providers.yaml]
scope: >
  Handoff của packet PKT-PC06-FIX-OQ03. Trạng thái: PARTIAL — 2 trong 6 write target đã land, 3 bị
  BLOCKED_LEASE vì một Worker khác đang ghi cùng lúc, 1 (handoff này) là file cuối. Kèm §5: văn bản
  đúng-để-dán cho ba file bị chặn, để packet kế tiếp không phải làm lại việc.
verification: E0 SELF_VALIDATION — evidence/tools/e0_check.py, đọc-chỉ-đọc, PASS 25 / FAIL 0.
claim_ceiling: DRAFT_FOR_REVIEW
---

# HANDOFF — `PKT-PC06-FIX-OQ03` (worker-WAI, 2026-09-08)

## 1. Trạng thái: `PARTIAL` + `BLOCKED_LEASE`

| # | Target | Thao tác | Kết quả |
| --- | --- | --- | --- |
| 1 | `contracts/ai/providers.yaml` | MODIFY | ✅ **đã ghi** |
| 2 | `precode/owner-decisions-06.md` | CREATE | ✅ **đã ghi** |
| 3 | `evidence/handoffs/PC06-OQ03-handoff.md` | CREATE | ✅ file này |
| 4 | `precode/decision-register.md` | MODIFY | ❌ **`BLOCKED_LEASE`** — không chạm một byte |
| 5 | `precode/requirements.csv` (hàng `REQ-OQ03`) | MODIFY | ❌ **`BLOCKED_LEASE`** — không chạm một byte |
| 6 | `precode/change-control.md` | MODIFY | ❌ **`BLOCKED_LEASE`** — không chạm một byte |

## 2. Before / after

| Path | Before (sha256 · bytes) | After (sha256 · bytes) |
| --- | --- | --- |
| `contracts/ai/providers.yaml` | `462e5321543df781e53d62b54cdffc819765e56f4d2842c871b82fe068dc1bbc` · 19517 · v0.1.0 | `562a2694ab3bc8e64a3b222adac3e8e00eb0226e1345c39f531dee8ea204d9df` · 34957 · v0.2.0 |
| `precode/owner-decisions-06.md` | ABSENT | `7cfdcfde549e2528856b1e2f68afd336705d2ec96b381caa00a6504b11d85018` · 18551 |
| `evidence/handoffs/PC06-OQ03-handoff.md` | ABSENT | (file này — hash do Coordinator tính khi freeze) |
| `precode/decision-register.md` | `058621d0…` lúc 18:02Z | **KHÔNG ĐỔI BỞI TÔI**; trên đĩa lúc 18:19Z là `d98f0174…` (do worker-WT) |
| `precode/change-control.md` | `0b3d2bfa…` lúc 18:02Z | **KHÔNG ĐỔI BỞI TÔI**; trên đĩa lúc 18:19Z là `b22a9283…` (do worker-WT) |
| `precode/requirements.csv` | `d3e150e3…` lúc 18:02Z | **KHÔNG ĐỔI BỞI TÔI**; trên đĩa lúc 18:19Z là `36138c9f…` (do worker-WT) |

Delta của `contracts/ai/providers.yaml`, tối thiểu và có chủ đích: (a) `version: 0.1.0 → 0.2.0`;
(b) `requirement_refs` thêm `REQ-OQ03`, `decision_refs` thêm `OD-20260908-06`; (c) `scope` **thêm** một đoạn
cập nhật, **không xoá** câu cũ; (d) một khối mới `registered_adapters` chèn giữa §2 và §3. Không byte nào của
§3–§8 bị đụng.

## 3. Kết quả nội dung

### 3.1 `REQ-OQ03` — đã được Owner trả lời

Nguyên văn: **"sonnet 5 + opus 5 for summary"** → `summary` = `claude-opus-5`; `label` và
`direction_phrasing` = `claude-sonnet-5`; cả hai họ `api_key`. Cổng vào Giai đoạn 3 của
`docs/master-plan.md` §3 đòi *câu trả lời*, và câu trả lời đã có. Chi tiết + kiểm cách đọc
`direction_phrasing` ở `precode/owner-decisions-06.md` §2 và §2.1.

Một điểm Owner nên thấy: `label` là task khối lượng lớn nhất và `REQ-D40` khuyến nghị **model rẻ** cho nó;
lựa chọn này đặt nó lên model mạnh. `providers.yaml` §7 cho phép tường minh (D40 là khuyến nghị, không phải
ràng buộc), nên đây là **chi phí đã chọn**, không phải lỗi hợp đồng.

### 3.2 `REQ-A5` — `permitted_for_this_use`, có điều kiện

Bảy trích dẫn nguyên văn + URL + ngày đọc nằm ở `precode/owner-decisions-06.md` §3. Tóm tắt: Commercial ToS
(eff. 2025-06-17) áp cho *"Customer's use of Anthropic API keys"*, nhập Usage Policy vào hợp đồng, cho
*"Customer… owns its Outputs"* và cho dùng Services để *"power products and services"*; toàn bộ 82 gạch của
*Universal Usage Standards* (Usage Policy eff. 2025-09-15) **không** gạch nào cấm chạy tự động, chạy khối
lượng lớn, gắn nhãn/tóm tắt nội dung bên thứ ba, hay lưu và dùng lại output; Service Specific Terms
(eff. 2026-06-08) không thêm hạn chế cho Developer Platform. Hai điều kiện **thuộc về phía mình** và vẫn mở:
`TC-A5-01` (*"Customer… represents and warrants that it has all rights and permissions required to submit
Inputs"* — ta gửi văn bản bên thứ ba) và `TC-A5-02` (cấm dùng input/output để train model — hiện không kích
hoạt vì embedding là model local).

**Đây là `SELF_VALIDATION` của một Worker, không phải chữ ký của Owner** — `providers.yaml` §5 ghi `reviewer`
"đây là Owner" và *"PC06 KHÔNG đọc thay"*, trong khi `OD-20260908-05` mục 1 giao việc đọc cho một Worker.
`CR-PC06-OQ03-02` xin chốt điểm này.

### 3.3 Cô lập — `enabled: false`, và đó là kết luận của văn bản chứ không của sự thận trọng

Câu hỏi packet đặt ra: có mục nào trong `ISO-01..05` mang được `not_applicable` cho một adapter `api_key`
HTTP thuần để đi tới `enabled: true` mà không cần probe? **Không.** Ba chỗ trong văn bản trả lời, theo thứ tự
sức nặng:

1. **§4 `status_values` → `not_applicable`: *"Chỉ dùng cho họ `api_key` với các tính chất mà **kiến trúc đã
   loại bỏ**"***. `ISO-03` (network egress) và `ISO-05` (credential đúng provider/đúng task giữ lease) là
   những tính chất mà đường `api_key` **tạo ra**, không phải loại bỏ: nó là đường duy nhất gọi mạng tới
   endpoint nhà cung cấp (§1 `api_key`) và là đường duy nhất nhận credential (§1 `cli_acp` có
   `secret_ref = NULL`, REQ-D51; ADR-0010 điểm 1 nói secret theo task). Hai mục này nằm **ngoài** tập mà
   `not_applicable` phủ, với **bất kỳ** cách đọc nào của câu đó. Vì `unverified ⇒ enabled = false`, kết luận
   `enabled: false` **đã bị quyết định xong ngay tại đây**, không cần giải quyết phần mơ hồ còn lại.
2. **§4 `current_status_vi`: *"Ở giai đoạn Pre-code, mọi adapter có `isolation.* = unverified`… Không có
   ngoại lệ, vì chưa có probe nào chạy (E3 = `NOT_RUN`)"***. Câu này phủ nốt `ISO-01`/`02`/`04`. Có một lý do
   thứ hai độc lập với nó: `not_applicable` giả định một **kiến trúc đã tồn tại** để loại bỏ được một tính
   chất; ở Pre-code `MOD-ai-adapter` chưa có một dòng mã, nên cái "đã loại bỏ" mới là **dự định** — và §4
   `principle_vi` nói thẳng *"Một lời hứa… KHÔNG phải bằng chứng cô lập"*.
3. **ADR-0010 điểm 3: *"Không kiểm chứng được thì không bật"***. Cách kiểm `ISO-03` là ghi tập đích của một
   lần chạy; cách kiểm `ISO-05` là gọi `secret.issue_task_credential` cho một worker **không** giữ lease và
   thấy nó bị từ chối. Cả hai đòi một lần **chạy**; E3 = `NOT_RUN` và `secret.issue_task_credential` chưa có
   mã.

**Chỗ văn bản thật sự mơ hồ, nói ra thay vì giấu.** Với `ISO-01`/`ISO-02`, ADR-0010 điểm 2 khoanh yêu cầu
"tắt tool, tắt file, tắt mạng" cho **đường CLI/ACP**, và §1 chỉ đặt `isolation_required: true` dưới `cli_acp`.
Một người có thể lập luận rằng adapter `api_key` không có bề mặt tool nên hai mục đó là `not_applicable`.
Bản ghi này **không** đi theo lập luận ấy, vì hai lý do ở mục 2 trên, **và** vì nó không đổi được kết quả:
`ISO-03`/`ISO-05` vẫn `unverified`. Nếu Coordinator/Owner muốn chốt khác cho `ISO-01`/`ISO-02`, đó là một
quyết định hợp đồng (`CR-PC06-OQ03-01` chạm cùng vùng), **không** phải một cách đọc mà Worker được tự chọn.

**Điều gì sẽ đổi kết luận:** không phải một cách đọc khác, mà một lần chạy E3 quan sát được egress cộng một
denied-case thật cho `secret.issue_task_credential`.

## 4. `BLOCKED_LEASE` — vì sao ba file không bị chạm

`LEASE-PC06-OQ03` (packet này, dispatch 01:06 giờ Owner) và `LEASE-PC07-TELEGRAM`
(`PKT-PC07-FIX-TELEGRAM`, worker-WT, dispatch 01:01) **cùng liệt kê** `precode/decision-register.md`,
`precode/change-control.md`, `precode/requirements.csv`. `protocol.md` §2: *"default lease độc quyền toàn
physical path; chỉ runtime có range-lock đã kiểm chứng mới được chia vùng (bộ profiles này **không** bật
range-sharing)"* — nên "chỉ hàng `REQ-OQ03`" và "chỉ hàng `CR-PC07-04`" vẫn là hai lease **toàn file** chồng
nhau. `uniqueItems` của schema không bắt được overlap xuyên packet; §2 nói trước điều đó.

Quan sát (không suy đoán):

| Giờ UTC | `decision-register.md` | `change-control.md` | `requirements.csv` |
| --- | --- | --- | --- |
| 18:02Z | `058621d0…` (144860 B) | `0b3d2bfa…` (42312 B) | `d3e150e3…` |
| 18:12Z | `aaaff446…` (152698 B) | `0293be59…` (51153 B) | `d3e150e3…` |
| 18:15Z | `d98f0174…` | `b22a9283…` | `36138c9f…` |
| 18:19Z | `d98f0174…` | `b22a9283…` | `36138c9f…` |

Ba file đổi bytes hai lần trong mười ba phút; `precode/change-control.md` đã trỏ tới
`precode/decision-register.md` §8.14.1 (mục của worker-WT); `evidence/handoffs/PC07-TELEGRAM-handoff.md`
**chưa tồn tại** ⇒ writer kia chưa quiesce, chưa release. Ghi thêm vào đó lúc này là công thức của một lost
update: worker-WT đọc baseline của nó trước khi tôi ghi, và bản ghi sau cùng sẽ nuốt bản trước.

`worker.md` (*"Baseline drift → giữ nguyên quan sát, trả `STALE_BASELINE`, chờ packet mới"*, *"không tiếp
quản stale lease"*) và `protocol.md` §5 (*lease overlap ⇒ `BLOCKED_LEASE`; quiesce, xác minh, lease mới*) dẫn
tới cùng một hành động: **dừng trước khi ghi**, giữ nguyên quan sát, báo lên. Đó là việc đã làm. Đây cũng
chính là hình dạng mà `CR-PC06-OQ03-06` gửi Coordinator: hai lease không được chồng nhau, và cái sửa là một
packet mới với baseline mới **sau khi** worker-WT handoff.

## 5. Văn bản đúng-để-dán cho ba file bị chặn

Packet kế tiếp chỉ cần dán, sau khi **đọc lại baseline mới** (§8.14 của worker-WT đã tồn tại, nên mục dưới
đánh số **§8.15**; nếu worker-WT thêm §8.15 thì lùi một số).

### 5.1 `precode/decision-register.md`

**(a) §0 — thêm một hàng vào bảng nhãn, ngay dưới hàng `ACCEPTED (OD-20260907-04)`:**

```markdown
| `ACCEPTED (OD-20260908-06)` | Quyết định đã được Owner chấp nhận ở biên bản **vòng sáu** — xem `precode/owner-decisions-06.md` |
```

**(b) §5 — thay đúng một hàng của bảng "Câu hỏi còn mở":**

```markdown
| REQ-OQ03 | Provider và model cụ thể? | **ĐÃ TRẢ LỜI** (OD-20260908-06) — `summary` = Claude Opus 5 (`claude-opus-5`); `label` và `direction_phrasing` = Claude Sonnet 5 (`claude-sonnet-5`); cả hai họ `api_key` | Owner ✅ | — (cổng vào M3 được thỏa; **việc bật** adapter vẫn bị chặn bởi cô lập, xem §8.15) |
```

**(c) Thêm §8.15 vào cuối file:**

```markdown
### 8.15 Quyết định của `OD-20260908-06` (vòng sáu, 2026-09-08) — `REQ-OQ03` đã được trả lời

Biên bản vòng sáu — `precode/owner-decisions-06.md`, ghi dưới `AUTH-COORD-OQ03` (cha
`AUTH-OWNER-20260908-06`), evidence `session_017CTbS7F4oTr4ZtFYkhdabD` — làm **một** việc và làm hết việc đó:
trả lời `REQ-OQ03`. Nguyên văn câu trả lời của Owner: **"sonnet 5 + opus 5 for summary"**.

| # | Quyết định | Trạng thái | Ghi ở đâu |
| --- | --- | --- | --- |
| 1 | `summary` → Claude **Opus 5** (`claude-opus-5`); `label` và `direction_phrasing` → Claude **Sonnet 5** (`claude-sonnet-5`); cả hai họ `api_key` | `ACCEPTED (OD-20260908-06)` | `contracts/ai/providers.yaml` §2.1 (v0.2.0); `precode/owner-decisions-06.md` §2 |

**Cổng vào Giai đoạn 3 đòi một CÂU TRẢ LỜI, không đòi một adapter đã bật.** `docs/master-plan.md` §3 viết
*"Cổng vào: `REQ-OQ03` phải được Owner trả lời."* Câu trả lời đã có, nên cổng ấy được thỏa. Việc **gọi được
model** thì chưa: cả hai mục adapter mang `enabled: false`.

**`REQ-A5` cho Anthropic: `permitted_for_this_use`, có điều kiện — và có nguồn.** Một Worker đã đọc
`www.anthropic.com/legal/commercial-terms` (eff. 2025-06-17), `/legal/aup` (Usage Policy, eff. 2025-09-15) và
`/legal/service-specific-terms` (eff. 2026-06-08) ngày 2026-09-08, chỉ đọc, `WebFetch` GET, **không** một lời
gọi nào tới `api.anthropic.com`, **không** dùng API key. Bảy trích dẫn nguyên văn ở `owner-decisions-06.md`
§3. Không điều khoản nào cấm chạy tự động không người trực, chạy khối lượng lớn, gắn nhãn/tóm tắt nội dung
bên thứ ba, hay lưu và dùng lại output. Hai điều kiện còn mở **thuộc về phía mình**: quyền đối với Input của
bên thứ ba (*"Customer… represents and warrants that it has all rights and permissions required to submit
Inputs to the Services."*) và cấm dùng input/output để train model (hiện không kích hoạt).

**Vì sao cả hai adapter vẫn `enabled: false` — và vì sao đó không phải sự thận trọng.** `providers.yaml` §4
`status_values` chỉ cho `not_applicable` với *"các tính chất mà **kiến trúc đã loại bỏ**"*. `ISO-03` (network
egress) và `ISO-05` (credential đúng task giữ lease) là những tính chất đường `api_key` **tạo ra** — nó là
đường duy nhất gọi mạng ra endpoint nhà cung cấp và là đường duy nhất nhận credential (`cli_acp` có
`secret_ref = NULL`). Chúng không thuộc tập `not_applicable` phủ, nên `unverified`, nên `enabled = false`
theo chính §4. `ISO-01`/`02`/`04` cũng `unverified` theo §4 `current_status_vi` (*"Không có ngoại lệ, vì chưa
có probe nào chạy"*). Cách kiểm cả hai mục quyết định đều đòi một lần **chạy**: E3 = `NOT_RUN`
(`contracts/ops/cli-acp-probe.md`), và `secret.issue_task_credential` chưa có mã.

**Năm điều vòng sáu KHÔNG làm.** (a) **Không** bật adapter nào. (b) **Không** tạo hàng `ENT-provider-config`,
không chạm secret store. (c) **Không** mở allowlist fallback — §6 chỉ nhận adapter `enabled = true`.
(d) **Không** đổi `REQ-AC16`: hai adapter này là `api_key`, đường không-API-key vẫn phụ thuộc adapter
`cli_acp` và luật báo `BLOCKED` (không phải `FAIL`) giữ nguyên. (e) **Không** đóng finding nào.

**Một điểm chi phí Owner nên thấy, ghi ở đây vì nó không tự lộ ra.** `label` là task khối lượng lớn nhất
(mọi post/work) và `REQ-D40` khuyến nghị **model rẻ** cho nó; lựa chọn này đặt nó lên model mạnh.
`providers.yaml` §7 cho phép tường minh (*"REQ-D40 là khuyến nghị mặc định… không phải ràng buộc cứng"*), nên
đây là một chi phí **đã được chọn**, không phải một vi phạm. Chỗ để hạ chi phí về sau là `label`, không phải
`summary`.
```

### 5.2 `precode/requirements.csv` — thay đúng dòng 111

Before (nguyên văn):

```csv
"REQ-OQ03","SRC-SPEC§13.1#row-03","Provider và model cụ thể cho gắn nhãn và cho summary. Người dùng trả lời. Chặn M3","ĐX","P0","MVP","open-question","B13","PC06","Không có mặc định an toàn; giữ OWNER_DECISION_REQUIRED trong phạm vi bật provider"
```

After:

```csv
"REQ-OQ03","SRC-SPEC§13.1#row-03","Provider và model cụ thể cho gắn nhãn và cho summary. Người dùng trả lời. Chặn M3","XN","P0","MVP","open-question","","PC06","Answered OD-20260908-06: summary=claude-opus-5; label+direction_phrasing=claude-sonnet-5; ca hai ho api_key. Cong vao M3 duoc thoa. KHONG bat adapter nao: ca hai enabled=false vi ISO-03/ISO-05 chua kiem chung (E3 NOT_RUN) — xem contracts/ai/providers.yaml §2.1 va precode/decision-register.md §8.15"
```

Ba điểm cần Coordinator xác nhận trước khi dán: (1) `ĐX → XN` đúng tiền lệ bốn dòng D08/D09/D42/D50 mà
`OD-20260907-01` promote; (2) `blocked_by` bỏ `B13` vì B13 đã `RATIFIED`; (3) cột `notes` trong file này
không dùng dấu tiếng Việt có dấu ở nhiều dòng — bản trên viết không dấu cho an toàn CSV, sửa lại nếu quy ước
khác. `acceptance/traceability.csv` dòng `REQ-OQ03` (hiện `PARTIAL`, `E0`) **ngoài lease** — cần packet riêng.

### 5.3 `precode/change-control.md` — thêm vào §10

```yaml
cr_id: CR-PC06-OQ03-01
raised_by: worker-WAI (PKT-PC06-FIX-OQ03), dưới AUTH-COORD-OQ03 (cha AUTH-OWNER-20260908-06)
addressed_to: PC06 (chủ hợp đồng contracts/ai/providers.yaml)
status: OPEN
source_of_change: >
  Mâu thuẫn nội bộ, phát hiện khi điền hai mục adapter thật đầu tiên theo template §2.
before: >
  contracts/ai/providers.yaml §4 `isolation.required_properties` liệt kê NĂM tính chất ISO-01..ISO-05,
  trong đó ISO-04 "Không gửi Telegram, không đổi recipient" và ISO-05 "Chỉ nhận credential của ĐÚNG
  provider cho task đang giữ lease". Nhưng §2 `example_entry.isolation` chỉ có bốn khoá:
  `{tools_disabled, filesystem_scope, network_egress, verification_method}` — và §2 required_fields ghi
  `{field: isolation, type: object, note_vi: "§4 — mọi trường con bắt buộc."}`.
after: >
  Thêm hai khoá trạng thái vào object `isolation` của template và của mọi mục đã đăng ký:
  `telegram_egress` (ISO-04) và `credential_scope` (ISO-05), cùng miền giá trị
  `verified | unverified | not_applicable`. Hai mục ở §2.1 hiện giữ đúng hình dạng bốn khoá của template
  và ghi khoảng trống ở `isolation_determination_vi.template_gap_vi`; khi template đổi, hai mục phải được
  điền `unverified` cho cả hai khoá mới.
reason: >
  "Mọi trường con bắt buộc" không thể thoả cho hai tính chất KHÔNG CÓ Ô ĐỂ GHI. Với họ api_key, ISO-05
  chính là tính chất quyết định (ADR-0010 điểm 1: credential theo task) — để nó không có chỗ ghi nghĩa là
  cái chặn `enabled` phải nằm trong prose thay vì trong một trường kiểm được bằng máy.
affected:
  requirements: [REQ-A5, REQ-AC17]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0 — thêm khoá bắt buộc vào một object đã có ví dụ chuẩn ⇒ major khi áp
  modules: [MOD-ai-adapter, MOD-settings-service]
  fixtures: []
  evidence: []
migration: >
  Chưa có mã và chưa có hàng dữ liệu nào; không cần chuyển đổi. Hai mục §2.1 đang enabled=false nên việc
  thêm hai ô không đổi cổng nào.
---
cr_id: CR-PC06-OQ03-02
raised_by: worker-WAI (PKT-PC06-FIX-OQ03)
addressed_to: PC06 + Owner
status: OWNER_DECISION_REQUIRED
source_of_change: >
  Quyết định Owner (OD-20260908-05 mục 1) lệch với câu chữ hợp đồng.
before: >
  contracts/ai/providers.yaml §5 `terms_check.fields` ghi `{field: reviewer, … note_vi: "Ai đã đọc. Ở MVP
  một người dùng, đây là Owner."}` và §5 `what_pc06_must_not_do_vi`: "PC06 KHÔNG đọc thay và KHÔNG đoán.
  Việc này là công việc tay, không tự động hoá được".
after: >
  Chốt một trong hai: (a) `reviewer` được phép là một Worker chạy dưới authority của Owner, và §5 ghi thêm
  rằng bản ghi ấy cần Owner ký xác nhận trước khi bất kỳ adapter nào `enabled = true`; hoặc (b) giữ nguyên
  §5, và lần đọc ở `precode/owner-decisions-06.md` §3 được coi là TÀI LIỆU CHUẨN BỊ, `terms_check.outcome`
  của hai mục §2.1 hạ về `not_read` cho tới khi Owner tự đọc.
reason: >
  OD-20260908-05 mục 1 nói nguyên văn "a Worker still does that, separately, before any adapter is set
  enabled = true". Hai câu không thể cùng đúng. Hiện `enabled = false` nên không cổng nào bị đi vòng, nhưng
  câu trả lời phải có TRƯỚC lần bật đầu tiên, vì entities.yaml
  `ck_provider_config_terms_before_enable` biến nó thành một CHECK chạy được.
affected:
  requirements: [REQ-A5]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0
    - contracts/data/entities.yaml    # ENT-provider-config.terms_check_by
  modules: [MOD-settings-service]
  fixtures: []
  evidence: []
migration: "Không cần; chưa có hàng provider_config nào."
---
cr_id: CR-PC06-OQ03-03
raised_by: worker-WAI (PKT-PC06-FIX-OQ03)
addressed_to: PC06 + PC01
status: OPEN
source_of_change: "Nguồn ngoài không đọc được trong quyền mạng được cấp."
before: >
  contracts/ai/providers.yaml §1 `api_key.usage_reporting: exact` với chú thích "Token count thật
  (SRC-SPEC §10.2)". Hai mục §2.1 khai `usage_reporting: exact`.
after: >
  Ghi rõ trong §1 hoặc §2.1 rằng `exact` áp cho SỐ TOKEN, còn `cost_micro_usd` là giá trị SUY RA từ bảng
  giá công bố của nhà cung cấp: khi chưa có bảng giá có nguồn, `cost_micro_usd` phải đi đường `unknown`
  (I14 cấm ghi 0), kể cả khi tokens_in/tokens_out đã chính xác.
reason: >
  API trả `usage.input_tokens` / `output_tokens` nhưng KHÔNG trả tiền. Bảng giá của Anthropic nằm sau một
  redirect ra ngoài allowlist (www.anthropic.com/pricing → claude.com/pricing), nên hiện không có con số
  giá nào có nguồn. Một adapter khai `exact` rồi ghi `cost_micro_usd = 0` sẽ vi phạm I14 trong khi vẫn
  "đúng" theo câu chữ hiện tại.
affected:
  requirements: [REQ-D44]
  contracts:
    - contracts/ai/providers.yaml     # 0.2.0
    - contracts/data/entities.yaml    # ENT-analysis-attempt usage
  modules: [MOD-ai-adapter]
  fixtures: []
  evidence: []
migration: "Không cần; chưa có mã."
```

Ba CR còn lại (`CR-PC06-OQ03-04` thiếu `precode/owner-decisions-05.md`; `CR-PC06-OQ03-05` xin mở host
`platform.claude.com` / `claude.com` cho tài liệu API và bảng giá; `CR-PC06-OQ03-06` hai lease chồng nhau;
`CR-PC06-OQ03-07` `entities.yaml` `terms_check_note_vi` nay sai một phần) là **CR gửi Coordinator/Owner**,
không phải sửa hợp đồng — bảng một dòng ở `precode/owner-decisions-06.md` §7 là bản ghi của chúng.

## 6. Evidence

| Trường | Giá trị |
| --- | --- |
| `evidence_id` | `EV-PC06-OQ03-01` |
| `producer` | `worker-WAI` |
| `kind` | **`SELF_VALIDATION`** — không phải `COORDINATOR_CHECK`, không phải `INDEPENDENT_AUDIT` |
| `command` | `PYTHONDONTWRITEBYTECODE=1 python3 /mnt/virtual/repo/xcrawl/evidence/tools/e0_check.py --repo /mnt/virtual/repo/xcrawl` (chạy từ scratch dir, không ghi vào repo) |
| `started/ended` | 2026-09-07T18:18Z / 2026-09-07T18:19Z UTC (= 2026-09-08 giờ Owner) |
| `oracle` | Không check nào có status FAIL |
| `observed` | **`TOTAL: 25 checks — PASS 25 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0`**, exit code **0** |
| `limitations` | (1) E0 chứng minh nhất quán nội bộ của tập được kiểm, **không** chứng minh runtime, không chứng minh điều khoản, không chứng minh cô lập. (2) Nó chạy trên cây thư mục lúc 18:19Z, **trong khi worker-WT đang ghi** ba file khác — kết quả PASS này không nói gì về bytes mà worker-WT ghi sau đó. (3) Không có E1–E4; E3 (probe cô lập) vẫn `NOT_RUN`. |

| Trường | Giá trị |
| --- | --- |
| `evidence_id` | `EV-PC06-OQ03-02` (REQ-A5) |
| `producer` | `worker-WAI` |
| `kind` | **`SELF_VALIDATION`** |
| `procedure` | `WebFetch` GET trên 5 URL: `/legal/aup` (×2 prompt), `/legal/commercial-terms` (×2 prompt), `/legal/service-specific-terms`, `docs.anthropic.com/en/api/versioning` (**301, dừng**), `www.anthropic.com/pricing` (**301, dừng**), `docs.anthropic.com/…/models/overview` (**301, dừng**) |
| `started/ended` | ≈2026-09-07T18:05Z / 18:11Z UTC |
| `oracle` | Mỗi kết luận phải có URL + ngày đọc + trích dẫn nguyên văn |
| `observed` | 7 dữ kiện có nguồn (`owner-decisions-06.md` §3); 3 URL bị `BLOCKED_SCOPE` vì redirect ra ngoài allowlist |
| `limitations` | Nội dung qua `WebFetch` (markdown + trích bằng model), không phải HTML thô do người đọc mắt. Điều khoản có ngày hiệu lực và hết đúng khi nhà cung cấp đổi. **Không** có lời gọi tới `api.anthropic.com`, **không** dùng API key, **không** có inference nào. |

## 7. Unresolved / next actor

1. **`BLOCKED_LEASE` trên ba file** — cần packet mới, baseline mới, sau khi `worker-WT` handoff. Văn bản
   đúng-để-dán ở §5. **Next actor: Coordinator.**
2. **Bảy CR** ở `precode/owner-decisions-06.md` §7; `CR-PC06-OQ03-02` cần **Owner**.
3. **`REQ-A5` chưa được Owner ký xác nhận**; hai điều kiện `TC-A5-01`/`TC-A5-02` còn mở.
4. **Cô lập chưa kiểm chứng** — cần E3; `enabled = false` giữ nguyên tới lúc đó.
5. **File ngoài lease chưa cập nhật:** `acceptance/traceability.csv` (dòng `REQ-OQ03`),
   `precode/gates.yaml`, `precode/README.md`, `precode/owner-decision-request.md` (khối "VẪN CHỜ" nay rỗng),
   `precode/baseline.json`, `agent_profile/registry.json`, `docs/master-plan.md` §3.
6. **Mọi card pin hash `contracts/ai/providers.yaml` nay `STALE`** (`change-control.md` §5: "hash là hash") —
   ít nhất `agent-tasks/TC-analysis-adapter-validation.md`. Coordinator pin lại; `STALE` nghĩa là pin lại,
   không phải `FAIL`.

`lease_released_at`: 2026-09-07T18:20Z UTC (2026-09-08 giờ Owner), ngay sau khi file này được ghi. Sau mốc
này `worker-WAI` không ghi thêm gì, kể cả sửa lỗi đánh máy.
