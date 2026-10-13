import run_roundtrip as q
import json,xml.etree.ElementTree as E,shutil
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
def main():
 assert not q.MOD.exists();shutil.copy2(q.Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll',q.MOD)
 try:
  t=E.parse(q.DATA/'A_TargetArtifact.rws');g=t.getroot().find('game');rm=g.find('researchManager');keys=rm.findall('progress/keys/li');values=rm.findall('progress/values/li');idx=next(i for i,k in enumerate(keys) if k.text=='Stonecutting');old=values[idx].text;values[idx].text='123';seed=q.DATA/'Research123_Composed.rws';t.write(seed,encoding='utf-8',xml_declaration=True)
  h=q.Host('Research_Composed',seed,40);assert h.ready;s=h.snap('research-composed');p=h.export('Research_Export');h.close()
  h=q.Host('Research_FreshRoundTrip',p,41);assert h.ready;s2=h.snap('research-fresh');h.close()
  t=E.parse(p);g=t.getroot().find('game');g.remove(g.find('researchManager'));omitted=q.DATA/'Research_Omitted.rws';t.write(omitted,encoding='utf-8',xml_declaration=True)
  h=q.Host('Research_Omitted',omitted,42);assert h.ready;gone=h.snap('research-omitted');out=h.export('Research_Quarantined');h.close()
  q.record('research-closure',{'originalProgress':old,'composedProgress':s['research'].get('Stonecutting'),'freshProcessProgress':s2['research'].get('Stonecutting'),'omittedProgress':gone['research'].get('Stonecutting',0),'omittedEngineReady':True,'omittedExportAllowed':out.exists(),'composedSha':q.sha(seed),'exportSha':q.sha(p),'omittedSha':q.sha(omitted)})
 finally:
  for h in q.OWNED:
   if h.p.poll() is None:
    try:h.close()
    except Exception:h.p.kill();h.p.wait()
  if q.MOD.exists() and q.sha(q.MOD)==q.sha(q.Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll'):q.MOD.unlink()
if __name__=='__main__':main()
