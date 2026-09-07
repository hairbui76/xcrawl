---
handoff_id: TC-x-feasibility-probe-handoff
packet_id: TC-x-feasibility-probe
worker_principal: worker-WX
authority_id: AUTH-COORD-TC-PROBE
parent_authority: AUTH-OWNER-20260907-04
lease_id: LEASE-TC-PROBE-e1
pin_epoch: PC10-PIN-P2-20260907
decision_refs: [OD-20260907-01, OD-20260907-02, OD-20260907-03, B05, B12, AMD-B02, AMD-B05, AMD-B08, ADR-0001, ADR-0006, ADR-0011, CR-PC05-01, CR-PC10-02]
invariant_refs: [I03, I10]
scenario_refs: [SC01, SC03, SC04, SC49]
requirement_refs: [REQ-A1, REQ-A7, REQ-D09, REQ-D24, REQ-D31, REQ-D32, REQ-D33, REQ-OQ05, REQ-AC01, REQ-AC03, REQ-AC04, REQ-S9.3-01, REQ-S9.3-02, REQ-S13.2-04]
evidence_manifest_id: EVM-TC-x-feasibility-probe
next_actor: Coordinator
lease_released_at: 2026-09-07T14:15Z
---

# HANDOFF — TC-x-feasibility-probe (M0, SP1): công cụ probe và runbook. Probe **chưa chạy**.

## 1. Danh tính và trạng thái

| Trường | Giá trị |
| --- | --- |
| `card_id` | `TC-x-feasibility-probe` · pin epoch `PC10-PIN-P2-20260907` |
| `worker_principal` | `worker-WX` |
| `authority_id` | `AUTH-COORD-TC-PROBE` (parent `AUTH-OWNER-20260907-04`, bản ghi `OD-20260907-03`) |
| `lease_id` | `LEASE-TC-PROBE-e1` (exclusive; message-tracked, không guard mức OS) |
| **`status`** | **`DONE_WITH_CONCERNS`** |
| `completion_claim` | `DRAFT_FOR_REVIEW`. **Không** `LIVE_FEASIBILITY_VERIFIED` và không gì gần nó |
| `next_actor` | `Coordinator` |
| `lease_released_at` | 2026-09-07T14:15Z |

**Trần thi hành của packet này là công cụ + runbook, và đó đúng là những gì tồn tại.** Không
một đợt probe nào đã chạy. Bằng chứng khả thi nguồn X: **`NOT_RUN`**.

**Vì sao `DONE_WITH_CONCERNS` chứ không phải `DONE`.** Sáu change request mở (mục 7), trong
đó hai cái là mâu thuẫn **thật** giữa card §8/§13 và hợp đồng/packet, và một cái
(`CR-TC-PROBE-06`) là một phụ thuộc chưa khai báo mà tôi **không** được phép tự sửa
(`SG-STACK`: chọn toolchain là việc của change control).

**Vì sao không `BLOCKED`.** Card `SG-02` chặn **việc chạy probe**, không chặn việc viết công
cụ và runbook; packet điều phối nói rõ trần của packet này là tooling. Tôi dừng đúng ở ranh
giới đó: `run_probe.py` **từ chối mở trình duyệt** khi cổng §6 chưa đủ bốn xác nhận, và
`evidence/runs/SP1-x-feasibility/runs.jsonl` **không tồn tại**.

## 2. Hai điều chặn probe live — nêu tên, không diễn giải

1. **Cổng Owner `collector-probe.md` §6, mục 2–4.** `OD-20260907-03` ghi thẳng ở dòng
   "Not decided in this round": *"probe gate items 2–4"* chưa được quyết. Mục 1 (D09) đã trả
   lời ở `OD-20260907-01`. Card `SG-02`: **stop tuyệt đối**, probe **không được chạy**.
2. **Máy của Owner.** Probe drives Chrome thật, profile riêng của dự án, tài khoản X thật
   (REQ-D09, `ADR-0001`, `ACT-collector.runs_on = personal_machine`). Không CI, không agent,
   không máy nào khác chạy được nó — và packet này không được phép thử.

Cả hai đều **ngoài** tầm của Worker. Không thứ gì trong gói này nới được chúng, và cổng §6
được cài **vào code** chứ không chỉ vào tài liệu, vì một cổng chỉ có trong văn xuôi là cổng
không ai kiểm được.

## 3. Kết quả từng stop gate của card §10

