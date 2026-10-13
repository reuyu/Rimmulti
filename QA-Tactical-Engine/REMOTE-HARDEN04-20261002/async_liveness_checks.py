from harness import *
from periodic_fault_checks import FaultProxy
import threading,queue,copy,concurrent.futures
class P(FaultProxy):
 def __init__(self):
  self.gui=threading.Event(); self.gui_received=threading.Event(); self.gui_done=threading.Event();self.gui_record=None;super().__init__()
 def handle(self,c):
  try:
   with c,socket.create_connection(('127.0.0.1',29900),10) as w:
    cr=c.makefile('rb');wr=w.makefile('rb')
    while line:=cr.readline():
     req=json.loads(line);w.sendall(line);raw=wr.readline();resp=json.loads(raw);case=None
     if req['CommandType']=='GET_SNAPSHOT':
      try:case=self.pending.get_nowait()
      except queue.Empty:pass
     elif req['CommandType']=='DRAFT' and self.gui.is_set():
      self.gui.clear();self.gui_received.set();case=dict(kind='gui_delay',seconds=2.0,done=self.gui_done)
     start=time.time()
     if case:
      if case['kind']=='close':c.shutdown(socket.SHUT_RDWR);case['done'].set();return
      time.sleep(case.get('seconds',0))
     rec=dict(utc=time.time(),received=start,command=req,kind=case['kind'] if case else 'normal',response=resp,bytes=len(raw.rstrip(b'\r\n')),delivery='attempt')
     try:c.sendall(raw);rec['delivery']='sent'
     except OSError as e:rec['delivery']=str(e)
     self.records.append(rec)
     if case:
      case['done'].set()
      if case['kind']=='gui_delay':self.gui_record=rec
  except (OSError,ValueError):pass
p=P();results={}
send(29901,'SET_REPLICATION 0');send(31801,'DISCONNECT');send(29901,'CONNECT_WORKER 127.0.0.1:29902');send(29901,'SET_REPLICATION 1');time.sleep(1)
results['baseline']=dict(metrics=send(31801,'METRICS'),native=send(31801,'SNAP'))
send(29901,'RESET_FRAME_METRICS');case=p.arm('delay',seconds=2);time.sleep(.1)
results['delayed_control']=[send(29901,'PING',5) for _ in range(4)];assert case['done'].wait(5);time.sleep(.2);results['after_2s']=dict(status=send(29901,'STATUS'),metrics=send(31801,'METRICS'))
case=p.arm('close');assert case['done'].wait(5);time.sleep(.06);results['close_status']=send(29901,'STATUS');time.sleep(1);results['close_recovery']=send(29901,'STATUS')
# Above deadline: retain real old Worker response, send it after client has timed out.
case=p.arm('delay',seconds=4.5);time.sleep(3.8);results['timeout_status']=send(29901,'STATUS');assert case['done'].wait(3);time.sleep(.8);results['after_late']=dict(status=send(29901,'STATUS'),metrics=send(31801,'METRICS'))
# Disconnect while a real Worker response is held; old reply must not apply.
case=p.arm('delay',seconds=2);time.sleep(.4);results['disconnect_before']=send(31801,'DISCONNECT');assert case['done'].wait(4);time.sleep(.3);results['disconnect_after']=send(31801,'SNAP')
send(29901,'CONNECT_WORKER 127.0.0.1:29902');time.sleep(.5);results['reconnect_status']=send(29901,'STATUS');results['reconnect_snapshot']=send(31801,'SNAP')
write('async-periodic-fault-results.json',results);write('async-proxy-wire.json',p.records);print('ASYNC FAULT CHECKS COMPLETE',flush=True)
send(29901,'RESET_FRAME_METRICS');p.gui.set();print('GUI DRAFT DELAY ARMED',flush=True)
if p.gui_received.wait(150):
 assert p.gui_done.wait(8);time.sleep(.4);results['delayed_gui']=dict(record=p.gui_record,status=send(29901,'STATUS'),native=send(31801,'DUMP'));write('async-periodic-fault-results.json',results);write('async-proxy-wire.json',p.records);print('GUI delay status:',results['delayed_gui']['status']['response'],flush=True)
else:print('GUI not received within window',flush=True)
send(29901,'SET_REPLICATION 0');send(31801,'DISCONNECT');send(29901,'CONNECT_WORKER 127.0.0.1:29900');send(29901,'SET_REPLICATION 1');p.stop()
