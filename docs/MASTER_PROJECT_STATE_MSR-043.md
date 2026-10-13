MASTER_PROJECT_STATE.md
Project: WarEconomy / RimMulti
State Revision: MSR-043
Date: 2026-10-02
Owner: Master (GPT-5.6 Sol)
This file is a current-state snapshot, not a replacement for the Canonical SRS.
If this file conflicts with the Canonical SRS or a later Master Decision, the higher-authority source wins.

1. Authority Hierarchy
1. Canonical SRS: 요구사항_명세서.md
2. Master Decisions / Accepted ADRs
3. This Master Project State Ledger
4. Agent reports / PoC reports / QA reports
5. Historical code/comments/chats
Only IDs from the root Canonical SRS are Canonical requirement IDs.
2. Canonical Requirement Baseline
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
3. Team
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
4. Core Product Architecture Known from SRS
Dual Time
- Dedicated Server World Time continues even with zero players.
- Settlement Local Time is separate and normally pauses while the settlement is offline.
- Tactical activity can temporarily activate actual RimWorld simulation.
- Server World Time, Settlement Local Time, Tactical Time, and RimWorld TicksGame must not be conflated.
Shared Tactical
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
Domain Authority
- Dedicated Server owns final Domain Authority.
- Tactical Worker may own Simulation Authority only for the active tactical scope.
- Player clients are never trusted final domain authority.
Feudal / Territory / Diplomacy / Economy
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
5. Explicit Product TBDs — DO NOT SILENTLY RESOLVE
- TBD-01: faction join + settlement-cap overflow
- TBD-02: WarPending forced-expulsion destination
- TBD-03: exact theft trigger timing
- TBD-04: full faction extinction rule
- TBD-05: partial tax collection / LastCollection / arrears semantics
6. Major Risks
- RISK-01 Offline Combat Authority — Critical
- RISK-02 Remote Tactical — High
- RISK-03 Persistent Offline Trade Inventory — High
- RISK-04 Atomic Full-Map Ownership Transfer — Medium-High
- RISK-05 Intent-Aware Betrayal — Medium
7. ADR Status
ADR-001 — Authenticated Identity / Central Authority / Persistent State
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
ADR-002 — Tactical Session / Offline Combat Authority
Status: PROVISIONALLY ACCEPTED
Primary candidate:
Candidate C — Trusted Tactical Worker Always
Current Master status:
- actual RimWorld Worker feasibility proven in bounded scope
- ENGINE-02 independent QA = FAIL
- Production Tactical = NOT AUTHORIZED
- Remote Tactical = NOT AUTHORIZED
- Candidate C remains primary target, not rejected
ADR-003 — Canonical Settlement State / Entity Identity / Save Provenance
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
ADR-004 — Distributed Ownership Transaction / Repair
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
ADR-005 — Intent / Betrayal
Status: NOT YET AUTHORED
ADR-006A — Temporal Authority
Status: ACCEPTED
Accepted core contracts:
- Dedicated Server WorldTick W, Settlement LocalTick L_s, engine TicksGame/G, and host monotonic time M are distinct authority/operational coordinates.
- Tactical progress is not a separate durable calendar; it continues the target settlement's existing L_s.
- Offline ordinary settlement simulation has ΔL=0; authorized Tactical simulation advances only the target L_s.
- One LocalClockId has at most one active writer. One engine execution island has one active LocalClock writer.
- Full Worker .rws is private checkpoint/materialization/extraction input only and is never a wholesale canonical replacement.
- Primary publication architecture = B2: full context for reference resolution + target-scoped simulation + Target-Scoped Outcome Publication / Canonical Merge.
- Canonical publication contains only authorized target write-set and explicit cross-boundary transfers.
- Temporal fields use typed temporal schema; blanket tick-field rebasing is forbidden.
- LOAD is fenced before autonomous simulation; READY requires semantic/temporal validation.
- World deadlines/cooldowns are server W authority.
- Offline trade/tax may mutate canonical assets with ΔL=0; local clock freeze does not forbid authorized asset transactions.
- Ordinary resume uses current canonical graph/time, never an old local full save as implicit authority.
Accepted product policies:
- Settlement-resident chronological and biological aging follow authorized residence/local simulation, not incidental Worker global G.
- Tactical participants age/progress according to the target settlement's advancing local/tactical timeline under supported vanilla mechanics.
- Moving between different local-date domains preserves current age and remaining-duration semantics; native anchors are reprojected rather than creating catch-up debt.
- Server process downtime policy: ΔW=0; resume from last durable committed W. Zero-player time still progresses while the server is running.
- Raw W does not automatically drive caravan/transit physiology. Transit physiology requires an explicit residence/transit clock policy before implementation.
- If multiple independent LocalClocks require simultaneous simulation, use separate execution islands or a separately validated per-map virtualization design; do not multiplex divergent local clocks through one raw global G by assumption.
Implementation/QA status:
- ADR acceptance does NOT close QA-ENGINE-004 or other ENGINE defects.
- B2 extraction/merge, temporal materialization, ordinary resume, transit physiology, and recovery remain implementation/validation work.
ADR-006B — Configuration & Content Manifest
Status: NOT YET AUTHORED
ADR-007 — Ordinary Settlement Simulation Authority / Multi-Settlement Execution Topology
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
ADR-008 — Shared World Layer / Transit / World Projection
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
8. Tactical Engine Gate
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
9. Current Master Constraints
1. Full Worker .rws is input/context unless explicitly validated otherwise.
2. Full Worker .rws output is NOT automatically canonical post-tactical state.
3. Production is unlocked per dependency, not by one global switch.
4. Unresolved ADR decisions must not be hard-coded into Production work.
5. PoCs are only for material uncertainty; prototype production is not a goal.
6. A developer's PASS never replaces independent QA.
7. Canonical SRS remains the ultimate product authority.
8. TBD-01..05 must never be silently decided.
10. Current Active Work
- Sol: ADR-006A completed; temporarily reassigned to independent Tactical Boundary verification/final QA because Verification B is unavailable
- Gemini A: WP-TAC-WORKER-HARDEN-01 submitted; must freeze the exact hardened implementation and provide reproducible self-regression artifacts
- Gemini B: UNAVAILABLE due to allocation/quota interruption; incomplete WP-VERIFY-TAC-BOUNDARY-02 produces no accepted evidence
- Gemini C: available for report reconciliation / traceability after Sol verification
- Master: ADR-002 remains PROVISIONALLY ACCEPTED; next Tactical hardening gate now depends on Sol independent verification of A's frozen implementation
11. Context-Recovery Rule
If Master conversational context appears incomplete, recover from:
1. Canonical SRS
2. MASTER_PROJECT_STATE.md
3. MASTER_DECISION_LOG.md
4. QA_DEFECT_LEDGER.md
5. current ADR / QA / Dev reports
Do not rely on chat memory as the sole project record.
12. MSR-002 Delta
- Dev A submitted Tactical_Worker_Hardening_Evidence_01.md.
- Self-reported improvements include strict manifest/load gating, RUN_TICKS quarantine, bounded slices/queue, engine-generated complex fixture, load-time tick fence, fastEcology suppression, and simulation start-debt fix.
- These are developer evidence only until Verification B and/or Sol independently confirm them.
- Master identified two report-status errors:
  1. ADR-002 is not rejected; it remains PROVISIONALLY ACCEPTED.
  2. QA-ENGINE-004 cannot be claimed resolved by this Work Package; it remains an ADR-006A architecture issue.
- Master also flagged a potential architectural regression: the report's dispatch inventory says World.WorldTick, WorldObjectsHolder.WorldObjectsTick, and FactionManagerTick are retained, which must be independently checked against temporal/domain-authority constraints.
13. MSR-003 Delta — ADR-006A Accepted
- ADR-006A_Temporal_Authority.md reviewed and accepted by Master with amendments/policy decisions.
- Temporal authority is now an upstream contract for ADR-002, ADR-003, and ADR-004.
- Primary publication direction is B2 / Target-Scoped Outcome Publication & Canonical Merge.
- Full Worker save wholesale publication remains prohibited.
- QA-ENGINE-004 remains OPEN until the accepted temporal contract is implemented and independently verified.
- Dev A's retained World/global dispatch paths must now be judged against ADR-006A, not developer labels such as "passive" or "read-only".
14. MSR-004 Delta — Verification B Temporarily Unavailable
- Gemini B stopped mid-task due to allocation/quota limits before producing a complete deliverable.
- No partial B work from the interrupted run is accepted as verification evidence unless later recovered as a complete, reproducible report.
- Temporary verification flow:
  A frozen implementation + self-regression evidence → Sol independent verification/final QA → C reconciliation if needed → Master Gate.
