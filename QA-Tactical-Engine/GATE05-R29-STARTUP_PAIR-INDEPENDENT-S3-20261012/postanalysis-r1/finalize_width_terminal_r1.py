"""New postrun metadata continuation; no old helper execution or candidate calls."""
from pathlib import Path
import sys,re,difflib,traceback
A=Path(__file__).resolve().parent
sys.path.insert(0,str(A.parent))
from review_setup import *
NOTICE=PKG/'MASTER_R29_S3_FINAL_WIDTH_SOURCE_AND_TERMINAL_CONTINUATION_20261012.md'
PARTIAL=PKG/'coordination/MASTER_R29_S3_FINAL_WIDTH_STOP_PARTIAL_SUCCESS_PRESERVATION_20261012.json'
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R29_Startup_Pair_Independent_S3_20261012.md'
def verify(rows):
    for r in rows:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(p)
def count_graph(x):
    children=list(x.values()) if isinstance(x,dict) else x if isinstance(x,list) else []
    parts=[count_graph(v) for v in children]
    return (1+sum(v[0] for v in parts),(0 if isinstance(x,(dict,list)) else 1)+sum(v[1] for v in parts))
def guard():
    assert sha(NOTICE)=='4517C5F7248C8AF1DA1BE77F5B87E7C333CE870170154102E6E2BE4C4EE8C142'
    verify(load(PARTIAL)['files']);verify(load(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')['pins'])
    assert load(A/'finalize_review_prepare.TOOL.json')['exit_code']==1
    assert load(A/'post_analysis.TOOL.json')['exit_code']==0
    f=load(A/'PRESERVATION_FINAL.json');verify(f['protected_files']);verify(f['frozen_files'])
    assert len(f['protected_files'])==14365 and len(f['frozen_files'])==132
    for al in load(Q/'RUN_ALLOCATION_PLAN.json')['allocations']:
        out=Path(al['output_root']);d=load(out/'OUTPUT_INVENTORY.json');verify(d['files'])
        assert {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}=={r['relative_path'] for r in d['files']}
        assert len(d['files'])==402
def metrics():
    guard();assert not REPORT.exists() and not (Q/'COMPLETION.json').exists()
    source=FROZEN/'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs'
    assert sha(source)=='391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1'
    mapping=next(r for r in load(MAN)['files'] if Path(r['frozen_path'])==source)
    assert mapping['sha256']==sha(source) and mapping['bytes']==source.stat().st_size
    lineages=load(Q/'R29_FROZEN_LINEAGE.json')['candidates']
    for candidate in lineages:
        doc=next(d for d in candidate['documents'] if Path(d['frozen_source_path'])==source)
        assert doc['matched'] and doc['actual_sha256']==sha(source)
    raw=source.read_bytes();s=raw.decode('utf-8-sig');needle='public class ValidatorTask';assert s.count(needle)==1
    start=s.index(needle);opening=s.index('{',start);depth=0;end=None
    for i in range(opening,len(s)):
        if s[i]=='{':depth+=1
        elif s[i]=='}':
            depth-=1
            if depth==0:end=i+1;break
    assert end is not None
    scope=s[start:end]
    fields=re.findall(r'public\s+(string|long|int|bool)\s+(\w+)\s*=',scope)
    assert len(fields)==27 and len({n for t,n in fields})==27
    expected={'simulatorGeneration':'long','workerGeneration':'long','resultEpoch':'long','targetMapIndex':'int','isConsumed':'bool'}
    actual={n:t for t,n in fields};assert all(actual[n]==t for n,t in expected.items())
    old=A/'finalize_review.py';new=Path(__file__)
    diff=''.join(difflib.unified_diff(old.read_text(encoding='utf-8-sig').splitlines(True),new.read_text(encoding='utf-8-sig').splitlines(True),fromfile='original-failed-finalize-TEXT-only',tofile='new-width-terminal-metadata-only'))
    dp=A/'WIDTH_TERMINAL_R1_SOURCE_DIFF.txt';assert not dp.exists();dp.write_bytes(diff.encode('utf-8'))
    write(A/'WIDTH_TERMINAL_R1_POSTRUN_SOURCE_PIN.json',dict(at=now(),helper=row(new),old_helper_TEXT_only=row(old),diff=row(dp),notice=row(NOTICE),partial_success_manifest=row(PARTIAL),actual_frozen_source=row(source),frozen_mapping=mapping,prebuild_oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),postrun_only=True,expected_changed=False,candidate_calls=0))
    write(A/'VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json',dict(at=now(),source=row(source),class_scope=scope,line_start=s[:start].count('\n')+1,line_end=s[:end].count('\n')+1,fields=[dict(name=n,CLR_source_type=t) for t,n in fields],required_widths=expected,PDB_source_both4of4=True,scope='SOURCE-only declared CLR types; normal JSON Integer comparisons and compiler typed references separate. No runtime edge/native width assertion.'))
    oracle=load(Q/'NORMAL_EXPECTED_ORACLE.json');counts=[]
    for fam,key,graph in [('PAIR','pair_cases','expected_full_observation_graph'),('Capture','normal_pairs','expected_observation_envelope')]:
        for c in oracle[key]:
            n,l=count_graph(c[graph]);counts.append(dict(case_id=c['case_id'],family=fam,hierarchical_nodes=n,scalar_leaves=l,phases=3))
    assert sum(c['hierarchical_nodes']*3 for c in counts)==6636
    write(A/'WIDTH_COVERAGE_COUNTERS_AND_LIMITATIONS_R1.json',dict(at=now(),case_counts=counts,per_run_assertions=438,assertion_split=dict(Pair=270,Capture=168),typed_rows=6700,Pair=3708,Capture_graphs=2928,descriptor_purity=64,per_run_ledger_rows=584,categories=dict(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18),indirect='Source calls two byte factories inside AdmitPairBytes:12 for six primary admits. Source-derived, not dynamic call tracing; grouped/manual ledger excludes uncounted internal/native calls.',width_witness=row(A/'VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json'),copy_limit='Pair detached IDs in-place; Capture IDs holder replacement only. No readonly exception/rejection.',runtime='Environment.Version and loaded managed corelib identity observed; native CLR modules UNOBSERVED.',candidate_extra_execution=0))
    write(A/'RESUME_ACK_RETURN_CAPTURE_LIMITATION.json',dict(at=now(),resume_ACK=row(A/'RESUME_ACK.json'),original_ACK=row(Q/'ACK_INITIAL.json'),actual_direct_send_return_observed_in_chat=True,independent_original_serialized_return_file='NOT_CAPTURED',no_fabricated_return_dict=True,Master_actual_direct_ACK_receipt='Separate Master evidence; not independently inferred from own transcribed threadId return',old_manually_transcribed_notice_tool_proofs='Original retained; tool-return text reconstructions, not independently captured API wire bytes.'))
    draft=A/'REPORT_DRAFT.md';text=draft.read_text(encoding='utf-8')
    fixes=[('최종 타입 폭 소스 witness의 자체 파일 선택 오류 정정은 Master disposition 대기 중이다.','최종 타입 폭 witness는 Master 승인된 새 metadata-only continuation에서 실제 frozen Census class scope를 읽어 완결했다. 원래 실패 exit1과 성공 partial artifacts는 불변이다.'),('마지막 width selection 정정은 이 draft 작성 시 pending이다.','마지막 width selection은 실제 mapped EngineHostCensus.cs의 unique ValidatorTask class72..101, long3/int1/bool1로 후속 witness를 작성했다. SOURCE-only이며 runtime edge/native evidence로 확대하지 않는다.')]
    for a,b in fixes:
        assert text.count(a)==1;text=text.replace(a,b)
    text+='\n\n추가 소스 witness와 node/leaf 후처리 수치는 `VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json`, `WIDTH_COVERAGE_COUNTERS_AND_LIMITATIONS_R1.json`에 기록했다. Pre-run oracle을 바꾸지 않았다. API return 증거 일부는 chat tool-returned text를 옮긴 reconstruction이며 원래 wire bytes/serialized return 파일을 독립 보존했다고 주장하지 않는다. 실제 terminal return은 구조화된 tool return을 별도 파일로 보존한다.\n\n| Family/case | 전체 nodes/phase | scalar leaves/phase | phases |\n|---|---:|---:|---:|\n'
    for c in counts:text+=f"| {c['family']}/{c['case_id']} | {c['hierarchical_nodes']} | {c['scalar_leaves']} | 3 |\n"
    assert not REPORT.exists();REPORT.write_bytes(text.encode('utf-8'))
    write(A/'WIDTH_TERMINAL_R1_REPORT_BINDING.json',dict(at=now(),draft=row(draft),final_report=row(REPORT),width=row(A/'VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json'),counters=row(A/'WIDTH_COVERAGE_COUNTERS_AND_LIMITATIONS_R1.json'),original_failure_exit=1,additional_test_calls=0,normal_unit='PASS_SCOPED',High3='OPEN',nativeE2='NOT_RELEASED',Master='PENDING'))
    print(json.dumps(dict(widths=expected,class_start_line=72,fields=27,case_counts=counts,report=row(REPORT),old_failure_preserved=True,candidate_calls=0)))
def seal():
    guard();assert load(A/'WIDTH_TERMINAL_R1_metrics_TOOL.json')['exit_code']==0
    verify(load(A/'WIDTH_TERMINAL_R1_POSTRUN_SOURCE_PIN.json')[k] for k in ['helper','old_helper_TEXT_only','diff','notice','partial_success_manifest','actual_frozen_source','prebuild_oracle'])
    assert not (Q/'COMPLETION.json').exists()
    initial=load(Q/'ACK_INITIAL.json');analysis=load(A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json');assert analysis['total_failed']==0
    cycles={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
    seal_logs={'WIDTH_TERMINAL_R1_seal_STDOUT.txt','WIDTH_TERMINAL_R1_seal_STDERR.txt','WIDTH_TERMINAL_R1_seal_TOOL.json'}
    files=[p for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in cycles|seal_logs and '__pycache__' not in p.parts]
    rows=[row(p) for p in files]+[row(REPORT)]
    write(Q/'EVIDENCE_MANIFEST.json',dict(at=now(),delivery_id=initial['delivery_id'],result_id=initial['result_id'],files=rows,file_count=len(rows),excluded_cycles=sorted(cycles),unfinished_actual_seal_logger_excluded=sorted(seal_logs),excluded_reason='Actual new outer seal first stdout/stderr and postreturn TOOL preserved separately; no unfinished stream hash claimed.',recursive_own_set=True,report=row(REPORT)))
    verify(rows)
    artifacts={k:row(p) for k,p in [('report',REPORT),('evidence_manifest',Q/'EVIDENCE_MANIFEST.json'),('normal_analysis',A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json'),('raw_crossculture',A/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json'),('counters',A/'WIDTH_COVERAGE_COUNTERS_AND_LIMITATIONS_R1.json'),('width',A/'VALIDATOR_TASK_SOURCE_WIDTH_WITNESS_R1.json'),('static',Q/'STATIC_SOURCE_SCOPE_BEFORE_BUILD.json'),('protected_final',A/'PRESERVATION_FINAL.json'),('final_output_verification',A/'FINAL_BOTH_RUN_INVENTORY_VERIFICATION.json'),('initial_ACK',Q/'ACK_INITIAL.json'),('resume_ACK',A/'RESUME_ACK.json')]}
    write(Q/'RESULT_INDEX.json',dict(at=now(),wp_id=initial['wp_id'],wp_revision='S3',delivery_id=initial['delivery_id'],result_id=initial['result_id'],status='COMPLETED_SCOPED_NORMAL_PASS_STATIC_REVISION_REQUIRED',verdict=analysis['verdict'],normal_unit='PASS_SCOPED',staticHigh3='OPEN',nativeE2='NOT_RELEASED',Foundation='HOLD',Master_adoption='PENDING',report_delivery='PENDING',artifacts=artifacts,execution=dict(QA_builds=1,normal_runs=2,assertions_each=438,failed=0,typed_each=6700,raw_expected_total=672,crossculture_pairs=336,production_build_modify=0,global_Awake_publisher_Process_native_game_adverse=0)))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),delivery_id=initial['delivery_id'],result_id=initial['result_id'],initial_ACK=row(Q/'ACK_INITIAL.json'),ACK_mirror=row(Q/'ACK.json'),resume_ACK=row(A/'RESUME_ACK.json'),result_index=row(Q/'RESULT_INDEX.json'),initial_pending_immutable=True,Master_adoption='PENDING'))
    write(Q/'RETURN_PENDING.json',dict(at=now(),target='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174',host='local',delivery='PENDING',no_unknown_delivery_retry=True,result_id=initial['result_id']))
    artifacts.update(result_index=row(Q/'RESULT_INDEX.json'),ACK_completion_binding=row(Q/'ACK_COMPLETION_BINDING.json'),return_pending=row(Q/'RETURN_PENDING.json'))
    verify(rows);verify(artifacts.values());guard()
    expected_paths={str(p) for p in files}
    actual_paths={str(p) for p in Q.rglob('*') if p.is_file() and p.name not in cycles|seal_logs and '__pycache__' not in p.parts}
    assert actual_paths==expected_paths
    completion=dict(schema_version=1,at=now(),wp_id=initial['wp_id'],wp_revision='S3',delivery_id=initial['delivery_id'],result_id=initial['result_id'],status='COMPLETED',verdict=analysis['verdict'],artifacts=artifacts,evidence_file_count=len(rows),normal_unit='PASS_SCOPED',staticHigh3='OPEN',runtimeE2='NOT_RELEASED',Foundation='HOLD',Master_adoption='PENDING',report_delivery='PENDING',QA_compile=1,QA_runs=2,candidate_rebuild=0,forbidden_calls=0,completion_last_atomic=True)
    temp=Q/'COMPLETION.json.tmp';assert not temp.exists();temp.write_bytes((json.dumps(completion,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));temp.rename(Q/'COMPLETION.json')
    print(json.dumps(dict(COMPLETION=row(Q/'COMPLETION.json'),report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),evidence_count=len(rows),status='COMPLETED_SCOPED_ONLY')))
if __name__=='__main__':
    mode=sys.argv[1];assert mode in ['metrics','seal']
    out=A/f'WIDTH_TERMINAL_R1_{mode}_STDOUT.txt';err=A/f'WIDTH_TERMINAL_R1_{mode}_STDERR.txt';proof=A/f'WIDTH_TERMINAL_R1_{mode}_TOOL.json'
    assert not out.exists() and not err.exists() and not proof.exists()
    code=0;so0,se0=sys.stdout,sys.stderr;started=now()
    with out.open('w',encoding='utf-8',newline='') as so,err.open('w',encoding='utf-8',newline='') as se:
        sys.stdout,sys.stderr=so,se
        try:
            if mode=='metrics':metrics()
            else:seal()
        except BaseException:code=1;traceback.print_exc()
        finally:sys.stdout,sys.stderr=so0,se0
    write(proof,dict(script=row(Path(__file__)),mode=mode,argv=list(sys.argv),cwd=str(Path.cwd()),started_at=started,finished_at=now(),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True,candidate_compiler_runner_calls=0))
    print(json.dumps(dict(mode=mode,exit_code=code,stdout=row(out),stderr=row(err),tool=row(proof))))
    sys.exit(code)
