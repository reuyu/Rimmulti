# QA Remote Tactical Presentation — Independent Review

## [QA REVIEW]

| 항목 | 판정 / 범위 |
|---|---|
| Work Package | WP-QA-REMOTE-TACTICAL-PRESENTATION-01 |
| Reviewer | Independent QA / Architecture Reviewer |
| 검증일 | 2026-10-02, 사용자 조작 + 독립 터미널 테스트 |
| 대상 | `POC_Remote_Tactical_Presentation_01.md`가 지정한 frozen Candidate P2 |
| **Final classification** | **PARTIAL / INSUFFICIENT GRAPHICAL EVIDENCE** |
| 필수 실제 GUI → remote intent gate | **NOT PASSED: 실제 징집 / 우클릭 이동이 Worker로 전송되지 않음** |
| Candidate C 권고 | **PROVISIONALLY ACCEPTED 유지. ACCEPTED 승격 근거 없음.** |
| Production 변경 | 없음. candidate 수정·재빌드·커밋 없음 |

분류의 `PARTIAL`은 실제 그래픽 실행 자체가 없었다는 뜻이 아니다. **실제 맵 렌더링·사용자 선택·정보창·기즈모 클릭·우클릭 작업 생성·선택 중 위치 보정은 확인했다.** 그러나 필수인 **real GUI input → remote intent → Worker execution → client reconciliation**의 연결은 실패했다. 테스트 러너가 직접 `SendCommand`를 호출하는 성공과 실제 사용자의 명령 성공을 구분해야 한다.

좁은 결론: native RimWorld Map을 비권위적인 화면으로 재사용하고, 명시적으로 호출한 Worker 명령 결과의 Pawn 위치·징집 상태를 반영하는 기반은 확인됐다. 이 revision이 실제 원격 전술 플레이를 제공한다는 주장이나 full-map replication 가능성까지 입증한 것은 아니다. 구현 누락이 P2 구조 자체의 불가능성을 증명하지도 않는다.

## 1. Requirement / decision traceability

Canonical ID는 최상위 `요구사항_명세서.md`에서만 가져왔다. 아래는 이 PoC의 증거 범위이며 전체 요구사항 인증이 아니다.

| Requirement | 검토 범위 / 결과 |
|---|---|
| SRS-FR-098 | Owner의 기존 Map 진입: 같은 fixture를 각 process에 로드한 mirror 기반만 확인. 실제 admission / canonical artifact provenance는 미검증. |
| SRS-FR-099 | 자기 Pawn만 조작: scripted Worker boundary에서 own 허용 / foreign 및 AI 거부 확인. 실제 GUI는 Worker를 거치지 않으며 foreign mirror Pawn도 로컬 징집 가능. end-to-end 충족 아님. |
| SRS-FR-100 | Vanilla와 유사한 일반 Map interaction: 화면 재사용은 확인. 실제 이동 전달 실패, item interaction / trade / reservations 등 구현·검증 미완료. |
| SRS-BR-009 | 방문·전투 공통 Tactical 논리: 이번 fixture command test만으로 session integration 충족 판정 불가. |
| SRS-NFR-004 | 상태 일관성: 위치·징집의 수동 보정 범위 확인. 오래된 snapshot 수용과 job / health 등의 미보정으로 전체 일관성 보장 없음. |
| SRS-NFR-007 | 중앙 상태 권한: client local ticks가 Worker snapshot을 바꾸지 않음은 확인. Dedicated Server domain / canonical commit은 이 PoC topology에 없으므로 충족 인증 아님. |
| SRS-NFR-008 | Client 장애 격리: 별도 process 분리는 확인. crash / disconnect / reconnect recovery 및 Server 전체 장애 격리 시험은 이번 범위 밖. |
| SRS-NFR-009 / 010 | 화면·선택·정보창·Draft gizmo·right-click의 native UI 사용 확인. local 성공처럼 표시되는 원격 실패 상태는 사용성 결함. |
| SRS-NFR-011 | 실제 원격 조작은 실패. scripted loopback 측정만 존재하며 최종 latency SLO는 인증하지 않음. |

Master MDR-011, MD-021은 A 보고서를 developer evidence로 인정하고 P2를 primary presentation candidate로 지정했으나 실제 graphics 경로의 독립 QA와 권한 분리를 요구한다. 본 보고서는 그 후속 검증 자료이며 Master의 gate / ADR status를 직접 변경하지 않는다. ADR-003/007/008 및 기존 QA-ENGINE blockers는 별개로 남는다.

## 2. Evidence policy / changes made

