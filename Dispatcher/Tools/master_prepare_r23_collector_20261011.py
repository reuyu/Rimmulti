from pathlib import Path
R=Path(__file__).resolve().parents[2];s=(R/'Dispatcher/Tools/master_collect_r22_declaration_20261011.py').read_text(encoding='utf8')
for a,b in [('r22','r23'),('R22','R23'),('declaration','identifier_mapping'),('DECLARATION','IDENTIFIER_MAPPING'),('9be1579a','31bd3af2'),('EngineGate05R23Declaration','EngineGate05R23IdentifierMapping'),("ack['envelope']==25","ack['envelope']==26"),('46764','49350'),('19812','19228'),('MASTER-CONTINUE-R23-20261011-01','MASTER-HEARTBEAT-R23-20261011T085442Z-01')]:s=s.replace(a,b)
start=s.index('def segments(raw):');end=s.index('os,_=segments(old)',start)
s=s[:start]+'''def segments(raw):
 spans=[]
 a=raw.index(b'                    originId = origin');z=raw.index(b'                    expectedRole = role.Trim(),',a);spans.append((a,z))
 for anchor in [b' IssueAdmissionReceipt(',b' IssueAdmissionReceiptFromBytes(']:
  start=raw.index(anchor);a=raw.index(b'            var desc = descriptor.Clone();',start);z=raw.index(b'            if (string.IsNullOrWhiteSpace(desc.originId))',a);spans.append((a,z))
 out=[];prev=0
 for a,z in spans:out.append(raw[prev:a]);prev=z
 out.append(raw[prev:]);return out,spans
''' +s[end:]
s=s.replace("p.resolve().is_relative_to(R)","p.resolve().is_relative_to(R)")
s=s.replace("'closure_changed':False,'foundation'","'trigger_received_at':'2026-10-11T08:54:42.092Z','closure_changed':False,'foundation'")
out=R/'Dispatcher/Tools/master_collect_r23_identifier_mapping_20261011.py';assert not out.exists();out.write_text(s,encoding='utf8');print('R23_COLLECTOR_PREPARED')
