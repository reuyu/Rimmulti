from common import *
import ast,difflib
assert load(Q/'prepare.TOOL.json')['exit_code']==0
p=OLD/'host.py';s=p.read_bytes().decode('utf-8');tree=ast.parse(s);names={'build','pre','run','post'};defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert {n.name for n in defs}==names
body='\n\n'.join(ast.get_source_segment(s,n) for n in defs).replace('adb6cbc8-c4f9-4436-b137-d550d683f493',MVID)
prefix='from common import *\nfrom normal_tools import mvid,runner_identity,external_paths,inventory,verify_inventory\nimport sys,shutil,subprocess\n\n'
pin='''def pin_paths():
    paths=[Path(r['frozen_path']) for r in load(MAN)['files']]+[Path(r['frozen_path']) for r in load(DEP)['files']]
    paths += [MAN,BASELINE,WP,BINDING,DEP,NJ]+[Path(r['path']) for r in load(BINDING)['literal_oracles'].values()]
    unfinished={f'host_pin.{s}' for s in ['STDOUT.txt','STDERR.txt','TOOL.json']}
    paths += [p for p in Q.rglob('*') if p.is_file() and p.relative_to(Q).as_posix() not in unfinished and not p.is_relative_to(Q/'runs')]+external_paths()
    return list({str(p).lower():p for p in paths}.values())
'''
top='''
mode=sys.argv[1]
if mode=='pin':
    assert load(Q/'prepare.TOOL.json')['exit_code']==load(Q/'plumbing.TOOL.json')['exit_code']==load(Q/'static_r1.TOOL.json')['exit_code']==0
    assert sha(Q/'NORMAL_EXPECTED_ORACLE.json')=='89C9EAE0722EF875577DCF2AC4D20687FDB19CE743B13AE285360225E79F9D7D' and not (Q/'runner/QaPureRunner.exe').exists()
    rows=[row(p) for p in pin_paths()]
    write(Q/'BUILD_INPUTS.json',dict(at=now(),files=rows,input_count=len(rows),oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),callplan=row(Q/'PRIMARY_NORMAL_CALLPLAN.json'),source=row(Q/'Harness/Program.cs'),toolchain=load(Q/'TOOLCHAIN_OBSERVED.json'),compiler_attempts=0,runner_calls=0,production_builds=0,old_PASS_inherited=False,unfinished_logger_exclusions=['host_pin.STDOUT.txt','host_pin.STDERR.txt','host_pin.TOOL.json']))
    print(json.dumps(dict(pins=len(rows),prospective=True,builds_runs=0)))
elif mode=='build':build()
elif mode in ['pre','run','post']:
    stage=int(sys.argv[2]);assert stage in [1,2];globals()[mode](stage)
else:raise ValueError(mode)
'''
new=prefix+pin+'\n'+body+top;assert not (Q/'host.py').exists();(Q/'host.py').write_bytes(new.encode('utf-8'))
(Q/'HOST_DEFINITION_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(s.splitlines(True),new.splitlines(True),fromfile=str(p),tofile=str(Q/'host.py'))).encode('utf-8'))
write(Q/'HOST_DEFINITION_PROVENANCE.json',dict(at=now(),old_TEXT_only=row(p),full_text=s,new_owned_host=row(Q/'host.py'),exact_diff=row(Q/'HOST_DEFINITION_EXACT_DIFF.txt'),copied_definitions=sorted(names),changed_only_selected_mvid_in_functions=True,old_top_level_modes_excluded=True,new_top_level_scope='Own pins,one owncompiler,two new normal child processes only',old_helper_EXEC_IMPORT=False))
print(json.dumps(dict(new_host=row(Q/'host.py'),definition_functions=sorted(names),old_top_level_executed=False,compiler_runner_calls=0)))
