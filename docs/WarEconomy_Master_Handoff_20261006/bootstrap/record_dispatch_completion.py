"""Record a previously verified tool submission; never submits or retries a WP."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[3];PKG=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
proof=json.loads((OUT/'sol-postdelivery-proof-confirmed.json').read_text(encoding='utf-8'))
turn=proof['turns'][0];ack=next(x for x in turn['items'] if x['type']=='agentMessage' and 'Gate05' in x.get('text',''))
assert proof['thread']['id']=='01a10fd9-2f90-79e2-a1c4-a1079c99f3ac' and turn['status']=='inProgress'
state=json.loads((PKG/'DISPATCHER_STATE.json').read_text(encoding='utf-8'))
assert not state['deliveries'] and state['migration_bootstrap_verified'] and not state['automation_enabled']
submitted=datetime.datetime.fromtimestamp(1791361489,datetime.timezone(datetime.timedelta(hours=9))).isoformat()
entry={'delivery_id':'LOCAL-SOL-GATE05-SUBMISSION-01','recipient':'sol','work_package':'WP_QA_ENGINE_GATE05','status':'IN_PROGRESS','delivery_status':'SENT',
       'submitted_at':submitted,'acknowledged_observed_at':now,'thread_id':proof['thread']['id'],'host_id':'local','turn_id':turn['id'],
       'acknowledgment_message_id':ack['id'],'submitted_message_file':str(PKG/'DISPATCH_MESSAGE_SOL_GATE05.md'),
       'submitted_message_sha256':sha(PKG/'DISPATCH_MESSAGE_SOL_GATE05.md'),
       'work_package_sha256':sha(PKG/'WP_QA_ENGINE_GATE05.md'),
       'evidence':[str(OUT/x) for x in ['sol-delivery-tool-result.json','sol-postdelivery-proof-confirmed.json','sol-predispatch-check.json','sol-endpoint-predispatch.json']],
       'verification':'tool success + new active turn + explicit Gate05 acceptance commentary; user message ID unavailable in read_thread snapshot',
       'attachments':'exact original WP embedded in saved prompt; absolute paths to local verification/freeze/source/raw evidence',
       'source':'latest user authorized exact WP delivery after verified bootstrap/idle','duplicate_retry':False}
state['deliveries'].append(entry);state['active_run']=None;state['updated_at']=now
state['endpoints']['sol']['last_verified_state']='active';state['endpoints']['sol']['current_wp']='WP_QA_ENGINE_GATE05'
for item in state['queued_work']:
 if item['recipient']=='sol':item.update(status='IN_PROGRESS',delivery_status='SENT',readiness='ALREADY_DISPATCHED_DO_NOT_RESEND',delivery_id=entry['delivery_id'])
state['automation_configuration_observation']={'path':str(Path.home()/'.codex/automations'),'exists':False,'project_schedule_observed':False,'checked_at':now}
report=PKG/'IDE_BOOTSTRAP_VERIFICATION.md'
with report.open('a',encoding='utf-8') as f:
 f.write(f'''\n\n## 전달 후 checkpoint — {now}\n\nSol Gate05 독립 E2는 **SENT → ACKNOWLEDGED → IN_PROGRESS**로 확인했다. 전송 tool 성공, 새 turn `{turn['id']}`, acknowledgment message `{ack['id']}` 및 “Gate05 bootstrap·동결 자료를 확인한 뒤 지정 DLL의 독립 검증을 진행”이라는 실제 commentary가 근거다. 원본 WP 전체가 prepared prompt에 포함되고 검증/freeze/raw evidence의 실제 local paths를 함께 전달했다. [전송 근거](bootstrap/sol-postdelivery-proof-confirmed.json). E2 완료나 PASS를 주장하지 않는다.\nA REV6 **NOT SENT** 유지, [Antigravity 전달 준비 문구](DISPATCH_MESSAGE_A_REV6.md). 사용자 위치 정보 외 idle/활성 WP/direct endpoint 미확인. C routine 새 WP 없음. 자동화 config directory C:/Users/user/.codex/automations는 관측 시 존재하지 않았으며 Dispatcher는 endpoint/non-overlap/scheduler 미충족으로 disabled 유지한다.\nBootstrap 완료 시점의 원본 보고서는 [immutable checkpoint](bootstrap/IDE_BOOTSTRAP_VERIFICATION_at_bootstrap.md)에 보존했다. 후속 state는 current report SHA와 immutable bootstrap report SHA를 별도로 저장한다.\n''')
state['bootstrap_verification_sha256']=sha(report)
state['bootstrap_checkpoint_report']=str(OUT/'IDE_BOOTSTRAP_VERIFICATION_at_bootstrap.md')
state['bootstrap_checkpoint_report_sha256']=sha(OUT/'IDE_BOOTSTRAP_VERIFICATION_at_bootstrap.md')
(PKG/'DISPATCHER_STATE.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (PKG/'DISPATCH_JOURNAL.jsonl').open('a',encoding='utf-8') as f:
 for typ,status in [('SENT','SENT'),('ACKNOWLEDGED','ACKNOWLEDGED'),('IN_PROGRESS','IN_PROGRESS')]:
  f.write(json.dumps({'event_id':'LOCAL-SOL-GATE05-'+typ,'at':now,'type':typ,'delivery_id':entry['delivery_id'],'recipient':'sol','work_package':'WP_QA_ENGINE_GATE05','status':status,'thread_id':proof['thread']['id'],'turn_id':turn['id'],'ack_message_id':ack['id'],'submitted_at':submitted,'message_sha256':entry['submitted_message_sha256'],'tool_proof':entry['evidence'][0],'ack_proof':entry['evidence'][1],'new_wp_or_closure_created':False},ensure_ascii=False)+'\n')
 f.write(json.dumps({'event_id':'LOCAL-BOOT-FINAL-CHECKPOINT','at':now,'type':'CURRENT_REPORT_UPDATED','report_sha256':sha(report),'original_bootstrap_report_sha256':state['bootstrap_checkpoint_report_sha256'],'a_status':'NOT_SENT','sol_status':'IN_PROGRESS','automation_enabled':False},ensure_ascii=False)+'\n')
for name in ['MASTER_AGENT_DISPATCH_BOARD.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md']:
 with (PKG/name).open('a',encoding='utf-8') as f:
  f.write(f'''\n\n## LOCAL-SOL-GATE05-DELIVERY-01 — {now}\n승인된 WP_QA_ENGINE_GATE05의 실제 전송/수신/시작을 확인: **SENT / ACKNOWLEDGED / IN_PROGRESS**.\nThread `01a10fd9-2f90-79e2-a1c4-a1079c99f3ac` / turn `{turn['id']}` / acknowledgment `{ack['id']}`. [전송 근거](bootstrap/sol-postdelivery-proof-confirmed.json), DISPATCH_JOURNAL.jsonl.\nA REV6 NOT SENT(별도 Antigravity endpoint/idle 미확인), C routine 새 WP 없음. Dispatcher disabled, Foundation HOLD, Engine E2 pending/002·006 OPEN. 이 전달로 신규 WP/architecture/closure를 만들지 않았다.\n''')
print(json.dumps({'a':'NOT_SENT','sol':'IN_PROGRESS','sol_turn_id':turn['id'],'automation_enabled':False,'migration_bootstrap_verified':True},indent=2))
