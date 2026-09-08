---
handoff_id: P0-skeleton-handoff
packet_id: PKT-P0-SKELETON
worker_principal: worker-WS
authority_id: AUTH-COORD-P0-SKELETON
parent_authority: AUTH-OWNER-20260907-03
lease_id: LEASE-P0-SKELETON-e1
decision_refs: [OD-20260907-01, OD-20260907-02, ADR-0006, ADR-0011]
invariant_refs: []
scenario_refs: []
requirement_refs: []
next_actor: Coordinator
lease_released_at: 2026-09-07T09:55Z
---

# HANDOFF — PKT-P0-SKELETON (Giai đoạn 0: bộ khung repo, gói hợp đồng sinh ra, CI)

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| `packet_id` | `PKT-P0-SKELETON` |
| `worker_principal` | `worker-WS` |
| `authority_id` | `AUTH-COORD-P0-SKELETON` (parent `AUTH-OWNER-20260907-03`, bản ghi `OD-20260907-02`) |
| `lease_id` | `LEASE-P0-SKELETON-e1` (exclusive, message-tracked) |
| `enforcement_mode` | code mutation dưới lease theo `OD-20260907-02` mục 3 — **không** có guard ở mức OS |
| **`status`** | **`DONE_WITH_CONCERNS`** |
| `completion_claim` | `IMPLEMENTATION_VERIFIED` **chỉ cho chính bộ khung** (boot, lint, type, test, cửa sinh-lại đều chạy thật ở máy này). **Không** claim gì về hành vi sản phẩm: chưa có hành vi nào |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T09:55Z |

**Vì sao `DONE_WITH_CONCERNS` chứ không phải `DONE`.** Mục 4 của checklist — `verify_cards.py`
xanh — **FAIL**, và nó fail vì một lý do nằm ngoài packet này: **ba file mà cả 18 card đã pin
đã bị sửa** trong lúc gói này chạy, bởi gói phê chuẩn `OD-20260907-02` chạy song song. 54
dòng pin (3 file × 18 card) không còn khớp. Xem `CR-P0-01`. Tôi **không** sửa card và
**không** sửa ba file đó: cả hai đều nằm ngoài write set, và làm vậy sẽ là tự chữa một tín
hiệu STALE thật.

**Vì sao không phải `STALE_BASELINE`.** Hai nguồn đã pin ở baseline §2 (`SRC-SPEC`,
`SRC-PLAN`) **không đổi** — kiểm ở đầu phiên và lại trước handoff, cả hai lần khớp. Stop
gate hàng đầu của baseline §6 không trigger.

**Vì sao không phải `BLOCKED_SCOPE`.** Không file nào bị pin bởi card cần thay đổi để gói
này hoàn thành. `precode/README.md` được sửa đúng **một dòng** như packet cho phép, và
`precode/README.md` **không** nằm trong bảng pin của bất kỳ card nào.

## 2. Changes — mọi file đã tạo

Tất cả là `CREATE`, baseline `ABSENT`, trừ hai dòng `MODIFY` ở cuối bảng.
**81 file mới, 1 073 841 byte.**

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `pyproject.toml` | CREATE | ABSENT | `dd454c42730bf3b5f0d09389fcc0853e61f100804b0873c150137c687eb3ba80` | 2763 |
| `uv.lock` | CREATE | ABSENT | `de2dccd2314abd1aec395a965adc53c019d06ad2d8e9aa004bf77692497b872d` | 192045 |
| `.python-version` | CREATE | ABSENT | `7b55f8e67b5623c4bef3fa691288da9437d79d3aba156de48d481db32ac7d16d` | 5 |
| `.gitignore` | CREATE | ABSENT | `7269891008827216ef49d2e5c34e986eb6318fef44bbe59b2ef13ceb2e1aac59` | 729 |
| `.pre-commit-config.yaml` | CREATE | ABSENT | `f9009c8cab5f11d83924cd913f95a14498796e9f7fee4a459bfcadcde37c7593` | 1843 |
| `Makefile` | CREATE | ABSENT | `8968aafbba824d3c3dbdda20ae478d85f38852e9174b7512d67230ac468dc100` | 2252 |
| `README.md` | CREATE | ABSENT | `7bcd44bd8db00ddd9deb796cb5a4d40e306f9a75b9a6cc6572bf89bc11805c75` | 6195 |
| `.github/workflows/e0.yml` | CREATE | ABSENT | `5ecf9e1a4dd911afe8ec0537ac76c545066b7a5b3d2a1c574e1aa41b38f708e3` | 1685 |
| `.github/workflows/openapi.yml` | CREATE | ABSENT | `dbe50b9ae4d7a8fb2e06e5caa0782f7ed86b97dc6813976ba89451f12d29250b` | 1330 |
| `.github/workflows/python.yml` | CREATE | ABSENT | `22b84e265c54f9700c784f4344a3df60208c1ef2274cea76d29f0df47a0455ed` | 1331 |
| `.github/workflows/web.yml` | CREATE | ABSENT | `676be4d52f4dcaeaf498382da3e97b3ce7eb68385622f5c06f463bf213cebe32` | 1093 |
| `evidence/tools/verify_cards.py` | CREATE | ABSENT | `7b344863d2d108aea965bbed208f558eca4bb560534f8933421f7e012dc976dd` | 20382 |
| `tests/README.md` | CREATE | ABSENT | `41e69ae796b52ae859f7c18a2d2cfcad3c0415cfa5e5a64bff0b9eaa983966cc` | 4891 |
| `tests/conftest.py` | CREATE | ABSENT | `8a5ebdfa182007056233f2e24ca8126cd1f5a4fd7b54c026cac7b593d886d3cd` | 6674 |
| `tests/contract/.gitkeep` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `tests/integration/.gitkeep` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `probe/README.md` | CREATE | ABSENT | `7495be45e780279b271839d40e631c137dc19f9df393695398e8289995816893` | 1885 |
| `probe/__init__.py` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `collector/app/__init__.py` | CREATE | ABSENT | `45458e7c3a67e8dba0d077307dd55be3f3f048f5717bb7ed8a12f9bcca7dd280` | 401 |
| `collector/app/main.py` | CREATE | ABSENT | `addef73dfcd10d43e3c5879dedad3414713c032cdea59c55e25cf49361c59651` | 2715 |
| `collector/__init__.py` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `collector/pyproject.toml` | CREATE | ABSENT | `34fd098fa1b1cb8436e783d197fd5b7b80ba066573d1a8ce38b940482e5d4758` | 716 |
| `collector/tests/__init__.py` | CREATE | ABSENT | `7967c5edc038f4113cd11c40f8a333a6065aab7002ec9105be4541fd15236de7` | 206 |
| `collector/tests/test_smoke.py` | CREATE | ABSENT | `3791c67c83259151a5c0a00cb410b688e8d11176efb12eb6ed428ff630ce33fe` | 1686 |
| `server/alembic.ini` | CREATE | ABSENT | `21f5459221b29f7170decb953c3fb7ad5c18f30e350f3faa52f0996038ad7139` | 1023 |
| `server/app/db/engine.py` | CREATE | ABSENT | `ebc1be75188dd9adfd8580ff56d95f116e9e5789b5f96aef69a86a87454a1540` | 3690 |
| `server/app/db/__init__.py` | CREATE | ABSENT | `93eaff672198abc74a9ef840334106c4787f4d151c1bd45920d50f1fb77cafa7` | 447 |
| `server/app/__init__.py` | CREATE | ABSENT | `88ac779fc38fbe89a4b1ae12585100eebdff1e7ac1dc999aecbe27d469d0372f` | 295 |
| `server/app/main.py` | CREATE | ABSENT | `36a63c4855467c68bbe6d71fa52164ba7ad5b961bef4593270f8975b4506f71e` | 4018 |
| `server/__init__.py` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `server/migrations/env.py` | CREATE | ABSENT | `5173c4028ac81842050eccc7cc5dd184c9b9f2b9a8eada47321a3736b197490a` | 2432 |
| `server/migrations/script.py.mako` | CREATE | ABSENT | `bddcf5ef550a1e7bdd3e5c84032c2527df7809ff7bfb737babfd3509d8058532` | 644 |
| `server/migrations/versions/0001_initial_empty_baseline.py` | CREATE | ABSENT | `c343348a5778cc4e2c3a0cfdfd18cd645fd18cb1c6d4e4d6bc3c480505aa43b3` | 842 |
| `server/pyproject.toml` | CREATE | ABSENT | `e38a1d0d7d4bd7c747aaa1a8f5c97b0cd2f42fbd308eec160524d8d79617fb24` | 1135 |
| `server/tests/__init__.py` | CREATE | ABSENT | `7d8fe0843bf317bb9fd50aa76860079bed2a6566bf9ad85f0b5ea19808527f54` | 203 |
| `server/tests/test_smoke.py` | CREATE | ABSENT | `03c3e4fc8b3355e7c295fe2baace8ba49e760c0aeb54509a656925a69f8d0cf6` | 3693 |
| `shared/rr_contracts/generate.py` | CREATE | ABSENT | `5ae97048a4374e87f5937d00d20fcc84cb710d21e68074301efd381459038037` | 23357 |
| `shared/rr_contracts/pyproject.toml` | CREATE | ABSENT | `58346cef43fbb84819baafb6b49874de96fb22c3a5ee909394b07b326f8bf95a` | 774 |
| `shared/rr_contracts/rr_contracts/generated/constants.py` | CREATE | ABSENT | `be176854b76734dae4adefb82e461ca29a9ebe565a6a6e25d4491b94812be2cd` | 1490 |
| `shared/rr_contracts/rr_contracts/generated/errors.py` | CREATE | ABSENT | `4325bf23d7a2d989ab78346609292de551675bc04cdb3b3e290190d4ffef14eb` | 7203 |
| `shared/rr_contracts/rr_contracts/generated/GENERATED_FROM.json` | CREATE | ABSENT | `ed76aefc67940671ff34506ec05d5609010b8bdfe3d85131c9e7c290c9de218a` | 3191 |
| `shared/rr_contracts/rr_contracts/generated/__init__.py` | CREATE | ABSENT | `d64b1795c4abe891998704985a43d8a8563efe859563ebe2aeb3382fb91f1f4b` | 3535 |
| `shared/rr_contracts/rr_contracts/generated/models/analysis_result.py` | CREATE | ABSENT | `e3c20aff795d406a6ef2416b6d1499f04ed3ea7e53cf745fdfb3ed137c2811d8` | 12491 |
| `shared/rr_contracts/rr_contracts/generated/models/ingest_batch.py` | CREATE | ABSENT | `fbb1046bf9e681bde0c5fa8437c552dad5bad1a24e5d521e65127d058a74373d` | 10097 |
| `shared/rr_contracts/rr_contracts/generated/models/ingest_receipt.py` | CREATE | ABSENT | `9572bd0f934dee458e2b1131a15caa08e4f0d0d790fa0ce7f5a8577d22a34147` | 16839 |
| `shared/rr_contracts/rr_contracts/generated/models/__init__.py` | CREATE | ABSENT | `77c9c9bb55031ef5af5893fcc02dea859caf9c592b0a6fd68a3804acd93c9f2b` | 2385 |
| `shared/rr_contracts/rr_contracts/generated/models/report.py` | CREATE | ABSENT | `e25d5349fcce0b6081cb48739b5397a6931e5bf80c062ed48f287df3ec13cfcc` | 26573 |
| `shared/rr_contracts/rr_contracts/generated/models/saved_snapshot.py` | CREATE | ABSENT | `c2ca3458b1ee47448e001d4e12a9a85b8d436fa358f089bbf1724e4ee83330d7` | 12165 |
| `shared/rr_contracts/rr_contracts/generated/models/target.py` | CREATE | ABSENT | `c95ec978d1ce832e61cf0bea23191b0fa304884a7e627a69803b6adb5a21a91e` | 7697 |
| `shared/rr_contracts/rr_contracts/generated/models/worker_assignment.py` | CREATE | ABSENT | `997c39f720a3240851adb5c708acc0aa6702b4fa3eb335ad215877d61ce9d953` | 22465 |
| `shared/rr_contracts/rr_contracts/generated/operations.py` | CREATE | ABSENT | `9342f92b1907d068f12f9e772c246cabf4bd1749c2fdf6f39b72b631da677d13` | 24028 |
| `shared/rr_contracts/rr_contracts/generated/states.py` | CREATE | ABSENT | `c84b3e3e5616509b593ceb49460e1c6fd3c18dbe07febf80f9fe60f4a13fc45d` | 6708 |
| `shared/rr_contracts/rr_contracts/__init__.py` | CREATE | ABSENT | `87c6b6ee6814e022b9879fb26e81b9a1fe1c684ca6595a228d36cd2892210a33` | 737 |
| `shared/rr_contracts/rr_contracts/py.typed` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `shared/rr_contracts/tests/test_generated_matches_contracts.py` | CREATE | ABSENT | `9ef2d20381cf16769d5967f16577e2f214fb9b6030996ca3405f383ff4c36264` | 3989 |
| `worker/app/__init__.py` | CREATE | ABSENT | `a076b4ef32d6c3aa3ac530b297c649799e97e227b5e6ce6dece400f66e6375b7` | 462 |
| `worker/app/main.py` | CREATE | ABSENT | `66221b8eeeb50766aadc8af415402336bff1d4b2d9a6ba945ba94de9cb7267c0` | 1938 |
| `worker/__init__.py` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `worker/pyproject.toml` | CREATE | ABSENT | `64995eabbc5cfd68b649f996edd2bb00a7e607196fe423aef282c49a4008ab2d` | 684 |
| `worker/tests/__init__.py` | CREATE | ABSENT | `fdc5bc42e9761a9038fa850b8dde74b029512f6dc14d8c7be3d13a49ccd5e879` | 203 |
| `worker/tests/test_smoke.py` | CREATE | ABSENT | `566879f35f1e73da2dfa7dd6e4ad8cb58e51f5bd74032a2194545ae00758234c` | 872 |
| `web/eslint.config.js` | CREATE | ABSENT | `63a35b0c382ac2e2ece6a7c84dabb6fab23f5c89df6f6137d0d639cd16ce8d8a` | 1042 |
| `web/index.html` | CREATE | ABSENT | `619f195f2b40001b8997942e077bf54829fae311e992ab77a1855c9fee54fde8` | 301 |
| `web/package.json` | CREATE | ABSENT | `40630e3a05f69de74be559df0489031da431d44482dc8c08c28670faf14cc57e` | 1340 |
| `web/package-lock.json` | CREATE | ABSENT | `4d151319d06d07ef9fc9855059d63fb7a40050ea691e83658607b1901f487ae1` | 170155 |
| `web/.prettierignore` | CREATE | ABSENT | `eb4905682e560a7493d0f6303451b883255fec07de812812e8f727dd5981aa1a` | 100 |
| `web/.prettierrc` | CREATE | ABSENT | `1ed256b071c0aacc1dfa91e5968b58c111e645a2c1c98b3be1d2cd64d0bca21c` | 89 |
| `web/scripts/generate.mjs` | CREATE | ABSENT | `7a1ad0b60156cbb02af147add312cab60ae87a473d97a2bf04c1e3ab9bb8b532` | 5961 |
| `web/src/App.test.tsx` | CREATE | ABSENT | `b2b29e2bf42083fe4f95cfb7190d19e6ecd26880f0aa101df992abdf25454073` | 1078 |
| `web/src/App.tsx` | CREATE | ABSENT | `f6a3a9e78b3d8a745726c550ca66c08ba1db9f982b9758986f45e684075793b6` | 2480 |
| `web/src/generated/GENERATED_FROM.json` | CREATE | ABSENT | `cc6fa45b0a1bb61ff4dd336f1cdfdf8055795ad71ce60f8d0e1a2c0978155e19` | 505 |
| `web/src/generated/openapi.d.ts` | CREATE | ABSENT | `0885e55f5f659044fe7b8f4bd146f13d9c4e48c716169e06d835f87dfd31ccaf` | 424259 |
| `web/src/lib/api.ts` | CREATE | ABSENT | `a2db648ed78c32d9cedfe34276c4f350986c8a7928d5308bcbf02684a1320669` | 2752 |
| `web/src/main.tsx` | CREATE | ABSENT | `a06bb3102fd5f30e05300ed0c9166b6c84f0a54601227b88eac924b298fd0912` | 1017 |
| `web/src/routes/.gitkeep` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `web/src/views/.gitkeep` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `web/tests/contract/generatedClient.test.ts` | CREATE | ABSENT | `b8ad71c69906262f8d574b6442be95a57b3620839ba3c2366c1d9de71e3ce839` | 2025 |
| `web/tests/integration/.gitkeep` | CREATE | ABSENT | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 0 |
| `web/tests/setup.ts` | CREATE | ABSENT | `d5a061f9af36e7bd65018554c0f8d371f35b26e3f16f801d82a4b1171b7e9bc7` | 110 |
| `web/tsconfig.json` | CREATE | ABSENT | `872903a085cf83e0f98c3764e916d94be60c496a109ec8c8353bd6d4141f977d` | 704 |
| `web/vite.config.ts` | CREATE | ABSENT | `62dd840e42955392d4f6dba691bf9e1b88978ebf0b2eef6c3675d8ae48827b7e` | 791 |

