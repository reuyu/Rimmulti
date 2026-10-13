MASTER_REVIEW_ADR003_ADR007_DRAFT01
Verdict
- ADR-003 Draft-1: PROPOSED / REVISION REQUIRED
- ADR-007 Draft-1: PROPOSED / REVISION REQUIRED
The drafts capture the correct architecture direction but contain several contract-level problems that would create rework if accepted unchanged.
ADR-007 Critical Corrections
1. Handoff ordering
   Do not revoke the client lease and then require a final upload.
   Correct model:
   barrier/freeze -> candidate final checkpoint under valid lease -> validate/commit -> revoke/fence -> grant Worker lease.
   If final checkpoint cannot be obtained, resume from the last committed canonical head.
2. Lease identity
   Use a monotonic server-issued fencing generation for write authority.
   Authentication token/capability and fencing generation are separate.
   SessionEpoch and WorkerGeneration remain principal/session identifiers referenced by the lease.
3. Disconnect
   A stale client may continue simulating locally; the server cannot trust physical stop.
   Canonical safety comes from lease revocation/fencing.
   Grace/checkpoint-loss policy remains OPEN (G-Q6).
4. G-Q1 topology
   Include:
   - Player-scoped clock
   - One active settlement per client
   - Per-map virtualization
   - Separate execution islands / remote ordinary simulation
ADR-003 Critical Corrections
1. Artifact format
   Do not equate the canonical Settlement artifact with a target-only .rws.
   RimWorld native .rws is a Game/World save and current target-only packaging is not yet proven.
   Define the logical canonical Settlement artifact/package; concrete format remains validation-dependent.
2. Canonical head vs pending operations
   Pending Auto Shop/Tax requests queued during Tactical do not increment the committed SettlementStateRevision.
   Otherwise the Worker checkpoint parent becomes stale by design.
   Increment only when the queued operation is actually committed.
3. Projection/index durability
   The index must be durable and verifiable/rebuildable.
   It cannot be only an in-memory convenience.
4. Entity identity scope
   Avoid turning B2-lite back into field-level/event-level serialization.
   Server EntityId is required for entities that cross canonical boundaries, are server-addressable, or are externally referenced.
   Internal ephemeral map objects may remain native-artifact-local unless they cross that boundary.
5. Native binding
   ThingComp or a global mapping component are implementation candidates, not an accepted contract.
   The ADR should state the binding invariants and validation requirements.
6. Hostile checkpoint validation
   Required layers:
   - content/version manifest
   - allowed serialized types/schema
   - size/complexity bounds
   - typed semantic reference validation
   - canonical EntityId/namespace checks
   - parent revision / writer lease / provenance
   - plausibility/audit policy (subject to G-Q2)
Accepted Direction Preserved
- Dedicated Server canonical custody
- Leased ordinary Simulation Writer
- B2-lite default baseline
- Exclusive Tactical material-state lease
- Tactical-time shop/tax queueing
- Stable cross-process canonical identity
- Untrusted client checkpoints