# MASTER_DECISION_LOG.md

Project: WarEconomy / RimMulti
Decision Log Revision: MDR-067
Date: 2026-10-02

> Append-only summary of Master-level decisions.
> The detailed source evidence remains in ADR/PoC/QA reports.

## MD-001 — Canonical Requirement Authority
Decision:
`요구사항_명세서.md` is the highest-authority SRS.
Only IDs from the root SRS are Canonical.

Consequence:
Lower requirement documents may reuse FR/BR/NFR IDs but do not redefine Canonical IDs.

## MD-002 — Official Gap Baseline v1
Decision:
Official Gap Baseline v1 adopted.

Consequence:
QA-001..QA-014 remain OPEN unless explicitly closed by Master after evidence.

## MD-003 — ADR-001 Accepted
Decision:
ADR-001 Authenticated Identity / Central Authority / Persistent State = ACCEPTED.

Key consequences:
- Server final Domain Authority
- SessionEpoch fencing
- authenticated mutation only
- durable persistence/revisions/idempotency
- Domain Authority != Simulation Authority

## MD-004 — Candidate C Selected as Tactical Primary Target
Decision:
Candidate C — Trusted Tactical Worker Always — selected as the primary tactical architecture target.

Status:
ADR-002 only PROVISIONALLY ACCEPTED.

Reason:
Actual RimWorld Worker feasibility needed runtime validation.

## MD-005 — POC-TAC-ENGINE-01 Master Gate
Decision:
Basic engine feasibility accepted within tested scope.
ADR-002 remains PROVISIONALLY ACCEPTED.

Reason:
Actual RimWorld process could load, tick, save, and fresh-reload, but independent QA exposed non-target/world progression and dependency-safety gaps.

## MD-006 — ENGINE-02 Independent QA Gate
Decision:
ENGINE-02 = FAIL.
ADR-002 remains PROVISIONALLY ACCEPTED.
Candidate C remains primary target.
Production Tactical and Remote Tactical remain blocked.

Reason:
Independent QA reproduced:
- undeclared dependency semantic loss reaching READY/SAVED
- unsafe long RUN_TICKS starvation
- frozen-map/global-time leakage
- global dispatch escape
- load-before-fence mutation
- fixture/oracle weaknesses

## MD-007 — Full Worker Save Publication Constraint
Decision:
A Worker-produced full `.rws` must NOT automatically be treated as canonical post-tactical state.

Reason:
Independent QA showed fresh load/export/reload can mutate non-target Map and worker-local World state.

Implication:
Architecture must choose between:
- safe full-save rebase/virtualization, or
- Target-Scoped Outcome Publication / Canonical Merge, or
- another validated alternative.

## MD-008 — Prototype Policy
Decision:
Prototype creation is not a project goal.

Rule:
Use PoCs only when a material architecture/engine uncertainty cannot be resolved by existing evidence, static analysis, or normal implementation/testing.

## MD-009 — Production Gate Policy
Decision:
There is no single global Production ON/OFF switch.

Rule:
A Production Work Package may begin only if it does not require an unresolved ADR/TBD decision to be guessed.

## MD-010 — Agent Operating Model
Decision:
Five-agent structure adopted.

Roles:
- Master: GPT-5.6 Sol
- Dev A: Gemini 3.8 Flash
- Verification B: Gemini 3.1 Pro
- Final QA: GPT-6.1 Sol
- Analysis C: Gemini 3.1 Pro Web

## MD-011 — Project Memory Model
Decision:
Project state is stored in persistent project documents, not only in chat context.

Core memory files:
- MASTER_PROJECT_STATE.md
- MASTER_DECISION_LOG.md
- QA_DEFECT_LEDGER.md

The Canonical SRS remains authoritative and must be re-provided when exact requirement wording is needed.

## MD-012 — Dev A Tactical Worker Hardening Submission
Decision:
`WP-TAC-WORKER-HARDEN-01` is accepted as **developer evidence only**, not as defect closure.

Consequences:
- QA-ENGINE-002/003/005/006/007/008 remain officially OPEN pending independent Verification B / Sol evidence.
- QA-ENGINE-004 remains OPEN and belongs to ADR-006A temporal architecture.
- ADR-002 remains PROVISIONALLY ACCEPTED, not rejected and not accepted.
- Verification B must run the corrected regression suite against the exact hardened scratch implementation.

Special review item:
Dev A's dispatch inventory retains some World/global paths (`World.WorldTick`, `WorldObjectsHolder.WorldObjectsTick`, `FactionManagerTick`, etc.). This may conflict with the stated temporal-policy freeze and must be independently verified before any gate change.

## MD-013 — ADR-006A Temporal Authority Accepted
Decision:
`ADR-006A — Temporal Authority` = **ACCEPTED**.

Primary architecture:
**B2 — full engine context for reference resolution + one active local-clock execution island + target-scoped simulation + Target-Scoped Outcome Publication / Canonical Merge.**

Accepted invariants:
- `W`, `L_s`, engine `G`, and monotonic `M` are distinct.
- Tactical time continues target `L_s`; it is not a separate canonical date.
- Offline ordinary settlement simulation has `ΔL=0`.
- one LocalClockId → at most one active writer.
- full Worker `.rws` is private checkpoint/extraction input, not whole-world canonical replacement.
- unknown/ambiguous temporal state fails closed rather than being blanket-rebased.
- load must be fenced before autonomous ticks and READY requires semantic/temporal validation.
- World deadlines are server-W authority.
- authorized offline asset operations may occur with `ΔL=0`.

Master policy decisions:
1. Settlement-resident chronological and biological aging follow authorized residence/local simulation; frozen ordinary settlements do not age merely because Worker/global `G` or server `W` advanced.
2. Tactical participants progress/age on the target settlement's local/tactical timeline.
3. Cross-local-domain movement preserves current age/duration and reprojects native anchors; local-date differences do not create catch-up debt.
4. Server process downtime: `ΔW=0`; resume from the last durable committed `W`.
5. Transit physiology is not implicitly driven by raw `W`; an explicit transit/residence clock policy is required before that subsystem is implemented.
6. Multiple simultaneously active divergent LocalClocks require separate execution islands or a separately validated virtualization mechanism.

Gate consequence:
ADR-006A acceptance is an architecture decision only. It does NOT close QA-ENGINE-004 or authorize Production Tactical. ADR-002 remains PROVISIONALLY ACCEPTED pending implementation/verification of the temporal/publication boundary.

## MD-014 — Temporary Verification Fallback While Gemini B Is Unavailable
Decision:
Gemini B's interrupted `WP-VERIFY-TAC-BOUNDARY-02` is treated as **NO VERDICT / NO ACCEPTED EVIDENCE**.

Temporary workflow:
1. Gemini A freezes the exact hardened scratch implementation and self-regression artifacts.
2. GPT-6.1 Sol independently runs/adapts the verification plan against that exact frozen revision.
3. Gemini C may reconcile Dev-vs-QA claims and requirement implications.
4. Master alone closes defects / changes ADR-002 Gate.

Controls:
- A's self-tests cannot close QA defects.
- Sol must independently reproduce material claims and run adversarial/negative cases, not merely review A's report.
- If A changes code after Sol starts, that result applies only to the old revision.
- When B becomes available again, B resumes as Verification/Test Engineer for later regression work; no permanent role removal is implied.

## MD-015 — Standalone ADR Artifact Requirement
Decision:
Every ADR with status ACCEPTED or PROVISIONALLY ACCEPTED must exist as a standalone project artifact.

Current formal artifacts created:
- ADR-001 — reconstructed from previously accepted Master decision
- ADR-002 — reconstructed from provisional Master decision and QA history
- ADR-006A — finalized accepted version from Sol proposal + Master decisions

This is documentation formalization only; it does not change architecture statuses.

## MD-016 — Architecture Plan Revised After External Red-Team Summary
Decision:
The project architecture plan is revised based on material gaps identified by an external Claude Opus 5.5 review summary.

Accepted plan changes:
1. Future ADR-003 is broadened from `Canonical Inventory / Save Provenance` to:
   **Canonical Settlement State / Entity Identity / Save Provenance**.
2. Add future:
   **ADR-007 — Ordinary Settlement Simulation Authority / Multi-Settlement Execution Topology**.
3. ADR-003 must define the canonical Settlement-state unit, stable cross-process entity identity, ordinary/Tactical/save provenance, and the shared mutation interface used by trade/tax/Tactical.
4. ADR-007 must define ordinary writer authority, divergent LocalClock topology, ordinary<->Tactical handoff, online reconciliation, and transit/residence-clock behavior.
5. ADR-004 remains the durable distributed commit/repair layer over the write-set defined upstream.
6. B2 remains the accepted primary architecture direction from ADR-006A, but its merge granularity is still an implementation-architecture decision. A coarse-grained whole-target snapshot + typed cross-boundary operation model must be analyzed before any field-level merge design is accepted.
7. Remote Tactical control/rendering is a mandatory validation before ADR-002 final acceptance. It is not started until the current frozen Worker candidate completes Sol independent verification, to avoid moving the QA target.

Not accepted as an immediate action:
- starting a new remote-play PoC while the current Worker candidate is frozen for independent QA.

Reason:
Preserve verification integrity while still recognizing Remote Tactical as an unresolved critical capability.

## MD-017 — Full ARCH-REDTEAM-REVIEW-001 Master Disposition

Source:
External `ARCH_REDTEAM_REVIEW_001.md`, reviewed in full. Reviewer did not inspect code or rerun evidence; findings are architecture review input, not independent runtime QA.

### Ratifications and interpretations

1. ADR-001 and ADR-002 reconstructed standalone files are explicitly re-ratified as the authoritative current texts for those ADRs.
2. SRS §4.2 `Client = Settlement Local Simulation / RimWorld Map` is interpreted as simulation placement/responsibility, not final domain/canonical-state authority. ADR-001 server-final authority remains controlling.
3. SRS §77 historical `Map Owner Authoritative` preference is superseded by ADR-002 Candidate C for the current architecture. The supersession is architectural, not a reduction of offline-combat requirements.
4. B2 remains accepted as the primary ADR-006A direction, but acceptance is conditional on feasibility gates; downstream work must not treat it as unfalsifiable.

### B2 falsification criteria

Reopen ADR-006A/B2 if any of the following is demonstrated for the supported vanilla+DLC+approved-mod profile:
- an engine-generated target graph cannot be extracted/re-materialized without semantic loss;
- safe publication requires general field-by-field reconciliation of arbitrary RimWorld/mod objects outside an engine;
- cross-process entity identity cannot be made collision-safe and reference-stable;
- a closed Global State Disposition Table cannot be established for approved content;
- required foreign/global reads causally contaminate target results in a way that cannot be projected/fenced;
- Remote Tactical presentation/control cannot meet functional/latency requirements under Candidate C;
- external settlement operations cannot be serialized or safely represented without violating canonical requirements.

### Architecture changes

5. ADR-003 scope remains broadened to `Canonical Settlement State / Entity Identity / Save Provenance`.
6. ADR-007 remains `Ordinary Settlement Simulation Authority / Multi-Settlement Execution Topology`.
7. Add ADR-008 `Shared World Layer / Transit / World Projection`.
8. Rename ADR-006B to `Configuration & Content Manifest`.
9. ADR-002 must be amended before final acceptance to include:
   - Tactical Replication & Client Presentation,
   - client/Worker generation fencing,
   - mid-session Domain↔Simulation event contract.

### B2 merge granularity direction

10. Default analysis target is **B2-lite**:
    - immutable engine-produced whole target Settlement/Map artifact,
    - one exclusive writer/asset lease during material simulation,
    - small server-maintained index/projection,
    - ordered typed cross-boundary operations/delta journal.
    Arbitrary field-level merge is not the default architecture.

### Trust/content

11. Owner-client checkpoints are untrusted input even when the owner holds a valid writer lease.
12. Server-pinned gameplay content manifest is required. Cosmetic client-only mods may be permitted only if allowlisted and proven not to participate in serialization/simulation/state.
13. Content/game updates on an existing world require an explicit migration gate and artifact compatibility plan.

