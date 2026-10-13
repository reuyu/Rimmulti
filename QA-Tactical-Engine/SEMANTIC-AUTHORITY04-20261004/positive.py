import common as g
import json,threading,time,shutil,subprocess
q=g.q;q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.write(q.DATA/'positive-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:400],flush=True)
q.record=rec;q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 source=g.CLEAN;expected=g.EXPECTED;chain=[]
 for index,letter in [(7,'A'),(9,'B'),(11,'C')]:
  h=q.Host('FreshChain'+letter,index);b,gr,vr=g.admit(h,'Input'+letter,source=source,expected=expected);inputManifest=g.manifest(h,'Chain'+letter+'Input');snapshot=h.snap('Chain'+letter+'Input');assert vr.startswith('INPUT_VALIDATED'),vr
  row={'stage':letter,'pid':h.p.pid,'sourceSHA':q.f.sha(source),'expected':expected,'actualInputHash':inputManifest['hash'],'inputResponse':vr,'purpose':'transport fidelity only; receipt authenticity evaluated separately'}
  if letter=='C':row['endTicks']=snapshot['ticksGame'];chain.append(row);h.close();break
  h.ticks(20);s=g.seal(h,gr,'Chain'+letter);sr,n,p=g.stage(h,'Chain'+letter);assert n,sr
  v=q.Host('FreshChainValidator'+letter,index+1);receipt,r=g.validate(v,h,s,p,'Chain'+letter+'Fresh');assert receipt is not None,r
  a=g.submit(h,receipt,'Chain'+letter);pr,final=g.promote(h,n,'Promoted'+letter);assert pr.startswith('ARTIFACT_APPROVED'),pr
  row.update({'sealedId':s['sealedResultId'],'epoch':s['resultEpoch'],'sealedHash':s['sealedManifestHash'],'stagedSHA':receipt['stagedSha'],'validatorPID':v.p.pid,'validatorReceipt':receipt,'submission':a,'promotion':pr,'finalSHA':q.f.sha(final),'byteExact':receipt['stagedSha']==q.f.sha(final),'receiptAuthenticator':'NONE; distinct PID is observed, not authenticated','countAsAuthorityGatePass':False})
  chain.append(row);q.write(q.DATA/'fresh-chain.json',chain);source=final;expected=s['sealedManifestHash'];v.close()
  if letter=='A':
   # Explicit live Goto+reservation transport test at zero further ticks.
   job=h.o.send('JOB');before=h.snap('ActiveJobBeforeSave');resBefore=h.o.send('RESERVATIONS');sjob=g.seal(h,gr,'ActiveJob');sj,nj,pj=g.stage(h,'ActiveJob');vj=q.Host('ActiveJobValidator',14);rr,rj=g.validate(vj,h,sjob,pj,'ActiveJobFresh');after=vj.snap('ActiveJobAfterLoad');rec('active-job-transport',{'job':job,'reservationsBefore':resBefore,'reservationsAfter':vj.o.send('RESERVATIONS'),'sealedHash':sjob['sealedManifestHash'],'loadedHash':g.manifest(vj,'ActiveJobReload')['hash'],'validation':rj,'receipt':rr,'beforeJob':before['maps'][0]['entities']['Human302']['pawn']['job'],'afterJob':after['maps'][0]['entities']['Human302']['pawn']['job']});vj.close()
   # Restore canonical source and prepare a native freshly validated replacement.
   b,gr,vr=g.admit(h,'ReplaceInput');s=g.seal(h,gr,'ReplaceInput');sr,n,p=g.stage(h,'ReplaceInput');v=q.Host('ReplacementValidator',15);rr,r=g.validate(v,h,s,p,'ReplaceFresh');assert rr,r;g.submit(h,rr,'ReplaceFresh');oldFinal=h.profile/'Saves/ReplacementFinal.rws';oldFinal.write_bytes(final.read_bytes());oldSHA=q.f.sha(oldFinal)
   lockScript=q.DATA/'lock-file.ps1';shutil.copy2(q.Q.parent/'SEMANTIC-AUTHORITY03-20261003/Evidence/lock-file.ps1',lockScript);signal=q.DATA/'replacement.locked';release=q.DATA/'replacement.release';si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
   locker=subprocess.Popen(['powershell','-NoProfile','-File',str(lockScript),'-p',str(oldFinal),'-signal',str(signal),'-release',str(release)],startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
   try:
    t=time.monotonic()
    while not signal.exists() and time.monotonic()-t<15:time.sleep(.05)
    assert signal.exists(),'QA exclusive file lock not established'
    locked=h.cmd('PROMOTE_STAGED '+n+' ReplacementFinal');st=g.state(h)
   finally:release.write_text('release');locker.wait(timeout=15)
   rec('exclusive-lock',{'response':locked,'priorSHA':oldSHA,'afterSHA':q.f.sha(oldFinal),'oldPreserved':oldSHA==q.f.sha(oldFinal),'stagePreserved':p.exists(),'stageSHA':q.f.sha(p) if p.exists() else None,'state':st,'lockerExit':locker.returncode})
   v.close();b,gr,vr=g.admit(h,'ReplaceSuccess');s=g.seal(h,gr,'ReplaceSuccess');sr,n,p=g.stage(h,'ReplaceSuccess');v=q.Host('ReplacementSuccessValidator',16);rr,r=g.validate(v,h,s,p,'ReplaceSuccessFresh');assert rr,r;g.submit(h,rr,'ReplaceSuccessFresh');newSHA=q.f.sha(p);pr,out=g.promote(h,n,'ReplacementFinal');backup=h.profile/'Saves/ReplacementFinal.bak.rws';rec('successful-replacement',{'response':pr,'priorSHA':oldSHA,'stagedSHA':newSHA,'finalSHA':q.f.sha(out),'backupSHA':q.f.sha(backup) if backup.exists() else None,'backupCorrect':backup.exists() and q.f.sha(backup)==oldSHA,'byteExact':q.f.sha(out)==newSHA});v.close()
  h.close()
 q.write(q.DATA/'fresh-chain.json',chain);rec('positive-complete',chain)
except Exception as e:rec('positive-error',repr(e));raise
finally:g.cleanup()
