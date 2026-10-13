from pathlib import Path
import json,hashlib,datetime,tomllib,sys
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R25-QA-COMPLETE-20261011-01';PID=32068;SESSION=71407;PREFIX='MASTER_SOL_R25_ROLE_USERDATA_S2_'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def data(p):return json.loads(read(p)['content'][0]['text'])
def event(e):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);stage=sys.argv[1]
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
if stage=='sending':
 op=c['active_operation'];assert op['type']=='SOL_R25_ROLE_USERDATA_S2' and op['wp_revision']=='S2' and not op['unknown_delivery']
 pre=data(C/(PREFIX+'PREDISPATCH_20261011.json'))['polls'][0];assert pre['thread']['id']==c['sol_thread_id'] and pre['thread']['status']['type']=='idle' and pre['latestTurn']['status']=='completed'
 for k in ['wp','baseline']:assert sha(Path(op[k+'_path']))==op[k+'_sha256']
 op.update(delivery_status='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL',unknown_delivery=True,actual_predispatch=pre,attempt_started_at=at);write(cp,c);event({'at':at,'event_id':op['delivery_id']+'-ATTEMPT','type':'SOL_R25_S2_DIRECT_DELIVERY_ATTEMPT','unknown_delivery':True});print('ONE_DELIVERY_PENDING_TOOL')
elif stage=='sent':
 op=c['active_operation'];assert op['unknown_delivery'] and op['wp_revision']=='S2'
 paths={k:C/(PREFIX+n+'_20261011.json') for k,n in [('pre','PREDISPATCH'),('tool','SEND_TOOL'),('post','POSTSEND')]};pre=data(paths['pre'])['polls'][0];post=data(paths['post'])['polls'][0]
 assert not read(paths['tool']).get('isError') and post['thread']['id']==c['sol_thread_id'] and post['latestTurn']['id']!=pre['latestTurn']['id'] and post['thread']['status']['type']=='active' and post['latestTurn']['status']=='inProgress'
 proof=dict(op,at=at,delivery_status='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN',unknown_delivery=False,status='SENT_IN_PROGRESS_ACK_PENDING',actual_snapshot=post,scope='EXACT_UNCHANGED_R25_NEW_S2_PROSPECTIVE_WINDOWS_CRLF_PRETTY_ORACLE_ONLY_FRESH_NORMAL4',production_modify_build=0,full_runtime_e2_released=False,closure_changed=False,foundation='HOLD',monitor='ACTUAL_PAUSED60MIN')
 for k,p in paths.items():proof[k+'_path']=str(p);proof[k+'_sha256']=sha(p)
 vp=C/(PREFIX+'DELIVERY_VERIFICATION_20261011.json');assert not vp.exists();write(vp,proof)
 c.update(active_operation=None,sol_current_attempt_id=op['delivery_id'],sol_current_wp=op['wp_id'],sol_current_revision='S2',sol_current_result_id=None,sol_status='R25_S2_WINDOWS_PRETTY_ORACLE_FRESH_NORMAL_QA_SENT_ACK_PENDING',sol_current_ack=None,sol_current_delivery=proof,sol_latest_delivery=proof,last_sol_cursor=post['cursor'],sol_next_wp_prepared=None,sol_next_action='AWAIT_R25_S2_NEW_RAW_BYTE_QA_RESULT_THEN_MASTER_DISPOSITION_AND_AUTOMATIC_M04_NEXT',updated_at=at)
 c['last_monitor_run']={'run_id':RUN,'guard_session':SESSION,'guard_pid':PID,'at':at,'status':'R25_S1_RAWFAIL_DISPOSED_S2_FRESH_ORACLE_QA_SENT_PAUSED','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R25_S1_COMPLETE_S2_GUARD_FINALLY_RELEASE_20261011.json')};write(cp,c)
 sp=H/'DISPATCHER_STATE.json';st=read(sp)
 for x in st['deliveries']:
  if x.get('delivery_id')=='SOL-GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011-01':x.update(status='COMPLETED_MASTER_DISPOSED_TYPED_PASS_RAW_BYTE_FAIL',completed_result_id=c['sol_latest_completion']['result_id'],master_review=c['sol_latest_completion']['master_review_path'])
 st['endpoints']['sol'].update(current_wp=op['wp_id'],current_wp_revision='S2',current_delivery_id=op['delivery_id'],current_result_id=None,current_turn_id=post['latestTurn']['id'],actual_turn_id=post['latestTurn']['id'],execution_phase='IN_PROGRESS',ack_verified=False,explicit_ack_pending=True,current_runtime_idle_verified=False,last_runtime_observation_cursor=post['cursor']);st['master_monitor_automation']=c['master_monitor_automation'];st['deliveries'].append({'delivery_id':op['delivery_id'],'recipient':'Sol','wp_id':op['wp_id'],'wp_revision':'S2','delivery_status':'SENT','status':'ACTIVE_ACK_PENDING','proof':str(vp),'runtime_e2_released':False});st['updated_at']=at;write(sp,st)
 e={'at':at,'event_id':op['delivery_id']+'-ACTUAL_SENT','type':'SOL_R25_S2_NEW_NORMAL_PRETTY_ORACLE_QA_ACTUAL_SENT','delivery_id':op['delivery_id'],'proof':str(vp),'proof_sha256':sha(vp),'turn_id':post['latestTurn']['id'],'cursor':post['cursor'],'protected':op['protected_unique_paths'],'no_duplicate_wp':True}
 rp=R/'Dispatcher/MASTER_RECEIPTS.json';rr=read(rp);assert not any(x.get('event_id')==e['event_id'] for x in rr['processed_dispatch_events']);rr['processed_dispatch_events'].append(e);rr['updated_at']=at;write(rp,rr);event(e)
 para=f'\n\n## LOCAL-R25-S1-DISPOSED-S2-FRESH-QA-ACTUAL-SENT — {at}\nOriginalSol{op["delivery_id"]}/{op["wp_id"]}/S2 actualdirectSENT/newturn{post["latestTurn"]["id"]}/cursor{post["revision"]}/ACKpending/no duplicate. Exactunchangedfrozen99DebugA9C31...MVID5553a632-0557-433f-8840-bb12875cf577 only;S1actual32PASS4FAILeachOSexit1and1824typed0mismatch Masteracceptedscopedselector-copy-values/raw8FAILpreserved. NewtechnicalWindowsprettyCRLForaclefromprimarysource/newS2same4normalinputs-typedgraphs/sameQAProgramlogic clone/finalbuild1-new2cultures/fullprospective rawbyteproof/noactualnormalization-or-outputcopy. Protected13315includesALLS1rawfail-oracle-source-runner-returngraph;QAnewline defectOPEN/nextA NOT_SENTpendingS2. ActualhourlyPAUSED/directcompletionpush/productionmodifybuild0/GlobalSafeAwake-nativeProcess-receipt-adverse0/EnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED/no newclosure. Proof{vp}\n'
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with p.open('a',encoding='utf8') as f:f.write(para)
 p=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';p.write_text(f'Current{at}: R25S1typedselectorgraphPASS/rawbyteFAILpreserved QAWindowsnewlineoracledefectOPEN. NewR25S2actualSENTturn{post["latestTurn"]["id"]}/cursor{post["revision"]}/ACKpending/samecandidate. NextA NOT_SENTpendingS2/directautomaticfollowup/samehourlyPAUSED/FoundationHOLD/fullGateE2NOTRELEASED.\n\n'+p.read_text(encoding='utf-8-sig'),encoding='utf8')
 print(json.dumps(e))
