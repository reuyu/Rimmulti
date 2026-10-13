from common import *
import sys,difflib,copy,re
assert load(Q/'static_review.TOOL.json')['exit_code']==0
binding=load(BINDING);check(list(binding['independent_literal_oracles'].values())+[binding['old_template_source'],binding['old_full_callplan']])
old=Path(binding['old_template_source']['path']);src=old.read_bytes().decode('utf-8');new=src
oldselected=str(OLD.parent.parent/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll')
# Exactly one candidate path binding; preserve frozen historical Newtonsoft and all semantic call code.
oldselected=str(ROOT/'Dispatcher/CANDIDATES/G05R29-46f60e2a/scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll')
assert new.count(oldselected.replace('\\','\\\\'))==1
new=new.replace(oldselected.replace('\\','\\\\'),str(SELECTED).replace('\\','\\\\'))
observations=r'''
 static void ObserveLoaded(string phase){
 var cfg=Read(Path.Combine(QRoot,"QA_RUNNER_CONFIG.json"));var a=typeof(OperatorChildLaunchInputs).Assembly;
 if(a.Location!=(string)cfg["selected"]["path"] || Hash(a.Location)!=(string)cfg["selected"]["sha256"] || a.ManifestModule.ModuleVersionId.ToString()!=(string)cfg["selected_mvid"])throw new Exception("STOP selected load identity mismatch");
 var loaded=new JArray();foreach(var asm in AppDomain.CurrentDomain.GetAssemblies().OrderBy(z=>z.GetName().Name)){if(asm.IsDynamic)continue;loaded.Add(new JObject{["name"]=asm.GetName().Name,["path"]=asm.Location,["sha256"]=Hash(asm.Location),["mvid"]=asm.ManifestModule.ModuleVersionId.ToString()});}
 Save("ACTUAL_LOADED_MANAGED_"+phase+".json",loaded);
 Save("SELECTED_LOAD_"+phase+".json",new JObject{["path"]=a.Location,["sha256"]=Hash(a.Location),["mvid"]=a.ManifestModule.ModuleVersionId.ToString(),["CLR_EnvironmentVersion"]=Environment.Version.ToString(),["corelib_path"]=typeof(object).Assembly.Location,["corelib_sha256"]=Hash(typeof(object).Assembly.Location),["corelib_mvid"]=typeof(object).Assembly.ManifestModule.ModuleVersionId.ToString()});
 }
'''
needle=' static string Out="";';assert new.count(needle)==1;new=new.replace(needle,observations+'\n static string QRoot="";'+needle)
needle='try{var oracle=Read(Path.Combine(q,"NORMAL_EXPECTED_ORACLE.json"));';assert new.count(needle)==1;new=new.replace(needle,'try{QRoot=q;ObserveLoaded("BEFORE");var oracle=Read(Path.Combine(q,"NORMAL_EXPECTED_ORACLE.json"));')
needle='var a=typeof(OperatorChildLaunchInputs).Assembly;Save("NORMAL_RESULTS.json"';assert new.count(needle)==1;new=new.replace(needle,'ObserveLoaded("AFTER");'+needle)
for bad in ['GetCurrentProcess','Process.Start','WorkerBridgeBootstrapper','TryInstallOperatorStartupConfig','SetPendingStartupHandoff','TryAcquirePendingStartupHandoff','InvalidateCache','BindingFlags','GetField','GetMethod']:assert bad not in new,bad
(Q/'Harness').mkdir();(Q/'runner').mkdir();(Q/'Harness/Program.cs').write_bytes(new.encode('utf-8'))
diff=''.join(difflib.unified_diff(src.splitlines(True),new.splitlines(True),fromfile=str(old),tofile=str(Q/'Harness/Program.cs')))
(Q/'TEMPLATE_EXACT_DIFF.txt').write_bytes(diff.encode('utf-8'))
write(Q/'TEMPLATE_REBINDING.json',dict(at=now(),old_TEXT_only=row(old),new_source=row(Q/'Harness/Program.cs'),exact_diff=row(Q/'TEMPLATE_EXACT_DIFF.txt'),edits=['Selected path exactly once','Public allowed assembly identity/loaded managed metadata BEFORE/AFTER only','New QRoot parameter binding'],semantic_oracle_callplan_unchanged=True,private_global_lifecycle_reflection_calls=0))
pair=load(Path(binding['independent_literal_oracles']['independent_pair_oracle']['path']));cap=load(Path(binding['independent_literal_oracles']['independent_Capture_oracle']['path']));combined=load(Path(binding['independent_literal_oracles']['combined_oracle']['path']))
assert combined['pair_cases']==pair['prospective_cases']
cap['pair_cases']=pair['prospective_cases'];assert cap==combined
check([binding['independent_literal_oracles']['combined_oracle']]);(Q/'NORMAL_EXPECTED_ORACLE.json').write_bytes(Path(binding['independent_literal_oracles']['combined_oracle']['path']).read_bytes())
assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')==binding['independent_literal_oracles']['combined_oracle']['sha256']
plan=load(Path(binding['old_full_callplan']['path']));plan['at']=now();plan.update(delivery_id=DELIVERY,result_id=load(Q/'ACK_INITIAL.json')['result_id'],normal_templates_TEXT_only=True)
write(Q/'PRIMARY_NORMAL_CALLPLAN.json',plan)
allowed=[row(SELECTED),row(NJ)]+[row(Path(r['frozen_path'])) for r in load(DEP)['files']]
write(Q/'QA_RUNNER_CONFIG.json',dict(selected=row(SELECTED),selected_mvid='7d436c98-659a-4df1-a085-06fe9e55a0bc',allowed_managed=allowed,delivery_id=DELIVERY,result_id=load(Q/'ACK_INITIAL.json')['result_id']))
allocations=[]
for i,culture in enumerate(['en-US','de-DE'],1):
    out=Q/f'runs/{i}-{culture}';out.mkdir(parents=True);allocations.append(dict(run_id='R32S1QA-'+uuid.uuid4().hex,culture=culture,output_root=str(out)))
write(Q/'RUN_ALLOCATION_PLAN.json',dict(allocations=allocations))
fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');dotnet=Path(r'C:\Program Files\dotnet\dotnet.exe');compiler=Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll')
refs=[fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll']]+[SELECTED,NJ]
for p in [dotnet,compiler]+refs:assert p.is_file(),str(p)
rsp=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-codepage:65001','-out:"'+str(Q/'runner/QaPureRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaPureRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in refs]+['"'+str(Q/'Harness/Program.cs')+'"']
(Q/'build.rsp').write_bytes(('\n'.join(rsp)+'\n').encode('utf-8'))
write(Q/'TOOLCHAIN_OBSERVED.json',dict(at=now(),dotnet=row(dotnet),compiler=row(compiler),compiler_support=[row(p) for p in sorted(compiler.parent.iterdir()) if p.is_file()],exact_resolved_references=[row(p) for p in refs],python=row(Path(sys.executable)),compiler_argv=[str(dotnet),str(compiler),'@'+str(Q/'build.rsp')],cwd=str(Q),build_attempts=0,production_builds=0))
write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),literal_binding=row(BINDING),independent_pair= binding['independent_literal_oracles']['independent_pair_oracle'],independent_Capture=binding['independent_literal_oracles']['independent_Capture_oracle'],combined=row(Q/'NORMAL_EXPECTED_ORACLE.json'),source=row(Q/'Harness/Program.cs'),callplan=row(Q/'PRIMARY_NORMAL_CALLPLAN.json'),expected_semantics_byte_exact=True,expected_not_R32_observation_derived=True,builds_calls=0))
# Supplement the already preserved csc.dll selector: producer actually prints csc.exe.
FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R32-CUSTODY-20261012-DIRECT-64ad38e2';mapping={r['original_path'].lower():Path(r['frozen_path']) for r in load(MAN)['files']};commands=[]
for run in load(FT/'BUILD_HOST_TOOL_TELEMETRY.json')['build_runs']:
    p=mapping[run['stdout_path'].lower()];text=p.read_bytes().decode('utf-8');lines=[s for s in text.splitlines() if 'csc.exe /noconfig ' in s];assert len(lines)==1
    refslist=[m.group(1) or m.group(2) for m in re.finditer(r' /reference:(?:"([^"]+)"|(\S+))',lines[0])];assert len(refslist)==120
    measured=[row(Path(p)) for p in refslist];commands.append(dict(configuration=run['configuration'],raw=row(p),whole_diagnostic_command=lines[0],actual_references=measured,reference_count=len(measured),prospective_producer_all_refs=False,fresh_csc_PID='UNOBSERVED'))
write(Q/'PRODUCER_COMPILER_COMMAND_EXACT_REFERENCES_SUPPLEMENT.json',dict(at=now(),records=commands,earlier_selector='csc.dll diagnostic selector found only CompilerServer; original witness retained, actual csc.exe command now independently parsed without rerunning producer',candidate_execution=0))
print(json.dumps(dict(pair6_Capture4=True,oracle_byte_exact=True,semantic_callplan_preserved=True,new_source=row(Q/'Harness/Program.cs'),references=len(refs),producer_diagnostic_refs=[r['reference_count'] for r in commands],builds_calls=0)))
