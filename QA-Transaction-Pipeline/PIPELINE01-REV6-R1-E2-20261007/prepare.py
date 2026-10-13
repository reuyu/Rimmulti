from pathlib import Path
import ast,json,hashlib,shutil,struct,uuid,datetime
ROOT=Path(r"C:\Users\user\Desktop\RimMulti")
Q=Path(__file__).resolve().parent
PKG=ROOT/"docs/WarEconomy_Master_Handoff_20261006"
TASK=ROOT/"Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01"
FROZEN=TASK/"FROZEN_REV6_R1"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def checks():
    d=json.loads((TASK/"MASTER_REV6_R1_FREEZE_MANIFEST.json").read_text(encoding="utf-8-sig"))
    return [dict(path=r["frozen_path"],sha256=sha(Path(r["frozen_path"])),bytes=Path(r["frozen_path"]).stat().st_size,matched=sha(Path(r["frozen_path"]))==r["sha256"] and Path(r["frozen_path"]).stat().st_size==r["bytes"]) for r in d["files"]]
def main():
    rows=checks();assert len(rows)==103 and all(r["matched"] for r in rows)
    write(Q/"freeze-before.json",dict(at=now(),rows=rows))
    assert not (Q/"Frozen").exists()
    shutil.copytree(FROZEN,Q/"Frozen")
    shutil.copytree(Q/"Frozen/WarEconomyMod/Source/Server/bin/Release/net8.0",Q/"Runtime")
    reader=PKG/"bootstrap/verify_local_identity.py"
    defs=[n for n in ast.parse(reader.read_text(encoding="utf-8-sig")).body if isinstance(n,ast.FunctionDef) and n.name=="mvid"]
    exec(compile(ast.Module(body=defs,type_ignores=[]),str(reader),"exec"),globals())
    reader=PKG/"coordination/sol_recovery_identity_20261007.py"
    wanted={"metadata_streams","codeview_guid","portable_pdb"}
    defs=[n for n in ast.parse(reader.read_text(encoding="utf-8-sig")).body if isinstance(n,ast.FunctionDef) and n.name in wanted]
    exec(compile(ast.Module(body=defs,type_ignores=[]),str(reader),"exec"),globals())
    lineage=[]
    paths=[Q/"Frozen/WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.dll",Q/"Frozen/WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.dll",Q/"Frozen/scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.dll"]
    for dll in paths:
        pdb=dll.with_suffix(".pdb");info=portable_pdb(pdb)
        info.update(dll=str(dll),dll_sha256=sha(dll),mvid=mvid(dll),pdb_path=str(pdb),pdb_sha256=sha(pdb),codeview_guid=codeview_guid(dll))
        assert info["guid"]==info["codeview_guid"] and all(d["matched"] for d in info["documents"])
        lineage.append(info)
    eng=json.loads((PKG/"bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json").read_text(encoding="utf-8-sig"))["files"]
    engine=[dict(path=p,sha256=sha(Path(p)),matched=sha(Path(p))==v["sha256"]) for p,v in eng.items()]
    assert all(r["matched"] for r in engine)
    write(Q/"identity.json",dict(at=now(),candidate_lineage=lineage,engine19=engine,master_inventory_sha256=sha(TASK/"MASTER_REV6_R1_FREEZE_MANIFEST.json")))
    write(Q/"bootstrap.json",dict(at=now(),delivery_attempt="SOL-PIPELINE-REV6-R1-E2-20261007-9fe0c9b59acc58",role="Independent QA",thread="01a11583-ff90-73e0-8916-d021e2bb038d",latest_user_change="Direct Master-A, unified30min replaces Dispatcher/10min; QA direct tools/completion report retained. Master-owned A monitor PAUSED per release; no QA automation changed.",authority="Server final Domain Authority; E1 is not E2; no automatic closure; Foundation HOLD",read_scope="current handoff/C controlling corrections, latest governance/communication deltas, scoped ADR acceptance and Master corrections/reviews; canonical SRS retained",candidate_frozen_root=str(FROZEN),qa_only_builds=True,old_e1_executed=False))
    print(json.dumps(dict(frozen_matched=len(rows),pdb_documents=[len(x["documents"]) for x in lineage],mvid=lineage[0]["mvid"],engine_matched=len(engine)),indent=2))
if __name__=="__main__":main()
