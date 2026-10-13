"""Record observed single direct CU delivery and actual hourly configuration."""
from pathlib import Path
import sys,tomllib
sys.path.insert(0,str(Path(__file__).parent))
import master_r29_s1_stop_prepare_s2_20261012 as m

def main():
 c=m.read(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json');b=m.read(m.R/'Dispatcher/MASTER_A_TASKS.json');t=b['tasks'][-1]
 assert t['wp_revision']=='GATE05-R39-PUBLISHER-GENERAL' and t['submission_attempts']==1 and c['active_operation']['dispatch_id']==t['dispatch_id']
 ui=m.C/'MASTER_R39_ACTUAL_UI_SENT_20261014.json';u=m.read(ui);assert u['exact_message']==t['exact_message'] and u['submit_count']==1
 assert any('Message input' in x and 'Value:' not in x for x in u['lines']) and any('Cancel (Ctrl+D)' in x for x in u['lines']) and any('Working' in x for x in u['lines'])
 ap=Path(r'C:\Users\user\.codex\automations\wareconomy-master\automation.toml');av=tomllib.loads(ap.read_text(encoding='utf-8-sig'))
 assert av['status']=='ACTIVE' and av['rrule']=='FREQ=HOURLY;INTERVAL=1' and av['target_thread_id']==c['master_thread_id'] and len(av['prompt'])==173
 p=m.C/'MASTER_R39_PUBLISHER_GENERAL_DISPATCH_HOURLY_ACTIVE_VERIFICATION_20261014.json'
 m.create(p,dict(at=m.now(),guard_session=97827,dispatch_id=t['dispatch_id'],envelope=42,actual_UI=m.row(ui),fresh_idle=m.row(m.C/'MASTER_R39_A_FRESH_IDLE_20261014.json'),draft=m.row(m.C/'MASTER_R39_EXACT_UI_DRAFT_20261014.json'),actual_protected19983_checker_exit0=True,delivery_status='SENT',submit_count=1,ACK='PENDING',automation_file=m.row(ap),actual_configuration=av,automation_tool=m.row(m.C/'MASTER_R39_HOURLY_RESUME_TOOL_20261014.json'),future_R39_scheduled_run_observed=False,native_E2='NOT_RELEASED',Foundation='HOLD'))
 t.update(status='IN_PROGRESS',delivery_status='SENT',unknown_delivery=False,sent_at=u['observed_at'],delivery_proof=str(p),actual_UI_working_verified=True,ACK_verified=False)
 b['updated_at']=m.now();m.save(m.R/'Dispatcher/MASTER_A_TASKS.json',b)
 c.update(a_current_dispatch_id=t['dispatch_id'],a_current_attempt_id=t['dispatch_id'],a_current_attempt=t['wp_revision'],a_current_wp=t['wp_id'],a_status='IN_PROGRESS_ACK_PENDING',a_result_completion_path=t['completion_path'],a_current_completion_path=t['completion_path'],a_latest_ack=None,a_latest_delivery=dict(dispatch_id=t['dispatch_id'],proof=m.row(p),delivery_status='SENT',unknown_delivery=False),a_prepared_dispatch_id=None,a_pending_dispatch_id=None,active_operation=None,updated_at=m.now())
 c['a_latest_runtime_observation']=dict(dispatch_id=t['dispatch_id'],actual_UI=m.row(ui),status='SENT_WORKING_ACK_PENDING')
 c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_checked_at=m.now(),configuration_proof=str(p),actual_config=av,latest_verification=str(p),pause_reason=None,resumed_by='Master after actual R39 single CU SENT',future_run_after_r39_resume_observed=False)
 m.save(m.R/'Dispatcher/MASTER_COMMUNICATION_STATE.json',c)
 ds=m.read(m.H/'DISPATCHER_STATE.json');ds['endpoints']['a'].update(current_wp=t['wp_id'],current_wp_revision=t['wp_revision'],current_dispatch_id=t['dispatch_id'],current_attempt_id=t['dispatch_id'],current_status='IN_PROGRESS_ACK_PENDING',execution_phase='IN_PROGRESS',current_runtime_status='ACTUAL_SINGLE_CU_SENT_WORKING_ACK_PENDING',last_verified_state='Working',last_verified_at=m.now(),ack_verified=False,ack_identity_verified=False,ack_reference_verified=False,ack_sha256=None,last_ack_proof=None,ack_proof=None,latest_ack_verification=None,last_delivery_proof=str(p),latest_submission_proof=str(p),last_ui_proof=str(ui),unknown_delivery=False)
 ds['updated_at']=m.now();m.save(m.H/'DISPATCHER_STATE.json',ds)
 m.event(dict(at=m.now(),event='A_R39_ACTUAL_SINGLE_CU_SENT_HOURLY_ACTIVE',dispatch_id=t['dispatch_id'],proof=m.row(p)))
 m.append_delta('LOCAL-A-R39-PUBLISHER-GENERAL-SENT-HOURLY-ACTIVE',t['dispatch_id']+'/WP_ENGINE_GATE05_R39_PUBLISHER_GENERAL/GATE05-R39-PUBLISHER-GENERAL/envelope42 actualfreshidle/exactdraft/oneSubmit/newexactusermessage/clearedcomposer/WorkingCancel verifiedSENT/IN_PROGRESS/ACKpending/noresend. Actual19983protected+late1/Engine9generated/knowninstalled unchanged checked; onlypublisher940CF77243666 source+ownAST/provenance6 sourceitems authorized/productionEnginebuild-publication-fixture-native-adverse0/currentSRS1.6/noWaylithmigration. Currentmonitor MUSTuse python Dispatcher/Tools/master_check_r39_publisher_general_status_20261014.py underactualrenewedguard plusSolcompact cursor64; legacylivepublisherpointerchecker notapplicable. Samewareconomy-master actualACTIVE60min173charcorrectMastertarget, futureR39rununobserved. OriginalSolR38NORMAL6scopedPASSdisposedcompletedidle64 waitsnewsafe frozen candidate/no duplicateQAprep; actualR38original6SCOPED_RUNTIME_PASSaccepted_notwholeGateE2. High4/Engine002006/Pipeline007schema/GQ1OPEN/FoundationHOLD/fullnativeE2NOTRELEASED/installedactorUNKNOWNOPEN. Proof '+str(p))
 print('R39 actualSENT/Working and same hourly ACTIVE durably recorded')

if __name__=='__main__':main()