| `precode/README.md` | MODIFY | `7231737dc7cbb8812406580c0b38e7cf83912667b63afb780ad9d4654aee720a` (bản PC10 gốc; file đã bị gói khác sửa trước tôi — xem ghi chú) | *(một dòng thêm vào bảng §2: "Bộ khung triển khai")* | +900 |
| `evidence/handoffs/P0-skeleton-handoff.md` | CREATE | ABSENT | *(chính file này)* | — |

> **Ghi chú về `precode/README.md`.** File này đã ở trạng thái `M` trong `git status` **trước
> khi** tôi chạm vào nó, do gói phê chuẩn `OD-20260907-02` chạy song song. Tôi chỉ **chèn một
> hàng** vào bảng §2 và không sửa dòng nào khác. Hash "before" ở trên là hash PC10 công bố ở
> handoff của họ, **không** phải nội dung ngay trước lần ghi của tôi — tôi không có bản chụp
> đó và không muốn khai một con số mình không đo được.

### 2.1 Năm file `.gitkeep`

`tests/contract/`, `tests/integration/`, `web/src/routes/`, `web/src/views/`,
`web/tests/integration/` là thư mục **rỗng** ở Giai đoạn 0 — chúng chỉ được lấp bởi card
Giai đoạn 1+. Git không theo dõi thư mục rỗng, nên không có `.gitkeep` thì cây thư mục mà
`G5-X4` yêu cầu sẽ **biến mất ngay ở lần clone đầu tiên**. Năm file rỗng này nằm ngoài chữ
của write set nhưng nằm trong mục đích của nó ("dựng bảy cây thư mục"); tôi ghi lại đây thay
vì lặng lẽ thêm.

## 3. Source baseline đã dựa vào

| Ref | Path | SHA-256 | Kiểm |
| --- | --- | --- | --- |
| SRC-PLAN | `research-radar-pre-code-plan.md` | `f65bb04657f30f1dffe9c96f2667ed9ca1bb1d9363cca3d857abb15034707f40` | khớp ở đầu phiên **và** trước handoff |
| SRC-SPEC | `research-radar-spec.md` | `d35e1f2daab30e7ab36969ecd9b9b0f227d8ab70fbf55482af47c4a1405e0e26` | khớp ở đầu phiên **và** trước handoff |

Read set khác đã đọc: `precode/adr/ADR-0011-frameworks-and-toolchain.md` (đọc **hai** bản —
xem `CR-P0-01`), `agent-tasks/README.md` §5 và §5.3, `docs/master-plan.md` §1–§3,
`contracts/http/openapi.yaml`, `contracts/schemas/*.json` (7 file),
`contracts/errors.yaml`, `contracts/ports.yaml`, `contracts/state/*.yaml` (5 file),
`contracts/capabilities.yaml`, `contracts/ui/screens.yaml`, `evidence/tools/e0_check.py`,
`evidence/tools/README.md`, `precode/README.md`, `agent_profile/worker.md`, 18 card
`agent-tasks/TC-*.md`.

## 4. Môi trường

| Công cụ | Phiên bản |
| --- | --- |
| `uv` | 0.12.9 (x86_64-unknown-linux-gnu) |
| Python | 3.12.3 (CPython, `/usr/bin/python3.12`) |
| Node | v22.23.2 |
| npm | 10.9.8 |
| `datamodel-code-generator` | 0.26.5 (từ `uv.lock`) |
| `openapi-spec-validator` | 0.7.x (từ `uv.lock`) |
| `openapi-typescript` | 7.9.x (từ `web/package-lock.json`) |
| `ruff` | 0.6.9 · `mypy` 1.x · `pytest` 8.4.2 |
| `vite` | 7.x · `vitest` 3.x · `eslint` 9.x · `typescript` 5.9.x |

Lock: `uv.lock` sha256 `de2dccd2314abd1aec395a965adc53c019d06ad2d8e9aa004bf77692497b872d`
(192 045 B, 121 gói resolve, 75 gói cài).
`web/package-lock.json` sha256 `4d151319d06d07ef9fc9855059d63fb7a40050ea691e83658607b1901f487ae1`
(170 155 B, 297 gói). `npm audit`: **0 vulnerabilities** — xem `EV-P0-09`.

**Cài từ mạng** (được `OD-20260907-02` mục 4 cho phép): PyPI qua `uv`, npm registry qua
`npm`. **Không** tải model, **không** cài trình duyệt, **không** gọi X / Telegram / provider
AI. `sentence-transformers` được **khai** ở `server/pyproject.toml` nhóm extra `embedding`
và **không** được cài (nó kéo PyTorch, và model cụ thể còn là câu hỏi chưa trả lời).
`playwright` (Python) và `@playwright/test` (npm) được cài như thư viện; **`playwright
install` chưa từng chạy** — không có binary trình duyệt nào trong repo hay trong môi trường.

## 5. Evidence records — tất cả `SELF_VALIDATION`, mức E0/E1

Mọi lệnh chạy ở `/mnt/virtual/repo/xcrawl` với `PYTHONDONTWRITEBYTECODE=1`. Không lệnh nào
chạm mạng ngoài registry gói. Không có lượt chạy nào bị bỏ qua rồi khai là PASS: mục nào
không chạy được ghi `NOT_RUN`.

### EV-P0-01 — `uv sync --all-packages --frozen`

| Trường | Giá trị |
| --- | --- |
| `command` | `uv sync --all-packages --frozen` |
| `started / ended` | 2026-09-07T09:41:49Z / 2026-09-07T09:41:49Z (0 s; lần cài đầu tiên mất 13 s) |
| `oracle` | lockfile đủ để dựng môi trường mà **không** phải resolve lại |
| `observed` | `Checked 75 packages`; `uv lock --check` cũng exit 0 (`Resolved 121 packages`) |
| `exit_code` | **0** · `status` **PASS** |
| `limitations` | Chứng minh lock nhất quán với `pyproject.toml`, không chứng minh phiên bản nào là đúng cho sản phẩm. |

### EV-P0-02 — `uv run pytest` trên cả bốn gói Python

| Trường | Giá trị |
| --- | --- |
| `command` | `uv run pytest` (testpaths: `tests`, `server/tests`, `collector/tests`, `worker/tests`, `shared/rr_contracts/tests`) |
| `started / ended` | 2026-09-07T09:41:49Z / 2026-09-07T09:42:03Z (14 s) |
| `oracle` | mọi test xanh, gồm cửa "sinh lại không diff" của `rr_contracts` |
| `observed` | **18 passed, 1 warning** (warning là `DeprecationWarning` của `anyio` bên trong `starlette.testclient`, không phải code của repo) |
| `exit_code` | **0** · `status` **PASS** |
| `limitations` | 18 test này kiểm **bộ khung**: app boot, kênh liveness trả đúng hai trường và **không** trường nào khác, bốn pragma SQLite được áp và foreign key **thực sự** bị ép, payload đăng ký capability không quy `unknown` thành `ok`, và cây sinh ra khớp hợp đồng. **Không** test nào kiểm hành vi nghiệp vụ — chưa có hành vi nào. E1 trên fixture vẫn `NOT_RUN`. |

### EV-P0-03 — web: `npm ci`, lint, typecheck, vitest, cửa sinh lại

| Trường | Giá trị |
| --- | --- |
| `commands` | `npm ci` · `npm run lint` (eslint + prettier) · `npm run typecheck` (`tsc --noEmit`) · `npm test` (vitest) · `npm run generate:check` |
| `started / ended` | 2026-09-07T09:42:03Z / 2026-09-07T09:42:17Z |
| `observed` | `npm ci` exit **0** (4 s) · lint exit **0** (3 s) · typecheck exit **0** (2 s) · vitest **11 passed / 2 files** exit **0** (4 s) · `generate:check` exit **0** (1 s) |
| `status` | **PASS** |
| `limitations` | Test web kiểm shell placeholder (đúng năm mục điều hướng SRC-SPEC §4, Reports là mặc định) và cửa sinh lại. Không có test read model nào — chúng thuộc hai card UI. Playwright Test được khai nhưng **không** chạy: E2E là thủ công theo giao thức. |

### EV-P0-04 — E0 sau khi thêm bộ khung: không đổi

