# RimWorld 1.7 / Waylith 영향 분석 — 2026-10-13

판정: 프로젝트 전체 재설계를 요구한다는 증거는 없다. Engine/Client·Harmony·런타임 연결과 Gate05 실제 실행 증거에 별도 호환성 검증이 필요하다. 1.7 호환 PASS/이전 승인/현재후보 재빌드/설치변경은 아니다. Canonical SRS 대상1.6 유지; 1.7 지원 결정은 아직 OPEN이다.

## 확인한 외부 사실과 근거

Ludeon 공식 발표는 UTC 2026-10-12 17:17, 한국시간 2026-10-13 02:17이다. Unity에서 Ludeon 자체 Waylith로 전환한1.7을 unstable beta로 공개했으며 main branch는1.6이다. 개발사 내부 측정2–4배, 후기콜로니2.2배, 1500mods로드14→6분은 제작사 측정이고 WarEconomy 성능측정이 아니다. 1.6/1.7 save 양방향 호환 및 대부분mod무수정호환을 발표했지만 모든mod/내부API/멀티플레이결정성 보장이 아니다. 별도 게임도 Waylith로 개발중이라고 언급했다. [공식 발표](https://ludeon.com/blog/2026/10/announcing-the-waylith-engine-and-update-1-7/), [공식 Steam 발표](https://steamcommunity.com/games/294100/announcements/detail/672882362547178634).

Harmony의 원개발자 RimWorld 저장소는1.7에 Harmony3/.NET10,1.6에 Harmony2.4.3/.NETFramework4.7.2를 사용한다고 명시한다. 이는 현재 public maintainer source 상태이며 우리 로컬 loaded DLL의 버전 관측을 대체하지 않는다. Build 안내도1.7만새build/old1.6payloadhash보존 및 fullin-gamecompat별도검증을 구분한다. [HarmonyRimWorld README](https://github.com/pardeike/HarmonyRimWorld), [BUILDING](https://github.com/pardeike/HarmonyRimWorld/blob/master/BUILDING.md). Harmony3.0.0-rc.2 공개release 존재, prerelease상태: [release](https://github.com/pardeike/Harmony/releases/tag/v3.0.0-rc.2). 이 사실로 임의자동업그레이드 또는 net472기존DLL이 전부 실행불가라고 단정하지 않는다.

기술적 추론은 위1차출처와 우리소스만을 근거로 한다. Community wiki의 UnityStubs/Waylith참조, 로그새경로, Prepatcher/Vulkan/shader 세부 주장은 검색에서 발견했으나 이 문서에서 공식확정값으로 채택하지 않는다. 공식1.7ModderPrimer/API전체계약과 실제1.7배포의 schema/assemblyinventory는 확보하지 않았다. 저자 직접작성compatmod사례는 존재하지만 우리 후보검증으로 승계하지 않는다.

## 실제 로컬 확인

- Canonical SRS docs/요구사항_명세서.md:6,37,1781는1.6대상.
- Steam 설치 Version.txt는 실제 `1.6.4871 rev590`이다. RimWorldWin64.exe666624, Assembly-CSharp15777280 존재; 조사한root/Managed의 Waylith.dll 및rootUnityStubs.dll 경로는없다. 일부경로absence와 Version.txt 관측이며 전체설치inventory/버전무결성증명은 아니다. 실행/Steambranch변경없음.
- Server csproj net8.0, Common netstandard2.0. Client 및 WorkerBridge csproj net472.
- Client Lib.Harmony PackageReference2.3.3; Worker은현재Steam Workshop0Harmony실제파일을 직접참조. Loadedversion은이번소스조사에서 새로확정하지 않았다.
- Client/Worker는 Assembly-CSharp, UnityEngine/CoreModule/IMGUIModule 등의1.6 Managed참조경로; PostBuild배포1.6/Assemblies. About.xml supported1.5/1.6이며1.7미표기; 1.5표기는canonical1.6QA PASS가 아니다.
- WorkerBridge MonoBehaviour/Unity Object/GameObject/DontDestroyOnLoad/Destroy/Awake/Update/OnDestroy/logMessageReceived와 Harmony TickManager/TickList/Map/World/Storyteller patch를 사용한다.
- Client MainThreadQueue.TickManagerUpdate→Time.deltaTime interpolation, Tick/World/fog/UIpatch는EngineAPI의존.
- EngineHostCensus는 실제Assembly-CSharp SHA와MVID를 boundcontentmanifest에 결속한다. 1.7의 다른게임어셈블리/CLR/native/patchprofile을1.6identity로 통과시키면 안된다. Latest exactR34Engine DLL8091F441/MVID7b08... 및 R35publisher9CAE...는현재frozenlineage이며 이번조사에서 수정하지 않았다.

## 영향 판정 — 우리 코드 기준 추론

| 영역 | 상대 영향 | 필요한 확인 |
|---|---|---|
| Dedicated Server·transaction/persistence·domainauthority | 직접 영향 낮음 | 게임과별도.net8 프로세스; 동일wire/schema값 원문·typedroundtrip 실제crossruntime검증 필요 |
| Common DTO/JSON·publisher 안전보완 | 비교적 낮음 | 계약/opaque원문보존 의미는유지; 새exe/assembly/path/manifestidentity만실제확정. 1.7이기존안전결함을해결하지않음 |
| Client/Worker build/reference/Harmony | 중간~높음 | 실제1.7reference와Harmony3 loadedpatch처리, oldDLLload가능성 및 새version별build 필요성부터검사 |
| Worker lifecycle·tick suppression/control·log callback | 높음 | 콜백순서/메인thread/ownedsocket-thread/normalshutdown/hold/oneLocalClockwriter의 실제관측. 호환API존재만으로semanticsPASS아님 |
| native Validator/content/context·resultreceiver | 높음 | 실제새game/runtime/native/content/issuer/channel/one-useboundtask identity에맞춘새E2 |
| UI/fog/rendering | 중간 | game/API/render변경대상patch 및실제화면검증. 현재Gate05native보다우선순위낮음 |
| 성능/worker운영비용 | 개선가능 | 제작사부하자료는고무적이나우리WorkerTPS/coldstartup/메모리/CPU는새benchmark전unknown |

설계의 DedicatedServer finalauthority, W/L/G/M, oneLocalClockwriter, islandbarrier, targetpublication, Workerboundedproposal은엔진교체로 바꿀필요가 확인되지 않았다. 빨라진게임이 동기화/권한/스키마/GQ1/PlayerGlobal 문제를자동해결하지 않는다. 엔진교체→headless전용server가능/zero-drift/perSettlementprocess 채택을추론하지 않는다.

“모드가 로드됨”, “저장파일호환”, “특정버전Worker/Validator의 의미·결정성·권한증거가맞음”은서로다르다. 1.6증거는그 lineage에서유효한역사로보존하지만1.7E2PASS로재사용하지 않는다. 서로다른1.6/1.7worker 또는검증자를 같은profile로 혼합하지 않는다; 같은seal/context에서허용하려면별도adoptedcompatcontract와새독립증거가필요하다. 아직그승인없음.

## 권장 진행과 현재 결정 범위

1. Current1.6 Gate05publisher/carrier/task연결보완과Solindependentreview는계속한다. Currentcandidate/QA/frozenruntime은보존, Steam설치/프로젝트targetframework/Harmony/SRS 자동변경하지 않는다.
2. 별도1.7 compatibility feasibility 작업은 실제betaexe/CLR/assembly/native/Unitycompat/Harmony/content/launchargv/logpathinventory와전용ownedroot 확보부터 시작하도록 준비할수있다. 이번요청은분석만이며 설치/다운로드/1.7실행WP는전송하지않았다.
3. 별도newcandidate에서modload/Harmonypatchtargets/AwakeUpdate/mainthread/logevent/ownedshutdown/tickhold/smallboundedstep/contentsnapshot을순서대로검증한뒤nativevalidator+oneusereceiverE2. .NET10만으로Common/Server를함께올릴이유는없다. 필요할때버전별Engineadapter/build와공통protocol을분리하며physicalsplitOPEN을자동채택하지않는다.
4. 1.7공식지원/우선개발target전환은제품결정이다. 새targetadoption과version별release/manifest/evidence 관리후About1.7표시. 기존1.6자료를덮어쓰지않는다.

직전추정 A추가WP4–6은현재1.6Gate05 기준이다. 1.7이전·dual-support까지자동포함한약속이아니다. 별도호환성조사 후 작은buildadapter+새runtime/E2준비로끝날지추가native보완이필요할지결정하며 오늘근거만으로추가WP개수를확정하지않는다. Gate05 E2현재NOT_RELEASED/High4OPEN/Engine002006Pipeline007-currentSchemaGQ1OPEN/FoundationHOLD unchanged.

조사방법: 공식발표/원개발자repository 검색·읽기 및로컬source/textmetadata조회만. Candidate/producerhelper/gamecompile·게임실행0; news조사로새agent/model/dispatcher/scheduler/Steambranch변경없음. 동시Sol R35보고서의선택적줄조회오류는별도sameWP R2skip/finalization승인으로처리했으며이번1.7분석과후보QA를혼합하지않는다.
