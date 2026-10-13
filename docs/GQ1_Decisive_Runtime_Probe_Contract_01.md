# GQ1_Decisive_Runtime_Probe_Contract_01.md

**Status:** DECISION / EVIDENCE CONTRACT — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## Objective
Convert current G-Q1, PlayerGlobal, and SharedWorld uncertainty into the smallest decisive runtime probe battery for Dev A and Sol. This contract defines the exact experiments needed to evaluate temporal isolation across execution domains without prematurely freezing the topology or `PlayerGlobal` physical schema.

**Controlling Hypothesis:**
`VANILLA MULTI-MAP FIRST -> MINIMAL INTERCEPTION -> SEPARATE EXECUTION ISLAND ONLY IF FALSIFIED`
*(Note: Execution-island / `LocalClock` domain is the topology unit, not `SettlementId`.)*

---

## 1. Probe Topology

The battery requires executing three comparable runtime configurations under strictly controlled variables (same `ContentProfile`, same source fixture lineage, same tick horizons, and same semantic oracle):

*   **Model A (Vanilla Baseline):** Shared execution island. Map A (Target) and Map B (Sibling/Frozen) loaded into the same RimWorld engine instance without custom temporal patching.
*   **Model B (Minimal Interception):** Shared execution island. Same as A, but implementing targeted Harmony intercepts (e.g., virtualizing `GenTicks` or `Find.TickManager`) *only* for the specific subsystems proven to leak in Model A.
*   **Model C (Control/Separate Island):** Map A and Map B run in completely separate OS processes / Engine Host instances.

## 2. Exact Clock Experiment

Execute the following horizons on the loaded topology:
*   **Action:** Actively/sliced tick Map A. Keep Map B locally frozen (zero map-local ticks invoked).
*   **Horizons:**
    *   Short: ~100 ticks.
    *   Medium: ~5,000 ticks.
    *   Long: ~60,000 ticks (1 in-game day).
    *   Extended: ~900,000 ticks (1 in-game quadrum) to force age, condition, and seasonal timers.
*   **Record at each horizon:** `TicksGame`, `TicksAbs`, `LocalClock` representation (Map-local), Map-local tick counts for Map A and Map B, and Domain/Wall time (strictly for logging, NEVER as simulation ordering authority).

## 3. Semantic Dimensions

For the frozen Map B, the probe must measure the following dimensions (if technically observable without destructive memory reads):
*   **Pawns:** Position, active job/stance, selected needs (rest/hunger), biological vs. chronological age, hediff severity/immunity progression.
*   **Environment:** Plant growth/age, fire spread, map condition duration (e.g., toxic fallout).
*   **Infrastructure:** Power grid state, fuel levels, workbench cooldowns.
*   **Global/Abstract:** Reservations, assignments, ideology ritual timers, quest expiration, storyteller/incident pools, `WorldPawns` GC lifecycle, and selected `GameComponents`.
*   **Mod Compatibility:** Include a representative admitted-profile mod (e.g., a custom tick manager) to monitor unhandled global hooks.

*(Explicitly mark any dimension that is unobservable via headless state inspection).*

## 4. Oracle (Evaluation Criteria)

**Do NOT use raw `.rws` byte equality or SHA hashes as pass/fail.** (Transient caches and RNG state make byte-diffs unreliable).

