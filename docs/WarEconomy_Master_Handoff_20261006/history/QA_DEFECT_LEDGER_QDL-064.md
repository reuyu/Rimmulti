# QA_DEFECT_LEDGER.md

Project: WarEconomy / RimMulti
Ledger Revision: QDL-064
Date: 2026-10-02

> Status in this ledger is controlled by Master decisions and independent QA evidence.

| ID | Severity | Status | Owner / Next Track | Blocking | Summary |
|---|---|---|---|---|---|
| QA-001 | High/Critical historical | OPEN | Foundation | Foundation | Identity/auth/version bypass |
| QA-002 | High | OPEN | Foundation | Foundation | No server persistence |
| QA-003 | Critical | OPEN | ADR-004 | Ownership/transfer | Distributed transfer non-atomic |
| QA-004 | High | OPEN | ADR-003/004 | Ownership/inventory | Incomplete ownership scope |
| QA-005 | High | OPEN | Foundation | Operations | TransferId / operation collision risk |
| QA-006 | High | OPEN | War | War | WarPending tier logic mismatch |
| QA-007 | High | OPEN | Tax/ADR-003 | Economy | Tax delinquency semantics mismatch |
| QA-008 | High | OPEN | Visit | Visit | Forged Visit HostPlayerId |
| QA-009 | High | OPEN | Visit | Visit | Cancel/Accept race |
| QA-010 | High | OPEN | Vision | Vision | Old fog behavior conflict |
| QA-011 | High | OPEN | Networking | Reconnect | Partial frame / missing epoch fencing |
| QA-012 | High | OPEN | ADR-004 | Recovery | Rollback / durable repair |
| QA-013 | High | OPEN | Economy | Market | NPC market trust/replay/etc. |
| QA-014 | Medium/High | OPEN | Visit/UI | Visit | Static/concurrency UI issues |
| QA-ENGINE-001 | Critical | PARTIAL / OPEN | Tactical hardening | ADR-002 | Non-target/world progression; normal scoped filter improved but global/load/clock escape remains |
| QA-ENGINE-002 | Critical | OPEN / STILL FAILING / STILL FAILING | Dev A + Verification B | ADR-002 | Missing/undeclared dependency can reach READY/SAVED with semantic loss |
| QA-ENGINE-003 | High | OPEN / PARTIAL / STILL FAILING | Dev A + Verification B | ADR-002 | Unsafe monolithic RUN_TICKS / unbounded slice starvation path |
| QA-ENGINE-004 | Critical | OPEN / STILL FAILING — ARCHITECTURE DEFINED, IMPLEMENTATION UNVERIFIED | Dev A + Verification B / Temporal integration | ADR-002 | ADR-006A now defines W/L/G/M separation and B2 publication; implementation/runtime proof still required |
| QA-ENGINE-005 | High | OPEN / STILL FAILING | Dev A + ADR-006A | ADR-002 | Global tick dispatch coverage / debug escape |
| QA-ENGINE-006 | High | OPEN / STILL FAILING | Dev A + Verification B | Engine Gate | Fixture/oracle cannot prove complete graph success |
| QA-ENGINE-007 | High | CLOSED | Dev A + ADR-006A | ADR-002 | Scope/authority fence not active before load/READY mutations |
| QA-ENGINE-008 | Medium | CLOSED | Dev A | Engine Gate | START uses prior frame elapsed time as simulation backlog |

## Notes

### QA-ENGINE-002
Independently reproduced by Sol and additionally supported by Verification B:
actual semantic loss can reach READY when `LOAD_SAVE` does not enforce complete dependency validation.

### QA-ENGINE-003
Sol independently reproduced a long RUN_TICKS path causing ~27s command starvation.
Verification B's sequential post-run polling does not invalidate this finding.

### QA-ENGINE-004
Architecture-level temporal problem.
Do not "fix" by arbitrary local patch before ADR-006A defines time-domain semantics.

### QA-ENGINE-006
Positive acceptance fixtures should be engine-valid.
Hand-authored XML is acceptable for deliberate negative/corruption tests, not as the sole basis for graph-integrity acceptance.

## Closure Rule

A defect is not closed by:
- successful build
- one happy-path test
- developer self-declaration
- a workaround that weakens the SRS
- an ADR proposal without implementation/evidence where runtime proof is required

Closure requires:
1. correct architectural decision where needed,
2. implementation/fix,
3. targeted regression evidence,
4. independent QA when severity/scope requires it,
5. Master closure decision.

## QDL-002 Developer Hardening Submission Note

Gemini A submitted self-test evidence claiming fixes for QA-ENGINE-002, 003, 005, 006, 007, and 008.

Official statuses are **not changed yet**.

Reasons:
- independent regression has not run against the exact hardened implementation;
- QA-ENGINE-004 is explicitly architectural and remains OPEN;
- QA-ENGINE-005 may have changed global/world dispatch policy and needs authority-scope review;
- QA-ENGINE-006 engine-generated fixture/oracle is promising but requires independent validation;
- QA-ENGINE-007 MapProbe-only load-drift evidence does not by itself prove full non-target/world preservation.

## QDL-003 ADR-006A Acceptance Note

ADR-006A is now ACCEPTED.

This changes the **oracle**, not the defect closure state.

Implications:
- QA-ENGINE-004 now has an accepted target contract but remains OPEN until implementation and independent verification.
- QA-ENGINE-005 must classify retained World/GameComponent/global dispatch against the accepted B2 write/read boundary.
- QA-ENGINE-007 load fencing must demonstrate that foreign/world state cannot become accepted canonical mutation and cannot causally contaminate target computation outside approved projections.
- QA-ENGINE-002 manifest/semantic failure gates must be compatible with temporal materialization/READY validation.
- QA-ENGINE-006 fixtures/oracles should include temporal-domain and cross-boundary assertions when B2 merge validation begins.

## QDL-004 Verification Availability Note

Gemini B's interrupted verification run has no accepted verdict.

For the current Tactical Worker candidate:
- QA-ENGINE-002/003/004/005/006/007/008 official statuses remain unchanged.
- Dev A evidence remains developer evidence.
- Sol independent verification will serve as the current independent closure evidence source.
- No defect may be closed based solely on A's self-reported hardening PASS.

## QDL-005 Documentation Governance Note

Formal ADR files now exist for ADR-001, ADR-002, and ADR-006A. No QA defect status changed as a result of documentation formalization.

## QDL-006 External Red-Team Architecture Note

No QA defect is closed or newly confirmed solely from the external review summary.

However, future QA must cover:
- ordinary simulation provenance and stale ordinary saves;
- stable cross-process entity identity and collision/rebinding failures;
- concurrent Tactical vs trade/tax mutations;
- remote client control/render path under Candidate C;
- untrusted save/materialization type/mod/content injection boundaries.

Existing QA-ENGINE states are unchanged.

## QDL-007 Full Red-Team Review Note

The complete `ARCH_REDTEAM_REVIEW_001.md` was reviewed.

No runtime QA defect is opened or closed solely from this architecture review.

Future acceptance suites must include:
- ordinary owner-client writer lease and stale/forged checkpoint handling;
- multi-settlement divergent-clock behavior;
- online owner trade/tax crash conservation;
- three-writer entity-ID collision/rebinding;
- approved-content classification and runtime non-weaponization;
- hostile checkpoint XML/type/schema rejection before Worker load;
- Tactical crash exploitation/recovery semantics;
- live World-domain event injection during Tactical;
- W restart monotonicity against committed operation timestamps;
- concurrent Occupy/SettlementLimit reservation.

B2-specific proof obligations:
- whole target artifact extract/rematerialize,
- cross-process ID stability,
- Global State Disposition Table completeness,
- temporal reprojection on ingress/egress,
- typed cross-boundary manifest,
- server-authored delta application,
- live hostility/domain-event roundtrip,
- artifact-before-pointer commit ordering,
- explicit B2 falsification trigger.

## QDL-008 Sol Independent QA Gate

Source:
`QA_Tactical_Worker_Hardening_Independent_Review.md`

Master closure decisions:
- QA-ENGINE-007 CLOSED — verified mechanical pre-load autonomous tick fence. This does not certify semantic READY correctness.
- QA-ENGINE-008 CLOSED — verified START elapsed-debt fix.

Remaining:
- QA-ENGINE-002 OPEN / STILL FAILING
  - Missing RecipeDef caused bill 1→0 while READY/SAVED.
  - Cross-registry wrong typed Def caused Battery loss while READY/SAVED.
  - Invalid body-part reference caused BionicEye loss while READY/SAVED.
- QA-ENGINE-003 OPEN / PARTIAL
  - normal RUN quarantine, STEP cap, cancel, server-timeout expiry improved;
  - disconnected client request can execute later;
  - diagnostic monolithic tick bypass remains;
  - lease/generation/deadline admission remains incomplete.
- QA-ENGINE-004 OPEN / STILL FAILING
  - foreign chronological getter still follows incidental Worker G;
  - typed temporal materialization and B2 publication are not implemented.
- QA-ENGINE-005 OPEN / STILL FAILING
  - world/history/tales and fastEcology defenses improved;
  - GameComponent dispatch remains mutable; native Anomaly timer changed;
  - foreign/global queries can causally enter target computation.