### Sequencing

14. Finish Sol QA on the frozen Worker candidate first.
15. After that, run Remote Tactical Presentation validation as a mandatory Candidate-C falsification gate, in parallel with ADR-003/ADR-007 analysis.
16. Build a shared Settlement State Pipeline before both Economy and full Tactical Production.
17. Recovery/failure injection is a per-phase exit criterion, not an end-only hardening phase.

## MD-018 — Frozen Worker Hardening Independent QA Gate

Decision:
Accept GPT-6.1 Sol's `QA_Tactical_Worker_Hardening_Independent_Review.md` as the independent QA result for the exact frozen `WP-TAC-WORKER-HARDEN-01` revision.

Master Gate:
- exact candidate overall hardening gate = FAIL
- Architecture Gate = BLOCKED BY ARCHITECTURE
- ADR-002 = PROVISIONALLY ACCEPTED
- Production Tactical / Remote Tactical Production = NOT AUTHORIZED

Defect decisions:
1. QA-ENGINE-007 = CLOSED.
   Scope of closure: mechanical pre-load autonomous tick fence through READY on the verified candidate/profile. Semantic/temporal READY validity remains covered by QA-ENGINE-002/004/005 and is not implied by this closure.
2. QA-ENGINE-008 = CLOSED.
   Scope of closure: pre-START elapsed wall-time debt/catch-up burst across load/export/idle/pause/cancel cases on the verified candidate/profile.
3. QA-ENGINE-002 = OPEN / STILL FAILING.
4. QA-ENGINE-003 = OPEN / PARTIAL.
5. QA-ENGINE-004 = OPEN / STILL FAILING.
6. QA-ENGINE-005 = OPEN / STILL FAILING.
7. QA-ENGINE-006 = OPEN / STILL FAILING.

Implementation sequencing:
- A may immediately address 002, 003, 006 and bounded implementation-safe portions of 005.
- 007/008 become locked regression requirements.
- A must not invent the final QA-ENGINE-004 temporal/B2 publication contract or broad GameComponent/global-state policy before ADR-003/007/008/006B settle the relevant authority boundaries.

## MD-019 — Master Disposition of C State/Ordinary Authority Brief

Source:
`Decision Brief_Canonical_State_and_Ordinary_Authority.md`

### Accepted now

1. ADR-003 scope:
   `Canonical Settlement State / Entity Identity / Save Provenance`.

2. B2-lite becomes the **default architecture baseline** under existing falsification rules:
   - whole engine-produced target Settlement/Map artifact as the coarse canonical material-state unit;
   - exclusive writer/asset lease while an engine process owns material simulation;
   - small server index/projection rather than a complete external RimWorld object model;
   - typed cross-boundary operations/delta journal for ingress, egress, ownership and queued external mutations.

3. Arbitrary field-level concurrent merge is not the default architecture.

4. G-Q3 decision:
   During an active Tactical material-state lease, target-settlement Auto Shop and Tax mutations are **queued**, not applied concurrently into the live Worker graph.
   After Tactical publication:
   - queued operations are revalidated against the new canonical revision/index;
   - valid operations are applied in order;
   - invalid operations fail/compensate according to the eventual ADR-003/004 contract.
   This is interpreted as consistent with the SRS because the SRS requires online/offline capability but does not require one-tick concurrent settlement mutation during an active battle.

5. Client checkpoint/save data is untrusted input.
   A valid writer lease grants the right to propose ordinary simulation progress, not the right to bypass content/schema/type/plausibility validation.

6. Stable cross-process EntityId and canonical Faction registry are mandatory before B2 publication/ownership transfer can be Production-safe.

### Deferred / decision request remains open

- G-Q1: multi-settlement clock topology.
- G-Q2: ordinary simulation trust/anti-cheat posture.
- G-Q4: Worker crash rollback/checkpoint semantics.
- G-Q6: ordinary progress-loss/checkpoint cadence/grace policy.
- G-Q8: exact Settlement Inventory scope and complex tax-delivery semantics.
- G-Q9: Auto Shop state after Occupy.
- G-Q10: owner UX under Candidate C, pending actual Remote Tactical evidence.
- G-Q5/Q5b: mid-session world/domain events and storyteller policy, to ADR-002 amendment + ADR-005.

### Governance

These deferred questions are not new Canonical TBD IDs.
Implementation must not silently encode an answer.

## MD-020 — ADR-003 / ADR-007 Draft-1 Not Yet Accepted

Decision:
Both C-authored Draft-1 ADRs are useful but require revision before Master acceptance.

### ADR-007 corrections

- Canonical custody / leased writer direction accepted.
- Handoff order must be:
  `freeze/barrier current writer -> receive candidate final checkpoint under current lease -> validate+commit -> revoke/fence -> grant next lease`.
- A disconnected/unresponsive client cannot be required to provide a final checkpoint. Fallback is the last committed canonical head.
- `WriterLeaseId/FencingToken` is a monotonic server-issued fencing generation; it may be accompanied by an authenticated capability but is not defined as "cryptographic or monotonic".
- SessionEpoch and Worker generation are referenced by the lease but are not collapsed into one identifier.
- G-Q6 remains open; server-side fencing is authoritative even if a stale client continues local simulation.
- G-Q1 must include Separate Execution Islands as an option.

### ADR-003 corrections

- Do not state that the canonical target artifact is necessarily a target-only `.rws`. The logical canonical unit is an immutable engine-produced Settlement materialization artifact/package. Current native full `.rws` is private execution/checkpoint input unless a validated target extraction/package format exists.
- Projection/index must be durable and recomputable/verifiable from canonical artifact + committed operations.
- Distinguish:
  `Committed SettlementStateRevision`
  from
  `Pending queued operations`.
  Pending Tactical-time shop/tax requests do not move the canonical head before they are revalidated and committed.
- Preserve B2-lite granularity: do not require per-Thing split/merge/destroy journaling for all internal map mutations. Canonical EntityId applies to entities that are server-addressable, cross-boundary, or externally referenced across canonical boundaries.
- Identity contract is accepted; concrete native binding mechanism remains implementation/PoC-dependent.
- Client artifact validation must include typed semantic integrity and provenance/plausibility checks; XML schema validity alone is insufficient.

Status:
- ADR-003: PROPOSED / REVISION REQUIRED
- ADR-007: PROPOSED / REVISION REQUIRED

## MD-021 — Remote Tactical Presentation PoC-01 Master Gate

Decision:
A's `POC_Remote_Tactical_Presentation_01.md` is accepted as **developer feasibility evidence**, not independent QA.

Gate:
- Remote Tactical Presentation PoC-01 = STRONG CONDITIONAL PASS
- Candidate C = PROVISIONALLY ACCEPTED remains
- Candidate P2 Mirrored Client Map = PRIMARY PRESENTATION CANDIDATE
- Remote Tactical Production = NOT AUTHORIZED

Accepted architectural direction:
1. Worker remains authoritative Simulation Authority for the Tactical execution island.
2. Presentation client may maintain a non-authoritative RimWorld mirror for rendering/inspection/input surfaces.
3. Client autonomous simulation does not grant authority; state must be reconciled from Worker-authoritative results.
4. Commands must be authorized/fenced at the Worker/server-issued session boundary.
5. Domain Authority remains Dedicated Server final commit.

Corrections to A's proposed amendment:
- `Dialog_Trade`, recruitment, arrest, social actions, etc. are not classified solely by UI name.
  Each operation must separate:
  (a) physical/simulation facts that may be produced by the Worker,
  (b) domain/economic/ownership/faction effects that require Server authority.
- Do not prescribe "two-phase commit" in ADR-002. Exact commit/repair mechanics belong ADR-003/004.
- Host player ownership does not imply authority over canonical inventory; canonical custody remains Server-side.

Evidence limitation:
The PoC presentation client used `-batchmode -nographics`. Claims of actual rendered frame rate, visual smoothness, real OnGUI usability, and human interaction are not independently established by this run.
Localhost RTT cannot be extrapolated into an accepted WAN SLO.

Required next gate:
Independent QA must run the frozen PoC artifacts and include a normal graphical presentation-client path (no `-batchmode -nographics` on the client) or equivalent direct evidence that the actual render/UI lifecycle works.


## MD-022 — ADR-003 / ADR-007 v2 Requires Final Contract Revision

Decision:
Do not accept ADR-003 or ADR-007 v2 yet.

Accepted improvements:
- Draft-1 handoff/fencing/revision/artifact/entity-scope corrections are directionally accepted.
- B2-lite baseline remains unchanged.
- Open G-Q1/G-Q2/G-Q6 decisions remain open.

Required final contract corrections:

### Canonical operation layers
Define three distinct layers:
1. `PendingOperationQueue`: uncommitted intents; does not move canonical revision and never enters a canonical materialization package.
2. `CommittedOperationLog`: durable canonical operations committed after an artifact's base revision but not necessarily folded into a new artifact.
3. `MaterializationManifest`: deterministic instructions generated from the current canonical artifact base + committed unapplied operations + explicitly admitted ingress/context.

### Artifact replay watermark
Every immutable Settlement artifact must declare the committed state revision it already contains (`ArtifactBaseStateRevision` or equivalent).
Materialization applies only committed operations after that watermark, preventing double application or omission.

### Online ordinary economic mutation
ADR-003/007 must define a serialization/barrier model for Server-authored material deltas while an owner client holds the ordinary writer lease.
A server commit may not silently make the client's next fast-forward checkpoint stale without a defined rebase/apply protocol.

Preferred architecture direction for drafting:
`server operation intent -> writer delta barrier -> authoritative operation commit/order -> client applies required delta -> lease base revision/watermark advances -> ordinary simulation resumes`.
The exact failure/compensation commit mechanics remain ADR-004 responsibility.

### Lease state machine
ADR-007 must explicitly define:
`UNLEASED -> LEASED_CLIENT | LEASED_WORKER -> DELTA_BARRIER or HANDOFF_BARRIER -> lease/resume or next lease`.

During a barrier:
- no ordinary checkpoint except the designated barrier candidate may commit;
- no second material writer may be granted;
- failure must fall back to a known committed head.

### Identity binding
Canonical `EntityId` is globally stable.
Native RimWorld `loadID` is execution-context-local and may be rebound during materialization if:
- mapping is unique within the materialization,
- all references are consistently rewritten/resolved,
- no collision or identity aliasing occurs.
Cross-boundary operations reference canonical EntityId, never native loadID.

### Semantic validation placement
Client artifacts remain hostile.
Static validation may happen on Dedicated Server, while RimWorld-specific semantic validation may execute in a server-controlled sandbox/validation Worker before canonical acceptance.
This does not grant that Worker canonical commit authority.


## MD-023 — ADR-003 Accepted

Decision:
Accept ADR-003 v3 as the authoritative architecture for Canonical Settlement State / Entity Identity / Save Provenance, with one Master clarification incorporated into the accepted artifact.

Controlling clarification:
- A Server-authored operation that has passed authorization and durable commit is canonical even if the ordinary client disconnects before applying it.
- Client ACK during `DELTA_BARRIER` is required only before that client's writer lease may resume from the advanced base.
- Failure to ACK revokes/fences the writer; the operation remains committed and is replayed/rematerialized from canonical state.
- Exact prepare/commit/retry/compensation mechanics remain ADR-004.

Status:
**ADR-003 = ACCEPTED**

Consequences:
- ADR-004 must consume ADR-003's artifact/revision/operation contracts.
- ADR-007 must align its DELTA_BARRIER and WriterLease state machine with this accepted contract.
- B2-lite remains falsifiable under MD-017 criteria.


## MD-024 — Remote Presentation Independent QA Gate

Decision:
Accept Sol's `QA_Remote_Tactical_Presentation_Independent_Review.md` as independent QA for the frozen RemotePresentation PoC.

