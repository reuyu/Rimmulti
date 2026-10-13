# ADR-006A — Temporal Authority

- Work Package: **WP-ADR-TEMPORAL-AUTHORITY-01**
- Role: Architecture / Independent QA Reviewer
- Decision Status: **PROPOSED**
- Date: 2026-10-02, Asia/Seoul
- Decision owner: **Master**
- Prerequisites: ADR-001 **ACCEPTED**; ADR-002 **PROVISIONALLY ACCEPTED**.
- Production implementation / commit / deployment / GUI: **NONE**.
- Scope: Server World Time, 독립 Settlement Local Time, active Tactical simulation, engine/native-save 시간 좌표 및 결과 채택 경계.
- 본 문서의 schema·상태·adapter 이름은 **설계 제안**이다. 구현 존재나 engine feasibility PASS를 뜻하지 않는다.

## 1. Proposed Decision

**권장안은 B의 제한된 형태: full context load + target-scoped simulation + target-scoped result extraction/merge + 하나의 active local clock domain당 하나의 engine execution island.**

핵심 결정 제안:

1. 서버의 durable **WorldTick(W)**, 정착지별 durable **LocalTick(Lₛ)**, engine의 **TicksGame(G)**, 운영용 **monotonic elapsed time(M)**을 서로 다른 값으로 취급한다.
2. Tactical의 tick은 대상 정착지 local timeline의 연속이다. 별도의 새 날짜로 reset하지 않으며 **Lₛ(final)=Lₛ(admission)+실제로 수행한 target ticks**로 진행한다. 전투로 offline 정착지의 local 시간이 진행하는 것과 offline **일반** simulation 정지는 양립한다.
3. 서로 다른 정착지의 W/L/G 사이에는 일반적인 `W=3×L` 또는 `L=G` 관계가 없다. 속도 변경, pause, offline, session/restart 때문에 전역 선형 변환은 성립하지 않는다.
4. full `.rws` export는 **private worker checkpoint / extraction input** 후보일 뿐이다. 그것을 통째로 canonical save pointer로 교체하는 권한을 부여하지 않는다.
5. canonical 결과에는 인가된 target graph와 명시적 cross-boundary transfer만 포함한다. 비대상 map/World subtree, worker global counter 및 domain timer를 wholesale 반영하지 않는다.
6. frozen graph의 timebase는 일반 background progression으로 바뀌지 않는다. 단, SRS가 요구하는 offline trade/tax는 별도 asset transaction으로 적용할 수 있다. **clock freeze ≠ inventory mutation 금지**다.
7. 타임스탬프는 typed temporal schema와 validated materialization으로 변환한다. “모든 Tick 필드에 같은 델타” 또는 raw XML 일괄 rebase는 채택하지 않는다.
8. load 이전부터 simulation을 fence하고, native getter/normalization/dispatch의 결과를 검증한 뒤 READY를 허용한다. ordinary-local resume도 같은 temporal admission을 거친다.

**제안 채택과 구현 Gate는 별개**다. ENGINE-02의 FAIL이나 QA-ENGINE-004~008은 문서 작성으로 해소되지 않는다. Master만 본 ADR의 ACCEPTED/REJECTED 상태를 결정한다.

## 2. Canonical Requirement Traceability

기준은 [요구사항_명세서.md](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md>)다. 하위 문서의 동명 번호를 Canonical ID로 사용하지 않는다.

| Requirement | Temporal obligation |
|---|---|
| SRS-FR-001 | 접속 Player 0명이어도 서버가 동작하는 동안 World Time 진행 |
| SRS-FR-002 | Settlement Local Time을 World Time과 독립 운영. SRS §3.1의 서로 다른 날짜·계절 허용 |
| SRS-FR-003 | Owner offline인 일반 settlement simulation 정지; offline tactical 예외와 구분 |
| SRS-FR-095 | offline 일반 방문 거절과 합법적인 offline 공격 admission을 구분 |
| SRS-FR-098 | 방문 시 기존 Map identity/state/timeline 보존 |
| SRS-FR-101 | 동일 Tactical session에서 peaceful→hostile; clock/session reset 없음 |
| SRS-FR-102, SRS-BR-010 | peaceful speed 입력 허용, server-accepted Last Input Wins 순서 |
| SRS-FR-103/104/105 | hostile 1x/no user pause; 종료 후 speed 선택 가능, 이전 속도 자동 복원 불필요 |
| SRS-FR-115/118/128/130/171/217 | WarPending/war cooldown/Betrayer/Ruins/NPC recovery는 server World clock |
| SRS-FR-153/154/155 | Owner offline 실제 전투, AI 방어, 실제 결과 영구 반영; 시간 구조의 어려움 때문에 공격 금지로 축소하지 않음 |
| SRS-FR-157/158 | 로그인/로그아웃의 controller 전환으로 battle timeline reset/duplicate advance 금지 |
| SRS-FR-166 | conquest의 Pawn/Animal/Building/Item ownership 변경과 entity clock/time state를 함께 추적 |
| SRS-FR-180/183/187, SRS-BR-016 | World-day tax policy, 실제 도착·징수 시각 기준 cycle, offline 징수; 시간 경과만으로 징수했다고 처리하지 않음 |
| SRS-FR-192 | 체납은 실제 징수 시도 결과. timer expiry만으로 생성하지 않음 |
| SRS-FR-206/207/208/209 | offline shop과 즉시 inventory 반영, 거래별 결과 통지; frozen-clock 자산 mutation 및 stale save 방어 |
| SRS-FR-219 | 가능한 한 vanilla NPC restock 유지. arbitrary target G 진행을 canonical restock으로 인정하지 않음 |
| SRS-CFG-001/023 | World speed와 NPC recovery 설정의 version/effective time 보존 |
| SRS-NFR-002/004/005/006/007 | ownership 원자성, coherent clock/save/inventory state, durable time/cooldown, 단일 중앙 확정 |
| SRS-NFR-008/011/012 | client 장애 격리, cooperative worker, audit 가능한 temporal transition |
| SRS-CON-003/010 | 실제 1.6 engine 지원과 offline combat authority 유지 |

**SRS에 명시되지 않은 사항:** Pawn chronological age가 universal World 날짜를 따라야 하는지, server process downtime 동안 World를 catch-up할지, 서로 다른 local 날짜 사이를 이동하는 entity의 세부 physiological policy. 본 ADR은 권장안을 제시하고 §23에서 Master 결정 항목으로 명시한다. 기존 구현의 고정 180 TPS를 설정 불가능한 요구로 승격하지 않는다.

## 3. Inputs and Evidence Classification

| Label | Input | Evidence class |
|---|---|---|
| SRS | root Canonical SRS, 특히 §3.1, FR-001~003, tactical/time/tax 요구 | Requirement |
| AUTH | [ADR-001](<C:/Users/user/Desktop/RimMulti/ADR-001_Authenticated_Authority_and_Persistent_State.md>) §§10–12, clock watermark/revisions/recovery | ACCEPTED architecture contract; 현재 구현 완료 증거 아님 |
| TAC | [ADR-002](<C:/Users/user/Desktop/RimMulti/ADR-002_Tactical_and_Offline_Combat_Authority.md>) session/lease/admission/recovery/commit | PROVISIONALLY ACCEPTED architecture target |
| E1 | [ENGINE-01 Dev evidence](<C:/Users/user/Desktop/RimMulti/POC_TAC_ENGINE_Evidence.md>) 및 [independent QA](<C:/Users/user/Desktop/RimMulti/QA_POC_TAC_ENGINE_Review.md>) | 실제 실행 중 독립 확인된 subset만 tested fact |
| E2 | [ENGINE-02 Dev evidence](<C:/Users/user/Desktop/RimMulti/POC_TAC_ENGINE_02_Evidence.md>) 및 [independent QA](<C:/Users/user/Desktop/RimMulti/QA_POC_TAC_ENGINE_02_Review.md>) | 보고서의 광범위 PASS를 그대로 채택하지 않음 |
| IL2 | [ENGINE-02 installed engine IL](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/ENGINE02-20261002/engine-il.txt>) | 해당 설치 assembly의 정적 동작 증거 |
| IL6 | [이번 read-only temporal IL audit](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/temporal-engine-il.txt>) | actual assembly 정적 분석. 새 game runtime 실행 아님 |
| GAP | [Official Gap Baseline v1](<C:/Users/user/Desktop/RimMulti/Official_Gap_Reconciliation_Candidate_v1.md>) | 채택된 기존 결함/구현 경계 |
| X3/X4 | ADR-003 — Canonical Inventory / Save Provenance; ADR-004 — Distributed Ownership Transaction / Repair | **NOT YET AUTHORED / FUTURE DEPENDENT ADR**. 예정 범위는 Master가 이번 작업 중 명시. 정식 원문·채택된 세부 계약 없음 |

