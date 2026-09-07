# AUDIT_REPORT `A3-P2-R1` — independent review of Phase 2 (FC-P2)

| Field | Value |
| --- | --- |
| packet | `PKT-A3-P2-R1` · authority `AUTH-COORD-A3-P2-R1` (parent `AUTH-OWNER-20260907-05`) · lease null |
| reviewer | `auditor-A3` — authored nothing in the repo; no repo write this round. Independent of every Phase-2 packet. |
| candidate | `FC-P2`, 466 entries, `manifest_sha256 = dafc1c83ca2108d50ccc5cc700115849b9537be31ff0155f5dd37c7bc5e469f0` |
| quiescence | Recomputed at start and end: **466/466** `path\|sha256\|bytes` identical, header hash reproduces. `git status --porcelain` 72 before and after. **Not `STALE`** — the declared `precode/` freeze held. |
| delta vs `FC-P1e4` | 53 added, 0 removed, 42 changed (95 touched). |
| network use by me | Four documentation GETs, all inside the granted allowlist (`info.arxiv.org`, `help.openalex.org`). No API host contacted. |

## 1. Regression (from a synced environment)

| Gate | Claim | My observation | Verdict |
| --- | --- | --- | --- |
| `uv run pytest` | "586 tests, 0 failures, 4 xfail" (connector handoff W2) | **582 passed, 4 xfailed, 0 failed** (49.4 s), exit 0 — i.e. **586 collected**, which is what the handoff says | REPRODUCED |
| `ruff check` | green | `All checks passed!` | REPRODUCED |
| `ruff format --check` | green | `88 files already formatted` | REPRODUCED |
| `mypy --strict` | green | `Success: no issues found in 30 source files` | REPRODUCED |
| `generate.py --check` | no diff | `generated tree matches a fresh run of the generator` | REPRODUCED |
| OpenAPI 3.1 | OK | `contracts/http/openapi.yaml: OK` | REPRODUCED |
| `verify_cards.py` | 13/13 @ `P2d` | **13 PASS / 0 FAIL over 19 cards, 3 571 assertions, 0 violations**, epoch `PC10-PIN-P2d-20260907` | REPRODUCED |
| `e0_check.py` | 25/25 | **25 PASS · 0 FAIL · 0 violations** | REPRODUCED |
| alembic, blank DB | one head | `0005_tc_research_connector_metadata (head)`; history shows `0004 → 0005` linear | REPRODUCED |

> The Coordinator's orientation said "~586 passed". The precise figures are **582 passed +
> 4 xfailed = 586 collected**. The handoff's own wording ("586 tests … 4 xfail") is accurate;
> the paraphrase was not. No test is skipped anywhere.

**Stability.** The connector handoff discloses that
`tests/integration/test_collector_resume_after_challenge.py` failed twice mid-packet and
passed in isolation, attributing it to Phase-2A writing that file concurrently. I re-ran the
**full suite three times** and that file **five times in isolation**: green every time, exit 0.
The disclosed explanation holds; I found no order- or state-dependence.

## 2. Network boundary — the strongest check I ran

I loaded a pytest plugin that replaces `socket.socket.connect`, `socket.connect_ex`,
`socket.sendto`, `socket.create_connection`, `socket.getaddrinfo` and `socket.gethostbyname`
with raisers, then ran the **entire workspace suite** under it.

**Result: 582 passed, 4 xfailed, exit 0 — zero network attempts, including zero DNS.**

That is not an argument from reading; it is a proof that no test in the repository touches the
network. Supporting checks:

* `export.arxiv.org` and `api.openalex.org` — the two hosts `OD-20260907-04` forbids **by
  name** — appear **nowhere** in `server/`, `collector/`, `worker/`, `probe/`, `shared/`,
  `tests/`, `acceptance/` or `web/`.
* Tests address `arxiv.test.invalid` / `openalex.test.invalid` (RFC 2606 reserved, not
  resolvable) through an injected `httpx.MockTransport`.
* The one `arxiv.org` string in server code is
  `server/app/research/client_arxiv.py:43 _ARXIV = "{http://arxiv.org/schemas/atom}"` — an XML
  **namespace URI**, not a host. A naive grep flags it; it is not a network reference.
* `system_resolver` is injectable and the shipped default is replaced in tests, which is why
  the DNS block above changed nothing.
* `evidence/runs/SP1-x-feasibility/runs.jsonl` **does not exist** (only `README.md` and
  `TEMPLATE-run-record.json`), before and after my work.

