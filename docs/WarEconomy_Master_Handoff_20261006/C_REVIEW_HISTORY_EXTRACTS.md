# Historical Master Review Extracts

Source: history/MASTER_PROJECT_STATE_MSR-067.md. Sections are reproduced without rewriting. Selected by heading: briefs, ADR reviews, boundary/Genesis/acceptance/dependency topics. Not every excerpt is claimed to be a C-authored document; these are Master governance records. Active-work rows and dates inside are historical. Use current root snapshot/corrections. Full history is bundled, so omitted extract is not missing full record.

## Extract index
- 13. MSR-003 Delta — ADR-006A Accepted
- 19. MSR-009 Delta — C Canonical State / Ordinary Authority Decision Brief
- 20. MSR-010 Delta — ADR-003 / ADR-007 Draft-1 Review
- 22. MSR-012 Delta — ADR-003 / ADR-007 v2 Review
- 23. MSR-013 Delta — ADR-003 Accepted
- 24. MSR-014 Delta — Independent Remote Presentation QA + ADR-007 v3 Review
- 25. MSR-015 Delta — ADR-007 Accepted Core Contract
- 26. MSR-016 Delta — ADR-008 Work Package Started
- 28. MSR-018 Delta — ADR-008 Draft-1 Review
- 29. MSR-019 Delta — ADR-008 Accepted Core Contract
- 30. MSR-019 Active Work Addition — ADR-006B Started
- 32. MSR-021 Delta — ADR-006B Draft-1 Review
- 34. MSR-023 Delta — ADR-006B Accepted
- 36. MSR-025 Delta — ADR-004 Draft-1 Review
- 37. MSR-026 Delta — ADR-004 Accepted
- 41. MSR-030 Active Work — ADR-005 Started
- 43. MSR-032 Delta — ADR-005 Draft-1 Review
- 44. MSR-033 Delta — ADR-005 Accepted
- 45. MSR-034 Delta — Open Decision Dependency Map Adopted with Master Corrections
- 48. MSR-037 Delta — G-Q8 Inventory Boundary Decision Brief Review
- 51. MSR-040 Delta — G-Q1 Ordinary Multi-Settlement Topology Brief Review
- 53. MSR-042 Delta — G-Q2 Ordinary Client Trust Brief Review
- 57. MSR-046 Delta — G-Q6 Disconnect/Grace Brief Review
- 58. MSR-047 Delta — Player-Global State Boundary Review
- 60. MSR-049 Delta — Settlement Genesis Authority Brief Review
- 67. MSR-056 Delta — ADR-001 Production Foundation Acceptance Brief
- 68. MSR-057 Delta — Pipeline REV3 E2 + Registry Acceptance Brief
- 69. MSR-058 Delta — TradeConfiguration Acceptance Brief
- 71. MSR-060 Delta — E-B Live Barrier / Delta Acceptance Brief
- 73. MSR-062 Delta — G-Q1 Temporal Topology Decision Brief REV2
- 76. MSR-065 Delta — PlayerGlobal / SharedWorld Temporal Boundary 01

## 13. MSR-003 Delta — ADR-006A Accepted

- `ADR-006A_Temporal_Authority.md` reviewed and accepted by Master with amendments/policy decisions.
- Temporal authority is now an upstream contract for ADR-002, ADR-003, and ADR-004.
- Primary publication direction is B2 / Target-Scoped Outcome Publication & Canonical Merge.
- Full Worker save wholesale publication remains prohibited.
- QA-ENGINE-004 remains OPEN until the accepted temporal contract is implemented and independently verified.
- Dev A's retained World/global dispatch paths must now be judged against ADR-006A, not developer labels such as "passive" or "read-only".



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
