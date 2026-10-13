from pathlib import Path
q=Path(r'C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\REMOTE-HARDEN04-20261002');root=q.parents[1]
text=r'''# QA Remote Tactical Presentation Hardening — Independent Review 04

[QA REVIEW]

- Work Package: **WP-QA-REMOTE-PRESENTATION-HARDEN-04**
- Reviewer: GPT-6.1 Sol, Independent QA / Architecture Reviewer
- 검증일: **2026-10-02 KST**. 원시 로그의 시간은 UTC.
- Target: `Remote_Tactical_Presentation_Hardening_03.md`의 동결 후보.
- Verdict: **PARTIAL / REMAINING BLOCKER**
- 제출 성격: Master에게 제공하는 독립 판정 및 결함 상태 **권고**. Master state/ledger는 변경하지 않았다.
- Production 수정/재빌드 및 후보 수정/재빌드: **없음**. 별도 QA 관찰 DLL만 빌드했다.

실제 OS 입력 → 네이티브 Draft/Go here → adapter/RPC → Worker 실행 → 주기적 snapshot → 움직이는 렌더링 및 도착 후 클릭은 재현됐다. 이전의 렌더링 이동 하위 장애는 해소됐다. 그러나 **GUI 명령 응답을 2초 늦추면 메인 스레드가 약 2.03초 멈추고**, A의 프로필 실행 옵션에서도 보조 리스너 충돌이 재현된다. 따라서 전체 작업 지시의 무조건 PASS는 승인할 수 없다.

## 1. 검증 범위와 증거 수준

본 판정은 Master WORK ORDER 항목 1–11에 대한 좁은 P2 Draft/Move presentation 검증이다. 전체 SRS 준수, 전체 맵 복제, Production 인증, temporal authority, inventory canonicalization, durable outcome publication의 완료 판정이 아니다.

- **ACTUAL_OS_GUI:** computer-use의 `sky` 입력으로 실제 그래픽 RimWorld 창의 초상화/스프라이트, Draft gizmo, 지형 우클릭, Go here 메뉴를 클릭했다. 직접 `ProcessInput`, `TryTakeOrderedJob`, `SendCommand` 호출을 GUI 증거로 사용하지 않았다.
- **RUNTIME_OBSERVER:** 별도 Harmony 관찰자는 GUI 진입, RPC, DTO 수신, 메인 apply 전후, Position/DrawPos/job/health, frame gap, grid references를 기록했다. 네트워크 수신 hook는 .NET/DTO 데이터만 읽고 Unity/Verse 객체에 접근하지 않는다.
- **QA_FIXTURE_CONTROL:** Worker 전용 control port로 fixture load, progression pause/resume, rotation을 설정했다. 메뉴에 Go here가 나타나도록 Player_B 토큰으로 Nick을 목적지 근처에 배치한 것은 명시적인 fixture 준비다. Player_A의 실제 Move 증거와 분리했다.
- **FAULT_PROXY:** 실제 후보의 자동 GET_SNAPSHOT 응답을 지연/변형/종료한 loopback proxy. observer/proxy가 후보 대신 polling, tween reset, movement reconciliation을 구현하지 않았다.
- **STATIC_ANALYSIS:** 동결 시 확보한 소스. A는 소스 해시와 재현 가능한 source→DLL 빌드 provenance를 제출하지 않았으므로, QA 도착 시 소스 해시 불변성과 실제 DLL 실행 증거를 구분한다.

증거 요약: [independent-summary.json](%Q%/independent-summary.json). 성공한 fault test 및 원시 관찰은 아래 항목에 연결했다. A의 15개 PASS 자체를 독립 테스트 결과로 합산하지 않았다.

## 2. 후보, fixture, 프로필, 프로세스 정체성

| 대상 | 독립 결과 |
|---|---|
| Candidate DLL SHA-256 | `0F57AFB12BE7D7C8FF1F12C231F8A3CA9815FB76069BEBDBB723604488C582BB` — 지시와 일치 |
| 실제 로드 경로 | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.RemotePresentation.PoC\1.6\Assemblies\WarEconomy.RemotePresentation.PoC.dll` |
| 실제 로드 MVID | `2dbc5682-70ee-48a8-b771-3ee15486f0ad` — Worker/Client 일치 |
| Fixture SHA-256 | `ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED` — 원본 및 두 프로필 복사본 대상 |
| Candidate/소스/관련 입력 도착 freeze | 13개 파일; 종료 전 재검사 일치 |
| Production 보호 범위 | `WarEconomyMod`의 당시 전체 파일 130개, 해시 변경 **0** |
| Worker | PID 23496, `-batchmode -nographics`, 별도 저장/로그 프로필 |
| Graphical client | PID 23352, graphics-capable 정상 실행, **Direct3D11**, batchmode/nographics 없음 |
| QA runtime 화면 | 실제 캡처 **1920×1080**. 요청 실행 옵션 1280×900과 실제 화면 크기를 혼동하지 않음 |
| Transport | Worker gameplay `127.0.0.1:29900`; Worker control `127.0.0.1:29903`; client QA control `29901`; observer `31800/31801`; fault proxy `29902` |

A의 181개 Production 파일 불변 주장은 그와 동일한 경로 목록이 제공되지 않아 그대로 인증하지 않았다. 본 보고서의 130개는 이번 독립 before/after 목록이다.

활성 모드는 A의 11개 항목(Harmony, Core, Royalty/Ideology/Biotech/Anomaly/Odyssey, WorkerBridge, ENGINE02 Probe, WarEconomy, RemotePresentation)에 QA observer만 추가했다. fixture나 dependency 구현은 고치지 않았다. 별도 QA 프로필의 소리/개발자 모드/일시정지 설정과 전용 포트는 시험 설정으로 기록했다. dependency manifest는 검사 당시 파일 정체성이며, A의 서명된 dependency freeze나 모든 dependency의 runtime MVID 증명으로 확대하지 않는다.

근거: [identity-before.json](%Q%/identity-before.json), [integrity-after.json](%Q%/integrity-after.json), [production-before.json](%Q%/production-before.json), [launch-pair.json](%Q%/launch-pair.json), [Client loaded module](%Q%/GraphicalClient/qa-module.txt), [Worker loaded module](%Q%/Worker/qa-module.txt), [dependency-manifest.json](%Q%/dependency-manifest.json), [profile-manifest.json](%Q%/profile-manifest.json).

## 3. 실제 GUI → Worker → rendered mirror

| 실제 입력 | 관찰 결과 |
|---|---|
| Strange 초상화 선택 | `Human302`, Map_0 선택/inspect 확인 |
| Draft gizmo 클릭 | native GUI `Event.current=Used` → adapter `REAL_GUI_GIZMO` → Worker `ACCEPTED` → authoritative Draft=true → mirror=true |
| Nick이 있는 지형 우클릭 | 실제 FloatMenu에 `Try to arrest Nick`, **Go here**, tending 항목 표시 |
| **Go here 실제 클릭** | `REAL_GUI_FLOATMENU`, Worker Move accepted, Worker ordered Goto → 반복적 자동 복제 → mirror Goto/Position/DrawPos → 도착 후 Goto 종료 |
| 추가 빈 지형 우클릭 | vanilla가 메뉴 없이 바로 발행한 Move도 동일 RPC/복제 경로를 통과. 앞선 Go here 메뉴 클릭과 구분 |
| 이동한 Strange 스프라이트 직접 클릭 | 도착 좌표 `(165,0,145)`, DrawPos `(165.50,8.41,145.50)`, 선택 ID **Human302**, inspect 정상 |
| 외국 참여자 Nick 선택 → Undraft gizmo 클릭 | 실제 native GUI → `AUTH_REJECTED`; Client와 Worker의 Human305 상태 XML은 전후 동일 |

UI prefix에서 local Draft/Goto의 최종 상태를 먼저 커밋하지 않았다. 예를 들어 첫 Draft의 RPC_ENTER/authoritative APPLY_ENTER 시 client Draft=false, Worker snapshot Draft=true, APPLY 이후에만 client=true다. 첫 Go here도 local job=None → Worker Goto snapshot → `IsReconciling=true`인 apply에서 mirror job 생성 순서다. 외국 폰은 rejection 이후에도 Draft/job/health/position이 유지됐다. reconciliation 내부 setter/job 호출은 관찰됐지만 재귀 gameplay RPC를 만들지 않았다.

추가 비-GUI 권한 회귀: own Pawn stale generation=999는 `STALE_GENERATION_REJECTED`; hostile AI `Mech_CentipedeBlaster3265`는 `AUTH_REJECTED`. 정상 generation의 own Pawn 수락은 실제 GUI로 검증했다. 이 결과는 static test Player_A/B token registry의 동작이며 Production 인증 증거가 아니다.

근거: [Client event trace](%Q%/GraphicalClient/qa-events.tsv), [Worker event trace](%Q%/Worker/qa-events.tsv), [own-drafted.jpg](%Q%/own-drafted.jpg), [native-move-issued.jpg](%Q%/native-move-issued.jpg), [moved-pawn-native-selected.jpg](%Q%/moved-pawn-native-selected.jpg), [foreign-draft-rejected.jpg](%Q%/foreign-draft-rejected.jpg), [foreign before](%Q%/before-foreign-client.json), [foreign after](%Q%/after-foreign-client.json), [authorization-focused.json](%Q%/authorization-focused.json).

## 4. 중간 위치, 렌더링, hit target 및 보정 안전성

실제 이동 입력을 받은 채로 Worker progression을 pause/resume하여 관찰 시점만 맞췄다. 이후 이동은 후보의 autonomous progression과 자동 replication이 수행했다. 수동 STEP_TICKS, 테스트 harness의 이동 완료 polling, QA의 tween/draw reset은 사용하지 않았다.

세 개의 **서로 다른 중간 렌더링 프레임**에서 Strange 스프라이트가 약 `(677,449)` → `(776,449)` → `(859,414)` 화면 위치로 이동했다. 대응하는 근접 apply 기록은 다음과 같다.

| 프레임 | authoritative snapshot Position (x,z) | Worker wire DrawPos (x,y,z) | apply 후 Client DrawPos | 실제 이미지 |
|---|---|---|---|---|
| 1 | (120,141) | (120.54,8.41,141.50) | 동일 표시 정밀도 | [중간 1](%Q%/verified-mid-render-1.jpg) |
| 2 | (125,141) | (124.97,8.41,141.50) | 동일 표시 정밀도 | [중간 2](%Q%/verified-mid-render-2.jpg) |
| 3 | (128,143) | (128.56,8.41,143.33) | 동일 표시 정밀도 | [중간 3](%Q%/verified-mid-render-3.jpg) |

캡처 완료 시간과 근접 apply 시간은 약 -39.6/-3.1/+27.4ms 차이가 있다. 이미지는 해당 프레임의 시각 증거이며 위 수치를 픽셀 단위의 동시 측정이라고 주장하지 않는다. 별도의 live Worker probe도 client probe보다 뒤에 실행되어 Worker가 더 진행한 값이 나온다. 비교 기준은 **client가 실제 적용한 authoritative snapshot**이다. 적용 후 Position은 5,589개 성공 관찰에서 일치했고 DrawPos는 로그의 소수점 2자리 정밀도에서 일치했다. 후보는 snapshot의 sub-cell DrawPos를 직접 투영한다. 도착 후 native Position/DrawPos가 수렴하고 실제 스프라이트 클릭으로 동일 폰을 선택했다.

안전성 관찰:

- Client `TicksGame=1824`, 관찰 tick counter=1은 load 직후 baseline부터 최종까지 유지: 시험 중 local DoSingleTick 증가 **0**. 초기 load 관찰 tick 1까지 0이라고 주장하지 않는다.
- 두 map의 duplicate spawned ThingID 수는 0. 테스트한 Human302/305의 ThingGrid reference는 각각 **1** 유지.
- 테스트 Pawn의 local `pather.Moving=false`; 도착 후 Goto가 남지 않았다. 선택/inspect/reference가 정상 유지됐다.
- Map_1을 보고 있는 동안 target Map_0의 periodic reconciliation/rotation만 적용되고 Map_1 Pawn 상태는 유지됐다.
- `Position` setter, 조건부 grid registration, `ResetTweenedPosToRoot`, reflected tweenedPos, `StopDead`는 native mirror 객체를 변경한다. 이를 “native 상태를 전혀 변경하지 않는다”로 해석하면 안 된다. 시험에서는 local simulation authority의 진행 없이 projection을 보정했다.
- 일반 body-part health graph와 모든 JobDriver를 복제한 것은 아니다. `CurJobReport`, health/dead/downed 전체 필드를 온전히 반영하지 않는다. Worker idle/Wait_Combat이 mirror None으로 표현되는 차이도 남는다.

기존 전체 reconciliation 결함은 유지한다. 특히 Stab severity를 client에서 **3→4**로 perturb한 뒤 정상 periodic snapshot 여러 회 수신 후에도 **4**였다. 후보의 `HediffDefs`/AddHediff 로직에는 severity/body-part/instance identity/제거 상태의 authoritative 복원이 없다. QA는 측정 후 fixture의 원래 severity만 명시적으로 복구했다. 이는 후보의 복구 성공으로 계산하지 않았다.

근거: [apply-oracle-summary.json](%Q%/apply-oracle-summary.json), [matched-render-snapshots.json](%Q%/matched-render-snapshots.json), [render-correlation.json](%Q%/render-correlation.json), [final-client.json](%Q%/final-client.json), [health-fault-result.json](%Q%/health-fault-result.json), [render correction source](%Q%/Reviewed/RemoteClientController.cs:435).

## 5. Privileged control boundary

**검사 대상 5개 control의 candidate-local 경계는 통과했다.**

- gameplay에서 LOAD_SAVE / SET_GENERATION / SET_PROGRESSION / SET_ROTATION / SIMULATE_DELAY에 각각 11개 변형, 총 **55건** 실행: 성공한 privileged business effect **0**.
- `Source=QA_TEST_CONTROL` + invalid/ordinary/실제 privileged-looking token, stale generation, wrong session, 다른 source 필드, object source, forged `IsControlSurface`, alternate command spelling을 포함했다.
- 정확한 command spelling은 `PRIVILEGE_REJECTED`; alternate spelling도 privileged handler에 도달하지 못했다. 전후 generation/progression/state는 유지됐다.
- 실제 QA control channel에서 invalid/Player_A token은 **10/10 거부**. 올바른 capability + 임의 Source는 허용됐다. 따라서 privilege는 Source 문자열이 아니라 **trusted listener가 설정하는 IsControlSurface + capability**에서 온다.
- 소스에는 gameplay 수신 단계와 main-thread dispatch 단계의 두 gate가 있다. TCP LISTEN과 소스 모두 loopback bind를 확인했다.

Static capability, Player_A/B token, plaintext local transport는 PoC fixture다. Production auth/TLS, 모든 legacy test command의 격리, 실제 사용자 권한 시스템은 인증하지 않았다. 특히 별도의 STEP_TICKS/TicksToSimulate 경로는 아래 worker/liveness 범위 한계를 유지한다.

근거: [privileged-boundary-results.json](%Q%/privileged-boundary-results.json), [listener-topology.txt](%Q%/listener-topology.txt), [gameplay gate](%Q%/Reviewed/RemoteWorkerController.cs:144), [trusted listener origin](%Q%/Reviewed/RemoteWorkerController.cs:267), [capability gate](%Q%/Reviewed/RemoteWorkerController.cs:367).

## 6. 비동기 주기 복제, 지연, 종료, 재접속

### 통과한 주기 복제 경로

- 실제 periodic ParseResponse는 background **thread 60**, Unity apply/native hooks는 **thread 1**에서 실행됐다.
- background loop는 한 번에 GET_SNAPSHOT 한 건만 기다린다. single-slot coalescing queue를 lock으로 전달하고 main Update가 하나를 검증/적용한다.
- periodic receive timeout=3.5초, send timeout=2초. background에서 native map/Pawn 변형 호출은 발견하지 않았다.
- 2초 실제 response 지연 시 periodic RTT 최대 **2,015.09ms**, 측정 구간 최대 main frame gap **19.0ms**. PING 응답은 약 10–26ms로 유지됐다. 별도의 focused proxy run도 PING 2.76–17.20ms였다.
- polling socket close 직후 `ReplicationDegraded=True`, 이후 자동 재연결로 False/복제 재개. fault 구간 관찰 frame gap은 63.4ms였으며 2초 freeze가 아니었다.
- 4.5초 지연(3.5초 deadline 초과)에서 degraded가 표시됐고, old seq **3666**의 늦은 응답은 apply되지 않았다.
- disconnect 도중 보류한 실제 response seq **3678**도 apply되지 않았다. disconnect 직후/늦은 응답 뒤의 lastSequence=3677, applied=3639 유지. reconnect 이후 sequence를 0으로 초기화하지 않고 복제가 재개됐다.

근거: [async-periodic-fault-results.json](%Q%/async-periodic-fault-results.json), [async-proxy-wire.json](%Q%/async-proxy-wire.json), [periodic-fault-native-results.json](%Q%/periodic-fault-native-results.json), [frame-gap trace](%Q%/GraphicalClient/qa-frame-gaps.tsv).

### QA-PRESENT-007 — 남은 High 결함: 실제 GUI RPC는 여전히 main-thread blocking

- Location: [RemoteClientController.cs:219](%Q%/Reviewed/RemoteClientController.cs:219), 특히 **239**의 `_reader.ReadLine()`; [GUI adapter](%Q%/Reviewed/RemoteGuiCommandAdapter.cs:82).
- Reproduction: gameplay proxy에서 다음 실제 native Draft response만 2초 보류 → 사용자가 실제 gizmo 클릭 → GUI callback 안에서 SendCommand가 응답을 기다림.
- Expected: pending UI를 표시하더라도 frame/UI 루프는 계속 실행하고 승인된 response만 main-thread projection에 반영.
- Actual: 해당 GUI/RPC는 thread 1에서 실행, `MaxFrameMs=2029.3ms`. 네트워크 응답 대기가 frame 정지로 연결됐다.
- Root cause: periodic 경로만 비동기화했고 interactive command는 별도 socket의 동기 read/write를 GUI prefix에서 직접 실행한다. 그 socket은 receive/send deadline도 설정하지 않는다. ConnectToWorker 또한 main-thread synchronous connect다.
- Required fix: interactive intent I/O도 bounded background command flow로 이동하고, epoch/generation/context를 갖춘 응답을 main-thread에서 처리. 승인 전 authoritative local Draft/Goto 금지를 유지할 것. 오류/timeout/pending 상태를 명확히 표현하고 command deadline을 둘 것.

또한 PeriodicMetrics는 매 snapshot을 누적하는 무제한 List이며 이번에 5,590개까지 증가했다. BenchmarkResults/EventHistory에도 자동 retention 상한이 없다. Client `_extQueue`, Worker `_commandQueue`는 unbounded이고 Update는 모두 drain한다. single-slot snapshot coalescing만으로 전체 queue/list boundedness가 해결된 것이 아니다. per-frame drain budget, command admission 제한, telemetry retention이 필요하다.

Disconnect는 `_pendingSnapshotToApply`를 비우거나 connection epoch를 변경하지 않는다. 이번 **in-flight socket** 늦은 응답 두 건의 차단은 통과했지만, 이미 coalesced된 old snapshot과 disconnect의 main-frame 순서 race까지 해소됐다고 인증하지 않는다. 신규 후보에서 이 ordering을 검증하고 epoch/fencing과 버퍼 lifecycle을 명확히 해야 한다. 이번 관찰로 기존 QA-PRESENT-003의 정상 sequence/session/gen/map gate를 재개방하지는 않는다.

## 7. Worker progression과 기존 fencing/rotation 회귀

Worker는 target map의 존재 확인 후 global DoSingleTick을 실행한다. frame당 max 5 ticks, 각 tick 뒤 8ms budget 확인, 실제 수행 tick만 accumulator에서 차감한다. 관찰된 24,407개 tick-bearing Update에서 max slice=5, median Update=1.326ms였다. **최대 Update는 49.03ms**: queue 처리 시간을 포함하며, tick 하나를 중간에 선점할 수 없으므로 “모든 Update가 hard 8ms 이하”는 증명하지 않는다. STEP_TICKS와 command의 TicksToSimulate 루프는 별도로 남아 있다.

실제 Move는 추가 수동 stepping 없이 진행했고 SET_PROGRESSION pause/resume에 반응했다. 이것은 좁은 movement liveness 증거다. global ticks가 다른 map/world를 함께 갱신하는 문제, Server World Time/frozen local time의 완전한 ADR-006A 구현을 승인하지 않는다.

실제 자동 periodic transport에서 poison state(99,99/변경된 Draft/rotation)를 동반한 다음 응답을 주입했다.

| Fault | 결과 |
|---|---|
| stale SnapshotSequence | 거부, native Pawn 상태 불변 |
| wrong TacticalSessionId | 거부, native Pawn 상태 불변 |
| wrong WorkerGeneration | 거부, native Pawn 상태 불변 |
| wrong TargetMapId | 거부, native Pawn 상태 불변 |
| unresolved target map | 거부, native Pawn 상태 불변 |

다른 viewed map에서 North/East/South/West를 Worker control → wire → 정상 periodic apply로 전달했다. 각각 native 0/1/2/3 일치, Map_1 Pawn 상태 불변. 직접 Validate 호출만으로 회귀 PASS를 만들지 않았다. poison health/Downed 등 모든 잘못된 snapshot field를 망라한 fuzz test라고 주장하지 않는다.

근거: [worker-slice-summary.json](%Q%/worker-slice-summary.json), [periodic-fault-native-results.json](%Q%/periodic-fault-native-results.json), [periodic-proxy-wire.json](%Q%/periodic-proxy-wire.json), [map-rotation-results.json](%Q%/map-rotation-results.json).

## 8. Fixture / initialization cleanliness — PARTIAL

의존 class/Def/reference가 있는 활성 프로필에서 두 map/51-Pawn target fixture가 로드됐다. 검사한 `Could not resolve / Could not load reference / Could not find class`는 0, proof-token texture/null-material 관련 로그도 0이었다. Graphic_StackCount 변경은 이 candidate-local 증상을 해소했다.

그러나 A runner와 동일한 **split argument** 방식 `-bridgeport 29101/29102`, `-qaport 30341/30342`로 실행해도 actual listener는 Worker의 **29100/30340**이었다. Client에는 WorkerBridge bind 실패와 QAEngine02.Boot의 SocketException이 재현됐다. 선언된 고유 포트가 실제 적용된 것으로 처리할 수 없다. QA는 parser/프로필/의존 DLL을 수정하거나 port binding을 몰래 우회하지 않았다.

- Location: [runner](%Q%/Reviewed/run_remote_presentation_hardening.py:187), WorkerBridge/Probe의 native GenCommandLine.TryGetCommandLineArg 사용 경로, [client log](%Q%/GraphicalClient/Player.log:34).
- Expected: 각 dependency의 실제 listening port가 프로필 manifest와 일치하고 두 프로세스가 충돌 없이 초기화.
- Actual: fallback/default port와 Client init exception.
- Required fix: 엔진의 CLI parsing에 맞는 argument/profile을 제시하고 실제 bind를 검증한 fixture/dependency manifest로 재동결할 것. 이번 대상은 수정하지 않았다.

headless Worker에는 shader/Null graphics/atlas 계열의 기존 초기화 로그가 다수 존재한다. 요약 검색에서 NullReferenceException 1,919행, post-long-event exception 1,918행이 관찰됐다. 이 수치는 검색된 **로그 행 수**이며 서로 독립된 1,919개 결함이라는 뜻이 아니다. 정상 graphical client에는 해당 NullReferenceException이 없었다. 이 headless render/atlas 조건을 serialization의 missing Def/reference failure와 혼동하지 않으며, 이 프로필 전체를 clean canonical load라고 인증하지 않는다. 기존 **QA-ENGINE-002** class와 연결하고 별도 중복 결함 ID를 생성하지 않았다. 글로벌 ENGINE 결함은 닫지 않는다.

근거: [GraphicalClient-log-summary.json](%Q%/GraphicalClient-log-summary.json), [Worker-log-summary.json](%Q%/Worker-log-summary.json), [listener-topology.txt](%Q%/listener-topology.txt), [client log](%Q%/GraphicalClient/Player.log), [Worker log](%Q%/Worker/Player.log).

## 9. Metrics 및 A 증거 규율 대조

| 독립 측정 | 결과 / 한계 |
|---|---|
| 실제 GUI response UTF-8 bytes | Accepted **19,472–19,511 B**; foreign rejection **19,563 B**; 모두 51-Pawn snapshot 포함 |
| periodic response UTF-8 bytes | **19,349–19,531 B**, 5,601개 wire 관찰 |
| snapshot 객체 자체 UTF-8 bytes | periodic **19,151–19,333 B**, full target 51-Pawn set |
| 전송 형식 | full Pawn-set snapshot, 별도 sparse delta/336 B 단일-Pawn packet으로 측정한 것이 아님 |
| 정상 applied cadence median | **166.84ms**, 약 6Hz; 후보 sleep 설정 150ms와 구분 |
| 정상 loopback RTT median | **15.14ms** (100ms 미만 표본의 median); WAN/NFR 최종 SLO 아님 |
| 지연 periodic RTT | 최대 **2,015.09ms** |
| DTO parsing 완료 → main apply entry | median **7.29ms**, 관찰 max **139.61ms**; raw socket first-byte→완료 지표가 아님 |
| apply method 실행 시간 median | **2.08ms** |
| periodic 2초 지연 main frame gap | **19.0ms** |
| 실제 GUI 2초 지연 main frame gap | **2,029.3ms** |

A의 `LoopbackReceiveToApplyMs`는 코드에서 **applyMs**, 즉 apply 메서드 실행 시간으로 저장된다(810행). 이름대로 receive→main-thread apply 지표가 아니다. 이번 observer는 별도의 DTO 수신 시각과 apply entry를 기록했다. observer SNAP/grid 조회 및 DUMP 자체는 main-thread 비용을 가진다. 이를 포함한 모든 구간의 최대 gap을 순수 candidate FPS로 포장하지 않았다. 위 fault frame 값은 해당 fault의 RESET_FRAME_METRICS/STATUS 구간이다.

과거 약 14.9KB의 51-Pawn response나 336B 주장과의 차이는 **버전/필드와 snapshot scope**를 구분해야 한다. 현 후보는 DrawPos 등을 포함한 51-Pawn full set이 약 19KB이며, 이 실측으로 336B full-map/최종 bandwidth를 주장할 수 없다. 압축/델타/WAN 성능은 입증하지 않았다.

A의 DEMO_02/03 SCRIPTED_GUI_CALL 명시는 개선됐다. A의 methods 호출과 viewport focus click을 이번 실제 native GUI input proof와 합치지 않았다. A가 제출한 6개 screenshot 해시는 전부 일치하지만 실제 해상도는 **1920×1080**으로, 보고서의 1280×720 표기는 틀렸다. A의 “native health를 건드리지 않는다”, 전체 QA-004 CLOSED, 모든 liveness CLOSED 해석 역시 위 코드/실측과 맞지 않는다. 따라서 QA-PRESENT-008의 무조건 종료는 권고하지 않는다.

근거: [wire-size-summary.json](%Q%/wire-size-summary.json), [independent-summary.json](%Q%/independent-summary.json), [A-screenshot-audit.json](%Q%/A-screenshot-audit.json), [metric assignment](%Q%/Reviewed/RemoteClientController.cs:810).

## 10. 결함별 Master 권고

| 결함 | 권고 | 범위 / 근거 |
|---|---|---|
| QA-PRESENT-001 | **CONFIRMED RESOLVED** | 실제 native Draft/Go here adapter chain, 승인 전 최종 local mutation 억제, foreign rejection 회귀 통과 |
| QA-PRESENT-002 | **CONFIRMED RESOLVED** | autonomous Worker movement + repeated 정상 periodic replication; client native position/도착 수렴 |
| QA-PRESENT-003 | **CONFIRMED RESOLVED** | 기존 4 fencing gate와 delayed old socket response 회귀 유지. 모든 connection-epoch race 해결 인증은 아님 |
| QA-PRESENT-004 — **Rendered movement sub-blocker** | **CONFIRMED RESOLVED** | 실제 OS Move, 3개 중간 rendered frame, authoritative DrawPos 투영, 도착 후 실제 hit/selection |
| QA-PRESENT-004 — **Overall reconciliation defect** | **STILL FAILING** | severity perturbation 미복원; body-part/instance health graph와 일반 job/status 불완전 |
| QA-PRESENT-005 | **CONFIRMED RESOLVED** | 네 방향 native/wire/periodic round-trip |
| QA-PRESENT-006 | **CONFIRMED RESOLVED** | 요구된 5개 privileged command의 gameplay 차단, loopback trusted channel + capability. PoC-local 범위 |
| QA-PRESENT-007 | **STILL FAILING** | periodic non-blocking 부분은 통과하나 actual GUI main-thread 2.03초 freeze, command deadline/retention/epoch lifecycle 미완료 |
| QA-PRESENT-008 | **PARTIAL** | scripted labels/UTF-8/full-set 구분 개선; metric 의미, screenshot 해상도, 과도한 CLOSED 주장 교정 필요 |
| QA-PRESENT-009 | **PARTIAL** | missing dependency 및 proof texture 증상 해소; actual auxiliary bind 충돌/initialization 잔존 |
| QA-PRESENT-010 | **CONFIRMED RESOLVED** | target binding/다른 viewed map 불변/unresolved target rejection |

기존 001/002/003/005/010을 새로운 추측으로 재개방하지 않는다. 기존 ENGINE 및 전체 architecture 결함에 대한 상태 변경도 하지 않는다.

## 11. Architecture conclusion / final recommendation

1. **테스트한 P2 Draft/Move slice E2 feasibility:** 정상 loopback 조건의 native intent→Worker execution→repeated rendered projection은 독립적으로 입증됐다. P2 presentation 접근이 불가능하다는 결과는 아니다.
2. **Actual OS/user rendered movement:** **입증됨**. direct method 호출을 GUI 대용으로 사용하지 않았다. 세 중간 위치, 도착 수렴, 실제 moved Pawn click이 있다.
3. **PoC/test control boundary:** 요구된 5개 command에 대해 **충분함**. Production authentication/TLS/all-command authority 승인은 아니다.
4. **Main-thread liveness:** periodic slice는 개선/통과. **전체 tested GUI interaction slice는 불충분**: 실제 Draft callback에서 2초 response가 frame freeze를 만든다.
5. **Candidate C:** **PROVISIONALLY ACCEPTED 유지 권고**. Master가 최종 상태를 결정한다.
6. **ADR-002 final acceptance 전 잔여 조건:** interactive RPC 비동기/timeout/epoch 및 bounded telemetry 검증; candidate-local startup/profile 정체성과 실제 listener clean initialization 재검증; broader reconciliation의 필요한 canonical scope를 명확히 하고 검증; 기존 QA-ENGINE-002/003/004/005/006 및 accepted ADR-003/004/006A/006B/007/008의 실제 authority/provenance/custody/publication/recovery 계약을 구현 증거로 충족. ADR의 core acceptance 자체를 runtime 결함 종료로 취급하지 말 것. MSR-028의 Production NOT AUTHORIZED/ADR-002 provisional 결정을 본 QA가 변경하지 않는다.

**권장 다음 조치:** A가 interactive command path와 후보 profile/실행 manifest를 좁은 수정 범위로 재동결하고, 새로운 해시의 후보에서 GUI 지연/epoch/보조 bind를 재검증한다. general health/inventory/full-map replication을 이번 GUI 성공만으로 완성 판정하지 않는다. 본 후보는 수정하지 않았다.

QA 실행 PID 23352/23496은 path/start-time을 확인한 뒤 종료했고 QA observer 정션만 제거했다. 사용자 게임/기존 Production/후보 배포를 변경하지 않았다. [cleanup.json](%Q%/cleanup.json). 증거 목록 및 해시는 [evidence-manifest.json](%Q%/evidence-manifest.json).

**최종 판정: PARTIAL / REMAINING BLOCKER.** 보고서 제출 후 다음 Master 지시를 기다린다.
'''
(root/'QA_Remote_Tactical_Presentation_Hardening_04.md').write_text(text.replace('%Q%',q.as_posix()),encoding='utf-8')
print(root/'QA_Remote_Tactical_Presentation_Hardening_04.md')