## 3. REQ-A6 — independent re-derivation from the primary sources

I fetched the documentation myself and asked for verbatim quotation. This is the one fact
nobody inside the implementation chain should be trusted to have got right by citing itself.

| fact | recorded in `retry-policy.yaml` 0.8.0 | what I read, first-hand | verdict |
| --- | --- | --- | --- |
| `A6-ARXIV-RATE` | `arxiv_requests_per_window: 1`, `arxiv_window_seconds: 3`, `arxiv_max_concurrent_connections: 1`, quoting `info.arxiv.org/help/api/tou.html` | *"When using the legacy APIs (including OAI-PMH, RSS, and the arXiv API), make no more than one request every three seconds, and limit requests to a single connection at a time."* | **CONFIRMED — verbatim, character for character** |
| `A6-ARXIV-IDENT` | `false`; "no page imposes an identification requirement", the private-information sentence being a collection statement | The page imposes no User-Agent/email/registration requirement; the private-information sentence is about collection, not a precondition | **CONFIRMED**, including the subtlety the record draws |
| `A6-OPENALEX-RATE` | `openalex_requests_per_window: 100`, `openalex_window_seconds: 1`, quoting `help.openalex.org/api/authentication/` | *"Two things return `429 Too Many Requests`: exceeding your daily budget, or making more than 100 requests per second."* | **CONFIRMED — verbatim** |
| `A6-OPENALEX-BUDGET` | `RESOLVED_NON_NUMERIC`; quotes *"every account gets $1 of API usage per day for free"* and *"a free key gives you 10× the keyless budget"*; **refuses** to turn "10×" into a number | Pricing page: *"every account gets $1 of API usage per day for free"*; authentication page: *"a free key gives you 10× the keyless budget"* | **CONFIRMED**, and the refusal to derive a number from "10×" is the correct call |

The citations are **real quotes at real URLs**, not fabrications. Two facts were re-derived
independently as the packet required; I did four.

The record's surrounding judgement is also sound, and worth saying: it keeps
`min_interval_ms = 3000` as a self-imposed floor ~300× stricter than OpenAlex's documented
limit, labels the floor `PROVISIONAL` and the documented limits `DOCS_derived`, refuses to
conflate the two, records `retrieved_at` with an explicit `expiry_vi`, and says `Retry-After`
and the `X-RateLimit-*` headers always win over any configured number.

**Contract→code direction is machine-enforced.**
`tests/integration/test_research_connector_health.py:164` loads `retry-policy.yaml` and
compares it against the shipped constants. I mutation-tested that guard in a scratch harness:
arXiv `1→2` req/window **caught**; OpenAlex `100→1000` **caught**; `retrieved_at` drift
**caught**. The constants are literals annotated with their source, but they cannot drift from
the contract without this test failing.

## 4. Per-card verdicts

### `TC-collector-checkpoint-resume` — claim **may stand**, scoped

§3's seven paths all exist and nothing outside them was written. All seven fixtures its §2
names are exercised by real assertions. Two write-set deviations are **declared** in handoff
§6, and both were resolved the right way round — the worker kept inside §3 rather than adding
an eighth module, and raised `CR-TC-COLLECTOR-02` asking the card to say which it wants. No
playwright import exists anywhere in `collector/app/`. The handoff explicitly claims nothing
about real X.

### `TC-research-connector-metadata` — claim **may stand**, scoped

Five fixtures, all exercised. Migration `0005` is a clean linear child of `0004`. The card's
mid-phase §9/§10 rewrite (`CR-PC10-14`) is the drift check the packet asked for, and I tested
each rewritten clause against behaviour rather than reading it:

| rewritten clause | how I tested it | result |
| --- | --- | --- |
| `SG-A6`(a) "explicit null ⇒ refuses to start, mechanism kept with a regression test" | ran `test_an_explicitly_nulled_rate_still_refuses` and `test_a_nulled_rate_makes_zero_requests_and_reports_the_req_a6_reason` | **holds** — `ConnectorNotConfigured` on three blanked shapes; end-to-end, `attempt_number == 0`, `recorder.requests == []`, health `unavailable` / `rate_facts_unresolved` |
| `SG-A6`(b) "contract → code, never the reverse" | mutation-tested the drift guard (above) | **holds**, 3/3 mutations caught |
| `SG-IDENT` "resolved to *no*, but the mechanism stays" | shipped `requires_contact_identity is False`; a `SourceConfig` declared as demanding identification still raises | **holds** |
| `SG-LIVE` "no real network" | full suite under a total socket/DNS block | **holds** |
| `SG-DOC` "no contract names a host/endpoint; don't invent one" | shipped defaults carry `endpoint_template = None` and empty `host_allowlist`; tests use `.invalid` hosts | **holds** |

