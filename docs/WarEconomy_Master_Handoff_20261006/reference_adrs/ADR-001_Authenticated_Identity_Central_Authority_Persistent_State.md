# ADR-001 — Authenticated Identity, Central Authority, and Persistent State

- Status: **ACCEPTED**
- Decision Owner: Master (GPT-5.6 Sol)
- Project: WarEconomy / RimMulti
- Canonical Requirement Source: `요구사항_명세서.md`
- Provenance: Reconstructed formal ADR from accepted Master decisions and project state. This file did not previously exist as a standalone artifact.

## 1. Context

The Dedicated Server must remain final authority for multiplayer domain state while clients and Tactical Workers may perform simulation. The design must prevent unauthenticated mutation, identity spoofing, stale sessions, duplicate operations, client-authoritative commits, restart loss, and inconsistent revision publication.

## 2. Decision

### 2.1 Canonical Player Identity
- Canonical `PlayerId` is an opaque server-issued UUID.
- Provider identity, authentication identity, and display identity are separate.
- Provider identifiers map uniquely to canonical PlayerId.
- A client-supplied SteamID string alone is not sufficient proof.

### 2.2 Authentication
- Steam is the preferred provider.
- Authentication requires trusted proof/ticket verification.
- Fallback ID/password may exist only under explicit server policy.
- First-contact/session tokens do not replace initial authentication.

### 2.3 Session State
Canonical lifecycle:
`CONNECTED -> HANDSHAKE_PENDING -> AUTHENTICATED -> WORLD_READY -> DISCONNECTED`

No gameplay/domain mutation is permitted before `WORLD_READY`.

### 2.4 Session Fencing
- Every authenticated session has a `SessionEpoch` or equivalent generation.
- Parser/apply paths fence stale messages.
- Reconnect cannot let an older session commit after a newer session becomes authoritative.
- Initial duplicate-login policy: reject the newly arriving duplicate session.

### 2.5 Domain Authority
Dedicated Server is final authority for Player/Faction identity, titles, Settlement metadata, war/alliance/betrayer state, tax/market/world-domain state, ownership, operation status, and canonical revisions.

Clients and Tactical Workers may propose or calculate results but cannot unilaterally commit final domain state.

### 2.6 Domain Authority vs Simulation Authority
**Domain Authority != Simulation Authority.**

A RimWorld execution process may simulate Pawn AI/jobs/projectiles/damage/map-local mechanics, while the Dedicated Server remains final authority for political/economic/ownership/domain commits.

### 2.7 Authorization Pipeline
Every mutating request must pass authenticated principal, current session/generation, domain authorization, expected revision/fencing, idempotency checks, durable commit, and auditable result publication.

### 2.8 Persistence
Core server state must be durable across restart.
- SQLite-first is acceptable initially.
- State uses versioned revisions as appropriate: World / Player / Faction / Settlement / Save / Inventory / Operation.
- Schema migration is required; silent incompatible reset is not acceptable.

### 2.9 Idempotency and Operation Journal
Mutating multi-step operations use `OperationId` or equivalent.
- same OperationId + same payload -> at most one effect; return prior terminal result
- same OperationId + different payload -> collision rejection
- restart preserves operation result/terminal state
- journal/audit/outbox patterns may provide durable processing/publication

### 2.10 Revision and Stale-State Rejection
A local save/hash alone does not establish authority. The server compares relevant current revisions before accepting mutation. Stale clients/saves/results are rejected or explicitly reconciled.

## 3. Consequences
Positive: centralized trust boundary, reconnect/replay protection, durable recovery foundation, clean simulation/domain separation.
Cost: explicit revision/operation plumbing and persistent operation metadata.

## 4. Deferred
ADR-001 does not solve Tactical Authority (ADR-002), Temporal Authority (ADR-006A), Canonical Inventory / Save Provenance (ADR-003), Distributed Ownership Transaction / Repair (ADR-004), or Intent/Betrayal (ADR-005). RimWorld Map Save + DB atomicity is **not** solved here.

## 5. Acceptance
**ACCEPTED by Master.**
