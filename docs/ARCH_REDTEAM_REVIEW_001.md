# ARCH-REDTEAM-REVIEW-001 — Independent Architecture Red-Team Review

- Project: WarEconomy / RimMulti
- Reviewer role: external adversarial architecture reviewer (not implementer, not decision authority)
- Decision authority: Master (GPT-5.6 Sol)
- Inputs reviewed: `요구사항_명세서.md` (SRS v1.0), `MASTER_PRIJECT_STATE.md` (MSR-004), `MASTER_DECISION_LOG.md` (MDR-004), `QA_DEFECT_LEDGER.md` (QDL-004), ADR-001, ADR-002, ADR-006A
- Date: 2026-10-02
- No source code, PoC reports or test artifacts were supplied. Every "evidence" statement below is evidence **as recorded in the supplied ledgers**. The reviewer has not reproduced any of it.

## Label legend

| Tag | Meaning |
|---|---|
| **[CANON]** | Canonical requirement: root SRS text |
| **[ACCEPTED]** | Accepted Master decision or accepted ADR (ADR-001, ADR-006A, MD-xxx) |
| **[PROVISIONAL]** | Provisionally accepted architecture (ADR-002 / Candidate C) |
| **[EVIDENCE]** | Evidence recorded in the supplied ledgers as independently reproduced. The reviewer did not re-run it |
| **[INFERENCE]** | Reviewer's reasoning from the documents and from known RimWorld engine behaviour |
| **[RECOMMENDATION]** | Reviewer's proposal. It has no authority until Master decides |

---

## 0. Status Verification (requested pre-check)

| Claim in review brief | Verified against documents | Note |
|---|---|---|
| ADR-001 ACCEPTED | Yes. ADR-001 §5, MD-003 | ADR file says "Reconstructed formal ADR… did not previously exist as a standalone artifact" |
| ADR-002 PROVISIONALLY ACCEPTED | Yes. ADR-002 §12, MD-004/005/006/012/013 | Also reconstructed |
| ADR-006A ACCEPTED | Yes. ADR-006A §19, MD-013 | |
| ADR-003 not authored | Yes. MSR §7 | |
| ADR-004 not authored | Yes. MSR §7 | |
| Tactical Production not authorized | Yes. ADR-002 §12, MD-006 | |
| Full Worker `.rws` not canonical | Yes. MD-007, ADR-006A §4 | |
| Target-scoped publication is the "preferred" direction | **More than preferred.** MD-013 and ADR-006A §3 make B2 the **accepted primary architecture**, while ADR-006A §17 still lists "B2 extraction/merge feasibility" as unproven | See FINDING-15 |

Document conflicts found (detail in Annex F):

- File-name mismatch. The ledger calls itself `MASTER_PROJECT_STATE.md`, but the supplied file is `MASTER_PRIJECT_STATE.md`. ADR file names contain typos (`Cenral`, `Ofline`, `.md.md`). The Context-Recovery Rule (MSR §11) recovers by file name, so this weakens it.
- SRS §4.2 gives the **Client** responsibility for "Settlement Local Simulation" and "RimWorld Map". SRS §4.1 leaves Settlement Inventory and Map **out** of the server-authority list. ADR-006A §10/§14 talks about "canonical assets" and the "current canonical target graph". Neither the SRS nor any ADR says who custodies the canonical settlement graph.
- SRS §77 still names "Map Owner Authoritative" as the preferred tactical architecture. ADR-002 selected Candidate C. SRS §87 makes this an architecture choice, so it is legitimate, but no explicit supersession is recorded.

---

## A. Executive Assessment

**Verdict: coherent but with specific unresolved blockers. I found no proven fundamental contradiction yet. One latent contradiction (FINDING-02) will become fundamental if it is left undecided.**

1. [INFERENCE] The tactical/temporal half of the design (ADR-001 + ADR-002 + ADR-006A) is internally disciplined. Fencing, one-writer and no-wholesale-publish are the right invariants.
2. [INFERENCE] The project has architected the **exception path** (Tactical) and left the **normal path** undesigned. The normal path is ordinary owner-client simulation, which produces the state that everything else consumes. No ADR owns ordinary-simulation custody, owner-client trust, or online↔Tactical handoff. This is the biggest gap.
3. [INFERENCE] ADR-006A's "one active LocalClock per execution island" collides with three other things: one player owning multiple settlements, conquest preserving each settlement's L_s, and the SRS making the client the local simulator. An owner holding two settlements with different L cannot run both in one vanilla client without a decision that no document has made.
4. [INFERENCE] ADR-006A allows concurrent offline asset mutation (§10) and also requires read-set/revision validation at Tactical publication (§13). Until ADR-003 chooses lock or merge, the default result is that a single offline trade invalidates an entire battle, or the battle overwrites the trade.
5. [INFERENCE] Offline trade and offline tax need **engine-semantic manipulation of canonical RimWorld entities** (Things, Pawns, quality, HP, relations) without a running owner. This is the same capability B2 publication needs. Economy and Tactical therefore share one core pipeline that is not yet designed. The plan builds Economy before Tactical without it.
6. [INFERENCE] Candidate C has evidence only for its **simulation** half. Its **presentation** half, where remote clients (including the owner during every visit) control pawns in a Worker-hosted map, has no ADR and no evidence. RISK-02 and NFR-011 are untouched.
7. [INFERENCE] Peaceful visits are long-running full colony simulation inside a Worker. B2's write-set therefore has to cover the whole vanilla + DLC + mod global-state surface, not just combat.
8. [INFERENCE] Trust escalation: client-simulated wealth and pawn counts feed Tier, which then drives titles, territory radius, war timers and SettlementLimit. Owner-uploaded save XML is untrusted, polymorphic input into a "trusted" Worker.
9. [RECOMMENDATION] Continue the current Tactical Worker hardening/verification, because it is not wasted. But **do not author ADR-003/004 on the planned scope**. First get Master decisions on: settlement custody and canonical state representation, multi-settlement clock topology, asset availability during Tactical, and ordinary-simulation trust posture.
10. [RECOMMENDATION] Re-sequence so a shared Settlement State Pipeline (materialize → simulate → extract → validate → commit) is built after Foundation and **before** both Economy and Tactical.

---

## B. Critical Architecture Findings

Severity scale: **Blocker** (must be decided before dependent ADRs/Production), **Critical**, **High**, **Medium**.

### FINDING-01 — Ordinary settlement simulation authority and custody are undesigned
Severity: **Blocker**

Evidence:
- [CANON] SRS §4.2: the Client is responsible for Settlement Local Simulation and RimWorld Map. FR-003: ordinary simulation stops while the owner is offline. FR-206/208/187: the server mutates settlement inventory while the owner is offline.
- [ACCEPTED] ADR-001 §2.5: clients "may propose… cannot unilaterally commit final domain state". ADR-006A §14: ordinary resume uses the "current canonical target graph", never an old local save.
- [ACCEPTED] MSR §7: ADR-003 expected scope includes "owner-local save provenance". No ADR's scope includes *who simulates ordinary time, under what lease, how often state is published, and how the canonical graph is produced*.

Architecture involved: ADR-001, ADR-006A, future ADR-003, ADR-002 (handoff).

Failure scenario: [INFERENCE] The owner plays four hours online. Nothing defines when the owner client's state becomes canonical. The client crashes, or the owner disconnects abruptly. The canonical graph is either (a) four hours stale, and the next offline trade sells items the owner already consumed, or (b) replaced by whatever the client last uploaded, which is unverifiable. Separately, an attack starts on the online owner's settlement. Candidate C requires the map to move into a Worker, but no protocol says how the live client is fenced, how its latest state is captured, or how its map is evicted and later re-injected.

Why the current plan does not cover it: ADR-003 as scoped is about *inventory and save provenance*, which is a data question. The missing piece is an *execution-authority* question, the ordinary-time analogue of ADR-002: writer lease for an owner client, checkpoint cadence, fast-forward-only upload, eviction to Worker, re-injection after Tactical, and hard stop on disconnect.

