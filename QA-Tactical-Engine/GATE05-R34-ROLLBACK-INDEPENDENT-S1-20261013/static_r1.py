from common import *
import re
assert load(Q/'bootstrap.TOOL.json')['exit_code']==0
old=ROOT/'Dispatcher/CANDIDATES/G05R33-d19c64a5/scratch/WorkerBridgeMod/Source/WorkerBridge.cs';a=old.read_bytes();b=WORKER.read_bytes()
assert len(a)==276524 and len(b)==276685 and a[:39056]==b[:39056] and a[45687:]==b[45848:]
dm=load(FT/'SOURCE_SCOPE_DIFF.json');d=dm['authorized_spans'];assert len(d)==1 and d[0]['orig_range']==[39056,45687] and d[0]['new_range']==[39056,45848]
assert d[0]['orig_sha256']==hashlib.sha256(a[39056:45687]).hexdigest().upper() and d[0]['new_sha256']==hashlib.sha256(b[39056:45848]).hexdigest().upper()
write(Q/'SOURCE_WHOLE_AWAKE_OUTSIDE_COMPARISON_R1.json',dict(at=now(),original=row(old),new=row(WORKER),original_range=[39056,45687],new_range=[39056,45848],original_span_sha=d[0]['orig_sha256'],new_span_sha=d[0]['new_sha256'],raw_utf8=b[39056:45848].decode('utf-8'),outside_bytes=269893,outside_prefix_sha=hashlib.sha256(b[:39056]).hexdigest().upper(),outside_suffix_sha=hashlib.sha256(b[45848:]).hexdigest().upper(),whole_outside_bitexact=True,producer_map_matches=True,CRCRLF_in_allowed_span=b'\r\r\n' in b[39056:45848],no_normalization=True))
s=b.decode('utf-8');lines=s.splitlines();anchors=[]
for lo,hi in [('internal static void CleanupOwnerPendingHandoff','        private TcpListener'),('        void Awake()','private void HandleUnityLogMessage'),('private void HandleUnityLogMessage','private void ListenLoop()'),('private void ListenLoop()','private string ProcessCommandMainThread'),('void OnDestroy()','public static class OperatorRolePathSelector')]:
    start=s.index(lo);end=s.index(hi,start);anchors.append(dict(start=lo,first_line=s[:start].count('\n')+1,raw_utf8=s[start:end]))
awake=b[39056:45848].decode('utf-8');n=awake.replace('\r','')
inner=n[n.index('                    catch\n'):n.index('\n            catch (Exception ex)\n')]
expected=['_startupInitializationComplete = false;','isRunning = false;','_staticStartupAborted = true;','throw;'];assert [inner.index(t) for t in expected]==sorted(inner.index(t) for t in expected)
for bad in ['.Stop(','.Abort(','Log.','logMessageReceived','Join(','Wait(','CleanupOwner']:assert bad not in inner
outer=n[n.index('\n            catch (Exception ex)\n'):]
tokens=['_startupInitializationComplete = false;','isRunning = false;','_staticStartupAborted = true;','Log.Error(', 'Application.logMessageReceived -=','listener?.Stop();','listenerThread?.Abort();','CleanupOwnerPendingHandoff(_retainedOwner);']
assert [outer.index(t) for t in tokens]==sorted(outer.index(t) for t in tokens)
assert n.count('listener?.Stop();')==n.count('listenerThread?.Abort();')==n.count('Application.logMessageReceived -=')==n.count('CleanupOwnerPendingHandoff(_retainedOwner);')==1
assert n.index('_activeAdmissionReceipt.IsValid()')<n.index('DebugSettings.fastEcology = false')<n.index('Application.logMessageReceived +=')<n.index('listener.Start();')<n.index('listenerThread.Start();')<n.index('_startupInitializationComplete = true;')
writers=[dict(line=i+1,source=v,context='\n'.join(lines[max(0,i-14):i+7])) for i,v in enumerate(lines) if '_staticStartupAborted = true' in v];assert len(writers)==6
findings=[
 ('S01','SUPPORTED_SOURCE_GAIN','Inner resource-start catch publishes incomplete/runningfalse/stickyabort under existing lock before immediate rethrow; Stop/Abort/log/callback/wait/owner cleanup removed from this path.'),
 ('S02','SUPPORTED_SOURCE_GAIN','C# lock unwinds on rethrow; outer catch synchronizes stickyabort separately, releases it before guarded log and callback/listener/thread cleanup. Each call appears once per outer path; no duplicate inner cleanup.'),
 ('S03','SUPPORTED_SOURCE_GAIN','Earlier receipt/policy/log/socket/thread construction failures reach outer flag publication before guarded log/independent cleanup attempts. Early priorabort/missingpair return paths remain before resource setup; log exception can reach same outer catch.'),
 ('S04','SUPPORTED_FIXED_GATE','Parentreceipt IsValid precedes fastEcology/callback/policy/resources. Durable mode-before-owner getter, managed ReferenceEquals/cohort/selectedspent/payload-only consume, unknownowner no borrowing all outside fixed.'),
 ('S05','SUPPORTED_FIXED_COMMIT_WITH_LIMIT','Shared final lock orders priorabort check/listener.Start/thread.Start/complete flag against six visible synchronized abort assignments. Transfer is not resource admission; successcommit vs postcommitabort distinct.'),
 ('S06','CLAIM_CORRECTION_REQUIRED_NOT_SOURCE_REBUILD','Blocking completely eliminated /100percent all-interleavings deadlock freedom unsupported: Start calls remain inside lock and BCL/OS/internal synchronization unmodeled. No actual deadlock/bypass/leak established.'),
 ('S07','CLAIM_SCOPE_CORRECTION','Caller has released startup lock before CleanupOwnerPendingHandoff, but helper acquires same internal lock for matching payload clear. Cleanup outside all locks is inaccurate; matching owner/null/no reset fixed.'),
 ('S08','SOURCE_ONLY_PARTIAL_START','Listener.Start throw and thread.Start throw publish own failclosed flags before outer cleanup; partial started resource teardown attempts guarded once. Stop/Abort may fail/block, so state publication is not native cleanup success.'),
 ('S09','OPEN_NATIVE_REENTRY_SCHEDULING','Listener/callback/client bodies have no visible startup lock or startup-held Join. ListenLoop can begin after Thread.Start before flag assignment; callback may be active during setup. No reentrancy/normal native timeline observed.'),
 ('S10','OPEN_POSTCOMMIT_NATIVE','Postcommit abort makes Update/M05 return but does not itself stop listener/client/callback. isRunning is plain cross-thread field; real visibility/unblock/thread exit and admitted postcommit scope require native evidence, not broad new repair inferred here.'),
 ('S11','SUPPORTED_FIXED_OWNER_ONDESTROY_WITH_LIMIT','Retained managed owner and finally cleanup fixed; unknown owner cannot borrow registered owner. Cleanup attempts/normal shutdown/native-null state remain untested, no crossowner kill/reset/schema added.'),
 ('S12','LAYOUT_NOT_SEMANTIC_FAILURE','CRCRLF only in allowed span and joined brace/method separator preserved raw; outside bitexact, compilation/PDB bound. Do not normalize or infer failure from layout.'),
 ('S13','NO_FULL_GATE_CLOSURE','PURE normal regression tests unchanged classes, not modified Awake/resources/authority/currenttask/provider/carrier/native. High4 and full/native E2 remain open; prose corrections alone need no production rebuild.')]
