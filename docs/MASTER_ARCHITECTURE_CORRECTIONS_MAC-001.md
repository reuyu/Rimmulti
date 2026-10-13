MASTER ARCHITECTURE CORRECTIONS — MAC-001
MPC-002 controlling clarification
These clarifications supersede conflicting lower-level wording until accepted ADR files are formally consolidated.
A. Fencing
FencingGeneration changes when execution authority changes or is invalidated:
- lease revoke;
- holder change;
- worker/session generation replacement;
- store incarnation replacement.
A normal server-authored commit while the same lease remains valid does not by itself increment FencingGeneration.
Instead it advances the required canonical base revision and applied-operation watermark that the writer must acknowledge/apply before publishing a later checkpoint.
B. Lease/barrier scope
The lease root is an execution island / LocalClock domain and contains a Settlement scope set.
Cardinality may be one or many.
This intentionally does not decide G-Q1.
A barrier is conservatively island-scoped unless runtime evidence proves a finer Settlement-only pause safe.
C. Transaction classes
Fast path:
single-scope typed domain operation -> one atomic canonical DB transaction; no PREPARED reservation.
Reservation path:
staged material, multi-scope or multi-party operation -> explicit durable reservations + PREPARED and a separately proven recovery contract.
D. Canonical operation identity
Key:
(PrincipalId, OperationId)
Fingerprint:
server-computed, versioned canonical typed envelope covering all semantically material authority/scope/revision/profile/config/payload fields.
E. Publication
Canonical decision and delivery are different things.
Operation decision is immutable COMMITTED or ABORTED.
Derived events are append-only and independently acknowledged/deduped per consumer.
F. Engine Host
One implementation boundary owns all RimWorld materialization/loading/semantic-validation modes.
B2-lite remains the storage/authority direction but is a hypothesis until round-trip evidence passes.
G. Vanilla-first
Reuse native multi-map, map lifecycle, jobs, pathing and simulation.
Custom topology/interception requires evidence of an actual conflict with LocalClock, authority or materialization semantics.
H. Material-state gate
No Production material mutation until the Engine Host round-trip/census and live barrier/delta evidence are reviewed.