| Cổng | Kết quả |
| --- | --- |
| `SG-01` | **Không trigger.** D09 đã được Owner trả lời (`OD-20260907-01` mục 1). Probe vẫn `NOT_RUN` — đó là việc phải làm, không phải việc đã làm |
| `SG-02` | **TRIGGER, và được tôn trọng.** Ba trong bốn xác nhận §6 còn thiếu ⇒ `OWNER_DECISION_REQUIRED`. Không đợt nào chạy. `config.ProbeConfig.owner_gate()` + `run_probe.check_owner_gate()` cài cổng này vào code; `main()` trả mã thoát `2` **trước khi** `open_driver` được gọi (test `test_cli_refuses_when_the_owner_gate_is_closed` monkeypatch `open_driver` thành một hàm ném AssertionError, nên nếu cổng lọt thì test đỏ) |
| `SG-03` | **Không trigger** (không có gì để bị chặn). Hành vi khi bị chặn đã cài: `source_blocked` ⇒ dừng hẳn, mã thoát 3, không luân chuyển gì |
| `SG-04` | **Không trigger.** Gói này không chạm connector nghiên cứu. `SL-4 chrome_scope: x_only` được `config` ép: `x_base_url` phải là host X, arXiv/OpenAlex bị từ chối ngay ở cấu hình |
| `SG-STACK` | **Không trigger, nhưng suýt.** Không chọn framework mới: Playwright đã do `ADR-0011` và `collector/pyproject.toml` nêu tên. Chỗ *suýt* là `probe/` chưa khai phụ thuộc — tôi **không** sửa `pyproject.toml`; xem `CR-TC-PROBE-06` |
| `SG-G5` | **Không trigger.** `OD-20260907-03` mục 3 là lệnh bắt đầu Giai đoạn 2 bằng văn bản; card §0 mang `dispatch_status: DISPATCHED` |
| `SG-PC09` | **Đã kiểm.** `acceptance/scenarios.yaml` nay tồn tại (sha256 `ca372775e943c49776ae853615bad275054773f8808eab12aa085651ca07ea17`). Đọc SC01/SC03/SC04/SC49: **không mâu thuẫn** với §8. Cả bốn là scenario cấp server/wire mà probe M0 (dry-run) không chạm — đúng như `collector-probe.md` §10 mục 6 đã nói. Chúng vẫn `NOT_RUN` |
| `SG-DENY` | **Không trigger.** Card không sở hữu operation nào và không mở cạnh nào. Ràng buộc default-deny áp dụng được ở đây là `SL-4`/`DC-COL-07`, đã cài ở `config` và kiểm ở `test_x_probe_boundaries.py` |
| `SG-HASH` | **Đã chạy hai lần.** Xem mục 4 |
| `SG-CONTRACT` | **Không trigger.** Không sửa hợp đồng, fixture hay expectation nào. Một điểm dễ đọc nhầm (`captcha` vs `challenge_required`) hóa ra **không** phải mâu thuẫn — xem mục 6 |
| `SG-EDGE` | **Không trigger.** Không cần cạnh, bảng, secret hay capability nào ngoài §5 |

## 4. Baseline — kiểm hai lần

Card đã được **pin lại** trong lúc gói này chạy: epoch `PC10-PIN-P1d-20260907` →
**`PC10-PIN-P2-20260907`** (`OD-20260907-03` mở Giai đoạn 2), và ba dòng hash đổi:
`precode/baseline.json`, `precode/decision-register.md`, `contracts/data/entities.yaml`.
Tôi đọc lại card, kiểm lại **toàn bộ 19 dòng** của §0 theo bảng **mới**, và **cả 19 khớp**.

`contracts/ops/collector-probe.md` — hợp đồng mà toàn bộ gói này dựa vào — **không đổi**
(`03e88010ce8d9a8e7ed7afbb5ab01caf4099ac77cde1298fb155731dddd55ca1`, 26 780 B) ở cả hai lần
kiểm, nên không có mét vuông nào của công việc phải làm lại. Card §3, §8 và §10 cũng không
đổi.

| Lần kiểm | Thời điểm | Kết quả |
| --- | --- | --- |
| 1 (trước dòng code đầu tiên) | 2026-09-07T13:27Z | 19/19 khớp bảng §0 epoch `P1d` |
| 2 (sau khi card được pin lại) | 2026-09-07T13:34Z | 19/19 khớp bảng §0 epoch `P2` |
| 3 (trước handoff) | 2026-09-07T14:12Z | 19/19 khớp; `SRC-SPEC` và `SRC-PLAN` không đổi |

## 5. Bằng chứng — tất cả `SELF_VALIDATION`

Mọi lệnh chạy tại `/mnt/virtual/repo/xcrawl` với `PYTHONDONTWRITEBYTECODE=1`. **Không lệnh
nào chạm mạng.** Không `playwright install`, không binary trình duyệt, không request nào tới
x.com. Mục nào không chạy được ghi `NOT_RUN` chứ không suy diễn.

