# Official Gap Reconciliation Candidate v1

[QA REVIEW]

- Work Package: **WP-BASELINE-02 — Gemini Gap Matrix Independent Reconciliation**
- Report title: **Official_Gap_Reconciliation_Candidate_v1**
- Recipient: Master (GPT-5.6 Sol)
- Reviewer: QA / Architecture Reviewer
- Reviewed: 2026-10-01 (Asia/Seoul)
- Work-package verdict: **CONDITIONAL PASS — reconciliation artifact completed; Master adoption pending**
- Architecture Gate: **BLOCKED BY ARCHITECTURE — unchanged**
- Production change: **NONE**. QA runner/report additions only; no production build, commit, game control, operational server restart or 7777 traffic.
- Requirement source: [최상위 SRS](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md>).
- Compared: [Gemini report](<C:/Users/user/Desktop/RimMulti/current_implementation_baseline_and_srs_gap_matrix.md>) and [independent Architecture & QA Baseline](<C:/Users/user/Desktop/RimMulti/QA-Baseline/Architecture & QA Baseline Report.md>).

**Candidate 결론:** 현재 구현은 메모리 기반 서버 clock/manager, TCP transport, client local map patch의 기초다. 인증된 중앙 권한, 원격 Tactical Simulation, durable inventory 및 ownership transaction은 완성되지 않았다. Gemini의 정확한 MISSING/CONFLICT 분석은 채택하되, enum/DTO/주석/단일 정상 흐름을 Requirement 완료로 본 판정은 교정한다. 이 문서는 공식 baseline의 **후보**이며 새로운 구현 승인이나 인게임 게이트 통과 보고가 아니다.

## A. Requirement ID Integrity

### A.1 Canonical rule

FR/BR/NFR/CON/CFG는 오직 `요구사항_명세서.md`의 정의를 사용한다. 아래 표의 Requirement는 모두 **SRS-** prefix를 붙였다. 하위 문서는 문서명과 원문 번호를 함께 붙이며 같은 숫자를 의미 일치 근거로 쓰지 않는다. Gemini의 원문 ID는 역사적 참조로만 보존한다. UC/SCN 번호는 별도 namespace다.

SRS에서 추출한 고유 항목은 **FR 234 + BR 19 + NFR 12 + CON 10 + CFG 26 = 301**개다. B.1은 이를 한 항목당 한 행으로 다룬다. 요구의 전체 문구와 SRS line은 별도 `reconciliation-canonical-matrix.json`에 보존한다. Compound requirement의 부분 구현을 SATISFIED로 승격하지 않는다.

### A.2 확인한 번호 오류

| Gemini 원문 의미/번호 | Canonical correction |
|---|---|
| FR-005 version | SRS-FR-006/007 |
| FR-010 enum | SRS-FR-014; enum 정의만으로 중앙 관리 완료 아님 |
| FR-027 / BR-005 King-only | SRS-BR-004, SRS-FR-036~040 |
| FR-036 radius | SRS-FR-053~055, SRS-CFG-006 |
| FR-047 공개, FR-048 생성/소멸 | SRS-FR-069, SRS-FR-070 |
| FR-068~070 visit | SRS-FR-090~094 |
| FR-079 hostile clock | SRS-FR-103/104; SRS-BR-018은 tax arrival 규칙 |
| FR-084 attacker Tier | SRS-FR-110/111 |
| FR-094~101 betrayal | SRS-FR-120~130 |
| FR-123 Occupy | SRS-FR-166, SRS-NFR-002/005 |
| BR-006 direct tax, BR-023 no-arrival | SRS-BR-015, SRS-BR-018 |
| FR-149~159 shop | SRS-FR-197~212 |
| FR-160~165 market | SRS-FR-213~219 |
| NFR-001 consistency / NFR-003 persistence / NFR-004 authority / NFR-007 crash isolation | 각각 SRS-NFR-004 / 006 / 007 / 008 |
| CON-008 map-owner / CON-009 offline authority | CON-008은 separate server, CON-009는 dual clock. Offline authority는 SRS-CON-010 및 FR-153~158 |
| CFG-002~005 하위 문서 순서 | SRS: Weight / Promotion Threshold / Demotion Threshold / Grace Period |
| NFR-010 config, NFR-009 audit (Gemini roadmap) | config는 CFG 및 NFR-003, audit는 FR-234/NFR-012 |
| FR-035 가입 초과 decision, FR-104 theft decision | 실제 TBD-01 / TBD-03. SRS-FR-035는 Title radius; FR-104는 hostile pause |

**자기 보고서도 교정:** 기존 QA baseline QA-002의 Ban 관련 `FR-233` 인용은 `SRS-FR-232`가 맞다. SRS-FR-233은 별도 관리자 UI를 필수로 하지 않는다는 범위 제약이다. ER/AC 등 기존 보조 참조는 본 후보의 Canonical Requirement ID로 사용하지 않는다.

### A.3 해석 확장 금지

- SRS-FR-116은 **Letter 또는 Message**다. Gemini의 “정식 Letter 없음”만으로 결함 판정하지 않는다. 내용과 대상/전달 보장이 검증 대상이다.
- Baron 한도 1개, JSON/SQLite 선택, config live reload, snapshot 10틱은 현재 Canonical 필수값이 아니다. CFG·ADR/PoC 선택 또는 TBD로 취급한다.
- Tribe 준비시간 0은 SRS-FR-111의 **변경 가능한 초기 balance 후보**다. 현재 defender Tier를 사용한다는 결함과 구분한다.
- SRS는 **전체 World의 완전 Lockstep**을 목표로 하지 않는다. Section 77의 Map-owner 방식은 후보이며, 사용되지 않는 packet enum 이름만으로 특정 Tactical 동기화 방식이 최종 승인/금지됐다고 결론 내리지 않는다.
- Offline이면 공격 불가로 바꾸지 않는다. CON-001/002의 명시된 fallback만 해당 범위에서 검토한다.
- TBD-01~05 및 SRS architecture 후보 선택은 Master decision 대상이며 구현 편의로 확정하지 않는다.

## B. Gemini Matrix Reconciliation

### B.0 Evidence and verdict semantics

**QA Verdict**는 요청된 reconciliation enum이다. **Final Candidate Verdict**는 구현 coverage 상태: SATISFIED / PARTIAL / CONFLICT / MISSING / UNKNOWN. CONFIRMED는 Gemini의 사실을 확인했다는 뜻이며 product PASS와 다르다. ID 오류는 A와 원문 crosswalk에서 별도로 교정하고, B.1은 교정된 요구의 실질 판정을 기록한다. `NOT ASSESSED`/독립 평가 누락은 Gemini omission이며 근거 없이 PASS를 만들지 않는다.

**Code Evidence catalogue** — 번호는 아래 실제 파일·메서드·line을 가리킨다.

| Evidence | Actual source / observed scope |
|---|---|
| E00 | 46 production C# 파일 전체 + 3 csproj 구조 검색. 구현 부재는 runtime class/handler/caller 부재 기준이며 enum/DTO만 있는 경우 별도 명시. `input-manifest.json`의 입력 경로/해시 참조 |
| E01 | [WorldTickManager](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Time/WorldTickManager.cs:33>): Start=0, independent loop, SyncIntervalTicks=180 → 약 **1Hz sync**, 180 packet/s 아님; lag 처리/메모리 clock |
| E02 | [Client clock](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Time/ClientWorldTickManager.cs:32>): combat mode 외부 설정 caller 없음; accumulator cap360/max15 per update; [TickPatches](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Patches/TickPatches.cs:31>) online world-only guard, dormant hostile guard |
| E03 | [Server router](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:115>): auth prerequisite 없음, handshake self-claimed ID/version; [client identity](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Networking/NetworkClient.cs:80>) PersonaName/nickname |
| E04 | [DiplomacyManager](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Managers/DiplomacyManager.cs:41>): defenderTier, Pending→Active, RecordBetrayal notification만. 전체 파일 **81줄**; [FactionTierHelper](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Models/Enums/FactionTier.cs:23>) hardcoded score/duration, evaluation callers 없음 |
| E05 | [NobilityTitleHelper](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Models/Enums/NobilityTitle.cs:25>): superior>subordinate, Count+ tax. 두 permission helper 생산 caller 없음 |
| E06 | [FeudalManager](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Managers/FeudalManager.cs:160>): pending/active in-memory, line198 ID overwrite, line262/267 pending 제거 후 ownership 변경; line117 tax deadline, line290 auto delinquency. [SettlementData](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Models/SettlementData.cs:20>) const radius2 / sequential TransferOwnership |
| E07 | [Atomic executor](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Fief/AtomicFiefTransferExecutor.cs:34>): map by int tile, spawned old-faction pawns, CanHaveFaction things, pretracked SetFaction; line135 save 없는 success; line212/254/320/351 snapshot restore null 검증 공백; line390 rollback 및 destroyed things skip |
| E08 | [Fog/Border](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Patches/FogOfWarPatches.cs:63>): cache-only FogSync(surface0), WorldObject.Draw line97 broad hide; line169 valid tile/layer, line201 2-Hop BFS proximity. Territory/Vision 생성기 아님 |
| E09 | [Settlement list apply](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Networking/NetworkClient.cs:200>): border cache 갱신; line291 로컬 등록은 connect 때 1회, actual remote world object materialization/deletion 없음. Feudal.RegisterSettlement line64 |
| E10 | [Camera jump](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Patches/LetterPatches.cs:27>): 미탐색 tile 이동 차단 및 layer 손실 |
| E11 | [Visit server](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Network/TcpNetworkServer.cs:163>): HostPlayerId caller trust; cancel line223/response254 separate get/check/set/remove; disconnect355 player-ID 기준 정리 |
| E12 | [Visit wait](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/UI/Dialog_VisitWait.cs:74>) Accepted 뒤 메시지/TODO; [Visit request](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/UI/Dialog_VisitRequest.cs:17>) static latest window; [Visit gizmo](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Patches/VisitPatches.cs:34>) owner presence/caravan arrival gate 없음 |
| E13 | [Client packet dispatch](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Networking/NetworkClient.cs:186>): War/Tax Message 일부; BetrayalNotification handler 없음 |
| E14 | [PacketHeader](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Packets/PacketHeader.cs:48>) Tactical enum-only; [Alliance DTO](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Packets/Diplomacy/PKT_AllianceAndBetrayal.cs:16>) 실제 class=PKT_AllianceAction, PKT_BetrayalNotification; P2P order DTO 없음 |
| E15 | [Market model](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Models/DynamicMarketState.cs:46>): lock/CloneSnapshot, quadratic buy/linear sale, fixed decay/stock +/-1; [Market manager](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Managers/DynamicMarketManager.cs:24>) string concatenated key/unchecked report |
| E16 | [Trade hooks](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Patches/TradePatches.cs:17>): GetPriceFor multiplier, TryExecute postfix count report; settlement/trader-kind identifiers. Actual engine quantity/direction/report timing 미실행 |
| E17 | [Server entry point](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Program.cs:20>): in-memory managers, seed NPC150/220, event broadcast, line60 quit/exit/status. save/config/kick/ban/audit writer 없음; fief target 없으면 broadcast fallback |
| E18 | [Session sender](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Network/ServerClientSession.cs:28>): reliable unbounded + pending Interlocked, tick bounded64 DropOldest, single async writer/5sec timeout, saturation disconnect. [Client receive](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Networking/NetworkClient.cs:39>) parser reused; queued dispatch167 epoch 없음 |
| E19 | [Client csproj](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/WarEconomy.Client.csproj:4>) **net472** with actual engine refs; Common netstandard2.0, Server net8.0 separate entry point; deployment hash record in baseline |

**Test Evidence catalogue**

- [T01~T08 rerun log](<C:/Users/user/Desktop/RimMulti/QA-Baseline/reconciliation-baseline-rerun.log>) / [runner source](<C:/Users/user/Desktop/RimMulti/QA-Baseline/BaselineChecks/Program.cs>): T01 zero-client clock **38 ticks/약 200ms**; T02 BASE-01 defender-tier; T03 BASE-03 colliding transfer IDs; T04 BASE-04 unauthenticated war; T05 BASE-05 incompatible version/identity metadata overwrite; T06 BASE-06 fake host; T07 BASE-02 no-arrival delinquency; T08 BASE-07 parser old partial frame.
- [T09~T16 new log](<C:/Users/user/Desktop/RimMulti/QA-Baseline/reconciliation-checks.log>) / [runner source](<C:/Users/user/Desktop/RimMulti/QA-Baseline/ReconciliationChecks/Program.cs>): T09 REC-01 Tribe→Empire Pending; T10 REC-02 notification only / missing claimed APIs/state; T11 REC-03 same report twice stock80; T12 REC-04 negative purchase stock110; T13 REC-05 composite-key alias; T14 REC-06 dormant Duke permission; T15 REC-07 concurrent1000 writes/independent snapshot **scoped PASS**; T16 REC-08 2→1.95 decay **scoped PASS**.
- **S = 정적 확인만 수행 / no dedicated runtime acceptance test.** Race interleavings, Unity rollback callbacks, save failure and Tactical latency have not been executed here.
- Rerun: **7/7 historical counterexamples reproduced**, plus **6/6 new counterexamples**, **2/2 scoped asset checks**. These counts are **not** product acceptance passes.
- Both runners compile current Common + Server sources directly, not historical server DLLs. Production entry-point CurrentTick dependency alone is stubbed at100. Reflection router tests enter the real handler using loopback ephemeral sessions; production 7777 is untouched.
- New runner compilation/run succeeded; baseline rerun had NU1900 vulnerability-feed access warning. No full solution rebuild or current Unity-runtime test is claimed. Initial new-runner field scan misclassified an event backing delegate as state; the QA predicate was corrected to exclude delegates and the final suite rerun. No production fix occurred.
- [Input integrity](<C:/Users/user/Desktop/RimMulti/QA-Baseline/reconciliation-input-integrity.json>): **55/55 baseline production/document inputs unchanged** before finalization. Gemini SHA256 `80E5D94CD448AEE04A4D390419DE9A075F4A5CB63A1828F5B5A255461B3359BA`.

### B.1 Canonical Requirement matrix

각 Requirement는 SRS의 해당 줄로 연결된다. 원문 번호의 숫자 일치가 아닌 Canonical 의미에 따라 판정했다. 축약 표시한 문구의 전체 내용은 JSON에 보존했다.

