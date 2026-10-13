from pathlib import Path
import json,subprocess,socket,time,shutil,hashlib,xml.etree.ElementTree as E,collections,sys,os
Q=Path(__file__).parent.resolve();R=Q.parent.parent;DATA=Q/'Evidence';DATA.mkdir(exist_ok=True)
EXE=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe')
MOD=R/'QA-Tactical-Engine/ENGINE02-20261002/ProbeMod/1.6/Assemblies/QA.RoundTrip.Observer.dll'
RESULTS={};OWNED=[]
sys.path.insert(0,str(Q/'Frozen'));from census_oracle import CensusOracle
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def record(k,v):RESULTS[k]=v;write(DATA/'results.json',RESULTS);print(k,json.dumps(v,ensure_ascii=False)[:1600],flush=True)
class Bridge:
 def __init__(self,port):self.s=socket.create_connection(('127.0.0.1',port),timeout=2);self.s.settimeout(65);self.f=self.s.makefile('r',encoding='utf-8')
 def send(self,cmd):
  self.s.sendall((cmd+'\n').encode());lines=[]
  while True:
   l=self.f.readline()
   if not l:raise EOFError(cmd)
   l=l.strip('\r\n').lstrip('\ufeff')
   if l=='---END---':return '\n'.join(lines)
   lines.append(l)
 def close(self):self.f.close();self.s.close()
class Host:
 def __init__(self,name,source,index):
  self.name=name;self.profile=Q/'Profiles'/name;self.profile.mkdir(parents=True,exist_ok=False);(self.profile/'Saves').mkdir();(self.profile/'Config').mkdir()
  mods=['brrainz.harmony','ludeon.rimworld','ludeon.rimworld.royalty','ludeon.rimworld.ideology','ludeon.rimworld.biotech','ludeon.rimworld.anomaly','ludeon.rimworld.odyssey','wareconomy.hybridmultiplayer','wareconomy.workerbridge.poc','qacodex.engine02.probe']
  (self.profile/'Config/ModsConfig.xml').write_text('<?xml version="1.0"?><ModsConfigData><version>1.6.4871 rev591</version><activeMods>'+''.join('<li>'+m+'</li>' for m in mods)+'</activeMods><knownExpansions>'+''.join('<li>'+m+'</li>' for m in mods[2:7])+'</knownExpansions></ModsConfigData>',encoding='utf-8')
  (self.profile/'Config/Prefs.xml').write_text('<PrefsData><volumeGame>0</volumeGame><volumeMusic>0</volumeMusic><devMode>True</devMode><runInBackground>True</runInBackground></PrefsData>',encoding='utf-8')
  shutil.copy2(source,self.profile/'Saves/Input.rws');self.port=32100+index;self.obsport=32200+index;qp=32300+index
  for port in [self.port,self.obsport,qp]:
   with socket.socket() as s:s.bind(('127.0.0.1',port))
  cmd=[str(EXE),'-batchmode',f'-savedatafolder={self.profile}','-logFile',str(self.profile/'player.log'),f'-bridgeport={self.port}',f'-qaport={qp}',f'-rtqaport={self.obsport}']
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  self.p=subprocess.Popen(cmd,cwd=Q,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);OWNED.append(self);self.b=None;self.o=None;t=time.monotonic()
  while time.monotonic()-t<65:
   if self.p.poll() is not None:raise RuntimeError(f'{name} early exit {self.p.returncode}')
   try:self.b=Bridge(self.port);self.hello=self.b.send('HELLO');self.o=Bridge(self.obsport);break
   except (OSError,EOFError):time.sleep(.3)
  if not self.b or not self.o:raise TimeoutError(name+' startup')
  record(name+'-launch',{'pid':self.p.pid,'args':cmd,'startupMs':(time.monotonic()-t)*1000,'hello':self.hello,'inputSha':sha(source),'mods':mods,'observerSha':sha(MOD)})
  self.load=self.b.send('LOAD_SAVE Input');deadline=time.monotonic()+100;self.states=[]
  while time.monotonic()<deadline:
   status=self.b.send('STATUS');self.states.append(status)
   if 'STATE: READY' in status or 'STATE: LOAD_FAILED' in status:break
   time.sleep(.3)
  self.ready='STATE: READY' in status;record(name+'-load',{'load':self.load,'ready':self.ready,'status':status,'states':self.states})
 def snap(self,label):
  x=json.loads(self.o.send('SNAP'));write(DATA/(label+'.snapshot.json'),x);return x
 def census(self,label):
  x=json.loads(self.b.send('GET_CENSUS_JSON 0'));write(DATA/(label+'.census.json'),x);return x
 def export(self,name):
  ans=self.b.send('EXPORT_SAVE '+name);p=self.profile/'Saves'/(name+'.rws');record(self.name+'-export-'+name,{'response':ans,'exists':p.exists(),'sha256':sha(p) if p.exists() else None,'bytes':p.stat().st_size if p.exists() else None});return p
 def ticks(self,n):
  before=self.b.send('STATUS');ans=self.b.send('STEP_TICKS '+str(n));deadline=time.monotonic()+40
  while time.monotonic()<deadline:
   st=self.b.send('STATUS')
   if 'RemainingStep=0,' in st:break
   time.sleep(.05)
  record(self.name+'-ticks-'+str(n),{'before':before,'response':ans,'after':st});return st
 def close(self):
  if self.p.poll() is None:
   try:self.b.send('SHUTDOWN')
   except Exception:pass
   try:self.p.wait(timeout=8)
   except subprocess.TimeoutExpired:self.p.kill();self.p.wait(timeout=8)
  for b in [self.b,self.o]:
   try:b.close()
   except Exception:pass
  record(self.name+'-exit',{'pid':self.p.pid,'exitCode':self.p.returncode})
