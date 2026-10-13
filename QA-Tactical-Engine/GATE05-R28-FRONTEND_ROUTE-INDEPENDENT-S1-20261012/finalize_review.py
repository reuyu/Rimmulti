from bootstrap_review import *
import os
REPORT=R/'docs/QA_EngineHost_Gate05_R28_Frontend_Route_Independent_S1_20261012.md'
EXCLUDE={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
if __name__=='__main__':
    before=load(Q/'PRESERVATION_BEFORE.json')
    after=preservation()
    assert before['protected_files']==after['protected_files']
    assert before['frozen_files']==after['frozen_files'] and before['managed_files']==after['managed_files']
    write(Q/'PRESERVATION_AFTER.json',after)
    e=load(Q/'STATIC_FRONTEND_IL_EVIDENCE.json')
    assert e['references_scan']['scanned_methoddefs']==90840 and not e['references_scan']['errors']
    assert not load(Q/'WORKER_DIRECT_ROUTE_CALLS.json')['direct_capture_calls']
    audit=load(Q/'STATIC_METADATA_AUDIT.json')
    assert len(audit['branch_validation'])==88 and len(audit['independent_mvid_reader_matches'])==5
    for row in load(Q/'R28_FROZEN_LINEAGE.json')['candidates']:
        assert row['guid']==row['codeview_guid'] and len(row['documents'])==4
        assert all(x['matched'] for x in row['documents'])
    ack=load(Q/'ACK_INITIAL.json')
    assert (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
    requirement=dict(at=now(),wp=pin(W),result_id=ack['result_id'],baseline=pin(B),
      own_result='READ_ONLY_STATIC_AUDIT_COMPLETE_CONNECTED_OPERATOR_ROUTE_REQUIRED_NATIVE_UNTESTED',
      actual_core_methods_scanned=90840,core_direct_references=18,worker_methods_scanned=532,worker_capture_calls=0,
      selected=pin(DLL),source=pin(SRC),pdb=pin(PDB),managed_libraries=e['libraries'],
      independent_mvid_readers_agree=5,codeview_pdb_source_documents_both_modes='4/4 EACH',
      protected_before_after_paths=14045,frozen83=True,managed4=True,
      bootstrap_install_before_attach='SOURCE_AND_IL_OBSERVED',AddComponent_native_Awake_timing='UNVERIFIED',
      core_savedatafolder_consumer='OBSERVED_STATIC',actual_native_root_cwd='UNTESTED',
      operator_owned_child_provider_pairing_registration='MISSING_IN_AUDITED_SOURCE_NOT_GLOBAL_NEGATIVE_PROOF',
      implementation_requirements=7,A_R28_proposal_read=False,new_schema_flags_carrier_adopted=False,
      production_modification_rebuild=0,qa_runner_compiler=0,assembly_load_reflection_invocations=0,native_game_Process_Unity_lifecycle=0,normal_adverse_rejection_executes=0,
      missing_evidence=['actual operator producer endpoint and protected transport','child effective cwd/early config-prefs root','native AddComponent/Awake ordering','current child registration lifetime and full authority binding','actual loaded content and stage semantic/native E2'],
      limitations=['Raw IL direct-reference scan excludes reflection/native/unaudited executable/other mods patches','Generic TypeSpec signatures retain exact hex, not full signature decompilation','No OS argv parsing or culture comparison test; sample argv outcomes static-derived only','No native secret leakage observed: argv logging path is static evidence','Pure R27 scoped PASS/QA dependency closure retained as prior Master disposition; no inherited integration/native PASS'],
      master_authority='Final Server domain authority; MD125-132, accepted ADR006B core control; no new PKI; Master closure/release',
      foundation='HOLD',full_native_E2='NOT_RELEASED',closure_changed=False)
    write(Q/'FINAL_REQUIREMENT_AND_MASTER_CORRECTION_BINDING.json',requirement)
    write(Q/'METADATA_TOOL_EXIT_PROOF.json',dict(at=now(),description='Observed functions exec_command returns for own read-only Python metadata tools; no managed runner or compilation',
      tools=[dict(script=s,os_exit_code=0,argv=['python','-B',str(Q/s)],cwd=str(R)) for s in ['bootstrap_review.py','extract_frontend.py','scan_routes.py','source_and_lineage.py','review_routes.py','implementation_requirements.py']],
      bootstrap_session_id=11533,scan_session_id=44278,full_raw_il_files=[pin(p) for p in Q.glob('*.il.txt')],
      failed_tool_parse_before_report_patch='functions JS SyntaxError before any tool execution/mutation; corrected report patch succeeded; not candidate failure',
      metadata_only=True))
    files=[pin(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in EXCLUDE and '__pycache__' not in p.parts]
    files.append(pin(REPORT))
    write(Q/'EVIDENCE_MANIFEST.json',dict(schema_version=1,at=now(),result_id=ack['result_id'],files=files,excluded_cycle_files=sorted(EXCLUDE)))
    manifest=pin(Q/'EVIDENCE_MANIFEST.json')
    index=dict(schema_version=1,at=now(),result_id=ack['result_id'],wp_id=ack['wp_id'],wp_revision='S1',delivery_id=ack['delivery_id'],status='COMPLETED_READ_ONLY_STATIC_AUDIT_NATIVE_UNTESTED',
      report=pin(REPORT),evidence_manifest=manifest,evidence_files=len(files),protected_unique_paths=14045,
      primary_artifacts=[pin(Q/n) for n in ['ACK_INITIAL.json','STATIC_FRONTEND_IL_EVIDENCE.json','SOURCE_ORDER_AND_ROUTE.json','IMPLEMENTATION_REVIEW_REQUIREMENTS.json','STATIC_METADATA_AUDIT.json','PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json','FINAL_REQUIREMENT_AND_MASTER_CORRECTION_BINDING.json']],
      report_delivery='PENDING',master_adoption='PENDING',builds=0,calls=0,foundation='HOLD',native_E2='NOT_RELEASED')
    write(Q/'RESULT_INDEX.json',index)
    binding=dict(at=now(),result_id=ack['result_id'],ack_initial=pin(Q/'ACK_INITIAL.json'),ack=pin(Q/'ACK.json'),report=pin(REPORT),manifest=manifest,index=pin(Q/'RESULT_INDEX.json'),original_pending_fields_not_rewritten=True)
    write(Q/'ACK_COMPLETION_BINDING.json',binding)
    write(Q/'RETURN_PENDING.json',dict(at=now(),result_id=ack['result_id'],endpoint='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174',host='local',status='PENDING_TERMINAL_DIRECT_SEND_AFTER_COMPLETION',unknown_delivery=False,no_automatic_retry=True))
    for r in files:
        p=Path(r['path']);assert pin(p)==r
    completion=dict(schema_version=1,at=now(),producer='Sol',wp_id=ack['wp_id'],wp_revision='S1',delivery_id=ack['delivery_id'],result_id=ack['result_id'],
       status='COMPLETED',verdict='READ_ONLY_STATIC_AUDIT_COMPLETE_CONNECTED_OPERATOR_ROUTE_REQUIRED_NATIVE_UNTESTED',
       artifacts=[pin(REPORT),manifest,pin(Q/'RESULT_INDEX.json'),pin(Q/'ACK_INITIAL.json'),pin(Q/'ACK_COMPLETION_BINDING.json'),pin(Q/'STATIC_FRONTEND_IL_EVIDENCE.json'),pin(Q/'SOURCE_ORDER_AND_ROUTE.json'),pin(Q/'IMPLEMENTATION_REVIEW_REQUIREMENTS.json'),pin(Q/'PRESERVATION_BEFORE.json'),pin(Q/'PRESERVATION_AFTER.json')],
       evidence_files=len(files),protected_unique_paths=14045,frozen_files=83,managed_files=4,all_preserved=True,
       libraries_mvids_independently_bound=5,codeview_pdb_source='Debug4/4 Release4/4',core_methoddefs=90840,core_decode_errors=0,worker_methoddefs=532,worker_Capture_direct_calls=0,
       implementation_requirements=7,production_candidate_modification_rebuild=0,QA_compiler_runner_build=0,candidate_calls=0,normal_adverse_rejection_lifecycle_executes=0,
       A_R28_proposal_read=False,limitations=requirement['limitations']+requirement['missing_evidence'],
       report_delivery='PENDING',master_disposition='PENDING',new_schema_flags_carrier_adopted=False,
       engine_pipeline_schema_GQ1='OPEN',foundation='HOLD',full_native_E2='NOT_RELEASED',closure_changed=False)
    tmp=Q/'COMPLETION.json.tmp';target=Q/'COMPLETION.json'
    assert not target.exists() and not tmp.exists()
    write(tmp,completion);os.replace(tmp,target) # Last primary graph write, atomic own-directory publication.
    for r in completion['artifacts']:assert pin(Path(r['path']))==r
    print(json.dumps(dict(result_id=ack['result_id'],evidence_files=len(files),protected=14045,report=pin(REPORT),manifest=manifest,index=pin(Q/'RESULT_INDEX.json'),completion=pin(target),all_preserved=True)))