증거 디렉터리: [REMOTE-PRESENTATION-20261002](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002).

- `Reviewed/Source/`는 frozen source의 검토용 복사본이다. source line 표기는 이 복사본 기준이며 원본과 SHA-256이 일치한다.
- QA 전용 observer는 실제 candidate `SendCommand`, native `Command_Toggle.ProcessInput`, Draft setter, `TryTakeOrderedJob`, draw / tick 호출을 기록했다. GUI 명령을 RPC로 바꾸는 interceptor는 추가하지 않았다.
- QA `RPC` 명령은 기존 candidate 메서드를 직접 호출하는 **단위 경로**다. 실제 GUI 경로로 인정하지 않는다.
- `RECONCILE`은 기존 reconciler에 snapshot을 전달하는 **실험 / fault injection 경로**다. GUI input 또는 자동 network replication의 증명이 아니다.
- 사용자 요청 이후 Computer Use / 화면 자동 조작 / 키보드·마우스 입력 자동화는 사용하지 않았다. 실제 화면 조작은 사용자가 수행했다.
- screenshot / video는 수집하지 않았다. 실제 graphical lifecycle 근거는 사용자 관찰, 정상 graphics 실행 인자, native draw / GUI event / state logs의 결합이다. 프레임율 측정은 아니다.
- A의 `RUN_POC_SUITE`는 frozen 결과 파일을 덮어쓰는 경로이므로 실행하지 않았다. 별도 독립 스크립트를 사용했다.

## 3. Artifact identity and process topology

### 3.1 Identity

독립 검증 전·후 **13 / 13 frozen identity 일치**, **76 / 76 Production 및 protected file 해시 일치**. 차이 0건. [integrity-after.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/integrity-after.json)에 경로·before·after가 있다.

| A가 지정한 artifact | SHA-256 |
|---|---|
| RemotePresentation.csproj | `96724F2E571338E7539E3128C28CED31F03F1211C085D2CB796FE0A556C60093` |
| Common/Protocols.cs | `DDD5E28FF8BF72763DFB33C7DBDA0EDD21FD34A87EA7EF8505CF98526BFF1785` |
| Common/OwnershipRegistry.cs | `6AF86F366164FFFFA67BA0D341580091BAA4DD1D5AE2FB6B4ECB07A4BFF513DD` |
| Worker/RemoteWorkerController.cs | `59EBB85A740ED9AD920EDF9680C8BD0DCB77CBE680DEB01C6A2D797063248B21` |
| Client/RemoteClientController.cs | `CA0EBF4A998038DA34F5B2CCDC7FDD308ABE65752A9062062FA603129A0DA09F` |
| Client/RemoteClientTestHarness.cs | `5F42DDFAB0A28D8F81DBED89F227285C3EF9ED4CE3CE72DF1F39B5C4FB55804B` |
| RemotePresentationMod.cs | `8C97AB5F88669852D33A07785FD307C8863EC9CE0879C4D5761BB1D92872EEE8` |
| deployed WarEconomy.RemotePresentation.PoC.dll | `B4376972DFABE26C27C629DD25C63C059FA9FB3FAD2A40E4AC0145A4685873F4` |
| run_remote_presentation_poc.py | `F2C51F54D60F745CD2D704885B8A2A2D7C66688154FEC7E39FF4FAEE127C4472` |
| remote_presentation_poc_results.json | `E353A0B30066F1241D8D3F23A42B82EAFD2A1D86ABCE9F99DBB09C9AE57A841D` |

나머지 3개는 기존 Worker source / DLL reference와 실제 fixture의 identity이다. fixture SHA-256은 `ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED`. 실제 로드된 remote DLL의 MVID는 `f10f6df9-e753-48a9-9146-df9034edf8cb`; 두 process의 `qa-module.txt`가 native load 경로와 DLL hash를 기록한다.

### 3.2 Topology

| 실행 | Worker | Presentation client | 인정 범위 |
|---|---|---|---|
| A | PID 26728, `-batchmode -nographics`, port 7792 | PID 33100, `-batchmode -nographics`, control 7793 | 개발자 headless evidence |
| 독립 core 단위 검증 | PID 22040, batch / nographics, 29800 | PID 16120, graphics 인자, 29801 | script RPC / native state 증거. 사용자 visible window 증거로 사용하지 않음. |
| 재실행 ManualSession2 | PID 20172 | PID 4904 | 창 노출이 사용자에게 확인되지 않아 graphical usability 합격 근거에서 제외. |
| **실제 사용자 수동 검증 ManualSession3** | **PID 31360, batch / nographics, 29800** | **PID 10328, 정상 graphics mode, 29801** | **사용자가 창·맵·UI를 확인하고 직접 클릭.** |

