# Architecture & QA Baseline Report

[QA REVIEW]

- Work Package: 신규 SRS 기준 독립적인 읽기 전용 Architecture / QA Baseline
- Reviewer: GPT-6.1 Sol, QA / Architecture Reviewer
- Recipient: Master — GPT-5.6 Sol
- Date: 2026-10-01 (Asia/Seoul)
- Verdict: **BLOCKED BY ARCHITECTURE**
- 의미: 기준선 조사는 완료했다. 현재 구현을 신규 SRS에 적합한 Architecture로 승인하지 않는다. 아래 기능 결함은 FAIL이며, 미확정 정책에 해당하는 작업만 BLOCKED BY REQUIREMENT다.
- Production 변경 / Commit / GUI 조작 / 운영 서버 재시작: **없음**
- 추가 파일: 이 보고서, QA 전용 실행기, 로그, 해시 매니페스트. 기능 구현을 대신하지 않았다.

## 1. 기준 문서와 증거 범위

다음 다섯 문서를 전체 읽었다. 우선순위는 사용자 지정 순서다.

| 순위 | 문서 | 검토 범위 |
|---|---|---|
| 1 | [요구사항_명세서.md](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md>) | FR-001~234, BR-001~019, NFR-001~012, CON-001~010, CFG-001~026, ER, AC, TBD |
| 2 | [요구사항_정규화.md](<C:/Users/user/Desktop/RimMulti/요구사항_정규화.md>) | 요구 정규화 및 품질 분석 전체 |
| 3 | [유스케이스_명세.md](<C:/Users/user/Desktop/RimMulti/유스케이스_명세.md>) | UC-01~24 및 공통 규칙 |
| 4 | [시나리오_기반_분석.md](<C:/Users/user/Desktop/RimMulti/시나리오_기반_분석.md>) | SCN-01~30 및 파생 Gap |
| 5 | [도메인_분석.md](<C:/Users/user/Desktop/RimMulti/도메인_분석.md>) | 실행 영역, 모델, 관계, 미확정 사항 전체 |

이 보고서의 FR / BR / NFR / CON / CFG 번호는 **최상위 SRS의 번호**다. 하위 문서는 동일 번호를 다른 의미로 사용한다. 예를 들어 영속성은 SRS NFR-006, 정규화 문서 NFR-003이다. 하위 문서의 PASS는 요구 문장의 품질 평가이며 제품 구현 통과가 아니다. 번호를 그대로 합친 Gap Matrix는 사용할 수 없다.

과거 QA-Phase2 / QA-Phase3 보고서와 테스트는 구현 이력 및 회귀 자산으로만 조사했다. 과거 Phase 승인이나 “19개/30개 테스트 통과”를 신규 SRS 승인 근거로 사용하지 않았다.

Evidence Reviewed:

- WarEconomyMod/Source 전체: 프로덕션 C# 46개와 프로젝트 3개, 총 49개 파일.
- WarEconomy.slnx, LoadFolders.xml, About.xml, 현재 1.6 배포 DLL.
- QA-Phase2 및 QA-Phase3 프로젝트 구성, 테스트 조건, 최신 및 과거 결과 로그.
- [input-manifest.json](<C:/Users/user/Desktop/RimMulti/QA-Baseline/input-manifest.json>): 프로덕션 소스/프로젝트 49개 + 공식 문서 5개 + About.xml, 총 55개 SHA-256. 테스트 실행 후 변경 0개.
- [artifact-hashes.json](<C:/Users/user/Desktop/RimMulti/QA-Baseline/artifact-hashes.json>), [review-support-hashes.json](<C:/Users/user/Desktop/RimMulti/QA-Baseline/review-support-hashes.json>).
- [baseline-build.log](<C:/Users/user/Desktop/RimMulti/QA-Baseline/baseline-build.log>), [baseline-checks.log](<C:/Users/user/Desktop/RimMulti/QA-Baseline/baseline-checks.log>).

이번에는 프로덕션 솔루션을 재빌드하지 않았다. Client 프로젝트의 PostBuild가 1.6 배포 폴더를 갱신하므로 읽기 전용 조사와 구분했다. 과거 build-round6-review.log의 0 warning / 0 error는 역사적 결과다. 이번 QA 실행기 빌드는 오류 0, 경고 2: NuGet 취약성 정보 조회 실패 NU1900이며 코드 컴파일 실패는 아니다.

배포 Client DLL과 기존 Debug Client DLL의 SHA-256이 일치하고, 배포 Common DLL과 Server Debug Common DLL도 일치한다. 이는 **파일끼리의 일치**이며 현재 소스에서 생성됐다는 재현 빌드 증명은 아니다. 이번 서버 반례 실행기는 기존 Server DLL 대신 현재 Common / Server 소스를 직접 컴파일했다.

## 2. 현재 Client / Server / Common 구조

| 영역 | 실제 구현 | 실행 및 의존성 | 재사용 검토 후보 |
|---|---|---|---|
| Common | DTO, enum, TCP 프레이밍, JSON 직렬화, 시간 상수, 시장/전쟁/세금 모델 | .NET Standard 2.0, Newtonsoft.Json 13.0.3 | 프레이밍, 기본 DTO, 시계 단위. 정책과 프로토콜 안전성은 별도 검증 필요 |
| Client | Harmony 패치, 접속/방문 창, main-thread queue, 월드 객체 보간, 시장 가격 패치, 로컬 양도 실행기 | .NET Framework 4.7.2, 실제 RimWorld Managed DLL 참조, Harmony 2.3.3 | UI 연결, 수신 디스패치, 엔진 API 조사/롤백 경험 |
| Server | TCP 세션, 고정 WorldTickManager, Diplomacy / Market / Feudal singleton 관리자, 콘솔 엔트리 | .NET 8.0, Common. RimWorld 엔진 참조 없음 | 독립 clock, 단일 socket writer, manager skeleton |
| QA | 콘솔 실행기와 엔진 경계 stub, reflection으로 private 상태 확인 | 대체로 .NET 8.0 | 패킷·실패 주입 테스트를 신규 요구에 맞춰 분리 가능 |

주요 위치:

- WarEconomyMod/Source/Client/WarEconomy.Client.csproj:4,19,42,46
- WarEconomyMod/Source/Server/WarEconomy.Server.csproj:5,17
- WarEconomyMod/Source/Common/WarEconomy.Common.csproj:4,12
- WarEconomyMod/Source/Server/Program.cs:20,28,32,56

Multiplayer-master 및 Rimworld-Together-development는 별도의 참고 소스다. WarEconomy 프로젝트 참조에 이들의 동기화 엔진은 없다. 참고 저장소에 Tactical/Save 기능이 있다는 사실을 WarEconomy의 구현 완료로 계산해서는 안 된다.

프로덕션 솔루션은 세 프로젝트만 포함하며 QA 프로젝트는 솔루션 밖에 있다. About.xml의 PackageId는 WarEconomy.HybridMultiplayer이고 1.5와 1.6을 모두 광고한다. 신규 SRS의 대상은 1.6이다. 1.5 패키지는 역사적 산출물로 구분해야 한다.

## 3. 실제 Authority Boundary

현재 상태는 **서버 중심 타이머 + 클라이언트의 독립 게임 객체 변경**이다. 인증된 도메인 권한과 공동 Tactical Authority가 완성된 구조가 아니다.

