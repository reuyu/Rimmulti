from pathlib import Path
import run_checks as q
import json,sqlite3,shutil,time
q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'semantic-results.json',q.RESULTS);print(k,str(v)[:300],flush=True)
q.record=record
q.H=q.Q/'HarnessExt/bin/Release/net8.0/Harness.dll'
for p in (q.Q/'Candidate').glob('*.dll'):
 if not (q.H.parent/p.name).exists():shutil.copy2(p,q.H.parent/p.name)
shutil.copy2(q.Q/'Candidate/runtimes/win-x64/native/e_sqlite3.dll',q.H.parent/'e_sqlite3.dll')
def thaw(db,fn):
 with q.conn(db) as c:
  rows=c.execute("select name,sql from sqlite_master where type='trigger'").fetchall()
  for n,s in rows:c.execute('DROP TRIGGER "'+n+'"')
  result=fn(c)
  for n,s in rows:c.execute(s)
 return result
base=q.fresh('mixed-authority-base')
for scope,count in [('A',4),('B',3)]:
 for i in range(2):q.execute(base,'mixed-'+scope+'C'+str(i),name=scope+'C'+str(i),scope=scope,expected=i)
 q.execute(base,'mixed-'+scope+'AB',name=scope+'AB',scope=scope,expected=0)
 for i in range(2,count):q.execute(base,'mixed-'+scope+'C'+str(i),name=scope+'C'+str(i),scope=scope,expected=i)
q.run('startup',base,'mixed-positive-ready');q.record('mixed-source-truth',q.truth(base))
# exact same OperationId valid composite parents, same and different scopes
for name,same in [('same-parent-scope',True),('different-parent-scope',False)]:
 db=q.fresh(name);q.execute(db,name+'-first',name='SAME',principal='P1',scope='S');q.execute(db,name+'-second',name='SAME',principal='P2',scope='S' if same else 'OTHER',expected=1 if same else 99);q.run('startup',db,name+'-ready')

def alter_observation(c,value,change_col=True,change_json=True,resign_reason=True):
 r=c.execute("select DetailsJson from AuditRecords where OperationId='AAB'").fetchone();details=json.loads(r[0]);old=details['observedRevision']
 if change_json:
  details['observedRevision']=value
  if resign_reason:details['reason']=f'STALE_REVISION: expected 0 != actual {value}'
  c.execute("update AuditRecords set DetailsJson=? where OperationId='AAB'",(json.dumps(details,separators=(',',':')),))
 if change_col:c.execute("update AuditRecords set OldRevision=? where OperationId='AAB'",(value,))
 if resign_reason:c.execute("update OperationRecords set FailureReason=? where OperationId='AAB'",(f'STALE_REVISION: expected 0 != actual {value}',))
 return {'sourceObserved':old,'injectedObserved':value,'columnChanged':change_col,'jsonChanged':change_json}
for name,val,col,js in [('historical-earlier',1,True,True),('historical-later',4,True,True),('other-scope-observed',3,True,True),('column-json-mismatch',1,True,False),('json-column-mismatch',1,False,True)]:
 db=q.clone(base,q.D/(name+'.db'));r=thaw(db,lambda c:alter_observation(c,val,col,js));q.record(name+'-injection',r);before=q.truth(db);q.run('startup',db,name);q.record(name+'-unchanged',before==q.truth(db))

def change_detail(c,op,key,val,remove=False):
 d=json.loads(c.execute('select DetailsJson from AuditRecords where OperationId=?',(op,)).fetchone()[0]);original=d.copy()
 if remove:d.pop(key,None)
 else:d[key]=val
 c.execute('update AuditRecords set DetailsJson=? where OperationId=?',(json.dumps(d,separators=(',',':')),op));return {'before':original,'after':d}
for key,value in [('status','SUCCESS'),('reason','WRONG'),('expectedRevision',8),('observedRevision',8),('scopeId','B'),('principalId','OTHER'),('operationId','OTHER')]:
 name='abort-detail-'+key;db=q.clone(base,q.D/(name+'.db'));q.record(name+'-injection',thaw(db,lambda c:change_detail(c,'AAB',key,value)));q.run('startup',db,name)
