from pathlib import Path
import json,xml.etree.ElementTree as E,collections,difflib
Q=Path(__file__).parent;D=Q/'Evidence';tree=E.parse(D/'A_TargetArtifact.rws');g=tree.getroot().find('game');m=g.find('maps')[0]
def thing(id):return next(t for t in m.find('things') if t.findtext('id')==id)
p=thing('Human302');a=thing('Boomrat3383');work=next(t for t in m.find('things') if t.findtext('def')=='TableSculpting')
out={'pawnSkills':E.tostring(p.find('skills'),encoding='unicode'),'health':E.tostring(p.find('healthTracker'),encoding='unicode')[:8500],'ownership':E.tostring(p.find('ownership'),encoding='unicode'),'animalSettings':E.tostring(a.find('playerSettings'),encoding='unicode'),'bills':E.tostring(work.find('billStack'),encoding='unicode'),'zones':E.tostring(m.find('zoneManager'),encoding='unicode'),'designations':E.tostring(m.find('designationManager'),encoding='unicode'),'conditions':E.tostring(m.find('gameConditionManager'),encoding='unicode'),'environmentExamples':{t.findtext('id'):E.tostring(t,encoding='unicode')[:1200] for t in m.find('things') if t.findtext('def') in ['Fire','Plant_Rice','Filth_Dirt']},'mapSections':[c.tag for c in m]}
(D/'input-inspection.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8');print(json.dumps(out,ensure_ascii=False)[:14000])
for name in ['A-to-B.diff.json','B-to-C.diff.json']:
 if (D/name).exists():
  x=json.loads((D/name).read_text(encoding='utf-8'));print(name,'total',len(x),json.dumps(x[:12],ensure_ascii=False))
f=Q/'Frozen/EngineHostCensus.cs';old=Q.parent.parent/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';diff=list(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(),f.read_text(encoding='utf-8-sig').splitlines()))
(D/'census-source-lineage.diff.txt').write_text('\n'.join(diff),encoding='utf-8');print('SOURCE LINEAGE DIFF',diff[:16])
