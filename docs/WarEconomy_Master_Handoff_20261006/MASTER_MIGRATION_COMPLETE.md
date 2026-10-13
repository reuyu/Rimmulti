# WarEconomy Master Migration Complete

Complete newly written handoff documents. Historical originals and review extracts are separately bundled. See 00_START_HERE.md for actual install/bootstrap.

## FILE: 00_START_HERE.md

# WarEconomy IDE Master Handoff
Project: WarEconomy / RimMulti / RimWorld 1.6
Decision checkpoint: 2026-10-06 Asia/Seoul
Package produced: 2026-10-07 Asia/Seoul
Status: DOCUMENTS PREPARED / LOCAL INSTALLATION AND BOOTSTRAP NOT EXECUTED

어제 통합 메시지로 전달한 문서를 실제 파일로 완성한 패키지다. 새 QA 결과나 이후 구현 진척을 가정하지 않는다.

## 설치
1. 실제 저장소 docs/master-handoff-20261006/에 ZIP 내용물을 푼다.
2. 기존 루트 AGENTS.md가 있으면 보존하고 이 패키지 AGENTS.md 지침을 병합한다. 없으면 복사한다.
3. IDE_MASTER_BOOTSTRAP_PROMPT.md 본문을 새 마스터의 첫 메시지로 전달한다.
4. 새 마스터는 SRS·현재 git 상태·governance·candidate·raw evidence를 대조한다.
5. 검증 후에만 다음 승인된 WP를 전달한다. 이 패키지 생성은 전송 증거가 아니다.

## 필수 읽기
- [Master handoff](MASTER_HANDOFF.md)
- [C 정정본](C_REVIEW_CORRECTIONS_CONSOLIDATED.md)
- [C 원문 판정표](C_SOURCE_DISPOSITION_REGISTER.md)
- [현재 상태](MASTER_PROJECT_STATE.md)
- [결정 delta](MASTER_DECISION_LOG.md)
- [QA delta](QA_DEFECT_LEDGER.md)
- [Dispatch](MASTER_AGENT_DISPATCH_BOARD.md)
- [ADR acceptance](ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md)
- [원문 목록](SOURCE_REGISTER.md)
- 해당 원문과 raw evidence

## 핵심 현재 상태
Pipeline REV5 E2 FAIL. 001/013만 시험 범위 내 CLOSED. 007·현재 V6 collation OPEN.
Engine Gate05 E1 accepted / E2 pending. Engine 002/006 OPEN.
G-Q1 OPEN. Foundation HOLD. 다음 작업 A Pipeline REV6, Sol Gate05 E2, 모두 NOT SENT.
C는 정규 배치에서 제외하고 필요할 때 분석자로 사용한다. 계정·대화를 삭제한 것이 아니다.
Dispatcher는 미설정이며 예약을 생성하지 않았다.

## 권한 해석
C 원문·ADR PROPOSED header·자체 PASS·과거 ledger 첫 표만 보고 현재 상태를 확정하지 않는다.
Master 정정과 범위별 acceptance를 함께 읽는다. 역사 자료는 history/, 원문 보고서는 source_reports/, ADR는 reference_adrs/에 보존했다.

## 없는 자료
Root 요구사항_명세서.md, 실제 source/git/binaries/raw logs/fixtures는 이 패키지에 없다.
모든 과거 C 원문을 확보한 것은 아니다. 역사 리뷰 추출은 포함했으며 미확보 원문은 재구성하지 않았다.
코드·실행 증거·로컬 설치를 직접 검증했다고 주장하지 않는다.


---

## FILE: AGENTS.md

# WarEconomy Master Instructions
실제 저장소 루트 AGENTS.md와 병합할 addendum다. 기존 빌드·보안·디렉터리 지침은 삭제하지 않는다.

## Mandatory recovery
새 세션/compaction 후 docs/master-handoff-20261006/00_START_HERE.md, MASTER_HANDOFF.md, C_REVIEW_CORRECTIONS_CONSOLIDATED.md, 현재 state/decision/defect/dispatch를 읽는다.
실제 root 요구사항_명세서.md와 작업 범위의 accepted ADR·Master correction·원문/증거를 확인한다.
설치 위치가 다르면 실제 경로를 찾는다.

## Authority
최신 사용자 명시 변경을 기록한다. Canonical SRS를 agent brief로 약화하지 않는다.
Accepted Master correction은 해당 draft 단정을 대체한다.
Dedicated Server가 final Domain Authority다. Engine/Client는 bounded simulation proposal을 만든다.
Full Worker .rws는 자동 wholesale canonical replacement가 아니다.
W/L/G/M, one LocalClock writer, island-scoped barrier, target-scoped publication을 유지한다.
G-Q1·exact PlayerGlobal schema·physical split은 OPEN이다.

## C guard
C 정정본을 읽지 않고 Research/Ideology/History/Genes owner, Quest/WorldPawns read-only projection, Tales/PlayLog/Storyteller/Weather discardability를 freeze하지 않는다.
UTC world ordering, Faction/SharedWorld revision 일괄 diagnostic, per-Settlement process, separate-process guaranteed zero drift를 채택하지 않는다.
원문이 단정해도 independently observed/explicitly adopted 상태를 확인한다.

## Evidence
E1 PASS는 independent E2를 대체하지 않는다.
Test name·100% PASS·cryptographically bound 표현과 실제 실행/authority proof를 구분한다.
Frozen candidate를 수정/재빌드하며 기존 E2를 재사용하지 않는다.
Release revision/schema/signature/SHA/MVID/source/PDB/manifest/evidence identity를 결속한다.
Critical/High closure는 구현·targeted regression·필요한 E2·Master disposition을 요구한다.
Foundation은 Pipeline E2 PASS 전 HOLD다.

