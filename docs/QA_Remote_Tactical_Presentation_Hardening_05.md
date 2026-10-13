# QA Remote Tactical Presentation — Hardening 05

[QA REVIEW]

- **Work Package:** WP-QA-REMOTE-PRESENTATION-HARDEN-05
- **Role:** Independent QA / Architecture Reviewer
- **Target:** `Remote_Tactical_Presentation_Hardening_04_REV1.md`의 exact frozen candidate
- **Final Verdict:** **PARTIAL / REMAINING BLOCKER**
- **검증일:** 2026-10-02, 실행 증거의 시각은 UTC
- **Master에게 제출하는 권고:** Candidate C는 **PROVISIONAL 유지**. Master state/defect ledger는 변경하지 않았다.

## 1. 판정 요약

실제 OS 마우스 입력 → 네이티브 Draft / Go here → GUI interceptor → 비동기 명령 → Worker 권한 검사·실제 엔진 실행 → 응답 → 메인 스레드 mirror 반영은 독립 재현됐다. 실제 이동 네 방향과 경로 전환의 facing도 개선됐다. 그러나 **이전 연결에서 파싱된 스냅샷이 재접속 후 새 epoch로 잘못 표시되어 적용되는 경합**과 **상한 없는 결과 대기열**이 남았다. 좁은 정상 GUI 경로의 성공을 전체 timeout/epoch/queue gate 통과로 확대할 수 없다.

| 검토 항목 | 독립 결과 |
|---|---|
| actual OS/user async Draft / Move E2 | 검증한 정상 interaction slice에서 입증 |
| GUI command network wait / local speculation | off-main I/O, 승인 전 Draft/Goto commit 억제 확인 |
| 지연·timeout·종료 시 interactive liveness | 검증한 loopback fault window에서 동작; 전체 connect lifecycle 보장은 아님 |
| timeout / epoch / queue semantics | **미통과:** old received response의 epoch 오표시, result queue 무상한 |
| 실제 이동 중 authoritative facing | 네 방향·전환·focus 우선순위의 검증 범위에서 통과 |
| frozen profile/listener startup | 지정 포트 정상; 그래픽 Client 정상. headless Worker의 atlas 예외는 별도 잔존 |
| general job/health/full-map/Production auth | 인증하지 않음 |

## 2. Freeze, provenance, 실행 구성

Production과 candidate는 수정·재빌드하지 않았다. QA-only observer만 빌드했다. 재접속 경합의 정확한 수신 지점을 관찰하기 위해 observer를 한 번 확장하고 같은 candidate DLL로 프로세스를 재시작했다. 첫 실행 로그는 `Phase1/`에 별도 보존했다.

