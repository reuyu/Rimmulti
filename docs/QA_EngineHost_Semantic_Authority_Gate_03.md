# QA_EngineHost_Semantic_Authority_Gate_03

[QA REVIEW]

- Work Package: **WP-QA-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-03**
- Reviewer: GPT-6.1 Sol — Independent QA / Architecture Reviewer
- Target: exact frozen `POC_EngineHost_Semantic_Authority_Gate_03.md` candidate
- Final Verdict: **FAIL**
- QA-ENGINE-002 recommendation: **STILL FAILING**
- QA-ENGINE-006 recommendation: **STILL FAILING**
- Evidence date: 2026-10-03, Asia/Seoul
- Scope: **Pruned Target-Map Owner Context**. G-Q1, PlayerGlobal schema, material Production 및 final G-Q6는 변경하거나 종료하지 않는다. Master 상태를 변경하지 않는다.

## 1. 판정 근거

실제 native SaveGame이 정상 live 상태를 직렬화한 직후, candidate의 staged SHA 산출 전에 QA observer가 skill·hediff·holder 수량을 바꾼 세 경우가 모두 **STAGED_OK → ARTIFACT_APPROVED**에 도달했다. Unity Error/Exception을 만들지 않았고 live 값과 ticks는 유지했다. 잘못된 저장 바이트의 SHA를 최초 검증 SHA로 받아들여, 이후 동일 SHA 확인만으로 승인했다.

`ValidateStagedXml`은 XML 구조·일부 envelope 존재만 검사하며 `actualManifestHash = expectedManifestHash`를 반환한다. 실제 저장 바이트에서 supported semantic manifest를 추출하지도, fresh engine validator로 재로딩하지도 않는다. 따라서 Master가 지정한 승격 전 saved-byte semantic proof가 없다.

추가로 staging 없는 직접 승격, arbitrary grant/self-sealing, authority 교체 후 남는 실행 권한, ResultEpoch fence 누락을 재현했다. 반면 15개 잘못된 input의 초기 admission 차단, legacy self-approval 제거, 전체 수집 manifest 해싱, same-tick live recensus, XML EOF/DTD 차단은 실제 개선으로 인정한다.

## 2. 실행 방법과 무결성 범위

후보 Production/PoC 소스·DLL·fixture는 수정하거나 재빌드하지 않았다. 별도 QA observer와 IL 분석 도구만 빌드했다. 기존 QA ProbeMod에 observer DLL을 잠시 추가했으며 작업 종료 후 제거했다. 기존 활성 mod 순서를 그대로 복사한 독립 savedata profile에서 실제 RimWorld Win64 프로세스를 실행했다. GUI 검증을 요구하는 작업이 아니므로 화면 제어 없이 native engine / terminal protocol로 검사했다.

Observer는 기본적으로 읽기 전용이다. 명시적으로 ARM/MUTATE/ARM_FIELD를 요청한 경우에만 QA fault를 적용했다. saved-byte fault는 native SaveGame postfix에서 수행되어 **candidate가 SHA를 잡기 전**이라는 경계를 보장한다. candidate 응답·조건식·promotion 로직을 패치하지 않았다. per-field fault는 반환 census의 한 필드만 바꾸는 synthetic gate test이며, 별도의 native 객체 same-tick mutation과 구분한다.

QA 보조 도구의 첫 supplement 실행에서 pretty JSON에 포함된 newline이 line protocol을 깨뜨렸다. 이는 QA orchestration 오류이며 후보 결함으로 세지 않았다. 원래 로그를 보존하고 compact JSON으로 고친 QA 스크립트를 새 profile/PID에서 재실행하여 남은 검사까지 완료했다. IL 도구에는 미사용 변수 경고 1개가 있었으며 후보 build 경고로 해석하지 않는다.

### 2.1 Freeze

| 범위 | Before 파일 수 | 최종 차이 | 의미 |
| --- | --- | --- | --- |
| exact candidate / fixtures / dependency / developer profiles | 294 | 0 | target freeze 유지 |
| WarEconomyMod 전체 별도 관찰 | 353 | 18 | Server subtree 변경 관측; 아래 한계 명시 |

**Production 전체가 불변이었다고 인증하지 않는다.** 별도 관찰에서 Server 소스 5개와 Server build 산출물 13개가 달라졌다. QA 호출은 이 파일들을 수정/빌드하지 않았으며 변경 주체는 이 audit에서 확인하지 않았다. 변경 목록과 before/after hash는 보존했다. 이 E2에는 Server DLL을 로드하지 않았고, 실제 로드한 WorkerBridge·Engine·Client/Common·profile/fixture 및 294개 exact candidate 파일은 unchanged였다. 따라서 이 보고서는 해당 Engine Host candidate에만 유효하고, 변경된 Server/Pipeline 후보의 인증에는 사용할 수 없다.

Freeze 원본: [candidate-before.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/candidate-before.json), [candidate-after.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/candidate-after.json), [production-before.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/production-before.json), [production-after.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/production-after.json).

### 2.2 Exact binary/source provenance

