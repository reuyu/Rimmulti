import independent_run as h,psutil,threading,time,json,subprocess
h.results={"date":"2026-10-02","tests":{}}
def write():(h.ROOT/"capacity-results.json").write_text(json.dumps(h.results,ensure_ascii=False,indent=2),encoding="utf-8")
h.write=write
try:
    pf1=h.prepare("Concurrent1");p1,b1=h.launch(pf1,29226);h.record("load1",h.load(b1,"Input",pf1))
    pf2=h.prepare("Concurrent2");p2,b2=h.launch(pf2,29227);h.record("load2",h.load(b2,"Input",pf2))
    proc1,proc2=psutil.Process(p1.pid),psutil.Process(p2.pid)
    cpu1,cpu2=proc1.cpu_times(),proc2.cpu_times()
    start=time.monotonic();measure=[]
    outputs={}
    def tick(b,pf,name):
        try:outputs[name]=h.command(b,"RUN_TICKS 10000",pf,"ticks")
        except Exception as e:outputs[name]={"error":repr(e)}
    ts=[threading.Thread(target=tick,args=(b1,pf1,"worker1")),threading.Thread(target=tick,args=(b2,pf2,"worker2"))]
    for t in ts:t.start()
    try:
        gpu=subprocess.run([r"C:\WINDOWS\system32\nvidia-smi.exe","--query-gpu=name,utilization.gpu,memory.used,memory.total","--format=csv,noheader"],capture_output=True,text=True,timeout=5)
        h.record("host_gpu_sample",{"stdout":gpu.stdout,"stderr":gpu.stderr,"exit_code":gpu.returncode,"scope":"aggregate host sample during two-worker burst; not per-worker VRAM or peak"})
    except Exception as e:h.record("host_gpu_sample",{"unavailable":repr(e)})
    while any(t.is_alive() for t in ts):
        measure.append({"elapsed_sec":time.monotonic()-start,"worker1_rss":proc1.memory_info().rss,"worker2_rss":proc2.memory_info().rss})
        time.sleep(.2)
    for t in ts:t.join()
    elapsed=time.monotonic()-start
    after1,after2=proc1.cpu_times(),proc2.cpu_times()
    h.record("simultaneous_burst",{"responses":outputs,"wall_sec":elapsed,"logical_cpu_count":psutil.cpu_count(),"cpu_seconds1":after1.user+after1.system-cpu1.user-cpu1.system,"cpu_seconds2":after2.user+after2.system-cpu2.user-cpu2.system,"sampled_peak_rss1":max(x["worker1_rss"] for x in measure),"sampled_peak_rss2":max(x["worker2_rss"] for x in measure),"samples":measure})
    h.record("export1",h.command(b1,"EXPORT_SAVE ConcurrentExport",pf1,"export"))
    h.record("export2",h.command(b2,"EXPORT_SAVE ConcurrentExport",pf2,"export"))
    h.record("file_isolation",{"worker1_export":str(pf1/"Saves/ConcurrentExport.rws"),"worker2_export":str(pf2/"Saves/ConcurrentExport.rws"),"same_path":(pf1/"Saves/ConcurrentExport.rws").resolve()==(pf2/"Saves/ConcurrentExport.rws").resolve(),"port1":29226,"port2":29227,"pid1":p1.pid,"pid2":p2.pid})
    h.shutdown(p1,b1,pf1)
    b2.close();p2.kill();p2.wait(timeout=10)
    h.record("F04_owned_process_kill",{"pid":p2.pid,"exit_code":p2.returncode,"has_exited":p2.poll() is not None,"scope":"loaded-map process crash detection; no durable recovery tested"})
except Exception as e:h.record("FATAL",{"error":repr(e)});raise
finally:
    for p in h.owned:
        if p.poll() is None:p.kill();p.wait(timeout=10)
    write()