ManualSession3은 사용자 실행용 launcher에서 `Start-Process`로 시작됐다. client에는 `-batchmode` / `-nographics`가 없으며 Direct3D11, 1280×900을 native 상태로 확인했다. QA 관찰 포트 31700/31701은 loopback이다. [launch-pair.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/launch-pair.json)은 실제 인자·PID·실행 시각을 보존한다.

Dedicated Domain Server는 이 PoC의 command loop에 포함되지 않는다. 이 두 process만으로 Server-issued authentication, domain commit, canonical inventory를 인증할 수 없다.

## 4. Independent core / authorization checks

증거: [core-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/core-results.json), `core_checks.py`, `ObserverMod/Source/Observer.cs`.

| 시험 | 독립 관찰 | 결론 / 한계 |
|---|---|---|
| own Pawn Draft | Player_A token → Human302 → `ACCEPTED`; Worker Draft=true, Wait_Combat | scripted authorization → native execution → snapshot → reconciliation 확인 |
| own Pawn Move | target (140,150), 120 native ticks; `ACCEPTED`; Worker (139,142) → (138,148), Goto; client 위치 일치 | 목적지 완주 시험은 아님. native path 진행과 반영은 확인. |
| foreign participant Pawn | Human305 → `AUTH_REJECTED` | fixture registry 소유권 거부 확인 |
| hostile AI Pawn | Mech_CentipedeBlaster3265 → `AUTH_REJECTED` | fixture registry 거부 확인 |
| stale generation | generation 2로 전환 후 generation 1 Draft → `STALE_GENERATION_REJECTED` | command boundary 확인 |
| current generation | generation 2 Draft → `ACCEPTED` | command boundary 확인 |
| client local ticks | client에 DoSingleTick 10회 직접 주입; Worker G=1943 유지, 전체 Pawn snapshot 전후 동일 | 이 주입이 Worker state를 바꾸지 않음 확인. 완전한 client mutation 격리 인증은 아님. |
| position divergence | client snapshot 위치 (99,99) 주입 후 fresh Worker snapshot 적용 | 위치 복원; ThingGrid reference 1, spawned ID 중복 0 |
| retained old snapshot | gen 2 결과에서 Draft=false인 뒤 gen 1 snapshot을 기존 reconciler에 전달 → Draft=true로 되돌아감 | **응답 / snapshot fencing 누락 재현.** 실제 wire reorder 시험과 구분. |

`OwnershipRegistry.cs:8`의 Player_A/B token과 `:14`의 Pawn mapping은 hard-coded fixture다. production identity / authenticated membership / server-issued tactical capability를 증명하지 않는다.

## 5. Actual graphical-client lifecycle — user-operated

증거: [user-final-observations.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/user-final-observations.json), `GraphicalClient/qa-events.tsv`, `selected-other-strange-client.json`, `after-user-rightclick-move-client.json`, 대응 `*-worker.json`.

| 실기 항목 | 결과 |
|---|---|
| 실제 맵 렌더링 | 사용자 정상 확인 + MapDrawer / DynamicDrawManager 반복 호출 |
| 카메라 pan / zoom | 사용자 체크리스트 정상 확인. 정밀 smoothness / FPS 측정은 하지 않음. |
| Pawn 선택 / inspect pane | 사용자 정상 확인 + Human302 selected=true |
| Draft gizmo 표시 / 실제 클릭 | 사용자 정상 확인 + native `ProcessInput`, GUI event 기록 |
| 실제 right-click 이동 입력 | 사용자 명령 표시 확인 + native `TryTakeOrderedJob`, `GUI=mouseDown`, Job=Goto |
| **실제 입력 → remote intent** | **FAIL. SendCommand RPC 기록 0건. Worker 상태 불변.** |

### 실제 event / authoritative 대조

UTC `2026-10-02T02:50:54.8163041Z`, Frame 7916:

```text
Role=CLIENT GUI=Used GIZMO_PROCESS Label=Draft
Role=CLIENT GUI=Used DRAFT_SET Pawn=Human302 Value=True
```

이후 같은 Pawn의 Undraft / Draft click도 기록됐다. 우클릭 시험에는 `GUI=mouseDown ORDER_JOB Pawn=Human302 Job=Goto`가 반복 기록됐다. checkpoint에서 client는 **Draft=true, Goto**, Worker는 **Draft=false, GotoWander, (139,142), G=1823**였다. client의 `rpcCalls=0`, `tickCalls=0`이었다. 따라서 보이는 명령 표시를 remote 실행으로 해석할 수 없다.