~~~mermaid
flowchart LR
    Clock["Server WorldTickManager"] --> Managers["메모리상의 War / Market / Feudal"]
    Managers --> TCP["TCP + JSON + 송신 Channel"]
    TCP --> Queue["Client MainThreadQueue"]
    Queue --> Local["각 Client의 로컬 World / Map"]
    Local --> Result["거래 보고 / 양도 Success 응답"]
    Result --> Managers
    Missing["공동 Tactical Simulation / 영속 트랜잭션 / 재고 원장 없음"]
~~~

| 상태 / 행동 | 현재 최종 변경 주체 | 서버의 실제 확인 | SRS 요구와의 차이 |
|---|---|---|---|
| WorldTick | Server clock | 프로세스 안에서 숫자 증가 | 재시작 저장 없음; 속도 고정 |
| Caravan / WorldObject tick | 각 Client | clock 숫자 전송만 | 서버에 Caravan 도메인/공통 이동 결과가 없음 |
| Map simulation | 각 Client의 RimWorld | 공동 simulation 없음 | 원격 자기 Pawn 명령/단일 Map 판정 미구현 |
| War | Server manager | 패킷의 attacker/defender 문자열 신뢰 | 인증·소속·최고 작위·cooldown 검사 없음 |
| NPC 시장 | Server manager | Client가 보고한 수량/방향을 신뢰 | 실제 거래 검증·중복 방지 없음 |
| Settlement 등록 | Server manager | sender.PlayerId와 기존 lord 문자열 비교 | PlayerId 자체를 발신자가 지정; 신규 tile/faction/title/한도 검증 없음 |
| 영지 양도 | Client가 Map 변경, Server가 ACK 후 DTO 변경 | TransferId와 실행 SessionId 일부 검사 | durable commit, save/version, 실패 복구/재접속 프로토콜 없음 |
| 방문 | Server가 요청을 라우팅, Client가 창 표시 | client HostPlayerId도 사용 | 실제 소유자 인가·동일 Map 진입·Presence UI 없음 |

근거: NetworkClient.cs:46,80,127,163,209; TcpNetworkServer.cs:121,134,163,288,296,304,312; AtomicFiefTransferExecutor.cs:37,99,135; ClientWorldTickManager.cs:71.

서버가 RimWorld 엔진을 직접 참조하지 않는 것 자체는 요구 위반이 아니다. 별도 simulation worker 등도 가능하다. 다만 현재 코드에는 어떤 방식의 오프라인 Tactical 실행 경로도 없다.

## 4. 주요 Persistent State

**WarEconomy 서버의 실제 저장/복원 구현을 찾지 못했다.** Common 객체의 JSON 네트워크 직렬화는 영속 저장이 아니다. 코드 전체에서 파일/DB 저장, checkpoint, journal, save migration, World restore, ExposeData 연동을 조사했다.

| 상태 | 현재 저장 위치 | Restart 후 보존 근거 |
|---|---|---|
| World Time | WorldTickManager._currentWorldTick | 없음. Program.Start() 기본 initialTick=0 |
| Player / 영구 인증 / Ban | session.PlayerId 문자열 | 영구 Player/Ban 저장소 자체 없음 |
| Faction / Member / Title / Feudal Tree | Tier enum 및 작은 _factionTiers dictionary; Settlement.LordTitle | 실제 Player/Faction/Tree aggregate 없음 |
| Settlement owner | FeudalManager._settlements | 메모리. startup에 고정 NPC seed 2건 |
| 양도 진행 상태 | pending / active dictionary | 메모리. 완료 journal / 복구 상태 없음 |
| War / Diplomacy | _activeWars / _factionTiers | 메모리. alliance/peace/betrayer 지속 상태 없음 |
| Tax / Delinquency | SettlementId별 _taxStates | 메모리. Player별 누적 미납 가치 없음 |
| NPC 시장 | _markets | 메모리. Client cache도 singleton 메모리 |
| Territory / Caravan / Trade orders / Inventory | 필요한 authoritative 모델 없음 | 저장할 상태 경로도 없음 |
| 실제 Pawn / Building / Item | 각 RimWorld 로컬 게임 | vanilla save와 서버 상태를 함께 확정하는 프로토콜 없음 |

관련 위치: WorldTickManager.cs:22,40; Program.cs:28,56; FeudalManager.cs:33,36,39,50; DiplomacyManager.cs:20,23; DynamicMarketManager.cs:20.

NFR-006은 FAIL이다. 서버 재시작 후 사용자 ID/소유권/전쟁/체납/시장/world time 복원이 되는 것으로 보고해서는 안 된다. 기존 local save를 다시 여는 것은 server restore 검증이 아니다.

## 5. Packet Architecture

Wire format: 2-byte ushort header + 4-byte int body length + UTF-8 JSON. BitConverter로 현재 호스트 byte order를 사용한다. 수신기는 TCP 분할/결합을 조립하며 body 상한은 10 MiB다.

- PacketSerializer.cs:9 — TypeNameHandling.Auto, 명시적 type allowlist binder 없음. 악성 type metadata 검증 필요. 이 조사에서는 임의 코드 실행 가능성을 실증하지 않았다.
- PacketReceiver.cs:19,50 — frame 조립 및 크기 검사. 잘못된 크기는 buffer reset하며 접속 종료/표준 오류 응답은 없다.
- ServerClientSession.cs:28,35 — Reliable unbounded Channel, tick bounded 64 / DropOldest.
- ServerClientSession.cs:99 — 4096개 이상 상태가 500회 초과되면 연결 종료. 이는 영속 delivery 보장이 아니다.
- ServerClientSession.cs:132,200 — 단일 송신 루프, write timeout 5초.
- NetworkClient.cs:127 — Client 송신은 동기 NetworkStream.Write. async 송신 queue/timeout/동시 쓰기 직렬화가 없다.
- MainThreadQueue.cs:19,34 — unbounded action queue, 한 action 종료 후 8ms budget 확인. 큰 action 자체의 정지는 제한하지 않는다.

구현된 주요 라우팅: handshake, settlement register/list, visit request/cancel/response, war request/update, NPC trade report/market sync, tax submit/delinquency, fief offer/execute/result.

선언만 있거나 실제 기능 경로가 없는 항목:

| 선언 | 확인 결과 |
|---|---|
| TacticalInstanceCreate/Join/Leave/LockstepCommand | header enum만 있음. 구현 packet/session/handler 없음 |
| P2PTradeOffer | header만 있음. 실제 inventory 거래 없음 |
| AllianceAction | DTO 있으나 server handler 없음 |
| FogOfWarSync | DTO와 client 적용은 있음. server Vision 생성/송신 경로 없음 |
| TaxCaravanDispatch | DTO와 manager 메서드 있으나 TCP dispatch handler 없음 |
| BetrayalNotification | manager 이벤트 DTO가 있으나 intent 탐지 호출/정치 상태 변경 없음 |
| Disconnect | enum 선언, 실제 종료는 socket/CTS |

프로토콜 버전 협상, 인증 완료 gating, 공통 command ID/ACK, 완료 결과 캐시, world/session epoch, object version, snapshot sequence, replay/reconnect 복구가 없다. TCP는 연결 내부 byte 순서를 제공하지만, 재접속·중복 요청·서버 재시작·manager 동시 실행의 비즈니스 무결성을 대신하지 못한다.

중요한 교정: 서버 simulation 목표는 180 TPS이지만 **PKT_WorldTickSync의 실제 생성 빈도는 약 1 Hz**다(WorldTickManager.cs:32,84). 과거 “초당 180개 tick packet 수신”은 신규 SRS의 승인 기준이 아니다. 100,000 tick flood는 synthetic queue stress다.

