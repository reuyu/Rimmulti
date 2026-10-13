# Player_Faction_Settlement_Registry_Acceptance_Brief_01.md

**Status:** DECISION / TRACEABILITY BRIEF — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Identity Taxonomy

The registry strictly defines canonical domain identities, decoupling logical ownership from material simulation.

*   **`PlayerId`:** (Stable) Immutable primary key for the human account.
*   **`PrincipalId`:** (Stable within session) The server-derived identity asserting the `PlayerId` behind an authenticated command.
*   **`FactionId`:** (Stable) Global identifier for a political entity (Player Tribe, NPC Faction, City-State).
*   **`PersonalFactionId`:** (Replaceable) A lifecycle pointer indicating the `FactionId` currently acting as the player's personal tribe. Dissolves upon joining a higher tier; regenerates upon expulsion. *Critically: `PlayerGlobalStateSegment` identity is keyed to `PlayerId`, never to `PersonalFactionId`, to survive these political transitions.*
*   **`SettlementId`:** (Stable) The global identifier for a discrete location/colony. Survives ownership changes and conquests.
*   **`SettlementOwnershipEpoch`:** (Replaceable/Monotonic) An integer revision that increments *only* when the legal domain owner of the `SettlementId` changes (e.g., conquest, faction join).
*   **`PlayerGlobalStateSegment` Owner Reference:** (Stable) Keyed strictly to `PlayerId`.
*   **`StoreIncarnationId`:** (Stable across restarts; Rotates on backup restore) Validates timeline continuity.

## 2. Creation & Lifecycle Scenarios

*   **Account Exists Pre-Genesis:** `PlayerId` is registered without any `FactionId` or `SettlementId`.
*   **First Personal Tribe Creation:** Server mints a `FactionId`, assigns it to the player's `PersonalFactionId` pointer.
*   **First Settlement Registration (Genesis):** Server mints `SettlementId`, assigns ownership to `PlayerId` / `FactionId`, and sets `SettlementOwnershipEpoch = 1`.
*   **Additional Owned Settlement:** Server mints new `SettlementId`, assigns to existing `PlayerId`, sets Epoch = 1.
*   **Join Another Faction:** `PlayerId` membership transfers to the new `FactionId`. `PersonalFactionId` dissolves. Affected `SettlementId`s update Faction ownership; `SettlementOwnershipEpoch` increments.
*   **Expulsion & New Personal Faction:** Player loses City-State membership. Server mints new `FactionId` for `PersonalFactionId`. Retained `SettlementId`s transfer to this new Faction; `SettlementOwnershipEpoch` increments.
*   **Branch Split:** Surviving branches receive new `FactionId`s. Associated `SettlementId`s update ownership; `SettlementOwnershipEpoch` increments.
*   **Conquest / Ownership Transfer:** `SettlementId` domain ownership transfers to the conqueror `PlayerId`/`FactionId`. `SettlementOwnershipEpoch` increments.
*   **Extinction / Deletion References:** *Deferred (TBD-01, TBD-04).* The registry must support marking `SettlementId`s or `FactionId`s as `DESTROYED` without violating foreign keys in historical records.

## 3. Ownership Authority

The registry defines the *Domain Owner*, which must never be conflated with the execution lease or physical item location.
*   **Domain Owner:** The legal `PlayerId` and/or `FactionId` holding sovereign rights to the `SettlementId`. Changed *only* by Dedicated Server domain rules (Conquest, Trade, Diplomacy).
*   **WriterLease Holder:** The ephemeral network session (`SessionEpoch`) or Tactical Worker authorized to mutate the physical artifact *right now*. Validated against the Domain Owner, but distinct.
*   **Material Custody:** The `MapSegment` or `TransitClockId` where the assets currently exist.
*   **Authority:** All ownership relations are 100% Dedicated Server authoritative. A client may never dictate its own Faction tier or Settlement ownership.

## 4. Revision Model

To ensure concurrency and prevent race conditions (e.g., a player configuring a shop exactly as their settlement is conquered), the metadata registry relies on specific revisions:
*   **`PlayerRecordRevision`:** Increments on player-level changes (e.g., username change, ban status).
*   **`FactionRevision`:** Increments on political state changes (war, alliance, tier promotion).
*   **`SettlementRegistryRevision`:** Increments on Settlement metadata changes (name change, coordinates).
*   **`SettlementOwnershipEpoch`:** Increments *strictly* on ownership transfer.
*   **Feature Binding:** Features like `TradeConfiguration` must bind to the `SettlementOwnershipEpoch`. If Player A configures an Auto-Shop (caching Epoch 5), but Player B conquers the settlement (advancing it to Epoch 6), Player A's pending trade config update must fail validation. The trade config becomes instantly stale upon epoch rotation, awaiting explicit product policy on whether to clear or transfer it.