## Coordination
처리 중인 에이전트에게 새 WP를 중복 전달하지 않는다.
결정·리뷰·closure·dispatch 변화는 durable 파일에 남긴다.
Dispatcher는 승인된 전달만 수행한다. 새로운 WP·gate·closure를 만들지 않는다.
첫 작업은 bootstrap/reconciliation이다. 그 전에 unattended dispatch는 disabled다.


---

## FILE: MASTER_HANDOFF.md

# Master Handoff
Checkpoint: 2026-10-06. Prepared: 2026-10-07.

## 목표
Dedicated Server canonical authority 위에 ordinary settlement, shared Tactical, lawful offline combat, custody/ownership, diplomacy/economy를 통합하는 RimWorld 1.6 모드다.
전체 요구사항은 root SRS로 복구한다. 이 요약은 SRS를 대체하지 않는다.

## 현재 위치
P1 Transaction Pipeline repair와 shared Engine Host semantic authority가 병목이다.
전체 진행 약 25~35%, 기반 PoC 약 65~75%라는 과거 수치는 대화상 추정이며 WBS 측정·일정·gate 근거가 아니다.

| Track | Evidence | Master disposition | Next |
|---|---|---|---|
| Pipeline REV5 | Sol E2 FAIL | 001/013 좁은 CLOSED, 007·V6 collation OPEN | A REV6 |
| Engine Gate05 | A E1 65/65 reported PASS | E1 accepted, E2 required, 002/006 OPEN | Sol Gate05 E2 |
| G-Q1 contract | C analysis/no code | accepted with corrections; no runtime verdict | corrected runtime contract |
| Migration | 사용자가 문서 생성 승인 | package prepared, local bootstrap pending | IDE Master |

## 보존할 계약
1. Server final Domain Authority; execution authority는 final custody가 아니다.
2. W(WorldTick), L(residence/local simulation), G(engine), M(monotonic operational time)는 별도다.
3. Offline ordinary ΔL=0. Authorized asset transaction을 금지하는 뜻은 아니다.
4. Accepted server downtime ΔW=0; 실행 중 zero-player W는 진행.
5. one LocalClock writer; island-scoped barrier. Divergent simultaneous clocks는 G-Q1 증거가 필요하다.
6. Full Worker save는 context/checkpoint/extraction input. Target write-set와 explicit transfer만 canonical merge.
7. ArtifactBaseStateRevision watermark와 CommittedSettlementStateRevision head를 구분.
8. PendingOperationQueue를 committed인 것처럼 materialize하지 않는다.
9. Durable operation key=(PrincipalId, OperationId). Principal과 SessionEpoch는 별도.
10. Caller hash는 authority가 아니다. StoreIncarnation은 ordinary restart 유지, timeline restore/rollback 등에 rotate.
11. Single-scope typed atomic path와 staged/multi-party PREPARED path를 구분.
12. Pipeline 현재 slice는 PublicationEvent durable append까지만. Consumer ACK/dedup/external effect exactly-once는 별도다.
13. ADR acceptance ≠ runtime completion. Material/trade/tax/tactical release는 아직 HOLD.

## C 기억 복구
C taxonomy는 유효하나 exact subsystem owner·physical split은 미확정이다.
Canonical PlayerGlobal revision은 Server-authorized다. Quest/WorldPawns read-only, Tales/PlayLog/Storyteller/Weather discard/re-roll은 미증명이다.
현재 correction과 history 추출을 필수로 읽는다.

## 다음 순서
Local bootstrap → A REV6/Sol Gate05 E2 → A freeze·Sol idle 후 Pipeline REV6 E2.
G-Q1 probe는 corrected contract로 후속 실행.
Pipeline E2 PASS 뒤 Foundation release 검토. G-Q1을 모든 metadata 작업의 blocker로 확대하지 않는다.

현재 사용자가 보고한 A/Sol/C 완료 상태를 전달 직전에 다시 확인한다. 새 WP는 아직 전송하지 않았다.


---

## FILE: MASTER_PROJECT_STATE.md

# MASTER_PROJECT_STATE — MSR-068
Decision checkpoint: 2026-10-06 Asia/Seoul. Package prepared: 2026-10-07.
Baseline: [historical MSR-067](history/MASTER_PROJECT_STATE_MSR-067.md).
로컬에 더 최신 자료가 있으면 번호만으로 덮어쓰지 않는다.

| Track | Current state | Gate |
|---|---|---|
| Pipeline P1 | REV5 independent E2 FAIL | targeted REV6 required |
| Engine Host | Gate05 E1 accepted/E2 pending | 002/006 OPEN |
| G-Q1 | C contract complete; corrected Master contract | OPEN/no runtime result |
| Foundation | architecture accepted | implementation HOLD |
| IDE Master | package prepared | bootstrap pending |
| C | no active next work | on-demand only |
| Dispatcher | instructions/template prepared | not configured |

## Delta
001 CLOSED: tested typed input/exact canonicalization scope.
013 CLOSED: tested actual writer/coordinator/final Shutdown/Dispose/Main/UNKNOWN convergence.
007 OPEN/HIGH: historical observation and full typed audit semantics.
MIG-PIPE-V6-COLLATION OPEN/HIGH: provisional ID; map after checking local ledger.
008 historical V5 CLOSED only; current V6 is not certified.
019 prior tested closure retained, regression required.
Engine 002/006 OPEN; Gate05 fixes E1 claimed/E2 pending.
Other historical defects retain scope/status unless separately adjudicated.