fs=[dict(id=i,status=k,observation=v) for i,k,v in findings]
paths=[('parentinvalid','RevokeReadiness then throw to outer; flags before guarded log/resourcescleanup, parent gate precedes subscription.'),('priorabortearly','Reads existing abort under lock; before acquire/setup sets incomplete/runningfalse and returns; sticky already true.'),('pairmissing','Requiredmode missing privatepair returns before side effects after flags/sticky lock; log failure also reaches outer guarded handler.'),('setup_policy_log_construction','Outer catches setup exception before commit; independently guarded attempts on null/unstarted resources after failure flags.'),('precommitabort','Final lock sees stickyabort; incomplete/runningfalse then throw; lock released and outer cleanup.'),('listenerstart_throw','Inner catch under lock publishes three flags then rethrows; no innerteardown, outer guarded cleanup after release.'),('threadstart_throw','Listener may be started; inner flags then unwind; outer once Stop/Abort attempts, actual native success unobserved.'),('successful_commit_postcommit_abort','Start both and complete under lock; later abort ordered after commit can hold Update/M05, native teardown not established.'),('cleanupthrows_unknownowner','Guarded logging/unsubscribe/Stop/Abort/helper independent for throws; blocking call can delay later attempts. Helper internal lock + no unsafe borrowed owner.')]
write(Q/'STATIC_ROLLBACK_ORDERING.json',dict(at=now(),source=row(WORKER),whole_scope=row(Q/'SOURCE_WHOLE_AWAKE_OUTSIDE_COMPARISON_R1.json'),anchors=anchors,abort_writers=writers,innercatch_raw_utf8=inner,outercatch_raw_utf8=outer,findings=fs,source_assessments=len(fs),failure_path_matrix=[dict(path=k,source_observation=v,execution='NOT_EXECUTED') for k,v in paths],verdict='R34_NARROW_ROLLBACK_SOURCE_GAINS_SUPPORTED_NATIVE_CLAIMS_UNSUPPORTED_NATIVE_UNTESTED',source_labels_not_tests=True,changed_lifecycle_execution=0))
cb=FT/'CALLBACK_LOCK_ORDER_REVIEW.md';claim=cb.read_bytes().decode('utf-8-sig');assert '100%' in claim and 'all thread interleavings' in claim
write(Q/'CLAIM_MATRIX.json',dict(at=now(),claims=fs,producer_callback_review=row(cb),producer_original_full_text=claim,universal_guarantee='UNSUPPORTED_NOT_ADOPTED',source_improvement_separate_from_prose=True,prose_correction_requires_candidate_rebuild=False,native_sync_unmodeled=True))
mapping={r['original_path'].lower():Path(r['frozen_path']) for r in load(MAN)['files']};bi=load(FT/'BUILD_INPUT_MANIFEST.json');inputs=[]
for key in ['input_source_files','generated_cs_documents','actual_resolved_compile_references','toolchain_executables_and_compiler_dlls']:
    for r in bi[key]:
        p=mapping.get(r['path'].lower(),Path(r['path']));v=row(p);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'];inputs.append(dict(category=key,declared=r,actual=v))