- QA-ENGINE-006 OPEN / STILL FAILING
  - fixture validity improved substantially;
  - final oracle is not trustworthy: 9/11 targeted negative corruptions were false negatives, plus inventory deletion was not tested by final predicate.

Regression locks:
- Any next candidate must preserve QA-ENGINE-007 zero autonomous tick behavior through READY.
- Any next candidate must preserve QA-ENGINE-008 no pre-START debt behavior.

## QDL-009 C Architecture Brief Note

No runtime QA defect changes result from the C decision brief.

New future acceptance requirements:
- B2-lite whole-target artifact replacement must be tested under exclusive material-state lease.
- queued Tactical-vs-Economy operations must be revalidated after Tactical publication and preserve asset conservation.
- cross-process EntityId allocation/binding must survive split/merge/create/destroy and fresh reload.
- owner checkpoints must be validated as hostile input before becoming canonical candidates.

Existing QA-ENGINE states from QDL-008 remain unchanged.

## QDL-010 ADR Draft Review Note

No defect status changes.

Future QA/ADR acceptance tests added:
- lease handoff cannot depend on a post-revocation client upload;
- stale old writer submissions rejected by monotonic fencing generation;
- queued Tactical-time Economy operations do not stale the active Worker candidate before publication;
- canonical projection/index can be rebuilt or verified from committed artifact + operations;
- server EntityId collisions are tested only for canonical/server-addressable entities without forcing a field-level event log for every internal Thing mutation;
- untrusted checkpoint tests include semantic loss/forgery, not just XML schema validity.

## QDL-011 Remote Presentation Validation Note

No existing QA-ENGINE defect state changes.

New Remote Presentation acceptance obligations:
- RP-AC-01: independent reproduction of own-Pawn command -> Worker execution -> client mirror reconciliation.
- RP-AC-02: unauthorized/foreign Pawn command rejection using server-authorized identity/generation.
- RP-AC-03: stale presentation generation rejection after reconnect/handoff.
- RP-AC-04: normal graphical client (not `-batchmode -nographics`) renders the mirrored map and preserves camera/selection/inspect/gizmo interaction.
- RP-AC-05: actual OnGUI/right-click/gizmo interception is demonstrated in the graphical lifecycle, not only model-method invocation.
- RP-AC-06: domain transactions from peaceful visits are routed through Server authority without local mirror becoming canonical.
- RP-AC-07: WAN/network latency and bandwidth remain unaccepted until measured outside loopback; no projected number is a final SLO.
- RP-AC-08: mirror snapshot scope expands beyond a few Pawn fields without producing destructive divergence for supported tactical state.


## QDL-012 ADR v2 Review Note

No existing defect status changes.

Additional future validation obligations:
- pending uncommitted operations never enter a canonical materialization;
- artifact replay watermark prevents duplicate or skipped delta application;
- online ordinary server-authored trade/tax does not invalidate or resurrect owner-client progress;
- HANDOFF_BARRIER / DELTA_BARRIER rejects racing checkpoints and stale fencing generations;
- stable EntityId survives native loadID rebinding across at least two independent engine instances;
- semantic validation Worker cannot convert untrusted input into canonical state without server commit.


## QDL-013 ADR-003 Acceptance Note

ADR-003 is now ACCEPTED architecture.

No runtime QA defect closes automatically.

Future validation must prove:
- deterministic replay from ArtifactBaseStateRevision;
- no pending operation enters canonical materialization;
- committed operations survive client disconnect before local application;
- stable EntityId across native loadID rebinding;
- projection/index rebuildability;
- hostile semantic validation before canonical acceptance.


## QDL-014 Remote Presentation Independent Findings

Independent QA accepted.

Remote Presentation findings for the current PoC revision:
- QA-PRESENT-001 HIGH OPEN — real GUI input bypasses remote command path.
- QA-PRESENT-002 HIGH OPEN — no operational Worker simulation / periodic replication cadence.
- QA-PRESENT-003 HIGH OPEN — response/snapshot freshness and map binding not fenced.
- QA-PRESENT-004 HIGH OPEN — reconciliation scope/native callback divergence.
- QA-PRESENT-005 MEDIUM OPEN — rotation wire encoding mismatch.
- QA-PRESENT-006 HIGH-IF-PROMOTED OPEN — fixture tokens / privileged debug control plane.
- QA-PRESENT-007 HIGH-IF-PROMOTED OPEN — main-thread blocking / unbounded dispatch.
- QA-PRESENT-008 MEDIUM OPEN — evidence oracle / metric overstatement.
- QA-PRESENT-009 HIGH OPEN — fixture dependency semantic load errors.
- QA-PRESENT-010 MEDIUM OPEN — snapshot target bound to currently viewed Map.

These are presentation-PoC findings and do not automatically change QA-ENGINE-002..008.

Remote Presentation feasibility gate remains OPEN.


## QDL-015 ADR-007 Acceptance Note

ADR-007 core lease/handoff architecture is ACCEPTED.

No runtime defect status changes automatically.

Future validation must prove:
- single-writer lease/fencing across client↔Worker handoff;
- DELTA_BARRIER designated-checkpoint ordering;
- post-commit client failure preserves committed operation;
- lease-base synchronization does not incorrectly advance artifact watermark;
- stale writer submissions are rejected after FencingGeneration advance;
- unresolved G-Q1/G-Q2/G-Q6 are not silently encoded by implementation.


## QDL-016 A Remote Presentation Hardening Report

Developer claim received; independent closure pending.

Candidate claims mapped to existing findings:
- QA-PRESENT-001: A claims FIXED — actual GUI Draft/Move now intercept into RPC.
- QA-PRESENT-002: A claims FIXED/PARTIAL — bounded autonomous Worker cadence implemented.
- QA-PRESENT-003: A claims FIXED — session/generation/map/sequence snapshot fencing.
- QA-PRESENT-004: A claims PARTIALLY HARDENED — narrow position/Draft/rotation/job/health reconciliation.
- QA-PRESENT-005: A claims FIXED — canonical named rotation encoding.
- QA-PRESENT-006: A claims TEST-SURFACE ISOLATED, not Production auth solved.
- QA-PRESENT-007: not considered closed; synchronous/blocking and bounded-dispatch behavior requires independent inspection.
- QA-PRESENT-008: prior metric overstatement must be independently re-measured.
- QA-PRESENT-009: A claims dependency-clean profile.
- QA-PRESENT-010: A claims FIXED via TargetMapId/session binding.

Official ledger state:
All QA-PRESENT-001..010 remain OPEN until independent Sol re-verification.


## QDL-017 ADR-008 Draft Review Note

No QA defect status changes.

Future ADR-008 validation obligations identified:
- stale world/custody revisions cannot move or duplicate a caravan;
- ingress/egress never yields zero-custody or double-custody after failure/restart;
- hidden WorldObjects are absent from unauthorized client projections;
- transit clock/materialization preserves Pawn/Animal/Item identity and timer semantics;
- server-controlled pathing/materialization cannot be replaced by untrusted client facts;
- offline economy operations use engine validation whenever projection/index facts are insufficient.


## QDL-018 ADR-008 Acceptance Note

ADR-008 core architecture is ACCEPTED.

No existing runtime defect closes automatically.

Future validation obligations:
- WorldObjectRevision stale-operation rejection survives restart/races;
- split/merge cannot duplicate or lose custody;
- ingress/egress failure never yields double-custody or zero-custody;
- hidden WorldObjects/intelligence are absent from unauthorized projections;
- TransitClock reprojection preserves age/rot/duration semantics;
- server-controlled path executor matches supported vanilla/DLC/approved-mod behavior;
- engine-free offline operations are rejected when required semantic facts are absent from the durable projection/index.

## QDL-019 Remote Presentation Independent Closure Update

### CLOSED
- **QA-PRESENT-001 — CLOSED**: real graphical GUI -> RPC -> Worker path independently confirmed; no pre-accept local authoritative success; foreign GUI command rejection preserves state.
- **QA-PRESENT-003 — CLOSED**: sequence/session/generation/map response admission and delayed old-response rejection independently confirmed.

### OPEN / PARTIAL
- QA-PRESENT-002 — PARTIAL: no automatic repeated replication.
- QA-PRESENT-004 — PARTIAL: job/health/lifecycle reconciliation incomplete.
- QA-PRESENT-005 — STILL FAILING: rotation mismatch.
- QA-PRESENT-006 — STILL FAILING: test-control bypass.
- QA-PRESENT-007 — PARTIAL: blocking/unbounded/legacy monolithic paths remain.
- QA-PRESENT-008 — STILL FAILING: evidence/metric oracle errors remain.
- QA-PRESENT-009 — STILL FAILING: dependency semantic load errors remain.
- QA-PRESENT-010 — STILL FAILING: reconciliation target remains `Find.CurrentMap`.

Existing QA-ENGINE defects remain unchanged.


## QDL-020 ADR-006B Draft Review Note

No existing defect closes.

Future validation obligations identified:
- missing ThingDef/RecipeDef/HediffDef/body-part/component dependencies are detected before canonical acceptance;
- content/profile mismatch cannot enter a writer lease or canonical checkpoint path;
- runtime semantic failure enters quarantine/repair without silently dropping objects;
- migration preserves old-profile readability and validates the transformed artifact under the new profile;
- operation-snapshotted config remains deterministic after later ConfigRevision changes;
- cosmetic/profile exceptions cannot invoke authority-sensitive mutation hooks.