이 문서의 각 설계 표는 **proposal**다. 아래 실제 값은 이전 독립 실행 증거이며, 본 작업에서 게임을 재실행해 새 결과를 얻었다고 주장하지 않는다. UI 수동 체크리스트 완료 기록은 historical UI evidence다. temporal architecture나 asset merge 승인 증거로 사용하지 않는다.

## 4. Actual Engine Behavior and Limits

### 4.1 Confirmed runtime behavior

- actual 1.6 `DoSingleTick()`은 global G를 증가시키며 global TickLists, maps 및 여러 global manager를 dispatch한다. ENGINE-01의 기본 loop는 non-target map과 worker World를 진행시켰다.
- ENGINE-02 필터의 정상 scoped 구간에서 non-target food/position/biological age/MapComponent는 정지했지만, Human100302 chronological age는 **698109109→698160590(+51,481)**였다.
- full export/fresh reload에서 non-target MapProbe **1→2**, Lord timer **+1**, `recentMemory.lastLightTick` **1823→53307**, 일부 plant age **+2000**, worker-local goodwill timer **1→2**가 확인됐다. raw XML diff 전체를 semantic corruption으로 계산한 것은 아니다.
- `fastEcology` 직접 TickLong 경로에서 non-target plants **25,835개**의 age 변화가 재현됐다.
- target held inventory rot/fire/power/AI 진행과 warmed loop **60.26 TPS**는 확인됐다. crop/bill/master 및 전체 graph/time codec completeness는 증명되지 않았다.
- 원본 단일 local save의 load→tick→native save→fresh reload는 제한된 state subset에서 가능했다. **target-only package, scoped extraction/merge, complete time rebase는 실행 증거가 없다.**

### 4.2 Additional static facts from installed engine

IL6는 설치된 RimWorld **1.6.4871 rev591 / Unity 2022.3.35f1** 환경의 Assembly-CSharp.dll을 대상으로 한다. engine SHA-256은 `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A`이며 입력 manifest에 기록했다. IL6를 통해 다음을 확인했다.

1. `TickManager.TicksAbs = ticksGameInt + gameStartAbsTick` 경로가 있다. start anchor가 없을 때 fallback도 있다. **G만 고치는 것으로 absolute clock의 의미를 보존하지 못한다.**
2. `Pawn_AgeTracker.AgeChronologicalTicks = GenTicks.TicksAbs - birthAbsTicksInt`. 반면 biological age는 `AgeTickInterval`의 실제 tick interval을 통해 갱신된다.
3. age tracker에는 `nextGrowthCheckTick` 등의 absolute scheduling field도 존재한다. birth timestamp 보정만으로 Pawn 전체가 안전해지는 것은 아니다.
4. `Thing.ExposeData`는 `tickDelta`를 저장한다. duration accumulator와 absolute timestamp를 같은 수식으로 취급하면 안 된다.
5. TickList bucket은 object hash와 tick interval에 의존한다. clock 좌표 변경은 rare/long dispatch phase와 함께 검토해야 한다.
6. `GenLocalDate`는 engine absolute time과 타일 longitude/location으로 날짜·계절을 구한다. World calendar와 local map calendar를 독립 제공해야 한다.
7. 실제 `get_TickRateMultiplier`에는 forced normal 및 adaptive branches가 있다. 기존 Common의 단순 “speed2=120/s, speed3=180/s” 상수를 vanilla engine speed enum 해석의 증거로 쓰지 않는다.

이 증거만으로 모든 DLC/mod timestamp codec, 로드 이전 clock interception, extracted graph 재적용 API를 구현 가능하다고 확정하지 않는다.

### 4.3 코드·증거 위치와 현재 구조의 한계

| 실제 위치 | 확인한 경계 |
|---|---|
| [Server WorldTickManager.cs:40](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Time/WorldTickManager.cs:40>) | 기본 initialTick=0과 메모리 counter. durable bootstrap/time revision 경계 없음 |
| [Server WorldTickManager.cs:58](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Server/Time/WorldTickManager.cs:58>) | 고정 rate pacing. system 예외 이후에도 tick 진행·broadcast 가능하며 과도한 pacing 부채를 버리는 경로 존재. ADR-001의 durable clock/event commit과 다름 |
| [ClientWorldTickManager.cs:77](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Client/Time/ClientWorldTickManager.cs:77>) | client delta 기반 accumulator, 360 상한, WorldObjectsHolder 직접 tick. canonical W 권한이나 Settlement별 clock adapter를 구현한 증거가 아님 |
| [WorldTimeConstants.cs:12](<C:/Users/user/Desktop/RimMulti/WarEconomyMod/Source/Common/Time/WorldTimeConstants.cs:12>) | 고정 배율·calendar 상수. actual native speed enum policy와 동일하다는 증거 없음 |
| [QA ENGINE-02:154](<C:/Users/user/Desktop/RimMulti/QA_POC_TAC_ENGINE_02_Review.md:154>) | chronological leak, fresh reload와 resume 반례, 모든 timer가 일제 catch-up했다고 주장하지 않는 제한 |
| [QA ENGINE-02:333](<C:/Users/user/Desktop/RimMulti/QA_POC_TAC_ENGINE_02_Review.md:333>) | QA-ENGINE-004~008의 시간/dispatch/load/pacing 결함. 기존 OPEN 상태 유지 |
| [Temporal IL:24](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/temporal-engine-il.txt:24>), [Temporal IL:270](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/temporal-engine-il.txt:270>) | native absolute clock과 chronological getter의 실제 식 |
| [Temporal IL:517](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/temporal-engine-il.txt:517>), [Temporal IL:812](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/temporal-engine-il.txt:812>) | tickDelta 저장과 local date getter. counter와 absolute calendar 구분 근거 |

이번 추가 증거는 설치된 Assembly-CSharp.dll의 metadata/IL을 읽은 것이며, game assembly를 실행하거나 새로운 runtime 합격을 얻은 것이 아니다. [정적 감사 도구](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/EngineIL/Program.cs>)와 [입력 hash 기록](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/inputs-before.json>)으로 확인 범위를 보존했다.

## 5. Authoritative Clock Taxonomy

| Clock / coordinate | Authority | Advance condition | Durability / use |
|---|---|---|---|
| **WorldTick W** | Dedicated Server domain clock | 서버 동작 중 admitted world advancement. player count와 local speed 무관 | committed watermark durable; 정치/경제/Caravan/World calendar |
| **Settlement LocalTick Lₛ** | server-recognized local timeline; 현재 ordinary/tactical simulation writer가 실행 | 해당 settlement의 authorized simulation step이 실제 완료 | checkpoint/accepted outcome과 결합. offline ordinary 구간 ΔL=0 |
| **Tactical progress Nₜ** | current worker lease | admission 후 target step 완료 횟수 | `Nₜ=Lₛ-Lₛ₀`; checkpoint의 recovery coordinate. 독립 calendar 아님 |
| **Engine G / engine Abs** | 해당 runtime의 operational coordinate | native tick execution / approved projection materialization | canonical W/L을 대체하지 않음. raw save counter는 authority proof 아님 |
| **Host monotonic M** | 해당 supervisor/server process | real elapsed time | pacing/watchdog/deadline. boot간 비교하지 않음; gameplay expiry의 durable key 아님 |
| **UTC / audit timestamp** | operator clock, diagnostic | wall clock | audit/support. clock correction이나 client 값으로 gameplay 시간 진행/timeout 순서 결정 안 함 |
| **Client display estimate** | presentation only | interpolation / correction | canonical command eligibility, age, inventory 또는 expiry를 확정하지 않음 |

`LocalTick`은 physics timestep budget과 논리적 local 날짜 증가의 기반이다. server가 모든 local step을 직접 계산해야 한다는 결정은 아니다. **어느 actor가 ordinary simulation 결과를 신뢰할 수 있게 제출하는지**는 ADR-001/002의 남은 provenance 경계와 연동해 결정한다.

### 5.1 Clock identity and lifetime

- LocalClockId는 `(WorldId, SettlementId, MapIdentity/Layer, TimelineLineage)`에 연결한다. nickname, process PID, login SessionEpoch에 연결하지 않는다.
- owner 변경/conquest, login, worker 재시작으로 Lₛ를 0으로 reset하지 않는다. Map identity가 유지되면 timeline도 이어진다.
- 새 settlement 생성은 별도 clock origin을 발급한다. 권장 초기 날짜 seed는 생성 시의 committed World calendar지만, 이후 W와 동기 진행하지 않는다.
- destroy 후 clock은 retired/tombstone으로 남겨 old save의 재등록을 막는다. Ruins 유지시간은 W clock이며 retired L의 연장이 아니다.

## 6. Option Analysis

