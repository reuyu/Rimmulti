from pathlib import Path
import hashlib,json,shutil
Q=Path(__file__).resolve().parent;R=Q.parent.parent;PROD=R/'WarEconomyMod';BIN=PROD/'Source/Server/bin/Release/net8.0'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def tree(): return {str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(PROD.rglob('*')) if p.is_file()}
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':
 assert not (Q/'freeze-before.json').exists();write(Q/'freeze-before.json',tree())
 (Q/'Candidate').mkdir();(Q/'Evidence').mkdir();(Q/'DBs').mkdir();(Q/'FrozenSource').mkdir()
 for p in BIN.rglob('*'):
  if p.is_file() and p.suffix not in ['.db','.db-wal','.db-shm']:
   dest=Q/'Candidate'/p.relative_to(BIN);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 for folder in ['Server','Common']:
  for p in (PROD/'Source'/folder).rglob('*'):
   if p.is_file() and p.suffix in ['.cs','.csproj'] and not any(x in p.parts for x in ['bin','obj']):
    dest=Q/'FrozenSource'/p.relative_to(PROD/'Source');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 for n in ['Production_Transaction_Pipeline_Slice_01_REV2.md','QA_Production_Transaction_Pipeline_01_REV1.md','QA_Production_Transaction_Pipeline_01.md']:
  shutil.copy2(R/n,Q/'FrozenSource'/n)
 write(Q/'copy-manifest.json',{str(p.relative_to(Q)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in Q.rglob('*') if p.is_file() and 'freeze-before' not in p.name})
 print('Frozen',len(tree()),'production files; Server DLL',sha(Q/'Candidate/WarEconomy.Server.dll'))
