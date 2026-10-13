from pathlib import Path
import json,hashlib,datetime,uuid,ast,struct
R=Path(r'C:\Users\user\Desktop\RimMulti');Q=R/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011';H=R/'docs/WarEconomy_Master_Handoff_20261006'
B=H/'coordination/MASTER_R27_CHILD_CAPTURE_PROTECTED_BASELINE_20261011.json';F=R/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868/MASTER_GATE05_R25_ROLE_USERDATA_REVIEW_FREEZE_MANIFEST.json';FR=R/'Dispatcher/CANDIDATES/G05R25-dd341868'
W=H/'WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_PREPARATION_S1.md';C=H/'MASTER_R27_CAPTURE_API_NAME_CORRECTION_20261012.md';EW=H/'WP_ENGINE_GATE05_R27_CHILD_CAPTURE.md';MR=H/'MASTER_REVIEW_ENGINE_GATE05_R26_DUAL_CHILD_REG_PREPARATION_20261011.md';OLD=R/'QA-Tactical-Engine/GATE05-R26-CHILD_REG-PREPARATION-S1-20261011/PROSPECTIVE_NORMAL_ORACLE.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,data):
    assert not p.exists(),str(p)
    p.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())
def preservation():
    for p,s in [(B,'FA99693BBED8427FA88B671A6140A1971A7A064C5856BED4E5826FE2682FD788'),(F,'FB436534FB8189D1BF20B2F888FAC2FDECCBBCB1C688CB6BD0ADCF7FEC9A0057'),(W,'7A17440B4598743EF214E0A08C81CB282F917BB081314B51D5CEB1D537FE07B9'),(C,'AA38D50D9B6EC9E2B74327BAB8348E1DEDD4EFB87BC0A2AECF0C85B27C39B7A3'),(EW,'F3C21DA71DCA1C32AE9A4F6BCA44669F0EFB4F2A7536B8BAA778B24147E4FB32'),(MR,'535B7C951DF14D491F78B5BE1A954BCBB130771F741F8CD60CCE4D0946E65F4A'),(OLD,'C103E85200D61536AAA048A08496A3DA9BE41CBB338786BF236BCFC1DF8B84CB')]:assert sha(p)==s,str(p)
    base=load(B);excluded={str(Path(x)).lower() for x in base['excluded_exact_current_mutable7']};assert len(excluded)==7
    rows=[];seen=set()
    for d in base['files']:
        p=Path(d['path']);key=str(p).lower();assert key not in excluded and key not in seen and p.resolve().is_relative_to(R.resolve());seen.add(key)
        actual=row(p);assert actual['sha256']==d['sha256'] and actual['bytes']==d['bytes'],str(p);rows.append(actual)
    frozen=[]
    for d in load(F)['files']:
        p=Path(d['frozen_path']);actual=row(p);assert actual['sha256']==d['sha256'] and actual['bytes']==d['size'];frozen.append(actual)
    assert len(rows)==13458 and len(frozen)==99
    return dict(at=now(),baseline=row(B),protected_unique_paths=13458,files=rows,frozen_files=frozen,all_matched=True,excluded_current_mutable7_not_read=True,A_ongoing_R27_source_runner_oracle_reports_not_read=True,candidate_QA_build_execute=0)
def identity():
    source=(R/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R27_PREPARATION_FROZEN_R25_LINEAGE.json')
    defs=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(Path=Path,ROOT=R,PKG=H,MAN=F,FROZEN=FR,Q=Q,ast=ast,struct=struct,uuid=uuid,hashlib=hashlib,sha=sha,load=load,write=write,now=now)
    exec(compile(ast.Module(body=defs,type_ignores=[]),'AST_ONLY_FROZEN_PE_PDB_METADATA','exec'),ns);v=ns['identity']();assert v[0]['dll_sha256']=='A9C31DB0EEEBDCFDF851C0160899A9E092579D8E333C030F34845A63FAAAB6E7' and v[0]['mvid']=='5553a632-0557-433f-8840-bb12875cf577';assert all(len(x['documents'])==4 and all(y['matched'] for y in x['documents']) for x in v);return v
if __name__=='__main__':
    Q.mkdir(parents=True,exist_ok=True);write(Q/'PRESERVATION_BEFORE.json',preservation());identity()
    result='SOL-GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R27_CHILD_CAPTURE_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R27-CHILD_CAPTURE-PREPARATION-S1-20261011-01',result_id=result,at=now(),status='ACKNOWLEDGED_INDEPENDENT_READ_ONLY_PREPARATION',report_path=str(R/'docs/QA_EngineHost_Gate05_R27_Child_Capture_Preparation_S1_20261011.md'),wp=row(W),api_correction=row(C),protected_paths=13458,frozen_R25_files=99,scope='Only frozenR25/preservedR26/Master15getter contract; no mutableR27/current7/A ongoing artifacts read',candidate_QA_build_load_execute=0,native_Process_game_assets_copy=0,governance_schema_scheduler_closure_changes=0,report_sha256='PENDING',manifest_sha256='PENDING',completion_sha256='PENDING',runtime_e2_released=False,foundation='HOLD')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);write(Q/'MASTER_PRIOR_DISPOSITION_RECEIPT.json',dict(at=now(),master_R26_review=row(MR),accepted_scope='R26 READ_ONLY preparation only; R27 PURECapture15/data-only approved; actual issuer/native OPEN',R26_completed_graph_unchanged=True,A_original_raw_not_rewritten=True,new_R27_execution_verdict='NOT_REVIEWED_NO_CANDIDATE',closure_changed=False,foundation='HOLD'))
    print(json.dumps(dict(result_id=result,ack_sha256=sha(Q/'ACK_INITIAL.json'),protected=13458,frozen99=True,PDB_sources=[4,4],mutableR27_read=0,builds_calls=0),indent=2))