## Architecture
001/003/004/005/006A/006B/007/008 core contracts have Master acceptance recorded with corrections/open boundaries.
002 PROVISIONALLY ACCEPTED. Several original drafts still say PROPOSED; use acceptance map.

## Open
G-Q1, G-Q2, G-Q6, exact globals, G-Q8, G-Q9, G-Q10, G-Q12a/b, G-Q13..17, TBD-01..05.
Further historical G-Q IDs are not closed by omission; reconcile full local list.

## Production sequence
P1 repair/E2 → P2 Foundation → P3 Player/Faction/Settlement registries → P4 metadata TradeConfiguration.
Material operations additionally need relevant Engine/E-B/custody/application-totality proof.
G-Q1 gates relevant ordinary multi-clock integration, not all metadata.
WAN P2 gates Remote Tactical/G-Q10, not unrelated server metadata.

## Limits
This snapshot reviews reports and Master history; it does not claim current repo/binary inspection or re-execution.


---

## FILE: MASTER_DECISION_LOG.md

# Master Decision Migration Delta — MDR-068
Preserve historical MD-001..MD-132 in [MDR-067](history/MASTER_DECISION_LOG_MDR-067.md).
MIG IDs below avoid collision with existing canonical IDs.

## MIG-MD-001 — REV5 disposition
Overall FAIL. Adopt 001/013 closure within tested scope; 007/current V6 collation OPEN. Foundation HOLD.

## MIG-MD-002 — Historical observation
Requested/observed revision, terminal reason/status and success-child absence need coherent durable decision binding.
Range checks, mutable duplicate copies or freely recomputable hash alone do not prove original observation.
Define witness/order and threat boundary. This is not an unstated requirement to defeat an administrator rewriting every trusted source.

## MIG-MD-003 — Typed audit
Require every mandatory field with correct type/meaning. Link terminal status, parent/scope, event/receipt, revisions and FailureReason.
Missing keys cannot pass conditional checks.

## MIG-MD-004 — Schema equality
Validate effective canonical key/index collation/comparison semantics and case-distinct keys.
Do not lowercase identities to hide the defect.

## MIG-MD-005 — Gate05
E1 accepted; independent E2 mandatory. 002/006 OPEN.
Nonce length and alive PID alone do not prove approved fresh validator execution.

## MIG-MD-006 — C corrections
Consolidated correction controls interpretation of named briefs. G-Q1 contract is experiment specification, not runtime proof.
Unreconciled C assertions remain hypotheses.

## MIG-MD-007 — Team
Regular team: IDE Master, A, Sol, Dispatcher. C optional analyst; no routine next WP. Existing source/conversation preserved.

## MIG-MD-008 — Bootstrap/dispatch
Reconcile SRS/local governance/candidate/evidence before automatic dispatch.
Documents are not delivery evidence. NOT SENT remains until verified submission.

## MIG-MD-009 — Dependencies
Pipeline E2 gates Foundation. Engine/G-Q1/E-B gate dependent operations only.
Physical PlayerGlobal split is not universally prerequisite to metadata or bounded evidence probes.


---

## FILE: QA_DEFECT_LEDGER.md

# QA Migration Delta — QDL-065
Complete historical inventory: [QDL-064](history/QA_DEFECT_LEDGER_QDL-064.md).
This current delta does not close omitted defects.

| Item | Status | Scope/next |
|---|---|---|
| QA-PIPELINE-001 | CLOSED | REV5 typed input/exact JSON tested scope |
| QA-PIPELINE-007 | OPEN/HIGH | historical decision + full typed audit |
| QA-PIPELINE-013 | CLOSED | actual writer/final lifetime/UNKNOWN tested scope |
| QA-PIPELINE-008 | historical V5 CLOSED | no implication for V6/future schema |
| MIG-PIPE-V6-COLLATION | OPEN/HIGH/provisional | identity comparison descriptor/canary |
| QA-PIPELINE-019 | prior closure retained | admitted derivation/identity, regressions |
| QA-ENGINE-002 | OPEN/E1 fix claimed | trusted lineage/context/profile E2 |
| QA-ENGINE-006 | OPEN/E1 fix claimed | saved supported semantics E2 |

013 does not certify unrelated server tasks/all pooled handles.
001 does not prove unlimited inputs/future serializers.
65/65 Gate05 E1 does not certify all mods/full game graph/production integration.

Preserve legacy QA-001..014, Engine, Presentation, Pipeline historical findings. Assign collation permanent ID only after local inventory check, preserving REV5 QA §8 traceability.


---

## FILE: MASTER_AGENT_DISPATCH_BOARD.md

# Dispatch — MADB-025
Checkpoint: 2026-10-06. All new work NOT SENT.

| Agent | Latest completed | Current | Next |
|---|---|---|---|
| A | Engine Gate05 E1 | Frozen/idle; recheck | WP_PIPELINE_REV6 |
| Sol | Pipeline REV5 E2 FAIL | Idle; recheck | WP_QA_ENGINE_GATE05 |
| C | G-Q1 contract | Complete/on-demand | none |
| Master | package | bootstrap pending | reconcile/dispatch |
| Dispatcher | none | not configured | approved deliveries |

A prerequisite: bootstrap verified, correct repo/worktree, Engine frozen boundary preserved, idle.
Sol prerequisite: exact Gate05 freeze/evidence identity, QA copies/harness, idle.