Required decision or validation:
- [RECOMMENDATION] A **Settlement Custody & Ordinary Simulation Authority** decision. It can be a new ADR, or the first half of a re-scoped ADR-003. It must define:
  1. The server custodies the canonical settlement graph, and the owner client is a leased writer.
  2. The owner-client LocalClock writer lease, unified with ADR-001 SessionEpoch and ADR-002 Worker generation into one fencing model.
  3. Fast-forward-only checkpoint acceptance (parent revision must equal canonical head).
  4. Client simulation hard-stops on disconnect, with the grace period as a product decision.
  5. The live-client → Worker handoff and the Worker → client re-injection.
- [RECOMMENDATION] A PoC is justified (material engine uncertainty): hot eviction and re-injection of one map inside a live vanilla 1.6 client, plus applying server-authored deltas at materialization.

### FINDING-02 — Multi-settlement owner vs "one LocalClock per execution island"
Severity: **Blocker** (needs a product decision)

Evidence:
- [CANON] Players own multiple settlements (FR-034 SettlementLimit, FR-163 Occupy). AC-002: different settlements may have different local dates.
- [ACCEPTED] ADR-006A §2: L_s is per settlement and is not reset by conquest or ownership change. §5: one execution island has one active LocalClock writer, and divergent active clocks need separate islands or validated virtualization.
- [ACCEPTED] ADR-006A §17 lists "ordinary multi-map topology" as open.

Failure scenario: [INFERENCE] Player P owns home settlement H (L=Day 40). P occupies settlement S (L=Day 112, preserved per ADR-006A). P logs in. A vanilla client ticks every player map on one TicksGame. If both maps load, either S's clock is silently rebased onto H's G, which violates "conquest does not reset" and the typed-temporal rules, or the client violates one-island-one-clock. The same applies to settlements founded at different times if founding inherits the player's then-current clock.

Why the current plan does not cover it: ADR-006A deliberately deferred it. No downstream ADR owns it, yet the Foundation data model (Settlement → LocalClockId) depends on the answer.

Required decision (Master product decision, see G-Q1). Options:
1. **Player-scoped clock.** All of a player's settlements share one LocalClock. Conquest or transfer *reprojects* the acquired settlement onto the new owner's clock, using the ADR-006A §7 cross-domain reprojection rule. This needs an ADR-006A amendment: "ownership change = clock-domain migration".
2. **One active settlement per client at a time.** The others stay frozen. Simple, but a large departure from vanilla multi-colony play.
3. **Per-map clock virtualization in one client.** A separately validated engine design. Highest risk.

[RECOMMENDATION] Option 1 is the only one that keeps vanilla multi-map play without a virtualization research project. It must be chosen explicitly, because it modifies an accepted ADR-006A statement.

### FINDING-03 — Online-owner economic mutation against a live, untrusted client
Severity: **Critical**

Evidence:
- [CANON] FR-211: Auto Shop operates while the owner is online. FR-207/208: immediate reflection. FR-187 explicitly allows offline tax, and SRS §59 does not restrict tax to offline, so online tax is also in scope. BR-017: the collector chooses substitute assets.
- [ACCEPTED] ADR-006A §10 covers only the offline case (ΔL=0).

Failure scenario: [INFERENCE] Buyer B purchases 50 steel from online owner O. The server must remove 50 steel from a map whose live writer is O's client. If the server credits B first and O's client never applies the removal (crash, modified client, local reload), the steel is duplicated. If the server waits for O's ACK, FR-207's "immediate" is at the mercy of O's client, and O can stall every trade. For forced tax, O can see the collector arriving and move or destroy high-value items, or pause/reload, before the server's request lands.

Why the current plan does not cover it: ADR-003's expected scope says "offline trade/tax interaction". The online case is the hard one.

Required decision or validation:
- [RECOMMENDATION] ADR-003 must define an **escrow protocol against a leased writer**. The server issues a removal directive bound to the writer lease and a checkpoint sequence. The client must apply it before its next accepted checkpoint, and any checkpoint that does not reflect the removal is rejected. The buyer's credit is committed at the server, with removal enforced through lease validity. Alternatively, define the "Settlement Inventory" used for shop/tax as a server-held escrow (see G-Q8).
- Gate test: kill the owner client between the trade commit and its next checkpoint, then assert no duplication after reconnect.

### FINDING-04 — Concurrent offline asset mutation vs B2 read-set validation
Severity: **Critical**

Evidence:
- [ACCEPTED] ADR-006A §10: authorized offline trade/tax/inventory operations may change revisions while ΔL=0. §13: Tactical conclusion must "validate read-set/revisions".
- [CANON] FR-206 (shop works offline), FR-187 (tax offline), FR-153 (offline attack). The SRS is silent on whether these may overlap on the same settlement.

Failure scenario: [INFERENCE] An attack on offline settlement S runs for 25 minutes. Meanwhile an auto-shop trade sells 30 of a 75-steel stack, and inside the Worker a defender pawn has just hauled that stack and merged it into another. At publication the InventoryRevision has moved. Strict read-set validation rejects the whole battle outcome, which violates FR-155. Ignoring the conflict either republishes the sold 30 steel (duplication, ER-008) or drops the trade.

Why the current plan does not cover it: both halves are accepted, but the conflict rule is deferred to an ADR that has no scope statement for it.

Required decision: G-Q3. Either:
- **(a) Exclusive asset lease.** While S is in a Tactical Session, auto-shop and tax on S are suspended or queued, and publication becomes "replace target subgraph under an exclusive lease". Much simpler.
- **(b) Concurrent mutation with typed merge** (fungible-quantity semantics, conflict compensation). Much harder; see Section E.

[RECOMMENDATION] (a). It does not delete FR-206/187. It defines temporary unavailability during an active battle, but Master must confirm it is not a weakening of the requirement.

### FINDING-05 — Canonical state representation, and engine-free manipulation of RimWorld entities
Severity: **Critical**

Evidence:
- [CANON] FR-191: tax may forcibly take Pawns, Slaves and Animals from an offline settlement. FR-207: the purchased item appears immediately in the buyer's caravan. FR-210: the letter jumps the camera to where the result item was spawned. FR-189: value comes from the Vanilla Market Value at collection time.
- [ACCEPTED] ADR-006A §6 typed temporal schema. Unknown state fails closed.

Failure scenario: [INFERENCE] With the owner offline, the server must enumerate S's inventory (FR-204), compute vanilla market value (which depends on quality, HP and stuff), remove a specific Pawn with relations, hediffs, gear and an absolute birth anchor, and insert it into a tax caravan. Without a RimWorld engine, the server needs its own model of Things and Pawns: the "custom serialization system" failure mode. With an engine, every offline trade or tax needs a Worker materialization, which costs latency and capacity, and FR-207 says "immediately".

Why the current plan does not cover it: everyone assumes that "canonical inventory" exists, and nobody decides what it physically is.

Required decision:
- [RECOMMENDATION] Decide the representation before ADR-003/004 are written. Recommended candidate: **canonical settlement = immutable engine-produced snapshot artifact + server-maintained inventory index (projection) + ordered server-authored delta journal**. Deltas ("remove thing X qty n", "spawn item spec at drop spot", "transfer pawn P to caravan C") are applied by an engine (owner client or Worker) at the next materialization, inside LOAD_FENCED/MATERIALIZING. Fungible items can be removed by delta without an engine. Complex entities (Pawns) either require a Worker transaction or are deferred-delivered. Master should confirm that deferred delivery is acceptable for Pawn tax (G-Q8 related).
- The FR-210 wording ("spawned location") already suggests materialization-time spawning. Use it.

### FINDING-06 — Global entity identity across processes is undefined
Severity: **Critical**

Evidence:
- [ACCEPTED] ADR-001 defines PlayerId only. ADR-006A §16 assigns "entity residence" to ADR-003. No document mentions Thing/Pawn/Faction identity.
- [INFERENCE] RimWorld allocates `thingIDNumber`, Pawn IDs and other load IDs from a per-game `UniqueIDsManager`. Every owner client and every Worker is a separate game.

