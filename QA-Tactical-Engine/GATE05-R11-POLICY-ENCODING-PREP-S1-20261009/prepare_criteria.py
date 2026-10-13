from review_setup import *
import copy

def ref_json(decl,ascii_escape):
    return json.dumps(decl,ensure_ascii=ascii_escape,separators=(',',':'),allow_nan=False).encode('utf-8')

if __name__=='__main__':
    assert not (Q/'NORMAL_REFERENCE_ORACLE.json').exists()
    # Every expected list and observed inventory is separately declared here.
    cases=[
      ('BASE','qa.policy.primary','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('EQUAL_SEPARATE','qa.policy.primary','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('ID_ONLY','qa.policy.alternate','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('REV_ONLY','qa.policy.primary','8',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('ORDER_ONLY','qa.policy.primary','7',['example.material','Example.Core'],['EXAMPLE.MATERIAL','example.core']),
      ('UNICODE_ID','정책.é.🌱','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('UNICODE_REV','qa.policy.primary','개정.é.e\u0301.🌱',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('DISPLAY_ID','정책 "표시" \\ route\t줄\nnext /','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('DISPLAY_REV','qa.policy.primary','rev "07" \\ notes\t단계\r\n끝',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('SPACED_ID',' qa.policy.primary ','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('SPACED_REV','qa.policy.primary',' 007 ',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('CASE_ID','QA.Policy.Primary','7',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('REV_NUMERIC_TEXT','qa.policy.primary','007',['Example.Core','example.material'],['example.core','EXAMPLE.MATERIAL']),
      ('PACKAGE_CASE_LOWER','qa.policy.primary','7',['example.core','example.material'],['EXAMPLE.CORE','example.material'])]
    variants={
      'LITERAL_UNICODE_MINIMAL':dict(non_ascii='Literal Unicode UTF8 including supplementary characters',ensure_ascii=False,quote_backslash='JSON backslash escapes',ordinary_controls='short escapes for b/f/n/r/t,other U+0000..001F lowercase four-digit u escape',forward_slash='literal /',hex_escape_case='lowercase',format='compact fixed key order,no BOM',adopted_candidate_convention=False),
      'ASCII_UNICODE_ESCAPED':dict(non_ascii='ASCII JSON Unicode escapes,lowercase four-digit u and supplementary surrogate pair',ensure_ascii=True,quote_backslash='JSON backslash escapes',ordinary_controls='short escapes for b/f/n/r/t,other U+0000..001F lowercase four-digit u escape',forward_slash='literal /',hex_escape_case='lowercase',format='compact fixed key order,no BOM',adopted_candidate_convention=False)}
    out={};ref_dir=Q/'normal_references';ref_dir.mkdir()
    for name,pid,rev,expected_ids,actual_ids in cases:
        raw_policy=dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId=pid,revision=rev,admittedPackageIds=expected_ids)
        # Canonical package normalization is specified;opaque ID/revision are exact text.
        decl=dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId=pid,revision=rev,admittedPackageIds=[x.lower() for x in expected_ids])
        actual=[dict(loadOrder=i,packageId=p) for i,p in enumerate(actual_ids)]
        refs={}
        for variant,details in variants.items():
            blob=ref_json(decl,details['ensure_ascii']);p=ref_dir/(name+'.'+variant+'.canonical.utf8.json');p.write_bytes(blob)
            decoded=json.loads(blob.decode('utf-8'));assert decoded==decl and list(decoded)==['schemaVersion','policyId','revision','admittedPackageIds'];assert not blob.startswith(b'\xef\xbb\xbf')
            refs[variant]=dict(reference=row(p),expected_sha256=hashlib.sha256(blob).hexdigest().upper(),utf8_hex=blob.hex(),decoded_expected=decl,expected_typed_binding=dict(schemaVersion='WE-PACKAGE-POLICY-V1',policyId=pid,revision=rev,policyDigest=hashlib.sha256(blob).hexdigest().upper()),status='REFERENCE_PREPARATION_NOT_CANDIDATE_OBSERVATION')
        out[name]=dict(expected_input=raw_policy,expected_canonical_declaration=decl,separate_observed_inventory_literal=actual,expected_opaque_utf16le_hex=dict(policyId=pid.encode('utf-16le').hex(),revision=rev.encode('utf-16le').hex()),expected_opaque_codepoints=dict(policyId=[ord(c) for c in pid],revision=[ord(c) for c in rev]),references=refs,matching_normal_inventory=True,actual_not_used_to_construct_expected=True)
    relations=[('BASE','EQUAL_SEPARATE','EQUAL'),('BASE','PACKAGE_CASE_LOWER','EQUAL'),('BASE','ID_ONLY','DIFFERENT_ID_ONLY'),('BASE','REV_ONLY','DIFFERENT_REVISION_ONLY'),('BASE','ORDER_ONLY','DIFFERENT_ORDER_ONLY'),('BASE','CASE_ID','DIFFERENT_OPAQUE_CASE_ONLY'),('BASE','REV_NUMERIC_TEXT','DIFFERENT_OPAQUE_REVISION_STRING'),('BASE','SPACED_ID','DIFFERENT_OPAQUE_ID_WHITESPACE'),('BASE','SPACED_REV','DIFFERENT_OPAQUE_REVISION_WHITESPACE')]
    reference_relations=[]
    for a,b,relation in relations:
        for variant in variants:
            equal=out[a]['references'][variant]['expected_sha256']==out[b]['references'][variant]['expected_sha256'];assert equal==(relation=='EQUAL')
            reference_relations.append(dict(left=a,right=b,variant=variant,expected_relation=relation,reference_bytes_and_digest_equal=equal,candidate_observed=False))
    write(Q/'NORMAL_REFERENCE_ORACLE.json',dict(at=now(),scope='Reference JSON/hash preparation only,not candidate tests',normative_declared_key_order=['schemaVersion','policyId','revision','admittedPackageIds'],normative_schemaVersion='WE-PACKAGE-POLICY-V1',digest='Uppercase SHA256 of chosen documented compact canonical JSON UTF8,noBOM;digest excluded from declaration input',opaque_identity='Exact ordinal string meaning,including whitespace/case/Unicode codepoints;noTrim/casefold/parse-as-number/normalization',normal_package_ids='ASCII normal dot IDs,invariantlowercase declaration;order/multiplicity retained,not sorted/deduped',variants=variants,cases=out,reference_relations=reference_relations,reference_case_count=len(out),reference_byte_files=2*len(out),concrete_r11_api_and_escape_convention='UNOBSERVED_PENDING_FUTURE_FREEZE',controls_executed=0,runner_builds_processes=0))
    decisions=[
      'Read exact future frozen source/report specification and Master adoption before selecting one concrete escape convention;do not choose whichever variant matches candidate output after a failure',
      'Confirm literal versus escaped non-ASCII/supplementary Unicode,slash and HTML-sensitive handling,short-control versus u escapes and hexadecimal case;if neither prepared variant matches adopted documented grammar,create a new prospective reference before any build/run',
      'Confirm exact four key order and schemaVersion,string revision,no digest field,no BOM,compact formatting,lowercase normal packages and preserved ordered sequence',
      'Resolve concrete policy DTO and pure Serialize/Deserialize API and returned check/admission/content binding field map after admission;do not invent API names or schema field carrier now',
      'Raw supplied package spelling may be carried diagnostically;canonical list meaning is lowercase ordered IDs. Exact raw-versus-normalized returned list spelling must be explicitly mapped before future assertions',
      'Only normal matching fully declared helper fixtures after separate admission. Declaration sequence/multiplicity semantics do not close broader loadOrder/physical order admission;do not create tied/duplicate/rejection fixtures',
      'Legacy composed boundary is corroborating label;assert typed schema/opaqueID/revision/digest through normal Check/admission/codec and independently record caller mutation',
      'General order/cache/native/operator/patch-settings remain separate source-only OPEN;no competing A task or scheduler/governance edit']
    write(Q/'ESCAPE_CONVENTION_DECISION_CRITERIA.json',dict(at=now(),criteria=decisions,future_selection_status='NOT_SELECTED_NO_R11_INSPECTION',candidate_digest_verified=False,reference_hashes_only=True))
    normal_specs=[
      ('N01','Typed schema/fixed representation','BASE','Four keys exact order and types/schemaVersion;digest excluded from canonical input;compact UTF8/noBOM'),
      ('N02','Independent equal instances','BASE/EQUAL_SEPARATE','Equal reference bytes/digest and separate construction;typed identity equal'),
      ('N03','Opaque ID-only change','BASE/ID_ONLY/CASE_ID','Exact ordinal ID changed,revision/list fixed;bytes/digest/binding differ;no case fold'),
      ('N04','Opaque revision-only change','BASE/REV_ONLY/REV_NUMERIC_TEXT','Revision string exact,ID/list fixed;007 distinct from7,no number parsing'),
      ('N05','Order-only change','BASE/ORDER_ONLY','SameID/revision,exact ordered canonical list and digest differ;actual inventory independently matching'),
      ('N06','Unicode identity','UNICODE_ID/UNICODE_REV','Exact BMP/supplementary and combining-codepoint sequence retained,no Unicode normalization'),
      ('N07','Quoted/control display text','DISPLAY_ID/DISPLAY_REV','Quotes/backslash/tab/CR/LF roundtrip exact;chosen documented escape reference bytes'),
      ('N08','Leading/trailing whitespace','SPACED_ID/SPACED_REV','NoTrim of ID/revision at declaration/check/admission/content serialization;UTF16 ordinal sequence exact'),
      ('N09','Normal package case','BASE/PACKAGE_CASE_LOWER','Canonical lowercased package list/order exact,equal reference bytes/digest;opaque identity remains exact'),
      ('N10','Policy roundtrip/reconstruction','Allnormalcases','Deserialize returns typed schema/ID/revision/list;reserialize chosen convention reproduces reference bytes,not status/count alone'),
      ('N11','Check/admission/full binding','Separatefullydeclaredmatchingpositivefixtures','All returned schema/ID/revision/digest/list/ordinal/meaning and full admitted content compared with predeclared oracle;raw returned list contract reconciled before execution'),
      ('N12','Caller mutation and lossless content binding','Normalfreshinstances','Pure serialization/check and admission caller changes recorded separately;fresh-originaltrue/explicitNormalize/false transport preserve declared opaque identity'),
      ('N13','R9/current content regression','Futurefreshgeneric+supportedcontrols','Unknown/null/empty/known-distinct/reverse meanings,65/current floatbits/int32/largeInt64/Unicode/ordered content multiplicity;no nativeallfieldclaim'),
      ('N14','Prospective exact evidence graph','FutureMasteradmittedcandidate','Chosen escape oracle before finalbuild,en-US/de-DEfreshprocesses,typed meaning then bytes/digest;actual numeric exits/prepost/loaded sourcePDB graph')]
    write(Q/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json',dict(at=now(),rows=[dict(id=i,topic=t,reference_case=c,exact_expected_assertion=e,status='PLANNED_NOT_EXECUTED',candidate_admission='FUTURE_MASTER_FREEZE_REQUIRED') for i,t,c,e in normal_specs],controls_executed=0))
    static_specs=[
      ('S01','Concrete typed versioned declaration','Exactly four normative keys and policy schema version;digest not part of declaration input'),
      ('S02','Documented canonical string escaping','Deterministic lossless encoding across culture;explicit convention selected before oracle/build'),
      ('S03','Same canonical digest routing','Both digest overloads route through same declared canonical policy bytes rather than delimiter join'),
      ('S04','Opaque identity exactness','NoTrim/casefold/numericparse/Unicode normalization throughout policy-related paths'),
      ('S05','Package identity/order representation','Normal invariantlowercase IDs;canonical declaration not sorted/deduped;broader admission order remains OPEN'),
      ('S06','Independent expected origin','Expected declaration separately supplied,not generated from actual/embedded status;no operator origin fromdigest'),
      ('S07','Typed full returned binding','Schema/ID/revision/digest/list matches same canonical declaration throughCheck/admission/contentcodec;legacyboundary corroborating only'),
      ('S08','Caller mutation/normalization scope','Policy-specific meaning preserved without broad unrelated content normalization rewrite'),
      ('S09','Actual Compute linkage static','Trace existing RunningMods/check before newly computed success statically;no provider call or runtime claim'),
      ('S10','General ordinal/order deferred','Physical array/loadOrder contract remains separate;no mismatch/tied/unsupported fixture'),
      ('S11','Cache/operator deferred','Policy generation/native configuration provenance remains separate;no configuration/cache API read or run'),
      ('S12','Patch/settings material deferred','No exclusion/noninterference certification from canonical policy correction'),
      ('S13','Frozen scope and history','Worker/csproj/72547prefix fixed,diff explicit;oldR8FAIL/R9historicalclosure/oldQA preserved'),
      ('S14','Exact new evidence admission','Future candidate exactSHA/MVID/PDB/source before independent execution,no producerchronology/inheritedPASS')]
    write(Q/'STATIC_REVIEW_CRITERIA.json',dict(at=now(),rows=[dict(id=i,topic=t,predicate=e,mode='DEFENSIVE_STATIC_ONLY',status='PLANNED_NOT_R11_CANDIDATE_REVIEWED') for i,t,e in static_specs],forbidden_branch_fixtures=0))
    source=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs';assert sha(source)=='E855F60CB91F1207A03530842F65A6CECCEEA5B5DFF01511B86821AD2600D6AC'
    field_specs=[('CanonicalNormalize policyId.Trim','String',1697,1703),('CanonicalNormalize revision.Trim','String',1697,1703),('CanonicalNormalize policyDigest/status.Trim','String',1697,1703),('Content codec JSON Serialize/Deserialize','ContentProfileManifest JSON',1790,1813),('Policy digest record overload','ExpectedPackagePolicyRecord',1815,1820),('Policy digest delimiter UTF8 preimage','String ID/revision+IEnumerable<String>',1821,1839),('Check typed result identity/list','PackagePolicyCheckResult',1883,1892),('Check physical list/order','List<ModContentRecord>/StringIDs',1906,1937),('TryAdmit typed disposition/boundary','PackagePolicyDispositionRecord',1953,2000),('Structural boundary checks','String+optional typed disposition',2094,2137),('Actual Compute check/binding','Configuredpolicy+ContentProfileManifest',2859,2885),('Current policy DTO/result/schema absence','StringID/revision/list/digest;no policy schemaVersion',2945,2973)]
    write(Q/'FROZEN_R10_FIELD_AND_CALLSITE_MATRIX.json',dict(at=now(),source=row(source),manifest=row(MAN),rows=[dict(concept=c,current_type=t,first_line=a,last_line=b,status='FROZEN_R10_STATIC_OBSERVED_FUTURE_R11_UNOBSERVED') for c,t,a,b in field_specs],future_required_concepts=['Policy schemaVersion WE-PACKAGE-POLICY-V1','Pure canonical Serialize/DeserializeAPI','Documented escape convention','Same canonical digest overload routing','Lossless opaque typed binding and noTrim','Exact pure check/admission/content schema mapping'],concrete_future_api_names='UNOBSERVED',mutable_r11_read=False,source_execution=0))
    prior=ROOT/'QA-Tactical-Engine/GATE05-R10-PACKAGE-POLICY-INDEPENDENT-S1-20261009'
    write(Q/'HISTORICAL_R10_REFERENCE_INDEX.json',dict(at=now(),files=[row(prior/n) for n in ['INPUT_EXPECTED_SEMANTICS.json','PACKAGE_POLICY_RESULTS.json','INDEPENDENT_REVIEW_FINDINGS.json','INDEPENDENT_EXECUTION_SUMMARY.json','CRITERIA_DISPOSITION.json','R10_LINEAGE.json']],prior_result_id=load(prior/'ACK.json')['result_id'],prior_case_counts=load(prior/'INDEPENDENT_EXECUTION_SUMMARY.json')['package_cases'],prior_pass_inherited=False,original_r8_fail_and_r9_narrow_closure_preserved=True,old_runner_executed=False))
    baseline=load(Q/'PRESERVATION_BEFORE.json');prefix=str(ROOT/'scratch/WorkerBridgeMod/Source').lower();originalfixed=[r for r in baseline['files'] if r['path'].lower().startswith(prefix)]
    assert all(Path(r['path']).name in ['WorkerBridge.cs','WorkerBridge.csproj'] for r in originalfixed)
    write(Q/'PROTECTED_PATH_SCOPE_AUDIT.json',dict(at=now(),original_fixed_source_hash_only=originalfixed,production_text_only_frozen_r10=True,mutable_r11_source_bin_obj_runner_completion_unread=True,initial_reader_adapter_note='Master new baseline uses bytes instead of older size;own reader adapted before correct ACK;actual SHA/size checked,no input normalization',controls_build_runs=0))
    write(Q/'PREPARATION_LIMITATIONS.json',dict(at=now(),r11_candidate_verdict='NOT_REVIEWED',controls_executed=0,qa_runner_builds=0,candidate_runner_processes=0,production_modify_builds=0,configuration_cache_provider_game_native_operator_oldrunner_negative_rejection_tied_ambiguity_adverse=0,actual_r11_apis_schema_field_carriers_escape='UNOBSERVED',normal_reference_json_hashes_not_candidate_proof=True,escape_reference_variants_not_adopted=True,general_order_cache_patchsettings_native_operator='OPEN_SEPARATE_GATES',closure_changed=False,runtime_e2_released=False,foundation='HOLD'))
    print(json.dumps(dict(reference_cases=len(out),byte_files=2*len(out),normal_criteria=14,static_criteria=14,source_constraints=12,controls_build_run=0),indent=2))
