from pathlib import Path
import json,hashlib,datetime,sys,ast,struct,uuid,tomllib
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S2-20261011'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
def ordered(e,a):
 if type(e)!=type(a):return False
 if isinstance(e,dict):return list(e)==list(a) and all(ordered(e[k],a[k]) for k in e)
 if isinstance(e,list):return len(e)==len(a) and all(ordered(x,y) for x,y in zip(e,a))
 return e==a
def refs(x):
 if isinstance(x,dict):
  if all(k in x for k in ['path','sha256','bytes']):check(x)
  for v in x.values():refs(v)
 elif isinstance(x,list):
  for v in x:refs(v)
ns=dict(struct=struct,uuid=uuid);tree=ast.parse((H/'bootstrap/verify_local_identity.py').read_text(encoding='utf-8-sig'));nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='mvid'];assert len(nodes)==1;exec(compile(ast.Module(body=nodes,type_ignores=[]),'Master_metadata_bytes_only','exec'),ns);mvid=ns['mvid']
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];co=read(Q/'COMPLETION.json');idx=read(Q/'RESULT_INDEX.json');em=read(Q/'EVIDENCE_MANIFEST.json');bind=read(Q/'ACK_COMPLETION_BINDING.json')
assert c['active_operation'] is None and all(co[k]==idx[k]==bind[k] for k in ['delivery_id','result_id','wp_id','wp_revision']) and co['result_id']==c['sol_current_result_id'] and co['status']=='COMPLETED'
assert sha(Q/'COMPLETION.json')=='421FF53D680B3E6B1C7FD12169626F4C34C8D364F08AB0C8C161986F09544684'
assert not any(x.get('result_id')==co['result_id'] for x in read(R/'Dispatcher/MASTER_RECEIPTS.json')['processed_results'])
refs(co);refs(idx);refs(bind);assert len(em['files'])==89
for f in em['files']:check(f)
assert sha(Q/'ACK_INITIAL.json')==c['sol_current_ack']['ack_sha256']==sha(Q/'ACK.json')
sf=C/'MASTER_SOL_R25_ROLE_USERDATA_S2_COMPLETION_SNAPSHOT_20261011.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
base=read(Path(d['baseline_path']));assert sha(Path(d['baseline_path']))==d['baseline_sha256'] and len(base['files'])==13315
for f in base['files']:check(f)
for n in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 p=read(Q/n);assert p['protected_unique_paths']==13315 and {f['path']:(f['sha256'],f['bytes']) for f in p['files']}=={f['path']:(f['sha256'],f['bytes']) for f in base['files']}
oldQ=R/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011'
assert sha(Q/'Program.cs')==sha(oldQ/'Program.cs')=='6614E455D316F046BC9072171B4A39F676148E61395AEF889C2E95974E6A615C'
oldOracle=read(oldQ/'NORMAL_EXPECTED_ORACLE.json');newOracle=read(Q/'NORMAL_EXPECTED_ORACLE.json')
assert list(oldOracle['cases'])==list(newOracle['cases'])
for key,e in oldOracle['cases'].items():
 n=newOracle['cases'][key];assert list(e)==list(n)
 assert ordered({k:v for k,v in e.items() if k!='expected_redacted_utf8_text'},{k:v for k,v in n.items() if k!='expected_redacted_utf8_text'})
 assert n['expected_redacted_utf8_text']==json.dumps(e['expected_redacted'],ensure_ascii=False,indent=2).replace(chr(10),chr(13)+chr(10))
