# Consolidated C Review Corrections
Status: CONTROLLING INTERPRETATION OF NAMED C BRIEFS.
Checkpoint: 2026-10-06. Prepared: 2026-10-07.
Current correction supplements the original historical Master records; it does not invent exact global schema.

## 1. Logical taxonomy retained
MapSegment/Settlement, PlayerGlobal/PlayerId, FactionDomain, SharedWorld projection, Domain-only, reconstructible, unresolved/mixed are useful axes.
They are not evidence that each RimWorld subsystem belongs in a particular owner.

## 2. Authority
Engine Host/ordinary client may propose supported simulated changes.
Dedicated Server authorizes final canonical PlayerGlobal/FactionDomain/SharedWorld revision advancement.
C's execution-lease-holder R/W wording is not unilateral canonical commit authority.

## 3. Subsystem correction matrix
| Raw claim | Current interpretation |
|---|---|
| Research/Ideology/History/Genes are PlayerGlobal truth | hypothesis; exact fields/owner OPEN |
| Quest read-only Domain/SharedWorld projection | lifecycle/mutators/clock/dependency proof needed |
| WorldPawns read-only SharedWorld projection | custody/reference/GC authority and physical representation OPEN |
| Tales/PlayLog discardable | discard/rebuild + noninterference evidence needed |
| Storyteller/Incidents re-roll per session | not adopted; canonical/temporal consequences unproven |
| Weather/Sky visual-only | indirect plant/job/condition/material impact must be checked |
| Royalty/Titles directly FactionDomain | native game titles are not automatically WarEconomy feudal titles |
| Global Def caches reconstructible | validate content/dependency effects; no blanket exemption |

## 4. Aging/clocks
Both biological and chronological residence aging follow accepted local/residence simulation policy.
Calendar/sky display drift may be allowed only with noninterference evidence.
Frozen resident chronological age progression is not automatically permitted by calling it global chronology.
Server W owns canonical world deadlines. C's UTC-or-server-ticked wording cannot silently replace ADR-006A.
UTC/M are logging/operational coordinates unless separately accepted. Transit physiology requires explicit clock/executor policy.

## 5. Revision binding
FactionDomain/SharedWorld revisions are not globally diagnostic.
If material semantics depend on a projection, its revision is hard-bound for relevant admission.
Diagnostic classification requires independence evidence.
Frozen Map + newer global is conditional on compatibility/revalidation; otherwise rebase/rematerialization/staged transformation.

## 6. Physical representation
No literal .rws → Map blob + PlayerGlobal blob split has been selected.
Separate blob, server canonical typed records projected into engine, or other validated representation remain possible.
C exact physical split stop-line is rejected.
Bounded E-B/Genesis probes need explicit dependencies/revisions, not exhaustive PlayerGlobal physical schema closure.

## 7. Cross-owner operations
Research/Ideology examples do not universally require staged .rws transactions.
First establish owner and actual material changes. Metadata-only operations do not acquire material transaction requirements automatically.
WorldPawns membership is not canonical custody by itself; stable EntityId/custody spans Map/World/Transit.

## 8. Context
Official term: Pruned Target-Map Owner Context.
Minimum dependency closure unproven. Required/likely/discardable classifications need runtime proof.
No null reference after load does not prove preserved graph/meaning.

## 9. G-Q1
Execution island/LocalClock domain is topology unit, not inherently one process per Settlement.
Shared-island barrier may pause siblings; this alone is not initial architecture blocker.
Independent simultaneous clocks and actual material semantics determine separation needs.
Model B means bounded evidence-driven interception/reprojection, not blanket getter virtualization.
Model A failure does not prove massive Model B changes or automatic Model C choice.
Mod compatibility is ContentProfile-specific/OPEN. Original REV2 gives inconsistent A/C risk labels; neither table is adopted.

## 10. Oracle
Raw .rws/XML equality is not decisive.
Use fresh-load supported manifest/census, explicit allowed differences, stable identity/custody/material conservation and save-load-resume controls.
Byte SHA identifies exact artifact/provenance; it is not general semantic equality.

## 11. Latest C contract corrections
- Separate-process zero drift is a test hypothesis, not guarantee.
- Weather/Tales/PlayLog differences are not blanket preapproved.
- Frozen chronological/biological aging must satisfy ADR-006A.
- After barrier release B may normally tick; compare to same-tick-schedule control instead of absolute unchanged state.
- Test mutation needs bounded authorized write-set and material accounting. Spawn Silver is not automatically neutral Production operation.
- Unobservable or unsupported dimension is UNOBSERVED/UNSUPPORTED, not PASS.
- Record model binaries/profiles/patch modes. Changed interception/configuration must not be hidden under a falsely identical profile claim.
- E1 feasibility is not E2 verification; contract closes no defect.

## 12. Earlier C reviews
Named historical topics include canonical state/ordinary authority, ADR proposals, open-decision map, G-Q8 inventory/tax/economic boundaries, G-Q1 topology, G-Q2 trust/firewall, G-Q6 grace, PlayerGlobal, Genesis, offline material, Foundation, registries, TradeConfiguration and E-B barrier.
Complete original C response set is not claimed available.
See C_REVIEW_HISTORY_EXTRACTS.md and full history/MSR/MDR for preserved corrections.
If exact Master review is missing, mark original UNRECONCILED ANALYSIS instead of adopting it by default.

## 13. Local guard
Preserve original bytes. Put correction pointer/sidecar visibly beside originals and mandatory root AGENTS instruction.
Do not relabel raw original ACCEPTED as if all paragraphs were ratified.
A source report lower in authority cannot override a later accepted correction.