| Criterion | A. Full-save time rebase / virtualization | B. Full context + scoped extraction/merge | C1. One-map clock-island package | C2. In-process per-map virtualization |
|---|---|---|---|---|
| Main idea | full Game의 모든 map/time fields를 변환하거나 virtualize한 후 전체 결과 publish | full context는 private execution용. target closure와 approved cross-boundary delta만 채택 | 실제 기존 target Map + 필요한 reference context만 native package로 materialize; runtime당 active clock1 | 하나의 engine G 아래 모든 map dispatch/getter를 Lₛ context로 가상화 |
| Single global G | 광범위 adapter 필요 | target G projection1개; non-target canonical time은 worker 밖에서 보존 | target G projection1개; 외부 context 절단/해석 필요 | dispatch마다 clock context, list/bucket/UI/DLC/global hook 전부 조정 |
| Frozen state | entire save의 모든 timer/graph 보존 증명 필요 | raw non-target export를 버리고 canonical base/revisions 보존 | non-target map을 실행 context에서 배제 가능하나 references 필요 | non-target tick뿐 아니라 derived getters/initialization도 virtualize |
| Scope/merge risk | 우발적 whole-world overwrite, stale inventory와 결합 | typed graph closure와 crossrefs/inventory merge가 핵심 위험 | package의 complete native graph와 ordinary reassembly가 핵심 위험 | implicit global reads와 mis-scoped callbacks가 핵심 위험 |
| Mod/DLC support | 알 수 없는 모든 time field가 global publication 위험 | target temporal field / global context hook 지원 목록 필요 | packaging/foreign reference 지원 목록 필요 | widest engine/mod interception surface |
| Current evidence | complete rebase **없음**; counterexamples 있음 | context load / scoped subset 실행 가능. extraction/merge **미검증** | native one-map save load는 있음. existing multi-map graph 절단 package는 **미검증** | dispatch/global dependencies 정적 확인. virtualization **미검증** |
| Smallest unresolved validation | one foreign frozen map의 typed timers + full save roundtrip; unknown fields fail-close | target graph mutation1개 + foreign reference + timer-preserving merge/reload | target graph+외부 reference1개를 package/load/serialize 후 비교 | 두 날짜의 map2개, alternate tick/getter/rare phase/load·UI read equality |
| Recommendation | 기본안으로 **채택하지 않음**. 제한된 support profile이면 재평가 가능 | **B2 형태 권장**, acceptance 전 feasibility 확정 아님 | 방어 가능한 대안/진행 방향. API·closure 성공을 가정하지 않음 | 일반 multi-map ordinary client의 필요성 확인 시 검토. 단순 get_TicksGame prefix만으로 승인 불가 |

### 6.1 B1 and B2 distinction

**B1: 모든 context map을 무조건 시뮬레이션하고 non-target 결과만 버리는 방식은 권장하지 않는다.** canonical pointer를 안 바꿔도 foreign Pawn/World 상태가 target AI, 관계 조회, cross-map callback에 영향을 줄 수 있다. 비용 낭비 외에 causal contamination 문제가 남는다.

**B2: full context를 reference resolution용으로 로드하되 target simulation과 인가된 helper만 실행한다.** out-of-scope context는 canonical projection 또는 readonly facade로 제공한다. 로드 normalization으로 private context가 변해도 그것을 자동 채택하지 않고, target computation에 영향을 주는 관계/clock query가 canonical context와 같은지 검증한다. 검증되지 않은 context mutation을 “결과를 버릴 것이므로 안전”이라고 처리하지 않는다.

### 6.2 Why not blind rebase

`ageTicks`, `lastLightTick`, `nextGrowthCheckTick`, `ticksLeftThisToil`, `tickDelta`, server WarDueTick는 모두 시간 관련이지만 같은 종류의 값이 아니다. 어떤 것은 duration, 어떤 것은 absolute origin, 어떤 것은 interval debt, 어떤 것은 W deadline이다. 전체 save에 Δ를 더하거나 빼면 이들 중 일부를 손상시킨다. 이름에 Tick이 포함됐다는 regex는 temporal schema가 아니다.

### 6.3 Ordinary topology limit

runtime당 clock1이라는 제약만으로 서로 다른 L을 가진 ordinary maps를 하나의 owner client에서 동시 시뮬레이션할 수는 없다. 현 native multi-map client에 이 문제가 자동 해결됐다고 가정하지 않는다.

가능한 경로는 **clock-island execution 분리(C1 계열)** 또는 **검증된 C2 virtualization**이다. 분리 시 ordinary writer의 신뢰/위치/renderer 및 비용은 별도 결정한다. ordinary 전체를 trusted server worker로 이동시키는 확대안은 ADR-002의 승인 범위를 넘으므로 Master 결정이 필요하다. “local clock이 달라지면 owner의 다른 Map은 영구 사용 금지”로 제품 요구를 줄이지 않는다.

## 7. Proposed Runtime and Publication Boundary

권장 흐름은 다음과 같다.

`canonical asset + local-time manifest → fenced materialization → scoped target simulation → validated extraction candidate → server CAS/operation commit → canonical target snapshot/time → ordinary/tactical next admission`

### 7.1 Single clock island

- 한 active execution island에는 **한 LocalClockId**만 tick writer로 존재한다. 하나의 tactical map에는 participant가 여러 명이어도 shared clock1개다.
- worker full context 안의 다른 maps는 concurrent active settlement로 승격하지 않는다. 각각의 canonical L은 별도 asset/time record에 그대로 남는다.
- public World view는 W 기준 server projection이다. target weather/lighting/local growth/date는 Lₛ 기준 engine simulation이다.
- 일부 global engine subsystem이 target에 필요하면 허용하되, 그 clock/read-set/output scope를 명시한다. 모든 GameComponent/Storyteller를 blanket skip해 target 기능이 멈추는 것은 해결책이 아니다.
- `GenTicks`/getter를 어디서나 W로 바꾸지 않는다. world command 및 target physics의 call context를 분리한다.

### 7.2 Scope of canonical result

채택 가능: target Map의 인가된 terrain/building/plant/pawn/animal/item/held/container/job/health/control effects, LocalClockId/L progression, explicit ingress/egress effects 및 인가된 domain operation evidence.

채택 불가: foreign map subtree, worker-local War/Faction/WorldPawns/Market/quest timers, full global clock, unrelated inventories, unmanaged mod-added global state. 외부 reference가 있다는 이유만으로 그 endpoint 전체를 target write-set에 넣지 않는다.

cross-boundary transfer는 별도 인가된 multi-aggregate write-set/CAS에 포함한다. 방문자 Pawn과 장비, retreat Caravan, loot, tax/trade 대상은 실제 entity/location 관계로 확인한다. graph closure에는 references가 포함되지만 **reference closure와 write authority closure는 같지 않다**.

## 8. Mapping W, L, Tactical Time and Engine Ticks

### 8.1 논리적 매핑

각 simulation segment는 다음 accepted anchor를 가진다. 이름들은 manifest의 **논리적 필드**이며, 현재 engine에 새 API가 있다고 주장하는 것이 아니다.

```text
World domain: W (64-bit committed tick), WorldCalendarOrigin, WorldRatePolicy
Local domain: LocalClockId, L0, LocalCalendarOrigin Ks
Engine anchor: G0, gameStartAbsTick A0, EngineProfileHash

N = number of completed authorized target steps since this anchor
L = L0 + N
G = G0 + N                       # normal non-replay execution segment
EngineAbs = A0 + G               # verified installed-engine path
LocalCalendar(L) = Ks + L        # logical absolute local calendar coordinate

Require at materialization: EngineAbs(G0) represents LocalCalendar(L0)
W has no inferred equality to G, L, or N.
```

`L0/G0/A0/Ks`의 변환은 §10의 typed codec을 따른다. native 정수 범위 때문에 논리적 날짜를 engine 좌표에 직접 표현할 수 없으면 검증된 calendar projection이 필요하다. 현재 getter가 이를 이미 지원한다고 가정하지 않는다.

local 날짜·계절 표시는 타일 longitude/latitude/layer와 local absolute coordinate를 사용한다. World Caravan 날짜와 정치 UI는 World calendar를 사용한다. **World는 겨울, Settlement는 여름인 상태는 정상**이며, 양쪽 날짜 차이를 동기화 오류로 처리하지 않는다.

### 8.2 실제 실행 속도

World time의 nominal 단위는 초당 60 ticks, 기본 설정 배율 3은 **180 W ticks/s**로 제안한다. CFG-001에 따라 유효한 양수의 speed policy를 변경할 수 있어야 한다. 기존 fixed180 구현을 변경 불가능한 요구사항으로 승격하지 않는다.

hostile target의 기본 1x는 **60 local ticks/s**로 제안한다. peaceful/ordinary speed mode는 실제 지원되는 engine policy에 매핑한다. Fast/Superfast 등의 enum 숫자와 배속을 같다고 가정하지 않고, 선택 mode와 effective pacing policy를 version으로 관리한다.

