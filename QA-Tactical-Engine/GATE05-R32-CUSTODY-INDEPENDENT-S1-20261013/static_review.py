from common import *
from unity_reference_metadata import read_object_methods
import re
assert load(Q/'bootstrap.TOOL.json')['exit_code']==0
FT=FROZEN/'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R32-CUSTODY-20261012-DIRECT-64ad38e2'
scope=load(FT/'MASTER_R32_AUTHORIZED_SOURCE_SCOPE.json');old=ROOT/'Dispatcher/CANDIDATES/G05R31-b8d47a10/scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
a=old.read_bytes();b=WORKER.read_bytes();spans=scope['allowed_byte_spans'];outside=[];last=0;prev=0
for r in spans+[dict(start=len(a),end=len(a))]:
    chunk=a[last:r['start']];assert b.count(chunk)==1;pos=b.index(chunk);assert pos>=prev and b[pos:pos+len(chunk)]==chunk
    outside.append(dict(old_range=[last,r['start']],new_range=[pos,pos+len(chunk)],bytes=len(chunk),sha256=hashlib.sha256(chunk).hexdigest().upper(),matched=True));last=r['end'];prev=pos+len(chunk)
assert sum(r['bytes'] for r in outside)==263961
decl={r['span_id']:r for r in load(FT/'SOURCE_SCOPE_DIFF.json')['authorized_spans']};changed=[]
for i,r in enumerate(spans):
    oldbytes=a[r['start']:r['end']];assert hashlib.sha256(oldbytes).hexdigest().upper()==r['sha256']
    lo,hi=outside[i]['new_range'][1],outside[i+1]['new_range'][0];raw=b[lo:hi];actualsha=hashlib.sha256(raw).hexdigest().upper();d=decl[r['id']]
    assert d['new_range']==[lo,hi] and d['new_sha256']==actualsha and d['orig_range']==[r['start'],r['end']]
    changed.append(dict(id=r['id'],byte_range=[lo,hi],sha256=actualsha,raw_utf8=raw.decode('utf-8'),producer_matches=True))
write(Q/'SOURCE_FULL_SCOPE_COMPARISON.json',dict(at=now(),old_source=row(old),new_source=row(WORKER),scope=row(FT/'MASTER_R32_AUTHORIZED_SOURCE_SCOPE.json'),changed=changed,outside=outside,outside_bytes=263961,all_maps_correct=True))
ref=next(Path(r['frozen_path']) for r in load(DEP)['files'] if Path(r['frozen_path']).name=='UnityEngine.CoreModule.dll')
write(Q/'UNITY_REFERENCE_IL.json',dict(at=now(),input=row(ref),reader=row(Q/'unity_reference_metadata.py'),**read_object_methods(ref),native_execution=0))
findings=[
 dict(id='S01',verdict='SOURCE_GAIN',observation='Set/cleanup/acquire now reject managed null and use exact ReferenceEquals. Native-null wrapper no longer skips matching managed payload cleanup. Null/null cannot match. No owner borrowing.'),
 dict(id='S02',verdict='SOURCE_GAIN',observation='Mode from durable marker before gameObject getter. Unknown retained owner remains null; required acquire fails/aborts without borrowing another owner. Update/M05 remain held; actual getter failure not observed.'),
 dict(id='S03',verdict='SOURCE_GAIN',observation='Prior abort checked under lock before acquire; acquire checks abort before transfer and clears only safely matching owner payload. Already-aborted legitimate owner cannot initialize via the R31 source countermodel.'),
 dict(id='S04',verdict='OPEN_SOURCE_CONCURRENCY_INTERVAL',observation='Successful acquire releases lock before logging/fastEcology/callback/policy/listener/thread setup. Another source path can mark abort during that interval; no atomic resource admission/recheck at listener start. Ordinary Unity-main-thread serialization is not independently proven. No actual concurrent/native execution.'),
 dict(id='S05',verdict='SOURCE_GAIN',observation='Awake catch sets incomplete/isRunning=false/sticky abort then guarded logging and independent callback/listener/thread/matching-payload cleanup attempts; log/cleanup throw cannot stop later listed own attempts. No Thread.Abort/native rollback success proof.'),
 dict(id='S06',verdict='SOURCE_GAIN',observation='OnDestroy uses retained owner, guarded error log and finally sets own isRunning=false and attempts resources; no this.gameObject getter, no selected/spent/abort reset.'),
 dict(id='S07',verdict='OPEN_UNKNOWN_OWNER_LIMIT',observation='Getter failure/unknown owner cannot legitimately clear another managed owner payload. Failclosed hold is evidenced in source; matching cleanup may remain unavailable. No native lifetime adoption.'),
 dict(id='S08',verdict='OPEN_LEGACY_OUTSIDE_SCOPE',observation='Old invalid-parent direct return occurs after callback subscription; remains outside four spans. RevokeReadiness/Process paths not executed. Do not claim all legacy startup paths rolled back or unchanged failure semantics.'),
 dict(id='S09',verdict='SOURCE_GAIN_WITH_STATE_QUALIFICATION',observation='Mode/registration-spent never reset, payload transferred atomically and cleared separately. Null payload does not encode distinct consume/ordinary-closed/failure history; no new schema required by QA.'),
 dict(id='S10',verdict='OPEN_NATIVE_AND_OTHER_HIGHS',observation='Bootstrap/Update/M05/PURE/carrier/publisher bodies fixed. Synchronous AddComponent/Awake propagation, socket/thread teardown/native pointer/event order not observed. High carrier/publisher/native/E1lineage closure not implied.'),
 dict(id='S11',verdict='SOURCE_BOUNDARY_QUALIFICATION',observation='Set does not check global abort before registering an as-yet-unspent record, but acquisition rejects prior abort and resource entry holds. No payload admission/reinitialization bypass proven; lifetime registration remains bounded.'),
]
full=b.decode('utf-8');anchors=[]
for start,end in [('        void Awake()','        private void HandleUnityLogMessage'),('        void Update()','            // Enforce fastEcology suppression'),('        void OnDestroy()','    public static class OperatorRolePathSelector')]:
    lo=full.index(start);hi=full.index(end,lo);anchors.append(dict(start=start,raw_utf8=full[lo:hi],first_line=full[:lo].count('\n')+1))
