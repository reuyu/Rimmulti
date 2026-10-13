# QA_POC_TAC_ENGINE_02_Review

- Work Package: **WP-QA-TAC-ENGINE-02**
- Role: Independent QA / Architecture Reviewer
- Date: 2026-10-02, Asia/Seoul
- Input: `POC_TAC_ENGINE_02_Evidence.md`, actual scratch Bridge/Supervisor/FixtureGenerator, installed RimWorld 1.6 engine, independent execution and native saves.
- Architecture: ADR-001 ACCEPTED; ADR-002 PROVISIONALLY ACCEPTED; Candidate C — Trusted Tactical Worker Always.
- Production Code Modification: **NONE**. GUI / Computer Use: **NONE**.
- Evidence directory: [ENGINE02 independent QA artifacts](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002>).
- Requirement IDs below refer exclusively to root `요구사항_명세서.md`.

## 1. Executive Verdict

**ENGINE-02 Architecture Gate: FAIL. Recommendation: OPTION 2 — Candidate C 유지, ADR-002 PROVISIONALLY ACCEPTED 유지.**

Gemini가 추가한 MapPreTick/MapPostTick/Thing.DoTick 필터와 cooperative loop는 실제 개선이다. 정상 경로에서 비대상 Pawn/Animal/held item과 MapComponent를 멈추면서 대상 AI, 건강, 전력, 인벤토리 부패와 환경 처리를 진행할 수 있었다. 워밍업 후 실시간 루프는 **60.26 TPS**였다.

그러나 다음 경계는 승인할 수 없다.

1. 실제 저장 파일에 사용된 미선언 Def와 누락 mod가 검증을 통과한다. **MANIFEST_OK → READY → SAVED**, 실제 아이템 **1 → 0**을 독립 재현했다.
2. **RUN_TICKS 50000**은 여전히 monolithic이다. 병행 STATUS가 **27,383.6 ms** 기다린 뒤 큐 타임아웃 오류를 받았다.
3. 비대상 맵의 생물학적 나이/허기가 멈춰도 전역 시계 기반 chronological age는 **51,481 ticks** 증가했다. Fresh reload와 scope 해제/재개를 수행했으나 rebase 구현은 없었다.
4. `fastEcology`는 Thing.DoTick을 우회한다. 단일 scoped tick에서 비대상 식물 **25,835개**의 age가 바뀌었다.
5. Fresh load 자체가 scope 활성화 전 비대상 MapComponent/Lord와 worker-local World 상태를 진행시켰다. Full save export/reload의 무변경 경계가 성립하지 않는다.
6. 복합 fixture와 oracle은 완전성 증거로 부족하다. 숫자 Thing ID 충돌 10쌍, 중복 Verb ID, 중복 playerSettings, 잘못된 battery 저장 필드, 빈 bill 및 누락된 최종 assertion이 있다.

| Previous Defect | Independent Resolution Verdict | Scope |
|---|---|---|
| QA-ENGINE-001 | **PARTIAL** | 정상 맵 틱 필터는 개선. Global escape / clock / load boundary가 남아 CLOSE 불가 |
| QA-ENGINE-002 | **STILL FAILING** | 별도 선언의 부재 검사만 성공. 실제 사용 dependency 누락 및 false-success export 재현 |
| QA-ENGINE-003 | **STILL FAILING** | START/기본 STEP은 cooperative. 노출된 RUN 및 무상한 SliceSize는 해결되지 않음 |

이 판정은 Candidate C 자체의 불가능성을 증명하지 않는다. 한정된 개선을 인정하되 Remote/Production 진입 전에 구체적인 blocker를 해소해야 한다. 기존 QA-001~QA-014도 이번 PoC로 닫히지 않는다.

## 2. Independent Execution Evidence

설치된 실제 `RimWorldWin64.exe`를 hidden batch process로 실행했다. Unity **2022.3.35f1**, RimWorld **1.6.4871 rev591**. 가짜 engine mock 결과가 아니다. 게임 화면을 열거나 마우스/키보드로 조작하지 않았다.

원본 Bridge DLL을 변경하지 않고 별도의 scratch QA companion을 사용했다. companion은 engine age / MapComponent / GameComponent를 관측하고, LIFE-05용 main-thread stall과 scope 해제 시험을 주입한다. 관측용 GameComponent는 **실제 World business state 손상 증거와 구분**한다. 이 callback이 실행됐다는 사실만으로 모든 GameComponent가 금지돼야 한다고 결론내리지 않는다.

| Evidence | Purpose |
|---|---|
| [results.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/results.json>) | 실제 command/response, elapsed time, lifecycle, cadence, cleanup |
| [run_engine02.py](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/run_engine02.py>) / [continuation](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/continue_engine02.py>) | 복합 load, 60 TPS, 50k burst, timeout retry, fresh reload/resume, omitted dependency |
| [clean_boundary_run.py](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/clean_boundary_run.py>) | 두 맵 inventory/fire/building 관측 및 fastEcology failure injection |
| [native-audit.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/native-audit.json>) | 원본 / native export / fresh reload XML의 실제 필드와 비교 |
| [boundary-summary.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/boundary-summary.json>) | held rot, battery, fire, plant escape, warm cadence |
| [engine-il.txt](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/engine-il.txt>) | 설치된 Assembly-CSharp의 실제 IL. Source 추측이나 외부 버전 코드가 아님 |
| [WorkerBridge.cs](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs>) / [Supervisor.cs](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/Supervisor.cs>) / [FixtureGenerator.cs](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/FixtureGenerator.cs>) | 검토 당시 scratch source 보존 |
| [Probe.cs](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/ProbeMod/Source/Probe.cs>) | QA-only 계측. Production/원본 Bridge 수정 없음 |
| [protected-after.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/protected-after.json>) | 보호한 입력 59개 SHA-256 전부 불변 |

