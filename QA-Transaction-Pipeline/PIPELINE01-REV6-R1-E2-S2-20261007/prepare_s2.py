from pathlib import Path
import json,hashlib,shutil,datetime,ast,struct,uuid
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');Q=Path(__file__).resolve().parent
PKG=ROOT/'docs/WarEconomy_Master_Handoff_20261006';TASK=ROOT/'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01';FROZEN=TASK/'FROZEN_REV6_R1'
PRIORS=[ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-20261007',ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-S1-20261007']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
for source,names in [(PKG/'bootstrap/verify_local_identity.py',{'mvid'}),(PKG/'coordination/sol_recovery_identity_20261007.py',{'metadata_streams','codeview_guid','portable_pdb'})]:
    exec(compile(ast.Module(body=[n for n in ast.parse(source.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(source),'exec'),globals())
def lineage(dll):
    p=dll.with_suffix('.pdb');r=portable_pdb(p);r.update(dll=str(dll),dll_sha256=sha(dll),dll_mvid=mvid(dll),pdb_sha256=sha(p),codeview_guid=codeview_guid(dll));assert r['guid']==r['codeview_guid'] and all(x['matched'] for x in r['documents']);return r
def freeze():
    rows=[];manifest=json.loads((TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json').read_text(encoding='utf-8-sig'))
    for f in manifest['files']:
        paths=[Path(f['original_path']),Path(f['frozen_path']),Q/'Frozen'/Path(f['frozen_path']).relative_to(FROZEN)]
        actual=[dict(path=str(p),sha256=sha(p)) for p in paths];assert all(r['sha256']==f['sha256'] for r in actual);rows.append(dict(expected=f['sha256'],paths=actual))
    engine=json.loads((PKG/'bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json').read_text(encoding='utf-8-sig'))['files'];eng=[dict(path=p,sha256=sha(Path(p)),matched=sha(Path(p))==r['sha256']) for p,r in engine.items()];assert len(rows)==103 and len(eng)==19 and all(r['matched'] for r in eng)
    old=[]
    for p,count in zip(PRIORS,[297,312]):
        m=json.loads((p/'EVIDENCE_MANIFEST.json').read_text());assert len(m['files'])==count
        files=[dict(path=r['path'],sha256=sha(Path(r['path'])),matched=sha(Path(r['path']))==r['sha256']) for r in m['files']];assert all(r['matched'] for r in files)
        old.append(dict(root=str(p),inventory_sha256=sha(p/'EVIDENCE_MANIFEST.json'),files=files))
    return dict(at=now(),candidate103=rows,engine19=eng,prior_inventories=old,master_manifest_sha256=sha(TASK/'MASTER_REV6_R1_FREEZE_MANIFEST.json'))
def snapshot(rev):
    dest=Q/'Tooling'/rev;assert not dest.exists();shutil.copytree(Q/'Harness/bin/Release/net8.0',dest/'bin')
    for name in ['Program.cs','Harness.csproj']:shutil.copy2(Q/'Harness'/name,dest/name)
    (dest/'generated-source').mkdir()
    for p in (Q/'Harness/obj/Release/net8.0').glob('*.cs'):shutil.copy2(p,dest/'generated-source'/p.name)
    info=lineage(dest/'bin/Harness.dll');files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.rglob('*')) if p.is_file()]
    write(dest/'SNAPSHOT_BEFORE_EXECUTION.json',dict(at=now(),revision=rev,lineage=info,files=files,execution_command=['dotnet',str(dest/'bin/Harness.dll'),'<seed|interrupt|retry>','<S2 DB>','<commit-parent|commit-audit|stale-audit>'],build_command=['dotnet','build',str(Q/'Harness/Harness.csproj'),'-c','Release','--ignore-failed-sources','-p:NuGetAudit=false'],executed_yet=False))
    write(Q/'candidate-tooling-before.json',dict(at=now(),candidate_freeze=freeze(),candidate_lineage=[lineage(Q/'Runtime/WarEconomy.Server.dll'),lineage(Q/'Runtime/WarEconomy.Common.dll')],tooling_revision=rev))
    print(json.dumps(dict(revision=rev,dll_sha256=info['dll_sha256'],mvid=info['dll_mvid'],documents=len(info['documents']),files=len(files))))
if __name__=='__main__':
    assert not (Q/'Frozen').exists();shutil.copytree(FROZEN,Q/'Frozen');shutil.copytree(Q/'Frozen/WarEconomyMod/Source/Server/bin/Release/net8.0',Q/'Runtime')
    (Q/'Evidence').mkdir();(Q/'Databases').mkdir();shutil.copy2(PRIORS[1]/'Harness/Harness.csproj',Q/'Harness/Harness.csproj')
    write(Q/'freeze-before.json',freeze());write(Q/'bootstrap.json',dict(at=now(),wp='WP_QA_PIPELINE_REV6_R1_E2_SUPPLEMENT',revision='S2',delivery_id='SOL-PIPELINE-REV6-R1-E2-S2-20261008-d4da89a6e81e',qa_root_date_suffix='20261007 retained exactly as WP requests; actual execution/report date20261008',role='Independent QA',latest_user_contract='direct Master reporting authorized; no governance/automation/closure changes',prior_inventories_preserved=[297,312]))
    print('S2 QA copy prepared; frozen/original/copy103, Engine19, prior297/S1312 MATCHED before execution')
