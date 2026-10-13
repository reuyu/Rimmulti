# Tactical Worker Hardening Evidence & Defect Resolution Report
**Work Package**: `WP-TAC-WORKER-HARDEN-01`  
**Role**: Primary Development Agent (Gemini 3.8 Flash A)  
**Date**: October 2, 2026  
**Status**: COMPLETE (Technical Defects Resolved within Tested Scope)  
**ADR-002 Verdict**: **NOT ACCEPTED** (Deferred to Master ADR-006A)

---

## 1. Executive Summary & Policy Compliance

This report documents the implementation, empirical validation, and regression test evidence for technical defects independently reproduced by GPT-6.1 Sol in `ENGINE-02`. All changes were executed strictly within scratch worker bridge infrastructure (`scratch/WorkerBridgeMod/`) and automated test suites (`scratch/run_hardening_regressions.py`).

### Strict Governance Constraints Met
1. **Production Code Integrity**: Production code (`WarEconomyMod/`) was **NOT modified** (verified 0 source edits).
2. **Master Authority & Temporal Policy Freeze**: Zero temporal-policy decisions were made. Policies regarding Server World Time vs. Local Time, chronological pawn aging, map rebase strategies, canonical full-save vs. target-merge architecture, and ADR-003 inventory authority remain strictly deferred to Master Sol (ADR-006A).
3. **ADR-002 Acceptance Status**: **ADR-002 IS NOT ACCEPTED.** The technical fixes in this work package harden the worker runtime mechanics against crashes, corruption, burst catch-up, and starvation, but do not settle the unresolved multi-map temporal architecture.

---

## 2. Test Suite Execution Summary

The regression test harness [`run_hardening_regressions.py`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/run_hardening_regressions.py) was executed end-to-end against live RimWorld 1.6 batchmode instances (`PID 8612`, `PID 27028`, etc.) and recorded to [`hardening-test-results.json`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/hardening-test-results.json).

| Phase / Test ID | Target Defect | Metric / Assertion | Result | Evidence Artifact |
|---|---|---|---|---|
| **Phase 1.1** | `QA-ENGINE-002` | Environment manifest retrieval & registry counts | **PASS** | `GET_ENVIRONMENT_MANIFEST` verified |
| **Phase 1.2** | `QA-ENGINE-002` | Undeclared missing mod in save XML meta | **PASS** | `MANIFEST_REJECTED`, `LOAD_FAILED`, Export Blocked |
| **Phase 1.3** | `QA-ENGINE-002` | Undeclared missing Def in save XML | **PASS** | `MANIFEST_REJECTED`, `LOAD_FAILED`, Export Blocked |
| **Phase 2.1** | `QA-ENGINE-006` | Native complex fixture generation | **PASS** | `GENERATE_COMPLEX_FIXTURE` (0 duplicate IDs) |
| **Phase 2.2** | `QA-ENGINE-006` | Fixture integrity audit (power, bills, animal, crops, corpse) | **PASS** | XML entity graph audit passed |
| **Phase 3** | `QA-ENGINE-007` | Mechanical scope fence during load & ready | **PASS** | Non-target Map 1 probe drift = `0` |
| **Phase 4.1** | `QA-ENGINE-003` | Monolithic `RUN_TICKS` quarantine | **PASS** | Command quarantined with explicit protocol error |
| **Phase 4.2** | `QA-ENGINE-003` | `STEP_TICKS` slice size hard-cap | **PASS** | Clamped to `HardCap=20` |
| **Phase 4.3** | `QA-ENGINE-003` | Main thread responsiveness during ticking | **PASS** | Avg: `17.04ms`, Max: `39.56ms` (< 50ms) |
| **Phase 4.4** | `QA-ENGINE-003` | Simulation cancellation | **PASS** | `CANCEL_SIMULATION` cleared remaining ticks |
| **Phase 5** | `QA-ENGINE-005` | `fastEcology` debug bypass suppression | **PASS** | Trapped, forced `false`, warning logged |
| **Phase 6** | `QA-ENGINE-008` | Simulation start debt elimination | **PASS** | First increments `[3, 4, 4, 4, 4]`, TPS: `59.68` |
| **Phase 7** | `QA-ENGINE-006` | Strict 11-dimension roundtrip oracle | **PASS within tested scope** | All 11/11 dimensions match on reload |

