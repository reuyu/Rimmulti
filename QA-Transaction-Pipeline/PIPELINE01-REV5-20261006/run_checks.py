from pathlib import Path
import json,sqlite3,subprocess,time,shutil,threading,hashlib,collections,socket,struct
import setup as f
Q=f.Q;R=f.R;E=Q/'Evidence';D=Q/'DBs';H=Q/'Harness/bin/Release/net8.0/Harness.dll';RESULTS={};OWNED=[];STOP=threading.Event();INVALID=[]
def save(): f.write(E/'results.json',RESULTS)
def record(k,v): RESULTS[k]=v;save();print(k,json.dumps(v,ensure_ascii=True)[:750],flush=True)
def check():
 b=json.loads((Q/'freeze-before.json').read_text(encoding='utf-8'));now=f.tree();diff=[p for p in set(b)|set(now) if b.get(p)!=now.get(p)]
 if diff: INVALID.extend(diff);f.write(E/'freeze-invalid.json',diff);raise RuntimeError('Frozen Production tree changed')
def watch():
 while not STOP.wait(15):
  try:check()
  except Exception:
   for p in list(OWNED):
    if p.poll() is None:p.kill()
   return
def run(mode,db,label=None,timeout=35,**opts):
 if INVALID:raise RuntimeError('Candidate invalidated')
 cmd=['dotnet',str(H),mode,str(db)]+[str(x) for k,v in opts.items() for x in ['--'+k.replace('_','-'),v]]
 p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',cwd=Q,creationflags=subprocess.CREATE_NO_WINDOW);OWNED.append(p)
 try:o,err=p.communicate(timeout=timeout)
 except subprocess.TimeoutExpired:p.kill();o,err=p.communicate();record(label or mode,{'timeout':True,'stdout':o,'stderr':err});return None
 rows=[]
 for l in o.splitlines():
  try:rows.append(json.loads(l))
  except ValueError:pass
 out={'pid':p.pid,'exit':p.returncode,'rows':rows,'stdout':o,'stderr':err};record(label or mode,out);return rows[-1] if rows else None
def conn(db): return sqlite3.connect(db,timeout=15)
def sql(db,s):
 with conn(db) as c:c.executescript(s)
def truth(db):
 with conn(db) as c:
  names=[r[0] for r in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
  return {'version':c.execute('pragma user_version').fetchone()[0],'app':c.execute('pragma application_id').fetchone()[0],'schema':c.execute('select type,name,tbl_name,sql from sqlite_master order by type,name').fetchall(),'tables':{n:c.execute('select * from "'+n.replace('"','""')+'"').fetchall() for n in names}}
def clone(source,dest):
 with conn(source) as a,conn(dest) as b:a.backup(b)
 return dest
def fresh(name):
 db=D/(name+'.db')
 if db.exists():
  with conn(db) as c:assert c.execute('pragma user_version').fetchone()[0]==0 and not c.execute("select name from sqlite_master where type='table'").fetchall()
 run('init',db,name+'-init');return db
def req(db,name='OP',scope='S',principal='P',expected=0,**changes):
 with conn(db) as c:inc=c.execute('select IncarnationId from StoreIncarnations where IsActive=1').fetchone()[0]
 x={'PrincipalId':principal,'OperationId':name,'ProbeScopeId':scope,'ExpectedProbeRevision':expected,'StoreIncarnationId':inc,'PayloadJson':'{"a":1}','ContentProfileFingerprint':'PROFILE'};x.update(changes)
 p=E/(name+'-'+str(time.time_ns())+'.request.json');f.write(p,x);return p
def execute(db,label,**changes): return run('execute',db,label,request=req(db,**changes))
def spawn(mode,db,label,**opts):
 log=open(E/(label+'.stdout'),'w',encoding='utf-8');cmd=['dotnet',str(H),mode,str(db)]+[str(x) for k,v in opts.items() for x in ['--'+k.replace('_','-'),v]]
 p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=Q,creationflags=subprocess.CREATE_NO_WINDOW);OWNED.append(p);return p,log
def barrier(path,p,seconds=15):
 end=time.monotonic()+seconds
 while not path.exists() and time.monotonic()<end:
  if p.poll() is not None:raise RuntimeError('process exited before barrier')
  time.sleep(.01)
 if not path.exists():raise TimeoutError(path)
