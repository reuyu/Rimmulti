from pathlib import Path
import re
R=Path(__file__).resolve().parents[2];src=R/'Dispatcher/Tools/master_r25_direct_transition_20261011.py';out=R/'Dispatcher/Tools/master_r26_direct_transition_20261011.py';assert not out.exists();s=src.read_text(encoding='utf8')
mapping={'MASTER-R24-RESUME-20261011T121945Z-01':'MASTER-R25-S2-COMPLETE-NEXT-20261011-01','PID=11696;SESSION=37601':'PID=24636;SESSION=35120','dd341868':'4d660e9b','A_R25':'A_R26','R25_MONITOR_RESUME':'R26_MONITOR_RESUME','MASTER_GATE05_R25_ROLE_USERDATA_DISPATCH':'MASTER_GATE05_R26_CHILD_REG_PREP_DISPATCH',"'current_before9'":"'production_fixed_files'",'==28':'==29',"'envelope':28":"'envelope':29",'future_R25_scheduled_run_observed':'future_R26_scheduled_run_observed','M04_PURE_ROLE_SELECTOR_ACTIVE_SAFE_BRANCH_DECLARED_LOG_ONLY_3SPANS4FIXED6OUTPUTS':'M04_READ_ONLY_CHILD_SEPARATE_DECLARATION_PRIVATE_REGISTRATION_CONTRACT_ALL9_FIXED','R25_ROLE_USERDATA':'R26_CHILD_REG_PREPARATION','R25_ACTUAL_SENT':'R26_ACTUAL_SENT','R24_DUAL_DISPOSED_R25':'R25_S2_DISPOSED_R26','MASTER_R24_RESUME_R25_GUARD':'MASTER_R25_S2_COMPLETE_R26_GUARD','future_run_after_r25_resume_observed':'future_run_after_r26_resume_observed','Master after actual R25 direct CU delivery':'Master after actual R26 direct CU delivery',"'Sol':'R24_DISPOSED_IDLE_AWAIT_NEW_R25_FROZEN_TARGETED_QA'":"'Sol':'R25S2_DISPOSED_IDLE_R26_INDEPENDENT_READONLY_PREPARED_NOT_SENT'"}
for a in mapping:assert a in src.read_text(encoding='utf8'),a
for a,b in mapping.items():s=s.replace(a,b)
# Preserve local run identities and replace the completed-R24 historical monitor block.
s=re.sub(r"c\['last_monitor_run'\]\.update\([^;]+\)","c['last_monitor_run']={'run_id':RUN,'guard_session':SESSION,'guard_pid':PID,'at':at,'status':'R25_S2_DISPOSED_R26_SENT_HOURLY_ACTIVE','release_status':'PENDING_ACTUAL_FINALLY'}",s,count=1)
start=s.index(" para=f'");end=s.index("elif stage=='released':",start)
s=s[:start]+""" para=f'\\n\\n## LOCAL-R25-S2-DISPOSED-A-R26-CHILD-REG-PREP-SENT — {at}\\nA{t["dispatch_id"]}/{t["wp_id"]}/envelope29 actualfreshidle/exactdraft/oneSend/newmessage/emptycomposer/WorkingCancel/SENT/ACKpending-or-separatelybound/no resend. R25S2freshnormal36PASS0FAILeach/1824typed24rawbytebounds/QAnewline scopedCLOSED only/S1raw8FAILpreserved/nativeOPEN. R26READ_ONLY separateoperator-ownedREAD_ONLYconfig-original7declaration-receipt privatechild-registration contract/minimumspans/prospectiveoracle ONLY/ALLproduction9fixed/build-execution-assetscopy0. Protected13419/R25frozen99/priorQA preserved;actualsamewareconomy-masterACTIVE60min173charcorrecttarget/futureR26runUNOBSERVED. OriginalSolR25S2completedidle/R26independentprepapprovedNOT_SENTuntildirecttoolproof. FullEnginePipelineGQ1OPEN/FoundationHOLD/nativeE2NOTRELEASED. Proof{p}\\n'
 for q in [R/'AGENTS.md',R/'docs/MASTER_GOVERNANCE_CURRENT.md',H/'MASTER_PROJECT_STATE.md',H/'MASTER_DECISION_LOG.md',H/'QA_DEFECT_LEDGER.md',H/'MASTER_AGENT_DISPATCH_BOARD.md',R/'Dispatcher/MASTER_UNIFIED_MONITOR_INSTRUCTIONS.md']:
  with q.open('a',encoding='utf8') as f:f.write(para)
 print(proof['status'])
"""+s[end:]
# Do not embed actual line breaks inside a generated quoted Python literal.
s=s.replace("para=f'\n\n##","para=f'\\n\\n##").replace("— {at}\nA","— {at}\\nA").replace("Proof{p}\n'","Proof{p}\\n'")
out.write_text(s,encoding='utf8');print(str(out))
