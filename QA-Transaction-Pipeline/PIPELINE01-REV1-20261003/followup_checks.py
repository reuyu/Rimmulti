import run_checks as q
import json,sqlite3,subprocess,hashlib,shutil
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
receiptDB=q.DATA/'identity.db';zones=[]
for culture,zone in [('en-US','UTC'),('ko-KR','Korea Standard Time'),('tr-TR','Turkey Standard Time'),('ar-SA','Arab Standard Time'),('de-DE','W. Europe Standard Time')]:
 zones.append(q.run('receipt',receiptDB,'actualzone-'+culture,culture=culture,process_zone=zone))
q.record('receipt-process-timezones',{'note':'process-only TimeZoneInfo.Local cache fixture; no OS/user timezone change and no candidate code patch','reloads':zones})
db=q.DATA/'identity.db';copy=q.DATA/'terminal-transition.db'
with sqlite3.connect(db) as a,sqlite3.connect(copy) as b:a.backup(b)
q.record('terminal-transition-api',{'before':q.state(copy),'transition':q.run('terminal-transition',copy,'terminal-transition-api'),'after':q.state(copy)})
q.record('fixture-mismatch-same-process',q.run('fixture-mismatch',db,'fixture-mismatch-same-process'))
# Force restore rotation in real gap AFTER active incarnation read, BEFORE BEGIN transaction.
db=q.init('incarnation-race');old=q.sql(db,'select IncarnationId from StoreIncarnations where IsActive=1')[0][0]
req=q.request('incarnation-race',StoreIncarnationId=old)
try:
 p,h,sig,rel=q.checkpoint(db,'incarnation-race','after-active-read',request=req,profile_incarnation='yes')
 rotation=q.run('rotate',db,'incarnation-race-rotate');rel.write_text('release');p.wait(timeout=15);h.close()
 output=json.loads((q.DATA/'incarnation-race.process.txt').read_text(encoding='utf-8').strip().splitlines()[-1])
 q.record('incarnation-race',{'old':old,'rotation':rotation,'executor':output,'db':q.state(db),'observer':'native SQLite PROFILE callback on pooled handle after SELECT IncarnationId; return value untouched'})
except Exception as ex:q.record('incarnation-race',{'notReproduced':repr(ex)})
# Unknown application claimed as ours on a zero-version existing database.
db=q.DATA/'foreign-app-v0.db';q.sql(db,'pragma application_id=42');q.sql(db,"create table ForeignSentinel(Value text)");q.sql(db,"insert into ForeignSentinel values ('foreign data')")
q.record('foreign-app-v0',{'beforeApp':42,'init':q.run('validate',db,'foreign-app-v0'),'after':q.state(db)})
# Legacy migration validates AFTER committing; incompatible residual object causes partial conversion/data loss.
rev0=q.ROOT/'QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/kill-after-commit.db';db=q.DATA/'legacy-partial-migration.db'
with sqlite3.connect(rev0) as a,sqlite3.connect(db) as b:a.backup(b)
q.sql(db,'create view ConsumerCursors as select 1 as Bogus')
old={t:q.sql(db,'select * from '+t) for t in ['OperationRecords','ProbeAggregates','CommitReceipts']}
q.record('legacy-partial-migration',{'before':old,'migration':q.run('validate',db,'legacy-partial-migration'),'after':q.state(db)})
# Legacy PREPARED cannot be forwarded; record the actual destructive migration instead of granting durability closure.
db=q.DATA/'legacy-prepared.db';source=q.ROOT/'QA-Transaction-Pipeline/PIPELINE01-20261002/Evidence/kill-after-prepared.db'
with sqlite3.connect(source) as a,sqlite3.connect(db) as b:a.backup(b)
q.sql(db,"update OperationRecords set State='PREPARED'");q.sql(db,'delete from PublicationOutbox');q.sql(db,'delete from CommitReceipts');q.sql(db,'delete from ProbeRevisionHistory');q.sql(db,'delete from ProbeAggregates')
q.record('legacy-prepared',{'before':q.sql(db,'select OperationId,State from OperationRecords'),'migration':q.run('validate',db,'legacy-prepared'),'after':q.state(db)})
# Actual SQLITE_LOCKED via observer throwing provider code6, error-path verification only (not natural lock workload).
# Native lock5 and native constraint19 were already exercised. Treat LOCKED branch as static/limited if no natural code6.
# Provenance and immutable candidate recheck.
before=json.loads((q.QA/'freeze-before.json').read_text(encoding='utf-8'));changes=[]
after={}
for p in (q.ROOT/'WarEconomyMod').rglob('*'):
 if p.is_file() and p.suffix.lower() in ('.cs','.csproj','.dll','.exe','.json','.pdb'):after[str(p.relative_to(q.ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest().upper()
for k in set(before)|set(after):
 if before.get(k,{}).get('sha256')!=after.get(k):changes.append({'path':k,'old':before.get(k,{}).get('sha256'),'new':after.get(k)})
q.record('freeze-after',{'filesBefore':len(before),'filesAfter':len(after),'changes':changes})
print('FOLLOWUP DONE',flush=True)
