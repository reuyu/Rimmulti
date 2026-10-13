from pathlib import Path
import json,hashlib,re
q=Path(r'C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\REMOTE-HARDEN04-20261002');root=q.parents[1];report=root/'QA_Remote_Tactical_Presentation_Hardening_04.md';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest().upper()
for r in ['Worker','GraphicalClient']:
 p=q/r/'Saves/EngineComplexFixture.rws';assert sha(p)=='ED3530BFB4B46A3092AB02300341F482B22ADD345F7E56F8328055A618DA86ED'
manifest=[]
for x in q.rglob('*'):
 if x.is_file() and not any(v in x.parts for v in ['__pycache__','obj','bin']) and x.name not in ['evidence-manifest.json','final-artifact-audit.json']:
  manifest.append(dict(path=str(x),bytes=x.stat().st_size,sha256=sha(x)))
(q/'evidence-manifest.json').write_text(json.dumps({'report':dict(path=str(report),sha256=sha(report)),'files':manifest},indent=2),encoding='utf-8')
links=re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8'));missing=[]
for v in links:
 if not Path(re.sub(r':\d+$','',v.strip('<>'))).exists():missing.append(v)
ident=json.loads((q/'identity-before.json').read_text());changes=[x['path'] for x in ident if sha(Path(x['path']))!=x['expected']];prod=json.loads((q/'production-before.json').read_text());pc=[x['path'] for x in prod if sha(Path(x['path']))!=x['expected']]
audit={'report_links':len(links),'missing_links':missing,'candidate_changes':changes,'production_changes':pc,'evidence_files':len(manifest),'fixtures_match':True,'report_bytes':report.stat().st_size}
(q/'final-artifact-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8');print(audit);assert not missing and not changes and not pc
