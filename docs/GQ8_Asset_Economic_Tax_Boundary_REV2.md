# GQ8_Asset_Economic_Tax_Boundary_REV2.md

**Status:** DECISION / EVIDENCE BRIEF — DO NOT RESOLVE PRODUCT POLICY WITHOUT REQUIREMENT AUTHORITY
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Paradigm Shift
Prior analysis of G-Q8 established that "Settlement Inventory" is not a single monolith. The architecture relies on three distinct boundaries:
1.  **`SettlementAssetGraph`**: The complete canonical material and custody graph (the artifact and its entities).
2.  **`SettlementEconomicInventory`**: The economy-facing projection (used for Auto-Shop and Trade).
3.  **`TaxSeizableAssetSet`**: The pool of assets eligible for forced tax collection (which may include non-fungible entities like Pawns or Slaves per FR-191)[cite: 1].

Recent Engine Host (E-A) findings introduce a critical runtime distinction: **Custody State** (where stable entity/reference identity matters, like Pawns and weapons) versus **Compressed/Environmental Geology** (where spatial/Def semantics matter, but entities lack stable native IDs, like unmined steel or soil). 

## 2. Asset Class Analysis & Matrix

This matrix evaluates how different RimWorld asset classes map to the three boundaries, their identity requirements, and how the Dedicated Server may mutate them.

| Asset Class | Canonical Custody | Stable `EntityId` Required? | `AssetGraph` Member? | `EconomicInventory` (Auto-Shop)? | `TaxSeizable` Eligible? | Engine Host Reqd for Mutate? | Projection Fields / Stale Failure |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Loose Items / Silver** | Settlement Map | No (Fungible) | Yes | Yes | Yes | No (if simple XML decrement safe) | Def, Count / Material Shortfall |
| **Stockpiles / Shelves** | Settlement Map | No (Location) | Yes | N/A (Yields loose items) | N/A | No | None (Containers transparent to index) |
| **Pawn Inventory (Carried)** | Pawn | No (Fungible) | Yes (Nested) | Policy Open | Policy Open | Yes (Safely updating pawn `ThingOwner`) | Def, Count, PawnID / Reference Loss |
| **Equipped Weapons / Apparel** | Pawn | Yes (Quality/Biocode) | Yes | No | Policy Open (FR-191)[cite: 1] | Yes (Semantic Pawn tracking) | Def, Quality, PawnID / Reference Loss |
| **Implants / Hediffs** | Pawn | Yes (Part of Pawn) | Yes | No | No (Usually) | Yes | None / Not indexed |
| **Animals / Slaves** | Faction / Map | Yes | Yes | No | Yes (FR-191)[cite: 1] | Yes (Ownership/Lord resolution) | EntityId, Value / ID Mismatch |
| **Colonists (Free Pawns)** | Faction / Map | Yes | Yes | No | Yes (FR-191)[cite: 1] | Yes (Deep faction/relation logic) | EntityId, Value / ID Mismatch |
| **Minified / Nested Containers** | Settlement Map | Yes (Inner contents) | Yes | Yes | Yes | Yes (Complex nested extraction) | Def, Quality, InnerValue / Parse Error |
| **Buildings / Workbenches** | Settlement Map | Yes / No | Yes | No | Policy Open | Yes (Grid/Region rebuilding) | Def, Position / Missing Reference |
| **Caravan / Transit Assets** | TransitClock | Yes | No (Shared World)[cite: 2] | No | No (Unless Tax Caravan target) | Yes (World custody transfer) | Not in Settlement Projection |
| **Quest / Borrowed / Locked** | Quest / System | Yes | Yes (Read-only) | No | No | N/A | Excluded / Hard Reject |
| **Reserved / Forbidden / Biocoded** | Settlement Map | Yes (Biocoded) | Yes | No | Policy Open | Yes (Reservation evaluation) | Excluded or Flagged / Race Condition |
| **Corpses** | Settlement Map | Yes | Yes | No | Policy Open (Value > 0) | Yes (Rot timer/relations) | Excluded or Value / Desync |
| **Crops / Plants (Unharvested)** | Map Geology | No | Yes (Compressed) | No | No | Yes (Grid update) | Excluded / N/A |
| **Mineables / Natural Geology** | Map Geology | No | Yes (Compressed) | No | No | Yes (Grid update) | Excluded / N/A |
| **Generated Map Features** | Map Geology | No | Yes | No | No | N/A | Excluded / N/A |

## 3. Key Architectural Questions Resolved

1.  **What belongs in `SettlementAssetGraph` after E-A?**
    It includes both discrete custody entities (with stable `EntityIds` for cross-boundary resolution) and compressed environmental geology. However, the Server indexing and cross-process mutation contracts strictly target the discrete custody entities and fungible items. Geology is preserved but generally excluded from direct cross-boundary economic mutation.
2.  **Which assets appear in Auto-Shop without independent removal?**
    None. If an item cannot be safely removed from the artifact (either via engine-free delta or Engine Host materialization), it must not appear in the `SettlementEconomicInventory` projection.
