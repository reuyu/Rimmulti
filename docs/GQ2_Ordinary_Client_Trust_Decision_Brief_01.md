# GQ2_Ordinary_Client_Trust_Decision_Brief_01.md

**Status:** DECISION BRIEF — DO NOT RESOLVE G-Q2
**Decision Owner:** Master (GPT-5.6 Sol)
**Project:** WarEconomy / RimMulti

## 1. The Residual Trust Problem
Under ADR-007, an owner client is granted a `WriterLeaseId` to act as an ordinary Settlement Simulation Writer[cite: 9, 11]. However, under ADR-003, owner checkpoints remain untrusted, hostile input[cite: 5, 11]. The core problem of G-Q2 is determining what evidence the Dedicated Server accepts from this untrusted materialization, and what it must independently validate, recompute, or reject before advancing the canonical `CommittedSettlementStateRevision`[cite: 5].

The validation domains strictly separate structural integrity from economic plausibility:
*   **Authenticated identity:** Server-validated against `SessionEpoch` (ADR-001)[cite: 3].
*   **Authorized writer lease:** Server-validated against `WriterLeaseId` and monotonic `FencingGeneration` (ADR-007)[cite: 9].
*   **Syntactic artifact validity:** Preflight check ensuring the `.rws` or package is structurally sound XML/data[cite: 5].
*   **Content/profile compatibility:** Server-validated against the exact `ContentProfileFingerprint` (ADR-006B)[cite: 8].
*   **Revision/parent validity:** Server-validated `CheckpointParentRevision` ensuring the client builds exactly on the last canonical head[cite: 5].
*   **Semantic engine validity:** Server-controlled engine load to verify RimWorld defs, cross-references, and graph integrity[cite: 5, 8].
*   **Economy/wealth plausibility:** Detecting impossible deltas (e.g., +50,000 Silver in 10 ticks).
*   **EntityId/custody integrity:** Ensuring no canonical cross-process ID is duplicated, stolen, or spoofed across boundaries[cite: 5].
*   **Historical replay consistency:** Proving the delta was legitimately derived from the prior state, not manipulated offline.
*   **Intentionally forged but engine-valid state:** The primary vulnerability where a player edits a save file offline to maximize Pawn skills or wealth, which the engine semantics will cleanly accept as "valid."

## 2. Candidate Trust Postures

### Posture 1: Structural + Semantic Validation Only
The server relies entirely on ADR-003 static preflight and semantic load validity[cite: 5].
*   **Cheat/Exploit Surface:** Massive. Players can freely memory-edit or save-edit offline to spawn items, heal pawns, and inflate wealth.
*   **False-Positive Risk:** Near zero. If the engine loads it, the server accepts it.
*   **Server Cost:** Low. Requires only a headless load and reference check.
*   **Mod Compatibility:** High. No heuristics to conflict with modded economic balance.
*   **Owner Autonomy/Performance:** Maximum.
*   **Dependency on G-Q1:** None.
*   **Compatibility with ADR-007:** Fully compatible, but treats the lease holder as a trusted domain actor after semantic checks pass.

### Posture 2: Plausibility Bounds / Anomaly Detection + Audit
The server tracks historical trajectories (wealth velocity, skill deltas) and flags impossible jumps.
*   **Cheat/Exploit Surface:** Moderate. Players can "drip-feed" forged wealth below the anomaly threshold.
*   **False-Positive Risk:** High. Legitimate massive wealth spikes (e.g., a lucky meteorite, a massive raid defeat, or a modded event) might trigger quarantine.
*   **Server Cost:** Low to Medium. Requires lightweight index extraction and delta comparison.
*   **Mod Compatibility:** Medium. Highly unbalanced mods may trigger false anomalies unless thresholds are exceptionally loose.
*   **Owner Autonomy/Performance:** High.
*   **Dependency on G-Q1:** None.
*   **Compatibility with ADR-007:** Fits perfectly into the checkpoint admission pipeline.

### Posture 3: Deterministic or Partial Replay for Selected Events
The client submits action logs alongside the artifact; the server replays specific high-value events (e.g., trade, tax, pawn generation) to verify the resulting material state.
*   **Cheat/Exploit Surface:** Low for covered events; high for uncovered events.
*   **False-Positive Risk:** High. RimWorld determinism is notoriously fragile across varying execution environments.
*   **Server Cost:** High. Requires maintaining strict replay logic and state matching.
*   **Mod Compatibility:** Low. Mods frequently break determinism.
*   **Owner Autonomy/Performance:** Medium (requires logging overhead).
*   **Dependency on G-Q1:** None.
*   **Compatibility with ADR-007:** Compatible, but heavily complicates the `MaterializationManifest` definition[cite: 5].

### Posture 4: Server/Worker Re-simulation of Sensitive Transitions
The owner client acts only as a viewer during specific high-risk economic events, transferring simulation authority back to a Tactical-like Worker for the duration of the event.
*   **Cheat/Exploit Surface:** Low.
*   **False-Positive Risk:** Low.
*   **Server Cost:** Extreme. Spawns remote Workers for ordinary gameplay segments.
*   **Mod Compatibility:** High (Worker is identical environment).
*   **Owner Autonomy/Performance:** Low. Handoffs interrupt ordinary play.
*   **Dependency on G-Q1:** Requires G-Q1 resolution to determine execution island topology for these handoffs.
*   **Compatibility with ADR-007:** Uses standard `HANDOFF_BARRIER` logic[cite: 9].

