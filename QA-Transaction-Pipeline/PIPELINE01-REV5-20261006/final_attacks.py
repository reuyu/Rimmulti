import run_checks as q
import json,time,shutil,sqlite3
q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'final-attacks-results.json',q.RESULTS);print(k,str(v)[:220],flush=True)
q.record=record
# Cross-principal reparenting between two existing valid composite keys (not merely UNKNOWN orphans).
base=q.D/'same-parent-scope.db'
for table in ['ProbeRevisionHistory','AuditRecords','CommitReceipts','PublicationEvents']:
 db=q.clone(base,q.D/('composite-swap-'+table+'.db'))
 with q.conn(db) as c:c.execute("update "+table+" set PrincipalId=case PrincipalId when 'P1' then 'P2' else 'P1' end")
 with q.conn(db) as c:fk=list(c.execute('pragma foreign_key_check'))
 q.record('composite-swap-'+table+'-fk',fk);q.run('startup',db,'composite-swap-'+table)
# Full principal identity retry controls and zero transaction after UNKNOWN.
q.H=q.Q/'HarnessExt/bin/Release/net8.0/Harness.dll'
db=q.fresh('unknown-uncommitted');q.run('timed-life',db,'unknown-uncommitted',timeout=25,point='before-read',hold=8000,n=1,signal=q.E/'unknown-uncommitted.signal',release=q.E/'unknown-uncommitted.release',inject='before-cas')
q.record('unknown-uncommitted-durable',q.truth(db));q.run('startup',db,'unknown-uncommitted-restart');q.run('historical',db,'unknown-uncommitted-query',op='TIMED');q.execute(db,'unknown-uncommitted-retry',scope='TIMED',name='TIMED',ContentProfileFingerprint='PROBE_PROFILE_V1')
# Actual admitted control/separator identities, safe QA file names.
db=q.fresh('control-identities');inc=q.truth(db)['tables']['StoreIncarnations'][0][0];requests=[]
for i,(p,o) in enumerate([('A:B','C'),('A','B:C'),('A\0','B'),('A','\0B'),('A\r\n','B'),('A','\r\nB'),('A\u2028','B'),('A','\u2028B'),('A\x1f','B'),('A','\x1fB')]):requests.append(dict(PrincipalId=p,OperationId=o,ProbeScopeId='CTRL'+str(i),ExpectedProbeRevision=0,StoreIncarnationId=inc,ContentProfileFingerprint='PROFILE',PayloadJson='{}'))
f=q.E/'controls.requests.json';q.f.write(f,requests+requests);q.run('batch',db,'control-identities',request=f);q.record('control-identity-truth',q.truth(db));q.run('startup',db,'control-identities-ready');q.check()
