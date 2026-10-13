from common import *
import ast,difflib
assert load(Q/'bootstrap.TOOL.json')['exit_code']==0;check(load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']);assert load(Q/'ACK_RETURN_TOOL_PROOF.json')['isError'] is False
texts=[]
for r in load(MAN)['files']:
    p=Path(r['frozen_path'])
    if p.suffix.lower() in ['.py','.cs','.csproj','.json','.md','.txt','.bin']:
        try:t=p.read_bytes().decode('utf-8-sig')
        except UnicodeDecodeError:continue
        texts.append(dict(**row(p),full_text=t))
write(Q/'FULL_FROZEN_TEXT_READ.json',dict(at=now(),files=texts,read_only=True))
src=S.read_bytes().decode('utf-8');tree=ast.parse(src,filename=str(S));functions=[]
for n in ast.walk(tree):
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
        functions.append(dict(name=n.name,line=n.lineno,end_line=n.end_lineno,source='\n'.join(src.splitlines()[n.lineno-1:n.end_lineno]),calls=[dict(line=k.lineno,expr=ast.unparse(k.func)) for k in ast.walk(n) if isinstance(k,ast.Call)]))
write(Q/'PASSIVE_SOURCE_AST.json',dict(at=now(),publisher=row(S),function_count=len(functions),functions=functions,imports=[ast.unparse(n) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))],candidate_import_execute=0))
old=ROOT/'Dispatcher/CANDIDATES/G05R35-16a25a7e/scratch/OperatorStartupPairR29/publish_operator_pair.py';diff=''.join(difflib.unified_diff(old.read_bytes().decode('utf-8').splitlines(True),src.splitlines(True),fromfile=str(old),tofile=str(S)))
(Q/'ACTUAL_R35_R36_SOURCE_DIFF.txt').write_bytes(diff.encode('utf-8'))
oracle=load(ORACLE);snap=[]
for c in oracle['cases']:
    ins=[]
    for r in c['inputs']:
        raw=r['raw_config_expected'];b=raw['utf8_text'].encode('utf-8');assert hashlib.sha256(b).hexdigest().upper()==raw['sha256'] and len(b)==raw['bytes'] and b.hex().upper()==raw['hex']
        ins.append(dict(role=r['role'],actual_future_path=r['actual_future_path'],config14=r['config14'],raw_identity={k:raw[k] for k in ['sha256','bytes']},original_descriptor7=r['original_descriptor7'],prospective_descriptor7=r['prospectively_approved_new_fixture_descriptor7'],input_keys=list(r)))
    snap.append(dict(case_id=c['case_id'],inputs=ins,other_keys=list(c)))
write(Q/'ORIGINAL_LITERAL_READ.json',dict(at=now(),oracle=row(ORACLE),cases=snap,full_oracle_read=True,raw12_hash_verified=True,fixture_materialized=False))
print(json.dumps(dict(publisher=row(S),full_frozen_texts=len(texts),functions=len(functions),case_ids=[c['case_id'] for c in snap],all_execution=0),ensure_ascii=False))
