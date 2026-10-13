from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa';FROZEN=TASK/'FROZEN_GATE05_R3_REVIEW';MAN=TASK/'MASTER_GATE05_R3_REVIEW_FREEZE_MANIFEST.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def verify_rows(rows,key):
    out=[]
    for row in rows:
        p=Path(row[key]);actual=sha(p);assert actual==row['sha256'],str(p);out.append(dict(path=str(p),sha256=actual,bytes=p.stat().st_size))
    return out
def preservation():
    assert sha(MAN)=='124C6AA900CB50ECE5C2F31B75BC197ACA194995BB90BDEDBD7EDA6B830E0972'
    r3=verify_rows(load(MAN)['files'],'frozen_path');assert len(r3)==133
    r2p=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708/MASTER_GATE05_R2_REJECTED_FREEZE_MANIFEST.json';r2=verify_rows(load(r2p)['files'],'frozen_path');assert len(r2)==107
    r1p=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780/MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json';r1=verify_rows(load(r1p)['files'],'frozen_path');assert len(r1)==147
    p=ROOT/'Dispatcher/A_TASKS/ENGINE_GATE05_BASELINE_BEFORE_R1_20261008/ARCHIVE_MANIFEST.json';arc=verify_rows(load(p)['files'],'archive_path');assert len(arc)==19
    p=ROOT/'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_REV6_R1_FREEZE_MANIFEST.json';pi=verify_rows(load(p)['files'],'frozen_path')+verify_rows(load(p)['files'],'original_path');assert len(pi)==206
    paths=[ROOT/'QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/qa-evidence-manifest.json',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-20261007/EVIDENCE_MANIFEST.json',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S1-20261007/EVIDENCE_MANIFEST.json',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/EVIDENCE_MANIFEST.json',ROOT/'QA-Tactical-Engine/GATE05-R3-QA-PREP-S1-20261008/EVIDENCE_MANIFEST.json'];qa=[]
    for p,count in zip(paths,[324,297,312,238,17]):
        files=load(p)['files'];rows=[dict(path=k,sha256=v['sha256']) for k,v in files.items()] if isinstance(files,dict) else files
        checked=verify_rows(rows,'path');assert len(checked)==count;qa.append(dict(manifest=str(p),manifest_sha256=sha(p),files=checked))
    return dict(at=now(),r3_frozen133=r3,r2_frozen107=r2,r1_frozen147=r1,old_archive19=arc,pipeline206=pi,qa_inventories=qa,mutable_source_or_installed_read=False)
def identity():
    mapping={str(Path(r['original_path'])).lower():Path(r['frozen_path']) for r in load(MAN)['files']}
    def frozen_doc(name):
        key=str(Path(name)).lower();assert key in mapping,'Document missing from R3 freeze: '+name;return mapping[key]
    ns=dict(Path=Path,struct=struct,uuid=uuid,hashlib=hashlib,sha=sha,frozen_doc=frozen_doc)
    p=PKG/'bootstrap/verify_local_identity.py';defs=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid'];exec(compile(ast.Module(body=defs,type_ignores=[]),str(p),'exec'),ns)
    p=PKG/'coordination/sol_recovery_identity_20261007.py';names={'metadata_streams','codeview_guid','portable_pdb'};defs=[n for n in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
    class Resolver(ast.NodeTransformer):
        def visit_Assign(self,n):
            if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='Path' and len(n.value.args)==1 and isinstance(n.value.args[0],ast.Name) and n.value.args[0].id=='name':n.value.func=ast.Name(id='frozen_doc',ctx=ast.Load())
            return self.generic_visit(n)
    defs=[Resolver().visit(n) if n.name=='portable_pdb' else n for n in defs];exec(compile(ast.fix_missing_locations(ast.Module(body=defs,type_ignores=[])),str(p),'exec'),ns)
    rows=[]
    for mode in ['Debug','Release']:
        dll=FROZEN/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');r=ns['portable_pdb'](pdb);r.update(dll=str(dll),dll_sha256=sha(dll),mvid=ns['mvid'](dll),pdb_sha256=sha(pdb),codeview_guid=ns['codeview_guid'](dll));assert r['guid']==r['codeview_guid'] and all(d['matched'] for d in r['documents'])
        for d in r['documents']:d['frozen_source_path']=str(frozen_doc(d['path']))
        rows.append(r)
    write(Q/'R3_LINEAGE.json',dict(at=now(),candidates=rows,document_source_resolution='frozen_path only',original_helper_top_level_executed=False,candidate_executed=False));return rows
if __name__=='__main__':
    assert not (Q/'ACK.json').exists();assert not (ROOT/'docs/QA_EngineHost_Gate05_R3_Independent_Review_S1_20261008.md').exists()
    rid='SOL-GATE05-R3-INDEPENDENT-REVIEW-S1-20261008-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R3_INDEPENDENT_REVIEW',wp_revision='S1',delivery_id='SOL-GATE05-R3-INDEPENDENT-REVIEW-S1-20261008-01',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Read-only frozen R3 independent static/normal-role/evidence review; no runtime E2',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R3_Independent_Review_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations='artifact hashes pending creation; no game/candidate/runner/build/adverse reproduction; retain original ACK bytes',current_monitor_contract='same hourly monitor PAUSED after A R3 terminal; QA direct completion reporting remains')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);write(Q/'PRESERVATION_BEFORE.json',preservation());rows=identity();print(json.dumps(dict(result_id=rid,frozen133=True,pdb_documents=[len(r['documents']) for r in rows],selected_sha256=rows[0]['dll_sha256'],selected_mvid=rows[0]['mvid']),indent=2))