### EV-TC-PROBE-01 — bằng chứng probe live

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION` (không có gì để tự kiểm: không có lần chạy) |
| `command` | *(không có)* |
| `oracle` | `collector-probe.md` §7 GO-1…GO-7 trên 5 ≤ N ≤ 10 đợt |
| `observed` | N = 0 |
| **`result`** | **`NOT_RUN`** |
| `blockers` | (1) `collector-probe.md` §6 mục 2–4 `OWNER_DECISION_REQUIRED`; (2) cần máy + tài khoản X của Owner |
| `manifest` | `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` |

### EV-TC-PROBE-02 — test ngoại tuyến của công cụ

| Trường | Giá trị |
| --- | --- |
| `type` | `SELF_VALIDATION`, mức E1 |
| `command` | `PYTHONDONTWRITEBYTECODE=1 uv run pytest tests/contract/test_x_probe_signals.py tests/contract/test_x_probe_record.py tests/contract/test_x_probe_go_no_go.py tests/contract/test_x_probe_boundaries.py -p no:warnings` |
| `started/ended` | 2026-09-07T14:00Z / 2026-09-07T14:00Z |
| `expected` | mọi test pass; không test nào cài hay mở trình duyệt |
| `observed` | **156 passed, 0 failed, 0 skipped, 0 xfailed** trong 2,37 s |
| `exit_code` | `0` |
| `result` | `PASS` |
| `limitations` | Chống đỡ cho **công cụ**, không cho khả thi nguồn X. Selector và marker là PROVISIONAL (`PROV-WX-01`) |

Phân bố: `test_x_probe_signals.py` 28 · `test_x_probe_record.py` 38 · `test_x_probe_go_no_go.py`
25 · `test_x_probe_boundaries.py` 65.

### EV-TC-PROBE-03 — lint và type

| Lệnh | Kết quả | `exit_code` |
| --- | --- | --- |
| `uv run ruff check probe/ tests/contract/test_x_probe_*.py` | `All checks passed!` | `0` |
| `uv run ruff format --check probe/` | không file nào cần format lại | `0` |
| `uv run mypy probe` | `Success: no issues found in 9 source files` (`--strict`, theo cấu hình `[tool.mypy]` của repo) | `0` |

### EV-TC-PROBE-04 — manifest validate được với schema

| Trường | Giá trị |
| --- | --- |
| `command` | `uv run python -c "…Draft202012Validator(schema).iter_errors(manifest)…"` |
| `oracle` | `evidence/manifest.schema.json` sha256 `25ddb1b7afb529b0ca9500fa2f293897723406a704a25d71b0c0ed187607dfd8` |
| `observed` | `VALID against evidence/manifest.schema.json` — 0 lỗi |
| `result` | `PASS` |

### EV-TC-PROBE-05 — CLI chạy ngoại tuyến, cổng từ chối đúng

Chạy với file cấu hình **trong scratch**, profile trỏ vào thư mục scratch rỗng. **Không mở
trình duyệt lần nào** (mọi lần đều dừng ở cổng hoặc ở `--dry-run`).

| Lệnh | Quan sát | `exit_code` |
| --- | --- | --- |
| `uv run python probe/x_feasibility/run_probe.py --config <scratch>/cfg.json --dry-run` | in đúng ba mục §6 còn thiếu, kèm `OWNER_DECISION_REQUIRED` và tham chiếu `SG-02` | `2` |
| cùng lệnh, cấu hình scratch bật đủ bốn xác nhận | `{"gate": "open", …, "note_vi": "…KHÔNG mở trình duyệt, KHÔNG chạm X…"}` | `0` |
| `… --runs 5` (đúng ví dụ ở card §8) | `--runs 5 vượt §3.1 probe_runs_per_day_max = 4…` | `2` |
| `uv run python probe/go_no_go.py <scratch>/out/runs.jsonl` | `Không tìm thấy file JSONL` | `3` |

> Bốn xác nhận trong file scratch mang `evidence_ref: "SCRATCH-TEST (không phải xác nhận thật
> của Owner)"`, file nằm ngoài repo và đã bị bỏ đi. **Không** có nghĩa cổng §6 đã mở.

### EV-TC-PROBE-06 — toàn cây test của repo

| Trường | Giá trị |
| --- | --- |
| `command` | `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:warnings --tb=no` |
| `observed` | `2 failed, 569 passed, 4 xfailed in 52.11s` |
| `result` | `PASS` cho phạm vi card này; hai fail **không thuộc gói này** |

Hai fail và vì sao chúng không phải của tôi:

