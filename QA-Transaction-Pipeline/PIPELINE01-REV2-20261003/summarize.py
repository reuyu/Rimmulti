from pathlib import Path
import json,collections,hashlib
import setup as f
Q=f.Q;E=Q/'Evidence';r=json.loads((E/'results.json').read_text(encoding='utf-8'))
before=json.loads((Q/'freeze-before.json').read_text(encoding='utf-8'));rawold=json.loads((Q.parent/'PIPELINE01-REV1-20261003/freeze-before.json').read_text(encoding='utf-8'))
old={str((f.R/p).resolve()) if not Path(p).is_absolute() else p:v for p,v in rawold.items()}
changed={p:v for p,v in before.items() if ('\\Source\\Server\\' in p or '\\Source\\Common\\' in p) and p.endswith(('.cs','.csproj')) and old.get(p)!=v and '\\bin\\' not in p and '\\obj\\' not in p}
removed={p:v for p,v in old.items() if p not in before and p.endswith(('.cs','.csproj')) and '\\Source\\Server\\' in p and '\\bin\\' not in p and '\\obj\\' not in p}
source={p:v for p,v in before.items() if p.endswith(('.cs','.csproj')) and '\\obj\\' not in p and '\\bin\\' not in p and ('\\Source\\Server\\Pipeline\\' in p or '\\Source\\Common\\' in p or p.endswith('\\Source\\Server\\Program.cs'))}
f.write(Q/'source-provenance.json',{'changedVsREV1':changed,'removedVsREV1':removed,'allRelevant':source})
deps=json.loads((Q/'Candidate/WarEconomy.Server.deps.json').read_text(encoding='utf-8'));f.write(Q/'package-versions.json',deps['libraries'])
meta=r['metadata']['rows'][-1]
schema={k:v for k,v in r.items() if k.startswith('schema-') and k.endswith('-summary')}
kill={k:{'before':{n:len(rows) for n,rows in v['durableBeforeRetry']['tables'].items()},'after':{n:len(rows) for n,rows in v['afterRetry']['tables'].items()}} for k,v in r.items() if k.startswith('kill-boundary-')}
summary={'candidateSHA':meta['sha'],'mvid':meta['mvid'],'exeSHA':f.sha(Q/'Candidate/WarEconomy.Server.exe'),'nativeSqliteSHA':f.sha(Q/'Candidate/runtimes/win-x64/native/e_sqlite3.dll'),'commonSHA':f.sha(Q/'Candidate/WarEconomy.Common.dll'),'changedProductionSources':changed,'removedProductionSources':removed,'schemas':schema,'schemaCount':len(schema),'schemaFalseReady':sum(v['ready'] for v in schema.values()),'kills':kill,'normal':{k:{a:v.get(a) for a in ['pid','exit','pipelineReady','listen','canonicalUnchanged','tables']} for k,v in r.items() if k.startswith('normal-')},'queue':{k:r[k]['rows'] for k in ['bounded-shutdown','queue-timeout-backpressure','queue-native-lock']}}
f.write(E/'summary.json',summary)
qa={str(p.relative_to(Q)):{'sha256':f.sha(p),'bytes':p.stat().st_size} for p in Q.rglob('*') if p.is_file() and p.suffix in ['.cs','.csproj','.py','.dll','.exe'] and 'obj' not in p.parts and 'Normal' not in p.parts and 'FrozenSource' not in p.parts}
f.write(Q/'qa-harness-manifest.json',qa)
after=f.tree();f.write(Q/'freeze-after.json',after);changes=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)];f.write(E/'final-integrity.json',{'productionBefore':len(before),'productionAfter':len(after),'changes':changes,'copiedServerMatchesProduction':f.sha(Q/'Candidate/WarEconomy.Server.dll')==f.sha(f.BIN/'WarEconomy.Server.dll'),'loadedServerMatchesCandidate':meta['sha']==f.sha(Q/'Candidate/WarEconomy.Server.dll')})
print(json.dumps({'changedSources':changed,'removedSources':list(removed),'exeSHA':summary['exeSHA'],'nativeSHA':summary['nativeSqliteSHA'],'commonSHA':summary['commonSHA'],'kills':kill,'schemas':len(schema),'falseReady':summary['schemaFalseReady'],'freezeChanges':changes},indent=2))