- This is a temporary degradation of the preferred five-agent flow, not a change in role philosophy.
- A may not keep modifying the verification target while Sol tests it; any code change creates a new candidate build/revision and requires re-verification.
15. MSR-005 Delta — Formal ADR Artifacts Created
Standalone formal ADR artifacts now exist:
- ADR-001_Authenticated_Identity_Central_Authority_Persistent_State.md
- ADR-002_Tactical_Session_Offline_Combat_Authority.md
- ADR-006A_Temporal_Authority_ACCEPTED.md
ADR-001 and ADR-002 are reconstructed formalizations of already-existing Master decisions; they are not new architecture decisions. ADR-006A is the finalized Master ACCEPTED form of Sol's proposal plus Master policy choices.
Governance rule: An ADR that is ACCEPTED or PROVISIONALLY ACCEPTED must have a standalone ADR artifact.
16. MSR-006 Delta — External Architecture Red-Team Summary
An external Claude Opus 5.5 web review summary was received. The full ARCH_REDTEAM_REVIEW_001.md artifact has not yet been supplied to Master, so only claims present in the user's pasted summary are treated as review input.
Master accepts the following as material architecture gaps/directions:
- ordinary settlement simulation authority/provenance is under-designed;
- multiple settlements with divergent LocalTicks create an unresolved execution-topology problem;
- online/offline trade/tax and Tactical must share a coherent Settlement-state mutation pipeline;
- stable cross-process entity identity is required before B2 merge can be considered production-safe;
- Candidate C still lacks remote-play evidence;
- untrusted owner save/materialization input requires an explicit type/mod/content trust boundary.
Plan change:
1. ADR-003 is broadened to Canonical Settlement State / Entity Identity / Save Provenance.
2. New ADR-007 is introduced for Ordinary Settlement Simulation Authority / Multi-Settlement Execution Topology.
3. ADR-004 remains Distributed Ownership Transaction / Repair and follows the canonical state/write-set contracts.
4. B2 remains accepted as the primary architecture direction, but merge granularity is not yet fixed.
5. A coarse-grained B2 variant — immutable whole-target-map/settlement snapshot under an exclusive simulation lease plus typed cross-boundary operations — is the preferred option to analyze in ADR-003 because it may avoid field-by-field custom serialization.
6. Remote Tactical validation is required before ADR-002 can become ACCEPTED, but it will start after the currently frozen A candidate completes Sol independent verification.
7. Transit clock/physiology becomes a prerequisite for end-to-end Tactical Production integration and is assigned to ADR-007; it does not block current Worker hardening tests.
17. MSR-007 Delta — Full ARCH-REDTEAM-REVIEW-001 Reviewed
The complete external architecture red-team report was reviewed by Master.
Master interpretations/decisions:
- SRS §4.2 assigning the Client "Settlement Local Simulation" is interpreted as simulation responsibility, not final canonical custody. ADR-001 remains controlling for final authority. Future ADR-003/007 must formalize how client-produced ordinary simulation becomes a candidate for canonical state.
- SRS §77's historical "Map Owner Authoritative" preference is explicitly superseded for current architecture by ADR-002 Candidate C, as an architecture choice permitted by the SRS architecture-choice section. This does not change the user-facing offline-combat requirements.
- ADR-001 and ADR-002 reconstructed standalone texts are re-ratified as the current authoritative ADR artifacts.
- ADR-006A B2 remains the accepted primary architecture direction, but it is now governed by explicit falsification criteria. Failure of those criteria reopens ADR-006A/B2 instead of forcing downstream ADRs to conform.
- Current preferred B2 granularity for ADR-003 analysis is B2-lite: whole target Settlement/Map artifact replacement under an exclusive writer/asset lease, plus typed cross-boundary operations and a small server index/manifest. Field-level arbitrary object merge is not accepted as the default.
- Client-originated save/checkpoint artifacts are hostile input. "Trusted Worker" means operator-controlled process, never trusted input.
- Gameplay content is server-pinned. Approved content must be classified before runtime admission; unknown critical content must not be allowed to weaponize runtime fail-closed behavior into immunity from offline attack.
- Remote Tactical Presentation/Replication is a mandatory falsification gate for Candidate C. It begins after the currently frozen Worker candidate finishes Sol independent QA, and may run in parallel with ADR-003/007 work.
- Shared World Layer / transit / world projection is elevated to ADR-008.
- ADR-006B is renamed Configuration & Content Manifest.
Open Master/product decisions remain where the SRS genuinely does not decide them, especially multi-settlement ordinary topology and detailed tax/inventory eligibility. They must not be silently encoded in implementation.
18. MSR-008 Delta — Sol Independent QA of Frozen Worker Candidate
Source:
QA_Tactical_Worker_Hardening_Independent_Review.md
Master accepts Sol's independent QA as authoritative evidence for the frozen WP-TAC-WORKER-HARDEN-01 candidate.
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
19. MSR-009 Delta — C Canonical State / Ordinary Authority Decision Brief
Source:
Decision Brief_Canonical_State_and_Ordinary_Authority.md
Master accepts the brief as architecture analysis input.
Accepted architecture decisions:
- ADR-003 scope remains Canonical Settlement State / Entity Identity / Save Provenance.
- B2-lite is promoted from preferred analysis option to the default architecture baseline, still subject to the B2 falsification criteria already recorded in MDR-007.
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
20. MSR-010 Delta — ADR-003 / ADR-007 Draft-1 Review
Received:
- ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance.md
- ADR-007_Ordinary_Settlement_Simulation_Authority.md
Master verdict:
- ADR-003 Draft-1: PROPOSED / REVISION REQUIRED
- ADR-007 Draft-1: PROPOSED / REVISION REQUIRED
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
5. ADR-003 must not assume a canonical target artifact is literally a target-only .rws; native full .rws remains non-canonical whole-world output. Canonical settlement artifact format/materialization package remains an implementation boundary until validated.
6. Server Projection / Index must be durable and derivable/verifiable; not merely "server-memory".
7. Queued but unapplied Tactical-time Economy operations do NOT advance SettlementStateRevision. They remain pending operations until post-Tactical revalidation/commit. Otherwise every queued trade would stale the Worker checkpoint and defeat the exclusive-lease design.
8. Whole-target B2-lite must not devolve into logging every internal split/merge/destroy. Canonical EntityId is mandatory for server-addressable/cross-boundary/persistent externally referenced entities; internal engine-only ephemeral identity remains inside the artifact unless exported.
9. Native loadID binding mechanism (ThingComp/global mapping/etc.) is not yet accepted; the ADR must specify the identity contract and mark the concrete binding mechanism as validation-required.
10. Hostile input validation needs typed semantic/content validation and provenance/plausibility checks in addition to XML schema/size/mod allowlist.
No QA defect status changes.
21. MSR-011 Delta — Remote Tactical Presentation PoC-01
Source:
POC_Remote_Tactical_Presentation_01.md
Master assessment:
STRONG CONDITIONAL PASS / INDEPENDENT QA REQUIRED
What A materially demonstrated in two real RimWorld 1.6 processes:
- a Worker-owned authoritative simulation can accept remote own-Pawn commands;
- a separate client-side RimWorld mirror can remain non-authoritative;
- local client ticks do not alter Worker state;
- snapshot reconciliation can correct mirror divergence;
- foreign/AI Pawn command attempts can be rejected at the Worker boundary;
- stale presentation generation commands can be rejected;
- move/draft/job/attack/health paths were exercised through the mirror/Worker loop.
Important limitation:
The presentation client itself was launched with -batchmode -nographics. Therefore this PoC does not independently prove actual human-visible rendered GUI usability, real OnGUI interaction, 60 FPS presentation, or end-user peaceful-visit UX. It proves engine/object/UI-model structural feasibility and command/reconciliation plumbing.
Architecture direction:
- Candidate P1 thin/raw-render client remains rejected as impractical.
- Candidate P2 non-authoritative Mirrored Client Map becomes the primary presentation candidate, not yet final ACCEPTED.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
- Actual graphical-client validation + independent QA are required before the remote-presentation falsification gate is considered passed.
Authority amendment direction:
- Tactical/physical simulation facts may be produced by the Worker.
- Domain/economic/ownership/faction-membership effects remain server-authorized/committed.
- Do not classify whole UI features as exclusively Worker or Server by name; mixed operations may produce Worker facts plus Server domain commits.
- Do not pre-commit to generic two-phase commit; ADR-003/004 define transaction semantics.
No existing QA-ENGINE defect status changes.
22. MSR-012 Delta — ADR-003 / ADR-007 v2 Review
Received:
- ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v2.md
- ADR-007_Ordinary_Settlement_Simulation_Authority_v2.md
Master verdict:
- ADR-003 v2: PROPOSED / REVISION REQUIRED
- ADR-007 v2: PROPOSED / REVISION REQUIRED
Draft-1 corrections successfully addressed:
- handoff now takes the final candidate while the old lease is still valid;
- dead/unresponsive client falls back to the last committed canonical head;
- FencingGeneration is separated from SessionEpoch/WorkerGeneration;
- G-Q1 includes Separate Execution Islands;
- target artifact is logical/format-neutral rather than assumed target-only .rws;
- durable projection/index is recognized;
- pending Tactical Economy operations no longer advance the canonical head;
- EntityId scope is narrowed away from all ephemeral internal objects;
- hostile input validation is broadened.
Remaining contract blockers:
1. PendingOperationQueue, CommittedOperationLog, and MaterializationManifest are not yet cleanly separated. Only committed operations may enter a canonical materialization manifest.
2. Every artifact needs an explicit ArtifactBaseStateRevision / applied-through watermark so committed operations are replayed exactly once.
3. Online ordinary Auto Shop/Tax against a live leased client remains under-designed. Fast-forward-only checkpoints will otherwise become stale whenever the server commits a material delta during ordinary play.
4. ADR-007 needs an explicit server-side lease state machine and HANDOFF_BARRIER admission rule. During a barrier, normal checkpoints/operations cannot race the final candidate.
5. Writer lease scope must bind SettlementId/LocalClockId, holder identity, base revision, fencing generation, and authorized write scope.
6. Canonical EntityId must remain stable, but native RimWorld loadID need not be globally stable across processes. Binding is per materialization context and must be unique/reference-consistent there.
7. Hostile semantic validation may be performed by a server-controlled validation engine/sandbox; Dedicated Server must not become a full RimWorld semantic parser.
8. The uploaded v2 ADR files are malformed as Markdown (almost all content is serialized onto one physical line). v3 must be normalized into readable structured Markdown.
No QA defect status changes.
23. MSR-013 Delta — ADR-003 Accepted
Source:
ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v3.md
Master decision:
ADR-003 — Canonical Settlement State / Entity Identity / Save Provenance = ACCEPTED
Master clarification incorporated into the authoritative accepted artifact:
- Server-authored committed deltas do not depend on client ACK for canonicality.
- DELTA_BARRIER client acknowledgement gates writer resumption/base advancement only.
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
24. MSR-014 Delta — Independent Remote Presentation QA + ADR-007 v3 Review
Source:
- QA_Remote_Tactical_Presentation_Independent_Review.md
- ADR-007_Ordinary_Settlement_Simulation_Authority_v3.md
Remote Presentation Gate
Independent Sol QA classification:
PARTIAL / INSUFFICIENT GRAPHICAL EVIDENCE
Master accepts this classification.
Confirmed:
- normal graphical RimWorld client rendered the mirror map;
- camera / selection / inspect / Draft gizmo / right-click native UI lifecycle worked;
- selected mirror Pawn could be reconciled without immediate render/reference breakage;
- scripted Worker RPC authorization and stale command-generation rejection worked.
Not confirmed / failed:
- actual GUI Draft/right-click commands were not converted into remote intents;
- GUI actions mutated the local mirror while Worker state remained unchanged (rpcCalls=0);
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
ADR-007 v3
ADR-007 v3 remains PROPOSED / REVISION REQUIRED.
Reason:
Its DELTA_BARRIER flow still states that the client applies/ACKs the delta before the writer base advances and on failure falls back to "last committed head" without explicitly preserving the already Server-committed delta. This is ambiguous/in tension with ACCEPTED ADR-003 MD-023.
Required correction:
- Server-authored operation canonical commit is independent of client ACK.
- ACK gates only resumption of the current writer lease.
- if ACK/apply fails, fence/revoke the client and rematerialize from the current committed head including the committed operation.
- distinguish pre-commit barrier failure from post-commit client-application failure.
25. MSR-015 Delta — ADR-007 Accepted Core Contract
Source:
ADR-007_Ordinary_Settlement_Simulation_Authority_v4.md
Master decision:
ADR-007 — Ordinary Settlement Simulation Authority / Topology = ACCEPTED for the core authority, lease, fencing, barrier, and handoff contract.
Open Decision Requests remain:
- G-Q1 Multi-Settlement Topology
- G-Q2 Ordinary Simulation Anti-Cheat / Residual Trust
- G-Q6 Checkpoint Loss Window / Disconnect Grace
Master clarifications incorporated:
- barrier admission applies to both HANDOFF_BARRIER and DELTA_BARRIER;
- responsive DELTA_BARRIER may first accept one designated barrier checkpoint;
- Server-authored operation commit is independent of client ACK;
- writer resumption advances BaseCommittedSettlementStateRevision, not ArtifactBaseStateRevision;
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
26. MSR-016 Delta — ADR-008 Work Package Started
New active analysis Work Package:
WP-ADR-SHARED-WORLD-01
Assigned:
Gemini 3.1 Pro C
Objective:
Produce PROPOSED ADR-008_Shared_World_Layer_Transit_World_Projection.md.
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
- A continues WP-REMOTE-PRESENTATION-HARDEN-01.
- C's ADR-008 analysis does not block or modify A's frozen presentation scope.
27. MSR-017 Delta — Remote Presentation Hardening Developer Evidence
Source:
Remote_Tactical_Presentation_Hardening_01.md
Master assessment:
DEVELOPER EVIDENCE ACCEPTED / INDEPENDENT VERIFICATION PENDING
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
28. MSR-018 Delta — ADR-008 Draft-1 Review
Source:
ADR-008_Shared_World_Layer_Transit_World_Projection.md
Master verdict:
ADR-008 Draft-1 = PROPOSED / REVISION REQUIRED
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
3. Define durable WorldStateRevision and per-object/custody revision/fencing sufficient to reject stale world mutations without forcing one global hot lock.
4. Do not destroy a caravan at ingress before durable custody transfer. Model PREPARED/PENDING ownership transition conceptually and defer exact atomic commit/outbox/repair mechanics to ADR-004.
5. Egress must likewise avoid temporary double custody between Settlement and Shared World.
6. Offline Tax/Trade may be committed from the durable projection/index only when the required canonical facts are sufficient. Operations requiring RimWorld semantic mutation/validation must use a server-controlled engine/materialization path; "offline = always no engine" is not accepted.
7. PendingOperationQueue is Settlement-local. A concurrent world operation targeting a caravan during ingress must be serialized/fenced in the Shared World custody domain, not automatically stuffed into the target Settlement queue.
8. Mod approval must reject or quarantine unsupported world behavior at approval/migration time. Do not claim arbitrary unknown mod code can safely be "stripped".
9. Global Faction registry projection must not leak hidden world-object/location state.
10. Separate "world movement continues offline" from "transit physiology progresses offline"; the latter remains tied to the transit-clock policy.
No existing QA defect status changes.
29. MSR-019 Delta — ADR-008 Accepted Core Contract
Source:
ADR-008_Shared_World_Layer_Transit_World_Projection_v2.md
Master decision:
ADR-008 — Shared World Layer / Transit / World Projection = ACCEPTED for the core world authority, revision/fencing, visibility projection, and custody-transfer contract.
Accepted:
- Dedicated Server canonical authority over WorldObjects/caravans, authoritative location/path progress, custody membership, world visibility state, and world-domain ordering;
- client/Worker WorldObjects are projections/materializations only;
- untrusted clients submit destination intent only; authoritative path/movement facts are server-controlled;
- WorldStateRevision plus per-object/custody revision model;
- explicit TransitClockId distinct from W and Settlement L_s;
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
30. MSR-019 Active Work Addition — ADR-006B Started
Assigned to Gemini 3.1 Pro C:
WP-ADR-CONFIG-CONTENT-01
Target:
PROPOSED ADR-006B_Configuration_Content_Manifest.md.
This work proceeds in parallel with Sol's independent re-verification of A's Remote Presentation hardening.
31. MSR-020 Delta — Remote Presentation Hardening Independent QA
Source: QA_Remote_Tactical_Presentation_Hardening_02.md
Master gate: PARTIAL / REMAINING BLOCKER
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
- QA-PRESENT-010 — STILL FAILING: reconciliation still targets Find.CurrentMap rather than an authority-bound map.
Architecture:
- Candidate P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
Parallel:
- A receives WP-REMOTE-PRESENTATION-HARDEN-02.
- C continues ADR-006B.
32. MSR-021 Delta — ADR-006B Draft-1 Review
Source:
ADR-006B_Configuration_Content_Manifest.md
Master verdict:
ADR-006B Draft-1 = PROPOSED / REVISION REQUIRED
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
2. Replace the absolute runtime guarantee "must not fail due to missing content/schema" with an invariant that server-pinned content drift must not be caused by an untrusted participant. Runtime defects/corruption may still fail safely into quarantine/REPAIR_REQUIRED without turning the target into an attack-immune state.
3. Migration must not load an old artifact directly under only the new profile. The migration pipeline must preserve an old-profile-compatible read/materialization context, then transform/validate into the new profile (or use an explicitly supported dual-profile migration adapter).
4. ContentProfileId and ContentProfileRevision semantics need sharpening: immutable profile identity/fingerprint vs. monotonically ordered world adoption/migration revision. Do not treat a changed profile as the same immutable identity unless defined by a separate stable lineage ID.
5. Artifact/checkpoint metadata must bind both the exact gameplay profile fingerprint and the schema/codec versions required for deterministic validation.
6. Add a MIGRATION_REQUIRED / QUARANTINED admission state distinct from generic REPAIR_REQUIRED.
7. Cosmetic mod eligibility cannot rely on an unverifiable universal proof. It requires server-approved capability classification and fail-closed exclusion from authority-sensitive hooks unless validated.
8. Config categories need a MIGRATION_REQUIRED class in addition to prospective/snapshotted/session-bound/historical.
9. Operation-snapshotted config must capture the exact value/config revision in durable operation state; referencing only "current ConfigRevision" later is insufficient.
10. Client handshake ordering must align with ADR-001 lifecycle: compatibility/profile checks may happen during handshake, but content mismatch is not itself authentication and must not collapse auth/session semantics.
No QA defect statuses change from this draft review.
33. MSR-022 Delta — ADR Evidence Policy / Project Checkpoint
Master governance policy added:
MASTER_ADR_EVIDENCE_POLICY.md
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
MASTER_PROJECT_CHECKPOINT_MPC-001.md
Current phase:
late architecture / targeted feasibility, before broad Production vertical-slice implementation.
34. MSR-023 Delta — ADR-006B Accepted
Source:
ADR-006B_Configuration_Content_Manifest_v2.md
Master decision:
ADR-006B — Configuration & Content Manifest = ACCEPTED (core contract).
Accepted core:
- immutable exact gameplay ContentProfileFingerprint;
- stable profile lineage identity + monotonic world adoption ContentProfileRevision;
- artifact/checkpoint profile + schema + semantic/temporal codec binding;
- content compatibility as admission, separate from identity authentication;
- layered dependency closure: manifest/hash -> typed static checks -> controlled engine load -> post-load semantic validation;
- runtime QUARANTINED / REPAIR_REQUIRED, with no silent drop;
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
35. MSR-024 Delta — Remote Presentation Hardening-02 Developer Evidence
Source:
Remote_Tactical_Presentation_Hardening_02(1).md
Master assessment:
DEVELOPER EVIDENCE ACCEPTED / INDEPENDENT VERIFICATION REQUIRED
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
1. A labels Draft/Move as REAL_GRAPHICAL_OBSERVATION, but the report describes direct invocation of Command_Toggle.ProcessInput(null) and TryTakeOrderedJob(...). Sol must distinguish actual OS/user GUI input from in-process method invocation.
2. The reported privileged gate is PrivilegedQaToken OR Source == "QA_TEST_CONTROL". If Source is client-controlled, an untrusted client may forge the source string and bypass the token. This must be attacked explicitly.
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
36. MSR-025 Delta — ADR-004 Draft-1 Review
Source:
ADR-004_Distributed_Ownership_Transaction_Repair.md
Master verdict:
ADR-004 Draft-1 = PROPOSED / REVISION REQUIRED
Accepted direction:
- OperationId + immutable payload hash idempotency;
- separate PREPARED / COMMITTED / PUBLISH_PENDING lifecycle;
- canonical commit is Server-controlled and distinct from RimWorld artifact publication;
- pre-commit abort vs post-commit forward recovery distinction;
- one-canonical-custody-owner invariant;
- outbox/journal/reconciler architecture;
- stale writer fencing and restart recovery requirements.
Critical corrections required:
1. Do not assume CommittedOperationLog alone can reconstruct every committed Tactical/material-state result after artifact loss. Engine-produced state may not be fully representable as typed domain operations.
2. Before canonical COMMIT, any non-reconstructible material result required by that commit must exist as a durable immutable staged result/candidate with hash, profile/schema identity, source/base revision and result manifest. The staged candidate is non-canonical but recovery-addressable.
3. Canonical commit must durably bind the operation to either:
   - reconstructible committed operations from an older artifact watermark; or
   - a durable staged material result that can be promoted/re-published after restart.
     A commit may not depend on volatile Worker/client memory.