검증한 Gemini fixture SHA-256은 **719530D9A76A7D73D8108B9AC0B4948FC74C87C104F0AA06295D2DCCF4A6EE88**, 크기는 **30,366,396 bytes**로 제출값과 일치했다. `Scoped/Saves/LongScoped.rws`의 export hash는 **EDBAB77037383072E3AB603D344C52223453BD5BF251CB3F61CD15352B23E473**이다.

독립 단일 worker 실행 PID: Scoped **12296**, TimeoutRetry **22048**, Fresh **29584**, Omitted **30832**, Symmetric **27472**, CleanBoundary **17464**. DualA/B는 **25424 / 31712**였다. 정확한 실행 인자는 각 profile의 `launch.json`에 있다. 독립 profile/port/save folder를 사용했고, 8개 test-owned process가 모두 종료됐다. 임시 QA 모드 정션도 제거했으며 QA source/evidence는 보존했다.

초기 LIFE-05 시도에서 QA client의 30초 socket timeout이 Bridge의 30초 deadline보다 먼저 발생했다. 해당 시도는 **INCONCLUSIVE**로 보존했다. 60초 client timeout으로 별도 process/profile에서 재시험한 결과만 LIFE-05 판정에 사용한다. `Symmetric`의 불완전 bill을 포함한 시험도 canonical graph 승인 증거로 사용하지 않는다. 관측 가능한 field별 증거와 fixture 결함을 분리했다.

## 3. QA-ENGINE-001 Resolution

**PARTIAL — 정상 실행 경로의 필터는 작동하지만 완전한 isolation은 미해결.**

| Observed State | Target | Non-target | Result |
|---|---|---|---|
| Human position/job/food | AI/needs 진행 | 기본 scoped 구간에서 3명 위치·현재 job·food 유지 | 좁은 범위 PASS |
| Animals | wander/lay down 등 진행 | 기본 scoped 구간에서 위치/현재 job 유지 | 좁은 범위 PASS |
| Inventory Meat_Muffalo stack 5 | 2k ticks 후 `rotProg=698.538147` | stack 5, rotProg 기본값 유지 | held ticking/filter PASS |
| Fire | 대상 Fire530001 소멸 | 비대상 Fire530002 size 0.5 유지 | 환경 tick/filter PASS |
| MapComponent probe | 대상 3 → 2007 | 비대상 1 → 1 | scoped MapComponent dispatch PASS |
| Player buildings | 대상 native battery 0.0653894618 → 17.7529678 | 보완 맵의 battery/bed/door 상태 유지 | 관측 field PASS |
| Natural plants | 대상 기본 tick 경로 조사 | 기본 freeze 관측; fastEcology에서 age 변경 | 전체 isolation FAIL |
| Crop/production | 실제 검증 대상 부족 | 제출 fixture의 summary에서 crops 0, player buildings 0 | 해당 주장 미입증 |

`Baseline → Scoped1000`의 World XML diff는 0이었다. 이 결과는 **해당 fixture·해당 구간의 serialized World subtree**만 지지한다. 모든 global callback, absolute-clock getter, DLC, save/load, 임의 mod effect를 검증한 것은 아니다.

Non-target reservation job reference 4개는 같은 scoped 구간의 native XML에서 바뀌었다. 복제 fixture의 reference alias/collision 문제가 함께 있으므로 이를 독립적인 production reservation bug로 단정하지 않는다. 다만 “전체 비대상 Map 불변”의 증거로도 사용할 수 없다.

관련 요구: **SRS-FR-003/098/100/153/155, SRS-NFR-004/007, SRS-CON-010**. Offline settlement freeze와 tactical effect의 범위를 별개로 보장해야 한다.

## 4. QA-ENGINE-002 Resolution

**STILL FAILING — 실제 dependency 누락이 false-success로 export됨.**

위치: [ValidateManifestInternal:536](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:536>), 564–583, 588–597; [HandleLoadSave:617](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:617>); [Update READY promotion:276](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:276>).

실제 custom token의 Def를 `QA_UndeclaredMissingToken`으로 바꾸고 save의 meta/modIds에 `qa.actually.missing.dependency`를 넣었다. fixture의 실제 entity stack은 존재하며, 별도 command requirements에는 넣지 않았다.

| Step | Actual |
|---|---|
| `VALIDATE_MANIFEST Input` | **MANIFEST_OK** |
| `VALIDATE_MANIFEST Input QA_UndeclaredMissingToken` | **MANIFEST_REJECTED** — 명시 선언을 주면 부재 검사는 작동 |
| `LOAD_SAVE Input 0` | **QUEUED**, 이후 **READY**, Maps=2 |
| Player log | unresolved ThingDef 및 관련 load/spawn 오류 |
| `EXPORT_SAVE AfterLoss` | **SAVED**, SHA-256 **B20FC169AFCA40B70EB242D858467335A62E9AED2A29E7DFB972EFC6C927A989** |
| 실제 사용 token XML entity | **input 1 → export 0** |

[Omitted execution](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Omitted>)와 native-audit의 `MissingInput/MissingExport`를 대조했다. 이는 예외 메시지가 없다는 뜻의 “silent” loss가 아니다. **경고/예외를 로그에 남기면서도 control contract가 canonical-success로 승격하는 문제**다.

필요 수정: dependency 추출의 신뢰 경계와 typed Def coverage를 정하고, 로더의 semantic validation/error 결과를 generation READY 및 export에 연결해야 한다. caller의 선택적 목록만 검사하는 것으로 해결되지 않는다.

