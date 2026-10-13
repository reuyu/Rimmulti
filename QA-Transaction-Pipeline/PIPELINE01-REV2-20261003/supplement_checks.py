import run_checks as q
from pathlib import Path
import json,sqlite3,time,shutil,subprocess,socket,struct,threading
q.RESULTS.update(json.loads((q.E/'results.json').read_text(encoding='utf-8')))
def normal(name,source=None,flags=None,network=False):
 dest=q.Q/'Normal'/name;shutil.copytree(q.Q/'Candidate',dest);db=dest/'war_economy_pipeline.db'
 if source:q.clone(source,db)
 before=q.truth(db) if db.exists() else None;log=open(q.E/('normal-'+name+'.log'),'w',encoding='utf-8')
 cmd=[str(dest/'WarEconomy.Server.exe')]+(flags or []);p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,cwd=dest,creationflags=subprocess.CREATE_NO_WINDOW);q.OWNED.append(p)
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
   with socket.create_connection(('127.0.0.1',7777),timeout=2) as s:s.sendall(struct.pack('<HI',65535,len(payload))+payload);time.sleep(.2)
   sent=True
  if p.poll() is None:p.stdin.write(b'status\nquit\n');p.stdin.flush();p.wait(timeout=7)
 finally:
  if p.poll() is None:p.kill();p.wait()
  log.close()
 text=(q.E/('normal-'+name+'.log')).read_text(encoding='utf-8');after=q.truth(db) if db.exists() else None
 q.record('normal-'+name,{'pid':p.pid,'exit':p.returncode,'pipelineReady':'PIPELINE_READY reached' in text,'listen':'Listening for RimWorld clients' in text,'gameplayReady':'Server ready!' in text,'probeFrameSent':sent,'canonicalUnchanged':before==after if before else None,'log':text,'tables':{k:len(v) for k,v in after['tables'].items()} if after else None})
def main():
 q.check();threading.Thread(target=q.watch,daemon=True).start()
 try:
  normal('fresh',network=True);normal('valid-event-restart',q.D/'same-stream.db');normal('missing-column',q.D/'schema-missing-column.db');normal('noop-trigger',q.D/'schema-noop-trigger.db');normal('foreign-zero',q.D/'foreign-zero-True.db');normal('legacy-v1',q.D/'legacy-real-1.db');normal('legacy-v2',q.D/'legacy-real-2.db')
  marker=q.D/'cli-marker.db';q.sql(marker,"create table Marker (id INTEGER PRIMARY KEY, value TEXT);insert into Marker values(1,'NO_CHANGE');");before=q.truth(marker)
  normal('old-test-cli',flags=['--test-pipeline-e1','--db',str(marker)]);normal('old-crash-cli',flags=['--crash-worker','--db',str(marker),'--scope','ATTACK','--fault','AfterCommitted']);q.record('old-cli-marker',{'unchanged':before==q.truth(marker)})
  # Idempotency across rotation: use the actual pre-rotation command envelope.
  old=json.loads(next(q.E.glob('OLD_LATE-*.request.json')).read_text(encoding='utf-8'));old['OperationId']='OP';old['ProbeScopeId']='S';p=q.E/'old-retry.request.json';q.f.write(p,old);q.run('execute',q.D/'incarnation.db','old-receipt-non-authorizing',request=p)
  # Same-ID JSON replay/collision through actual dispatcher, not only canonicalizer.
  db=q.fresh('json-retry');q.execute(db,'json-first',PayloadJson='{"b":2,"a":1}');q.execute(db,'json-reordered-retry',PayloadJson='{"a":1,"b":2}')
  db=q.fresh('array-retry');q.execute(db,'array-first',PayloadJson='[1,2]');q.execute(db,'array-reorder-reject',PayloadJson='[2,1]')
  db=q.fresh('numeric-retry');q.execute(db,'numeric-first',PayloadJson='1.0000000000000001');q.execute(db,'numeric-distinct-retry',PayloadJson='1.0')
  db=q.fresh('numeric-infinity');q.execute(db,'infinity-number-first',PayloadJson='{"n":1e309}');q.execute(db,'infinity-string-retry',PayloadJson='{"n":"Infinity"}')
  # Corrupt committed receipt/event/audit state in valid SQLite. Reconciler claims consistency.
  base=q.D/'same-stream.db'
  for name,s in {'receipt-revision':"update CommitReceipts set CommittedRevision=999",'receipt-hash':"update CommitReceipts set ReceiptHash='tampered'",'event-payload':"update PublicationEvents set CanonicalPayload='false'",'event-principal-state':"update PublicationEvents set EventType='UNRELATED'",'missing-audit':"delete from AuditRecords",'missing-history':"delete from ProbeRevisionHistory"}.items():
   db=q.clone(base,q.D/('consistency-'+name+'.db'));q.sql(db,s);q.run('startup',db,'consistency-'+name)
  # Real legacy WAL-containing copies, observe all logical rows plus main/WAL/SHM.
  for ver in [1,2]:
   db=q.clone(q.D/('legacy-real-'+str(ver)+'.db'),q.D/('legacy-wal-'+str(ver)+'.db'));c=q.conn(db);c.execute('pragma journal_mode=WAL');col=next(r[1] for r in c.execute('pragma table_info(AuditRecords)') if r[1] in ['TimestampEpochMs','TimestampUtc','Timestamp'])
   c.execute('update AuditRecords set "'+col+'"="'+col+'"');c.execute('pragma user_version='+str(ver));c.commit();before=q.truth(db)
   def files():return {str(x):{'sha256':q.f.sha(x),'bytes':x.stat().st_size} for x in [db,Path(str(db)+'-wal'),Path(str(db)+'-shm')] if x.exists()}
   b=files();q.run('startup',db,'legacy-wal-'+str(ver));q.record('legacy-wal-'+str(ver)+'-preservation',{'logicalUnchanged':before==q.truth(db),'beforeFiles':b,'afterFiles':files()});c.close()
  q.check()
 finally:
  q.STOP.set()
  for p in q.OWNED:
   if p.poll() is None:p.kill();p.wait()
  after=q.f.tree();q.f.write(q.Q/'freeze-after.json',after);before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('freeze-supplement',{'changes':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)],'count':len(after)})
if __name__=='__main__':main()