4. Artifact promotion is conditional on exact manifest/base/head/profile/hash validation. An arbitrary candidate file may never be promoted just because the DB operation committed.
5. Disconnect/crash before COMMIT does not always imply ABORT. If the Server has a complete durable PREPARED record and all required authoritative facts/staged material, a Server-owned operation may continue to commit. Otherwise it aborts/expires.
6. PREPARED reservations/locks require deterministic lock ordering, expiry/recovery ownership, and explicit distinction between durable reservation and writer fencing. Avoid permanent deadlocks after restart.
7. EntityIds reserved during PREPARED are provisional/reserved identifiers only; they are not canonical visible entities until COMMITTED.
8. Cross-scope commit must define one transactionally consistent commit record covering source custody, destination custody, operation state, and source/destination revisions. SettlementProjectionRevision is not a substitute for canonical material revision.
9. Projection/outbox updates are derived side effects and must not be described as part of the canonical truth unless they are explicitly in the same durable DB transaction. Projection may lag canonical commit and be repaired.
10. Failure matrix row “during DB commit = ambiguous” is too weak. After restart, durable storage must deterministically classify the transaction as committed or not committed; ambiguity may exist to the caller, not in canonical recovery.
11. Semantic validation failure after materialization must distinguish:
    - pre-commit candidate rejection/quarantine;
    - post-commit publication validation failure, which requires forward repair/quarantine and must not erase the committed domain decision.
