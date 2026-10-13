from pathlib import Path
import re
R=Path(__file__).resolve().parents[2];src=R/'Dispatcher/Tools/master_collect_sol_r25_complete_20261011.py';out=R/'Dispatcher/Tools/master_collect_sol_r25_s2_complete_20261011.py';assert not out.exists();s=src.read_text(encoding='utf8')
changes={
 'GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011':'GATE05-R25-ROLE_USERDATA-INDEPENDENT-S2-20261011',
 'MASTER_SOL_R25_ROLE_USERDATA_INDEPENDENT_COMPLETION_':'MASTER_SOL_R25_ROLE_USERDATA_S2_COMPLETION_',
 "'wp_revision':'S1'":"'wp_revision':'S2'",
 '30CD695EA556B6AA0D0CB6E2A8F647AD2DE31254ECE603E7755184E492A54505':'421FF53D680B3E6B1C7FD12169626F4C34C8D364F08AB0C8C161986F09544684',
 'MASTER-R25-QA-COMPLETE-20261011-01':'MASTER-R25-S2-COMPLETE-NEXT-20261011-01',
 "'guard_session':71407,'guard_pid':32068":"'guard_session':35120,'guard_pid':24636",
 "summary['actual_run_exits']==[1,1]":"summary['actual_run_exits']==[0,0]",
 "host['numeric_exit']==tool['exit_code']==1":"host['numeric_exit']==tool['exit_code']==0",
 "sum(f['status']=='PASS' for f in res['results'])==32":"sum(f['status']=='PASS' for f in res['results'])==36",
 "sum(f['status']=='FAIL' for f in res['results'])==4 and res['failed_assertions']==4":"sum(f['status']=='FAIL' for f in res['results'])==0 and res['failed_assertions']==0",
 "numeric_exit=1,raw_pass=32,raw_fail=4":"numeric_exit=0,raw_pass=36,raw_fail=0",
 "'raw_os_exits':[1,1],'raw_assertion_verdict':'FAIL_PRESERVED'":"'raw_os_exits':[0,0],'raw_assertion_verdict':'PASS_NEW_S2_S1_FAIL_PRESERVED'",
 "'exits':[1,1],'LF_CRLF_failures':8":"'exits':[0,0],'exact_raw_byte_bindings':24",
 "assert '\\r' not in expected and raw!=expected and raw.replace('\\r\\n','\\n')==expected":"assert '\\r\\n' in expected and raw==expected",
}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
for a,b in [(88,89),(13220,13315),(157,160)]:s=re.sub(r'\b'+str(a)+r'\b',str(b),s)
s=s.replace("diagnostic_only_CRLF_to_LF_equal=True,raw_assertion_status='FAIL_PRESERVED'","raw_assertion_status='PASS_EXACT_NEW_ORACLE'")
s=s.replace("len(bytechecks)==8","len(bytechecks)==24")
start=s.index('  bytechecks.append(');end=s.index('\n processes.append',start)
line=s[start:end]
assert line.count('bytechecks.append(')==1
line=line.replace('case_id=key,','case_id=key,phase=phase,')
s=s[:start]+"  for phase in ['redactedBefore','redactedAfterSource','redactedAfterDetached']:\n   assert obs[phase].encode()==expected.encode()\n "+line+s[end:]
# Exact immutable old runner logic and independent expected-graph formatting correction.
i=s.index('summary=read(')
extra="""oldQ=R/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011'
assert sha(Q/'Program.cs')==sha(oldQ/'Program.cs')=='6614E455D316F046BC9072171B4A39F676148E61395AEF889C2E95974E6A615C'
oldOracle=read(oldQ/'NORMAL_EXPECTED_ORACLE.json');newOracle=read(Q/'NORMAL_EXPECTED_ORACLE.json')
assert list(oldOracle['cases'])==list(newOracle['cases'])
for key,e in oldOracle['cases'].items():
 n=newOracle['cases'][key];assert list(e)==list(n)
 assert ordered({k:v for k,v in e.items() if k!='expected_redacted_utf8_text'},{k:v for k,v in n.items() if k!='expected_redacted_utf8_text'})
 assert n['expected_redacted_utf8_text']==json.dumps(e['expected_redacted'],ensure_ascii=False,indent=2).replace(chr(10),chr(13)+chr(10))
"""
s=s[:i]+extra+s[i:]
s=s.replace("'byte_failure_diagnosis_independently_checked':bytechecks","'exact_raw_byte_bindings_master_checked':bytechecks,'S1_raw_fail_unchanged_protected':True,'S2_only_oracle_formatting_and_sourceclone_checked':True")
s=s.replace("'master_read_limitations':['cp949 console omittedutf8 causedmetadata print failure;rerunreadwithutf8 only','MicrosoftdocsURLs inaccessible;primaryreferencesource read instead']","'master_read_limitations':[]")
out.write_text(s,encoding='utf8');print(str(out))