## QDL-021 ADR-006B Acceptance Note

ADR-006B core architecture is ACCEPTED.

No existing runtime defect closes automatically.

Future proof obligations:
- exact profile mismatch is rejected before writer/materialization admission;
- missing Def/Recipe/Hediff/body-part/component/reference failures are detected by layered semantic validation;
- no silent object/component drop becomes canonical;
- old-profile artifacts remain readable by the migration path before transformation;
- failed migration does not advance the active ContentProfileRevision;
- OPERATION_SNAPSHOTTED config replays deterministically after later config changes;
- cosmetic capability exceptions cannot reach authority-sensitive mutation paths.

## QDL-022 Hardening-02 Developer Claims — Independent Closure Pending

A claims:
- QA-PRESENT-002 fixed for the tested Move slice via periodic controller replication;
- QA-PRESENT-005 fixed via canonical rotation wire contract;
- QA-PRESENT-009 resolved for this candidate by dependency-complete profile;
- QA-PRESENT-010 fixed via authority-bound map resolution;
- test-control isolation improved;
- cadence debt bug fixed.

Official status before E2:
- QA-PRESENT-001 — CLOSED
- QA-PRESENT-003 — CLOSED
- QA-PRESENT-002 — OPEN / claimed fixed, verify
- QA-PRESENT-004 — OPEN / PARTIAL
- QA-PRESENT-005 — OPEN / claimed fixed, verify
- QA-PRESENT-006 — OPEN / SECURITY RECHECK REQUIRED
- QA-PRESENT-007 — OPEN / PARTIAL
- QA-PRESENT-008 — OPEN / claimed evidence cleanup, verify
- QA-PRESENT-009 — OPEN / claimed candidate-local resolution, verify
- QA-PRESENT-010 — OPEN / claimed fixed, verify

Security-specific attack:
Attempt privileged control commands with:
- invalid/ordinary token + forged `Source = QA_TEST_CONTROL`;
- stale generation + privileged-looking source;
- wrong session + privileged-looking source.
A string/source marker controlled by the remote client is not sufficient privilege proof.

Existing QA-ENGINE defects remain unchanged.

## QDL-023 ADR-004 Draft Review Note

No runtime defect status changes.

Future transaction proof obligations refined:
- kill/restart after durable staged material but before COMMIT;
- kill/restart after COMMIT before promotion;
- loss/corruption of staged candidate;
- committed operation whose result is not fully replayable from typed operations;
- deterministic committed-vs-not-committed recovery after crash during DB transaction;
- PREPARED lock expiry/deadlock recovery;
- caller disconnect after PREPARED where Server can still safely commit;
- stale candidate promotion attempt against wrong base/head/profile/hash;
- projection/outbox lag repaired without changing canonical truth.


## QDL-024 ADR-004 Acceptance Note

ADR-004 core architecture is ACCEPTED.

No existing runtime defect closes automatically.

Required future E1/E2/E3 transaction tests:
- kill/restart at PREPARED, COMMITTING, COMMITTED/PUBLISH_PENDING;
- same OperationId same payload idempotent retry;
- same OperationId different payload rejection;
- deterministic multi-scope reservation ordering and restart cleanup;
- stale writer publication after post-commit fence advance;
- committed typed-replay recovery;
- committed staged-result recovery;
- staged-result corruption/hash mismatch;
- orphan staged-result GC safety;
- projection/outbox replay;
- split/merge nested EntityId custody;
- source/destination race with one-owner invariant;
- post-commit semantic/publication failure entering forward repair without erasing canonical decision.


## QDL-025 Remote Presentation E2 Closure Update

### CLOSED
- **QA-PRESENT-001 — CLOSED**
- **QA-PRESENT-002 — CLOSED**
- **QA-PRESENT-003 — CLOSED**
- **QA-PRESENT-005 — CLOSED**
- **QA-PRESENT-010 — CLOSED**

### OPEN
- **QA-PRESENT-004 — STILL FAILING / HIGH**
  - native Position converges but DrawPos/rendered sprite stays stale;
  - rendered position / hit target / presentation state diverge;
  - health graph reconciliation remains incomplete.

- **QA-PRESENT-006 — STILL FAILING / HIGH-IF-PROMOTED**
  - forged remote `Source=QA_TEST_CONTROL` bypasses token/session/generation protections for privileged controls.

- **QA-PRESENT-007 — STILL FAILING / HIGH-IF-PROMOTED**
  - synchronous main-thread snapshot read; delayed response stalls frames/control path;
  - timeout/reconnect, queue/list bounds and legacy blocking risks remain.

- **QA-PRESENT-008 — PARTIAL**
  - operational metrics improved;
  - A evidence oracle still misclassifies direct native method invocation as graphical user evidence and omits DrawPos/display oracle.

- **QA-PRESENT-009 — PARTIAL**
  - declared dependencies complete;
  - remaining asset/init/listener/headless errors prevent clean-load certification.

Existing QA-ENGINE-002..006 remain unchanged.


## QDL-026 Pipeline Design Review Note

No runtime defect status changes.

Design-level proof obligations carried forward:
- PREPARED recovery chooses abort vs autonomous completion from durable completeness + operation policy, not timeout alone;
- typed-operation and staged-material recovery paths remain distinct;
- artifact watermark lag is tolerated without changing canonical head;
- first Production pipeline slice must not encode unresolved G-Q8/G-Q9/TBD-05 policy;
- duplicate retry, stale revision, post-commit outbox failure, restart recovery, and stale lease publication require explicit sequence/test definitions before implementation authorization.


## QDL-027 Pipeline Design-02 Acceptance Note

No runtime QA defect closes.

New Production Slice-01 proof obligations:
- same OperationId + same payload returns stable receipt under concurrency;
- same OperationId + different payload is rejected;
- stale ProbeRevision CAS cannot commit;
- only one concurrent CAS winner advances ProbeRevision;
- crash/restart after durable PREPARED is deterministic;
- crash/restart after COMMITTED before outbox delivery preserves canonical probe result;
- outbox replay is idempotent;
- DB transaction crash resolves committed vs not-committed deterministically;
- no gameplay Settlement revision/state changes during the probe;
- probe/control surface is inaccessible to ordinary gameplay clients in release configuration;
- WAL/synchronous/unique-constraint behavior is recorded as evidence.

ADR-004 staged-material, Settlement artifact, EntityId custody, and gameplay mutation proofs remain future scopes.

## QDL-028 Hardening-03 Developer Claims — Independent Verification Pending

Official statuses remain unchanged pending E2:
- QA-PRESENT-001 — CLOSED
- QA-PRESENT-002 — CLOSED
- QA-PRESENT-003 — CLOSED
- QA-PRESENT-004 — OPEN / STILL FAILING from prior E2; A claims rendered sub-blocker fixed
- QA-PRESENT-005 — CLOSED
- QA-PRESENT-006 — OPEN / STILL FAILING from prior E2; A claims separate control boundary fixed
- QA-PRESENT-007 — OPEN / STILL FAILING from prior E2; A claims non-blocking transport fixed
- QA-PRESENT-008 — PARTIAL; A claims evidence oracle/metrics corrected
- QA-PRESENT-009 — PARTIAL; A claims candidate-local init cleanup
- QA-PRESENT-010 — CLOSED

Focused E2 closure criteria:
- 004 rendered-position/hit-target sub-scope: actual visible movement + actual user selection/click consistency;
- 006: forged Source/token/session/generation cannot gain privileged control on gameplay transport; control endpoint privilege derived from trusted channel/capability;
- 007: delayed/closed/late transport cannot block Unity main thread or apply stale state; background thread performs no Unity mutation;
- 008: evidence labels and byte metrics are no longer overstated;
- 009: active profile/logs no longer show candidate-relevant dependency/asset/listener initialization failures.

Existing QA-ENGINE-002..006 remain unchanged.

## QDL-029 ADR-005 Draft Review Note

No runtime defect statuses change.

Future ADR-005 proof obligations identified:
- multiple projectile/hit facts under one authorized action are not deduplicated away;
- duplicate FactId is idempotently rejected;
- autonomous trap/turret/mental-state facts carry recoverable causal provenance;
- stale diplomacy revision at authorization/execution/decision is handled deterministically;
- committed relationship transition is delivered/replayed to Worker in order without making Worker domain authority;
- Worker crash after execution cannot silently publish material state while losing required betrayal provenance;
- reconnect/replay does not duplicate betrayal decisions or relationship transitions;
- delayed Worker ACK does not roll back committed diplomacy state.


## QDL-030 ADR-005 Acceptance Note

ADR-005 core architecture is ACCEPTED.

No runtime defect closes automatically.

Future E1/E2/E3 proof obligations:
- one AuthorizedAction produces multiple FactIds without loss or false dedupe;
- duplicate FactId is idempotently ignored/rejected;
- IntentId -> ActionExecutionId -> FactId correlation survives network/reconnect/replay;
- autonomous trap/turret/mental-state actions preserve causal provenance without a PlayerIntent;
- staged Tactical result with missing required political provenance is quarantined;
- scoped diplomacy CAS resolves concurrent relationship changes deterministically;
- committed SessionDomainEvents replay in aggregate-revision order after disconnect/reconnect;
- Worker hot-applies a committed relationship transition and recalculates local hostility/AI without becoming domain authority;
- delayed Worker ACK does not roll back or duplicate the Server's committed political state.

