import extra_checks as x
import json,time
q=x.q;q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.f.write(q.E/'completion-results.json',q.RESULTS);print(k,str(v)[:180],flush=True)
q.record=rec
# Native kill after SQLite transaction begins, before CAS.
db=q.fresh('kill-before-cas');req=q.req(db);signal=q.E/'kill-before-cas.signal';release=q.E/'kill-before-cas.release';p,log=q.spawn('execute',db,'kill-before-cas',request=req,point='before-cas',signal=signal,release=release);q.barrier(signal,p);p.kill();p.wait();log.close();q.record('kill-before-cas-durable',q.truth(db));q.run('startup',db,'kill-before-cas-restart');q.run('execute',db,'kill-before-cas-retry',request=req)
# Valid committed-only startup, physical executable; deep mutations also checked using actual Main.
x.normal('rev4-valid-committed',q.D/'confirmed-graph-base.db')
for name in ['valid-hash-receipt-swap','event-id-swap','operation-fingerprint','audit-details']:
 x.normal('rev4-false-ready-'+name,q.D/('confirmed-graph-'+name+'.db'))
# Correct hash duplicate receipt, matching full metadata, balanced by removal on another operation.
db=q.clone(q.D/'confirmed-graph-base.db',q.D/'balanced-valid-receipt.db')
with q.conn(db) as c:
 c.row_factory=q.sqlite3.Row;r=dict(c.execute("select * from CommitReceipts where OperationId='SAC1'").fetchone());c.execute("delete from CommitReceipts where OperationId='SBC1'");r['ReceiptId']+='DUP';r['ReceiptHash']=q.hashlib.sha256(':'.join(str(r[k]) for k in ['ReceiptId','PrincipalId','OperationId','ProbeScopeId','CommittedRevision','StoreIncarnationId','CommittedAtEpochMs']).encode()).hexdigest().upper();c.execute('insert into CommitReceipts values('+','.join('?' for _ in r)+')',list(r.values()))
q.run('startup',db,'balanced-valid-receipt')
# Response remains pending beyond configured 2s admission timeout while writer is barrier-held; shutdown eventually returns terminal.
q.run('queue-timeout',q.fresh('response-deadline'),'response-deadline',timeout=30,n=1205)
q.check();after=q.f.tree();q.f.write(q.Q/'freeze-after.json',after);before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('final-freeze',{'count':len(after),'changes':[k for k in set(after)|set(before) if after.get(k)!=before.get(k)]})