관련 요구: **SRS-FR-098/155, SRS-NFR-004/006/007, SRS-CON-010**. 기존 QA-ENGINE-002를 계속 OPEN으로 유지하며 동일 root cause를 새 ID로 중복 발행하지 않는다.

## 5. QA-ENGINE-003 Resolution

**STILL FAILING — cooperative 경로와 starvation 경로가 동시에 공개돼 있다.**

| Test | Independent Result |
|---|---|
| Warmed START_SIMULATION 60, STATUS 병행 | **60.261 TPS**, 91 samples, 평균 **12.810 ms**, P95 **15.595 ms**, 최대 **16.563 ms** |
| 기본 STEP_TICKS 2000 10 | 모든 2000 ticks 완료, 제어 루프에 양보; 약 **3,494.7 ms** |
| RUN_TICKS 50000 | engine loop **27,517.7 ms**, 1817 TPS; TCP response **27,534.4 ms** |
| 해당 burst 중 STATUS | **27,383.6 ms**, `ERROR: Request timed out in worker queue.` |
| SHUTDOWN responsive sample | acknowledgement **16.236 ms**; test-owned processes clean exit |

실측 결과를 “최대 latency <17 ms”라는 전체 command 보장으로 확대할 수 없다. 안정적인 warm real-time 구간에는 적용되지만 RUN/load/save와 임의 SliceSize에는 해당하지 않는다.

위치: [HandleRunTicks:719](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:719>)는 여전히 `for(count)` 전체를 처리한다. [HandleStepTicks:710](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:710>)는 caller가 제공한 양수 SliceSize에 최대치를 적용하지 않는다. `STEP_TICKS 50000 50000`도 구조적으로 같은 main-thread monopoly 경로다. 이 두 번째 입력은 별도 실행하지 않았으며 source evidence로 구분한다.

필요 수정: 안전하지 않은 RUN을 worker protocol에서 제거/통합하고, tick 수뿐 아니라 **main-thread 시간 budget** 및 hard slice cap을 적용해야 한다. 긴 native save/load의 제어/lease 결과도 별도 정책이 필요하다.

최종 NFR-011 network latency 목표 또는 worker capacity를 이번 수치로 설정하지 않는다. 관련 요구: **SRS-NFR-008/011**, ADR-002 cooperative execution/control boundary.

## 6. Global Tick Escape Audit

실제 installed `TickManager.DoSingleTick` 및 dispatch IL를 읽었다. 아래의 “unclassified”는 전부 금지하라는 뜻이 아니다. target에 필요한 경로와 domain/out-of-scope 경로를 나눌 **명시적 policy가 없다**는 뜻이다.

| Actual Engine Path | Current Adapter | Independent Assessment |
|---|---|---|
| MapPreTick / MapPostTick | instance == target | 기본 경로 필터 작동; target MapComponent 진행, non-target 멈춤 |
| normal/rare/long TickList → Thing.DoTick | Map/MapHeld 비교 | 정상 dispatch는 필터 통과. held inventory rot 관측 |
| Thing.DoTick → IThingHolder/ThingOwner.DoTick | recursive holder path | MapHeld target item ticking이 실제 작동. cryptosleep contents suspension은 엔진 의도와 구분 |
| **TickList fastEcology → Entity.TickLong 직접 호출** | **필터 없음** | **재현 FAIL**. DoTick prefix 우회, 비대상 식물 25,835 age 변경 |
| World.WorldTick / WorldPostTick | active scope에서 false | 해당 body 아래 WorldPawns/WorldComponents/FactionManager 등을 막는 구조. load/activation window는 별도 실패 |
| Storyteller / QuestManager / Autosaver / DateNotifier / TaleManager / History | prefix suppression | 해당 method body에 한정. 다른 callback/absolute time 접근을 차단한다는 뜻 아님 |
| Scenario.TickScenario | 없음 | 시나리오 component effect unclassified |
| StoryWatcher / GameEnder | 없음 | 전역 adaptation/endgame/letter effect unclassified |
| **GameComponentUtility.GameComponentTick** | **없음** | 실측 GameProbe **7 → 1484**, 장기 구간 51484. GameComponent callbacks 도달 증명 |
| LetterStackTick | 없음 | elapsed global time 기반 timeout/removal 경로 별도 policy 필요 |
| TransportShipManager.ShipObjectsTick | 없음 | target 밖 ship lifecycle 및 DLC 연계 effect audit 필요 |
| FilthMonitor / optional ScreenshotTaker | 없음 | map context/side effect 분류 필요. raw call 존재로 forbidden mutation 단정하지 않음 |
| mod Harmony prefixes/postfixes / injected components | blanket guarantee 없음 | 기본 method body를 skip해도 다른 patch의 side effect까지 불변이 되지 않음 |
| no Map / no MapHeld unspawned Thing | false | world context 억제에는 유리. 합법 target object가 아직 anchor를 갖지 않는 경우의 policy/시험은 없음 |

### Actual escape injection

기본 scoped 2000 ticks를 마친 뒤 QA companion에서 `DebugSettings.fastEcology=true`를 **한 번의 DoSingleTick 동안만** 적용하고 원상복구했다. scope는 활성 상태, target은 Map0였다.

- 비대상 `Plant_TallGrass109996`: age **23737 → 25737**.
- 비대상 `Plant_HealrootWild111354`: age **2577908 → 2579908**.
- 비대상 plant age가 변한 native ID: **25,835개**.

이는 debug configuration의 통제 가능한 경로다. 모든 production session에 fastEcology가 기본 켜진다는 주장은 아니다. 허용 worker profile에서 확실히 금지/검증하거나 동일 scope를 적용해야 한다. fixture/Prefs의 devMode와 debug profile 지원 범위를 gate에 명시해야 한다.

## 7. Clock Isolation / Resume Test

**Verdict: FAIL. 실제 rebase 구현 및 이행 증거 없음.**