## QDL-031 Decision-Dependency Mapping Note

No runtime defect status changes.

QA sequencing implication:
- PIPELINE_PROBE_CAS may be tested without resolving G-Q8/TBD-05.
- future inventory mutation QA must wait for a defined G-Q8 inventory boundary.
- remote-presentation WAN/UX evidence belongs to G-Q10 acceptance and does not gate offline-attack core correctness tests.
- ADR-005 provenance/event infrastructure can be tested before final G-Q13..17 liability rules are chosen.


## QDL-032 Remote Presentation Hardening-04 E2 Update

### CLOSED
- QA-PRESENT-001 — CLOSED
- QA-PRESENT-002 — CLOSED
- QA-PRESENT-003 — CLOSED
- QA-PRESENT-005 — CLOSED
- QA-PRESENT-006 — CLOSED for PoC/test-control boundary
- QA-PRESENT-010 — CLOSED

### PARTIAL / OPEN
- QA-PRESENT-004 — PARTIAL
  - Rendered movement / DrawPos / hit-target sub-blocker: CONFIRMED RESOLVED
  - Overall reconciliation: STILL FAILING
  - known remaining examples: Hediff severity/body-part/instance/removal semantics and general job/status representation

- QA-PRESENT-007 — STILL FAILING / HIGH
  - periodic polling is non-blocking;
  - interactive Draft/Move command path still performs synchronous socket wait on Unity main thread;
  - ~2s delayed command response caused ~2.03s main-thread stall;
  - interactive command deadlines and full queue/epoch lifecycle remain incomplete.

- QA-PRESENT-008 — PARTIAL
  - evidence labeling improved and actual OS GUI proof independently exists;
  - A metric naming/screenshot-resolution/over-closure claims still need correction.

- QA-PRESENT-009 — PARTIAL
  - missing Def/class/reference and proof texture issue improved;
  - actual auxiliary listener port collision / initialization errors remain.

Existing QA-ENGINE-002..006 remain unchanged.


## QDL-033 Hardening-04 Addendum — New Facing Defect

### NEW
**QA-PRESENT-011 — Dynamic Facing / Authoritative Pose Staleness**
- Severity: MEDIUM
- Status: OPEN
- Scope: Remote Tactical presentation visual correctness
- Requirement area: rendered operational presentation / movement-facing coherence
- Evidence:
  - westward real GUI movement retained Worker `Rotation=East` across 84 consecutive Goto samples;
  - eastward real GUI movement retained Worker `Rotation=West` across 24 samples;
  - Client applied the Worker-provided value correctly.
- Not the same defect as QA-PRESENT-005.
- QA-PRESENT-005 remains CLOSED for enum/wire/native round-trip.

Required closure evidence:
1. record authoritative movement vector / next path cell;
2. record native Worker Rotation;
3. record stance/focus/aim target and any body/head/render facing available;
4. distinguish valid aim-facing from stale movement-facing;
5. for true stale cases, emit/apply an authoritative presentation pose/facing that tracks the correct engine semantics;
6. verify real north/south/east/west movement and direction changes;
7. preserve legitimate stationary/aim/focus facing;
8. retain QA-PRESENT-005 codec correctness and no-client-authority guarantees.

Current presentation statuses:
- QA-PRESENT-004 — PARTIAL
- QA-PRESENT-006 — CLOSED
- QA-PRESENT-007 — STILL FAILING
- QA-PRESENT-008 — PARTIAL
- QA-PRESENT-009 — PARTIAL
- QA-PRESENT-011 — OPEN


## QDL-034 G-Q8 Evidence Planning Note

No runtime defect status changes.

Future G-Q8 E1/E2 proof must distinguish:
- projection enumeration from actual material mutation;
- fungible aggregate keys from underlying entity/stack identity;
- `SettlementEconomicInventory` from `TaxSeizableAssetSet`;
- frozen LocalClock from safe mutation of persisted jobs/reservations;
- pre-commit staged candidate from canonical custody.

Minimum future probes:
- complete ThingOwner/nested-container enumeration;
- loose stack split/remove + save/reload;
- building-contained item removal;
- pawn inventory/equipment/apparel mutation via engine semantics;
- Animal/Slave/Pawn tax-transfer candidate handling;
- reservation/job target mutation;
- caravan/transport staging double-spend fencing;
- stack merge/split EntityId rebinding;
- stale client/checkpoint replay after offline asset mutation.

These proofs are not required for `PIPELINE_PROBE_CAS`.


## QDL-035 Remote Presentation REV1 Developer Evidence Note

No defect closes from A self-report alone.

Pending E2 targets:

### QA-PRESENT-007
A claims asynchronous interactive command I/O and bounded queues.
Independent QA must verify:
- no command socket wait/connect on Unity main thread;
- delayed command does not freeze frames;
- timeout behavior is internally consistent;
- late/old-epoch command response cannot apply;
- queue admission and per-frame drain remain bounded under burst/flood.

### QA-PRESENT-009
A claims corrected `-flag=value` profile binding.
Independent QA must verify actual listeners and startup logs on the exact frozen candidate/profile.

### QA-PRESENT-011
A claims dynamic pose closure.
Independent QA must verify:
- real west/east/north/south movement;
- at least one direction change;
- Worker authoritative pose is semantically current;
- legitimate aim/focus facing is not overwritten incorrectly;
- Client does not infer authoritative facing locally.

### QA-PRESENT-008
Evidence-discipline concern remains:
- some "REAL_GRAPHICAL_OBSERVATION" entries cite native method calls;
- two different screenshot labels report identical size and SHA256;
- the 2s-success vs 800ms-timeout configuration requires clarification.


## QDL-036 Future Trade-Configuration Slice Proof Obligations

No current QA defect closes or reopens.

For the future Auto-Shop configuration slice, require:
- current owner may update only their own Settlement configuration;
- stale/future owner or forged Settlement ownership is rejected;
- ownership epoch changes between validation and commit cause CAS/re-authorization failure;
- same OperationId + same payload returns stable receipt;
- same OperationId + different payload is rejected;
- stale TradeConfigurationRevision cannot overwrite newer config;
- two concurrent config updates have one deterministic revision winner;
- Sell/Buy order setup causes zero inventory reservation;
- Buy order setup causes zero Silver reservation;
- no `CommittedSettlementStateRevision` or artifact watermark changes;
- invalid/unavailable ContentProfile definition reference is rejected;
- crash after commit before outbox replays notification without re-committing config;
- G-Q9 ownership-transfer behavior remains unimplemented/isolated;
- no actual FR-204+ trade execution is accidentally activated.


## QDL-037 G-Q1 Runtime Proof Obligations

No runtime defect status changes.

Future G-Q1 evidence must prove:
- Settlement A and B with divergent LocalClockIds can be sequentially materialized without cross-clock contamination;
- hard unload/reload clears or correctly rebinds relevant global singleton/cache state;
- only the intended Settlement has an active writer lease at each switch in the single-active candidate;
- stale writer/checkpoint from Settlement A cannot publish after Settlement B becomes active;
- crash/reconnect restores the correct Settlement artifact + LocalClock + fencing generation;
- Tactical admission of an inactive Settlement uses canonical server custody, not an owner's stale local artifact;
- if separate-process islands are evaluated, simultaneous progression remains isolated and resource cost is measured.

These are architecture/feasibility obligations, not new QA-PRESENT defect closures.


## QDL-038 Remote Presentation Hardening-05 E2 Update

### QA-PRESENT-004
**STILL FAILING overall**
- rendered Position/DrawPos/hit target: resolved;
- general health/body-part/instance/job reconciliation: unresolved.

### QA-PRESENT-007
**PARTIAL**
Confirmed improvements:
- actual native GUI Draft/Move uses async enqueue;
- interactive socket serialization/write/read occurs off-main;
- main-thread authoritative apply remains on Unity thread;
- 2s delayed native command stayed responsive in the tested loopback window;
- timeout/socket-close/late-response command effects were fenced in the tested cases.

Remaining:
- **H05-01 HIGH** — old-connection periodic response can be parsed before reconnect, then stamped with the new current TransportEpoch at coalescing and incorrectly applied.
- **H05-02 MEDIUM** — `_cmdResultQueue` is unbounded; observed high-water 273 under 1000-command stress.
- **H05-03 MEDIUM** — initial/external reconnect performs synchronous `TcpClient.Connect` on main thread; explicit bounded connect lifecycle absent.

### QA-PRESENT-008
**STILL FAILING**
Evidence discipline mismatches include:
- duplicated byte-identical screenshots presented as different states;
- incorrect REAL_GRAPHICAL_OBSERVATION labeling in A report;
- reported 1280x720 versus actual 1920x1080 captures;
- timeout/queue/history/source-code descriptions not matching the frozen candidate;
- interactive payload size mislabeled;
- reported pose pseudo-code differs from actual frozen source.

### QA-PRESENT-009
**CLOSED — narrow listener/profile subdefect**
- actual runtime ports and `-flag=value` consumption independently verified;
- no candidate bind collision.
Headless atlas/semantic-load concerns remain under QA-ENGINE-002 class.

### QA-PRESENT-011
**CLOSED — tested movement/focus slice**
- actual OS/user movement in four directions;
- path direction changes;
- 93 Worker/wire/client pose samples with mismatch 0;
- real moving+focus samples preserve focus-first Aiming semantics;
- no client-side position-delta facing authority.

