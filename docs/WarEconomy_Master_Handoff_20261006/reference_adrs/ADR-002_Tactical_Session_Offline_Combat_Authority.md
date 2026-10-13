# ADR-002 — Tactical Session and Offline Combat Authority

- Status: **PROVISIONALLY ACCEPTED**
- Decision Owner: Master (GPT-5.6 Sol)
- Project: WarEconomy / RimMulti
- Canonical Requirement Source: `요구사항_명세서.md`
- Provenance: Reconstructed formal ADR from provisional Master decisions, ENGINE-01/02 evidence, and independent QA. This file did not previously exist as a standalone artifact.

## 1. Context
The product requires real shared Tactical Sessions for visits and attacks, including lawful attacks against offline settlement owners. Engine difficulty must not be solved by disabling offline combat, actual map damage, shared tactical interaction, defender AI, or persistent outcomes.

## 2. Candidate
Primary candidate: **Candidate C — Trusted Tactical Worker Always**.
A controlled RimWorld process performs actual Tactical simulation for the active Tactical Session. Candidate C remains preferred but not yet Production-approved.

## 3. Authority Split
### Dedicated Server — Domain Authority
Determines legal entry, admission, participant identity, hostile/peaceful phase, ownership/political result, final canonical commit, and operation/lease state.

### Tactical Worker — Simulation Authority
May calculate Pawn AI/jobs/combat/projectiles/damage/health/map mutation/environmental effects within authorized Tactical scope.

### Client
May issue only authorized control intent for permitted Pawns. Client is never trusted to submit final battle/domain outcomes.

## 4. Session Model
- Same tile does not automatically share a map.
- Explicit visit or lawful attack creates a Tactical Session.
- Multiple factions may participate.
- Each player directly controls only their own Pawns.
- Offline defender may be AI-controlled.
- Mid-battle AI↔player control handoff is supported as an architecture target.

## 5. Time / Speed
Temporal authority is defined by ADR-006A.
- peaceful Tactical: server-accepted Last Input Wins speed changes
- hostile Tactical: forced 1x
- hostile user pause disabled
- control handoff does not reset/duplicate timeline

## 6. Offline Attack
Lawful offline attack remains mandatory. The architecture may not require defender presence as a shortcut.

## 7. Worker Model
- actual RimWorld 1.6 process
- operator-controlled WorkerBridge
- supervisor/orchestrator
- initially one Worker process per active Tactical execution island
- explicit lifecycle and generation/lease fencing
- cooperative tick execution; unsafe monolithic long main-thread loops are unacceptable

## 8. Save / Result Authority
A Worker save is not automatically authoritative.
After ADR-006A:
- full `.rws` may be private checkpoint/materialization/extraction input
- full Worker `.rws` must not replace canonical whole-world state by default
- preferred direction: target-scoped outcome publication / canonical merge
- inventory canonicalization -> ADR-003
- durable multi-state commit/repair -> ADR-004

## 9. Crash / Lease Safety
- one Tactical lineage/LocalClock has one active authoritative writer
- stale Worker generations are fenced
- timeout alone does not prove old Worker inactivity
- recovery cannot allow two Workers to publish the same lineage
- Worker crash must not silently revert already committed death/loot/damage

## 10. Evidence So Far
Bounded evidence supports actual RimWorld load, controlled ticking, target Pawn/Animal/health/power/held-item/fire progression subsets, native save/reload, multi-process isolation sanity, and cooperative ~60 TPS in tested warm conditions.

Independent QA also exposed dependency-loss false success, unsafe long tick path, global/foreign dispatch escape, temporal leakage through engine `TicksGame`, load-before-fence effects, and fixture/oracle weaknesses.

These do not prove Candidate C impossible, but prevent full acceptance.

## 11. Dependencies
ADR-002 depends on ADR-001, ADR-006A, future ADR-003, and future ADR-004.

## 12. Gate Status
**PROVISIONALLY ACCEPTED**.

Not authorized yet:
- Production Tactical
- Remote Tactical Production
- defect closure based only on developer self-tests

ADR-002 may become ACCEPTED only after required implementation and independent evidence demonstrate the accepted temporal/publication/inventory/commit boundaries for the supported profile.
