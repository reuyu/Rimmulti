from review_setup import *
import difflib,re

SOURCE=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
OLD=ROOT/'Dispatcher/CANDIDATES/G05R10-81a28ecb/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
def anchor(first,last):return dict(source=row(SOURCE),first_line=first,last_line=last)

if __name__=='__main__':
    assert not (Q/'INDEPENDENT_EXECUTION_SUMMARY.json').exists()
    one=load(Q/'RUN1_ARCHIVE/NORMAL_RESULTS.json');two=load(Q/'NORMAL_RESULTS.json');assert len(one['results'])==len(two['results'])==247 and one['failed_assertions']==two['failed_assertions']==0
    pairs=[]
    for p in sorted((Q/'RUN1_ARCHIVE').glob('*.canonical.json')):
        other=Q/p.name;assert p.read_bytes()==other.read_bytes();pairs.append(dict(run1=row(p),run2=row(other),canonical_utf8_equal=True))
    assert len(pairs)==71
    policies1=load(Q/'RUN1_ARCHIVE/POLICY_ENCODING_RESULTS.json');policies2=load(Q/'POLICY_ENCODING_RESULTS.json');assert policies1==policies2 and len(policies2)==15
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json');reference_bindings=[]
    for name,c in oracle['policy_cases'].items():
        for folder in [Q/'RUN1_ARCHIVE',Q]:
            actual=folder/(name+'.policy.canonical.json');assert actual.read_bytes()==Path(c['reference']['path']).read_bytes();assert sha(actual)==c['expected_digest']
            reference_bindings.append(dict(case_id=name,actual=row(actual),independent_reference=c['reference'],matched=True,selected_before_calls=True))
    typed_count=0;typed_files=[]
    def checks(value):
        if isinstance(value,dict):
            if 'matched' in value and 'expected' in value and 'actual' in value:yield value
            for v in value.values():yield from checks(v)
        elif isinstance(value,list):
            for v in value:yield from checks(v)
    for folder in [Q/'RUN1_ARCHIVE',Q]:
        for p in folder.glob('*.json'):
            if p.name.endswith(('checks.json','check_results.json')) or p.name=='HISTORICAL65_FIELD_RESULTS.json':
                rows=list(checks(load(p)));assert all(r['matched'] for r in rows),str(p)
                if rows:typed_count+=len(rows);typed_files.append(dict(file=row(p),typed_checks=len(rows),all_matched=True))
    process=[]
    for i in [1,2]:
        raw=(Q/f'RUN{i}_RAW.txt').read_text(encoding='utf-8-sig');pre=load(Q/f'PRE_RUN{i}_MANIFEST.json');m=re.search(r'Culture=([^\s]+) Runtime=([^\s]+) ProcessId=(\d+)',raw)
        assert m and m.group(1)==pre['culture'] and pre['run_id'] in raw
        process.append(dict(run_id=pre['run_id'],culture=m.group(1),runtime=m.group(2),process_id=int(m.group(3)),raw=row(Q/f'RUN{i}_RAW.txt')))
    assert process[0]['process_id']!=process[1]['process_id'];write(Q/'FRESH_PROCESS_PROOF.json',dict(at=now(),rows=process,distinct_process_ids=True,game_native_validator=False))
    fixed=[]
    for name in ['WorkerBridge.cs','WorkerBridge.csproj']:
        a=SOURCE.parent/name;b=OLD.parent/name;assert a.read_bytes()==b.read_bytes();fixed.append(dict(current=row(a),prior=row(b),matched=True))
    assert SOURCE.read_bytes()[:72547]==OLD.read_bytes()[:72547]
    (Q/'SOURCE_SCOPE_DIFF.txt').write_text(''.join(difflib.unified_diff(OLD.read_text(encoding='utf-8-sig').splitlines(True),SOURCE.read_text(encoding='utf-8-sig').splitlines(True),fromfile=str(OLD),tofile=str(SOURCE))),encoding='utf-8')
    write(Q/'FIXED_SOURCE_SCOPE.json',dict(at=now(),files=fixed,prefix_bytes=72547,prefix_sha256=hashlib.sha256(SOURCE.read_bytes()[:72547]).hexdigest().upper(),prefix_match=True,diff=row(Q/'SOURCE_SCOPE_DIFF.txt'),production_modify_builds=0))
    findings=[
      dict(id='R11-QA-M01',mapping='R11-M01',disposition='CREDITED_SCOPED_CURRENT_POLICY_ENCODING_AND_OPAQUE_BINDING_PASS',anchors=[anchor(1703,1708),anchor(1821,1917),anchor(1959,1970),anchor(2076,2114)],finding='Fixed-field current policy JSON and documented literal Unicode escape convention matches independently selected before-call bytes/SHA in15 normal declarations. All declaration/record/scalar digest overloads,current-schema conversions,four matching checks,two supported admissions verify opaque whitespace/case/Unicode/revision text and full typed content/caller state. Delimiter join and ID/revision Trim removed. Not a general collision/injectivity or native authority guarantee.'),
      dict(id='R11-QA-M02',mapping='R11-M02',disposition='STATIC_QUALIFIED_GENERAL_SCHEMA_CARRIER_OPEN',anchors=[anchor(1851,1879),anchor(2030,2053),anchor(3059,3112)],finding='Declaration.schemaVersion is writable. Serializer uses supplied nonempty schema;general DTO deserializer does not enforce a closed supported schema. ToRecord omits schema and record.ToDeclaration restores current constant. Check/result/disposition have no separate schema carrier. Exact supported WE-PACKAGE-POLICY-V1 roundtrip/parity/digest passes;other schema handling and provenance remain static OPEN. No unknown-schema/missing-required/rejection fixture or execution.'),
      dict(id='R11-QA-M03',mapping='R11-M03',disposition='GENERAL_ORDER_CACHE_MATERIAL_NATIVE_SEPARATE_OPEN',anchors=[anchor(1647,1675),anchor(1982,2016),anchor(1553,1629),anchor(1690,1702)],finding='Physical-list package check versus loadOrder sorting remains;normal aligned ordinal/ID comparisons pass only scoped fixtures. Policy/cache generation/operator installation and patch/settings summary/source/native coverage remain unresolved. Configuration/properties/cache/provider/actualCompute/game/native/operator not invoked. Structural helper/embedded ADMITTED/digest is not expected approval authority.'),
      dict(id='R11-QA-M04',mapping='R11-M04',disposition='PRODUCER_PACKAGING_REVISION_REQUIRED_ORIGINAL_JSON_INVALID',anchors=[],finding='Frozen producer release JSON is syntactically invalid. Original hash/raw preserved;admission relies on Master independently observed identity sidecar. New QA cannot certify producer release/chronology or repair original bytes.'),
      dict(id='R11-QA-M05',mapping='R11-M05',disposition='PRODUCER_PREDICATE_GRAPH_QUALIFIED_NEW_QA_ONLY',anchors=[],finding='14 producer labels match source/result/raw,limited positive predicates only. Pre-run/results IDs differ;actual complete prospective build/process/toolchain/loaded dependency/input-oracle graph is established for new QA only. Producer raw UTF16LE BOM decoded explicitly without changing original.')]
    write(Q/'INDEPENDENT_REVIEW_FINDINGS.json',dict(at=now(),source=row(SOURCE),findings=findings,unknown_schema_adverse_reproductions=0,full_gate_e2_released=False,closure_changed=False))
    normal=load(PREP/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json');static=load(PREP/'STATIC_REVIEW_CRITERIA.json')
    normal_rows=[]
    for r in normal['rows']:
        qualification='SUPPORTED_CURRENT_VERSION_NORMAL_SCOPE_PASS'
        if r['id'] in ['N01','N10','N11']:qualification+=' / GENERAL_SCHEMA_CARRIER_STATIC_OPEN'
        if r['id']=='N05':qualification+=' / GENERAL_ORDINAL_ADMISSION_OPEN'
        detail='Direct independent bytes/SHA,typed outputs and recorded caller state in new current-version normal cases;see policy/codec artifacts'
        if r['id']=='N12':detail='Generic codec false/explicitNormalize/fresh-originaltrue/reconstruction on separate instances;new opaque binding is checked before/after supported helper plus reconstructed content serialization. Admission internally normalizes before output;not represented as a pre-Normalize policy-bearing fresh-originaltrue control.'
        normal_rows.append(dict(preparation_criterion=r,disposition=qualification,evidence=detail))
    static_rows=[dict(preparation_criterion=r,disposition='DEFENSIVE_STATIC_REVIEWED_WITH_EXPLICIT_GENERAL_SCHEMA_ORDER_CACHE_NATIVE_LIMITS',runtime_adverse_branch_executed=False) for r in static['rows']]
    write(Q/'CRITERIA_DISPOSITION.json',dict(at=now(),normal=normal_rows,static=static_rows,normal_criteria=14,static_criteria=14,no_blanket_scope_pass=True))
    producer=FROZEN/'scratch/EngineGate05R11PolicyEncoding';program=producer/'Harness/Program.cs';source=program.read_text(encoding='utf-8-sig');result=load(producer/'results.json');pre=load(producer/'CANDIDATE_PRE_RUN_MANIFEST.json');rawpath=producer/'raw_console.txt';blob=rawpath.read_bytes();assert blob.startswith(b'\xff\xfe');raw=blob[2:].decode('utf-16le')
    labels=list(re.finditer(r'RunTest\(report, "(TC[^"]+)"',source));assert len(labels)==14
    assert [m.group(1) for m in labels]==[r['test_id'] if 'test_id' in r else r['id'] for r in result['test_cases']]
    descriptions=[
      'One literal expected compact JSON/fixed key order/schema for ASCII normal declaration;independent literal is narrow credit',
      'Schema/ID/revision/every fixture package plus serialized reconstruction;normal policy roundtrip only',
      'Equal instances/digest length and SHA computed from candidate serialization,not a pre-built independent byte oracle',
      'Ordinary ID spaces/revision tabs roundtrip and digest equality;not full admitted content binding',
      'Unicode/punctuation quote/backslash escape substrings and opaque roundtrip;not all JSON escape convention cases',
      'Mixed-versus-lower package serialization/digest equality;normal case rule only',
      'Isolated normal ID/revision/order and pure declaration multiplicity differences;not universal collision resistance or duplicate admission',
      'Three digest overloads equal;no independent expected canonical bytes in this predicate',
      'Matching success/status/ID/revision/digest/counts;not every list ordinal/element or full content',
      'Matching return/nonempty plus selected disposition/boundary fields;not full decoded content/caller state',
      'Two opaque disposition fields after Normalize;not all content transport views',
      'R11 contract/fixture flag and positive admission/Validate;not actual loaded native profile',
      'Null/empty/known modVersion values after canonical codec;not independently all compatibility/reverse/fresh original views',
      'Two ThingDefs/two Hediffs sorting;not eight-family/full native material semantics']
    rows=[]
    for m,desc in zip(labels,descriptions):
        assert m.group(1) in raw;rows.append(dict(test_id=m.group(1),source_line=source[:m.start()].count('\n')+1,predicate_scope=desc,producer_reexecuted=False))
    release=FROZEN/'docs/RELEASE_MANIFEST_ENGINE_GATE05_R11_POLICY_ENCODING.json';assert sha(release)=='290507994A0E13A3A8F04F77637F240F3C7F55E63308E387B216831219AA8F80'
    try:load(release);raise AssertionError('Expected original malformed JSON not observed')
    except json.JSONDecodeError as error:parse=dict(error=str(error),line=error.lineno,column=error.colno,position=error.pos)
    write(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json',dict(at=now(),source=row(program),raw=row(rawpath),raw_encoding='UTF16LE_BOM',raw_original_preserved=True,results=row(producer/'results.json'),pre_run=row(producer/'CANDIDATE_PRE_RUN_MANIFEST.json'),release_original=row(release),release_json_valid=False,release_parse_error=parse,master_admission_sidecar=row(ADMISSION),rows=rows,label_count=14,source_result_raw_labels_matched=True,producer_pre_run_id=pre['run_id'],producer_result_run_id=result['run_id'],pre_result_run_id_equal=pre['run_id']==result['run_id'],producer_culture=result['culture'],packaging_revision_required=True,producer_old_chronology_certified_by_new_qa=False,producer_runner_executed_by_qa=0,limitations=['Additional culture result files/labels do not establish complete actual process numeric exits/prepin/toolchain/loaded hashes/input literal oracle','Post-completion frozen identity is not before-run chronology','Invalid release original not fixed or replaced;structured Master admission is separate']))
    summary=dict(at=now(),verdict='SCOPED_CURRENT_POLICY_ENCODING_OPAQUE_BINDING_CODEC_PASS_SCHEMA_STATIC_QUALIFIED_PACKAGING_REVISION_REQUIRED_NATIVE_UNTESTED',generic_cases=12,policy_cases=15,targeted_version_cases=6,qa_runner_builds=1,candidate_runner_processes=2,assertions_per_run=[247,247],failed_assertions_per_run=[0,0],actual_build_exit=load(Q/'BUILD_TOOL_PROOF.json')['exit_code'],actual_run_exits=[load(Q/'RUN1_TOOL_PROOF.json')['exit_code'],load(Q/'RUN2_TOOL_PROOF.json')['exit_code']],canonical_crossprocess_pairs=71,pair_categories=dict(generic=12,fresh_original_true=12,structural_admitted=2,policy_declaration=15,matching_record_admitted=15,matching_declaration_admitted=15),pairs=pairs,independent_policy_reference_bindings=reference_bindings,typed_checks=typed_count,typed_files=typed_files,policy_typed_observations_crossprocess_equal=True,historical_leaf_count=65,base_semantic_leaves=len(load(Q/'BASE.semantic_checks.json')),policy_admitted_semantic_leaves=[r['admissions'][0]['semantic_leaves'] for r in policies2],runner=load(Q/'PRE_RUN1_MANIFEST.json')['runner'],actual_processes=process,pinned_files_per_run=[len(load(Q/f'PRE_RUN{i}_MANIFEST.json')['files']) for i in [1,2]],loaded_managed_per_run=12,all_loaded_pre_pins_matched=True,explicit_runner_calls_per_run=dict(policySerialize=45,policyDeserialize=15,EscapeJsonString=30,digestOverloads=45,ToRecord=30,ToDeclaration=30,matchingCheck=60,matchingTryAdmit=30,structuralValidate=2,structuralTryAdmit=2),call_count_scope='Explicit runner source call sites only,nested pure calls not instrumented',selected_sha256=sha(FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'),selected_mvid='e6c6f6fd-2915-4493-8ef9-dc5d87de1c6b',production_modify_builds=0,configuration_cache_provider_native_game_operator_old_negative_rejection_tied_unknownschema_ambiguity_adverse=0,new_closure=False,full_gate_e2_released=False,foundation='HOLD')
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',summary)
    print(json.dumps({k:summary[k] for k in ['verdict','canonical_crossprocess_pairs','typed_checks','base_semantic_leaves','assertions_per_run','actual_run_exits']},indent=2))
