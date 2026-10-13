from pathlib import Path
import json,subprocess,socket,time,shutil,xml.etree.ElementTree as E,threading,sys,copy,hashlib
import setup as f
Q=f.Q;R=f.R;DATA=Q/'Evidence';MOD=f.PROBE/'1.6/Assemblies/QA.SemanticGate.Observer.dll'
RESULTS={};OWNED=[];STOP=threading.Event();INVALID=threading.Event()
if '--resume' in sys.argv:
 RESULTS.update(json.loads((DATA/'results.json').read_text(encoding='utf-8')))
 if 'unhandled' in RESULTS:RESULTS.setdefault('qa-harness-interruptions',[]).append(RESULTS.pop('unhandled'))
def write(p,x):f.write(p,x)
def record(k,v):RESULTS[k]=v;write(DATA/'results.json',RESULTS);print(k,json.dumps(v,ensure_ascii=False)[:500],flush=True)
def check():
 b=json.loads((Q/'candidate-before.json').read_text(encoding='utf-8'));a=f.candidates();changes=[p for p in set(b)|set(a) if b.get(p)!=a.get(p)]
 if changes:INVALID.set();record('INVALID-FREEZE',changes);raise RuntimeError('candidate changed')
def watch():
 while not STOP.wait(30):
  try:check()
  except Exception:break
class Bridge:
 def __init__(self,port):self.s=socket.create_connection(('127.0.0.1',port),timeout=2);self.s.settimeout(100);self.f=self.s.makefile('r',encoding='utf-8')
 def send(self,cmd):
  if INVALID.is_set():raise RuntimeError('invalid freeze')
  self.s.sendall((cmd+'\n').encode());lines=[]
  while True:
   l=self.f.readline()
   if not l:raise EOFError(cmd)
   l=l.strip('\r\n').lstrip('\ufeff')
   if l=='---END---':return '\n'.join(lines)
   lines.append(l)
 def close(self):self.f.close();self.s.close()
class Host:
 def __init__(self,name,index):
  self.name=name;self.profile=Q/'Profiles'/name;self.profile.mkdir(parents=True,exist_ok=False);(self.profile/'Saves').mkdir();(self.profile/'Config').mkdir()
  shutil.copy2(Q/'Frozen/Developer-A/Config/ModsConfig.xml',self.profile/'Config/ModsConfig.xml')
  (self.profile/'Config/Prefs.xml').write_text('<PrefsData><volumeGame>0</volumeGame><volumeMusic>0</volumeMusic><devMode>True</devMode><runInBackground>True</runInBackground></PrefsData>',encoding='utf-8')
  self.port=33200+index;self.obsport=33300+index;qp=33400+index
  for port in [self.port,self.obsport,qp]:
   with socket.socket() as s:s.bind(('127.0.0.1',port))
  args=[str(f.ENGINE/'RimWorldWin64.exe'),'-batchmode',f'-savedatafolder={self.profile}','-logFile',str(self.profile/'player.log'),f'-bridgeport={self.port}',f'-qaport={qp}',f'-sgqaport={self.obsport}']
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  self.p=subprocess.Popen(args,cwd=Q,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);OWNED.append(self);self.b=None;self.o=None;t=time.monotonic()
  while time.monotonic()-t<80:
   if self.p.poll() is not None:raise RuntimeError(name+' early exit')
   try:self.b=Bridge(self.port);self.hello=self.b.send('HELLO');self.o=Bridge(self.obsport);break
   except(OSError,EOFError):time.sleep(.3)
  if not self.o:raise TimeoutError(name+' launch')
  meta=json.loads(self.o.send('META'));write(DATA/(name+'-metadata.json'),meta)
  record(name+'-launch',{'pid':self.p.pid,'args':args,'hello':self.hello,'meta':meta})
 def cmd(self,s,label=None):
  ans=self.b.send(s);record(label or (self.name+'-'+s),ans);return ans
 def load(self,source,label='Input',mapidx=0):
  dest=self.profile/'Saves'/(label+'.rws');shutil.copy2(source,dest);r=self.cmd(f'LOAD_SAVE {label} {mapidx}');t=time.monotonic();states=[]
  while time.monotonic()-t<100:
   st=self.b.send('STATUS');states.append(st)
   if 'STATE: READY' in st or 'STATE: LOAD_FAILED' in st:break
   time.sleep(.2)
  self.ready='STATE: READY' in st;record(self.name+'-load-'+label,{'ready':self.ready,'sourceSHA':f.sha(source),'status':st,'states':states,'elapsed':time.monotonic()-t});return self.ready
 def snap(self,label):
  x=json.loads(self.o.send('SNAP'));write(DATA/(label+'.snapshot.json'),x);return x
 def census(self,label):
  x=json.loads(self.o.send('CENSUS'));p=DATA/(label+'.full-census.json');write(p,x);return p,x
 def compare(self,path):return json.loads(self.o.send('COMPARE '+str(path)))
 def export(self,label):
  ans=self.cmd('EXPORT_SAVE '+label);p=self.profile/'Saves'/(label+'.rws');record(label+'-artifact',{'path':str(p),'exists':p.exists(),'sha':f.sha(p) if p.exists() else None,'stagingQuarantine':[x.name for x in (self.profile/'Saves').glob('*') if 'Staging_' in x.name or 'Quarantine_' in x.name]});return ans,p
 def ticks(self,n):
  self.cmd('STEP_TICKS '+str(n)+' 20');t=time.monotonic()
  while time.monotonic()-t<40:
   s=self.b.send('STATUS')
   if 'RemainingStep=0,' in s:break
   time.sleep(.1)
  record(self.name+'-ticks-complete',s);return s
 def close(self):
  if self.p.poll() is None:
   try:self.b.send('SHUTDOWN')
   except Exception:pass
   try:self.p.wait(timeout=10)
   except subprocess.TimeoutExpired:self.p.kill();self.p.wait(timeout=10)
  for b in [self.b,self.o]:
   try:b.close()
   except Exception:pass
  record(self.name+'-exit',{'pid':self.p.pid,'exit':self.p.returncode})
