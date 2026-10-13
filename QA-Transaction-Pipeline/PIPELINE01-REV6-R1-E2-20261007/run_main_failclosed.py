import json,shutil,sqlite3
import run_processes as r
from prepare import Q,write,now
r.records.extend(json.loads((r.E/'processes.json').read_text()))
for v in [6,8]:
    dest=Q/f'MainUnsupported{v}';assert not dest.exists();shutil.copytree(Q/'Runtime',dest)
    db=dest/'war_economy_pipeline.db';c=sqlite3.connect(db)
    c.executescript(f'CREATE TABLE LegacyEvidence(x INTEGER); INSERT INTO LegacyEvidence VALUES(42); PRAGMA application_id=1463898693; PRAGMA user_version={v};');c.commit();c.close()
    p,d,t=r.launch(f'actual-main-unsupported-{v}',[str(dest/'WarEconomy.Server.exe')],dest);r.finish(p,d,t)
    assert d['exit']==2 and not any('Listening' in s for s in d['output']),d
    c=sqlite3.connect(db);assert c.execute('pragma user_version').fetchone()[0]==v and c.execute('select x from LegacyEvidence').fetchone()[0]==42;c.close()
p,d,t=r.harness('recover-supplement','recover',Q/'Databases/r2-supplement.db');r.finish(p,d,t);assert d['exit']==0
write(r.E/'all-process-controls-completed.json',dict(at=now(),completed=True,process_count=len(r.records),normal_exit_zero=sum(d['exit']==0 for d in r.records),expected_failclosed_exit_two=sum(d['exit']==2 for d in r.records),all_exit_expected=all(d['exit'] in [0,2] for d in r.records),owned_interruption_count=0,production_crash_cuts_tested=False,power_loss_tested=False))
print(json.dumps(dict(process_count=len(r.records),normal_exit_zero=sum(d['exit']==0 for d in r.records),failclosed_exit_two=sum(d['exit']==2 for d in r.records))))