The card's §9 correctly re-bases the ceiling reason on `SG-DOC` + `SG-LIVE` and states that
clearing `PLACEHOLDER_KC` does **not** confer `CONTRACT_READY` — that judgement belongs to
PC05/Coordinator. See `F-A3-P2-01` for the one place this update did not reach.

### `TC-x-feasibility-probe` — **tooling only; no code claim, correctly**

The handoff claims `DRAFT_FOR_REVIEW` and states in as many words: **not**
`LIVE_FEASIBILITY_VERIFIED` "and nothing near it". `contracts/ops/collector-probe.md` §6
distinguishes an **administratively** open gate from operational permission, and keeps every
number at `NOT_RUN`.

I tested the gate rather than trusting the prose, by running `run_probe` against three scratch
configs:

| config | result |
| --- | --- |
| shipped example (3 of 4 unconfirmed) | **exit 2**, `OWNER_DECISION_REQUIRED` |
| all four `confirmed: true` but **empty** `evidence_ref` | **exit 2** — a self-typed `true` is correctly not a written confirmation |
| all four confirmed **with** `evidence_ref` | proceeds to `launch_persistent_context` and aborts on the example's placeholder profile path (`EACCES … '/home/<bạn>'`) |

**Disclosure:** the third case shows the owner gate is the *only* thing between a satisfied
config and a browser launch — which is the intended design, the Owner being the runner. No
browser started, no network occurred, nothing was created (the placeholder path is
unwritable), and `runs.jsonl` remains absent. I report it because an auditor should say when a
check came one step from the boundary it was testing.

## 5. Contract amendments and records

* **`AMD-ENT-owner-01`** is now `status: ACCEPTED` with `ratified_by: OD-20260907-03`,
  `ratified_at: 2026-09-07`. `ratification.owner_decision_vi` cites OD-20260907-03 item 1
  (authority `AUTH-OWNER-20260907-04`), and `history_vi` **preserves** the earlier
  `PROVISIONAL` state and the now-spent "the Owner may object" condition rather than deleting
  it. `OD-20260907-03` line 56 confirms the ratification independently. The R3 gap this came
  from is also recorded structurally (`deviation_from`, `deviation_authority`,
  `deviation_change_request: CR-PC10-13`). This closes the standing caveat on
  `TC-owner-auth-session`'s label: **it no longer rests on a provisional contract.**
* **`contracts/`** changed in exactly three files — `data/entities.yaml`,
  `retry-policy.yaml` (0.6.0→0.8.0), `ops/collector-probe.md` (0.3.0→0.5.0). Nothing else.
  `acceptance/` changed only in `traceability.csv`.
* **`research-radar-spec.md` is byte-unchanged**: `d35e1f2d…`, identical to the value pinned
  in every card's §0. `AMD-SPEC-D34-01` sits in `decision-register.md` §3 in that section's
  existing amendment style; it records the false premise **without** touching the immutable
  spec, which is the correct mechanism.
* **`REQ-A6`, `REQ-D34`, `REQ-S13.2-01`** are all `XN`, each note naming the resolution date,
  the decision and the authority.
* **Card churn**: comparing every card committed at `4ddefb2` against disk, **19 of 19 changed
  only inside §0** — no §1–§13 byte moved across the whole `P1d → P2d` span. Final-epoch pins
  match disk (`verify_cards` `pins`, 3 571 assertions, 0 violations).
* **No undeclared writes**: all 95 touched paths are named in a handoff, coordination record
  or decision file. Zero unclaimed.

## 6. Findings

### `F-A3-P2-01` — LOW — two stale "REQ-A6 is unresolved" cross-references survive the resolution

* `evidence/handoffs/TC-research-connector-metadata-handoff.md:10` — the `completion_claim`
  justifies the module not being `CONTRACT_READY` "**because REQ-A6 is unresolved**". REQ-A6
  *is* resolved (`retry-policy.yaml` 0.8.0, `DOCS_derived`, no null value; `requirements.csv`
  `XN`), and the card's own rewritten §9 says so explicitly, naming `SG-DOC` and `SG-LIVE` as
  the real reasons. The label is right; its stated reason is the pre-resolution one.