| Artifact | Bytes | Verified SHA-256 |
| --- | --- | --- |
| RimWorldWin64.exe | 666624 | `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D` |
| Assembly-CSharp.dll | 15777280 | `5CF1B5BE399D5B1C9C56CA72C9D35B4ECF307FEACF5859D04AC5A1AA5926356A` |
| installed WorkerBridge DLL | 104960 | `A95B324EC7DA26155ACF75E64D5B122CF987903157A24C984AAE05D4EE7972CC` |
| reported WorkerBridge DLL | 104960 | `A95B324EC7DA26155ACF75E64D5B122CF987903157A24C984AAE05D4EE7972CC` |
| WorkerBridge.cs | 77410 | `E6DA162AC188818DA7C0BA57E840764C581B7D1D696CC6E2163F6C53B0948BDD` |
| EngineHostCensus.cs | 55179 | `98B487574BBA45081135A32E67325F33B6DAC97560B5914B151A3F4BFB073EAC` |
| WorkerBridge PDB | 25960 | `7EA23F16404008F9E7209A3F8F9FCE1FC251BE41BE338D9F5C43653822095881` |
| clean full source | 25896703 | `BCDEA94EFEE63A609EA6652B24B8913CD8C74A5ABB1A36489D386E892FC44FC4` |
| clean ContextB | 14015618 | `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B` |
| A harness | 49376 | `B2A3B3FC8D89DC90409652BB6A644EFAACFC6D6726E503954226F48213D03AE8` |
| A results | 32141 | `C1D728BDD9766C07DDB3DFD51E4A5504FB590493A335FAF31F44549BBB49FEDB` |
| A active ModsConfig | 753 | `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C` |
| A promoted output | 14041726 | `1B5471D89E889E283A828F3C6366F84DAA63152AB9DB6FC6B819C3098FD45F0F` |
| B promoted output | 14043493 | `F90A4E3032BDCBE12A2F84955037FAC5FCB25D291C197E8B4386EEAE1D460EC6` |

**A report의 provenance 불일치:** report가 제시한 harness SHA는 `BD18CD7AE12D4C614E3F786C557F8BDC87EAFBDE1D4BDEAA84BD36F8B2E0CF08`, results SHA는 `C0BD59DE964098937AE6E52D963F9E1EF67000B039A208D1F7730DEE9BFDEAC1`이다. QA 시작 시 원본과 Frozen copy의 실제 hash는 위 표의 `B2A3…03AE8` 및 `C1D7…9FEDB`였고 종료까지 unchanged였다. 따라서 A harness/results를 report의 exact hashed evidence와 일치한다고 인증하지 않는다. 직접 검사한 expected WorkerBridge DLL, source/PDB, 엔진 및 A/B promoted artifacts는 report와 일치한다. 독립 QA는 이 확인된 code/binary와 새 QA harness에 근거한다.