12. Exact transaction behavior must support both:
    - typed operation-only commits;
    - commits whose material-state consequence requires a durable staged artifact/result manifest.
No existing QA defect closes from this draft.
37. MSR-026 Delta — ADR-004 Accepted
Source:
ADR-004_Distributed_Ownership_Transaction_Repair_v2.md
Master decision:
ADR-004 — Distributed Ownership Transaction / Repair = ACCEPTED (core contract).
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
- CommittedSettlementStateRevision is canonical material head; ArtifactBaseStateRevision is only the artifact fold watermark;
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
38. MSR-027 Delta — Remote Presentation Hardening-03 Independent QA
Source:
QA_Remote_Tactical_Presentation_Hardening_03.md
Master gate:
PARTIAL / REMAINING BLOCKER
Independent E2 results accepted:
Newly CLOSED
- QA-PRESENT-002 — CLOSED
  - Worker autonomous movement plus normal RemoteClientController.Update() periodic replication independently reproduced.
  - 30 automatic post-command updates arrived without TestHarness/manual GET_SNAPSHOT.
  - client native Pawn.Position and coarse move completion converged to Worker state.
- QA-PRESENT-005 — CLOSED
  - North/East/South/West round-trip independently verified through actual Worker -> wire -> normal periodic client apply.
