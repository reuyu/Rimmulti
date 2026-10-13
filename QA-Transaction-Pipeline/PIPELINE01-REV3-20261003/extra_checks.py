import run_checks as q
import json,hashlib,time,sqlite3,threading,shutil,subprocess,socket,struct
q.RESULTS.update(json.loads((q.E/'results.json').read_text(encoding='utf-8')))

def normal(name,source=None,flags=None,network=False):
 dest=q.Q/'Normal'/name;shutil.copytree(q.Q/'Candidate',dest);db=dest/'war_economy_pipeline.db'
 if source:q.clone(source,db)
 before=q.truth(db) if db.exists() else None;log=open(q.E/('normal-'+name+'.log'),'w',encoding='utf-8')
 p=subprocess.Popen([str(dest/'WarEconomy.Server.exe')]+(flags or []),stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,cwd=dest,creationflags=subprocess.CREATE_NO_WINDOW);q.OWNED.append(p)
 try:
  end=time.monotonic()+8;reached=False
  while time.monotonic()<end:
   text=(q.E/('normal-'+name+'.log')).read_text(encoding='utf-8')
   if 'Server ready!' in text:reached=True;break
   if p.poll() is not None:break
   time.sleep(.04)
  sent=False
  if network and reached:
   payload=json.dumps({'OperationType':'PIPELINE_PROBE_CAS','PrincipalId':'REMOTE_ATTACK','OperationId':'REMOTE_OP','ProbeScopeId':'REMOTE_SCOPE','ExpectedProbeRevision':0}).encode()
   with socket.create_connection(('127.0.0.1',7777),timeout=2) as s:s.sendall(struct.pack('<HI',65535,len(payload))+payload);time.sleep(.3)
   sent=True
  if p.poll() is None:p.stdin.write(b'status\nquit\n');p.stdin.flush();p.wait(timeout=7)
 finally:
  if p.poll() is None:p.kill();p.wait()
  log.close()
 text=(q.E/('normal-'+name+'.log')).read_text(encoding='utf-8');after=q.truth(db) if db.exists() else None
 q.record('normal-'+name,{'pid':p.pid,'exit':p.returncode,'pipelineReady':'PIPELINE_READY reached' in text,'listen':'Listening for RimWorld clients' in text,'gameplayReady':'Server ready!' in text,'probeFrameSent':sent,'canonicalUnchanged':before==after if before else None,'log':text,'tables':{k:len(v) for k,v in after['tables'].items()} if after else None})

def terminal_native():
 db=q.fresh('terminal-native');q.execute(db,'tn-commit');q.execute(db,'tn-abort',name='ABORT')
 before=q.truth(db)
 with q.conn(db) as c:cols=[r[1] for r in c.execute('pragma table_info(OperationRecords)')]
 for op in ['OP','ABORT']:
  expr=','.join("'changed'" if n=='PayloadJson' else '"'+n+'"' for n in cols)
  select=expr+f" FROM OperationRecords WHERE OperationId='{op}'"
  cases={'update':f"UPDATE OperationRecords SET PayloadJson='changed' WHERE OperationId='{op}'",'delete':f"DELETE FROM OperationRecords WHERE OperationId='{op}'",'insert-replace':'INSERT OR REPLACE INTO OperationRecords SELECT '+select,'replace-into':'REPLACE INTO OperationRecords SELECT '+select,'raw-insert':'INSERT INTO OperationRecords SELECT '+select,'upsert':'INSERT INTO OperationRecords SELECT '+select+" ON CONFLICT(PrincipalId,OperationId) DO UPDATE SET PayloadJson='changed'"}
  for name,s in cases.items():
   file=q.E/f'terminal-{op}-{name}.sql';file.write_text(s,encoding='utf-8');q.run('sql',db,f'tn-{op}-{name}',sqlfile=file)
 q.run('startup',db,'tn-restart');q.execute(db,'tn-retry');q.execute(db,'tn-abort-retry',name='ABORT');q.record('terminal-native-truth',{'unchanged':before==q.truth(db),'truth':q.truth(db)})

