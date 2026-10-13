import extra_checks as x
import json,time,sqlite3
q=x.q;q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'completion-results.json',q.RESULTS);print(k,str(v)[:220],flush=True)
q.record=record;q.check()
# Positive normal executable evidence using candidate-generated mixed/contended/composite parent fixtures.
for name in ['mixed-authority-base','cas','same-id','same-stream','same-parent-scope','different-parent-scope']:
 x.normal('rev5-'+name,q.D/(name+'.db'))
x.normal('rev5-fresh',network=True)
for name in ['historical-earlier','historical-later','other-scope-observed','abort-detail-status','failure-reason','commit-detail-eventId']:
 x.normal('rev5-false-ready-'+name,q.D/(name+'.db'))
# Canary and actual legacy4/5 admission; fresh/normal state preservation.
db=q.clone(q.D/'mixed-authority-base.db',q.D/'canary-mixed.db');before=q.truth(db)
for i in range(3):q.run('startup',db,'canary-mixed-'+str(i))
q.record('canary-mixed-unchanged',before==q.truth(db))
for ver in [4,5]:
 db=q.D/('legacy-real-'+str(ver)+'.db');before=q.truth(db);q.run('startup',db,'legacy-real-'+str(ver));q.record('legacy-'+str(ver)+'-unchanged',before==q.truth(db))
for ver in range(1,6):x.normal('rev5-legacy-'+str(ver),q.D/('legacy-real-'+str(ver)+'.db'))
# Native hook and CAS-before cut regression, not just successful sequential commits.
for point in ['before-cas','native-wal']:
 db=q.fresh('hardkill-'+point);request=q.req(db);signal=q.E/('hardkill-'+point+'.signal');release=q.E/('hardkill-'+point+'.release');p,log=q.spawn('execute',db,'hardkill-'+point,request=request,point=point,signal=signal,release=release);q.barrier(signal,p);p.kill();p.wait();log.close();q.record('hardkill-'+point+'-durable',q.truth(db));q.run('startup',db,'hardkill-'+point+'-restart');q.run('execute',db,'hardkill-'+point+'-retry',request=request)
# Parseable committed old/new/status and required-key omissions; actual stored fields, not only extra fields.
base=q.D/'mixed-authority-base.db'
for op in ['AC0','AAB']:
 with q.conn(base) as c:source=json.loads(c.execute('select DetailsJson from AuditRecords where OperationId=?',(op,)).fetchone()[0])
 for key in source:
  if op=='AC0':
   db=q.clone(base,q.D/('commit-remove-'+key+'.db'));modified=source.copy();modified.pop(key)
   q.sql(db,"update AuditRecords set DetailsJson='"+json.dumps(modified).replace("'","''")+"' where OperationId='AC0'");q.run('startup',db,'commit-remove-'+key)
  if key=='oldRevision':
   db=q.clone(base,q.D/'commit-old-json.db');modified=source|{'oldRevision':999};q.sql(db,"update AuditRecords set DetailsJson='"+json.dumps(modified)+"' where OperationId='AC0'");q.run('startup',db,'commit-old-json')
# terminal immutability remains enforced in actual production connection and graph schema.
marker=q.D/'marker.db';q.sql(marker,"create table Marker(id INTEGER,value TEXT);insert into Marker values(1,'KEEP')");before=q.truth(marker)
x.normal('rev5-old-testflags',flags=['--test-pipeline-e1','--db',str(marker)]);x.normal('rev5-old-crashflags',flags=['--crash-worker','--db',str(marker),'--fault','AfterCommitted']);q.record('cli-marker-unchanged',before==q.truth(marker))
q.check()
