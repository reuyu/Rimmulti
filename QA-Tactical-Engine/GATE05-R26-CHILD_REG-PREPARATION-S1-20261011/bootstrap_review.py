import pathlib, json, hashlib, datetime, uuid
R=pathlib.Path(r'C:\Users\user\Desktop\RimMulti')
Q=R/'QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011'
H=R/'docs/WarEconomy_Master_Handoff_20261006'
B=H/'coordination/MASTER_R26_CHILD_REG_PREPARATION_PROTECTED_BASELINE_20261011.json'
F=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868/MASTER_GATE05_R25_ROLE_USERDATA_REVIEW_FREEZE_MANIFEST.json'
S=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R26-CHILD-REG-PREP-20261011-DIRECT-4d660e9b/MASTER_R26_READ_ONLY_SCOPE.json'
W=H/'WP_QA_ENGINE_GATE05_R26_CHILD_REGISTRATION_PREPARATION_S1.md'
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,x):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
def check(rows,key,sizekey):
    out=[]
    for r in rows:
        p=pathlib.Path(r[key]);assert p.is_relative_to(R),str(p)
        size=p.stat().st_size;digest=sha(p)
        assert size==r[sizekey] and digest==r['sha256'],str(p)
        out.append(dict(path=str(p),sha256=digest,bytes=size))
    return out
def preservation():
    assert sha(B)=='7C8F9B588BE47C45C5B39B5EB1573F4B238D1EB8F75D5EBF53B714C3C69DCE2B'
    assert sha(F)=='FB436534FB8189D1BF20B2F888FAC2FDECCBBCB1C688CB6BD0ADCF7FEC9A0057'
    assert sha(S)=='A0FD270ED08131CC6C1AD22849F058406691345CFF60A66FF9BF598AFE56BB98'
    assert sha(W)=='90C985A42BBA414697FBE362CFEED538364AC557DC3897800FACC0161D5AB5F4'
    b=check(load(B)['files'],'path','bytes');f=check(load(F)['files'],'frozen_path','size');s=check(load(S)['production_fixed_files'],'path','bytes')
    assert len(b)==13419 and len(f)==99 and len(s)==9
    return dict(at=now(),protected_unique_paths=len(b),protected_files=b,frozen_files=f,production_fixed_files=s,all_matched=True,production_build_execute=0,qa_runner_build_execute=0,native_assets_copy=0)
if __name__=='__main__':
    Q.mkdir(parents=True,exist_ok=True)
    write(Q/'PRESERVATION_BEFORE.json',preservation())
    rid='SOL-GATE05-R26-CHILD_REG-PREPARATION-S1-20261011-'+uuid.uuid4().hex
    ack=dict(schema_version=1,wp_id='WP_QA_ENGINE_GATE05_R26_CHILD_REGISTRATION_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R26-CHILD_REG-PREPARATION-S1-20261011-01',result_id=rid,at=now(),status='ACKNOWLEDGED_READ_ONLY_PREPARATION',wp_sha256=sha(W),protected_paths=13419,frozen_files=99,current_production_files=9,selected_sha256='A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7',selected_mvid_master_admitted='5553a632-0557-433f-8840-bb12875cf577',master_s2_disposition='QA_NEWLINE_SCOPED_CLOSED_S1_FAIL_PRESERVED_NATIVE_OPEN',production_build_execute=0,qa_runner_build_execute=0,native_assets_copy=0,report_hash='PENDING',evidence_manifest_hash='PENDING',completion_hash='PENDING',A_current_R26_proposal_read=False,closure_changed=False,runtime_e2_released=False,foundation='HOLD')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
    print(json.dumps(dict(result_id=rid,ack_sha256=sha(Q/'ACK_INITIAL.json'),protected=13419,frozen=99,current=9,all_matched=True),indent=2))