## 6. 기존 Tactical / Visit 구현

현재 구현된 것은 기즈모 및 승인/거절/취소 메시지 프로토콜이다.

- VisitPatches.cs:23은 기존 Gizmo 열거를 보존하고 새 Command_Action을 추가한다.
- VisitPatches.cs:34는 비플레이어 settlement + 연결 여부만 검사한다. Owner Presence, WarPending, Caravan 실제 도착, 요청 가능한 Caravan 소유권을 검사하지 않는다.
- 요청 CaravanId는 기본 빈 문자열이다(VisitPatches.cs:48; VisitRequestData.cs:34).
- TcpNetworkServer.cs:170은 요청자가 HostPlayerId를 넣으면 서버 owner 조회를 건너뛴다.
- known owner offline의 일반 경로는 서버 거절한다. owner 없는/등록되지 않은 대상은 NPC로 추정하여 자동 승인한다. 실제 NPC 판별은 없다.
- Dialog_VisitWait.cs:88은 승인 메시지만 출력하며, :89에 추후 Map loading 연동 주석이 있다.
- Dialog_VisitRequest / Wait는 각각 static _currentInstance 하나만 추적한다. 여러 요청 창은 WindowStack에 존재할 수 있어도 취소/응답은 최신 창만 찾는다.
- ClientWorldTickManager.CurrentCombatMode는 enum/property와 speed guard에만 쓰인다. 실제 session 상태 전이로 설정하는 호출은 없다.
- request expire tick/Expired enum은 있으나 server timeout 처리 경로는 없다.

따라서 FR-098~107, BR-009~010의 공동 Tactical / remote control은 미구현이다. 창이 닫히고 “진입합니다” 메시지가 나온 것을 맵 진입 성공으로 보고하면 안 된다.

## 7. 기존 Territory / Transfer 구현

### Territory

실제 기능은 타 세력 정착지 중심의 고정 2-hop 정착 금지 검사다.

- SettlementData.cs:20 BorderRadius=2 상수.
- FogOfWarPatches.cs:169,201은 layer 존재/상한 검사 후 같은 layer의 이웃 그래프를 2-hop 탐색한다.
- :244는 다른 Faction을 일괄 enemy로 취급하며 server 목록 또는 local vanilla settlement를 검사한다.
- :304 정착 Prefix는 연결되지 않은 게임에서도 실행된다.
- server 전체 목록은 client의 KnownSettlements 목록만 갱신한다(NetworkClient.cs:200). 원격 Settlement WorldObject / 공개 Tier / Faction Border renderer를 생성하지 않는다.
- server territory tile ownership / claim priority / connectivity / title territory / destruction 이벤트 모델이 없다.
- 고정 seed tile 150/220은 실제 공유 World seed/위치와 검증되지 않았다.

2-hop BFS 구현 자체가 있다는 사실은 FR-053~068 Territory 시스템이 구현됐다는 의미가 아니다. 서버 목록의 layer 보존은 유용하지만 고정 반경/순수 client 검사는 신규 정책으로 재사용 여부를 심사해야 한다.

### Transfer

흐름: owner offer → server pending → client Execute → result → server SettlementData.TransferOwnership.

기존 개선점은 보존 가능한 회귀 자산이다: collection snapshot, SetFaction 전에 rollback 대상 등록, TransferId/SessionId 검사, 실패 rollback, claim 최종 상태 비교, 불완전 복구 경고.

그러나 다음 경계가 빠져 있다.

- 맵 식별은 int TileId만 사용. SettlementId와 LayerId를 확인하지 않는다.
- 대상은 oldFaction 소속 spawned pawn 및 CanHaveFaction=true인 oldFaction thing이다. 모든 관련 Item/holder/비spawn pawn과 Player 소유권 이전을 대표하지 않는다.
- PreviousLordPlayerId / NewLordPlayerId를 엔진 소유권 검증/변경에 사용하지 않는다. 같은 Faction의 다른 Player 간 양도는 Faction 변경만으로 표현할 수 없다.
- Client는 save 확정 전에 성공 통보하며 SendPacket은 void / 연결 종료 시 조용히 return할 수 있다.
- Server는 success boolean을 신뢰하고 owner DTO만 확정한다. Entity manifest/save hash/version 검증 없음.
- pending timeout / disconnect rollback / restart recovery / 완료 ID 기록 없음.
- 불완전 rollback 상태는 문자열 경고로만 전달되고 서버에서 일반 실패 처리한다. 자동 resync/quarantine/recovery 없음.
- Conquest, Faction Join, Demotion, Expulsion, Feudal Split과 결합한 transaction은 없다.

## 8. Requirement Compliance / 새 SRS와의 충돌

이는 첫 기준선의 그룹별 판정이다. 개별 FR 전체의 최종 SATISFIED Matrix는 Gemini 제출물과 대조할 때 작성한다. PARTIAL은 전체 Work Package의 CONDITIONAL PASS를 의미하지 않는다.

| SRS Requirement | 판정 | 현재 근거 / 부족한 증거 |
|---|---|---|
| FR-001 | PASS — 제한된 sanity | 실제 current-source WorldTickManager가 0 client에서 tick 38까지 진행. 장시간 성능 검증은 아님 |
| FR-002~003, CON-009 | PARTIAL | world object tick 분리만 있음. local calendar 및 offline lifecycle/동기화 저장 검증 없음 |
| FR-004~010 | FAIL | nickname/client ID 신뢰, version 미검증, 영구 Player/개인 Tribe 생성 없음 |
| FR-011~020, CFG-002~005 | FAIL | enum/score helper만 있음. color lifecycle, server 평가, 연결영토/봉건 조건, grace state 없음 |
| FR-021~052, BR-001~005 | FAIL | Faction/Player/Tree aggregate, 가입/작위/강등/제명 원자성 없음 |
| FR-053~068, BR-006 | FAIL | 고정 2-hop client 정착 차단. server border/priority/연결성/title territory 없음 |
| FR-069~070, BR-007 | FAIL | 시야 밖 Settlement Draw 차단; 목록 cache만으로 공개 WorldObject 갱신 안 됨 |
| FR-071~089 | FAIL | server strategic vision/scout/ambush/detection/sharing 없음 |
| FR-090~094 | PARTIAL | 요청 UI/순차 취소는 있으나 host 위조, 경쟁/중복/다중 창 문제 |
| FR-095~097 | FAIL | 일반 server offline 거절만 일부 구현. 위조 host 우회 및 disabled/tooltip 없음 |
| FR-098~107, BR-009~010 | FAIL | Map 입장/remote own-Pawn/공동 session 상태/last-input 속도 구현 없음 |
| FR-108~119, BR-011 | FAIL | 최고 작위 검증 없음, 준비시간 defender tier 사용, pending attack/퇴거/cooldown 없음 |
| FR-120~132, BR-012 | FAIL | betrayal notification 메서드만 있음. intent/관계/표시/기간/용서 상태 없음 |
| FR-133~151, BR-013 | FAIL | alliance handler/1-hop participants/peace obligations 없음 |
| FR-152~162, CON-010 | FAIL / BLOCKED BY ARCHITECTURE | online/offline 공동 실제 Map 전투, AI 인수, 결과 영속화 없음 |
| FR-163~179, NFR-001~002/005 | FAIL | victory/occupy/destroy/ruins/split 없음. transfer의 scope와 durable atomicity 부족 |
| FR-180~196, BR-015~018 | FAIL | 정책/직속 tree/actual collection 없음. 자동 deadline 체납은 명시적 충돌 |
| FR-197~212, BR-019 | FAIL / BLOCKED BY ARCHITECTURE | actual offline inventory, auto shop order/ledger/save reconciliation 없음 |
| FR-213~219 | PARTIAL | server market lock/clone/broadcast/decay 있음. 인증/실거래/초기 sync/공식/config/restock 검증 부족 |
| FR-220~229 | FAIL | 접속/방문 UI 및 몇 개 message만 존재. 통합 UI/오프라인 사건 letter 없음 |
| FR-230~234, NFR-012 | FAIL | 콘솔 quit/exit/status만 있음. kick/ban/영속 audit 없음 |
| CFG-001~026, NFR-003 | FAIL | 설정 loader/validation 없음; 숫자가 상수로 분산 |
| NFR-004~007 | FAIL | 인메모리 상태 + 신뢰 입력 + client ACK로 확정. durable consistency 없음 |
| NFR-008 | PARTIAL | 세션 catch/disconnect 및 tick-system exception isolation 있음. 운영 shutdown/resource flood까지 통과한 것은 아님 |
| NFR-009~010 | PARTIAL | 일부 vanilla UI 사용. 완성된 관리 UI/사용성 검증 없음 |
| NFR-011 | 미측정 | 실제 Remote Tactical 실행 경로가 없어 latency 목표/결과를 주장할 수 없음 |

