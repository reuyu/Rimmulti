import run_engine02 as t
from run_engine02 import *
t.res=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
def main():
 pa=h.prepare('DualA',ROOT/'Scoped/Saves/Baseline.rws');pb=h.prepare('DualB',ROOT/'Scoped/Saves/Baseline.rws');la={}
 def one(p,port,key):la[key]=h.launch(p,port)
 a=threading.Thread(target=one,args=(pa,29346,'a'));b=threading.Thread(target=one,args=(pb,29347,'b'));a.start();b.start();a.join();b.join();proca,ca=la['a'];procb,cb=la['b']
 aa=threading.Thread(target=ready,args=(ca,pa,'Input','0'));bb=threading.Thread(target=ready,args=(cb,pb,'Input','1'));aa.start();bb.start();aa.join();bb.join()
 cmd(ca,'GET_ALL_MAPS_SUMMARY',pa,'before');cmd(cb,'GET_ALL_MAPS_SUMMARY',pb,'before')
 aa=threading.Thread(target=steps,args=(ca,pa,100));bb=threading.Thread(target=steps,args=(cb,pb,100));aa.start();bb.start();aa.join();bb.join()
 cmd(ca,'GET_ALL_MAPS_SUMMARY',pa,'after');cmd(cb,'GET_ALL_MAPS_SUMMARY',pb,'after');cmd(ca,'EXPORT_SAVE IndependentA',pa,'export');cmd(cb,'EXPORT_SAVE IndependentB',pb,'export')
 ca.close();ca=h.Bridge(29346);cmd(ca,'HELLO',pa,'LIFE04-reconnect');cmd(ca,'STATUS',pa,'LIFE04-state')
 stop(proca,ca,pa);stop(procb,cb,pb)
 log('dual-done',{'pids':[proca.pid,procb.pid],'ports':[29346,29347],'scope':[0,1]})
try:main()
except Exception as ex:log('dual-fatal',repr(ex));raise
finally:
 for proc in h.owned:
  if proc.poll() is None:proc.kill();proc.wait(timeout=10)
 log('dual-owned-cleanup',{'pids':[p.pid for p in h.owned],'all_terminated':all(p.poll() is not None for p in h.owned)})
