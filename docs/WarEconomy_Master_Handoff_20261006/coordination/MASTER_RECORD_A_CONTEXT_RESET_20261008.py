"""Record the user's manual recovery handoff; never delivers a message or runs a candidate."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import tomllib

ROOT = Path(__file__).resolve().parents[3]
HANDOFF = ROOT / 'docs/WarEconomy_Master_Handoff_20261006'
DISPATCHER = ROOT / 'Dispatcher'
TASK_ID = 'WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708'
TASK_DIR = DISPATCHER / 'A_TASKS' / TASK_ID
PROMPT = HANDOFF / 'A_CONTEXT_RECOVERY_AND_GATE05_R2_20261008.md'
EVENT_ID = TASK_ID + '-USER-MANUAL-RECOVERY-PREPARED'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def write(path, data):
    temporary = path.with_suffix(path.suffix + '.master-tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)

def main():
    journal = HANDOFF / 'DISPATCH_JOURNAL.jsonl'
    if any(json.loads(line).get('event_id') == EVENT_ID for line in journal.read_text(encoding='utf-8-sig').splitlines() if line.strip()):
        print('ALREADY_RECORDED; no duplicate writes')
        return
    board = read(DISPATCHER / 'MASTER_A_TASKS.json')
    task = next(t for t in board['tasks'] if t['dispatch_id'] == TASK_ID)
    comm = read(DISPATCHER / 'MASTER_COMMUNICATION_STATE.json')
    state = read(HANDOFF / 'DISPATCHER_STATE.json')
    assert task['status'] == 'PREPARED_NOT_SENT'
    assert comm['active_operation']['dispatch_id'] == TASK_ID
    assert comm['active_operation']['status'] == 'SUBMISSION_PENDING'
    assert not Path(task['ack_path']).exists()
    assert not Path(task['completion_path']).exists()
    assert sha(Path(task['instruction_path'])) == task['instruction_sha256']
    assert sha(Path(task['work_package_path'])) == task['work_package_sha256']
    lock = read(DISPATCHER / 'MASTER_MONITOR_LOCK_INFO.json')
    assert lock['status'] == 'LOCKED' and lock['run_id'] == 'MASTER-HEARTBEAT-20261008-0158'
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    assert (now - datetime.datetime.fromisoformat(lock['locked_at'])).total_seconds() < lock['max_hold_seconds']
    at = now.isoformat()
    config_path = Path('C:/Users/user/.codex/automations/wareconomy-master/automation.toml')
    config = tomllib.loads(config_path.read_text(encoding='utf-8'))
    assert config['status'] == 'PAUSED'
    assert config['target_thread_id'] == '01a1156b-97ec-7ce0-9e4a-dfc4a3acb174'
    module_spec = importlib.util.spec_from_file_location('a_preservation', DISPATCHER / 'master_check_a_result.py')
    checker = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(checker)
    preservation = checker.inspect_preservation(task)
    assert not preservation['preservation_errors'], preservation['preservation_errors']

    message = (
        '당신은 WarEconomy / RimMulti의 개발 에이전트 A입니다. 한국어로 소통하세요.\n'
        '다음 로컬 지시문을 전체 읽고 그 순서대로 컨텍스트를 복구하세요:\n'
        + str(PROMPT) + '\n'
        '최신 Master 판정·원문 SRS·C 정정·보존 evidence를 먼저 대조하고, '
        '승인된 WP_ENGINE_GATE05_R2 / GATE05-R2만 수행하세요.\n'
        '중복 작업이나 실제 blocker가 없으면 고유 task 폴더에 A_RECOVERY_ACK.md와 ACK.json을 기록하고 R2를 시작하세요. '
        '작업 경과는 A_WORK_LOG.md에 남기고, 완료 증거의 실제 hash를 계산한 뒤 COMPLETION.json을 마지막에 작성하세요.\n'
        '기존 frozen candidate/QA evidence/게임 설치를 보존하고, Master governance·예약을 변경하거나 '
        'E1을 E2/closure로 승격하지 마세요.\n'
    )
    paste_path = TASK_DIR / 'USER_PASTE_MESSAGE.txt'
    assert not paste_path.exists()
    paste_path.write_text(message, encoding='utf-8')
    event = {
        'event_id': EVENT_ID, 'type': 'USER_A_CONTEXT_RESET_MANUAL_RECOVERY_PREPARED', 'at': at,
        'dispatch_id': TASK_ID, 'wp_id': task['wp_id'], 'wp_revision': task['wp_revision'],
        'source': 'Latest human instruction: A context reset; write recovery prompt for human copy/paste',
        'recovery_prompt': str(PROMPT), 'recovery_prompt_sha256': sha(PROMPT),
        'exact_user_paste_message': str(paste_path), 'exact_user_paste_message_sha256': sha(paste_path),
        'previous_pending_ui_operation': comm['active_operation'],
        'pending_ui_disposition': 'ABORTED_BEFORE_INPUT_OR_SUBMISSION',
        'actual_ui_input_performed_for_r2': False, 'actual_ui_submission_performed_for_r2': False,
        'delivery_status': 'NOT_SENT', 'human_paste_observed': False,
        'ack_present': False, 'completion_present': False, 'monitor': 'PAUSED_ACTUAL_CONFIG_VERIFIED',
        'scope_changed': False, 'closure_changed': False,
        'a_endpoint_after_reset': 'UNVERIFIED', 'qa_dispatch': False,
        'preservation_errors': preservation['preservation_errors'],
        'engine_archive_checks': len(preservation['engine_archive_checks']),
        'pipeline_preservation_checks': len(preservation['pipeline_preservation_checks']),
        'prior_candidate_checks': len(preservation['prior_candidate_checks']),
        'configuration_path': str(config_path), 'configuration_sha256': sha(config_path),
        'resume_condition': 'Master observes actual user delivery or matching A recovery/ACK, reconciles task/endpoint/no overlap, then resumes same existing30min monitor',
    }
    proof_path = TASK_DIR / 'MASTER_USER_RECOVERY_PREPARED.json'
    write(proof_path, event)
    write(TASK_DIR / 'MASTER_RECOVERY_PRESERVATION_CHECK.json', preservation)
    task.update(delivery_status='NOT_SENT', delivery_override='USER_MANUAL_PASTE_RECOVERY_THIS_ATTEMPT',
                recovery_prompt_path=str(PROMPT), recovery_prompt_sha256=sha(PROMPT),
                user_paste_message_path=str(paste_path), user_paste_message_sha256=sha(paste_path),
                recovery_delivery_state='AWAIT_USER_DELIVERY', a_context_status='USER_REPORTED_RESET_UNVERIFIED',
                pending_ui_disposition='ABORTED_BEFORE_INPUT_OR_SUBMISSION',
                pending_ui_disposition_proof=str(proof_path), updated_at=at)
    board['updated_at'] = at
    comm['last_aborted_operation'] = event
    comm['active_operation'] = None
    comm['a_current_attempt_id'] = None
    comm['a_status'] = 'AWAIT_USER_CONTEXT_RECOVERY_DELIVERY'
    comm['a_next_delivery_override'] = {'scope': 'THIS_R2_ATTEMPT', 'route': 'USER_COPY_PASTE',
        'dispatch_id': TASK_ID, 'prompt_path': str(PROMPT), 'proof': str(proof_path), 'status': 'NOT_SENT'}
    comm['a_endpoint_context_status'] = 'USER_REPORTED_RESET_CURRENT_CONVERSATION_UNVERIFIED'
    comm['master_monitor_automation']['configuration_checked_at'] = at
    comm['master_monitor_automation']['status'] = 'PAUSED'
    comm['master_monitor_automation']['desired_status'] = 'PAUSED'
    comm['last_monitor_run'] = {'run_id': lock['run_id'], 'automation_id': 'wareconomy-master',
        'heartbeat_at': '2026-10-07T16:58:25.212Z', 'checked_at': at,
        'a': 'R1_REVIEWED_REVISION_REQUIRED_R2_NOT_SENT_USER_RECOVERY_PREPARED',
        'sol': 'idle_no_new_wp', 'new_delivery': False, 'closure_changed': False,
        'exclusive_lock_session': 8733, 'disposition_proof': str(proof_path)}
    comm['updated_at'] = at
    endpoint = state['endpoints']['a']
    endpoint['historical_delivery_verified_before_context_reset'] = endpoint['runtime_delivery_verified']
    endpoint['runtime_delivery_verified'] = False
    endpoint['current_wp'] = None
    endpoint['context_reset_observed_from_user_at'] = at
    endpoint['current_conversation_status'] = 'UNVERIFIED_AFTER_USER_REPORTED_CONTEXT_RESET'
    state['a_environment']['idle'] = 'UNKNOWN_AFTER_CONTEXT_RESET'
    state['a_environment']['context_reset'] = True
    state['routing_policy']['next_a_delivery_override'] = 'USER_COPY_PASTE_RECOVERY_THIS_R2_ATTEMPT'
    state['queued_work'].append({'recipient': 'a', 'work_package': task['wp_id'], 'revision': task['wp_revision'],
        'delivery_id': TASK_ID, 'status': 'PREPARED_NOT_SENT', 'delivery_status': 'NOT_SENT',
        'readiness': 'AWAIT_USER_CONTEXT_RECOVERY_DELIVERY', 'prerequisites_verified': False,
        'work_package_path': task['work_package_path'], 'recovery_prompt_path': str(PROMPT),
        'prepared_message': str(paste_path), 'delivery_override': 'USER_COPY_PASTE_THIS_ATTEMPT'})
    state['master_monitor_automation'] = comm['master_monitor_automation'].copy()
    state['updated_at'] = at
    for path, data in [(DISPATCHER / 'MASTER_A_TASKS.json', board),
                       (DISPATCHER / 'MASTER_COMMUNICATION_STATE.json', comm),
                       (HANDOFF / 'DISPATCHER_STATE.json', state)]:
        write(path, data)
    for path in [journal, DISPATCHER / 'MASTER_MONITOR_JOURNAL.jsonl']:
        with path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + '\n')
    delta = (
        '\n\n## LOCAL-A-CONTEXT-RESET-USER-RECOVERY — ' + at + '\n'
        'Latest user reports A context reset and asks for recovery instructions to paste personally. '
        'Prepared A_CONTEXT_RECOVERY_AND_GATE05_R2_20261008.md and exact USER_PASTE_MESSAGE.txt; '
        'existing R2 scope/revision/dispatch unchanged. Pending Master UI operation aborted before any input/submission. '
        'R2 PREPARED_NOT_SENT/NOT SENT; no ACK/COMPLETION exists. Current A conversation/runtime unverified after reset; '
        'historical submission proof retained. User paste is not presumed. Same existing monitor actual PAUSED; '
        'resume only after actual delivery/matching recovery ACK and Master reconciliation. '
        'Engine archive19/Pipeline206/R1 frozen147 preservation checks match. R1 REVISION_REQUIRED/E2_NOT_RELEASED; '
        'Sol idle/no duplicate QA; Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD. '
        'A recovery/implementation writes only task-owned A_RECOVERY_ACK.md/A_WORK_LOG.md/ACK/terminal evidence, '
        'no Master governance or automation edits. Proof: ' + str(proof_path) + '\n'
    )
    header = ('Current local delta: A user-reported context reset; recovery prompt prepared for USER_COPY_PASTE; '
              'Gate05-R2 approved NOT SENT; pending UI submission aborted before input. Monitor PAUSED. '
              'R1 REVISION_REQUIRED/E2_NOT_RELEASED; Sol idle; Pipeline full E2 INCONCLUSIVE; '
              '007/current schema/Engine002006/G-Q1 OPEN,Foundation HOLD.')
    for name in ['MASTER_PROJECT_STATE.md', 'MASTER_DECISION_LOG.md', 'QA_DEFECT_LEDGER.md', 'MASTER_AGENT_DISPATCH_BOARD.md']:
        path = HANDOFF / name
        content = path.read_text(encoding='utf-8-sig')
        lines = content.splitlines()
        if len(lines) > 1 and lines[1].startswith('Current local delta:'):
            lines[1] = header
        path.write_text('\n'.join(lines) + '\n' + delta, encoding='utf-8')
    with (ROOT / 'docs/MASTER_GOVERNANCE_CURRENT.md').open('a', encoding='utf-8') as stream:
        stream.write('\nLatest user A context reset: [A recovery + Gate05-R2](WarEconomy_Master_Handoff_20261006/A_CONTEXT_RECOVERY_AND_GATE05_R2_20261008.md) '
                     'prepared for human paste; R2 NOT SENT/current A endpoint unverified. Pending UI operation aborted before input; '
                     'monitor PAUSED pending actual delivery/ACK. Same R2 scope/identity and prior gate dispositions retained.\n')
    with (ROOT / 'AGENTS.md').open('a', encoding='utf-8') as stream:
        stream.write('\n## A context reset / manual recovery exception — 2026-10-08\n'
                     'Latest user asks to personally paste the new A recovery instructions. This R2 attempt uses '
                     'docs/WarEconomy_Master_Handoff_20261006/A_CONTEXT_RECOVERY_AND_GATE05_R2_20261008.md and task USER_PASTE_MESSAGE.txt. '
                     'R2 is approved NOT SENT; pending UI operation aborted before any input/submission. '
                     'Do not assume old A conversation/idle proof survives context reset. Master records actual user delivery/ACK '
                     'and reconciles before resuming the same monitor; PAUSED meanwhile. Default future direct Computer Use routing remains. '
                     'R1 REVISION_REQUIRED/E2_NOT_RELEASED/frozen147; existing Engine19/Pipeline103/QA protected; '
                     'Engine002006/Pipeline007/current schema/G-Q1 OPEN,Foundation HOLD.\n')
    print(json.dumps({'status': 'RECOVERY_PROMPT_PREPARED_NOT_SENT', 'prompt': str(PROMPT),
        'prompt_sha256': sha(PROMPT), 'paste_message': str(paste_path), 'proof': str(proof_path),
        'preservation_counts': [event['engine_archive_checks'], event['pipeline_preservation_checks'], event['prior_candidate_checks']],
        'monitor': config['status'], 'scope_changed': False}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
