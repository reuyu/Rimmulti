from harness import *
import copy
results={}
def obs(name,cmdline):
 r=send(31801,cmdline);write(name+'.json',r);return r
# A genuine already-coalesced snapshot; only delay candidate Update, do not supply fencing.
obs('coalesced-hold','HOLD_APPLY 1');time.sleep(.4)
before=obs('coalesced-ready','LIGHT');x=ET.fromstring(before['response']);assert x.get('coalesced')=='true'
obs('coalesced-race-arm','COALESCED_RACE');time.sleep(.25)
obs('coalesced-race-result','LIGHT');obs('coalesced-release','HOLD_APPLY 0');time.sleep(.3)
obs('coalesced-after-apply','LIGHT')
# Stress admission and result retention with main-thread apply unavailable.
obs('queue-hold','HOLD_APPLY 1');rows=[]
for i in range(10):
 rows.append(send(31801,'STRESS 100'));time.sleep(.3)
write('queue-stress-batches.json',rows);obs('queue-high-water','LIGHT');obs('queue-release','HOLD_APPLY 0');time.sleep(2);obs('queue-drained','LIGHT')
# Command identity / collision: candidate worker, not GUI evidence.
own0=worker(cmd('GET_SNAPSHOT'));c=cmd('DRAFT',TargetPawnId='Human302')
first=worker(c);retry=worker(c);alter=worker({**c,'CommandType':'MOVE','TargetCellX':150,'TargetCellZ':140})
results['idempotency']=dict(before=own0,first=first,retry=retry,alteredPayload=alter)
results['privilege']=[worker(cmd(k,Source='QA_TEST_CONTROL')) for k in ['LOAD_SAVE','SET_GENERATION','SET_PROGRESSION','SET_ROTATION','SIMULATE_DELAY']]
results['auth']=[worker(cmd('DRAFT',TargetPawnId=p)) for p in ['Human305','Mech_Centipede1969']]
results['generation']=[worker(cmd('GET_SNAPSHOT',Generation=g)) for g in [0,1]]
# Existing snapshot fences direct validation, separately identified as scripted.
base=worker(cmd('GET_SNAPSHOT'))['parsed'];snap=copy.deepcopy(base['Snapshot']);results['fences']=[]
for name,field,value in [('sequence','SnapshotSequence',0),('session','TacticalSessionId','WRONG'),('generation','WorkerGeneration',999),('map','TargetMapId','Map_1'),('unresolved','TargetMapId','Map_9999')]:
 r=copy.deepcopy(base);r['Snapshot'][field]=value
 # Perturb own fields so an accidental accept has an observable effect.
 p=pawn(r['Snapshot']);p['PosX']=99;p['PosZ']=99;p['Drafted']=False;p['Rotation']='North'
 results['fences'].append(dict(name=name,response=send(31801,'VALIDATE '+base64.b64encode(json.dumps(r).encode()).decode())))
# Wrong viewed map must not redirect correctly fenced Map_0 reconciliation.
results['bindingBefore']=send(31801,'SNAP');results['viewMap1']=send(31801,'VIEW_MAP 1');time.sleep(.5);results['bindingAfter']=send(31801,'SNAP');results['restoreView']=send(31801,'VIEW_MAP 0')
results['rotation']=[]
for i in range(4):
 control(cmd('SET_ROTATION',CustomData=str(i),TargetPawnId='Human302',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED'));time.sleep(.3)
 results['rotation'].append(dict(rotation=i,wire=worker(cmd('GET_SNAPSHOT')),client=send(31801,'LIGHT')))
write('regression-checks.json',results);obs('post-checks','DUMP');write('worker-post-checks.json',send(31800,'DUMP'));print('CHECKS COMPLETE',flush=True)
