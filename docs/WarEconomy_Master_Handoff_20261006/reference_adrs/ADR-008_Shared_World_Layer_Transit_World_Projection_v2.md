# ADR-008_Shared_World_Layer_Transit_World_Projection_v2.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the architecture boundary for the Shared World Layer, covering caravans, world objects, transit custody, temporal semantics, and vision-filtered projections. It integrates strictly with the established upstream contracts:
*   **ADR-001:** Dedicated Server retains final Domain Authority[cite: 16].
*   **ADR-003:** Canonical material state relies on immutable artifacts, committed operations, and stable cross-process `EntityId` mapping[cite: 18].
*   **ADR-006A:** WorldTick ($W$), Settlement LocalTick ($L_s$), Engine Tick ($G$), and host monotonic time ($M$) are strictly distinct[cite: 17]. 
*   **ADR-007:** Execution is bound by strict writer leases, fencing, and barriers[cite: 19].

The Dedicated Server owns the canonical Shared World state; client and Worker WorldObjects are projections and materializations, not the final authority.

## 2. Shared World Canonical State & Fencing
The Dedicated Server maintains canonical representations for the world layer without becoming a full RimWorld serializer.

**Revisions & Fencing:**
*   **`WorldStateRevision`:** A global revision for world-level domain states and timelines.
*   **`WorldObjectRevision` (Custody Revision):** A per-object or per-custody-graph revision. To avoid bottlenecking all independent world updates on a single global revision lock, individual caravans and world objects maintain their own `WorldObjectRevision`.
*   **Stale Operation Rejection:** Any operation targeting a `WorldObject` must provide the expected `WorldObjectRevision`. If the revision has advanced, the operation is rejected or requires re-evaluation.
*   **Split/Merge Ordering:** Caravan splitting or merging operations must strictly reference the current `WorldObjectRevision` of the involved entities to ensure transactional ordering and prevent item duplication or loss.
*   **Restart Durability:** All canonical `WorldObject` identities, pathing progress, and custody graphs must be durably committed so that world state restores exactly upon Server restart[cite: 16, 17].

## 3. WorldObject / Caravan Movement Authority
An untrusted client pathing or routing result is **never** authoritative. 

*   **Client Proposal:** A client may submit a destination or pathing intent only.
*   **Movement Execution:** Pathing and movement costs must be determined by server-controlled executors. Valid candidates include:
    *   A deterministic server-side implementation of supported RimWorld movement math.
    *   A server-controlled RimWorld/world engine that computes path and movement facts, which the Server then validates and commits.
*   **Zero-Player Movement:** World movement is driven directly from the Server's $W$ state. As long as the Dedicated Server is running, $W$ advances and caravan movement continues along committed paths, even if zero players are online (FR-001)[cite: 14, 17].

## 4. Transit Residence & Clock Model
Under ADR-006A, transit physiology requires an explicit clock domain. Raw $W$ is **not** equal to the physiological transit tick, and using raw $W$ to directly step physiological timers (e.g., hunger, rot) is prohibited[cite: 17].

*   **`TransitClockId` & Transit Tick:** Every caravan or transit group is assigned a `TransitClockId`. The transit tick represents the local physiological coordinate of the entities in that group.
*   **Relation to $W$:** The advancement of the transit tick is a function of $W$ (e.g., advancing while the caravan is traveling or resting), but the two domains remain structurally distinct.
*   **Zero-Player Physiology:** While world *movement* always follows $W$, transit *physiology* advancement with zero players online depends entirely on how the `TransitClock` policy is executed. It must not be directly inferred from $W$.
*   **Reprojection Rules:** When Pawns/Items move between a Settlement ($L_s$) and a Caravan (`TransitClockId`), native absolute anchors (e.g., birth dates, rot timers) must be explicitly reprojected to the destination clock domain during ingress/egress to prevent catch-up debt[cite: 17].

**Decision Request (G-Q12):** How is the mandatory `TransitClock` physiology executed/materialized?
Candidate executors include:
*   A continuous server-controlled transit worker.
*   Bounded/batched server-controlled engine materializations (calculating accrued physiological deltas only when required).
*   Another server-controlled validated mechanism.

## 5. Vision-Filtered Projection & Faction Registry
Clients only receive projections of the world state authorized by their visibility rules.

*   **Vision Filtering:** The Dedicated Server projects `WorldObjects` to a client based on faction ownership, alliances, territory, scouts, and ambush detection (FR-071 to FR-088)[cite: 14]. Hidden `WorldObjects` or intelligence state must remain strictly filtered and are never sent to unauthorized clients.
*   **Faction Registry Projection:** To prevent `FactionId` collisions and ensure consistent relationship rendering, the stable Faction registry identity is globally projected to all clients and Workers[cite: 18]. However, this global projection applies *only* to identity and political state, not to the hidden locations of a faction's caravans or secret world objects.
*   **Stale Projection Removal:** When a caravan leaves visibility (or uses Ambush), the server actively issues despawn/fog directives to prune the client's projection[cite: 14].

## 6. Tactical Ingress & Egress (Custody Transfer)
Movement between the Shared World and a Settlement Local Execution Island is a strict custody transfer, **not** an immediate destroy/create pattern. 