| Requirement | Gemini Verdict (original ID/line) | QA Verdict | Final Candidate Verdict | Code Evidence | Test Evidence | Reason |
|---|---|---|---|---|---|---|
| [SRS-FR-001](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:240>) 서버는 접속 Player가 0명인 경우에도 World Time을 계속 진행해야 한다. | L116 FR-001 SATISFIED | CONFIRMED | SATISFIED | E01 | T01 | 접속 세션 없이 월드 시계가 진행한다. 지속 TPS·재시작·설정 검증까지 통과했다는 의미는 아니다. |
| [SRS-FR-002](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:243>) Settlement Local Time은 World Time과 독립적으로 진행될 수 있어야 한다. | L117–118 FR-002/003 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E01,E02 | S | 틱 분리와 누적기는 존재하지만 owner offline 생명주기·공동 Map Authority·calendar 동기화가 완성되지 않았다. 게임 실행 중 Disconnect 시 vanilla map이 계속 도는 경로가 남는다. |
| [SRS-FR-003](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:246>) Settlement Owner가 Offline인 동안 일반 Settlement Simulation은 정지해야 한다. | L117–118 FR-002/003 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E01,E02 | S | 틱 분리와 누적기는 존재하지만 owner offline 생명주기·공동 Map Authority·calendar 동기화가 완성되지 않았다. 게임 실행 중 Disconnect 시 vanilla map이 계속 도는 경로가 남는다. |
| [SRS-FR-004](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:249>) 시스템은 Player를 영구적으로 식별해야 한다. | L119 FR-004 PARTIAL | CONFIRMED | PARTIAL | E03 | T05 | Handshake carrier는 있으나 PersonaName/닉네임은 영구 Steam ID가 아니며 서버 인증도 없다. |
| [SRS-FR-005](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:252>) Player 영구 식별은 Steam ID를 우선 사용해야 한다. Steam ID 기반 식별 구현이 현실적으로 불가능한 경우 ID/Password 기반 계정을 대체 방식으… | L119 FR-004 PARTIAL | CONFIRMED | PARTIAL | E03 | T05 | Handshake carrier는 있으나 PersonaName/닉네임은 영구 Steam ID가 아니며 서버 인증도 없다. |
| [SRS-FR-006](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:257>) 서버는 Client와 Server의 Protocol 또는 Mod Version을 검증해야 한다. | L120 FR-005 PARTIAL | DOWNGRADE REQUIRED | MISSING | E03 | T05 | Version 필드 수신만 구현됐다. 비호환 접속을 거부하지 않는다. |
| [SRS-FR-007](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:260>) 호환되지 않는 Version의 Client 접속은 거부해야 한다. | L120 FR-005 PARTIAL | DOWNGRADE REQUIRED | MISSING | E03 | T05 | Version 필드 수신만 구현됐다. 비호환 접속을 거부하지 않는다. |
| [SRS-FR-008](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:263>) 신규 Player에게 개인 Faction을 생성해야 한다. | L121 FR-006~007 MISSING | CONFIRMED | MISSING | E00,E03 | S | 영구 Player/Faction 생성 aggregate와 가입 생명주기가 없다. GetFactionTier의 Tribe default는 신규 세력 생성이 아니다. |
| [SRS-FR-009](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:266>) 신규 개인 Faction의 기본 이름은 Player 이름을 기반으로 생성해야 한다. | L121 FR-006~007 MISSING | CONFIRMED | MISSING | E00,E03 | S | 영구 Player/Faction 생성 aggregate와 가입 생명주기가 없다. GetFactionTier의 Tribe default는 신규 세력 생성이 아니다. |
| [SRS-FR-010](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:269>) 신규 개인 Faction의 Tier는 Tribe여야 한다. | L121 FR-006~007 MISSING | CONFIRMED | MISSING | E00,E03 | S | 영구 Player/Faction 생성 aggregate와 가입 생명주기가 없다. GetFactionTier의 Tribe default는 신규 세력 생성이 아니다. |
| [SRS-FR-011](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:276>) 신규 Faction에는 기존 활성 Faction과 충분히 구별되는 색상을 자동 배정해야 한다. | L122 FR-008~009 MISSING | CONFIRMED | MISSING | E00 | S | 색상 할당·반환·재사용 관리자 없음. 자동 색상 UI 미제공만으로 FR-012를 충족했다고 보지 않는다. |
| [SRS-FR-012](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:279>) Player가 임의로 Faction 색상을 선택할 필요는 없다. | L122 FR-008~009 MISSING | CONFIRMED | MISSING | E00 | S | 색상 할당·반환·재사용 관리자 없음. 자동 색상 UI 미제공만으로 FR-012를 충족했다고 보지 않는다. |
| [SRS-FR-013](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:282>) 소멸 또는 병합되어 더 이상 사용되지 않는 Faction 색상은 재사용할 수 있어야 한다. | L122 FR-008~009 MISSING | CONFIRMED | MISSING | E00 | S | 색상 할당·반환·재사용 관리자 없음. 자동 색상 UI 미제공만으로 FR-012를 충족했다고 보지 않는다. |
| [SRS-FR-014](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:297>) 서버는 Faction Tier를 중앙에서 관리해야 한다. | L123 FR-010 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E04 | S | 5-tier enum과 서버 Tier dictionary는 있다. 실제 Faction 집계·권한 있는 변경·영속 상태 관리는 없다. |
| [SRS-FR-015](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:300>) Tier 평가에는 최소한 다음 요소를 사용할 수 있어야 한다. - 유효 Settlement 수 - Faction Total Wealth - 활동 Pawn 수 - 연결 T… | L124 FR-011~014 CONFLICT | CONFIRMED | PARTIAL | E04,E00 | S | 평가 helper/하드코딩은 확인되지만 생산 코드 호출자가 없다. '즉시 자동 승격/강등 구현'은 틀렸고 연결 territory·title·grace 상태는 미구현이다. FR-016은 설정 부재, FR-017~020은 런타임 MISSING. |
| [SRS-FR-016](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:309>) Tier 평가 공식의 Weight 및 Threshold는 서버 설정으로 변경 가능해야 한다. 초기 개념식은 다음과 같다. `Score = SettlementCount ×… | L124 FR-011~014 CONFLICT | CONFIRMED | CONFLICT | E04,E00 | S | 평가 helper/하드코딩은 확인되지만 생산 코드 호출자가 없다. '즉시 자동 승격/강등 구현'은 틀렸고 연결 territory·title·grace 상태는 미구현이다. FR-016은 설정 부재, FR-017~020은 런타임 MISSING. |
| [SRS-FR-017](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:318>) 승격 조건을 만족한 Faction은 자동 승격해야 한다. | L124 FR-011~014 CONFLICT | CONFIRMED | MISSING | E04,E00 | S | 평가 helper/하드코딩은 확인되지만 생산 코드 호출자가 없다. '즉시 자동 승격/강등 구현'은 틀렸고 연결 territory·title·grace 상태는 미구현이다. FR-016은 설정 부재, FR-017~020은 런타임 MISSING. |
| [SRS-FR-018](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:321>) 강등 기준 미달 시 즉시 강등하지 않고 설정된 Grace Period를 적용해야 한다. | L124 FR-011~014 CONFLICT | CONFIRMED | MISSING | E04,E00 | S | 평가 helper/하드코딩은 확인되지만 생산 코드 호출자가 없다. '즉시 자동 승격/강등 구현'은 틀렸고 연결 territory·title·grace 상태는 미구현이다. FR-016은 설정 부재, FR-017~020은 런타임 MISSING. |
| [SRS-FR-019](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:324>) Grace Period 종료 전에 조건이 회복되면 강등을 취소해야 한다. | L124 FR-011~014 CONFLICT | CONFIRMED | MISSING | E04,E00 | S | 평가 helper/하드코딩은 확인되지만 생산 코드 호출자가 없다. '즉시 자동 승격/강등 구현'은 틀렸고 연결 territory·title·grace 상태는 미구현이다. FR-016은 설정 부재, FR-017~020은 런타임 MISSING. |
| [SRS-FR-020](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:327>) Grace Period 종료까지 조건이 회복되지 않으면 Faction을 강등해야 한다. | L124 FR-011~014 CONFLICT | CONFIRMED | MISSING | E04,E00 | S | 평가 helper/하드코딩은 확인되지만 생산 코드 호출자가 없다. '즉시 자동 승격/강등 구현'은 틀렸고 연결 territory·title·grace 상태는 미구현이다. FR-016은 설정 부재, FR-017~020은 런타임 MISSING. |
| [SRS-BR-001](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:334>) Tribe는 단독 Player Faction이다. | L190 BR-003 수정 필요 | CONFIRMED | MISSING | E00,E03 | S | Tribe 단독 membership와 신규 faction lifecycle 없음. |
| [SRS-FR-021](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:337>) Tribe는 다른 Player를 가입시킬 수 없어야 한다. | L128 FR-019~023 MISSING | CONFIRMED | MISSING | E00 | S | Tribe 가입 차단을 포함한 가입 프로토콜 자체가 없다. |
| [SRS-FR-022](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:340>) Tribe가 Minor Faction 승격 조건을 만족하면 다음 두 작업을 하나의 원자적 사건으로 수행해야 한다. - Faction Tier → Minor Faction… | L125 FR-015 MISSING; L191 BR-004 미구현 | CONFIRMED | MISSING | E00,E04 | S | Founder/King와 Tier를 함께 commit하는 transaction 없음. |
| [SRS-FR-023](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:355>) Faction Tier가 상승할 때 최고 통치자에게 Faction 이름 변경 기회를 한 번 제공해야 한다. | L127 FR-017~018 MISSING | CONFIRMED | MISSING | E00 | S | 승격 1회 개명·skip 보존·정확한 진행도 UI 없음. |
| [SRS-FR-024](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:358>) 이름 변경 Dialog는 Vanilla RimWorld의 정착지/세력 명명 UX와 유사한 방식으로 제공할 수 있다. | L127 FR-017~018 MISSING | CONFIRMED | UNKNOWN | E00 | S | Vanilla 유사 naming UX는 허용 방식이다. 이를 mandatory implementation으로 확대하지 않는다. 전제인 개명 flow가 없어 적용 증거가 없다. |
| [SRS-FR-025](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:361>) Player가 변경을 건너뛰면 기존 이름을 유지해야 한다. | L127 FR-017~018 MISSING | CONFIRMED | MISSING | E00 | S | 승격 1회 개명·skip 보존·정확한 진행도 UI 없음. |
| [SRS-FR-026](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:368>) Minor Faction 이상은 다른 독립 Player의 가입 요청을 받을 수 있어야 한다. | L128 FR-019~023 MISSING | CONFIRMED | MISSING | E00 | S | 가입 인가·기존 세력 해체·player/settlement 편입 transaction 없음. |
| [SRS-FR-027](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:371>) Faction Ruler는 가입 요청을 수락하거나 거절할 수 있어야 한다. | L128 FR-019~023 MISSING | CONFIRMED | MISSING | E00 | S | 가입 인가·기존 세력 해체·player/settlement 편입 transaction 없음. |
| [SRS-FR-028](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:374>) 가입이 수락되면 가입 Player의 기존 개인 Faction은 해체되어야 한다. | L128 FR-019~023 MISSING | CONFIRMED | MISSING | E00 | S | 가입 인가·기존 세력 해체·player/settlement 편입 transaction 없음. |
| [SRS-FR-029](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:377>) 가입 Player와 해당 Player의 Settlement는 대상 Faction으로 편입되어야 한다. | L128 FR-019~023 MISSING | CONFIRMED | MISSING | E00 | S | 가입 인가·기존 세력 해체·player/settlement 편입 transaction 없음. |
| [SRS-FR-030](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:380>) 가입 Player는 가입과 동시에 최소 Baron 작위를 받아야 한다. | L129 FR-024~026 PARTIAL | DOWNGRADE REQUIRED | MISSING | E05,E00 | S | Title enum은 개인 단일 Title·가입 최소 Baron·Branch 지정·승강등 대체 정책 구현이 아니다. |
| [SRS-FR-031](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:383>) 가입 시 어느 봉건 계통에 속할지 지정해야 한다. | L129 FR-024~026 PARTIAL | DOWNGRADE REQUIRED | MISSING | E05,E00 | S | Title enum은 개인 단일 Title·가입 최소 Baron·Branch 지정·승강등 대체 정책 구현이 아니다. |
| [SRS-BR-002](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:386>) Player는 동시에 하나의 Faction에만 정식 소속될 수 있다. | L188 BR-001 일치 | DOWNGRADE REQUIRED | MISSING | E03,E06 | T05 | 세션 FactionId 필드는 단일 Player 소속 invariant가 아니다. 서버 Player aggregate와 멤버십 검증 없음. |
| [SRS-BR-003](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:404>) Player는 동시에 하나의 Title만 보유할 수 있다. | L189 BR-002 일치 | DOWNGRADE REQUIRED | MISSING | E05,E06 | S | 영지별 NobilityTitle은 Player가 하나의 Title만 가지게 하는 모델이 아니다. |
| [SRS-FR-032](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:407>) Title 승진 시 이전 Title은 새 Title로 대체해야 한다. | L129 FR-024~026 PARTIAL | DOWNGRADE REQUIRED | MISSING | E05,E00 | S | Title enum은 개인 단일 Title·가입 최소 Baron·Branch 지정·승강등 대체 정책 구현이 아니다. |
| [SRS-FR-033](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:410>) Title 강등 시 이전 Title은 새 Title로 대체해야 한다. | L129 FR-024~026 PARTIAL | DOWNGRADE REQUIRED | MISSING | E05,E00 | S | Title enum은 개인 단일 Title·가입 최소 Baron·Branch 지정·승강등 대체 정책 구현이 아니다. |
| [SRS-FR-034](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:413>) Title별 최대 Settlement 수를 별도로 설정할 수 있어야 한다. | L136 FR-042~044 MISSING(작위령); 나머지 미독립평가 | CONFIRMED | MISSING | E05,E00 | S | Title별 SettlementLimit과 내부 작위령 반경 데이터/설정 없음. Gemini L475의 FR-035는 가입 초과 처리라는 오번호다. |
| [SRS-FR-035](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:416>) Title별 내부 작위령 Radius를 별도로 설정할 수 있어야 한다. | L136 FR-042~044 MISSING(작위령); 나머지 미독립평가 | CONFIRMED | MISSING | E05,E00 | S | Title별 SettlementLimit과 내부 작위령 반경 데이터/설정 없음. Gemini L475의 FR-035는 가입 초과 처리라는 오번호다. |
| [SRS-BR-004](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:423>) 작위 임명, 승진, 강등 및 박탈은 King 이상만 수행할 수 있다. | L192 BR-005 정면 충돌 | CONFIRMED | MISSING | E05,E00 | T14 | Duke 허용 helper는 정책과 충돌하지만 unused다. 실제 King-only 인가 및 관리 endpoint는 미구현. |
| [SRS-FR-036](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:426>) King 이상은 Player를 특정 Feudal Branch에 임명할 수 있어야 한다. | L130 FR-027 CONFLICT | CONFIRMED | MISSING | E05,E00 | T14 | CanRevokeOrExpel은 Duke도 허용하지만 호출자가 없다. 이것은 재사용 시 정책 충돌이며 live 박탈 endpoint가 구현됐다는 증거는 아니다. |
| [SRS-FR-037](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:429>) King 이상은 Player를 승진시킬 수 있어야 한다. | L130 FR-027 CONFLICT | CONFIRMED | MISSING | E05,E00 | T14 | CanRevokeOrExpel은 Duke도 허용하지만 호출자가 없다. 이것은 재사용 시 정책 충돌이며 live 박탈 endpoint가 구현됐다는 증거는 아니다. |
| [SRS-FR-038](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:432>) King 이상은 Player를 강등시킬 수 있어야 한다. | L130 FR-027 CONFLICT | CONFIRMED | MISSING | E05,E00 | T14 | CanRevokeOrExpel은 Duke도 허용하지만 호출자가 없다. 이것은 재사용 시 정책 충돌이며 live 박탈 endpoint가 구현됐다는 증거는 아니다. |
| [SRS-FR-039](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:435>) King 이상은 관리 권한이 있는 Player의 Title을 박탈할 수 있어야 한다. | L130 FR-027 CONFLICT | CONFIRMED | MISSING | E05,E00 | T14 | CanRevokeOrExpel은 Duke도 허용하지만 호출자가 없다. 이것은 재사용 시 정책 충돌이며 live 박탈 endpoint가 구현됐다는 증거는 아니다. |
| [SRS-FR-040](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:438>) Empire에서는 Emperor가 King Title을 박탈할 수 있어야 한다. | L130 FR-027 CONFLICT | CONFIRMED | MISSING | E05,E00 | T14 | CanRevokeOrExpel은 Duke도 허용하지만 호출자가 없다. 이것은 재사용 시 정책 충돌이며 live 박탈 endpoint가 구현됐다는 증거는 아니다. |
| [SRS-FR-041](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:445>) Title 강등으로 SettlementLimit이 감소했을 때 Player가 Limit을 초과하면 강등을 즉시 완료해서는 안 된다. | Gemini FR Matrix에서 강등+양도 원자 흐름 누락 | INSUFFICIENT EVIDENCE | MISSING | E00,E06,E07 | T03 | Limit 해소 전 강등 보류와 Title/영지의 공동 commit 경로 없음. |
| [SRS-FR-042](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:448>) 대상 Player는 Limit을 만족할 만큼 Settlement를 King 또는 Emperor에게 양도해야 한다. | Gemini FR Matrix에서 강등+양도 원자 흐름 누락 | INSUFFICIENT EVIDENCE | MISSING | E00,E06,E07 | T03 | Limit 해소 전 강등 보류와 Title/영지의 공동 commit 경로 없음. |
| [SRS-FR-043](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:451>) Settlement 양도와 Title 변경은 일관된 Transaction으로 처리해야 한다. | Gemini FR Matrix에서 강등+양도 원자 흐름 누락 | INSUFFICIENT EVIDENCE | MISSING | E00,E06,E07 | T03 | Limit 해소 전 강등 보류와 Title/영지의 공동 commit 경로 없음. |
| [SRS-NFR-001](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:454>) 중간 실패로 인해 Settlement만 이전되고 Title이 변경되지 않는 등의 부분 완료 상태를 남겨서는 안 된다. | L220 NFR-001(상태 일관성; 실제 NFR-004) | REQUIREMENT-ID ERROR | MISSING | E00,E06 | T03 | Canonical 의미는 강등+Settlement 양도 부분 완료 금지다. 해당 공동 transaction은 미구현. |
| [SRS-BR-005](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:461>) Title Revocation과 Faction Expulsion은 동일한 결과를 가진다. | L194 BR-007 미구현 | CONFIRMED | MISSING | E00 | S | Title revocation=expulsion을 수행하는 transaction 없음. |
| [SRS-FR-044](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:464>) Player가 제명되면 해당 Faction에서 제거되어야 한다. | L131 FR-028~032 MISSING | CONFIRMED | MISSING | E00,E06 | S | 박탈=제명, 신규 Faction·잔여 자산 재평가·한도 양도 경로 없음. |
| [SRS-FR-045](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:467>) 제명 Player에게 새로운 개인 Faction을 생성해야 한다. | L131 FR-028~032 MISSING | CONFIRMED | MISSING | E00,E06 | S | 박탈=제명, 신규 Faction·잔여 자산 재평가·한도 양도 경로 없음. |
| [SRS-FR-046](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:470>) 제명 Player의 남은 Settlement는 해당 신규 Faction에 유지해야 한다. | L131 FR-028~032 MISSING | CONFIRMED | MISSING | E00,E06 | S | 박탈=제명, 신규 Faction·잔여 자산 재평가·한도 양도 경로 없음. |
| [SRS-FR-047](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:473>) 신규 Faction Tier는 현재 소유 자산을 기준으로 다시 계산해야 한다. | L131 FR-028~032 MISSING | CONFIRMED | MISSING | E00,E06 | S | 박탈=제명, 신규 Faction·잔여 자산 재평가·한도 양도 경로 없음. |
| [SRS-FR-048](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:476>) 제명으로 SettlementLimit을 초과하게 되는 경우 강등과 동일하게 초과 Settlement를 기존 King 또는 Emperor에게 양도해야 한다. | L131 FR-028~032 MISSING | CONFIRMED | MISSING | E00,E06 | S | 박탈=제명, 신규 Faction·잔여 자산 재평가·한도 양도 경로 없음. |
| [SRS-FR-049](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:483>) Faction의 Feudal 구조는 Tree 구조를 가져야 한다. 예: ```text Emperor ├─ King A │   ├─ Duke A │   │   └─ Mar… | L132 FR-033~034 UI MISSING; L193 BR-006 충돌 | CONFIRMED | MISSING | E00,E05,E06 | S | 봉건 Tree/Branch와 복수 King 모델이 없다. Settlement의 title 필드는 Player title tree가 아니다. |
| [SRS-FR-050](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:497>) 동일 Faction 내부에서도 서로 다른 Feudal Branch를 구분해야 한다. | L132 FR-033~034 UI MISSING; L193 BR-006 충돌 | CONFIRMED | MISSING | E00,E05,E06 | S | 봉건 Tree/Branch와 복수 King 모델이 없다. Settlement의 title 필드는 Player title tree가 아니다. |
| [SRS-FR-051](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:500>) 세금 및 관리 관계는 Feudal Tree를 기준으로 판단해야 한다. | L132 FR-033~034 UI MISSING; L193 BR-006 충돌 | CONFIRMED | MISSING | E00,E05,E06 | S | 봉건 Tree/Branch와 복수 King 모델이 없다. Settlement의 title 필드는 Player title tree가 아니다. |
| [SRS-FR-052](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:507>) Empire는 복수 King을 포함할 수 있어야 한다. 추가 King은 다음 방법으로 생성할 수 있다. - 다른 Nation을 복속시키고 기존 King을 유지 - Emp… | L132 FR-033~034 UI MISSING; L193 BR-006 충돌 | CONFIRMED | MISSING | E00,E05,E06 | S | 봉건 Tree/Branch와 복수 King 모델이 없다. Settlement의 title 필드는 Player title tree가 아니다. |
| [SRS-FR-053](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:519>) 각 Settlement는 주변 Tile에 Faction Territory를 생성해야 한다. | L133 FR-036 CONFLICT | CONFIRMED | CONFLICT | E08,E04 | S | 고정 2-Hop 정착 금지 검사와 BorderRadius=2는 Tier별 territory 생성·설정과 다르다. |
| [SRS-FR-054](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:522>) Territory Radius는 Faction Tier에 따라 달라야 한다. | L126 FR-016 CONFLICT; L133 FR-036 CONFLICT | CONFIRMED | CONFLICT | E08,E04 | S | 고정 2-Hop 정착 금지 검사와 BorderRadius=2는 Tier별 territory 생성·설정과 다르다. |
| [SRS-FR-055](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:525>) Faction Tier별 Border Radius는 서버 설정 가능해야 한다. | L126 FR-016 CONFLICT; L133 FR-036 CONFLICT | CONFIRMED | CONFLICT | E08,E04 | S | 고정 2-Hop 정착 금지 검사와 BorderRadius=2는 Tier별 territory 생성·설정과 다르다. |
| [SRS-FR-056](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:528>) 동일 Faction Settlement의 Border가 연결되면 하나의 연결된 Territory로 취급해야 한다. | L134 FR-037~040 PARTIAL | DOWNGRADE REQUIRED | MISSING | E08,E00 | S | BFS는 tile 거리 검사다. 연결 Territory를 합치고 구멍을 보존하는 생성기가 아니다. |
| [SRS-FR-057](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:531>) Border 사이의 빈 Tile은 자동으로 채우지 않아야 한다. 중간 Territory가 필요하면 실제 Settlement를 추가해야 한다. | L134 FR-037~040 PARTIAL | DOWNGRADE REQUIRED | MISSING | E08,E00 | S | BFS는 tile 거리 검사다. 연결 Territory를 합치고 구멍을 보존하는 생성기가 아니다. |
| [SRS-FR-058](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:536>) Settlement가 파괴되면 해당 Settlement가 제공하던 Border는 즉시 제거해야 한다. | L134 FR-037~040 파괴 시 제거 PARTIAL | DOWNGRADE REQUIRED | MISSING | E08,E09 | S | SRS-FR-058은 파괴 시 border 제거다. 목록/cache는 있으나 제거 이벤트와 authoritative Territory 재계산 경로는 없다. |
| [SRS-BR-006](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:545>) Territory 충돌 시 먼저 존재한 Territory가 우선한다. | L201 BR-014 수정 필요 | CONFIRMED | MISSING | E08,E00 | S | 선점 Territory timestamp/priority engine 없음. |
| [SRS-FR-059](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:548>) 후발 Border 확장은 기존 타 Faction Territory를 덮어써서는 안 된다. | L135 FR-041 MISSING; L201 BR-014 수정 필요 | CONFIRMED | MISSING | E00,E08 | S | 선점 territory 확장 방지·생성 순서 처리가 없다. '연결 territory 규모 평가'는 FR-015의 하위 요소다. |
| [SRS-FR-060](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:555>) Player가 Title을 가지면 해당 Player가 소유한 Settlement들의 Territory는 해당 Title Territory를 구성해야 한다. | L136 FR-042~044 MISSING | CONFIRMED | MISSING | E08,E00 | S | Title territory, 아군 표시 및 연결 territory 계산 없음. |
| [SRS-FR-061](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:558>) Title Territory Radius는 Title Rank에 따라 달라질 수 있어야 한다. | L136 FR-042~044 MISSING | CONFIRMED | MISSING | E08,E00 | S | Title territory, 아군 표시 및 연결 territory 계산 없음. |
| [SRS-FR-062](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:561>) Faction 내부 구성원은 내부 작위령 경계를 확인할 수 있어야 한다. | L136 FR-042~044 MISSING | CONFIRMED | MISSING | E08,E00 | S | Title territory, 아군 표시 및 연결 territory 계산 없음. |
| [SRS-FR-063](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:564>) 다른 Faction의 Player에게 내부 작위령 경계를 표시할 필요는 없다. | L136 FR-042~044 MISSING | CONFIRMED | UNKNOWN | E08,E00 | S | 외부 Faction에 내부 작위령을 표시할 필요는 없다. 외부 표시 미구현을 결함으로 요구하지 않는다. Title Territory 자체는 미구현이어서 경계 검증은 보류. |
| [SRS-FR-064](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:571>) Faction Tier 승격 조건에 연결 Territory 규모를 포함할 수 있어야 한다. 구체적인 최소 Tile 수는 서버 설정 대상이다. | L136 FR-042~044 MISSING | CONFIRMED | MISSING | E08,E00 | S | Title territory, 아군 표시 및 연결 territory 계산 없음. |
| [SRS-FR-065](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:580>) Nation 이상 Faction의 Border는 적대 Faction에 대해 통제되어야 한다. | L137 FR-045~046 MISSING | CONFIRMED | MISSING | E00 | S | Nation+ 국경 진입 제한·중립/동맹 통행 정책 없음. |
| [SRS-FR-066](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:583>) 정식 공격 권한이 없는 적대 Faction은 Nation 이상 Territory에 진입할 수 없어야 한다. | L137 FR-045~046 MISSING | CONFIRMED | MISSING | E00 | S | Nation+ 국경 진입 제한·중립/동맹 통행 정책 없음. |
| [SRS-FR-067](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:586>) Neutral Faction은 통행할 수 있어야 한다. | L137 FR-045~046 MISSING | CONFIRMED | MISSING | E00 | S | Nation+ 국경 진입 제한·중립/동맹 통행 정책 없음. |
| [SRS-FR-068](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:589>) Alliance Faction은 통행할 수 있어야 한다. | L137 FR-045~046 MISSING | CONFIRMED | MISSING | E00 | S | Nation+ 국경 진입 제한·중립/동맹 통행 정책 없음. |
| [SRS-FR-069](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:598>) 모든 Player에게 다음 정보를 항상 공개해야 한다. - Settlement 위치 - Settlement 생성 - Settlement 파괴 - Faction 이름 - … | L138 FR-047 CONFLICT | CONFIRMED | CONFLICT | E08,E10 | S | WorldObject.Draw가 타 세력 정착지를 미탐색/History에서 숨기고 CameraJumper도 차단한다. |
| [SRS-FR-070](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:609>) Vision 밖에서도 신규 Settlement 및 Settlement 소멸 상태를 갱신해야 한다. | L139 FR-048 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E09 | S | 목록 packet/cache 업데이트는 있다. 실제 원격 WorldObject 생성·소멸 및 authoritative 삭제 경로는 없다. 캐시 수신은 인게임 실시간 공개와 같지 않다. |
| [SRS-BR-007](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:612>) World Map 정보 은폐의 핵심 대상은 Caravan이다. | L140 FR-049 MISSING; L198 BR-011 충돌; L199 BR-012 미구현 | CONFIRMED | CONFLICT | E08,E10 | S | 비플레이어 WorldObject를 광범위하게 숨긴다. Caravan도 숨길 수 있지만 정책에 따른 selective detection은 아니다. 흑백 tile shader가 현재 구현됐다는 인용은 잘못이다. |
| [SRS-FR-071](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:619>) Settlement의 Vision Radius는 해당 Settlement의 Border Radius와 동일해야 한다. | L141 FR-050 PARTIAL | DOWNGRADE REQUIRED | MISSING | E08,E00 | S | Border와 같은 settlement Vision 생성 경로 없음. ApplyFogSync의 '2칸' 주석은 서버 vision 구현이 아니다. |
| [SRS-FR-072](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:622>) Caravan의 Vision은 구성 Pawn 중 Shooting이 가장 높은 Pawn을 기준으로 계산해야 한다. | L142 FR-051 MISSING | CONFIRMED | MISSING | E00,E08 | S | Caravan 최고 Shooting 기반 vision 계산 없음. |
| [SRS-FR-073](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:625>) Vision 정보는 Faction 단위로 공유해야 한다. | L143 FR-052~053 MISSING | CONFIRMED | MISSING | E00,E08 | S | Faction/Alliance vision 합집합과 서버 producer 없음. |
| [SRS-FR-074](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:628>) Alliance Faction끼리는 Vision 정보를 실시간 공유해야 한다. | L143 FR-052~053 MISSING | CONFIRMED | MISSING | E00,E08 | S | Faction/Alliance vision 합집합과 서버 producer 없음. |
| [SRS-FR-075](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:635>) Settlement가 아닌 일반 World Tile의 Caravan은 Scout 상태를 시작할 수 있어야 한다. | L144 FR-054~059 MISSING | CONFIRMED | MISSING | E00 | S | Scout state·이동 제한·bonus·해제 흐름 없음. |
| [SRS-FR-076](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:638>) Scout 상태 동안 Caravan은 이동할 수 없어야 한다. | L144 FR-054~059 MISSING | CONFIRMED | MISSING | E00 | S | Scout state·이동 제한·bonus·해제 흐름 없음. |
| [SRS-FR-077](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:641>) Scout 상태에서는 추가 Vision Bonus를 제공해야 한다. | L144 FR-054~059 MISSING | CONFIRMED | MISSING | E00 | S | Scout state·이동 제한·bonus·해제 흐름 없음. |
| [SRS-FR-078](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:644>) Scout 상태에는 최대 지속시간을 둘 필요가 없다. 사용자가 종료할 때까지 유지할 수 있어야 한다. | L144 FR-054~059 MISSING | CONFIRMED | MISSING | E00 | S | Scout state·이동 제한·bonus·해제 흐름 없음. |
| [SRS-FR-079](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:649>) Scout를 종료하면 설정된 Movement Lock 시간이 지나기 전까지 Caravan은 이동할 수 없어야 한다. | L144 FR-054~059 MISSING | CONFIRMED | MISSING | E00 | S | Scout state·이동 제한·bonus·해제 흐름 없음. |
| [SRS-FR-080](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:652>) Scout 상태에서 공격받으면 Scout를 즉시 종료하고 해당 Tile에서 전투를 진행해야 한다. | L144 FR-054~059 MISSING | CONFIRMED | MISSING | E00 | S | Scout state·이동 제한·bonus·해제 흐름 없음. |
| [SRS-FR-081](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:659>) Caravan은 적대적 Vision 안에서 Ambush를 시작할 수 없어야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-082](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:662>) Ambush 중 Caravan은 이동할 수 없어야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-083](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:665>) Ambush는 Caravan을 상대 Vision에서 확률적으로 숨겨야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-084](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:668>) Ambush Detection은 최소 다음 요소를 사용해야 한다. - Observer Caravan의 최고 Shooting - Ambushed Caravan의 전체 개체… | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-085](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:675>) Ambush Detection은 Faction별로 독립 판정해야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-086](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:678>) 한 Faction이 Ambushed Caravan을 발견했다고 해서 모든 Faction이 자동 발견해서는 안 된다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-087](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:681>) 한 Faction이 탐지에 성공하면 해당 Faction에는 Ambush 종료까지 Caravan을 계속 표시해야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-088](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:684>) 탐지 결과는 해당 Faction의 Alliance에도 공유해야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-FR-089](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:687>) Ambush 종료 후 즉시 다시 Ambush할 수 없도록 Cooldown을 적용해야 한다. | L145 FR-060~067 MISSING | CONFIRMED | MISSING | E00 | S | Ambush state/확률 detection 및 Faction 단위 상태 없음. |
| [SRS-BR-008](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:690>) Ambush는 전술 전투 Bonus를 제공하지 않는다. Ambush의 목적은 World Map상의 Caravan 은폐다. | L145 Ambush MISSING | CONFIRMED | MISSING | E00 | S | 전략 은폐 전용 Ambush와 bonus 없는 실제 흐름 미구현. |
| [SRS-FR-090](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:699>) 다른 Player의 Settlement에 평화적으로 진입하려면 Entry Request를 보내야 한다. | L146 FR-068~070 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E11,E12 | T06,S | 방문 carrier/기즈모/모달은 있다. owner routing spoof, Cancel/Accept race, 중복 요청 덮어쓰기와 static 단일 dialog 추적이 남아 완전 protocol 승인은 불가. |
| [SRS-FR-091](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:702>) Settlement Owner는 Entry Request를 수락하거나 거절할 수 있어야 한다. | L146 FR-068~070 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E11,E12 | T06,S | 방문 carrier/기즈모/모달은 있다. owner routing spoof, Cancel/Accept race, 중복 요청 덮어쓰기와 static 단일 dialog 추적이 남아 완전 protocol 승인은 불가. |
| [SRS-FR-092](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:705>) 방문 요청자는 Owner가 승인하기 전 Request를 취소할 수 있어야 한다. | L146 FR-068~070 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E11,E12 | T06,S | 방문 carrier/기즈모/모달은 있다. owner routing spoof, Cancel/Accept race, 중복 요청 덮어쓰기와 static 단일 dialog 추적이 남아 완전 protocol 승인은 불가. |
| [SRS-FR-093](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:708>) 취소된 Request는 이후 늦게 도착한 Accept로 다시 활성화되어서는 안 된다. | L146 FR-068~070 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E11,E12 | T06,S | 방문 carrier/기즈모/모달은 있다. owner routing spoof, Cancel/Accept race, 중복 요청 덮어쓰기와 static 단일 dialog 추적이 남아 완전 protocol 승인은 불가. |
| [SRS-FR-094](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:711>) 각 Request는 고유 Request ID 및 상태를 가져야 한다. | L146 FR-068~070 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E11,E12 | T06,S | 방문 carrier/기즈모/모달은 있다. owner routing spoof, Cancel/Accept race, 중복 요청 덮어쓰기와 static 단일 dialog 추적이 남아 완전 protocol 승인은 불가. |
| [SRS-FR-095](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:718>) Settlement Owner가 Offline이면 일반 Visit Request를 보낼 수 없어야 한다. | L147 FR-071~072 PARTIAL; L202 BR-015 일치 | DOWNGRADE REQUIRED | CONFLICT | E11 | T06 | known owner offline 정상 경로는 거절하지만 caller가 HostPlayerId를 지정하면 우회한다. |
| [SRS-FR-096](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:721>) Visit 버튼을 비활성화해야 한다. | L147 FR-071~072 PARTIAL | CONFIRMED | MISSING | E11,E12 | S | owner offline이어도 Visit gizmo가 활성화되는 생산 경로다. server 거절 응답이 버튼 비활성 요구를 대신하지 않는다. |
| [SRS-FR-097](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:724>) 마우스를 올렸을 때 Owner가 Offline이라는 사유를 Tooltip으로 알려야 한다. | L147 FR-071~072 PARTIAL | CONFIRMED | MISSING | E11,E12 | S | owner offline tooltip 구현이 없다. server 거절 메시지를 해당 UI requirement 완료로 세지 않는다. |
| [SRS-FR-098](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:731>) 방문이 승인되면 방문자는 Settlement Owner의 기존 Map에 진입해야 한다. | L148 FR-073~076 PARTIAL | DOWNGRADE REQUIRED | MISSING | E12,E00 | S | Accept 뒤 메시지/TODO뿐이다. 기존 맵 진입·원격 Pawn 제어 구현은 AtomicExecutor와 무관하다. |
| [SRS-FR-099](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:734>) 각 Player는 자신의 Pawn만 직접 조작할 수 있어야 한다. | L148 FR-073~076 PARTIAL | DOWNGRADE REQUIRED | MISSING | E12,E00 | S | Accept 뒤 메시지/TODO뿐이다. 기존 맵 진입·원격 Pawn 제어 구현은 AtomicExecutor와 무관하다. |
| [SRS-FR-100](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:737>) 방문자의 일반 Map Interaction은 Vanilla RimWorld와 유사한 수준으로 허용해야 한다. 이는 다음과 같은 행동을 시스템적으로 지나치게 차단하지 않는… | L148 FR-073~076 PARTIAL | DOWNGRADE REQUIRED | MISSING | E12,E00 | S | Accept 뒤 메시지/TODO뿐이다. 기존 맵 진입·원격 Pawn 제어 구현은 AtomicExecutor와 무관하다. |
| [SRS-BR-009](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:754>) 방문 Session과 전투 Session은 서로 완전히 다른 시스템으로 분리하지 않는다. | L149 FR-077 MISSING | CONFIRMED | MISSING | E00,E12 | S | 공동 Tactical session 없음. |
| [SRS-FR-101](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:757>) Peaceful Tactical Session에서 적대 행동이 발생하면 동일 Session을 유지한 채 Hostile 상태로 전환할 수 있어야 한다. | L149 FR-077 MISSING | CONFIRMED | MISSING | E00,E02 | S | 평화→적대 동일 Tactical session manager 없음. |
| [SRS-FR-102](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:764>) Peaceful Tactical Session에서는 모든 참가 Player가 Speed를 변경할 수 있어야 한다. | L150 FR-078 MISSING | CONFIRMED | MISSING | E00,E02 | S | 모든 참가자의 speed 명령 정렬/Last Input Wins 처리 없음. |
| [SRS-BR-010](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:767>) 시간 제어 충돌은 Last Input Wins 규칙을 사용한다. 예: - A가 3x - 이후 B가 Pause - 전체 Session → Pause | L204 BR-017 미구현 | CONFIRMED | MISSING | E00,E02 | S | 참가 speed command의 Last Input Wins ordering 없음. |
| [SRS-FR-103](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:780>) Hostile 상태에서는 Session Speed를 1x로 강제해야 한다. | L151 FR-079 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E02 | S | setter/pause guard는 존재하지만 CurrentCombatMode를 Hostile로 설정하는 생산 경로가 없다. 진입 당시 speed 강제까지 보장하지 않는다. |
| [SRS-FR-104](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:783>) Hostile 상태에서는 Pause를 비활성화해야 한다. | L151 FR-079 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E02 | S | setter/pause guard는 존재하지만 CurrentCombatMode를 Hostile로 설정하는 생산 경로가 없다. 진입 당시 speed 강제까지 보장하지 않는다. |
| [SRS-FR-105](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:786>) 전투가 종료되면 이전 Speed를 자동 복원할 필요는 없다. Player가 다시 Speed를 선택하도록 한다. | Gemini Matrix 독립 평가 없음 | INSUFFICIENT EVIDENCE | UNKNOWN | E02,E00 | S | 이전 speed 자동 복원은 필수가 아니다. 이 optional 정책을 신규 기능 MISSING으로 요구하지 않는다. 실제 전투 종료 생명주기가 없으므로 적용 검증은 보류한다. |
| [SRS-FR-106](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:795>) 하나의 Tactical Session은 복수 Faction 참가자를 지원해야 한다. 예: `A + 동맹 B vs C + 동맹 D` | L152 FR-080 MISSING; L148 본인 Pawn PARTIAL | CONFIRMED | MISSING | E00 | S | 복수 참가자·Pawn command owner 검증 및 remote replication 없음. |
| [SRS-FR-107](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:802>) 각 참가 Player는 자신의 Pawn만 조작한다. | L152 FR-080 MISSING; L148 본인 Pawn PARTIAL | CONFIRMED | MISSING | E00 | S | 복수 참가자·Pawn command owner 검증 및 remote replication 없음. |
| [SRS-BR-011](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:809>) 정식 War Declaration은 해당 Faction의 최고 작위 보유자만 수행할 수 있다. | L195 BR-008 수정 필요 | CONFIRMED | CONFLICT | E03,E04 | T04 | 최고 작위자 아닌 미인증 요청도 war 생성. authority 실제 반례. |
| [SRS-FR-108](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:812>) 선전포고 시 Target Faction을 지정해야 한다. | L153 FR-081~083 PARTIAL | CONFIRMED | PARTIAL | E04,E03 | T04 | target 지정/WarData 생성은 있다. 최고 작위자 인가가 없고 미인증 packet도 war를 생성한다. SRS에 별도 사유 입력 필수 요구는 없다. |
| [SRS-FR-109](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:815>) 선전포고 이후 WarPending 상태를 생성해야 한다. | L153 FR-081~083 PARTIAL | CONFIRMED | PARTIAL | E04,E03 | T04 | target 지정/WarData 생성은 있다. 최고 작위자 인가가 없고 미인증 packet도 war를 생성한다. SRS에 별도 사유 입력 필수 요구는 없다. |
| [SRS-FR-110](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:818>) WarPending Duration은 공격 Faction Tier를 기준으로 계산해야 한다. | L154 FR-084 CONFLICT; L155 FR-085 SATISFIED | CONFIRMED | CONFLICT | E04 | T02,T09 | 공격자 대신 방어자 Tier 사용. Tribe→Empire도 Pending 15552000틱이다. Tribe 0시간은 변경 가능한 초기 후보이며 현재 충족 상태가 아니다. |
| [SRS-FR-111](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:821>) Tier별 WarPending Duration은 서버 설정 가능해야 한다. 초기 Balance 후보: - Tribe: 0시간 - Minor Faction: 2시간 - C… | L154 FR-084 CONFLICT; L155 FR-085 SATISFIED | CONFIRMED | CONFLICT | E04 | T02,T09 | 공격자 대신 방어자 Tier 사용. Tribe→Empire도 Pending 15552000틱이다. Tribe 0시간은 변경 가능한 초기 후보이며 현재 충족 상태가 아니다. |
| [SRS-FR-112](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:838>) WarPending 중 공격자는 방어 Faction을 공격할 수 없어야 한다. | Gemini Matrix 독립 평가 누락 | INSUFFICIENT EVIDENCE | MISSING | E00,E04 | S | Pending 중 양쪽 공격 금지와 방어 territory 내 공격 Caravan 퇴거 로직 없음. |
| [SRS-FR-113](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:841>) WarPending 중 방어자 역시 공격자를 공격할 수 없어야 한다. | Gemini Matrix 독립 평가 누락 | INSUFFICIENT EVIDENCE | MISSING | E00,E04 | S | Pending 중 양쪽 공격 금지와 방어 territory 내 공격 Caravan 퇴거 로직 없음. |
| [SRS-FR-114](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:844>) WarPending 시작 시 방어자 Territory 안에 존재하는 공격 Faction Caravan을 즉시 퇴거시켜야 한다. | Gemini Matrix 독립 평가 누락 | INSUFFICIENT EVIDENCE | MISSING | E00,E04 | S | Pending 중 양쪽 공격 금지와 방어 territory 내 공격 Caravan 퇴거 로직 없음. |
| [SRS-FR-115](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:850>) WarPending Timer가 종료되면 정식 War 상태로 전환해야 한다. | L156 FR-086~089 PARTIAL | CONFIRMED | PARTIAL | E04 | S | Pending→Active timer 실제 구현 인정. 권한/올바른 duration/재시작 복원은 미충족. |
| [SRS-FR-116](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:857>) 선전포고를 받은 Faction 구성원에게 Letter 또는 Message를 제공해야 한다. 해당 알림에는 최소 다음 정보가 포함되어야 한다. - 공격 Faction - … | L156 FR-086~089 PARTIAL | CONFIRMED | PARTIAL | E04,E13 | S | Message를 허용하는 SRS이므로 'Letter 없음' 자체는 결함이 아니다. 양측 대상·남은 시간/예정시각과 재접속 전달 검증이 부족하다. |
| [SRS-FR-117](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:866>) 공격 Faction에도 선전포고가 정상적으로 처리되었다는 알림을 제공해야 한다. | L156 FR-086~089 PARTIAL | CONFIRMED | PARTIAL | E04,E13 | S | Message를 허용하는 SRS이므로 'Letter 없음' 자체는 결함이 아니다. 양측 대상·남은 시간/예정시각과 재접속 전달 검증이 부족하다. |
| [SRS-FR-118](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:873>) 전쟁 종료 후 동일 Faction에 다시 선전포고할 수 없는 Cooldown을 적용해야 한다. | L157 FR-090~093 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | Cooldown 기록·재선전 차단 메서드가 없다. L89 인용은 81줄 실제 파일을 벗어난다. |
| [SRS-FR-119](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:876>) 해당 Cooldown은 다른 Faction을 대상으로 한 선전포고에는 적용되지 않는다. | L157 FR-090~093 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | Cooldown 기록·재선전 차단 메서드가 없다. L89 인용은 81줄 실제 파일을 벗어난다. |
| [SRS-FR-120](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:885>) 최고 통치자의 War Declaration 없이 구성원이 타 Faction을 의도적으로 공격하면 두 Faction을 적대 관계로 전환해야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-121](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:888>) 해당 공격 Faction 전체에 Betrayer 결과를 적용해야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-BR-012](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:891>) 개별 Player의 행동이 Faction 전체에 정치적 책임을 발생시킬 수 있다. | L196 BR-009 일치 | DOWNGRADE REQUIRED | MISSING | E04 | T10 | Faction 문자열 notification만으로 정치 책임·betrayer 상태 반영을 입증하지 못한다. |
| [SRS-FR-122](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:898>) 정당한 공격 권한 없이 의도적으로 타 Faction을 공격한 Faction에는 Betrayer Status를 부여해야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-123](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:901>) Betrayer Faction의 Settlement를 World Map에서 식별할 수 있어야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-124](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:904>) Faction 이름 뒤에 `(배신자)`와 같은 식별 표시를 제공해야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-125](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:907>) Betrayer가 피해 Faction과 Alliance 관계였다면 두 Faction 사이 Alliance는 즉시 해제해야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-126](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:910>) Betrayer가 가진 다른 Faction과의 Alliance는 유지해야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-127](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:913>) 다른 Faction은 Betrayer Faction을 War Declaration 없이 공격할 수 있어야 한다. | L158 FR-094~098 SATISFIED; L196/207 BR-009/020 일치 | DOWNGRADE REQUIRED | MISSING | E04,E13 | T10 | RecordBetrayal은 콘솔+notification event stub이다. intent 감지·정치 상태·공격권·timer·client handler 없음. |
| [SRS-FR-128](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:920>) Betrayer Status는 설정된 기간이 지나면 자동 해제되어야 한다. | L159 FR-099~101 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | 자동 만료/피해자 해제/반복 연장 구현 없음. L175는 존재하지 않는다. |
| [SRS-FR-129](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:923>) 피해 Faction은 Betrayer Status를 조기에 해제할 수 있어야 한다. | L159 FR-099~101 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | 자동 만료/피해자 해제/반복 연장 구현 없음. L175는 존재하지 않는다. |
| [SRS-FR-130](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:926>) Betrayer 상태에서 추가 Betrayal이 발생하면 필요 경과시간을 증가시켜야 한다. 관련 값은 서버 설정 가능해야 한다. | L159 FR-099~101 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | 자동 만료/피해자 해제/반복 연장 구현 없음. L175는 존재하지 않는다. |
| [SRS-FR-131](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:935>) 적을 공격하다 발생한 일반 Friendly Fire는 Betrayer 판정을 발생시키지 않아야 한다. | L160 FR-102~104 MISSING | CONFIRMED | MISSING | E00,E04 | S | Intent/Friendly Fire/AoE filtering 미구현. 제안 currentJob 비교로 비행 중 projectile intent를 인증할 수 없다. |
| [SRS-FR-132](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:938>) 가능하다면 AoE도 실제 의도된 Target을 기준으로 판정해야 한다. 예: `Target = Enemy C → B가 폭발에 휘말림 → Betrayal 아님` 반면 B를… | L160 FR-102~104 MISSING | CONFIRMED | MISSING | E00,E04 | S | Intent/Friendly Fire/AoE filtering 미구현. 제안 currentJob 비교로 비행 중 projectile intent를 인증할 수 없다. |
| [SRS-CON-001](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:947>) 의도 기반 AoE 판정 구현 난도가 지나치게 높을 경우 모든 AoE를 Betrayal 판정에서 제외하는 Fallback을 허용한다. | L225 CON-001~007 완벽 준수 | DOWNGRADE REQUIRED | MISSING | E00 | S | 실제 의미는 intent AoE 난도 높을 때 전체 AoE 제외 fallback 허용. 처리 구현/선택은 없다. |
| [SRS-FR-133](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:971>) Faction Ruler는 다른 Faction에 Alliance Request를 보낼 수 있어야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-134](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:974>) 상대 Ruler는 이를 수락하거나 거절할 수 있어야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-135](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:977>) Alliance는 Faction 전체에 적용되어야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-136](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:980>) Alliance Faction은 Vision을 공유해야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-137](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:983>) Alliance Faction은 Territory를 자유 통행할 수 있어야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-138](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:986>) Alliance Settlement 방문도 자동 진입이 아니라 Entry Approval을 요구해야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-139](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:989>) Alliance 파기 후 재신청 Cooldown을 적용할 수 있어야 한다. | L162 동맹 등록 존재; Packet 표 alliance carrier | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10,S | PKT_AllianceAction carrier만 존재하며 Request/Accept/Break runtime handlers와 alliance registry 없음. |
| [SRS-FR-140](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:996>) Faction이 War에 진입하면 해당 Faction의 직접 Alliance는 자동 전쟁 참가 상태가 되어야 한다. | L206 BR-019 미구현 | CONFIRMED | MISSING | E00,E04 | S | 직접 동맹 1-Hop 참전/실제 Tile 진입 모델 없음. |
| [SRS-BR-013](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:999>) 자동 참전은 1-Hop까지만 적용한다. 예: `A ↔ B ↔ C` A와 C가 직접 Alliance가 아니면 A의 War로 C가 자동 참전하지 않는다. | L206 BR-019 미구현 | CONFIRMED | MISSING | E04,E14 | S | Alliance registry/직접 1-Hop 자동 참전 없음. |
| [SRS-FR-141](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1008>) Alliance 병력이 Tactical Battle에 실제 참여하려면 직접 해당 Tile에 진입해야 한다. | L206 BR-019 미구현 | CONFIRMED | MISSING | E00,E04 | S | 직접 동맹 1-Hop 참전/실제 Tile 진입 모델 없음. |
| [SRS-FR-142](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1015>) War 중인 Faction은 서로 평화협정을 제안할 수 있어야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-143](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1018>) 평화협정은 무조건 평화를 지원해야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-144](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1021>) 평화협정은 특정 물품을 조건으로 하는 조건부 평화를 지원해야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-145](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1024>) 조건부 평화는 Item 및 Quantity를 요구조건으로 사용할 수 있어야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-146](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1027>) 조건부 평화 수락 시 Vanilla Quest와 유사한 시간 제한 의무를 생성해야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-147](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1030>) 조건을 기한 내 충족하면 Peace를 유지해야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-148](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1033>) 조건을 이행하지 않으면 War 상태로 즉시 복귀해야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-149](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1036>) 조건 미이행으로 복귀한 War에는 재선전포고 Cooldown을 적용하지 않아야 한다. | L161 FR-105~109 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04 | T10 | ConcludeWar조차 없음. 협정·조건부 item obligation·자동 재개·cooldown 예외 미구현. |
| [SRS-FR-150](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1043>) 직접 Alliance로 War에 참가한 Faction도 적국과 평화협정을 체결할 수 있어야 한다. | L162 FR-110~111 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10 | 동맹 대리 평화/Primary와 AlliedParticipant 구분 없음. '영지 전멸 자동 종전'은 해당 SRS 번호의 문구가 아니다. |
| [SRS-FR-151](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1046>) 동맹이 체결한 평화협정은 Primary Faction의 본 전쟁까지 종료시킬 수 있어야 한다. 따라서 War 데이터는 최소 다음을 구분할 수 있어야 한다. - Prima… | L162 FR-110~111 PARTIAL | DOWNGRADE REQUIRED | MISSING | E04,E14 | T10 | 동맹 대리 평화/Primary와 AlliedParticipant 구분 없음. '영지 전멸 자동 종전'은 해당 SRS 번호의 문구가 아니다. |
| [SRS-FR-152](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1058>) 정당한 공격 권한이 있는 Caravan은 Settlement Owner의 승인 없이 침공할 수 있어야 한다. 정당한 공격 권한은 예를 들어 다음에서 발생한다. - 정식 … | L163 FR-112 MISSING | CONFIRMED | MISSING | E00,E12 | S | 합법 공격권으로 approval 없이 invasion하는 경로 없음. |
| [SRS-FR-153](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1071>) Settlement Owner가 Offline이어도 정당한 공격을 허용해야 한다. | L164 FR-113~118 MISSING | CONFIRMED | MISSING | E00,E12 | S | 오프라인 기존 map load·AI·결과 save·로그인 핸드오버 없음. FR-158에는 CON-002 명시 fallback이 있으나 공격 금지는 대안이 아니다. |
| [SRS-FR-154](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1074>) Offline Defender의 Pawn은 AI가 대신 제어해야 한다. | L164 FR-113~118 MISSING | CONFIRMED | MISSING | E00,E12 | S | 오프라인 기존 map load·AI·결과 save·로그인 핸드오버 없음. FR-158에는 CON-002 명시 fallback이 있으나 공격 금지는 대안이 아니다. |
| [SRS-FR-155](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1077>) Offline Combat 결과는 실제 Settlement 상태에 영구 반영되어야 한다. 포함: - Pawn 사망 - Pawn 부상 - Building 파괴 - Item… | L164 FR-113~118 MISSING | CONFIRMED | MISSING | E00,E12 | S | 오프라인 기존 map load·AI·결과 save·로그인 핸드오버 없음. FR-158에는 CON-002 명시 fallback이 있으나 공격 금지는 대안이 아니다. |
| [SRS-FR-156](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1090>) Offline Owner가 이후 접속하면 Settlement가 공격받았다는 Letter를 표시해야 한다. 상세 전투 Report까지 제공할 필요는 없다. | L164 FR-113~118 MISSING | CONFIRMED | MISSING | E00,E12 | S | 오프라인 기존 map load·AI·결과 save·로그인 핸드오버 없음. FR-158에는 CON-002 명시 fallback이 있으나 공격 금지는 대안이 아니다. |
| [SRS-FR-157](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1099>) Offline Defender가 전투 도중 접속할 경우 가능하면 AI Control을 Player Control로 전환해야 한다. | L164 FR-113~118 MISSING | CONFIRMED | MISSING | E00,E12 | S | 오프라인 기존 map load·AI·결과 save·로그인 핸드오버 없음. FR-158에는 CON-002 명시 fallback이 있으나 공격 금지는 대안이 아니다. |
| [SRS-FR-158](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1102>) Player가 전투 도중 로그아웃하면 가능하면 AI가 Pawn 제어권을 인수해야 한다. | L164 FR-113~118 MISSING | CONFIRMED | MISSING | E00,E12 | S | 오프라인 기존 map load·AI·결과 save·로그인 핸드오버 없음. FR-158에는 CON-002 명시 fallback이 있으나 공격 금지는 대안이 아니다. |
| [SRS-CON-002](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1105>) FR-158 구현이 지나치게 어려운 경우 해당 Pawn을 무조작 상태로 두는 Fallback을 허용할 수 있다. | L225 CON-001~007 완벽 준수 | DOWNGRADE REQUIRED | MISSING | E00 | S | 실제 의미는 FR-158 offline 이탈 Pawn 무조작 fallback 허용. 해당 tactical lifecycle 없음. |
| [SRS-FR-159](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1112>) 전투 후퇴는 가능한 한 Vanilla RimWorld 규칙을 따라야 한다. | L165 FR-119~120 MISSING | CONFIRMED | MISSING | E00 | S | Remote battle retreat/승패/Caravan 재구성 및 결과 authority 없음. |
| [SRS-FR-160](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1115>) 공격자가 Map 가장자리로 후퇴할 수 있어야 한다. | L165 FR-119~120 MISSING | CONFIRMED | MISSING | E00 | S | Remote battle retreat/승패/Caravan 재구성 및 결과 authority 없음. |
| [SRS-FR-161](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1118>) 생존 공격 Pawn은 후퇴 후 Caravan으로 재구성되어야 한다. | L165 FR-119~120 MISSING | CONFIRMED | MISSING | E00 | S | Remote battle retreat/승패/Caravan 재구성 및 결과 authority 없음. |
| [SRS-FR-162](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1121>) Victory 판정은 가능한 한 Vanilla RimWorld의 적대 Entity 제거 기준을 따라야 한다. | L165 FR-119~120 MISSING | CONFIRMED | MISSING | E00 | S | Remote battle retreat/승패/Caravan 재구성 및 결과 authority 없음. |
| [SRS-FR-163](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1133>) Occupy 전 공격자의 SettlementLimit을 확인해야 한다. | L166 FR-121~122 MISSING | CONFIRMED | MISSING | E00,E06 | S | Occupy/Destroy 선택·한도 초과 점령 차단 없음. |
| [SRS-FR-164](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1136>) SettlementLimit을 초과하는 경우 Occupy를 선택할 수 없어야 한다. | L166 FR-121~122 MISSING | CONFIRMED | MISSING | E00,E06 | S | Occupy/Destroy 선택·한도 초과 점령 차단 없음. |
| [SRS-FR-165](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1139>) Occupy 시 Settlement Owner를 승자 Player로 변경해야 한다. | L166 FR-121~122 MISSING | CONFIRMED | MISSING | E00,E06 | S | Occupy/Destroy 선택·한도 초과 점령 차단 없음. |
| [SRS-FR-166](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1142>) 점령 시 다음 Entity Ownership을 새 Owner에 맞게 변경해야 한다. - Pawn - Animal - Building - Item - 기타 Settleme… | L167 FR-123 SATISFIED; L238/389 100% rollback | DOWNGRADE REQUIRED | PARTIAL | E06,E07 | T03,S | local SetFaction 및 snapshot helper는 있지만 items/holders/player owner/layer가 빠지고 durable save와 서버 commit이 분리된다. 완전 원자 양도는 미충족. |
| [SRS-NFR-002](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1151>) Ownership Transfer는 원자적으로 수행되어야 한다. 부분 변경 상태를 남겨서는 안 된다. | L221 NFR-002 완벽; L167 원자 양도 SATISFIED | DOWNGRADE REQUIRED | CONFLICT | E06,E07 | T03,S | runtime 일부분 보상 rollback ≠ durable 원자 ownership. 전체 entity 범위 및 server/client repair state 부재. |
| [SRS-FR-167](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1160>) 승자가 Destroy를 선택하면 공격 Caravan을 먼저 구성할 수 있어야 한다. | L168 FR-124~126 MISSING | CONFIRMED | MISSING | E00 | S | 파괴·제거·ruins/expiry 및 server topology 변경 없음. |
| [SRS-FR-168](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1163>) 공격 Caravan이 Settlement에서 출발하면 Settlement를 제거해야 한다. | L168 FR-124~126 MISSING | CONFIRMED | MISSING | E00 | S | 파괴·제거·ruins/expiry 및 server topology 변경 없음. |
| [SRS-FR-169](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1166>) Settlement 제거와 동시에 해당 Border를 제거해야 한다. | L168 FR-124~126 MISSING | CONFIRMED | MISSING | E00 | S | 파괴·제거·ruins/expiry 및 server topology 변경 없음. |
| [SRS-FR-170](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1169>) 파괴된 위치에는 임시 Ruins Site를 생성해야 한다. | L168 FR-124~126 MISSING | CONFIRMED | MISSING | E00 | S | 파괴·제거·ruins/expiry 및 server topology 변경 없음. |
| [SRS-FR-171](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1172>) Ruins Site는 설정된 시간이 지나면 제거해야 한다. | L168 FR-124~126 MISSING | CONFIRMED | MISSING | E00 | S | 파괴·제거·ruins/expiry 및 server topology 변경 없음. |
| [SRS-BR-014](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1179>) Settlement가 없다는 사실만으로 Faction이 소멸해서는 안 된다. | L208/209 BR-021/022 수정 필요 | CONFIRMED | MISSING | E00 | S | Faction 생존/Caravan 잔존 판정 모델 없음. |
| [SRS-FR-172](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1182>) Settlement가 0이어도 Caravan이 존재하면 Faction은 유지해야 한다. | L169 FR-127~128 MISSING | CONFIRMED | MISSING | E00 | S | Caravan 잔존 기반 Faction 생존과 자산 변화 tier 재평가 없음. |
| [SRS-FR-173](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1185>) Settlement를 잃으면 Faction 규모를 다시 평가하여 Tier를 변경할 수 있어야 한다. | L169 FR-127~128 MISSING | CONFIRMED | MISSING | E00 | S | Caravan 잔존 기반 Faction 생존과 자산 변화 tier 재평가 없음. |
| [SRS-FR-174](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1197>) 최고 통치자의 Caravan이 살아 있다면 Faction을 즉시 해체해서는 안 된다. | L170 FR-129~132 MISSING | CONFIRMED | MISSING | E00 | S | branch split·신규 Faction·생존자 King 공동 transaction 없음. |
| [SRS-FR-175](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1200>) 최고 통치 Branch가 완전히 제거된 경우 생존 Feudal Branch를 추출해야 한다. | L170 FR-129~132 MISSING | CONFIRMED | MISSING | E00 | S | branch split·신규 Faction·생존자 King 공동 transaction 없음. |
| [SRS-FR-176](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1203>) 각 최고 생존 Branch를 독립 Faction으로 전환해야 한다. | L170 FR-129~132 MISSING | CONFIRMED | MISSING | E00 | S | branch split·신규 Faction·생존자 King 공동 transaction 없음. |
| [SRS-FR-177](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1206>) 같은 Branch 아래의 하위 Vassal은 함께 유지해야 한다. | L170 FR-129~132 MISSING | CONFIRMED | MISSING | E00 | S | branch split·신규 Faction·생존자 King 공동 transaction 없음. |
| [SRS-FR-178](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1209>) 각 분리 Faction의 자산을 기준으로 Tier를 다시 계산해야 한다. | L170 FR-129~132 MISSING | CONFIRMED | MISSING | E00 | S | branch split·신규 Faction·생존자 King 공동 transaction 없음. |
| [SRS-FR-179](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1212>) 조건을 만족한 최고 생존 귀족은 새 King이 될 수 있어야 한다. | L170 FR-129~132 MISSING | CONFIRMED | MISSING | E00 | S | branch split·신규 Faction·생존자 King 공동 transaction 없음. |
| [SRS-BR-015](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1225>) Tax는 Direct Superior가 Direct Vassal에게만 부과할 수 있다. King이 자신의 Duke 아래에 있는 Count에게 직접 Tax를 설정해서는 안… | L193 BR-006 정면 충돌 | CONFIRMED | MISSING | E05,E06 | S | Direct Superior/Vassal 인가 없음. Count helper dormant 조건과 live collection 구현 부재를 구분한다. |
| [SRS-FR-180](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1234>) Superior는 Direct Vassal에게 반복 Tax Policy를 설정할 수 있어야 한다. Tax Policy는 최소 다음 정보를 포함한다. - Target It… | L171 FR-133~135 CONFLICT | CONFIRMED | MISSING | E05,E06 | S | Tax policy/Direct Superior→Direct Vassal tree 인가 없음. Count helper는 dormant 충돌로서 실제 세금 권한 endpoint는 아니다. |
| [SRS-FR-181](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1247>) Vassal은 자신의 Tax Policy를 확인할 수 있어야 한다. | L171 FR-133~135 CONFLICT | CONFIRMED | MISSING | E05,E06 | S | Tax policy/Direct Superior→Direct Vassal tree 인가 없음. Count helper는 dormant 충돌로서 실제 세금 권한 endpoint는 아니다. |
| [SRS-FR-182](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1250>) Vassal은 최소 다음 정보를 미리 확인할 수 있어야 한다. - 요구 Item - 요구 수량 - 다음 징수 가능 시점 | L171 FR-133~135 CONFLICT | CONFIRMED | MISSING | E05,E06 | S | Tax policy/Direct Superior→Direct Vassal tree 인가 없음. Count helper는 dormant 충돌로서 실제 세금 권한 endpoint는 아니다. |
| [SRS-BR-016](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1261>) Tax Cycle은 예정일이 아니라 마지막 실제 징수일 기준으로 다시 계산한다. 예: - Cycle: 10일 - 최초 징수 가능: Day 10 - 실제 징수: Day 1… | L174 FR-143~144 CONFLICT | CONFIRMED | MISSING | E06 | T07 | 실제 징수 후 cycle reset이 없고 deadline만 있다. |
| [SRS-FR-183](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1275>) Tax Collection은 실제 Tax Caravan이 Settlement에 도착했을 때만 실행할 수 있어야 한다. | L172 FR-136~138 CONFLICT | CONFIRMED | MISSING | E06 | T07 | 실제 tax caravan/arrival/inventory collection이 없다. deadline은 자동 징수가 아니라 자동 체납을 만든다. |
| [SRS-FR-184](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1278>) Tax Caravan 도착 시 일반 Visit 이외에 `세금 징수` 행동을 제공해야 한다. | L172 FR-136~138 CONFLICT | CONFIRMED | MISSING | E06 | T07 | 실제 tax caravan/arrival/inventory collection이 없다. deadline은 자동 징수가 아니라 자동 체납을 만든다. |
| [SRS-FR-185](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1281>) Tax Collection은 Settlement Map에 직접 들어가지 않고 Trade와 유사한 UI로 수행해야 한다. | L172 FR-136~138 CONFLICT | CONFIRMED | MISSING | E06 | T07 | 실제 tax caravan/arrival/inventory collection이 없다. deadline은 자동 징수가 아니라 자동 체납을 만든다. |
| [SRS-FR-186](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1284>) Tax Collection에는 Visit Approval이 필요하지 않다. | L172 FR-136~138 CONFLICT | CONFIRMED | MISSING | E06 | T07 | 실제 tax caravan/arrival/inventory collection이 없다. deadline은 자동 징수가 아니라 자동 체납을 만든다. |
| [SRS-FR-187](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1287>) Offline Settlement에도 Tax Collection을 수행할 수 있어야 한다. | L172 FR-136~138 CONFLICT | CONFIRMED | MISSING | E06 | T07 | 실제 tax caravan/arrival/inventory collection이 없다. deadline은 자동 징수가 아니라 자동 체납을 만든다. |
| [SRS-FR-188](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1306>) 지정 Item이 부족하면 가능한 수량을 우선 징수할 수 있어야 한다. | L173 FR-139~142 PARTIAL | DOWNGRADE REQUIRED | MISSING | E06 | S | 지정 item 수량 차감조차 없다. PaidResources 불검증 boolean 처리이며 line258은 transfer 결과 검증이다. |
| [SRS-FR-189](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1309>) 부족 Quantity는 징수 시점의 해당 Item Vanilla Market Value로 환산해야 한다. | L173 FR-139~142 PARTIAL | DOWNGRADE REQUIRED | MISSING | E06 | S | 지정 item 수량 차감조차 없다. PaidResources 불검증 boolean 처리이며 line258은 transfer 결과 검증이다. |
| [SRS-FR-190](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1312>) Tax Collector는 해당 부족 Value 이하의 다른 자산을 강제로 선택하여 징수할 수 있어야 한다. | L173 FR-139~142 PARTIAL | DOWNGRADE REQUIRED | MISSING | E06 | S | 지정 item 수량 차감조차 없다. PaidResources 불검증 boolean 처리이며 line258은 transfer 결과 검증이다. |
| [SRS-BR-017](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1315>) 대체 납부 Item 선택권은 납세 Vassal이 아니라 징수자에게 있다. | L211 BR-024 미구현(가치 한도) | CONFIRMED | MISSING | E06 | S | SRS-BR-017은 대체 품목 선택권=징수자다. 가치 한도 자체는 SRS-FR-189/191이며 둘 다 미구현. |
| [SRS-FR-191](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1322>) Tax의 강제징수 대상은 조건을 만족하면 다음을 포함할 수 있어야 한다. - Item - Animal - Slave - Pawn - 기타 Vanilla Market Va… | L173 FR-139~142 PARTIAL | DOWNGRADE REQUIRED | MISSING | E06 | S | 지정 item 수량 차감조차 없다. PaidResources 불검증 boolean 처리이며 line258은 transfer 결과 검증이다. |
| [SRS-FR-192](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1337>) Tax Caravan의 실제 징수 시도 후 미징수 금액이 남으면 Tax Delinquent 상태를 생성해야 한다. | L174 FR-143~144 CONFLICT; L175 FR-145~148 CONFLICT | CONFIRMED | CONFLICT | E06 | T07 | 미도착 deadline만으로 체납, Settlement별 key 및 count 기록. Player별 누적 부족 가치/실제 징수일 기준 cycle 아님. |
| [SRS-FR-193](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1340>) Delinquency는 Settlement가 아니라 Player 단위로 관리해야 한다. | L174 FR-143~144 CONFLICT; L175 FR-145~148 CONFLICT | CONFIRMED | CONFLICT | E06 | T07 | 미도착 deadline만으로 체납, Settlement별 key 및 count 기록. Player별 누적 부족 가치/실제 징수일 기준 cycle 아님. |
| [SRS-FR-194](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1343>) 미납 Value를 누적해야 한다. | L175 FR-145~148 CONFLICT | CONFIRMED | MISSING | E06,E00 | S | ConsecutiveDelinquentCount만 있고 Player별 누적 미납 Value 모델이 없다. |
| [SRS-FR-195](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1346>) 다음 징수 시 기존 체납 Value를 추가 징수 가능액에 포함해야 한다. 예: 현재 Tax + 누적 Delinquency | L175 FR-145~148 CONFLICT | CONFIRMED | MISSING | E06,E00 | S | 다음 실제 징수 시 현재 Tax에 누적 체납 Value를 합치는 collection 경로가 없다. |
| [SRS-FR-196](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1353>) 누적 체납이 커지면 이전에는 Value 한도 때문에 징수할 수 없던 고가 자산도 징수할 수 있어야 한다. | L175 FR-145~148 CONFLICT | CONFIRMED | MISSING | E06,E00 | S | 누적 체납 Value로 이전 고가 자산을 징수 가능하게 하는 실제 선택/차감 로직이 없다. |
| [SRS-BR-018](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1356>) Tax Caravan이 방문하지 않았다는 사실만으로 체납을 생성해서는 안 된다. | L210 BR-023 정면 충돌 | CONFIRMED | CONFLICT | E06 | T07 | Tax Caravan 미도착인데 deadline으로 체납 생성이 재현됨. |
| [SRS-FR-197](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1370>) 각 Settlement는 독립적인 Auto Shop 설정을 가질 수 있어야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-198](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1373>) Player는 Settlement별 Sell Order를 설정할 수 있어야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-199](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1376>) Player는 Settlement별 Buy Order를 설정할 수 있어야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-200](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1379>) Item 지정 UI는 가능한 한 Vanilla RimWorld의 Item Filter 및 거래 UX를 따라야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-201](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1382>) Player는 거래 가격을 자유롭게 설정할 수 있어야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-BR-019](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1385>) Player 간 거래 가격에는 시스템적인 최소/최대 가격 제한을 두지 않는다. | L212 BR-025 일치 | DOWNGRADE REQUIRED | MISSING | E00,E14 | S | P2P order/price 모델 없음. 가격 제한이 없다는 부재만으로 실거래 자유가격 기능의 충족을 판정하지 않는다. |
| [SRS-FR-202](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1392>) Auto Shop 등록 시 Item 재고를 예약하지 않아야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-203](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1395>) Buy Order 등록 시 Silver를 예약하지 않아야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-204](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1398>) 거래 시점의 실제 Settlement Inventory를 기준으로 판매 가능 수량을 계산해야 한다. 예: 등록 100 실제 재고 30 → Buyer에게 30만 표시. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-205](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1408>) Buy Order는 거래 시점에 실제 존재하는 Silver 범위까지만 체결해야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-206](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1415>) Settlement Owner가 Offline이어도 Auto Shop은 동작해야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-207](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1418>) 구매 Item은 거래 완료 즉시 Buyer Caravan에 반영해야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-208](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1421>) 판매 대금 또는 매입 Item은 Settlement Inventory에 즉시 반영해야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-209](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1424>) Offline 중 발생한 거래는 Owner에게 각각 별도 Letter로 알려야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-210](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1427>) Letter 클릭 시 거래 결과 Item이 Spawn된 위치로 Camera를 이동시켜야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-211](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1434>) Settlement Owner가 Online이어도 Auto Shop을 사용할 수 있어야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-212](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1437>) Online Player끼리는 별도로 Vanilla RimWorld식 직접 Barter 거래도 할 수 있어야 한다. | L176 FR-149~159 MISSING; L212 BR-025 자유가격 일치 | CONFIRMED | MISSING | E00,E14 | S | P2P shop order/price/inventory/purchase carrier와 구현 없음. 자유 가격 필드가 있다는 주장은 실제 모델에 없다. |
| [SRS-FR-213](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1444>) NPC Market 상태는 다음 Key 단위로 독립 관리해야 한다. `NPC Settlement + Item Def` | L177 FR-160~164 SATISFIED | DOWNGRADE REQUIRED | CONFLICT | E15,E16 | T11,T12,T13 | 정착지/품목별 dictionary는 있지만 key concatenation이 서로 다른 두 쌍을 같은 market으로 합친다. REC-05는 독립 관리 invariant 위반을 재현한다. |
| [SRS-FR-214](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1449>) 한 Player가 발생시킨 시장 변화는 이후 모든 Player에게 동일하게 적용되어야 한다. | L177 FR-160~164 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E15,E16 | T11,T12,T13 | NPC market cache/매입·매출 carrier와 후킹 존재. client report 신뢰·replay/음수·복합 key collision 및 실제 transaction 증명이 없다. |
| [SRS-FR-215](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1452>) NPC Settlement에서 특정 Item이 대량 구매되면 해당 Item 판매 가격을 지수적으로 상승시켜야 한다. | L177 FR-160~164 SATISFIED; L255 Math.Exp | DOWNGRADE REQUIRED | CONFLICT | E15 | S | buy는 Math.Pow(1-stockRatio,2)*1.5 가산식, sale은 선형 stockRatio 차감이다. 지수 가격 충격 주장/요구 충족 판정은 성립하지 않는다. |
| [SRS-FR-216](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1455>) NPC Settlement에 특정 Item이 대량 판매되면 해당 Item 매입 가격을 지수적으로 하락시켜야 한다. | L177 FR-160~164 SATISFIED; L255 Math.Exp | DOWNGRADE REQUIRED | CONFLICT | E15 | S | buy는 Math.Pow(1-stockRatio,2)*1.5 가산식, sale은 선형 stockRatio 차감이다. 지수 가격 충격 주장/요구 충족 판정은 성립하지 않는다. |
| [SRS-FR-217](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1458>) 가격은 World Time 경과에 따라 Vanilla Base Price 방향으로 서서히 회귀해야 한다. | L177 FR-160~164 SATISFIED | DOWNGRADE REQUIRED | PARTIAL | E15,E16 | T15,T16 | model lock·snapshot·단계적 기본가 회귀는 인정. 설정 불가·초기 tick 및 market join sync/영속 상태 부재. 실제 경제 transaction 통과가 아니다. |
| [SRS-FR-218](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1461>) 관련 계수는 서버 설정으로 변경 가능해야 한다. | L177 FR-160~164 SATISFIED | DOWNGRADE REQUIRED | MISSING | E15,E16 | T15,T16 | 가격 계수/decay/clamp가 상수이고 external config loader가 없다. lock/decay 구현은 설정 변경 요구의 부분 완료 증거가 아니다. |
| [SRS-FR-219](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1464>) NPC Inventory Restock은 가능한 한 Vanilla RimWorld의 기존 Restock Mechanism을 유지해야 한다. | L178 FR-165 SATISFIED | INSUFFICIENT EVIDENCE | PARTIAL | E15,E16 | S | 바닐라 inventory restock 직접 패치 없음은 인정하나 shadow stock은 ±1 임의 보충한다. 실제 stock과 독립 가격 모델의 일치·엔진 restock 회귀 미검증. |
| [SRS-FR-220](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1471>) WarEconomy 주요 기능은 하나의 통합 관리 창을 통해 접근할 수 있어야 한다. | L179 FR-166~172 MISSING; L132 tree UI MISSING | CONFIRMED | MISSING | E00,E12 | S | 통합 main window/탭/tree 관리와 행동 UI 없음. |
| [SRS-FR-221](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1474>) 기능이 지나치게 많은 독립 MainTab으로 분산되지 않도록 해야 한다. | L179 FR-166~172 MISSING; L132 tree UI MISSING | CONFIRMED | MISSING | E00,E12 | S | 통합 main window/탭/tree 관리와 행동 UI 없음. |
| [SRS-FR-222](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1477>) 통합 Window 내부는 필요한 경우 Tab 또는 이에 준하는 명확한 Navigation 구조를 사용해야 한다. 논리적 영역 예: - Overview - Faction … | L179 FR-166~172 MISSING; L132 tree UI MISSING | CONFIRMED | MISSING | E00,E12 | S | 통합 main window/탭/tree 관리와 행동 UI 없음. |
| [SRS-FR-223](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1494>) Faction 관리 UI에서 최소 다음 정보를 확인할 수 있어야 한다. - Faction Tier - Tier Progress - 최고 통치자 - 구성원 - 각 구성원의… | L179 FR-166~172 MISSING; L132 tree UI MISSING | CONFIRMED | MISSING | E00,E12 | S | 통합 main window/탭/tree 관리와 행동 UI 없음. |
| [SRS-FR-224](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1507>) Tier 조건은 추상적 Progress Bar만이 아니라 실제 숫자를 표시해야 한다. 예: - Settlement: 3 / 4 - Wealth: 120000 / 1500… | L127 FR-017~018 MISSING | CONFIRMED | MISSING | E00 | S | 승격 1회 개명·skip 보존·정확한 진행도 UI 없음. |
| [SRS-FR-225](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1516>) Feudal Hierarchy는 Tree UI로 시각화할 수 있어야 한다. | L179 FR-166~172 MISSING; L132 tree UI MISSING | CONFIRMED | MISSING | E00,E12 | S | 통합 main window/탭/tree 관리와 행동 UI 없음. |
| [SRS-FR-226](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1519>) 관련 관리 권한이 있는 Player는 해당 UI에서 필요한 관리 행동을 실행할 수 있어야 한다. | L179 FR-166~172 MISSING; L132 tree UI MISSING | CONFIRMED | MISSING | E00,E12 | S | 통합 main window/탭/tree 관리와 행동 UI 없음. |
| [SRS-FR-227](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1526>) 일반 Event Notification은 별도 Event Log UI보다 Vanilla Letter/Message 체계를 우선 사용해야 한다. | L179 FR-166~172 MISSING | UPGRADE JUSTIFIED | PARTIAL | E13,E12 | S | 기존 war/tax/visit Messages가 있어 모든 알림이 전무하다는 평가는 과하다. 전체 정치/경제 통지는 없다. |
| [SRS-FR-228](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1529>) Offline Trade는 거래별 Letter를 생성해야 한다. | L179 FR-166~172 MISSING | CONFIRMED | MISSING | E00 | S | Offline Trade별 별도 Letter 생성 경로가 없다. 전체 P2P 거래도 미구현이다. |
| [SRS-FR-229](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1532>) Offline Attack은 공격받았다는 Letter를 생성해야 한다. 상세 전투 Report는 필수 요구가 아니다. | L179 FR-166~172 MISSING | CONFIRMED | MISSING | E00 | S | Offline Attack 통지 Letter가 없다. 상세 전투 Report는 필수가 아니므로 추가 요구하지 않는다. |
| [SRS-FR-230](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1541>) Server Administrator는 Console에서 Player를 Kick할 수 있어야 한다. | L180 FR-173~176 MISSING | CONFIRMED | MISSING | E17 | S | 콘솔은 quit/exit/status만 있다. permanent ID kick/ban, 저장 audit 파일 없음. |
| [SRS-FR-231](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1544>) Server Administrator는 Console에서 Player를 Ban할 수 있어야 한다. | L180 FR-173~176 MISSING | CONFIRMED | MISSING | E17 | S | 콘솔은 quit/exit/status만 있다. permanent ID kick/ban, 저장 audit 파일 없음. |
| [SRS-FR-232](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1547>) Ban은 Player 영구 식별자를 기준으로 저장해야 한다. | L180 FR-173~176 MISSING | CONFIRMED | MISSING | E17 | S | 콘솔은 quit/exit/status만 있다. permanent ID kick/ban, 저장 audit 파일 없음. |
| [SRS-FR-233](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1550>) 게임 내 별도 Admin UI는 필수 요구사항이 아니다. | L180 운영 묶음 MISSING | UPGRADE JUSTIFIED | SATISFIED | E17,E00 | S | SRS-FR-233은 별도 관리자 UI가 필수 아님이라는 범위 제약이다. 관리자 UI 미구현을 missing feature로 처리하지 않는다. |
| [SRS-FR-234](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1557>) 서버는 주요 관리 및 게임 Event를 Audit Log로 남길 수 있어야 한다. 권장 기록 대상: - Player 접속/종료 - Kick/Ban - Faction 가입… | L180 FR-173~176 MISSING | CONFIRMED | MISSING | E17 | S | 콘솔은 quit/exit/status만 있다. permanent ID kick/ban, 저장 audit 파일 없음. |
| [SRS-CFG-001](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1586>) World Time Speed | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-002](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1589>) Tier Score Weight | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-003](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1592>) Tier Promotion Threshold | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-004](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1595>) Tier Demotion Threshold | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-005](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1598>) Demotion Grace Period | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-006](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1601>) Tier별 Border Radius | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-007](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1604>) Title별 Title Territory Radius | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-008](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1607>) Title별 SettlementLimit | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-009](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1610>) Tier별 허용 Title 수 | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-010](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1613>) Tier별 WarPending Duration | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-011](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1616>) PostWar Redeclaration Cooldown | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-012](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1619>) Alliance Reapplication Cooldown | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-013](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1622>) Betrayer Base Duration | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-014](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1625>) Repeated Betrayal Duration 증가 규칙 | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-015](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1628>) Scout Vision Bonus | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-016](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1631>) Scout Movement Lock Duration | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-017](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1634>) Ambush Detection Coefficient | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-018](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1637>) Ambush Movement Lock Duration | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-019](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1640>) Ambush Reuse Cooldown | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-020](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1643>) Tax 관련 기본 값 | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-021](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1646>) NPC Buy Pressure 계수 | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-022](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1649>) NPC Sell Pressure 계수 | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-023](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1652>) NPC Price Recovery Rate | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-024](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1655>) NPC Price Maximum/Minimum Modifier | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-025](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1658>) Ruins Site Duration | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-CFG-026](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1661>) 기타 향후 Balance Parameter | L227 CFG-001~026 전체 하드코딩 | DOWNGRADE REQUIRED | MISSING | E01,E04,E05,E06,E15,E17 | S | 외부 config loader 없음은 맞다. 일부는 상수/helper이고 많은 항목은 기능 자체가 미구현이므로 '26개 모두 구현된 하드코딩'은 틀리다. CFG-002~005 하위 문서 의미를 SRS 순서로 교정해야 한다. |
| [SRS-NFR-003](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1668>) 잘못된 Server Configuration 값이 서버 World 상태를 조용히 손상시켜서는 안 된다. 설정 Format과 잘못된 값 처리 방식은 Architecture… | L222 NFR-003(영속성; 실제 NFR-006); L227 CFG | REQUIREMENT-ID ERROR | MISSING | E17,E04,E15 | S | Canonical 의미는 invalid config로 world 손상 금지. config 로더/validation/실패 정책 없음. |
| [SRS-NFR-004](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1682>) Faction, Title, Settlement, Territory, War, Tax, Market 및 Ownership 상태는 서로 모순된 최종 상태를 가져서는 안 된… | L220 NFR-001 상태 일관성 | CONFIRMED | CONFLICT | E03,E06,E07 | T03,T04,T05 | ConcurrentDictionary는 서로 다른 aggregate의 최종 일관성을 보장하지 않는다. |
| [SRS-NFR-005](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1688>) 다음 작업은 부분 성공 상태를 허용하지 않아야 한다. - Settlement Transfer - Settlement Occupation - Faction Join - T… | L221 완벽 원자성 주장 | DOWNGRADE REQUIRED | CONFLICT | E06,E07 | T03,S | Join/Demotion/Expulsion/Split 없음, transfer pending 충돌·ACK/save crash window 존재. |
| [SRS-NFR-006](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1701>) 서버 재시작 이후에도 최소 다음 상태가 보존되어야 한다. - Player - Faction - Title - Feudal Tree - Settlement Ownershi… | L222 NFR-003 영속성 미구현 | CONFIRMED | MISSING | E17,E06,E04,E15 | S | 서버 world clock/Player/Faction/Tax/Market/War/Ban 저장·복원 및 pending journal 없음. |
| [SRS-NFR-007](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1723>) 서버 중앙 상태에 대해 둘 이상의 Client가 서로 다른 최종 결과를 확정할 수 없어야 한다. | L223 NFR-004 서버 중심 권한 확립 | DOWNGRADE REQUIRED | CONFLICT | E03,E06,E07 | T04,T05,T06 | 미인증 war, PlayerId spoof, client final-state result 신뢰. 서버 타이머 중심이라는 사실과 인증된 중앙 final authority는 다르다. |
| [SRS-NFR-008](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1729>) 하나의 Client Disconnect 또는 Crash가 Dedicated Server 전체를 정지시켜서는 안 된다. | L224 NFR-007 장애 격리 처리됨 | INSUFFICIENT EVIDENCE | PARTIAL | E18,E01 | S | 세션 cancellation/예외 격리 scaffolding은 있다. 느린 client·malformed payload·OOM·engine host crash 전체 fault matrix는 미실행. |
| [SRS-NFR-009](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1735>) UI는 기능 수에 비해 지나치게 난잡하지 않아야 한다. 주요 목표: - 가독성 - 일관성 - 최소 클릭 - 현재 상태 이해 - 행동 결과 예측 가능성 | Gemini Matrix 누락; L457 audit에 NFR-009 오인용 | INSUFFICIENT EVIDENCE | PARTIAL | E12,E00 | S | 기존 Dialog/Gizmo 존재. 통합 UI는 없고 화면 사용성은 이번 터미널 검증 범위 밖이다. |
| [SRS-NFR-010](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1749>) 기능적으로 적합한 경우 다음 RimWorld UX를 재사용해야 한다. - Letter - Message - Dialog - Gizmo - Float Menu - Trad… | Gemini Matrix 누락; L444 config에 NFR-010 오인용 | INSUFFICIENT EVIDENCE | PARTIAL | E12,E13,E16 | S | 실제 의미는 vanilla UX 재사용이며 Dialog/Gizmo/TradeUI/Message 활용은 인정한다. config 요구는 CFG/NFR-003이다. |
| [SRS-NFR-011](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1764>) Remote Tactical Player가 자신의 Pawn에게 명령할 때 실제 Multiplayer 게임으로 사용할 수 있는 수준의 반응성을 제공해야 한다. 정확한 La… | L342/369 prediction으로 충족 제안 | ARCHITECTURE ISSUE | MISSING | E00 | S | remote commands 없고 latency 목표도 PoC 이후 정해야 한다. 예측이나 10틱 snapshot 제안 자체는 측정 증거가 아니다. |
| [SRS-NFR-012](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1772>) 중요한 정치적/소유권 Event는 분쟁 발생 시 Server Operator가 추적할 수 있어야 한다. | L180 audit MISSING; Matrix 독립 항목 누락 | CONFIRMED | PARTIAL | E17,E06,E04 | S | 콘솔 사건 로그 일부 존재. durable audit와 분쟁 추적 가능한 authenticated event chain은 없다. |
| [SRS-CON-003](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1780>) 대상 게임 Version은 RimWorld 1.6이다. | L225 CON-001~007 완벽 준수 | INSUFFICIENT EVIDENCE | PARTIAL | E19 | S | net472 client의 설치 1.6 engine 참조/배포 존재. 이번 작업은 실제 게임 로드·모든 Harmony runtime 검증을 재실행하지 않았다. |
| [SRS-CON-004](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1783>) Client Mod는 RimWorld Client 환경에서 실행된다. | L225 CON-001~007 완벽 준수 | INSUFFICIENT EVIDENCE | PARTIAL | E19 | S | net472 client의 설치 1.6 engine 참조/배포 존재. 이번 작업은 실제 게임 로드·모든 Harmony runtime 검증을 재실행하지 않았다. |
| [SRS-CON-005](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1786>) 초기 운영에서는 Server Binary를 프로젝트 운영자만 보유한다. | L225 CON-001~007 완벽 준수 | INSUFFICIENT EVIDENCE | UNKNOWN | E19,E00 | S | operator-only server binary/Workshop client-only/초기 사용자 hosting 범위는 운영·배포 정책이다. 소스 구조만으로 완벽 준수 단정 불가. |
| [SRS-CON-006](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1789>) Steam Workshop에는 Client Mod만 배포하는 방향을 기본으로 한다. | L225 CON-001~007 완벽 준수 | INSUFFICIENT EVIDENCE | UNKNOWN | E19,E00 | S | operator-only server binary/Workshop client-only/초기 사용자 hosting 범위는 운영·배포 정책이다. 소스 구조만으로 완벽 준수 단정 불가. |
| [SRS-CON-007](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1792>) 일반 사용자가 Dedicated Server를 운영하는 기능은 초기 요구 범위가 아니다. | L225 CON-001~007 완벽 준수 | INSUFFICIENT EVIDENCE | UNKNOWN | E19,E00 | S | operator-only server binary/Workshop client-only/초기 사용자 hosting 범위는 운영·배포 정책이다. 소스 구조만으로 완벽 준수 단정 불가. |
| [SRS-CON-008](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1795>) Dedicated Server는 RimWorld Client와 분리된 프로세스로 운영하는 것을 기본으로 한다. | L226 CON-008~009 Tactical/Offline 미해결 | REQUIREMENT-ID ERROR | SATISFIED | E19,E17 | S | Canonical CON-008은 별도 Dedicated Server 프로세스다. 독립 net8 entry point로 충족. Remote 권한 모델의 Canonical 강제 ID로 사용하지 않는다. |
| [SRS-CON-009](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1798>) Server World Time과 Settlement Local Time은 서로 독립적이어야 한다. | L226 CON-008~009 Tactical/Offline 미해결; L117 clock SATISFIED | REQUIREMENT-ID ERROR | PARTIAL | E01,E02 | T01,S | Canonical CON-009은 dual clock 독립성이다. 분리 scaffold만 존재하며 session/presence와 calendar 경계 검증 필요. |
| [SRS-CON-010](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md:1856>) Offline Settlement Combat을 지원할 수 있는 Authority 구조가 최종 Architecture에 반드시 존재해야 한다. | L304 Offline risk(잘못된 CON-009) | ARCHITECTURE ISSUE | MISSING | E00,E12 | S | Offline Combat authority 반드시 존재해야 한다. 구조 결정을 기다리며 요구 축소 불가. |