- QA-PRESENT-010 — CLOSED
  - client apply is bound to snapshot TargetMapId rather than viewed Find.CurrentMap.
  - Map_1 remained unchanged while Map_0 was authoritative target.
  - unresolved target map was explicitly rejected.
Still OPEN / material blockers
- QA-PRESENT-004 — STILL FAILING / HIGH
  - Pawn.Position follows authoritative snapshots but rendered Pawn.DrawPos/sprite remains at the old location.
  - screen position, hit target, selection/inspect coordinates therefore diverge.
  - health/Hediff graph reconciliation also remains incomplete.
- QA-PRESENT-006 — STILL FAILING / HIGH-IF-PROMOTED
  - cmd.Source == "QA_TEST_CONTROL" is remote/client-controlled and grants privileged control.
  - invalid token / stale generation / wrong session + forged Source successfully executed privileged controls, including generation mutation and fixture reload.
- QA-PRESENT-007 — STILL FAILING / HIGH-IF-PROMOTED
  - timer replication performs synchronous socket ReadLine on the Unity main thread.
  - a 2-second delayed response caused ~2.03 s frame gap and ~1.87 s control-response delay.
  - timeout/reconnect and bounded queue/list behavior remain incomplete.
Still OPEN / partial
- QA-PRESENT-008 — PARTIAL
  - periodic payload/cadence metrics are now materially improved and independently consistent;
  - A's evidence oracle still conflates direct native method invocation with actual OS GUI input in its own harness and does not check DrawPos/displayed movement.
- QA-PRESENT-009 — PARTIAL
  - declared fixture dependencies are now present and prior missing class/Def symptoms are resolved;
  - texture/null-material, auxiliary listener conflict, and headless initialization errors remain, so a clean canonical load is not certified.