Previously closed:
QA-PRESENT-001/002/003/005/006/010 remain CLOSED.

No QA-ENGINE defect is closed by this report.


## QDL-039 G-Q2 Future Proof Obligations

No current runtime defect status changes.

Future G-Q2 E1/E2 probes must include:
- valid-current-parent artifact with forged +Silver: semantic validator acceptance vs provenance detector behavior;
- same admitted ContentProfile cheap-Def -> expensive-Def substitution;
- stale parent artifact rejection;
- duplicate/missing/spoofed EntityId explicit fail-closed rejection without validator crash;
- custody duplication across two otherwise engine-valid artifacts;
- forged Pawn skill/health changes;
- wealth/tier input path proving client artifact cannot directly grant political promotion;
- server-authored typed operation followed by stale/forged checkpoint attempting to erase or contradict it;
- mod/profile mismatch rejection as a separate compatibility test;
- crash/restart/quarantine behavior for rejected candidate artifacts.

Broad deterministic replay of arbitrary ordinary gameplay is not required unless later evidence makes it necessary.


## QDL-040 Pipeline Slice-01 E2 Attack Targets

No existing defect is closed by A's E1 report.

Independent Pipeline E2 must attack at minimum:

1. **Operation fingerprint completeness**
   - reuse OperationId with same PayloadJson but altered ProbeScopeId;
   - altered ExpectedProbeRevision;
   - altered ActorId/principal;
   - altered operation type;
   - altered ContentProfileFingerprint.
   Any semantically different operation must not be treated as a harmless idempotent replay.

2. **CAS under independent connections/processes**
   - 20+ contenders;
   - separate SQLite connections and preferably separate processes;
   - exactly one canonical revision winner;
   - no uncaught SQLITE_BUSY/LOCKED corruption or ambiguous outcome.

3. **Commit-boundary kill**
   - hard kill immediately before/inside/after tx.Commit;
   - restart determines canonical truth solely from durable DB state.

4. **PREPARED package integrity**
   - missing/corrupt fields;
   - tampered payload/hash;
   - incomplete durable reservation;
   - stale expected revision;
   - deterministic abort vs forward recovery.

5. **Outbox duplicate window**
   - side effect succeeds;
   - crash before DELIVERED/PUBLISHED marker;
   - restart redelivers;
   - consumer/idempotency boundary prevents double semantic effect.

6. **Durability configuration**
   - record actual WAL and synchronous mode;
   - justify canonical durability policy;
   - no test-only switch silently weakening Production.

7. **Receipt/audit/outbox uniqueness and restart**
   - no duplicate receipt;
   - no second ProbeRevision;
   - audit remains coherent;
   - operation terminal state converges deterministically.

8. **Gameplay isolation**
   - actual network dispatch cannot invoke probe;
   - internal-only test surface cannot be reached through ordinary authenticated gameplay routing.

9. **Schema/migration/startup recovery**
   - fresh DB;
   - existing schema;
   - failed/partial migration;
   - recovery ordering before accepting gameplay mutations.


## QDL-041 — Pipeline E2 Defects Adopted

All are OPEN.

### QA-PIPELINE-001 — HIGH
Incomplete/caller-controlled operation fingerprint.
Same OperationId can return prior success for changed scope/revision/actor/profile; supplied hash can mask changed payload.

### QA-PIPELINE-002 — HIGH
Corrupt/incomplete PREPARED auto-commits during recovery.

### QA-PIPELINE-003 — HIGH
Live executor/recovery race can overwrite committed/PUBLISHED truth as ABORTED.

### QA-PIPELINE-004 — HIGH
No consumer dedup/idempotency contract for at-least-once external publication effect.

### QA-PIPELINE-005 — HIGH
FAILED publication entries are excluded from recovery and can remain abandoned.

### QA-PIPELINE-006 — HIGH
DELIVERED publication + COMMITTED operation split can remain permanently non-converged.

### QA-PIPELINE-007 — HIGH
Normal server startup has no pipeline initialization/recovery readiness barrier before gameplay admission.

### QA-PIPELINE-008 — HIGH
Schema version/user_version is trusted without logical schema validation; malformed/future schemas may pass initialization.

### QA-PIPELINE-009 — HIGH
Production durability claims exceed actual WAL/synchronous=NORMAL default; power-loss safety unproven.

### QA-PIPELINE-010 — MEDIUM
Concurrent exact same-id retry can escape as SQLite UNIQUE exception instead of stable typed outcome.

### QA-PIPELINE-011 — MEDIUM
Storage/locking errors can be misreported as stale CAS; durable ambiguous-outcome/query policy missing.

### QA-PIPELINE-012 — MEDIUM
CommitReceipt representation/hash is not canonical across reload/time-zone formatting and publication status is conflated with immutable commit receipt.

### Reclassified shared engine blockers
QA-ENGINE-002 and QA-ENGINE-006 remain OPEN and are additionally classified as **Engine Host shared blockers**.
No prior QA defect is closed by MPC-002.


## QDL-042 — Pipeline REV1 Candidate Status

QA-PIPELINE-001..012 remain **OPEN / REV1 FIX CLAIMED / E2 PENDING**.

Do not use REV1 report defect-number mappings as authoritative; QDL-041 original IDs control.

Independent REV1 E2 must re-run the exact original reproductions and the replacement-candidate regression matrix.

Additional verification items:
- QA-PIPELINE-013 candidate watch: Release binary may still contain test/probe harness types or CLI surfaces; inspect and classify after E2.
- QA-PIPELINE-014 candidate watch: Channel executor capacity/backpressure/shutdown semantics were not demonstrated in the developer report; inspect under overload and shutdown.
These are WATCH items, not official defects until independently reproduced.


## QDL-043 — G-Q6 Future Verification Obligations

No new current defect is opened from the C brief.

Future ordinary-authority E1/E2 must test:
- ACTIVE -> SUSPENDED_GRACE -> same-session resume;
- grace expiry -> atomic fence -> replacement writer;
- higher-priority Tactical/domain handoff during grace -> fence before replacement;
- old transport reconnect after replacement -> reject;
- new SessionEpoch reconnect -> old authority invalid;
- torn checkpoint staging -> ArtifactBaseStateRevision unchanged;
- committed server operation before client ACK -> old client cannot erase/override it;
- repeated transport flap without generation leaks;
- normal server restart during grace under the chosen durable/invalidating policy;
- StoreIncarnation mismatch;
- malicious client continuing simulation during transport loss cannot gain additional authority merely by reconnecting.

Exact grace duration and barrier timeout remain policy/config, not QA constants.


## QDL-044 — Player-Global E-A Verification Obligations

No current implementation defect status changes.

Future Engine Host E-A/E2 must test:
- materialize Map A with PlayerGlobalRevision R;
- advance allowed PlayerGlobal state through another context;
- materialize frozen Map B against newer PlayerGlobalRevision without advancing B's LocalClock;
- exact manifest records composed revisions;
- missing required global dependency fails closed/quarantines;
- extra irrelevant global context is not required for correctness;
- Faction reference rebinding after personal-faction lifecycle changes;
- WorldPawn relationship/reference closure;
- ResearchManager/IdeoManager dependency closure;
- raw TicksGame/global timestamp contamination across divergent LocalClocks;
- two simultaneous maps reading one global revision;
- concurrent attempted global mutation produces one canonical ordering, not lost update;
- reconstructible engine-global components can be regenerated without census/reference loss.

These are evidence obligations, not claims that the current PoC already implements PlayerGlobalStateSegment.


## QDL-045 — Pipeline REV1 E2 and Engine E-A Update

### Original QA-PIPELINE status after REV1 E2
- 001 STILL FAILING — ambiguous delimiter-based envelope fingerprint
- 002 CLOSED — fast-path PREPARED removed; future reservation path not certified
- 003 PARTIAL — normal race fixed, storage API can still mutate terminal COMMITTED -> ABORTED
- 004 STILL FAILING — durable external effect duplicates across restart
- 005 PARTIAL — transient replay improved, permanent/gap disposition missing
- 006 PARTIAL — decision split improved, ACK/cursor does not solve external effect window
- 007 STILL FAILING — startup may READY with unresolved/unwired pending publication
- 008 STILL FAILING — logical schema/constraints/migration validation incomplete
- 009 CLOSED — WAL/FULL configuration contract
- 010 CLOSED — same-ID process concurrency
- 011 STILL FAILING — aggregate storage constraint can still be misreported as stale
- 012 CLOSED — receipt canonicalization

### New official defects
- QA-PIPELINE-013 HIGH OPEN — unbounded writer admission and unsafe shutdown
- QA-PIPELINE-014 HIGH OPEN — stream cursor gap skipping
- QA-PIPELINE-015 CRITICAL OPEN — destructive/partially committed legacy migration
- QA-PIPELINE-016 HIGH OPEN — StoreIncarnation TOCTOU
- QA-PIPELINE-017 HIGH OPEN — mutable admitted request
- QA-PIPELINE-018 MEDIUM OPEN — Release test/fault control packaging

### REV2 scope effect
QA-PIPELINE-004/005/006/014 are not silently closed by removing the generic dispatcher.
If the unsafe generic consumer path is fully removed from Production P1, those defects become:
`NOT APPLICABLE TO P1 / DEFERRED CONSUMER GATE`
only after Sol verifies the code path is absent and P1 makes no delivery claim.

