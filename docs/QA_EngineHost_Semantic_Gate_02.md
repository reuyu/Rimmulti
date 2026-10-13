# QA Engine Host Semantic Gate 02 — Independent E2

```yaml
Work Package: WP-QA-ENGINE-HOST-SEMANTIC-GATE-02
Reviewer: GPT-6.1 Sol / Independent QA & Architecture Reviewer
Date: 2026-10-03 (Asia/Seoul)
Target: POC_EngineHost_Semantic_Gate_02.md
Verdict: FAIL
QA-ENGINE-002 Recommendation: STILL FAILING
QA-ENGINE-006 Recommendation: STILL FAILING
Candidate Source / Binary / Fixture Modified by QA: No
Candidate Rebuilt: No
Candidate Freeze: 205 files before / 205 after / 0 changes
Master Ledger / Architecture State Changed: No
```

## 1. 판정과 핵심 증거

**최종 판정: FAIL.** 비교기를 적용하면 독립 변조 15/15건을 검출하고 export를 차단한다. 그러나 그 비교기의 기준을 누가 승인할 수 있는지 보장하지 않는다. 손상된 READY 상태에서 `EXPORT_CENSUS → APPROVE_SEMANTIC → EXPORT_SAVE`를 실행한 **6/6건 모두 ARTIFACT_APPROVED**였다.

더 직접적인 저장 경계 실패도 재현했다. 승인된 live Shooting=10을 그대로 두고 QA 주입으로 **staged save의 Shooting만 15**로 변경하자 오류 없이 승격됐다. 새 프로세스에서 승인된 파일을 읽으면 실제 Shooting=15이며 원래 기준과 불일치한다. XML 끝부분을 잘라 문서가 완성되지 않은 파일도 ARTIFACT_APPROVED였다.

비틱 상태 변경 10/10건도 재승인 없이 export됐다. 그중 7건은 현재 comparator도 불일치를 검출하는 상태이고, 나머지 3건은 수집된 field 자체를 comparator가 검사하지 않는 사례다. 일반 tick/reload/map-switch 차단과 save-time Error/Exception 격리는 통과했지만 이 우회를 닫지 못한다.

증거 루트: [SEMANTIC-GATE02-20261003](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003). [results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/results.json), [summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/summary.json)에 명령 응답, PID, 입력 SHA, 상태, comparator 결과, 최종 파일 존재 여부를 기록했다. A의 assertion을 호출하여 통과 수를 재사용하지 않았다.

## 2. Exact provenance와 증거의 경계

### 실제 바이너리와 fixture

