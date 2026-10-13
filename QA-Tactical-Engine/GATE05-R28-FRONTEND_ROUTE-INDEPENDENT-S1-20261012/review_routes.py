from bootstrap_review import *
from raw_metadata import PE
from source_and_lineage import source_span
def method(e,fragment):
    return next(m for v in e['methods'].values() for m in v if fragment in m['method'])
def anchor(m,offsets=None):
    a={k:m[k] for k in ['method_token','method','rva','implementation_flags','method_flags','signature_hex','body_available']}
    if m['body_available']:
        a.update({k:m[k] for k in ['method_file_offset','code_file_offset','code_bytes','code_sha256','header_and_code_sha256']})
        if offsets:a['instructions']=[x for x in m['instructions'] if x['il_offset'] in offsets]
    return a
if __name__=='__main__':
    e=load(Q/'STATIC_FRONTEND_IL_EVIDENCE.json')
    core=PE(load(D)['files'][0]['frozen_path']);worker=PE(DLL)
    supplement=[core.body(i) for i,n in core.methods() if any(x in n for x in ['Verse.UnityData::CopyUnityData','Verse.PlayDataLoader+<>c::<DoPlayLoad>b__4_4','Verse.LoadedModManager::CreateModClasses','Verse.LoadedModManager::CreateMod','Verse.LongEventHandler::ExecuteToExecuteWhenFinished'])]
    write(Q/'INITIALIZATION_SUPPLEMENT_IL.json',dict(library=core.identity(),methods=supplement))
    from extract_frontend import text
    (Q/'INITIALIZATION_SUPPLEMENT.il.txt').write_text(text(supplement),encoding='utf-8')
    wrefs=[]
    for i,n in worker.methods():
        m=worker.body(i)
        for k,x in enumerate(m.get('instructions',[])):
            o=x['operand']
            if isinstance(o,dict) and any(t in o['resolved'] for t in ['GenCommandLine::TryGetCommandLineArg','OperatorChildLaunchInputs::Capture','GameObject::AddComponent','GenFilePaths::get_SaveDataFolderPath']):
                wrefs.append(dict(caller=m['method'],caller_token=m['method_token'],caller_code_sha256=m['code_sha256'],instruction=x,context=m['instructions'][max(0,k-3):k+3]))
    write(Q/'WORKER_DIRECT_ROUTE_CALLS.json',dict(methoddefs=worker.counts[6],references=wrefs,direct_capture_calls=[r for r in wrefs if 'OperatorChildLaunchInputs::Capture' in r['instruction']['operand']['resolved']],scope='Exact selected Worker IL only; no native/dynamic callers inference'))
    m=method(e,'GenCommandLine::TryGetCommandLineArg')
    cli=dict(id='CLI01',status='OBSERVED_STATIC_IL_NOT_EXECUTED',anchor=anchor(m,['IL_0000','IL_000D','IL_0019','IL_001C','IL_0026','IL_002D','IL_0043','IL_004A','IL_004F','IL_005B']),
      source_of_tokens='System.Environment.GetCommandLineArgs(), fresh linear scan every call from argv index0; no token dictionary/cache',
      split='Contains(char61) then Split(char61,StringSplitOptions0); exactly2 parts required',
      accepted_key_forms=['key=value','-key=value'],key_matching='String.Compare(string,string,bool true); ignore-case overload, no Ordinal comparison specified',
      duplicate='First matching well-formed argv item wins; no duplicate rejection, no last-wins dictionary; malformed multi-equals item skipped',
      value='Second part as-is, including empty/leading/trailing whitespace/Unicode; no Trim/unquote/unescape/percent/base64 decoding in this method; false=>out null',
      unsupported=['key value','-key value','--key=value when queried key','any token whose value contains an additional ='],
      encoding='OS command-line to argv splitting occurs before this IL and is UNVERIFIED here. Ensure one argv item per key=value; quote/backslash/Unicode conversion needs future exact OS/runtime evidence. Quoting does not prevent this later Split from seeing =.',
      examples_derivation_only=[dict(argv='-operatororigin=  Ω plan  ',returned='  Ω plan  '),dict(argv='-operatorconfig=C:\\space root\\a.json',returned='C:\\space root\\a.json',condition='Already a single argv item'),dict(argv='-operatororigin=a=b',returned=None,reason='3 split parts; skipped'),dict(argv='-savedatafolder=',returned='',reason='Parser accepts empty; path getter substitutes directory separator')])
    pathm=method(e,'GenFilePaths::get_SaveDataFolderPath')
    paths=dict(id='PATH01',status='OBSERVED_STATIC_IL_NATIVE_EFFECTIVE_ROOT_UNTESTED',anchor=anchor(pathm,['IL_0000','IL_0005','IL_000A','IL_0011','IL_0029','IL_002E','IL_0035','IL_0054','IL_006F','IL_00E1','IL_00F7','IL_00FF','IL_0104']),
       actual_flag='savedatafolder',actual_spelling='-savedatafolder=<value> or savedatafolder=<value> in one argv',
       cache='Private static saveDataPath initialized null in .cctor, first getter selects path and stores it; subsequent calls with non-null cached string bypass selection',
       trim_bug_observed='TrimEnd(backslash,slash) return popped; original value remains, do not claim trailing slash removed',
       empty_override='Empty parser value becomes DirectorySeparatorChar string; no empty/absolute/approved-root check by this core branch',
       fs_effects='DirectoryInfo(path) Exists/Create are present; relative path permitted by this branch and depends on actual child cwd; no GetFullPath/Path.IsPathFullyQualified here',
       fallback='No accepted override => UnityData editor/platform/persistentDataPath branch or Application persistentDataPath native getter. Actual fallback values/platform UNOBSERVED.',
       initialization_chain=['Root.CheckGlobalInit calls UnityDataInitializer.CopyUnityData atIL0058, Prefs.Init atIL0067, then queues StaticConstructorOnStartupUtility.CallAll delegate atIL008A/009B',
         'Prefs.Init first instruction calls GenFilePaths.PrefsFilePath; that calls ConfigFolderPath -> FolderUnderSaveData -> SaveDataFolderPath; can create directories before Worker bootstrap admission',
         'GenFilePaths .cctor only initialization, not new override route; no mutable setter caller outside getter/.cctor found in full core direct IL scan'],
       declared_vs_actual='Worker SafeSaveDataFolderPath selects frozen role declaration, not this core cache. Declared READ_ONLY ValidatorUserDataDirectory does not set native/core effective root.',
       early_boundary='Operator must provision launch argv and cwd before fresh child starts/first GenFilePaths access; adding override in Worker bootstrap or Awake is too late to assume config/prefs isolation.',
       references=[anchor(method(e,x)) for x in ['GenFilePaths::get_PrefsFilePath','GenFilePaths::get_ConfigFolderPath','GenFilePaths::FolderUnderSaveData','Prefs::Init','Root::CheckGlobalInit']])
    bootstrap=method(e,'WorkerBridgeBootstrapper::.cctor')
    install=method(e,'WorkerBridgeComponent::TryInstallOperatorStartupConfig')
    awake=method(e,'WorkerBridgeComponent::Awake')
    lifecycle=dict(id='ORDER01',status='MANAGED_SOURCE_IL_ORDER_OBSERVED_NATIVE_AWAKE_TIMING_UNVERIFIED',
      static_attribute=load(Q/'FROZEN_SOURCE_ANCHORS.json')['bootstrap_attributes'],
      startup_core=anchor(method(e,'StaticConstructorOnStartupUtility::CallAll'),['IL_000A','IL_0025']),
      bootstrap=anchor(bootstrap,['IL_01E0','IL_022C','IL_02BC','IL_02C5','IL_02CD']),
      observed_order=['read7 declaration -> IssueAdmissionReceipt -> TryInstallOperatorStartupConfig success -> GameObject ctor -> DontDestroyOnLoad -> AddComponent<WorkerBridgeComponent>',
        'TryInstall calls receipt.IsValid and lock; stores single process-global activeReceipt/activeSnapshot/sealed flag before returning true',
        'Awake changes fastEcology and subscribes log callback before existing receipt guard; receipt guard precedes policy/log/TCP listener/thread, but no private child registration or task receiver precedes them'],
      install=anchor(install,['IL_0005','IL_0023','IL_002A','IL_0031','IL_0048','IL_0053','IL_0059']),
      awake=anchor(awake,['IL_0003','IL_0014','IL_001A','IL_0026','IL_0061']),
      addcomponent_wrappers=[anchor(method(e,'UnityEngine.GameObject::AddComponent sig=300'),['IL_000C']),anchor(method(e,'UnityEngine.GameObject::AddComponent sig=200'),['IL_0003']),anchor(method(e,'UnityEngine.GameObject::Internal_AddComponentWithType'))],
      native_frontier='Generic AddComponent -> Type overload -> Internal_AddComponentWithType (RVA0/implementation flag internal-call). No managed Awake call in wrappers; exact immediate/deferred Awake/registration order not proven.',
      minimum_safe_order='Finish immutable validated startup context before invoking AddComponent; assume Awake may occur during native call. Awake must acquire/gate per-instance child context before policy/listener/task side effects. Never rely on post-AddComponent property assignment or inactive-object trick without native proof.',
      current_global_not_registry='One-time process startup receipt seal is observed. It is not a per-current-task child owner register, pairing proof or authentication.')
    logging=dict(id='LOG01',status='OBSERVED_STATIC_SENSITIVE_ARGV_LOGGING_ROUTE',
      anchor=anchor(method(e,'Root::CheckGlobalInit'),['IL_0008','IL_001E','IL_0023','IL_0028','IL_002D']),
      fact='Root logs all command line arguments after argv0 through Skip(1)/ToSpaceList/Log.Message before Prefs/bootstrap. Current launcher includes capabilityNonce on child command line.',
      limit='No child started/log produced/OS visibility or ACL examined. Potential exposure route, not an executed leak proof.',
      requirement='Do not promote argv capability as protected issuer channel. New route must use operator-owned protected channel or approved early log redaction with exact scope; public non-secret locator is separate from capability.')
    exact=[source_span(SRC,a,z,n) for a,z,n in [(42,136,'BOOTSTRAP'),(422,436,'INSTALL'),(438,459,'DECLARED_ROOT'),(559,602,'AWAKE'),(1964,2143,'STAGE_TASK_MAKER'),(2190,2345,'LAUNCHER'),(2424,2585,'EXECUTE_TASK_COMMAND'),(2587,2898,'COMPLETE_CURRENT_VALIDATION'),(3445,3452,'DESTROY'),(3454,3474,'ROLE_SELECTOR'),(3476,3719,'PURE_CAPTURE')]]
    route=dict(at=now(),result_id=load(Q/'ACK_INITIAL.json')['result_id'],selected=pin(DLL),source=pin(SRC),CLI=cli,paths=paths,ordering=lifecycle,argv_logging=logging,exact_source_anchors=exact,
      current_route=[
        dict(step='operator7 bootstrap',observed='One CLI config admission/receipt, process-global seal; no real separate child config producer/approval-channel implementation observed in selected sources',authority='ByteSHA/descriptor/config consistency only; IsTrusted/publicfactory/privateconstructor not independent operator approval'),
        dict(step='simulator stage',observed='Owned sealed result -> random taskId/capability/secret -> exact task27/currentTask/task file and result channel; MD126 owns simulator nonce',authority='Retain existing legitimate simulator producer, no blanket Engine mint ban'),
        dict(step='launch',observed='Private currentTask nonce matches request, parent config exe/SHA/freeform ValidatorArguments/ValidatorCwd; --task-file spacevalue and --nonce spacevalue appended; cwd only applied if Directory.Exists',authority='No separately operator-approved READ_ONLY receipt/pair/current-task registration or pure Capture consumption'),
        dict(step='child frontend',observed='Selected bootstrap only consumes7 plus Awake bridgeport; no task-file/nonce reader. Full core90840 direct method scan finds only savedatafolder TryGet caller, no task/nonce receiver',authority='Flags without consumer cannot form child task channel; no claim about unaudited separate executable/reflection'),
        dict(step='bridge task command',observed='HandleExecuteValidatorTask splits argument on space, file lookup/deserialization/nonce self-check, actual profile/stage/load/result; separate TCP command, not CLI receiver',authority='Space path unsafe in command split; protected issuer/current owned pairing still needs connected provider, do not execute here'),
        dict(step='owner lifetime',observed='RevokeReadiness clears task/seal/receipt/process fields; OnDestroy only stops log/listener/thread, not full task/process cleanup',authority='Do not infer new child registry lifecycle or at-most-once consume from existing state fields') ],
      schema_changes=0,config_fields_fixed=14,descriptor_fields_fixed=7,task_fields_fixed=27,new_flags_or_carrier_adopted=False,A_R28_proposal_read=False,
      production_builds=0,qa_compiler_builds=0,candidate_calls=0,normal_adverse_rejection_lifecycle_runs=0,fullnative_e2='NOT_RELEASED',foundation='HOLD')
    write(Q/'SOURCE_ORDER_AND_ROUTE.json',route)
    # Structural metadata proof only; static assertions are not runtime assertions.
    validation=[]
    for lib,ms in e['methods'].items():
        for m in ms:
            if not m['body_available']:continue
            starts={i['il_offset'] for i in m['instructions']};starts.add(f"IL_{m['code_bytes']:04X}")
            for x in m['instructions']:
                if x['opcode']=='switch':assert all(t in starts for t in x['operand'])
                elif isinstance(x['operand'],str) and x['operand'].startswith('IL_'):assert x['operand'] in starts
            validation.append(dict(module=lib,token=m['method_token'],code_sha256=m['code_sha256'],branch_targets_valid=True))
    idrefs={}
    pure=H/'bootstrap/verify_local_identity.py'
    defs=[n for n in ast.parse(pure.read_text(encoding='utf-8-sig')).body if isinstance(n,ast.FunctionDef) and n.name=='mvid']
    ns=dict(struct=struct,uuid=uuid);exec(compile(ast.Module(body=defs,type_ignores=[]),str(pure)+'#mvid-only','exec'),ns)
    for row in e['libraries']:
        actual=ns['mvid'](Path(row['path']));assert actual==row['mvid'];idrefs[row['path']]=actual
    write(Q/'STATIC_METADATA_AUDIT.json',dict(at=now(),branch_validation=validation,independent_mvid_reader_matches=idrefs,source_pdb4of4_both_modes=load(Q/'R28_FROZEN_LINEAGE.json'),core_scan_errors=0,core_scanned_methoddefs=90840,worker_scanned_methoddefs=532,decoder_limitations='Metadata TypeSpec/generic signature labels retain exact raw signature hex; not full decompiler/type verifier. Scan covers direct managed IL tokens only.',assembly_loads=0,old_helper_top_level_executions=0))
    print(json.dumps(dict(typed_facts=4,source_anchors=len(exact),branch_methods=len(validation),independent_mvid_matches=len(idrefs),worker_capture_callers=0)))

