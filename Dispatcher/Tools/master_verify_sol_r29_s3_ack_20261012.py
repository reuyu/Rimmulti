from pathlib import Path
import importlib.util,json,sys,tomllib
P=Path(__file__).with_name('master_r29_s1_stop_prepare_s2_20261012.py');sp=importlib.util.spec_from_file_location('m',P);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def main():
 cs=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');assert cs['active_operation'] is None
 d=cs['sol_current_delivery'];assert d['wp_revision']=='S3' and d['delivery_status']=='SENT'
 Q=Path(d['qa_root']);ack=m.read(Q/'ACK_INITIAL.json');ackrow=m.row(Q/'ACK_INITIAL.json')
 assert ackrow['sha256']=='E62D7A47248E015DBB1C293723108E8368D544F0221B6CC3028122AFB382FE31' and ackrow['bytes']==2892
 assert ack['wp_id']==d['wp_id'] and ack['wp_revision']=='S3' and ack['delivery_id']==d['delivery_id']
 assert ack['result_id']=='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012-8d682aff4ebd4996a12529142c0d7431'
 assert ack['normal_verdict']=='PENDING' and ack['initial_QA_builds_candidate_calls']==0
 for k in ['wp','master_admission','baseline','frozen_manifest','selected','matching_PDB','exact_newtonsoft']:m.check(ack[k])
 assert ack['selected']['sha256']==d['selected_sha256'] and ack['selected_mvid']==d['selected_mvid']
 snap=json.loads(m.read(m.C/'MASTER_SOL_R29_S3_ACK_SNAPSHOT_20261012.json')['content'][0]['text'])['polls'][0]
 assert snap['thread']['status']['type']=='active' and snap['latestTurn']['status']=='inProgress' and snap['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
 template=m.R/'Dispatcher/Tools/MASTER_R29_S3_REVIEW_SETUP_TEMPLATE.py';assert (Q/'review_setup.py').read_bytes()==template.read_bytes()
 assert m.row(template)['sha256']=='2878AE853B4B271A615EFA56A7E0C0568466F9FC4A1EE33B4E1DA3D7DA034EC7'
 pre=m.read(Q/'PREFLIGHT_PROOF.json');assert all(pre[k] is True for k in ['byte_equal','original_S1_unchanged','EOF_preserved','exhaustive8_replacements_verified','PREP_original_S1_unchanged','baseline14365_schema','frozen132_bytes_schema','dependencies_exist'])
 exits=m.read(Q/'INITIAL_TOOL_EXIT_PROOF.json');assert exits['preflight']['exit_code']==0 and exits['metadata']['exit_code']==0 and exits['both_exits_assertions_inspected_before_dependent_steps'] is True
 before=m.read(Q/'PRESERVATION_BEFORE.json');assert before['all_matched'] and before['protected_unique_paths']==14365
 baseline=m.read(Path(d['baseline_path']));assert before['protected_files']==baseline['files']
 for v in before['protected_files']:m.check(v)
 for v in before['frozen_files']:m.check(v)
 assert len(before['frozen_files'])==132
 lineage=m.read(Q/'R29_FROZEN_LINEAGE.json');assert lineage['candidate_executed'] is False and lineage['original_helper_top_level_executed'] is False
 pe=[]
 for mode,qa in zip(['DEBUG','RELEASE'],lineage['candidates']):
  own=m.read(m.C/('MASTER_R29_'+mode+'_PE_PDB_TOOL_20261012.json'));assert own['exit_code']==0;v=json.loads(own['output'])
  assert qa['mvid']==v['mvid'] and qa['codeview_guid']==v['codeviewGuid']==qa['guid']==v['pdbGuid']
  assert len(qa['documents'])==len(v['documents'])==4
  expected={x['path']:x for x in v['documents']}
  for doc in qa['documents']:
   o=expected[doc['path']];assert doc['matched'] and doc['pdb_hash']==doc['actual_sha256']==o['expected']==o['actual'];assert m.row(Path(doc['frozen_source_path']))['sha256']==doc['pdb_hash']
  assert m.row(Path(qa['dll']))['sha256']==qa['dll_sha256'];assert m.row(Path(qa['dll']).with_suffix('.pdb'))['sha256']==qa['pdb_sha256'];pe.append(dict(mode=mode,mvid=qa['mvid'],source_documents=4,CodeView_PDB_match=True))
 evidence=[m.row(Q/name) for name in ['ACK_INITIAL.json','review_setup.py','PREFLIGHT_PROOF.json','PREFLIGHT_STDOUT.txt','PREFLIGHT_STDERR.txt','INITIAL_TOOL_EXIT_PROOF.json','INITIAL_METADATA_STDOUT.txt','INITIAL_METADATA_STDERR.txt','PRESERVATION_BEFORE.json','R29_FROZEN_LINEAGE.json']]
 scheduler=tomllib.loads(Path(r'C:\Users\user\.codex\automations\wareconomy-master\automation.toml').read_text(encoding='utf-8'));assert scheduler['status']=='PAUSED' and scheduler['rrule']=='FREQ=HOURLY;INTERVAL=1'
 proof=m.C/'MASTER_SOL_R29_S3_ACK_VERIFICATION_20261012.json'
 summary=dict(at=m.now(),guard_run='MASTER-R29-S3-ACK-20261012-01',guard_session=52418,guard_pid=35528,delivery_id=d['delivery_id'],wp_id=d['wp_id'],wp_revision='S3',result_id=ack['result_id'],ACK_INITIAL=ackrow,actual_snapshot=snap,evidence=evidence,protected_paths=14365,frozen_files=132,metadata_pe_pdb=pe,master_verdict='ACK_VERIFIED_R29_S3_BYTE_EXACT_METADATA_INITIAL_IDENTITY_PASS_NORMAL_QA_IN_PROGRESS',initial_QA_compiler_runner_candidate_calls=0,current_normal_verdict='PENDING',not_final_normal_or_native_PASS=True,Master_candidate_execution=0,native_E2='NOT_RELEASED',Foundation='HOLD',new_WP_sent=False,duplicate_sent=False,closure_changed=False,scheduler_actual=scheduler)
 m.create(proof,summary)
 cs.update(sol_current_ack=dict(ack,Master_verification=m.row(proof)),sol_current_result_id=ack['result_id'],sol_status='IN_PROGRESS_ACK_VERIFIED_NORMAL_PENDING',last_sol_cursor=snap['cursor'],sol_runtime_observation=snap,updated_at=m.now());d.update(status='IN_PROGRESS_ACK_VERIFIED_NORMAL_PENDING',result_id=ack['result_id'],ack_verified=True,ack_sha256=ackrow['sha256'],ack_proof=m.row(proof),actual_snapshot=snap);cs['sol_latest_delivery']=d;m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',cs)
 ds=m.read(m.H/'DISPATCHER_STATE.json');e=ds['endpoints']['sol'];e.update(current_result_id=ack['result_id'],ack_verified=True,ack_sha256=ackrow['sha256'],ack_proof=str(proof),latest_ack_verification=str(proof),explicit_ack_pending=False,current_status='INDEPENDENT_R29_S3_NORMAL_QA_IN_PROGRESS_ACK_VERIFIED',current_runtime_status='ACTUAL_SAME_S3_TURN_ACTIVE_AND_ACK_VERIFIED',last_runtime_observation_cursor=snap['cursor'],last_cursor=snap['cursor'],last_observation_at=m.now(),latest_progress_proof=str(proof));ds['updated_at']=m.now();m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(summary,event='SOL_R29_S3_ACK_INITIAL_METADATA_VERIFIED'))
 m.append_delta('LOCAL-SOL-R29-S3-ACK-INITIAL-METADATA-VERIFIED',summary['master_verdict']+'. Original same active turn/cursor187/exact delivery S3/result '+ack['result_id']+'. Master rehash14365/frozen132/byteexact template4775/EOF+PREP-S1 and initialpreflight-metadata exit0 checked. Both actual PE MVID/CodeView/PDB/source4of4 match prior independently obtained Master metadata. Independent normal runner/positive fulltypedraw-copy preparation continues; initial build/candidate0, normal verdict PENDING; no inherited/whole-gate PASS/new WP/duplicate/closure. QA metadata/text2 defects remain OPEN until final fresh QA disposition; source High3 and Engine/Pipeline/GQ1 OPEN/Foundation HOLD/native E2 NOT RELEASED. A R30 NOT SENT pending findings/same actual hourly PAUSED/direct Sol reporting. Proof '+str(proof))
 print(json.dumps(dict(status=summary['master_verdict'],proof=m.row(proof),new_WP_sent=False),ensure_ascii=False))
if __name__=='__main__':main()
