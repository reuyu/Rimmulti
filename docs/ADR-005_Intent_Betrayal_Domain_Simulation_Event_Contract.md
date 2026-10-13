# ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the architecture contract for intent-aware betrayal, evaluating aggressive actions, and synchronizing mid-session Domain $\leftrightarrow$ Simulation events. The Dedicated Server must strictly differentiate between lawful hostile action, accidental collateral damage, explicit aggressive intent, and autonomous AI behavior. 

This architecture integrates with accepted upstream constraints:
*   **ADR-001 & ADR-002:** The Dedicated Server holds final Domain Authority (political states, alliances, betrayal). The Tactical Worker holds Simulation Authority (calculating AI, projectiles, damage) but cannot unilaterally declare betrayal or political changes[cite: 26, 27].
*   **ADR-003 & ADR-004:** Operations use stable `EntityId` mapping, monotonic revisions, and durable transaction/idempotency rules[cite: 28, 29].
*   **ADR-006A:** Temporal domains ($W$ vs $L_s$) govern timers such as WarPending and Betrayer durations[cite: 30].
*   **ADR-007:** Leased writers execute bounded simulation logic and are subject to fencing barriers[cite: 32].

## 2. Required Distinctions
To prevent unilateral client or Worker political declarations, the architecture separates the event lifecycle into distinct conceptual layers:

*   **`PlayerIntent` / `CommandIntent`:** A client-proposed operation (e.g., "Drafted Pawn A attacks Entity B"). It is untrusted until validated by the Server/Worker.
*   **`AuthorizedAction`:** A validated intent that the Worker is permitted to execute within its simulation lease.
*   **`SimulationFact`:** An objective observation produced by the Worker (e.g., "Pawn A fired a weapon toward Coordinate X").
*   **`DamageFact` / `OutcomeFact`:** An objective consequence produced by the Worker (e.g., "Pawn C received 10 damage from Projectile P").
*   **`DomainEventCandidate`:** The Server's aggregation of `PlayerIntent`, `SimulationFact`, and `DamageFact` correlated via an `OperationId`.
*   **`BetrayalDecision`:** A Dedicated Server canonical commit determining that a `DomainEventCandidate` violates diplomacy rules, generating a political consequence (FR-120, FR-122)[cite: 24].
*   **`RelationshipTransition`:** The durably committed political state change (e.g., Faction X is now Hostile to Faction Y, and Faction X gains the `Betrayer` status)[cite: 24].

## 3. Intent Provenance & Authentication
Intent cannot be derived solely from "who took damage." A client's claim that an attack was an "accident" is not authoritative. Intent is captured, authenticated, and bound using strict provenance metadata:
*   **Session & Principal:** Bound to the authenticated `SessionEpoch` and `PlayerId`[cite: 26].
*   **Idempotency Key:** Bound to a unique `OperationId` generated at intent creation[cite: 29].
*   **Target Identifiers:** Must reference canonical `EntityId` and `FactionId`, never volatile client memory pointers or native `loadID`s[cite: 28].
*   **Execution Context:** Bound to the active `WriterLeaseId`, `TacticalSessionId` (Worker Generation), and current `DiplomacyRevision`.
*   **Temporal Coordinate:** Bound to the exact `WorldTick` ($W$) and `LocalTick` ($L_s$) at the time the intent was authorized[cite: 30].

## 4. Worker Event Contract
The Tactical Worker executes physical mechanics but is strictly prohibited from mutating domain logic.
*   **Permitted Reports:** The Worker may report that an attack was executed (`SimulationFact`), the source/target of a projectile, area-effect collateral (`DamageFact`), target identity (`EntityId`), and the `OperationId` that initiated the action.
*   **Prohibited Commits:** The Worker **must not** directly commit `Betrayer` status, break alliances, declare war, assign political penalties, or unilaterally flip Faction manager hostility flags across the world[cite: 24, 27].

