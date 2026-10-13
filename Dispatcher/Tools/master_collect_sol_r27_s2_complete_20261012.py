from pathlib import Path
import json,hashlib,datetime,sys,ast,struct,uuid,collections
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
def refs(x):
 if isinstance(x,dict):
  if all(k in x for k in ['path','sha256','bytes']):check(x)
  for y in x.values():refs(y)
 elif isinstance(x,list):
  for y in x:refs(y)
def eq(expected,actual,path='$'):
 assert type(expected)==type(actual),(path,type(expected),type(actual))
 n=1
 if isinstance(expected,dict):
  assert list(expected)==list(actual),path
  for k in expected:n+=eq(expected[k],actual[k],path+'.'+k)
 elif isinstance(expected,list):
  assert len(expected)==len(actual),path
  for i,(a,b) in enumerate(zip(expected,actual)):n+=eq(a,b,path+'['+str(i)+']')
 else:assert expected==actual,(path,expected,actual)
 return n
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');assert c['active_operation'] is None;d=c['sol_current_delivery'];Q=Path(d['qa_root']);x=read(Q/'COMPLETION.json');rr=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert all(x[k]==d[k] for k in ['delivery_id','wp_id','wp_revision','selected_sha256','selected_mvid']) and x['result_id']==c['sol_current_result_id'] and x['status']=='COMPLETED' and not any(z.get('result_id')==x['result_id'] for z in rr['processed_results'])
assert sha(Q/'COMPLETION.json')=='0066F232BEACA142483F0E76FE468DB43D435CD809C363DA490AAD24B9034AB5'
em=read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==361 and sha(Q/'EVIDENCE_MANIFEST.json')=='D99E28E0699BF84E87BC62065D26AACF87CF49AAA2BDB758C9F8B6F61BB09379'
for f in em['files']:check(f)
refs(x);refs(read(Q/'RESULT_INDEX.json'));refs(read(Q/'ACK_COMPLETION_BINDING.json'))
assert sha(Q/'ACK_INITIAL.json')==c['sol_current_ack']['initial_ACK']['sha256']==sha(Q/'ACK.json')
sf=C/'MASTER_SOL_R27_CHILD_CAPTURE_S2_COMPLETION_SNAPSHOT_20261012.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0];assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
base=read(Path(d['baseline_path']));assert len(base['files'])==13674
for f in base['files']:check(f)
for name in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 p=read(Q/name);assert p['protected_unique_paths']==13674 and {f['path']:(f['sha256'],f['bytes']) for f in p['files']}=={f['path']:(f['sha256'],f['bytes']) for f in base['files']}
oracle=read(Q/'NORMAL_EXPECTED_ORACLE.json');assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')=='5961CD18DA05B67F6DE40DA8A6EBB289D94ACF85054D57FB31FE4B8C5530C4C7';assert sha(Q/'PRIMARY_NORMAL_CALLPLAN.json')=='CED0429567C53FED699CF57D6E77E005EAF1BAD62667ADE6842B318D88FA326A'
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');comp=summary['compiler'];refs(comp);assert comp['exit_code']==0 and comp['build_attempts']==1 and comp['productionbuilds']==0 and comp['stdout']['bytes']==34168 and comp['stderr']['bytes']==0
admit=read(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json');assert len(admit['pins'])==139 and datetime.datetime.fromisoformat(admit['at'])<datetime.datetime.fromisoformat(comp['started_at'])
for f in admit['pins']:check(f)
refs(read(Q/'ORACLE_BEFORE_BUILD.json'));refs(read(Q/'TOOLCHAIN_OBSERVED.json'));refs(read(Q/'S2_CORRECTED_DEPENDENCY_BEFORE_BUILD.json'))
src=H/'bootstrap/verify_local_identity.py';node=next(n for n in ast.parse(src.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid');ns={'struct':struct,'uuid':uuid};exec(compile(ast.Module(body=[node],type_ignores=[]),str(src),'exec'),ns)
pairs={p['case_id']:p for p in oracle['normal_pairs']};assert len(pairs)==4
typed=0;envrows=0;rawcount=0;runrows=[]
for i,run in enumerate(summary['runs'],1):
 root=Path(run['stdout']['path']).parent;host=read(root/'HOST_RUN_PROCESS_OBSERVATION.json');refs(host);assert host['owned_child_pid']==run['owned_PID'] and host['numeric_exit']==run['actual_OS_exit']==0
 pre=read(Q/f'PRE_RUN{i}_MANIFEST.json');post=read(root/'POST_RUN_IDENTITY.json');assert len(pre['files'])==150 and pre['files']==post['files']
 assert datetime.datetime.fromisoformat(pre['at'])<datetime.datetime.fromisoformat(host['started_at']) and datetime.datetime.fromisoformat(comp['completed_at'])<datetime.datetime.fromisoformat(host['started_at'])
 for f in pre['files']:check(f)
 refs(pre['runner']);refs(post['runner']);assert ns['mvid'](Path(pre['runner']['exe']['path']))==pre['runner']['mvid']
 for doc in pre['runner']['portable_pdb']['documents']:assert sha(Path(doc['path']))==doc['pdb_hash']==doc['actual_sha256'] and doc['matched']
 loaded=read(root/'ACTUAL_LOADED_MANAGED.json');assert len(loaded)==10;pin={f['path'].lower():f for f in pre['files']}
 for f in loaded:
  p=Path(f['path']);assert p.stat().st_size==pin[f['path'].lower()]['bytes'] and sha(p)==f['sha256']==pin[f['path'].lower()]['sha256'] and ns['mvid'](p)==f['mvid']
 assert next(f for f in loaded if f['name']=='Newtonsoft.Json')['mvid']=='dd21e087-47d9-4bce-bed8-b56112226337'
 result=read(root/'NORMAL_RESULTS.json');assert result['selected_sha256']==d['selected_sha256'] and result['selected_mvid']==d['selected_mvid'] and result['failed_assertions']==0 and len(result['results'])==168 and all(z['status']=='PASS' for z in result['results'])
 rows=read(root/'TYPED_CHECKS.json');assert len(rows)==2992 and all(z['matched'] and z['expected_type']==z['actual_type'] and z['expected']==z['actual'] for z in rows);typed+=len(rows)
 ledger=read(root/'ACTUAL_ADMITTED_CALL_LEDGER.json');assert len(ledger)==296
 scopes=collections.Counter(z['scope'] for z in ledger);assert scopes['primary_direct']==20 and scopes['ordered_getter']==180
 api=collections.Counter(z['api'] for z in ledger if z['scope']=='primary_direct');assert api=={'IssueAdmissionReceiptFromBytes.parent':4,'IssueAdmissionReceiptFromBytes.child':4,'receipt.IsValid.parent':4,'receipt.IsValid.child':4,'OperatorChildLaunchInputs.Capture':4}
 for case,p in pairs.items():
  for phase in ['BEFORE','AFTER_CALLER','AFTER_RETURNED']:
   graph=read(root/f'{case}.{phase}.graph.json');envrows+=eq(p['expected_observation_envelope'],graph,case+'.'+phase)
   rawexpected={'capture':p['expected_Capture15_compact_utf8'],'envelope':p['expected_full_envelope_compact_utf8'],'approved7':p['expected_approved7_compact_utf8'],'task27':p['expected_task27_compact_utf8'],'options7':p['expected_option7_compact_utf8'],'invocation2':p['expected_invocation2_compact_utf8'],'receiptParent':p['expected_receipt_pretty_utf8']['parent'],'receiptChild':p['expected_receipt_pretty_utf8']['child'],'snapshotParent':p['expected_snapshot_pretty_utf8']['parent'],'snapshotChild':p['expected_snapshot_pretty_utf8']['child']}
   for label,v in rawexpected.items():actual=(root/f'{case}.{phase}.{label}.utf8').read_bytes();assert actual==v['utf8_text'].encode('utf8') and len(actual)==v['bytes'] and hashlib.sha256(actual).hexdigest().upper()==v['sha256'];rawcount+=1
  m=p['mutations_after_successful_capture_only'];caller=read(root/f'{case}.caller_owned_mutations.json');returned=read(root/f'{case}.returned_owned_mutations.json')
  assert caller['Task']==m['callerTask27'] and caller['ParentDescriptor']==m['submittedParentDescriptor7'] and caller['ChildDescriptor']==m['submittedChildDescriptor7']
  for key,expectkey in [('Task','returnedTask27'),('ApprovedChildDeclaration','returnedApprovedDeclaration7'),('ParentPolicyDeclaration','returnedParentPolicyDeclaration4'),('ChildPolicyDeclaration','returnedChildPolicyDeclaration4'),('ParentPolicyRecord','returnedParentPolicyRecord4'),('ChildPolicyRecord','returnedChildPolicyRecord4'),('OptionCopy','detachedOperatorOptionCopy7'),('InvocationCopy','detachedTaskInvocationCopy2')]:assert returned[key]==m[expectkey],(case,key)
 inv=read(root/'OUTPUT_INVENTORY.json');assert inv['file_count']==157 and len(inv['files'])==157
 for f in inv['files']:check(f)
 assert {str(p.resolve()) for p in root.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}=={str(Path(f['path']).resolve()) for f in inv['files']}
 runrows.append({'root':str(root),'PID':host['owned_child_pid'],'exit':0,'PASS':168,'FAIL':0,'runtime_typed':2992,'pins':150,'loaded':10,'outputs':157,'culture':host['observed_culture']})
assert typed==5984 and envrows==5856 and rawcount==240
cross=read(Q/'CROSS_CULTURE_NORMAL_PAIRS.json');assert len(cross['pairs'])==4
for pair in cross['pairs']:
 for phase in pair['complete_three_phase_graph_pair']:check(phase['enUS']);check(phase['deDE']);assert Path(phase['enUS']['path']).read_bytes()==Path(phase['deDE']['path']).read_bytes()
refs(read(Q/'FINAL_RUNTIME_PIN_AND_RECURSIVE_SEAL.json'));refs(read(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json'));refs(read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json'));refs(read(Q/'CLR_MANAGED_LOAD_PROVENANCE.json'))
beforeInv=read(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory'];afterInv=read(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['first_inventory'];assert beforeInv==afterInv
bp=R/'Dispatcher/MASTER_A_TASKS.json';t=read(bp)['tasks'][-1];sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
pp=C/'MASTER_R27_S2_COMPLETION_PRESERVATION_20261012.json';assert not pp.exists();write(pp,pres)
vp=C/'MASTER_SOL_R27_CHILD_CAPTURE_S2_COMPLETION_VERIFICATION_20261012.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-R27-S2-COMPLETE-NEXT-20261012-01','guard_session':76245,'guard_pid':2728,'delivery_id':x['delivery_id'],'wp_id':x['wp_id'],'wp_revision':'S2','result_id':x['result_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'evidence_count':361,'protected':13674,'actual_snapshot':sn,'runs':runrows,'Master_runtime_typed':typed,'Master_independent_envelope_rows':envrows,'Master_exact_raw_bindings':rawcount,'compile_builds':1,'compiler_exit':0,'compiler_stdout_bytes':34168,'compiler_stderr_bytes':0,'managed_loads_independent_PE_MVID_per_run':10,'allprepost_and_recursive_pathset':True,'prospective_compiler_allrefs_source_input_oracle_callplan':True,'readonly_policy_ids_control':'Holder replacement only; not inplace mutation; backing private source proof separate','actual_EnvironmentVersion_nativeCLR_module':'UNOBSERVED; managed corelib SHA/MVID observed','selected_sha256':d['selected_sha256'],'selected_mvid':d['selected_mvid'],'matching_pdb_sha256':'F0BC1B7D92F67593EA967F56A90EE302C76B920A46B98EF77219F7B884C47814','frozen_manifest':d['frozen_manifest'],'frozen_manifest_sha256':d['frozen_manifest_sha256'],'verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','Master_candidate_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'}
write(vp,proof);print(json.dumps({'status':proof['verification_status'],'evidence':361,'protected':13674,'typed':typed,'envelope':envrows,'raw':rawcount,'PASSeach':168,'FAIL':0}))