summary=read(Q/'INDEPENDENT_EXECUTION_SUMMARY.json');assert summary['actual_run_exits']==[0,0] and summary['qa_finalbuilds']==1 and co['allproduction_globalSafeAwake_Process_receipt_native_negative']==0
compiler=read(Q/'BUILD_TOOL_PROOF.json');refs(compiler);assert compiler['exit_code']==0 and compiler['build_attempts']==1 and compiler['stdout']['bytes']==3413 and compiler['stderr']['bytes']==0
oracle=read(Q/'NORMAL_EXPECTED_ORACLE.json');assert len(oracle['cases'])==4 and not oracle['output_derived'];processes=[];bytechecks=[];typedtotal=0
for stage in [1,2]:
 pre=read(Q/f'PRE_RUN{stage}_MANIFEST.json');out=Path(pre['output_root']);post=read(out/'POST_RUN_IDENTITY.json');host=read(out/'HOST_RUN_PROCESS_OBSERVATION.json');tool=read(out/'RUN_TOOL_PROOF.json');res=read(out/'NORMAL_RESULTS.json')
 assert pre['files']==post['files'] and len(pre['files'])==160 and host['numeric_exit']==tool['exit_code']==0 and host['argv']==pre['argv'] and host['cwd']==pre['cwd'] and host['observed_culture']==pre['culture']
 for f in pre['files']:check(f)
 refs(host);assert res['selected_sha256']==co['selected_sha256'] and res['selected_mvid']==co['selected_mvid'] and mvid(Path(res['selected_path']))==co['selected_mvid']
 assert len(res['results'])==36 and sum(f['status']=='PASS' for f in res['results'])==36 and sum(f['status']=='FAIL' for f in res['results'])==0 and res['failed_assertions']==0
 assert all(x['id'].endswith('_FULL13_UTC_BYTES_INITIAL') for x in res['results'] if x['status']=='FAIL')
 typed=read(out/'TYPED_CHECKS.json');assert len(typed)==912 and all(x['matched'] and x['expected_type']==x['actual_type'] and ordered(x['expected'],x['actual']) for x in typed);typedtotal+=len(typed)
 loaded=read(out/'ACTUAL_LOADED_MANAGED.json');assert len(loaded)==10
 for f in loaded:assert sha(Path(f['path']))==f['sha256'] and mvid(Path(f['path']))==f['mvid']
 inv=read(out/'OUTPUT_INVENTORY.json');assert len(inv['files'])==21
 for f in inv['files']:check(f)
 assert {f['relative_path'] for f in inv['files']}=={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}
 for key,e in oracle['cases'].items():
  obs=read(out/(key+'.observation.json'));raw=obs['redactedBefore'];expected=e['expected_redacted_utf8_text']
  assert '\r\n' in expected and raw==expected and raw==obs['redactedAfterSource']==obs['redactedAfterDetached'] and ordered(json.loads(raw),e['expected_redacted'])
  assert ordered(obs['callerBefore'],e['input']) and ordered(obs['callerImmediatelyAfter'],e['input']) and all(ordered(obs[k],e['expected_graph']) for k in ['graphInitial','graphAfterSource','graphAfterDetached'])
  assert obs['selectedBefore']==obs['selectedAfter']==e['expected_selected']
  for phase in ['redactedBefore','redactedAfterSource','redactedAfterDetached']:
   assert obs[phase].encode()==expected.encode()
   bytechecks.append(dict(stage=stage,case_id=key,phase=phase,expected_sha256=hashlib.sha256(expected.encode()).hexdigest().upper(),actual_sha256=hashlib.sha256(raw.encode()).hexdigest().upper(),expected_bytes=len(expected.encode()),actual_bytes=len(raw.encode()),CRLF_count=raw.count('\r\n'),LF_count=expected.count('\n'),raw_assertion_status='PASS_EXACT_NEW_ORACLE'))
 processes.append(dict(stage=stage,pid=host['owned_child_pid'],culture=host['observed_culture'],numeric_exit=0,raw_pass=36,raw_fail=0,typed_rows=912,typed_failed=0,pins=160,loaded=10,recursive_outputs=21))
assert typedtotal==1824 and len(bytechecks)==24
for key in oracle['cases']:
 ps=[Path(read(Q/f'PRE_RUN{s}_MANIFEST.json')['output_root'])/(key+'.observation.json') for s in [1,2]];assert ps[0].read_bytes()==ps[1].read_bytes()
master=read(C/'MASTER_GATE05_R25_ROLE_USERDATA_E1_VERIFICATION_20261011.json');fm=Path(master['frozen_manifest']);assert sha(fm)==master['frozen_manifest_sha256']
for f in read(fm)['files']:check({'path':f['frozen_path'],'sha256':f['sha256'],'bytes':f['size']})
for f in master['before_after_checks']:
 if f['phase']=='AFTER':check({'path':f['path'],'sha256':f['sha256'],'bytes':f['size']})
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
vp=C/'MASTER_SOL_R25_ROLE_USERDATA_S2_COMPLETION_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-R25-S2-COMPLETE-NEXT-20261011-01','guard_session':35120,'guard_pid':24636,'delivery_id':co['delivery_id'],'wp_id':co['wp_id'],'wp_revision':'S2','result_id':co['result_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'report':co['report'],'evidence_manifest':co['evidence_manifest'],'result_index':co['result_index'],'evidence_count':89,'protected_unique_paths':13315,'actual_snapshot':sn,'processes':processes,'typed_rows_master_checked':1824,'typed_mismatches':0,'exact_raw_byte_bindings_master_checked':bytechecks,'S1_raw_fail_unchanged_protected':True,'S2_only_oracle_formatting_and_sourceclone_checked':True,'crossculture_byte_pairs':4,'selected_sha256':co['selected_sha256'],'selected_mvid':co['selected_mvid'],'frozen_manifest':str(fm),'frozen_manifest_sha256':sha(fm),'raw_os_exits':[0,0],'raw_assertion_verdict':'PASS_NEW_S2_S1_FAIL_PRESERVED','verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION','master_candidate_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','scheduler_actual':cfg,'initial_metadata_schema_failure':'SOURCE_ONLY_ARCHIVED_NO_CANDIDATE_CALL','master_read_limitations':[]}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'evidence':89,'protected':13315,'typed':1824,'typed_mismatch':0,'exits':[0,0],'exact_raw_byte_bindings':24,'status':'VERIFIED_PENDING_MASTER_DISPOSITION'}))