## 5. Server Decision Pipeline
The lifecycle of an intent-aware domain event follows a strict Server $\rightarrow$ Worker $\rightarrow$ Server pipeline:
1.  **Authenticated Intent:** Client submits `PlayerIntent` to the Server/Worker boundary. An `OperationId` is generated.
2.  **Authorization:** Server validates that the actor owns the Pawn and holds a valid `WriterLeaseId`.
3.  **Simulation & Correlation:** Worker simulates the action. It emits `SimulationFact`s and `DamageFact`s, tagged with the `OperationId`.
4.  **Rule Evaluation:** The Server matches the facts to the `OperationId`. It evaluates the canonical `DiplomacyRevision` at the time of intent. If the target was allied/neutral and the intent was explicitly hostile, a `BetrayalDecision` is formulated.
5.  **Durable Domain Operation:** The Server executes an ADR-004 `COMMITTED` transaction, advancing the `DiplomacyRevision` and updating Faction standings (FR-121, FR-125)[cite: 24, 29].
6.  **Projection:** The Server projects the new `RelationshipTransition` (e.g., Hostile flag, Betrayer status) back to all active Tactical Sessions and connected clients[cite: 27].

## 6. Accidental & Indirect Effects
The Server evaluates `DomainEventCandidate`s against explicit product policies to determine if an action constitutes a betrayal. 
*   **Friendly Fire / AOE:** If `PlayerIntent` targeted a legitimate enemy, but the resulting `DamageFact` hit a neutral/ally, the Server may classify this as an accident (FR-131, FR-132)[cite: 24]. *(Fallback: If intent-based AOE calculation is computationally prohibitive, CON-001 permits an explicit fallback exempting all AOE from betrayal logic)*[cite: 24].
*   **Traps / Turrets:** These generate `DamageFact`s without a live `PlayerIntent`. Provenance is tied to the owner of the structure.
*   **Mental Breaks / Berserk:** Generates a `SimulationFact` driven by AI, explicitly marked with a `MentalState` flag. 
*   **Offline Attacker / AI:** Autonomous combat (e.g., an offline lawful attack, FR-153) evaluates under the initial domain authorization of the attack. AI-driven targeting errors during a lawful attack do not generate new betrayals[cite: 24].
*   **Stale Orders:** If an alliance forms while a projectile is mid-air, the Server evaluates the `DiplomacyRevision` *at the time the intent was authorized*, protecting players from retroactive betrayal.

*Note: Specific punishments for traps, turrets, or mental breaks hitting allies are deferred to Master Product-Policy Decisions (see Section 10).*

## 7. Mid-Session Domain Changes
Tactical Sessions are dynamic. If the Server commits a `BetrayalDecision` or `WarDeclaration` (FR-101, FR-115), the active session must react without the Worker becoming the domain authority[cite: 24, 27].
*   **Event Push:** The Server durably commits the `RelationshipTransition` and increments the `DiplomacyRevision`. It pushes this revisioned event into the Worker's `PendingOperationQueue` / `MaterializationManifest`[cite: 28].
*   **Worker Update:** The Worker consumes the event and updates its local, projected `FactionManager` (e.g., flipping Peaceful to Hostile) enforcing forced 1x speed and disabling pause (FR-103, FR-104)[cite: 24].
*   **Fencing:** The Server rejects any new `PlayerIntent` that references an outdated `DiplomacyRevision` if that intent relies on an obsolete peaceful state.

## 8. Required Matrices

