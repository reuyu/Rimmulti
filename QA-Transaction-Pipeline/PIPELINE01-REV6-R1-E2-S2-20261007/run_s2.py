from prepare_s2 import Q,write,now,sha
from pathlib import Path
import subprocess,threading,time,json,sqlite3,sys
E=Q/'Evidence';H=Q/'Tooling/R1/bin/Harness.dll';processes=[];cases=[]
def launch(name,mode,db,stage):
    snap=json.loads((Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json').read_text());assert sha(H)==snap['lineage']['dll_sha256']
    argv=['dotnet',str(H),mode,str(db),stage]
    p=subprocess.Popen(argv,cwd=Q,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
    r=dict(name=name,pid=p.pid,argv=argv,cwd=str(Q),started=now(),output=[],exit=None,tool_revision='R1',tool_sha256=sha(H));processes.append(r)
    def read():
        for line in p.stdout:r['output'].append(line.rstrip())
    t=threading.Thread(target=read,daemon=True);t.start();return p,r,t
def finish(p,r,t):
    r['exit']=p.wait(timeout=20);t.join(2);r['ended']=now();write(E/'processes.json',processes)
    (E/(r['name']+'.console.txt')).write_bytes(('\n'.join(r['output'])+'\n').encode());return r
def normal(name,mode,db,stage):
    p,r,t=launch(name,mode,db,stage);finish(p,r,t);assert r['exit']==0,r;return r
def get(tag,r):return json.loads(next(s.removeprefix(tag+' ') for s in r['output'] if s.startswith(tag+' ')))
def db_snapshot(db,label):
    c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    tables=[x[0] for x in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
    rows={t:[dict(x) for x in c.execute('select rowid as _rowid,* from '+t+' order by rowid')] for t in tables}
    integrity=c.execute('pragma integrity_check').fetchone()[0];fk=[list(x) for x in c.execute('pragma foreign_key_check')];assert integrity=='ok' and not fk;c.close()
    d=dict(path=str(db),at=now(),rows=rows,integrity=integrity,fk_violations=fk,python_sqlite=sqlite3.sqlite_version)
    write(E/(label+'.json'),d);return d
def main():
    write(E/'python-driver-before.json',dict(at=now(),source=str(Path(__file__).resolve()),source_sha256=sha(Path(__file__)),invocation=['python',str(Path(__file__).resolve()),*sys.argv[1:]],snapshot=str(Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json')))
    for stage in ['commit-parent','commit-audit','stale-audit']:
        db=Q/f'Databases/{stage}.db';assert not db.exists();normal(stage+'-seed','seed',db,stage)
        baseline=db_snapshot(db,stage+'-baseline');p,r,t=launch(stage+'-interrupt','interrupt',db,stage)
        deadline=time.monotonic()+15
        while not any(s.startswith('AFTER_DELEGATED_WRITE ') for s in r['output']) and p.poll() is None and time.monotonic()<deadline:time.sleep(.01)
        if not any(s.startswith('AFTER_DELEGATED_WRITE ') for s in r['output']):
            if p.poll() is None:p.kill();r['cleanup_owned_kill']=True
            finish(p,r,t);case=dict(stage=stage,status='UNOBSERVED',reason='no repository signal within bounded timeout',retry_performed=False);cases.append(case);write(E/'s2-results.json',dict(cases=cases,full_gate='INCONCLUSIVE_FULL_GATE'));continue
        signal=get('AFTER_DELEGATED_WRITE',r);write(E/(stage+'-transaction-signal.json'),signal)
        assert signal['stage']==stage and signal['pid']==p.pid and signal['transaction_attached']
        assert signal['implementation']['sha256']=='65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78'
        rows=signal['rows'];counts={k:len(v) for k,v in rows.items()}
        expected={'OperationRecords':2,'CommitReceipts':1,'PublicationEvents':1,'AuditRecords':1,'ProbeRevisionHistory':1}
        if stage=='commit-audit':expected={k:2 for k in expected}
        elif stage=='stale-audit':expected['AuditRecords']=2
        assert all(counts[k]==n for k,n in expected.items()),counts
        assert rows['ProbeAggregates'][0]['ProbeRevision']==(2 if stage=='commit-audit' else 1)
        target=next(x for x in rows['OperationRecords'] if x['OperationId']=='InterruptedOperation');assert target['State']==('ABORTED' if stage=='stale-audit' else 'COMMITTED')
        external=db_snapshot(db,stage+'-external-at-pause');assert external['rows']==baseline['rows'],'external reader saw uncommitted data'
        assert p.poll() is None
        proof=dict(at=now(),owned_handle_pid=p.pid,argv=r['argv'],cwd=r['cwd'],signal=signal['site'],transaction_instance=signal['transaction_instance'],connection_instance=signal['connection_instance'],external_rows_equal_baseline=True,termination_boundary='AFTER_DEFAULT_REPOSITORY_RETURN_BEFORE_COORDINATOR_COMMIT')
        write(E/(stage+'-owned-termination.json'),proof);p.kill();finish(p,r,t);assert r['exit']!=0
        cold=db_snapshot(db,stage+'-after-termination-before-native-recovery');assert cold['rows']==baseline['rows'],'cold read retained partial rows'
        retry=normal(stage+'-retry','retry',db,stage);final=db_snapshot(db,stage+'-after-retry')
        final_rows=final['rows'];exp={'OperationRecords':2,'CommitReceipts':1 if stage=='stale-audit' else 2,'PublicationEvents':1 if stage=='stale-audit' else 2,'AuditRecords':2,'ProbeRevisionHistory':1 if stage=='stale-audit' else 2}
        assert all(len(final_rows[k])==n for k,n in exp.items());assert final_rows['ProbeAggregates'][0]['ProbeRevision']==(1 if stage=='stale-audit' else 2)
        assert final_rows['StoreIncarnations']==baseline['rows']['StoreIncarnations']
        for table in baseline['rows']:
            for row in baseline['rows'][table]:
                if table!='ProbeAggregates':assert row in final_rows[table],(table,row)
        assert get('RECOVERY_BEFORE_RETRY',retry)['Success'] and get('RECOVERY_AFTER_RETRY',retry)['Success']
        assert get('RETRY',retry)['outcome']==('STALE_REVISION' if stage=='stale-audit' else 'SUCCESS')
        assert get('TERMINAL_REPEAT',retry)['outcome']==('ALREADY_ABORTED' if stage=='stale-audit' else 'ALREADY_COMMITTED')
        cases.append(dict(stage=stage,status='PASS',signal_site=signal['site'],pending_counts=counts,pending_target_state=target['State'],external_baseline_preserved=True,cold_baseline_preserved=True,retry=get('RETRY',retry),terminal_repeat=get('TERMINAL_REPEAT',retry),final_counts={k:len(v) for k,v in final_rows.items()},incarnation_unchanged=True))
        write(E/'s2-results.json',dict(at=now(),cases=cases,observed_controls='PASS' if all(c['status']=='PASS' for c in cases) else 'INCONCLUSIVE',full_gate='INCONCLUSIVE_FULL_GATE',native_commit_internal_cut=False,power_loss=False,repository_interruption_count=sum(c['status']=='PASS' for c in cases)))
    for r in processes:
        loaded=get('LOADED',r);assert loaded['tool']['sha256']==r['tool_sha256'] and loaded['server']['sha256']=='65FD5E73DBBE9A5F1454305A61C2E63022BEB4553F7A1BAE96E48CAE4B187F78'
    print(json.dumps(dict(cases=[dict(stage=c['stage'],status=c['status']) for c in cases],processes=len(processes),normal_exit_zero=sum(p['exit']==0 for p in processes),owned_repository_terminations=sum(c['status']=='PASS' for c in cases))))
if __name__=='__main__':main()