**Required Oracle Pipeline:**
1.  Capture baseline `SupportedSemanticManifest` (a deterministic census of Map B's material assets, pawn stats, and entity IDs) before the experiment.
2.  Execute temporal experiment (ticking Map A).
3.  Save and fresh-load the Map B artifact.
4.  Recompute the `SupportedSemanticManifest`.
5.  Compare against the explicit allowed-difference set.
6.  Verify stable `EntityId`, custody, and material conservation (e.g., no items vanished, no pawns died).

## 5. Allowed-Difference Policy

*   **Allowed Cosmetic/Global Drift:** Visual sky/weather changes, chronological calendar year changes, day/night cycles (provided they do not kill plants via lack of light during offline time).
*   **Allowed Reconstructible Drift:** Ephemeral `PlayLog` entries, `TaleManager` bloat, transient UI/camera caches.
*   **PROHIBITED Frozen Material-State Drift:** Pawn biological aging, Hediff progression (fatal diseases advancing), plant rotting, item deterioration, job completion/failure, or fuel consumption on Map B.
*   **PROHIBITED Domain/Global Authority Drift:** Map B autonomously completing a Quest, spawning a raid, or mutating Faction relations while its `LocalClock` is frozen.
*   **Unresolved:** Any difference not classified above forces a halt until Master defines its policy. (No difference is "cosmetic" merely by naming convention; it requires noninterference evidence).

## 6. Resume / Catch-up

After the extended frozen interval:
*   Resume Map B `LocalClock` ticking.
*   **Observe:** Immediate and subsequent 100 ticks.
*   **Detect:** "Catch-up bursts" (e.g., 50 days of plant growth resolving in 1 tick, or pawns instantly collapsing from sleep deprivation).
*   **Detect:** Timers that jump abruptly based on global absolute time instead of local elapsed time.
*   **Action:** Fresh-save and reload again.
*   **Pass Criteria:** Zero prohibited material catch-up or silent canonical mutation. Map B continues exactly as if no real-world time or Map A time had passed.

## 7. Shared-Island Barrier (E-B Semantics)

To prove feasibility of online mutation within a shared execution topology:
*   Establish a `DELTA_BARRIER` on the shared island containing Map A (active) and Map B (active).
*   Verify *all* scoped Settlements within that execution island achieve quiescence.
*   Apply a neutral, bounded test mutation (e.g., spawn 1 Silver on Map A). No unresolved product-policy trade logic.
*   Release barrier. Resume ticking.
*   **Prove:** Map B's material state remains entirely unchanged.
*   **Prove:** No catch-up burst on Map A or Map B post-resume.

## 8. PlayerGlobal / SharedWorld Observation

During the tick horizons, monitor `Research`, `Ideology`, `Quests`, `WorldPawns`, and `GameComponents`:
*   Identify where the state physically lives in memory.
*   Identify which clock (`TicksGame`, `TicksAbs`, UTC) triggers its updates.
*   Determine if a fresh load of Map B strictly requires this state to avoid null references.
*   Determine if ticking Map A causes canonical mutations to this global state that Map B automatically inherits (e.g., Research unlocks).
*   Classify if the state is safely projectable (read-only) or reconstructible.

## 9. Model B Falsification Surface

If Model A leaks prohibited state (e.g., `TicksAbs` kills a frozen pawn via disease):
*   Identify the exact getter/tick path (e.g., `Pawn_HealthTracker`).
*   Estimate interception scope (Bounded vs. Broad).
*   **Falsify Model B if:** The required Harmony patches are unbounded/unpatchable, unsafe to unrelated global state, routinely bypassed by supported mods, or unable to preserve deterministic save/load/resume semantics.
*   If falsified, the hypothesis shifts to Model C.

## 10. Model C Control

Use the separate-process topology to measure the baseline:
*   Measure absolute semantic isolation (guaranteed zero drift).
*   Measure the RAM/CPU cost of running $N$ execution islands vs. 1 shared island.
*   Identify the IPC/Network complexity of projecting `FactionDomainState` and `SharedWorldProjection` across multiple OS processes compared to a shared memory space.

## 11. Decision Matrix Output Format

The final report from A/Sol must populate this matrix:

| Subsystem / Observable | Model A Result (Drift?) | Model B Required? | Model C Control | Material Impact | Decision Consequence | Next Runtime Owner |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| e.g., Hediff Severity | (Pass/Fail) | (Yes/No/Scope) | (Baseline) | (High/Low) | (Forces C if unpatchable) | (Map vs Global) |

## 12. E2 Ownership (Dev vs. Verification)

*   **Dev A (E1):** Implement the temporal harness, wire up the headless topologies (A, B, C), define the `SupportedSemanticManifest` extractor, and run the initial feasibility battery to identify the most obvious leaks.
*   **Sol (E2):** Independently execute the battery using hostile configurations, edge-case mods from the admitted profile, and extreme tick horizons. Sol is solely responsible for asserting that no prohibited drift occurs. *Feasibility does not equal verification.*

## 13. Stop Line

Execution of this contract will end with one of the following architectural states:
*   **Model A sufficient:** Vanilla shared-island ticking naturally isolates required state for the initial profile.
*   **Model B preferred:** Vanilla leaks, but interception is narrowly bounded, stable, and highly performant compared to Model C.
*   **Model C required:** Deep engine temporal coupling makes shared-islands fundamentally unsafe for divergent `LocalClock` domains.
*   **Still OPEN:** Probe reveals a smaller, specific blocker set requiring Master's explicit product-policy resolution.

*(Do not close G-Q1 based on assumptions; await the E2 semantic oracle results.)*