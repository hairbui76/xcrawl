# OWNER_DECISION record — 2026-09-07 (second round)

- decision_id: `OD-20260907-02`
- issuer: Owner (session user), plain-text instruction in the Claude Code session: "accept ADR-0011, start phase 0 and 1" and "I accept, continue but you can spawn up to 10 subagents Opus high effort".
- evidence_ref: Claude Code session `session_0156UBBHDSeC9soECzSVUb3U` (continuation of `session_017QmDJtMqD9o1z79waqSB9W`), 2026-09-07.
- authority created: `AUTH-OWNER-20260907-03` — parent of every Phase 0 / Phase 1 Worker packet.

| # | Item | Owner's answer | Effect |
| --- | --- | --- | --- |
| 1 | ADR-0011 frameworks and toolchain | **Accepted** | ADR-0011 status `provisional-accepted` → `accepted`, `ratified_by: OD-20260907-02`; answer-sheet line filled |
| 2 | Start coding: Phase 0 (repo skeleton + CI) and Phase 1 (M1: data store, ingest, auth, storage readiness) per `docs/master-plan.md` | **Start** | Gate G5 entry granted for the Phase 1 cards: `TC-ingest-idempotent-ack-lost`, `TC-canonical-identity-merge`, `TC-owner-auth-session`, `TC-storage-write-blocked-readiness`; Phase 0 closes G5-X4 (repo layout) |
| 3 | Operating mode for code | Implied by #2 (Coordinator ruling, disclosed): `agent_profile/protocol.md` §2 restricts `DOCUMENTARY_DRAFT` to documents and requires runtime guards for `ENFORCED` mode, which do not exist; the explicit Owner instruction outranks the pinned protocol (registry `instruction_precedence`). Code mutation therefore proceeds under the same message-tracked exclusive leases, exact write sets and independent review used for the documents, with the residual risk (no OS-level enforcement) recorded here and in the decision register. | Recorded as `PROV-PC00-08` (Coordinator ruling under Owner instruction; Owner may object) |
| 4 | Dependency downloads | Implied by #2: installing declared packages from PyPI/npm is permitted for Workers (it is part of building, not a product side effect); no other network use; no secrets; no live X/Telegram/AI calls (E3 stays NOT_RUN) | Recorded in the phase packets' capability lines |
| 5 | Subagent budget | Up to 10 Opus subagents, high effort, for this phase | Coordinator ledger |

Claim ceiling for Phase 0/1 output: `IMPLEMENTATION_VERIFIED` at most (E1 contract tests on fixtures + E2 fault injection where the cards demand it), never INTEGRATION/LIVE. Product status stays `NOT_READY_FOR_PRODUCT_CODE` until G5 is fully MET and Phase 1 evidence is registered.
