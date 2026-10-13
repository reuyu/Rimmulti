from pathlib import Path
import json,datetime,hashlib,tomllib,sys
sys.stdout.reconfigure(encoding='utf8');R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def data(p):return json.loads(read(p)['content'][0]['text'])
def append(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);op=c['active_operation'];stage=sys.argv[1];prefix='MASTER_SOL_R18_CONFIG_ADMISSION_SEAL_INDEPENDENT_'
if stage=='pause_sending':
 cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
 assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id'] and cfg['name']=='WarEconomy Master 통합 작업 확인'
 assert not read(C/'MASTER_R18_TERMINAL_PAUSE_TOOL_20261010.json').get('isError')
 vp=C/'MASTER_R18_TERMINAL_PAUSED_CONFIG_VERIFICATION_20261010.json';assert not vp.exists()
 write(vp,{'at':at,'actual_config':cfg,'reason':'R18A terminal Masterdisposed;directSol freshindependentQAcontinues','guard_session':41964,'guard_pid':11096})
 c['master_monitor_automation'].update(status='PAUSED',desired_status='PAUSED',configuration_verified=True,configuration_checked_at=at,configuration_proof=str(vp),pause_reason='R18terminalreviewed/directindependentQA')
 bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);b['tasks'][-1].update(monitor_status='PAUSED60MIN_VERIFIED',monitor_configuration_proof=str(vp));b['updated_at']=at;write(bp,b)
 pre=data(C/(prefix+'PREDISPATCH_20261010.json'))['polls'][0]
 assert pre['thread']['id']=='01a11583-ff90-73e0-8916-d021e2bb038d' and pre['thread']['status']['type']=='idle' and pre['latestTurn']['status']=='completed' and pre['revision']==112
 assert op['delivery_status']=='PREPARED_NOT_SENT' and not op['unknown_delivery'] and sha(Path(op['wp_path']))==op['wp_sha256'] and sha(Path(op['baseline_path']))==op['baseline_sha256']
 base=read(Path(op['baseline_path']));assert len(base['files'])==op['protected_unique_paths']==9374
 for f in base['files']:
  q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['bytes']
 op.update(delivery_status='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL',unknown_delivery=True,actual_predispatch=pre,attempt_started_at=at)
 c['updated_at']=at;write(cp,c)
 append({'at':at,'event_id':op['delivery_id']+'-ATTEMPT','type':'SOL_R18_DIRECT_DELIVERY_ATTEMPT_HOURLY_PAUSED','delivery_id':op['delivery_id'],'wp_sha256':op['wp_sha256'],'baseline_sha256':op['baseline_sha256'],'baseline_count':9374,'unknown_delivery':True})
 print(json.dumps({'status':'PAUSED60MIN_DELIVERY_PENDING_TOOL','delivery_id':op['delivery_id'],'wp_sha':op['wp_sha256'],'baseline':9374}))