초기 클릭은 같은 이름 Strange인 다른 map의 **Human100302**였다. 이를 Human302의 Worker 값과 비교해 같은 객체의 불일치라고 판정하지 않았다. 이후 native selected ID를 확인하고 Human302의 실제 GUI event / Worker 상태로 독립 재검증했다. 체크리스트가 동명 Pawn을 구분하지 못한 것은 QA 안내의 모호성이었으며 사용자 조작 결함으로 분류하지 않는다.

Static cross-check: candidate의 gameplay Harmony patch는 `RemotePresentationMod.cs`의 `TickManagerUpdate` 억제뿐이다. Draft / FloatMenu / ordered job을 remote command로 변환하는 UI adapter가 없다. A의 Draft / Move 시험은 `RemoteClientTestHarness.cs:175` 이후 코드에서 **직접 SendCommand 호출**로 진행됐다.

또한 Worker도 자동 TickManagerUpdate가 억제된다. 명시적 `TicksToSimulate` / `STEP_TICKS`가 없으면 native tactical clock이 진행하지 않으며 periodic snapshot push도 없다. 사용자가 본 전체 정지 상태는 frozen candidate의 동작과 일치한다. client만 로컬로 움직이도록 만드는 것을 성공 조건으로 삼아서는 안 된다.

## 6. Selected mirror correction / rendering safety

사용자가 Human302를 선택한 상태에서 기존 candidate reconciler에 일부러 변형한 snapshot을 전달했다. QA는 선택·카메라·GUI 입력을 조작하지 않았다.

1. before: map 0, (139,142), Draft=true, Goto, selected=true.
2. perturb: snapshot의 own Pawn PosX만 +4 → (143,142). 선택 유지.
3. 5초 후 실제 Worker snapshot을 적용 → (139,142), Draft=false. 선택 유지.
4. 이후 native draw 호출 18188 → 18627, OnGUI 관찰 38236 → 39114; ThingGrid reference=1, 중복 spawned ID=0.
5. 사용자 확인: **“선택·정보창·맵 모두 정상, 중복이나 깨짐 없음”.**

Worker의 전후 G / Pawn state는 변하지 않았다. 확인 범위는 기존 Pawn의 위치·징집 correction과 선택 유지다. Thing 생성 / 제거, selected Pawn 사망·despawn, 다른 Map 이동, inventory / reservation / projectile 교체 등에는 이 안전성을 일반화하지 않는다.

중요한 제한: 보정 뒤 client job은 **Clean**, Worker job은 **GotoWander**다. reconciler가 CurJobDef / job graph를 적용하지 않으며 Draft setter 등 native callback은 tick 억제 중에도 local state를 바꿀 수 있다. **tick 억제만으로 presentation 객체가 모든 side effect에서 불변이 되는 것은 아니다.**

증거: `ManualSession3/selected-mirror-{before,perturbed,restored,after}.json`, `selected-mirror-canonical-before.json`, `selected-mirror-worker-after.json`, `manual_mirror_correction.py`.

## 7. Actual snapshot scope

| 상태 | Worker snapshot | Client reconciliation | 판단 |
|---|---|---|---|
| Pawn identity / position | 현재 Map Pawn 51개, fixture ThingID / 좌표 | 같은 ID의 기존 Pawn만 위치 변경 | 위치 부분 확인. stable cross-process identity 계약 아님. |
| Draft | bool 포함 | setter 적용 | 보정 확인. callback의 local job side effect 별도. |
| Rotation | native `Rot4.ToString()`; 실제 wire 값 `"3"`, `"1"` 등 | `"North"` / `"East"` / `"West"`만 처리; 나머지 South | **numeric/string protocol 불일치** |
| Jobs | CurJobDef / 보고 문자열 | 적용 없음 | local inspect / job state 불일치 확인 |
| Health | 요약·비율·Downed·Dead·Hediff def names | 없는 Hediff def를 추가하는 작업만 수행 | 제거 / severity / body part / occurrence ID / Dead / Downed 복원 없음 |
| Reservations / pathing | 없음 | 없음 | stale mirror query가 권위 있는 실행 가능성의 근거가 될 수 없음 |
| projectiles / items / buildings / fire | 없음 | 없음 | full-map replication 인증 불가 |
| zones / power / bills / containers / other components | 없음 | 없음 | full-map interaction 가능성 추정 금지 |
| map/session binding / sequence | snapshot generation / tick만 존재 | generation / monotonic check 없음; Find.CurrentMap 사용 | wrong-map apply / stale response 위험 |