Previously closed and regression-confirmed:
- QA-PRESENT-001 — CLOSED
- QA-PRESENT-003 — CLOSED
Architecture:
- P2 remains PRIMARY PRESENTATION CANDIDATE.
- Candidate C remains PROVISIONALLY ACCEPTED.
- P2 is not falsified.
- tested Draft/Move internal state replication is E2-proven.
- rendered Move presentation is not yet E2-proven.
- Remote Tactical Production remains NOT AUTHORIZED.
Next:
- A receives a narrowly scoped Hardening-03 implementation WP.
- C continues Shared Settlement State Pipeline Design.
39. MSR-028 Delta — Shared Settlement State Pipeline Design-01 Review
Source:
Shared_Settlement_State_Pipeline_Design_01.md
Master verdict:
INCOMPLETE DELIVERABLE / RESUBMISSION REQUIRED
Production implementation remains NOT AUTHORIZED.
The submitted file terminates during the OperationRecord sketch and does not contain the majority of the required Work Order deliverables.
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
7. ArtifactBaseStateRevision/artifact pointer advances only after validated artifact fold; canonical CommittedSettlementStateRevision may already be ahead.
8. Lease timeout behavior must not silently resolve G-Q6. Design the mechanism while leaving grace/expiry policy open behind configuration/decision boundary.
No runtime QA defect status changes.
Parallel work remains:
- A: Remote Presentation Hardening-03
- C: Pipeline Design-02 resubmission
- Sol: next focused presentation E2 verification after A freezes candidate
40. MSR-029 Delta — Shared Settlement State Pipeline Design-02 Accepted for Narrow Infrastructure Slice
Source:
Shared_Settlement_State_Pipeline_Design_02.md
Master verdict:
DESIGN ACCEPTED WITH MASTER CORRECTIONS
NARROW PRODUCTION INFRASTRUCTURE IMPLEMENTATION AUTHORIZED / QUEUED
Key correction:
The proposed TEST_TYPED_NOOP_SYNC must not increment CommittedSettlementStateRevision without an actual Settlement material-state mutation.
Accepted first implementation slice:
PIPELINE_PROBE_CAS
- dedicated non-gameplay ProbeScopeId
- dedicated ProbeRevision
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
The Production infrastructure WP is authorized but queued; A should begin it only after freezing/completing the current Hardening-03 candidate so the Tactical QA target is not disturbed.
C is free for the next architecture analysis after this design acceptance.
41. MSR-030 Active Work — ADR-005 Started
C completed the accepted Shared Settlement State Pipeline Design-02 task.
Assigned to Gemini 3.1 Pro C:
WP-ADR-INTENT-BETRAYAL-01
Target:
PROPOSED ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract.md
This work is independent of:
- A's current Remote Presentation Hardening-03;
- the queued Production Transaction Pipeline Slice-01.
Current execution order for A:
1. finish/freeze Remote Presentation Hardening-03;
2. Sol focused E2 verification;
3. then begin authorized WP-PROD-TRANSACTION-PIPELINE-01 unless Master redirects based on QA.
42. MSR-031 Delta — Remote Presentation Hardening-03 Developer Candidate Frozen
Source:
Remote_Tactical_Presentation_Hardening_03.md
Frozen candidate:
- DLL SHA256 0F57AFB12BE7D7C8FF1F12C231F8A3CA9815FB76069BEBDBB723604488C582BB
- Fixture SHA256 ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED
- Production WarEconomyMod/ reported unchanged by A
Master assessment:
DEVELOPER EVIDENCE ACCEPTED / E2 INDEPENDENT VERIFICATION REQUIRED
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
2. The new candidate's Draft and Move tests are explicitly SCRIPTED_GUI_CALL, not actual OS/user GUI command evidence. Previous E2 actual-OS evidence exists for the prior candidate, but the new frozen candidate requires focused GUI regression.
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
- The queued WP-PROD-TRANSACTION-PIPELINE-01 remains queued until this focused E2 result is reviewed.
Parallel:
- Sol: WP-QA-REMOTE-PRESENTATION-HARDEN-04
- C: ADR-005 Intent/Betrayal analysis
43. MSR-032 Delta — ADR-005 Draft-1 Review
Source:
ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract.md
Master verdict:
ADR-005 Draft-1 = PROPOSED / REVISION REQUIRED
Accepted direction:
- Intent, simulation facts, domain evaluation, and political commit are separate layers.
- Tactical Worker remains Simulation Authority only.
- Dedicated Server remains final betrayal/diplomacy Domain Authority.
- intent provenance must bind authenticated principal/session, canonical identities, Tactical session/generation and diplomacy context.
- mid-session relationship changes must be revisioned and projected back to active Tactical sessions.
- trap/turret/mental-break/autonomous cases require explicit provenance and product policy.
Required corrections before acceptance:
1. Client intent must be admitted/authorized by the Dedicated Server before it becomes an AuthorizedAction. Worker may validate simulation preconditions but must not be a co-authority for domain authorization.
2. Do not use one OperationId as both intent identity and all simulation-fact identities. One action can produce many projectiles/hits/AOE facts. Add distinct IntentId/OperationId, ActionExecutionId, FactId/EventSequence, and causal-parent/root identity.
3. Autonomous events without a live PlayerIntent need a first-class provenance root (AutonomousActionContext or equivalent), not a fabricated player intent.
4. Do not hard-code betrayal timing/policy from the intent-time DiplomacyRevision. Record authorization-time and decision-time relationship revisions and let explicit product policy decide how mid-flight diplomacy changes are treated.
5. Do not hard-code “mid-air alliance => no retroactive betrayal”, “offline AI targeting errors never betray”, or “direct targeted attack + DamageFact is sufficient”. These are product-policy Decision Requests unless directly fixed by canonical SRS.
6. Distinguish Tactical control authority from ADR-007 writer lease. Client pawn command authorization requires owner/controller assignment and Tactical control/session fencing; the Worker lease is not itself the player's command right.
7. A committed live RelationshipTransition must not be placed in ADR-003 PendingOperationQueue as if it were uncommitted state, nor rely on MaterializationManifest for mid-session delivery. Define a durable/replayable Session Domain Event / Outbox stream for already-committed domain events.
8. Worker fact dedupe must be by fact/event identity, not OperationId alone. Multiple legitimate facts under one action must survive.
9. Worker crash after physical execution but before fact report cannot simply mean “facts lost -> ABORTED”. If material outcome survives or can later be canonically published, required provenance/facts must be durably recoverable or the candidate must be rejected/quarantined as semantically incomplete.
10. Betrayal/domain transition commit must CAS against a scoped diplomacy/relationship aggregate revision; do not assume one global hot DiplomacyRevision unless intentionally designed.
11. Separate evidence records from canonical political state. PlayerIntent/SimulationFact/DamageFact may be durably journaled evidence, while BetrayalDecision/RelationshipTransition are canonical domain state transitions.
12. Define ordered/idempotent mid-session event ACK/replay semantics. Worker/client ACK may gate local projection readiness but never the Server's already-durable political commit.
Existing Canonical TBD-01..05 remain unchanged.
No runtime QA defect status changes.
Parallel:
- Sol continues focused Remote Presentation Hardening-04 E2 QA.
- A remains paused with the frozen presentation candidate and queued Production transaction slice.
- C receives ADR-005 v2 revision work.
44. MSR-033 Delta — ADR-005 Accepted
Source:
ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract_v2.md
Master decision:
ADR-005 — Intent / Betrayal / Domain-Simulation Event Contract = ACCEPTED (core contract).
Accepted core:
- Server-first authorization of untrusted CommandIntent;
- immutable AuthorizedActionEnvelope;
- separate IntentId / ActionExecutionId / FactId / causal identities;
- AutonomousActionContext for non-player-originated events;
- scoped diplomacy aggregate revisions rather than one mandatory global hot revision;
- product-policy separation for betrayal trigger timing/liability;
- durable politically relevant fact provenance tied to ADR-004 staged-result/event durability;
- ordered durable SessionDomainEventLog / domain outbox for already-committed mid-session political changes;
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
45. MSR-034 Delta — Open Decision Dependency Map Adopted with Master Corrections
Source:
Open_Decision_Dependency_Map_01.md
Master disposition:
ACCEPTED AS SEQUENCING BASELINE WITH MASTER CORRECTIONS
Key accepted findings:
- PIPELINE_PROBE_CAS is blocked by no open policy decision.
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
46. MSR-035 Delta — Remote Presentation Hardening-04 Independent QA
Source:
QA_Remote_Tactical_Presentation_Hardening_04.md
Master gate:
PARTIAL / REMAINING BLOCKER
Independent E2 findings adopted:
E2 proven
- actual OS/user Draft and native Go-here interaction reaches the adapter/RPC/Worker path;
- no speculative local final Draft/Goto commit before authoritative apply;
- foreign Pawn command remains rejected;
- Worker autonomous movement is repeatedly replicated;
- rendered Pawn Position/DrawPos follows authoritative movement;
- at least three distinct intermediate rendered positions were observed;
- final rendered position converges and actual click/selection resolves the moved Pawn;
- target-map binding, snapshot fencing, and four-direction rotation regressions remain intact;
- required privileged control commands are blocked on gameplay transport and accepted only through the PoC-local trusted control channel/capability.
Official defect updates
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
Remaining narrow presentation blocker
Interactive GUI command I/O is still synchronous on Unity thread:
GUI callback -> SendCommand -> socket ReadLine
A delayed Draft response of ~2 seconds caused a ~2.03 second main-thread frame freeze.
Periodic replication is independently improved:
- network wait off-main-thread;
- bounded one-in-flight periodic request;
- single-slot coalescing;
- 3.5s receive timeout;
- delayed/closed socket and stale late response fencing reproduced.
But this does not fix the interactive command path.
Additional candidate-local issues
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
- queued WP-PROD-TRANSACTION-PIPELINE-01 remains queued until the next focused presentation E2 result is reviewed.
- C continues G-Q8 decision brief analysis.
47. MSR-036 Delta — Hardening-04 QA Addendum / Dynamic Facing
Source:
QA_Remote_Tactical_Presentation_Hardening_04(1).md, Section 12 addendum.
Master disposition:
Addendum accepted. New defect QA-PRESENT-011 opened.
Overall Hardening-04 gate remains:
PARTIAL / REMAINING BLOCKER
New defect
QA-PRESENT-011 — Dynamic Facing / Authoritative Pose Staleness — OPEN / MEDIUM
Independent preserved-evidence review found:
- during a real westward Move, Worker snapshots retained Rotation=East through 84 consecutive Goto samples;
- during a later real eastward Move, Worker snapshots retained Rotation=West through 24 Goto samples;
- the Client correctly applied the received rotation, so this is not evidence of the previously-fixed East/West wire codec bug;
- the defect boundary is the Worker-side authoritative presentation pose/facing source or its engine update conditions.
Master interpretation:
- QA-PRESENT-005 remains CLOSED for 4-way rotation wire representation and round-trip.
- QA-PRESENT-011 is separate: whether the Worker emits semantically current facing/pose during movement/aim/stance.
- Do not blindly derive facing from position delta on the Client, because legitimate aim/focus/stance can intentionally differ from movement direction.
- Root cause is not yet fixed or fully classified; Worker movement vector/path-next-cell, stance/focus/aim target, native Rotation/body/head/render pose must be correlated first.
Impact on current A assignment
WP-REMOTE-PRESENTATION-HARDEN-04 is superseded by:
WP-REMOTE-PRESENTATION-HARDEN-04-REV1
REV1 retains all prior interactive-command async / epoch / queue / listener cleanup requirements and adds the narrow dynamic-facing investigation/fix.
Remote Tactical Production remains NOT AUTHORIZED.
Candidate C / ADR-002 remains PROVISIONALLY ACCEPTED.
48. MSR-037 Delta — G-Q8 Inventory Boundary Decision Brief Review
Source:
GQ8_Settlement_Inventory_Boundary_Decision_Brief_01.md
Master disposition:
DECISION BRIEF ACCEPTED AS ANALYSIS INPUT / G-Q8 REMAINS OPEN
The brief correctly identifies that:
- physical presence, custody, economic eligibility, and safe mutation are different concepts;
- nested ThingOwner / Pawn-bound / transfer-staging assets are materially riskier than simple fungible ground stock;
- runtime RimWorld 1.6 evidence is required before assuming engine-free mutation is safe across complex asset graphs;
- G-Q8 blocks inventory-dependent Production semantics, but not PIPELINE_PROBE_CAS.
Master corrections:
1. Do not define one universal set called "Settlement Inventory" for Auto-Shop, Tax seizure, tier/wealth projection, and canonical material custody.
2. Under G-Q8, distinguish at least:
   - SettlementEconomicInventory / sellable-fungible projection used by Auto-Shop availability;
   - TaxSeizableAssetSet used by forced tax collection;
   - underlying SettlementAssetGraph / canonical custody graph.
     These may overlap but are not required to be identical.
