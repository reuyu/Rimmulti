# WarEconomy 현재 계획 및 성과 설명

기준: 2026-10-07 Asia/Seoul, IDE Master local recovery와 최신 직접 thread/automation 대조 이후. 신규 기능 WP/release/closure를 만들지 않고 accepted 계획·현재 사실·후속 gate를 설명한다. 최신 실제 상태는 current governance와 dispatch journal의 후속 delta가 통제한다.

## 제품 목표

RimWorld 1.6의 독립 Settlement simulation과 영속 Dedicated Server world를 결합한다. World Time은 서버 실행 중 zero-player에도 진행하고 ordinary offline Settlement Local Time은 멈춘다. 멈춘 정착지에도 authorized offline attack, Auto Shop, Tax를 지원하며 실제 Pawn/건물/물건/소유권 결과가 재접속 후 보존되어야 한다.

플레이 경험은 Faction/봉건 작위·계통/Tier/영토, Caravan의 Strategic Vision·Scout·Ambush, WarPending/Alliance/Betrayal/Peace, 공동 Map 방문·전투, P2P Auto Shop/NPC Dynamic Market/Tax, 통합 관리 UI·Vanilla Letter와 운영 Console을 포함한다. Raw original SRS가 기준이고 분석 brief의 축약 ID를 canonical ID로 쓰지 않는다.

## 확보한 계약

- Server final Domain Authority, Engine/Client의 bounded simulation proposal 및 leased submission과 final canonical custody 구별.
- W/L/G/M과 resident biological/chronological aging 정책, one LocalClock writer, island-scoped barrier, target-scoped canonical publication.
- Whole Worker .rws는 context/checkpoint/extraction input이지 whole canonical replacement가 아니다.
- Stable EntityId/custody, artifact watermark vs committed material head, pending vs committed operations, exact context/profile/revision bindings.
- Stable PrincipalId와 SessionEpoch 분리, durable operation key=(PrincipalId,OperationId), terminal decision/idempotency, same-holder commit vs authority replacement fencing 구별.
- Single-scope typed atomic fast path와 staged/multi-party PREPARED/reservation path 구별; non-reconstructible material은 durable stage-before-commit.
- ADR001/003/004/005/006A/006B/007/008 core acceptance 및 후속 correction. ADR002 provisionally accepted. Acceptance는 runtime completion이 아니다.

G-Q1, exact PlayerGlobal field ownership/physical split, ordinary-client trust(G-Q2), disconnect/grace(G-Q6), inventory/tax eligibility(G-Q8), occupy 후 order policy(G-Q9), WAN remote UX(G-Q10), transit physiology(G-Q12a/b), betrayal liability(G-Q13..17), SRS TBD01..05 등은 필요 범위에서 OPEN이다. C의 초기 owner/read-only/discardable/UTC/process 단정으로 닫지 않는다.

## 이미 이룬 구현/검증 성과와 한계

### Persistence Pipeline

SQLite operation/receipt/audit/publication-event/CAS/recovery substrate와 QA-owned OS-process/hard-kill harness가 있다. REV5 독립 E2는 실제 candidate를 고정하고 concurrency/CAS/idempotency, WAL FULL, terminal 보호, incarnation, 정상 mixed restart 등을 시험했다. 001 typed input/exact JSON 및 013 actual writer/Shutdown/Dispose/Main/UNKNOWN은 tested scope에 한정해 CLOSED다. 019 prior tested closure도 유지한다.

전체 verdict는 FAIL이다. 007 historical decision observation/full typed audit consistency와 current V6 key collation admission이 아직 OPEN이다. Historical V5 schema008 closure가 current V6 인증은 아니다. PublicationEvent durable append까지만 P1이며 consumer ACK/external exactly-once를 인증하지 않았다.

### Engine Host / Remote presentation

