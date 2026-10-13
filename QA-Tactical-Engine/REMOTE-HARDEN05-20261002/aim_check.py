from harness import *
write('aim-replication-on.json',send(7793,'SET_REPLICATION 1'))
write('aim-worker-draft.json',worker(cmd('DRAFT',TargetPawnId='Human302')))
write('aim-worker-attack.json',worker(cmd('ATTACK',TargetPawnId='Human302',TargetThingId='Human305')))
write('aim-progression.json',control(cmd('SET_PROGRESSION',CustomData='1',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED')))
rows=[]
for i in range(70):
 rows.append(dict(utc=time.time(),wire=worker(cmd('GET_SNAPSHOT')),worker=send(31800,'LIGHT'),client=send(31801,'LIGHT')));time.sleep(.07)
write('aim-progress-samples.json',rows)
write('aim-pause.json',control(cmd('SET_PROGRESSION',CustomData='0',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED')))
write('aim-client-dump.json',send(31801,'DUMP'));write('aim-worker-dump.json',send(31800,'DUMP'))
aim=[r for r in rows if pawn(r['wire']['parsed']['Snapshot'])['PoseSource']=='Aiming']
print('ACTUAL ENGINE BUSY FOCUS SAMPLES',len(aim))
if aim:print(pawn(aim[0]['wire']['parsed']['Snapshot']))
