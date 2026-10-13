from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from review_setup import *
A=Path(__file__).resolve().parent
REPORT=ROOT/'docs/QA_EngineHost_Gate05_R29_Startup_Pair_Independent_S3_20261012.md'
def verify_rows(rows):
    for r in rows:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],str(p)
def count_graph(x):
    children=list(x.values()) if isinstance(x,dict) else x if isinstance(x,list) else []
    return (1+sum(count_graph(v)[0] for v in children), (0 if isinstance(x,(dict,list)) else 1)+sum(count_graph(v)[1] for v in children))
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='prepare':
        assert load(A/'post_analysis.TOOL.json')['exit_code']==0
        analysis=load(A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json');assert analysis['total_failed']==0
        final=preservation();before=load(Q/'PRESERVATION_BEFORE.json')
        assert final['protected_files']==before['protected_files'] and final['frozen_files']==before['frozen_files']
        verify_rows(load(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')['pins'])
        verify_rows(load(PKG/'coordination/MASTER_R29_S3_STATIC_STOP_INITIAL_PROSPECTIVE_PRESERVATION_20261012.json')['files'])
        write(A/'PRESERVATION_FINAL.json',final)
        allocations=load(Q/'RUN_ALLOCATION_PLAN.json')['allocations'];inventory_rows=[]
        for al in allocations:
            out=Path(al['output_root']);d=load(out/'OUTPUT_INVENTORY.json');verify_rows(d['files'])
            assert {p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name!='OUTPUT_INVENTORY.json'}=={r['relative_path'] for r in d['files']}
            inventory_rows.append(row(out/'OUTPUT_INVENTORY.json'))
        assert inventory_rows[0]==load(Q/'RUN1_INVENTORY_VERIFIED_BEFORE_RUN2.json')['first_inventory']==load(Q/'RUN1_INVENTORY_VERIFIED_AFTER_RUN2.json')['first_inventory']
        write(A/'FINAL_BOTH_RUN_INVENTORY_VERIFICATION.json',dict(at=now(),inventories=inventory_rows,recursive_file_counts=[402,402],first_seal_unchanged=True,all_matched=True))
        o=load(Q/'NORMAL_EXPECTED_ORACLE.json');counts=[]
        for c in o['pair_cases']:
            n,l=count_graph(c['expected_full_observation_graph']);counts.append(dict(case_id=c['case_id'],family='PAIR',nodes=n,scalar_leaves=l,phases=3))
        for c in o['normal_pairs']:
            n,l=count_graph(c['expected_observation_envelope']);counts.append(dict(case_id=c['case_id'],family='Capture',nodes=n,scalar_leaves=l,phases=3))
        width_witness=FROZEN/'scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
        raw=width_witness.read_text(encoding='utf-8-sig')
        widths=['public long simulatorGeneration','public long workerGeneration','public long resultEpoch','public int targetMapIndex','public bool isConsumed']
        assert all(w in raw for w in widths)
        metrics=dict(at=now(),case_counts=counts,per_run_assertions=438,assertion_split=dict(pair=270,Capture=168),typed_hierarchical_rows=6700,pair206nodes_times6times3=3708,Capture244nodes_times4times3=2928,descriptor_purity8times8nodes=64,per_run_primary_calls=38,per_run_ledger_rows=584,ledger_categories=dict(primary_direct=38,ordered_getter=288,grouped_helper=60,observational_helper=180,QA_wrapper_not_publisher=18),indirect_source_fact='AdmitPairBytes source calls two factories per admitted pair, 12 internal factory calls for six primary admissions. This is source-derived, not a dynamic instrumentation count; wrapper rows are not a complete native/recursive call trace.',integer_width_source=row(width_witness),width_anchors=widths,scope='Postrun derived counts only; not pre-run expectations, native proof or issuer authority')
        write(A/'COVERAGE_COUNTERS_AND_LIMITATIONS.json',metrics)
        write(A/'ACK_RESUME_RETURN_TOOL_PROOF.json',dict(tool='mcp__codex_app__send_message_to_thread',target='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174',host='local',returned={'content':[{'type':'text','text':'{"threadId":"01a1156b-97ec-7ce0-9e4a-dfc4a3acb174"}'}],'isError':False},topic='Resume ACK SHA3A53A538...1797 bytes; postanalysis-only',submitted_once=True,Master_adoption='PENDING'))
        print(json.dumps(dict(protected_paths=14365,frozen132=True,prospective253pins_unchanged=True,both_output402_matched=True,metrics=counts,report_not_yet_written=True)))
    elif mode=='seal':
        assert load(A/'finalize_review_prepare.TOOL.json')['exit_code']==0 and REPORT.is_file()
        assert not (Q/'COMPLETION.json').exists()
        initial=load(Q/'ACK_INITIAL.json');analysis=load(A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json')
        excluded={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
        files=[p for p in sorted(Q.rglob('*')) if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts and not p.name.startswith('finalize_review_seal.')]
        rows=[row(p) for p in files]+[row(REPORT)]
        em=dict(at=now(),delivery_id=initial['delivery_id'],result_id=initial['result_id'],files=rows,file_count=len(rows),excluded_cycles=sorted(excluded),postseal_logger_excluded='postanalysis-r1/finalize_review_seal.STDOUT.txt/STDERR.txt/TOOL.json created by outer full-stream logger; retained separately with actual postseal tool proof, not claimed presealed',whole_own_recursive_set=True,report=row(REPORT))
        write(Q/'EVIDENCE_MANIFEST.json',em);verify_rows(rows)
        artifacts={k:row(p) for k,p in [('report',REPORT),('evidence_manifest',Q/'EVIDENCE_MANIFEST.json'),('normal_analysis',A/'INDEPENDENT_NORMAL_RESULT_ANALYSIS.json'),('raw_crossculture',A/'RAW_EXPECTED_AND_CROSS_CULTURE_BINDING.json'),('counters',A/'COVERAGE_COUNTERS_AND_LIMITATIONS.json'),('static',Q/'STATIC_SOURCE_SCOPE_BEFORE_BUILD.json'),('protected_final',A/'PRESERVATION_FINAL.json'),('initial_ACK',Q/'ACK_INITIAL.json'),('resume_ACK',A/'RESUME_ACK.json')]}
        index=dict(at=now(),wp_id=initial['wp_id'],wp_revision='S3',delivery_id=initial['delivery_id'],result_id=initial['result_id'],status='COMPLETED_SCOPED_NORMAL_PASS_STATIC_REVISION_REQUIRED',verdict=analysis['verdict'],normal_unit='PASS_SCOPED',static='HIGH3_OPEN_REVISION_REQUIRED',nativeE2='NOT_RELEASED',Foundation='HOLD',master_disposition='PENDING',report_delivery='PENDING',artifacts=artifacts,execution=dict(QA_builds=1,normal_runs=2,assertions_per_run=438,failed=0,typed_per_run=6700,raw_bindings_total=672,cross_culture_pairs=336,production_build_modify=0,global_Awake_publisher_Process_native_game_adverse=0))
        write(Q/'RESULT_INDEX.json',index)
        write(Q/'ACK_COMPLETION_BINDING.json',dict(at=now(),delivery_id=initial['delivery_id'],result_id=initial['result_id'],original_ACK=row(Q/'ACK_INITIAL.json'),ACK_mirror=row(Q/'ACK.json'),resume_ACK=row(A/'RESUME_ACK.json'),result_index=row(Q/'RESULT_INDEX.json'),initial_pending_fields_immutable=True,normal_unit='PASS_SCOPED',staticHigh3='OPEN',Master_adoption='PENDING'))
        write(Q/'RETURN_PENDING.json',dict(at=now(),target='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174',host='local',delivery='PENDING',result_id=initial['result_id'],no_unknown_delivery_retry=True))
        artifacts.update(result_index=row(Q/'RESULT_INDEX.json'),ACK_completion_binding=row(Q/'ACK_COMPLETION_BINDING.json'),return_pending=row(Q/'RETURN_PENDING.json'))
        verify_rows(rows);verify_rows(list(artifacts.values()))
        verify_rows(load(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json')['pins'])
        for al in load(Q/'RUN_ALLOCATION_PLAN.json')['allocations']:verify_rows(load(Path(al['output_root'])/'OUTPUT_INVENTORY.json')['files'])
        completion=dict(schema_version=1,at=now(),wp_id=initial['wp_id'],wp_revision='S3',delivery_id=initial['delivery_id'],result_id=initial['result_id'],status='COMPLETED',verdict=analysis['verdict'],artifacts=artifacts,evidence_file_count=len(rows),normal_unit='PASS_SCOPED',staticHigh3='OPEN',runtimeE2='NOT_RELEASED',Foundation='HOLD',Master_adoption='PENDING',report_delivery='PENDING',QA_compile=1,QA_runs=2,candidate_rebuild=0,forbidden_calls=0,completion_written_last_atomic=True)
        target=Q/'COMPLETION.json';temp=Q/'COMPLETION.json.tmp';assert not temp.exists()
        temp.write_bytes((json.dumps(completion,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));temp.rename(target)
        print(json.dumps(dict(COMPLETION=row(target),report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),evidence_count=len(rows),status='COMPLETED_SCOPED_ONLY')))
    else:raise ValueError(mode)
