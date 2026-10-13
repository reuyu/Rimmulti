from review_setup import *
import difflib,collections
oracle=load(Q/'NORMAL_EXPECTED_ORACLE.json');rows=[]
for a in load(Q/'RUN_ALLOCATION_PLAN.json')['allocations']:
    out=Path(a['output_root']);typed=load(out/'TYPED_CHECKS.json');fails=[r for r in typed if not r['matched']]
    for n,c in oracle['cases'].items():
        d=load(out/(n+'.observation.json'));actual=d['redactedBefore'];expected=c['expected_redacted_utf8_text'];diff=''.join(difflib.unified_diff(expected.splitlines(True),actual.splitlines(True),fromfile='PinnedOriginalOracle',tofile='ActualCandidateRedaction'))
        print(n,repr(diff[:600]));rows.append(dict(run_id=a['run_id'],case_id=n,initial_utf8bytes_matched=expected==actual,original_expected=expected,original_actual=actual,diff=diff,typed_failures=[r for r in fails if r['path'].startswith(n+'.')],json_values_equal=json.loads(actual)==c['expected_redacted'],expected_order=list(c['expected_redacted']),actual_order=list(json.loads(actual)),candidate_response=row(out/(n+'.observation.json')),no_oracle_runner_candidate_mutation=True))
    print('typedrows',len(typed),'bad',len(fails))
write(Q/'UNEXPECTED_NORMAL_FAILURE_DIAGNOSIS.json',dict(at=now(),rows=rows,allcandidatebuilds=0,QAfinalbuilds=1,freshcultures2=True,rebuild_rerun_oraclechange=0,originalraw_failed_assertions_preserved=True))