| Trường | Giá trị |
| --- | --- |
| `command` | `uv run python evidence/tools/e0_check.py --repo . --json-out <scratch>/E0-after.json` |
| `started / ended` | 2026-09-07T09:42:17Z / 2026-09-07T09:42:22Z (5 s) |
| `oracle` | 24/24 PASS **và** kết quả từng check **giống hệt** lượt chạy nền tôi chạy trước khi ghi file nào |
| `observed` | **TOTAL: 24 checks — PASS 24 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0**. So sánh từng check (`check_id`, `status`, `checked`, số violation) với `E0-baseline.json` chạy lúc 09:14:17Z **trước khi tôi ghi file nào**: **giống hệt từng dòng**. `files_scanned` 220 → **222** |
| `exit_code` | **0** · `status` **PASS** |
| `limitations` | Hai file làm `files_scanned` tăng là **`evidence/tools/verify_cards.py`** (của tôi) và **`precode/owner-decisions-02.md`** (của gói chạy song song) — đó là đúng hai file mới xuất hiện dưới `SCAN_DIRS` giữa hai lượt chạy (`git status`). Không file nào trong chúng bị check header đòi hỏi, nên không check nào đổi trạng thái, đúng như packet dự đoán. Công cụ **không** quét `server/`, `collector/`, `worker/`, `web/`, `tests/` hay `README.md` gốc — chúng nằm ngoài `SCAN_DIRS` — nên một E0 xanh **không** nói gì về bộ khung tôi vừa dựng. |
| `xác nhận sau cùng` | Chạy lại **sau khi** ghi chính file handoff này: vẫn **24/24 PASS, 0 violation, exit 0**, `files_scanned` 223 (+1 = handoff này), và **không check nào khác kết quả so với lượt nền**. Điều này đáng ghi vì handoff mang nhãn claim và `E0-12` quét `evidence/` — xem `CR-P0-02`. |

### EV-P0-05 — validator OpenAPI 3.1 trên `contracts/http/openapi.yaml` (lần đầu tiên trong toàn bộ dự án)

| Trường | Giá trị |
| --- | --- |
| `command` | `uv run openapi-spec-validator contracts/http/openapi.yaml` |
| `started / ended` | 2026-09-07T09:42:23Z / 2026-09-07T09:42:25Z (2 s) |
| `input_hash` | `28b3820e983736f8a02c1ea32fe062ef818b0b1bc29fcb583cab6b34de784d92` (231 705 B) — **khớp đúng** hash mà cả 18 card đã pin |
| `oracle` | tài liệu tuân thủ OpenAPI 3.1 |
| `observed` (nguyên văn) | `contracts/http/openapi.yaml: OK` |
| `exit_code` | **0** · `status` **PASS** |
| `limitations` | Đây là điều `evidence/tools/README.md` §5 mục 3 và `docs/master-plan.md` §1.5 ghi là **chưa từng chạy**. Nay đã chạy và **sạch**. Nó chứng minh **cấu trúc** hợp lệ; nó **không** chứng minh nội dung API đúng nghiệp vụ, và không nói gì về việc `openapi.yaml` có đủ điều kiện `CONTRACT_READY` hay không (`CR-PC10-07` vẫn mở). `CR-P0-01` mà packet dự phòng cho trường hợp validator FAIL vì vậy **không** được raise. |

### EV-P0-06 — `verify_cards.py`: 8/9 check PASS, `pins` FAIL

| Trường | Giá trị |
| --- | --- |
| `command` | `uv run python evidence/tools/verify_cards.py --repo . --json-out <scratch>/cards-after.json` |
| `started / ended` | 2026-09-07T09:42:22Z / 2026-09-07T09:42:23Z (1 s) |
| `oracle` | EV-PC10-01 (a)–(g) + quy tắc epoch §0 + phép kiểm (m) của `agent-tasks/README.md` §5.3 |
| `observed` | **9 check trên 18 card, 2 889 assertion, 54 violation.** `pins` **FAIL** 501 dòng kiểm / 54 lệch. Tám check còn lại PASS: `epoch` 18/18 cùng `PC10-PIN-OD01e-20260907`; `paths` 705; `operations` 133; `scenarios` 268; `errors` 100; `modules` 96; `invariants` 122; `layout` 951 |
| `exit_code` | **1** · `status` **FAIL** |
| `nội dung 54 lệch` | đúng ba file, mỗi file trên cả 18 card: `precode/adr/ADR-0011-frameworks-and-toolchain.md` (pin `9cdec0d7…` 17 052 B → đĩa `6be9189a…` 18 989 B), `precode/baseline.json` (`c99474a6…` → `d25e2edd…`), `precode/decision-register.md` (`3596a52b…` → `4d1a5d6e…`) |
| `nguyên nhân` | gói phê chuẩn `OD-20260907-02` chạy **song song** với gói này đã ghi vào ba file đó (`git status` xác nhận: 8 file `precode/`+`evidence/` ở trạng thái `M`, không file nào do tôi ghi trừ `precode/README.md`). Đây là drift **thật**, không phải false positive |
| `limitations` | Công cụ đọc **lời khai**; nó không đọc nghĩa của card. Một card qua hết 9 check vẫn có thể giao sai việc. |

### EV-P0-07 — self-test âm: `verify_cards.py` có thật sự bắt được lỗi không

Một PASS chỉ đáng tin khi check bắt được đúng thứ nó tuyên bố bắt. Tôi tiêm khiếm khuyết vào
**bản sao** corpus trong thư mục scratch (không bao giờ trong repo), **in ra từng lần tiêm và
khẳng định nó đã landing** trước khi chạy — đúng bài học `evidence/tools/README.md` §5b ghi
lại.

| Check | Đột biến đã tiêm (và đã xác nhận landing) | Kết quả |
| --- | --- | --- |
| `layout` | thêm `web/bad_module.py` và `server/bad_module.ts` vào cây scratch | **Bắt cả hai**, nêu đúng đường dẫn |
| `epoch` | `PC10-PIN-OD01e-20260907` → `PC10-PIN-BOGUS-20260101` trên một card | **Bắt được**, nêu đúng card |
| `paths` | `contracts/ops/secrets.md` → `contracts/ops/secrets-does-not-exist.md` | **Bắt được** |
| `operations` | `auth.login` → `auth.log_in_please` trong §4 | **Bắt được**, nêu "absent from ports.yaml" |
| `scenarios` | `SC40` → `SC99` | **Bắt được** |
| `errors` | `CSRF_REJECTED` → `CSRF_TOTALLY_MADE_UP` trong §7 | **Bắt được** |
| `pins` | *không cần tiêm* — 54 lệch thật ở EV-P0-06 **là** bằng chứng check này bắt được drift | — |

Lần chạy đầu của self-test này **thất bại đúng cách**: hai trong năm đột biến không landing
(token không tồn tại ở dạng tôi giả định), script assert và dừng. Nếu tôi không assert, nó đã
báo "PASS" cho một check chưa từng được thử.

### EV-P0-08 — fixture loader chạy thật trên `acceptance/fixtures/**`

| Trường | Giá trị |
| --- | --- |
| `command` | script scratch nạp `tests/conftest.py` và duyệt cả chín thư mục fixture |
| `oracle` | mọi fixture parse được; `.rows()` **ném lỗi** ở thư mục nêu oracle bằng văn xuôi; tên không tồn tại ném `FixtureNotFound` |
| `observed` | **86 fixture** nạp được: `ai` 11 · `boundary` 1 · `collection` 12 · `e2e` 1 · `identity` 14 · `recovery` 13 · `reporting` 14 · `telegram` 18 · `ui` 2. **44** fixture phơi `given.rows`, **74** phơi `events`. `recovery/c-disk-full-mid-ingest` gọi `.rows("work")` → `FixtureShapeError` đúng như thiết kế. Tên không tồn tại → `FixtureNotFound` kèm danh sách thư mục |
| `exit_code` | **0** · `status` **PASS** |
| `limitations` | **Đây là một lượt chạy tay, không phải một cửa hồi quy.** Write set của packet chỉ gồm `tests/README.md` và `tests/conftest.py`, không gồm một `tests/test_*.py`, nên loader **không có test của chính nó trong CI**. Xem `CR-P0-05`. |

### EV-P0-09 — lint, type, và bề mặt bảo mật của phụ thuộc

| Lệnh | Exit | Ghi chú |
| --- | --- | --- |
| `uv run ruff check .` | **0** | `evidence/` và hai thư mục sinh ra bị loại trừ có khai báo lý do trong `pyproject.toml` |
| `uv run ruff format --check .` | **0** | 24 file |
| `uv run mypy` | **0** | `--strict` trên `server/app` (4 file); `rr_contracts` được **follow** để lấy kiểu nhưng không bị ép `--strict` — nó là máy sinh |
| `uv run python shared/rr_contracts/generate.py --check` | **0** | sinh lại 7 model + 4 module hằng số, diff rỗng (10 s) |
| `cd web && npm run generate:check` | **0** | diff rỗng |
| `npm audit` | — | **0 vulnerabilities.** Lượt pin đầu của tôi có 10 advisory (1 critical, 6 high); tôi nâng `vite` 7 / `vitest` 3 / `react-router-dom` 7 / `@playwright/test` ≥1.55.1 / `eslint` 9.36+ và cài lại. Nâng `openapi-typescript` 7.4→7.9 **đổi đầu ra sinh ra**, và cửa `generate:check` **đã bắt đúng điều đó** trước khi tôi kịp bỏ sót |
| Quét secret | — | không tìm thấy private key hay chuỗi dạng API key nào trong cây (trừ `.git`, `.venv`, `node_modules`). Không có `.env` nào; `.gitignore` chặn `.env` và `.env.*` |
| `git status` | — | không có `__pycache__` lạc; `.venv/`, `node_modules/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` đều nằm trong `.gitignore` |

### Những gì **không** chạy — `NOT_RUN`

- **E1** (contract test trên fixture), **E2** (fault injection), **E3** (live), **E4** (đánh giá): không có hành vi nghiệp vụ nào để kiểm.
- `pre-commit run --all-files`: `.pre-commit-config.yaml` được **viết** nhưng **chưa chạy**; chạy nó sẽ gọi hook `end-of-file-fixer`/`trailing-whitespace` có khả năng **ghi** vào file ngoài write set. Nó là cửa của lập trình viên, không phải bằng chứng của gói này.
- CI trên GitHub Actions: bốn workflow được **viết**, chưa runner nào chạy chúng. Điều tôi kiểm được là từng lệnh bên trong chúng chạy xanh ở máy này, và YAML parse được.
- `alembic upgrade head`: revision khởi tạo là no-op và `RR_DATABASE_URL` cố ý không có mặc định; migration chain chưa được thi hành lần nào.
- `playwright install`, tải model embedding, mọi lời gọi X / Telegram / provider AI.

## 6. Checklist của packet

| # | Mục | Trạng thái | Exit | Ở đâu |
| --- | --- | --- | --- | --- |
| 1 | `uv sync` xong; `uv run pytest` xanh trên cả bốn gói Python (smoke + generated-matches) | **DONE** | `0` / `0` | `EV-P0-01`, `EV-P0-02` — 18 passed |
| 2 | `npm ci` trong `web/` xong; `npm run lint`, `npm test` xanh; client sinh ra khớp | **DONE** | `0` / `0` / `0` / `0` | `EV-P0-03` — 11 passed, 2 file |
| 3 | `e0_check.py` vẫn 24/24 PASS sau khi tôi thêm file | **DONE** | `0` | `EV-P0-04` — giống hệt lượt nền từng dòng |
| 4 | `verify_cards.py` PASS trên số dòng card đang pin | **NOT_DONE** | `1` | `EV-P0-06` — 501 dòng pin, **54 lệch**, 8/9 check PASS. Nguyên nhân ngoài packet: xem `CR-P0-01`. **Tôi không sửa file nào bị pin.** |
| 5 | Kết quả validator OpenAPI ghi trung thực | **DONE** | `0` | `EV-P0-05` — `contracts/http/openapi.yaml: OK`. Không lỗi nào ⇒ **không** raise CR cho PC05, và job CI **không** cần `continue-on-error` |
| 6 | Mọi file sinh ra mang header `# GENERATED — do not edit; source sha256 …`, và cửa diff-on-regenerate tồn tại cho **cả hai** ngôn ngữ | **DONE** | `0` / `0` | Header: 12 file Python sinh ra + `web/src/generated/openapi.d.ts` (test `test_every_generated_file_carries_the_banner` và `carries the do-not-edit banner` ép điều này). Cửa: `shared/rr_contracts/tests/test_generated_matches_contracts.py` và `web/tests/contract/generatedClient.test.ts` |
| 7 | Không secret, không `.env`, không tải model, không cài trình duyệt | **DONE** | — | `EV-P0-09` |

