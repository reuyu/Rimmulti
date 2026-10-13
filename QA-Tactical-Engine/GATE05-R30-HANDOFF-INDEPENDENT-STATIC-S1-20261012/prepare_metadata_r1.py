from qa_common import *
import sys,traceback,difflib
out=Q/'METADATA_SCHEMA_R1_PREPARE_STDOUT.txt';err=Q/'METADATA_SCHEMA_R1_PREPARE_STDERR.txt';proof=Q/'METADATA_SCHEMA_R1_PREPARE_TOOL.json'
assert not out.exists() and not err.exists() and not proof.exists()
code=0;so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se
    try:
        dep=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
        assert sha(dep)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
        r=next(r for r in load(dep)['files'] if Path(r['frozen_path']).name=='UnityEngine.CoreModule.dll')
        p=Path(r['frozen_path']);baseline=next(v for v in load(BASELINE)['files'] if Path(v['path'])==p)
        assert sha(p)==r['sha256']==baseline['sha256'] and p.stat().st_size==r['size']==baseline['bytes']
        old=Q/'review_static.py';new=Q/'review_static_r1.py';b=old.read_bytes()
        assert b.count(b"refrow['bytes']")==1 and not new.exists();new.write_bytes(b.replace(b"refrow['bytes']",b"refrow['size']"))
        logold=Q/'log_stage.py';lognew=Q/'log_stage_r1.py';s=logold.read_bytes();needle=b"'review_static.py','finalize.py'"
        assert s.count(needle)==1 and not lognew.exists();lognew.write_bytes(s.replace(needle,b"'review_static.py','review_static_r1.py','finalize.py'"))
        dp=Q/'METADATA_SCHEMA_R1_EXACT_DIFF.txt';assert not dp.exists();dp.write_bytes(''.join(difflib.unified_diff(b.decode('utf-8').splitlines(True),new.read_text(encoding='utf-8').splitlines(True),fromfile='original-KeyError-size-locator',tofile='new-fixed-schema-locator')).encode('utf-8'))
        write(Q/'METADATA_SCHEMA_R1_CORRECTION.json',dict(at=now(),original_helper=row(old),corrected_helper=row(new),diff=row(dp),original_failure_tool=row(Q/'review_static_references.TOOL.json'),original_stderr=row(Q/'review_static_references.STDERR.txt'),sealed_dependency_manifest=row(dep),actual_size_key='size',actual_reference=row(p),protected_baseline_row=baseline,scope='WP-authorized passive JSON schema locator correction only; no hash/type/source/expected semantic change; original failure remains exit1',candidate_compiler_runner_native_calls=0,new_logger=row(lognew)))
        print(json.dumps(dict(corrected=row(new),size_key='size',bytes=r['size'],baseline_match=True,source_and_hash_semantics_unchanged=True)))
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=so0,se0
write(proof,dict(at=now(),script=row(Path(__file__)),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True));print(json.dumps(dict(exit_code=code,stdout=row(out),stderr=row(err))));sys.exit(code)