실제 시나리오: Map0 target / Map1 frozen → 상당한 global tick 진행 → `LongScoped` native export → 기존 worker 종료 → fresh process load → QA companion으로 Scope.Deactivate → unscoped 1 tick 및 1000 ticks → native export. Scope 해제/vanilla 재개는 QA companion의 시험 주입이며 현재 Bridge가 정식 resume/rebase command를 제공한다는 뜻은 아니다.

| Measurement | Before | After long scoped progression |
|---|---:|---:|
| Global TicksGame | 1826 | 53307 |
| Non-target Human100302 chronological age | 698109109 | **698160590** |
| Same pawn biological age | 176109107 | **176109107** |
| Same pawn food | 0.7479999 | **0.7479999** |
| Non-target MapProbe | 1 | **1** |

chronological age delta는 **51,481**이다. 실제 engine getter IL는 `GenTicks.TicksAbs - birthAbsTicksInt`다. Pawn ticking만 막아도 global counter 기반 값은 이미 바뀐다.

Fresh reload에서는 global counter가 53307 이상으로 유지됐고 chronological age도 증가 상태였다. `RESUME_UNSCOPED 1`은 rebase 없이 실행됐으며 이후 1000 ticks에서도 같은 시간 기준이 유지됐다. 생물학적 나이는 재개 구간의 약 1000 ticks만 늘고, food도 약 .028 감소했다. **이번 fixture에서 needs가 5만 ticks 전량을 일시에 catch-up했다는 증거는 없다.** 모든 timer가 폭주한다고 주장하지 않는다.

그러나 native reload에서 비대상 `recentMemory.lastLightTick`은 **1823 → 53307**, job driver `ticksLeftThisToil`은 **-162 → -163**으로 바뀌었다. 자연 식물 일부도 reload 한 틱의 rare/long dispatch로 age **+2000**을 받았다. session elapsed time을 모든 frozen object가 동일하게 무시한다는 가정은 성립하지 않는다.

| Required Resume Dimension | Coverage / Verdict |
|---|---|
| Needs | 관측된 food/rest는 scoped freeze; resume ~1000 tick progression. broad all-needs catch-up safety는 PARTIAL |
| Job timers | native field와 현재 job 조사. reload/재개 변화 있음; 전체 job 유형 미검증 |
| Hediff | 기존 age/part/condition fields 조사; duration/expiry 타입 전체는 NOT TESTED |
| Plant growth / timers | 자연 식물 age 변화 확인. 실제 살아 있는 crop growth proof 부족 |
| Power | target native energy 및 fresh reload energy 조사. network timing 전 범위는 PARTIAL |
| Bills/production | 제출 bill은 empty. QA experimental nonempty bill은 잘못된 fixture로 제외. **NOT TESTED** |
| Age | chronological clock leak **FAIL**, biological freeze subset 확인 |
| Cooldowns / scheduled events | 전역 tick 경로 정적 검토; 의미 있는 expiry fixture에 대한 독립 oracle **NOT TESTED** |

필요 후속 requirement: worker elapsed ticks와 server-authoritative time의 관계, absolute timestamp / interval accumulator / scheduled-event rebasing 대상과 적용 지점을 명시하고, **save/reload/merge/resume end-to-end 구현**으로 검증한다. 아직 존재하지 않는 server orchestrator를 구현 증거로 사용할 수 없다. chronology가 server world time을 따라야 하는지, frozen local time을 따라야 하는지도 Master가 정책으로 확정해야 하며 worker의 임의 tactical counter로 결정되면 안 된다.

## 8. Manifest Completeness Review

**“full manifest safety”는 DOWNGRADE REQUIRED. 현재는 caller-declared ThingDef/mod 존재 검사 PoC다.**

| Question | Actual Source / Test |
|---|---|
| reqMods / reqDefs 생성 | LOAD/VALIDATE command의 공백/쉼표 인자에서 생성. save 전체 dependency 자동 추출 없음 |
| save meta.modIds 활용 | HashSet `saveModIds`를 만들지만 이후 사용하지 않음 |
| 실제 사용하는 undeclared ThingDef | 독립 누락 fixture에서 검증 통과, entity loss 후 READY/SAVED |
| HediffDef / RecipeDef / ResearchProjectDef | typed validation 없음; 별도 engine 실행에 의한 각각의 loss는 NOT TESTED |
| 같은 packageId, 다른 mod version / DLL / Def content | 버전/해시/content fingerprint 비교 없음. 실제 교체 mod 실험은 NOT TESTED |
| DLC mismatch | DLC도 saveModIds에서 읽은 뒤 검증하지 않음. actual missing DLC save load는 NOT TESTED; 보장할 코드 경로 없음 |
| game version | 비어 있으면 허용; `StartsWith("1.6")` 문자열만 검사. 정확한 patch/revision compatibility 검증 아님 |
| whole XML validation | meta를 읽은 뒤 break. 뒤쪽 malformed XML/graph 손상까지 preflight했다고 볼 수 없음 |
| post-load data loss detection | nonempty Maps / Playing / no LongEvent만 READY 조건. load logs/graph expected inventory와 결합하지 않음 |
| canonical export gating | READY만 검사. READY가 false-success이면 export도 success |

필수 경계: **partial load + entity loss가 READY/EXPORT로 승격되지 않아야 한다**. 자동 dependency 계산 방식은 ADR/PoC에서 정할 수 있지만 trusted package manifest의 완전성, content compatibility 및 post-load semantic gate는 생략할 수 없다.

## 9. Complex Graph Review

**Subset roundtrip: 확인. “100% complex entity graph integrity”: INSUFFICIENT EVIDENCE / DOWNGRADE REQUIRED.**

