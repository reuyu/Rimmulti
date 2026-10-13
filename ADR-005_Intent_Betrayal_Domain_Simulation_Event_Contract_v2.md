ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract_v2.md
Status: ACCEPTED — Core Intent / Betrayal / Session-Domain Event Contract
Decision Owner: Master (GPT-5.6 Sol)
Project: WarEconomy / RimMulti
1. Context & Baseline
This ADR defines the architecture contract for intent-aware betrayal, mid-session domain events, and the provenance of actions within a Tactical Session. It strictly enforces the boundary between Dedicated Server Domain Authority (which decides betrayal and political transitions) and Tactical Worker Simulation Authority (which observes physical interactions).
This contract aligns with:
- ADR-001 & ADR-002: Server final Domain Authority; Worker Simulation Authority[cite: 26, 27].
- ADR-003 & ADR-004: Canonical material state, staged-result recovery, and OperationId idempotency[cite: 28, 29].
- ADR-006A: Distinction between $W$, $L_s$, and $G$ clock domains[cite: 30].
- ADR-007 & ADR-008: Writer fencing, lease contracts, and canonical custody invariants[cite: 23, 32].
2. Identity & Causality Model
One intent may spawn multiple projectiles, area-of-effect (AOE) damages, and secondary fires. To prevent data loss or false deduplication, the architecture separates causality layers:
- IntentId / OperationId: Identifies the requested client action or server-initiated operation[cite: 29].
- ActionExecutionId: Identifies a specific execution instance accepted by the Worker (e.g., a weapon cooldown cycle completing and firing).
- FactId / EventSequence: A unique, monotonic identifier for every individual observation (e.g., "Bullet hit Pawn A", "Bullet hit Wall"). Deduplication occurs strictly on FactId, never by dropping subsequent facts sharing a parent OperationId.
- CausalityRootId: The root identifier linking secondary effects (fire, explosions) back to the originating ActionExecutionId or autonomous trigger.
- ParentFactId (Optional): Links chained events (e.g., a trap triggering $\rightarrow$ causing an explosion).
- Context Binding: All facts must bind the current TacticalSessionId and WorkerGeneration[cite: 27, 32].
3. Authority Pipeline & AuthorizedActionEnvelope
CommandIntent (from a client) is inherently untrusted. The Tactical Worker is prohibited from conferring political/domain authorization.
1. Untrusted CommandIntent: Submitted by the client.
2. Dedicated Server Authorization: The Server verifies ownership, authenticated principal (SessionEpoch), and current Faction diplomacy[cite: 26, 28]. (Note: ADR-007 WriterLeaseId is for material-state writing and is not used as player command authorization)[cite: 32].
3. AuthorizedActionEnvelope: The Server generates an immutable envelope. If a direct client-to-Worker transport is utilized for latency, this envelope acts as a Server-issued/fenced capability token.
4. Worker Execution: The Worker validates simulation preconditions (e.g., "Is the pawn conscious?") and executes the action.
5. Simulation / Damage Facts: The Worker observes outcomes and streams facts back to the Server, bound to the envelope's provenance.
6. Server Rule Evaluation: The Server evaluates the facts against the current DiplomacyRevision.
7. ADR-004 Domain Commit: The Server durably commits any resulting political changes (e.g., BetrayalDecision)[cite: 29].
8. Session Domain Event Projection: The Server pushes the committed relationship transition back to active Workers/clients.
AuthorizedActionEnvelope Fields
- Immutable action/intent identity (IntentId).
- Authenticated principal (SessionEpoch / PlayerId).
- Controlled Pawn / EntityId.
- Command class (e.g., Attack, Draft).
- Intended target EntityId / FactionId / Coordinate.
- TacticalSessionId & WorkerGeneration.
- Controller / control epoch.
- Authorized diplomacy/relationship scope + revision.
- Authorization WorldTick ($W$)[cite: 30].
- Relevant Local/Tactical tick context (if known).
- Expiry / fencing constraints.
- Payload hash / integrity binding.
4. AutonomousActionContext
Hostile outcomes frequently occur without a live PlayerIntent (e.g., traps, turrets, mental breaks, autonomous AI, offline lawful attacks FR-153)[cite: 24]. The architecture does not synthesize fake player intent for these. Instead, it utilizes an AutonomousActionContext containing:
- Source EntityId.
- Owner/controller provenance (e.g., the Faction that built the trap).
- TacticalSessionId / WorkerGeneration.
- Causal trigger (e.g., TrapSprung, MentalState_Berserk).
- Relevant domain authorization context (e.g., the DiplomacyRevision when the offline attack was authorized).
5. Relationship Revision Model
Diplomacy changes rely on explicit aggregate revisions, not a single global hot revision.
- DiplomacyScopeId: Identifies the relationship aggregate (e.g., a specific Faction Pair).
- AuthorizationRelationshipRevision: The diplomacy revision when the AuthorizedActionEnvelope was generated.
- DecisionRelationshipRevision: The diplomacy revision at the exact moment the Server evaluates the BetrayalRuleInput.
- Domain Commit: Political transitions use Compare-And-Swap (CAS) against these revisions during the ADR-004 commit[cite: 29]. The architecture preserves these history coordinates so that product-policy can explicitly decide if intent-time or impact-time governs.
6. Betrayal Trigger Policy Boundary (Decision Requests)
The architecture captures the BetrayalRuleInput (intent, execution, consequence, causal provenance, relationship revisions, autonomous classification). It does not hard-code the final gameplay policy. 
Decision Requests (G-Q13 through G-Q18):
- G-Q13 (Trap/Turret): Are traps/turrets hitting allies liable for betrayal?
- G-Q14 (Mental Break): Are berserk pawns hitting allies liable for betrayal?
- G-Q15 (AOE Liability): Are AOE/explosive collateral hits against allies considered betrayal, or are they exempt (CON-001)[cite: 24]?
- G-Q16 (Mid-Air Alliance Change): If an alliance forms while a projectile is mid-air, does the impact trigger betrayal, or does the AuthorizationRelationshipRevision protect the attacker?
- G-Q17 (Offline AI Error): Do offline AI targeting errors during a lawful attack generate new betrayals?
- (Note: TBD-03 regarding exact theft trigger timing remains explicitly unchanged)[cite: 24].
7. Worker Fact Journal & Staged Result Integration
Politically relevant facts (e.g., who killed whom) must survive Worker crashes and candidate staging.
- Integration with ADR-004: If a Tactical material outcome (staged result candidate) may become canonical, the required provenance/facts associated with that outcome must be durably linked to the staged result manifest or the committed typed event stream[cite: 29].
- Semantic Validation: If a Worker crashes and a candidate artifact is submitted with materially incomplete required provenance (e.g., a dead pawn exists in the artifact, but no DamageFact or ActionExecutionId explains it), the candidate must fail semantic validation / quarantine. It must not silently publish[cite: 29, 31].
8. Live Session Domain Event Stream
Mid-session diplomacy changes (e.g., War Declaration, Alliance Break) are pushed to the Worker via a durable ordered stream, replacing the improper use of ADR-003's PendingOperationQueue or MaterializationManifest for live updates.
- SessionDomainEventLog / Domain Outbox: An ordered sequence of committed RelationshipTransitions.
- Fields: SessionDomainEventId, domain aggregate revision, TacticalSessionId, event payload.
- Lifecycle:
  1. Server commit is final and canonical before any Worker/client ACK.
  2. Event is placed in the outbox and pushed to the Worker projection.
  3. Worker ACK gates Worker projection readiness and command admission under the new revision.
  4. Automatically replayed upon reconnect to ensure the Worker projection matches canonical truth.
