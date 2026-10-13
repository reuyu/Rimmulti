# GQ8_Offline_Material_Application_Contract_01.md

**Status:** DECISION / EVIDENCE BRIEF — DO NOT RESOLVE PRODUCT POLICY
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Corrected Transaction Model (Offline Execution)

The previous assumption that a projection check immediately authorizes an economic commit is conceptually flawed and violates canonical custody (ADR-003). FR-202/203 prohibit stock/Silver reservation *at order registration*, but execution-time fencing is mandatory.

The correct, strict pipeline for offline material mutations (like Auto-Shop execution) is:
1. **Fence:** Acquire the `WriterLease` / `DELTA_BARRIER` on the offline Settlement.
2. **Canonical Materialize/Rebase:** Load the canonical `ArtifactBaseStateRevision`.
3. **Apply Complete Candidate Mutation:** Attempt to deduct/transfer the exact required items in-memory.
4. **Semantic Validate:** Ensure the mutation did not corrupt references, jobs, or limits.
5. **Durable Staged Result:** Persist the mutated artifact as a candidate manifest/blob.
6. **Canonical Economic/Domain Commit:** Execute the ADR-004 database transaction against the Domain State (e.g., deducting buyer Silver, transferring ownership).
7. **Promote/Fold:** Advance `CommittedSettlementStateRevision` and set the staged result as the new canonical baseline.

*Crucial Distinction:* A stale projection or material shortfall discovered during step 3 causes a clean **ABORT/RETRY**. `REPAIR_REQUIRED` is strictly reserved for severe system failures occurring *after* Step 6 (post-commit), where the domain state has mutated but the artifact promotion failed catastrophically.

## 2. Mutation Mechanism Comparison

| Characteristic | A. Engine Host Staged Mutation | B. Engine-Free Typed Codec | C. Server-Custodied Escrow |
| :--- | :--- | :--- | :--- |
| **Source-of-truth input** | `.rws` artifact + Engine Semantics | `.rws` artifact (XML) | Domain State / Database |
| **Supported asset classes** | All (Pawns, Nested, Equipped, Fungible) | Strictly bounded fungibles (Ground stacks) | Only items actively deposited by player |
| **Stable identity/rebinding** | Natively handled by RimWorld engine | High risk; requires custom XML heuristics | Escrow holds canonical `EntityId`s directly |
| **Engine cache/ref risks** | Zero (Headless engine manages caches) | High (May break jobs, `ThingOwner` limits) | Zero (Material artifact not touched offline) |
| **Application-totality proof**| Deterministic failure if items missing | Deterministic failure via XML parsing | Immediate DB check |
| **Crash boundary** | Safe (Discard memory, revert to base) | Safe (Discard XML delta) | Safe (Standard DB transaction) |
| **Staged-result format** | Complete newly saved `.rws` artifact | Patch/Delta or newly saved `.rws` | N/A (No material mutation required) |
| **Semantic validation** | Native engine `load()` verification | Fragile (Relies on schema assumptions) | N/A |
| **Performance/Cost** | High (CPU/RAM overhead of loading RimWorld) | Low (Fast XML manipulation) | Minimal (DB only) |

*Note: Model C (Escrow) alters the canonical UX of "selling from stockpiles" and must not be adopted unless explicitly authorized as a product policy by Master.*

## 3. Fungible Identity & Rebinding Contract

Fungible items (e.g., Steel, Silver, basic meals) require strict conservation rules across the material/domain boundary.

*   **Aggregation vs. Identity:** `SettlementEconomicInventory` aggregates fungibles, ignoring transient RimWorld `loadID`s. However, the material mutation (Engine Host or Codec) *must* map the deduction to specific `loadID`s in the artifact.
*   **Deterministic Selection:** The mutation logic must define a deterministic selection protocol when pulling 450 Steel from three stacks of 200. (e.g., "closest to trade beacon" or "highest stack count first").
*   **Split/Merge Conservation:** Deducting 150 from a stack of 200 leaves 50. The remaining stack retains its native `loadID`. The extracted 150 ceases to exist in the `.rws` artifact.
*   **Boundary Crossing & `EntityId` Minting:** If extracted fungibles are transferred to a Caravan (Shared World), the Server mints a new canonical `EntityId` (or a fungible manifest entry) for the Caravan. The transient native `loadID` is permanently stripped.
*   **Sufficiency of `DefName` + Quantity:** `DefName` + quantity is **only** sufficient for pure, stateless fungibles (Silver, Steel, Wood). It is intrinsically insufficient for anything involving Quality, Stuff (Material), HitPoints, Biocoding, Minification, or Tainted status. Those require explicit sub-criteria in the projection and exact matching during material apply.
*   **Nested Holders:** Attempting to extract fungibles from nested holders (Hoppers, Shelves, pawn inventories) is exponentially harder for an Engine-Free Codec and strongly pushes the architecture toward the Engine Host model.

