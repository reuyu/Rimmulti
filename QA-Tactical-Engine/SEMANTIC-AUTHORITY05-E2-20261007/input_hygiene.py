"""Bounded parser/read-only smoke controls on own fixtures, not bypass reproduction."""
import json, traceback
import native_positive as h

h.DATA=h.Q/"Evidence/InputHygiene"
h.DATA.mkdir(parents=True,exist_ok=True)
h.RESULT={"attempt_id":h.f.ATTEMPT,"started_at":h.f.stamp(),"scope":"small malformed XML, normal READ_ONLY enforcement, malformed grant revocation","chain":[],"checks":[],"processes":[]}

def main():
    try:
        host=h.Host("InputHygiene")
        fixtures={
            "EOF":"<savegame><meta><gameVersion>1.6.4871 rev591</gameVersion>",
            "SecondRoot":"<savegame><meta><gameVersion>1.6.4871 rev591</gameVersion></meta></savegame><extra/>",
            "DTD":"<!DOCTYPE savegame []><savegame><meta><gameVersion>1.6.4871 rev591</gameVersion></meta></savegame>",
        }
        for label,text in fixtures.items():
            host.cmd("RESET_WORKER")
            path=host.profile/"Saves"/(label+".rws")
            path.write_text(text,encoding="utf-8")
            generation=int(h.re.search(r"Gen=(\d+)",host.cmd("HELLO")).group(1))+1
            bundle=dict(authorityId="QA-HYGIENE-"+label,storeIncarnation="STORE_INCARNATION_POC_01",baseLineage="LINEAGE_CLEAN_CONTEXT_B_REV1",expectedSourceArtifactHash=h.f.sha(path),manifestVersion="4.0",expectedManifestHash=h.EXPECTED,contentProfileFingerprint=h.PROFILE,targetScopeId="SETTLEMENT-B",targetMapId=0,workerGeneration=generation,allowedOperationMode="READ_ONLY")
            registered=host.cmd("REGISTER_AUTHORITY "+json.dumps(bundle,separators=(",",":")))
            h.record_check(label+" parser-control authority",registered.startswith("AUTHORITY_REGISTERED"),registered)
            response=host.cmd("LOAD_SAVE "+label+" 0")
            status=host.cmd("STATUS")
            h.record_check(label+" bounded malformed input rejected",response.startswith("LOAD_REJECTED") and "SimulationReady=False" in status,dict(response=response,status=status,fixture=str(path),sha256=h.f.sha(path),scope="input preflight rejection; not fresh staged-byte semantic rejection"))
        host.cmd("RESET_WORKER")
        _,grant,census=host.admit(h.Q/"Frozen/TargetSettlement_Clean_ContextB.rws",h.EXPECTED,name="ValidReadOnly",mode="READ_ONLY")
        step=host.cmd("STEP_TICKS 1 1")
        seal=host.cmd("SEAL_RESULT "+grant["grantId"])
        after=json.loads(host.cmd("GET_CENSUS_JSON 0"))
        h.record_check("READ_ONLY no ticks or seal", "READ_ONLY" in step and "READ_ONLY" in seal and after==census,dict(step=step,seal=seal,before_ticks=census["ticksGame"],after_ticks=after["ticksGame"],full_declared_census_equal=after==census))
        malformed=host.cmd("REGISTER_GRANT {")
        status=host.cmd("GET_SEMANTIC_STATUS")
        blocked={command:host.cmd(command) for command in ("STEP_TICKS 1 1","SEAL_RESULT "+grant["grantId"],"STAGE_SAVE RejectedMalformedGrant","PROMOTE_STAGED MissingStage MissingFinal")}
        h.record_check("malformed grant revokes input readiness", "SimulationReady=False" in status and "VALIDATION_FAILED" in status and all("ERROR" in r or "BLOCKED" in r for r in blocked.values()) and not (host.profile/"Saves/MissingFinal.rws").exists(),dict(response=malformed,status=status,commands=blocked,scope="from valid input READ_ONLY state; outstanding sealed-stage/receipt revocation not exercised"))
        h.RESULT["runtime_status"]="INPUT_HYGIENE_CONTROLS_COMPLETED"
    except Exception as exc:
        h.RESULT["runtime_status"]="INTERRUPTED_OR_FAILED"
        h.RESULT["harness_error"]=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        print("input hygiene stopped",str(exc),flush=True)
    finally:
        for host in h.OWNED:
            if host.p.poll() is None:host.close()
        h.RESULT["finished_at"]=h.f.stamp()
        h.save()
        print(h.RESULT["runtime_status"],flush=True)

if __name__=="__main__":main()
