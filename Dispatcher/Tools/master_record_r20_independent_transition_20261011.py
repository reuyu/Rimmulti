from pathlib import Path
import json, datetime, hashlib, tomllib, sys, re
sys.stdout.reconfigure(encoding='utf8')
R = Path(__file__).resolve().parents[2]
H = R/'docs/WarEconomy_Master_Handoff_20261006'
C = H/'coordination'
prefix = 'MASTER_SOL_R20_TRUSTED_STARTUP_INDEPENDENT_'
RUN = 'MASTER-HEARTBEAT-R20-20261010T204031Z-01'
PID, SESSION = 8144, 61701
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def data(p): return json.loads(read(p)['content'][0]['text'])
def event(e):
    for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
        with p.open('a',encoding='utf8') as f: f.write(json.dumps(e,ensure_ascii=False)+'\n')
def config():
    cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'))
    assert cfg['status']=='PAUSED' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1'
    assert len(cfg['prompt'])==173 and cfg['target_thread_id']=='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
    assert cfg['name']=='WarEconomy Master 통합 작업 확인'
    return cfg
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json'
c=read(cp)
stage=sys.argv[1]
if stage=='pause_sending':
    op=c['active_operation']
    assert op['delivery_id']=='SOL-GATE05-R20-TRUSTED-STARTUP-INDEPENDENT-S1-20261011-01'
    cfg=config()
    assert not read(C/'MASTER_R20_TERMINAL_PAUSE_TOOL_20261011.json').get('isError')
    vp=C/'MASTER_R20_TERMINAL_PAUSED_CONFIG_VERIFICATION_20261011.json'
    assert not vp.exists()
    write(vp,{'at':at,'actual_config':cfg,'reason':'R20 A terminal reviewed; fresh independent Sol QA continues directly','guard_session':SESSION,'guard_pid':PID})
    c['master_monitor_automation'].update(status='PAUSED',desired_status='PAUSED',configuration_verified=True,configuration_checked_at=at,configuration_proof=str(vp),pause_reason='R20 terminal reviewed/direct independent QA')
    bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp)
    assert b['tasks'][-1]['dispatch_id'].endswith('e35ff656')
    b['tasks'][-1].update(monitor_status='PAUSED60MIN_VERIFIED',monitor_configuration_proof=str(vp));b['updated_at']=at;write(bp,b)
    pre=data(C/(prefix+'PREDISPATCH_20261011.json'))['polls'][0]
    assert pre['thread']['id']==c['sol_thread_id'] and pre['thread']['status']['type']=='idle' and pre['latestTurn']['status']=='completed' and pre['revision']==124
    assert op['delivery_status']=='PREPARED_NOT_SENT' and not op['unknown_delivery']
    assert sha(Path(op['wp_path']))==op['wp_sha256']=='3CF8C1741BD40BB06985C4ED3EFB18BA30896EB187AD6521218F0727CE539782'
    assert sha(Path(op['baseline_path']))==op['baseline_sha256']=='FD284886A8E6F08D063D845BE8962A6A06CE526C70B34562F8370B380DB9D1E4'
    base=read(Path(op['baseline_path']))
    assert len(base['files'])==op['protected_unique_paths']==10346
    for f in base['files']:
        q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['bytes']
    op.update(delivery_status='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL',unknown_delivery=True,actual_predispatch=pre,attempt_started_at=at)
    c['updated_at']=at;write(cp,c)
    event({'at':at,'event_id':op['delivery_id']+'-ATTEMPT','type':'SOL_R20_DIRECT_DELIVERY_ATTEMPT_HOURLY_PAUSED','delivery_id':op['delivery_id'],'wp_sha256':op['wp_sha256'],'baseline_sha256':op['baseline_sha256'],'baseline_count':10346,'unknown_delivery':True})
    print(json.dumps({'status':'PAUSED60MIN_DELIVERY_PENDING_TOOL','delivery_id':op['delivery_id'],'baseline':10346}))
