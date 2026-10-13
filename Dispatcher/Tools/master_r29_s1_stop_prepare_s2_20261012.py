from pathlib import Path
import json,hashlib,datetime,sys,tomllib
sys.stdout.reconfigure(encoding='utf-8')
R=Path(r'C:\Users\user\Desktop\RimMulti');H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
Q=R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S1-20261012'
NEWQ=R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-INDEPENDENT-S2-20261012'
WP1=H/'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S1.md'
WP2=H/'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_INDEPENDENT_S2.md'
B1=C/'MASTER_R29_FRESH_PAIR_QA_PROTECTED_BASELINE_20261012.json'
B2=C/'MASTER_R29_S2_PAIR_QA_PROTECTED_BASELINE_20261012.json'
D='SOL-GATE05-R29-STARTUP_PAIR-INDEPENDENT-S2-20261012-01'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def row(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper(),bytes=p.stat().st_size)
def save(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def create(p,j):assert not p.exists(),str(p);save(p,j)
def check(v,pathkey='path'):
 p=Path(v[pathkey]);a=row(p);assert a['sha256']==v['sha256'] and a['bytes']==v['bytes'],str(p);return a
def event(j):
 for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p.open('a',encoding='utf-8') as f:f.write(json.dumps(j,ensure_ascii=False)+'\n')
def append_delta(title,body):
 for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  assert p.exists(),str(p)
  with p.open('a',encoding='utf-8') as f:f.write('\n\n## '+title+' — '+now()+'\n'+body+'\n')
def main():
 assert not NEWQ.exists() and not WP2.exists() and not B2.exists()
 cs=read(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');assert cs.get('active_operation') is None
 raw=read(C/'MASTER_SOL_R29_S1_STOP_IDLE_SNAPSHOT_20261012.json');snap=json.loads(raw['content'][0]['text'])['polls'][0]
 assert snap['thread']['status']['type']=='idle' and snap['latestTurn']['status']=='completed'
 comp=read(Q/'COMPLETION.json');assert comp['status']=='BLOCKED' and comp['candidate_verdict']=='NOT_EXECUTED'
 assert comp['compiler_QA_runner_candidate_publisher_native_Process_adverse_calls']==0
 assert cs['sol_current_delivery']['delivery_id']==comp['delivery_id']
 rec=read(R/'Dispatcher/MASTER_RECEIPTS.json');assert not any(x.get('result_id')==comp['result_id'] for x in rec['processed_results'])
 em=read(Q/'EVIDENCE_MANIFEST.json');verified=[check(v) for v in em['files']];assert len(verified)==9
 for v in comp['artifacts']:check(v)
 index=read(Q/'RESULT_INDEX.json');check(index['report']);check(index['manifest'])
 old=read(B1);verified_old=[check(v) for v in old['files']];assert len(verified_old)==14332
 man=Path(cs['sol_current_delivery']['frozen_manifest']);assert row(man)['sha256']==cs['sol_current_delivery']['frozen_manifest_sha256']
 frozen=[check(v,'frozen_path') for v in read(man)['files']];assert len(frozen)==132
 assert all('bytes' in v and 'size' not in v for v in read(man)['files'])
 rawerr=(Q/'BOOTSTRAP_FAILURE_RAW.txt').read_text(encoding='utf-8');assert "KeyError: 'size'" in rawerr
 report=Path(index['report']['path']);stopfiles=[row(p) for p in sorted(Q.rglob('*')) if p.is_file()]+[row(report)]
 preservation=C/'MASTER_R29_S1_STOP_TERMINAL_PRESERVATION_20261012.json'
 create(preservation,dict(at=now(),files=stopfiles,original_failed_helper_and_raw_immutable=True,execution=0))
 dedup={v['path']:v for v in verified_old}
 for v in stopfiles:dedup[v['path']]=v
 create(B2,dict(at=now(),files=list(dedup.values()),protected_unique_paths=len(dedup),S1_STOP_added=True,currentR29production9_newpublisher_fixed_duringQA=True,oldQA_R27_R28_R29prep_preserved=True))
 review=H/'MASTER_REVIEW_ENGINE_GATE05_R29_QA_S1_BOOTSTRAP_STOP_20261012.md'
 assert not review.exists()
 review.write_text('# R29 QA S1 중단 판정과 새 S2 승인\n\nACCEPTED_OWN_METADATA_STOP_CANDIDATE_NOT_EXECUTED_FRESH_S2_AUTHORIZED.\n\n실제 원래 Sol completed/idle cursor181. 원문 보고서와 evidence9, 완료/index/ACK를 대조했다. ACK는 오류 이후 처음 작성됐다. metadata Python exit1은 frozen manifest의 bytes를 size로 읽은 자체 도구 오류다. 후보·compiler·runner·publisher·native 실행0; candidate FAIL/PASS 및 independent identity 완료를 주장하지 않는다. Master가 기존14332 protected paths와 frozen132 SHA/bytes를 재검증했다. 이 검증은 Sol의 미완료 inventory를 소급 PASS로 만들지 않는다.\n\nS1 helper/raw/terminal/report 전체 '+str(len(stopfiles))+' 파일을 byte-exact 보호한다. 초기 같은 S1 정정 승인 준비 중 terminal/ACK가 도착해 사전 assert에서 중단됐으며 승인 파일·state·전송은 생성하지 않았다. sealed S1을 재시도하지 않는다. 새 S2는 동일 frozen candidate/oracle/static+positive PURE admission만 사용한다. size→bytes와 새 QA root/WP/revision/delivery/result/baseline 결속만 새 metadata helper에 정정한다. 후보·oracle·생산기 코드를 수정하지 않는다.\n\n새 S2 initial metadata 검증 후 prospective final QA compiler1/two fresh normal runs를 승인한다. 정상 pair6/fulltyped/raw/copy + newcandidate Capture4, source High 정적 리뷰 범위는 S1과 같다. 새로운 오류/proofgap은 원문 보존 STOP/보고; 추가 자동 재시도 금지. Source High3 OPEN, A R30 NOT SENT pending independent findings. Foundation HOLD/full native E2 NOT RELEASED. Same hourly monitor PAUSED/direct Sol push 유지.\n',encoding='utf-8')
 body=WP1.read_text(encoding='utf-8').replace('INDEPENDENT-S1-20261012','INDEPENDENT-S2-20261012').replace('Independent_S1_20261012.md','Independent_S2_20261012.md').replace(' / S1',' / S2').replace('/S1/','/S2/').replace('wp/S1/','wp/S2/').replace(str(B1),str(B2)).replace(row(B1)['sha256'],row(B2)['sha256']).replace('14332',str(len(dedup)))
 prefix='# S2 controlling correction / fresh delivery\n\nRead '+str(review)+' SHA'+row(review)['sha256']+'. Original S1 STOP terminal is preserved, NOT candidate FAIL/PASS. New delivery '+D+'. New root '+str(NEWQ)+'; new report '+str(R/'docs/QA_EngineHost_Gate05_R29_Startup_Pair_Independent_S2_20261012.md')+'. Never write or rerun S1.\n\nAuthorize TEXT-only clone of failed own S1 review_setup.py into NEW S2 helper. Exactly correct frozen row r[\'size\'] to r[\'bytes\']; rebind S2 WP/revision/delivery/unique result/new baseline path SHA count and root via __file__. Exhaustive source diff must identify every replacement. All frozen candidate/dependency/admission/oracle/normal call semantics unchanged. Baseline count '+str(len(dedup))+' SHA'+row(B2)['sha256']+'. Inspect JSON schema TEXT before invocation; metadata-only AST parse is allowed. Do not execute/import old S1 top level. Perform new initial metadata/identity validation; create immutable ACK before dependent compile/candidate work. Full runner build1 and two fresh normal runs remain admitted; no prior candidate runs occurred. Any new error/FAIL/proofgap STOP and report, no retry without new Master disposition.\n\n'
 WP2.write_text(prefix+body,encoding='utf-8')
 assert str(R/'docs/QA_EngineHost_Gate05_R29_Startup_Pair_Independent_S1_20261012.md') not in WP2.read_text(encoding='utf-8')
 proof=C/'MASTER_SOL_R29_S1_STOP_DISPOSITION_S2_PREPARATION_20261012.json'
 summary=dict(at=now(),guard_run='MASTER-R29-QA-METADATA-CORRECTION-20261012-01',guard_session=13411,guard_pid=19332,result_id=comp['result_id'],delivery_id=comp['delivery_id'],wp_revision='S1',completion_sha256=row(Q/'COMPLETION.json')['sha256'],actual_snapshot=snap,evidence_count=9,protected_paths=14332,frozen_files=132,independent_QA_before_after_incomplete=True,Master_rehash_not_retroactive_QA_PASS=True,master_verdict='ACCEPTED_OWN_METADATA_STOP_CANDIDATE_NOT_EXECUTED_FRESH_S2_AUTHORIZED',review=row(review),preservation=row(preservation),new_wp=row(WP2),new_baseline=row(B2),new_delivery=D,new_status='APPROVED_NOT_SENT',candidate_executions=0,native_e2_released=False,closure_changed=False,foundation='HOLD')
 create(proof,summary)
 cs['sol_latest_completion']=dict(summary,proof=row(proof));cs['sol_current_delivery'].update(status='BLOCKED_MASTER_DISPOSED_METADATA_STOP',result_id=comp['result_id'],completion_sha256=summary['completion_sha256'],master_disposition=summary['master_verdict'],actual_snapshot=snap)
 cs['sol_prepared_delivery']=dict(delivery_id=D,wp_id=comp['wp_id'],wp_revision='S2',wp_path=str(WP2),wp_sha256=row(WP2)['sha256'],baseline_path=str(B2),baseline_sha256=row(B2)['sha256'],protected_unique_paths=len(dedup),qa_root=str(NEWQ),delivery_status='APPROVED_NOT_SENT',unknown_delivery=False,frozen_manifest=str(man),frozen_manifest_sha256=row(man)['sha256'],selected_sha256=cs['sol_current_delivery']['selected_sha256'],selected_mvid=cs['sol_current_delivery']['selected_mvid'])
 cs['updated_at']=now();save(R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',cs)
 rec['processed_results'].append(dict(at=now(),recipient='Sol',result_id=comp['result_id'],completion_sha256=summary['completion_sha256'],master_verdict=summary['master_verdict'],review=row(review),proof=row(proof),candidate_executions=0,native_e2_released=False,closure_changed=False));rec['updated_at']=now();save(R/'Dispatcher/MASTER_RECEIPTS.json',rec)
 tasks=read(R/'Dispatcher/MASTER_A_TASKS.json');tasks['tasks'][-1]['preservation_policy']['qa_preserved_manifests'].append(dict(path=str(preservation),sha256=row(preservation)['sha256']));tasks['updated_at']=now();save(R/'Dispatcher/MASTER_A_TASKS.json',tasks)
 defect=C/'MASTER_DEFECT_QA_G05_R29_METADATA_SCHEMA_20261012.json'
 create(defect,dict(at=now(),defect_id='QA-G05-R29-METADATA-SCHEMA-20261012-01',status='OPEN',kind='QA_OWN_TOOL_NOT_CANDIDATE',cause="frozen manifest bytes read as size",original_stop_preserved=row(preservation),repair_authorized_delivery=D,closure_requires='fresh S2 metadata proof and normal QA disposition',candidate_verdict='NOT_EXECUTED'))
 event(dict(summary,event='SOL_R29_S1_STOP_MASTER_DISPOSED_S2_PREPARED'))
 append_delta('LOCAL-SOL-R29-S1-METADATA-STOP-S2-PREPARED',summary['master_verdict']+'. Original idle181/evidence9/Master rehash14332+frozen132; QA identity incomplete/candidate/compiler/runner0. S1 raw and terminal protected; new S2 same exact candidate/oracle/static+positive PURE authorized NOT SENT until fresh idle/direct proof. QA-G05-R29-METADATA-SCHEMA OPEN; source High3 and Engine/Pipeline/GQ1 OPEN/Foundation HOLD/native E2 NOT RELEASED. Same hourly PAUSED/direct Sol push. Review '+str(review)+'; proof '+str(proof))
 print(json.dumps(dict(status='S1_STOP_DISPOSED_S2_PREPARED_NOT_SENT',baseline_count=len(dedup),stopfiles=len(stopfiles),wp=row(WP2),proof=row(proof)),ensure_ascii=False))
if __name__=='__main__':main()