Failure scenario: [INFERENCE] Worker W1 (attack on S) and owner client O (settlement H) both create `Thing_Steel48211`. Attacker loot from S egresses into a caravan that later enters H. Two Things share a load ID, and cross-references (hauling reservations, ownership, `Pawn.relations`, bills, Lords) resolve to the wrong object or fail to load. This is the semantic-loss class of QA-ENGINE-002, but produced by correct code. The same applies to player Faction load IDs: FR-008 creation, FR-028 dissolution and FR-176 split must be identical in every client world and every Worker context.

Required decision: [RECOMMENDATION] A server-authoritative ID allocation scheme (ID-range leases per writer, or a namespaced ID prefix per writer generation), plus a canonical Faction registry projected into every engine instance. Place it in re-scoped ADR-003, or in a short "Entity Identity" section of the custody decision. It is a real boundary because B2, offline deltas and ownership transfer all depend on it.

### FINDING-07 — Remote tactical presentation/replication has no ADR and no evidence
Severity: **Critical**

Evidence:
- [CANON] FR-098/099/102, NFR-011, RISK-02 (High). SRS §77 suggested 20–30 Hz snapshots under owner authority.
- [PROVISIONAL] ADR-002 says "Remote Tactical = NOT AUTHORIZED". The evidence list (ADR-002 §10) is entirely Worker-side simulation.
- [INFERENCE] Under Candidate C "Always", **every** participant is a remote client, including the owner of the visited settlement (visits require an online owner, FR-095).

Failure scenario: [INFERENCE] The Worker simulates correctly, but a RimWorld client cannot present a map it does not simulate (jobs, reservations, float menus, gizmos, designators, pathing previews, inspect panes), or it can do so only with unacceptable latency. Candidate C would then be infeasible for every visit and every online defence, after Tactical simulation, B2 and ADR-004 have been built around it.

Why the current plan does not cover it: no planned ADR covers replication, determinism/RNG, client connection topology (direct to Worker vs relayed through the server), or command validation location.

Required decision: [RECOMMENDATION] A **Tactical Replication & Client Presentation** decision: snapshot-thin-client vs lockstep/deterministic mirror vs hybrid; Worker authentication of client commands via server-issued tokens; client-side fencing of stale Worker generations. A presentation PoC should run **in parallel now**. It is the remaining material uncertainty that can still invalidate Candidate C.

### FINDING-08 — Peaceful visits turn Tactical into full ordinary simulation inside a Worker
Severity: **High**

Evidence:
- [CANON] BR-009, FR-100: vanilla-like interaction during visits. Visits have no stated maximum duration. FR-102: peaceful speed is Last Input Wins, so up to 3x.
- [ACCEPTED] B2: publish only the authorized target write-set plus explicit cross-boundary transfers.

Failure scenario: [INFERENCE] During a two-hour peaceful visit the owner's colonists research (the vanilla ResearchManager is game-global, i.e. player-global), gain ideology development points, change pawn records and tales, fire storyteller incidents, start or advance quests, change goodwill with NPC factions, and bond animals. None of these live inside the target map. Under B2, each is either (a) silently lost, (b) leaked from Worker-global state, or (c) a hand-classified cross-boundary type. The classification list is the global-state surface of vanilla + all DLC + every approved mod.

Required decision:
- [RECOMMENDATION] Make the classification an explicit, closed artifact: a **Global State Disposition Table** covering every GameComponent, WorldComponent, manager and DLC system, each marked *projected-in read-only / published-delta / suppressed / forbidden*. Its completeness gates READY (it links to QA-ENGINE-005).
- [RECOMMENDATION] Master should decide whether storyteller incidents run in Tactical Sessions (G-Q5b).

### FINDING-09 — Mid-session coupling between Domain Authority and Simulation Authority
Severity: **High**

Evidence:
- [CANON] FR-101 (Peaceful→Hostile in the same session), FR-103 (forced 1x), FR-120/121 (an unauthorized attack makes the factions hostile and the whole faction Betrayer), FR-148 (failed conditional peace returns to war immediately), FR-115 (WarPending→War on a W timer).
- [ACCEPTED] ADR-006A §9 world deadlines on W. §12 admission binds "ordered external event/input watermark". §13 publication at the boundary.

Failure scenario: [INFERENCE]
1. A visitor shoots a colonist. The Worker must emit a hostile-action event with intent attribution *now*. The server must decide Betrayer/War *now* and push the faction-relation change *into* the Worker, because RimWorld faction hostility is global Faction state. That is a live bidirectional channel, not boundary publication.
2. A peace agreement is accepted at W while the battle runs at forced 1x (W runs 3x by default, CFG-001). Is the attack still lawful? Admission-time legality vs live legality is undefined.
3. The defender faction is dissolved (FR-028) or split (FR-176) mid-battle.

Required decision: [RECOMMENDATION] Add a mid-session domain event contract to ADR-002 (or ADR-005), defining event direction, ordering by server sequence, and what world-domain changes do to an active session. The product semantics are G-Q5.

### FINDING-10 — World layer (caravans/world objects) authority, transit clock, and client world projection
Severity: **High** (hidden blocker for Tactical)

Evidence:
- [CANON] SRS §3.1: caravan world movement runs on World Time. FR-072..089: vision, scout and ambush are per-faction, server-side information asymmetry. FR-161: surviving attackers re-form a caravan. FR-183: tax requires an actual Tax Caravan arrival. TBD-02: forced expulsion.
- [ACCEPTED] ADR-006A §15: transit physiology needs an explicit transit/residence clock contract "before that subsystem is implemented".
- [EVIDENCE] MD-012: Dev A's Worker retains `World.WorldTick`, `WorldObjectsHolder.WorldObjectsTick` and `FactionManagerTick`. The world-layer authority gap is already leaking into implementation.

Failure scenario: [INFERENCE] Every attacker arrives as a caravan and leaves as one, and every tax collector and buyer is a caravan. If caravans are simulated by the owner's vanilla client, they move at the client's speed instead of W, the client knows hidden enemy positions (which defeats ambush), and a client reload duplicates caravan cargo (silver paid to an auto-shop comes back). If caravans are server-side, something must hold their Pawn graphs, apply transit physiology, and project them, filtered by vision, into every client's RimWorld world.

Why the current plan does not cover it: ADR-004 lists "caravans" only as an ownership-transaction topic. Nobody owns simulation authority over the world layer, or the per-viewer world projection (player factions, foreign settlements, visible caravans) that every client and Worker world needs.

Required decision: [RECOMMENDATION] A **Shared World Layer** decision: server-authoritative world objects; caravan Pawn custody (transit residence domain); transit clock policy (currently deferred, but it is a *Tactical prerequisite*); vision-filtered projection into client worlds; Faction registry projection (links to FINDING-06).

### FINDING-11 — Content/mod manifest, fail-closed weaponization, and content migration
Severity: **High**

Evidence:
- [CANON] FR-006/007 (version check), CON-006 (Workshop client mod).
- [ACCEPTED] ADR-006A §6: unknown critical temporal state fails closed. §12: admission binds an engine/content/schema fingerprint. ADR-001 §2.8: schema migration for the DB only.
- [EVIDENCE] QA-ENGINE-002: an undeclared dependency reached READY/SAVED with semantic loss.

Failure scenario: [INFERENCE]
1. A defender builds an object from an approved mod whose ThingComp has an unclassified tick field. Fail-closed blocks Tactical admission, so the settlement becomes un-attackable. Fail-closed has turned into an exploit against CON-010/FR-153.
2. A mod or RimWorld patch updates on a server that has run for months. Stored snapshot artifacts were serialized under the old content, and the Worker loads them under the new content. No migration rule exists.
3. A client has a cosmetic mod the Worker lacks, and its uploaded checkpoint references defs the Worker cannot resolve.

