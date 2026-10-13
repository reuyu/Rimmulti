import run_checks as q
import extra_checks as extra
import json,time
q.RESULTS.update(json.loads((q.E/'results.json').read_text(encoding='utf-8')))
q.check()
q.run('meta',q.D/'schema-base.db','metadata-final')
q.run('fingerprints',q.fresh('fingerprint-complete'),'fingerprint-complete')
q.run('startup',q.D/'inputs.db','invalid-json-name-durable-restart')
# Earlier wrappers used PROFILE rather than the helper's default PROBE_PROFILE_V1;
# these COLLISION_REJECTED outcomes are harness envelope mismatches, not retry regressions.
for point in ['after-cas','after-audit','native-commit','native-wal']:
 db=q.D/('shutdown-'+point+'.db');q.run('historical',db,'shutdown-query-exact-'+point,principal='P',op='BOUNDARY');q.execute(db,'shutdown-retry-exact-'+point,scope='BOUNDARY',name='BOUNDARY',ContentProfileFingerprint='PROBE_PROFILE_V1')
for name in ['queue-held','queue-lock']:
 db=q.D/(name+'.db');q.run('historical',db,name+'-query-exact',principal='P',op='Q0');q.execute(db,name+'-retry-exact',scope='QUEUE',name='Q0',ContentProfileFingerprint='PROBE_PROFILE_V1')
# Reconstitute the recorded durable NOT-PRESENT snapshot from the >38s lock experiment.
# This is explicitly a QA recovery fixture; the physical original was already retried by final_checks.
before=q.RESULTS['long-lock-results']['beforeRetry'];db=q.clone(q.D/'schema-base.db',q.D/'long-lock-recorded-recovery.db')
with q.conn(db) as c:
 c.execute('delete from StoreIncarnations')
 c.executemany('insert into StoreIncarnations values(?,?,?,?)',before['tables']['StoreIncarnations'])
q.record('long-lock-reconstructed-equality',q.truth(db)==before);q.run('startup',db,'long-lock-recorded-recovery-restart');q.run('historical',db,'long-lock-recorded-no-receipt',principal='P',op='Q0');q.execute(db,'long-lock-recorded-exact-retry',scope='QUEUE',name='Q0',ContentProfileFingerprint='PROBE_PROFILE_V1')
# Correctly hashed duplicate receipt, so an unrelated hash failure cannot hide cardinality failure.
db=q.clone(q.D/'same-stream.db',q.D/'consistency-duplicate-receipt-valid.db')
with q.conn(db) as c:
 r=list(c.execute('select * from CommitReceipts limit 1').fetchone());r[0]+='_duplicate';r[-1]=q.hashlib.sha256(':'.join(str(x) for x in r[:-1]).encode()).hexdigest().upper();c.execute('insert into CommitReceipts values('+','.join('?' for _ in r)+')',r)
q.run('startup',db,'consistency-duplicate-receipt-valid');extra.normal('consistency-duplicate-receipt-valid',db)
# Foreign key target-column mutation distinct from source-column mutation.
db=q.clone(q.D/'schema-base.db',q.D/'schema-fk-target.db');q.rebuild_table(db,'CommitReceipts',lambda s:s.replace('REFERENCES OperationRecords(PrincipalId, OperationId)','REFERENCES OperationRecords(OperationId, PrincipalId)'));q.run('startup',db,'schema-fk-target');extra.normal('schema-fk-target',db)
extra.normal('schema-index-partial',q.D/'schema-index-partial.db')
after=q.f.tree();q.f.write(q.Q/'freeze-after.json',after);before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('freeze-reconciled',{'count':len(after),'changes':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]});q.check()
