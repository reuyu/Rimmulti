from pathlib import Path
import hashlib,json,shutil
r=Path('.').resolve();q=r/'QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004';q.mkdir()
old=r/'QA-Tactical-Engine/SEMANTIC-AUTHORITY03-20261003'
s=(old/'setup.py').read_text(encoding='utf-8').replace('03.md','04.md').replace('gate_03','gate_04').replace('A95B324EC7DA26155ACF75E64D5B122CF987903157A24C984AAE05D4EE7972CC','8DB1D5A34DE2E3B2B6A61F078933D5828F2A99FB4E14E5694F7C3A8C80917EC9')
s=s[:s.index("if __name__=='__main__':")]
(q/'setup.py').write_text(s,encoding='utf-8')
exec(compile(s,str(q/'setup.py'),'exec'),{'__file__':str(q/'setup.py'),'__name__':'qa_setup'})
import sys;sys.path.insert(0,str(q));import setup as f
for folder in ['Frozen','Evidence','Observer','Profiles']:(q/folder).mkdir()
f.write(q/'candidate-before.json',f.candidates());f.write(q/'production-before.json',f.prod())
for n in ['TargetSettlement_Clean_ContextB.rws','TargetSettlement_Clean_ContextB.census.json','WarEconomy.WorkerBridge.PoC.dll','run_semantic_authority_gate_04.py','semantic_authority_gate_04_results.json']:shutil.copy2(r/'scratch'/n,q/'Frozen'/n)
for n in ['WorkerBridge.cs','EngineHostCensus.cs']:
 for label,root in [('Reported',r/'scratch/WorkerBridgeMod'),('Installed',f.WB)]:shutil.copy2(root/'Source'/n,q/'Frozen'/(label+'-'+n))
for ext in ['dll','pdb']:shutil.copy2(r/'scratch/WorkerBridgeMod/Source/bin/Release/net472'/('WarEconomy.WorkerBridge.PoC.'+ext),q/'Frozen'/('WarEconomy.WorkerBridge.PoC.'+ext))
shutil.copy2(r/'POC_EngineHost_Semantic_Authority_Gate_04.md',q/'Frozen/POC_EngineHost_Semantic_Authority_Gate_04.md')
shutil.copytree(old/'Observer',q/'Observer',dirs_exist_ok=True)
(q/'Frozen/Developer-A/Config').mkdir(parents=True)
shutil.copy2(old/'Frozen/Developer-A/Config/ModsConfig.xml',q/'Frozen/Developer-A/Config/ModsConfig.xml')
(q/'protocol.py').write_bytes((old/'protocol.py').read_bytes())
for name in ['WarEconomy.WorkerBridge.PoC.dll','run_semantic_authority_gate_04.py','semantic_authority_gate_04_results.json']:
 print(name,f.sha(q/'Frozen'/name))
print('Installed Root',f.WB,'DLL',f.sha(f.WB/'1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll'),'Candidate files',len(f.candidates()))
assert f.sha(q/'Frozen/WarEconomy.WorkerBridge.PoC.dll')=='8DB1D5A34DE2E3B2B6A61F078933D5828F2A99FB4E14E5694F7C3A8C80917EC9'
