# Player_Global_State_Boundary_Decision_Brief_01.md

**Status:** DECISION BRIEF — DO NOT RESOLVE FINAL PRODUCT POLICY
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Canonical Requirement & Lifecycle Trace
The RimWorld engine natively stores vast amounts of data in global `World` and `Game` components. However, under WarEconomy's decoupled architecture, a player may own multiple settlements[cite: 1], and these settlements operate on independent `LocalClockId` timelines ($L_s$)[cite: 7]. This section traces how lifecycle events interact with state that exceeds a single `SettlementId`.

*   **New Player / Personal Tribe Creation:** A new player automatically receives a personal Faction (Tribe)[cite: 1]. Vanilla RimWorld binds Research, Ideology, and Faction identity globally.
*   **Multiple Owned Settlements:** The player can own multiple settlements up to their Title limit (FR-034)[cite: 1]. If Research is stored globally, simulating Settlement A while Settlement B is offline (frozen $L_s$) forces a decision on whether Settlement B instantly inherits the research upon waking, or if research is bound per-map.
*   **Faction Join & Personal Faction Dissolution:** When joining a higher-tier Faction, the player's personal faction dissolves, and their settlements transfer (FR-026, FR-028, FR-029)[cite: 1].
*   **Expulsion / New Faction Creation:** If expelled (or titles revoked), a new personal faction is generated and the player's settlements are transferred (FR-044, FR-045, FR-046)[cite: 1].
*   **Branch Split:** If a King's branch collapses, surviving branches become independent Factions (FR-174 to FR-178)[cite: 1].
*   **Tactical Materialization of One Settlement:** A Tactical Worker must materialize only the target settlement and necessary global context without mutating the rest of the world (ADR-006A, B2-lite)[cite: 7, 10, 11].
*   **Caravan / Transit Custody:** Exists in the Shared World Layer under a distinct `TransitClockId` (ADR-008)[cite: 2].
*   **Research / Ideology / Royalty / Quests:** These are historically engine-global. Modifying them in one active settlement creates temporal paradoxes for offline settlements owned by the same player.
*   **Offline Settlement Materialization:** A frozen settlement may be subject to offline Typed operations (e.g., Tax) which must not corrupt or require full global state (ADR-004)[cite: 6, 7].

## 2. Candidate State Ownership Taxonomy

### 2.1 MapSegment (`SettlementId`)
*   **Source-of-truth Authority:** Dedicated Server (via Artifact fold)[cite: 5].
*   **Revision Owner:** `ArtifactBaseStateRevision` / `CommittedSettlementStateRevision`[cite: 5].
*   **Reader / Writer Roles:** Leased Client or Tactical Worker (Writer)[cite: 9], Server (Validator/Archiver)[cite: 5].
*   **Mutation:** Mutated by ordinary owner client or Tactical Worker under an active lease[cite: 9].
*   **Composition:** Contains purely local things (Pawns, Buildings, localized zones).

### 2.2 PlayerGlobalStateSegment (`PlayerId` or `PersonalFactionId`)
*   **Source-of-truth Authority:** Dedicated Server.
*   **Revision Owner:** `PlayerGlobalRevision`.
*   **Reader / Writer Roles:** Engine Host / Leased Client.
*   **Mutation:** Written by the active settlement's client. 
*   **Cross-segment issues:** If Player owns Map A (Active) and Map B (Frozen), modifying this segment in Map A must safely propagate to Map B upon Map B's resumption without advancing Map B's $L_s$[cite: 7].

### 2.3 FactionDomainState (`FactionId`)
*   **Source-of-truth Authority:** Dedicated Server Database[cite: 3].
*   **Revision Owner:** `DiplomacyRevision` / `FactionStateRevision`.
*   **Reader / Writer Roles:** Dedicated Server (Writer). Engine Host (Reader/Projected)[cite: 3].
*   **Mutation:** **Never** mutated by ordinary clients or Tactical Workers. They may only propose intents[cite: 3, 4]. Includes Tier, Titles, War/Alliance states[cite: 1].
*   **Merge Behavior:** Projected into the engine at load time to satisfy native RimWorld `FactionManager` requirements.

### 2.4 SharedWorldProjection
*   **Source-of-truth Authority:** Dedicated Server Database[cite: 2].
*   **Revision Owner:** `WorldStateRevision` / `WorldObjectRevision`[cite: 2].
*   **Reader / Writer Roles:** Dedicated Server (Writer). Clients/Workers (Readers).
*   **Composition:** Caravans, NPC settlements, active quests[cite: 2]. Pushed to the Engine Host strictly for vision-filtered context[cite: 2].