def fingerprint_identity():
 if 'fingerprint-matrix' not in RESULTS:
  db=fresh('fingerprints');run('fingerprints',db,'fingerprint-matrix');run('meta',db,'metadata');run('pool',db,'pooled-durability')
 db=fresh('identity');base=req(db)
 run('execute',db,'identity-first',request=base);run('execute',db,'identity-retry',request=base)
 original=json.loads(base.read_text(encoding='utf-8'))
 for field,v in {'ProbeScopeId':'OTHER','ExpectedProbeRevision':1,'ContentProfileFingerprint':'OTHER','ConfigSnapshotRef':'OTHER','OperationType':'OTHER','OperationSchemaVersion':2,'PayloadJson':'{"a":2}'}.items():
  x=original|{field:v};p=E/(field+'.request.json');f.write(p,x);run('execute',db,'collision-'+field,request=p)
 execute(db,'identity-different-principal',principal='P2',scope='S2')
 f.write(E/'identity.truth.json',truth(db))
 run('immutable',fresh('immutable'),'immutable-admission')
 for culture in ['en-US','ko-KR','ar-SA','fr-FR','tr-TR']:run('receipt',db,'receipt-'+culture,culture=culture)
def concurrency():
 for kind,n in [('cas',25),('same-id',12)]:
  db=fresh(kind);procs=[]
  for i in range(n):
   p,log=spawn('execute',db,kind+str(i),request=req(db,name='OP' if kind=='same-id' else 'OP'+str(i)));procs.append((p,log,kind+str(i)))
  rows=[]
  for p,log,label in procs:
   p.wait(timeout=35);log.close();s=(E/(label+'.stdout')).read_text(encoding='utf-8');rows += [json.loads(l) for l in s.splitlines() if l.startswith('{')]
  f.write(E/(kind+'.process-results.json'),rows);record(kind+'-summary',{'processes':n,'outcomes':collections.Counter(x.get('result',{}).get('Status',x.get('status')) for x in rows),'truth':truth(db)})
 # Same stream with independent process/connection writers; revision losers retry with a new operation ID.
 db=fresh('same-stream');success=0;attempt=0;allrows=[]
 for round in range(8):
  with conn(db) as c:
   row=c.execute('select ProbeRevision from ProbeAggregates where ProbeScopeId="S"').fetchone();rev=row[0] if row else 0
  procs=[]
  for i in range(6):
   label=f'stream-{round}-{i}';p,log=spawn('execute',db,label,request=req(db,name=label,expected=rev));procs.append((p,log,label))
  for p,log,label in procs:
   p.wait(timeout=35);log.close();allrows += [json.loads(l) for l in (E/(label+'.stdout')).read_text(encoding='utf-8').splitlines() if l.startswith('{')]
 run('read',db,'events-page1',scope='S',after=0,limit=3);run('read',db,'events-page2',scope='S',after=3,limit=3);run('read',db,'events-page-restart',scope='S',after=0,limit=100)
 record('same-stream-summary',{'processes':48,'outcomes':collections.Counter(x.get('result',{}).get('Status') for x in allrows),'truth':truth(db)});f.write(E/'same-stream.process-results.json',allrows)
def terminal_and_fence():
 db=fresh('terminal');execute(db,'terminal-commit');execute(db,'terminal-abort',name='ABORT',expected=0)
 original=truth(db);attempts=[]
 for op in ['OP','ABORT']:
  for kind,s in [('update',f"UPDATE OperationRecords SET PayloadJson='tampered' WHERE OperationId='{op}'"),('delete',f"DELETE FROM OperationRecords WHERE OperationId='{op}'"),('upsert',f"INSERT INTO OperationRecords SELECT * FROM OperationRecords WHERE OperationId='{op}' ON CONFLICT(PrincipalId,OperationId) DO UPDATE SET PayloadJson='tampered'")]:
   with conn(db) as c:
    try:c.execute(s);c.commit();attempts.append({'op':op,'kind':kind,'allowed':True})
    except sqlite3.Error as ex:attempts.append({'op':op,'kind':kind,'allowed':False,'error':str(ex)})
  with conn(db) as c:
   columns=[r[1] for r in c.execute('pragma table_info(OperationRecords)')];expressions=["'tampered'" if n=='PayloadJson' else '"'+n+'"' for n in columns];s='INSERT OR REPLACE INTO OperationRecords SELECT '+','.join(expressions)+f" FROM OperationRecords WHERE OperationId='{op}'"
   try:c.execute(s);c.commit();attempts.append({'op':op,'kind':'replace','allowed':True,'recursiveTriggers':c.execute('pragma recursive_triggers').fetchone()[0]})
   except sqlite3.Error as ex:attempts.append({'op':op,'kind':'replace','allowed':False,'error':str(ex)})
 record('terminal-sql',{'attempts':attempts,'before':original,'after':truth(db)});run('startup',db,'terminal-replaced-startup')
 db=fresh('incarnation');execute(db,'incarnation-first');old=req(db,name='OLD_LATE',scope='NEW');signal=E/'admitted.signal';p,log=spawn('admitted',db,'fence-admitted',request=old,signal=signal);barrier(signal,p);run('rotate',db,'rotation-separate-process',new_id='ROTATED_QA');p.wait(timeout=20);log.close();record('fence-old-admitted',{'stdout':(E/'fence-admitted.stdout').read_text(encoding='utf-8'),'truth':truth(db)})
 run('startup',db,'rotation-restart');run('historical',db,'historical-old-receipt');run('execute',db,'old-incarnation-retry',request=E/'neverexists') if False else None
 record('incarnation-truth',truth(db))