### B.2 Gemini business rows and non-matrix assertions

아래는 Gemini 원문 번호를 보존한 대조표다. 비즈니스 규칙 25개 행과 matrix 밖의 완성도 주장을 모두 검토한다.

| Gemini source | Canonical target / QA disposition | Reason |
|---|---|---|
| L188 BR-001 일치 | BR-002 / DOWNGRADE REQUIRED | Single session field ≠ permanent single Faction membership |
| L189 BR-002 일치 | BR-003 / DOWNGRADE REQUIRED | Settlement title ≠ single Player title |
| L190 BR-003 수정 | BR-001, FR-021 / CONFIRMED | Tribe-only membership missing |
| L191 BR-004 missing | FR-022 / CONFIRMED | Founder King transaction missing |
| L192 BR-005 conflict | BR-004, FR-036~040 / CONFIRMED | Dormant helper conflict; live endpoint missing |
| L193 BR-006 conflict | BR-015, FR-051/180~182 / CONFIRMED | Direct relationship model missing; Count helper unused |
| L194 BR-007 missing | BR-005, FR-044~048 / CONFIRMED | Revocation/expulsion transaction missing |
| L195 BR-008 수정 | BR-011 / CONFIRMED | Unauthorized declaration reproduced |
| L196 BR-009 일치 | BR-012, FR-120/121 / DOWNGRADE REQUIRED | Event stub only |
| L197 BR-010 철학 일치 | FR-100/120/121 / INSUFFICIENT EVIDENCE | Philosophy is not executable compliance; permission and consequences missing |
| L198 BR-011 conflict | FR-069/070, BR-007 / CONFIRMED | Broad object hiding conflict |
| L199 BR-012 missing | BR-007, FR-072 / CONFIRMED | Selective caravan detection missing; some legacy broad hiding exists |
| L200 BR-013 missing | FR-073/074 / CONFIRMED | Vision sharing missing |
| L201 BR-014 수정 | BR-006, FR-059 / CONFIRMED | Priority implementation missing, not mature partial territory engine |
| L202 BR-015 일치 | FR-095~097 / DOWNGRADE REQUIRED | Offline refusal can be spoofed; UI incomplete |
| L203 BR-016 missing | FR-153~158/187/206 / CONFIRMED | Offline simulation/result/inventory authority missing |
| L204 BR-017 missing | BR-010, FR-102 / CONFIRMED | Last Input Wins missing |
| L205 BR-018 일치 | FR-103/104 / DOWNGRADE REQUIRED | Guard unreachable through real session lifecycle |
| L206 BR-019 missing | BR-013, FR-140/141 / CONFIRMED | One-Hop alliance missing |
| L207 BR-020 일치 | FR-127 / DOWNGRADE REQUIRED | CanDeclareWar method and Betrayer attack authorization do not exist |
| L208 BR-021 수정 | BR-014, FR-172/173 / CONFIRMED | Survival model missing |
| L209 BR-022 수정 | FR-172 / CONFIRMED | Caravan survival missing |
| L210 BR-023 conflict | BR-018 / CONFIRMED | No-arrival delinquency reproduced |
| L211 BR-024 missing | FR-189/191 / CONFIRMED | Value conversion/limit missing; collector choice additionally BR-017 |
| L212 BR-025 일치 | BR-019, FR-199~201 / DOWNGRADE REQUIRED | No P2P order model or free-price implementation |
| L25/233 높은 완성도 / 즉시 재사용 | NFR-002/004~007 etc / DOWNGRADE REQUIRED | C의 component별 제한 적용. 전체 모듈 승인 불가 |
| L58 diagram Diplomacy has alliances/cooldown/betrayer | FR-118~151 / DOWNGRADE REQUIRED | Actual 81-line manager lacks those state machines |
| L62 Client netstandard2.0 | CON-004 / DOWNGRADE REQUIRED | Client is net472; Common is netstandard2.0 |
| L80~99 Packet architecture | PARTIAL / DOWNGRADE REQUIRED | Framing/DTO family is real. Concluded transition, full alliance routing, host-only execute, unique TransferId guarantees and exponential price computation claims are false |
| L238 100% rollback | FR-166/NFR-002/005 / DOWNGRADE REQUIRED | Local compensating helper excludes scope/durability/repair |
| L241 perfect dual clock/hostile speed | FR-002/003/103/104 / DOWNGRADE REQUIRED | Separation scaffold real; session/presence/calendar authority incomplete |
| L244 main-thread dispatch prevents all NRE/reconnect interference | NFR-004/008 / DOWNGRADE REQUIRED | Dispatch pattern useful; old parser/queued work survive session boundary |
| L247 TradeHook immediate operation | FR-213~219 / INSUFFICIENT EVIDENCE | Hook existence confirmed, actual engine direction/count/report timing not independently exercised |
| L255 Math.Exp | FR-215/216 / DOWNGRADE REQUIRED | No Math.Exp in production; polynomial buy and linear sale |
| L258 100% Reliable delivery | NFR-004/008 / DOWNGRADE REQUIRED | Queue avoids ordinary bounded drops; no durable ACK/replay recovery after saturation disconnect/write failure/process crash |
| L261 precise180 TPS | FR-001/CFG-001 / INSUFFICIENT EVIDENCE | Target180 and short zero-client progress confirmed, sustained precision not certified; 1Hz WorldTickSync |