def prune(source,target):
 t=E.parse(source);g=t.getroot().find('game');maps=g.find('maps');parent=maps[0].findtext('mapInfo/parent');id=parent.split('_')[-1]
 for m in list(maps)[1:]:maps.remove(m)
 objects=g.find('world/worldObjects/worldObjects')
 for obj in list(objects):
  if obj.findtext('ID')!=id:objects.remove(obj)
 t.write(target,encoding='utf-8',xml_declaration=True);return {'parent':parent,'maps':len(maps),'worldObjects':len(objects),'sha256':sha(target)}
GEO={'Granite','Slate','Limestone','Marble','Sandstone','MineableSteel','MineableSilver','MineableJade','MineableUranium','MineableGold','MineablePlasteel','MineableComponentsIndustrial','ChunkGranite','ChunkLimestone','ChunkSlate','ChunkMarble','ChunkSandstone'}
def normalize(s,mapindex=0):
 m=s['maps'][mapindex];custody={};environment=[]
 for id,v in m['entities'].items():
  if v['category'] in ('Filth','Plant') or v['def']=='Fire' or v['def'] in GEO:
   f=v['fields'];environment.append({'def':v['def'],'pos':v['pos'],'hp':v['hp'],'stack':v['stack'],'state':{k:f[k] for k in ['fireSize','growthInt','ageInt','thickness','ticksSinceSpawn','ticksSinceThickened','unlitTicks','sown'] if k in f}});continue
  c={k:v.get(k) for k in ['id','def','class','stack','hp','pos','rot','stuff','faction','holder']}
  if 'pawn' in v:
   p=v['pawn'];c['pawn']={k:p[k] for k in ['skills','equipment','apparel','inventory','ownedBed','master','followDrafted','followFieldwork','relations','bio','chrono','food','rest','ideology']};c['pawn']['hediffs']=[{k:h[k] for k in ['id','def','part','severity']} for h in p['hediffs']];c['job']=p['job']
  if 'bills' in v:c['bills']=v['bills']
  if 'assignedPawns' in v:c['assignedPawns']=v['assignedPawns']
  if 'power' in v:c['power']=v['power']
  # Stable, saved comp scalar/reference fields; independent static oracle supplements hidden fields.
  c['comps']=[x for x in v.get('comps',[]) if any(k in x['fields'] for k in ['storedEnergy','quality','fuel','refuelTargetFuelLevel'])]
  custody[id]=c
 return {'custody':custody,'environment':sorted(environment,key=lambda e:json.dumps(e,sort_keys=True)),'zones':m['zones'],'designations':m['designations'],'conditions':m['conditions'],'weather':m['weather'],'duplicates':m['duplicateIds'],'errors':s['errors']}
