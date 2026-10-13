GQ8 Settlement Inventory Boundary — MASTER CORRECTED DECISION BRIEF
Status: ACCEPTED ANALYSIS BASELINE — G-Q8 OPEN
Controlling decomposition
G-Q8 must not be represented as one universal set.
1. SettlementAssetGraph
The complete canonical material/custody graph belonging to or materially associated with a Settlement.
2. SettlementEconomicInventory
The economy-facing availability projection used by operations such as Auto-Shop.
This can be narrower and favor fungible assets.
3. TaxSeizableAssetSet
The policy-defined assets a Tax Collector may select.
This can include non-fungible entity categories and can require engine-backed material transfer.
The three sets overlap but are not identical by definition.
Corrected principles
- physical presence != canonical custody != economic availability != tax eligibility;
- a fungible quantity projection does not prove engine-free mutation is safe;
- LocalClock freeze does not clear persisted jobs/reservations/references;
- nested ThingOwner, equipment/apparel, minified/contained graphs, transfer staging, and Pawn/Animal/Slave entities require runtime semantic proof;
- direct XML deletion is not the default architecture;
- pre-commit staged results are non-canonical and do not acquire custody;
- entity identity requirements differ between aggregate projection and actual material transfer;
- Auto-Shop eligibility and Tax seizure eligibility must be specified separately.
Decision status
No A/B/C option is selected.
G-Q8 requires:
1. runtime RimWorld evidence;
2. then Master product-boundary decisions for EconomicInventory and TaxSeizableAssetSet.
PIPELINE_PROBE_CAS remains unblocked.