## 9. Defects — Gemini가 재현하고 수정할 구체적 항목

각 Location은 프로젝트 루트 기준이며 현재 해시 기준 line이다. 테스트로 재현한 항목은 BASE 번호, 그 외는 정적 증거라고 명시했다. 아래 권고는 구현 지시가 아닌 검증자의 요구 충족 조건이다.

### QA-001 — 인증되지 않은 identity로 서버 권한 우회

- Severity: **Critical**
- Requirement: FR-004~007, BR-011, NFR-007, ER-004~005
- Location: Server/Network/TcpNetworkServer.cs:121,125,134,288,296,304; Client/UI/Dialog_ConnectServer.cs:129
- Reproduction: BASE-04는 handshake 없이 WarDeclarationRequest 전송. BASE-05는 victim PlayerId 및 INCOMPATIBLE-VERSION으로 handshake 후 기존 victim settlement metadata 수정.
- Expected: 인증/호환성 검증 전 상태 변경 금지; player/faction/title 권한을 서버가 확인.
- Actual: PlayerId='' 세션이 전쟁을 생성. 타인 ID와 비호환 version이 허용되고 이름/타일 수정 성공.
- Root Cause: 인증 상태 없이 self-declared identity를 권한의 근거로 사용.
- Required Fix: 영구 identity 인증 및 immutable session binding, 버전 gating, command별 서버 도메인 인가. nickname 변경은 권한 변경과 분리. 같은 identity의 복수 session 정책도 필요.

### QA-002 — 서버 상태 영속 저장/복원 없음

