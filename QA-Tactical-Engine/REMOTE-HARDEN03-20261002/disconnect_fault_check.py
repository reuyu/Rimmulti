from periodic_fault_checks import FaultProxy,native_state
from harness import *

proxy=FaultProxy()
send(29901,'SET_REPLICATION 0');send(31801,'DISCONNECT');send(29901,'CONNECT_WORKER 127.0.0.1:29902');send(29901,'SET_REPLICATION 1');time.sleep(.25)
before=send(29901,'STATUS');case=proxy.arm('close');assert case['done'].wait(5);time.sleep(.4)
after=send(29901,'STATUS');state=native_state()
write('periodic-disconnect-result.json',dict(before=before,after=after,native=state,proxy=proxy.records))
write('after-disconnect-client.json',send(31801,'DUMP'))
send(29901,'SET_REPLICATION 0');send(31801,'DISCONNECT');proxy.stop()
print(after['response'])