Required decision: [RECOMMENDATION] A server-pinned **Content Manifest** as part of world identity, with an approval gate requiring full temporal/global-state classification for every approved mod. Content updates become versioned world migrations. Fold this into ADR-006B (rename it "Configuration & Content Manifest") rather than creating another ADR. Product question G-Q7.

### FINDING-12 — Owner-uploaded save XML is untrusted polymorphic input into a trusted Worker
Severity: **High** (security)

Evidence:
- [PROVISIONAL] ADR-002 §3: Worker = "Trusted" simulation authority. [INFERENCE] The Worker loads the canonical settlement graph, which originated as an owner-client upload.
- [INFERENCE] RimWorld's Scribe loader instantiates types named in `Class="…"` attributes from any loaded assembly. It also follows cross-references and can be fed very large or cyclic documents.

Failure scenario: [INFERENCE] A modified client uploads a checkpoint that instantiates unexpected types, plants objects with absurd stat values, or is oversized. The "trusted" Worker loads it and simulates the attacker's battle against forged defences. In the worst case, unexpected type construction runs side-effecting code during load, before the load fence. QA-ENGINE-007 shows load-before-fence mutation already exists.

Required decision: [RECOMMENDATION] Treat every client-originated artifact as hostile:
- a type allowlist and schema validation on the server **before** acceptance into canonical
- size and complexity limits
- plausibility deltas versus the previous checkpoint (FINDING-13)

"Trusted Worker" must mean *operator-controlled process*, never *trusted input*.

### FINDING-13 — Trust escalation: client-simulated state feeds political power
Severity: **High**

Evidence:
- [CANON] FR-015: Tier uses Faction Total Wealth and Active Pawn count. FR-017: automatic promotion. FR-034/054/110: Tier and Title drive SettlementLimit, border radius and WarPending duration.
- [CANON] SRS §4.2: the client simulates the settlement. [ACCEPTED] ADR-001 §2.10: a local save/hash alone does not establish authority.

Failure scenario: [INFERENCE] A client edits memory or a save, or uses dev mode, to inflate wealth. Its checkpoint passes revision checks because it is a valid fast-forward, and the faction auto-promotes to Empire. Inflated items are sold through the auto-shop into the shared economy and the NPC market (FR-214).

Required decision: Master must state the **ordinary-simulation trust posture** (G-Q2). Ordinary progress cannot be server-verified without re-simulation. The realistic options are plausibility/rate bounds plus audit (accepting residual cheat risk), or moving ordinary simulation to Workers (conflicts with SRS §4.2). It must be a deliberate risk acceptance, not an accident.

### FINDING-14 — Tactical crash recovery semantics and crash-as-exploit
Severity: **High** (product decision)

Evidence:
- [PROVISIONAL] ADR-002 §9: "Worker crash must not silently revert already committed death/loot/damage". [ACCEPTED] ADR-006A §13: publication happens at an accepted boundary.

Failure scenario: [INFERENCE] If publication happens only at conclusion, a crash reverts everything since admission, including deaths that players watched happen. A losing side that can crash the Worker (mod exception paths triggered by crafted commands, resource exhaustion) gets a free rollback. If intermediate boundaries commit durably, B2 merge runs repeatedly mid-battle, which multiplies FINDING-04/08 complexity.

Required decision: G-Q4. Options: rollback to last checkpoint with notice / void to admission state / incremental durable commits. Also decide whether a crash attributable to one side's input has consequences.

### FINDING-15 — ADR-006A accepted B2 before B2 feasibility exists; no reopen trigger
Severity: **Medium** (governance, but high rework cost)

Evidence: [ACCEPTED] MD-013 makes B2 the "primary architecture". ADR-006A §17: "Still open: B2 extraction/merge feasibility…".

Failure scenario: [INFERENCE] ADR-003 and ADR-004 are authored on B2, then B2 extraction proves impractical for the global-state surface (FINDING-08) or for ID integrity (FINDING-06). Three ADRs reopen at once.

Required decision: [RECOMMENDATION] Add explicit **falsification criteria** to ADR-006A §3 (what result reopens B2) and name the fallback (e.g. "B2-lite: whole target-map subgraph replacement under exclusive lease", Section E).

### FINDING-16 — W durability and time regression after a crash
Severity: **Medium**

Evidence: [ACCEPTED] ADR-006A §8: ΔW=0 during downtime; resume from the last durable committed W.

Failure scenario: [INFERENCE] W is checkpointed every N seconds, but operations commit continuously with W stamps. After a crash, W resumes *below* the stamps of already-committed operations (a war declared at W=1000 when W restarts at 990). Deadlines, cooldowns and BR-016 "last actual collection" arithmetic go negative or re-fire.

Required decision: [RECOMMENDATION] An invariant: restart W = max(last W checkpoint, max W of any committed operation). Every operation commit is also a W commit. An implementation rule, but it must be in Foundation acceptance tests.

### FINDING-17 — Configuration retroactivity
Severity: **Medium**

Evidence: [CANON] SRS §73: config changes apply after restart. CFG-010/011/013/025 are durations. NFR-003.

Failure scenario: [INFERENCE] The operator changes the Empire WarPending duration from 24h to 2h and restarts. Does an in-flight WarPending end immediately? Do Ruins expire? Unspecified, and NFR-003 forbids silent corruption.

Required decision: [RECOMMENDATION] ADR-006B must define a snapshot-at-creation vs live-reevaluation policy per config class.

### FINDING-18 — Verification independence is degraded at the exact point of highest risk
Severity: **Medium** (process)

Evidence: [ACCEPTED] MD-014: Sol (GPT-6.1) is the sole independent verifier while B is unavailable. ADR-006A provenance: "derived from GPT-6.1 Sol's ADR-006A proposal". ADR-001 and ADR-002 are "reconstructed" documents.

Failure scenario: [INFERENCE] The author of the temporal contract verifies the implementation against that same contract, and blind spots in the contract do not get tested. The reconstructed ADRs may differ from what was originally decided.

Required decision: [RECOMMENDATION] When B returns, B should re-run the ADR-006A conformance suite. Master should explicitly re-ratify the reconstructed ADR-001/002 texts as the authoritative versions.

---

## C. Hidden Dependencies

### C.1 Cross-ADR consistency issues

| # | ADRs | Conflicting assumptions | Failure scenario | Consequence |
|---|---|---|---|---|
| X1 | ADR-001 ↔ ADR-006A ↔ SRS §4.2 | Clients never commit domain state, yet the canonical graph is the ordinary resume source, and the client is the only ordinary simulator | Nobody is defined as producing the canonical graph | FINDING-01: a decision is missing, and ADR-003 cannot be written without it |
| X2 | ADR-006A §5 ↔ ADR-006A §2 ↔ SRS | One clock per island; L_s preserved through conquest; a player has many settlements | An owner with divergent settlements logs in | FINDING-02: latent contradiction |
| X3 | ADR-006A §10 ↔ §13 | Concurrent asset mutation allowed; read-set validation at publication | A trade during a battle invalidates the battle | FINDING-04 |
| X4 | ADR-002 ↔ ADR-003 ↔ ADR-004 | ADR-002 acceptance needs ADR-003/004; ADR-003 tactical canonicalization needs proven B2 extraction (ADR-002 Worker); ADR-004 commit design needs the ADR-003 artifact format | **Circular dependency**: each waits for the other | Break it by deciding the canonical state representation (FINDING-05) and entity identity (FINDING-06) first, independently of all three |
| X5 | ADR-006A §15 ↔ ADR-002 | Transit clock deferred "until that subsystem"; Tactical requires caravan ingress/egress (FR-161, attackers arrive by caravan) | Tactical Production cannot avoid caravans | Transit policy is a **Tactical prerequisite**, not a later subsystem |
| X6 | ADR-001 SessionEpoch ↔ ADR-002 Worker generation ↔ ADR-006A one-writer | Three separate fencing notions; owner-client-as-writer is not covered by any | An owner reconnects while a Tactical admission is mid-flight; an old session's checkpoint lands after the Worker lease is granted | [RECOMMENDATION] One **LocalClock writer lease** with a monotonic fencing token, issued by the server, held by either a client session or a Worker generation |
| X7 | ADR-002 ↔ future ADR-005 ↔ B2 | B2 publishes at boundaries; betrayal and hostility need live events and live faction-relation pushes | A Peaceful→Hostile flip needs a server decision mid-session | FINDING-09 |
| X8 | ADR-006A §9 ↔ SRS FR-146 + NFR-010 | World deadlines on W; conditional peace is "Vanilla Quest-like" | An implementer uses a vanilla Quest in the client, so the timer runs on client G | Implementation trap: reuse Quest *UI* only, keep the timer on server W |
| X9 | ADR-001 "Trusted" ↔ ADR-002 "Trusted Worker" | Trust in the process is conflated with trust in its inputs | FINDING-12 | Security boundary sits at the wrong place |
| X10 | ADR-006A §6 fail-closed ↔ CON-010 | Unknown state blocks admission; offline attack must exist | FINDING-11 | Fail-closed must be a *content-approval-time* gate, not a runtime denial |