### Engine Host proof obligations
No existing QA-ENGINE defect is closed by A E1.

For independent E-A QA, specifically re-test QA-ENGINE-002/006 class:
engine READY is insufficient; census/reference oracle must catch silent accepted loss/corruption.


## QDL-046 — Genesis Future Proof Obligations

No current Production defect status changes.

Before Genesis Production, E1/E2 must verify:
- same GenesisOperationId retry creates exactly one Settlement and one terminal receipt;
- crash before generation, during generation, after artifact generation, after identity binding, and before canonical admission;
- target Settlement uniqueness under concurrent genesis attempts;
- ContentProfile mismatch fail-closed;
- stable EntityId/custody binding before canonical admission;
- duplicate native loadID / duplicate stable EntityId attacks;
- first PlayerGlobalRevision + MapSegment composition and independent revision identities;
- server restart with staged but noncanonical genesis work;
- additional-settlement caravan custody transfer + newly generated map environment;
- tampered client artifact rejection/quarantine if client-assisted genesis is ever enabled;
- economically significant environmental/map differences are covered by the chosen generation/admission contract;
- no Tier/wealth/political state is granted directly from an untrusted genesis artifact.

Same-seed determinism is a conditional test for Model C, not a universal QA gate.


## QDL-047 — Pipeline REV2 E1 Claims / E2 Gate

Existing QA-PIPELINE statuses remain unchanged pending E2.

### REV2 claimed fixes requiring independent closure
- 001 fingerprint ambiguity -> V2 tagged/length-prefixed encoding
- 003 terminal-state mutation -> insert-only journal + DB triggers
- 007 startup readiness -> P1-only readiness semantics
- 008 logical schema -> v3 structural validator
- 011 storage-error typing -> strict classification
- 013 ingress/shutdown -> bounded Channel + dedicated thread + drain
- 015 destructive migration -> v1/v2 durable-record fail-closed
- 016 incarnation TOCTOU -> in-transaction validation/rotation discipline
- 017 mutable request -> immutable admission
- 018 Release test controls -> separate TestHarness

### P1 scope-removal candidates
If Sol verifies consumer/cursor/ACK/delivery execution is absent from Production P1:
- 004, 005, 006, 014 may be reclassified from current Pipeline P1 defects to
  `DEFERRED CONCRETE-CONSUMER GATE / NOT APPLICABLE TO P1`.
This does not close their underlying external-delivery problem for future consumers.

### New E2 watch items
Not official defects unless reproduced:

- **QA-PIPELINE-WATCH-019:** non-empty `application_id=0,user_version=0` foreign DB may be adopted as fresh.
- **QA-PIPELINE-WATCH-020:** schema validator may not fully validate UNIQUE/CHECK/index/trigger semantics.
- **QA-PIPELINE-WATCH-021:** shutdown join timeout may still permit unresolved callers or worker-after-dispose.
- **QA-PIPELINE-WATCH-022:** same-stream sequence allocation under independent processes may expose race/busy ambiguity.
- **QA-EVIDENCE-WATCH-001:** REV2 report omits exact frozen source/binary SHA/MVID provenance.

## QDL-048 — Engine Host Round-Trip E2

### QA-ENGINE-002
Status: **STILL FAILING — CRITICAL**
Comparator failure does not block export; READY/SAVED can still carry semantic loss.

### QA-ENGINE-006
Status: **STILL FAILING — HIGH**
Current oracle misses multiple READY-preserving semantic changes including skills, hediff severity, bill state, zone location, fire size and condition duration.

### Evidence lineage watch
Before next E2, exact fixture/source/DLL/MVID/profile/export hashes must be frozen and reported.

### Positive evidence retained
- fresh-process A -> B -> C works;
- narrow custody/reference subset survives;
- active Goto/reservation reload has positive evidence;
- selected environment conservation works;
- global temporal contamination is independently confirmed.


## QDL-049 — Pipeline REV2 E2 Official Update

### CLOSED / retained narrow closure
- QA-PIPELINE-002 — CLOSED, P1 fast-path PREPARED absence only.
- QA-PIPELINE-009 — CLOSED, WAL/FULL configuration contract.
- QA-PIPELINE-010 — CLOSED, same-ID process concurrency.
- QA-PIPELINE-012 — CLOSED, receipt representation/hash scope.
- QA-PIPELINE-015 — CLOSED, legacy v1/v2 fail-closed preservation.
- QA-PIPELINE-017 — CLOSED, admitted request immutability.
- QA-PIPELINE-018 — CLOSED, executable destructive Release test-control scope.

### DEFERRED from P1
- QA-PIPELINE-004
- QA-PIPELINE-005
- QA-PIPELINE-006
- QA-PIPELINE-014

Status:
**NOT APPLICABLE TO P1 / DEFERRED CONCRETE-CONSUMER GATE**

They are not globally solved. Reopen against the first real consumer.

### OPEN
- QA-PIPELINE-001 HIGH — lossy Unicode/JSON numeric canonicalization can false-retry.
- QA-PIPELINE-003 HIGH — SQLite REPLACE bypasses terminal immutability.
- QA-PIPELINE-007 HIGH PARTIAL — startup consistency incomplete and production writer lifetime not actually bound to READY.
- QA-PIPELINE-008 HIGH — strict schema semantics false-READY.
- QA-PIPELINE-011 MEDIUM — aggregate storage constraint misclassified as stale revision.
- QA-PIPELINE-013 HIGH — channel-close waiters/orphaned callers and writer-after-Dispose.
- QA-PIPELINE-016 HIGH PARTIAL — explicit old incarnation fenced, but missing/blank incarnation auto-binds current.
- QA-PIPELINE-019 HIGH NEW — `(PrincipalId,OperationId)` journal key conflicts with global receipt/event IDs derived without principal.

### Retired watches
- WATCH-019 foreign zero identity — not reproduced.
- WATCH-020 strict schema — absorbed into QA-PIPELINE-008.
- WATCH-021 shutdown — absorbed into QA-PIPELINE-013.
- WATCH-022 same-stream concurrency — not reproduced in tested 48-process contention.
- QA-EVIDENCE-WATCH-001 — resolved by Sol exact provenance.

QA-ENGINE-002/006 remain OPEN while A works on Semantic Gate 02.


## QDL-050 — Engine Semantic Gate 02 Developer Claim

QA-ENGINE-002:
**OPEN / FIX CLAIMED / E2 PENDING**

Claimed improvements:
- READY no longer sufficient;
- comparator mismatch blocks export;
- semantic state/generation/map/tick checks;
- staged save + quarantine.

QA-ENGINE-006:
**OPEN / FIX CLAIMED / E2 PENDING**

Claimed improvements:
- 15 supported semantic dimensions;
- clean positive fixture;
- 15/15 developer negative battery blocked.

### E2 attack obligations

- self-generated manifest must not create a self-approval bypass;
- approval manifest provenance/authority must be explicit;
- non-tick semantic mutation after approval must invalidate/reject export;
- manifest/context/profile replacement after approval must invalidate/reject;
- save-time silent semantic loss must be caught before final artifact approval;
- negative battery must be independently reproduced;
- fresh-process positive round-trip must use trusted manifest lineage;
- candidate profile/DLL/source/artifact hashes must match A's report.

No Engine defect closes from E1 self-report.


## QDL-051 — G-Q8 Offline Material Future Proof Obligations

No current runtime defect closes.

Before offline Auto-Shop material execution:
- offline material-scope reservation/fence must exclude competing writers/operations;
- online owner case must exercise DELTA_BARRIER rather than the offline shortcut;
- stale projection shortfall must abort before canonical commit;
- staged result must be durable, immutable, and bound to base/profile/hash before commit;
- commit advances committed state once;
- promotion advances artifact watermark without a second committed revision;
- crash pre-commit leaves canonical state unchanged;
- crash post-commit/pre-promotion converges from the bound staged result;
- corrupted post-commit staged result enters forward repair without erasing the canonical decision;
- stack split/merge conserves total quantity and supported attributes;
- nested-holder and reservation/reference semantics must be proven for any supported class;
- future engine-free codec must pass fresh Engine Host semantic reload;
- projection eligibility flags must not silently encode unresolved product policy.

TBD-05 and exact TaxSeizable policy remain open.


## QDL-052 — Engine Semantic Gate 02 E2 + Pipeline REV3 Candidate

### QA-ENGINE-002
Status: **STILL FAILING — CRITICAL**

Confirmed:
- 6/6 self-baselining corrupt states reached ARTIFACT_APPROVED;
- same-tick non-tick semantic mutation can retain stale approval;
- silently changed staged bytes can be promoted;
- truncated XML can be promoted;
- promotion-time generation/live changes are not re-fenced.

### QA-ENGINE-006
Status: **STILL FAILING — HIGH**

Confirmed:
- 15 major negative classes are now independently detected when a trusted witness is used;
- supported predicate remains incomplete;
- some collected fields are not compared;
- fixture/static oracle discrepancies remain;
- saved-byte semantic proof is absent.

### Pipeline REV3
Status:
**E1 FIX CLAIMED / E2 PENDING**

Re-test open Pipeline defects:
- 001
- 003
- 007
- 008
- 011
- 013
- 016
- 019

