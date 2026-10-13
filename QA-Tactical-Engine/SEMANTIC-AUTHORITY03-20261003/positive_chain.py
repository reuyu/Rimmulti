import run_gate as g
import json,time
q=g.q
q.RESULTS.update(json.loads((q.DATA/'results.json').read_text(encoding='utf-8')))
original=q.record
def small(x):
 if isinstance(x,dict):return {k:('[separate native sealed manifest evidence retained]' if k=='manifestJson' else small(v)) for k,v in x.items()}
 if isinstance(x,list):return [small(v) for v in x]
 return x
q.record=lambda k,v:original(k,small(v))
def main():
 g.install()
 try:
  source=g.CLEAN;expected=g.EXPECTED;chain=[]
  for i,letter in enumerate(['A','B','C'],3):
   h=q.Host('IndependentChain'+letter,i)
   admission=g.admit(h,'ChainInput'+letter,source=source,expected=expected)
   beforePath,before=h.census('chain-'+letter+'-input')
   observed=json.loads(h.o.send('FIELDS'))['baselineHash']
   q.record('chain-'+letter+'-input-proof',{'sourceSha':q.f.sha(source),'expectedHash':expected,'liveHash':observed,'admission':admission,'match':observed==expected,'pid':h.p.pid})
   assert admission.startswith('INPUT_VALIDATED')
   if letter=='A':h.snap('independent-runtime-and-clean-graph')
   if letter=='C':
    chain.append({'process':'C','pid':h.p.pid,'sourceSha':q.f.sha(source),'authorityId':'ChainInputC','profileSha':q.f.sha(h.profile/'Config/ModsConfig.xml'),'expectedHash':expected,'liveHash':observed,'inputValidation':admission,'prePromotionValidator':False,'purpose':'post-promotion transport regression only'})
    h.close();break
   h.ticks(100)
   currentPath,current=h.census('chain-'+letter+'-posttick')
   sealed=g.seal(h,'UNREGISTERED-CHAIN-'+letter)
   q.write(q.DATA/('chain-'+letter+'-native-result-manifest.json'),sealed)
   sr,name,path=g.stage(h,'Independent'+letter)
   stagedSha=q.f.sha(path) if path.exists() else None
   pr,final=g.promote(h,name,'IndependentPromoted'+letter)
   row={'process':letter,'pid':h.p.pid,'sourceSha':q.f.sha(source),'authorityId':sealed['authorityId'],'contentProfile':sealed['contentProfileFingerprint'],'profileSha':q.f.sha(h.profile/'Config/ModsConfig.xml'),'generation':sealed['workerGeneration'],'grant':sealed['grantId'],'resultEpoch':sealed['resultEpoch'],'ticks':sealed['ticksGame'],'sealedManifestHash':sealed['sealedManifestHash'],'stagingPath':str(path),'stagedSha':stagedSha,'validatorPid':None,'validatorResult':'NONE: candidate performs XML envelope only','stage':sr,'promotion':pr,'promotedSha':q.f.sha(final),'posttickManifestPath':str(currentPath),'validAuthorityPublication':False}
   chain.append(row);q.write(q.DATA/'independent-chain.json',chain)
   source=final;expected=sealed['sealedManifestHash']
   # Verify save-time failures independently preserve the just-approved output.
   if letter=='A':
    old=q.f.sha(final)
    for fault in ['error','throw']:
     h.cmd('VALIDATE_INPUT') # May reject post-tick against original input; restore expected current result explicitly.
     b=g.bundle(h,source=g.CLEAN,id='QA-POSTTICK-FAULT-'+fault,generation=g.state(h)['currentGeneration'],expected=expected)
     g.register(h,b,'fault-'+fault);assert h.cmd('VALIDATE_INPUT').startswith('INPUT_VALIDATED')
     g.seal(h,'UNREGISTERED-FAULT-'+fault);h.o.send('ARM '+fault)
     fsr,fn,fp=g.stage(h,'SaveError_'+fault)
     q.record('native-save-error-'+fault,{'stage':fsr,'priorFinalSha':old,'currentFinalSha':q.f.sha(final),'priorUnchanged':old==q.f.sha(final),'state':g.state(h),'quarantine':[str(p) for p in (h.profile/'Saves').glob('Quarantine_*')]})
    assert g.admit(h,'SelfSealNativeMutation').startswith('INPUT_VALIDATED')
    mutation=json.loads(h.o.send('MUTATE skill'));selfSeal=g.seal(h,'UNREGISTERED-AFTER-DIRECT-MUTATION');selfStage,selfName,selfPath=g.stage(h,'WrongSelfSealed');selfPromotion,selfFinal=g.promote(h,selfName,'WrongSelfSealedFinal')
    q.record('native-mutation-arbitrary-self-seal',{'mutation':mutation,'sealed':selfSeal,'stage':selfStage,'promotion':selfPromotion,'priorChainArtifactUnchanged':q.f.sha(final)==old,'wrongFinalSkill':q.facts(selfFinal)['skill'] if selfFinal.exists() else None})
   h.close()
  q.write(q.DATA/'independent-chain.json',chain);q.record('independent-chain-complete',chain)
 except Exception as e:q.record('chain-unhandled',repr(e));raise
 finally:g.cleanup()
if __name__=='__main__':main()
