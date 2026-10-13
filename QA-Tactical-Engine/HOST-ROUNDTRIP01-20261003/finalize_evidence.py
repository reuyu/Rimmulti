from pathlib import Path
import json,hashlib,shutil,collections
import run_roundtrip as q
def manifest(paths):
 return {str(p):{'sha256':q.sha(p),'bytes':p.stat().st_size} for p in paths}
before=json.loads((q.Q/'production-before.json').read_text(encoding='utf-8'))
after=manifest(sorted((q.R/'WarEconomyMod').rglob('*')) if False else sorted(p for p in (q.R/'WarEconomyMod').rglob('*') if p.is_file()))
q.write(q.Q/'production-after.json',after)
changes=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
cb=json.loads((q.Q/'candidate-before.json').read_text(encoding='utf-8'))
ca=manifest([Path(p) for p in cb if Path(p).is_file()]);q.write(q.Q/'candidate-after.json',ca)
cc=[p for p in set(cb)|set(ca) if cb.get(p)!=ca.get(p)]
aLog=Path(r'C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch\PoC_RoundTrip\player.log')
shutil.copy2(aLog,q.DATA/'A_original_player.log')
snaps={n:json.loads((q.DATA/(n+'.snapshot.json')).read_text(encoding='utf-8')) for n in ['A-baseline','B-before','B-posttick','C-reloaded','D-job-reload','D-job-after40','clock-before','clock-target0-after300','clock-target1-after300']}
stats={}
for n,s in snaps.items():
 stats[n]={'pid':s['pid'],'ticksGame':s['ticksGame'],'ticksAbs':s['ticksAbs'],'maps':[]}
 for m in s['maps']:
  pawns=[(k,v) for k,v in m['entities'].items() if k in ['Human302','Human100302']]
  stats[n]['maps'].append({'mapId':m['mapId'],'pawns':[{'id':k,'position':v['pos'],'bio':v['pawn']['bio'],'chrono':v['pawn']['chrono'],'food':v['pawn']['food'],'rest':v['pawn']['rest'],'job':v['pawn']['job'].get('def')} for k,v in pawns]})
env={}
for x,y in [('A-baseline','B-before'),('B-posttick','C-reloaded')]:
 a=q.normalize(snaps[x]);b=q.normalize(snaps[y]);ds=q.diff(a,b)
 env[x+'->'+y]={'rawDifferences':len(ds),'environmentDifferences':len(q.diff(a['environment'],b['environment'])),'custodyIdentitiesEqual':set(a['custody'])==set(b['custody']),'custodyCount':len(a['custody']),'diffPaths':collections.Counter(d['path'].rsplit('.',1)[-1] for d in ds)}
qaFiles=[p for p in q.Q.rglob('*') if p.is_file() and p.suffix in ['.py','.cs','.csproj','.dll','.xml'] and ('obj' not in p.parts) and ('Profiles' not in p.parts)]
q.write(q.Q/'qa-harness-manifest.json',manifest(sorted(qaFiles)))
q.write(q.DATA/'final-integrity-and-clock.json',{'productionBeforeCount':len(before),'productionAfterCount':len(after),'productionChanges':changes,'candidateChanges':cc,'observerRemoved':not q.MOD.exists(),'stats':stats,'environmentComparisons':env,'AlogSHA':q.sha(q.DATA/'A_original_player.log')})
print(json.dumps({'productionCount':len(after),'productionChanges':changes,'candidateChanges':cc,'observerRemoved':not q.MOD.exists(),'stats':stats,'environmentComparisons':env},ensure_ascii=False,indent=2))
