import extra_checks as x
import json
q=x.q;q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'collation-confirmation-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=record
for name in ['OperationRecords','ProbeAggregates']:x.normal('rev5-collation-'+name,q.D/('collation-'+name+'.db'))
db=q.fresh('case-control');q.execute(db,'case-P',principal='P',name='SAME',scope='S');q.execute(db,'case-p',principal='p',name='SAME',scope='s');q.run('startup',db,'case-control-ready')
for name in ['schema-base','collation-OperationRecords','collation-ProbeAggregates']:
 with q.conn(q.D/(name+'.db')) as c:
  facts={t:{'ddl':c.execute('select sql from sqlite_master where name=?',(t,)).fetchone()[0],'indexes':{r[1]:list(c.execute('pragma index_xinfo('+r[1]+')')) for r in c.execute('pragma index_list('+t+')').fetchall()}} for t in ['OperationRecords','ProbeAggregates']}
 q.record(name+'-collation-facts',facts)
q.check()
