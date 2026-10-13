import run_checks as q
q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'schema-collation-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=record
for table,col in [('OperationRecords','PrincipalId'),('ProbeAggregates','ProbeScopeId')]:
 db=q.clone(q.D/'schema-base.db',q.D/('collation-'+table+'.db'));before=q.truth(db)
 q.rebuild_table(db,table,lambda s:s.replace(col+' TEXT',col+' TEXT COLLATE NOCASE'));after=q.truth(db);assert before!=after
 q.run('startup',db,'collation-'+table+'-ready')
 if table=='OperationRecords':
  q.execute(db,'collation-actor-P',name='SAME',principal='P',scope='S1');q.execute(db,'collation-actor-p',name='SAME',principal='p',scope='S2')
 else:
  q.execute(db,'collation-scope-S',name='ONE',scope='S');q.execute(db,'collation-scope-s',name='TWO',scope='s')
 q.record('collation-'+table+'-truth',q.truth(db))
q.check()
