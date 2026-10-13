from pathlib import Path
import json
import master_r29_s1_stop_prepare_s2_20261012 as m

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];assert c['active_operation'] is None
 Q=Path(d['qa_root']);a=m.read(Q/'ACK_INITIAL.json');ar=m.row(Q/'ACK_INITIAL.json')
 assert ar['sha256']=='A50AE909E62719528753EFA2C7485A83D77EB473239CA86BB22641DB487FA4EE' and ar['bytes']==3013 and (Q/'ACK.json').read_bytes()==(Q/'ACK_INITIAL.json').read_bytes()
 assert a['delivery_id']==d['delivery_id'] and a['wp_id']==d['wp_id'] and a['wp_revision']==d['wp_revision'] and a['initial_compiler_runner_candidate_calls']==0 and not a['old_PASS_inherited']
 s=json.loads(m.read(m.C/'MASTER_SOL_R33_INDEPENDENT_S1_ACK_SNAPSHOT_20261013.json')['content'][0]['text'])['polls'][0]
 assert s['latestTurn']['id']==d['actual_new_turn_id'] and s['latestTurn']['status']=='inProgress' and s['thread']['status']['type']=='active'
 for k in ['WP','baseline','supplement','freeze','selected','PDB','source','oracle_binding']:m.check(a[k])
 base=m.read(Path(d['baseline_path']));pres=m.read(Q/'PRESERVATION_BEFORE.json')
 def ids(v):return {r['path'].lower():(r['sha256'],r['bytes']) for r in v}
 assert ids(base['files'])==ids(pres['protected_files']) and len(base['files'])==17099
 for v in base['files']:m.check(v)
 for key,count in [('frozen_files',71),('prep_terminal_files',54),('outside_helper_files',6)]:
  assert len(pres[key])==count
  for v in pres[key]:m.check(v)
 tool=m.read(Q/'bootstrap.TOOL.json');assert tool['exit_code']==0 and tool['first_streams_complete']
 for k in ['script','stdout','stderr']:m.check(tool[k])
 # Compare the immutable candidate/PDB/source identity with prior independent
 # Master file-byte PE/PDB proof; do not execute the producer reader or candidate.
 pe=m.read(Q/'FROZEN_PE_PDB_IDENTITY.json');assert len(pe['candidates'])==2
 for v in pe['candidates']:
  m.check(v['DLL']);m.check(v['PDB']);assert not v['candidate_loaded']
  expected='adb6cbc8-c4f9-4436-b137-d550d683f493' if v['mode']=='Debug' else 'c739a55b-d61c-43b0-a16d-6e38edf57e62'
  assert v['PE']['mvid']==expected and v['PE']['codeview']['guid']==v['portable_PDB']['pdb_guid']
  docs=v['portable_PDB']['documents'];assert len(docs)==4
  for x in docs:assert m.row(Path(x['frozen_source_path']))['sha256']==x['expected_sha256']==x['actual_sha256'] and x['matched']
 refs=[m.row(m.C/('MASTER_R33_'+mode+'_PE_PDB_TOOL_20261013.json')) for mode in ['DEBUG','RELEASE']]
 verdict='ACK_VERIFIED_EXACT_R33_INDEPENDENT_STATIC_AND_FRESH_NORMAL_QA_IN_PROGRESS'
 p=m.C/'MASTER_SOL_R33_INDEPENDENT_S1_ACK_VERIFICATION_20261013.json';v=dict(at=m.now(),delivery_id=d['delivery_id'],result_id=a['result_id'],ACK=ar,actual_snapshot=s,master_verdict=verdict,protected_unique_paths_actually_rehashed=17099,frozen_files_rehashed=71,prep_terminal_rehashed=54,outside_helpers_rehashed=6,bootstrap_actual_exit=0,bootstrap_tool=m.row(Q/'bootstrap.TOOL.json'),QA_PE_source4of4=m.row(Q/'FROZEN_PE_PDB_IDENTITY.json'),prior_Master_independent_PE_PDB_proofs=refs,selected_sha256=a['selected']['sha256'],selected_mvid=a['selected_mvid'],initial_execution0_is_initial_not_future_verdict=True,passive_review_filename_json_vs_md='READONLY_LOCATOR_NO_CANDIDATE_FAILURE_NO_NEW_EXECUTION_ADMISSION',candidate_verdict='PENDING',nativeE2='NOT_RELEASED',Foundation='HOLD',scheduler='PAUSED_HOURLY_UNCHANGED',no_new_WP_or_duplicate=True,guard_run='MASTER-R33-INDEPENDENT-ACK-20261013-01',guard_session=62883)
 m.create(p,v);d.update(status=verdict,ACK_verified=True,ACK_sha256=ar['sha256'],result_id=a['result_id'],ACK_proof=str(p));c.update(sol_current_delivery=d,sol_status=verdict,last_sol_cursor=s['cursor'],sol_snapshot_cursor=s['cursor'],updated_at=m.now());m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['sol'].update(current_status=verdict,last_cursor=s['cursor'],current_runtime_status='ACTUAL_ACTIVE_IN_PROGRESS',last_result_id=a['result_id'],last_ACK_proof=str(p));m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(v,event='SOL_R33_INDEPENDENT_S1_ACK_VERIFIED',proof=m.row(p)))
 m.append_delta('LOCAL-SOL-R33-INDEPENDENT-S1-ACK',verdict+'. Original sameactualactive turn/cursor26/result'+a['result_id']+' initialACKA50AE.../3013 matched. Master actualrehash17099+frozen71+prepterminal54+outsidehelpers6/bootstrapexit0/raw matched. BothPE/PDBsource4of4 matches priorMaster independently boundexactcandidate/source unchanged; noMastercandidatebuild/run. Initialcompiler/runner/native0 notfutureQAverdict. Purebuild1/twopositiveprocesses existingWP only, oldPASSnotinherited/staticresourceclaimedlimitsindependentreview; noextraWP/duplicate/schedulerchange. Passivefilename.json vs actual.md readonlysearch is notcandidatefailure. High4OPEN/FoundationHOLD/fullnativeE2NOTRELEASED/samehourlyPAUSED. Proof '+str(p))
 print(json.dumps(dict(status=verdict,protected_paths=17099,proof=m.row(p))))

if __name__=='__main__':main()
