from prepare_s2 import Q,ROOT,write,now,sha,freeze
from pathlib import Path
import ast,json,sqlite3,re,hashlib,struct,base64,collections
E=Q/'Evidence'
def main():
    old=ROOT/'QA-Transaction-Pipeline/PIPELINE01-REV6-R1-E2-20261007/verify_data.py'
    names={'digest','encstr','fingerprint','bwstr','derivative','normalize','descriptor','rows','typed','audit'}
    exec(compile(ast.Module(body=[n for n in ast.parse(old.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(old),'exec'),globals())
    results=[];schemas=[]
    for stage in ['commit-parent','commit-audit','stale-audit']:
        db=Q/f'Databases/{stage}.db';r=audit(db);assert r['typed_operations']==2
        assert r['counts']==({'COMMITTED':1,'ABORTED':1} if stage=='stale-audit' else {'COMMITTED':2})
        results.append(r);c=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);d,metadata=descriptor(c);c.close()
        sig=hashlib.sha256(d.encode()).hexdigest().upper();assert sig=='079CFBAC4246592B4E2300630BBB39528C44CCAA6C1199C9811E9B1DB9C4B63C'
        (E/(stage+'-independent-descriptor.txt')).write_bytes(d.encode());write(E/(stage+'-schema-metadata.json'),metadata);schemas.append(dict(stage=stage,actual_signature=sig))
    cases=json.loads((E/'s2-results.json').read_text());assert len(cases['cases'])==3 and all(r['status']=='PASS' for r in cases['cases'])
    processes=json.loads((E/'processes.json').read_text());snapshot=json.loads((Q/'Tooling/R1/SNAPSHOT_BEFORE_EXECUTION.json').read_text())
    assert len(processes)==9 and all(sha(Path(f['path']))==f['sha256'] for f in snapshot['files'])
    for p in processes:
        loaded=json.loads(next(s.removeprefix('LOADED ') for s in p['output'] if s.startswith('LOADED ')))
        assert loaded['tool']['sha256']==snapshot['lineage']['dll_sha256'] and loaded['tool']['mvid']==snapshot['lineage']['dll_mvid']
        assert loaded['server']['mvid']=='bbb3d4f4-423c-4379-a931-58e4b3a50add'
        if 'interrupt' in p['name']:assert p['exit']!=0 and any(s.startswith('AFTER_DELEGATED_WRITE ') for s in p['output']) and not any(s.startswith('BOUNDARY_TIMEOUT ') for s in p['output'])
        else:assert p['exit']==0
    write(E/'independent-final-data-results.json',dict(at=now(),pass_=True,final_typed_operations=6,committed=5,aborted=1,actual_schema_checks=schemas,databases=results,old_oracle_top_level_executed=False,oracle_source_sha256=sha(old),tool_snapshot20_unchanged=True))
    after=freeze();before=json.loads((Q/'freeze-before.json').read_text());assert before['candidate103']==after['candidate103'] and before['engine19']==after['engine19'] and before['prior_inventories']==after['prior_inventories'];write(Q/'freeze-after.json',after)
    print(json.dumps(dict(final_typed_operations=6,committed=5,aborted=1,schemas=3,frozen_original_copy103_engine19_prior297_S1312_changes=0)))
if __name__=='__main__':main()