### C.2 Dependency graph (ADR → Production)

```
                 Master product decisions (G-Q1..Q10)
                               │
        ┌──────────────────────┼─────────────────────────┐
        ▼                      ▼                         ▼
 [NEW] Custody & Ordinary   [Scope] Entity Identity   ADR-006B Config
 Simulation Authority       + Canonical State         + Content Manifest
 (FINDING-01/02/03/13)      Representation (05/06)    (11/17)
        │                      │                         │
        └──────────┬───────────┘                         │
                   ▼                                     │
        ADR-003 Inventory / Save Provenance  ◄───────────┤
        (lock-vs-merge, escrow, deltas)                  │
                   │                                     │
                   ▼                                     │
        ADR-004 Ownership Txn / Repair                   │
        (single DB commit point + staged artifacts)      │
                   │                                     │
  [NEW] Shared World Layer (caravans, transit clock,     │
        world projection) ◄── ADR-006A §15               │
                   │                                     │
                   ▼                                     ▼
  FOUNDATION: auth/session (QA-001/011), persistence (QA-002), op journal (QA-005),
  W durability, lease/fencing service, artifact store, schema+content migration
                   │
       ┌───────────┴────────────────────────┐
       ▼                                    ▼
 Server-only domain                 SETTLEMENT STATE PIPELINE
 (Faction/Feudal/Territory/         (materialize→simulate→extract→validate→commit;
  Diplomacy/War state machines)      owner-client lease; delta application; reconnect)
       │                                    │
       │      ┌─────────────────────────────┼───────────────────────┐
       ▼      ▼                             ▼                       ▼
  Ownership-moving actions        ECONOMY (shop/tax/NPC)    TACTICAL (Worker + replication
  (join FR-029, demotion FR-042,  needs ADR-003, TBD-05     [NEW], visits QA-008/009,
  expel FR-046, split FR-176)                               offline attack, conquest,
  need ADR-004 + engine                                     ADR-005 intent, TBD-03)
  ownership transform
```

### C.3 Production plan review (requested review area 8)

| Planned order | Issue | Recommendation |
|---|---|---|
| Foundation first | Correct, but the Settlement schema (LocalClockId, custody lease, revision set, entity ID authority) depends on FINDING-01/02/05/06 | Block only the Settlement/entity schema on those decisions. Auth, session, persistence and journal can start now |
| Faction/Feudal/Territory before Economy | The server-side state machines are safe. But faction join (FR-028/029), demotion transfer (FR-042), expulsion (FR-046) and branch split (FR-176) all rewrite **faction references inside RimWorld maps**, which is RISK-04 in disguise | Build the political state machines early, behind an ADR-004 operation interface. Implement the ownership-moving effects only after the pipeline exists |
| Diplomacy/War before Tactical | War/WarPending/Alliance are server-only, so fine. Betrayal (FR-120..132) needs Tactical intent events | Move Betrayal detection into Tactical, together with ADR-005 and TBD-03 |
| Economy before Tactical | Offline trade/tax need the same materialize/delta/extract machinery as B2 (FINDING-05). Building Economy first invites a server-side Thing model that later conflicts with B2 | Build the **Settlement State Pipeline** before both, so Economy and Tactical become two clients of one pipeline |
| Tactical after Economy | Remote presentation (FINDING-07) is unproven and can invalidate Candidate C | Run a presentation PoC **now**, in parallel. Do not wait for the Tactical phase to discover infeasibility |
| Visit flows (QA-008/009/014) under a separate "Visit" track | Visits *are* Tactical Sessions under Candidate C | Merge into Tactical |
| UI as a late phase | Acceptable for the consolidated window (FR-220..226). Not acceptable for client **world projection** and **tactical presentation**, which are core client architecture rather than UI | Split "Client Integration" (early, with the pipeline) from "UI consolidation" (late) |
| Hardening near the end | Recovery and failure injection *define* ADR-004 correctness | Make failure-injection gates part of every phase's exit criteria |

---

## D. Missing Architecture Decisions

Only genuine boundaries are listed. Several are best handled as **scope changes** to planned ADRs rather than new ADRs.

| # | Decision | Why it is a real boundary | Proposed home |
|---|---|---|---|
| D1 | **Settlement Custody & Ordinary Simulation Authority**: who simulates ordinary time, writer lease, checkpoint acceptance, disconnect stop, client↔Worker handoff, online-owner economic escrow | It is an execution-authority question, parallel to ADR-002, and no ADR owns it (FINDING-01/02/03) | New ADR, or the first half of a re-scoped ADR-003. **Must precede ADR-003 inventory work** |
| D2 | **Canonical State Representation & Entity Identity**: snapshot + index + delta journal; ID allocation authority; Faction registry | Prerequisite to B2, offline trade, ownership transfer and ADR-004; it breaks the X4 cycle (FINDING-05/06) | Front section of ADR-003 (re-scoped "Canonical Settlement State") |
| D3 | **Shared World Layer**: authority over caravans and world objects, transit residence clock, vision-filtered world projection into clients and Workers | Neither ADR-004 (transaction) nor ADR-006A (deferred) covers *simulation* of the world layer; it is a Tactical prerequisite (FINDING-10) | New ADR (absorbs the ADR-006A §15 deferral) |
| D4 | **Tactical Replication & Client Presentation**: thin-client vs mirror, RNG/determinism, client connection topology, command authentication at the Worker, client-side generation fencing | RISK-02 has no ADR; it can invalidate Candidate C (FINDING-07) | New ADR, or a mandatory ADR-002 amendment before ADR-002 can be ACCEPTED |
| D5 | **Content Manifest & Content Migration** | The world's validity is bound to content; fail-closed needs an approval-time gate (FINDING-11) | Fold into ADR-006B → "Configuration & Content Manifest" |
| D6 | **Mid-session domain event contract** | Live Domain↔Simulation coupling (FINDING-09) | Amendment to ADR-002, with the semantics referenced by ADR-005 |
| D7 | **Unified writer-lease / fencing model** | Three partial fencing notions (X6) | Section in D1, referenced by ADR-001/002/004 |

Not recommended as ADRs (implementation detail or covered already): packet format, DB engine (SQLite already accepted), snapshot Hz, a separate RNG ADR (belongs in D4), a separate recovery ADR (belongs in ADR-004), W checkpoint rule (Foundation test, FINDING-16).

---

## E. B2 Publication Analysis

Design under attack [ACCEPTED, ADR-006A §3/§13]: full engine context for reference resolution + one active local-clock island + target-scoped simulation + target-scoped outcome publication / canonical merge.

### E.1 Strongest case FOR B2