Queue: Pipeline REV6 E2 after A E1 freeze + Sol Gate05 completion.
G-Q1 runtime after capacity and bounded fixture/oracle readiness.
Foundation release only after Pipeline E2 PASS and scoped Master release.

Delivery lifecycle: READY_TO_DISPATCH → SENT → ACKNOWLEDGED → IN_PROGRESS → COMPLETED.
BLOCKED/DELIVERY_UNCERTAIN are separate. Recheck uncertain delivery before retry.


---

## FILE: ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md

# ADR Acceptance / Authority Map
Core acceptance does not ratify every draft paragraph or certify runtime completion.

| ADR | Master status | Controlling record |
|---|---|---|
| 001 | ACCEPTED architecture; Foundation HOLD | MD-003; MSR-056 corrections |
| 002 | PROVISIONALLY ACCEPTED | trusted tactical worker primary candidate/runtime gates |
| 003 | ACCEPTED core | MD-023 + watermark/state amendments |
| 004 | ACCEPTED core | MD-038 + fast/staged path amendments |
| 005 | ACCEPTED core | MD-045; liability G-Q13..17 OPEN |
| 006A | ACCEPTED | MD-013/ACCEPTED artifact |
| 006B | ACCEPTED core | MD-035 + MD-114/130 |
| 007 | ACCEPTED core | MD-026; G-Q1/2/6 OPEN |
| 008 | ACCEPTED core | MD-030; G-Q12a/b OPEN |

Original ADRs are copied unchanged into reference_adrs/. Several PROPOSED headers are stale.
Read history/MDR and Master corrections together. Embedded [cite: n] and file:/// references in drafts are not self-contained evidence.
Historical MSR-067 initial tables are stale; later deltas carry acceptance updates.
Root SRS remains canonical product baseline; latest explicit user change must be recorded.
No product TBD closes through core acceptance.


---

## FILE: C_REVIEW_CORRECTIONS_CONSOLIDATED.md

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


---

## FILE: C_SOURCE_DISPOSITION_REGISTER.md

# C Source Disposition Register
| Original | Disposition | Controlling source |
|---|---|---|
| GQ1_Temporal_Topology_Decision_Brief_REV2.md | analysis accepted with corrections/G-Q1 OPEN | consolidated correction + MSR-062 |
| PlayerGlobal_SharedWorld_Temporal_Boundary_01.md | taxonomy retained/owner+physical split OPEN | consolidated correction + MSR-065 |
| GQ1_Decisive_Runtime_Probe_Contract_01.md | corrected experiment specification/no runtime | consolidated correction + corrected contract |
| ADR-003 v3 | core accepted later | MD-023/later amendments |
| ADR-004 v2 | core accepted later | MD-038/later path amendments |
| ADR-005 v2 | core accepted later/liability OPEN | MD-045/G-Q records |
| ADR-006B v2 | core accepted later | MD-035/114/130 |
| ADR-007 v4 | core accepted later/topology-trust-grace OPEN | MD-026/later corrections |
| ADR-008 v2 | core accepted later/transit physiology OPEN | MD-030/G-Q12 |
| other C briefs | reconcile before design freeze | exact historical Master disposition |

Suggested visible original-side pointer:
“ANALYSIS ORIGINAL. Read C_REVIEW_CORRECTIONS_CONSOLIDATED.md and applicable Master disposition before using as implementation contract. Assertions are not automatically accepted decisions.”

Original copies in source_reports/reference_adrs are unchanged. Their folder NOTICE files and root reading rule provide the guard without altering original evidence.


---

## FILE: MASTER_REVIEW_PIPELINE_REV5_E2.md

# Master Review — Pipeline REV5 E2
Source: source_reports/QA_Production_Transaction_Pipeline_01_REV5.md
Master verdict: FAIL — TARGETED REV6 REQUIRED.

## Accepted independent progress
Five prior typed input errors now INVALID_REQUEST/durable rows 0.
Natural mixed COMMITTED/ABORTED restart and principal-scoped identities recover.
Actual writer/final Shutdown/Dispose/Main and UNKNOWN query/retry pass tested scope.
Concurrency/CAS/idempotency, hard-kill/terminal/incarnation/WAL regressions retained.
Current exact REV5 release manifest exists and entries match.

## Blockers
Plausible historical observed-revision rewrite reaches READY/LISTEN.
ABORTED status/reason/FailureReason/required typed-key omissions pass.
COMMITTED audit event/parent/scope/revision fields are incompletely checked.
Current V6 descriptor ignores identity collation, merging case-distinct keys.

## Expected report-verified provenance
Server DLL SHA: 1143AE62FD74F0C93F0504B48C1501D5153F40C2E903BD4D69BA9BE1E6983479
Server MVID: a5cba4c3-1e2f-4a19-a35c-0241ccf12e81
Common DLL SHA: 2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB
Manifest: RELEASE_MANIFEST_PIPELINE_REV5.json
Manifest SHA: D609795D8B50ED98850B8C73E951EA7F8E9B21B6193E815CF4890B9E2BB7D9E6
V6 signature: 64BDB62037D70303D7F2AE15D39FC7E7DFD9F01021B5E0AA0709A51FA507E721

These are expected values from report, not current local inspection by migration Master.

## Documentation
A sample DDL differs from frozen DDL. Actual report: history PK=(ProbeScopeId,ProbeRevision); audit PK=AuditId; composite principal/op FKs.
E1 named OS-process/hard-kill/package batteries do not all execute claimed categories. Correct actual coverage in REV6.
001/013 narrow CLOSED. 007/current schema OPEN. Foundation HOLD.


---

## FILE: MASTER_REVIEW_ENGINE_GATE05_E1.md

