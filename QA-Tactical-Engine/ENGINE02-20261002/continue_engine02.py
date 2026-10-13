import run_engine02 as t
from run_engine02 import *
t.res=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
def main2():
 p=profile('TimeoutRetry',ROOT/'Scoped/Saves/LongScoped.rws');proc,b=launch(p,29343,30340);b.s.settimeout(60);q=h.Bridge(30340,60);ready(b,p)
 cmd(q,'SNAP',p,'before-timeout');qr=h.Bridge(30340,60);blocked={}
 def block():blocked['response']=qr.send('BLOCK 33000')
 th=threading.Thread(target=block);th.start()
 while not (p/'qa-block-entered.txt').exists():time.sleep(.05)
 cmd(b,'STEP_TICKS 77 10',p,'LIFE05-timeout');th.join();log('LIFE05-block-retry',blocked);qr.close();time.sleep(.3)
 cmd(b,'STATUS',p,'LIFE05-after');cmd(q,'SNAP',p,'after-timeout');q.close();stop(proc,b,p)
 p2=profile('Fresh',ROOT/'Scoped/Saves/LongScoped.rws');proc2,b2=launch(p2,29341,30340);q2=h.Bridge(30340,60)
 ready(b2,p2);cmd(q2,'SNAP',p2,'clock-reloaded');cmd(b2,'GET_MAP_DETAILED_SUMMARY 0',p2,'graph-reloaded');cmd(b2,'EXPORT_SAVE ReloadBaseline',p2,'reloaded-export')
 cmd(q2,'RESUME_UNSCOPED 1',p2,'resume-one');cmd(q2,'SNAP',p2,'clock-resumed-one');cmd(b2,'EXPORT_SAVE ResumeOne',p2,'resume-one-export')
 cmd(q2,'RESUME_UNSCOPED 1000',p2,'resume1000');cmd(q2,'SNAP',p2,'clock-resumed1000');cmd(b2,'EXPORT_SAVE Resume1000',p2,'resume1000-export')
 q2.close();stop(proc2,b2,p2)
 r=ET.parse(FIX);g=r.getroot();ET.SubElement(g.find('meta/modIds'),'li').text='qa.actually.missing.dependency'
 for e in g.iter('def'):
  if e.text=='WarEconomy_TacticalProofToken':e.text='QA_UndeclaredMissingToken'
 bad=ROOT/'OmittedDependency.rws';r.write(bad,encoding='utf-8',xml_declaration=True)
 p3=profile('Omitted',bad);proc3,b3=launch(p3,29342,30340)
 cmd(b3,'VALIDATE_MANIFEST Input',p3,'omitted-validate');cmd(b3,'VALIDATE_MANIFEST Input QA_UndeclaredMissingToken',p3,'declared-negative');ready(b3,p3)
 cmd(b3,'EXPORT_SAVE AfterLoss',p3,'after-loss-export');cmd(b3,'STATUS',p3,'after-loss-status');stop(proc3,b3,p3)
 log('continuation-done',True)
try:main2()
except Exception as ex:log('continuation-fatal',repr(ex));raise
finally:
 for proc in h.owned:
  if proc.poll() is None:proc.kill();proc.wait(timeout=10)
 log('continuation-owned-cleanup',{'pids':[p.pid for p in h.owned],'all_terminated':all(p.poll() is not None for p in h.owned)})
