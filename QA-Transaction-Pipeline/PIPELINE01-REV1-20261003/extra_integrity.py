import run_checks as q
import json,hashlib
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
db=q.DATA/'aborted.db'
q.record('aborted-new-id-same-attempt',{
 'execute':q.run('execute',db,'aborted-new-id-same-attempt',request=q.request('aborted-new-id-same-attempt',OperationId='NEW_STALE_ATTEMPT',ExpectedProbeRevision=5)),
 'retry':q.run('execute',db,'aborted-new-id-same-attempt-retry',request=q.request('aborted-new-id-same-attempt',OperationId='NEW_STALE_ATTEMPT',ExpectedProbeRevision=5)),
 'records':q.sql(db,'select PrincipalId,OperationId,ExpectedProbeRevision,State,FailureReason from OperationRecords')})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest().upper()
deps=[]
for source in (q.QA/'FrozenRelease').rglob('*'):
 if not source.is_file() or source.suffix.lower() not in ('.dll','.json'):continue
 target=q.QA/'Harness/bin/Debug/net8.0'/source.relative_to(q.QA/'FrozenRelease')
 deps.append({'relativePath':str(source.relative_to(q.QA/'FrozenRelease')),'frozenSha256':sha(source),'harnessSha256':sha(target) if target.exists() else None,'sameBytes':target.exists() and sha(source)==sha(target)})
q.record('runtime-copy-identity',deps)