출처: `Protocols.cs:35`, `:58`; `RemoteWorkerController.cs:424` 이후 snapshot builder; `RemoteClientController.cs:224` 이후 reconciler. client map에 없는 Pawn은 skip하며 create / delete / lifecycle reconciliation을 하지 않는다.

## 8. Peaceful visit boundary — native engine static inspection

실제 설치된 RimWorld engine `Assembly-CSharp.dll`의 IL을 metadata reader로 독립 조사했다. **실제 거래를 수행했다고 주장하지 않는다.** 재현 가능한 reader는 `EngineIL/Program.cs`, 출력은 [native-ui-il.txt](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/native-ui-il.txt)다.

### 8.1 FloatMenu / right-click

RimWorld 1.6의 경로:

```text
FloatMenuMakerMap.GetOptions / GetProviderOptions
→ FloatMenuOptionProvider_DraftedMove.GetSingleOption / PawnCanGoto
→ PawnGotoAction
→ Pawn_JobTracker.TryTakeOrderedJob
```

`GetOptions`는 `Find.CurrentMap`, bounds, selected Pawn을 읽으며 native provider가 reachability를 판단한다. `PawnCanGoto`는 `ReachabilityUtility.CanReach`, `PawnGotoAction`은 `TryTakeOrderedJob`를 호출한다. 실제 사용자 우클릭에서 local ordered job 생성까지 확인했다.

- **Presentation-only:** 메뉴 표시·선택·대상 미리보기·예상 이동 표시. stale snapshot 기반 메뉴는 잠정 정보다.
- **Worker simulation fact:** 현재 Map 상태에 따른 reachability / reservation 검증, native job 실행·pathing·대상 상호작용·실제 item 이동 / damage / detention의 물리적 결과.
- **Server domain effect:** entry / role permission, participant-controlled Pawn 범위, 의도한 공격의 attribution, Betrayer / 정치 상태 / canonical ownership 변경. UI가 허용 옵션을 보였다는 사실은 authorization proof가 아니다.

거래 접근 메뉴도 `FloatMenuOptionProvider_Trade`에서 `JobDefOf.TradeWithPawn`과 `TryTakeOrderedJob`를 사용한다. 따라서 “trade UI이므로 전부 Server에서만 실행”이라고 단순 분류해서는 안 된다. Worker의 접근·도달·physical trader interaction과 Server의 최종 경제 효과를 분리해야 한다.

### 8.2 Dialog_Trade / equivalent transaction

독립 IL chain:

```text
Dialog_Trade.DoWindowContents acceptance callback
→ TradeDeal.TryExecute
→ Tradeable.ResolveTrade
→ ITrader.GiveSoldThingToPlayer / GiveSoldThingToTrader
→ Pawn_TraderTracker implementation: SplitOff / stock / container mutations
```

- **Presentation-only:** 수량 입력·정렬·가격 / mass preview·아직 확정하지 않은 offer / gift 선택.
- **Worker simulation fact:** trader·negotiator의 존재·도달·살아 있음, 실제 Thing / stack / container 및 위치 변화. native barter의 이러한 물리적 결과를 Worker가 산출할 수 있다.
- **Server domain/economic commit:** canonical custody / inventory revision / settlement writer lease, 가격·잔액·취득 및 소유권 확정, relation / faction effects와 감사 기록. physical effect와 동일 operation의 결과로 연결돼야 한다.

현재 candidate는 trade acceptance를 remote intent로 변환하거나 Server final commit과 연결하지 않는다. vanilla `TryExecute`를 presentation Map에서 확정 실행하면 mirror를 실제 거래의 근거로 오인할 수 있다. ADR-003/004의 canonicalization / publication / failure 계약으로 연결할 필요가 있으나 **generic two-phase commit이나 구체적 distributed commit 구현을 이 보고서에서 선결정하지 않는다.**

A TEST_15는 classification dictionary를 만들고 성공을 반환한다. 실제 trade / economic authority / durable publication 시험이 아니다.

## 9. Performance evidence discipline

