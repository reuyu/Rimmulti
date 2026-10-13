# Trade_Configuration_Acceptance_Brief_01.md

**Status:** DECISION / TRACEABILITY BRIEF — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Exact Scope

The `TradeConfiguration` slice represents the purest form of metadata-only domain state. It captures the player's economic intent (Buy Orders and Sell Orders) without interacting with RimWorld engine semantics.

**In Scope:**
*   Persistence of Trade intents (e.g., Target `ItemDef`, Buy/Sell Price, Target Quantity, Active/Paused status) per Settlement (FR-197, BR-019).
*   Enforcement of ownership capability to modify these intents.
*   Concurrency and idempotency handling (Pipeline P1).
*   Outbox event generation to notify the live client of configuration changes.

**Strictly Out of Scope:**
*   Reading, parsing, or modifying the Settlement's physical `.rws` inventory.
*   Checking actual Silver balances or Item availability.
*   Reserving items or Silver for pending orders.
*   Executing trades or interacting with the `DELTA_BARRIER` / Engine Host.
*   Tax collection policies.

## 2. Canonical Identity

The configuration exists as a long-lived Domain Aggregate decoupled from ephemeral network state.
*   **Aggregate Root:** `SettlementId`. The trade configuration is an extension of the Settlement's domain state.
*   **Owner Reference:** Binds to the current legal `PlayerId` or `FactionId` dictating policy.
*   **`TradeConfigurationRevision`:** A strictly monotonic integer incrementing on every successful modification of the configuration payload.
*   **`SettlementOwnershipEpoch`:** A snapshot of the Registry's ownership epoch at the time the configuration was last authorized or modified.
*   **`StoreIncarnationId` Binding:** Implicitly bound to the global timeline; if the database restores from backup, the configuration rolls back congruently.
*   **Why `SessionEpoch` is Excluded:** `SessionEpoch` is a transient network connection capability used to fence execution leases and replay attacks. Domain intent (Trade Configuration) outlives network sessions; a player disconnecting does not delete their Auto-Shop prices.

## 3. Authorization

Authorization strictly follows the ADR-001 Foundation and Registry models.
*   The Command Router receives an incoming `UpdateTradeConfiguration` payload wrapped in a secure envelope bearing the server-derived `PrincipalId`.
*   The Trade Domain queries the Registry: `VerifyOwnerAtEpoch(SettlementId, PrincipalId, ExpectedOwnershipEpoch)`.
*   **Stale Epoch Rejection:** If the client submits `ExpectedOwnershipEpoch = 5` but the Registry reports Epoch 6 (e.g., the settlement was just conquered), the transaction is violently rejected as `UNAUTHORIZED_STALE_EPOCH`.
*   **Zero Client Trust:** The domain logic NEVER trusts a `PlayerId` embedded in the client's JSON payload. It relies exclusively on the `PrincipalId` injected by the auth middleware.

## 4. Ownership Transfer Behavior

When a Settlement changes hands (e.g., conquest, faction transfer), the `SettlementOwnershipEpoch` increments in the Registry.