**필수 충돌 A~F의 후보 판정**

1. **AtomicFiefTransferExecutor:** 전체 ownership transaction은 **PARTIAL, architecture-blocked**다. SetFaction 대상 선제 추적, snapshot capture, 실패 상세 UI는 인정한다. 그러나 일반 item/contained inventory/world pawn/player ownership/layer 범위, save-before-ACK, durable pending/commit, collision rejection 및 repair journal이 없다. null 설정/claim 복원 검증과 destroyed thing 처리도 완전하지 않다. “100% 완성”을 취소하고 QA-003/004/005/012를 유지한다.
2. **Visit:** DTO/Gizmo/Dialog와 정상 경로의 offline 거절·disconnect cleanup 패턴은 재사용 후보다. Host lookup/인가, request uniqueness, terminal state, timeout/epoch 및 동시 다이얼로그 추적은 재설계한다. Remote map admission/session은 신규 구현이 필요하다. 승인 응답 수신만으로 실제 맵 진입 요구가 충족되지는 않는다.
3. **Dual Clock / Offline:** 접속자0의 server clock core는 확인했다. client world/local 분리는 partial이다. owner presence에 따른 일반 시뮬레이션 중지, tactical 예외, calendar/date 및 reconnect state는 미완성이다. 게임을 실행하지 않으면 tick하지 않는다는 설명만으로 FR-003을 PASS 처리할 수 없다.
4. **Betrayal:** RecordBetrayal notification stub는 reference 자산이다. intent 감지, Betrayer 정치 상태/기한/공격권, Alliance 관계 및 persistence는 **MISSING**이다. 이미 완성된 manager에 hook만 빠진 상태가 아니다.
5. **NPC Market:** lock/clone/decay와 cache adapter는 재사용 후보다. price pressure는 SRS에 맞게 다시 정의한다. report 인증, transaction ID/replay, 수량 경계, compound key, config 및 접속/재시작 동기화가 필요하다.
6. **Authority:** 실태는 메모리 기반 서버 타이머/목록과 클라이언트의 최종 map 변경이다. QA-001이 재현됐으며 NFR-007의 인증된 중앙 최종 권한은 성립하지 않는다. Tactical authority는 구현 자체가 없다.