운영용 monotonic `M`으로 active segment의 실행 budget을 계산한다. START 이전의 load/export/idle 시간이 `unscaledDeltaTime`을 통해 새 실행 budget으로 유입되지 않게 한다. rate 변경 시 segment를 닫고, fractional remainder와 이미 승인한 미실행 budget을 명시적으로 인계한다.

미실행 budget을 처리 완료된 L로 발표하지 않는다. cooperative slice의 wall-clock/tick budget에는 상한을 두며, 승인된 실행 부채는 별도로 계수한다. 처리 불능으로 lease가 유효하지 않게 되면 무한 catch-up 대신 RECOVERING으로 전환한다. committed 시간을 되돌리거나 worker 과부하 때문에 server W를 정지하지 않는다.

native tick의 G 증가와 target effect 완료는 같은 증거가 아니다. step 도중 예외로 일부 effect만 적용되면 completed marker를 발급하지 않고 해당 segment를 FAULTED로 격리한다. 이 상태에서 G/L 식을 정상 진행처럼 이어 쓰거나 성공 결과를 발표하지 않는다. graph와 시간의 복구 가능성을 함께 검증한다.

worker의 active G가 반영된 foreign chronological getter/calendar를 그대로 UI나 target AI에 노출하지 않는다. foreign view는 그 Settlement의 canonical local anchor를 사용해야 한다. full context의 raw getter를 readonly라고 부르는 것만으로 시간 격리가 성립하지 않는다.

### 8.3 64-bit 논리 시간과 engine 좌표 범위

canonical W/L/deadline/receipt는 checked 64-bit integer를 사용한다. native engine에는 int 좌표가 있으므로 supported range를 검사해야 한다. 미검증 mod 필드를 wrap/reset하면서 시간 연속성을 주장하지 않는다.

engine 좌표를 재설정해야 하면 typed field·calendar·periodic phase·cache 변환을 검증한 뒤 `EngineClockEpoch`를 갱신한다. **논리적 L/Ks는 계속 유지**한다. overflow 직전의 안전 정지는 장애 격리이며 장기 운영 요구의 성공적인 해결은 아니다. §21의 최소 검증을 거쳐 지원 가능한 rollover 경계를 정해야 한다.

## 9. Age Semantics — Proposed Product Policy

SRS는 biological/chronological age의 clock을 직접 지정하지 않는다. 아래는 **Master 승인 대기 중인 제품 정책 제안**이다.

### 9.1 권장 정책

- **Biological age:** 실제 authorized simulation에서 vanilla age mechanics가 발생시킨 변화만 반영한다. 성장 촉진/억제, cryo, hediff 등의 효과를 보존한다. offline ordinary 구간에는 일반적인 나이 증가가 없다.
- **Engine chronological age / birth coordinate:** Settlement/Tactical 체류 중에는 local timeline을 따른다. frozen ordinary 구간에는 증가하지 않는다. native `birthAbsTicks`는 현재 engine projection에 맞춰 복원하며, 다른 Map의 날짜 차이로 나이를 바꾸지 않는다.
- **Universal World birth/audit metadata:** 필요하면 W 도메인의 별도 이력으로 보존한다. 이를 native age getter의 birth 값에 그대로 대입하지 않는다.
- **Tactical 중 Owner offline:** 대상 L이 진행하므로 주민의 나이도 지원되는 vanilla 규칙에 따라 진행한다. 전투 종료 후 Owner가 offline이면 일반 simulation freeze로 돌아간다.
- **서로 다른 local 날짜 사이 이동:** 진입 직전 chronological/biological age와 성장 상태를 보존한다. 도착 Map의 날짜 차이는 나이 증가 부채가 아니다.

도착 당시 canonical chronological age가 `C`, 새 도메인의 projected absolute time이 `Anew`라면 native birth projection은 `Anew-C`이다. biological age에는 이 공식을 적용하지 않는다. growth progress, `nextGrowthCheckTick`, birthday/periodic state 등은 각각 별도 codec으로 처리한다.

### 9.2 Transit / World Pawn 경계

Caravan 이동은 W를 따른다. Caravan Pawn/Animal/Item의 physiology·aging·rot을 W로 진행시킬지, World 이동 시간과 연결된 별도 transit simulation으로 실행할지는 명시적인 정책이 필요하다. 현재 .NET Server가 vanilla World Pawn physiology 전체를 계산한다고 가정하지 않는다.

본 ADR이 요구하는 인터페이스는 **현재 entity의 residence ClockDomain, 이동 barrier, 값과 remaining duration의 인계**다. transit의 계산 backend와 생리 진행 규칙은 미결정이다. 전 여행 기간 생리 변화가 없다고 임의로 정하거나 두 engine이 같은 Pawn을 동시에 tick해서는 안 된다. §23에서 Master 결정 항목으로 남긴다.

### 9.3 대안

chronological age만 universal W를 따르게 할 수도 있다. 그러려면 frozen local date/bio age와의 차이, World speed 변경, 나이 기반 자격 조건 및 DLC/mod hook 영향을 정책으로 정의해야 한다. QA-ENGINE-004의 나이 부분은 승인된 정책을 기준으로 재평가한다. **worker G의 우연한 진행이 나이 정책을 결정하는 현재 상태는 어느 대안에서도 허용하지 않는다.**

## 10. Absolute Timestamp and Temporal Field Contract

각 필드는 `ClockDomain / SemanticKind / Unit / Sentinel / EntityScope / CodecVersion`을 가진다. schema는 지원하는 game/DLC/mod content fingerprint에 연결한다.

| Kind | Canonical representation | 변환·보존 규칙 |
|---|---|---|
| LOCAL_INSTANT | ClockId + 논리 L 좌표 / local 이력 | game-relative timestamp는 anchor 차이로 native에 투영. offline World 경과분을 더하지 않음 |
| LOCAL_ABSOLUTE_CALENDAR | Ks + L / entity birth coordinate | engine absolute anchor까지 반영. 날짜·계절·birth의 의미 보존 |
| LOCAL_DEADLINE | local due L 또는 명시적인 remaining ticks | due/remaining을 구분. 도메인 이동 시 remaining duration을 새 anchor에 연결 |
| WORLD_DEADLINE | WorldId + due W + operation/policy revision | 서버만 만료를 판정. native quest/letter는 view 또는 authorized event consumer |
| DURATION / COUNTER | ageTicks / ticksLeftThisToil / rotProgress 등 정의된 값 | 시간 원점 이동으로 변경하지 않음. 해당 mechanic 실행으로만 갱신 |
| INTERVAL_DEBT / PHASE | tickDelta, fraction, periodic bucket state 등 | frozen 기간은 부채에 추가하지 않음. 기존 local interval 잔여값은 지우지 않음 |
| NON_TIME_ID | loadID / JobID / entity revision 등 | rebase 대상 아님. 큰 정수라는 사실은 시간 필드라는 증거가 아님 |
| SENTINEL / UNSET | 필드별 -1/null/특수값 | sentinel이면 변환하지 않음. 모든 -1에 같은 의미를 부여하지 않음 |
| UNSUPPORTED / AMBIGUOUS | 불완전한 temporal metadata | admission/merge 거절 또는 REPAIR_REQUIRED. silent default 금지 |

같은 clock domain의 game-relative native timestamp `x`에만 `x'=G0new+(x-G0old)`를 적용할 수 있다. absolute timestamp는 Abs anchor를 사용한다. remaining duration에 같은 delta를 더하지 않는다. **W deadline을 local timestamp로 바꿔 그 권한을 engine에 넘기지 않는다.**

MapHeld/residence context, mapless entity, global getter 접근을 구분한다. mapless라고 무조건 W를 배정하지 않는다. supported registry에 clock 소속과 접근 경로를 선언해야 한다.

manifest가 지정했다는 이유만으로 임의 CLR type, callback 또는 저장된 코드를 실행하지 않는다. typed registry, supported schema, content hash 및 reference 검증이 먼저다.

## 11. Subsystem Temporal Responsibility