* `precode/requirements.csv`, `REQ-P0-04` note — still reads "*nhịp gọi còn KC theo
  REQ-D34*" though `REQ-D34` is now `XN`. The row's own status is correct; only the note is stale.

Same class as `F-A3R3-03`: a fact moved and one or two dependent sentences did not follow.
**Remediation constraint:** restate both from the current contract, not from memory; the card
§9 wording is the model. `OPEN`; no patch supplied.

### `F-A3-P2-02` — LOW — a test double ships inside a production module

`collector/app/reader.py:644` defines `RecordedSource`, a replay-and-count test double, in
production code. The worker **declared** this (handoff §6.2) with a real reason — both test
files need it, `collector/tests/` is not in card §3, and its read counter is the oracle for
"no new collection request after the stop" — and chose it over exceeding the write set, which
was the right trade. I verified it is inert: pure list replay plus a counter, no browser, no
socket, no session. The residual is structural, not behavioural: production code now carries
test scaffolding, and nothing marks it as non-shippable.
**Remediation constraint:** when `CR-TC-COLLECTOR-02` settles where the X source port lives,
settle this with it — a `collector/tests/` conftest helper or an explicitly test-only module.
`OPEN`.

**New findings: 2 (LOW 2). MEDIUM 0 · HIGH 0.** I close nothing and supply no patches.

## 7. Verdict

**Overall: PASS.** Everything the Coordinator's orientation asserted, I verified independently
and found accurate, with the two low-severity exceptions above. The two strongest results are
the ones that could not be got by reading: the full suite is green with **every real socket
and DNS call blocked**, and the four REQ-A6 facts reproduce **verbatim** from the primary
documentation I fetched myself.

| item | verdict |
| --- | --- |
| `TC-collector-checkpoint-resume` — `IMPLEMENTATION_VERIFIED` | **may stand, scoped** to the collector-side E1/E2 scope; no claim about real X |
| `TC-research-connector-metadata` — `IMPLEMENTATION_VERIFIED` | **may stand, scoped** to E1 with recorded responses; module **not** `CONTRACT_READY` (`SG-DOC` + `SG-LIVE`) |
| `TC-x-feasibility-probe` | **tooling accepted; no feasibility claim exists and none may be inferred** |
| contract amendments (`AMD-ENT-owner-01` ratified, retry-policy 0.8.0, collector-probe 0.5.0) | **ACCEPT** |
| network-grant boundary honoured | **YES** — proven, not asserted |
| card/code drift (`CR-PC10-14` rewrite) | **no drift found**; every rewritten clause tested against behaviour |
| skeleton / regression | **PASS** |

## 8. Residual and limitations

* **Phase-2 epochs `P2`, `P2b`, `P2c` cannot be verified hop-by-hop**: those bytes exist
  nowhere I can read. I verified the **aggregate** `P1d → P2d` span (only §0 moved) and that
  the final epoch's pins match disk. Anyone wanting per-hop assurance needs the intermediate
  manifests kept.
* **REQ-A6 facts carry an expiry.** They are true of documentation read on 2026-09-07 and do
  not renew. `A6-ARXIV-IDENT` and `A6-OPENALEX-IDENT` are **negative** facts over a handful of
  pages — weaker than positive ones, as the contract itself says.
* **`MOD-research-connector` is not `CONTRACT_READY`** and this report does not make it so:
  no contract names either API host/endpoint (`SG-DOC`), and E3 has never run (`SG-LIVE`).
* **SP1 has not run.** The probe gate is administratively open only; every probe number is
  `NOT_RUN` and no feasibility conclusion exists.
* Open CRs carried forward: `CR-TC-COLLECTOR-02`, `CR-TC-research-01` (fix verified),
  `CR-PC10-14`, `CR-PC10-13`, `CR-TC-storage-04`, `CR-TC-ingest-05`, `CR-TC-AUTH-01`,
  `CR-TC-IDENTITY-02/03`, `CR-P0-06`; `F-A3R4-01`, `F-A3-P2-01`, `F-A3-P2-02` open.
* E3/E4 remain **0 everywhere**; concurrency is still argued from structure, not from a
  multi-process race test.
* Completion ceiling: independent `AUDIT_REPORT` over the scope above. Not product
  acceptance, not a security assessment, no live API calls.
