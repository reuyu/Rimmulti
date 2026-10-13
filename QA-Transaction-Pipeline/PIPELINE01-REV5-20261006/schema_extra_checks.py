import run_checks as q
import json
q.RESULTS={}
def record(k,v):q.RESULTS[k]=v;q.f.write(q.E/'schema-extra-results.json',q.RESULTS);print(k,str(v)[:200],flush=True)
q.record=record
base=q.D/'schema-base.db'
cases={
 'literal-escaped':lambda d:q.rebuild_table(d,'OperationRecords',lambda s:s.replace("'COMMITTED'","'COM''MITTED'")),
 'check-comment':lambda d:q.rebuild_table(d,'ProbeAggregates',lambda s:s.replace('CHECK (ProbeRevision >= 0)','CHECK (1 /* ProbeRevision >= 0 */)')),
 'trigger-comment':lambda d:q.sql(d,"DROP TRIGGER trg_operation_records_no_update;CREATE TRIGGER trg_operation_records_no_update BEFORE UPDATE ON OperationRecords BEGIN SELECT 1 /* RAISE(ABORT,'immutable') */;END"),
 'trigger-expression':lambda d:q.sql(d,"DROP TRIGGER trg_operation_records_no_update;CREATE TRIGGER trg_operation_records_no_update BEFORE UPDATE ON OperationRecords WHEN 1=0 BEGIN SELECT RAISE(ABORT,'immutable');END"),
 'fk-target':lambda d:q.rebuild_table(d,'CommitReceipts',lambda s:s.replace('REFERENCES OperationRecords(PrincipalId, OperationId)','REFERENCES OperationRecords(OperationId, PrincipalId)')),
 'fk-update':lambda d:q.rebuild_table(d,'AuditRecords',lambda s:s.replace('ON UPDATE NO ACTION','ON UPDATE CASCADE')),
 'index-unique':lambda d:q.sql(d,'DROP INDEX IX_PublicationEvents_Stream_Seq;CREATE UNIQUE INDEX IX_PublicationEvents_Stream_Seq ON PublicationEvents(StreamId,Seq)'),
 'history-principal-nullable':lambda d:q.rebuild_table(d,'ProbeRevisionHistory',lambda s:s.replace('PrincipalId TEXT NOT NULL','PrincipalId TEXT')),
 'history-principal-type':lambda d:q.rebuild_table(d,'ProbeRevisionHistory',lambda s:s.replace('PrincipalId TEXT NOT NULL','PrincipalId INTEGER NOT NULL')),
 'history-fk-principal':lambda d:q.rebuild_table(d,'ProbeRevisionHistory',lambda s:s.replace('FOREIGN KEY (PrincipalId, OperationId)','FOREIGN KEY (ProbeScopeId, OperationId)')),
 'history-pk-order':lambda d:q.rebuild_table(d,'ProbeRevisionHistory',lambda s:s.replace('PRIMARY KEY (ProbeScopeId, ProbeRevision)','PRIMARY KEY (ProbeRevision, ProbeScopeId)')),
 'audit-fk-target':lambda d:q.rebuild_table(d,'AuditRecords',lambda s:s.replace('REFERENCES OperationRecords(PrincipalId, OperationId)','REFERENCES OperationRecords(OperationId, PrincipalId)')),
 }
for name,edit in cases.items():
 db=q.clone(base,q.D/('v6-schema-'+name+'.db'));old=q.truth(db);edit(db);before=q.truth(db);assert old!=before,name+' mutation no effect';q.run('startup',db,'v6-schema-'+name);q.record(name+'-preserved',before==q.truth(db))
q.check()