Final gate for this exact revision:
- Remote Presentation = PARTIAL / INSUFFICIENT GRAPHICAL EVIDENCE
- Candidate C = PROVISIONALLY ACCEPTED
- Candidate P2 = PRIMARY PRESENTATION CANDIDATE
- Remote Tactical Production = NOT AUTHORIZED

Independent evidence:
1. Actual normal graphical client rendering/UI lifecycle exists.
2. Scripted Worker command/auth/reconcile path exists.
3. Actual user GUI Draft/right-click path does **not** enter that RPC path.
4. Actual GUI mutation is local-only in the current candidate; Worker remains unchanged.
5. Snapshot response application lacks generation/map/sequence freshness fencing.
6. Worker operational cadence and periodic replication are absent.
7. Mirror reconciliation is partial, not full-map authority replication.

Interpretation:
This is an implementation-gap result, not evidence that Candidate P2 is architecturally impossible.

Next gate:
A must implement one real graphical command path end-to-end, authoritative Worker progression/reconciliation, snapshot freshness fencing, and dependency-clean test setup. Sol then performs a narrow regression of that exact path.

## MD-025 — ADR-007 v3 Still Proposed

ADR-007 v3 is not accepted yet.

Required final clarification to align with ACCEPTED ADR-003:
- Server-authored canonical delta commit must not depend on client ACK.
- Client ACK gates writer resumption/base advancement only.
- pre-commit barrier abort may return to the prior committed head;
- post-commit client failure must preserve the new committed head and fence/rematerialize the client.
- `DELTA_BARRIER` text must explicitly distinguish these two failure phases.

Status:
ADR-007 = PROPOSED / REVISION REQUIRED


## MD-026 — ADR-007 Core Contract Accepted

Decision:
Accept ADR-007 v4 as the authoritative core architecture for ordinary Settlement simulation authority, writer leases, fencing, DELTA/HANDOFF barriers, and ordinary↔Tactical handoff, with Master clarifications incorporated into the accepted artifact.

Controlling rules:
1. Barrier admission applies to both DELTA_BARRIER and HANDOFF_BARRIER.
2. A responsive ordinary writer may submit one designated barrier checkpoint before a Server-authored material delta is evaluated.
3. Durable Server commit makes the operation canonical independently of client ACK.
4. ACK gates only writer resumption/synchronization.
5. `BaseCommittedSettlementStateRevision` advances when the writer catches up to the canonical head.
6. `ArtifactBaseStateRevision` advances only on canonical artifact fold.
7. Post-commit writer failure fences/rematerializes; it never erases the committed operation.
8. Disconnect safety is server fencing, not trust in physical stop.

Status:
**ADR-007 = ACCEPTED (core contract).**

Open Decision Requests retained:
- G-Q1
- G-Q2
- G-Q6

Implementation must not silently choose among those policy/topology options.


## MD-027 — Start ADR-008 Shared World Layer Analysis

Decision:
Assign Gemini 3.1 Pro C to `WP-ADR-SHARED-WORLD-01`.

The Work Package prepares a PROPOSED ADR-008 covering Shared World Layer / Transit / World Projection.

This is intentionally parallel to A's Remote Presentation hardening because the two scopes do not require the same implementation target.

No ADR-008 decision is pre-accepted by this assignment.
No TBD is resolved.


## MD-028 — Remote Presentation Hardening Requires Independent Re-Verification

Decision:
Accept A's `Remote_Tactical_Presentation_Hardening_01.md` as developer evidence only.

A has plausibly addressed the exact independent failures identified by Sol:
- real GUI → RPC adapter for Draft and Move;
- suppression of local speculative authority;
- bounded Worker progression;
- snapshot session/generation/map/sequence fencing;
- narrow authoritative job/rotation/health reconciliation;
- dependency-clean graphical profile.

No QA-PRESENT finding is closed from this report alone.

Required next step:
Freeze the exact candidate artifacts/hashes identified in A's report and assign Sol a narrow regression verification.

If Sol independently reproduces the real GUI command loop and the snapshot/cadence/fencing invariants without material new blockers, Master may close the corresponding QA-PRESENT defects and treat the P2 remote-presentation feasibility gate as passed.

This still does not by itself:
- accept ADR-002 finally;
- close QA-ENGINE-002..006;
- authorize Production Tactical;
- prove full-map replication;
- certify WAN latency/NFR-011.


## MD-029 — ADR-008 Draft-1 Requires Revision

Decision:
Do not accept ADR-008 Draft-1 yet.

### Accepted now

- Dedicated Server is final Shared World Domain Authority.
- Canonical Shared World state includes stable world/caravan identity, authoritative location/routing state, custody membership, visibility state, and revision/fencing metadata.
- world-map projection is server filtered; clients/Workers never gain authority merely by materializing WorldObjects.
- world movement is a world-domain process tied to Server runtime / WorldTick, not client local ticks.
- Tactical ingress/egress reuses ADR-003 EntityId/materialization contracts and ADR-007 barriers.
- explicit transit/residence clock is mandatory; raw W is not physiology time.

### Rejected / corrected Draft-1 options

- Blindly trusting client-proposed pathing/routing is not an allowable authority model.
- "World-Scheduled Delta (No Clock)" conflicts with ADR-006A and is removed.
- Immediate caravan destroy/create across ingress/egress cannot be treated as the durable transaction algorithm before ADR-004.
- Offline economy is not categorically engine-free.
- Unsupported mod world code is not assumed safely strippable.

### Open architecture/product questions after correction

- Which server-controlled executor computes exact vanilla/modded world pathing cost and caravan movement facts?
- How does the mandatory TransitClock obtain its physiology execution: continuous server-controlled worker, bounded/batched engine materialization, or another validated server-controlled mechanism?
- Which transit physiological semantics are product-required while all players are offline?

These are Decision Requests, not new Canonical TBD IDs.


## MD-030 — ADR-008 Core Contract Accepted

Decision:
Accept ADR-008 v2 as the authoritative core Shared World Layer / Transit / World Projection architecture, with Master clarifications incorporated into the standalone accepted artifact.

Controlling rules:
1. Dedicated Server owns final Shared World canonical state.
2. World movement facts are server-controlled; client pathing results are never authority.
3. Transit physiology uses an explicit TransitClock distinct from W.
4. W may order/schedule world events but does not become a universal physiology clock.
5. Independent WorldObjects are fenced by per-object/custody revision; WorldStateRevision is global ordering/projection metadata, not a required single hot CAS for every mutation.
6. Custody transfer has one canonical owner at commit boundaries; exact transaction/repair mechanics are ADR-004.
7. Hidden world intelligence is filtered before projection.
8. Engine-free offline operation is permitted only when durable canonical projection facts are sufficient.

Open Decision Request:
- G-Q12a: transit physiology semantics while Server runs / zero players online.
- G-Q12b: transit physiology executor/materialization mechanism.

Status:
**ADR-008 = ACCEPTED (core contract).**


## MD-031 — Start ADR-006B Configuration & Content Manifest Analysis

Assign C to `WP-ADR-CONFIG-CONTENT-01`.

No ADR-006B decision is pre-accepted by this assignment.
No Canonical TBD is resolved.

## MD-032 — Remote Presentation Hardening 02 Independent Gate

Adopt Sol's classification: **PARTIAL / REMAINING BLOCKER**.

Master officially closes:
- QA-PRESENT-001
- QA-PRESENT-003

The remaining narrow feasibility blocker is operational repeated replication:
Worker movement continues, but the graphical mirror receives no further authoritative updates after the command response until an explicit `GET_SNAPSHOT` is issued.

Controlling interpretations:
- test-harness refresh is not operational replication;
- PING size is not snapshot payload size;
- localhost values are not WAN/NFR SLO;
- the fixture is not dependency-clean while semantic dependency errors remain;
- automatic cadence improvement does not close legacy Worker boundedness/liveness defects.

Next A scope:
Implement repeated authoritative replication for the already-proven Draft/Move slice and fix adjacent state-binding defects only. Do not expand into full-map replication, trade, or Production.


## MD-033 — ADR-006B Draft-1 Requires Revision

Decision:
Do not accept ADR-006B Draft-1 yet.

### Accepted architecture direction
- server-pinned gameplay content profile;
- explicit content/profile revisioning;
- layered semantic validation;
- approval-time reject/quarantine of unsupported content;
- config retroactivity classification;
- server-controlled migration;
- cosmetic capability allowlisting.

### Required corrections
- static dependency proof is not sufficient or universally possible;
- pinned profiles reduce drift but cannot guarantee runtime load can never fail;
- runtime failure must quarantine/repair without giving users a way to weaponize unsupported content against lawful offline actions;
- old canonical artifacts require an old-profile-compatible migration read/materialization phase before transformation to the new profile;
- immutable content fingerprint and world-adoption revision must be separated clearly;
- durable operations must capture snapshotted config values/revisions;
- migration-required config/content changes need an explicit state.

Status:
ADR-006B = PROPOSED / REVISION REQUIRED

## MD-034 — Formalize ADR Evidence / Acceptance Policy

Adopt `MASTER_ADR_EVIDENCE_POLICY.md`.

This policy explains and governs why some ADR cores may be ACCEPTED without code experiments while engine-dependent ADR claims require targeted PoC and independent reproduction.

ACCEPTED never implies Production-ready.
Production authorization remains per-scope and requires required E3 evidence.

A previously ACCEPTED ADR may be reopened if explicit runtime falsification disproves a central assumption.


## MD-035 — ADR-006B Core Contract Accepted

Decision:
Accept ADR-006B v2 as the authoritative Configuration & Content Manifest architecture, with Master acceptance clarifications incorporated into the standalone accepted artifact.

This is an E0/Type-C architecture acceptance:
- the profile/config/migration/admission contract is fixed;
- actual semantic-validator completeness remains an E1/E2/E3 proof obligation.

Controlling rules:
1. exact gameplay profile identity is immutable and server-derived;
2. world adoption revision advances only after successful canonical profile adoption;
3. compatibility admission is separate from ADR-001 authentication;
4. cosmetic exceptions are explicit server-approved capabilities bound to package/profile identity;
5. runtime semantic failure quarantines/repairs and never silently drops canonical state;
6. operation-snapshotted config is durable replay input;
7. exact migration transaction/rollback/repair semantics are ADR-004 scope.

Status:
**ADR-006B = ACCEPTED**

## MD-036 — Hardening-02 Requires Independent P2 Gate

Decision:
Accept A's Hardening-02 report as E1 developer feasibility evidence.

Do not yet adopt `OPERATIONAL MOVE PRESENTATION PASS` as the Master gate.

Independent E2 verification must confirm:
- actual OS/user GUI Draft and right-click Move reach the candidate adapter;
- timer-driven replication is normal client-controller behavior and continues without TestHarness refresh;
- at least three authoritative movement updates advance the mirror while Worker moves;
- final Worker/mirror position and completion state converge;
- stale periodic updates are rejected;
- target-map binding prevents wrong-map application;
- all four rotations round-trip;
- fixture loads without the previously observed missing dependency errors;
- privileged test-control cannot be bypassed by forged `Source` or other ordinary client-controlled fields;
- replication polling does not introduce a new unacceptable main-thread blocking/liveness failure.

If this focused E2 gate passes without a new existential blocker, Master may declare the tested P2 presentation slice feasible and close additional QA-PRESENT findings.

This still will not:
- finally accept ADR-002;
- close QA-ENGINE-002..006;
- prove full-map replication;
- prove trade/social interaction;
- authorize Production Tactical;
- certify WAN/NFR-011.

## MD-037 — ADR-004 Draft-1 Requires Revision

Decision:
Do not accept ADR-004 Draft-1 yet.

The draft has the correct transaction shape, but its recovery model assumes too strongly that the database operation log can always recreate the committed RimWorld material state.

Controlling correction:
**No canonical commit may depend on volatile or non-reconstructible material state.**

Before COMMITTED, every required material result must be either:
- reconstructible from an accepted artifact watermark + committed typed operations; or
- durably staged as an immutable, hashed, profile/schema-bound result package/manfiest that recovery can later promote or rebuild from.