Engine Host materialization/save/fresh-load 및 supported V4 census/job/reservation/selected saved-fields의 PoC evidence가 축적됐다. Native engine round-trip 가능성과 candidate admission/lineage가 안전하다는 것은 다른 gate다. Gate04 independent audit FAIL 이후 Gate05가 validator task/seal/stage/profile/fence/control-plane/atomic promotion을 수정했다고 E1 보고했다. Gate05 E1 accepted report이며 65/65는 independent E2가 아니다. Engine002/006 OPEN.

Remote presentation에서는 actual mouse→native Draft/Go here→async network→Worker authorization/execution→mirror apply의 제한된 정상 경로와 movement facing을 independent E2로 입증했다. Hardening05 final PARTIAL / REMAINING BLOCKER: reconnect epoch provenance, unbounded result queue/backpressure, connect lifecycle 등은 남았다. WAN/complete jobs/health/full-map/Production auth를 인증하지 않았다.

기존 Server/Common/Client의 network/time/domain/UI prototype code는 재사용 후보지만 과거 gap report의 SATISFIED/PASS를 최신 전체 Production 승인으로 승계하지 않는다. 전쟁 기준/작위 관리/Tax 체납/Settlement 공개와 Caravan 시야 같은 SRS 충돌도 해당 후속 feature gate에서 재대조한다.

### 새 Master의 recovery 성과

실제 package/SRS/AGENTS/source 경로를 복구하고 최신 history/C correction/current governance를 병합했다. Git repository 미관측을 기록하여 HEAD/clean을 가정하지 않았다. REV5 manifest12/12, prior Production recorded freeze353/353, Server PDB20/20, Common25/25를 실제 대조했다. Gate05 exact DLL/source/fixture와 matching Debug PDB4/4를 복구하고 report harness/results SHA 및 다른 Release/배포 PDB 차이를 기록했다.

삭제된 Sol endpoint의 원래 SENT proof는 보존하고 INTERRUPTED_CONTEXT_LOST로 기록했다. 사용자 지정 새 Sol thread01a11583-ff90-73e0-8916-d021e2bb038d의 read/idle와 직접 사용자 QA 보고 승인을 확인했다. Sol recovery 결과19/19 freeze/PDB4/4 matched와 실제 역방향 보고를 수신한 뒤 same-scope fresh Gate05 E2를 전달했다. 현재 SENT/ACKNOWLEDGED/IN_PROGRESS이며 verdict 없음.

## 현재 두 작업

| Track | 현재 실제 상태 | 다음 판정 근거 |
|---|---|---|
| Sol Gate05 independent E2 | 새 endpoint에 recovery 후 fresh restart 전달/수신/진행 확인 | exact unchanged candidate의 QA-owned new raw evidence, supported-scope verdict 및 limits |
| A Pipeline REV6 repair | 승인된 원본 scope를 Dispatcher outbox에 고유 ID로 등록; REGISTERED_NOT_SENT | Dispatcher actual idle/prerequisite/journal proof 뒤 SENT; 이후 A E1 freeze/manifest |

A의 실제 구현 착수/완료를 outbox 등록만으로 주장하지 않는다. 기존 사용자 hourly 자동화 WarEconomy 전달 업무 실행은 ACTIVE/A-only/QA excluded 설정을 확인했으나 target history/wait은 missing source rollout 오류로 실제 runtime 전달 미검증이다.

Master↔Sol은 direct thread tools로 소통한다. A는 Dispatcher만 담당한다. Master10분 heartbeat는 direct Sol 및 canonical Dispatcher/A_TO_MASTER_INBOX.jsonl, DISPATCHER_JOURNAL.jsonl 결과를 수집하는 별도 역할이며 Antigravity를 직접 조작하지 않는다. Substantive governance/approved outbox는 Master, A inbox/journal은 Dispatcher, independent evidence/recommendation은 Sol이 관리한다.

## 다음 순서와 완료 기준