**Candidate Policies (Product Choice Deferred):**
*   **A. Auto-Clear:** The entire `TradeConfiguration` is wiped clean upon transfer.
*   **B. Disable & Require Rebind:** The configuration transfers to the new owner but is marked `INACTIVE`, requiring the new owner to explicitly audit and re-enable it.
*   **C. Transfer As-Is:** The new owner immediately assumes the active shop (High risk of exploiting the new owner's silver).

**Mandatory Architecture Invariant (Frozen):**
Regardless of the chosen policy, the old owner's authenticated update attempts, and any pending offline trade executions authorized under the old epoch, **must instantly fail validation** the moment the epoch increments.

## 5. FR-202/203 No-Reservation Semantics

*   **FR-202 (No Item Reservation):** Creating a Sell Order for 500 Steel does not lock, remove, or reserve 500 Steel in the artifact.
*   **FR-203 (No Silver Reservation):** Creating a Buy Order for 500 Steel does not escrow the required Silver.
*   **Execution Fencing Clarification:** This lack of reservation applies *only* to the order registration (metadata) phase. When an actual buyer executes a trade (future G-Q8 work), the execution phase *will* utilize a `DELTA_BARRIER` and strict totality checks. Trade Configuration simply registers the intent.

## 6. Revision / CAS (Compare-And-Swap)

To prevent the ABA problem (e.g., a player editing prices on two different PCs simultaneously), updates require strict CAS concurrency control.
*   **Command Payload:** Must include `ExpectedTradeConfigurationRevision` and `ExpectedOwnershipEpoch`.
*   **Mismatch / Collision:** If the expected revision does not match the database, the transaction aborts with `CONCURRENCY_CONFLICT`.
*   **Idempotency (P1):** If the exact same `OperationId` + `PrincipalId` arrives twice (network retry), the server returns the cached `COMMITTED` receipt without advancing the revision again.

## 7. Persistence / Restart Matrix

| Scenario | State / Resolution |
| :--- | :--- |
| **Server Restart** | Trade Configurations load cleanly from the database. No impact. |
| **StoreIncarnation Rotation** | Database restores to prior state. Clients attempting CAS with newer revisions fail and must resync. |
| **Duplicate Update Retry** | Pipeline idempotency cache intercepts it. No DB mutation. |
| **Stale Client Config Edit** | Client submits edit with `ConfigRevision = 10`, but DB is at 11. Rejected (CAS). |
| **Ownership Transfer Race** | Client submits edit, but `SettlementOwnershipEpoch` just incremented. Rejected (Auth). |
| **Profile/ItemDef Mismatch** | Client tries to list a modded item that is not in the `ContentProfileFingerprint`. Rejected. |

## 8. API Boundary

The internal Domain API exposed to the Command Router must be minimal:

*   `GetTradeConfiguration(SettlementId)` $\rightarrow$ Returns current Orders, `TradeConfigurationRevision`, and `SettlementOwnershipEpoch`.
*   `UpdateTradeOrders(SettlementId, ExpectedConfigRev, ExpectedOwnershipEpoch, OrdersList, OperationId)`
*   `SetTradeStatus(SettlementId, ExpectedConfigRev, ExpectedOwnershipEpoch, IsEnabled, OperationId)`

Direct physical item transfers, validations of inventory availability, or queries to RimWorld defs (other than verifying the `ItemDef` string against the hashed profile manifest) are prohibited in this boundary.

## 9. Acceptance Matrix

| Requirement | Field / Invariant | Authority | Revision / CAS | Failure Mode | E1 Test (Dev) | E2 Test (Sol) | Blocks Next Slice |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| FR-197 (Define Orders) | `BuyOrders`, `SellOrders` | Server DB | `TradeConfigRevision` | Invalid ItemDef | Save/Load valid config | Submit invalid `ItemDef` string | Offline Trade Execution |
| Ownership Fencing | `PrincipalId` verification | Registry | `OwnershipEpoch` | `UNAUTHORIZED` | Submit with wrong `PrincipalId` | Epoch race condition | Offline Trade Execution |
| Concurrency (CAS) | Exact Revision Match | Server DB | `TradeConfigRevision` | `CONFLICT` | Concurrent update test | Network lag double-submit | General Domain UI |
| Idempotency (P1) | `OperationId` uniqueness | Pipeline | N/A | Return Cached | Submit same `OperationId` | Reconnect packet replay | General Domain UI |
| FR-202/203 | Zero Material Mutate | Server DB | `TradeConfigRevision` | Pipeline Violation | Ensure artifact untouched | N/A | Offline Trade Execution |

## 10. Stop Line

The `TradeConfiguration` slice is officially COMPLETE when a client can durably and idempotently create, read, and update authenticated Trade Orders, fully fenced by the `SettlementOwnershipEpoch` and `TradeConfigurationRevision`, resulting in an Outbox event for UI synchronization.

**It does NOT:**
*   Execute a trade.
*   Inspect actual `.rws` stock.
*   Reserve material stock or Silver balances.
*   Transfer any items or currency.
*   Invoke the Engine Host or generate deltas.
*   Collect any tax.