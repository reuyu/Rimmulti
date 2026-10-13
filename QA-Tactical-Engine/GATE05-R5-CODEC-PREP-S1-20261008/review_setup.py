from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R4-20261008-DIRECT-825ae8a1';FROZEN=TASK/'FROZEN_R4_REVIEW';MAN=TASK/'MASTER_GATE05_R4_REVIEW_FREEZE_MANIFEST.json'
OLDQ=ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R4-INDEPENDENT-REVIEW-S1-20261008'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def verify_rows(rows,key):
    out=[]
    for row in rows:
        p=Path(row[key]);actual=sha(p);assert actual==row['sha256'],str(p);out.append(dict(path=str(p),sha256=actual,bytes=p.stat().st_size))
    return out
def legacy(name):
    nodes=[n for n in ast.parse((PREVQ/'review_setup.py').read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name==name];ns=dict(globals());exec(compile(ast.Module(body=nodes,type_ignores=[]),'read_only_legacy_metadata','exec'),ns);return ns[name]()
def preservation():
    d=legacy('preservation');p=PREVQ/'EVIDENCE_MANIFEST.json';files=verify_rows(load(p)['files'],'path');assert len(files)==17;d['qa_inventories'].append(dict(manifest=str(p),manifest_sha256=sha(p),files=files))
    for name in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','COMPLETION.json','ACK_COMPLETION_BINDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json']:
        p=PREVQ/name;d['protected_terminal_and_manifest_bindings'].append(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size))
    d['at']=now();d['mutable_r5_candidate_read_or_written']=False;return d
def identity():return legacy('identity')
def flatten(d):
    rows={}
    for key in ['r4_frozen232','r3_frozen133','r2_frozen107','r1_frozen147','old_archive19','pipeline206','protected_terminal_and_manifest_bindings']:rows.update({x['path']:x['sha256'] for x in d[key]})
    for m in d['qa_inventories']:rows[m['manifest']]=m['manifest_sha256'];rows.update({x['path']:x['sha256'] for x in m['files']})
    return rows
if __name__=='__main__':
    assert not (Q/'ACK.json').exists();assert not (ROOT/'docs/QA_EngineHost_Gate05_R5_Codec_Preparation_S1_20261008.md').exists()
    rid='SOL-GATE05-R5-CODEC-PREP-S1-20261008-'+uuid.uuid4().hex
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R5_CODEC_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R5-CODEC-PREP-S1-20261008-01',result_id=rid,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,previous_wp='R4 independent review completed/reported/Master accepted',scope='Preparation on immutable historical R4 fields/content, positive normal codec plan and provenance criteria only; no R5 candidate review',report_path=str(ROOT/'docs/QA_EngineHost_Gate05_R5_Codec_Preparation_S1_20261008.md'),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Pending artifact hashes; immutable initial ACK retained','No mutable R5 source/bin/obj reads, candidate/runner/game/native execution/build/production changes/adverse reproduction'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);p=preservation();write(Q/'PRESERVATION_BEFORE.json',p);ids=identity();print(json.dumps(dict(result_id=rid,r4frozen232=True,qa1222=True,protected_unique_paths=len(flatten(p)),historical_r4_pdb_sources=[len(x['documents']) for x in ids]),indent=2))