1. `tests/integration/test_identity_merge_audit.py::test_migration_chain_resolves_to_a_single_head`
   — test đó hard-code `heads == ["0004_merge_phase1_heads"]`, nhưng
   `server/migrations/versions/0005_tc_research_connector_metadata.py` đã xuất hiện (card 2B
   chạy song song). Card này **không tạo migration nào** — nó không chạm DB (§4: "Không DB").
2. `tests/integration/test_collector_resume_after_challenge.py::…` — file của card
   `TC-collector-checkpoint-resume` đang được viết song song.

Tôi **không** sửa cả hai: chúng nằm ngoài write set, và sửa một tín hiệu STALE thật của gói
khác là đúng thứ `agent_profile/worker.md` cấm. Báo lại để Coordinator định tuyến.

## 6. Changes — mọi file

**26 file mới + 1 file sửa. 213 568 byte mới** (đã tính cả manifest và chính file handoff
này ở mục 6.3). Tất cả `CREATE` từ baseline `ABSENT`, trừ dòng ở mục 6.4.

### 6.1 Write set của card §3

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `probe/x_feasibility/run_probe.py` | CREATE | ABSENT | `5476c862ab348e7fd89ff207c177d9c93652ebb8b443eda02ca44753b0e11107` | 24809 |
| `probe/x_feasibility/record.py` | CREATE | ABSENT | `6e3a3fbbea9b02271e9bc4641770c63241975b9ae7c5789975373203925fe50b` | 16212 |
| `evidence/runs/SP1-x-feasibility/README.md` | CREATE | ABSENT | `be67e9e128196a2a89d9c21d8730db0fd2587b239f2af0db1561979d1fd701d8` | 3711 |
| `evidence/runs/SP1-x-feasibility/TEMPLATE-run-record.json` | CREATE | ABSENT | `4200219a29131d6415bc4c9e7736eab317902eb9d5d2d2a8f9ac2f768101dbd0` | 3165 |

### 6.2 Ngoài chữ của §3, trong chữ của packet điều phối

Packet yêu cầu thẳng: bộ dò tín hiệu, script go/no-go tại `probe/go_no_go.py`, runbook tại
`probe/README.md`, và test ngoại tuyến. Card §3 chỉ liệt kê hai file `.py`. Tôi theo
**packet** (chỉ dẫn cụ thể hơn) và báo lệch ở `CR-TC-PROBE-05`.

| Path | Op | Before | After (sha256) | Bytes | Vì sao |
| --- | --- | --- | --- | --- | --- |
| `probe/x_feasibility/__init__.py` | CREATE | ABSENT | `422e3baa6f9937aab0d9fca75871b0ddb95a3f4e78ce989d99a7ba6bfbb3c6e8` | 1895 | gói Python + `PROTOCOL_VERSION` |
| `probe/x_feasibility/config.py` | CREATE | ABSENT | `4b60124eda876151daae0d744aed1faaa8a61fb776712d338fa4d641093d1da1` | 15185 | cổng §6, cổng profile D09, ngân sách §3 |
| `probe/x_feasibility/signals.py` | CREATE | ABSENT | `53265c58220434f38b73bae8fadf9caa29a8554723b311e9cba65d80460de13f` | 17371 | bộ dò §4 (thuần, không I/O) |
| `probe/x_feasibility/dom.py` | CREATE | ABSENT | `5be94dcb1df80414864de9c14d23ea8b2cbd15517bc7a906e9679e2e99293feb` | 9227 | selector X + bộ đọc HTML ngoại tuyến |
| `probe/x_feasibility/go_no_go.py` | CREATE | ABSENT | `438954ba3637aff649122c089764f4991d05ee991deacbe86037a937e08fe4a9` | 9954 | §7 nguyên văn |
| `probe/go_no_go.py` | CREATE | ABSENT | `a75c59fa39a2d6d17c2afc2f609a61a02dea099408e734b39430c94d928c9229` | 1183 | lối vào đúng tên packet đặt |
| `probe/probe-config.example.json` | CREATE | ABSENT | `a0759663b31a2bebd29b7550c8e68ed75c9a984ebce10a9dcc739fba3c62859c` | 2219 | mẫu cấu hình (không secret) |
| `tests/contract/test_x_probe_signals.py` | CREATE | ABSENT | `9583bcedbf0b0b5a44029f29fb93db7d18cd29499af204ca836b4826d2f856b4` | 13107 | 28 test |
| `tests/contract/test_x_probe_record.py` | CREATE | ABSENT | `77a9e8e2c3d89a73a611af97918e583eabd1f4ef1414ec52f67de380d301959e` | 11940 | 38 test |
| `tests/contract/test_x_probe_go_no_go.py` | CREATE | ABSENT | `c916af7a9a677cf4053cd295b60c96f6b7f29a2cf1dc302ef19882f34e70bf56` | 9637 | 25 test |
| `tests/contract/test_x_probe_boundaries.py` | CREATE | ABSENT | `2e7fc0ac167e0d32f40d364e610b2f05f0637627e5b84b2b990bfd92c850022c` | 22214 | 65 test |
| `tests/contract/x_probe_synthetic_pages/README.md` | CREATE | ABSENT | `59d0e689c44358ff8efeda2e15866bd579e0a0b6a950a664e080c69211952d83` | 3184 | vì sao HTML ở đây, không ở `acceptance/` |
| `tests/contract/x_probe_synthetic_pages/healthy-feed.html` | CREATE | ABSENT | `8447e44f3aba0513d85a814af1bb8ef140a31f5b97eba3bd2090ce497ebdbc9e` | 1752 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/challenge-verify.html` | CREATE | ABSENT | `3a998cd904cd032fe4284a0e0a2b9e9a9c7b5e2fec2d04a07aa645ff24eb9d6c` | 457 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/challenge-arkose-iframe.html` | CREATE | ABSENT | `8c7dce610d6181a3022f80d213700cb038f4e4d6081fb55d22513e91119a27a5` | 435 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/session-expired-login.html` | CREATE | ABSENT | `092eda2f5652b3776e156901e9ccf82f5e8e5c0734490f9a199c679db6570c11` | 363 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/access-blocked.html` | CREATE | ABSENT | `65264159114c84907025df2d56138afac87217a408512c69d90bcff7d5b24e2d` | 338 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/rate-limited.html` | CREATE | ABSENT | `7e820504499c4df417a86a81b73f913ff67f4a0bd3c30fad7f0e75e7d7d544e0` | 369 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/layout-changed-missing-fields.html` | CREATE | ABSENT | `854a64fe5a3184d4bb3e03ba78ea241442e519b78a1edeab96e817fd1cc9242a` | 889 | trang tổng hợp |
| `tests/contract/x_probe_synthetic_pages/layout-changed-no-containers.html` | CREATE | ABSENT | `f11e5e8918ea9383e481cb03375232979824053cf8d466a340d65d83a2e475b4` | 551 | trang tổng hợp |

