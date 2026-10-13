import run_checks as q
import json,time,threading,hashlib,re
q.RESULTS.update(json.loads((q.E/'results.json').read_text(encoding='utf-8')))
q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 q.run('normal-lifetime',q.D/'lifetime.db','actual-main-shutdown-lifetime',timeout=15)
 for point in ['after-cas','after-audit','native-commit','native-wal']:
  db=q.fresh('shutdown-'+point);signal=q.E/('shutdown-'+point+'.signal');release=q.E/('shutdown-'+point+'.release')
  q.run('shutdown-boundary',db,'shutdown-boundary-'+point,timeout=25,point=point,signal=signal,release=release)
  before=q.truth(db);q.run('startup',db,'shutdown-restart-'+point);q.execute(db,'shutdown-retry-'+point,scope='BOUNDARY',name='BOUNDARY');q.record('shutdown-truth-'+point,{'beforeRetry':before,'afterRetry':q.truth(db)})
 # Native post-WAL hook supplies an independent after-commit/pre-response hard-kill cut.
 for point in ['before-cas','native-wal']:
  db=q.fresh('hardkill-extra-'+point);request=q.req(db);signal=q.E/('kill-extra-'+point+'.signal');release=q.E/('kill-extra-'+point+'.release');p,log=q.spawn('execute',db,'hardkill-extra-'+point,request=request,point=point,signal=signal,release=release);q.barrier(signal,p);p.kill();p.wait();log.close();before=q.truth(db);q.run('startup',db,'hardkill-extra-restart-'+point);q.run('execute',db,'hardkill-extra-retry-'+point,request=request);q.record('hardkill-extra-truth-'+point,{'pid':p.pid,'beforeRetry':before,'afterRetry':q.truth(db)})
 db=q.fresh('long-lock');c=q.conn(db);c.execute('BEGIN IMMEDIATE');start=time.monotonic();signal=q.E/'long-lock.signal';release=q.E/'long-lock.release';p,log=q.spawn('queue-lock',db,'long-lock',signal=signal,release=release,n=1205)
 try:q.barrier(signal,p,seconds=42);time.sleep(32)
 finally:c.rollback();c.close();elapsed=time.monotonic()-start;release.write_text('release',encoding='utf-8')
 p.wait(timeout=15);log.close();rows=[json.loads(x) for x in (q.E/'long-lock.stdout').read_text(encoding='utf-8').splitlines() if x.startswith('{')];before=q.truth(db);q.record('long-lock-results',{'pid':p.pid,'lockHeldSeconds':elapsed,'rows':rows,'beforeRetry':before});q.run('startup',db,'long-lock-restart');q.execute(db,'long-lock-retry',scope='QUEUE',name='Q0')
 # Independent canonical schema descriptor reconstruction with Python sqlite metadata.
 with q.conn(q.D/'schema-base.db') as c:
  tables=[r[0] for r in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
  assert tables==['AuditRecords','CommitReceipts','OperationRecords','ProbeAggregates','ProbeRevisionHistory','PublicationEvents','StoreIncarnations']
  lines=[f"APP:{c.execute('pragma application_id').fetchone()[0]};VER:{c.execute('pragma user_version').fetchone()[0]}"]
  shape={}
  for t in tables:
   lines.append('TABLE:'+t);cols=c.execute(f"pragma table_info('{t}')").fetchall();shape[t]={'columns':cols,'foreignKeys':c.execute(f"pragma foreign_key_list('{t}')").fetchall(),'indexes':[]}
   lines.extend(f'  COL:{r[1]}|{r[2].upper()}|{r[3]}|{r[5]}' for r in cols)
   lines.extend(sorted(f'  FK:{r[0]}:{r[1]}:{r[3]}->{r[2]}({r[4]})|UPD:{r[5]}|DEL:{r[6]}' for r in shape[t]['foreignKeys']))
   for r in sorted(c.execute(f"pragma index_list('{t}')").fetchall(),key=lambda x:x[1]):
    columns=[i[2] for i in c.execute(f"pragma index_info('{r[1]}')")];shape[t]['indexes'].append({'metadata':r,'columns':columns});lines.append(f"  IDX:{r[1]}|UNIQ:{r[2]}|ORIGIN:{r[3]}|COLS:{','.join(columns)}")
  for name,t,sql in c.execute("select name,tbl_name,sql from sqlite_master where type='trigger' order by name"):
   lines.append(f"TRIGGER:{name}|ON:{t}|SQL:{re.sub(r'\s+',' ',sql.strip().lower())}")
  for name,sql in c.execute("select name,sql from sqlite_master where type='table' and name not like 'sqlite_%' order by name"):
   sql=re.sub(r'\s+',' ',sql.strip().lower())
   for m in re.finditer(r'check\s*\((.*?)\)',sql,re.I):lines.append(f'CHECK:{name}|{m.group(1).strip()}')
  descriptor='\r\n'.join(lines)+'\r\nACTIVE_INCARNATIONS:'+str(c.execute('select count(*) from StoreIncarnations where IsActive=1').fetchone()[0]);sig=hashlib.sha256(descriptor.encode()).hexdigest().upper()
  q.f.write(q.E/'independent-schema.json',{'signature':sig,'expectedSignature':'0B9C2C39AA681138DD671F181299BBE66ED1660E50FDCB3D1FCE831DCFED7F56','match':sig=='0B9C2C39AA681138DD671F181299BBE66ED1660E50FDCB3D1FCE831DCFED7F56','shape':shape,'descriptor':descriptor})
 # Full release manifest inclusion and exact hash check, not just matching Server DLL.
 manifest=json.loads((q.R/'RELEASE_MANIFEST_PIPELINE_REV3.json').read_text(encoding='utf-8'));records=[]
 for name,v in manifest['Files'].items():
  p=q.f.BIN/name;records.append({'name':name,'expected':v['sha256'],'actual':q.f.sha(p),'bytes':p.stat().st_size,'match':q.f.sha(p)==v['sha256'] and p.stat().st_size==v['bytes']})
 residues=[str(p.relative_to(q.f.BIN)) for p in q.f.BIN.rglob('*') if p.is_file() and ('.db' in p.name.lower() or any(p.name.lower().endswith(x) for x in ['.tmp','.log']) or 'test' in p.name.lower())]
 q.record('release-provenance',{'manifestSha':q.f.sha(q.R/'RELEASE_MANIFEST_PIPELINE_REV3.json'),'e1Sha':q.f.sha(q.R/'scratch/pipeline_e1_rev3_results.json'),'files':records,'residues':residues})
 q.check()
finally:
 q.STOP.set()
 for p in q.OWNED:
  if p.poll() is None:p.kill();p.wait()
 after=q.f.tree();q.f.write(q.Q/'freeze-after.json',after);before=json.loads((q.Q/'freeze-before.json').read_text(encoding='utf-8'));q.record('freeze-final',{'count':len(after),'changes':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]})
