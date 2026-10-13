from pathlib import Path
import json,hashlib,re,shutil
ROOT=Path(r'C:\Users\user\Desktop\RimMulti');QA=Path(__file__).parent
PROD=ROOT/'WarEconomyMod'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
files=[p for p in PROD.rglob('*') if p.is_file() and p.suffix.lower() in ('.cs','.csproj','.dll','.exe','.json','.pdb')]
(QA/'freeze-before.json').write_text(json.dumps({str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files},indent=2),encoding='utf-8')
report=(ROOT/'Production_Transaction_Pipeline_Slice_01_REV1.md').read_text(encoding='utf-8-sig')
verified=[]
for line in report.splitlines():
 if not ('| `WarEconomyMod/' in line and re.search(r'[A-F0-9]{64}',line)):continue
 path=line.split('`')[1];expected=re.search(r'[A-F0-9]{64}',line).group();actual=sha(ROOT/path)
 verified.append({'path':path,'expected':expected,'actual':actual,'match':actual==expected})
(QA/'source-provenance.json').write_text(json.dumps(verified,indent=2),encoding='utf-8')
assert all(x['match'] for x in verified)
bin=PROD/'Source/Server/bin/Release/net8.0';expected='288AADC7C8B88A3492583797F2D4537F73EC88362723671E0222BF0AEDB3ED8C'
assert sha(bin/'WarEconomy.Server.dll')==expected
shutil.copytree(bin,QA/'FrozenRelease',ignore=shutil.ignore_patterns('*.db','*.db-wal','*.db-shm'),dirs_exist_ok=True)
assets=json.loads((PROD/'Source/Server/obj/project.assets.json').read_text(encoding='utf-8-sig'))
(QA/'package-versions.json').write_text(json.dumps(assets['libraries'],indent=2),encoding='utf-8')
print(json.dumps({'sourceManifest':len(verified),'matches':sum(x['match'] for x in verified),'protectedFiles':len(files),'releaseDll':sha(bin/'WarEconomy.Server.dll')}))
