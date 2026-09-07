# OWNER_DECISION record — 2026-09-07 (third round)

- decision_id: `OD-20260907-03`
- issuer: Owner (session user), plain-text instruction: "accept both, start phase 2" (after the Phase 0/1 report naming exactly two items: AMD-ENT-owner-01 and PROV-PC00-08).
- evidence_ref: Claude Code session `session_0156UBBHDSeC9soECzSVUb3U`, 2026-09-07.
- authority created: `AUTH-OWNER-20260907-04` — parent of every Phase 2 Worker packet.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | AMD-ENT-owner-01 (four credential/lockout fields on `owner`, entities.yaml 0.2.0) | **Ratified** | amendment status PROVISIONAL → ACCEPTED (OD-20260907-03); entities.yaml keeps CONTRACT_READY; the auth card's IMPLEMENTATION_VERIFIED no longer rests on a provisional contract |
| 2 | PROV-PC00-08 (coding under message-tracked leases with independent review; no OS-level enforcement) | **Accepted** | decision register row → ACCEPTED (OD-20260907-03); residual risk acknowledged by the Owner |
| 3 | Start Phase 2 per docs/master-plan.md: 2A = M0 X feasibility probe (cards TC-x-feasibility-probe, TC-collector-checkpoint-resume); 2B = M2 paper connector (operations research.fetch_work_metadata / research.get_connector_health; a card must be written first — none exists) | **Start** | Phase 2 Worker packets authorised; **the probe's live runs remain gated** on collector-probe.md §6 items 2–4 (item 1, D09, was answered in OD-20260907-01) and on the Owner's machine; the connector remains hard-blocked for CONTRACT_READY by REQ-A6 until the four rate/identity facts are recorded from official documentation — no number may be guessed |

Not decided in this round (asked separately): probe gate items 2–4; the four REQ-A6 facts or permission for a Worker to fetch the official arXiv/OpenAlex documentation over the network.