1. [EVIDENCE] Wholesale full-save publication is empirically unsafe. Fresh load/export/reload mutated non-target maps and Worker-local World state (MD-007). B2 is the direct structural answer.
2. [INFERENCE] Minimal write-set equals minimal blast radius. A buggy or mod-corrupted Worker can only damage what it was authorized to write, and the server can *mechanically* reject writes outside scope. That is the only enforceable form of "Domain ≠ Simulation authority" (ADR-001 §2.6).
3. [INFERENCE] Target-scoped revisions are the only way to let other settlements, other battles and offline economy proceed concurrently without global locking. Wholesale publication would serialize the world.
4. [INFERENCE] Explicit cross-boundary transfers (loot egress, pawn ingress/egress, ownership change) are exactly the units ADR-004 needs for an auditable, idempotent commit (NFR-012, ER-002).
5. [INFERENCE] Full context for reading keeps vanilla reference resolution intact (relations, factions, ideology) without inventing a custom loader.

### E.2 Strongest case AGAINST B2

1. **The RimWorld object graph is not partitioned by map.** [INFERENCE] Pawn relations, WorldPawns, ideology/precepts, royalty titles and permits, mechanitor bonds, bonded animals, quests and Lords, tale records, faction goodwill, research, storyteller state and history records all cross map boundaries. "Target write-set" is a set that someone must enumerate by hand, and peaceful visits (FINDING-08) make it the *whole* surface.
2. **Entity creation and destruction break identity.** [INFERENCE] Stack split creates IDs and merge destroys them. Projectiles, filth, corpses, blueprints and frames are created and destroyed constantly. Without global ID authority (FINDING-06), merging a target subgraph into canonical can collide with IDs minted by other writers.
3. **Field-level "canonical merge" is the custom serialization system.** [INFERENCE] If merge means reconciling individual Things or fields with concurrent offline mutations, the server needs a RimWorld object model outside the engine, which is the collapse path. Each mod's ThingComp/MapComponent then needs a codec.
4. **Read-set validation is undefinable in practice.** [INFERENCE] AI decisions inside the Worker read foreign state: enemy faction relations, world conditions, other pawns' relations, global research unlocking buildable defences. Validating "the read-set did not change" needs read-tracking across arbitrary engine and mod code.
5. **Temporal fields are everywhere in mod state.** [INFERENCE] Under fail-closed, every unclassified mod field is a potential denial of offline attack (FINDING-11).
6. **Nested holders and movement.** [INFERENCE] Things inside pawn inventories, inside caravans, inside transport pods, inside containers, on shelves, inside corpses. A Pawn that leaves the map mid-battle (FR-160 retreat to the edge) changes residence domain, and its whole nested holder tree must move with a typed temporal reprojection.
7. **World events during combat** (FINDING-09) are writes from outside into the island, which a pure "outcome publication" model does not have.

### E.3 Reviewer judgement (no score)

[INFERENCE] B2 is **structurally sound in principle but missing one fundamental boundary decision**. B2 does not say what is merged at what granularity.

- **"B2-field-merge"** (concurrent mutation reconciled per entity or field) is **likely to collapse into an impractical custom serialization system** for RimWorld + DLC + mods.
- **"B2-lite"** is tractable: the target map is replaced *as a whole subgraph* under an exclusive asset lease. Cross-boundary effects travel only as an enumerated, typed manifest (pawn/item egress and ingress, ownership transform, global deltas from the Disposition Table). IDs come from server-leased ranges.

The engine stays the only thing that understands RimWorld objects. The server only stores opaque target-map artifacts plus a small typed index and manifest.

[RECOMMENDATION] Master should explicitly pin B2 to the B2-lite granularity, conditional on G-Q3 = exclusive lease, or record why field-merge is required.

### E.4 Unresolved proof obligations

| # | Obligation | Kind |
|---|---|---|
| P1 | Target-map subgraph extract → store → re-materialize into a *different* engine context (other foreign maps, other world) with zero semantic loss, on an **engine-generated** complex fixture (QA-ENGINE-006 rule) | PoC/validation |
| P2 | Server-leased ID ranges or namespaces survive extract/re-materialize with no collision across ≥3 concurrent writers | Validation |
| P3 | A Global State Disposition Table exists for vanilla + each owned DLC + each approved mod, and READY fails when an unclassified component is present | Artifact + gate |
| P4 | Typed reprojection of every absolute-anchor field for Pawns/Things crossing clock domains (birth anchors, corpse time of death, Lord/Job expiries) | Validation |
| P5 | Cross-boundary manifest covers retreat → caravan (FR-161), loot, captured prisoners, ownership transform (FR-166), and defender pawns away in caravans | Validation |
| P6 | A server-authored delta journal (offline trades/tax) applies deterministically at materialization, with conflict detection when a referenced Thing no longer exists | Validation |
| P7 | Live hostile-flip path: Worker hostile event → server decision → faction-relation push into the Worker within one tick budget | PoC |
| P8 | Publication commit is a single DB transaction that swaps a pointer to an already-durable, hash-verified artifact (ADR-004 premise) | Design + failure injection |
| P9 | Explicit falsification criteria for B2 itself (FINDING-15) | Governance |

---

## F. Recommended Architecture Sequence

```
Step 0  (now, parallel, no new scope)
        - Continue WP-TAC-WORKER-HARDEN-01 verification (simulation boundary only).
        - Start Remote Tactical Presentation PoC (FINDING-07)  ← material uncertainty.
        - Doc hygiene: file names, re-ratify reconstructed ADR-001/002, B2 falsification criteria.

Step 1  Master product decisions: G-Q1..Q10.

Step 2  D2 Canonical State Representation + Entity Identity      (breaks the X4 cycle)
        D1 Settlement Custody & Ordinary Simulation Authority     (+ D7 unified writer lease)
        PoC only if needed: live-client map eviction/re-injection + delta application.

Step 3  ADR-003 Inventory / Save Provenance (lock-vs-merge per G-Q3, escrow per FINDING-03,
        Settlement Inventory definition per G-Q8, TBD-05 must be closed before tax impl).
        ADR-006B Configuration + Content Manifest (D5).

Step 4  ADR-004 Ownership Transaction / Repair
        (single DB commit point; staged immutable artifacts; outbox; recovery scan; quarantine).
        D3 Shared World Layer (caravans, transit clock, world projection).

Step 5  FOUNDATION implementation (QA-001/002/005/011 first), W durability rule,
        lease/fencing service, artifact store, schema + content migration, failure injection harness.

Step 6  Server-only political domain (Faction/Feudal/Territory/Diplomacy/War state machines),
        with ownership-moving effects behind ADR-004 interfaces.

Step 7  SETTLEMENT STATE PIPELINE + Client Integration
        (owner-client lease, checkpoint, reconnect/stale-save, world projection, server caravans).

Step 8  ECONOMY on the pipeline (auto-shop online/offline, tax, NPC market) + ownership-moving
        political actions (join/demotion/expel/split) using engine ownership transform.

Step 9  TACTICAL on the pipeline: D4 replication, visits (QA-008/009/014), offline attack,
        conquest/occupy (FR-163..171), ADR-005 intent/betrayal (needs TBD-03), D6 mid-session events.
        ADR-002 → ACCEPTED only here, on evidence.

Step 10 UI consolidation (FR-220..226); hardening is continuous via per-phase gates; Release.
```

Rationale: the expensive rework risks are (a) building Economy on a server-side Thing model, (b) building Tactical publication before identity and representation exist, and (c) discovering presentation infeasibility after committing to Candidate C. This order front-loads those three.

---

## G. Questions for Master

Only questions that need a product or architecture decision. None of them is answerable from the SRS. No TBD is resolved here.

