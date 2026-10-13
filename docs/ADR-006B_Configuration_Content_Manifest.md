# ADR-006B_Configuration_Content_Manifest.md

**Status:** PROPOSED (Not Accepted)
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. Context & Baseline
This ADR defines the configuration and content manifest contracts necessary to prevent client/Worker content drift, silent semantic load loss, and the weaponization of "fail-closed" mechanics. It aligns with the upstream constraints established in ACCEPTED ADR-001 (Version/Protocol Admission), ADR-003 (Hostile Checkpoint Validation), ADR-006A (Temporal Schema Classification), ADR-007 (Writer Lease Admission), and ADR-008 (World-Layer Content)[cite: 16, 17, 18, 19, 23].

## 2. Required Manifest Identity
To enforce strict content parity, the Dedicated Server pins a canonical content profile.
*   **`ContentProfileId`:** A unique identifier for a specific, server-approved combination of content.
*   **`ContentProfileRevision`:** Increments whenever the active pinned profile undergoes an authorized migration or update.
*   **Manifest Components:** The profile must strictly define:
    *   RimWorld base build/revision.
    *   The official DLC set.
    *   Approved mod package IDs and explicit versions/hashes.
    *   A deterministic load order.
    *   Assembly/data hashes (where exact binary parity is required).
    *   The supported serialization/schema profile (to validate typed structures before load).
    *   A Def registry/dependency fingerprint (to prevent missing `ThingDef` or `RecipeDef` errors).
    *   A server-approved gameplay-content capability set.
*   **Content Separation:** The manifest explicitly distinguishes between:
    *   Gameplay/simulation-affecting content (strict parity required for all).
    *   Presentation-only/cosmetic client content (eligible for bypass if proven safe).
    *   QA/test-only content (strictly excluded from Production profiles).
    *   Server/Worker infrastructure content (e.g., bridge assemblies).

## 3. Admission Contracts
No gameplay mutation or simulation lease may proceed if the required gameplay content profile is incompatible[cite: 16, 19].
*   **Client $\rightarrow$ Server Handshake:** Clients must declare their active profile. Mismatches in gameplay content result in immediate pre-auth rejection[cite: 16].
*   **Owner Checkpoint $\rightarrow$ Canonical Validation:** The `ContentProfileRevision` under which a checkpoint was generated must match the server's current pinned profile. Checkpoints from older revisions require explicit migration (see Section 8)[cite: 18].
*   **Ordinary Client & Tactical Worker Materialization:** Engines must initialize strictly matching the `ContentProfileId`. A Tactical Worker failing to load the exact pinned profile aborts the `HANDOFF_BARRIER`[cite: 19].
*   **Shared World Executors:** Server-controlled pathing or transit executors must utilize the pinned profile to ensure movement costs and physiology calculations perfectly match client expectations[cite: 23].

## 4. Semantic Dependency Policy
To address observed semantic loss (missing Defs, invalid body-part references, registry mismatches), the architecture mandates strict semantic dependency closure.
*   **Approval-Time Closure:** A `ContentProfileId` cannot be pinned until all Def cross-references (e.g., a custom `HediffDef` referencing a `RecipeDef`) are statically proven to exist.
*   **Layered Validation:** Literal XML scanning is insufficient. Validation requires:
    *   Typed registry/reference validation at the server preflight level[cite: 18].
    *   Server-controlled engine semantic validation (a headless validator load) before a profile is approved for live canonical acceptance[cite: 18].
*   **Post-Load Validation:** Validation must assert identity, count, and relationship integrity after the engine initializes to ensure no components were silently dropped by mod code.

## 5. Approval-Time vs. Runtime Failure (Weaponization Prevention)
The architecture must prevent a scenario where unsupported content (e.g., an unclassified temporal mod) blocks admission to a Tactical Session, thereby rendering a settlement immune to lawful offline attacks (FR-153).
*   **Approval/Migration Gate:** Unsupported, unclassified, or ambiguous content is rejected or quarantined *at approval/migration time*. The server will not pin a `ContentProfileId` containing unclassified components.
*   **Runtime Guarantee:** Once a `ContentProfileId` is pinned, runtime admission to a Tactical Worker *must not* fail due to missing content or schema errors.
*   **Silent Drop Prohibition:** Nothing may be silently dropped during load. If an artifact contains unknown data during runtime (due to a defect), it must enter a `REPAIR_REQUIRED` state and alert operators, rather than silently deleting the object and continuing[cite: 18].

## 6. Configuration Authority and Revision
Server configuration balances gameplay rules against the risk of ambiguous retroactivity.
*   **`ConfigRevision`:** A monotonic revision tracking the current state of server-authoritative gameplay settings (e.g., Tier thresholds, WarPending durations)[cite: 16].
*   **Authority & Scope:** The Dedicated Server is authoritative over all gameplay config. Client presentation preferences (e.g., UI scale, volume) remain locally scoped and out of the manifest.
*   **Retroactivity Policy:** Config fields must be explicitly classified to resolve retroactivity concerns:
    *   *Immediately Prospective:* Applies to new calculations instantly (e.g., NPC market price recovery rates).
    *   *Operation-Snapshotted:* The value is captured at the time of the operation and remains fixed (e.g., a WarPending timer started at 24 hours remains 24 hours, even if the global config is later reduced to 12 hours).
    *   *Session/Restart-Bound:* Requires a server restart or new session to apply (e.g., map generation rules).
    *   *Non-Retroactive Historical:* Cannot alter past events or durably committed operations.

