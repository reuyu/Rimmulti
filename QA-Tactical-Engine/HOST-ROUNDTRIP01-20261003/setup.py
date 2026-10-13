from pathlib import Path
import json,hashlib,shutil,xml.etree.ElementTree as E
Q=Path(__file__).parent.resolve();R=Q.parent.parent
A=Path(r'C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch')
ENGINE=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
if __name__=='__main__':
 manifest={str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in (R/'WarEconomyMod').rglob('*') if p.is_file()}
 write(Q/'production-before.json',manifest)
 wb=A/'WorkerBridgeMod';paths=[R/'scratch/ComplexSettlementFixture.rws',R/'scratch/TargetSettlement_ContextB.rws',R/'scratch/Census_Baseline.json',R/'scratch/settlement_roundtrip_results.json',R/'POC_EngineHost_Settlement_RoundTrip_01.md']
 paths+=list((R/'scratch').glob('*.py'))+[wb/'Source/WorkerBridge.cs',wb/'Source/EngineHostCensus.cs',wb/'Source/WorkerBridge.csproj',wb/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll',ENGINE/'RimWorldWin64.exe',ENGINE/'RimWorldWin64_Data/Managed/Assembly-CSharp.dll']
 paths+=list((R/'QA-Tactical-Engine/ENGINE02-20261002/ProbeMod').glob('1.6/Assemblies/*.dll'))
 paths+=list((A/'PoC_RoundTrip/Saves').glob('*.rws'))
 write(Q/'candidate-before.json',{str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in paths if p.exists()})
 for p in [R/'scratch/ComplexSettlementFixture.rws',R/'scratch/TargetSettlement_ContextB.rws',R/'scratch/Census_Baseline.json',wb/'Source/WorkerBridge.cs',wb/'Source/EngineHostCensus.cs',wb/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll',R/'scratch/census_oracle.py',R/'scratch/run_settlement_roundtrip_poc.py']:
  (Q/'Frozen').mkdir(exist_ok=True);shutil.copy2(p,Q/'Frozen'/p.name)
 assert sha(R/'scratch/ComplexSettlementFixture.rws')=='E04E535638FB344D4C831B6D981DAC82C385FE26388DF7AA5F9E8861BF397AED'
 tree=E.parse(R/'scratch/TargetSettlement_ContextB.rws');game=tree.getroot().find('game')
 globals={c.tag:{'bytes':len(E.tostring(c)),'children':len(c),'childTags':sorted(set(x.tag for x in c))[:25]} for c in game if c.tag!='maps'}
 world=game.find('world');worlds={c.tag:{'bytes':len(E.tostring(c)),'children':len(c),'childTags':sorted(set(x.tag for x in c))[:25]} for c in world}
 write(Q/'context-static-inventory.json',{'maps':len(game.find('maps')),'globalSections':globals,'worldSections':worlds})
 print(json.dumps({'protectedFiles':len(manifest),'candidateDLL':sha(wb/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll'),'sourceCensusWorkspaceMatchesLoadedSource':sha(wb/'Source/EngineHostCensus.cs')==sha(R/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'),'contextSections':list(globals)}))
