from pathlib import Path
import json,tomllib
import master_r29_s1_stop_prepare_s2_20261012 as m
def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];assert c['active_operation'] is None and d['delivery_id']=='SOL-GATE05-R32-CUSTODY-INDEPENDENT-S1-20261013-01' and not d.get('ACK_verified',False)
 Q=Path(d['qa_root']);ack=m.read(Q/'ACK_INITIAL.json');ar=m.row(Q/'ACK_INITIAL.json');assert ar['sha256']=='FCA87F6EDADAC42F112BB9FB9365D525202F6D8CB4F40CF5B340A5B0B262272A' and ar['bytes']==2649 and m.row(Q/'ACK.json')==dict(ar,path=str(Q/'ACK.json'))
 assert all(ack[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and ack['selected_mvid']==d['selected_mvid'] and ack['verdict']=='PENDING' and ack['initial_build_runner_calls']==0 and ack['production_build_modify']==0 and ack['native_execution']==0 and not ack['prior_PASS_inherited']
 for key in ['wp','baseline','freeze','selected','PDB','source','oracle_template_binding']:m.check(ack[key])
 bj=m.read(Path(d['baseline_path']));assert len(bj['files'])==16026
 for v in bj['files']:m.check(v)
 fm=m.read(Path(d['frozen_manifest']));assert len(fm['files'])==64
 for v in fm['files']:
  a=m.row(Path(v['frozen_path']));assert a['sha256']==v['sha256'] and a['bytes']==v['bytes']
 before=m.read(Q/'PRESERVATION_BEFORE.json');assert before['protected_count']==16026 and before['frozen_count']==64 and before['all_matched']
 assert {v['path'].lower():(v['sha256'],v['bytes']) for v in before['protected_files']}=={v['path'].lower():(v['sha256'],v['bytes']) for v in bj['files']}
 assert {v['path'].lower():(v['sha256'],v['bytes']) for v in before['frozen_files']}=={v['frozen_path'].lower():(v['sha256'],v['bytes']) for v in fm['files']}
 tool=m.read(Q/'bootstrap.TOOL.json');assert tool['exit_code']==0 and tool['first_streams_complete']
 for k in ['script','stdout','stderr']:m.check(tool[k])
 pe=m.read(Q/'FROZEN_PE_PDB_IDENTITY.json')
 for v in pe['candidates']:
  own=json.loads(m.read(m.C/f"MASTER_R32_{v['mode'].upper()}_PE_PDB_TOOL_20261013.json")['output']);m.check(v['DLL']);m.check(v['PDB']);assert not v['candidate_loaded'] and v['PE']['mvid']==own['mvid'] and v['PE']['codeview']['guid']==own['codeviewGuid'] and v['portable_PDB']['pdb_guid']==own['pdbGuid'] and not v['portable_PDB']['original_mutable_source_read']
  docs=v['portable_PDB']['documents'];assert len(docs)==4
  for z in docs:
   a=m.row(Path(z['frozen_source_path']));assert a['sha256']==z['actual_sha256']==z['expected_sha256'];assert any(w['expected']==a['sha256'] and w['path']==z['original_document_name'] for w in own['documents'])
 prov=m.read(Q/'METADATA_DEFINITION_PROVENANCE.json')
 for v in prov['copies']:
  a=m.check(v['source_TEXT_only']);b=m.check(v['new_definition']);assert a['sha256']==b['sha256']
 snapshot=json.loads(m.read(m.C/'MASTER_SOL_R32_ACK_SNAPSHOT_20261013.json')['content'][0]['text'])['polls'][0];assert snapshot['thread']['status']['type']=='active' and snapshot['latestTurn']['status']=='inProgress' and snapshot['latestTurn']['id']==d['actual_new_turn_id']
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf-8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
 b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];comp=m.row(Path(t['completion_path']));assert comp['sha256']==t['completion_sha256'] and t['status']=='COMPLETED_REVIEWED_FRESH_INDEPENDENT_QA_PENDING'
 installed=m.read(m.C/'MASTER_R32_POSTDISPATCH_PRESERVATION_VERIFICATION_20261012.json')['installed_known_unchanged_OPEN_actorUNKNOWN'];m.check(installed)
 initial=[m.row(Q/name) for name in ['ACK_INITIAL.json','bootstrap.STDOUT.txt','bootstrap.STDERR.txt','bootstrap.TOOL.json','FROZEN_PE_PDB_IDENTITY.json','METADATA_DEFINITION_PROVENANCE.json','RECOVERY_AND_AUTHORITY_AUDIT.json','PRESERVATION_BEFORE.json','ORACLE_TEMPLATE_TEXT_INSPECTION.json']]
 preservation=m.C/'MASTER_R32_QA_INITIAL_ACK_METADATA_PRESERVATION_20261013.json';m.create(preservation,dict(at=m.now(),files=initial,ongoing_outputs_not_pinned=True,ACK_status_mirror_excluded=True,initial_metadata_only_not_terminal=True))
 p=m.C/'MASTER_SOL_R32_ACK_VERIFICATION_20261013.json';v=dict(at=m.now(),delivery_id=d['delivery_id'],result_id=ack['result_id'],ACK=ar,bootstrap_tool=m.row(Q/'bootstrap.TOOL.json'),PE_PDB_source=m.row(Q/'FROZEN_PE_PDB_IDENTITY.json'),copy_provenance=m.row(Q/'METADATA_DEFINITION_PROVENANCE.json'),actual_snapshot=snapshot,protected_paths=16026,frozen_files=64,initial_metadata_preservation=m.row(preservation),master_verdict='ACK_VERIFIED_R32_INDEPENDENT_STATIC_AND_FRESH_POSITIVE_PURE_QA_IN_PROGRESS_VERDICT_PENDING',initial_QA_candidate_compiler_runner_native_calls=0,current_execution_verdict='PENDING_NOT_TERMINAL',no_prior_PASS_inherited=True,A_terminal_completion_unchanged=comp,installed_known_unchanged_OPEN_actorUNKNOWN=installed,Foundation='HOLD',native_E2='NOT_RELEASED',monitor='ACTUAL_PAUSED_HOURLY',guard_run='MASTER-R32-SOL-ACK-20261013-01',guard_session=98776);m.create(p,v)
 d.update(result_id=ack['result_id'],ACK_sha256=ar['sha256'],ACK_verified=True,ACK_proof=str(p),status='ACK_VERIFIED_INDEPENDENT_STATIC_FRESH_POSITIVE_QA_IN_PROGRESS_VERDICT_PENDING');c.update(sol_current_delivery=d,sol_status=d['status'],sol_current_result_id=ack['result_id'],sol_current_ack=dict(v,proof=m.row(p)),last_sol_cursor=snapshot['cursor'],sol_snapshot_cursor=snapshot['cursor'],updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['sol'].update(current_result_id=ack['result_id'],ack_verified=True,ack_sha256=ar['sha256'],ack_proof=str(p),current_status=d['status'],explicit_ack_pending=False,last_cursor=snapshot['cursor'],latest_progress_proof=str(p));m.save(m.H/'DISPATCHER_STATE.json',ds)
 b['tasks'][-1]['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(preservation),sha256=m.row(preservation)['sha256']));b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 m.event(dict(v,event='SOL_R32_ACK_BOUND_ACTUAL_ACTIVE_VERDICT_PENDING',proof=m.row(p)))
 m.append_delta('LOCAL-SOL-R32-INDEPENDENT-STATIC-FRESH-POSITIVE-ACK','OriginalSol '+d['delivery_id']+'/S1/result46a87b... ACK_INITIAL+mirrorFCA87F...2649 matched sameactualactive'+snapshot['latestTurn']['id']+'/cursor'+snapshot['cursor']+'. Master independently rehashed16026protected/64frozen/freshQAbyte-reader bothMVID-CV-PDB-source4of4 versus priorownPE/rawbootstrapexit0 fullfirststreams. Initial9published metadata protected; ongoingoutputs notpinned/statusACKmirrorexcluded. Initial compiler/runner/candidate/native0 NOT terminal; freshstatic+Pair6Capture4 QA inprogress/normalverdictPENDING/no oldPASSinherit/newWPduplicate0. A R32terminal reviewed/unchangedoriginalcompletion/installedknownOPENunknown. Sameactual hourlyPAUSED; High4OPEN/nativeE2NOTRELEASED/FoundationHOLD. Proof '+str(p))
 print('R32_ACK_VERIFIED_ACTIVE_VERDICT_PENDING')
if __name__=='__main__':main()