| Dimension | Native / Engine Evidence | Judgment |
|---|---|---|
| Weapon | Gun_Autopistol9001, carried weapon preserved in Long → Reload | subset PASS |
| Apparel | shirts/pants/vest present, native references retained | subset 확인; final Gemini pass assertion 누락 |
| Inventory | MedicineIndustrial9004 stack 5, nested innerList retained | subset PASS; final Gemini pass assertion 누락 |
| Nontrivial hediff / installed part | Stab severity 3 / part index55, BionicTongue index22 존재 | part/def subset 확인; 중복 Hediff identity 및 progression audit 별도 필요 |
| Bed assignment | Human302 ↔ Bed9104 references preserved | subset PASS |
| Door / workbench / battery | native identities retained | fixture battery starts at near0, report의 600 초기화 불성립; workbench bill empty |
| Stockpile | zone/filter/priority XML 존재 | 게임 내 유효 settings와 저장된 inventory 관계 전체 oracle 부족 |
| Tamed animal/master | animal faction PlayerColony, **master null** | claimed master relationship **미입증** |
| Corpse / nested holder | Corpse_Human3240 inside **AncientCryptosleepCasket3236**, inner ref Thing_Human3237 유지 | nested subset 확인; 해당 corpse가 sarcophagus에 있다는 설명은 부정확 |
| Crops | fixture에 Plant_Rice XML 있지만 live summary crops=0; QA 보완 cell grid에서도 rice 관측 실패 | crop growth claim 승인 불가 |
| Faction / location / stable IDs | 일부 native entity/assignment 비교 가능 | 전체 graph 승인 불가; errors와 normalization 먼저 제거 필요 |

### Fixture correctness

- 원본 복합 fixture의 numeric Thing ID가 10쌍 충돌한다. 예: Gun_Autopistol9001 / Plant_Grass9001; Bed9104 / Plant_Grass9104; Plant_Rice9108 / Plant_Brambles9108. 실제 player log에서 loaded-object registration `ArgumentException`이 발생했다.
- 복제된 두 맵의 일부 Verb loadID도 중복된다. `Cannot register ... Id already used`가 로그에 있다. **QA의 기존 TwoMapFixtureV2 remapping에서도 이 경계를 충분히 처리하지 못한 점을 인정한다.** Gemini가 이를 기반으로 증분 fixture를 만든 것이므로 모든 fixture 결함을 신규 Bridge 구현 탓으로 돌리지 않는다.
- Boomrat의 첫 playerSettings/master는 null이고 두 번째 playerSettings에 master를 덧붙였다. 실제 serializer/engine master는 null이다. 별도의 QA 보완에서도 유효한 master 상태를 확립하지 못했으므로 master 복원 PASS를 부여하지 않는다.
- Battery는 `<storedEnergy>600</storedEnergy>`를 쓰지만 actual native field는 `<storedPower>`다. 초기 native export는 **0.0653894618**, 이후 target tick으로 **17.7529678**이 됐다.
- Workbench의 billStack/bills는 빈 목록이다. 실제 recipe/bill/production progress persistence를 시험하지 않는다.
- Stab part index55는 engine summary에서 Leg다. 보고서의 Torso 설명과 일치하지 않는다.

### Oracle correctness

[Supervisor final graph verdict:528](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/Supervisor.cs:528>)는 `apparelMatches`, `inventoryMatches`, `buildingMatches`를 계산/출력하지만 **PASS 조건에 포함하지 않는다**. Animal master, corpse/holder ownership, power energy, full faction identity, hediff severity, entity IDs of equipped/contained items도 충분히 검증하지 않는다. Faction **defName**은 서로 다른 Faction instance identity의 동등성 증명이 아니다.

World isolation PASS도 [Supervisor:428](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/Supervisor.cs:428>)에서 executable oracle 없이 문자열로 지정한다. `target progressed`에 OR를 사용하므로 target crop/기타 subtype의 동작 실패가 PASS를 막지 않는다. Empty collection에 대해 변화가 없다는 사실도 검증 완료로 확대하면 안 된다.

필요 수정은 Production이 아니라 **fixture/oracle의 신뢰성 보완**이다. 엔진에서 생성된 유효 graph를 기준으로 전체 business identity와 관계를 비교해야 한다.

## 10. Target Simulation Completeness

필터가 target을 통째로 멈추는 것은 아니다. 다음은 실제 engine/native field로 확인했다.

| Target System | Evidence | Result |
|---|---|---|
| Pawn AI / needs | position/jobs changed; target food 감소 | PASS within tested scope |
| Animals | wander/lay down 및 위치 변화 | PASS within tested scope |
| Hediff | 장기 구간 Malnutrition 신규 발생, 기존 injury/part 저장 | 정상 health progression의 일부 확인 |
| Battery / power components | storedPower 0.0653894618 → 17.7529678 → 600 | 충전 진행 확인. 모든 power topology 보장 아님 |
| Map component | target QA MapProbe progresses; non-target basic interval frozen | component dispatch 확인 |
| **held tickable Thing** | target inventory Meat_Muffalo stack5 rotProg **698.538147**, non-target rotProg 기본 유지 | 실제 held-object ticking 확인 |
| Fire/environment | target fire 소멸, non-target fire size0.5 유지 | 환경 tick subset 확인 |
| Crop growth | live crop oracle 대상 없음 | **NOT PROVEN** |
| Workbench production / bill completion | meaningful valid nonempty bill fixture 없음 | **NOT TESTED** |
| Arbitrary unspawned / suspended holders / DLC effect | IL 경로 조사, 구체적인 모든 타입은 시험 안 함 | **PARTIAL** |