| Subsystem | Active target | Frozen Settlement | 경계 검증 |
|---|---|---|---|
| Needs | 실제 vanilla local interval/조건으로 진행 | hunger/rest 등의 일반 tick 0. asset 명령은 needs tick을 발생시키지 않음 | 값, interval 잔여값, 첫 resume 결과 |
| Jobs / toil | L 기준 진행. queue idle/W 진행을 job timeout으로 해석하지 않음 | job/remaining toil/local timestamp 보존 | target reference, local expiry, L/control revision |
| Hediffs / wounds | severity/age/healing/expiry의 실제 local mechanics | 일반 진행 정지. 외부 인가된 medical effect는 별도 operation | duration과 absolute expiry 구분, body-part graph |
| Biological / chronological age | §9의 승인 정책과 vanilla 효과 | 승인된 frozen semantics. raw G 파생값을 자동 채택하지 않음 | getter, growth deadline, birthday/hash phase, cryo |
| Plants / crops | target local season/light/growth/age/long interval | growth/age 보존. offline W를 long tick 부채로 만들지 않음 | 유효한 crop, local season, 첫 resume 경계 |
| Power | 대상 network/component/소비량의 실제 local 진행 | 에너지와 timer 보존. W 경과분으로 충·방전하지 않음 | storedPower, network state/phase, load 초기화 |
| Bills / production | 실제 local work/job/rate/recipe | progress/order 보존. W 기준 server duty와 구분 | 유효한 nonempty bill, 작업 잔여량, recipe/ingredient와 inventory revision |
| Held / contained inventory | residence clock에 따른 mechanics. 인가된 target MapHeld dispatch | rot/recharge 등의 일반 진행 정지. trade/tax는 자산 변경 | quantity/container, rot, suspended contents |
| Fire / weather / environment | 대상의 정당한 effect와 필요한 helper | background progression 없음 | helper 허용 범위, out-of-scope callback |
| Map components / mod hooks | scope/clock을 선언한 helper 실행 | canonical 변경과 target 계산에 대한 외부 영향 제한 | unknown global getter/mutation 검출. 기능 전체를 끄는 방식은 미충족 |
| World-dependent map event | W 기준 server event를 tick/control barrier에서 적용 | 필요한 domain/asset effect만 적용, 일반 simulation 재개 안 함 | event dedup/W revision, entry authority |

offline freeze를 모든 local state가 절대 불변이라는 뜻으로 확대하지 않는다. offline battle/shop/tax/ownership change는 SRS가 요구하는 상태 변경이다. **어떤 operation으로 상태가 변했는지와 local simulation tick을 소비했는지를 각각 기록**한다.

## 12. World Cooldowns, Events and Configuration

### 12.1 서버 소유 deadline

WarPending/war cooldown/Alliance cooldown/Betrayer extension/Ruins expiry/NPC recovery/Tax cycle은 W를 따른다. local pause, peaceful speed 또는 client 날짜 표시로 기한을 바꾸지 않는다.

```text
WorldDeadline = (WorldId, DueWorldTick, ConfigRevision, CreationOperationId)
Eligibility = CurrentCommittedW >= DueWorldTick AND current domain preconditions
```

서버 내부 SystemPrincipal이 기한 처리를 실행한다. deadline/effect/operation receipt/outbox는 durable하게 일치해야 한다. restart/retry가 같은 만료를 중복 적용하지 않는다. 설정 변경이 이후 생성 deadline에만 적용되는지, 기존 deadline도 변경하는지는 versioned policy로 명시한다. 남은 기한을 임의로 재계산하지 않는다.

NPC restock은 SRS-FR-219의 vanilla 친화성 요구를 보존한다. 필요한 native world helper/backend는 W 기준 요청과 canonical NPC inventory authority에 연결하고, target worker의 incidental World tick 결과로 restock을 확정하지 않는다. 현재 Server가 vanilla restock 전체를 구현했다는 증거는 없다. 구체적인 stock canonicalization은 ADR-003의 검토 대상이다.

### 12.2 Durable pacing과 서버 downtime

ADR-001의 committed watermark 계약을 유지한다. durable W보다 앞선 시간을 authoritative하게 발표하거나 해당 시간의 domain ACK를 완료하지 않는다. batch 진행은 가능하나, 넘어간 due event를 순서대로 검사하고 commit해야 한다.

restart는 durable W/config/deadline에서 복원한다. 이전 프로세스의 M을 새 프로세스의 M에서 빼지 않는다. **권장 downtime 정책은 서버 정지 중 ΔW=0, 마지막 committed W부터 재개**다. FR-001은 접속자 0명을 다루며 서버 정지 중 wall-clock catch-up은 명시하지 않으므로 Master 승인 대기 사항이다.

wall-clock catch-up을 선택하면 trusted elapsed source, 상한, clock rollback 방어, rate policy segments 및 due event의 ordered durable application/audit가 필요하다. 어느 정책에서도 정지된 Local clock을 자동 catch-up하지 않는다.

### 12.3 Tactical pause 중 World event

peaceful map이 pause여도 W 기반 War 권한·기한은 진행한다. receipt를 가진 **zero-tick control barrier**에서 event를 반영할 수 있어야 한다. hostile 전환을 다음 physics tick까지 기다려 영구 정지하지 않는다. 현재 L 경계에서 phase/speed/authority를 변경하고, 첫 hostile effect 전에 1x/no-pause를 적용한다.

World 상태가 combat에 영향을 주면 server-issued ordered event와 관련 DomainRevision을 사용한다. native World manager 전체를 tick해 정치 deadline을 다시 실행하지 않는다. 사용자 pause와 fault freeze는 다른 상태다.

### 12.4 Tax와 offline inventory

SRS-BR-016에 따라 다음 cycle은 `LastActualCollectionW + CycleWorldTicks`다. 징수 후보 deadline만으로 income/delinquency를 생성하지 않는다.

offline trade/tax로 InventoryRevision/SaveRevision이 증가해도 L은 같을 수 있다. 수령 World 시간은 transaction/audit metadata이고, frozen Map에 item을 물질화하는 local anchor는 L이다. freshness/charge 등은 이동 정책에 따라 보존한다. 날짜 차이를 전체 inventory의 aging delta로 만들지 않는다.

active Tactical 자산 변경은 current lease/clock의 zero-tick control barrier 또는 authorized local tick 경계에서 순서화한다. worker의 materialized inventory와 canonical inventory가 동일 operation을 가리켜야 한다. 전투가 끝날 때까지 shop을 일괄 비활성화하는 것을 기본 해결책으로 삼지 않는다. 구체적인 canonicalization/merge 알고리즘은 **ADR-003**, durable multi-state commit은 **ADR-004**의 책임이다.

## 13. Save / Load / Reload Lifecycle

| Phase | Clock contract | Gate |
|---|---|---|
| SELECTING | 현재 accepted save/time/inventory revision set 선택 | 과거 local artifact를 canonical source로 사용하지 않음 |
| LOAD_FENCED | principal/lease, expected anchor, no-tick policy를 **loader 이전**에 설정 | normal/rare/long/global/mod dispatch 통제 |
| MATERIALIZING | Def/reference/typed temporal state를 local projection으로 복원 | 미지원 시간 필드·불완전 graph를 성공 처리하지 않음 |
| POSTLOAD_VALIDATING | local tick delta 0, reference/getter/phase 비교 | normalization의 target/foreign effect와 계산 영향 검증 |
| READY_FROZEN | anchor/ref graph/counter/phase/capability 일치 | 자발적 tick 없음. gameplay 시작은 별도 transition |
| ACTIVE | 완료된 target step으로 L/N 갱신 | queue 처리 전후 lease/epoch/time fence |
| CHECKPOINT_BARRIER | graph와 temporal manifest를 같은 L 경계에서 capture | export 중 pointer/L watermark를 전진시키지 않음 |
| EXTRACTING / PREPARED | private .rws에서 scoped graph/time candidate 추출 | full context를 canonical outcome으로 자동 승격하지 않음 |
| COMMITTED | receipt와 target state/time/revisions가 같은 accepted boundary | ACK 소실은 조회로 복구. effect/time 재적용 없음 |
| RECOVERING / QUARANTINED | 미복구 state/clock을 정상 상태로 발표하지 않음 | recovery horizon 복원·검증 전 writer 재개 금지 |

load tick fence만으로 post-load normalization/ID 재생성/getter 평가를 모두 막을 수는 없다. semantic 검증과 extraction scope 검증도 필요하다.

reload 성공은 파일이 존재하고 Playing 상태라는 뜻이 아니다. content/clock anchor/revision/timer/holder/assignment가 일치해야 시간적으로 READY다. missing Def 후의 false-success publication도 이 gate에서 거절한다.

## 14. Tactical Admission

1. 서버가 authenticated actor와 legal entry를 검증한다. offline 일반 Visit는 SRS-FR-095에 따르되 합법적인 offline attack은 허용한다.
2. target의 **현재 coherent base**를 선택한다: SaveRevision/InventoryRevision/SettlementRevision/LocalClockId/TimeRevision/L/관련 ConfigRevision. online ordinary writer는 handoff barrier에서 정지하고 미반영 accepted progress를 조정한다.
3. old writer를 fence하고 current lease/temporal grant를 durable하게 등록한다. old writer의 물리적 종료 또는 안전 격리를 확인하기 전 같은 clock의 두 번째 writer를 실행하지 않는다.
4. visitor/attacker entity를 진입시킬 때 값과 remaining timer를 보존하고 서로 다른 날짜 경계를 변환한다. 출신 Map과 대상 Map에서 같은 Pawn을 이중 tick/복제하지 않는다.
5. base/local clock/engine anchor/phase/bounded pacing policy를 worker에 전달하고 LOAD_FENCED부터 복원한다.
6. input 권한을 발급하기 전에 getter/graph/time gate를 통과한다. Tactical 시작점은 **대상의 기존 L**이다.
7. hostile이면 첫 effect 전 1x/no user pause. peaceful이면 server-accepted 입력 순서로 Last Input Wins를 적용한다. W는 계속 진행한다.