# Master Review — Engine Gate05 E1
Source: source_reports/POC_EngineHost_Semantic_Authority_Gate_05(2).md
E1 PASS — DEVELOPER EVIDENCE ACCEPTED / E2 REQUIRED.
65/65 is developer-reported evidence, not independent closure.

## Claimed changes
Simulator-owned ValidatorTask/32-byte capability, internally issued receipt, disabled caller-nominated API, sealed-manifest binding, control-plane revocation, authority/grant lineage/scope/budget/mode, epoch fencing, loaded-content profile, atomic replacement, fresh positive chain.

## Independent questions
Capability protected from caller? Unrelated live PID accepted?
Real launched validator task/result channel bound? Task expected file immutable?
Actual fresh-load proof required before completion?
All authority-defining fields/source/scope/map/version/result/epoch checked?
Stage identity preserved across validation/promotion?
Semantic content digest stronger than counts? Both processes compute independently?
Unsafe copy-overwrite fallback absent?

## Expected report identities
WorkerBridge SHA: 2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C
MVID: 12bb9237-1b3e-4b20-89a7-69ad729861e1
WorkerBridge.cs SHA: BC9FD8DAA608892E97903BA56114B7186BABF29157ADAE45658238C3DD497549
EngineHostCensus.cs SHA: 954C12F7500EC0BF4AE8265D2F66EFA39369A69F2C9DF3D1DBA20A9F54CBD024

## Scope/gate
Current V4 supported evidence includes bounded active JobDef/loadID/targets/reservations and other declared fields.
Not full JobDriver/toil/path/expiry/queue, whole game graph or all-mod compatibility.
Engine 002/006 stay OPEN pending exact-candidate independent E2/Master disposition.


---

## FILE: GQ1_RUNTIME_PROBE_CONTRACT_MASTER_CORRECTED.md

# G-Q1 Master Corrected Runtime Probe Contract
CONTRACT ONLY / NOT EXECUTED.
Supersedes conflicting experiment/policy assertions in C contract; original retained.

## Question
Can required local semantics be preserved by shared island, bounded interception/reprojection, or separate islands for admitted profile?
Distinguish shared LocalClock, independently frozen/divergent clocks, simultaneous progression, island-wide barrier.
One Settlement is not automatically one process.

## Configurations
A shared baseline without newly introduced temporal virtualization.
B evidence-driven bounded changes only.
C separate-island control, still independently validated.
Document tick suppression/instrumentation; do not label a custom dispatch harness unmodified Vanilla.

## Controls
Same fixture lineage/semantic state, equivalent content/horizons, per-model profile/binary/patch-mode identity.
No-target-simulation save/load control and same-tick-schedule resume control.
Mutation operation has explicit grant/write-set/material accounting.
If profile changes with patches, record and justify distinct identity.

## Horizons
100/5,000/60,000/900,000 ticks as feasible, boundary transitions, save/load, immediate/subsequent resume.
Record L/G/W/M without adopting UTC canonical order.

## Frozen observations
Biological+chronological age, needs/jobs/health/immunity, plants/fire/conditions, fuel/power, reservations/assignments and global dependencies.
Only actually supported oracle dimensions get PASS/FAIL; others UNOBSERVED/UNSUPPORTED.

## Oracle
Baseline supported manifest → experiment → save → fresh load → supported manifest → explicit allowed differences → EntityId/custody/material conservation.
Use no-simulation controls for normal reconstruction effects. Bytes auxiliary provenance only.

## Allowed differences
No subsystem is allowed merely by visual/transient naming.
Frozen resident age and forbidden catch-up prohibited.
World-domain authorized mutations are separately accounted, not engine autonomy.

## Barrier
Quiesce island; apply bounded approved operation; release/resume; compare identical tick-schedule control.
Normal post-resume change is allowed per semantics; extra/unapproved mutation/catch-up is not.

## Global matrix
Candidate owner, actual mutator/clock, load dependency, material influence, revision binding, reconstructible evidence, interception/separation consequence.
Research/Ideology/Quest/WorldPawns owner remains OPEN until supported decision/evidence.

## Outputs
A sufficient / B bounded-justified / C needed for specific semantics / STILL OPEN with smaller blockers.
E1 feasibility then independent E2. No closure from this contract.


---

## FILE: WP_PIPELINE_REV6.md

# WP — Production Transaction Pipeline REV6
Owner: A. READY AFTER VERIFIED BOOTSTRAP / NOT SENT.
Baseline: exact REV5 + source_reports/QA_Production_Transaction_Pipeline_01_REV5.md.

## Objective
Narrow repair of historical decision/audit semantics and current schema comparison; preserve closed input/lifetime behavior.

## Required work
1. Define historical decision witness/order and threat boundary. Explain how observed revision at decision is established; reject reported coherent-history rewrites. Range, mutable duplicate or recomputable hash alone insufficient. Expose unsatisfied limits rather than claim PASS.
2. Complete required typed audit semantics. Validate mandatory key/type/status/reason/FailureReason/parent/scope/event/receipt/old-new revisions; reject omission/contradiction/unsupported facts; state extra-field/version policy.
3. Canonical key/index collations and relevant comparison semantics in descriptor/validation; rollback-safe case-distinct runtime canary. Do not normalize original identity semantics away.
4. Explicit versions: REV6 release is not schema version. Persistence change requires schema bump. Descriptor/signature contract change needs explicit version/documentation. Do not silently reuse old V6 identity with new meaning. Legacy handling explicit fail-closed/offline policy.
5. Actual DDL/test coverage/current manifest/source-PDB lineage/freeze documentation. Protect frozen Engine candidate.

