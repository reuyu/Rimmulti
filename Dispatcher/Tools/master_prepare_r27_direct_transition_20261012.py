from pathlib import Path
import re
p=Path(__file__).with_name('master_r26_direct_transition_20261011.py');s=p.read_text(encoding='utf8')
s=s.replace("RUN='MASTER-R25-S2-COMPLETE-NEXT-20261011-01';PID=24636;SESSION=35120","RUN='MASTER-R26-R27-RECOVERY-20261012-01';PID=20116;SESSION=83680")
s=s.replace('4d660e9b','cdc223f3').replace('MASTER_R26_MONITOR_RESUME_TOOL','MASTER_R27_MONITOR_RESUME_TOOL').replace('MASTER_GATE05_R26_CHILD_REG_PREP_DISPATCH_MONITOR_ACTIVE','MASTER_GATE05_R27_CHILD_CAPTURE_DISPATCH_MONITOR_ACTIVE')
s=s.replace("['production_fixed_files']","['all9_before']")
s=s.replace("==29","==30").replace("'envelope':29","'envelope':30")
s=s.replace('R26','R27').replace('r26','r27')
s=s.replace('MASTER_R25_S2_COMPLETE_R27_GUARD_FINALLY_RELEASE_20261011','MASTER_R26_R27_RECOVERY_GUARD_FINALLY_RELEASE_20261012')
s=s.replace('M04_READ_ONLY_CHILD_SEPARATE_DECLARATION_PRIVATE_REGISTRATION_CONTRACT_ALL9_FIXED','M04_PURE_IMMUTABLE_DATA_ONLY_CAPTURE_ONE_INSERTION_NO_REGISTRATION_LAUNCHER')
s=s.replace("'Sol':'R25S2_DISPOSED_IDLE_R27_INDEPENDENT_READONLY_PREPARED_NOT_SENT'","'Sol':'R26_DISPOSED_IDLE_R27_CAPTURE_QA_READONLY_PREPARATION_NOT_SENT'")
# Replace final append prose, retaining structured actual proof fields.
start=s.index(" para=f'");end=s.index("\n for q in",start)
s=s[:start]+""" para=f'\\n\\n## LOCAL-R26-DISPOSED-A-R27-PURE-CAPTURE-SENT — {at}\\nA{t[\"dispatch_id\"]}/{t[\"wp_id\"]}/envelope30 actualfreshidle/exactdraft/oneSend/newmessage/emptycomposer/WorkingCancel/SENT;identitymatchedACK separately tracked/no resend. SinglePUREimmutableOperatorChildLaunchInputs.Capture/15getters/approved7-task27-originalstrings/data-only NOT_REGISTERED_NOT_ISSUER_AUTHENTICATED;oneinsertion166910/twoexistingfixedsegments/Censuscsprojfixed/6projectoutputs only. Newnormal4pairs-finalE1 thenMasterexactfreeze→freshSolQA;registration-launcher-Process-native0. R26 A10/Sol29 READONLY preparationaccepted/Aunsupportedclaims corrected/oldR25S2scopedPUREPASS andS1rawFAILpreserved. Sameactualwareconomy-masterACTIVE60min173charcorrecttarget/futureR27runUNOBSERVED. OriginalSolR26completedidle/newR27read-onlyQAprepNOT_SENTuntildirectproof. FullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{p}\\n'
""".rstrip()+s[end:]
# Above triple-quoted replacement needs literal escape text inside generated Python.
s=s.replace("para=f'\n\n## LOCAL", "para=f'\\n\\n## LOCAL").replace("— {at}\nA", "— {at}\\nA").replace("Proof{p}\n'", "Proof{p}\\n'")
# Do not copy unrelated old R24 run state into new monitor update.
a=s.index(";c['master_monitor_automation'].update(");z=s.index(";c['last_monitor_run']=",a)
s=s[:a]+""";c['master_monitor_automation'].update(status='ACTIVE',desired_status='ACTIVE',interval_minutes=60,configuration_verified=True,configuration_checked_at=at,configuration_proof=str(p),future_run_after_r27_resume_observed=False,pause_reason=None,resumed_by='Master after actual R27 direct CU delivery')"""+s[z:]
out=p.with_name('master_r27_direct_transition_20261012.py');compile(s,str(out),'exec');assert not out.exists();out.write_text(s,encoding='utf8')
print(out)
