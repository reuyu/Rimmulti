"""Read/hash exact R38 producer source and E1 metadata; no publisher execution."""
from pathlib import Path
import sys,json,shutil,difflib,ast
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');t=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];T=Path(t['exact_message_path']).parent;E=Path(t['new_owned_E1_root']);co=m.read(T/'COMPLETION.json');ack=m.read(T/'ACK_INITIAL.json')
 assert c.get('active_operation') is None and t['wp_revision']=='GATE05-R38-PUBLISHER-BOUNDARIES' and t['delivery_status']=='SENT' and not t['unknown_delivery']
 for k in ['dispatch_id','wp_id','wp_revision']:assert t[k]==co[k]==ack[k]
 assert co['envelope']==ack['delivery_envelope_revision']==41 and co['status']=='COMPLETED'
 assert not any(x.get('result_id')==co['result_id'] for x in m.read(m.R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
 refs=[m.check(x) for x in t['reference_paths']];assert len(refs)==11
 for k in ['instruction','release','contract','scope_baseline']:assert m.row(Path(ack[k+'_path']))['sha256']==ack[k+'_sha256']
 assert (T/'ACK_INITIAL.json').read_bytes()==(T/'ACK.json').read_bytes()
 arts=[]
 for x in co['artifacts']:
  a=m.row(Path(x['path']));assert a['sha256']==x['sha256'] and a['bytes']==x['size'];arts.append(a)
 fixed=[m.check(x) for x in t['production_fixed_files']]
 for x in m.read(T/'BEFORE_AFTER_PRESERVATION.json')['all_Engine9_files']:
  a=m.row(Path(x['path']));assert a['sha256']==x['expected_sha256']==x['actual_sha256'] and a['bytes']==x['expected_bytes']==x['actual_bytes']
 pin=m.read(E/'AST_INPUT_MANIFEST.json');hp=m.read(E/'AST_HOST_TOOL_PROOF.json');ex=hp['childExecution']
 for k in ['targetPublisher','childScript','launcherScript']:
  x=pin[k];m.check(dict(path=x['path'],sha256=x['sha256'],bytes=x['size_bytes']))
 i=pin['pythonInterpreter'];m.check(dict(path=i['executablePath'],sha256=i['sha256'],bytes=i['sizeBytes']))
 assert pin['pinnedAtUtc']<=ex['startedAtUtc']<ex['completedAtUtc'] and ex['exitCode']==0 and ex['pid']==9668
 assert hp['inputManifestSha256']==m.row(E/'AST_INPUT_MANIFEST.json')['sha256']
 for k in ['stdout','stderr']:m.check(dict(path=ex[k+'RawPath'],sha256=ex[k+'RawSha256'],bytes=ex[k+'RawBytes']))
 raw=m.read(Path(ex['stdoutRawPath']));assert raw==hp['astVerificationSummary'] and raw['top_level_function_count']==18 and raw['size_bytes']==43666
 source=Path(t['allowed_mutable_paths'][0]);tree=ast.parse(source.read_bytes(),filename=str(source));assert sum(1 for _ in ast.walk(tree))==raw['total_ast_nodes'] and len([x for x in tree.body if isinstance(x,ast.FunctionDef)])==18
 modrows=[]
 for x in pin['launcherModuleObservations']:modrows.append(m.check(dict(path=x['path'],sha256=x['sha256'],bytes=x['size_bytes'])))
 owned=m.read(E/'OWNED_OUTPUT_MANIFEST.json');listed=[m.check(dict(path=x['absolute_path'],sha256=x['sha256'],bytes=x['bytes'])) for x in owned['files']];actual=[m.row(p) for p in sorted(E.rglob('*')) if p.is_file()];listedpaths={x['path'].lower() for x in listed};extra=[x for x in actual if x['path'].lower() not in listedpaths]
 F=m.R/'Dispatcher/CANDIDATES/G05R38-10b9846e';assert not F.exists();F.mkdir();paths={str(p).lower():p for root in [T,E] for p in root.rglob('*') if p.is_file()}
 for x in arts+fixed:paths[x['path'].lower()]=Path(x['path'])
 frozen=[]
 for p in paths.values():
  a=m.row(p);out=F/p.relative_to(m.R);out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,out);assert m.row(out)['sha256']==a['sha256'];frozen.append(dict(original_path=str(p),frozen_path=str(out),sha256=a['sha256'],bytes=a['bytes']))
 fm=T/'MASTER_GATE05_R38_PUBLISHER_BOUNDARIES_REVIEW_FREEZE_MANIFEST.json';m.create(fm,dict(at=m.now(),dispatch_id=t['dispatch_id'],files=frozen,freeze_kind='POST_COMPLETION_SOURCE_AND_RAW_NOT_RUNTIME_ADMISSION',python_MVID='N_A'))
 old=m.R/'Dispatcher/CANDIDATES/G05R37-de39916a/scratch/OperatorStartupPairR29/publish_operator_pair.py';diff=m.C/'MASTER_R38_ACTUAL_SOURCE_DIFF_20261014.txt';assert not diff.exists();diff.write_text(''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True),source.read_text(encoding='utf-8').splitlines(True),fromfile=str(old),tofile=str(source))),encoding='utf-8')
 p=m.C/'MASTER_GATE05_R38_PUBLISHER_BOUNDARIES_E1_VERIFICATION_20261014.json';m.create(p,dict(at=m.now(),guard_session=26686,dispatch_id=t['dispatch_id'],result_id=co['result_id'],completion=m.row(T/'COMPLETION.json'),artifact_count=len(arts),artifacts=arts,refs=refs,ACK=m.row(T/'ACK_INITIAL.json'),ACK_mirror_equal=True,fixed_Engine9=fixed,freeze=m.row(fm),frozen_files=len(frozen),publisher=m.row(source),python_MVID='N_A',actual_source_diff=m.row(diff),AST=dict(PID=9668,exit_code=0,stdout=ex['stdoutRawBytes'],stderr=ex['stderrRawBytes'],functions18_totalnodes4926=True,source_interpreter_child_launcher_pins_matched=True,launcher_claimed_modulecount=pin['launcherModuleObservationsCount'],launcher_actual_pinned_rows=len(modrows),actual_child_importfile_context_absent=True),owned_declared=len(listed),owned_actual=len(actual),owned_unlisted=extra,protected19598_actual_checker_exit0_chunk='4e2214',Master_candidate_build_publication_native_adverse_executions=0,native_E2='NOT_RELEASED',Foundation='HOLD'))
 print(json.dumps(dict(status='R38_EXACT_SOURCE_E1_FROZEN_NOT_RUNTIME_ADMITTED',proof=m.row(p),freeze=m.row(fm),frozen_files=len(frozen),owned_extra=extra),ensure_ascii=False))

if __name__=='__main__':main()
