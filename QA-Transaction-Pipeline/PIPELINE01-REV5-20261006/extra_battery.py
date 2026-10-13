import extra_checks as x
q=x.q;q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'extra-results.json',q.RESULTS);print(k,str(v)[:180],flush=True)
q.record=record
x.identities();x.terminal_native();x.schema_extra();q.check()
