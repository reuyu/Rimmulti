from prepare_s1 import Q,ROOT,PRIOR,write,now,sha,PKG,mvid
import ast,json,sqlite3,re,hashlib,struct,uuid
from pathlib import Path
E=Q/'Evidence'
def main():
    source=PRIOR/'verify_data.py';wanted={'normalize','descriptor'}
    exec(compile(ast.Module(body=[n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in wanted],type_ignores=[]),str(source),'exec'),globals())
    results=[]
    for phase in ['','Run2/']:
        for name in ['acknowledged','fixture','normal-copy','normal-vacuum','backup-source-copy','normal-backup']:
            path=Q/f'{phase}Databases/{name}.db';c=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);desc,metadata=descriptor(c);c.close()
            sig=hashlib.sha256(desc.encode()).hexdigest().upper();assert sig=='079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C'
            prefix='run2-' if phase else 'run1-'
            (E/(prefix+name+'-independent-descriptor.txt')).write_bytes(desc.encode());write(E/(prefix+name+'-schema-metadata.json'),metadata);results.append(dict(db=str(path),signature=sig))
    for phase in ['','Run2/']:
        evidence=Q/f'{phase}Evidence';procs=json.loads((evidence/'processes.json').read_text())
        ack=next(r for r in procs if r['name']=='ack-child');retry=next(r for r in procs if r['name']=='ack-restart-retry')
        old=json.loads(next(s.removeprefix('ACK_SUCCESS_DURABLE ') for s in ack['output'] if s.startswith('ACK_SUCCESS_DURABLE ')))['result']['Receipt']
        new=json.loads(next(s.removeprefix('RETRY ') for s in retry['output'] if s.startswith('RETRY ')))['Receipt'];assert old==new
        base=json.loads((evidence/'fixture-closed-baseline.json').read_text())['records']
        assert len(base['OperationRecords'])==10 and len(base['CommitReceipts'])==8 and len(base['AuditRecords'])==10
        assert {a['ProbeScopeId']:a['ProbeRevision'] for a in base['ProbeAggregates']}=={'A':3,'B':3,'C':2}
        assert all(a['OldRevision']==2 and a['NewRevision'] is None for a in base['AuditRecords'] if a['EventType']=='PROBE_CAS_REJECTED')
    reader=PKG/'coordination/sol_recovery_identity_20261007.py';wanted={'metadata_streams','codeview_guid','portable_pdb'}
    exec(compile(ast.Module(body=[n for n in ast.parse(reader.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name in wanted],type_ignores=[]),str(reader),'exec'),globals())
    lineage=[]
    for dll in [Q/'Tooling/R1/bin/Harness.dll',Q/'Runtime/WarEconomy.Server.dll',Q/'Runtime/WarEconomy.Common.dll']:
        p=dll.with_suffix('.pdb');info=portable_pdb(p);info.update(dll=str(dll),sha256=sha(dll),mvid=mvid(dll),pdb_sha256=sha(p),codeview_guid=codeview_guid(dll));assert info['guid']==info['codeview_guid'] and all(r['matched'] for r in info['documents']);lineage.append(info)
    snapshot=json.loads((Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json').read_text());assert all(sha(__import__('pathlib').Path(f['path']))==f['sha256'] for f in snapshot['files'])
    write(E/'independent-schema-lineage-results.json',dict(at=now(),schema_checks=results,lineage=lineage,tool_before_after_unchanged=True,descriptor_algorithm_source=str(source),descriptor_algorithm_source_sha256=sha(source),prior_top_level_execution=False))
    print(json.dumps(dict(schemas=len(results),lineage_documents=[len(i['documents']) for i in lineage],all_matched=True)))
if __name__=='__main__':main()
