# ADR-006B_Configuration_Content_Manifest_v2.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the configuration and content manifest contracts necessary to prevent client/Worker content drift, silent semantic load loss, and the weaponization of "fail-closed" mechanics. It operates within the upstream constraints established in ACCEPTED ADR-001 (Version/Protocol Admission)[cite: 16], ADR-003 (Hostile Checkpoint Validation)[cite: 18], ADR-006A (Temporal Schema Classification)[cite: 17], ADR-007 (Writer Lease Admission)[cite: 19], and ADR-008 (World-Layer Content)[cite: 23].

## 2. Profile Identity Model
To enforce strict content parity, the Dedicated Server utilizes a distinct profile identity and revision model:
*   **`ContentProfileId`:** A stable identifier for the lineage or name of the server's approved content profile.
*   **`ContentProfileFingerprint`:** The immutable, exact gameplay profile identity. It is a deterministic hash or strict signature of the RimWorld build/revision, official DLC set, approved mod package IDs, mod versions/hashes, deterministic load order, and approved gameplay-content capability set.
*   **`ContentProfileRevision`:** The monotonic world-level sequence of accepted profile migrations/adoptions.

All artifacts, checkpoints, client sessions, and Worker materializations must securely bind to the exact `ContentProfileFingerprint` they were produced under.

## 3. Schema & Codec Binding
Artifact and checkpoint metadata must be strictly bound to their generation context to decide between compatible loads, migration requirements, or outright rejection[cite: 18]. The metadata must include:
*   The exact `ContentProfileFingerprint` and `ContentProfileId`.
*   The `ContentProfileRevision`.
*   The **Serialization/Schema Version** of the state format.
*   The **Temporal/Semantic Codec Version** (specifically where ADR-006A typed temporal fields depend on it for interpretation)[cite: 17].

## 4. Admission Contracts & ADR-001 Alignment
Content and profile compatibility checks are admission and handshake gates; they do *not* constitute authentication[cite: 16].
*   **Handshake Pipeline:** The architecture strictly preserves the ADR-001 lifecycle: `CONNECTED` $\rightarrow$ `HANDSHAKE_PENDING` $\rightarrow$ `AUTHENTICATED` $\rightarrow$ `WORLD_READY`[cite: 16]. Protocol and mod compatibility checks occur during `HANDSHAKE_PENDING`[cite: 16].
*   **Checkpoint & Artifact Validation:** Owner checkpoints entering canonical validation (ADR-003) must match the expected `ContentProfileFingerprint`[cite: 18].
*   **Engine Materialization:** Ordinary clients, Tactical Workers, and Shared World pathing executors must initialize using the exact pinned profile[cite: 19, 23]. No gameplay mutation may proceed if the required gameplay content profile is incompatible[cite: 16].

## 5. Dependency Closure Policy
Static proof alone is an insufficient acceptance oracle for RimWorld modifications due to dynamic code and generated references. Dependency closure is enforced via layered approval:
1.  **Manifest/Hash/Load-Order Validation:** Standard byte and version parity checks.
2.  **Typed Static Registry/Reference Validation:** Preflight checks for known, statically analyzable references (e.g., XML cross-references) where possible[cite: 18].
3.  **Server-Controlled Engine Semantic Load:** Loading the profile into a controlled, headless engine to evaluate deep load semantics[cite: 18].
4.  **Post-Load Graph/Reference/Identity Checks:** Validating identity, counts, and component attachments post-initialization.
5.  **Explicit Disposition:** Any unclassified, unsupported, or ambiguous content discovered during validation receives an explicit rejection or quarantine disposition.

## 6. Runtime Failure Invariant
A pinned approved profile guarantees that untrusted participants cannot introduce content drift into a lawful Tactical or ordinary session. However, it cannot make all runtime content/schema failures impossible.
*   **Defect Handling:** Runtime operator/server defects or corrupted canonical state trigger a `QUARANTINED` or `REPAIR_REQUIRED` status[cite: 17, 18].
*   **No Silent Drop:** Failures must never silently delete data, drop entities, or ignore unresolvable references[cite: 18].
*   **No Defender Immunity:** "Fail-closed" mechanics must never be interpreted or exploitable as a defender-controlled immunity mechanism against lawful offline attacks (FR-153)[cite: 14].