def diff(a,b,path='$',out=None):
 if out is None:out=[]
 if type(a)!=type(b):out.append({'path':path,'expected':a,'actual':b});return out
 if isinstance(a,dict):
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:out.append({'path':path+'.'+str(k),'expected':a.get(k),'actual':b.get(k)})
   else:diff(a[k],b[k],path+'.'+str(k),out)
 elif isinstance(a,list):
  if len(a)!=len(b):out.append({'path':path+'.length','expected':len(a),'actual':len(b)})
  for i,(x,y) in enumerate(zip(a,b)):diff(x,y,path+'['+str(i)+']',out)
 elif a!=b:out.append({'path':path,'expected':a,'actual':b})
 return out
def main():
 assert not MOD.exists();shutil.copy2(Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll',MOD)
 try:
  a=Host('A_Source',Q/'Frozen/ComplexSettlementFixture.rws',1);assert a.ready
  ac=a.census('A-baseline');asnap=a.snap('A-baseline');write(DATA/'trusted-baseline.normalized.json',normalize(asnap));source=a.export('A_FullExport');a.close()
  target=DATA/'A_TargetArtifact.rws';record('target-extraction',prune(source,target));record('source-vs-context-dependencies',{'sourceMaps':len(asnap['maps']),'sourceWorldObjects':len(asnap['worldObjects'])})
  b=Host('B_Target',target,2);assert b.ready;bc=b.census('B-before');bs=b.snap('B-before')
  changes=diff(normalize(asnap),normalize(bs));write(DATA/'A-to-B.diff.json',changes);record('fresh-A-to-B',{'errors':len(changes),'sample':changes[:12],'pidA':a.p.pid,'pidB':b.p.pid,'mapsB':len(bs['maps']),'objectsB':bs['worldObjects'],'observerErrors':bs['errors']})
  job=json.loads(b.o.send('JOB'));record('active-job-created',job);b.snap('B-active-job');active=b.export('B_ActiveJob')
  b.ticks(100);post=b.snap('B-posttick');b.census('B-posttick');postpath=b.export('B_PostTick');b.close()
  c=Host('C_Rematerialized',postpath,3);assert c.ready;cs=c.snap('C-reloaded');c.census('C-reloaded');changes2=diff(normalize(post),normalize(cs));write(DATA/'B-to-C.diff.json',changes2);record('fresh-B-to-C',{'errors':len(changes2),'sample':changes2[:12],'pidB':b.p.pid,'pidC':c.p.pid,'mapsC':len(cs['maps']),'observerErrors':cs['errors']});c.close()
  d=Host('D_ActiveJobReload',active,4);assert d.ready;ds=d.snap('D-job-reload');d.ticks(40);d.snap('D-job-after40');record('job-reload',{'source':str(active),'BJob':next(v['pawn']['job'] for v in json.loads((DATA/'B-active-job.snapshot.json').read_text(encoding='utf-8'))['maps'][0]['entities'].values() if v['id']=='Human302'),'DJob':ds['maps'][0]['entities']['Human302']['pawn']['job'],'reservationsD':ds['maps'][0]['reservations']});d.close()
  record('core-complete',{'AtoBErrors':len(changes),'BtoCErrors':len(changes2),'targetArtifact':str(target),'postArtifact':str(postpath),'pids':[a.p.pid,b.p.pid,c.p.pid]})
 except Exception as e:record('unhandled',{'error':repr(e)});raise
 finally:
  for h in OWNED:
   if h.p.poll() is None:
    try:h.close()
    except Exception:h.p.kill();h.p.wait(timeout=10)
  # Observer is QA-only temporary instrumentation, exact bytes checked before removing own single file.
  if MOD.exists() and sha(MOD)==sha(Q/'Observer/bin/Release/net472/QA.RoundTrip.Observer.dll'):MOD.unlink()
if __name__=='__main__':main()
