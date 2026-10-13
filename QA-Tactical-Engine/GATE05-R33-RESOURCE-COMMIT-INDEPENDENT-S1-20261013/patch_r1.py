from common import *
import sys,traceback,difflib
out=Q/'PATCH_R1_STDOUT.txt';err=Q/'PATCH_R1_STDERR.txt';proof=Q/'PATCH_R1_TOOL.json';assert not out.exists() and not err.exists() and not proof.exists()
code=0;so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se
    try:
        assert load(Q/'static.TOOL.json')['exit_code']==1
        old=(Q/'static.py').read_bytes().decode('utf-8');actual=WORKER.read_bytes().decode('utf-8');assert actual.count('        private string ProcessCommandMainThread')==1
        assert old.count("'        private void ExecuteRequest'")==1
        new=old.replace("'        private void ExecuteRequest'","'        private string ProcessCommandMainThread'").replace("Q/'SOURCE_WHOLE_AWAKE_OUTSIDE_COMPARISON.json'","Q/'SOURCE_WHOLE_AWAKE_OUTSIDE_COMPARISON_R1.json'")
        dest=Q/'static_r1.py';assert not dest.exists();dest.write_bytes(new.encode('utf-8'));diff=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(Q/'static.py'),tofile=str(dest)));(Q/'STATIC_R1_EXACT_DIFF.txt').write_bytes(diff.encode('utf-8'))
        logold=(Q/'log.py').read_bytes().decode('utf-8');lognew=logold.replace("'bootstrap.py','static.py'","'bootstrap.py','static.py','static_r1.py'");assert lognew!=logold
        ld=Q/'log_r1.py';assert not ld.exists();ld.write_bytes(lognew.encode('utf-8'));(Q/'LOGGER_R1_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(logold.splitlines(True),lognew.splitlines(True))).encode('utf-8'))
        write(Q/'STATIC_R1_LOCATOR_CORRECTION.json',dict(at=now(),original_helper=row(Q/'static.py'),original_failure_tool=row(Q/'static.TOOL.json'),original_failure_stderr=row(Q/'static.STDERR.txt'),new_helper=row(dest),exact_diff=row(Q/'STATIC_R1_EXACT_DIFF.txt'),new_logger=row(ld),logger_diff=row(Q/'LOGGER_R1_EXACT_DIFF.txt'),actual_unique_boundary='private string ProcessCommandMainThread',scope='Passive source boundary locator correction and new witness filename only; original first witness/helper/raw unchanged. No candidate/oracle/hash expectation change.',candidate_build_or_run=0))
        print(json.dumps(dict(locator_corrected=True,new_version=True,first_failed_raw_retained=True,source_oracle_changes=0,candidate_calls=0)))
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=so0,se0
write(proof,dict(script=row(Path(__file__)),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True,candidate_calls=0))
print(json.dumps(dict(exit_code=code,stdout=row(out),stderr=row(err))));sys.exit(code)