*   **Custody Transfer States:** Transitions utilize conceptual states such as `PREPARED`, `INGRESS_PENDING`, and `EGRESS_PENDING`. (Exact transaction, outbox, and repair algorithms are deferred to ADR-004).
*   **One Canonical Owner Invariant:** At any canonical commit boundary, an `EntityId` graph has exactly *one* authoritative custody owner (either a `CaravanId` on the World layer or a `SettlementId` on the Local layer).
*   **Concurrent Operations:** If a concurrent world operation (e.g., a world-event or another caravan merging) targets a Caravan while it is in the `INGRESS_PENDING` or `EGRESS_PENDING` state, the operation must be fenced and serialized in the Shared World custody domain *before* the Settlement's `PendingOperationQueue` is relevant[cite: 18].

## 7. Tax / Economy World Interaction
*   **Physical Arrival:** Tax caravans must physically arrive at a settlement for collection[cite: 14].
*   **Offline / Server-Side Commits:** If the durable projection/index contains sufficient facts to safely execute a typed canonical operation (e.g., transferring a known fungible item quantity), the Server may execute a server-only typed commit without an engine[cite: 18].
*   **Engine Semantic Requirement:** If the operation requires RimWorld semantic state hidden inside the artifact (e.g., calculating the precise quality/value of apparel for tax substitution), a server-controlled engine/materialization must be utilized before committing through ADR-003/ADR-004 pathways.
*   *Note:* TBD-05 (partial tax collection timestamp semantics) remains explicitly unresolved[cite: 14, 22].

## 8. World-Layer Content / Mod Boundary
Mods interacting with the Shared World Layer (e.g., custom `WorldComponents`, `WorldObjects`, incidents) must not compromise the integrity of the world simulation or disable lawful offline attacks.

*   **Approval-Time Classification:** Under ADR-006B, all content must be classified against a pinned content profile at approval/migration time[cite: 19].
*   **Disposition:** Unsupported or unclassified world components are explicitly rejected or quarantined prior to live admission. We do *not* claim that unknown executing engine code can simply be "stripped" safely at runtime.

---

## 9. Required Decision Table

| Item | Classification | Action/Note |
| :--- | :--- | :--- |
| **Pathing & Movement Authority** | Fixed by Accepted ADR/SRS | Server-controlled executor; client submits intent only. |
| **Transit Clock Mandate** | Fixed by Accepted ADR/SRS | Distinct `TransitClockId` required; $W \neq TransitTick$[cite: 17]. |
| **Transit Physiology Execution (G-Q12)** | Product-policy decision required | Choose continuous transit worker, batched engine materialization, or alternative validated execution. |
| **World Movement w/ 0 Players** | Fixed by Accepted ADR/SRS | Continues following $W$ while Dedicated Server runs (FR-001)[cite: 14, 17]. |
| **Transit Physiology w/ 0 Players** | Deferred to G-Q12 | Depends on the selected transit physiology materialization executor. |
| **Vision-Filtered Projection** | Fixed by Accepted ADR/SRS | Server strips hidden data before projection[cite: 14]. Faction registry projected globally[cite: 18]. |
| **Ingress/Egress Custody Transfer** | Architecture decision Master can make now | Adoption of `PREPARED`/`PENDING` states ensuring 1 canonical owner per `EntityId` graph. |
| **Concurrent Ops during Ingress** | Architecture decision Master can make now | Serialized in World Domain *before* Settlement `PendingOperationQueue`. |
| **Mod/Content World Component Policy** | Deferred to ADR-006B | Approval-time classification and quarantine[cite: 19]. |
| **Exact TX/Repair for Custody Transfer** | Deferred to ADR-004 | Detailed atomic commit, outbox, and compensation logic. |

---

## 10. Required Contract Matrix

| Field / State | Canonical Owner | Authoritative Writer | Readers / Projections | Revision / Fence | Clock Domain |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `WorldObjectId` / `CaravanId` | Dedicated Server | Server | Visible clients | `WorldObjectRevision` | $W$ |
| `WorldStateRevision` | Dedicated Server | Server | All connected clients | N/A (Root Fence) | $W$ |
| `WorldObjectRevision` (Custody) | Dedicated Server | Server | Visible clients | `WorldObjectRevision` | $W$ |
| `TransitClockId` | Dedicated Server | Server | None (Internal) | `WorldObjectRevision` | $W$ |
| Tile / Path Progress | Dedicated Server | Server Path Executor | Vision-authorized clients | `WorldObjectRevision` | $W$ |
| Membership / Custody Graph | Dedicated Server | Server | Vision-authorized clients | `WorldObjectRevision` | `TransitClockId` |
| Visibility State (Scout/Ambush) | Dedicated Server | Server | Faction/Alliance only | `WorldObjectRevision` | $W$ |
| Ingress/Egress Transfer State | Dedicated Server | Server / Target Writer | Receiving Engine | `SettlementStateRevision` / `WorldObjectRevision` | $W \leftrightarrow L_s$ |

---

## 11. End State

*   **Acceptance Readiness:** The Server Domain Authority over WorldObjects, the vision-filtering rules, the segregation of $W$ from `TransitTick`, the custody transfer states (`PREPARED`/`PENDING`), and the concurrent operation serialization order are architecturally sound and ready for Master acceptance.
*   **Remaining Decision Requests:** G-Q12 (Transit Physiology Execution mechanism).
*   **Runtime Proof Obligations:** Proving server-controlled pathing executors match client-expected logic without granting the client authority. Proving absolute anchor reprojection during ingress/egress custody transfers works without corrupting physiological timers.
*   **Contradictions:** No contradictions exist with ADR-001, ADR-003, ADR-006A, or ADR-007. The boundaries between World, Settlement, and Lease are strictly maintained.