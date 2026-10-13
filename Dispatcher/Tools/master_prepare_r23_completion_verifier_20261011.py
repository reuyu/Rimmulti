from pathlib import Path
import re
R=Path(__file__).resolve().parents[2]
s=(R/'Dispatcher/Tools/master_verify_r22_independent_completion_20261011.py').read_text(encoding='utf8')
for a,b in [('R22','R23'),('r22','r23'),('DECLARATION','IDENTIFIER_MAPPING'),('f555312829e4454ea4d3e254fcfc054d','6676d9031f23400b975339ea0a56f0ea'),('823D25293FF027F9E6FF962C5C775F214B2789E71AE782ACA860D01C173FDB19','350A3AA6FEFC83D0045B7C2D4633E65F8E8951B2606C385A8C0F8E543EA1DD42'),('578','646'),('11639','12350'),('261','297'),('208','220'),('249','273'),('618','706'),('410','466'),('176','200'),("==32\n assert not any", "==40\n assert not any"),('11080','12456'),('114','126'),('24321','25056'),('97421','34592'),('19552','34628'),('four_mutable_spans_five_fixed_segments','three_mutable_spans_four_fixed_segments'),('FOUR_SPAN_SCOPE','THREE_SPAN_SCOPE'),('five_fixed_ordered_segments','four_fixed_ordered_segments'),('==5\nfor row','==4\nfor row'),('QA.R23','QA.R23'),('G05R23-9be1579a','G05R23-31bd3af2'),('EngineGate05R23Declaration','EngineGate05R23IdentifierMapping'),("len(inv)==18","len(inv)==24"),("==54 and result", "==66 and result"),("producer18_nonself", "producer24_nonself")]:s=re.sub(r"\b"+re.escape(a)+r"\b",b,s) if a.isdigit() else s.replace(a,b)
# Receipt counts are20 in each culture; only original sixteen UTC families retain the zero/fraction/whole classification.
s=s.replace("assert len(receipt_bindings)==32", "assert len(receipt_bindings)==40")
s=s.replace("len(utc['rows'])==32", "len(utc['rows'])==40")
s=s.replace("})==16\nassert all", "})==20\nassert all")
s=s.replace("[('ZERO_FRACTION7_MAIN',16),('FRACTION7',8),('WHOLE_SECONDS',8)]", "[('ZERO_FRACTION7_MAIN',16),('FRACTION7',8),('WHOLE_SECONDS',8),('ROLECAP_EQUIVALENCE',8)]")
s=s.replace("len(used['cases'])==32", "len(used['cases'])==40")
s=s.replace("'M01_CLI_original_identifier_Trim':'REVISION_REQUIRED_SOURCEONLY','role_capability_normalization':'OPEN_SOURCEONLY_CANONICAL_INPUTS_PASS'", "'M01_CLI_original_identifier_mapping':'SOURCE_FIX_CREDITED_NATIVECLI_UNTESTED','role_capability_normalization':'FRESH_NORMAL4_PRIVATECOPY_EQUIVALENCE_PASS','producer_call_count_correction':'ACTUAL_RAW_SUM66_SUPERSEDES_MASTER71_ANNOTATION'")
s=s.replace("'receipt_cases':16", "'receipt_cases':20")
s=s.replace("PASS_PENDING_MASTER_DISPOSITION;M01_CLI_TRIM_REVISION_REQUIRED", "PASS_PENDING_MASTER_DISPOSITION;CLI_SOURCE_FIX_NORMAL_EQUIVALENCE_CREDITED_NATIVECLI_UNTESTED")
s=s.replace("'grouped_reads':220", "'grouped_reads':240")
# Strong check for the newly admitted role/capability normal equivalence, without executing candidate.
at=s.index("scope=read(Q/'THREE_SPAN")
s=s[:at]+'''roles=read(Q/'NORMAL_ROLECAP_EQUIVALENCE_FULLGRAPH_BINDING.json');assert len(roles['cases'])==8
for row in roles['cases']:
 verify(row['fulltyped_original_purity']);d=row['original_descriptor']
 assert row['originalcaller_andusedClone_verbatim_before_edits'] and row['entiregraph_andredactedBytes_matched'] and row['positive_semantically_equivalent_contract_explicitly_admitted'] and not row['negative_rejection']
 assert d['expectedRole'] in ['  simulation  ','  read_only  '] and d['expectedCapabilityBoundary']=='  local_sandboxed  '
 assert row['bound_role']==d['expectedRole'].strip().upper() and row['bound_capability']=='LOCAL_SANDBOXED'
''' + s[at:]
out=R/'Dispatcher/Tools/master_verify_r23_independent_completion_20261011.py';compile(s,str(out),'exec');out.write_text(s,encoding='utf8');print('R23_READONLY_COMPLETION_VERIFIER_PREPARED')
