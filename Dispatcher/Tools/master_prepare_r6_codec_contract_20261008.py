from pathlib import Path
import json,datetime,uuid,hashlib,copy,sys
sys.stdout.reconfigure(encoding='utf-8')
R=Path(__file__).resolve().parents[2];H=R/'docs/WarEconomy_Master_Handoff_20261006';sys.path.insert(0,str(R/'Dispatcher'));import master_check_a_result as checker
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return checker.digest(p)
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();bp=R/'Dispatcher/MASTER_A_TASKS.json';b=read(bp);old=b['tasks'][-1];assert old['dispatch_id']=='WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046' and old['status'].startswith('COMPLETED_REVIEWED')
cp=R/'Dispatcher/MASTER_COMMUNICATION_STATE.json';comm=read(cp);assert comm['active_operation'] is None and comm['sol_status']=='R5_CODEC_INDEPENDENT_COMPLETED_MASTER_ACCEPTED_IDLE' and comm['master_monitor_automation']['status']=='PAUSED'
id='WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-'+uuid.uuid4().hex[:8];T=R/'Dispatcher/A_TASKS'/id
wp=H/'WP_ENGINE_GATE05_R6_CODEC_CONTRACT.md';release=H/'RELEASE_ENGINE_GATE05_R6_CODEC_CONTRACT_20261008.md';policy=copy.deepcopy(old['preservation_policy'])
policy['additional_preserved_candidate_manifests'].append({'path':policy['prior_candidate_freeze_manifest'],'sha256':policy['prior_candidate_freeze_manifest_sha256'],'lineage':'R4_REVIEW232'})
policy['prior_candidate_freeze_manifest']=old['frozen_manifest'];policy['prior_candidate_freeze_manifest_sha256']=old['frozen_manifest_sha256'];policy['prior_candidate_lineage']='R5_REVIEW113'
q=R/'QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008';qm=q/'EVIDENCE_MANIFEST.json';policy['qa_preserved_manifests'].append({'path':str(qm),'sha256':sha(qm)})
deps=Path(comm['a_latest_result']['managed_dependency_manifest']);dm=read(deps)
policy['fixed_current_files'].append({'path':str(deps),'sha256':sha(deps),'size':deps.stat().st_size})
for row in dm['files']:
 p=Path(row.get('frozen_path',row.get('path')));assert p.is_file();policy['fixed_current_files'].append({'path':str(p),'sha256':row['sha256'],'size':p.stat().st_size})
