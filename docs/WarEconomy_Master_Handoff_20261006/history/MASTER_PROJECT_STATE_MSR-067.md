# MASTER_PROJECT_STATE.md

Project: WarEconomy / RimMulti
State Revision: MSR-067
Date: 2026-10-02
Owner: Master (GPT-5.6 Sol)

> This file is a current-state snapshot, not a replacement for the Canonical SRS.
> If this file conflicts with the Canonical SRS or a later Master Decision, the higher-authority source wins.

## 1. Authority Hierarchy

1. Canonical SRS: `요구사항_명세서.md`
2. Master Decisions / Accepted ADRs
3. This Master Project State Ledger
4. Agent reports / PoC reports / QA reports
5. Historical code/comments/chats

Only IDs from the root Canonical SRS are Canonical requirement IDs.

## 2. Canonical Requirement Baseline

Known root-SRS ranges:
- FR-001..FR-234
- BR-001..BR-019
- NFR-001..NFR-012
- CON-001..CON-010
- CFG-001..CFG-026
- ER-001..ER-010
- AC-001..AC-015
- TBD-01..TBD-05
- RISK-01..RISK-05

Canonical core count:
FR + BR + NFR + CON + CFG = 301

Important: this ledger does NOT contain the full SRS wording. The root SRS remains authoritative.

## 3. Team

- Master: GPT-5.6 Sol
  - requirements authority, ADR decisions, Work Packages, final Gate
- Primary Development Agent A: Gemini 3.8 Flash
  - implementation, PoCs, fixes
- Verification & Test Engineer B: Gemini 3.1 Pro
  - fixtures, negative tests, failure injection, regression evidence
- Architecture / Final Independent QA: GPT-6.1 Sol
  - independent architecture review and final QA recommendation
- Architecture & Requirements Analysis Agent C: Gemini 3.1 Pro (Web)
  - traceability, report reconciliation, decision briefs, project-state support

## 4. Core Product Architecture Known from SRS

### Dual Time
- Dedicated Server World Time continues even with zero players.
- Settlement Local Time is separate and normally pauses while the settlement is offline.
- Tactical activity can temporarily activate actual RimWorld simulation.
- Server World Time, Settlement Local Time, Tactical Time, and RimWorld `TicksGame` must not be conflated.

### Shared Tactical
- Same tile does not automatically mean shared map.
- Explicit visit or lawful attack creates a Tactical Session.
- Participants interact with the same actual battlefield state.
- Each player directly controls only their own Pawns.
- Peaceful speed: Last Input Wins.
- Hostile: forced 1x, user pause disabled.
- Offline lawful attack must remain supported.
- Offline defender AI is required/preferred.
- Mid-battle AI↔player control handoff is a desired behavior.
- Tactical outcome must persist; client cannot simply assert victory.

### Domain Authority
- Dedicated Server owns final Domain Authority.
- Tactical Worker may own Simulation Authority only for the active tactical scope.
- Player clients are never trusted final domain authority.

### Feudal / Territory / Diplomacy / Economy
Known major product areas include:
- one player one faction/title, multiple settlements
- settlement/faction tiers
- feudal title hierarchy
- territory and vision
- alliances/diplomacy
- war/WarPending
- betrayal/intent-aware aggression
- visit/attack flows
- occupation/destruction
- tax
- P2P trade
- settlement auto-shop/offline trade
- NPC economy
- extensive configuration

## 5. Explicit Product TBDs — DO NOT SILENTLY RESOLVE

- TBD-01: faction join + settlement-cap overflow
- TBD-02: WarPending forced-expulsion destination
- TBD-03: exact theft trigger timing
- TBD-04: full faction extinction rule
- TBD-05: partial tax collection / LastCollection / arrears semantics

## 6. Major Risks

- RISK-01 Offline Combat Authority — Critical
- RISK-02 Remote Tactical — High
- RISK-03 Persistent Offline Trade Inventory — High
- RISK-04 Atomic Full-Map Ownership Transfer — Medium-High
- RISK-05 Intent-Aware Betrayal — Medium

## 7. ADR Status

### ADR-001 — Authenticated Identity / Central Authority / Persistent State
Status: ACCEPTED

Key accepted contracts:
- canonical opaque PlayerId
- provider identity separated from display identity
- Steam-preferred verified authentication
- fallback auth by server policy
- session state machine and SessionEpoch fencing
- no gameplay mutation before authenticated/world-ready state
- duplicate-login policy: reject new session
- Dedicated Server final Domain Authority
- authorization pipeline
- durable persistence
- revision model
- OperationId / idempotency
- journal/audit/outbox patterns
- SQLite-first candidate accepted
- Domain Authority separated from Simulation Authority
- Map Save + DB atomicity is NOT solved by ADR-001

### ADR-002 — Tactical Session / Offline Combat Authority
Status: PROVISIONALLY ACCEPTED

Primary candidate:
Candidate C — Trusted Tactical Worker Always

Current Master status:
- actual RimWorld Worker feasibility proven in bounded scope
- ENGINE-02 independent QA = FAIL
- Production Tactical = NOT AUTHORIZED
- Remote Tactical = NOT AUTHORIZED
- Candidate C remains primary target, not rejected

### ADR-003 — Canonical Settlement State / Entity Identity / Save Provenance
Status: NOT YET AUTHORED

Expected responsibility:
- canonical Settlement state representation
- stable cross-process EntityId and native RimWorld ID binding
- canonical inventory authority
- SaveRevision / InventoryRevision / SettlementStateRevision
- owner-local save provenance
- ordinary-simulation result provenance
- offline trade/tax interaction
- Tactical outcome publication boundary
- stale-save rejection
- duplication prevention
- reconnect reconciliation
- shared Settlement state mutation pipeline used by ordinary, Tactical, trade, tax, and ownership operations

### ADR-004 — Distributed Ownership Transaction / Repair
Status: NOT YET AUTHORED

Expected responsibility:
- save artifact + DB commit boundary
- settlement ownership
- Pawn/Animal/Item/Building ownership
- caravans
- occupation/destroy/conquest
- durable prepare/commit
- partial failure
- rollback/repair/quarantine
- operation idempotency/fencing

### ADR-005 — Intent / Betrayal
Status: NOT YET AUTHORED

### ADR-006A — Temporal Authority
Status: ACCEPTED

Accepted core contracts:
- Dedicated Server WorldTick `W`, Settlement LocalTick `L_s`, engine `TicksGame/G`, and host monotonic time `M` are distinct authority/operational coordinates.
- Tactical progress is not a separate durable calendar; it continues the target settlement's existing `L_s`.
- Offline ordinary settlement simulation has `ΔL=0`; authorized Tactical simulation advances only the target `L_s`.
- One `LocalClockId` has at most one active writer. One engine execution island has one active LocalClock writer.
- Full Worker `.rws` is private checkpoint/materialization/extraction input only and is never a wholesale canonical replacement.
- Primary publication architecture = **B2: full context for reference resolution + target-scoped simulation + Target-Scoped Outcome Publication / Canonical Merge**.
- Canonical publication contains only authorized target write-set and explicit cross-boundary transfers.
- Temporal fields use typed temporal schema; blanket tick-field rebasing is forbidden.
- LOAD is fenced before autonomous simulation; READY requires semantic/temporal validation.
- World deadlines/cooldowns are server `W` authority.
- Offline trade/tax may mutate canonical assets with `ΔL=0`; local clock freeze does not forbid authorized asset transactions.
- Ordinary resume uses current canonical graph/time, never an old local full save as implicit authority.

Accepted product policies:
- Settlement-resident chronological and biological aging follow authorized residence/local simulation, not incidental Worker global `G`.
- Tactical participants age/progress according to the target settlement's advancing local/tactical timeline under supported vanilla mechanics.
- Moving between different local-date domains preserves current age and remaining-duration semantics; native anchors are reprojected rather than creating catch-up debt.
- Server process downtime policy: `ΔW=0`; resume from last durable committed `W`. Zero-player time still progresses while the server is running.
- Raw `W` does not automatically drive caravan/transit physiology. Transit physiology requires an explicit residence/transit clock policy before implementation.
- If multiple independent LocalClocks require simultaneous simulation, use separate execution islands or a separately validated per-map virtualization design; do not multiplex divergent local clocks through one raw global `G` by assumption.

Implementation/QA status:
- ADR acceptance does NOT close QA-ENGINE-004 or other ENGINE defects.
- B2 extraction/merge, temporal materialization, ordinary resume, transit physiology, and recovery remain implementation/validation work.

### ADR-006B — Configuration & Content Manifest
Status: NOT YET AUTHORED

### ADR-007 — Ordinary Settlement Simulation Authority / Multi-Settlement Execution Topology
Status: NOT YET AUTHORED

Expected responsibility:
- who is Simulation Authority during ordinary online settlement play
- how owner-client progress becomes a candidate for canonical acceptance
- multi-settlement / divergent LocalClock execution topology
- handoff ordinary <-> Tactical
- stale/forged ordinary progress rejection
- online owner reconciliation after offline trade/tax
- Caravan/transit residence clock and physiology backend
- simultaneous writer prevention across owner client / Worker / server-side operations

This ADR is now considered a real architecture gap discovered by external red-team review, not an implementation detail.

### ADR-008 — Shared World Layer / Transit / World Projection
Status: NOT YET AUTHORED

Expected responsibility:
- Dedicated Server authority over caravans and world objects
- caravan Pawn/Animal/Item custody while in transit
- transit residence clock / physiology policy
- vision-filtered world projection into clients and Workers
- Faction registry projection across engine instances
- tactical ingress/egress between World domain and Settlement LocalClock domains
- server-side world event ordering relevant to active Tactical sessions

This is an upstream dependency for complete Tactical and tax/caravan workflows.

## 8. Tactical Engine Gate

ENGINE-01:
- actual RimWorld worker path proven
- independent QA found multi-map progression and dependency-loss failures

ENGINE-02 Dev claim:
- PASS within tested scope

ENGINE-02 Sol independent QA:
- FAIL
- Architecture Gate: BLOCKED BY ARCHITECTURE
- ADR-002 recommendation: remain PROVISIONALLY ACCEPTED

Confirmed limited successes:
- scoped Pawn/Animal/held-object/MapComponent filtering works in normal tested paths
- target AI/needs/health/power/held rot/fire subsets progress
- warmed cooperative real-time loop ~60 TPS
- several lifecycle race paths behave correctly
- dual worker profile/port isolation sanity passed

Major unresolved boundaries:
- missing dependency can still reach READY/SAVED with semantic loss
- unsafe monolithic RUN_TICKS remains
- frozen-map chronological/global time leakage
- fastEcology/global dispatch escape
- load-before-fence mutations
- fixture/oracle integrity problems
- full-save roundtrip non-target/world drift

## 9. Current Master Constraints

1. Full Worker `.rws` is input/context unless explicitly validated otherwise.
2. Full Worker `.rws` output is NOT automatically canonical post-tactical state.
3. Production is unlocked per dependency, not by one global switch.
4. Unresolved ADR decisions must not be hard-coded into Production work.
5. PoCs are only for material uncertainty; prototype production is not a goal.
6. A developer's PASS never replaces independent QA.
7. Canonical SRS remains the ultimate product authority.
8. TBD-01..05 must never be silently decided.

## 10. Current Active Work

- Sol: ADR-006A completed; temporarily reassigned to independent Tactical Boundary verification/final QA because Verification B is unavailable
- Gemini A: `WP-TAC-WORKER-HARDEN-01` submitted; must freeze the exact hardened implementation and provide reproducible self-regression artifacts
- Gemini B: UNAVAILABLE due to allocation/quota interruption; incomplete WP-VERIFY-TAC-BOUNDARY-02 produces no accepted evidence
- Gemini C: available for report reconciliation / traceability after Sol verification
- Master: ADR-002 remains PROVISIONALLY ACCEPTED; next Tactical hardening gate now depends on Sol independent verification of A's frozen implementation

## 11. Context-Recovery Rule

If Master conversational context appears incomplete, recover from:
1. Canonical SRS
2. `MASTER_PROJECT_STATE.md`
3. `MASTER_DECISION_LOG.md`
4. `QA_DEFECT_LEDGER.md`
5. current ADR / QA / Dev reports

Do not rely on chat memory as the sole project record.

## 12. MSR-002 Delta

- Dev A submitted `Tactical_Worker_Hardening_Evidence_01.md`.
- Self-reported improvements include strict manifest/load gating, RUN_TICKS quarantine, bounded slices/queue, engine-generated complex fixture, load-time tick fence, fastEcology suppression, and simulation start-debt fix.
- These are **developer evidence only** until Verification B and/or Sol independently confirm them.
- Master identified two report-status errors:
  1. ADR-002 is not rejected; it remains PROVISIONALLY ACCEPTED.
  2. QA-ENGINE-004 cannot be claimed resolved by this Work Package; it remains an ADR-006A architecture issue.
- Master also flagged a potential architectural regression: the report's dispatch inventory says `World.WorldTick`, `WorldObjectsHolder.WorldObjectsTick`, and `FactionManagerTick` are retained, which must be independently checked against temporal/domain-authority constraints.

## 13. MSR-003 Delta — ADR-006A Accepted

- `ADR-006A_Temporal_Authority.md` reviewed and accepted by Master with amendments/policy decisions.
- Temporal authority is now an upstream contract for ADR-002, ADR-003, and ADR-004.
- Primary publication direction is B2 / Target-Scoped Outcome Publication & Canonical Merge.
- Full Worker save wholesale publication remains prohibited.
- QA-ENGINE-004 remains OPEN until the accepted temporal contract is implemented and independently verified.
- Dev A's retained World/global dispatch paths must now be judged against ADR-006A, not developer labels such as "passive" or "read-only".

## 14. MSR-004 Delta — Verification B Temporarily Unavailable

- Gemini B stopped mid-task due to allocation/quota limits before producing a complete deliverable.
- No partial B work from the interrupted run is accepted as verification evidence unless later recovered as a complete, reproducible report.
- Temporary verification flow:
  `A frozen implementation + self-regression evidence → Sol independent verification/final QA → C reconciliation if needed → Master Gate`.
- This is a temporary degradation of the preferred five-agent flow, not a change in role philosophy.
- A may not keep modifying the verification target while Sol tests it; any code change creates a new candidate build/revision and requires re-verification.

## 15. MSR-005 Delta — Formal ADR Artifacts Created

Standalone formal ADR artifacts now exist:
- `ADR-001_Authenticated_Identity_Central_Authority_Persistent_State.md`
- `ADR-002_Tactical_Session_Offline_Combat_Authority.md`
- `ADR-006A_Temporal_Authority_ACCEPTED.md`

ADR-001 and ADR-002 are reconstructed formalizations of already-existing Master decisions; they are not new architecture decisions. ADR-006A is the finalized Master ACCEPTED form of Sol's proposal plus Master policy choices.

Governance rule: **An ADR that is ACCEPTED or PROVISIONALLY ACCEPTED must have a standalone ADR artifact.**

## 16. MSR-006 Delta — External Architecture Red-Team Summary

An external Claude Opus 5.5 web review summary was received. The full `ARCH_REDTEAM_REVIEW_001.md` artifact has not yet been supplied to Master, so only claims present in the user's pasted summary are treated as review input.

Master accepts the following as material architecture gaps/directions:
- ordinary settlement simulation authority/provenance is under-designed;
- multiple settlements with divergent LocalTicks create an unresolved execution-topology problem;
- online/offline trade/tax and Tactical must share a coherent Settlement-state mutation pipeline;
- stable cross-process entity identity is required before B2 merge can be considered production-safe;
- Candidate C still lacks remote-play evidence;
- untrusted owner save/materialization input requires an explicit type/mod/content trust boundary.

Plan change:
1. ADR-003 is broadened to `Canonical Settlement State / Entity Identity / Save Provenance`.
2. New ADR-007 is introduced for `Ordinary Settlement Simulation Authority / Multi-Settlement Execution Topology`.
3. ADR-004 remains Distributed Ownership Transaction / Repair and follows the canonical state/write-set contracts.
4. B2 remains accepted as the primary architecture direction, but merge granularity is not yet fixed.
5. A coarse-grained B2 variant — immutable whole-target-map/settlement snapshot under an exclusive simulation lease plus typed cross-boundary operations — is the preferred option to analyze in ADR-003 because it may avoid field-by-field custom serialization.
6. Remote Tactical validation is required before ADR-002 can become ACCEPTED, but it will start after the currently frozen A candidate completes Sol independent verification.
7. Transit clock/physiology becomes a prerequisite for end-to-end Tactical Production integration and is assigned to ADR-007; it does not block current Worker hardening tests.

## 17. MSR-007 Delta — Full ARCH-REDTEAM-REVIEW-001 Reviewed

The complete external architecture red-team report was reviewed by Master.

Master interpretations/decisions:
- SRS §4.2 assigning the Client "Settlement Local Simulation" is interpreted as **simulation responsibility**, not final canonical custody. ADR-001 remains controlling for final authority. Future ADR-003/007 must formalize how client-produced ordinary simulation becomes a candidate for canonical state.
- SRS §77's historical "Map Owner Authoritative" preference is explicitly superseded for current architecture by ADR-002 Candidate C, as an architecture choice permitted by the SRS architecture-choice section. This does not change the user-facing offline-combat requirements.
- ADR-001 and ADR-002 reconstructed standalone texts are re-ratified as the current authoritative ADR artifacts.
- ADR-006A B2 remains the accepted primary architecture direction, but it is now governed by explicit falsification criteria. Failure of those criteria reopens ADR-006A/B2 instead of forcing downstream ADRs to conform.
- Current preferred B2 granularity for ADR-003 analysis is **B2-lite**: whole target Settlement/Map artifact replacement under an exclusive writer/asset lease, plus typed cross-boundary operations and a small server index/manifest. Field-level arbitrary object merge is not accepted as the default.
- Client-originated save/checkpoint artifacts are hostile input. "Trusted Worker" means operator-controlled process, never trusted input.
- Gameplay content is server-pinned. Approved content must be classified before runtime admission; unknown critical content must not be allowed to weaponize runtime fail-closed behavior into immunity from offline attack.
- Remote Tactical Presentation/Replication is a mandatory falsification gate for Candidate C. It begins after the currently frozen Worker candidate finishes Sol independent QA, and may run in parallel with ADR-003/007 work.
- Shared World Layer / transit / world projection is elevated to ADR-008.
- ADR-006B is renamed `Configuration & Content Manifest`.

Open Master/product decisions remain where the SRS genuinely does not decide them, especially multi-settlement ordinary topology and detailed tax/inventory eligibility. They must not be silently encoded in implementation.

## 18. MSR-008 Delta — Sol Independent QA of Frozen Worker Candidate

Source:
`QA_Tactical_Worker_Hardening_Independent_Review.md`

Master accepts Sol's independent QA as authoritative evidence for the frozen `WP-TAC-WORKER-HARDEN-01` candidate.

Gate:
- Worker Hardening Gate: FAIL
- Architecture Gate: BLOCKED BY ARCHITECTURE
- ADR-002: PROVISIONALLY ACCEPTED remains
- Production Tactical: NOT AUTHORIZED

Defect state changes:
- QA-ENGINE-007: CLOSED for the original mechanical pre-load autonomous-tick fence defect on the verified candidate/profile.
- QA-ENGINE-008: CLOSED for START elapsed-debt/catch-up burst.
- QA-ENGINE-002: OPEN / STILL FAILING.
- QA-ENGINE-003: OPEN / PARTIAL.
- QA-ENGINE-004: OPEN / STILL FAILING.
- QA-ENGINE-005: OPEN / STILL FAILING.
- QA-ENGINE-006: OPEN / STILL FAILING.

Important evidence:
- missing RecipeDef / cross-registry typed Def / invalid body-part reference can still reach READY/SAVED after semantic loss;
- client disconnect can leave an accepted queued STEP executing later without a proper lease/result contract;
- public diagnostic monolithic tick path remains exposed;
- GameComponent dispatch mutates global state, including native Anomaly timer state;
- the claimed 11-dimension oracle is not trustworthy: 9/11 targeted corruptions escaped detection, and inventory deletion was not part of the final predicate;
- pre-load autonomous ticking was independently observed as zero through READY until the first authorized step;
- START after load/export/idle/pause/cancel independently showed no elapsed-time burst.

Next implementation scope:
A may fix QA-ENGINE-002/003/006 and implementation-safe QA-ENGINE-005 issues while preserving closed 007/008 regressions.
QA-ENGINE-004/B2 publication and broader global-state policy must follow ADR-003/007/008/006B contracts rather than being guessed in scratch code.

## 19. MSR-009 Delta — C Canonical State / Ordinary Authority Decision Brief

Source:
`Decision Brief_Canonical_State_and_Ordinary_Authority.md`

Master accepts the brief as architecture analysis input.

Accepted architecture decisions:
- ADR-003 scope remains `Canonical Settlement State / Entity Identity / Save Provenance`.
- B2-lite is promoted from preferred analysis option to the **default architecture baseline**, still subject to the B2 falsification criteria already recorded in MDR-007.
- Default B2-lite granularity:
  - immutable engine-produced whole target Settlement/Map snapshot/artifact,
  - exclusive material-state writer/asset lease while Tactical simulation owns the target,
  - small server-maintained index/projection,
  - ordered typed cross-boundary operation/delta journal.
- Field-level arbitrary RimWorld object merge is not an accepted default.
- During an active Tactical material-state lease, target-settlement Auto Shop / Tax mutations are queued and revalidated/applied after the Tactical publication boundary, rather than concurrently field-merging into the live Worker state.
- Owner-client checkpoints/saves are hostile/untrusted inputs even when produced by a valid leased writer.
- Stable cross-process EntityId and server-authoritative Faction identity are mandatory ADR-003 concerns.
- Server-authoritative Shared World Layer / transit remains ADR-008 scope.
- Content manifest/type/schema allowlisting remains ADR-006B scope.

Still open / not silently decided:
- G-Q1 multi-settlement ordinary clock topology;
- G-Q2 ordinary-client cheat/trust posture and accepted residual risk;
- G-Q4 Tactical crash semantics;
- G-Q6 ordinary checkpoint loss window/grace behavior;
- G-Q8 exact Settlement Inventory inclusion set and offline Pawn/Animal tax delivery timing;
- G-Q9 Auto-shop order state after Occupy;
- G-Q10 whether Candidate C owner remote UX is acceptable; this is deferred until the Remote Tactical Presentation PoC provides evidence.
- G-Q5/Q5b remains for ADR-002 amendment + ADR-005.

Sequencing:
- A: Remote Tactical Presentation PoC remains the immediate Candidate-C falsification task.
- C: next prepares proposed ADR-003 and ADR-007 as a coordinated pair; ADR-003 may advance on identity/canonical-state decisions while ADR-007 keeps product-policy decision requests explicit.
- Sol: available for independent review after new runtime or ADR evidence.

## 20. MSR-010 Delta — ADR-003 / ADR-007 Draft-1 Review

Received:
- `ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance.md`
- `ADR-007_Ordinary_Settlement_Simulation_Authority.md`

Master verdict:
- ADR-003 Draft-1: **PROPOSED / REVISION REQUIRED**
- ADR-007 Draft-1: **PROPOSED / REVISION REQUIRED**
- Neither ADR is ACCEPTED yet.

Accepted direction remains:
- Dedicated Server is canonical custodian.
- owner client is a leased Simulation Writer candidate.
- B2-lite remains the default falsifiable baseline.
- target Tactical material state uses an exclusive material-state lease.
- target Auto Shop/Tax operations queue during Tactical.
- stable cross-process canonical identity is required.
- owner checkpoints are untrusted input.

Required corrections before acceptance:
1. ADR-007 handoff must use a barrier:
   freeze current writer -> final checkpoint candidate while lease still valid -> validate/commit -> revoke/fence old writer -> grant Worker lease.
   If the client is unavailable, use the last committed canonical head; never depend on a forced final upload after revocation.