`Symmetric`에서 수동 추가한 bill은 save NRE를 발생시켰다. 이를 engine/Bridge의 production bill bug로 분류하지 않고 **불완전한 QA fixture로 제외**했다. `CleanBoundary`는 해당 bill을 제거한 후 inventory/fire/filter 목적만 시험했다. 이름과 달리 inherited Verb identity 문제까지 모두 해결한 canonical-clean fixture라는 뜻은 아니다.

최종 Tactical Worker completeness PASS에는 원격 command/owner pawn control 외에도 target plant/production, held/suspended object의 지원 목록 및 failure oracle가 필요하다.

## 11. Lifecycle / LIFE-05

| Lifecycle | Independent Evidence | Verdict |
|---|---|---|
| LIFE-01 LOAD 중 tick | `ERROR ... state is LOADING` | PASS for tested overlap |
| LIFE-02 LOAD 중 export | `ERROR ... state is LOADING`; Premature export 없음 | PASS for tested overlap |
| LIFE-03 LOAD 중 second load | `already in progress (Gen=1, State=LOADING)` | PASS for tested overlap |
| LIFE-04 disconnect/reconnect | 별도 fresh socket에서 HELLO/STATUS, generation/map state 유지 | PASS for idle connection replacement; pending control cancellation 보장 아님 |
| **LIFE-05 timeout 후 late queued execution** | 33초 main-thread block, server response 30,001.2ms timeout, 이후 queued STEP77 만료 거부 | **PASS for server-timeout queued-command scenario** |
| LIFE-06 shutdown 중 command | second socket RUN10에 EOF, SHUTDOWN ack16.236ms, process exit | PASS for tested shutdown |

LIFE-05 재시험: `TimeoutRetry/before-timeout.txt`와 `after-timeout.txt`, server STATUS를 대조했다. **TicksSim=0, RemainingStep=0** 유지; STEP77이 나중에 실행되지 않았다. global tick 53310 → 53314의 일부 idle/startup drift는 있었지만 **77 tick step의 실행 증거가 아니다**. scoped business request는 큐 age >10초 검사로 거부됐다.

Generation counter만 보고 PASS한 것이 아니다. 실제 서버 timeout 응답을 받은 뒤 main-thread를 풀어 결과를 검사했다. 초기 30초 QA socket deadline failure는 이 최종 성공 증거로 사용하지 않았다.

남은 범위: caller의 더 짧은 deadline/disconnect, 이미 실행 중인 긴 RUN/save, queued request의 generation/session fencing, load failure의 LOADING 탈출. `BridgeRequest.CorrelationId`는 0으로 남고 dispatch에서 검증하지 않는다. queued-time 검사와 cancellation/fencing은 서로 다른 보장이다. 모든 operation lifecycle이 완성됐다고 판단하지 않는다.

## 12. Full Save Roundtrip Side Effects

**FAIL for full non-target/world preservation boundary.** 단순 XML 문자열의 변경 수와 semantic damage를 분리했다.

`LongScoped → fresh ReloadBaseline`에서:

- Non-target QA MapProbe **1 → 2**.
- Non-target Lord `ticksInToil` **1824 → 1825**.
- Non-target job driver timer **-162 → -163**.
- Non-target recentMemory.lastLightTick **1823 → 53307**.
- Non-target 자연 식물 일부 age **+2000**.
- worker-local World faction naturalGoodwillTimer **1 → 2**.
- World component cycleIndex **3648 → 3650**.
- target battery **600 → 599.999695**.

READY 활성화 전에 native Game이 Playing으로 들어가 실제 tick을 실행할 수 있다. source Update는 이후에 scope와 pause를 설정한다. 이 window에서 WorldTick suppression도 아직 active가 아니다. 비교는 all-native field diff와 live MapProbe를 함께 사용했다.

World XML raw diff **3569개**를 전부 business-state corruption으로 계산하지 않았다. ideology/precept ordering과 normalization 변화가 포함되어 있고 compressed field의 직렬화 차이도 있다. 반면 위 counter/timer/plant age는 실제 상태 변경의 구체적 증거다.

Stable subset의 bed/weapon/medicine relation은 fresh reload에서 보존됐다. 이것과 full non-target save preservation은 별개다. 완전한 목표가 raw full-save merge라면 load 중 fence를 먼저 적용하거나, 영향 범위를 검증한 extraction/merge 전략으로 non-target graph를 canonical 결과에서 제외해야 한다. 두 방식 중 어느 것을 택하든 실제 end-to-end proof가 필요하다.

World time 용어도 분리한다.

1. **TickManager global counter:** 증가함.
2. **World.WorldTick body:** active prefix로 기본 scoped 구간 억제. load/activation과 기타 global paths는 별도.
3. **Dedicated Server World Time:** 이번 standalone engine test는 실제 서버에 연결하지 않았다. 변경 불가라는 환경 사실은 canonical server authority integration 검증이 아니다.

따라서 `World Ticks simulated by Worker: 0`은 “scope active 동안 해당 WorldTick body를 skip한다”로 제한해 표기해야 한다. worker artifact의 world-domain state 전체 불변을 뜻할 수 없다.

## 13. Dual Worker Sanity

독립 두 process에 **같은 complex native baseline**을 넣고 별도 profile/port에서 load와 scoped STEP100을 병행했다. DualA(PID25424)는 target0, DualB(PID31712)는 target1이다. 각 worker의 RemainingStep=0 및 TicksSim=100을 확인했고, 각각 다른 save folder에 IndependentA/IndependentB export가 SAVED로 반환됐다. 두 process 모두 exit code0으로 종료했다. **PASS within this sanity scope.**

[dual_lifecycle_run.py](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/dual_lifecycle_run.py>), `DualA/launch.json`, `DualB/launch.json`, `dual.log`, `results.json`의 `dual-done`이 실제 PID/port/state/결과를 기록한다. ports는 **29346 / 29347**이다.