- **Q1 — Multi-settlement clock topology (FINDING-02).** When an owner is online, should all their settlements simulate simultaneously? If yes, choose between: (a) a player-scoped clock, where conquest/transfer reprojects the acquired settlement onto the new owner's clock (this amends the ADR-006A "conquest does not reset L_s" statement), or (c) separately validated per-map clock virtualization. If no, (b) one active settlement per client session.
- **Q2 — Ordinary-simulation trust posture (FINDING-13).** Accept client-authoritative ordinary progress, protected by plausibility/rate bounds and audit, with explicitly accepted residual cheat risk flowing into wealth, Tier and the economy? Or require Worker-hosted ordinary simulation (which conflicts with SRS §4.2)?
- **Q3 — Asset availability during an active Tactical Session (FINDING-04).** May auto-shop trades and tax collection on the *target* settlement be suspended or queued while a Tactical Session on it is active? Or must they run concurrently (forcing field-level merge)? What happens when a Tax Caravan arrives at a settlement under hostile attack?
- **Q4 — Worker crash semantics (FINDING-14).** On a Tactical Worker crash: roll back to the last checkpoint, void to admission state, or commit incremental durable boundaries? Does a crash attributable to one side's inputs carry consequences?
- **Q5 — World-domain events during an active session (FINDING-09).** If peace is accepted, Betrayer status expires or is forgiven, WarPending converts to War, a participant faction is dissolved or split, or a participant is expelled while a battle is active: does the session continue under admission-time legality, end, or re-evaluate? (Q5b: do storyteller incidents fire inside Tactical Sessions, peaceful or hostile?)
- **Q6 — Online progress-loss window (FINDING-01).** What maximum ordinary-progress loss is acceptable when an owner client crashes or disconnects abruptly? This sets checkpoint cadence and cost. Does simulation stop immediately on disconnect, or after a grace period?
- **Q7 — Mod policy (FINDING-11).** Must every client match an exact server-pinned content manifest, or are client-only cosmetic mods allowed? Are content or game updates allowed on a running world (requiring world migration), or only at world reset?
- **Q8 — Definition of "Settlement Inventory" (FR-204/188/191).** Which holders count for auto-shop and tax: stockpiles/storage only, ground items in the home area, pawn-carried inventory, equipped gear, building contents, the settlement's caravans away from home? For Pawn/Slave/Animal tax against an offline settlement, is deferred delivery (at the next materialization) acceptable versus immediate?
- **Q9 — Auto-shop state on Occupy (FR-165/166 are silent).** Do Sell/Buy orders and prices transfer to the new owner, reset, or get suspended?
- **Q10 — Owner UX under Candidate C "Always" (FINDING-07).** Confirm the consequence: during every visit and every attack on an online owner's settlement, the owner plays that settlement remotely through a Worker, with network latency on their own colony. Is that acceptable, or should an owner-hosted variant be retained for peaceful visits?

---

# Annexes (requested review areas not fully covered above)

## Annex 1 — Distributed State Failure Analysis (review area 4)

Common premise [RECOMMENDATION]: **one atomic commit point = a single DB transaction**. Every other effect is either (i) an immutable, content-addressed, durable artifact written *before* the commit, or (ii) an idempotent outbox effect delivered *after* it. Every commit is conditional on the current writer-lease fencing token and the expected revisions.

| # | Scenario | What goes wrong without a guarantee | ADR-003 must guarantee | ADR-004 must guarantee |
|---|---|---|---|---|
| 1 | Tactical outcome complete, DB commit fails | Battle lost or applied twice on retry; target resumes from a pre-battle graph | Outcome = target artifact + typed manifest + revision expectations, all immutable | Session enters PREPARED; artifact durable before commit attempt; retries idempotent on (SessionId, Generation, BoundarySeq); target stays locked (no ordinary resume, no new admission) until COMMITTED or explicit ABORTED; Worker may die after artifact durability |
| 2 | DB commit succeeds, artifact publication fails | Canonical pointer to a missing or corrupt artifact | Pointer may reference only artifacts already verified durable (hash checked) | Ordering rule: artifact → verify → commit pointer. Client notification and letters (FR-156) via outbox. Artifact GC may never delete artifacts referenced by committed revisions or non-terminal prepares. Detected corruption → quarantine + restore from previous artifact + journal |
| 3 | Worker dies after partial simulation | Ghost partial deaths/loot; attacker caravan lost | Participant caravans and target state at admission are recoverable | Recovery per G-Q4; both sides restored symmetrically; lease generation increments; session state durable |
| 4 | ACK lost after successful commit | Duplicate publish → double loot | — | OperationId derived deterministically from (session, generation, boundary), never per-attempt random; retry returns the prior terminal result (ADR-001 §2.9); supervisor can query operation status |
| 5 | Stale owner save reconnects | Rollback of offline trades or battle damage; duplication (RISK-03) | Checkpoints accepted fast-forward only (parent == canonical head); a stale client must discard local state and re-materialize from canonical; local save load is disabled in multiplayer | Session reconnect = new writer lease; old session's in-flight uploads fenced |
| 6 | Offline shop mutates inventory during combat | Battle invalidated or trade overwritten (FINDING-04) | Per G-Q3: exclusive lease (reject/queue with a user-visible reason) or typed fungible merge with compensation | Queued operations re-validated against post-battle revisions; queued ones that fail are aborted with a buyer refund |
| 7 | Tax overlaps tactical inventory use | Collector takes items the battle destroyed | Same as 6; tax computation evaluated against the committed post-battle index | TBD-05 must be closed before LastCollection is written |
| 8 | Conquest changes ownership with operations in flight | Trade silver paid to the old owner; tax policy on a now-foreign vassal; a second Occupy by the same attacker exceeds SettlementLimit | Every settlement-scoped operation binds the expected OwnerEpoch; old-epoch operations fail or compensate | Occupy reserves SettlementLimit capacity atomically at choice time (FR-163/164, ER-003), so two concurrent victories cannot both pass a check-then-act race; ownership transform executed by the engine inside the island and committed with the outcome |
| 9 | Old Worker reconnects after lease replacement | Two publishers for one lineage; clients follow a ghost battle | — | Commits conditional on the current fencing token; artifact namespace per generation; the bridge rejects stale generations; **clients also reject snapshots and commands for stale generations** (needs D4) |
| 10 | Server restart during a multi-state operation (demotion + transfer FR-043, join FR-029, split FR-176) | Partial completion, violating NFR-001/005 and ER-010 | — | Durable saga journal; on restart, a recovery scan drives every non-terminal operation forward or back; online owner-client writers fenced before commit; W restart rule (FINDING-16) |

## Annex 2 — Temporal Architecture Attack (review area 5)

| Assumption | Attack | Status |
|---|---|---|
| W / L / G / M separation | Sound. Trap: vanilla systems reused for UX (Quests FR-146, letters with dates, tale dates) silently read G. Every reuse needs a W/L mapping | [INFERENCE] implementation trap |
| One active writer per LocalClock | Sound, but writers include **owner clients** (not stated) | X6/D7 |
| One active LocalClock per island | Collides with multi-settlement owners | FINDING-02, latent contradiction |
| Frozen ordinary time (FR-003) | Consistent. But an untrusted client that keeps simulating after disconnect produces uncommittable progress; the hard stop must be enforced client-side and rejected server-side | FINDING-01 |
| Tactical continues L_s | Sound. Consequence: an attacker's pawns age on the target clock, and the attacker's *home* clock does not advance for them. Fine per policy, but each participant's anchors must be reprojected at both ingress and egress (P4) | [ACCEPTED] + obligation |
| Chronological age follows residence | Residence is undefined for caravan pawns, pawns in transport pods, prisoners taken in battle, and visitors staying hours | Needs D3 |
| Different local calendars | Season and biome follow L, but **weather/temperature in the Worker** must come from the target's L, not from the context save's G. Same for daylight (combat visibility) | [INFERENCE] test case |
| Server downtime ΔW=0 | Consistent with FR-001 (zero players ≠ process down). W regression risk after a crash | FINDING-16 |
| Cross-domain Pawn movement | Remaining-duration semantics require a *typed* inventory of duration vs anchor fields across vanilla + DLC + mods. Same closure problem as FINDING-08/11 | P3/P4 |
| Offline inventory mutation with ΔL=0 | Items or pawns created by trade or tax at W must be anchored on the *receiving* domain's clock (corpse age, rot, pawn birth anchor). A server without an engine cannot do that reprojection, which argues for delta application at materialization | FINDING-05 |
| Hostile forced 1x vs W at 3x (CFG-001) | One real hour of battle = three world hours. WarPending, peace deadlines and Betrayer expiry can cross during a battle | FINDING-09 / G-Q5 |
| Long-running coordinates | Per-settlement L is unbounded over years, and G is int-based in the engine. Rollover is listed in ADR-006A §17 but has no owner | [INFERENCE] Foundation test |