Regression-lock closed/deferred statuses from QDL-049 remain unchanged until E2 confirms no regression.

### New watch — not official until reproduced
- QA-PIPELINE-WATCH-020: derivative ID raw string formatting may be ambiguous when PrincipalId/OperationId contain separators.
- QA-PIPELINE-WATCH-021: Decimal canonicalization may underflow/round accepted values below supported precision.
- QA-PIPELINE-WATCH-022: duplicate JSON object keys may collapse before fingerprinting instead of rejecting ambiguous input.


## QDL-053 — ADR-001 Foundation Future E1/E2 Obligations

No runtime defect is opened or closed by C's E0 brief.

Before ADR-001 Production Foundation can be marked runtime-complete, verify at minimum:

### Identity/auth
- client-supplied PrincipalId/ActorId cannot override server-derived identity;
- invalid/expired credential cannot create authenticated session;
- two sessions for the same PlayerId have distinct SessionEpochs when separate logical sessions are allowed;
- transport reconnect to an existing valid logical session preserves SessionEpoch;
- new session does not silently change PrincipalId.

### Operation identity
- exact retry after reconnect resolves by durable `(PrincipalId,OperationId)`;
- SessionEpoch change does not create a second canonical operation solely because the session changed;
- stale session frame cannot gain authority by replaying a prior operation envelope.

### Store incarnation
- ordinary server restart preserves StoreIncarnationId;
- restore/rollback invalidates old incarnation;
- old-incarnation mutation fails closed;
- StoreIncarnationId is treated as opaque identity, not trusted client chronology.

### Startup/readiness
- no canonical mutation before Pipeline + world/incarnation + auth/session Foundation readiness;
- Foundation can become ready without Engine Host/materialization and without future Faction/Settlement registries;
- feature route depending on an unavailable later registry remains disabled;
- malformed/legacy schema fails closed according to Pipeline policy.

### Handshake/profile
- protocol mismatch fail-closed;
- profile mismatch fail-closed as compatibility admission;
- client fingerprint assertion is not recorded as anti-cheat proof;
- malformed/unknown frame bounded and rejected;
- ordinary route cannot invoke privileged control capability.

### Restart/session
- metadata-only Foundation restart behavior is explicit;
- future WriterLease/G-Q6 restart semantics are not silently inferred from Foundation session implementation.

These obligations become executable only after Pipeline E2 authorizes Foundation implementation.


## QDL-054 — Pipeline REV3 E2 Official Update

### Newly CLOSED
- QA-PIPELINE-003 — CLOSED within tested DB terminal-row boundary.
- QA-PIPELINE-011 — CLOSED within typed storage-error scope.
- QA-PIPELINE-016 — CLOSED for mandatory explicit incarnation and cross-process rotation fence.

### OPEN
- QA-PIPELINE-001 HIGH — exact JSON input identity still lossy/ambiguous.
  Reproduced:
  - `1e-29` vs `-1e-29` -> both `0.0`;
  - `1e-40` vs `0.0` -> same canonical value;
  - 29+ precision values collapse;
  - invalid surrogate in JSON property names accepted;
  - duplicate JSON keys silently collapse;
  - trailing second root/content ignored.

- QA-PIPELINE-007 HIGH PARTIAL — startup consistency + service ownership incomplete.
  Reproduced:
  - 9 logical consistency mutations reach READY;
  - normal Main returns while coordinator writer remains alive/readiness true.

- QA-PIPELINE-008 HIGH PARTIAL — semantic schema identity incomplete.
  Reproduced:
  - CHECK literal case change preserves candidate signature but changes SQLite semantics;
  - partial index predicate omitted from signature.

- QA-PIPELINE-013 HIGH PARTIAL — ingress fixed, worker lifetime not.
  Reproduced:
  - Dispose returns while worker remains alive;
  - later repository activity/commit occurs after Dispose;
  - normal server quit leaves service coordinator alive.

- QA-PIPELINE-019 HIGH — delimiter-based derivative IDs are non-injective.
  Reproduced with underscore, Unicode and long identity pairs.

### Retained
- 002/009/010/012/015/017/018 regression closure.
- 004/005/006/014 deferred concrete-consumer gate.

### REV4 E2 obligations
Must preserve all independent process/kill/durability regressions while closing the five open defect groups above.


## QDL-055 — TradeConfiguration Future E1/E2 Obligations

No runtime defect opens/closes from the E0 brief.

Before TradeConfiguration runtime gate:

### Authorization / ownership
- client-supplied PlayerId/FactionId cannot override server-derived PrincipalId;
- wrong owner/controller rejected;
- stale SettlementOwnershipEpoch rejected;
- ownership transfer racing config update yields one canonical ordering;
- old-epoch update cannot succeed after transfer commit.

### Config CAS / idempotency
- stale TradeConfigurationRevision rejected;
- exact `(PrincipalId,OperationId)` retry returns stored receipt without second revision advance;
- same operation identity with changed config payload collision-rejected;
- reconnect/new SessionEpoch does not change PrincipalId operation identity.

### Store incarnation
- old-incarnation config command rejected even if numeric revisions match restored DB state.

### Content/profile
- invalid ItemDef/reference rejected against server canonical profile registry;
- profile change that removes a referenced def fails closed or marks incompatible according to explicit migration policy;
- no silent destructive config deletion.

### Material isolation
- config create/update/read performs zero `.rws` access;
- zero stock/Silver reservation;
- zero Engine Host/DELTA_BARRIER/material mutation.

### Publication
- canonical config commit + PublicationEvent append are atomic;
- absence of a UI consumer does not make the config transaction unready;
- no claim of exactly-once UI delivery.

### Ownership-transfer product policy
Whatever policy is later selected (clear/disable/rebind/transfer), E2 must prove old-epoch mutation/execution authorization cannot survive the epoch change.


## QDL-056 — Engine Semantic Authority Gate 03 Developer Result

### QA-ENGINE-002
Status:
**OPEN / MATERIAL FIX CLAIMED / E2 PENDING**

Developer-positive claims:
- self-census cannot nominate input authority;
- wrong source SHA/generation/map rejected;
- same-tick live mutations block stage/promotion;
- full XML parse;
- staged SHA recheck;
- promotion uses replacement/backup path.

Still required:
- pre-promotion fresh semantic validation of exact staged SHA;
- ContentProfile/context/base authority binding;
- control-plane simulation-grant authority;
- promotion-boundary race/replacement recovery.

### QA-ENGINE-006
Status:
**OPEN / MATERIAL FIX CLAIMED / E2 PENDING**

Developer-positive claims:
- prior missed followFieldwork/plant age/bill suspended now change canonical live hash;
- 15 corrupt inputs rejected under clean authority;
- A/B/C post-promotion manifest parity.

Still required:
- prove closed SupportedSemanticManifest schema;
- prove all declared supported fields participate in canonical hash/equality;
- independently verify job/reservation and reference fields if retained in supported scope;
- prove staged saved bytes reproduce the sealed manifest before promotion.

### New E2 watch items
Not official defects until independently reproduced:

- **QA-ENGINE-WATCH-007:** staged serializer can silently change supported semantic state before staged SHA capture and still be promoted.
- **QA-ENGINE-WATCH-008:** AuthorityBundle may omit ContentProfile/base/context binding required by the authority contract.
- **QA-ENGINE-WATCH-009:** `SEAL_RESULT <grantId>` may accept an unregistered/arbitrary grant identifier.
- **QA-ENGINE-WATCH-010:** replacement/promotion failure may damage the prior approved final or leave ambiguous canonical file state.


## QDL-057 — E-B Future Runtime Proof Obligations

No runtime defect opens/closes from the E0 brief.

Before E-B can pass:

### Barrier cut
- BarrierId unique/replay-safe;
- ACK binds lease/fencing generation, island scope set, base revisions and command watermark;
- no command can be both outside the ACK cut and materialized inside the frozen candidate;
- no post-cut mutation/checkpoint is accepted into the old base.

### Island scope
- all Settlements sharing the leased LocalClock domain stop local progression during barrier;
- target Settlement alone receives the typed material change;
- sibling Settlement material remains unchanged;
- no catch-up ticks on resume.

### Same-holder success
- FencingGeneration unchanged;
- WriterLease holder unchanged;
- committed revision advances once;
- artifact/result identity advances coherently;
- resume occurs from exact committed result.

### Abort/recovery
- pre-commit shortfall/failure leaves canonical state unchanged;
- connected same holder may resume only after exact rollback/rebase proof;
- lost transport enters SUSPENDED_GRACE, not automatic replacement;
- replacement writer only after revoke/fence;
- post-commit disconnect resumes only after committed-result proof/rebase.

### Delta semantics
- operation is server-authored and base-bound;
- application is total or fail-closed;
- no partial material mutation survives failed validation;
- duplicate Barrier message is coordination-idempotent;
- duplicate canonical OperationId uses durable Pipeline idempotency.

### G-Q1 observation
- record global TicksGame/TicksAbs/global component behavior separately;
- do not reinterpret global-clock contamination as successful per-Settlement LocalClock isolation.

## QDL-058 — Engine Gate03 E2 + Pipeline REV4 E1

QA-ENGINE-002: **STILL FAILING — CRITICAL**
- wrong supported serialized bytes promoted;
- stage-less promotion bypass;
- arbitrary grant labels;
- mutable authority/incomplete profile-mode binding;
- stale readiness after failed validation;
- missing ResultEpoch/stage receipt binding.