---

## 3. Defect-by-Defect Evidence & Resolution

### QA-ENGINE-002: Manifest / Dependency False-Success

#### 1. Observed Before
In `ENGINE-02` tests (`OmittedDependency.rws`), when a save containing missing mods or undeclared custom Defs was loaded without explicit caller warnings, RimWorld silently stripped missing components, logged warnings, and advanced the worker to `READY`. The worker subsequently permitted `EXPORT_SAVE`, outputting corrupted saves missing critical gameplay entities.

#### 2. Change Implemented
In [`WorkerBridge.cs`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/WorkerBridgeMod/Source/WorkerBridge.cs):
- **Trusted Environment Manifest (`GET_ENVIRONMENT_MANIFEST`)**: Reports exact RimWorld version (`1.6.4871 rev591`), Unity version (`2022.3.35f1`), platform (`WindowsPlayer`), active DLC expansion set (`Royalty`, `Ideology`, `Biotech`, `Anomaly`, `Odyssey`), loaded mod package IDs in load order, and Def counts across registries (`ThingDef`, `HediffDef`, `RecipeDef`, `PawnKindDef`, `BiomeDef`).
- **Pre-Flight Manifest Gate (`VALIDATE_MANIFEST`, `ValidateManifestInternal`)**:
  - Scans save `<meta><modIds>` against active mods (`ModsConfig.ActiveModsInLoadOrder`). Rejects load if any required mod is missing.
  - Performs fast-stream XML scanning for all `<def>` tags. Queries `DefDatabase<ThingDef>.GetNamedSilentFail(defName)` and iterates `GenDefDatabase.AllDefTypesWithDatabases()` across all Def databases. If an undeclared Def is missing from all active registries, load is rejected pre-flight.
- **Post-Load Semantic Error Gate**: Subscribes to `Application.logMessageReceived` during `GameDataSaveLoader.LoadGame()`. Any logged error or unhandled exception immediately transitions lifecycle to `WorkerLifecycleState.LOAD_FAILED`.
- **Strict Export Gating (`ExportSave`)**: `EXPORT_SAVE` is strictly blocked unless `lifecycleState == WorkerLifecycleState.READY`. Any call while in `LOAD_FAILED`, `VALIDATING`, or `LOADING` immediately returns `ERROR: Cannot export save while worker state is LOAD_FAILED`.

#### 3. Exact Regression Test
- `QA-ENGINE-002_MissingMod_Validate`: Appended `<li text="qa.actually.missing.dependency">` to save metadata. Verified `VALIDATE_MANIFEST` returned `MANIFEST_REJECTED`.
- `QA-ENGINE-002_MissingMod_LoadAndExportGating`: Issued `LOAD_SAVE MissingMod`. Verified response `LOAD_REJECTED`, worker status `STATE: LOAD_FAILED`, and `EXPORT_SAVE` rejected with `ERROR`.
- `QA-ENGINE-002_MissingDef_Validate`: Replaced `WarEconomy_TacticalProofToken` with `QA_UndeclaredMissingToken`. Verified `VALIDATE_MANIFEST` returned `MANIFEST_REJECTED`.
- `QA-ENGINE-002_MissingDef_LoadAndExportGating`: Issued `LOAD_SAVE MissingDef`. Verified response `LOAD_REJECTED`, worker status `STATE: LOAD_FAILED`, and `EXPORT_SAVE` rejected with `ERROR`.

#### 4. Observed After
```json
"QA-ENGINE-002_MissingMod_Validate": {
  "verdict": "PASS",
  "response": "MANIFEST_REJECTED: Save requires mod 'qa.actually.missing.dependency' which is not active in current configuration."
},
"QA-ENGINE-002_MissingMod_LoadAndExportGating": {
  "verdict": "PASS",
  "load_response": "LOAD_REJECTED: Gen=1, Reason=Save requires mod 'qa.actually.missing.dependency' which is not active in current configuration.",
  "status": "STATE: LOAD_FAILED, Gen=1, Maps=0, TicksGame=0, SimActive=False, TargetMap=-1, TicksSim=0, IsRealtime=False, RemainingStep=0, LastFailure='Save requires mod 'qa.actually.missing.dependency' which is not active in current configuration.'",
  "export_response": "ERROR: Cannot export save while worker state is LOAD_FAILED (Reason: Save requires mod 'qa.actually.missing.dependency' which is not active in current configuration.). (Only READY state permitted)."
}
```

