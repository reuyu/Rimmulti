"""Genuine local positive controls only; no forged receipts/tasks or bypass attempts."""
from pathlib import Path
import json, socket, subprocess, time, shutil, hashlib, re, traceback
import prepare_recovery as f

Q=f.Q
DATA=Q/"Evidence"
PROFILE="7DDC73B75FA4AA1B00177EA4C73380A7E233A972968D5C0BF91852CD1C2F8D40"
EXPECTED="9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC"
OWNED=[]
RESULT={"attempt_id":f.ATTEMPT,"started_at":f.stamp(),"scope":"genuine fresh native positive controls; authority security not inferred","chain":[],"checks":[],"processes":[]}
ALLOWED={"HELLO","STATUS","SHUTDOWN","GET_PROFILE_FINGERPRINT","GET_ENVIRONMENT_MANIFEST","GET_CENSUS_JSON","GET_SEMANTIC_STATUS","REGISTER_AUTHORITY","REGISTER_GRANT","LOAD_SAVE","VALIDATE_INPUT","STEP_TICKS","SEAL_RESULT","GET_SEALED_RESULT","STAGE_SAVE","GET_ACTIVE_VALIDATOR_TASK","EXECUTE_VALIDATOR_TASK","COMPLETE_STAGE_VALIDATION","GET_STAGE_VALIDATION_RECEIPT","PROMOTE_STAGED","RESET_WORKER"}

def save(): f.write(DATA/"native-positive-results.json",RESULT)

def record_check(name,passed,details):
    RESULT["checks"].append(dict(name=name,passed=passed,details=details))
    save()
    print(name, "PASS" if passed else "FAIL", flush=True)
    if not passed: raise AssertionError(name)

def assert_freeze():
    baseline=json.loads((Q/"bootstrap-freeze-recheck.json").read_text(encoding="utf-8"))
    mf=json.loads((f.PKG/"bootstrap/GATE05_LOCAL_FREEZE_MANIFEST.json").read_text(encoding="utf-8-sig"))
    changed=[p for p,e in mf["files"].items() if not Path(p).is_file() or f.sha(Path(p))!=e["sha256"] or Path(p).stat().st_size!=e["bytes"]]
    if changed:
        RESULT["candidate_drift"]=changed
        save()
        raise RuntimeError("frozen Engine candidate changed; evidence reuse stopped")

def available_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1",0))
        return s.getsockname()[1]

class Bridge:
    def __init__(self,port):
        self.sock=socket.create_connection(("127.0.0.1",port),timeout=3)
        self.sock.settimeout(45)
        self.reader=self.sock.makefile("r",encoding="utf-8",newline="")
    def send(self,command):
        assert command.split(" ",1)[0] in ALLOWED
        self.sock.sendall((command+"\n").encode("utf-8"))
        lines=[]
        while True:
            line=self.reader.readline()
            if not line: raise EOFError("owned native process closed protocol")
            if line.strip("\r\n\ufeff")=="---END---": break
            lines.append(line.lstrip("\ufeff"))
        raw="".join(lines)
        return raw[:-2] if raw.endswith("\r\n") else raw[:-1] if raw.endswith("\n") else raw
    def close(self):
        self.reader.close()
        self.sock.close()

