"""QA-owned file lock/normal replacement controls; no tampering or bypass."""
from pathlib import Path
import ctypes, traceback, sys
import native_positive as h

ESCALATED="--qa-unsandboxed" in sys.argv
h.DATA=h.Q/("Evidence/ReplacementUnsandboxed" if ESCALATED else "Evidence/Replacement")
h.DATA.mkdir(parents=True,exist_ok=True)
h.RESULT={"attempt_id":h.f.ATTEMPT,"started_at":h.f.stamp(),"scope":"normal first final, delete-sharing lock failure, clean reset and atomic replacement/backup","execution_context":"approved unsandboxed QA action" if ESCALATED else "sandboxed","chain":[],"checks":[],"processes":[]}

def validate_promote(sim,grant,label,final_name):
    if ESCALATED:label="Escalated"+label
    seal,task,stage=sim.seal_stage(grant,label)
    receipt=h.fresh_validate(sim,seal,task,stage,label)
    return seal,task,stage,receipt

def main():
    sim=None
    try:
        sim=h.Host("EscalatedReplacement" if ESCALATED else "Replacement")
        _,grant,_=sim.admit(h.Q/"Frozen/TargetSettlement_Clean_ContextB.rws",h.EXPECTED)
        seal,task,stage,receipt=validate_promote(sim,grant,"ReplacementFirst","ExistingFinal")
        first_sha=h.f.sha(stage)
        response=sim.cmd("PROMOTE_STAGED "+stage.stem+" ExistingFinal")
        final=sim.profile/"Saves/ExistingFinal.rws"
        h.record_check("replacement first-final",response.startswith("ARTIFACT_APPROVED") and final.exists() and h.f.sha(final)==first_sha,dict(response=response,stage_sha=first_sha,final_sha=h.f.sha(final)))
        old_sha=h.f.sha(final)
        seal,task,stage,receipt=validate_promote(sim,grant,"ReplacementLocked","ExistingFinal")
        before_stage=h.f.sha(stage)
        assert final.resolve().is_relative_to(h.Q.resolve())
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p]
        kernel.CreateFileW.restype=ctypes.c_void_p
        kernel.CloseHandle.argtypes=[ctypes.c_void_p]
        # Permit reads/writes but omit FILE_SHARE_DELETE: backup-copy can proceed;
        # File.Replace must fail rather than substitute an overwrite fallback.
        handle=kernel.CreateFileW(str(final),0x80000000,3,None,3,0x80,None)
        if handle in (None,ctypes.c_void_p(-1).value): raise OSError(ctypes.get_last_error(),"QA final-lock setup failed")
        try:
            response=sim.cmd("PROMOTE_STAGED "+stage.stem+" ExistingFinal")
        finally:
            kernel.CloseHandle(handle)
        h.record_check("locked actual-File.Replace preserves final",response.startswith("PROMOTION_FAILED") and "Atomic File.Replace failed" in response and h.f.sha(final)==old_sha and stage.exists() and h.f.sha(stage)==before_stage,dict(response=response,old_sha=old_sha,after_sha=h.f.sha(final),stage_preserved=stage.exists(),stage_sha=h.f.sha(stage) if stage.exists() else None,lock_scope="QA-owned ExistingFinal only; FILE_SHARE_READ|WRITE, no DELETE"))
        state=sim.cmd("GET_SEMANTIC_STATUS")
        h.record_check("replace-failure revokes readiness","SimulationReady=False" in state and "VALIDATION_FAILED" in state,state)
        reset=sim.cmd("RESET_WORKER")
        _,grant,_=sim.admit(final,seal["sealedManifestHash"],name="ReplacementReinput")
        seal,task,stage,receipt=validate_promote(sim,grant,"ReplacementSuccess","ExistingFinal")
        new_sha=h.f.sha(stage)
        response=sim.cmd("PROMOTE_STAGED "+stage.stem+" ExistingFinal")
        backup=sim.profile/"Saves/ExistingFinal.bak.rws"
        h.record_check("normal replacement exact final and backup",response.startswith("ARTIFACT_APPROVED") and h.f.sha(final)==new_sha and backup.exists() and h.f.sha(backup)==old_sha,dict(response=response,old_sha=old_sha,stage_sha=new_sha,final_sha=h.f.sha(final),backup=str(backup),backup_sha=h.f.sha(backup) if backup.exists() else None,reset=reset))
        h.RESULT["runtime_status"]="REPLACEMENT_CONTROLS_COMPLETED"
    except Exception as exc:
        h.RESULT["runtime_status"]="INTERRUPTED_OR_FAILED"
        h.RESULT["harness_error"]=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        print("replacement control stopped",str(exc),flush=True)
    finally:
        for owned in h.OWNED:
            if owned.p.poll() is None:owned.close()
        h.RESULT["finished_at"]=h.f.stamp()
        h.save()
        print(h.RESULT["runtime_status"],flush=True)

if __name__=="__main__":main()
