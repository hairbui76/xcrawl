---
contract_id: CT-precode-owner-decisions-13
version: 1.0.0
status: accepted
document_type: OWNER_DECISION
decision_id: OD-20261017-13
issuer: Owner (người dùng của phiên Claude Code này), bằng tin nhắn trực tiếp sau khi được trình bày bốn chỗ thiếu để Claude chạy thật
issued_at: 2026-10-17
evidence_ref: "Claude Code session session_01XQgXrAiGrnAUFS3jowQf2w, 2026-10-17 — nguyên văn: \"làm cả bốn việc đi, model thì dùng opus 5.5\""
authority_created: AUTH-OWNER-20261017-14
owner_role: requirements owner (PC00)
source_refs:
  - docs/owner-runbook.md §8 (AI)
  - contracts/ai/providers.yaml §2.1, §6
  - precode/owner-decisions-12.md (vòng trước)
requirement_refs: [precode/requirements.csv]
decision_refs: [REQ-OQ03, REQ-D40, B13, ADR-0010]
producers: [PC00]
consumers: [PC06, PC04, PC10]
dependencies: [precode/decision-register.md, precode/baseline.json]
scope: >
  Biên bản quyết định của Owner ngày 2026-10-17, vòng mười ba (hai mục). Bản ghi hiệu lực là file
  này + precode/decision-register.md §8.18, viết cùng lượt.
verification: E0 — self-validation + evidence/tools/e0_check.py chạy chỉ đọc; không có E1–E4.
claim_ceiling: DRAFT_FOR_REVIEW
---

# OWNER_DECISION `OD-20261017-13` — 2026-10-17 (vòng mười ba)

## 1. Định danh

| Trường | Giá trị |
| --- | --- |
| `decision_id` | `OD-20261017-13` |
| Người ban hành | **Owner**, nguyên văn: *"làm cả bốn việc đi, model thì dùng opus 5.5"* |
| `evidence_ref` | Claude Code session `session_01XQgXrAiGrnAUFS3jowQf2w`, 2026-10-17 |
| Authority phát sinh | **`AUTH-OWNER-20261017-14`** |

## 2. Hai quyết định

| # | Mục | Quyết định | Hiệu lực |
| --- | --- | --- | --- |
| 1 | Model AI (`REQ-OQ03`) | **`claude-opus-5-5`** thay cho cặp `claude-sonnet-5` (label, direction_phrasing) + `claude-opus-5` (summary) của `OD-20260908-06` | `contracts/ai/providers.yaml` 0.2.0 → 0.3.0: **một** mục `anthropic@claude-opus-5-5` phục vụ cả ba tác vụ, `request_timeout_seconds: 120` (min của ba `inference_timeout`), `effort_by_task: {label: low, summary: medium, direction_phrasing: medium}`. Lệch khỏi khuyến nghị REQ-D40 (rẻ cho `label`) là lựa chọn §7 `rules_vi` cho phép; chi phí giữ bằng `effort`, không bằng hạ model. **`enabled: false` giữ nguyên** — mục mới là version mới, cô lập phải kiểm từ đầu (ADR-0010 §5) |
| 2 | Bốn việc còn thiếu để Claude chạy thật | **Làm cả bốn**: (a) khai endpoint `https://api.anthropic.com` trong hợp đồng; (b) transport thật qua SDK `anthropic`; (c) lệnh khởi tạo/kích hoạt generation embedding; (d) vòng build/publish báo cáo theo lịch | (a) `providers.yaml` mục §2.1 mang `endpoint` + `endpoint_allowlist: [api.anthropic.com]` — tập `ai_provider_endpoints_configured` của ISO-03 nay có nội dung. (b)–(d) là mã, ghi ở handoff tương ứng |

## 3. Không được quyết ở vòng này

- **Bật adapter.** Vẫn cần bằng chứng cô lập E3 (`ISO-01..05`), runbook §8.3.
- **Fallback phía server của Anthropic** (`fallbacks`). Không bật: `providers.yaml` §6 `default: off`, và kết quả do model khác tạo ra không khớp mục đã đăng ký. Owner có thể bật bằng một allowlist có thứ tự.
- `REQ-A3` / `REQ-OQ09` (model embedding) vẫn `KC`.

## 4. Truy vết

| Nơi ghi nhận | Nội dung |
| --- | --- |
| `precode/decision-register.md` §0, §8.18 | Nhãn `ACCEPTED (OD-20261017-13)` và bảng hiệu lực |
| `precode/requirements.csv` | Ghi chú `REQ-OQ03` |
| `precode/baseline.json` | Anchor `OD-20261017-13` |
| `agent_profile/registry.json` | `AUTH-OWNER-20261017-14` |
| `contracts/ai/providers.yaml` 0.3.0 | Mục 1 và 2(a) |
| `agent-tasks/` | Card ghim `providers.yaml` / sổ đăng ký ⇒ `STALE` ⇒ một lượt pin lại, epoch `PC10-PIN-P8-20261017` |