2. WriterLease fencing token must be a monotonic server-issued generation. Authentication capability/token and fencing generation are distinct concepts.
3. Disconnect policy cannot simultaneously be "immediate hard stop" and G-Q6 OPEN. Physical client stop is not trusted; server rejection after revocation is authoritative.
4. ADR-007 must restore Separate Execution Islands as an explicit G-Q1 topology option.
5. ADR-003 must not assume a canonical target artifact is literally a target-only `.rws`; native full `.rws` remains non-canonical whole-world output. Canonical settlement artifact format/materialization package remains an implementation boundary until validated.
6. Server Projection / Index must be durable and derivable/verifiable; not merely "server-memory".
7. Queued but unapplied Tactical-time Economy operations do NOT advance SettlementStateRevision. They remain pending operations until post-Tactical revalidation/commit. Otherwise every queued trade would stale the Worker checkpoint and defeat the exclusive-lease design.
8. Whole-target B2-lite must not devolve into logging every internal split/merge/destroy. Canonical EntityId is mandatory for server-addressable/cross-boundary/persistent externally referenced entities; internal engine-only ephemeral identity remains inside the artifact unless exported.
9. Native loadID binding mechanism (ThingComp/global mapping/etc.) is not yet accepted; the ADR must specify the identity contract and mark the concrete binding mechanism as validation-required.
10. Hostile input validation needs typed semantic/content validation and provenance/plausibility checks in addition to XML schema/size/mod allowlist.

No QA defect status changes.

## 21. MSR-011 Delta — Remote Tactical Presentation PoC-01

Source:
`POC_Remote_Tactical_Presentation_01.md`

Master assessment:
**STRONG CONDITIONAL PASS / INDEPENDENT QA REQUIRED**

What A materially demonstrated in two real RimWorld 1.6 processes:
- a Worker-owned authoritative simulation can accept remote own-Pawn commands;
- a separate client-side RimWorld mirror can remain non-authoritative;
- local client ticks do not alter Worker state;
- snapshot reconciliation can correct mirror divergence;
- foreign/AI Pawn command attempts can be rejected at the Worker boundary;
- stale presentation generation commands can be rejected;
- move/draft/job/attack/health paths were exercised through the mirror/Worker loop.

Important limitation:
The presentation client itself was launched with `-batchmode -nographics`. Therefore this PoC does **not** independently prove actual human-visible rendered GUI usability, real OnGUI interaction, 60 FPS presentation, or end-user peaceful-visit UX. It proves engine/object/UI-model structural feasibility and command/reconciliation plumbing.

Architecture direction:
- Candidate P1 thin/raw-render client remains rejected as impractical.
- Candidate P2 non-authoritative Mirrored Client Map becomes the **primary presentation candidate**, not yet final ACCEPTED.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
- Actual graphical-client validation + independent QA are required before the remote-presentation falsification gate is considered passed.

Authority amendment direction:
- Tactical/physical simulation facts may be produced by the Worker.
- Domain/economic/ownership/faction-membership effects remain server-authorized/committed.
- Do not classify whole UI features as exclusively Worker or Server by name; mixed operations may produce Worker facts plus Server domain commits.
- Do not pre-commit to generic two-phase commit; ADR-003/004 define transaction semantics.

No existing QA-ENGINE defect status changes.


## 22. MSR-012 Delta — ADR-003 / ADR-007 v2 Review

Received:
- `ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v2.md`
- `ADR-007_Ordinary_Settlement_Simulation_Authority_v2.md`

Master verdict:
- ADR-003 v2: **PROPOSED / REVISION REQUIRED**
- ADR-007 v2: **PROPOSED / REVISION REQUIRED**

Draft-1 corrections successfully addressed:
- handoff now takes the final candidate while the old lease is still valid;
- dead/unresponsive client falls back to the last committed canonical head;
- FencingGeneration is separated from SessionEpoch/WorkerGeneration;
- G-Q1 includes Separate Execution Islands;
- target artifact is logical/format-neutral rather than assumed target-only `.rws`;
- durable projection/index is recognized;
- pending Tactical Economy operations no longer advance the canonical head;
- EntityId scope is narrowed away from all ephemeral internal objects;
- hostile input validation is broadened.

Remaining contract blockers:
1. `PendingOperationQueue`, `CommittedOperationLog`, and `MaterializationManifest` are not yet cleanly separated. Only committed operations may enter a canonical materialization manifest.
2. Every artifact needs an explicit `ArtifactBaseStateRevision` / applied-through watermark so committed operations are replayed exactly once.
3. Online ordinary Auto Shop/Tax against a live leased client remains under-designed. Fast-forward-only checkpoints will otherwise become stale whenever the server commits a material delta during ordinary play.
4. ADR-007 needs an explicit server-side lease state machine and HANDOFF_BARRIER admission rule. During a barrier, normal checkpoints/operations cannot race the final candidate.
5. Writer lease scope must bind SettlementId/LocalClockId, holder identity, base revision, fencing generation, and authorized write scope.
6. Canonical EntityId must remain stable, but native RimWorld loadID need not be globally stable across processes. Binding is per materialization context and must be unique/reference-consistent there.
7. Hostile semantic validation may be performed by a server-controlled validation engine/sandbox; Dedicated Server must not become a full RimWorld semantic parser.
8. The uploaded v2 ADR files are malformed as Markdown (almost all content is serialized onto one physical line). v3 must be normalized into readable structured Markdown.

No QA defect status changes.


## 23. MSR-013 Delta — ADR-003 Accepted

Source:
`ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v3.md`

Master decision:
**ADR-003 — Canonical Settlement State / Entity Identity / Save Provenance = ACCEPTED**

Master clarification incorporated into the authoritative accepted artifact:
- Server-authored committed deltas do not depend on client ACK for canonicality.
- `DELTA_BARRIER` client acknowledgement gates writer resumption/base advancement only.
- client failure after server commit fences the writer; next materialization reconstructs from artifact watermark + committed operations.
- PendingOperationQueue remains non-canonical.
- canonical EntityId is cross-process authority identity; native loadID is materialization-local.
- detailed transaction/recovery/compensation remains ADR-004.

Accepted ADR-003 core:
- B2-lite logical Settlement materialization artifact/package;
- durable rebuildable server projection/index;
- PendingOperationQueue / CommittedOperationLog / MaterializationManifest separation;
- ArtifactBaseStateRevision deterministic replay watermark;
- CommittedSettlementStateRevision canonical head;
- online ordinary DELTA_BARRIER integration contract;
- stable canonical EntityId with native loadID rebinding;
- layered hostile-input validation.

ADR-007 remains awaiting v3 review.
No QA defect status changes solely from ADR-003 acceptance.


## 24. MSR-014 Delta — Independent Remote Presentation QA + ADR-007 v3 Review

Source:
- `QA_Remote_Tactical_Presentation_Independent_Review.md`
- `ADR-007_Ordinary_Settlement_Simulation_Authority_v3.md`

### Remote Presentation Gate

Independent Sol QA classification:
**PARTIAL / INSUFFICIENT GRAPHICAL EVIDENCE**

Master accepts this classification.

Confirmed:
- normal graphical RimWorld client rendered the mirror map;
- camera / selection / inspect / Draft gizmo / right-click native UI lifecycle worked;
- selected mirror Pawn could be reconciled without immediate render/reference breakage;
- scripted Worker RPC authorization and stale command-generation rejection worked.

Not confirmed / failed:
- actual GUI Draft/right-click commands were not converted into remote intents;
- GUI actions mutated the local mirror while Worker state remained unchanged (`rpcCalls=0`);
- operational Worker tick + periodic replication cadence is absent;
- response/snapshot freshness fencing is absent;
- reconciliation scope is narrow and does not cover authoritative job/health/item/reservation/full-map state;
- the PoC fixture still carries unresolved dependencies;
- loopback performance evidence does not establish WAN/NFR SLO.

Architecture status:
- Candidate C remains PROVISIONALLY ACCEPTED.
- Candidate P2 Mirrored Client Map remains PRIMARY PRESENTATION CANDIDATE.
- Remote Tactical Production remains NOT AUTHORIZED.
- P2 is not falsified; the exact revision fails the mandatory GUI-to-Worker gate.

### ADR-007 v3

ADR-007 v3 remains **PROPOSED / REVISION REQUIRED**.

Reason:
Its `DELTA_BARRIER` flow still states that the client applies/ACKs the delta before the writer base advances and on failure falls back to "last committed head" without explicitly preserving the already Server-committed delta. This is ambiguous/in tension with ACCEPTED ADR-003 MD-023.

Required correction:
- Server-authored operation canonical commit is independent of client ACK.
- ACK gates only resumption of the current writer lease.
- if ACK/apply fails, fence/revoke the client and rematerialize from the current committed head **including the committed operation**.
- distinguish pre-commit barrier failure from post-commit client-application failure.


## 25. MSR-015 Delta — ADR-007 Accepted Core Contract

Source:
`ADR-007_Ordinary_Settlement_Simulation_Authority_v4.md`

Master decision:
**ADR-007 — Ordinary Settlement Simulation Authority / Topology = ACCEPTED for the core authority, lease, fencing, barrier, and handoff contract.**

Open Decision Requests remain:
- G-Q1 Multi-Settlement Topology
- G-Q2 Ordinary Simulation Anti-Cheat / Residual Trust
- G-Q6 Checkpoint Loss Window / Disconnect Grace

Master clarifications incorporated:
- barrier admission applies to both HANDOFF_BARRIER and DELTA_BARRIER;
- responsive DELTA_BARRIER may first accept one designated barrier checkpoint;
- Server-authored operation commit is independent of client ACK;
- writer resumption advances `BaseCommittedSettlementStateRevision`, not `ArtifactBaseStateRevision`;
- artifact watermark advances only when a new artifact fold containing that state is accepted;
- post-commit client failure fences the writer but never reverts the committed operation;
- immediate disconnect policy means server-side lease revocation/fencing, not trusting physical client stop.

Architecture status:
- ADR-001 ACCEPTED
- ADR-006A ACCEPTED
- ADR-003 ACCEPTED
- ADR-007 ACCEPTED (open Decision Requests above)
- ADR-002 PROVISIONALLY ACCEPTED
- ADR-004 not yet authored
- ADR-008 not yet authored

No QA defect closes solely from ADR-007 acceptance.


## 26. MSR-016 Delta — ADR-008 Work Package Started

New active analysis Work Package:
`WP-ADR-SHARED-WORLD-01`

Assigned:
Gemini 3.1 Pro C

Objective:
Produce PROPOSED `ADR-008_Shared_World_Layer_Transit_World_Projection.md`.

Scope:
- server-authoritative caravans / WorldObjects;
- transit custody and temporal policy candidates;
- world movement;
- vision-filtered projection;
- Tactical ingress/egress;
- tax/attack/retreat caravans;
- cross-domain EntityId and clock continuity.

Constraints:
- ADR-001/003/006A/007 are controlling upstream contracts.
- ADR-002 remains provisional.
- TBD-01..05 remain unresolved.
- No Production implementation.
- Product-policy questions must remain explicit Decision Requests.

Parallel work:
- A continues `WP-REMOTE-PRESENTATION-HARDEN-01`.
- C's ADR-008 analysis does not block or modify A's frozen presentation scope.


## 27. MSR-017 Delta — Remote Presentation Hardening Developer Evidence

Source:
`Remote_Tactical_Presentation_Hardening_01.md`

Master assessment:
**DEVELOPER EVIDENCE ACCEPTED / INDEPENDENT VERIFICATION PENDING**

A reports that the exact scratch RemotePresentation candidate now addresses the narrow failures from Sol's previous independent QA:

- actual native Draft gizmo path is intercepted and converted to remote intent;
- actual native right-click Move path is intercepted and converted to remote intent;
- local speculative Draft/ordered-job mutation is suppressed before Worker acceptance;
- Worker has bounded autonomous progression rather than harness-only tick stepping;
- replication binds TacticalSessionId / WorkerGeneration / TargetMapId / SnapshotSequence;
- stale/wrong session/generation/map snapshots are rejected;
- narrow reconciliation now includes Pawn identity, position, Draft, rotation, current job status and health;
- dependency-clean graphical profile and screenshots are reported;
- foreign Pawn and hostile AI commands remain rejected;
- Production remains untouched.

Master does NOT yet close QA-PRESENT findings from A self-report.

Important verification concerns:
- A's new snapshot-size/latency numbers must be independently checked; prior Sol QA measured materially larger full 51-Pawn responses.
- "health fully updated" and "job reconciliation" must be tested for destructive callback/divergence, not accepted from implementation description.
- Worker 60 TPS / 5 ticks-frame / 8 ms cadence is only a narrow 1x Tactical feasibility path, not yet a complete peaceful Last-Input-Wins speed policy or final temporal implementation.
- screenshots listed in A's local evidence are not by themselves Master-independent verification.
- test-only LOAD_SAVE / SET_GENERATION / static token controls remain non-Production evidence.

Gate:
- Candidate P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
- Sol narrow independent re-verification required on the frozen hardening candidate.


## 28. MSR-018 Delta — ADR-008 Draft-1 Review

Source:
`ADR-008_Shared_World_Layer_Transit_World_Projection.md`

Master verdict:
**ADR-008 Draft-1 = PROPOSED / REVISION REQUIRED**

Accepted architecture direction:
- Dedicated Server is canonical authority for Shared World Layer identity, existence, location, route state, visibility state, and world-domain ordering.
- client/Worker world state is projection/materialization only.
- world movement may advance while the Server runs and zero players are connected; Server downtime does not accrue WorldTick catch-up.
- vision filtering must occur server-side before hidden world state is projected.
- Tactical ingress/egress must reuse ADR-003 canonical EntityId/operation contracts and ADR-007 barriers.
- raw WorldTick is not a universal physiology clock.
- an explicit transit/residence clock domain is mandatory under ADR-006A.

Required revision:
1. G-Q11 is not a valid product choice as written. Client-proposed routing/path costs may never be blindly trusted as authoritative. The remaining architecture choice is between a deterministic server implementation and a server-controlled RimWorld/world-validation engine.
2. G-Q12 must not include a "No Clock" model. ADR-006A already requires an explicit transit/residence clock. The open choice is executor/materialization policy for that clock, not whether the clock exists.
3. Define durable `WorldStateRevision` and per-object/custody revision/fencing sufficient to reject stale world mutations without forcing one global hot lock.
4. Do not destroy a caravan at ingress before durable custody transfer. Model PREPARED/PENDING ownership transition conceptually and defer exact atomic commit/outbox/repair mechanics to ADR-004.
5. Egress must likewise avoid temporary double custody between Settlement and Shared World.
6. Offline Tax/Trade may be committed from the durable projection/index only when the required canonical facts are sufficient. Operations requiring RimWorld semantic mutation/validation must use a server-controlled engine/materialization path; "offline = always no engine" is not accepted.
7. `PendingOperationQueue` is Settlement-local. A concurrent world operation targeting a caravan during ingress must be serialized/fenced in the Shared World custody domain, not automatically stuffed into the target Settlement queue.
8. Mod approval must reject or quarantine unsupported world behavior at approval/migration time. Do not claim arbitrary unknown mod code can safely be "stripped".
9. Global Faction registry projection must not leak hidden world-object/location state.
10. Separate "world movement continues offline" from "transit physiology progresses offline"; the latter remains tied to the transit-clock policy.

No existing QA defect status changes.


## 29. MSR-019 Delta — ADR-008 Accepted Core Contract

Source:
`ADR-008_Shared_World_Layer_Transit_World_Projection_v2.md`

Master decision:
**ADR-008 — Shared World Layer / Transit / World Projection = ACCEPTED for the core world authority, revision/fencing, visibility projection, and custody-transfer contract.**

Accepted:
- Dedicated Server canonical authority over WorldObjects/caravans, authoritative location/path progress, custody membership, world visibility state, and world-domain ordering;
- client/Worker WorldObjects are projections/materializations only;
- untrusted clients submit destination intent only; authoritative path/movement facts are server-controlled;
- `WorldStateRevision` plus per-object/custody revision model;
- explicit `TransitClockId` distinct from W and Settlement L_s;
- server-side vision filtering before projection;
- PREPARED / INGRESS_PENDING / EGRESS_PENDING custody-transfer contract;
- one canonical custody owner per EntityId graph at commit boundaries;
- engine-free typed offline operation only when durable projection/index facts are sufficient;
- unsupported world-layer content handled by ADR-006B approval/migration policy.

Master clarifications:
- TransitClock is the physiological residence domain; W is not TransitTick.
- ingress/egress physiological reprojection is TransitClock <-> L_s.
- WorldStateRevision is not a universal global CAS lock; WorldObjectRevision fences independent object/custody mutations.
- exact custody transaction/recovery remains ADR-004.
- concrete server-controlled path executor remains runtime-validation dependent.

Open Decision Request G-Q12:
- G-Q12a transit physiology product semantics, including zero-player behavior;
- G-Q12b transit physiology execution/materialization mechanism.

No new Canonical TBD IDs created.

Architecture state now:
- ADR-001 ACCEPTED
- ADR-003 ACCEPTED
- ADR-006A ACCEPTED
- ADR-007 ACCEPTED
- ADR-008 ACCEPTED (G-Q12 open)
- ADR-002 PROVISIONALLY ACCEPTED
- ADR-004 not yet authored
- ADR-006B not yet authored

No runtime QA defect closes solely from ADR-008 acceptance.


## 30. MSR-019 Active Work Addition — ADR-006B Started

Assigned to Gemini 3.1 Pro C:
`WP-ADR-CONFIG-CONTENT-01`

Target:
PROPOSED `ADR-006B_Configuration_Content_Manifest.md`.

This work proceeds in parallel with Sol's independent re-verification of A's Remote Presentation hardening.

## 31. MSR-020 Delta — Remote Presentation Hardening Independent QA

Source: `QA_Remote_Tactical_Presentation_Hardening_02.md`

Master gate: **PARTIAL / REMAINING BLOCKER**

Independent closure:
- QA-PRESENT-001 — CLOSED: real graphical Draft/right-click Move enter the candidate RPC path; no pre-accept local authoritative Draft/Goto; foreign-Pawn GUI Draft rejection preserves local state.
- QA-PRESENT-003 — CLOSED: stale sequence, wrong session, wrong generation, and wrong map responses are rejected; delayed/replayed old TCP response does not regress state.

Still open:
- QA-PRESENT-002 — PARTIAL: Worker autonomous progression exists, but no operational repeated authoritative replication path; mirror stalls after initial Move response.
- QA-PRESENT-004 — PARTIAL: job/status and health/Hediff graph reconciliation remain incomplete.
- QA-PRESENT-005 — STILL FAILING: rotation wire encoding mismatch.
- QA-PRESENT-006 — STILL FAILING: test-control commands remain on the same endpoint before normal auth/generation checks.
- QA-PRESENT-007 — PARTIAL: cadence boundedness improved, but blocking receive, unbounded queue drain and legacy monolithic paths remain.
- QA-PRESENT-008 — STILL FAILING: evidence/metric oracle still conflates PING with snapshot size and explicit refresh with operational replication.
- QA-PRESENT-009 — STILL FAILING: fixture/profile still has semantic dependency errors.
- QA-PRESENT-010 — STILL FAILING: reconciliation still targets `Find.CurrentMap` rather than an authority-bound map.

Architecture:
- Candidate P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.

Parallel:
- A receives `WP-REMOTE-PRESENTATION-HARDEN-02`.
- C continues ADR-006B.


## 32. MSR-021 Delta — ADR-006B Draft-1 Review

Source:
`ADR-006B_Configuration_Content_Manifest.md`

Master verdict:
**ADR-006B Draft-1 = PROPOSED / REVISION REQUIRED**

Accepted direction:
- Dedicated Server pins authoritative gameplay content/profile identity.
- gameplay-affecting client/Worker content requires compatibility admission.
- content/config revisions participate in lease/checkpoint/materialization admission.
- semantic dependency validation must be layered; XML/string scanning alone is insufficient.
- unsupported/unclassified world/simulation content is rejected/quarantined before live admission.
- config retroactivity must be explicitly classified.
- cosmetic/client-only content requires a separately approved capability boundary.
- content migration is a server-controlled process and must not silently drop canonical state.

Required corrections before acceptance:
1. Replace "all Def cross-references statically proven" with layered dependency closure. Static proof is insufficient for dynamic/runtime-created references; approval requires static registry checks plus controlled-engine load/semantic validation.
2. Replace the absolute runtime guarantee "must not fail due to missing content/schema" with an invariant that **server-pinned content drift must not be caused by an untrusted participant**. Runtime defects/corruption may still fail safely into quarantine/REPAIR_REQUIRED without turning the target into an attack-immune state.
3. Migration must not load an old artifact directly under only the new profile. The migration pipeline must preserve an old-profile-compatible read/materialization context, then transform/validate into the new profile (or use an explicitly supported dual-profile migration adapter).
4. `ContentProfileId` and `ContentProfileRevision` semantics need sharpening: immutable profile identity/fingerprint vs. monotonically ordered world adoption/migration revision. Do not treat a changed profile as the same immutable identity unless defined by a separate stable lineage ID.
5. Artifact/checkpoint metadata must bind both the exact gameplay profile fingerprint and the schema/codec versions required for deterministic validation.
6. Add a `MIGRATION_REQUIRED` / `QUARANTINED` admission state distinct from generic `REPAIR_REQUIRED`.
7. Cosmetic mod eligibility cannot rely on an unverifiable universal proof. It requires server-approved capability classification and fail-closed exclusion from authority-sensitive hooks unless validated.
8. Config categories need a `MIGRATION_REQUIRED` class in addition to prospective/snapshotted/session-bound/historical.
9. Operation-snapshotted config must capture the exact value/config revision in durable operation state; referencing only "current ConfigRevision" later is insufficient.
10. Client handshake ordering must align with ADR-001 lifecycle: compatibility/profile checks may happen during handshake, but content mismatch is not itself authentication and must not collapse auth/session semantics.

No QA defect statuses change from this draft review.

## 33. MSR-022 Delta — ADR Evidence Policy / Project Checkpoint

Master governance policy added:
`MASTER_ADR_EVIDENCE_POLICY.md`

Key rule:
ADR ACCEPTED means an architecture contract is chosen, not that implementation/runtime proof is complete.

Evidence classes:
- E0 analytical/contract evidence
- E1 developer feasibility evidence
- E2 independent verification
- E3 Production/regression evidence

Engine-feasibility ADRs require E2 for their central existential claim.
Normative contracts may be accepted at E0 with explicit runtime proof obligations.
Hybrid ADRs may accept the core while leaving runtime-sensitive subcontracts provisional/open.

Project checkpoint:
`MASTER_PROJECT_CHECKPOINT_MPC-001.md`

Current phase:
late architecture / targeted feasibility, before broad Production vertical-slice implementation.


## 34. MSR-023 Delta — ADR-006B Accepted

Source:
`ADR-006B_Configuration_Content_Manifest_v2.md`

Master decision:
**ADR-006B — Configuration & Content Manifest = ACCEPTED (core contract).**

Accepted core:
- immutable exact gameplay `ContentProfileFingerprint`;
- stable profile lineage identity + monotonic world adoption `ContentProfileRevision`;
- artifact/checkpoint profile + schema + semantic/temporal codec binding;
- content compatibility as admission, separate from identity authentication;
- layered dependency closure: manifest/hash -> typed static checks -> controlled engine load -> post-load semantic validation;
- runtime `QUARANTINED` / `REPAIR_REQUIRED`, with no silent drop;
- config retroactivity categories including OPERATION_SNAPSHOTTED and MIGRATION_REQUIRED;
- old-profile-compatible migration read -> transform -> new-profile validation -> canonical adoption;
- server-approved fingerprint-bound cosmetic capability profile.

Master clarifications:
- ContentProfileRevision advances only after successful canonical adoption;
- staged/failed migration does not replace the current active profile;
- clients cannot self-declare cosmetic safety;
- pinned content prevents participant-driven drift but cannot guarantee runtime defects never occur;
- exact durable migration transaction/recovery remains ADR-004;
- validator effectiveness remains a runtime proof obligation.

Architecture state:
- ADR-001 ACCEPTED
- ADR-003 ACCEPTED
- ADR-006A ACCEPTED
- ADR-006B ACCEPTED
- ADR-007 ACCEPTED
- ADR-008 ACCEPTED
- ADR-002 PROVISIONALLY ACCEPTED
- ADR-004 next architecture priority
- ADR-005 later

No runtime QA defect closes solely from ADR-006B acceptance.

## 35. MSR-024 Delta — Remote Presentation Hardening-02 Developer Evidence

Source:
`Remote_Tactical_Presentation_Hardening_02(1).md`

Master assessment:
**DEVELOPER EVIDENCE ACCEPTED / INDEPENDENT VERIFICATION REQUIRED**

