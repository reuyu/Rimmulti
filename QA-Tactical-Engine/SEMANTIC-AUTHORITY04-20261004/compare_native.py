import common as g
import json,threading,shutil
q=g.q;q.RESULTS={}
def rec(k,v):q.RESULTS[k]=v;q.write(q.DATA/'canonical-comparators.json',q.RESULTS);print(k,json.dumps(v,ensure_ascii=True)[:250],flush=True)
q.record=rec;q.check();threading.Thread(target=q.watch,daemon=True).start();shutil.copy2(q.Q/'Observer/bin/Release/net472/QA.SemanticAuthority.Observer.dll',q.MOD)
try:
 h=q.Host('NativeV4Comparator',20);b,gr,vr=g.admit(h,'ComparatorClean');base=g.manifest(h,'ComparatorV4Baseline');expected=json.loads(base['json']);assert base['hash']==g.EXPECTED
 old=json.loads((q.DATA/'battery-results.json').read_text(encoding='utf-8'))
 rows=[]
 for i in range(1,16):
  label=f'input-{i:02}';d=old[label];pair={'expected':expected,'actual':d['finalLiveManifest']};path=q.DATA/(label+'.comparepair-v4.json');q.write(path,pair);result=json.loads(h.o.send('COMPAREPAIR '+str(path)));rows.append({'case':label,'actualNativeDigest':d['finalLiveManifestHash'],'expectedNativeDigest':base['hash'],'compare':result,'originalLiveStateEvidence':'battery-results.json:'+label,'inputBytesSHA':d['sourceSHA']})
 rec('v4-comparison-results',rows);h.close();rec('comparators-complete',True)
except Exception as e:rec('comparator-error',repr(e));raise
finally:
 g.cleanup();assert q.f.sha(q.MOD)==q.f.sha(q.Q/'Observer/bin/Release/net472/QA.SemanticAuthority.Observer.dll');q.MOD.unlink()