**Bốn trong bảy mục là câu hỏi có/không; ba mục còn lại là lệnh có exit code.** Mục 4 là mục
duy nhất không đạt, và nó không đạt vì một thay đổi tôi không gây ra và không được phép sửa.

## 7. Quyết định kỹ thuật cấp gói (PROVISIONAL) — Coordinator nên soi

Bốn quyết định dưới đây **không** có trong packet và **không** được ADR-0011 nói tới. Tôi
chọn phương án bảo thủ nhất, ghi lại đây để bị bác nếu sai. Không quyết định nào chạm
`contracts/`; đảo bất kỳ cái nào chỉ tốn công sửa code.

### `PROV-P0-01` — import root là gốc repo; `server`, `collector`, `worker`, `probe` là package

**Vấn đề thật.** Card pin `server/app/…`, `collector/app/…` **và** `worker/app/…`. Nếu ba
gói này được cài như ba distribution thì cả ba khai một package top-level tên **`app`** —
chúng **đè lên nhau** trên cùng một `sys.path`, và `tests/contract/` (nơi card đặt cả test
auth lẫn test collector) cần **hai** trong ba cùng lúc. Đây không phải rủi ro lý thuyết:
`pytest` đã báo `import file mismatch` ngay lượt chạy đầu.

**Cách giải.** Mỗi thư mục mang một `__init__.py` và **chính nó** là package: import là
`server.app.auth.service`, `collector.app.reader`, … Ba gói `app` thành ba subpackage khác
tên đầy đủ. Gốc repo là import root (`pythonpath = ["."]`).

**Hệ quả.** `server`, `collector`, `worker` là workspace member **ảo** (`tool.uv.package =
false`): uv resolve phụ thuộc của chúng vào một lockfile chung nhưng không build/cài chúng.
`shared/rr_contracts` là package thật, vì cả ba đều import nó.

**Điều quan trọng:** **không đường dẫn file nào ở §3 của bất kỳ card nào bị đổi.** Cái đổi là
tên module, thứ nằm ở §8 (lệnh) — chỗ card đã khai là `PROVISIONAL`.

### `PROV-P0-02` — `$ref` liên-schema được **giải trước khi sinh**, không sửa tay sau khi sinh

`contracts/schemas/report.schema.json` trỏ tới `target.schema.json` bằng **URL `$id`**
(`https://research-radar.local/...`). Cả hai bộ sinh đều gãy ở đó: `datamodel-codegen` đòi
output là thư mục rồi sinh ra `from ..target import schema` (một import trèo ra khỏi
package, không chạy được); `openapi-typescript` thì **cố fetch URL** và fail.

Sửa tay file sinh ra là **đúng cái mà gói này tồn tại để cấm**. Nên cả hai bộ sinh **giải
tham chiếu trước khi sinh**, trong thư mục tạm, không ghi gì vào `contracts/`:

- Python: schema được **bundle** — schema bị trỏ tới được đưa vào `$defs` dưới tiền tố
  `ext_<stem>`, và `$defs` riêng của nó được đổi tên thành `ext_<stem>__<name>` để `ulid`,
  `sha256`, `timestamp_utc_ms`… của hai schema **không đụng nhau**.
- TypeScript: cả cây `contracts/schemas` + `contracts/http` được chép sang thư mục tạm giữ
  nguyên bố cục (nên `../schemas/…` vẫn đúng) và mọi URL `$id` được thay bằng tên file cạnh
  nó.

Cả hai phép biến đổi là **văn bản thuần và không phụ thuộc thứ tự**, nên đầu ra vẫn là hàm
thuần của byte nguồn. Không ràng buộc nào, không tên trường nào bị đổi.

### `PROV-P0-03` — `sentence-transformers` được **khai** chứ không cài

`server/pyproject.toml` có extra `embedding`. `uv sync` **không** cài nó. Lý do: nó kéo
PyTorch (ADR-0011 đã gọi tên đây là chi phí đã biết), và model cụ thể còn là câu hỏi chưa
trả lời — cài một thư viện để dùng một model chưa chọn là mua trước một quyết định.

### `PROV-P0-04` — bốn tham số SQLite

`journal_mode=WAL` và `foreign_keys=ON` là **ràng buộc hợp đồng**, không phải lựa chọn (backup
nhất quán của AMD-B11 chỉ WAL-safe khi DB thật sự ở WAL; ràng buộc tham chiếu trong
`contracts/data/entities.yaml` **không được ép** nếu thiếu pragma kia — smoke test chèn một
foreign key mồ côi và đòi nó bị từ chối). Hai tham số còn lại là **giá trị kỹ thuật của Giai
đoạn 0**, có số và có lý do, không phải số hợp đồng: `busy_timeout=5000` ms (hai người ghi —
vòng lặp scheduler và một request HTTP — sẽ tranh nhau; không có timeout thì SQLite ném
`database is locked` ngay lập tức và một lần chờ ngắn biến thành một lỗi giả) và
`synchronous=NORMAL` (cặp đôi an toàn đã biết của WAL: bền trước crash ứng dụng, còn cửa sổ
mất điện — đó chính là lý do hợp đồng backup tồn tại). Card nào cần số khác thì truyền tường
minh.

## 8. Unresolved refs — change request

### `CR-P0-01` — 18 card `STALE`: ba file đã pin bị sửa trong lúc gói này chạy · **BLOCKING**

**Sự việc.** `verify_cards.py` báo 54 dòng pin lệch, đúng ba file trên cả 18 card:

| File đã pin | Card pin | Trên đĩa | Bytes |
| --- | --- | --- | --- |
| `precode/adr/ADR-0011-frameworks-and-toolchain.md` | `9cdec0d78592c67068188e7dffcf9e03f361fe202263bb47a95b2298337a8340` | `6be9189a5e61b03eb44bdbfb2ca6841b1ca2d04f9dbf140fcc39764be5a9b155` | 17 052 → 18 989 |
| `precode/baseline.json` | `c99474a6744a3827f75961884d5d8daf1d9fb0bfe212547c216d1574d32ac81a` | `d25e2edd05437dc4…` | — |
| `precode/decision-register.md` | `3596a52b6ce8cb39a0ae07501fd177c80a4fdb7b19317fc82a3dd8e3df63a75d` | `4d1a5d6e5d2a4f0a…` | — |

**Nguyên nhân.** Gói ghi bản phê chuẩn `OD-20260907-02` chạy **song song** với gói này và đã
đổi `ADR-0011` từ `provisional-accepted` sang `accepted` (`ratified_by: OD-20260907-02`), kèm
`baseline.json` và `decision-register.md`. Tôi đọc ADR-0011 **hai lần** trong phiên: bản
trước và bản sau, và tôi xây theo bản sau — nội dung kỹ thuật của bảng lựa chọn **không đổi**
giữa hai bản, chỉ phần trạng thái/phê chuẩn đổi.

**Vì sao tôi không sửa.** Card nằm ngoài write set. Quan trọng hơn: một pin lệch **là** tín
hiệu STALE mà `INV-06` dựng lên. Tự sửa nó ở đây sẽ là im lặng gỡ đúng cái chuông vừa kêu.

**Việc cần làm, trước khi card Giai đoạn 1 được phát.** Re-pin cả 18 card sang một epoch mới
(ví dụ `PC10-PIN-OD02a-20260907`) với ba hash mới. Đây là công việc của gói sở hữu
`agent-tasks/` (PC10), không phải của gói này. `verify_cards.py` sẽ chuyển xanh ngay khi
việc đó xong — và nếu nó không chuyển xanh, nghĩa là còn drift khác.

### `CR-P0-02` — cửa `E0-12` giả định "chưa có code nào tồn tại"; giả định đó nay sai

`E0-12-forbidden-strings` cấm **tuyệt đối** mọi nhãn trên `CONTRACT_READY` trong toàn bộ phạm
vi quét (gồm `evidence/`), với lý do viết thẳng trong oracle: *"no code exists, so nothing
above it is establishable"*. Sau `OD-20260907-02` mục 2, code **đã** tồn tại và trần claim
của Giai đoạn 0/1 **là** `IMPLEMENTATION_VERIFIED`.

Hệ quả cụ thể: nếu tôi ghi trần hoàn thành của mình vào một **trường có cấu trúc** trong
front-matter của handoff này (`claim_ceiling:` hay `completion_claim:`), `E0-12` sẽ FAIL. Tôi
vì vậy để trần claim trong **bảng §1** (nơi nhãn nằm trong backtick và check bỏ qua), và
front-matter **không** mang hai khóa đó. Đó là một cách viết vòng, không phải một cách sửa.

**Việc cần làm** (chủ sở hữu: PC09): mở `E0-12` cho `evidence/handoffs/**` và
`evidence/runs/**` được khai nhãn tới đúng trần mà Owner đã cho phép ở giai đoạn tương ứng,
và giữ lệnh cấm cho `contracts/`/`acceptance/`. Không sửa gấp: hiện chưa có gì hỏng, chỉ có
một chỗ mà văn bản trung thực phải luồn lách để đi qua một cửa đã lỗi thời.

### `CR-P0-03` — hai đường dẫn card nằm ngoài "bảy thư mục"

1. `agent-tasks/TC-backup-restore-drill.md` §3 pin `tools/backup_cli.py`. `tools/` là cây
   top-level **thứ tám**, không có trong bảy thư mục của `agent-tasks/README.md` §5.3 hay
   ADR-0011. Tôi **không** tạo nó (ngoài write set). Card M8 sẽ phải tạo nó, hoặc §5.3 phải
   khai nó, hoặc file phải chuyển vào `server/`. `verify_cards.py` đã tính `tools/` là cây
   Python cho phép kiểm (m) không báo động sai khi nó xuất hiện.
2. `agent-tasks/README.md` §5.3 mô tả `tests/` là `contract/`, `unit/`, `integration/` ở một
   chỗ và chỉ hai thư mục ở chỗ khác. §3 của cả 18 card chỉ dùng `contract/` và
   `integration/`. Tôi tạo hai thư mục đó và ghi trong `tests/README.md` §4 rằng `unit/` sẽ
   do card đầu tiên thực sự cần nó tạo ra.

### `CR-P0-04` — quy chủ sở hữu `web/src/lib/api.ts` trong amendment của Coordinator lệch với card

Amendment giữa phiên của Coordinator nói `web/src/lib/api.ts` do `TC-owner-auth-session` sở
hữu. Card **nói ngược lại, tường minh**: §3 của `TC-owner-auth-session` có một hàng ghi
*"nửa trình duyệt của CSRF **không** thuộc card này … do card `TC-ui-runs-three-states` /
`TC-ui-reports-detail` sở hữu"*, và `agent-tasks/README.md` §5.3 nói cùng điều đó.

Tôi làm theo **card**, vì card là văn bản đã được pin: file tôi tạo là một stub fetch có kiểu,
**không có logic CSRF**, và header của nó nêu **cả ba** card cùng ranh giới giữa chúng. Hiệu
lực thực tế giống hệt điều Coordinator yêu cầu; chỉ phần quy chủ sở hữu là khác. Xin xác nhận
lại để hai văn bản không lệch tiếp.

Ghi chú kèm theo cho hai card UI: `TC-ui-runs-three-states` §3 mô tả `api.ts` là *"client HTTP
**sinh từ** openapi.yaml"*. Ở bố cục này việc sinh được tách làm hai: **kiểu wire** là code
sinh ra (`web/src/generated/openapi.d.ts`, có cửa diff-on-regenerate), còn `api.ts` là một lớp
bọc `fetch` mỏng **viết tay** đứng trên các kiểu đó — đây là mô hình chuẩn của
`openapi-typescript`. Nếu card muốn `api.ts` **toàn bộ** là máy sinh thì cần một bộ sinh khác
và một CR.

### `CR-P0-05` — fixture loader chưa có cửa hồi quy

`tests/conftest.py` đã chạy thật trên 86 fixture (`EV-P0-08`) nhưng **không có test của chính
nó trong CI**, vì write set của packet không cho phép tạo `tests/test_*.py`. Card Giai đoạn 1
đầu tiên dùng loader sẽ biến nó thành cửa thật; cho tới lúc đó, một hồi quy trong loader sẽ
**không** bị bắt.

### Ghi chú: `CR-P0-01` mà packet dự phòng cho validator OpenAPI **không** được raise

Packet nói: nếu `openapi-spec-validator` FAIL thì ghi mọi lỗi thành `CR-P0-01` cho PC05 và
cho phép job CI mang `continue-on-error`. Nó **PASS** (`EV-P0-05`), nên không có CR, và
`.github/workflows/openapi.yml` **không** mang `continue-on-error` — một job có thể fail thật
mới là một job đáng chạy. Số hiệu `CR-P0-01` được dùng lại cho phát hiện blocking ở trên.