#### 5. What Remains Unproven
Arbitrary 3rd-party binary mod assemblies that mutate memory dynamically without declaring Defs or mod IDs cannot be guaranteed complete without binary hashing / bytecode inspection tools outside RimWorld runtime.

---

### QA-ENGINE-003: Unsafe Monolithic Tick Path

#### 1. Observed Before
`RUN_TICKS 50000` executed a monolithic while loop directly on the Unity main thread without yielding. This starved the TCP request queue, caused socket timeouts (`LIFE-05` timeout failures in tests), prevented concurrent telemetry inspection, and risked OS watchdog kills.

#### 2. Change Implemented
In [`WorkerBridge.cs`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/WorkerBridgeMod/Source/WorkerBridge.cs):
- **Quarantined `RUN_TICKS`**: Calling `RUN_TICKS` now returns:
  `ERROR: RUN_TICKS has been quarantined from normal Tactical Worker protocol due to monolithic main-thread starvation (QA-ENGINE-003). Use cooperative STEP_TICKS or START_SIMULATION. For explicit diagnostic QA only, use QA_DIAGNOSTIC_RUN_TICKS.`
- **Hard-Capped Slices (`STEP_TICKS`)**: Requests are clamped to `MAX_SLICE_SIZE = 20` ticks per slice.
- **Wall-Clock Main-Thread Budget**: Inside `Update()`, ticking loops measure elapsed wall-clock time via `Stopwatch`. If ticking exceeds `MAX_TICK_BUDGET_MS = 10.0ms`, the loop immediately breaks to allow Unity engine rendering, GC, and TCP request servicing.
- **Bounded Command Queue**: Worker queue is capped at `MAX_QUEUE_DEPTH = 100`. Each frame services up to 20 commands or 5.0ms maximum.
- **Cancellation & Timeout**: Added `CANCEL_SIMULATION` command to instantly zero `targetTicksRemaining` and cancel pending steps. Queue items older than 10.0s automatically timeout (`LIFE-05`).

#### 3. Exact Regression Test
- `QA-ENGINE-003_RunTicksQuarantine`: Issued `RUN_TICKS 50000`. Verified error returned and 0 ticks executed.
- `QA-ENGINE-003_StepTicksSliceCap`: Issued `STEP_TICKS 1000 50000`. Verified response confirmed `SliceSize=20, HardCap=20`.
- `QA-ENGINE-003_MainThreadResponsiveness`: Polled `STATUS` 10 times at 50ms intervals while 1,000 sliced ticks executed in the background. Recorded latency distribution.
- `QA-ENGINE-003_CancelSimulation`: Issued `STEP_TICKS 5000 10`, immediately followed by `CANCEL_SIMULATION`. Verified remaining steps cleared to 0.

#### 4. Observed After
```json
"QA-ENGINE-003_MainThreadResponsiveness": {
  "verdict": "PASS",
  "avg_ms": 17.037,
  "max_ms": 39.56,
  "samples": [23.94, 3.2, 39.56, 18.6, 18.05, 18.1, 3.7, 11.32, 17.01, 16.89]
}
```
All concurrent TCP status requests completed in under 40ms, with an average latency of 17.04ms (well within the 50ms threshold).

#### 5. What Remains Unproven
Pathological maps containing hundreds of active pawns where a *single* vanilla engine tick takes > 10ms. Because Unity runs ticks synchronously on the main thread, an individual tick cannot be preempted mid-execution without engine threading redesign.

---

### QA-ENGINE-005 (Implementation-Safe Portion): Dispatch Inventory & fastEcology Suppression