1. **현재 두 gate 처리.** A REV6는 historical decision witness/required typed audit/current schema comparison과 explicit schema/signature evolution을 좁게 수정한다. Sol은 exact Gate05 independent E2를 수행한다. 실패/누락이면 좁은 수정/확인 작업으로 돌아가고 unsupported를 PASS로 계산하지 않는다.
2. **Pipeline REV6 independent E2.** A E1 결과·exact manifest/source/PDB/schema/signature와 freeze를 Master가 검토하고 Sol Gate05 완료/idle 후 전달한다. 변경된 candidate에 REV5 evidence를 재사용하지 않는다. 통과하지 않으면 Foundation HOLD 유지.
3. **ADR001 Production Foundation.** Pipeline E2 PASS와 scoped Master release 후 server-derived stable Principal/auth session/readiness/protocol/world/incarnation/content compatibility/capability/immutable command envelope의 최소 ingress slice를 구현·독립 검증한다. JWT/provider/TLS policy는 C brief만으로 freeze하지 않는다.
4. **최소 Player/Faction/Settlement registry.** Durable stable identity/membership/typed ownership relation/ownership epoch와 custody·execution 권한을 분리한다. 필요한 lifecycle/TBD를 구현 직전에 결정한다. Auth credentials나 War/Tier/전체 material을 registry에 섞지 않는다.
5. **첫 Settlement metadata slice: TradeConfiguration.** Ownership/config revision CAS와 durable retry/publication append로 buy/sell intent 설정을 저장한다. 물건/Silver를 예약하거나 실제 거래하지 않는다. Foundation+Registry 필요, final G-Q1/Engine topology가 모든 metadata의 blocker는 아니다.
6. **Material proof track.** Gate05 exact independent disposition 후 bounded E-B live island barrier/delta, offline exclusive material reservation/staging/semantic validation/commit/promotion/recovery, custody/identity와 material accounting을 증명한다. Engine pass만으로 Auto Shop/Tax/Occupy/Tactical material integration을 승인하지 않는다.
7. **Ordinary temporal topology와 global context.** Corrected G-Q1 contract로 Vanilla shared-island→bounded interception→separate-island control을 비교한다. Frozen/resume/save-load, resident age/hediff/jobs/plants/conditions/global dependencies, allowed differences/custody/conservation을 증명한다. Physical PlayerGlobal split이나 per-Settlement process를 선결정하지 않는다.
8. **Genesis/Caravan/실제 경제·소유권 feature.** Explicit server-authorized genesis와 durable admission, transfer/custody와 temporal/context bindings를 검증한 뒤 작은 end-to-end material slice부터 통합한다. G-Q8/TBD05 등 product-dependent eligibility/tax policy는 해당 feature 전에 결정한다.
9. **Remote Tactical/전쟁·외교/봉건 시스템/UX.** Presentation reconnect/queue/liveness와 relevant WAN gate를 통과하고 own-Pawn commands, online/offline defense transition, combat result persistence를 통합한다. Alliance1-hop, intent-aware betrayal, feudal lifecycle, strategic vision, NPC market, Tax, UI/letters를 SRS 원문과 각각 대조하며 feature-level E1/E2를 거친다.
10. **통합/운영 acceptance.** Fresh start/reconnect/restart/restore, concurrency/failure recovery, profile/mod compatibility의 declared scope, end-to-end SRS acceptance와 operator audit/backup/config를 검증하여 release한다. Deadline/완료율은 승인된 WBS와 측정 근거 없이 숫자로 단정하지 않는다.

현재 우선순위는 새로운 gameplay를 늘리는 것보다 Pipeline과 Engine candidate의 남은 correctness gate를 독립 증거로 통과시키는 것이다. 그 다음 metadata foundations를 먼저 진전시키고 material/temporal/presentation의 각 proof track은 필요한 범위에서 병행한다. 이 설명은 새로운 broad implementation 승인이 아니다.