9. Mid-Session Effects
Upon receiving a SessionDomainEventLog payload, the Tactical Worker updates its projection:
- Hostility Projection: Flips local RimWorld FactionManager hostility flags.
- Command Authorization: Flushes stale command intents relying on outdated diplomacy.
- AI Hostility: Triggers native AI recalculation for target acquisition.
- Session Speed: Enforces hostile-session speed (forced 1x) and pause locks if required by SRS (FR-103, FR-104)[cite: 24].
- Invariant: The Worker reacts to the transition; it never originates it.
10. Required Matrices
Event Authority Matrix
Event / Fact	Producer	Trusted Validator	Durable Owner	Canonical-Domain Status	Identity Key	Consumers
CommandIntent	Client	Dedicated Server	Dedicated Server	Untrusted	IntentId	Server Auth
AuthorizedActionEnvelope	Dedicated Server	Dedicated Server	Dedicated Server	Canonical	IntentId	Worker
SimulationFact	Worker	Dedicated Server	Dedicated Server	Projected Fact	FactId	Server (Rule Eval)
DamageFact	Worker	Dedicated Server	Dedicated Server	Projected Fact	FactId	Server (Rule Eval)
BetrayalDecision	Dedicated Server	Dedicated Server	Dedicated Server	Canonical	OperationId	Database, Outbox
RelationshipTransition	Dedicated Server	Dedicated Server	Dedicated Server	Canonical	DiplomacyScopeId + Rev	All Clients/Workers


