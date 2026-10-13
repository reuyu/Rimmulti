from pathlib import Path
import json
import master_r29_s1_stop_prepare_s2_20261012 as m
def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];assert c['active_operation'] is None
 Q=Path(d['qa_root']);ack=m.read(Q/'ACK_INITIAL.json');ar=m.row(Q/'ACK_INITIAL.json');assert ar['sha256']=='F587A9EE427F338A6116329580AF6306C4EA69AC58A50F79162F21FE739FE7DA' and ar['bytes']==2440 and m.row(Q/'ACK.json')==dict(ar,path=str(Q/'ACK.json'))
 assert all(ack[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and ack['selected_mvid']==d['selected_mvid'] and ack['static_verdict']=='PENDING'
 for key in ['wp','baseline','freeze','selected','matching_PDB','source']:m.check(ack[key])
 bj=m.read(Path(d['baseline_path']));assert len(bj['files'])==15854
 for v in bj['files']:m.check(v)
 fm=m.read(Path(d['frozen_manifest']));assert len(fm['files'])==131
 for v in fm['files']:
  a=m.row(Path(v['frozen_path']));assert a['sha256']==v['sha256'] and a['bytes']==v['bytes']
 tool=m.read(Q/'bootstrap.TOOL.json');assert tool['exit_code']==0 and tool['first_streams_complete'] and tool['candidate_compiler_runner_native_calls']==0
 for k in ['script','stdout','stderr']:m.check(tool[k])
 pe=m.read(Q/'INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json');assert pe['original_source_fallback'] is False and pe['candidate_CLR_execution']==0
 for v in pe['candidates']:
  own=json.loads(m.read(m.C/f"MASTER_R31_{v['mode'].upper()}_PE_PDB_TOOL_20261012.json")['output']);m.check(v['DLL']);m.check(v['PDB']);assert v['PE']['mvid']==own['mvid'] and v['PE']['codeview']['guid']==own['codeviewGuid'] and v['portable_PDB']['pdb_guid']==own['pdbGuid']
  docs=v['portable_PDB']['documents'];assert len(docs)==4
  for z in docs:
   a=m.row(Path(z['frozen_source_path']));assert a['sha256']==z['actual_sha256']==z['expected_sha256'];assert any(w['expected']==a['sha256'] and w['path']==z['original_document_name'] for w in own['documents'])
 prov=m.read(Q/'METADATA_READER_DEFINITION_PROVENANCE.json')
 for v in prov['copies']:
  a=m.check(v['old_source_TEXT_only']);b=m.check(v['new_own_definition_module']);assert a['sha256']==b['sha256'] and not v['old_top_level_helper_executed_or_imported']
 snapshot=json.loads(m.read(m.C/'MASTER_SOL_R31_STATIC_ACK_ACTIVE_SNAPSHOT_20261012.json')['content'][0]['text'])['polls'][0];assert snapshot['thread']['status']['type']=='active' and snapshot['latestTurn']['status']=='inProgress' and snapshot['latestTurn']['id']==d['actual_new_turn_id']
 initial=[m.row(Q/name) for name in ['ACK_INITIAL.json','bootstrap.STDOUT.txt','bootstrap.STDERR.txt','bootstrap.TOOL.json','INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json','METADATA_READER_DEFINITION_PROVENANCE.json','RECOVERY_AND_AUTHORITY_AUDIT.json']]
 preservation=m.C/'MASTER_R31_STATIC_QA_INITIAL_ACK_METADATA_PRESERVATION_20261012.json';m.create(preservation,dict(at=m.now(),files=initial,ongoing_outputs_not_pinned=True,ACK_status_mirror_excluded=True,initial_metadata_only_not_terminal=True))
 p=m.C/'MASTER_SOL_R31_STATIC_ACK_VERIFICATION_20261012.json';v=dict(at=m.now(),delivery_id=d['delivery_id'],result_id=ack['result_id'],ACK=ar,bootstrap_tool=m.row(Q/'bootstrap.TOOL.json'),PE_PDB_source=m.row(Q/'INDEPENDENT_FROZEN_PE_PDB_IDENTITY.json'),copy_provenance=m.row(Q/'METADATA_READER_DEFINITION_PROVENANCE.json'),actual_snapshot=snapshot,protected_paths=15854,frozen_files=131,initial_metadata_preservation=m.row(preservation),master_verdict='ACK_VERIFIED_R31_INDEPENDENT_STATIC_IN_PROGRESS_VERDICT_PENDING',candidate_compiler_runner_native_global_adverse=0,no_prior_PASS_inherited=True,Foundation='HOLD',native_E2='NOT_RELEASED',monitor='PAUSED_HOURLY',guard_run='MASTER-R31-SOL-STATIC-ACK-20261012-01',guard_session=51844);m.create(p,v)
 d.update(result_id=ack['result_id'],ACK_sha256=ar['sha256'],ACK_verified=True,ACK_proof=str(p),status='ACK_VERIFIED_INDEPENDENT_STATIC_IN_PROGRESS_VERDICT_PENDING');c.update(sol_current_delivery=d,sol_status=d['status'],sol_current_result_id=ack['result_id'],sol_current_ack=dict(v,proof=m.row(p)),last_sol_cursor=snapshot['cursor'],updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['sol'].update(current_result_id=ack['result_id'],ack_verified=True,ack_sha256=ar['sha256'],ack_proof=str(p),current_status=d['status'],explicit_ack_pending=False,last_cursor=snapshot['cursor'],latest_progress_proof=str(p));m.save(m.H/'DISPATCHER_STATE.json',ds)
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');b['tasks'][-1]['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(preservation),sha256=m.row(preservation)['sha256']));b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 m.event(dict(v,event='SOL_R31_STATIC_ACK_BOUND_ACTUAL_ACTIVE_VERDICT_PENDING',proof=m.row(p)))
 m.append_delta('LOCAL-SOL-R31-INDEPENDENT-STATIC-ACK','OriginalSol '+d['delivery_id']+'/S1/result4daa915... ACK_INITIAL+mirrorF587A...2440 matches sameactualactive'+snapshot['latestTurn']['id']+'/cursor'+snapshot['cursor']+'. Master independently rehashed15854protected/131frozen/freshQAbyte-reader bothMVID-CV-PDB-source4of4 vs priorownPE/rawbootstrapexit0 firststreams. Definition-only oldreaders TEXT bytecopied/no oldtop-levelhelper execute. Initial7published metadata protected/ongoing outputs notpinned; allcandidatecompiler/native/global/adverse0notterminal/staticverdictPENDING/noR29PASSinherit/newWPduplicate0. A R31terminalreviewed revisionrequired/nextA NOTSENTpendingindependent/sameactualhourlyPAUSED/FoundationHOLD/nativeE2NOTRELEASED. Proof '+str(p))
 print('R31_ACK_VERIFIED_ACTIVE_STATIC_VERDICT_PENDING')
if __name__=='__main__':main()
