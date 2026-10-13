"""Freeze and copy the selected candidate; no runtime/build/candidate writes."""
from pathlib import Path
import ast, hashlib, json, shutil, datetime

ROOT = Path(r"C:\Users\user\Desktop\RimMulti")
Q = Path(__file__).resolve().parent
PKG = ROOT / "docs/WarEconomy_Master_Handoff_20261006"
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld")
ATTEMPT = "SOL-GATE05-E2-RESTART-8f58fb41362f4934a502e604a65f5896"

def sha(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""): h.update(block)
    return h.hexdigest().upper()

def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def stamp():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()

def snapshot():
    paths = set()
    trees = [ROOT/"scratch/WorkerBridgeMod", ROOT/"WarEconomyMod", GAME/"Mods/WarEconomy.WorkerBridge.PoC", GAME/"Mods/ProbeMod", GAME/"Mods/Harmony", GAME/"Mods/WarEconomy", GAME/"RimWorldWin64_Data/Managed"]
    for tree in trees:
        if tree.is_dir():
            paths.update(p for p in tree.rglob("*") if p.is_file())
    if (GAME/"Data").is_dir():
        paths.update(p for p in (GAME/"Data").rglob("*") if p.is_file() and p.suffix.lower() in (".xml", ".dll", ".json"))
    mf = json.loads((PKG/"bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json").read_text(encoding="utf-8-sig"))
    paths.update(Path(p) for p in mf["files"])
    return {str(p):dict(sha256=sha(p), bytes=p.stat().st_size, resolved_path=str(p.resolve())) for p in sorted(paths)}

def main():
    if (Q/"freeze-before.json").exists():
        raise RuntimeError("existing attempt freeze preserved; setup must not overwrite")
    mf = json.loads((PKG/"bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json").read_text(encoding="utf-8-sig"))
    discrepancies = [p for p,e in mf["files"].items() if not Path(p).is_file() or sha(Path(p))!=e["sha256"] or Path(p).stat().st_size!=e["bytes"]]
    assert not discrepancies, discrepancies
    write(Q/"bootstrap-freeze-recheck.json", dict(at=stamp(), files=len(mf["files"]), changes=discrepancies))
    before = snapshot()
    write(Q/"freeze-before.json", before)
    copies = [
        ROOT/"scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll",
        ROOT/"scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb",
        ROOT/"scratch/WorkerBridgeMod/Source/WorkerBridge.cs",
        ROOT/"scratch/WorkerBridgeMod/Source/EngineHostCensus.cs",
        ROOT/"scratch/TargetSettlement_Clean_ContextB.rws",
        ROOT/"scratch/TargetSettlement_Clean_ContextB.v4.census.json",
        ROOT/"scratch/run_semantic_authority_gate_05.py",
        ROOT/"scratch/semantic_authority_gate_05_results.json",
        ROOT/"docs/POC_EngineHost_Semantic_Authority_Gate_05.md",
        ROOT/"docs/QA_EngineHost_Semantic_Authority_Gate_04.md",
        PKG/"WP_QA_ENGINE_GATE05.md",
        PKG/"bootstrap/engine-pdb-recovered.json",
    ]
    inventory = []
    for p in copies:
        dest = Q/"Frozen"/p.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(p, dest)
        inventory.append(dict(source=str(p), copy=str(dest), sha256=sha(dest), same_bytes=sha(dest)==sha(p)))
    write(Q/"frozen-copy-index.json", inventory)
    ack = PKG/"coordination/SOL_RECOVERY_ACK_20261007.json"
    srs = ROOT/"docs"/"\uC694\uAD6C\uC0AC\uD56D_\uBA85\uC138\uC11C.md"
    assert srs.is_file()
    write(PKG/"coordination/SOL_RECOVERY_ACK_UTF8_CORRECTION_20261007.json", dict(original_ack=str(ack), original_ack_sha256=sha(ack), correction_scope="path rendering only; original bytes retained", canonical_srs_path=str(srs), canonical_srs_sha256=sha(srs), encoding="UTF-8", attempt_id=ATTEMPT, at=stamp()))
    write(Q/"attempt.json",dict(attempt_id=ATTEMPT,thread_id="01a11583-ff90-73e0-8916-d021e2bb038d",wp_id="WP_QA_ENGINE_GATE05",started_at=stamp(),scope="read-only defensive review and genuine positive native execution; bypass/forgery reproduction not executed",runtime_verdict="PENDING",freeze_count=len(before)))
    print(json.dumps(dict(freeze_count=len(before),bootstrap_files=len(mf["files"]),copies=len(inventory),qa_root=str(Q)),indent=2))

if __name__ == "__main__": main()
