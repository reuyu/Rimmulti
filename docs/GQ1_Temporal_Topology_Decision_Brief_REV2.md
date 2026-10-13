# GQ1_Temporal_Topology_Decision_Brief_REV2.md

**Status:** DECISION / EVIDENCE BRIEF — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Candidate Topology Models

The core architecture must resolve how multiple `LocalClockId` ($L_s$) domains progress when a player owns multiple Settlements.

| Characteristic | Model A: Vanilla Multi-Map (Shared Global Tick) | Model B: Vanilla Multi-Map + Minimal Interception | Model C: Separate Execution Islands (Per-Clock Process) |
| :--- | :--- | :--- | :--- |
| **Independent Freezing** | Map content freezes (pawns/jobs), but global time ($G$) advances. | Map content freezes, and $G$ getters are virtualized per map. | Absolute physical process isolation. |
| **Global State** | `TicksGame` and `TicksAbs` march forward for all maps. | Intercepted/Faked depending on context. | Fully isolated per process. |
| **Interception Surface** | Zero. | High (Harmony patches on `Find.TickManager` and `GenTicks`). | Zero. |
| **Materialization Cost** | Low (Single engine load). | Low (Single engine load). | Extreme (Full RimWorld boot per Settlement). |
| **Cross-Map References** | Natively supported via `WorldPawns`. | Natively supported but temporal desync risks exist. | Hard barrier; requires complex IPC/Network sync. |
| **Barrier Implications** | Scoped to the entire engine; halts all loaded maps. | Scoped to the entire engine; halts all loaded maps. | Isolated; barriers only halt the target map. |
| **Failure / Recovery** | Process crash kills all active maps. | Process crash kills all active maps. | Process crash kills only one map. |
| **Mod Compatibility Risk** | High (Mods relying on $G$ will desync inactive maps). | Medium (Mods may bypass patched getters). | Low (Standard vanilla execution environment). |

## 2. Temporal Subsystem Inventory

Based on native RimWorld architecture and current Engine Host evidence, temporal systems map as follows:

*   **Map-Local Tick Driven (Freeze safely):**
    *   Pawn biological needs (hunger, rest).
    *   Pawn job execution, pathing, and active stances.
    *   Plant resting/growth updates (if tied to map ticking).
    *   Map conditions (e.g., toxic fallout duration on a specific map).
    *   Power grid, fuel consumption, and workbench cooldowns.
*   **Global `TicksGame` / `TicksAbs` Driven (Advance regardless of map tick):**
    *   Chronological age (birthdays).
    *   Weather/Sky visual interpolation and Day/Night cycles.
    *   `GameComponents` `Tick()` execution.
    *   Storyteller / Incident tracking timers.
*   **Mixed / Unknown (Requires Probes):**
    *   Hediff severity/immunity timers (often mixed biology + global tick).
    *   Ideology ritual cooldowns and role expectation timers.
    *   Research progression (often map-driven by pawns, but globally tracked).
    *   Modded tick managers (e.g., custom faction economy mods).
*   **Domain Authority (Should NOT be Engine-Driven):**
    *   Quest expiration and generation.
    *   Caravan/Transit world objects (Driven by Shared World `TransitClockId`).

## 3. LocalClock Semantic Contract

The WarEconomy `LocalClockId` contract strictly requires decoupling the elapsed simulation time of a *specific* settlement ($L_s$) from global chronology ($G$).

**Minimum Observable Contract:**
1.  **Local Simulation:** If a map is offline/frozen, its physical assets (Pawns, Items, Buildings) must endure exactly zero simulated time decay or progression.
2.  **Domain Deadlines vs. Game Time:** Economy events (Auto-Shop fulfillment, Tax epochs) are driven by Server UTC or discrete Domain operations, *not* engine `TicksGame`.
3.  **Visuals vs. Canonical State:** It is architecturally acceptable if the sky (day/night) or chronological year desyncs across maps, *provided* this does not corrupt the saved XML artifact's semantic validity or `ArtifactBaseStateRevision`. We only need to virtualize getters that affect canonical material state (e.g., preventing a frozen pawn from dying of old age because the global clock advanced 50 years).

## 4. E-B Implication (Barrier Scoping)

The current `DELTA_BARRIER` is execution-island scoped.
*   If two Settlements (Map A and Map B) share one Engine instance (Model A/B), triggering a `DELTA_BARRIER` on Map A will inherently quiesce Map B.
*   **Acceptability for First Production:** This is fully acceptable. If a single owner is running both maps in a single client process, freezing the entire client to process an offline trade is a valid UX tradeoff to avoid Model C's massive RAM cost.
*   **Requirement for Independent Ticking (Model C):** Separate processes are *only* mandated if the SRS demands that Map A runs concurrently in the background while the player actively manipulates Map B, *and* Model B's interception proves fundamentally unsafe.

