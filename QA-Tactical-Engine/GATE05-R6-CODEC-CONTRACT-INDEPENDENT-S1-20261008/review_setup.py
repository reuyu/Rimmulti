from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R6-1f657abe';MAN=TASK/'MASTER_GATE05_R6_CODEC_CONTRACT_REVIEW_FREEZE_MANIFEST.json'
R5TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046';DEP=R5TASK/'MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R5-CODEC-INDEPENDENT-S1-20261008'
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
    ns=dict(globals(),TASK=R5TASK,FROZEN=R5TASK/'FROZEN_R5_CODEC_REVIEW',MAN=R5TASK/'MASTER_GATE05_R5_CODEC_REVIEW_FREEZE_MANIFEST.json',PREP=ROOT/'QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008');defs=[n for n in ast.parse((PREVQ/'review_setup.py').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=defs,type_ignores=[]),'prior_read_only_inventory','exec'),ns);d=ns['preservation']()
    p=PREVQ/'EVIDENCE_MANIFEST.json';files=verify_rows(load(p)['files'],'path');assert len(files)==101;d['qa_inventories'].append(dict(manifest=str(p),manifest_sha256=sha(p),files=files))
    for name in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','COMPLETION.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
        p=PREVQ/name;d['protected_terminal_and_manifest_bindings'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    assert sha(MAN)=='61BCABD85920C84B978FD9E826DEB672B45F0935D5CC329C33A88F002A90CEEA';d['r6_frozen112']=verify_rows(load(MAN)['files'],'frozen_path');assert len(d['r6_frozen112'])==112;d['protected_terminal_and_manifest_bindings'].append(dict(path=str(MAN),sha256=sha(MAN),bytes=MAN.stat().st_size));d['at']=now();return d
def flatten(d):
    rows={}
    for key in ['r6_frozen112','r5_frozen113','managed_dep4','r4_frozen232','r3_frozen133','r2_frozen107','r1_frozen147','old_archive19','pipeline206','protected_terminal_and_manifest_bindings']:rows.update({x['path']:(x['sha256'],x['bytes']) for x in d[key]})
    for m in d['qa_inventories']:rows[m['manifest']]=(m['manifest_sha256'],Path(m['manifest']).stat().st_size);rows.update({x['path']:(x['sha256'],x['bytes']) for x in m['files']})
    return rows
def identity():
    p=ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py';source=p.read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R6_LINEAGE.json');defs=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'frozen_candidate_identity','exec'),ns);ids=ns['identity']();assert ids[0]['dll_sha256']=='721807FF00245B5B56DD94220531DB5DF620933E5905ADF692FC6336DD402E9B' and ids[0]['mvid']=='b3481641-2711-4b0e-96dd-db0983c2b689';assert ids[1]['mvid']=='354737fd-10a8-4160-8307-3e186c2118e6';return ids
if __name__=='__main__':
    assert not (Q/'ACK.json').exists();assert not (ROOT/'docs/QA_EngineHost_Gate05_R6_Codec_Contract_Independent_S1_20261008.md').exists()
    rid='SOL-GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R6_CODEC_CONTRACT_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R6-CODEC-CONTRACT-INDEPENDENT-S1-20261008-01',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Fresh frozen R6 defensive static and positive pure codec/normal ValidateContract helper only;no R5 PASS inheritance',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R6_Codec_Contract_Independent_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Initial artifact hashes pending creation','No production build/change/provider/cache/game/native/operator/old runner/TC11/TC13/adverse or rejection execution','Long-path partial candidate folder UNADMITTED;valid short freeze only'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);d=preservation();write(Q/'PRESERVATION_BEFORE.json',d);ids=identity();print(json.dumps(dict(result_id=rid,frozen112=True,qa1342=True,protected_unique_paths=len(flatten(d)),pdb_documents=[len(x['documents']) for x in ids]),indent=2))
