from harness import *
import threading
class Proxy:
 def __init__(self):self.fault=None;self.lock=threading.Lock();self.records=[]
 def handle(self,s):
  with s:
   with socket.create_connection(('127.0.0.1',7792)) as w:
    a=s.makefile('r',encoding='utf-8-sig');b=w.makefile('r',encoding='utf-8-sig')
    while True:
     line=a.readline()
     if not line:return
     c=json.loads(line);t=time.time();w.sendall(line.encode());r=b.readline()
     if not r:return
     with self.lock:
      f=self.fault if self.fault and self.fault['kind']==c['CommandType'] else None
      if f:self.fault=None
     rec=dict(utc=t,command=c,response=json.loads(r),fault=f)
     self.records.append(rec);write('proxy-records.json',self.records)
     if f:
      (ROOT/'proxy-active.json').write_text(json.dumps(rec),encoding='utf-8')
      if f.get('close'):return
      time.sleep(f.get('delay',0))
     try:s.sendall(r.encode());rec['forwardedUTC']=time.time()
     except OSError as e:rec['forwardFailure']=str(e);return
 def controls(self,s):
  with s:
   a=s.makefile('r',encoding='utf-8')
   c=json.loads(a.readline())
   with self.lock:self.fault=c
   s.sendall(b'ARMED\n')
 def listen(self,port,fn):
  with socket.socket() as l:
   l.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);l.bind(('127.0.0.1',port));l.listen()
   while True:
    s,_=l.accept();threading.Thread(target=fn,args=(s,),daemon=True).start()
p=Proxy();threading.Thread(target=p.listen,args=(29904,p.controls),daemon=True).start();p.listen(29902,p.handle)
