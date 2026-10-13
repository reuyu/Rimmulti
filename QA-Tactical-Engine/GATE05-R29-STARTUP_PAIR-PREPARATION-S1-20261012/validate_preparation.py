from bootstrap_review import *
from prepare_oracle import compact,binding,DECL,TOP,GET
if __name__=='__main__':
    o=load(Q/'PRE_RUN_EXPECTED_ORACLE.json');cases=o['prospective_cases'];assert len(cases)==6
    out=[]
    for i,c in enumerate(cases):
        b=c['expected_bundle4'];raw=c['expected_bundle_compact_UTF8_noLF']
        assert list(b)==TOP and binding(compact(b))==raw
        assert not raw['utf8_text'].endswith('\n') and raw['hex'].startswith('7B22')
        assert len(c['expected_pair_readonly4'])==4 and list(c['expected_pair_readonly4'])==GET
        for side,key in [('parent','independently_supplied_parent14_7'),('child','independently_supplied_child14_7')]:
            x=c[key];d=x['original_descriptor7'];assert list(d)==DECL
            assert len(x['config14'])==14 and len(x['receipt11'])==11 and len(x['snapshot15'])==15
            assert binding(compact(x['config14']))==x['raw_config']
            assert x['raw_config']['sha256']==d['expectedConfigSha256']==x['receipt11']['BoundConfigSha256']
            p=Path(d['expectedConfigPath']);assert p.is_relative_to(Q) and p.read_bytes()==x['raw_config']['utf8_text'].encode('utf-8')
            assert c['expected_bundle4'][side+'Declaration']==d
            assert c['expected_'+side.title()+'Declaration_fresh_original7']==d
            assert x['receipt11']['AdmittedAtUtc']==x['snapshot15']['IssuedAtUtc']==x['config14']['issuedAtUtc']
            # Every opaque original is independently expected without decoding copied actual output.
            assert x['receipt11']['BoundOriginId']==d['originId'] and x['receipt11']['BoundLaunchPlanId']==d['launchPlanId']
        if i>=4:
            assert all(k in c['operatorPairId_original'] for k in ['=','"','\\','Ω'])
            assert all(k in b['parentDeclaration']['originId'] for k in ['=','"','\\','Ω'])
            assert all(k in b['childDeclaration']['originId'] for k in ['=','"','\\','Ω'])
        assert len(c['full_ordered_type_map'])==206
        assert not Path(c['publisher_future_plan']['owned_output_root']).exists()
        out.append(dict(case_id=c['case_id'],expected_bundle_sha256=raw['sha256'],expected_bundle_bytes=raw['bytes'],typed_rows=206,phase_count=3,data_consistency_only=True,producer_candidate_calls=0))
    for p in load(Q/'PROSPECTIVE_INPUT_LITERAL_MANIFEST.json')['files']:
        assert pin(Path(p['path']))==p
    b=load(B)
    fixedobj=[p for p in b['files'] if Path(p['path']).is_relative_to(R/'scratch/WorkerBridgeMod/Source/obj')]
    assert len(fixedobj)==4
    write(Q/'PRESERVATION_HASH_SCOPE_NOTE.json',dict(at=now(),mandatory_baseline_fixed_generated_obj4=fixedobj,
      method='Hash-only preservation of immutable baseline entries; no semantic analysis or mutable R29 implementation read',
      no_blanket_zero_bytes_under_obj_claim=True,mutable7_excluded_unread=True,R29_new_publisher_source_and_bins_objects_not_read=True,
      authority='WP explicitly requires SHA-size before/after of all14105 baseline paths; fixed4 generated metadata are in that protected baseline, not approved mutable7'))
    write(Q/'NORMAL_DATA_CONSISTENCY_AUDIT.json',dict(at=now(),cases=out,total_typed_rows=1236,three_phase_graphs=18,literal_input_files=30,
       original_and_noLF_bundle_identity_checked=True,old_raw14_byte_exact_first4=True,own_fixture_locator_rebind_explicit=True,
       source_metadata_failure_preserved_and_corrected=True,future_publisher_root_not_created=True,
       executed_producer_compiler_candidate_native_adverse=0,kind='PREPARATION_DATA_CHECK_NOT_EXECUTABLE_TEST_PASS',R29_candidate_verdict='NOT_REVIEWED'))
    print(json.dumps(dict(normal_cases=6,typed_rows=1236,phase_graphs=18,literal_files=30,candidate_or_producer_execution=0,all_prospective_data_consistent=True)))

