# ARCH-REDTEAM-REVIEW-002 — Midpoint Review Before First Real Gameplay Mutation

- Project: WarEconomy / RimMulti
- Reviewer role: hostile independent principal architect (not implementer, not decision authority)
- Decision authority: Master (GPT-5.6 Sol)
- Date: 2026-10-02
- Inputs: SRS v1.0, MSR-043, MDR-043 (MD-001..MD-055), QDL-040, ADR-001, ADR-002, ADR-003 v3, ADR-004 v2, ADR-005 v2, ADR-006A, ADR-006B v2, ADR-007 (file "v5", header "v4"), ADR-008 v2, Shared_Settlement_State_Pipeline_Design_02, Production_Transaction_Pipeline_Slice_01
- No source code, database file or test artifact was supplied. Statements about the pipeline implementation are derived from the developer report text (including its quoted C# excerpt). Independent E2 has **not** run.

## Label legend

| Tag | Meaning |
|---|---|
| **[CANON]** | Root SRS text |
| **[ACCEPTED]** | Accepted ADR / Master Decision (MD-xxx) / Master acceptance clarification |
| **[PROVISIONAL]** | ADR-002 / Candidate C / P2 presentation candidate |
| **[E2]** | Independent QA evidence adopted by Master in the ledgers (not re-run by this reviewer) |
| **[DEV-E1]** | Developer self-report only, which is not evidence of correctness |
| **[INFERENCE]** | Reviewer reasoning, including from known RimWorld 1.6 / SQLite / .NET behaviour |
| **[RECOMMENDATION]** | Reviewer proposal, not binding until Master decides |

---

## 1. Executive Verdict

### **CONTINUE WITH CORRECTIONS**, split by track:

| Track | Verdict |
|---|---|
| Server transaction substrate (Pipeline Slice-01) | **Continue with corrections.** Fix 6 concrete defects/ambiguities (MR-06..MR-11) before E2 sign-off. Several are hard to retrofit once real data exists |
| First real gameplay mutation (TradeConfiguration) | **Re-sequence.** The idea is sound, but it is premature. ADR-001 Foundation is still unimplemented (QA-001/002/005/011 OPEN), and no canonical Settlement registry exists to fence "current owner/epoch" against (MR-12) |
| Anything touching Settlement **material** state (trade execution, tax, checkpoints, Tactical publication) | **HOLD on runtime evidence.** The central B2-lite primitive (extract one settlement, re-materialize it elsewhere, detect loss) has **zero** runtime evidence, yet eight ADRs depend on it (MR-03) |
| Accepted ADR set | **Two contract corrections required now**: the ADR-004 §9 vs ADR-007 Phase-B fencing contradiction (MR-01), and island-scoped vs settlement-scoped barriers and leases (MR-02, MR-14). **Two missing canonical homes**: player-global engine state (MR-04) and settlement genesis (MR-05) |

Bottom line: [INFERENCE] the project is solving the right problem, because the SRS forces independent clocks, offline attack and offline trade. But since the last review it has spent its effort on paper contracts and presentation polish, while the critical-path engine primitive got no runtime work. The ADR set is now internally coherent on paper, with one real contradiction. Its biggest risk is that it is **unfalsified**, not that it is wrong.

---

## 2. Top Findings

Template: severity, source, failure scenario, coverage, minimum correction.

### MR-01 — ADR-004 §9 contradicts ADR-007 DELTA_BARRIER Phase B (fencing on every commit)
- **Severity:** Critical
- **Source:** [ACCEPTED] ADR-004 §9: "After transaction COMMIT, the FencingGeneration advances. Any stale checkpoint or worker publication carrying the old generation is strictly rejected. To resume, the writer must rematerialize from the newly advanced CommittedSettlementStateRevision." [ACCEPTED] ADR-007 §5 Phase B and Clarification 4/5: after a server-authored commit the client ACKs and applies the delta, `BaseCommittedSettlementStateRevision` advances, and the **same lease resumes**.
- **Failure scenario:**
  - Literal ADR-004 reading: every online Auto-Shop sale (FR-211) bumps the fencing generation, so the owner client must rematerialize, i.e. reload its map. One buyer = one reload of the owner's colony.
  - Literal ADR-007 reading: the generation does *not* advance, so ADR-004's "stale publication after commit" protection depends only on the base-revision check.
  - Implementers will pick one reading per code path. Fencing semantics then diverge between the transaction layer and the lease layer, which is exactly the class of defect already seen in QA-PRESENT-007/H05-01 (old-connection response relabeled with the current epoch).
- **Coverage:** Not covered. Both texts are ACCEPTED, and each claims "no contradictions".
- **Minimum correction:** [RECOMMENDATION] Master clarification:
  - `FencingGeneration` advances **only on lease revocation or holder change**.
  - A server-authored commit against a live lease advances the *required base revision*, and the lease stays valid only after ACK.
  - Every checkpoint must carry `(FencingGeneration, CheckpointParentRevision, AppliedOperationWatermark)`, and the server rejects one whose watermark is below the committed ops for that scope.
  - Amend ADR-004 §9 wording to say "advances the fencing generation **if the writer is revoked**; otherwise advances the required base revision".

### MR-02 — DELTA_BARRIER is island-scoped in practice, costs a save-hitch, and is a griefing vector
- **Severity:** Critical (before any online trade/tax execution)
- **Source:** [ACCEPTED] ADR-007 §4/§5 (barrier per settlement writer, one designated barrier checkpoint). [ACCEPTED] ADR-006A §5 (one engine island has one G). [CANON] FR-207 ("immediately"), FR-211 (Auto-Shop while online), FR-187 (tax online/offline).
- **Failure scenario:** [INFERENCE]
  1. A vanilla client advances every loaded map on one `TicksGame`, so you cannot freeze "settlement A" while settlement B on the same client keeps ticking. A DELTA_BARRIER therefore freezes the **whole client game**.
  2. The "one designated barrier checkpoint" is a save/extract of live engine state. RimWorld saves of mid/late colonies take seconds and cause visible hitches. One online trade = one game freeze plus upload.
  3. Many buyers hitting an online owner's shop cause repeated freezes. A buyer who wants to harm an online rival can spam cheap purchases. If the owner's machine misses the barrier timeout, ADR-007 §4 fences the owner and **discards all progress since the last checkpoint**. Buyers can force progress loss on others.
- **Coverage:** The mechanism is defined, but its cost, scope and abuse resistance are not. G-Q6 (grace/cadence) interacts with it but does not cover it. No runtime evidence exists.
- **Minimum correction:**
  - [RECOMMENDATION] Declare barriers **execution-island-scoped**.
  - Add mandatory **barrier coalescing**: online server-authored ops queue and are applied together at barrier windows tied to checkpoint cadence, so the barrier rate is bounded independently of the buyer rate.
  - Add per-target rate limits.
  - Specify that a barrier timeout during a server-initiated barrier never discards more than one checkpoint interval of owner progress, or else returns the op to the queue instead of fencing.
  - Whether "immediately" (FR-207) tolerates a bounded barrier window is a **product question** (Section 6).
  - Run runtime PoC E-B (Section 5) before the trade-execution slice.

### MR-03 — The B2-lite core primitive is unproven, and its loading context is undefined
- **Severity:** Critical (for all material-state work)
- **Source:** [ACCEPTED] ADR-003 §2: artifact "format (e.g. target-only .rws or custom package) remains validation-required". [ACCEPTED] ADR-006A §3: "**full engine context** for reference resolution". MSR-010 correction 5: native full `.rws` is not canonical. [E2] QA-ENGINE-005 (GameComponent dispatch mutates global state, including the Anomaly timer). QA-ENGINE-001/004 (non-target/world drift).
- **Failure scenario:**
  - Nothing recorded in MSR-001..043 shows a single settlement extracted from one RimWorld game and re-materialized into a *different* game context without loss.
  - If ADR-006A's "full engine context" means "load the whole owner world and suppress everything else", the E2 record already shows that leaks (005/001/004).
  - If it means "synthesize a minimal world from server projections plus the target artifact", no ADR or WP owns that synthesizer: faction registry projection, world grid, world pawns, ideology and research stubs.
  - Every downstream ADR (003 manifest replay, 004 staged results, 007 handoff, 008 ingress, 006B migration) assumes this works.
- **Coverage:** Not covered by evidence. The G-Q1 brief's sequential-materialization probe (MSR-040) is queued **after** TradeConfiguration and is framed as a topology probe, not as the B2-lite falsification test.
- **Minimum correction:**
  - [RECOMMENDATION] Make **PoC E-A "Settlement Artifact Round-Trip"** the next engine work item, ahead of more presentation hardening. Scope: extract → store → materialize into a synthetic minimal world → census compare → re-extract → hash/census stability.
  - Decide explicitly whether the materialization context is *full owner world* or a *synthetic minimal world*. [RECOMMENDATION] Synthetic minimal world, given QA-ENGINE-005.
  - Add a **census manifest** (entity counts by class, EntityId set, per-holder totals, value totals) to the ADR-003 artifact contract, generated at extraction. Load-time loss is then detectable by comparison instead of by an oracle. QA-ENGINE-006 showed 9/11 corruptions escaping the hand-built oracle.

### MR-04 — Player-global RimWorld engine state has no canonical home
- **Severity:** Critical
- **Source:** [ACCEPTED] ADR-003 defines per-*Settlement* artifacts. ADR-008 covers caravans and world objects. [CANON] FR-028/029 (joining dissolves the personal faction), FR-176 (branch split), FR-045 (expulsion creates a new faction).
- **Failure scenario:** [INFERENCE]
  - In vanilla, some state is global per game or per player faction rather than per map: research progress, Ideoligion and precepts, world pawns of the player faction (kidnapped, traveling, in pods, banished), tales and history, storyteller state, royalty titles and permits, bonded relationships, quest state, and faction goodwill with NPC factions.
  - In a per-settlement artifact model, none of it belongs to a settlement.
  - Materializing settlement A then B in one client (G-Q1 sequential option) must merge or overwrite that state. A Worker materializing an offline settlement (Tactical) needs the owner's research and ideology for building and precept semantics.
  - On FR-028 join, the personal faction dissolves. What happens to its research and ideology is undefined.
- **Coverage:** Not covered. FINDING-08 of REVIEW-001 raised the global-state surface. ADR-003/007/008 absorbed custody, but not *player-global* state.
- **Minimum correction:**
  - [RECOMMENDATION] Add a **PlayerGlobalSegment** (per player / personal faction) to the ADR-003 canonical representation, with its own revision. Each materialization composes `PlayerGlobalSegment(owner) + MapSegment(target)`. Tactical Workers read the owner segment read-only unless the write-set explicitly includes it (e.g. a research or ideology development effect).
  - New product decision: what happens to research, ideology and other player-global state on faction join, expulsion and split (Section 6).

### MR-05 — Settlement genesis authority is missing (the first artifact has no parent)
- **Severity:** High
- **Source:** [CANON] FR-008/010 (new player → personal Tribe). No SRS or ADR text defines who creates the **initial colony** (scenario, starting pawns, starting items) or a later settlement founding. [ACCEPTED] ADR-003 §7 (checkpoints are hostile), MSR-042 correction 2 ("current-parent forged state remains the central G-Q2 vulnerability").
- **Failure scenario:** [INFERENCE] The first canonical artifact of a player is, by default, a vanilla new-game created on the client. It has no `CheckpointParentRevision` to compare against, so it is the *least* verifiable checkpoint in the system. A modified client can start with arbitrary silver, pawns or archotech gear, which then feeds Auto-Shop, Tier wealth (FR-015) and the NPC market (FR-214). Settlement founding also decides the `LocalClockId` assignment, which is a hidden G-Q1 answer.
- **Coverage:** Not covered.
- **Minimum correction:**
  - [RECOMMENDATION] A short "Settlement Genesis" contract inside ADR-003/007. Genesis artifacts are produced by a **server-controlled engine** from a server-approved scenario, or at least validated against scenario bounds.
  - Settlement founding is a server-authorized custody transfer from caravan to new settlement (ADR-008 egress), with an explicit LocalClockId assignment rule left open behind G-Q1.

### MR-06 — Pipeline durability: WAL + `synchronous=NORMAL` is not durable for canonical commits
- **Severity:** Critical (cheap to fix now, very expensive to fix after real economy data)
- **Source:** [DEV-E1] Slice-01 header "Synchronous: NORMAL/FULL", E1_13 "Synchronous='1' (NORMAL)". QDL-040 attack 6.
- **Failure scenario:** [INFERENCE, SQLite documented behaviour]
  - In WAL mode with `synchronous=NORMAL`, a committed transaction survives an *application* crash, but can be **rolled back by OS crash or power loss**, because the WAL is not fsynced at each commit.
  - E1's hard-crash tests (`Environment.FailFast`) are process crashes, so they **cannot distinguish NORMAL from FULL**.
  - Sequence: a trade commits, the receipt goes to the buyer and an outbox letter is delivered, then the host loses power. On restart the commit is gone. The client holds a receipt for an operation the server never committed. Later idempotent replay of the same OperationId re-executes against a different head.
  - `PRAGMA synchronous` is **per connection**. A pooled connection that missed the pragma runs at a different level, which explains a "NORMAL & FULL" report.
- **Coverage:** Not covered. E1 cannot detect it.
- **Minimum correction:**
  - [RECOMMENDATION] For the canonical DB, `journal_mode=WAL` + `synchronous=FULL`, set in the connection-open path for **every** connection and asserted at startup. Fail startup if it is not in effect.
  - Do not release a receipt or deliver any outbox effect before `Commit()` returns under FULL.
  - Document the remaining risk (disk write caches) as an operations requirement.
  - Add an E2 test that verifies the pragma on every connection obtained from the pool.

### MR-07 — Operation identity: incomplete fingerprint, non-canonical hashing, global OperationId namespace
- **Severity:** High
- **Source:** [ACCEPTED] ADR-001 §2.9, ADR-004 §2 (identity includes scope, expected revisions, principal, type, profile, config snapshot). [DEV-E1] Slice-01 §2.6 step 1 ("compute/verify SHA-256 PayloadHash"), `OperationRecords` stores `ProbeScopeId/ExpectedProbeRevision/ActorId/ContentProfileFingerprint` as separate columns. QDL-040 attack 1.
- **Failure scenarios:** [INFERENCE]
  1. **Envelope gap.** If `PayloadHash = SHA256(PayloadJson)` and scope, revision, actor, type and profile live outside the payload, then reusing an OperationId with the same payload but a different scope returns `ALREADY_COMMITTED` with **another scope's receipt**. The caller believes scope B was updated.
  2. **Non-canonical JSON.** Hashing raw JSON bytes makes a semantically identical retry with different key order or whitespace (a client library update, or a resend through a different serializer) a false `COLLISION_REJECTED`.
  3. **"compute/verify"** suggests the client may supply a hash. A client-supplied hash is meaningless for authority.
  4. **Global PK namespace.** `OperationId` is a global PK and clients choose UUIDs. A malicious client that learns or guesses another player's OperationId can squat it, causing a later collision or denial, or replay it with the same payload and receive the **other principal's receipt** (information leak).
  5. **ABORTED retry semantics are unspecified.** Step 2 handles COMMITTED/PUBLISHED/PREPARED only. If an ABORTED (stale) OperationId can be retried and later commits, the client sees "stale" and then "committed" for the same id.
- **Coverage:** Partially. ADR-004 lists the fields, but the implementation hash scope is unknown.
- **Minimum correction:** [RECOMMENDATION]
  - `RequestFingerprint = SHA256(canonical serialization of {OperationType, SchemaVersion, PrincipalId, TargetScopes[], ExpectedRevisions[], ContentProfileFingerprint, ConfigSnapshotRef, typed payload})`, computed **server-side from the parsed typed DTO**, not from raw bytes.
  - Make identity `(PrincipalId, OperationId)`. A different principal reusing the id is rejected without revealing existence.
  - ABORTED is terminal: a same-fingerprint retry returns the stored ABORTED result, and a new attempt requires a new OperationId.

### MR-08 — Coordinator ↔ Reconciler race and unconditional state transitions
- **Severity:** High
- **Source:** [DEV-E1] Slice-01 §2.6 (the CAS-failure path calls `tx.Rollback()` and then `_journal.UpdateState(..., ABORTED, ..., conn)` **outside** the transaction). §2.7 (the reconciler runs at startup *and as a background scanner*, and "autonomously completes commit" for PREPARED).
- **Failure scenario:** [INFERENCE]
  1. The request thread writes PREPARED (step 4) and stalls (GC pause, lock wait).
  2. The background reconciler finds the PREPARED record, sees the expected revision matches, and commits: revision advances, receipt is inserted, state = COMMITTED.
  3. The request thread resumes, opens its transaction, and its CAS fails because the revision moved. It rolls back and **unconditionally overwrites the state to ABORTED**, then returns STALE to the client.
  4. Durable state now has an advanced revision and a receipt alongside an operation record that says ABORTED. The client was told STALE for an operation that committed.
  5. The same overwrite can happen with crash timing alone: a crash between rollback and the ABORT update leaves PREPARED, which the reconciler later aborts. That case is harmless. The unconditional overwrite is the bug.
- **Coverage:** Not covered by E1 (E1_07 tests crash-then-reconcile serially, not concurrently).
- **Minimum correction:** [RECOMMENDATION]
  - All journal transitions are compare-and-set on state: `UPDATE ... SET State=@new WHERE OperationId=@id AND State=@expected`. Zero rows means re-read and return the actual terminal result.
  - The CAS-failure path must first check whether *this* operation already committed (receipt exists).
  - PREPARED ownership: either the background reconciler only adopts PREPARED rows older than a lease/TTL owned by a dead process instance (`OwnerInstanceId` + heartbeat), or there is exactly one in-process commit executor (see Section 3, the single-writer simplification).
  - Optionally add DB `CHECK`/trigger constraints for legal transitions.

### MR-09 — The probe's PREPARED is not a reservation, so E1 does not test ADR-004 PREPARED semantics; for single-scope ops PREPARED is unnecessary
- **Severity:** High (risk of false confidence and wrong reuse)
- **Source:** [ACCEPTED] ADR-004 §4 and Clarification 2 (PREPARED = durable reservation with ordering, expiry and recovery ownership). [DEV-E1] Slice-01: PREPARED is a row in `OperationRecords`. Nothing in the report says a PREPARED probe op blocks other ops on the same `ProbeScopeId`. E1_05 shows concurrent ops resolving purely through CAS.
- **Failure scenario:** [INFERENCE] Future slices copy the probe pattern assuming "PREPARED = locked". A multi-scope custody transfer (ADR-008 ingress, Occupy) then PREPAREs while another operation commits on one of the scopes. The commit-time CAS catches it (good), but the reservation guarantee ADR-004 relies on (no conflicting publication while undecided, ADR-004 Clarification 4) was never implemented or tested. Meanwhile, for a single-scope typed operation, a separate PREPARED write before a single atomic SQLite transaction adds one more crash state and buys nothing.
- **Coverage:** Not covered. The E1 classification "PREPARED/COMMITTED/PUBLISHED lifecycle proven" overstates what was tested.
- **Minimum correction:** [RECOMMENDATION]
  - **Two paths.**
    - *Fast path* (single-scope typed op): one IMMEDIATE transaction inserts the operation record, CAS, receipt, audit and outbox. No PREPARED.
    - *Reservation path* (staged material, multi-scope, multi-party): a PREPARED row plus `ScopeReservations(ScopeId UNIQUE, OperationId, ExpiresAtW, OwnerInstanceId)`, all acquired **in one transaction**.
  - With SQLite's single writer, acquiring all reservations atomically in one transaction makes ADR-004's "deterministic lock ordering to avoid deadlocks" unnecessary.
  - The probe should add a two-scope reservation variant before E2 claims PREPARED semantics.
- **Q7: when may PREPARED auto-forward?** Only if **all** of the following hold:
  - (a) the operation type is on an explicit autonomous-completion allowlist;
  - (b) the durable package is complete and its stored fingerprint recomputes from the stored typed payload;
  - (c) every staged artifact it references exists and its hash verifies;
  - (d) every expected revision still equals the current revision;
  - (e) authorization is **re-evaluated at commit time** against current state (session not revoked/banned, ownership epoch unchanged, diplomacy revision per op contract);
  - (f) the reservation has not expired (measured in W or monotonic time, never wall clock);
  - (g) the writer lease / fencing generation it bound is still current;
  - (h) no newer operation from the same principal on the same scope supersedes it.
  - Otherwise ABORT. Multi-party consent operations never auto-forward.

### MR-10 — Outbox model: state conflation, double delivery, no ordering or cursor
- **Severity:** High
- **Source:** [DEV-E1] Slice-01 §2.5–2.7 (one status column per entry; inline delivery in step 6 plus reconciler replay; operation becomes PUBLISHED when the outbox is delivered). [ACCEPTED] ADR-004 §4 (`PUBLISHED/APPLIED` = "artifact watermark and projections updated"). ADR-005 §8 (ordered per-session domain event stream with ACK/replay).
- **Failure scenarios:** [INFERENCE]
  1. **Terminology collision.** The probe's PUBLISHED means "outbox delivered". ADR-004's PUBLISHED means "artifact/projection applied". Real operations have several derived effects (projection, N clients, Worker, letters). One operation state cannot represent N independent deliveries.
  2. **Double delivery.** Inline and background delivery of the same PENDING row race. E1 tests serial replay only.
  3. **No order.** ADR-005 requires strict per-session ordering by diplomacy revision. A status-flag outbox with retries reorders deliveries.
  4. **Unbounded growth.** Delivered rows are never compacted, which matters on a long-running server.
- **Coverage:** Partial. E1_11 proves replay does not re-advance the revision, which is necessary but not sufficient.
- **Minimum correction:** [RECOMMENDATION]
  - Replace push-with-flags by an **append-only event log with a monotonic sequence per stream** (`StreamId, Seq`). Each consumer keeps its own durable cursor and dedupes by `(StreamId, Seq)`.
  - Operation terminal state is COMMITTED. Delivery progress lives per consumer, not on the operation.
  - Retention and compaction policy goes in the outbox spec.
  - This one primitive serves ADR-005 SessionDomainEventLog, ADR-008 world projection deltas, client letters (FR-156/209/229) and audit export.

### MR-11 — Store incarnation: backup restore resets fencing generations and revisions
- **Severity:** High
- **Source:** [ACCEPTED] ADR-001 §2.8 (durable persistence), ADR-007 (`FencingGeneration` monotonic and server-issued), ADR-006A §8 (resume from last durable W). No backup/restore contract exists anywhere.
- **Failure scenario:** [INFERENCE]
  - The operator restores yesterday's DB after corruption. Monotonic counters go back: FencingGeneration 7 → 5, and revisions and W regress.
  - A Worker or client still holding generation 7 from before the restore now looks **newer** than any lease the server issues next (6), so stale writers pass fencing.
  - Clients hold receipts for operations that no longer exist. Artifacts in the file store are newer than the DB references, or (if the file store is restored separately) older, which puts many settlements into REPAIR_REQUIRED at once.
- **Coverage:** Not covered.
- **Minimum correction:** [RECOMMENDATION]
  - A `StoreIncarnationId` (random, new on every restore or migration-rollback) included in every lease, fencing token, receipt and session. Any mismatch means reject and rematerialize.
  - Content-addressed, append-only artifact store, and backups taken DB-first (SQLite backup API / `VACUUM INTO`) followed by artifacts, so the artifact set is a superset.
  - A W restart rule: `W_restart ≥ max(W stamped on any committed op)`.

### MR-12 — First real mutation is queued on an unimplemented Foundation
- **Severity:** High (sequencing)
- **Source:** QDL-040: QA-001 (identity/auth/version bypass), QA-002 (no server persistence), QA-005 (operation collision), QA-011 (partial frame / missing epoch fencing) are all **OPEN**. MSR-039: TradeConfiguration must "bind expected Settlement ownership identity/epoch and re-authorize at commit".
- **Failure scenario:** [INFERENCE] TradeConfiguration needs (a) an authenticated principal through ADR-001's lifecycle, (b) a canonical Settlement record with owner and ownership epoch, and (c) content-profile validation of referenced Defs (ADR-006B admission). None of these exists in Production. The slice will either stub them, embedding throwaway auth and ownership models that become hidden contracts, or grow into an unplanned Foundation slice without its own gate.
- **Coverage:** Not covered by the sequencing (MSR-039/043).
- **Minimum correction:** [RECOMMENDATION] Insert ADR-001 Foundation (auth/session/handshake/profile admission/framing epoch fencing/durable W) and Player + personal Faction + Settlement registry slices before TradeConfiguration (Section 5).

### MR-13 — "Server-controlled engine" sprawl: six roles, no owner, one shared blocker
- **Severity:** High
- **Source:** The accepted ADRs separately require a server-controlled RimWorld engine for:
  1. ADR-003 §7 layer-2 semantic validation;
  2. ADR-006B §5 profile approval / semantic load;
  3. ADR-006B §8 content migration;
  4. ADR-008 §3 pathing executor (candidate);
  5. ADR-008 §4 transit physiology (G-Q12b candidate);
  6. ADR-008 §7 engine-backed tax substitution;
  7. plus ADR-002 Tactical Worker (and MR-05 genesis).
  [E2] QA-ENGINE-002 (semantic loss reaches READY) and QA-ENGINE-006 (oracle misses 9/11 corruptions) are open.
- **Failure scenario:** [INFERENCE] Each role grows its own loader, fence, profile binding and validation. The validator then accepts an artifact that the Tactical Worker loads differently, or migration produces an artifact the validator would reject. QA-ENGINE-002 is filed against ADR-002 (Tactical), but it is really a defect of the **shared engine-hosting primitive**: every role above inherits it.
- **Coverage:** Not covered. No ADR or WP owns an "Engine Host".
- **Minimum correction:** [RECOMMENDATION]
  - Name one **Engine Host** component (single materialization loader, single load fence, single census/semantic validator, profile binding, lease client) that all roles are thin modes of.
  - Re-file QA-ENGINE-002/006 as Engine Host blockers that gate every role, not only Tactical.
  - No new ADR is needed; an implementation-boundary note in ADR-003 suffices.

### MR-14 — Per-Settlement writer lease quietly encodes a G-Q1 answer
- **Severity:** High
- **Source:** [ACCEPTED] ADR-007 §2 (lease binds `SettlementId` + `LocalClockId` + holder). ADR-006A §5 (one LocalClockId has one writer; one island has one clock). MSR-040 correction 6.
- **Failure scenario:** [INFERENCE]
  - Under G-Q1 Option A (player-scoped clock, the most vanilla-like), one `LocalClockId` spans several settlements. Under per-settlement leases, that is several leases on one clock, i.e. "multiple writers" for one clock unless the holder is defined as the island.
  - Barriers (MR-02) and handoffs would freeze one lease while the island keeps advancing the shared clock.
  - The current interface therefore favours Options B/C/D without saying so.
- **Coverage:** MSR-040 says the per-settlement lease is "the correct stable deferral interface". Reviewer disagrees.
- **Minimum correction:** [RECOMMENDATION] Key the lease on the **execution island / LocalClockId** with a *set* of settlement scopes (cardinality 1 for options B/C/D, ≥1 for A). Barriers and fencing apply to the island lease. This keeps G-Q1 genuinely open.
- **Vanilla-first test of G-Q1:** [INFERENCE] ADR-006A §2 says L_s identity "must remain stable **or explicitly migrate**". ADR-008 already requires TransitClock ↔ L_s anchor reprojection. So Option A (vanilla multi-map with a player-scoped clock; conquest = explicit clock migration plus reprojection) is *already permitted* by the accepted text and reuses a codec you must build anyway. It is the vanilla-first default that should be falsified first, before virtualization or multi-process islands.

### MR-15 — Wealth/Tier protection is circular under current-parent forgery
- **Severity:** High
- **Source:** [ACCEPTED] MSR-042 correction 8 ("server must derive/validate promotion input from an accepted canonical projection or separately protected evidence path"). Correction 2 (current-parent forgery undetectable by lineage). [CANON] FR-015/017 (auto-promotion), FR-034/054/110 (Tier/Title drive limits, borders, WarPending).
- **Failure scenario:** [INFERENCE] The "accepted canonical projection" is *derived from accepted owner checkpoints*. A forged-but-valid current-parent checkpoint passes layers A and C, so the projection faithfully reports forged wealth and auto-promotion fires. The phrase "derive from canonical projection" sounds protective but is not, unless layer D (plausibility) exists for exactly these fields.
- **Coverage:** Framed (Layered Trust), but no layer-D control is designed or scheduled.
- **Minimum correction:** [RECOMMENDATION] Before Tier evaluation or any trade *execution* reaches Production, define an **economic firewall**:
  - The fields that cross from client-authored state into shared/political state (Tier wealth input, pawn count, Auto-Shop sell quantities, tax-seizable value) pass rate/plausibility bounds relative to the last server-witnessed state.
  - Tier promotion uses a lagged, bounded wealth figure.
  - Thresholds stay Master policy (G-Q2). The *existence* of the control point is architecture.

### MR-16 — Committed typed ops may be unapplicable at materialization, making REPAIR_REQUIRED a de facto immunity
- **Severity:** Medium
- **Source:** [ACCEPTED] ADR-008 §7 / Clarification 7 (engine-free commit from projection when facts suffice). ADR-003 §4 (replay committed ops > watermark). ADR-006B §6 (no defender immunity).
- **Failure scenario:** [INFERENCE] An offline trade commits "remove 50 steel" against the projection. At the next materialization the engine finds 49, because of an index extraction bug, deterioration accounting, or a stack in a container the index counted differently. Replay fails, the settlement goes REPAIR_REQUIRED, and Tactical admission against it is impossible until an operator acts. Repeated, this is attack immunity.
- **Coverage:** Not covered beyond "REPAIR_REQUIRED".
- **Minimum correction:** [RECOMMENDATION]
  - An **application-totality invariant**: a typed op may be committed engine-free only if its engine application is total given the index facts.
  - Index facts must come from the same census used for artifact validation (MR-03).
  - Define a bounded automatic degrade, e.g. apply with shortfall compensation recorded as a typed compensating op, and audit it, rather than blocking the settlement.
  - Whether a shortfall compensates the buyer is product policy.

### MR-17 — Revision/identifier proliferation
- **Severity:** Medium
- **Source:** ADR-003 §4 (5 settlement revisions), ADR-007 (lease base revision, FencingGeneration), ADR-008 (World/WorldObject revisions), ADR-006B (ContentProfileRevision, ConfigRevision), ADR-005 (diplomacy scope revisions), MSR-039 (TradeConfigurationRevision), Slice-01 (ProbeRevision), plus SessionEpoch, WorkerGeneration, TransportEpoch and ownership epoch.
- **Failure scenario:** [INFERENCE] Each new aggregate gets bespoke version plumbing and bespoke CAS code, so fencing bugs multiply (QA-PRESENT-007/H05-01 is already one).
- **Minimum correction:** [RECOMMENDATION]
  - One `Aggregates(AggregateType, AggregateId, Version)` primitive with a single CAS helper. Typed names exist only in code.
  - One `FencingToken = (StoreIncarnationId, LeaseKind, Generation)` type shared by sessions, leases, Workers and transports.
  - Keep the ADR names. Do not implement them as separate mechanisms.

### MR-18 — Evidence allocation is inverted relative to risk
- **Severity:** Medium (process, high rework leverage)
- **Source:** MSR-021..041: six presentation hardening/QA rounds (including dynamic facing, QA-PRESENT-011) versus zero runtime work on settlement artifact round-trip, live-client barrier cost, or player-global state. MD-014: one independent verifier (Sol).
- **Failure scenario:** [INFERENCE] P2 presentation is valuable, but it is not the falsification point of the material architecture. If MR-03 fails (artifact round-trip impractical), the accepted ADR-003/004/007/008 set needs revision. Facing correctness does not reduce that risk.
- **Minimum correction:** [RECOMMENDATION] Freeze presentation at its current E2 state, except for H05-01 (a fencing correctness bug). Redirect engine capacity to PoCs E-A/E-B (Section 5).

### MR-19 — Context-recovery documents are internally inconsistent
- **Severity:** Medium
- **Evidence:**
  - MSR-043 §7 "ADR Status" still lists ADR-003/004/005/006B/007/008 as **NOT YET AUTHORED**, and §10 "Current Active Work" is the MSR-004 text. Only the appended deltas (§44) give the true state. The Context-Recovery Rule (§11) points readers at this file.
  - The `ADR-005` file header says **"Status: PROPOSED (Not Accepted)"** and has no Master acceptance section, while MSR-033/MD-045 say ACCEPTED.
  - The `ADR-007` file is named v5 but its header says v4.
  - ADR-004/005/006B/008 contain residual `[cite: N]` markers referencing no supplied source.
  - ADR-005 says "G-Q13 through G-Q18" but defines 13..17.
  - ADR-003 §2 says the projection is "completely rebuildable from artifact plus committed operations", which ADR-004 Clarification 8 overrides.
- **Failure scenario:** An agent recovering context from the files reconstructs the wrong ADR status. This is the exact purpose the files serve.
- **Minimum correction:** Rewrite MSR §7/§10 as current state (move history to an appendix). Stamp the ADR-005 acceptance into the file. Strip citation artifacts. Fold acceptance clarifications into the ADR bodies.

### MR-20 — Probe code ships in the Production server binary
- **Severity:** Low
- **Source:** [DEV-E1] Slice-01 §2.8 (isolation by "no packet type" plus `InternalProbeTestSurface` runtime denial).
- **Minimum correction:** [RECOMMENDATION] Exclude probe and test surfaces at build time (separate assembly or `#if`), or restrict them to the admin console channel (FR-230 class). E2 should still inspect real dispatch, as MSR-043 asks.

---

## 3. Architecture Simplifications

### 3.1 Reuse SQLite / .NET instead of custom infrastructure

| Instead of | Use | Why |
|---|---|---|
| Deterministic multi-scope lock ordering (ADR-004 §4) | One `BEGIN IMMEDIATE` transaction acquiring all `ScopeReservations` rows (UNIQUE(ScopeId)) | SQLite has a single writer, so all-or-nothing acquisition cannot deadlock |
| Concurrent coordinators racing on CAS | A **single commit executor** (one writer thread fed by `System.Threading.Channels`). CAS still validates *client* expectations | SQLite serializes writers anyway. One executor removes the coordinator/reconciler race (MR-08) and SQLITE_BUSY handling |
| Hand-rolled state-machine guarding | Conditional `UPDATE ... WHERE State=@expected`, plus `CHECK` constraints / triggers on legal transitions, `STRICT` tables | Invariants are enforced by the DB, and E2 can test them directly |
| Idempotency lookups in code | `INSERT ... ON CONFLICT DO NOTHING RETURNING` on `(PrincipalId, OperationId)` | Atomic dedupe inside the commit transaction |
| Ad-hoc migration | Transactional DDL (SQLite DDL is transactional) in one transaction per migration step, `PRAGMA user_version`, and `PRAGMA application_id` to refuse wrong DB files | Partial migration becomes impossible (QDL-040 attack 9) |
| Custom backup | SQLite Online Backup API / `VACUUM INTO`, then copy the append-only artifact store | Consistent superset backups (MR-11) |
| Push outbox with status flags | Append-only stream table plus per-consumer cursors (MR-10) | One mechanism for ADR-005/008, letters and audit |
| Wall-clock expiry | Monotonic time (M) for process liveness, W for domain expiry | ADR-006A already separates these. Wall-clock jumps must not mass-expire reservations |

### 3.2 Reuse vanilla RimWorld

| Area | Vanilla mechanism to reuse | Custom part that remains |
|---|---|---|
| Multi-settlement (G-Q1) | Vanilla multi-map in one game with a player-scoped clock, if Option A survives PoC E-A/E-B | Clock migration on conquest/transfer (reprojection codec already required by ADR-008) |
| Intent/betrayal facts (ADR-005) | [INFERENCE] `DamageInfo.Instigator`/`Weapon`, `Projectile.launcher`/`intendedTarget`, the vanilla faction "member took damage" goodwill hooks and `HistoryEvent` records already attribute damage and intended target | Server-side rule evaluation and envelope provenance. Generate `FactId`s from these hooks; do not build parallel causality tracking first |
| World pathing (ADR-008 §3) | Do not reimplement vanilla world-path math. Export the world tile-cost/road/river table once per content profile from an Engine Host, then run A* on the server against that table, re-exporting when season/biome modifiers change | Season-dependent cost refresh. Validate equivalence once per profile, not continuously |
| Trade/Tax UI | `Dialog_Trade` with custom `ITrader`/`Tradeable` (NFR-010) | Server-backed availability |
| Conditional peace | Vanilla Quest UI for presentation only | Timer on server W (ADR-006A §9) |
| Factions in client/Worker worlds | Vanilla `Faction` objects instantiated from the ADR-008 registry projection | Stable EntityId ↔ loadID binding |
| Settlement founding | Vanilla settle flow, intercepted to become a server-authorized custody op (MR-05) | Genesis contract |
| Letters/messages | Vanilla Letter/Message stack fed by outbox streams | — |

### 3.3 Delete or postpone

- **PREPARED on single-scope typed ops**: delete (MR-09).
- **Operation-level PUBLISHED state**: delete; track delivery per consumer (MR-10).
- **"Deterministic server implementation of RimWorld movement math"** as an ADR-008 candidate: drop in favour of the exported cost table.
- **General-purpose projection/index**: build only the fields an implemented feature needs (FR-204 fungible quantities, Tier inputs). Do not mirror the RimWorld object model server-side (REVIEW-001 collapse risk).
- **Further presentation polish** beyond H05-01 until the material-path PoCs report (MR-18).
- **Cosmetic Capability Profile machinery** (ADR-006B §9): postpone. Ship "exact gameplay profile, no client-only mods" first. It is a valid strict default, and the ADR permits the cosmetic path without requiring it.

---

## 4. Pipeline Slice-01 Review

### 4.1 What E1 actually proves (developer evidence only)
- [DEV-E1] Within one process, an SQLite transaction can atomically combine a CAS update, journal state, receipt, audit row and outbox row. Rollback before `Commit()` discards all of them.
- [DEV-E1] Process termination (`FailFast`) at three chosen points yields DB states that the reconciler resolves to the expected end state, **serially** after restart.
- [DEV-E1] Same id + same payload returns the stored receipt, and same id + different payload is rejected, **for the payload field only**.
- [DEV-E1] In-process tasks contending on one expected revision produce one winner.
- [DEV-E1] The gameplay packet table has no probe packet type.

### 4.2 What E1 does not prove
| Gap | Why it matters |
|---|---|
| Durability under OS crash / power loss | `synchronous=NORMAL` is indistinguishable from FULL in process-kill tests (MR-06) |
| Kill *inside* `Commit()` | Only "before" and "after" fault points were exercised |
| Concurrency between request path and background reconciler | MR-08 race is untested |
| Multi-process / multi-connection contention | In-process tasks may share connection pooling semantics. Real Production has one process, but multiple connections and the reconciler |
| PREPARED as reservation | Not implemented (MR-09) |
| Fingerprint completeness / canonical hashing / principal scoping | MR-07 |
| Outbox duplicate effect at the consumer | The dispatcher is presumably a no-op, so the "exactly-once effect" boundary is untested |
| Ordering of outbox deliveries | Required by ADR-005 |
| Disk-full / IO error at commit | Outcome classification on `Commit()` exception is untested |
| Startup ordering | Recovery must complete before gameplay admission opens |
| Anything distributed | No second durable store (artifact files), no lease, no external participant, no engine. The ADR-004 hard cases (staged artifact + DB pointer, torn artifact write, promotion validation) are untouched |

[INFERENCE] **Q5 answer:** the probe is a good *first* substrate test, but it proves SQLite mechanics only. It does not exercise the property that makes ADR-004 hard: **two durable stores (DB + artifact files) plus an external writer under a lease**. A second probe is needed before any real material mutation (Section 5, Slice P2).

### 4.3 Mandatory E2 attacks (in addition to QDL-040 items 1–9)
1. **Durability policy:** dump `PRAGMA journal_mode/synchronous` from *every* pooled connection and from the reconciler. Fail if any canonical write path runs below FULL. Optionally run a VM power-cut test (hard reset of a VM or `dm-flakey`-style) to show commit survival.
2. **Fingerprint envelope:** QDL-040 item 1, plus semantically identical JSON with different key order/whitespace must be **accepted as a replay**, not as a collision. Supplying a forged client hash must have no effect.
3. **Principal scoping:** principal B reusing principal A's OperationId with an identical payload must not receive A's receipt and must not learn whether it exists.
4. **ABORTED retry:** retry after STALE must return the stored ABORTED result and never commit later.
5. **Coordinator/reconciler race:** inject a delay between PREPARED and the commit transaction while the background reconciler runs. Assert no journal state contradicts receipt/revision. Repeat 1000× with randomized delays.
6. **Kill inside commit:** kill the process repeatedly with random timing around `Commit()`, using an external `kill -9` loop rather than in-process fault points. Assert that the state is always either fully committed or fully absent, and that a client retry converges.
7. **Commit exception classification:** simulate `SQLITE_FULL`/`SQLITE_IOERR` at commit. The coordinator must re-read durable state before replying, and must never reply COMMITTED on an exception.
8. **Outbox double delivery:** run inline delivery and the background reconciler concurrently on the same entry with a counting consumer. Then crash after the consumer effect and before the DELIVERED marker. Assert the consumer dedupes by `(StreamId, Seq)` or `OutboxId`.
9. **Outbox ordering:** 100 ops on one scope with randomized delivery failures. The consumer must observe a gap-free order or explicitly buffer.
10. **Startup gating:** start the server with pending PREPARED and outbox rows. Prove gameplay admission stays closed until the reconciler finishes. Prove a failed migration leaves the DB at the old `user_version` and refuses to start.
11. **Isolation in source:** static inspection of the actual dispatch table and reflection paths, plus a release-build check that the probe is absent or unreachable (MR-20).
12. **Two-scope variant (if implemented):** reservation acquisition is atomic, and an expired reservation is released only by its owner instance or after its owner is dead.

### 4.4 Q8: what the fingerprint must bind
Yes. The fingerprint must bind `OperationType` and schema version, `PrincipalId`, every target scope, every expected revision, `ContentProfileFingerprint`, config snapshot reference (ADR-006B §7), and the typed payload. Compute it server-side over a canonical serialization. `OperationId` is unique per principal. W/time stamps and SessionEpoch must **not** be in the fingerprint, so a legitimate retry from a reconnected session still dedupes. Re-check session validity as authorization, not as identity.

---

## 5. Production Sequence Review

### 5.1 Q9: is TradeConfiguration a sound next step?
[INFERENCE] **Sound in content, wrong in position.**
- Policy risk is low and its FR scope (FR-197..203, BR-019) is well chosen.
- Architectural yield is low. It is a single-aggregate CRUD that exercises none of: material state, lease, barrier, EntityId, Engine Host, artifact store or outbox fan-out to many consumers.
- It depends on two things that do not exist yet: an authenticated principal and a canonical Settlement/ownership-epoch record (MR-12).
- Run it after Foundation + registries. It then becomes a cheap confirmation slice.

### 5.2 Q10: better first real mutations
| Candidate | SRS | Policy risk | Evidence produced |
|---|---|---|---|
| **Player registration + personal Faction creation** | FR-004/005/008/009/010/011/013, FR-234 | None (no TBD/G-Q) | ADR-001 principal mapping, aggregate creation with uniqueness constraints (color distinctness FR-011, name), Faction EntityId registry (ADR-003 §6), registry projection fan-out to every client (ADR-008 §5) through the new outbox stream, audit. **Everything else depends on these entities** |
| **Kick/Ban** | FR-230/231/232 | None | Admin channel, session revocation → fencing (ADR-001 §2.4), durable ban by PlayerId, NFR-006 |
| **Alliance request / accept / reject / cancel** | FR-133/134/139, ER-001-like late-accept race | Low (no TBD) | Multi-party consent state machine (the "live consent lost → ABORT" rule of ADR-004 §6), W-based cooldown with config snapshot (ADR-006B §7), DiplomacyScope aggregate (ADR-005 §5), fan-out to two factions. It is the same race class as QA-009 (Visit cancel/accept) |
| TradeConfiguration | FR-197..203 | Low | Single aggregate CRUD + ownership-epoch fence |

### 5.3 Recommended sequence (from today)

```
NOW (parallel tracks)
 ├─ P-track (Production, server only)
 │   Slice P1  Pipeline Slice-01 corrections + E2
 │             (MR-06 FULL sync, MR-07 envelope/principal, MR-08 conditional transitions /
 │              single executor, MR-09 fast path, MR-10 stream outbox, MR-11 StoreIncarnationId,
 │              MR-20 build exclusion)
 │             GATE: E2 passes items 4.3 + QDL-040 1–9 on the corrected frozen build.
 │
 │   Slice P2  ADR-001 Foundation
 │             auth (Steam ticket / fallback policy), session lifecycle, SessionEpoch,
 │             handshake + ContentProfileFingerprint admission (ADR-006B §4),
 │             frame integrity + epoch fencing (QA-011), durable W clock + restart rule,
 │             startup recovery gating.
 │             GATE: QA-001/002/005/011 closed with E2; fencing-token type shared (MR-17).
 │
 │   Slice P3  Player + personal Faction + Kick/Ban + Faction registry stream
 │             GATE: E2 incl. outbox fan-out ordering/dedupe with ≥3 real client consumers,
 │             restart mid-fan-out, ban → session fenced.
 │
 │   Slice P4  Alliance request/accept/reject/cancel (+ cooldown W, config snapshot)
 │             GATE: E2 late-accept / cancel race, restart during pending request,
 │             config change across restart does not alter snapshotted cooldown.
 │
 │   Slice P5  Settlement registry (metadata only, created by test/admin fixture until genesis)
 │             + TradeConfiguration (as queued, with ownership-epoch fence).
 │             GATE: E2 ownership-epoch race; content-profile Def validation; FR-201/BR-019 no clamp.
 │
 └─ E-track (engine PoCs, scratch, not Production) — start now, report before any material slice
     E-A  Settlement artifact round-trip into a synthetic minimal world, with census manifest,
          two divergent LocalClockIds loaded sequentially in one client (absorbs G-Q1 probe A/B),
          PlayerGlobalSegment composition (MR-04).
     E-B  Live-client barrier cost: freeze + extract one settlement from a running
          client on a large colony; measure hitch, upload size; apply a server delta in-engine;
          repeat at 1/10/60 s cadence.  (Decides MR-02, informs G-Q6.)
     E-C  WAN P2: existing presentation candidate under injected latency/jitter/loss
          (e.g. 80/150/250 ms RTT, 1–3% loss).  (Decides G-Q10, informs Contrarian.)

STOP/GO before ANY material-state Production slice (trade execution, tax, checkpoint
acceptance, genesis, Tactical publication):
  - E-A PASS (zero census loss on engine-generated complex fixture; loss detection proven
    on deliberately corrupted fixtures, i.e. QA-ENGINE-002/006 class),
  - E-B result reviewed and MR-02 barrier policy decided,
  - MR-01 / MR-04 / MR-05 / MR-14 decisions recorded,
  - Engine Host ownership assigned (MR-13).
Then: Slice P6 = Settlement Genesis via Engine Host (first real artifact + EntityId + census
projection), followed by offline Auto-Shop execution (needs G-Q8) and then online (needs MR-02).
```

### 5.3a Q17/Q18: PoCs needed now vs speculative

| Needed now (material uncertainty on the critical path) | Defer (speculative or not yet on the critical path) |
|---|---|
| E-A settlement artifact round-trip + census + PlayerGlobalSegment | Simultaneous multi-process islands (G-Q1 Option D), until E-A/E-B fail Option A/B |
| E-B live-client barrier/extract cost and in-engine delta application | Per-map clock virtualization (G-Q1 Option C) |
| E-C P2 under WAN impairment | Transit physiology executor (G-Q12b) |
| Loss-detection on deliberately corrupted artifacts (a slice of E-A, covering the QA-ENGINE-002/006 class) | Server pathing executor equivalence; content-migration engine; cosmetic capability validation; intent-aware AoE (CON-001 fallback exists); Storyteller-in-Tactical; deterministic replay of ordinary play (MSR-042 correction 7 already rejects it as a default); further presentation fidelity (health/job/facing breadth) |

### 5.4 Q14: is Tactical converging with ordinary materialization?
[INFERENCE] **Not yet. Two state systems are being built.**
- The Tactical Worker track (ENGINE-01/02, HARDEN-01) loads **full `.rws` worlds and filters ticks**.
- ADR-003 materialization is **artifact + committed-op manifest**.
- The P2 presentation candidate replicates via **custom per-field snapshot reconciliation**. QA-PRESENT-004 (general health/job reconciliation still failing) is the custom-serialization risk moved from persistence into replication.
- Convergence requires that the Tactical Worker be rebuilt to materialize from the same `MaterializationManifest` through the same Engine Host (MR-13), and that it emit staged results in the same artifact + census format.
- [RECOMMENDATION] Make that the explicit entry criterion for the next Worker WP. Further hardening of the full-save-filtering Worker is sunk cost.

### 5.5 Q15: defects that indicate architecture flaws
| Defect | Architectural reading |
|---|---|
| QA-ENGINE-002 (semantic loss reaches READY) | RimWorld's loader logs errors and continues, so loss detection cannot rely on load success. It needs an **independent census manifest** carried with the artifact (MR-03). This is an Engine Host primitive, not a Tactical bug (MR-13) |
| QA-ENGINE-005 / 001 / 004 (global dispatch and world drift) | "Full engine context + suppress" is inherently leaky. This argues for a **synthetic minimal world** context (MR-03) |
| QA-ENGINE-006 (oracle misses 9/11 corruptions) | The ADR-003 layer-2 and ADR-006B layer-3 "semantic validation" were accepted assuming an oracle that has not been shown to exist |
| QA-PRESENT-004 (general reconciliation failing) | P2 per-field replication will scale with vanilla+mod component count, the same collapse risk REVIEW-001 identified for field-merge |
| QA-PRESENT-007 / H05-01 (epoch relabeling) | Fencing is implemented ad hoc per transport. One shared fencing-token type is needed (MR-17) |
| QA-008 / QA-011 | Principal and epoch are not yet bound at the protocol layer. This is a Foundation prerequisite for every real mutation (MR-12) |

---

## 6. Open Decisions

### 6.1 Must decide now (blocks correct substrate or interface shape)
| # | Decision | Why now |
|---|---|---|
| D-1 | Canonical DB durability policy (`synchronous=FULL`, receipt release only after durable commit) | Retrofitting after real data is a migration of trust (MR-06) |
| D-2 | Operation identity = `(PrincipalId, OperationId)` + server-computed canonical fingerprint envelope; ABORTED terminal | Wire-protocol-visible (MR-07) |
| D-3 | Clarify ADR-004 §9 vs ADR-007 Phase B: what advances FencingGeneration | Contradiction between accepted ADRs (MR-01) |
| D-4 | Lease keyed on execution island / LocalClockId with a settlement-set scope; barriers island-scoped | Otherwise the interface embeds a G-Q1 answer (MR-14, MR-02) |
| D-5 | StoreIncarnationId + backup/restore contract + W restart rule | Must be in every token from day one (MR-11) |
| D-6 | Single PREPARED auto-forward rule (MR-09 conditions a–h) and fast-path vs reservation-path split | Every future op copies this |
| D-7 | Name the Engine Host as one component; re-file QA-ENGINE-002/006 against it | Prevents six divergent loaders (MR-13) |
| D-8 | Commit to PoC E-A/E-B/E-C before any material slice; freeze presentation polish except H05-01 | Evidence allocation (MR-18) |

### 6.2 Runtime evidence first (decide after the PoC reports)
| Item | Evidence needed |
|---|---|
| B2-lite artifact format and materialization context (full vs synthetic world) | E-A |
| G-Q1 multi-settlement topology (test Option A first, see MR-14) | E-A (sequential), then E-B |
| DELTA_BARRIER feasibility/policy (coalescing window, rate limits, timeout behaviour) | E-B |
| G-Q6 checkpoint cadence / disconnect grace | E-B |
| G-Q10 remote owner UX / WAN acceptance | E-C |
| G-Q8 SettlementEconomicInventory / TaxSeizableAssetSet / SettlementAssetGraph boundary | E-A census + targeted engine mutation tests |
| G-Q2 layer-D thresholds | E-A census deltas on real play sessions |
| G-Q12b transit physiology executor | Defer until caravan custody slice; Engine Host mode |

### 6.3 New product decisions created by this review (not TBDs and not resolved here)
| # | Question | Source |
|---|---|---|
| N-1 | On faction join (FR-028), expulsion (FR-045) and branch split (FR-176), what happens to the player's research progress, ideology and other player-global engine state? | MR-04 |
| N-2 | Does FR-207 "immediately" tolerate a bounded server-defined barrier window (e.g. trade shown as pending until the next barrier) when the owner is **online**? | MR-02 |
| N-3 | Genesis: is the initial colony generated by a server-controlled scenario, or client-generated and validated against scenario bounds? | MR-05 |
| N-4 | When a committed offline trade cannot be fully applied at materialization (shortfall), is the buyer compensated, or is the shortfall absorbed? | MR-16 |
| N-5 | *(Optional G-Q8 option for Master only, not adopted)* Should a server-custodied "trade depot" (goods moved out of the engine into server custody, like loading a caravan) be an allowed definition of SettlementEconomicInventory? It removes online barriers for trade, but may be judged a narrowing of FR-204, so it needs requirement authority. Tax (FR-191) would still need engine-backed seizure | MR-02 |

### 6.4 Safely deferrable (decide before the specific feature, not before the substrate)
G-Q4 (Tactical crash semantics), G-Q5b (Storyteller in Tactical), G-Q9 (Auto-Shop after Occupy), G-Q12a (transit physiology semantics), G-Q13..17 (betrayal liability), cosmetic capability profile, content-migration engine implementation, separate-process simultaneous islands. **Canonical TBD-01..05 remain OPEN**, each before its feature (TBD-05 before tax, TBD-03 before theft/betrayal, TBD-01 before faction join, TBD-02 before WarPending expulsion, TBD-04 before extinction).

### 6.5 Q11: are G-Q1/G-Q2/G-Q6 correctly deferred?
- **G-Q1:** Deferral is correct in principle, but the per-settlement lease and per-settlement barrier already embed a hidden answer (MR-14). Correct the interface (D-4), then defer.
- **G-Q2:** Correctly deferred for metadata slices. **Not** deferrable past genesis (MR-05) or trade execution (MR-15). The control point must exist even if thresholds are open.
- **G-Q6:** Correctly behind configuration. However, the ADR-007 §4 rule "timeout → fence → fall back to last committed head" is already a partial answer: it fixes the *loss semantics* and leaves only the duration open. Combined with MR-02 griefing, that semantics deserves review with E-B data.

### 6.6 Q12: does the owner-client WriterLease create a trust problem large enough to switch?
[INFERENCE] **Not by itself.** Forged current-parent state exists in any client-simulated design and is containable with an economic firewall (MR-15). The *stronger* reasons to reconsider server-hosted ordinary simulation are operational:
- barrier cost (MR-02);
- the multi-map clock problem (MR-14);
- Tactical/ordinary state-system convergence (5.4).
Those are decided by E-B and E-C, not by trust arguments. See Section 7.

### 6.7 Q13: are wealth/tier/economy decisions protected from hostile owner saves?
**No, not yet.** The current wording is circular (MR-15), and genesis is unguarded (MR-05). Neither blocks P1–P5. Both block Tier automation and trade execution.

---

## 7. Contrarian Alternative

### "Uniform Engine Host": every simulated settlement runs in an operator-controlled engine; every client is a P2 mirror

**Shape:**
- While a settlement's owner is online, or a session targets it, the settlement simulates in an operator-hosted Engine Host process: one process per active LocalClock island, or per player with a player-scoped clock.
- All clients, including owners during ordinary play, are non-authoritative P2 mirrors that send commands.
- Canonical state = Engine Host checkpoints. The process is operator-trusted, and only *commands* are hostile input.
- Offline settlements stay frozen as artifacts. The Engine Host materializes them on demand for attack, tax or trade.

**What it deletes:**
- Owner-checkpoint forgery (G-Q2 save-state authority disappears; command exploits remain).
- DELTA_BARRIER against a hostile client (the server applies deltas in its own engine).
- Client ↔ Worker HANDOFF_BARRIER (it is the same host).
- G-Q6 progress loss on client crash.
- Most of G-Q1 (islands are simply processes).
- The "engine-free offline trade" constraint (an engine is always available).
- The dual state system (5.4): Tactical, ordinary, validation, migration, transit and genesis become modes of one host.
- Genesis trust (MR-05).

**What it costs:**
- **Requirement conflict.** [CANON] SRS §4.2 assigns "Settlement Local Simulation" to the Client. This alternative cannot be adopted by architecture alone; it needs explicit Master/user requirement interpretation or amendment. **Not proposed as a silent change.**
- **Every vanilla interaction must become a remote command.** That covers bills, work priorities, zones, architect designators, storage filters and every mod gizmo. [INFERENCE] The existing RimWorld Multiplayer mod's sync-method/sync-field approach shows this is feasible but large, with a permanent per-mod compatibility burden. This is the biggest vanilla-first cost, and QA-PRESENT-004 shows reconciliation breadth is already the hard part.
- **WAN latency for all play, all the time.** G-Q10 then applies to every player, not only visits.
- **Server resources.** [INFERENCE] One RimWorld process per active island (order of 1–3 GB RAM and a core each). Viable for an operator-run server with tens of concurrent players (CON-005/007), not hundreds.

**When it is superior:**
1. E-B shows live-client barrier/checkpoint cost is unacceptable at realistic trade rates, **and**
2. E-C shows P2 is playable at target WAN latency, **and**
3. the target concurrent population is small enough to host, **and**
4. command-ification can be done generically (intercepting at Designator/Gizmo/Command/FloatMenu level) rather than per feature.

If (1) holds but (2) or (4) fails, the cheaper pivot is **N-5 (server-custodied trade depot)** plus a coalesced barrier for the rare tax case. That would keep owner-client simulation and remove the high-frequency barrier.

[RECOMMENDATION] Do not switch now. Make E-B and E-C produce exactly the numbers that decide between: current architecture, current architecture + depot, and Uniform Engine Host. Record the decision criteria in advance so the result cannot be rationalized afterwards.

---

## Appendix A — Top 10 Catastrophic Production Failure Paths (Q19, unranked)

| # | Failure path | Trigger | Consequence | Guard |
|---|---|---|---|---|
| 1 | Power loss after receipt release with `synchronous=NORMAL` | Host/VM crash | Receipts/letters for non-existent commits, replay divergence, duplicated goods | MR-06 |
| 2 | DB restore without incarnation change | Operator recovery | Stale Workers/clients pass fencing, economy time-travel | MR-11 |
| 3 | Fencing contradiction implemented two ways | ADR-004 §9 vs ADR-007 | Either every trade reloads the owner, or stale writers publish | MR-01 |
| 4 | Barrier storm / timeout fencing | Buyer spam on an online owner | Owner game freezes, progress discarded, griefing | MR-02 |
| 5 | Forged genesis or current-parent checkpoint | Modified client | Inflated wealth → auto Tier → political and economic distortion | MR-05, MR-15 |
| 6 | Player-global state lost or duplicated | Sequential materialization, faction join, Tactical | Research/ideology rollback or duplication, broken precept semantics | MR-04 |
| 7 | Validator false PASS + artifact fold + GC of the previous artifact | QA-ENGINE-002 class | Permanent silent entity loss | MR-03 census; retain the previous N artifacts until a census-verified fold |
| 8 | Unapplicable committed ops → REPAIR_REQUIRED | Index drift | De facto attack immunity, operator backlog | MR-16 |
| 9 | Engine Host divergence | Six separately built loaders | Validator/Worker/migration disagree on the same artifact | MR-13 |
| 10 | Coordinator/reconciler race | Load spike / GC pause | Journal says ABORTED while revision and receipt exist; client told STALE for a committed op | MR-08 |

Near misses: OperationId squatting and receipt leak (MR-07); outbox reorder breaking the ADR-005 diplomacy order (MR-10); recovery documents misleading an agent (MR-19); single-verifier bottleneck (MD-014).

## Appendix B — Q4: is B2-lite still the simplest viable model?
[INFERENCE] **Yes for storage and authority:** opaque engine artifacts + typed ops + small index, with no field merge. It needs three amendments to stay viable:
- the artifact is **segmented** (PlayerGlobalSegment + MapSegment) (MR-04);
- it carries a **census manifest** (MR-03);
- its materialization context is explicitly a **synthetic minimal world** (MR-03).

Without E-A it remains a hypothesis.

## Appendix C — Q2: over-specified ADRs likely to force rework
| ADR | Over-specification | Risk |
|---|---|---|
| ADR-004 §4 | Lock ordering, PREPARED for all ops | Unnecessary under SQLite single writer. Slows every op (MR-09) |
| ADR-004 §9 | Fencing advance on every commit | Contradiction (MR-01) |
| ADR-005 §2 | Five-level causality identity before any liability policy | Build from vanilla DamageInfo/Projectile facts first. Keep `FactId`, and defer the rest until G-Q13..17 |
| ADR-007 §2/§4 | Per-settlement lease and barrier | Embeds G-Q1 (MR-14) |
| ADR-008 §3 | "Deterministic server implementation of RimWorld movement math" as a candidate | Reimplementing vanilla. Use the exported cost table |
| ADR-006B §9 | Cosmetic capability model | Postpone. Exact-profile default suffices |
| ADR-003 §4 | Five settlement revisions | Implement through one aggregate-version primitive (MR-17) |

ADR-001, ADR-006A, ADR-003 §3/§6/§8 and ADR-008 §5/§6 are, in the reviewer's view, appropriately specified.

## Appendix D — Q3: contradictions among ADR-003/004/006A/007/008
1. ADR-004 §9 ↔ ADR-007 §5 Phase B: fencing advance vs resume (MR-01). **Real contradiction.**
2. ADR-006A §3 "full engine context" ↔ ADR-003 target artifact + manifest: context unspecified (MR-03). **Gap that will become a contradiction.**
3. ADR-006A §5 one clock per island ↔ ADR-007 per-settlement barrier and lease (MR-02/MR-14). **Latent contradiction for G-Q1 Option A.**
4. ADR-003 §2 "projection completely rebuildable from artifact + ops" ↔ ADR-004 Clarification 8. Resolved by the clarification, but the ADR-003 body is stale (MR-19).
5. ADR-008 §7 engine-free typed commit ↔ ADR-006B §6 no defender immunity, through MR-16. **Interaction risk**, not a textual contradiction.

## Appendix E — Q1: right problem or reimplemented vanilla?
[INFERENCE] **Right problem.** The SRS genuinely forces independent clocks (FR-002/003, AC-002), offline attack (CON-010) and offline trade/tax (FR-187/206). No vanilla mechanism provides these. The complexity risk is in *how* it is solved:
- per-field replication (P2) and the server index should stay minimal;
- PREPARED, revisions and outbox should use DB primitives;
- vanilla multi-map and vanilla damage attribution should be tested before custom alternatives.

The largest observed waste so far is effort spent polishing a presentation path while leaving the material path unfalsified, not over-engineering of individual mechanisms.

## Appendix F — Question → section map
| Q | Where |
|---|---|
| 1 | App. E |
| 2 | App. C |
| 3 | App. D, MR-01/02/14 |
| 4 | App. B, MR-03 |
| 5 | 4.2 |
| 6 | MR-06..MR-10, 4.3 |
| 7 | MR-09 |
| 8 | MR-07, 4.4 |
| 9 | 5.1, MR-12 |
| 10 | 5.2 |
| 11 | 6.5, MR-14 |
| 12 | 6.6, Section 7 |
| 13 | 6.7, MR-15, MR-05 |
| 14 | 5.4, MR-13 |
| 15 | 5.5 |
| 16 | 3.3, App. C |
| 17 | 5.3, 5.3a |
| 18 | 5.3a, 6.4 |
| 19 | App. A |
| 20 | 5.3 |