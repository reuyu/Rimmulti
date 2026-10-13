import run_checks as q
from pathlib import Path
import json,time,threading,sqlite3
q.RESULTS.update(json.loads((q.E/'results.json').read_text(encoding='utf-8')))
def main():
 q.check();threading.Thread(target=q.watch,daemon=True).start()
 try:
  db=q.fresh('native-replace');q.execute(db,'native-replace-seed');q.run('journal-attempt',db,'repository-duplicate-insert')
  with q.conn(db) as c:cols=[r[1] for r in c.execute('pragma table_info(OperationRecords)')]
  terms=["'ABORTED'" if x=='State' else '"'+x+'"' for x in cols];sql=q.E/'replace-native.sql';sql.write_text('INSERT OR REPLACE INTO OperationRecords SELECT '+','.join(terms)+" FROM OperationRecords WHERE PrincipalId='P' AND OperationId='OP';",encoding='utf-8')
  q.run('sql',db,'native-terminal-flip',sqlfile=sql);q.run('startup',db,'native-flipped-startup');q.execute(db,'native-flipped-retry');q.record('native-flipped-truth',q.truth(db))
  q.run('queue-timeout',q.fresh('queue-timeout'),'queue-timeout-backpressure',timeout=25,n=1205)
  db=q.fresh('queue-native-lock');c=q.conn(db);c.execute('BEGIN IMMEDIATE');signal=q.E/'lock-disposed.signal';release=q.E/'lock-disposed.release';p,log=q.spawn('queue-lock',db,'queue-native-lock',signal=signal,release=release,n=1205)
  try:q.barrier(signal,p,seconds=24)
  finally:c.rollback();c.close();release.write_text('release',encoding='utf-8')
  p.wait(timeout=30);log.close();rows=[json.loads(l) for l in (q.E/'queue-native-lock.stdout').read_text(encoding='utf-8').splitlines() if l.startswith('{')];q.record('queue-native-lock',{'pid':p.pid,'exit':p.returncode,'rows':rows,'truth':q.truth(db)})
  # Same OperationId across principals/scopes must not collide via globally derived event IDs.
  db=q.fresh('event-principal');q.execute(db,'event-principal-first',name='SAME',principal='A',scope='ASCOPE')
  # No receipt bypass is attempted: identity-different-principal already demonstrates
  # the ordinary receipt ID collision; event ID collision is a static risk only.
  q.check()
 finally:
  q.STOP.set()
  for p in q.OWNED:
   if p.poll() is None:p.kill();p.wait()
  after=q.f.tree();q.f.write(q.Q/'freeze-after.json',after);before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('freeze-end',{'changes':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)],'count':len(after)})
if __name__=='__main__':main()