## 5. PlayerGlobal Interaction

Global temporal systems interact heavily with WarEconomy boundaries:
*   **`PlayerGlobalStateSegment`:** Contains Research progress, Ideology precepts, and global Tale generation limits. These must merge gracefully when an execution island boots.
*   **`FactionDomainState`:** Titles, Faction relations, and Quests. These must be decoupled from `TicksGame` and driven by Domain Authority.
*   **`SharedWorldProjection`:** World pawns and transit caravans. Operated by the Server; projected as read-only to the execution island.
*   **Reconstructible Context:** Weather managers, sky trackers, and transient `PlayLog` entries. These can drift globally and be discarded safely upon materialization fold.

## 6. Minimal-Interception Falsification Criteria

**Reject Model B (Forcing Model C) if:**
1.  Unpatchable static/global state causes catastrophic AI/Physics failures when two maps have diverging logical times.
2.  Crucial vanilla mechanics (like Hediffs or Biocoding) persistently use raw `Find.TickManager.TicksAbs` causing offline pawns to instantly die or lose state upon switching maps.
3.  High-adoption mods bypass `GenTicks` Harmony patches, universally corrupting the `ArtifactBaseStateRevision`.
4.  The `DELTA_BARRIER` cannot deterministically freeze a shared engine without a "catch-up burst" (where queued global ticks execute instantly on resume).

**Accept Model B (for Production) if:**
The desync only affects visual chronology (e.g., the year reads 5505 on one map and 5502 on another), but no material assets, pawn health, or `EntityId` stability is corrupted during save/load cycles.

## 7. Runtime Probe Plan (A/Sol)

To definitively answer G-Q1, execute the following battery:
1.  **Differential Ticking:** Load Map A and Map B. Tick Map A exactly 60,000 times (1 in-game day). Tick Map B 0 times.
2.  **State Audit:** Verify Map B pawn rest/hunger, plant growth, and hediff progression is exactly 0. Verify chronological age advancement.
3.  **Global Component Audit:** Inspect `QuestManager` and `GameComponents` for unhandled tick expiration.
4.  **Barrier Pause/Resume:** Execute a `DELTA_BARRIER` on the shared island. Verify NO catch-up burst occurs upon `RESUMING`.
5.  **Artifact Comparison:** Save Map B. Compare the XML against the baseline. Any unexpected delta identifies a leaked global getter.
6.  *(Comparison)* **Model C Baseline:** Run the exact same test using two separate RimWorld process instances. Compare the artifact deltas to isolate the cross-contamination caused by Model A/B.

*Decision-Changing Result:* If Step 5 reveals permanent pawn/asset corruption in Map B, Model A is dead, and Model B requires massive patching effort, tilting the architecture toward Model C.

## 8. Decision Matrix

| Requirement / Subsystem | Model A (Vanilla Shared) | Model B (Vanilla Patched) | Model C (Multi-Process) | Current Evidence | Missing Evidence | Release Consequence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Independent Pawn/Job Freeze** | Promising | Promising | Absolute | Map-local ticks freeze. | Hediff/Age behavior. | N/A (Baseline met) |
| **Global `TicksAbs` Isolation** | Fails | Virtualized | Absolute | `TicksAbs` advances globally. | Patchability of `Find.TickManager`. | Determines if B is viable over C. |
| **Execution Island Barrier** | Halts all maps | Halts all maps | Halts target map | Island-scoped barrier confirmed. | UX impact of halting background maps. | If unacceptable, forces C. |
| **Cross-Map XML Integrity** | High Risk | Medium Risk | Zero Risk | Not yet verified. | Artifact byte-comparison after differential ticking. | Primary falsification criterion. |
| **Mod Compatibility** | Low | Medium | High | Unknown. | Mod call-site instrumentation. | Limits supported modpack. |

## 9. End State

**Recommendation: Remain OPEN with a smaller decisive probe set.**

Keep the current hypothesis: **Vanilla Multi-Map First -> Minimal Interception -> Separate Island Only if Falsified.**

Current evidence proves that basic map-local pausing is feasible, but the full impact of global `TicksGame` progression on offline map assets (like Hediffs and chronological age) inside a shared execution island remains unproven. Master must await the results of the "Differential Ticking / Artifact Comparison" probe before permanently freezing the execution topology (G-Q1). 

This deferred decision does not block `PIPELINE_PROBE_CAS` or metadata foundations (ADR-001/Trade Config), which rely on Domain Authority, not Engine execution topology.