## 9. Điều gói này **không** chứng minh

- **Không hành vi nghiệp vụ nào tồn tại.** Không operation nào ngoài `health.get_liveness`
  được route, và cả nó cũng chỉ trả `up` + phiên bản schema.
- **`health.get_readiness` cố ý không được route** — nó thuộc
  `TC-storage-write-blocked-readiness`. Có một test khẳng định `/v1/health/readiness` trả
  **404**, để nếu ai đó lặng lẽ thêm route vào app factory thì ranh giới sở hữu bị đem ra xem
  lại chứ không bị vượt qua tình cờ.
- **Không thư mục domain nào của server được tạo** (`auth/`, `ingest/`, `identity/`,
  `storage/`, `health/`) — card sở hữu chúng.
- **Không migration nào chạy.** Revision khởi tạo là no-op có chủ đích: schema thật được viết
  từ `contracts/data/entities.yaml` bởi card Giai đoạn 1, và bịa bảng ở đây sẽ dựng một nguồn
  sự thật thứ hai cạnh hợp đồng entity.
- **E0 xanh không nói gì về bộ khung** — `e0_check.py` chỉ quét `contracts/`, `acceptance/`,
  `precode/`, `evidence/`.
- **Tính tất định của code sinh ra là tất định *với một toolchain đã khóa*.** Nâng
  `openapi-typescript` 7.4 → 7.9 **đã** đổi đầu ra; cửa `generate:check` bắt được, nhưng điều
  đó nghĩa là `uv.lock` và `package-lock.json` là một phần của định nghĩa "sinh lại không
  diff", không chỉ là phụ thuộc.
- **Không có independent audit.** Mọi thứ ở đây là `SELF_VALIDATION`: tôi viết cả code lẫn
  công cụ kiểm nó.

## 10. Bàn giao

`next_actor`: **Coordinator**. `lease_released_at`: **2026-09-07T09:55Z**.

Sau file này tôi không chạm file nào nữa. Commit là việc của Coordinator; tôi chưa chạy lệnh
git nào có tác dụng ghi.

**Việc Coordinator nên làm trước khi phát card Giai đoạn 1:** giải `CR-P0-01` (re-pin 18
card). Cho tới lúc đó `verify_cards.py` còn đỏ, và một card `STALE` theo `INV-06` thì không
được thi hành.

---

# Addendum — `PKT-P0-FIX1`

- `packet_id`: `PKT-P0-FIX1` · `worker_principal`: `worker-WS` · `authority_id`:
  `AUTH-COORD-P0-FIX1` (parent `AUTH-OWNER-20260907-03`) · `lease_id`:
  `LEASE-P0-SKELETON-e2` (fencing 2) · **`status`: `DONE`** · `next_actor`: `Coordinator` ·
  `lease_released_at`: 2026-09-07T10:40Z.
- MODIFY grant: **`server/tests/test_smoke.py` only**. Nothing else was written except this
  addendum. No file under `contracts/`, `acceptance/`, `agent-tasks/` or `precode/` was
  touched.

## A.1 Vì sao Giai đoạn 0 phải sửa một test của chính nó

Test `test_readiness_is_not_routed_in_phase_0` khẳng định `GET /v1/health/readiness` trả
**404**. Nó là một **tripwire có chủ đích**, ghi ngay trong docstring gốc: readiness không
thuộc packet Giai đoạn 0, nên nếu ai đó lặng lẽ thêm route vào app factory thì ranh giới sở
hữu bị đem ra xem lại chứ không bị vượt tình cờ.

Giai đoạn 1 **vượt nó có chủ đích và đúng thẩm quyền**:
`agent-tasks/TC-storage-write-blocked-readiness.md` nay sở hữu route và
`server/app/health/router.py`; `agent-tasks/TC-owner-auth-session.md` sở hữu nửa phiên, và
health router **từ chối mặc định** khi chưa có dependency phiên nào được tiêm. Quan sát
trước khi sửa: `assert 401 == 404` — tức route **đã tồn tại** và trả `401`, không phải
`404`.

Tripwire đã làm xong việc của nó. Cách xử lý đúng là **đảo nó thành sự thật của Giai đoạn
1**, không phải xóa: một test ranh giới thôi khẳng định gì thì tệ hơn không có test.

## A.2 Cái gì thay thế nó

`test_readiness_is_not_routed_in_phase_0` → **`test_readiness_is_routed_and_denies_an_unauthenticated_caller`**,
khẳng định ba điều thay vì một:

1. route **tồn tại** — `health.get_readiness` và `health.get_liveness` đều có trong
   `app.routes` (một refactor làm rơi route sẽ fail ở đây);
2. trên **app factory trần** (không tiêm dependency phiên) nó trả **401**, không phải 200 và
   không phải 404 — `contracts/http/openapi.yaml` gán path này scheme `ownerSessionCookie`
   trong khi `/healthz` mang `security: []`;
3. **mã lỗi** là `UNAUTHORIZED`, đọc từ `ErrorCode` sinh ra. `agent-tasks/README.md` §5.2:
   trả sai mã cũng là FAIL, không chỉ sai hành vi.

Thêm một test mới, **`test_liveness_stays_open_while_readiness_is_locked`**: `/healthz` →
200 **và** `/v1/health/readiness` → 401 trong cùng một khẳng định. `contracts/state/storage.yaml`
HC-01 buộc liveness trả lời được cả khi DB không đọc được — nghĩa là nó **không** được nằm
sau một phiên, vì tra phiên là một phép đọc DB; HC-02 đặt readiness sau phiên owner vì nó lộ
nội bộ từng module. Đặt hai vế cạnh nhau để một thay đổi kiểu "khóa hết endpoint health lại
cho an toàn" không lặng lẽ khóa luôn liveness.

Docstring của module cũng được sửa: nó không còn nói "chưa có hành vi nghiệp vụ nào" — câu
đó nay sai — mà nói rõ file này cố ý dừng ở mức boot-và-ranh-giới, để một lỗi ở đây nghĩa là
**bộ khung** hỏng chứ không phải một tính năng hồi quy.

| File | Op | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `server/tests/test_smoke.py` | MODIFY | `03c3e4fc8b3355e7c295fe2baace8ba49e760c0aeb54509a656925a69f8d0cf6` (3 693 B, bản `PKT-P0-SKELETON`) | `3b7b1231f0b65c0d4a3eb65f6602e2f9d613ba18a0e89c5b25fd5eb7e5a601c7` | 6 709 |

File này có 7 test trước, **8 test** sau (một test đảo chiều, một test mới).

## A.3 Bằng chứng — `EV-P0-10`, `SELF_VALIDATION`

Mọi lệnh ở `/mnt/virtual/repo/xcrawl`, `PYTHONDONTWRITEBYTECODE=1`, 2026-09-07T10:34–10:36Z.

| Cửa | Lệnh | Exit | Kết quả |
| --- | --- | --- | --- |
| Toàn bộ suite Python | `uv run pytest -p no:cacheprovider -q` | **0** | **263 passed, 4 xfailed, 0 failed** (36 s). Trước gói này: 261 passed / 4 xfailed / **1 failed** |
| Chỉ file đã sửa | `uv run pytest -p no:cacheprovider server/tests/test_smoke.py` | **0** | **8 passed** |
| Lint | `uv run ruff check .` | **0** | `All checks passed!` |
| Format | `uv run ruff format --check .` | **0** | 58 file đã đúng định dạng |
| Type | `uv run mypy` | **0** | `Success: no issues found in 24 source files` (`--strict` trên `server/app`, theo ADR-0011) |
| Web | `cd web && npm test` | **0** | **11 passed / 2 file** |
| E0 | `uv run python evidence/tools/e0_check.py --repo . --json-out <scratch>` | **0** | **24 checks — PASS 24 · FAIL 0 · BLOCKED 0 · N/A 0 · violations 0** |
| Card pins | `uv run python evidence/tools/verify_cards.py --repo . --json-out <scratch>` | **0** | **13 checks trên 18 card — 13 PASS, 0 FAIL, 0 BLOCKED, 3 211 assertion, 0 violation** |

Chi tiết `verify_cards.py`: `pins` 501 · `epoch` 22 · `paths` 705 · `operations` 133 ·
`scenarios` 268 · `errors` 100 · `modules` 96 · `invariants` 122 · `obligations` 90 ·
`claim_labels` 45 · `pc09_unpinned` 126 · `stack` 18 · `layout` 985.

> **`CR-P0-01` đã đóng.** Ở `PKT-P0-SKELETON`, `pins` FAIL với **54** lệch vì ba file đã pin
> bị gói phê chuẩn song song sửa. Nay `pins` **PASS 501/501, 0 lệch**: card đã được re-pin,
> đúng việc mà `CR-P0-01` yêu cầu. Công cụ cũng đã được gói khác **mở rộng** từ 9 lên 13
> check (thêm `obligations`, `claim_labels`, `pc09_unpinned`, `stack`) — mở rộng đó không
> phải của tôi và tôi không sửa gì trong file đó ở gói này.

## A.4 Trạng thái cây làm việc

`git status --porcelain` sau khi sửa: **không có artefact lạc nào ngoài `.gitignore`.**

- Bốn mục bị Git bỏ qua và **đã** nằm trong `.gitignore`: `.venv/`, `web/node_modules/`,
  `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`.
- **Không** có `__pycache__` nào ngoài `.venv/` và `node_modules/`.
- **Không** có `*.db`, `*.db-wal`, `*.db-shm` nào trong cây làm việc; file `.db` duy nhất
  tồn tại là `.mypy_cache/3.12/cache.db`, nằm trong thư mục đã bị bỏ qua **và** khớp luôn
  luật `*.db`.
- **Không** có `.env` nào.
- Mọi mục `??` còn lại là sản phẩm hợp lệ của Giai đoạn 0/1 chờ Coordinator commit: bộ khung
  (`pyproject.toml`, `uv.lock`, `server/`, `collector/`, `worker/`, `shared/`, `tests/`,
  `web/`, `probe/`, `.github/`, `Makefile`, `README.md`, `.gitignore`,
  `.pre-commit-config.yaml`, `.python-version`), `evidence/tools/verify_cards.py`, năm
  handoff và bốn file `evidence/runs/*.json` của các card Giai đoạn 1, và
  `precode/owner-decisions-02.md`.
- `.claude/` là thư mục cấu hình của phiên, **đã tồn tại từ trước** khi gói này bắt đầu và
  không do tôi tạo. Coordinator quyết định có commit nó hay không.

## A.5 Điều addendum này **không** chứng minh

Tôi sửa **một test**. Tôi **không** đọc, review hay xác nhận hiện thực của bốn card Giai
đoạn 1 — chúng có handoff riêng và người review riêng. Một suite 263 xanh nói rằng mọi test
**đã được viết** đều pass; nó không nói rằng những test đó phủ đúng nghĩa vụ chứng minh ở §8
của từng card. Đây vẫn là `SELF_VALIDATION`, không phải audit độc lập.

---

# Addendum — `PKT-P0-FIX2`

- `packet_id`: `PKT-P0-FIX2` · `worker_principal`: `worker-WS` · `authority_id`:
  `AUTH-COORD-P0-FIX2` (parent `AUTH-OWNER-20260907-03`) · `lease_id`:
  `LEASE-P0-SKELETON-e3` (fencing 3) · `next_actor`: `Coordinator`.
- Nguồn: `FIX-A3R1-rulings.md` (2026-09-07T11:00Z) và `A3-R1-report.md` — ba mục
  `F-A3R1-07`, `F-A3R1-15`, `F-A3R1-02`.
- MODIFY grant: `README.md`, `server/app/db/faults.py` (chỉ khi cần),
  `shared/rr_contracts/**` file sinh ra + `GENERATED_FROM.json`, `web/src/generated/**`
  (chỉ khi đổi). Không file nào khác được ghi ngoài addendum này.

## B.1 `F-A3R1-07` — nhận `server/app/db/faults.py` vào write set của Giai đoạn 0

| File | Op | sha256 | Bytes | Dòng |
| --- | --- | --- | --- | --- |
| `server/app/db/faults.py` | ADOPT (không sửa) | `035547f389346549729b15df3b3e8e253d3b6c48610ea5ea5e13520faaf2eb8c` | 4 274 | 116 |