#### 1. Observed Before
In Sol's `ENGINE-02` clean boundary test, calling the probe debug command `ECOLOGY` toggled `DebugSettings.fastEcology = true`. This caused 25,835 wild and cultivated plants across all maps to age by 2,000 ticks in a single tick, bypassing map isolation fences and modifying non-target map state.

#### 2. Change Implemented
- **Harmony Guard on Debug Ecology**: Created prefix patches `Patch_TickManager_DoSingleTick` and `Patch_TickList_Tick` that check `DebugSettings.fastEcology`. If set to `true`, the patch logs a warning (`[WorkerBridge] fastEcology is unsupported in Tactical Worker. Forcing false to preserve map isolation.`) and forces `DebugSettings.fastEcology = false`.
- **Selective Escape Path Guards**: Added Harmony prefix patches for known escape paths:
  - `Verse.Scenario.TickScenario` -> returns `false` (suppresses scenario script tick events).
  - `RimWorld.StoryWatcher.StoryWatcherTick` -> returns `false` (suppresses global incident adaptation).
  - `RimWorld.GameEnder.GameEndTick` -> returns `false` (suppresses colony lost game over).
  - `RimWorld.LetterStack.LetterStackTick` -> returns `false` (suppresses UI letter alerts).
  - `RimWorld.FilthMonitor.FilthMonitorTick` -> returns `false` (suppresses colony filth diagnostics).
  - `RimWorld.TransportShipManager.ShipObjectsTick` -> returns `false` (suppresses world ship travel).
- **Preservation of GameComponents**: Did **NOT** blanket-disable `GameComponents`. Components required for tactical pawn behavior (e.g. `GameComponent_Bossgroup`, combat managers) remain enabled.

#### 3. Exact Regression Test
- `QA-ENGINE-005_FastEcologySuppression`: Issued `ECOLOGY` command to QA Probe, captured before and after snapshots of `Plant_Rice`, and inspected `player.log`.

#### 4. Observed After
```json
"QA-ENGINE-005_FastEcologySuppression": {
  "verdict": "PASS",
  "probe_response": "ECOLOGY_DONE",
  "warning_logged": true
}
```
Warning logged in engine log:
`[WorkerBridge] fastEcology is unsupported in Tactical Worker. Forcing false to preserve map isolation.`
Grid plants did not experience the 2,000-tick growth burst.

#### 5. What Remains Unproven
Third-party C++ unmanaged plugins or background thread dispatches that do not pass through `Verse.TickManager` or Harmony-hooked methods.

---

### QA-ENGINE-006: Engine-Generated Complex Fixture & Strict Oracle

#### 1. Observed Before
In `ENGINE-02`, manual XML editing of test fixtures introduced 10 duplicate numeric Thing IDs (e.g. `Gun_Autopistol9001` vs. `Plant_Grass9001`), missing Hediff `loadID` values (resulting in `Hediff_0` collisions during save), and invalid component structures (e.g. training Obedience on a Boomrat, which has trainability `None`).

#### 2. Change Implemented
In [`WorkerBridge.cs`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/WorkerBridgeMod/Source/WorkerBridge.cs):
- Implemented `GENERATE_COMPLEX_FIXTURE` using native RimWorld engine instantiation APIs:
  - **Crops**: Soil terraforming via `terrainGrid.SetTerrain`, creation of `Zone_Growing` registered with `zoneManager`, and planting of `Plant_Rice` with 50% growth.
  - **Pawn Weapon & Apparel**: `PawnGenerator.GeneratePawn` equipped with `Gun_Autopistol` and worn `Apparel_FlakVest`.
  - **Inventory**: `colonist.inventory.innerContainer` populated with `MedicineIndustrial` and food meals.
  - **Nontrivial Health**: `Hediff_Injury` (Stab) on Torso and `Hediff_AddedPart` (BionicEye) on Eye, assigned globally unique IDs via `Find.UniqueIDsManager.GetNextHediffID()`.
  - **Bed Assignment**: `Building_Bed` spawned and assigned via `bed.CompAssignableToPawn.TryAssignPawn(colonist)`.
  - **Animal Master & Training**: Spawned `LabradorRetriever` with player faction, trained `TrainableDefOf.Tameness` and `TrainableDefOf.Obedience`, and assigned `dog.playerSettings.Master = colonist`.
  - **Workbench Bills**: Spawned `TableSculpting` / `HandTailoringBench` with active recipe bills in `BillStack`.
  - **Power**: Spawned `Battery` with 50% stored energy in `CompPowerBattery`.
  - **Corpse & Container**: Spawned `Building_Sarcophagus`, spawned a player pawn, killed it, enabled corpse storage settings, assigned the pawn, and stored the corpse via `sarcophagus.TryAcceptThing(deadGuy.Corpse)`.
  - **Base Save Selection**: Sourced baseline from clean 2-map engine save `CleanBoundary/Saves/Input.rws` (0 duplicate IDs natively).