**Cancel/Accept race의 정적 근거:** Response가 shared request의 Pending을 읽은 뒤 Cancel이 dictionary에서 제거하고 Cancelled로 바꿀 수 있다. 이후 Response가 이미 얻은 reference를 Accepted로 다시 쓰고 visitor에 보내는 순서가 가능하다. dictionary의 thread safety는 복합 상태 전이의 원자성을 보장하지 않는다. 이번 작업에서는 이 interleaving의 runtime scheduling 주입을 수행하지 않았으므로 실기 race 재현으로 보고하지 않는다.

### B.3 Gemini modification recommendations (all nine rows)

| Source/module | QA Verdict | Corrected scope |
|---|---|---|
| L271 Diplomacy | CONFIRMED | Attacker Tier/BR-011 인가 필요. Cooldown과 betrayal lifecycle은 기존 값을 config로 옮기는 작업이 아니라 신규 state machine이며 ADR 이후 |
| L272 WarDeclarationData | CONFIRMED | DefenderTierAtDeclaration 의미 교정 필요; wire/save schema migration·idempotency·tick unit 함께 설계 |
| L273 FactionTier helper | CONFIRMED | CFG-002 Weight/003 Promotion/004 Demotion/005 Grace로 교정; timer/caller/territory aggregation 신규 |
| L274 NobilityTitle | CONFIRMED | King-only, direct tax 규칙 교정 필요. helper 교체만으로 aggregate 권한 완료 아님 |
| L275 SettlementData | CONFIRMED | radius2와 Tier 국경 충돌. Graph/layer/precedence authority를 먼저 결정; getter만 바꾸면 안 됨 |
| L276 FeudalManager | CONFIRMED | 자동 체납 제거 방향은 맞음. arrival+actual collection+last successful cycle+Player value 모델과 함께 설계 |
| L277 TaxDelinquencyState | CONFIRMED | Player별 누적 가치 모델 필요. public setters/atomic multi-inventory 상태 검증 포함 |
| L278 WorldTimeConstants | CONFIRMED | CFG-001로 speed 외부화 방향 맞음. 게임 고정 시간 단위와 configurable speed 분리 |
| L279 Program/config/audit | CONFIRMED | 시작 config/validation, FR-230~232/234 운영 기능 필요. JSON와 live reload는 결정 후보, 필수 SRS가 아님 |

