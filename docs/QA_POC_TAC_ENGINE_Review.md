# QA_POC_TAC_ENGINE_Review

- Work Package: **WP-QA-TAC-ENGINE-01**
- Role: Independent QA / Architecture Reviewer
- Date: **2026-10-02 (Asia/Seoul)**
- Canonical requirements: 최상위 [요구사항_명세서.md](<C:/Users/user/Desktop/RimMulti/요구사항_명세서.md>)만 사용
- Input: [POC_TAC_ENGINE_Evidence.md](<C:/Users/user/Desktop/RimMulti/POC_TAC_ENGINE_Evidence.md>)
- Architecture context: ADR-001 **ACCEPTED**, ADR-002 **PROVISIONALLY ACCEPTED**, Candidate C
- Production source modification/commit: **NONE**
- GUI/Computer Use: **NONE**. 프로세스·소켓·파일·engine IL·terminal harness만 사용
- Original QA-001~QA-014: **OPEN 유지**

## 1. Executive Verdict

**Gemini Verdict:** POC-TAC-ENGINE = PASS within tested scope.

**QA Verdict:** **기본 엔진 경로는 PASS within bounded tested scope. 전체 ENGINE architecture acceptance는 FAIL / Gate BLOCKED BY ARCHITECTURE.** 실제 worker 실행 가능성과 현재 실행 방식의 SRS 적합성은 별개다.

**Recommended ADR-002 Status:** **PROVISIONALLY ACCEPTED 유지 — OPTION 2. 먼저 POC-TAC-ENGINE-02.**

독립 재실행에서 actual RimWorld process → 기존 save load → 실제1,000 ticks/AI·needs 진행 → native export → 별도 fresh process reload는 성공했다. 그러나 다음 두 가지는 미검증이 아니라 **실제 실패 재현**이다.

1. 두 맵을 load한 뒤 current RUN_TICKS를 호출하면 비Target 맵의 Pawn/jobs/needs도 진행하고 worker-local World 상태도 변경된다.
2. 실제 required custom Def가 포함된 native save에서 해당 mod를 제외하면 아이템이 유실되는데도 bridge는 Playing 및 SAVED를 반환한다.

복잡한 소유권/assignment graph, selective tick adapter, normal1x cadence는 아직 NOT TESTED다. “100% entity integrity”, graphics-headless, capacity/remote latency PASS는 인정하지 않는다. C 자체의 불가능성은 입증되지 않았으므로 OPTION 3 REDESIGN REQUIRED까지 판정하지 않는다.

| Review scope | QA verdict |
|---|---|
| A actual executable supervised noninteractive launch | PASS |
| B existing actual .rws load | PASS |
| C actual engine tick + wander/jobs/needs | PASS, combat defense AI까지 아님 |
| D native save/export | PASS, artifact 생성 범위 |
| E fresh separate process reload | PASS |
| F selected Pawn/animal/manufactured-item semantic fields | PASS in specified fields; full semantic graph PARTIAL |
| Multi-map isolation | **FAIL** |
| Worker World Tick exclusion | **FAIL** for current worker; 중앙 서버 World Time 변화는 미측정 |
| Complex ownership/assignment graph | **NOT TESTED** |
| Required mod/Def absence safe rejection | **FAIL** |
| Two loaded workers concurrent burst + exports | PASS in simple fixture scope |
| Normal1x, heartbeat responsiveness, tactical latency/capacity | NOT TESTED / current long batch servicing defect confirmed |

실제 판정 입력을 [review-verification.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/review-verification.json>)에 보존했다. boolean true인 “failure reproduced”는 architecture PASS라는 뜻이 아니다.

## 2. Evidence Independently Verified

### Evidence inventory

| ID | Evidence | Scope |
|---|---|---|
| E-01 | [independent_run.py](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/independent_run.py>) / [console](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/independent-run-console.txt>) / [results](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/run-results.json>) | Actual exe launch, core lifecycle, long command, F01/F02/F05 |
| E-02 | [Independent1 player.log](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/Independent1/player.log>) / [launch](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/Independent1/launch.json>) / [native export](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/Independent1/Saves/IndependentExport.rws>) | actual engine/version/device/profile/load/export |
| E-03 | [Independent2 player.log](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/Independent2/player.log>) / [fresh snapshot](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/Independent2/reloaded.txt>) / [fresh native export](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/Independent2/Saves/ReloadExport.rws>) | new PID/profile, export reload, native semantic fields |
| E-04 | [semantic-audit.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/semantic-audit.json>) / [human-field-diffs.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/human-field-diffs.json>) | XML subtree vs snapshot audit, 제외 범위 명시 |
| E-05 | [EngineIL source](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/EngineIL/Program.cs>) / [actual engine IL](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/engine-il.txt>) | installed Assembly-CSharp metadata, no hypothetical API |
| E-06 | [multi-map harness](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/multi_map_run.py>) / [fixture contract v2](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/two-map-fixture-contract-v2.json>) / [v2 console](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/multi-map-console-v2.txt>) | scratch2map test save, nonTarget progression |
| E-07 | [MultiMapV2 Before](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/MultiMapV2/Saves/Before.rws>) / [After](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/MultiMapV2/Saves/After.rws>) / [log](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/MultiMapV2/player.log>) | same2maps pre/post native saves, error-free v2 load/tick/export path |
| E-08 | [dependency harness](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/dependency_run.py>) / [fixture builder](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/build_dependency_fixture.py>) / [dependency-results.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/dependency-results.json>) | actual required custom Def positive→absent negative |
| E-09 | [RequiresCustomDef native save](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/DependencyPresent/Saves/RequiresCustomDef.rws>) / [Absent log](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/DependencyAbsent/player.log:43>) / [loss re-export](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/DependencyAbsent/Saves/MissingDefResult.rws>) | custom item1→0, Playing/SAVED despite loader errors |
| E-10 | [capacity harness](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/capacity_run.py>) / [capacity-results.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/capacity-results.json>) | 2 loaded maps/ports, simultaneous10,000 ticks, CPU/RAM sample, export, F04 kill |
| E-11 | [input before hashes](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/input-hashes-before.json>) / [external before hashes](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/external-hashes-before.json>) / [protection-after.json](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/protection-after.json>) | 55 inputs unchanged, original save/bridge DLL/engine exe+DLL unchanged, cleanup |
| E-12 | [reviewed Bridge source copy](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/GeminiSourceReviewed/WorkerBridge.cs>) / [reviewed Supervisor source](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/GeminiSourceReviewed/TacticalSupervisor.cs>) / [multi-instance probe](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/GeminiSourceReviewed/test_multi_instance.ps1>) | readonly original scratch implementations captured for line-level review |