A claims the prior narrow P2 blocker is closed:
- autonomous client-controller replication after Move;
- 17 periodic authoritative updates at ~6.14 Hz;
- graphical mirror follows Worker to destination without TestHarness GET_SNAPSHOT;
- authority-bound target-map application;
- four-direction rotation wire contract;
- fixture dependency-complete profile;
- privileged test-control gating;
- cadence debt accounting correction.

Master does not close any additional QA-PRESENT defect from A self-report alone.

Important verification concerns:
1. A labels Draft/Move as REAL_GRAPHICAL_OBSERVATION, but the report describes direct invocation of `Command_Toggle.ProcessInput(null)` and `TryTakeOrderedJob(...)`. Sol must distinguish actual OS/user GUI input from in-process method invocation.
2. The reported privileged gate is `PrivilegedQaToken OR Source == "QA_TEST_CONTROL"`. If `Source` is client-controlled, an untrusted client may forge the source string and bypass the token. This must be attacked explicitly.
3. Periodic replication uses timer-driven GET_SNAPSHOT polling. This is allowed for feasibility, but Sol must verify it is operational controller behavior, not TestHarness behavior, and assess main-thread blocking/overlap/liveness.
4. QA-PRESENT-007 remains open unless blocking/unbounded dispatch risks are actually resolved.
5. Dependency-clean evidence must be independently checked; adding QA-only probe mods may make the test fixture complete, but does not prove Production profile readiness.
6. ~16.8 KB full 51-Pawn snapshots at ~6.14 Hz are loopback feasibility evidence only, not WAN/NFR proof.
7. General health/job/full-map replication remains outside this narrow feasibility gate.

Gate:
- Candidate P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
- Sol focused independent verification is the next required step.

Parallel:
- C continues ADR-004 Transaction/Repair.

## 36. MSR-025 Delta — ADR-004 Draft-1 Review

Source:
`ADR-004_Distributed_Ownership_Transaction_Repair.md`

Master verdict:
**ADR-004 Draft-1 = PROPOSED / REVISION REQUIRED**

Accepted direction:
- OperationId + immutable payload hash idempotency;
- separate PREPARED / COMMITTED / PUBLISH_PENDING lifecycle;
- canonical commit is Server-controlled and distinct from RimWorld artifact publication;
- pre-commit abort vs post-commit forward recovery distinction;
- one-canonical-custody-owner invariant;
- outbox/journal/reconciler architecture;
- stale writer fencing and restart recovery requirements.

Critical corrections required:
1. Do not assume `CommittedOperationLog` alone can reconstruct every committed Tactical/material-state result after artifact loss. Engine-produced state may not be fully representable as typed domain operations.
2. Before canonical COMMIT, any non-reconstructible material result required by that commit must exist as a **durable immutable staged result/candidate** with hash, profile/schema identity, source/base revision and result manifest. The staged candidate is non-canonical but recovery-addressable.
3. Canonical commit must durably bind the operation to either:
   - reconstructible committed operations from an older artifact watermark; or
   - a durable staged material result that can be promoted/re-published after restart.
   A commit may not depend on volatile Worker/client memory.
4. Artifact promotion is conditional on exact manifest/base/head/profile/hash validation. An arbitrary candidate file may never be promoted just because the DB operation committed.
5. Disconnect/crash before COMMIT does not always imply ABORT. If the Server has a complete durable PREPARED record and all required authoritative facts/staged material, a Server-owned operation may continue to commit. Otherwise it aborts/expires.
6. `PREPARED` reservations/locks require deterministic lock ordering, expiry/recovery ownership, and explicit distinction between durable reservation and writer fencing. Avoid permanent deadlocks after restart.
7. EntityIds reserved during PREPARED are provisional/reserved identifiers only; they are not canonical visible entities until COMMITTED.
8. Cross-scope commit must define one transactionally consistent commit record covering source custody, destination custody, operation state, and source/destination revisions. `SettlementProjectionRevision` is not a substitute for canonical material revision.
9. Projection/outbox updates are derived side effects and must not be described as part of the canonical truth unless they are explicitly in the same durable DB transaction. Projection may lag canonical commit and be repaired.
10. Failure matrix row “during DB commit = ambiguous” is too weak. After restart, durable storage must deterministically classify the transaction as committed or not committed; ambiguity may exist to the caller, not in canonical recovery.
11. Semantic validation failure after materialization must distinguish:
    - pre-commit candidate rejection/quarantine;
    - post-commit publication validation failure, which requires forward repair/quarantine and must not erase the committed domain decision.
12. Exact transaction behavior must support both:
    - typed operation-only commits;
    - commits whose material-state consequence requires a durable staged artifact/result manifest.

No existing QA defect closes from this draft.


## 37. MSR-026 Delta — ADR-004 Accepted

Source:
`ADR-004_Distributed_Ownership_Transaction_Repair_v2.md`

Master decision:
**ADR-004 — Distributed Ownership Transaction / Repair = ACCEPTED (core contract).**

Accepted core:
- OperationId + immutable payload-hash idempotency;
- two commit classes: replayable typed operation vs durable staged material result;
- no canonical commit may depend on volatile Worker/client memory;
- durable PREPARED reservation boundary;
- deterministic committed-vs-not-committed recovery after DB crash;
- canonical commit separated from artifact/projection publication;
- post-commit forward recovery rather than erasing committed events;
- one canonical custody owner at commit boundaries;
- staged-result hash/profile/schema/base/head validation;
- projection/outbox lag treated as repairable derived state.

Master clarifications:
- `CommittedSettlementStateRevision` is canonical material head; `ArtifactBaseStateRevision` is only the artifact fold watermark;
- PREPARED reservations must survive restart and follow deterministic scope ordering;
- cross-custody COMMIT atomically binds source + destination dispositions/revisions + result reference;
- barrier admission blocks conflicts before commit; post-commit fencing generation/revision advance rejects old writers;
- committed staged material remains retained until publication/repair supersession completes;
- orphan staged material remains non-canonical and is GC-eligible only after recovery proves it is unreferenced;
- typed log alone is not universally sufficient for staged-material recovery.

Architecture state:
- ADR-001 ACCEPTED
- ADR-003 ACCEPTED
- ADR-004 ACCEPTED
- ADR-006A ACCEPTED
- ADR-006B ACCEPTED
- ADR-007 ACCEPTED
- ADR-008 ACCEPTED
- ADR-002 PROVISIONALLY ACCEPTED
- ADR-005 not yet authored

No runtime QA defect closes solely from ADR-004 acceptance.

Next architecture-to-production transition:
compose the accepted ADRs into the Shared Settlement State Pipeline design and first Production vertical-slice gate.


## 38. MSR-027 Delta — Remote Presentation Hardening-03 Independent QA

Source:
`QA_Remote_Tactical_Presentation_Hardening_03.md`

Master gate:
**PARTIAL / REMAINING BLOCKER**

Independent E2 results accepted:

### Newly CLOSED
- **QA-PRESENT-002 — CLOSED**
  - Worker autonomous movement plus normal `RemoteClientController.Update()` periodic replication independently reproduced.
  - 30 automatic post-command updates arrived without TestHarness/manual GET_SNAPSHOT.
  - client native `Pawn.Position` and coarse move completion converged to Worker state.

- **QA-PRESENT-005 — CLOSED**
  - North/East/South/West round-trip independently verified through actual Worker -> wire -> normal periodic client apply.

- **QA-PRESENT-010 — CLOSED**
  - client apply is bound to snapshot TargetMapId rather than viewed `Find.CurrentMap`.
  - Map_1 remained unchanged while Map_0 was authoritative target.
  - unresolved target map was explicitly rejected.

### Still OPEN / material blockers
- **QA-PRESENT-004 — STILL FAILING / HIGH**
  - `Pawn.Position` follows authoritative snapshots but rendered `Pawn.DrawPos`/sprite remains at the old location.
  - screen position, hit target, selection/inspect coordinates therefore diverge.
  - health/Hediff graph reconciliation also remains incomplete.

- **QA-PRESENT-006 — STILL FAILING / HIGH-IF-PROMOTED**
  - `cmd.Source == "QA_TEST_CONTROL"` is remote/client-controlled and grants privileged control.
  - invalid token / stale generation / wrong session + forged Source successfully executed privileged controls, including generation mutation and fixture reload.

- **QA-PRESENT-007 — STILL FAILING / HIGH-IF-PROMOTED**
  - timer replication performs synchronous socket `ReadLine` on the Unity main thread.
  - a 2-second delayed response caused ~2.03 s frame gap and ~1.87 s control-response delay.
  - timeout/reconnect and bounded queue/list behavior remain incomplete.

### Still OPEN / partial
- **QA-PRESENT-008 — PARTIAL**
  - periodic payload/cadence metrics are now materially improved and independently consistent;
  - A's evidence oracle still conflates direct native method invocation with actual OS GUI input in its own harness and does not check DrawPos/displayed movement.

- **QA-PRESENT-009 — PARTIAL**
  - declared fixture dependencies are now present and prior missing class/Def symptoms are resolved;
  - texture/null-material, auxiliary listener conflict, and headless initialization errors remain, so a clean canonical load is not certified.

Previously closed and regression-confirmed:
- QA-PRESENT-001 — CLOSED
- QA-PRESENT-003 — CLOSED

Architecture:
- P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- P2 is **not falsified**.
- tested Draft/Move internal state replication is E2-proven.
- rendered Move presentation is not yet E2-proven.
- Remote Tactical Production remains NOT AUTHORIZED.

Next:
- A receives a narrowly scoped Hardening-03 implementation WP.
- C continues Shared Settlement State Pipeline Design.


## 39. MSR-028 Delta — Shared Settlement State Pipeline Design-01 Review

Source:
`Shared_Settlement_State_Pipeline_Design_01.md`

Master verdict:
**INCOMPLETE DELIVERABLE / RESUBMISSION REQUIRED**
**Production implementation remains NOT AUTHORIZED.**

The submitted file terminates during the `OperationRecord` sketch and does not contain the majority of the required Work Order deliverables.

Direction accepted provisionally:
- Operation Journal
- Canonical State / Revision Store
- Settlement Projection / Index Store
- Artifact Store
- Staged Result Store
- Publication Outbox
- Recovery Reconciler
- Writer Lease / Fencing Registry
- Content/Profile Admission
- MaterializationManifest Builder
- EntityId Registry

Required corrections:
1. Complete the missing design sections: remaining DTOs, transaction sequences, Production Gate, runtime proof plan, open-decision isolation, and proposed A implementation WP outline.
2. Add the required Semantic Validation Adapter and Audit/Receipt surface.
3. Do not use Tax/Auto-Shop semantics as the first plumbing slice unless inventory canonicality is already fixed. G-Q8, G-Q9, and TBD-05 remain open.
4. Prefer a policy-neutral internal pipeline operation/fixture for the first infrastructure implementation, or explicitly prove that a chosen real operation does not depend on unresolved inventory/tax/auto-shop policy.
5. Recovery Reconciler must not blindly abort every expired PREPARED record. Under ADR-004, complete durable PREPARED operations may continue autonomously when operation policy allows.
6. Do not imply the Projection/Index is universally rebuildable from Artifact + typed CommittedOperationLog only; staged-material commits may require their canonical/staged result chain.
7. `ArtifactBaseStateRevision`/artifact pointer advances only after validated artifact fold; canonical `CommittedSettlementStateRevision` may already be ahead.
8. Lease timeout behavior must not silently resolve G-Q6. Design the mechanism while leaving grace/expiry policy open behind configuration/decision boundary.

No runtime QA defect status changes.

Parallel work remains:
- A: Remote Presentation Hardening-03
- C: Pipeline Design-02 resubmission
- Sol: next focused presentation E2 verification after A freezes candidate


## 40. MSR-029 Delta — Shared Settlement State Pipeline Design-02 Accepted for Narrow Infrastructure Slice

Source:
`Shared_Settlement_State_Pipeline_Design_02.md`

Master verdict:
**DESIGN ACCEPTED WITH MASTER CORRECTIONS**
**NARROW PRODUCTION INFRASTRUCTURE IMPLEMENTATION AUTHORIZED / QUEUED**

Key correction:
The proposed `TEST_TYPED_NOOP_SYNC` must **not** increment `CommittedSettlementStateRevision` without an actual Settlement material-state mutation.

Accepted first implementation slice:
`PIPELINE_PROBE_CAS`
- dedicated non-gameplay `ProbeScopeId`
- dedicated `ProbeRevision`
- uses Production transaction/journal/outbox/recovery infrastructure
- not exposed to ordinary gameplay protocol in release configuration
- does not mutate Settlement inventory/material state
- does not resolve G-Q8/G-Q9/TBD-05

Authorized Slice-01 components:
- SQLite-first Operation Journal / transaction persistence
- Probe aggregate CAS/revision store
- CommitReceipt / audit records
- Publication Outbox
- Recovery Reconciler
- idempotency / payload collision protection
- bounded reservation/recovery metadata
- tracing by OperationId

Deferred from Slice-01:
- real Settlement material mutation / CommittedSettlementStateRevision change
- Artifact fold/replay implementation
- staged Tactical result promotion
- EntityId custody transfer
- Tax / Auto-Shop / trade semantics
- Tactical barriers and Worker publication

A remains assigned to Remote Presentation Hardening-03 first.
The Production infrastructure WP is authorized but **queued**; A should begin it only after freezing/completing the current Hardening-03 candidate so the Tactical QA target is not disturbed.

C is free for the next architecture analysis after this design acceptance.

## 41. MSR-030 Active Work — ADR-005 Started

C completed the accepted Shared Settlement State Pipeline Design-02 task.

Assigned to Gemini 3.1 Pro C:
`WP-ADR-INTENT-BETRAYAL-01`

Target:
PROPOSED `ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract.md`

This work is independent of:
- A's current Remote Presentation Hardening-03;
- the queued Production Transaction Pipeline Slice-01.

Current execution order for A:
1. finish/freeze Remote Presentation Hardening-03;
2. Sol focused E2 verification;
3. then begin authorized `WP-PROD-TRANSACTION-PIPELINE-01` unless Master redirects based on QA.

## 42. MSR-031 Delta — Remote Presentation Hardening-03 Developer Candidate Frozen

Source:
`Remote_Tactical_Presentation_Hardening_03.md`

Frozen candidate:
- DLL SHA256 `0F57AFB12BE7D7C8FF1F12C231F8A3CA9815FB76069BEBDBB723604488C582BB`
- Fixture SHA256 `ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED`
- Production `WarEconomyMod/` reported unchanged by A

Master assessment:
**DEVELOPER EVIDENCE ACCEPTED / E2 INDEPENDENT VERIFICATION REQUIRED**

A claims:
- rendered Pawn Position/DrawPos convergence and hit-target consistency;
- separate gameplay/control transport closing forged Source privilege bypass;
- background non-blocking replication with bounded in-flight request;
- 2-second delayed response without Unity main-thread freeze;
- disconnect degraded-state handling and reconnect;
- candidate-local fixture/init cleanup;
- improved evidence classification and UTF-8 byte metrics.

Important Master interpretations:
1. A's report is E1, not E2. A cannot self-certify closure of independent QA gates.
2. The new candidate's Draft and Move tests are explicitly `SCRIPTED_GUI_CALL`, not actual OS/user GUI command evidence. Previous E2 actual-OS evidence exists for the prior candidate, but the new frozen candidate requires focused GUI regression.
3. The report's hit-target test uses native query/selector calls. Sol must verify a real OS/user click on the visibly moved Pawn resolves correctly.
4. QA-PRESENT-004 is broader than rendering. If render/hit-target is fixed but health/general reconciliation remains incomplete, official defect may remain PARTIAL even while the narrow Draft/Move presentation feasibility gate passes.
5. QA-PRESENT-006 can close for the PoC/test surface only if privileged controls are truly unreachable through ordinary gameplay transport and control privilege cannot be forged from untrusted payload fields. This does not certify Production authentication.
6. QA-PRESENT-007 requires verification that background transport performs no Unity/RimWorld object mutation off-main-thread, has bounded/coalescing apply behavior, deadlines, disconnect fencing, and rejects late stale responses.
7. QA-PRESENT-009 remains pending independent log/profile verification.

Gate state:
- Candidate P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
- A must not modify the frozen presentation candidate while Sol verifies it.
- The queued `WP-PROD-TRANSACTION-PIPELINE-01` remains queued until this focused E2 result is reviewed.

Parallel:
- Sol: `WP-QA-REMOTE-PRESENTATION-HARDEN-04`
- C: ADR-005 Intent/Betrayal analysis

## 43. MSR-032 Delta — ADR-005 Draft-1 Review

Source:
`ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract.md`

Master verdict:
**ADR-005 Draft-1 = PROPOSED / REVISION REQUIRED**

Accepted direction:
- Intent, simulation facts, domain evaluation, and political commit are separate layers.
- Tactical Worker remains Simulation Authority only.
- Dedicated Server remains final betrayal/diplomacy Domain Authority.
- intent provenance must bind authenticated principal/session, canonical identities, Tactical session/generation and diplomacy context.
- mid-session relationship changes must be revisioned and projected back to active Tactical sessions.
- trap/turret/mental-break/autonomous cases require explicit provenance and product policy.

Required corrections before acceptance:
1. Client intent must be admitted/authorized by the Dedicated Server before it becomes an `AuthorizedAction`. Worker may validate simulation preconditions but must not be a co-authority for domain authorization.
2. Do not use one `OperationId` as both intent identity and all simulation-fact identities. One action can produce many projectiles/hits/AOE facts. Add distinct `IntentId/OperationId`, `ActionExecutionId`, `FactId/EventSequence`, and causal-parent/root identity.
3. Autonomous events without a live PlayerIntent need a first-class provenance root (`AutonomousActionContext` or equivalent), not a fabricated player intent.
4. Do not hard-code betrayal timing/policy from the intent-time `DiplomacyRevision`. Record authorization-time and decision-time relationship revisions and let explicit product policy decide how mid-flight diplomacy changes are treated.
5. Do not hard-code “mid-air alliance => no retroactive betrayal”, “offline AI targeting errors never betray”, or “direct targeted attack + DamageFact is sufficient”. These are product-policy Decision Requests unless directly fixed by canonical SRS.
6. Distinguish Tactical control authority from ADR-007 writer lease. Client pawn command authorization requires owner/controller assignment and Tactical control/session fencing; the Worker lease is not itself the player's command right.
7. A committed live `RelationshipTransition` must not be placed in ADR-003 `PendingOperationQueue` as if it were uncommitted state, nor rely on `MaterializationManifest` for mid-session delivery. Define a durable/replayable Session Domain Event / Outbox stream for already-committed domain events.
8. Worker fact dedupe must be by fact/event identity, not OperationId alone. Multiple legitimate facts under one action must survive.
9. Worker crash after physical execution but before fact report cannot simply mean “facts lost -> ABORTED”. If material outcome survives or can later be canonically published, required provenance/facts must be durably recoverable or the candidate must be rejected/quarantined as semantically incomplete.
10. Betrayal/domain transition commit must CAS against a scoped diplomacy/relationship aggregate revision; do not assume one global hot `DiplomacyRevision` unless intentionally designed.
11. Separate evidence records from canonical political state. PlayerIntent/SimulationFact/DamageFact may be durably journaled evidence, while BetrayalDecision/RelationshipTransition are canonical domain state transitions.
12. Define ordered/idempotent mid-session event ACK/replay semantics. Worker/client ACK may gate local projection readiness but never the Server's already-durable political commit.

Existing Canonical TBD-01..05 remain unchanged.
No runtime QA defect status changes.

Parallel:
- Sol continues focused Remote Presentation Hardening-04 E2 QA.
- A remains paused with the frozen presentation candidate and queued Production transaction slice.
- C receives ADR-005 v2 revision work.


## 44. MSR-033 Delta — ADR-005 Accepted

Source:
`ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract_v2.md`

Master decision:
**ADR-005 — Intent / Betrayal / Domain-Simulation Event Contract = ACCEPTED (core contract).**

Accepted core:
- Server-first authorization of untrusted CommandIntent;
- immutable `AuthorizedActionEnvelope`;
- separate `IntentId` / `ActionExecutionId` / `FactId` / causal identities;
- `AutonomousActionContext` for non-player-originated events;
- scoped diplomacy aggregate revisions rather than one mandatory global hot revision;
- product-policy separation for betrayal trigger timing/liability;
- durable politically relevant fact provenance tied to ADR-004 staged-result/event durability;
- ordered durable `SessionDomainEventLog` / domain outbox for already-committed mid-session political changes;
- Worker projection ACK/replay that never controls the Server's canonical political commit;
- Worker remains Simulation Authority only; Dedicated Server remains final betrayal/diplomacy Domain Authority.

Master clarifications:
- authorization-time revision is provenance, not the final CAS target;
- G-Q16 remains open: intent-time vs impact/decision-time precedence is not decided;
- multiple facts under one intent are preserved and deduped by FactId/event identity;
- session delivery order must preserve diplomacy aggregate revision order;
- missing required provenance blocks/quarantines material publication rather than silently inferring a betrayal outcome;
- G-Q13..G-Q17 and TBD-03 remain open.

Architecture state:
- ADR-001 ACCEPTED
- ADR-003 ACCEPTED
- ADR-004 ACCEPTED
- ADR-005 ACCEPTED
- ADR-006A ACCEPTED
- ADR-006B ACCEPTED
- ADR-007 ACCEPTED
- ADR-008 ACCEPTED
- ADR-002 PROVISIONALLY ACCEPTED

No runtime QA defect closes solely from ADR-005 acceptance.

Current parallel:
- Sol: Remote Presentation Hardening-04 E2 verification
- A: frozen presentation candidate; queued Production Transaction Pipeline Slice-01
- C: next assigned to open-decision dependency mapping / sequencing

## 45. MSR-034 Delta — Open Decision Dependency Map Adopted with Master Corrections

Source:
`Open_Decision_Dependency_Map_01.md`

Master disposition:
**ACCEPTED AS SEQUENCING BASELINE WITH MASTER CORRECTIONS**

Key accepted findings:
- `PIPELINE_PROBE_CAS` is blocked by no open policy decision.
- TBD-05 is a hard blocker for offline Tax semantics.
- G-Q5 mid-session domain-event transport is CLOSED / absorbed by ADR-005; G-Q5b Storyteller policy remains open.
- ADR-005 successfully allows G-Q13..17 liability rules to remain behind a stable evaluator interface.
- G-Q2/G-Q6 can be isolated behind explicit interfaces until their production acceptance point.

Key corrections:
- G-Q10 does not block offline attack core; it is an online-owner WAN/UX acceptance gate.
- G-Q5b does not block betrayal infrastructure.
- G-Q13..17 block feature-complete liability behavior, not intent/fact/event infrastructure.
- G-Q8 blocks inventory-based canonical mutation/indexing, not every possible Settlement mutation.
- G-Q1 requires architecture/runtime evidence, not only product preference.
- G-Q12a/b block transit physiology, not basic caravan custody ingress/egress.
- TBD-01/02/04 block their specific faction-join / forced-expulsion / extinction behaviors, not generic Occupy/Destroy as a whole.
- temporary defaults in C's analysis are not approved Production policy.

Official cleanup:
- G-Q5 = CLOSED / ABSORBED BY ADR-005
- G-Q5b = OPEN
- Canonical TBD-01..05 remain OPEN
- G-Q1/2/4/6/8/9/10/12a/12b/13..17 remain OPEN unless separately resolved

No runtime QA defect changes.

Current execution:
- Sol: Remote Presentation Hardening-04 E2
- A: frozen presentation candidate; Production Pipeline Slice-01 queued
- C: next decision-brief analysis on G-Q8


## 46. MSR-035 Delta — Remote Presentation Hardening-04 Independent QA

Source:
`QA_Remote_Tactical_Presentation_Hardening_04.md`

Master gate:
**PARTIAL / REMAINING BLOCKER**

Independent E2 findings adopted:

### E2 proven
- actual OS/user Draft and native Go-here interaction reaches the adapter/RPC/Worker path;
- no speculative local final Draft/Goto commit before authoritative apply;
- foreign Pawn command remains rejected;
- Worker autonomous movement is repeatedly replicated;
- rendered Pawn Position/DrawPos follows authoritative movement;
- at least three distinct intermediate rendered positions were observed;
- final rendered position converges and actual click/selection resolves the moved Pawn;
- target-map binding, snapshot fencing, and four-direction rotation regressions remain intact;
- required privileged control commands are blocked on gameplay transport and accepted only through the PoC-local trusted control channel/capability.