### B.4 Obsolete / conflicting classification

| Gemini removal claim | QA Verdict | Candidate disposition |
|---|---|---|
| L287 FogOfWarTileCache 전체 불필요 | DOWNGRADE REQUIRED | 이 cache로 정착지를 숨기는 정책은 폐기. Tile set/cache pattern은 Caravan vision/reference 자산으로 쓸 수 있어 파일 전체가 구조적으로 금지되는 것은 아님 |
| L289~292 Fog rendering 전면 교체 | CONFIRMED | 실제 충돌은 WorldObject.Draw와 camera 차단. Gemini가 지목한 WorldRenderer_RenderWorld/안개 WorldObjectsHolderTick renderer는 현재 파일에 없음. 광범위 은폐를 selective Caravan 정책으로 REPLACE; 유효성/BFS helper는 별도 평가 |
| L293 Letter camera patch 폐기 | CONFIRMED | 공개 정착지와 거래 알림 camera jump를 막는 blanket rule은 REPLACE. Generic jump UX adapter까지 금지하는 것은 아님 |
| L295 TacticalLockstepCommand enum 삭제 | INSUFFICIENT EVIDENCE | Enum-only 잔재는 cleanup/reference 대상. 명명 자체로 SRS 위반 또는 Map-owner 최종 선정의 근거는 아니다. Protocol ADR에서 wire compatibility/재사용 이름 결정 |

