from harness import *
def observation(name):
 r=send(31701,'SNAP');write(name+'.json',r);return ET.fromstring(r['response'])
def pawn(snapshot,pawn_id='Human302'):
 return next(x for x in snapshot['Pawns'] if x['PawnId']==pawn_id)
results={}
initial=rpc(cmd('GET_SNAPSHOT'));write('initial-snapshot.json',initial)
results['own_draft']=rpc(cmd('DRAFT',TargetPawnId='Human302'))
results['own_move']=rpc(cmd('MOVE',TargetPawnId='Human302',TargetCellX=140,TargetCellZ=150,TicksToSimulate=120))
results['native_client_after_move']=observation('client-after-move').attrib
results['foreign_reject']=rpc(cmd('DRAFT',TargetPawnId='Human305'))
results['ai_reject']=rpc(cmd('DRAFT',TargetPawnId='Mech_CentipedeBlaster3265'))
before=worker(cmd('GET_SNAPSHOT'))['parsed']['Snapshot'];local=send(31701,'LOCAL_TICKS 10');write('client-local-ticks.json',local)
after=worker(cmd('GET_SNAPSHOT'))['parsed']['Snapshot']
results['local_ticks_independence']={'worker_G_before':before['AuthoritativeTick'],'worker_G_after':after['AuthoritativeTick'],'worker_pawns_equal':before['Pawns']==after['Pawns']}
snapshot=rpc(cmd('GET_SNAPSHOT'))['parsed'];mirrored=observation('mirror-corrected-after-local-ticks')
# QA fault injection passes a deliberately altered snapshot to the existing reconciler.
# It adds no GUI interceptor and does not change candidate source.
import copy
bad=copy.deepcopy(snapshot);p=pawn(bad['Snapshot']);p['PosX']=99;p['PosZ']=99
fault=send(31701,'RECONCILE '+base64.b64encode(json.dumps(bad).encode()).decode());write('mirror-fault-injected.json',fault)
correct=rpc(cmd('GET_SNAPSHOT'));live=observation('mirror-corrected');live_pawn=live.find("pawn[@id='Human302']")
results['position_correction']={'authoritative':pawn(correct['parsed']['Snapshot']),'live':live_pawn.attrib,'grid_refs':live.find("grid[@pawn='Human302']").attrib,'duplicate_spawned_ids':live.get('duplicateSpawnedThingIds')}
results['set_generation']=worker(cmd('SET_GENERATION',Generation=2))
results['stale_generation']=rpc(cmd('DRAFT',TargetPawnId='Human302',Generation=1))
results['current_generation']=rpc(cmd('DRAFT',TargetPawnId='Human302',Generation=2))
# Retained snapshot handling is a unit boundary check, not an actual packet reorder experiment.
old=send(31701,'RECONCILE '+base64.b64encode(json.dumps(snapshot).encode()).decode());write('stale-snapshot-reconcile.json',old)
results['old_snapshot_reconcile']=ET.fromstring(old['response']).find("pawn[@id='Human302']").attrib
results['latest_reconcile']=rpc(cmd('GET_SNAPSHOT',Generation=2))
bench=[]
for i in range(10):
 r=rpc(cmd('GET_SNAPSHOT',Generation=2));bench.append({'external_QA_roundtrip_ms':r['roundtrip_ms'],'utf8_response_bytes':r['response_utf8_bytes'],'status':r['parsed']['Status'],'pawns':len(r['parsed']['Snapshot']['Pawns'])})
results['snapshot_benchmark']=bench
results['final_worker']=worker(cmd('GET_SNAPSHOT',Generation=2))
results['final_client']=observation('client-final').attrib
write('core-results.json',results)
print(json.dumps({'own':results['own_draft']['parsed']['Status'],'move':results['own_move']['parsed']['Status'],'foreign':results['foreign_reject']['parsed']['Status'],'ai':results['ai_reject']['parsed']['Status'],'stale':results['stale_generation']['parsed']['Status'],'current':results['current_generation']['parsed']['Status'],'independent':results['local_ticks_independence'],'correction_grid':results['position_correction']['grid_refs'],'benchmark':bench},indent=2))
