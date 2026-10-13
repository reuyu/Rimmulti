import protocol as q
import json,time,re,threading,shutil,copy,os
from pathlib import Path
CLEAN=q.Q/'Frozen/TargetSettlement_Clean_ContextB.rws';EXPECTED='98F7817C57C57D05C43BABEC5B3A110163EED48A1B8878F4A135EBECDFF1423A'
def state(h):return json.loads(h.o.send('INTERNAL'))
def bundle(h,source=CLEAN,expected=EXPECTED,id='QA-CLEAN',generation=None,**changes):
 b={'authorityId':id,'expectedSourceArtifactHash':q.f.sha(source),'manifestVersion':'3.0','expectedManifestHash':expected,'contentProfileFingerprint':'PROFILE-SETTLEMENT-B','targetMapId':0,'workerGeneration':state(h)['currentGeneration']+1 if generation is None else generation,'allowedOperationMode':'SIMULATION'};b.update(changes);return b
def register(h,b,label):
 p=q.DATA/(label+'.authority.json');q.write(p,b);r=h.cmd('REGISTER_AUTHORITY '+json.dumps(b,separators=(',',':')),label+'-register');return r
def admit(h,label,source=CLEAN,expected=EXPECTED,**changes):
 b=bundle(h,source,expected,id=label,**changes);register(h,b,label);assert h.load(source,label),h.b.send('STATUS');r=h.cmd('VALIDATE_INPUT',label+'-input');q.record(label+'-authority-binding',{'bundle':b,'live':state(h),'sourceSha':q.f.sha(source),'profileSha':q.f.sha(h.profile/'Config/ModsConfig.xml')});return r
def seal(h,label):
 r=h.cmd('SEAL_RESULT '+label,label+'-seal');sealed=json.loads(h.b.send('GET_SEALED_RESULT')) if r.startswith('RESULT_SEALED') else None;q.record(label+'-sealed-result',sealed);return sealed
def stage(h,label):
 r=h.cmd('STAGE_SAVE '+label,label+'-stage');m=re.search("StagingName='([^']+)'",r);path=h.profile/'Saves'/((m.group(1) if m else 'NONE')+'.rws');return r,m.group(1) if m else None,path
def promote(h,name,label):
 r=h.cmd('PROMOTE_STAGED '+str(name)+' '+label,label+'-promote');p=h.profile/'Saves'/(label+'.rws');q.record(label+'-output',{'exists':p.exists(),'path':str(p),'sha':q.f.sha(p) if p.exists() else None,'facts':q.facts(p) if p.exists() else None});return r,p
def install():
 q.check();assert not q.MOD.exists();shutil.copy2(q.Q/'Observer/bin/Release/net472/QA.SemanticAuthority.Observer.dll',q.MOD);threading.Thread(target=q.watch,daemon=True).start()
def cleanup():
 q.STOP.set()
 for h in q.OWNED:
  if h.p.poll() is None:
   try:h.close()
   except Exception:h.p.kill();h.p.wait(timeout=10)
 if q.MOD.exists() and q.f.sha(q.MOD)==q.f.sha(q.Q/'Observer/bin/Release/net472/QA.SemanticAuthority.Observer.dll'):q.MOD.unlink()
 q.write(q.Q/'candidate-after.json',q.f.candidates());q.write(q.Q/'production-after.json',q.f.prod());q.check()