Causality Matrix
Root	Intermediate 1	Intermediate 2	Fact Identity
PlayerIntent $\rightarrow$	ActionExecutionId $\rightarrow$	Projectile Spawn $\rightarrow$	FactId (Hit)
AutonomousActionContext $\rightarrow$	Trap Sprung $\rightarrow$	Explosion $\rightarrow$	FactId (AOE Hit)
AutonomousActionContext $\rightarrow$	Berserk Trigger $\rightarrow$	Melee Attack $\rightarrow$	FactId (Damage)


Betrayal Rule Input Matrix
Input Field	Architectural Fact	Product-Policy Choice
Explicit Hostile Intent (IntentId)	Fact	Policy decides weight
Execution Occurred	Fact	N/A
Target Identity / Faction	Fact	Policy defines protected classes
Consequence/Damage Amount	Fact	Policy decides threshold
Causal Provenance (Trap/AI)	Fact	Policy (G-Q13, G-Q14)
AuthorizationRelationshipRevision	Fact	Policy (G-Q16 mid-air rules)


Session Domain Event Matrix
Flow	Ordering	Revision	ACK Behavior	Fencing
Server $\rightarrow$ Worker	Strict sequence per TacticalSessionId	DecisionRelationshipRevision	Gates Worker command admission	Rejects intents using old revisions


Failure / Race Matrix
Scenario	Durable Evidence / Canonical Truth	Retry / Replay Behavior	Policy Eval Status
Duplicate IntentId	Canonical Truth unchanged	Deduplicated via IntentId	Proceed
Duplicate FactId	Canonical Truth unchanged	Deduplicated via FactId	Proceed
Two Valid Facts from One Action	Correlated via CausalityRootId	Both processed	Proceed
Out-of-Order Facts	Sorted by EventSequence / Tick	Reorder before eval	Proceed
Worker Crash (Execution, Pre-Report)	Material outcome missing provenance	Candidate quarantined via ADR-003/004	Quarantine / Repair
Server Crash (Fact Receipt, Pre-Decision)	Facts durably logged before crash	Reconciler re-evaluates facts on boot	Proceed
Diplomacy Rev Change Before Execution	Envelope contains old authorization	Worker blocks execution or Server rejects	Proceed
Diplomacy Rev Change Between Exec/Consequence	AuthorizationRelationshipRevision preserved	Evaluate against intent-time revision	Policy dependent (G-Q16)
Decision Commit Racing Diplomacy Op	ADR-004 CAS detects conflict	Re-evaluate or reject	Proceed
Committed Transition + Delayed Worker Delivery	Server domain is Canonical Truth	Worker catches up; stale intents fenced	Proceed
Reconnect / Replay	Tracked via FactId / IntentId	Ignore duplicates	Proceed
Stale Control Epoch	Rejected during envelope generation	Intent ignored	Proceed
Autonomous Event w/ No PlayerIntent	AutonomousActionContext is Truth	Evaluate based on causality	Policy dependent (G-Q13/G-Q14)