Owner login은 새로운 Map/clock을 만들지 않는다. 현재 session에서 ControlRevision을 전환한다. logout AI takeover와 peaceful→hostile 전환도 동일 L/session lineage를 유지한다.

## 15. Tactical Conclusion and Canonical Publication

1. 특정 L 경계에서 대상 simulation을 freeze하고 input/external event watermark와 graph/time state를 capture한다.
2. 인가된 scoped graph와 temporal candidate를 추출한다. `TicksSimulated` 보고만으로 모든 entity의 시간 무결성을 인정하지 않는다.
3. read-set/revision을 재검증한다. 중간 tax/shop/ownership 변경이 있으면 blind overwrite를 거절하고 authorized ordered effect를 조정한다.
4. **시간 계약:** canonical target graph, accepted L/TimeRevision, 관련 inventory/save/ownership revisions와 operation receipt는 하나의 논리적 accepted boundary를 가리켜야 한다. immutable artifact의 durable 준비 및 pointer/DB commit·복구 방식은 ADR-004가 결정한다. 이 단계의 inventory canonicalization은 ADR-003이 결정한다.
5. 실제 death/injury/destruction/loot를 final graph에 보존한다. clock만 되돌려 피해를 취소하거나 outcome만 확정하고 old timer/inventory를 남기지 않는다.
6. 다음 writer에 current canonical state를 전달한다. conquest/owner 변경은 L을 reset하지 않는다.
7. Owner offline이면 ordinary freeze, online이면 §16의 resume gate를 적용한다. 마지막 참가자 퇴장으로 검증되지 않은 old save가 자동 재개되지 않는다.

기술 barrier는 사용자 pause가 아니다. barrier/overload/crash로 W를 되돌리거나 hostile 사용자 pause를 되살리지 않는다. 반응 시간은 검증 대상이나, 본 ADR에서 SRS-NFR-011의 최종 수치를 선결정하지 않는다.

## 16. Ordinary-local Simulation Resume

**Resume은 current canonical materialization과 새 writer authorization이다. Owner의 오래된 full save를 여는 것으로 대체할 수 없다.**

- 현재 accepted target L/graph를 이어받는다. 전투 중 진행된 L은 보존하며, 공격받지 않은 다른 정착지는 그 정착지의 원래 L을 유지한다.
- pause/offline 동안의 W 경과분을 needs/jobs/hediffs/plants/power/bills의 catch-up 부채로 더하지 않는다. 기존 local remaining duration/interval debt는 보존한다.
- age/calendar는 승인된 정책을 적용한다. W와 L의 차이를 보정해야 할 오류로 취급하지 않는다.
- fresh load의 0-tick 상태와 첫 local tick/rare·long interval 결과를 같은 clock의 정상 pause/resume reference와 비교한다. 유효한 expiry/bill/plant가 필요하다.
- 같은 client 프로세스에 다른 local 날짜의 active Map이 있으면 raw global G 변경으로 충돌시키지 않는다. 승인된 clock-island routing 또는 검증된 C2 virtualization이 필요하다.
- client의 elapsed counter만으로 local save를 채택하지 않는다. extreme L 증가로 production/age 이득을 위조하지 못하도록 grant/revision을 확인한다. 결과 provenance와 inventory 합법성은 ADR-003에서 결정한다.
- disconnect 시 ordinary writer를 fence하고 freeze를 durable하게 기록한다. W 및 인가된 offline asset operation은 계속 진행한다.

**일반 owner client의 multi-map 시간 분리와 결과 provenance는 아직 미해결 경계**다. 이를 구현 완료로 표시하지 않는다. full-save publication이 부적합하다는 이유로 ordinary resume을 영구 생략하거나 다른 정착지 사용을 금지하지 않는다. 실제 writer 위치·신뢰·렌더링 topology의 확대는 Master의 별도 결정이 필요하다.

## 17. Crash / Restart and Time Recovery

### 17.1 World restart

durable W/config/deadline/operation/outbox를 복원·검증한다. 정상 restart로 발표된 W/revision이 후퇴하지 않는다. 현재 memory ticker의 initial0 시작은 이 요구를 충족하지 않는다.

### 17.2 Worker restart

lease를 revoke/fence하고 old process 종료 또는 안전 격리를 확인한다. checkpoint는 `Lcheckpoint / EngineAnchor / EventWatermark / InputWatermark / RecoveryHorizon`과 연결한다.

- 내부 recovery는 이전 checkpoint L에서 시작할 수 있다. 그러나 **accepted horizon 미만의 상태를 정상 READY로 발표하지 않는다.**
- replay를 사용하려면 ordered input뿐 아니라 AI/RNG/external effect까지 accepted L/state로 복원됨을 입증해야 한다.
- 결정성 replay가 미검증 또는 불가능하면 recoverable state/effect를 보존하는 별도 방식이 필요하다. `L += missingTicks`만으로 누락 효과를 재생성했다고 처리하지 않는다.
- 증거가 부족하면 QUARANTINED/REPAIR_REQUIRED다. 전투 전 save를 현재 정상 상태로 되살려 committed death/loot를 취소하지 않는다.

vanilla/mod replay 결정성은 tested fact가 아니다. 구체적인 복구 방식은 ADR-002 및 미래 ADR-004와 조정하며, 본 ADR은 accepted graph와 accepted 시간의 공동 복원을 요구한다.

### 17.3 Commit 중 중단

commit 이전 prepared artifact는 operation reconciliation 대상이다. 그 존재만으로 canonical L/result가 증가하지 않는다. commit 이후 ACK 소실은 receipt 조회로 복구하며 같은 tick/graph effect를 재적용하지 않는다.

committed pointer의 artifact/time manifest가 없거나 손상되면 repair 상태다. old checkpoint의 clock record를 새 receipt에 붙여 정상처럼 보이게 하지 않는다. 운영자가 history rollback을 선택하더라도 정상 restart와 구분된 명시적 lineage/migration/audit가 필요하다.

## 18. Stale Save / Stale Time Rejection

signature/hash만으로 temporal authority가 성립하지 않는다. 서버의 current grant와 revision/read-set 조회가 필요하다.

| 제출 상태 | 처리 |
|---|---|
| 잘못된 WorldId / SettlementId / MapIdentity / LocalClockId | 다른 timeline 적용 거절 |
| old SessionEpoch / LeaseGeneration / ordinary writer generation | 미적용 command/result fence. historical receipt 조회와 구분 |
| save hash는 같지만 old Save/Inventory/TimeRevision | canonical replacement 거절. 인가된 recovery/reconcile만 허용 |
| Lsubmitted < accepted horizon | 정상 resume/commit 거절. recovery-only 내부 stage에서만 허용 |
| Lsubmitted가 current grant/검증된 processed step을 초과 | 거절. client wall-clock/TicksGame을 권한 증명으로 사용하지 않음 |
| 같은 OperationId, 다른 payload/clock range | collision 거절·audit |
| 같은 OperationId, 같은 완료 receipt | 기존 결과 반환. time/asset 재적용 없음 |
| engine anchor / gameStartAbs / policy/schema/content hash 불일치 | materialization/merge 거절. default clock 생성 금지 |
| 필수 필드 누락/unknown critical temporal state/post-load entity loss | LOAD_FAILED 또는 REPAIR_REQUIRED. READY/EXPORT 승격 금지 |
| full worker Game을 whole-world canonical replacement로 제출 | 권장 B2 endpoint 계약 위반으로 거절 |

W가 진행한다는 이유만으로 target candidate를 무조건 stale로 만들지 않는다. 필요한 domain read-set와 ordered external event watermark를 검사한다. 매 Map step에 global WorldRevision 전체 일치를 요구하면 정상 World 진행 때문에 target commit이 계속 실패할 수 있다.

## 19. Persistence and Revision Model

아래는 **최소 논리 계약** 제안이며 DB 제품, inventory merge 표현, distributed commit 알고리즘을 결정하지 않는다.

| Record | 최소 의미 |
|---|---|
| WorldTimeState | WorldId, CommittedW, WorldCalendarOrigin, RatePolicy/ConfigRevision, TimeSchemaVersion, due-event/outbox 연계 |
| LocalTimeState | LocalClockId, Settlement/MapIdentity, acceptedL, Ks, TimeRevision, lifecycle/writer fence, TemporalPolicyVersion, current SaveRevision 연계 |
| MaterializationManifest | base Save/Inventory/Settlement revisions, anchor(L0/G0/A0), engine/DLC/mod/schema fingerprint, scope/reference graph hash |
| ExecutionGrant | session/lease/instance/writer generation, phase/rate policy, base L, ordered input/events, permitted write-set |
| CheckpointTimeState | completed L/N, EngineClockEpoch/anchor, durable input/event watermark, interval/phase/typed state, artifact hash |
| OperationReceipt | OperationId/PayloadHash, base/result revision과 clock horizon, scoped graph/artifact hash, terminal state |

