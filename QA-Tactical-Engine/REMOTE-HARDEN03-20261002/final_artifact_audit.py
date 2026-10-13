from pathlib import Path
from datetime import datetime, timezone
import json,hashlib,re,xml.etree.ElementTree as ET
from PIL import Image
Q=Path(__file__).resolve().parent
R=Q.parent.parent/'QA_Remote_Tactical_Presentation_Hardening_03.md'
def read(n):return json.loads((Q/n).read_text(encoding='utf-8-sig'))
def sha(p):
 with Path(p).open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest().upper()
checks=[]
for category,name in [('frozen','identity-before.json'),('production','production-before.json')]:
 for x in read(name):
  entry=dict(category=category,path=x['path'],expected=x['expected'],actual=sha(x['path']))
  entry['match']=entry['expected']==entry['actual'];checks.append(entry)
assert all(x['match'] for x in checks)
sourcecopies=[]
for x in read('identity-before.json'):
 if x['source'].startswith('QA arrival'):
  p=Path(x['path']);relative=Path(*p.parts[p.parts.index('Source')+1:]);cp=Q/'Reviewed/Source'/relative
  sourcecopies.append(dict(path=str(p),copy=str(cp),match=sha(p)==sha(cp)))
assert all(x['match'] for x in sourcecopies)
fixture=ET.parse(Q/'Worker/Saves/EngineComplexFixture.rws').getroot()
declared=[x.text.lower() for x in fixture.find('meta/modIds')]
profiles=[]
for role in ['Worker','GraphicalClient']:
 cfg=Q/role/'Config/ModsConfig.xml';active=[x.text.lower() for x in ET.parse(cfg).getroot().find('activeMods')]
 profiles.append(dict(role=role,active_mods=active,fixture_declared_mods=declared,missing_declared_dependencies=sorted(set(declared)-set(active)),fixture_sha256=sha(Q/role/'Saves/EngineComplexFixture.rws'),config_sha256=sha(cfg),reviewed_config_sha256=sha(Q/'Reviewed'/(role+'-ModsConfig.xml'))))
assert all(not p['missing_declared_dependencies'] for p in profiles)
(Q/'profile-manifest.json').write_text(json.dumps(profiles,indent=2),encoding='utf-8')
text=R.read_text(encoding='utf-8-sig')
links=re.findall(r'\]\((C:/[^)]+)\)',text)
missing=[x for x in links if not Path(x).exists()]
assert all(Path(x).name in {'evidence-manifest.json','final-artifact-audit.json'} for x in missing)
assert not re.search(r'[\u3040-\u30ff]',text)
frames={}
for n in ['own-drafted.jpg','operational-move.jpg','stale-render-after-arrival.jpg']:
 with Image.open(Q/n) as im:frames[n]=dict(format=im.format,width=im.width,height=im.height,sha256=sha(Q/n))
audit=dict(utc=datetime.now(timezone.utc).isoformat(),checks=checks,copied_source=sourcecopies,report_links=len(links),missing_links=missing,frames=frames)
(Q/'final-artifact-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
files=[]
for p in sorted(Q.rglob('*')):
 if not p.is_file() or p.name=='evidence-manifest.json' or any(x in {'bin','obj','__pycache__'} for x in p.relative_to(Q).parts):continue
 files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
manifest=dict(utc=datetime.now(timezone.utc).isoformat(),report=dict(path=str(R),bytes=R.stat().st_size,sha256=sha(R)),files=files)
(Q/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(frozen=18,production=62,copied_source=len(sourcecopies),links=len(links),missing_links=missing,files=len(files),report_sha256=manifest['report']['sha256'],profile_dependencies_verified=True)))
