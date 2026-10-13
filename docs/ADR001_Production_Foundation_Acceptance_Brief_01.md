# ADR001_Production_Foundation_Acceptance_Brief_01.md

**Status:** DECISION / TRACEABILITY BRIEF — NO CODE
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Identity and Authentication

The Production Foundation replaces synthetic test fixtures with hostile-environment primitives.
*   **Stable `PlayerId`:** The canonical, immutable database primary key representing a human user account, completely decoupled from transient session data or RimWorld pawn identities.
*   **Authentication & Session Establishment:** The process by which the server validates provided credentials (whether standard password, OAuth, or pre-shared key, dictated by product policy) and issues a cryptographically secure, ephemeral Session Token.
*   **Session Token / Capability:** A bearer or signed token (e.g., JWT or secure session ID) held by the client, representing an active, authenticated connection.
*   **Server-Derived `PrincipalId`:** The server middleware extracts the `PrincipalId` (which maps to `PlayerId` + `SessionEpoch`) *exclusively* by validating the Session Token.
*   **Privilege / Control-Plane Separation:** Admin and system-level operations require a distinct authorization capability (e.g., `IsAdmin` flag in the session token or a dedicated internal endpoint port), preventing ordinary players from escalating to server operators.
*   **Why probe fixtures fail:** E1/E2 pipeline probes inject a synthetic `ActorId` directly into the command pipeline to test transaction durability. In Production, accepting a client-asserted `ActorId` over the wire is a critical vulnerability. The server must derive the actor from the validated token.

## 2. SessionEpoch and Reconnect

*   **Creation / Advancement:** A `SessionEpoch` is a monotonic identifier minted upon a *new* authenticated login (a full session establishment). It represents a single continuous logical session for a `PlayerId`.
*   **Transport Reconnect vs. New Session:** If a client drops the TCP socket but reconnects holding a still-valid Session Token (e.g., within the G-Q6 `SUSPENDED_GRACE` window), the server binds the new socket to the *existing* `SessionEpoch`. If the token expires or the user logs in from another machine, a *new* `SessionEpoch` is minted.
*   **Stale Old-Process Rejection:** If an old, zombified client process sends a packet using `SessionEpoch` 1, but the server has already advanced the player to `SessionEpoch` 2 (due to a new login), the server violently rejects the packet.
*   **G-Q6 `SUSPENDED_GRACE` Interaction:** During the grace period, the `SessionEpoch` remains alive in memory, reserving the player's execution rights.
*   **`FencingGeneration` Advancement:** `FencingGeneration` (ADR-007) advances when a new `WriterLease` is acquired or when a *new* `SessionEpoch` forcibly takes over an existing lease. A simple transport socket reconnect using the *same* `SessionEpoch` within the grace period does **not** advance the `FencingGeneration`.

## 3. Handshake & Admission Order

The server connection pipeline must follow a strict, fail-closed handshake before any domain operation is permitted. Failure at any step drops the socket immediately.

1.  **Protocol & Schema Version Check:** Validates the network protocol format.
2.  **Server/World Identity & `StoreIncarnationId` Broadcast:** Server identifies itself.
3.  **`ContentProfileFingerprint` Check:** Client must hash-match the Server's required RimWorld mods/defs (ADR-006B).
4.  **Authentication:** Client provides credentials/token. Server derives `PrincipalId`.
5.  **`SessionEpoch` Mint/Resume:** Server checks active sessions, resumes or mints a new epoch.
6.  **Authorization/Capability Binding:** Server attaches roles (e.g., Admin vs. Ordinary) to the session context.
7.  **Readiness ACK:** Server sends a READY signal. Domain commands are now accepted.

## 4. Frame and Message Integrity

This layer guarantees that accepted byte streams map to authentic intentions.
*   **Length / Framing:** Strict byte-length headers prevent buffer overflow and fragmented reads.
*   **Authenticated Session Binding:** Every parsed command frame is stamped by the connection middleware with the derived `SessionEpoch` and `PrincipalId`. The domain logic *never* reads these from the payload itself.
*   **Replay / Stale Frame Rejection:** Frames must include request correlation IDs or monotonic sequence numbers to prevent replay attacks over the same session.
*   **Malformed / Unknown Packets:** Logged and dropped. If repetitive, the socket is severed.
*   **Endpoint Isolation:** Admin/Control-plane commands are either routed to a different physical port or hard-fenced by the middleware role-checker before deserialization.
*   **Integrity vs. Encryption:** Transport encryption (TLS) prevents eavesdropping. Frame integrity prevents a validly encrypted client from injecting forged actor identities or replaying old commands into the pipeline. Both are required.

## 5. Durable World / Server Identity

*   **Server / World Identity:** The global, persistent identifier for the multiplayer instance (e.g., "World Alpha"). Survives restarts, updates, and backups.
*   **Schema Version:** The code-level database layout version. Survives restarts, changes on patches.
*   **`ContentProfileFingerprint`:** The exact hash of allowed RimWorld XML defs/mods. Survives restarts, changes only when server admins update the modpack.
*   **`StoreIncarnationId` (MPC-002 correction):** A monotonic ID representing the continuum of the database. Survives ordinary restarts. It **rotates (advances)** *only* when the server is wiped or restored from an older backup. This explicitly fences out offline client states that belong to a dead timeline.
*   **`SessionEpoch`:** Strictly ephemeral. Destroyed on server restart or expiration.

