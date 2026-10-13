from pathlib import Path
import json,hashlib,re,sqlite3
q=Path('QA-Transaction-Pipeline/PIPELINE01-REV4-20261004');r=q.parent.parent;b=q/'Candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
m=json.loads((r/'RELEASE_MANIFEST_PIPELINE_REV3.json').read_text(encoding='utf-8-sig'))
out={'manifestPath':str((r/'RELEASE_MANIFEST_PIPELINE_REV3.json').resolve()),'manifestSHA':sha(r/'RELEASE_MANIFEST_PIPELINE_REV3.json'),'declaredSchema':m['SchemaVersion'],'manifestChecks':{n:{'expected':v['sha256'],'actual':sha(b/n) if (b/n).exists() else None,'match':(b/n).exists() and sha(b/n)==v['sha256']} for n,v in m['Files'].items()},'actualFiles':{str(p.relative_to(b)):{'sha':sha(p),'bytes':p.stat().st_size} for p in b.rglob('*') if p.is_file()},'e1SHA':sha(r/'scratch/pipeline_e1_rev4_results.json'),'reportSHA':sha(r/'Production_Transaction_Pipeline_Slice_01_REV4.md'),'sourceHashes':{str(p.relative_to(q/'FrozenSource')):sha(p) for p in (q/'FrozenSource').rglob('*') if p.suffix in ['.cs','.csproj']},'deps':json.loads((b/'WarEconomy.Server.deps.json').read_text())['libraries']}
(q/'Evidence/provenance-complete.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print('Manifest mismatches',[(n,v['actual']) for n,v in out['manifestChecks'].items() if not v['match']]);print('EXE PDB E1',[out['actualFiles'][n]['sha'] for n in ['WarEconomy.Server.exe','WarEconomy.Server.pdb']],out['e1SHA'])
# Independently reproduce the source-defined descriptor from SQLite introspection, without calling candidate checker.
c=sqlite3.connect(q/'DBs/schema-base.db');lines=[f"APP:{c.execute('pragma application_id').fetchone()[0]};VER:{c.execute('pragma user_version').fetchone()[0]}"]
def norm(sql):
 parts=re.split("('(?:''|[^'])*')",sql)
 return ''.join(p if i%2 else re.sub(r'\s+',' ',p.upper()) for i,p in enumerate(parts)).strip()
tables=c.execute("select name,sql from sqlite_master where type='table' and name not like 'sqlite_%' order by name").fetchall()
for t,ddl in tables:
 lines.append('TABLE:'+t)
 for row in c.execute('pragma table_info('+t+')'):lines.append(f'  COL:{row[1]}|{row[2].upper()}|{row[3]}|{row[5]}')
 lines+=sorted(f'  FK:{a}:{z}:{fr}->{to}({col})|UPD:{u}|DEL:{d}' for a,z,to,fr,col,u,d,mat in c.execute('pragma foreign_key_list('+t+')'))
 for _,name,unique,origin,partial in sorted(c.execute('pragma index_list('+t+')').fetchall(),key=lambda r:r[1]):
  cols=','.join(str(r[2]) for r in c.execute('pragma index_info('+name+')'));sql=c.execute('select sql from sqlite_master where name=?',(name,)).fetchone()[0];where=''
  if sql and ' WHERE ' in sql.upper():where='|'+norm(sql[sql.upper().index(' WHERE '):].strip())
  lines.append(f'  IDX:{name}|UNIQ:{unique}|ORIGIN:{origin}|PARTIAL:{partial}|COLS:{cols}'+where)
for name,t,sql in c.execute("select name,tbl_name,sql from sqlite_master where type='trigger' order by name"):lines.append(f'TRIGGER:{name}|ON:{t}|SQL:{norm(sql)}')
for t,ddl in tables:
 for match in re.finditer(r'check\s*\((.*?)\)',ddl,re.I):lines.append('CHECK:'+t+'|'+norm(match.group(1)))
desc='\r\n'.join(lines)+'\r\nACTIVE_INCARNATIONS:'+str(c.execute('select count(*) from StoreIncarnations where IsActive=1').fetchone()[0]);h=hashlib.sha256(desc.encode()).hexdigest().upper();(q/'Evidence/schema-independent-descriptor.txt').write_bytes(desc.encode());(q/'Evidence/schema-independent-hash.json').write_text(json.dumps({'hash':h,'matchesExpected':h=='3DD745591298C7C7BB84C889C98D0B2B0A3EF0E5145F719D6973DEFA4BBB5A73'}));print('Independent schema signature',h)
