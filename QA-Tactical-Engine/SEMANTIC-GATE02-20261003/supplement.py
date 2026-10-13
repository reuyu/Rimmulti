import run_qa as q
import json,threading,shutil,time,xml.etree.ElementTree as E
q.RESULTS.update(json.loads((q.DATA/'results.json').read_text(encoding='utf-8')))
def main():
 assert q.RESULTS.get('all-complete');q.check();assert not q.MOD.exists();shutil.copy2(q.Q/'Observer/bin/Release/net472/QA.SemanticGate.Observer.dll',q.MOD);threading.Thread(target=q.watch,daemon=True).start()
 try:
  h=q.Host('Supplement',6);clean=q.Q/'Frozen/TargetSettlement_Clean_ContextB.rws';full=q.Q/'Frozen/CleanSettlementFixture.rws';trusted=q.DATA/'clean-live.full-census.json'
  q.record('fresh-no-game-export',h.cmd('EXPORT_SAVE NoGameBlocked'))
  bad=q.Q/'Profiles/IndependentGateR3/Saves/SavedBytes_silent-skill.rws';assert h.load(bad,'ReloadApprovedWrongBytes');cp,c=h.census('saved-wrong-fresh-reload');q.record('saved-wrong-fresh-reload',{'sourceSHA':q.f.sha(bad),'skill':q.pawn(c)['skills']['Shooting'] if hasattr(q,'pawn') else next(p for p in c['pawns'] if p['id']=='Human302')['skills']['Shooting'],'comparator':h.compare(trusted),'status':h.b.send('STATUS')})
  assert h.load(clean,'GenerationFault');h.cmd('APPROVE_SEMANTIC '+str(trusted));h.o.send('ARM generation');r,p=h.export('GenerationAtSaveBoundary');proof=json.loads((h.profile/'save-fault-evidence.json').read_text(encoding='utf-8'));q.record('generation-at-save-boundary',{'proof':proof,'export':r,'exists':p.exists(),'afterStatus':h.b.send('STATUS'),'afterSemantic':h.b.send('GET_SEMANTIC_STATUS')})
  assert h.load(clean,'WrongProfile');cp,c=h.census('wrong-profile-base');c.update(contentProfileFingerprint='NOT_THE_RUNNING_CONTENT_PROFILE',sourceFixtureSHA256=q.f.sha(full),contextFixtureSHA256='F'*64,workerGeneration=-1,sourceAuthority='UNTRUSTED_LOCAL_FILE');p=q.DATA/'wrong-profile-authority.json';q.write(p,c);q.record('wrong-profile-approval',h.cmd('APPROVE_SEMANTIC '+str(p)));h.export('WrongProfileApproved')
  # Real network reload admits no old approval while loading or after generation transition.
  h.cmd('APPROVE_SEMANTIC '+str(trusted));q.record('before-reload-generation',h.b.send('STATUS'));h.cmd('LOAD_SAVE WrongProfile 0');q.record('during-reload-export',h.cmd('EXPORT_SAVE DuringReloadBlocked'));deadline=time.monotonic()+100
  while time.monotonic()<deadline:
   st=h.b.send('STATUS')
   if 'STATE: READY' in st or 'STATE: LOAD_FAILED' in st:break
   time.sleep(.2)
  q.record('after-reload-status',st);q.record('after-reload-unapproved-export',h.cmd('EXPORT_SAVE AfterReloadBlocked'))
  assert h.load(full,'TwoMapContext');h.snap('two-map-before');h.cmd('EXPORT_CENSUS OtherMapManifest 1');m=h.profile/'Saves/OtherMapManifest.census.json';q.record('actual-other-map-manifest',{'manifest':str(m),'mapIndex':json.loads(m.read_text(encoding='utf-8-sig'))['mapIndex'],'approvalAgainstMap0':h.cmd('APPROVE_SEMANTIC '+str(m))})
  h.cmd('EXPORT_CENSUS TargetMap0 0');h.cmd('APPROVE_SEMANTIC '+str(h.profile/'Saves/TargetMap0.census.json'));h.cmd('SET_TARGET_MAP 1');q.record('map-switch-export-fence',h.cmd('EXPORT_SAVE MapSwitchBlocked'));h.cmd('SET_TARGET_MAP 0');h.ticks(20);h.snap('two-map-after20');h.close();q.record('supplement-complete',True);q.check()
 except Exception as e:q.record('supplement-unhandled',repr(e));raise
 finally:
  q.STOP.set()
  for h in q.OWNED:
   if h.p.poll() is None:
    try:h.close()
    except Exception:h.p.kill();h.p.wait(timeout=10)
  if q.MOD.exists() and q.f.sha(q.MOD)==q.f.sha(q.Q/'Observer/bin/Release/net472/QA.SemanticGate.Observer.dll'):q.MOD.unlink()
  q.write(q.Q/'candidate-after.json',q.f.candidates());q.write(q.Q/'production-after.json',q.f.prod());q.check()
if __name__=='__main__':main()