Post-commit artifact/publication failure is forward-recovery territory. Pre-commit disconnect does not automatically force ABORT if the Server already owns sufficient durable prepared facts.

ADR-004 remains:
**PROPOSED / REVISION REQUIRED**


## MD-038 — ADR-004 Core Transaction / Repair Contract Accepted

Decision:
Accept ADR-004 v2 as the authoritative E0 transaction/recovery contract with Master clarifications incorporated into the standalone accepted artifact.

Controlling rules:
1. canonical commit never depends on volatile material state;
2. replayable typed operations and staged-material commits are distinct recovery classes;
3. PREPARED uses durable restart-recoverable reservations;
4. cross-scope commit atomically binds source/destination custody and canonical revisions;
5. `ArtifactBaseStateRevision` is an artifact watermark, not the canonical head;
6. post-commit artifact/projection failure uses forward recovery;
7. staged material referenced by a committed transaction remains recovery-addressable until publication/repair completes;
8. projection/outbox lag cannot roll back canonical truth;
9. kill/crash/race correctness remains E1/E2/E3 proof.

Status:
**ADR-004 = ACCEPTED**


## MD-039 — Remote Presentation Hardening-03 Independent Gate

Decision:
Adopt Sol's E2 classification:
**PARTIAL / REMAINING BLOCKER**

Officially close:
- QA-PRESENT-002
- QA-PRESENT-005
- QA-PRESENT-010

Retain:
- QA-PRESENT-004 STILL FAILING
- QA-PRESENT-006 STILL FAILING
- QA-PRESENT-007 STILL FAILING
- QA-PRESENT-008 PARTIAL
- QA-PRESENT-009 PARTIAL

Controlling interpretation:

The P2 architecture now has independent proof for:
- actual OS GUI Draft/Move intent;
- Worker execution;
- autonomous repeated authoritative state replication;
- sequence/session/generation/map admission fencing;
- map-bound application;
- four-direction rotation.

The remaining presentation feasibility gap is no longer network/state propagation itself. It is the **client presentation lifecycle and liveness boundary**:
1. authoritative `Position` must be reflected by rendered `DrawPos`/sprite/hit target without giving the mirror simulation authority;
2. privileged controls must derive from a trusted role/channel/capability, never an untrusted Source string;
3. periodic replication must not synchronously block the Unity main thread.

If these are independently closed on the next frozen candidate, Master may declare the tested P2 Draft/Move presentation slice E2-feasible even if broader full-map/health/job replication remains outside that slice.

ADR-002 will still remain PROVISIONAL until Worker semantic/temporal/publication and broader Tactical integration obligations are satisfied.


## MD-040 — Pipeline Design-01 Is Incomplete; No Production Authorization

Decision:
Do not authorize A to implement the Shared Settlement State Pipeline from Design-01.

Reason:
The submitted artifact ends mid-`OperationRecord` definition and omits required sequences, gates, evidence plan, and implementation outline.

Partial architecture direction is retained, but the first proposed gameplay example (`offline Tax / Auto-Shop inventory deduction`) is not accepted as policy-safe because unresolved G-Q8/G-Q9/TBD-05 may affect canonical inventory and tax/auto-shop semantics.

Next action:
C must deliver `Shared_Settlement_State_Pipeline_Design_02.md` with:
- complete component/data contracts;
- ADR-004-correct recovery semantics;
- a policy-neutral first infrastructure slice or a proof that the chosen real operation avoids all unresolved policy;
- exact Production Gate and A implementation outline.

Status:
**Pipeline Production Gate = BLOCKED BY DESIGN COMPLETENESS**


## MD-041 — Accept Pipeline Design-02 With Narrow Production Authorization

Decision:
Accept `Shared_Settlement_State_Pipeline_Design_02` with controlling Master corrections.

Do not permit a no-op infrastructure probe to advance real `CommittedSettlementStateRevision`.

The first authorized Production infrastructure operation is:
`PIPELINE_PROBE_CAS`

It exercises:
- OperationId / payload-hash identity
- durable PREPARED
- CAS on a dedicated ProbeRevision
- atomic probe COMMIT
- durable receipt/audit
- outbox
- restart reconciler
- duplicate retry / collision rejection

It does not exercise or claim:
- Settlement material-state mutation
- ArtifactBaseStateRevision
- Tactical staged-result publication
- gameplay inventory semantics
- Tax/Auto-Shop
- EntityId custody transfer

Production authorization is per-scope and limited to this infrastructure slice.

A must finish/freeze Remote Presentation Hardening-03 before starting the queued Production WP.

## MD-042 — Start ADR-005 Intent / Betrayal Analysis

Assign C to `WP-ADR-INTENT-BETRAYAL-01`.

No betrayal trigger/policy is pre-decided by this assignment.
Client/Worker remain non-authoritative for final political/domain state.
Canonical TBD-01..05 remain unresolved.

## MD-043 — Hardening-03 Frozen Candidate Requires Final Focused Presentation E2 Regression

Decision:
Accept A's `RENDERED OPERATIONAL PRESENTATION PASS` as developer E1 evidence only.

Do not yet close QA-PRESENT-004/006/007/008/009.

Assign Sol a focused exact-candidate E2 regression.

The narrow P2 Draft/Move presentation slice may receive:
**CONFIRMED RENDERED OPERATIONAL PRESENTATION PASS**
if Sol independently confirms:
- actual OS/user Draft + Move on this frozen candidate;
- rendered DrawPos/sprite/hit-target follows authoritative movement;
- gameplay transport cannot invoke privileged controls even with forged metadata;
- network wait is off-main-thread and Unity apply remains main-thread bounded;
- delay/disconnect/late-response tests do not freeze or regress state;
- target-map/fencing/rotation regressions remain intact.

QA-PRESENT-004 may remain PARTIAL for general health/job/lifecycle scope without blocking this narrow presentation-feasibility verdict, provided its rendered-movement sub-blocker is independently resolved.

A remains paused from starting the queued Production transaction slice until Master reviews Sol's E2 result, preserving the previously established execution order.

## MD-044 — ADR-005 Draft-1 Requires Revision

Decision:
Do not accept ADR-005 Draft-1 yet.

The architecture direction is correct, but the draft currently mixes architectural provenance with unresolved betrayal policy and uses an insufficient single-OperationId event model.

Controlling corrections:
- Server-first authorization produces an immutable AuthorizedAction envelope.
- One intent/action may emit many independently identified Simulation/Damage facts.
- Autonomous events need explicit causal provenance without fabricating live player intent.
- intent-time and decision-time diplomacy revisions are both recorded; product policy determines trigger/timing semantics.
- live committed diplomacy changes use a durable ordered Session Domain Event/Outbox stream, not the uncommitted PendingOperationQueue or initial MaterializationManifest.
- Worker crash recovery must not silently lose politically relevant facts if the associated material outcome may survive.
- Tactical client control authority is distinct from Worker writer lease.

Status:
**ADR-005 = PROPOSED / REVISION REQUIRED**


## MD-045 — ADR-005 Core Contract Accepted

Decision:
Accept ADR-005 v2 as the authoritative E0/Type-C intent/betrayal/session-domain-event contract with Master clarifications.

Controlling rules:
1. Dedicated Server authorizes intent before Worker execution authority exists.
2. Intent/action/fact identities are distinct; fact dedupe never collapses valid multi-hit/AOE facts.
3. Autonomous actions carry first-class provenance without fake PlayerIntent.
4. Authorization-time, execution/consequence, and decision-time relationship context are preserved; final trigger semantics remain product policy.
5. Diplomacy commit CASes against the current scoped aggregate revision, not the historical authorization revision.
6. Mid-session committed political changes travel over a durable ordered Session Domain Event/Outbox stream.
7. Worker/client ACK gates projection readiness only; it is not canonical commit.
8. Required political provenance must survive together with any staged Tactical material result that may become canonical.

Status:
**ADR-005 = ACCEPTED**

No G-Q13..G-Q17 or TBD-03 policy is resolved by this acceptance.

## MD-046 — Adopt Corrected Open-Decision Dependency Baseline

Decision:
Adopt `Open_Decision_Dependency_Map_01_MASTER_CORRECTED.md` as the current sequencing baseline.

The baseline distinguishes:
- implementation blockers;
- completion/release blockers.

This prevents open product policy from unnecessarily freezing lower-level infrastructure while also preventing temporary test defaults from silently becoming Production semantics.

Officially mark:
**G-Q5 = CLOSED / ABSORBED BY ADR-005**
**G-Q5b = OPEN**

No other G-Q/TBD is resolved by this decision.


## MD-047 — Hardening-04 E2: Render/Control Proven, Interactive Command Liveness Still Blocks

Decision:
Adopt Sol's final verdict:
**PARTIAL / REMAINING BLOCKER**

Master closure:
- close QA-PRESENT-006 for the PoC/test-control boundary;
- mark the rendered-movement/hit-target sub-scope of QA-PRESENT-004 closed;
- keep QA-PRESENT-004 overall PARTIAL because general health/job/lifecycle reconciliation is incomplete;
- keep QA-PRESENT-007 OPEN because actual GUI command RPC still blocks the Unity main thread;
- keep QA-PRESENT-008 and 009 PARTIAL.

The next A work is limited to:
1. asynchronous/bounded interactive command transport;
2. command timeout / disconnect / late-response / connection-epoch fencing;
3. bounded command/apply/telemetry queue behavior needed by that path;
4. actual candidate profile/listener argument correctness and clean initialization evidence.

Do not expand this hardening into general health, inventory, full-map replication, or Production authentication.

The queued Production Transaction Pipeline Slice-01 remains authorized but not started until Master reviews the next focused E2 presentation result.


## MD-048 — Add QA-PRESENT-011; Keep QA-PRESENT-005 Closed

Decision:
Accept Sol's Section 12 addendum as material E2 evidence.

Create:
**QA-PRESENT-011 — Dynamic Facing / Authoritative Pose Staleness**
Status:
**OPEN / MEDIUM**

Do not reopen QA-PRESENT-005.

Rationale:
QA-PRESENT-005 proved that North/East/South/West values are serialized and applied correctly. The new evidence instead shows that the Worker may keep an old/stale `Pawn.Rotation` while the pawn is physically moving in the opposite direction.

The required fix must determine whether the authoritative visual pose should come from:
- native Pawn.Rotation;
- stance/focus/aim state;
- path/movement state;
- or a composite presentation-pose contract.

Client-side `position delta -> facing` overwrite is not authorized as a generic fix because it could break legitimate aiming/focus behavior.

The current A hardening WP is revised before implementation/freeze.


## MD-049 — G-Q8 Brief Accepted; Split Economic Inventory from Tax Seizable Assets

Decision:
Accept C's G-Q8 decision brief as useful analysis, but do not resolve G-Q8.

Architectural clarification:
The system must not assume one monolithic asset set serves every economy use case.

Within the G-Q8 decision family, explicitly distinguish:
1. **SettlementAssetGraph** — canonical material/custody graph;
2. **SettlementEconomicInventory** — assets/quantities exposed to ordinary economy and Auto-Shop availability;
3. **TaxSeizableAssetSet** — assets the tax collection rules may select, potentially including non-fungible entities such as Pawn/Animal/Slave under canonical SRS.

These sets may overlap but are not required to be identical.

Consequences:
- Auto-Shop can remain narrow and fungible without forcing Pawn/equipment into shop inventory.
- Tax may require a broader selector plus engine-backed material transfer for semantically complex assets.
- Tier/wealth projection must not automatically be equated with either shop stock or tax-seizable assets.
- no direct XML surgery is approved as the general offline mutation mechanism.

G-Q8 remains:
**OPEN — runtime proof first, then Master product-boundary decision.**


## MD-050 — Hardening-04 REV1 Candidate Frozen; Self-PASS Not Yet Adopted

