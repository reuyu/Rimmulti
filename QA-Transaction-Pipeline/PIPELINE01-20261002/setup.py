from pathlib import Path
import hashlib,json,re,shutil,subprocess
ROOT=Path(r'C:\Users\user\Desktop\RimMulti')
QA=Path(__file__).parent
PROD=ROOT/'WarEconomyMod'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
files=[p for p in PROD.rglob('*') if p.is_file() and p.suffix.lower() in ('.cs','.csproj','.dll','.exe','.json')]
manifest={str(p.relative_to(ROOT)): {'sha256':sha(p),'bytes':p.stat().st_size} for p in files}
(QA/'freeze-before.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
report=(ROOT/'Production_Transaction_Pipeline_Slice_01.md').read_text(encoding='utf-8-sig')
matches=[]
for line in report.splitlines():
 if re.search(r'[0-9A-F]{64}',line) and '|' in line:
  matches.append(line)
(QA/'developer-hash-rows.txt').write_text('\n'.join(matches),encoding='utf-8')
for part in ('Server','Common'):
 shutil.copytree(PROD/'Source'/part,QA/'BuildCopy'/'Source'/part,ignore=shutil.ignore_patterns('bin','obj'),dirs_exist_ok=True)
shutil.copytree(PROD/'Source'/'Server'/'bin'/'Debug'/'net8.0',QA/'FrozenRuntime',ignore=shutil.ignore_patterns('*.db','*.db-wal','*.db-shm'),dirs_exist_ok=True)
assets=json.loads((PROD/'Source'/'Server'/'obj'/'project.assets.json').read_text(encoding='utf-8-sig'))
(QA/'package-versions.json').write_text(json.dumps(assets['libraries'],indent=2),encoding='utf-8')
print(json.dumps({'protected_files':len(manifest),'developer_manifest_rows':len(matches),'server_sha':sha(QA/'FrozenRuntime'/'WarEconomy.Server.dll')}))
