from pathlib import Path
import json,hashlib,datetime,sys,shutil
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination';Q=R/'QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f.get('bytes',f.get('size',f.get('size_bytes'))),str(p)
def refs(x):
 if isinstance(x,dict):
  if all(k in x for k in ['path','sha256']) and any(k in x for k in ['bytes','size','size_bytes']):check(x)
  for y in x.values():refs(y)
 elif isinstance(x,list):
  for y in x:refs(y)
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();c=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=read(R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1];T=Path(t['completion_path']).parent;a=read(T/'COMPLETION.json');sol=read(Q/'COMPLETION.json');rr=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert c['active_operation'] is None and a['dispatch_id']==t['dispatch_id'] and a['wp_id']==t['wp_id'] and a['task_revision']==t['wp_revision'] and a['envelope']==29 and all(a[k]==0 for k in ['candidate_build_count','candidate_execution_count','native_execution_count','assets_copy_count','production_files_modified_count'])
assert a['e1_verdict']=='READ_ONLY_PREPARATION_NO_EXECUTION' and not any(x.get('result_id') in [a['result_id'],sol['result_id']] for x in rr['processed_results'])
assert all(sol[k]==c['sol_current_delivery'][k] for k in ['delivery_id','wp_id','wp_revision']) and sol['result_id']==c['sol_current_result_id'] and sol['status']=='COMPLETED';assert sha(Q/'COMPLETION.json')=='C6DE14FC7948F620DF50CC6A34CA151F97793F91C17D2137422D63B24A95DD73'
assert len(a['artifacts'])==10
for f in a['artifacts']:check(f)
em=read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==29
for f in em['files']:check(f)
refs(sol);refs(read(Q/'RESULT_INDEX.json'));refs(read(Q/'ACK_COMPLETION_BINDING.json'))
assert sha(Q/'ACK_INITIAL.json')==c['sol_current_ack']['initial_ACK']['sha256']==sha(Q/'ACK.json')
sf=C/'MASTER_SOL_R26_CHILD_REG_PREPARATION_COMPLETION_SNAPSHOT_20261011.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['latestTurn']['id']==c['sol_current_delivery']['actual_snapshot']['latestTurn']['id']
base=read(Path(c['sol_current_delivery']['baseline_path']));assert len(base['files'])==13419
for f in base['files']:check(f)
for n in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 p=read(Q/n);assert p['protected_unique_paths']==13419 and {f['path']:(f['sha256'],f['bytes']) for f in p['protected_files']}=={f['path']:(f['sha256'],f['bytes']) for f in base['files']}
prod=t['production_fixed_files'];assert len(prod)==9
for f in prod:check(f)
for n in ['ENGINE_FREEZE_BEFORE.json','ENGINE_FREEZE_AFTER.json']:
 p=read(T/n);fs=p['files'] if isinstance(p,dict) else p;assert len(fs)==9
 for f in fs:check(f)
anchors=read(Q/'SOURCE_ANCHORS.json');assert len(anchors['anchors'])==20
for f in anchors['source_files']:check(f)
for x in anchors['anchors']:
 raw=Path(x['path']).read_bytes();span=raw[x['start_byte']:x['end_byte_exclusive']];assert sha(Path(x['path']))==x['file_sha256'] and hashlib.sha256(span).hexdigest().upper()==x['span_sha256'] and len(span)==x['bytes']
 assert raw[:x['start_byte']].count(b'\n')+1==x['start_line']
points=read(Q/'PROPOSED_MINIMUM_PATCH_SPANS.json')['exact_points'];assert len(points)==7
for x in points:
 raw=Path(x['path']).read_bytes();assert sha(Path(x['path']))==x['base_sha256'] and hashlib.sha256(raw[x['context_start']:x['context_end']]).hexdigest().upper()==x['context_sha256']
assert points[0]['start_byte']==points[0]['end_byte_exclusive']==166910
field=read(Q/'OWNERSHIP_FIELD_SOURCE_MAP.json');assert len(field['field_rows'])==114
oracle=read(Q/'PROSPECTIVE_NORMAL_ORACLE.json');assert len(oracle['four_normal_fixture_pairs'])==4 and oracle['candidate_calls']==0 and oracle['qa_runner_build_execute']==0
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0];pp=T/'MASTER_R26_TERMINAL_PRESERVATION.json';assert not pp.exists();pp.write_text(json.dumps(pres,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Preparation documents freeze, never a new production candidate identity.
paths={Path(f['path']).resolve() for f in a['artifacts']};paths.add((T/'COMPLETION.json').resolve());F=R/'Dispatcher/CANDIDATES/G05R26-docs-4d660e9b';rows=[]
for p in sorted(paths):
 dest=F/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(p)==sha(dest);rows.append({'original_path':str(p),'frozen_path':str(dest),'sha256':sha(dest),'size':dest.stat().st_size})
fm=T/'MASTER_R26_PREPARATION_REVIEW_FREEZE_MANIFEST.json';assert not fm.exists();fm.write_text(json.dumps({'at':at,'kind':'READONLY_PREPARATION_DOCUMENTS_ONLY_NOT_NEW_ENGINE_CANDIDATE','files':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
vp=C/'MASTER_R26_DUAL_CHILD_REG_PREPARATION_COMPLETION_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-R26-SOL-COMPLETE-20261011-01','guard_session':94864,'guard_pid':20528,'A_dispatch_id':t['dispatch_id'],'A_result_id':a['result_id'],'A_completion_sha256':sha(T/'COMPLETION.json'),'A_artifacts':10,'A_completion_alias_reconciliation':'task_revision=Masterwp_revision;size_bytes=actualsize;no producer/report_kind/status/role labels;exacttask-envelope-report-ACK E1readonly evidence adoptedwithoutrewriting','Sol_delivery_id':sol['delivery_id'],'Sol_result_id':sol['result_id'],'Sol_completion_sha256':sha(Q/'COMPLETION.json'),'Sol_evidence':29,'Sol_actual':sn,'protected_paths':13419,'production9fixed':True,'source_anchors_master_matched':20,'insertion_contexts_master_matched':7,'field_rows':114,'prospective_pairs':4,'prospective_execution':0,'A_preparation_freeze':row(fm),'A_docs_frozen_count':len(rows),'selected_sha256':sol['selected_sha256'],'selected_mvid':sol['selected_mvid'],'candidate_build_execute':0,'native_e2_released':False,'closure_changed':False,'foundation':'HOLD','verification_status':'VERIFIED_PENDING_MASTER_DISPOSITION'}
vp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'A_artifacts':10,'Sol_evidence':29,'protected':13419,'anchors':20,'contexts':7,'docfreeze':len(rows),'status':'VERIFIED_PENDING_MASTER_DISPOSITION'}))
