# QA Engine Host Settlement Round-Trip Independent Review

```yaml
Work Package: WP-QA-ENGINE-HOST-SETTLEMENT-ROUNDTRIP-01
Reviewer: Independent QA / Architecture Reviewer
Date: 2026-10-03
Target: POC_EngineHost_Settlement_RoundTrip_01.md candidate/evidence lineage
Verdict: FAIL
QA-ENGINE-002 Recommendation: OPEN / STILL FAILING
QA-ENGINE-006 Recommendation: OPEN / STILL FAILING
B2-lite Core Gate Recommendation: Do not approve this exact candidate/profile
Master State: Not modified
```

## 1. 判定 근거

**현재 후보는 E2 round-trip core PASS 요건을 만족하지 않는다.** 서로 다른 엔진 프로세스 A→B→C에서 대상 맵을 저장·로드·100틱 실행·재저장하는 경로는 실제 동작했다. 그러나 의미 검증과 export 승인 경계가 실패했다.

- 의미 변조 10건 모두 `READY`에 도달하고 `SAVED` 산출물을 만들었다. 9건은 독립 live oracle에서 실제 상태 불일치가 확인됐다. 나머지 동물 follow 변조는 엔진 로드 후 차이가 남지 않아 검출 성공으로 계산하지 않는다.
- 실제 불일치 9건 중 후보 C# 비교기는 3건, Python 비교기는 2건만 검출했다. **C# 비교기가 FAIL을 반환한 경우에도 후보는 export를 허용했다.**
- 변조하지 않은 원본 fixture에서도 누락 DesignationDef, 중복 load-ID 등록 오류와 작업표 저장 `NullReferenceException`이 발생했다. `READY / LastFailure=''`와 `SAVED`는 의미 무결성 증거가 아니다. A의 원래 로그에도 같은 종류의 문제가 있다.
- A 보고서의 두 export SHA와 현재 제출 디렉터리의 실제 SHA가 불일치한다. “보고된 정확한 산출물” 전체를 일치 검증했다고 인증할 수 없다. 아래 실행 결과는 QA 시작 시 동결한 실제 source/DLL/fixture 바이트에 대한 결과다.

이는 해당 후보의 실패이며, B2-lite 설계 전체가 불가능하다는 판정은 아니다. G-Q1, PlayerGlobal 최종 스키마, 모든 모드 호환성 또는 Production material/Tactical 구현 승인을 의미하지 않는다.

## 2. Provenance 및 실행 경계

증거 루트: [HOST-ROUNDTRIP01-20261003](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003).

원시 증거는 [results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Evidence/results.json), 프로세스별 `Profiles/*/player.log`, `Evidence/*.snapshot.json`, `*.census.json`, `.rws` 및 manifest에 보존했다. GUI 검증이 아닌 engine-host 시험이다.

### 2.1 실제 profile / DLL

- RimWorld **1.6.4871 rev591 Win64**. `-batchmode`, 별도 savedatafolder, 별도 loopback 제어 포트. `-nographics`는 사용하지 않았다. 후보는 재빌드하지 않았다.
- Harmony, Core, Royalty, Ideology, Biotech, Anomaly, Odyssey, `wareconomy.hybridmultiplayer`, `wareconomy.workerbridge.poc`, **`qacodex.engine02.probe`**. 마지막 ProbeMod는 A의 실제 ModsConfig에도 존재하지만 보고서 profile 목록에는 누락됐다. 따라서 문서에 적힌 순수 profile과 실제 측정 profile을 동일시하지 않는다.
- Worker DLL 실제 로드 경로: `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll`. 이 경로는 A scratch의 후보로 연결된다. 실제 loaded assembly path/hash/MVID를 live observer로 확인했다.
- A 보고서는 DLL SHA/MVID 전체 manifest를 제공하지 않았다. 아래 값은 독립적으로 관측·동결한 값이며, 알려지지 않은 개발자 기대값을 대신 만들어 낸 것이 아니다.