TimeRevision은 매 tick의 DB transaction을 강제하지 않는다. admission/handoff/checkpoint/policy/result 등 **coherent accepted boundary**에서 갱신한다. runtime-applied L과 durable-accepted L을 구분하고 ACK/replication이 어느 horizon까지 durable effect를 약속하는지 정의한다.

시간 관점의 최소 논리 commit 단위는 operation/result, 영향받은 graph/save/inventory/ownership/time revision set와 audit/outbox다. engine 외부 artifact까지 DB transaction 하나로 자동 원자화된다고 가정하지 않는다. ADR-001/002의 immutable artifact와 coherent pointer 계약을 유지하되 구체적 multi-state commit/repair는 ADR-004로 넘긴다.

## 20. Interaction with ADR-003 and ADR-004

### 20.1 상태와 책임

Master 확인에 따라 두 ADR은 **NOT YET AUTHORED / FUTURE DEPENDENT ADR**다. 정식 원문이 없으며 원문 계약을 인용·대조하거나 ACCEPTED라고 표현하지 않는다.

- **ADR-003 — Canonical Inventory / Save Provenance:** canonical inventory authority, Save/InventoryRevision, player local save, offline trade/tax, active-map inventory, concurrent mutation, stale-save/duplication 방지, reconnect, ordinary provenance와 Tactical entity canonicalization을 결정할 예정이다.
- **ADR-004 — Distributed Ownership Transaction / Repair:** artifact와 Server DB commit 경계, ownership/occupation/destroy/conquest, inventory/Caravan multi-state transaction, durable prepare/commit, partial failure/rollback/repair/quarantine, idempotency/fencing과 Tactical durable publication을 결정할 예정이다.

Master의 현재 provisional 방향인 **full worker save 전체를 canonical outcome으로 자동 승격하지 않음**을 반영한다. 이는 본 ADR의 B2 권장 경계와 부합하나 scoped merge의 실제 feasibility PASS 또는 최종 채택을 뜻하지 않는다.

### 20.2 ADR-006A가 요구하는 선행 인터페이스

| 시간·publication 계약 | ADR-003에 요구하는 인터페이스 | ADR-004에 요구하는 인터페이스 |
|---|---|---|
| Entity residence / authority | entity/location/holder와 ClockDomain, ordinary/tactical/world writer 구분 | 동일 entity/clock의 current lease/writer generation을 transaction에 fence |
| Coherent revision set | inventory/save base와 result가 LocalClockId/L/TimeRevision에 연결 | graph/time/ownership/revision/receipt가 한 accepted boundary를 가리키도록 복구 가능한 commit |
| Zero-tick external operation | offline trade/tax 및 active-map 자산 변경에서 ΔL=0 허용, quantity/권한 canonicalization | 해당 effect의 artifact 적용과 durable state를 조정. general simulation 재개 금지 |
| Cross-domain 이동 | quantity/location/identity 보존, residence clock/remaining timer 인계 | ingress/egress 다중 state와 clock projection의 partial failure 격리 |
| Result publication | 인가된 target entity와 explicit cross-boundary write-set만 canonicalization | full context는 private checkpoint. target outcome pointer와 clock manifest의 joint recovery |
| Stale save / reconnect | current Save/Inventory/TimeRevision과 ordinary provenance 확인 | old lease/operation 결과 fence, committed receipt의 idempotent 재조회 |
| Ordinary resume | current canonical graph/inventory를 새 writer에 제공 | current L/time manifest의 loader-before fence, interruption/handoff 복구 |
| Crash / repair | 완료된 quantity/effect가 old save로 중복·취소되지 않음 | accepted temporal horizon보다 오래된 graph를 정상 READY로 발표하지 않음 |

이 표는 상세 inventory merge나 DB/artifact commit 알고리즘을 선결정하지 않는다. ADR-003/004는 작성 시 **채택된 시간-domain 및 publication-boundary 결정을 입력 계약으로 추적**해야 한다. 본 ADR이 PROPOSED인 동안은 충돌을 Master에게 제출하고, 서로 독립적으로 반대 계약을 확정하지 않는다.

### 20.3 의존 순서와 충돌 처리

1. Master가 ADR-006A의 clock/policy/publication 방향을 결정한다.
2. ADR-003은 canonical inventory/provenance와 시간 manifest의 입력·출력 관계를 설계한다.
3. ADR-004는 그 write-set와 시간 horizon에 대한 durable multi-state commit/repair를 설계한다. ADR-003/004의 설계 검토는 병행할 수 있으나 상대방의 미확정 세부사항을 사실로 가정하지 않는다.
4. full-save publication, ownership 변경 시 clock reset, W delta를 local inventory aging으로 사용하는 안은 명시적인 충돌이다. Master 변경 결정 없이 도입하지 않는다.
5. ADR-003/004의 정식 원문과 QA 대조 전에는 alignment 완료/PASS라고 하지 않는다.

## 21. Smallest Necessary Validation — No Automatic New Prototype

이번 작업에서 새 게임 프로세스나 runtime PoC를 실행하지 않았다. 다음 검증은 **선택한 option의 미입증 경계에 필요한 최소 조건**이다. 이미 확인된 동작을 반복 확인하려고 자동으로 prototype을 발행하지 않는다. 가능한 검증은 static contract, pure unit 또는 기존 scratch harness의 좁은 acceptance test를 사용한다.

| 질문 | 기존 증거 충분? | 필요한 최소 검증 / 이유 |
|---|---|---|
| W/G/L을 분리해야 하는가 | YES: SRS, chrono leak, installed getter | 새 runtime 불필요. schema/static 계약 검토 |
| 실제 engine bootstrap/scoped held rot/fire/power/cooperative loop가 가능한가 | 확인한 subset은 YES | 같은 기능 확인만을 위한 새 PoC 불필요. 변경 시 기존 regression 재사용 |
| W deadline의 durable dedup/restart/config segments | engine 시험 불필요 | fake monotonic clock + 실제 persistence/operation test. engine 전체 실행 대신 실패 주입 |
| B2 extraction이 foreign reference/quantity/time을 유지하는가 | NO | 다른 local 날짜를 가진 valid native fixture의 target 변경 1건+foreign reference 1건을 추출→canonical base에 적용→fresh load. foreign canonical graph 불변, target relation/timer 보존 및 foreign clock 조회가 target 계산에 잘못 유입되지 않는지 확인 |
| load 이전 clock fence/getter normalization이 가능한가 | NO: escape가 재현됨 | 0-tick load/fresh reload. 유효한 Pawn+expiry hediff/job/crop/power/nonempty bill/held rot의 semantic 비교. 계획만으로 normalization 안전성을 증명할 수 없음 |
| 첫 ordinary resume의 rare/long phase/debt 보존 | NO | 서로 다른 local 날짜 2개에서 reference freeze/resume과 첫 tick 및 한 interval 경계를 비교. 대량 catch-up 시험은 불필요 |
| C1의 package/reference closure | 선택 시에만 NO | 기존 Map+held container+off-map reference 하나를 package/load/export. 유사 새 Map 생성으로 대체하지 않음 |
| C2의 per-map virtualization | 선택 시에만 NO | 다른 local 날짜 2개를 교대로 dispatch, getter/rare phase/save-reload 비교. 단일 getter patch 성공만으로 불충분 |
| engine int range/anchor rollover | NO, 장기 운영 설계 필요 | overflow 인접 경계만 typed age/deadline/phase/calendar 비교. production clock 변경 금지 |
| autonomous AI/external effect recovery | replay 결정성 미입증 | 복구 방식 선택 후 critical effect 하나의 crash/recover 비교. RNG seed만으로 static proof 불가 |
| ordinary writer trust / ADR-003/004 연동 | 책임·계약 결정이 선행 | 자동 prototype 발행 안 함. 문서 계약을 먼저 검토한 후 남은 engine 경계만 실검증 |

기존 complex fixture의 ID/verb/master/crop/bill 불비를 그대로 두고 전수 PASS를 발표하지 않는다. 유효한 engine-generated graph와 실패를 탐지하는 oracle이 선행되어야 한다. 이는 모든 RimWorld/mod를 한 번에 검증하는 거대 PoC 요구가 아니라 선택된 supported profile의 시간 계약을 검증하는 최소 경계다.

## 22. Invariants and QA Acceptance Criteria

### 22.1 Invariants

