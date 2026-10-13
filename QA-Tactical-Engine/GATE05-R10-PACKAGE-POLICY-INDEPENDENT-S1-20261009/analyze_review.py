from review_setup import *
import difflib,re

src=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
old=ROOT/'Dispatcher/CANDIDATES/G05R9-fbe8a43b/scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
def row(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def anchor(first,last):return dict(source=row(src),first_line=first,last_line=last)

if __name__=='__main__':
    assert not (Q/'INDEPENDENT_REVIEW_FINDINGS.json').exists()
    a=load(Q/'RUN1_ARCHIVE/NORMAL_RESULTS.json');b=load(Q/'NORMAL_RESULTS.json')
    assert len(a['results'])==len(b['results'])==135 and a['failed_assertions']==b['failed_assertions']==0
    pairs=[]
    names=[p.name for p in (Q/'RUN1_ARCHIVE').iterdir() if p.name.endswith('.canonical.json')]
    for n in names:
        x=Q/'RUN1_ARCHIVE'/n;y=Q/n;assert x.read_bytes()==y.read_bytes();pairs.append(dict(run1=row(x),run2=row(y),canonical_utf8_byte_equal=True))
    policies1=load(Q/'RUN1_ARCHIVE/PACKAGE_POLICY_RESULTS.json');policies2=load(Q/'PACKAGE_POLICY_RESULTS.json')
    assert policies1==policies2
    fields=load(Q/'DTO_FIELD_METADATA.json');assert len(fields)==len(load(Q/'RUN1_ARCHIVE/DTO_FIELD_METADATA.json'))
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json')
    for directory in [Q/'RUN1_ARCHIVE',Q]:
        for p in directory.glob('*.checks.json'):
            assert all(r['matched'] for r in load(p)),str(p)
        for p in directory.glob('*.semantic_checks.json'):
            assert all(r['matched'] for r in load(p)),str(p)
    fixed=[]
    for n in ['WorkerBridge.cs','WorkerBridge.csproj']:
        p=src.parent/n;o=old.parent/n;assert p.read_bytes()==o.read_bytes();fixed.append(dict(current=row(p),prior=row(o),matched=True))
    assert src.read_bytes()[:72547]==old.read_bytes()[:72547]
    diff=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),src.read_text(encoding='utf-8-sig').splitlines(True),fromfile=str(old),tofile=str(src)))
    (Q/'SOURCE_SCOPE_DIFF.txt').write_text(diff,encoding='utf-8')
    write(Q/'FIXED_SOURCE_SCOPE.json',dict(at=now(),files=fixed,prefix_bytes=72547,prefix_sha256=hashlib.sha256(src.read_bytes()[:72547]).hexdigest().upper(),prefix_match=True,source_diff=row(Q/'SOURCE_SCOPE_DIFF.txt'),production_changes_builds=0))
    findings=[
        dict(id='R10-QA-M01',master_mapping='R10-M01',disposition='CREDITED_STATIC_AND_SCOPED_POSITIVE_HELPER_PASS',anchors=[anchor(1843,1951),anchor(1953,2000),anchor(2859,2885)],finding='Distinct expected policy parameter and complete physical package list comparison are implemented. Observed RunningMods path invokes the same check before newly computed successful output;not derived expected list. Six fresh normal positive cases independently verify both digest/check overloads and supported admission. Actual Compute was not executed;operator origin is untested.'),
        dict(id='R10-QA-M02',master_mapping='R10-M02',disposition='STATIC_REVISION_REQUIRED_GENERAL_POLICY_ENCODING',anchors=[anchor(1815,1839),anchor(1697,1703),anchor(2945,2959)],finding='Digest accepts opaque string ID/revision/list using delimiter-only UTF8 concatenation and lowercased packages. No separate typed versioned policy schema/reconstructible canonical representation/escaping-length contract or input grammar is declared. Normal independently declared preimage hashes pass only for approved unpadded dot-ID cases. Manifest binding strings are trimmed independently of the declared digest/boundary;general identity normalization semantics remain unestablished.',negative_or_ambiguity_fixture_run=False),
        dict(id='R10-QA-M03',master_mapping='R10-M03',disposition='SCOPED_ALIGNED_ORDER_PASS_STATIC_REVISION_REQUIRED_GENERAL_ORDER_CONTRACT',anchors=[anchor(1906,1937),anchor(1647,1669),anchor(1988,1996)],finding='Check iterates physical activeMods list and package IDs without inspecting loadOrder. Supported helper checks before CanonicalNormalize sorts by loadOrder. Normal physical order aligned with sequential ordinal passes exact full comparisons,including order-only changed policy with unchanged ID/revision. Broader physical-versus-ordinal contract is not proved. No mismatch/tied/rejection runtime case.'),
        dict(id='R10-QA-M04',master_mapping='R10-M04',disposition='STRUCTURAL_HELPER_ONLY_NOT_PACKAGE_AUTHORITY',anchors=[anchor(2094,2137),anchor(1953,2000)],finding='ValidateContract and no-policy TryAdmitManifest are structural codec helpers. Embedded binding/status and nonempty digest are not distinct expected approval. Six separate-policy supported positive helper cases are stronger narrow evidence;neither synthetic helper nor digest proves authority installation.'),
        dict(id='R10-QA-M05',master_mapping='R10-M05',disposition='STATIC_REVISION_REQUIRED_POLICY_CACHE_BINDING_NATIVE_ORIGIN_UNTESTED',anchors=[anchor(1553,1603),anchor(1615,1630),anchor(2859,2885)],finding='Setter/getter clones and lock are visible. Configure/Clear change configured policy without cache invalidation or generation binding. GetActual returns cached fingerprint before Compute check. No configuration/cache/property execution;trusted operator installation,concurrency and cached policy lifecycle remain unverified.'),
        dict(id='R10-QA-M06',master_mapping='R10-M06',disposition='OTHER_MATERIAL_AND_NATIVE_GATES_OPEN',anchors=[anchor(1654,1662),anchor(1684,1696),anchor(2940,2942)],finding='Patch/settings disposition defaults and patch summary synchronization remain. Package matching cannot establish raw patch/settings exclusion,source child/native version availability,complete loaded census or operator/worker-validator authority. No global catalogue or C owner/schema/topology decision.')]
    write(Q/'INDEPENDENT_REVIEW_FINDINGS.json',dict(at=now(),source=row(src),findings=findings,master_findings_independently_qualified=True,offensive_or_rejection_reproductions=0,closure_changed=False))
    prep=ROOT/'QA-Tactical-Engine/GATE05-R10-PACKAGE-POLICY-PREP-S1-20261009'
    nd={
        'N01':('SCOPED_PASS','Six separate expected/actual normal helper cases;all result fields and complete observed IDs/ordinals'),
        'N02':('SCOPED_PASS_GENERAL_REPRESENTATION_OPEN','Equal independent literal declarations and independently computed normal preimage/digest;no candidate canonical policy bytes API exists'),
        'N03':('SCOPED_PASS','Revision-only change with fixed policyId/list and full binding checks'),
        'N04':('SCOPED_PASS','PolicyId-only change with fixed revision/list and full binding checks'),
        'N05':('SCOPED_ALIGNED_ORDER_PASS_GENERAL_ORDER_OPEN','Order-only case fixed ID/revision;direct entire order+ordinal checks. Generic physical-vs-loadOrder contract static-qualified'),
        'N06':('SCOPED_PASS','Alternate normal complete matching list;full semantics and binding'),
        'N07':('PARTIAL_NORMAL_PREIMAGE_PASS_STATIC_REVISION_REQUIRED','Independent UTF8 delimiter preimage/digest only;typed schema/candidate canonical reconstruction API unimplemented'),
        'N08':('SCOPED_PASS','CheckPackagePolicy and TryAdmitWithPackagePolicy supported positive cases only;actual loaded approval untested'),
        'N09':('SCOPED_PASS','Six version target cases across five views/12 generic cases in each new process'),
        'N10':('SCOPED_PASS','65 historical representative leaves;full BASE/current fields float32/int64/string/order checks,not all native content'),
        'N11':('SCOPED_NORMAL_PASS_GENERAL_NORMALIZATION_OPEN','Unpadded normal policy IDs/revision/digest and caller changes fully checked;undefined trimming not executed'),
        'N12':('SCOPED_PASS','Own finalbuild1,freshprocess2,135PASS each,pre/post116 each/allactual loaded12 pinned,32canonical pairs')}
    normal=[]
    for r in load(prep/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json')['rows']:
        status,detail=nd[r['id']];normal.append(dict(preparation_criterion=r,disposition=status,evidence=detail))
    static_map={'S01':'M01','S02':'M02','S03':'M03','S04':'M04','S05':'M01','S06':'M01/M05','S07':'M05','S08':'M05','S09':'M02/M03/M06','S10':'M02/M04','S11':'M06','S12':'M06','S13':'FIXED_SOURCE_SCOPE','S14':'NEW_EXECUTION_GRAPH'}
    static=[dict(preparation_criterion=r,independent_mapping=static_map[r['id']],disposition='DEFENSIVE_STATIC_REVIEWED_WITH_EXPLICIT_FINDING_LIMITS',runtime_branch_executed=False) for r in load(prep/'STATIC_REVIEW_CRITERIA.json')['rows']]
    write(Q/'CRITERIA_DISPOSITION.json',dict(at=now(),normal=normal,static=static,normal_criteria=len(normal),static_criteria=len(static),all_criteria_not_blanket_pass=True))
    producer=FROZEN/'scratch/EngineGate05R10PackagePolicy';program=producer/'Harness/Program.cs';text=program.read_text(encoding='utf-8-sig');result=load(producer/'results.json');raw=(producer/'raw_console.txt').read_text(encoding='utf-8-sig');pre=load(producer/'CANDIDATE_PRE_RUN_MANIFEST.json')
    descriptions=[
      'Float2/double2 FormatLossless parse equality only;not every content codec numeric field',
      'Three normal activeMods loadOrder/package placements after Normalize;no duplicated mod entries',
      'Two ThingDefs and two JobDefs normal sorting;not all native families',
      'Nonempty JSON/non-null reconstructed plus schema/contract/buildIdentity and three counts;not every typed field',
      'PatchCount5+8 synchronized to13;not provenance/noninterference approval',
      'Same process,culture switching on already normalized shared instance;not fresh processes',
      'Three assembly entries package/name expected placement;not complete identity fields',
      'Three verb ranges and Comp sequence/count including repeat;not all verbClass fields',
      'Three stage minSeverity values/count;not all stage labels',
      'Representative fixture positive ValidateContract;no DefDatabase observation',
      'Positive structural TryAdmit return/nonempty JSON/empty reason;no distinct policy or full decoded semantics',
      'One changed research baseCost yields distinct JSON/hash;not general collision breadth',
      'Schema/contract/coverage/status constants and required fixture flags;not loaded native content',
      'Assembly package/name placement;does not test stats despite description',
      'Default UNCONFIGURED plus producer legacy rejection predicate;outside allowed positive scope,not rerun',
      'Three version meanings,culture switch same process,Serialize(true) after Normalize;independent QA adds fresh original true',
      'Case-insensitive equal normal policies,order-only and revision-only digest changes;no independent expected digest/preimage,no policyId-only assertion or policy canonical serialization despite label',
      'Positive status/count/boundary and alternate helper portions;limited decoded content/binding checks. Contains out-of-scope negative portion preserved,not reproduced',
      'Configuration/property lifecycle/snapshot APIs;outside admitted pure-positive scope,not executed by QA']
    labels=re.findall(r'RunTest\("(TC\d+_[^"]+)"',text);assert len(labels)==19 and labels==[r['test_id'] for r in result['results']]
    rows=[]
    for i,(label,desc) in enumerate(zip(labels,descriptions)):
        assert label in raw;line=next(j+1 for j,s in enumerate(text.splitlines()) if 'RunTest("'+label+'"' in s)
        rows.append(dict(test_id=label,source_line=line,producer_status=result['results'][i]['status'],predicate_scope=desc,independently_reexecuted=False,scope_deviation=i+1 in [15,18,19]))
    write(Q/'PRODUCER_COVERAGE_AND_PACKAGING.json',dict(at=now(),source=row(program),raw=row(producer/'raw_console.txt'),results=row(producer/'results.json'),pre_run=row(producer/'CANDIDATE_PRE_RUN_MANIFEST.json'),label_count=19,label_source_result_raw_identity_matched=True,rows=rows,producer_pre_run_id=pre['run_id'],producer_result_run_id=result['run_id'],pre_result_run_id_equal=pre['run_id']==result['run_id'],chronology_complete=False,packaging_gaps=['Pre-run ID differs from results actual run_id','Producer graph does not provide complete independently bound numeric build/run exits/compiler/framework/resolved actual hashes/semantic artifacts;QA prospective graph does not repair producer history','Post-completion freeze is not independent pre-execution chronology','ProducerTC15/18negative+TC19configuration scope deviations preserved;no rerun or permission inheritance'],producer_execution_by_qa=0))
    summary=dict(at=now(),verdict='SCOPED_NORMAL_PACKAGE_CODEC_HELPERS_PASS_STATIC_REVISION_REQUIRED_NATIVE_UNTESTED',generic_cases=12,package_cases=6,targeted_version_cases=6,explicit_runner_package_digest_overload_calls_per_run=12,explicit_runner_check_overload_calls_per_run=12,positive_supported_admission_calls_per_run=6,structural_validate_calls_per_run=2,structural_try_admit_calls_per_run=2,qa_runner_builds=1,processes=2,assertions_per_run=[len(a['results']),len(b['results'])],failed_assertions=[0,0],actual_build_exit=load(Q/'BUILD_TOOL_PROOF.json')['exit_code'],actual_run_exits=[load(Q/'RUN1_TOOL_PROOF.json')['exit_code'],load(Q/'RUN2_TOOL_PROOF.json')['exit_code']],canonical_crossprocess_pairs=len(pairs),pair_categories=dict(generic=12,fresh_original_true=12,structural_admitted=2,supported_package_admitted=6),pairs=pairs,policy_observations_crossprocess_equal=True,historical_leaves=65,base_semantic_leaves=len(load(Q/'BASE.semantic_checks.json')),dto_metadata_fields=len(fields),pinned_input_files_per_run=[len(load(Q/f'PRE_RUN{i}_MANIFEST.json')['files']) for i in [1,2]],actual_loaded_pre_pin_matched=True,selected_sha256=sha(FROZEN/'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'),selected_mvid='7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb',runner=load(Q/'PRE_RUN1_MANIFEST.json')['runner'],production_modify_builds=0,configuration_cache_provider_native_game_operator_runs=0,old_runner_negative_rejection_tied_ambiguity_adverse_runs=0,closure_changed=False,runtime_e2_released=False,foundation='HOLD')
    assert len(pairs)==32
    write(Q/'INDEPENDENT_EXECUTION_SUMMARY.json',summary)
    print(json.dumps({k:summary[k] for k in ['verdict','assertions_per_run','canonical_crossprocess_pairs','base_semantic_leaves','dto_metadata_fields','actual_run_exits']},indent=2))
