# ADR-006A — Temporal Authority

- Status: **ACCEPTED**
- Decision Owner: Master (GPT-5.6 Sol)
- Project: WarEconomy / RimMulti
- Canonical Requirement Source: `요구사항_명세서.md`
- Provenance: Finalized Master version derived from GPT-6.1 Sol's ADR-006A proposal plus explicit Master policy decisions.

## 1. Problem
RimWorld exposes a largely global engine tick coordinate, but the product requires continuously advancing Dedicated Server World Time while running, independently frozen Settlement-local timelines, Tactical simulation that can advance one target settlement while others remain frozen, and offline asset transactions that may mutate inventory without advancing local simulation time.

Therefore engine `TicksGame` cannot be treated as the canonical game clock.

## 2. Accepted Clock Domains
### WorldTick `W`
Dedicated Server authority. Used for world calendar, diplomacy/war deadlines, tax cycles, ruins/recovery timers, world scheduled domain effects, and other explicitly world-timed systems.

### Settlement LocalTick `L_s`
Independent per-settlement local timeline.
- offline ordinary simulation: `Delta L_s = 0`
- login/logout, conquest, or ownership change does not reset it
- timeline identity must remain stable or explicitly migrate

### Tactical Progress `N_t`
Not a separate durable calendar.
`L_s(final) = L_s(admission) + completed authorized target steps`

### Engine Tick `G`
Operational RimWorld execution coordinate only. It does not itself prove World time, Settlement local time, operation eligibility, authoritative aging, or canonical publication.

### Monotonic Runtime Time `M`
Pacing/watchdog/service-budget only. Not a durable gameplay clock.

## 3. Primary Runtime Architecture
Accepted primary direction:
**B2 — Full context for reference resolution + one active local-clock execution island + target-scoped simulation + Target-Scoped Outcome Publication / Canonical Merge**.

## 4. Full Save Rule
A full Worker `.rws` may be a private checkpoint or extraction/materialization input, but is **not** automatically a canonical whole-world replacement.
Foreign maps, unrelated inventories, Worker-local world state, incidental global timers, and raw engine clock state must not be wholesale published.

## 5. One Clock Island / One Writer
- one `LocalClockId` -> at most one active writer
- one engine execution island -> one active LocalClock writer
- divergent active LocalClocks require separate execution islands or separately validated virtualization
- one raw `G` must not be assumed safe for settlements with different local dates

## 6. Temporal Schema
At minimum distinguish local instant, local absolute calendar, local deadline, world deadline, duration/counter, interval debt/phase, non-time identifier, sentinel/unset, and unsupported/ambiguous state.

Blanket rebase of every field containing `Tick` is prohibited. Unknown critical temporal state fails closed or enters repair/quarantine.

## 7. Aging Policy
### Biological Age
Advances only through authorized local/tactical simulation and explicit supported effects. Offline ordinary freeze does not automatically age the Pawn.

### Chronological Age
For Settlement-resident Pawns, follows the authorized residence/local timeline rather than incidental Worker `G` or Server `W`. Frozen ordinary settlements do not age merely because W/G advanced elsewhere.

### Tactical Participants
Target LocalTick advances during Tactical simulation, so supported local physiological/aging mechanics may progress normally.

### Cross-domain Movement
Moving between different local-date domains preserves current age/state and remaining-duration meaning. Date difference does not create catch-up debt. Native absolute anchors are reprojected as required.

## 8. Server Downtime
Initial policy: while the server process is stopped, `Delta W = 0`. Restart resumes from last durable committed W. While server runs, W continues even with zero connected players. No wall-clock catch-up is currently adopted.

## 9. World Deadlines
World-domain timers/deadlines use committed server W. Worker G, client display time, peaceful speed, and Settlement pause do not own these deadlines.

## 10. Offline Asset Mutation
Clock freeze does not imply asset immutability. Authorized offline trade/tax/ownership/inventory operations may change revisions with `Delta L_s = 0`, but remain ordered, authorized, revision-checked, durable, and auditable.

## 11. Load / READY
Conceptual lifecycle:
`SELECTING -> LOAD_FENCED -> MATERIALIZING -> POSTLOAD_VALIDATING -> READY_FROZEN -> ACTIVE -> CHECKPOINT_BARRIER -> EXTRACTING/PREPARED -> COMMITTED`

Autonomous simulation must be fenced before load can escape into normal ticking. `Playing` alone is not READY. Semantic graph, temporal anchor, revision, dependency, and scope validation are required.

## 12. Tactical Admission
Admission binds Settlement/Map identity, LocalClockId, base accepted L, relevant Save/Inventory/Settlement/Time revisions, Worker lease/generation, engine/content/schema fingerprint, permitted write-set, and ordered external event/input watermark.

## 13. Tactical Conclusion / Publication
At an accepted local boundary:
- freeze target execution
- extract authorized target graph/write-set
- validate read-set/revisions
- include explicit ingress/egress/cross-boundary operations
- publish graph + local time + related revisions as one coherent accepted boundary

Inventory canonicalization belongs to ADR-003. Durable multi-state commit/repair belongs to ADR-004.

## 14. Ordinary Resume
Resume from current canonical target graph, current accepted LocalTick, and current revisions. Do not reopen an old owner-local full save as implicit authority. Offline World elapsed time does not become automatic local catch-up debt for needs/jobs/hediffs/crops/power/bills/local mechanics.

## 15. Transit / Caravan Boundary
World movement scheduling may use W. Pawn/Animal physiology/aging/rot during transit is **not automatically defined by raw W**. An explicit transit/residence clock contract is required before implementation.

## 16. Downstream ADR Contracts
ADR-003 must define canonical inventory/save provenance, entity residence, Save/Inventory/Time revision relations, stale owner save handling, offline asset operations, tactical inventory canonicalization, and duplication prevention.

ADR-004 must define artifact + DB + graph + ownership + inventory + time-horizon commit, durable prepare/commit, partial failure, repair/quarantine, idempotent recovery, and accepted-horizon fencing.

## 17. Implementation Status
ADR-006A ACCEPTED does **not** prove implementation. Still open: B2 extraction/merge feasibility, typed temporal materialization, load/READY temporal fence completeness, ordinary multi-map topology, cross-domain codecs, transit physiology, crash/recovery, long-term engine coordinate rollover, and mod/DLC temporal compatibility.

## 18. QA Impact
QA-ENGINE-004 remains OPEN with architecture defined. QA-ENGINE-005 and QA-ENGINE-007 must be evaluated against this ADR. Developer labels such as `passive`, `read-only`, or `minimal coherence` are not sufficient without independent evidence.

## 19. Acceptance
**ACCEPTED by Master.**
This ADR is an upstream contract for ADR-002 implementation completion, ADR-003, and ADR-004.
