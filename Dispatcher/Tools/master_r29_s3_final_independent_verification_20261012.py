from pathlib import Path
import json, hashlib, sys, collections, datetime
sys.stdout.reconfigure(encoding='utf-8')
R=Path(r'C:\Users\user\Desktop\RimMulti');H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
Q=R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S3-20261012'
OUT=C/'MASTER_SOL_R29_S3_FINAL_INDEPENDENT_EVIDENCE_VERIFICATION_20261012.json'
def rd(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def row(p):
 p=Path(p);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper(),bytes=p.stat().st_size)
def ck(v,key='path'):
 a=row(v[key]);assert a['sha256']==v['sha256'] and a['bytes']==v['bytes'],v[key];return a
def exact(a,b,path='root'):
 assert type(a) is type(b),(path,type(a).__name__,type(b).__name__)
 if isinstance(a,dict):
  assert list(a)==list(b),(path,'ordered keys')
  for k in a:exact(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),(path,'array length')
  for i,(x,y) in enumerate(zip(a,b)):exact(x,y,path+'['+str(i)+']')
 else:assert a==b,(path,'value')
def rawbytes(v):
 b=v['utf8_text'].encode('utf-8');assert hashlib.sha256(b).hexdigest().upper()==v['sha256'] and len(b)==v['bytes'];return b
