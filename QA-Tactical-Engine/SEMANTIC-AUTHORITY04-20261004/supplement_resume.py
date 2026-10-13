import common as g
import json,threading,copy,base64
q=g.q;q.RESULTS=json.loads((q.DATA/'supplement-results.json').read_text(encoding='utf-8'))
def rec(k,v):q.RESULTS[k]=v;q.write(q.DATA/'supplement-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:450],flush=True)
q.record=rec;q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 h=q.Host('SupplementResumeSimulator',17);v=q.Host('SupplementResumeValidator',18)
 for fault in []:
  b,gr,a,sr,n,p=g.prepare(h,'Fixed_'+fault,fault=fault);proof=json.loads((h.profile/'save-fault-evidence.json').read_text());assert n,sr
  rr,reject=g.validate(v,h,a,p,'LegitA_'+fault);mb=g.manifest(v,'FixedB_'+fault);forged=a|{'manifestJson':mb['json'],'sealedManifestHash':mb['hash']};receipt,r=g.validate(v,h,forged,p,'ExpectedB_'+fault);acc=g.submit(h,receipt,'ExpectedB_'+fault) if receipt else 'NONE';pr,out=g.promote(h,n,'WrongFinal_'+fault)
  rec('forged-'+fault,{'faultProof':proof,'sealedA':a['sealedManifestHash'],'loadedB':mb['hash'],'legitimateAValidator':reject,'forgedValidator':r,'receipt':receipt,'acceptance':acc,'promotion':pr,'finalExists':out.exists(),'finalSHA':q.f.sha(out) if out.exists() else None})
 # Re-run the formerly masked stage recensus checks from RESULT_SEALED, before staging.
 for mode in ['skill','hediff','holder','zone','designation','relation','assignment','followFieldwork','plantAge','billSuspended','hediffPart','hediffId']:
  b,gr,vr=g.admit(h,'SameTick_'+mode);s=g.seal(h,gr,'SameTick_'+mode);before=g.manifest(h,'Before_'+mode);m=h.o.send('MUTATE '+mode);after=g.manifest(h,'After_'+mode);stage,n,p=g.stage(h,'SameTick_'+mode);pr,out=g.promote(h,n,'SameTickFinal_'+mode);rec('same-tick-'+mode,{'mutation':m,'beforeHash':before['hash'],'afterHash':after['hash'],'stage':stage,'promotion':pr,'finalExists':out.exists()})
 # Partial command validation must not retain an already authorized result.
 for cmd in ['REGISTER_GRANT','REGISTER_AUTHORITY','SUBMIT_STAGE_VALIDATION_RECEIPT']:
  for bad in ['', '{bad-json']:
   b,gr,s,sr,n,p=g.prepare(h,'Malformed_'+cmd+('_empty' if not bad else '_json'));r=g.craft(h,s,p);g.submit(h,r,'BeforeMalformed');failed=h.cmd(cmd+' '+bad);after=g.state(h);pr,out=g.promote(h,n,'AfterMalformed_'+cmd+('_empty' if not bad else '_json'));rec('malformed-'+cmd+('-empty' if not bad else '-json'),{'validationError':failed,'stateAfterError':after,'promotion':pr,'finalExists':out.exists()})
 # Same ID lineage/incarnation changes, before admission (immutable identity claim).
 for field in ['storeIncarnation','baseLineage']:
  h.cmd('RESET_WORKER');b=g.bundle(h,id='IMMUTABLE-'+field);a=g.register(h,b,'Original_'+field);r=g.register(h,b|{field:'FOREIGN-LINEAGE'},'Changed_'+field);rec('authority-immutability-'+field,{'first':a,'modified':r,'state':g.state(h)})
 # Admitted scope and grant budget coverage are recorded without claiming full temporal policy.
 b,gr,vr=g.admit(h,'ReadOnlyDowngrade',allowedOperationMode='READ_ONLY');gr2=gr|{'allowedMode':'SIMULATION'};rg=h.cmd('REGISTER_GRANT '+json.dumps(gr2));rec('readonly-downgrade',{'grant':rg,'step':h.cmd('STEP_TICKS 1 1'),'seal':h.cmd('SEAL_RESULT '+gr['grantId'])})
 b,gr,vr=g.admit(h,'GrantBudget');h.cmd('REGISTER_GRANT '+json.dumps(gr|{'tickBudget':1}));r=h.ticks(5);rec('grant-budget',{'requested':5,'declaredGrantBudget':1,'status':r,'seal':h.cmd('SEAL_RESULT '+gr['grantId'])})
 # Profile bytes change only in QA-owned Config. Live Def drift also proves the runtime hash excludes Def content.
 b,gr,vr=g.admit(h,'DefContent');before=h.cmd('GET_PROFILE_FINGERPRINT');m=h.o.send('MUTATE defLabel');after=h.cmd('GET_PROFILE_FINGERPRINT');rec('def-drift',{'before':before,'mutation':m,'after':after,'equal':before==after})
 profile=h.profile/'Config/ModsConfig.xml';orig=profile.read_bytes();root=q.E.fromstring(orig);active=root.find('activeMods');active[:]=list(reversed(list(active)));q.E.ElementTree(root).write(profile,encoding='utf-8',xml_declaration=True);rec('reordered-profile',{'fingerprint':h.cmd('GET_PROFILE_FINGERPRINT'),'step':h.cmd('STEP_TICKS 1 1'),'seal':h.cmd('SEAL_RESULT '+gr['grantId'])});profile.write_bytes(orig)
 # Save-time errors are genuine Log.Error / exception at the real native save boundary.
 final=h.profile/'Saves/PriorApproved.rws';source=q.Q/'Profiles/CriticalSimulator/Saves/LegitFinal.rws';final.write_bytes(source.read_bytes());old=q.f.sha(final)
 for fault in ['error','throw']:
  b,gr,s,sr,n,p=g.prepare(h,'SaveError_'+fault,fault=fault);pr,out=g.promote(h,n,'PriorApproved');rec('native-save-'+fault,{'stage':sr,'promotion':pr,'priorSHA':old,'afterSHA':q.f.sha(final),'unchanged':q.f.sha(final)==old,'state':g.state(h),'quarantine':[str(x) for x in (h.profile/'Saves').glob('Quarantine_*')]})
 h.close();v.close();rec('supplement-complete',True)
except Exception as e:rec('supplement-error',repr(e));raise
finally:g.cleanup()
