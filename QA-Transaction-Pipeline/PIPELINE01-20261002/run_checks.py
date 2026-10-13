from pathlib import Path
import subprocess,json,sqlite3,time,hashlib,re,collections,os
QA=Path(__file__).parent.resolve();ROOT=QA.parent.parent
DOTNET=r'C:\Program Files\dotnet\dotnet.exe'
HAR=QA/'Harness'/'bin'/'Debug'/'net8.0'/'Harness.dll'
DATA=QA/'Evidence';DATA.mkdir(exist_ok=True)
RESULTS={}
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def request(name,**changes):
 d=dict(OperationId='OP',ProbeScopeId='SCOPE',ExpectedProbeRevision=0,PayloadJson='{"value":1}',ActorId='ACTOR_A',ContentProfileFingerprint='PROFILE_A');d.update(changes)
 p=DATA/(name+'.request.json');write(p,d);return p
def args(mode,db,**opts):
 a=[DOTNET,str(HAR),mode,str(db)]
 for k,v in opts.items():a+=['--'+k.replace('_','-'),str(v)]
 return a
def run(mode,db,name,**opts):
 p=subprocess.run(args(mode,db,**opts),capture_output=True,text=True,encoding='utf-8',timeout=65)
 (DATA/(name+'.stdout.txt')).write_text(p.stdout+'\nSTDERR:\n'+p.stderr,encoding='utf-8')
 try:r=json.loads(p.stdout.strip().splitlines()[-1])
 except:r={'status':'UNPARSEABLE','stdout':p.stdout,'stderr':p.stderr}
 r['exitCode']=p.returncode;return r
def init(name):
 db=DATA/(name+'.db')
 if db.exists():
  i=2
  while (DATA/(name+f'-attempt{i}.db')).exists():i+=1
  db=DATA/(name+f'-attempt{i}.db')
 r=run('init',db,name+'-init');assert r['exitCode']==0,r
 return db
def sql(db,query,values=()):
 with sqlite3.connect(db) as c:return c.execute(query,values).fetchall()
def state(db):
 out={'path':str(db)}
 with sqlite3.connect(db) as c:
  for t in ['ProbeAggregates','ProbeRevisionHistory','OperationRecords','CommitReceipts','AuditRecords','PublicationOutbox']:
   c.row_factory=sqlite3.Row
   try:out[t]=[dict(r) for r in c.execute('select * from '+t)]
   except Exception as e:out[t]={'error':str(e)}
  out['integrity']=c.execute('pragma integrity_check').fetchone()[0]
 return out
def save():write(DATA/'results.json',RESULTS)
def record(k,v):RESULTS[k]=v;save();print(k, json.dumps(v,ensure_ascii=False)[:1100],flush=True)
def start_checkpoint(db,name,point,mode='execute',req=None,throw=None,effects=None):
 import uuid
 suffix=str(uuid.uuid4())[:8]
 sig=DATA/(name+'-'+suffix+'.signal');rel=DATA/(name+'-'+suffix+'.release');opts={'point':point,'signal':sig,'release':rel}
 if req:opts['request']=req
 if effects:opts['effects']=effects
 if throw:opts['throw']=throw
 out=open(DATA/(name+'.process.txt'),'w',encoding='utf-8')
 p=subprocess.Popen(args(mode,db,**opts),stdout=out,stderr=subprocess.STDOUT)
 deadline=time.monotonic()+40
 while True:
  try:
   json.loads(sig.read_text())
   break
  except (FileNotFoundError,json.JSONDecodeError):pass
  if p.poll() is not None:raise RuntimeError((name,'exited before checkpoint',p.returncode,(DATA/(name+'.process.txt')).read_text(encoding='utf-8')))
  if time.monotonic()>deadline:p.kill();p.wait();raise TimeoutError(name)
  time.sleep(.005)
 return p,out,sig,rel
def kill_checkpoint(db,name,point,**opts):
 p,out,sig,rel=start_checkpoint(db,name,point,**opts)
 sigdata=json.loads(sig.read_text());p.kill();p.wait(timeout=10);out.close()
 return {'signal':sigdata,'OSKillExitCode':p.returncode,'durableBeforeRecovery':state(db)}