## C. Reusable Components

분류는 **현재 scope 그대로**에 대한 기준이다. `REUSE AFTER HARDENING`은 수정을 승인하는 명령이 아니며 선행 ADR과 acceptance test가 필요하다.

| Component / Gemini claim | Classification | Allowed reuse / required conditions |
|---|---|---|
| FactionTier / NobilityTitle 순수 enum 값 | **REUSE AS-IS** | 값 표현 carrier 한정. Title spelling/schema 호환은 ADR에서 확인; enum 존재는 membership/policy 완료 아님 |
| Vanilla hour/day tick conversion 상수 | **REUSE AS-IS** | 엔진 시간 단위 변환에 한정. WorldSpeed=3, prep hours, balance table까지 고정 재사용 아님 |
| AtomicFiefTransferExecutor 전체 (L236/389) | **REUSE AS TEST/REFERENCE ASSET ONLY** | pretracking/snapshot/collection ToList 패턴 참고. 현재 executor를 conquest transaction으로 연결하는 방식은 금지: full ownership scope/lease/save/journal/repair PoC 필요 |
| FeudalManager transfer coordinator | **REPLACE** | Global unique operation identity, epoch/version, durable prepare/commit/abort/repair, duplicate outcome, timeout/recovery 필요 |
| ClientWorldTickManager + TickPatches (L239) | **REUSE AFTER HARDENING** | accumulator/guard 패턴 인정. presence, canonical date/calendar, mode transition, reconnect reset, debt/lag policy 검증 |
| MainThreadQueue + NetworkClient (L242) | **REUSE AFTER HARDENING** | Main thread marshalling 재사용. parser per-epoch, queued epoch check, cache reset, connection/handshake distinction, client send serialization 필요 |
| TradePatches (L245) | **REUSE AFTER HARDENING** | Price/Trade UI adapter 재사용. 실제 1.6 trade direction/count timing과 unique settlement identity, authoritative transaction proof 확인 |
| VisitPatches / Dialog_VisitWait / Request (L248) | **REUSE AFTER HARDENING** | 보이는 UX scaffold 재사용. pending registry, multiple windows, cancellation finality, offline disabled state, real caravan arrival과 Tactical admission 연결 |
| Visit server lifecycle/authorization | **REPLACE** | Server-owned host lookup, auth session/ownership capability, unique RequestId, atomic terminal winner, validated response payload, timeout/lease |
| DynamicMarketState lock/clone/decay pattern (L253) | **REUSE AFTER HARDENING** | T15/T16 scope 통과 인정. public state confinement, configurable decay, initial tick/stock semantics, compound key, durable state |
| Market buy/sell pressure formula | **REPLACE** | SRS-FR-215/216 semantics와 CFG-021~024 기준으로 formula oracle 및 boundary tests 먼저 |
| ServerClientSession single writer/channel (L256) | **REUSE AFTER HARDENING** | 단일 writer/tick loss tolerance 패턴 재사용. bounded resource policy, application ACK/dedup recovery, disconnect semantics, pending counter/timeout stress 필요 |
| TcpNetworkServer framing transport | **REUSE AFTER HARDENING** | framing, session events 참고. auth gate/allowlisted packet schema/validated payload, session uniqueness, reconnect epoch 필요 |
| TcpNetworkServer domain authority dispatch | **REPLACE** | self-claimed entity ownership 및 packet results 신뢰 모델은 중앙 authority/transaction ADR로 재설계 |
| WorldTickManager (L259) | **REUSE AFTER HARDENING** | zero-client tick core와 ITickableWorldSystem callback 인정. durable tick, config, lateness handling, callback fault isolation/perf |
| FogOfWarTileCache / History snapshots | **REUSE AS TEST/REFERENCE ASSET ONLY** | Tile-state/cache 자료구조 참고용. 현재 모든 WorldObject 은폐 정책은 재사용 불가 |
| Fog WorldObject.Draw / Letter blanket jump restriction | **REPLACE** | 항상 공개 정적 정보와 Caravan detection을 분리; visible selection/path/UI leak 포함 검사 |
| SettlementBorderProximityValidator 2-Hop BFS | **REUSE AFTER HARDENING** | 실제 neighbors/layer/upper bounds 검사 인정. CFG radius/graph ownership/precedence 구현 자체는 아니며 graph oracle test 필요 |
| Tactical packet enum / 기존 DTO | **REUSE AS TEST/REFERENCE ASSET ONLY** | Wire documentation 참고. 누락된 session/commands/state/journal을 enum으로 완성 판정 금지 |
| Debug transfer / QA historical tests | **REUSE AS TEST/REFERENCE ASSET ONLY** | local engine smoke/stub checks용. debug direct Execute는 서버 pending transaction을 만들지 않아 server→engine→save→commit E2E가 아니다 |
| Round3~5 및 기존 Phase 승인 자료 | **REUSE AS TEST/REFERENCE ASSET ONLY** | 역사적 정상/rollback 사례 참고. 새 Canonical SRS Gate 또는 durable fault tests의 대체 자료 아님 |

