# ADR-008_Shared_World_Layer_Transit_World_Projection.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the architecture boundary for the Shared World Layer. It establishes authority over caravans, world map movement, transit custody, vision-filtered projection, and the transition boundaries (ingress/egress) between the Shared World and Settlement Local Execution Islands. 

**Controlling Upstream Constraints:**
*   **ADR-001:** Dedicated Server owns final Domain Authority[cite: 22].
*   **ADR-003:** Canonical material state uses an artifact + committed operations + index[cite: 18]. Canonical `EntityId` is globally stable[cite: 18].
*   **ADR-006A:** WorldTick ($W$), Settlement LocalTick ($L_s$), and Engine Tick ($G$) are distinct[cite: 17]. Cross-domain movement preserves age and remaining-duration semantics[cite: 17].
*   **ADR-007:** Strict writer leases protect canonical publication[cite: 19].

## 2. Shared World Canonical State
The Dedicated Server holds the canonical representation of the world domain[cite: 20]. The server is *not* a full RimWorld World serializer; it stores only the data necessary for authority and routing.

**Canonical Server Representation:**
*   `WorldObjectId` / `CaravanId`: Server-issued, stable identity[cite: 14].
*   `FactionId`: The owning player's faction[cite: 14].
*   **Location & Pathing:** Current `Tile`, destination `Tile`, and movement progress (tied to $W$)[cite: 14, 17].
*   **Custody Graph:** A list of member `EntityIds` (Pawns, Animals) and aggregated carried `EntityIds` (Items)[cite: 14]. Nested inventories are maintained as opaque graphs bound to the root `EntityId` unless explicitly split[cite: 18].
*   **Visibility State:** Ambush/Scout status and faction visibility classifications[cite: 14].

*Distinction:* The server maintains the canonical *domain state* of a caravan. The detailed physiological graph (needs, rot, hediffs) remains serialized (as an extracted subgraph artifact) while in transit, bound to the `CaravanId`.

## 3. WorldObject / Caravan Authority
The Dedicated Server is the sole authoritative writer for world-layer location, routing, and existence[cite: 20].

*   **Creation & Destruction:** Server creates caravans upon egress from a settlement or retreat from a battle. Server destroys them upon ingress or starvation/extinction[cite: 14, 20].
*   **Movement & Routing:** Server controls movement progress based on $W$[cite: 14, 17]. 
*   **Split/Merge & Member Modification:** Server authorizes changes to the custody graph (e.g., merging two caravans, discarding items)[cite: 14, 20].
*   **Simulation Dependency:** *Decision Request (G-Q11).* Does the server blindly execute client-proposed routing/split operations, or does it require a server-controlled "World Engine" to calculate exact pathing costs, biome modifiers, and merge semantics?

## 4. Transit Residence & Clock Model
When Pawns/Items are removed from a Settlement ($L_s$) and placed into a Caravan, they enter transit. Raw $W$ cannot be directly applied to their internal timers (e.g., biological age, rot, hunger) because RimWorld physiological math expects native engine ticks, and a blanket rebase causes corruption (ADR-006A)[cite: 17].

**Candidate Models for Transit Physiology:**
1.  **Dedicated TransitClock (Server-Stepped):** The caravan maintains its own $L_c$ (Local Caravan Tick) which advances proportionally with $W$ only while the caravan is moving or resting. Physiology is updated via delta operations at the next materialization.
2.  **Settlement-Like LocalClock (Client Leased):** The caravan is treated like a mobile settlement. An online owner client receives a writer lease for the caravan and simulates its internal map/physiology[cite: 19]. *Risk:* Client controls ambush visibility and movement speed[cite: 14, 20].
3.  **World-Scheduled Delta (No Clock):** Internal physiological timers freeze upon egress. Upon ingress, the Server injects a "Transit Duration" delta into the receiving engine, which uses a custom RimWorld component to mathematically age the pawns and rot items by the elapsed time.

*Decision Request (G-Q12):* Master product policy is required to select the transit physiology model.

## 5. World Movement
World movement is driven by Dedicated Server $W$[cite: 14, 17].

*   **Progress:** Movement between tiles advances based on caravan movement speed multiplied by $\Delta W$[cite: 14, 17].
*   **Interruption:** Scout detection, Ambush triggers, or Server operator commands can interrupt movement[cite: 14].
*   **Server Restart:** Caravan progress is durably saved. Upon restart, progress resumes from the last committed $W$[cite: 17].
*   **Stale Clients:** Clients receive updated Tile coordinates via server projection. If a client lags, the server projection overwrites local visual positioning.

## 6. Vision-Filtered Projection
Clients must not receive hidden canonical data, preventing memory-reading cheats[cite: 14, 20].

*   **Projection:** The Server pushes a filtered `WorldObject` list to each client based on their Faction's `Vision Radius`, Alliances, and active Scout/Ambush states (FR-071 to FR-088)[cite: 14].
*   **Visibility Gain/Loss:** When an enemy caravan enters a client's vision range, the Server dynamically pushes the entity data. When it leaves, the Server sends a despawn/fog directive[cite: 14].
*   **Tactical Worker Projection:** Tactical Workers receive only the world projection necessary for the active battle (e.g., the target settlement and arriving caravans), avoiding massive memory bloat.
*   **Faction Registry:** The global Faction registry is projected entirely to ensure `FactionId` consistency[cite: 18].