| 근거 | 인정 가능한 해석 |
|---|---|
| A TEST_14 | 10번 `PING` 응답 측정. PING은 Pawn snapshot을 채우지 않는다. 평균 230은 full/delta map snapshot의 크기가 아니다. |
| A SnapshotSizeBytes | `respJson.Length` 사용: UTF-8 byte count가 아니라 문자열 길이. |
| A ExecutionToClientVisibleUpdateMs | 응답 수신 timestamp가 reconciliation보다 먼저 기록된다. 실제 visible rendered frame latency가 아니다. |
| 독립 QA GET_SNAPSHOT 10회 | loopback, native Pawn 51개 응답 **14,968 UTF-8 bytes / 회**; external QA → main-thread command → Worker → reconcile → 응답 경로 |
| 독립 roundtrip | 최소 **18.20 ms**, 평균 **25.48 ms**, 중앙값 **26.97 ms**, 최대 **30.10 ms** |

독립 수치에도 QA socket / main-thread scheduling overhead가 포함된다. GUI-to-visible latency, Worker-only latency, WAN latency가 아니다. 10개 표본은 percentile SLO나 부하 안정성 근거로 부족하다.

동일 full response를 10Hz / 20Hz로 보낸다고 단순 계산하면 각각 149,680 / 299,360 byte/s 수준이지만, 이는 측정된 streaming bandwidth가 아니며 TCP overhead와 다른 Map state가 빠져 있다. frozen 구현에는 이러한 periodic replication이 없다. A의 WAN 45–65ms, smooth 60+FPS 주장은 이번 검증에서도 인증하지 않는다.

## 10. Findings / required fixes

아래 `QA-PRESENT-*`는 이번 보고서의 local finding ID다. 기존 QA-ENGINE ledger의 상태를 변경하거나 닫지 않는다.

### QA-PRESENT-001 — High — Real UI input bypasses remote command path

- Requirement: SRS-FR-099 / 100, SRS-NFR-009 / 011; mandatory work-order graphical intent check.
- Location: `RemotePresentationMod.cs:132` tick patch; `RemoteClientTestHarness.cs:175` 직접 호출 시험; candidate에 GUI adapter 없음. 실제 native 경로는 `Command_Toggle.ProcessInput` 및 `FloatMenuOptionProvider_DraftedMove.PawnGotoAction`.
- Reproduction: graphical client에서 Human302 선택 → Draft → 바닥 우클릭.
- Expected: 권한 있는 remote intent 전송 → Worker 실행 → authoritative 결과만으로 mirror 확정.
- Actual: local Draft / Goto 생성, RPC 0건, Worker 미징집·GotoWander 유지; 화면의 명령 표시만 존재.
- Required fix: 실제 UI lifecycle의 command boundary를 구현하고 local business effect를 최종 성공으로 보여주지 않도록 처리. GUI action과 command/response를 연계한 독립 재검증 필요. QA가 interceptor를 대신 구현하지 않았음.

### QA-PRESENT-002 — High — No operational simulation / replication cadence

- Requirement: SRS-FR-100, SRS-NFR-011; Candidate C continuous tactical presentation.
- Location: `RemotePresentationMod.cs:132`, `RemoteWorkerController.cs:150`, `:373`, `:394`; client Update `:282`.
- Actual: 양쪽 자동 ticks 차단; Worker progression은 명시적 tick 명령만 수행. client periodic snapshot stream 없음. real GUI loop가 없는 상태에서는 전체가 멈춤.
- Required fix: Master의 temporal contract 내에서 Worker progression budget / cadence와 snapshot delivery contract를 구현. client command가 임의로 simulation time의 권한을 가지도록 확장하지 않음.

### QA-PRESENT-003 — High — Snapshot generation / freshness not fenced

- Requirement: SRS-NFR-004; ADR-001 fencing / Candidate C replication boundary.
- Location: `RemoteClientController.cs:215`, `:224`.
- Reproduction: gen 2 최신 상태의 Draft=false 뒤 gen 1 retained snapshot 적용.
- Actual: 과거 Draft=true로 되돌아감. reconciler에 rejection branch 없음.
- Required fix: session / tactical generation / map binding / ordered snapshot freshness 검증을 실제 response apply 경계에 적용. reconnect / reordered response 시험 필요. command-generation rejection 성공과 별개다.

### QA-PRESENT-004 — High — State scope / native callback divergence

- Requirement: SRS-FR-100, SRS-NFR-004.
- Location: `Protocols.cs:35`, `RemoteClientController.cs:224–279`.
- Actual: client correction 후 Clean vs Worker GotoWander. health reconciliation은 def-name 추가만 수행; 실제 health graph 복원 아님. items / reservations 등은 snapshot 자체에 없음.
- Required fix: 지원 interaction에 필요한 최소 state graph, lifecycle / identity, callback side effect policy와 정확한 apply oracle을 정의. 51-Pawn snapshot을 full-map replication으로 소개하지 않음.

