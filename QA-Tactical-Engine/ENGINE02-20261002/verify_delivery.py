import json,pathlib,re,hashlib,psutil
R=pathlib.Path(__file__).resolve().parent;workspace=R.parents[1];report=workspace/'QA_POC_TAC_ENGINE_02_Review.md'
s=report.read_text(encoding='utf-8');canonical=set(re.findall(r'^##\s+((?:FR|BR|NFR|CON|CFG)-\d+)',(workspace/'요구사항_명세서.md').read_text(encoding='utf-8'),re.M))
ids=set(re.findall(r'SRS-((?:FR|BR|NFR|CON|CFG)-\d+)',s));links=re.findall(r'\]\(<([^>]+)>\)',s)
missing=[x for x in links if not pathlib.Path(re.sub(r':\d+$','',x)).exists()]
before=json.loads((R/'protected-before.json').read_text(encoding='utf-8-sig'));after=[]
for x in before:
 h=hashlib.sha256(pathlib.Path(x['Path']).read_bytes()).hexdigest().upper();after.append({'Path':x['Path'],'Before':x['Hash'],'After':h,'Unchanged':h==x['Hash']})
(R/'protected-after.json').write_text(json.dumps(after,ensure_ascii=False,indent=2),encoding='utf-8')
owned=[]
for launch in R.glob('*/launch.json'):
 data=json.loads(launch.read_text(encoding='utf-8'));pid=data['pid'];alive=False
 try:
  p=psutil.Process(pid);alive=p.name().lower()=='rimworldwin64.exe' and abs(p.create_time()-data['start'])<10
 except psutil.NoSuchProcess:pass
 owned.append({'profile':launch.parent.name,'pid':pid,'owned_worker_alive':alive})
out={'numbered_sections':re.findall(r'^## (\d+)\.',s,re.M),'canonical_srs_ids_reviewed':sorted(ids),'unknown_srs_ids':sorted(ids-canonical),'missing_artifact_links':missing,'protected_inputs':len(after),'changed_protected_inputs':[x['Path'] for x in after if not x['Unchanged']],'process_cleanup':owned,'qa_probe_junction_absent':not pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\QA-Codex-Engine02-Probe').exists(),'japanese_kana_found':bool(re.search(r'[\u3040-\u30ff]',s))}
assert out['numbered_sections']==[str(x) for x in range(1,18)]
assert not out['unknown_srs_ids'] and not missing and not out['changed_protected_inputs']
assert not any(x['owned_worker_alive'] for x in owned) and out['qa_probe_junction_absent'] and not out['japanese_kana_found']
(R/'delivery-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
manifest=[]
for p in R.rglob('*'):
 if p.is_file() and not any(x in ('obj','bin','__pycache__') for x in p.parts) and p.name!='artifact-manifest.json':manifest.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper()})
manifest.append({'path':str(report),'bytes':report.stat().st_size,'sha256':hashlib.sha256(report.read_bytes()).hexdigest().upper()})
(R/'artifact-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'validation':'PASS','sections':17,'protected_unchanged':len(after),'workers_terminated':len(owned),'linked_artifacts_found':len(links),'manifest_artifacts':len(manifest),'report_bytes':report.stat().st_size},indent=2))
