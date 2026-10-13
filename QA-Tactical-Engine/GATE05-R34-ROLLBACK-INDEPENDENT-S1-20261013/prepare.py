from common import *
import ast,difflib,sys
assert load(Q/'static_r1.TOOL.json')['exit_code']==load(Q/'PATCH_LOCATOR.TOOL.json')['exit_code']==0
bind=load(BINDING);check(list(bind['literal_oracles'].values())+[bind['old_template_TEXT_only'],bind['old_callplan'],bind['old_combined_literal']])
old=Path(bind['old_template_TEXT_only']['path']);src=old.read_bytes().decode('utf-8');oldpath=str(ROOT/'Dispatcher/CANDIDATES/G05R33-d19c64a5/scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll').replace('\\','\\\\');assert src.count(oldpath)==1
new=src.replace(oldpath,str(SELECTED).replace('\\','\\\\'))
for bad in ['GetCurrentProcess','Process.Start','WorkerBridgeBootstrapper','TryInstallOperatorStartupConfig','SetPendingStartupHandoff','TryAcquirePendingStartupHandoff','InvalidateCache','BindingFlags','GetField','GetMethod']:assert bad not in new
(Q/'Harness').mkdir();(Q/'runner').mkdir();(Q/'Harness/Program.cs').write_bytes(new.encode('utf-8'))
(Q/'TEMPLATE_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(src.splitlines(True),new.splitlines(True),fromfile=str(old),tofile=str(Q/'Harness/Program.cs'))).encode('utf-8'))
write(Q/'TEMPLATE_REBINDING.json',dict(at=now(),old_source_TEXT_only=row(old),new_source=row(Q/'Harness/Program.cs'),diff=row(Q/'TEMPLATE_EXACT_DIFF.txt'),only_selected_path_changed=True,normal_public_call_semantics_unchanged=True,old_top_helper_executed=False))
pair=load(Path(bind['literal_oracles']['independent_pair_oracle']['path']));cap=load(Path(bind['literal_oracles']['independent_Capture_oracle']['path']));combined=load(Path(bind['literal_oracles']['combined_oracle']['path']));assert combined['pair_cases']==pair['prospective_cases'];cap['pair_cases']=pair['prospective_cases'];assert cap==combined
(Q/'NORMAL_EXPECTED_ORACLE.json').write_bytes(Path(bind['literal_oracles']['combined_oracle']['path']).read_bytes());assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')=='89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D'
plan=load(Path(bind['old_callplan']['path']));plan.update(at=now(),delivery_id=DELIVERY,result_id=load(Q/'ACK_INITIAL.json')['result_id']);write(Q/'PRIMARY_NORMAL_CALLPLAN.json',plan)
write(Q/'QA_RUNNER_CONFIG.json',dict(selected=row(SELECTED),selected_mvid=MVID,allowed_managed=[row(SELECTED),row(NJ)]+[row(Path(r['frozen_path'])) for r in load(DEP)['files']],delivery_id=DELIVERY,result_id=load(Q/'ACK_INITIAL.json')['result_id']))
alloc=[]
for i,c in enumerate(['en-US','de-DE'],1):
    p=Q/f'runs/{i}-{c}';p.mkdir(parents=True);alloc.append(dict(run_id='R34S1QA-'+uuid.uuid4().hex,culture=c,output_root=str(p)))
write(Q/'RUN_ALLOCATION_PLAN.json',dict(allocations=alloc))
fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');dotnet=Path(r'C:\Program Files\dotnet\dotnet.exe');compiler=Path(r'C:\Program Files\dotnet\sdk\10.0.201\Roslyn\bincore\csc.dll');refs=[fw/n for n in ['mscorlib.dll','System.dll','System.Core.dll']]+[SELECTED,NJ]
for p in [dotnet,compiler]+refs:assert p.is_file()
rsp=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-codepage:65001','-out:"'+str(Q/'runner/QaPureRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaPureRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in refs]+['"'+str(Q/'Harness/Program.cs')+'"'];(Q/'build.rsp').write_bytes(('\n'.join(rsp)+'\n').encode('utf-8'))
write(Q/'TOOLCHAIN_OBSERVED.json',dict(at=now(),dotnet=row(dotnet),compiler=row(compiler),compiler_support=[row(p) for p in sorted(compiler.parent.iterdir()) if p.is_file()],exact_resolved_references=[row(p) for p in refs],python=row(Path(sys.executable)),compiler_argv=[str(dotnet),str(compiler),'@'+str(Q/'build.rsp')],cwd=str(Q),build_attempts=0))
p=OLD/'normal_tools.py';s=p.read_bytes().decode('utf-8');tree=ast.parse(s);assert all(isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) for n in tree.body)
(Q/'normal_tools.py').write_bytes(p.read_bytes());write(Q/'DEFINITION_PLUMBING_PROVENANCE.json',dict(at=now(),old_TEXT=row(p),full_text=s,new_definition_only_module=row(Q/'normal_tools.py'),byte_identical=True,old_helper_EXEC_IMPORT=False))
write(Q/'ORACLE_BEFORE_BUILD.json',dict(at=now(),binding=row(BINDING),literal_pair=bind['literal_oracles']['independent_pair_oracle'],literal_Capture=bind['literal_oracles']['independent_Capture_oracle'],combined=row(Q/'NORMAL_EXPECTED_ORACLE.json'),source=row(Q/'Harness/Program.cs'),callplan=row(Q/'PRIMARY_NORMAL_CALLPLAN.json'),semantics_byte_exact=True,actual_output_derived=False,initial_builds_runs=0))
print(json.dumps(dict(source=row(Q/'Harness/Program.cs'),combined_oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),only_path_rebound=True,Pair6_Capture4=True,references=5,builds_runs=0)))
