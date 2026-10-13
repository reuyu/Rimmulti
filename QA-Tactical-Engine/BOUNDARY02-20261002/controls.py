from harness import *
from concurrent.futures import ThreadPoolExecutor
def frames(q,p,name):
    response=command(q,'FRAME_STATS',p,name)['response'];rows=[]
    for line in response.splitlines():
        fr,ms,calls,g=line.split(',');rows.append({'frame':int(fr),'ms':float(ms),'calls':int(calls),'Gstart':int(g)})
    return rows
def debt_case(b,q,p,name,prelude):
    b.send('PAUSE_SIMULATION');prelude();q.send('FRAME_RESET')
    before=parsed(b.send('STATUS'));t0=time.monotonic();response=b.send('START_SIMULATION 60');samples=[]
    while time.monotonic()-t0<3.0:
        start=time.monotonic();status=b.send('STATUS');end=time.monotonic();samples.append({'t_start':start-t0,'t_end':end-t0,**parsed(status)});time.sleep(.025)
    pause=b.send('PAUSE_SIMULATION');f=frames(q,p,name+'-frames');final=parsed(b.send('STATUS'));time.sleep(.35);idle=parsed(b.send('STATUS'))
    s0,s1=samples[0],samples[-1];tps=(s1['TicksSim']-s0['TicksSim'])/(s1['t_end']-s0['t_end'])
    result={'start_response':response,'pause_response':pause,'before':before,'after_pause':final,'after_idle':idle,'samples':samples,'TPS':tps,'first_frame_counts':[x['calls'] for x in f[:8]],'max_frame_calls':max((x['calls'] for x in f),default=0),'first_tick_after_start_ms':None if not f else f[0]['ms'],'paused_stable':final['TicksSim']==idle['TicksSim']}
    write_json(p/(name+'.json'),result);print(name,{'tps':tps,'first_frame_counts':result['first_frame_counts'],'max':result['max_frame_calls']},flush=True);return result