### Event Authority Matrix
| Event / Fact | Producer | Validator | Canonical Owner | Idempotency / Revision Key | Consumers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PlayerIntent` | Owner Client | Server / Worker | Server | `OperationId` / `FencingGeneration` | Worker (Simulation) |
| `SimulationFact` | Tactical Worker | Server | Server | `OperationId` | Server (Rule Eval) |
| `DamageFact` | Tactical Worker | Server | Server | `OperationId` / `EntityId` | Server (Rule Eval) |
| `BetrayalDecision` | Dedicated Server | Dedicated Server | Dedicated Server | `DiplomacyRevision` | Database, Outbox |
| `RelationshipTransition`| Dedicated Server | Dedicated Server | Dedicated Server | `DiplomacyRevision` | All Clients, Active Workers |

### Betrayal Decision Input Matrix
| Candidate Input | Trusted Source | Sufficient Alone? | Required Correlation | Policy-Dependent Fields |
| :--- | :--- | :--- | :--- | :--- |
| **Direct Targeted Attack** | `PlayerIntent` + `DamageFact` | Yes | `OperationId` | Target Faction, Current Diplomacy |
| **Explosive / AOE** | `DamageFact` | No | Intent Target vs Hit Entity | Fallback policy (CON-001) |
| **Trap / Turret Damage** | `DamageFact` | No | Structure Ownership Identity | Autonomous liability rules |
| **Theft / Item Interaction** | `SimulationFact` | No | Settlement Owner `FactionId` | Exact trigger timing (TBD-03) |
| **Mental Break Attack** | `DamageFact` | No | AI State Flag (`MentalStateDef`) | Mental break liability rules |

### Failure / Race Matrix
| Scenario | Resolution / Outcome |
| :--- | :--- |
| **Duplicate Intent** | Server/Worker deduplicates via `OperationId` matching. Idempotent reject. |
| **Duplicate Worker Fact** | Server ignores facts with an already processed `OperationId`. |
| **Worker Crash (Post-Hit, Pre-Report)**| Facts lost. Transaction is `ABORTED` or rolled back per ADR-004. Domain state remains unchanged. |
| **Diplomacy Change between Intent and Hit** | Evaluated against the `DiplomacyRevision` bound to the original `PlayerIntent`. No retroactive betrayal. |
| **Reconnect / Replay** | Replayed intents rejected via `FencingGeneration` and `OperationId`[cite: 19, 29]. |
| **Domain Decision Committed, Worker Update Delayed** | Worker continues simulating under old projection briefly, but Server restricts/fences any domain commits contradicting the new `DiplomacyRevision`. |

---

## 9. Acceptance Readiness

**Safe E0 Architecture Decisions (Master can accept now):**
*   Strict separation of `PlayerIntent`, `SimulationFact`, and `BetrayalDecision`.
*   Dedicated Server domain pipeline (Intent $\rightarrow$ Execution $\rightarrow$ Evaluation $\rightarrow$ Commit).
*   Prohibition of Tactical Workers unilaterally mutating Faction Manager hostility/betrayer status.
*   Binding of intents to `DiplomacyRevision` to prevent retroactive betrayal during mid-air projectiles.
*   Mid-session domain updates pushed via revisioned operations rather than Worker-internal logic.

**Product-Policy Decision Requests (Explicitly OPEN):**
*   **G-Q13:** Are Trap/Turret autonomous hits against allies considered Betrayal?
*   **G-Q14:** Are Mental Break attacks against allies considered Betrayal, or exempt due to lack of player control?
*   **TBD-03:** Exact theft trigger timing (Is it Betrayal upon picking up the item, changing ownership, or exiting the map?)[cite: 24].
*   **G-Q15:** Should the project utilize the CON-001 AOE fallback (exempting all AOE from betrayal) or enforce complex intent-vs-hit correlation[cite: 24]?

**Runtime E1/E2/E3 Proof Obligations:**
*   Proof that a Tactical Worker can receive a mid-session `RelationshipTransition` from the Server and instantly update its local Faction standings (flipping neutral to hostile) without breaking pawn AI.
*   Proof that `OperationId` correlation survives the journey from client intent $\rightarrow$ Worker simulation $\rightarrow$ Server evaluation.

**Contradictions with Accepted ADRs:**
*   None. This contract operates entirely within the constraints of ADR-001 (Server Authority), ADR-002 (Worker Simulation), ADR-004 (Idempotent Commits), and ADR-007 (Writer Fencing).