Internal contradiction found: **none strict inside ADR-006A text**. One latent contradiction (FINDING-02) and one unresolved pair (§10 vs §13, FINDING-04).

## Annex 3 — Ordinary Simulation Path (review area 6)

| Question | Current answer in documents | Assessment |
|---|---|---|
| Who is authoritative when the owner is online? | SRS §4.2: the client simulates. ADR-001: the client cannot commit domain state. Settlement map/inventory is not in the SRS §4.1 server list | **Undefined**: FINDING-01 |
| How is an owner-local save trusted? | ADR-001 §2.10: a hash is not authority; ADR-006A §14: an old local save is not implicit authority | Only the *negative* rule exists. There is no acceptance protocol, no hostile-input sanitization (FINDING-12) and no plausibility posture (FINDING-13) |
| Multiple settlements with different LocalTicks? | ADR-006A §5/§17: open | **Blocker**: FINDING-02 |
| Can one client simulate more than one local timeline? | Only via a "separately validated virtualization design" | No evidence; G-Q1 |
| Ordinary → Tactical handoff? | Not described | **Missing**: live-client fence, capture, eviction (FINDING-01) |
| Tactical → ordinary return? | ADR-006A §14: resume from the canonical graph | Direction defined. The mechanism (re-injecting a map into a live client that has other maps running) is unproven |
| Stale or forged ordinary progress rejected? | Revision comparison (ADR-001 §2.10) | Stale: solvable with fast-forward-only. Forged: **not solvable by revisions**; needs a Master trust decision |

Conclusion: [INFERENCE] **Yes, this is the most under-designed area of the architecture**, and it is upstream of Economy, Tactical admission and Tier.

## Annex 4 — Security / Trust Boundary (review area 7)

| Actor | May request | May calculate | May propose | May authoritatively commit | Escalation risks found |
|---|---|---|---|---|---|
| Non-owner client | Visits, trades, war/diplomacy actions, tactical commands for own pawns | Local UI prediction only | Commands | Nothing | Forged HostPlayerId (QA-008); commands addressed to foreign pawns must be rejected by the Worker using server-issued identity, not client-claimed identity; client-claimed AoE "intended target" must never be trusted for Betrayal (FR-132): intent is derived from the command the Worker actually executed |
| Owner client | Same, plus settlement management | **Ordinary local simulation** (SRS §4.2) | Checkpoints of its settlements | Nothing (ADR-001) | **De facto commits** the canonical graph through checkpoints (FINDING-01/13); polymorphic XML into the Worker (FINDING-12); can stall or evade online trade/tax (FINDING-03); save-scumming via local reload |
| Tactical Worker | — | Pawn AI, combat, map mutation within scope | Target write-set + manifest + events | Nothing; the server commits | Executes mod code, so "trusted process" ≠ "correct output". The server must validate scope mechanically. Retained world ticks (MD-012) let it calculate world-layer state it has no authority over |
| Dedicated Server | — | Domain rules, W, market, tax, legality | — | All domain state, revisions, pointers | Must not compute RimWorld entity semantics without an engine (FINDING-05) |
| Supervisor / orchestrator | Worker lifecycle | Lease timing | — | Lease grants (on the server's behalf) | Timeout ≠ inactivity (ADR-002 §9); must be the only issuer of fencing tokens |
| Persistence layer | — | — | — | Stores commits | Partial failures (torn artifact writes, disk full, SQLite busy); needs hash verification on read and disk-full fail-safe |
| External / mod code | — | Runs inside clients and Workers | Indirectly through saves and events | Nothing | Unclassified global or temporal state; fail-closed weaponization (FINDING-11); load-time side effects (QA-ENGINE-007) |
| Server administrator | Console kick/ban (FR-230/231) | — | — | Admin operations | Must be audited (FR-234); manual repair of quarantined state needs an ADR-004 procedure, not raw DB edits |

## Annex 5 — Ten Missing Failure Modes (review area 9, unranked)

| # | Scenario | Violated requirement / principle | Subsystem | Recommended gate / test |
|---|---|---|---|---|
| 1 | Online-owner auto-shop sale, then the owner client crashes or reloads before applying the removal, so the item is duplicated | FR-211, ER-008, RISK-03, NFR-004 | Economy / custody | Kill the owner client between trade commit and next checkpoint; assert total item conservation across buyer + seller after reconnect |
| 2 | An owner with two settlements on different L logs in, and one clock is silently rebased | ADR-006A §5, §2; AC-002 | Ordinary sim / temporal | Conquer a settlement with a divergent L; log in; assert both L values and all pawn ages match policy |
| 3 | Client-forged wealth → automatic Tier promotion | FR-015/017, ADR-001 §2.5 | Faction tier / trust | Upload a checkpoint with implausible wealth delta; assert quarantine/rejection and no promotion |
| 4 | Thing/Pawn load-ID collision between two writers after loot egress | NFR-004, QA-ENGINE-002 class | Pipeline / B2 | Three concurrent writers minting IDs; transfer items across; assert zero collisions and intact references after reload |
| 5 | Defender places an approved-mod object with an unclassified temporal comp, so offline attack is denied | CON-010, FR-153 | Content manifest / admission | Content approval rejects mods lacking classification; runtime admission can never fail for approved content |
| 6 | Malicious checkpoint XML instantiates unexpected types or forged stats in the Worker | ADR-002 trust, NFR-008 | Security / pipeline | Fuzz uploaded checkpoints; type allowlist; assert server-side rejection before any Worker load |
| 7 | Losing side induces a Worker crash to roll the battle back | FR-155, ADR-002 §9 | Tactical recovery | Fault injection on command handling; assert the policy from G-Q4 holds and no side gains from a crash |
| 8 | Peace accepted, or WarPending converts, at W while a battle runs at 1x | FR-112/115/148, NFR-004 | Diplomacy ↔ Tactical | Fire world-domain events during an active session; assert the behaviour from G-Q5 is deterministic and audited |
| 9 | W resumes below committed operation timestamps after a crash | ADR-006A §8, BR-016, FR-118 | Foundation / temporal | Kill -9 the server between a W checkpoint and an operation commit; assert W_restart ≥ max committed W |
| 10 | Two concurrent victories by the same attacker both pass the SettlementLimit check at Occupy | FR-163/164, ER-003, NFR-005 | Conquest / ADR-004 | Concurrent Occupy choices; assert exactly one succeeds or capacity is reserved atomically |

Also notable, but outside the top ten: faction dissolution, split or rename not propagated into every client and Worker RimWorld world (FR-028/176, FR-013 color reuse); per-viewer world projection leaking hidden caravan positions to a client (FR-083/086); artifact store growth and GC on a long-running server; an operator config change retroactively shortening an in-flight WarPending (FINDING-17).

## Annex 6 — Document Conflicts and Hygiene

1. `MASTER_PRIJECT_STATE.md` (supplied file) vs `MASTER_PROJECT_STATE.md` (self-declared name, used by the Context-Recovery Rule).
2. ADR file names: `Cenral`, `Ofline`, `.md.md`, and `_ACCEPTED` embedded in a file name (statuses change, file names should not).
3. ADR-001 and ADR-002 are self-declared "reconstructed" artifacts. Master should re-ratify them as authoritative text.
4. SRS §77 preference (Map Owner Authoritative) vs ADR-002 Candidate C: record an explicit supersession note.
5. SRS §4.1 server-authority list omits settlement inventory/map, while ADR-006A treats "canonical assets/graph" as server-held. This needs an explicit Master interpretation (it feeds D1/D2).
6. The review brief calls B2 the "preferred" direction, but the ledgers record B2 as the **accepted primary architecture** (MD-013) with feasibility still open (ADR-006A §17).
7. SRS §90 "Critical Risk PoC" lists Offline Inventory as a PoC target. No Offline Inventory PoC is recorded anywhere in the ledgers.