### 6.3 Handoff và manifest (packet điều phối mục 2 và 8)

| Path | Op | Before | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` | CREATE | ABSENT | `0a3e67c3a6cdb9ef354d332ab9355b6c058d39ffb6d217a01e85775511e5deb3` | 12139 |
| `evidence/handoffs/TC-x-feasibility-probe-handoff.md` | CREATE | ABSENT | *(chính file này)* | — |

### 6.4 File duy nhất bị SỬA

| Path | Op | Before (sha256) | After (sha256) | Bytes |
| --- | --- | --- | --- | --- |
| `probe/README.md` | MODIFY (viết lại toàn bộ) | `7495be45e780279b271839d40e631c137dc19f9df393695398e8289995816893` (1885 B, bản Giai đoạn 0) | `5b97af5c05c8603bddb2938e4d6526db7f600b5f93c6100ae5632f294eb70167` | 17026 |

Bản Giai đoạn 0 mở đầu bằng *"Chưa có code ở đây, và đó là đúng"* — câu đó nay **sai**, và
để nguyên nó là để một câu sai làm cửa vào thư mục. Bản mới là runbook packet yêu cầu, và nó
giữ nguyên điều bản cũ nói đúng: cổng §6 nằm **trước** khi probe chạy, không phải sau.

**Không** file nào khác bị chạm. `contracts/`, `acceptance/`, `precode/` **read-only** và
không byte nào đổi. Không lệnh git nào làm biến đổi repo. Không `__pycache__`
(`PYTHONDONTWRITEBYTECODE=1`, đã kiểm bằng `find`).

## 7. Change requests

### `CR-TC-PROBE-01` — card §8 nêu `--runs 5`, mâu thuẫn `collector-probe.md` §3.1

Card §8: `python probe/x_feasibility/run_probe.py --runs 5`. Nhưng §3.1 đặt
`probe_runs_per_day_max = 4` **và** `probe_min_gap_minutes = 60` **và**
`probe_span_days_min = 3`. Năm đợt trong một lần gọi phá cả ba.

**Đã làm:** `run_probe.py` **từ chối** `--runs 5` kèm đúng điều khoản từ chối nó (xem
EV-TC-PROBE-05), và runbook §6 chỉ nhịp đúng: `--runs 1`, hai lần/ngày, trong 3–5 ngày —
cũng chính là nhịp vận hành 08:00/20:00 mà probe cần đo. **Không** nới ngưỡng để hợp với ví
dụ của card. **Đề nghị:** sửa ví dụ ở card §8 thành `--runs 1`.

### `CR-TC-PROBE-02` — lệnh ở card §8 không chạy được nếu không có bootstrap `sys.path`

`README.md` §4 chốt import root là **gốc repo** (`probe/…` import là `probe.…`). Nhưng
`python probe/x_feasibility/run_probe.py` đặt `probe/x_feasibility/` lên `sys.path`, không
phải gốc repo ⇒ `ModuleNotFoundError: No module named 'probe'` ngay dòng import đầu tiên
(đã tái hiện).

**Đã làm:** thêm một bootstrap `sys.path` **có bảo vệ** (`if __name__ == "__main__" and
__package__ in {None, ""}`) ở đầu hai file lối vào, kèm `# ruff: noqa: E402` và giải thích.
Nó là no-op khi import và khi chạy bằng `-m`. **Đề nghị:** hoặc giữ nguyên, hoặc đổi card §8
sang `uv run python -m probe.x_feasibility.run_probe` và bỏ bootstrap. Đây là lựa chọn của
change control, không phải của tôi.