def main():
 install()
 try:
  h=q.Host('IndependentAuthority',1);assert admit(h,'Baseline').startswith('INPUT_VALIDATED');q.record('baseline-hash',json.loads(h.o.send('FIELDS'))['baselineHash']);h.census('baseline');q.record('baseline-facts',q.facts(CLEAN))
  # Highest priority: candidate saves correct live state, QA alters bytes before candidate records staged SHA.
  for fault in ['silent-skill','silent-hediff','silent-holder','broken-tail','trailing','dtd']:
   assert admit(h,'SavedByte_'+fault).startswith('INPUT_VALIDATED');sealed=seal(h,'UNREGISTERED-'+fault);before=state(h);h.o.send('ARM '+fault);sr,name,path=stage(h,'SavedByte_'+fault);proof=h.profile/'save-fault-evidence.json';inj=json.loads(proof.read_text(encoding='utf-8')) if proof.exists() else None
   pr,out=promote(h,name,'Promoted_'+fault) if name else ('not attempted',h.profile/'Saves'/('Promoted_'+fault+'.rws'))
   q.record('saved-byte-'+fault,{'sealed':sealed,'before':before,'stage':sr,'promotion':pr,'outputExists':out.exists(),'injection':inj,'after':state(h),'stagingQuarantine':[str(p) for p in (h.profile/'Saves').glob('*') if ('SavedByte_'+fault) in p.name]})
  # Trusted input regressions: independently create 15 persistent corruptions.
  for i in range(1,16):
   k=f'{i:02}';root=q.E.parse(CLEAN).getroot();q.mutate(root,k);p=q.DATA/(k+'-wrong-input.rws');q.E.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True)
   q.record('negative-'+k+'-facts',{'expected':q.facts(CLEAN),'injected':q.facts(p),'sha':q.f.sha(p)})
   r=admit(h,'InputNegative'+k,source=p);legacy=h.cmd('APPROVE_SEMANTIC '+str(p),'negative-'+k+'-legacy');cp,c=h.census('negative-'+k+'-live');selfapprove=h.cmd('APPROVE_SEMANTIC '+str(cp),'negative-'+k+'-self');checks={x:h.cmd(x+' '+arg,'negative-'+k+'-'+x) for x,arg in [('STEP_TICKS','1 1'),('START_SIMULATION',''),('SEAL_RESULT','ARBITRARY'),('STAGE_SAVE','Rejected'+k),('EXPORT_SAVE','Rejected'+k),('PROMOTE_STAGED','InputNegative'+k+' BypassNegative'+k)]}
   q.record('negative-'+k+'-gate',{'validation':r,'legacy':legacy,'self':selfapprove,'state':state(h),'commands':checks,'finalExists':(h.profile/'Saves'/('BypassNegative'+k+'.rws')).exists(),'liveCensusPath':str(cp)})
  # Native same-tick state mutations rather than tick-equivalence assumptions.
  for mutation in ['skill','hediff','holder','zone','designation','relation','assignment','followFieldwork','plantAge','billSuspended','hediffPart','hediffId']:
   assert admit(h,'SameTick_'+mutation).startswith('INPUT_VALIDATED');seal(h,'NO-REGISTRY-'+mutation);before=state(h);m=json.loads(h.o.send('MUTATE '+mutation));sr,name,path=stage(h,'Blocked_'+mutation);q.record('same-tick-'+mutation,{'mutation':m,'before':before,'after':state(h),'stage':sr,'pathExists':path.exists()})
  # Full declared-field hash/equality and actual post-seal gate using one-shot census fault injection.
  assert admit(h,'FieldMatrix').startswith('INPUT_VALIDATED');matrix=json.loads(h.o.send('FIELDS'));q.write(q.DATA/'declared-field-matrix.json',matrix)
  gates=[]
  for row in matrix['rows']:
   h.b.send('VALIDATE_INPUT');h.b.send('SEAL_RESULT FIELD-TEST');h.o.send('ARM_FIELD '+row['path']);response=h.b.send('STAGE_SAVE BlockedField');gates.append({'field':row['field'],'path':row['path'],'hashChanged':row['hashChanged'],'comparatorPass':row['comparatorPass'],'stage':response,'proof':h.o.send('FIELD_PROOF')})
  q.write(q.DATA/'declared-field-gates.json',gates);q.record('declared-field-summary',{'rows':len(gates),'hashChanged':sum(x['hashChanged'] for x in gates),'stageBlocked':sum(x['stage'].startswith('STAGE_BLOCKED') for x in gates),'comparatorPassDespiteHashChange':sum(x['comparatorPass'] for x in gates)})
  h.close();q.record('main-complete',True);q.check()
 except Exception as e:q.record('unhandled',repr(e));raise
 finally:cleanup()
if __name__=='__main__':main()
