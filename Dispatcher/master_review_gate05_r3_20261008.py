"""Read-only R3 evidence review and durable Master disposition; no E1 rerun."""
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK = ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()

def write(p, d):
    Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    state_path=ROOT/'Dispatcher/MASTER_COMMUNICATION_STATE.json'
    state=read(state_path)
    assert state['active_operation'] is None and state['a_current_attempt_id']==TASK.name
    c=read(TASK/'COMPLETION.json')
    assert sha(TASK/'COMPLETION.json')=='3EBE3AAEF5A32B802B5EEFD6004709F88218E65E11462AAC033E5A4B8898E5F4'
    assert c['task_id']==TASK.name and c['work_package_id']=='WP_ENGINE_GATE05_R3'
    assert c['result_id']=='GATE05-R3-E1-COMPLETION-20261008-01'
    receipts_path=ROOT/'Dispatcher/MASTER_RECEIPTS.json'
    receipts=read(receipts_path)
    assert not any(x.get('result_id')==c['result_id'] for x in receipts['processed_results'])
    freeze_path=TASK/'MASTER_GATE05_R3_REVIEW_FREEZE_MANIFEST.json'
    freeze=read(freeze_path)
    for row in freeze['files']:
        assert sha(row['original_path'])==sha(row['frozen_path'])==row['sha256'],row['original_path']
    lineage=[]
    for config in ['Debug','Release']:
        dll=ROOT/f'scratch/WorkerBridgeMod/Source/bin/{config}/net472/WarEconomy.WorkerBridge.PoC.dll'
        pdb=dll.with_suffix('.pdb')
        result=subprocess.run(['dotnet',str(ROOT/'Dispatcher/Tools/InspectLineage/bin/Debug/net8.0/InspectLineage.dll'),str(dll),str(pdb)],capture_output=True,text=True,check=True)
        metadata=json.loads(result.stdout)
        assert metadata['codeviewMatched'] and len(metadata['documents'])==4 and all(x['matched'] for x in metadata['documents'])
        for doc in metadata['documents']:
            frozen=next(x for x in freeze['files'] if Path(x['original_path']).resolve()==Path(doc['path']).resolve())
            assert sha(frozen['frozen_path'])==doc['expected']
            doc['frozen_source_path']=frozen['frozen_path']
        metadata.update(dll_sha256=sha(dll),pdb_sha256=sha(pdb),scope='metadata read only; no candidate execution/build')
        write(H/f'coordination/ENGINE_GATE05_R3_{config.upper()}_PDB_SOURCE_20261008.json',metadata)
        lineage.append(metadata)
    manifest=read(ROOT/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R3.json')
    evidence_checks=[]
    for name,item in manifest['verification_evidence'].items():
        p=(ROOT/item['path']).resolve();assert p.is_relative_to(ROOT)
        evidence_checks.append({'role':name,'path':str(p),'matched':sha(p)==item['sha256'],'size_matched':p.stat().st_size==item['bytes']})
    for item in manifest['source_files']:
        assert sha(ROOT/item['path'])==item['sha256']
    results=read(ROOT/'scratch/EngineGate05R3/results.json')
    raw=(ROOT/'scratch/EngineGate05R3/raw_console.txt').read_text(encoding='utf-8-sig')
    assert len(results['results'])==32 and results['passed']==32 and results['failed']==0
    assert len(re.findall(r'^\[PASS\]',raw,re.M))==32
    qa_pres=read(ROOT/'QA-Tactical-Engine/GATE05-R3-QA-PREP-S1-20261008/PRESERVATION_AFTER.json')
    qa_counts=[]
    for inv in qa_pres['qa_inventories']:
        assert sha(inv['manifest'])==inv['manifest_sha256']
        for item in inv['files']:
            assert sha(item['path'])==item['sha256']
        qa_counts.append(len(inv['files']))
    for item in read(ROOT/'QA-Tactical-Engine/GATE05-R3-QA-PREP-S1-20261008/EVIDENCE_MANIFEST.json')['files']:
        assert sha(item['path'])==item['sha256']
    checked=read(H/'coordination/MASTER_HEARTBEAT_20261008_1356_FILE_CHECK.json')
    now=datetime.now().astimezone().isoformat()
    review_path=H/'MASTER_REVIEW_ENGINE_GATE05_R3_E1_20261008.md'
    proof_path=H/'coordination/MASTER_GATE05_R3_E1_VERIFICATION_20261008.json'
    findings=[
        {'id':'R3-M01','severity':'Critical','disposition':'OPEN_STATIC_CONTRACT_FAILURE','finding':'Nonce checks improved; fixed admitted executable/binary/config and owned validator workload/result origin still not established. Launch parses caller-selected executable/arguments; Bind helper supplies/accepts existing process identity instead of proving trusted launch origin.','anchors':['WorkerBridge.cs:2057','WorkerBridge.cs:2081','WorkerBridge.cs:2121','WorkerBridge.cs:2187','WorkerBridge.cs:2222']},
        {'id':'R3-M02','severity':'High','disposition':'OPEN_NORMAL_FLOW_REGRESSION','finding':'Issued validator task/result is READ_ONLY; completion requires same allowedMode as SIMULATION grant. Genuine SIMULATION→seal/stage→READ_ONLY validator path is rejected statically; harness injects READ_ONLY grant. Role mapping must preserve approved simulator authority, not change it to make fixture pass.','anchors':['WorkerBridge.cs:1760','WorkerBridge.cs:1986','WorkerBridge.cs:2545','EngineGate05R3/Program.cs:286']},
        {'id':'R3-M03','severity':'High','disposition':'OPEN_STATIC_CONTRACT_FAILURE','finding':'DTO/context equality expanded and consume failure now revokes: credit. Full MD128 proof still incomplete: validator copies task context, target map clamps by index without stable identity proof, executable carried into receipt without admitted binary/config equality, no fully defined current authority/role mapping. MD129 Execute/Bind early failures remain unclassified.','anchors':['WorkerBridge.cs:2187','WorkerBridge.cs:2230','WorkerBridge.cs:2295','WorkerBridge.cs:2331','WorkerBridge.cs:2500','WorkerBridge.cs:2631']},
        {'id':'R3-M04','severity':'High','disposition':'OPEN_MD130_NOT_REMEDIATED','finding':'Mod missing-file fail-closed, extra Thing material fields and R-format credited. Version/capability flag upgrade is not typed lossless encoding: delimiter strings, skipped nulls, null-empty collapse, incomplete patch/settings/material/order support remain; FAIL-02 checks only constant schema string. No all-Def serialization or blanket sorting prohibition imposed.','anchors':['EngineHostCensus.cs:1534','EngineHostCensus.cs:1651','EngineHostCensus.cs:1681','EngineHostCensus.cs:1719','EngineHostCensus.cs:1878','EngineGate05R3/Program.cs:590']},
        {'id':'R3-M05','severity':'High','disposition':'OPEN_EVIDENCE_SCOPE_FAILURE','finding':'32 reported PASS/raw counts agree but OS child is cmd echo; runner writes ValidatorResult, armed component/authority/grant/seal are reflection fixtures and actual content profile is mocked. GENUINE_CONTROL_FLOW labels do not prove genuine native semantic validator. Adverse forged fixtures fall outside issued defensive/normal-only scope; Master never reruns or commissions these.','anchors':['EngineGate05R3/Program.cs:244','EngineGate05R3/Program.cs:263','EngineGate05R3/Program.cs:399','EngineGate05R3/Program.cs:413']},
        {'id':'R3-M06','severity':'High','disposition':'OPEN_NATIVE_ISOLATION_EVIDENCE_GAP','finding':'Native observation reports launch from protected Steam original with -quicktest, not RuntimeCopy executable; report omits -quicktest. No actual isolated userdata/mod paths, loaded new candidate SHA/MVID/profile/staged native census/result/loader output/numeric exit proof. PID startup observed only; NATIVE_UNTESTED/CAUSE_UNKNOWN. No claim that original saves were modified or DRM blocked.','anchors':['EngineGate05R3/native_execution_observation.txt','POC_EngineHost_Semantic_Authority_Gate_05_R3.md:4']},
        {'id':'R3-M07','severity':'High','disposition':'OPEN_PROVENANCE_SCHEMA_FAILURE','finding':'10 completion artifact SHA/size matches; manifest source/binary identity and Debug/Release PDB source4/4 match. Report table source/results/raw SHA values differ from actual/manifest. Standard completion lacks exact dispatch_id/wp_id/wp_revision/completed_at/e1_verdict/limitations/required roles and absolute paths; aliases resolve same task, not another task. Before-execution freeze/dependency/content proof missing.','anchors':['COMPLETION.json','RELEASE_MANIFEST_ENGINE_GATE05_R3.json','POC_EngineHost_Semantic_Authority_Gate_05_R3.md:2']},
        {'id':'R3-M08','severity':'High','disposition':'OPEN_KNOWN_INSTALLED_INCIDENT','finding':'Installed BB3B... unchanged from pre-R3 observed incident; old expected2D64... not normalized/restored. Actor/cause UNKNOWN. Archive19/prior254/Pipeline206/QA preserved. No full installed-baseline-preservation claim accepted.','anchors':['MASTER_HEARTBEAT_20261008_1356_FILE_CHECK.json']},
    ]
    proof={'at':now,'dispatch_id':TASK.name,'wp_id':'WP_ENGINE_GATE05_R3','wp_revision':'GATE05-R3','result_id':c['result_id'],'completion_sha256':sha(TASK/'COMPLETION.json'),'reported_e1_verdict':c['verdict'],'master_verdict':'REVISION_REQUIRED_E2_RUNTIME_NOT_RELEASED','alias_identity_reconciled':True,'standard_schema_accepted':False,'artifact_checks':read(H/'coordination/MASTER_R3_ALIASED_ARTIFACT_CHECK_20261008.json')['checks'],'manifest_evidence_checks':evidence_checks,'lineage':lineage,'frozen_manifest':str(freeze_path),'frozen_manifest_sha256':sha(freeze_path),'frozen_files':len(freeze['files']),'freeze_kind':freeze['kind'],'reported_test_count':32,'native_semantic_candidate_execution':'UNTESTED','candidate_execution_by_master':False,'findings':findings,'preservation_counts':{'archive':19,'prior':254,'pipeline':206,'qa':qa_counts,'r3_preparation_evidence':17},'installed_actual_sha256':checked['actual_installed_sha256'],'installed_incident':'OPEN_UNCHANGED_ACTOR_CAUSE_UNKNOWN','closure_changed':False,'foundation':'HOLD','monitor_pause':'PENDING_ACTUAL_TOOL','master_review_path':str(review_path)}
    write(proof_path,proof)
    text=f'# Gate05-R3 E1 Master 판정\n\n{now}\n\n**REVISION_REQUIRED / E2_RUNTIME_NOT_RELEASED**. 실제 같은 A task terminal을 수집했다. Alias task/WP와 report의 GATE05-R3 revision은 식별되지만 standard completion을 충족하지 않는다. 원문을 고치지 않고 보존했다. Fresh runtime E2를 발행하지 않는다. 다음 A 수정 WP는 Sol의 새 R3 독립 정적 검토 후 좁혀 발행한다. 이 시점 새 A WP는 NOT SENT다.\n\n'
    for f in findings:
        text+=f'## {f["id"]} — {f["disposition"]}\n\n{f["finding"]}\n\nSource anchors: '+', '.join(f['anchors'])+'\n\n'
    text+=f'## 실제 identity 및 범위\n\nSelected Debug SHA {lineage[0]["dll_sha256"]},MVID {lineage[0]["mvid"]},PDB {lineage[0]["pdb_sha256"]}. Alternate Release SHA {lineage[1]["dll_sha256"]},MVID {lineage[1]["mvid"]},PDB {lineage[1]["pdb_sha256"]}. Both CodeView match/source4/4,133 post-completion immutable files. This is not execution-before proof. Completion SHA {proof["completion_sha256"]}; freeze manifest SHA {proof["frozen_manifest_sha256"]}.\n\n32/32 labels are fixture/OS child evidence, not native coverage. Genuine issuance/STEP/SEAL/STAGE/profile/fresh-load/census/validator result/approved promotion absent. Mode regression found by defensive source inspection, not execution or exploit reproduction. No Master candidate build/execution; no original installed restore or attribution.\n\nOriginal report table source WorkerBridge B9A098... vs actual4BC9B...; census5C66... vs actualA912...; results47385... vs actualA066...; raw029988.../10384bytes vs actual2EBC.../10822bytes. Relative-path completion artifacts are locally reconciled to exact same workspace; checker out-of-project messages arise from non-absolute contract failure, not evidence of external reported artifacts.\n\nEngine002/006,Pipeline007/current schema,G-Q1 OPEN; Foundation HOLD; narrow historical closures retained. User-hourly monitor run after R3 resume observed now; pause only after this durable terminal review. Sol independent R3 read-only review permitted on exact frozen133, without runtime E2 release/build/execute/adverse fixtures. Master findings are evidence for independent agreement/disagreement.\n\nProof: {proof_path}\n'
    review_path.write_text(text,encoding='utf-8')
    receipt={**proof,'type':'A_ENGINE_GATE05_R3_E1','processed_at':now,'master_review_sha256':sha(review_path),'verification_path':str(proof_path),'verification_sha256':sha(proof_path)}
    receipts['processed_results'].append(receipt);receipts['updated_at']=now;write(receipts_path,receipts)
    board_path=ROOT/'Dispatcher/MASTER_A_TASKS.json';board=read(board_path)
    task=next(x for x in board['tasks'] if x['dispatch_id']==TASK.name)
    task.update(status='COMPLETED_REVIEWED_REVISION_REQUIRED',master_verdict=proof['master_verdict'],result_id=c['result_id'],completion_sha256=proof['completion_sha256'],master_review_path=str(review_path),review_freeze_manifest=str(freeze_path),review_freeze_manifest_sha256=sha(freeze_path),reviewed_at=now,monitor_status='PAUSE_PENDING')
    board['updated_at']=now;write(board_path,board)
    state.update(a_status='R3_COMPLETED_MASTER_REVISION_REQUIRED_E2_RUNTIME_NOT_RELEASED',a_latest_result=receipt,a_pending_dispatch_id=None,updated_at=now)
    state['master_monitor_automation'].update(future_run_after_r3_resume_observed=True,first_run_after_r3_resume_observed_at=now,desired_status='PAUSED',pause_reason='R3 terminal collected; revision required; Sol independent static review next')
    write(state_path,state)
    dispatch_path=H/'DISPATCHER_STATE.json';dispatch=read(dispatch_path)
    for item in dispatch['deliveries']:
        if item.get('delivery_id')==TASK.name:item.update(status=task['status'],result_id=c['result_id'],master_verdict=proof['master_verdict'],master_review_path=str(review_path))
    dispatch['latest_master_review']={'at':now,'review':str(review_path),'proof':str(proof_path),'status':proof['master_verdict'],'scheduler':'PAUSE_PENDING','new_dispatch':False}
    dispatch['updated_at']=now;write(dispatch_path,dispatch)
    delta=f'\n\n## LOCAL-ENGINE-GATE05-R3-E1-MASTER — {now}\nActual R3 terminal aliases reconciled;10 declared artifacts SHA/size matched;Debug/Release CodeView/source4/4 matched,133 immutable post-completion review freeze. REVISION_REQUIRED/E2_RUNTIME_NOT_RELEASED: normal SIMULATION grant vs READ_ONLY validator equality regression, remaining operator admitted identity/context/typed content/native isolation and schema/provenance gaps. 32 fixture/OS-child PASS labels are not genuine native E2;no rerun/adverse reproduction. Known installed incident unchanged OPEN/actor UNKNOWN;archive19/prior254/Pipeline206/QA324297312238 + preparation17 preserved. R3 resumed scheduled run observed now;actual pause pending tool. Next Sol exact frozen R3 independent static WP pending delivery;new A follow-up NOT SENT pending independent review refinement. No closure;Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review {review_path};proof {proof_path}\n'
    for path in [ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',ROOT/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
        with path.open('a',encoding='utf-8') as f:f.write(delta)
    event={'event_id':c['result_id']+'-MASTER-REVIEWED','at':now,'type':'A_R3_TERMINAL_REVIEWED','result_id':c['result_id'],'dispatch_id':TASK.name,'master_verdict':proof['master_verdict'],'proof':str(proof_path),'proof_sha256':sha(proof_path),'closure_changed':False,'monitor_pause_pending':True}
    for path in [ROOT/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl',H/'DISPATCH_JOURNAL.jsonl']:
        with path.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
    print(json.dumps({'verdict':proof['master_verdict'],'frozen_files':133,'review':str(review_path),'lineage':[(x['mvid'],len(x['documents'])) for x in lineage]},ensure_ascii=False))

if __name__=='__main__':main()
