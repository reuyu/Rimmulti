import protocol as q
import threading,json
q.check();threading.Thread(target=q.watch,daemon=True).start()
try:
 h=q.Host('Smoke',1);q.record('profile-runtime',h.cmd('PROFILE_FINGERPRINT'));q.record('internal',h.o.send('INTERNAL'));h.close()
finally:q.STOP.set()
