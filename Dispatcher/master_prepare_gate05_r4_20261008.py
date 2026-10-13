"""Prepare unique R4 under user-authorized automatic A follow-up; no UI send."""
import copy
import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
import master_check_a_result as checker

ROOT=Path(__file__).resolve().parent.parent
D=ROOT/'Dispatcher'
H=ROOT/'docs/WarEconomy_Master_Handoff_20261006'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    now=datetime.now().astimezone().isoformat()
    board=read(D/'MASTER_A_TASKS.json')
    assert not any(t['status'] in ['SENT','ACKNOWLEDGED','IN_PROGRESS','DELIVERY_UNCERTAIN','PREPARED_NOT_SENT'] for t in board['tasks'])
    state=read(D/'MASTER_COMMUNICATION_STATE.json');assert state['active_operation'] is None
    old=next(t for t in board['tasks'] if t['dispatch_id']=='WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa')
    assert old['status']=='COMPLETED_REVIEWED_REVISION_REQUIRED'
    assert state['sol_latest_result']['master_verdict']=='ACCEPTED_INDEPENDENT_STATIC_REVISION_REQUIRED_RUNTIME_UNTESTED'
    ident='WE-A-ENGINE-GATE05-R4-20261008-DIRECT-'+uuid.uuid4().hex[:8]
    folder=D/'A_TASKS'/ident;folder.mkdir()
    policy=copy.deepcopy(old['preservation_policy'])
    policy['additional_preserved_candidate_manifests'].append({'path':policy['prior_candidate_freeze_manifest'],'sha256':policy['prior_candidate_freeze_manifest_sha256'],'lineage':'R2_REJECTED107'})
    policy.update(prior_candidate_freeze_manifest=old['review_freeze_manifest'],prior_candidate_freeze_manifest_sha256=old['review_freeze_manifest_sha256'],prior_candidate_lineage='R3_REVIEW133')
    qp=read(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/PRESERVATION_AFTER.json')
    policy['qa_preserved_manifests']=[{'path':x['manifest'],'sha256':x['manifest_sha256']} for x in qp['qa_inventories']]
    qm=ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/EVIDENCE_MANIFEST.json'
    policy['qa_preserved_manifests'].append({'path':str(qm),'sha256':sha(qm)})
    installed=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll')
    assert sha(installed)==policy['known_installed_incident']['observed_sha256_at_dispatch']
    wp=H/'WP_ENGINE_GATE05_R4.md';release=H/'MASTER_REVIEW_ENGINE_GATE05_R3_INDEPENDENT_QA_S1_20261008.md'
    task={'dispatch_id':ident,'recipient':'A','approved':True,'wp_id':'WP_ENGINE_GATE05_R4','wp_revision':'GATE05-R4','delivery_envelope_revision':7,'created_at':now,'approved_at':now,'approval_source':'User automatic A follow-up routing and latest continue; Master accepted independent R3 static findings within same Engine repair scope','status':'PREPARED_NOT_SENT','delivery_status':'NOT_SENT','route':'computer-use/Antigravity','delivery_owner':'Master','instruction_path':str(folder/'INSTRUCTIONS.md'),'work_package_path':str(wp),'work_package_sha256':sha(wp),'release_path':str(release),'release_sha256':sha(release),'follows_dispatch_id':old['dispatch_id'],'preservation_policy':policy,'ack_path':str(folder/'ACK.json'),'completion_path':str(folder/'COMPLETION.json'),'runtime_verdict':None,'ack_existed_before_delivery':False,'completion_existed_before_delivery':False,'prerequisites':['real Master exclusive lock','fresh exact A conversation idle','no active/unknown A delivery','immutable archive/prior/Pipeline/QA bytes matched','known installed incident unchanged','actual UI submission before same hourly monitor activation']}
    pres=checker.inspect_preservation(task)
    assert len(pres['preservation_errors'])==1 and str(installed) in pres['preservation_errors'][0]
    assert (len(pres['engine_archive_checks']),len(pres['pipeline_preservation_checks']),len(pres['prior_candidate_checks']),len(pres['qa_preservation_checks']))==(19,206,387,1205)
    before=folder/'MASTER_PRESERVATION_BEFORE_DISPATCH.json'
    write(before,{'at':now,'dispatch_id':ident,'preservation':pres,'known_installed_incident_open_unchanged':True,'no_candidate_rebuild':True})
    refs=[release,H/'MASTER_REVIEW_ENGINE_GATE05_R3_E1_20261008.md',Path(state['sol_latest_result']['report_path']),ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/CORRECTION_PRIORITIES.md',ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/INDEPENDENT_FINDINGS.md',H/'C_REVIEW_CORRECTIONS_CONSOLIDATED.md',H/'history/MASTER_DECISION_LOG_MDR-067.md',H/'REFERENCE_MOD_REUSE_ANALYSIS_20261008.md',Path(policy['prior_candidate_freeze_manifest'])]
    task['reference_paths']=[str(x) for x in refs]
    instructions=f'''# Master 승인 R4 전달

Dispatch ID {ident}; WP_ENGINE_GATE05_R4 / GATE05-R4 / envelope7. 기존 R3 terminal과 Sol 독립 결과를 Master가 수집·채택했다. Latest user continue + 기존 자동 A 전달 승인에 따른 동일 Engine repair 후속 수정이다.

1. WP `{wp}` 전체와 controlling release `{release}`를 먼저 읽는다. task root `{folder}`. 원래 R3 PASS_WITH_LIMITS/32 labels/표준 completion 준수 주장은 채택되지 않았다.
2. 다른 WP 처리 중이면 중복 시작하지 말고 ACK로 알린다. 새 ACK에 schema_version1,dispatch_id `{ident}`,wp_id WP_ENGINE_GATE05_R4,wp_revision GATE05-R4,recipient A,status ACKNOWLEDGED|IN_PROGRESS|BLOCKED,acknowledged_at timezone,note를 실제로 쓴다.
3. WP 단계1~6을 순서대로 구현·입증한다. 원래 SIMULATION grant와 READ_ONLY validator role을 각각 유지/결속한다. 고정 admitted workload/origin과 실제 native normal flow를 구현하고 stage/source/profile/task/result/receipt/promotion 증거를 연결한다. Native 정상 workload가 없으면 BLOCKED/UNTESTED를 정확히 보고하며 fixture PASS로 전면 해소를 주장하지 않는다.
4. 정확9 mutable Engine paths 및 새 scratch/EngineGate05R4/R4 report/manifest/task만 변경한다. before proof `{before}`. Archive19/prior R3+R2+R1=387/Pipeline206/QA1205 보호를 확인했다. R3 COMPELETION/133 snapshot 및 모든 기존 QA/원문/상위 governance/예약은 보존한다.
5. 새 licensed project RuntimeCopy 안의 executable/userdata/mod/profile로만 정상 실행한다. Steam 원래 exe/core/installed/probe/실제 save를 실행 대상으로 삼거나 변경/restore하지 않는다. Known installed BB3B... vs old2D64... actor/cause UNKNOWN/OPEN 유지. 보호/DRM 우회 금지. 원본 asset은 승인된 copy source로만 사용한다.
6. Defensive review/normal positive controls만 수행한다. 새 forged/replay/tamper/bypass fixture나 exploit 절차를 만들지 않고 과거 adverse runner를 재실행하지 않는다. Runner-authored result/reflection/profile override는 native 결과가 아니다. 동일 candidate의 실제 loaded profile/census를 입증한다.
7. 새 pre-run exact candidate/source/PDB/dependency/content/config/tooling snapshot과 before/after preservation을 결속한다. 보고서/manifest/COMPLETION은 실제 bytes에서 계산한다. 표준 completion exact fields/required roles/absolute paths를 envelope/WP와 대조한 뒤 마지막에 발행한다. BLOCKED/FAILED는 실제 reason/partial artifacts/UNTESTED를 남긴다. E1→E2/closure를 선언하지 않는다.

필수 reference 절대경로:
'''+''.join('- '+str(x)+'\n' for x in refs)
    (folder/'INSTRUCTIONS.md').write_text(instructions,encoding='utf-8')
    message=f'Master 승인 새 작업: {folder/"INSTRUCTIONS.md"} 를 전체 읽고 WP_ENGINE_GATE05_R4/GATE05-R4를 수행하세요. R3와 Sol 독립 리뷰는 완료·보존됐습니다. 먼저 새 task에 ACK.json, 마지막에 표준 COMPLETION.json을 작성하세요. 정상 native가 없으면 BLOCKED/UNTESTED로 정확히 보고하고, 다른 WP 처리 중이면 중복 시작하지 마세요.'
    (folder/'UI_MESSAGE.txt').write_text(message,encoding='utf-8')
    task.update(instruction_sha256=sha(folder/'INSTRUCTIONS.md'),exact_message_path=str(folder/'UI_MESSAGE.txt'),exact_message=message,exact_message_sha256=sha(folder/'UI_MESSAGE.txt'),preservation_before_path=str(before),preservation_before_sha256=sha(before))
    write(folder/'MASTER_DELIVERY_PREPARED.json',{'task':task,'actual_delivery':False,'exclusive_lock_session':19419,'monitor':'PAUSED_UNTIL_CONFIRMED_SUBMISSION'})
    board['tasks'].append(task);board['updated_at']=now;write(D/'MASTER_A_TASKS.json',board)
    state.update(a_pending_dispatch_id=ident,a_status='R4_APPROVED_NOT_SENT',active_operation={'run_id':'MASTER-SOL-R3-INDEPENDENT-COMPLETE-R4-20261008-01','dispatch_id':ident,'phase':'PREPARED_AWAIT_FRESH_UI_SUBMISSION','started_at':now},updated_at=now);write(D/'MASTER_COMMUNICATION_STATE.json',state)
    event={'event_id':ident+'-PREPARED','at':now,'type':'A_R4_APPROVED_NOT_SENT','dispatch_id':ident,'wp_id':task['wp_id'],'wp_revision':task['wp_revision'],'instruction_path':task['instruction_path'],'approved':True,'actual_delivery':False,'scheduler':'PAUSED60MIN_UNTIL_SUBMISSION','closure_changed':False}
    for path in [D/'MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
        with path.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
    delta=f'\n\n## LOCAL-A-R4-APPROVED-PREPARED — {now}\nSame Engine repair WP_ENGINE_GATE05_R4/GATE05-R4/envelope7 approved {ident},PREPARED_NOT_SENT. Exact paths/message/prerequisites recorded. Archive19/prior387/Pipeline206/QA1205 protected;checker now guards QA manifests as well. Known installed unchanged OPEN. User automatic A follow-up + continue authorizes routine direct delivery;actual fresh idle/submission still required. Sol independent artifact result accepted but thread usage-failed operational state separate;no new QA WP. Same hourly monitor PAUSED until actual A submission. No gate/closure change,Foundation HOLD. Instructions {task["instruction_path"]}\n'
    for path in [H/'MASTER_AGENT_DISPATCH_BOARD.md',H/'MASTER_DECISION_LOG.md',H/'MASTER_PROJECT_STATE.md',ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md']:
        with path.open('a',encoding='utf-8') as f:f.write(delta)
    print(json.dumps({'dispatch_id':ident,'instruction_path':task['instruction_path'],'message':message,'counts':{'archive':19,'prior':387,'pipeline':206,'qa':1205},'status':'PREPARED_NOT_SENT'},ensure_ascii=False))

if __name__=='__main__':main()