def identities():
 for i,pair in enumerate([(('A_B','C'),('A','B_C')),(('A_','B'),('A','_B')),(('한_글','림'),('한','글_림')),(('A:'+('x'*300)+'_B','C'),('A:'+('x'*300),'B_C'))]):
  db=q.fresh('derivative-'+str(i));requests=[]
  for j,(p,o) in enumerate(pair):
   r=q.req(db,name=o,principal=p,scope='S'+str(j));requests.append(r);q.run('execute',db,f'derivative-{i}-{j}',request=r)
  for j,r in enumerate(requests):q.run('execute',db,f'derivative-retry-{i}-{j}',request=r)
  q.record(f'derivative-truth-{i}',q.truth(db))
 for i,(a,b) in enumerate([('1e-29','-1e-29'),('1e-40','0.0'),('1.00000000000000000000000000001','1.00000000000000000000000000002'),('0.123456789012345678901234567891','0.123456789012345678901234567892'),('{"a":1,"a":2}','{"a":2}'),('{"x":{"a":1,"a":2}}','{"x":{"a":2}}'),('{"a":1} {"evil":2}','{"a":1}')]):
  db=q.fresh('canonical-replay-'+str(i));q.execute(db,f'canonical-{i}-first',PayloadJson=a);q.execute(db,f'canonical-{i}-retry',PayloadJson=b)
 # Strict ordering and representable distinction, and numeric spelling identity observations.
 for i,(a,b) in enumerate([('{"b":2,"a":1}','{"a":1,"b":2}'),('[1,2]','[2,1]'),('0','0.0'),('1.0','1e0'),('1','1.0'),('0.0000000000000000000000000001','0.0000000000000000000000000002')]):
  db=q.fresh('canonical-control-'+str(i));q.execute(db,f'canonical-control-{i}-first',PayloadJson=a);q.execute(db,f'canonical-control-{i}-retry',PayloadJson=b)

def schema_extra():
 base=q.D/'schema-base.db'
 cases={
 'raise-wrong-predicate':lambda d:q.sql(d,"DROP TRIGGER trg_operation_records_no_replace;CREATE TRIGGER trg_operation_records_no_replace BEFORE INSERT ON OperationRecords FOR EACH ROW WHEN 0 BEGIN SELECT RAISE(ABORT,'lookalike');END"),
 'check-literal-case':lambda d:q.rebuild_table(d,'OperationRecords',lambda s:s.replace("'COMMITTED', 'ABORTED'","'committed', 'aborted'")),
 'unique-order':lambda d:q.rebuild_table(d,'PublicationEvents',lambda s:s.replace('UNIQUE (StreamId, Seq)','UNIQUE (Seq, StreamId)')),
 'index-order':lambda d:q.sql(d,'DROP INDEX IX_PublicationEvents_Stream_Seq;CREATE INDEX IX_PublicationEvents_Stream_Seq ON PublicationEvents(Seq,StreamId)'),
 'index-partial':lambda d:q.sql(d,'DROP INDEX IX_PublicationEvents_Stream_Seq;CREATE INDEX IX_PublicationEvents_Stream_Seq ON PublicationEvents(StreamId,Seq) WHERE Seq<0')}
 for name,edit in cases.items():
  db=q.clone(base,q.D/('schema-'+name+'.db'));edit(db);before=q.truth(db);q.run('startup',db,'schema-'+name);q.record('schema-'+name+'-unchanged',before==q.truth(db))
  if name=='check-literal-case':q.execute(db,'schema-case-real-commit')

def consistency():
 base=q.D/'same-stream.db'
 changes={
 'missing-receipt':'delete from CommitReceipts',
 'receipt-hash':"update CommitReceipts set ReceiptHash='wrong'",
 'receipt-revision':'update CommitReceipts set CommittedRevision=999',
 'receipt-scope':"update CommitReceipts set ProbeScopeId='OTHER'",
 'receipt-principal':"update CommitReceipts set PrincipalId='OTHER'",
 'receipt-operation':"update CommitReceipts set OperationId='OTHER'",
 'missing-event':'delete from PublicationEvents',
 'event-payload':"update PublicationEvents set CanonicalPayload='false'",
 'event-hash':"update PublicationEvents set PayloadFingerprint='bad'",
 'event-type':"update PublicationEvents set EventType='WRONG'",
 'event-stream':"update PublicationEvents set StreamId='OTHER'",
 'event-seq':"update PublicationEvents set Seq=Seq+100",
 'event-incarnation':"update PublicationEvents set StoreIncarnationId='OTHER'",
 'missing-history':'delete from ProbeRevisionHistory',
 'history-middle':'delete from ProbeRevisionHistory where ProbeRevision=4',
 'aggregate-revision':'update ProbeAggregates set ProbeRevision=999',
 'aggregate-missing':'delete from ProbeAggregates',
 'missing-audit':'delete from AuditRecords',
 'audit-values':"update AuditRecords set ProbeScopeId='OTHER', OldRevision=999,NewRevision=999,DetailsJson='wrong'",
 'orphan-receipt':"update CommitReceipts set OperationId='ORPHAN'",
 'orphan-event':"update PublicationEvents set OperationId='ORPHAN'",
 'duplicate-receipt':"insert into CommitReceipts select ReceiptId||'_dup',PrincipalId,OperationId,ProbeScopeId,CommittedRevision,StoreIncarnationId,CommittedAtEpochMs,ReceiptHash from CommitReceipts",
 'duplicate-event':"insert into PublicationEvents select StreamId,Seq+100,EventId||'_dup',PrincipalId,OperationId,EventType,CanonicalPayload,PayloadFingerprint,StoreIncarnationId,CreatedAt,CreatedAtEpochMs from PublicationEvents"}
 for name,s in changes.items():
  db=q.clone(base,q.D/('consistency-'+name+'.db'));q.sql(db,s);before=q.truth(db);q.run('startup',db,'consistency-'+name);q.record('consistency-'+name+'-unchanged',before==q.truth(db))
 # ABORTED + success rows with matching FK keys. Use legitimate aborted operation generated by candidate.
 for kind in ['receipt','event']:
  db=q.clone(base,q.D/('consistency-aborted-'+kind+'.db'));q.execute(db,'seed-aborted-'+kind,name='ABORTED',expected=0)
  if kind=='receipt':s="insert into CommitReceipts select ReceiptId||'_abort',PrincipalId,'ABORTED',ProbeScopeId,CommittedRevision,StoreIncarnationId,CommittedAtEpochMs,ReceiptHash from CommitReceipts limit 1"
  else:s="insert into PublicationEvents select StreamId,Seq+100,EventId||'_abort',PrincipalId,'ABORTED',EventType,CanonicalPayload,PayloadFingerprint,StoreIncarnationId,CreatedAt,CreatedAtEpochMs from PublicationEvents limit 1"
  q.sql(db,s);q.run('startup',db,'consistency-aborted-'+kind)

