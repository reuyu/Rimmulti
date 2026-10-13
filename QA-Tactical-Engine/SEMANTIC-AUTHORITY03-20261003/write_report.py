import json,hashlib
from pathlib import Path
import setup as f
Q=f.Q;E=Q/'Evidence';R=f.R
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
r=read(E/'results.json');integrity=read(E/'final-integrity-summary.json');neg=read(E/'independent-negative-summary.json');chain=read(E/'independent-chain.json');matrix=read(E/'declared-field-matrix.json')
def link(p,label=None,line=None):
 p=Path(p).resolve();return '['+(label or p.name)+']('+p.as_posix()+(':'+str(line) if line else '')+')'
def txt(x):return json.dumps(x,ensure_ascii=False).replace('|','\\|')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(x).replace('\n',' ') for x in row)+' |' for row in rows)+'\n'
WB=R/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';CE=R/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
doc=r'''# QA_EngineHost_Semantic_Authority_Gate_03

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

'''
doc+=table(['범위','Before 파일 수','최종 차이','의미'],[
 ['exact candidate / fixtures / dependency / developer profiles',integrity['candidateFiles'],len(integrity['candidateChanges']),'target freeze 유지'],
 ['WarEconomyMod 전체 별도 관찰',integrity['productionFiles'],len(integrity['productionChanges']),'Server subtree 변경 관측; 아래 한계 명시']])
