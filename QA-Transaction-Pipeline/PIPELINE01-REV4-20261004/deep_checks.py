from pathlib import Path
import run_checks as q
import json,time,threading,hashlib,shutil,sqlite3,subprocess
q.RESULTS={}
def record(k,v):
 q.RESULTS[k]=v;q.f.write(q.E/'deep2-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:400],flush=True)
q.record=record
q.H=q.Q/'HarnessExt/bin/Release/net8.0/Harness.dll'
out=q.H.parent
for p in (q.Q/'Candidate').glob('*.dll'):
 if not (out/p.name).exists():shutil.copy2(p,out/p.name)
shutil.copy2(q.Q/'Candidate/runtimes/win-x64/native/e_sqlite3.dll',out/'e_sqlite3.dll')

def batch():
 db=q.fresh('deep-json');inc=q.truth(db)['tables']['StoreIncarnations'][0][0]
 cases=[('tinypos','1e-29'),('tinyneg','-1e-29'),('tiny40','1e-40'),('zero','0'),('precision1','1.00000000000000000000000000001'),('precision2','1.00000000000000000000000000002'),('frac1','0.123456789012345678901234567891'),('frac2','0.123456789012345678901234567892')]
 for n in ['1e308','1e-308','1e309','1e-309','1e2147483648','1e-2147483648','1E+000','1.0','1e0','1','0.0','-0','-0e308','0e-308','0e309']:cases.append(('num'+str(len(cases)),n))
 cases+= [('mant1000','9'*1000),('mant1001','9'*1001),('mantZeroLead','0.'+'0'*400+'1'),('mant1000scaled','9'*1000+'e-308'),('dup-root','{"a":1,"a":2}'),('dup-nested','{"x":{"a":1,"a":2}}'),('dup-array','[{"a":1,"a":2}]'),('dup-escaped','{"a":1,"\\u0061":2}'),('sur-key','{"\\ud800":1}'),('sur-value','{"a":"\\ud800"}'),('sur-low','"\\udc00"'),('sur-reversed','"\\udc00\\ud800"'),('sur-valid','"\\ud83d\\ude00"'),('second-root','{} {}'),('trailing','{}x'),('trailing-space','{} \r\n\t'),('depth64','['*64+'0'+']'*64),('depth65','['*65+'0'+']'*65),('size1mb',json.dumps('x'*1048576)),('size4mb',json.dumps('x'*4194304))]
 requests=[]
 for name,payload in cases:requests.append(dict(PrincipalId='P',OperationId=name,ProbeScopeId=name,ExpectedProbeRevision=0,StoreIncarnationId=inc,ContentProfileFingerprint='PROFILE',PayloadJson=payload))
 # Equivalent spellings and collisions use one operation ID each on actual production coordinator.
 for group,vals in [('eq',['1','1.0','1e0','1E+000']),('zeroeq',['0','-0','0.0','0e308','-0e-308']),('tinycollision',['1e-29','-1e-29']),('tiny40collision',['1e-40','0']),('pcollision',['1.00000000000000000000000000001','1.00000000000000000000000000002']),('fcollision',['0.123456789012345678901234567891','0.123456789012345678901234567892'])]:
  for v in vals:requests.append(dict(PrincipalId='P',OperationId=group,ProbeScopeId=group,ExpectedProbeRevision=0,StoreIncarnationId=inc,ContentProfileFingerprint='PROFILE',PayloadJson=v))
 f=q.E/'deep-json.requests.json';q.f.write(f,requests);q.run('batch',db,'json-full',timeout=60,request=f)
 q.record('json-truth',q.truth(db))

def schema():
 base=q.D/'schema-base.db'
 cases={
 'escaped-check':lambda d:q.rebuild_table(d,'OperationRecords',lambda s:s.replace("'COMMITTED'","'COM''MITTED'")),
 'check-comment':lambda d:q.rebuild_table(d,'ProbeAggregates',lambda s:s.replace('CHECK (ProbeRevision >= 0)','CHECK (1 /* ProbeRevision >= 0 */)')),
 'trigger-comment':lambda d:q.sql(d,"DROP TRIGGER trg_operation_records_no_update;CREATE TRIGGER trg_operation_records_no_update BEFORE UPDATE ON OperationRecords BEGIN SELECT 1 /* RAISE(ABORT,'immutable') */;END"),
 'trigger-predicate-lookalike':lambda d:q.sql(d,"DROP TRIGGER trg_operation_records_no_update;CREATE TRIGGER trg_operation_records_no_update BEFORE UPDATE ON OperationRecords WHEN 1=0 BEGIN SELECT RAISE(ABORT,'immutable');END"),
 'fk-target':lambda d:q.rebuild_table(d,'CommitReceipts',lambda s:s.replace('REFERENCES OperationRecords(PrincipalId, OperationId)','REFERENCES OperationRecords(OperationId, PrincipalId)')),
 'fk-update':lambda d:q.rebuild_table(d,'CommitReceipts',lambda s:s.replace('ON UPDATE NO ACTION','ON UPDATE CASCADE')),
 'index-uniqueness':lambda d:q.sql(d,'DROP INDEX IX_PublicationEvents_Stream_Seq;CREATE UNIQUE INDEX IX_PublicationEvents_Stream_Seq ON PublicationEvents(StreamId,Seq)'),
 }
 for name,change in cases.items():
  db=q.clone(base,q.D/('deep-schema-'+name+'.db'));change(db);before=q.truth(db);q.run('startup',db,'deep-schema-'+name);q.record('deep-schema-'+name+'-unchanged',before==q.truth(db))
 db=q.clone(q.R/'QA-Transaction-Pipeline/PIPELINE01-REV3-20261003/DBs/identity.db',q.D/'legacy-real-4.db');before=q.truth(db);q.run('startup',db,'legacy-real-4');q.record('legacy4-unchanged',before==q.truth(db))
 db=q.clone(base,q.D/'canary-no-mutation.db');before=q.truth(db)
 for i in range(3):q.run('startup',db,'canary-ready-'+str(i))
 q.record('canary-no-durable-mutation',before==q.truth(db))
 q.record('schema-introspection',{'tables':q.truth(base)['schema'],'pragmas':{t:{'columns':list(q.conn(base).execute('pragma table_info('+t+')')),'fk':list(q.conn(base).execute('pragma foreign_key_list('+t+')')),'indexes':list(q.conn(base).execute('pragma index_list('+t+')'))} for t in q.truth(base)['tables']}})

def thaw(d,fn):
 with q.conn(d) as c:
  rows=c.execute("select name,sql from sqlite_master where type='trigger'").fetchall()
  for n,s in rows:c.execute('DROP TRIGGER "'+n+'"')
  fn(c)
  for n,s in rows:c.execute(s)

def graph():
 base=q.fresh('deep-graph-base')
 for scope in ['SA','SB']:
  q.execute(base,'seed-'+scope+'-1',name=scope+'C1',scope=scope)
  q.execute(base,'seed-'+scope+'-2',name=scope+'C2',scope=scope,expected=1)
  q.execute(base,'seed-'+scope+'-abort',name=scope+'AB',scope=scope,expected=0)
 q.run('startup',base,'deep-graph-valid')
 def swap_receipts(c):
  c.row_factory=sqlite3.Row;rows=c.execute("select * from CommitReceipts where CommittedRevision=1 order by ProbeScopeId").fetchall();ids=[r['ReceiptId'] for r in rows]
  for r in rows:c.execute('update CommitReceipts set ReceiptId=ReceiptId||\'TEMP\' where OperationId=?',(r['OperationId'],))
  for r,new in zip(rows,reversed(ids)):
   h=hashlib.sha256(':'.join(map(str,[new,r['PrincipalId'],r['OperationId'],r['ProbeScopeId'],r['CommittedRevision'],r['StoreIncarnationId'],r['CommittedAtEpochMs']])).encode()).hexdigest().upper()
   c.execute('update CommitReceipts set ReceiptId=?,ReceiptHash=? where OperationId=?',(new,h,r['OperationId']))
 def swap_events(c):
  rows=c.execute('select EventId,OperationId from PublicationEvents where Seq=1 order by StreamId').fetchall()
  for _,op in rows:c.execute("update PublicationEvents set EventId=EventId||'TEMP' where OperationId=?",(op,))
  for r,new in zip(rows,reversed(rows)):c.execute('update PublicationEvents set EventId=? where OperationId=?',(new[0],r[1]))
 cases={'valid-hash-receipt-swap':swap_receipts,'event-id-swap':swap_events,'audit-details':lambda c:c.execute("update AuditRecords set DetailsJson='{\"ReceiptId\":\"WRONG\",\"Fingerprint\":\"WRONG\"}'"),'operation-type':lambda c:c.execute("update OperationRecords set OperationType='WRONG'"),'operation-profile':lambda c:c.execute("update OperationRecords set ContentProfileFingerprint='WRONG'"),'operation-fingerprint':lambda c:c.execute("update OperationRecords set RequestFingerprint='WRONG'"),'operation-incarnation-aborted':lambda c:c.execute("update OperationRecords set StoreIncarnationId='WRONG' where State='ABORTED'"),'audit-orphan':lambda c:c.execute("update AuditRecords set OperationId='ORPHAN' where OperationId='SAC1'"),'history-orphan':lambda c:c.execute("update ProbeRevisionHistory set OperationId='ORPHAN' where ProbeScopeId='SA' and ProbeRevision=1"),'missing-operation':lambda c:c.execute("delete from OperationRecords where OperationId='SAC1'"),'balanced-missing-extra-audit':lambda c:(c.execute("delete from AuditRecords where OperationId='SAC1'"),c.execute("insert into AuditRecords select AuditId||'_DUP',PrincipalId,OperationId,ProbeScopeId,EventType,OldRevision,NewRevision,DetailsJson,TimestampEpochMs from AuditRecords where OperationId='SBC1'")),'balanced-receipt-parent-duplicate':lambda c:c.execute("update CommitReceipts set PrincipalId='P',OperationId='SBC1' where OperationId='SAC1'"),'history-gap':lambda c:c.execute("update ProbeRevisionHistory set ProbeRevision=3 where ProbeScopeId='SA' and ProbeRevision=2"),'aggregate-gap':lambda c:c.execute("update ProbeAggregates set ProbeRevision=3 where ProbeScopeId='SA'")}
 for name,fn in cases.items():
  db=q.clone(base,q.D/('deep-graph-'+name+'.db'));thaw(db,fn);before=q.truth(db);q.run('startup',db,'deep-graph-'+name);q.record('deep-graph-'+name+'-unchanged',before==q.truth(db))
 for name in ['sameid-valid-commit','sameid-valid-abort']:
  db=q.fresh(name);q.execute(db,name+'-first',name='SAME',scope='S',principal='P1')
  q.execute(db,name+'-second',name='SAME',scope='S' if name.endswith('commit') else 'OTHER',principal='P2',expected=1 if name.endswith('commit') else 999)
  q.run('startup',db,name+'-restart')

def life():
 db=q.fresh('service-extended');q.run('lifetime-extended',db,'service-extended',timeout=35);q.run('startup',db,'service-extended-restart')
 for point in ['after-cas','after-audit','native-commit','native-wal']:
  db=q.fresh('deep-shutdown-'+point);q.run('shutdown-boundary',db,'deep-shutdown-'+point,timeout=30,point=point,signal=q.E/('deep-'+point+'.signal'),release=q.E/('deep-'+point+'.release'));q.run('startup',db,'deep-shutdown-'+point+'-restart')
 db=q.fresh('deep-lock');c=q.conn(db);c.execute('BEGIN IMMEDIATE');signal=q.E/'deep-lock.signal';release=q.E/'deep-lock.release';p,log=q.spawn('queue-lock',db,'deep-lock',signal=signal,release=release,n=1205)
 try:q.barrier(signal,p,seconds=42);time.sleep(4)
 finally:c.rollback();c.close();release.write_text('release')
 p.wait(timeout=35);log.close();q.record('deep-lock-evidence',{'pid':p.pid,'stdout':(q.E/'deep-lock.stdout').read_text(encoding='utf-8'),'truth':q.truth(db)});q.run('startup',db,'deep-lock-restart')
 db=q.fresh('deep-nativewal-kill');request=q.req(db);signal=q.E/'deepkill-wal.signal';release=q.E/'deepkill-wal.release';p,log=q.spawn('execute',db,'deepkill-wal',request=request,point='native-wal',signal=signal,release=release);q.barrier(signal,p);p.kill();p.wait();log.close();q.record('deepkill-wal-truth',q.truth(db));q.run('startup',db,'deepkill-wal-restart');q.run('execute',db,'deepkill-wal-retry',request=request)
 main=q.Q/'MainActive';main.mkdir(exist_ok=True);old=q.Q;q.Q=main
 try:q.run('main-active',main/'unused.db','actual-main-active',timeout=30)
 finally:q.Q=old

def schema_resume():
 base=q.D/'schema-base.db';db=q.clone(q.R/'QA-Transaction-Pipeline/PIPELINE01-REV3-20261003/DBs/identity.db',q.D/'legacy-real-4.db');before=q.truth(db);q.run('startup',db,'legacy-real-4');q.record('legacy4-unchanged',before==q.truth(db))
 db=q.clone(base,q.D/'canary-no-mutation.db');before=q.truth(db)
 for i in range(3):q.run('startup',db,'canary-ready-'+str(i))
 q.record('canary-no-durable-mutation',before==q.truth(db));q.record('schema-introspection',{'tables':q.truth(base)['schema'],'pragmas':{t:{'columns':list(q.conn(base).execute('pragma table_info('+t+')')),'fk':list(q.conn(base).execute('pragma foreign_key_list('+t+')')),'indexes':list(q.conn(base).execute('pragma index_list('+t+')'))} for t in q.truth(base)['tables']}})

try:
 q.RESULTS.update(json.loads((q.E/'deep-results.json').read_text(encoding='utf-8')));schema_resume();graph();life();q.check()
finally:
 for p in q.OWNED:
  if p.poll() is None:p.kill();p.wait()
 after=q.f.tree();before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('deep-freeze',{'changes':[p for p in set(after)|set(before) if after.get(p)!=before.get(p)]})