## 7. Content Migration
Content updates (adding/removing mods, DLC changes, Def updates) to an actively running world require a formal migration contract.
*   **State Machine:** `CURRENT_PROFILE` $\rightarrow$ `MIGRATION_PENDING` $\rightarrow$ `MIGRATING` $\rightarrow$ `NEW_PROFILE`.
*   **Artifact Migration:** When the server pins a new `ContentProfileRevision`, older canonical artifacts cannot be loaded directly. They must be processed through a server-controlled migration engine.
*   **Validation:** The migration engine loads the old artifact under the new content profile, performs data migration (if supported by the mod/update), and outputs a new artifact. This new artifact must pass the Semantic Dependency Policy (Section 4).
*   **Rollback:** If migration fails (e.g., missing Defs cause catastrophic semantic loss), the migration is aborted. The world remains quarantined on the old profile until an operator intervenes or provides a valid migration path.

## 8. Cosmetic Client-Only Mods
Cosmetic mods may bypass exact gameplay-content parity *only* if they are explicitly declared, audited, and added to the approved cosmetic capability profile.
*   **Eligibility Strict Rules:** The mod must be proven **not** to:
    *   Alter simulation data (e.g., changing tick rates, pathing costs).
    *   Add/remove serialized gameplay state (e.g., custom `ThingComps` that save data).
    *   Alter Defs used by the simulation.
    *   Modify authority-sensitive UI into local gameplay mutation (e.g., a UI mod that bypasses the `PendingOperationQueue`).
    *   Change canonical operation semantics.

## 9. Cross-ADR Integration
*   **ADR-001 (Auth):** Rejects connections lacking the pinned `ContentProfileId` before the `WORLD_READY` state[cite: 16].
*   **ADR-003 (Validation):** Uses the manifest to execute static preflight and schema validation on untrusted owner checkpoints[cite: 18].
*   **ADR-006A (Temporal):** Requires all mods in the manifest to have their temporal fields fully classified against the W/L_s/G/M schema[cite: 17].
*   **ADR-007 (Writer Lease):** A lease is only granted if the writer executes the exact `ContentProfileId`. Checkpoints uploaded under an old profile during a migration barrier are fenced[cite: 19].
*   **ADR-008 (World Layer):** Server-controlled pathing executors load the exact Defs and costs specified by the pinned `ContentProfileId`[cite: 23].

---

## 10. Decision Table

| Item | Classification | Action/Note |
| :--- | :--- | :--- |
| **Manifest Components (Hashes, Load Order)** | Safe Master architecture decision now | Mandates strict parity to prevent drift. |
| **Approval-Time Dependency Closure** | Safe Master architecture decision now | Prevents weaponization of fail-closed mechanics against offline attacks. |
| **Config Retroactivity Categories** | Safe Master architecture decision now | Classifying configs (e.g., Operation-Snapshotted vs. Prospective) resolves ambiguity. |
| **Cosmetic Mod Eligibility Rules** | Safe Master architecture decision now | Strict non-simulation rules prevent cheat escalation. |
| **Server-Controlled Engine Migration** | Safe Master architecture decision now | Defines the boundary; actual tool implementation deferred. |
| **Exact list of Approved Mods** | Product-policy decision | Master/Operator must curate the actual allowlist. |
| **Exact Config Values (e.g., War Duration)** | Product-policy decision | Operator defined via Server Config. |
| **Semantic Validation Implementation** | Runtime validation required | Proving a headless engine can reliably assert graph integrity post-load. |
| **Transaction / Migration Commit Mechanics** | Deferred to ADR-004 | Durable transition between `ContentProfileRevisions`. |

---

## 11. Acceptance Readiness
*   **Decisions safe to accept:** The structural requirement for a pinned `ContentProfileId`, Approval-Time vs. Runtime failure policies, the Config Retroactivity classification model, and the Cosmetic Mod eligibility boundary.
*   **Remaining Decision Requests:** None strictly within the architecture boundary. (The actual *contents* of the allowlist and config values are product/operator tasks).
*   **Runtime proof obligations:** Proving that the server-controlled semantic validation engine can reliably detect dropped Defs or missing `ThingComps` without generating false positives on transient engine data.
*   **Contradictions:** No contradictions exist with ADR-001, ADR-003, ADR-006A, ADR-007, or ADR-008.

## 12. Contract Matrix

| State / Field | Owner | Writer | Readers | Validation Boundary | Revision / Fencing |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ContentProfileId` / `Revision`** | Dedicated Server | Server Operator | All Clients & Workers | Pre-auth Handshake | `ContentProfileRevision` |
| **`ConfigRevision`** | Dedicated Server | Server Operator | All Clients & Workers | Admission / Action Execution | `ConfigRevision` |
| **Artifact `ContentProfileRevision`** | Dedicated Server | Authoritative Artifact Writer | Semantic Validator / Materializer | Hostile Checkpoint Preflight | Matches Pinned Profile or triggers Migration |
| **Session / Lease Expected Profile** | Dedicated Server | Server Coordinator | Leased Writer | Lease Grant | Exact `ContentProfileId` Match |
| **Cosmetic Capability Profile** | Dedicated Server | Server Operator | Client Handshake | Approval-Time Static Audit | Bound to `ContentProfileRevision` |
| **Migration State** | Dedicated Server | Migration Coordinator | Canonical Validators | Server-Controlled Migration Engine | Advances `ContentProfileRevision` |