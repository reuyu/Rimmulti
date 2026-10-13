from common import *
import sys,difflib
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R35_Publisher_Independent_Static_S1_20261013.md';RESULT=load(Q/'ACK_INITIAL.json')['result_id']
AUTH2=PKG/'MASTER_R35_STATIC_R2_SKIP_OPTIONAL_QUERY_FINALIZE_20261013.md';ADD=PKG/'coordination/MASTER_R35_STATIC_R2_OPTIONAL_QUERY_STOP_PRESERVATION_20261013.json';PART=PKG/'coordination/MASTER_R35_STATIC_LOCATOR_STOP_PARTIAL_PRESERVATION_20261013.json'
def guards():
    assert sha(AUTH2)=='20E2DB6E27AA790DEFEBE93079C687EE7692E2A9502DA976C25EEEADA6D9B074';assert sha(ADD)=='1BF0E3A6EA39D55247A45C280E37F8825A3E1F2BFB99B14666826A678F261E71'
    for n in ['bootstrap','resume_r1','review_r1']:
        d=load(Q/(n+'.TOOL.json'));assert d['exit_code']==0;check([d['stdout'],d['stderr']]);check(load(Q/(n+'.INPUT.json'))['files'])
    assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='E2EF90D0C15554347D6791B60982C17A24547109D046DE8F9A0CDB11050981C5'
    assert load(Q/'RESUME_R1_MASTER_RETURN_TOOL_PROOF.json')['isError'] is True
    assert load(Q/'RESUME_R1_MASTER_RETURN_RETRY1_TOOL_PROOF.json')['isError'] is False
    a=load(Q/'REVIEW_EXECUTION_ACCOUNTING.json');assert a['verdict']==VERDICT and a['publisher_Engine_compiler_runner_fixture_native_adverse_rejection']==0
    return a
mode=sys.argv[1];a=guards()
if mode=='prepare':
    after=preservation();before=load(Q/'PRESERVATION_BEFORE.json')
    for k in ['protected_files','frozen_files']:assert before[k]==after[k]
    partial=check(load(PART)['files']);assert len(partial)==16;additional=check(load(ADD)['files'])
    for f in ['PASSIVE_INPUT_MANIFEST.json','PASSIVE_R1_INPUT_MANIFEST.json']:check(load(Q/f)['files'])
    write(Q/'PRESERVATION_AFTER_R2.json',after)
    write(Q/'ADDITIONAL_PRESERVATION_AFTER_R2.json',dict(at=now(),partial_manifest=row(PART),partial_files=partial,additional_manifest=row(ADD),additional_files=additional,partial_count=len(partial),additional_count=len(additional),all_matched=True))
    unique={r['path'].lower() for rows in [after['protected_files'],after['frozen_files'],partial,additional] for r in rows}
    write(Q/'PRESERVATION_BEFORE_AFTER_R2.json',dict(at=now(),before=row(Q/'PRESERVATION_BEFORE.json'),after=row(Q/'PRESERVATION_AFTER_R2.json'),additional=row(Q/'ADDITIONAL_PRESERVATION_AFTER_R2.json'),protected_count=19229,frozen_count=34,partial_count=16,additional_count=len(additional),unique_paths_across_categories=len(unique),all_full_lists_equal=True,all_SHA_bytes_match=True))
    auth=AUTH2.read_bytes().decode('utf-8');write(Q/'FINAL_OPERATIONAL_QUALIFICATIONS_R2.json',dict(at=now(),authorization=row(AUTH2),authorization_full_text=auth,result_id=RESULT,optional_query='SKIPPED_PERMANENTLY_NOT_RETRIED',query_error_actual_conversation='decc95 PowerShellparseexit1 beforePython; complete conversation retained, notfabricatedbinaryraw',initial_locator_error='df9195 preserved, MasterboundedR1 wholefile/symbol recovery',R1_transport='Initialauto-reviewusage-limit NOTEXECUTED/failedactualreturn preserved; retry1actualsuccess',source_review=row(Q/'review_r1.TOOL.json'),report=row(REPORT),review_rerun=0,candidate_publisher_Engine_compiler_fixture_native_adverse=0,Master_disposition='PENDING'))
    old=(Q/'log_r1.py').read_bytes().decode('utf-8');new=(Q/'log_finalize_r2.py').read_bytes().decode('utf-8');(Q/'FINALIZATION_LOGGER_R2_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(Q/'log_r1.py'),tofile=str(Q/'log_finalize_r2.py'))).encode('utf-8'))
    print(json.dumps(dict(all_preserved=True,protected=19229,frozen=34,partial=16,additional=len(additional),unique_paths=len(unique),all_execution=0,optional_query='SKIPPED_NO_RETRY',report=row(REPORT))))
elif mode=='seal':
    d=load(Q/'finalize_r2_prepare.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']]);check([load(Q/'FINAL_OPERATIONAL_QUALIFICATIONS_R2.json')['report']])
    excluded=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json','finalize_r2_seal.STDOUT.txt','finalize_r2_seal.STDERR.txt','finalize_r2_seal.TOOL.json']
    files=[row(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.relative_to(Q).as_posix() not in excluded]+[row(REPORT)];check(files)
    ctx=dict(delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R35_PUBLISHER_INDEPENDENT_STATIC',stage='S1',result_id=RESULT,verdict=VERDICT,scope='FROZEN_PUBLISHER_TEXT_STATIC_ONLY',publisher_Engine_compiler_fixture_native_adverse=0,Master_disposition='PENDING',Foundation='HOLD',full_native_E2='NOT_RELEASED',closure=False)
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),**ctx,files=files,file_count=len(files),cycle_and_postseal_exclusions=excluded,actual_seal_logger_and_direct_return_preserved_separately=True))
    write(Q/'RESULT_INDEX.json',dict(at=now(),**ctx,source_accounting=a,counts_not_runtime_tests=True,report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ACK=row(Q/'ACK_INITIAL.json'),preservation=row(Q/'PRESERVATION_BEFORE_AFTER_R2.json'),operational_qualifications=row(Q/'FINAL_OPERATIONAL_QUALIFICATIONS_R2.json')))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),**ctx,initial_ACK=row(Q/'ACK_INITIAL.json'),initial_mirror=row(Q/'ACK.json'),resume_R1_ACK=row(Q/'RESUME_R1_ACK.json'),initial_ACK_unchanged=True,manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),report=row(REPORT)))
    write(Q/'RETURN_PENDING.json',dict(at=now(),**ctx,status='PENDING_TOOL_SUBMISSION',intent='One direct completion after actual numeric seal exit; actual structuredreturn separate, no impliedacceptance'))
    arts=[row(Q/n) for n in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_PENDING.json','PRESERVATION_BEFORE_AFTER_R2.json']]+[row(REPORT)];check(load(Q/'EVIDENCE_MANIFEST.json')['files']);check(arts)
    comp=dict(at=now(),**ctx,status='COMPLETED',artifacts=arts,evidence_file_count=len(files),source_counts=dict(flow=9,config=13,path=10,CLI=6,claims=7,R36_requirements=8,normal_prepared_cases=6),source_counts_not_tests=True,production_changes=0,optional_query_retries=0,review_reruns=0,atomic_completion_last=True,postseal_exclusions=excluded)
    write(Q/'COMPLETION.json.tmp',comp);assert not (Q/'COMPLETION.json').exists();(Q/'COMPLETION.json.tmp').rename(Q/'COMPLETION.json')
    print(json.dumps(dict(report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json'),evidence_file_count=len(files),all_execution=0,verdict=VERDICT)))
else:raise ValueError(mode)