### Official defect updates
- QA-PRESENT-001 — CLOSED
- QA-PRESENT-002 — CLOSED
- QA-PRESENT-003 — CLOSED
- QA-PRESENT-004 — PARTIAL
  - rendered movement / hit-target sub-blocker = CLOSED
  - broader health/job/lifecycle reconciliation = STILL FAILING
- QA-PRESENT-005 — CLOSED
- QA-PRESENT-006 — CLOSED (PoC/test-control boundary only; not Production auth)
- QA-PRESENT-007 — STILL FAILING / HIGH
- QA-PRESENT-008 — PARTIAL
- QA-PRESENT-009 — PARTIAL
- QA-PRESENT-010 — CLOSED

### Remaining narrow presentation blocker
Interactive GUI command I/O is still synchronous on Unity thread:
`GUI callback -> SendCommand -> socket ReadLine`

A delayed Draft response of ~2 seconds caused a ~2.03 second main-thread frame freeze.

Periodic replication is independently improved:
- network wait off-main-thread;
- bounded one-in-flight periodic request;
- single-slot coalescing;
- 3.5s receive timeout;
- delayed/closed socket and stale late response fencing reproduced.

But this does not fix the interactive command path.

### Additional candidate-local issues
- auxiliary WorkerBridge/QA listener port arguments are not actually honored under the current split-argument runner syntax; default ports are used and client-side bind exceptions recur.
- dependency/missing Def/texture issues improved, but candidate profile is not yet cleanly initialized.
- background telemetry/command queues and retention are not all bounded.
- disconnect/coalesced-snapshot epoch ordering is not fully proven.

Architecture:
- P2 remains PRIMARY PRESENTATION CANDIDATE.
- normal-condition rendered Draft/Move path is E2-feasible.
- full tested Draft/Move interaction slice is not yet E2-passed because interactive command liveness fails.
- Candidate C / ADR-002 remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.

Execution order:
- A receives one more narrow Remote Presentation hardening WP.
- queued `WP-PROD-TRANSACTION-PIPELINE-01` remains queued until the next focused presentation E2 result is reviewed.
- C continues G-Q8 decision brief analysis.


## 47. MSR-036 Delta — Hardening-04 QA Addendum / Dynamic Facing

Source:
`QA_Remote_Tactical_Presentation_Hardening_04(1).md`, Section 12 addendum.

Master disposition:
**Addendum accepted. New defect QA-PRESENT-011 opened.**
Overall Hardening-04 gate remains:
**PARTIAL / REMAINING BLOCKER**

### New defect
**QA-PRESENT-011 — Dynamic Facing / Authoritative Pose Staleness — OPEN / MEDIUM**

Independent preserved-evidence review found:
- during a real westward Move, Worker snapshots retained `Rotation=East` through 84 consecutive Goto samples;
- during a later real eastward Move, Worker snapshots retained `Rotation=West` through 24 Goto samples;
- the Client correctly applied the received rotation, so this is not evidence of the previously-fixed East/West wire codec bug;
- the defect boundary is the Worker-side authoritative presentation pose/facing source or its engine update conditions.

Master interpretation:
- QA-PRESENT-005 remains CLOSED for 4-way rotation wire representation and round-trip.
- QA-PRESENT-011 is separate: whether the Worker emits semantically current facing/pose during movement/aim/stance.
- Do not blindly derive facing from position delta on the Client, because legitimate aim/focus/stance can intentionally differ from movement direction.
- Root cause is not yet fixed or fully classified; Worker movement vector/path-next-cell, stance/focus/aim target, native Rotation/body/head/render pose must be correlated first.

### Impact on current A assignment
`WP-REMOTE-PRESENTATION-HARDEN-04` is superseded by:
`WP-REMOTE-PRESENTATION-HARDEN-04-REV1`

REV1 retains all prior interactive-command async / epoch / queue / listener cleanup requirements and adds the narrow dynamic-facing investigation/fix.

Remote Tactical Production remains NOT AUTHORIZED.
Candidate C / ADR-002 remains PROVISIONALLY ACCEPTED.


## 48. MSR-037 Delta — G-Q8 Inventory Boundary Decision Brief Review

Source:
`GQ8_Settlement_Inventory_Boundary_Decision_Brief_01.md`

Master disposition:
**DECISION BRIEF ACCEPTED AS ANALYSIS INPUT / G-Q8 REMAINS OPEN**

The brief correctly identifies that:
- physical presence, custody, economic eligibility, and safe mutation are different concepts;
- nested ThingOwner / Pawn-bound / transfer-staging assets are materially riskier than simple fungible ground stock;
- runtime RimWorld 1.6 evidence is required before assuming engine-free mutation is safe across complex asset graphs;
- G-Q8 blocks inventory-dependent Production semantics, but not `PIPELINE_PROBE_CAS`.

Master corrections:
1. Do not define one universal set called "Settlement Inventory" for Auto-Shop, Tax seizure, tier/wealth projection, and canonical material custody.
2. Under G-Q8, distinguish at least:
   - `SettlementEconomicInventory` / sellable-fungible projection used by Auto-Shop availability;
   - `TaxSeizableAssetSet` used by forced tax collection;
   - underlying `SettlementAssetGraph` / canonical custody graph.
   These may overlap but are not required to be identical.
3. SRS tax eligibility for Pawn/Animal/Slave does not imply that equipped weapons/apparel are independently tax-seizable items or part of Auto-Shop inventory. That remains policy/engine semantics.
4. The brief is internally inconsistent where it marks equipped gear tax-eligible while later asking whether Pawn Tax means stripping gear or taking the Pawn entity. Treat that question as unresolved.
5. "Job-reserved items are safe offline because LocalTick is frozen" is not accepted. Frozen LocalClock prevents progression; it does not prove that saved Job/Reservation/Lord/reference graphs can be mutated engine-free.
6. `ThingOwner`/nested graph complexity and engine-hidden references mean direct XML node deletion is not an accepted production mutation strategy. Typed server operations may still require server-controlled RimWorld materialization/semantic application.
7. Projection aggregation may use fungible quantity keys without per-stack EntityId, but actual material application/cross-boundary transfer still needs an identity/rebinding strategy consistent with ADR-003.
8. A staged Tactical result is non-canonical. It does not own canonical custody merely because the blob exists. Pre-commit custody remains with the prior canonical owner until ADR-004 COMMITTED.
9. "Option C = zero tax evasion" is an overclaim; excluded/ambiguous asset classes and policy exemptions can still exist.
10. The brief's "minimum safe choice" is not adopted as policy. In particular, an Option-B-like economic inventory cannot by itself satisfy tax collection against Pawn/Animal/Slave categories; a broader TaxSeizableAssetSet may need engine-backed seizure.

G-Q8 status:
**OPEN — RUNTIME PROOF + PRODUCT BOUNDARY DECISION REQUIRED**

Current A sequencing unchanged:
- Remote Presentation Hardening-04 REV1 first;
- focused Sol E2;
- Production `PIPELINE_PROBE_CAS` next if presentation gate permits;
- G-Q8 runtime evidence is needed before first inventory-dependent Settlement mutation, not before the probe.

C is assigned a new task to identify the best first real **non-inventory** Settlement mutation candidate after the pipeline probe.


## 49. MSR-038 Delta — Remote Presentation Hardening-04 REV1 Developer Candidate

Source:
`Remote_Tactical_Presentation_Hardening_04_REV1.md`

Frozen candidate:
- DLL SHA256 `55182E92E1E077181B3B944E4EA450F7623E47BCD45084E4FEB0ECD22BD34E3E`
- Fixture SHA256 `ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED`
- Production `WarEconomyMod/` reported unchanged by A

Master assessment:
**E1 CANDIDATE FROZEN / INDEPENDENT E2 REQUIRED**
**A's self-classification `ASYNC INTERACTIVE PRESENTATION PASS` is not yet adopted.**

A claims:
- interactive Draft/Move command socket I/O moved off Unity main thread;
- bounded command/result queues and command timeouts;
- transport-epoch fencing across reconnect;
- dynamic authoritative pose/facing generated by Worker;
- listener/profile argument syntax and runtime binds corrected;
- prior render/control/fencing behavior preserved.

Material evidence gaps / inconsistencies requiring E2:
1. The REV1 Work Order required actual north/south movement and at least one real direction change. A's report provides actual west/east movement but only a scripted North/South wire round-trip; no real north/south Goto or direction-change evidence is shown.
2. Several tests are labeled `REAL_GRAPHICAL_OBSERVATION` while their key observation cites direct native calls such as `Find.Selector.Select()` / `TryTakeOrderedJob`. These cannot substitute for actual OS/user input.
3. `screen_05_destination_reached.png` and `screen_06_foreign_pawn_rejected.png` have the same reported byte size and identical SHA256, so they cannot be accepted as two independent visual states.
4. The report claims a 2-second delayed Draft eventually applies successfully while also reporting an 800 ms command receive timeout. The per-test timeout configuration/state transition is not explained and must be independently resolved.
5. Dynamic pose code prioritizes `pather.Moving` before `Stance_Busy` aiming. This may be correct for the tested case, but moving+aim/focus semantics are not independently demonstrated and must not be inferred from stationary tests.
6. A's `QA-PRESENT-011 CLOSED` claim is developer-only. Official status remains OPEN pending E2 actual movement/pose verification.
7. A's `QA-PRESENT-007` and `QA-PRESENT-009` closure claims are not adopted pending E2 fault/profile verification.
8. Queue caps must be proven under load; a bounded design claim is not sufficient without overflow/high-water behavior.

Official defect statuses remain unchanged from QDL-034 until Sol verification:
- QA-PRESENT-004 — PARTIAL
- QA-PRESENT-006 — CLOSED
- QA-PRESENT-007 — STILL FAILING
- QA-PRESENT-008 — PARTIAL
- QA-PRESENT-009 — PARTIAL
- QA-PRESENT-011 — OPEN

Next:
- Sol assigned `WP-QA-REMOTE-PRESENTATION-HARDEN-05`.
- A must not modify/rebuild the frozen presentation candidate while Sol verifies it.
- queued Production `WP-PROD-TRANSACTION-PIPELINE-01` remains not started until Master reviews the E2 result.
- C continues `WP-FIRST-REAL-SETTLEMENT-MUTATION-CANDIDATE-01`.


## 50. MSR-039 Delta — First Real Settlement/Domain Mutation Candidate Selected

Source:
`First_Real_Settlement_Mutation_Candidate_01.md`

Master disposition:
**RECOMMENDED NEXT REAL DOMAIN MUTATION ACCEPTED WITH CORRECTIONS**
**NO IMPLEMENTATION AUTHORIZATION YET**

Selected next real mutation after `PIPELINE_PROBE_CAS`:
**Auto-Shop Trade Configuration Update (Setup Phase)**

Controlling scope:
- persistent per-Settlement Auto-Shop order/config metadata;
- Buy/Sell order declaration only;
- no inventory reservation;
- no Silver reservation;
- no actual trade execution;
- no Settlement material artifact mutation;
- no `CommittedSettlementStateRevision` advance;
- no G-Q8 inventory lookup;
- no G-Q9 conquest integration.

Canonical requirement focus:
- FR-197 Settlement-specific Auto Shop configuration;
- FR-198 Sell Order;
- FR-199 Buy Order;
- FR-201 freely configurable trade price;
- BR-019 no system min/max trade-price clamp;
- FR-202 Sell/Auto-Shop registration does not reserve stock;
- FR-203 Buy Order registration does not reserve Silver.

FR-200 Vanilla-like Item Filter / trade UX is a later UI acceptance concern and is not part of the first backend transaction slice.

Master corrections:
1. C's recommendation is accepted as the **best current next real domain mutation**, not as the only theoretically safe candidate.
2. C's elimination analysis overstates blockers:
   - basic Caravan custody ingress/egress is not categorically blocked by G-Q1/G-Q12a/b;
   - generic Occupy/Destroy is not categorically blocked by TBD-01/TBD-02.
   These earlier Master dependency corrections remain controlling.
3. Use a dedicated canonical `TradeConfigurationRevision` (or equivalently named AutoShopConfig aggregate revision), not `CommittedSettlementStateRevision` and not an ambiguous catch-all `SettlementMetadataRevision`.
4. Every mutation binds expected Settlement ownership identity/epoch and re-authorizes at commit. This prevents a former owner from committing a stale order update across an Occupy/ownership race without deciding G-Q9.
5. G-Q9 remains open: this slice does not decide whether existing orders persist/reset/suspend when ownership changes.
6. G-Q8 remains open: FR-204+ actual available quantity, FR-205 actual Silver, FR-206+ execution, and inventory effects are outside this slice.
7. Content-profile validation applies to referenced gameplay definitions/selectors. The backend must not silently lock future FR-200 UI semantics to an unnecessarily narrow DTO solely for this slice.
8. No arbitrary economic price min/max may be introduced contrary to FR-201/BR-019. Structural serialization/overflow validation is still allowed.
9. Outbox/UI notification may be implemented as derived delivery, but full final Auto-Shop UI is not required by this backend slice.

Sequencing:
- A: frozen Remote Presentation REV1 candidate under Sol Hardening-05 E2.
- After Master reviews Sol: A begins `WP-PROD-TRANSACTION-PIPELINE-01`.
- Only after Pipeline Slice-01 achieves the required E2 gate may the queued Trade Configuration Production slice begin.
- C proceeds to G-Q1 ordinary multi-settlement topology decision brief.

Remote Tactical Production remains NOT AUTHORIZED.


## 51. MSR-040 Delta — G-Q1 Ordinary Multi-Settlement Topology Brief Review

Source:
`GQ1_Ordinary_MultiSettlement_Topology_Decision_Brief_01.md`

Master disposition:
**DECISION BRIEF ACCEPTED AS ANALYSIS INPUT / G-Q1 REMAINS OPEN**
**Classification: RUNTIME PROOF FIRST / DEFER BEHIND LEASE-MATERIALIZATION INTERFACES**

Accepted findings:
- Canonical SRS permits multiple Settlement ownership, but does not require multiple divergent LocalClock settlements to simulate concurrently inside one client process.
- ADR-006A one-active-LocalClock-per-execution-island remains controlling.
- ADR-007 per-Settlement WriterLease/Fencing boundary is the correct stable deferral interface.
- `PIPELINE_PROBE_CAS` and TradeConfiguration domain mutation do not require G-Q1 resolution.

Master corrections:
1. Candidate 1 `Single Active Materialization` does not have proven "absolute isolation". Sequential materialization may still leak global singleton/cache state. This is an engine-proof obligation.
2. Candidate 4 `Hybrid Lazy Materialization` is not yet "high feasibility" or "seamless". It is a promising architecture direction only after sequential unload/rematerialize, server-authored offline delta, and Tactical handoff are proven.
3. G-Q1 is not a pure product-policy question. It combines:
   - product UX choice;
   - RimWorld 1.6 engine/process feasibility;
   - temporal isolation;
   - lease/materialization recovery architecture.
4. Candidate 3 `Server-Hosted Ordinary Workers` is inconsistent with the currently accepted owner-client ordinary-writer architecture and prior SRS interpretation, but should be classified as an architecture fallback requiring explicit ADR/SRS-direction change rather than dismissed only by prose.
5. Multiple Local Islands must distinguish operator/server-hosted processes from user-owned local processes; G-Q2 trust differs materially between them.
6. A 1:1 `SettlementId -> active WriterLeaseId` registry does not mean one client may safely hold arbitrarily many active leases. Admission policy remains G-Q1 and runtime-evidence dependent.
7. Tactical admission for an inactive settlement must use the last committed canonical head and server-controlled materialization; it must not depend on waking the owner's inactive local artifact.
8. Cross-island caravan custody is not required to decide the ordinary topology itself; it is useful integration evidence but should not be the first G-Q1 probe.

Current G-Q1 status:
**OPEN — ENGINE/PROCESS FEASIBILITY EVIDENCE REQUIRED BEFORE CLIENT-INTEGRATION TOPOLOGY FREEZE**

Preferred first proof sequence:
A. sequentially materialize two settlement artifacts with intentionally divergent LocalClockIds in one client/runtime, with hard unload between them;
B. prove no foreign clock/global singleton/cache contamination;
C. prove lease revoke/fence and re-materialization on switch/crash;
D. only then compare separate-process simultaneous islands.

No topology is selected by this review.

Current program sequencing unchanged:
- Sol: Remote Presentation Hardening-05 E2
- A: frozen presentation candidate, then `WP-PROD-TRANSACTION-PIPELINE-01`
- after pipeline gate: queued TradeConfiguration Production slice
- G-Q1 runtime probe is queued before ordinary multi-settlement Client Integration, not on the current transaction critical path
- C proceeds to G-Q2 ordinary-client trust decision brief


## 52. MSR-041 Delta — Remote Presentation Hardening-05 E2 and Production Pipeline Release

Source:
`QA_Remote_Tactical_Presentation_Hardening_05.md`

Master verdict:
**PARTIAL / REMAINING BLOCKER — ADOPTED**

### E2 now independently proven
- actual OS/user selection, native Draft, terrain right-click, native Go here;
- GUI adapters enqueue asynchronously with no speculative local Draft/Goto authority;
- Worker authorization and actual engine execution;
- repeated autonomous replication and rendered movement;
- moved-Pawn hit target / selection;
- foreign Pawn rejection through actual GUI interaction;
- actual west/east/north/south movement plus direction change;
- semantic facing/pose in the tested movement/focus slice;
- gameplay/control-port separation;
- frozen listener/profile bind correctness.

### Defect status changes
- QA-PRESENT-004 — **STILL FAILING overall**
  - narrow rendered Position/DrawPos/hit-target sub-scope remains resolved;
  - general health/body-part/job reconciliation remains unresolved.
- QA-PRESENT-007 — **PARTIAL**
  - ordinary GUI command socket I/O / receive path is now E2-proven off-main and responsive in the tested fault window;
  - remaining transport lifecycle blockers:
    - H05-01 HIGH: response parsed from an old connection can be relabeled with the current TransportEpoch before coalescing and then applied after reconnect;
    - H05-02 MEDIUM: `_cmdResultQueue` is not actually bounded/backpressured;
    - H05-03 MEDIUM: initial/external reconnect still performs synchronous `TcpClient.Connect` on the main thread and has no explicit bounded connect deadline.
- QA-PRESENT-008 — **STILL FAILING**
  - A evidence manifest contains duplicated screenshot evidence and several metric/source/evidence-classification inaccuracies.
- QA-PRESENT-009 — **CLOSED for the narrow listener/profile subdefect**
  - declared `-flag=value` ports are consumed;
  - candidate-related bind collisions were not observed;
  - this does not close QA-ENGINE-002/headless semantic-load concerns.
- QA-PRESENT-011 — **CLOSED for the tested movement/focus pose slice**
  - actual four-direction movement, direction changes, 93 matched pose samples and moving+focus behavior independently verified.
- QA-PRESENT-001/002/003/005/006/010 remain CLOSED.

### Important corrections adopted
- A's report description of a movement-first `DetermineAuthoritativeFacing()` does not match the frozen source. Actual frozen source is focus-first, consistent with the tested engine behavior.
- A's claimed 800 ms general command timeout is incorrect. Native adapter tests used a 4000 ms timeout; the 800 ms case was an explicitly configured test.
- A's reported 280-byte interactive payload is not representative of actual GUI replies; independent GUI replies carried full ~22.6 KB Pawn-set snapshots.
- two A screenshot files advertised as independent evidence are byte-identical.
- endpoint ownership labels in A's report require correction.

### Architecture status
- P2 presentation actual async Draft/Move interaction is E2-feasible.
- Candidate C / ADR-002 remains **PROVISIONALLY ACCEPTED**.
- Remote Tactical Production remains **NOT AUTHORIZED**.
- presentation transport lifecycle still requires a narrow repair and focused reverify before the narrow P2 gate can be fully closed.

### Program sequencing decision
The remaining presentation blockers are now isolated to the Remote Tactical presentation transport/evidence scope and no longer justify serially blocking the independent Shared Settlement transaction substrate.

Therefore:
**`WP-PROD-TRANSACTION-PIPELINE-01` = AUTHORIZED TO START NOW.**

A must:
- leave the frozen Remote Presentation candidate untouched;
- implement the Production transaction probe only in the authorized `WarEconomyMod/` scope;
- freeze/report that candidate before returning to presentation transport repair.

Remote presentation transport repair is queued after the pipeline candidate is frozen.

C continues `WP-GQ2-ORDINARY-TRUST-BRIEF-01`.

Remote Tactical Production remains blocked regardless of the Production transaction slice.


## 53. MSR-042 Delta — G-Q2 Ordinary Client Trust Brief Review

Source:
`GQ2_Ordinary_Client_Trust_Decision_Brief_01.md`

Master disposition:
**DECISION BRIEF ACCEPTED WITH CORRECTIONS / G-Q2 REMAINS OPEN**

Accepted:
- owner-client checkpoint/materialization remains hostile/untrusted input despite authenticated WriterLease;
- structural/semantic engine validity does not establish legitimate provenance;
- identity/lease/fencing, revision lineage, profile/schema compatibility, EntityId/custody integrity are mandatory invariants, not optional anti-cheat policy;
- G-Q2 does not block `PIPELINE_PROBE_CAS` or server-authored TradeConfiguration metadata mutation;
- G-Q2 must be resolved before hostile ordinary-client material publication is Production-approved.

Master corrections:
1. `ContentProfileFingerprint` proves the artifact uses an admitted content universe/version/load order; it does NOT prove that an admitted cheap ThingDef was not maliciously replaced with another admitted expensive ThingDef. Same-profile semantic substitution remains a provenance/plausibility problem.
2. `CheckpointParentRevision` rejects stale lineage but does NOT detect arbitrary offline edits made on top of the current valid parent revision. Current-parent forged state remains the central G-Q2 vulnerability.
3. `EntityId` duplication must fail closed with explicit validation/quarantine; a validator crash is not acceptable evidence of correct rejection.
4. Structural + semantic validation is compatible with ADR-007 mechanically, but does NOT turn the lease holder into a trusted domain actor. WriterLease is authority to write a scoped materialization candidate, not proof of truth.
5. Posture 5 server-hosted ordinary simulation does not have literally zero cheat surface or false-positive risk. It removes owner save-state forgery authority, but command exploits, bugs, mod exploits, authorization flaws and server compromise remain possible.
6. Posture 4 does not require full G-Q1 resolution merely to define a sensitive-transition handoff; it depends on accepted handoff/materialization interfaces and runtime feasibility. Full ordinary topology may remain deferred.
7. Partial deterministic replay of arbitrary mining/harvesting is not the first evidence priority. First prove whether selected server-authored/high-value typed operations can be reconciled against client checkpoints; broad RimWorld deterministic replay is likely disproportionate and must not become an implicit architecture requirement.
8. Wealth/tier trust must be separated:
   - client-reported wealth is not automatically authoritative political input;
   - if Faction Tier promotion depends on wealth, the server must derive/validate the promotion input from an accepted canonical projection or separately protected evidence path.
9. Ban/kick is administration/response, not an integrity mechanism. It cannot substitute for mandatory canonical validation.
10. G-Q2 policy should be framed per mutation/domain sensitivity rather than one global posture for all checkpoint fields.

Controlling direction:
**Layered Trust, not one global Posture.**
- Layer A: mandatory hard invariants.
- Layer B: server-authored typed operations / protected domain state where feasible.
- Layer C: semantic validation of engine materialization.
- Layer D: selective plausibility/provenance controls for high-impact client-authored state.
- Layer E: audit/admin response.

No final thresholds or anomaly policy selected.

C next:
prepare G-Q6 checkpoint-loss/disconnect-grace decision brief, because it directly interacts with ADR-007 writer lease lifecycle but can remain behind configurable policy.


## 54. MSR-043 Delta — Production Midpoint Architecture Checkpoint

Trigger:
A submitted `Production_Transaction_Pipeline_Slice_01.md` with developer classification:
**E1 PIPELINE PROBE PASS**

Master disposition:
**E1 DEVELOPER EVIDENCE ACCEPTED / PRODUCTION CANDIDATE FROZEN / E2 REQUIRED**

This is the first implemented Production persistence/transaction substrate in `WarEconomyMod/`.

Reported candidate:
- internal operation `PIPELINE_PROBE_CAS`
- SQLite-backed operation journal / PREPARED / COMMITTED / PUBLISHED lifecycle
- ProbeRevision CAS
- commit receipt
- audit
- durable outbox
- recovery reconciler
- hard-process crash evidence
- gameplay transport isolation
- no Settlement material mutation
- no `CommittedSettlementStateRevision` increment
- no `ArtifactBaseStateRevision` mutation
- no EntityId transfer
- no Tax/Trade/Auto-Shop execution/Tactical integration.