3. SRS tax eligibility for Pawn/Animal/Slave does not imply that equipped weapons/apparel are independently tax-seizable items or part of Auto-Shop inventory. That remains policy/engine semantics.
4. The brief is internally inconsistent where it marks equipped gear tax-eligible while later asking whether Pawn Tax means stripping gear or taking the Pawn entity. Treat that question as unresolved.
5. "Job-reserved items are safe offline because LocalTick is frozen" is not accepted. Frozen LocalClock prevents progression; it does not prove that saved Job/Reservation/Lord/reference graphs can be mutated engine-free.
6. ThingOwner/nested graph complexity and engine-hidden references mean direct XML node deletion is not an accepted production mutation strategy. Typed server operations may still require server-controlled RimWorld materialization/semantic application.
7. Projection aggregation may use fungible quantity keys without per-stack EntityId, but actual material application/cross-boundary transfer still needs an identity/rebinding strategy consistent with ADR-003.
8. A staged Tactical result is non-canonical. It does not own canonical custody merely because the blob exists. Pre-commit custody remains with the prior canonical owner until ADR-004 COMMITTED.
9. "Option C = zero tax evasion" is an overclaim; excluded/ambiguous asset classes and policy exemptions can still exist.
10. The brief's "minimum safe choice" is not adopted as policy. In particular, an Option-B-like economic inventory cannot by itself satisfy tax collection against Pawn/Animal/Slave categories; a broader TaxSeizableAssetSet may need engine-backed seizure.
G-Q8 status:
OPEN — RUNTIME PROOF + PRODUCT BOUNDARY DECISION REQUIRED
Current A sequencing unchanged:
- Remote Presentation Hardening-04 REV1 first;
- focused Sol E2;
- Production PIPELINE_PROBE_CAS next if presentation gate permits;
- G-Q8 runtime evidence is needed before first inventory-dependent Settlement mutation, not before the probe.
C is assigned a new task to identify the best first real non-inventory Settlement mutation candidate after the pipeline probe.
49. MSR-038 Delta — Remote Presentation Hardening-04 REV1 Developer Candidate
Source:
Remote_Tactical_Presentation_Hardening_04_REV1.md
Frozen candidate:
- DLL SHA256 55182E92E1E077181B3B944E4EA450F7623E47BCD45084E4FEB0ECD22BD34E3E
- Fixture SHA256 ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED
- Production WarEconomyMod/ reported unchanged by A
Master assessment:
E1 CANDIDATE FROZEN / INDEPENDENT E2 REQUIRED
A's self-classification ASYNC INTERACTIVE PRESENTATION PASS is not yet adopted.
A claims:
- interactive Draft/Move command socket I/O moved off Unity main thread;
- bounded command/result queues and command timeouts;
- transport-epoch fencing across reconnect;
- dynamic authoritative pose/facing generated by Worker;
- listener/profile argument syntax and runtime binds corrected;
- prior render/control/fencing behavior preserved.
Material evidence gaps / inconsistencies requiring E2:
1. The REV1 Work Order required actual north/south movement and at least one real direction change. A's report provides actual west/east movement but only a scripted North/South wire round-trip; no real north/south Goto or direction-change evidence is shown.
2. Several tests are labeled REAL_GRAPHICAL_OBSERVATION while their key observation cites direct native calls such as Find.Selector.Select() / TryTakeOrderedJob. These cannot substitute for actual OS/user input.
3. screen_05_destination_reached.png and screen_06_foreign_pawn_rejected.png have the same reported byte size and identical SHA256, so they cannot be accepted as two independent visual states.
4. The report claims a 2-second delayed Draft eventually applies successfully while also reporting an 800 ms command receive timeout. The per-test timeout configuration/state transition is not explained and must be independently resolved.
5. Dynamic pose code prioritizes pather.Moving before Stance_Busy aiming. This may be correct for the tested case, but moving+aim/focus semantics are not independently demonstrated and must not be inferred from stationary tests.
6. A's QA-PRESENT-011 CLOSED claim is developer-only. Official status remains OPEN pending E2 actual movement/pose verification.
7. A's QA-PRESENT-007 and QA-PRESENT-009 closure claims are not adopted pending E2 fault/profile verification.
8. Queue caps must be proven under load; a bounded design claim is not sufficient without overflow/high-water behavior.
Official defect statuses remain unchanged from QDL-034 until Sol verification:
- QA-PRESENT-004 — PARTIAL
- QA-PRESENT-006 — CLOSED
- QA-PRESENT-007 — STILL FAILING
- QA-PRESENT-008 — PARTIAL
- QA-PRESENT-009 — PARTIAL
- QA-PRESENT-011 — OPEN
Next:
- Sol assigned WP-QA-REMOTE-PRESENTATION-HARDEN-05.
- A must not modify/rebuild the frozen presentation candidate while Sol verifies it.
- queued Production WP-PROD-TRANSACTION-PIPELINE-01 remains not started until Master reviews the E2 result.
- C continues WP-FIRST-REAL-SETTLEMENT-MUTATION-CANDIDATE-01.
50. MSR-039 Delta — First Real Settlement/Domain Mutation Candidate Selected
Source:
First_Real_Settlement_Mutation_Candidate_01.md
Master disposition:
RECOMMENDED NEXT REAL DOMAIN MUTATION ACCEPTED WITH CORRECTIONS
NO IMPLEMENTATION AUTHORIZATION YET
Selected next real mutation after PIPELINE_PROBE_CAS:
Auto-Shop Trade Configuration Update (Setup Phase)
Controlling scope:
- persistent per-Settlement Auto-Shop order/config metadata;
- Buy/Sell order declaration only;
- no inventory reservation;
- no Silver reservation;
- no actual trade execution;
- no Settlement material artifact mutation;
- no CommittedSettlementStateRevision advance;
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
1. C's recommendation is accepted as the best current next real domain mutation, not as the only theoretically safe candidate.
2. C's elimination analysis overstates blockers:
   - basic Caravan custody ingress/egress is not categorically blocked by G-Q1/G-Q12a/b;
   - generic Occupy/Destroy is not categorically blocked by TBD-01/TBD-02.
     These earlier Master dependency corrections remain controlling.
3. Use a dedicated canonical TradeConfigurationRevision (or equivalently named AutoShopConfig aggregate revision), not CommittedSettlementStateRevision and not an ambiguous catch-all SettlementMetadataRevision.
4. Every mutation binds expected Settlement ownership identity/epoch and re-authorizes at commit. This prevents a former owner from committing a stale order update across an Occupy/ownership race without deciding G-Q9.
5. G-Q9 remains open: this slice does not decide whether existing orders persist/reset/suspend when ownership changes.
6. G-Q8 remains open: FR-204+ actual available quantity, FR-205 actual Silver, FR-206+ execution, and inventory effects are outside this slice.
7. Content-profile validation applies to referenced gameplay definitions/selectors. The backend must not silently lock future FR-200 UI semantics to an unnecessarily narrow DTO solely for this slice.
8. No arbitrary economic price min/max may be introduced contrary to FR-201/BR-019. Structural serialization/overflow validation is still allowed.
9. Outbox/UI notification may be implemented as derived delivery, but full final Auto-Shop UI is not required by this backend slice.
Sequencing:
- A: frozen Remote Presentation REV1 candidate under Sol Hardening-05 E2.
- After Master reviews Sol: A begins WP-PROD-TRANSACTION-PIPELINE-01.
- Only after Pipeline Slice-01 achieves the required E2 gate may the queued Trade Configuration Production slice begin.
- C proceeds to G-Q1 ordinary multi-settlement topology decision brief.
Remote Tactical Production remains NOT AUTHORIZED.
51. MSR-040 Delta — G-Q1 Ordinary Multi-Settlement Topology Brief Review
Source:
GQ1_Ordinary_MultiSettlement_Topology_Decision_Brief_01.md
Master disposition:
DECISION BRIEF ACCEPTED AS ANALYSIS INPUT / G-Q1 REMAINS OPEN
Classification: RUNTIME PROOF FIRST / DEFER BEHIND LEASE-MATERIALIZATION INTERFACES
Accepted findings:
- Canonical SRS permits multiple Settlement ownership, but does not require multiple divergent LocalClock settlements to simulate concurrently inside one client process.
- ADR-006A one-active-LocalClock-per-execution-island remains controlling.
- ADR-007 per-Settlement WriterLease/Fencing boundary is the correct stable deferral interface.
- PIPELINE_PROBE_CAS and TradeConfiguration domain mutation do not require G-Q1 resolution.
Master corrections:
1. Candidate 1 Single Active Materialization does not have proven "absolute isolation". Sequential materialization may still leak global singleton/cache state. This is an engine-proof obligation.
2. Candidate 4 Hybrid Lazy Materialization is not yet "high feasibility" or "seamless". It is a promising architecture direction only after sequential unload/rematerialize, server-authored offline delta, and Tactical handoff are proven.
3. G-Q1 is not a pure product-policy question. It combines:
   - product UX choice;
   - RimWorld 1.6 engine/process feasibility;
   - temporal isolation;
   - lease/materialization recovery architecture.