- Severity: **Critical** — 서버 재시작 시 공유 상태 소실
- Requirement: NFR-006, FR-004, FR-233, AC-015
- Location: Server/Program.cs:20,28,56; Server/Time/WorldTickManager.cs:22,40; Server/Managers/*의 in-memory dictionary
- Reproduction: 정적 확인. 상태 변경 후 프로세스를 다시 시작하면 신규 manager와 tick=0으로 시작하는 경로뿐이다. 운영 서버를 실제 재시작하지 않았다.
- Expected: SRS NFR-006 목록의 상태 및 진행 중 transaction을 복구.
- Actual: restore/save 호출 및 저장소 없음. 기본 NPC seed만 재생성.
- Root Cause: 네트워크 DTO와 런타임 manager를 durable state로 오인할 여지가 있음.
- Required Fix: save schema/version, 원자적 checkpoint/journal, recovery 및 재시작 검증 계획. 저장 기술은 Master의 ADR 대상.

### QA-003 — 소유권 양도의 Client 변경과 Server 확정이 원자적이지 않음

- Severity: **Critical**
- Requirement: NFR-002/004/005/007, FR-166, ER-010, AC-013
- Location: Client/Fief/AtomicFiefTransferExecutor.cs:99,120,135; Client/Networking/NetworkClient.cs:127,129; Server/Managers/FeudalManager.cs:262,274
- Reproduction: 정적 실패 경로. client entity 변경 후 result 전송 전에 disconnect/crash 또는 save 실패. 반대로 server commit 후 client의 이전 save 재로드.
- Expected: 모든 참여 상태가 하나의 durable 결과로 수렴하고 retry/reconnect에도 한번만 적용.
- Actual: client는 전송/저장 확인 없이 true 반환; server는 ACK 부재 시 pending 유지 또는 메모리 owner만 변경. recovery 없음.
- Root Cause: 로컬 try/catch rollback을 분산 transaction의 완료로 취급.
- Required Fix: durable prepare/commit/result 상태, fencing/version 및 idempotent 재적용/조회. 프로세스 crash cut point별 save/server/entity 대조.

### QA-004 — 전체 Entity 및 Player 소유권 이전 범위 부족

- Severity: **Critical** — Ownership Corruption 가능
- Requirement: FR-166, NFR-002/005, UC-05
- Location: Client/Fief/AtomicFiefTransferExecutor.cs:37,68,104,105; Common/Packets/Feudal/PKT_FiefTransfer.cs:41
- Reproduction: 정적. 비spawn/holder 안의 pawn/item, CanHaveFaction=false인 자원, 같은 faction 내 다른 Player 사이 양도, surface/다른 layer의 같은 tileId를 포함한 map.
- Expected: 관련 entity만 빠짐없이 새 Player에게 이전; 방문자/다른 구성원 보호; 정확한 settlement/layer 지정.
- Actual: spawned + faction filter 및 SetFaction만 수행. NewLordPlayerId는 소유권 변경에 쓰이지 않음. packet에 LayerId 없음; map은 TileId만 조회.
- Root Cause: Faction 동일성을 Player ownership의 대리값으로 사용하고 map entity graph 대신 일부 목록만 처리.
- Required Fix: 안정적인 world/settlement/layer/entity ID, Player ownership 모델과 complete manifest, holder/reference scope 정의, 모든 관련 entity 불변식 테스트.

### QA-005 — TransferId 충돌로 다른 영지 pending 덮어쓰기

- Severity: **High**
- Requirement: NFR-004/005, ER-002
- Location: Server/Managers/FeudalManager.cs:183,198,199,245,267
- Reproduction: BASE-03. first/second 영지에 같은 ID로 offer 후 각각 성공 ACK.
- Expected: collision/replay를 거부하거나 원 요청의 결과 반환; 서로 다른 transaction 보존.
- Actual: second pending이 first를 덮어씀. first ACK는 settlement mismatch로 무시, second만 확정되고 first의 active mapping 잔존.
- Root Cause: settlement별 lock은 있지만 global transfer ID의 유일성/내용 일치/완료 상태 검증 없음.
- Required Fix: 서버가 transaction identity를 확정하거나 client key를 authenticated owner/내용과 bind하고 원자적 삽입/완료 기록. replay after completion/restart도 검사.

### QA-006 — WarPending이 방어자 Tier를 사용

- Severity: **High**
- Requirement: FR-110~111
- Location: Server/Managers/DiplomacyManager.cs:43; Common/Models/WarDeclarationData.cs:36,39
- Reproduction: BASE-01. attacker Empire, defender Tribe.
- Expected: 공격자 Tier의 configured pending 적용.
- Actual: defender Tribe로 즉시 Active, prepTicks=0.
- Root Cause: 과거 defender 기준 모델/필드/헬퍼가 유지됨.
- Required Fix: 공격자 Tier 기준의 서버 설정 적용 및 비대칭 pair 테스트. 시간 단위 정책도 명시해야 함; 현재 helper는 hours를 현실시간 648000 ticks/hour로 환산한다.

### QA-007 — 실제 징수 없이 체납, Settlement별 관리 및 boolean 납부 신뢰

- Severity: **High**
- Requirement: FR-180~196, BR-015~018
- Location: Server/Managers/FeudalManager.cs:33,117,139,290; Common/Models/TaxDelinquencyState.cs:21,32; Server/Network/TcpNetworkServer.cs:304
- Reproduction: BASE-02. dispatch만 하고 arrival/collection 없이 tick 180000.
- Expected: 체납 없음. actual collection 부족분을 Player별 가치로 기록; 직접 봉신/collector/재고 검증.
- Actual: 자동 Delinquent. PaidResources와 실제 재고를 검증하지 않고 IsPaid로 완납/체납 변경.
- Root Cause: due-date/납세자의 boolean 모델이 SRS의 물리적 징수 모델과 다름.
- Required Fix: actual collection transaction, Player delinquent value, 직접 관계 및 caravan arrival 검증. 부분 납부 LastCollection은 TBD-05 결정 후 적용.

### QA-008 — 임의 HostPlayerId로 방문 Owner 인가 및 Offline 거절 우회

- Severity: **High**
- Requirement: FR-091/095, NFR-007
- Location: Server/Network/TcpNetworkServer.cs:170,172,186,192
- Reproduction: BASE-06. 실제 owner는 offline이지만 caller가 online unrelated host를 지정.
- Expected: 서버 등록 owner가 유일한 승인 주체; offline이면 요청 거절.
- Actual: unrelated session에 VisitRequest 전달.
- Root Cause: server-authoritative owner보다 packet의 host를 우선.
- Required Fix: target settlement를 검증하고 host를 항상 authoritative owner에서 도출; 실제 caravan/visitor/faction 도메인 권한 검사.

### QA-009 — 취소/승인 및 중복 요청의 원자적 terminal transition 없음

- Severity: **High**
- Requirement: FR-092~094, ER-001
- Location: Server/Network/TcpNetworkServer.cs:192,227,236,258,268,274,279
- Reproduction: 정적 경쟁 반례. response thread가 Pending 검사한 직후 cancel thread가 remove/Cancelled; response가 Accepted로 덮어쓰고 승인 송신. 같은 RequestId로 새 요청 덮어쓰기/늦은 응답도 가능.
- Expected: 하나의 terminal winner만 확정; cancel 완료 후 accept 불가; ID 재사용/내용 충돌 안전 거부.
- Actual: dictionary 개별 메서드만 concurrent-safe. read/status/write/send/remove 전체는 비원자적이다.
- Root Cause: mutable VisitRequestData 상태 전이에 CAS/lock/serial executor 없음.
- Required Fix: authenticated request registry와 원자적 transition 및 완료/tombstone/version 관리. 강제 interleaving으로 검증할 것; 순차 sleep 테스트만으로 통과 불가.

### QA-010 — 새 SRS에 반하는 Settlement 은폐 및 고정 국경 정책

- Severity: **High**
- Requirement: FR-053~074, BR-006~007, CFG-006~007
- Location: Client/Patches/FogOfWarPatches.cs:29,97,109,115,244,304; Client/Patches/LetterPatches.cs:33; Common/Models/SettlementData.cs:20
- Reproduction: 정적. 타 faction settlement의 tile이 default Unexplored 또는 History. 또는 Tier/config/외교가 다른 영토/국경 사례.
- Expected: Settlement 공개 정보를 vision과 무관하게 표시; 서버의 Tier별 border, 선점 priority와 연결성 반영.
- Actual: 모든 nonplayer WorldObject.Draw 차단 및 카메라 jump 차단. 국경은 다른 faction 중심 2-hop로 고정.
- Root Cause: 역사적 Fog/알박기 정책을 신규 Strategic Vision/Territory와 동일시.
- Required Fix: 공개 Settlement와 은폐 Caravan을 분리하고 server Territory 및 Presence/View 모델을 설계. 참고용 old Fog 렌더링 전체를 자동 재사용하지 말 것.

### QA-011 — 재접속 때 이전 프레임/메인 스레드 작업의 세션 경계 없음

- Severity: **High**
- Requirement: NFR-004/007; 재접속 regression
- Location: Client/Networking/NetworkClient.cs:39,112,163,167,186; Client/Threading/MainThreadQueue.cs:19
- Reproduction: BASE-07은 partial old frame 뒤 같은 PacketReceiver에 new-session tick frame을 넣는 최소 실험. 별도로 enqueue 후 disconnect/reconnect하고 queue 처리하면 old action이 실행될 수 있음(정적).
- Expected: connection별 receiver 및 적용 시점 epoch 검사. 이전 세션의 데이터가 새 world에 적용되지 않음.
- Actual: fresh parser는 WorldTickSync 1건, reused parser는 Handshake 1건으로 오조립. queued action은 sessionId를 저장/검사하지 않음.
- Root Cause: receive loop 입구의 SessionId 가드만 있고 parser 및 callback 적용 수명주기는 공유됨.
- Required Fix: receiver/stream/CTS를 세션 객체로 묶고 dispatch 시 epoch 검사. cache/world lifecycle reset과 연결 재시도 경쟁도 검증.

### QA-012 — 불완전 Rollback을 durable 복구 대상 상태로 보존하지 않음

- Severity: **Critical** — 이미 발생한 부분 복구 실패 상태를 방치
- Requirement: NFR-002/004/005, ER-010
- Location: Client/Fief/AtomicFiefTransferExecutor.cs:143,159,212,254,315,423,504; Server/Managers/FeudalManager.cs:262,279
- Reproduction: 정적. reverse SetFaction 실패 또는 claim 복원 실패로 Incomplete rollback 결과 전송. null snapshot 값이 callback에서 새 claim으로 바뀌거나 thing이 파괴되는 경우도 포함.
- Expected: 불완전 상태를 명확히 보존하고 새 변경을 막은 뒤 durable 이전 상태 복원/검증. 정상 복구로 오판정하지 않음.
- Actual: client는 경고 문자열; server는 pending 제거 후 former owner 유지 로그뿐. null claim/Area/Master는 복원 검사를 건너뛰고, destroyed transferred thing은 최종 검증에서 제외.
- Root Cause: 복구 실패 reporting과 실제 repair 프로토콜이 분리되어 있지 않음. snapshot equality가 일부 non-null/live object만 검사.
- Required Fix: typed repair-needed 상태, recovery checkpoint/manifest 및 제한된 변경 허용 정책. null↔non-null, tracker 소실, destruction, save 실패도 최종 상태 oracle에 포함.
- Note: 이전 테스트는 일부 오류를 경고로 표시함을 증명한다. 원자성 요구를 만족하는 복구 완료 증거는 아니다.

### QA-013 — NPC 거래 보고를 중복/위조/비정상 수량과 함께 신뢰

- Severity: **High**
- Requirement: FR-213~219, NFR-004/007
- Location: Server/Network/TcpNetworkServer.cs:296; Server/Managers/DynamicMarketManager.cs:33; Common/Models/DynamicMarketState.cs:46,72
- Reproduction: 정적. 같은 report 반복, 거래 없이 수량 보고, negative/overflow 수량, 임의 settlement/def 입력.
- Expected: 유효한 거래만 market에 한번 반영; inventory/event 기준 검증 및 invalid 수량 거부.
- Actual: report.Count로 재고/가격 변경. transaction ID 없음. 구매/매도 lock은 허위/중복 command를 막지 않음.
- Root Cause: 사후 client 보고를 authoritative transaction으로 사용.
- Required Fix: 거래 identity/증거 및 수량/domain 검증, replay 방지, server 계산 결과 사용. underscore string key collision도 composite key 검증에 포함.

### QA-014 — 여러 방문 다이얼로그의 수명주기를 최신 1건만 추적

- Severity: **Medium**
- Requirement: FR-091~094, NFR-009
- Location: Client/UI/Dialog_VisitRequest.cs:17,26,39; Client/UI/Dialog_VisitWait.cs:17,26,74
- Reproduction: 정적. 같은 owner에게 두 요청 창을 표시한 후 첫 요청 취소/응답. 최신 창과 ID가 달라 첫 창 정리 누락.
- Expected: RequestId마다 맞는 창 상태 갱신/종료.
- Actual: static 1개 참조만 검색. 남은 WindowStack 창의 stale accept 입력 가능.
- Root Cause: 요청 registry 대신 singleton window reference.
- Required Fix: RequestId 기반 UI registry 및 disconnect/expiry/terminal status 정리. 복수 caravan/request 정책은 Master가 정한 모델에 맞출 것.

## 10. Critical Architecture Risk / Architecture Concerns

| 위험 | 판정 | 부족한 Architecture / 검증 Gate |
|---|---|---|
| RISK-01 Offline Combat Authority | **BLOCKED BY ARCHITECTURE / Critical** | owner offline에서 기존 map load, authoritative simulation + AI, 공격 결과 durable save, 재로그인 반영. 단순 offline 공격 거절은 요구 변경이므로 대안이 아님 |
| RISK-02 Remote Tactical Session | **BLOCKED BY ARCHITECTURE** | session authority, own-Pawn command validation, replication/snapshot, speed state, join/reconnect/handoff. header enum이나 Dialog로 통과 불가 |
| RISK-03 Offline Inventory | **BLOCKED BY ARCHITECTURE / Critical integrity risk** | item identity/actual stock/silver, save revision, escrow 대신 실제 즉시 반영, concurrent trade/tax, stale save replay 방어 |
| RISK-04 Atomic Ownership Transfer | **FAIL / Critical** | complete ownership scope, cross-process durable commit/recovery, same-faction Player transfer, unfinished repair 관리 |
| RISK-05 Betrayal Intent | **미구현, High requirement risk** | command intended target ↔ actual damage 증거, legitimate attack/pending state, faction-wide result. AoE fallback은 SRS CON-001 허용 범위에서만 |

추가 Architecture Concerns:

- ConcurrentDictionary는 내부 mutable 객체의 multi-field transaction을 보호하지 않는다. SettlementData.TransferOwnership은 lord/title/faction을 순차 변경하고 GetAllSettlements는 같은 객체 참조를 반환한다. 등록과 ACK commit도 같은 settlement version/lock으로 묶이지 않았다.
- singleton manager와 local engine global 상태가 테스트 격리/World 교체를 어렵게 한다. server domain 실행 순서 및 transaction 단위 serialization 전략이 필요하다.
- unreliable tick을 drop하는 것은 현재 clock snapshot엔 가능하다. future combat command / inventory / entity event에 같은 정책을 적용하면 안 된다.
- unbounded Reliable queue는 연결 단절 후 전달, ACK, restart 복원을 보장하지 않는다. queue count 기준은 byte memory cap과 동일하지 않다.
- server count는 TryWrite 후 increment, reader는 dequeue 시 decrement하므로 순간 음수 및 disconnect reset과 경합 가능. 현재 2,100건 성공만으로 flow-control oracle을 승인하지 않는다.
- main-thread queue 8ms는 action 비용 상한이 아니다. 동기 Client SendPacket 및 large transfer는 실제 프레임 정지 위험이 있다.
- cache를 실제 공유 World와 연결하는 server world seed/world identity 모델이 없다. 각 vanilla save의 GetUniqueLoadID를 global server ID로 사용할 수 있는지 검증해야 한다.
- dormant helper CanRevokeOrExpel(superior>subordinate)는 Duke→Baron을 허용하며 SRS BR-004의 King+와 충돌한다(NobilityTitle.cs:25). CanLevyTaxes의 Count+ 제한도 direct-vassal 규칙을 대표하지 않는다. 현재 호출 경로는 없으므로 즉시 공격 가능한 endpoint로 보고하지 않지만 재사용 전 수정/폐기 판단이 필요하다.
- NPC price는 현재 polynomial/선형 증가·감소와 고정 상수이며 SRS의 지수적 quantity 기반 공식/config를 그대로 충족했다고 할 수 없다. bid/ask에 하나의 multiplier를 적용하는 구조와 vanilla restock 상태 관계도 검증해야 한다.
- 접속/서버 변경 시 market 및 fog singleton cache 초기화 경로가 없다. 이전 서버 정보로 가격/시야를 판단할 regression 가능.
- About 설명의 “과거 관측 흑백 렌더링”, 고정3x 등은 actual implementation/new SRS 검증 없이 제품 기능 사실로 사용할 수 없다.

## 11. 현재 Automated Test 구조와 Test Review

| 자산 | 실제 검증 | 한계 |
|---|---|---|
| QA-Phase2/Program.cs | tick 100k + Reliable 2100 생성 후 queue와 socket drain, ID 집합/헤더별 700건 | **송신 루프를 시작하기 전에 enqueue**. live producer/drain 동시 과부하와 전체 server routing 테스트가 아님. private Channel _items reflection 의존 |
| Checks / Round2 / R3Independent / R4Independent / R5Independent | 과거 결함 재현 및 일부 regression | REPRO_PASS는 결함 존재 성공. 고친 소스에서 old assertion이 실패해도 제품 회귀와 구분 필요 |
| Round3 / Round4 / Round5Checks | pending owner, ACK ID, owner overwrite, cancel authorization, rollback 관련 좁은 조건 | 매번 새 manager/일부 singleton. replay/crash/save/restart/authority 전체 요구 검증 없음 |
| R6Independent | property-shaped Area/Master restore 예외, 오류 UI/result serialization | original client executor + engine stub. real callbacks/holder graph/save 미검증 |
| engine IL inspection | 실제 설치 엔진 API 형태/claim 함수 조사 | 실제 map를 simulation/save/load하고 invariant를 대조하는 integration test와 다름 |

참조 구성은 대부분 기존 Server/Debug DLL을 HintPath로 사용하고 client executor/dialog source를 링크한다. 따라서 소스 변경 없이 오래된 DLL로 테스트될 가능성을 항상 해시/빌드 manifest로 확인해야 한다. 이번 독립 실행기는 Common / Server 소스를 직접 컴파일하여 이 문제를 줄였다.

과거 latest 로그는 Round5Checks 30 CHECK PASS, R6Independent 12 CHECK PASS를 포함하지만 **이번 턴 재실행 결과가 아니다**. 실제 Engine integration 및 신규 SRS 전체 통과는 주장하지 않는다.

현재 테스트에 신규 SRS ID와 invariant matrix가 없다. “19개 통과”나 “100%”는 포함된 assertion의 범위일 뿐 누락된 requirement coverage를 뜻하지 않는다. NoData의 300ms 검사도 thread scheduling race의 완전한 증거가 아니다.

### 이번 독립 terminal 실행

실행기: [BaselineChecks/Program.cs](<C:/Users/user/Desktop/RimMulti/QA-Baseline/BaselineChecks/Program.cs>)
프로젝트: [BaselineChecks/BaselineChecks.csproj](<C:/Users/user/Desktop/RimMulti/QA-Baseline/BaselineChecks/BaselineChecks.csproj>)

현재 Common와 Server managers/network/time 소스를 직접 링크했다. production Program entry point는 실행하지 않고 CurrentTick=100으로만 대체했다. 실제 TCP loopback 쌍은 ephemeral port로 만들며 private handler에 프레임 body를 전달한다. 운영 7777 서버, 사용자 save, GUI는 사용하지 않는다. loopback pair/clock은 finally/Stop으로 정리했다.

| Case | 관측값 | 제품 판정 |
|---|---|---|
| BASE-01 | Empire 공격자/Tribe 방어자 → Active, prepTicks=0 | FR-110 FAIL |
| BASE-02 | 도착/징수 없음 → tick180000 Delinquent, count1 | BR-018 / FR-192 FAIL |
| BASE-03 | 동일 transfer ID → first old owner+잔존 active, second new owner | transaction isolation FAIL |
| BASE-04 | PlayerId 빈 세션 → 전쟁 생성 1건 | BR-011 / authority FAIL |
| BASE-05 | 타인 PlayerId + 비호환 version → victim metadata 수정 성공 | identity/version gate FAIL |
| BASE-06 | offline actual owner → unrelated client host queue에 요청 | visit owner/offline gate FAIL |
| BASE-07 | old partial frame + 새 frame → WorldTickSync 대신 Handshake 조립 | receiver lifecycle FAIL |
| Clock sanity | 0 client, 약 200ms → world tick38 | FR-001의 기본 진행 확인 |

**7/7은 일곱 결함 반례를 확인했다는 의미다.** 제품 PASS가 아니다. 재현되지 않은 Unity/실제 저장/실전 동시성은 정적 분석 또는 미검증으로 남겼다.

재실행 명령(프로젝트 루트):

~~~powershell
dotnet build .\QA-Baseline\BaselineChecks\BaselineChecks.csproj --ignore-failed-sources
dotnet .\QA-Baseline\BaselineChecks\bin\Debug\net8.0\BaselineChecks.dll
~~~

## 12. 앞으로 QA에 필요한 Test Harness

모든 harness는 Requirement ID, 독립 oracle, deterministic seed/virtual clock, source+binary+save manifest, 실패시 exit code, 실행 trace를 갖춰야 한다. 다음은 설계 검토용 요구이며 이번에 Production 구현을 추가하지 않았다.

| Harness | 핵심 검증 | 연결 Requirement |
|---|---|---|
| Authentication / Protocol adversarial | pre-auth command, 위조 ID/faction/title, incompatible version, re-handshake, 같은 ID의 reconnect/복수 session | FR-004~007, BR-011, NFR-007 |
| Transport & Command replay | TCP split/coalesce, corrupt length/JSON, duplicate application command, handler order, session epoch, late old callback, slow client | NFR-004/007/008, ER-001~002 |
| Virtual World Clock / Config | zero-client tick, server restart monotonicity, pending/cooldown/grace/decay boundary, bad configuration | FR-001, CFG, NFR-003/006 |
| Process Save / Restart oracle | crash 전후 canonical server state, journal/checkpoint partial write, IO exception/disk full, schema version restore | NFR-006/012 |
| Transaction coordinator fault injection | prepare/engine/save/commit/ACK 각 단계 crash; duplicate/reorder/concurrent request; repair failure; exactly-once business outcome | NFR-001~002/004~007, ER-002/010 |
| Real RimWorld engine adapter | map entity graph, holder/비spawn pawn, death/despawn/destroy callbacks, bed/grave/throne/master/area 및 실제 save/load 비교 | FR-166, NFR-002 |
| Multi-client Tactical | own-Pawn commands만, 동일 map authoritative state, Peaceful→Hostile 유지, Last Input Wins, 1x/Pause, reconnect/handoff | FR-098~107, BR-009~010 |
| Offline Combat worker PoC | owner process 없음 → 실제 save map load + AI defense → 전투 → persist → owner restore; worker crash/restart | FR-153~158, CON-010, AC-015 |
| Inventory conservation ledger oracle | 판매자+구매자+caravan+silver 총량 보존; 동일 stack concurrent tax/trade; stale local save; retry/crash/disk failure | FR-183~212, ER-008~010 |
| Faction / Feudal graph model test | 단일 faction/title, 최초 King atomicity, join/demotion/expel/branchsplit, cycle/orphan 방지 | FR-008~052/172~179 |
| Territory / Strategic Vision graph oracle | configured radius, holes/first claim, destruction, layer bounds, 공개 settlement/은폐 caravan, 1-hop alliance sharing | FR-053~089 |
| Diplomacy intent / alliance graph | attacker-tier pending, 양방향 pending 공격금지, highest ruler, betrayal intended target/FF, 1-hop allies, peace breach | FR-108~151 |
| UI state automation without GUI | per-request dialog registry, offline disabled reason, terminal state/재접속 cleanup; manual UX는 마지막에 사용자 | FR-090~097/220~229 |

관측 항목: transaction ID + PlayerId + session epoch + object revision + save/checkpoint revision + phase + commit decision + retry count. “예외 로그 없음”보다 entity/재고/소유권 불변식이 중요하다.

Packet reorder 테스트는 TCP 연결 자체가 byte order를 뒤집는다는 가정이 아니다. 서로 다른 sender, 세션 교체, handler scheduling, retry와 stale command의 적용 순서를 바꿔 검증한다.

## 13. Regression Risks

- offline 방문 거절을 추가하다 offline attack/tax/trade까지 거절하는 회귀.
- 기존 Fog 전체를 재사용해 공개 settlement를 숨기거나 secret caravan data를 모두 broadcast하는 회귀.
- identity 도입 후 nickname/local load ID에 묶인 ownership을 잘못 migration하는 회귀.
- 같은 faction 내 Player 양도에서 모든 동료 pawn/entity를 빼앗는 회귀.
- transaction result retry로 실제 map이나 inventory를 두 번 변경하는 회귀.
- AI/owner authority handoff 후 두 simulation이 동시에 확정하는 split-brain.
- tax 개편 시 deadline 자체로 체납을 만들거나 LastCollection을 예정일로 계산하는 회귀.
- singleton cache가 새 server/save에 잔존하여 가격/vision/owner가 오염되는 회귀.
- 모드가 offline vanilla 게임의 Draw/settle/letter를 변경하는 회귀.
- historical REPRO assertion을 release acceptance test로 집계하는 회귀.

## 14. Gemini Gap Analysis에서 반드시 확인할 영역

Gemini의 Current Implementation Baseline + SRS Gap Matrix가 제출되면 다음 표를 실제 source와 test로 독립 대조한다. 이번 첫 보고서는 그 제출물의 주장에 기대지 않았다.

| Gemini 주장 후보 | 반드시 요구할 증거 / 오판정 방지 |
|---|---|
| clock 구현 완료 | 180 TPS simulation vs 약1Hz packet 구분, config 및 restart 보존, local calendar 분리 |
| authentication/handshake 완료 | identity proof, version reject, pre-auth gate. Auth 로그만으로 완료 불가 |
| Tactical 구현 완료 | enum 아닌 command handler/authority/session, real map join 및 own Pawn trace |
| offline combat 지원 | owner process 없이 simulation/save 결과. offline 공격 차단은 요구 위반 |
| Territory 완료 | server tile owner/priority/connectivity, Tier radius/title territory. client 2-hop만으로 불가 |
| world settlement sync 완료 | cache 아닌 실제 WorldObject 공개 rendering 및 create/destroy 반영 |
| visit lifecycle 안전 | forged host, unique ID collision, cancel/accept concurrent winner, expiry, 여러 창/재접속 |
| atomic transfer 완료 | 전체 entity/Player ownership, layer/world IDs, durable save/ACK/restart/rollback repair |
| Faction/Tier/Feudal 완료 | enum/helper 아닌 aggregate/authority/호출 경로/transaction, first King/branch invariants |
| Tax 완료 | arrival+actual collection, direct relation, Player 미납 가치, deadline non-event |
| offline trade 완료 | 실제 local inventory/silver/caravan과 durable ledger 대조; NPC price DTO는 해당 기능이 아님 |
| NPC 시장 완료 | 독립 keys, amount 공식/config, initial sync/replay/위조 검증/vanilla restock |
| Betrayal/Alliance/Peace 완료 | intent event의 caller, political durable state, direct 1-hop graph/peace obligation |
| Persistence 완료 | 저장 코드, save artifact, process restart compare, partial-write/crash tests |
| test 100% 통과 | requirement trace / oracle / stub 한계 / current binary hash / REPRO vs acceptance 분리 |
| 참고 repo 기능 재사용 | 실제 csproj dependency 및 실행 경로. 동일 폴더 존재만으로 불가 |

필요한 판정 대응: CONFIRMED / CORRECTION REQUIRED / ARCHITECTURE ISSUE / INSUFFICIENT EVIDENCE. Source evidence 없는 SATISFIED는 승인하지 않는다.

## 15. Master에게 제출하는 Decision Requests

### DR-01 — Offline / Tactical / Persistent Inventory Authority ADR

[DECISION REQUEST]

Affected Requirement:
FR-098~107, FR-153~158, FR-183~212, NFR-002/004~007, CON-010.

Observed Conflict:
현재 owner-local Map과 in-memory server만 존재한다. owner offline에서는 shared authoritative Map과 실제 inventory를 실행/변경/영속화할 주체가 없다. offline 정상 simulation 정지와 필요시 combat simulation은 모두 충족해야 한다.

Code Evidence:
Server.csproj는 RimWorld engine/worker dependency 없음. Dialog_VisitWait.cs:89 map loading TODO. AtomicFiefTransferExecutor.cs:37 local loaded map만 사용. Program.cs:20~56 timer managers만 시작.

Option A:
별도 server-controlled RimWorld simulation worker가 Tactical/Offline Map을 실행하고 durable checkpoint/revision을 서버와 확정한다.

Option B:
온라인 owner hosting과 offline worker authority handoff를 결합하고 lease/epoch fencing과 단일 durable save source를 제공한다.

Trade-offs:
A는 worker 운영/API/메모리/엔진 로딩 검증이 필요하다. B는 owner/worker handoff, crash 및 split-brain 방어가 추가된다. 두 안 모두 offline combat과 실제 재고 보존 PoC가 필수다. SRS는 한 기술을 강제하지 않는다.

Recommendation:
Master가 authority / inventory / transaction / persistence ADR 범위를 확정한 뒤 최소 offline combat+save restore PoC부터 검증한다. 후보 확정 전 의존 대규모 기능의 구현 승인을 보류한다. owner offline 공격 금지는 대안으로 승인하지 않는다.

### DR-02 — 명시적 미결정 정책

[DECISION REQUEST]

Affected Requirement:
TBD-01 가입 초과 한도, TBD-02 퇴거 tile, TBD-03 절도 trigger, TBD-04 완전 소멸 entity 범위, TBD-05 부분 징수 LastCollection; 관련 FR-026~031/114/120~132/172~179/180~196.

Observed Conflict:
정책이 최상위 SRS에서 미확정이다. prototype helper/default나 시나리오 권장 문장을 확정 정책으로 승격할 근거가 없다.

Code Evidence:
FeudalManager는 신규 tree/join/split/policy가 없으며 current tax는 due-date 모델이다. 전체 source에 theft intent/eviction selector 구현 없음.

Option A:
Master가 각 정책을 승인하고 requirement baseline에 명시적인 결정 기록을 연결한다.

Option B:
관련 구현 Work Package만 BLOCKED BY REQUIREMENT로 두고 명확한 기능과 Architecture 검증은 진행한다.

Trade-offs:
A는 관련 상세 구현을 열 수 있지만 사용자 제품 선택이 필요할 수 있다. B는 다른 작업을 막지 않으나 해당 정책의 acceptance oracle은 아직 확정할 수 없다.

Recommendation:
현재는 B. Master가 기존 SRS의 다섯 TBD를 개별 결정한다. QA가 임의로 값을 만들지 않는다. 미결정 정책을 이유로 Offline Combat 등 이미 명확한 요구를 축소하지 않는다.

## 16. Final Recommendation

1. **현재 SRS 적합성 / Architecture 구현 Gate는 승인하지 않는다: BLOCKED BY ARCHITECTURE.**
2. Gemini가 제출할 Gap Matrix에서 enum/DTO/UI 메시지/주석/참고 repo를 구현 완료로 계산하지 않는지 우선 검증한다.
3. Master가 Critical Authority와 persistence/inventory/transaction 경계를 먼저 확정하고 작은 PoC에 독립 failure test를 요구한다.
4. 기존 packet framing, channel writer, main-thread dispatch, engine API 조사 및 rollback 회귀 자산은 검증 후 재사용 후보로 유지한다. 전체 재작성은 이번 보고서의 지시가 아니다.
5. 재현된 결함은 Gemini의 수정 또는 승인된 Architecture Work Package로 추적한다. QA는 Production을 직접 수정하지 않는다.
6. 아직 사용자 인게임 승인 요청 단계가 아니다. 첫 Baseline 보고 이후 Gemini 제출물과 코드의 독립 대조가 다음 작업이다.

## 17. 보고서 전달 상태

로컬 보고서 및 QA 증거 파일 작성은 완료했다. Master 후보 채팅 `프로젝트 인수인계 파악`(ID: 6abdcebb-5184-83e8-884f-2029851d9a18)에 보고서를 전송하려 했으나 자동 승인 검토가 거부했다. 일반적인 Master 보고 권한은 있으나 이 구체적인 채팅이 사용자가 지정한 보고 대상이라는 신뢰 가능한 확인이 부족하다는 사유다. 실제 전송은 이루어지지 않았다. 대상 채팅에 대한 사용자의 명시적인 확인 후 제출할 수 있다. 이 전달 제한은 코드/요구사항 조사 및 로컬 기준선 보고서의 완료 여부와는 별개다.