### `CR-TC-PROBE-03` — vị trí evidence manifest: card §13 ≠ packet điều phối

Card §13: `evidence/runs/TC-x-feasibility-probe/manifest.json` (PROVISIONAL). Packet điều
phối mục 2 và mọi tiền lệ Giai đoạn 1 (`TC-owner-auth-session-E1-…json` v.v.):
`evidence/runs/<card>-E1-<UTC>.json`. Tôi theo **packet + tiền lệ**. **Đề nghị:** sửa card
§13 cho khớp, để card sau không phải chọn lại.

### `CR-TC-PROBE-04` — `evidence/index.json` chưa được cập nhật

Card §13 nói *"Đăng ký run vào `evidence/index.json`"*. File đó **không** nằm trong write set
(packet mục 2), do PC09 sở hữu và được **sinh ra**, không sửa tay. Tôi **không** chạm nó.
**Cần:** Coordinator sinh lại index để bản ghi `EV-E1-01-tc-x-feasibility-probe` xuất hiện.

### `CR-TC-PROBE-05` — card §3 không có đường dẫn test, nhưng packet bắt buộc có test

Card §3 chỉ có hai file `.py` và một thư mục evidence. Packet điều phối yêu cầu test ngoại
tuyến cho bộ dò, cho JSONL và cho go/no-go, "under the card's test paths" — card không có
đường dẫn nào như vậy.

**Đã làm:** đặt test ở `tests/contract/` (đã nằm trong `testpaths` của `pyproject.toml`, nên
CI chạy chúng mà **không** phải sửa file dùng chung), và HTML tổng hợp ở
`tests/contract/x_probe_synthetic_pages/` kèm README giải thích vì sao chúng **không** nằm ở
`acceptance/fixtures/` (`README.md` §3.2: fixture là oracle duy nhất — HTML này là **đầu
vào** của unit test, không phải oracle của scenario; oracle vẫn là `contracts/` và bốn
fixture `collection/{a,c,e,g}`, và test đọc thẳng chúng). **Đề nghị:** bổ sung hai đường dẫn
này vào card §3.

### `CR-TC-PROBE-06` — `probe/` phụ thuộc `playwright` mà không khai báo

`probe/` **không** là thành viên `uv` workspace và không có `pyproject.toml`.
`probe/x_feasibility/run_probe.py` import `playwright`, gói này chỉ được khai ở
`collector/pyproject.toml`. Hôm nay chạy được vì cả workspace dùng chung một venv — nhưng
phụ thuộc của `probe/` đang **không được khai báo**, và một lần cài chỉ-server sẽ làm probe
gãy trên máy Owner.

Tôi **không** sửa: `pyproject.toml` là file dùng chung ngoài write set, thêm thành viên
workspace là thay đổi toolchain, và `SG-STACK` nói rõ chọn framework/thư viện ⇒ DỪNG và raise
CR. **Cần quyết:** thêm `probe` vào `tool.uv.workspace.members` với `probe/pyproject.toml`
khai `playwright`, hay ghi rõ probe dùng venv của collector.

### `CR-TC-PROBE-07` (thấp) — hai cách viết cho cùng một tình huống

`collector-probe.md` §5 dùng `captcha`; `worker.report_stop` trên wire
(`contracts/http/openapi.yaml`, `contracts/ports.yaml`) dùng `challenge_required`; fixture
`c-challenge-mid-batch` dùng bản wire. **Đây không phải defect** — §5 nói rõ sáu giá trị đầu
khớp `run.yaml`, và `run.yaml` §1 đúng là `captcha`. Hai từ vựng, hai lớp.

