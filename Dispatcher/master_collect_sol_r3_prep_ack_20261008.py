"""Collect the existing Sol preparation ACK; no dispatch, execution or gate change."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HANDOFF = ROOT / 'docs/WarEconomy_Master_Handoff_20261006'
DELIVERY = 'SOL-GATE05-R3-QA-PREP-S1-20261008-01'
EVENT = DELIVERY + '-ACK-COLLECTED'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    receipts_path = ROOT / 'Dispatcher/MASTER_RECEIPTS.json'
    receipts = read(receipts_path)
    if any(x.get('event_id') == EVENT for x in receipts['processed_dispatch_events']):
        print('ACK_ALREADY_COLLECTED')
        return
    state_path = ROOT / 'Dispatcher/MASTER_COMMUNICATION_STATE.json'
    state = read(state_path)
    assert state['active_operation'] is None
    assert state['sol_current_attempt_id'] == DELIVERY
    ack_path = ROOT / 'QA-Tactical-Engine/GATE05-R3-QA-PREP-S1-20261008/ACK.json'
    ack = read(ack_path)
    assert (ack['producer'], ack['delivery_id'], ack['wp_id'], ack['wp_revision']) == ('Sol', DELIVERY, 'WP_QA_ENGINE_GATE05_R3_PREPARATION', 'S1')
    assert ack['status'] == 'ACKNOWLEDGED_IN_PROGRESS'
    assert ack['other_active_wp'] is False and ack['runtime_e2_released'] is False
    wp = HANDOFF / 'WP_QA_ENGINE_GATE05_R3_PREPARATION_S1.md'
    assert digest(wp) == '4F068A272E32925F164B598D94096AADC49BA14A63A427329778D5F86F6F9486'
    manifest_path = ROOT / 'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708/MASTER_GATE05_R2_REJECTED_FREEZE_MANIFEST.json'
    assert digest(manifest_path) == '110A796F5699495998D61503016F8F7C0430B9EC988DD20220D51416AACD421C'
    files = read(manifest_path)['files']
    assert len(files) == 107
    for entry in files:
        frozen = Path(entry['frozen_path'])
        assert frozen.stat().st_size == entry['size'] and digest(frozen) == entry['sha256'].upper(), str(frozen)
    now = datetime.now().astimezone().isoformat()
    proof_path = HANDOFF / 'coordination/MASTER_SOL_R3_PREP_S1_ACK_VERIFICATION_20261008.json'
    proof = {
        'event_id': EVENT, 'at': now, 'delivery_id': DELIVERY,
        'source_thread_id': state['sol_thread_id'], 'result_id': ack['result_id'],
        'ack_path': str(ack_path), 'ack_sha256': digest(ack_path), 'ack': ack,
        'wp_path': str(wp), 'wp_sha256': digest(wp),
        'r2_manifest_path': str(manifest_path), 'r2_manifest_sha256': digest(manifest_path),
        'master_rehashed_frozen_files': 107,
        'direct_reverse_ack_received': True,
        'sol_reported_preservation': 'archive19/R1frozen147/Pipeline206/QA324297312238 and frozen Debug/Release PDB source4/4; not all independently rerun in this ACK collection',
        'actual_wait_snapshot': {'cursor': '2745552a-f142-41a1-8eaf-3fe7b2d500ca:21', 'thread_status': 'active', 'turn_id': '01a119a8-fa39-7762-9056-0ab6e37ac537', 'turn_status': 'inProgress', 'error': None, 'latest_message_id': 'msg_0c6b28ae575c2341016ac715a30aec87d0aeb9d3eabab432f1'},
        'status': 'ACK_VERIFIED_QA_PREPARATION_IN_PROGRESS',
        'runtime_e2_released': False, 'completion_received': False,
        'gate_changed': False, 'closure_changed': False, 'scheduler_changed': False,
        'lock_run_id': 'MASTER-SOL-R3-PREP-ACK-20261008-01', 'lock_session_id': 68710,
    }
    write(proof_path, proof)
    event = {k: proof[k] for k in ['event_id', 'at', 'delivery_id', 'result_id', 'status', 'runtime_e2_released', 'closure_changed', 'scheduler_changed']}
    event.update(type='SOL_QA_PREPARATION_ACK_VERIFIED', proof=str(proof_path), proof_sha256=digest(proof_path), ack_sha256=proof['ack_sha256'])
    state['sol_status'] = proof['status']
    state['sol_latest_progress_note'] = 'S1 ACK verified; immutable R2 independent review and R3 matrix/native planning active; no runtime E2 release or duplicate WP.'
    state['last_sol_cursor'] = proof['actual_wait_snapshot']['cursor']
    state['sol_current_ack'] = event
    state['updated_at'] = now
    write(state_path, state)
    receipts['processed_dispatch_events'].append(event)
    receipts['updated_at'] = now
    write(receipts_path, receipts)
    dispatch_path = HANDOFF / 'DISPATCHER_STATE.json'
    dispatch = read(dispatch_path)
    sol = dispatch['endpoints']['sol']
    sol.update(last_observation_at=now, ack_verified=True, ack_sha256=proof['ack_sha256'], current_result_id=ack['result_id'], current_status=proof['status'], ack_proof=str(proof_path))
    for item in dispatch['deliveries']:
        if item.get('delivery_id') == DELIVERY:
            item.update(ack_verified=True, ack_sha256=proof['ack_sha256'], acknowledged_at=ack['at'], result_id=ack['result_id'])
    dispatch['updated_at'] = now
    write(dispatch_path, dispatch)
    paragraph = f'\n\n## LOCAL-SOL-QA-PREP-S1-ACK — {now}\nOriginal Sol direct ACK matches {DELIVERY}/WP_QA_ENGINE_GATE05_R3_PREPARATION/S1/result {ack["result_id"]}; actual same turn active/inProgress/cursor21. Master independently rehashed R2 frozen107 and WP/manifest identity; Sol additional preservation/PDB checks remain producer-reported in this collection. ACK_VERIFIED_QA_PREPARATION_IN_PROGRESS; no completion/runtime E2/closure/scheduler change or duplicate dispatch. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Proof: {proof_path}\n'
    for path in [ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md', HANDOFF/'MASTER_PROJECT_STATE.md', HANDOFF/'MASTER_DECISION_LOG.md', HANDOFF/'MASTER_AGENT_DISPATCH_BOARD.md', ROOT/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
        with path.open('a', encoding='utf-8') as stream:
            stream.write(paragraph)
    for path in [ROOT/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl', HANDOFF/'DISPATCH_JOURNAL.jsonl']:
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + '\n')
    print(json.dumps({'status': proof['status'], 'frozen_matches': 107, 'proof': str(proof_path)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
