from pathlib import Path
import subprocess,json,sqlite3,time,hashlib,re,collections,shutil,os
QA=Path(__file__).parent.resolve();ROOT=QA.parent.parent;DATA=QA/'Evidence';DATA.mkdir(exist_ok=True)
DOTNET=r'C:\Program Files\dotnet\dotnet.exe';HAR=QA/'Harness/bin/Debug/net8.0/Harness.dll';RESULTS={}
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def request(name,**changes):
 d=dict(PrincipalId='P_A',OperationId='OP',ProbeScopeId='SCOPE',ExpectedProbeRevision=0,PayloadJson='{"a":1,"b":2}',ContentProfileFingerprint='PROFILE_A',ConfigSnapshotRef='CONFIG_A');d.update(changes)
 p=DATA/(name+'.request.json');write(p,d);return p
def args(mode,db,**opts):
 a=[DOTNET,str(HAR),mode,str(db)]
 for k,v in opts.items():a+=['--'+k.replace('_','-'),str(v)]
 return a
def run(mode,db,name,**opts):
 env=os.environ.copy()
 if 'tz' in opts:env['TZ']=str(opts.pop('tz'))
 p=subprocess.run(args(mode,db,**opts),capture_output=True,text=True,encoding='utf-8',timeout=65,env=env)
 (DATA/(name+'.stdout.txt')).write_text(p.stdout+'\nSTDERR:\n'+p.stderr,encoding='utf-8')
 try:r=json.loads(p.stdout.strip().splitlines()[-1])
 except:r={'status':'UNPARSEABLE','stdout':p.stdout,'stderr':p.stderr}
 r['exitCode']=p.returncode;return r
def init(name):
 db=DATA/(name+'.db');assert not db.exists(),name
 r=run('init',db,name+'-init');assert r['exitCode']==0,r
 return db
def sql(db,query,values=()):
 with sqlite3.connect(db) as c:return c.execute(query,values).fetchall()
def state(db):
 out={'path':str(db)}
 with sqlite3.connect(db) as c:
  c.row_factory=sqlite3.Row
  for t in ['StoreIncarnations','ProbeAggregates','ProbeRevisionHistory','OperationRecords','CommitReceipts','AuditRecords','PublicationEvents','ConsumerCursors','ConsumerDurableAcks']:
   try:out[t]=[dict(r) for r in c.execute('select * from '+t)]
   except Exception as e:out[t]={'error':str(e)}
  out['schema']=c.execute('pragma user_version').fetchone()[0];out['applicationId']=c.execute('pragma application_id').fetchone()[0]
 return out
def record(k,v):RESULTS[k]=v;write(DATA/'results.json',RESULTS);print(k,json.dumps(v,ensure_ascii=False)[:750],flush=True)
def checkpoint(db,name,point,mode='execute',**opts):
 sig=DATA/(name+'.signal');release=DATA/(name+'.release');out=open(DATA/(name+'.process.txt'),'w',encoding='utf-8')
 p=subprocess.Popen(args(mode,db,point=point,signal=sig,release=release,**opts),stdout=out,stderr=subprocess.STDOUT);deadline=time.monotonic()+35
 while not sig.exists():
  if p.poll() is not None:raise RuntimeError((name,p.returncode,(DATA/(name+'.process.txt')).read_text(encoding='utf-8')))
  if time.monotonic()>deadline:p.kill();p.wait();out.close();raise TimeoutError(name)
  time.sleep(.005)
 return p,out,sig,release
def kill(db,name,point,**opts):
 p,out,sig,release=checkpoint(db,name,point,**opts);signal=json.loads(sig.read_text());p.kill();p.wait(timeout=10);out.close()
 return {'signal':signal,'OSKillExitCode':p.returncode,'dbBefore':state(db)}
def ledger(db):
 if not db.exists():return {'effects':0,'balance':0}
 with sqlite3.connect(db) as c:
  return {'effects':c.execute('select count(*) from Ledger').fetchone()[0],'balance':c.execute('select coalesce(sum(Value),0) from Balances').fetchone()[0], 'entries':c.execute('select ConsumerId,EventId,Seq,StreamId,Fingerprint,Payload from Ledger').fetchall()}

