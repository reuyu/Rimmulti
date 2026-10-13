## 4. Real graphical Draft loop — confirmed

맵 위 Human302를 실제로 클릭해 선택·정보창·기즈모를 확인한 뒤 Draft 버튼을 클릭했다.

2026-10-02 **12:52:27 KST** (raw log UTC 03:52:27), Frame 9975:

```text
NATIVE_GIZMO label=Draft                         GUI=Used
DRAFT_ENTER target=True                        draft=False, job=GotoWander
RPC_ENTER type=DRAFT source=REAL_GUI_GIZMO       draft=False, job=GotoWander
WIRE_RESPONSE status=ACCEPTED                   ownBeforeApply draft=False
APPLY_ENTER                                    draft=False
DRAFT_ENTER / EXIT under Reconciling=True       draft=True, job=Wait_Combat
APPLY_EXIT accepted=True                        draft=True
```

독립 Worker query에서도 Draft=true를 확인했다. GUI adapter가 원래 setter의 즉시 로컬 변경을 억제했으며, 응답을 적용하기 직전까지 client Draft=false였다. 최종 Draft=true는 승인된 Worker snapshot 적용 과정에서 발생했다. 시험 전 client와 Worker가 모두 미징집 상태였음도 대조했다.

**이 Draft slice의 필수 loop는 확인됐다.** 다만 같은 apply에서 Worker rotation=3이 client rotation=2로 표시되는 결함도 확인됐다. Draft 성공을 다른 필드의 정확성까지 확장하지 않는다.

증거: `before-gui-draft-{client,worker}.json`, `after-gui-draft-{client,worker}.json`, `GraphicalClient/qa-events.tsv`, [own-selected-before-draft.png](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/own-selected-before-draft.png), [own-drafted.png](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/own-drafted.png).

## 5. Real Move loop — intent / execution confirmed; repeated presentation fails

Human302를 선택·징집한 상태로 실제 바닥을 우클릭했다. native GUI event는 `mouseDown`이었다.

2026-10-02 **12:53:50 KST** (UTC 03:53:50), Frame 14958:

```text
ORDER_ENTER requested=Goto                       local job=Wait_Combat
RPC_ENTER type=MOVE source=REAL_GUI_FLOATMENU      local job=Wait_Combat
WIRE_RESPONSE status=ACCEPTED                     local job=Wait_Combat before apply
APPLY_ENTER seq=8
ORDER_ENTER under Reconciling=True                requested=Goto
APPLY_EXIT accepted=True                          position=(139,0,142)
```

Worker는 autonomous cadence로 목적지 **(147,142)**까지 이동했다. QA는 이 이동을 위해 STEP 또는 TicksToSimulate를 보내지 않았다. Worker의 native ordered job 실행과 위치 변경을 독립 query로 확인했다.

그러나 이후 Worker STATUS를 25회 측정하는 동안에도 client는 다음 상태를 유지했다.

```text
position=(139,0,142), Draft=true, job=Wait_Combat
LastAppliedSnapshotSequence=8, RPC calls=2
```

Worker는 이미 (147,142)에 도달했고 G=4672 → 4972로 계속 진행했다. **Worker의 진행을 client가 계속 따라가는 반복 replication은 없었다.** client Update는 external control queue를 처리할 뿐, periodic GET_SNAPSHOT / unsolicited snapshot receiver / delta stream은 없다.

A의 DEMO_08은 TestHarness `:298`에서 명시적으로 GET_SNAPSHOT을 보내 한 번 refresh한 결과다. operational repeated replication의 증거가 아니다. 후속 negative test를 준비하며 QA가 명시적 GET_SNAPSHOT을 보내자 client 위치도 따라갔지만, 이것은 **시험 준비용 refresh**이지 누락 기능을 해결한 것이 아니다.

증거: `before-gui-move-*.json`, `move-progression-worker-{start,end}.json`, `move-no-qa-poll-client.json`, `active-status-latency.json`, [move-mirror-stalled-valid.png](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/move-mirror-stalled-valid.png).

## 6. Local side-effect negative / foreign GUI authorization

같은 frozen graphical client에서 **Human305 (Player_B)**를 실제 선택하고 Draft 버튼을 클릭했다. 거부 전후 상태를 정확히 비교하기 위해 Worker cadence를 정지하고, 시험 직전 client를 정규 snapshot으로 동기화했다.