elif stage=='sent':
 assert op['delivery_status']=='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL' and op['unknown_delivery']
 paths={k:C/(prefix+n+'_20261010.json') for k,n in [('pre','PREDISPATCH'),('tool','SEND_TOOL'),('post','POSTSEND')]}
 pre=data(paths['pre'])['polls'][0];post=data(paths['post'])['polls'][0]
 assert not read(paths['tool']).get('isError') and post['thread']['status']['type']=='active' and post['latestTurn']['status']=='inProgress' and post['latestTurn']['id']!=pre['latestTurn']['id']
 proof=dict(op,at=at,delivery_status='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN',unknown_delivery=False,status='SENT_IN_PROGRESS_ACK_PENDING',actual_snapshot=post,protected_paths_master_rehashed=9374,scope='R18_FROZEN_STATIC_POSITIVE_PURE_CONFIG_ADMISSION_SNAPSHOT_FILEHASH_REDACTION_NO_PROCESS_GLOBALSTARTUP_NATIVE',qa_owned_runner_build_allowed=True,production_modify_build=0,full_runtime_e2_released=False,closure_changed=False,foundation='HOLD',monitor='ACTUAL_PAUSED60MIN')
 for k,q in paths.items():proof[k+'_path']=str(q);proof[k+'_sha256']=sha(q)
 vp=C/(prefix+'DELIVERY_VERIFICATION_20261010.json');assert not vp.exists();write(vp,proof)
 c.update(active_operation=None,sol_current_attempt_id=op['delivery_id'],sol_current_wp=op['wp_id'],sol_current_result_id=None,sol_status='R18_FRESH_INDEPENDENT_STATIC_POSITIVE_PURE_CONFIG_ADMISSION_QA_SENT_IN_PROGRESS_ACK_PENDING',sol_current_ack=None,sol_current_delivery=proof,sol_latest_delivery=proof,last_sol_cursor=post['cursor'],sol_next_wp_prepared=None,sol_next_action='AWAIT_DIRECT_R18_QA_COMPLETION_THEN_MASTER_VERIFY_DISPOSE_NECESSARY_BOUNDED_A_CORRECTION_AUTOMATICALLY',updated_at=at)
 c['last_monitor_run']={'run_id':op['guard_run'],'guard_session':41964,'guard_pid':11096,'at':at,'status':'R18_A_TERMINAL_REVIEWED_FROZEN_PAUSED_ORIGINAL_SOL_FRESH_QA_ACTUAL_SENT','trigger_received_at':'2026-10-10T06:37:48.784Z','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R18_HEARTBEAT_GUARD_FINALLY_RELEASE_20261010.json')};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';s=read(sp);s['endpoints']['sol'].update(current_wp=op['wp_id'],current_delivery_id=op['delivery_id'],current_result_id=None,current_turn_id=post['latestTurn']['id'],actual_turn_id=post['latestTurn']['id'],execution_phase='IN_PROGRESS',ack_verified=False,explicit_ack_pending=True,current_runtime_idle_verified=False,last_runtime_observation_cursor=post['cursor'])
 s['master_monitor_automation']=c['master_monitor_automation'];s['deliveries'].append({'delivery_id':op['delivery_id'],'recipient':'Sol','wp_id':op['wp_id'],'wp_revision':'S1','delivery_status':'SENT','status':'ACTIVE_ACK_PENDING','proof':str(vp),'runtime_e2_released':False});s['updated_at']=at;write(sp,s)
 e={'at':at,'event_id':op['delivery_id']+'-ACTUAL_SENT','type':'SOL_R18_FRESH_SCOPED_INDEPENDENT_QA_ACTUAL_SENT','delivery_id':op['delivery_id'],'proof':str(vp),'proof_sha256':sha(vp),'turn_id':post['latestTurn']['id'],'cursor':post['cursor'],'protected':9374,'no_duplicate_wp':True}
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in r['processed_dispatch_events']);r['processed_dispatch_events'].append(e);r['updated_at']=at;write(rp,r);append(e)
 para=f'\n\n## LOCAL-R18-TERMINAL-PAUSED-SOL-FRESH-INDEPENDENT-SENT — {at}\nOriginal Sol {op["delivery_id"]}/{op["wp_id"]}/S1 actualdirectSENT/newactive{post["latestTurn"]["id"]}/cursor{post["revision"]};ACKpending/no substitute/duplicate. FrozenR18DebugAE7B.../MVID9e8501fc-d16e-413b-8682-17ba8550d9bf/PDB86E10.../92freezeSHAC558CC57.../9374baselineSHA{op["baseline_sha256"]} Masterrehashed. IndependentSTATIC+positivePUREnormal config ParseStrict/admitbyte-fileSHA/explicitdescriptor/detachedsnapshot fulltyped ownership-policy/redaction-filehash-limitedcodec;normal opaque spaces-UnicodepolicyID/revision mustpreservefixedCensuscontract,nooutput-drivenoraclefix. Externalhost onlyfreshQA-ownedpuremanagedrunnerchild telemetryallowed inline;ALLC#Process/globalWorkerinstaller-ActiveStartup-Awake-bootstrap/native-game-adverse/productionbuild0. A sourceimprovementscredited/remainingmissing-config trusted readiness+origin-schema-Trim+role-context-native OPEN;historicalstaleselfinventory/partialgraph preserved. SameactualhourlyPAUSED60min/173char/correctname-target/directSolcompletionpushcontinues. NewAcorrectiveWP NOT_SENT pendingfreshindependentfindings;Masterautomaticverification/disposition/nextnecessaryboundedwork,no routinehumancontinue. Engine002006/Pipeline007/schema/G-Q1OPEN/FoundationHOLD/fullGateE2NOTRELEASED/no closure. Proof {vp}\n'
 for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with q.open('a',encoding='utf8') as f:f.write(para)
 pointer=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md'
 pointer.write_text(f'Current {at}: R18terminal23artifacts/frozen92/configcopy-byteSHA-schema staticcredit/bootstraprevisionrequired/opaqueTrim andmissingtrustedgate/origin-schema gaps/nativeUNTESTED. OriginalSol freshR18static-positivePUREconfig-admission-snapshot helpers actualSENT/newturn{post["latestTurn"]["id"]}/cursor{post["revision"]},ACKpending/9374baseline. SameactualhourlyPAUSED60min;directcompletionpushcontinues. No newA untilindependentfindings;Masterautomaticreview/disposition/boundedfollowup,nohumancontinue. Productionbuild0/native/fullGateE2NOTRELEASED/FoundationHOLD/Engine002006/Pipeline007/schema/G-Q1OPEN/no closure.\n\n'+pointer.read_text(encoding='utf-8-sig'),encoding='utf8')
 print(json.dumps(e,ensure_ascii=True))
else:raise ValueError(stage)