| 객체 | SHA-256 / MVID |
|---|---|
| Source fixture, 30,370,467 bytes | `E04E535638FB344D4C831B6D981DAC82C385FE26388DF7AA5F9E8861BF397AED` — A 보고서와 일치 |
| WorkerBridge.PoC.dll, 86,016 bytes | `272C8C620999B38A287AEEEAEACDEE2602FF1A35E7E39B6E1CC697B83948815D` |
| Worker DLL MVID | `698aca67-cdbc-4649-a965-217aa4737ca2` |
| 실제 WorkerBridge.cs | `774FEA412E05EA5C75C4DE7EDA6912C6EBEF099DA1ADD920C3D8B0EF233D6C24` |
| 실제 EngineHostCensus.cs | `8D94CC1D8E09C69DBB5B12DA3F67C30C1E44345E1877EEC436EC4D4C0CA6C45A` |
| Assembly-CSharp.dll | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` |
| Engine MVID | `61e41735-6189-4da4-9d21-0260257b5097` |
| 실제 로드 WarEconomy.Client.dll | `645B78FFC7F44814193040BBCAE06A9F9FDD9AD61368CBDEB80165A1BF5D0E14` |
| 실제 로드 WarEconomy.Common.dll | `BE104A1A807E026438D1134F86A67AEF3804EC0C28AAD03FB3A8F9C4E04770DA` |

작업 폴더의 `scratch/WorkerBridgeMod/Source/EngineHostCensus.cs`는 실제 설치 후보의 source와 달랐다. 실제 후보 source를 QA `Frozen`에 복사하여 검토했고 차이를 `Evidence/census-source-lineage.diff.txt`에 기록했다. Production/후보 수정 또는 차이의 암묵적 보정은 하지 않았다.

### 2.2 A 보고서 산출물 불일치

| A 산출물 | 보고된 SHA | QA 시작 당시 실제 SHA |
|---|---|---|
| RT_Candidate_Artifact.rws, 13,972,111 bytes | `01349BD6F21C64EB7D03B1FE104B8008064F9FE9CBE6AF7641B26FE4A936E7FE` | `2F459166F45258D3461E0EDD7559F4BC536622056063D5CEE8CE7FC3D637C647` |
| RT_PostTick_Artifact.rws, 13,993,609 bytes | `3DF67CA7F4312F6C66567AE294A5080BE65FECE102E27CD58249BE1C7ECBEEC3` | `94C2E3DAF0A9C92F203321B9FD0B477A2858D330C33BB8718618F11A8D1E1F40` |

파일 크기는 같지만 SHA가 다르다. 원인은 확인되지 않았다. A의 두 파일을 QA가 덮어쓰지 않았다. 정확한 보고 산출물 lineage 인증에는 개발자의 manifest 정정/설명이 필요하다.

### 2.3 불변성 및 QA observer

[candidate-before.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/candidate-before.json)과 `candidate-after.json`에서 동결 대상 변경 **0건**이다. source, 후보 DLL, engine, A 산출물/스크립트를 포함한다.

`WarEconomyMod` 전체는 337→358 files, before/after 차이 **26경로**였다. 모두 `Source/Testing/WarEconomy.Pipeline.TestHarness` 아래 다른 시험 source, DLL/PDB 또는 신규 TestRuns_REV2 DB/WAL/SHM다. **QA가 수정한 파일은 아니며 변경 주체는 이 시험에서 확인하지 않았다.** `Source/Testing` 밖 Production 구현·배포 파일은 변경 0건이다. 그러므로 전체 `WarEconomyMod/` 불변이라고 보고하지 않는다. 정확한 목록은 [final-integrity-and-clock.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Evidence/final-integrity-and-clock.json)과 `production-before/after.json`에 있다.

QA-only observer는 기존 QA ProbeMod에 임시 추가했다. 새 Game/MapComponent를 등록하지 않고 native 상태를 읽는다. `JOB` 명령만 명시적으로 QA fixture에 native Goto/예약을 생성한다. `COMPARE/COMPAREPAIR`는 후보의 실제 C# 비교기를 호출하며 후보 구현을 바꾸지 않는다. QA DLL v1 SHA `2DFDAE8A990FD41E81EFF1FC51C1F00F968D40509158D2D60DC7AB2987C43E2B`, v2 SHA `369616996C142A5F8C5BE22C45A6F1FC3AADCD17995246D1E4CFA39A31143FBE`. C# pair 비교 추가 후 v2를 사용했고 설치 시점/hash는 각 launch 기록에 있다. 최종 설치된 임시 DLL은 제거했다. 모든 20개 QA engine process는 종료됐고 마지막 확인에서 RimWorld 프로세스가 남지 않았다.

관련 개발자/QA script와 source/DLL hash는 [qa-harness-manifest.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/qa-harness-manifest.json) 및 candidate manifest에 있다. 실제 A/QA ModsConfig 및 QA Prefs hash는 [profile-manifest.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/profile-manifest.json)에 있다. QA observer/IL 도구만 빌드했으며 Production 빌드 또는 후보 재빌드 결과를 주장하지 않는다.

## 3. Fresh-process A→B→C

A의 스크립트는 `procRT / bridgeRT` 하나를 실행한 뒤 그 안에서 Source→Candidate→PostTick을 여러 `LOAD_SAVE` generation으로 로드한다. [동결 스크립트:256](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Frozen/run_settlement_roundtrip_poc.py:256). 이는 fresh-process 증거가 아니다.

독립 시험은 아래 순서로 앞 프로세스의 종료를 확인하고 다음 프로세스를 실행했다.

| 단계 | PID | 실제 결과 |
|---|---:|---|
| A_Source | 25592 | source 2 maps/94 WorldObjects, tick1823. 변조·추출 전에 live census와 독립 snapshot을 취득. native export 후 종료0 |
| B_Target | 33220 | A export를 동일 pruning 방식으로 target map/parent만 남긴 입력에서 fresh load. 1 map/1 WorldObject, tick1823. native JOB+예약, 정확히100틱 완료 대기, tick1923 export 후 종료0 |
| C_Rematerialized | 16516 | B posttick export fresh load. 1 map, tick1923, 폰 위치/작업 및 선택된 환경 상태 재확인. 종료0 |
| D_ActiveJobReload | 30488 | B의 active-job 저장본 fresh load. Goto/예약 유지. 추가40틱 완료. 종료0 |

### 독립 산출물

| 객체 | bytes | SHA-256 |
|---|---:|---|
| A native full export | 25,815,308 | `BB4E0EDB00F4AC4053F380DC1B6D53F0E9041F6063590D851D9CF92915E25993` |
| QA A_TargetArtifact.rws | 13,962,912 | `B76CB6E816D98D4C9446BC3050F10DD9107AF8E00454E7366FC6F4F0F1A0F9AE` |
| B_ActiveJob.rws | 13,984,864 | `717EA0467A033B351D7ADE6FEBA2D58390B11DBFF59CD0D82E2AFF57FD19D6E9` |
| B_PostTick.rws | 13,985,339 | `831D8B09F0D01918A78622714ADBD4CAD87B39708075FAF6976A24082EE38D7A` |

**추출의 정확한 의미:** 후보의 `EXPORT_SAVE`는 whole Game save를 출력한다. QA는 A가 사용한 알고리즘대로 다른 maps/worldObjects만 제거했다. 이를 독립 MapSegment extractor 또는 complete canonical detached schema가 이미 구현된 것으로 간주하지 않는다.

QA의 제한된 custody 분류 346개에서 ID set/Def/count/holder/기어·소지품·선택된 관계가 유지됐다. 이 숫자는 최종 canonical custody 스키마가 아니다. 비교 결과를 0으로 덮어쓰지 않았다.

- A→B raw diff **50건**: jobGiverKey49, null/missing ingredientFilter 표현1.
- B-posttick→C raw diff **33건**: jobGiverKey21, null/missing lastJobDriverMade11, tickedLastWeather1.
- 엔진 IL에서 `WeatherManager.tickedLastWeather`와 transient job-driver pointer는 해당 ExposeData에 저장되지 않아 reconstructible/cache로 분류한다.
- **jobGiverKey는 `Job.ExposeData`가 `lastJobGiverKey`로 저장한다.** 로드에서 think-node key를 찾지 못한 경고가 있고 다음 저장 시 null jobGiver가 -1로 바뀐다. 모두 단순 ephemeral이라고 제거할 근거가 없다. 현재 fixture reference 무결성은 OPEN이다.

## 4. 실제 Context B 및 의존 경계

Context B는 target Map0, `WorldObject_91`, tile`50878,0`만 남긴다. 하지만 factions16, WorldPawns20, ideologies13 및 **모든 원래 root Game/World section**을 유지한다. ResearchManager, QuestManager, storyteller/history/tales/policies, WorldGrid, 전체 Faction/Ideo registry, world features/landmarks, pocketMaps와 components가 남는다. **owner global context를 유지한 pruned save이며 최소 dependency closure 증명이 아니다.**

| 의존성 | 현재 시험의 분류 / 필요한 경계 |
|---|---|
| Target MapParent / map-parent link | mandatory canonical composed input. 대상 identity/ownership와 matching 필요 |
| 참조 Faction registry | canonical composed projection 필요. 원본 전체16개 유지가 최소 집합임을 입증하지 않음 |
| WorldGrid/target tile | read-only projected context. 관련 지형/날짜/타일 lookup에 필요; 전체 grid가 최소인지는 미결 |
| TickManager saved temporal metadata | mandatory composed clock input. runtime singleton/카운터와 canonical 시간 권한은 분리 |
| Target 관련 Research/Ideology/외부 Pawn references | canonical composed input 후보. 소유자·lease·revision/provenance는 future ADR 계약 필요 |
| Game/World/Map components의 저장 state | 관련 state는 보존 대상. component 전체를 ephemeral로 제거하지 않음; relevance closure 미결 |
| Runtime grids/lookups/job-driver/cache | reconstructible/ephemeral, native rebuild 여부 검증 필요 |
| Quest/Game-global 정책/기록 | 현재 보존하지만 비어 있거나 영향이 미시험. 무조건 제거 가능으로 판정하지 않음 |

실제 live component inventory:

- Game7: QAEngine02.GameProbe, Anomaly, Bossgroup, PawnDuplicator, PsychicRitualManager, DebugTools, OnetimeNotification.
- World6: OrbitalScannerWorldComponent, TilePollutionComp, TileTemperaturesComp, LocationGenerator, WorldGenData, GravshipController.
- Map12: QAEngine02.MapProbe, BiomeCondition, BreakdownManager, Fleshmass, MixedBiome, TileMutatorCondition, FishShadow, LavaFX, PollutionInfo, RoadInfo, Vacuum, WaterInfo.

전체 타입명/실제 상태는 snapshots와 `context-static-inventory.json`에 보존했다. 이 목록은 삭제 whitelist 또는 확정 PlayerGlobal 스키마가 아니다.

## 5. 독립 oracle, fixture 및 정상 로드 실패

Trusted live baseline은 A_Source에서 **추출/재materialization/변조 전에** 취득했다. Python XML oracle로 source와 native output을 별도로 비교했다. live baseline만 사용하면 첫 로드에서 이미 사라진 상태를 정상으로 오인하므로 source-static 교차검증을 병행했다.

독립 observer는 `Map.spawnedThings` 및 nested holders를 조사한다. 후보의 `listerThings.AllThings`는 filth를 포함하지 않는다. Def/position 기반 환경 conservation을 custody identity와 분리했다. 다만 observer도 범용 전체 graph verifier가 아니다. Power comp 일부 scalar와 native 저장 reference는 조사했지만 power-net member의 정확한 ThingComp identity 연결, 모든 bill parameter 및 예약 target struct의 완전 live oracle는 입증하지 않았다. 후보의 부분 문자열/카운트 비교를 전체 graph fidelity로 승격하지 않는다.

### 원본 fixture 자체의 문제

[source-static-crosscheck.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Evidence/source-static-crosscheck.json), [A_Source 로그:50](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Profiles/A_Source/player.log:50), [A의 원래 로그](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Evidence/A_original_player.log).

- Source Designations3(`Mine`, **`PlantsCut`**, `Haul`)→native export2. `PlantsCut` Def lookup 실패 후 null designation 제거. 실제 source→load 손실이다.
- 원본에서 weapon/apparel/medicine과 식물의 숫자 ID9001/9002/9004가 재사용된다. 이것과 별도로 실제 엔진 로그에 중복 `Hediff_0` 및 Verb load-directory 등록 오류가 있다. 숫자 재사용과 모든 load-ID 문자열 충돌을 같은 사실로 단정하지 않는다.
- 원본 bill은 유효한 ingredientFilter를 갖추지 못했다. native save에 **`Exception while saving Bill_Make_SculptureSmall_0: NullReferenceException`** 발생. output bill은 recipe와 일부 필드만 남은 부분 직렬화 상태인데 후보는 `SAVED`를 반환했다. 완전히 유효한 입력 bill의 configuration이 잃어버려졌다고 주장하는 대신, fixture의 유효성 미충족과 부분 save 승인이라는 실제 실패를 판정한다.
- A의 기존 `PoC_RoundTrip/player.log`에도 PlantsCut, Hediff_0와 bill save 예외가 있다. QA observer가 새로 만든 오류라는 설명은 맞지 않는다.

### A의 fixture 설명과 실제 데이터 차이

| 문서 주장 | 실제 관측 |
|---|---|
| Boomrat master=Strange, followDrafted=True | master=null, followDrafted=False |
| Rice growing zone / harvest designation | Zone_Stockpile ID1. source PlantsCut invalid; growing zone 없음 |
| TableSculpting9105 | TableSculpting9106 |
| Aurora9109, duration15000 | Aurora850160, duration60000 |
| Corpse in sarcophagus | AncientCryptosleepCasket의 nested corpse |

또한 기어 상세도 문서와 달라 실제 snapshot을 기준으로 했다. 이 fixture는 positive master/follow, growing-zone crop, valid bill configuration, royalty/quest closure를 입증하지 않는다.

## 6. Silent corruption battery 및 실제 export 공격

동일한 신뢰 baseline/미변조 QA target artifact에서 각각 독립 입력을 만들고 **10개의 fresh process**로 로드했다. 입력 field의 정적 변조와 엔진의 최종 live 값을 함께 기록했다. C#은 동결 DLL의 `CompareCensus`를 실제 호출했고 Python은 동결 oracle를 실행했다. 자연 compressed geology의 ID 차이가 의미 변조 검출을 가리지 않도록 **후보 비교기 challenge용 pair에서만 geology/filth ID/count 항목을 양쪽 동일하게 제외**했다. 별도 독립 환경 oracle는 아래 환경값을 검증한다. 이 분리를 전체 후보 oracle의 성공으로 계산하지 않는다.

| 변조 | 기대→실제 live | 독립 mismatch | 후보 C# | 후보 Python | 실제 export |
|---|---|---|---|---|---|
| held medicine stack | 5→4 | 검출 | FAIL | FAIL | **SAVED** |
| Shooting skill | 7→11 | 검출 | PASS | PASS | **SAVED** |
| Stab severity | 3→1 | 검출 | PASS | PASS | **SAVED** |
| hediff 제거 | 2→1 | 검출 | FAIL | PASS | **SAVED** |
| animal follow false→true XML | live false→false | 변조 잔존 안 함 | PASS | PASS | SAVED |
| bill 제거 | 1→0 | 검출 | PASS | PASS | **SAVED** |
| zone cell | (140,0,140)→(140,0,141), count 동일 | 검출 | PASS | PASS | **SAVED** |
| fireSize | 0.45→0.9 | 검출 | PASS | PASS | **SAVED** |
| bed relation 비치명적 누락 | Bed9104→empty | 검출 | FAIL | FAIL | **SAVED** |
| Aurora duration | 60000→12000 | 검출 | PASS | PASS | **SAVED** |

[silent-summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Evidence/silent-summary.json). Engine READY **10/10**, 실제 live mismatch **9/10**, 그 9건의 export 허용 **9/9**. Both-oracle false PASS **6건**이다. 동물 변조는 시도됐지만 지속된 실제 차이가 없어 검출률 분모에서 제외했다. 유효한 master/follow 상태의 positive round trip은 별도 미검증 항목이다.

QA 파일명의 `Quarantined_*`는 QA 보관 명칭이다. **후보가 quarantine을 수행했다는 뜻이 아니다.**

A의 원래 `Corrupt_1_MissingHeldItem`와 `Corrupt_5_CorruptedAssignment`도 재시험했다. 3초 이후 즉시 판정하지 않고 최대100초 상태 polling을 수행했으며 **두 경우 모두 READY→SAVED**였다. 나머지 A 원래4건의 최종 상태는 재시험했다고 주장하지 않는다.

A script는 `sleep(3.0)` 후 상태를 읽고, oracle mismatch boolean을 `failClosedEnforced`라고 기록한다. corruption 후 실제 export 거부를 시험하지 않는다. [스크립트:362](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Frozen/run_settlement_roundtrip_poc.py:362), [스크립트:401](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Frozen/run_settlement_roundtrip_poc.py:401). 잠깐의 LOADING 또는 mismatch의 발견은 enforced fail-closed 경계가 아니다.

## 7. 주요 실패 원인 및 수정 요구 — 기존 결함에 연결

### QA-ENGINE-002 — Critical, STILL FAILING

**Location:** [WorkerBridge.cs:1480](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Frozen/WorkerBridge.cs:1480), `ExportSave`; load log tracking:412–447.

**Reproduction:** medicine stack5→4 또는 bed relation 누락. READY 도달. 후보 실제 C# comparator FAIL 확인. 그 뒤 `EXPORT_SAVE` 요청.

**Expected:** 검증 실패한 generation/artifact는 valid canonical export/accept 경로에 진입할 수 없어야 함.

**Actual:** `READY`만 검사한 뒤 `SaveGame`, File.Exists, hash로 `SAVED`. native save의 내부 로그 예외/부분 직렬화도 output 존재로 승인.

**Root Cause:** 비교 결과가 export lifecycle에 연결되지 않는다. Application log counter도 관측된 실제 load/save 의미 오류를 유효 승인에서 배제하지 못했다. 이를 엔진 내부 오류 전달의 정확한 원인까지 입증했다고 주장하지 않는다.

**Required Fix:** 유효한 source manifest/profile·generation·map·clock/revision에 결속된 semantic approval을 export/admission/publication 경계에서 검증할 것. 내부 save 오류와 partial output은 valid artifact와 분리할 것. 검증 이후 state가 변하면 승인을 무효화할 것. 단순 READY counter 강화만으로 본 공격은 닫히지 않는다. Production commit 방식은 본 시험에서 선결정하지 않는다.

### QA-ENGINE-006 — High, STILL FAILING

**Location:** [EngineHostCensus.cs:583](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Frozen/EngineHostCensus.cs:583), hediff string 생성:441, 비교:675, zones count:703; Frozen Python oracle 및 fixture generator.

**Actual:** skill은 수집하지만 비교 안 함. hediff는 Def/part 문자열만으로 severity 미검증. bill configuration/삭제, 동일 수의 zone 위치, fire dynamics, condition duration 검증 누락. Python은 hediff 제거도 놓친다. master/follow positive 상태와 valid bill/growing zone은 fixture에 없다.

**Required Fix:** 독립 source-static/live trusted oracle와 정확한 persisted reference/semantic assertions를 정의할 것. 최소 본 battery의 잔존9건을 검출하고 실제 gate에서 차단할 것. 양성 master/follow·valid bill·구역·power 연결·외부 Pawn 관계 fixture를 실제 native API/schema로 확인할 것. 환경 ID 재생성을 이유로 상태 자체를 제거하지 말 것. 최초 로드에서 발생한 손실을 post-load baseline으로 정상화하지 말 것.

두 결함을 닫거나 별도 새 결함 번호로 중복 생성하지 않는다. 기존 ledger 유지 권고이며 Master 상태를 직접 변경하지 않았다.

## 8. 환경 상태 및 jobs/reservations

### 환경 conservation

A→B와 B-posttick→C 모두 독립 normalized environment에서 **선택된 Def+position/count/HP 및 fire/growth/age/filth scalar 차이0**이다. geology3,670개는 해당 Def/position에서 ID가 모두 바뀌지만 공간·Def conservation은 유지됐다. strict custody ID 주장으로 혼합하지 않는다.

- Filth2,158(rock rubble2,157+dirt1)의 실제 spawnedThings 기반 상태를 비교했다. 후보 lister census의 누락을 count0으로 정상화하지 않았다.
- Source/B-before Fire1→B post100 Fire0→C Fire0. tick 중 native 소멸과 save/load 손실을 분리하여 posttick 기준으로 비교했다.
- 식물의 선택된 growth/age/position 상태, map conditions와 weather를 별도로 취득했다. full environmental schema/모든 임의 모드 field는 미인증이다.
- `tickedLastWeather` 차이는 해당 엔진 ExposeData에 저장되지 않는 cache다. condition duration/fireSize 변조를 검출하지 못하는 문제와 혼동하지 않는다.

### 활성 작업 / 예약

Native JOB 생성: Human302, Goto target `(140,0,148)`, Job_200000, 예약 성공. B100틱 후 위치 `(139,0,142)`→`(138,0,146)`, Goto 유지. C는 동일 위치/작업을 재로드했다. 별도 D는 active-job 저장본에서 Goto 및 reservation claimant Human302/Job_200000/maxPawns1/stackCount-1을 복원했다.

D40틱에서 bio 시간은 진행했지만 정수 cell 위치는 그대로였다. 따라서 D40틱만으로 목표 도착/완전 path continuation을 인증하지 않는다. engine `ReservationManager.ExposeData`는 예약을 저장하고 post-load에 무효 target/claimant/job를 정리한다. 해당 예약 target은 XML에서 대조했고 observer의 LocalTargetInfo struct reflection이 완전하지 않아 live 전체 예약 graph 검증은 미인증이다. 1-map context에서 외부 map job/예약 누출은 관측되지 않았다. source jobGiverKey 경고는 별도 OPEN reference 문제로 남긴다.

## 9. Player-global closure

원본 source의 research progress는 이 경로를 강하게 시험하기에 부족했다. QA-only composed input에 **Stonecutting progress123**을 부여했다. Process12860에서 load/export, fresh Process23948에서 progress **123→123**을 확인했다. 이는 canonical ResearchManager가 **함께 포함됐을 때** 유지되는 좁은 증거다.

ResearchManager를 전부 제거한 supplementary Process24572는 100초 관측에서 `LOADING`, LastFailure빈값이었다. 로그에는 null manager/render/alert 예외가 있었고 QA ready assertion이 실패했다. harness는 cleanup 후 종료했으며 READY 또는 export 성공으로 기록하지 않았다. **제거하면 자동 기본 상태로 안전 복원된다는 가정은 확인되지 않았다.** 이 실패는 composed closure dependency의 추가 증거다. `run_research_closure.py`의 비정상 종료를 test PASS로 숨기지 않는다.

- Ideologies13 유지. source precepts99→native output614. 엔진이 누락 precept/기본값을 보완하는 로그가 있다. 모두 잘못된 변경이라고 단정하지 않지만 “정확히 동일한 전역 상태”가 아니다. canonical provenance/승인된 보완 정책 필요.
- WorldPawns20 유지. Human302 spouse Human309 같은 target 외부 Pawn 관계가 실제 존재하며 map이 없는 외부 참조도 조사했다. 전체 owner WorldPawns 유지가 최소 closure임을 입증하지 않았다.
- Royalty DLC는 활성화돼 있으나 fixture의 royal titles/permits0. tracker 존재만으로 title/permit/faction 관계 보존을 인증하지 않는다.
- quests0. QuestManager 및 GameComponents는 남아 있으나 target에 관련된 active quest의 external reference/reward/lifecycle은 미검증이다.

**최종 PlayerGlobal schema는 OPEN**. 어느 owner-global state를 lease하여 composed input으로 제공하고 어떤 mutation을 publish할지는 future ADR 계약으로 남긴다.

## 10. G-Q1 / clock 독립 증거

Fresh source2maps PID34708에서 Map0 300틱 완료 후 Map1로 전환하여 다시300틱 완료했다. 실제 값:

| 상태 | TicksGame / TicksAbs | Map0 bio / chrono | Map1 bio / chrono | GlobalProbe / MapProbe0 / MapProbe1 |
|---|---|---|---|---|
| before | 1823 /16823 | 176109104 /698109106 | 176109104 /698109106 | 0 /0 /0 |
| Map0 +300 | 2123 /17123 | 176109404 /698109406 | **176109104 /698109406** | 300 /300 /0 |
| Map1 +300 | 2423 /17423 | **176109404 /698109706** | 176109392 /698109706 | 600 /300 /300 |

비활성 폰의 position/food/rest/bio는 해당 구간에서 동결됐다. Map1 inactive 구간 rest0.954493/food0.7479999 유지. 이후 Map0 inactive 구간 rest0.949743/food0.7399999 유지. 선택된 식물 growth도 동결됐다. 그러나 chronological getter는 비활성 맵에서도 +300씩 진행한다. SkyGlow는 Map1 inactive0.64→0.66, Map0 inactive0.81→0.84로 바뀐다. process-global QA GameComponent도 계속 tick한다. **map local simulation freeze와 전체 temporal getter/전역 state freeze는 다르다.**

actual engine IL: [engine-il.txt](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Evidence/engine-il.txt). 최소 Vanilla 다중 맵 targeted virtualization 검토 대상:

| 실제 callsite/subsystem | 필요한 분리 / 증거 한계 |
|---|---|
| Pawn_AgeTracker.AgeChronologicalTicks→GenTicks.TicksAbs−birthAbsTicks | inactive temporal getter 오염 실제 재현. biological age와 별도 clock provenance 필요 |
| GenLocalDate.HourOfDay/DayTick/DayPercent→global absolute tick + longitude; SkyManagerUpdate→DayPercent | tile longitude는 시간대 offset만 제공. 독립 frozen time을 제공하지 않음. UI/render clock도 map context 필요 |
| TickManager.DoSingleTick + GameComponent tick | 전역 increment와 map scoped dispatch 분리. global component counter 진행 실제 측정 |
| Pawn_AgeTracker.AgeTickInterval, PowerNet.PowerNetTick의 TicksGame 조회 | static IL로 실제 global getter 의존 확인. 대상 deadline/phase와 저장 timestamp 경계 검증 필요 |
| Pawn_NeedsTracker.NeedsTrackerTickInterval / HealthTick→Hediff.TickInterval / Plant.TickLong / JobTrackerTick | tick frequency와 elapsed-counter category를 직접 조사. 멈춘 dispatch와 absolute deadline 재개를 분리. 모든 field virtualization이 검증됐다는 뜻 아님 |
| Job.ExposeData/startTick, Bill/Bill_Production.ExposeData/ShouldDoNow, WeatherManager 및 condition state | 저장 absolute timestamp/reference를 단순 rebase하면 안 됨. 정확한 persisted clock-domain 계약 후 resume/reload 검사 필요 |

이 목록은 engine-specific audit 시작점이며 모든 필요 hook을 완성했다고 인증하지 않는다. **G-Q1 유지 OPEN.** singleton이라는 이유만으로 Separate Execution Islands를 선택하지 않는다. 시간 컨텍스트/targeted virtualization과 별도 실행 섬의 비교는 Master의 독립 ADR 결정이다.

## 11. Master에게 권고하는 다음 게이트

1. A의 exact report/actual artifact SHA·actual profile·source lineage 차이를 정정하고 검증 가능한 manifest로 재동결한다.
2. clean semantic fixture를 먼저 입증한다. missing Def, duplicate registry error와 partial bill save가 남은 결과를 canonical clean-load 증거로 제출하지 않는다.
3. source provenance에 결속된 semantic approval 및 save-error/partial-output quarantine을 실제 export/admission 경로에 연결하고 본 negative battery를 다시 실행한다.
4. complete custody/reference와 선택된 dynamic environmental assertions를 명확히 한다. valid bill/power/master/follow positive graph 및 active-job reload continuation을 보완한다.
5. 수정 후보에서 fresh A→B→C를 다시 실행한다. PlayerGlobal과 G-Q1은 별도 OPEN 계약/검증으로 유지한다.

**최종 판정: FAIL.** Native fresh-process materialization/저장 및 좁은 target state 보존 경로는 관측됐지만, 이 정확한 후보의 B2-lite core gate는 승인하지 않는다. QA-ENGINE-002/006은 STILL FAILING 유지 권고다. G-Q1·PlayerGlobal·material-state Production·Tactical Production·all-mod 호환성은 승인하지 않으며 Master ledger를 변경하지 않았다. 요청된 독립 보고서를 제출하고 추가 구현을 시작하지 않는다.