- GUI callback 진입: Human305 Draft=false, GotoWander.
- Worker response: **AUTH_REJECTED**.
- client callback 종료: Draft=false, GotoWander.
- **대상 Pawn의 native XML 전체가 전후 동일했다.** 위치·job target·health/Hediffs·selection도 같았다.
- 가짜 Draft 성공 상태는 발생하지 않았다. 거부 응답에 포함된 정규 snapshot은 적용되지만 거부된 command를 성공 처리하는 변경은 없었다.

own Move에서도 응답 수신·적용 직전까지 local job은 Wait_Combat이었다. 미승인 local Goto는 시작하지 않았다. reconciliation 내부의 native job callback은 section 9에서 별도로 검토한다.

증거: `before-foreign-gui-{client,worker}.json`, `after-foreign-gui-{client,worker}.json`, GUI log UTC `03:56:12`, Frame 23478.

## 7. Worker progression / liveness / budget

증거: [progression-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/progression-results.json), `Worker/qa-worker-slices.tsv`, `active-status-latency.json`; candidate `RemoteWorkerController.cs:154–181`, `:416–443`.

| 항목 | 독립 결과 / 제한 |
|---|---|
| 자율 진행 | 3.651초 동안 G=10347 → 10560, 관측58.34 TPS. native path가 목적지까지 진행한 사실도 확인. |
| active STATUS 응답 | 이동 관찰 중25 samples: 평균15.66ms, 최대37.28ms. 별도12 samples도 응답. loopback·소규모 정상 부하 범위. |
| automatic slice | source의 `Math.Min(desiredTicks,5)` 확인. legacy STEP 전8,771 update samples의 관측 최대는3 ticks. 최대5까지 실제 사용했다는 의미는 아님. |
| wall-clock | native tick 이후 elapsed>=8ms이면 break하는 **협조적 체크**는 있음. single tick을 preempt할 수 없으며 Update 전체의 엄격한8ms 상한도 아님. |
| whole Update 측정 | 최대158.8193ms, 8ms 초과19회. command 처리·observer overhead 포함. 개별 native tick이나 cadence loop만의 소요 시간은 아님. |
| queue / legacy path | 무제한 queue drain, STEP_TICKS 및 TicksToSimulate의 monolithic loop가 남아 있음. cadence 정지 상태에서 STEP_TICKS=6도 ACCEPTED. bounded cadence와 모든 command 경로의 boundedness는 별개. |
| pause | native pause 후 G=10567 → 10567. |
| disable | SET_PROGRESSION=0 후 G=10605 → 10605. |
| cancel | transaction / queued-command cancellation API는 이 후보에 없음. disable은 이미 실행 중인 monolithic command의 cancel을 보장하지 않음. |

추가 정적 결함: `:169`는 **실제로 실행한 ticks가 아니라 desiredTicks 전체**를 accumulator에서 뺀다. 5-tick cap이나 시간 체크로 실행하지 못한 debt도 사라진다. runtime stall injection을 추가 수행하지 않았으며, 이 항목은 식에 근거한 정적 결함으로 구분한다.

**ADR-006A 구현 완료는 인증하지 않는다.** native DoSingleTick / global TicksGame, world / foreign-map dispatch, temporal materialization / publication의 기존 문제가 이 cadence로 해결되지는 않는다. A의 “ADR-006A compliant / hard8ms / no monolithic”이라는 포괄 판정은 수정이 필요하다.

## 8. Snapshot fencing — narrow response guard confirmed

### Direct poisoned snapshot tests

각 vector에는 잘못된 위치, Draft 반전, job=None, health=0, Dead/Downed=true, Burn def를 넣었다. metadata 한 종류씩을 잘못 설정하고 기존 `ValidateAndApplySnapshot`을 호출했다.

| Vector | Response | 대상 Pawn native state 전후 |
|---|---|---|
| SnapshotSequence == LastApplied | OUT_OF_ORDER | 동일 |
| wrong TacticalSessionId | WRONG_SESSION | 동일 |
| wrong WorkerGeneration | WRONG_GENERATION | 동일 |
| wrong TargetMapId | WRONG_MAP | 동일 |

### Actual TCP response replay / delay

