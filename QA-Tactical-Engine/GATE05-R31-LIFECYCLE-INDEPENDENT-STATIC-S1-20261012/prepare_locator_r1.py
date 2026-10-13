from qa_common import *
import sys,traceback,difflib
out=Q/'LOCATOR_R1_PREPARE_STDOUT.txt';err=Q/'LOCATOR_R1_PREPARE_STDERR.txt';proof=Q/'LOCATOR_R1_PREPARE_TOOL.json';assert not out.exists() and not err.exists() and not proof.exists()
code=0;so0,se0=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se
    try:
        manifest=load(MAN);matching=[r for r in manifest['files'] if Path(r['frozen_path']).name=='Newtonsoft.Json.dll'];assert len(matching)==1;verify(matching,'frozen_path')
        declared=next(r for r in load(FT/'BUILD_INPUT_MANIFEST.json')['compiler_dependencies'] if r['name']=='Newtonsoft.Json.dll')
        assert Path(declared['path']).is_file()
        original=Q/'review.py';new=Q/'review_r1.py';b=original.read_bytes()
        before=b"            assert r['path'].lower() in base\n            p=Path(base[r['path'].lower()]['path']);verify([base[r['path'].lower()]])"
        after=b"            if r['path'].lower() in base:\n                p=Path(base[r['path'].lower()]['path']);verify([base[r['path'].lower()]])\n            else:\n                candidates=[Path(v['frozen_path']) for v in mapping.values() if Path(v['frozen_path']).name==r['name']]\n                assert len(candidates)==1\n                p=candidates[0]"
        assert b.count(before)==1
        corrected=b.replace(before,after)
        oldpart=b"evidence_discrepancy_not_repaired=True))"
        newpart=b"evidence_discrepancy_not_repaired=True,declared_path_in_QA_baseline=r['path'].lower() in base,current_unprotected_declared_path_observation=(row(Path(r['path'])) if r['path'].lower() not in base and Path(r['path']).is_file() else None),frozen_path_is_metadata_witness_not_proof_of_declared_compile_reference=True))"
        assert corrected.count(oldpart)==1;corrected=corrected.replace(oldpart,newpart)
        assert not new.exists();new.write_bytes(corrected)
        logger=Q/'log_stage.py';ln=Q/'log_stage_r1.py';l=logger.read_bytes();needle=b"'review.py','finalize.py'";assert l.count(needle)==1 and not ln.exists();ln.write_bytes(l.replace(needle,b"'review.py','review_r1.py','finalize.py'"))
        dp=Q/'LOCATOR_R1_EXACT_DIFF.txt';assert not dp.exists();dp.write_bytes(''.join(difflib.unified_diff(b.decode('utf-8').splitlines(True),corrected.decode('utf-8').splitlines(True),fromfile='original-baseline-coverage-assumption-failed',tofile='new-existing-frozen-locator-with-explicit-coverage-gap')).encode('utf-8'))
        write(Q/'LOCATOR_R1_CORRECTION.json',dict(at=now(),old=row(original),new=row(new),diff=row(dp),first_failed_tool=row(Q/'review_provenance.TOOL.json'),first_full_stderr=row(Q/'review_provenance.STDERR.txt'),actual_unique_frozen_reference=matching[0],declared_dependency=declared,current_declared_path=row(Path(declared['path'])),scope='WP authorized passive frozen path locator correction; baseline coverage gap and declared dependency mismatches remain findings, no source/hash/type/expected changes',original_candidate_or_native_calls=0))
        print(json.dumps(dict(unique_frozen=row(Path(matching[0]['frozen_path'])),declared_path_missing_baseline_coverage=True,declared_original_current=row(Path(declared['path'])),new_helper=row(new),no_mismatch_repair=True)))
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=so0,se0
write(proof,dict(at=now(),script=row(Path(__file__)),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True));print(json.dumps(dict(exit_code=code,stdout=row(out),stderr=row(err))));sys.exit(code)
