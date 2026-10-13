from harness import *
import harness
ROOT=ROOT/'ManualSession3'
harness.ROOT=ROOT
for kind,port in [('Worker',29800),('GraphicalClient',29801)]:
 deadline=time.monotonic()+150
 while time.monotonic()<deadline:
  try:
   ping=worker(cmd('PING')) if kind=='Worker' else send(port,'PING',3)
   if 'PONG' in ping['response']:break
  except OSError:pass
  time.sleep(.5)
 else:raise RuntimeError('Listener failed: '+kind)
 loaded=worker(cmd('LOAD_SAVE',CustomData='EngineComplexFixture')) if kind=='Worker' else send(port,'LOAD_SAVE EngineComplexFixture')
 write(kind+'/load.json',loaded)
 write(kind+'/ready.json',ready(kind,port,kind=='Worker'))
 print(kind+' loaded isolated map.',flush=True)
write('connect.json',send(29801,'CONNECT_WORKER 127.0.0.1:29800'))
write('before-manual-client.json',send(31701,'SNAP'))
write('before-manual-worker.json',worker(cmd('GET_SNAPSHOT')))
write('ready-for-user.json',{'utc':time.time(),'generation':1})
print('Worker connected. Manual test ready.',flush=True)
