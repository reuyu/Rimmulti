from harness import *
for port in [29900,29901]:
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  try:
   r=send(port,json.dumps(cmd('PING')) if port==29900 else 'PING',2)
   if 'PONG' in r['response']:break
  except OSError:pass
  time.sleep(1)
 else:raise RuntimeError('Listener unavailable '+str(port))
 print('Listener ready',port,flush=True)
write('worker-load.json',worker(cmd('LOAD_SAVE',CustomData='EngineComplexFixture',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',Source='QA_TEST_CONTROL')))
write('client-load.json',send(29901,'LOAD_SAVE EngineComplexFixture'))
for port in [29900,29901]:
 deadline=time.monotonic()+90
 while time.monotonic()<deadline:
  r=send(port,json.dumps(cmd('STATUS')) if port==29900 else 'STATUS',5)
  if 'MAPS=2' in r['response'] or 'Maps=2' in r['response']:break
  time.sleep(1)
 else:raise RuntimeError('Fixture load unavailable')
write('connect.json',send(29901,'CONNECT_WORKER 127.0.0.1:29900'))
write('initial-worker.json',worker(cmd('GET_SNAPSHOT')))
write('initial-client.json',send(31801,'SNAP'))
print('QA PAIR READY',flush=True)

