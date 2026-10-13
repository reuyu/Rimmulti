import extra_checks as x
q=x.q
q.RESULTS={}
def record(k,v):
 q.RESULTS[k]=v;q.f.write(q.E/'normal-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=record
q.check()
x.normal('rev4-fresh',network=True);x.normal('rev4-valid-restart',q.D/'same-stream.db')
for name in ['check-literal-case','raise-wrong-predicate','wrong-pk-order','wrong-nullable','wrong-type','unique-order','index-partial','multiple-active']:
 x.normal('rev4-schema-'+name,q.D/('schema-'+name+'.db'))
for name in ['receipt-scope','event-type','duplicate-event','audit-values','missing-receipt','receipt-hash','event-stream']:
 x.normal('rev4-consistency-'+name,q.D/('consistency-'+name+'.db'))
for ver in [1,2,3,4]:x.normal('rev4-legacy-'+str(ver),q.D/('legacy-real-'+str(ver)+'.db'))
x.normal('rev4-foreign',q.D/'foreign-zero-True.db')
marker=q.D/'deep-marker.db';q.sql(marker,"create table Marker(id INTEGER,value TEXT);insert into Marker values(1,'KEEP')");before=q.truth(marker)
x.normal('rev4-old-testargs',flags=['--test-pipeline-e1','--db',str(marker)]);x.normal('rev4-old-crashargs',flags=['--crash-worker','--db',str(marker),'--fault','AfterCommitted']);q.record('cli-marker-preserved',before==q.truth(marker));q.check()
