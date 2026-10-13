from pathlib import Path
import json,hashlib,socket,time,subprocess,shutil,xml.etree.ElementTree as ET,base64,uuid
ROOT=Path(__file__).resolve().parent
SCRATCH=Path(r'C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch')
EXE=Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe')
def write(name,value):
 (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def identity():
 for v in json.loads((ROOT/'identity-before.json').read_text(encoding='utf-8')):
  if hashlib.sha256(Path(v['path']).read_bytes()).hexdigest().upper()!=v['actual']:raise RuntimeError('REVISION MISMATCH '+v['path'])
def send(port,text,timeout=55):
 identity();start=time.monotonic()
 with socket.create_connection(('127.0.0.1',port),timeout) as s:
  s.settimeout(timeout);s.sendall((text+'\n').encode());f=s.makefile('r',encoding='utf-8-sig');response=f.readline().rstrip('\r\n')
 return {'response':response,'roundtrip_ms':(time.monotonic()-start)*1000,'response_utf8_bytes':len(response.encode('utf-8'))}
def cmd(kind,**extra):return {'CommandId':str(uuid.uuid4()),'CommandType':kind,'Token':'Player_A_Token','Generation':1,**extra}
def worker(c):
 r=send(29800,json.dumps(c));r['command']=c;r['parsed']=json.loads(r['response']);return r
def rpc(c):
 r=send(31701,'RPC '+base64.b64encode(json.dumps(c).encode()).decode());r['command']=c;r['parsed']=json.loads(r['response']);return r
def snap():
 r=send(31701,'SNAP');r['xml']=ET.fromstring(r['response']);return r
def ready(profile,port,worker_mode):
 deadline=time.monotonic()+120
 while time.monotonic()<deadline:
  try:
   result=worker(cmd('STATUS')) if worker_mode else send(port,'STATUS')
   text=result['parsed']['Message'] if worker_mode else result['response']
   if ('MAPS=2' in text or 'Maps=2' in text) and ('PAWNS=51' in text or 'Pawns=51' in text):return result
  except (OSError,ValueError):pass
  time.sleep(.4)
 raise RuntimeError('Native map not ready in '+profile)

def launch_pair():
 identity();owned=[]
 try:
  for name,old in [('Worker','RemoteTactical_WorkerData'),('GraphicalClient','RemoteTactical_ClientData')]:
   p=ROOT/name
   if p.exists():raise RuntimeError('Refusing to overwrite QA profile '+str(p))
   (p/'Config').mkdir(parents=True);(p/'Saves').mkdir()
   cfg=ET.parse(SCRATCH/old/'Config/ModsConfig.xml');ET.SubElement(cfg.getroot().find('activeMods'),'li').text='qacodex.remote.presentation.observer';cfg.write(p/'Config/ModsConfig.xml',encoding='utf-8',xml_declaration=True)
   prefs=ET.parse(SCRATCH/old/'Config/Prefs.xml')
   for key,value in [('screenWidth','1280'),('screenHeight','900'),('fullScreen','False'),('pauseOnError','False')]:
    n=prefs.getroot().find(key)
    if n is None:n=ET.SubElement(prefs.getroot(),key)
    n.text=value
   prefs.write(p/'Config/Prefs.xml',encoding='utf-8',xml_declaration=True)
   shutil.copy2(SCRATCH/'Harden_Manifest/Saves/EngineComplexFixture.rws',p/'Saves/EngineComplexFixture.rws')
   args=[str(EXE),'-savedatafolder='+str(p),'-logfile',str(p/'player.log')]
   if name=='Worker':args+=['-batchmode','-nographics','-remote-worker','-worker-port','29800','-qa-port','31700']
   else:args+=['-remote-client','-client-port','29801','-connect','127.0.0.1:29800','-qa-port','31701','-screen-fullscreen','0','-screen-width','1280','-screen-height','900']
   startup=subprocess.STARTUPINFO()
   startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
   startup.wShowWindow = 0 if name=='Worker' else 1
   proc=subprocess.Popen(args,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW if name=='Worker' else 0);owned.append(proc)
   write(name+'/launch.json',{'pid':proc.pid,'args':args,'utc':time.time()})
   deadline=time.monotonic()+120
   while time.monotonic()<deadline:
    try:
     pong=worker(cmd('PING')) if name=='Worker' else send(29801,'PING',3)
     if 'PONG' in pong['response']:break
    except OSError:pass
    time.sleep(.5)
   else:raise RuntimeError('Listener failed '+name)
   load=worker(cmd('LOAD_SAVE',CustomData='EngineComplexFixture')) if name=='Worker' else send(29801,'LOAD_SAVE EngineComplexFixture')
   write(name+'/load.json',load);write(name+'/ready.json',ready(name,29801,name=='Worker'))
  write('connect.json',send(29801,'CONNECT_WORKER 127.0.0.1:29800'))
  write('pair-ready.json',{'pids':[x.pid for x in owned],'utc':time.time()});print('PAIR READY',flush=True)
  deadline=time.monotonic()+3600
  while time.monotonic()<deadline and not (ROOT/'STOP').exists():
   if any(x.poll() is not None for x in owned):raise RuntimeError('Owned process exited early')
   time.sleep(.5)
 finally:
  for proc in reversed(owned):
   if proc.poll() is None:
    proc.terminate()
    try:proc.wait(timeout=10)
    except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
  write('pair-cleanup.json',{'pids':[x.pid for x in owned],'exit_codes':[x.poll() for x in owned]})
if __name__=='__main__':launch_pair()
