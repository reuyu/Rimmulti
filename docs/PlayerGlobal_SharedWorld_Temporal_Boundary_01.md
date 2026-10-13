# PlayerGlobal_SharedWorld_Temporal_Boundary_01.md

**Status:** DECISION / TRACEABILITY BRIEF — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Boundary Categories

To decouple RimWorld's monolithic execution context into independent, distributable domains, subsystems must be classified into the following canonical owners:
*   **MapSegment (`SettlementId`):** Strictly local physical artifacts (buildings, local pawns, items on the ground). Mutated by the `WriterLease` holder.
*   **PlayerGlobalStateSegment (`PlayerId`):** State owned by the player account that spans all their owned settlements.
*   **FactionDomainState (`FactionId`):** Political, diplomatic, and hierarchical state strictly governed by Server Domain rules.
*   **SharedWorldProjection (`WorldStateRevision`):** Context spanning all players/factions (e.g., active transit caravans, NPC bases).
*   **Domain-Authority-Only State:** State managed exclusively in the Server database that never originates from engine materialization.
*   **Engine-Reconstructible Context:** Ephemeral game state that is discarded upon save/disconnect and rebuilt on load without canonical persistence.
*   **Unresolved / Mixed:** Subsystems requiring targeted runtime probes to untangle.

## 2. Subsystems Classification

| Subsystem | Canonical Truth | Materialization Dependency | Read/Write Role | Time Source |
| :--- | :--- | :--- | :--- | :--- |
| **ResearchManager** | `PlayerGlobalStateSegment` | Yes (Required to load Map) | Engine Host (R/W) | Mixed/Local (driven by pawns) |
| **Ideology / Precepts** | `PlayerGlobalStateSegment` | Yes (Required to load Map) | Engine Host (R/W) | Mixed/Unresolved |
| **QuestManager** | Domain-Authority / SharedWorld | Yes (Read-only context) | Read-only Projection | Domain Clock |
| **WorldPawns** | `SharedWorldProjection` | Yes (Prevents reference crashes)| Read-only Projection | Domain Clock / Unresolved |
| **Tales / PlayLog** | Engine-Reconstructible | No (Discardable) | Reconstructible cache | `TicksGame` |
| **Storyteller / Incidents**| Engine-Reconstructible / Map | No (Re-rolled per session) | Reconstructible cache | `TicksGame` / Map-Local |
| **History (Stats)** | `PlayerGlobalStateSegment` | Yes (Wealth graphs) | Engine Host (R/W) | `TicksGame` |
| **Royalty / Titles** | `FactionDomainState` | Yes (Required for permit/UI) | Read-only Projection | Domain Clock |
| **Genes / Xenotypes** | `PlayerGlobalStateSegment` | Yes (Custom player genes) | Engine Host (R/W) | N/A (Static) |
| **Weather/Sky/Calendar**| Engine-Reconstructible | No (Visual only) | Reconstructible cache | `TicksGame` |
| **GameComponents** | Unresolved | Unknown | Unknown | Unknown |
| **Faction References** | `FactionDomainState` | Yes (Hard dependency) | Read-only Projection | N/A (Static attributes) |
| **Caravans/Transit** | `SharedWorldProjection` | Yes (Vision context) | Read-only Projection | Domain / TransitClock |
| **Map Conditions** | `MapSegment` | Yes (Map-local state) | Engine Host (R/W) | `LocalClockId` |
| **Global Def Caches** | Engine-Reconstructible | No | Reconstructible cache | N/A |

## 3. Stable Owner and Revision Binding

*   **`MapSegment`:** Owned by `SettlementId`. Revision: `ArtifactBaseStateRevision`. Mutated by the execution lease holder.
*   **`PlayerGlobalStateSegment`:** Owned by `PlayerId` (NEVER `PersonalFactionId`). Revision: `PlayerGlobalRevision`. Mutated by the execution lease holder. A frozen `MapSegment` **can and must** compose dynamically with a newer `PlayerGlobalRevision` upon materialization (e.g., if a player unlocked research while on another map).
*   **`FactionDomainState`:** Owned by `FactionId`. Revision: `FactionDomainRevision`. Mutated *exclusively* by Server Domain Authority. Engine Host may only consume it as a projection.
*   **`SharedWorldProjection`:** Owned by Server Global. Mutated exclusively by Server Domain. Engine Host consumes as read-only.

## 4. Temporal Semantics

*   **`LocalClockId` (Map-Local):** Drives Map Conditions, Pawn biology (hunger, rest), and Jobs. Must completely freeze when the map is unleased.
*   **`TicksGame` / `TicksAbs` (Global Engine):** Drives sky visuals, calendar, and historical stats. Global advancement while a Settlement is frozen is **allowed** (and reprojected upon materialization) *only* if it does not corrupt canonical material assets.
*   **Domain / World Clock:** Real-time UTC or server-ticked. Drives Quests, Tax deadlines, and Caravan transit. Advances regardless of map execution state.
*   **Mixed / Unresolved:** Hediff progression, chronological age, and ritual cooldowns. If global time advancement corrupts a frozen pawn's Hediff (e.g., fatal disease progresses instantly upon waking), it forces interception or `LocalClockId` virtualization.

