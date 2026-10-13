import run_engine02 as t
from run_engine02 import *
t.res=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
def main():
 r=ET.parse(ROOT/'IndependentSymmetric.rws')
 for i,hd in enumerate(r.getroot().findall('.//hediffs/li')):
  if hd.findtext('def')=='BionicTongue':
   for x in hd.findall('loadID'):hd.remove(x)
   ET.SubElement(hd,'loadID').text=str(550000+i)
 for m in r.getroot().find('game/maps'):
  for thing in list(m.find('things')):
   if thing.get('Class')=='Plant' and thing.findtext('pos')=='(145, 0, 145)' and thing.findtext('def')!='Plant_Rice':m.find('things').remove(thing)
   if thing.find('billStack/bills') is not None:thing.find('billStack/bills').clear()
 source=ROOT/'CleanSymmetric.rws';r.write(source,encoding='utf-8',xml_declaration=True)
 p=profile('CleanBoundary',source);proc,b=launch(p,29345,30340);q=h.Bridge(30340,60);ready(b,p)
 cmd(q,'SNAP',p,'before');cmd(b,'EXPORT_SAVE Before',p,'before-export');steps(b,p,2000)
 cmd(q,'SNAP',p,'after2000');cmd(b,'EXPORT_SAVE After',p,'after-export')
 cmd(q,'ECOLOGY',p,'ecology-one');cmd(q,'SNAP',p,'after-ecology');cmd(b,'EXPORT_SAVE Ecology',p,'ecology-export')
 # A fresh client trying a post-shutdown control must receive EOF/error and no side effect.
 other=h.Bridge(29345,5);q.close();start=time.monotonic();bye=b.send('SHUTDOWN');log('CleanBoundary_shutdown',{'response':bye,'ms':(time.monotonic()-start)*1000})
 try:log('LIFE06-post-shutdown',other.send('RUN_TICKS 10'))
 except Exception as ex:log('LIFE06-post-shutdown',{'exception':repr(ex)})
 other.close();b.close();proc.wait(timeout=15)
try:main()
except Exception as ex:log('clean-fatal',repr(ex));raise
finally:
 for proc in h.owned:
  if proc.poll() is None:proc.kill();proc.wait(timeout=10)
 log('clean-owned-cleanup',{'pids':[p.pid for p in h.owned],'all_terminated':all(p.poll() is not None for p in h.owned)})