### QA-PRESENT-005 — Medium — Rotation encoding mismatch

- Requirement: SRS-NFR-004 / 009.
- Location: `RemoteWorkerController.cs:455`, `RemoteClientController.cs:256–260`.
- Actual: native numeric rotation `"3"`를 client는 South로 처리. 현재 비교 분기가 숫자 값을 해석하지 않음.
- Required fix: canonical wire representation을 일치시키고 4방향 모두 실제 native 값으로 시험.

### QA-PRESENT-006 — High if promoted — Fixture tokens / privileged debug commands

- Requirement: SRS-FR-099, SRS-NFR-007; ADR-001 authenticated mutation boundary.
- Location: `OwnershipRegistry.cs:8–21`; `RemoteWorkerController.cs:186–204`가 auth / generation check `:210–221`보다 선행.
- Actual: static Player_A/B token. LOAD_SAVE / SET_GENERATION은 일반 auth check를 거치지 않음. 내부 실험 제어면이며 production access boundary가 아니다.
- Required fix: test-only control plane을 배포 면에서 격리하고 Server-issued identity / participant ownership / generation fencing과 연결. static test token을 production authentication의 증거로 삼지 않음.

### QA-PRESENT-007 — High if promoted — Main-thread blocking / unbounded dispatch

- Requirement: SRS-NFR-011; 기존 Worker starvation / liveness 문제와 연동.
- Location: `RemoteClientController.cs:175` synchronous ReadLine; `RemoteWorkerController.cs:150`, `:375–398`.
- Actual: main thread에서 blocking receive, 무제한 queued-command drain / monolithic tick loops. 이 revision은 별도 hardened Worker 구현을 자동 상속하지 않음.
- Required fix: 검증된 Worker hardening 계약과 bounded / cancellable dispatch, timeout / disconnect UI 결과를 연결. 이번 시험은 악의적 장시간 flood를 추가 실행하지 않았으며 정적 위험으로 보고한다.

### QA-PRESENT-008 — Medium — Evidence oracle / metric overstatement

- Location: `RemoteClientTestHarness.cs:306`, `:448`, `:472–488`; `RemoteClientController.cs:208–210`.
- Actual: health count `>=`라 변화 없어도 통과 가능; PING 문자열 길이를 snapshot bandwidth로 소개; trade dictionary 생성은 실제 거래 시험 아님; reconciliation 전 수신 시각을 visible update로 소개.
- Required fix: 실제 GUI correlation, field equality / lifecycle oracle, GET_SNAPSHOT UTF-8 크기, render timestamp, 실제 domain-side effect 기준으로 test / report 수정.

### QA-PRESENT-009 — High — Fixture dependency semantic load errors

- Location: `ManualSession3/GraphicalClient/player.log:57`, `:63`, `:68` 및 Worker load log; A의 fixture / active mod configuration.
- Actual: frozen fixture에 QAEngine02.GameProbe / MapProbe와 WarEconomy_TacticalProofToken 참조가 있으나 A의 active mods에는 그 dependency가 없다. abstract component load exception, missing ThingDef, unresolved / null spawn 로그가 발생한다.
- Required fix: dependency-complete fixture / manifest와 strict semantic load validation을 제공. QA는 숨겨진 dependency를 켜서 candidate를 고치지 않았다. 기존 QA-ENGINE dependency blocker와 연결되지만 자동 closure / 새 원인 판정은 하지 않음.
- Scope: surviving Pawn의 narrow command / rendering 증거는 유효하되 clean full-state load나 safe canonical artifact의 증거는 아니다.

### QA-PRESENT-010 — Medium — Snapshot target bound to currently viewed Map

- Location: `RemoteClientController.cs:226–239`, `Protocols.cs:58`.
- Actual: Find.CurrentMap의 같은 ThingID만 찾으며 snapshot에 MapId binding 없음. 다른 Map을 보면 own Worker Pawn을 찾지 못하고 silent skip 가능. 동명 clone의 실제 존재 / map 전환은 독립 확인.
- Required fix: session-bound target Map / artifact identity로 reconcile target을 결정하고 missing entity / stale map을 명시적으로 처리. first foreign-map click을 같은 entity mismatch로 오인하지 않음.

## 11. A report reconciliation / architecture recommendation

