import run_checks as q
import threading,json
q.RESULTS['fingerprint-matrix']={'note':'Old direct surrogate fingerprint helper not used as admission proof; actual Inputs will run separately.'}
q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 q.fingerprint_identity();q.concurrency();q.terminal_and_fence();q.storage_kills();q.schema_cases();q.check()
finally:
 q.STOP.set()
 for p in q.OWNED:
  if p.poll() is None:p.kill();p.wait()
 q.record('base-final-freeze',{'unchanged':json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'))==q.f.tree()})