results={}
try:
    p=profile('ConcurrentControls',observer=True);proc,b=launch(p,29605,30605,31605);q=Bridge(31605)
    load_result=load(b,p)
    if not load_result['ready']:raise RuntimeError('Valid control fixture did not become READY')
    command(q,'EVENTS',p,'load-lifecycle-events')
    pre=parsed(b.send('STATUS'));rr=command(b,'RUN_TICKS 50000',p,'normal-run50000');post=parsed(b.send('STATUS'));results['run_quarantine']={'command':rr,'before':pre,'after':post,'G_delta':post['TicksGame']-pre['TicksGame'],'L_delta':post['TicksSim']-pre['TicksSim']}
    q.send('FRAME_RESET');sender=Bridge(29605);statusclient=Bridge(29605)
    response=sender.send('STEP_TICKS 50000 999999');samples=[]
    for i in range(45):
        start=time.monotonic();status=statusclient.send('STATUS');ms=(time.monotonic()-start)*1000;samples.append({'ms':ms,'status':status,**parsed(status)});time.sleep(.025)
    cancel=sender.send('CANCEL_SIMULATION');settled=parsed(statusclient.send('STATUS'));time.sleep(.3);later=parsed(statusclient.send('STATUS'));f=frames(q,p,'oversized-step-frames')
    lat=sorted(x['ms'] for x in samples);results['parallel_status_slice_cancel']={'step_response':response,'separate_status_connection':True,'all_samples_active':all(x['RemainingStep']>0 for x in samples),'samples':samples,'avg_ms':sum(lat)/len(lat),'max_ms':max(lat),'p95_ms':lat[int(.95*(len(lat)-1))],'max_actual_ticks_per_frame':max(x['calls'] for x in f),'cancel':cancel,'settled':settled,'later':later,'cancellation_stable':settled['TicksSim']==later['TicksSim']}
    sender.close();statusclient.close();write_json(ROOT/'control-results.json',results);print('parallel', {k:v for k,v in results['parallel_status_slice_cancel'].items() if k not in ['samples','step_response']},flush=True)
    results['start_after_long_load']=debt_case(b,q,p,'debt-after-load',lambda:load(b,p))
    results['start_after_export']=debt_case(b,q,p,'debt-after-export',lambda:command(b,'EXPORT_SAVE BeforeDebt',p,'debt-export'))
    results['start_after_idle']=debt_case(b,q,p,'debt-after-idle',lambda:time.sleep(3.0))
    results['pause_resume']=debt_case(b,q,p,'debt-pause-resume',lambda:time.sleep(1.0))
    results['cancel_restart']=debt_case(b,q,p,'debt-cancel-restart',lambda:(b.send('CANCEL_SIMULATION'),time.sleep(1.0)))
    write_json(ROOT/'control-results.json',results)
    # A blocked main thread creates a real simultaneous network queue flood.
    # Raising ThreadPool minimum only changes QA environment, not candidate code.
    results['threadpool_qa_setup']=command(q,'THREADS 256',p,'threadpool-min')
    marker=p/'observer-block-entered.txt';blockresult={};blockclient=Bridge(31605,90)
    def block():
        try:blockresult['response']=blockclient.send('BLOCKQUEUE 33000')
        except Exception as e:blockresult['error']=repr(e)
    blocker=threading.Thread(target=block);blocker.start()
    start=time.monotonic()
    while not marker.exists():
        if time.monotonic()-start>5:raise RuntimeError('Block injection not entered')
        time.sleep(.01)
    pre_flood=parsed(b.send('STATUS')) if False else results['cancel_restart']['after_idle']
    clients=[Bridge(29605,45) for _ in range(180)]
    barrier=threading.Barrier(180);flood=[]
    def hit(i):
        barrier.wait();t=time.monotonic()
        try:return {'i':i,'response':clients[i].send('STEP_TICKS 7 1'),'ms':(time.monotonic()-t)*1000}
        except Exception as e:return {'i':i,'error':repr(e),'ms':(time.monotonic()-t)*1000}
    with ThreadPoolExecutor(max_workers=180) as pool:flood=list(pool.map(hit,range(180)))
    blocker.join(timeout=50);blockclient.close()
    for c in clients:c.close()
    time.sleep(.7);after=parsed(b.send('STATUS'));time.sleep(1);late=parsed(b.send('STATUS'))
    depth=[int(line.split(',')[1]) for line in (p/'observer-queue-depth.csv').read_text().splitlines()]
    results['queue_flood_timeout_no_late_execution']={'connections':180,'block_ms':33000,'before':pre_flood,'after':after,'late':late,'peak_queue_depth':max(depth),'capacity_rejections':sum('capacity exceeded' in x.get('response','') for x in flood),'socket_wait_timeouts':sum('Timeout waiting' in x.get('response','') for x in flood),'worker_expired_rejections':sum('timed out in worker queue' in x.get('response','') for x in flood),'successful_steps':sum(x.get('response','').startswith('OK:') for x in flood),'network_errors':sum('error' in x for x in flood),'block_result':blockresult,'responses':flood,'G_delta':after['TicksGame']-pre_flood['TicksGame'],'L_delta':after['TicksSim']-pre_flood['TicksSim'],'stable_after_resume':after['TicksSim']==late['TicksSim']}
    write_json(ROOT/'control-results.json',results);print('queue',{k:v for k,v in results['queue_flood_timeout_no_late_execution'].items() if k!='responses'},flush=True)
    # Queue-expiry happens before the 30s network wait, without relying on socket timeout.
    marker.unlink();blockresult={};blockclient=Bridge(31605,90);blocker=threading.Thread(target=lambda:blockresult.update(response=blockclient.send('BLOCKQUEUE 12000')));blocker.start()
    while not marker.exists():time.sleep(.01)
    expired=Bridge(29605,45);response=expired.send('STEP_TICKS 77 1');blocker.join();expired.close();blockclient.close();current=parsed(b.send('STATUS'))
    results['explicit_queue_expiry']={'response':response,'status':current,'G_delta':current['TicksGame']-late['TicksGame'],'L_delta':current['TicksSim']-late['TicksSim']}
    write_json(ROOT/'control-results.json',results)
    command(q,'EVENTS',p,'final-lifecycle-events');q.close();stop(proc,b,p)
finally:cleanup()
