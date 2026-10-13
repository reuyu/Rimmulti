Open Decision Dependency Map 01 — MASTER CORRECTED
Status: ACCEPTED SEQUENCING BASELINE — NO PRODUCT DECISIONS
Decision Owner: Master (GPT-5.6 Sol)
Source Reviewed: Open_Decision_Dependency_Map_01.md
1. Controlling Interpretation
This artifact distinguishes two different dependency classes:
- Implementation Blocker — the scope cannot be implemented without inventing an unresolved policy/architecture decision.
- Completion / Release Blocker — infrastructure or partial behavior may be implemented behind a stable interface, but the feature cannot be declared product-complete or release-ready until the decision is made.
An open decision is not an implementation blocker merely because the final feature eventually depends on it.
No Canonical TBD or G-Q is resolved by this document.
2. Master Dispositions
Decision	Master sequencing disposition	Earliest mandatory point
TBD-01 Faction join + settlement cap overflow	Later product decision. Blocks faction-join overflow behavior, not Occupy/Destroy generally.	Before Faction Join / SettlementLimit enforcement
TBD-02 WarPending forced-expulsion destination	Later product decision / possibly runtime-informed. Blocks forced-expulsion behavior, not Occupy/Destroy generally.	Before WarPending world-layer expulsion implementation
TBD-03 Theft trigger timing	Runtime proof first + product decision. Blocks theft-specific betrayal transition, not the entire ADR-005 intent/fact substrate.	Before peaceful-visit theft production behavior
TBD-04 Full faction extinction	Later product decision. Blocks extinction/GC semantics only.	Before faction extinction cleanup
TBD-05 Partial tax / LastCollection	Hard product blocker for Tax.	Before offline Tax domain implementation
G-Q1 Multi-settlement ordinary topology	Runtime/architecture decision, not pure product policy. Stable lower layers may proceed; end-to-end multi-settlement ordinary simulation cannot.	Before multi-settlement client/process integration
G-Q2 Ordinary-client residual trust	Defer behind validation interface, but real untrusted client publication cannot be production-approved with an accept-all stub.	Before accepting hostile ordinary-client canonical publication
G-Q4 Tactical crash semantics	Runtime proof first. ADR-004 already fixes commit/recovery mechanics; remaining product semantics concern pre-commit/in-session failure handling.	Before Tactical crash/reconnect product completion
G-Q5	CLOSED / ABSORBED BY ADR-005. Session-domain delivery mechanism is accepted.	N/A
G-Q5b Storyteller in Tactical	Later product/config decision. Does not block betrayal substrate.	Before Tactical feature-complete simulation profile
G-Q6 Checkpoint loss/disconnect grace	Defer behind configurable lease/checkpoint mechanism.	Before ordinary-client UX/recovery policy is frozen
G-Q8 Settlement Inventory boundary	Hard blocker for inventory index/tax/auto-shop semantics, not for every possible Settlement mutation.	Before first inventory-based canonical mutation/indexer
G-Q9 Auto-Shop after Occupy	Later product decision. Blocks conquest × Auto-Shop integration only.	Before ownership-transfer integration with Auto-Shop
G-Q10 Owner UX under Candidate C	NFR/UX acceptance gate, not a blocker for offline-attack correctness or core visit protocol. WAN proof required before full remote-owner Tactical product acceptance.	Before online-owner Tactical release gate
G-Q12a Transit physiology semantics	Runtime/product decision. Does not block basic caravan custody ingress/egress if transit physiology is explicitly deferred/stasis.	Before transit physiology feature
G-Q12b Transit physiology execution mechanism	Runtime proof first. Same separation as G-Q12a.	Before transit physiology executor
G-Q13 Trap/Turret liability	Defer behind ADR-005 rule interface. Blocks final liability behavior, not intent/fact infrastructure.	Before betrayal feature completion
G-Q14 Mental-break liability	Same as G-Q13.	Before betrayal feature completion
G-Q15 AOE liability	Same as G-Q13.	Before betrayal feature completion
G-Q16 Mid-air alliance-change rule	Same as G-Q13.	Before betrayal feature completion
G-Q17 Offline AI targeting-error liability	Same as G-Q13.	Before betrayal feature completion


