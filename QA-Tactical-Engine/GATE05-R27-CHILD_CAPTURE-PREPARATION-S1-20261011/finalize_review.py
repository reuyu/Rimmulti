from bootstrap_review import R,Q,H,W,C,EW,MR,F,B,OLD,FR,load,sha,row,write,now,preservation
import pathlib,json,hashlib
REPORT=R/'docs/QA_EngineHost_Gate05_R27_Child_Capture_Preparation_S1_20261011.md'
if __name__=='__main__':
    assert not REPORT.exists() and not (Q/'COMPLETION.json').exists()
    ack=load(Q/'ACK_INITIAL.json');assert sha(Q/'ACK.json')==sha(Q/'ACK_INITIAL.json')
    oracle=load(Q/'PROSPECTIVE_CAPTURE_ORACLE.json');old=load(OLD);names=[g['name'] for g in oracle['getter15_order_types']];assert len(names)==15 and names[-1]=='Scope'
    assert oracle['actual_candidate_factory_Capture_getters_calls']==0 and not oracle['mutable_R27_read'];assert len(oracle['normal_pairs'])==4
    typed=0;rawsets=0
    def verify_text(v):
        t=v['utf8_text'].encode();assert len(t)==v['bytes'] and hashlib.sha256(t).hexdigest().upper()==v['sha256'] and not v['BOM'] and not v['trailing_newline'];return json.loads(t)
    for new,prev in zip(oracle['normal_pairs'],old['four_normal_fixture_pairs']):
        assert new['input_parent14_and_original7']==prev['parent_separately_authored'] and new['input_child14_and_original7']==prev['child_separately_authored'] and new['input_task27']==prev['synthetic_owned_task27']
        expected=new['expected_Capture15'];assert list(expected)==names and len(expected)==15 and expected['Scope']=='DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED'
        assert len(expected['ApprovedChildDeclaration'])==7 and list(expected['ApprovedChildDeclaration'])==oracle['descriptor7_order'];assert list(expected['Task'])==[x['field'] for x in oracle['task27_field_types']]
        assert expected['OperatorOptionValues']==[expected['ApprovedChildDeclaration'][x] for x in oracle['operator_option_value_order']]
        assert expected['TaskInvocationValues']==[new['input_task_file_path'],expected['Task']['capabilityNonce']]
        assert expected['SelectedUserDataDirectory']==new['input_child14_and_original7']['config14']['validatorUserDataDirectory'] and expected['WorkingDirectory']==new['input_child14_and_original7']['config14']['validatorCwd']
        assert verify_text(new['expected_Capture15_compact_utf8'])==expected and verify_text(new['expected_full_envelope_compact_utf8'])==new['expected_observation_envelope']
        assert verify_text(new['expected_approved7_compact_utf8'])==expected['ApprovedChildDeclaration'] and verify_text(new['expected_task27_compact_utf8'])==expected['Task']
        assert verify_text(new['expected_option7_compact_utf8'])==expected['OperatorOptionValues'] and verify_text(new['expected_invocation2_compact_utf8'])==expected['TaskInvocationValues']
        for side,k in [('parent','input_parent14_and_original7'),('child','input_child14_and_original7')]:
            assert verify_text(new['expected_receipt_pretty_utf8'][side])==new[k]['expected_receipt_redaction11'];assert verify_text(new['expected_snapshot_pretty_utf8'][side])==new[k]['expected_snapshot_redaction13']
        m=new['mutations_after_successful_capture_only']
        for label in ['callerTask27','returnedTask27']:
            assert list(m[label])==list(expected['Task']) and all(type(v)==type(expected['Task'][k]) and v!=expected['Task'][k] for k,v in m[label].items())
        assert list(m['returnedApprovedDeclaration7'])==oracle['descriptor7_order'] and all(v!=expected['ApprovedChildDeclaration'][k] for k,v in m['returnedApprovedDeclaration7'].items())
        assert new['actual_tests_executed']==0;typed+=len(new['ordered_type_map']);rawsets+=10
    assert typed==976
    source=load(Q/'FROZEN_SCHEMA_SOURCE_OBSERVATION.json')
    for a in source['spans']:
        p=pathlib.Path(a['path']);data=p.read_bytes()[a['start']:a['end_exclusive']];assert sha(p)==a['file_sha256'] and len(data)==a['bytes'] and hashlib.sha256(data).hexdigest().upper()==a['sha256']
    assert len(source['spans'])==8 and len(source['task27_CSharp_types'])==27
    ledger=load(Q/'PROSPECTIVE_CALLPLAN.json');assert ledger['per_run_primary_direct_calls']==dict(IssueAdmissionReceiptFromBytes=8,receipt_IsValid=8,OperatorChildLaunchInputs_Capture=4);assert ledger['per_run_Capture_getter_observations']==180
    line=load(Q/'R27_PREPARATION_FROZEN_R25_LINEAGE.json')['candidates'];assert len(line)==2 and all(len(x['documents'])==4 and all(v['matched'] for v in x['documents']) for x in line)
    refs=load(Q/'RECOVERY_AND_REQUIREMENT_BINDING.json')['references'];write(Q/'FINAL_REFERENCE_OBSERVATION.json',dict(at=now(),references=[row(pathlib.Path(v['path'])) for v in refs],mutable_governance_reference_snapshot=True,Master_live_metadata_changes_not_oldcandidate_lineage=True,A_ongoing_R27_NOT_READ=True))
    write(Q/'PRESERVATION_AFTER.json',preservation());before=load(Q/'PRESERVATION_BEFORE.json');after=load(Q/'PRESERVATION_AFTER.json');assert before['files']==after['files'] and before['frozen_files']==after['frozen_files']
    write(Q/'FINAL_PREPARATION_METADATA_AUDIT.json',dict(at=now(),verdict='INDEPENDENT_READ_ONLY_CAPTURE15_FULL_GRAPH_COPY_AND_PROVENANCE_PREPARATION_COMPLETE_R27_NOT_REVIEWED',normal_pair_count=4,getter15_names_order_types_bound=True,descriptor_field7_order_and_option_value7_order_distinct=True,task27_CLR_types_bound=True,all_caller_and_returned_task27_mutations_specified=True,prospective_type_map_rows=976,prospective_raw_value_sets=rawsets,raw_expected_self_consistency_only_not_candidate_test=True,frozen_source_spans=8,PDB_sources_per_mode=[4,4],protected13458_before_after_matched=True,frozen99_matched=True,current_mutable7_excluded_not_read=True,original_R26_inputs_oracle_unchanged=True,actual_candidate_QA_compiler_factory_Capture_load_calls=0,native_Process_game_assets_copy=0,source_schema_WP_governance_closure_scheduler_changes=0,actual_R27_candidate_verdict='NOT_REVIEWED_NO_EXACT_FROZEN_CANDIDATE_ADMISSION',future_execution_provenance_phases=7,construction_copy_risks=9,fullgate_runtime_e2='NOT_RELEASED',foundation='HOLD'))
    text='''# Gate05 R27 Capture — 독립 QA 준비 S1

Master 승인된 15 getter 계약에 맞춘 **독립 READ_ONLY 준비를 완료**했습니다. 정상 pair4개·전체 typed/raw UTF8 기대값·caller/returned Task27 및 approved7/policy/list 소유권 계획·향후 실행 증거 체크리스트를 작성했습니다. **실행 PASS가 아니며 R27 candidate는 NOT_REVIEWED**입니다. Mutable R27 source/bin/obj/A ongoing runner·oracle·결과는 읽지 않았고 컴파일·QA runner·factory·Capture·DLL load·game/native/Process/assetscopy 실행0입니다.

WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_PREPARATION/S1, delivery SOL-GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011-01. 원문 QA WP SHA7A17440B4598743EF214E0A08C81CB282F917BB081314B51D5CEB1D537FE07B9와 Master API 정정 SHA AA38D50D9B6EC9E2B74327BAB8348E1DEDD4EFB87BC0A2AECF0C85B27C39B7A3를 함께 결속했습니다. 기존 WP를 수정하지 않았습니다.

반환 OperatorLaunchDescriptor는 PascalCase properties가 아니라 실제 소문자 public fields7입니다. 선언 순서는 originId, expectedConfigId, expectedRole, expectedCapabilityBoundary, launchPlanId, expectedConfigPath, expectedConfigSha256. OperatorOptionValues는 expectedConfigPath, expectedConfigSha256, originId, launchPlanId, expectedConfigId, expectedRole, expectedCapabilityBoundary 값의 순서입니다. 두 순서를 구분했습니다. Padded 정상 pair의 approved read_only/local_sandboxed를 BoundRole READ_ONLY/LOCAL_SANDBOXED로 대체하지 않는 정확한 값 기대를 포함했습니다.

| 준비 증거 | 범위 |
|---|---|
| Getter 계약 | ParentReceipt부터 Scope까지 정확15 이름/type/순서 및 full graph |
| Normal fixtures | 독립 parent14/child14/original7/raw SHA, 네 R26 pair 원문 그대로 |
| Typed 기대값 | observation envelope에976 hierarchical type/order rows; 실행 비교 count 아님 |
| Raw UTF8 기대값 | pair당10 value sets/총40, compact와 Windows pretty CRLF 분리 |
| Task ownership | caller27·returned27 각각 전 필드 변경값, 총216 field edits 명시 |
| Other ownership | returned approved7/submitted descriptors/policy4-record4/detached option7-invocation2 및 policy IDs |
| Source/provenance | frozen R25 source span8/Debug-Release PE-MVID-CodeView-PDB source4/4/후속 증거7단계 |
| Preservation | protected13458/frozen99 before-after SHA-size 동일; 허용 current mutable7은 읽지 않음 |

[관측 계약](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/OBSERVATION_CONTRACT.md), [전체 prospective oracle](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/PROSPECTIVE_CAPTURE_ORACLE.json), [소유권 표](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/COPY_OWNERSHIP_MATRIX.json), [향후 실행 증거 체크리스트](C:/Users/user/Desktop/RimMulti/QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/FUTURE_EXECUTION_PROVENANCE_CHECKLIST.json)에 실제 literal/type/order/source와 제한을 남겼습니다.

Scope 기대값은 DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED입니다. Exe/SHA는 부모 receipt, cwd/declared UserData는 별도 READ_ONLY child, task/result/stage/nonce는 원문 copied task에서 가져옵니다. 별도 child를 parent.role 교체로 만들지 않았습니다. Origin·plan 공백/Ω/opaque policy ID-revision/UTC .1234567Z·.0000000Z/경로 원문과 package order를 그대로 유지했습니다. Pair의 cross-policy 값은 데이터 복사 제어이며 실제 pairing/content equality나 nonce 인증이 아닙니다.

각 정상 fixture에서 BEFORE→caller task27와 실제 submitted descriptors 전체 변경→returned task27/approved7/policy/list detached copy 변경의 세 단계 전체 기대값과 raw UTF8는 같습니다. Edited 값을 re-admit/Capture 재호출/control plane에 적용하지 않습니다. 실제 read-only backing을 cast-mutate하거나 예외를 확인하는 부정 실행은 계획하지 않았습니다. IReadOnlyList 인터페이스 자체는 숨겨진 backing 증명이 아니므로 미래 source/PE 검토와 정상 detached-copy 관측을 분리했습니다.

Validated 기존 receipt/snapshot reference 보관은 Master 허용된 전략이며 새 receipt constructor를 요구하지 않았습니다. Caller task alias/returned backing 노출/approved7 canonical 대체/불필요한 receipt 재구성/누락된 task scalar-CLRwidth/implicit path normalization/Scope authority 과장/default DateTime parsing 위험9개를 독립 static·정상 회귀 기준으로 기록했습니다. 기존 IsValid 내부 path comparison의 Path.GetFullPath는 frozen source 사실입니다. 새 Capture의 direct IO/output normalization 금지와 구분하며 모든 transitive helper가 path calls0이라고 주장하지 않았습니다.

미래 new exact candidate QA가 별도 승인되면 proposed 한 run의 primary direct calls는 IssueAdmissionReceiptFromBytes8/IsValid8/Capture4, getter observation180입니다. Nested validation/selector/parser/normal policy digest와 grouped redaction helpers를 direct count와 구분했습니다. 현재 실행된 횟수는 모두0이고 label PASS·비율·E2를 만들지 않았습니다. New final QA build1/two fresh cultures는 **Master exact freeze/admission/new QA WP 뒤**에만 수행하는 제안입니다. Source/PDB/compiler/all references/input/oracle/callplan pre-pin, complete stdoutstderr/numericOSexit/actual loaded SHA-independentMVID/pre-post/full recursive first-before-second/all-after seal 및 immutable terminal proof가 필요합니다. Normal failure는 원문 보존·Master 보고이며 자체 expected 변경/재빌드/재실행 금지입니다.

이번 old frozen R25 selected Debug A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7/MVID5553a632-0557-433f-8840-bb12875cf577/PDBsource4of4 관측은 역사 lineage의 새 정적 metadata 확인입니다. 실제 R27 SHA/MVID/runtime identity를 뜻하지 않습니다. Master approved insertion scope의 byte166910/two fixed segments는 old frozen source와만 대조했습니다. 변경 중인 current production7의 before-after identity를 주장하지 않습니다.

R26 준비와 R25 S2 scoped PASS·QA newline CLOSED·S1 rawFAIL는 원문 보존했고 새 R27 PASS로 승계하지 않았습니다. Actual operator issuer/provider/private registry/current task equality(M05)/frontend·cwd·nativeGenroot·staged/content(M04/M06)/revoke(M07)는 OPEN입니다. Dedicated Server final Domain Authority, Engine002006/Pipeline007/schema/G-Q1/exact PlayerGlobal/physical split OPEN/Foundation HOLD/fullnativeE2 NOT_RELEASED/closure Master를 유지합니다. Source·기존 rawFAIL·governance·WP·schema·scheduler 수정0, OriginalSteam/Workshop/UserData/save/restore/install 접근0, known installed incident actor UNKNOWN/OPEN입니다.
'''
    REPORT.write_bytes(text.encode());rid=ack['result_id']
    common=dict(schema_version=1,producer='Sol',report_kind='INDEPENDENT_READ_ONLY_PREPARATION',wp_id=ack['wp_id'],wp_revision='S1',delivery_id=ack['delivery_id'],result_id=rid,verdict='INDEPENDENT_CAPTURE15_NORMAL_TYPED_RAW_COPY_PROVENANCE_PREPARATION_COMPLETE_R27_CANDIDATE_NOT_REVIEWED',protected_paths=13458,frozen_R25_files=99,all_preservation_matched=True,current_mutable7_not_read=True,getters15=15,normal_prospective_pairs=4,prospective_type_rows=976,prospective_raw_value_sets=40,caller_returned_task_mutation_fields=216,descriptor_actual_fields=7,descriptor_and_option_orders_distinct=True,frozen_source_spans=8,frozen_old_PDB_sources=[4,4],future_provenance_phases=7,construction_copy_risks=9,production_changes=0,QA_compiler_runner_factory_Capture_load_execute=0,native_Process_game_assets_copy=0,A_ongoing_R27_artifacts_read=False,actual_R27_candidate_verdict='NOT_REVIEWED_PENDING_NEW_EXACT_ADMISSION',original_R26_inputs_unchanged=True,governance_WP_schema_scheduler_closure_changes=0,runtime_e2_released=False,foundation='HOLD',limitations=['Preparation, not execution PASS','Old frozenR25 PE/PDB metadata only, not actual newR27 identity','Scope data-only, not operator auth/registration/native','IReadOnlyList backing needs future static review, no mutation exception probes','New QA execution requires Master exact freeze/newWP'])
    excluded={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
    paths=[p for p in Q.rglob('*') if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]+[REPORT];rows=[row(p) for p in sorted(paths,key=lambda x:str(x).lower())]
    write(Q/'EVIDENCE_MANIFEST.json',dict(**common,at=now(),artifact_count=len(rows),files=rows,exclusion='Primarygraph/transport cycle only; immutable ACK/report/source/prospective metadata included'))
    write(Q/'RESULT_INDEX.json',dict(**common,artifact_count=len(rows),report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ack=row(Q/'ACK_INITIAL.json'),primary_graph_complete='AFTER_LAST_COMPLETION_WRITE',report_delivery='PENDING_DIRECT_MASTER_RETURN'))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(result_id=rid,initial_ack=row(Q/'ACK_INITIAL.json'),ack=row(Q/'ACK.json'),report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),result_index=row(Q/'RESULT_INDEX.json'),initial_ack_pending_fields_unmodified=True))
    write(Q/'COMPLETION.json',dict(**common,status='COMPLETED',completed_at=now(),artifact_count=len(rows),report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),result_index=row(Q/'RESULT_INDEX.json'),ack_completion_binding=row(Q/'ACK_COMPLETION_BINDING.json'),primary_graph_complete=True,report_delivery='PENDING_DIRECT_MASTER_RETURN'))
    for d in rows:assert row(pathlib.Path(d['path']))==d
    for name in ['RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json']:
        for value in load(Q/name).values():
            if isinstance(value,dict) and {'path','sha256','bytes'}<=set(value):assert row(pathlib.Path(value['path']))==value
    result=dict(result_id=rid,status='PENDING_ONE_AUTHORIZED_TERMINAL_SEND',artifact_count=len(rows),report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json'));write(Q/'RETURN_PENDING.json',result);print(json.dumps(result,indent=2))
