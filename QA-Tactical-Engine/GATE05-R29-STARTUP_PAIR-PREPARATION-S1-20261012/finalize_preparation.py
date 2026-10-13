from bootstrap_review import *
import os
REPORT=R/'docs/QA_EngineHost_Gate05_R29_Startup_Pair_Preparation_S1_20261012.md'
EXCLUDE={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
if __name__=='__main__':
    before=load(Q/'PRESERVATION_BEFORE.json');after=preservation()
    assert before['protected_files']==after['protected_files'] and before['frozen83']==after['frozen83']
    assert before['current_fixed_Census_csproj']==after['current_fixed_Census_csproj']
    write(Q/'PRESERVATION_AFTER.json',after)
    a=load(Q/'ACK_INITIAL.json');assert (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
    o=load(Q/'PRE_RUN_EXPECTED_ORACLE.json');audit=load(Q/'NORMAL_DATA_CONSISTENCY_AUDIT.json')
    assert len(o['prospective_cases'])==6 and audit['total_typed_rows']==1236
    for row in load(Q/'PROSPECTIVE_INPUT_LITERAL_MANIFEST.json')['files']:assert pin(Path(row['path']))==row
    fixedobj=load(Q/'PRESERVATION_HASH_SCOPE_NOTE.json')
    assert len(fixedobj['mandatory_baseline_fixed_generated_obj4'])==4
    write(Q/'FINAL_SCOPE_AND_REQUIREMENT_BINDING.json',dict(at=now(),result_id=a['result_id'],wp=pin(W),contract=pin(C),master_R28review=pin(MR),baseline=pin(B),
       prospective_oracle=pin(Q/'PRE_RUN_EXPECTED_ORACLE.json'),normal_cases=6,typed_hierarchical_rows=1236,expected_phase_conditions=18,literal_input_expectation_files=30,
       APIs='4readonly properties+2freshoriginal7getters+1PUREadmission contract; actual tokens pending new candidate',
       original_descriptor7_and_used_clone7_distinct=True,own_fixture_locator_rebind_explicit=True,first4historical_raw14_byte_exact=True,
       producer_build_QA_compile_candidate_bootstrap_Unity_native_Process_adverse_rejection_execution=0,
       mutable_R29_implementation_source_publisher_outputs_read=False,protected_fixed_obj4_hash_only=True,
       own_metadata_regex_failure_exit1_preserved=True,corrected_metadata_exit0=True,metadata_data_checks_not_executable_test_PASS=True,
       protected_unique_paths=14105,frozen_files=83,current_fixed_Census_csproj_matched=2,
       R28_artifact_acceptance_and_operational_usagefailure_separate=True,R29_candidate_verdict='NOT_REVIEWED',
       operator_issuer_currenttask_native_facts='PENDING',full_native_E2='NOT_RELEASED',foundation='HOLD',Engine_Pipeline_schema_GQ1='OPEN',closure_changed=False))
    files=[pin(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in EXCLUDE and '__pycache__' not in p.parts]
    files.append(pin(REPORT))
    write(Q/'EVIDENCE_MANIFEST.json',dict(schema_version=1,at=now(),result_id=a['result_id'],files=files,excluded_cycle_files=sorted(EXCLUDE)))
    index=dict(schema_version=1,at=now(),result_id=a['result_id'],wp_id=a['wp_id'],wp_revision='S1',delivery_id=a['delivery_id'],status='PREPARATION_COMPLETED_NO_EXECUTABLE_VERDICT',report=pin(REPORT),evidence_manifest=pin(Q/'EVIDENCE_MANIFEST.json'),evidence_files=len(files),protected_unique_paths=14105,
      primary_artifacts=[pin(Q/n) for n in ['ACK_INITIAL.json','PRE_RUN_EXPECTED_ORACLE.json','FIELD_AND_API_MATRIX.json','PROVENANCE_AND_NATIVE_BOUNDARY_CRITERIA.json','PROSPECTIVE_INPUT_LITERAL_MANIFEST.json','NORMAL_DATA_CONSISTENCY_AUDIT.json','PRESERVATION_HASH_SCOPE_NOTE.json','PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']],
      report_delivery='PENDING',master_adoption='PENDING',normal_execution_assertions=0,actual_R29candidate_verdict='NOT_REVIEWED',full_native_E2='NOT_RELEASED',foundation='HOLD')
    write(Q/'RESULT_INDEX.json',index)
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),result_id=a['result_id'],ACK_INITIAL=pin(Q/'ACK_INITIAL.json'),ACK=pin(Q/'ACK.json'),report=pin(REPORT),manifest=pin(Q/'EVIDENCE_MANIFEST.json'),index=pin(Q/'RESULT_INDEX.json'),initial_pending_fields_immutable=True))
    write(Q/'RETURN_PENDING.json',dict(at=now(),result_id=a['result_id'],endpoint='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174',host='local',status='PENDING_TERMINAL_DIRECT_SEND',unknown_delivery=False,no_duplicate_retry=True))
    for row in files:assert pin(Path(row['path']))==row
    comp=dict(schema_version=1,at=now(),producer='Sol',wp_id=a['wp_id'],wp_revision='S1',delivery_id=a['delivery_id'],result_id=a['result_id'],status='COMPLETED',verdict='INDEPENDENT_NORMAL_ORACLE_PREPARATION_COMPLETE_R29_CANDIDATE_NOT_REVIEWED_NO_EXECUTION_PASS',
      artifacts=[pin(REPORT),pin(Q/'EVIDENCE_MANIFEST.json'),pin(Q/'RESULT_INDEX.json'),pin(Q/'ACK_INITIAL.json'),pin(Q/'ACK_COMPLETION_BINDING.json'),pin(Q/'PRE_RUN_EXPECTED_ORACLE.json'),pin(Q/'FIELD_AND_API_MATRIX.json'),pin(Q/'PROVENANCE_AND_NATIVE_BOUNDARY_CRITERIA.json'),pin(Q/'PRESERVATION_BEFORE.json'),pin(Q/'PRESERVATION_AFTER.json')],
      evidence_files=len(files),protected_unique_paths=14105,frozen_files=83,current_fixed_Census_csproj=2,all_preserved=True,normal_cases_prepared=6,typed_hierarchical_rows=1236,expected_phase_graph_conditions=18,literal_inputs=30,
      schema='NEW_ADOPTED_AUXILIARY_PAIR4_CONFIG14_DESCRIPTOR7_TASK27_UNCHANGED',
      production_QA_compiler_producer_candidate_bootstrap_Unity_native_Process_adverse_rejection_executes=0,
      mutable_R29_implementation_read=False,fixed_baseline_obj4_hash_only=True,
      limits=['Preparation only, no current R29 API tokens/build/normal tests/PASS','Publisher fixture locator paths rebound prospectively, first4raw14 unchanged/oldoriginal7 sidecar preserved','Actual operator authorization/ACL/host/native argv/root/cwd/Awake timing unobserved','Actual current task pairing/registration/protectedreceiver/M05launch/consume/native profile are separate future gates','Own source regex metadata failure preserved and corrected, not candidate failure','Contract method names only; actual candidate source/signatures pending Master admission'],
      report_delivery='PENDING',master_disposition='PENDING',R29_candidate_verdict='NOT_REVIEWED',Foundation='HOLD',full_native_E2='NOT_RELEASED',Engine_Pipeline_schema_GQ1='OPEN',closure_changed=False)
    tmp=Q/'COMPLETION.json.tmp';target=Q/'COMPLETION.json';assert not tmp.exists() and not target.exists()
    write(tmp,comp);os.replace(tmp,target)
    for row in comp['artifacts']:assert pin(Path(row['path']))==row
    print(json.dumps(dict(result_id=a['result_id'],evidence_files=len(files),report=pin(REPORT),manifest=pin(Q/'EVIDENCE_MANIFEST.json'),index=pin(Q/'RESULT_INDEX.json'),completion=pin(target),protected=14105,all_preserved=True,execution=0)))

