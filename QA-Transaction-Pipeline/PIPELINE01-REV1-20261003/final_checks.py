import run_checks as q
import json, hashlib
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
db=q.DATA/'identity.db'
fp=q.sql(db,"select RequestFingerprint from OperationRecords where PrincipalId='P_A' and OperationId='OP'")[0][0]
q.record('caller-hash-authority', {
 'samePayloadWrongHash':q.run('execute',db,'caller-hash-same',request=q.request('caller-hash-same',CallerSuppliedPayloadHash='WRONG_HASH')),
 'changedPayloadOriginalFingerprint':q.run('execute',db,'caller-hash-changed',request=q.request('caller-hash-changed',PayloadJson='{"a":999}',CallerSuppliedPayloadHash=fp)),
 'originalFingerprint':fp})
before=json.loads((q.QA/'freeze-before.json').read_text(encoding='utf-8'))
after={str(p.relative_to(q.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest().upper() for p in (q.ROOT/'WarEconomyMod').rglob('*') if p.is_file() and p.suffix.lower() in ('.cs','.csproj','.dll','.exe','.json','.pdb')}
changes=[{'path':k,'before':before.get(k,{}).get('sha256'),'after':after.get(k)} for k in set(before)|set(after) if before.get(k,{}).get('sha256')!=after.get(k)]
q.record('freeze-final',{'filesBefore':len(before),'filesAfter':len(after),'changes':changes})
print('RESULT KEYS:', ', '.join(q.RESULTS))
for k in ['metadata','queue-delay','queue-starved-proof','aborted','normal-fresh','normal-pending','normal-missing-column','incarnation-race','release-battery']:
 print(k,json.dumps(q.RESULTS.get(k),ensure_ascii=False)[:11000])
