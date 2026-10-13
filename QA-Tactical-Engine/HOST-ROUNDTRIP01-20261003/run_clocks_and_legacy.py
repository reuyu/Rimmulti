import run_roundtrip as q
import json,shutil
q.RESULTS=json.loads((q.DATA/'results.json').read_text(encoding='utf-8'))
def main():
 assert not q.MOD.exists();shutil.copy2(q.Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll',q.MOD)
 try:
  h=q.Host('Clock_FullSource',q.Q/'Frozen/ComplexSettlementFixture.rws',30);assert h.ready
  before=h.snap('clock-before');oldprobe=q.Bridge(32330);q.record('clock-probe-before',{'probe':oldprobe.send('SNAP'),'worker':h.b.send('PROBE_LOCAL_CLOCKS')})
  h.ticks(300);after=h.snap('clock-target0-after300');q.record('clock-probe-target0',{'probe':oldprobe.send('SNAP'),'worker':h.b.send('PROBE_LOCAL_CLOCKS')})
  select=h.b.send('SET_TARGET_MAP 1');h.ticks(300);after1=h.snap('clock-target1-after300');q.record('clock-probe-target1',{'select':select,'probe':oldprobe.send('SNAP'),'worker':h.b.send('PROBE_LOCAL_CLOCKS')});oldprobe.close();h.close()
  for i,(name,src) in enumerate([('A_MissingHeldItem','Corrupt_1_MissingHeldItem'),('A_CorruptedAssignment','Corrupt_5_CorruptedAssignment')],31):
   source=q.R/'scratch/CorruptedFixtures'/(src+'.rws');h=q.Host('Legacy_'+name,source,i)
   q.record('legacy-'+name,{'inputSha':q.sha(source),'fullWaitReady':h.ready,'status':h.states[-1],'export':str(h.export('Legacy_'+name)) if h.ready else h.b.send('EXPORT_SAVE ShouldReject')});h.close()
 finally:
  for h in q.OWNED:
   if h.p.poll() is None:
    try:h.close()
    except Exception:h.p.kill();h.p.wait()
  if q.MOD.exists() and q.sha(q.MOD)==q.sha(q.Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll'):q.MOD.unlink()
if __name__=='__main__':main()
