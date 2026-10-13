import common as g
import json,threading,copy,time
q=g.q;q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.write(q.DATA/'battery-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:320],flush=True)
q.record=rec
q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 h=q.Host('RegressionBattery',4)
 # Persistent wrong inputs: clean expected truth remains fixed; input SHA intentionally matches each corrupted package.
 for i in range(1,16):
  key=f'{i:02}';root=q.E.parse(g.CLEAN).getroot();q.mutate(root,key);p=q.DATA/('input-'+key+'.rws');q.E.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
  b,gr,validation=g.admit(h,'Input'+key,source=p);live=g.manifest(h,'input-'+key+'-live');cp,c=h.census('input-'+key);commands={cmd:h.cmd(cmd+' '+arg,'input-'+key+'-'+cmd) for cmd,arg in [('STEP_TICKS','1 1'),('SEAL_RESULT',gr['grantId']),('STAGE_SAVE','Negative'+key),('PROMOTE_STAGED','Input'+key+' Bypass'+key)]}
  q.record('input-'+key,{'expectedFacts':q.facts(g.CLEAN),'injectedFacts':q.facts(p),'sourceSHA':q.f.sha(p),'finalLiveManifestHash':live['hash'],'finalLiveManifest':json.loads(live['json']),'comparator':h.compare(q.Q/'Frozen/TargetSettlement_Clean_ContextB.census.json'),'validation':validation,'state':g.state(h),'commands':commands,'finalExists':(h.profile/'Saves'/('Bypass'+key+'.rws')).exists()})
 # Original save byte attacks: observer changes bytes before candidate records staged SHA; live state remains clean.
 for fault in ['silent-skill','silent-hediff','silent-holder','broken-tail','trailing','dtd']:
  b,gr,s,stage,n,p=g.prepare(h,'Stage_'+fault,fault=fault);pr,out=g.promote(h,n,'StageFinal_'+fault);q.record('stage-'+fault,{'stage':stage,'promotion':pr,'exists':out.exists(),'faultProof':json.loads((h.profile/'save-fault-evidence.json').read_text(encoding='utf-8')),'state':g.state(h)})
 # Metadata checks and lifecycle; every trial re-admits clean fixture explicitly.
 b,gr,v=g.admit(h,'Idempotence');h.cmd('RESET_WORKER');b=g.bundle(h,id='IMMUTABLE');r1=g.register(h,b,'identical-first');r2=g.register(h,b,'identical-second');b2=b|{'targetMapId':1};r3=g.register(h,b2,'changed-bundle');q.record('authority-idempotence',{'first':r1,'identical':r2,'changed':r3,'state':g.state(h)})
 for field,value in [('expectedSourceArtifactHash','0'*64),('manifestVersion','wrong'),('expectedManifestHash','0'*64),('contentProfileFingerprint','0'*64),('targetMapId',1),('workerGeneration',999),('targetScopeId','FOREIGN-SCOPE'),('allowedOperationMode','READ_ONLY')]:
  label='Auth_'+field
  try:b,gr,v=g.admit(h,label,**{field:value});commands={cmd:h.cmd(cmd+' '+arg,label+'-'+cmd) for cmd,arg in [('STEP_TICKS','1 1'),('SEAL_RESULT',gr['grantId']),('STAGE_SAVE',label),('PROMOTE_STAGED',label+' '+label+'Final')]};q.record('authority-'+field,{'admission':v,'commands':commands,'state':g.state(h)})
  except Exception as e:q.record('authority-'+field,{'qaException':repr(e),'state':g.state(h)})
 # Valid scope vs grant metadata: no attempt to implement missing production authentication.
 for field,value in [('authorityId','OTHER'),('workerGeneration',999),('targetMapIndex',1),('scopeId','OTHER'),('allowedMode','INVALID'),('grantId','')]:
  b,gr,v=g.admit(h,'Grant_'+field);bad=gr|{field:value};r=h.cmd('REGISTER_GRANT '+json.dumps(bad));st=g.state(h);step=h.cmd('STEP_TICKS 1 1');seal=h.cmd('SEAL_RESULT '+gr['grantId']);q.record('grant-'+field,{'register':r,'afterValidation':st,'step':step,'seal':seal,'after':g.state(h)})
 for label,idval in [('unknown','UNKNOWN'),('blank','')]:
  b,gr,v=g.admit(h,'Seal_'+label);r=h.cmd('SEAL_RESULT '+idval);q.record('seal-'+label,{'response':r,'state':g.state(h),'stepAfter':h.cmd('STEP_TICKS 1 1')})
 b,gr,v=g.admit(h,'AfterLoad');r=g.register(h,g.bundle(h,id='NEW-AFTER-LOAD'),'after-load');q.record('authority-after-load',{'response':r,'state':g.state(h),'step':h.cmd('STEP_TICKS 1 1')})
 # Native same-tick changes must invalidate sealed truth, including full manifest fields omitted by comparator.
 for m in ['followFieldwork','plantAge','billSuspended','hediffPart','hediffId']:
  b,gr,s,sr,n,p=g.prepare(h,'Native_'+m);r=h.o.send('MUTATE '+m);ss=h.cmd('STAGE_SAVE NativeBlocked_'+m);q.record('native-'+m,{'mutation':r,'stage':ss,'state':g.state(h)})
 b,gr,v=g.admit(h,'Jobs');job=json.loads(h.o.send('JOB'));before=g.manifest(h,'job-before');resBefore=json.loads(h.o.send('RESERVATIONS'));m=h.o.send('MUTATE jobTarget');after=g.manifest(h,'job-target-after');q.record('job-target-scope',{'job':job,'reservations':resBefore,'mutation':m,'beforeHash':before['hash'],'afterHash':after['hash'],'hashEqual':before['hash']==after['hash'],'beforeJob':h.snap('job-target-native')['maps'][0]['entities']['Human302']['pawn']['job']})
 h.o.send('MUTATE clearReservations');removed=g.manifest(h,'reservation-after');q.record('reservation-gate',{'before':resBefore,'after':h.o.send('RESERVATIONS'),'hashChanged':after['hash']!=removed['hash']})
 q.record('declared-field-matrix',json.loads(h.o.send('FIELDS')))
 h.close();q.record('battery-complete',True)
except Exception as e:q.record('battery-error',repr(e));raise
finally:g.cleanup()