class Host:
    def __init__(self,name):
        assert_freeze()
        self.name="Run02"+name
        self.profile=Q/"Profiles"/self.name
        self.profile.mkdir(parents=True,exist_ok=False)
        (self.profile/"Config").mkdir()
        (self.profile/"Saves").mkdir()
        (self.profile/"Tasks").mkdir()
        shutil.copy2(f.ROOT/"QA-Tactical-Engine/SEMANTIC-AUTHORITY04-20261004/Frozen/Developer-A/Config/ModsConfig.xml",self.profile/"Config/ModsConfig.xml")
        (self.profile/"Config/Prefs.xml").write_text("<PrefsData><volumeGame>0</volumeGame><volumeMusic>0</volumeMusic><devMode>True</devMode><runInBackground>True</runInBackground></PrefsData>",encoding="utf-8")
        self.port=available_port()
        probe_port=available_port()
        self.commands=[]
        args=[str(f.GAME/"RimWorldWin64.exe"),"-batchmode",f"-savedatafolder={self.profile}","-logFile",str(self.profile/"player.log"),f"-bridgeport={self.port}",f"-qaport={probe_port}"]
        si=subprocess.STARTUPINFO()
        si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow=0
        self.p=subprocess.Popen(args,cwd=Q,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
        self.bridge=None
        self.row=dict(name=name,pid=self.p.pid,args=args,started_at=f.stamp(),profile=str(self.profile),exit_code=None)
        RESULT["processes"].append(self.row)
        OWNED.append(self)
        save()
        deadline=time.monotonic()+100
        while time.monotonic()<deadline:
            if self.p.poll() is not None: raise RuntimeError(name+" early native exit "+str(self.p.returncode))
            try:
                self.bridge=Bridge(self.port)
                hello=self.cmd("HELLO")
                if hello.startswith("READY:"): break
            except (OSError,EOFError): time.sleep(.3)
        else: raise TimeoutError(name+" native launch timeout")
        print(name,"native PID",self.p.pid,"connected",flush=True)
        actual=self.cmd("GET_PROFILE_FINGERPRINT").split(":",1)[1].strip()
        self.row["native_content_fingerprint"]=actual
        self.row["environment_manifest"]=self.cmd("GET_ENVIRONMENT_MANIFEST")
        record_check(name+" approved-profile",actual==PROFILE,dict(expected=PROFILE,actual=actual))
    def cmd(self,command):
        answer=self.bridge.send(command)
        # This private QA evidence contains only normally issued, attempt-local tasks/results.
        self.commands.append(dict(at=f.stamp(),command=command,response=answer))
        f.write(DATA/(self.name+"-commands.json"),self.commands)
        return answer
    def admit(self,source,expected,name="Input",mode="SIMULATION",authority=None):
        source=Path(source)
        dest=self.profile/"Saves"/(name+".rws")
        if source.resolve()!=dest.resolve(): shutil.copy2(source,dest)
        generation=int(re.search(r"Gen=(\d+)",self.cmd("HELLO")).group(1))+1
        bundle=authority or dict(authorityId="QA-G05-"+self.name+"-"+str(generation),storeIncarnation="STORE_INCARNATION_POC_01",baseLineage="LINEAGE_CLEAN_CONTEXT_B_REV1",expectedSourceArtifactHash=f.sha(dest),manifestVersion="4.0",expectedManifestHash=expected,contentProfileFingerprint=PROFILE,targetScopeId="SETTLEMENT-B",targetMapId=0,workerGeneration=generation,allowedOperationMode=mode)
        reg=self.cmd("REGISTER_AUTHORITY "+json.dumps(bundle,separators=(",",":")))
        record_check(self.name+" authority",reg.startswith("AUTHORITY_REGISTERED") or reg.startswith("AUTHORITY_ACK"),reg)
        grant=dict(grantId="QA-GRANT-"+self.name+"-"+str(generation),authorityId=bundle["authorityId"],workerGeneration=generation,scopeId=bundle["targetScopeId"],targetMapIndex=bundle["targetMapId"],allowedMode=mode,executionClass="VALIDATOR" if mode=="READ_ONLY" else "TACTICAL_PROBE",tickBudget=0 if mode=="READ_ONLY" else 20)
        response=self.cmd("REGISTER_GRANT "+json.dumps(grant,separators=(",",":")))
        record_check(self.name+" grant",response.startswith("GRANT_REGISTERED") or response.startswith("GRANT_ACK"),response)
        load=self.cmd("LOAD_SAVE "+name+" 0")
        states=[]
        deadline=time.monotonic()+100
        while time.monotonic()<deadline:
            state=self.cmd("STATUS")
            states.append(state)
            if "STATE: READY" in state or "STATE: LOAD_FAILED" in state: break
            time.sleep(.25)
        record_check(self.name+" fresh-native-load","STATE: READY" in state,dict(load=load,final_state=state,input_sha=f.sha(dest)))
        validation=self.cmd("VALIDATE_INPUT")
        record_check(self.name+" input",validation.startswith("INPUT_VALIDATED"),validation)
        raw=self.cmd("GET_CENSUS_JSON 0")
        (DATA/(self.name+"-loaded-census.json")).write_text(raw,encoding="utf-8")
        actual=hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()
        record_check(self.name+" independent-census-SHA",actual==expected,dict(expected=expected,actual=actual,field_comparison="full declared V4 JSON",file=str(DATA/(self.name+"-loaded-census.json"))))
        return bundle,grant,json.loads(raw)
    def seal_stage(self,grant,label):
        seal_response=self.cmd("SEAL_RESULT "+grant["grantId"])
        record_check(self.name+" seal",seal_response.startswith("RESULT_SEALED"),seal_response)
        seal=json.loads(self.cmd("GET_SEALED_RESULT"))
        raw=self.cmd("GET_CENSUS_JSON 0")
        f.write(DATA/(label+"-sealed.json"),seal)
        record_check(label+" own-seal-equality",hashlib.sha256(raw.encode("utf-8")).hexdigest().upper()==seal["sealedManifestHash"] and json.loads(raw)==json.loads(seal["manifestJson"]),dict(sealed_hash=seal["sealedManifestHash"]))
        response=self.cmd("STAGE_SAVE "+label)
        record_check(label+" stage",response.startswith("STAGED_OK"),response)
        task=json.loads(self.cmd("GET_ACTIVE_VALIDATOR_TASK"))
        f.write(DATA/(label+"-simulator-task.json"),task)
        p=Path(task["stagedFilePath"])
        record_check(label+" exact-stage",f.sha(p)==task["stagedSha"] and task["sealedManifestHash"]==seal["sealedManifestHash"],dict(stage=str(p),sha=f.sha(p)))
        return seal,task,p
    def close(self):
        if self.p.poll() is None:
            try:
                if self.bridge:self.cmd("SHUTDOWN")
                self.p.wait(timeout=15)
            except Exception:
                self.row["forced_owned_cleanup"]=True
                self.p.kill()
                self.p.wait(timeout=15)
        if self.bridge:
            try:self.bridge.close()
            except Exception:pass
        self.row.update(exit_code=self.p.returncode,ended_at=f.stamp())
        save()

def fresh_validate(sim,seal,task,stage,label):
    validator=Host("Validator"+label)
    staged_name=stage.stem
    val_authority=dict(authorityId=task["authorityId"],storeIncarnation=task["storeIncarnation"],baseLineage=task["baseLineage"],expectedSourceArtifactHash=task["stagedSha"],manifestVersion=task["manifestVersion"],expectedManifestHash=task["sealedManifestHash"],contentProfileFingerprint=task["contentProfileFingerprint"],targetScopeId=task["scopeId"],targetMapId=task["targetMapIndex"],workerGeneration=1,allowedOperationMode="READ_ONLY")
    _,_,census=validator.admit(stage,task["sealedManifestHash"],name=staged_name,mode="READ_ONLY",authority=val_authority)
    record_check(label+" validator-supported-equality",census==json.loads(seal["manifestJson"]),dict(simulator_pid=sim.p.pid,validator_pid=validator.p.pid,manifest_hash=seal["sealedManifestHash"]))
    copied_task=validator.profile/"Tasks"/(task["validatorTaskId"]+".task.json")
    f.write(copied_task,task)
    response=validator.cmd("EXECUTE_VALIDATOR_TASK "+str(copied_task)+" "+task["capabilityNonce"])
    record_check(label+" genuine-validator-result",response.startswith("VALIDATOR_RESULT:"),dict(response_prefix=response.split("ResultJson=",1)[0],validator_pid=validator.p.pid))
    result=json.loads(response.split("ResultJson=",1)[1])
    record_check(label+" observed-owned-validator",result["validatorProcessId"]==str(validator.p.pid) and validator.p.pid!=sim.p.pid and validator.p.poll() is None,dict(simulator_pid=sim.p.pid,validator_pid=validator.p.pid,claim="QA launch/handle proof, not simulator-enforced authentication"))
    completion=sim.cmd("COMPLETE_STAGE_VALIDATION "+json.dumps(result,separators=(",",":")))
    record_check(label+" valid-completion",completion.startswith("STAGE_VALIDATION_ACCEPTED"),completion)
    receipt=json.loads(sim.cmd("GET_STAGE_VALIDATION_RECEIPT"))
    f.write(DATA/(label+"-native-receipt.json"),receipt)
    record_check(label+" stage-unchanged-after-validation",f.sha(stage)==task["stagedSha"],dict(sha=f.sha(stage)))
    validator.close()
    return receipt

def main():
    DATA.mkdir(parents=True,exist_ok=True)
    assert_freeze()
    source=Q/"Frozen/TargetSettlement_Clean_ContextB.rws"
    expected=EXPECTED
    try:
        for letter in ("A","B","C"):
            sim=Host("Simulator"+letter)
            _,grant,census=sim.admit(source,expected)
            row=dict(stage=letter,pid=sim.p.pid,source=str(source),source_sha=f.sha(source),input_manifest_hash=expected,input_ticks=census["ticksGame"],loaded_profile=sim.row["native_content_fingerprint"])
            if letter=="C":
                row["role"]="fresh downstream consumer; no promotion"
                RESULT["chain"].append(row)
                sim.close()
                break
            step=sim.cmd("STEP_TICKS 5 5")
            deadline=time.monotonic()+35
            while time.monotonic()<deadline:
                status=sim.cmd("STATUS")
                if "RemainingStep=0," in status:break
                time.sleep(.2)
            ticked=json.loads(sim.cmd("GET_CENSUS_JSON 0"))
            record_check(letter+" five-authorized-ticks",ticked["ticksGame"]==census["ticksGame"]+5,dict(before=census["ticksGame"],after=ticked["ticksGame"],response=step))
            seal,task,stage=sim.seal_stage(grant,"Chain"+letter)
            receipt=fresh_validate(sim,seal,task,stage,letter)
            stage_sha=f.sha(stage)
            promotion=sim.cmd("PROMOTE_STAGED "+stage.stem+" Promoted"+letter)
            final=sim.profile/"Saves"/("Promoted"+letter+".rws")
            record_check(letter+" first-final",promotion.startswith("ARTIFACT_APPROVED") and final.exists() and f.sha(final)==stage_sha,dict(response=promotion,stage_sha=stage_sha,final_sha=f.sha(final) if final.exists() else None))
            row.update(sealed_manifest_hash=seal["sealedManifestHash"],sealed_result_id=seal["sealedResultId"],result_epoch=seal["resultEpoch"],stage_sha=stage_sha,validator_pid=receipt["validatorProcessId"],final=str(final),final_sha=f.sha(final),authority_gate_pass=False,reason="genuine functionality chain; issuer boundary and content completeness assessed separately")
            RESULT["chain"].append(row)
            save()
            source=final
            expected=seal["sealedManifestHash"]
            sim.close()
        RESULT["runtime_status"]="POSITIVE_CHAIN_COMPLETED"
    except Exception as exc:
        RESULT["runtime_status"]="INTERRUPTED_OR_FAILED"
        RESULT["harness_error"]=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        print("native positive run stopped:",type(exc).__name__,str(exc),flush=True)
    finally:
        for h in OWNED:
            if h.p.poll() is None:h.close()
        RESULT["finished_at"]=f.stamp()
        save()
        print("runtime status",RESULT["runtime_status"],flush=True)

if __name__=="__main__":main()