Master checkpoint:
**Do not start the queued first real gameplay mutation yet.**

Before `WP-PROD-TRADE-CONFIG-01` can be released:
1. Sol must independently attack/verify the Pipeline Slice-01 candidate (E2).
2. A high-level independent architecture red-team review will be requested from the user-selected external reviewer.
3. Master will reconcile both reviews into a midpoint plan/gate.

Specific E2 concerns from report inspection:
- verify the idempotency/collision fingerprint includes every semantically material request field, not only `PayloadJson`; `ProbeScopeId`, expected revision, actor/principal, operation type, content/profile binding must not be silently ignored when an OperationId is reused;
- verify exact SQLite `synchronous` policy used for canonical commit; `NORMAL` vs `FULL` must not be ambiguous;
- attack hard-process kill immediately around the real commit boundary, not only cooperative/in-process fault injection;
- verify PREPARED forward recovery uses a complete durable request package and cannot adopt a partial/tampered reservation;
- verify multi-process/multi-connection CAS and SQLite busy behavior, not only in-process task concurrency;
- verify outbox at-least-once semantics when the external side effect succeeds but the delivered marker crashes before persistence; duplicate delivery must be harmless/deduped at the consumer boundary;
- verify audit/receipt/outbox uniqueness and operation state transitions under restart/retry;
- inspect gameplay isolation in actual dispatch/source, not only the test surface;
- confirm Production startup/recovery ordering and migration failure behavior.

Program status during checkpoint:
- A: pipeline candidate frozen; no TradeConfig implementation yet.
- Sol: assigned Pipeline independent E2.
- C: G-Q6 brief continues.
- Remote Presentation transport repair remains queued.
- TradeConfiguration Production slice remains selected/queued, NOT authorized.
- Remote Tactical Production remains NOT authorized.


## 55. MSR-044 Delta — MPC-002 Midpoint Gate Result

Inputs:
- `QA_Production_Transaction_Pipeline_01.md` — GPT-6.1 Sol independent E2
- `Architecture midpoint red-team.md` — external independent architecture review

### Master Gate

**MPC-002 = HOLD — ARCHITECTURE REVISION REQUIRED**

This is a targeted foundation hold, not a project reset.

Validated reusable core:
- one SQLite transaction can atomically commit ProbeRevision CAS + history + operation decision + receipt + commit audit + publication record;
- independent 25-process, different-OperationId CAS produced exactly one winner and deterministic stale losers;
- real dispatcher isolation for the internal probe was independently confirmed;
- hard process kills around the local SQLite commit boundary preserved the tested local atomic subset.

E2 failure:
Sol independently reproduced foundation defects in operation identity, PREPARED recovery integrity, live/recovery concurrency, publication delivery semantics, startup/recovery admission, logical schema validation, durability policy, exact-retry concurrency, storage-error typing and receipt canonicalization.

Official new defects:
QA-PIPELINE-001..012 OPEN.

### Production sequencing

`WP-PROD-TRADE-CONFIG-01` remains valid as a future Settlement metadata slice but is **RE-SEQUENCED / NOT AUTHORIZED**.

New order:
1. P1-R — Correct and simplify Production Transaction Pipeline; independent E2 required.
2. P2 — ADR-001 Production Foundation: authentication/session/epoch/profile admission/durable W/startup readiness.
3. P3 — Core canonical registries: Player/personal Faction/admin fencing; then Settlement metadata registry.
4. P4 — TradeConfiguration setup mutation with real owner/ownership-epoch fencing.
5. No Settlement material-state Production mutation until Engine Host round-trip/barrier evidence gates are satisfied.

Engine evidence track:
- E-A Settlement Artifact Round-Trip / census / materialization-context PoC becomes the next critical engine proof.
- E-B live-client barrier cost + in-engine server delta is required before online material mutation.
- E-C WAN P2 remains required before Remote Tactical/G-Q10 release, but is NOT a blocker for unrelated server metadata Production.

### Controlling architecture corrections

1. Canonical SQLite connections use WAL + synchronous=FULL and startup asserts the effective setting.
2. Operation identity becomes `(PrincipalId, OperationId)` plus a server-computed canonical typed-envelope fingerprint. Caller hashes are not authoritative. ABORTED is terminal for that key/fingerprint.
3. `FencingGeneration` advances on lease revocation/holder/incarnation change, not on every server-authored commit. A continuing lease instead advances its required base revision/applied-operation watermark.
4. Lease/barrier interface is execution-island/LocalClock-domain scoped with a set of Settlement scopes; this keeps G-Q1 open. Finer per-Settlement barrier isolation requires runtime proof.
5. Introduce `StoreIncarnationId`; restore/rollback rotates it. Tokens/receipts/leases must bind the incarnation once those types exist.
6. Split ADR-004 execution:
   - single-scope typed fast path: one atomic commit transaction, no PREPARED reservation;
   - staged/multi-scope/multi-party path: explicit durable ScopeReservations + PREPARED, separately implemented/tested.
   Autonomous PREPARED completion is allowlisted and must revalidate a complete immutable durable package and current authority.
7. One shared **Engine Host** implementation boundary owns RimWorld materialization loader, profile binding, census/semantic validation and engine-backed modes. QA-ENGINE-002/006 are now shared Engine Host blockers, not merely Tactical defects.
8. Publication is not operation state. Canonical decision ends at COMMITTED/ABORTED; derived delivery uses append-only events with stable event identity and per-consumer durable acknowledgement/dedup.
9. Player-global engine state requires a canonical ownership/home segment before materialization Production; exact field schema remains analysis/runtime-informed.
10. Settlement genesis requires an explicit authority contract before first real artifact Production.
11. Economic/political state derived from owner-authored material requires an explicit validation/firewall control point before Tier automation or trade execution.
12. Engine-free typed material operations must satisfy an application-totality invariant before commit.

### Evidence allocation

Freeze further presentation-fidelity expansion.
The existing Remote transport lifecycle repair remains queued, but no additional P2 fidelity work is authorized until the foundation/Engine Host critical path advances.

C continues G-Q6.
A receives P1-R correction work.
Sol re-verifies P1-R after freeze.


## 56. MSR-045 Delta — Pipeline REV1 E1 Freeze and Parallel Engine-Host Release

Source:
`Production_Transaction_Pipeline_Slice_01_REV1.md`

Master disposition:
**E1 PIPELINE REV1 PASS — DEVELOPER EVIDENCE ACCEPTED / E2 REQUIRED**

Exact reported frozen Production candidate:
- Release `WarEconomy.Server.dll` SHA256:
  `288AADC7C8B88A3492583797F2D4537F73EC88362723671E0222BF0AEDB3ED8C`
- Debug `WarEconomy.Server.dll` SHA256:
  `FE52E1C52D9B633DA6A062DC88D4300D627515DE07BD831B2C0090B74633BEB3`
- schema `user_version=2`
- application_id `0x57415245`
- reported E1: 19/19 PASS.

Accepted as E1 evidence:
- probe fast path no longer uses PREPARED;
- `(PrincipalId, OperationId)` identity and server-computed envelope fingerprint are reported implemented;
- one-transaction canonical decision fast path;
- Channel-fed single commit executor;
- operation decision separated from append-only publication stream;
- WAL/FULL and startup readiness gate;
- StoreIncarnationId;
- canonical epoch-millisecond receipt representation;
- typed storage busy/failure outcomes;
- no gameplay/material mutation in the slice.

Not accepted yet:
- A's statement that QA-PIPELINE-001..012 are "closed".
- Any Production gameplay mutation authorization.
- Any claim of independent exactly-once publication semantics.
- Any claim that Release/test-surface isolation is complete.

Reporting correction:
REV1's defect-ID mapping is inconsistent with QDL-041 for several items.
QDL-041 IDs remain authoritative until Sol independently re-verifies each original defect.

Additional E2 focus:
- prove process-level, not merely task-level, concurrency;
- hard-process crash after external semantic effect but before durable consumer ACK;
- verify Release assembly/build excludes or safely gates test/probe execution surfaces;
- verify schema constraints/indexes/application_id, not merely table/column presence;
- inspect Channel capacity/backpressure and shutdown/drain semantics;
- verify startup recovery/readiness behavior with transient/permanent consumer failure;
- verify ABORTED exact retry and collision semantics;
- verify StoreIncarnation rotation and stale identity behavior.

Parallel sequencing:
- Sol: Pipeline REV1 E2 now.
- A: because REV1 is frozen, scratch-only Engine Host Settlement Round-Trip PoC is now released in parallel.
- TradeConfiguration remains NOT AUTHORIZED.
- no material-state Production mutation.


## 57. MSR-046 Delta — G-Q6 Disconnect/Grace Brief Review

Source:
`GQ6_Checkpoint_Disconnect_Grace_Decision_Brief_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — G-Q6 REMAINS OPEN**

Accepted:
- clean disconnect, transient transport loss, process/machine crash, torn checkpoint upload, barrier interruption, committed-before-ACK, stale-old-process reconnect must be distinguished;
- committed server operations never roll back because the client disappears;
- replacement writer admission requires old authority to be fenced first;
- grace duration is a configurable/product choice informed by runtime evidence;
- G-Q6 does not block backend transaction infrastructure or server-authored metadata mutations;
- G-Q6 must be resolved before ordinary owner-client Production integration.

Controlling corrections after MPC-002 / MAC-001:

1. **Lease scope**
   The lease/barrier root is execution-island / LocalClock-domain scoped and carries a Settlement scope set.
   Do not describe the controlling lease as inherently per-Settlement.

2. **Transport reconnect vs session restart**
   Distinguish:
   - transport reconnect while the same authenticated SessionEpoch/lease remains in GRACE/SUSPENDED state;
   - full session restart/new SessionEpoch.
   A transport reconnect within an allowed grace does not automatically require a new FencingGeneration.
   A new SessionEpoch/holder/incarnation requires authority reissue/fencing of the old holder.

3. **Grace state**
   During transport loss, if grace exists, the Server marks the lease `SUSPENDED_GRACE`.
   While suspended:
   - no replacement writer may be admitted;
   - the Server may revoke/fence the suspended holder if a higher-priority handoff/domain operation requires authority;
   - if revoked during grace, later reconnect cannot resume the old lease and must rematerialize/reacquire.

4. **Client pause is not independently trustworthy**
   A well-behaved client must pause local simulation on detected authority loss, but the Server cannot treat client self-report of pause as proof against a hostile owner.
   Any acceptance of resumed client-authored material remains subject to G-Q2 trust policy and authority/revision/watermark validation.
   G-Q6 must not silently solve G-Q2.

5. **Unaccepted progress**
   A hard process crash destroys volatile uncheckpointed progress, but local-disk autosave/recovery may still exist.
   Such local recovery is not canonical merely because it exists; acceptance is separately governed by lineage/trust/materialization rules.

6. **Checkpoint upload**
   Torn/incomplete upload must never advance artifact watermark.
   Implementation may discard or quarantine resumable staging; exact upload-resume policy is not decided here.

7. **Barrier grace**
   Do not preselect zero grace for DELTA_BARRIER.
   Barrier behavior is an E-B runtime/product decision because island-wide pause cost, coalescing and griefing risk must be measured first.

8. **Server restart during grace**
   Do not hard-code `UNLEASED` as the only correct restart result.
   The implementation must either:
   - durably restore a still-valid suspended lease; or
   - explicitly invalidate/fence it before accepting a replacement.
   StoreIncarnationId does not rotate on ordinary restart.

9. **Replacement writer invariant**
   Timeout may trigger revocation, but timeout alone is not the fencing mechanism.
   The atomic sequence is:
   timeout/policy trigger -> revoke/fence old authority -> advance authority generation if required -> grant replacement.

10. **Evidence dependency**
   G-Q6 final choice waits on Engine E-B live barrier/disconnect measurements and ordinary lease-state-machine probes.

Current execution:
- A: Engine Host Settlement Round-Trip PoC IN PROGRESS (user confirmed).
- Sol: Pipeline REV1 independent E2 IN PROGRESS (user confirmed).
- C: G-Q6 brief COMPLETE; next analysis assignment prepared below.


## 58. MSR-047 Delta — Player-Global State Boundary Review

Source:
`Player_Global_State_Boundary_Decision_Brief_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — BOUNDARY MODEL ADOPTED, EXACT FIELD SCHEMA OPEN**

### Adopted ownership taxonomy

The following categories are now the controlling conceptual split:

1. `MapSegment(SettlementId)`
   - map-local physical/material engine state;
   - canonical custody on Dedicated Server;
   - simulated only by an authorized execution island.

2. `PlayerGlobalStateSegment(PlayerId)`
   - engine-global/player-global state that must survive across multiple Settlement materializations;
   - has independent `PlayerGlobalRevision`;
   - composed into Engine Host materialization without rewriting frozen MapSegments.

3. `FactionDomainState(FactionId)`
   - server-domain authoritative political state;
   - Titles/Tier/War/Alliance/Betrayer and equivalent domain truth;
   - Engine Host receives only a projection.

4. `SharedWorldProjection`
   - server-authoritative cross-map/world context required for simulation/visibility/custody.

5. Engine-ephemeral/reconstructible context
   - not canonical merely because Vanilla serializes it;
   - exact membership must be proven by E-A.

### Corrections

1. **Stable ownership key**
   `PlayerGlobalStateSegment` is keyed by stable `PlayerId`, not by `PersonalFactionId`.
   Personal factions may dissolve/re-form during join/expulsion/split and are therefore references/lifecycle inputs, not the durable identity of player-global state.

2. **No direct client-global overwrite**
   The phrase "written by the active settlement's client" is too broad.
   Dedicated Server owns canonical `PlayerGlobalRevision`.
   An authorized Engine Host / owner execution island may submit allowed player-global mutations, but the Server serializes/validates the canonical commit.
   No last-writer-wins whole-segment overwrite.

3. **Concurrent island rule**
   Multiple execution islands must not concurrently mutate the same player-global revision without explicit server arbitration.
   The final mechanism may be typed global operations, a global write lease, or another validated primitive; exact mechanism remains open until E-A/G-Q1 evidence.
   The stable requirement is one canonical ordered revision history.

4. **Clock-domain rule**
   `PlayerGlobalRevision` is not a Settlement LocalClock.
   A frozen MapSegment may observe a newer player-global state when next materialized without advancing its `LocalClockId`.
   Any time-bearing global field must explicitly identify its clock domain; raw `TicksGame` values must not be merged blindly across divergent LocalClocks.

5. **Materialization binding**
   Each Engine Host materialization must record the exact composed context revisions used, including at minimum:
   - Map/Artifact revision;
   - PlayerGlobalRevision if present;
   - relevant SharedWorldProjection revision;
   - FactionDomain projection revision/config snapshot where applicable.
   This belongs in/alongside the MaterializationManifest rather than inside the frozen MapSegment.

6. **No automatic Map artifact rewrite**
   Player-global changes do not rewrite offline settlement artifacts.
   Composition/rebase occurs at materialization/admission with explicit revision binding and validation.

7. **WorldPawns classification remains evidence-first**
   C's suggestion that most local WorldPawns are discardable is not adopted as a blanket rule.
   Pawns participating in relationships, custody, caravans, quests, royalty or other cross-boundary references may require PlayerGlobal/SharedWorld representation.
   E-A must discover the minimum reference closure.

8. **Quest classification remains open**
   "active quests = SharedWorldProjection" is too broad.
   Quest/domain/engine ownership must be classified by actual authority, temporal semantics and references.
   No global quest schema is frozen now.

9. **Research/Ideology**
   Strong candidates for player-global engine context, but exact ownership/mutation and join/expulsion/split inheritance remain product decisions.
   Architecture only freezes that such state cannot be duplicated independently inside every MapSegment if Vanilla/global semantics are to be preserved.

10. **Domain projection remains read-only**
    Engine mutation may produce facts/intents, but political/domain truth remains Dedicated-Server authoritative.

### E-A consequences

A/Sol Engine Host Round-Trip evidence must record:
- global manager/reference dependencies;
- exact context needed for Research/Ideology;
- cross-map WorldPawn closure;
- Faction reference rebinding behavior;
- time-bearing global fields and their clock source;
- whether two maps can compose the same player-global context safely;
- what engine-global components can be safely reconstructed rather than persisted.

### Freeze status

The **conceptual boundary** is frozen enough for E-A and future design.
The **exact physical schema/field membership** is NOT frozen.

Final schema freeze is required before:
- Settlement Genesis Production;
- final MaterializationManifest builder;
- any Production artifact fold that depends on player-global composition.


## 59. MSR-048 Delta — Pipeline REV1 E2 FAIL + Engine Host E-A E1 Result

Sources:
- `QA_Production_Transaction_Pipeline_01_REV1.md`
- `POC_EngineHost_Settlement_RoundTrip_01.md`

### A. Pipeline REV1

Master verdict:
**E2 FAIL — ADOPTED**

Exact independently verified Release DLL:
`288AADC7C8B88A3492583797F2D4537F73EC88362723671E0222BF0AEDB3ED8C`

Confirmed improvements:
- independent 25-process different-ID race: 1 SUCCESS / 24 STALE;
- independent 12-process same-ID race: 1 SUCCESS / 11 ALREADY_COMMITTED;
- local SQLite decision transaction atomic subset;
- fast-path PREPARED removed;
- WAL/FULL connection policy effective;
- canonical receipt epoch/hash fixed;
- actual network probe route remains unavailable.

Original QA-PIPELINE disposition adopted:
- 001 STILL FAILING
- 002 CLOSED — narrow fast-path only
- 003 PARTIAL
- 004 STILL FAILING
- 005 PARTIAL
- 006 PARTIAL
- 007 STILL FAILING
- 008 STILL FAILING
- 009 CLOSED — durability configuration contract
- 010 CLOSED
- 011 STILL FAILING
- 012 CLOSED

New defects adopted:
- QA-PIPELINE-013 HIGH — unbounded admission / shutdown abandons accepted requests
- QA-PIPELINE-014 HIGH — publication cursor can jump over an unaccepted event
- QA-PIPELINE-015 CRITICAL — v1 migration destroys durable probe history and can commit destructive migration before validation
- QA-PIPELINE-016 HIGH — StoreIncarnation validation/rotation TOCTOU
- QA-PIPELINE-017 HIGH — mutable request object may change actor/target/payload after admission
- QA-PIPELINE-018 MEDIUM — dangerous local test/fault controls ship in ordinary Release binary

MPC-002 remains HOLD.

### Pipeline simplification decision

REV2 narrows the Production transaction foundation.

Foundation P1 responsibility:
- immutable admitted command;
- server-computed canonical operation identity;
- single local canonical decision transaction;
- immutable receipt/audit;
- append-only ordered `PublicationEvents` record;
- durable schema/incarnation/startup readiness.

Foundation P1 will **not** execute generic external consumers, maintain generic ACK/cursors, or claim exactly-once semantic delivery.

Rationale:
Exactly-once external effect is consumer-specific. The REV1 `DurableTestConsumer` proved only in-memory dedup and failed across process restart. A generic callback cannot prove an external consumer's atomic idempotency contract.

Future consumer slices must define:
- stable EventId/idempotency key;
- recomputed payload fingerprint;
- consumer-side durable acceptance/effect transaction or equivalent idempotency query/receipt;
- ordered stream gap policy;
- mandatory-consumer readiness policy.

Until such a consumer exists, P1 proves durable event availability/order, not delivery completion.

### B. Engine Host E-A

Master verdict:
**STRONG E1 SUPPORT FOR B2-LITE ROUND-TRIP CORE / INDEPENDENT E2 REQUIRED**

Developer evidence accepted:
- target Settlement round-trip through target-only Engine Host context;
- zero reported custody census mismatch across load/export/reload/tick/re-export;
- complex custody fixture includes pawns/health/equipment/apparel/inventory/animal/buildings/power/nested holders/corpse/zones/designations;
- dual in-engine + static XML census concept;
- 6 deliberate corruption cases reported fail-closed;
- target-only Context B startup succeeded with required faction/map-parent/world-grid/tick context;
- Production `WarEconomyMod/` remained untouched;
- inactive map scoped simulation remained frozen for tested pawn/need/plant state;
- process-global `TicksGame/TicksAbs` contamination was explicitly rediscovered.

Not yet accepted:
- "complete B2-lite Production feasibility";
- exact PlayerGlobalStateSegment membership;
- Research/Ideology/WorldPawn/Quest/Royalty reference closure;
- full G-Q1 topology;
- LocalClock virtualization;
- material-state Production;
- Genesis Production;
- generic claim of 100% all RimWorld/mod semantic graph fidelity.

Critical E2 additions:
- fresh-process cross-process round-trip, not only repeated loads in one Engine process;
- silent-corruption cases that still reach engine READY but census must reject;
- dynamic/environmental state census including filth/fire/conditions/plants where applicable;
- actual job/reservation/load-time reference behavior;
- player-global dependency closure;
- validate target-only context is not silently relying on retained process caches/global objects.

### Current parallel execution plan

- A: Pipeline REV2 correction/simplification.
- Sol: Engine Host Settlement Round-Trip independent E2.
- C: Settlement Genesis brief delivery remains unconfirmed unless user already sent it.
- TradeConfiguration remains NOT AUTHORIZED.
- Material-state Production remains blocked.


## 60. MSR-049 Delta — Settlement Genesis Authority Brief Review