별도 QA proxy에서 fresh seq=36이 이미 적용된 뒤, 과거의 **51-Pawn 실제 응답(seq=2)**을250ms 지연하여 C# client의 실제 reader에 전달했다. client는 seq=36을 유지했고, rejection counter가1 증가했으며 대상 Pawn의 native state는 같았다. 다음 fresh seq=38은 정상 network 경로로 받아들였다.

이는 **application response의 지연 및 과거 응답 replay**다. TCP byte stream의 packet reorder를 재현한 것은 아니다. 첫 proxy vector는 로딩 도중의0-Pawn 응답이어서 guard에 들어가지 않았다. 합격 근거에서 제외하고,51-Pawn vector를 확인한 `v2-*` 보정 시험을 수행했다. 첫 증거도 보존했다.

증거: [focused-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/focused-results.json), `fault-*.json`, [v2-wire-proxy-events.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/v2-wire-proxy-events.json), `v2-wire-stale-{before,after}.json`.

제한: reconnect/session epoch의 완전한 인증 계약과 server command의 TacticalSession binding은 미해결이다. wrong session을 넣은 GET_SNAPSHOT command는 Worker에서 ACCEPTED됐다. 별도로 stale command generation은 STALE_GENERATION_REJECTED, hostile AI Pawn 명령은 AUTH_REJECTED를 확인했다.

## 9. Reconciliation correctness / narrow graph scope

| 상태 | 독립 결과 |
|---|---|
| identity | 같은 fixture의 native ThingID를 비교. Human302 / Human305의 대응 확인. server canonical EntityId ↔ context-local native ID mapping은 아님. |
| position | 응답 수신 시점의 위치 적용은 동작. Worker의 지속적인 변화는 반복 전달되지 않음. |
| Draft | 승인 전 로컬 변경 억제와 authoritative 적용 확인. foreign rejection 전후 동일. |
| 4 rotations | Worker native0/1/2/3 → wire `"0"/"1"/"2"/"3"` → client **2/2/2/2**. South만 일치. |
| current job | Goto / None 한정 처리는 추가됐지만 mirror Goto의 target은 **실제 목적지가 아니라 snapshot의 현재 위치**. 실제 Move 적용 후 client가 Wait_Combat에 남음. 일반 job graph/status 일치가 아님. |
| health / Hediff | existing Stab severity를 QA-local에서3→4로 바꾸고 fresh snapshot을 적용해도4 유지. source는 없는 def 추가만 수행. severity/body part/occurrence ID/removal/Dead/Downed 복원 없음. |
| native damage trial | APPLY_DAMAGE는 ACCEPTED였지만 Worker/client 모두 신규 Cut 없음, Hediff3개, health=1. 응답 문구만으로 injury replication을 PASS 처리하지 않음. 반복 refresh 후에도3개 유지. |
| grid / selection | checkpoints에서 Human302/Human305의 ThingGrid reference=1, spawned ThingID 중복0. selected Human305도 유지. spawn/despawn/death/map transfer 시 reference 안전성은 미시험. |
| callback side effects | IsReconciling이 recursive RPC를 억제함. native Draft/job callback 자체를 무부작용으로 만들지는 않음. 같은 위치를 target으로 하는 Goto mirror job 등 올바른 job/status 표시가 미해결. |
| wrong-map apply | wrong TargetMapId는 metadata gate에서 거부. 그러나 apply 대상은 여전히 Find.CurrentMap. expected Map_0과 실제 표시 Map이 다른 경우의 binding은 정적으로 미해결. 이번 실제 GUI 시험은 map0에 한정. |

Location: `RemoteWorkerController.cs:501`, `RemoteClientController.cs:285–368`, `Protocols.cs`의 PawnReplicationData. rotation 주석이 canonical 문자열을 선언해도 Worker가 native 숫자 값을 출력하는 구현은 그대로다.

items/buildings/projectiles/reservations/fire/zones/power/bills/entity lifecycle 등 full-map replication은 구현·검증하지 않았다.51-Pawn set을 canonical Settlement graph나 완전한 Tactical projection으로 인증하지 않는다.

## 10. Dependency-clean / authentication surfaces

### Clean-load claim rejected

두 실제 process에서 올바른 fixture hash 및 A의 active profile로 다음 오류를 재현했다.

- missing `QAEngine02.GameProbe` / `MapProbe` → abstract component load exception;
- missing `WarEconomy_TacticalProofToken` ThingDef;
- unresolved / null spawn 등 semantic load error.

