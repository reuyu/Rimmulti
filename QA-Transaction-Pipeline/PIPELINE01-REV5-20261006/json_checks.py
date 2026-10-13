from pathlib import Path
import run_checks as q
import json,time,threading,hashlib,shutil,sqlite3,subprocess
q.RESULTS={}
def record(k,v):
 q.RESULTS[k]=v;q.f.write(q.E/'json-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:400],flush=True)
q.record=record
q.H=q.Q/'HarnessExt/bin/Release/net8.0/Harness.dll'
out=q.H.parent
for p in (q.Q/'Candidate').glob('*.dll'):
 if not (out/p.name).exists():shutil.copy2(p,out/p.name)
shutil.copy2(q.Q/'Candidate/runtimes/win-x64/native/e_sqlite3.dll',out/'e_sqlite3.dll')

def batch():
 db=q.fresh('deep-json');inc=q.truth(db)['tables']['StoreIncarnations'][0][0]
 cases=[('tinypos','1e-29'),('tinyneg','-1e-29'),('tiny40','1e-40'),('zero','0'),('precision1','1.00000000000000000000000000001'),('precision2','1.00000000000000000000000000002'),('frac1','0.123456789012345678901234567891'),('frac2','0.123456789012345678901234567892')]
 for n in ['1e308','1e-308','1e309','1e-309','1e2147483648','1e-2147483648','1E+000','1.0','1e0','1','0.0','-0','-0e308','0e-308','0e309']:cases.append(('num'+str(len(cases)),n))
 cases+= [('mant1000','9'*1000),('mant1001','9'*1001),('mantZeroLead','0.'+'0'*400+'1'),('mant1000scaled','9'*1000+'e-308'),('dup-root','{"a":1,"a":2}'),('dup-nested','{"x":{"a":1,"a":2}}'),('dup-array','[{"a":1,"a":2}]'),('dup-escaped','{"a":1,"\\u0061":2}'),('sur-key','{"\\ud800":1}'),('sur-value','{"a":"\\ud800"}'),('sur-low','"\\udc00"'),('sur-reversed','"\\udc00\\ud800"'),('sur-valid','"\\ud83d\\ude00"'),('second-root','{} {}'),('trailing','{}x'),('trailing-space','{} \r\n\t'),('depth64','['*64+'0'+']'*64),('depth65','['*65+'0'+']'*65),('size1mb',json.dumps('x'*1048576)),('size4mb',json.dumps('x'*4194304))]
 requests=[]
 for name,payload in cases:requests.append(dict(PrincipalId='P',OperationId=name,ProbeScopeId=name,ExpectedProbeRevision=0,StoreIncarnationId=inc,ContentProfileFingerprint='PROFILE',PayloadJson=payload))
 # Equivalent spellings and collisions use one operation ID each on actual production coordinator.
 for group,vals in [('eq',['1','1.0','1e0','1E+000']),('zeroeq',['0','-0','0.0','0e308','-0e-308']),('tinycollision',['1e-29','-1e-29']),('tiny40collision',['1e-40','0']),('pcollision',['1.00000000000000000000000000001','1.00000000000000000000000000002']),('fcollision',['0.123456789012345678901234567891','0.123456789012345678901234567892'])]:
  for v in vals:requests.append(dict(PrincipalId='P',OperationId=group,ProbeScopeId=group,ExpectedProbeRevision=0,StoreIncarnationId=inc,ContentProfileFingerprint='PROFILE',PayloadJson=v))
 f=q.E/'deep-json.requests.json';q.f.write(f,requests);q.run('batch',db,'json-full',timeout=60,request=f)
 q.record('json-truth',q.truth(db))

batch();q.check()