if __name__=='__main__':
 # Evidence identity: exact frozen DLL is loaded by the QA process; isolated build does not alter it.
 db=init('metadata');record('metadata-normal',run('meta',db,'metadata-normal'))
 record('metadata-full',run('meta',db,'metadata-full',sync='FULL'))
 report=(ROOT/'Production_Transaction_Pipeline_Slice_01.md').read_text(encoding='utf-8-sig')
 verified=[]
 for line in (QA/'developer-hash-rows.txt').read_text(encoding='utf-8').splitlines():
  parts=[s.strip(' `') for s in line.split('|') if s.strip()]
  if not parts[0].startswith('Source'):continue
  p=ROOT/'WarEconomyMod'/Path(parts[0]);expected=re.search('[0-9A-F]{64}',line).group()
  actual=hashlib.sha256(p.read_bytes()).hexdigest().upper();verified.append({'path':str(p),'expected':expected,'actual':actual,'match':expected==actual})
 record('manifest',verified)
 # Baseline + complete semantic envelope collision challenges.
 db=init('fingerprints');r=request('fingerprint-base');baseline=run('execute',db,'fingerprint-base',request=r)
 tests={}
 for field,value in [('ProbeScopeId','OTHER_SCOPE'),('ExpectedProbeRevision',99),('ActorId','ACTOR_B'),('ContentProfileFingerprint','PROFILE_B'),('PayloadJson','{"value":2}')]:
  tests[field]=run('execute',db,'fingerprint-'+field,request=request('fingerprint-'+field,**{field:value}))
 tests['same-retry']=run('execute',db,'fingerprint-retry',request=r)
 # OperationType is not a request field: mutate stored type to demonstrate missing semantic collision guard (not a supported remote command).
 sql(db,"update OperationRecords set OperationType='OTHER_OPERATION' where OperationId='OP'")
 tests['stored-OperationType-altered']=run('execute',db,'fingerprint-type',request=r)
 # Request-supplied hash is accepted without recomputation.
 tests['forged-PayloadHash']=run('execute',db,'fingerprint-forged-hash',request=request('fingerprint-forged-hash',PayloadJson='{"value":999}',PayloadHash=hashlib.sha256(b'{"value":1}').hexdigest()))
 record('fingerprints',{'baseline':baseline,'tests':tests,'db':state(db)})
 # independent OS processes and SQLite connections; same expected revision.
 for kind in ['native-race','prepared-barrier-race','same-id-race']:
  db=init(kind);count=25 if kind!='same-id-race' else 10
  ps=[];handles=[];start=DATA/(kind+'.start');release=DATA/(kind+'.release')
  for i in range(count):
   name=kind+'-'+str(i);req=request(name,OperationId='DUPLICATE' if kind=='same-id-race' else 'OP_'+str(i),PayloadJson='{"same":true}' if kind=='same-id-race' else '{"index":'+str(i)+'}')
   opt={'request':req,'start':start,'ready':DATA/(name+'.ready')}
   if kind!='native-race':opt.update(point='prepared-before-audit' if kind=='prepared-barrier-race' else 'after-record-read',signal=DATA/(name+'.signal'),release=release)
   h=open(DATA/(name+'.process.txt'),'w',encoding='utf-8');handles.append(h)
   ps.append(subprocess.Popen(args('execute',db,**opt),stdout=h,stderr=subprocess.STDOUT))
  deadline=time.monotonic()+40
  while not all((DATA/(kind+'-'+str(i)+'.ready')).exists() for i in range(count)):
   if time.monotonic()>deadline:raise TimeoutError(kind+' ready')
   time.sleep(.02)
  start.write_text('start');begin=time.monotonic()
  if kind!='native-race':
   while not all((DATA/(kind+'-'+str(i)+'.signal')).exists() for i in range(count)):
    if time.monotonic()>deadline:raise TimeoutError(kind+' barrier')
    time.sleep(.02)
   release.write_text('release')
  for p,h in zip(ps,handles):p.wait(timeout=60);h.close()
  outcomes=[json.loads((DATA/(kind+'-'+str(i)+'.process.txt')).read_text(encoding='utf-8').strip().splitlines()[-1]) for i in range(count)]
  record(kind,{'count':count,'summary':dict(collections.Counter(o.get('result',{}).get('Status',o['status']) for o in outcomes)), 'elapsedMs':(time.monotonic()-begin)*1000,'outcomes':outcomes,'db':state(db)})
 # Actual OS hard-kill, no caught exception or finally rollback before termination.
 points=['prepared-before-audit','after-prepared','before-cas','after-cas','after-receipt','after-audit-PROBE_CAS_COMMITTED','after-outbox','before-commit','native-commit','after-commit','after-effect','after-delivered']
 for point in points:
  name='kill-'+point;db=init(name);req=request(name);effects=DATA/(name+'.effects.jsonl')
  result=kill_checkpoint(db,name,point,req=req,effects=effects)
  result['recover']=run('recover',db,name+'-recover',effects=effects)
  result['durableAfterRecovery']=state(db)
  result['recoverAgain']=run('recover',db,name+'-recover-again',effects=effects)
  result['retry']=run('execute',db,name+'-retry',request=req,effects=effects)
  result['effects']=[json.loads(l) for l in effects.read_text().splitlines()] if effects.exists() else []
  record(name,result)
 # Tamper a real durable PREPARED package from exact candidate.
 tamper=[('payload-changed',"update OperationRecords set PayloadJson='{\"value\":666}'"),('payload-empty',"update OperationRecords set PayloadJson=''"),('payload-invalid-json',"update OperationRecords set PayloadJson='not-json'"),('hash-changed',"update OperationRecords set PayloadHash='BAD_HASH'"),('hash-empty',"update OperationRecords set PayloadHash=''"),('scope-changed',"update OperationRecords set ProbeScopeId='EVIL_SCOPE'"),('scope-empty',"update OperationRecords set ProbeScopeId=''"),('actor-changed',"update OperationRecords set ActorId='EVIL_ACTOR'"),('actor-empty',"update OperationRecords set ActorId=''"),('profile-changed',"update OperationRecords set ContentProfileFingerprint='EVIL_PROFILE'"),('profile-empty',"update OperationRecords set ContentProfileFingerprint=''"),('type-changed',"update OperationRecords set OperationType='NOT_PROBE'"),('revision-changed','update OperationRecords set ExpectedProbeRevision=1')]
 for label,query in tamper:
  name='tamper-'+label;db=init(name);req=request(name)
  original=kill_checkpoint(db,name,'after-prepared',req=req)
  if label=='revision-changed':sql(db,"insert into ProbeAggregates values ('SCOPE',1,'2026-10-02T00:00:00Z','2026-10-02T00:00:00Z')")
  sql(db,query);before=state(db)
  result=run('recover',db,name+'-recover');record(name,{'before':before,'recover':result,'after':state(db)})
 # Real write failures around inserts and split publication updates, candidate decides response/recovery.
 points=['before-audit-PROBE_CAS_PREPARED','before-receipt','before-audit-PROBE_CAS_COMMITTED','before-outbox','before-delivered','before-state-PUBLISHED','dispatch-throws','dispatch-return-false']
 for point in points:
  name='writefail-'+point;db=init(name);req=request(name);effects=DATA/(name+'.effects.jsonl')
  result=run('execute',db,name,request=req,throw=point,effects=effects);before=state(db)
  recovery=run('recover',db,name+'-recover',effects=effects);after=state(db)
  record(name,{'execute':result,'before':before,'recover':recovery,'after':after,'retry':run('execute',db,name+'-retry',request=req),'effects':[json.loads(l) for l in effects.read_text().splitlines()] if effects.exists() else []})
 # Native SQLite constraint failure in atomic receipt/audit/outbox insert.
 for table in ['CommitReceipts','AuditRecords','PublicationOutbox']:
  name='sqlfail-'+table;db=init(name);req=request(name)
  condition=" WHEN NEW.EventType='PROBE_CAS_COMMITTED'" if table=='AuditRecords' else ''
  sql(db,f"create trigger qa_write_failure before insert on {table}{condition} begin select RAISE(ABORT,'QA simulated storage constraint'); end")
  result=run('execute',db,name,request=req);before=state(db);sql(db,'drop trigger qa_write_failure')
  record(name,{'execute':result,'before':before,'recover':run('recover',db,name+'-recover'),'after':state(db)})
 # Busy lock beyond actual provider CommandTimeout; candidate has no typed busy/retry outcome handling.
 db=init('busy');req=request('busy');c=sqlite3.connect(db);c.execute('begin immediate')
 h=open(DATA/'busy.process.txt','w',encoding='utf-8');p=subprocess.Popen(args('execute',db,request=req),stdout=h,stderr=subprocess.STDOUT)
 begin=time.monotonic();p.wait(timeout=55);elapsed=time.monotonic()-begin;h.close();c.rollback();c.close()
 record('busy-lock',{'elapsedSeconds':elapsed,'outcome':json.loads((DATA/'busy.process.txt').read_text().strip().splitlines()[-1]),'db':state(db)})
 # Fresh, malformed and future migration version behavior.
 for label,setup in [('bad-v0',"create table ProbeAggregates(Bogus text)"),('broken-v1',"pragma user_version=1"),('future-v999',"pragma user_version=999")]:
  db=DATA/('migration-'+label+'.db');sql(db,setup)
  initialized=run('init',db,'migration-'+label+'-init')
  meta=run('meta',db,'migration-'+label+'-meta')
  execute=run('execute',db,'migration-'+label+'-execute',request=request('migration-'+label))
  record('migration-'+label,{'init':initialized,'meta':meta,'execute':execute,'db':state(db)})
 # Exact compiled Production entrypoint E1 test, isolated working directory and explicit DB.
 p=subprocess.run([DOTNET,str(QA/'FrozenRuntime'/'WarEconomy.Server.dll'),'--test-pipeline-e1','--db',str(DATA/'developer-battery.db'),'--json',str(DATA/'developer-battery.json')],cwd=DATA,capture_output=True,text=True,encoding='utf-8',timeout=90)
 (DATA/'developer-battery.stdout.txt').write_text(p.stdout+'\nSTDERR:\n'+p.stderr,encoding='utf-8');record('developer-battery',{'exitCode':p.returncode,'report':json.loads((DATA/'developer-battery.json').read_text())})
 # Freeze recheck at end.
 before=json.loads((QA/'freeze-before.json').read_text());changes=[]
 for path,old in before.items():
  p=ROOT/path;new=hashlib.sha256(p.read_bytes()).hexdigest().upper() if p.exists() else 'MISSING'
  if new!=old['sha256']:changes.append({'path':path,'old':old['sha256'],'new':new})
 record('freeze-after',{'files':len(before),'changes':changes})
 print('DONE',flush=True)