**Ghi chú quy chủ sở hữu.** File này được `TC-storage-write-blocked-readiness` tạo ra nhưng
không nằm trong §3 của card đó, và cũng không nằm trong `PKT-P0-SKELETON` — Giai đoạn 0 chỉ
giao `db/engine.py` và `db/__init__.py`. `A3-R1` xếp đây là khiếm khuyết **của dispatch**
cũng ngang với của Worker: ghi chú dispatch Giai đoạn 1 §4 nói tới *"SQLite failure injection
via the wrapper in `server/app/db/`"* như thể nó đã tồn tại, và Worker dựng đúng cái mà
dispatch giả định. Coordinator đã thừa nhận khiếm khuyết đó và **nhận file vào bộ khung Giai
đoạn 0**, nơi nó thuộc về theo bản chất: nó không phải hạ tầng của một card mà là **hạ tầng
test dùng chung** — ba test integration của **hai** card khác nhau import nó
(`tests/integration/test_readiness_independent_channel.py`,
`tests/integration/test_ingest_ack_lost.py`,
`tests/integration/test_disk_full_no_ack.py`). Chủ sở hữu từ nay là bộ khung Giai đoạn 0
(`worker-WS`), cùng chỗ với `db/engine.py`. Việc nhận này **không** sửa §3 của card nào —
`A3-R1` nói thẳng rằng vá bằng cách thêm vào card sau sự việc là sửa chính cái oracle.

**Review so với quy ước của `server/app/db/` — kết luận: KHÔNG sửa gì.** Tôi đọc file đối
chiếu `db/engine.py` trên bảy điểm:

| Quy ước của `server/app/db/` | `faults.py` | |
| --- | --- | --- |
| `from __future__ import annotations` ngay sau docstring | có | ✓ |
| Docstring module giải thích **vì sao**, trích hợp đồng đích danh | có — `TC-storage-write-blocked-readiness` §8, `contracts/state/storage.yaml` `write_blocked`, `REQ-S9.3-08`, `I02` | ✓ |
| Hằng số module chú thích bằng `#:` | `DISK_FULL_MESSAGE`, `_WRITE_PREFIXES` | ✓ |
| Hàm nội bộ mang tiền tố `_`; tham số hook không dùng cũng vậy | `_is_write`, `_before_cursor_execute(self, _conn, _cursor, …)` — đúng như `_apply_pragmas(dbapi_connection, _connection_record)` của `engine.py` | ✓ |
| Móc vào engine bằng `sqlalchemy.event.listen` | có, cùng cơ chế `engine.py` dùng cho pragma | ✓ |
| `@contextmanager` trả `Iterator[...]` | `disk_full()` | ✓ |
| Qua `ruff check`, `ruff format --check`, `mypy --strict` | cả ba **exit 0** (`mypy` tính nó trong 24 file của `server/app`) | ✓ |

Một điểm **không** phải vi phạm mà là lựa chọn đúng, tôi ghi lại để nó không bị "sửa cho nhất
quán" sau này: `db/__init__.py` re-export API của `engine.py` nhưng **không** re-export
`WriteFaultInjector`. Ba test import thẳng `from server.app.db.faults import …`. Giữ nguyên
như vậy là có chủ đích — đưa một bộ tiêm lỗi vào bề mặt công khai của package sẽ khiến code
sản phẩm với tới nó dễ hơn mức nên có. Tôi **không** sửa.

Điều file này **không** chứng minh (đã ghi trong chính docstring của nó, và tôi xác nhận
lại): nó tái hiện *điều kiện quan sát được* của một đĩa đầy, **không** tái hiện hành vi thật
của SQLite trên một volume đầy — đặc biệt là chuyện file có hỏng hay không (`REQ-S9.3-08`).
Vế đó thuộc một drill sống và vẫn `NOT_RUN`.

## B.2 `F-A3R1-15` — dạng `uv sync` trong `README.md`

`README.md:102` mô tả job CI `python` chạy `uv sync --frozen`. Dạng đó **prune** các
workspace member và sinh 11 lỗi collection; workflow thật
(`.github/workflows/python.yml:32`) và `make setup` đều dùng `--all-packages`. File tự mâu
thuẫn với chính dòng 22 của nó.

Sửa **hai** chỗ trong `README.md` (đây là toàn bộ số lần dạng sai xuất hiện trong file):

| Dòng | Trước | Sau |
| --- | --- | --- |
| 102 (bảng CI) | `uv sync --frozen` | `uv sync --all-packages --frozen` — khớp đúng byte với `.github/workflows/python.yml` |
| 29 (văn xuôi về extra `embedding`) | "không được cài bởi `uv sync`" | "không được cài bởi `uv sync --all-packages`" |

Dòng 22 (khối cài đặt) vốn đã đúng.

**Hai chỗ còn lại tôi *không* sửa, và vì sao.**

1. `server/pyproject.toml:25` — comment *"Declared, NOT installed by `uv sync`"* mang cùng
   dạng thiếu cờ. File đó **không nằm trong MODIFY grant** của gói này. Nó là một comment mô
   tả (extra không được cài), không phải một lệnh để người đọc chép, nên tác hại nhỏ hơn
   hẳn dòng 102 — nhưng nó vẫn nên được sửa ở gói nào có grant. Ghi lại thành việc còn mở.
2. `evidence/handoffs/P0-skeleton-handoff.md` §6 và §7 (dòng 326, 384) cũng viết `uv sync`
   trần. **Tôi cố ý không sửa**: đó là **bản ghi bằng chứng** của gói `PKT-P0-SKELETON`, và
   lệnh thật đã chạy được ghi nguyên văn ở `EV-P0-01` là `uv sync --all-packages --frozen`.
   Sửa lại lời văn của một bản ghi bằng chứng sau khi nó được audit là việc tệ hơn hẳn cái
   nó sửa. Dạng chuẩn được nêu ở đây, trong addendum, đúng chỗ của nó.

## B.3 `F-A3R1-02` — sinh lại `shared/rr_contracts` sau `AMD-ENT-owner-01`

**Cổng.** Gói này chờ `worker-W3n` nhả `PKT-PC02-FIX12`. Cổng mở lúc **2026-09-07T11:11:10Z**:
`evidence/handoffs/PC02-handoff.md` §L1 khai `lease_released_at 2026-09-07T11:12Z` cho
`LEASE-PC02-e13`. Tôi **không** bắt đầu sinh lại trước mốc đó, kể cả khi `entities.yaml` đã
thấy đổi trên đĩa lúc 11:06Z — file đổi không phải là lease nhả, và W3n còn ghi tiếp sau đó
(hash đi từ `fb92d433…` sang `f5ea0511…`). Sinh lại trên một baseline còn đang chuyển động sẽ
tạo ra một artefact không tái lập được.

**Kết quả: sinh lại xong, và đúng như dự đoán không có diff nào.**

| Bộ sinh | Lệnh | Exit | Kết quả |
| --- | --- | --- | --- |
| Python | `uv run python shared/rr_contracts/generate.py` | **0** | 7 model, 28 mã lỗi, 85 operation id, 16 state enum (9 s) |
| TypeScript | `cd web && node scripts/generate.mjs` | **0** | `openapi.d.ts` 403 396 B |
| So sánh | `sha256sum` 16 file sinh ra, trước ∥ sau | — | **giống hệt từng byte, cả 16 file** |

`GENERATED_FROM.json` **không đổi** ở cả hai phía, vì 15 nguồn của nó không đổi:

| File | sha256 | |
| --- | --- | --- |
| `shared/rr_contracts/rr_contracts/generated/GENERATED_FROM.json` | `ed76aefc67940671ff34506ec05d5609010b8bdfe3d85131c9e7c290c9de218a` | không đổi |
| `web/src/generated/GENERATED_FROM.json` | `cc6fa45b0a1bb61ff4dd336f1cdfdf8055795ad71ce60f8d0e1a2c0978155e19` | không đổi |
| `web/src/generated/openapi.d.ts` | `0885e55f5f659044fe7b8f4bd146f13d9c4e48c716169e06d835f87dfd31ccaf` | không đổi |

`contracts/http/openapi.yaml` (`28b3820e…`) và cả bảy `contracts/schemas/*.json` **không
đổi** — đúng như packet dự đoán ("they should not"), nên `web/src/generated/**` không có gì
để cập nhật.

**Vì sao không có diff, và vì sao đó là kết quả đúng.** `contracts/data/entities.yaml`
**không nằm trong 15 nguồn** của bộ sinh, và đó là thiết kế của `PKT-P0-SKELETON`: write set
của nó nêu đích danh "Pydantic v2 models cho mọi `contracts/schemas/*.json`; enum/hằng số cho
mã lỗi từ `errors.yaml`, operation id từ `ports.yaml`, state enum từ `contracts/state/*.yaml`"
— tức **hợp đồng wire**, không phải hợp đồng **cơ sở dữ liệu**. Hai thứ khác hình dạng: có
cột không bao giờ qua dây (`password_hash` là ví dụ chuẩn — `PKT-PC02-FIX12` §L2 ghi rõ nó
**KHÔNG BAO GIỜ** được trả bởi bất kỳ read model nào), và có trường payload không bao giờ là
cột.

Coordinator đã ra ruling xác nhận điều này và yêu cầu ghi lại nó ở nơi người đọc bộ sinh sẽ
gặp. Tôi thêm một mục **"What is deliberately NOT a source"** vào docstring của
`shared/rr_contracts/generate.py` — đặt ngay trên `ALL_SOURCES`, chỗ mà một người đang hỏi
"tại sao entities.yaml không có ở đây" sẽ nhìn vào — nêu ba điều: entities.yaml cố ý không
phải nguồn; hợp đồng entity tới code bằng **hai đường khác**, cả hai đọc thẳng
`entities.yaml` (revision base của Alembic dưới `server/migrations/versions/`, do `worker-WM`;
và `tests/contract/test_schema_matches_entities.py`, cửa vĩnh viễn do `worker-WA` — chính là
phép kiểm mà `F-A3R1-02` yêu cầu biến thành thường trực); và rằng `AMD-ENT-owner-01` vì vậy
**đúng khi không sinh ra diff nào**.

| File | Op | sha256 sau | Bytes |
| --- | --- | --- | --- |
| `shared/rr_contracts/generate.py` | MODIFY (chỉ docstring) | `8e3f9ed49d9abad9983ed5c2ff55a7be576ac7af92fea26ad724bb46827052e3` | 24 602 |
| `README.md` | MODIFY (hai dòng `uv sync`) | `f6ae875fd95b5cf6291f7a843b774706e6dce8ae5a0c8b8aa93f8c69722661c9` | 6 225 |

Sửa docstring **không thể** làm đổi đầu ra — và điều đó được chứng minh chứ không phải suy
luận: `generate.py --check` chạy **sau** khi sửa vẫn exit 0.

## B.4 Bằng chứng — `EV-P0-11`, `SELF_VALIDATION`

Chạy 2026-09-07T11:11–11:13Z tại `/mnt/virtual/repo/xcrawl`, `PYTHONDONTWRITEBYTECODE=1`,
sau khi `LEASE-PC02-e13` đã nhả.

| Cửa | Lệnh | Exit | Kết quả |
| --- | --- | --- | --- |
| Sinh lại Python | `uv run python shared/rr_contracts/generate.py` | **0** | 7 model · 28 mã lỗi · 85 operation · 16 state enum |
| Sinh lại web | `cd web && node scripts/generate.mjs` | **0** | 403 396 B |
| Diff 16 file sinh ra | `sha256sum` trước/sau | — | **0 file đổi** |
| Cửa Python "khớp hợp đồng" | `uv run pytest … test_generated_matches_contracts.py` | **0** | **4 passed** |
| Cửa web "khớp hợp đồng" | `npx vitest run tests/contract/generatedClient.test.ts` | **0** | **4 passed** |
| `--check` Python | `generate.py --check` | **0** | `generated tree matches a fresh run of the generator` |
| `--check` web | `node scripts/generate.mjs --check` | **0** | `generated client matches a fresh run of the generator` |
| **Toàn bộ suite Python** | `uv run pytest -p no:cacheprovider` | **0** | **291 passed, 4 xfailed, 0 failed** (36,6 s) |
| Lint | `uv run ruff check .` | **0** | `All checks passed!` |
| Format | `uv run ruff format --check .` | **0** | 60 file |
| Type | `uv run mypy` | **0** | `Success: no issues found in 25 source files` |
| Web | `cd web && npm test` | **0** | **11 passed / 2 file** |
| E0 (chỉ đọc) | `evidence/tools/e0_check.py --repo . --json-out <scratch>` | **0** | **24 checks — PASS 24 · FAIL 0 · BLOCKED 0 · violations 0**; giống hệt lượt `PKT-P0-FIX1` từng check, `files_scanned` 227 → 227 |
| Card pins | `evidence/tools/verify_cards.py --repo .` | **0** | **13 PASS / 0 FAIL, 3 213 assertion, 0 violation**; `pins` **501/501** trên epoch `PC10-PIN-P1c-20260907` (`entities.yaml` `f5ea0511…`, 235 547 B — WP đã re-pin) |