## 5. Materialization Manifest

When the Server admits a candidate `.rws` fold, the `MaterializationManifest` must record:
*   **Hard Admission Binding:**
    *   `ArtifactBaseStateRevision` (Identifies the physical map delta).
    *   `PlayerGlobalRevision` (Identifies the exact research/ideology state embedded in this fold).
    *   `ContentProfileFingerprint` (Validates the def/mod schema used).
*   **Diagnostic Metadata (Not strictly required for admission fencing):**
    *   `FactionDomainRevision` snapshot.
    *   `SharedWorldProjection` snapshot.

## 6. Cross-Owner Atomicity

How operations spanning the `MapSegment` and Global/Domain state are transacted (ADR-004):
*   **Pawn Joins/Leaves Map:** Staged material result (Pawn leaves `MapSegment`) + Domain Commit (Pawn enters `TransitClockId` custody).
*   **Research Progress:** Staged material result + Domain Commit (Advances `PlayerGlobalRevision`).
*   **Ideology Role/Precept Change:** Staged material result + Domain Commit (Advances `PlayerGlobalRevision`).
*   **Quest Reward / Domain Event:** Staged material result + Domain Commit (Server deducts quest from Domain, Client stages spawned items in `.rws`).
*   **Royalty / Title Effects:** Eventual projection only. (Engine grants honor $\rightarrow$ Domain commits title update $\rightarrow$ Client eventually receives projected updated `FactionDomainState`).
*   *(Note: Ordinary single-scope material interactions like mining or crafting do NOT require a multi-scope `PREPARED` domain transaction; they remain purely within the `MapSegment` delta).*

## 7. Context Minimization (Pruned Target-Map Context)

During Engine Host materialization (or E-A PoC), the global context must be minimized:
*   **Proven Required:** `FactionManager` (requires at least the owner and active NPC factions), `TickManager` (base instantiation).
*   **Likely Required:** `ResearchManager`, `IdeoManager` (must be preserved from `PlayerGlobalStateSegment` to prevent null references during job execution).
*   **Reconstructible / Discardable:** `WeatherManager`, `TaleManager`, `PlayLog`, historical stat tracking graphs.
*   **Candidate Projection:** `WorldPawns`, `QuestManager`.

## 8. G-Q1 Linkage & Probe Plan

Certain subsystems will decisively dictate the final G-Q1 (Topology) outcome. If a subsystem relies heavily on `TicksAbs` and corrupts frozen material state, it forces either massive Harmony interception or isolated per-map processes (Model C).

**Prioritized Probe List (for A/Sol):**
1.  **Hediff Progression vs. `TicksAbs`:** Probe if pawn disease/immunity natively relies on global time. (If yes: G-Q1 decisive risk).
2.  **Chronological Age:** Probe if a frozen pawn magically ages 5 years if the engine `TicksGame` advances. (If yes: minor interception needed, not necessarily Model C).
3.  **WorldPawn GC Logic:** Probe if the engine aggressively garbage-collects `WorldPawns` if they haven't been ticked/interacted with on the active map. (If yes: requires Server projection overriding).
4.  **Ideology Ritual Cooldowns:** Probe if they expire based on `TicksGame`.

## 9. Acceptance Matrix

| Subsystem | Candidate Owner | Time Source | Materialization Dependency | Authority | Current Evidence | Missing Evidence | G-Q1 Consequence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Research** | `PlayerGlobal` | Mixed | Hard Dependency | Engine Host | Extracts safely | Cross-map merge safety | Low |
| **Ideology** | `PlayerGlobal` | Mixed | Hard Dependency | Engine Host | Extracts safely | Ritual timers | Medium |
| **Quests** | Domain Authority| Domain UTC| Read-Only Proj | Server | Fails if missing | Reprojection pipeline | Low (Domain handled) |
| **WorldPawns** | `SharedWorld` | Domain | Read-Only Proj | Server | GC crashes isolated maps | GC override safety | High |
| **Hediffs** | `MapSegment` | Unknown | Hard Dependency | Engine Host | Saved with Pawns | `TicksAbs` vs `LocalClock` | **High (May force Model C)** |
| **Age/Birthdays**| `MapSegment` | `TicksAbs`| Hard Dependency | Engine Host | Saved with Pawns | `TicksAbs` vs `LocalClock` | Medium (Patchable) |

## 10. Stop Line

The architecture must freeze the following minimal boundary logic **before** proceeding to Engine Host Production materialization, E-B PoC, or Genesis PoC:

1.  **Serialization Boundary:** The exact code-level mechanism to split the `.rws` save into a `MapSegment` blob and a `PlayerGlobalStateSegment` blob.
2.  **Manifest Revisioning:** The requirement that every valid checkpoint upload must carry both an `ArtifactBaseStateRevision` and a `PlayerGlobalRevision`.
3.  **Read-Only Projections:** The architectural commitment that Faction Tier/Titles and WorldPawns will be handled as read-only projections injected into the Engine Host, rather than simulated natively by the client.

*(The exhaustive field-level schema of `PlayerGlobalStateSegment` and the final G-Q1 topology remain OPEN pending the targeted temporal probes).*