elif stage=='sent':
    op=c['active_operation'];assert op['delivery_status']=='DELIVERY_ATTEMPT_PENDING_ACTUAL_TOOL' and op['unknown_delivery']
    paths={k:C/(prefix+n+'_20261011.json') for k,n in [('pre','PREDISPATCH'),('tool','SEND_TOOL'),('post','POSTSEND')]}
    pre=data(paths['pre'])['polls'][0];post=data(paths['post'])['polls'][0]
    assert not read(paths['tool']).get('isError')
    assert post['thread']['id']==c['sol_thread_id'] and post['thread']['status']['type']=='active' and post['latestTurn']['status']=='inProgress'
    assert post['latestTurn']['id']!=pre['latestTurn']['id']
    proof=dict(op,at=at,delivery_status='SENT_ACTUAL_TOOL_NEW_ACTIVE_TURN',unknown_delivery=False,status='SENT_IN_PROGRESS_ACK_PENDING',actual_snapshot=post,protected_paths_master_rehashed=10346,scope='R20_FROZEN_STATIC_POSITIVE_PURE_TRUSTED_STARTUP_EXPLICIT_DESCRIPTOR_RECEIPT_FULL_GRAPH_AND_NORMAL_OPAQUE_REGRESSION_NO_PROCESS_GLOBALSTARTUP_NATIVE',qa_owned_runner_build_allowed=True,production_modify_build=0,full_runtime_e2_released=False,closure_changed=False,foundation='HOLD',monitor='ACTUAL_PAUSED60MIN')
    for k,q in paths.items(): proof[k+'_path']=str(q);proof[k+'_sha256']=sha(q)
    vp=C/(prefix+'DELIVERY_VERIFICATION_20261011.json');assert not vp.exists();write(vp,proof)
    c.update(active_operation=None,sol_current_attempt_id=op['delivery_id'],sol_current_wp=op['wp_id'],sol_current_result_id=None,sol_status='R20_FRESH_INDEPENDENT_STATIC_POSITIVE_PURE_TRUSTED_STARTUP_QA_SENT_IN_PROGRESS_ACK_PENDING',sol_current_ack=None,sol_current_delivery=proof,sol_latest_delivery=proof,last_sol_cursor=post['cursor'],sol_next_wp_prepared=None,sol_next_action='AWAIT_DIRECT_R20_QA_COMPLETION_THEN_MASTER_VERIFY_DISPOSE_NEXT_BOUNDED_TRUSTED_STARTUP_ORIGIN_WORK_AUTOMATICALLY',updated_at=at)
    c['last_monitor_run']={'run_id':RUN,'guard_session':SESSION,'guard_pid':PID,'at':at,'status':'R20_A_TERMINAL_REVIEWED_FROZEN_PAUSED_ORIGINAL_SOL_FRESH_QA_ACTUAL_SENT','trigger_received_at':'2026-10-10T20:40:31.261Z','release_status':'PENDING_ACTUAL_FINALLY','release_proof_path':str(C/'MASTER_R20_HEARTBEAT_GUARD_FINALLY_RELEASE_20261011.json')}
    write(cp,c)
    sp=H/'DISPATCHER_STATE.json';s=read(sp)
    s['endpoints']['sol'].update(current_wp=op['wp_id'],current_delivery_id=op['delivery_id'],current_result_id=None,current_turn_id=post['latestTurn']['id'],actual_turn_id=post['latestTurn']['id'],execution_phase='IN_PROGRESS',ack_verified=False,explicit_ack_pending=True,current_runtime_idle_verified=False,last_runtime_observation_cursor=post['cursor'])
    s['master_monitor_automation']=c['master_monitor_automation']
    s['deliveries'].append({'delivery_id':op['delivery_id'],'recipient':'Sol','wp_id':op['wp_id'],'wp_revision':'S1','delivery_status':'SENT','status':'ACTIVE_ACK_PENDING','proof':str(vp),'runtime_e2_released':False})
    s['updated_at']=at;write(sp,s)
    e={'at':at,'event_id':op['delivery_id']+'-ACTUAL_SENT','type':'SOL_R20_FRESH_SCOPED_INDEPENDENT_QA_ACTUAL_SENT','delivery_id':op['delivery_id'],'proof':str(vp),'proof_sha256':sha(vp),'turn_id':post['latestTurn']['id'],'cursor':post['cursor'],'protected':10346,'no_duplicate_wp':True}
    rp=R/'Dispatcher/MASTER_RECEIPTS.json';r=read(rp)
    assert not any(x.get('event_id')==e['event_id'] for x in r['processed_dispatch_events'])
    r['processed_dispatch_events'].append(e);r['updated_at']=at;write(rp,r);event(e)
    para=f'\n\n## LOCAL-R20-TERMINAL-PAUSED-SOL-INDEPENDENT-SENT — {at}\nOriginal Sol {op["delivery_id"]}/{op["wp_id"]}/S1 actualdirectSENT/newturn{post["latestTurn"]["id"]}/cursor{post["revision"]},ACKpending/no duplicate/substitute. Frozen109SHA03BD6923.../selectedDebug482166A77BF90569626A5CB27D83A4D949BD57DA85BA660F03067C833FB777F0/MVID9e516c44-35c8-49b8-b3ec-f73ec58ba12f/PDBEC057...source4/4/10346protected Masterrehashed. Missing startup guards and receipt wiring sourcecredit; explicit descriptor defaults/optional fields/internalconstructor provenance/static strictness remainqualifiedOPEN. Producer TEST05 7invalidhelpercases each out of positive-only scope preserved/no replay;current14nonself stream inventories match/manual83 notprofiler/no fullprospective originalgraph. Fresh independentSTATIC+normalPUREfullyspecified descriptor/8receiptcases full11properties-redaction/nested15snapshot/13snapshot-redaction/25result/bounded16normal opaque regression;newQA-ownedrunner allowed,ALL productionmodifybuild/C#Process/globalstartup-installer-ActiveReceipt-Awake/native/adverse0. Historical R19 scoped opaque defectCLOSED notinheritedR20PASS. Same actualhourlyPAUSED60min/173char/correcttarget/directcompletionpush; nextA NOT_SENT pending QA. WholeEngine002006/Pipeline007/schema/G-Q1OPEN/FoundationHOLD/fullnativeGateE2NOTRELEASED/no broaderclosure. Proof {vp}\n'
    for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
        with q.open('a',encoding='utf8') as f: f.write(para)
    pointer=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md'
    pointer.write_text(f'Current {at}: R20 A terminal109 frozen/29artifacts,missing startup guard+receipt sourcecredit/explicit declaration revision required/producer14invalid helpercalls preserved. OriginalSol new R20 exact independentSTATIC+positivePURE receipt fullgraph and boundedopaque regression actual SENT/newturn{post["latestTurn"]["id"]}/cursor{post["revision"]}/ACKpending/10346protected. Samehourly PAUSED/directcompletionpush, nextA pendingQA Masterdisposition automatic/nohumancontinue. HistoricalR19opaque scopedCLOSED/wholeEngine002006-Pipeline007-schema-GQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED.\n\n'+pointer.read_text(encoding='utf-8-sig'),encoding='utf8')
    print(json.dumps(e,ensure_ascii=True))