Decision:
Accept A's REV1 implementation as a frozen E1 candidate suitable for independent verification.

Do not accept the developer's `ASYNC INTERACTIVE PRESENTATION PASS` as the Master gate yet.

Mandatory E2 checks:
- actual OS/user Draft and Move on the exact frozen candidate;
- actual north, south, east, west movement plus one direction change;
- moving/aiming/stance facing semantics, especially because movement currently has priority over Stance_Busy in the reported pose source;
- 2-second delayed interactive command with explicit timeout configuration and no Unity freeze;
- timeout/late response/disconnect/reconnect epoch fencing;
- bounded queue overflow/load behavior;
- clean actual listener binds with the frozen runner/profile;
- foreign Pawn rejection with real user interaction;
- screenshot/evidence manifest integrity.

Official QA-PRESENT status does not change from A's report alone.


## MD-051 — Select Auto-Shop Trade Configuration as Next Real Domain Mutation

Decision:
Select **Auto-Shop Trade Configuration Update (Setup Phase)** as the preferred first real gameplay/domain mutation after the transaction pipeline probe passes its gate.

Reason:
The canonical SRS explicitly requires per-Settlement Buy/Sell order configuration while also explicitly forbidding inventory or Silver reservation at configuration time. Therefore the setup mutation can exercise real authenticated, durable, revisioned gameplay-domain state without requiring G-Q8 inventory semantics or engine materialization.

The first backend slice includes:
- per-Settlement TradeConfiguration aggregate;
- dedicated TradeConfigurationRevision;
- authenticated current-owner authorization;
- expected ownership epoch/revision fencing;
- expected TradeConfigurationRevision CAS;
- replayable typed ADR-004 commit;
- content-profile validation for referenced gameplay definitions;
- audit/receipt/outbox behavior.

It excludes:
- inventory availability;
- trade matching/execution;
- Silver/item transfer;
- FR-204+ execution semantics;
- Occupy/G-Q9 behavior;
- final FR-200 UI.

Status:
**SELECTED / QUEUED — NOT YET AUTHORIZED FOR IMPLEMENTATION**

Prerequisite:
`PIPELINE_PROBE_CAS` must complete the required Production E1/E2 gate first.


## MD-052 — G-Q1 Brief Accepted; Runtime Proof Required Before Topology Choice

Decision:
Do not resolve G-Q1 from the current brief.

Adopt the following architecture facts:
1. multiple Settlement ownership does not imply simultaneous multi-Settlement simulation in one client process;
2. each actively simulated Settlement retains its own LocalClockId and WriterLease/Fencing context;
3. topology may remain deferred behind lease/materialization interfaces for current server-domain Production slices.

Reject as unproven:
- "Single Active Materialization = absolute isolation";
- "Hybrid Lazy Materialization = high feasibility / seamless integration";
- "G-Q1 = pure product policy".

G-Q1 is now explicitly:
**RUNTIME PROOF FIRST + PRODUCT/UX DECISION AFTER FEASIBILITY**

A targeted future engine probe is queued, but it does not delay `PIPELINE_PROBE_CAS` or the selected TradeConfiguration domain mutation.


## MD-053 — Accept Hardening-05 Partial E2; Release Transaction Pipeline Production Slice

Decision:
Adopt Sol's Hardening-05 verdict:
**PARTIAL / REMAINING BLOCKER**

Official closures:
- QA-PRESENT-009 narrow listener/profile subdefect = CLOSED.
- QA-PRESENT-011 tested movement/focus dynamic-facing subdefect = CLOSED.

Official narrowing:
- QA-PRESENT-007 = PARTIAL, not closed.
  Remaining blockers are transport-epoch provenance, bounded result retention/backpressure, and bounded asynchronous connect lifecycle.

Do not reopen QA-PRESENT-005: the wire/native rotation codec remains independently correct.

Do not accept A's evidence manifest as clean; QA-PRESENT-008 remains failing.

Sequencing decision:
Release `WP-PROD-TRANSACTION-PIPELINE-01` for immediate A implementation.

Rationale:
The Shared Settlement transaction substrate is architecture-independent of the remaining Remote Presentation transport defects. Continuing to hold the first Production persistence/transaction slice behind unrelated presentation hardening would add serial delay without reducing transaction risk.

Constraints:
- Remote Tactical Production remains NOT AUTHORIZED.
- frozen presentation candidate remains immutable while the pipeline slice is implemented.
- after the pipeline candidate is frozen, A may return to the queued presentation lifecycle repair while independent pipeline verification proceeds.


## MD-054 — G-Q2 Brief Accepted; Adopt Layered Trust Framing

Decision:
Do not select Posture 1/2/3/4/5 globally.

Adopt a layered trust architecture:
A. mandatory authentication/lease/revision/profile/identity/custody invariants;
B. server-authored typed/domain operations for sensitive state where architecture already supports them;
C. server-controlled engine semantic validation for material artifacts;
D. selective provenance/plausibility controls for high-impact residual client-authored state;
E. audit/admin response.

Important:
- WriterLease never means "trusted truth producer".
- current-parent save edits are not defeated by revision lineage alone.
- ContentProfile admission is not provenance of legitimate in-profile state transitions.
- administrative bans do not replace integrity validation.
- wealth used for political/tier decisions requires protected server-side derivation/validation.

G-Q2 remains:
**OPEN — RUNTIME EVIDENCE + RISK/POLICY DECISION REQUIRED BEFORE ORDINARY CLIENT MATERIAL PUBLICATION PRODUCTION ACCEPTANCE.**


## MD-055 — Insert Midpoint Independent Architecture Review Before First Real Gameplay Mutation

Decision:
Create a deliberate midpoint gate after the first Production transaction substrate and before the first real gameplay-domain mutation.

Inputs:
- A Pipeline Slice-01 E1 candidate;
- Sol independent Pipeline E2;
- external independent architecture red-team review;
- current canonical SRS / accepted ADRs / open-decision map / QA ledger.

No first real gameplay mutation begins until Master reconciles these inputs.

A's `E1 PIPELINE PROBE PASS` is accepted as developer evidence only.

The checkpoint is intended to detect:
- wrong problem decomposition;
- unnecessary custom implementation where Vanilla/SQLite/framework behavior should be reused;
- hidden coupling between accepted ADRs;
- incorrect Production sequencing;
- unproven recovery assumptions;
- policy accidentally embedded in infrastructure;
- missing failure/race/security boundaries;
- overengineering.

TradeConfiguration remains the selected next real domain mutation but stays QUEUED.


## MD-056 — MPC-002 HOLD; Adopt Foundation Corrections

Decision:
**HOLD — ARCHITECTURE REVISION REQUIRED**

Reason:
The first independent Production E2 is FAIL, and the external red-team identified contract contradictions that materially affect every future gameplay operation.

The hold is narrow:
- preserve the proven local SQLite transaction/CAS core;
- replace faulty identity/recovery/publication/startup contracts before real gameplay state is layered on top.

### Decisions effective immediately

**D1 Durability**
Canonical Production DB: `journal_mode=WAL`, `synchronous=FULL`, asserted on every canonical connection/startup. Process-crash evidence does not imply power-loss durability.

**D2 Operation identity**
Canonical key = `(PrincipalId, OperationId)`.
Server computes a versioned canonical fingerprint over:
OperationType, PrincipalId, target scope set, expected revisions, ContentProfileFingerprint, config snapshot reference when relevant, and typed payload.
A caller-supplied payload hash is never trusted as identity evidence.
Same key + mismatch = collision reject.
ABORTED terminal result is stable; a new attempt uses a new OperationId.

**D3 Fencing**
Correct ADR-004/ADR-007 conflict:
FencingGeneration changes when writer authority/incarnation changes.
A server-authored operation under a continuing lease advances required base revision / applied-operation watermark instead of forcing a new fencing generation and rematerialization for every commit.

**D4 Lease scope**
Lease identity is execution-island / LocalClock-domain scoped and carries its Settlement scope set.
Barriers are island-scoped unless runtime evidence proves finer isolation safe.
This is an interface correction, not a final G-Q1 topology choice.

**D5 Store incarnation**
Add StoreIncarnationId to durable authority/receipt token family. Restore or rollback rotates it. Define consistent DB/artifact backup contract and W restart lower bound.

**D6 Fast path vs reservation path**
Do not use PREPARED for every operation.
Single-scope metadata/CAS uses a one-transaction fast path.
PREPARED is reserved for staged/multi-scope/multi-party operations with real durable reservations.
Auto-forward is allowlisted and fail-closed on any missing/tampered/stale authority input.

**D7 Engine Host**
Use one shared Engine Host component boundary for materialization/semantic validation/profile load/migration/Tactical modes.
No separate loader stacks per feature.

**D8 Runtime evidence**
E-A and E-B are mandatory before material-state Production.
E-C is mandatory before Remote Tactical/G-Q10 release, not before unrelated server metadata slices.

### Sequencing supersession

Previous statement "TradeConfiguration is the next real gameplay mutation" is superseded in sequencing.
TradeConfiguration remains the preferred first **Settlement-scoped configuration mutation**, but only after:
- corrected pipeline E2;
- ADR-001 Production Foundation;
- canonical Settlement metadata/ownership registry.

Alliance is not inserted as a mandatory prerequisite; it remains a later domain slice.

Canonical TBD-01..05 remain OPEN.


## MD-057 — Accept Pipeline REV1 as E1 Candidate; Start Parallel Engine Proof

Decision:
Accept A's `E1 PIPELINE REV1 PASS` as developer evidence only.

Do not close QA-PIPELINE-001..012 until independent E2.

Release two parallel tracks:
1. Sol independently verifies exact Pipeline REV1 candidate.
2. A starts the scratch-only Engine Host Settlement Round-Trip PoC.

Reason:
The Pipeline REV1 candidate is now frozen, so A can advance the independent engine/materialization critical path without modifying the frozen Production candidate.

TradeConfiguration remains re-sequenced behind:
- Pipeline REV1 E2 PASS;
- ADR-001 Production Foundation;
- canonical Settlement ownership registry.

No material-state Production mutation is authorized.

The separate old G-Q1 PoC remains non-dispatched; its useful Vanilla-first clock/materialization questions are absorbed into the Engine Host round-trip PoC.


## MD-058 — G-Q6 Remains Open; Adopt SUSPENDED_GRACE State Model Boundary

Decision:
Do not choose a fixed reconnect grace duration yet.

Adopt the minimum architecture boundary:

`ACTIVE -> SUSPENDED_GRACE -> {ACTIVE(resumed), REVOKED/FENCED}`

Rules:
- no replacement writer while the old authority is merely suspended;
- any replacement/handoff first revokes/fences the suspended authority;
- transport reconnect within the same still-valid SessionEpoch may resume the same lease without gratuitous FencingGeneration change;
- new SessionEpoch / holder / store incarnation requires new authority and invalidates the old holder;
- client-side pause during disconnection is normative behavior, not trusted anti-cheat evidence;
- committed server operations remain canonical and may force suspended/old clients to rematerialize;
- barrier-specific grace remains evidence-first, not fixed now.

G-Q6:
**OPEN — E-B + LEASE STATE-MACHINE RUNTIME EVIDENCE REQUIRED BEFORE ORDINARY-CLIENT PRODUCTION INTEGRATION.**

Canonical TBD-01..05 unaffected.


## MD-059 — Adopt Player-Global Boundary; Keep Exact Schema Evidence-Driven

Decision:
Adopt `PlayerGlobalStateSegment(PlayerId)` as a first-class canonical composition boundary.

This is not a field schema approval.

Rules:
- stable owner key is PlayerId;
- PersonalFactionId is lifecycle/reference metadata, not segment identity;
- PlayerGlobal state has its own revision;
- Dedicated Server orders canonical commits;
- owner/Engine Host may submit allowed mutations but may not overwrite the entire canonical segment without arbitration;
- MapSegments are not rewritten merely because global state changes;
- materialization binds exact global/world/domain projection revisions;
- time-bearing global data must carry an explicit clock domain;
- world-pawn/quest membership is runtime-evidence driven;
- domain political state is never moved into PlayerGlobal engine state.