client log `:58`, `:64`, `:69`, Worker log `:4171`, `:4177`, `:4182`. 실제 붉은 debug log 화면을 [graphical-load-errors.png](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/graphical-load-errors.png)에 저장했다.

A의 **dependency-clean fixture** 주장은 잘못됐다. 기존 **QA-ENGINE-002 class**의 미해결 증상 및 QA-PRESENT-009의 지속으로 연결한다. 중복 QA-ENGINE ID를 만들거나 기존 결함을 닫지 않는다. surviving Pawn의 좁은 GUI 증거는 유효하지만 안전한 canonical load의 증거는 아니다.

### TestSurface flag is not isolation

`SET_PROGRESSION(CustomData=0)`을 **INVALID_TOKEN / Generation=999 / WRONG_SESSION**으로 보내도 ACCEPTED, TestSurface=true였다. `LOAD_SAVE / SET_GENERATION / SET_PROGRESSION`은 같은 Worker endpoint에서 auth check보다 먼저 실행된다. boolean flag는 실제 authorization 또는 endpoint 격리가 아니다.

static Player_A/B token은 fixture 한정이다. 정상 GUI gameplay command는 ownership / command-generation check를 통과하지만 production authentication 또는 server-issued capability를 증명하지 않는다.

## 11. Metrics / previous ~14.9KB discrepancy

| 실제 측정 대상 | Actual UTF-8 bytes / scope |
|---|---|
| GUI Draft response | 전체 응답 **15,062 bytes**, snapshot JSON **14,857 bytes**, **51 Pawns** |
| GUI Move response | 전체 응답 **15,101 bytes**, snapshot JSON **14,875 bytes**, **51 Pawns** |
| foreign GUI rejection response | 전체15,166 bytes, snapshot JSON14,894 bytes,51 Pawns |
| explicit GET_SNAPSHOT10 samples | 각 전체15,115 bytes,51 Pawns. 해당 fixture의 현재 상태와CommandId 등에 의존. |
| independent PING | **374 bytes,0 Pawns**. A의336B는 같은 empty PONG 계열이며 Pawn snapshot이 아님. |
| delta / periodic snapshot | **구현 없음 / 측정 대상 없음**. full response를 delta라고 부르지 않음. |

GUI wire size는 candidate의 실제 reader가 받은 문자열에서 UTF-8 byte count를 구했다. snapshot은 candidate `SerializeSnapshot`의 JSON section을 따로 계수했다. envelope를 포함한 응답 크기와 구분했다.

GET_SNAPSHOT10회 external-QA loopback roundtrip: 최소 **17.63ms**, 평균 **36.78ms**, 최대 **51.92ms**. QA socket → Unity queue → candidate SendCommand → Worker → reconcile → QA 응답까지 포함한다. 순수 client-worker RTT나 GUI-visible latency가 아니다.

앞선 약14,968B의51-Pawn 응답과 이번 약15KB는 모순되지 않는다. 새 metadata/state/envelope 차이가 있다. **336B participant delta로 압축됐다는 증거는 없다.** A TestHarness `:492`는 여전히 PING을 측정하며, `SnapshotSizeBytes`는 client `respJson.Length`라는 문자 수다. ExecutionToClientVisibleUpdate도 reconciliation 이전의 수신 시각을 쓴다.

WAN 추정치, 최종 NFR SLO, render FPS, input-to-displayed-frame percentile은 인증하지 않는다.

## 12. QA-PRESENT-001..010 recommendations

이는 **Master에게 제출하는 결함별 권고**다. 공식 ledger를 수정하지 않았다. CONFIRMED RESOLVED는 표에 명시한 좁은 범위만 뜻한다.

