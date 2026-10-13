from review_setup import *
import shutil
if __name__=='__main__':
    assert not (Q/'runner/QaPureRunner.exe').exists() and not (Q/'BUILD_TOOL_PROOF.json').exists() and not (Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json').exists()
    archive=Q/'prebuild_setup_attempt';archive.mkdir();shutil.copy2(Q/'BUILD_INVOCATION_TOOL_PROOF.json',archive/'BUILD_INVOCATION_TOOL_PROOF.json')
    write(archive/'SETUP_FAILURES.json',dict(at=now(),pin_exit=1,reason='Stale source-only prepare_evidence_tools.py file name in new pin list;actual helper absent',subsequent_build_wrapper_exit=1,subsequent_runpre_exit=1,all_compiler_process_launches=0,all_candidate_calls=0,new_expected_values_unchanged=True,final_pin_not_written=True))
    print('Pre-pin setup failure archived;compiler andcandidate calls0;old candidate/QA unchanged')