| 항목 | 독립 확인 |
|---|---|
| candidate SHA256 | `55182E92E1E077181B3B944E4EA450F7623E47BCD45084E4FEB0ECD22BD34E3E` |
| fixture SHA256 | `ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED` |
| 실제 로드 DLL 경로 | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.RemotePresentation.PoC\1.6\Assemblies\WarEconomy.RemotePresentation.PoC.dll` |
| 실제 로드 MVID | `eb3374c2-b212-4dc0-8719-0462ebc0e833` — Worker/Client 일치 |
| A manifest source/runner/result/fixture/DLL | 광고된 10개 파일 모두 해시 일치; 검증 종료 후 변경 0개 |
| Production 보호 파일 | 130개, 전후 변경·추가·삭제 0개 |
| 그래픽 Client | `Direct3D11`, 실제 **1920×1080**, client ticks 0 |
| Worker | `-batchmode -nographics`, 독립 프로세스 |

A runner는 evidence 삭제와 profile 재생성을 수행하므로 실행하지 않았다. **동결 runner의 flags/active mod profile을 복제**하고 QA 저장 폴더·로그·observer만 추가해 독립 실행했다. 게임 명령·제어·dependency 포트는 runner와 동일하다. runtime screenshot 해상도와 `Screen.width/height`를 확인했으며, CLI의 1280×720을 실제 해상도로 간주하지 않았다.

근거: [freeze 전 manifest](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/identity-before.json), [freeze 후 manifest](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/identity-after.json), [실제 로드 모듈](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/GraphicalClient/qa-module.txt), [첫 실행 topology](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/phase1-launch.json), [재실행 topology](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/launch-pair.json), [최종 무결성 감사](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/final-audit-summary.json).

## 3. 실제 OS GUI 증거와 authority loop

아래 행동은 computer-use의 native OS mouse input으로 수행했다. `Selector.Select`, `ProcessInput`, `TryTakeOrderedJob`, `SendCommand`를 테스트 코드에서 직접 호출한 결과를 GUI proof로 세지 않았다.

1. 자신의 Strange/Human302 초상화를 실제 클릭·더블클릭하여 선택하고 맵/inspect pane을 확인했다.
2. 네이티브 Draft 기즈모를 실제 클릭했다. `GUI=Used`, main thread 1에서 setter interceptor가 호출됐다. 같은 callback 종료 시 Draft는 여전히 false였다. thread 64의 I/O 응답 후 main thread 1의 `IsReconciling=True` 구간에서 true로 바뀌었다.
3. 실제 지형/Nick 위치를 우클릭하여 네이티브 FloatMenu를 열고 **Go here**를 실제 클릭했다. `ORDER_ENTER requested=Goto` → `ASYNC_EXIT` → Worker accepted Goto → 자율 progression → 반복 스냅샷으로 위치·DrawPos가 변했다. 승인 전 local authoritative Goto는 시작하지 않았다.
4. 도착한 폰의 실제 렌더링 위치를 클릭했다. 올바른 폰 선택, inspect pane, hit target을 확인했다.
5. Nick/Human305 초상화를 실제 클릭하고 Draft를 실제 클릭했다. Worker가 `AUTH_REJECTED`를 반환했고 Nick의 Draft=false가 유지됐다. 거절 후 지속되는 가짜 징집 성공 상태가 없었다.

정상 Draft `CMD_ee35c72e`의 network 처리 span은 39.7839ms였다. 실제 GUI 명령 13개의 **Submit enqueue span**은 0.1322–0.7358ms였다. 이 값은 전체 `Command_Toggle.ProcessInput` 소요 시간을 재는 값이 아니므로 A의 전체 GUI callback 값과 동일 지표로 취급하지 않는다.

근거: [native Draft 화면](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/native-normal-draft.jpg), [실제 Go here 메뉴](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/native-go-here-menu.jpg), [도착 위치 선택 화면](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/native-destination-selection.jpg), [외국 폰 거절 화면](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/foreign-native-rejected.jpg), [GUI/네트워크/apply trace](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/Phase1/GraphicalClient/qa-events.tsv).

## 4. Thread, timeout, failure, retry

`SubmitCommandAsync`는 GUI main thread에서 enqueue만 한다. `ProcessInteractiveCommandOffMainThread`의 serialization/write/read와 `ParseResponse`는 background thread에서 관찰됐다. `ValidateAndApplySnapshot`, Draft 및 native Pawn mutation은 main thread에서 관찰됐다. 반면 **ConnectToWorker → ConnectCommandSocket의 동기 TcpClient.Connect는 initial/external reconnect 호출 시 main thread에서 실행**된다. 또한 synchronous `SendCommand` test wrapper는 main-thread wait를 유지한다. wrapper로 얻은 결과는 interactive liveness 증거로 사용하지 않았다.

| Fault | 실제 timeout / response delay | 관찰 결과 | epoch / local apply | frame 증거 |
|---|---|---|---|---|
| normal native Draft | 4000ms / 정상 | Accepted, 39.7839ms network span | epoch 2, 응답 후 적용 | 네이티브 callback은 enqueue 후 즉시 반환 |
| native Draft 2초 지연 | **4000ms** / 2000ms | Accepted, 2072.5241ms | epoch 3, 대기 중 기존 true 유지, 승인 후 false | reset-to-capture window의 candidate frame peak 94.6181ms |
| native Draft 기한 초과 | 4000ms / 5000ms | TimedOut, 4020.4403ms | epoch 3, mirror false 유지; 늦은 응답 적용 없음 | 해당 reset-to-capture peak 96.8065ms |
| native Draft 응답 전 소켓 종료 | 4000ms / 즉시 종료 | TransportFailed, 11.2326ms | epoch 4, false 유지 | 독립 fault 구간 gap 19.0907ms |
| scripted async 800ms deadline | **800ms** / 1500ms | TimedOut, 795.8323ms processing span | enqueue-to-deadline와 socket remainder 사용; 늦은 응답 적용 없음 | 독립 fault 구간 gap 22.6784ms |
| 실제 native Draft pending 중 reconnect | 4000ms / 3000ms | 전송 중 연결 종료로 network state TimedOut; main drain은 old epoch result를 invalidation | epoch **10→11**, old command의 Draft 적용 없음 | reset-to-capture peak 17.4416ms |

Network span은 전체 GUI-to-apply RTT와 같지 않다. 800ms 시험은 socket write 이전 대기 시간을 deadline에서 빼므로 off-main method span이 800ms보다 작을 수 있다. 첫 번째 수동 재접속 시도는 응답이 먼저 완료되어 pending race 증거로 제외했고, 프록시가 실제 native Draft를 감지한 직후 재접속하는 별도 재현을 사용했다. 2초·5초 시험의 frame peak는 정확한 network subinterval만의 최댓값이 아니라 reset부터 상태 capture까지의 **보수적 상한**이다. startup/load, DUMP, QA fault로 apply를 의도적으로 중지한 구간은 정상 GUI frame SLO로 사용하지 않았다.

**A의 2초 성공 / 800ms 모순:** native adapter의 실제 기본 timeout은 4000ms이고 A의 timeout test는 명시적으로 800ms를 전달한다. 따라서 서로 다른 시험이다. 모든 command socket이 800ms라는 보고서 설명은 수정해야 한다.

동일 CommandId를 보존한 Draft 재전송은 Worker `_commandHistory`에서 응답을 재사용했고 Draft를 두 번 toggle하지 않았다. 같은 ID의 payload를 Move로 바꾸면 기존 Draft 성공 응답과 `IDEMPOTENT_RETRY`가 반환됐으며 Move 효과는 없었다. **payload collision validation, durable idempotency, Production authentication을 입증한 것은 아니다.** history는 100개 cache이고 duplicate lookup은 현재 authorization/generation 검사보다 앞선다. 이 PoC의 collision/identity scope는 후속 계약에서 명시해야 한다.

근거: [fault trace 요약](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/phase1-command-faults.json), [native pending reconnect trigger](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/native-reconnect-trigger.json), [retry/fence 단위 결과](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/regression-checks.json), [sync connect 위치](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/Reviewed/Client/RemoteClientController.cs:269).

## 5. 잔여 결함 — QA-PRESENT-007 하위 근거

### H05-01 — High: old received snapshot이 새 transport epoch로 재표시됨

- **위치:** `RemoteClientController.cs:992–995`, `Disconnect:1258`, `Update:1215`.
- **원인:** periodic request의 송신 epoch를 보존하지 않고, 응답 파싱 후 coalesced slot에 넣는 순간의 **현재 TransportEpoch**를 `_pendingSnapshotEpoch`로 기록한다. disconnect가 slot을 비워도 아직 slot에 들어오기 전의 old response를 막지 못한다.
- **정확한 재현:** 실제 periodic TCP 응답을 수신·파싱한 후, QA observer가 background ParseResponse 반환 직전만 지연시켰다. 이 observer는 candidate의 필터/epoch/DTO를 바꾸지 않았다. main thread에서 disconnect/reconnect했고, Worker의 Draft를 true→false로 되돌린 뒤 old parsed response를 재개했다.
- **기대:** old connection의 snapshot은 새 연결에서 폐기된다.
- **실제:** old snapshot **sequence 7**이 새 **epoch 6**으로 coalesced되어 accepted/apply됐다. 새 연결의 client Draft=false가 **true로 변했으며**, 현재 Worker Draft는 false였다.
- **필요 수정:** request/connection 생성 시점의 immutable transport context를 응답까지 유지하고, receive/coalesce/apply 모두에서 검사해야 한다. arrival 시점의 current epoch로 old data를 재표시하면 안 된다. snapshot metadata fence만으로 transport fence를 대신하지 않는다.

별도 요구였던 **이미 coalesced된 snapshot** 경합도 실행했다: epoch 7의 sequence 3064를 slot에서 확인한 뒤 disconnect/reconnect하면 slot은 비워지고 epoch 9로 진행했다. 이 세부 시험은 통과했다. 하지만 그 결과가 위 **received-before-coalescing** race까지 해결했다는 뜻은 아니다.

근거: [old-response 실제 Draft 오염](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/epoch-race-summary.json), [실제 수신/apply trace](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/GraphicalClient/qa-events.tsv), [재현 스크립트](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/receive_race_mutation.py), [observer delay만 수행하는 코드](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/ObserverMod/Source/ParseBarrier.cs), [이미 coalesced된 race trace](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/Phase1/GraphicalClient/qa-events.tsv).

### H05-02 — Medium: 결과 queue는 bounded가 아님

- **위치:** `RemoteClientController.cs:113–115`, `ProcessInteractiveCommandOffMainThread`의 result enqueue, `Update:1062`.
- **시험:** candidate main-thread apply만 지연시킨 QA fault 상태에서 실제 `SubmitCommandAsync`로 100개씩 10회, **1000개** 요청. QA가 결과를 대신 처리하거나 queue 상한을 구현하지 않았다.
- **실제:** 273개 admit / 727개 QUEUE_FULL. send queue high-water **32**. result queue는 snapshot capture 시 **267**, 전체 관찰 high-water **273**. `_cmdResultQueue`에는 상한·backpressure가 없다.
- **회복:** apply 재개 후 최대 **5개/frame** drain; 약 **897.839ms** 동안 결과를 분산 처리했다. 이 시험에서 multi-second drain burst는 없었다. 이는 result retention이 bounded라는 증거가 아니다.
- **필요 수정:** waiting/in-flight/completed-undrained를 포함한 admission 또는 bounded result/backpressure와 failure callback 보존 정책을 정해야 한다. queue 이름·capacity·metrics 보고서도 실제 구현과 맞춰야 한다.

Snapshot slot은 하나이고, PeriodicMetrics는 **100개**에서 trim됐다. GUI event history도 source상 100개이다. A의 `_pendingCommandQueue=64`, `_commandResultQueue=64`, history=30 주장은 frozen source와 맞지 않는다. 결과 queue의 소스상 이름은 `_cmdResultQueue`이다.

근거: [1000개 admission 결과](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/queue-stress-batches.json), [queue high-water](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/queue-high-water.json), [최종 queue 관찰값](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/native-reconnect-after.json), [drain 시간/예산](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/final-metric-summary.json).

### H05-03 — Medium: connect는 전체적으로 off-main/bounded가 아님

`ConnectToWorker`는 main-thread external command processing에서 동기 `TcpClient.Connect`를 실행한다. command thread의 auto-connect도 explicit bounded Connect deadline이 없고 receive/send timeout은 connect 후 설정한다. 정상 loopback에서는 빨리 끝났으나 **모든 connect/read/write가 off-main이고 전체 연결 deadline도 보장됐다**고 인증할 수 없다. 초기 연결·재연결도 asynchronous immutable connection context로 처리하고 connection lifetime/cancellation boundary를 명시해야 한다.

## 6. Dynamic facing / authoritative pose

실제 OS Move 명령으로 다음을 검증했다. 각 경로의 35회 native state sampling과 sequence별 Worker/wire/client 비교를 보존했다.

| 경로 | 실제 Position 구간 | moving native sample | 관찰 rotation |
|---|---|---:|---|
| Go here 메뉴 | (139,142) → (145,141) | 7 | East |
| 서쪽 | (145,141) → (125,141) | 21 | West; 장애물 우회 경로 포함 |
| 북쪽 | (125,141) → (125,156) | 14 | North |
| 남쪽 | (125,156) → (125,134) | 21 | South 15 / West 4 / East 2: 경로 전환 |
| 동쪽 | (125,134) → (155,134) | 30 | East |

sequence 기준으로 client observation을 wire/Worker pose trace에 연결한 **Goto 샘플 93개에서 rotation mismatch 0**이었다. 표본마다 Worker Position, nextCell, native rotation, stance/focus, wire Rotation/PoseSource, client rotation/DrawPos를 기록했다. 실제 중간 렌더링에서도 진행 방향에 맞는 자세를 확인했다. client position delta로 회전을 추정하는 수정은 하지 않았다.

**중요한 보고서 오류:** A 보고서 §5.2의 `DetermineAuthoritativeFacing()` / movement-first 코드는 이 동결 소스에 없다. 실제 `BuildReplicationSnapshot:764`는 **Stance_Busy + valid focus를 먼저 처리하고**, 그 다음 movement를 처리한다. 설치된 1.6 엔진 IL의 `Pawn_RotationTracker.UpdateRotation`도 busy focus를 movement보다 앞서 처리한다. `Pawn_PathFollower.PatherTick`의 FullBodyBusy return은 moving flag 자체를 반드시 false로 만들지는 않는다.

불확실한 priority를 enum codec만으로 판정하지 않기 위해 작은 실제 엔진 시험을 추가했다. QA script가 Worker의 기존 ATTACK command로 **실제 AttackMelee job**을 실행했으며, fake Stance를 주입하지 않았다. **31개 실제 Busy/focus DTO**, 그중 **6개 moving=true + valid focus native sample**을 관찰했다. 이 경우 wire가 Aiming/focus 방향을 우선했다. 따라서 해당 priority concern은 이 candidate에서 재현되지 않으며, movement-first로 바꾸는 것을 권고하지 않는다. 이 시험은 ranged aim/burst graph 전체나 GUI Attack E2 인증이 아니다.

StationaryDrafted/StationaryIdle은 이동이 끝난 뒤의 정상 Worker 자세와 구분했다. codec는 North=0, East=1, South=2, West=3의 별도 round-trip을 통과했다. semantic movement-facing과 단순 codec 통과를 구별한다.

근거: [sequence별 pose 비교](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/matched-movement-pose.json), [경로 native sampling](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/movement-summary.json), [남쪽 방향 전환](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/south-pose-table.json), [실제 moving+focus 표본](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/moving-focus-examples.json), [엔진 IL](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/engine-pose-il.txt), [실제 Worker pose 구현](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/Reviewed/Worker/RemoteWorkerController.cs:764).

화면 근거: [서쪽 중간 frame](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/west-turn-mid-1.jpg), [북쪽 frame](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/north-mid-1.jpg), [남쪽 중간 frame](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/south-mid-2.jpg), [동쪽 중간 frame](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/east-mid-2.jpg).

## 7. Focused regression, snapshot scope, progression

- stale sequence, wrong TacticalSessionId, WorkerGeneration, TargetMapId 및 unresolved map의 직접 snapshot validation 시험은 모두 거절됐다. 이 결과는 **transport epoch race 통과와 별개**이다. 별도 command Generation=0 입력은 parser에서 1로 정규화되어 ACCEPTED였으므로, 그 입력을 stale-command rejection 증거로 세지 않았다.
- wrong viewed Map_1에서 정상 Map_0 snapshot을 받더라도 Map_1으로 잘못 적용되지 않았다.
- gameplay port에 LOAD_SAVE / SET_GENERATION / SET_PROGRESSION / SET_ROTATION / SIMULATE_DELAY를 보내면 5/5 PRIVILEGE_REJECTED였다. static Player_A/B token과 privileged capability는 **PoC test fixture**이며 Production authentication으로 인증하지 않는다.
- final observation에서 두 map 모두 duplicate Thing ID 0; Human302/305의 ThingGrid reference는 각 1개였다. 실제 도착 후 선택/정보창과 rendering은 정상이다.
- client ordinary autonomous tick은 0이었다. Worker의 progression과 반복 periodic replication이 위치를 바꿨다. narrow Pawn snapshot은 jobs/reservations/projectiles/items/buildings/fire/zones/power 등의 full-map graph를 해결하지 않는다.
- Worker Update slice 3120개에서 observed tick 수 합 3133, 최대 4 ticks/slice였다. 전체 Update elapsed 최대 169.1622ms, 8ms 초과 16개였다. 이 값은 command processing과 관찰 overhead를 포함한다. source의 8ms 검사는 **DoSingleTick 종료 후** 수행되므로 hard preemption deadline이 아니다. 실시간 8ms 절대 상한 통과로 보고하지 않는다.
- target map 존재를 확인한 뒤 호출하는 `TickManager.DoSingleTick()`는 global engine progression이다. 이번 시험은 complete ADR-006A World/Local/Tactical temporal implementation을 인증하지 않는다.

health severity/body part/instance graph, general job reconciliation에 대한 기존 QA-PRESENT-004 overall 결함을 닫지 않는다. 해당 광범위 기능은 이번 수정의 비목표이며 재검증 통과 근거도 없다.

## 8. Listener / dependency profile

| 실제 endpoint | 구현 owner | 결과 |
|---|---|---|
| 7792 | RemoteWorkerController gameplay | 정상 |
| 7794 | RemoteWorkerController privileged control | 정상 |
| **7793** | **RemoteClientController control** | 정상; WorkerBridge auxiliary가 아님 |
| 29101 / 29102 | WorkerBridge auxiliary, Worker / Client | 정상 |
| 30341 / 30342 | QAEngine02 Probe, Worker / Client | 정상 |
| 31800 / 31801 | QA-only observer, Worker / Client | 별도 관찰 endpoint |

실제 listener PID와 `-flag=value`를 대조했다. fallback/default-port collision 및 candidate-related bind SocketException 0건. A 보고서의 endpoint owner 명칭은 교정해야 한다.

graphical Client의 unresolved class/Def/cross-reference, MissingMethodException, Harmony failure, NullReferenceException 검색 결과는 0건이었다. 의도된 모든 DLC를 포함한 active profile에서 fixture를 로드했다. **headless Worker**에서는 shader unsupported 189회 및 atlas 초기화 NullReferenceException **1918 occurrence**가 각 실행 로그에 있었다. 대표 stack은 `GlobalTextureAtlasManager.TryInsertStatic / ThingDef.PostLoad`이다. 이를 candidate bind 오류로 합산하거나 1918개 독립 결함으로 해석하지 않는다. 그렇다고 canonical semantic load가 완전히 clean하다고 인증하지도 않는다. 기존 **QA-ENGINE-002 class**와 연결하고 별도 blocker를 자동으로 닫지 않는다.

근거: [runtime listeners](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/runtime-listeners.txt), [로그 분류](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/runtime-log-audit.json), [Worker 로그](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/Phase1/Worker/Player.log), [graphical Client 로그](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/Phase1/GraphicalClient/Player.log).

## 9. A evidence manifest 및 측정 규율

`screen_05_destination_reached.png`와 `screen_06_foreign_pawn_rejected.png`는 실제로 **byte-identical**이다. 각 3,034,093 bytes, SHA256 `95414209DAF0BBCEEAB042ACF08E2C19D739B651D5AE30D491E334DD99056385`. 해시 표가 잘못된 것이 아니라 두 실제 파일의 내용이 같다. 독립적인 도착/foreign GUI proof 두 건으로 사용하지 않았다. accidental file copy였다는 원인까지 단정하지 않는다. frozen harness의 DEMO_11은 foreign 선택/네이티브 클릭이 아니라 **직접 SendCommand**이며 source에는 SCRIPTED_TEST_EVIDENCE로 표기돼 있다. foreign state와 선택 화면이 변하지 않는 scripted 시험에서 같은 화면이 저장될 수 있다. A 보고서의 REAL_GRAPHICAL_OBSERVATION 표기는 부정확하다.

A의 screenshot 8개는 모두 **1920×1080**이다. 보고서의 1280×720은 실행 argument이며 실제 capture 해상도가 아니다.

| 독립 측정 | 결과 / 정확한 범위 |
|---|---|
| Phase1 periodic full Pawn-set JSON | 4231개, 51 Pawn; 22,569–22,691 UTF-8 bytes, median **22,630** |
| 실제 interactive Draft reply | 수신·파싱 성공 4개, 모두 51 Pawn snapshot 포함; 22,630–22,637 bytes |
| 실제 interactive Move reply | 5개, 모두 51 Pawn; 22,628–22,677 bytes |
| 실제 foreign rejection reply | 22,733 bytes, 51 Pawn snapshot 포함 |
| 최종 periodic retained sample | payload 22,724 bytes; cadence median 166.626ms |
| 최종 periodic loopback wire RTT | median 14.786ms, 10.824–19.550ms |
| final reconcile execution | median 2.268ms — **receive-to-apply 전체가 아님** |
| Phase1 observer parse→apply enter | median 8.8235ms; 의도된 apply 지연까지 포함한 전체 max 902.0528ms |

cadence max 74,995.61ms는 시험 중 subscription을 의도적으로 중단했다 재개한 구간을 포함한다. 정상 steady cadence max로 보고하지 않는다. A의 280-byte “interactive metadata only”를 실제 graphical Draft/Move payload로 인정하지 않는다. 이 candidate는 정상 interactive reply에도 full snapshot을 넣는다. 이전 ~14.9KB보다 pose/focus fields 등이 증가한 full-set JSON이며, 단일 Pawn delta나 ~336B replication이 아니다. WAN latency/최종 NFR SLO는 인증하지 않았다.

근거: [A screenshot 파일 감사](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/A-screens-audit.json), [독립 wire payload 집계](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/independent-metrics.json), [최종 timing sample](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/final-metric-summary.json).

## 10. Defect별 Master 권고

| Defect | 권고 | 근거 |
|---|---|---|
| QA-PRESENT-004 overall | **STILL FAILING** | 이번 narrow position/DrawPos/hit target은 통과. general health/job graph 미해결 |
| QA-PRESENT-007 | **PARTIAL** | 실제 GUI async/liveness 개선 확인. H05-01 epoch 오염, H05-02 무상한 result queue, H05-03 sync connect 잔존 |
| QA-PRESENT-008 | **STILL FAILING** | duplicated screenshot / GUI evidence 분류 / 해상도 / timeout·queue·retention·pose code·payload·timing 명칭이 실제와 불일치 |
| QA-PRESENT-009 | **CONFIRMED RESOLVED** — narrow listener/profile subdefect | 정상 flags 소비·포트 분리·bind 오류 없음. canonical clean-load/QA-ENGINE-002 전체 종료는 아님 |
| QA-PRESENT-011 | **CONFIRMED RESOLVED** — tested movement/focus slice | 실제 네 방향·전환, 93 matched samples, 실제 moving+focus 우선순위 확인; 일반 ranged/animation pose graph 인증 아님 |

QA-PRESENT-001/002/003/005/006/010은 종전 narrow CLOSED 범위를 유지하는 것을 권고한다. 003의 session/gen/map/sequence fence와 005의 codec는 transport epoch나 general pose graph 인증이 아니다. 새 transport race를 이유로 기존의 정상 metadata fence 자체가 실패했다고 기록하지 않는다.

## 11. Architecture conclusion / 다음 acceptance 조건

1. **실제 OS/user async Draft/Move E2는 입증됐다.** A의 scripted method-call 증거와 분리해 독립 native 입력으로 검증했다.
2. **검증한 loopback interactive fault window에서는 liveness가 개선됐다.** 전체 reconnect/connect deadline, WAN, 모든 command-control surface의 responsiveness 인증은 아니다.
3. **epoch와 결과 queue는 아직 correctness/boundedness를 만족하지 않는다.** H05-01/02/03 수정 후 새 후보를 freeze하고 해당 실패 조건을 집중 재검증해야 한다.
4. **이동 중 dynamic facing은 검증한 semantic slice에서 해결됐다.** 실제 source의 focus-first 정책을 유지해야 하며, 보고서의 movement-first pseudo-code는 교정해야 한다.
5. **listener startup은 clean**, graphical Client는 dependency/reference 오류가 없었다. headless canonical semantic-load는 별도 ENGINE gate이다.
6. 따라서 좁은 P2 정상 경로가 동작하더라도 이번 전체 narrow gate의 최종 승인은 권고하지 않는다.
7. **Candidate C는 PROVISIONAL 유지**를 권고한다. ADR-002 최종 acceptance 전에는 잔여 presentation transport/queue 결함, 정확한 evidence manifest, ENGINE semantic/recovery blocker를 해결해야 한다. ADR-003/007/008 등의 accepted 설계는 그 runtime implementation이 검증됐다는 뜻이 아니다. inventory/provenance, outcome publication, repair, tactical admission/lifecycle 및 temporal authority의 기존 별도 gate도 유지한다. Production remote tactical 구현/배포를 이번 리뷰로 승인하지 않는다.

## 12. 종료 및 보존

QA가 시작한 Worker/Client 프로세스의 경로·PID·시작 시각을 확인한 후 종료했다. QA 프록시도 종료했고 observer junction만 제거했다. Production, frozen candidate, A runner/profile/evidence source는 변경하지 않았다. 7777 서버는 이번 테스트의 제어 대상이 아니었다.

근거: [QA cleanup 기록](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/cleanup.json), [Production 전후 무결성](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-HARDEN05-20261002/final-audit-summary.json).

**P2 presentation의 실제 async interaction slice는 입증됐지만, 안전한 transport lifecycle까지 입증된 것은 아니다. Candidate C의 PROVISIONAL 유지와 잔여 결함 수정 후 집중 재검증을 Master에게 권고하며, 이 보고서 제출 후 다음 지시를 기다린다.**
