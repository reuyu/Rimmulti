from pathlib import Path
import json,re,hashlib
qa=Path(__file__).parent;root=qa.parent.parent
r=json.loads((qa/'Evidence/results.json').read_text(encoding='utf-8'))
report=root/'QA_Production_Transaction_Pipeline_01_REV1.md';s=report.read_text(encoding='utf-8')
missing=[]
for dest in re.findall(r'\]\(([^)]+)\)',s):
 path=re.sub(r':\d+$','',dest)
 if not Path(path).exists():missing.append(dest)
assert not missing,missing
assert all(f'QA-PIPELINE-{i:03}' in s for i in range(1,19))
before=json.loads((qa/'freeze-before.json').read_text(encoding='utf-8'))
after={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest().upper() for p in (root/'WarEconomyMod').rglob('*') if p.is_file() and p.suffix.lower() in ('.cs','.csproj','.dll','.exe','.json','.pdb')}
changes=[k for k in set(before)|set(after) if before.get(k,{}).get('sha256')!=after.get(k)]
assert not changes,changes
print('Links validated; QA IDs 001..018 present; protected Production files:',len(after),'changes:',len(changes))
print('Runtime copied dependency mismatches/missing:',json.dumps([x for x in r['runtime-copy-identity'] if not x['sameBytes']],ensure_ascii=False))
print('CAS:',r['different-id-race']['summary'],r['same-id-race']['summary'])
print('Delimiter statuses:',r['delimiter-collision']['first']['result']['Status'],r['delimiter-collision']['changedEnvelope']['result']['Status'])
for k in ['schema-no-state-check','schema-no-fk','schema-multiple-active','startup-65-persistent','normal-fresh']:
 x=r[k];print(k,json.dumps({a:b for a,b in x.items() if a not in ('db','after','before','effects','log')},ensure_ascii=False)[:1800])