assert len(inputs)==133 and len(bi['actual_resolved_compile_references'])==120
outputs=[]
for r in load(FT/'BUILD_OUTPUT_MANIFEST.json')['outputs']:
    v=row(mapping[r['path'].lower()]);assert v['sha256']==r['sha256'] and v['bytes']==r['bytes'];outputs.append(dict(declared=r,actual=v))
assert len(outputs)==7
host=load(FT/'BUILD_HOST_TOOL_TELEMETRY.json');raw=[];commands=[]
for run in host['build_runs']:
    assert run['exit_code']==0
    for ch in ['stdout','stderr']:
        p=mapping[run[ch+'_path'].lower()];v=row(p);assert v['sha256']==run[ch+'_sha256'] and v['bytes']==run[ch+'_bytes'];raw.append(dict(configuration=run['configuration'],channel=ch,file=v))
    p=mapping[run['stdout_path'].lower()];t=p.read_bytes().decode('utf-8');cmd=[l for l in t.splitlines() if 'csc.exe /noconfig ' in l];assert len(cmd)==1
    refs=[m.group(1) or m.group(2) for m in re.finditer(r' /reference:(?:"([^"]+)"|(\S+))',cmd[0])];assert len(refs)==120
    measured=[row(Path(p)) for p in refs];assert {r['path'].lower():r['sha256'] for r in measured}=={r['path'].lower():r['sha256'] for r in bi['actual_resolved_compile_references']}
    server=[l for l in t.splitlines() if 'CompilerServer:' in l];commands.append(dict(configuration=run['configuration'],raw=row(p),exact_command=cmd[0],references=measured,compiler_server_lines=server,server_PID_startend='UNOBSERVED'))
texts=[]
for p in sorted(FROZEN.rglob('*')):
    if p.is_file() and p.suffix.lower() in {'.json','.md','.py','.cs','.csproj','.txt'}:texts.append(dict(**row(p),raw_utf8=p.read_bytes().decode('utf-8-sig'),TEXT_only=True))
write(Q/'PRODUCER_FULL_TEXT_READ_AUDIT.json',dict(at=now(),files=texts,producer_helper_EXEC_IMPORT=False))
owned=[r for r in load(MAN)['files'] if r['original_path'].lower().endswith('.py') and 'enginegate05r34rollback-a4d6866c' in r['original_path'].lower()];assert len(owned)==5
write(Q/'PROVENANCE_REVIEW.json',dict(at=now(),inputs133=inputs,outputs7=outputs,binary_raw4=raw,host=host,compiler_commands=commands,new_owned_helpers=owned,producer_prospective_time='INTERNAL_CHRONOLOGY_NOT_INDEPENDENTLY_OBSERVED_BEFORE_BUILD',server_identity='UNOBSERVED',recursive_output_graph='7 final outputs; owned helper placement/frozen75 do not prove full prospective recursive graph',producer_semantic_native=0,build_success_not_E2PASS=True))
(Q/'NEXT_MINIMAL_REPAIR.md').write_bytes(('Narrow R34 source fixes are supported: failclosed publication inside existing commit lock, rethrow releases caller lock, no inner native teardown, outer guarded cleanup attempts once. No new production rebuild is required solely to correct repeated universal deadlock/blocking prose. Correct documentation to visible source ordering and caller/helper internal lock scope; retain originals and provenance limits. No actual deadlock/leak/bypass/native cleanup success established. Native readiness requires a separately admitted exact candidate/normal owned resources/context/lifecycle evidence; existing native plan is planning only. Preserve Start-under-lock priorabort serialization pending any explicitly approved source scope, owner/cohort/selectedspent/stickyabort/no borrowedowner, fixed outside bytes. Unknown owner, postcommit abort, native callback/thread stop and normal shutdown remain untested. No registry/schema/global kill/reset. Master chooses next scope/closure; Foundation HOLD.\n').encode('utf-8'))
print(json.dumps(dict(source_assessments=len(fs),failure_paths=len(paths),outside269893=True,inner_StopAbort=0,failure_before_cleanup=True,outer_each_once=True,abort_writers=len(writers),inputs=133,outputs=7,raw_streams=4,actual_reference_counts=[len(c['references']) for c in commands],new_owned_helpers=len(owned),native_execution=0)))
