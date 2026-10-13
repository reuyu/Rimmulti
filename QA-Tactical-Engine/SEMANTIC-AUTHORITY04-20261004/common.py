import protocol as q
import json,re,base64,time,copy,shutil,hashlib
CLEAN=q.Q/'Frozen/TargetSettlement_Clean_ContextB.rws';EXPECTED='9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC'
if (q.DATA/'results.json').exists():q.RESULTS.update(json.loads((q.DATA/'results.json').read_text(encoding='utf-8')))
def state(h):return json.loads(h.o.send('INTERNAL'))
def manifest(h,label):
 m=json.loads(h.o.send('MANIFEST'));q.write(q.DATA/(label+'.manifest.json'),m);return m

def bundle(h,source=CLEAN,expected=EXPECTED,id='AUTH',**changes):
 b=dict(authorityId=id,expectedSourceArtifactHash=q.f.sha(source),manifestVersion='4.0',expectedManifestHash=expected,contentProfileFingerprint=q.f.sha(h.profile/'Config/ModsConfig.xml'),targetScopeId='SETTLEMENT-B',targetMapId=0,workerGeneration=state(h)['currentGeneration']+1,allowedOperationMode='SIMULATION');b.update(changes);return b

def register(h,b,label):q.write(q.DATA/(label+'.authority.json'),b);return h.cmd('REGISTER_AUTHORITY '+json.dumps(b,separators=(',',':')),label+'-register')
def grant(h,b,label,**changes):
 g=dict(grantId='GRANT-'+label,authorityId=b['authorityId'],workerGeneration=b['workerGeneration'],scopeId=b['targetScopeId'],targetMapIndex=b['targetMapId'],allowedMode=b['allowedOperationMode'],executionClass='TACTICAL_PROBE',tickBudget=20);g.update(changes);q.write(q.DATA/(label+'.grant.json'),g);r=h.cmd('REGISTER_GRANT '+json.dumps(g,separators=(',',':')),label+'-grant');return g,r

def admit(h,label,source=CLEAN,expected=EXPECTED,**changes):
 h.cmd('RESET_WORKER',label+'-reset');b=bundle(h,source,expected,id='AUTH-'+label,**changes);r=register(h,b,label);g,gr=grant(h,b,label);ready=h.load(source,label);v=h.cmd('VALIDATE_INPUT',label+'-validate');q.record(label+'-admission',{'authority':b,'grant':g,'register':r,'grantResponse':gr,'ready':ready,'validate':v,'state':state(h),'sourceSHA':q.f.sha(source)});return b,g,v

def seal(h,g,label):
 r=h.cmd('SEAL_RESULT '+g['grantId'],label+'-seal');s=json.loads(h.b.send('GET_SEALED_RESULT')) if r.startswith('RESULT_SEALED') else None;q.write(q.DATA/(label+'.sealed.json'),s);return s

def stage(h,label):
 r=h.cmd('STAGE_SAVE '+label,label+'-stage');m=re.search("StagingName='([^']+)'",r);name=m.group(1) if m else None;p=h.profile/'Saves'/((name or 'NONE')+'.rws');q.record(label+'-staging',{'response':r,'path':str(p),'exists':p.exists(),'sha':q.f.sha(p) if p.exists() else None,'state':state(h)});return r,name,p

def prepare(h,label,fault=None):
 b,g,v=admit(h,label);assert v.startswith('INPUT_VALIDATED'),v;s=seal(h,g,label);assert s is not None
 if fault:h.o.send('ARM '+fault)
 r,n,p=stage(h,label);return b,g,s,r,n,p

def craft(h,s,p,**changes):
 r=dict(receiptId='QA-CRAFT-'+str(time.time_ns()),stagedFilePath=str(p),stagedSha=q.f.sha(p),sealedResultId=s['sealedResultId'],resultEpoch=s['resultEpoch'],manifestVersion='4.0',sealedManifestHash=s['sealedManifestHash'],authorityId=s['authorityId'],grantId=s['grantId'],workerGeneration=s['workerGeneration'],scopeId=s['targetScopeId'],targetMapIndex=s['targetMapId'],contentProfileFingerprint=s['contentProfileFingerprint'],sourceArtifactHash=s['sourceArtifactHash'],validatorProcessId='2147483646',validatorResult='PASS',validatedAt='2026-10-04T00:00:00Z');r.update(changes);return r

def submit(h,r,label):q.write(q.DATA/(label+'.receipt.json'),r);return h.cmd('SUBMIT_STAGE_VALIDATION_RECEIPT '+json.dumps(r,separators=(',',':')),label+'-submit')
def promote(h,n,label):
 r=h.cmd('PROMOTE_STAGED '+str(n)+' '+label,label+'-promote');p=h.profile/'Saves'/(label+'.rws');q.record(label+'-final',{'response':r,'path':str(p),'exists':p.exists(),'sha':q.f.sha(p) if p.exists() else None,'facts':q.facts(p) if p.exists() else None,'state':state(h)});return r,p

def validate(v,sim,s,p,label,expected=None):
 m=s['sealedManifestHash'] if expected is None else expected
 b,g,vr=admit(v,label,source=p,expected=m,allowedOperationMode='READ_ONLY')
 if not vr.startswith('INPUT_VALIDATED'):return None,vr
 # Exact loaded name must equal staged basename, not the authority registration label.
 # Register/reload again with authority generation of next load.
 v.cmd('RESET_WORKER',label+'-named-reset');b=bundle(v,p,m,id='AUTH-V-'+label,allowedOperationMode='READ_ONLY');register(v,b,label+'-named');grant(v,b,label+'-named');assert v.load(p,p.stem);v.cmd('VALIDATE_INPUT',label+'-named-validate');live=manifest(v,label+'-loaded')
 encoded=base64.b64encode(json.dumps(s,separators=(',',':')).encode()).decode();r=v.cmd('VALIDATE_AS_PRE_PROMOTION_VALIDATOR '+s['authorityId']+' '+encoded+' '+str(p)+' '+q.f.sha(p),label+'-validator-command');receipt=json.loads(r.split('Receipt=',1)[1]) if r.startswith('STAGE_VALIDATED: Receipt=') else None
 q.record(label+'-fresh-proof',{'simulatorPID':sim.p.pid,'validatorPID':v.p.pid,'savedata':str(v.profile),'sourceSHA':q.f.sha(p),'activeModsConfigSHA':q.f.sha(v.profile/'Config/ModsConfig.xml'),'authority':b,'expectedSealed':s,'loadedManifestHash':live['hash'],'receipt':receipt,'response':r});return receipt,r

def cleanup():
 q.STOP.set()
 for h in q.OWNED:
  if h.p.poll() is None:
   try:h.close()
   except Exception:h.p.kill();h.p.wait(timeout=10)
 q.check()
