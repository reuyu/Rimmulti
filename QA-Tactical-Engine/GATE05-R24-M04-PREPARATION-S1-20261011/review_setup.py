from pathlib import Path
import json,hashlib,datetime,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent;PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006'
FROZEN=ROOT/'Dispatcher/CANDIDATES/G05R23-31bd3af2';SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
MAN=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R23-IDENTIFIER-MAPPING-20261011-DIRECT-31bd3af2/MASTER_GATE05_R23_IDENTIFIER_MAPPING_REVIEW_FREEZE_MANIFEST.json'
BASELINE=PKG/'coordination/MASTER_R24_M04_PREPARATION_PROTECTED_BASELINE_20261011.json';WP=PKG/'WP_QA_ENGINE_GATE05_R24_M04_PREPARATION_S1.md'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R24_M04_Preparation_S1_20261011.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
def preservation():
    assert sha(BASELINE)=='F02B2EA7360767393EBE679638FFDC548E43BC500B4B2EA0702E91BD50C88050' and sha(WP)=='DDF2EDFEC85EFAE0DB005B226C334238678CA729B7B618CE540E8EF216BA0234'
    assert sha(MAN)=='6D11497A1D2B8AA06DD3D8B8692E7B90B502D414C59455DC326ADC9921BF5CEE'
    files=[];seen=set()
    for r in load(BASELINE)['files']:
        p=Path(r['path']);k=str(p).lower();assert p.resolve().is_relative_to(ROOT.resolve()) and k not in seen;seen.add(k);size=r.get('bytes',r.get('size'));assert sha(p)==r['sha256'] and p.stat().st_size==size,str(p);files.append(row(p))
    assert len(files)==13002
    for r in load(MAN)['files']:
        p=Path(r['frozen_path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['size']
    return dict(at=now(),protected_unique_paths=13002,baseline=row(BASELINE),frozen_manifest=row(MAN),files=files,candidate_orasset_execution=False)
if __name__=='__main__':
    assert not (Q/'ACK_INITIAL.json').exists()
    write(Q/'PRESERVATION_BEFORE.json',preservation())
    assert sha(SOURCE)=='2076E3A88B57A55CDDB5F25950ED26EB2310224A43A91C8917EEC6588CD5983F'
    ack=dict(schema_version=1,producer='Sol',wp_id='WP_QA_ENGINE_GATE05_R24_M04_PREPARATION',wp_revision='S1',delivery_id='SOL-GATE05-R24-M04-PREPARATION-S1-20261011-01',result_id='SOL-GATE05-R24-M04-PREPARATION-S1-20261011-'+uuid.uuid4().hex,at=now(),status='ACKNOWLEDGED_IN_PROGRESS',scope='READ_ONLY exactfrozenR23M04roleuserdata-ownedfrontend-launchcontract preparation;no A R24crossreading',other_active_wp=False,report_path=str(REPORT),report_sha256=None,evidence_manifest_path=str(Q/'EVIDENCE_MANIFEST.json'),evidence_manifest_sha256=None,limitations=['ALL production/source/build9 fixed','Build-load-candidate/native/game/operator/process/adverse/copyinstall0','No PASS closure fullnativeE2NOTRELEASED FoundationHOLD'])
    write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack);print(json.dumps(dict(result_id=ack['result_id'],protected=13002,frozen=126,build_load_execute=0)))