def main():
 assert not OUT.exists()
 comp=rd(Q/'COMPLETION.json');assert comp['status']=='COMPLETED' and comp['wp_revision']=='S3'
 assert comp['QA_compile']==1 and comp['QA_runs']==2 and comp['candidate_rebuild']==comp['forbidden_calls']==0
 for v in comp['artifacts'].values():ck(v)
 em=rd(Q/'EVIDENCE_MANIFEST.json');assert em['result_id']==comp['result_id'] and len(em['files'])==em['file_count']==927
 for v in em['files']:ck(v)
 actual={str(p) for p in Q.rglob('*') if p.is_file()};included={v['path'] for v in em['files'] if str(Q) in v['path']}
 excluded={str(Q/n) for n in em['excluded_cycles']}|{str(Q/'postanalysis-r1'/n) for n in em['unfinished_actual_seal_logger_excluded']}
 assert actual-included==excluded,(sorted(actual-included-excluded),sorted(excluded-actual))
 seal=rd(Q/'postanalysis-r1/WIDTH_TERMINAL_R1_seal_TOOL.json');assert seal['exit_code']==0 and seal['candidate_compiler_runner_calls']==0
 for k in ['script','stdout','stderr']:ck(seal[k])
 idx=rd(Q/'RESULT_INDEX.json');ackb=rd(Q/'ACK_COMPLETION_BINDING.json')
 assert idx['result_id']==ackb['result_id']==comp['result_id'] and idx['delivery_id']==comp['delivery_id']
 for v in idx['artifacts'].values():ck(v)
 for k in ['initial_ACK','ACK_mirror','resume_ACK','result_index']:ck(ackb[k])
 baseline=rd(C/'MASTER_R29_S3_PAIR_QA_PROTECTED_BASELINE_20261012.json')
 for v in baseline['files']:ck(v)
 assert len(baseline['files'])==14365
 frozen=rd(Q/'ACK_INITIAL.json')['frozen_manifest'];ck(frozen);fm=rd(frozen['path'])
 for v in fm['files']:ck(v,'frozen_path')
 assert len(fm['files'])==132
 prebuild=rd(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')
 assert len(prebuild['pins'])==253 and prebuild['candidate_calls_beforepin']==prebuild['builds_beforepin']==0
 for v in prebuild['pins']:ck(v)
 build=rd(Q/'BUILD_TOOL_PROOF.json');assert build['exit_code']==0 and build['build_attempts']==1 and build['production_candidate_builds']==0
 assert datetime.datetime.fromisoformat(prebuild['at'])<datetime.datetime.fromisoformat(build['started_at'])
 ck(build['stdout']);ck(build['stderr'])
 oracle=rd(Q/'NORMAL_EXPECTED_ORACLE.json');ck(prebuild['oracle'])
 pairprep=R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012/PRE_RUN_EXPECTED_ORACLE.json'
 captureprep=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/PROSPECTIVE_CAPTURE_ORACLE.json'
 assert row(pairprep)['sha256']=='7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02'
 assert row(captureprep)['sha256']=='5961CD18DA05B67F6DE40DA8A6EBB289D94ACF85054D57FB31FE4B8C5530C4C7'
 exact(oracle['pair_cases'],rd(pairprep)['prospective_cases']);exact(oracle['normal_pairs'],rd(captureprep)['normal_pairs'])
 rawmap={};graphmap={}
 for case in oracle['pair_cases']:
  cid='PAIR_'+case['case_id'];p=case['independently_supplied_parent14_7'];ch=case['independently_supplied_child14_7']
  entries={'pair.envelope':case['expected_full_graph_compact_UTF8'],'pair.bundleProjection':case['expected_bundle_compact_UTF8_noLF']}
  for name,part in [('parent',p),('child',ch)]:
   for suffix,key in [('original7','original_declaration7_compact_utf8'),('receipt11','receipt_compact_utf8'),('snapshot15','snapshot_compact_utf8'),('receipt.pretty','receipt_redacted_pretty_windows_utf8'),('snapshot.pretty','snapshot_redacted_pretty_windows_utf8')]:entries['pair.'+name+'.'+suffix]=part[key]
  for phase in ['BEFORE','AFTER_CALLER','AFTER_RETURNED']:
   for name,v in entries.items():rawmap[cid+'.'+phase+'.'+name+'.utf8']=rawbytes(v)
   graphmap[cid+'.'+phase+'.pair.graph.json']=case['expected_full_observation_graph']
 for case in oracle['normal_pairs']:
  cid=case['case_id'];entries={}
  for name,key in [('capture','expected_Capture15_compact_utf8'),('envelope','expected_full_envelope_compact_utf8'),('approved7','expected_approved7_compact_utf8'),('task27','expected_task27_compact_utf8'),('options7','expected_option7_compact_utf8'),('invocation2','expected_invocation2_compact_utf8')]:entries[name]=case[key]
  for name,key in [('receipt','expected_receipt_pretty_utf8'),('snapshot','expected_snapshot_pretty_utf8')]:
   entries[name+'Parent']=case[key]['parent'];entries[name+'Child']=case[key]['child']
  for phase in ['BEFORE','AFTER_CALLER','AFTER_RETURNED']:
   for name,v in entries.items():rawmap[cid+'.'+phase+'.'+name+'.utf8']=rawbytes(v)
   graphmap[cid+'.'+phase+'.graph.json']=case['expected_observation_envelope']
 assert len(rawmap)==336 and len(graphmap)==30
 summaries=[];runroots=[Q/'runs/1-en-US',Q/'runs/2-de-DE']
 for run in runroots:
  inv=rd(run/'OUTPUT_INVENTORY.json');assert len(inv['files'])==inv['file_count']==402
  for v in inv['files']:ck(v)
  assert {str(p) for p in run.rglob('*') if p.is_file()}=={v['path'] for v in inv['files']}|{str(run/'OUTPUT_INVENTORY.json')}
  assert {p.name for p in run.glob('*.utf8')}==set(rawmap)
  for name,b in rawmap.items():assert (run/name).read_bytes()==b,name
  for name,g in graphmap.items():exact(g,rd(run/name),name)
  nr=rd(run/'NORMAL_RESULTS.json');assert nr['failed_assertions']==0 and len(nr['results'])==438
  assert all(v['status']=='PASS' for v in nr['results']) and len({v['id'] for v in nr['results']})==438
  typed=rd(run/'TYPED_CHECKS.json');assert len(typed)==6700 and all(v['matched'] and v['expected_type']==v['actual_type'] for v in typed)
  for v in typed:exact(v['expected'],v['actual'],v['path'])
  ledger=rd(run/'ACTUAL_ADMITTED_CALL_LEDGER.json');counts=dict(collections.Counter(v['scope'] for v in ledger))
  assert counts==dict(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18)
  pre=rd(run/'PRE_RUN_INPUT_MANIFEST.json');post=rd(run/'POST_RUN_IDENTITY.json');assert len(pre['files'])==len(post['files'])==264 and post['all_prepost_matched']
  for v in pre['files']+post['files']:ck(v)
  assert {v['path']:(v['sha256'],v['bytes']) for v in pre['files']}=={v['path']:(v['sha256'],v['bytes']) for v in post['files']}
  host=rd(run/'HOST_RUN_PROCESS_OBSERVATION.json');assert host['numeric_exit']==0 and host['CSharp_Process_calls']==0 and host['only_owned_new_QA_runner']
  ck(host['stdout']);ck(host['stderr'])
  loaded=rd(run/'ACTUAL_LOADED_MANAGED.json');assert len(loaded)==10
  for v in loaded:assert row(v['path'])['sha256']==v['sha256']
  assert rd(run/'ACTUAL_LOADED_PREPIN_BINDING.json')['all_matched']
  summaries.append(dict(run_id=nr['run_id'],culture=host['culture'],pid=host['owned_child_pid'],exit_code=0,assertions_pass=438,typed_hierarchical_rows=6700,raw_expected_files=336,full_graphs=30,inventory_files=402,prepost_pins=264,loaded_managed=10,ledger=counts))
 assert summaries[0]['pid']!=summaries[1]['pid'] and summaries[0]['run_id']!=summaries[1]['run_id']
 for name in rawmap:assert (runroots[0]/name).read_bytes()==(runroots[1]/name).read_bytes()
 for name in graphmap:exact(rd(runroots[0]/name),rd(runroots[1]/name),name)
 static=rd(Q/'STATIC_SOURCE_SCOPE_BEFORE_BUILD.json');assert static['outside_total_bytes']==234431
 for k in ['old_source','new_source','scope_manifest','publisher_source']:ck(static[k])
 width=rd(Q/'postanalysis-r1/VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json');ck(width['source'])
 snapraw=rd(C/'MASTER_SOL_R29_S3_COMPLETED_IDLE_SNAPSHOT_20261012.json');snap=json.loads(snapraw['content'][0]['text'])['polls'][0]
 assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
 result=dict(at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),result_id=comp['result_id'],delivery_id=comp['delivery_id'],completion=row(Q/'COMPLETION.json'),report=comp['artifacts']['report'],evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),evidence_files=927,cycle_exclusions=em['excluded_cycles'],postseal_logger_exclusions=em['unfinished_actual_seal_logger_excluded'],terminal_return=row(Q/'RETURN_TOOL_PROOF.json'),delivery_status=row(Q/'DELIVERY_STATUS.json'),protected_paths=14365,frozen_files=132,prospective_compile_pins=253,prebuild_oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),original_pair_oracle=row(pairprep),original_Capture_oracle=row(captureprep),independent_original_oracle_equivalence=True,independent_raw_expected_bindings=672,crossculture_raw_pairs=336,independent_ordered_graphs=60,crossculture_graph_pairs=30,runs=summaries,static_outside_bytes=234431,width_source_only=True,actual_snapshot=snap,qa_builds=1,qa_runs=2,production_modify_rebuild=0,Master_candidate_execution_build=0,static_High3='OPEN',native_E2='NOT_RELEASED',Foundation='HOLD',limitation='Positive pure data only; wrapper bundle projection, SOURCE-only widths/internal calls; Capture ID holder replacement is not in-place array isolation; no native/operator/issuer/channel/consume/rejection validation.',Master_readonly_schema_probe_correction='Key Sol absent in endpoint mapping; actual existing schema inspected, no candidate or QA mutation.')
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(dict(status='MASTER_INDEPENDENT_VERIFICATION_PASS_SCOPED',proof=row(OUT),protected_paths=14365,evidence_files=927,raw_expected=672,graph_pairs=30,source_High3='OPEN',native_E2='NOT_RELEASED'),ensure_ascii=False))
if __name__=='__main__':main()
