from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046';FROZEN=TASK/'FROZEN_R5_CODEC_REVIEW';MAN=TASK/'MASTER_GATE05_R5_CODEC_REVIEW_FREEZE_MANIFEST.json';DEP=TASK/'MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
PREP=ROOT/'QA-Tactical-Engine/GATE05-R5-CODEC-PREP-S1-20261008'
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
    ns=dict(globals(),TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1',FROZEN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1/FROZEN_R4_REVIEW',MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1/MASTER_GATE05_R4_REVIEW_FREEZE_MANIFEST.json',OLDQ=ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008',PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008')
    defs=[n for n in ast.parse((PREP/'review_setup.py').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef)];exec(compile(ast.Module(body=defs,type_ignores=[]),'legacy_read_only_preservation','exec'),ns);d=ns['preservation']()
    p=PREP/'EVIDENCE_MANIFEST.json';files=verify_rows(load(p)['files'],'path');assert len(files)==19;d['qa_inventories'].append(dict(manifest=str(p),manifest_sha256=sha(p),files=files))
    for name in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','COMPLETION.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
        p=PREP/name;d['protected_terminal_and_manifest_bindings'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    assert sha(MAN)=='C8FFA291F9B67074AE4C9E916FE2761D3A10D2A691F44F96D58E05E0CDED1692';assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    d['r5_frozen113']=verify_rows(load(MAN)['files'],'frozen_path');assert len(d['r5_frozen113'])==113;d['managed_dep4']=verify_rows(load(DEP)['files'],'frozen_path');assert len(d['managed_dep4'])==4
    for p in [MAN,DEP]:d['protected_terminal_and_manifest_bindings'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    d['at']=now();d['mutable_r5_source_bin_obj_read_or_written']=False;return d
def flatten(d):
    rows={}
    for key in ['r5_frozen113','managed_dep4','r4_frozen232','r3_frozen133','r2_frozen107','r1_frozen147','old_archive19','pipeline206','protected_terminal_and_manifest_bindings']:rows.update({x['path']:(x['sha256'],x['bytes']) for x in d[key]})
    for m in d['qa_inventories']:rows[m['manifest']]=(m['manifest_sha256'],Path(m['manifest']).stat().st_size);rows.update({x['path']:(x['sha256'],x['bytes']) for x in m['files']})
    return rows
def identity():
    source=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R5_LINEAGE.json');nodes=[n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen_identity','exec'),ns);ids=ns['identity']();assert ids[0]['dll_sha256']=='930B69D012F34BFD3BB50F97B86629BAEA082D201A3A81696549DF1450075AE8';assert ids[0]['mvid']=='0e6b7cca-e02c-4af5-97da-5de31ec7aec3';assert ids[1]['mvid']=='7552980a-c4e1-4126-9451-e2114be623ae';return ids
if __name__=='__main__':
    assert not (Q/'ACK.json').exists();assert not (ROOT/'docs/QA_EngineHost_Gate05_R5_Codec_Independent_S1_20261008.md').exists()
    rid='SOL-GATE05-R5-CODEC-INDEPENDENT-S1-20261008-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R5_CODEC_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R5-CODEC-INDEPENDENT-S1-20261008-01',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='Frozen exact selected Debug pure Serialize/Deserialize and DTO normal unit QA plus static review; no full provider/game/native/operator execution',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R5_Codec_Independent_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Initial artifact hashes pending creation','QA-only runner build allowed; production rebuild/modification forbidden','Actual provider/cache/game/native/authority/promotion/A runner/TC11/adverse execution forbidden'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);d=preservation();write(Q/'PRESERVATION_BEFORE.json',d);ids=identity();print(json.dumps(dict(result_id=rid,r5frozen113=True,managed4=True,qa1241=True,protected_unique_paths=len(flatten(d)),pdb_documents=[len(x['documents']) for x in ids],release_actual_mvid=ids[1]['mvid']),indent=2))
