from pathlib import Path
import run_checks as q
import json
q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.f.write(q.E/'valid-consistency-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=rec
db=q.fresh('valid-stream-eight')
for i in range(8):q.execute(db,'valid-seed-'+str(i),name='V'+str(i),expected=i)
q.run('startup',db,'valid-stream-eight-ready')
s=Path(__file__).with_name('extra_checks.py').read_text(encoding='utf-8')
s=s[s.index('def consistency():'):s.index('\ndef shutdown():')].replace("base=q.D/'same-stream.db'","base=q.D/'valid-stream-eight.db'").replace('consistency-','valid-consistency-')
exec(compile(s,'valid-consistency-generated','exec'));consistency();q.check()