- **INV-TIME-001:** W와 L/G는 다른 authority domain. worker/client는 W를 확정하지 않는다.
- **INV-TIME-002:** offline 일반 simulation의 ΔL=0. 인가된 offline battle/asset operation과 구분한다.
- **INV-TIME-003:** 완료한 target N steps에만 L=L0+N. pause/idle/load/export는 step이 아니다.
- **INV-TIME-004:** LocalClockId의 active writer는 최대 1개. session/owner/worker 변경은 clock reset이 아니다.
- **INV-TIME-005:** 서로 다른 local 날짜 사이 이동은 biological age/remaining duration을 바꾸지 않으며 승인된 chronological 정책을 따른다.
- **INV-TIME-006:** server W deadline은 local pause/speed와 무관하고 business effect는 durable operation당 최대 한 번이다.
- **INV-TIME-007:** 권장 B2에서 raw full worker Game은 canonical whole-world replacement 권한이 없다.
- **INV-TIME-008:** graph/save/inventory/time revision과 recovery horizon은 같은 accepted boundary를 가리킨다.
- **INV-TIME-009:** LOAD/RELOAD/READY는 의도하지 않은 target tick이나 foreign canonical effect를 만들지 않는다. normalization/getter도 검증한다.
- **INV-TIME-010:** stale generation/clock manifest/save로 일반 write/resume하지 않는다. retry로 time을 중복 진행하지 않는다.
- **INV-TIME-011:** unknown timestamp에 silent default/rebase를 적용하지 않으며 overflow를 clock reset으로 숨기지 않는다.
- **INV-TIME-012:** frozen inventory의 정당한 trade/tax는 ΔL=0으로 반영할 수 있다.

### 22.2 Acceptance matrix

| ID | 기대 결과 | 현재 증거 상태 |
|---|---|---|
| AC-TIME-01 | 접속자 0명 W 진행, local pause/offline의 W deadline 영향 0, coherent restart | 계약 명확. durable temporal 통합 PASS 미제출 |
| AC-TIME-02 | W 겨울/MapA 여름/MapB 가을 유지, 날짜 차이를 오류 처리하지 않음 | 요구·설계 근거 있음. 실제 multi-clock projection 미검증 |
| AC-TIME-03 | offline ordinary L0, battle L0+N, 종료 후 offline freeze | scoped subset 개선 확인. proposed timeline publication 미구현 |
| AC-TIME-04 | age/needs/jobs/hediffs/crop/power/valid bill/held의 첫 resume이 reference와 일치 | 기존 FAIL 및 미검증 경계 존재 |
| AC-TIME-05 | extraction/apply 후 foreign graph/W 불변, target 실제 효과 보존 | 구현·검증 미실시 |
| AC-TIME-06 | pre-load fence, 0-tick reload, semantic READY, missing Def 거절 | ENGINE-02 load/manifest 반례 존재 |
| AC-TIME-07 | offline 자산 즉시 반영, L 불변, stale owner save duplication 0 | 미래 ADR-003/004 통합 필요 |
| AC-TIME-08 | 다른 날짜 domain 이동에서 age/duration/quantity/location 보존 | typed 계약 제안. runtime 미검증 |
| AC-TIME-09 | duplicate/reorder/ACK loss/restart의 effect/time 중복 0 | ADR-001 계약 있음. temporal 통합 미실증 |
| AC-TIME-10 | crash 후 accepted horizon 미만 normal resume 없음, committed death/loot 취소 0 | 복구 구현 미실증 |
| AC-TIME-11 | START 전 idle/export 시간 유입 없음, hostile 1x/no pause, control responsive | warm 60TPS subset 확인. cold-start/RUN 문제 OPEN |
| AC-TIME-12 | ADR-003/004가 시간/write-set/publication/recovery 입력 계약 추적 | NOT YET AUTHORED. 정식 alignment 미검증 |

이 표는 acceptance 조건이며 문서 작성이 PASS 증거는 아니다. 기존 QA-001~014와 QA-ENGINE-001~008은 수정과 독립 증거가 제출될 때까지 OPEN이다.

## 23. Decision Requests and Residual Architecture Risks

### DREQ-TIME-001 — Age / transit semantics

[DECISION REQUEST]

- **Affected Requirement:** SRS-FR-002/003/098/153/155. 세부 나이 clock은 SRS 미지정.
- **Observed Conflict:** engine chronological age는 global Abs, local 날짜는 독립이다. 이동/transit physiology를 정책 없이 환산할 수 없다.
- **Code Evidence:** IL6 age getter, E2 chronological +51,481, SRS §3.1.
- **Option A:** residence-domain local chronological/biological 정책과 typed migration. transit 진행 backend·정책 명시.
- **Option B:** chronological만 universal W, biological은 실제 simulation. eligibility/DLC/mod 영향도 명시.
- **Trade-offs:** A는 local freeze/날짜와 잘 맞지만 migration codec 필요. B는 세계 기준 나이 일관성이 있으나 local 날짜와의 차이 및 getter adapter 부담.
- **Recommendation:** A 제안. transit 정책은 명시적으로 결정하고 worker G의 우연한 진행에 맡기지 않음.

### DREQ-TIME-002 — Server downtime

[DECISION REQUEST]

- **Affected Requirement:** SRS-FR-001, SRS-NFR-006, SRS-CFG-001.
- **Observed Conflict:** 접속자 0명일 때 진행은 필수. 서버 정지 중 wall-clock catch-up은 미지정.
- **Code Evidence:** SRS FR-001, ADR-001의 durable World watermark.
- **Option A:** 정지 중 ΔW=0, 마지막 committed W부터 재개.
- **Option B:** versioned trusted elapsed policy로 catch-up, due event ordered commit.
- **Trade-offs:** A는 운영 정지로 기한의 실제 날짜가 늘어남. B는 clock 조작/장기 catch-up/정치 effect burst 관리 필요.
- **Recommendation:** 초기 정책 A를 Master 승인 대상으로 제안. 정상 운영 중 접속자 0명의 W는 정지하지 않음.

### DREQ-TIME-003 — Publication / ordinary topology

[DECISION REQUEST]

- **Affected Requirement:** SRS-FR-002/003/098/155/206~208, SRS-NFR-004/006/007, SRS-CON-010.
- **Observed Conflict:** global G 하나와 독립 local 날짜, offline asset mutation이 충돌한다. Master의 full-save 자동 승격 금지 방향에 맞는 scoped publication·ordinary resume 경계가 필요하다.
- **Code Evidence:** E2 reload leak/manifest loss, installed getters/dispatch, ADR-002 ordinary provenance OPEN.
- **Option A:** B2 + target-scoped publication + clock-island routing 방향. ordinary writer/render/import topology는 별도 명시.
- **Option B:** A 또는 C2를 지원 profile에서 엄격히 검증해 채택. 필요하면 ordinary execution topology를 확대 변경.
- **Trade-offs:** A는 whole-world overwrite 위험을 줄이나 graph/time extraction과 ordinary routing 필요. B는 기존 full-save workflow 유지 가능성이 있으나 engine/DLC/mod interception 범위가 넓음.
- **Recommendation:** B2를 기본 방향으로 제안. ADR-003은 canonicalization/provenance, ADR-004는 durable commit/repair를 설계하며 시간 계약을 추적. full-save publication의 묵시적 승인 금지.

잔여 위험은 implicit foreign/global read, unknown mod field, phase/cache, cross-map 이동, ordinary provenance, nondeterministic recovery, engine int 범위다. 요구를 축소하지 않고 설계 결정과 최소 검증으로 구분한다.

## 24. Decision Status

**PROPOSED ONLY. Master 최종 결정 대기.**

- ADR-001 ACCEPTED 계약을 변경하지 않는다.
- ADR-002를 ACCEPTED로 승격하지 않는다. Candidate C의 temporal 경계를 보완하는 제안이다.
- ADR-003/004는 NOT YET AUTHORED / FUTURE DEPENDENT ADR이며 예정 범위만 Master 확인에 따라 사용한다.
- Production code, 기존 ADR, engine/game/server save를 수정하지 않는다.
- 수행한 작업은 요구·증거·소스 read-only 검토, installed engine metadata/IL 읽기, 본 ADR 및 QA 검증 metadata 작성이다.
- runtime 검증이 필요한 경계만 특정했다. 새 prototype 자동 발행, 기능 구현, 게임 재실행은 하지 않았다.
- Master 결정 대상은 B2 publication 방향, age/transit/downtime 정책과 ordinary multi-map execution 경계다. 상세 inventory merge/분산 commit은 미래 ADR로 넘긴다.

문서 검증은 [validation.json](<C:/Users/user/Desktop/RimMulti/QA-Baseline/TemporalADR-20261002/validation.json>)에 기록한다. 보호 입력 64건의 SHA-256 불변, Canonical SRS 번호 존재, local evidence link와 문서 구조를 검사했다. 이는 **문서·입력 무결성 확인**이며 새로운 runtime 시험 또는 Architecture Gate PASS가 아니다.

제안 채택과 구현의 독립 QA 합격은 다른 gate다. 기존 Architecture Gate를 본 문서만으로 변경하지 않는다.