doc+='''
**Production 전체가 불변이었다고 인증하지 않는다.** 별도 관찰에서 Server 소스 5개와 Server build 산출물 13개가 달라졌다. QA 호출은 이 파일들을 수정/빌드하지 않았으며 변경 주체는 이 audit에서 확인하지 않았다. 변경 목록과 before/after hash는 보존했다. 이 E2에는 Server DLL을 로드하지 않았고, 실제 로드한 WorkerBridge·Engine·Client/Common·profile/fixture 및 294개 exact candidate 파일은 unchanged였다. 따라서 이 보고서는 해당 Engine Host candidate에만 유효하고, 변경된 Server/Pipeline 후보의 인증에는 사용할 수 없다.

'''
doc+='Freeze 원본: '+link(Q/'candidate-before.json')+', '+link(Q/'candidate-after.json')+', '+link(Q/'production-before.json')+', '+link(Q/'production-after.json')+'.\n\n'
doc+='''### 2.2 Exact binary/source provenance

'''
paths=[('RimWorldWin64.exe',f.ENGINE/'RimWorldWin64.exe'),('Assembly-CSharp.dll',f.ENGINE/'RimWorldWin64_Data/Managed/Assembly-CSharp.dll'),('installed WorkerBridge DLL',f.WB/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll'),('reported WorkerBridge DLL',Q/'Frozen/WarEconomy.WorkerBridge.PoC.dll'),('WorkerBridge.cs',Q/'Frozen/Reported-WorkerBridge.cs'),('EngineHostCensus.cs',Q/'Frozen/Reported-EngineHostCensus.cs'),('WorkerBridge PDB',Q/'Frozen/WarEconomy.WorkerBridge.PoC.pdb'),('clean full source',Q/'Frozen/CleanSettlementFixture.rws'),('clean ContextB',Q/'Frozen/TargetSettlement_Clean_ContextB.rws'),('A harness',Q/'Frozen/run_semantic_authority_gate_03.py'),('A results',Q/'Frozen/semantic_authority_gate_03_results.json'),('A active ModsConfig',Q/'Frozen/Developer-A/Config/ModsConfig.xml'),('A promoted output',Q/'Frozen/Developer-A/Saves/TargetSettlement_Promoted_A.rws'),('B promoted output',Q/'Frozen/Developer-B/Saves/TargetSettlement_Promoted_B.rws')]
doc+=table(['Artifact','Bytes','Verified SHA-256'],[[n,p.stat().st_size,'`'+f.sha(p)+'`'] for n,p in paths])
doc+=r'''
**A report의 provenance 불일치:** report가 제시한 harness SHA는 `BD18CD7AE12D4C614E3F786C557F8BDC87EAFBDE1D4BDEAA84BD36F8B2E0CF08`, results SHA는 `C0BD59DE964098937AE6E52D963F9E1EF67000B039A208D1F7730DEE9BFDEAC1`이다. QA 시작 시 원본과 Frozen copy의 실제 hash는 위 표의 `B2A3…03AE8` 및 `C1D7…9FEDB`였고 종료까지 unchanged였다. 따라서 A harness/results를 report의 exact hashed evidence와 일치한다고 인증하지 않는다. 직접 검사한 expected WorkerBridge DLL, source/PDB, 엔진 및 A/B promoted artifacts는 report와 일치한다. 독립 QA는 이 확인된 code/binary와 새 QA harness에 근거한다.

RimWorld **1.6.4871 rev591**, Unity **2022.3.35f1**. Runtime-loaded `Assembly-CSharp` MVID: `61e41735-6189-4da4-9d21-0260257b5097`; WorkerBridge MVID: `5ea0cf12-3e06-44e2-966a-87f320133bde`. Runtime WorkerBridge loaded path:

`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll`

actual loaded assembly SHA도 expected `A95B…972CC`와 일치했다. reported source와 installed source 두 파일도 일치한다. Portable PDB CodeView/PDB GUID는 모두 `a2a1023e-afa0-4cf4-938a-86250de6dbf2`; 두 핵심 source와 generated assembly metadata를 포함한 4/4 document checksum이 실제 source와 일치한다. 재빌드 없이 PDB와 compiled IL 및 runtime으로 lineage를 확인했다.

'''
doc+='증거: '+link(E/'pdb-provenance.json')+', '+link(E/'candidate-gate-il.txt')+', '+link(E/'engine-paths-il.txt')+', '+link(E/'IndependentAuthority-metadata.json')+', '+link(E/'independent-runtime-and-clean-graph.snapshot.json')+'.\n\n'
doc+='''### 2.3 Active profile / process topology

동일한 10개 mod 순서: `brrainz.harmony` → Core → Royalty → Ideology → Biotech → Anomaly → Odyssey → `wareconomy.hybridmultiplayer` → `wareconomy.workerbridge.poc` → `qacodex.engine02.probe`. QA observer는 마지막 mod의 추가 assembly이며 새로운 11번째 mod가 아니다. Harmony runtime 2.2.2.0 및 전체 실제 mod/assembly 경로·SHA/MVID는 metadata에 기록했다.

모든 QA ModsConfig SHA: `FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C`. `PROFILE-SETTLEMENT-B`는 bundle의 문자열 값이며 실제 profile fingerprint를 검증한 결과가 아니다.

'''
launches=[(k,v) for k,v in r.items() if k.endswith('-launch')]
doc+=table(['Process/profile','PID','용도'],[[k.removesuffix('-launch'),v['pid'],'independent native engine, loopback bridge/observer'] for k,v in launches])
doc+='''
실행 인자는 각 launch record에 보존했다. 각 프로세스는 `-batchmode`, 독립 `-savedatafolder`, 별도 log/bridge/observer port를 사용했다. 완료한 QA 프로세스만 종료했고 observer를 제거했다. 21개 사용 port가 모두 재바인드 가능했다. final integrity JSON에 cleanup 결과가 있다.

## 3. Trusted input admission — 15개 독립 persistent corruption

QA가 clean fixture의 복사본을 직접 변형했다. wrong file의 source SHA는 bundle에 정확히 넣고 semantic expected hash는 clean 값 `98F7817C57C57D05C43BABEC5B3A110163EED48A1B8878F4A135EBECDFF1423A`로 유지하여 source-byte mismatch와 semantic mismatch를 구분했다.

모두 engine READY에는 진입했지만 `INPUT_REJECTED`, `SimulationReady=false`였다. legacy `APPROVE_SEMANTIC` 및 current-state self-census 승인도 거절했다. STEP_TICKS / START_SIMULATION / SEAL_RESULT / STAGE_SAVE / EXPORT_SAVE / PROMOTE_STAGED를 각각 실제 호출했으며 최종 bypass artifact는 생성되지 않았다. 이것은 **최초 untrusted input admission의 개선**이며, 이미 승인된 상태에서 authority를 교체하는 §4와는 다른 결과다.

'''
names=['held stack','Shooting skill','Stab severity','BionicTongue existence','animal master/follow','bill targetCount','Growing zone cell','Mine target','fire size','plant growth','Aurora duration','assigned bed','external relation','battery stored energy','nested holder Def']
inject=['4','15','1','removed','master removed / false / false','25','(139,0,146)','(150,0,151)','0.90','0.40','12000','assignment removed','ExSpouse','200','WoodLog']
doc+=table(['Case','Dimension','Expected native','Injected persisted input','Final native','Admission / final'],[[x['case'],names[i],txt(x['expectedLiveValue']),inject[i],txt(x['finalLiveValue']),'REJECTED / absent'] for i,x in enumerate(neg)])
doc+='\n모든 injected input 원본/SHA, final live census, 개별 command 응답: '+link(E/'independent-negative-summary.json')+', '+link(E/'results.json')+'.\n\n'
doc+='''## 4. AuthorityBundle / simulation grant

실제 AuthorityBundle 필드: `authorityId`, `expectedSourceArtifactHash`, `manifestVersion`, `expectedManifestHash`, `contentProfileFingerprint`, `targetMapId`, `workerGeneration`, `allowedOperationMode`, `expectedSourceSha`.

`REGISTER_AUTHORITY`는 path가 아닌 **inline JSON**을 받는다. 파일 내용 변경만으로 등록 객체가 바뀌지는 않는다. 그러나 같은 파일의 변경된 JSON을 같은 authorityId로 다시 등록하면 기존 bundle을 덮어쓴다. immutable registry / immutable ID binding은 구현되어 있지 않다.

'''
doc+=table(['Attack','Observed','Assessment'],[
 ['wrong source SHA before LOAD','LOAD_REJECTED; old identical bundle + different source bytes도 차단','PASS, pre-load 경계에 한정'],
 ['wrong source SHA registered AFTER loaded READY','INPUT_VALIDATED → STEP accepted → RESULT_SEALED','FAIL: 재등록/검증이 실제 loaded source에 binding하지 않음'],
 ['expectedSourceSha alias only / primary source hash blank','INPUT_VALIDATED; alias ignored','source SHA 선택적·alias 무효'],
 ['wrong ContentProfileFingerprint','NOT-THE-ACTIVE-PROFILE 승인 후 STEP/SEAL accepted','FAIL: 계산/대조 없이 metadata 복사'],
 ['allowedOperationMode = READ_ONLY','INPUT_VALIDATED; STEP 1 수행; SEAL accepted','FAIL: permission mode 미적용'],
 ['stale generation in newly loaded untrusted state','VALIDATE_INPUT generation error; admission 없음','PASS for fresh untrusted state'],
 ['wrong generation AFTER previously validated state','VALIDATE_INPUT error but trustedSimulationReady=true; STEP accepted; SEAL rejects generation','FAIL: readiness revocation 누락'],
 ['wrong targetMapId AFTER validated state','VALIDATE_INPUT map error but STEP accepted AND SEAL accepted','FAIL: seal에서 authority target map 대조도 누락'],
 ['wrong manifestVersion','REGISTER rejected; 이전 valid authority 유지','PASS: invalid bundle 수락으로 해석하지 않음'],
 ['wrong expectedManifestHash','INPUT_REJECTED; trusted=false; STEP/SEAL blocked','PASS'],
 ['same AuthorityId with changed bytes / new generation','REGISTER overwrites; genrepaired reuse validated','FAIL relative to immutable/replay-bound authority claim'],
 ['bundle file replaced without REGISTER','cached authority unchanged; original binding validated','PASS: no file-path re-read surface'],
 ['contextId/scopeId/profileIdentifier/storeIncarnationId/baseArtifactRevision','unknown JSON fields discarded; clean hash input accepted','NOT IMPLEMENTED, lineage validation 없음'],
 ['arbitrary/stale-labelled/foreign-labelled grant','all RESULT_SEALED; blank auto-generates grant','FAIL: no pre-registered authorized grant model'],
 ['duplicate SEAL_RESULT label','new epoch/result accepted','not idempotent or permission-bound']])
doc+='''
`targetMapId`는 현재 구현에서 Map.Index와 비교된다. canonical context identity나 안정적인 scope identity를 인증하는 것과 같지 않다. `expectedSourceSha`는 사용되지 않는 별도 필드다. source/profile/context/store/base revision을 암묵적으로 directory 또는 문자열이 보장한다고 추론하지 않았다.

Grant 검사는 존재하지 않는다. 테스트의 “stale/foreign grant”는 과거 label 또는 다른 authority를 뜻하는 임의 label이다. 실제 authorized grant record가 없으므로 genuine cross-authority registered grant validation을 인증할 수 없다. **localhost control protocol에 접속한 QA가 control plane 역할을 수행한 검사**이며, normal gameplay client 또는 Production authentication 취약점의 재현이라고 주장하지 않는다.

추가 native 재현: clean admission 후 STEP 없이 Shooting 10→15를 같은 tick에서 변경하고 `SEAL_RESULT UNREGISTERED-AFTER-DIRECT-MUTATION` 호출. 변경된 자체 live census 해시 `504EDD5F…`로 봉인됐으며 STAGE_SAVE와 normal promotion이 모두 통과해 skill15 artifact가 생겼다. legacy self-approval은 제거됐지만 **권한 없는 grant를 통한 결과 self-baselining**은 남아 있다.

'''
doc+='위치: '+link(WB,'REGISTER overwrite',979)+', '+link(WB,'ValidateInput early-return / readiness',1093)+', '+link(WB,'SealResult grant label',1284)+', '+link(CE,'AuthorityBundle schema',15)+'.\n\n'
doc+='## 5. Closed manifest — 지원 필드와 실제 gate\n\n'
doc+='`ComputeManifestHash`가 `ToJson()` 전체를 SHA-256으로 해싱한다. 기존 수집 필드 중 hash에서 빠졌던 followFieldwork, plant age, bill suspended/settings, hediff part/loadID는 포함된다.\n\n'
schema=[]
for name,fields in matrix['fields'].items():
 if name in ['AuthorityBundle','ResultManifest']:continue
 schema.append([name,', '.join('`'+x['name']+'`' for x in fields)])
doc+=table(['Declared record','Fields'],schema)
doc+='''
clean graph의 **97개 대표 scalar/element field path**를 하나씩 변형했다. 모두 canonical hash가 변했고, 실제 STAGE_SAVE post-seal recensus에서 **97/97 차단**됐다. active Goto/reservation graph를 QA가 실제 native API로 만들고 추가 **5/5 reservation field**를 변형했으며 모두 hash change + stage rejection이었다. 합계 **102/102 수집 leaf 대표 경로**. 모든 leaf 값/경로와 비교 결과는 JSON으로 보존했다. list cardinality/전체 record도 JSON에 포함됨은 source/IL로 확인했으나 모든 entity instance·조합·빈 collection cardinality를 exhaustive runtime mutation했다고 주장하지 않는다.

`CompareCensus` helper는 97개 중 **63개**에 대해 hash가 달라져도 `isPass=true`였다. 실제 input/stage gate는 전체 hash를 쓰므로 이 63건을 현 candidate gate 우회라고 분류하지 않는다. 그러나 이 helper PASS를 full equality 또는 향후 saved-byte validator의 성공 기준으로 사용하면 부족하다.

**명시적 범위 한계:** Pawn.curJob와 Reservation.job는 JobDef 이름만 수집한다. Job unique ID, current job targetA/targetB/queue/driver state를 포함하지 않는다. native Goto target을 `(140,0,148)`에서 `(139,0,143)`으로 바꾸되 reservation target은 유지한 테스트에서 census 전체가 동일했다. 별도 observer는 예약 job ID `Job_200000`을 보았으나 canonical manifest에는 `Goto`만 들어간다. 따라서 active job identity/target 보존을 인증하지 않는다. 현재 선언된 reservation claimant/Def/target/maxPawns/stackCount 검증과 full active job semantics를 구분한다. 상세 bill은 나열된 필드만, power는 수집 scalar만, hediff는 나열된 Def/part/severity/loadID만 해당한다. all-mod component / 완전한 map semantics가 아니다.

'''
doc+='증거: '+link(E/'declared-field-matrix.json')+', '+link(E/'declared-field-gates.json')+', '+link(E/'job-field-matrix.json')+', `results.json: reservation-field-gates / job-target-scope`. 구현: '+link(CE,'full manifest hash',258)+'.\n\n'
doc+='''## 6. Same-tick native mutation / promotion fences

native 객체 12개 mutation: skill, hediff severity, holder count, zone cell, designation, relation, bed ownership, followFieldwork, plant age, bill suspended, hediff part, hediff loadID. 모두 beforeTicks=afterTicks=1823이며 seal 후 STAGE_SAVE가 차단됐다. zone native mutation은 ID1 Stockpile의 cell 제거이며 persistent input case07은 Growing zone cell 변경으로 두 검사를 구분한다.

'''
doc+=table(['After stage attack','Native result','Verdict'],[[name,r['promotion-fence-'+key]['response'].split(':',1)[0],'BLOCKED' if not r['promotion-fence-'+key]['promoted'] else 'FAIL — approved'] for name,key in [('live skill mutation','skill'),('Worker generation change','generation'),('currentResultEpoch increment','epoch'),('staged-file byte change','bytes'),('protocol SEAL_RESULT again/new epoch','reseal')]])
doc+='''
epoch direct injection과 실제 protocol reseal을 분리했다. 실제 reseal 테스트는 epoch19에서 staging한 바이트를 epoch20/new grant로 재봉인한 뒤, 새 staging validation 없이 normal promotion해 `ARTIFACT_APPROVED … Epoch=20`에 도달했다. currentResultEpoch와 staged approval tuple을 대조하는 fence가 없다. byte change와 generation reject가 이를 보완하지 못한다.

## 7. 최고 우선순위 saved-byte semantic attack

sealed live clean hash는 세 경우 모두 `98F7817C…`. native 저장을 완료한 뒤 staged file의 field만 수정했으며 ticks1823, live Shooting10, Stab3, held count5를 그대로 확인했다. 잘못된 file의 SHA를 candidate가 이후에 수집했다. Unity Error/Exception을 주입하지 않았다.

'''
faultrows=[]
for mode,field,expected,wrong in [('silent-skill','Shooting',10,15),('silent-hediff','Stab severity',3,1),('silent-holder','held item count',5,4)]:
 x=r['saved-byte-'+mode];inj=x['injection'];faultrows.append([field,expected,wrong,'STAGED_OK','ARTIFACT_APPROVED','`'+inj['afterSha']+'`'])
doc+=table(['Supported field','Live/expected','Saved wrong value','Stage','Normal promotion','Altered staged / final SHA'],faultrows)
doc+='''
세 altered SHA는 실제 promoted artifact SHA와 일치한다. staging 출력의 ManifestHash는 sealed expected hash였지만 저장 바이트의 의미에서 계산한 값이 아니었다. structural XML은 유효했으므로 envelope validator를 통과했다. 이는 **진짜 bad bytes publication**이며, 단순한 코드 추정이나 promotion 이후 파일 편집이 아니다.

'''
doc+='Observer 경계 구현: '+link(Q/'Observer/Mutations.cs','native SaveGame postfix',33)+'. candidate 경계: '+link(WB,'native save',1390)+' → '+link(WB,'ValidateStagedXml',1416)+' → '+link(WB,'staged SHA',1425)+'. 핵심 원인: '+link(CE,'expected hash copied as actual',1180)+'.\n\n'
doc+='''## 8. Stage 없는 직접 promotion

새 Worker에서 clean admission → seal만 수행한 뒤, 별도의 wrong-skill input 복사본을 `NotStaged.rws`로 두었다. STAGE_SAVE를 한 번도 호출하지 않고 `PROMOTE_STAGED NotStaged DirectWithoutStaging`를 호출했다. **ARTIFACT_APPROVED**, final Shooting15. INTERNAL에서 lastStagedPath 및 lastStagedSha가 둘 다 빈 문자열인 것을 확인했다.

원인: promotion이 STAGED_VALIDATED뿐 아니라 RESULT_SEALED도 허용하며, 저장된 staged SHA가 비어 있으면 비교를 생략한다. caller path를 lastStagedPath와도 비교하지 않는다. staging·structural validation·semantic validation 전체를 건너뛴다.

'''
doc+='위치: '+link(WB,'RESULT_SEALED accepted',1447)+', '+link(WB,'caller-chosen staging path',1452)+', '+link(WB,'optional staged SHA check',1493)+'. 증거: `results.json: DirectWithoutStaging-promote / DirectWithoutStaging-output / no-stage-internal`.\n\n'
doc+='''## 9. XML structure, save errors, replacement safety

'''
doc+=table(['Boundary attack','Observed','Result'],[
 ['native-save postfix: malformed EOF','STAGE_FAILED; quarantine; no final approved output','PASS'],
 ['native-save postfix: second root / trailing structure','STAGE_FAILED; quarantine; no final approved output','PASS'],
 ['native-save postfix: DTD/entity declaration','DtdProcessing.Prohibit rejects before STAGED_VALIDATED','PASS'],
 ['native save-time Unity Error','STAGE_FAILED Errors=1; quarantine; prior final unchanged','PASS'],
 ['native save-time thrown IOException','STAGE_FAILED; quarantine; prior final unchanged','PASS'],
 ['lock existing approved final with exclusive FileShare.None','PROMOTION_FAILED; previous SHA unchanged; staging retained','PASS failure preservation'],
 ['replacement retry after lock released','Access denied; previous final unchanged; backup absent','normal replacement NOT VERIFIED'],
 ['fresh independent worker, normal replacement with no lock injection','Access denied; prior unchanged; staging retained','normal replacement NOT VERIFIED'],
 ['independent PowerShell/.NET File.Replace on tiny QA files','same Access denied','environment-wide limitation, do not attribute solely to candidate']])
doc+='''
previous approved output safetyを 실제 SHA로 확인했다. recovery retry는 새 admission/seal/stage 후 실행했다. candidate는 성공 경로에 `.bak.rws`를 만들도록 구현하지만 이 환경에서 정상 File.Replace 자체가 실패해 성공적인 backup creation/recovery를 인증하지 못했다. engine IL에서 FilePathForSavedGame은 filename에 `.rws`를 추가함을 확인했으며 filename 충돌이라는 추정으로 보고하지 않는다. Production fix를 임의로 제안하지 않고 deployment permission/filesystem 조건에서 정상 replacement 검증이 필요하다고 기록한다. 기존 final 보존 실패는 재현되지 않았다. candidate 전체 semantic gate FAIL의 근거는 이 환경 제한과 무관한 §7/8이다.

'''
doc+='증거: `results.json: replacement-failure-safety / replacement-backup / fresh-normal-replacement / native-save-error-error / native-save-error-throw`, '+link(E/'windows-replace-control.json')+'.\n\n'
doc+='''## 10. Fresh pre-promotion validator와 A→B→C

**candidate에는 승격 전 fresh validator가 없다.** registration / seal / stage / promote compiled path가 native save → static XML envelope → SHA → move/replace를 수행한다. fresh validation Worker/PID/profile/input SHA/expected sealed-manifest comparison receipt를 만들거나 소비하는 단계가 없다. validation 기대 hash를 독립적으로 계산하지 않고 그대로 돌려준다. 따라서 validator PID/result는 **NONE**, 검증한 staged semantic SHA는 **없음**이다.

독립 A/B/C를 추가 실행했다. A clean input에서100ticks, B A-output에서100ticks, C B-output을 fresh process에서 로드했다. B loaded hash=A sealed hash, C loaded hash=B sealed hash였다. 서로 다른 실행의 RNG/변동으로 developer의 post-tick hash와 QA post-tick hash가 반드시 같다고 요구하지 않았으며 deterministic simulation을 인증하지 않는다.

'''
doc+=table(['Process','PID','Source SHA','Authority / gen / epoch / grant','Sealed or loaded manifest','Staged / promoted SHA','Pre-promotion semantic validator'],[
 [x['process'],x['pid'],'`'+x['sourceSha']+'`',x['authorityId']+' / '+str(x.get('generation',1))+' / '+str(x.get('resultEpoch','n/a'))+' / '+x.get('grant','n/a'),'`'+x.get('sealedManifestHash',x.get('liveHash',''))+'`','`'+x.get('stagedSha','n/a')+'` / `'+x.get('promotedSha','n/a')+'`','NONE; not valid authority publication'] for x in chain])
doc+='''
ContentProfileは A/B bundleの `PROFILE-SETTLEMENT-B`; actual ModsConfig SHAは §2.3。Cも同一 actual profileで `ChainInputC` を登録した。全行の source/profile/seal/epoch/staged/final情報は independent-chain.json にある。A/Bの stage/promote成功を authority gateの valid promotionと数えない。Cは promotion後の transport regressionであり、missing pre-promotion validatorの代替ではない。expected sealed hashをQA harnessが次プロセスに渡したので、外部のdurable canonical authority sourceを証明したものでもない。

'''
doc+='証拠: '+link(E/'independent-chain.json')+', '+link(E/'positive-chain.log')+'.\n\n'
doc+='''## 11. Findings / required candidate changes

以下のG03番号はこの報告内のfinding識別子。新規QDL番号を勝手に付与せず、既存QA-ENGINE-002/006に関連づける。

### G03-01 — supported wrong saved bytes promoted

- Severity: **Critical**（authority gateが誤ったpersisted stateをapproved outcomeとして公開）
- Mapping: QA-ENGINE-002 / QA-ENGINE-006; Work Order §7/9/11
- Reproduction / Expected / Actual: §7の3件。sealed ResultManifestに対するexact staged bytesのfresh semantic validationが必要だが、XML envelopeとwrong SHA captureだけでapproved。
- Root cause: EngineHostCensus.cs:1180; WorkerBridge.cs:1416/1434。
- Required fix: promotion前にexact staged SHAをfresh engine validatorへ渡し、期待値をsealed ResultManifestから受け取り、actual loaded supported manifestと完全比較する。source/context/profile/generation/epoch/grantと検証receiptを結び、candidate/staged self-censusを期待 authorityにしない。

### G03-02 — staging-less promotion bypass

- Severity: **Critical**; Mapping: QA-ENGINE-002/006; Work Order §2/7/10
- Location: WorkerBridge.cs:1447/1452/1493。
- Reproduction: §8。stage未実行、wrong skill file、empty lastStagedShaでapproved。
- Required fix: successful stage-validation receiptを必須とし、path/exactSHA/sealedResult/generation/epochにbindingする。RESULT_SEALEDや空SHAだけでpromotionしない。caller指定pathをauthority proofに使わない。

### G03-03 — arbitrary grants / wrong operation mode / result self-baselining

- Severity: **High**; Mapping: QA-ENGINE-002/006; Work Order §4
- Location: EngineHostCensus.cs:15; WorkerBridge.cs:1256/1287。
- Reproduction: unregistered/stale-labelled/foreign-labelled/blank grant全てseal、READ_ONLYでstep/seal、direct native skill change→arbitrary self-seal→approved。
- Required fix: control-plane authorized grant registry/receiptにAuthorityId、scope/context、generation、operation permission、execution/result lineageをbindingし、不明・stale・foreign grantをreject。sealはlabel入力のみでsimulation outcomeの正当性を宣言してはならない。

### G03-04 — mutable authority and stale readiness

- Severity: **High**; Mapping: QA-ENGINE-002; Work Order §3
- Location: WorkerBridge.cs:979/1035/1093/1099; AuthorityBundle schema。
- Reproduction: registry overwrite; loaded後のwrong source/profile受理; wrong gen/map validation error後もSTEP許可、wrong mapではSEALも許可。
- Required fix: loaded artifact provenanceとactual profile/contextをimmutable authority bindingに含める。authority変更・全validation失敗経路でreadiness/seal/staging approvalを失効させ、STEP/SEAL/PROMOTEでもcurrent authorityをチェックする。absent scope/store/base lineageをdirectory名で代替しない。unused expectedSourceSha aliasの意味を統一。

### G03-05 — ResultEpoch / staged-result binding missing

- Severity: **High**; Mapping: QA-ENGINE-002/006; Work Order §10
- Location: WorkerBridge.cs:1284/1432/1462/1493。
- Reproduction: private epoch incrementでもapproved; native protocol reseal epoch19→20でold stageがapproved。
- Required fix: staged receiptにresultEpochとsealed authority/result identityを固定し、current epoch/resultとの完全一致を要求。resealでold staging validationを失効させる。同一live hashを異なるgrant/epochの代替にしない。

### G03-06 — comparator/helper and declared scope limitations

- Severity: **Medium**（helper equality誤解）; Mapping: QA-ENGINE-006 scope / test-evidence limitation。
- Location: EngineHostCensus.cs:673 (`CompareCensus`); PawnRecord / ReservationRecord / GenerateCensus job projection。
- Observation: 63/97 unequal hash testでhelper PASS。ただしcurrent gateは全hashなので実際stageはreject。JobDefのみではactive job ID/targetを検証できない。
- Required fix: current gateの改善を認めつつ、future fresh validatorのequalityがこのpartial helperを唯一のpredicateに使わないこと。supported graphとunsupported job/controller fieldsをexplicitに宣言し、scope拡張を認証済みと主張しない。

正常replacement成功/backupの環境制限は別のevidence limitationであり、G03-01..05のsemantic/authority defectを置き換えない。

## 12. A report reconciliation / defect disposition

'''
doc+=table(['A claim','Independent conclusion'],[
 ['legacy candidate self-approval removed','CONFIRMED: initial 15 invalid inputs + APPROVE_SEMANTIC blocked'],
 ['immutable AuthorityBundle','NOT CONFIRMED: REGISTER overwrites; source/profile/context/mode binding incomplete'],
 ['authoritative simulation grant','NOT CONFIRMED: arbitrary label accepted; direct mutation can self-seal'],
 ['whole collected V3 semantic hash','CONFIRMED within declared projection: 102 representative leaf paths gated'],
 ['same-tick recensus before stage/promote','CONFIRMED for tested native fields; does not validate saved bytes'],
 ['saved-byte proof / definitive QA-ENGINE-002/006 closure','REJECT: three supported semantic corruptions promoted'],
 ['generation, epoch, staged SHA reverified','generation + SHA observed; epoch binding FAIL'],
 ['atomic replacement / backup preservation','forced failure preserved previous output; normal success/backup not proven in environment'],
 ['A→B→C freshness closes authority','transport fidelity confirmed; C is post-promotion, not required validator']])
doc+='''
'''+table(['Existing defect','Recommendation','Reason'],[
 ['QA-ENGINE-002','**STILL FAILING**','initial admission improved; arbitrary grant/authority overwrite + wrong saved-byte publication persist'],
 ['QA-ENGINE-006','**STILL FAILING**','full collected hash improved; saved-byte semantic validator absent, direct stage bypass and epoch/result fence absent']])
doc+='''
## 13. Evidence index / limits / final recommendation

'''
for p in [E/'results.json',E/'final-integrity-summary.json',E/'independent-negative-summary.json',E/'declared-field-matrix.json',E/'declared-field-gates.json',E/'job-field-matrix.json',E/'independent-chain.json',E/'candidate-gate-il.txt',E/'pdb-provenance.json',E/'main-run.log',E/'supplement-run.log',E/'supplement-retry.log',E/'positive-chain.log',E/'replacement-check.log']:
 doc+='- '+link(p)+'\n'
doc+='''
個別finalwrong artifact、quarantine、injected input、profileログ、fullcensusは同じQArootのEvidence/Profilesに保管した。evidence_manifest.jsonは生成したQA source/binary/evidence/fixture出力のexact hashesを含む（自己参照を除く）。reportとmanifestが指す物証を削除・candidateへ上書きしていない。

Engine startupにはSteamAPI.Init failedとhidden ritual precept補完のmessageがあった。初期supported graphはnative READYおよびexpected manifest hash一致、read observer errors=[]を確認したが、これを全mod/world/global stateのsemantic clean certificationに拡張しない。known automatic global context修復やtemporal contaminationをG-Q1/PlayerGlobalの解決と解釈しない。crash durability、network gameplay authentication、full-map/job-driver semantics、final production engine authorityの認証は本Work Order外。

**Master recommendation:** このcandidateのQA-ENGINE-002/006 closureを承認しない。改善したinput admission/full collected hash/structural validationは保持可能だが、必須fresh staged-byte semantic validator、authorized grant/authority lineage、strict stage/epoch promotion bindingを修正した新しいfrozen candidateが必要。Masterの既存gate状態はこのreportでは変更しない。

**Final Verdict: FAIL.** 本Work Orderの検証・報告を終了し次指示を待つ。
'''
# Keep report Korean-facing; common architecture labels remain English.
replacements={'previous approved output safetyを':'previous approved output safety를','ContentProfileは':'ContentProfile은','証拠:':'증거:','個別finalwrong artifact、quarantine、injected input、profileログ、fullcensusは同じQArootのEvidence/Profilesに保管した。':'개별 wrong final artifact·quarantine·injected input·profile 로그·full census는 같은 QA root의 Evidence/Profiles에 보관했다.','evidence_manifest.jsonは生成したQA source/binary/evidence/fixture出力のexact hashesを含む（自己参照を除く）。reportとmanifestが指す物証を削除・candidateへ上書きしていない。':'evidence_manifest.json에 QA source/binary/evidence/fixture 출력의 exact hash를 기록했다(자기 자신 제외). 증거 파일을 삭제하거나 candidate에 덮어쓰지 않았다.','Engine startupにはSteamAPI.Init failedとhidden ritual precept補完のmessageがあった。初期supported graphはnative READYおよびexpected manifest hash一致、read observer errors=[]を確認したが、これを全mod/world/global stateのsemantic clean certificationに拡張しない。known automatic global context修復やtemporal contaminationをG-Q1/PlayerGlobalの解決と解釈しない。crash durability、network gameplay authentication、full-map/job-driver semantics、final production engine authorityの認証は本Work Order外。':'Engine startup에는 SteamAPI.Init failed와 hidden ritual precept 보완 메시지가 있었다. 초기 supported graph는 native READY·expected manifest hash 일치·read observer errors=[]를 확인했지만, 전체 mod/world/global state의 semantic clean 인증으로 확장하지 않는다. 알려진 global context 자동 보완이나 temporal contamination을 G-Q1/PlayerGlobal 해결로 해석하지 않는다. crash durability·network gameplay authentication·full-map/job-driver semantics·최종 Production engine authority 인증은 본 Work Order 밖이다.','**Master recommendation:** このcandidateのQA-ENGINE-002/006 closureを承認しない。改善したinput admission/full collected hash/structural validationは保持可能だが、必須fresh staged-byte semantic validator、authorized grant/authority lineage、strict stage/epoch promotion bindingを修正した新しいfrozen candidateが必要。Masterの既存gate状態はこのreportでは変更しない。':'**Master recommendation:** 이 candidate의 QA-ENGINE-002/006 closure를 승인하지 않을 것을 권고한다. 개선된 input admission/full collected hash/structural validation은 유지할 수 있으나, 필수 fresh staged-byte semantic validator·authorized grant/authority lineage·strict stage/epoch promotion binding을 갖춘 새로운 frozen candidate가 필요하다. Master의 기존 gate 상태를 변경하지 않는다.','**Final Verdict: FAIL.** 本Work Orderの検証・報告を終了し次指示を待つ。':'**Final Verdict: FAIL.** 본 Work Order의 검증·보고를 종료하고 다음 지시를 기다린다.'}
for a,b in replacements.items():doc=doc.replace(a,b)
(R/'QA_EngineHost_Semantic_Authority_Gate_03.md').write_text(doc,encoding='utf-8')
print('Report written',len(doc))