## 5. Genesis Integration

The registry handles the metadata precursor to Engine Host artifact generation:
*   **Reservation:** Receives an intent, reserves a `SettlementId` in `PENDING_GENESIS` state.
*   **Idempotency:** Binds to `GenesisOperationId`. Retries return the pending reservation.
*   **Association:** Binds the pending `SettlementId` to the `PlayerId`.
*   **Artifact Admission:** Once the Engine Host completes the `.rws` generation and it passes validation, the registry updates the `SettlementId` state to `ACTIVE`, links the initial `ArtifactBaseStateRevision`, and initializes `SettlementOwnershipEpoch = 1`.

## 6. PlayerGlobal Integration

The registry provides structural pointers without defining the physical XML/JSON schema of the global state:
*   **Identity Key:** `PlayerGlobalStateSegment` is requested via `PlayerId`.
*   **Revision:** Tracked via `PlayerGlobalRevision` to prevent stale global state injection during artifact materialization.
*   **Domain Segregation:** `FactionDomainState` (Tier, Titles, War) is held natively in the registry database and projected to the client/Engine Host as read-only. It is never mastered in the `PlayerGlobalStateSegment`.

## 7. TradeConfiguration Prerequisite API

To unblock the `TradeConfiguration` slice, the Registry must expose the following internal, server-side API:
*   `GetSettlementOwnerInfo(SettlementId) -> { PlayerId, FactionId, SettlementOwnershipEpoch, State }`
*   `VerifyOwnerAtEpoch(SettlementId, PrincipalId, ExpectedEpoch) -> Boolean`
*   `GetFactionMembership(PrincipalId) -> { FactionId, Role }`
*   *(No inventory, material, or economic data is exposed by this API.)*

## 8. Auth/Session Interaction

Following ADR-001:
*   The Registry receives the `PrincipalId` from the Command Router.
*   The Registry does *not* care about `SessionEpoch` (which handles transport replay and lease fencing).
*   A client dropping their socket and generating a new `SessionEpoch` has zero impact on `SettlementOwnershipEpoch` or Domain Ownership.

## 9. Failure / Restart Matrix

| Scenario | State / Resolution |
| :--- | :--- |
| **Duplicate Create/Register** | Blocked by Unique Constraints on `PlayerId` / Idempotency Key. |
| **Stale Ownership Revision** | Command rejected (e.g., updating TradeConfig with old Epoch). |
| **Concurrent Conquest / Config Update** | Database CAS locks `SettlementId`. If Conquest wins, Config Update fails epoch check. |
| **Server Restart** | Registry loads perfectly from persistent DB. No data loss. |
| **Incarnation Rotation (Backup Restore)** | `StoreIncarnationId` changes. All external caches/clients invalidated. |
| **Genesis Reserved, Artifact Fails** | `SettlementId` remains `PENDING_GENESIS` until timeout, then garbage collected. |
| **Ownership Transferred, Index Delay** | Core domain ownership is canonical instantly. Dependent projections eventually consistent. |

## 10. Acceptance Matrix

| Requirement | Registry Entity | Revision / Epoch | Authority | E1 Test (Dev) | E2 Test (Sol) | Next Slice Unblocked |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Account Tracking | `PlayerRecord` | `PlayerRecordRevision` | Server | Create Player | Duplicate PlayerId Reject | Genesis Metadata |
| Faction Topology | `FactionRecord` | `FactionRevision` | Server | Create Faction | Change membership | Genesis Metadata |
| Settlement Domain | `SettlementRecord` | `SettlementRegistryRev` | Server | Reserve Settlement | Query non-existent ID | TradeConfiguration |
| Ownership Fencing | `OwnerRelation` | `SettlementOwnershipEpoch` | Server | Update Owner, Check Epoch | Stale Epoch Config Reject | TradeConfiguration |
| Genesis Prep | `SettlementRecord` | `GenesisOperationId` | Server | Reserve pending ID | Idempotent reserve retry | Genesis Engine Host |

## 11. End State

**Recommended Smallest Production Registry Slice:**
The implementation should strictly encompass the relational/document models and internal APIs for `PlayerRecord`, `FactionRecord`, and `SettlementRecord`, with a strict enforcement of `SettlementOwnershipEpoch`.

This slice establishes the absolute minimum structure necessary to support authenticated domain ownership checks, unblocking both the `TradeConfiguration` metadata mutation and the Genesis Metadata Admission, without touching actual RimWorld `.rws` material state or finalizing Engine Host logic.