**`E0-19` không tồn tại.** Packet nói "nếu `e0_check.py` có phép kiểm generated-matches
`E0-19` thì chạy nó ở chế độ chỉ đọc". `grep -n "E0-19" evidence/tools/e0_check.py` trả
**0 dòng**; công cụ vẫn có đúng 24 check và không check nào tên như vậy. Kết quả cho mục này
là **`NOT_APPLICABLE`** — không phải PASS. Cửa "file sinh khớp hợp đồng" hiện do **test**
gánh (hai dòng `pytest`/`vitest` ở trên), không do E0; ADR-0011 §Nguồn vẫn liệt kê "thêm kiểm
tra E0 'mã sinh khớp hash hợp đồng'" là việc còn lại chưa làm, và nó vẫn đúng.

## B.5 `CR-P0-06` — bộ sinh không phủ `contracts/data/entities.yaml`

**Ghi lại theo yêu cầu của Coordinator, không phải một đề nghị đổi phạm vi.**

Hôm nay, một amendment với entity (`AMD-ENT-owner-01`) tới được code bằng hai đường đọc thẳng
`entities.yaml`: DDL trong revision Alembic, và `tests/contract/test_schema_matches_entities.py`.
Cả hai đều **viết tay**. Nghĩa là hình dạng bảng tồn tại ở ba nơi — hợp đồng, migration, test
— và chỉ **một** cặp trong ba được máy so khớp (migration ↔ test, sau `upgrade head`). Hợp
đồng ↔ migration được chứng minh **gián tiếp**, qua test đó.

Cải tiến khả dĩ: sinh một **registry entity** bằng Python từ `entities.yaml` (tên bảng, cột,
kiểu, nullability, UNIQUE/CHECK) và cho migration lẫn test cùng đọc nó, để "hình dạng bảng"
có đúng **một** nguồn máy đọc được. Chi phí không nhỏ: `entities.yaml` là 235 KB với 60
entity, index riêng phần và cột generated, và bộ sinh sẽ phải mã hoá đúng ngữ nghĩa SQLite
của chúng.

**Không thuộc phạm vi gói này.** Nó mở rộng `ALL_SOURCES`, tức đổi hợp đồng đầu ra của
`shared/rr_contracts`, và cần một quyết định của Coordinator kèm một packet có write set nói
rõ. Ghi ở đây để nó không bị mất.

## B.6 Việc còn mở mà gói này **không** được phép sửa

1. **`server/pyproject.toml:25`** mang comment *"Declared, NOT installed by `uv sync`"* —
   cùng lớp lỗi với `F-A3R1-15` nhưng file **không nằm trong MODIFY grant**. Đó là comment mô
   tả chứ không phải lệnh để chép, nên tác hại nhỏ; vẫn nên sửa ở gói nào có grant.
2. **`F-A3R1-02` chưa đóng bởi gói này.** Tôi làm phần sinh lại. Phần chứng minh —
   `tests/contract/test_schema_matches_entities.py`, khẳng định mọi cột sau `alembic upgrade
   head` phân giải về một trường của `entities.yaml` — thuộc `worker-WA`, và
   `PKT-PC02-FIX12` §L8 cũng nói đúng điều đó. `AMD-ENT-owner-01` vẫn **PROVISIONAL** cho tới
   khi Owner được trình và không phản đối.
3. **`F-A3R1-07` đóng ở tầng quy chủ sở hữu, không ở tầng hành vi.** Tôi nhận file và ghi
   hash; tôi **không** review chất lượng của ba test integration dùng nó — chúng thuộc card
   của chúng và có người review riêng.

## B.7 Kết thúc

`lease_released_at`: **2026-09-07T11:15Z** (`LEASE-P0-SKELETON-e3`, fencing 3). Sau dòng này
tôi không ghi thêm file nào. Không lệnh git mutation, không mạng, không secret, không
`__pycache__` lạc. Ba file được ghi trong gói này: `README.md`,
`shared/rr_contracts/generate.py` (docstring), và addendum này. `server/app/db/faults.py`
được **nhận** chứ không sửa. Mười sáu file sinh ra được **sinh lại** và không đổi byte nào.

---

# Addendum — `PKT-P0-FIX3`

- `packet_id`: `PKT-P0-FIX3` · `worker_principal`: `worker-WS` · `authority_id`:
  `AUTH-COORD-P0-FIX3` (parent `AUTH-OWNER-20260907-03`) · `lease_id`:
  `LEASE-P0-SKELETON-e4` (fencing 4) · **`status`: `DONE`** · `next_actor`: `Coordinator` ·
  `lease_released_at`: 2026-09-07T11:20Z.
- Đóng nốt mục 1 của `B.6` — thứ mà `PKT-P0-FIX2` phát hiện nhưng không có grant để sửa.
- MODIFY grant: `server/pyproject.toml` và mọi file khác tôi sở hữu còn in dạng `uv sync`
  trần. Thực tế chỉ **một** file cần sửa.

## C.1 Khảo sát trước khi sửa

Quét toàn repo (`*.toml`, `*.md`, `*.yml`, `*.yaml`, `Makefile`, `*.py`, `*.mjs`, trừ
`.venv/` và `node_modules/`) tìm mọi lần `uv sync` xuất hiện: **22 lần**, trong đó 13 nằm ở
`evidence/handoffs/P0-skeleton-handoff.md` (bản ghi lịch sử, xem C.4). Chín lần còn lại nằm
ở file mã và tài liệu sống, và **đúng một** trong chín là dạng trần:

| File | Trước | |
| --- | --- | --- |
| `server/pyproject.toml:25` | ``uv sync`` | **dạng trần — lỗi** |
| `.github/workflows/{e0,openapi,python}.yml` | `uv sync --all-packages --frozen` | đã đúng |
| `README.md:102` | `uv sync --all-packages --frozen` | đã đúng (`PKT-P0-FIX2`) |
| `README.md:22`, `README.md:29`, `tests/README.md:78`, `precode/README.md:92` | `uv sync --all-packages` | đã đúng |
| `Makefile:20` | `$(UV) sync --all-packages` | đã đúng (qua biến, không khớp grep chuỗi) |

`collector/pyproject.toml`, `worker/pyproject.toml`, `shared/rr_contracts/pyproject.toml` và
`pyproject.toml` gốc **không nhắc `uv sync` ở đâu cả** — không có gì để sửa trong chúng.

## C.2 Thay đổi — đúng một file, đúng một dòng

| File | Op | sha256 sau | Bytes |
| --- | --- | --- | --- |
| `server/pyproject.toml` | MODIFY (comment) | `fc171d93055860758d99283569073da39c978204057e07d0f884811796d5c7e9` | 1 159 |

```
- # Declared, NOT installed by `uv sync`. sentence-transformers pulls PyTorch (ADR-0011
- # "Tiêu cực và chi phí"); the embedding model itself is REQ-OQ09 / REQ-A3 and is not
- # chosen yet. No model is ever downloaded by this repo's test or CI paths.
+ # Declared, NOT installed by `uv sync --all-packages --frozen`. sentence-transformers pulls
+ # PyTorch (ADR-0011 "Tiêu cực và chi phí"); the embedding model itself is REQ-OQ09 / REQ-A3
+ # and is not chosen yet. No model is ever downloaded by this repo's test or CI paths.
```

Ba dòng comment được ngắt lại cho vừa giới hạn độ dài; **không một ký tự nào** của phần TOML
có nghĩa bị đụng tới. `tomllib.load` sau khi sửa: parse được, `optional-dependencies` vẫn
đúng một extra `embedding`.

## C.3 Hai dạng đúng, và vì sao repo cố ý giữ cả hai

Sau lần sửa này, **không còn dạng trần nào** ngoài `evidence/handoffs/`. Chín lần xuất hiện
chia thành hai dạng, và sự khác nhau là có chủ đích chứ không phải sót:

| Dạng | Ở đâu | Vì sao |
| --- | --- | --- |
| `uv sync --all-packages --frozen` | ba workflow CI, `README.md:102` (mô tả job CI), `server/pyproject.toml:25` | Ngữ cảnh **tái lập được**: `--frozen` bắt job **fail** thay vì lặng lẽ resolve lại khi `uv.lock` lệch với `pyproject.toml`. Một lockfile trôi là một build không tái lập được |
| `uv sync --all-packages` | `README.md:22` (khối cài đặt), `README.md:29`, `tests/README.md:78`, `precode/README.md:92`, `Makefile:20` (`make setup`) | Ngữ cảnh **cài đặt của người phát triển**: ở đây `--frozen` sẽ **có hại** — một người vừa clone về mà lock hơi cũ sẽ nhận một lỗi cứng thay vì một lần resolve |

Khiếm khuyết mà `F-A3R1-15` bắt được là **thiếu `--all-packages`** — dạng đó prune các
workspace member và sinh 11 lỗi collection. Cả chín lần nay đều mang cờ đó. Việc có hay không
`--frozen` là một trục **khác**, và nó đúng theo ngữ cảnh ở cả chín chỗ.

## C.4 Mười ba lần trong chính file này — cố ý không sửa

`evidence/handoffs/P0-skeleton-handoff.md` còn `uv sync` trần ở dòng 326 và 384, cùng các
trích dẫn ở §B.2 nhắc lại **nguyên văn chuỗi sai** đang được sửa. Cả hai loại đều **phải**
giữ nguyên: đây là bản ghi bằng chứng, `EV-P0-01` ghi lệnh thật đã chạy là
`uv sync --all-packages --frozen`, và một mục fix mà không trích được chuỗi hỏng thì không
đọc được. Sửa lời văn của một bản ghi đã qua audit tệ hơn hẳn cái nó sửa.

## C.5 Bằng chứng — `EV-P0-12`, `SELF_VALIDATION`

2026-09-07T11:18–11:20Z, `PYTHONDONTWRITEBYTECODE=1`, tại `/mnt/virtual/repo/xcrawl`.

| Cửa | Lệnh | Exit | Kết quả |
| --- | --- | --- | --- |
| Grep của packet | `grep -rn "uv sync" --include='*.toml' --include='*.md' --include='*.yml' --include='Makefile' .` (trừ `.venv/`, `node_modules/`, `evidence/handoffs/`) | — | **9 dòng, tất cả mang `--all-packages`**; 0 dạng trần |
| Grep mở rộng (thêm `*.yaml`, `*.py`, `*.mjs`) lọc lấy dòng **không** có `--all-packages` | — | — | **0 dòng** |
| TOML còn hợp lệ | `tomllib.load('server/pyproject.toml')` | **0** | parse OK, extra `embedding` nguyên vẹn |
| Cài đặt | `uv sync --all-packages --frozen` | **0** | `Checked 75 packages in 1ms` — không resolve lại |
| Lock không đổi | `sha256sum uv.lock` | — | `de2dccd2314abd1aec395a965adc53c019d06ad2d8e9aa004bf77692497b872d` — **giống hệt** `PKT-P0-SKELETON` |
| Toàn bộ suite | `uv run pytest -q -p no:cacheprovider` | **0** | **291 passed, 4 xfailed, 0 failed** — **không đổi** so với `PKT-P0-FIX2` |

Sửa một comment thì không được làm gì di chuyển, và bảng trên là cách chứng minh điều đó chứ
không phải cách khẳng định nó: `uv.lock` hash giống hệt, và số test giống hệt lượt trước.

## C.6 Kết thúc

`lease_released_at`: **2026-09-07T11:20Z** (`LEASE-P0-SKELETON-e4`, fencing 4). Hai file được
ghi trong gói này: `server/pyproject.toml` và addendum này. Không lệnh git mutation, không
mạng, không secret, không `__pycache__` lạc. `B.6` mục 1 nay **đóng**; mục 2 (`F-A3R1-02`,
`worker-WA`) và mục 3 vẫn thuộc người khác.

---

# Addendum — `PKT-P0-FIX4`

- `packet_id`: `PKT-P0-FIX4` · `worker_principal`: `worker-WS` · `lease_id`: `LEASE-P0-e5` ·
  **`status`: `DONE_WITH_CONCERNS`** · `next_actor`: `Coordinator` ·
  `lease_released_at`: 2026-09-08T00:20Z.
- Nguồn: `A3-P4-R1-report.md` `F-A3-P4-02` (MEDIUM) và `FIX-A3P4R1-rulings.md`.
- Lease: `pyproject.toml`, `uv.lock`, `.github/workflows/python.yml`, `Makefile`,
  `.gitignore`, `server/tests/test_smoke.py`, addendum này. Không file nào khác được ghi.
- **`DONE_WITH_CONCERNS`** vì suite đầy đủ có **1 fail** và hai cửa E0/card có FAIL — cả ba
  thuộc worker khác trong cùng đợt, không do gói này. Chi tiết ở D.5.

## D.1 Cái mà `F-A3-P4-02` thực sự tìm ra

