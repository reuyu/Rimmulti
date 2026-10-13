from harness import *
import threading,queue,concurrent.futures,copy

class FaultProxy:
 def __init__(self):
  self.pending=queue.Queue();self.records=[];self.running=True
  self.listener=socket.socket();self.listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);self.listener.bind(('127.0.0.1',29902));self.listener.listen()
  threading.Thread(target=self.accept,daemon=True).start()
 def accept(self):
  while self.running:
   try:c,_=self.listener.accept();threading.Thread(target=self.handle,args=(c,),daemon=True).start()
   except OSError:return
 def handle(self,c):
  try:
   with c, socket.create_connection(('127.0.0.1',29900),10) as w:
    cr=c.makefile('rb');wr=w.makefile('rb')
    while line:=cr.readline():
     request=json.loads(line);w.sendall(line);raw=wr.readline();response=json.loads(raw)
     try:case=self.pending.get_nowait()
     except queue.Empty:case=None
     start=time.time();out=copy.deepcopy(response)
     if case:
      snap=out['Snapshot'];p=pawn(snap)
      if case['kind'] in ['stale','session','generation','map','unresolved']:
       p.update(PosX=99,PosZ=99,Drafted=False,CurJobDef='None',Rotation='North')
       if case['kind']=='stale':snap['SnapshotSequence']=case['sequence']
       elif case['kind']=='session':snap['TacticalSessionId']='WRONG_SESSION'
       elif case['kind']=='generation':snap['WorkerGeneration']=999
       elif case['kind']=='map':snap['TargetMapId']='Map_1'
       else:snap['TargetMapId']='Map_UNRESOLVABLE'
      elif case['kind']=='delay':time.sleep(case['seconds'])
      elif case['kind']=='close':c.shutdown(socket.SHUT_RDWR);case['done'].set();break
     wire=json.dumps(out,separators=(',',':'),ensure_ascii=False).encode()+b'\n' if case else raw
     c.sendall(wire)
     self.records.append(dict(utc=time.time(),received=start,command=request,kind=case['kind'] if case else 'normal',worker_response=response,delivered_response=out,bytes=len(wire)-1))
     if case:case['done'].set()
  except (OSError,ValueError):pass
 def arm(self,kind,**args):
  c=dict(kind=kind,done=threading.Event(),**args);self.pending.put(c);return c
 def stop(self):self.running=False;self.listener.close()

def native_state():
 x=observation()['xml']
 return dict(counters=x.attrib,pawns=[p.attrib for p in x.findall('.//pawn')])

if __name__=='__main__':
 proxy=FaultProxy();results={}
 # Disconnect/reconnect setup changes transport only; periodic work stays candidate Update.
 send(29901,'SET_REPLICATION 0');send(31801,'DISCONNECT');send(29901,'CONNECT_WORKER 127.0.0.1:29902');send(29901,'SET_REPLICATION 1');time.sleep(.3)
 for kind in ['stale','session','generation','map','unresolved']:
  if kind=='unresolved':send(31801,'EXPECT_MAP Map_UNRESOLVABLE')
  before=native_state();case=proxy.arm(kind,sequence=int(before['counters']['lastSequence']))
  assert case['done'].wait(5),kind
  after=native_state()
  results[kind]=dict(before=before,after=after,pawn_state_unchanged=before['pawns']==after['pawns'],rejected_delta=int(after['counters']['rejected'])-int(before['counters']['rejected']))
  if kind=='unresolved':send(31801,'EXPECT_MAP Map_0')
  time.sleep(.2)
 # Inject one actual delayed periodic response and measure control latency plus frame gap.
 delay=proxy.arm('delay',seconds=2.0);time.sleep(.12)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(send,29901,'PING',6) for _ in range(4)]
  results['delayed_periodic_control']=[f.result() for f in futures]
 assert delay['done'].wait(5)
 write('periodic-fault-native-results.json',results);write('periodic-proxy-wire.json',proxy.records)
 write('after-periodic-fault-client.json',send(31801,'DUMP'));write('after-periodic-fault-metrics.json',send(31801,'METRICS'))
 send(29901,'SET_REPLICATION 0');send(31801,'DISCONNECT');send(29901,'CONNECT_WORKER 127.0.0.1:29900');send(29901,'SET_REPLICATION 1')
 proxy.stop()
 print(json.dumps({k:dict(unchanged=v['pawn_state_unchanged'],rejected_delta=v['rejected_delta']) for k,v in results.items() if k!='delayed_periodic_control'}))
 print('Delayed periodic control RTT ms:',[round(x['roundtrip_ms'],2) for x in results['delayed_periodic_control']])
