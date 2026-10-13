from review_setup import ROOT,Q,PKG,R2,R2MAN,load,write,sha,now,preservation
import json
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R3_Preparation_S1_20261008.md'
def link(label,p,line=None):return f'[{label}]({p.as_posix()}{":"+str(line) if line else ""})'
def main():
    assert not REPORT.exists() and not (Q/'COMPLETION.json').exists(),'preserve existing attempts'
    ack=load(Q/'ACK.json');rid=ack['result_id'];before=load(Q/'PRESERVATION_BEFORE.json');after=preservation()
    for key in ['r2_frozen107','old_archive19','r1_frozen147','pipeline206','qa_inventories']:assert before[key]==after[key],key
    write(Q/'PRESERVATION_AFTER.json',after)
    index=load(Q/'R2_EVIDENCE_INDEX.json');lineage=load(Q/'R2_LINEAGE.json');selected=lineage['candidates'][0];alt=lineage['candidates'][1]
    conclusions=[dict(id='R2-M01',assessment='STATIC_CONTRACT_FAILURE_CONFIRMED_WITH_QUALIFICATION',qualification='Public validation request permitted; failure is unconstrained executable/config selection and unproved operator origin.'),dict(id='R2-M02',assessment='STATIC_CLOSED_CONTEXT_FAILURE_CONFIRMED',qualification='Result has11 fields; task/receipt/promote carry more fields but do not prove validator context equality.'),dict(id='R2-M03',assessment='STATIC_LIFECYCLE_FAILURE_CONFIRMED_WITH_QUALIFICATION',qualification='File channel not inherently prohibited; exact owned process/result/consume contract required; validator may normally exit after result.'),dict(id='R2-M04',assessment='SUPPORTED_ENCODING_COVERAGE_GAP_CONFIRMED_WITH_QUALIFICATION',qualification='Core/mod identity and R-format progress credited; no blanket all-Def serialization or sort-is-always-invalid claim.'),dict(id='R2-M05',assessment='EVIDENCE_SCOPE_FAILURE_CONFIRMED',qualification='Production handler fixture and real OS child are not genuine native semantic validator execution.'),dict(id='R2-M06',assessment='NATIVE_UNTESTED_CAUSE_UNKNOWN',qualification='No native launch/loader proof; unconditional NAT03 plusfalse file bool does not prove DRM cause or standalone impossibility.'),dict(id='R2-M07',assessment='FULL_PRESERVATION_CLAIM_NOT_ESTABLISHED',qualification='Archive preserved; known installed mismatch actor/cause remainUNKNOWN; no installed restore/reread or attribution.'),dict(id='R2-M08',assessment='COMPLETION_FORMAT_FAILURE_IDENTITY_RECONCILED',qualification='Same R2 task aliases and12 frozen artifact hashes identified; missingstandard result/producer/schema fields remain.')]
    write(Q/'INDEPENDENT_CONCLUSIONS.json',dict(at=now(),result_id=rid,findings=conclusions,md129='Static early-return coverage incomplete; role/relevant state must be classified; no observed stale-capability exploit',r3_static_reviewed=False,r3_runtime_e2_released=False,runtime_processes=0,rebuilds=0,attack_reproduction=False,full_required_coverage=False))
    write(Q/'QA_METADATA_HELPER_DIAGNOSTIC.json',dict(at=now(),failure='First PDB metadata helper invocation lacked sha in extracted-function namespace',repair='Provide sha and force all PDB source document resolution through frozen_path map',candidate_executed=False,mutable_source_read=False,final_pdb_documents_matched=[4,4]))
    worker=R2/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';census=R2/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';runner=R2/'scratch/EngineGate05R2/Program.cs'
    report=f'''# Engine Gate05-R3 준비 QA S1 — 독립 R2 검토

**준비 작업 완료. R2의 중요 정적 계약 공백과 native/evidence 미충족을 독립 확인했고, R3 검증 matrix 및 정상 native feasibility plan을 작성했다. R3 E2는 미발행·미실행이며 PASS/closure 판정은 없다.** Master R2-M01~08을 자동 채택하지 않고 frozen source/raw/accepted MD125~132와 대조했으며 아래 해석 보완을 제시한다.

Result `{rid}`. Delivery `SOL-GATE05-R3-QA-PREP-S1-20261008-01`; WP `WP_QA_ENGINE_GATE05_R3_PREPARATION`, revision `S1`. 완료 {now()} (Asia/Seoul). 이전 Pipeline S2는 완료·보고된 상태였고 중복 active QA WP는 없었다.

## 정확한 대상과 보존

검토 대상은 R2 immutable107이며 R3 mutable 구현/Debug/Release를 읽거나 실행하지 않았다. WP SHA `4F068A272E32925F164B598D94096AADC49BA14A63A427329778D5F86F6F9486`, R2 freeze manifest SHA `110A796F5699495998D61503016F8F7C0430B9EC988DD20220D51416AACD421C`를 먼저 확인했다.

| 항목 | 독립 확인값 |
|---|---|
| R2 selected Debug DLL SHA / MVID | `{selected['dll_sha256']}` / `{selected['mvid']}` |
| matching Debug PDB SHA | `{selected['pdb_sha256']}` |
| alternate Release DLL SHA / MVID | `{alt['dll_sha256']}` / `{alt['mvid']}` |
| alternate PDB SHA | `{alt['pdb_sha256']}` |
| WorkerBridge.cs SHA | `{sha(worker)}` |
| EngineHostCensus.cs SHA | `{sha(census)}` |
| R2 runner source SHA | `{sha(runner)}` |
| raw/results summary | 24 checkpoints,23 reported PASS/1 BLOCKED; raw와 JSON 집계 일치 |

PE MVID/CodeView/PDB GUID를 metadata bytes에서 읽고 Debug/Release source+generated documents 각4/4 checksum을 **frozen source 사본에만** 대조했다. PDB의 original document path는 매핑 key이며 mutable 원본을 읽지 않았다. {link('R2 lineage',Q/'R2_LINEAGE.json')}에는 원래 document name과 실제 frozen_source_path가 함께 있다. 검토 시점 freeze를 E1 실행 전 snapshot으로 소급하지 않는다.

R2 frozen107, old Engine archive19, rejected R1 frozen147, Pipeline original+frozen206 및 이전 QA324/297/312/238 전후 모두 동일하다. allowed R3 Engine source9개의 current bytes는 역사 후보 보존 기준으로 검사하지 않았다. 원본 installed DLL도 재독취/수정/restore하지 않았다. known installed incident는 OPEN이며 old2D64… archive와 historically observedBB3B…를 동일 candidate로 합치지 않았다. {link('before preservation',Q/'PRESERVATION_BEFORE.json')}, {link('after preservation',Q/'PRESERVATION_AFTER.json')}.

## 독립 판정과 Master finding 보완

| ID | 독립 결론과 근거 |
|---|---|
| M01 | 정적 operator-origin/config 경계 미충족. {link('Worker launch',worker,2057)}는 요청 입력에서 executable/arguments를 선택하고 admitted fixed binary/config와의 결속을 확인하지 않는다. {link('Bind',worker,2170)}의 handle 저장도 launch origin 자체의 증명이 아니다. **public caller가 validation 실행을 요청하는 것 자체는 MD126이 허용한다**. 실패 원인을 request reachability만으로 설명하면 지나치게 넓다 |
| M02 | {link('ValidatorResult DTO',census,100)}의11 fields와 {link('Complete',worker,2322)}를 직접 대조했다. authority/source/store/grant/generation/scope/target/mode/version/seal/epoch의 result context가 빠져 있다. task 값으로 receipt를 만드는 경로와 후단 Promote의 generation/epoch/authority 검사 진전은 존재하지만 validator의 빠진 context proof를 대신하지 못한다 |
| M03 | 다른 result-file fallback, result process-start field의 비교 누락, {link('consume',worker,2469)}에서 task consumed 설정 뒤 rename exception 무시 및 cleanup 정책 공백을 확인했다. **file channel 자체가 금지된 것은 아니고**, MD126은 동등한 operator-controlled mechanism을 허용한다. 정상 validator가 결과를 남긴 후 exit할 수 있으므로 completion 순간 무조건 alive라는 새 요구도 만들지 않는다 |
| M04 | {link('ContentProfileProvider',census,1516)}에서 core SHA/MVID, active mod order, statBases 값, R-format과8 family guard 개선을 credit한다. 그러나 delimiter entry, null/empty collapse·null skip, 일부 collection sorting, patch count/미정 settings coverage, missing mod-assembly hash의 empty record는 typed supported material coverage를 충분히 보장하지 않는다. **모든 Def 완전 serialization이나 모든 sorting 금지를 새 요구로 채택하지 않는다** |
| M05 | {link('Runner fixture',runner,241)}의 uninitialized/reflection/profile stub와 sleep child/runner-authored result, source Contains/cache flag assertions를 확인했다. Production handler logic 일부와 실제 OS child evidence는 있으나 genuine native staged load/census/actual loaded profile revalidation의 증거가 아니다 |
| M06 | {link('NAT03',runner,570)}은 file existence bool 이후 unconditional BLOCKED. raw boolFalse와 원문 report의 DRM 원인 설명이 충돌한다. native executable/argv/PID/exit/loader attempt proof가 없어 **NATIVE_UNTESTED / CAUSE_UNKNOWN**이다. 이번 준비에서도 실행 가능/불가능을 반대로 단정하지 않았다 |
| M07 | NAT02 assertion은 archive hash로 PASS를 정하고 installed hash는 출력한다. archive 보존과 installed old-baseline 동일성을 구분한다. known incident의 변경 actor/cause를 이 snapshot만으로 A에게 귀속하지 않는다. preservation FULL claim은 입증되지 않았고 incident를 정상화하지 않았다 |
| M08 | 원문 completion aliases로 같은 R2 task를 식별하고12 declared deliverables를 matching frozen SHA에 직접 대조했다. selected/alternate DLL/PDB4개도 식별했다. 그러나 standard producer/report_kind/result_id/artifacts/schema/time/WP fields는 부재다. **다른 task라고 단정하지 않고 identity reconciliation과 completion-format failure를 분리**한다 |

MD129는 RevokeReadiness의 실제 철회 동작을 credit한다. Bind/Execute/deprecated handler의 early return/exception에는 일관된 wiring이 보이지 않으므로 relevant state·validator/simulator 역할별 failure→clean reset/re-admission 표가 필요하다. 모든 query 오류나 모든 process 역할에 무조건 전역 revoke를 요구하지 않는다. Native stale-capability exploitation을 관측했다고 주장하지 않는다.

상세 line/SHA/근거와 독립 qualification은 {link('independent findings',Q/'INDEPENDENT_R2_FINDINGS.md')}, {link('source/raw/completion evidence index',Q/'R2_EVIDENCE_INDEX.json')}, {link('structured conclusions',Q/'INDEPENDENT_CONCLUSIONS.json')}에 있다. 전체 checkpoint 수는 필수 gate category 완료 수가 아니다. public-key cryptography는 MD126의 필수 조건이 아니며 기존 fresh validator 방향을 철회하지 않았다.

## R3 verification matrix와 정상 native 준비

{link('R3 matrix',Q/'R3_VERIFICATION_MATRIX.md')}는 operator-owned issuance→admitted launch→fresh staged load→actual profile/census→owned result consume→internal receipt→approved promotion의 정상 flow를 정의한다. accepted MD128의16 logical dimensions 각각에 task/result/receipt/current authority·grant·seal/current epoch의 source equality, 필요한 native trace 및 UNTESTED 조건을 표로 분리했다. Validator READ_ONLY와 simulation grant mode의 역할 매핑을 명시해야 하며 서로 다른 역할 값을 무조건 동일 문자열로 강제하지 않는다.

Matrix는 MD129 failure/re-admission, MD130 versioned typed field/type/null/missing/empty/order 및 실제 loaded assembly/mod/DLC/Def/patch/settings coverage·cache epoch, MD131 promotion primitive, installed incident, execution-before provenance/standard completion을 포함한다. Static review와 normal positive flow만으로 모든 adverse rejection runtime coverage가 생겼다고 계산하지 않는다. forged/tampered authority/receipt/history/schema construction이나 새 exploit 절차는 설계하지 않았다.

{link('native feasibility plan',Q/'NATIVE_FEASIBILITY_PLAN.md')}는 별도 admitted R3 release 뒤 licensed project runtime의 exe/game-data/native/Managed/mod/save-data/profile/task/log paths·identity를 확인하는 최소 절차와 log bundle을 제시한다. 원본 Steam/Workshop/core/ProbeMod/user save 변경·protection 우회는 허용하지 않는다. launch args는 실제 admitted launcher/runtime 지원을 확인한 뒤 확정하며 지금 실행 가능한 launch command나 새 harness를 만들지 않았다.

읽은 MP {link('HostUtil.StartArbiter',ROOT/'Multiplayer-master/Multiplayer-master/Source/Client/Networking/HostUtil.cs',214)}는 현재 executable의 child process/log/save-data/start-error 처리 참고다. Arbiter는 lockstep 비교 참가자이고 WarEconomy의 staged fresh semantic validator나 zero-drift proof가 아니다. 참조 모드 설치·빌드·실행/통합도0이다.

## Coverage와 산출물

이번 수행: immutable bytes/PDB/source metadata 확인, 독립 정적 계약·evidence 분류, matrix와 feasibility design. Game/native/candidate/runner 실행0, Production 또는 QA runtime harness build0, authority/forgery/vulnerability reproduction0. 모든 R3 static implementation 판정과 native row는 아직 NOT_REVIEWED/UNTESTED이며 fresh runtime E2는 별도 Master release가 필요하다. R2 static failure가 새 R3 candidate의 failure/PASS를 자동 결정하지 않는다.

Canonical SRS와 accepted MD/C/ADR006B를 유지한다. Server가 final Domain Authority이며 Full Worker .rws를 wholesale canonical replacement하지 않는다. W/L/G/M, one LocalClock writer, island barrier/target publication 및 supported V4 범위의 한계를 유지한다. G-Q1/PlayerGlobal schema·physical split, Quest/WorldPawns read-only, subsystem owner/discardability, separate-process zero drift를 freeze하지 않았다. Engine002/006/Pipeline007/current schema OPEN, Foundation HOLD 및 기존 narrow closures를 변경하지 않았다.

{link('ACK',Q/'ACK.json')}의 초기 bytes는 Master가 확인한 그대로 보존한다. 완성 artifact hashes는 별도 ACK_COMPLETION_BINDING/RESULT_INDEX/COMPLETION에 결속하며 원래 ACK의 아직 생성 전 null hash를 소급 바꾸지 않는다. {link('evidence manifest',Q/'EVIDENCE_MANIFEST.json')}, {link('result index',Q/'RESULT_INDEX.json')}, {link('COMPLETION',Q/'COMPLETION.json')}은 실제 report/근거/matrix/plan/preservation hashes를 참조한다. manifest/self 및 terminal binding/transport metadata는 hash cycle을 피하도록 제외하고 index에서 별도 결속한다.

Metadata helper의 초기 namespace sha 누락은 진단과 수정 내용에 보존했다. 이는 파일 metadata 검토 도구의 오류이며 candidate/runtime failure가 아니다. 기존 hourly monitor/통신/상위 governance는 수정하지 않았다. 사용자 승인된 direct tool로 Master에게 즉시 한 번 완료 보고하고 delivery proof를 별도로 보존한다.
'''
    REPORT.write_bytes(report.encode())
    excluded={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','COMPLETION.json','ACK_COMPLETION_BINDING.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
    files=[dict(path=str(p),relative_path=p.relative_to(Q).as_posix(),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in excluded]
    manifest=Q/'EVIDENCE_MANIFEST.json';write(manifest,dict(schema_version=1,result_id=rid,at=now(),scope='QA preparation/static review only',report_path=str(REPORT),report_sha256=sha(REPORT),files=files,self_terminal_transport_excluded=sorted(excluded)))
    artifacts=[dict(role=role,path=str(path),sha256=sha(path)) for role,path in [('qa_report',REPORT),('independent_findings',Q/'INDEPENDENT_R2_FINDINGS.md'),('r3_verification_matrix',Q/'R3_VERIFICATION_MATRIX.md'),('native_feasibility_plan',Q/'NATIVE_FEASIBILITY_PLAN.md'),('r2_evidence_index',Q/'R2_EVIDENCE_INDEX.json'),('r2_source_pdb_lineage',Q/'R2_LINEAGE.json'),('preservation_before',Q/'PRESERVATION_BEFORE.json'),('preservation_after',Q/'PRESERVATION_AFTER.json'),('evidence_manifest',manifest)]]
    binding=dict(schema_version=1,producer='Sol',report_kind='QA_PREPARATION',result_id=rid,delivery_id=ack['delivery_id'],wp_id=ack['wp_id'],wp_revision='S1',at=now(),status='COMPLETED_PREPARATION',scope=ack['scope'],report_path=str(REPORT),report_sha256=sha(REPORT),evidence_manifest_path=str(manifest),evidence_manifest_sha256=sha(manifest),initial_ack_path=str(Q/'ACK.json'),initial_ack_sha256=sha(Q/'ACK.json'),runtime_e2_released=False)
    write(Q/'ACK_COMPLETION_BINDING.json',binding)
    result=dict(**binding,r2_static_verdict='STATIC_CONTRACT_FAILURES_AND_EVIDENCE_GAPS_CONFIRMED',r3_verdict='NOT_REVIEWED_NOT_RELEASED',native_feasibility='PLAN_ONLY_UNTESTED',independent_conclusions=conclusions,qualification_points=['caller request allowed; admitted executable/config boundary required','filechannel equivalent may be allowed; owned lifecycle required','validator may exit normally after result','meaningfulorder/scope coverage rather than all-Def serialization','installed mismatch actor/cause unknown','same R2 task reconciled; standard schema still missing'],preservation_counts=dict(r2=107,old_engine_archive=19,r1=147,pipeline=206,qa=[324,297,312,238]),preservation_changes=0,evidence_files=len(files),artifacts=artifacts,full_required_coverage=False,mutable_R3_source_read=False,installed_original_read=False,game_candidate_runner_processes=0,runtime_harness_builds=0,forged_or_attack_reproduction=False,closure_changed=False,governance_changed=False,scheduler_changed=False,report_delivery='PENDING')
    write(Q/'RESULT_INDEX.json',result)
    completion=dict(binding);completion.update(status='COMPLETED',summary='Independent immutable R2 static review, R3 verification matrix/native plan complete; no runtime E2',verdict='PREPARATION_COMPLETE_NO_RUNTIME_VERDICT',limitations=['R2 snapshot is post-review, not execution-before proof','R3 mutable candidate not inspected or executed','R3 static/native evidence NOT_REVIEWED/UNTESTED','No exploitation/authority-forgery reproduction','Installed incident actor/cause UNKNOWN; no original restore','No gate closure/Foundation release'],artifacts=artifacts,result_index_path=str(Q/'RESULT_INDEX.json'),result_index_sha256=sha(Q/'RESULT_INDEX.json'),ack_binding_sha256=sha(Q/'ACK_COMPLETION_BINDING.json'))
    write(Q/'COMPLETION.json',completion)
    print(json.dumps(dict(result_id=rid,report_sha256=sha(REPORT),manifest_sha256=sha(manifest),evidence_files=len(files),completion_sha256=sha(Q/'COMPLETION.json')),indent=2))
def repair_unpublished_terminal():
    assert REPORT.exists() and not (Q/'COMPLETION.json').exists()
    diagnostic=load(Q/'QA_METADATA_HELPER_DIAGNOSTIC.json');diagnostic['terminal_metadata_repair']='Duplicate status keyword during final COMPLETION construction corrected before completion/report delivery';write(Q/'QA_METADATA_HELPER_DIAGNOSTIC.json',diagnostic)
    manifest=load(Q/'EVIDENCE_MANIFEST.json')
    for row in manifest['files']:row['sha256']=sha(__import__('pathlib').Path(row['path']));row['bytes']=__import__('pathlib').Path(row['path']).stat().st_size
    write(Q/'EVIDENCE_MANIFEST.json',manifest)
    binding=load(Q/'ACK_COMPLETION_BINDING.json');binding['evidence_manifest_sha256']=sha(Q/'EVIDENCE_MANIFEST.json');write(Q/'ACK_COMPLETION_BINDING.json',binding)
    result=load(Q/'RESULT_INDEX.json');result['evidence_manifest_sha256']=binding['evidence_manifest_sha256']
    for row in result['artifacts']:row['sha256']=sha(__import__('pathlib').Path(row['path']))
    write(Q/'RESULT_INDEX.json',result)
    completion=dict(binding);completion.update(status='COMPLETED',summary='Immutable R2 independent static review and R3 matrix/native preparation complete; no runtime E2',verdict='PREPARATION_COMPLETE_NO_RUNTIME_VERDICT',limitations=['R2 post-review snapshot is not execution-before proof','R3 mutable candidate NOT_REVIEWED/native UNTESTED','No exploit/forged authority reproduction','Known installed incident actor/cause UNKNOWN','No closure/Foundation release'],artifacts=result['artifacts'],result_index_path=str(Q/'RESULT_INDEX.json'),result_index_sha256=sha(Q/'RESULT_INDEX.json'),ack_binding_sha256=sha(Q/'ACK_COMPLETION_BINDING.json'))
    write(Q/'COMPLETION.json',completion)
    print(json.dumps(dict(result_id=binding['result_id'],report_sha256=sha(REPORT),manifest_sha256=sha(Q/'EVIDENCE_MANIFEST.json'),evidence_files=len(manifest['files']),completion_sha256=sha(Q/'COMPLETION.json')),indent=2))
if __name__=='__main__':
    import sys
    if '--repair-unpublished-terminal' in sys.argv:repair_unpublished_terminal()
    else:main()
