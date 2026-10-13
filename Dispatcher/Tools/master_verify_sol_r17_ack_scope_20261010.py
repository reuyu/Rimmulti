from pathlib import Path
import json,datetime,hashlib,sys
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def append(p,d):
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(d,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
delivery=c['sol_latest_delivery'];Q=Path(delivery['qa_root']);ap=Q/'ACK_INITIAL.json';ack=read(ap)
assert ack['delivery_id']==c['sol_current_attempt_id']==delivery['delivery_id']
assert ack['wp_id']==c['sol_current_wp'] and ack['wp_revision']=='S1' and ack['producer']=='Sol' and ack['status']=='ACKNOWLEDGED_IN_PROGRESS' and not ack['other_active_wp']
assert ack['result_id']=='SOL-GATE05-R17-OWNED-BOOTSTRAP-INDEPENDENT-S1-20261010-4cc8216bb6e144339a4dce4bc543d344'
sf=C/'MASTER_SOL_R17_OWNED_BOOTSTRAP_INDEPENDENT_ACK_SNAPSHOT_20261010.json';snap=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert snap['thread']['status']['type']=='active' and snap['latestTurn']['id']==delivery['actual_snapshot']['latestTurn']['id'] and snap['latestTurn']['status']=='inProgress'
assert sha(Path(delivery['wp_path']))==delivery['wp_sha256']=='01890B40A98F199DF9F8BA9FE20A2402200A365DAC2CD52D6E1C39E421676580'
base=Path(delivery['baseline_path']);assert sha(base)==delivery['baseline_sha256'];files=read(base)['files'];assert len(files)==9082
for f in files:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
before=read(Q/'PRESERVATION_BEFORE.json');assert before['protected_unique_paths']==9082 and before['baseline']['sha256']==sha(base)
assert {f['path']:(f['sha256'],f['bytes']) for f in before['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
line=read(Q/'R17_FROZEN_LINEAGE.json');master=read(C/'MASTER_GATE05_R17_OWNED_BOOTSTRAP_E1_VERIFICATION_20261010.json')['lineage']
assert len(line['candidates'])==2 and not line['candidate_executed'] and not line['original_helper_top_level_executed']
for q in line['candidates']:
 m=next(x for x in master if x['mvid']==q['mvid']);assert q['dll_sha256']==m['dll_sha256'] and q['pdb_sha256']==m['pdb_sha256'] and q['guid']==q['codeview_guid']==m['pdbGuid']==m['codeviewGuid']
 assert len(q['documents'])==4
 for d in q['documents']:
  md=next(x for x in m['documents'] if x['path']==d['path']);p=Path(d['frozen_source_path']);assert d['matched'] and md['matched'] and d['pdb_hash']==d['actual_sha256']==md['expected']==md['actual']==sha(p)
clar=H/'MASTER_R17_QA_HOST_LAUNCHER_TELEMETRY_SCOPE_CLARIFICATION_20261010.md'
assert sha(clar)=='B35BF9836E70B162571730D301CF2452F7E01F080568F80C69D0FD47414BAB59'
sendp=C/'MASTER_SOL_R17_HOST_TELEMETRY_CLARIFICATION_SEND_TOOL_20261010.json';send=read(sendp)
assert not send.get('isError',False) and json.loads(send['content'][0]['text'])['threadId']==c['sol_thread_id']
postp=C/'MASTER_SOL_R17_HOST_TELEMETRY_CLARIFICATION_POSTSEND_20261010.json';post=json.loads(read(postp)['content'][0]['text'])['polls'][0]
assert post['latestTurn']['id']==snap['latestTurn']['id'] and post['latestTurn']['status']=='inProgress'
vp=C/'MASTER_SOL_R17_OWNED_BOOTSTRAP_INDEPENDENT_ACK_SCOPE_VERIFICATION_20261010.json';assert not vp.exists()
proof={'at':at,'guard_run':'MASTER-SOL-R17-ACK-SCOPE-20261010-01','guard_session':94421,'guard_pid':23240,'delivery_id':ack['delivery_id'],'wp_id':ack['wp_id'],'wp_revision':'S1','result_id':ack['result_id'],'ack_path':str(ap),'ack_sha256':sha(ap),'actual_snapshot':snap,'protected_paths_master_rehashed':9082,'baseline_sha256':sha(base),'qa_lineage_path':str(Q/'R17_FROZEN_LINEAGE.json'),'qa_lineage_sha256':sha(Q/'R17_FROZEN_LINEAGE.json'),'master_metadata_comparison':'DebugReleaseSHA-MVID-CodeView-PDB-source4/4 matched','verdict':'ACK_VERIFIED_INDEPENDENT_R17_STATIC_POSITIVE_PURE_QA_IN_PROGRESS','clarification_path':str(clar),'clarification_sha256':sha(clar),'clarification_send_tool':str(sendp),'clarification_send_tool_sha256':sha(sendp),'clarification_delivery_status':'ACTUAL_SAME_WP_DIRECT_TOOL_ACCEPTED_SEPARATE_SOL_ACK_PENDING','clarification_postsnapshot':post,'same_wp':True,'new_wp':False,'original_wp_sha256':delivery['wp_sha256'],'host_launcher_scope':'Only newly built isolated QA pure managed runner owned child PID/numeric OS exit/argv/cwd/culture/raw-output telemetry','csharp_candidate_Process_identity_queries_allowed':False,'qa_runner_build_allowed':True,'execution_verdict':'PENDING;initial ACK not yet built is historical,not assertion of current execution count','master_candidate_build_execute':0,'runtime_e2_released':False,'closure_changed':False,'monitor':'SAME_HOURLY_PAUSED_DIRECT_QA_COMPLETION_PUSH','foundation':'HOLD'}
write(vp,proof)
c.update(sol_status=proof['verdict'],sol_current_result_id=ack['result_id'],sol_current_ack=proof,sol_last_ack=proof,last_sol_cursor=post['cursor'],updated_at=at)
c['sol_current_scope_clarification']={k:proof[k] for k in ['at','clarification_path','clarification_sha256','clarification_delivery_status','same_wp','new_wp']}
c['last_monitor_run']={'run_id':proof['guard_run'],'guard_session':94421,'guard_pid':23240,'at':at,'status':'R17_ACK_VERIFIED_SAME_WP_HOST_LAUNCH_TELEMETRY_CLARIFICATION_ACTUAL_SENT','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R17_ACK_SCOPE_GUARD_FINALLY_RELEASE_20261010.json')}
write(cp,c)
sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(ack_verified=True,explicit_ack_pending=False,current_result_id=ack['result_id'],execution_phase='IN_PROGRESS',last_runtime_observation_cursor=post['cursor'],same_wp_scope_clarification=proof['clarification_path']);s['updated_at']=at;write(sp,s)
e=dict(proof,event_id=ack['delivery_id']+'-ACK-SCOPE-VERIFIED',type='SOL_R17_ACK_VERIFIED_SAME_WP_HOST_TELEMETRY_CLARIFICATION_SENT',proof_path=str(vp),proof_sha256=sha(vp))
rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr)
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:append(p,e)
para=f'\n\n## LOCAL-SOL-R17-INDEPENDENT-ACK-AND-HOST-TELEMETRY-CLARIFICATION — {at}\nOriginal Sol {ack["delivery_id"]}/{ack["result_id"]} initial ACK matches actual same active turn {snap["latestTurn"]["id"]}/cursor {post["revision"]}. Master rehashed 9082 protected paths and compared Debug/Release SHA-MVID-CodeView-PDB source 4/4 with independent Master metadata. Current scoped QA execution verdict PENDING; no completion inherited. Same-WP host-owned new isolated pure QA runner launch telemetry/PID/numeric OS exit permitted by controlling sidecar {clar} SHA {sha(clar)}; C# runner/candidate ALL Process/VerifyProcessIdentity/self-PID queries and native/operator/global Worker startup/adverse remain forbidden. Original WP/ACK unchanged; prospective sidecar pin before final build/calls required. Direct clarification tool accepted/same actual active turn observed, separate Sol clarification ACK pending; no new WP/duplicate/production modification or scheduler change. Same hourly PAUSED/direct completion push. Engine002006/Pipeline007/current schema/G-Q1 OPEN, Foundation HOLD/no runtime E2/closure. Proof {vp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
print(json.dumps({'verdict':proof['verdict'],'protected':9082,'cursor':post['revision'],'result_id':ack['result_id'],'clarification':'SENT_SAME_WP_ACK_PENDING','new_wp':False},ensure_ascii=True))