`pyproject.toml` khai `files = ["server/app"]`, và ADR-0011 hàng "Lint / format" nói
`mypy --strict` **"cho lõi server"**. CI khớp ADR **chính xác** — nên không có gì trong
FC-P4 vi phạm. Vấn đề không phải một lần lệch chuẩn; nó là **chuẩn đã thôi phủ sản phẩm**.
ADR-0011 được viết khi `server/app` là mã sản phẩm Python **duy nhất**. Từ đó `worker/app`,
`collector/app` và `probe/` ra đời — adapter AI, collector, công cụ probe — và **không file
nào trong chúng được bất kỳ job CI nào kiểm kiểu**. Khoảng trống này rộng dần qua bốn giai
đoạn, không nhìn thấy được từ bên trong một card nào.

Đó là lý do sửa nằm ở gói bộ khung chứ không ở từng card: chỉ file bộ khung mới đổi được
phạm vi cửa, và `types-*` phải vào dev deps ở `pyproject.toml` gốc — đúng thứ đã chặn
`CR-TC-adapter-06`.

## D.2 Thay đổi

| File | Op | sha256 sau | Bytes |
| --- | --- | --- | --- |
| `pyproject.toml` | MODIFY | `9e98948fdae08ae333ecf9d4a47244c157c09ad14002d8b06f477c7ac1d55450` | 4 277 |
| `uv.lock` | MODIFY | `a4a274b3a4f0f0a9d41c40df7814e1e4387c541fc11a819763314101b0d1158c` | 193 757 |
| `server/tests/test_smoke.py` | MODIFY | `127f8fa8b7a46bb37bd8f23c3c029ee5f4c0f0e9bb391045aebb5d6e07c41186` | 7 905 |
| `.github/workflows/python.yml` | MODIFY | `a5f2b5ffe8adc380246ed717c966ec4617a8ed13a4bb1ff5ae0932b3d036e7ce` | — |
| `Makefile` | MODIFY | `4b69521180bb197520cca0529c7a2e65f632d59de8cd6dcfc7cefa066ee220ce` | — |
| `.gitignore` | MODIFY | `b972490e60228f85da4c130db7ab50997e6922667a00be5a0f107c2c2cacbf6c` | 1 081 |

### (1) Phạm vi mypy

```
- files = ["server/app"]
+ files = ["server/app", "worker/app", "collector/app", "probe"]
```

`strict = true` **giữ nguyên**. Số file đi từ **64 → 87** (`server/app` 64, `worker/app` 7,
`collector/app` 7, `probe` 9). Comment trong `pyproject.toml` nay nói thẳng **cái gì không
nằm trong danh sách và vì sao** — mã sinh ra (máy sinh, không sửa tay được) và các cây test.

### (2) Hai gói stub — đóng `CR-TC-adapter-06`

`types-PyYAML>=6.0,<7` và `types-jsonschema>=4.23,<5` vào `[dependency-groups] dev`. Resolve
thành `types-pyyaml==6.0.12.20260906` và `types-jsonschema==4.26.0.20260518` (123 gói, +2).
Chúng vào `pyproject.toml` gốc chứ không vào `worker/pyproject.toml` vì cửa là **toàn repo**
— và chính chỗ đặt này là thứ mà card không có quyền ghi, nên `CR-TC-adapter-06` mới bị kẹt.

Hai lỗi rộng-phạm-vi mà audit báo (`worker/app/adapter/base.py:39` `yaml`,
`worker/app/adapter/validate.py:40` `jsonschema`) là **thiếu stub, không phải lỗi kiểu** —
sau khi cài, cả hai biến mất mà **không một dòng mã sản phẩm nào** bị đụng tới.

### (3) `server/tests/test_smoke.py` — sửa thật, và quyết định về phạm vi được ghi rõ

**Quyết định (packet yêu cầu nêu tường minh): cây test KHÔNG nằm trong `files`.** Ba lý do,
ghi cả trong `pyproject.toml`:

1. Fixture pytest đến từ plugin và phần lớn **không có kiểu**; `--strict` ở đó đo plugin
   nhiều hơn đo test.
2. `tests/`, `collector/tests`, `worker/tests`, `shared/rr_contracts/tests` **thuộc card
   khác**. Đưa chúng vào cửa nghĩa là bộ khung có thể **chặn** worker của những card đó —
   một quyền mà gói này không nên có.
3. ADR-0011 đặt cửa cho **mã sản phẩm**; mở rộng sang test là một quyết định khác, cần ADR
   riêng.

**Nhưng file smoke là file của Giai đoạn 0, nên tôi sửa nó cho sạch dù cửa không với tới.**
Năm lỗi, hai lớp:

- `client.app.title` / `client.app.routes` — `TestClient.app` mang kiểu ASGI callable, không
  có `.title` hay `.routes`. Sửa **không** bằng `cast` (cast sẽ nói dối về kiểu của vật):
  thêm một fixture `app() -> FastAPI` riêng, `client(app)` dựng trên nó, và hai test dùng
  thẳng `app`. Kiểu thật đi suốt.
- `int(pragmas["foreign_keys"])` ×3 — `read_pragmas` trả `dict[str, object]` vì `PRAGMA` trả
  đúng kiểu của chính pragma đó (chuỗi cho `journal_mode`, số cho ba cái kia). Sửa bằng một
  helper `_pragma_int` **assert `isinstance(value, int)`** rồi mới trả. Thu hẹp bằng assert
  chứ không bằng cast, nên nếu một ngày pragma trả về text thì test **fail to tiếng** thay
  vì âm thầm biến phép so sánh thành vô nghĩa. Hai `# type: ignore[no-untyped-def]` trên
  `tmp_path` cũng được thay bằng annotation `Path` thật.

`uv run mypy --strict server/tests/test_smoke.py` → **`Success: no issues found in 1 source
file`**. `pytest` trên chính file đó → **8 passed**.

### (4) Tên bước CI và Makefile

| Chỗ | Trước | Sau |
| --- | --- | --- |
| `.github/workflows/python.yml` | `mypy --strict (server core)` | `mypy --strict (all Python production trees)` + comment nêu bốn cây |
| `Makefile` mục tiêu `lint` | `mypy (server core)` | `mypy --strict (server/worker/collector/probe)` |

**Ngoài lease:** `.pre-commit-config.yaml:35` vẫn ghi `name: mypy --strict (server core)`.
File đó không nằm trong lease của gói này; hook chạy đúng lệnh (`uv run mypy`, phạm vi lấy từ
`pyproject.toml`) nên **hành vi đúng, chỉ nhãn cũ**. Cần một gói có grant để đổi.

### (5) `.gitignore`

`__pycache__/` và `*.py[cod]` **đã có từ `PKT-P0-SKELETON`**; tôi thêm `*.pyc` tường minh
theo packet và một comment giải thích. Quan trọng hơn con số dòng: tôi **chứng minh** các
luật thật sự bắt, thay vì khai là chúng có:

```
$ git check-ignore -v -- server/app/__pycache__/x.pyc worker/app/__pycache__/y.pyc probe/z.pyc collector/app/w.pyo
.gitignore:6:__pycache__/   server/app/__pycache__/x.pyc
.gitignore:6:__pycache__/   worker/app/__pycache__/y.pyc
.gitignore:8:*.pyc          probe/z.pyc
.gitignore:7:*.py[cod]      collector/app/w.pyo
```

Cả bốn đều bị bỏ qua, ở mọi độ sâu. **Nên cache lạc trong đợt này không đến từ lỗ hổng
trong `.gitignore`** — chúng đến từ lượt chạy quên `PYTHONDONTWRITEBYTECODE=1`. Comment mới
trong file nói đúng điều đó, để lần sau không ai đi vá nhầm chỗ.

## D.3 Bằng chứng — `EV-P0-13`, `SELF_VALIDATION`

2026-09-08T00:05–00:18Z, `PYTHONDONTWRITEBYTECODE=1`, `/mnt/virtual/repo/xcrawl`.

| Cửa | Exit | Kết quả |
| --- | --- | --- |
| `uv lock` + `uv sync --all-packages` | **0** | 123 gói resolve; `+ types-jsonschema==4.26.0.20260518`, `+ types-pyyaml==6.0.12.20260906` |
| **`uv run mypy`** (phạm vi mới) | **0** | **`Success: no issues found in 87 source files`** |
| `uv run mypy --strict server/tests/test_smoke.py` | **0** | `Success: no issues found in 1 source file` |
| `uv run ruff check .` | **0** | `All checks passed!` |
| `uv run ruff format --check .` | **0** | 165 file |
| `pytest server/tests/test_smoke.py` | **0** | 8 passed |
| `git check-ignore -v` (4 đường dẫn) | — | 4/4 bị bỏ qua |
| **`uv run pytest`** (toàn bộ) | **1** | **1 030 passed, 1 failed, 5 xfailed** — xem D.5 |
| `evidence/tools/e0_check.py` | — | **27 checks: PASS 26 · FAIL 1** — xem D.5 |
| `evidence/tools/verify_cards.py` | — | **12 PASS / 1 FAIL**, 3 730 assertion, 38 vi phạm — xem D.5 |

Trước lúc cài stub, phạm vi rộng cho đúng **2 lỗi**, cả hai là `import-untyped`. Sau khi cài:
0. **Không một dòng mã sản phẩm nào ngoài lease bị sửa** — đúng chỉ thị của packet.

## D.4 Điều gói này **không** chứng minh

Cửa nay **với tới** 87 file; nó không nói rằng 23 file mới vào phạm vi là **đúng**. Chúng
sạch dưới `--strict` — mỗi worker đã tự báo strict-clean cho gói của mình, và lượt chạy này
xác nhận điều đó ở mức toàn repo. `--strict` bắt được thiếu annotation và sai kiểu; nó không
bắt được logic sai. Ngoài ra cửa vẫn **không** với tới cây test và mã sinh ra, theo quyết
định ở D.2 (3).

## D.5 Ba cửa đỏ — không cửa nào của gói này

Tôi báo cả ba thay vì im lặng, và cả ba đều là **việc đang bay của worker khác trong cùng
đợt**, đúng như dòng `Order` của ruling dự liệu.

**(a) `pytest` — 1 fail: `tests/integration/test_pending_survives_cursor.py::test_fixture_e_the_late_discovery_is_still_a_new_discovery`.**
Lý do nguyên văn: `[XPASS(strict)] CR-TC-BACKFILL-09: publisher._write_first_announcements
announces an item whose summary_state is still 'pending', so the late discovery returns as
prior_reference`. Đây **chính là** `F-A3-P4-01`, và nó **XPASS** nghĩa là **W4A đã sửa xong**
`publisher`; bước còn lại theo ruling là *"W4B then flips its strict xfail (gated on W4A's
addendum)"*. Một `xfail(strict=True)` đã hết lý do tồn tại — tức là một tin **tốt** hiển thị
dưới dạng đỏ. Không thuộc lease của tôi; sửa nó là W4B.

**(b) `e0_check.py` — 1 FAIL: `E0-21-marker-reason-freshness`** trên
`tests/integration/test_denied_edges.py`: marker nói `TC-storage-write-blocked-readiness`
còn thiếu, nhưng handoff của card đó đã tồn tại. Đây là check **mới** mà PC09-P4 vừa thêm
theo `F-A3-P4-03`, và nó đang bắt đúng thứ nó sinh ra để bắt. File thuộc card khác.

**(c) `verify_cards.py` — `pins` FAIL, 38 vi phạm** trên hai file:
`precode/adr/ADR-0011-frameworks-and-toolchain.md` (`da5181b2…` → `defbe74e…`) và
`precode/decision-register.md` (`8d6a87fb…` → `a38e2ce1…`). Đó là **W1n** đang sửa ADR-0011
theo cùng finding `F-A3-P4-02` này. Ruling xếp `WP re-pin P4b (ADR-0011 moved)` **sau** W1n
và tôi, nên pin lệch ở thời điểm này là **đúng lịch**, không phải hỏng.

Không cửa nào trong ba cửa trên đổi trạng thái vì thay đổi của tôi: sửa của tôi gồm cấu hình
mypy, hai gói stub chỉ-kiểu (không có mã chạy), một comment `.gitignore`, hai nhãn, và một
file test của chính Giai đoạn 0.

## D.6 Kết thúc

`lease_released_at`: **2026-09-08T00:20Z** (`LEASE-P0-e5`). Sáu file trong lease được ghi,
cộng addendum này. Mạng chỉ dùng để cài hai gói stub từ PyPI, đúng như packet cho phép.
Không lệnh git mutation, không secret, không `__pycache__` lạc.

Việc còn mở thuộc người khác: nhãn `.pre-commit-config.yaml` (ngoài lease), `F-A3-P4-01`
(W4A/W4B), `E0-21` trên `test_denied_edges.py`, và re-pin P4b (WP, sau khi W1n xong ADR-0011).
