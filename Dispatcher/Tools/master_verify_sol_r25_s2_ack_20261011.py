from pathlib import Path
import json,datetime,hashlib,tomllib,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R25-QA-S2-ACK-20261011-01';PID=3880;SESSION=19395
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
if len(sys.argv)>1 and sys.argv[1]=='released':
 p=C/'MASTER_R25_S2_ACK_GUARD_FINALLY_RELEASE_20261011.json';raw=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json')
 assert raw['exit_code']==0 and '"status": "RELEASED"' in raw['output'] and RUN in raw['output'] and info['status']=='RELEASED' and info['run_id']==RUN and info['pid']==PID and c['last_monitor_run']['run_id']==RUN
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':RUN+'-RELEASE','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':RUN,'pid':PID,'proof':str(p)});print('ACTUAL_ACK_GUARD_RELEASE_RECORDED');sys.exit(0)
d=c['sol_current_delivery'];Q=Path(d['qa_root']);ap=Q/'ACK_INITIAL.json';ack=read(ap)
assert ack['delivery_id']==c['sol_current_attempt_id']==d['delivery_id'] and ack['wp_id']==c['sol_current_wp']=='WP_QA_ENGINE_GATE05_R25_ROLE_USERDATA_INDEPENDENT' and ack['wp_revision']=='S2' and ack['producer']=='Sol' and ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp']
assert ack['result_id']=='SOL-GATE05-R25-ROLE_USERDATA-INDEPENDENT-S2-20261011-098499b5238a467cb87509c88d8d2e07' and ack['report_sha256'] is None and ack['evidence_manifest_sha256'] is None and sha(Q/'ACK.json')==sha(ap)
sf=C/'MASTER_SOL_R25_ROLE_USERDATA_S2_ACK_SNAPSHOT_20261011.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='active' and sn['latestTurn']['status']=='inProgress' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
assert sha(Path(d['wp_path']))==d['wp_sha256']=='C3EC431869CD63E643E26DF22F1A80EE314967AD8589F8CF70B4F37A3113454B'
base=Path(d['baseline_path']);assert sha(base)==d['baseline_sha256'];files=read(base)['files'];assert len(files)==13315
for f in files:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==13315 and before['baseline']['sha256']==sha(base)
assert {f['path']:(f['sha256'],f['bytes']) for f in before['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
mp=read(C/'MASTER_GATE05_R25_ROLE_USERDATA_E1_VERIFICATION_20261011.json');line=read(Q/'R25_FROZEN_LINEAGE.json');assert len(line['candidates'])==2 and not line['candidate_executed'] and not line['original_helper_top_level_executed']
for q in line['candidates']:
 m=next(x for x in mp['lineage'] if x['mvid']==q['mvid'])
 assert q['dll_sha256']==m['dll_sha256'] and q['pdb_sha256']==m['pdb_sha256'] and q['guid']==q['codeview_guid']==m['pdbGuid']==m['codeviewGuid'] and len(q['documents'])==4
 for f in q['documents']:
  md=next(x for x in m['documents'] if x['path']==f['path']);assert f['matched'] and md['matched'] and f['pdb_hash']==f['actual_sha256']==md['expected']==md['actual']==sha(Path(f['frozen_source_path']))
fm=Path(mp['frozen_manifest']);assert sha(fm)==mp['frozen_manifest_sha256'] and len(read(fm)['files'])==99
t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1];rr=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert t['result_id']==mp['result_id'] and sha(Path(t['completion_path']))==mp['completion_sha256'] and sum(x.get('result_id')==mp['result_id'] for x in rr['processed_results'])==1
current=[]
for f in mp['before_after_checks']:
 if f['phase']=='AFTER':
  p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['size'];current.append(str(p))
assert len(current)==9
sp=Q/'THREE_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json';scope=read(sp);w=Path(scope['source']['path']);wb=w.read_bytes()
assert sha(w)==scope['source']['sha256']==mp['source_sha256'] and scope['all_other_bytes_exact'] and len(scope['three_authorized_spans'])==3 and len(scope['four_fixed_ordered_segments'])==4
for seg in scope['four_fixed_ordered_segments']:
 f=seg['original_fixed_file'];p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'] and wb[seg['new_start']:seg['new_end']]==p.read_bytes() and seg['bytes_exact']
for f in scope['fixed']:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
oldq=R/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011'
assert sha(Q/'Program.cs')==sha(oldq/'Program.cs')=='6614E455D316F046BC9072171B4A39F676148E61395AEF889C2E95974E6A615C'
oldoracle=read(oldq/'NORMAL_EXPECTED_ORACLE.json');neworacle=read(Q/'NORMAL_EXPECTED_ORACLE.json')
assert list(neworacle['cases'])==list(oldoracle['cases']) and len(neworacle['cases'])==4
for key,e in oldoracle['cases'].items():
 n=neworacle['cases'][key];assert list(e)==list(n)
 assert {k:v for k,v in e.items() if k!='expected_redacted_utf8_text'}=={k:v for k,v in n.items() if k!='expected_redacted_utf8_text'}
 expected=json.dumps(e['expected_redacted'],ensure_ascii=False,indent=2).replace(chr(10),chr(13)+chr(10))
 assert n['expected_redacted_utf8_text']==expected and e['expected_redacted_utf8_text']!=expected
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
vp=C/'MASTER_SOL_R25_ROLE_USERDATA_S2_ACK_VERIFICATION_20261011.json';assert not vp.exists()
proof={'at':at,'guard_run':RUN,'guard_session':SESSION,'guard_pid':PID,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'wp_revision':'S2','result_id':ack['result_id'],'ack_path':str(ap),'ack_sha256':sha(ap),'actual_snapshot':sn,'snapshot_path':str(sf),'snapshot_sha256':sha(sf),'protected_paths_master_rehashed':13315,'baseline_sha256':sha(base),'qa_lineage_path':str(Q/'R25_FROZEN_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R25_FROZEN_LINEAGE.json'),'master_metadata_comparison':'DebugReleaseSHA-MVID-CodeView-PDB-source4/4matched','three_span_scope_admission_path':str(sp),'three_span_scope_admission_sha256':sha(sp),'four_fixed_segments_matched':4,'current_production_package_identity_checked':9,'A_terminal_completion_deduped_unchanged':True,'verdict':'ACK_VERIFIED_INDEPENDENT_R25_S2_NEWLINE_ORACLE_FRESH_NORMAL_QA_IN_PROGRESS','S2_program_exact_S1_bytes_and_four_oracle_formatting_only_changes_master_checked':True,'initial_ACK_execution_statement':'InitialACKnotbuilt;currentQAexecutionverdictPENDING;notanobservationoflaterongoingexecution','QA_metadata_helper_schema_failure':'Historicallegacyworker_before_sha256lookupfailedbeforewrites;actualsource_before/authorized_spans/byteshandled;candidateexecution0there','qa_owned_runner_build_allowed':True,'master_candidate_build_execute':0,'new_wp':False,'runtime_e2_released':False,'closure_changed':False,'monitor_actual_status':'PAUSED60MIN173CHAR_SAME_TARGET','foundation':'HOLD'}
write(vp,proof);c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,sol_last_ack=proof,last_sol_cursor=sn['cursor'],updated_at=at);c['last_monitor_run']={'run_id':RUN,'guard_session':SESSION,'guard_pid':PID,'at':at,'status':'R25_ACK_IDENTITY_SCOPE_SAME_ACTIVE_TURN_PROTECTED_MATCHED_NO_NEW_WP','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R25_S2_ACK_GUARD_FINALLY_RELEASE_20261011.json')};write(cp,c)
sfp=H/'DISPATCHER_STATE.json';st=read(sfp);st['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=sn['cursor']);st['updated_at']=at;write(sfp,st)
e=dict(proof,event_id=ack['delivery_id']+'-ACK-VERIFIED',type='SOL_R25_S2_INDEPENDENT_ACK_VERIFIED',proof_path=str(vp),proof_sha256=sha(vp));assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(R/'Dispatcher/MASTER_RECEIPTS.json',rr);event(e)
para=f'\n\n## LOCAL-SOL-R25-S2-INDEPENDENT-ACK — {at}\nOriginalSol{ack["delivery_id"]}/{ack["result_id"]} immutableinitialACK identitymatched actualsameactiveTurn{sn["latestTurn"]["id"]}/cursor{sn["revision"]};Master13315protected/frozen99/current9/DebugReleasePEMVID-CodeViewPDB-source4of4/threeauthorizedspansfourorderedfixedsegments matched. FreshS2normal4cases ToSnapshot4Select8/full15snapshot13redaction-policyUTC-callerpurity QA executionverdictPENDING;Program exactS1bytesSHA6614E... and fourcases formattingONLY prospectivelyindependentorderedgraphCRLF correction Mastermatched;S1raw8FAIL/OSexit1protected;initialnotbuilt statement historical. LegacyQAmetadatahelper worker_before_sha256 schemafailure archived/read-only correctedtoactualsource_before/authorized_spans/bytes,notcandidatefailure/nativeexecutionproof. NonewWP/duplicate/productionmodifyrebuild/globalSafeAwake/native/receipt/adverse execution/closure/schedulerchange;sameactualhourlyPAUSED/directcompletionpush/nextA NOT_SENTpendingS2_QA. EnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'verdict':proof['verdict'],'protected':13315,'cursor':sn['revision'],'result_id':ack['result_id'],'new_wp':False}))