def shutdown():
 q.run('lifetime',q.fresh('lifetime'),'service-coordinator-lifetime')
 db=q.fresh('queue-held');q.run('queue',db,'queue-held',timeout=25,n=1205);q.record('queue-held-truth',q.truth(db))
 # Real lock remains held beyond the full native busy/default window, then release after completion/deadline.
 db=q.fresh('queue-lock');c=q.conn(db);c.execute('BEGIN IMMEDIATE');signal=q.E/'queue-lock.signal';release=q.E/'queue-lock.release';p,log=q.spawn('queue-lock',db,'queue-lock',signal=signal,release=release,n=1205)
 try:q.barrier(signal,p,seconds=42)
 finally:c.rollback();c.close();release.write_text('release',encoding='utf-8')
 p.wait(timeout=35);log.close();rows=[json.loads(x) for x in (q.E/'queue-lock.stdout').read_text(encoding='utf-8').splitlines() if x.startswith('{')];q.record('queue-lock-result',{'pid':p.pid,'rows':rows,'truth':q.truth(db)})
 q.run('startup',db,'queue-lock-restart')
 q.execute(db,'queue-lock-query-retry',scope='QUEUE',name='Q0')
 q.run('startup',q.D/'queue-held.db','queue-held-restart');q.execute(q.D/'queue-held.db','queue-held-query-retry',scope='QUEUE',name='Q0')

def main():
 q.check();threading.Thread(target=q.watch,daemon=True).start()
 try:
  terminal_native();identities();schema_extra();consistency();shutdown()
  normal('fresh',network=True);normal('valid-restart',q.D/'same-stream.db')
  for name in ['check-literal-case','raise-wrong-predicate','wrong-pk-order','wrong-nullable','wrong-type','wrong-stream-unique','unique-order','wrong-fk-columns','wrong-fk-actions','wrong-check','index-order','multiple-active']:
   normal('schema-'+name,q.D/('schema-'+name+'.db'))
  for name in ['receipt-scope','event-type','duplicate-event','audit-values','missing-receipt','receipt-hash','event-stream']:
   normal('consistency-'+name,q.D/('consistency-'+name+'.db'))
  for ver in [1,2,3]:normal('legacy-'+str(ver),q.D/('legacy-real-'+str(ver)+'.db'))
  normal('foreign-zero',q.D/'foreign-zero-True.db')
  marker=q.D/'marker.db';q.sql(marker,"create table Marker(id INTEGER,value TEXT);insert into Marker values(1,'KEEP')");before=q.truth(marker)
  normal('old-test-args',flags=['--test-pipeline-e1','--db',str(marker)]);normal('old-crash-args',flags=['--crash-worker','--db',str(marker),'--fault','AfterCommitted']);q.record('cli-marker-preservation',before==q.truth(marker))
  q.check()
 finally:
  q.STOP.set()
  for p in q.OWNED:
   if p.poll() is None:p.kill();p.wait()
  after=q.f.tree();q.f.write(q.Q/'freeze-after.json',after);before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('freeze-extra',{'count':len(after),'changes':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]})
if __name__=='__main__':main()
