"""Read-only independent initial inventory / bootstrap proof validation."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m
Q=m.R/'QA-Tactical-Engine/GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014'

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');d=c['sol_current_delivery'];ack=m.read(Q/'ACK_INITIAL.json')
 assert c['active_operation'] is None and d['delivery_id']==ack['delivery_id'] and d['wp_id']==ack['wp'] and d['wp_revision']==ack['stage']
 assert (Q/'ACK_INITIAL.json').read_bytes()==(Q/'ACK.json').read_bytes()
 assert m.row(Q/'ACK_INITIAL.json')['sha256']=='038FA117B1B2EEED468A622A98D1E49C861D913C40A6A6ED63DF8F5AE191E4AC'
 for key in ['wp_identity','freeze_manifest','protected_baseline','publisher','initial_inventory']:m.check(ack[key])
 base=m.read(Path(d['baseline_path']));assert len(base['files'])==19380
 for x in base['files']:m.check(x)
 fm=m.read(Path(d['frozen_manifest']));assert len(fm['files'])==43
 for x in fm['files']:m.check(x,'frozen_path')
 inv=m.read(Q/'PRESERVATION_BEFORE.json')
 assert len(inv['protected_files'])==19380
 assert {x['path'].lower():(x['sha256'],x['bytes']) for x in inv['protected_files']}=={x['path'].lower():(x['sha256'],x['bytes']) for x in base['files']}
 pin=m.read(Q/'bootstrap.INPUT.json');tool=m.read(Q/'bootstrap.TOOL.json')
 assert tool['exit_code']==0 and tool['pid']==11432 and pin['at']<tool['start']<tool['end']
 for x in pin['files']+pin['launcher_default_module_observations']:m.check(x)
 for key in ['stdout','stderr','input_manifest']:m.check(tool[key])
 assert tool['stdout']['bytes']==423 and tool['stderr']['bytes']==0
 stdout=json.loads((Q/'bootstrap.STDOUT.txt').read_text(encoding='utf-8-sig'));assert stdout['ACK']['sha256']==m.row(Q/'ACK_INITIAL.json')['sha256']
 raw=m.read(m.C/'MASTER_SOL_R36_STATIC_ACK_ACTIVE_SNAPSHOT_20261014.json');s=json.loads(raw['content'][0]['text'])['polls'][0]
 assert s['latestTurn']['id']==d['actual_new_turn_id'] and s['latestTurn']['status']=='inProgress' and s['revision']==44
 out=m.C/'MASTER_SOL_R36_STATIC_S1_ACK_VERIFICATION_20261014.json'
 m.create(out,dict(at=m.now(),guard_session=21025,delivery_id=d['delivery_id'],result_id=ack['result_id'],ACK=m.row(Q/'ACK_INITIAL.json'),ACK_mirror_equal=True,
  actual_snapshot=s,protected19380_actual_SHA_bytes_matched=True,frozen43_actual_SHA_bytes_matched=True,initial_inventory=m.row(Q/'PRESERVATION_BEFORE.json'),
  bootstrap=dict(tool=m.row(Q/'bootstrap.TOOL.json'),input=m.row(Q/'bootstrap.INPUT.json'),exit_code=0,PID=11432,stdout423_stderr0=True,prospective_input_files=len(pin['files']),default_observations=len(pin['launcher_default_module_observations'])),
  scope='STATIC_TEXT_ONLY_REVIEW_IN_PROGRESS',candidate_publisher_compiler_Engine_fixture_native_adverse_executions=0,native_E2='NOT_RELEASED',Foundation='HOLD',no_new_WP=True))
 print(json.dumps(dict(status='R36_SOL_ACK_AND_INITIAL_EVIDENCE_VERIFIED',proof=m.row(out),result_id=ack['result_id']),ensure_ascii=False))

if __name__=='__main__':main()
