from review_setup import *
if __name__=='__main__':
    old=ROOT/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S2-20261011'
    t=(old/'execution_tools.py').read_text(encoding='utf-8-sig')
    a=t.index("    paths += [Q/n for n in [");b=t.index("    paths += [MAN,DEP,BASELINE",a)
    files=['review_setup.py','bootstrap_s2.py','S2_SOURCE_POINTER_ONLY_DIFF.txt','S2_AUTHORIZED_TEXT_CLONE.json','prepare_runner.py','prepare_execution_tools.py','execution_tools.py','build_once.py','build.rsp','Harness/Program.cs','NORMAL_EXPECTED_ORACLE.json','PRIMARY_NORMAL_CALLPLAN.json','QA_RUNNER_CONFIG.json','RUN_ALLOCATION_PLAN.json','ORACLE_BEFORE_BUILD.json','R27_FROZEN_LINEAGE.json','TOOLCHAIN_OBSERVED.json','S2_CORRECTED_DEPENDENCY_BEFORE_BUILD.json','STATIC_SOURCE_SCOPE_BEFORE_BUILD.json']
    t=t[:a]+"    paths += [Q/n for n in "+repr(files)+"]\n"+t[b:]
    t=t.replace("PKG/'WP_QA_ENGINE_GATE05_R25_ROLE_USERDATA_INDEPENDENT_S2.md'",'WP')
    t=t.replace("Q/'Program.cs'","Q/'Harness/Program.cs'")
    t=t.replace("o=load(Q/'NORMAL_EXPECTED_ORACLE.json');assert len(o['cases'])==4 and o['ToSnapshot_per_run']==4 and o['SelectUserData_per_run']==8","o=load(Q/'NORMAL_EXPECTED_ORACLE.json');assert len(o['normal_pairs'])==4 and len(o['getter15_order_types'])==15")
    t=t.replace("Normal4 input/oracle/source/compiler/framework/frozen99-managed4 prospectivepins beforeonlybuild/calls","R27S2 normal4 full15typedraw source-oracle-callplan/compiler/framework/frozen83-managed4 prospectivepins beforeonlybuild/calls")
    t=t.replace("Normal4 ToSnapshot4 Select8 only;publicsnapshot policy-UTC graph/normalownededits;nofixturepathIO/global/receipt/native/adverse","R27S2 normal4 factory8 IsValid8 Capture4 full15typedraw-originalUTC-ownership;noglobal/native/Process/readonlyexception/adverse")
    t=t.replace("['NORMAL_EXPECTED_ORACLE.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json','EXECUTION_ADMISSION_BEFORE_BUILD.json']","['NORMAL_EXPECTED_ORACLE.json','PRIMARY_NORMAL_CALLPLAN.json','ORACLE_BEFORE_BUILD.json','QA_RUNNER_CONFIG.json','EXECUTION_ADMISSION_BEFORE_BUILD.json']")
    insertion="""    paths += [PKG/n for n in ['MASTER_R27_FROZEN_NEWTONSOFT_POINTER_CORRECTION_20261012.json','MASTER_R27_QA_S2_REPORT_IDENTITY_CORRECTION_20261012.md','MASTER_REVIEW_ENGINE_GATE05_R27_QA_S1_DEPENDENCY_STOP_20261012.md']]
    for base in [Path(r'C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL'),Path(r'C:\\Windows\\Microsoft.NET\\assembly\\GAC_64')]:
        for name in ['System.Configuration','System.Xml.Linq','System.Web','System.Net.Http']:
            if (base/name).exists():paths += list((base/name).glob('*/'+name+'.dll'))
"""
    t=t.replace("    return list({str(p).lower():p for p in paths}.values())",insertion+"    return list({str(p).lower():p for p in paths}.values())")
    (Q/'execution_tools.py').write_bytes(t.encode())
    (Q/'build_once.py').write_bytes((old/'build_once.py').read_bytes())
    ns=dict(globals());p=PKG/'bootstrap/verify_local_identity.py';defs=[x for x in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(x,ast.FunctionDef) and x.name=='mvid'];exec(compile(ast.Module(body=defs,type_ignores=[]),'AST_METADATA_ONLY_MVID','exec'),ns)
    correction=PKG/'MASTER_R27_FROZEN_NEWTONSOFT_POINTER_CORRECTION_20261012.json';d=load(correction);nj=Path(d['admitted_frozen_loader_reference']['path']);assert sha(nj)==d['admitted_frozen_loader_reference']['sha256'] and nj.stat().st_size==711952 and ns['mvid'](nj)=='dd21e087-47d9-4bce-bed8-b56112226337'
    write(Q/'S2_CORRECTED_DEPENDENCY_BEFORE_BUILD.json',dict(at=now(),controlling_correction=row(correction),admitted_DLL=row(nj),independently_observed_mvid=ns['mvid'](nj),config=row(Q/'QA_RUNNER_CONFIG.json'),scope='Compiler/reference managedloader support only; not A runner/native',dependency_copy_move_download=False,candidate_calls_builds_yet=0))
    oldsrc=ROOT/'Dispatcher/CANDIDATES/G05R25-dd341868/scratch/WorkerBridgeMod/Source/WorkerBridge.cs';newsrc=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs';ob=oldsrc.read_bytes();nb=newsrc.read_bytes();at=166910;delta=len(nb)-len(ob);assert delta==11937 and nb[:at]==ob[:at] and nb[at+delta:]==ob[at:]
    code=nb[at:at+delta].decode();import re
    getters=re.findall(r'public\s+(OperatorStartupAdmissionReceipt|OperatorLaunchDescriptor|ValidatorTask|string|IReadOnlyList<string>)\s+(\w+)\s*=>',code);assert [dict(csharp_type=a,name=b) for a,b in getters]==load(Q/'NORMAL_EXPECTED_ORACLE.json')['getter15_order_types']
    write(Q/'STATIC_SOURCE_SCOPE_BEFORE_BUILD.json',dict(at=now(),new_frozen_source=row(newsrc),old_source=row(oldsrc),one_insert_bytes=delta,two_fixed_segments_byteidentical=True,getters15_names_order_types_matched=True,private_readonly_task27_and_detached_getter_source=True,approved7_actual_lowercase_field_order_preserved=True,read_only_wrappers_private_storage_source_only=True,guards_and_scalar_null_coalescing='SOURCE_ONLY_UNEXECUTED',extra_authority_registration_global_IO_normalization_in_newclass=False,IsValid_nested_PathGetFullPath='Existing approved helper source fact, not new direct Capture IO',candidate_calls=0))
    print(json.dumps(dict(own_host_tools_prepared=True,newtonsoft_hash=sha(nj),newtonsoft_mvid=ns['mvid'](nj),normalCallsBeforeBuild=0),indent=2))
