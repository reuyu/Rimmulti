from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1';FROZEN=TASK/'FROZEN_R4_REVIEW';MAN=TASK/'MASTER_GATE05_R4_REVIEW_FREEZE_MANIFEST.json'
OLDQ=ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008'
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
    source=(OLDQ/'review_setup.py').read_text(encoding='utf-8-sig');fn=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='preservation'];ns=dict(globals(),MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/MASTER_GATE05_R3_REVIEW_FREEZE_MANIFEST.json');exec(compile(ast.Module(body=fn,type_ignores=[]),'old_preservation_read_only', 'exec'),ns);data=ns['preservation']()
    assert sha(MAN)=='D047D0095CEDDA8E5F0FB6871EA4C24AF0866CA569514049FFAD7E91B7C1460C';rows=verify_rows(load(MAN)['files'],'frozen_path');assert len(rows)==232;data['r4_frozen232']=rows
    p=OLDQ/'EVIDENCE_MANIFEST.json';files=verify_rows(load(p)['files'],'path');assert len(files)==17;data['qa_inventories'].append(dict(manifest=str(p),manifest_sha256=sha(p),files=files))
    bindings=[]
    for name in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','COMPLETION.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
        p=OLDQ/name;bindings.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    for p in [MAN,ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/MASTER_GATE05_R3_REVIEW_FREEZE_MANIFEST.json',ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708/MASTER_GATE05_R2_REJECTED_FREEZE_MANIFEST.json',ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780/MASTER_GATE05_R1_REJECTED_FREEZE_MANIFEST.json',ROOT/'Dispatcher/A_TASKS/ENGINE_GATE05_BASELINE_BEFORE_R1_20261008/ARCHIVE_MANIFEST.json',ROOT/'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_REV6_R1_FREEZE_MANIFEST.json']:
        bindings.append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    data['protected_terminal_and_manifest_bindings']=bindings;data['at']=now();return data
def identity():
    source=(OLDQ/'review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R4_LINEAGE.json');fn=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=fn,type_ignores=[]),'frozen_pdb_metadata_only','exec'),ns);return ns['identity']()
if __name__=='__main__':
    assert not (Q/'ACK.json').exists();assert not (ROOT/'docs/QA_EngineHost_Gate05_R4_Independent_Review_S1_20261008.md').exists()
    rid='SOL-GATE05-R4-INDEPENDENT-REVIEW-S1-20261008-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R4_INDEPENDENT_REVIEW',wp_revision='S1',delivery_id='SOL-GATE05-R4-INDEPENDENT-REVIEW-S1-20261008-01',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,previous_wp='R3 independent review completed and reported; new R4 turn executing reads/metadata only',prior_usage_failure_not_assumed_current=True,scope='exact frozen R4 independent static/evidence review; runtime E2 not released',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R4_Independent_Review_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Initial artifact hashes pending creation','candidate/runner/game/native execution0,build0,production change0,adverse reproduction0'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);write(Q/'PRESERVATION_BEFORE.json',preservation());ids=identity();print(json.dumps(dict(result_id=rid,frozen232=True,prior387=True,qa1205=True,pdb_documents=[len(x['documents']) for x in ids],dll_sha=ids[0]['dll_sha256'],mvid=ids[0]['mvid']),indent=2))