| 대상 | SHA-256 / 실제 식별값 |
|---|---|
| RimWorld | **1.6.4871 rev591**, Unity **2022.3.35f1** — 실제 HELLO/META/player.log |
| RimWorldWin64.exe | `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D` |
| Assembly-CSharp.dll | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` |
| Assembly-CSharp MVID | `61e41735-6189-4da4-9d21-0260257b5097` — actual loaded snapshot |
| WorkerBridge DLL, 99,840 bytes | `2FDEB8DB7EE9271044294ADAA9D8CFEC86D559510D7F8182234F9FCBEFB3D5BC` |
| WorkerBridge MVID | `9e1e7d98-530c-4911-908e-fd2f876ef05e` — actual loaded META 및 PE metadata |
| WorkerBridge.cs | `6D4D5064C25C84BD6ED670833D1BEDCB2D173EB5623E2E0A708C8A26B260512A` |
| 보고 대상 EngineHostCensus.cs | `01A7430F083201961AA96248CD12C6443DA6DDC9A62607EBC6504FA053BA3C48` |
| CleanSettlementFixture.rws, 25,896,703 bytes | `BCDEA94EFEE63A609EA6652B24B8913CD8C74A5ABB1A36489D386E892FC44FC4` |
| TargetSettlement_Clean_ContextB.rws, 14,015,735 bytes | `6F535B9162C5C5267F1BA57DC056891449C4879AD51C5A906DC96AFBEF7CEEBD` |
| A 제출 A_ApprovedArtifact.rws | `0D6B538566BA11A879D4E50BBF52392D0CC57D21DFFF9BD81A1F01312A0F424B` |
| A 제출 B_PostTick_Artifact.rws | `BC522786B61E620B9B370CBF3218A6BF38959123F1B6DF668A1EA8E842B55483` |
| A/B/C ModsConfig.xml | `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C` — 세 파일 동일 |

위 주요 DLL/fixture/export 해시는 제출 보고서와 일치한다. 실제 로드 WorkerBridge 경로는 아래 설치 junction의 대상이다.

`C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll`

[IndependentGateR2-metadata.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/IndependentGateR2-metadata.json) 및 이후 process metadata에 loaded path/SHA/MVID를 보존했다. QA는 다른 DLL을 빌드하여 대신 실행하지 않았다.

### Source / harness lineage의 불일치

실제 설치 junction 옆의 `Source/EngineHostCensus.cs` SHA는 **`123602142BFC13B1C599782CB6B3465D1B25A38480832F0322B454981C7C5F47`**이며 보고서의 workspace source와 다르다. 이 옆 파일을 무조건 actual compiled source라고 간주하면 안 된다. 동결 DLL의 `CensusManifestData.ToJson` IL은 `JsonConvert.SerializeObject`를 호출한다. 보고 대상 `01A743...`와 이 동작이 일치하고, 옆 source의 수동 JSON 작성 구현과는 다르다. 해당 옆 source/bin의 과거 DLL/PDB도 시험 DLL과 해시가 달라 **시험 DLL의 source checksum 증명으로 사용하지 않았다**.

양쪽 source를 `Frozen/Reported-*`, `Frozen/Loaded-*`로 각각 보존했다. 실제 바이너리의 승인/export/comparator IL은 [worker-il.txt](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/worker-il.txt)에 독립 추출했다. 정상 동작·결함 재현의 대상은 명시된 `2FDEB8...` DLL이다. sidecar source 일치를 비롯한 build lineage 전체가 인증됐다는 뜻은 아니다.

제출된 보조 증거의 정확한 SHA도 현재 파일과 다르다.

| 파일 | A 보고서 SHA | QA 동결 실제 SHA |
|---|---|---|
| census_oracle.py | `CF92120038F6E6DAF356B272A80775C51DC9DDC10A887EB41D09DE95CE6A784B` | `0B9079D5E52276B44D1BC41DDFFBC08390EBE2EEFEB5AD0F4E6FCC7E5B12555D` |
| run_semantic_gate_02.py | `D6587A13B2C969F2A9B801D38DCEDD2EBC409BE76E6CE36B8287F41604BA6451` | `F24301FBD648BF602CBD6818E4A5A9E959CAE383C22E058D313E5FFBC174D0B5` |
| semantic_gate_02_results.json | `C6C82ACD9A833E8F59C75E5D875F614603B6432DEBA39420F3E502B59D04A41B` | `A3A8B51EEFCE69CDA682E8C53B77FC4B0B0039D370EAF9ACF115C3E9E9248B94` |

이 차이는 QA 시작 전부터 있었으며 QA 도중의 candidate 변경은 아니다. 보고서·보조 파일의 freeze lineage 정정이 필요하며 A의 E1 숫자를 독립 증거로 채택하지 않는다.

### 동결 범위 / 동시 작업 / QA instrumentation

Engine Host 후보 source/binaries/fixtures/profile, 설치 WorkerBridge, QA Probe 원본, Harmony 및 실제 로드 Base DLL 등을 **205파일**로 명시하여 동결했다. [final-integrity.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/final-integrity.json): **205→205, candidate 변경0**.

전체 Production 트리도 참고용으로 전후 기록했다. 별도 Pipeline 작업이 진행되어 Server subtree의 파일·빌드·오래된 DB를 포함한 **17경로가 변경/삭제**, 총358→353이었다. 따라서 “프로젝트 전체가 변경0”이라고 주장하지 않는다. 이 서버 subtree는 본 실행에 로드되지 않으며 Engine Host candidate 동결과 실제 로드 DLL은 변하지 않았다. **QA가 Production에 쓴 파일은 없다.**

초기 광범위 scratch inventory에서 별도 SQLite 실험 script 추가를 감지해 engine 실행 전 멈췄다. 보고 대상 파일의 변경0을 확인하고 불필요한 별도 작업 파일을 제외하여 위 범위를 재동결했다. `initial-broad-inventory.json`, `preflight-scope-event.json`에 기록을 남겼다. 후보 변경을 무시하며 검증을 계속한 것이 아니다.

QA-only Observer DLL은 기존 ProbeMod에 **추가 파일**로 잠시 배치했고 종료 후 그 정확한 파일만 제거했다. 원래 Probe DLL, 후보 DLL, fixture는 바꾸지 않았다. 관찰 기능은 engine 객체를 읽고, 별도 명령은 명시된 시험 상태를 변조한다. 저장 경계 주입은 QA assembly의 Harmony **native `GameDataSaveLoader.SaveGame` postfix**에서 QA-owned staged file 또는 시험 live 상태만 바꾼다. WorkerBridge gate/comparator 구현을 patch하거나 성공 응답을 대체하지 않는다. 비주입 실행에는 해당 fault가 작동하지 않는다.

Observer v1/v2는 SHA/MVID와 loaded path를 process별 metadata에 남겼고 v1 binary를 Evidence에 보존했다. Production/PoC를 재빌드하지 않고 QA Observer와 IL reader만 빌드했다. GUI/Computer Use는 사용하지 않았다.

## 3. Profile와 clean positive fixture

실제 활성 순서는 A와 같은 10개다.

1. brrainz.harmony
2. ludeon.rimworld
3. ludeon.rimworld.royalty
4. ludeon.rimworld.ideology
5. ludeon.rimworld.biotech
6. ludeon.rimworld.anomaly
7. ludeon.rimworld.odyssey
8. wareconomy.hybridmultiplayer
9. wareconomy.workerbridge.poc
10. qacodex.engine02.probe

추가 Observer는 10번 mod에서 읽는 QA assembly다. candidate의 gameplay Def/profile를 바꾸지 않았다. 구버전의 DLC 누락 문제는 본 profile에서 재현되지 않았다. 그러나 **“clean fixture이고 설명한 graph가 그대로 존재한다”는 주장은 승인하지 않는다.**

| 지원 graph | 독립 live 확인 / 제출 설명과의 차이 |
|---|---|
| Skills | Human302 Shooting10 등 7개 지정 skill 확인. 누락된 나머지5개 skill은 엔진이 level0으로 자동 추가 |
| Hediffs | Stab3/Torso 확인. BionicTongue1은 **Tongue가 아니라 Finger/right index finger**에 붙어 있음 |
| Animal | LabradorRetriever207367 Master=Human302, followDrafted/Fieldwork=true 확인 |
| Bill | TableSculpting990014 Make_SculptureSmall, targetCount10, skill range0~20 확인. clean save의 부분 bill 예외는 관측 안 됨 |
| Zones | stockpile ID1, 2cells; growing **ID0, 1cell**. 제출된 ID1/2·growing24cells와 다름 |
| Designations | Mine150/150, CutPlant 대상 rice, Haul 대상 held medicine의 3건 확인 |
| Bed | Bed990012↔Human302 ownedBed/assignment 확인 |
| Nested holder | MinifiedThing990030→Stool990031, corpse→Human207370 확인 |
| Power | Battery energy600 및 SolarGenerator를 포함한 native PowerNet 확인 |
| Fire | size0.45 확인. 위치는 **(170,0,170)**, ticksSinceSpawn0; 제출146/146·50과 다름 |
| Plant | rice **growth0.5/age0**; 제출0.85/12000과 다름. 원본 XML도 growth0.5, age 없음 |
| Condition | Aurora duration60000 확인. live ticksPassed1823; 제출2500과 다름 |
| External relation | Human302 Spouse→Human309 확인 |
| Active job / reservation | 기본 Human302 GotoWander 확인, **기본 reservation table0**. 별도 QA ordered Goto와 예약을 실제 API로 만들어 round-trip 시험 |

첫 원본/context load에서는 `Thing_Human100302/100305/100308`에 대한 **RitualObligation 참조 해석 실패3건**, hidden ritual precept 자동 보완 및 누락 skill 자동 추가가 로그에 있었다. 해당 player-global 의무 graph를 지원 범위에서 명시적으로 제외하거나 승인된 보완으로 설명하지 않은 상태이므로 전체 clean claim을 인증하지 않는다. native Missing Def/duplicate registration/partial-bill-save 오류가 clean target에서 다시 발생했다고 과장하지는 않는다.

기존 source-static census를 현재 live와 비교하면 **4errors**다: corpse 안의 Human207370 누락 기준, mech animal 분류, null/empty master 및 Thing_ prefix master 차이. 이 기준으로 원본부터 실패하는 battery는 특정 주입의 검출 증거가 될 수 없다.

독립 negative 시험은 원본의 selected static facts와 live 값을 먼저 기록한 후, **동일한 clean live witness**와 각 주입 결과를 비교했다. 이 witness는 comparator 회귀 anchor다. 최초 로드 손실을 정당화하는 canonical authority manifest로 인정한 것이 아니다. 위 positive 차이와 경고는 별도 실패로 유지한다.

## 4. 독립 persistent negative battery — 15건

Candidate fixture를 읽어 QA-owned copy에서 XML을 독립 변조했다. 원본에 쓰지 않았다. 각 case마다 실제 `LOAD_SAVE`, READY 확인, full live observer/census, 실제 DLL comparator, `APPROVE_SEMANTIC`, 실제 `EXPORT_SAVE`를 실행했다.

| Case | Source expected → injected input → final live | Comparator | 실제 export / 최종 approved 파일 |
|---|---|---|---|
| 01 held stack | Medicine5→4→4 | count mismatch | BLOCKED / 없음 |
| 02 skill | Shooting10→15→15 | skill mismatch | BLOCKED / 없음 |
| 03 severity | Stab3→1→1 | severity mismatch | BLOCKED / 없음 |
| 04 removal | BionicTongue1개→제거→0개 | count/missing | BLOCKED / 없음 |
| 05 master/follow | Human302/true→master없음/false→없음/false | master/followDrafted | BLOCKED / 없음 |
| 06 bill | targetCount10→25→25 | targetCount mismatch | BLOCKED / 없음 |
| 07 zone | growing cell139/145→139/146→동일 변경 | exact-cell mismatch | BLOCKED / 없음 |
| 08 designation | Mine150/150→150/151→동일 변경 | target mismatch | BLOCKED / 없음 |
| 09 fire | size0.45→0.90→0.90 | size mismatch | BLOCKED / 없음 |
| 10 plant | 실제 growth0.5→0.4→0.4 | growth mismatch | BLOCKED / 없음 |
| 11 condition | duration60000→12000→12000 | duration mismatch | BLOCKED / 없음 |
| 12 bed | Human302 소유/배정→해제→해제 | owned-bed mismatch | BLOCKED / 없음 |
| 13 relation | Spouse→ExSpouse→ExSpouse | relation mismatch | BLOCKED / 없음 |
| 14 power | energy600→200→200 | scalar mismatch | BLOCKED / 없음 |
| 15 nested holder | Stool990031→inner defWoodLog→WoodLog990031 | missing/unexpected/container | BLOCKED / 없음 |

**15/15 READY, 15/15 검출, 15/15 최종 export 차단.** 각 입력 SHA 및 source/injected facts는 `negative-XX-input`, 실제 live는 `negative-XX-live.snapshot.json`/`full-census.json`, comparator와 응답은 `negative-XX-comparator`/`gate`다. [negative-independent-summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/negative-independent-summary.json)에 모두 묶었다. 최종 approved 경로와 staging/quarantine 경로를 구분했다. 비교 실패 단계에서 차단된 case는 staged save 자체를 생성하지 않았다.

**A battery의 추가 문제:** A의 10번 fixture는 실제 `<growth>0.5</growth>` 그대로다. generator는 존재하지 않는 `growthInt` element만 찾고 없으면 넘어간다. 제출된 “0.85→0.40” 주입이 그 파일에 없다. 원본부터 틀린 source-static 기준에 거절된 것을 plant 변조 검출로 해석할 수 없다. QA는 실제 저장 field `growth`를 바꾸어 별도로 검출을 입증했다.

## 5. Mandatory self-baselining attack

**QA-ENGINE-002: STILL FAILING. Severity: 기존 Critical 유지.**

Location: [HandleApproveSemantic:1585](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1585), [LoadFromFile/Compare:1624](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1624), [EXPORT_CENSUS:1854](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1854).

재현:

1. 02/03/04/06/07/13의 persistent corrupt input을 로드하여 READY.
2. clean witness로 비교하고 승인하면 SEMANTIC_REJECTED/EXPORT_BLOCKED.
3. **같은 손상된 live 상태**에서 `EXPORT_CENSUS SelfCorruptedXX 0`.
4. 생성 파일을 `APPROVE_SEMANTIC <absolute path>`로 제출.
5. `EXPORT_SAVE SelfCorruptedXX_Approved`.

**Actual: 6/6 SEMANTIC_APPROVED→ARTIFACT_APPROVED.** Shooting15, Stab1, BionicTongue없음, bill25, 이동된 zone, ExSpouse가 각각 최종 저장 XML에도 남았다. 비교 실패 상태에서 새 census를 주면 failed 상태 자체도 다시 승인된다. independent source/context authority 또는 invariant의 거절은 없었다.

Root Cause: 비교 대상과 기대값을 동일한 손상 상태가 결정한다. 임의 파일 경로로 전달된 manifest가 신뢰된 기준인지, 어느 source/context/profile/revision에서 승인됐는지 확인하지 않는다. loopback control caller를 Production 인증으로 취급하지 않는다. 내부 제어 caller가 신뢰됐다는 주장만으로 그 caller가 현재 corrupt 결과를 canonical 기대값으로 지정할 권한까지 증명하지 못한다.

Required Fix: approval 기준의 nomination authority와 source/context/profile/revision binding을 명시하고 실제 gate에서 검증할 것. 현 상태에서 수집한 self-census는 evidence output으로 구분할 것. comparator 구현의 검사량을 늘리는 것만으로 self-baselining은 해결되지 않는다.

## 6. Manifest authority / path attacks

| 공격 | 실제 결과 / 해석 |
|---|---|
| Saves 밖 arbitrary absolute path | 승인·export 허용. 위치 자체가 권한 증거는 아님 |
| 동일 material에 mapIndex99/mapTile-123/parent WRONG/playerFaction WRONG/ticks-999/manifestVersion wrong | comparator0errors, 승인·export 허용. 해당 origin metadata 검사 없음 |
| 실제 Map1에서 EXPORT_CENSUS한 manifest를 Map0에 제출 | 52,356 material mismatches로 거절. origin binding 때문이라고 확대 해석하지 않음 |
| 이전 generation의 동일-state manifest 재제출 | Gen18의 witness가 reload Gen19에서 재승인·export됨. manifest generation/provenance 없음 |
| 다른 profile/fixture authority claim | 잘못된 ContentProfileFingerprint/ContextFixtureSHA/sourceAuthority/generation claim을 담은 파일도 승인·export. 모델에 없는 권위 field는 무시됨 |
| A의 Profile_A manifest 재제출 | 실제 material이 같아 승인. 물리적 profile directory가 다르다는 사실 자체를 잘못된 content profile로 간주하지 않음 |
| A의 Profile_B post-tick manifest를 pre-tick 상태에 제출 | actual 변화로 거절. profile/source provenance 검증 증거는 아님 |
| 승인 후 같은 filename을 다른 bytes로 교체 | export 허용, 응답은 **교체 전 manifest SHA** 유지 |

파일 교체 뒤 이전 hash를 유지하는 것만으로 무조건 semantic corruption이라고 단정하지 않는다. immutable approved manifest를 실제 보존하고 그것을 기준으로 bytes를 검증한다면 파일 재읽기가 필수는 아닐 수 있다. **현재는 trusted immutable manifest record도, export 시 그 record와의 live/staged 의미 대조도 없다.** 따라서 filename 또는 출력 hash만으로 authority binding을 인증할 수 없다.

APPROVE_SEMANTIC에는 caller의 expected manifest hash를 받는 인자가 없다. manifest 파일을 읽어 비교한 뒤 별도 open으로 hash한다. 읽기·비교·hash가 동일 bytes를 증명하는 원자적 read가 아니며 해당 파일-read TOCTOU는 정적 위험이다. 그 정확한 외부 file-replacement race를 실행 재현했다고 주장하지 않는다.

## 7. Non-tick mutation invalidation과 comparator 잔여 누락

Location: [export bindings:1679](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1679), [approvedCensus 저장:1655](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1655), [CompareCensus:576](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-EngineHostCensus.cs:576).

각 시험을 원본 load→clean 승인→native live 변조→export 순서로 독립 실행했다. **모든 시험의 TicksGame은 1823→1823**이다. 별도 legitimate generation/revision fence가 변조를 검출한 흔적은 없었다.

| 변경 | live comparator | 재승인 없는 export |
|---|---|---|
| Shooting10→15 | FAIL | ARTIFACT_APPROVED |
| Stab3→1 | FAIL | ARTIFACT_APPROVED |
| holder count5→4 | FAIL | ARTIFACT_APPROVED |
| stockpile cell 제거 | FAIL | ARTIFACT_APPROVED |
| Mine designation 제거 | FAIL | ARTIFACT_APPROVED |
| Spouse relation 제거 | FAIL | ARTIFACT_APPROVED |
| owned bed 해제 | FAIL | ARTIFACT_APPROVED |
| followFieldwork true→false | **PASS** | ARTIFACT_APPROVED |
| plant age0→12001 | **PASS** | ARTIFACT_APPROVED |
| bill suspended false→true | **PASS** | ARTIFACT_APPROVED |

Root Cause(002): approval 무효화는 특정 tick 경로에만 연결돼 있다. approval 때 저장하는 `approvedCensus`는 export에서 다시 비교하지 않는다. Ticks/map index/generation 같음은 semantic state 같음이 아니다.

Root Cause(006): followFieldwork/plant age/bill suspended는 수집하지만 비교하지 않는다. hediff.part/loadID와 curJob도 수집하되 현재 비교는 각각 def+severity 및 job 미검증이다. clean fixture의 BionicTongue가 Finger에 붙어 있는 상태를 manifest 생성만으로 정상화했다. 15개 큰 차이 검출로 모든 선언 field나 complete reference graph를 인증할 수 없다.

Required Fix: supported semantic field 계약과 complete comparator predicate를 일치시키고, tick-independent mutation invalidation 또는 semantic/version proof를 export에 결속할 것. age/part/followFieldwork/bill settings를 수집만 하고 검증했다고 제출하지 말 것.

## 8. Saved-byte semantic proof — 실제 실패

Location: [SaveGame:1741](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1741), [XML gate:1771](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1771), [promotion:1804](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Frozen/Reported-WorkerBridge.cs:1804).

**Severity: 기존 QA-ENGINE-002 Critical / QA-ENGINE-006 High에 연결. 새 공식 결함 번호를 임의 생성하지 않는다.**

QA native SaveGame postfix는 serialization 종료 후 gate가 file를 검사하기 전에 QA-owned staged file만 변경했다. comparator/export gate 자체는 원래 DLL 그대로다. 이는 특정 vanilla serializer가 자연히 Shooting을 잘못 저장한다고 주장하는 것이 아니라, Work Order가 요구한 **오류 로그 없는 잘못된 staged bytes의 gate 시험**이다.

### Silent semantic alteration

- 승인/live Shooting: **10**.
- native save가 처음 쓴 Shooting: **10**.
- QA staged XML 변경 후 Shooting: **15**, live는 여전히10.
- Unity Error/Exception 발생 없이 **ARTIFACT_APPROVED**.
- 최종 SHA: `EFB5AF74FB63C28EBA441B3A3902E91DCC3F4E53400FFC18D45E786A50FDD99F`.
- 새 프로세스 PID19712에서 최종 파일을 로드하면 **READY / Shooting15**.
- 원래 clean 기준 comparator: **SKILL_MISMATCH Expected10 got15**.

`save-fault-silent-skill`, `saved-wrong-fresh-reload` 및 saved XML이 직접 증거다. 따라서 단순 live approval이 saved artifact의 의미를 증명하지 않는다.

### XML tail corruption

native 생성 파일 끝200bytes를 제거했다. `<savegame>/<meta>` 앞부분은 남는다. gate는 두 요소를 만나자 읽기를 중단하여 손상된 파일을 **ARTIFACT_APPROVED**했다.

- SHA: `F4A5DE8F57E77AB1316B5B3325B69ADFD600F0BE1875C5EC5D87BFD71F4594C7`.
- 독립 전체 XML parse: **unclosed token, line433301 column2**.
- [truncated-approved-xml-validation.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/truncated-approved-xml-validation.json).

Actual validation은 전체 XML 문서 완전성도, supported field static comparison도, fresh rematerialization 비교도 수행하지 않는다. 그 조건에서 승인됐다는 hash는 잘못된 파일의 hash일 뿐이다.

Required Fix: staged bytes의 완전한 syntax/semantic proof를 trusted approved state와 결속할 것. runtime fresh reload가 필요한 field는 실제 rematerialized graph와 비교하고, static 검증 가능한 field는 정확한 persisted schema로 검사할 것. 약한 envelope 검사를 semantic validation으로 명명하지 말 것.

## 9. Save-time Error / Exception gate

**이 좁은 경로는 통과.** QA native postfix의 실제 `Verse.Log.Error` 또는 IOException으로 candidate의 기존 log listener/exception catch를 시험했다.

| 공격 | 실제 결과 | 이전 최종 승인 파일 |
|---|---|---|
| 실제 Error log1건 | EXPORT_FAILED, VALIDATION_FAILED, Quarantine_* 파일 | SHA 불변 `109AC80DA0E5856267871F9CD5753F676A55065AE75C59AEB4F8088405162B2F` |
| 실제 IOException | EXPORT_FAILED, VALIDATION_FAILED, Quarantine_* 파일 | SHA 불변 `B136C32CFF0F3E277A9F66DFE2A6BAD4CBF31544FF8EBB180AA179CC3F81574C` |

이전 final을 먼저 승인·저장한 뒤 **같은 final name**을 대상으로 실패시켰다. 신규 실패 파일이 final을 덮어쓰지 않았다. 실패 후 재검증 상태도 확인했다. 그러나 semanticState만 FAILED이고 `lastValidationSummary`에는 이전 “0errors approved” 문구가 남는다. 실제 실패는 lastFailureReason/export 응답에 있으므로 혼동 방지 필요.

실제 staging/quarantine은 별도 Staging/Quarantine directory가 아니라 **Saves 안의 `Staging_*` / `Quarantine_*` filename prefix**다. A의 directory 설명과 구분한다. 정상 승격도 existing final의 `File.Delete` 뒤 `File.Move`이며 원자적 교체가 아니다. 두 호출 사이 프로세스 종료/이동 실패 시 기존 final 소실 가능성은 정적 잔여 위험이며 이번 저장 오류 시험에서 재현됐다고 주장하지 않는다.

## 10. Approval invalidation races / lifecycle

| 경계 | 시험 결과 |
|---|---|
| 일반 STEP_TICKS 후 export | approval 무효화, export 차단 |
| 승인 후 실제 LOAD_SAVE, LOADING 중 export | 차단 |
| generation 증가하여 reload READY 후, 재승인 없는 export | VALIDATION_REQUIRED / 차단 |
| 새 Worker NO_GAME에서 export | 차단 |
| 승인 Map0→실제 SET_TARGET_MAP1→export | Map index mismatch / 차단 |
| native save 반환 직전에 live skill10→15, 동일 tick | 최종 ARTIFACT_APPROVED. 저장 bytes10/live15로 달라진 lifecycle을 승인 유지 |
| native save 반환 직전에 실제 DoSingleTick1823→1824 | ARTIFACT_APPROVED, 응답/ApprovedTicks는1823 유지 |
| native save 반환 직전에 QA generation2→3 | **ARTIFACT_APPROVED, actual Gen3 / ApprovedGen2** |

마지막3개는 QA boundary injection이다. 실제 network reload가 main-thread save 중 동시에 완료됐다고 주장하지 않는다. ordinary command reload 차단은 인정하되 gate의 마지막 binding 검사가 promotion 이전에 재실행되지 않는 것을 분리 검증했다. async lifecycle 또는 save callback mutation을 안전하게 처리한다는 주장에는 이 경계가 필요하다.

generation 주입의 첫 QA 시도는 long field를 int로 읽는 Observer 오류로 IOException 경로처럼 실패했다. 그 결과를 generation fence PASS로 계산하지 않았다. QA Observer v2에서 타입을 바로잡은 **`generation-at-save-boundary`**가 실제 Gen2→3 우회를 입증한다. candidate는 바꾸지 않았다.

## 11. 독립 fresh-process A→B→C

| process | PID | 실제 결과 |
|---|---:|---|
| FreshA | 34736 | fixture load. QA native ordered Goto / 예약 생성. 실제 승인/export |
| FreshB | 28740 | A artifact load. 현재 선언 census field 비교0diff. Goto와 예약 유지. 100 sliced ticks 실행 |
| FreshC | 35260 | B post-tick artifact load. 현재 선언 census field 비교0diff. post-tick 위치/job/예약 유지 |

독립 A export SHA: **`4162C72C1D27B53E74102C05B02903C76C7CD546716BFE7FDB46BA7DF9CA22FD`**.

독립 B export SHA: **`3A0AFEE1C78E176602488D41BCDC235511AE7B559AAE50F4456571D158DBC464`**.

실제 Human302:

- A / B-before: `(139,0,142)`, Goto Job_200000, target `(140,0,148)`.
- B after100 / C: `(138,0,146)`, Goto 유지.
- 예약 claimant Human302, Job_200000, target140/148, maxPawns1, stackCount-1은 A→B→C에 보존.
- B는 TicksGame1823→1923, unapproved post-tick export는 차단.

후속 승인은 B의 **post-tick self-census**를 사용했다. 이는 전송 fidelity witness이며 trusted authority source를 증명하는 manifest가 아니다. B의 합법적 상태 변화 범위를 독립 정치/경제/temporal authority가 승인했다는 주장으로 사용하지 않는다.

현재 census에 선언된 수집 field는 generatedAt을 제외하고 observation collection 순서를 정규화하여 A→B/B-post→C 모두0diff였다. [all-declared-fields-A-B.diff.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/all-declared-fields-A-B.diff.json), [all-declared-fields-B-C.diff.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/all-declared-fields-B-C.diff.json), [fresh-jobs-and-progress.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/fresh-jobs-and-progress.json). 이는 comparison에 빠진 graph 전체/모든 engine private field까지 보존됐다는 뜻은 아니다. 직접 job/reservation 비교는 census comparator의 job 미검증과 별도로 수행했다.

Clean source 자체도 PID11844에서 실제 2-map load/save를 수행했으며 export는 가능했다. 그 성공이 앞서 기록한 source reference 문제나 잘못된 positive field 설명을 해소하지는 않는다.

## 12. Context / G-Q1 / scope guard

본 context의 공식 명칭은 **Pruned Target-Map Owner Context**다. source2maps에서 target1map 및 관련 parent world object로 가지치기한 결과이며 owner World/Ideo/Research/Quest 등 상당한 global context가 남아 있다. **minimal dependency closure를 입증하지 않았다.**

G-Q1은 해결하지 않았다. supplementary2-map 시험에서 target0의20 sliced ticks를 실행했다. 비대상 Map1 Human1100302 biological age는176109104로 유지되고 위치도 동일하지만 chronological age는 **698109106→698109126(+20)**였다. target/global TicksGame1823→1843. 기존 global clock contamination은 남아 있으며 [GQ1-regression-only.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/GQ1-regression-only.json)에 기록했다.

local target progression/regression 범위만 관찰했다. ADR-006A 전체 구현, PlayerGlobal authority, minimal closure, ownership/inventory canonicalization, Pipeline/Trade/Tax/Tactical Production 또는 all-mod 호환성은 인증하지 않는다. 과거 UI 수동 체크리스트의 완료 표시는 이번 semantic gate의 승인 근거가 아니다.

## 13. 결함별 Master 권고

| 기존 결함 | 권고 | 인정할 개선 | 남은 blocker |
|---|---|---|---|
| **QA-ENGINE-002** | **STILL FAILING** | explicit approval lifecycle, compare-fail export block, save Error/Exception 격리와 prior-file 보존 | self-baselining authority bypass, non-tick stale approval, saved-byte semantic/XML 손상 승인, promotion 전 binding 미재검사, unresolved clean graph |
| **QA-ENGINE-006** | **STILL FAILING** | 15개 실제 큰 변조를 검출하는 개선된 comparator. narrow fresh-process field/job/reservation 보존 | 누락 field 검사, 잘못된 fixture/oracle baseline, self-census를 trusted oracle로 사용, 실제 saved-byte proof 부재 |

두 결함은 개별로 판단했다. 002의 publication gate만 실패한 것을 근거로 모든 006 comparator 검출을 부정하지 않는다. 반대로 15/15 검출을 근거로 002 authority 또는 전체 006 graph를 닫지 않는다. 두 결함 모두 이번 독립 실패가 있으므로 closure 권고는 불가하다.

## 14. QA evidence limitations와 필요한 후속 수정

QA harness의 XML thing tag/XPath 및 실제 persisted `growth` field 접근을 바로잡는 과정에서 시험이 중단된 적이 있다. 실패한 QA harness 시도를 후보 실패 수에 넣지 않았다. 이전 유효 case 증거를 보존하고 case10부터 이어 실행했다. Observer/IL reader의 compile/encoding/path 문제도 QA 도구 수정으로만 처리했다. candidate 수정/재빌드는 없었다.

후속 후보는 다음을 만족해야 한다.

1. 정확한 primary source/binary/fixture/profile 및 E1 harness/results hash를 다시 제출할 것. 설치 옆 source와 published DLL lineage를 구분할 것.
2. 원본부터 독립 검증되는 positive graph를 만들고 BionicTongue part, plant/fire/condition/zone 값과 active reservation 설명을 실제 엔진 값으로 정정할 것. unresolved references를 승인된 범위로 설명하거나 고칠 것.
3. manifest nomination authority와 source/context/profile/revision/generation 계약을 실질적으로 gate에 연결할 것. 손상 결과의 self-census가 approval input으로 승격될 수 없어야 한다.
4. non-tick 변조와 승인 후 상태 변화가 stale approval로 publish되지 않도록 할 것. complete supported-field comparator와 실제 export 검증을 일치시킬 것.
5. staged artifact의 saved-byte semantic proof 및 전체 XML 완전성을 final promotion 전에 확인할 것. silent altered file와 truncation negative regression을 포함할 것.
6. post-save/pre-promotion binding/version proof와 기존 final 교체/실패 계약을 정리할 것. verified Error/Exception quarantine 및 real reload/map-switch 차단을 유지할 것.

QA-only source/binaries의 hash는 [qa-harness-manifest.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/qa-harness-manifest.json), candidate/profiles/export SHA는 [frozen-artifacts.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Evidence/frozen-artifacts.json)와 before/after manifests에 보존했다. QA가 실행한 Worker process는 모두 종료했고 추가 Observer 파일도 제거했다. Master ledger와 architecture state는 수정하지 않았다.

**최종 판정: FAIL. QA-ENGINE-002 / QA-ENGINE-006 모두 STILL FAILING 유지 권고.** 독립 보고서 제출 후 새 구현·수정·추가 PoC를 시작하지 않는다.