if __name__=='__main__':
 db=init('meta');record('metadata',run('meta',db,'metadata'));record('pooled-durability',run('pool',db,'pooled-durability'))
 db=init('identity');req=request('identity');first=run('execute',db,'identity-first',request=req);tests={}
 for key,value in [('ProbeScopeId','OTHER_SCOPE'),('ExpectedProbeRevision',99),('ContentProfileFingerprint','PROFILE_B'),('OperationType','OTHER_TYPE'),('OperationSchemaVersion',2),('ConfigSnapshotRef','CONFIG_B'),('PayloadJson','{"a":999}')]:
  tests[key]=run('execute',db,'identity-'+key,request=request('identity-'+key,**{key:value}))
 tests['canonical-payload']=run('execute',db,'identity-reordered',request=request('identity-reordered',PayloadJson=' { "b":2, "a":1 } '))
 tests['fake-hash-different-payload']=run('execute',db,'identity-fakehash',request=request('identity-fakehash',PayloadJson='{"a":999}',CallerSuppliedPayloadHash='ORIGINAL_FINGERPRINT'))
 tests['different-principal']=run('execute',db,'identity-other-principal',request=request('identity-other-principal',PrincipalId='P_B',ProbeScopeId='PRINCIPAL_B_SCOPE'))
 record('identity',{'first':first,'tests':tests,'db':state(db)})
 db=init('delimiter');r1=request('delimiter-first',ContentProfileFingerprint='PROFILE|EXTRA',ConfigSnapshotRef='CONFIG');r2=request('delimiter-second',ContentProfileFingerprint='PROFILE',ConfigSnapshotRef='EXTRA|CONFIG')
 record('delimiter-collision',{'first':run('execute',db,'delimiter-first',request=r1),'changedEnvelope':run('execute',db,'delimiter-second',request=r2),'db':state(db)})
 for kind,n in [('different-id-race',25),('same-id-race',12)]:
  db=init(kind);start=DATA/(kind+'.start');ps=[];outs=[]
  for i in range(n):
   name=kind+'-'+str(i);req=request(name,OperationId='OP' if kind=='same-id-race' else 'OP_'+str(i));out=open(DATA/(name+'.process.txt'),'w',encoding='utf-8');outs.append(out)
   ps.append(subprocess.Popen(args('execute',db,request=req,start=start,ready=DATA/(name+'.ready')),stdout=out,stderr=subprocess.STDOUT))
  end=time.monotonic()+35
  while not all((DATA/(kind+'-'+str(i)+'.ready')).exists() for i in range(n)):
   if time.monotonic()>end:raise TimeoutError(kind)
   time.sleep(.01)
  start.write_text('start');begin=time.monotonic()
  for p,o in zip(ps,outs):p.wait(timeout=35);o.close()
  results=[json.loads((DATA/(kind+'-'+str(i)+'.process.txt')).read_text(encoding='utf-8').strip().splitlines()[-1]) for i in range(n)]
  record(kind,{'workers':n,'summary':dict(collections.Counter(x.get('result',{}).get('Status',x['status']) for x in results)),'elapsedMs':(time.monotonic()-begin)*1000,'results':results,'db':state(db)})
 db=init('aborted');req=request('aborted',ExpectedProbeRevision=5)
 record('aborted',{'first':run('execute',db,'aborted-first',request=req),'exactRetry':run('execute',db,'aborted-retry',request=req),'changed':run('execute',db,'aborted-changed',request=request('aborted-changed',ExpectedProbeRevision=0)),'newId':run('execute',db,'aborted-new',request=request('aborted-new',OperationId='NEW_OP')),'db':state(db)})
 # Proper incarnation rotation/restart and old receipt historical lookup.
 db=init('incarnation');old=sql(db,'select IncarnationId from StoreIncarnations where IsActive=1')[0][0];req=request('incarnation',StoreIncarnationId=old)
 first=run('execute',db,'incarnation-first',request=req);rotation=run('rotate',db,'incarnation-rotate');new=rotation['incarnation']
 record('incarnation',{'old':old,'new':new,'first':first,'rotation':rotation,'staleRetry':run('execute',db,'incarnation-stale',request=req),'historicalReceipt':run('receipt',db,'incarnation-historical'),'newRetry':run('execute',db,'incarnation-new-retry',request=request('incarnation-new-retry',StoreIncarnationId=new)),'newMutation':run('execute',db,'incarnation-new-mutation',request=request('incarnation-new-mutation',OperationId='NEW',ExpectedProbeRevision=1,StoreIncarnationId=new)),'restart':run('validate',db,'incarnation-restart'),'db':state(db)})
 # Full actual kill boundary battery, including consumer-side durable effect/ACK/cursor windows.
 points=['before-lookup','before-cas','after-cas','after-record','after-receipt','after-audit','after-event','before-commit','native-commit','after-commit','after-consumer-effect','after-server-ack','before-cursor','after-cursor']
 for point in points:
  name='kill-'+point;db=init(name);req=request(name);consumerDB=DATA/(name+'.consumer.db')
  result=kill(db,name,point,request=req,consumer='fixture',consumer_db=consumerDB)
  result['consumerBefore']=ledger(consumerDB);result['restart']=run('recover',db,name+'-restart',consumer='fixture',consumer_db=consumerDB)
  result['consumerAfter']=ledger(consumerDB);result['retry']=run('execute',db,name+'-retry',request=req,consumer='fixture',consumer_db=consumerDB)
  result['recoveryAgain']=run('recover',db,name+'-again',consumer='fixture',consumer_db=consumerDB);result['dbAfter']=state(db)
  record(name,result)
 # Contract example proves interface can support dedup but does not silently fix candidate.
 db=init('qa-persistent-contract');cdb=DATA/'qa-persistent-contract.consumer.db';req=request('qa-persistent-contract')
 result=kill(db,'qa-persistent-contract','after-consumer-effect',request=req,consumer='persistent',consumer_db=cdb)
 result['restart']=run('recover',db,'qa-persistent-contract-restart',consumer='persistent',consumer_db=cdb);result['consumer']=ledger(cdb);record('qa-persistent-contract',result)
 # Changed payload same EventId: actual consumer does not recompute supplied fingerprint.
 event=state(db)['PublicationEvents'][0];wrong=dict(event,PayloadJson='{"changed":true}')
 ep=DATA/'tampered-event.json';write(ep,wrong)
 fixtureDB=DATA/'fixture-tamper.consumer.db'
 record('payload-mismatch',{'fixtureWithOriginalFingerprint':run('consumer-event',db,'fixture-payload-mismatch',event=ep,consumer='fixture',consumer_db=fixtureDB),'fixtureEffects':ledger(fixtureDB),'QAContractReject':run('consumer-event',db,'persistent-payload-mismatch',event=ep,consumer='persistent',consumer_db=cdb)})
 # Live writer vs simultaneous convergence must not alter committed operation.
 db=init('live-convergence');req=request('live-convergence');p,o,sig,release=checkpoint(db,'live-convergence','after-commit',request=req)
 recovery=run('recover',db,'live-convergence-recover');release.write_text('release');p.wait(timeout=10);o.close()
 record('live-convergence',{'recovery':recovery,'db':state(db),'retry':run('execute',db,'live-convergence-retry',request=req)})
 # Stream replay ordering, rejection, lag and startup must evaluate remaining work, not just one 50-row page.
 for consumer in ['throw-first','false-first']:
  name='stream-'+consumer;db=init(name);cdb=DATA/(name+'.consumer.db');req=request(name)
  run('bulk',db,name+'-seed',request=req,count=3)
  r=run('dispatch',db,name+'-dispatch',consumer=consumer,consumer_db=cdb)
  after=state(db);r2=run('dispatch',db,name+'-retry',consumer='persistent',consumer_db=cdb)
  record(name,{'dispatch':r,'afterFirst':after,'retry':r2,'effects':ledger(cdb),'after':state(db)})
 db=init('live-stream-gap');cdb=DATA/'live-stream-gap.consumer.db'
 first=run('execute',db,'live-stream-gap-first',request=request('live-stream-gap-first'),consumer='throw-first',consumer_db=cdb)
 second=run('execute',db,'live-stream-gap-second',request=request('live-stream-gap-second',OperationId='OP2',ExpectedProbeRevision=1),consumer='throw-first',consumer_db=cdb)
 r=run('dispatch',db,'live-stream-gap-retry',consumer='persistent',consumer_db=cdb)
 record('live-stream-gap',{'first':first,'second':second,'retry':r,'db':state(db),'effects':ledger(cdb)})
 db=init('two-consumers');cdb=DATA/'two-consumers.consumer.db';run('bulk',db,'two-consumers-seed',request=request('two-consumers'),count=3)
 a=run('dispatch',db,'two-consumers-A',consumer='persistent',consumer_db=cdb,consumer_id='A');beforeB=state(db)
 b=run('dispatch',db,'two-consumers-B',consumer='persistent',consumer_db=cdb,consumer_id='B')
 record('two-consumers',{'A':a,'beforeB':beforeB,'B':b,'after':state(db),'effects':ledger(cdb)})
 for count,consumer in [(1,'throw'),(1,'persistent'),(65,'persistent')]:
  name=f'startup-{count}-{consumer}';db=init(name);cdb=DATA/(name+'.consumer.db');run('bulk',db,name+'-seed',request=request(name),count=count)
  result=run('startup',db,name,consumer=consumer,consumer_db=cdb)
  record(name,{'startup':result,'after':state(db),'effects':ledger(cdb)})
 # Logical schema negative fixtures; no production data modified.
 malformed=[('wrong-app','pragma application_id=42'),('future-version','pragma user_version=999'),('missing-table','drop table ConsumerDurableAcks'),('missing-op-column','alter table OperationRecords drop column OperationType'),('missing-receipt-column','alter table CommitReceipts drop column ReceiptHash'),('missing-index','drop index IX_OperationRecords_Scope'),('multiple-active',"insert into StoreIncarnations values('EXTRA_ACTIVE',1,1,NULL)")]
 for label,query in malformed:
  name='schema-'+label;db=init(name);sql(db,query);record(name,{'validate':run('validate',db,name),'startup':run('startup',db,name+'-startup'),'db':state(db)})
 # Alter material constraints without removing table/columns. SQLite writable_schema is QA corruption injection.
 for label,table,old,new in [('no-pk','OperationRecords','PRIMARY KEY (PrincipalId, OperationId)',''),('no-state-check','OperationRecords',"CHECK (State IN ('COMMITTED', 'ABORTED'))",''),('no-event-unique','PublicationEvents','EventId TEXT NOT NULL UNIQUE','EventId TEXT NOT NULL'),('no-fk','CommitReceipts','FOREIGN KEY (PrincipalId, OperationId) REFERENCES OperationRecords(PrincipalId, OperationId)','')]:
  name='schema-'+label;db=init(name)
  with sqlite3.connect(db) as c:
   ddl=c.execute('select sql from sqlite_master where name=?',(table,)).fetchone()[0]
   changed=ddl.replace(old,new)
   if new=='':changed=changed.replace(',\n                        \n', '\n').replace(',\n                    )','\n                    )')
   c.execute('pragma writable_schema=ON');c.execute('update sqlite_master set sql=? where name=?',(changed,table));v=c.execute('pragma schema_version').fetchone()[0];c.execute(f'pragma schema_version={v+1}')
  record(name,{'originalDDL':ddl,'changedDDL':changed,'validate':run('validate',db,name),'startup':run('startup',db,name+'-startup')})
 # Genuine original v1 durable data: copy QA REV0 DB via SQLite backup, not live file copying.
 rev0=ROOT/'QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/kill-after-commit.db';db=DATA/'legacy-v1.db'
 with sqlite3.connect(rev0) as src,sqlite3.connect(db) as dest:src.backup(dest)
 old={t:sql(db,'select * from '+t) for t in ['OperationRecords','ProbeAggregates','CommitReceipts','PublicationOutbox']}
 migrated=run('validate',db,'legacy-v1-migrate');record('legacy-v1',{'before':old,'migration':migrated,'after':state(db)})
 # Storage failures: genuine native constraints; I/O-like observer; bounded writer lock.
 for label,table in [('aggregate-constraint','ProbeAggregates'),('receipt-constraint','CommitReceipts'),('event-constraint','PublicationEvents')]:
  name='storage-'+label;db=init(name);sql(db,f"create trigger qa_fail before insert on {table} begin select RAISE(ABORT,'QA constraint failure'); end")
  record(name,{'execute':run('execute',db,name,request=request(name)),'db':state(db)})
 db=init('io-like');record('io-like',{'execute':run('execute',db,'io-like',request=request('io-like'),inject='before-receipt'),'db':state(db)})
 db=init('busy');conn=sqlite3.connect(db);conn.execute('begin immediate');res=run('execute',db,'busy',request=request('busy'));conn.rollback();conn.close();record('busy',{'execute':res,'db':state(db)})
 # Receipt reload across cultures; Windows TZ environment may not change actual local zone: record actual zones.
 receiptDB=DATA/'identity.db';cultureTests=[]
 for culture,tz in [('en-US','UTC'),('ko-KR','Asia/Seoul'),('tr-TR','Europe/Istanbul'),('ar-SA','Asia/Riyadh'),('de-DE','Europe/Berlin')]:
  cultureTests.append(run('receipt',receiptDB,'receipt-'+culture,culture=culture,tz=tz))
 record('receipt-cultures',cultureTests)
 for mode in ['delay','starved']:
  db=init('queue-'+mode);r=run('queue',db,'queue-'+mode,request=request('queue-'+mode),queue_mode=mode);record('queue-'+mode,{'metrics':r,'db':state(db)})
 print('MAIN DONE',flush=True)
