import helpers as h
import pathlib,time,json,threading,re,shutil,xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
FIX=h.SCRATCH/'OriginalSave/POC_TAC_ENGINE_02_MultiMap_Complex.rws'
h.ROOT=ROOT
res={}
def log(key,value):
 res[key]=value;(ROOT/'results.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8');print(key,json.dumps(value,ensure_ascii=False),flush=True)
def profile(name,source=FIX):
 p=h.prepare(name,source)
 cfg=ET.parse(p/'Config/ModsConfig.xml');ET.SubElement(cfg.getroot().find('activeMods'),'li').text='qacodex.engine02.probe';cfg.write(p/'Config/ModsConfig.xml',encoding='utf-8',xml_declaration=True)
 return p
def launch(p,port,qaport):
 # helpers launches with the independent probe default port; only one probe worker at a time.
 return h.launch(p,port)
def cmd(b,c,p,label):
 start=time.monotonic();s=b.send(c);(p/(label+'.txt')).write_text(s,encoding='utf-8');v={'command':c,'response':s,'ms':round((time.monotonic()-start)*1000,3)};log(p.name+'_'+label,v);return s
def ready(b,p,name='Input',extra='0'):
 cmd(b,'LOAD_SAVE '+name+' '+extra,p,'load-request')
 states=[];start=time.monotonic()
 while time.monotonic()-start<100:
  s=b.send('STATUS');states.append(s)
  if s.startswith('STATE: READY'):break
  if s.startswith('STATE: LOAD_FAILED'):break
  time.sleep(.3)
 (p/'load-states.txt').write_text('\n'.join(states),encoding='utf-8');log(p.name+'_load',{'state':s,'ms':(time.monotonic()-start)*1000});return s
def steps(b,p,n,slice=10):
 cmd(b,f'STEP_TICKS {n} {slice}',p,'step-request-'+str(n));start=time.monotonic()
 while time.monotonic()-start<100:
  s=b.send('STATUS')
  if 'RemainingStep=0' in s:break
  time.sleep(.03)
 log(p.name+'_step-finish-'+str(n),{'state':s,'ms':(time.monotonic()-start)*1000})
def stop(proc,b,p):h.shutdown(proc,b,p)
def main():
 p=profile('Scoped');proc,b=launch(p,29340,30340);q=h.Bridge(30340,60)
 cmd(b,'LOAD_SAVE Input 0',p,'life-load')
 for label,c in [('LIFE01','RUN_TICKS 100'),('LIFE02','EXPORT_SAVE Premature'),('LIFE03','LOAD_SAVE Input 0')]:cmd(b,c,p,label)
 start=time.monotonic()
 while time.monotonic()-start<100:
  s=b.send('STATUS')
  if s.startswith('STATE: READY'):break
  time.sleep(.3)
 log('initial-ready',s)
 cmd(q,'SNAP',p,'clock-before');cmd(b,'GET_ALL_MAPS_SUMMARY',p,'maps-before');cmd(b,'GET_MAP_DETAILED_SUMMARY 0',p,'graph-before')
 cmd(b,'EXPORT_SAVE Baseline',p,'baseline-export')
 cmd(b,'START_SIMULATION 60',p,'realtime-start');samples=[];t0=time.monotonic()
 while time.monotonic()-t0<6:
  t=time.monotonic();s=b.send('STATUS');samples.append({'t':t,'ms':(time.monotonic()-t)*1000,'state':s});time.sleep(.05)
 cmd(b,'PAUSE_SIMULATION',p,'realtime-pause');log('realtime-samples',samples)
 steps(b,p,1000)
 cmd(b,'GET_ALL_MAPS_SUMMARY',p,'maps-after1000');cmd(b,'EXPORT_SAVE Scoped1000',p,'after1000-export')
 lb=h.Bridge(29340,90);sb=h.Bridge(29340,90);lr={}
 def long():lr.update({'response':cmd(lb,'RUN_TICKS 50000',p,'run50000')})
 th=threading.Thread(target=long);th.start();time.sleep(.15);sr=cmd(sb,'STATUS',p,'parallel-status');th.join();lb.close();sb.close()
 cmd(q,'SNAP',p,'clock-after-long');cmd(b,'EXPORT_SAVE LongScoped',p,'long-export');cmd(b,'GET_MAP_DETAILED_SUMMARY 0',p,'graph-long')
 # LIFE05: only scratch probe blocks Unity's main thread; real bridge remains untouched.
 qr=h.Bridge(30340,60);block_result={}
 def block():block_result['response']=qr.send('BLOCK 33000')
 th=threading.Thread(target=block);th.start()
 while not (p/'qa-block-entered.txt').exists():time.sleep(.05)
 t=time.monotonic();cmd(b,'STEP_TICKS 77 10',p,'LIFE05-timeout');th.join();log('LIFE05-block',{'seconds':time.monotonic()-t,**block_result});qr.close();time.sleep(.2)
 cmd(b,'STATUS',p,'LIFE05-after');cmd(q,'SNAP',p,'LIFE05-clock');q.close()
 # Reconnect then shutdown boundary.
 br=h.Bridge(29340);cmd(br,'HELLO',p,'LIFE04-reconnect');br.close()
 stop(proc,b,p)
 p2=profile('Fresh',p/'Saves/LongScoped.rws');proc2,b2=launch(p2,29341,30340);q2=h.Bridge(30340,60)
 ready(b2,p2);cmd(q2,'SNAP',p2,'clock-reloaded');cmd(b2,'GET_MAP_DETAILED_SUMMARY 0',p2,'graph-reloaded');cmd(b2,'EXPORT_SAVE ReloadBaseline',p2,'reloaded-export')
 cmd(q2,'RESUME_UNSCOPED 1',p2,'resume-one');cmd(q2,'SNAP',p2,'clock-resumed-one');cmd(b2,'EXPORT_SAVE ResumeOne',p2,'resume-one-export')
 cmd(q2,'RESUME_UNSCOPED 1000',p2,'resume1000');cmd(q2,'SNAP',p2,'clock-resumed1000');cmd(b2,'EXPORT_SAVE Resume1000',p2,'resume1000-export')
 q2.close();stop(proc2,b2,p2)
 # Missing actual custom ThingDef and missing actual mod in SAVE metadata, neither passed as command requirements.
 r=ET.parse(FIX);g=r.getroot();g.find('meta/modIds').append(ET.Element('li'));g.find('meta/modIds')[-1].text='qa.actually.missing.dependency'
 for e in g.iter('def'):
  if e.text=='WarEconomy_TacticalProofToken':e.text='QA_UndeclaredMissingToken'
 bad=ROOT/'OmittedDependency.rws';r.write(bad,encoding='utf-8',xml_declaration=True)
 p3=profile('Omitted',bad);proc3,b3=launch(p3,29342,30340)
 cmd(b3,'VALIDATE_MANIFEST Input',p3,'omitted-validate');cmd(b3,'VALIDATE_MANIFEST Input QA_UndeclaredMissingToken',p3,'declared-negative');ready(b3,p3)
 cmd(b3,'EXPORT_SAVE AfterLoss',p3,'after-loss-export');cmd(b3,'STATUS',p3,'after-loss-status');stop(proc3,b3,p3)
 log('done',True)
if __name__=='__main__':
 try:main()
 except Exception as ex:log('fatal',repr(ex));raise
 finally:
  for proc in h.owned:
   if proc.poll() is None:proc.kill();proc.wait(timeout=10)
  log('owned-cleanup',{'pids':[p.pid for p in h.owned],'all_terminated':all(p.poll() is not None for p in h.owned)})