## Regressions
Natural mixed restart/CAS losers/principal IDs; historical/audit mutations and required omissions; schema semantics/canaries; exact JSON; actual shutdown/Main/UNKNOWN; process concurrency/real hard-kill; terminal/incarnation/WAL FULL.
When claiming OS-process or kill coverage actually execute those categories.

## Deliverables
Implementation report, design rationale, actual descriptor/schema/signature, current release manifest, harness/results, negative proof, binary SHA/MVID/source/PDB identities, before/after Engine freeze proof.

## Stop
No auth/Foundation/gameplay/material/broad architecture expansion.
E1 does not close 007/schema. Independent E2 follows.


---

## FILE: WP_QA_ENGINE_GATE05.md

# WP — Engine Semantic Authority Gate05 Independent E2
Owner: Sol. READY AFTER EXACT CANDIDATE RECONCILIATION / NOT SENT.

## Objective
Independently test trusted validator lineage, expected truth immutability, exact staged semantics, lifecycle/context/content fences.

## Isolation
QA-owned copies/fixtures. Production candidate frozen before/after. No silent production rebuild or changes while reusing evidence.

## Required
1. Binary/source/census/harness/fixture/results identity.
2. Real simulator/operator task creation/launch/result proof within declared PoC threat model.
3. Capability secrecy, process identity binding, unrelated live process, replay/stale generation.
4. Task expected-manifest immutability and simulator own immutable seal equality.
5. Mandatory actual fresh native RimWorld staged-byte load.
6. Every authority context field: task, stage path/SHA, source, generations, authority/incarnation/lineage, grant/scope/map/mode, profile, manifest version, seal/result/current epoch, expected/actual semantic hashes.
7. Failures revoke relevant stale capability; scope/mode/budget/re-grant/reseal fences.
8. Both processes independently verify loaded-content profile. Test actual authority-relevant core/mod/DLC/Def/content drift and coverage; distinguish semantic digest from count-only inventory.
9. Staged bytes stable through validation/promotion; changes between phases blocked.
10. Supported saved-field mutation/malformed data checks; genuine positive controls.
11. Existing-final lock preservation/backup/atomic replacement/no unsafe fallback/first-final path.
12. Fresh A→B→C chain and supported-semantic equality.
13. Accurate bounded V4 scope; no whole game/job graph or all-mod claim.

## Evidence
Separate static inspection/runtime negative/positive/untested boundary. Test name alone is not coverage.
Provide exact freeze manifest, raw results, repro descriptions, supported scope and independent verdict.

## Verdict
PASS in declared supported scope / FAIL with blockers / BLOCKED due missing evidence.
Recommend closure; Master adjudicates. Does not automatically close G-Q1/material integration/all-mod compatibility.


---

## FILE: DISPATCHER_INSTRUCTIONS.md

# Dispatcher Instructions
Model suggestion from prior reviewed guidance: GPT-6.1 Sol / Medium.
Hourly schedule configured separately. No scheduled task has been created by this package.

## Role
Specified project conversations only. New completion result → Master; only Master-approved WP → idle recipient.
Persistent board/journal source of truth; no reliance on prior scheduled-run memory.

## Configuration
Actual repo root, Master/A/Sol endpoint identity, board/journal paths, non-overlap mechanism, enabled flag, bootstrap verification.
Missing/null config means BLOCKED. Endpoint guess prohibited.

## Run
1. Check enabled/bootstrap/config/non-overlap.
2. Read board/journal; verify conversation and current WP.
3. Detect actual final response + required artifacts, not temporary silence/PASS word.
4. Forward new originals/evidence to Master; E1/E2 clearly separated.
5. Read explicit approved next dispatch; verify revision/files/dependencies/idle.
6. Recheck journal before submitting.
7. Transmit; verify target visible message/attachments.
8. Record time/source/recipient/WP/files/message identity. If uncertain DELIVERY_UNCERTAIN; inspect before retry.
9. End without waiting indefinitely for agent completion.
10. No change → NO_CHANGE.

## Authority
User authorized project-agent result/WP transmissions within specified routes. Routine approved delivery does not need repeated confirmation.
No new WP/priorities/architecture/closure/gate/candidate edits.
Report suggestions are not Master approval.
Only approved delivery-state/journal fields change, not substantive governance.
Login/CAPTCHA/access failure → stop affected action/report.
Initial run establishes current state, never replays all past artifacts.


---

## FILE: LOCAL_RECONCILIATION_CHECKLIST.md

# Local Reconciliation Checklist
NOT EXECUTED IN THIS WEB ENVIRONMENT.

| Check | Actual result | Missing effect |
|---|---|---|
| repo root/branch/commit/git status | pending | preserve user work/locate actual project |
| root SRS/AGENTS | pending | new requirement freeze blocked |
| newest local governance | pending | compare content, not number overwrite |
| Pipeline REV5 manifest/SHA/MVID/source/PDB | pending | old E2 not attached to changed candidate |
| Gate05 binary/census/harness/results/fixture | pending | exact candidate release blocked |
| raw QA JSON/logs | pending | claim remains report-level |
| actual runtime/package versions | pending | record reproducibility differences |
| C original visible correction pointers | pending | do not freeze from raw C |
| Dispatcher endpoints/shared journal/lock | pending | unattended dispatch disabled |

Reported source root: C:/Users/user/Desktop/RimMulti/. Find actual mapping.
Pipeline E2 evidence: QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/.
No source/binaries/raw evidence for those paths are bundled except reports.