RimWorld **1.6.4871 rev591**, Unity **2022.3.35f1**. Runtime-loaded `Assembly-CSharp` MVID: `61e41735-6189-4da4-9d21-0260257b5097`; WorkerBridge MVID: `5ea0cf12-3e06-44e2-966a-87f320133bde`. Runtime WorkerBridge loaded path:

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll`

actual loaded assembly SHA도 expected `A95B…972CC`와 일치했다. reported source와 installed source 두 파일도 일치한다. Portable PDB CodeView/PDB GUID는 모두 `a2a1023e-afa0-4cf4-938a-86250de6dbf2`; 두 핵심 source와 generated assembly metadata를 포함한 4/4 document checksum이 실제 source와 일치한다. 재빌드 없이 PDB와 compiled IL 및 runtime으로 lineage를 확인했다.

증거: [pdb-provenance.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/pdb-provenance.json), [candidate-gate-il.txt](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/candidate-gate-il.txt), [engine-paths-il.txt](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/engine-paths-il.txt), [IndependentAuthority-metadata.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/IndependentAuthority-metadata.json), [independent-runtime-and-clean-graph.snapshot.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/independent-runtime-and-clean-graph.snapshot.json).

### 2.3 Active profile / process topology

동일한 10개 mod 순서: `brrainz.harmony` → Core → Royalty → Ideology → Biotech → Anomaly → Odyssey → `wareconomy.hybridmultiplayer` → `wareconomy.workerbridge.poc` → `qacodex.engine02.probe`. QA observer는 마지막 mod의 추가 assembly이며 새로운 11번째 mod가 아니다. Harmony runtime 2.2.2.0 및 전체 실제 mod/assembly 경로·SHA/MVID는 metadata에 기록했다.

모든 QA ModsConfig SHA: `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C`. `PROFILE-SETTLEMENT-B`는 bundle의 문자열 값이며 실제 profile fingerprint를 검증한 결과가 아니다.

| Process/profile | PID | 용도 |
| --- | --- | --- |
| IndependentAuthority | 14304 | independent native engine, loopback bridge/observer |
| AuthorityAttacks | 28972 | independent native engine, loopback bridge/observer |
| AuthorityAttacksRetry | 25544 | independent native engine, loopback bridge/observer |
| IndependentChainA | 32612 | independent native engine, loopback bridge/observer |
| IndependentChainB | 30636 | independent native engine, loopback bridge/observer |
| IndependentChainC | 10348 | independent native engine, loopback bridge/observer |
| FreshReplacement | 31128 | independent native engine, loopback bridge/observer |

실행 인자는 각 launch record에 보존했다. 각 프로세스는 `-batchmode`, 독립 `-savedatafolder`, 별도 log/bridge/observer port를 사용했다. 완료한 QA 프로세스만 종료했고 observer를 제거했다. 21개 사용 port가 모두 재바인드 가능했다. final integrity JSON에 cleanup 결과가 있다.

## 3. Trusted input admission — 15개 독립 persistent corruption

QA가 clean fixture의 복사본을 직접 변형했다. wrong file의 source SHA는 bundle에 정확히 넣고 semantic expected hash는 clean 값 `98F7817C57C57D05C43BABEC5B3A110163EED48A1B8878F4A135EBECDFF1423A`로 유지하여 source-byte mismatch와 semantic mismatch를 구분했다.

모두 engine READY에는 진입했지만 `INPUT_REJECTED`, `SimulationReady=false`였다. legacy `APPROVE_SEMANTIC` 및 current-state self-census 승인도 거절했다. STEP_TICKS / START_SIMULATION / SEAL_RESULT / STAGE_SAVE / EXPORT_SAVE / PROMOTE_STAGED를 각각 실제 호출했으며 최종 bypass artifact는 생성되지 않았다. 이것은 **최초 untrusted input admission의 개선**이며, 이미 승인된 상태에서 authority를 교체하는 §4와는 다른 결과다.

| Case | Dimension | Expected native | Injected persisted input | Final native | Admission / final |
| --- | --- | --- | --- | --- | --- |
| 01 | held stack | 5 | 4 | 4 | REJECTED / absent |
| 02 | Shooting skill | 10 | 15 | 15 | REJECTED / absent |
| 03 | Stab severity | 3.0 | 1 | 1.0 | REJECTED / absent |
| 04 | BionicTongue existence | true | removed | false | REJECTED / absent |
| 05 | animal master/follow | ["Human302", true, true] | master removed / false / false | ["", false, false] | REJECTED / absent |
| 06 | bill targetCount | 10 | 25 | 25 | REJECTED / absent |
| 07 | Growing zone cell | ["(139, 0, 145)"] | (139,0,146) | ["(139, 0, 146)"] | REJECTED / absent |
| 08 | Mine target | ["(150, 0, 150)"] | (150,0,151) | ["(150, 0, 151)"] | REJECTED / absent |
| 09 | fire size | 0.45 | 0.90 | 0.9 | REJECTED / absent |
| 10 | plant growth | 0.5 | 0.40 | 0.4 | REJECTED / absent |
| 11 | Aurora duration | 60000 | 12000 | 12000 | REJECTED / absent |
| 12 | assigned bed | "Bed990012" | assignment removed | "" | REJECTED / absent |
| 13 | external relation | "Spouse" | ExSpouse | "ExSpouse" | REJECTED / absent |
| 14 | battery stored energy | 600.0 | 200 | 200.0 | REJECTED / absent |
| 15 | nested holder Def | "Stool" | WoodLog | "WoodLog" | REJECTED / absent |

모든 injected input 원본/SHA, final live census, 개별 command 응답: [independent-negative-summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/independent-negative-summary.json), [results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/results.json).

## 4. AuthorityBundle / simulation grant

실제 AuthorityBundle 필드: `authorityId`, `expectedSourceArtifactHash`, `manifestVersion`, `expectedManifestHash`, `contentProfileFingerprint`, `targetMapId`, `workerGeneration`, `allowedOperationMode`, `expectedSourceSha`.

`REGISTER_AUTHORITY`는 path가 아닌 **inline JSON**을 받는다. 파일 내용 변경만으로 등록 객체가 바뀌지는 않는다. 그러나 같은 파일의 변경된 JSON을 같은 authorityId로 다시 등록하면 기존 bundle을 덮어쓴다. immutable registry / immutable ID binding은 구현되어 있지 않다.

| Attack | Observed | Assessment |
| --- | --- | --- |
| wrong source SHA before LOAD | LOAD_REJECTED; old identical bundle + different source bytes도 차단 | PASS, pre-load 경계에 한정 |
| wrong source SHA registered AFTER loaded READY | INPUT_VALIDATED → STEP accepted → RESULT_SEALED | FAIL: 재등록/검증이 실제 loaded source에 binding하지 않음 |
| expectedSourceSha alias only / primary source hash blank | INPUT_VALIDATED; alias ignored | source SHA 선택적·alias 무효 |
| wrong ContentProfileFingerprint | NOT-THE-ACTIVE-PROFILE 승인 후 STEP/SEAL accepted | FAIL: 계산/대조 없이 metadata 복사 |
| allowedOperationMode = READ_ONLY | INPUT_VALIDATED; STEP 1 수행; SEAL accepted | FAIL: permission mode 미적용 |
| stale generation in newly loaded untrusted state | VALIDATE_INPUT generation error; admission 없음 | PASS for fresh untrusted state |
| wrong generation AFTER previously validated state | VALIDATE_INPUT error but trustedSimulationReady=true; STEP accepted; SEAL rejects generation | FAIL: readiness revocation 누락 |
| wrong targetMapId AFTER validated state | VALIDATE_INPUT map error but STEP accepted AND SEAL accepted | FAIL: seal에서 authority target map 대조도 누락 |
| wrong manifestVersion | REGISTER rejected; 이전 valid authority 유지 | PASS: invalid bundle 수락으로 해석하지 않음 |
| wrong expectedManifestHash | INPUT_REJECTED; trusted=false; STEP/SEAL blocked | PASS |
| same AuthorityId with changed bytes / new generation | REGISTER overwrites; genrepaired reuse validated | FAIL relative to immutable/replay-bound authority claim |
| bundle file replaced without REGISTER | cached authority unchanged; original binding validated | PASS: no file-path re-read surface |
| contextId/scopeId/profileIdentifier/storeIncarnationId/baseArtifactRevision | unknown JSON fields discarded; clean hash input accepted | NOT IMPLEMENTED, lineage validation 없음 |
| arbitrary/stale-labelled/foreign-labelled grant | all RESULT_SEALED; blank auto-generates grant | FAIL: no pre-registered authorized grant model |
| duplicate SEAL_RESULT label | new epoch/result accepted | not idempotent or permission-bound |

`targetMapId`는 현재 구현에서 Map.Index와 비교된다. canonical context identity나 안정적인 scope identity를 인증하는 것과 같지 않다. `expectedSourceSha`는 사용되지 않는 별도 필드다. source/profile/context/store/base revision을 암묵적으로 directory 또는 문자열이 보장한다고 추론하지 않았다.

Grant 검사는 존재하지 않는다. 테스트의 “stale/foreign grant”는 과거 label 또는 다른 authority를 뜻하는 임의 label이다. 실제 authorized grant record가 없으므로 genuine cross-authority registered grant validation을 인증할 수 없다. **localhost control protocol에 접속한 QA가 control plane 역할을 수행한 검사**이며, normal gameplay client 또는 Production authentication 취약점의 재현이라고 주장하지 않는다.

추가 native 재현: clean admission 후 STEP 없이 Shooting 10→15를 같은 tick에서 변경하고 `SEAL_RESULT UNREGISTERED-AFTER-DIRECT-MUTATION` 호출. 변경된 자체 live census 해시 `504EDD5F…`로 봉인됐으며 STAGE_SAVE와 normal promotion이 모두 통과해 skill15 artifact가 생겼다. legacy self-approval은 제거됐지만 **권한 없는 grant를 통한 결과 self-baselining**은 남아 있다.

위치: [REGISTER overwrite](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:979), [ValidateInput early-return / readiness](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1093), [SealResult grant label](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1284), [AuthorityBundle schema](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:15).

## 5. Closed manifest — 지원 필드와 실제 gate

`ComputeManifestHash`가 `ToJson()` 전체를 SHA-256으로 해싱한다. 기존 수집 필드 중 hash에서 빠졌던 followFieldwork, plant age, bill suspended/settings, hediff part/loadID는 포함된다.

| Declared record | Fields |
| --- | --- |
| ContainerRecord | `containerId`, `containerType`, `items` |
| ContainedItemRecord | `id`, `def`, `count`, `stuff`, `quality`, `hp` |
| HediffRecordV3 | `def`, `part`, `partIndex`, `severity`, `loadID` |
| RelationRecordV3 | `relationDef`, `otherPawnId` |
| PawnRecord | `id`, `name`, `faction`, `isColonist`, `assignedBed`, `curJob`, `skills`, `hediffs`, `equipment`, `apparel`, `inventory`, `relations` |
| AnimalRecord | `id`, `def`, `faction`, `master`, `followDrafted`, `followFieldwork` |
| BillRecordV3 | `recipe`, `repeatMode`, `repeatCount`, `targetCount`, `suspended`, `allowedSkillRange`, `allowedDefs` |
| BuildingRecord | `id`, `def`, `stuff`, `hp`, `power`, `batteryStoredEnergy`, `assignedPawns`, `bills` |
| ZoneRecord | `id`, `label`, `type`, `cells`, `plantDefToGrow` |
| DesignationRecord | `def`, `target` |
| ConditionRecord | `def`, `id`, `duration`, `ticksPassed` |
| FireRecordV3 | `id`, `pos`, `fireSize`, `ticksSinceSpawn` |
| PlantRecordV3 | `id`, `def`, `pos`, `growth`, `age` |
| ReservationRecord | `claimant`, `job`, `target`, `maxPawns`, `stackCount` |
| GlobalDependencyRecord | `playerFaction`, `factionsReferenced`, `worldObjectsReferenced`, `defsReferenced` |
| CensusManifestData | `manifestVersion`, `manifestSchema`, `unclassifiedScopePolicy`, `mapIndex`, `mapTile`, `parentWorldObject`, `playerFaction`, `ticksGame`, `entityCount`, `entityIdSet`, `defCounts`, `classCounts`, `stackTotals`, `containerHierarchy`, `pawns`, `animals`, `buildings`, `zones`, `designations`, `conditions`, `fires`, `plants`, `reservations`, `globalDependencies` |

clean graph의 **97개 대표 scalar/element field path**를 하나씩 변형했다. 모두 canonical hash가 변했고, 실제 STAGE_SAVE post-seal recensus에서 **97/97 차단**됐다. active Goto/reservation graph를 QA가 실제 native API로 만들고 추가 **5/5 reservation field**를 변형했으며 모두 hash change + stage rejection이었다. 합계 **102/102 수집 leaf 대표 경로**. 모든 leaf 값/경로와 비교 결과는 JSON으로 보존했다. list cardinality/전체 record도 JSON에 포함됨은 source/IL로 확인했으나 모든 entity instance·조합·빈 collection cardinality를 exhaustive runtime mutation했다고 주장하지 않는다.

`CompareCensus` helper는 97개 중 **63개**에 대해 hash가 달라져도 `isPass=true`였다. 실제 input/stage gate는 전체 hash를 쓰므로 이 63건을 현 candidate gate 우회라고 분류하지 않는다. 그러나 이 helper PASS를 full equality 또는 향후 saved-byte validator의 성공 기준으로 사용하면 부족하다.

**명시적 범위 한계:** Pawn.curJob와 Reservation.job는 JobDef 이름만 수집한다. Job unique ID, current job targetA/targetB/queue/driver state를 포함하지 않는다. native Goto target을 `(140,0,148)`에서 `(139,0,143)`으로 바꾸되 reservation target은 유지한 테스트에서 census 전체가 동일했다. 별도 observer는 예약 job ID `Job_200000`을 보았으나 canonical manifest에는 `Goto`만 들어간다. 따라서 active job identity/target 보존을 인증하지 않는다. 현재 선언된 reservation claimant/Def/target/maxPawns/stackCount 검증과 full active job semantics를 구분한다. 상세 bill은 나열된 필드만, power는 수집 scalar만, hediff는 나열된 Def/part/severity/loadID만 해당한다. all-mod component / 완전한 map semantics가 아니다.

증거: [declared-field-matrix.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/declared-field-matrix.json), [declared-field-gates.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/declared-field-gates.json), [job-field-matrix.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/job-field-matrix.json), `results.json: reservation-field-gates / job-target-scope`. 구현: [full manifest hash](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:258).

## 6. Same-tick native mutation / promotion fences

native 객체 12개 mutation: skill, hediff severity, holder count, zone cell, designation, relation, bed ownership, followFieldwork, plant age, bill suspended, hediff part, hediff loadID. 모두 beforeTicks=afterTicks=1823이며 seal 후 STAGE_SAVE가 차단됐다. zone native mutation은 ID1 Stockpile의 cell 제거이며 persistent input case07은 Growing zone cell 변경으로 두 검사를 구분한다.

| After stage attack | Native result | Verdict |
| --- | --- | --- |
| live skill mutation | PROMOTION_BLOCKED | BLOCKED |
| Worker generation change | PROMOTION_BLOCKED | BLOCKED |
| currentResultEpoch increment | ARTIFACT_APPROVED | FAIL — approved |
| staged-file byte change | PROMOTION_BLOCKED | BLOCKED |
| protocol SEAL_RESULT again/new epoch | ARTIFACT_APPROVED | FAIL — approved |

epoch direct injection과 실제 protocol reseal을 분리했다. 실제 reseal 테스트는 epoch19에서 staging한 바이트를 epoch20/new grant로 재봉인한 뒤, 새 staging validation 없이 normal promotion해 `ARTIFACT_APPROVED … Epoch=20`에 도달했다. currentResultEpoch와 staged approval tuple을 대조하는 fence가 없다. byte change와 generation reject가 이를 보완하지 못한다.

## 7. 최고 우선순위 saved-byte semantic attack

sealed live clean hash는 세 경우 모두 `98F7817C…`. native 저장을 완료한 뒤 staged file의 field만 수정했으며 ticks1823, live Shooting10, Stab3, held count5를 그대로 확인했다. 잘못된 file의 SHA를 candidate가 이후에 수집했다. Unity Error/Exception을 주입하지 않았다.

| Supported field | Live/expected | Saved wrong value | Stage | Normal promotion | Altered staged / final SHA |
| --- | --- | --- | --- | --- | --- |
| Shooting | 10 | 15 | STAGED_OK | ARTIFACT_APPROVED | `D46914E255AA45E42435DB55D501F9B29736A2637DDDD19CDB8267AA6752D90B` |
| Stab severity | 3 | 1 | STAGED_OK | ARTIFACT_APPROVED | `EB67BC52EAFFD3E23B38EA97DD7CC14B456C4DA5F27BEEBDED4BDA12CFDEE80A` |
| held item count | 5 | 4 | STAGED_OK | ARTIFACT_APPROVED | `E6463AA1E1D65CD27834202CD6F5F393F2D584C24DDB72654208EB6CFF3F2032` |

세 altered SHA는 실제 promoted artifact SHA와 일치한다. staging 출력의 ManifestHash는 sealed expected hash였지만 저장 바이트의 의미에서 계산한 값이 아니었다. structural XML은 유효했으므로 envelope validator를 통과했다. 이는 **진짜 bad bytes publication**이며, 단순한 코드 추정이나 promotion 이후 파일 편집이 아니다.

Observer 경계 구현: [native SaveGame postfix](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Observer/Mutations.cs:33). candidate 경계: [native save](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1390) → [ValidateStagedXml](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1416) → [staged SHA](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1425). 핵심 원인: [expected hash copied as actual](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs:1180).

## 8. Stage 없는 직접 promotion

새 Worker에서 clean admission → seal만 수행한 뒤, 별도의 wrong-skill input 복사본을 `NotStaged.rws`로 두었다. STAGE_SAVE를 한 번도 호출하지 않고 `PROMOTE_STAGED NotStaged DirectWithoutStaging`를 호출했다. **ARTIFACT_APPROVED**, final Shooting15. INTERNAL에서 lastStagedPath 및 lastStagedSha가 둘 다 빈 문자열인 것을 확인했다.

원인: promotion이 STAGED_VALIDATED뿐 아니라 RESULT_SEALED도 허용하며, 저장된 staged SHA가 비어 있으면 비교를 생략한다. caller path를 lastStagedPath와도 비교하지 않는다. staging·structural validation·semantic validation 전체를 건너뛴다.

위치: [RESULT_SEALED accepted](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1447), [caller-chosen staging path](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1452), [optional staged SHA check](C:/Users/user/Desktop/RimMulti/scratch/WorkerBridgeMod/Source/WorkerBridge.cs:1493). 증거: `results.json: DirectWithoutStaging-promote / DirectWithoutStaging-output / no-stage-internal`.

## 9. XML structure, save errors, replacement safety

| Boundary attack | Observed | Result |
| --- | --- | --- |
| native-save postfix: malformed EOF | STAGE_FAILED; quarantine; no final approved output | PASS |
| native-save postfix: second root / trailing structure | STAGE_FAILED; quarantine; no final approved output | PASS |
| native-save postfix: DTD/entity declaration | DtdProcessing.Prohibit rejects before STAGED_VALIDATED | PASS |
| native save-time Unity Error | STAGE_FAILED Errors=1; quarantine; prior final unchanged | PASS |
| native save-time thrown IOException | STAGE_FAILED; quarantine; prior final unchanged | PASS |
| lock existing approved final with exclusive FileShare.None | PROMOTION_FAILED; previous SHA unchanged; staging retained | PASS failure preservation |
| replacement retry after lock released | Access denied; previous final unchanged; backup absent | normal replacement NOT VERIFIED |
| fresh independent worker, normal replacement with no lock injection | Access denied; prior unchanged; staging retained | normal replacement NOT VERIFIED |
| independent PowerShell/.NET File.Replace on tiny QA files | same Access denied | environment-wide limitation, do not attribute solely to candidate |

previous approved output safety를 실제 SHA로 확인했다. recovery retry는 새 admission/seal/stage 후 실행했다. candidate는 성공 경로에 `.bak.rws`를 만들도록 구현하지만 이 환경에서 정상 File.Replace 자체가 실패해 성공적인 backup creation/recovery를 인증하지 못했다. engine IL에서 FilePathForSavedGame은 filename에 `.rws`를 추가함을 확인했으며 filename 충돌이라는 추정으로 보고하지 않는다. Production fix를 임의로 제안하지 않고 deployment permission/filesystem 조건에서 정상 replacement 검증이 필요하다고 기록한다. 기존 final 보존 실패는 재현되지 않았다. candidate 전체 semantic gate FAIL의 근거는 이 환경 제한과 무관한 §7/8이다.

증거: `results.json: replacement-failure-safety / replacement-backup / fresh-normal-replacement / native-save-error-error / native-save-error-throw`, [windows-replace-control.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/windows-replace-control.json).

## 10. Fresh pre-promotion validator와 A→B→C

**candidate에는 승격 전 fresh validator가 없다.** registration / seal / stage / promote compiled path가 native save → static XML envelope → SHA → move/replace를 수행한다. fresh validation Worker/PID/profile/input SHA/expected sealed-manifest comparison receipt를 만들거나 소비하는 단계가 없다. validation 기대 hash를 독립적으로 계산하지 않고 그대로 돌려준다. 따라서 validator PID/result는 **NONE**, 검증한 staged semantic SHA는 **없음**이다.

독립 A/B/C를 추가 실행했다. A clean input에서100ticks, B A-output에서100ticks, C B-output을 fresh process에서 로드했다. B loaded hash=A sealed hash, C loaded hash=B sealed hash였다. 서로 다른 실행의 RNG/변동으로 developer의 post-tick hash와 QA post-tick hash가 반드시 같다고 요구하지 않았으며 deterministic simulation을 인증하지 않는다.

| Process | PID | Source SHA | Authority / gen / epoch / grant | Sealed or loaded manifest | Staged / promoted SHA | Pre-promotion semantic validator |
| --- | --- | --- | --- | --- | --- | --- |
| A | 32612 | `EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B` | ChainInputA / 1 / 1 / UNREGISTERED-CHAIN-A | `95935EFCF9F6E38BBFBCE9034BE1A7F81DC5F73EBF7723DFAC85B5B70DFBBC93` | `F46BE2AD779CC1F9056DB572892CAA4E85A91C9752ED006A49DF60CC0BEFC904` / `F46BE2AD779CC1F9056DB572892CAA4E85A91C9752ED006A49DF60CC0BEFC904` | NONE; not valid authority publication |
| B | 30636 | `F46BE2AD779CC1F9056DB572892CAA4E85A91C9752ED006A49DF60CC0BEFC904` | ChainInputB / 1 / 1 / UNREGISTERED-CHAIN-B | `40266EED065791B46C0FA72C6D8441052AE52ADB0F5BC1F4B78681F135804EEB` | `3CCDEA158EC378C3D5EF84F160249593276E3DF16B8BD184067B970C08AF2F8A` / `3CCDEA158EC378C3D5EF84F160249593276E3DF16B8BD184067B970C08AF2F8A` | NONE; not valid authority publication |
| C | 10348 | `3CCDEA158EC378C3D5EF84F160249593276E3DF16B8BD184067B970C08AF2F8A` | ChainInputC / 1 / n/a / n/a | `40266EED065791B46C0FA72C6D8441052AE52ADB0F5BC1F4B78681F135804EEB` | `n/a` / `n/a` | NONE; not valid authority publication |

ContentProfile은 A/B bundle의 `PROFILE-SETTLEMENT-B`이며 실제 ModsConfig SHA는 §2.3에 기록했다. C도 동일 실제 profile에서 `ChainInputC`를 등록했다. 전체 source/profile/seal/epoch/staged/final 정보는 independent-chain.json에 있다. A/B stage/promote 성공을 authority gate의 유효한 승격으로 인정하지 않는다. C는 승격 후 transport regression이며 필수 승격 전 validator를 대신하지 못한다. 기대 sealed hash는 QA harness가 다음 프로세스로 전달했으므로 외부 durable canonical authority source를 증명한 것도 아니다.

증거: [independent-chain.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/independent-chain.json), [positive-chain.log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/positive-chain.log).

## 11. Findings / required candidate changes

아래 G03 번호는 이 보고서 안의 finding 식별자다. 공식 QDL 번호를 임의로 만들지 않고 기존 QA-ENGINE-002/006에 연결한다.

### G03-01 — supported wrong saved bytes promoted

- Severity: **Critical** — authority gate가 잘못된 persisted state를 approved outcome으로 공개한다.
- Mapping: QA-ENGINE-002 / QA-ENGINE-006; Work Order §7/9/11
- Reproduction / Expected / Actual: §7의 3건. sealed ResultManifest에 대한 exact staged bytes의 fresh semantic validation이 필요하지만 XML envelope와 잘못된 SHA capture만으로 승인됐다.
- Root cause: EngineHostCensus.cs:1180; WorkerBridge.cs:1416/1434。
- Required fix: 승격 전에 exact staged SHA를 fresh engine validator에 전달하고, 기대값을 sealed ResultManifest에서 받아 실제 로드된 supported manifest와 완전히 비교한다. source/context/profile/generation/epoch/grant와 validation receipt를 결합하고 candidate/staged self-census를 기대 authority로 쓰지 않는다.

### G03-02 — staging-less promotion bypass

- Severity: **Critical**; Mapping: QA-ENGINE-002/006; Work Order §2/7/10
- Location: WorkerBridge.cs:1447/1452/1493。
- Reproduction: §8. stage 미실행·wrong skill file·empty lastStagedSha 상태에서 승인됐다.
- Required fix: 성공한 stage-validation receipt를 필수로 요구하고 path/exactSHA/sealedResult/generation/epoch에 binding한다. RESULT_SEALED 또는 빈 SHA만으로 승격하지 않는다. caller가 지정한 path를 authority proof로 쓰지 않는다.

### G03-03 — arbitrary grants / wrong operation mode / result self-baselining

- Severity: **High**; Mapping: QA-ENGINE-002/006; Work Order §4
- Location: EngineHostCensus.cs:15; WorkerBridge.cs:1256/1287。
- Reproduction: unregistered/stale-labelled/foreign-labelled/blank grant 모두 seal됐다. READ_ONLY에서 step/seal이 가능했고 direct native skill change → arbitrary self-seal → approved가 재현됐다.
- Required fix: control-plane authorized grant registry/receipt에 AuthorityId·scope/context·generation·operation permission·execution/result lineage를 binding하고 unknown/stale/foreign grant를 거절한다. seal이 label 입력만으로 simulation outcome의 정당성을 선언해서는 안 된다.

### G03-04 — mutable authority and stale readiness

- Severity: **High**; Mapping: QA-ENGINE-002; Work Order §3
- Location: WorkerBridge.cs:979/1035/1093/1099; AuthorityBundle schema。
- Reproduction: registry overwrite, 로드 이후 wrong source/profile 수락, wrong gen/map validation error 이후에도 STEP 허용. wrong map에서는 SEAL도 허용됐다.
- Required fix: loaded artifact provenance와 실제 profile/context를 immutable authority binding에 포함한다. authority 변경 및 모든 validation 실패 경로에서 readiness/seal/staging approval을 무효화하며 STEP/SEAL/PROMOTE에서도 current authority를 검사한다. 누락된 scope/store/base lineage를 directory명으로 대체하지 않고 unused expectedSourceSha alias의 의미를 통일한다.

### G03-05 — ResultEpoch / staged-result binding missing

- Severity: **High**; Mapping: QA-ENGINE-002/006; Work Order §10
- Location: WorkerBridge.cs:1284/1432/1462/1493。
- Reproduction: private epoch increment 이후에도 승인됐고 native protocol reseal epoch19→20에서 old stage가 승인됐다.
- Required fix: staged receipt에 resultEpoch와 sealed authority/result identity를 고정하고 current epoch/result와 완전히 일치해야 한다. reseal에서 old staging validation을 무효화한다. 동일 live hash가 다른 grant/epoch를 대체하지 못하게 한다.

### G03-06 — comparator/helper and declared scope limitations

- Severity: **Medium**（helper equality誤解）; Mapping: QA-ENGINE-006 scope / test-evidence limitation。
- Location: EngineHostCensus.cs:673 (`CompareCensus`); PawnRecord / ReservationRecord / GenerateCensus job projection。
- Observation: 63/97 unequal hash test에서 helper는 PASS였다. 다만 current gate는 전체 hash를 사용하므로 실제 stage는 거절됐다. JobDef만으로 active job ID/target을 검증하지 못한다.
- Required fix: 개선된 current gate를 유지하고 future fresh validator가 partial helper만을 equality predicate로 사용하지 않게 한다. supported graph와 unsupported job/controller fields를 명시하고 scope 확장을 이미 인증한 것으로 주장하지 않는다.

정상 replacement 성공/backup의 환경 제한은 별도의 evidence limitation이며 G03-01..05의 semantic/authority 결함을 대신하지 않는다.

## 12. A report reconciliation / defect disposition

| A claim | Independent conclusion |
| --- | --- |
| legacy candidate self-approval removed | CONFIRMED: initial 15 invalid inputs + APPROVE_SEMANTIC blocked |
| immutable AuthorityBundle | NOT CONFIRMED: REGISTER overwrites; source/profile/context/mode binding incomplete |
| authoritative simulation grant | NOT CONFIRMED: arbitrary label accepted; direct mutation can self-seal |
| whole collected V3 semantic hash | CONFIRMED within declared projection: 102 representative leaf paths gated |
| same-tick recensus before stage/promote | CONFIRMED for tested native fields; does not validate saved bytes |
| saved-byte proof / definitive QA-ENGINE-002/006 closure | REJECT: three supported semantic corruptions promoted |
| generation, epoch, staged SHA reverified | generation + SHA observed; epoch binding FAIL |
| atomic replacement / backup preservation | forced failure preserved previous output; normal success/backup not proven in environment |
| A→B→C freshness closes authority | transport fidelity confirmed; C is post-promotion, not required validator |

| Existing defect | Recommendation | Reason |
| --- | --- | --- |
| QA-ENGINE-002 | **STILL FAILING** | initial admission improved; arbitrary grant/authority overwrite + wrong saved-byte publication persist |
| QA-ENGINE-006 | **STILL FAILING** | full collected hash improved; saved-byte semantic validator absent, direct stage bypass and epoch/result fence absent |

## 13. Evidence index / limits / final recommendation

- [results.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/results.json)
- [final-integrity-summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/final-integrity-summary.json)
- [independent-negative-summary.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/independent-negative-summary.json)
- [declared-field-matrix.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/declared-field-matrix.json)
- [declared-field-gates.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/declared-field-gates.json)
- [job-field-matrix.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/job-field-matrix.json)
- [independent-chain.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/independent-chain.json)
- [candidate-gate-il.txt](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/candidate-gate-il.txt)
- [pdb-provenance.json](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/pdb-provenance.json)
- [main-run.log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/main-run.log)
- [supplement-run.log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/supplement-run.log)
- [supplement-retry.log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/supplement-retry.log)
- [positive-chain.log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/positive-chain.log)
- [replacement-check.log](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003/Evidence/replacement-check.log)

개별 wrong final artifact·quarantine·injected input·profile 로그·full census는 같은 QA root의 Evidence/Profiles에 보관했다. evidence_manifest.json에 QA source/binary/evidence/fixture 출력의 exact hash를 기록했다(자기 자신 제외). 증거 파일을 삭제하거나 candidate에 덮어쓰지 않았다.

Engine startup에는 SteamAPI.Init failed와 hidden ritual precept 보완 메시지가 있었다. 초기 supported graph는 native READY·expected manifest hash 일치·read observer errors=[]를 확인했지만, 전체 mod/world/global state의 semantic clean 인증으로 확장하지 않는다. 알려진 global context 자동 보완이나 temporal contamination을 G-Q1/PlayerGlobal 해결로 해석하지 않는다. crash durability·network gameplay authentication·full-map/job-driver semantics·최종 Production engine authority 인증은 본 Work Order 밖이다.

**Master recommendation:** 이 candidate의 QA-ENGINE-002/006 closure를 승인하지 않을 것을 권고한다. 개선된 input admission/full collected hash/structural validation은 유지할 수 있으나, 필수 fresh staged-byte semantic validator·authorized grant/authority lineage·strict stage/epoch promotion binding을 갖춘 새로운 frozen candidate가 필요하다. Master의 기존 gate 상태를 변경하지 않는다.

**Final Verdict: FAIL.** 본 Work Order의 검증·보고를 종료하고 다음 지시를 기다린다.
