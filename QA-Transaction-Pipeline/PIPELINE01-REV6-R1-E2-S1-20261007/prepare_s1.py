from pathlib import Path
import ast,json,hashlib,shutil,struct,uuid,datetime
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent
PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006';TASK=ROOT/'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01';FROZEN=TASK/'FROZEN_REV6_R1'
PRIOR=ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-20261007'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
reader=PKG/'bootstrap/verify_local_identity.py'
exec(compile(ast.Module(body=[n for n in ast.parse(reader.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid'],type_ignores=[]),str(reader),'exec'),globals())
def freeze():
    manifest=json.loads((TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json').read_text(encoding='utf-8-sig'));rows=[]
    for f in manifest['files']:
        r=dict(expected=f['sha256'])
        for k in ['original_path','frozen_path']:
            p=Path(f[k]);r[k]=str(p);r[k+'_sha256']=sha(p);assert sha(p)==f['sha256']
        if (Q/'Frozen').exists():
            p=Q/'Frozen'/Path(f['frozen_path']).relative_to(FROZEN);r['qa_path']=str(p);r['qa_sha256']=sha(p);assert sha(p)==f['sha256']
        rows.append(r)
    eng=json.loads((PKG/'bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json').read_text(encoding='utf-8-sig'))['files'];engine=[dict(path=p,sha256=sha(Path(p)),matched=sha(Path(p))==r['sha256']) for p,r in eng.items()];assert len(rows)==103 and len(engine)==19 and all(r['matched'] for r in engine)
    old=json.loads((PRIOR/'EVIDENCE_MANIFEST.json').read_text());prior=[dict(path=r['path'],matched=sha(Path(r['path']))==r['sha256']) for r in old['files']];assert len(prior)==297 and all(r['matched'] for r in prior)
    return dict(at=now(),candidate103=rows,engine19=engine,prior297=prior,prior_inventory_sha256=sha(PRIOR/'EVIDENCE_MANIFEST.json'),prior_report_sha256=sha(ROOT/'docs/QA_Production_Transaction_Pipeline_01_REV6_R1.md'),master_manifest_sha256=sha(TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json'))
def snapshot(rev):
    dest=Q/'Tooling'/rev;assert not dest.exists();shutil.copytree(Q/'Harness/bin/Release/net8.0',dest/'bin');shutil.copy2(Q/'Harness/Program.cs',dest/'Program.cs');shutil.copy2(Q/'Harness/Harness.csproj',dest/'Harness.csproj')
    for p in (Q/'Harness/obj/Release/net8.0').glob('*.cs'):
        (dest/'generated-source').mkdir(exist_ok=True);shutil.copy2(p,dest/'generated-source'/p.name)
    dll=dest/'bin/Harness.dll';pdb=dll.with_suffix('.pdb');files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.rglob('*')) if p.is_file()]
    write(dest/'SNAPSHOT_BEFORE_EXECUTION.json',dict(at=now(),tooling_revision=rev,source_sha256=sha(dest/'Program.cs'),dll=str(dll),dll_sha256=sha(dll),dll_mvid=mvid(dll),pdb_sha256=sha(pdb),files=files,execution_command=['dotnet',str(dll),'<mode>','<QA-owned DB path>'],executed_yet=False))
    print(json.dumps(dict(revision=rev,dll_sha256=sha(dll),mvid=mvid(dll),files=len(files))))
if __name__=='__main__':
    write(Q/'freeze-before.json',freeze());assert not (Q/'Frozen').exists();shutil.copytree(FROZEN,Q/'Frozen');shutil.copytree(Q/'Frozen/WarEconomyMod/Source/Server/bin/Release/net8.0',Q/'Runtime')
    (Q/'Databases').mkdir();(Q/'Evidence').mkdir();shutil.copy2(PRIOR/'Harness/Harness.csproj',Q/'Harness/Harness.csproj')
    write(Q/'bootstrap.json',dict(at=now(),wp='WP_QA_PIPELINE_REV6_R1_E2_SUPPLEMENT',revision='S1',delivery_id='SOL-PIPELINE-REV6-R1-E2-S1-20261007-54d0d39948ff',latest_user_contract='Direct Master-A, unified30min; QA direct completion report; no governance/automation changes',authorization='Existing human QA and report-to-Master authorization; exact Master S1 local WP',prior_provenance_gap_not_retroactively_fixed=True))
    print('S1 bootstrap: frozen/original103, Engine19, prior297 MATCHED')
