from harness import *
import re,statistics
out={}
worker(cmd('SET_PROGRESSION',CustomData='1'));send(31800,'PAUSE 0')
start=time.perf_counter();a=worker(cmd('STATUS'));series=[]
for i in range(12):
 series.append(worker(cmd('STATUS')));time.sleep(.2)
b=worker(cmd('STATUS'));elapsed=time.perf_counter()-start
getg=lambda r:int(re.search(r'TICKS=(\d+)',r['parsed']['Message']).group(1))
out['autonomous']={'seconds':elapsed,'G_before':getg(a),'G_after':getg(b),'observed_tps':(getg(b)-getg(a))/elapsed,'status_rtt_ms':[r['roundtrip_ms'] for r in series]}
send(31800,'PAUSE 1');p1=worker(cmd('STATUS'));time.sleep(1);p2=worker(cmd('STATUS'));out['pause']={'before':getg(p1),'after':getg(p2)}
send(31800,'PAUSE 0');time.sleep(.5);worker(cmd('SET_PROGRESSION',CustomData='0'));p1=worker(cmd('STATUS'));time.sleep(1);p2=worker(cmd('STATUS'));out['disable']={'before':getg(p1),'after':getg(p2)}
send(31800,'DUMP')
rows=[]
for l in (ROOT/'Worker/qa-worker-slices.tsv').read_text().splitlines():
 m=re.search(r'frame=(\d+) ticks=(\d+) elapsedMs=([\d.]+)',l)
 if m:rows.append({'frame':int(m[1]),'ticks':int(m[2]),'elapsed_ms':float(m[3])})
out['update_measurement_before_legacy_step']={'frames':len(rows),'max_ticks':max(r['ticks'] for r in rows),'max_update_elapsed_ms':max(r['elapsed_ms'] for r in rows),'updates_over_8ms':sum(r['elapsed_ms']>8 for r in rows),'measurement_scope':'Whole candidate Worker Update including command dispatch, observer counter overhead; not isolated native tick cost'}
# Six ticks suffice to demonstrate the retained command-path slice bypass; no flood / huge loop.
legacy=worker(cmd('STEP_TICKS',TicksToSimulate=6,Source='QA_LEGACY_BOUNDARY_UNIT'))
out['legacy_step_six']={'status':legacy['parsed']['Status'],'message':legacy['parsed']['Message']}
write('progression-results.json',out)
send(31800,'DUMP')
print(json.dumps(out,indent=2))