Open product decisions:
- research/ideology inheritance on faction join;
- expulsion/split inheritance;
- exact player-global mutation authority;
- exact quest/royalty/world-pawn membership.

These do not block current Pipeline REV1 QA or E-A.
They block final Genesis/materialization schema freeze.


## MD-060 — Pipeline Foundation Stops at Durable Event Append

Decision:
Do not implement a generic Production external-effect dispatcher/cursor/ACK framework in Pipeline Foundation P1.

P1 canonical completion is:
`COMMITTED decision + immutable receipt/audit + durable ordered event append`.

`PublicationEvents` is an append-only source for later explicit consumers.

No P1 claim of:
- external exactly-once effect;
- generic PUBLISHED state;
- mandatory-consumer catch-up;
- consumer cursor completion.

Each real consumer later receives its own idempotency/order/recovery gate.

This supersedes the REV1 generic callback/cursor design.

Reason:
Sol independently demonstrated that the generic callback model duplicates durable external effects and can skip failed predecessors. Consumer atomicity cannot be proven by an in-memory test dictionary.

This is a simplification, not a relaxation:
no gameplay feature may rely on event delivery until its concrete consumer contract passes E2.

## MD-061 — B2-lite Core Moves from Unproven to E1-Supported

A's E-A report is accepted as meaningful developer runtime evidence that:
- target-only Settlement materialization is feasible in a reduced valid RimWorld context;
- census-based loss detection is viable;
- custody entity/reference round-trip is feasible for the tested complex fixture.

B2-lite is no longer classified as having zero runtime evidence.

However it remains validation-required because:
- no independent E2 yet;
- cross-process fresh-host round-trip must be confirmed;
- player-global closure remains open;
- G-Q1 global time contamination remains observed;
- broader mod/content semantic coverage remains open.

No material-state Production gate opens from E1 alone.


## MD-062 — Genesis Has Explicit Authority Boundary; Model Selection Deferred

Decision:
Adopt an explicit Genesis Authority contract without selecting the final trust model.

Mandatory genesis identity:
- server-authorized `GenesisOperationId`;
- target Settlement identity reserved/unique;
- approved generation/founding specification;
- ContentProfileFingerprint;
- StoreIncarnationId;
- LocalClockId;
- PlayerId/Faction/domain projection binding;
- staged census/manifest;
- terminal GenesisReceipt.

There is no ordinary CheckpointParentRevision at genesis.

Canonical admission rule:
**No MapSegment becomes canonical until its gameplay-significant state, stable identities/custody, profile, census and authority bindings are accepted together.**

Native RimWorld loadIDs are not canonical EntityIds.

Additional Settlement founding:
- existing caravan people/items use ADR-008 custody transfer;
- new map/environment uses an explicit genesis generation/admission path.

Model A (server Engine Host), B (hostile client + validation), C (server manifest/seed + client materialization), and E (hybrid) remain architecture options.
Model D is the custody-transfer portion of additional-settlement founding, not by itself the whole genesis of the new map.

Evidence order favors Model A/D first.
No requirement currently forces deterministic same-seed byte-equivalent RimWorld generation.

No canonical TBD is resolved by this decision.


## MD-063 — Accept Pipeline REV2 E1; Require Exact Independent Freeze Identity

Decision:
Accept A's `E1 PIPELINE REV2 PASS` as developer evidence.

Do not close any QA-PIPELINE defect until Sol E2.

REV2 architecture direction is ratified for verification:
- P1 ends at canonical decision + ordered durable event append;
- no generic consumer/exactly-once delivery framework in P1;
- immutable command admission;
- unambiguous typed fingerprint;
- terminal operation rows are immutable;
- StoreIncarnation fence is inside the canonical commit boundary;
- bounded writer ingress/lifecycle;
- schema v3 fail-closed/non-destructive policy;
- Production Release excludes destructive test controls.

Evidence-discipline requirement:
A's report lacks exact frozen candidate hashes/MVID.
Independent QA must establish and publish the candidate source/binary identity before testing.
A must preserve the candidate unchanged until E2 completes.

No Production gameplay gate opens from E1.

## MD-064 — Engine Host E2 FAIL; Separate Materialization Feasibility from Semantic Admission

Decision:
Reject the exact Engine Host Round-Trip candidate for E2 without rejecting B2-lite.

Canonical Engine Host export/admission requires a source-bound semantic approval state, not merely engine READY or successful file creation.

Semantic approval must bind:
- trusted source/candidate manifest identity;
- content/profile identity;
- engine generation/session identity;
- target map/scope;
- relevant artifact/global-context revisions;
- census/reference result;
- approval generation.

Any relevant mutation after approval invalidates approval until revalidation.

A save with material serialization errors or semantic mismatch cannot become canonical merely because a file exists.

Context naming correction:
Current Context B is a **pruned target-map owner context**; a truly minimal/synthetic dependency closure remains unproven.


## MD-065 — Pipeline REV2 Fails E2; REV3 Is a Narrow Contract Repair

Decision:
Do not redesign P1 again.

REV3 keeps:
- single canonical SQLite decision transaction;
- no PREPARED for single-scope probe;
- durable event append only;
- bounded single writer;
- WAL/FULL;
- no generic consumer execution.

REV3 must repair:
1. lossless/rejecting canonical input encoding;
2. terminal REPLACE bypass;
3. exact schema semantics;
4. aggregate storage-error typing;
5. shutdown/admission lifetime;
6. mandatory explicit StoreIncarnation;
7. startup consistency + actual writer lifetime;
8. globally unique receipt/event identity consistent with `(PrincipalId,OperationId)`.

### New operation-global identity rule

Operation arbitration key remains:
`(PrincipalId, OperationId)`.

Any globally keyed derivative identity must include the principal-scoped operation identity or be generated as a globally unique stored ID.

A derivative ID must never collapse two valid operations solely because two principals chose the same OperationId.

## MD-066 — G-Q8 Offline Material Commit Uses Stage-Before-Commit

Decision:
For an offline operation that changes RimWorld material state, projection/index availability is a hint and preflight input, not sufficient commit authority.

Default safe flow:
`fence -> materialize -> apply complete change -> semantic validate -> durable stage -> canonical DB commit -> promote`.

Expected material shortfall discovered while constructing the staged result occurs **before** canonical commit and causes abort/retry.

Post-commit `PUBLISH_PENDING/REPAIR_REQUIRED` is for unexpected failure to promote/recover an already validated, commit-bound staged result.

FR-202/203 no-reservation applies to order registration, not transaction-time execution fencing.

No direct XML material mutation path is approved until a dedicated codec passes E2 application-totality and semantic-integrity proof.


## MD-067 — Semantic Approval Must Be Source-Authoritative, Not Self-Baselined

Decision:
A semantic manifest is authoritative only when its provenance is itself trusted.

The following sequence is NOT sufficient canonical validation by itself:
`read current candidate state -> generate census from it -> compare candidate to that same census -> approve`.

That only proves self-consistency.

A valid semantic approval must establish why the reference manifest/invariants are trusted:
- prior canonical artifact/manifest lineage;
- server-authorized deterministic/staged operation expectation;
- trusted Engine Host structural/invariant oracle;
- or another explicit authority source.

For free-running simulation where the exact post-tick state is not predetermined, approval may combine:
- source-bound provenance;
- structural/reference invariants;
- conservation/authority constraints;
- supported semantic sanity checks;
rather than byte/field equality to an unknown future state.

The concrete contract remains E2/architecture-validation dependent.

## MD-068 — Artifact Approval Applies to Saved Bytes

Decision:
Pre-save live-state approval is necessary but not sufficient for canonical artifact promotion.

The staged saved artifact must be validated strongly enough to show that serialization did not silently drop or alter supported canonical state.

A save log with no exception and a well-formed XML envelope is not, by itself, semantic proof of the output bytes.

Exact implementation may use:
- static saved-artifact oracle;
- immediate fresh-process reload;
- trusted serialization manifest comparison;
- or another independently validated method.

No Production artifact admission until this boundary passes E2.


## MD-069 — Offline Material Mutation Uses Scope Fence, Not Always DELTA_BARRIER

Decision:
Use a generic exclusive material-scope execution reservation/fence as the architecture primitive.

- Offline/unleased Settlement: acquire the material-scope reservation/fence directly.
- Online owner-held Settlement: enter the ADR-007 DELTA_BARRIER flow before material mutation.
- Tactical/other holder: follow the applicable handoff/fencing contract; do not bypass active authority.

The scope root remains execution-island/LocalClock domain + Settlement scope set.

## MD-070 — Material Commit and Artifact Fold Revisions Are Distinct

Decision:
A successful canonical DB commit advances `CommittedSettlementStateRevision`.

Subsequent promotion/fold of the commit-bound staged artifact advances:
- `ArtifactBaseStateRevision`;
- `ArtifactRevision`;
- derived projection/index watermarks as appropriate.

Promotion does not re-advance the committed state.

## MD-071 — Engine-Free Material Codec Is Optional Optimization

Decision:
Do not authorize direct XML mutation as a Production path.

A future engine-free codec may be admitted only for a tightly bounded semantic subset after independent E2 proves:
- immutable staged-copy operation;
- exact base/profile binding;
- application totality;
- semantic conservation;
- deterministic/replay-safe selection;
- clean fresh Engine Host reload;
- equivalence to the declared canonical result.

Byte-for-byte equality with Engine Host output is not required.


## MD-072 — Split Semantic Admission from Simulation Result Sealing

Decision:
Do not use one generic `APPROVE_SEMANTIC <manifest path>` operation for both untrusted input admission and post-simulation result approval.

Two authority phases are required:

1. **Trusted Input Admission**
   - compares an untrusted/staged input artifact against a Dedicated-Server-authorized immutable authority manifest/bundle;
   - candidate-generated census is evidence only and cannot nominate its own authority;
   - source artifact/profile/context/base revision/generation scope are bound.

2. **Trusted Simulation Result Sealing**
   - available only after trusted input admission and a valid simulation authority/grant;
   - captures the result manifest from the operator-controlled Worker;
   - binds it to the admitted source, WorkerGeneration, target scope, execution grant and result epoch;
   - the result manifest becomes the expected semantic description of the staged output bytes.

This does not make the Worker untrusted.
It prevents untrusted input from becoming canonical merely by describing itself.

## MD-073 — Export Approval Requires Current-State Revalidation and Saved-Byte Proof

Decision:
A semantic approval snapshot is stale if current live semantic state no longer matches it, even when `TicksGame`, map index and generation are unchanged.

Before export/promotion:
- recompute canonical supported semantic manifest/hash from current live state;
- require it to match the sealed approval snapshot;
- save to immutable staging;
- validate complete XML/document structure;
- independently validate the staged saved bytes against the sealed result manifest;
- re-check generation/context/result epoch immediately before promotion.

For current PoC/E2, the preferred saved-byte proof is a **fresh validation Worker/process** using the same pinned ContentProfile and target context.

Promotion must preserve the previous approved final until the new candidate is fully validated.

## MD-074 — Supported Semantic Manifest Is a Closed Schema

Decision:
For a declared `SupportedSemanticManifestVn`, every field collected into the canonical manifest contributes to its canonical hash/equality predicate.

Do not collect fields and then silently omit them from approval comparison.

Fields outside the supported manifest are explicitly `UNCLASSIFIED/OUT_OF_SCOPE`, not implicitly certified.

Structured diffs are diagnostic; canonical normalized manifest hash/equality is the gate.

## MD-075 — Pipeline REV3 Enters Independent E2

Decision:
Accept REV3 as the frozen E1 candidate.

Do not close QA-PIPELINE defects until independent Sol verification.

Additional E2 watch:
Principal-aware derivative IDs are still raw formatted strings.
Unless identifier grammar proves ambiguity impossible, QA must attack delimiter/escaping collisions before QA-PIPELINE-019 can close.