### 2.5 Engine-Ephemeral / Reconstructible
*   **Source-of-truth Authority:** None (Discarded).
*   **Examples:** Most of `TaleManager`, `PlayLog`, local `WorldPawns` not currently crossing boundaries.
*   **Mutation:** The engine will generate these natively. They must **not** be saved canonically to avoid bloat and cross-map contamination.

## 3. Cross-Segment Reference Hazards
*   **WorldPawns:** Vanilla RimWorld heavily relies on `WorldPawns` for relationships. If Map A creates a relationship with a pawn that is subsequently saved globally, Map B's engine might crash if that pawn is missing from its isolated projection.
*   **Faction References:** Items and Pawns hold hard references to `Faction`. If a player's `PersonalFactionId` dissolves during a Faction Join[cite: 1], all serialized references in all offline `.rws` artifacts owned by that player become invalid unless explicitly migrated.
*   **Temporal Leakage:** If `PlayerGlobalStateSegment` records timestamps (e.g., "Quest accepted at Tick X"), injecting this segment into a map with a different $L_s$ coordinate will cause immediate expiration or logical failure[cite: 7].

## 4. Join / Expulsion / Split Unresolved Product Questions
*   **Faction Join:** When a player joins a City-State, do their settlements permanently adopt the City-State's Research and Ideology, or do they maintain their personal tech tree? If they inherit it, is their previous progress destroyed or suspended?
*   **Expulsion / Split:** When a player is expelled (FR-044) or a branch splits (FR-174)[cite: 1], what global state does the newly generated Faction inherit? Do they clone the parent Faction's research, or revert to their pre-join state?
*   **Shared Global Segments:** Can two Settlements owned by the same player safely share a single `PlayerGlobalStateSegment` in memory if they possess different `LocalClockIds` (ADR-006A), or does this violate engine assumptions?

## 5. Minimum Architecture Invariants
1.  **Domain Isolation:** Political state (Titles, Diplomacy, Faction Tiers, Betrayer status) remains the exclusive domain of the Dedicated Server (ADR-001)[cite: 3]. It must be injected into the Engine Host as a read-only projection.
2.  **Clock Independence:** Global components must not force a synchronization of `LocalClockId` ($L_s$) across multiple settlements (ADR-006A)[cite: 7].
3.  **Artifact Immutability:** Offline settlements cannot have their physical artifacts updated simply because a player's global state changed. The global state must be merged dynamically at load time (ADR-003)[cite: 5].

## 6. E-A Runtime Evidence Checklist
Dev A and Sol must empirically discover the following in RimWorld 1.6 during the Engine Host PoC:
*   [ ] **ResearchManager Isolation:** Can `ResearchManager` be extracted, serialized, and injected into a fresh Engine instance without crashing due to missing `World` references?
*   [ ] **IdeoManager Dependencies:** Does `IdeoManager` hold hard references to `WorldObjects` or specific `Pawns` that would fail validation in an isolated Settlement map?
*   [ ] **Royalty / Titles:** Do Royal Titles attached to a `Pawn` safely persist if the overarching `Faction` definition is dynamically projected at load time?
*   [ ] **WorldPawns Purge:** Can an Engine Host map load and simulate cleanly if `WorldPawns` is violently purged of all pawns not actively present on the loaded Map or in declared relations?
*   [ ] **GameComponent Clock Reliance:** Which vanilla `GameComponents` (e.g., QuestManager, TaleManager) rely on raw `TicksGame` ($G$) versus localized ticks, and do they corrupt when $G$ differs from their last serialized state[cite: 7]?

## 7. Decisions Safe to Defer
*   **Product Policy on Inheritance:** Whether research/ideology is cloned, wiped, or suspended upon Faction Join/Split (TBD-01, etc.) can be deferred. The architecture only needs to know *where* to store it, not the business logic of how to mutate it during a join.
*   **Royalty Permit Cooldowns:** The exact temporal mechanics of permit cooldowns across divergent $L_s$ timelines can be stubbed or ignored for the initial PoC.

## 8. Freeze Point
The physical separation and schema format of the `MapSegment` versus the `PlayerGlobalStateSegment` must be frozen **before Dev A authors the final Genesis Production logic (the code that builds the initial artifact from a starting scenario)** and before the final `MaterializationManifest` builder is approved (ADR-003)[cite: 5]. Without this freeze, the Engine Host cannot reliably extract or inject state.