### Posture 5: Fully Server-Hosted Ordinary Simulation (Fallback)
The Dedicated Server hosts the map continuously; the client sends inputs only (Candidate C for ordinary play).
*   **Cheat/Exploit Surface:** Zero (within game rules).
*   **False-Positive Risk:** Zero.
*   **Server Cost:** Extreme. Unscalable for hundreds of settlements.
*   **Mod Compatibility:** High.
*   **Owner Autonomy/Performance:** Dictated by WAN latency.
*   **Dependency on G-Q1:** Rejects all client-hosted G-Q1 options.
*   **Compatibility with ADR-007:** Replaces the client writer lease entirely with a view lease.

## 3. Critical Forgery Examples

*   **Silver/Item creation:** An offline save edit inflates a stack from 50 to 50,000. Engine-valid, structurally sound, breaks economy.
*   **Pawn skill/health manipulation:** An offline save edit revives a dead pawn or maxes skills. Circumvents medical/training mechanics.
*   **Wealth inflation affecting Faction Tier:** A player generates artificial wealth to cross the promotion threshold for a new `Faction Tier` (FR-015)[cite: 1, 10]. Allows unearned political power and expanded `SettlementLimit` (FR-034)[cite: 1].
*   **Duplicated EntityId/custody:** Duplicating a server-addressable `EntityId` (e.g., a high-value prisoner) in the XML. Must be strictly rejected by ADR-003 uniqueness invariants[cite: 5].
*   **Stale pre-tax/pre-trade checkpoint:** An owner tries to submit a checkpoint from *before* a server-authored `DELTA_BARRIER` deducted tax, attempting to erase the transaction. Defeated by ADR-007 `BaseCommittedSettlementStateRevision` fencing[cite: 9].
*   **Save edited offline then reconnected:** Player drops connection, edits save, reconnects. Must be caught by parent revision constraints or plausibility bounds.
*   **Valid-looking modded ThingDef substitution:** Player swaps a cheap item's Def to an expensive modded item's Def. Must be caught by ADR-006B `ContentProfileFingerprint` validation[cite: 8].

## 4. Required Boundary: Invariants vs. Policy

An accept-all `IAnomalyDetector` must never bypass the following **Mandatory Architecture Invariants**:
1.  **Identity & Lease Auth:** Must strictly pass ADR-001 authentication and hold the correct ADR-007 `FencingGeneration`[cite: 3, 9].
2.  **Revision Lineage:** The checkpoint must map exactly to the `CheckpointParentRevision`; stale replays are hard-rejected[cite: 5].
3.  **Content Manifest Match:** The artifact must strictly bind to the server-pinned `ContentProfileFingerprint` (ADR-006B)[cite: 8].
4.  **`EntityId` Uniqueness:** The canonical registry must strictly reject any artifact containing duplicated, spoofed, or missing server-addressable `EntityIds`[cite: 5].

**Residual-Risk / Product Choices (The G-Q2 Policy Space):**
*   How to handle engine-valid but mathematically improbable jumps in fungible wealth or pawn skills.
*   Whether to invest engineering budget into an anomaly detection heuristic (Posture 2) vs. accepting the risk (Posture 1).
*   Whether the ultimate fallback for severe economy exploitation is banning the player via Server Administration (FR-231) rather than complex runtime prevention[cite: 1].

## 5. Evidence Plan

Before Master can decide G-Q2, Dev A and Sol must execute the following runtime probes against the pipeline:
1.  **Forged Checkpoint Acceptance:** Modify an XML save offline (e.g., +10k Silver) and confirm it passes ADR-003 semantic load without crashing the headless validator.
2.  **Stale Revision Replay:** Submit a valid, older checkpoint. Confirm the server strictly rejects it based on `CommittedSettlementStateRevision`[cite: 5].
3.  **EntityId Duplication:** Clone a canonical Pawn `EntityId` in the XML. Confirm the server projection logic crashes or explicitly rejects the collision.
4.  **Mod/Profile Mismatch:** Introduce a new `ThingDef` into the artifact. Confirm ADR-006B rejection[cite: 8].
5.  **Partial Replay Feasibility:** Test if a minimal deterministic log of wealth-generating events (e.g., mining, harvesting) can be reliably replayed without divergence in RimWorld 1.6.

## 6. End State

*   **Implementable Invariants:** The pipeline must immediately enforce ADR-007 fencing, ADR-003 revision parent matching, ADR-006B profile checks, and `EntityId` collision rejection. These are not subject to G-Q2 policy.
*   **Genuine Product/Risk Decisions:** Master must decide the acceptable level of economic forgery (Posture 1 vs. 2 vs. 5) and the UX cost of anomaly false positives.
*   **Runtime Facts Needed:** The actual feasibility of catching manual XML edits via heuristic bounds without triggering false positives on modded events or massive raids.
*   **G-Q2 Freeze Point:** G-Q2 must be decided **before ordinary-client Production acceptance/integration**. It does not block the current `PIPELINE_PROBE_CAS` or Server-authored metadata mutations.