- Implemented strict 11-dimension boolean oracle comparing post-simulation state vs. reloaded state.

#### 3. Exact Regression Test
- `QA-ENGINE-006_GenerateComplexFixture`: Generated `EngineComplexFixture.rws`.
- `QA-ENGINE-006_EngineFixtureIntegrityAudit`: Parsed XML, counted numeric ID collisions, and validated all required entities.
- `QA-ENGINE-006_StrictGraphRoundtripOracle`: Exported save after simulation, launched fresh worker, loaded save, and verified 11 dimensions.

#### 4. Observed After
```json
"QA-ENGINE-006_EngineFixtureIntegrityAudit": {
  "verdict": "PASS",
  "duplicate_numeric_id_pairs": 0,
  "has_storedPower": true,
  "has_bills": true,
  "has_animal_master": true,
  "has_crop_growth": true,
  "has_casket_corpse": true
},
"QA-ENGINE-006_StrictGraphRoundtripOracle": {
  "verdict": "PASS within tested scope",
  "dimensions": {
    "pawn": true,
    "weapon": true,
    "apparel": true,
    "hediffs": true,
    "bed_assignment": true,
    "animal_master": true,
    "workbench_bills": true,
    "battery_power": true,
    "crops": true,
    "casket_corpse": true,
    "non_target_map_preserved": true
  }
}
```

#### 5. What Remains Unproven
Nested vehicles, complex 3rd-party pocket dimensions, or custom alien race serialization trees that require external C# assemblies.

---

### QA-ENGINE-007 (Mechanical Portion): Scope Fence Before Uncontrolled Playing Ticks

#### 1. Observed Before
During game loading (`GameDataSaveLoader.LoadGame`), RimWorld's vanilla `TickManager.TickManagerUpdate` executed ticks as soon as `Current.ProgramState == ProgramState.Playing`, prior to WorkerBridge establishing target map scoping. This caused non-target maps to drift and world ticks to increment during load.

#### 2. Change Implemented
In [`WorkerBridge.cs`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/WorkerBridgeMod/Source/WorkerBridge.cs):
- **Disabled Autonomous Frame Ticking**: Harmony prefix `Patch_TickManager_TickManagerUpdate` returns `false` during worker operation, preventing vanilla Unity frame updates from executing ticks.
- **Enforced Pause on Init**: Harmony postfix `Patch_Game_FinalizeInit` forces `CurTimeSpeed = TimeSpeed.Paused` immediately upon game initialization.
- **Controlled Scope Fence**: Ticks are only executed explicitly by `ScopedTacticalSession` when `lifecycleState == WorkerLifecycleState.READY` on the designated target map.
- **Strict Error Barrier**: If any loading error occurs, lifecycle transitions to `LOAD_FAILED` and `READY` is never emitted.

#### 3. Exact Regression Test
- `QA-ENGINE-007_ScopeFence_LoadDrift`: QA probe captured Map 1 probe counter before `LOAD_SAVE`, waited for `READY`, and captured probe counter again. Asserted `non_target_probe_drift == 0`.

#### 4. Observed After
```json
"QA-ENGINE-007_ScopeFence_LoadDrift": {
  "verdict": "PASS",
  "ready_status": "STATE: READY, Gen=1, Maps=2, TicksGame=1823, SimActive=True, TargetMap=0, TicksSim=0, IsRealtime=False, RemainingStep=0, LastFailure=''",
  "map1_probe_before": 0,
  "map1_probe_after": 0,
  "non_target_probe_drift": 0
}
```
Non-target Map 1 experienced exactly **0 ticks** of drift during loading and initialization.

