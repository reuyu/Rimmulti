# WarEconomy 참조 모드 재사용 분석 — 2026-10-08

Master disposition: **구체적 재사용 후보 채택 / 통합 구현·새 WP·runtime PASS는 미승인**. 사용자 요청에 따라 실제 로컬 소스를 정적으로 분석했다. 현재 A의 Gate05-R2를 유지한다. 해당 코드의 WarEconomy 후보 편입은 별도 범위·새 identity·검증이 필요하다.

Multiplayer의 시간 context 전환, native child process 기동, save/load 재구성, replay/진단 코드는 우리 PoC의 구현 비용을 줄일 수 있다. Together는 공유 World·정착지·거래·방문 UX와 server packet 흐름을 참고하는 데 유용하다. 그러나 두 모드가 작동한다는 사실만으로 WarEconomy의 서버 최종 권한, 오프라인 경제 원자성, 독립 validator, 시간 비간섭을 증명하지 않는다.

## 1. 실제 자료와 분석 한계

| 항목 | 실제 확인 |
|---|---|
| 프로젝트 | `C:\Users\user\Desktop\RimMulti`; root `.git` 없음. Git HEAD/branch/clean 상태 unavailable |
| MP 루트 | `C:\Users\user\Desktop\RimMulti\Multiplayer-master\Multiplayer-master` |
| RT 루트 | `C:\Users\user\Desktop\RimMulti\Rimworld-Together-development\Rimworld-Together-development` |
| MP 버전/의존성 | Client csproj ReleaseVersion 0.6.2 / net48 / C#12 / Krafs.Rimworld.Ref 1.6.4566 / Harmony2.4.1 / MultiplayerAPI0.6.0. About은 RimWorld1.6, >=1.6.4491, Prepatcher 의존을 선언 |
| RT 범위 | About은1.5/1.6 지원 선언. 로컬 Source의 csproj는 Server/RTServer.csproj 하나; net8.0. RTClient/RTShared/RTNetwork는 Source/Assemblies의 DLL이고 그 프로젝트 원문은 없음 |
| 기준 출처 | 로컬 LICENSE/About/csproj/실제 함수·테스트 원문. 두 참조 root의 `.git`도 없음; upstream commit/최신 release/로컬 수정 여부는 미확정 |
| 실행 | 참조 모드 설치·빌드·실행·테스트를 하지 않았다. 아래 테스트는 **읽은 테스트 코드**이며 실행 PASS가 아님. DLL 역컴파일도 하지 않음 |
| identity | `coordination/REFERENCE_MOD_SOURCE_INVENTORY_20261008.json`: 검토 대상 파일의 실제 SHA256/size/line count 및 핵심 함수 line anchors. 분석 스냅샷 식별이지 우리 frozen candidate manifest가 아님 |

MP csproj의 CopyToRimworld target은 기본 ModOutputPath의 Assemblies/AssembliesCustom를 변경한다. PersonalDefinitions.targets를 조건부 import한다. 검토만을 위해 빌드를 실행하지 않았다. MP net48/RimWorld1.6.4566 의존을 우리 WorkerBridge net472 및 실제 설치와 호환된다고 추정하지 않는다. RT Server net8.0이라는 공통점도 DB/프로토콜/authority 호환성을 뜻하지 않는다.

## 2. 라이선스와 재사용 방식