이 검증은 port/profile/save isolation sanity다. complex graph의 기존 fixture 결함을 치유하거나 worker authority isolation을 전체 승인하는 시험이 아니다. **Capacity certification, max concurrent sessions, per-worker VRAM, remote bandwidth 추정으로 사용하지 않는다.**

## 14. Remaining Risks

- Trusted immutable package manifest와 실제 content/version compatibility 미완성.
- Scope 활성화 이전 load lifecycle 및 export/reload normalization의 authoritative-effect 경계 미완성.
- absolute timestamps / ages / cooldown / scheduled events의 timebase와 rebase 구현 미완성.
- GameComponent/Scenario/Letter/Ship/DLC/mod hook의 허용 scope와 worker-supported profile 미정의.
- 전역 command/queue bounds, inflight cancellation, generation/session fencing, fault propagation 미완성.
- STEP slice/count/TPS 상한 및 NaN/overflow, invalid target index의 잘못된 map 선택 등 입력 경계 미검증.
- meaningful crop/bill/master graph fixture와 negative graph oracle 미완성.
- full export의 atomic publication, disk failure, torn save, hash/content semantic gate 미검증.
- server-side durable commit / operation idempotency / fencing / worker crash recovery는 별도 미구현/미검증. 원본 QA-001~014 OPEN.
- Remote Tactical pawn authorization, input transport, result distribution, leases와 takeover, client reconnect는 이번 engine PoC의 합격 범위가 아니다.

이 항목들을 구현 난이도 때문에 offline 공격 금지 또는 target interaction 축소로 해결해서는 안 된다. **SRS-FR-153/154/155, SRS-CON-010** 요구를 그대로 유지한다.

## 15. New Defects

### QA-ENGINE-004 — Frozen map의 authoritative timebase 미분리

- **Severity: CRITICAL — architecture boundary / result artifact의 논리적 시간 오염 위험.** 아직 canonical server에 commit됐다는 뜻은 아니다.
- **Requirement:** SRS-FR-003/155, SRS-NFR-004/006/007; ADR-002 clock isolation.
- **Location:** [WorkerBridge.Update:347](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:347>), DoSingleTick 사용; source 전체에 rebase 구현 없음; actual Pawn_AgeTracker.get_AgeChronologicalTicks IL.
- **Reproduction:** target0 / frozen1 → 51k 이상 global ticks → export/fresh reload → scope deactivate/resume.
- **Expected:** frozen map의 시간을 authoritative policy에 맞게 보존/재기준화하고 elapsed tactical time을 새 canonical state에 임의로 적용하지 않음.
- **Actual:** non-target chronological age +51,481, reload lastLightTick 1823→53307; future-rebase 설명만 존재.
- **Root Cause:** 하나의 TicksGame을 모든 map의 absolute time으로 사용하며 tick filtering만 수행.
- **Required Fix:** 중앙 world time / local map time contract와 실제 rebase/extraction/merge 구현, typed timer fixture의 end-to-end acceptance. Master 정책 결정이 필요한 age 의미도 명시.

### QA-ENGINE-005 — Global tick dispatch coverage 및 debug escape

- **Severity: HIGH.**
- **Requirement:** SRS-FR-003/153/155, SRS-NFR-007, SRS-CON-010.
- **Location:** [Patch_Thing_DoTick:109](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:109>); actual TickList.Tick IL_0089 / IL_00D5; unfiltered GameComponentUtility and other dispatches.
- **Reproduction:** scoped target0, fastEcology를 한 tick만 활성화.
- **Expected:** 지원 worker profile은 non-target mutation 경로를 차단/거부하고 target-required global hooks의 permission policy를 명시.
- **Actual:** non-target plants 25,835개 age 변화; GameComponent callbacks은 무분류 상태로 계속 실행.
- **Root Cause:** DoTick만 intercept하면 모든 entity/global tick을 포함한다는 불완전 coverage 가정.
- **Required Fix:** engine dispatch inventory, supported DLC/mod/debug profiles, per-path allow/suppress policy 및 guard/injection tests. 모든 GameComponent를 일괄 차단하는 식의 target 기능 손상은 허용되지 않음.

### QA-ENGINE-006 — Fixture / oracle가 전체 graph 성공을 증명하지 못함

- **Severity: HIGH — Architecture Gate의 false-positive test risk.**
- **Requirement:** SRS-FR-098/100/155, SRS-NFR-004/006; ENGINE-02 complex graph acceptance.
- **Location:** [FixtureGenerator.cs](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/FixtureGenerator.cs>); [Supervisor:419](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/Supervisor.cs:419>), 428, 528.
- **Reproduction:** supplied hash-matched fixture load/log/native export; inspect master/bill/power/IDs; mutate apparel/inventory/building comparison counters in a logical test review of final predicate.
- **Expected:** graph fixture의 identity/reference가 유효하고 필수 graph dimensions의 불일치가 반드시 FAIL로 전파됨.
- **Actual:** numeric Thing/Verb ID collisions; master null; empty bills; battery field mismatch; apparel/inventory/building counters가 final PASS predicate에 없음; world PASS hardcoded.
- **Root Cause:** 수동 XML graph 작성 및 요약 문자열 일부에 의존하는 불완전 oracle. 기존 QA fixture의 remapping 부족도 포함.
- **Required Fix:** engine-generated valid fixture, globally unique runtime load IDs, real master/training/bill/plant state, full semantic oracle와 fail-by-mutation negative tests. Production 문제와 test asset 문제를 구분해서 수정.

### QA-ENGINE-007 — Load/Ready 이전 scope fence가 없음

