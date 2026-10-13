from prepare import Q,write,now
import subprocess,threading,time,json,shutil,socket
E=Q/'Evidence'; H=Q/'Harness/bin/Release/net8.0/Harness.dll'
records=[]
def launch(name,args,cwd=Q):
    p=subprocess.Popen(args,cwd=cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    r=dict(name=name,pid=p.pid,argv=[str(a) for a in args],cwd=str(cwd),started=now(),output=[],exit=None)
    records.append(r)
    def read():
        for line in p.stdout:r['output'].append(line.rstrip());r['last_output_at']=now()
    t=threading.Thread(target=read,daemon=True);t.start()
    return p,r,t
def finish(p,r,t,timeout=45):
    r['exit']=p.wait(timeout=timeout);t.join(2);r['ended']=now()
    write(E/'processes.json',records)
    (E/(r['name']+'.console.txt')).write_text('\n'.join(r['output'])+'\n',encoding='utf-8')
    return r
def harness(name,*args):return launch(name,['dotnet',str(H),*map(str,args)])
def main():
    p,r,t=harness('independent-suite-r2');finish(p,r,t);assert r['exit']==0,r['output']
    gate=Q/'Databases/concurrent.release';assert not gate.exists()
    workers=[harness('concurrent-'+str(i),'cas',Q/'Databases/r2-concurrent.db','ConcurrentPlayer',f'Race{i}','ConcurrentScope',0,'unused',gate) for i in range(8)]
    limit=time.monotonic()+30
    while not all(any('CHILD_READY ' in s for s in r['output']) for p,r,t in workers):
        assert time.monotonic()<limit,'concurrent readiness timeout';time.sleep(.02)
    overlap=dict(released=now(),alive_pids=[p.pid for p,r,t in workers if p.poll() is None],worker_count=8)
    assert len(overlap['alive_pids'])==8
    gate.write_text('release',encoding='utf-8');write(E/'concurrent-overlap.json',overlap)
    outcomes=[]
    for p,r,t in workers:
        finish(p,r,t);assert r['exit']==0
        outcomes.append(json.loads(next(s.removeprefix('CHILD_RESULT ') for s in r['output'] if s.startswith('CHILD_RESULT '))))
    counts={x:sum(o['result']['Outcome']==x for o in outcomes) for x in {'SUCCESS','STALE_REVISION'}}
    write(E/'concurrent-outcomes.json',dict(counts=counts,results=outcomes));assert counts=={'SUCCESS':1,'STALE_REVISION':7},counts
    for i in range(5):
        p,r,t=harness('sequential-'+str(i),'cas',Q/'Databases/r2-ordered-process.db','OrderedPlayer',f'Sequential{i}','OrderedScope',i)
        finish(p,r,t);assert r['exit']==0 and '"Outcome":"SUCCESS"' in '\n'.join(r['output'])
    # Same durable operation in independent overlapping processes is a normal retry control.
    gate2=Q/'Databases/identity.release';assert not gate2.exists()
    workers=[harness('identity-'+str(i),'cas',Q/'Databases/r2-ordered-process.db','OrderedPlayer','SameOperation','IdentityScope',0,'unused',gate2) for i in range(4)]
    limit=time.monotonic()+30
    while not all(any('CHILD_READY ' in s for s in r['output']) for p,r,t in workers):
        assert time.monotonic()<limit;time.sleep(.02)
    write(E/'identity-overlap.json',dict(released=now(),alive_pids=[p.pid for p,r,t in workers if p.poll() is None]));gate2.write_text('release',encoding='utf-8')
    outcomes=[]
    for p,r,t in workers:
        finish(p,r,t);assert r['exit']==0
        outcomes.append(json.loads(next(s.removeprefix('CHILD_RESULT ') for s in r['output'] if s.startswith('CHILD_RESULT '))))
    counts={x:sum(o['result']['Outcome']==x for o in outcomes) for x in {'SUCCESS','ALREADY_COMMITTED'}}
    write(E/'identity-outcomes.json',dict(counts=counts,results=outcomes));assert counts=={'SUCCESS':1,'ALREADY_COMMITTED':3}
    for name in ['natural-history','concurrent','ordered-process','unknown','lifetime']:
        p,r,t=harness('recover-'+name,'recover',Q/f'Databases/r2-{name}.db');finish(p,r,t);assert r['exit']==0
    dest=Q/'MainRuntime';assert not dest.exists();shutil.copytree(Q/'Runtime',dest)
    probe=socket.socket()
    try:probe.bind(('0.0.0.0',7777))
    except OSError as ex:
        write(E/'main-not-run.json',dict(reason='port7777 unavailable',error=str(ex)));return
    finally:probe.close()
    p,r,t=launch('actual-main-normal-quit',[str(dest/'WarEconomy.Server.exe')],dest)
    limit=time.monotonic()+20
    while not any('Server ready! Listening' in s for s in r['output']):
        assert p.poll() is None and time.monotonic()<limit,r['output'];time.sleep(.02)
    r['quit_submitted_at']=now();p.stdin.write('status\nquit\n');p.stdin.flush();finish(p,r,t);assert r['exit']==0
    write(E/'process-controls-completed.json',dict(completed=True,at=now(),process_count=len(records),owned_interruption_count=0,power_loss=False))
    print(json.dumps(dict(process_count=len(records),all_exit_zero=all(r['exit']==0 for r in records),concurrent=8,identity=4,sequential=5,actual_main=True)))
if __name__=='__main__':main()