## MD-076 — Principal Identity Is Stable Across Session Epochs

Decision:
`PrincipalId` identifies the authenticated actor/subject.
`SessionEpoch` identifies a logical authenticated session.

They are separate fields.

Canonical operation identity remains principal-scoped and must not be silently re-keyed by transient SessionEpoch changes.

A server-authored command envelope may carry:
- PrincipalId;
- SessionEpoch;
- OperationId;
- StoreIncarnationId;
- capability/auth context;
- protocol/profile context;
as distinct values.

## MD-077 — Foundation Does Not Resolve Final Transport Crypto or Auth Provider

Decision:
Freeze the security properties, not a specific provider/format.

Required:
- credentials are validated by the Server or trusted auth integration;
- clients cannot self-assert PrincipalId;
- sessions/capabilities are server-authored;
- malformed/stale/unauthorized commands fail closed.

Not frozen here:
- password vs OAuth vs external identity provider;
- JWT vs opaque session handle;
- exact TLS deployment policy absent a controlling SRS requirement.

## MD-078 — Foundation Startup Precedes Domain Registries

Decision:
Foundation READY does not require Faction/Settlement registries that have not yet been implemented.

Readiness is layered:
1. persistence/Pipeline/world-incarnation/content/auth/session Foundation;
2. Player/Faction/Settlement Registry;
3. later feature-specific registries/services.

A route may be unavailable until its layer is READY without making the entire metadata Foundation unavailable.

## MD-079 — SessionEpoch Does Not Automatically Fence Settlement Authority

Decision:
Creating a new SessionEpoch is not itself a Settlement FencingGeneration event.

If the new session replaces an active writer authority, the lease revocation/replacement protocol performs the fencing action.

Same-SessionEpoch transport reconnect does not advance FencingGeneration.

G-Q6 restart/grace policy remains open for ordinary simulation.


## MD-080 — Pipeline REV3 Rejected; REV4 Is the Final Narrow Foundation Repair Target

Decision:
Preserve P1 architecture.

REV4 repairs only:
- canonical JSON identity;
- startup consistency;
- schema semantic signature;
- shutdown/worker lifetime;
- derivative ID encoding.

Do not add gameplay features, consumers, PREPARED flow, or material state.

## MD-081 — Registry Separates Stable Identity, Membership, Ownership, Execution, and Custody

Decision:
The following are separate canonical concepts:
- PlayerId / stable PrincipalId subject;
- FactionId and membership relation;
- SettlementId;
- legal ownership/control relation;
- SettlementOwnershipEpoch;
- WriterLease/execution authority;
- material custody location.

No single field or relation substitutes for the others.

## MD-082 — Ownership Epoch Changes Only on Canonical Ownership Change

Decision:
`SettlementOwnershipEpoch` advances when the canonical legal ownership/control relation for that Settlement changes.

Faction join, expulsion, branch split, conquest, or other lifecycle events advance the epoch only if their committed domain result changes that ownership/control relation.

This does not resolve TBD-01 or TBD-04.

## MD-083 — Genesis Reservation IDs Are Not Timeout-Recycled

Decision:
A reserved SettlementId/GenesisOperationId becomes durable history.

Abandoned/failed genesis may transition to a terminal non-active state, but canonical identifiers are not deleted and reused by timeout GC.

Noncanonical staged files/blobs may be garbage-collected under a separate retention policy.


## MD-084 — TradeConfiguration Is Ownership-Epoch-Bound Metadata, Not Material State

Decision:
TradeConfiguration canonical state is a metadata aggregate keyed to SettlementId.

Its mutation transaction must atomically validate:
- server-derived PrincipalId authorization via Registry;
- expected SettlementOwnershipEpoch;
- expected TradeConfigurationRevision;
- StoreIncarnationId;
- durable operation identity/fingerprint.

It does not inspect or reserve RimWorld material state.

## MD-085 — Registry Owns Ownership Truth; TradeConfig Stores Only a Binding Snapshot

Decision:
Current legal owner/controller remains authoritative in the Registry.

TradeConfiguration may store the ownership epoch and optional non-authoritative owner snapshot for audit/display, but must not become a competing ownership source of truth.

## MD-086 — TradeConfig Publication Is Durable Event Append Only

Decision:
A successful TradeConfiguration mutation may append a typed PublicationEvent in the canonical transaction.

This does not imply:
- generic Outbox dispatcher;
- UI delivery;
- ACK;
- exactly-once external effect;
- startup catch-up.

Those semantics belong to a future concrete consumer.

## MD-087 — Trade Execution Fencing Depends on Current Execution Authority

Decision:
No universal DELTA_BARRIER rule exists for all trade execution.

- offline/unleased material scope -> exclusive server material-scope reservation/fence;
- owner-client active scope -> DELTA_BARRIER;
- Tactical/other holder -> appropriate handoff/fencing.

TradeConfiguration metadata updates use none of these material barriers.


## MD-088 — Fresh Saved-Artifact Validation Is a Pre-Promotion Gate

Decision:
A post-promotion fresh-process validation is evidence, not a canonical admission gate.

For Engine Host artifact promotion, the exact staged SHA that will be promoted must be validated **before promotion** by an independent fresh validation context capable of:
- loading the staged artifact;
- reconstructing the declared SupportedSemanticManifest;
- comparing its canonical hash/equality to the sealed ResultManifest;
- verifying pinned ContentProfile/context/source lineage;
- reporting no blocking load/reference errors.

Only the exact validated staged SHA may be promoted.

A staged SHA check by itself proves byte immutability after hashing, not semantic correctness of the bytes that were originally hashed.

## MD-089 — Authority Bundle Must Bind Full Admission Context

Decision:
Trusted input authority must bind, at minimum:
- AuthorityId/nonce;
- source artifact SHA;
- expected SupportedSemanticManifest version/hash;
- ContentProfileFingerprint;
- target scope/map/context identity;
- StoreIncarnation/base artifact or equivalent PoC lineage placeholder;
- Worker generation/session identity;
- allowed operation mode.

A field not yet available in PoC may be represented by an explicit test placeholder, but it must not be silently omitted from the authority model.

## MD-090 — Simulation Result Sealing Requires an Authorized Grant

Decision:
A ResultManifest is authoritative only when produced:
- from successfully admitted trusted input;
- by the operator-controlled Worker;
- under a control-plane-authorized simulation grant bound to the current AuthorityId/context/generation.

A caller-chosen arbitrary `grantId` string is not by itself grant authority.

## MD-091 — Gate03 May Enter Independent Audit Despite E1 Partial

Decision:
Freeze and independently inspect Gate03 now rather than silently correcting it before QA.

Reason:
- self-baselining and same-tick stale approval are materially redesigned;
- independent QA can determine whether the missing pre-promotion validator is only a report omission or an implementation omission;
- A can advance Pipeline REV4 in parallel without touching the frozen Gate03 candidate.

No QA-ENGINE defect closes until Sol returns.


## MD-092 — DELTA_BARRIER Quiesces the Execution-Island / LocalClock Scope

Decision:
Until narrower LocalClock virtualization is independently proven, DELTA_BARRIER quiescence applies to the WriterLease execution island / LocalClock domain and its Settlement scope set.

A delta may mutate only one target Settlement while sibling Settlements in the same island remain unchanged but paused.

This is consistent with MPC-002 and does not resolve G-Q1.

## MD-093 — Barrier ACK Is a Sequence-Bound Quiescent Cut

Decision:
A valid barrier ACK is not merely a boolean client response.

It must bind the frozen execution cut to:
- BarrierId;
- lease/fencing generation;
- island/scope set;
- base revisions;
- LocalClock/tick position;
- last applied command watermark;
- final checkpoint/census/artifact identity or equivalent proof.

The Server accepts the cut only when all mutations up to the watermark are accounted for and no later mutation is admitted into the frozen base.

Wall-clock timestamps are not the ordering authority.

## MD-094 — Barrier Abort Does Not Imply Lease Revocation

Decision:
A pre-commit barrier failure may return the same holder to ACTIVE without FencingGeneration change if:
- no canonical commit occurred;
- client state is proven rolled back/rebased to the accepted barrier base;
- lease/session authority remains valid.

If exact safe state cannot be proven, use SUSPENDED_GRACE or explicit revoke/fence before replacement.

## MD-095 — Resume Requires Exact Committed Material Identity

Decision:
After canonical commit, the holder may resume only from material state proven identical to the committed staged result.

A full re-download is one recovery mechanism, not a universal requirement.

Resume authorization binds:
- committed state revision;
- artifact/result identity;
- WriterLease/FencingGeneration;
- LocalClock resume point.

No catch-up burst is permitted merely because wall/global time advanced during the barrier.

## MD-096 — Gate03 Fails E2; Retain Authority Split
Retain trusted input admission + trusted simulation result sealing. Do not revert to candidate self-census approval.

## MD-097 — StageValidationReceipt Is Mandatory
Promotion may succeed only from an immutable StageValidationReceipt binding exact staged SHA/path, SealedResultId, ResultEpoch, AuthorityId, authorized GrantId, WorkerGeneration, target scope/context, ContentProfileFingerprint, source/base lineage, and validator result. RESULT_SEALED alone can never authorize promotion.

## MD-098 — Saved-Byte Validator Computes Actual Manifest
The pre-promotion validator must fresh-load the exact staged bytes and compute the supported semantic manifest from those bytes. It must not copy expected hash into actual hash or treat XML well-formedness as semantic equality.

## MD-099 — Authority and Grants Are Immutable Generation-Scoped Capabilities
AuthorityId cannot be overwritten within a loaded generation. Changed authority requires reset/new generation. SimulationGrant must be pre-authorized and bound to AuthorityId/generation/scope/mode; unknown/stale/cross-authority/blank grants cannot STEP/SEAL.

## MD-100 — Pipeline REV4 Enters Independent E2
Freeze REV4 as current P1 candidate. ADR-001 Foundation implementation remains blocked until Sol independently closes 001/007/008/013/019.

## MD-101 — G-Q1 Remains Vanilla-First and Evidence-Driven
Retain `VANILLA MULTI-MAP FIRST -> MINIMAL INTERCEPTION -> SEPARATE EXECUTION ISLAND ONLY IF FALSIFIED`.
Model A failure does not itself force Model C. Model B is rejected only if required supported-profile semantics cannot be achieved by a bounded, testable interception/reprojection surface.

## MD-102 — Execution Island Is the Unit of Clock Isolation
Do not equate SettlementId with process/island identity.
An execution island owns one active LocalClock domain and a Settlement scope set.
Separate process/island is required only when independent LocalClock/simulation authority needs physical isolation.

## MD-103 — G-Q1 Uses Semantic Artifact Comparison
Decisive saved-artifact probes must fresh-load artifacts, compute supported semantic manifests/census, compare explicit allowed differences, and verify custody/entity/material conservation.
Raw `.rws` byte equality is not required unless separately proven deterministic.

## MD-104 — PlayerGlobal Temporal Membership Remains Open
G-Q1 does not freeze the exact PlayerGlobal field schema.
Research, Ideology, Tales, Quest state, WorldPawns and global managers remain ownership/dependency questions.
PlayerGlobalStateSegment remains keyed by PlayerId.

## MD-105 — Cosmetic Chronology May Drift Only Under Noninterference
Per-Settlement visual sky/calendar equality is not inherently required.
Shared global-time behavior may remain only if it cannot mutate frozen supported material state, violate domain deadlines, cause forbidden catch-up, or break the admitted ContentProfile.

## MD-106 — Pipeline REV4 Fails E2; REV5 Is a Narrow Recovery/Lifetime Repair

Decision:
Do not redesign P1.

REV5 repairs only:
- input validation exception typing;
- legitimate ABORTED recovery semantics;
- principal-scoped history/parent identity;
- recovery semantic binding for operation envelope / receipt / event / audit;
- actual writer termination ownership;
- exact Release manifest/provenance.

No gameplay, material state, consumer execution, or PREPARED workflow is added.

