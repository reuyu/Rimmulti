"""Reconcile the human-confirmed A handoff and already-resumed monitor; no dispatch."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import tomllib

ROOT = Path(__file__).resolve().parents[3]
H = ROOT / 'docs/WarEconomy_Master_Handoff_20261006'
D = ROOT / 'Dispatcher'
ID = 'WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708'
RUN = 'MASTER-USER-A-R2-DELIVERY-20261008-0223'
EVENT_ID = ID + '-USER-DELIVERY-CONFIRMED'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def write(p, data):
    temp = p.with_suffix(p.suffix + '.master-tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(p)

def main():
    if any(json.loads(line).get('event_id') == EVENT_ID for line in (H / 'DISPATCH_JOURNAL.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()):
        print('ALREADY_RECORDED')
        return
    board = read(D / 'MASTER_A_TASKS.json')
    task = next(t for t in board['tasks'] if t['dispatch_id'] == ID)
    comm = read(D / 'MASTER_COMMUNICATION_STATE.json')
    state = read(H / 'DISPATCHER_STATE.json')
    assert task['status'] == 'PREPARED_NOT_SENT' and comm['active_operation'] is None
    assert not any(t['status'] in ['SENT', 'ACKNOWLEDGED', 'IN_PROGRESS', 'DELIVERY_UNCERTAIN'] for t in board['tasks'])
    lock = read(D / 'MASTER_MONITOR_LOCK_INFO.json')
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    assert lock['status'] == 'LOCKED' and lock['run_id'] == RUN
    assert (now - datetime.datetime.fromisoformat(lock['locked_at'])).total_seconds() < lock['max_hold_seconds']
    at = now.isoformat()
    for path_key, hash_key in [('instruction_path', 'instruction_sha256'), ('work_package_path', 'work_package_sha256'),
                               ('recovery_prompt_path', 'recovery_prompt_sha256'), ('user_paste_message_path', 'user_paste_message_sha256')]:
        assert sha(Path(task[path_key])) == task[hash_key]
    config_path = Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml')
    config = tomllib.loads(config_path.read_text(encoding='utf-8'))
    assert config['id'] == 'wareconomy-master' and config['kind'] == 'heartbeat'
    assert config['status'] == 'ACTIVE' and config['rrule'] == 'FREQ=MINUTELY;INTERVAL=30'
    assert config['target_thread_id'] == comm['master_thread_id']
    assert config['prompt'].strip() == (D / 'MASTER_MONITOR_TRIGGER.txt').read_text(encoding='utf-8-sig').strip()
    spec = importlib.util.spec_from_file_location('a_check', D / 'master_check_a_result.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    preservation = checker.inspect_preservation(task)
    assert not preservation['preservation_errors'], preservation['preservation_errors']
    ack_path = Path(task['ack_path'])
    ack = None
    ack_errors = []
    if ack_path.exists():
        try:
            ack = read(ack_path)
            ack_errors = [k for k in ['dispatch_id', 'wp_id', 'wp_revision', 'recipient'] if ack.get(k) != task.get(k)]
            if ack.get('schema_version') != 1 or ack.get('status') not in ['ACKNOWLEDGED', 'IN_PROGRESS', 'BLOCKED']:
                ack_errors.append('schema/status')
            if datetime.datetime.fromisoformat(ack.get('acknowledged_at', '')).tzinfo is None:
                ack_errors.append('timezone')
        except (ValueError, TypeError, OSError) as exc:
            ack_errors.append(str(exc))
    ack_verified = ack is not None and not ack_errors
    status = ack['status'] if ack_verified and ack['status'] in ['ACKNOWLEDGED', 'IN_PROGRESS'] else 'SENT'
    task_dir = Path(task['completion_path']).parent
    proof_path = task_dir / 'MASTER_USER_DELIVERY_CONFIRMED.json'
    proof = {
        'event_id': EVENT_ID, 'type': 'A_R2_USER_DELIVERY_AND_MONITOR_ACTIVE_RECONCILED', 'at': at,
        'dispatch_id': ID, 'wp_id': task['wp_id'], 'wp_revision': task['wp_revision'],
        'submission_actor': 'User', 'delivery_evidence_type': 'DIRECT_HUMAN_CONFIRMATION',
        'human_statement': 'A에게 전달했어. 그리고 예약 작업 확인도 다시 시작해놨어',
        'actual_submission_time': None, 'submission_time_observed': False, 'master_ui_submission': False,
        'status': status, 'delivery_status': 'SENT', 'ack_verified': ack_verified,
        'ack_present': ack_path.exists(), 'ack_errors': ack_errors,
        'completion_present': Path(task['completion_path']).exists(),
        'recovery_ack_present': (task_dir / 'A_RECOVERY_ACK.md').exists(),
        'new_a_conversation_ui_identity': 'UNVERIFIED_AFTER_CONTEXT_RESET',
        'monitor_resumed_by': 'User', 'configuration_changed_by_master': False,
        'configuration': config, 'configuration_path': str(config_path), 'configuration_sha256': sha(config_path),
        'prompt_chars': len(config['prompt']), 'future_run_after_this_resume_observed': False,
        'preservation_errors': preservation['preservation_errors'],
        'preservation_counts': {'engine_archive': len(preservation['engine_archive_checks']),
            'pipeline_original_frozen': len(preservation['pipeline_preservation_checks']),
            'rejected_r1_frozen': len(preservation['prior_candidate_checks'])},
        'sol_snapshot': {'cursor': comm['last_sol_cursor'], 'state': 'idle', 'changed': False},
        'new_dispatch': False, 'closure_changed': False, 'foundation': 'HOLD',
    }
    if ack_path.exists():
        proof['ack_sha256'] = sha(ack_path)
    write(proof_path, proof)
    write(task_dir / 'MASTER_USER_DELIVERY_PRESERVATION_CHECK.json', preservation)
    task.update(status=status, delivery_status='SENT', submission_actor='User',
        submission_evidence_type='DIRECT_HUMAN_CONFIRMATION', actual_submission_time=None,
        sent_observed_at=at, submission_proof=str(proof_path), submission_proof_sha256=sha(proof_path),
        recovery_delivery_state='USER_DELIVERY_CONFIRMED_ACK_PENDING' if not ack_verified else 'ACK_VERIFIED',
        a_context_status='RECOVERY_PENDING' if not ack_verified else 'ACK_VERIFIED_RECOVERY_REPORT_SEPARATE',
        execution_observation='AWAIT_ACK' if not ack_verified else 'ACK_VERIFIED', updated_at=at)
    if ack_verified:
        task.update(acknowledged_at=ack['acknowledged_at'], ack_sha256=sha(ack_path))
    board['updated_at'] = at
    comm['a_current_attempt_id'] = ID
    comm['a_status'] = 'SENT_AWAIT_RECOVERY_ACK' if not ack_verified else status
    comm['a_result_completion_path'] = task['completion_path']
    comm['a_next_delivery_override']['status'] = 'SENT_USER_CONFIRMED'
    comm['a_next_delivery_override']['delivery_proof'] = str(proof_path)
    comm['a_last_delivery'] = {'dispatch_id': ID, 'delivery_status': 'SENT', 'status': status,
        'actor': 'User', 'observed_at': at, 'actual_submission_time': None, 'proof': str(proof_path),
        'ack_verified': ack_verified, 'resend_allowed': False}
    monitor = comm['master_monitor_automation']
    monitor.update(status='ACTIVE', desired_status='ACTIVE', configuration_verified=True,
        configuration_checked_at=at, configuration_proof=str(proof_path), resumed_by='User',
        future_run_after_engine_r2_resume_observed=False)
    comm['last_monitor_run'] = {'run_id': RUN, 'checked_at': at, 'a': comm['a_status'],
        'sol': 'idle_unchanged_cursor18', 'new_delivery_by_master': False, 'user_delivery_reconciled': True,
        'closure_changed': False, 'exclusive_lock_session': 16614}
    comm['updated_at'] = at
    state['endpoints']['a'].update(current_wp=task['wp_id'], delivery_evidence_type='DIRECT_HUMAN_CONFIRMATION',
        user_delivery_confirmed_at=at, current_conversation_status='UI_UNVERIFIED_RECOVERY_ACK_PENDING')
    state['a_environment'].update(current_active_wp=task['wp_id'], idle='DO_NOT_DISPATCH_USER_DELIVERY_ACK_PENDING')
    q = next(x for x in state['queued_work'] if x.get('delivery_id') == ID)
    q.update(status=status, delivery_status='SENT', readiness='DO_NOT_DUPLICATE_AWAIT_RECOVERY_ACK',
             user_delivery_confirmed_at=at, delivery_proof=str(proof_path))
    state['deliveries'].append({'delivery_id': ID, 'recipient': 'a', 'work_package': task['wp_id'],
        'revision': task['wp_revision'], 'status': status, 'delivery_status': 'SENT',
        'submission_actor': 'User', 'observed_at': at, 'actual_submission_time': None, 'proof': str(proof_path),
        'runtime_verdict': None, 'ack_verified': ack_verified})
    state['master_monitor_automation'] = monitor.copy()
    state['updated_at'] = at
    for p, data in [(D / 'MASTER_A_TASKS.json', board), (D / 'MASTER_COMMUNICATION_STATE.json', comm), (H / 'DISPATCHER_STATE.json', state)]:
        write(p, data)
    for p in [D / 'MASTER_MONITOR_JOURNAL.jsonl', H / 'DISPATCH_JOURNAL.jsonl']:
        with p.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(proof, ensure_ascii=False) + '\n')
    delta = ('\n\n## LOCAL-A-R2-USER-DELIVERY-ACTIVE — ' + at + '\n'
        'Human directly confirms A recovery/R2 instruction delivery and manual monitor resume. '
        'Same exact R2 dispatch/WP/envelope recorded SENT based on direct human statement; actual submission time '
        'and new A conversation UI identity unobserved. ACK/recovery report pending at this check; no execution/closure claim. '
        'No Master resend/new WP. Actual existing wareconomy-master ACTIVE/30min/173char file-reference prompt/current Master '
        'target verified; no scheduler mutation or duplicate automation by Master. Future scheduled run after this resume '
        'not yet observed. Engine archive19/Pipeline206/rejected R1 frozen147 match. Sol idle/cursor18 unchanged, no QA dispatch. '
        'Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. Proof: ' + str(proof_path) + '\n')
    header = ('Current local delta: A Gate05-R2 SENT by user confirmation; recovery/ACK pending, no duplicate WP. '
              'Existing monitor ACTIVE30min verified after user resume. R1 REVISION_REQUIRED/E2_NOT_RELEASED; Sol idle; '
              'Pipeline full E2 INCONCLUSIVE;007/current schema/Engine002006/G-Q1 OPEN,Foundation HOLD.')
    for name in ['MASTER_PROJECT_STATE.md', 'MASTER_DECISION_LOG.md', 'QA_DEFECT_LEDGER.md', 'MASTER_AGENT_DISPATCH_BOARD.md']:
        p = H / name
        lines = p.read_text(encoding='utf-8-sig').splitlines()
        if len(lines) > 1 and lines[1].startswith('Current local delta:'):
            lines[1] = header
        p.write_text('\n'.join(lines) + '\n' + delta, encoding='utf-8')
    with (ROOT / 'docs/MASTER_GOVERNANCE_CURRENT.md').open('a', encoding='utf-8') as stream:
        stream.write('\nLatest human confirmation: A recovery/R2 instruction SENT by user; recovery/ACK pending. '
                     'Existing wareconomy-master ACTIVE30min/short file prompt/current Master target verified; no resend. '
                     'No Engine E2 release/closure; historical R1 disposition and protected archives retained.\n')
    with (ROOT / 'AGENTS.md').open('a', encoding='utf-8') as stream:
        stream.write('\n## A manual recovery delivery confirmed — 2026-10-08\n'
            'User directly confirms A recovery/R2 instruction delivered and existing monitor resumed. '
            'Master recorded same R2 task SENT via direct human confirmation; ACK/recovery pending, new conversation UI unverified. '
            'Actual existing monitor ACTIVE30min/short file prompt/correct Master endpoint verified. '
            'Do not resend R2 or keep treating it as NOT SENT based on older preparation paragraphs. '
            'No execution/completion/E2/closure is inferred from this delivery. Latest task/journal govern.\n')
    with (D / 'MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md').open('a', encoding='utf-8') as stream:
        stream.write('\n2026-10-08 후속 실제 확인: 사용자가 복구/R2 지시 전달과 예약 재개를 직접 확인했다. '
            '같은 R2 task는 사용자 전달 근거 SENT/ACK pending이며 기존 monitor ACTIVE30min 실제 설정을 확인했다. '
            '앞의 NOT SENT/PAUSED는 역사 준비 상태다. 새 대화 UI identity는 미검증이고 ACK/recovery를 파일로 수집한다. '
            '전달을 반복하지 않는다. 정상 진행/변경 없음이면 조용히 종료하며 terminal evidence 검토 후 pause 계약을 유지한다.\n')
    check = checker.inspect()
    write(task_dir / 'MASTER_AFTER_USER_DELIVERY_CHECK.json', check)
    print(json.dumps({'delivery_status': 'SENT_USER_CONFIRMED', 'task_status': status,
        'ack_verified': ack_verified, 'result_check': check['status'], 'monitor': config['status'],
        'interval_minutes': 30, 'preservation_counts': proof['preservation_counts'], 'proof': str(proof_path)}, ensure_ascii=True))

if __name__ == '__main__':
    main()