Source:
`Settlement_Genesis_Authority_Decision_Brief_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — GENESIS AUTHORITY MODEL REMAINS OPEN**

Accepted:
- first canonical Settlement has no ordinary checkpoint parent and requires an explicit server-authorized genesis operation;
- first-player genesis, additional-settlement founding, and faction lifecycle changes must be treated as distinct cases;
- ContentProfile binding, idempotency, audit, stable identity/custody, separate Map/PlayerGlobal revisions, and server-domain authority are mandatory;
- additional Settlement founding must reuse existing caravan custody for transferred colonists/items;
- exact Genesis trust model must freeze before Genesis Production.

Corrections:

1. **Server Engine Host is operator-trusted, not “absolute trust”.**
   Model A removes owner-client save forgery authority but still requires profile binding, scenario/input validation, census/export gating, crash recovery and audit.

2. **Client artifacts are never repaired by silent stripping/clamping.**
   Model B/C candidate artifacts are staged hostile input.
   Invalid or unverifiable starting material is rejected/quarantined or regenerated through a trusted path.
   Do not mutate a hostile candidate into an apparently canonical artifact by ad-hoc deletion/clamping.

3. **Terrain/layout is economically significant.**
   Mountains, mineables/resources, fertile soil, geothermal access, ancient structures, biome/map features and other generated environment can materially affect starting/economic value.
   Do not classify arbitrary client-generated terrain as economically safe merely because pawn/item totals match.

4. **Additional Settlement founding is not only custody transfer.**
   Caravan settlers/items already have canonical custody and must transfer through ADR-008.
   The new Map/environment itself is a new generated material artifact and requires its own authorized generation/admission contract.

5. **Genesis is not forced into current P1 PREPARED semantics.**
   There is no `CheckpointParentRevision`, but the replacement contract is:
   - unique `GenesisOperationId` / idempotency identity;
   - expected absence/nonexistence of the target Settlement genesis record;
   - authorized scenario/founding specification;
   - staged artifact/census/profile bindings;
   - terminal GenesisReceipt.
   Whether a future Genesis operation uses the ADR-004 reservation/PREPARED path is implementation evidence-dependent and must not be inherited from the current fast-path probe.

6. **Stable EntityIds must exist before canonical admission completes.**
   Native RimWorld loadIDs are not the canonical identity source.
   For Engine-Host generation, identities can be assigned/bound during trusted staged generation.
   For client-generated candidates, the candidate remains noncanonical until validated entities are deterministically rebound/mapped to server-issued stable identity and the accepted artifact/manifest reflects those bindings.
   “Accept first, then parse and mint” is not allowed.

7. **PlayerGlobal initialization is a separate canonical segment with coordinated genesis.**
   Initial `PlayerGlobalRevision` and Map/Artifact revision are separate.
   Genesis may atomically authorize the composition, but it must not collapse both into one revision/blob.

8. **Fraud prevention covers all gameplay-significant generated state.**
   Not only starting Pawn count/skills/inventory:
   traits, genes/xenotype, hediffs, apparel/equipment quality, animals, resources, map features and other approved-scenario outputs must either be generated by a trusted Engine Host or validated against a complete admissible contract.
   Wealth alone is not a sufficient oracle.

9. **Expulsion/branch split are not ordinary map genesis, but reference rebinding remains required.**
   Existing MapSegments should not be regenerated merely for faction lifecycle.
   However stale Faction references may require projection/rebind/migration at materialization; C's statement that physical artifacts simply remain intact is a desired direction, not yet a universal runtime proof.

10. **Deterministic generation is not mandatory unless the chosen model depends on it.**
    Same seed producing byte-identical artifacts is not an architecture requirement.
    A server-controlled Engine Host may generate a nondeterministic but server-approved artifact and commit its resulting manifest/receipt.
    Model C requires stronger reproducibility/validation evidence and therefore has a higher burden.

### Evidence priority

Before choosing A/B/C/E:
1. E-A independent Engine Host E2;
2. controlled Engine Host Vanilla scenario/new-settlement generation proof;
3. genesis crash/idempotency/staged-admission proof;
4. hostile client candidate tamper proof only if Model B/C remains desirable;
5. exact-seed determinism only if Model C is still under consideration.

Current preferred evidence direction:
**Model A/D feasibility first; Model B/C remain alternatives, not selected policy.**

Reason:
The project now has strong E1 evidence that a server-controlled target-only Engine Host can materialize and validate RimWorld state, so the least-trust genesis path should be tested before investing in hostile-client genesis validation.

No Genesis Production authorized.


## 61. MSR-050 Delta — Pipeline REV2 E1 Freeze

Source:
`Production_Transaction_Pipeline_Slice_01_REV2.md`

Master disposition:
**E1 PIPELINE REV2 PASS — DEVELOPER EVIDENCE ACCEPTED / E2 REQUIRED**

Accepted E1 claims within developer-evidence scope:
- immutable admission command snapshot;
- tagged/length-prefixed Fingerprint V2;
- terminal OperationRecords update/delete DB triggers;
- StoreIncarnation validation inside canonical transaction;
- Production P1 ends at durable ordered event append;
- generic consumer/cursor/ACK path removed from P1;
- bounded ingress + dedicated writer thread + drain-on-shutdown design;
- typed storage failures;
- schema v3 fail-closed direction;
- startup readiness narrowed to P1 responsibilities;
- test/fault controls moved out of ordinary Production Server assembly;
- reported 22/22 E1 categories PASS;
- no gameplay/material mutation.

No QA defect is closed by A self-report.

### Provenance note

The submitted REV2 report states that source, Release binaries and schema are frozen, but does not list:
- exact Production source SHA-256 manifest;
- Release Server DLL SHA-256;
- Release EXE SHA-256;
- MVID;
- test-harness/evidence JSON SHA-256.

Therefore independent E2 must establish the exact frozen candidate identity before executing tests.
A must not modify Pipeline REV2 source while E2 is pending.

### Mandatory E2 additions beyond A's battery

1. **Schema v3 structural equivalence**
   Attack required columns/types/nullability, PK order, UNIQUE, FK, CHECK, trigger body/behavior and required indexes, not only trigger existence.

2. **Foreign zero-identity DB**
   A non-empty SQLite database with `application_id=0`, `user_version=0` and unrelated tables must not be mistaken for a fresh empty DB and adopted as WARE.

3. **Legacy fail-closed physical/logical preservation**
   Check main DB + WAL/SHM/logical durable records. Do not infer no mutation from main-file byte equality alone.

4. **Stream sequence concurrency**
   Multiple independent processes/connections append to the same stream; `(StreamId, Seq)` remains unique/ordered with no ambiguous failure.

5. **Shutdown hard boundary**
   Delay/block writer beyond configured join timeout and verify no worker continues against disposed resources and every admitted caller gets a terminal typed outcome.

6. **Bounded admission semantics**
   Verify Production capacity/config and distinction between queue-full backpressure vs SQLite STORAGE_BUSY.

7. **Incarnation race**
   Repeat old-admitted-command vs independent-process rotation at real transaction boundary.

8. **Fingerprint edge cases**
   null vs empty, Unicode, embedded zero/newlines, large strings, array ordering and canonical JSON edge cases; mandatory StoreIncarnation cannot be omitted.

9. **Release packaging**
   Actual Release deployment contains no destructive test/fault CLI, test batteries or callable local control path. Separate test assembly must not be implicitly deployed as Production.

10. **Event log scope**
    Verify no callback/cursor/ACK/delivery claim remains in P1 and no startup path treats undelivered events as failure/readiness work.

### Current gate

Pipeline REV2 is frozen.
No ADR-001 Production Foundation or gameplay-domain mutation begins until independent E2 passes.

A:
**FROZEN / IDLE pending Pipeline REV2 E2** unless Master explicitly releases a non-overlapping scratch task.

Sol:
Pipeline REV2 E2 becomes the next transaction verification task.
If Sol is already executing the previously released Engine Host Round-Trip E2, do not interrupt that run; Pipeline REV2 E2 remains next in queue.

## 62. MSR-051 Delta — Engine Host Round-Trip E2 Result

Source:
`QA_EngineHost_Settlement_RoundTrip_01.md`

Master verdict:
**E2 FAIL — EXACT ENGINE HOST CANDIDATE REJECTED / B2-LITE ARCHITECTURE NOT FALSIFIED**

Independent QA recommendations adopted:
- QA-ENGINE-002: STILL FAILING
- QA-ENGINE-006: STILL FAILING
- B2-lite exact candidate/profile: NOT APPROVED

### What E2 did prove

1. Fresh-process materialization works in principle.
2. Target-map pruning works as a transport/materialization technique.
3. Active job/reservation persistence has positive narrow evidence.
4. Selected environmental state can be conserved without stable geology Thing IDs.
5. Global-clock contamination is independently confirmed; G-Q1 remains OPEN.

### Why E2 failed

1. Semantic approval is not connected to export.
2. Oracle coverage remains insufficient.
3. The source fixture is not a clean semantic reference.
4. Context B was overstated as synthetic-minimal; it is currently a pruned target-map owner context.
5. Evidence lineage mismatch exists between developer-reported artifacts/profile/source and QA-observed candidate lineage.

### Architecture interpretation

B2-lite remains the primary architecture direction.
This E2 FAIL shows materialization transport is feasible but semantic/census approval and provenance are not yet safe enough for canonical admission.

### Current sequencing

- Sol: may immediately move to Pipeline REV2 independent E2.
- A: may work in parallel on scratch-only Engine Host Semantic Gate / Clean Fixture 02.
- Pipeline REV2 Production source remains frozen while Sol verifies it.
- Material-state Production remains HOLD.


## 63. MSR-052 Delta — Pipeline REV2 E2 + G-Q8 REV2

Sources:
- `QA_Production_Transaction_Pipeline_01_REV2.md`
- `GQ8_Asset_Economic_Tax_Boundary_REV2.md`

### Pipeline REV2

Master verdict:
**E2 FAIL — TARGETED REV3 REQUIRED**

Independent candidate identity accepted:
- Server DLL SHA256 `3DDA6E077F19583C456FA64CECC5C65F3057E1D8CC4E4B32B411F4D70F39F3FA`
- Server DLL MVID `0a999e64-335e-4fc3-8998-ba152e7e7340`
- Server.exe SHA256 `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C`
- Common DLL SHA256 `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`
- Production tree 358/358 unchanged during QA.

Independent successes retained:
- 25 OS-process CAS: 1 SUCCESS / 24 STALE.
- 12 OS-process same-ID: 1 SUCCESS / 11 ALREADY_COMMITTED.
- same-stream 48-process contention preserved Seq ordering in tested scope.
- hard-kill pre-commit leaves no canonical effect; post-commit retry returns prior receipt.
- immutable admitted DTO/collections passed.
- WAL/FULL passed.
- legacy v1/v2 fail-closed preservation passed.
- foreign app0/version0 nonempty DB rejection passed.
- Release destructive test controls removed.

Defect disposition:
- QA-PIPELINE-001 STILL FAILING.
- QA-PIPELINE-002 CLOSED — narrow P1 fast path.
- QA-PIPELINE-003 STILL FAILING.
- QA-PIPELINE-004/005/006/014 -> NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE.
- QA-PIPELINE-007 PARTIAL / OPEN.
- QA-PIPELINE-008 STILL FAILING.
- QA-PIPELINE-009 CLOSED — configuration contract.
- QA-PIPELINE-010 CLOSED.
- QA-PIPELINE-011 STILL FAILING.
- QA-PIPELINE-012 CLOSED.
- QA-PIPELINE-013 STILL FAILING.
- QA-PIPELINE-015 CLOSED.
- QA-PIPELINE-016 PARTIAL / OPEN.
- QA-PIPELINE-017 CLOSED.
- QA-PIPELINE-018 CLOSED.
- QA-PIPELINE-019 HIGH OPEN — principal-scoped OperationId collides in global ReceiptId/EventId namespace.

MPC-002 remains HOLD.
ADR-001 Production Foundation remains blocked on Pipeline E2.

### G-Q8 REV2

Master verdict:
**ACCEPTED WITH CORRECTIONS — THREE-BOUNDARY MODEL RETAINED / G-Q8 OPEN**

Retain:
1. `SettlementAssetGraph`
2. `SettlementEconomicInventory`
3. `TaxSeizableAssetSet`

Corrections:
- membership in AssetGraph does not imply economic availability or tax eligibility;
- no Production direct XML decrement is approved by this brief;
- fungible projection may aggregate quantities without exposing per-stack stable identity, but material application must use deterministic selection/rebinding + conservation and mint/transfer stable identity when a material entity crosses a canonical custody boundary;
- Pawn/Animal/Slave are discrete EntityId candidates, never fungible quantities;
- implants/equipment are nested Pawn state; independent tax seizure remains product policy unless requirements explicitly force it;
- geology/natural state remains material/environmental graph, not Auto-Shop inventory by default.

Most important transaction correction:
**Do not normally commit the trade/domain effect merely from a stale projection and then discover material shortfall.**

For offline material mutation:
1. acquire/fence the relevant material scope;
2. materialize/rebase from canonical head;
3. apply the complete material change to a staged candidate;
4. semantic/census validation PASS;
5. durably bind staged result;
6. only then perform the canonical economic/domain commit;
7. promote/publish the already validated result.

A pre-commit shortfall is an ABORT/RETRY, not `REPAIR_REQUIRED`.
`PUBLISH_PENDING/REPAIR_REQUIRED` is reserved for failures after a valid staged result has already been bound by canonical commit.

FR-202/203 prohibit reservation at order registration/setup; they do not prohibit transaction-time fencing/reservation required for execution atomicity.

G-Q8 remains OPEN for exact economic/tax membership policy and runtime mutation proof.

### Active agents

- A: **IN PROGRESS** — `WP-POC-ENGINE-HOST-SEMANTIC-GATE-02`.
- Sol: **IDLE** after Pipeline REV2 E2.
- C: G-Q8 REV2 COMPLETE; next decision brief ready.
- Claude: IDLE.

Do not interrupt A or give A Pipeline REV3 yet.
Pipeline REV3 is prepared but QUEUED until A finishes the current Engine Host Semantic Gate work.


## 64. MSR-053 Delta — Engine Host Semantic Gate 02 E1 Freeze

Source:
`POC_EngineHost_Semantic_Gate_02.md`

Master disposition:
**E1 ENGINE SEMANTIC GATE PASS — DEVELOPER EVIDENCE ACCEPTED / E2 REQUIRED**

Accepted as developer evidence:
- exact WorkerBridge/source/fixture/profile provenance is now reported;
- clean fixture replaces the known dirty round-trip fixture;
- explicit semantic approval lifecycle exists;
- READY alone no longer directly authorizes export;
- reported 15/15 READY-preserving negative cases are rejected and final export blocked;
- tick advancement invalidates approval;
- staged save/quarantine path exists;
- fresh-process A -> B -> C positive round-trip reports zero unexplained declared-manifest mismatch;
- Pipeline REV2 Production source remained untouched.

Official defect status:
- QA-ENGINE-002: OPEN / FIX CLAIMED / E2 PENDING
- QA-ENGINE-006: OPEN / FIX CLAIMED / E2 PENDING

A's statement that these defects are formally CLOSED is not adopted before independent E2.

### New E2 focus

1. **Self-baselining bypass**
   The positive Process B flow creates a census from the current post-tick state and then approves that same manifest.
   Independent QA must determine whether an untrusted/incorrect current state can:
   `mutate -> EXPORT_CENSUS -> APPROVE_SEMANTIC(self) -> EXPORT`
   and thereby bypass source-bound semantic authority.

2. **Approval authority**
   Establish who is authorized to nominate the manifest used for approval.
   A manifest created from the candidate being judged is not automatically a trusted oracle.

3. **Non-tick mutation invalidation**
   Reported lifecycle explicitly proves tick invalidation.
   E2 must mutate supported semantic state without advancing `TicksGame` and verify approval is invalidated or revalidation is otherwise mandatory before export.

4. **Post-save semantic validation**
   Current report proves save-error interception and XML envelope validation before promotion.
   E2 must test silent serialization loss/alteration in the staged artifact.
   `ARTIFACT_APPROVED` must correspond to the saved bytes, not only the pre-save live state.

5. **Binding completeness**
   Approval must be bound to the intended source/profile/generation/target/context identity.
   Map index + ticks + generation alone are not automatically sufficient for canonical provenance.

6. **Manifest tamper/race**
   Changing/replacing the manifest or relevant context after approval must not preserve authority through a stale approval token/state.

### Current execution

- A's Semantic Gate 02 candidate is FROZEN for Sol.
- Sol is released to independently verify Semantic Gate 02.
- A is released to start queued Pipeline REV3 in parallel.
- A must not modify the frozen Semantic Gate 02 candidate during Sol QA.
- C next WP remains ready/not-confirmed unless user has already sent it.


## 65. MSR-054 Delta — G-Q8 Offline Material Application Contract Review

Source:
`GQ8_Offline_Material_Application_Contract_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — EXECUTION CONTRACT NARROWED / MUTATION MECHANISM OPEN**

### Accepted

- `SettlementEconomicInventory` is advisory and revision-bound; it never independently authorizes canonical material commit.
- Offline material mutation follows stage-before-commit.
- Expected material shortfall discovered while constructing the candidate is pre-commit `ABORT/RETRY`.
- Post-commit `PUBLISH_PENDING/REPAIR_REQUIRED` is reserved for failure after canonical commit has already bound a valid staged result.
- Tax execution remains a distinct contract from Auto-Shop execution.
- Fungible projection and discrete custody identity must not be conflated.

### Controlling corrections

1. **Offline execution does not inherently use `DELTA_BARRIER`.**
   `DELTA_BARRIER` is the ordinary-client online coordination state.
   For an offline/unleased Settlement, the Server acquires an exclusive material-scope execution reservation/fence over the relevant execution-island/LocalClock domain + Settlement scope set.
   If the scope is actively leased to an owner client, then the online DELTA_BARRIER protocol is required.

2. **Revision transition correction.**
   The canonical DB commit is the point that advances the new `CommittedSettlementStateRevision`.
   Promotion/fold of the already-bound staged result advances `ArtifactBaseStateRevision` / `ArtifactRevision` and derived projection watermarks.
   Promotion must not invent a second committed-state advance.

3. **Engine Host risk is not zero.**
   Native Engine Host mutation reduces custom cache/reference risk, but QA-ENGINE-002/006 remain under independent Semantic Gate 02 verification.
   Engine Host support is bounded by the approved ContentProfile and validated semantic manifest.

4. **No direct canonical XML edit.**
   A future engine-free codec may operate only on an immutable staged copy bound to exact artifact/profile/revision context.
   In-place mutation of the canonical artifact is not allowed.

5. **Fungible `DefName + quantity` is projection-level only.**
   It is sufficient only for an explicitly defined equivalence class.
   Material selection must still account for eligibility and material distinctions such as holder/location, stuff, quality, HP, taint, biocode, forbidden/reservation/quest state when relevant.
   Exact Auto-Shop eligibility policy remains open.

6. **Selection policy remains product/implementation open.**
   The architecture requires deterministic/replay-safe conservation for a fixed staged input, not a product-visible rule such as "closest to trade beacon".
   Exact stack selection ordering is not frozen.

7. **Projection flags vs exclusions.**
   Forbidden/reserved/quest-bound/holder state should be represented as facts/capabilities when required.
   Whether each category is excluded from Auto-Shop is a product rule unless canonical requirements explicitly decide it.
   Do not silently encode all such exclusions as architecture.

8. **Codec equivalence means semantic equivalence, not byte identity.**
   A future engine-free codec need not produce byte-for-byte identical `.rws` output to Engine Host.
   It must preserve the same declared canonical semantic result and pass independent materialization/census validation.

9. **Staged-result durability requirement.**
   Crash safety claims for both Engine Host and codec depend on immutable durable staged output + hash/profile/base binding before canonical DB commit.
   An in-memory mutation alone is not a safe PREPARED result.

### Current preferred evidence path

- Engine Host staged mutation is the primary evidence path because the semantic gate is actively being hardened.
- Engine-free typed codec remains an optional optimization for a very narrow proven fungible subset.
- Server-custodied escrow/depot remains an optional product model and is not adopted.

### Current agents

- A: Pipeline REV3 IN PROGRESS.
- Sol: Engine Host Semantic Gate 02 E2 IN PROGRESS.
- C: G-Q8 Offline Material Application Contract COMPLETE.
- Claude: IDLE.


## 66. MSR-055 Delta — Semantic Gate 02 E2 FAIL + Pipeline REV3 E1 Freeze

Sources:
- `QA_EngineHost_Semantic_Gate_02.md`
- `Production_Transaction_Pipeline_Slice_01_REV3.md`

### A. Engine Host Semantic Gate 02

Master verdict:
**E2 FAIL — QA-ENGINE-002 / QA-ENGINE-006 STILL FAILING**

Independent improvements retained:
- 15/15 selected READY-preserving corruptions independently detected and blocked when a clean witness manifest is used;
- tick/reload/map-switch invalidation paths work in the tested paths;
- save-time Error/IOException quarantine works and preserves previous approved final;
- fresh-process A -> B -> C transport fidelity and narrow job/reservation persistence remain positive evidence;
- candidate bytes remained frozen during QA.

Blocking failures adopted:

1. **Self-baselining authority bypass**
   A corrupt READY state can export its own census and then use that census as the approval authority.
   Independent QA reproduced 6/6 corrupt states reaching ARTIFACT_APPROVED.

2. **Manifest provenance/authority is not enforced**
   Arbitrary paths, stale-generation manifests and manifests containing false source/profile/context claims can be accepted if material values match.

3. **Approval is stale across non-tick mutation**
   Approval binding uses tick/map/generation but does not prove semantic state immutability.
   QA changed supported live state at the same TicksGame and export still succeeded.

4. **Comparator schema is incomplete**
   Collected fields such as followFieldwork, plant age, bill suspended, hediff part/load identity and job semantics are not all in the gate predicate.

5. **Saved bytes are not semantically approved**
   Pre-save live approval + Error listener + weak XML envelope check is insufficient.
   QA altered staged Shooting 10 -> 15 without log error and it was promoted.
   Truncated/unclosed XML was also promoted.

6. **Promotion does not re-check final bindings**
   Generation/tick/live semantic state can change at the save boundary without blocking promotion.

7. **Fixture/evidence lineage still has discrepancies**
   Multiple submitted positive values differ from independent live values; unresolved RitualObligation references remain; sidecar source/harness hashes do not fully match report claims.

Architecture consequence:
B2-lite transport/materialization remains viable.
The next correction is a semantic-authority protocol, not another broad comparator-only expansion.

### B. Pipeline REV3

Master verdict:
**E1 PIPELINE REV3 PASS — DEVELOPER EVIDENCE ACCEPTED / E2 REQUIRED**

Developer claims accepted only as E1:
- 20/20 mandatory categories;
- schema v4;
- REPLACE guard;
- strict input rejection;
- bounded admission/shutdown;
- mandatory StoreIncarnation;
- startup cross-table checks and writer startup;
- principal-aware derivative IDs;
- release residue manifest;
- no gameplay/material mutation.

Candidate provenance:
- Server DLL SHA256 `8F140D23F8D1BD90A00F3F5B9000C1E01EA0D3CD5AB0615A967635E7668F0209`
- Server DLL MVID `19f86704-dcba-42bd-85a3-bda2ff1ccb78`
- Server EXE SHA256 `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C`
- Common DLL SHA256 `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`

No QA-PIPELINE defect closes from A self-report.

Mandatory E2 focus:
- decimal underflow/precision loss and duplicate JSON keys;
- all string positions for surrogate validation;
- derivative ID delimiter ambiguity (`PrincipalId` / `OperationId` containing `_` or similar);
- schema v4 semantic signature and trigger behavior;
- shutdown UNKNOWN_QUERY_REQUIRED convergence and no worker-after-dispose;
- actual normal entrypoint startup/shutdown writer lifetime;
- cross-table consistency tamper matrix;
- legacy/foreign DB regression;
- release deployment manifest.

### Current parallel plan

- Sol: Pipeline REV3 independent E2.
- A: Engine Host Semantic Authority / Saved-Artifact Gate 03.
- C: ADR-001 Foundation brief delivery remains unconfirmed unless user already sent it.
- Material-state Production remains HOLD.


## 67. MSR-056 Delta — ADR-001 Production Foundation Acceptance Brief

