import pathlib, socket, subprocess, time, json, hashlib, shutil, re, threading, xml.etree.ElementTree as ET, ctypes
ROOT=pathlib.Path(__file__).resolve().parent
SCRATCH=pathlib.Path(r"C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch")
EXE=pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")
ORIGINAL=SCRATCH/"OriginalSave/QA_Phase3_Baseline_20261001.rws"
owned=[]
results={"date":"2026-10-02 Asia/Seoul","tests":{}}
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest().upper()
def write():
    (ROOT/"run-results.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
def record(name,data):
    results["tests"][name]=data
    write()
    print(name,json.dumps(data,ensure_ascii=False),flush=True)
class Bridge:
    def __init__(self,port,timeout=30):
        self.s=socket.create_connection(("127.0.0.1",port),timeout=timeout);self.s.settimeout(timeout)
        self.file=self.s.makefile("r",encoding="utf-8-sig",newline="")
    def send(self,cmd):
        self.s.sendall((cmd+"\n").encode())
        lines=[]
        while True:
            l=self.file.readline()
            if not l: raise RuntimeError("EOF before END")
            l=l.rstrip("\r\n").lstrip("\ufeff")
            if l=="---END---":break
            lines.append(l)
        return "\n".join(lines)
    def close(self):
        self.file.close(); self.s.close()
def prepare(name,source=ORIGINAL,save_name="Input"):
    profile=ROOT/name
    if profile.exists(): raise RuntimeError("Refusing overwrite of previous run: "+str(profile))
    (profile/"Config").mkdir(parents=True);(profile/"Saves").mkdir()
    shutil.copy2(SCRATCH/"WorkerData_Session1/Config/ModsConfig.xml",profile/"Config/ModsConfig.xml")
    shutil.copy2(SCRATCH/"WorkerData_Session1/Config/Prefs.xml",profile/"Config/Prefs.xml")
    if source: shutil.copy2(source,profile/"Saves"/(save_name+".rws"))
    return profile
def launch(profile,port):
    args=[str(EXE),"-batchmode","-savedatafolder="+str(profile),"-logfile",str(profile/"player.log"),"-bridgeport="+str(port)]
    si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
    start=time.monotonic()
    p=subprocess.Popen(args,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW,cwd=str(ROOT))
    owned.append(p)
    (profile/"launch.json").write_text(json.dumps({"pid":p.pid,"port":port,"args":args,"start":time.time()},indent=2),encoding="utf-8")
    for _ in range(180):
        if p.poll() is not None: raise RuntimeError("Worker exited "+str(p.returncode))
        try:
            b=Bridge(port);h=b.send("HELLO"); break
        except (OSError,RuntimeError):time.sleep(.5)
    else:raise TimeoutError("No bridge")
    # Enumerate window handles only; no screen/UI interaction.
    visible=[]
    try:
        callback=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
        def each(hwnd,_):
            pid=ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
            if pid.value==p.pid and ctypes.windll.user32.IsWindowVisible(hwnd): visible.append(int(hwnd))
            return True
        ctypes.windll.user32.EnumWindows(callback(each),0)
    except Exception as e:visible=["unavailable: "+repr(e)]
    record("launch_"+profile.name,{"pid":p.pid,"startup_ms":round((time.monotonic()-start)*1000,1),"hello":h,"visible_windows":visible})
    return p,b
def load(b,name,profile):
    start=time.monotonic(); response=b.send("LOAD_SAVE "+name);states=[]
    while time.monotonic()-start<90:
        s=b.send("STATUS");states.append(s)
        if s.startswith("STATE: Playing"):break
        time.sleep(.5)
    else:raise TimeoutError("Load not Playing")
    (profile/"load.txt").write_text(response+"\n"+"\n".join(states),encoding="utf-8")
    return {"response":response,"state":s,"load_ms":round((time.monotonic()-start)*1000,1)}
def command(b,cmd,profile,name):
    start=time.monotonic();r=b.send(cmd)
    (profile/(name+".txt")).write_text(r,encoding="utf-8")
    return {"response":r,"roundtrip_ms":round((time.monotonic()-start)*1000,1)}
def shutdown(p,b,profile):
    response=b.send("SHUTDOWN");b.close()
    try:p.wait(timeout=15)
    except subprocess.TimeoutExpired:p.kill();p.wait()
    record("shutdown_"+profile.name,{"response":response,"exit_code":p.returncode})
def xml_inventory(path):
    r=ET.parse(path).getroot(); g=r.find("game")
    maps=[]
    for m in g.find("maps"):
        pawns=[t for t in m.find("things") if t.get("Class")=="Pawn"]
        maps.append({"uniqueID":m.findtext("uniqueID"),"parent":m.findtext("mapInfo/parent"),"things":len(m.find("things")),"pawns":len(pawns),"human":[t.findtext("id") for t in pawns if t.findtext("def")=="Human"]})
    return {"ticks":g.findtext("tickManager/ticksGame"),"maps":maps}
def main():
    pre=sha(ORIGINAL);record("original_before",{"path":str(ORIGINAL),"sha256":pre,"size":ORIGINAL.stat().st_size})
    profile1=prepare("Independent1");p1,b1=launch(profile1,29220)
    record("load1",load(b1,"Input",profile1))
    record("maps1",command(b1,"GET_MAP_INFO",profile1,"map-info"))
    command(b1,"GET_ENTITY_SUMMARY",profile1,"before")
    record("tick1000",command(b1,"RUN_TICKS 1000",profile1,"tick1000"))
    command(b1,"GET_ENTITY_SUMMARY",profile1,"after")
    record("export1",command(b1,"EXPORT_SAVE IndependentExport",profile1,"export"))
    export1=profile1/"Saves/IndependentExport.rws"
    record("export1_xml",xml_inventory(export1))
    shutdown(p1,b1,profile1)
    profile2=prepare("Independent2",export1,"Reload");p2,b2=launch(profile2,29221)
    record("load2",load(b2,"Reload",profile2))
    command(b2,"GET_ENTITY_SUMMARY",profile2,"reloaded")
    record("export2",command(b2,"EXPORT_SAVE ReloadExport",profile2,"export"))
    command(b2,"RUN_TICKS nonsense",profile2,"malformed-ticks")
    command(b2,"NO_SUCH_COMMAND",profile2,"unknown-command")
    bdrop=Bridge(29221);r=bdrop.send("HELLO");bdrop.close()
    breconnect=Bridge(29221);rr=breconnect.send("HELLO");breconnect.close()
    record("F05_reconnect",{"first":r,"second":rr,"worker_alive":p2.poll() is None})
    longb=Bridge(29221,timeout=60);statusb=Bridge(29221,timeout=60)
    long_result={}
    def runlong():
        try:long_result.update(command(longb,"RUN_TICKS 50000",profile2,"long-ticks"))
        except Exception as e:long_result["error"]=repr(e)
    t=threading.Thread(target=runlong);t.start();time.sleep(.15)
    sr=command(statusb,"STATUS",profile2,"during-long-ticks-status")
    t.join(timeout=60)
    record("long_tick_servicing",{"ticks":long_result,"parallel_status":sr})
    longb.close();statusb.close()
    # Missing/corrupted load after an already loaded valid map checks stale success.
    (profile2/"Saves/Corrupted.rws").write_text("<savegame><game><broken>",encoding="utf-8")
    record("F02_load_request",command(b2,"LOAD_SAVE Corrupted",profile2,"corrupt-load-request"))
    time.sleep(3)
    record("F02_after_valid",command(b2,"STATUS",profile2,"corrupt-load-status"))
    record("F01_load_request",command(b2,"LOAD_SAVE DoesNotExist",profile2,"missing-load-request"))
    time.sleep(2)
    record("F01_status",command(b2,"STATUS",profile2,"missing-load-status"))
    shutdown(p2,b2,profile2)
    post=sha(ORIGINAL);record("original_after",{"sha256":post,"unchanged":pre==post})
if __name__=="__main__":
    try:main()
    except Exception as e:
        record("FATAL",{"type":type(e).__name__,"message":str(e)})
        raise
    finally:
        for p in owned:
            if p.poll() is None:
                p.kill()
                try:p.wait(timeout=10)
                except subprocess.TimeoutExpired:pass
        results["owned_processes_terminated"]=all(p.poll() is not None for p in owned)
        write()