### Independent execution method

- Gemini Supervisor를 그대로 실행하면 hard-coded scratch directory를 재귀 삭제하므로 실행하지 않았다. 기존 evidence를 보존하고 별도 Python supervisor/harness를 workspace QA 경로에 작성했다.
- 실제 exe: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe`.
- arguments: `-batchmode -savedatafolder=<QA profile> -logfile <QA profile/player.log> -bridgeport=<unique port>`.
- Python subprocess에 hidden startup/CREATE_NO_WINDOW를 설정했다. profiles/ports는 기존291xx 테스트와 분리된29220~29227.
- original WorkerBridge DLL/junction은 그대로 사용했다. 단 required dependency 테스트만 별도 XML-only scratch mod에 임시 정션을 만들어 isolated profile에서 활성화했다. 기존 mod/config/Production을 교체하지 않았으며 종료 후 정확한 정션만 제거했다.
- native 창을 클릭하거나 screenshot을 읽지 않았다. owned PID의 top-level visible window handle만 terminal API로 열거해0개임을 기록했다. graphics device 존재는 player.log의 D3D11로 검증했다.
- actual existing copied baseline save:13,477,182bytes; initial game tick1823; map250x250, settlement tile50878/layer0; primary fixture1map.
- QA의 첫2map fixture에 Lord/Table ID 충돌이 발생했다. 이를 **INVALID FIXTURE ATTEMPT**로 보존하고 결론 근거에서 제외했다. v2는 Thing/raw Thing_ references·Lord IDs를 remap하고 existing second Settlement parent와 연결했다. v2에서 save/load/tick/export 로그에 해당 collision/exception은 없었다. 이것은 isolated scratch cloned test map이지 canonical user2settlement save의 complete graph 검증은 아니다.

이 QA에서 실제 실행한 entry points:

```powershell
python QA-Tactical-Engine/20261002/independent_run.py
dotnet run --project QA-Tactical-Engine/20261002/EngineIL/EngineIL.csproj
python QA-Tactical-Engine/20261002/multi_map_run.py
python QA-Tactical-Engine/20261002/build_dependency_fixture.py
python QA-Tactical-Engine/20261002/dependency_run.py
python QA-Tactical-Engine/20261002/capacity_run.py
python QA-Tactical-Engine/20261002/audit_semantics.py
python QA-Tactical-Engine/20261002/verify_review_evidence.py
```

재실행은 scripts/fixture를 fresh QA directory에 복사하고 required-def 정션을 그 새 fixture로 연결한 환경에서 수행한다. harness는 기존 profile을 덮어쓰지 않으며 `Refusing overwrite`로 중단한다. 위 명령을 현존 evidence directory에서 그대로 재실행하여 evidence를 지우면 안 된다.

## 3. Claims Confirmed

| Claim | Independent result | Exact scope |
|---|---|---|
| actual runtime supervised launch | PID24756, RimWorld1.6.4871 rev591 / Unity2022.3.35f1, visible window0 | 현재 Windows/GPU/Steam 환경, batchnoninteractive |
| existing .rws load | Playing, Maps1, TicksGame1823, PausedTrue | copied original fixture |
| engine ticking | RUN_TICKS1000,1823→2823,574.4ms/1740.8TPS | synchronous unpaced loop |
| basic vanilla AI/needs | colonist movement/jobs/food transitions; actual .rws states | wander/job progression, defense/combat AI 아님 |
| native export | IndependentExport.rws,13,151,598bytes, elapsed759ms | GameDataSaveLoader.SaveGame, XML parse/readback |
| fresh process reload | new PID27988/profile Independent2, same tick2823 | original process 종료 후 별도 process |
| selected semantic state | Pawn3 IDs/pos/jobs/healthTracker/equipment/apparel/inventory/ownership/playerSettings XML reviewed fields 유지; animal47 dump rows 동일; manufactured4 item fields 동일 | 없던 equipment/assignment 정상 복원까지 아님 |
| original copied source protected | pre/post SHA256 identical | protected source/file scope, section11 |
| multiple worker base feasibility | PID28252/27824, maps loaded, simultaneous10,000ticks each, separate exports | upgraded independent evidence; no complex/capacity target claim |

최초 startup10,910.9ms, load5,663.9ms, fresh process startup6,040.1ms/load5,093.8ms를 기록했다. single run timings이며 cold/warm/cache/동시 host 작업이 섞인 값이다. Gemini의 과거 exact4,556/6,381ms 자체를 다시 입증한 것이 아니다.

## 4. Claims Downgraded

| Gemini expression | QA correction | Evidence |
|---|---|---|
| Headless / 완전 백그라운드 | **D3D11-dependent noninteractive/windowless batch process**. true graphics-headless 아님 | E-02/03의 D3D11; original Test1 NullGfx errors |
| GUI 렌더링 비용0% | visible top-level window0은 확인. GPU/render threads/cost0%는 입증되지 않음 | GPUdevice allocation, per-render workload 미계측 |
| entity integrity100% | reviewed Pawn/animal/manufactured fields로 한정; loose items60/1210 sample, complete graph NOT TESTED | Bridge387/405; Supervisor333 |
| ownership 보존100% | Pawn faction/emptyownership subtree 등 좁은 필드 유지. Bed/Grave/Area/Master/container/conquest 보존 미검증 | empty assignments/zero player buildings |
| natural chunks1206 전수 일치 | 전수 bridge dump 없음. coordinates/quantity 전체 감사 증거 부족 | item Take60; audit output checks only ID/Stack |
| full semantic state identical | human needs의 recentMemory.lastLightTick이 reload에서 변경됨. exact identity claim 불가 | E-04, section6 |
| 확장성 기반 / 컨테이너 deployment 입증 | 2 processes 가능; container/GPU-free service/remote latency/capacity는 미검증 | original probe는 bootstrap만; QA loaded burst는 확대 범위 |
| multi-worker independent bridge ports 입증 | **원 probe로는 불충분**. script에 bridgeport 인자/HELLO/profile mod config 없음; original Inst logs도 WorkerBridge 없음 | E-12; 이번 E-10으로2loaded/2ports 범위 추가 확인 |
| 30~45x 실제 Tactical 성능 | unpaced DoSingleTick microbenchmark.1x cadence/command latency/capacity와 동일하지 않음 | long batch STATUS15.6s 지연 |
| F01~F05 architecture failure 모두 PASS | F03 INVALID TEST; 나머지도 failure-specific narrow facts와 recovery 검증을 구분 | section9 |
| AI simulation 성공 | wander/pathing/needs는 CONFIRMED; actual offline AI combat defense, lord tactics, casualty permanence는 NOT TESTED | no battle workload |

Gemini가 확인한 실제 runtime/save feasibility는 인정한다. 그러나 모드/DB/worker authority 설계가 완성되었다거나 Engine PoC의 모든 architecture invariant가 통과했다고 확장하지 않는다.

## 5. Multi-Map / World Tick Findings

**Overall: FAIL. Selective adapter feasibility: PARTIAL(정적 후보만 확인), runtime adapter validation NOT TESTED.**

### QA-ENGINE-001

- **Severity:** Critical — proposed authoritative worker가 권한 대상 밖 settlement state를 변경할 위험.
- **Requirement:** SRS-FR-003, SRS-FR-098/153, SRS-CON-010, SRS-NFR-007; ADR-002 INV-TAC-001/007/013.
- **Location:** [WorkerBridge.RunTicks:326](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/GeminiSourceReviewed/WorkerBridge.cs:326>), DoSingleTick call343; actual TickManager.DoSingleTick IL.
- **Reproduction:** native-load 가능한2map fixturev2를 load → EXPORT_SAVE Before → RUN_TICKS1000 → EXPORT_SAVE After → both maps XML Pawn fields 비교.
- **Expected:** Target map0만 진행. 비Target map1은 jobs/needs/map evolution freeze. worker가 authoritative server World domain을 separately simulation하지 않음.
- **Actual:** map1의3colonists 모두 needs/jobs/position 변경. worker-local worldPawns/worldObjects/components 변경. 전체 TickManager ticks1823→2823.
- **Root Cause:** bridge가 unfiltered whole-game DoSingleTick을 사용. global TickList는 Map별 필터가 없고 MapPreTick/MapPostTick이 Find.Maps 전체를 대상으로 한다.
- **Required Fix:** 별도 ENGINE-02에서 target scope/global manager/world projection/local-clock을 포함한 selective adapter 또는 실제 target-only context packaging을 증명. production을 이 QA가 대신 수정하지 않음.

비Target map1 관찰값:

| Pawn | Position before → after | Food before → after | Jobs/needs |
|---|---|---|---|
| Human100302 | (139,142)→(128,152) | 0.747999907→0.71999985 | changed |
| Human100305 | (144,142)→(153,144) | 0.751999915→0.723999858 | changed |
| Human100308 | (133,152)→(143,142) | 0.751999915→0.727999866 | changed |

[semantic-audit](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/semantic-audit.json>)는 target0의3colonists도 진행한 것을 함께 기록한다. fire/production의 freeze는 별도 fixtures가 없으므로 NOT TESTED; 이들까지 성공/실패 수치를 만들지 않는다.

**actual IL 순서:** Find.Maps→each MapPreTick(IL0011) → global normal/rare/long TickList(0067/0072/007D) → other global managers → World.WorldTick(00B9) → World.WorldPostTick(014F) → each MapPostTick(016D) → History/GameComponent/Autosaver/Transport 등. Gemini의 “WorldTick 뒤 모든 map” 설명과 달리 실제1.6 order에는 map pre/global thing ticks가 먼저다. 문제의 본질은 순서보다 **scope가 whole game**인 점이다.

World.WorldTick은 WorldPawns/FactionManager/WorldObjects/PathGrid/WorldComponent 등을 호출한다. native pre/post world subtrees와 settlement tickDelta도 변경됐다. 다만 bridge GET_WORLD_INFO의 `WorldTicks`는 실제로 `TickManager.TicksGame`를 출력한다. 이 숫자를 dedicated server180TPS World Time 측정값으로 보지 않는다. 이번 worker는 서버에 연결하지 않았으므로 **중앙 서버 World Time 손상 자체를 관찰했다는 주장은 하지 않는다**.

### Minimum safe hook assessment

설치 DLL에서 다음 intervention points는 확인했다.

1. Map.MapPreTick / Map.MapPostTick에 active target scope gating.
2. global TickList의 Thing.DoTick dispatch와 rare/long paths에 MapHeld/owner-context gating. carried/contained/unspawned/world Pawn은 단순 Spawned+Map 체크만으로 누락 가능.
3. World.WorldTick / WorldPostTick과 world/game/story/scenario/autosave/global components의 별도 policy.
4. 공용 TicksGame 증가로 nonTarget absolute timers/ages/jobs가 나중에 resume할 때 catch-up하지 않도록 per-map clock/rebase 계약.

이는 **hook 후보이며 최소 safe adapter를 입증한 결과는 아니다**. WorldObjectsHolderTick만 막아도 world pawns/components는 남는다. Find.Maps에서 다른 map을 임시 제거하기만 해도 global registered TickLists/crossrefs가 남는다. arbitrary override/mod tick, global storyteller의 target routing과 background-load behavior까지 검증해야 한다.

Full Game save를 유지한 selective tick이 가능한지 현재 결과는 BLOCKED가 아니라 **PARTIAL feasibility / isolation FAIL**이다. 불가능하다고도 단정하지 않는다. ENGINE-02는 adapter와 target-only packaged Game/World context 두 대안을 평가해야 한다.

## 6. Complex Graph Findings

**Overall: NOT TESTED for requested complete ownership graph. Basic semantic preservation: PARTIAL.**

| Requested coverage | Current evidence | Verdict |
|---|---|---|
| player-owned Building | player buildings0 | NOT TESTED |
| Door | player Door fixture/assignment test 없음 | NOT TESTED |
| Bed ownership | Bed=None, ownership assignments 없음 | NOT TESTED |
| Workbench | player workbench workload 없음 | NOT TESTED |
| Stockpile/Zone | owned stockpile/zone roundtrip scenario 없음 | NOT TESTED |
| equipped weapon | Weapon=None | NOT TESTED |
| Apparel |3humans,2each; native apparel subtree reviewed | PASS within baseline apparel scope |
| Pawn inventory item | Inv=0 | NOT TESTED |
| Animal |47 rows stable ID/Def/Faction/Pos/Job 동일 | PASS in these fields, no trainer/master assignment proof |
| Container/Held item | player-held container graph coverage 없음 | NOT TESTED |
| Corpse | corpse ownership/nested Pawn scenario 없음 | NOT TESTED |
| installed body part/health condition | healthTracker basic subtree 유지; BionicHeart는 loose item | NOT TESTED for installed part/disease |
| ownership/assignment references | nonempty Bed/Grave/Area/Master tests 없음 | NOT TESTED |

원 save의 XML에는 nonplayer structures/mechanoid 등 summary가 다루지 않는 상태도 있다. 이를 발견했다는 사실이 full graph를 검증했다는 뜻은 아니다. 복잡한1.6compatible save 및 nonempty assignment fixture는 ENGINE-02에 필요하다.

**Native XML vs snapshot 차이:** Pawn3의 reviewed fields는 needs를 제외하고 동일했다. needs의 recentMemory.lastLightTick은 example Human302에서2721→2823으로 변했다. TicksGame 자체는2823으로 유지됐다. Food/Rest rounded snapshot이 같다고 entire needs state까지 identical인 것은 아니다. load-init reconciliation으로 보이지만 정상적 semantic normalization인지 engine evidence/whitelist로 분류해야 한다. 현재 이를 확정적인 health corruption으로 판정하지 않는다.

원 source auditor는 Pawn match에서 position/weapon만 gate한다(Supervisor307/312). health, Food/Rest, Job, apparel, inventory, faction, Bed/Area/Master를 최종 assertion하지 않는다. animals/items 비교도 최종 PASS 조건에 들어가지 않는다(Supervisor333~336). baseline buildings0의0/0은 coverage가 아니다.

Natural chunks는 reload 때 generated ThingID가 달라질 수 있지만, 이를 이유로 모든 inventory/stack identity를 위치로 대체해서는 안 된다. ADR-002 stable entity registry와 transferable asset lineage는 별도 계약이다. 이번 audit는 manufactured4의ID/Def/Pos/Stack/health를 native XML에서 확인했으나 compressed natural1206 전체 position/quantity/entity semantics는 전수 검증하지 않았다.

## 7. Manifest / Missing Dependency Findings

**Overall: FAIL — required dependency removal caused data loss without bridge-level reject.**

### QA-ENGINE-002

- **Severity:** Critical — required asset Def 누락 상태가 normal load/export로 publish될 위험.
- **Requirement:** SRS-FR-098/155, SRS-NFR-004/006/007, SRS-CON-010; ADR-002 ENGINE manifest/semantic graph criteria.
- **Location:** Bridge.LoadSave281~292, GetStatus260~278, ExportSave422~454; [actual absent log43](<C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/20261002/DependencyAbsent/player.log:43>).
- **Reproduction:** scratch XML mod의 QA_TestRequiredHeart Def를 활성화 → 해당 Thing이 든 fixture load/native save → fresh profile에서 그 mod 제외 → same native save load → re-export.
- **Expected:** missing required dependency/Def를 detect하고 LOAD_FAILED/manifest mismatch로 safe reject; Playing/normal SAVED 및 canonical publish 금지.
- **Actual:** native RequiresCustomDef save의 modIds에 qacodex.requireddef.fixture, custom item1 확인. absent profile에서 Playing, Maps1, tick1823. log에 unresolved ThingDef/NRE/spawn failure. bridge는 SAVED를 반환하고 native re-export의 custom item0.
- **Root Cause:** mod/Def manifest prevalidation 없음. engine partial load/errors가 game/maps existence와 ProgramState Playing만으로 성공 처리됨. file exists/hash는 semantic integrity proof가 아님.
- **Required Fix:** required manifest/schema/build/Def registry validation 및 correlated load operation failure state; critical loader errors/partial graph를 safe reject. EXPORT/canonical publish는 validated Ready generation만 허용. actual native negative fixture를 regression으로 유지.

실제 warning/error가 있으므로 완전히 로그 없는 “silent” corruption이라고 쓰지 않는다. **bridge/supervisor contract에서 성공으로 통과하는 partial-load data loss**가 정확한 표현이다.

테스트 모드는 workspace scratch XML-only, 원 BionicHeart definition을 새 defName으로 복사한 별도 dependency다. original custom save를 실제 엔진으로 재저장해 required dependency를 native artifact에 넣었다. save text에 unknown name만 적은 invalid XML test와 다르다. missing provider는 active profile에서만 제외했고 original source/생산 mod를 삭제하지 않았다.

ENGINE-F03의 존재하지 않는 config package ID test는 이 요구를 검증하지 않는다. 이번 actual negative로 manifest validation은 단순 OPEN을 넘어 **현재 bridge의 safe rejection failure가 재현**됐다.

## 8. Multi-Worker Findings

**Gemini claim scope:** two game processes bootstrap **CONFIRMED**; 두 독립 bridge/map workloads라는 과거 주장 **INSUFFICIENT**.

Original test_multi_instance.ps1은 fresh dirs에서 exe2개를 시작하고8초 후 HasExited/WorkingSet만 확인한다. ModsConfig 준비, bridgeport 설정, HELLO, LOAD_SAVE, ticks/export가 없다. actual Inst1/Inst2 logs에도 WorkerBridge startup이 없다. 따라서 원 probe의 “29100/29101 독립 명령 처리”는 source/log와 맞지 않는다.

**Independent expanded probe:** simple-save loaded dual-worker flow **PASS within tested scope**.

| Metric | Worker1 | Worker2 |
|---|---|---|
| PID |28252|27824|
| bridge port |29226|29227|
| initial maps/ticks |1/1823|1/1823|
| simultaneous burst |10,000ticks|10,000ticks|
| engine loop duration |4,055.7ms|4,050.7ms|
| final ticks |11823|11823|
| engine loop TPS |2465.7|2468.7|
| sampled peak RSS |954.125MiB|929.539MiB|
| measured process CPU time |9.90625s|9.1875s|
| native export |success, Concurrent1 profile|success, Concurrent2 profile|

측정 wall4.1059s에 CPU는 process multi-thread 합계다. single-core100% scale로 각각 약241.3%/223.8%이며 host16logical CPUs 전체 대비는 약15.1%/14.0%. “단일 main thread만100%”라고 환산하지 않는다.

ConcurrentExport는 같은 filename이지만 서로 다른 Saves directories에 저장됐다. game bridge ports도 별도였다. 두 exports는 concurrent burst 후 **순차적으로** 수행했으며 concurrent serialization/GPU pressure maximum을 검증한 것은 아니다.

nvidia-smi aggregate sample: RTX2070SUPER, GPU9%, host-used2421MiB/total8192MiB. 이는 host 전체 한 시점 값이다. per-worker VRAM150MB나 peak GPU capacity는 **NOT MEASURED**. complex maps, normal realtime scheduling, latency,1host 최대worker수, container deployment은 NOT TESTED. capacity 미확정은 단일 worker의 basic ENGINE path PASS와 분리한다.

## 9. Failure Test Review

| Test | QA classification | Confirmed narrow fact | Not established |
|---|---|---|---|
| F01 nonexistent save | **PARTIAL** | independent rerun: FileNotFoundException log, NoGame/Maps0, no dummy Playing | typed correlated failure/result, retained coherent checkpoint, retry/recovery |
| F02 truncated XML | **PARTIAL** | independent rerun: XmlException, NoGame/Maps0; previously loaded worker도 false Playing 없음 | broader semantic corruption, durable repair, recovery to prior good state |
| F03 fake missing package config | **INVALID TEST** for required save dependency | booting with unrelated missing ID는 별도 robustness probe | actual required mod/Def reject; section7의 independent negative는 FAIL |
| F04 force kill | **CONFIRMED**, process detection scope | independent loaded worker PID27824 kill→HasExited/exit1 | checkpoint restore, generation fencing, journal/ownership recovery |
| F05 socket reconnect | **CONFIRMED**, transport scope | existing loaded worker survives close; fresh HELLO works | tactical participant auth/epoch/control fencing, late command/result isolation |

F01/F02의 failed-load state는 MainThread ProcessCommand response와 separate async loader lifecycle가 연결되어 있지 않다. 실제 load request는 QUEUED였고 error reason은 player.log에만 남았다. NoGame이면 “아직 loading/failed/원래 idle”를 명시된 operation result로 구분하지 못한다. 기존 F02 assertion `!Playing || Maps0`는 indefinitely Loading도 PASS시킬 수 있다. 우리 rerun에서는 실제 NoGame까지 확인해 corrupt XML rejection의 좁은 사실은 강화했다.

F04는 loaded-map actual kill로 원 idle-only probe보다 넓게 확인했다. crash consistency는 POC-TAC-CRASH이며 ENGINE-F04를 그 gate의 PASS로 재사용하지 않는다.

## 10. WorkerBridge Code Review

**Main engine API thread routing:** 기본 successful path는 **CONFIRMED**. listener/ThreadPool이 text를 받고 ConcurrentQueue에 enqueue한다(160~191). Unity Update97/129에서 engine calls를 실행한다. LoadGame/DoSingleTick/SaveGame/Quit을 listener가 직접 실행하는 경로는 source에서 발견하지 않았다.

background exception handler의 Verse.Log.Warning214는 별도 log call이며, 이를 근거 없이 map thread corruption으로 판정하지 않는다. 해당 logging path의 thread contract는 별도 확인 여지가 있다.

### QA-ENGINE-003 — long batch monopolizes main thread

- **Severity:** High, NFR-011/lease-health recovery integration risk.
- **Requirement:** SRS-NFR-011/008; ADR-002 command servicing/lease-watchdog model.
- **Location:** Update129의 queue drain, RunTicks326~351.
- **Reproduction:** connectionA RUN_TICKS50000;150ms 뒤 connectionB STATUS.
- **Expected:** simulation을 budgeted slices로 실행하고 control/status/heartbeat가 bounded servicing을 받음. future gameplay 구현에서 same-thread long loop 금지.
- **Actual:**50,000ticks15,699.4ms. second STATUS roundtrip15,551.1ms. Update coroutine/yield/service 중간 지점 없음.
- **Root Cause:** single Update에서 unbounded count synchronous for loop 및 queue exhaustion.
- **Required Fix:** scratch ENGINE-02의 real-time/sliced loop로1x cadence와 status/heartbeat responsiveness를 계측. microbenchmark command는 separate offline diagnostic으로 명시.

### Additional lifecycle findings

| Finding | Location | Risk / QA action |
|---|---|---|
| no command count/request size bounds | ReadLine172 / RunTicks tickCount parsing | oversized line memory, huge valid int main-thread stall; production auth 요구가 아니라 PoC observability/liveness 문제 |
| unbounded queue / drain-all Update |191 /129| many connections can starve frame/service; PoC future controlled harness에도 bounded budget 필요 |
| timeout doesn't cancel request |TCS.Wait30000 at194| timeout response after request remains queued; late LOAD/EXPORT/SHUTDOWN may execute. static risk, actual timeout-followup injection NOT TESTED |
| disconnect doesn't withdraw queued request |HandleClient160~218| reconnect success가 old command fencing proof 아님; engine session lease adapter에 lifecycle cancellation 필요 |
| load during load / export during load not gated |LoadSave281 / ExportSave422| LongEvent/status-aware readiness/generation 없음; partial/old Current.Game export risk. dynamic concurrent load race NOT TESTED |
| first pause enforced after Playing once |Update117~126, load resets flag288| load/FinalizeInit effects or tick window0을 완전히 보장하지 않음; first-ready barrier와 semantic state audit 필요 |
| export validates only File.Exists/hash |441~454| prior same filename leftover/semantic partial export를 구분하지 못할 위험; new artifact identity/validation contract 필요 |
| shutdown doesn't cancel accepted clients/TCS |248~254, OnDestroy457| accepting listener stop 외 client tasks blockedReadLine/TCS resources explicit cleanup 없음; leak count stress NOT TESTED |
| Thread.Abort fallback swallowed |OnDestroy461| deterministic lifetime join/stop proof 아님; observed normal exit0과 contract 분리 |
| game TickManager internal exceptions logged |E-05 DoSingleTick catch+Log.Error| RUN_TICKS OK와 tick counter가 전체 subsystem success를 증명하지 않음; log/error counter와 semantic checks 병행 |

PoC에 production authentication/security 전체를 요구하는 결함 목록이 아니다. successful engine demonstration의 재현성·scope·liveness를 평가했다. malformed tick count/unknown command는 independent run에서 ERROR를 반환했고 process가 유지됐다. oversized/flood/repeated-LOAD interleavings는 아직 **NOT TESTED**이며 발견한 static risks를 dynamic FAIL로 과장하지 않는다.

**Supervisor test-review issues:** final preservation assertion incomplete(section6); ReadLine loop에 timeout 없음33~35; exceptional path catches/prints only478~480, Main void는 nonzero failure exit를 보장하지 않음; failure path owned process cleanup finally가 없음. explicit acceptance failure를 process exit0만 보고 성공으로 처리하면 안 된다. 이 QA harness는 unique owned processes를 finally에서 종료하고 결과/errors를 separate JSON에 남겼다.

## 11. Resource/Performance Interpretation

- 1,740.8TPS는 paused game에서 engine ticks를 unpaced synchronous 반복한 **microbenchmark**다.
- dual worker2465~2469TPS도 short burst. map population complexity, rendering/network/GC/serialization 및 background jobs 영향을 분리한 representative throughput이 아니다.
- normal1x real-time worker가 required cadence를 유지하는지는 **NOT TESTED**. bridge에는 continuous speed/tick scheduling control이 없고 default paused/manual RUN_TICKS 방식이었다.
- long RUN_TICKS에서 same-main-thread bridge command servicing이15.6초 지연됐다.30초를 넘는 burst면 current HandleClient wait timeout과 late execution 위험이 있지만 그 dynamic boundary는 NOT TESTED.
- GPU/D3D11 요구는 current local device에서 확인했다. graphics/render cost0%, VRAM150MB/worker, virtualGPU equivalence, Steam 없는 host, Linux/service 계정/container 환경은 입증하지 않았다.
- latency numeric target은 SRS-NFR-011에 따라 later architecture PoC/측정 뒤 Master가 정한다. 이번 loop TPS로 이를 결정하지 않는다.

**Original save protection: CONFIRMED.**

pre/post protected source13,477,182bytes, SHA256:

`C963F1B26747E00E261EE0AC341E3E761F00F0957103999B42E4DB1491E742F4`

source는 Gemini OriginalSave directory에서 read/copy만 했다. engine inputs와 exports는 workspace profiles의 Saves directories에 저장했고 original filename/path를 export target으로 쓰지 않았다. 별도 before/after manifest에서 source save, actual exe, Assembly-CSharp.dll, original Bridge DLL 모두 hash unchanged. production/requirement input55건 변경0. 테스트 중 player.log/profile output 경로는 launch records와 save-folder override logs로 대조했다.

기본 사용자 AppData 전체 또는 모든 Steam cache를 hash audit한 것은 아니다. 따라서 “사용자 프로필의 모든 파일을 일체 건드리지 않음”까지 일반화하지 않는다.

모든 이번 QA-owned RimWorld processes가 종료됐다. 종료 시 RimWorld process 잔존0, scratch required-def junction 제거 확인. fixture/evidence는 workspace에 보존했다. 기존 Gemini bridge junction/Production Mods는 교체·삭제하지 않았다.

## 12. Remaining Critical Risks

| Risk | State | Requirement / consequence |
|---|---|---|
| nonTarget map simulation | **REPRODUCED FAIL** | SRS-FR-003, settlement authority scope 밖 irreversible changes 가능 |
| unintended worker World progression | **REPRODUCED FAIL** | server Domain Authority와 local engine world mutation conflict; SRS-NFR-007 |
| required mod/Def partial load | **REPRODUCED FAIL** | SRS-FR-098/155, SRS-NFR-004/006; missing assets를 success publish 위험 |
| complete entity/assignment ownership graph | **OPEN / NOT TESTED** | QA-004, SRS-FR-166/NFR-002 |
| engine artifacts + domain durable atomic commit | **OPEN** | QA-003, SRS-NFR-005/006/007; filesystem native save 성공만으로 해결 아님 |
| partial rollback / repair lifecycle | **OPEN** | QA-012; default NoGame/Playing flag로 durable repair를 대체 못함 |
| local tick clock / nonTarget deferred timer effects | **OPEN** | frozen state가 resume할 때 elapsed global TicksGame로 catch-up하지 않는지 |
| canonical stable entity/stack/location registry | **OPEN** | regenerated natural IDs와 complete movable asset identities 구분 |
| old lease/session result and crash replay | **OPEN** | standalone socket reconnect/HasExited proof만으로 fencing/recovery 성립 안 함 |
| ordinary owner-local imported save legitimacy | **OPEN** | trusted tactical worker가 pre-battle user-forged items를 정당화하지 못함 |

이번 current scratch worker는 Dedicated Server domain에 결과를 commit하지 않았다. 따라서 actual production ownership corruption/Item Duplication 발생을 관찰했다고 보고하지 않는다. **그 위험을 막는 architecture contracts가 아직 충족되지 않은 것**과 scratch data loss/isolation failures를 분리한다.

## 13. Required Follow-up PoCs

**우선: POC-TAC-ENGINE-02 — Target-Scope Simulation, Required Manifest Reject & Complex Save Integrity.**

| Subtask | Setup | Pass criteria | Failure criteria / artifacts |
|---|---|---|---|
| ENGINE02-ISOLATION | actual2+maps, target/nonTarget Pawn/jobs/needs, active fire/production, full World context | target actual AI/ticks 진행; nonTarget semantic state/timers 유지; World authority/projection boundary; save+fresh reload+resume 검사 | nonTarget changes/global side effects/deferred timer catch-up면 FAIL; hook coverage/actual IL/semantic graph |
| ENGINE02-SELECTIVE | scoped MapPre/Post, normal/rare/long Things 및 global managers; target-only context 대안도 비교 | held/unspawned/world refs를 포함해 verified target scope, no stale registered Thing leak | global list filtering만 주장하거나 mod/clock effects 미검증이면 PARTIAL; safe-hook proof/document |
| ENGINE02-COMPLEX | nonempty owned Building/Door/Bed/Workbench/Zone, weapon/apparel/inventory/animal/container/corpse/condition/assignment fixture | engine load→tick→save→fresh reload에서 stable graph/ownership/crossrefs/location·quantities 동일 또는 명시된 valid transformations |0/0, sample-only, empty assignment, silently substituted object는 FAIL; full graph diff+oracle |
| ENGINE02-MANIFEST | actual native required mod/Def save, mod/build/schema/hash/Def removal/mismatch | pre-load deterministic reject or staged validated failure; Playing/SAVED/canonical publish 금지; retained coherent prior state | 현재1→0 같은 accepted loss FAIL; loader event/result log, artifact validation |
| ENGINE02-LIFECYCLE | load 중 RUN/EXPORT/reload, concurrent commands, socket close/timeout, shutdown | correlated LoadOperation state, Ready generation only, canceled late work0, bounded cleanup/service | no-op/readiness false success/stale export/late side effect FAIL |
| ENGINE02-CADENCE | normal1x with bounded Update slices, status/heartbeat under load, long diagnostic separated | measured tick cadence/jitter + bounded control servicing, pause/readiness barriers | burstTPS만으로 pass 금지; time traces/resource sample |
| ENGINE02-RESTART | complex checkpoint fresh process reload + entity/container/Caravan location | same stable registry, no duplicated/lost references; load-init semantic differences classified | unexplained graph loss/quarantine omission FAIL |

순서: target/world isolation와 manifest negative를 먼저 막고, complex fixture·cadence·lifecycle·restart를 동반 검증한다. 그 뒤 POC-TAC-REMOTE의 own Pawn presentation/command path를 진행한다. ENGINE02는 tactical gameplay/persistence 구현 전체 완료를 요구하는 package가 아니지만 다음 REMOTE 개발의 authority scope 전제를 고정해야 한다.

POC-TAC-CRASH는 durable checkpoint/input replay/lease fencing/domain commit을 별도로 검증한다. ENGINE native save success와 process-kill detection을 그 PoC PASS로 대체하지 않는다. Inventory/Ordinary Simulation Authority ADR의 asset provenance boundary도 그대로 남는다.

## 14. Recommendation to Master

**OPTION 2 채택을 권고한다.**

1. basic actual Windows RimWorld worker/load/tick/save/fresh reload feasibility는 인정한다. Candidate C를 지금 폐기할 근거는 없다.
2. **ADR-002 PROVISIONALLY ACCEPTED를 유지**하고 full ACCEPTED 승격을 보류한다.
3. **POC-TAC-ENGINE-02를 먼저 발주:** target/world isolation와 manifest-safe rejection은 actual reproduced failures이므로 후속 requirement/architecture gate다.
4. complex ownership graph 및 normal1x control servicing/restart semantic normalization을 ENGINE02 acceptance에 포함한다.
5. ENGINE02 결과 뒤 POC-TAC-REMOTE. 기존 QA-001~014 OPEN 유지; 새 QA-ENGINE-001/002/003도 해결 evidence 전 CLOSE 금지.

[ADR-002](<C:/Users/user/Desktop/RimMulti/ADR-002_Tactical_and_Offline_Combat_Authority.md>)는 이번 Master Work Order의 **PROVISIONALLY ACCEPTED** 상태만 동기화했다. 완전 ACCEPTED 승격이나 design contract 임의 변경을 하지 않았다. original design의 “PoC 미실행” 표기는 작성 당시 historical baseline이며 현재 실제 검증은 본 보고서가 별도 기록한다.

Master가 PoC scope/feasibility evidence를 검토해 다음 work order를 정한다. Production 구현/커밋은 수행하지 않았으며, 본 제출 후 다음 지시를 기다린다.

