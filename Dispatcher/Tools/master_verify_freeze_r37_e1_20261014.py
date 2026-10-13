"""Read/hash R37 producer evidence and preserve exact post-completion source; never executes it."""
from pathlib import Path
import sys,json,shutil,difflib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
T=m.R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a'
E=m.R/'scratch/EngineGate05R37PublisherFinal-de39916a'

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];co=m.read(T/'COMPLETION.json');ack=m.read(T/'ACK_INITIAL.json')
 assert c['active_operation'] is None and t['wp_revision']=='GATE05-R37-PUBLISHER-FINAL' and t['delivery_status']=='SENT' and not t['unknown_delivery']
 for k in ['dispatch_id','wp_id','wp_revision']:assert t[k]==co[k]==ack[k]
 assert co['envelope']==ack['delivery_envelope_revision']==40 and co['status']=='COMPLETED'
 assert not any(x.get('result_id')==co['result_id'] for x in m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
 refs=[m.check(x) for x in t['reference_paths']];assert len(refs)==9
 for k in ['instruction','release','contract','scope_baseline']:
  p=Path(ack[k+'_path']);assert m.row(p)['sha256']==ack[k+'_sha256']
 assert (T/'ACK_INITIAL.json').read_bytes()==(T/'ACK.json').read_bytes()
 arts=[]
 for x in co['artifacts']:
  a=m.row(Path(x['path']));assert a['sha256']==x['sha256'] and a['bytes']==x['size'];arts.append(a)
 fixed=[m.check(x) for x in t['production_fixed_files']]
 ba=m.read(T/'BEFORE_AFTER_PRESERVATION.json')
 for x in ba['all_Engine9_files']:
  a=m.row(Path(x['path']));assert a['sha256']==x['expected_sha256']==x['actual_sha256'] and a['bytes']==x['expected_bytes']==x['actual_bytes']
 pin=m.read(E/'AST_INPUT_MANIFEST.json');hp=m.read(E/'AST_HOST_TOOL_PROOF.json');ex=hp['execution']
 for key in ['target_source','child_tool_script']:m.check(pin[key])
 i=pin['interpreter'];m.check(dict(path=i['executable_path'],sha256=i['sha256'],bytes=i['bytes']))
 assert pin['pinned_at_utc']<=ex['start_time_utc']<ex['end_time_utc'] and ex['exit_code']==0 and ex['pid']==15208
 for key in ['stdout','stderr']:m.check(hp['streams'][key])
 raw=json.loads(Path(hp['streams']['stdout']['path']).read_text(encoding='utf-8'));assert raw['body_node_count']==36 and raw['function_count']==16 and raw['bytes']==40358
 assert raw['functions']==hp['child_observed_ast']['functions'] and raw['child_sys_path']==hp['child_observed_environment']['child_sys_path'] and raw['child_modules_loaded']==hp['child_observed_environment']['child_modules_loaded']
 owned=m.read(E/'OWNED_OUTPUT_MANIFEST.json');listed=[]
 for x in owned['files']:listed.append(m.check(dict(path=x['absolute_path'],sha256=x['sha256'],bytes=x['bytes'])))
 actual=[m.row(p) for p in sorted(E.rglob('*')) if p.is_file()];listed_paths={x['path'].lower() for x in listed};extra=[x for x in actual if x['path'].lower() not in listed_paths]
 F=m.R/'Dispatcher/CANDIDATES/G05R37-de39916a';assert not F.exists();F.mkdir()
 paths={str(p).lower():p for root in [T,E] for p in root.rglob('*') if p.is_file()}
 for x in arts+fixed:paths[x['path'].lower()]=Path(x['path'])
 frozen=[]
 for p in paths.values():
  a=m.row(p);out=F/p.relative_to(m.R);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out);assert m.row(out)['sha256']==a['sha256'];frozen.append(dict(original_path=str(p),frozen_path=str(out),sha256=a['sha256'],bytes=a['bytes']))
 fm=T/'MASTER_GATE05_R37_PUBLISHER_FINAL_REVIEW_FREEZE_MANIFEST.json';m.create(fm,dict(at=m.now(),dispatch_id=t['dispatch_id'],files=frozen,freeze_kind='POST_COMPLETION_SOURCE_AND_RAW_NOT_RUNTIME_ADMISSION',python_MVID='N_A'))
 pub=Path(t['allowed_mutable_paths'][0]);old=m.R/'Dispatcher/CANDIDATES/G05R36-d2d6556b/scratch/OperatorStartupPairR29/publish_operator_pair.py';diff=m.C/'MASTER_R37_ACTUAL_SOURCE_DIFF_20261014.txt';assert not diff.exists();diff.write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),pub.read_text(encoding='utf-8').splitlines(True),fromfile=str(old),tofile=str(pub))),encoding='utf-8')
 proof=m.C/'MASTER_GATE05_R37_PUBLISHER_FINAL_E1_VERIFICATION_20261014.json';m.create(proof,dict(at=m.now(),guard_session=91210,dispatch_id=t['dispatch_id'],result_id=co['result_id'],completion=m.row(T/'COMPLETION.json'),artifact_count=len(arts),artifacts=arts,refs=refs,ACK=m.row(T/'ACK_INITIAL.json'),ACK_mirror_equal=True,fixed_Engine9=fixed,freeze=m.row(fm),frozen_files=len(frozen),publisher=m.row(pub),python_MVID='N_A',actual_source_diff=m.row(diff),
  AST=dict(PID=15208,exit_code=0,stdout3022_stderr0=True,body36_functions16=True,source_interpreter_checker_pin_matched=True,actual_child_sys_path_and_module_list_matched=True,outer_helper_environment_library_hashes_not_bound=True),
  owned_declared=len(listed),owned_actual=len(actual),owned_unlisted=extra,protected19452_special_checker='PENDING_FINAL_RETURN_NOT_ASSERTED',Master_candidate_build_publication_native_adverse_executions=0,native_E2='NOT_RELEASED',Foundation='HOLD'))
 print(json.dumps(dict(status='R37_RAW_AND_EXACT_FREEZE_VERIFIED_BASELINE_CHECKER_PENDING',proof=m.row(proof),freeze=m.row(fm),frozen_files=len(frozen),owned_extra=extra),ensure_ascii=False))

if __name__=='__main__':main()