for key in ['expectedRevision','observedRevision','scopeId','principalId','operationId','status','reason']:
 name='abort-remove-'+key;db=q.clone(base,q.D/(name+'.db'));thaw(db,lambda c:change_detail(c,'AAB',key,None,True));q.run('startup',db,name)
for name,sql in {'failure-reason':"update OperationRecords set FailureReason='SUCCESS' where OperationId='AAB'",'abort-eventtype':"update AuditRecords set EventType='PROBE_CAS_COMMITTED' where OperationId='AAB'",'audit-parent-swap':"update AuditRecords set PrincipalId='OTHER' where OperationId='AAB'",'history-parent-swap':"update ProbeRevisionHistory set OperationId='BC0' where OperationId='AC0'",'receipt-principal-swap':"update CommitReceipts set PrincipalId='OTHER' where OperationId='AC0'",'orphan-parent':"delete from OperationRecords where OperationId='AC0'",'duplicate-history-parent':"update ProbeRevisionHistory set OperationId='AC0' where OperationId='AC1'"}.items():
 db=q.clone(base,q.D/(name+'.db'));thaw(db,lambda c:c.execute(sql));q.run('startup',db,name)
# Complete envelope independently recomputed, for both terminal states.
fields={'PrincipalId':"'OTHER'",'OperationId':"'OTHER'",'ProbeScopeId':"'OTHER'",'ExpectedProbeRevision':'999','OperationType':"'OTHER'",'OperationSchemaVersion':'999','ContentProfileFingerprint':"'OTHER'",'ConfigSnapshotRef':"'OTHER'",'StoreIncarnationId':"'OTHER'",'PayloadJson':"'{\"x\":99}'",'RequestFingerprint':"'OTHER'"}
for op in ['AC0','AAB']:
 for key,val in fields.items():
  name='envelope-'+op+'-'+key;db=q.clone(base,q.D/(name+'.db'));thaw(db,lambda c:c.execute(f'update OperationRecords set {key}={val} where OperationId=?',(op,)));q.run('startup',db,name)
# Typed commit audit contract: inject missing extra domain fields explicitly.
for key,val in [('receiptId','WRONG'),('fingerprint','WRONG'),('eventId','WRONG'),('principalId','WRONG'),('operationId','WRONG'),('scopeId','WRONG'),('expectedRevision',99),('newRevision',99)]:
 name='commit-detail-'+key;db=q.clone(base,q.D/(name+'.db'));q.record(name+'-injection',thaw(db,lambda c:change_detail(c,'AC0',key,val)));q.run('startup',db,name)
def swaps(c,kind):
 c.row_factory=sqlite3.Row;table='CommitReceipts' if kind=='receipt' else 'PublicationEvents';key='ReceiptId' if kind=='receipt' else 'EventId';rows=c.execute('select * from '+table+" where OperationId in ('AC0','BC0') order by OperationId").fetchall();ids=[r[key] for r in rows]
 for r in rows:c.execute(f'update {table} set {key}={key}||\'TEMP\' where OperationId=?',(r['OperationId'],))
 for r,new in zip(rows,reversed(ids)):
  c.execute(f'update {table} set {key}=? where OperationId=?',(new,r['OperationId']))
  if kind=='receipt':
   h=q.hashlib.sha256(':'.join(map(str,[new,r['PrincipalId'],r['OperationId'],r['ProbeScopeId'],r['CommittedRevision'],r['StoreIncarnationId'],r['CommittedAtEpochMs']])).encode()).hexdigest().upper();c.execute('update CommitReceipts set ReceiptHash=? where OperationId=?',(h,r['OperationId']))
for kind in ['receipt','event']:
 db=q.clone(base,q.D/('swap-'+kind+'.db'));thaw(db,lambda c:swaps(c,kind));q.run('startup',db,'swap-'+kind)
q.run('inputs',q.fresh('all-inputs'),'all-inputs');q.run('derivative',base,'derivative-boundaries');q.check()
