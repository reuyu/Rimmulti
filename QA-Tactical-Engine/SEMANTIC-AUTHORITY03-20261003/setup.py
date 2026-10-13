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
 paths+=[R/n for n in ['POC_EngineHost_Semantic_Authority_Gate_03.md','scratch/CleanSettlementFixture.rws','scratch/TargetSettlement_Clean_ContextB.rws','scratch/TargetSettlement_Clean_ContextB.census.json','scratch/WarEconomy.WorkerBridge.PoC.dll','scratch/run_semantic_authority_gate_03.py','scratch/semantic_authority_gate_03_results.json']]
 paths +=list((R/'WarEconomyMod/1.6').rglob('*'))+list((R/'WarEconomyMod/About').rglob('*'))
 paths+=[ENGINE/'RimWorldWin64.exe',ENGINE/'RimWorldWin64_Data/Managed/Assembly-CSharp.dll',ENGINE/'RimWorldWin64_Data/Managed/UnityEngine.CoreModule.dll']
 return {str(p):{'sha':sha(p),'bytes':p.stat().st_size} for p in sorted(set(paths)) if p.is_file() and p.name!=OBSERVER}
if __name__=='__main__':
 assert not (Q/'candidate-before.json').exists()
 write(Q/'candidate-before.json',candidates());write(Q/'production-before.json',prod())
 for folder in ['Frozen','Evidence','Observer','Profiles']:(Q/folder).mkdir(exist_ok=True)
 for n in ['CleanSettlementFixture.rws','TargetSettlement_Clean_ContextB.rws','TargetSettlement_Clean_ContextB.census.json','WarEconomy.WorkerBridge.PoC.dll','run_semantic_authority_gate_03.py','semantic_authority_gate_03_results.json']:
  shutil.copy2(R/'scratch'/n,Q/'Frozen'/n)
 for n in ['WorkerBridge.cs','EngineHostCensus.cs']:
  for label,root in [('Reported',R/'scratch/WorkerBridgeMod'),('Installed',WB)]:
   p=root/'Source'/n
   if p.exists():shutil.copy2(p,Q/'Frozen'/(label+'-'+n))
 shutil.copy2(R/'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb',Q/'Frozen/WarEconomy.WorkerBridge.PoC.pdb')
 for letter in ['A','B','C']:
  root=R/f'scratch/Profiles/Profile_Pos_{letter}'
  for p in root.rglob('*'):
   if p.is_file() and (p.suffix in ['.rws','.json'] or p.name=='ModsConfig.xml'):
    dest=Q/'Frozen'/('Developer-'+letter)/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 shutil.copy2(R/'POC_EngineHost_Semantic_Authority_Gate_03.md',Q/'Frozen/POC_EngineHost_Semantic_Authority_Gate_03.md')
 expected='A95B324EC7DA26155ACF75E64D5B122CF987903157A24C984AAE05D4EE7972CC'
 assert sha(Q/'Frozen/WarEconomy.WorkerBridge.PoC.dll')==expected
 assert sha(WB/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll')==expected
 old=R/'QA-Tactical-Engine/SEMANTIC-GATE02-20261003/Observer'
 for name in ['Observer.cs','Mutations.cs','Observer.csproj']:
  s=(old/name).read_text(encoding='utf-8').replace('QA.SemanticGate.Observer','QA.SemanticAuthority.Observer').replace('QASemantic','QAAuthority').replace('sgqaport','agqaport').replace('qa.semanticgate.faults','qa.semanticauthority.faults');(Q/'Observer'/name).write_text(s,encoding='utf-8')
 print(json.dumps({'workerSha':expected,'installedRoot':str(WB),'candidateFiles':len(candidates()),'productionFiles':len(prod()),'installedSourceMatches':{n:sha(WB/'Source'/n)==sha(R/'scratch/WorkerBridgeMod/Source'/n) for n in ['WorkerBridge.cs','EngineHostCensus.cs']}}))
