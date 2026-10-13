from common import *
import ast,difflib
d=load(Q/'bootstrap.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']]);check(load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']);assert load(Q/'ACK_RETURN_TOOL_PROOF.json')['isError'] is False
texts=[]
for r in load(MAN)['files']:
    p=Path(r['frozen_path'])
    if p.suffix.lower() in ['.py','.json','.md','.txt','.cs','.csproj','.bin']:
        try:t=p.read_bytes().decode('utf-8-sig')
        except UnicodeDecodeError:continue
        texts.append(dict(**row(p),full_text=t))
write(Q/'FULL_FROZEN_TEXT_READ.json',dict(at=now(),files=texts))
src=S.read_bytes().decode('utf-8');tree=ast.parse(src,filename=str(S));functions=[]
for n in ast.walk(tree):
    if isinstance(n,ast.FunctionDef):functions.append(dict(name=n.name,line=n.lineno,end_line=n.end_lineno,source='\n'.join(src.splitlines()[n.lineno-1:n.end_lineno]),calls=[dict(line=k.lineno,expression=ast.unparse(k.func)) for k in ast.walk(n) if isinstance(k,ast.Call)]))
write(Q/'PASSIVE_SOURCE_AST.json',dict(at=now(),publisher=row(S),body_node_count=len(tree.body),functions=functions,imports=[ast.unparse(n) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))],candidate_import_execute=0))
old=ROOT/'Dispatcher/CANDIDATES/G05R36-d2d6556b/scratch/OperatorStartupPairR29/publish_operator_pair.py';diff=''.join(difflib.unified_diff(old.read_bytes().decode('utf-8').splitlines(True),src.splitlines(True),fromfile=str(old),tofile=str(S)))
p=Q/'ACTUAL_R36_R37_SOURCE_DIFF.txt';assert not p.exists();p.write_bytes(diff.encode('utf-8'))
oracle=load(ORACLE);cases=[]
for c in oracle['cases']:
    ins=[]
    for i in c['inputs']:
        raw=i['raw_config_expected'];b=raw['utf8_text'].encode('utf-8');assert hashlib.sha256(b).hexdigest().upper()==raw['sha256'] and len(b)==raw['bytes'] and b.hex().upper()==raw['hex']
        ins.append(dict(role=i['role'],raw_identity={k:raw[k] for k in ['sha256','bytes']},config14=i['config14'],original_descriptor7=i['original_descriptor7'],prospective_descriptor7=i['prospectively_approved_new_fixture_descriptor7']))
    cases.append(dict(case_id=c['case_id'],operatorPairId_original=c['expected_aux4']['operatorPairId'],inputs=ins))
write(Q/'ORIGINAL_LITERAL_READ.json',dict(at=now(),oracle=row(ORACLE),prior_R36_matrix=row(OLDQ/'ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json'),cases=cases,raw12_hash_verified=True,old_oracles_changed=False,fixture_materialized=False))
print(json.dumps(dict(publisher=row(S),full_text_files=len(texts),body_nodes=len(tree.body),functions=len(functions),cases=[c['case_id'] for c in cases],all_candidate_execution=0),ensure_ascii=False))
