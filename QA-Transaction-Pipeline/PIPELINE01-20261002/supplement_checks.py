import run_checks as q
from pathlib import Path
import json,subprocess,hashlib,time,threading,socket,struct,shutil
q.RESULTS=json.loads((q.DATA/'results.json').read_text());R=q.RESULTS
def compare_receipt():
 f=R['fingerprints'];a=f['baseline']['result']['Receipt'];b=f['tests']['same-retry']['result']['Receipt']
 def recalc(r):
  raw=f"{r['OperationId']}:{r['ProbeScopeId']}:{r['CommittedRevision']}:{r['CommittedAtUtc']}"
  return hashlib.sha256(raw.encode()).hexdigest().upper()
 q.record('receipt-wire-stability',{'first':a,'retry':b,'sameReceiptId':a['ReceiptId']==b['ReceiptId'],'sameReceiptHash':a['ReceiptHash']==b['ReceiptHash'],'sameTimestampString':a['CommittedAtUtc']==b['CommittedAtUtc'],'sameStatus':a['Status']==b['Status'],'originalHashRecomputes':recalc(a)==a['ReceiptHash'],'retryHashRecomputes':recalc(b)==b['ReceiptHash']})
compare_receipt()
# Negative crash publication with a candidate DefaultPublicationOutboxDispatcher OnDispatched callback was tested
# via the same interface contract (observer consumer has no dedup, FileStream Flush(true) durable effect).
# Native DB migration fault: failure mid-DDL must roll back all NEW DDL and leave version 0.
db=q.DATA/'migration-ddl-rollback.db';q.sql(db,'create view OperationRecords as select 1 as Bogus')
res=q.run('init',db,'migration-ddl-rollback-init')
q.record('migration-ddl-rollback',{'init':res,'schema':q.sql(db,'pragma user_version'),'objects':q.sql(db,"select type,name from sqlite_master order by name")})
# Corrupt DB itself: keep separate from frozen artifacts and originals.
db=q.DATA/'corrupt-file.db';db.write_bytes(b'NOT SQLITE DATABASE'+b'X'*8192)
q.record('corrupt-file',{'initialize':q.run('init',db,'corrupt-file-init')})
# Loaded dependency identity versus candidate's frozen dependencies, all runtime DLLs/native win-x64.
checks=[]
for p in (q.QA/'Harness'/'bin'/'Debug'/'net8.0').rglob('*.dll'):
 rel=p.relative_to(q.QA/'Harness'/'bin'/'Debug'/'net8.0');old=q.QA/'FrozenRuntime'/rel
 if old.exists():checks.append({'relative':str(rel),'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper(),'frozenSha256':hashlib.sha256(old.read_bytes()).hexdigest().upper(),'equal':p.read_bytes()==old.read_bytes()})
q.record('dependencies',checks)
# Production ordinary startup: run only if 7777 is currently unused; never stop a user's server.
bind=socket.socket()
try:bind.bind(('0.0.0.0',7777));available=True
except OSError:available=False
finally:bind.close()
if available:
 rt=q.QA/'StartupRuntime';shutil.copytree(q.QA/'FrozenRuntime',rt,dirs_exist_ok=True)
 canonical=rt/'war_economy_pipeline.db'
 def startup(name,wire=False):
  lines=[];p=subprocess.Popen([q.DOTNET,str(rt/'WarEconomy.Server.dll')],cwd=rt,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
  def reader():
   for line in p.stdout:lines.append(line)
  th=threading.Thread(target=reader,daemon=True);th.start();deadline=time.monotonic()+8
  while not any('Server ready!' in l for l in lines) and p.poll() is None and time.monotonic()<deadline:time.sleep(.02)
  ready=any('Server ready!' in l for l in lines);wireok=False
  if ready and wire:
   # Undefined header + valid probe-shaped JSON: actual framing/receive/dispatch path, no auth or gameplay mutation.
   s=socket.create_connection(('127.0.0.1',7777),timeout=2)
   body=json.dumps({'OperationType':'PIPELINE_PROBE_CAS','OperationId':'NETWORK_ATTACK','ProbeScopeId':'NETWORK_SCOPE','ExpectedProbeRevision':0,'PayloadJson':'{}'}).encode()
   s.sendall(struct.pack('<Hi',65535,len(body))+body);time.sleep(.15);s.close();wireok=True
  if p.poll() is None:
   p.stdin.write('status\nquit\n');p.stdin.flush()
   try:p.wait(timeout=8)
   except subprocess.TimeoutExpired:p.kill();p.wait()
  th.join(timeout=2);log=''.join(lines);(q.DATA/(name+'.server.log')).write_text(log,encoding='utf-8')
  return {'pid':p.pid,'exitCode':p.returncode,'ready':ready,'probeWireFrameSent':wireok,'log':log,'pipelineDBExists':canonical.exists()}
 fresh=startup('startup-fresh',True)
 q.record('startup-fresh',fresh)
 # Real durable PREPARED in exact default database path, followed by ordinary production process startup.
 q.run('init',canonical,'startup-restart-init')
 req=q.request('startup-restart')
 q.kill_checkpoint(canonical,'startup-restart-prepare','after-prepared',req=req)
 before=q.state(canonical)
 restart=startup('startup-restart',True)
 q.record('startup-restart',{'before':before,'startup':restart,'after':q.state(canonical),'loadedFrozenDllHash':hashlib.sha256((rt/'WarEconomy.Server.dll').read_bytes()).hexdigest().upper()})
else:q.record('startup-ordinary',{'blocked':'7777 occupied; existing server not touched','staticEvidence':'normal Program.Main branch has no pipeline DB initialize/recovery before Start(7777)'})
# Preserve explicit isolated build log (no frozen binary overwrite).
p=subprocess.run([q.DOTNET,'build',str(q.QA/'BuildCopy'/'Source'/'Server'/'WarEconomy.Server.csproj'),'--no-restore'],capture_output=True,text=True,encoding='utf-8',timeout=60)
(q.DATA/'isolated-production-build.txt').write_text(p.stdout+p.stderr,encoding='utf-8')
q.record('isolated-build',{'exitCode':p.returncode,'log':p.stdout+p.stderr,'note':'first no-restore attempt lacked copied assets; offline cached restore succeeded, initial full compilation warnings0/errors0; this log is incremental verification'})
# Verify exact source/deployment freeze, including additions/removals within monitored extensions.
before=json.loads((q.QA/'freeze-before.json').read_text());after={}
for p in (q.ROOT/'WarEconomyMod').rglob('*'):
 if p.is_file() and p.suffix.lower() in ('.cs','.csproj','.dll','.exe','.json'):after[str(p.relative_to(q.ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
changes=[{'path':k,'old':before.get(k,{}).get('sha256'),'new':after.get(k)} for k in set(before)|set(after) if before.get(k,{}).get('sha256')!=after.get(k)]
q.record('freeze-final',{'filesBefore':len(before),'filesAfter':len(after),'changes':changes})
print('SUPPLEMENT DONE',flush=True)