elif stage=='audit':
    assert c['active_operation'] is None
    cfg=config();v=c['sol_current_delivery'];assert v['wp_id']=='WP_QA_ENGINE_GATE05_R20_TRUSTED_STARTUP_INDEPENDENT' and not v['unknown_delivery']
    for key in ['wp','baseline','pre','tool','post']: assert sha(Path(v[key+'_path']))==v[key+'_sha256']
    t=read(R/'Dispatcher/MASTER_A_TASKS.json')['tasks'][-1]
    assert t['dispatch_id'].endswith('e35ff656') and t['monitor_status']=='PAUSED60MIN_VERIFIED'
    ev=read(C/'MASTER_GATE05_R20_TRUSTED_STARTUP_E1_VERIFICATION_20261011.json');assert ev['verification_status']=='MASTER_DISPOSED'
    receipts=read(R/'Dispatcher/MASTER_RECEIPTS.json')
    assert sum(x.get('result_id')=='WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-RESULT-01' for x in receipts['processed_results'])==1
    assert sum(x.get('event_id')==v['delivery_id']+'-ACTUAL_SENT' for x in receipts['processed_dispatch_events'])==1
    assert read(C/'MASTER_DEFECT_ENGINE_G05_OPAQUE_R18_20261010.json')['status']=='CLOSED'
    q=C/'MASTER_R20_QA_CURRENT_PROGRESS_SNAPSHOT_20261011.json';s=data(q)['polls'][0]
    assert s['thread']['id']==c['sol_thread_id'] and s['latestTurn']['id']==v['actual_snapshot']['latestTurn']['id']
    assert s['thread']['status']['type']=='active' and s['latestTurn']['status']=='inProgress'
    c.update(last_sol_cursor=s['cursor'],sol_last_observation={'at':at,'path':str(q),'actual_snapshot':s,'explicit_ACK':'PENDING_SEPARATE_IDENTITY_PROOF'},updated_at=at);write(cp,c)
    sp=H/'DISPATCHER_STATE.json';d=read(sp);d['endpoints']['sol']['last_runtime_observation_cursor']=s['cursor'];d['updated_at']=at;write(sp,d)
    dest=C/'MASTER_R20_TERMINAL_QA_SENT_COORDINATION_AUDIT_20261011.json';assert not dest.exists()
    write(dest,{'at':at,'run_id':RUN,'guard_session':SESSION,'guard_pid':PID,'A_result_dedupe_count':1,'Sol_delivery_dedupe_count':1,'Sol_actual':s,'Sol_ACK':'PENDING','scheduler_actual':cfg,'protected_paths':10346,'scoped_defect':'R19_SCOPED_CLOSED_NO_INHERITED_R20_VERDICT','next_A':'NOT_SENT_PENDING_INDEPENDENT_QA','actual_guard_finally_release':'PENDING','full_runtime_e2_released':False,'closure_changed':False,'foundation':'HOLD'})
    event({'at':at,'event_id':v['delivery_id']+'-FINAL-AUDIT','type':'R20_TERMINAL_FROZEN_PAUSED_SOL_FRESH_QA_SENT','proof':str(dest),'proof_sha256':sha(dest)})
    print('R20_TERMINAL_PAUSED_ORIGINAL_SOL_ACTIVE_ACK_PENDING_AWAIT_FRESH_QA')
