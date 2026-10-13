from review_setup import *
if __name__=='__main__':
    assert not (Q/'runner/QaPureRunner.exe').exists();initial=(Q/'pin_admission.py').read_text(encoding='utf-8-sig');(Q/'PIN_ADMISSION_INITIAL.txt').write_text(initial,encoding='utf-8')
    write(Q/'PRE_BUILD_METADATA_RECONCILIATION.json',dict(at=now(),initial_tool_chunk='763b06',initial_exit=1,initial_assertion='HumanannotationValidatorResult26,actualmanualoracle andfrozensource25fields;config14/redacted13correct',candidate_calls=0,runner_builds=0,source_census_unchanged=True,oracle_case_values_unchanged=True,scope='Beforebuild text/countannotation correction only,notobservedcandidateoutput'))
    for n in ['Program.cs','RunnerTemplate.cs.txt','pin_admission.py']:
        p=Q/n;s=p.read_text(encoding='utf-8-sig').replace('==26','==25').replace('result26','result25').replace('Whole26fields','Whole25fields');p.write_text(s,encoding='utf-8')
    d=load(Q/'ORACLE_BEFORE_BUILD.json');d['source']=row(Q/'Program.cs');d.pop('validator_result_fields_full26');d['validator_result_fields_full25']=True;write(Q/'ORACLE_BEFORE_BUILD.json',d)