def node(root,id):return root.find("game/maps/li/things/*[id='"+id+"']")
def facts(path):
 root=E.parse(path).getroot();m=root.find('game/maps/li');p=node(root,'Human302');animal=node(root,'LabradorRetriever207367');bench=node(root,'TableSculpting990014');bill=bench.find('billStack/bills/li') if bench is not None else E.Element('missing');bed=node(root,'Bed990012');nested=node(root,'MinifiedThing990030');power=node(root,'Battery509102');plant=node(root,'Plant_Rice990011');fire=node(root,'Fire990010')
 p=p if p is not None else E.Element('missing');animal=animal if animal is not None else E.Element('missing');bed=bed if bed is not None else E.Element('missing');nested=nested if nested is not None else E.Element('missing');power=power if power is not None else E.Element('missing');plant=plant if plant is not None else E.Element('missing')
 return {'skill':p.findtext("skills/skills/li[def='Shooting']/level"),'hediffs':[(x.findtext('def'),x.findtext('severity')) for x in p.findall('healthTracker/hediffSet/hediffs/li')],'held':p.findtext("inventory/innerContainer/innerList/li[id='MedicineIndustrial990005']/stackCount"),'master':animal.findtext('playerSettings/master'),'followDrafted':animal.findtext('playerSettings/followDrafted'),'followFieldwork':animal.findtext('playerSettings/followFieldwork'),'bill':E.tostring(bill,encoding='unicode'),'zones':[E.tostring(x,encoding='unicode') for x in m.findall('zoneManager/allZones/li')],'designations':[E.tostring(x,encoding='unicode') for x in m.findall('designationManager/allDesignations/li')],'fire':fire.findtext('fireSize') if fire is not None else None,'growth':plant.findtext('growth'),'age':plant.findtext('age'),'condition':[E.tostring(x,encoding='unicode') for x in m.findall('gameConditionManager/activeConditions/li')],'bed':bed.findtext('assignedPawns/li'),'relation':[E.tostring(x,encoding='unicode') for x in p.findall('social/directRelations/li')],'power':power.findtext('storedPower'),'nested':nested.findtext('innerContainer/innerList/li/def')}
def mutate(root,k):
 p=node(root,'Human302');m=root.find('game/maps/li')
 if k=='01':p.find("inventory/innerContainer/innerList/li[id='MedicineIndustrial990005']/stackCount").text='4'
 if k=='02':p.find("skills/skills/li[def='Shooting']/level").text='15'
 if k=='03':p.find("healthTracker/hediffSet/hediffs/li[def='Stab']/severity").text='1'
 if k=='04':hs=p.find('healthTracker/hediffSet/hediffs');hs.remove(hs.find("li[def='BionicTongue']"))
 if k=='05':ps=node(root,'LabradorRetriever207367').find('playerSettings');ps.remove(ps.find('master'));ps.find('followDrafted').text='False';ps.find('followFieldwork').text='False'
 if k=='06':node(root,'TableSculpting990014').find('billStack/bills/li/targetCount').text='25'
 if k=='07':m.find("zoneManager/allZones/li[label='Growing zone 1']/cells/li").text='(139, 0, 146)'
 if k=='08':m.find("designationManager/allDesignations/li[def='Mine']/target").text='(150, 0, 151)'
 if k=='09':node(root,'Fire990010').find('fireSize').text='.90'
 if k=='10':node(root,'Plant_Rice990011').find('growth').text='.40'
 if k=='11':m.find("gameConditionManager/activeConditions/li[def='Aurora']/duration").text='12000'
 if k=='12':node(root,'Bed990012').find('assignedPawns').clear();p.find('ownership/ownedBed').text='null'
 if k=='13':p.find("social/directRelations/li[otherPawn='Thing_Human309']/def").text='ExSpouse'
 if k=='14':node(root,'Battery509102').find('storedPower').text='200'
 if k=='15':node(root,'MinifiedThing990030').find('innerContainer/innerList/li/def').text='WoodLog'
