import run_checks as q
import json
q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.f.write(q.E/'input-validation-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=rec
q.run('inputs',q.fresh('all-inputs'),'all-inputs');q.run('meta',q.D/'all-inputs.db','extended-loaded-metadata');q.record('inputs-truth',q.truth(q.D/'all-inputs.db'));q.check()
