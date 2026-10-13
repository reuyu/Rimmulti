"""R28 read-only QA bootstrap; byte hashing only, no assembly loading."""
from pathlib import Path
import json, hashlib, datetime, uuid, ast, struct
R=Path(r'C:\Users\user\Desktop\RimMulti')
Q=R/'QA-Tactical-Engine/GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012'
H=R/'docs/WarEconomy_Master_Handoff_20261006'
B=H/'coordination/MASTER_R28_OPERATOR_ROUTE_PROTECTED_BASELINE_20261012.json'
F=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R27-CHILD-CAPTURE-20261011-DIRECT-cdc223f3/MASTER_GATE05_R27_CHILD_CAPTURE_REVIEW_FREEZE_MANIFEST.json'
D=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
W=H/'WP_QA_ENGINE_GATE05_R28_FRONTEND_ROUTE_INDEPENDENT_S1.md'
FR=R/'Dispatcher/CANDIDATES/G05R27-cdc223f3'
SRC=FR/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
DLL=FR/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
PDB=DLL.with_suffix('.pdb')
def now(): return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest().upper()
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def pin(p): return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def check(rows,key,sizekey):
    out=[]
    for row in rows:
        p=Path(row[key]); assert p.is_relative_to(R),str(p)
        v=pin(p); assert v['sha256']==row['sha256'] and v['bytes']==row[sizekey],str(p)
        out.append(v)
    return out
def preservation():
    for p,e in [(B,'6E87FEEC96B34498EB608D3AB495FAE26188AC977DE510CB1AC07CA4078E7FCE'),(F,'1FD4B9EFB368EE03F327241418C5CC0ACC08F9210E6E1BD271AECC373D219EE3'),(D,'7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'),(W,'900F65801BEBE556A925FF4087B0D13FD65FF79729FF605BB4370096FDFDC55C')]:
        assert sha(p)==e,str(p)
    b=check(load(B)['files'],'path','bytes')
    f=check(load(F)['files'],'frozen_path','size')
    d=check(load(D)['files'],'frozen_path','size')
    assert len(b)==14045 and len(f)==83 and len(d)==4
    assert sha(SRC)=='B292AB846F78568F74333F58C5967ED38CAAA2F59B07393FC846F4329583E388'
    assert sha(DLL)=='68BFE5105FA0471AAAF7943009703BB2599B39C5B572833507D6733BCE63CF64'
    assert sha(PDB)=='F0BC1B7D92F67593EA967F56A90EE302C76B920A46B98EF77219F7B884C47814'
    return dict(at=now(),protected_unique_paths=len(b),protected_files=b,frozen_files=f,managed_files=d,all_matched=True,production_build_execute=0,qa_runner_build_execute=0,native_assets_copy=0)
def recovery():
    names=['AGENTS.md','docs/요구사항_명세서.md','docs/MASTER_GOVERNANCE_CURRENT.md',
      'Dispatcher/README.md','Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md',
      'Dispatcher/MASTER_COMMUNICATION_STATE.json','Dispatcher/MASTER_RECEIPTS.json','Dispatcher/MASTER_MONITOR_JOURNAL.jsonl']
    names += ['docs/WarEconomy_Master_Handoff_20261006/'+n for n in ['00_START_HERE.md','MASTER_HANDOFF.md','C_REVIEW_CORRECTIONS_CONSOLIDATED.md','C_REVIEW_HISTORY_EXTRACTS.md','IDE_BOOTSTRAP_VERIFICATION.md','MASTER_PROJECT_STATE.md','MASTER_DECISION_LOG.md','QA_DEFECT_LEDGER.md','MASTER_AGENT_DISPATCH_BOARD.md','DISPATCHER_STATE.json','DISPATCH_JOURNAL.jsonl','ADR_ACCEPTANCE_AND_AUTHORITY_MAP.md','reference_adrs/ADR-006B_ContentProfileFingerprint.md','history/MASTER_DECISION_LOG_MDR-067.md','MASTER_REVIEW_ENGINE_GATE05_R27_CHILD_CAPTURE_INDEPENDENT_S2_20261012.md']]
    rows=[]
    for n in names:
        p=R/n
        if not p.exists(): rows.append(dict(path=str(p),missing=True));continue
        t=p.read_text(encoding='utf-8-sig')
        v=pin(p);v['latest_excerpt']=t[-3500:]
        rows.append(v)
    return dict(at=now(),read_full_text_for_local_recovery=True,files=rows,A_R28_proposal_read=False,current_hourly_lifecycle='ACTIVE_AFTER_A_R28_SENT_MASTER_OWNED_UNCHANGED',authority='Dedicated Server final Domain Authority; MD125-132 control stage authority; no new PKI',historical_preparation_not_runtime_pass=True,engine_pipeline_schema_GQ1='OPEN',foundation='HOLD',native_full_gate_E2='NOT_RELEASED')
if __name__=='__main__':
    Q.mkdir(parents=True,exist_ok=True)
    write(Q/'RECOVERY_REFERENCE_AUDIT.json',recovery())
    write(Q/'PRESERVATION_BEFORE.json',preservation())
    a=dict(schema_version=1,wp_id='WP_QA_ENGINE_GATE05_R28_FRONTEND_ROUTE_INDEPENDENT',wp_revision='S1',
      delivery_id='SOL-GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012-01',
      result_id='SOL-GATE05-R28-FRONTEND_ROUTE-INDEPENDENT-S1-20261012-'+uuid.uuid4().hex,
      at=now(),status='ACKNOWLEDGED_READ_ONLY_STATIC_FRONTEND_ROUTE',wp=pin(W),baseline=pin(B),frozen_manifest=pin(F),
      protected_paths=14045,frozen_files=83,managed_files=4,selected=pin(DLL),pdb=pin(PDB),
      selected_mvid_master_admitted='44ba753c-6570-49d8-8068-4edf87a4e5d0',A_current_R28_proposal_read=False,
      production_build_execute=0,qa_runner_build_execute=0,assembly_invocations=0,native_game_lifecycle_calls=0,
      report_hash='PENDING',evidence_manifest_hash='PENDING',completion_hash='PENDING',
      runtime_e2_released=False,foundation='HOLD',closure_changed=False)
    write(Q/'ACK_INITIAL.json',a);write(Q/'ACK.json',a)
    print(json.dumps(dict(result_id=a['result_id'],ack_sha256=sha(Q/'ACK_INITIAL.json'),protected=14045,frozen=83,managed=4,all_matched=True)))