MP root LICENSE는 **MIT, Copyright(c)2018 Zetrith**다. 코드 추출·개조 후보로 사용할 수 있으나 복사/상당 부분 사용 시 저작권·허가문을 보존해야 한다. 종속 라이브러리와 별도 표시된 파일의 조건은 각각 확인한다. [MIT 원문](https://opensource.org/license/mit).

RT root LICENSE 및 About/Licenses/LICENSE.txt는 **CC BY-NC-ND4.0**다. §2(a)(1)은 비상업 목적의 개작물 제작·복제를 허용하지만 개작물의 공개 공유를 허용하지 않는다. 따라서 RT 코드를 개조해 공개 WarEconomy 배포에 넣는 경로는 현재 라이선스만으로 승인하지 않는다. 별도 허가/해당 파일의 다른 적합한 라이선스가 확인돼야 한다. 비공개 비상업 PoC 개작 자체를 일률 금지라고 해석하지도 않는다. 우선 동작·개념을 참고하고 우리 계약으로 독립 구현한다. [CC 법문 §2·§3](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode.en).

단순 변수명 변경을 독립 구현으로 취급하지 않는다. 추출 시 원본 절대경로/SHA/함수·범위/저자/라이선스/변경 이유를 provenance로 기록하고 별도 adapter 경계를 둔다. 이번 분석에서는 외부 코드를 제품 소스에 복사하지 않았다.

## 3. 구현·PoC 재사용 매트릭스

다음 경로의 MP/RT 접두사는 §1의 실제 루트다. 구체 줄 번호와 SHA는 inventory의 anchors/files에 결속했다. 등급은 **추출·개조 후보**, **독립 구현 참고**, **테스트 참고**, **미채택/불충분**이며 runtime 판정이 아니다.

| 필요한 기능 / 연결 gate | 실제 코드와 관측 동작 | 재사용 판단 및 우리에게 필요한 변경 |
|---|---|---|
| 맵별 LocalClock / G-Q1 ModelB | MP `Source/Client/AsyncTime/AsyncTimeComp.cs`의 Tick/PreContext/PostContext. mapTicks·gameStartAbsTickMap·RNG·normal/rare/long TickList를 맵마다 유지하며 전역 TickManager/Rand/Faction context를 전환 | **가장 유용한 개조 후보**. 섬/LocalClock owner·쓰기 경계를 서버 lease와 연결한다. static 전역 context를 동시 스레드 격리처럼 취급하지 않는다. 순차 실행으로 divergent maps의 비간섭을 먼저 시험 |
| UI/예외 경로의 시간 읽기 | MP `AsyncTime/SetMapTime.cs`, TimeSnapshot. ticks/speed/slower/gameStartAbsTick을 저장·복구하고 MapUpdate·UI·tooltip·sound 등 호출에 Harmony 패치를 적용 | **제한된 interception surface/QA 목록 후보**. Finalizer와 Postfix 사용 차이를 확인하고 예외/중첩 호출 후 복구를 검증. 전체 getter virtualization 또는 모든 모드 호환성을 주장하지 않음 |
| Quest lifecycle·시간 의존 | MP `AsyncTime/MultiplayerAsyncQuest.cs`. QuestManager tick을 대체하고 quest parts의 mapParent로 map/world cache를 나누며 생성·accept·end·load·abandon 경로를 처리 | **G-Q1 dependency/테스트 참고**. 실제로 QuestTick을 실행하므로 Quest를 무조건 read-only projection이라고 freeze하면 안 됨. 정해진 QuestPart 타입 목록과 하나의 map을 찾는 방식은 mixed/multimap/modded Quest 전체를 해결하지 않음 |
| World W / zero-player 운영 | MP `AsyncWorldTimeComp.cs`: worldTicks/RNG는 별도지만 DesiredTimeSpeed는 가장 빠른 맵 또는 맵이 없을 때 선택 speed에서 유도 | **scheduler 그대로 미채택**. SRS§3.1/ADR006A의 Dedicated Server W, zero-player 진행, downtimeΔW0, 설정 speed를 우리의 server executor에 유지. MP World loop를 Domain World Authority로 대체하지 않음 |
| fresh RimWorld validator process / Gate05 | MP `Networking/HostUtil.cs` StartArbiter: loopback listener를 준비하고 현재 executable을 `-batchmode -nographics -arbiter -connect=...`로 Process.Start. `Common/LiteNetManager.cs` LiteNetArbiterManager는 OS 할당 port 사용 | **launcher 패턴 개조 후보**. 승인된 프로젝트 내부 licensed runtime copy의 명시 exe를 trusted operator가 시작/소유. isolated save-data/task/log/timeout/cleanup, staged input SHA, full MD128 context, actual loaded DLL/MVID/profile, operator-controlled 결과 채널을 별도로 구현 |
| Arbiter 의미·headless 범위 | MP ArbiterPatches/ArbiterWindowFix는 arbiter의 UI/render 경로를 줄임. `Source/Server/Server.cs`는 standalone server에서 arbiter unsupported를 출력 | **바로 가져다 validator 완성 불가**. Arbiter는 lockstep 비교 참가자다. 단계별 staged bytes를 fresh-load하여 census를 내는 독립 validator가 아님. 일반 server executable만으로 Verse native simulation이 생기지 않음. nographics가 모든 Unity/Def load 성공을 보장하지 않음 |
| save→load→resume / Engine semantic oracle | MP `Saving/SaveLoad.cs` SaveGameToDoc/LoadInMainThread/SaveAndReload: Scribe로 small components·World·maps를 저장하고 main thread에서 로드, faction·commands·일부 UI state를 복구 | **materializer/control fixture 후보**. 우리 checkpoint를 지원된 native loader로 재구성하는 adapter에 참고. SaveAndReload는 현 프로세스를 재사용하므로 fresh validator 증거가 아님. 실제 fresh process에서 대상 census/참조/물질 보존/재개 control 필요 |
| 맵 별 serialization / Pruned Target Context | MP SaveLoad.CreateGameDataSnapshot는 각 map XML을 MapData로 분리하고 maps node를 비운 GameData와 SessionData/MapCmds 보관. Loader.DataSnapshotToXml은 선택 맵을 다시 결합 | **구체 format/materialization 실험 후보**. 남은 World/global의 dependency closure·revision·재참조를 검증해야 함. 이 serializer 구조가 exact PlayerGlobal owner/schema 또는 .rws 물리 split 채택을 뜻하지 않음 |
| Cross-reference 생명주기 / canonical EntityId | MP `Saving/SharedCrossRefs.cs`는 native loadID directory의 맵별 Thing/PassingShip/Bill을 unregister/reregister. `Saving/CrossRefs.cs`는 load/save 참조 패치 | **참조 graph 테스트 및 adapter 후보**. native loadID는 canonical EntityId/custody/ownership epoch가 아님. 우리 durable mapping과跨경계 참조 검증을 별도 유지; WorldPawns membership만으로 custody를 추정하지 않음 |
| 맵 스트리밍·target-only 네트워크 | MP Server_MapResponse/ClientPlayingState.HandleMapResponse 및 관련 branch는 존재. **MultiplayerServer.CanUseStandaloneMapStreaming(int mapId)=>false** | **활성 작동 기능으로 미채택**. 테스트 StandaloneMapStreamingTest도 방송 유지/MapResponse 미전송을 검사. dormant scaffold와 실사용 map serialization을 구분. 이를 target-scoped canonical publication 완료로 부르지 않음 |
| UI 명령 동기화 / shared Tactical | MP `Common/ScheduledCommand.cs`, CommandHandler.Send 및 AsyncTimeComp.ExecuteCmd. 서버 tick/map/faction/player로 command를 일정에 넣고 native Designator/Sync를 실행 | **Tactical transport/command adapter 후보**. 세션 참여·작위/외교/법적 공격·lease/fencing 검증은 우리 server contract. MP의 client deterministic execution을 canonical Domain commit authority로 채택하지 않음 |
| ContentProfile coverage / Gate05 MD130 | MP MultiplayerData.CollectDefInfos/GetDefInfo는 comp·serialization type 목록 및 Vanilla Def 이름을 수집하고 count/int AggregateHash를 만듦 | **enumeration coverage 참고**. 이름/타입/count hash는 Def material fields·실제 loaded binary/settings/order·lossless/versioned content manifest가 아님. mod assembly Def 제외/ignored Vanilla 타입도 있음. 그대로 semantic fingerprint로 사용 불가 |
| RNG/desync·trace / G-Q1 QA | MP SyncCoordinator/ClientSyncOpinion/MapRandomStateData: 같은 시작 tick의 의견 비교, map/world/command RNG state 일부와 stack trace hash, round mode를 기록 | **원인 찾기 보조 계측 후보**. 우리 supported manifest/census·stable ID·custody·conservation oracle과 병행. RNG/hash 일치만으로 의미 동일성/PASS를 판정하지 않음; 관측 누락을 UNOBSERVED로 명시 |
| replay·evidence packaging | MP `Saving/Replay.cs`는 world/map save·commands·section timeline·mod 이름/ID를 ZIP에 보관 | **QA 재현 형식 참고**. 우리 run/task/result ID·binary/source/PDB SHA/MVID/loaded profile·독립 실행 proof·raw index를 추가. replay ZIP 및 mod 이름이 authority/cryptographic binding을 자동 증명하지 않음 |
| join/loading/keepalive / transport QA | MP Tests.ServerTest/Helper는 실제 local LiteNet server/client와 OS 선택 port를 구성하고 join point abort/loading keepalive를 검사. Packet/Serialization tests도 있음 | **QA harness 부품 후보**. transport reliability fixture에 이용. SQLite coordinator의 CAS/PREPARED/commit/crash/recovery/PublicationEvent durability 증거와는 다른 범위; net8 tests 성공을 native RimWorld 성공으로 승격하지 않음 |
| pause/barrier | MP FreezeManager는 host frozen state/10초 wait/host absent fallback으로 server freeze를 조절. TimeControlFallbackTest는 host absent면 non-host time command 허용을 검사 | **동작·테스트 참고만**. accepted island barrier에는 one writer·fencing·final checkpoint validate/commit·revocation·grant가 필요. HostOnly/LowestWins/fallback을 SRS peace Last Input Wins 또는 hostile control에 자동 적용하지 않음 |
| Faction.OfPlayer 전환 | MP FactionContext/FactionContextSetters: stack으로 native player faction pointer를 전환하고 맵/명령 context에 적용 | **native context adapter 후보**. 우리 FactionDomain/feudal/diplomacy는 Dedicated Server가 관리. 네이티브 Faction/Title을 WarEconomy 작위/권한과 동일시하지 않음 |
| 저장 업로드/복귀 / Together | RT PM_Saves.ReceiveSaveFromClient는 사용자 파일에 FileBytes를 기록. PM_Map은 tile·username 확인 경로 뒤 bytes를 저장 | **독립 구현 참고**. checkpoint staging/storage/owner routing UX만 참고; malicious-input admission, actual profile/fresh load/census, CAS/durable revision·canonical publication은 우리 구현. 서버가 파일을 보관한다는 사실과 최종 의미 검증을 구분 |
| 오프라인 raid/온라인 visit·동기화 | RT PM_Raid는 저장된 map을 찾아 전달; PM_Synchronous는 connected settlement owner의 승인/짝 연결·action relay를 담당 | **product flow 참고**. offline target data retrieval은 있지만 서버 trusted worker의 offline combat/outcome publication proof가 아님. Client source가 없어 native map import/전투 계산/결과 내부는 UNOBSERVED |
| 선물/무역/시장·오프라인 대금 | RT PM_Transfers는 Request/Accept/Reject/Recover의 online relay. PM_Market는 listing removal, seller payment/pending payment, response flow | **UX/state vocabulary 참고**. 우리 P2P inventory/Silver reservation, durable op-key/typed atomic or PREPARED transaction, server custody, retry/recovery는 대체 못함. 읽은 handler는 이 contract를 증명하지 않음; 의존 DLL 내부 전체 부재라고 단정하지도 않음 |
| 공유 World/정착지/Caravan/Sites/Guild | RT PM_Settlements는 tile uniqueness·owner username metadata와 broadcast, PM_Caravan은 add/remove/move relay, PM_Sites·PM_Guilds는 build/reward/membership flow | **독립 구현 참고**. SRS server W movement·territory/vision/warpending/feudal hierarchy·tax/Audit durable authority는 우리 도메인에 새로 연결. guild admin rank가 우리 Title chain/liege/tier를 구현한 것이 아님 |
| mod 일치 UX | RT PM_Mods는 ModName·settings hash·order/config policy를 비교하고 deny reason을 보냄 | **불일치 안내/설정 UI 참고**. AllowAll/admin/unenforced 조건이 있고 actual loaded-content semantic manifest가 아님. Gate05 MD130 decoder/encoder를 이 비교기로 교체하지 않음 |

## 4. 현재 PoC에 연결하는 구체 후속 순서

이 목록은 **Master 분석 backlog**다. 구현 WP를 새로 발행하거나 처리 중 A에 추가 feature 작업을 보내지 않았다.

1. **Gate05 R2 review가 우선.** 현재 A의 operator-owned validator/content 수정을 먼저 수집한다. native launcher가 실제 한계이면 HostUtil/LiteNetArbiterManager를 참고해 최소 launcher adapter 범위를 정한다. 전체 MP 모드를 Engine에 설치해서 빈틈을 가리지 않는다. 승인된 격리 runtime에서 실제 parent/child PID·exe SHA·exit·load task·loaded profile·result origin을 남긴다. genuine staged A→B→C를 fresh processes로 읽고 supported census와 MD128/129를 대조해야 한다. 기존 E2 FAIL/R1 rejection은 새 후보 PASS로 승계하지 않는다.
2. **G-Q1 bounded ModelB control.** AsyncTimeComp/TimeSnapshot에서 최소 맵 clock/RNG 전환 surface와 Quest/UI dependencies를 추출 후보로 삼는다. A-running/B-paused, 반대, 별도 tick schedule control, save/load/resume, exception/nested context restore를 같은 지원 profile에서 비교한다. 생물학·chronological age, job/path/plant/weather material effect, Quest deadline/mutator, Storyteller·WorldPawns/Tales/PlayLog 관측을 inventory로 남긴다. B가 barrier 후 정상 tick하면 동일 schedule control과 비교한다. 실패/관측 불가를 감추지 않고 ModelC 비교 조건으로 남긴다. 지금 G-Q1 OPEN 유지.
3. **target map materialization 실험.** SaveLoad/Loader/SharedCrossRefs를 작은 fixture/control adapter로 검토한다. 맵+필요 World/global 결합, DLC/Def 및 entity cross refs, dropped reference/GC, owner revision hard binding, extraction write-set 및 재개 semantics를 검사한다. null exception 부재/XML equality만 PASS로 삼지 않는다. Runtime proof 전에 exact PlayerGlobal schema/physical split을 채택하지 않는다.
4. **Tactical command/replay/transport 후속.** ScheduledCommand/Designator syncing, desync traces, replay, join/loading tests를 제품의 shared Tactical entry/resync UX로 연결한다. Command security/authority schema·server leases와 canonical publication은 우리의 accepted ADR를 유지한다. material/trade/tax/Tactical release 및 Foundation gate를 건너뛰지 않는다.
5. **Together의 World/UI flow는 별도 독립 구현 backlog.** 저장/방문/raid/trade/market/Caravan/sites/guild 흐름을 기능 체크리스트로 사용한다. 로컬 client/shared/network source 부재와 ND 조건을 먼저 해결할 때까지 직접 코드 이식 WP를 내지 않는다. feudal·diplomacy·vision·tax·NPC dynamic market는 해당 SRS/정책 OPEN 항목에 맞춰 구현한다.

각 실제 추출 WP에는 origin SHA/license notice, 최소 의존 파일, 달라지는 patch/profile, adapter write-set, candidate build/freeze 규칙, targeted regression, independent E2 기준을 포함한다. vendor compatibility/version drift는 지원 profile별로 검증한다. 이 보고서의 우선순위는 일정/진척률 추정이 아니다. ArbiterPatches 자체에도 World/Planet rendering의 작동/1.6 검증 TODO가 있어 headless 성공을 원문만으로 인증할 수 없다.

## 5. 그대로 채택하면 안 되는 주장

- “MP의 per-map clock이 있으니 G-Q1이 이미 해결됐다” → map/global/Quest/material 비간섭은 우리 profile runtime으로 검증해야 한다.
- “batchmode Arbiter니까 독립 semantic authority validator다” → MP peer opinion과 MD126~129 operator task/result admission은 역할이 다르다.
- “Def 이름 hash면 실제 content semantics가 묶인다” → MD130 material field/lossless/order/null/load origin을 누락한다.
- “map XML을 분리했으니 PlayerGlobal owner/물리 split은 확정” → loader 편의 format과 canonical owner 계약을 구분한다.
- “스트리밍 테스트 파일이 있으니 map-only streaming 작동” → 로컬 function은 false, positive runtime proof 없음.
- “Quest/Weather/Storyteller는 버려도 된다” → MP도 context/tick dependencies를 다루며 controlling C correction은 blanket discard/read-only를 거절한다.
- “Together 서버 저장이 있으니 offline authority/거래 원자성 완료” → client bytes/relay/payment handler는 우리의 custody/PREPARED/recovery gate를 증명하지 않는다.
- “MP HostOnly/host absent fallback을 그대로 쓰면 시간 정책 구현” → SRS peace/hostile/W/L 및 island fencing 규약과 대조해야 한다.
- “작동하는 모드 코드 사용으로 E1/E2가 이전된다” → 새 adapter/new binary/profile로 새 검증이 필요하다.
- “참조 모드는 모두 오픈소스라 개조 배포 가능” → 실제 RT ND 조건과 DLL-only source scope가 있다.

## 6. A 재시작과 설치 identity incident — 분석과 별도

최신 사용자 재리셋/재처리 보고와 실제 같은 R2 ACK/복구 보고서를 대조했다. dispatch `WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708`, WP/revision/recipient/IN_PROGRESS가 일치한다. 이전 possible stall attention은 reset+새 ACK로 superseded; 구현/native 실행/완료를 그 ACK로 증명하지 않는다.

Master 실제 보존 검사에서 archive19/Pipeline original+frozen206/R1 frozen147은 유지됐지만 **기존 Steam 설치 WorkerBridge DLL이 바뀌었다**. 기대 SHA `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C`, 실제 `BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61`, size110080, last-write metadata `2026-10-07T23:57:40.244423Z`. 변경 주체/원인 UNKNOWN. 해당 경로는 허용 nine Engine paths 밖이며 기존 설치 immutable 계약과 불일치한다. Master는 원본을 변경/복구하거나 baseline hash를 덮어쓰지 않았다. 관측 bytes를 프로젝트 incident 폴더에 보존했다.

근거: `coordination/MASTER_R2_RECOVERY_ACK_REVIEW_20261008.json`, `coordination/ENGINE_INSTALLED_IDENTITY_INCIDENT_20261008/`. 같은 R2에 대한 보존 확인 notice를 task에 작성했다. NOTICE의 전달 상태는 `MASTER_PRESERVATION_NOTICE_DELIVERY_20261008.json` 실제 proof로만 판단한다. 새 implementation WP가 아니다. 기존 archive E2의 역사 identity는 보존되며, 현재 설치를 old19 candidate로 취급하지 않는다. provenance/격리 runtime 실제 loaded identity를 해결하기 전 새 Engine E2 release를 하지 않는다.

Engine002/006, Pipeline007/current schema, G-Q1 OPEN / Pipeline full E2 INCONCLUSIVE / Foundation HOLD 유지. 기존 001/013 narrow CLOSED 등 역사 scope는 유지. 기존 hourly monitor의 cadence/lifecycle은 변경하지 않았다.

## 7. 검증과 남은 불확실성

실행 검증은 아직 하지 않았다. 실제 소스/테스트/라이선스/의존성·function body를 확인했고 inventory로 현재 bytes를 식별했다. WarEconomy 생산 코드나 candidate는 이 분석으로 수정·재빌드하지 않았다. 현재 production tree에서 MP/RT class-name/provenance 키워드 검색은 관련 Tactical 주석 외 직접 재사용 근거를 찾지 못했다; 이것은 이름을 바꾼 복사까지 없다는 감사 증명은 아니다.

미확정: 로컬 모드의 upstream commit/변경자, RT client/shared/network 내부 source/별도 사용 허가, 우리 runtime과 MP ref/API/Prepatcher 호환성, G-Q1 material dependency closure, native validator 실행 증거, 설치 DLL 변경 주체, reference test 실행 결과. Native/headless/runtime API/ContentProfile이 달라지면 별도 새 candidate proof가 필요하다.

## 8. 우선 검토 코드 바로가기

| 용도 | 실제 파일 |
|---|---|
| 맵 tick/context | [AsyncTimeComp.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Client/AsyncTime/AsyncTimeComp.cs:110) |
| 시간 저장·복구 | [SetMapTime.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Client/AsyncTime/SetMapTime.cs:203) |
| fresh native launcher | [HostUtil.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Client/Networking/HostUtil.cs:214) |
| listener | [LiteNetManager.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Common/LiteNetManager.cs:80) |
| snapshot 분리·조립 | [SaveLoad.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Client/Saving/SaveLoad.cs:187), [Loader.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Client/Saving/Loader.cs:83) |
| 비활성 스트리밍 | [MultiplayerServer.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Common/MultiplayerServer.cs:234) |
| 이름/count fingerprint 한계 | [MultiplayerData.cs](C:/Users/user/Desktop/RimMulti/Multiplayer-master/Multiplayer-master/Source/Client/MultiplayerData.cs:117) |
| client bytes 저장 | [PM_Saves.cs](C:/Users/user/Desktop/RimMulti/Rimworld-Together-development/Rimworld-Together-development/Source/Server/PacketManagers/PM_Saves.cs:98) |
| 시장/payment flow | [PM_Market.cs](C:/Users/user/Desktop/RimMulti/Rimworld-Together-development/Rimworld-Together-development/Source/Server/PacketManagers/PM_Market.cs:93) |
