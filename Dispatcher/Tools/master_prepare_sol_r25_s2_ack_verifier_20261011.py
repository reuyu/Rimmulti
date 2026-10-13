from pathlib import Path
import re
root=Path(__file__).resolve().parents[2];src=root/'Dispatcher/Tools/master_verify_sol_r25_ack_20261011.py';out=root/'Dispatcher/Tools/master_verify_sol_r25_s2_ack_20261011.py';assert not out.exists()
s=src.read_text(encoding='utf8')
changes={
 "'MASTER-R25-QA-ACK-20261011-01';PID=29832;SESSION=76616":"'MASTER-R25-QA-S2-ACK-20261011-01';PID=3880;SESSION=19395",
 "MASTER_R25_ACK_GUARD_FINALLY_RELEASE_20261011.json":"MASTER_R25_S2_ACK_GUARD_FINALLY_RELEASE_20261011.json",
 "MASTER_SOL_R25_ROLE_USERDATA_INDEPENDENT_ACK_SNAPSHOT_20261011.json":"MASTER_SOL_R25_ROLE_USERDATA_S2_ACK_SNAPSHOT_20261011.json",
 "MASTER_SOL_R25_ROLE_USERDATA_INDEPENDENT_ACK_VERIFICATION_20261011.json":"MASTER_SOL_R25_ROLE_USERDATA_S2_ACK_VERIFICATION_20261011.json",
 "ack['wp_revision']=='S1'":"ack['wp_revision']=='S2'",
 "'wp_revision':'S1'":"'wp_revision':'S2'",
 "SOL-GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011-d7ea2f5481e84f7eb9d0f718220793ec":"SOL-GATE05-R25-ROLE_USERDATA-INDEPENDENT-S2-20261011-098499b5238a467cb87509c88d8d2e07",
 "9FA1907CB215201E8AB8ACC89C033592B38B2260AACE1B7CB8F90CEC793030F0":"C3EC431869CD63E643E26DF22F1A80EE314967AD8589F8CF70B4F37A3113454B",
 "ACK_VERIFIED_INDEPENDENT_R25_STATIC_NORMAL_ROLE_USERDATA_QA_IN_PROGRESS":"ACK_VERIFIED_INDEPENDENT_R25_S2_NEWLINE_ORACLE_FRESH_NORMAL_QA_IN_PROGRESS",
 "SOL_R25_INDEPENDENT_ACK_VERIFIED":"SOL_R25_S2_INDEPENDENT_ACK_VERIFIED",
 "LOCAL-SOL-R25-INDEPENDENT-ACK":"LOCAL-SOL-R25-S2-INDEPENDENT-ACK",
 "nextA NOT_SENTpendingQA":"nextA NOT_SENTpendingS2_QA",
}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
s=re.sub(r'\b13220\b','13315',s)
anchor="cfg=tomllib.loads("
i=s.index(anchor)
addition="""oldq=R/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011'
assert sha(Q/'Program.cs')==sha(oldq/'Program.cs')=='6614E455D316F046BC9072171B4A39F676148E61395AEF889C2E95974E6A615C'
oldoracle=read(oldq/'NORMAL_EXPECTED_ORACLE.json');neworacle=read(Q/'NORMAL_EXPECTED_ORACLE.json')
assert list(neworacle['cases'])==list(oldoracle['cases']) and len(neworacle['cases'])==4
for key,e in oldoracle['cases'].items():
 n=neworacle['cases'][key];assert list(e)==list(n)
 assert {k:v for k,v in e.items() if k!='expected_redacted_utf8_text'}=={k:v for k,v in n.items() if k!='expected_redacted_utf8_text'}
 expected=json.dumps(e['expected_redacted'],ensure_ascii=False,indent=2).replace('\\n','\\r\\n')
 assert n['expected_redacted_utf8_text']==expected and e['expected_redacted_utf8_text']!=expected
"""
# Escapes above belong to the generated Python source, not literal line breaks.
addition=addition.replace("replace('\n','\r\n')","replace('\\\\n','\\\\r\\\\n')")
# Use explicit raw source for the single generation line.
lines=addition.splitlines();lines=[line for line in lines if not line.startswith(" expected=")]
addition='\n'.join(lines)+'\n'
# Insertion must precede the dependent expected assertion.
needle=" assert n['expected_redacted_utf8_text']==expected"
addition=addition.replace(needle," expected=json.dumps(e['expected_redacted'],ensure_ascii=False,indent=2).replace(chr(10),chr(13)+chr(10))\n"+needle)
s=s[:i]+addition+s[i:]
proofneedle="'initial_ACK_execution_statement':"
s=s.replace(proofneedle,"'S2_program_exact_S1_bytes_and_four_oracle_formatting_only_changes_master_checked':True,"+proofneedle)
s=s.replace("Freshnormal4cases ToSnapshot4Select8/full15snapshot13redaction-policyUTC-callerpurity QA executionverdictPENDING;initialnotbuilt statement historical.","FreshS2normal4cases ToSnapshot4Select8/full15snapshot13redaction-policyUTC-callerpurity QA executionverdictPENDING;Program exactS1bytesSHA6614E... and fourcases formattingONLY prospectivelyindependentorderedgraphCRLF correction Mastermatched;S1raw8FAIL/OSexit1protected;initialnotbuilt statement historical.")
out.write_text(s,encoding='utf8');print(str(out))
