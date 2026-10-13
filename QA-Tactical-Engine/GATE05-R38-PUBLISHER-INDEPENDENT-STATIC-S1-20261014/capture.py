from common import *
import ast,difflib
d=load(Q/'bootstrap.TOOL.json');assert d['exit_code']==0;check([d['stdout'],d['stderr']]);check(load(Q/'PASSIVE_INPUT_MANIFEST.json')['files']);assert load(Q/'ACK_RETURN_TOOL_PROOF.json')['isError'] is False
check(load(Q/'RECOVERY_R1_PROSPECTIVE_SUPPLEMENT.json')['files']);check(load(Q/'STOP_INITIAL_PARTIAL_PRESERVATION.json')['files'])
texts=[]
for r in load(MAN)['files']:
    p=Path(r['frozen_path'])
    if p.suffix.lower() in ['.py','.json','.md','.txt','.cs','.csproj','.bin']:
        try:t=p.read_bytes().decode('utf-8-sig')
        except UnicodeDecodeError:continue
        texts.append(dict(**row(p),full_text=t))
write(Q/'FULL_FROZEN_TEXT_READ.json',dict(at=now(),files=texts))
src=S.read_bytes().decode('utf-8');tree=ast.parse(src,filename=str(S));funcs=[]
for n in ast.walk(tree):
    if isinstance(n,ast.FunctionDef):funcs.append(dict(name=n.name,line=n.lineno,end_line=n.end_lineno,source='\n'.join(src.splitlines()[n.lineno-1:n.end_lineno]),calls=[dict(line=k.lineno,expression=ast.unparse(k.func)) for k in ast.walk(n) if isinstance(k,ast.Call)]))
write(Q/'PASSIVE_SOURCE_AST.json',dict(at=now(),publisher=row(S),body_node_count=len(tree.body),AST_node_count=sum(1 for n in ast.walk(tree)),functions=funcs,imports=[ast.unparse(n) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))],candidate_import_execute=0))
old=ROOT/'Dispatcher/CANDIDATES/G05R37-de39916a/scratch/OperatorStartupPairR29/publish_operator_pair.py';p=Q/'ACTUAL_R37_R38_SOURCE_DIFF.txt';assert not p.exists();p.write_bytes(''.join(difflib.unified_diff(old.read_bytes().decode('utf-8').splitlines(True),src.splitlines(True),fromfile=str(old),tofile=str(S))).encode('utf-8'))
oracle=load(ORACLE);up1={c['case_id']:c for c in load(oracle['literal_pair']['path'])['prospective_cases']};up2={c['case_id']:c for c in load(oracle['literal_combined']['path'])['pair_cases']};master={(r['case_id'],r['role']):r for r in load(RAWWIT)['original_raw12']};out=[]
for c in oracle['cases']:
    for inp in c['inputs']:
        cid=c['case_id'];role=inp['role'];raw=inp['raw_config_expected'];b=raw['utf8_text'].encode('utf-8');assert hashlib.sha256(b).hexdigest().upper()==raw['sha256'] and len(b)==raw['bytes'] and b.hex().upper()==raw['hex'];decoded=json.loads(b.decode('utf-8'))
        for up in [up1[cid],up2[cid]]:
            ur=up['independently_supplied_'+role+'14_7']['raw_config'];assert ur['utf8_text']==raw['utf8_text'] and ur['sha256']==raw['sha256'];assert json.loads(ur['utf8_text'])==decoded
        expected_utc='2026-10-11T00:00:00.1234567Z' if role=='parent' else '2026-10-11T00:00:01.0000000Z';assert decoded['issuedAtUtc']==expected_utc
        mr=master[(cid,role)];assert mr['raw_sha256']==raw['sha256'] and mr['raw_bytes']==raw['bytes'] and mr['issuedAtUtc_raw']==expected_utc and mr['operatorPairId']==c['expected_aux4']['operatorPairId']
        legacy=inp['config14'];diff={k:dict(recorded=legacy.get(k),raw_decoded=decoded.get(k)) for k in set(legacy)|set(decoded) if legacy.get(k)!=decoded.get(k)}
        out.append(dict(case_id=cid,role=role,raw_sha256=raw['sha256'],raw_bytes=raw['bytes'],issuedAtUtc_raw=decoded['issuedAtUtc'],config14_raw_decoded=decoded,legacy_recorded_config14=legacy,legacy_metadata_differences=diff,original_descriptor7=inp['original_descriptor7'],prospective_descriptor7=inp['prospectively_approved_new_fixture_descriptor7'],operatorPairId_original=c['expected_aux4']['operatorPairId'],both_upstream_raw_match=True,Master_raw_witness_match=True,old_files_changed=False))
write(Q/'TIMESTAMP_RAW_CORRECTION_ASSESSMENT.json',dict(at=now(),correction=row(CORR),Master_witness=row(RAWWIT),oracle=row(ORACLE),upstreams=[oracle['literal_pair'],oracle['literal_combined']],raw12=out,all_children_original_seven_zero_fraction=True,previous_QA_prose='INCORRECT_CHILD_01Z_USED_RECORDED_TYPED_VIEW_INSTEAD_OF_RAW_DECODE',correction_disposition='ADOPTED_FROM_INDEPENDENT_RAW_UTF8_HASH_BYTES_DECODE',old_QA_oracles_reports_unchanged=True,no_new_expected_fixture=True))
print(json.dumps(dict(publisher=row(S),full_texts=len(texts),body_nodes=len(tree.body),AST_nodes=sum(1 for n in ast.walk(tree)),functions=len(funcs),raw12_match=True,child_utc=out[1]['issuedAtUtc_raw'],legacy_differences=[dict(case_id=r['case_id'],role=r['role'],diff=r['legacy_metadata_differences']) for r in out if r['legacy_metadata_differences']],all_candidate_execution=0),ensure_ascii=False))
