from pathlib import Path
import hashlib,json,shutil
Q=Path(__file__).resolve().parent;R=Q.parent.parent
ENGINE=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld')
WB=(ENGINE/'Mods/WarEconomy.WorkerBridge.PoC').resolve()
PROBE=R/'QA-Tactical-Engine/ENGINE02-20261002/ProbeMod'
OBSERVER='QA.SemanticAuthority.Observer.dll'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def prod():return {str(p):{'sha':sha(p),'bytes':p.stat().st_size} for p in (R/'WarEconomyMod').rglob('*') if p.is_file()}
def candidates():
 paths=list((R/'scratch/WorkerBridgeMod').rglob('*'))+list(WB.rglob('*'))+list(PROBE.rglob('*'))+list((ENGINE/'Mods/Harmony').rglob('*'))+list((R/'scratch/CorruptedFixtures').rglob('*'))
 paths+=list((R/'scratch/Profiles').rglob('*'))
 paths+=[R/n for n in ['POC_EngineHost_Semantic_Authority_Gate_04.md','scratch/CleanSettlementFixture.rws','scratch/TargetSettlement_Clean_ContextB.rws','scratch/TargetSettlement_Clean_ContextB.census.json','scratch/WarEconomy.WorkerBridge.PoC.dll','scratch/run_semantic_authority_gate_04.py','scratch/semantic_authority_gate_04_results.json']]
 paths +=list((R/'WarEconomyMod/1.6').rglob('*'))+list((R/'WarEconomyMod/About').rglob('*'))
 paths+=[ENGINE/'RimWorldWin64.exe',ENGINE/'RimWorldWin64_Data/Managed/Assembly-CSharp.dll',ENGINE/'RimWorldWin64_Data/Managed/UnityEngine.CoreModule.dll']
 return {str(p):{'sha':sha(p),'bytes':p.stat().st_size} for p in sorted(set(paths)) if p.is_file() and p.name!=OBSERVER}
