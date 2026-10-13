from review_setup import *
import sys,copy
PAIRCODE=r'''
 class PairPhase:Phase {public OperatorLaunchDescriptor ParentDescriptor=new OperatorLaunchDescriptor(),ChildDescriptor=new OperatorLaunchDescriptor();}
 static PairPhase ObservePair(OperatorStartupPairSnapshot x,string id,string stage,JObject c){
 var p=new PairPhase();
 Mark("Pair.ParentReceipt",id,"ordered_getter");var parent=x.ParentReceipt;
 Mark("Pair.ChildReceipt",id,"ordered_getter");var child=x.ChildReceipt;
 Mark("Pair.OperatorPairId",id,"ordered_getter");var pairId=x.OperatorPairId;
 Mark("Pair.Scope",id,"ordered_getter");var scope=x.Scope;
 Mark("Pair.GetParentDeclaration",id,"ordered_getter");p.ParentDescriptor=x.GetParentDeclaration();
 Mark("Pair.GetChildDeclaration",id,"ordered_getter");p.ChildDescriptor=x.GetChildDeclaration();
 var pg=Descriptor(p.ParentDescriptor);var cg=Descriptor(p.ChildDescriptor);
 var pair=new JObject{["ParentReceipt"]=Receipt(parent,p,true,id),["ChildReceipt"]=Receipt(child,p,false,id),["OperatorPairId"]=pairId,["Scope"]=scope};
 Mark("Snapshot.ToRedactedJson.parent",id,"observational_helper");string ps=parent.Snapshot.ToRedactedJson();
 Mark("Snapshot.ToRedactedJson.child",id,"observational_helper");string cs=child.Snapshot.ToRedactedJson();
 Mark("Receipt.ToRedactedJson.parent",id,"observational_helper");string pr=parent.ToRedactedJson();
 Mark("Receipt.ToRedactedJson.child",id,"observational_helper");string cr=child.ToRedactedJson();
 p.Envelope=new JObject{["PairReadonly4"]=pair,["ParentDeclaration7"]=pg,["ChildDeclaration7"]=cg,["ParentPolicyRecord4"]=JToken.FromObject(p.ParentRecord),["ChildPolicyRecord4"]=JToken.FromObject(p.ChildRecord),["ParentSnapshotRedaction13"]=Parse(ps),["ChildSnapshotRedaction13"]=Parse(cs),["ParentReceiptRedaction11"]=Parse(pr),["ChildReceiptRedaction11"]=Parse(cr)};
 Save(id+"."+stage+".pair.graph.json",p.Envelope);
 Check(id+"_"+stage+"_PAIR_FULL_TYPED",Compare(c["expected_full_observation_graph"],p.Envelope,id+".pair."+stage));
 Raw(id,stage,"pair.envelope",p.Envelope.ToString(Formatting.None),c["expected_full_graph_compact_UTF8"]);
 var pi=c["independently_supplied_parent14_7"];var ci=c["independently_supplied_child14_7"];
 Raw(id,stage,"pair.parent.original7",pg.ToString(Formatting.None),pi["original_declaration7_compact_utf8"]);
 Raw(id,stage,"pair.child.original7",cg.ToString(Formatting.None),ci["original_declaration7_compact_utf8"]);
 Raw(id,stage,"pair.parent.receipt11",pair["ParentReceipt"].ToString(Formatting.None),pi["receipt_compact_utf8"]);
 Raw(id,stage,"pair.child.receipt11",pair["ChildReceipt"].ToString(Formatting.None),ci["receipt_compact_utf8"]);
 Raw(id,stage,"pair.parent.snapshot15",pair["ParentReceipt"]["Snapshot"].ToString(Formatting.None),pi["snapshot_compact_utf8"]);
 Raw(id,stage,"pair.child.snapshot15",pair["ChildReceipt"]["Snapshot"].ToString(Formatting.None),ci["snapshot_compact_utf8"]);
 Raw(id,stage,"pair.parent.receipt.pretty",pr,pi["receipt_redacted_pretty_windows_utf8"]);
 Raw(id,stage,"pair.child.receipt.pretty",cr,ci["receipt_redacted_pretty_windows_utf8"]);
 Raw(id,stage,"pair.parent.snapshot.pretty",ps,pi["snapshot_redacted_pretty_windows_utf8"]);
 Raw(id,stage,"pair.child.snapshot.pretty",cs,ci["snapshot_redacted_pretty_windows_utf8"]);
 Mark("QA.BundleProjection",id,"QA_wrapper_not_publisher");
 var bundle=new JObject{["schemaVersion"]="we-operator-startup-pair/v1",["operatorPairId"]=pairId,["parentDeclaration"]=pg.DeepClone(),["childDeclaration"]=cg.DeepClone()};
 Raw(id,stage,"pair.bundleProjection",bundle.ToString(Formatting.None),c["expected_bundle_compact_UTF8_noLF"]);
 return p;}
 static void PairCases(JArray cases){
 foreach(JObject c in cases){
 string id="PAIR_"+(string)c["case_id"];
 byte[] bb=Encoding.UTF8.GetBytes((string)c["expected_bundle_compact_UTF8_noLF"]["utf8_text"]);
 byte[] pb=Encoding.UTF8.GetBytes((string)c["independently_supplied_parent14_7"]["raw_config"]["utf8_text"]);
 byte[] cb=Encoding.UTF8.GetBytes((string)c["independently_supplied_child14_7"]["raw_config"]["utf8_text"]);
 string bh=BytesHash(bb),ph=BytesHash(pb),ch=BytesHash(cb);
 Mark("OperatorStartupPairAdmission.AdmitPairBytes",id,"primary_direct");
 var a=OperatorStartupPairAdmission.AdmitPairBytes(bb,(string)c["expected_bundle_compact_UTF8_noLF"]["sha256"],pb,cb);
 Check(id+"_NORMAL_ADMIT",a.isValid&&a.error==""&&a.pair!=null);
 Check(id+"_CALLER_BYTES_UNCHANGED_BY_ADMISSION",bh==BytesHash(bb)&&ph==BytesHash(pb)&&ch==BytesHash(cb));
 Mark("receipt.IsValid.parent",id,"primary_direct");Check(id+"_PARENT_VALID",a.pair.ParentReceipt.IsValid());
 Mark("receipt.IsValid.child",id,"primary_direct");Check(id+"_CHILD_VALID",a.pair.ChildReceipt.IsValid());
 var p0=ObservePair(a.pair,id,"BEFORE",c);
 bb[0]^=1;pb[0]^=1;cb[0]^=1;
 Save(id+".caller_array_mutation.json",new JObject{["bundle_sha_after"]=BytesHash(bb),["parent_sha_after"]=BytesHash(pb),["child_sha_after"]=BytesHash(cb),["arrays_edited_after_success_only"]=true,["readmitted"]=false});
 var p1=ObservePair(a.pair,id,"AFTER_CALLER",c);
 Check(id+"_FRESH_DECLARATIONS_AFTER_CALLER",!Object.ReferenceEquals(p0.ParentDescriptor,p1.ParentDescriptor)&&!Object.ReferenceEquals(p0.ChildDescriptor,p1.ChildDescriptor));
 var m=(JObject)c["planned_copy_controls"];
 EditDescriptor(p0.ParentDescriptor,(JObject)m["returnedParentDeclaration7"]);EditDescriptor(p0.ChildDescriptor,(JObject)m["returnedChildDeclaration7"]);
 EditDeclaration(p0.ParentDecl,(JObject)m["returnedParentPolicyDeclaration4"]);EditDeclaration(p0.ChildDecl,(JObject)m["returnedChildPolicyDeclaration4"]);
 EditRecord(p0.ParentRecord,(JObject)m["returnedParentPolicyRecord4"]);EditRecord(p0.ChildRecord,(JObject)m["returnedChildPolicyRecord4"]);
 for(int k=0;k<p0.ParentIdsCopy.Length;k++)p0.ParentIdsCopy[k]="edited.parent.ids."+k;
 for(int k=0;k<p0.ChildIdsCopy.Length;k++)p0.ChildIdsCopy[k]="edited.child.ids."+k;
 Save(id+".returned_owned_mutations.json",new JObject{["ParentDeclaration7"]=Descriptor(p0.ParentDescriptor),["ChildDeclaration7"]=Descriptor(p0.ChildDescriptor),["ParentPolicyDeclaration"]=JToken.FromObject(p0.ParentDecl),["ChildPolicyDeclaration"]=JToken.FromObject(p0.ChildDecl),["ParentPolicyRecord"]=JToken.FromObject(p0.ParentRecord),["ChildPolicyRecord"]=JToken.FromObject(p0.ChildRecord),["ParentIdsDetachedInplace"]=JArray.FromObject(p0.ParentIdsCopy),["ChildIdsDetachedInplace"]=JArray.FromObject(p0.ChildIdsCopy)});
 var p2=ObservePair(a.pair,id,"AFTER_RETURNED",c);
 Check(id+"_FRESH_DECLARATIONS_AFTER_RETURNED",!Object.ReferenceEquals(p0.ParentDescriptor,p2.ParentDescriptor)&&!Object.ReferenceEquals(p0.ChildDescriptor,p2.ChildDescriptor));
 }}
'''
if __name__=='__main__':
    assert sha(PREP/'PRE_RUN_EXPECTED_ORACLE.json')=='7371185E68771EA8613373E3948344B988D86C361421EE9DAF681036CBD95D02'
    assert sha(CAP/'PROSPECTIVE_CAPTURE_ORACLE.json')=='5961CD18DA05B67F6DE40DA8A6EBB289D94ACF85054D57FB31FE4B8C5530C4C7'
    old=ROOT/'QA-Tactical-Engine/GATE05-R27-CHILD_CAPTURE-INDEPENDENT-S2-20261012/Harness/Program.cs'
    src=old.read_text(encoding='utf-8-sig')
    src=src.replace('G05R27-cdc223f3','G05R29-46f60e2a').replace('EngineGate05R27ChildCapture','EngineGate05R29StartupPair')
    marker=' static string BytesHash(byte[] bytes)'
    assert src.count(marker)==1
    src=src.replace(marker,PAIRCODE+'\n'+marker)
    needle='var oracle=Read(Path.Combine(q,"NORMAL_EXPECTED_ORACLE.json"));'
    assert src.count(needle)==1
    src=src.replace(needle,needle+'PairCases((JArray)oracle["pair_cases"]);')
    src=src.replace('["culture"]=CultureInfo.CurrentCulture.Name,','["culture"]=CultureInfo.CurrentCulture.Name,["EnvironmentVersion"]=Environment.Version.ToString(),')
    src=src.replace('COMPLETED normal4 factory8 IsValid8 Capture4','COMPLETED pair6 plus Capture4')
    for bad in ['GetCurrentProcess','Process.Start','WorkerBridgeBootstrapper','TryInstallOperatorStartupConfig','SetPendingStartupHandoff','InvalidateCache']:assert bad not in src
    (Q/'Harness').mkdir();(Q/'runner').mkdir()
    (Q/'Harness/Program.cs').write_bytes(src.encode('utf-8'))
    cap=copy.deepcopy(load(CAP/'PROSPECTIVE_CAPTURE_ORACLE.json'))
    pair=copy.deepcopy(load(PREP/'PRE_RUN_EXPECTED_ORACLE.json'))
    cap['pair_cases']=pair['prospective_cases']
    write(Q/'NORMAL_EXPECTED_ORACLE.json',cap)
    write(Q/'PRIMARY_NORMAL_CALLPLAN.json',dict(at=now(),pair_cases=6,Capture_cases=4,AdmitPairBytes_primary=6,receiptFactory_primary=8,IsValid_primary=20,Capture_primary=4,pair_getters_ordered=108,Capture_getters_ordered=180,phases_per_case=3,pair_raw_sets_per_phase=12,Capture_raw_sets_per_phase=10,caller_byte_edits_after_success=True,no_readmission_after_mutation=True,Pair_ID_detached_array_inplace=True,Capture_ID_control_holder_replacement_only=True,QA_bundleProjection_not_publisher=True,publisher_global_native_Process_adverse_calls=0))
    allowed=[row(SELECTED),row(NJ)]+[row(Path(r['frozen_path'])) for r in load(DEP)['files']]
    write(Q/'QA_RUNNER_CONFIG.json',dict(selected=row(SELECTED),selected_mvid='5c410658-e435-4ae4-8aa3-d074fbcf4f5d',allowed_managed=allowed))
    allocations=[]
    for i,culture in enumerate(['en-US','de-DE'],1):
        out=Q/f'runs/{i}-{culture}';out.mkdir(parents=True)
        allocations.append(dict(run_id='R29S3QA-'+uuid.uuid4().hex,culture=culture,output_root=str(out)))
    write(Q/'RUN_ALLOCATION_PLAN.json',dict(allocations=allocations))
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2')
    dotnet=Path(r'C:\Program Files\dotnet\dotnet.exe');compiler=Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll')
    refs=[fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll']]+[SELECTED,NJ]
    for p in [dotnet,compiler]+refs:assert p.is_file(),str(p)
    rsp=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-codepage:65001','-out:"'+str(Q/'runner/QaPureRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaPureRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in refs]+['"'+str(Q/'Harness/Program.cs')+'"']
    (Q/'build.rsp').write_bytes(('\n'.join(rsp)+'\n').encode('utf-8'))
    write(Q/'TOOLCHAIN_OBSERVED.json',dict(at=now(),dotnet=row(dotnet),compiler=row(compiler),compiler_support=[row(p) for p in sorted(compiler.parent.glob('*.dll'))],resolved_build_references=[row(p) for p in refs],python=row(Path(sys.executable)),prospective_compiler_argv=[str(dotnet),str(compiler),'@'+str(Q/'build.rsp')],cwd=str(ROOT),build_attempts_sofar=0))
    write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),independent_pair_oracle=row(PREP/'PRE_RUN_EXPECTED_ORACLE.json'),independent_Capture_oracle=row(CAP/'PROSPECTIVE_CAPTURE_ORACLE.json'),combined_oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),source=row(Q/'Harness/Program.cs'),callplan=row(Q/'PRIMARY_NORMAL_CALLPLAN.json'),actualoutput_derived=False,old_QA_Program_TEXT_only_pattern=row(old),actual_candidate_calls=0,builds=0,expectation_semantics_unchanged=True))
    print(json.dumps(dict(pair_cases=6,Capture_cases=4,source=row(Q/'Harness/Program.cs'),oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),references=len(refs),compile_candidate_calls=0)))

