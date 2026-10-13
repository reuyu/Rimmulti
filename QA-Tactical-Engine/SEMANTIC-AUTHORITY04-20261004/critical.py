import common as g
import json,threading,copy
q=g.q;q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 s=q.Host('CriticalSimulator',2);v=q.Host('CriticalValidator',3)
 b,gr,seal,sr,n,p=g.prepare(s,'CleanReceipt');q.record('clean-full-manifest',g.manifest(s,'clean-baseline'))
 receipt,response=g.validate(v,s,seal,p,'LegitReceipt');assert receipt is not None,response
 q.record('legit-submission',g.submit(s,receipt,'LegitReceipt'));q.record('legit-promotion',g.promote(s,n,'LegitFinal')[0]);q.write(q.DATA/'legit-original-receipt.json',receipt)
 # Literal hand-crafted issuer with no real validator, signature or IPC proof.
 b,gr,seal,sr,n,p=g.prepare(s,'Handcrafted');fake=g.craft(s,seal,p);r=g.submit(s,fake,'Handcrafted');pr,out=g.promote(s,n,'HandcraftedFinal');q.record('handcrafted-bypass',{'receipt':fake,'acceptance':r,'promotion':pr,'finalExists':out.exists()})
 # Supported saved-byte field omitted by subset XML checks: static stage passes B while immutable result stays A.
 for fault in ['silent-bill','silent-follow','silent-plantAge']:
  b,gr,a,sr,n,p=g.prepare(s,'SavedB_'+fault,fault=fault)
  if not n:q.record('savedB-'+fault,{'stage':sr,'unexpectedStageBlocked':True});continue
  # Legit A expected validation should fail against B.
  receipt,reject=g.validate(v,s,a,p,'RejectA_'+fault);q.record('savedB-legit-A-'+fault,{'validator':reject,'receipt':receipt})
  # A caller constructs expected B from the validator engine's current B (deliberately untrusted self-baseline).
  mb=g.manifest(v,'B_'+fault);forged=copy.deepcopy(a);forged['sealedManifestHash']=mb['hash'];forged['manifestJson']=mb['json']
  receipt,response=g.validate(v,s,forged,p,'ForgedB_'+fault)
  accept=g.submit(s,receipt,'ForgedB_'+fault) if receipt else 'NO RECEIPT';pr,out=g.promote(s,n,'ForgedFinal_'+fault) if receipt else ('NO RECEIPT',s.profile/'Saves/absent.rws')
  q.record('forged-expected-'+fault,{'sealedA':a,'forgedB':forged,'loadedB':mb,'stage':sr,'receipt':receipt,'validator':response,'simulatorAccept':accept,'promotion':pr,'finalExists':out.exists(),'finalSHA':q.f.sha(out) if out.exists() else None})
 s.close();v.close();q.record('critical-complete',True)
except Exception as e:q.record('critical-harness-error',repr(e));raise
finally:g.cleanup()
