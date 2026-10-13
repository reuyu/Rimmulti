import run_gate as g
q=g.q
import json,copy,shutil,time,re,os
q.RESULTS.update(json.loads((q.DATA/'results.json').read_text(encoding='utf-8')))
original_record=q.record
def small(x):
 if isinstance(x,dict):return {k:("[full manifest omitted from repeated log; native sealed hash retained]" if k=='manifestJson' else small(v)) for k,v in x.items()}
 if isinstance(x,list):return [small(v) for v in x]
 return x
q.record=lambda k,v:original_record(k,small(v))
def main():
 g.install()
 try:
  # Fresh worker proves a direct promote attempt without any staging validation.
  h=q.Host('AuthorityAttacksRetry',6);assert g.admit(h,'FreshAuthority').startswith('INPUT_VALIDATED');g.seal(h,'NEVER-REGISTERED-GRANT')
  root=q.E.parse(g.CLEAN).getroot();q.mutate(root,'02');wrong=h.profile/'Saves/NotStaged.rws';q.E.ElementTree(root).write(wrong,encoding='utf-8',xml_declaration=True);g.promote(h,'NotStaged','DirectWithoutStaging');q.record('no-stage-internal',g.state(h))
  # Test grant namespace; not a test of production socket authentication.
  for label in ['ANY-NEW-GRANT','STALE-GRANT-FROM-PRIOR','OTHER-AUTHORITY-GRANT','ANY-NEW-GRANT','']:
   h.cmd('SEAL_RESULT '+label,'grant-'+(label or 'blank'));q.record('grant-'+(label or 'blank')+'-state',g.state(h))
  # Register pre-load wrong source, then show that post-load registration skips the same source binding.
  b=g.bundle(h,id='WrongSourceBefore',expectedSourceArtifactHash='0'*64);g.register(h,b,'wrong-source-before');q.record('wrong-source-before-load',h.load(g.CLEAN,'WrongSource'))
  assert g.admit(h,'RestoredInput').startswith('INPUT_VALIDATED')
  for field,value in [('expectedSourceArtifactHash','0'*64),('contentProfileFingerprint','NOT-THE-ACTIVE-PROFILE'),('allowedOperationMode','READ_ONLY'),('authorityId','FreshAuthority'),('expectedSourceSha','F'*64),('workerGeneration',999),('targetMapId',999),('manifestVersion','wrong'),('expectedManifestHash','F'*64)]:
   assert g.admit(h,'Bound_'+field).startswith('INPUT_VALIDATED');b=g.bundle(h,id='Overwrite-'+field,generation=g.state(h)['currentGeneration']);b[field]=value
   if field=='expectedSourceSha':b['expectedSourceArtifactHash']=''
   registered=g.register(h,b,'after-load-'+field);v=h.cmd('VALIDATE_INPUT','after-load-'+field+'-validate');ready=g.state(h);step=h.cmd('STEP_TICKS 1 1','after-load-'+field+'-step');time.sleep(.12);s=h.cmd('SEAL_RESULT ARBITRARY','after-load-'+field+'-seal');q.record('authority-attack-'+field,{'bundle':b,'register':registered,'validate':v,'stateAfterValidate':ready,'step':step,'seal':s,'profileSha':q.f.sha(h.profile/'Config/ModsConfig.xml')})
  # Filename/byte replacement: REGISTER takes inline JSON, not a manifest path.
  assert g.admit(h,'BundleBytes').startswith('INPUT_VALIDATED');b=g.bundle(h,id='REUSED-ID',generation=g.state(h)['currentGeneration']);path=q.DATA/'authority-replace.json';q.write(path,b);reg=h.cmd('REGISTER_AUTHORITY '+json.dumps(json.loads(path.read_text()),separators=(',',':')));saved=h.b.send('GET_AUTHORITY');b['contentProfileFingerprint']='REPLACED';b['expectedManifestHash']='F'*64;q.write(path,b);unchanged=h.b.send('GET_AUTHORITY')==saved;q.record('bundle-file-replaced-only',{'registered':reg,'cachedUnchanged':unchanged,'validation':h.cmd('VALIDATE_INPUT')});q.record('same-id-replace-registration',{'register':h.cmd('REGISTER_AUTHORITY '+json.dumps(json.loads(path.read_text()),separators=(',',':'))),'newBundle':json.loads(h.b.send('GET_AUTHORITY')),'state':g.state(h)})
  # Old bundle after generation/source reload; updated generation with the same AuthorityId is also tried.
  assert g.admit(h,'ReuseSource').startswith('INPUT_VALIDATED');old=json.loads(h.b.send('GET_AUTHORITY'));sourceVariant=q.DATA/'SameSemanticsDifferentBytes.rws';sourceVariant.write_bytes(g.CLEAN.read_bytes()+b'\n');g.register(h,old,'exact-bundle-replay-before-other-source');q.record('authority-replay-other-source-load',h.load(sourceVariant,'OtherBytes'))
  assert g.admit(h,'SourceReset').startswith('INPUT_VALIDATED');old=json.loads(h.b.send('GET_AUTHORITY'));g.register(h,old,'same-authority-prior-generation');h.load(g.CLEAN,'NextGeneration');q.record('old-authority-validation',h.cmd('VALIDATE_INPUT'));old['workerGeneration']=g.state(h)['currentGeneration'];g.register(h,old,'reuse-authority-id-new-generation');q.record('reused-authority-id-validation',h.cmd('VALIDATE_INPUT'))
  # Unknown required lineage placeholders are not silently claimed as enforced.
  b=g.bundle(h,id='ForeignLineage',generation=g.state(h)['currentGeneration'],contextId='WRONG-CONTEXT',scopeId='WRONG-SCOPE',profileIdentifier='WRONG-PROFILE-ID',storeIncarnationId='WRONG-STORE',baseArtifactRevision=-999);g.register(h,b,'unknown-lineage-fields');q.record('unknown-lineage-fields-result',{'returnedAuthority':json.loads(h.b.send('GET_AUTHORITY')),'validation':h.cmd('VALIDATE_INPUT')})
  # Post-stage fences and reseal: explicit currentResultEpoch change must not reuse old staging.
  for mode in ['skill','generation','epoch','bytes','reseal']:
   assert g.admit(h,'PromotionFence_'+mode).startswith('INPUT_VALIDATED');g.seal(h,'GRANT-'+mode);sr,name,path=g.stage(h,'StageFence_'+mode);before=g.state(h)
   if mode=='bytes':q.E.parse(path).getroot();path.write_bytes(path.read_bytes()+b'\n')
   elif mode=='reseal':h.cmd('SEAL_RESULT OTHER-GRANT-RESEAL')
   else:h.o.send('MUTATE '+mode)
   response,final=g.promote(h,name,'FenceResult_'+mode);q.record('promotion-fence-'+mode,{'before':before,'after':g.state(h),'response':response,'promoted':final.exists()})
  # File.Replace failure retains prior final and staging; backup is explicit on successful replacement.
  assert g.admit(h,'ReplaceTest').startswith('INPUT_VALIDATED');g.seal(h,'REPLACE-GRANT');_,name,path=g.stage(h,'ReplaceStage1');_,prior=g.promote(h,name,'PriorFinal');oldSha=q.f.sha(prior)
  g.seal(h,'REPLACE-GRANT-2');_,name,path=g.stage(h,'ReplaceStage2')
  lockScript=q.DATA/'lock-file.ps1';lockScript.write_text("param([string]$p,[string]$signal,[string]$release)\n$qaFile=[System.IO.File]::Open($p,[System.IO.FileMode]::Open,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)\ntry{[System.IO.File]::WriteAllText($signal,'locked');while(-not [System.IO.File]::Exists($release)){Start-Sleep -Milliseconds 20}}finally{$qaFile.Dispose()}\n",encoding='utf-8');signal=q.DATA/'replace-lock.signal';release=q.DATA/'replace-lock.release'
  lock=q.subprocess.Popen(['powershell','-NoProfile','-File',str(lockScript),str(prior),str(signal),str(release)],creationflags=q.subprocess.CREATE_NO_WINDOW)
  try:
   deadline=time.monotonic()+10
   while not signal.exists() and time.monotonic()<deadline:time.sleep(.05)
   assert signal.exists();r=h.cmd('PROMOTE_STAGED '+name+' PriorFinal','locked-final-promotion')
  finally:release.write_text('release',encoding='utf-8');lock.wait(timeout=10)
  q.record('replacement-failure-safety',{'response':r,'oldSha':oldSha,'afterSha':q.f.sha(prior),'unchanged':oldSha==q.f.sha(prior),'stagingRetained':path.exists(),'state':g.state(h)})
  # Fresh validation/seal after failure; successful replacement yields a previous-artifact backup.
  assert g.admit(h,'ReplaceRecovery').startswith('INPUT_VALIDATED');g.seal(h,'REPLACE-RECOVERY');_,name,path=g.stage(h,'ReplaceStage3');g.promote(h,name,'PriorFinal');backup=h.profile/'Saves/PriorFinal.bak.rws';q.record('replacement-backup',{'exists':backup.exists(),'priorMatch':backup.exists() and q.f.sha(backup)==oldSha,'backupSha':q.f.sha(backup) if backup.exists() else None})
  # Active job and reservation graph: collected job field is a Def, not identity/targets.
  assert g.admit(h,'Jobs').startswith('INPUT_VALIDATED');job=json.loads(h.o.send('JOB'));beforePath,before=h.census('job-before-target');r=json.loads(h.o.send('MUTATE jobTarget'));afterPath,after=h.census('job-after-target');q.record('job-target-scope',{'job':job,'mutation':r,'censusEqual':before==after,'reservations':json.loads(h.o.send('RESERVATIONS'))})
  matrix=json.loads(h.o.send('FIELDS'));q.write(q.DATA/'job-field-matrix.json',matrix);gates=[]
  # Authorize the explicit QA-seeded job fixture through control-plane expected state.
  b=g.bundle(h,id='QA-SEEDED-JOB',generation=g.state(h)['currentGeneration'],expected=matrix['baselineHash']);g.register(h,b,'seeded-job-authority');h.cmd('VALIDATE_INPUT')
  for row in matrix['rows']:
   if not row['field'].startswith('reservations'):continue
   h.b.send('VALIDATE_INPUT');h.b.send('SEAL_RESULT FIELD-JOB');h.o.send('ARM_FIELD '+row['path']);gates.append({'field':row['field'],'hashChanged':row['hashChanged'],'stage':h.b.send('STAGE_SAVE BlockedReservation')})
  q.record('reservation-field-gates',gates);h.close();q.record('supplement-complete',True)
 except Exception as e:q.record('supplement-unhandled',repr(e));raise
 finally:g.cleanup()
if __name__=='__main__':main()
