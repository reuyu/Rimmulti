from pathlib import Path
import json,hashlib,sys,datetime,ast,struct,uuid,shutil
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);p=p if p.is_absolute() else R/p;assert sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size')),str(p)
def refs(x):
 if isinstance(x,dict):
  if 'path' in x and 'sha256' in x and ('bytes' in x or 'size' in x):check(x)
  for v in x.values():refs(v)
 elif isinstance(x,list):
  for v in x:refs(v)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];T=Path(t['instruction_path']).parent;d=c['sol_current_delivery'];Q=Path(d['qa_root']);a=read(T/'COMPLETION.json');q=read(Q/'COMPLETION.json');lock=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json')
assert lock['status']=='LOCKED' and lock['run_id']=='MASTER-R28-DUAL-COMPLETE-20261012-01' and c['active_operation'] is None
assert all(a[k]==t[k] for k in ['dispatch_id','wp_id','wp_revision']) and a['envelope']==31 and a['status']=='COMPLETED'
assert all(q[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and q['result_id']==c['sol_current_result_id'] and q['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='FA5D86D37469181F9C2D1F728E9716DF511AE5F68CAEA09E9E93DFDEB8E53283'
refs(a);refs(q);refs(read(T/'RESULT_INDEX.json'));refs(read(Q/'RESULT_INDEX.json'));refs(read(Q/'ACK_COMPLETION_BINDING.json'))
ae=read(T/'EVIDENCE_MANIFEST.json');qe=read(Q/'EVIDENCE_MANIFEST.json');assert len(qe['files'])==38
for f in ae['task_documents']+qe['files']:check(f)
assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='AD2F58855FB9D4FC49C7068389F217BE498DD63093D0FA460CBA6025CB15A52B'
base=read(Path(d['baseline_path']));assert len(base['files'])==14045
for f in base['files']:check(f)
expected={f['path']:(f['sha256'],f['bytes']) for f in base['files']}
for name in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 z=read(Q/name);assert z['all_matched'] and z['protected_unique_paths']==14045 and {f['path']:(f['sha256'],f['bytes']) for f in z['protected_files']}==expected
 z=read(T/name);assert z['all_matched'] and {f['path']:(f['sha256'],f['bytes']) for f in z['files']}=={f['path']:(f['sha256'],f['bytes']) for f in t['production_fixed_files']}
sn=json.loads(read(C/'MASTER_SOL_R28_FRONTEND_ROUTE_COMPLETION_SNAPSHOT_20261012.json')['content'][0]['text'])['polls'][0];assert sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id'] and sn['latestTurn']['status']=='failed' and 'usage limit' in sn['latestTurn']['error']['message']
source=H/'bootstrap/verify_local_identity.py';node=next(z for z in ast.parse(source.read_text(encoding='utf8')).body if isinstance(z,ast.FunctionDef) and z.name=='mvid');ns={'struct':struct,'uuid':uuid};exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns)
il=read(Q/'STATIC_FRONTEND_IL_EVIDENCE.json');audit=read(Q/'STATIC_METADATA_AUDIT.json');modules={Path(f['path']).name:f for f in il['libraries']}
for f in il['libraries']:check(f);assert ns['mvid'](Path(f['path']))==f['mvid']
assert len(modules)==5 and audit['core_scan_errors']==0 and audit['core_scanned_methoddefs']==90840 and audit['worker_scanned_methoddefs']==532
verified=[];internal=[]
for module,methods in il['methods'].items():
 data=Path(modules[module]['path']).read_bytes()
 for method in methods:
  if not method['body_available']:
   assert int(method['rva'],16)==0;internal.append({'module':module,'token':method['method_token'],'flags':method['implementation_flags']});continue
  start=method['code_file_offset'];code=data[start:start+method['code_bytes']];assert hashlib.sha256(code).hexdigest().upper()==method['code_sha256'] and code.hex().upper()==method['raw_code_hex'].upper()
  joined=b''
  for ins in method['instructions']:
   raw=bytes.fromhex(ins['raw_hex']);pos=ins['file_offset'];assert data[pos:pos+len(raw)]==raw;joined+=raw
  assert joined==code;verified.append({'module':module,'token':method['method_token'],'code_sha256':method['code_sha256'],'bytes':len(code)})
assert len(audit['branch_validation'])==88 and all(z['branch_targets_valid'] for z in audit['branch_validation'])
core=il['methods']['Assembly-CSharp.dll'];cmd=next(m for m in core if m['method_token']=='0x060054D8');paths=next(m for m in core if m['method_token']=='0x06005522');root=next(m for m in core if m['method_token']=='0x060015F4');unity=next(m for m in il['methods']['UnityEngine.CoreModule.dll'] if m['method_token']=='0x060018E3')
assert cmd['code_sha256']=='74F28CE61BEC0CCE4C527B713B4FDB796D51731292A64A647B6996151D9B524A' and paths['code_sha256']=='AFF5BD726B688E874B45B12135B8952EF0E1588111D2917BB65FC6A76830DBD9' and not unity['body_available']
route=read(Q/'SOURCE_ORDER_AND_ROUTE.json');assert any(i['opcode']=='pop' for i in paths['instructions']) and 'not proven' in route['ordering']['native_frontier']
assert 'UNTESTED' in q['verdict'] and q['production_candidate_modification_rebuild']==q['QA_compiler_runner_build']==q['candidate_calls']==q['normal_adverse_rejection_lifecycle_executes']==0
patch=(T/'IMPLEMENTATION_PATCH_PROPOSAL.diff').read_text(encoding='utf8');assert '_pairedChildAdmissionReceipt' in patch and 'public static OperatorStartupAdmissionReceipt? PairedChildAdmissionReceipt' in patch and '--nonce=' in patch and 'childArgs = $"{childArgs} {baseArgs}"' in patch
froot=R/'Dispatcher/CANDIDATES/G05R28-7c324c51';assert not froot.exists();froot.mkdir();frozen=[]
ps={str(Path(f['path']).resolve()).lower():Path(f['path']) for f in a['artifacts']};ps[str((T/'COMPLETION.json').resolve()).lower()]=T/'COMPLETION.json'
for p in ps.values():
 dest=froot/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert sha(dest)==sha(p);frozen.append(dict(row(p),original_path=str(p),frozen_path=str(dest)))
fm=T/'MASTER_R28_OPERATOR_ROUTE_PROPOSAL_FREEZE_MANIFEST.json';assert not fm.exists();write(fm,{'at':at,'files':frozen,'scope':'IMMUTABLE_PROPOSAL_DOCS_NOT_NEW_ENGINE_CANDIDATE','R27_binary_unchanged':True})
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];write(C/'MASTER_R28_DUAL_COMPLETION_PRESERVATION_20261012.json',pres)
proof={'at':at,'guard_run':lock['run_id'],'guard_session':99760,'guard_pid':33196,'A_result_id':a['result_id'],'A_completion':row(T/'COMPLETION.json'),'A_evidence_count':len(ae['task_documents']),'A_artifacts_count':len(a['artifacts']),'A_proposal_freeze':row(fm),'A_proposal_frozen_files':len(frozen),'Sol_result_id':q['result_id'],'Sol_completion':row(Q/'COMPLETION.json'),'Sol_report':q['artifacts'][0],'Sol_evidence_count':38,'Sol_actual_snapshot':sn,'Sol_artifact_terminal':'COMPLETED_VERIFIED','Sol_runtime_operational_status':'FAILED_USAGE_LIMIT_NOTLOADED_SEPARATE_FROM_ARTIFACT_COMPLETION','protected_unique_paths':14045,'current_production9_fixed':True,'five_library_MVID_independently_matched':True,'raw_method_IL_and_instruction_bytes_verified':verified,'internalcall_no_managed_Awake_proof':internal,'88_branch_maps_declared_valid':True,'core_direct_scan_reported':90840,'core_decode_errors_reported':0,'Worker_direct_scan_reported':532,'tool_command_ledger':'Resolved absolute own scriptpaths; source invocation was relative; no literal OS argv proof','A_raw_IL_tool_provenance':'Producer opcode summaries only; no complete token-RVA-fileoffset-codehash/raw tool stream graph','verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','Master_candidate_build_execute':0,'native_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
p=C/'MASTER_GATE05_R28_DUAL_OPERATOR_ROUTE_VERIFICATION_20261012.json';assert not p.exists();write(p,proof);print(json.dumps({'status':proof['verification_status'],'A_artifacts':len(a['artifacts']),'A_frozen':len(frozen),'Sol_evidence':38,'raw_methods_verified':len(verified),'protected':14045,'Sol_runtime':'USAGE_FAILED_ARTIFACT_COMPLETED'},ensure_ascii=False))
