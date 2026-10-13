from harness import *
print(send(7793,'SET_REPLICATION 1')['response']);time.sleep(.25)
write('receive-race-before.json',send(31801,'LIGHT'))
print(send(31801,'PARSE_HOLD')['response'])
deadline=time.time()+5
while time.time()<deadline:
 r=send(31801,'PARSE_STATUS')
 if 'waiting=True' in r['response']:break
 time.sleep(.03)
else:raise TimeoutError('Parser barrier was not reached')
write('receive-race-parked.json',r)
write('receive-race-disable.json',send(7793,'SET_REPLICATION 0'))
write('receive-race-disconnect.json',send(31801,'DISCONNECT'))
write('receive-race-reconnect.json',send(7793,'CONNECT_WORKER 127.0.0.1:7792'))
write('receive-race-new-epoch.json',send(31801,'LIGHT'))
write('receive-race-release.json',send(31801,'PARSE_RELEASE'));time.sleep(.3)
write('receive-race-after.json',send(31801,'LIGHT'));write('receive-race-dump.json',send(31801,'DUMP'))
print(send(31801,'LIGHT')['response'][:310])