| A claim | Independent assessment |
|---|---|
| 별도 client에서 native map UI 재사용 가능 | **좁은 범위 확인.** 실제 사용자 graphical lifecycle 근거 추가. |
| full end-to-end Client Input loop 확인 | **수정 필요.** scripted method-call loop는 확인, actual GUI loop는 실패. |
| client local ticks가 Worker를 바꾸지 않음 | **재현 확인.** tested 10 ticks 및 전체 Pawn snapshot 범위. |
| foreign / hostile / stale generation 거부 | **fixture command boundary 재현 확인.** production identity / response fencing은 아님. |
| health 포함 authoritative state reconciliation | **범위 축소 필요.** 실제 apply는 일부 Pawn 필드이며 job / health graph 불일치. |
| 230-byte snapshot / 10–20Hz bandwidth | **수정 필요.** PING 크기. 51-Pawn 실제 응답은 14,968 UTF-8 bytes. |
| Peaceful visit dual authority 필요 | **효과 단위 분리는 타당.** UI 이름으로 Worker / Server를 전부 나누거나 generic 2PC를 결정해서는 안 됨. |

권고:

1. **Candidate C는 PROVISIONALLY ACCEPTED 유지.** P2 native rendering의 긍정 증거를 보존하지만 이번 exact frozen revision의 mandatory GUI-to-Worker gate를 통과로 처리하지 않는다.
2. 실제 Draft 또는 right-click 중 최소 한 경로의 GUI adapter와 authoritative reconciliation을 구현한 다음, **그 경로만 같은 방식으로 재검증**한다. QA observer를 기능 구현으로 사용하지 않는다.
3. remote session / Map binding, snapshot ordering, lifecycle / minimum state graph, Worker cadence / client freeze, physical facts ↔ Server commit의 계약을 ADR-002 amendment 및 관련 ADR과 연결한다.
4. canonical Settlement state / entity identity / provenance는 ADR-003, ordinary writer handoff는 ADR-007, shared world / transit는 ADR-008 및 accepted temporal boundary와 연결한다. inventory publication / commit / repair 상세는 ADR-003/004 계약을 따른다.
5. 기존 QA-ENGINE-002/003/004/005/006 등의 liveness·dependency·temporal·publication blockers는 본 presentation 성공 항목으로 닫지 않는다. 최종 state / authority 계약의 승인과 구현 검증은 별도 gate다.
6. 현 시점에 새로운 대형 prototype을 자동 요구하지 않는다. 우선 실제 UI 경로와 보고 oracle의 구현 누락을 고치고, 기존 fixture의 정확한 dependency 상태에서 최소 회귀 시험을 수행한다. full-map replication feasibility는 필요한 interaction scope / state contract가 정해진 뒤 남는 engine uncertainty만 검증한다.

## 12. Completion / evidence custody

- 요청된 실제 화면 수동 항목은 종료: rendering / camera / selection / inspect / gizmo / right-click / selected correction. actual GUI-to-remote intent는 **실패로 완료**했다. 더 클릭해도 구현 누락이 해결되지는 않는다.
- Unit / static 요구 항목은 완료했다. full-map replication, 실제 trade commit, crash / WAN 등 범위 밖 항목은 통과 처리하지 않았다.
- 테스트용 Worker 31360 / graphical client 10328은 executable path와 시작 시각을 launch record와 대조한 뒤 종료. 다른 서버 / 게임 프로세스는 종료하지 않았다.
- 이번 QA가 추가한 `Mods/QA.Remote.Observer` junction만 대상까지 확인하고 제거. observer 원본·DLL·로그는 보존. 기존 Production / frozen PoC links는 유지.
- No Production edits / candidate fixes / commits. hash identity 검증 자료 보존.
- 수동 체크리스트는 시험 지시 자료이며 이 보고서의 최종 판정을 대체하지 않는다.

주요 증거:

- [core-results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/core-results.json)
- [실제 GUI event log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/GraphicalClient/qa-events.tsv)
- [사용자 최종 관찰](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/user-final-observations.json)
- [실제 우클릭 client state](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/after-user-rightclick-move-client.json)
- [대응 Worker state](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/after-user-rightclick-move-worker.json)
- [선택 중 보정 후 native state](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/selected-mirror-after.json)
- [engine UI IL](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/native-ui-il.txt)
- [hash integrity](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/integrity-after.json)
- [process cleanup](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/ManualSession3/cleanup.json)
- [observer junction cleanup](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/junction-cleanup.json)
- [증거 파일 SHA-256 manifest](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/REMOTE-PRESENTATION-20261002/evidence-manifest.json)

Master action requested: 본 독립 증거를 반영해 MD-021의 conditional evidence 범위를 명확히 하고, 실제 GUI command loop 결함 수정·최소 재검증을 지시할 것. Candidate C / 관련 ADR의 최종 승인 여부는 Master가 결정한다.