## 7. Configuration Authority & Retroactivity
The Dedicated Server is authoritative over all gameplay configurations. Ambiguity regarding whether a configuration change affects past events is resolved by categorizing all `ConfigRevision` fields into explicit retroactivity policies:
*   **`IMMEDIATELY_PROSPECTIVE`:** Applies instantly to all new calculations (e.g., global NPC market recovery rates)[cite: 14].
*   **`OPERATION_SNAPSHOTTED`:** The config value applies to a specific operation and must not retroactively change. The durable operation state *must* record the effective config value or immutable config snapshot reference used when the operation was created[cite: 16]. Later replay/recovery must use this snapshotted value, never the current config[cite: 16].
*   **`SESSION_OR_RESTART_BOUND`:** Requires a server restart or a new player session to apply (e.g., map generation constraints)[cite: 14].
*   **`MIGRATION_REQUIRED`:** A config schema change that is severe enough to require a formal world migration sequence.
*   **`NON_RETROACTIVE_HISTORICAL`:** Values that purely document past states and cannot alter durably committed operations.

## 8. Content Migration Pipeline & States
When the `ContentProfileRevision` advances, older canonical artifacts cannot safely load directly under the new profile unless the migration mechanism explicitly supports a dual-profile adapter.
*   **Conceptual Flow:** Old-profile compatible read/materialization $\rightarrow$ Migration Transform $\rightarrow$ New-profile semantic validation $\rightarrow$ New canonical artifact adoption. (Exact transaction/rollback mechanics remain ADR-004 scope).
*   **Migration State Machine:**
    *   `CURRENT`: The world is running normally on the active profile.
    *   `MIGRATION_REQUIRED`: A new profile is staged, and the world is halted awaiting transformation.
    *   `MIGRATION_PENDING`: Migration operations are queued.
    *   `MIGRATING`: The server-controlled migration engine is processing the artifact graph.
    *   `QUARANTINED`: Migration failed (e.g., unresolvable semantic loss). Operator intervention required.
    *   `CURRENT (new)`: The world successfully adopted the new `ContentProfileRevision`.

*(Note: `REPAIR_REQUIRED` is kept strictly for defective/corrupted canonical state, not planned version migrations)[cite: 16, 17].*

## 9. Cosmetic Capability Model
Client-only cosmetic mods may bypass strict gameplay-content parity only if they conform to a server-approved **Cosmetic Capability Profile**.
*   The profile defines known, allowed hooks and resources.
*   The mod must possess no serialized gameplay state.
*   The mod must perform no simulation Def mutation.
*   The mod must not provide authority-sensitive input bypasses.
*   **Admission:** If a client mod exceeds the approved cosmetic capability profile, admission fails closed and the client is rejected at the handshake[cite: 16].

---

## 10. Contract Matrix

| Field / Component | Owner | Writer | Reader | Validation Boundary | Revision / Fencing Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ContentProfileId`** | Dedicated Server | Server Operator | All Clients & Workers | Handshake Admission | Tied to profile lineage/name |
| **`ContentProfileFingerprint`** | Dedicated Server | Server Operator | Checkpoint Preflight / Handshake | Immutable exact profile hash | Fences incompatible payloads |
| **`ContentProfileRevision`** | Dedicated Server | Migration Coordinator | Materialization Logic | Migration Flow | Monotonic world-adoption sequence |
| **`ConfigRevision`** | Dedicated Server | Server Operator | Authority / Operation Logic | Action Execution | Evaluated per retroactivity category |
| **Artifact Profile Binding** | Dedicated Server | Authoritative Artifact Writer | Semantic Validator | Hostile Checkpoint Preflight | Rejects mismatch vs expected Fingerprint |
| **`SchemaVersion` / `CodecVersion`** | Dedicated Server | Server Operator | Deserializer / Temporal Codec | Artifact Load | Triggers migration or rejection on mismatch |
| **Session Expected Profile** | Dedicated Server | Server Coordinator | Owner Client | Handshake (`HANDSHAKE_PENDING`) | Fences clients lacking the Fingerprint |
| **Worker Expected Profile** | Dedicated Server | Server Coordinator | Tactical / Pathing Worker | Worker Lease Grant | Aborts materialization on mismatch |
| **`CosmeticCapabilityProfile`** | Dedicated Server | Server Operator | Client Handshake | Approval-Time / Static Audit | Rejects if client exceeds capability bounds |
| **`MigrationState`** | Dedicated Server | Migration Coordinator | Admission Control | Migration Engine | Halts admission during `MIGRATING`/`QUARANTINED` |

---

## 11. End State

*   **Acceptance Readiness:** The layered dependency closure, explicit migration states, retroactivity categories, and profile identity separation (Fingerprint vs. Revision) safely address the fail-closed weaponization and config consistency risks. The ADR is ready for Master acceptance.
*   **Remaining Decision Requests:** None strictly within this architecture boundary. Master/Operator product decisions govern the actual contents of the config values and the specific mods placed on the allowlist.
*   **Runtime Proof Obligations:** Proving the server-controlled engine can successfully perform post-load semantic identity/reference validation to detect dropped references without relying purely on static XML analysis.
*   **Contradictions:** No contradictions exist with ADR-001, ADR-003, ADR-006A, ADR-007, or ADR-008. The boundaries are firmly respected.