Nhưng nó là một cái bẫy đọc thật: người viết collector rất dễ ghi nhầm giá trị vào cột nhầm.
`probe/x_feasibility/signals.py` giữ **cả hai** trong `STOP_CONDITION_MAP`
(`stop_reason` + `wire_stop_reason`), và `test_x_probe_signals.py` khóa chúng vào `run.yaml`,
openapi, `errors.yaml` và bốn fixture cùng lúc. **Đề nghị:** một dòng chú thích chéo ở §5.
Không chặn gì.

## 8. Ghi chú PROVISIONAL do tôi đưa vào

### `PROV-WX-01` — selector và marker chưa từng đối chiếu với X thật

Gói này chạy **không có mạng**. Mọi `data-testid` ở `dom.py` và mọi chuỗi hiển thị ở
`signals.py` là **PROVISIONAL**: không cái nào được kiểm trên trang X thật.

Điều làm cái này an toàn chứ không phải một quả bom hẹn giờ là **fail-closed**: khi không
nhận ra trang, bộ dò trả `ST-7 source_layout_changed` và đợt **dừng**, chứ không trả về một
đợt rỗng im lặng. `contracts/errors.yaml` mô tả đúng ngữ nghĩa đó ("vào được nhưng không đọc
được", cần **người phát triển** sửa bộ đọc), và §7 GO-6 biến nó thành **KHÔNG KẾT LUẬN** —
không phải một GO giả. Runbook §7 nói với Owner đúng điều đó, và `extra_markers` cho phép
**thêm** marker theo đúng chữ tài khoản họ thấy (thêm được, không xóa được).

### Ba lựa chọn thiết kế tôi ghi lại thay vì im lặng

1. **`author_threads_opened` luôn `0`.** Probe không mở thread. Không tiêu chí go/no-go nào
   dùng trường này; mở thread đốt ngân sách và kéo theo nghĩa vụ `SL-1` (chỉ thread của chính
   tác giả) mà probe không cần để trả lời REQ-A1. Mỗi bản ghi nói điều này trong
   `unobservable_scope_vi`.
2. **Sổ `posts_new_vs_previous_runs` lưu digest sha256, không lưu `x_post_id`.** §5 cần con
   số "bao nhiêu bài chưa từng thấy", tức cần trí nhớ xuyên đợt — nhưng không cần chính các
   id. Digest đủ trả lời "đã gặp chưa?" và vô dụng cho việc dựng lại ai đăng gì.
3. **Đợt đi hết mọi từ khóa trong ngân sách được ghi `limit_reached` + `limit_kind = posts`,
   marker `scroll_steps_exhausted`.** §4 không có hàng "kết thúc tự nhiên", và bịa một giá
   trị mới sẽ đưa một `stop_reason` ngoài enum §5 vào bản ghi. Câu đúng là: đợt chạm một ngân
   sách của chính nó (`max_scroll_steps_per_term`), và `notes_vi` nói rõ ngân sách nào. Hằng
   số `SCROLL_BUDGET_STOP` được tách riêng để chỗ **duy nhất** probe ghi một điều kiện dừng
   nó **không quan sát trên trang** là nhìn thấy được và test được.

## 9. Ranh giới §2 — cài vào code, không chỉ vào văn xuôi

`tests/contract/test_x_probe_boundaries.py` quét chính source của `probe/` và **fail** nếu
thấy: bất kỳ lời gọi `.click(` nào (nên không có gì để lỡ trỏ vào nút xác minh — I10), gán
`user_agent`, cấu hình `proxy`, `set_extra_http_headers`, `add_init_script`, cờ che dấu vết
webdriver, tên dịch vụ giải CAPTCHA nào, mọi mẫu luân chuyển account, và mọi đường tới
`api.x.com`/`api.twitter.com` (SRC-SPEC §2.3 xếp X API trả phí ngoài phạm vi).

Thêm ba lớp nữa:

- `PlaywrightXDriver` **không có** `click`/`tap`/`fill`/`type`/`press`/`check`/`select_option`
  — bề mặt driver **là** ranh giới: cái gì driver không làm được thì vòng chạy không làm được;
- `config.py` **từ chối** file cấu hình mang khóa `user_agent`, `proxy`, `accounts`,
  `fingerprint`, `captcha_solver`, `stealth`…; và từ chối `x_base_url` không phải host X
  (`SL-4 chrome_scope: x_only`), profile Chrome mặc định (P1), ngân sách vượt §3.2, nhịp dưới
  sàn 2000 ms;
- `record.py` **từ chối ghi** một bản ghi còn sót cookie/token/`@handle`/đường dẫn home, và
  mọi dòng log đi qua `RedactingFormatter`.

Playwright chỉ được import **bên trong** `open_driver` (khẳng định bằng AST), nên toàn bộ
156 test chạy mà không cài trình duyệt — và `import probe.x_feasibility.run_probe` không kéo
theo Playwright.

## 10. Checklist của packet

| Mục | Trạng thái | Ở đâu |
| --- | --- | --- |
| Script probe Playwright, persistent context, profile từ config, không bao giờ profile mặc định | DONE | `probe/x_feasibility/run_probe.py` `open_driver`; `config.py` `_check_profile_dir` |
| Quan sát chỉ-đọc theo §3: mở feed/search theo tag, cuộn trong ngân sách, đếm bài | DONE | `run_probe.run_one` |
| Phát hiện challenge/blocked/rate-limit/session-expired theo tín hiệu §4 | DONE | `probe/x_feasibility/signals.py` |
| Dừng ở **mọi** điều kiện §4; không bao giờ bấm xác minh | DONE | `run_one` + không có `.click(` nào trong `probe/` |
| Ghi một bản ghi JSONL mỗi đợt đúng hình dạng §5 vào `evidence/runs/SP1-x-feasibility/` | DONE | `record.append_record`; thư mục đã tạo kèm README + biểu mẫu |
| Không bản ghi bịa | DONE | `runs.jsonl` **không tồn tại**; chỉ có `TEMPLATE-run-record.json` (biểu mẫu, không phải đợt) |
| Che danh tính trong log | DONE | `record.REDACTIONS` + `RedactingFormatter`; validator từ chối bản ghi còn sót |
| Runbook `probe/README.md` từng bước | DONE | `probe/README.md` §1–§11 |
| `probe/go_no_go.py` đọc JSONL, áp §7 nguyên văn | DONE | `probe/go_no_go.py` → `probe/x_feasibility/go_no_go.py` |
| Test ngoại tuyến cho bộ dò trên fixture collection | DONE | `test_x_probe_signals.py` (28) |
| Test cho JSONL writer/validator | DONE | `test_x_probe_record.py` (38) |
| Test go/no-go trên đợt tổng hợp, cả GO lẫn NO-GO | DONE | `test_x_probe_go_no_go.py` (25) |
| Trình duyệt Playwright **không** cài, **không** mở trong test | DONE | `test_x_probe_boundaries.py`; khẳng định bằng AST |
| Không gọi X | DONE | `network_access: false`; không request nào |
| Không mutate git | DONE | không lệnh git nào ngoài `status` chỉ-đọc |
| `PYTHONDONTWRITEBYTECODE=1` | DONE | mọi lệnh; không `__pycache__` |
| Scratch dưới `…/scratchpad/wx/` | DONE | cấu hình test và thư mục out đều ở đó |
| HANDOFF + evidence manifest, feasibility = `NOT_RUN` | DONE | file này + `evidence/runs/TC-x-feasibility-probe-E1-20260907T140211Z.json` |

## 11. Owner cần làm gì để probe chạy được

1. Trả lời **bằng văn bản** ba mục còn lại của `collector-probe.md` §6 (ngân sách §3 + điều
   kiện dừng §4; tiêu chí go/no-go §7; rủi ro tài khoản REQ-A7).
2. Trên máy cá nhân: `uv sync --all-packages` rồi `uv run playwright install chromium`.
3. Tạo profile Chrome **riêng của dự án** và đăng nhập X **bằng tay** (`probe/README.md` §3.2–3.3).
4. Chép `probe/probe-config.example.json`, điền đường dẫn profile, từ khóa, và bốn
   `owner_confirmations` kèm `evidence_ref` trỏ tới văn bản ở bước 1.
5. `uv run python probe/x_feasibility/run_probe.py --config <file> --runs 1`, hai lần/ngày,
   trong 3–5 ngày; rồi `uv run python probe/go_no_go.py evidence/runs/SP1-x-feasibility/runs.jsonl`
   và gửi lại `runs.jsonl` + `probe.log` + kết quả go/no-go (`probe/README.md` §10).

## 12. Điều gói này **không** thiết lập

- **Không** nói gì về khả thi nguồn X. N = 0.
- **Không** chứng minh selector/marker khớp X thật (`PROV-WX-01`).
- **Không** chứng minh SC01/SC03/SC04/SC49 — chúng là scenario server/wire, probe M0 dry-run
  không chạm (`collector-probe.md` §10 mục 6). Cả bốn vẫn `NOT_RUN`.
- **Không** chứng minh đường ingest, dedup, coverage hay chất lượng nội dung (§10 mục 2–5).
- **Không** mở cổng SP1. Điều kiện của SP1 là *Owner chấp nhận* §6 — chưa có.
- **Không** có audit độc lập. Mọi thứ ở đây là `SELF_VALIDATION`; **không** ai được viết
  "independent audit passed" dựa trên file này.
