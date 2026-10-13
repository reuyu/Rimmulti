from pathlib import Path
import sys,json,hashlib,traceback,datetime
Q=Path(__file__).resolve().parent
out=Q/'RESUME_POSTANALYSIS_PREPARE_STDOUT.txt';err=Q/'RESUME_POSTANALYSIS_PREPARE_STDERR.txt';proof=Q/'RESUME_POSTANALYSIS_PREPARE_TOOL.json'
assert not out.exists() and not err.exists() and not proof.exists()
def row(p):return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest().upper(),bytes=p.stat().st_size)
code=0;olds,olde=sys.stdout,sys.stderr
with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
    sys.stdout,sys.stderr=so,se
    try:
        from review_setup import load,write,sha,PKG,now
        notice=PKG/'MASTER_R29_S3_POSTRUN_ANALYSIS_R1_AUTHORIZATION_20261012.md'
        assert sha(notice)=='4585469BF681B1AA314260144B910995CF143B07896FFBAE51C1C31C612815E6'
        assert not (Q/'COMPLETION.json').exists()
        A=Q/'postanalysis-r1';assert not A.exists();A.mkdir()
        inventories=[]
        for al in load(Q/'RUN_ALLOCATION_PLAN.json')['allocations']:
            r=Path(al['output_root']);d=load(r/'OUTPUT_INVENTORY.json');files=d['files']
            assert {p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}=={v['relative_path'] for v in files}
            for v in files:
                p=r/v['relative_path'];assert str(p)==v['path'] and sha(p)==v['sha256'] and p.stat().st_size==v['bytes']
            assert len(files)==402 and sum(v['relative_path'].endswith('.utf8') for v in files)==336
            assert {'ACTUAL_ADMITTED_CALL_LEDGER.json','TYPED_CHECKS.json','NORMAL_RESULTS.json'}<={v['relative_path'] for v in files}
            inventories.append(row(r/'OUTPUT_INVENTORY.json'))
        initial=load(Q/'ACK_INITIAL.json');assert sha(Q/'ACK_INITIAL.json')=='E62D7A47248E015DBB1C293723108E8368D544F0221B6CC3028122AFB382FE31'
        write(A/'RESUME_ACK.json',dict(at=now(),delivery_id=initial['delivery_id'],result_id=initial['result_id'],wp_id=initial['wp_id'],wp_revision='S3',resume_id='SOL-GATE05-R29-STARTUP_PAIR-S3-POSTANALYSIS-R1-20261012-01',status='ACKNOWLEDGED_POSTANALYSIS_ONLY',notice=row(notice),original_ACK=row(Q/'ACK_INITIAL.json'),actual_matching_sealed_inventories=inventories,compile_allowance_used=1,runner_allowance_used=2,additional_candidate_calls_allowed=0,normal_verdict='FINAL_REVIEW_PENDING',sourceHigh3='OPEN',nativeE2='NOT_RELEASED',Foundation='HOLD'))
        draft=(Q/'post_analysis.py').read_bytes()
        prefix=b'from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parent.parent))\n'
        derived=prefix+draft
        derived=derived.replace(b'from collections import Counter\n',b'from collections import Counter\nA=Path(__file__).resolve().parent\n')
        derived=derived.replace(b"write(Q/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json'",b"write(A/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json'")
        derived=derived.replace(b"write(Q/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json'",b"write(A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json'")
        (A/'post_analysis.py').write_bytes(derived)
        (A/'log_stage.py').write_bytes((Q/'log_stage_r1.py').read_bytes())
        write(A/'POSTANALYSIS_PROSPECTIVE_SOURCE.json',dict(at=now(),draft=row(Q/'post_analysis.py'),prepared=row(A/'post_analysis.py'),logger=row(A/'log_stage.py'),output_location_only_adaptation=True,no_oracle_or_run_changes=True))
        print(json.dumps(dict(resume_ACK=row(A/'RESUME_ACK.json'),inventories_matched=2,output_paths_verified=804,prepared_analysis=row(A/'post_analysis.py'),candidate_calls=0)))
    except BaseException:code=1;traceback.print_exc()
    finally:sys.stdout,sys.stderr=olds,olde
proof.write_bytes((json.dumps(dict(script=row(Path(__file__)),at=datetime.datetime.now().isoformat(),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True),indent=2)+'\n').encode('utf-8'))
print(json.dumps(dict(exit_code=code,stdout=row(out),stderr=row(err)),ensure_ascii=True));sys.exit(code)