QA-ENGINE-006: **STILL FAILING — HIGH**
- full collected hash materially improved and 102 representative leaf paths were independently exercised;
- no fresh saved-byte semantic validator;
- active job target/identity remains outside the current declared canonical manifest beyond JobDef;
- partial helper comparator must not become the equality gate.

Pipeline REV4:
**E1 FIX CLAIMED / E2 PENDING**
Official OPEN groups remain:
001, 007, 008, 013, 019.
Retain prior closures unless E2 finds regression.
004/005/006/014 remain deferred concrete-consumer gate.

## QDL-059 — G-Q1 Decisive Runtime Proof Obligations

No existing runtime defect closes from the E0 brief.

Before G-Q1 topology can close:
- two maps in one shared island;
- controlled target-map advancement while sibling remains locally frozen;
- start/end supported semantic manifests for both;
- fresh reload before final comparison;
- instrument pawn needs, biological/chronological age, jobs, hediff timers, plants, conditions/fire, power/fuel, weather/sky, GameComponents, research, ideology/ritual, quest/storyteller/incident timers, WorldPawns/world objects and representative admitted-profile mod tick managers where feasible;
- use multiple horizons, including ~60,000 ticks where practical;
- prove no forbidden catch-up on resume;
- use semantic manifest/census + explicit allowed differences, not raw bytes.

If Model A leaks supported material state:
identify exact call sites/state transitions, test bounded minimal interception, and repeat the semantic oracle.
Only if the required semantics remain unsafe/unbounded/unpatchable for the supported profile does evidence favor Model C.

Separate-process results are an isolation control, not automatic proof of one process per Settlement.

## QDL-060 — Pipeline REV4 E2 Official Update

### CLOSED
- QA-PIPELINE-008 — CLOSED for independently tested Schema V5 contract.
- QA-PIPELINE-019 — CLOSED for admitted principal/operation/revision derivative identity scope.

### PARTIAL / OPEN
- QA-PIPELINE-001 — PARTIAL / OPEN.
  Remaining defect is typed rejection classification:
  escaped malformed surrogate inputs and minimum exponent overflow are rejected with no durable row, but incorrectly surface as STORAGE_FAILURE rather than INVALID_REQUEST.

### STILL FAILING / OPEN
- QA-PIPELINE-007 — HIGH.
  Reproduced:
  - legitimate STALE/ABORTED history rejects startup;
  - history lookup loses PrincipalId/full operation parent identity;
  - six semantic graph mutations false-READY, including swapped ReceiptId/EventId, wrong audit details, OperationType, ContentProfileFingerprint, RequestFingerprint.

- QA-PIPELINE-013 — HIGH.
  Reproduced:
  - Shutdown/Dispose returns with writer alive;
  - Main returns with writer alive;
  - after-CAS repository activity occurs after Dispose returned.

### Packaging/provenance watch
REV4 official Release manifest was not updated; only old REV3 manifest exists.
This is not a new P1 semantic defect by itself, but the next frozen candidate must supply an exact current Release manifest before E2.

### REV5 closure battery must include
- natural mixed COMMITTED+ABORTED restart positive;
- 25-process CAS DB restart positive;
- cross-principal same OperationId in same and different scopes;
- envelope fingerprint recomputation;
- ReceiptId/EventId canonical derivation checks;
- typed audit detail verification;
- all six REV4 false-READY mutations;
- active writer shutdown beyond prior ~6s return window;
- actual Program.Main with active operation;
- escaped surrogate and int-min exponent typed INVALID_REQUEST;
- complete regression of closed 008/019 and prior durability/concurrency locks.

## QDL-061 — Engine Gate04 E1 Submission

### QA-ENGINE-002
Status:
**OPEN / MATERIAL FIX CLAIMED / E2 PENDING**

Developer evidence now claims:
- pre-promotion fresh validator;
- mandatory StageValidationReceipt;
- stage-less promotion blocked;
- immutable AuthorityBundle;
- registered SimulationGrant;
- ResultEpoch/reseal invalidation;
- replacement safety.

Independent closure still requires:
- receipt issuer authenticity/provenance;
- validator expected-manifest substitution attack;
- cross-worker/result/stage receipt replay attacks;
- profile/context/grant binding;
- readiness revocation across all failure paths.

### QA-ENGINE-006
Status:
**OPEN / MATERIAL FIX CLAIMED / E2 PENDING**

Developer evidence:
- full canonical manifest hash remains the gate;
- saved-byte semantic corruptions fail fresh validation;
- current job semantic scope explicitly limited to JobDef.

Independent closure still requires:
- fresh validator really computes actual staged manifest;
- expected result comes from simulator's sealed result;
- receipt is bound to exact staged SHA/result/profile/context;
- no claim beyond explicitly supported manifest fields.

### E2 watch
- receipt JSON/PID forgery;
- validator supplied forged sealedResB64;
- receipt replay after reset/reseal;
- same ModsConfig with authority-relevant profile-content drift;
- scope/map-index substitution;
- validator process/profile mismatch.

## QDL-062 — PlayerGlobal / SharedWorld Temporal Boundary Obligations

No runtime defect closes from this brief.

Before global ownership/schema claims can close:
- identify stable owner, actual mutator(s), revision/time source and fresh-load dependency for each subsystem;
- prove whether the subsystem can change supported material state while a MapSegment is frozen;
- prove reconstructible claims via discard/rebuild + fresh-load semantic comparison + subsequent supported gameplay;
- prove read-only projection claims cannot canonically mutate and use explicit revision binding where material semantics depend on the projection;
- test frozen MapSegment + newer compatible PlayerGlobal, incompatible newer global revision, stale dependency, and rebase/rematerialization;
- for cross-owner operations prove stable entity/custody identity, staged material result where material changes, canonical commit ordering, revision bindings and crash recovery.

Prioritize G-Q1 evidence for:
hediff/age, Research/Ideology if Engine-global, WorldPawns/reference lifecycle, GameComponents, Quest/Storyteller/Incident state, and representative mod global managers.

## QDL-063 — Pipeline REV5 E1 Submission

QA-PIPELINE-001:
**OPEN / FIX CLAIMED / E2 PENDING**
Developer claims all five REV4 typed-input failures now return INVALID_REQUEST with zero durable rows.

QA-PIPELINE-007:
**OPEN / MATERIAL FIX CLAIMED / E2 PENDING**
Developer claims legitimate mixed COMMITTED/ABORTED restart, 25-process loser restart, cross-principal same OperationId under Schema V6, six false-READY rejection, and semantic envelope/receipt/event/audit checks.
Independent watch: forged plausible ObservedRevisionAtDecision must not pass a range-only predicate.

QA-PIPELINE-013:
**OPEN / FIX CLAIMED / E2 PENDING**
Developer claims final Dispose/Shutdown/Main waits for writer exit while caller UNKNOWN remains bounded.

QA-PIPELINE-008:
Historical V5 status CLOSED. V6 requires independent schema-regression verification.

QA-PIPELINE-019:
CLOSED / regression required.

REV5 E2 mandatory attacks:
- five typed-invalid input cases;
- natural mixed COMMITTED/ABORTED restart;
- 25-process CAS loser restart;
- cross-principal same OperationId;
- plausible historical observed-revision tamper;
- rejection reason/status tamper;
- every fingerprint-bound envelope field;
- ReceiptId/EventId swap/re-sign;
- typed audit mutation;
- independent V6 descriptor/signature/canary/legacy checks;
- active writer held beyond old/E1 shutdown windows;
- actual Program.Main with active operation;
- full concurrency/hard-kill/terminal/incarnation/WAL regressions;
- exact current REV5 package manifest verification.

## QDL-064 — Engine Gate04 Independent E2

### QA-ENGINE-002
Status:
**STILL FAILING — CRITICAL**

Reproduced:
- caller-crafted receipt with fake/empty validatorProcessId accepted;
- caller-substituted expected manifest B obtains a real validator receipt and promotes supported-corrupt B under sealed A;
- receipt scope/map/version/hash/source fields incompletely checked;
- stale capability survives several control-plane validation errors;
- grant scope can diverge from authority scope;
- storeIncarnation/baseLineage omitted from AuthorityBundle equality;
- current epoch internal invariant incomplete;
- ModsConfig-only profile does not bind admitted content bytes.

### QA-ENGINE-006
Status:
**STILL FAILING — HIGH**

Reproduced:
- supported followFieldwork corruption False promoted under sealed A(True) through expected-B substitution;
- supported bill suspended corruption True promoted under sealed A(False) through expected-B substitution.

Positive:
- legitimate A expected manifest rejects B;
- full V4 hash reacts to independently exercised declared fields;
- same-tick supported mutations are detected;
- job target/loadID/reservation persistence works for tested slice.

### Gate05 required closure set
- operator-owned validator task/capability;
- no caller-nominated expected manifest;
- no generic caller-authored promotion receipt;
- complete closed-schema result/receipt/context equality;
- consistent control-plane failure revocation;
- authority/grant scope + lineage equality;
- current epoch binding;
- ADR-006B actual-loaded-content fingerprint;
- corrected V4 authority artifact/documentation;
- fail-closed canonical replacement fallback;
- diagnostic NullReference cleanup.

No QA-ENGINE closure before new independent E2.
