"""Record already observed single native UI delivery; never sends or runs a candidate."""
from pathlib import Path
import sys, tomllib
sys.path.insert(0, str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m

def main():
    c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json')
    b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json'); t=b['tasks'][-1]
    assert t['wp_revision']=='GATE05-R36-PUBLISHER-CONTRACT' and t['submission_attempts']==1
    ui=m.C/'MASTER_R36_ACTUAL_UI_SENT_20261013.json'; u=m.read(ui)
    assert u['submit_count']==1 and u['exact_message']==t['exact_message']
    assert any('Cancel (Ctrl+D)' in x for x in u['lines']) and any('Working' in x for x in u['lines'])
    assert any('Message input' in x and 'Value:' not in x for x in u['lines'])
    ap=Path(r'C:\Users\user\.codex\automations\wareconomy-master\automation.toml')
    av=tomllib.loads(ap.read_text(encoding='utf-8-sig'))
    assert av['status']=='ACTIVE' and av['rrule']=='FREQ=HOURLY;INTERVAL=1'
    assert av['target_thread_id']==c['master_thread_id'] and len(av['prompt'])==173
    proof=m.C/'MASTER_R36_PUBLISHER_CONTRACT_DISPATCH_HOURLY_ACTIVE_VERIFICATION_20261013.json'
    data=dict(at=m.now(),dispatch_id=t['dispatch_id'],wp_revision=t['wp_revision'],envelope=39,
      actual_UI=m.row(ui),draft=m.row(m.C/'MASTER_R36_EXACT_UI_DRAFT_20261013.json'),
      delivery_status='SENT',actual_UI_working=True,submit_count=1,ACK='PENDING',
      guard_session=56970,actual_protected19301_checker_exit0_this_invocation=True,
      automation_file=m.row(ap),actual_configuration=av,future_R36_scheduled_run_observed=False,
      passive_env_lookup_failure='CODEX_HOME absent; first read failed before mutation; actual known user .codex config verified',
      native_E2='NOT_RELEASED',Foundation='HOLD',SRS_target='1.6',Waylith_migration='NOT_ADOPTED')
    m.create(proof,data)
    t.update(status='IN_PROGRESS',delivery_status='SENT',unknown_delivery=False,sent_at=u['observed_at'],
      actual_UI_working_verified=True,delivery_proof=str(proof),ACK_verified=False)
    b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
    c.update(a_current_dispatch_id=t['dispatch_id'],a_current_attempt=t['wp_revision'],a_current_wp=t['wp_id'],
      a_status='IN_PROGRESS_ACK_PENDING',a_prepared_dispatch_id=None,a_pending_dispatch_id=None,
      a_current_completion_path=t['completion_path'],a_latest_delivery=dict(data,proof=m.row(proof)),
      active_operation=None,updated_at=m.now())
    monitor=c['master_monitor_automation']
    monitor.update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,
      configuration_proof=str(proof),configuration_checked_at=m.now(),resumed_by='Master after actual R36 single UI SENT',
      pause_reason=None,no_resume_in_this_review=False,future_run_after_r36_resume_observed=False)
    m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
    ds=m.read(m.H/'DISPATCHER_STATE.json')
    ds['endpoints']['a'].update(current_wp=t['wp_id'],current_dispatch_id=t['dispatch_id'],
      current_status='IN_PROGRESS_ACK_PENDING',last_verified_state='Working',delivery_status='SENT',
      actual_delivery_proof=str(proof),last_verified_at=m.now(),unknown_delivery=False)
    ds['updated_at']=m.now();m.save(m.H/'DISPATCHER_STATE.json',ds)
    m.event(dict(at=m.now(),event='A_R36_ACTUAL_SINGLE_CU_SENT_HOURLY_ACTIVE',dispatch_id=t['dispatch_id'],proof=m.row(proof)))
    m.append_delta('LOCAL-A-R36-PUBLISHER-CONTRACT-SENT-HOURLY-ACTIVE',
      t['dispatch_id']+'/envelope39 actual fresh idle/exact draft/one Send/new exact user message/cleared composer/Working Cancel verified. SENT/IN_PROGRESS/ACK pending/no resend. Only publisher9CAE22371 source+AST mutable, all9Engine/generated fixed; actual protected19301 checker exit0. Controlling nonblank policy correction adopted; no 1.7 target migration. Same wareconomy-master actual ACTIVE60min/173char/correct Master target; future R36 scheduled run unobserved. Original Sol R35 independent static disposed/completed idle42 waits fresh frozen R36; no duplicate WP. Current monitor uses python Dispatcher/Tools/master_check_r36_publisher_contract_status_20261013.py under actual renewed guard, not legacy live-publisher pointer checker. High4/Engine002006/Pipeline007-currentSchema/GQ1 OPEN/native fullE2 NOT_RELEASED/Foundation HOLD/installed incident actorUNKNOWN OPEN. Proof '+str(proof))
    print('R36 actual SENT / hourly ACTIVE recorded; ACK pending')

if __name__=='__main__': main()