## MD-107 — Reject Audit Separates Requested and Observed Revision

Decision:
A stale/CAS-rejected operation must preserve both meanings explicitly:

- `ExpectedRevision`: revision requested by the command;
- `ObservedRevisionAtDecision`: canonical revision actually observed when rejecting.

Recovery must validate each field against its own semantic role.

For a legitimate stale request these values are expected to differ.

Do not rewrite historical observation using the current aggregate revision during restart.

## MD-108 — Persistence Parent Identity Uses Full Canonical Operation Identity

Decision:
Every durable child relationship that belongs to an operation must be unambiguously bound to the canonical operation identity.

Canonical operation identity remains:
`(PrincipalId, OperationId)` within the StoreIncarnation/world timeline.

A history/receipt/event/audit lookup may use:
- both PrincipalId and OperationId;
- or a durable internal OperationRecordId that is uniquely/FK-bound to that pair.

OperationId alone is never sufficient.

## MD-109 — Recovery Recomputes Semantic Parent Bindings

Decision:
Startup/recovery must not accept a persistence graph merely because row counts and stored hashes are internally self-consistent.

For each operation, recovery must independently validate where applicable:
- canonical request/envelope fingerprint from stored typed envelope fields;
- operation type/schema/profile/config/incarnation relationship;
- expected ReceiptId derivation;
- expected EventId derivation;
- receipt/event parent identity;
- typed audit details and rejection/commit semantics;
- history parent identity and revision relation.

Stored child IDs/hashes are data to verify, not authority for recomputing themselves.

## MD-110 — Caller Deadline Is Separate From Service Termination

Decision:
A request caller may receive a bounded `UNKNOWN_QUERY_REQUIRED` response while the writer is still resolving an ambiguous in-flight operation.

But final service lifetime completion is different:
- final `Dispose/Shutdown/Main` success must not return while the owned writer is alive;
- active coordinator ownership must remain reachable until writer exit and DB cleanup;
- readiness/admission close before termination wait;
- an emergency process-abort policy is separate from a clean shutdown contract.

A timeout return with `IsDisposed=false` is not successful disposal.

## MD-111 — Pipeline Schema Closure Survives Explicit Version Evolution

Decision:
QA-PIPELINE-008 is closed for the independently verified V5 schema contract.

If REV5 needs a schema change to repair principal-scoped history identity, create an explicit later schema version (expected V6) and independently re-run the closed schema guarantees.
Do not silently mutate V5 semantics in place.

## MD-112 — Gate04 Enters Independent E2

Decision:
Accept Gate04 as an E1 PASS candidate only.

No QA-ENGINE defect closes until Sol independently verifies:
- saved-byte semantic validation;
- immutable authority/grant lineage;
- receipt authenticity and replay boundaries;
- exact result/epoch/stage binding;
- profile/context binding.

## MD-113 — Validator Receipt Is Evidence Only If Issuer and Expected Result Are Bound

Decision:
A StageValidationReceipt is canonical promotion evidence only when the simulator can establish both:

1. the receipt was produced by an authorized fresh validator instance/process under the approved validation profile; and
2. the validator compared the staged bytes against the simulator's exact immutable SealedResult, not a caller-substituted expected manifest.

A different PID string alone is not sufficient issuer proof.

The exact mechanism may be:
- orchestrator-issued validator session/capability;
- keyed receipt MAC/signature;
- trusted local IPC with unforgeable handle/nonce;
- another equivalently strong operator-controlled binding.

Do not require public-key cryptography specifically.

## MD-114 — ContentProfile Runtime Binding Is Distinct From Build Provenance

Decision:
Frozen Worker/RimWorld source and binary hashes prove which candidate QA tested.
They do not automatically prove runtime ContentProfile admission.

For Engine authority, ContentProfileFingerprint must represent the gameplay-relevant admitted profile sufficiently to detect authority-relevant content changes.
ModsConfig/order alone may be insufficient if mod binaries/Defs/schema/codec change under the same list.

Exact profile algorithm remains controlled by ADR-006B and independent E2 evidence.

## MD-115 — Gate04 Job Semantic Claim Is Explicitly Narrow

Decision:
Current SupportedSemanticManifest may claim active job coverage only for fields actually represented and independently gated.

Gate04 currently documents JobDef-only job coverage.
Do not infer full job identity/targets/queue/driver-state certification from the A->B->C transport chain.

## MD-116 — PlayerGlobal Boundary Is Logical Before It Is Physical
`PlayerGlobalStateSegment(PlayerId)` is a canonical logical segment. It does not yet require a literal separate `.rws` blob. Physical representation may be extracted serialized state, server canonical records projected into Engine Host, or another independently validated representation. Exact field schema and codec remain OPEN.

## MD-117 — Canonical Global Revision Advancement Is Server-Authorized
WriterLease/Engine Host simulation authority does not independently advance canonical PlayerGlobalRevision, FactionDomainRevision, or SharedWorld canonical state. Engine execution may produce typed proposals/staged results/evidence; Dedicated Server performs canonical commit/revision advancement.

## MD-118 — Materialization Manifest Hardness Is Dependency-Sensitive
A revision/context reference is a hard admission binding whenever accepted material semantics depend on it. PlayerGlobal/FactionDomain/SharedWorld references are not globally classified as hard or diagnostic. Declare and bind dependencies per admitted profile/artifact.

## MD-119 — Reconstructible Context Requires Noninterference Evidence
A global subsystem may be treated as reconstructible/discardable only after evidence shows rebuild/discard cannot change supported MapSegment material state, canonical domain/global state, stable EntityId/custody, or authorized future operation semantics.

## MD-120 — G-Q1 Probe Precedes Exact Global Ownership Closure
Use targeted runtime evidence to classify global subsystems before freezing final PlayerGlobal/SharedWorld field ownership. The next decisive artifact is a G-Q1 runtime probe contract, not a full PlayerGlobal physical schema.

## MD-121 — Pipeline REV5 Enters E2 Queue, Not Parallel Dispatch
Accept REV5 as E1 PASS developer evidence and freeze the exact candidate.
Do not interrupt Sol's active Engine Gate04 E2.
Pipeline REV5 E2 is queued and becomes dispatchable only after Sol returns Gate04.
No ADR-001 Foundation implementation is released before REV5 independently passes E2.

## MD-122 — ABORTED Recovery Must Validate Historical Meaning, Not Only Range
For a durable stale/CAS rejection, recovery must establish requested ExpectedRevision, ObservedRevisionAtDecision, rejection reason/status, and zero success children.
A predicate such as `0 <= observed <= current && observed != expected` is not sufficient if a false historical observation can be substituted without detection.
Use an immutable/typed decision binding or equivalent durable semantic proof.

## MD-123 — Schema V6 Reopens Candidate Schema Verification
QA-PIPELINE-008 remains CLOSED for independently verified V5.
REV5 intentionally changes schema to V6, so V6 must independently re-prove the closed schema guarantees before Production acceptance.

## MD-124 — Pipeline REV5 Packaging Evidence Must Be Exact
The frozen candidate must expose an identifiable current release manifest containing candidate binary hashes/MVIDs, schema version/signature, relevant source/PDB lineage, E1 result hash, and package inventory sufficient to distinguish REV5 from earlier candidates.
A test name alone is not evidence of a manifest artifact.

## MD-125 — Gate04 Fails E2; Fresh Validator Mechanism Is Retained

Decision:
Do not revert the fresh-process validator architecture.

Gate04 established that a fresh RimWorld process can load exact staged bytes and compare supported semantic state.

Gate05 must fix the provenance/control path:
- who creates the validation task;
- where the expected sealed result comes from;
- how the simulator knows the validator result belongs to that exact task/result/stage.

## MD-126 — Validator Task Is Simulator/Operator-Owned, Not Caller-Nominated

Decision:
The simulator/operator creates an immutable `ValidatorTask` from its own current sealed result.

A caller may request validation to run, but may not supply:
- expected manifest JSON/hash;
- SealedResultId/epoch authority;
- arbitrary receipt;
- arbitrary validator identity.

Preferred Gate05 PoC shape:
1. simulator has immutable current SealedResult;
2. simulator creates random ValidatorTaskId/capability bound to exact stage/result/context;
3. simulator/operator launches a fresh validator process;
4. expected result is supplied from the task generated by the simulator, not from a caller field;
5. validator loads exact staged SHA and computes actual manifest;
6. validator returns task-bound result over an operator-controlled channel/capability;
7. simulator creates/accepts StageValidationReceipt only for that exact task.

Public-key cryptography is not required.
A process-owned local pipe + unguessable task capability/nonce or equivalent operator-controlled mechanism is sufficient for the PoC threat model.

## MD-127 — Public Caller-Submitted Receipt Is Not Promotion Authority

Decision:
`SUBMIT_STAGE_VALIDATION_RECEIPT <caller JSON>` must not be a generic public authority transition.

Promotion authority must originate from an internally registered validator task/result.

If a compatibility/debug submit command remains, it cannot transition the canonical simulator into STAGED_VALIDATED unless the receipt can be matched to an outstanding operator-owned validator task and its protected result channel/capability.

PID inequality is diagnostic only, never issuer proof.

## MD-128 — Complete Result/Receipt Context Is Closed-Schema Equality

Decision:
Stage validation and promotion must bind and compare every authority-defining field in the supported contract, including:
- ValidatorTaskId/capability;
- staged path + staged SHA;
- source artifact hash;
- AuthorityId;
- StoreIncarnation/baseLineage placeholder;
- GrantId;
- WorkerGeneration;
- scopeId;
- stable target context/map identity;
- allowed operation mode;
- ContentProfileFingerprint;
- SupportedSemanticManifest version;
- SealedResultId;
- ResultEpoch/currentResultEpoch;
- sealed manifest hash;
- actual validator-computed manifest hash.

No "carried but unchecked" authority field is allowed.

## MD-129 — Control-Plane Validation Failures Revoke Stale Capabilities

Decision:
For authority/grant/profile/input/validator-task/receipt validation commands, any malformed or semantically invalid attempt clears stale execution/promotion capabilities according to the state machine:
- trustedSimulationReady false;
- active seal/stage receipt invalid where relevant;
- STEP/SEAL/STAGE/PROMOTE blocked until explicit clean reset/re-admission.

Ordinary read/query syntax errors need not revoke unrelated authority; this decision applies to control-plane authority transitions.

## MD-130 — ContentProfile Uses an Actual Loaded-Content Manifest

Decision:
ModsConfig XML hash alone is not the accepted ADR-006B ContentProfileFingerprint.

Gate05 PoC must construct a canonical content manifest from actual admitted content sufficient to detect authority-relevant drift.

At minimum include/bind:
- RimWorld build/version and relevant core assembly identity;
- active mod package IDs/order;
- admitted mod assembly SHA/MVID inventory;
- DLC/mod version/content identity available to the runtime;
- canonical Def/content census or another ADR-006B-compatible semantic content digest;
- profile schema/version/capabilities.

Expected profile is operator-approved; Worker and validator independently compute/verify actual loaded profile before trusted admission/validation.

## MD-131 — Unsafe Replacement Fallback Is Fail-Closed

Decision:
For an existing approved final, if the verified same-volume atomic replacement primitive cannot be used, promotion fails closed and preserves the prior final.

Do not fall back to copy-overwrite/delete for canonical promotion.

A first-time final with no prior file may use a separately validated same-volume atomic rename/move path.

## MD-132 — Gate04 Semantic Scope Is Corrected to Actual V4 Evidence

Decision:
Current V4 supported manifest evidence includes:
- active JobDef;
- active job loadID;
- targetA/B/C representations implemented by the census;
- reservation claimant/job/target/maxPawns/stackCount;
plus the other declared V4 fields independently exercised.

This does not certify the complete RimWorld Job/JobDriver/toil/path/expiry/queue state graph.

Stale V3 shipped census JSON is not a V4 authority oracle and must be replaced/versioned explicitly in Gate05 evidence.