| Defect | Recommendation | 근거 / 남은 작업 |
|---|---|---|
| **QA-PRESENT-001** | **CONFIRMED RESOLVED** | 실제 Draft/right-click이 candidate adapter에서 Worker로 전달됨. 수신 전 로컬 Draft/Goto 없음. foreign GUI 거부 전후 상태 동일. 지속적인 Move 표시는 QA-PRESENT-002로 미해결. |
| **QA-PRESENT-002** | **PARTIAL** | 자율 Worker 진행·pause/disable 확인. **자동 반복 replication 없음**. accumulator debt 제거도 남음. |
| **QA-PRESENT-003** | **CONFIRMED RESOLVED** | 시험한 response admission의sequence/session/generation/map guard, poisoned state 불변, 실제TCP 과거 응답 거부 확인. production session/command binding은 제외. |
| **QA-PRESENT-004** | **PARTIAL** | guarded Draft apply와 제한된job 처리 개선. destination/status·health graph·lifecycle·native callback side effect는 불완전. |
| **QA-PRESENT-005** | **STILL FAILING** | 4방향 시험에서 numeric wire → South 고정 재현. |
| **QA-PRESENT-006** | **STILL FAILING** | TestSurface flag만 추가. 무인증control command를 같은endpoint에서 수용. fixture token은 production 인증 근거가 아님. |
| **QA-PRESENT-007** | **PARTIAL** | automatic cadence에tick cap/soft time check 추가. main-thread blocking ReadLine, 무제한queue drain, legacy monolithic command는 남음. |
| **QA-PRESENT-008** | **STILL FAILING** | A의GUI 증거 분류가 direct method call을 포함. repeated replication은 manual query. PING을snapshot size로 보고하며visible latency oracle도 부정확. |
| **QA-PRESENT-009** | **STILL FAILING** | 같은fixture/active manifest에서dependency semantic error 재현. QA-ENGINE-002 class로 연결. |
| **QA-PRESENT-010** | **STILL FAILING** | metadata rejection은 추가됐으나reconcile target은Find.CurrentMap 유지. expected binding으로 actual Map을 선택하지 않음. 정적 근거로 지속 판정. |

필요 수정 위치:

1. `RemoteClientController.cs:372` Update/receive 경로: Move 이후 Worker 진행을 자동·반복 전달해 mirror가 따라가도록 구현.
2. `RemoteWorkerController.cs:501` / client `:320–324`: native numeric rotation과 wire representation 일치.
3. client `:338–364`: 실제 destination/status 처리 및 지원 health scope의 정확한 oracle.
4. client `:287`: session-bound Map을 선택하고 viewed Map과 authority target을 구분.
5. Worker `:215–249`, `:154`, `:416–443`, client `:183`: control isolation, bounded command dispatch, timeout/liveness.
6. fixture/profile dependency 정리 및 semantic error가 있는 로드를clean으로 판정하지 않는 검증.
7. TestHarness `:186`, `:256`, `:298`, `:492`: method invocation/explicit refresh/PING과 real GUI/operational replication/snapshot 구분.

새 광범위 PoC를 자동 요구하지 않는다. 우선 **실제 Move의 반복 replication 경로**를 완성하고 동일한 좁은 interaction을 재검증할 것. QA observer를 기능 구현으로 사용해 합격 상태를 만들어서는 안 된다.

## 13. Completion / final architecture statement

- 정상 graphics client에서 actual Draft/Move/foreign rejection을 독립 수행했고, 직접 메서드 시험과 분리했다.
- snapshot admission/실제TCP 과거응답,4 rotations,severity,cadence/pause/legacy boundary,payload를 focused tests로 검증했다.
- QA 두 process는 PID·실행 경로·시작 시각을 대조해 종료했다. 이번 observer junction만 제거했으며 source/DLL/logs/frames/test scripts는 보존했다. [cleanup.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN02-20261002/cleanup.json).
- 기존 Production/candidate mod junction은 변경하지 않았다. Master state/defect ledger도 편집하지 않았다.

**P2 feasibility:** 시험한 Draft interaction은 입증됐다. 실제 Move intent와 Worker execution도 입증됐지만, 지속적인 mirror 추종은 실패했다. 따라서 요청된 Draft+Move presentation slice 전체의 gate는 미통과다.

**Candidate C:** PROVISIONAL 유지 권고. 이번 부분 성공으로 ADR-002를 최종 ACCEPTED로 승격하지 않는다.

**ADR-002 최종 acceptance 전 조건:** 지원 interaction의 반복 authoritative replication과 올바른 state/fencing/map lifecycle, 안전한 dependency-complete materialization, 검증된 Worker liveness/temporal/publication 경계, accepted ADR-003/006A/007 및 후속 ADR-004/008과의 구현 계약이 필요하다. 기존 QA-ENGINE-002/003/004/005/006을 이 presentation 결과로 닫지 않고, loopback 값을WAN/final NFR SLO로 승격하지 않는다. 상세 최종 gate와 승인 여부는 Master가 결정한다.

**본 보고서로 작업을 종료하고 다음 Master 지시를 기다린다.**