Preserve/Git checkpoint before installing docs. Merge AGENTS and governance; do not delete SRS or overwrite newer decisions.
Missing sources do not stop independent recovery work; record affected verification/design gate BLOCKED.
Bootstrap report: actual paths/git state, identities matched/changed/missing, evidence, blockers/closure scope, C rejected assertions, conflicts/merge, next NOT SENT.


---

## FILE: IDE_MASTER_BOOTSTRAP_PROMPT.md

당신은 WarEconomy / RimMulti의 새 IDE Master다. 한국어로 소통한다.

첫 작업은 재설계/구현이 아니라 local context recovery다.
docs/master-handoff-20261006/00_START_HERE.md의 읽기 순서를 따른다. 위치가 다르면 실제 패키지를 찾는다.
특히 C_REVIEW_CORRECTIONS_CONSOLIDATED.md와 역사 리뷰를 먼저 읽는다. C의 초기 원문 단정을 정답으로 freeze하지 않는다.

현재: Pipeline REV5 E2 FAIL; 001/013 좁은 CLOSED; 007/current V6 collation OPEN.
Engine Gate05 E1 accepted/E2 pending; 002/006 OPEN. G-Q1 OPEN. Foundation HOLD.
A/Sol/C 사용자 보고상 완료. 새 WP 모두 NOT SENT.

실제 root SRS/AGENTS/git 상태와 latest governance, candidate manifest/SHA/MVID/source/PDB, QA raw evidence를 대조한다.
누락/다른 hash/더 최신 결정을 기록하고 이 패키지 번호만으로 덮어쓰지 않는다.
별도 IDE_BOOTSTRAP_VERIFICATION.md를 실제 확인값으로 작성:
1) 실제 repo/SRS/AGENTS 경로와 git 상태.
2) 후보 identity/evidence matched/changed/missing.
3) blocker/CLOSED 범위/Foundation HOLD 이유.
4) C에서 채택하면 안 되는 주장 최소 6개와 controlling correction.
5) 다음 A REV6/Sol Gate05 E2, 아직 NOT SENT.
6) governance 차이/병합 결과/불확실 항목.

검증 후 시각/근거를 dispatch state에 기록하고 migration_bootstrap_verified를 true로 한다.
그 뒤 정확한 WP를 idle recipient에 전달한다.
직접 전송할 수 없으면 파일/문구만 준비하고 NOT SENT 유지.
C routine 새 WP 없음. Dispatcher는 endpoints/journal/non-overlap 확인 후 활성화.
앞으로 결정/리뷰/closure/dispatch는 매번 로컬 문서로 기록한다.


---

## FILE: SOURCE_REGISTER.md

# Source Register

Package checkpoint is 2026-10-06; produced 2026-10-07. 21 original files recovered. Original report bytes are unchanged. Source hashes identify report files, not game/Server binaries.