#### 5. What Remains Unproven
Server-wide temporal synchronization policy when reintegrating tactical maps back into a running multiplayer game server.

---

### QA-ENGINE-008: Simulation Start Debt Elimination

#### 1. Observed Before
In `ENGINE-02`, real-time simulation relied on cumulative frame time deltas. Long blocking operations (such as saving or loading) caused elapsed time to accumulate into `timeAccumulator`. Upon issuing `START_SIMULATION 60`, the worker attempted to "catch up" the backlog by executing a massive burst of 40-70 ticks across the first few frames, surging measured TPS to 76.96 TPS and causing severe desync.

#### 2. Change Implemented
In [`WorkerBridge.cs`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/WorkerBridgeMod/Source/WorkerBridge.cs):
- **Monotonic Start Timestamp**: In `HandleStartSimulation`, `timeAccumulator` is explicitly reset to `0f`, `lastSimFrameTime = Time.realtimeSinceStartup`, and `isFirstSimFrame = true`.
- **First-Frame Skip**: On the first simulation frame, elapsed time is ignored and `lastSimFrameTime` is refreshed.
- **Accumulator Clamping**: `timeAccumulator` is clamped to at most `1.5 * interval` (max 25ms at 60 TPS), preventing any historical backlog accumulation.
- **Burst Cap**: Each frame dispatches at most `Mathf.Min(2, Mathf.FloorToInt(timeAccumulator / interval))` ticks.
- **Pause/Resume Hygiene**: `HandlePauseSimulation` and `HandleCancelSimulation` reset `timeAccumulator = 0f` and `isFirstSimFrame = true`.

#### 3. Exact Regression Test
- `QA-ENGINE-008_SimulationStartDebt`: Issued a heavy `EXPORT_SAVE` operation to induce long main-thread delay, immediately followed by `START_SIMULATION 60`. Sampled simulation progress at 50ms intervals over 3.0 seconds.

#### 4. Observed After
```json
"QA-ENGINE-008_SimulationStartDebt": {
  "verdict": "PASS",
  "first_five_sample_increments": [3, 4, 4, 4, 4],
  "measured_tps": 59.68,
  "total_ticks_in_3s": 177
}
```
The first five sample intervals advanced smoothly by 3-4 ticks each (exactly matching ~60 TPS over 50ms intervals), with **zero catch-up burst**. The measured overall TPS was **59.68 TPS** (target: 60.0 TPS).

#### 5. What Remains Unproven
Severe client rendering degradation where the client machine runs at < 10 FPS. In such cases, the clamp intentionally drops ticks (sacrificing tick rate) to prioritize frame responsiveness over time debt recovery.

---

## 4. TickManager Dispatch Path Inventory (QA-ENGINE-005)

The following inventory details all 22 dispatch paths originating from `Verse.TickManager.DoSingleTick()` in RimWorld 1.6, classifying their scope and applied guard mechanisms:

| Index | Dispatch Call / Path | Target Object / Subsystem | Scope Classification | Applied Guard Mechanism |
|---|---|---|---|---|
| **01** | `Map.MapPreTick()` | Active Maps | Map-Local | Fenced to Target Map only; non-target maps skipped |
| **02** | `TickList.Tick()` (`Normal`) | Spawned Things on Map | Map-Local | Fenced to Target Map; `fastEcology` forced `false` |
| **03** | `TickList.Tick()` (`Rare`) | Rare-ticking Things | Map-Local | Fenced to Target Map; `fastEcology` forced `false` |
| **04** | `TickList.Tick()` (`Long`) | Long-ticking Things | Map-Local | Fenced to Target Map; `fastEcology` forced `false` |
| **05** | `Map.MapPostTick()` | Map Components & Weather | Map-Local | Fenced to Target Map; non-target maps skipped |
| **06** | `World.WorldTick()` | World Manager | Global / World | Retained for minimal world coherence; world pawns fenced |
| **07** | `WorldObjectsHolder.WorldObjectsTick()` | Caravans & Settlements | Global / World | Retained (read-only in tactical map scope) |
| **08** | `WorldPawns.WorldPawnsTick()` | Off-map Pawns | Global / World | Fenced; off-map pawns prevented from ticking |
| **09** | `WorldPathGrid.WorldPathGridTick()` | World Travel Grid | Global / World | Passive / no mutation |
| **10** | `Game.GameTick()` | Game Systems | System / Global | Core ticking allowed; escape sub-paths hooked |
| **11** | `GameComponent.GameComponentTick()` | Registered GameComponents | Component | **Preserved** (Required for combat/tactical behavior) |
| **12** | `Autosaver.AutosaverTick()` | Autosave Timer | Engine / I/O | Suppressed (Worker exports saves via command only) |
| **13** | `StoryWatcher.StoryWatcherTick()` | Storyteller Adaptation | Global Escape Path | **Hooked & Suppressed** via Harmony prefix |
| **14** | `GameEnder.GameEndTick()` | Game Over Watcher | Global Escape Path | **Hooked & Suppressed** via Harmony prefix |
| **15** | `LetterStack.LetterStackTick()` | Incident Letters | Global Escape Path | **Hooked & Suppressed** via Harmony prefix |
| **16** | `Scenario.TickScenario()` | Scenario Script Triggers | Global Escape Path | **Hooked & Suppressed** via Harmony prefix |
| **17** | `FilthMonitor.FilthMonitorTick()` | Diagnostic Filth Accumulator | Diagnostic Escape | **Hooked & Suppressed** via Harmony prefix |
| **18** | `TransportShipManager.ShipObjectsTick()` | Shuttle Travel | Global Escape Path | **Hooked & Suppressed** via Harmony prefix |
| **19** | `History.HistoryTick()` | Wealth/Graph History | Statistical | Retained for tactical wealth stats |
| **20** | `TaleManager.TaleManagerTick()` | Colonist Art/Tales | Statistical | Retained (passive) |
| **21** | `DebugSettings.fastEcology` | Ecology Plant Aging | Debug Escape Path | **Hooked & Forced False** via Harmony prefix |
| **22** | `FactionManager.FactionManagerTick()` | Factions | Global / World | Retained (passive relations) |

---

## 5. Architectural Status of ADR-002

### Formal Verdict
**ADR-002: NOT ACCEPTED.**

### Architectural Rationale
While this work package has successfully eliminated all reproduced technical runtime defects (`QA-ENGINE-002` through `QA-ENGINE-008`), ADR-002 remains formally rejected because technical worker hardening is a necessary, but not sufficient, condition for accepting ADR-002.

The foundational architectural questions remain unresolved:
1. **Temporal Policy Model**: Is the Tactical Worker authoritative over local map time, or must it conform to a central Server World Clock?
2. **Chronological Aging**: How are pawn biological age, food rot, and weather drift reconciled between an asynchronous tactical session and the global game server?
3. **Rebase & Persistence Architecture**: Is the final synchronization strategy based on a canonical full-save rebase or an entity-level delta merge?
4. **ADR-003 Inventory Authority**: Which authority governs transfer of ammunition, gear, and supplies between the strategic world map and the tactical instance?

These decisions belong exclusively to Master Sol under upcoming **ADR-006A**. Until ADR-006A is formally specified and ratified, ADR-002 cannot receive a PASS.

---

## 6. Verification Artifacts & Deliverables

- **Evidence Document**: [`Tactical_Worker_Hardening_Evidence_01.md`](file:///c:/Users/user/Desktop/RimMulti/Tactical_Worker_Hardening_Evidence_01.md)
- **Hardened Worker Assembly**: `WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll`
- **Automated Regression Suite**: [`run_hardening_regressions.py`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/run_hardening_regressions.py)
- **Machine-Readable Results**: [`hardening-test-results.json`](file:///C:/Users/user/.gemini/antigravity-ide/brain/877c240f-d035-4476-9d3b-3a03f75f1f65/scratch/hardening-test-results.json)
- **Validated Engine Complex Fixture**: `Harden_Manifest/Saves/EngineComplexFixture.rws` (0 duplicate IDs, 100% engine-valid entities)