## D. Existing Defects Mapping

기존 QA 식별자를 유지한다. Canonical 번호와 증거를 보정했으며, 이번 작업에서 Production 변경이 없으므로 기존 결함을 임의로 resolved 처리하지 않는다.

| Defect | Severity | Canonical Requirement mapping | Actual evidence / status |
|---|---|---|---|
| QA-001 identity/auth/version | Critical | FR-004~007, BR-011, NFR-007 | E03; T04/T05. 미인증 war 및 self-claimed identity metadata 수정 재현 |
| QA-002 persistence | Critical | NFR-006, FR-004, FR-232, CON-010 | E17/E06/E04/E15. 메모리만 존재. 이전 Ban FR-233 인용 교정 |
| QA-003 distributed transfer | Critical | FR-166, FR-043, NFR-001/002/004/005/007 | E06/E07. client change/result 송신과 server commit 및 save가 분리됨 |
| QA-004 ownership scope | Critical | FR-166, NFR-002/005 | E07. all spawned old-faction + CanHaveFaction만. 일반 items/holders/player owner/layer 범위 미충족 |
| QA-005 TransferId collision | High | NFR-004/005, FR-166 | T03: 다른 settlement가 같은 ID로 pending overwrite; first orphan 유지 |
| QA-006 wrong war Tier | High | FR-110/111, CFG-010 | T02/T09. opposite Tier 두 방향 모두 결함 확인 |
| QA-007 tax semantics | High | FR-180~196, BR-015~018 | T07/E06. 실제 징수 없음/미도착 체납/settlement key/boolean report 신뢰 |
| QA-008 forged visit host | High | FR-091/095, NFR-007 | T06/E11. 실제 owner offline인데 다른 online host에 request 라우팅 |
| QA-009 Cancel/Accept race | High | FR-092~094, NFR-004 | E11. shared mutable request의 check/set/remove atomicity 없음. static interleaving 근거; 이번 runtime race 주입 미실행 |
| QA-010 fog/territory conflict | High | FR-053~074, BR-006/007, CFG-006/007 | E08/E10. 공개 settlement 차폐, fixed2, territory/vision 없음 |
| QA-011 reconnect epoch/parser | High | NFR-004/007/008 | T08/E18. old partial frame으로 new packet header 손상; queued apply에는 epoch 없음 |
| QA-012 repair rollback | Critical | FR-166, NFR-002/004/005/006 | E07/E06. incomplete rollback 문자열/UI만, server pending 제거 후 원소유 유지 log; durable repair/resync 완료 경로 없음 |
| QA-013 market trust/replay | High | FR-213~219, NFR-004/007 | T11/T12/T13/E15. 중복·음수 report/compound key alias 확인. 기존 defect 범위의 구체화 |
| QA-014 concurrent visit UI | Medium | FR-091~094, NFR-009 | E12. static latest dialog로 여러 창 cancel/close 대상 추적 부족; 실제 화면 테스트 이번 범위 밖 |

**Required Fix boundaries:** QA-001은 authenticated session→Player→Faction→entity capability chain과 version gate, QA-002/003/005/012는 durable operation/revision/repair journal, QA-004는 complete engine entity graph snapshot, QA-008/009/014는 서버 canonical lifecycle와 client request registry가 필요하다. QA-006/007/010/013은 해당 policy/authority ADR에 연결된 독립 oracle tests로 재검증한다. 임시 UI 성공/단일 정상 경로/빌드만으로 close하지 않는다.

**Missing regression coverage:** duplicate/reorder/late ACK, live Disconnect/reconnect, server restart, failed save before/after commit, simultaneous purchase/tax/transfer, destroyed ownership target/null settings, callback mutation, stale client save overwrite, corrupted durable record, session lease expiry. 기존 테스트가 상당 부분 stub/reflection/정상 흐름이므로 실제 엔진/저장 연결 검증을 별도 요구한다.

## E. Architecture Blockers

Gemini의 5개 proposal은 구현 증거가 아니라 ADR 입력이다. Architecture Gate 해제 권한은 Master에게 있다.

### ADR-01 — Authenticated identity and central authority

[DECISION REQUEST]

- **Affected Requirement:** FR-004~007, BR-002/003/011, NFR-004/007/012.
- **Observed Conflict:** packet의 PlayerId/FactionId와 결과를 caller가 정한다. Server catalogue가 있어도 중앙 최종 권한이 아니다.
- **Code Evidence:** E03/E06/E07; T04/T05/T06.
- **Option A:** Steam 우선 영구 identity 검증 + authenticated session, domain ownership/version capability, authoritative operation journal.
- **Option B:** Steam 경로가 현실적으로 불가능함이 확인되면 SRS-FR-005의 ID/Password 대체 방식 + 같은 domain 인가 체계.
- **Trade-offs:** 로그인 API/운영 보안 부담은 다르나 self-claimed nickname trust는 어느 옵션에서도 허용되지 않는다.
- **Recommendation:** identity proof/duplicate login/session epoch/version/packet authorization matrix를 먼저 결정. 중앙 정치·경제 권한과 Tactical simulation 권한을 별도 명시한다.

### ADR-02 — Offline Combat + Remote Tactical Authority

[DECISION REQUEST]

- **Affected Requirement:** FR-098~107, FR-152~162, CON-010, NFR-007/008/011.
- **Observed Conflict:** 현재 Tactical engine 없음. Gemini L334의 “dedicated server는 engine을 돌릴 수 없다”는 현재 net8 참조 부재를 기술적 불가능으로 일반화한 주장이다. L337의 통계 sanity check는 plausible forged outcome을 인증하지 못한다.
- **Code Evidence:** E00/E12/E14/E19. Gemini L304~369는 proposal, 실행 코드/latency test 없음.
- **Option A:** Server가 lease/epoch를 발급하는 attacker-host temporary session + remote command/snapshot. SRS architecture 후보와 부합하나 untrusted host 결과 검증 방식을 명시해야 한다.
- **Option B:** trusted engine worker/host authority 및 remote replication 가능성 PoC. 현재 코드가 지원하지 않는다는 사실과 기술적으로 불가능하다는 주장은 구분한다.
- **Trade-offs:** A는 engine 접근이 쉬우나 attacker cheating/host disconnect/relogin 합류/결과 save가 위험. B는 trusted simulation 경계를 만들 수 있으나 실제 1.6 engine 운영 가능성/성능을 PoC로 입증해야 한다.
- **Recommendation:** 공격자 주최 방식을 완료 승인하지 않는다. threat model, lease revocation, outcome validation 및 restart/host crash/rejoining defender를 포함한 최소 실제 engine PoC를 최우선 수행. 평화/전투는 동일 session 구조를 사용한다. Offline 공격 금지로 우회하지 않는다.
- **Gemini verdict:** **ARCHITECTURE ISSUE**. Map-owner/remote command 제안은 유효 후보지만 latency 충족이나 anti-cheat 완성 증거가 아니다.

### ADR-03 — Canonical inventory, save revision, offline trade/tax

[DECISION REQUEST]

- **Affected Requirement:** FR-183~212, NFR-004/006/007, FR-153~156.
- **Observed Conflict:** logout snapshot + login delta만으로 crash 전 재고, 실제 buyer Caravan, concurrent tax/occupation와 stale save를 처리할 수 없다. ConcurrentDictionary는 여러 asset debit/credit의 DB transaction이 아니다.
- **Code Evidence:** E00/E06/E15. Gemini L373~383 제안에는 entity revision/durable materialization/duplicate delta protocol 없음.
- **Option A:** 서버 durable canonical entity/inventory ledger + revisioned engine materialization; buyer/seller assets와 actual collection을 하나의 operation으로 commit.
- **Option B:** durable authoritative map snapshot/engine worker에서 실제 inventory transaction 후 동일 revision을 server와 client에 반영.
- **Trade-offs:** A는 map unloaded 상태 표현이 가능하지만 ledger가 실제 자산의 유일한 최신 상태여야 하고 login 때 중복 spawn 및 stale local save overwrite를 금지해야 한다. B는 engine fidelity가 높으나 PoC 의존성이 크다.
- **Recommendation:** “로그인 때 화면에 materialize”와 “로그인 때 비로소 거래를 확정”을 구분한다. 전자는 authoritative persistent entity state가 즉시 변하고 exactly-once로 적용된다면 후보가 될 수 있다. 후자는 FR-206~208의 즉시 실제 재고 반영을 만족하지 않는다. SRS의 가격/상품 조건·최대 보유 수량·예약 없는 상점 정책을 축소하지 않는다.
- **Gemini verdict:** **ARCHITECTURE ISSUE**. ledger pattern은 조건부 후보, 100% overselling/duplication 방지 주장은 입증 안 됨.

### ADR-04 — Durable distributed ownership and repair

[DECISION REQUEST]

- **Affected Requirement:** FR-022/028/029/041~048/166/174~179, NFR-001/002/004~007.
- **Observed Conflict:** local success packet은 durable commit이 아니며 ACK 소실 뒤 engine과 server가 다를 수 있다. Pending 제거 뒤 incomplete rollback을 repair record로 남기지 않는다.
- **Code Evidence:** E06/E07/T03; Gemini L387~392의 “그대로 연결”은 충분하지 않다.
- **Option A:** versioned prepare/apply-save/commit coordinator + durable idempotent receipt 및 repair quarantine.
- **Option B:** single trusted engine/state transaction authority + server domain commit을 동일 durable checkpoint에 포함.
- **Trade-offs:** A는 failure windows와 보상 실패 관리가 복잡하다. B는 engine 운영 결정을 선행해야 한다. 어느 방식도 일부 faction만 바꾸고 success로 보고할 수 없다.
- **Recommendation:** complete entity scope(player owner, pawn, building, animal, item, holders, map/layer, title/tree/territory 등)와 rollback 결과 oracle을 먼저 확정. Unique TransferId/session lease, expected revision, duplicate completed result, retry/timeout/restart recovery, unrepaired state 행동 차단/운영 추적을 PoC로 증명.
- **Gemini verdict:** **ARCHITECTURE ISSUE / DOWNGRADE REQUIRED**.

### ADR-05 — Authenticated intent and political consequences

[DECISION REQUEST]

- **Affected Requirement:** FR-120~132, BR-012, CON-001, NFR-006/007/012; theft TBD-03.
- **Observed Conflict:** Damage 시점 CurJob TargetA/B는 발사/명령 시점의 실제 intent와 다를 수 있다. miss/무피해 의도 공격을 놓치거나 projectile 도착 중 변경된 job으로 오판정할 수 있다. client report 자체도 위조 가능하다.
- **Code Evidence:** E04/E00; Gemini L400~414 pseudocode는 실행/검증 코드가 아니다.
- **Option A:** Tactical authority의 command/verb/projectile launch intent 기록, owner/capability/target/eventID 검증 후 server political state transition.
- **Option B:** 명시적으로 허용된 CON-001 범위에서 모든 AoE를 제외하되 direct intent와 ordinary friendly fire는 authority event로 처리.
- **Trade-offs:** A는 attribution 구현 비용이 높다. B는 AoE 배반 탐지 범위를 좁히는 명시적 fallback이며 일반 공격·Betrayer persistence를 생략하는 근거가 아니다.
- **Recommendation:** original intent를 immutable event로 보존하고 delayed impact, job change, collateral, miss, concurrent betrayal, repeat timer/restart 테스트를 작성. theft 시점은 Master/User TBD 결정에 의존한다.
- **Gemini verdict:** **ARCHITECTURE ISSUE**.

### ADR-06 — Configuration, time and domain invariants

- **Affected Requirement:** CFG-001~026, NFR-003, FR-015~020/034/035/110/111/180~196/213~219.
- **Decision needed:** canonical parameter names/types/ranges/units, game-time vs real-time unit, invalid config 실패/default 정책, config schema version 및 save migration.
- **Gemini proposals:** JSON/SQLite/live reload는 유효 선택지이나 SRS 필수 기술이 아님. 두 clock과 prep/tax/market timers 단위를 먼저 정의한다. dormant score helper와 “전체26개 hardcoded” 주장을 runtime implementation으로 승인하지 않는다.
- **Recommendation:** balances는 config oracle에서 검증하고 policy invariants를 separate domain test로 검증. reload 지원을 추가 scope로 할지 Master 결정.

**TBD register:** SRS TBD-01 가입 초과 SettlementLimit, TBD-02 Pending 퇴거 상세, TBD-03 theft intent/시점, TBD-04 Caravan-only Faction 생존 상세, TBD-05 체납 상환/해소 정책을 canonical 문구 그대로 Master에 제출한다. Gemini L475/479의 원문 ID 및 Baron limit1을 정정한다. 아직 결정되지 않은 정책은 `BLOCKED BY REQUIREMENT`; 구현 가능한 부분도 Authority 미정이면 `BLOCKED BY ARCHITECTURE`로 별도 관리한다.

## F. Recommended Immediate Work Order

**지금은 ADR/PoC/검증 주문만 권장하며 Production 구현을 시작하지 않는다.** Gemini L418~467처럼 Offline Authority를 가장 마지막 WP로 미루면 inventory/transfer/remote 구조의 기반을 다시 작성할 위험이 크다.

| Order | Proposed work package | Prerequisite / deliverable / independent acceptance |
|---|---|---|
| 1 | WP-BASELINE-ADOPT | Master가 이 후보의 Canonical ID/coverage/defect를 채택 또는 근거 있는 수정. Gemini 원문 matrix의 nonexistent method/ID/100% claim 정정. Production 코드 변경 없음 |
| 2 | WP-ADR-AUTH-STATE | ADR-01 + persistent state ownership/identity/session epoch/save revision 확정. 각 packet의 authenticated caller, 대상, permission, replay policy matrix |
| 3 | WP-ADR-TACTICAL-OFFLINE | ADR-02 및 ADR-03/04의 공통 lease/inventory/commit 경계 결정. Offline attack mandatory, single Map simulation, own Pawn control, late join/host disconnect/restart 회복 요구 유지 |
| 4 | WP-POC-OFFLINE-TAC | 최소 실제 1.6 existing map load/AI defense, visitor/defender remote commands, peaceful→hostile, owner offline/online handover, host crash/restart, latency 측정. GUI 자동화 없이 engine test runner/headless 가능성부터 검증; 최종 인게임 승인은 User |
| 5 | WP-POC-INVENTORY-TXN | 1개 item/entity를 buyer+seller+tax/transfer와 동시에 변경, persistence 실패 단계별 주입, duplicate/reorder/relogin delta/stale save 재사용. 총량 보존·동일 operation 1회 효과·restart 후 revision oracle |
| 6 | WP-POC-OWNERSHIP-REPAIR | complete entity graph, layer, null/Destroyed ownership target, callback mutation, save/ACK crash window, TransferId collision, rollback failure quarantine/repair 완료 테스트. POC-INV/TAC 결정된 권한 모델 사용 |
| 7 | WP-ADR-INTENT-CONFIG | ADR-05/06 및 TBD-01~05. Intent oracle/clock units/config validation 결정; scope 축소 없이 선택 기록 |
| 8 | WP-IMPLEMENTATION-PLAN-REQUEST | 위 PoC evidence와 ADR로 Gemini revised gap/work dependency 제안. 그때 Master가 Production WP를 승인; QA는 requirement-specific gates와 failure tests 리뷰 |

**QA Test Harness 발주 요건**

- 실제 Common/Server source 기반 authenticated multi-session protocol harness: duplicate/reorder/drop/delay/late ACK, host spoof, reconnect epoch, cancellation winner 1개, repeated RequestId.
- Durable repository/fault injector: before/after prepare, engine apply, save flush, server commit, response; restart recovery. 단순 dictionary mock을 durable persistence로 간주하지 않는다.
- RimWorld 1.6 entity snapshot oracle: player/faction identity뿐 아니라 spawned/unspawned/contained pawn+animal+item+building, claims/area/master/job/work, layer 및 complete ownership graph를 비교. stub과 real engine test 결과를 분리한다.
- Inventory conservation oracle: buyer/seller/Caravan/settlement 총량 및 item instance identity; partial payment/tax, sale cancellation, concurrent operation과 stale save rollback 탐지.
- Tactical deterministic command/event recorder: own Pawn permission, shared authoritative Map, Last Input Wins, 1x/no-pause real transition, multiFaction/AI takeover, measured latency.
- Market formula/config oracle: quantity/direction/domain boundary/replay/composite key independence, valid defaults/invalid config, initial price tick, vanilla restock coexistence. 거래 report가 실제1회 execution과 연결됐는지 검증.
- Requirement traceability: 테스트 이름/설명/실행 로그에 Canonical SRS ID, assertion의 관찰 대상, mock 범위, 불통과 시 actual vs expected를 기록. 구현 식을 그대로 복제한 테스트만으로 PASS하지 않는다.

**Final Recommendation to Master**

현재 Gate **BLOCKED BY ARCHITECTURE 유지**. 본 후보를 공식 기준으로 채택하기 전에 Canonical mapping과 ADR-01~06/TBD 처리 방식을 Master가 확정한다. 유효한 기존 helper/UX/transport 자산은 보존하되 완성된 transaction/authority로 취급하지 않는다. 다음 단계는 새 Production 기능 구현이 아니라 가장 위험한 Offline/Tactical/Inventory/Ownership 경계를 결정하고 독립 failure PoC로 증명하는 것이다.

이 보고서는 현재 Master Work Order 대화에 산출물로 전달한다. 별도 다른 채팅으로 전송한 것으로 보고하지 않는다. Gemini의 revised baseline/gap matrix 또는 Master 다음 지시를 기다린다.

