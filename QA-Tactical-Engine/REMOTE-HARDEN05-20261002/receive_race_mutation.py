from harness import *
send(7793,'SET_REPLICATION 0');write('old-epoch-client-before.json',send(31801,'LIGHT'))
write('old-epoch-worker-draft-on.json',worker(cmd('DRAFT',TargetPawnId='Human302')))
send(31801,'PARSE_HOLD');send(7793,'SET_REPLICATION 1')
deadline=time.time()+5
while time.time()<deadline:
 r=send(31801,'PARSE_STATUS')
 if 'waiting=True' in r['response']:break
 time.sleep(.03)
else:raise TimeoutError('Missing barrier')
write('old-epoch-parked.json',r);send(7793,'SET_REPLICATION 0')
write('old-epoch-disconnect.json',send(31801,'DISCONNECT'));write('old-epoch-reconnect.json',send(7793,'CONNECT_WORKER 127.0.0.1:7792'))
write('old-epoch-worker-draft-off.json',worker(cmd('DRAFT',TargetPawnId='Human302')))
write('old-epoch-new-session-before-release.json',send(31801,'LIGHT'))
send(31801,'PARSE_RELEASE');time.sleep(.3)
write('old-epoch-stale-mutated-client.json',send(31801,'LIGHT'));write('old-epoch-dump.json',send(31801,'DUMP'))
print(send(31801,'LIGHT')['response'][:680])
