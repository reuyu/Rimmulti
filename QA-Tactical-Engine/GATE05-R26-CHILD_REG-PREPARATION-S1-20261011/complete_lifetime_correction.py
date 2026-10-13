from bootstrap_review import R,Q,load,sha,write,now
import re,hashlib,json
S=R/'Dispatcher/CANDIDATES/G05R25-dd341868/scratch/WorkerBridgeMod/Source/WorkerBridge.cs'
p=Q/'LIFETIME_SOURCE_MAP.json';archive=Q/'LIFETIME_SOURCE_MAP.initial_lookup_draft.json';assert archive.exists() and sha(archive)==sha(p)
d=load(archive);b=S.read_bytes();src=b.decode('utf-8-sig');updated=[]
needles=dict(RevokeReadiness='            currentValidatorTask = null;',DoSingleScopedTick='                    currentValidatorTask = null;',HandleRegisterGrant='                currentValidatorTask = null;',HandleResetWorker='            currentValidatorTask = null;',HandleSealResult='            currentValidatorTask = null;',HandleStageSave='            currentValidatorTask = task;',HandleLoadSave='            currentGeneration++;',HandleCompleteStageValidation='                currentValidatorTask.isConsumed = true;',OnDestroy='            isRunning = false;')
expected=dict(RevokeReadiness=511,DoSingleScopedTick=764,HandleRegisterGrant=1407,HandleResetWorker=1447,HandleSealResult=1918,HandleStageSave=2134,HandleLoadSave=1483,HandleCompleteStageValidation=2821,OnDestroy=3447)
for r in d['sites']:
    method=r['method'];match=re.search(r'(?:private\s+(?:void|string)|void)\s+'+re.escape(method)+r'\s*\(',src);start=match.start();startbyte=len(src[:start].encode())+(3 if b.startswith(b'\xef\xbb\xbf') else 0);off=b.index(needles[method].encode(),startbyte);lo=max(0,off-180);hi=min(len(b),off+180)
    ct=dict(line=b[:off].count(b'\n')+1,byte_offset=off,context_start=lo,context_end=hi,context_sha256=hashlib.sha256(b[lo:hi]).hexdigest().upper(),context_utf8=b[lo:hi].decode())
    assert ct['line']==expected[method],(method,ct['line'],expected[method])
    if ct!=r['current_context']:updated.append(dict(method=method,initial_line=r['current_context']['line'],corrected_line=ct['line']))
    r['current_context']=ct
d['metadata_correction']='Initial own metadata searched first invocation rather than declaration; final declaration anchored. Original draft and line annotation failure preserved; candidate/QA calls0.'
p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode())
write(Q/'OWN_METADATA_CORRECTION.json',dict(at=now(),initial_draft_archive=dict(path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size),failure_record=str(Q/'LIFETIME_METADATA_FAILURE.txt'),failed_tool='correct_lifetime_anchors.py',final_tool='complete_lifetime_correction.py',final_lifetime=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size),changed_rows=updated,scope='QA-owned unfrozen draft metadata only',candidate_build_execute=0,qa_runner_execute=0,original_protected_evidence_changed=False))
print(json.dumps(dict(changed_rows=updated,final_sha256=sha(p),calls=0),indent=2))
