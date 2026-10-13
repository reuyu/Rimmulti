from pathlib import Path
import json,hashlib,datetime,sys,shutil,re
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f.get('size',f.get('bytes')),str(p)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];T=Path(t['completion_path']).parent;x=read(T/'COMPLETION.json')
assert c['active_operation'] is None and all(x[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and x['envelope']==30 and x['status']=='COMPLETED'
assert len(x['artifacts'])==31
for f in x['artifacts']:check(f)
before=read(T/'ENGINE_FREEZE_BEFORE.json')['files'];after=read(T/'ENGINE_FREEZE_AFTER.json')['files'];assert len(before)==len(after)==9
prior=read(Path(t['preservation_policy']['prior_candidate_freeze_manifest']));lookup={f['original_path'].lower():f for f in prior['files']}
for f in before:
 old=lookup[f['path'].lower()];assert old['sha256']==f['sha256'];assert sha(Path(old['frozen_path']))==f['sha256'] and Path(old['frozen_path']).stat().st_size==f['size']
for f in after:check(f)
scope=read(Path(t['scope_baseline_path']));oldSource=Path(lookup[scope['source_before']['path'].lower()]['frozen_path']).read_bytes();raw=Path(scope['source_before']['path']).read_bytes();pos=166910;delta=len(raw)-len(oldSource)
assert delta==11937 and raw[:pos]==oldSource[:pos] and raw[pos+delta:]==oldSource[pos:]
insert=raw[pos:pos+delta].decode('utf8');assert 'public sealed class OperatorChildLaunchInputs' in insert and 'DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED' in insert
assert not any(p in insert for p in ['Process.','File.','Directory.','Path.GetFullPath','_activeAdmissionReceipt','_activeStartupConfig'])
# Parse source field names/CLR widths; no DLL/candidate execution or private reflection.
census=Path(t['production_fixed_files'][0]['path']);assert census.name=='EngineHostCensus.cs'
taskblock=census.read_text(encoding='utf8').split('public class ValidatorTask',1)[1].split('public class ValidatorResult',1)[0]
taskfields=re.findall(r'public (string|long|int|bool) (\w+)\s*=',taskblock);assert len(taskfields)==27
for typ,name in taskfields:
 assert re.search(r'private readonly '+typ+r' _'+name+r';',insert) and name+' = _'+name in insert and '_'+name+' = task.'+name in insert
assert 'Array.AsReadOnly(new string[]' in insert and 'GetDetachedTask()' in insert and 'GetApprovedChildDeclaration()' in insert
pes=[]
for mode,expected in [('DEBUG','44ba753c-6570-49d8-8068-4edf87a4e5d0'),('RELEASE','c9da01fd-6e6e-49c1-9bfd-9cb1d3a1a8a8')]:
 p=C/f'MASTER_R27_{mode}_PE_PDB_TOOL_20261012.json';tool=read(p);assert tool['exit_code']==0;pe=json.loads(tool['output']);assert pe['mvid']==expected and pe['codeviewMatched'] and len(pe['documents'])==4 and all(z['matched'] for z in pe['documents'])
 for f in pe['documents']:assert sha(Path(f['path']))==f['expected']==f['actual']
 pes.append(pe)
base=read(Path(c['sol_current_delivery']['baseline_path']));assert len(base['files'])==13458
for f in base['files']:check(f)
additional=read(Path(t['additional_completed_QA_preservation']['path']))
for f in additional['additional_QA_original_files']:check(f)
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
pp=T/'MASTER_R27_TERMINAL_PRESERVATION.json';assert not pp.exists();write(pp,pres)
tele=read(R/'scratch/EngineGate05R27ChildCapture/HOST_TELEMETRY.json');runchecks=[]
for run in tele['runs']:
 rp=Path(run['report_file']);out=read(rp);root=rp.parent
 assert run['exit_code']==0 and out['total_cases']==4 and out['issue_receipt_calls']==8 and out['capture_calls']==4 and out['all_cases_passed'] and len(out['cases'])==4
 for kind in ['stdout','stderr']:assert sha(root/(kind+'.txt'))==run[kind+'_sha256']
 graph=[root/f'graph_case_{i}_before.json' for i in range(1,5)];assert all(p.exists() for p in graph)
 runchecks.append({'culture':run['culture'],'pid':run['pid'],'exit':run['exit_code'],'PASS_labels':4,'direct_factory':8,'direct_Capture':4,'stdout_reported_bytes':run['stdout_bytes'],'stdout_actual_bytes':(root/'stdout.txt').stat().st_size,'stderr_actual_bytes':(root/'stderr.txt').stat().st_size,'graphs_before4_actual_keys':[list(read(p)) for p in graph],'graphs_after_present':bool(list(root.glob('*after*')))})
runner=R/'scratch/EngineGate05R27ChildCapture/Harness/Program.cs';runnertext=runner.read_text(encoding='utf8')
assert 'NotSupportedException' not in runnertext and 'IList<' not in runnertext
# Report claims readonly-list exception behavior, but inspected current runner contains no probe.
paths={Path(f['path']).resolve() for f in x['artifacts']}
for root in [T,R/'scratch/EngineGate05R27ChildCapture']:
 paths.update(p.resolve() for p in root.rglob('*') if p.is_file())
paths.update(Path(f['path']).resolve() for f in after)
for pe in pes:paths.update(Path(f['path']).resolve() for f in pe['documents'])
for mode in ['Debug','Release']:
 root=R/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472'
 paths.update(p.resolve() for p in root.iterdir() if p.is_file())
F=R/'Dispatcher/CANDIDATES/G05R27-cdc223f3';assert not F.exists();rows=[]
for p in sorted(paths):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
fm=T/'MASTER_GATE05_R27_CHILD_CAPTURE_REVIEW_FREEZE_MANIFEST.json';assert not fm.exists();write(fm,{'at':at,'dispatch_id':t['dispatch_id'],'result_id':x['result_id'],'kind':'POST_COMPLETION_MASTER_REVIEW_FREEZE_NEW_ENGINE_CANDIDATE_NOT_E2_PASS','files':rows})
vp=C/'MASTER_GATE05_R27_CHILD_CAPTURE_E1_VERIFICATION_20261012.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-R27-SOL-PREP-COMPLETE-20261012-01','guard_session':8532,'guard_pid':11168,'dispatch_id':x['dispatch_id'],'wp_id':x['wp_id'],'wp_revision':x['wp_revision'],'result_id':x['result_id'],'completion_sha256':sha(T/'COMPLETION.json'),'artifact_count':31,'before_after_rows':18,'current9_matched':True,'fixed_old_segments':2,'inserted_bytes':delta,'task_scalar_fields':27,'Debug_Release_PE_PDB':pes,'selected_sha256':'68BFE5105FA0471AAAF7943009703BB2599B39C5B572833507D6733BCE63CF64','selected_mvid':pes[0]['mvid'],'selected_pdb_sha256':'F0BC1B7D92F67593EA967F56A90EE302C76B920A46B98EF77219F7B884C47814','source_sha256':sha(Path(scope['source_before']['path'])),'preserved_paths':13458,'new_completed_QA_files_checked':len(additional['additional_QA_original_files']),'E1_run_checks':runchecks,'producer_expected_oracle_gap':'Partial old/proposed values disagree with actual runner inputs; missing independent full graph typed/raw comparison/postmutation graphs/compiler-allrefs/prospective pre-run and loaded identity proof','readonly_list_exception_claim':'REPORT_ONLY_CURRENT_RUNNER_NO_IST_MUTATION_OR_NOT_SUPPORTED_PROBE_FOUND_NOT_EXECUTED_PROOF','task_null_scalar_coalescing':'SourceOnly/unexecuted; normal fully specified nonnull inputs only admission','frozen_manifest':str(fm),'frozen_manifest_sha256':sha(fm),'frozen_files':len(rows),'frozen_root':str(F),'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','Master_candidate_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
write(vp,proof);print(json.dumps({'status':proof['verification_status'],'artifacts':31,'frozen':len(rows),'selected':proof['selected_sha256'],'MVID':proof['selected_mvid'],'E1coverage':'PARTIAL_NOT_FULL_PASS','QA_next':'NEW_EXACT_STATIC_AND_NORMAL_PURE_CAPTURE_ONLY'}))