## 6. Startup Gate

Before the Server transitions from `STARTING` to `READY` (accepting authenticated canonical mutations), the following must be true:
1.  **DB / Schema:** Database connection pool is alive and schema migrations are fully applied.
2.  **Pipeline:** The underlying transaction pipeline/bus is active.
3.  **Identity:** World Identity and `StoreIncarnationId` are successfully loaded from the DB.
4.  **Content Profile:** The `ContentProfileFingerprint` is computed/loaded into memory.
5.  **Auth / Session Services:** The Session Manager is ready to accept socket connections.
6.  **Required Registries:** Player and Faction basic lookup caches are warm.
*(Note: Engine Host readiness and Settlement artifact materialization are NOT required for the Foundation to reach READY. Metadata/Trade mutations can execute purely in the domain layer).*

## 7. Minimal Authorization Model

The initial Production authorization model requires only the absolute minimum to unblock subsequent domain slices (like Auto-Shop setup):
*   **Own Identity:** The middleware guarantees `Command.Actor == PrincipalId`.
*   **Admin / Control-Plane:** A binary capability (e.g., `IsServerAdmin`) for operations like creating accounts or wiping the server.
*   **Delegated Ownership Checks:** The middleware does *not* query "Does Player X own Settlement Y?". It passes the authenticated `PrincipalId` to the Domain Command Router. The Domain Aggregate (e.g., `TradeConfiguration`) is responsible for validating ownership rules.

## 8. Failure and Restart Matrix

| Scenario | State / Resolution |
| :--- | :--- |
| **Server Restart** | All `SessionEpoch`s destroyed. Clients must perform full reconnect/auth. |
| **Client Reconnect (Token Valid)** | Resumes existing `SessionEpoch`. Pending async ACKs flush to client. |
| **Client Reconnect (Token Expired)** | Token rejected. Client must re-authenticate. New `SessionEpoch` minted. |
| **Stale Session Packet** | Packet dropped. Client socket closed if mismatch persists. |
| **Backup Restore (Time Travel)** | `StoreIncarnationId` rotates. All existing client offline caches violently invalidated. |
| **Profile Mismatch at Handshake** | Socket dropped with `CONTENT_MISMATCH` reason. |
| **Malformed Handshake** | Socket dropped. Potential IP throttle. |
| **Auth Success, Server Not READY** | Handshake succeeds, but Server returns `SERVICE_UNAVAILABLE` and drops. |
| **Duplicate Request (Post-Reconnect)** | Idempotency key (ADR-004) hits Cache. Returns original result. |

## 9. Acceptance Matrix

| Requirement / Invariant | Production Component | State / Token / Revision | Failure Mode | E1 Test (Dev) | E2 Test (Sol) | Blocks Next Slice |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Handshake / Profile (ADR-006B) | Connection Router | `ContentProfileFingerprint` | Socket dropped pre-auth | Inject bad hash | Connect w/ unapproved mod | Auth/Session Gate |
| Auth to Identity (ADR-001) | Auth Middleware | `SessionToken` $\rightarrow$ `PrincipalId` | Auth Denied | Valid/Invalid token | Forge token signature | Auth/Session Gate |
| Continuity (MPC-002) | DB / Bootloader | `StoreIncarnationId` | Handshake reject | Restore DB, verify ID increment | Client cache rejection | Auth/Session Gate |
| Stale Replay Fencing | Session Manager | `SessionEpoch` | Frame dropped | 2 sockets, same player | Inject stale Epoch | Auth/Session Gate |
| Domain Auth Delegation | Command Router | `PrincipalId` injected into Envelope | Domain Reject (Not Owner) | Send command for unowned entity | Try to edit another's Auto-Shop | Player/Faction/Settlement Gate |
| Transaction Idempotency | Pipeline Substrate | `OperationId` (ADR-004) | Returns cached response | Send same ID twice | Network partition retry test | Material-State Gate |

## 10. Deliverable End State

**Recommended Smallest Implementable Slice:**
The ADR-001 Production Foundation Slice should be scoped strictly to:
1.  **Bootstrapper:** Loading `StoreIncarnationId` and `ContentProfileFingerprint`.
2.  **Connection Manager:** The TCP/WebSocket listener enforcing the Handshake sequence.
3.  **Auth Middleware:** Validating the token and generating the `PrincipalId` / `SessionEpoch`.
4.  **Command Router:** Wrapping the incoming payload in a secure envelope (stamped with the derived identity) and passing it to the internal Pipeline Substrate.

**Exact Stop Line:**
This slice ends exactly where the Domain Command Router receives the securely enveloped, authenticated command. It does not implement any actual Player creation, Faction logic, or Settlement mutation.

*(Note: ADR-001 is NOT marked runtime-complete. This brief serves as the E0/Preparation boundary to authorize the Foundation implementation work package, which will commence after the Pipeline P1 contract passes its E2 gate).*