Source:
`ADR001_Production_Foundation_Acceptance_Brief_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — E0 FOUNDATION BOUNDARY FROZEN / IMPLEMENTATION STILL GATED ON PIPELINE E2**

### Accepted boundary

The smallest Production Foundation slice ends when a syntactically valid command has:
- passed server startup/readiness admission;
- been associated with an authenticated stable Principal;
- been associated with a logical SessionEpoch;
- passed protocol/world/content compatibility admission;
- been authorized for its coarse capability;
- been wrapped in a server-authored immutable command envelope;
- reached the Domain Command Router / Pipeline boundary.

The slice does NOT implement:
- gameplay Player creation/lifecycle beyond auth-account identity;
- Faction/Feudal logic;
- Settlement ownership/mutation;
- Trade/Tax;
- material artifact mutation;
- ordinary WriterLease execution;
- Tactical publication.

### Corrections

1. **PrincipalId is stable subject identity; SessionEpoch is separate.**
   `PrincipalId` must not be defined as `PlayerId + SessionEpoch`.
   Pipeline idempotency is principal-scoped and must survive transport reconnect and, where policy allows, later session establishment.
   SessionEpoch is an independent authority/liveness field in the server-authored envelope.

2. **Do not hard-code JWT, bearer format, OAuth/password, or TLS from this brief.**
   Foundation requires a server-validated authentication credential and session binding.
   Exact credential provider/token encoding remains product/deployment policy.
   Transport confidentiality/TLS is not frozen by this brief unless a canonical SRS requirement separately mandates it.

3. **New SessionEpoch does not itself advance FencingGeneration.**
   FencingGeneration advances only when the relevant writer/execution authority is revoked/replaced/handed off or StoreIncarnation/authority domain changes according to the controlling lease contract.
   A new authenticated session with no writer takeover does not mutate settlement fencing.

4. **Same-session transport reconnect does not gain authority from the token alone.**
   Resume requires the server-side logical session to remain valid and, where execution authority exists, the relevant lease to remain resumable.
   G-Q6 `SUSPENDED_GRACE` owns writer-resume semantics.

5. **Server restart does not globally resolve G-Q6.**
   The initial metadata-only Foundation may invalidate in-memory sessions on restart and force re-authentication.
   Future ordinary WriterLease restart behavior still follows G-Q6: durable suspended authority or explicit invalidation/fencing before replacement.
   StoreIncarnationId does not rotate on an ordinary restart.

6. **FencingGeneration semantics corrected.**
   Simple socket reconnect within the same SessionEpoch does not advance it.
   A different SessionEpoch only causes advancement when it actually replaces/revokes an execution authority that was fenced by that generation.

7. **Handshake order is a prerequisite graph, not the exact packet order frozen here.**
   No canonical mutation may be accepted until all required checks succeed:
   protocol compatibility, server readiness, authentication, stable PrincipalId, SessionEpoch, WorldId/StoreIncarnation, content/profile compatibility, and coarse capability authorization.
   Whether public server/world/profile metadata is sent before or after authentication is a protocol/security implementation decision.

8. **StoreIncarnationId is opaque unique incarnation identity, not required to be a numeric monotonic counter.**
   It survives ordinary restart and changes on restore/rollback/wipe/replacement events that invalidate the old persistence timeline.

9. **ContentProfile handshake proves compatibility claim, not hostile-client attestation.**
   A client-reported fingerprint is not by itself anti-cheat proof of the actually loaded client state.
   G-Q2 and Engine Host profile admission remain separate trust layers.

10. **Correlation ID is not replay protection by itself.**
    Request correlation identifies request/response pairs.
    Domain replay/idempotency uses PrincipalId + OperationId and durable lookup.
    A protocol may additionally use per-session frame sequencing/nonces, but that is not invented as a universal requirement here.

11. **Privilege isolation occurs before privileged dispatch/execution, not necessarily before all parsing.**
    Framing and bounded message-type parsing may be required to identify the command.
    Privileged payload handling must not be reachable through the ordinary gameplay route without capability enforcement.

12. **Startup gate does not require future Faction/Settlement registries.**
    Foundation READY requires its own auth/account, world/incarnation, content-profile and Pipeline substrate readiness.
    Player/Faction/Settlement domain registries are next-slice dependencies and gate only routes that need them.

13. **No implication that Trade mutation is available at Foundation READY.**
    TradeConfiguration remains later and requires at least the minimal ownership registry.

14. **Schema startup wording corrected.**
    Current schema must be validated/accepted.
    Legacy schema may require explicit offline migration/reset; normal startup must not imply destructive automatic migration.

15. **Duplicate request uses durable pipeline idempotency, not an ephemeral cache.**
    Exact retry queries/returns the prior durable outcome by principal-scoped operation identity.

### Gate

ADR-001 remains architecture-accepted but not runtime-complete.

Production Foundation implementation is authorized only after Pipeline REV3 independent E2 passes.


## 68. MSR-057 Delta — Pipeline REV3 E2 + Registry Acceptance Brief

Sources:
- `QA_Production_Transaction_Pipeline_01_REV3.md`
- `Player_Faction_Settlement_Registry_Acceptance_Brief_01.md`

### A. Pipeline REV3

Master verdict:
**E2 FAIL — TARGETED REV4 REQUIRED**

Exact independent candidate:
- Server DLL SHA256 `8F140D23F8D1BD90A00F3F5B9000C1E01EA0D3CD5AB0615A967635E7668F0209`
- Server DLL MVID `19f86704-dcba-42bd-85a3-bda2ff1ccb78`
- Server.exe SHA256 `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C`
- Common DLL SHA256 `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`
- Production freeze 353 -> 353, zero changes.

Official defect disposition adopted:
- QA-PIPELINE-001: STILL FAILING / OPEN
- QA-PIPELINE-003: CLOSED — tested terminal SQL boundary
- QA-PIPELINE-007: PARTIAL / OPEN
- QA-PIPELINE-008: PARTIAL / OPEN
- QA-PIPELINE-011: CLOSED — typed storage-error scope
- QA-PIPELINE-013: PARTIAL / OPEN
- QA-PIPELINE-016: CLOSED — explicit incarnation + cross-process rotation
- QA-PIPELINE-019: STILL FAILING / OPEN

Regression closure retained unless future regression:
002, 009, 010, 012, 015, 017, 018.

004/005/006/014 remain:
`NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE`.

Independent positives retained:
- process CAS/same-ID/same-stream concurrency;
- hard-kill transaction atomicity;
- WAL/FULL/foreign_keys/recursive_triggers connection policy;
- bounded ingress/no invisible producer waiters;
- mandatory StoreIncarnation;
- terminal UPDATE/DELETE/REPLACE/UPSERT protection;
- real legacy v1/v2/v3 fail-closed preservation;
- no gameplay probe route;
- clean Release package residue scope.

Remaining REV4 work is narrow:
1. exact/lossless JSON input identity;
2. complete startup consistency + coordinator lifecycle ownership;
3. semantic schema identity;
4. actual writer termination ownership;
5. injective derivative receipt/event identity.

ADR-001 Production Foundation implementation remains blocked.

### B. Player/Faction/Settlement Registry E0

Master verdict:
**ACCEPTED WITH CORRECTIONS — REGISTRY E0 BOUNDARY FROZEN / IMPLEMENTATION NOT YET AUTHORIZED**

Accepted:
- logical ownership is separate from WriterLease and material custody;
- PlayerGlobal segment is keyed by PlayerId, not personal faction identity;
- SettlementId survives ownership transfer;
- ownership epoch/revision fences stale feature configuration;
- Registry remains Dedicated-Server authoritative;
- no RimWorld material state belongs in this slice;
- TradeConfiguration depends on ownership/faction metadata, not inventory.

Corrections:

1. **PrincipalId is stable across SessionEpochs.**
   It is not merely "stable within session".
   SessionEpoch remains separate and does not rewrite domain ownership.

2. **PersonalFactionId is a replaceable reference, not a separate durable identity domain.**
   Model it as a nullable/current `PersonalFactionRef -> FactionId` (or equivalent relation).
   FactionId itself identifies the faction record and is never reused.

3. **SettlementOwnershipEpoch advances only when the canonical legal ownership/control relation actually changes.**
   Join/expulsion/split do not automatically imply transfer of every Settlement.
   Those lifecycle outcomes remain governed by requirements/TBDs.

4. **Do not resolve TBD-01 through registry lifecycle prose.**
   Faction join + settlement-cap overflow remains open.
   The registry must support whichever authorized transfer/retain/reject result Master later selects.

5. **TBD-04 applies to full faction extinction.**
   It is distinct from TBD-01.
   Faction/Settlement records should support terminal/tombstoned status without reusing historical IDs, but exact extinction policy remains open.

6. **FactionRevision must not absorb War/Alliance/Tier domain state.**
   Minimal registry owns faction identity, membership and registry metadata.
   `FactionDomainState` retains political truth such as Tier/Titles/War/Alliance.
   Use distinct membership/record revision if needed.

7. **Ownership relation must be explicit, not ambiguous `PlayerId and/or FactionId`.**
   Registry must represent the exact legal owner/controller relation(s) as typed fields/relations.
   Player ownership and controlling-faction membership are separate facts even if both are returned by one query.

8. **OwnershipEpoch is monotonic within a StoreIncarnation timeline.**
   A backup restore may rewind DB numbers; StoreIncarnationId fences the old timeline.

9. **Genesis reservation is durable and idempotent; do not timeout-delete canonical identity.**
   A failed/abandoned genesis may transition to `ABORTED`/`CANCELLED`/tombstoned state according to future Genesis policy.
   SettlementId/GenesisOperationId history is not garbage-collected and reused merely because a timeout elapsed.
   Only noncanonical staged blobs may be garbage-collected.

10. **Genesis ownership epoch initialization**
    Reservation may bind intended owner/controller while `PENDING_GENESIS`.
    The first active ownership epoch becomes canonical only with accepted Genesis admission.
    Exact pending representation is implementation detail.

11. **Concurrent ownership/config uses CAS/expected epoch, not a vague long-lived DB lock.**
    TradeConfiguration commits against the observed ownership epoch in the same canonical transaction boundary.

12. **Ownership transfer invalidates dependent authorization immediately by epoch check.**
    Projection/index rebuilding may be eventual, but stale TradeConfiguration must not be usable merely because cleanup/rebuild is delayed.

13. **PlayerRecord does not own auth credentials or broad political state.**
    Auth/account credential handling remains Foundation.
    Political Tier/Titles/War remains FactionDomainState.
    Registry Player record is the stable domain identity/reference needed by later slices.

### Current agents

- A: Engine Semantic Authority Gate 03 — IN PROGRESS.
- Sol: Pipeline REV3 E2 COMPLETE / IDLE.
- C: Registry Acceptance Brief COMPLETE.
- Claude: IDLE.

Do not send A another WP while Gate03 is in progress.
Pipeline REV4 is prepared in Master queue only.


## 69. MSR-058 Delta — TradeConfiguration Acceptance Brief

Source:
`Trade_Configuration_Acceptance_Brief_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — TRADECONFIG E0 BOUNDARY FROZEN / IMPLEMENTATION NOT AUTHORIZED**

### Accepted

TradeConfiguration is metadata-only domain state.

In scope:
- durable buy/sell intent/configuration;
- authenticated ownership authorization;
- configuration revision CAS;
- ownership-epoch fencing;
- durable idempotent mutation through Pipeline P1;
- canonical publication-event append for later projection/UI consumption.

Out of scope:
- actual stock/Silver reads;
- item/Silver reservation at registration time;
- trade execution;
- material mutation;
- Engine Host;
- DELTA_BARRIER execution;
- Tax.

### Corrections

1. **P1 has PublicationEvents, not a generic Outbox delivery system.**
   A TradeConfiguration commit may append a durable typed `PublicationEvent` in the same canonical transaction.
   P1 does not promise subscriber execution, UI delivery, ACK, replay consumer, or exactly-once external effect.
   Any UI/projector consumer is a future concrete-consumer gate.

2. **Idempotency is durable, not an in-memory cache.**
   Exact retry uses `(PrincipalId, OperationId)` plus canonical fingerprint and stored terminal receipt.
   Do not describe retry as a transient "cache intercept."

3. **Future trade execution does not universally use DELTA_BARRIER.**
   - offline/unleased Settlement: exclusive material-scope execution reservation/fence;
   - online owner-held Settlement: ADR-007 DELTA_BARRIER;
   - other execution holder: applicable handoff/fencing contract.
   TradeConfiguration itself uses none of these because it is metadata-only.

4. **Registry is the authoritative owner/controller truth.**
   TradeConfiguration should not create a second authoritative owner relation.
   Canonical binding is:
   - `SettlementId`;
   - `SettlementOwnershipEpoch` last validated at commit;
   - optional owner/controller snapshot only for audit/display, explicitly non-authoritative.

5. **Ownership check and config CAS must be atomic at commit.**
   The canonical update transaction checks:
   - current Registry ownership/control relation;
   - expected SettlementOwnershipEpoch;
   - expected TradeConfigurationRevision;
   before advancing the configuration revision.
   A preflight authorization check alone is insufficient.

6. **Ownership transfer policy remains product-open.**
   Auto-clear / disable-and-rebind / transfer-as-is are candidate policies only.
   Frozen invariant:
   old-epoch authorization cannot mutate or execute under the new ownership epoch.
   A transfer transaction and a concurrent config update are serialized by expected-epoch CAS.

7. **SessionEpoch is not a durable config key.**
   This part of C's brief is adopted.
   PrincipalId remains stable subject identity across SessionEpochs.

8. **TradeConfigurationRevision is monotonic only within a StoreIncarnation timeline.**
   Restore/rollback may rewind DB values; StoreIncarnationId fences the old timeline.

9. **ItemDef validation uses the Server's canonical content/profile registry.**
   A client-supplied `ItemDef` string is validated against the server-admitted ContentProfile/definition set.
   A client's claimed fingerprint is not the authority.

10. **Exact order key/value schema remains open where requirements do not force it.**
    Do not invent floating-point pricing semantics.
    Canonical numeric fields must use exact deterministic encoding suitable for the requirement's unit.
    If future APIs support order-level mutation rather than whole-config replacement, stable `TradeOrderId` may be required; it is not frozen by this brief.

11. **"ABA problem" terminology is not controlling.**
    The required invariant is monotonic config revision + ownership epoch + StoreIncarnation fencing.
    Do not imply classic ABA mechanics if the stored state never reuses the same revision identity in an incarnation.

12. **StoreIncarnation rotation is not merely "newer revision fails CAS."**
    An old-incarnation command fails the explicit StoreIncarnation gate even if numeric config/ownership revisions happen to match after restore.

13. **Profile change handling is separate from ownership epoch.**
    A previously valid TradeConfiguration may reference defs absent from a new admitted ContentProfile.
    Startup/profile migration policy must mark/reject incompatible entries according to a future configuration migration contract.
    Do not silently delete them.

### Gate

TradeConfiguration implementation requires:
1. Pipeline E2 PASS;
2. ADR-001 Production Foundation runtime gate;
3. minimal Player/Faction/Settlement Registry runtime gate.

It does NOT wait for Engine Host merely to persist metadata.
Trade execution remains independently blocked by G-Q8/material-state gates.


## 70. MSR-059 Delta — Engine Semantic Authority Gate 03 Developer Result

Source:
`POC_EngineHost_Semantic_Authority_Gate_03.md`

Master disposition:
**E1 PARTIAL — AUTHORITY/SEALING CORE PASS / SAVED-BYTE SEMANTIC GATE PRE-E2 BLOCKER**

Developer classification `E1 ENGINE SEMANTIC AUTHORITY GATE PASS` is not fully adopted.

### Accepted developer evidence

- legacy candidate self-approval path is rejected;
- control-plane AuthorityBundle exists before input validation;
- source artifact SHA / target map / Worker generation checks are present;
- 15 corrupted input fixtures are reported rejected before simulation/export;
- same-tick live mutation is re-censused before staging/promotion and reported blocked;
- ResultManifest/ResultEpoch sealing exists;
- full XML parse-to-EOF is reported;
- staged-file SHA is pinned and rechecked before promotion;
- File.Replace + backup promotion path is reported;
- fresh-process A -> B -> C post-promotion transport fidelity reports exact manifest parity;
- Pipeline candidate remained untouched.

Candidate provenance reported:
- WorkerBridge DLL SHA256 `A95B324EC7DA26155ACF75E64D5B122CF987903157A24C984AAE05D4EE7972CC`
- WorkerBridge MVID `5ea0cf12-3e06-44e2-966a-87f320133bde`
- WorkerBridge.cs SHA256 `E6DA162AC188818DA7C0BA57E840764C581B7D1D696CC6E2163F6C53B0948BDD`
- EngineHostCensus.cs SHA256 `98B487574BBA45081135A32E67325F33B6DAC97560B5914B151A3F4BFB073EAC`
- clean target fixture SHA256 `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B`

### Pre-E2 blockers / mandatory questions

1. **Fresh validator is post-promotion in the submitted flow.**
   The Work Order required a fresh validation Worker/process to load the staged artifact and compare it with the sealed ResultManifest **before promotion**.
   The submitted flow shows:
   `STAGE_SAVE -> ValidateStagedXml -> PROMOTE_STAGED`,
   then later Process C loads the already-promoted Process B artifact.
   This proves post-hoc fidelity, not an admission gate on the exact staged bytes.

2. **Staged SHA only detects mutation after the SHA was captured.**
   It does not prove that native serialization itself produced bytes semantically equal to the sealed live result.
   A silent serializer/postfix alteration occurring before `lastStagedSha` is captured could still become the pinned staged artifact unless a fresh semantic validator rejects it.

3. **AuthorityBundle ContentProfile binding is not evidenced in the report.**
   The controlling WP required ContentProfileFingerprint/profile binding.
   The report demonstrates manifest version, generation, map and source hash checks, but does not show wrong-profile rejection.

4. **Simulation grant authority is not independently evidenced.**
   `SEAL_RESULT <grantId>` records a grant ID, but the report does not prove that the grant itself was pre-authorized and bound by the control plane rather than accepted as an arbitrary label.

5. **Closed semantic manifest coverage is not fully demonstrated.**
   Gate03 shows followFieldwork, plant age and bill suspended now influence the live hash.
   However the report does not establish that every declared supported field, including prior active job/reservation semantics where declared, participates in the canonical equality/hash contract.

6. **Authority bundle/replay binding needs attack coverage.**
   Sol must attack stale/reused AuthorityId, wrong ContentProfile, wrong base/revision/context, bundle byte replacement and cross-artifact replay.

7. **Promotion safety must preserve prior final under replacement failure.**
   File.Replace with backup is directionally correct; independent QA must induce replacement failure/crash boundary and verify old approved final is recoverable and no unvalidated target becomes canonical.

### Interpretation

B2-lite transport remains viable.
Gate03 materially improves the authority model.
The remaining issue is not self-baselining anymore; it is proving that the exact **pre-promotion saved bytes** are semantically identical to the sealed trusted result and bound to the full authority context.

### Current execution

- Gate03 candidate is FROZEN for Sol.
- Sol is released to independent Gate03 E2/audit.
- A is released to Pipeline REV4 in parallel.
- C is IN PROGRESS on E-B Live Barrier/Delta Acceptance Brief (user confirmed delivery).


## 71. MSR-060 Delta — E-B Live Barrier / Delta Acceptance Brief

Source:
`EB_Live_Barrier_Delta_Acceptance_Brief_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — E-B E0 BOUNDARY FROZEN / RUNTIME POC NOT YET RELEASED**

### Accepted

- E-B is specifically the online owner-held WriterLease case.
- Domain Authority and Simulation Authority remain separate.
- successful same-holder barrier/delta does not advance FencingGeneration.
- `ACTIVE -> SUSPENDED_GRACE -> {ACTIVE(resumed), REVOKED/FENCED}` remains controlling.
- client UI/read-only interaction may continue while scoped mutation/ticks are quiesced.
- direct arbitrary XML mutation is prohibited.
- material mutation must be staged/validated before canonical commit.
- commit/revision/promotion/resume are distinct phases.
- final G-Q1/G-Q6 are not resolved by E-B.

### Corrections

1. **Dedicated Server is final Domain Authority, not an unqualified "absolute source of truth".**
   Material simulation may be temporarily authoritative on the valid WriterLease holder within its simulation contract.
   Server remains final authority for canonical domain commit, lease/fence state and accepted artifact lineage.

2. **SessionEpoch is a logical authenticated session, not a socket identifier.**
   It may survive a transport reconnect.
   Socket/transport connection identity is separate.

3. **Barrier root is execution-island / LocalClock-domain scoped.**
   The quiescence target is the entire Settlement scope set carried by that execution island/LocalClock domain, unless narrower clock virtualization has been independently proven.
   A material delta may target one Settlement while all Settlements in the same island pause.

4. **Two-settlement E-B evidence must not require the unrelated Settlement to keep ticking.**
   Under the current Vanilla-first shared-island hypothesis:
   - both Settlements in the island may freeze;
   - only the target Settlement may change materially;
   - neither Settlement may receive a catch-up burst on resume.
   Per-Settlement continued ticking requires separate G-Q1 evidence.

5. **Barrier cut must be sequence/watermark based, not timestamp based.**
   `BARRIER_REQUESTED` establishes a specific cut identity.
   BarrierRequest/ACK must bind at minimum:
   - BarrierId / OperationId relation;
   - WriterLease/LeaseGeneration;
   - FencingGeneration;
   - execution-island + Settlement scope set;
   - base CommittedSettlementStateRevision / ArtifactBaseStateRevision;
   - LocalClock/tick boundary;
   - last applied/accepted client command sequence;
   - final checkpoint/census/artifact hash or equivalent quiescence evidence.

6. **ACK means exact quiescent cut, not "client says stopped".**
   The client stops accepting new scoped mutation locally at the cut.
   The server must account for all client mutations up to the acknowledged sequence before accepting the barrier.
   Commands after the cut are rejected/deferred for post-resume; they are not silently processed against the frozen base.

7. **Post-request/pre-ACK command semantics corrected.**
   C's "processed normally or queued" is too ambiguous.
   Commands already applied before the client observes the cut belong to the final ACK/checkpoint watermark.
   Commands not yet applied at/after cut are held/rejected for post-resume.
   The protocol must never create a command whose server/domain ordering disagrees with the frozen material base.

8. **Client ACK cannot be validated merely by dropping later packets.**
   Server packet rejection is necessary but not proof of already-applied local state.
   The ACK must carry/check a bound checkpoint/census/revision/watermark and lease generation.

9. **BARRIER_ACKED does not transfer WriterLease.**
   The same holder remains the lease holder in a quiesced substate.
   FencingGeneration stays constant unless the lease is actually revoked/replaced.

10. **Engine Host and handoff are not "perfect" reference handling.**
    Native engine mutation reduces custom rebinding risk but remains subject to QA-ENGINE semantic-authority/saved-byte gates and ContentProfile constraints.

11. **Engine-free typed delta needs application-totality proof, not only schema parsing.**
    It must be bound to exact base/EntityIds/eligibility and produce a complete validated candidate or fail without partial material effect.

12. **Successful live material sequence uses stage-before-commit.**
    Preferred proof ordering:
    - barrier cut accepted;
    - exact frozen base/checkpoint established;
    - server-authored operation applied to a candidate;
    - candidate semantically validated and durably staged/bound;
    - canonical DB commit advances CommittedSettlementStateRevision;
    - staged result is promoted/folded or client state is proven identical to it;
    - RESUME carries committed revision + artifact/result identity;
    - same holder resumes only from that committed state.

13. **Pre-commit abort does not automatically revoke the lease.**
    If the client remains connected and can prove rollback/rebase to the accepted barrier base, the barrier may abort and the same lease may resume without fencing.
    Revoke/fence is required when authority safety cannot be re-established or grace/timeout policy demands replacement.

14. **Post-commit disconnect does not always require full redownload.**
    The same valid session/lease may resume if it proves its current material state exactly matches the committed staged result.
    Otherwise it must rebase/download before resuming ticks.

15. **Duplicate Barrier message and duplicate canonical Operation are distinct.**
    Barrier transport replay is idempotent coordination keyed by BarrierId/state.
    Canonical operation retry is durable `(PrincipalId, OperationId)` Pipeline idempotency.
    Do not describe both as an in-memory cache.

16. **Concurrent deltas serialize on the material-scope barrier/reservation, not a generic command-router queue guarantee.**
    A second delta may queue, retry or reject according to barrier policy, but may not overlap mutation against the same frozen scope.

17. **Ownership transfer is checked by ownership epoch only for operations that depend on ownership authorization.**
    If ownership changes before the material/domain commit, the operation must fail its expected-epoch check.
    Do not make DELTA_BARRIER itself the ownership source of truth.

18. **ArtifactBaseStateRevision is a revision pointer, not necessarily the raw physical file hash.**
    Artifact/content hashes may bind the concrete artifact separately.

### E-B runtime gate

Do not release E-B runtime PoC until:
- current Engine Semantic Authority candidate receives Master review after Sol Gate03 audit;
- exact E-B test operation is chosen so it does not resolve Trade/Tax product semantics;
- G-Q1 shared-island implications are explicitly carried into the test.

### Current agents

- A: Pipeline REV4 — IN PROGRESS (user confirmed delivery).
- Sol: Engine Semantic Authority Gate03 audit — IN PROGRESS (user confirmed delivery).
- C: E-B brief COMPLETE.

## 72. MSR-061 Delta — Engine Gate03 E2 FAIL + Pipeline REV4 E1 Freeze

Sources:
- `QA_EngineHost_Semantic_Authority_Gate_03.md`
- `Production_Transaction_Pipeline_Slice_01_REV4.md`

### Engine Semantic Authority Gate03
Master verdict:
**E2 FAIL — QA-ENGINE-002 / QA-ENGINE-006 STILL FAILING**

Independent positives retained:
- 15 corrupted inputs rejected at admission;
- legacy self-approval removed;
- whole collected manifest hash now gates tested fields;
- 102 representative declared semantic leaf paths affected the hash and were blocked in tested scope;
- same-tick recensus catches tested live mutations;
- XML EOF/DTD/second-root failures are rejected;
- save-time Error/IOException quarantine preserves the prior approved output;
- fresh A->B->C transport fidelity remains positive.

Independent blockers:
1. wrong supported saved bytes can be promoted: no pre-promotion fresh semantic validator;
2. promotion can bypass STAGE_SAVE from RESULT_SEALED;
3. arbitrary/stale/blank grant labels can seal results;
4. AuthorityBundle can be overwritten/re-registered and actual profile/context/base lineage is incompletely enforced;
5. failed revalidation can leave stale STEP/SEAL authority;
6. ResultEpoch is not bound to the staged result; reseal/new epoch can promote old staged bytes;
7. current manifest does not prove full active-job identity/targets;
8. normal File.Replace success/backup was not verified in QA environment, though forced failure preserved the prior final.

Parallel-change reconciliation:
Sol observed broader Server subtree changes while Engine QA ran. The exact 294-file Engine candidate/fixture/dependency set remained unchanged, and the changing Server/Pipeline DLL was not loaded by this Engine audit. This Engine verdict is therefore valid for the frozen Engine candidate only. Pipeline REV4 requires its own independent freeze/E2.

### Pipeline REV4
Master verdict:
**E1 PIPELINE REV4 PASS — DEVELOPER EVIDENCE ACCEPTED / INDEPENDENT E2 REQUIRED**

Developer claims:
- exact streaming JSON/arbitrary-precision numeric identity;
- injective domain-separated derivative IDs;
- Schema V5 semantic checks + rollback startup canaries;
- explicit full consistency graph;
- service lifetime/coordinator shutdown ownership;
- 27/27 mandatory E1 categories PASS;
- no P1 redesign or gameplay/material mutation.

Reported hashes:
- Server DLL `EACBDD3AE976515779E25C4450C549CB2AD20E8F699C738E05D747EADD211A92`
- Server EXE `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C`
- Server PDB `A8A8998992F80885F50EBCF35F60CDF1F8F12FA0926E92B034FD54CFDF469464`
- Common DLL `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`
- E1 JSON `F3E971600E95D6D1696124BE304FC6AFAB741B47EE9A809C93E42DE86BD182FB`

No additional QA-PIPELINE defect closes from A self-report.
Sol must independently establish exact MVID/source/package freeze and re-run the five open groups plus regression locks.

### Current execution
- A: ready for Engine Semantic Authority Gate04.
- Sol: ready for Pipeline REV4 independent E2.
- C: G-Q1 Temporal Topology Decision Brief REV2 IN PROGRESS.

## 73. MSR-062 Delta — G-Q1 Temporal Topology Decision Brief REV2

Source:
`GQ1_Temporal_Topology_Decision_Brief_REV2.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — G-Q1 REMAINS OPEN / VANILLA-FIRST HYPOTHESIS RETAINED**

