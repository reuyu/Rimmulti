"""Independent normal existing-final control; no lock or fault injection."""
import traceback, sys
import native_positive as h

ESCALATED="--qa-unsandboxed" in sys.argv
h.DATA=h.Q/("Evidence/ReplacementWithoutLockUnsandboxed" if ESCALATED else "Evidence/ReplacementWithoutLock")
h.DATA.mkdir(parents=True,exist_ok=True)
h.RESULT={"attempt_id":h.f.ATTEMPT,"started_at":h.f.stamp(),"scope":"fresh profile; existing-final normal replacement with no prior lock","execution_context":"approved unsandboxed QA action" if ESCALATED else "sandboxed","chain":[],"checks":[],"processes":[]}

def main():
    try:
        host=h.Host("EscalatedReplacementNoLock" if ESCALATED else "ReplacementNoLock")
        _,grant,_=host.admit(h.Q/"Frozen/TargetSettlement_Clean_ContextB.rws",h.EXPECTED)
        old_sha=None
        for index in (1,2):
            label=("EscalatedNoLock" if ESCALATED else "NoLock")+str(index)
            seal,task,stage=host.seal_stage(grant,label)
            h.fresh_validate(host,seal,task,stage,label)
            stage_sha=h.f.sha(stage)
            response=host.cmd("PROMOTE_STAGED "+stage.stem+" ExistingFinalNoLock")
            final=host.profile/"Saves/ExistingFinalNoLock.rws"
            backup=host.profile/"Saves/ExistingFinalNoLock.bak.rws"
            details=dict(response=response,stage_sha=stage_sha,final_sha=h.f.sha(final) if final.exists() else None,prior_sha=old_sha,stage_preserved=stage.exists(),backup_sha=h.f.sha(backup) if backup.exists() else None,prior_lock_used=False)
            passed=response.startswith("ARTIFACT_APPROVED") and final.exists() and h.f.sha(final)==stage_sha and (index==1 or backup.exists() and h.f.sha(backup)==old_sha)
            h.record_check("normal no-lock promotion "+str(index),passed,details)
            old_sha=h.f.sha(final)
        h.RESULT["runtime_status"]="NORMAL_REPLACEMENT_COMPLETED"
    except AssertionError as exc:
        h.RESULT["runtime_status"]="CANDIDATE_NORMAL_REPLACEMENT_CHECK_FAILED"
        h.RESULT["candidate_check_failure"]=str(exc)
    except Exception as exc:
        h.RESULT["runtime_status"]="HARNESS_OR_ENVIRONMENT_INTERRUPTION"
        h.RESULT["harness_error"]=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        for host in h.OWNED:
            if host.p.poll() is None:host.close()
        h.RESULT["finished_at"]=h.f.stamp()
        h.save()
        print(h.RESULT["runtime_status"],flush=True)

if __name__=="__main__":main()