3. Corrected Production Scope Matrix
Production Scope	Implementation Blockers	Completion / Release Blockers	Can proceed now?
1. PIPELINE_PROBE_CAS	None	None for the probe scope	YES — already authorized/queued
2. First non-inventory Settlement typed mutation	Only the semantic contract of the chosen mutation	Broader product decisions as applicable	Potentially, after Probe gate
3. First inventory-based Settlement mutation / canonical inventory index	G-Q8	G-Q2 depending on hostile client publication path	NO until G-Q8
4. Offline Tax	G-Q8, TBD-05	tax UX/config details	NO
5. Auto-Shop	G-Q8	G-Q9 only when integrated with Occupy/conquest	Partial infrastructure yes; feature semantics no
6. Caravan custody ingress/egress	No mandatory G-Q1/G-Q12 requirement for server-side custody transaction itself	G-Q1 for client/map integration; G-Q12a/b for physiology during transit	Core custody can proceed later without resolving all three
7. Ordinary multi-settlement simulation	G-Q1	G-Q2, G-Q6 for production trust/UX policy	NO for end-to-end topology
8. Visit flow — protocol/session lifecycle	Stable server/session contracts	G-Q10 for final online-owner UX; TBD-03 for theft-specific behavior	Core flow can proceed
9. Tactical offline attack core	Existing ADR-002/engine blockers, not G-Q10	G-Q4 crash semantics for full resilience	Not yet; G-Q10 is not the blocker
10. Tactical crash/reconnect	Runtime proof + G-Q4 policy	G-Q10 only for online-owner UX acceptance	Proof work can proceed; final semantics pending
11. Intent/Betrayal infrastructure	None beyond accepted ADR-005 interfaces	TBD-03 and G-Q13..17 for complete gameplay rules	YES after appropriate Production sequencing
12. Transit physiology	G-Q12a, G-Q12b	NFR/performance validation	NO
13. Occupy / Destroy mechanics	Scope-specific ownership/transaction contracts	G-Q9 only for Auto-Shop carryover	Can proceed without TBD-01/02/04 if extinction/join/WarPending subfeatures are separated
14. Full faction extinction	TBD-04	cleanup/UI details	NO
15. Faction join / settlement-cap overflow	TBD-01	UI/error messaging	NO
16. WarPending forced expulsion	TBD-02	routing/performance validation	NO
17. UI consolidation / release	None as a single architecture dependency	All unresolved user-visible product policies relevant to shipped features	LATE


4. Corrections to the Submitted Analysis
4.1 G-Q10 does not block offline attack core
Remote-owner WAN UX is relevant when a human owner is online and interacting with Candidate C presentation.
A lawful offline attack with defender AI does not require an online-owner UX decision. Therefore G-Q10 is a release/online-owner Tactical gate, not an implementation blocker for offline attack authority/simulation.
4.2 G-Q5b does not block betrayal/intent production
Whether Storyteller incidents run during Tactical is orthogonal to ADR-005 intent/fact/domain-event infrastructure.
G-Q5b may affect Tactical content behavior, but does not block:
- AuthorizedActionEnvelope;
- FactId/correlation;
- BetrayalRuleEvaluator interface;
- SessionDomainEventLog.
4.3 G-Q13..17 are not blockers for ADR-005 infrastructure
ADR-005 intentionally separated fact capture from liability policy.
Therefore implementation may proceed for:
- provenance;
- action/fact journaling;
- causal correlation;
- rule input DTOs;
- event delivery.
The final evaluator behavior remains incomplete until G-Q13..17 are decided.
4.4 G-Q8 is narrower than “all first real Settlement mutation”
G-Q8 blocks any mutation whose correctness depends on the definition of Settlement Inventory.
It does not automatically block a real Settlement mutation unrelated to inventory if that mutation is already fully specified by accepted contracts.
Master should choose the next real Settlement slice based on semantic completeness, rather than assuming it must be inventory-first.
4.5 G-Q1 is partly an engine-feasibility architecture decision
The ordinary multi-settlement topology is constrained by ADR-006A's one-active-LocalClock-per-engine-island rule and RimWorld engine behavior.
It should not be treated as a zero-evidence pure product choice. A later targeted feasibility comparison may be required before Master freezes the topology.
4.6 G-Q12a/b do not block basic custody transfer
ADR-008 already defines canonical caravan/world custody.
A caravan may enter/exit Settlement custody while transit physiology remains explicitly deferred/stasis. G-Q12a/b block physiological progression in transit, not the existence of custody transitions themselves.
4.7 “Temporary defaults” must not silently become Production policy
Examples such as:
- reject-if-over-cap;
- nearest-border expulsion;
- wipe Auto-Shop settings;
- accept-all anomaly detector
may be useful only in isolated tests if explicitly fenced. They are not approved default Production behavior unless Master separately decides them.
5. Near-Term Sequencing
Before PIPELINE_PROBE_CAS
No open product decision is required.
Before the first real Settlement state mutation
Master should first choose the mutation class:
- if inventory-based -> G-Q8 must be decided;
- if non-inventory and fully specified -> it may proceed without G-Q8.
Before ordinary multi-settlement integration
G-Q1 requires architecture/runtime evidence and a Master decision.
G-Q2/G-Q6 may remain behind explicit interfaces until production acceptance.
Before Tactical product completion
G-Q4 must be resolved.
G-Q10 requires WAN/UX evidence for online-owner flows.
G-Q5b is a later profile/config choice, not a core blocker.
Before betrayal product completion
TBD-03 and G-Q13..17 must be decided for their respective behaviors.
ADR-005 infrastructure itself may be built earlier.
6. Cleanup
- G-Q5 = CLOSED / ABSORBED BY ADR-005.
- G-Q5b remains OPEN.
- No new Canonical TBD IDs are created.
- G-Q13..17 remain OPEN.
- No product-policy answer is selected by this map.