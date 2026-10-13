from pathlib import Path
import json,datetime,hashlib,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def payload(result):return json.loads(next(x['text'] for x in result['content'] if x['type']=='text' and x['text'].startswith('{')))
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
send=C/'MASTER_SOL_R4_INDEPENDENT_S1_SEND_TOOL_20261008.json';post=C/'MASTER_SOL_R4_INDEPENDENT_S1_POSTSEND_20261008.json';before=C/'MASTER_SOL_R4_INDEPENDENT_S1_PREDISPATCH_20261008.json'
assert not load(send).get('isError',False)
prior=payload(load(before))['polls'][0];current=payload(load(post))['polls'][0]
assert prior['latestTurn']['status']=='failed' and current['latestTurn']['status']=='inProgress' and current['latestTurn']['id']!=prior['latestTurn']['id']
wp=H/'WP_QA_ENGINE_GATE05_R4_INDEPENDENT_REVIEW_S1.md'
proof={'at':at,'delivery_id':'SOL-GATE05-R4-INDEPENDENT-REVIEW-S1-20261008-01','wp_id':'WP_QA_ENGINE_GATE05_R4_INDEPENDENT_REVIEW','wp_revision':'S1','wp_path':str(wp),'wp_sha256':sha(wp),'status':'SENT_IN_PROGRESS_ACK_PENDING','recipient_thread_id':'01a11583-ff90-73e0-8916-d021e2bb038d','turn_id':current['latestTurn']['id'],'cursor':current['cursor'],'predispatch':str(before),'predispatch_sha256':sha(before),'send_tool_proof':str(send),'send_tool_sha256':sha(send),'postsend':str(post),'postsend_sha256':sha(post),'runtime_e2_released':False,'new_a_wp':'NOT_SENT_PENDING_INDEPENDENT_REVIEW','monitor':'PAUSED60MIN_ACTUAL_CONFIG_VERIFIED','closure_changed':False,'operational_recovery':'NEW_TURN_STARTED; explicit ACK pending; old usage failure not current active status'}
p=C/'MASTER_SOL_R4_INDEPENDENT_S1_DELIVERY_VERIFICATION_20261008.json';save(p,proof)
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=load(cp)
assert c['active_operation']['operation_id']=='SOL-R4-INDEPENDENT-S1-SEND-20261008-01'
c.update(active_operation=None,sol_last_wp=c.get('sol_current_wp'),sol_current_wp=proof['wp_id'],sol_current_attempt_id=proof['delivery_id'],sol_status=proof['status'],last_sol_cursor=proof['cursor'],sol_current_delivery=proof,sol_runtime_observation=current,updated_at=at)
c['sol_recovery']['status']='ORIGINAL_ENDPOINT_NEW_R4_TURN_STARTED_ACK_PENDING'
save(cp,c)
sp=H/'DISPATCHER_STATE.json';s=load(sp);s['updated_at']=at;s['latest_master_dispatch']=proof;s['master_monitor_automation']=c['master_monitor_automation']
s['endpoints']['sol'].update(current_wp=proof['wp_id'],current_delivery_id=proof['delivery_id'],execution_phase='IN_PROGRESS',runtime_delivery_verified=True,operational_ready=True,operational_ready_basis='actual new active turn; ACK pending',current_turn_id=proof['turn_id'])
s['deliveries'].append({'delivery_id':proof['delivery_id'],'recipient':'sol','work_package':proof['wp_id'],'revision':'S1','status':proof['status'],'delivery_status':'SENT','thread_id':proof['recipient_thread_id'],'host_id':'local','turn_id':proof['turn_id'],'observed_at':at,'tool_proof':str(send),'turn_proof':str(post),'verification':str(p),'runtime_verdict':'NOT_RELEASED_STATIC_ONLY','duplicate_retry':False})
save(sp,s)
rp=R/'Dispatcher/MASTER_RECEIPTS.json';receipts=load(rp);event=dict(proof,event_id=proof['delivery_id']+'-SENT',type='SOL_FRESH_R4_INDEPENDENT_STATIC_REVIEW_DISPATCH',proof=str(p),proof_sha256=sha(p));receipts['processed_dispatch_events'].append(event);receipts['updated_at']=at;save(rp,receipts)
paragraph=f'''\n\n## LOCAL-R4-TERMINAL-PAUSED-SOL-INDEPENDENT-STATIC-SENT — {at}\nActual same wareconomy-master tool/config PAUSED,60min/173char prompt/correct Master target preserved. R4 terminal REVISION_REQUIRED/E2_RUNTIME_NOT_RELEASED,232 frozen;new A corrective WP NOT SENT pending independent review. Original Sol {proof['delivery_id']}/{proof['wp_id']}/S1 direct tool SENT/new actual active turn {proof['turn_id']}/cursor {proof['cursor']};ACK pending. This replaces completed R3 review as current WP. Previous systemError usage failure is historical;current actual turn started,no substitute agent/new model. Scope exact frozen R4 read-only independent static/coverage/corrective priorities,game/runner/native/candidate execution/build0,production untouched;no runtime E2 or closure. Sol direct completion push continues while scheduler paused. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Delivery proof {p};pause proof {C/'MASTER_GATE05_R4_PAUSED_CONFIG_VERIFICATION_20261008.json'}\n'''
for dest in [R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md',R/'AGENTS.md']:
 with dest.open('a',encoding='utf-8') as f:f.write(paragraph)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps(proof,ensure_ascii=False))