| File | Role | Original identity | SHA-256 |
|---|---|---|---|
| [MASTER_PROJECT_STATE_MSR-067.md](<history/MASTER_PROJECT_STATE_MSR-067.md>) | historical governance | libfile_0a9d0aa54f248191995c5c46c33502e0 | b5ce6e3bae59aaae078a01e15212bf1aae88002437c6e7d67555506df3ddccdd |
| [MASTER_DECISION_LOG_MDR-067.md](<history/MASTER_DECISION_LOG_MDR-067.md>) | historical governance | libfile_af21345099d8819186f5f925ff5f8cdf | 5e188d9cdd1c79e3666dc12ae647b6adac87ce1050afa811cc717ee0ae68f6f4 |
| [QA_DEFECT_LEDGER_QDL-064.md](<history/QA_DEFECT_LEDGER_QDL-064.md>) | historical governance | libfile_bcc0ec7df0c881919c697acc51256b7e | 8c5387a0cc7cbaad36bbbe5c3a9170a704677902c7398e609835b1aed1759aaf |
| [MASTER_AGENT_DISPATCH_BOARD_MADB-024.md](<history/MASTER_AGENT_DISPATCH_BOARD_MADB-024.md>) | historical governance | libfile_0a74c2e1d9c08191a3867f935fde2474 | 77f6127a72020ba43d5c0ca967397b0e17e6bcf20f0fbfe05119e46bd2aba56c |
| [MASTER_REVIEW_PLAYERGLOBAL_SHAREDWORLD_TEMPORAL_BOUNDARY_01.md](<history/MASTER_REVIEW_PLAYERGLOBAL_SHAREDWORLD_TEMPORAL_BOUNDARY_01.md>) | historical governance | libfile_5601650c8d3881918d73f785dddf8ebe | b8bce9703c9dc33c561752091295a950e602f2aa4bee445e4b96054a17c0fe17 |
| [POC_EngineHost_Semantic_Authority_Gate_05(2).md](<source_reports/POC_EngineHost_Semantic_Authority_Gate_05(2).md>) | report / evidence contract | libfile_63b1a67b7b4c819187cf3e86fd8d78a9 | 8749d510d794aa08b7b0482d377c0d72eab65cb51c58e692898eedd01a2fc168 |
| [QA_Production_Transaction_Pipeline_01_REV5.md](<source_reports/QA_Production_Transaction_Pipeline_01_REV5.md>) | report / evidence contract | libfile_cfc75bf826e88191aec1817355eef49c | 77605d27cd041758bf7181c3a40673e172a3e270b5ea3ebd66e58000e242bcf9 |
| [GQ1_Decisive_Runtime_Probe_Contract_01.md](<source_reports/GQ1_Decisive_Runtime_Probe_Contract_01.md>) | report / evidence contract | libfile_301b50a6313c8191a59d28875607cbf8 | be82fc7583c84111c34fde69ba437e516fbe453492af0f907d7e11e54f853416 |
| [GQ1_Temporal_Topology_Decision_Brief_REV2.md](<source_reports/GQ1_Temporal_Topology_Decision_Brief_REV2.md>) | report / evidence contract | libfile_fbe5666794ec8191a920adcbe63f6383 | f8674c838356e9f9fb7690c818e76e8ff164e163742ff4645c3aa6ac56390bec |
| [PlayerGlobal_SharedWorld_Temporal_Boundary_01.md](<source_reports/PlayerGlobal_SharedWorld_Temporal_Boundary_01.md>) | report / evidence contract | libfile_6c4f5f49c2748191b1bac5f9925dec96 | 37c506be149eef606f562be29d2c9f86d100b8c30b67c804d1282dd3e7ccb351 |
| [ADR-001_Authenticated_Identity_Central_Authority_Persistent_State.md](<reference_adrs/ADR-001_Authenticated_Identity_Central_Authority_Persistent_State.md>) | ADR original with later amendments | libfile_d6133598767481919960b8156ea31f6c | 9ce1f33842a9d3fa0a46a8811db80fb1294c12f71de6689d9045135d5487cc86 |
| [ADR-002_Tactical_Session_Offline_Combat_Authority.md](<reference_adrs/ADR-002_Tactical_Session_Offline_Combat_Authority.md>) | ADR original with later amendments | libfile_81f74b2fe348819188b9ceca2a0345aa | 99a5849e134a1b27ce9c012486f8b7abc0da1b56fafcc3bb15c0845e2be67997 |
| [ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v3.md](<reference_adrs/ADR-003_Canonical_Settlement_State_Entity_Identity_Save_Provenance_v3.md>) | ADR original with later amendments | libfile_e3fec367e0ec8191abc70510e1c0bea0 | 4bf52e85ef0a7e5ec04902b09532556e62213420635d10c8a49cb5957bc0f015 |
| [ADR-004_Distributed_Ownership_Transaction_Repair_v2.md](<reference_adrs/ADR-004_Distributed_Ownership_Transaction_Repair_v2.md>) | ADR original with later amendments | libfile_4412ccf81b688191848a94d653afb2df | 83605b985d5c5f8e80f652b17258ff7ba4fbd6364c00cf2f3d5e4752df2eb2c9 |
| [ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract_v2.md](<reference_adrs/ADR-005_Intent_Betrayal_Domain_Simulation_Event_Contract_v2.md>) | ADR original with later amendments | libfile_a39f8e4ec18c8191a85cfc7b5d528db9 | 462e2e9fcbbd5e556fc8e0624447a77ea60f55f0499abe60db3359deeb38250b |
| [ADR-006A_Temporal_Authority_ACCEPTED.md](<reference_adrs/ADR-006A_Temporal_Authority_ACCEPTED.md>) | ADR original with later amendments | libfile_b8e4a236def48191bb88fd5767019d15 | 8044b431a10b4965efcdee7a02747ef06dcff016d494420a230cc20c1ee53ac6 |
| [ADR-006B_Configuration_Content_Manifest_v2.md](<reference_adrs/ADR-006B_Configuration_Content_Manifest_v2.md>) | ADR original with later amendments | libfile_11b31845b9748191a4a84639a54ca04b | d68ce6d758ad5c93450bd6767a8d3416dbd3e1946eeb0d464ff45b8caa79fcd4 |
| [ADR-007_Ordinary_Settlement_Simulation_Authority_v4.md](<reference_adrs/ADR-007_Ordinary_Settlement_Simulation_Authority_v4.md>) | ADR original with later amendments | libfile_f4053d8799f8819195c29861d2b13a62 | 4e29479d74ec8a55a2d6c0640217514502c08436e764da0b9324c7c687387d24 |
| [ADR-008_Shared_World_Layer_Transit_World_Projection_v2.md](<reference_adrs/ADR-008_Shared_World_Layer_Transit_World_Projection_v2.md>) | ADR original with later amendments | libfile_9213b6e7ca9c8191a0b4c73c849c9f05 | 5652fe5ca47af9b963a8ec6ffd8cb3035a6424eacbb3e227afd79ddbe481fca7 |
| [QA_EngineHost_Semantic_Authority_Gate_04.md](<source_reports/QA_EngineHost_Semantic_Authority_Gate_04.md>) | report / evidence contract | libfile_045dd835489c81918981522db268d8b9 | 8cb8f52d9c3338de26a2829cc4b92c4cc5a512ede9523c608aa6da1ee2727e1e |
| [Production_Transaction_Pipeline_Slice_01_REV5.md](<source_reports/Production_Transaction_Pipeline_Slice_01_REV5.md>) | report / evidence contract | libfile_4c342ff43c748191ab013163b02d0cbb | aa4dedc234bdb29b8ec952ba15feba35082a1c51b850eb4d7d9dd2f03e495c8e |

## Not bundled
Canonical root 요구사항_명세서.md, actual repository/git/binaries/fixtures/raw QA logs. Full historical C original set not claimed available. Recover from user local sources; do not reconstruct missing wording.

## Local evidence paths from reports
C:/Users/user/Desktop/RimMulti/; Pipeline QA evidence QA-Transaction-Pipeline/PIPELINE01-REV5-20261006/. Actual mapping must be verified.

## Interpretation
Read C corrections and ADR acceptance map first. Original PROPOSED/PASS/cryptographically bound phrases are not standalone Master approval.
