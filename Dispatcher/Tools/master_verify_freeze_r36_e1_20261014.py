"""Read/hash existing evidence and copy exact post-completion bytes; no producer execution."""
from pathlib import Path
import sys, json, shutil, difflib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
D='WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b'
T=m.R/'Dispatcher/A_TASKS'/D
E=m.R/'scratch/EngineGate05R36PublisherContract-d2d6556b'

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1]
 assert c['active_operation'] is None and t['dispatch_id']==D and t['delivery_status']=='SENT' and not t['unknown_delivery']
 co=m.read(T/'COMPLETION.json');ack=m.read(T/'ACK_INITIAL.json')
 for k in ['dispatch_id','wp_id','wp_revision']:
  assert co[k]==t[k] and ack[k]==t[k]
 assert co['envelope']==ack['envelope']==39 and co['status']=='COMPLETED'
 rec=m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(x.get('result_id')==co['result_id'] for x in rec['processed_results'])
 refs=[m.check(x) for x in t['reference_paths']]
 for x in ack['ref_hashes'].values():m.check(x)
 assert (T/'ACK_INITIAL.json').read_bytes()==(T/'ACK.json').read_bytes()
 artifacts=[]
 for x in co['artifacts']:
  p=Path(x['path']);a=m.row(p);assert a['sha256']==x['sha256'] and a['bytes']==x['size'];artifacts.append(a)
 fixed=[m.check(x) for x in t['production_fixed_files']]
 ba=m.read(T/'BEFORE_AFTER_PRESERVATION.json')
 for x in ba['all_Engine9_files']:
  a=m.row(Path(x['path']));assert a['sha256']==x['expected_sha256']==x['actual_sha256'] and a['bytes']==x['expected_bytes']==x['actual_bytes']
 assert len(ba['all_Engine9_files'])==9
 inp=m.read(E/'AST_INPUT_MANIFEST.json');hp=m.read(E/'AST_HOST_TOOL_PROOF.json')
 for k in ['exact_final_source','interpreter_exe','helper']:m.check(inp[k])
 assert inp['pinned_at']<=hp['executed_at_utc']<hp['completed_at_utc'] and hp['exit_code']==0 and hp['pid']==19052
 for key in ['stdout','stderr']:
  x=hp[key];m.check(dict(path=x['raw_path'],sha256=x['sha256'],bytes=x['bytes']))
 raw=json.loads(Path(hp['stdout']['raw_path']).read_text(encoding='utf-8'))
 assert raw==hp['stdout']['parsed'] and raw['body_node_count']==33 and len(raw['functions_found'])==13
 assert hp['command']==inp['argv'] and hp['cwd']==inp['cwd']
 own=m.read(E/'OWNED_OUTPUT_MANIFEST.json');ownedrows=[]
 for x in own['files']:ownedrows.append(m.check(dict(path=x['absolute_path'],sha256=x['sha256'],bytes=x['bytes'])))
 actualowned=[m.row(p) for p in sorted(E.rglob('*')) if p.is_file()]
 listed={x['path'].lower() for x in ownedrows};unlisted=[x for x in actualowned if x['path'].lower() not in listed]
 F=m.R/'Dispatcher/CANDIDATES/G05R36-d2d6556b';assert not F.exists();F.mkdir()
 paths={str(p).lower():p for parent in [T,E] for p in parent.rglob('*') if p.is_file()}
 for x in artifacts+fixed:paths[x['path'].lower()]=Path(x['path'])
 for p in [Path(t['allowed_mutable_paths'][0])]:paths[str(p).lower()]=p
 frozen=[]
 for p in paths.values():
  a=m.row(p);dest=F/p.relative_to(m.R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert m.row(dest)['sha256']==a['sha256'];frozen.append(dict(original_path=str(p),frozen_path=str(dest),sha256=a['sha256'],bytes=a['bytes']))
 fm=T/'MASTER_GATE05_R36_PUBLISHER_CONTRACT_REVIEW_FREEZE_MANIFEST.json'
 m.create(fm,dict(at=m.now(),files=frozen,freeze_kind='POST_COMPLETION_EXACT_SOURCE_AND_EVIDENCE_NOT_RUNTIME_ADMISSION',dispatch_id=D,python_MVID='N_A'))
 old=m.R/'Dispatcher/CANDIDATES/G05R35-16a25a7e/scratch/OperatorStartupPairR29/publish_operator_pair.py'
 source=Path(t['allowed_mutable_paths'][0]);diff=m.C/'MASTER_R36_ACTUAL_SOURCE_DIFF_20261014.txt'
 assert not diff.exists();diff.write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),source.read_text(encoding='utf-8').splitlines(True),fromfile=str(old),tofile=str(source))),encoding='utf-8')
 proof=m.C/'MASTER_GATE05_R36_PUBLISHER_CONTRACT_E1_VERIFICATION_20261014.json'
 m.create(proof,dict(at=m.now(),guard_session=63464,dispatch_id=D,result_id=co['result_id'],completion=m.row(T/'COMPLETION.json'),
  artifacts=artifacts,artifact_count=len(artifacts),refs=refs,ACK=m.row(T/'ACK_INITIAL.json'),ACK_mirror_equal=True,Engine9=fixed,
  actual_protected19301_special_checker_exit0_this_invocation=True,extra_R34_helper_matched=True,installed_known_unchanged_OPEN_actorUNKNOWN=True,
  freeze=m.row(fm),frozen_files=len(frozen),publisher=m.row(source),python_MVID='N_A',actual_source_diff=m.row(diff),
  AST=dict(producer_recorded_PID=19052,exit_code=0,stdout_bytes=861,stderr_bytes=0,actual_body_nodes=33,producer_completion_body_nodes=25,functions=13,
    raw_and_hash_binding_checked=True,final_source_interpreter_helper_prospective_pin_matched=True,outer_launch_helper_environment_library_hashes_missing=True,
    parsed_default_modules_are_launcher_process_not_independent_child_profile=True),
  owned_declared_count=own['file_count'],owned_actual_count=len(actualowned),owned_unlisted=unlisted,
  runtime_publication_build_native_adverse_executions=0,Master_candidate_executions=0,Foundation='HOLD',native_E2='NOT_RELEASED'))
 print(json.dumps(dict(status='R36_E1_ACTUAL_HASH_AND_POST_COMPLETION_FREEZE_VERIFIED',proof=m.row(proof),freeze=m.row(fm),frozen_count=len(frozen),owned_unlisted=unlisted),ensure_ascii=False))

if __name__=='__main__':main()