## 7. Tactical Ingress / Egress
The boundary between the Shared World and a Local Execution Island utilizes the ADR-003 `MaterializationManifest` and ADR-007 barriers[cite: 18, 19].

*   **Ingress (Arrival):** A caravan arrives at a target settlement. The server triggers a `HANDOFF_BARRIER` (ADR-007)[cite: 19]. The caravan's canonical artifact subgraph is extracted, and its `EntityIds` are added to the target's `MaterializationManifest` as an explicit ingress operation[cite: 18]. The caravan is destroyed on the world layer.
*   **Egress (Departure/Retreat):** Pawns leaving a map (e.g., retreating attackers FR-161, exiting caravans) are published as explicit egress operations in the `CommittedOperationLog`[cite: 14, 18]. The Server intercepts these, removes them from the settlement's canonical index, packages their artifact subgraph, and spawns a new `CaravanId` on the World layer[cite: 18].
*   **Reprojection:** Absolute anchors (e.g., birth dates) are reprojected from the source clock to the destination clock during ingress/egress to prevent catch-up debt (ADR-006A)[cite: 17].

## 8. Tax & Economy World Interaction
*   **Physical Tax Caravan:** Tax collection requires a physical caravan arrival (FR-183)[cite: 14].
*   **Offline Owner:** If the target is offline, the Server executes a `DELTA_BARRIER` against the offline settlement's index (ADR-003) to perform the tax/trade transfer without an engine[cite: 18, 19].
*   **Online / Tactical Conflict:** If the target is online, a `DELTA_BARRIER` forces the owner client to apply the transaction[cite: 19]. If the settlement is currently in a Tactical Session, the collector's operation is queued (ADR-003 PendingOperationQueue) and the collector visually waits on the world map[cite: 18].

## 9. World-Layer Content / Mod Boundary
Approved mods may add `WorldComponents`, incidents, or custom `WorldObjects`[cite: 15].
*   **Boundary:** The Server must not crash or fail-closed at runtime due to unclassified mod world-data.
*   **Manifest Link:** ADR-006B (Content Manifest) must enforce that any mod interacting with the World Layer is statically analyzed. Unknown world-layer code is stripped or execution is blocked *at approval time*, ensuring offline attacks (FR-153) are never prevented by an unrecognized world component[cite: 14, 15].

---

## 10. Explicit Questions to Reconcile / Contract Matrix

### Decision Table

| Question | Status / Classification | Action Required |
| :--- | :--- | :--- |
| **1. Who simulates caravan pathing?** | Product-policy decision required (G-Q11) | Decide if Server needs a headless RimWorld instance to validate path costs, or if client proposals are blindly trusted. |
| **2. Who simulates transit physiology?** | Product-policy decision required (G-Q12) | Select a transit model (Dedicated Clock, Client Leased, or World-Scheduled Delta). |
| **3. What is the residence clock of a Pawn in transit?** | Deferred to G-Q12 decision | Depends on transit physiology model. |
| **4. Does transit continue when all players are offline?** | Fixed by SRS (FR-001) / ADR-006A | Yes. World Time $W$ continues. |
| **5. What happens during Server process downtime?** | Fixed by ADR-006A (§8) | $\Delta W = 0$. Resume from committed $W$. |
| **6. How are world-hidden entities projected?** | Architecture decision made | Server-side vision filtering. Client only receives visible `WorldObjects`. |
| **7. Can one caravan participate in >1 execution island?** | Fixed by ADR-003/007 | No. One writer lease per material scope. |
| **8. Caravan crosses into Tactical while targeted?** | Fixed by ADR-003 | World operation is queued in `PendingOperationQueue`. |
| **9. How are attacker/retreat revisions fenced?** | Architecture decision made | Processed via `HANDOFF_BARRIER` and `CommittedOperationLog`. |
| **10. TBD-02 forced-expulsion destination?** | TBD | Do not resolve here. |

### Contract Matrix

| State/Field | Owner | Authoritative Writer | Projection Readers | Revision/Fencing | Clock Domain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WorldObjectId` / `CaravanId` | Server | Server | All visible clients | WorldRevision | $W$ |
| Caravan Location/Path | Server | Server | Vision-authorized clients | WorldRevision | $W$ |
| Transit Physiology (Needs/Rot) | Server (Opaque) | Deferred (G-Q12) | None (Opaque in transit) | SaveRevision | Deferred (G-Q12) |
| Faction Vision/Fog | Server | Server | Faction Members/Allies | WorldRevision | $W$ |
| Ingress/Egress Manifest | Server | Server / Target Writer | Receiving Engine | SettlementStateRevision | $W \rightarrow L_s$ |

## 11. Acceptance Readiness
*   **Decisions safe for Master acceptance now:** Vision-filtered projection, Server authority over routing/location, Ingress/Egress via MaterializationManifest, Tax caravan queueing.
*   **Open Master/product-policy questions:** G-Q11 (Pathing Simulation Authority), G-Q12 (Transit Physiology Model).
*   **Runtime proof obligations:** Proving a client can dynamically spawn/despawn `WorldObjects` based on server vision directives without breaking local UI references.
*   **Downstream dependencies:** ADR-006B (Content Manifest for mod world components), ADR-004 (Durable compensation for failed ingress/egress transactions).