First Real Settlement Mutation Candidate — MASTER ACCEPTED
Status: SELECTED / QUEUED — NOT YET AUTHORIZED FOR IMPLEMENTATION
Selected candidate
Auto-Shop Trade Configuration Update (Setup Phase)
This is the preferred next real gameplay-domain mutation after PIPELINE_PROBE_CAS.
It is selected because order configuration is canonical gameplay state but does not reserve or mutate Item/Silver material state at setup time.
Scope boundary
Uses:
- per-Settlement TradeConfiguration
- dedicated TradeConfigurationRevision
- authenticated owner authorization
- ownership epoch/revision fencing
- ADR-004 replayable typed commit
- content-profile validation
- audit/receipt/outbox
Does not use:
- Settlement inventory availability
- Silver availability
- actual trade execution
- material artifact mutation
- G-Q8
- G-Q9 conquest behavior
- CommittedSettlementStateRevision
Gate
Implementation begins only after Master explicitly releases the queued WP following successful PIPELINE_PROBE_CAS E1/E2 gating.