3.  **How do FR-202/203 (No stock/Silver reservation) affect execution?**
    Because setup does not reserve items (FR-202) or Silver (FR-203)[cite: 1], the execution phase must perform a strict **totality check**. At execution, the server reads the current projection; if sufficient, it commits the ADR-004 transaction[cite: 6]. The subsequent material apply must succeed fully. If the material artifact lacks the items (a shortfall race), the materialization fails, and the committed domain operation enters `REPAIR_REQUIRED` (forward recovery or compensation)[cite: 6].
4.  **Does equipped gear belong in projections/tax?**
    *Product Policy remains OPEN.* It does not belong in the fungible `SettlementEconomicInventory` (Auto-Shop). It *may* belong in the `TaxSeizableAssetSet` to satisfy FR-191[cite: 1], but executing this requires a full Engine Host to strip the gear safely without corrupting the pawn.
5.  **How are Pawn/Animal/Slave tax candidates represented?**
    They are represented in the index as discrete canonical `EntityIds` coupled with an evaluated Market Value. They are never treated as fungible stacks.
6.  **Which natural resources are economic but not custody entities?**
    Unharvested crops, mineable steel/components, and steam geysers represent massive potential wealth but possess zero custody/inventory status until physically extracted via engine jobs. They are excluded from the economic/tax boundaries.
7.  **What application-totality invariant is required?**
    **Atomic Material Application:** An engine-free delta or Engine Host material instruction must succeed completely (all specified items deducted, all targets valid) or fail entirely. No partial material writes are allowed for a single `OperationId`[cite: 6].
8.  **What happens on material apply shortfall (stale projection)?**
    If the Server commits a trade based on the projection, but the Engine Host/XML delta finds the items missing (e.g., destroyed by fire offline), the artifact cannot be updated. The operation halts at `PUBLISH_PENDING` and triggers `REPAIR_REQUIRED`, demanding explicit domain compensation (e.g., refunding the buyer) per ADR-004[cite: 6].
9.  **EntityId / rebinding rules for fungible stacks?**
    Fungible stacks (e.g., 500 Steel) do not require persistent global `EntityIds`. The Server targets them by `DefName` and Quantity. During materialization, the Engine Host dynamically selects native `loadID` stacks to consume, safely splitting or merging native items to satisfy the domain quantity requirement.
10. **What blocks offline trade execution vs. Tax policy?**
    *Offline Trade Execution* is blocked only by defining the fungible `SettlementEconomicInventory` boundary and proving engine-free or headless stack deduction. *Tax Collection* is blocked by TBD-05 (LastCollection)[cite: 1, 12] and G-Q8 product policy (are pawns/equipped gear strictly seizable, thus mandating Engine Host extraction?).

## 4. E-A / E-B Evidence Integration & Future Probes

A's Engine Host self-reports (E-A) provide useful feasibility context but are **not** independent E2 validation. Master requires Verification B or Sol to execute targeted runtime probes before authorizing production implementation of these boundaries:

*   **Stack Split/Merge Rebinding:** Probe whether the Engine Host can deterministically consume exactly 450 Steel from multiple scattered stacks, update native `loadIDs`, and save cleanly.
*   **Nested Holder Transfer:** Probe extracting a minified building or an item from a hopper without corrupting the parent container's reference graph.
*   **Equipped Item Removal:** Force-remove a biocoded weapon from an offline pawn via Engine Host. Verify the pawn does not throw exceptions upon normal client resume.
*   **Animal/Pawn Custody Transfer:** Probe transferring a Slave (`EntityId`) to a Tax Caravan (`TransitClockId`)[cite: 2], verifying `Lord` and `Faction` unbinding.
*   **Engine-Free Silver Decrement:** Attempt an XML-only direct deduction of Silver. Prove it does not break wealth caches or job reservations upon client load.
*   **Material Apply Shortfall:** Inject a missing-item scenario during artifact fold. Prove the system halts and surfaces the failure rather than silently ignoring the missing quantity.
*   **Concurrent Owner / Barrier Interaction:** Test a `DELTA_BARRIER` attempting to deduct an item while a live client's pawn is mid-haul (testing reservation collision)[cite: 9].

## 5. Freeze Points

To prevent policy leakage and safely sequence Production, the following boundaries must be frozen by Master at specific gates:

1.  **Before Offline Auto-Shop Execution:** Freeze the `SettlementEconomicInventory` definition (e.g., "Only unreserved fungible items in Stockpile Zones"). Engine-free or headless stack deduction must pass E2 proof.
2.  **Before Online Auto-Shop Execution:** Freeze the `DELTA_BARRIER` client-acknowledgement and reservation-race handling policies (ADR-007)[cite: 9].
3.  **Before Tax Collection (Execution):** Freeze TBD-05[cite: 12], and decide the `TaxSeizableAssetSet` product policy (e.g., "Does Tax take slaves, and do we require Engine Host to do so?").
4.  **Before Ownership Transfer / Conquest Fold:** Freeze canonical `EntityId` transfer mechanics for Pawns, Animals, and complex structures, as conquest transfers the entire `SettlementAssetGraph`.