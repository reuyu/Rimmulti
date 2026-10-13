"""Verify and collect Sol preparation only; no candidate execution or dispatch."""
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
H = ROOT / 'docs/WarEconomy_Master_Handoff_20261006'
Q = ROOT / 'QA-Tactical-Engine/GATE05-R3-QA-PREP-S1-20261008'
RESULT = 'SOL-GATE05-R3-QA-PREP-S1-20261008-12a1013654024c9a942c63826f8a5b0d'
DELIVERY = 'SOL-GATE05-R3-QA-PREP-S1-20261008-01'

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()

def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    receipts_path = ROOT / 'Dispatcher/MASTER_RECEIPTS.json'
    receipts = read(receipts_path)
    prior = [x for x in receipts['processed_results'] if x.get('result_id') == RESULT]
    if prior:
        assert prior[0]['completion_sha256'] == sha(Q/'COMPLETION.json'), 'Result integrity conflict'
        print('ALREADY_REVIEWED')
        return
    state_path = ROOT / 'Dispatcher/MASTER_COMMUNICATION_STATE.json'
    state = read(state_path)
    assert state['active_operation'] is None and state['sol_current_attempt_id'] == DELIVERY
    c, idx, m = [read(Q/n) for n in ['COMPLETION.json', 'RESULT_INDEX.json', 'EVIDENCE_MANIFEST.json']]
    assert sha(Q/'COMPLETION.json') == '2595BB17C1017F8E691BB2EE7598E4512D927E9BC81F3174B4F90294812C3266'
    assert c['result_id'] == idx['result_id'] == m['result_id'] == RESULT
    assert (c['delivery_id'], c['wp_id'], c['wp_revision'], c['report_kind'], c['status']) == (DELIVERY, 'WP_QA_ENGINE_GATE05_R3_PREPARATION', 'S1', 'QA_PREPARATION', 'COMPLETED')
    assert c['runtime_e2_released'] is False
    for key in ['report', 'evidence_manifest', 'result_index']:
        assert sha(c[key+'_path']) == c[key+'_sha256']
    assert sha(c['initial_ack_path']) == c['initial_ack_sha256'] == state['sol_current_ack']['ack_sha256']
    assert sha(Q/'ACK_COMPLETION_BINDING.json') == c['ack_binding_sha256']
    for item in c['artifacts']:
        assert sha(item['path']) == item['sha256'], item['path']
    assert len(m['files']) == 17
    for item in m['files']:
        assert sha(item['path']) == item['sha256'] and Path(item['path']).stat().st_size == item['bytes'], item['path']
    before, after = read(Q/'PRESERVATION_BEFORE.json'), read(Q/'PRESERVATION_AFTER.json')
    counts = {}
    for group in ['r2_frozen107', 'old_archive19', 'r1_frozen147', 'pipeline206']:
        assert before[group] == after[group], group
        for item in after[group]:
            assert sha(item['path']) == item['sha256'] and Path(item['path']).stat().st_size == item['bytes'], item['path']
        counts[group] = len(after[group])
    assert before['qa_inventories'] == after['qa_inventories']
    qa_counts = []
    for inv in after['qa_inventories']:
        assert sha(inv['manifest']) == inv['manifest_sha256']
        for item in inv['files']:
            assert sha(item['path']) == item['sha256'] and Path(item['path']).stat().st_size == item['bytes'], item['path']
        qa_counts.append(len(inv['files']))
    assert qa_counts == [324, 297, 312, 238]
    lineage = read(Q/'R2_LINEAGE.json')
    for candidate in lineage['candidates']:
        assert sha(candidate['dll']) == candidate['dll_sha256']
        assert len(candidate['documents']) == 4 and candidate['guid'] == candidate['codeview_guid']
        for document in candidate['documents']:
            assert sha(document['frozen_source_path']) == document['pdb_hash'] == document['actual_sha256']
    now = datetime.now().astimezone().isoformat()
    proof_path = H/'coordination/MASTER_SOL_R3_PREP_S1_COMPLETION_VERIFICATION_20261008.json'
    review_path = H/'MASTER_REVIEW_ENGINE_GATE05_R3_QA_PREPARATION_S1_20261008.md'
    proof = {
        'at': now, 'result_id': RESULT, 'delivery_id': DELIVERY,
        'completion_path': str(Q/'COMPLETION.json'), 'completion_sha256': sha(Q/'COMPLETION.json'),
        'report_path': c['report_path'], 'report_sha256': c['report_sha256'],
        'result_index_sha256': c['result_index_sha256'], 'evidence_manifest_sha256': c['evidence_manifest_sha256'],
        'evidence_files_verified': 17, 'completion_artifacts_verified': len(c['artifacts']),
        'preservation_counts_verified': counts, 'qa_preservation_counts_verified': qa_counts,
        'pdb_frozen_source_checksums_verified': [4, 4],
        'lineage_scope': 'DLL/frozen-source bytes matched; reported PDB GUID/MVID agrees with previous independent Master R2 metadata inspection; PE parser not rerun in this collection',
        'actual_thread': {'thread_id': state['sol_thread_id'], 'host_id': 'local', 'status': 'idle', 'turn_id': '01a119a8-fa39-7762-9056-0ab6e37ac537', 'turn_status': 'completed', 'cursor': '2745552a-f142-41a1-8eaf-3fe7b2d500ca:22', 'final_message_id': 'msg_0c6b28ae575c2341016ac71b45166c87d08f5fff76d89c1d29'},
        'master_verdict': 'ACCEPTED_QA_PREPARATION_NO_RUNTIME_VERDICT',
        'runtime_e2_released': False, 'r3_static_implementation_reviewed': False,
        'candidate_or_game_execution_by_master': False, 'closure_changed': False,
        'scheduler_changed': False, 'foundation': 'HOLD', 'master_review_path': str(review_path),
        'lock_run_id': 'MASTER-SOL-R3-PREP-COMPLETE-20261008-01', 'lock_session_id': 96399,
    }
    write(proof_path, proof)
    review_path.write_text(f'''# Gate05 R3 QA 준비 S1 Master 판정

{now}. {RESULT} / {DELIVERY}.

**ACCEPTED_QA_PREPARATION_NO_RUNTIME_VERDICT**. Sol의 immutable R2 독립 정적 검토, R3 검증 matrix·정상 native 준비안을 채택한다. R2 REVISION_REQUIRED/E2_NOT_RELEASED는 유지한다. R3 implementation은 아직 검토하지 않았고 native E2는 NOT_RELEASED/UNTESTED다.

원본 COMPLETION SHA {proof['completion_sha256']}, report SHA {c['report_sha256']}, manifest SHA {c['evidence_manifest_sha256']}, index SHA {c['result_index_sha256']}를 실제 bytes와 대조했다. 17 evidence files/9 declared artifacts, unchanged original ACK binding, R2 frozen107/archive19/R1 frozen147/Pipeline206/QA324·297·312·238 전후 및 현재 bytes를 확인했다. frozen PDB 문서 checksum 각각4/4와 기존 Master R2 metadata lineage에 결속했다. 기존 Sol actual completed turn/idle/cursor22와 직접 완료 보고가 일치한다. Hash 일치는 실행 gate coverage 증명이 아니다.

## 독립 정정 채택 범위

Sol R2-M01~08을 원문 frozen source/raw 및 accepted MD126~132와 대조했다. operator-origin/fixed admitted executable·config, full supported MD128 context, channel/instance/consume, typed actual loaded content 공백과 native 미관측은 유지된다. 다음 qualification은 accepted correction의 의미를 좁혀 명확히 하며 gate를 약화하지 않는다.

- Public caller의 validation 요청은 MD126 허용이다. 요청 가능 자체가 결함은 아니며 operator-owned issuance/launch 및 admitted identity를 입증해야 한다.
- File channel은 equivalent operator-controlled mechanism일 수 있다. 정당한 result-after-exit lifecycle을 일괄 금지하지 않는다. Owned origin/instance/context/consume/cleanup을 입증해야 한다.
- MD130은 supported authority-relevant content/typed lossless encoding을 요구한다. 모든 Def serialization 또는 모든 sorting 금지를 새 요구로 만들지 않는다. 지원 field/order/null/material coverage와 누락 identity를 명시적으로 처리해야 한다.
- MD129는 relevant control-plane capabilities/state의 철회와 clean reset/re-admission을 요구한다. Query 오류 전역 revoke나 관측되지 않은 stale capability exploit을 주장하지 않는다.
- Archive 보존과 installed old-baseline 동일성을 분리한다. Installed incident actor/cause UNKNOWN/OPEN이며 자동 restore/hash 정상화하지 않는다.
- R2 completion aliases는 같은 task를 식별하지만 standard schema 미충족은 유지한다. 검토 후 freeze를 실행 전 provenance로 소급하지 않는다.

R3 matrix의 16 logical dimensions는 MD128 supported contract의 evidence mapping이다. 역할별 mode와 secret/capability proof는 의미에 맞게 결속해야 하며 공개 receipt에 secret 복사를 새 요구로 만들지 않는다. Normal controls/정적 review를 adverse rejection runtime PASS로 확대하지 않는다.

## 다음 행동

A는 이미 전달한 동일 R3 WP를 계속 처리한다. 중복 WP/새 수정 지시를 보내지 않는다. Sol은 이 준비 WP 완료 상태이며 별도 admitted exact R3 후보와 fresh runtime E2 WP를 기다린다. A terminal의 identity/source/PDB/raw/실제 native provenance를 Master가 검토·freeze한 뒤 Sol의 idle를 다시 확인하고 발행한다. 기존 hourly ACTIVE 예약은 A 결과 수집을 계속하고 A terminal disposition 후 pause한다. 이번 QA 완료는 예약 변경 사유가 아니다.

Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD 및 historical narrow CLOSED 유지. C owner/discardability/PlayerGlobal/physical split 채택 없음. Master/QA Production candidate 실행·재빌드 없음.

Proof: {proof_path}
''', encoding='utf-8')
    record = {**proof, 'type': 'SOL_GATE05_R3_QA_PREPARATION_S1', 'processed_at': now, 'master_review_sha256': sha(review_path), 'proof': str(proof_path), 'proof_sha256': sha(proof_path)}
    receipts['processed_results'].append(record)
    receipts['updated_at'] = now
    write(receipts_path, receipts)
    state.update(sol_status='IDLE_QA_PREPARATION_COMPLETE_MASTER_REVIEWED', sol_latest_result=record, sol_latest_progress_note='R3 preparation accepted; await separate admitted frozen candidate/fresh runtime E2 WP.', last_sol_cursor=proof['actual_thread']['cursor'], updated_at=now)
    write(state_path, state)
    dispatch_path = H/'DISPATCHER_STATE.json'
    dispatch = read(dispatch_path)
    dispatch['endpoints']['sol'].update(last_verified_state='idle', current_status=state['sol_status'], last_result_id=RESULT, last_verdict=proof['master_verdict'], last_observation_at=now)
    for item in dispatch['deliveries']:
        if item.get('delivery_id') == DELIVERY:
            item.update(status='COMPLETED_MASTER_REVIEWED', result_id=RESULT, master_verdict=proof['master_verdict'], completion_sha256=proof['completion_sha256'], master_review_path=str(review_path))
    dispatch['updated_at'] = now
    write(dispatch_path, dispatch)
    paragraph = f'\n\n## LOCAL-SOL-R3-PREPARATION-S1-COMPLETE — {now}\n{RESULT}/{DELIVERY}: original direct report matches actual completed/idle turn/cursor22. Master accepts independent R2 review + R3 matrix/native plan as ACCEPTED_QA_PREPARATION_NO_RUNTIME_VERDICT;17 evidence hashes and archive/R1/R2/Pipeline/QA preservation verified. MD126/129/130 qualifications adopted within existing accepted scope; no gate weakening. R3 implementation NOT_REVIEWED/runtime E2 NOT_RELEASED/UNTESTED, R2 rejected, installed incident OPEN/actor UNKNOWN. A same R3 remains active; Sol awaits admitted exact candidate/separate fresh E2 WP. No new dispatch/scheduler/closure. Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Review: {review_path}; proof: {proof_path}\n'
    for path in [ROOT/'docs/MASTER_GOVERNANCE_CURRENT.md', H/'MASTER_PROJECT_STATE.md', H/'MASTER_DECISION_LOG.md', H/'QA_DEFECT_LEDGER.md', H/'MASTER_AGENT_DISPATCH_BOARD.md', ROOT/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
        with path.open('a', encoding='utf-8') as stream:
            stream.write(paragraph)
    event = {'event_id': RESULT+'-MASTER-REVIEWED', 'at': now, 'type': 'SOL_QA_PREPARATION_COMPLETION_REVIEWED', 'result_id': RESULT, 'delivery_id': DELIVERY, 'verdict': proof['master_verdict'], 'proof': str(proof_path), 'proof_sha256': sha(proof_path), 'closure_changed': False, 'scheduler_changed': False}
    for path in [ROOT/'Dispatcher/MASTER_MONITOR_JOURNAL.jsonl', H/'DISPATCH_JOURNAL.jsonl']:
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=False)+'\n')
    print(json.dumps({'verdict': proof['master_verdict'], 'counts': counts, 'qa_counts': qa_counts, 'review': str(review_path)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