policy['historical_allowlist_is_not_r6_source_scope']=True
refs=[H/'MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_E1_20261008.md',H/'MASTER_REVIEW_ENGINE_GATE05_R5_CODEC_INDEPENDENT_S1_20261008.md',R/'docs/QA_EngineHost_Gate05_R5_Codec_Independent_S1_20261008.md',q/'INDEPENDENT_FINDINGS.md',q/'FIELD_COVERAGE_INDEX.json',q/'DTO_FIELD_METADATA.json',q/'UPSTREAM_MANAGED_FIELD_METADATA.json',q/'PRODUCER_COVERAGE_INDEX.json',Path(old['frozen_manifest']),deps,H/'MASTER_REVIEW_ENGINE_GATE05_R4_INDEPENDENT_QA_S1_20261008.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',R/'docs/요구사항_명세서.md',H/'C_REVIEW_CORRECTIONS_CONSOLIDATED.md',H/'history/MASTER_DECISION_LOG_MDR-067.md']
T.mkdir()
baseline={'at':at,'dispatch_id':id,'policy':policy,'baseline':[{'path':str(Path(p)),'sha256':sha(Path(p)),'size':Path(p).stat().st_size} for p in policy['allowed_changed_engine_paths']],'exact_mutable_source':'EngineHostCensus ContentProfileProvider suffix only;WorkerBridge/csproj/prefix fixed','counts':{'archive':19,'prior_candidates':732,'pipeline':206,'qa':1342,'managed_dependencies':4},'independent_r5_review':str(refs[1])};write(T/'MASTER_R6_SCOPE_BASELINE.json',baseline)
instr=f'''# A R6 codec contract exact instruction
Dispatch {id};WP_ENGINE_GATE05_R6_CODEC_CONTRACT/GATE05-R6-CODEC-CONTRACT/envelope9.
Master approved narrow technical repair after independent R5 pure normal codec PASS,remaining static revision required/native untested.
Read entire WP {wp} SHA {sha(wp)} and release {release} SHA {sha(release)}.
Source boundary is ContentProfileProvider suffix/typed codec only,not historical9 allowlist. Task MASTER_R6_SCOPE_BASELINE.json binds fixed WorkerBridge/csproj/Census prefix and archive19/prior732/Pipeline206/QA1342/managed4.
Implement explicit supported field/disposition and collector mapping,canonical set precondition/normalization while retaining material sequence/multiplicity,actual Debug/Release/tooling/raw normal provenance. Valid optional semantics remain allowed. Missing required observation cannot be silent successful trusted content.
Normal pure DTO codec controls/build only. No provider/cache/native/game/operator/old/adverse runner execution;unobserved stays untested,not fabricated PASS. Old installed incident is OPEN,no external restore. Never modify old candidate/QA/governance.
Write new identity-matched ACK {T/'ACK.json'},work log {T/'A_WORK_LOG.md'},write terminal {T/'COMPLETION.json'} last with actual artifacts standard schema. Closure/full E2 remains Master,changedcandidate needs fresh independent Sol.
Absolute references and actual hashes:
'''+''.join(f'- {p} SHA {sha(p)}\n' for p in refs)
(T/'INSTRUCTIONS.md').write_text(instr,encoding='utf-8')
msg=f'Master 승인 신규 작업 {id}입니다. {T/"INSTRUCTIONS.md"} 전체와 연결된 WP/release를 읽고 R6 codec contract만 수행하세요. R5 독립 정상 codec QA는 좁은 PASS이며,필수 데이터 disposition/collector mapping·canonical 정렬 계약·최종 실제 packaging을 수정합니다. 고정 source/이전 frozen/QA/설치는 보존하고 native·이전/adverse runner는 실행하지 마세요. ACK와 완료를 이 새 task에 기록하고 전체 E2/closure는 Master 판단을 기다리세요.'
(T/'UI_MESSAGE.txt').write_text(msg,encoding='utf-8')
task={'dispatch_id':id,'recipient':'A','approved':True,'wp_id':'WP_ENGINE_GATE05_R6_CODEC_CONTRACT','wp_revision':'GATE05-R6-CODEC-CONTRACT','delivery_envelope_revision':9,'created_at':at,'approved_at':at,'approval_source':'User automatic A follow-up/directCU;Master accepted independent R5 codec unit QA and narrow static correction','status':'PREPARED_NOT_SENT','delivery_status':'NOT_SENT','route':'Master Computer Use Antigravity','delivery_owner':'Master','instruction_path':str(T/'INSTRUCTIONS.md'),'instruction_sha256':sha(T/'INSTRUCTIONS.md'),'work_package_path':str(wp),'work_package_sha256':sha(wp),'release_path':str(release),'release_sha256':sha(release),'follows_dispatch_id':old['dispatch_id'],'preservation_policy':policy,'scope_baseline_path':str(T/'MASTER_R6_SCOPE_BASELINE.json'),'scope_baseline_sha256':sha(T/'MASTER_R6_SCOPE_BASELINE.json'),'ack_path':str(T/'ACK.json'),'completion_path':str(T/'COMPLETION.json'),'runtime_verdict':'FULL_GATE_E2_NOT_RELEASED','ack_existed_before_delivery':False,'completion_existed_before_delivery':False,'prerequisites':['fresh exact A conversation idle/composer proof','live renewed exclusive guard','archive19/prior732/Pipeline206/QA1342/managed4/fixedsource match','actual submission before SENT/hourly resume'],'reference_paths':[str(p) for p in refs],'exact_message_path':str(T/'UI_MESSAGE.txt'),'exact_message':msg,'exact_message_sha256':sha(T/'UI_MESSAGE.txt')}
pres=checker.inspect_preservation(task);assert len(pres['engine_archive_checks'])==19 and len(pres['prior_candidate_checks'])==732 and len(pres['qa_preservation_checks'])==1342 and len(pres['pipeline_preservation_checks'])==206
assert len(pres['preservation_errors'])==1 and 'Steam' in pres['preservation_errors'][0],pres['preservation_errors']
write(T/'MASTER_PRESERVATION_BEFORE_DISPATCH.json',pres);task.update(preservation_before_path=str(T/'MASTER_PRESERVATION_BEFORE_DISPATCH.json'),preservation_before_sha256=sha(T/'MASTER_PRESERVATION_BEFORE_DISPATCH.json'))
b['tasks'].append(task);b['updated_at']=at;write(bp,b);comm.update(a_pending_dispatch_id=id,a_status='R6_CODEC_CONTRACT_PREPARED_NOT_SENT',updated_at=at);write(cp,comm)
event={'at':at,'event_id':id+'-PREPARED','type':'A_R6_CODEC_CONTRACT_APPROVED_PREPARED','dispatch_id':id,'status':'NOT_SENT','task_root':str(T),'instruction_path':str(T/'INSTRUCTIONS.md'),'counts':baseline['counts'],'preservation_proof':task['preservation_before_path'],'known_installed_incident':'UNCHANGED_OPEN','runtime_e2_released':False,'closure_changed':False,'monitor':'PAUSED60MIN'}
write(H/'coordination/MASTER_GATE05_R6_CODEC_CONTRACT_PREPARED_20261008.json',event)
for dest in [R/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
 with dest.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
print(json.dumps({'dispatch_id':id,'task_root':str(T),'status':'NOT_SENT','preservation':baseline['counts']},ensure_ascii=False))