def main():
 check();assert not MOD.exists();shutil.copy2(Q/'Observer/bin/Release/net472/QA.SemanticGate.Observer.dll',MOD);threading.Thread(target=watch,daemon=True).start()
 try:
  clean=Q/'Frozen/TargetSettlement_Clean_ContextB.rws';source=Q/'Frozen/CleanSettlementFixture.rws';record('source-static',facts(source));record('context-static',facts(clean))
  if '--resume' in sys.argv:
   h=Host('IndependentGateR3',1);assert h.load(clean);trusted=DATA/'clean-live.full-census.json';record('resume-baseline-comparator',h.compare(trusted))
  else:
   h=Host('IndependentGateR2',1);assert h.load(clean);snap=h.snap('clean-live');trusted,full=h.census('clean-live');record('clean-ready-census',{'entities':full['entityCount'],'errors':snap['errors'],'reservations':json.loads(h.o.send('RESERVATIONS'))})
   record('source-manifest-comparator',h.compare(Q/'Frozen/TargetSettlement_Clean_ContextB.census.json'))
   h.cmd('APPROVE_SEMANTIC '+str(trusted));h.export('CleanPositive');h.snap('clean-after-save')
  for i in range(1,16):
   k=f'{i:02}'
   if 'negative-'+k+'-gate' in RESULTS:continue
   root=E.parse(clean).getroot();mutate(root,k);p=DATA/(k+'-injected.rws');E.ElementTree(root).write(p,encoding='utf-8',xml_declaration=True);record('negative-'+k+'-input',{'source':facts(clean),'injected':facts(p),'sha':f.sha(p)})
   assert h.load(p,'Negative'+k);s=h.snap('negative-'+k+'-live');cp,c=h.census('negative-'+k+'-live');compare=h.compare(trusted);record('negative-'+k+'-comparator',compare)
   h.cmd('APPROVE_SEMANTIC '+str(trusted));res,out=h.export('Negative'+k+'_Blocked');record('negative-'+k+'-gate',{'mismatch':not compare['isPass'],'response':res,'finalExists':out.exists()})
   if k in ['02','03','04','06','07','13']:
    h.cmd('EXPORT_CENSUS SelfCorrupted'+k+' 0');selfm=h.profile/'Saves'/('SelfCorrupted'+k+'.census.json');h.cmd('APPROVE_SEMANTIC '+str(selfm));r,out=h.export('SelfCorrupted'+k+'_Approved');record('self-baseline-'+k,{'response':r,'exists':out.exists(),'saved':facts(out) if out.exists() else None,'manifestSHA':f.sha(selfm)})
  # Non-tick mutations: isolated load/approval, true direct engine mutation, real export.
  for mutation in ['skill','hediff','holder','zone','designation','relation','assignment','followFieldwork','plantAge','billSuspended']:
   assert h.load(clean,'Clean_'+mutation);h.cmd('APPROVE_SEMANTIC '+str(trusted));before=h.b.send('GET_SEMANTIC_STATUS');r=json.loads(h.o.send('MUTATE '+mutation));cp,c=h.census('non-tick-'+mutation);cmp=h.compare(trusted);after=h.b.send('GET_SEMANTIC_STATUS');out,p=h.export('NonTick_'+mutation);record('non-tick-'+mutation,{'mutation':r,'comparator':cmp,'before':before,'after':after,'export':out,'finalExists':p.exists()})
  # Path/provenance attacks use exact live census with altered metadata and immutable fixtures.
  assert h.load(clean,'Paths');cp,c=h.census('path-clean');foreign=copy.deepcopy(c);foreign.update(mapIndex=99,mapTile=-123,parentWorldObject='WorldObject_WRONG',playerFaction='Faction_WRONG',ticksGame=-999,manifestVersion='wrong')
  fp=DATA/'arbitrary-external-manifest.json';write(fp,foreign);record('manifest-wrong-context',{'compare':h.compare(fp),'approval':h.cmd('APPROVE_SEMANTIC '+str(fp))});h.export('WrongContext_Approved')
  oldgen=h.b.send('STATUS');assert h.load(clean,'ReloadGeneration');record('stale-generation-manifest',{'priorStatus':oldgen,'newStatus':h.b.send('STATUS'),'approval':h.cmd('APPROVE_SEMANTIC '+str(cp))});h.export('StaleManifest_Approved')
  for folder in ['Developer-A','Developer-B']:
   manifests=list((Q/'Frozen'/folder/'Saves').glob('*.census.json'))
   for p in manifests:record('developer-manifest-'+p.stem,{'path':str(p),'approval':h.cmd('APPROVE_SEMANTIC '+str(p))})
  replace=DATA/'replace-after-approval.json';write(replace,c);h.cmd('APPROVE_SEMANTIC '+str(replace));old=f.sha(replace);write(replace,{'invalidated':'different bytes'});r,p=h.export('ReplacedManifest_Approved');record('manifest-replaced',{'oldSHA':old,'newSHA':f.sha(replace),'export':r,'exists':p.exists()})
  # Save fault injection changes only QA copied outputs or live test state, not candidate code.
  for fault in ['silent-skill','broken-tail','mutate-skill','tick','generation']:
   assert h.load(clean,'Fault_'+fault);h.cmd('APPROVE_SEMANTIC '+str(trusted));h.o.send('ARM '+fault);r,p=h.export('SavedBytes_'+fault);ev=h.profile/'save-fault-evidence.json';record('save-fault-'+fault,{'export':r,'exists':p.exists(),'injection':json.loads(ev.read_text()) if ev.exists() else None,'semanticStatus':h.b.send('GET_SEMANTIC_STATUS'),'savedFacts':facts(p) if p.exists() and fault!='broken-tail' else None})
  # Actual log error / thrown exception: previous approved target must remain unchanged.
  for fault in ['error','throw']:
   assert h.load(clean,'Error_'+fault);h.cmd('APPROVE_SEMANTIC '+str(trusted));r,p=h.export('Prior_'+fault);old=f.sha(p) if p.exists() else None;h.cmd('APPROVE_SEMANTIC '+str(trusted));h.o.send('ARM '+fault);r,p=h.export('Prior_'+fault);record('save-error-'+fault,{'response':r,'priorSHA':old,'afterSHA':f.sha(p) if p.exists() else None,'preserved':p.exists() and f.sha(p)==old,'semanticStatus':h.b.send('GET_SEMANTIC_STATUS')})
  # Actual command ordering / context generation fences.
  assert h.load(clean,'Race');h.cmd('APPROVE_SEMANTIC '+str(trusted));h.ticks(1);h.export('TickBeforeExport_Blocked');h.cmd('APPROVE_SEMANTIC '+str(trusted));h.cmd('SET_TARGET_MAP 1');h.export('MapBeforeExport');h.close()
  # Three distinct fresh processes; authoritative input baseline kept separate from post-tick self evidence.
  a=Host('FreshA',2);assert a.load(clean);record('fresh-A-job-injection',json.loads(a.o.send('JOB')));a.census('fresh-A');a.snap('fresh-A');record('fresh-A-reservations',json.loads(a.o.send('RESERVATIONS')));a.cmd('APPROVE_SEMANTIC '+str(trusted));r,ap=a.export('IndependentA');a.close()
  b=Host('FreshB',3);assert b.load(ap);before=b.snap('fresh-B-before');bp,bc=b.census('fresh-B-before');record('fresh-A-B',{'comparator':b.compare(trusted),'reservations':json.loads(b.o.send('RESERVATIONS'))});b.ticks(100);b.export('B_PostTick_Unapproved');post=b.snap('fresh-B-post');postp,postc=b.census('fresh-B-post');b.cmd('EXPORT_CENSUS PostTickSelf 0');selfp=b.profile/'Saves/PostTickSelf.census.json';b.cmd('APPROVE_SEMANTIC '+str(selfp));r,bout=b.export('IndependentB');b.close()
  c=Host('FreshC',4);assert c.load(bout);c.snap('fresh-C');c.census('fresh-C');record('fresh-B-C',{'comparator':c.compare(postp),'reservations':json.loads(c.o.send('RESERVATIONS'))});c.close()
  # Source's claimed clean two-map load is a separate positive claim, not substituted by pruned context.
  d=Host('FullSource',5);assert d.load(source);d.snap('full-source');d.census('full-source');d.cmd('EXPORT_CENSUS FullSourceSelf 0');d.cmd('APPROVE_SEMANTIC '+str(d.profile/'Saves/FullSourceSelf.census.json'));d.export('FullSourcePositive');d.close()
  record('all-complete',True);check()
 except Exception as e:record('unhandled',{'error':repr(e)});raise
 finally:
  STOP.set()
  for h in OWNED:
   if h.p.poll() is None:
    try:h.close()
    except Exception:h.p.kill();h.p.wait(timeout=10)
  if MOD.exists() and f.sha(MOD)==f.sha(Q/'Observer/bin/Release/net472/QA.SemanticGate.Observer.dll'):MOD.unlink()
  write(Q/'candidate-after.json',f.candidates());write(Q/'production-after.json',f.prod());check()
if __name__=='__main__':main()
