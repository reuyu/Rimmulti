import run_checks as q
import json,subprocess,threading,time,socket,struct,shutil,sqlite3
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
def normal(name,seed=None,wire=False):
 rt=q.QA/('Normal-'+name);shutil.copytree(q.QA/'FrozenRelease',rt,dirs_exist_ok=True)
 db=rt/'war_economy_pipeline.db'
 if seed:seed(db)
 before=q.state(db) if db.exists() else None
 p=subprocess.Popen([q.DOTNET,str(rt/'WarEconomy.Server.dll')],cwd=rt,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',creationflags=subprocess.CREATE_NO_WINDOW)
 lines=[]
 def reader():
  for l in p.stdout:lines.append(l)
 th=threading.Thread(target=reader,daemon=True);th.start();deadline=time.monotonic()+10
 while p.poll() is None and not any('Server ready!' in l for l in lines) and time.monotonic()<deadline:time.sleep(.02)
 ready=any('Server ready!' in l for l in lines)
 wireok=False
 if ready and wire:
  sock=socket.create_connection(('127.0.0.1',7777),timeout=2);body=json.dumps({'OperationType':'PIPELINE_PROBE_CAS','PrincipalId':'REMOTE','OperationId':'REMOTE_ATTACK','ProbeScopeId':'REMOTE_SCOPE','ExpectedProbeRevision':0,'PayloadJson':'{}'}).encode();sock.sendall(struct.pack('<Hi',65535,len(body))+body);time.sleep(.12);sock.close();wireok=True
 if p.poll() is None:
  p.stdin.write('status\nquit\n');p.stdin.flush()
  try:p.wait(timeout=8)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 th.join(timeout=1);log=''.join(lines);(q.DATA/(name+'.normal.log')).write_text(log,encoding='utf-8')
 return {'pid':p.pid,'exitCode':p.returncode,'ready':ready,'wireProbeSent':wireok,'log':log,'before':before,'after':q.state(db) if db.exists() else None}
def seed_pending(db):
 q.run('init',db,'normal-pending-init');q.run('execute',db,'normal-pending-seed',request=q.request('normal-pending'))
def seed_schema(db,label):
 source=q.DATA/('schema-'+label+'.db')
 with sqlite3.connect(source) as src,sqlite3.connect(db) as dst:src.backup(dst)
bind=socket.socket()
try:bind.bind(('0.0.0.0',7777));available=True
except OSError:available=False
finally:bind.close()
if available:
 q.record('normal-fresh',normal('fresh',wire=True))
 q.record('normal-pending',normal('pending',seed_pending,wire=True))
 q.record('normal-future-schema',normal('future-schema',lambda db:seed_schema(db,'future-version')))
 q.record('normal-missing-column',normal('missing-column',lambda db:seed_schema(db,'missing-op-column')))
else:q.record('normal-entrypoint',{'blocked':'Existing 7777 listener; untouched','staticOnly':True})
# Optional developer test CLI actually present in RELEASE; run only with explicit QA-owned test DB.
rt=q.QA/'TestCliRuntime';shutil.copytree(q.QA/'FrozenRelease',rt,dirs_exist_ok=True)
p=subprocess.run([q.DOTNET,str(rt/'WarEconomy.Server.dll'),'--test-pipeline-e1','--db',str(q.DATA/'release-battery.db'),'--json',str(q.DATA/'release-battery.json')],cwd=rt,capture_output=True,text=True,encoding='utf-8',timeout=80)
(q.DATA/'release-battery.log').write_text(p.stdout+'\nSTDERR:\n'+p.stderr,encoding='utf-8')
q.record('release-battery',{'exitCode':p.returncode,'report':json.loads((q.DATA/'release-battery.json').read_text(encoding='utf-8')) if (q.DATA/'release-battery.json').exists() else None})
print('STARTUP DONE',flush=True)
