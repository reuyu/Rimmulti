from qa_common import *
import sys
from unity_reference_metadata import read_object_methods
E1=FROZEN/'scratch/EngineGate05R31Lifecycle-b8d47a10'
OLD=ROOT/'Dispatcher/CANDIDATES/G05R30-16ce928f/scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
def w(p,a,z,label):
    b=p.read_bytes();v=b[a:z]
    return dict(id=label,file=row(p),byte_range=[a,z],line_range=[b[:a].count(b'\n')+1,b[:z].count(b'\n')+1],bytes=len(v),sha256=hashlib.sha256(v).hexdigest().upper(),raw_utf8=v.decode('utf-8'))
def method_witness(start,end,label):
    b=WORKER.read_bytes();a=b.index(start.encode());z=b.index(end.encode(),a+len(start));return w(WORKER,a,z,label)
def guard():
    assert load(Q/'bootstrap.TOOL.json')['exit_code']==0 and load(Q/'ACK_INITIAL.json')['delivery_id']==DELIVERY
    verify(load(MAN)['files'],'frozen_path')
def metadata_source():
    a=OLD.read_bytes();b=WORKER.read_bytes();scope=load(FT/'MASTER_R31_AUTHORIZED_SOURCE_SCOPE.json');producer=load(FT/'SOURCE_SCOPE_DIFF.json')
    assert sha(OLD)==scope['Worker_original']['sha256']=='B1F8C00D1DF6E8E797EAC8E5A7F7FB462679BA06E79096D5C558C687BD413311'
    spans=sorted(scope['allowed_byte_spans'],key=lambda r:r['start']);assert len(spans)==7
    previous=cursor=0;outside=[]
    for i,r in enumerate(spans+[dict(start=len(a),end=len(a))]):
        chunk=a[previous:r['start']];assert chunk and b.count(chunk)==1
        loc=b.find(chunk,cursor);assert loc>=0 and (i!=0 or loc==0)
        outside.append(dict(old_range=[previous,r['start']],new_range=[loc,loc+len(chunk)],bytes=len(chunk),sha256=hashlib.sha256(chunk).hexdigest().upper(),entire_bytes_equal=True))
        cursor=loc+len(chunk);previous=r['end']
    assert cursor==len(b) and len(outside)==8 and sum(r['bytes'] for r in outside)==260917
    changes=[];comparison=[]
    declared={v['span_id']:v for v in producer['authorized_spans']}
    for i,r in enumerate(spans):
        assert hashlib.sha256(a[r['start']:r['end']]).hexdigest().upper()==r['before_sha256']
        actual=w(WORKER,outside[i]['new_range'][1],outside[i+1]['new_range'][0],r['id']);changes.append(actual)
        p=declared[r['id']];comparison.append(dict(id=r['id'],actual_range=actual['byte_range'],declared_range=p['new_range'],actual_sha256=actual['sha256'],declared_sha256=p['new_sha256'],range_matches=actual['byte_range']==p['new_range'],sha_matches=actual['sha256']==p['new_sha256'],producer_original_range_matches=p['orig_range']==[r['start'],r['end']]))
    write(Q/'INDEPENDENT_SOURCE_BYTE_MAP.json',dict(at=now(),source=row(WORKER),old_source=row(OLD),scope=row(FT/'MASTER_R31_AUTHORIZED_SOURCE_SCOPE.json'),producer_map=row(FT/'SOURCE_SCOPE_DIFF.json'),entire_seven_changed=changes,entire_eight_outside=outside,outside_bytes=260917,all_outside_equal=True,producer_comparison=comparison,mismatch_policy='Keep genuine producer map discrepancies unchanged; independent actual map is review evidence, never rewrite original.'))
    dep=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046/MASTER_R5_MANAGED_QA_DEPENDENCIES_MANIFEST.json'
    assert sha(dep)=='7FCB91EEB8489365E4304AFFDC601CCD0CCE2259365FD861A785AD658C183481'
    refrow=next(r for r in load(dep)['files'] if Path(r['frozen_path']).name=='UnityEngine.CoreModule.dll');ref=Path(refrow['frozen_path'])
    assert sha(ref)==refrow['sha256'] and ref.stat().st_size==refrow['size']
    write(Q/'UNITY_REFERENCE_READER_INPUT_PIN.json',dict(at=now(),manifest=row(dep),input=row(ref),reader=row(Q/'unity_reference_metadata.py'),metadata_definition_provenance=row(Q/'METADATA_READER_DEFINITION_PROVENANCE.json'),scope='New independent byte binding/IL inspection only; no old verdict inheritance or Unity execution.'))
    observed=read_object_methods(ref);write(Q/'UNITY_REFERENCE_CUSTODY_IL.json',dict(at=now(),input=row(ref),dependency_manifest=row(dep),**observed,native_execution=0))
    print(json.dumps(dict(source_bytes=len(b),seven_changed=True,outside260917=True,wrong_producer_ranges=sum(not v['range_matches'] for v in comparison),wrong_producer_hashes=sum(not v['sha_matches'] for v in comparison),actual_maps=[dict(id=r['id'],range=r['byte_range']) for r in changes],new_Unity_binding=observed['reference_mvid'],candidate_calls=0)))
