from common import *
import sys
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R35_Publisher_Preparation_S1_20261013.md';RESULT=load(Q/'ACK_INITIAL.json')['result_id']
def guards():
    for n in ['bootstrap','analyze','expectations']:
        d=load(Q/(n+'.TOOL.json'));assert d['exit_code']==0;check([d['stdout'],d['stderr']])
    assert sha(Q/'ACK_INITIAL.json')==sha(Q/'ACK.json')=='324F15D40478C42268B20BAF2C170D77AA5116F775B3EF85C02BDCAF46FC8C03'
    a=load(Q/'PREPARATION_EXECUTION_ACCOUNTING.json');assert a['verdict']==VERDICT
    for k in ['fixturewriting','publishercalls','compilerbuilds','candidatecalls','subprocesschildren','nativegame','adverse_rejection','mutable_R35_read_hash']:assert a[k]==0
    return a
mode=sys.argv[1];a=guards()
if mode=='prepare':
    b=load(Q/'PRESERVATION_BEFORE.json');aft=preservation()
    for k in ['protected_files','additive_late_helper','frozen_files']:assert b[k]==aft[k]
    oracle=load(Q/'NORMAL_PUBLISHER_EXPECTATION_ORACLE.json');orig=load(PAIR);assert len(oracle['cases'])==6
    for c,o in zip(oracle['cases'],orig['prospective_cases']):
        assert c['case_id']==o['case_id'];assert c['publication_calls_now']==c['fixture_files_now']==0
        for r,key in zip(c['inputs'],['independently_supplied_parent14_7','independently_supplied_child14_7']):
            raw=r['raw_config_expected'];v=raw['utf8_text'].encode('utf-8');assert hashlib.sha256(v).hexdigest().upper()==raw['sha256']==o[key]['raw_config']['sha256'] and len(v)==raw['bytes'] and v.hex().upper()==raw['hex']
            assert r['config14']==o[key]['config14'] and r['original_descriptor7']==o[key]['original_descriptor7']
            assert [k for k in r['original_descriptor7'] if r['original_descriptor7'][k]!=r['prospectively_approved_new_fixture_descriptor7'][k]]==['expectedConfigPath']
        raw=c['expected_bundle'];v=raw['utf8_text'].encode('utf-8');assert hashlib.sha256(v).hexdigest().upper()==raw['sha256'] and len(v)==raw['bytes'] and json.loads(raw['utf8_text'])==c['expected_aux4']
    write(Q/'PREPARATION_SELF_REVIEW.json',dict(at=now(),case_count=6,config_literals=12,path_only_changes=12,original_oracles=[row(PAIR),row(COMBINED)],all_expected_bytes_SHA_hex_checked=True,not_publisher_or_fixture_execution=True,no_future_path_existence_claim=True))
    write(Q/'PRESERVATION_AFTER.json',aft);unique={r['path'].lower() for k in ['protected_files','additive_late_helper','frozen_files'] for r in aft[k]}
    write(Q/'PRESERVATION_BEFORE_AFTER.json',dict(at=now(),before=row(Q/'PRESERVATION_BEFORE.json'),after=row(Q/'PRESERVATION_AFTER.json'),protected_count=19103,additional_count=1,frozen_count=75,unique_paths_across_categories=len(unique),all_full_lists_equal=True,all_SHA_bytes_match=True,mutable_R35_read_hash=0))
    print(json.dumps(dict(protected=19103,extra=1,frozen=75,unique_paths=len(unique),all_preserved=True,self_review='EXPECTED_METADATA_ONLY',all_execution=0,report=row(REPORT))))
elif mode=='seal':
    d=load(Q/'finalize_prepare.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']]);assert load(Q/'PRESERVATION_BEFORE_AFTER.json')['all_full_lists_equal']
    excluded=['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','COMPLETION.json.tmp','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json','finalize_seal.STDOUT.txt','finalize_seal.STDERR.txt','finalize_seal.TOOL.json']
    files=[row(p) for p in sorted(Q.rglob('*')) if p.is_file() and p.relative_to(Q).as_posix() not in excluded]+[row(REPORT)];check(files)
    ctx=dict(delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R35_PUBLISHER_PREPARATION',stage='S1',result_id=RESULT,verdict=VERDICT,R35='NOT_READ_NOT_REVIEWED',execution_admission=False,Master_disposition='PENDING',Foundation='HOLD',full_native_E2='NOT_RELEASED')
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),**ctx,files=files,file_count=len(files),cycle_and_postseal_exclusions=excluded,postseal_logger_and_structured_return_captured_separately=True))
    write(Q/'RESULT_INDEX.json',dict(at=now(),**ctx,accounting=a,counts_not_execution=True,protected=19103,additional=1,frozen=75,report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),initial_ACK=row(Q/'ACK_INITIAL.json'),self_review=row(Q/'PREPARATION_SELF_REVIEW.json'),preservation=row(Q/'PRESERVATION_BEFORE_AFTER.json')))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),**ctx,initial_ACK=row(Q/'ACK_INITIAL.json'),mirror=row(Q/'ACK.json'),index=row(Q/'RESULT_INDEX.json'),manifest=row(Q/'EVIDENCE_MANIFEST.json'),report=row(REPORT),initial_ACK_unchanged=True))
    write(Q/'RETURN_PENDING.json',dict(at=now(),**ctx,status='PENDING_TOOL_SUBMISSION',intent='One direct completion report after actual seal; structured return saved separately'))
    arts=[row(Q/n) for n in ['EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','RETURN_PENDING.json','PRESERVATION_BEFORE_AFTER.json']]+[row(REPORT)];check(load(Q/'EVIDENCE_MANIFEST.json')['files']);check(arts)
    comp=dict(at=now(),**ctx,status='COMPLETED',artifacts=arts,evidence_file_count=len(files),preparation_counts=dict(normal_cases=6,config_literals=12,path_bindings=12,old_source_gaps=12,source_refusal_obligations=15,readiness_deltas=7,admission_criteria=12,plan_steps=9),candidate_compiler_fixture_publisher_subprocess_native_adverse=0,mutable_R35_read_hash=0,counts_not_tests=True,closure=False,atomic_completion_last=True,postseal_exclusions=excluded)
    write(Q/'COMPLETION.json.tmp',comp);assert not (Q/'COMPLETION.json').exists();(Q/'COMPLETION.json.tmp').rename(Q/'COMPLETION.json')
    print(json.dumps(dict(report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json'),evidence_file_count=len(files),all_execution=0,verdict=VERDICT)))
else:raise ValueError(mode)