def storage_kills():
 for table in ['ProbeAggregates','CommitReceipts','PublicationEvents','AuditRecords']:
  db=fresh('constraint-'+table);sql(db,f"CREATE TRIGGER qa_constraint BEFORE INSERT ON {table} BEGIN SELECT RAISE(ABORT,'QA constraint failure'); END;")
  r=execute(db,'storage-constraint-'+table);record('storage-truth-'+table,truth(db))
 for point in ['before-cas','before-receipt','before-event','before-audit']:
  db=fresh('io-'+point);run('execute',db,'io-'+point,request=req(db),inject=point);record('io-truth-'+point,truth(db))
 db=fresh('native-locked');sql(db,'CREATE TABLE QA_Lock (v INTEGER);INSERT INTO QA_Lock VALUES(1);INSERT INTO QA_Lock VALUES(2);');run('execute',db,'native-locked',request=req(db),inject='native-locked');record('locked-truth',truth(db))
 db=fresh('busy');c=conn(db);c.execute('BEGIN IMMEDIATE');run('execute',db,'native-busy',request=req(db),timeout=18);c.rollback();c.close();record('busy-truth',truth(db))
 for point in ['after-cas','after-receipt','after-event','after-audit','native-commit','after-return']:
  db=fresh('kill-'+point);request=req(db);signal=E/(point+'.signal');release=E/(point+'.release');p,log=spawn('execute',db,'kill-'+point,request=request,point=point,signal=signal,release=release);barrier(signal,p);p.kill();p.wait();log.close();before=truth(db);run('startup',db,'restart-'+point);run('execute',db,'retry-'+point,request=request);record('kill-boundary-'+point,{'killPID':p.pid,'durableBeforeRetry':before,'afterRetry':truth(db)})
def rebuild_table(db,table,change):
 with conn(db) as c:
  c.execute('PRAGMA foreign_keys=OFF');ddl=c.execute('select sql from sqlite_master where type="table" and name=?',(table,)).fetchone()[0];dependent=c.execute('select sql from sqlite_master where tbl_name=? and type in ("index","trigger") and sql is not null',(table,)).fetchall();rows=c.execute('select * from '+table).fetchall();c.execute('DROP TABLE '+table);c.execute(change(ddl))
  for row in rows:c.execute('insert into '+table+' values('+','.join('?' for _ in row)+')',row)
  for (s,) in dependent:c.execute(s)
