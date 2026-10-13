import run_checks as q
import json,shutil,time,threading,subprocess,concurrent.futures
q.RESULTS={};mutex=threading.Lock()
def record(k,v):
 with mutex:q.RESULTS[k]=v;q.f.write(q.E/'lifetime-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=record;q.H=q.Q/'HarnessExt/bin/Release/net8.0/Harness.dll'
# all fresh DBs initialized before concurrent cases; no candidate modifications.
cases=[('hold6','before-read',6000,1205),('hold8','before-read',8000,1),('hold13','before-read',13000,1),('aftercas','after-cas',8000,1),('afteraudit','after-audit',8000,1),('precommit','native-commit',8000,1),('postwal','native-wal',8000,1)]
for name,point,hold,n in cases:q.fresh('lifetime-'+name)
def trial(t):
 name,point,hold,n=t;db=q.D/('lifetime-'+name+'.db');q.run('timed-life',db,'lifetime-'+name,timeout=35,point=point,hold=hold,n=n,signal=q.E/(name+'.signal'),release=q.E/(name+'.release'));q.run('startup',db,'restart-'+name);q.run('historical',db,'query-'+name,op='TIMED');q.execute(db,'retry-'+name,scope='TIMED',name='TIMED',ContentProfileFingerprint='PROBE_PROFILE_V1')
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for result in pool.map(trial,cases):pass
# External real SQLite lock released on timer, independently of Dispose completion.
db=q.fresh('lifetime-lock');lock=q.conn(db);lock.execute('BEGIN IMMEDIATE');signal=q.E/'lock.signal';release=q.E/'lock.release'
p,log=q.spawn('queue-lock',db,'lifetime-lock',signal=signal,release=release,n=1205);time.sleep(13);lock.rollback();lock.close();release.write_text('independent release',encoding='utf-8');p.wait(timeout=25);log.close();q.record('lifetime-lock',{'pid':p.pid,'exit':p.returncode,'stdout':(q.E/'lifetime-lock.stdout').read_text(encoding='utf-8')});q.run('startup',db,'restart-lock');q.run('historical',db,'query-lock',op='Q0');q.execute(db,'retry-lock',scope='QUEUE',name='Q0',ContentProfileFingerprint='PROBE_PROFILE_V1')
# Main executes inside dedicated QA working directory; actual Main owns actual network listener.
old=q.Q;main=old/'MainActive';main.mkdir();q.Q=main
try:q.run('main-active',main/'unused.db','actual-main-active',timeout=30)
finally:q.Q=old
q.check();q.record('lifetime-freeze',{'unchanged':q.f.tree()==json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'))})