4. Candidate 3 Server-Hosted Ordinary Workers is inconsistent with the currently accepted owner-client ordinary-writer architecture and prior SRS interpretation, but should be classified as an architecture fallback requiring explicit ADR/SRS-direction change rather than dismissed only by prose.
5. Multiple Local Islands must distinguish operator/server-hosted processes from user-owned local processes; G-Q2 trust differs materially between them.
6. A 1:1 SettlementId -> active WriterLeaseId registry does not mean one client may safely hold arbitrarily many active leases. Admission policy remains G-Q1 and runtime-evidence dependent.
7. Tactical admission for an inactive settlement must use the last committed canonical head and server-controlled materialization; it must not depend on waking the owner's inactive local artifact.
8. Cross-island caravan custody is not required to decide the ordinary topology itself; it is useful integration evidence but should not be the first G-Q1 probe.
Current G-Q1 status:
OPEN — ENGINE/PROCESS FEASIBILITY EVIDENCE REQUIRED BEFORE CLIENT-INTEGRATION TOPOLOGY FREEZE
Preferred first proof sequence:
A. sequentially materialize two settlement artifacts with intentionally divergent LocalClockIds in one client/runtime, with hard unload between them;
B. prove no foreign clock/global singleton/cache contamination;
C. prove lease revoke/fence and re-materialization on switch/crash;
D. only then compare separate-process simultaneous islands.
No topology is selected by this review.
Current program sequencing unchanged:
- Sol: Remote Presentation Hardening-05 E2
- A: frozen presentation candidate, then WP-PROD-TRANSACTION-PIPELINE-01
- after pipeline gate: queued TradeConfiguration Production slice
- G-Q1 runtime probe is queued before ordinary multi-settlement Client Integration, not on the current transaction critical path
- C proceeds to G-Q2 ordinary-client trust decision brief
52. MSR-041 Delta — Remote Presentation Hardening-05 E2 and Production Pipeline Release
Source:
QA_Remote_Tactical_Presentation_Hardening_05.md
Master verdict:
PARTIAL / REMAINING BLOCKER — ADOPTED
E2 now independently proven
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
Defect status changes
- QA-PRESENT-004 — STILL FAILING overall
  - narrow rendered Position/DrawPos/hit-target sub-scope remains resolved;
  - general health/body-part/job reconciliation remains unresolved.
- QA-PRESENT-007 — PARTIAL
  - ordinary GUI command socket I/O / receive path is now E2-proven off-main and responsive in the tested fault window;
  - remaining transport lifecycle blockers:
    - H05-01 HIGH: response parsed from an old connection can be relabeled with the current TransportEpoch before coalescing and then applied after reconnect;
    - H05-02 MEDIUM: _cmdResultQueue is not actually bounded/backpressured;
    - H05-03 MEDIUM: initial/external reconnect still performs synchronous TcpClient.Connect on the main thread and has no explicit bounded connect deadline.
- QA-PRESENT-008 — STILL FAILING
  - A evidence manifest contains duplicated screenshot evidence and several metric/source/evidence-classification inaccuracies.
- QA-PRESENT-009 — CLOSED for the narrow listener/profile subdefect
  - declared -flag=value ports are consumed;
  - candidate-related bind collisions were not observed;
  - this does not close QA-ENGINE-002/headless semantic-load concerns.
- QA-PRESENT-011 — CLOSED for the tested movement/focus pose slice
  - actual four-direction movement, direction changes, 93 matched pose samples and moving+focus behavior independently verified.
- QA-PRESENT-001/002/003/005/006/010 remain CLOSED.
Important corrections adopted
- A's report description of a movement-first DetermineAuthoritativeFacing() does not match the frozen source. Actual frozen source is focus-first, consistent with the tested engine behavior.
- A's claimed 800 ms general command timeout is incorrect. Native adapter tests used a 4000 ms timeout; the 800 ms case was an explicitly configured test.
- A's reported 280-byte interactive payload is not representative of actual GUI replies; independent GUI replies carried full ~22.6 KB Pawn-set snapshots.
- two A screenshot files advertised as independent evidence are byte-identical.
- endpoint ownership labels in A's report require correction.
Architecture status
- P2 presentation actual async Draft/Move interaction is E2-feasible.
- Candidate C / ADR-002 remains PROVISIONALLY ACCEPTED.
- Remote Tactical Production remains NOT AUTHORIZED.
- presentation transport lifecycle still requires a narrow repair and focused reverify before the narrow P2 gate can be fully closed.
Program sequencing decision
The remaining presentation blockers are now isolated to the Remote Tactical presentation transport/evidence scope and no longer justify serially blocking the independent Shared Settlement transaction substrate.
Therefore:
WP-PROD-TRANSACTION-PIPELINE-01 = AUTHORIZED TO START NOW.
A must:
- leave the frozen Remote Presentation candidate untouched;
- implement the Production transaction probe only in the authorized WarEconomyMod/ scope;
- freeze/report that candidate before returning to presentation transport repair.
Remote presentation transport repair is queued after the pipeline candidate is frozen.
C continues WP-GQ2-ORDINARY-TRUST-BRIEF-01.
Remote Tactical Production remains blocked regardless of the Production transaction slice.
53. MSR-042 Delta — G-Q2 Ordinary Client Trust Brief Review
Source:
GQ2_Ordinary_Client_Trust_Decision_Brief_01.md
Master disposition:
DECISION BRIEF ACCEPTED WITH CORRECTIONS / G-Q2 REMAINS OPEN
Accepted:
- owner-client checkpoint/materialization remains hostile/untrusted input despite authenticated WriterLease;
- structural/semantic engine validity does not establish legitimate provenance;
- identity/lease/fencing, revision lineage, profile/schema compatibility, EntityId/custody integrity are mandatory invariants, not optional anti-cheat policy;
- G-Q2 does not block PIPELINE_PROBE_CAS or server-authored TradeConfiguration metadata mutation;
- G-Q2 must be resolved before hostile ordinary-client material publication is Production-approved.
Master corrections:
1. ContentProfileFingerprint proves the artifact uses an admitted content universe/version/load order; it does NOT prove that an admitted cheap ThingDef was not maliciously replaced with another admitted expensive ThingDef. Same-profile semantic substitution remains a provenance/plausibility problem.
2. CheckpointParentRevision rejects stale lineage but does NOT detect arbitrary offline edits made on top of the current valid parent revision. Current-parent forged state remains the central G-Q2 vulnerability.
3. EntityId duplication must fail closed with explicit validation/quarantine; a validator crash is not acceptable evidence of correct rejection.
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
Layered Trust, not one global Posture.
- Layer A: mandatory hard invariants.
- Layer B: server-authored typed operations / protected domain state where feasible.
- Layer C: semantic validation of engine materialization.
- Layer D: selective plausibility/provenance controls for high-impact client-authored state.
- Layer E: audit/admin response.
No final thresholds or anomaly policy selected.
C next:
prepare G-Q6 checkpoint-loss/disconnect-grace decision brief, because it directly interacts with ADR-007 writer lease lifecycle but can remain behind configurable policy.
54. MSR-043 Delta — Production Midpoint Architecture Checkpoint
Trigger:
A submitted Production_Transaction_Pipeline_Slice_01.md with developer classification:
E1 PIPELINE PROBE PASS
Master disposition:
E1 DEVELOPER EVIDENCE ACCEPTED / PRODUCTION CANDIDATE FROZEN / E2 REQUIRED
This is the first implemented Production persistence/transaction substrate in WarEconomyMod/.
Reported candidate:
- internal operation PIPELINE_PROBE_CAS
- SQLite-backed operation journal / PREPARED / COMMITTED / PUBLISHED lifecycle
- ProbeRevision CAS
- commit receipt
- audit
- durable outbox
- recovery reconciler
- hard-process crash evidence
- gameplay transport isolation
- no Settlement material mutation
- no CommittedSettlementStateRevision increment
- no ArtifactBaseStateRevision mutation
- no EntityId transfer
- no Tax/Trade/Auto-Shop execution/Tactical integration.
Master checkpoint:
Do not start the queued first real gameplay mutation yet.
Before WP-PROD-TRADE-CONFIG-01 can be released:
1. Sol must independently attack/verify the Pipeline Slice-01 candidate (E2).
2. A high-level independent architecture red-team review will be requested from the user-selected external reviewer.
3. Master will reconcile both reviews into a midpoint plan/gate.
Specific E2 concerns from report inspection:
- verify the idempotency/collision fingerprint includes every semantically material request field, not only PayloadJson; ProbeScopeId, expected revision, actor/principal, operation type, content/profile binding must not be silently ignored when an OperationId is reused;
- verify exact SQLite synchronous policy used for canonical commit; NORMAL vs FULL must not be ambiguous;
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