write(Q/'STATIC_CUSTODY_RESOURCE_REVIEW.json',dict(at=now(),source=row(WORKER),findings=findings,anchors=anchors,source_case_count=len(findings),changed_lifecycle_execution=0,verdict='SOURCE_GAINS_CREDITED_CONCURRENCY_LEGACY_UNKNOWN_OWNER_NATIVE_OPEN',Foundation='HOLD'))
write(Q/'CLAIM_MATRIX.json',dict(at=now(),claims=findings,source_case_labels_not_runtime_tests=True,Master_inputs_challenged=True,no_closure=True))
mapping={r['original_path'].lower():Path(r['frozen_path']) for r in load(MAN)['files']};build=load(FT/'BUILD_INPUT_MANIFEST.json');inputs=[]
for key in ['input_source_files','generated_cs_documents','actual_resolved_compile_references','toolchain_executables_and_compiler_dlls']:
    for r in build[key]:
        p=mapping.get(r['path'].lower(),Path(r['path']));v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'],r['path'];inputs.append(dict(category=key,declared=r,observed=v,matched=True))
assert len(inputs)==19
host=load(FT/'BUILD_HOST_TOOL_TELEMETRY.json');raw=[]
for run in host['build_runs']:
    assert run['exit_code']==0
    for channel in ['stdout','stderr']:
        p=mapping[run[channel+'_path'].lower()];v=row(p);assert v['sha256']==run[channel+'_sha256'] and v['bytes']==run[channel+'_bytes'];raw.append(dict(configuration=run['configuration'],channel=channel,file=v,matched=True))
    p=mapping[run['stdout_path'].lower()];txt=p.read_bytes().decode('utf-8',errors='replace');commands=[ln for ln in txt.splitlines() if 'csc.dll' in ln or 'CompilerServer:' in ln];print('\n'.join(commands))
    assert any('server processed compilation' in ln for ln in commands)
    write(Q/('PRODUCER_'+run['configuration'].upper()+'_COMPILER_TEXT.json'),dict(input=row(p),diagnostic_commands=commands,read_full=True,decode_replacement_count=txt.count('\ufffd'),actual_fresh_csc_PID='UNOBSERVED'))
texts=[]
for p in sorted(FROZEN.rglob('*')):
    if p.is_file() and p.suffix.lower() in {'.json','.md','.py','.cs','.csproj'}:texts.append(dict(**row(p),raw_utf8=p.read_bytes().decode('utf-8-sig'),TEXT_only=True))
write(Q/'PRODUCER_TEXT_READ_AUDIT.json',dict(at=now(),files=texts,top_level_producer_EXEC_IMPORT=False))
write(Q/'PROVENANCE_REVIEW.json',dict(at=now(),producer_input19=inputs,binary_streams=raw,host=host,producer_declared_chronology='internally consistent, not QA observed before compile',compiler_server_processed=True,fresh_compiler_PID_start_end='UNOBSERVED',full_framework_refs_prospectively_pinned_by_producer=False,producer_recursive_helper_graph='INCOMPLETE',producer_unit_native_execution=0,producer_BUILD_ONLY_not_PASS=True,R31_errors_not_rewritten=True))
(Q/'NEXT_MINIMAL_REPAIR.md').write_bytes(b'Retain managed-custody, mode-before-getter, prior-abort acquire gate, guarded own Awake/OnDestroy cleanup and spent/mode monotonicity. Independently bound normal PURE regression does not execute changed lifecycle. Before native closure, Master must resolve/observe abort-to-resource concurrency interval, unknown owner cleanup limit, legacy invalid-parent callback return and actual native event/resource ownership/teardown. Preserve compiler-server/prospective-framework/recursive-helper provenance limits; no retrospective proof. No new WP/schema/policy/reset/global kill/closure is made here. Foundation HOLD.\n')
print(json.dumps(dict(source_findings=len(findings),outside263961=True,producer_maps_correct4=True,input19matched=True,binary4matched=True,PURE_identity_whitelist_admitted=True,candidate_calls=0)))
