import pathlib, socket, subprocess, time, json, hashlib, shutil, re, threading, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
WORKSPACE=ROOT.parent.parent
SCRATCH=pathlib.Path(r'C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch')
EXE=pathlib.Path(r'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe')
FIXTURE=SCRATCH/'Harden_Manifest/Saves/EngineComplexFixture.rws'
FREEZE=json.loads((ROOT/'candidate-freeze-manifest.json').read_text(encoding='utf-8-sig'))
owned=[]
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest().upper()
def check_identity():
    mismatches=[v['path'] for v in FREEZE.values() if sha(v['path'])!=v['sha256'].upper()]
    if mismatches: raise RuntimeError('REVISION MISMATCH: stop all candidate testing: '+repr(mismatches))
def write_json(p,data): pathlib.Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
class Bridge:
    def __init__(self,port,timeout=45):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=timeout);self.s.settimeout(timeout)
        self.file=self.s.makefile('r',encoding='utf-8-sig',newline='')
    def send(self,cmd):
        self.s.sendall((cmd+'\n').encode()); lines=[]
        while True:
            line=self.file.readline()
            if not line: raise RuntimeError('EOF before END marker')
            line=line.rstrip('\r\n').lstrip('\ufeff')
            if line=='---END---': return '\n'.join(lines)
            lines.append(line)
    def close(self):
        try:self.file.close()
        finally:self.s.close()
def profile(name,source=FIXTURE,observer=False,omit_mod=None):
    p=ROOT/name
    if p.exists(): raise RuntimeError('Refusing to overwrite prior QA profile '+str(p))
    (p/'Config').mkdir(parents=True);(p/'Saves').mkdir()
    cfg=ET.parse(SCRATCH/'Harden_Manifest/Config/ModsConfig.xml')
    mods=cfg.getroot().find('activeMods')
    if observer: ET.SubElement(mods,'li').text='qacodex.boundary02.observer'
    if omit_mod:
        for m in list(mods):
            if m.text==omit_mod:mods.remove(m)
    cfg.write(p/'Config/ModsConfig.xml',encoding='utf-8',xml_declaration=True)
    shutil.copy2(SCRATCH/'Harden_Manifest/Config/Prefs.xml',p/'Config/Prefs.xml')
    if source:shutil.copy2(source,p/'Saves/Input.rws')
    return p
def launch(p,port,qaport,obsport=None):
    check_identity()
    args=[str(EXE),'-batchmode','-savedatafolder='+str(p),'-logfile',str(p/'player.log'),'-bridgeport='+str(port),'-qaport='+str(qaport)]
    if obsport:args+=['-obsport='+str(obsport)]
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
    proc=subprocess.Popen(args,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW,cwd=str(ROOT));owned.append(proc)
    write_json(p/'launch.json',{'pid':proc.pid,'args':args,'start_utc':time.time(),'candidate_dll':sha(FREEZE['WarEconomy.WorkerBridge.PoC.dll (Assemblies)']['path'])})
    start=time.monotonic()
    while time.monotonic()-start<120:
        if proc.poll() is not None:raise RuntimeError('Worker exited '+str(proc.returncode))
        try:
            b=Bridge(port,10);hello=b.send('HELLO');(p/'hello.txt').write_text(hello,encoding='utf-8');return proc,b
        except (OSError,RuntimeError):time.sleep(.5)
    raise TimeoutError('Worker bridge bootstrap')
def command(b,cmd,p,name):
    check_identity();start=time.monotonic();response=b.send(cmd)
    data={'command':cmd,'response':response,'roundtrip_ms':(time.monotonic()-start)*1000}
    write_json(p/(name+'.json'),data);return data
def load(b,p,name='Input',target=0):
    check_identity();start=time.monotonic();response=b.send(f'LOAD_SAVE {name} {target}');states=[]
    while time.monotonic()-start<120:
        status=b.send('STATUS');states.append({'elapsed':time.monotonic()-start,'status':status})
        if 'STATE: READY,' in status or 'STATE: LOAD_FAILED,' in status:break
        time.sleep(.15)
    else:raise TimeoutError('Load did not reach terminal lifecycle')
    result={'request':response,'states':states,'ready':'STATE: READY,' in status,'elapsed_ms':(time.monotonic()-start)*1000}
    write_json(p/('load-'+name+'.json'),result);return result
def parsed(s):
    return {k:int(v) for k,v in re.findall(r'(Gen|Maps|TicksGame|TicksSim|RemainingStep|TargetMap)=(-?\d+)',s)}
def step(b,p,n,slice=20):
    response=b.send(f'STEP_TICKS {n} {slice}');start=time.monotonic()
    while time.monotonic()-start<120:
        s=b.send('STATUS')
        if parsed(s).get('RemainingStep')==0:break
        time.sleep(.04)
    else:raise TimeoutError('Steps incomplete')
    return {'response':response,'status':s,'ms':(time.monotonic()-start)*1000}
def stop(proc,b,p):
    try:response=b.send('SHUTDOWN');write_json(p/'shutdown.json',{'response':response})
    finally:
        b.close()
        try:proc.wait(timeout=15)
        except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
def cleanup():
    for proc in owned:
        if proc.poll() is None:proc.kill();proc.wait(timeout=10)
    check_identity()
    write_json(ROOT/'owned-process-cleanup.json',{'pids':[p.pid for p in owned],'all_terminated':all(p.poll() is not None for p in owned)})