elif stage=='released':
    q=C/'MASTER_R20_HEARTBEAT_GUARD_FINALLY_RELEASE_20261011.json';r=read(q)['actual_release_tool'];raw=r['output']
    pid_match=re.search(r'id"\s*:\s*8144\b',raw) or re.search(r'"pid":\s*[0-9]+\r?\n\x1b\[[0-9;]+H8144\b',raw)
    assert r['exit_code']==0 and '"status": "RELEASED"' in raw and f'"run_id": "{RUN}"' in raw and pid_match
    released_at=re.search(r'"released_at"\s*:\s*"([^"]+)"',raw).group(1)
    c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=released_at,release_proof_path=str(q),all_child_commands_completed_before_release=True);c['updated_at']=at;write(cp,c)
    audit=C/'MASTER_R20_TERMINAL_QA_SENT_COORDINATION_AUDIT_20261011.json';d=read(audit);d.update(actual_guard_finally_release='RELEASED_HELPER_EXIT0',release_proof=str(q));write(audit,d)
    event({'at':at,'event_id':'MASTER-R20-HEARTBEAT-GUARD-RELEASE-20261011-01','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','run_id':RUN,'pid':PID,'proof':str(q),'all_child_commands_completed_before_release':True})
    print('ACTUAL_R20_GUARD_FINALLY_RELEASE_RECORDED_EXIT0')
else: raise ValueError(stage)