def provenance():
    assert load(Q/'review_metadata_source.TOOL.json')['exit_code']==0
    mapping={r['original_path'].lower():r for r in load(MAN)['files']};base={r['path'].lower():r for r in load(BASELINE)['files']}
    build=load(FT/'BUILD_INPUT_MANIFEST.json');dependencies=[]
    for r in build['compiler_dependencies']:
        if r['path'].lower() in mapping:p=Path(mapping[r['path'].lower()]['frozen_path'])
        else:
            assert r['path'].lower() in base
            p=Path(base[r['path'].lower()]['path']);verify([base[r['path'].lower()]])
        v=row(p);dependencies.append(dict(declared=r,actual_immutable_file=v,sha_matches=r['sha256']==v['sha256'],bytes_matches=r['bytes']==v['bytes'],evidence_discrepancy_not_repaired=True))
    host=load(E1/'HOST_TELEMETRY.json');runs=[];stdout=[];prepins=[]
    for i,r in enumerate(host['runs'],1):
        p=Path(mapping[r['execution_report_path'].lower()]['frozen_path']);rep=load(p)
        raw=Path(mapping[r['stdout_path'].lower()]['frozen_path']);binary=raw.read_bytes();supplement=binary.replace(b'\r\r\n',b'\r\n');supplement_sha=hashlib.sha256(supplement).hexdigest().upper()
        stdout.append(dict(culture=r['culture'],actual_raw=row(raw),declared_sha=r['stdout_sha256'],actual_matches_declared=sha(raw)==r['stdout_sha256'],CRCRLF_count=binary.count(b'\r\r\n'),read_only_CRCRLF_to_CRLF_sha=supplement_sha,supplement_matches_declared=supplement_sha==r['stdout_sha256'],original_rewritten=False,interpretation='Text-write newline translation visible in host source is only a mechanism hypothesis; actual and supplemental hashes do not automatically recover declared raw.'))
        report_time=datetime.datetime.fromisoformat(rep['timestamp_utc'].replace('Z','+00:00'));build_time=datetime.datetime.fromisoformat(build['generated_at'])
        pre=load(FT/f'PRE_RUN_MANIFEST_{i}.json');selected=pre['selected_debug_candidate'];runner=pre['runner_identity'];runnerfile=Path(mapping[runner['runner_exe_path'].lower()]['frozen_path'])
        prepins.append(dict(culture=r['culture'],prepin_file=row(FT/f'PRE_RUN_MANIFEST_{i}.json'),selected_sha_matches_current=selected['sha256']==sha(SELECTED),runner_sha_matches_current=runner['runner_exe_sha256']==sha(runnerfile),prospective_existence='UNOBSERVED: current declarations not before-execution existence proof',full_dependency_CLR_oracle_callplan_inputs='INCOMPLETE'))
        runs.append(dict(culture=r['culture'],producer_PID=r['pid'],producer_numeric_exit=r['exit_code'],raw_report=row(p),actual_identity={k:rep[k] for k in ['wp_id','wp_revision','dispatch_id','envelope']},Pair_labels=len(rep['pair_cases']),Capture_labels=len(rep['r27_regression_cases']),producer_internal_time=rep['timestamp_utc'],BUILD_INPUT_generated=build['generated_at'],declared_build_after_report_seconds=(build_time-report_time).total_seconds(),host_report_SHA_matches=r['execution_report_sha256']==sha(p),runtime_scope='Producer claimed positive pure observations only; no fresh independent runtime/E2'))
    hostsource=E1/'run_r31_battery.py';text=hostsource.read_text(encoding='utf-8-sig');assert 'stdout_b.decode("utf-8", errors="replace")' in text and 'with open(stdout_file, "w", encoding="utf-8")' in text
    fixtures=[]
    for n in range(1,7):
        spec=E1/f'PublishedPairs/case_{n:02d}/publish_spec.json';pub=E1/f'PublishedPairs/case_{n:02d}/PROVENANCE_MANIFEST.json';s=load(spec);p=load(pub)
        fixtures.append(dict(case=n,spec=row(spec),copied_provenance=row(pub),declared_parent_path=s['parentDeclaration']['expectedConfigPath'],declared_child_path=s['childDeclaration']['expectedConfigPath'],publishedAtUtc=p['publishedAtUtc'],publisher=p['publisher'],interpretation='Historical literal fixture/provenance copied; not proof of a new R31 publication or actual publisher execution.'))
    corpus=[]
    for p in sorted(FT.rglob('*')):
        if p.is_file() and p.suffix.lower() in {'.json','.md','.txt'}:corpus.append(dict(file=row(p),raw_utf8=p.read_text(encoding='utf-8-sig')))
    for p in [hostsource,E1/'Harness/Program.cs',FROZEN/'docs/WarEconomy_Master_Handoff_20261006/A_ENGINE_GATE05_R31_LIFECYCLE_REPORT_20261012.md']:
        corpus.append(dict(file=row(p),raw_utf8=p.read_text(encoding='utf-8-sig')))
    write(Q/'FROZEN_PRODUCER_TEXT_READ_AUDIT.json',dict(at=now(),files=corpus,entire_read=True,scripts_IMPORTED_EXECUTED=False))
    oldman=ROOT/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R30-HANDOFF-20261012-DIRECT-16ce928f/MASTER_GATE05_R30_HANDOFF_REVIEW_FREEZE_MANIFEST.json';old=verify(load(oldman)['files'],'frozen_path');assert len(old)==128
    ownboundary=load(FT/'MASTER_R31_AUTHORIZED_SOURCE_SCOPE.json')['new_owned_E1_root'];actual_host_root=str(ROOT/'scratch/EngineGate05R31Lifecycle-b8d47a10')
    write(Q/'PROVENANCE_REVIEW.json',dict(at=now(),verdict='EVIDENCE_HASH_MAP_BINDING_AND_FULL_GRAPH_REVISION_REQUIRED',build_manifest=row(FT/'BUILD_INPUT_MANIFEST.json'),dependencies=dependencies,dependency_mismatch_count=sum(not v['sha_matches'] for v in dependencies),stdout_bindings=stdout,stdout_mismatch_count=sum(not r['actual_matches_declared'] for r in stdout),supplement_not_original_binary_raw=True,host_source=row(hostsource),producer_runs=runs,current_prepin_declarations=prepins,actual_new_owned_root=actual_host_root,scope_new_owned_root=ownboundary,new_owned_boundary_implemented=ownboundary==actual_host_root,historical_fixture_provenance=fixtures,old_frozen128_verified=old,fulltyped_raw_copy='API contracts/fixture lists and selected-field sentinel tests; no whole expected/actual graph or phase-by-phase value/type/order/raw ledger',actual_loadedselected_MVID_CLR_corelib='UNOBSERVED',full_compiler_commands_source_references_toolhash_PID_streams_prospective_callplan_oracle='INCOMPLETE',no_hash_type_source_oracle_repair=True,candidate_compiler_runner_native_global_adverse_execution=0))
    print(json.dumps(dict(dependencies=len(dependencies),wrong_dependency_hashes=sum(not v['sha_matches'] for v in dependencies),wrong_dependency_sizes=sum(not v['bytes_matches'] for v in dependencies),wrong_stdout_hashes=sum(not r['actual_matches_declared'] for r in stdout),CRCRLF_supplement_still_mismatch=[not r['supplement_matches_declared'] for r in stdout],raw_R31_identities=[r['actual_identity'] for r in runs],new_owned_root=ownboundary==actual_host_root,declared_afterrun_seconds=[r['declared_build_after_report_seconds'] for r in runs],old_frozen128_preserved=True,candidate_calls=0)))
if __name__=='__main__':
    guard();mode=sys.argv[1]
    if mode=='metadata_source':metadata_source()
    elif mode=='provenance':provenance()
    else:raise ValueError(mode)