## 4. Projection Semantics Contract

The `SettlementEconomicInventory` projection guarantees the following semantics:
*   **Advisory Availability:** It represents what *was* available at the time of the last checkpoint. It does not guarantee current material reality.
*   **Revision Binding:** Every projection is hard-bound to a specific `ArtifactBaseStateRevision`.
*   **Staleness:** It is instantly considered "stale advisory data" if a live client is currently simulating under an active `WriterLease`.
*   **Exclusion Flags:** Must inherently exclude items marked Forbidden, items bound to active Quests, or items actively reserved by Jobs (if discernible).
*   **Rebuild Source:** Rebuilt exclusively by parsing an accepted `.rws` artifact or receiving a Server-authored mutation fold.
*   **Never Authorizes Commit:** The projection **never** authorizes a domain commit. It only authorizes the initiation of the fencing and candidate mutation process.

## 5. Failure-State Matrix (Offline Trade Sequence)

| Scenario / Step | Architectural State / Action | Resolution |
| :--- | :--- | :--- |
| Sell order exists, no stock reserved | Advisory Projection updated | N/A |
| Buyer execution begins | Acquire `DELTA_BARRIER`, Load artifact | Proceed |
| **Projection stale / Material shortfall** | Items missing/destroyed in artifact | **ABORT / RETRY** (Buyer notified, Barrier dropped) |
| Candidate staged successfully | Mutation completes in-memory, `.rws` staged | `VALIDATING` $\rightarrow$ `PREPARED` |
| **Crash before DB commit** | Process dies before domain commit | **ABORT / RETRY** (Staged blob orphaned/GC'd) |
| DB commit succeeds | Server canonical state updated | **COMMITTED / PUBLISH_PENDING** |
| **Commit succeeds, crash pre-promotion**| Fold incomplete | `COMMITTED`, Reconciler resumes fold on boot |
| **Staged candidate corrupt post-commit**| DB committed, but artifact unreadable | **REPAIR_REQUIRED** (Admin/Forward recovery needed) |
| Exact retry (Duplicate Request) | Idempotency key match | Return cached `COMMITTED` receipt |
| Competing offline operation | Lease collision at Fence | Queue or **ABORT / RETRY** |

## 6. Tax Reuse Boundary

The offline Auto-Shop material application logic cannot be completely reused for Tax Collection due to strict domain differences:
*   **Discrete Custody:** Tax rules (FR-191) target Pawns, Slaves, and Animals. These possess canonical `EntityId`s and deep relationship/Lord bindings, wholly incompatible with fungible `DefName` + quantity logic.
*   **Equipped/Nested State:** Taxing a Pawn requires resolving what happens to its equipped gear, mandating full Engine Host semantic resolution.
*   **TBD-05 Dependency:** Tax requires complex lifecycle policies (partial collection / `LastCollection` resets) that Trade Execution lacks.
*   **TaxSeizable != AutoShop Available:** The `TaxSeizableAssetSet` will inherently include items a player would never intentionally place in the `SettlementEconomicInventory`.

## 7. Evidence Plan (Runtime Probes)

Dev A and Sol must deliver the following runtime evidence:
1.  **450 Steel across Stacks:** Prove deterministic extraction of a split quantity across 3 un-merged stacks, verifying engine/codec handles `loadID` lifecycle safely.
2.  **Silver Decrement:** Prove a pure fungible Silver deduction doesn't corrupt Wealth caches upon client resume.
3.  **Nested Holder Extraction:** Prove extraction from a RimWorld `Shelf` or `Hopper`.
4.  **Stale Projection Shortfall:** Initiate execution where projection says 500 exist, but artifact has 400. Prove pipeline hits strict `ABORT` before domain commit.
5.  **Crash Pre-Commit:** Stage the candidate, simulate server crash, verify clean state on reboot.
6.  **Crash Post-Commit (Promotion):** Commit to DB, simulate crash before `.rws` fold. Prove Reconciler detects `PUBLISH_PENDING` and completes the fold.
7.  **Concurrent Material Ops:** Hit the `DELTA_BARRIER` with two simultaneous offline trade requests; verify orderly queueing or explicit fencing rejection.
8.  **Engine Host vs Codec Equivalence:** (If Codec is pursued) Prove the XML-codec produces an artifact byte-for-byte semantically identical to one generated by the Engine Host for a pure fungible deduction.

## 8. Freeze Point

**Before Offline Auto-Shop Execution begins development**, Master must freeze:
1. The choice of Mutation Mechanism (Engine Host vs. Engine-Free Codec) for fungibles.
2. The exact Fungible Identity/Rebinding contract (how split stacks are handled).
3. The Transaction Model integration, ensuring E1/E2 tests explicitly validate the `fence -> materialize -> validate -> stage -> commit` totality rule.