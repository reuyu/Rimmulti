"""R29 preparation only: protected byte hashing, no mutable R29 reads/build/calls."""
from pathlib import Path
import json,hashlib,datetime,uuid
R=Path(r'C:\Users\user\Desktop\RimMulti')
Q=R/'QA-Tactical-Engine/GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012'
H=R/'docs/WarEconomy_Master_Handoff_20261006'
W=H/'WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_PREPARATION_S1.md'
C=H/'MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md'
MR=H/'MASTER_REVIEW_ENGINE_GATE05_R28_DUAL_OPERATOR_ROUTE_20261012.md'
B=H/'coordination/MASTER_R29_STARTUP_PAIR_PROTECTED_BASELINE_20261012.json'
F=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R27-CHILD-CAPTURE-20261011-DIRECT-cdc223f3/MASTER_GATE05_R27_CHILD_CAPTURE_REVIEW_FREEZE_MANIFEST.json'
FR=R/'Dispatcher/CANDIDATES/G05R27-cdc223f3'
OLD=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011/PROSPECTIVE_CAPTURE_ORACLE.json'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest().upper()
def pin(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,x):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def preservation():
    assert sha(B)=='FA0A09D459C03127301504251BF0188CEC04A3C5415A61F466DEC357298D95C3'
    assert sha(C)=='2EEE68E2E3B6D0FD3777D8F1F13EDDE3239D7697CD9339B03B324D108CE9A531'
    assert sha(F)=='1FD4B9EFB368EE03F327241418C5CC0ACC08F9210E6E1BD271AECC373D219EE3'
    base=load(B);excluded={Path(x) for x in base['excluded_exact_current_mutable7']}
    assert len(excluded)==7
    out=[]
    for r in base['files']:
        p=Path(r['path']);assert p.is_relative_to(R) and p not in excluded
        assert not p.is_relative_to(R/'scratch/OperatorStartupPairR29')
        v=pin(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],str(p);out.append(v)
    assert len(out)==14105
    frozen=[]
    for r in load(F)['files']:
        p=Path(r['frozen_path']);v=pin(p)
        assert v['sha256']==r['sha256'] and v['bytes']==r['size'];frozen.append(v)
    fixed=[pin(R/'scratch/WorkerBridgeMod/Source'/n) for n in ['EngineHostCensus.cs','WorkerBridge.csproj']]
    for v in fixed:assert v in out
    return dict(at=now(),protected_unique_paths=14105,protected_files=out,frozen83=frozen,current_fixed_Census_csproj=fixed,excluded_mutable7=[str(p) for p in sorted(excluded)],mutable_R29_source_publisher_bin_obj_read=False,all_matched=True,compiler_candidate_game_native_Process_execution=0)
if __name__=='__main__':
    Q.mkdir(parents=True,exist_ok=True)
    write(Q/'PRESERVATION_BEFORE.json',preservation())
    ack=dict(at=now(),schema_version=1,wp_id='WP_QA_ENGINE_GATE05_R29_STARTUP_PAIR_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R29-STARTUP_PAIR-PREP-S1-20261012-01',result_id='SOL-GATE05-R29-STARTUP_PAIR-PREPARATION-S1-20261012-'+uuid.uuid4().hex,status='ACKNOWLEDGED_READ_ONLY_NORMAL_ORACLE_PREPARATION',wp=pin(W),contract=pin(C),master_review=pin(MR),baseline=pin(B),frozen_manifest=pin(F),protected_paths=14105,frozen_files=83,current_fixed_files=2,old_R28_artifact_accepted_operational_usage_failed_separate=True,mutable_R29_read=False,builds=0,candidate_calls=0,native_lifecycle_Process_adverse_runs=0,R29_candidate_verdict='NOT_REVIEWED',report_hash='PENDING',manifest_hash='PENDING',completion_hash='PENDING',foundation='HOLD',native_E2='NOT_RELEASED')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
    write(Q/'RECOVERY_DELTA_AND_MASTER_BINDING.json',dict(at=now(),controlling_inputs=[pin(p) for p in [W,C,MR,B,F,OLD]],master_R28_artifact_verdict='ACCEPTED_STATIC_EVIDENCE',R28_operational_status='usagefailed/notLoaded175 distinct from completed artifact',actual_R29_delivery_proof=pin(H/'coordination/MASTER_SOL_R29_STARTUP_PAIR_PREPARATION_DELIVERY_VERIFICATION_20261012.json'),current_hourly='ACTIVE60min Master owned unchanged',scope='Frozen R27/history + adopted new auxiliary pair contract, no mutable R29 source/publisher/output read',new_aux_contract='ADOPTED_CONTRACT_NOT_YET_INDEPENDENTLY_REVIEWED_AS_IMPLEMENTATION',candidate_and_native_execution=0))
    print(json.dumps(dict(result_id=ack['result_id'],ack=pin(Q/'ACK_INITIAL.json'),protected=14105,frozen=83,fixed=2)))

