from pathlib import Path
import hashlib,json,shutil,re,xml.etree.ElementTree as E
Q=Path(__file__).resolve().parent;R=Q.parent.parent
ENGINE=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld')
WB=(ENGINE/'Mods/WarEconomy.WorkerBridge.PoC').resolve()
PROBE=R/'QA-Tactical-Engine/ENGINE02-20261002/ProbeMod'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def prod():return {str(p):{'sha':sha(p),'bytes':p.stat().st_size} for p in (R/'WarEconomyMod').rglob('*') if p.is_file()}
def candidates():
 paths=list((R/'scratch/WorkerBridgeMod').rglob('*'))+list(WB.rglob('*'))
 paths+=list((R/'scratch/CorruptedFixtures').rglob('*'))+list((R/'scratch/Profiles').rglob('*'))
 paths+=list(R.glob('POC_EngineHost_Semantic_Gate_02.md'))
 paths +=[R/'scratch'/n for n in ['CleanSettlementFixture.rws','TargetSettlement_Clean_ContextB.rws','TargetSettlement_Clean_ContextB.census.json','WarEconomy.WorkerBridge.PoC.dll','run_semantic_gate_02.py','census_oracle.py','semantic_gate_02_results.json','generate_clean_positive_fixture.py','generate_corruption_battery_v2.py']]
 paths +=list((R/'WarEconomyMod/1.6').rglob('*'))+list((R/'WarEconomyMod/About').rglob('*'))
 paths+=list(PROBE.rglob('*'))+list((ENGINE/'Mods/Harmony').rglob('*'))
 paths +=[ENGINE/'RimWorldWin64.exe',ENGINE/'RimWorldWin64_Data/Managed/Assembly-CSharp.dll']
 return {str(p):{'sha':sha(p),'bytes':p.stat().st_size} for p in paths if p.is_file() and p.name!='QA.SemanticGate.Observer.dll'}
if __name__=='__main__':
 assert not (Q/'candidate-before.json').exists()
 write(Q/'candidate-before.json',candidates());write(Q/'production-before.json',prod())
 for folder in ['Frozen','Evidence','Observer','Profiles']: (Q/folder).mkdir(exist_ok=True)
 for n in ['CleanSettlementFixture.rws','TargetSettlement_Clean_ContextB.rws','TargetSettlement_Clean_ContextB.census.json','WarEconomy.WorkerBridge.PoC.dll','run_semantic_gate_02.py','census_oracle.py','semantic_gate_02_results.json']:
  shutil.copy2(R/'scratch'/n,Q/'Frozen'/n)
 for n in ['WorkerBridge.cs','EngineHostCensus.cs']:
  shutil.copy2(WB/'Source'/n,Q/'Frozen'/('Loaded-'+n));shutil.copy2(R/'scratch/WorkerBridgeMod/Source'/n,Q/'Frozen'/('Reported-'+n))
 for n in ['A','B','C']:
  for p in (R/f'scratch/Profiles/Profile_{n}').rglob('*'):
   if p.is_file() and (p.suffix in ['.rws','.json'] or p.name=='ModsConfig.xml'):
    d=Q/'Frozen'/('Developer-'+n)/p.relative_to(R/f'scratch/Profiles/Profile_{n}');d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
 report=(R/'POC_EngineHost_Semantic_Gate_02.md').read_text(encoding='utf-8')
 write(Q/'Evidence/claimed-hashes.json',re.findall(r'[A-F0-9]{64}',report))
 shutil.copy2(R/'POC_EngineHost_Semantic_Gate_02.md',Q/'Frozen/POC_EngineHost_Semantic_Gate_02.md')
 old=R/'QA-Tactical-Engine/HOST-ROUNDTRIP01-20261003/Observer'
 code=(old/'Observer.cs').read_text(encoding='utf-8').replace('QARoundTrip','QASemantic').replace('rtqaport','sgqaport').replace('QA.RoundTrip.Observer','QA.SemanticGate.Observer')
 code=code.replace('else if(p[0]=="JOB")value=StartJob();','else if(p[0]=="MUTATE")value=Mutations.Apply(p[1]);else if(p[0]=="ARM")value=Mutations.Arm(p[1]);else if(p[0]=="RESERVATIONS")value=Mutations.Reservations();else if(p[0]=="META")value=Mutations.Meta();else if(p[0]=="JOB")value=StartJob();')
 code=code.replace('var g=new GameObject','new HarmonyLib.Harmony("qa.semanticgate.faults").PatchAll();var g=new GameObject')
 (Q/'Observer/Observer.cs').write_text(code,encoding='utf-8')
 proj=(old/'Observer.csproj').read_text(encoding='utf-8').replace('QA.RoundTrip.Observer','QA.SemanticGate.Observer')
 proj=proj.replace('</ItemGroup>','<Reference Include="0Harmony"><HintPath>'+str(ENGINE/'Mods/Harmony/Current/Assemblies/0Harmony.dll')+'</HintPath><Private>False</Private></Reference></ItemGroup>')
 (Q/'Observer/Observer.csproj').write_text(proj,encoding='utf-8')
 print(json.dumps({'protectedProduction':len(prod()),'protectedCandidate':len(candidates()),'workerSHA':sha(WB/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll'),'sourceMismatch':sha(WB/'Source/EngineHostCensus.cs')!=sha(R/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs')}))
