from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
R2TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708';R2=R2TASK/'FROZEN_GATE05_R2_REJECTED';R2MAN=R2TASK/'MASTER_GATE05_R2_REJECTED_FREEZE_MANIFEST.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def verify_rows(rows,key):
    out=[]
    for r in rows:
        p=Path(r[key]);actual=sha(p);assert actual==r['sha256'],str(p);out.append(dict(path=str(p),sha256=actual,bytes=p.stat().st_size))
    return out
def preservation():
    assert sha(R2MAN)=='110A796F5699495998D61503016F8F7C0430B9EC988DD20220D51416AACD421C'
    r2=verify_rows(load(R2MAN)['files'],'frozen_path');assert len(r2)==107
    archive=ROOT/'Dispatcher/A_TASKS/ENGINE_GATE05_BASELINE_BEFORE_R1_20261008/ARCHIVE_MANIFEST.json';old19=verify_rows(load(archive)['files'],'archive_path');assert len(old19)==19
    r1man=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780/MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json';r1=verify_rows(load(r1man)['files'],'frozen_path');assert len(r1)==147
    pm=ROOT/'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_REV6_R1_FREEZE_MANIFEST.json';pipe=verify_rows(load(pm)['files'],'original_path')+verify_rows(load(pm)['files'],'frozen_path');assert len(pipe)==206
    inventories=[ROOT/'QA-Tactical-Engine/SEMANTIC-AUTHORITY05-E2-20261007/qa-evidence-manifest.json',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-20261007/EVIDENCE_MANIFEST.json',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S1-20261007/EVIDENCE_MANIFEST.json',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S2-20261007/EVIDENCE_MANIFEST.json'];qa=[]
    for path,count in zip(inventories,[324,297,312,238]):
        files=load(path)['files'];rows=[dict(path=k,sha256=v['sha256']) for k,v in files.items()] if isinstance(files,dict) else files
        checked=verify_rows(rows,'path');assert len(checked)==count;qa.append(dict(manifest=str(path),manifest_sha256=sha(path),files=checked))
    return dict(at=now(),r2_frozen107=r2,old_archive19=old19,r1_frozen147=r1,pipeline206=pipe,qa_inventories=qa,mutable_engine_sources_checked=False,installed_original_read=False,known_installed_incident='OPEN; no restoration or baseline normalization',hourly_monitor_changed=False)
def identity():
    docmap={str(Path(r['original_path'])).lower():Path(r['frozen_path']) for r in load(R2MAN)['files']}
    def frozen_doc(name):
        key=str(Path(name)).lower();assert key in docmap,'PDB document not present in R2 snapshot: '+name;return docmap[key]
    source=PKG/'bootstrap/verify_local_identity.py';defs=[n for n in ast.parse(source.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid'];ns=dict(struct=struct,uuid=uuid,Path=Path,hashlib=hashlib,frozen_doc=frozen_doc)
    ns['sha']=sha
    exec(compile(ast.Module(body=defs,type_ignores=[]),str(source),'exec'),ns)
    source=PKG/'coordination/sol_recovery_identity_20261007.py';names={'metadata_streams','codeview_guid','portable_pdb'};defs=[n for n in ast.parse(source.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names]
    class FrozenResolver(ast.NodeTransformer):
        def visit_Assign(self,node):
            if isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Name) and node.value.func.id=='Path' and len(node.value.args)==1 and isinstance(node.value.args[0],ast.Name) and node.value.args[0].id=='name':node.value.func=ast.Name(id='frozen_doc',ctx=ast.Load())
            return self.generic_visit(node)
    defs=[FrozenResolver().visit(n) if n.name=='portable_pdb' else n for n in defs];module=ast.fix_missing_locations(ast.Module(body=defs,type_ignores=[]));exec(compile(module,str(source),'exec'),ns)
    rows=[]
    for mode in ['Debug','Release']:
        dll=R2/f'scratch/WorkerBridgeMod/Source/bin/{mode}/net472/WarEconomy.WorkerBridge.PoC.dll';pdb=dll.with_suffix('.pdb');p=ns['portable_pdb'](pdb);p.update(dll=str(dll),dll_sha256=sha(dll),mvid=ns['mvid'](dll),pdb_sha256=sha(pdb),codeview_guid=ns['codeview_guid'](dll));assert p['guid']==p['codeview_guid'] and all(d['matched'] for d in p['documents']);p['source_resolution']='original document names resolved ONLY to matching R2 frozen_path';rows.append(p)
    for row in rows:
        for document in row['documents']:document['frozen_source_path']=str(frozen_doc(document['path']))
    write(Q/'R2_LINEAGE.json',dict(at=now(),candidates=rows,mutable_source_read=False,helper_original_top_level_executed=False))
    return rows
if __name__=='__main__':
    wp=PKG/'WP_QA_ENGINE_GATE05_R3_PREPARATION_S1.md';assert sha(wp)=='4F068A272E32925F164B598D94096AADC49BA14A63A427329778D5F86F6F9486';assert not (Q/'ACK.json').exists()
    rid='SOL-GATE05-R3-QA-PREP-S1-20261008-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',delivery_id='SOL-GATE05-R3-QA-PREP-S1-20261008-01',wp_id='WP_QA_ENGINE_GATE05_R3_PREPARATION',wp_revision='S1',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Immutable R2 independent static review; R3 matrix/native feasibility planning only',runtime_e2_released=False,report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R3_Preparation_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations='Report/manifest not yet created; no runtime/rebuild/reproduction authorization; new R3 candidate not inspected',latest_user_change='Existing Master monitor hourly60min/ACTIVE; A R3 active exact9 allowed Engine paths mutable; old installed incident OPEN; QA direct completion reporting retained')
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);write(Q/'PRESERVATION_BEFORE.json',preservation());rows=identity();print(json.dumps(dict(result_id=rid,r2_matched=107,archive_matched=19,r1_matched=147,pipeline=206,prior_qa=[324,297,312,238],pdb_frozen_documents=[len(r['documents']) for r in rows]),indent=2))
