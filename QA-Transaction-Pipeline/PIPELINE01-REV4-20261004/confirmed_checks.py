from pathlib import Path
p=Path(__file__).with_name('deep_checks.py');s=p.read_text(encoding='utf-8').split('\ntry:\n q.RESULTS')[0]
s=s.replace("  q.execute(base,'seed-'+scope+'-abort',name=scope+'AB',scope=scope,expected=0)\n",'').replace('deep-graph','confirmed-graph')
exec(compile(s,str(p),'exec'))
q.RESULTS={}
def rec(k,v):
 q.RESULTS[k]=v;q.f.write(q.E/'confirmed-results.json',q.RESULTS);print(k,str(v)[:220],flush=True)
q.record=rec
q.RESULTS.update(json.loads((q.E/'confirmed-results.json').read_text(encoding='utf-8')));q.check();q.run('lifetime-extended',q.fresh('service-observed'),'service-observed',timeout=35);q.run('startup',q.D/'service-observed.db','service-observed-restart')
# Actual admitted control/separator Principal/Operation values, with safe QA request filenames.
db=q.fresh('derivative-controls');inc=q.truth(db)['tables']['StoreIncarnations'][0][0];requests=[]
for i,t in enumerate([('A:B','C'),('A','B:C'),('A\0','B'),('A','\0B'),('A\r\n','B'),('A','\r\nB'),('A\u2028','B'),('A','\u2028B'),('A\x1f','B'),('A','\x1fB')]):
 requests.append(dict(PrincipalId=t[0],OperationId=t[1],ProbeScopeId='CTRL'+str(i),ExpectedProbeRevision=0,StoreIncarnationId=inc,ContentProfileFingerprint='PROFILE',PayloadJson='{}'))
f=q.E/'derivative-controls.requests.json';q.f.write(f,requests+requests);q.run('batch',db,'derivative-controls',request=f);q.record('derivative-controls-truth',q.truth(db));q.run('startup',db,'derivative-controls-ready')
# Query UNKNOWN using original caller-retained envelope and exact profile, not a newly generated operation ID.
for label,scope,op in [('deep-shutdown-after-cas','BOUNDARY','BOUNDARY'),('deep-shutdown-native-wal','BOUNDARY','BOUNDARY'),('deep-lock','QUEUE','Q0')]:
 db=q.D/(label+'.db');q.run('historical',db,'identity-query-'+label,principal='P',op=op);q.execute(db,'identity-retry-'+label,scope=scope,name=op,ContentProfileFingerprint='PROBE_PROFILE_V1')
q.check()
