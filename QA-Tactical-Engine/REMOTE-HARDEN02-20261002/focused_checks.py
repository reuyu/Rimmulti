from harness import *
import copy,re,statistics
results={}
# Application gate faults use intentionally poisoned data in every relevant Pawn field.
fresh=rpc(cmd('GET_SNAPSHOT',Source='QA_FENCING_BASELINE'))
baseline=send(31801,'SNAP');write('fencing-baseline-client.json',baseline)
def own_xml(r):
 return ET.tostring(ET.fromstring(r['response'].split('\t',1)[-1]).find(".//pawn[@id='Human302']"),encoding='unicode')
for kind in ['stale_sequence','wrong_session','wrong_generation','wrong_map']:
 bad=copy.deepcopy(fresh['parsed']);s=bad['Snapshot'];p=pawn(s);p.update(PosX=99,PosZ=99,Drafted=not p['Drafted'],CurJobDef='None',HealthPercent=0,Dead=True,Downed=True,HediffDefs=['Burn'])
 s['SnapshotSequence']+=10000
 if kind=='stale_sequence':s['SnapshotSequence']=fresh['parsed']['Snapshot']['SnapshotSequence']
 elif kind=='wrong_session':s['TacticalSessionId']='WRONG_SESSION'
 elif kind=='wrong_generation':s['WorkerGeneration']=999
 else:s['TargetMapId']='Map_1'
 r=send(31801,'VALIDATE '+base64.b64encode(json.dumps(bad).encode()).decode())
 results[kind]={'response':r['response'].split('\t',1)[0],'own_native_state_unchanged':own_xml(r)==own_xml(baseline)}
 write('fault-'+kind+'.json',r)
# Explicit state perturbation on Worker is QA-only, not a candidate input implementation.
rotations=[]
for direction in range(4):
 send(31800,'ROTATE Human302 '+str(direction))
 r=rpc(cmd('GET_SNAPSHOT',Source='QA_ROTATION_UNIT'))
 native=observation();rotations.append({'worker_native_direction':direction,'wire':pawn(r['parsed']['Snapshot'])['Rotation'],'client_native_direction':int(live_pawn(native).get('rotation'))})
results['rotations']=rotations
# The existing Stab already exists in the fixture. Fresh snapshot cannot restore its severity.
before=observation();stab=live_pawn(before).find("hediff[@def='Stab']");original=float(stab.get('severity'))
write('health-before-native.json',{k:v for k,v in before.items() if k!='xml'})
send(31801,'SEVERITY Human302 Stab '+str(original+1))
rpc(cmd('GET_SNAPSHOT',Source='QA_HEALTH_UNIT'))
after=observation();write('health-after-refresh-native.json',{k:v for k,v in after.items() if k!='xml'})
results['health_existing_severity_correction']={'original':original,'injected':original+1,'after_authoritative_refresh':float(live_pawn(after).find("hediff[@def='Stab']").get('severity'))}
# Restore the deliberately changed QA-local severity; this is not a candidate fix.
send(31801,'SEVERITY Human302 Stab '+str(original))
bench=[]
for i in range(10):
 r=rpc(cmd('GET_SNAPSHOT',Source='QA_SNAPSHOT_METRIC'))
 snap_json=json.dumps(r['parsed']['Snapshot'],ensure_ascii=False,separators=(',',':'))
 bench.append({'external_qa_rtt_ms':r['roundtrip_ms'],'actual_response_utf8_bytes':r['utf8_response_bytes'],'pawns':len(r['parsed']['Snapshot']['Pawns']),'parsed_json_reserialization_snapshot_bytes':len(snap_json.encode())})
results['get_snapshot_loopback']=bench
p=rpc(cmd('PING',Source='QA_PING_METRIC'));write('ping-metric.json',p);results['ping_metric']={'bytes':p['utf8_response_bytes'],'pawns':len(p['parsed']['Snapshot']['Pawns'])}
# Command generation and ownership proof remain narrow fixture tests.
results['ai_reject']=rpc(cmd('MOVE',TargetPawnId='Mech_CentipedeBlaster3265',TargetCellX=140,TargetCellZ=150,Source='QA_UNIT'))['parsed']['Status']
results['stale_command']=rpc(cmd('DRAFT',TargetPawnId='Human302',Generation=999,Source='QA_UNIT'))['parsed']['Status']
results['wrong_command_session']=worker(cmd('GET_SNAPSHOT',TacticalSessionId='UNAUTHORIZED_OTHER_SESSION'))['parsed']['Status']
write('focused-results.json',results)
send(31801,'DUMP')
print(json.dumps(results,indent=2))