Current hypothesis remains:
**VANILLA MULTI-MAP FIRST -> MINIMAL INTERCEPTION -> SEPARATE EXECUTION ISLAND ONLY IF FALSIFIED**

Accepted:
- basic map-local freezing is promising but global `TicksGame` / `TicksAbs` contamination remains real;
- G-Q1 is not ready for closure;
- execution-island barrier quiescence may pause sibling Settlements sharing one LocalClock domain;
- this shared-island pause is acceptable for an initial candidate unless a canonical requirement/product decision requires independent simultaneous progression;
- global-time-sensitive systems need targeted runtime classification;
- metadata foundations do not depend on final G-Q1 closure.

Corrections:
1. Model C is per independent execution-island/LocalClock domain, not inherently per Settlement.
2. Model B does not pre-commit to virtualizing every global tick getter; interception/reprojection is evidence-driven and only for canonical-impacting dependencies.
3. Mod compatibility risk remains OPEN; the brief itself gives contradictory risk labels for Models A/C.
4. Temporal subsystem classifications are hypotheses unless independently observed.
5. Quest/Research/Ideology/WorldPawns ownership is not resolved here.
6. PlayerGlobal exact field schema remains OPEN; stable owner remains PlayerId.
7. Weather/sky/PlayLog/Tales/global managers are not automatically safe-to-discard reconstructible context.
8. Cosmetic/global chronology drift is acceptable only if it cannot mutate frozen canonical material/domain state or cause forbidden catch-up.
9. Raw `.rws` byte equality is not the G-Q1 oracle. Use fresh-load semantic manifest/census comparison plus explicit allowed differences and custody/material conservation.
10. Model A failure does not automatically reject Model B. Model C becomes preferred only if required semantics cannot be achieved with a bounded maintainable interception surface for the supported profile.
11. The 60,000-tick probe is useful but must be combined with shorter/longer horizons and boundary transitions.
12. Under Models A/B the barrier remains island-scoped; per-Settlement barrier isolation is not assumed.

G-Q1 next evidence gate:
compare pure shared-island Vanilla behavior, targeted minimal interception only where Vanilla violates the LocalClock material contract, and separate-process isolation as a control. Classify each dependency as safe global/reconstructible, domain-owned, bounded interception required, island separation required, or unresolved.

Current agents:
- A: Engine Semantic Authority Gate04 IN PROGRESS.
- Sol: Pipeline REV4 E2 IN PROGRESS.
- C: G-Q1 brief COMPLETE.

## 74. MSR-063 Delta — Pipeline REV4 Independent E2

Source:
`QA_Production_Transaction_Pipeline_01_REV4.md`

Master verdict:
**E2 FAIL — TARGETED REV5 REQUIRED**

Exact independent candidate:
- Server DLL SHA256 `EACBDD3AE976515779E25C4450C549CB2AD20E8F699C738E05D747EADD211A92`
- Server MVID `72eda58c-0deb-41fb-8834-b41274e2c35f`
- Server EXE SHA256 `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C`
- Server PDB SHA256 `A8A8998992F80885F50EBCF35F60CDF1F8F12FA0926E92B034FD54CFDF469464`
- Common DLL SHA256 `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`
- Common MVID `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7`
- E1 results SHA256 `F3E971600E95D6D1696124BE304FC6AFAB741B47EE9A809C93E42DE86BD182FB`
- Production freeze 353 -> 353, zero changes.

### Official defect disposition

- QA-PIPELINE-001: **PARTIAL / OPEN**
  - exact numeric identity, duplicate-key handling, trailing-root rejection, raw invalid UTF-16 are independently fixed;
  - escaped malformed surrogates and `int.MinValue` exponent reach `STORAGE_FAILURE` instead of `INVALID_REQUEST`;
  - no durable operation is created in those failures.

- QA-PIPELINE-007: **STILL FAILING / OPEN**
  - legitimate ABORTED CAS-loser history can make restart fail;
  - history parent identity drops PrincipalId / full canonical operation identity;
  - six independent persistence-graph semantic mutations still reach READY.

- QA-PIPELINE-008: **CLOSED — tested Schema V5 contract**
  - 34/34 independent schema mutations fail closed;
  - independent descriptor equals expected signature;
  - startup canaries are rollback-only;
  - real nonempty v1-v4 fail closed preserving state.

- QA-PIPELINE-013: **STILL FAILING / OPEN**
  - bounded admission/caller completion improved;
  - final Shutdown/Dispose/Main completion is not tied to actual writer termination;
  - Release path can return with writerAlive=true and later repository activity.

- QA-PIPELINE-019: **CLOSED — admitted identity/derivation scope**
  - delimiter/Unicode/long/control-like identities independently coexist;
  - exact retries return stored derivative IDs;
  - receipt/event namespaces and revision encoding are independently distinct.

Retained closures unless future regression:
002, 003, 009, 010, 011, 012, 015, 016, 017, 018.

004/005/006/014 remain:
`NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE`.

### Independent positives retained

- 25-process one-winner CAS;
- 12-process same-ID exact retry;
- same-stream ordering under contention;
- real hard-kill atomicity across pre/post commit cuts;
- WAL/FULL/foreign_keys/recursive_triggers;
- terminal UPDATE/DELETE/REPLACE/UPSERT protection;
- explicit StoreIncarnation fencing;
- no generic consumer/ACK/PUBLISHED path;
- no gameplay/material mutation;
- clean Release runtime residue.

### REV5 scope

P1 architecture remains unchanged.

REV5 is limited to:
1. typed input-exception classification cleanup;
2. legitimate ABORTED/reject-audit recovery semantics;
3. full principal-scoped operation/history parent identity;
4. complete persistence-envelope/derived-ID/audit semantic reconciliation;
5. final writer/service lifetime ownership;
6. candidate Release manifest/provenance update.

If history schema changes are required, bump schema explicitly and preserve prior closed schema guarantees through regression.

ADR-001 Production Foundation implementation remains BLOCKED pending Pipeline E2 PASS.

### Current agents

- A: Engine Semantic Authority Gate04 — IN PROGRESS.
- Sol: Pipeline REV4 E2 COMPLETE / IDLE.
- C: PlayerGlobal / SharedWorld Temporal Boundary — IN PROGRESS.

Do not send A REV5 while Gate04 is in progress.

## 75. MSR-064 Delta — Engine Semantic Authority Gate04 Developer Result

Source:
`POC_EngineHost_Semantic_Authority_Gate_04.md`

Master disposition:
**E1 ENGINE SEMANTIC AUTHORITY GATE04 PASS — DEVELOPER EVIDENCE ACCEPTED / E2 REQUIRED**

A's developer classification is accepted at E1 only.
QA-ENGINE-002 and QA-ENGINE-006 remain OPEN until independent Sol verification.

### Developer improvements accepted as E1 evidence

- immutable/idempotent AuthorityBundle registration;
- registration after load/admission blocked;
- validation failure revokes readiness;
- actual active ModsConfig-derived profile value checked against AuthorityBundle;
- pre-registered SimulationGrant required;
- READ_ONLY blocks STEP/SEAL;
- fresh independent RimWorld validator loads exact staged bytes before promotion;
- StageValidationReceipt required;
- RESULT_SEALED cannot directly promote;
- caller staging path substitution blocked;
- reseal/ResultEpoch invalidates old stage receipt;
- staged-file SHA rechecked at promotion;
- three supported saved-byte semantic mutations rejected before promotion;
- XML EOF/second-root/DTD rejected;
- replacement failure preserves old final;
- subsequent same-volume replacement + backup reported successful;
- fresh A -> validator -> promote -> B -> validator -> promote -> C chain reported PASS.

Candidate provenance reported:
- RimWorldWin64 SHA `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D`
- Assembly-CSharp SHA `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`
- Assembly-CSharp MVID `61e41735-6189-4da4-9d21-0260257b5097`
- WorkerBridge DLL SHA `8DB1D5A34DE2E3B2B6A61F078933D5828F2A99FB4E14E5694F7C3A8C80917EC9`
- WorkerBridge MVID `9424f95c-8a3b-43b3-b99f-dd0b377d37b2`
- WorkerBridge.cs SHA `A2AB7352B3069E94670F938A2404D83FFE0FB49B558B11E7E0754E6481091DB8`
- EngineHostCensus.cs SHA `00985787D67FA2629B4A63FCF178842D3A48941AE6EDFEA78AC37B0DFA8D8B50`
- clean Context B SHA `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B`
- Gate04 harness SHA `AD6FA026F7EA38005A8EF63AFE8CF2EEA03F56A788AF30F5E9EAC22581FFDBF9`
- Gate04 result JSON SHA `A051DD4D93484DA61C96334A9720EC327E21EFD4AA9E8513251FEB6D06D1F4CC`
- developer ContentProfile value `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C`

### Mandatory E2 questions

1. **StageValidationReceipt issuer authenticity**
   The report calls the receipt "signed/cryptographically validated" but does not document the signing/issuer key model.
   `validatorProcessId != currentPid` alone is not authority.
   Sol must determine whether a caller can fabricate/modify a receipt JSON with a different PID and valid-looking fields.

2. **Validator expected-manifest substitution**
   The validator command accepts `sealedResB64`.
   Sol must attempt to give the validator a caller-crafted sealed result that matches a corrupted staged file, obtain a validator receipt, then submit that receipt to the simulator.
   Simulator acceptance must independently bind the receipt to its own immutable current SealedResultId/manifest/epoch, not merely trust what the validator was told.

3. **Receipt replay/cross-worker/cross-stage**
   Attack receipt reuse across:
   - another WorkerGeneration;
   - another AuthorityId;
   - another GrantId;
   - another staged SHA/path;
   - another profile/context;
   - another ResultEpoch/SealedResultId.

4. **ContentProfile completeness**
   The E1 report's profile fingerprint is the SHA of the active ModsConfig.
   Sol must establish whether Gate04 authority binds a complete enough admitted profile for this PoC.
   Same ModsConfig with changed mod/assembly/definition content must not silently satisfy a profile contract if that content is authority-relevant.
   Do not confuse exact candidate freeze/provenance with runtime ContentProfile binding.

5. **Grant completeness**
   Verify actual grant binding to stable scope/context, generation and mode, not merely target map index.
   Unknown/stale/cross-authority grants must fail after all relevant state transitions.

6. **Readiness revocation**
   After every failed authority/profile/grant/input validation path, independently prove STEP/SEAL/STAGE/PROMOTE remain blocked until explicit reset/re-admission.

7. **Job scope statement**
   Gate04 explicitly bounds current job coverage to JobDef.
   Do not certify active job ID/targets/driver state as supported.
   Previous narrow Goto/reservation persistence evidence remains separate from full semantic-manifest coverage.

8. **Fresh validator isolation**
   Verify actual validator is a distinct native RimWorld process/profile and that validator output is consumed only for the exact staged SHA.
   The validator must not alter/promote the simulator's canonical final itself.

### Current execution

- A Gate04 candidate FROZEN.
- Sol ready for Gate04 independent E2.
- A ready for Pipeline REV5.
- C PlayerGlobal / SharedWorld Temporal Boundary remains IN PROGRESS.

## 76. MSR-065 Delta — PlayerGlobal / SharedWorld Temporal Boundary 01

Source:
`PlayerGlobal_SharedWorld_Temporal_Boundary_01.md`

Master disposition:
**ACCEPTED WITH CORRECTIONS — LOGICAL BOUNDARY TAXONOMY RETAINED / EXACT OWNERSHIP AND PHYSICAL SPLIT REMAIN OPEN**

Accepted:
- logical categories `MapSegment(SettlementId)`, `PlayerGlobalStateSegment(PlayerId)`, `FactionDomainState(FactionId)`, `SharedWorldProjection`, Domain-only, reconstructible, unresolved/mixed;
- PlayerGlobal stable owner is PlayerId, never PersonalFactionId;
- materialization records the global/domain revisions/context it actually depends on;
- frozen MapSegment may compose with a newer compatible global/domain projection;
- G-Q1 remains OPEN.

Corrections:
1. Research, Ideology, History, Genes, Quests, WorldPawns, Tales/PlayLog, Storyteller, Weather/Sky, GameComponents, Royalty and other globals are hypotheses, not frozen ownership/schema.
2. PlayerGlobal exact fields remain OPEN.
3. Reconstructible/discardable requires noninterference evidence; appearance as visual/transient is insufficient.
4. Quest/WorldPawns are not automatically read-only projections; exact lifecycle/reference authority remains evidence-driven.
5. WriterLease/Engine Host may simulate/propose global changes but Dedicated Server remains final authority for canonical PlayerGlobal/FactionDomain/SharedWorld revision advancement.
6. Frozen Map + newer PlayerGlobal composition is conditional on dependency compatibility/revalidation; otherwise rebase/rematerialization/staged transform is required.
7. Materialization hard vs diagnostic revision bindings are dependency-sensitive; Faction/SharedWorld revisions are not globally diagnostic.
8. ContentProfileFingerprint remains a hard admission binding under ADR-006B.
9. Cross-owner examples are not universal transaction rules; first establish canonical owner and whether material state changes.
10. Pawn/world/transit custody remains multi-boundary with stable EntityId; exact WorldPawns physical representation is OPEN.
11. `Pruned Target-Map Owner Context` remains non-minimal/unproven.
12. No literal `.rws` -> Map blob + PlayerGlobal blob split is selected yet.
13. E-B runtime PoC does not require final PlayerGlobal physical schema, but its test operation must have bounded global dependencies.
14. Genesis runtime PoC needs explicit dependency/revision bindings, not complete PlayerGlobal schema closure.

Current agents:
- A: Pipeline REV5 IN PROGRESS.
- Sol: Engine Semantic Authority Gate04 E2 IN PROGRESS.
- C: PlayerGlobal / SharedWorld Temporal Boundary COMPLETE.

## 77. MSR-066 Delta — Pipeline REV5 Developer Result

Source:
`Production_Transaction_Pipeline_Slice_01_REV5.md`

Master disposition:
**E1 PIPELINE REV5 PASS — DEVELOPER EVIDENCE ACCEPTED / INDEPENDENT E2 REQUIRED**

A's developer classification is accepted at E1 only.
QA-PIPELINE-001 / 007 / 013 remain OPEN until independent Sol verification.

### Candidate provenance reported
- Server DLL SHA256 `1143AE62FD74F0C93F0504B48C1501D5153F40C2E903BD4D69BA9BE1E6983479`
- Server MVID `a5cba4c3-1e2f-4a19-a35c-0241ccf12e81`
- Server EXE SHA256 `0C1B14510C3CDC7396848E7228660456F7F127F97E680B785A7B62665765378C`
- Server PDB SHA256 `754752E0E97E5FA7ACC09B5568B7780C86CB3C57CCD8E5F82CC8C3CC31BB90F1`
- Common DLL SHA256 `2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB`
- Common MVID `84b7cb6b-224a-43de-b2b6-1f67e2e51cf7`
- Common PDB SHA256 `5119FE41A0FD3BB6B6DCA299B85FD3EEF0F91D4FB7B1AC77DAEDA762E9B2D0F0`
- E1 results SHA256 `4B44749D3EBD2DFF0ABEE881620BE8E4A311B6260A233C11D3D2E713B62C9AFB`
- Schema V6 signature `64BDB62037D70303D7F2AE15D39FC7E7DFD9F01021B5E0AA0709A51FA507E721`

Reported isolation:
Engine Semantic Authority Gate04 candidate remains untouched/frozen.

### Developer improvements accepted as E1 evidence
1. remaining escaped-surrogate/int-min-exponent failures return INVALID_REQUEST with zero durable operations;
2. Schema V6 adds PrincipalId to ProbeRevisionHistory and composite `(PrincipalId,OperationId)` parent FKs;
3. natural mixed COMMITTED/ABORTED restart reportedly reaches READY;
4. 25-process winner/24-loser DB reportedly restarts READY;
5. cross-principal same OperationId same/different scopes reportedly works;
6. six REV4 false-READY mutations reportedly fail;
7. request fingerprint, derivative receipt/event identity and typed audit relationships are reportedly revalidated;
8. final Dispose/Shutdown/Main reportedly wait for actual writer termination;
9. caller UNKNOWN deadline is separated from service lifetime completion;
10. legacy v1-v5 fail closed;
11. 21/21 E1 batteries PASS.

### Mandatory E2 watch items
1. ABORTED observed-revision historical truth: a plausible-but-false past observed revision must not pass merely because `0 <= observed <= current` and `observed != expected`.
2. ABORTED semantic reason/status must be exact, not generic zero-child acceptance.
3. RequestFingerprint must be independently recomputed from canonical envelope/payload.
4. Receipt/Event expected IDs must be independently derived from canonical parent identity/revision.
5. COMMITTED/ABORTED audit DetailsJson must be typed semantic evidence, not subset-matching free text.
6. Schema V6 must independently re-prove the schema guarantees that were closed for V5.
7. Clean Shutdown/Dispose/Main must remain blocked with writer held beyond both old ~6s and A's 7–8s E1 windows.
8. The report does not identify a current REV5 release-manifest filename/hash in its provenance table; Sol must verify the actual package manifest artifact exists and matches the frozen candidate.

### Current execution
- A: REV5 candidate FROZEN / IDLE.
- Sol: Engine Semantic Authority Gate04 E2 IN PROGRESS.
- C: G-Q1 Decisive Runtime Probe Contract IN PROGRESS.
- Pipeline REV5 E2: QUEUED for Sol after Gate04 E2 completes.

## 78. MSR-067 Delta — Engine Semantic Authority Gate04 Independent E2

Source:
`QA_EngineHost_Semantic_Authority_Gate_04.md`

Master verdict:
**E2 FAIL — QA-ENGINE-002 / QA-ENGINE-006 STILL FAILING**

### Exact independent candidate

- RimWorldWin64 SHA `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D`
- Assembly-CSharp SHA `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`
- Assembly-CSharp MVID `61e41735-6189-4da4-9d21-0260257b5097`
- WorkerBridge DLL SHA `8DB1D5A34DE2E3B2B6A61F078933D5828F2A99FB4E14E5694F7C3A8C80917EC9`
- WorkerBridge MVID `9424f95c-8a3b-43b3-b99f-dd0b377d37b2`
- WorkerBridge.cs SHA `A2AB7352B3069E94670F938A2404D83FFE0FB49B558B11E7E0754E6481091DB8`
- EngineHostCensus.cs SHA `00985787D67FA2629B4A63FCF178842D3A48941AE6EDFEA78AC37B0DFA8D8B50`
- Target Context B SHA `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B`
- Actual ModsConfig SHA `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C`
- independent clean V4 engine manifest digest `9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC`

Exact Engine candidate freeze:
456 -> 456 files, zero candidate changes.

Broader Production tree changed during QA, consistent with concurrent Pipeline REV5 work, but the tested Engine candidate did not load the changed Server/Pipeline DLL. Therefore Engine E2 evidence remains valid for its exact frozen candidate and is not a Pipeline freeze certificate.

### Independent blockers adopted

1. **Validator receipt issuer is not authoritative.**
   A caller-crafted StageValidationReceipt with visible fields plus a fake different PID was accepted and reached ARTIFACT_APPROVED.
   Receipt has no operator-controlled task identity, unforgeable capability/nonce, authenticated local channel, or equivalent issuer proof.

2. **Validator expected truth is caller-substitutable.**
   Simulator sealed trusted result A.
   QA produced persisted result B with supported semantic differences.
   Validator correctly rejected B when compared to A.
   QA then supplied B's self-census as the validator's expected manifest while retaining A metadata.
   Validator issued a real receipt, and simulator promoted B under sealed A.

3. **Receipt/result binding is incomplete.**
   Receipt field mutations for scopeId, targetMapIndex, manifestVersion, sealedManifestHash, sourceArtifactHash and empty validatorProcessId were accepted in isolated tests.
   Existing checks for staged SHA/path, generation, authorityId, grantId, profile, sealedResultId and resultEpoch are not sufficient.

4. **Failure revocation is inconsistent.**
   Several malformed/invalid REGISTER_GRANT / REGISTER_AUTHORITY / receipt submissions return errors but leave old valid grant/readiness/stage authority usable.
   Control-plane validation failure paths do not consistently transition to the required fail-closed state.

5. **Authority/grant scope lineage is incomplete.**
   Grant scope can differ from AuthorityBundle scope and still STEP/SEAL.
   Changing grant scope after receipt can still allow promotion.
   Authority equality omits storeIncarnation/baseLineage.

6. **Current epoch fence is incomplete.**
   Direct internal mutation of currentResultEpoch can leave old sealed result/receipt promotable because promotion compares receipt to sealed object but not the current epoch source.
   Normal reseal/reset does invalidate old receipt; the reproduced issue is an internal invariant gap.

7. **ContentProfile binding violates ADR-006B direction.**
   Runtime fingerprint hashes only ModsConfig XML.
   Same ModsConfig with changed admitted assembly bytes retains the same fingerprint and permits admission/STEP.
   Frozen binary provenance is not equivalent to runtime content-profile admission.

8. **Supported semantic scope documentation is stale.**
   Actual V4 active-job coverage is stronger than the Gate04 report:
   JobDef + loadID + targetA/B/C are in the manifest, and reservation fields are also present.
   Complete job-driver/toil/path state remains unproven.
   Shipped `.census.json` is manifestVersion 3.0 and must not be treated as the V4 authority oracle.

9. **Diagnostic error branch defect.**
   Same-tick stage recensus failures correctly revoke/block output but return NullReferenceException after sealedResult is cleared.
   This is not a corruption bypass but must be corrected.

10. **Replacement fallback durability limit.**
    Normal File.Replace/backup and exclusive-lock preservation passed.
    The UnauthorizedAccessException copy-overwrite fallback is not crash-atomic and was not independently validated.
    Production authority must not rely on that fallback.

### Independent positives retained

- 15/15 persistent bad-input admission cases rejected;
- large saved Shooting/hediff/stack corruption rejected;
- malformed EOF / second-root / DTD rejected;
- normal no-receipt/direct/path/reseal/reset fences largely work;
- 102/102 representative declared primitive field mutations changed full digest;
- 12/12 tested same-tick live mutations changed full hash and blocked final output;
- actual Goto target/loadID and reservation survived tested fresh-load validation;
- A->B->C transport/fresh-load mechanics function;
- replacement lock failure preserves old final;
- successful replacement creates correct backup and exact stage/final bytes.

### Interpretation

B2-lite transport/materialization is not falsified.
Fresh-process validation is mechanically feasible.

The remaining blocker is **trusted result lineage**:
the validator must receive expected truth from the simulator/operator's immutable sealed result, and the resulting validation evidence must be tied to a real operator-controlled validator task rather than caller-authored JSON/PID fields.

### Current execution

- Sol: Gate04 E2 COMPLETE / now ready for Pipeline REV5 E2.
- A: Pipeline REV5 frozen / now ready for Engine Gate05.
- C: G-Q1 Decisive Runtime Probe Contract IN PROGRESS.
