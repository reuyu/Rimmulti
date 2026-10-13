from pathlib import Path
import ast,json,hashlib,datetime,uuid,struct
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
TASK=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R23-IDENTIFIER-MAPPING-20261011-DIRECT-31bd3af2';FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R23-31bd3af2';MAN=TASK/'MASTER_GATE05_R23_IDENTIFIER_MAPPING_REVIEW_FREEZE_MANIFEST.json'
DEP=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R23_QA_INDEPENDENT_PROTECTED_BASELINE_RECONCILED_20261011.json';PREP=ROOT/'QA-Tactical-Engine/GATE05-R13-POLICY-CACHE-LIFECYCLE-PREP-S1-20261009';PREVQ=ROOT/'QA-Tactical-Engine/GATE05-R14-POLICY-CAPTURE-PUBLICATION-INDEPENDENT-S1-20261009'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R23_Identifier_Mapping_Independent_S1_20261011.md';ADMISSION=PKG/'coordination/MASTER_GATE05_R23_IDENTIFIER_MAPPING_E1_VERIFICATION_20261011.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def preservation():
    assert sha(BASELINE)=='58A4E0E9F7748C0E23E5D2818CA29D3C72151E3052E2811989C4290B9A520181'
    assert sha(MAN)=='6D11497A1D2B8AA06DD3D8B8692E7B90B502D414C59455DC326ADC9921BF5CEE'
    assert sha(DEP)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    assert sha(PKG/'WP_QA_ENGINE_GATE05_R23_IDENTIFIER_MAPPING_INDEPENDENT_S1.md')=='3AB773C5CEF01FE98514D78C2C3087D64000CBC3B39A5060214FCEC811DDC662'
    d=load(BASELINE);files=[];seen=set()
    for r in d['files']:
        p=Path(r['path']);key=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and key not in seen;seen.add(key)
        size=r['bytes'] if 'bytes' in r else r['size'];assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==d['protected_unique_paths']==12350
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),baseline=row(BASELINE),protected_unique_paths=len(files),files=files,original_steam_userdata_mutable_candidate_read=False)
def identity():
    text=(ROOT/'QA-Tactical-Engine/GATE05-R3-INDEPENDENT-REVIEW-S1-20261008/review_setup.py').read_text(encoding='utf-8-sig').replace('R3_LINEAGE.json','R23_FROZEN_LINEAGE.json')
    defs=[n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='identity'];ns=dict(globals());exec(compile(ast.Module(body=defs,type_ignores=[]),'metadata_only_frozen_definitions','exec'),ns);r=ns['identity']()
    assert r[0]['dll_sha256']=='4379BE35700337F797BB17F25D5BAC2A8014FAA9332D9878E587A12E5758A9C4' and r[0]['mvid']=='5bdada93-1f00-40e3-ab4d-7b23f4b2d086'
    assert r[1]['mvid']=='af4e01b8-2da9-479c-b4ab-9bde73824bbd';return r



if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists() and not REPORT.exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation());meta=identity()
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R23_IDENTIFIER_MAPPING_INDEPENDENT',wp_revision='S1',delivery_id='SOL-GATE05-R23-IDENTIFIER_MAPPING-INDEPENDENT-S1-20261011-01',result_id='SOL-GATE05-R23-IDENTIFIER_MAPPING-INDEPENDENT-S1-20261011-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',other_active_wp=False,scope='ExactfrozenR23 STATIC+normalPURE20receipt fullgraph originalUnicodeoriginplan actualusedClone14copy rolecap4equivalence UTCopaque plusnormal16snapshot only',report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['Terminal hashes pending','Opaque policyId/revision whitespaceUnicode unchanged independentoracle;normalFAILreportedwithoutcorrection/rerun','Process/globalWorkerinstaller/bootstrap/native/adverse0','NewQArunner notyetbuilt','FullGateE2NOTRELEASED/FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected_unique_paths=12350,selected_sha256=meta[0]['dll_sha256'],candidateexecuted=False)))