elif stage=='audit':
 d=c['sol_current_delivery'];assert c['active_operation'] is None and d['wp_revision']=='S2' and not d['unknown_delivery']
 for k in ['wp','baseline','pre','tool','post']:assert sha(Path(d[k+'_path']))==d[k+'_sha256']
 rr=read(R/'Dispatcher/MASTER_RECEIPTS.json');old=c['sol_latest_completion'];assert sum(x.get('result_id')==old['result_id'] for x in rr['processed_results'])==1 and sum(x.get('event_id')==d['delivery_id']+'-ACTUAL_SENT' for x in rr['processed_dispatch_events'])==1
 dest=C/'MASTER_R25_S1_COMPLETE_S2_SENT_FINAL_AUDIT_20261011.json';assert not dest.exists();write(dest,{'at':at,'guard_run':RUN,'guard_session':SESSION,'guard_pid':PID,'S1_terminal_receipt_deduped':1,'S2_delivery_deduped':1,'S2_actual':d['actual_snapshot'],'S2_ACK':'PENDING','protected':13315,'production_modify_build':0,'S1_raw_OS_exits':[1,1],'S1_rawFAIL_preserved':True,'QA_newline_defect':'OPEN','scheduler_actual':cfg,'full_runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD','finally_release':'PENDING'});event({'at':at,'event_id':d['delivery_id']+'-FINAL-AUDIT','type':'R25_S1_DISPOSED_S2_ACTUAL_SENT','proof':str(dest),'proof_sha256':sha(dest)});print('S2_FINAL_AUDIT_MATCHED')
elif stage=='released':
 p=C/'MASTER_R25_S1_COMPLETE_S2_GUARD_FINALLY_RELEASE_20261011.json';raw=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json')
 assert raw['exit_code']==0 and '"status": "RELEASED"' in raw['output'] and RUN in raw['output'] and info['status']=='RELEASED' and info['run_id']==RUN and info['pid']==PID and c['last_monitor_run']['run_id']==RUN
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],all_child_commands_completed_before_release=True);write(cp,c);event({'at':at,'event_id':RUN+'-RELEASE','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':RUN,'pid':PID,'proof':str(p)});print('ACTUAL_GUARD_RELEASE_RECORDED')
else:raise ValueError(stage)