- **Severity: HIGH.**
- **Requirement:** SRS-FR-003/155, SRS-NFR-004/006/007.
- **Location:** [Update:276](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:276>), 292–298; [HandleLoadSave:648](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:648>).
- **Reproduction:** LongScoped export → all-new process → LOAD → READY → native reexport; compare frozen MapProbe/Lord/plants and World counters.
- **Expected:** full-save lifecycle까지 비대상 graph와 worker-local world authority를 보호한 이후 READY 허용.
- **Actual:** non-target MapProbe1→2, Lord+1, World goodwill timer+1, 일부 plants+2000. generation READY 판정은 이 mutation을 검사하지 않음.
- **Root Cause:** Playing 진입 후 MonoBehaviour.Update에서 늦게 scope/pause 설정; engine init/normalization도 semantic gate 밖.
- **Required Fix:** load-time fence 및 canonical merge scope/semantic validation. initialization의 의도된 변경과 forbidden tick effect를 독립 oracle로 분리.

### QA-ENGINE-008 — START가 이전 idle frame의 시간을 simulation backlog로 사용

- **Severity: MEDIUM.**
- **Requirement:** SRS-FR-003, SRS-NFR-004; ENGINE-02 target cadence contract.
- **Location:** [Update real-time accumulator:349](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:349>), [HandleStartSimulation:684](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/Reviewed/WorkerBridge.cs:684>).
- **Reproduction:** native export가 같은 Unity frame을 오래 점유한 직후 START60 → 약 6초간 STATUS 조회.
- **Expected:** START를 수락한 이후의 경과 시간만 60TPS 실행 budget에 반영.
- **Actual:** 초기 sample에 10→50→90→120 tick catch-up burst; 표본 평균 **76.96TPS**. 워밍업 후 시작하면 **60.26TPS**.
- **Root Cause:** accumulator는 0으로 초기화하지만, 같은 Update에서 START 이전의 긴 처리를 포함하는 `Time.unscaledDeltaTime`을 가산.
- **Required Fix:** START의 monotonic time 경계를 기준으로 budget을 계산하고 pause/export/resume 사이의 시간 반영 및 debt policy를 시험. 정상 warm cadence가 양호한 점은 인정.

## 16. ADR-002 Recommendation

**OPTION 2 — ADR-002 PROVISIONALLY ACCEPTED 유지.** QA가 ADR 상태를 ACCEPTED로 변경하지 않는다. 이 권고를 Production implementation 시작 승인으로 해석해서도 안 된다.

의존 순서에 따른 targeted work:

1. **Fixture/oracle trust gate:** engine-native graph 생성, numeric/Verb/Hediff/Job identity 검증, 실제 crops/master/nonempty bills/holders, 전체 dimension assertion과 negative mutation tests. 현 fixture로 “100%” 승인 증거를 만들지 않는다.
2. **Package/load publication gate:** save에서 사용하는 mod/DLC/typed Def/content fingerprint 생성·검증, post-load error/graph failure 시 READY/EXPORT 차단. 미선언 missing ThingDef와 다른 Def category 재시험.
3. **Pre-load authority fence + dispatch policy:** Playing 전부터 scope/clock 제어, GameComponent/Scenario/DLC/mod/debug 경로 분류. fastEcology 거부/필터 및 load 중 World/non-target drift 방어 증명.
4. **Clock/rebase or target-only merge PoC:** Master가 server-world/local-map time 계약 확정. 충분한 경과 ticks, save/fresh reload/scope 해제/resume을 거쳐 age/needs/jobs/hediffs/plants/power/bills/cooldowns/events 실검증.
5. **One cooperative command path:** RUN과 무상한 slice 제거/통합, wall-clock budget/cancellation/fencing, timeout/disconnect/inflight/export 결과 검증. cold-start cadence와 heartbeat도 시험.
6. 위 QA 이후 Master가 **ADR-002 ACCEPTED 여부**와 Remote Tactical 독립 PoC/Production 진입 경로 결정.

Candidate C를 포기할 근거는 아직 없다. 다음 단계로 넘어가기 위해서는 이번에 재현한 false-success publication과 authority/clock/load 경계를 “future work” 설명만으로 남겨둘 수 없다.

## 17. Final QA Verdict

```yaml
[QA REVIEW]
Work Package: WP-QA-TAC-ENGINE-02
Requirements Reviewed:
  - SRS-FR-003
  - SRS-FR-098
  - SRS-FR-100
  - SRS-FR-153
  - SRS-FR-154
  - SRS-FR-155
  - SRS-NFR-004
  - SRS-NFR-006
  - SRS-NFR-007
  - SRS-NFR-008
  - SRS-NFR-011
  - SRS-CON-010
Verdict: FAIL
Architecture Status: BLOCKED BY ARCHITECTURE
ADR-002 Recommendation: OPTION 2 — PROVISIONALLY ACCEPTED 유지
Previous Defect Resolution:
  QA-ENGINE-001: PARTIAL
  QA-ENGINE-002: STILL FAILING
  QA-ENGINE-003: STILL FAILING
Confirmed Limited Success:
  - 정상 scoped Pawn/Animal/held object/MapComponent filter
  - target AI/needs/health/power/held rot/fire progression subset
  - warmed cooperative real-time loop ~60TPS
  - LIFE-01/02/03/05/06의 실행된 경계 시나리오
New Defects: QA-ENGINE-004 through QA-ENGINE-008
Production Modified: false
GUI Used: false
Final Recommendation: Master에게 제출; targeted boundary 수정/QA 후 gate 재심사
```

정상 경로의 개선을 인정하지만 **“Every requirement satisfied / boundary safe / 100% graph integrity”는 독립 증거가 지지하지 않는다**. 요구를 축소하지 않고 Candidate C의 경계를 강화해야 한다. 이 보고서를 Master에게 제출하고 다음 지시를 기다린다.
