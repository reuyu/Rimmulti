from prepare_s1 import Q,write,now,sha
import subprocess,threading,time,json,shutil,sqlite3
E=Q/'Evidence';H=Q/'Tooling/R1/bin/Harness.dll';processes=[]
def run(name,mode,path,*more):
    snap=json.loads((Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json').read_text());assert sha(H)==snap['dll_sha256']
    argv=['dotnet',str(H),mode,str(path),*map(str,more)]
    p=subprocess.Popen(argv,cwd=Q,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    r=dict(name=name,pid=p.pid,argv=argv,cwd=str(Q),at=now(),output=[],tooling_revision='R1',tool_sha256=sha(H),exit=None)
    processes.append(r)
    def read():
        for line in p.stdout:r['output'].append(line.rstrip())
    t=threading.Thread(target=read,daemon=True);t.start();return p,r,t
def finish(p,r,t):
    r['exit']=p.wait(timeout=25);t.join(2);r['ended']=now();write(E/'processes.json',processes);(E/(r['name']+'.txt')).write_text('\n'.join(r['output'])+'\n',encoding='utf-8')
    return r
def normal(name,mode,path,*more):
    p,r,t=run(name,mode,path,*more);finish(p,r,t);assert r['exit']==0,r
    return r
def snapshot_db(path,label):
    c=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    tables=[r[0] for r in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
    records={t:[dict(r) for r in c.execute('select rowid as _rowid,* from '+t+' order by rowid')] for t in tables}
    integrity=c.execute('pragma integrity_check').fetchone()[0];fk=[list(r) for r in c.execute('pragma foreign_key_check')];assert integrity=='ok' and not fk
    byop={(o['PrincipalId'],o['OperationId']):o['_rowid'] for o in records['OperationRecords']};relationships=[]
    for a in records['OperationRecords']:
        if a['State']=='ABORTED':
            for h in records['ProbeRevisionHistory']:
                if h['ProbeScopeId']==a['ProbeScopeId']:
                    row=byop[(h['PrincipalId'],h['OperationId'])];relationships.append(dict(aborted=a['OperationId'],commit=h['OperationId'],revision=h['ProbeRevision'],commit_rowid=row,abort_rowid=a['_rowid'],before=row<a['_rowid']))
    d=dict(path=str(path),at=now(),records=records,integrity=integrity,foreign_key_violations=fk,rowid_relationships=relationships,python_sqlite=sqlite3.sqlite_version)
    write(E/(label+'.json'),d);c.close();return d
def semantics(s):
    return {t:sorted([json.dumps({k:v for k,v in r.items() if k!='_rowid'},sort_keys=True) for r in rows]) for t,rows in s['records'].items()}
def compare(base,after,label):
    semantic_equal=semantics(base)==semantics(after)
    relations_equal=[{k:v for k,v in r.items() if k not in ['commit_rowid','abort_rowid']} for r in base['rowid_relationships']]==[{k:v for k,v in r.items() if k not in ['commit_rowid','abort_rowid']} for r in after['rowid_relationships']]
    rowids_equal=base['records']==after['records']
    assert semantic_equal and relations_equal
    return dict(name=label,semantic_equal=semantic_equal,rowid_relation_equal=relations_equal,all_rowids_equal=rowids_equal)
def main():
    write(E/'python-driver-before.json',dict(at=now(),source=str(Q/'run_s1.py'),sha256=sha(Q/'run_s1.py'),invocation=['python',str(Q/'run_s1.py')],tool_snapshot=str(Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json')))
    ack=Q/'Databases/acknowledged.db';p,r,t=run('ack-child','ackchild',ack)
    limit=time.monotonic()+20
    while not any(s.startswith('ACK_SUCCESS_DURABLE ') for s in r['output']):
        assert p.poll() is None and time.monotonic()<limit,r;time.sleep(.01)
    observed=json.loads(next(s[len('ACK_SUCCESS_DURABLE '):] for s in r['output'] if s.startswith('ACK_SUCCESS_DURABLE ')))
    assert observed['result']['outcome']=='SUCCESS' and all(v==1 for v in observed['counts'].values())
    before=snapshot_db(ack,'ack-before-termination');assert len(before['records']['OperationRecords'])==1
    # This exact Popen handle belongs only to the child just created above.
    assert p.poll() is None;proof=dict(at=now(),owned_pid=p.pid,argv=r['argv'],cwd=r['cwd'],observed_success=observed,durable_external_readback=before['path'],termination_boundary='AFTER_ACKNOWLEDGED_RESULT_AND_DURABLE_READBACK; writer idle; no internal cut')
    write(E/'owned-termination-before.json',proof);p.kill();finish(p,r,t);assert r['exit']!=0
    normal('ack-restart-retry','retryack',ack);after=snapshot_db(ack,'ack-after-restart');ack_result=compare(before,after,'acknowledged termination/restart')
    fixture=Q/'Databases/fixture.db';normal('create-fixture','fixture',fixture);base=snapshot_db(fixture,'fixture-closed-baseline')
    normal('fixture-recovery-retry','verify',fixture);assert semantics(base)==semantics(snapshot_db(fixture,'fixture-after-recovery'))
    # No live writer handles remain. Byte-copy baseline is QA-owned and fresh.
    bytecopy=Q/'Databases/normal-copy.db';vacuum=Q/'Databases/normal-vacuum.db';backup_source=Q/'Databases/backup-source-copy.db';backup=Q/'Databases/normal-backup.db'
    for path in [bytecopy,vacuum,backup_source]:assert not path.exists();shutil.copy2(fixture,path)
    normal('copy-recovery-retry','verify',bytecopy);copyresult=compare(base,snapshot_db(bytecopy,'copy-after'),'normal closed byte copy')
    vacbefore=snapshot_db(vacuum,'vacuum-before');normal('native-vacuum','vacuum',vacuum);vacafter=snapshot_db(vacuum,'vacuum-after');vacresult=compare(vacbefore,vacafter,'native VACUUM')
    normal('vacuum-recovery-retry','verify',vacuum);assert semantics(vacafter)==semantics(snapshot_db(vacuum,'vacuum-after-retry'))
    normal('native-backup','backup',backup_source,backup);backupbefore=snapshot_db(backup,'backup-after-api');backupresult=compare(base,backupbefore,'normal BackupDatabase')
    normal('backup-recovery-retry','verify',backup);assert semantics(backupbefore)==semantics(snapshot_db(backup,'backup-after-retry'))
    for r in processes:
        loaded=json.loads(next(s[len('LOADED '):] for s in r['output'] if s.startswith('LOADED ')))
        assert loaded['tool']['sha256']==r['tool_sha256'] and loaded['server']['sha256']=='65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78'
    write(E/'s1-results.json',dict(at=now(),observed_controls='PASS',full_gate='INCONCLUSIVE_FULL_GATE',process_count=len(processes),owned_terminations=1,normal_exit_zero=sum(r['exit']==0 for r in processes),acknowledged_baseline=ack_result,maintenance=[copyresult,vacresult,backupresult],internal_cuts_tested=False,universal_rowid_theorem=False,power_loss_tested=False))
    print(json.dumps(dict(process_count=len(processes),owned_termination=1,normal_exit_zero=sum(r['exit']==0 for r in processes),controls='PASS',vacuum=vacresult)))
if __name__=='__main__':main()
