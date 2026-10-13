import common as g
import json,threading,copy,shutil,time
q=g.q;q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.write(q.DATA/'fences-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:400],flush=True)
q.record=rec;q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 h=q.Host('FenceSimulator',5);v=q.Host('FenceValidator',6)
 # Each single-field receipt check uses an otherwise correctly bound structure. Issuer authenticity is separately known broken.
 fields=[('stagedSha','0'*64),('stagedFilePath','C:/QA/Other.rws'),('workerGeneration',999),('authorityId','OTHER'),('grantId','OTHER'),('contentProfileFingerprint','0'*64),('sealedResultId','OTHER'),('resultEpoch',999),('scopeId','OTHER'),('targetMapIndex',999),('manifestVersion','WRONG'),('sealedManifestHash','0'*64),('sourceArtifactHash','0'*64),('validatorProcessId','')]
 for field,value in fields:
  b,gr,s,sr,n,p=g.prepare(h,'Receipt_'+field);r=g.craft(h,s,p,**{field:value});accepted=g.submit(h,r,'Receipt_'+field);pr,out=g.promote(h,n,'ReceiptFinal_'+field);rec('receipt-'+field,{'field':field,'injected':value,'acceptance':accepted,'promotion':pr,'finalExists':out.exists(),'state':g.state(h)})
 # Fresh real validator receiving substituted sealed-result metadata, with unchanged legitimate manifest.
 for field,value in [('sealedResultId','FORGED-ID'),('authorityId','FORGED-AUTH'),('grantId','FORGED-GRANT'),('resultEpoch',999)]:
  b,gr,s,sr,n,p=g.prepare(h,'Validator_'+field);forged=s|{field:value};receipt,vr=g.validate(v,h,forged,p,'Validator_'+field);a=g.submit(h,receipt,'Validator_'+field) if receipt else 'NONE';pr,out=g.promote(h,n,'ValidatorFinal_'+field);rec('forged-metadata-'+field,{'validator':vr,'receipt':receipt,'acceptance':a,'promotion':pr,'finalExists':out.exists()})
 old=json.loads((q.DATA/'legit-original-receipt.json').read_text());b,gr,s,sr,n,p=g.prepare(h,'CrossProcess');a=g.submit(h,old,'CrossProcess');rec('cross-process-original',{'receiptIssuer':old['validatorProcessId'],'simulatorPID':h.p.pid,'response':a,'state':g.state(h)})
 # No receipt and direct RESULT_SEALED bypasses.
 b,gr,vr=g.admit(h,'Direct');s=g.seal(h,gr,'Direct');a=h.cmd('PROMOTE_STAGED Direct DirectFinal');r,n,p=g.stage(h,'NoReceipt');a2,fp=g.promote(h,n,'NoReceiptFinal');rec('no-receipt',{'directResultSealed':a,'stagedWithoutReceipt':a2,'finalExists':fp.exists()})
 # Boundary changes after accepted receipt; QA metadata mutation is explicitly observer-only.
 for attack in ['epoch','generation','skill','stageBytes','path','reseal','reset','profile','scopeGrant','badReceiptJson']:
  b,gr,s,sr,n,p=g.prepare(h,'Fence_'+attack);receipt=g.craft(h,s,p);a=g.submit(h,receipt,'Fence_'+attack);before=g.state(h);mutation=None;originalProfile=None
  if attack in ['epoch','generation','skill']:mutation=h.o.send('MUTATE '+attack)
  elif attack=='stageBytes':p.write_bytes(p.read_bytes()+b' ');mutation={'beforeSHA':receipt['stagedSha'],'afterSHA':q.f.sha(p)}
  elif attack=='path':shutil.copy2(p,h.profile/'Saves/Arbitrary.rws');n='Arbitrary'
  elif attack=='reseal':mutation=h.cmd('SEAL_RESULT '+gr['grantId'])
  elif attack=='reset':mutation=h.cmd('RESET_WORKER')
  elif attack=='profile':
   profile=h.profile/'Config/ModsConfig.xml';originalProfile=profile.read_bytes();profile.write_bytes(originalProfile+b'\n<!-- QA profile drift -->');mutation=h.cmd('GET_PROFILE_FINGERPRINT')
  elif attack=='scopeGrant':mutation=h.cmd('REGISTER_GRANT '+json.dumps(gr|{'scopeId':'OTHER'}))
  elif attack=='badReceiptJson':mutation=h.cmd('SUBMIT_STAGE_VALIDATION_RECEIPT {bad-json')
  pr,out=g.promote(h,n,'FenceFinal_'+attack);rec('fence-'+attack,{'acceptance':a,'before':before,'mutation':mutation,'promotion':pr,'finalExists':out.exists(),'after':g.state(h)})
  if originalProfile is not None:profile.write_bytes(originalProfile)
 # Actual original receipt after clean reseal/new epoch and RESET.
 b,gr,s,sr,n,p=g.prepare(h,'OldStage');r=g.craft(h,s,p);g.submit(h,r,'OldStage');s2=g.seal(h,gr,'OldStageNewSeal');a=g.submit(h,r,'OldStageReplay');pr,out=g.promote(h,n,'OldStageFinal');rec('old-stage-reseal',{'oldEpoch':s['resultEpoch'],'newEpoch':s2['resultEpoch'],'response':a,'promotion':pr,'finalExists':out.exists()})
 b,gr,s,sr,n,p=g.prepare(h,'ResetReceipt');r=g.craft(h,s,p);h.cmd('RESET_WORKER');a=g.submit(h,r,'ResetReceipt');pr,out=g.promote(h,n,'ResetReceiptFinal');rec('old-receipt-reset',{'acceptance':a,'promotion':pr,'finalExists':out.exists()})
 # Grant replay after reset; different authority lineage ignored or rejected is recorded explicitly.
 b,gr,vr=g.admit(h,'GrantReset');h.cmd('RESET_WORKER');a=h.cmd('REGISTER_GRANT '+json.dumps(gr));rec('grant-after-reset',{'response':a,'step':h.cmd('STEP_TICKS 1 1'),'seal':h.cmd('SEAL_RESULT '+gr['grantId']),'state':g.state(h)})
 h.close();v.close();rec('fences-complete',True)
except Exception as e:rec('fences-error',repr(e));raise
finally:g.cleanup()
