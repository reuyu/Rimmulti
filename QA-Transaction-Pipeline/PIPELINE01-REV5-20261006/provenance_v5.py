from pathlib import Path
import json,hashlib,shutil
q=Path('QA-Transaction-Pipeline/PIPELINE01-REV5-20261006').resolve();r=q.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper();mf=r/'RELEASE_MANIFEST_PIPELINE_REV5.json';m=json.loads(mf.read_text(encoding='utf-8-sig'))
checks={}
for section in ['BinaryArtifacts','ModifiedSourceFiles']:
 for name,item in m[section].items():checks[section+'/'+name]={'path':item['RelativePath'],'expected':item['Sha256'],'actual':sha(r/item['RelativePath']),'match':sha(r/item['RelativePath'])==item['Sha256']}
x=m['E1Results'];checks['E1']={'path':x['RelativePath'],'expected':x['Sha256'],'actual':sha(r/x['RelativePath']),'match':sha(r/x['RelativePath'])==x['Sha256']}
meta=json.loads((q/'Evidence/runtime-metadata.json').read_text(encoding='utf-8-sig'));assert meta['sha']==m['BinaryArtifacts']['WarEconomy.Server.dll']['Sha256'];assert meta['mvid']==m['BinaryArtifacts']['WarEconomy.Server.dll']['Mvid']
lineage={f:json.loads((q/'Evidence'/f).read_text(encoding='utf-8-sig')) for f in ['server-pdb-lineage.json','common-pdb-lineage.json']}
obj={'manifest':{'filename':mf.name,'sha':sha(mf),'allEntriesMatch':all(x['match'] for x in checks.values()),'contents':m,'checks':checks},'runtime':meta,'pdbCounts':{n:{'docs':len(x['documents']),'matching':sum(d['match'] for d in x['documents']),'codeview':x['codeviewGuid'],'pdb':x['pdbGuid']} for n,x in lineage.items()},'package':{str(p.relative_to(q/'Candidate')):{'sha':sha(p),'bytes':p.stat().st_size} for p in (q/'Candidate').rglob('*') if p.is_file()},'libs':json.loads((q/'Candidate/WarEconomy.Server.deps.json').read_text())['libraries']}
(q/'Evidence/provenance-complete.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8');print('Manifest',sha(mf),obj['manifest']['allEntriesMatch'],'PDB',obj['pdbCounts'])
# independent descriptor from prior QA source, use current V6 data/constant
s=(r/'QA-Transaction-Pipeline/PIPELINE01-REV4-20261004/provenance_checks.py').read_text(encoding='utf-8-sig');s=s[s.index('# Independently reproduce'):].replace('3DD745591298C7C7BB84C889C98D0B2B0A3EF0E5145F719D6973DEFA4BBB5A73','64BDB62037D70303D7F2AE15D39FC7E7DFD9F01021B5E0AA0709A51FA507E721')
import sqlite3,re
exec(compile(s,'QA-independent-schema','exec'))
for version,folder in [(4,'PIPELINE01-REV3-20261003'),(5,'PIPELINE01-REV4-20261004')]:
 src=r/'QA-Transaction-Pipeline'/folder/'DBs/identity.db';dest=q/'DBs'/('legacy-real-'+str(version)+'.db')
 with sqlite3.connect(src) as a,sqlite3.connect(dest) as b:a.backup(b)
# freeze E1 source evidence without executing developer assertions
for name in ['Program.cs','E1_Rev5_Runner.csproj']:
 p=r/'scratch/E1_Rev5_Runner'/name;d=q/'FrozenSource/A_E1_Runner'/name;d.parent.mkdir(exist_ok=True);shutil.copy2(p,d)
