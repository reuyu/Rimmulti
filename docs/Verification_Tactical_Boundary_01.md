# Verification_Tactical_Boundary_01

## Track 1 — Fixture Trust & Track 2 — Oracle Trust

### CLAIM
The complex test state preserves all required semantic dimensions (apparel, inventory, building health, assignment/master, nested holder, quantity, identity, crop, bill, storedPower) across a tactical session boundary, and the oracle robustly fails if any dimension is corrupted.

### SETUP
1. Evaluated developer's `POC_TAC_ENGINE_02_MultiMap_Complex.rws`.
2. Found it lacked `nonempty bill` and `real_storedPower`.
3. Injected `<li Class="Bill_Production">` into `TableSculpting` and `<storedPower>314.15</storedPower>` into `Battery` via script.
4. Loaded via `LOAD_SAVE`, ran ticks, and exported to `BoundaryExport.rws`.
5. Executed fail-by-mutation tests by selectively stripping `wornApparel`, `innerContainer`, `health`, `stackCount`, and `id`.

### ORACLE
1. Exported save must contain identical or logically-progressed semantic data for all 10 tracked dimensions.
2. If any dimension is manually corrupted (e.g. `wornApparel` cleared), the oracle must fail.

### OBSERVED
- `storedPower` correctly progressed from `314.15` to `314.171631`, proving active simulation rather than just string retention.
- `wornApparel`, `inventory`, `nested_holder`, `quantity`, `identity`, `real_crop`, `nonempty_bill`, `building_health` were successfully preserved.
- **FAILURE DETECTED:** The `assignment_master` field, which contained `Thing_Human302` in the base fixture, was silently wiped to `null` on all animals in the exported save.
- All fail-by-mutation tests passed (the oracle successfully failed when dimensions were intentionally corrupted).

### EVIDENCE
```json
[track1_fixture_trust] 
Original save master count: 1 (Thing_Human302)
Exported save master count: 0 (all null)

[mutated_apparel_oracle] True
[mutated_inventory_oracle] True
[mutated_building_oracle] True
[mutated_nested_oracle] True
[mutated_quantity_oracle] True
[mutated_identity_oracle] True
```

### SCOPE
Proves that the engine is capable of retaining deep nested structures (apparel/inventory/bills) and actively simulating power. Proves the oracle does not blindly return PASS. Proves a specific bug exists in `master` animal assignments during scoped simulation.

### DOES NOT PROVE
Does not prove that ALL reference-based fields are lost, only that `master` animal assignments are vulnerable during load/export. Does not prove whether the master was on a different map.

---

## Track 3 — Dependency Negatives

### CLAIM
Partial semantic loss caused by missing dependencies (mods or defs) must never reach canonical-success READY/EXPORT.

### SETUP
1. Mutated the valid `BoundaryFixture.rws` to include an undeclared mod `qa.missing.mod` in `modIds`.
2. Renamed the `TableSculpting` def to `QA_MissingThingDef`.
3. Issued `LOAD_SAVE Input` to the engine without pre-calling `VALIDATE_MANIFEST`.

### ORACLE
Engine should either reject the load or halt in a `FAILED` state rather than reaching `READY`.

### OBSERVED
The engine parsed the file, dropped the unrecognized entities (partial semantic loss), and successfully reached the `READY` state. The boundary invariant is violated if the caller relies solely on `LOAD_SAVE`.

### EVIDENCE
```json
[track3_dependency_negatives] {
  "response": "QUEUED: Gen=1, LoadGame queued for 'Input'. TargetMapIndex=0. Poll STATUS to monitor.",
  "states": [
    "STATE: LOADING, Gen=1...",
    "STATE: READY, Gen=1, Maps=2, TicksGame=1824, SimActive=True, TargetMap=0, TicksSim=0, IsRealtime=False, RemainingStep=0"
  ],
  "reached_ready": true
}
```

### SCOPE
Proves that RimWorld's native load behavior silently accepts data loss. Proves the architecture is entirely reliant on the external caller rigidly enforcing `VALIDATE_MANIFEST` before `LOAD_SAVE`. 

### DOES NOT PROVE
Does not prove that `VALIDATE_MANIFEST` itself is broken, only that the boundary gateway `LOAD_SAVE` lacks internal strict enforcement.

---

## Track 4 — Execution Bounds

### CLAIM
The engine handles large requests, queue flooding, and maintains acceptable control-service latency.

### SETUP
1. Requested `RUN_TICKS 10000`.
2. Issued 50 rapid `STATUS` requests sequentially to flood the command queue.

### ORACLE
Engine must not crash or deadlock. Control latency should remain bounded.

### OBSERVED
The engine completed 10,000 ticks in ~4.9 seconds. The queue flood of 50 requests resolved in 834.6 ms (averaging ~16.7 ms per request), demonstrating stable responsiveness even while idle/paused.

### EVIDENCE
```json
[track4_large_run] 4945.7 ms
[track4_queue_flood_ms] 834.6 ms
```

### SCOPE
Proves the synchronous socket bridge can handle standard bulk requests and high-frequency polling without dropping connections.

### DOES NOT PROVE
Does not prove performance under heavy 60 TPS simulation load, only baseline idle/paused control latency.

---

## Track 5 — Load Boundary

### CLAIM
The load sequence predictably transitions non-target map/world states to READY.

### SETUP
Measured state transitions from before `LOAD_SAVE` to canonical `READY`.

### ORACLE
Extract precise timestamps for when the engine reaches `READY`. 

### OBSERVED
- `LOADING` state held for ~13.5 seconds.
- Transitioned directly to `READY, SimActive=True, TargetMap=0`.
- (Note: `Playing` and `Fence` substrings are not utilized in this bridge version's STATUS string).

### EVIDENCE
```json
[track5_load_boundary] {
  "before_load": 0,
  "ready": 13549.3
}
```

### SCOPE
Proves the boundary status polling mechanism correctly catches the transition to readiness.

### DOES NOT PROVE
Does not solve temporal policy (ADR-006A) or prove whether the non-target maps advanced during the 13.5 seconds of load time.
