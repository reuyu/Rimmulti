from pathlib import Path
root = Path(__file__).resolve().parents[2]
source = (root / 'Dispatcher/Tools/master_verify_sol_r22_independent_ack_20261011.py').read_text(encoding='utf8')
for old, new in [
 ('R22', 'R23'), ('r22', 'r23'), ('DECLARATION', 'IDENTIFIER_MAPPING'),
 ('f555312829e4454ea4d3e254fcfc054d', '6676d9031f23400b975339ea0a56f0ea'),
 ('22920', '5376'), ('33893', '80603'), ('11639', '12350'),
 ('81E81464ACFF598C05787230DAA5F18EFC4EC90AA1BC844AD352D27D6262CA93', '3AB773C5CEF01FE98514D78C2C3087D64000CBC3B39A5060214FCEC811DDC662'),
 ('0BA31AF369F34D1238E54DDE4173799614FC9547AD20924EB42E1D48BFA7D06E', '58A4E0E9F7748C0E23E5D2818CA29D3C72151E3052E2811989C4290B9A520181'),
 ('len(read(fm)[\'files\'])==114', 'len(read(fm)[\'files\'])==126'),
 ('/frozen114/', '/frozen126/'), ('/frozen114', '/frozen126'),
]: source = source.replace(old, new)
# Preserve the exact immutable initial ACK if the active agent later publishes a final ACK.
source = source.replace("and sha(ap)==sha(Q/'ACK.json')", '')
source = source.replace("'initial_ACK_scope_qualification':'Generic config scope label partial; exact frozen R23 sent WP controls declaration/privatecapture/receipt/fullgraph/Unicode-originplan/UTC-regression scope. Raw ACK unchanged.'", "'initial_ACK_scope_qualification':'Exact sent WP controls twenty normal receipts: sixteen UTC/opaque regressions plus four admitted valid padded-lowercase role/capability cases, usedClone14 and normal16snapshot. Initial console receipt16 annotation is historical; prospective oracle20 required. Raw ACK unchanged.'")
# Independently compare the source scope admission with Master-owned fixed segment bytes.
marker = "cfg=tomllib.loads"
addition = '''scope_path=Q/'THREE_SPAN_SCOPE_ADMISSION_BEFORE_CALLS.json';scope=read(scope_path)
worker=Path(scope['source']['path']);wb=worker.read_bytes()
assert sha(worker)==scope['source']['sha256']==masterproof['source_sha256'] and len(wb)==scope['source']['bytes']
assert scope['all_other_bytes_exact'] and len(scope['three_authorized_spans'])==3 and len(scope['four_fixed_ordered_segments'])==4
for seg in scope['four_fixed_ordered_segments']:
 p=Path(seg['original_fixed_file']['path']);assert sha(p)==seg['original_fixed_file']['sha256'] and p.stat().st_size==seg['original_fixed_file']['bytes']
 assert wb[seg['new_start']:seg['new_end']]==p.read_bytes() and seg['bytes_exact']
for row in scope['fixed']:
 p=Path(row['path']);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
'''
source = source.replace(marker, addition + marker)
source = source.replace("'A_terminal_completion_deduped_unchanged':True", "'three_span_scope_admission_path':str(scope_path),'three_span_scope_admission_sha256':sha(scope_path),'four_fixed_segments_independently_matched':4,'A_terminal_completion_deduped_unchanged':True")
start=source.index("para=f'")
end=source.index('\nfor q in [', start)
source=source[:start]+'''para=f'\\n\\n## LOCAL-SOL-R23-INDEPENDENT-ACK — {at}\\nOriginal Sol {ack["delivery_id"]}/{ack["result_id"]} immutable initial ACK matches actual active turn {snap["latestTurn"]["id"]}, cursor {snap["revision"]}. Master rehashed12350 protected paths, frozen126 and current production9; Debug/Release SHA-MVID-CodeView/PDB-source4of4 and all four ordered fixed segments matched. Fresh20 normal receipt fullgraph, private-copy rolecap4 equivalence, original identifiers/usedClone14 and normal16snapshot QA remain execution-verdict PENDING. Initial notbuilt statement and receipt16 annotation are historical; exact sent WP/prospective oracle20 controls. Original evidence unchanged; no duplicate/new WP, production rebuild, native/global/Process/adverse execution, new closure or scheduler change. M01 source fix credited OPEN pending fresh QA; native CLI remains SOURCE_ONLY/unobserved. R19 opaque/R21 UTC historical scoped CLOSED retained. Same actual hourly monitor PAUSED; direct completion push continues. Engine002006/Pipeline007/current schema/G-Q1 OPEN, Foundation HOLD, full native E2 NOT_RELEASED. Proof {vp}\\n'
''' + source[end:]
target=root/'Dispatcher/Tools/master_verify_sol_r23_independent_ack_20261011.py'
assert not target.exists()
compile(source,str(target),'exec')
target.write_text(source,encoding='utf8')
print('R23_METADATA_ONLY_ACK_VERIFIER_PREPARED')
