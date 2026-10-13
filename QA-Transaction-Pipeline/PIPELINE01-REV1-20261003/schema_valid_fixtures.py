import run_checks as q
import json,sqlite3
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
source=q.DATA/'meta.db'
with sqlite3.connect(source) as c:
 ddl=c.execute("select name,sql from sqlite_master where type='table' and sql is not null").fetchall()
 indexes=c.execute("select sql from sqlite_master where type='index' and sql is not null").fetchall()
 incarnation=c.execute('select * from StoreIncarnations').fetchall()
for label,table,old,new in [('wrong-pk-valid','OperationRecords','PRIMARY KEY (PrincipalId, OperationId)','PRIMARY KEY(PrincipalId), UNIQUE(PrincipalId,OperationId)'),('no-event-unique-valid','PublicationEvents','EventId TEXT NOT NULL UNIQUE','EventId TEXT NOT NULL')]:
 db=q.DATA/('schema-'+label+'.db')
 with sqlite3.connect(db) as c:
  for name,sql in ddl:c.execute(sql.replace(old,new) if name==table else sql)
  for (sql,) in indexes:c.execute(sql)
  c.executemany('insert into StoreIncarnations values (?,?,?,?)',incarnation)
  c.execute('pragma application_id=1463898693');c.execute('pragma user_version=2')
 result={'validate':q.run('validate',db,'schema-'+label),'startup':q.run('startup',db,'schema-'+label+'-startup'),'integrity':q.sql(db,'pragma integrity_check'),'schema':q.sql(db,'select sql from sqlite_master where name=?',(table,))}
 if label=='wrong-pk-valid':
  result['first']=q.run('execute',db,'schema-wrong-pk-first',request=q.request('schema-wrong-pk-first'))
  result['second']=q.run('execute',db,'schema-wrong-pk-second',request=q.request('schema-wrong-pk-second',OperationId='SECOND',ExpectedProbeRevision=1))
 result['db']=q.state(db);q.record('schema-'+label,result)
print('VALID SCHEMA FIXTURES DONE',flush=True)
