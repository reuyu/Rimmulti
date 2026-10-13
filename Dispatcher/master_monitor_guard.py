"""Hold a real Windows byte-range lock across one Master monitor invocation.

Start with exec_command (an interactive session is needed), keep the session ID,
and send RELEASE with write_stdin in finally. Exit 75 means another run owns it.
This helper never sends messages, executes QA, or changes governance/outboxes.
"""
from pathlib import Path
import datetime,json,msvcrt,os,sys,threading,time,uuid

root=Path(__file__).resolve().parent
lock=root/'MASTER_MONITOR_RUN.lock'
info=root/'MASTER_MONITOR_LOCK_INFO.json'
run_id=sys.argv[1] if len(sys.argv)>1 else str(uuid.uuid4())
handle=lock.open('a+b')
if lock.stat().st_size==0:
 handle.write(b'0');handle.flush()
handle.seek(0)
try:msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
except OSError:
 print(json.dumps({'status':'LOCK_BUSY','run_id':run_id}),flush=True)
 handle.close();raise SystemExit(75)

def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
record={'status':'LOCKED','run_id':run_id,'pid':os.getpid(),'locked_at':now(),'mechanism':'Windows msvcrt exclusive byte-range lock, byte0','max_hold_seconds':1800}
info.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record),flush=True)
stop=threading.Event()
wake=threading.Event()
lease_mutex=threading.Lock()
lease_deadline=time.monotonic()+1800
def read_input():
 global lease_deadline
 for line in sys.stdin:
  command=line.strip()
  if command=='RELEASE':break
  if command=='RENEW':
   with lease_mutex:
    if stop.is_set() or time.monotonic()>=lease_deadline:
     print(json.dumps({'status':'LEASE_EXPIRED_NO_RENEW','run_id':run_id}),flush=True)
     break
    lease_deadline=time.monotonic()+1800
    record.update(renewed_at=now(),renewal_count=record.get('renewal_count',0)+1)
    info.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'LOCK_RENEWED','run_id':run_id,'pid':os.getpid(),'renewed_at':record['renewed_at'],'max_hold_seconds':1800}),flush=True)
   wake.set()
 stop.set()
 wake.set()
threading.Thread(target=read_input,daemon=True).start()
try:
 while not stop.is_set():
  with lease_mutex:remaining=lease_deadline-time.monotonic()
  if remaining<=0:
   with lease_mutex:
    if time.monotonic()<lease_deadline:continue
    stop.set()
    record['release_reason']='TTL_EXPIRED'
   break
  wake.wait(remaining)
  wake.clear()
 if 'release_reason' not in record:record['release_reason']='RELEASE_OR_STDIN_CLOSED'
finally:
 handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1);handle.close()
 record.update(status='RELEASED',released_at=now())
 info.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(record),flush=True)
