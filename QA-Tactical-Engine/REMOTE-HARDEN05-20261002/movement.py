from harness import *
import sys
name=sys.argv[1];delay=float(sys.argv[2]) if len(sys.argv)>2 else 10
start=time.time()+delay;write('movement-start.json',dict(name=name,start=start));print('RESUME_AT',start,flush=True)
while time.time()<start:time.sleep(.05)
write(name+'-resume.json',control(cmd('SET_PROGRESSION',CustomData='1',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED')))
rows=[]
for i in range(35):
 rows.append(dict(utc=time.time(),worker=send(31800,'LIGHT'),client=send(31801,'LIGHT')));time.sleep(.13)
write(name+'-samples.json',rows)
write(name+'-pause.json',control(cmd('SET_PROGRESSION',CustomData='0',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED')))
print(name,'SAMPLED',len(rows),flush=True)