11. Acceptance Readiness
E0-Safe Architecture Decisions:
- Strict pipeline: Untrusted Intent $\rightarrow$ Server Authorization $\rightarrow$ AuthorizedActionEnvelope $\rightarrow$ Worker Execution $\rightarrow$ Simulation Facts $\rightarrow$ Server Commit.
- Separation of IntentId, ActionExecutionId, and FactId for 1:N causality trees.
- AutonomousActionContext for trap/AI events (no fake player intent).
- Live SessionDomainEventLog pushing canonical updates to Worker projections, completely decoupled from PendingOperationQueue.
- Staged-result quarantine if a material artifact lacks required FactId provenance.
Product-Policy Decision Requests:
- G-Q13 (Trap/Turret liability).
- G-Q14 (Mental Break liability).
- G-Q15 (AOE / Explosive liability).
- G-Q16 (Mid-air alliance change resolution).
- G-Q17 (Offline AI targeting error liability).
Existing TBD Dependencies:
- TBD-03 (Exact theft trigger timing)[cite: 24].
E1/E2/E3 Proof Obligations:
- End-to-end IntentId to FactId correlation across the network boundary.
- Ordered mid-session diplomacy update forcing an active Worker to flip hostile flags and recalculate AI targets.
- Worker crash recovery ensuring a staged artifact missing provenance is quarantined.
Contradictions:
- None. Operates seamlessly with ADR-001 (Server Authority), ADR-002 (Worker Simulation), ADR-003/004 (Transaction & Staged Results), ADR-006A (Temporal Schema), and ADR-007 (Writer Fencing).
12. Master Acceptance Clarifications
The following interpretations are controlling:
1. AuthorizationRelationshipRevision is historical provenance, not the canonical CAS target.
   It records the relationship state under which the action was authorized. A betrayal/political commit CASes against the then-current revision of the scoped diplomacy aggregate (DecisionRelationshipRevision / expected current aggregate head). If that CAS fails, the Server re-evaluates or rejects according to the operation contract.
2. No intent-time vs. impact-time policy is decided by this ADR.
   The Failure/Race Matrix row for a relationship change between execution and consequence must be read as: preserve AuthorizationRelationshipRevision, execution/consequence facts, and the decision-time aggregate revision; evaluate according to the accepted G-Q16 policy. The architecture does not mandate intent-time precedence.
3. AuthorizedActionEnvelope is durable server-authorized evidence/capability, not itself a political domain transition.
   It is canonical as an authorization record for the action, but it must not be confused with committed diplomacy state.
4. Fact identity is per observation.
   FactId must be globally unique or unique within an unambiguous (TacticalSessionId, WorkerGeneration, EventSequence) namespace. Multiple legitimate facts sharing one IntentId/OperationId must never be dropped as duplicates.
5. EventSequence is an ordering coordinate, not a substitute for causal identity.
   Causality is carried by CausalityRootId / ParentFactId / ActionExecutionId. Ordering and causality may differ.
6. Politically relevant fact durability is coupled to material-result durability.
   If a staged Tactical result may become canonical, the minimum provenance required by the applicable betrayal policy must be durably bound to that staged result before canonical publication. Missing required provenance is a semantic-validation failure, not an automatic assumption of innocence or betrayal.
7. Session-domain delivery is ordered and replayable, but ACK is not canonical commit.
   The Server's RelationshipTransition is final when durably committed. Worker/client ACK only advances their projection cursor/readiness. A stale Worker projection may cause command admission to pause/fence, but it cannot roll back the political commit.
8. Session ordering must also preserve aggregate revision order.
   Delivery may be sequenced per TacticalSessionId, but events affecting the same diplomacy aggregate must never be applied out of aggregate-revision order across reconnect/replay.
9. Worker-side hostility/AI refresh is projection behavior.
   The Worker may update projected FactionManager hostility and AI targeting only after receiving a committed Server event. This never grants the Worker authority to originate the relationship transition.
10. Decision Requests remain open.
    G-Q13 through G-Q17 and TBD-03 remain unresolved product-policy questions. The heading reference to “G-Q13 through G-Q18” is corrected to G-Q13 through G-Q17 unless a future Master decision creates a distinct G-Q18.
11. Runtime proof remains required.
    Acceptance of this ADR does not prove that the current Worker can safely hot-apply diplomacy transitions, preserve fact provenance through crashes, or maintain end-to-end IntentId→FactId correlation. Those remain E1/E2/E3 obligations.
Master Status: ACCEPTED