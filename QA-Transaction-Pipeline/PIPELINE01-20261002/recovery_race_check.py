import run_checks as q
import json
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
db=q.init('live-vs-recovery');req=q.request('live-vs-recovery')
p,h,sig,release=q.start_checkpoint(db,'live-vs-recovery','prepared-before-audit',req=req)
try:
 recovered=q.run('recover',db,'live-vs-recovery-recover')
 committed=q.state(db)
 release.write_text('release')
 p.wait(timeout=35);h.close()
 original=json.loads((q.DATA/'live-vs-recovery.process.txt').read_text(encoding='utf-8').strip().splitlines()[-1])
 q.record('live-vs-recovery',{'recover':recovered,'afterRecoveryBeforeOriginalResumes':committed,'originalExecute':original,'afterOriginalResumes':q.state(db),'retry':q.run('execute',db,'live-vs-recovery-retry',request=req)})
finally:
 if p.poll() is None:p.kill();p.wait()
 h.close()
