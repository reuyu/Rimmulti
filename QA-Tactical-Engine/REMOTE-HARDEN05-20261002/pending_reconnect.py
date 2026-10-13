from harness import *
initial=len(json.loads((ROOT/'proxy-records.json').read_text(encoding='utf-8')))
print('WAITING FOR NATIVE DRAFT',flush=True)
deadline=time.time()+120
while time.time()<deadline:
 try:
  data=json.loads((ROOT/'proxy-records.json').read_text(encoding='utf-8'))
  if len(data)>initial and data[-1]['command']['CommandType']=='DRAFT':break
 except (OSError,ValueError):pass
 time.sleep(.03)
else:raise TimeoutError('No native Draft')
write('native-reconnect-trigger.json',dict(utc=time.time(),record=data[-1]))
write('native-reconnect-command.json',send(7793,'CONNECT_WORKER 127.0.0.1:29902'))
time.sleep(4);write('native-reconnect-after.json',send(31801,'LIGHT'));write('native-reconnect-dump.json',send(31801,'DUMP'));print('RECONNECT FAULT COMPLETE',flush=True)
