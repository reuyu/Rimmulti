from pathlib import Path
import json,hashlib,datetime,sys,tomllib,copy
sys.stdout.reconfigure(encoding='utf8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';C=H/'coordination'
RUN='MASTER-R27-SOL-PREP-COMPLETE-20261012-01';PID=11168;SESSION=8532
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def row(p):return {'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check(f):
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes'],str(p)
def refs(x):
 if isinstance(x,dict):
  if all(k in x for k in ['path','sha256','bytes']):check(x)
  for y in x.values():refs(y)
 elif isinstance(x,list):
  for y in x:refs(y)
def type_map(x,path='$'):
 typ='object' if isinstance(x,dict) else 'array' if isinstance(x,list) else 'boolean' if isinstance(x,bool) else 'integer' if isinstance(x,int) else 'string' if isinstance(x,str) else 'null' if x is None else 'number'
 result=[{'path':path,'json_type':typ,'ordered_keys':list(x) if isinstance(x,dict) else None,'length':len(x) if isinstance(x,list) else None}]
 if isinstance(x,dict):
  for k,v in x.items():result+=type_map(v,path+'.'+k)
 elif isinstance(x,list):
  for i,v in enumerate(x):result+=type_map(v,path+'['+str(i)+']')
 return result
def raw_checks(x):
 count=0
 if isinstance(x,dict):
  if 'utf8_text' in x and 'sha256' in x and 'bytes' in x:
   raw=x['utf8_text'].encode('utf8');assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest().upper()==x['sha256'];count+=1
  for y in x.values():count+=raw_checks(y)
 elif isinstance(x,list):
  for y in x:count+=raw_checks(y)
 return count
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';c=read(cp);assert c['active_operation'] is None
if len(sys.argv)>1 and sys.argv[1]=='released':
 p=C/'MASTER_R27_SOL_PREP_COMPLETE_GUARD_FINALLY_RELEASE_20261012.json';raw=read(p)['actual_release_tool'];info=read(R/'Dispatcher/MASTER_MONITOR_LOCK_INFO.json');assert raw['exit_code']==0 and info['status']=='RELEASED' and info['run_id']==RUN and info['pid']==PID
 c['last_monitor_run'].update(release_status='RELEASED_ACTUAL_HELPER_EXIT0',released_at=info['released_at'],all_child_commands_completed_before_release=True);write(cp,c)
 for p2 in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
  with p2.open('a',encoding='utf8') as f:f.write(json.dumps({'at':at,'event_id':RUN+'-RELEASE','type':'OPERATIONAL_GUARD_FINALLY_RELEASE','proof':str(p)},ensure_ascii=False)+'\n')
 print('ACTUAL_GUARD_RELEASE_RECORDED');sys.exit(0)
d=c['sol_current_delivery'];Q=Path(d['qa_root']);x=read(Q/'COMPLETION.json');rr=read(R/'Dispatcher/MASTER_RECEIPTS.json')
assert all(x[k]==d[k] for k in ['delivery_id','wp_id','wp_revision']) and x['result_id']==c['sol_current_result_id'] and x['status']=='COMPLETED' and not any(z.get('result_id')==x['result_id'] for z in rr['processed_results'])
assert sha(Q/'COMPLETION.json')=='DD4E5312832B548A92B85EA47E8497044C098A9536D4BE03C93FBD6E01C3959E' and sha(Q/'EVIDENCE_MANIFEST.json')=='AB226B9DB1D24EE98FA9D84F81DD9FDFC554E7D981785BF2828AAD37EB495545'
assert all(x[k]==0 for k in ['production_changes','QA_compiler_runner_factory_Capture_load_execute','native_Process_game_assets_copy','governance_WP_schema_scheduler_closure_changes']) and x['actual_R27_candidate_verdict']=='NOT_REVIEWED_PENDING_NEW_EXACT_ADMISSION'
em=read(Q/'EVIDENCE_MANIFEST.json');assert len(em['files'])==23
for f in em['files']:check(f)
refs(x);refs(read(Q/'RESULT_INDEX.json'));refs(read(Q/'ACK_COMPLETION_BINDING.json'))
assert sha(Q/'ACK_INITIAL.json')==c['sol_current_ack']['initial_ACK']['sha256']==sha(Q/'ACK.json')
sf=C/'MASTER_SOL_R27_CHILD_CAPTURE_PREPARATION_COMPLETION_SNAPSHOT_20261012.json';sn=json.loads(read(sf)['content'][0]['text'])['polls'][0]
assert sn['thread']['id']==c['sol_thread_id'] and sn['thread']['status']['type']=='idle' and sn['latestTurn']['status']=='completed' and sn['latestTurn']['id']==d['actual_snapshot']['latestTurn']['id']
base=read(Path(d['baseline_path']));files=base['files'];assert len(files)==13458
for f in files:check(f)
for name in ['PRESERVATION_BEFORE.json','PRESERVATION_AFTER.json']:
 p=read(Q/name);assert p['protected_unique_paths']==13458 and {f['path']:(f['sha256'],f['bytes']) for f in p['files']}=={f['path']:(f['sha256'],f['bytes']) for f in files}
o=read(Q/'PROSPECTIVE_CAPTURE_ORACLE.json');refs(o);old=read(Path(o['source_R26_oracle']['path']))['four_normal_fixture_pairs'];assert len(o['normal_pairs'])==4 and o['actual_candidate_factory_Capture_getters_calls']==0
getters=['ParentReceipt','ChildReceipt','ApprovedChildDeclaration','Task','TaskFilePath','ExecutablePath','ExecutableExpectedSha256','WorkingDirectory','SelectedUserDataDirectory','OperatorOptionValues','TaskInvocationValues','ResultChannelPath','StagedFilePath','StagedSha','Scope']
assert [z['name'] for z in o['getter15_order_types']]==getters
count=0;rawcount=0;edits=0
for p,prior in zip(o['normal_pairs'],old):
 assert p['case_id']==prior['case_id'] and p['input_parent14_and_original7']==prior['parent_separately_authored'] and p['input_child14_and_original7']==prior['child_separately_authored'] and p['input_task27']==prior['synthetic_owned_task27']
 cap=p['expected_Capture15'];plan=prior['expected_data_only_closed_plan'];assert list(cap)==getters and cap['ParentReceipt']==plan['parentReceipt11'] and cap['ChildReceipt']==plan['childReceipt11'] and cap['Task']==p['input_task27']
 assert cap['TaskFilePath']==plan['taskFilePath'] and cap['ExecutablePath']==plan['executablePath'] and cap['ExecutableExpectedSha256']==plan['executableSha256'] and cap['WorkingDirectory']==plan['workingDirectory'] and cap['SelectedUserDataDirectory']==plan['declaredRoleUserData']
 assert cap['OperatorOptionValues']==[plan['existingOperatorOptionValues7'][k] for k in ['operatorconfig','operatorconfigsha','operatororigin','operatorlaunchplan','operatorconfigid','operatorrole','operatorcapability']]
 assert cap['TaskInvocationValues']==[plan['taskInvocationValues']['taskFilePath'],plan['taskInvocationValues']['capabilityNonce']] and cap['ResultChannelPath']==plan['protectedResultChannelPath'] and cap['StagedFilePath']==plan['stagedFilePath'] and cap['StagedSha']==plan['stagedSha']
 assert cap['Scope']=='DATA_ONLY_NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED' and list(cap['ApprovedChildDeclaration'])==o['descriptor7_order'] and cap['ApprovedChildDeclaration']==p['input_child14_and_original7']['expected_usedClone_descriptor7']
 tasknames=[z['field'] for z in o['task27_field_types']];assert list(cap['Task'])==tasknames
 mutations=p['mutations_after_successful_capture_only']
 for key in ['callerTask27','returnedTask27']:assert list(mutations[key])==tasknames;edits+=len(mutations[key])
 expected=type_map(p['expected_observation_envelope']);assert expected==p['ordered_type_map'];count+=len(expected)
 rawcount+=sum(raw_checks(vv) for kk,vv in p.items() if kk.startswith('expected_') and 'utf8' in kk)
 for k,g in [('expected_Capture15_compact_utf8',cap),('expected_full_envelope_compact_utf8',p['expected_observation_envelope']),('expected_task27_compact_utf8',cap['Task']),('expected_approved7_compact_utf8',cap['ApprovedChildDeclaration']),('expected_option7_compact_utf8',cap['OperatorOptionValues']),('expected_invocation2_compact_utf8',cap['TaskInvocationValues'])]:
  assert json.dumps(g,ensure_ascii=False,separators=(',',':'))==p[k]['utf8_text']
assert count==976 and rawcount==40 and edits==216
source=read(Q/'FROZEN_SCHEMA_SOURCE_OBSERVATION.json');refs(source['sources']);assert len(source['spans'])==8
for f in source['spans']:
 raw=Path(f['path']).read_bytes();span=raw[f['start']:f['end_exclusive']];assert hashlib.sha256(span).hexdigest().upper()==f['sha256'] and len(span)==f['bytes'] and sha(Path(f['path']))==f['file_sha256']
callplan=read(Q/'PROSPECTIVE_CALLPLAN.json');assert callplan['per_run_primary_direct_calls']=={'IssueAdmissionReceiptFromBytes':8,'receipt_IsValid':8,'OperatorChildLaunchInputs_Capture':4} and callplan['per_run_Capture_getter_observations']==180 and callplan['reads_or_builds_now']==0
assert len(read(Q/'CONSTRUCTION_COPY_RISKS.json')['risks'])==9 and len(read(Q/'FUTURE_EXECUTION_PROVENANCE_CHECKLIST.json')['phases'])==7
bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);t=b['tasks'][-1];assert t['dispatch_id'].endswith('cdc223f3') and t['delivery_status']=='SENT' and not t['unknown_delivery']
for f in t['production_fixed_files']:check(f)
sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as ck
pres=ck.inspect_preservation(t);assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0]
pp=C/'MASTER_R27_SOL_PREP_COMPLETION_A_PRESERVATION_20261012.json';assert not pp.exists();write(pp,pres)
cfg=tomllib.loads(Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml').read_text(encoding='utf8'));assert cfg['status']=='ACTIVE' and cfg['rrule']=='FREQ=HOURLY;INTERVAL=1' and len(cfg['prompt'])==173 and cfg['target_thread_id']==c['master_thread_id']
verdict='ACCEPTED_INDEPENDENT_R27_CAPTURE15_NORMAL_TYPED_RAW_COPY_PROVENANCE_PREPARATION_NO_CANDIDATE_VERDICT'
review=H/'MASTER_REVIEW_ENGINE_GATE05_R27_CHILD_CAPTURE_QA_PREPARATION_S1_20261012.md';assert not review.exists()
review.write_text(f'''# R27 독립 QA 준비 — Master 채택

{at};{x['result_id']}. **{verdict}**.

원래 Sol actual completed/idle166/동일 turn과 immutable ACK·report/manifest/index/binding/COMPLETION last를 대조했다. Evidence23, baseline13458 paths, before-after identities 및 frozen R25 source spans8이 실제 SHA-size 일치한다. Master 독립 literal 대조 결과 정상4 pair의 원래 parent14/child14/raw 선언 및 task27이 이전 독립 R26 입력 그대로이고, 승인15getter graph·소문자 descriptor7 declaration순서·option7 별도순서·원문 case/opaque ID/policy/UTC/path copy mapping이 일치한다. 전체976 hierarchical type/order rows,40 prospective raw UTF8 value-set SHA-size/6 compact serializers per pair,caller/returned Task 전필드216 edits를 확인했다. 이 수치는 **준비 자료**이며 실행 assertions/PASS가 아니다.

기존 validated immutable receipt reference 보관은 허용하고 새로운 receipt constructor를 요구하지 않는다. 정상 detached-copy 관측만으로 실제 IReadOnlyList backing 비노출을 증명하지 못하므로 새 candidate static source/PE review에서 private storage를 확인한다. 실제 task27 CLR widths/approved7 getter별 새 복사/Scope/data-only/non-auth/불필요한 normalization/opaque원문/UTC 보존 등 risk9을 fresh candidate 기준으로 채택한다. 기존 IsValid 내부 Path.GetFullPath comparison은 source 사실이며 새 Capture direct output normalization/IO 금지와 구분한다. 기존 approved helper 호출을 transitive path call0이라고 주장하지 않는다.

정상 direct factory8/IsValid8/Capture4 및180 orderedgetter per run은 후속 새 QA WP callplan 후보이며 이번 실행0이다. Final source/input/oracle/callplan/compiler/all reference pre-pin, finalQA build1, en-US/de-DE fresh runs, complete OS exit/stdoutstderr, actual loaded SHA+독립 MVID, recursive first-before-second/all-after/pre-post identity와 immutable terminal의7 phase 계획을 채택한다. 새 R27candidate SHA/MVID/source/PDB는 NOT_REVIEWED이고 이번 Sol은 mutable7/A ongoing artifact를 읽지 않았다는 QA 범위 선언(전 OS 접근trace 증거는 아님)을 유지한다. Master도 이번 후보 실행·재빌드0이다.

A R27 {t['dispatch_id']}는 아직 처리 중이며 COMPLETION 관측={Path(t['completion_path']).exists()}. 새 WP를 중복 전송하지 않는다. Same hourly monitor 실제 ACTIVE60min/173char/correct Master target, 변경 없음. Sol 준비 artifacts와 terminal graph를 additively 보호하고 기존 sent WP/baseline을 수정하지 않는다. 다음 실제 A terminal→Master 원문·normal E1·exact source/build identity review→새 freeze/admission→idle originalSol의 별도 fresh 실행 QA를 자동 전달한다. Preparation completion이나 old R25 scoped PASS는 새 E2가 아니다.

실제 operator producer/private registration/M04 native frontend/cwd/Genroot/M05 currenttask equality/M06 content/staged load/M07 revoke는 OPEN. Engine002006/Pipeline007/current schema/G-Q1/exact PlayerGlobal/physical split OPEN/Foundation HOLD/fullnativeE2 NOT_RELEASED. R25 S2 좁은 정상 PURE PASS·QA newline CLOSED와 원래 S1 rawFAIL은 보존하며 closure 변화0. Known installed incident 동일 OPEN/actor UNKNOWN/restore0.

초기 Master schema 조회에 기본 cp949 read_text로 오류가 나 UTF8명시 조회로 정정했다. 원문/source/QA 변경·재실행 없음. 원래 primary report_delivery PENDING은 지우지 않고 실제 direct snapshot/수신과 구분해 결속한다.
''',encoding='utf8')
vp=C/'MASTER_SOL_R27_CHILD_CAPTURE_PREPARATION_COMPLETION_VERIFICATION_20261012.json';assert not vp.exists()
proof={'at':at,'guard_run':RUN,'guard_pid':PID,'guard_session':SESSION,'delivery_id':x['delivery_id'],'wp_id':x['wp_id'],'wp_revision':'S1','result_id':x['result_id'],'completion_sha256':sha(Q/'COMPLETION.json'),'evidence_count':23,'protected_paths':13458,'source_spans':8,'Master_typed_rows':count,'Master_raw_value_sets':rawcount,'Master_task_edits':edits,'normal_preparation_pairs':4,'actual_snapshot':sn,'snapshot':row(sf),'master_verdict':verdict,'master_review_path':str(review),'master_review_sha256':sha(review),'candidate_build_execute':0,'actual_R27_candidate_verdict':'NOT_REVIEWED','A_completion_exists':Path(t['completion_path']).exists(),'scheduler_actual':cfg,'new_WP':False,'closure_changed':False,'runtime_e2_released':False,'foundation':'HOLD'}
write(vp,proof);rec=dict(proof,verification_path=str(vp),verification_sha256=sha(vp));rr['processed_results'].append(rec);rr['updated_at']=at;write(R/'Dispatcher/MASTER_RECEIPTS.json',rr)
added=[row(p) for p in Q.rglob('*') if p.is_file()];added.append(row(Path(x['report']['path'])))
addp=C/'MASTER_R27_PRESERVATION_AFTER_QA_PREPARATION_20261012.json';assert not addp.exists();write(addp,{'at':at,'original_baseline':row(Path(d['baseline_path'])),'additional_QA_original_files':added,'no_initial_baseline_or_sent_WP_changes':True,'A_exact_current7_still_mutable':True})
t['preservation_policy']['qa_preserved_manifests'].append({'path':str(Q/'EVIDENCE_MANIFEST.json'),'sha256':sha(Q/'EVIDENCE_MANIFEST.json')});t['additional_completed_QA_preservation']=row(addp);write(bp,b)
c.update(sol_status='R27_READONLY_QA_PREPARATION_COMPLETE_ACCEPTED_WAIT_NEW_EXACT_CANDIDATE',sol_latest_completion=rec,last_sol_cursor=sn['cursor'],sol_next_action='WAIT_A_R27_TERMINAL_THEN_MASTER_REVIEW_EXACT_FREEZE_AND_FRESH_ORIGINAL_SOL_EXECUTION_QA_NO_USER_CONTINUE',updated_at=at)
c['last_monitor_run']={'run_id':RUN,'guard_pid':PID,'guard_session':SESSION,'at':at,'status':'R27_SOL_PREP_COMPLETE_ACCEPTED_A_IN_PROGRESS_NO_DUPLICATE','release_status':'PENDING_ACTUAL_FINALLY'};write(cp,c)
sp=H/'DISPATCHER_STATE.json';st=read(sp);st['endpoints']['sol'].update(execution_phase='TERMINAL_R27_PREPARATION_ACCEPTED',current_runtime_idle_verified=True,last_result_id=x['result_id'],latest_review=str(review),last_runtime_observation_cursor=sn['cursor'])
for dd in st['deliveries']:
 if dd.get('delivery_id')==x['delivery_id']:dd.update(status='COMPLETED_MASTER_ACCEPTED_READ_ONLY_PREPARATION',master_review=str(review),completed_result_id=x['result_id'])
st['updated_at']=at;write(sp,st)
e=dict(proof,event_id=x['delivery_id']+'-MASTER-COMPLETE',type='SOL_R27_INDEPENDENT_READONLY_PREPARATION_MASTER_ACCEPTED',proof_path=str(vp),proof_sha256=sha(vp))
for p in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with p.open('a',encoding='utf8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
para=f'\n\n## LOCAL-SOL-R27-CAPTURE-QA-PREP-COMPLETE — {at}\n{verdict}. OriginalSol completedidle166/23evidence13458protected/frozen99/source8/976prospective typed rows40rawUTF8 sets216task edits matched;execution0/notPASS/R27candidateNOT_REVIEWED. Whole15getter/original lowercase approved7-vsoption7order/task27/deepcopy9risk/future7proof phases adopted as preparation only. Existing IsValid nested Path.GetFullPath comparison separate from newCapture direct IO-normalization ban. A sameR27PURECapture IN_PROGRESS/noCOMPLETION/no duplicate WP;completed QA23+terminalgraph additivelyprotected/no sentWP-baseline changes. SameactualhourlyACTIVE60min173charcorrecttarget; nextAterminal→Masterexactreviewfreeze→idleoriginalSol fresh executionQA automatic. OldR25S2scopedPASS/S1FAILpreserved/fullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED/closure0. Review{review};proof{vp};preservation{addp}\n'
for p in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
 with p.open('a',encoding='utf8') as f:f.write(para)
nx=H/'MASTER_NEXT_TECHNICAL_ACTIONS_20261009.md';nx.write_text(para+'\n'+nx.read_text(encoding='utf-8-sig'),encoding='utf8')
print(json.dumps({'status':verdict,'protected':13458,'evidence':23,'typed_preparation':count,'raw_preparation':rawcount,'A_completion':proof['A_completion_exists'],'newWP':False}))
