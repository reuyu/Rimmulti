import common as g
import json,threading
q=g.q;q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.write(q.DATA/'content-drift-results.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:450],flush=True)
q.record=rec;q.check();threading.Thread(target=q.watch,daemon=True).start()
original=q.MOD.read_bytes();baseline=json.loads((q.DATA/'FreshChainA-metadata.json').read_text());baselineObserver=[a for m in baseline['mods'] for a in m['assemblies'] if a['name']=='QA.SemanticAuthority.Observer'][0]
try:
 # PE overlay changes only the QA-owned, explicitly unfrozen observer assembly in the admitted QAProbe package.
 q.MOD.write_bytes(original+b'QA-owned PE overlay content-drift check 20261004\n');h=q.Host('ContentAssemblyDrift',19);b,gr,vr=g.admit(h,'ContentDrift');new=json.loads(h.o.send('META'));newObserver=[a for m in new['mods'] for a in m['assemblies'] if a['name']=='QA.SemanticAuthority.Observer'][0];finger=h.cmd('GET_PROFILE_FINGERPRINT');rec('same-config-assembly-byte-drift',{'baselineObserver':baselineObserver,'changedObserver':newObserver,'sameAssemblyMVID':baselineObserver['mvid']==newObserver['mvid'],'differentAssemblySHA':baselineObserver['sha']!=newObserver['sha'],'configSHA':q.f.sha(h.profile/'Config/ModsConfig.xml'),'reportedProfile':finger,'inputAdmission':vr,'simulation':h.ticks(1),'scope':'QA-only assembly byte input in active QAProbe; no frozen WorkerBridge or production file modified'});h.close();rec('content-complete',True)
except Exception as e:rec('content-error',repr(e));raise
finally:
 g.cleanup();q.MOD.write_bytes(original)