def schema_cases():
 base=fresh('schema-base');cases={
 'wrong-app':lambda d:sql(d,'pragma application_id=123'),
 'zero-app-v3':lambda d:sql(d,'pragma application_id=0'),
 'future-version':lambda d:sql(d,'pragma user_version=7'),
 'missing-table':lambda d:sql(d,'drop table AuditRecords'),
 'missing-column':lambda d:rebuild_table(d,'AuditRecords',lambda s:s.replace('DetailsJson TEXT,','')),
 'wrong-type':lambda d:rebuild_table(d,'ProbeAggregates',lambda s:s.replace('ProbeRevision INTEGER','ProbeRevision TEXT')),
 'wrong-nullable':lambda d:rebuild_table(d,'ProbeAggregates',lambda s:s.replace('ProbeRevision INTEGER NOT NULL','ProbeRevision INTEGER')),
 'wrong-pk-order':lambda d:rebuild_table(d,'OperationRecords',lambda s:s.replace('PRIMARY KEY (PrincipalId, OperationId)','PRIMARY KEY (OperationId, PrincipalId)')),
 'missing-stream-unique':lambda d:rebuild_table(d,'PublicationEvents',lambda s:s.replace('UNIQUE (StreamId, Seq),','')),
 'wrong-stream-unique':lambda d:rebuild_table(d,'PublicationEvents',lambda s:s.replace('UNIQUE (StreamId, Seq)','UNIQUE (StreamId, EventType)')),
 'wrong-event-pk':lambda d:rebuild_table(d,'PublicationEvents',lambda s:s.replace('EventId TEXT PRIMARY KEY NOT NULL','EventId TEXT NOT NULL')),
 'missing-fk':lambda d:rebuild_table(d,'CommitReceipts',lambda s:s.replace(',\n                        FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId) ON UPDATE NO ACTION ON DELETE RESTRICT','')),
 'wrong-fk-columns':lambda d:rebuild_table(d,'CommitReceipts',lambda s:s.replace('FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId)','FOREIGN KEY (ProbeScopeId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId)')),
 'wrong-fk-actions':lambda d:rebuild_table(d,'CommitReceipts',lambda s:s.replace('ON DELETE RESTRICT','ON DELETE CASCADE')),
 'missing-check':lambda d:rebuild_table(d,'ProbeAggregates',lambda s:s.replace(' CHECK (ProbeRevision >= 0)','')),
 'wrong-check':lambda d:rebuild_table(d,'OperationRecords',lambda s:s.replace("CHECK (State IN ('COMMITTED', 'ABORTED'))","CHECK (State IN ('COMMITTED', 'ABORTED', 'PREPARED'))")),
 'missing-trigger':lambda d:sql(d,'drop trigger trg_operation_records_no_update'),
 'noop-trigger':lambda d:sql(d,'drop trigger trg_operation_records_no_update;create trigger trg_operation_records_no_update BEFORE UPDATE ON OperationRecords BEGIN SELECT 1;END'),
 'missing-index':lambda d:sql(d,'drop index IX_PublicationEvents_Stream_Seq'),
 'wrong-index':lambda d:sql(d,'drop index IX_PublicationEvents_Stream_Seq;create index IX_PublicationEvents_Stream_Seq on PublicationEvents(EventType)'),
 'zero-active':lambda d:sql(d,'update StoreIncarnations set IsActive=0'),
 'multiple-active':lambda d:sql(d,"insert into StoreIncarnations values('SECOND',1,0,null)")}
 for name,edit in cases.items():
  db=clone(base,D/('schema-'+name+'.db'));edit(db)
  with conn(db) as c:ok=c.execute('pragma integrity_check').fetchone()[0]
  before=truth(db);r=run('startup',db,'schema-'+name);record('schema-'+name+'-summary',{'integrity':ok,'ready':r is not None and r.get('ready')==True,'canonicalUnchanged':before==truth(db)})
 # Nonempty foreign zero-identity and empty unrelated schema both remain foreign, not fresh.
 for has_data in [True,False]:
  db=D/('foreign-zero-'+str(has_data)+'.db');sql(db,'create table CustomerSecret (id integer primary key, secret text);'+("insert into CustomerSecret values(1,'preserve')" if has_data else ''));before=truth(db);run('startup',db,'foreign-zero-'+str(has_data));record('foreign-zero-'+str(has_data)+'-truth',{'unchanged':before==truth(db),'before':before,'after':truth(db)})
 for version,folder in [(1,'PIPELINE01-20261002'),(2,'PIPELINE01-REV1-20261003'),(3,'PIPELINE01-REV2-20261003')]:
  source=R/'QA-Transaction-Pipeline'/folder/'Evidence/identity.db'
  if not source.exists():source=R/'QA-Transaction-Pipeline'/folder/('DBs/identity.db' if version==3 else 'Evidence/fingerprints.db')
  db=clone(source,D/('legacy-real-'+str(version)+'.db'));before=truth(db);run('startup',db,'legacy-real-'+str(version));record('legacy-real-'+str(version)+'-truth',{'source':str(source),'sourceSha':f.sha(source),'actualVersion':before['version'],'unchanged':before==truth(db),'logicalBefore':before,'logicalAfter':truth(db)})
def main():
 if (E/'results.json').exists():RESULTS.update(json.loads((E/'results.json').read_text(encoding='utf-8')))
 check();threading.Thread(target=watch,daemon=True).start()
 shutil.copy2(R/'QA_DEFECT_LEDGER_QDL-047.md',Q/'FrozenSource/QA_DEFECT_LEDGER_QDL-047.md')
 try:
  fingerprint_identity();check();concurrency();check();terminal_and_fence();check();storage_kills();check();schema_cases();check();run('queue',fresh('shutdown-queue'),'bounded-shutdown',timeout=28,n=1205)
 finally:
  STOP.set()
  for p in OWNED:
   if p.poll() is None:p.kill();p.wait()
  after=f.tree();f.write(Q/'freeze-after.json',after);before=json.loads((Q/'freeze-before.json').read_text(encoding='utf-8'));record('freeze-final',{'changes':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)],'count':len(after)})
if __name__=='__main__':main()
