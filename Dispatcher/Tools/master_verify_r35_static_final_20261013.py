"""Master passive verification of original Sol terminal; no producer/candidate execution."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
Q=m.R/'QA-Tactical-Engine/GATE05-R35-PUBLISHER-INDEPENDENT-STATIC-S1-20261013'
def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];co=m.read(Q/'COMPLETION.json');idx=m.read(Q/'RESULT_INDEX.json');em=m.read(Q/'EVIDENCE_MANIFEST.json');bind=m.read(Q/'ACK_COMPLETION_BINDING.json');assert c['active_operation'] is None and d['delivery_id']==co['delivery_id'] and co['result_id']==c['sol_current_result_id'] and co['status']=='COMPLETED'
 assert m.row(Q/'COMPLETION.json')['sha256']=='E350EE70EE8874BBA19CA7F47254FCD236B9F1AC2ADCB5BDB5CEB57A06F1B793';assert len(em['files'])==58
 for v in em['files']+co['artifacts']:m.check(v)
 for k in ['report','manifest','initial_ACK','preservation','operational_qualifications']:m.check(idx[k])
 for k in ['initial_ACK','initial_mirror','resume_R1_ACK','manifest','index','report']:m.check(bind[k])
 for x in [idx,em,bind]:assert x['result_id']==co['result_id'] and x['delivery_id']==co['delivery_id']
 assert (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
 ba=m.read(Q/'PRESERVATION_BEFORE_AFTER_R2.json')
 for k in ['before','after','additional']:m.check(ba[k])
 bef=m.read(Path(ba['before']['path']));aft=m.read(Path(ba['after']['path']));extra=m.read(Path(ba['additional']['path']))
 assert bef['protected_files']==aft['protected_files'] and bef['frozen_files']==aft['frozen_files'];base=m.read(Path(d['baseline_path']));assert bef['protected_files']==base['files']
 for k in ['partial_manifest','additional_manifest']:m.check(extra[k])
 assert extra['partial_files']==m.read(Path(extra['partial_manifest']['path']))['files'] and extra['additional_files']==m.read(Path(extra['additional_manifest']['path']))['files']
 allrows=bef['protected_files']+bef['frozen_files']+extra['partial_files']+extra['additional_files'];unique={}
 for v in allrows:
  key=v['path'].lower()
  if key in unique:assert unique[key]['sha256']==v['sha256'] and unique[key]['bytes']==v['bytes']
  unique[key]=v
 assert len(unique)==19274 and len(extra['partial_files'])==16 and len(extra['additional_files'])==45
 for v in unique.values():m.check(v)
 fm=m.read(Path(d['frozen_manifest']));assert len(fm['files'])==34
 for v in fm['files']:m.check(v,'frozen_path')
 steps=[]
 for p in Q.glob('*.TOOL.json'):
  t=m.read(p);assert t['exit_code']==0 and t['first_streams_complete']
  for k in ['script','input_pin','stdout','stderr']:
   if k in t:m.check(t[k])
  if 'input_pin' in t:
   pin=m.read(Path(t['input_pin']['path']));assert pin['at']<=t['started_at']
   for v in pin['files']:m.check(v)
  steps.append(dict(tool=m.row(p),exit=0,stdout_bytes=t['stdout']['bytes'],stderr_bytes=t['stderr']['bytes']))
 assert len(steps)==5 and m.read(Q/'finalize_r2_seal.TOOL.json')['stdout']['bytes']==1136
 ret=m.read(Q/'RETURN_TOOL_PROOF.json');assert not ret.get('isError',False);delivery=m.read(Q/'DELIVERY_STATUS.json');assert not delivery['actual_tool_isError']
 for v in delivery['postseal_actual_artifacts']:m.check(v)
 a=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];assert a['wp_revision']=='GATE05-R35-PUBLISHER' and a['status'].startswith('COMPLETED')
 for v in a['production_fixed_files']:m.check(v)
 provenance=m.read(Q/'PROVENANCE_REVIEW.json');assert provenance['artifact_count']==20 and provenance['owned_inventory_diff']['frozen_actual_count']==15
 for v in provenance['artifacts']:
  if 'bytes' in v:m.check(v,'frozen_path' if 'frozen_path' in v else 'path')
 req=m.read(Q/'MINIMAL_R36_CORRECTIVE_REQUIREMENTS.json');assert req['requirement_count']==8 and co['publisher_Engine_compiler_fixture_native_adverse']==0 and co['optional_query_retries']==0 and co['review_reruns']==0
 raw=m.read(m.C/'MASTER_SOL_R35_STATIC_COMPLETION_ACTUAL_SNAPSHOT_20261013.json');snap=json.loads(raw['content'][0]['text'])['polls'][0];assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
 installed=Path(r'C:/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/WarEconomy.WorkerBridge.PoC/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll');assert m.row(installed)['sha256']=='BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61'
 out=m.C/'MASTER_SOL_R35_STATIC_FINAL_INDEPENDENT_EVIDENCE_VERIFICATION_20261013.json';m.create(out,dict(at=m.now(),result_id=co['result_id'],delivery_id=co['delivery_id'],actual_snapshot=snap,completion=m.row(Q/'COMPLETION.json'),report=idx['report'],evidence58=True,protected19229_frozen34_partial16_additional45_unique19274_actual_rehash=True,full_beforeafter_lists_matched=True,steps=steps,actual_terminal_return=m.row(Q/'RETURN_TOOL_PROOF.json'),Engine_fixed=True,installed_known_unchanged_OPEN_actorUNKNOWN=True,R36_requirements8_source_only=True,optionalquery_retries0_review_reruns0=True,publisher_Engine_compiler_fixture_native_adverse0=True,Master_candidate_build_execution0=True,policy_schema_exactconstant_NOT_required_on_actual_config_receipt_digest_route=True,source_counts_not_runtime_tests=co['source_counts'],nativeE2='NOT_RELEASED',Foundation='HOLD',guard_session=56970));print(json.dumps(dict(status='R35_STATIC_TERMINAL_VERIFIED_NOT_RUNTIME_PASS',proof=m.row(out)),ensure_ascii=False))
if __name__=='__main__':sys.stdout.reconfigure(encoding='utf-8');main()
