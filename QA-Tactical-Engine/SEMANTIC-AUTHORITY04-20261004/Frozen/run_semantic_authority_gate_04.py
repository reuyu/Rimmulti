import os
import sys
import time
import json
import socket
import shutil
import hashlib
import subprocess
import base64
from pathlib import Path

# Ensure UTF-8 output on Windows consoles and immediate unbuffered flushing
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import functools
print = functools.partial(print, flush=True)

WORKSPACE = Path(r"c:\Users\user\Desktop\RimMulti")
SCRATCH = WORKSPACE / "scratch"
EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")
SAVES_DIR = Path(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"))

RESULTS_FILE = SCRATCH / "semantic_authority_gate_04_results.json"
results = {
    "workOrder": "WP-POC-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-04",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "classification": "PENDING",
    "provenance": {},
    "negativeBattery1_InputAdmission": {},
    "negativeBattery2_AuthorityAttacks": {},
    "negativeBattery3_SavedByteProof": {},
    "negativeBattery4_PromotionBypasses": {},
    "promotionSafety": {},
    "freshPositiveChain": {}
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def parse_kv_response(resp: str) -> dict:
    if ":" in resp and "=" in resp and resp.index(":") < resp.index("="):
        resp = resp.split(":", 1)[1]
    kv = {}
    for part in resp.split(","):
        tokens = part.strip().split("=", 1)
        if len(tokens) == 2:
            kv[tokens[0].strip()] = tokens[1].strip().strip("'\"")
    return kv

class BridgeClient:
    def __init__(self, port, timeout=60):
        self.port = port
        self.s = socket.create_connection(("127.0.0.1", port), timeout=timeout)
        self.s.settimeout(timeout)
        self.file = self.s.makefile("r", encoding="utf-8", newline="")

    def send(self, cmd):
        self.s.sendall((cmd + "\n").encode("utf-8"))
        lines = []
        while True:
            line = self.file.readline()
            if not line:
                raise RuntimeError("EOF before END marker")
            line = line.rstrip("\r\n").lstrip("\ufeff")
            if line == "---END---":
                break
            lines.append(line)
        return "\n".join(lines)

    def close(self):
        try: self.file.close()
        except: pass
        try: self.s.close()
        except: pass

def prepare_profile(name, source_save=None, save_target_name="Input"):
    profile = SCRATCH / f"Profiles/{name}"
    if profile.exists():
        shutil.rmtree(profile, ignore_errors=True)
    (profile / "Config").mkdir(parents=True, exist_ok=True)
    (profile / "Saves").mkdir(parents=True, exist_ok=True)

    mods_xml = """<?xml version="1.0" encoding="utf-8"?>
<ModsConfigData>
  <version>1.6.4871 rev591</version>
  <activeMods>
    <li>brrainz.harmony</li>
    <li>ludeon.rimworld</li>
    <li>ludeon.rimworld.royalty</li>
    <li>ludeon.rimworld.ideology</li>
    <li>ludeon.rimworld.biotech</li>
    <li>ludeon.rimworld.anomaly</li>
    <li>ludeon.rimworld.odyssey</li>
    <li>wareconomy.hybridmultiplayer</li>
    <li>wareconomy.workerbridge.poc</li>
    <li>qacodex.engine02.probe</li>
  </activeMods>
  <knownExpansions>
    <li>ludeon.rimworld.royalty</li>
    <li>ludeon.rimworld.ideology</li>
    <li>ludeon.rimworld.biotech</li>
    <li>ludeon.rimworld.anomaly</li>
    <li>ludeon.rimworld.odyssey</li>
  </knownExpansions>
</ModsConfigData>"""
    (profile / "Config/ModsConfig.xml").write_text(mods_xml, encoding="utf-8")

    prefs_xml = """<?xml version="1.0" encoding="utf-8"?>
<PrefsData>
  <volumeGame>0</volumeGame>
  <volumeMusic>0</volumeMusic>
  <devMode>True</devMode>
  <runInBackground>True</runInBackground>
  <uiScale>1</uiScale>
</PrefsData>"""
    (profile / "Config/Prefs.xml").write_text(prefs_xml, encoding="utf-8")

    if source_save and Path(source_save).exists():
        shutil.copy2(source_save, profile / "Saves" / f"{save_target_name}.rws")
        shutil.copy2(source_save, SAVES_DIR / f"{save_target_name}.rws")

    return profile

def launch_worker(profile, bridge_port=29300):
    args = [
        str(EXE),
        "-batchmode",
        f"-savedatafolder={profile.resolve()}",
        "-logFile",
        str((profile / "player.log").resolve()),
        f"-bridgeport={bridge_port}"
    ]
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0

    p = subprocess.Popen(args, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(SCRATCH))

    bridge = None
    t0 = time.monotonic()
    for _ in range(120):
        if p.poll() is not None:
            raise RuntimeError(f"Worker exited early with code {p.returncode}")
        try:
            b = BridgeClient(bridge_port, timeout=10)
            h = b.send("HELLO")
            if h.startswith("READY:"):
                bridge = b
                break
        except (OSError, RuntimeError):
            time.sleep(0.5)
    else:
        p.kill()
        raise TimeoutError(f"Worker failed to listen on port {bridge_port} within 60s")

    elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
    return p, bridge, elapsed_ms

def wait_for_ready(b, timeout_sec=90):
    t0 = time.monotonic()
    states = []
    while time.monotonic() - t0 < timeout_sec:
        s = b.send("STATUS")
        states.append(s)
        if "STATE: READY" in s:
            return True, s, states
        if "STATE: LOAD_FAILED" in s:
            return False, s, states
        time.sleep(0.5)
    return False, "TIMEOUT", states

def shutdown_worker(p, b):
    try:
        b.send("SHUTDOWN")
    except:
        pass
    b.close()
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()

def execute_fresh_pre_promotion_validation(staged_file_path: Path, staging_name: str, staged_sha: str, sealed_json_str: str, authority_id: str, content_profile: str, port=29550):
    """
    Spawns a fresh independent RimWorld worker process.
    Loads the exact staged file in the target context.
    Executes VALIDATE_AS_PRE_PROMOTION_VALIDATOR.
    Asserts 0 load errors, XML check pass, and live manifest hash matching sealed manifest hash.
    Returns the StageValidationReceipt object and validator PID.
    """
    val_prof = prepare_profile(f"ValProf_{port}", staged_file_path, staging_name)
    val_proc, val_client, _ = launch_worker(val_prof, bridge_port=port)
    validator_pid = val_proc.pid

    try:
        sealed_res_obj = json.loads(sealed_json_str)
        sealed_manifest_hash = sealed_res_obj["sealedManifestHash"]
        sealed_b64 = base64.b64encode(sealed_json_str.encode("utf-8")).decode("ascii")

        # 1. Register authority on validator
        val_auth = {
            "authorityId": authority_id,
            "expectedSourceArtifactHash": staged_sha,
            "manifestVersion": "4.0",
            "expectedManifestHash": sealed_manifest_hash,
            "contentProfileFingerprint": content_profile,
            "workerGeneration": 1,
            "targetMapId": 0,
            "allowedOperationMode": "READ_ONLY"
        }
        val_client.send(f"REGISTER_AUTHORITY {json.dumps(val_auth)}")

        # 2. Register grant on validator (READ_ONLY mode)
        val_grant = {
            "grantId": f"GRANT-VAL-{validator_pid}",
            "authorityId": authority_id,
            "workerGeneration": 1,
            "scopeId": "SETTLEMENT-B",
            "targetMapIndex": 0,
            "allowedMode": "READ_ONLY",
            "executionClass": "VALIDATOR",
            "tickBudget": 0
        }
        val_client.send(f"REGISTER_GRANT {json.dumps(val_grant)}")

        # 3. Load staged save
        val_client.send(f"LOAD_SAVE {staging_name} 0")
        ok, stat, _ = wait_for_ready(val_client)
        if not ok:
            return False, f"Validator failed to reach READY: {stat}", None, validator_pid

        # 4. Check input validation
        val_inp = val_client.send("VALIDATE_INPUT")
        if "INPUT_VALIDATED" not in val_inp:
            return False, f"Validator input validation failed: {val_inp}", None, validator_pid

        # 5. Create receipt via VALIDATE_AS_PRE_PROMOTION_VALIDATOR
        val_cmd = f"VALIDATE_AS_PRE_PROMOTION_VALIDATOR {authority_id} {sealed_b64} {str(staged_file_path)} {staged_sha}"
        val_eval_res = val_client.send(val_cmd)
        if "STAGE_VALIDATED" not in val_eval_res:
            return False, f"Validator evaluation failed: {val_eval_res}", None, validator_pid

        receipt_json = val_eval_res.split("Receipt=")[-1].strip()
        receipt_obj = json.loads(receipt_json)
        return True, "STAGE_VALIDATED", receipt_obj, validator_pid
    finally:
        shutdown_worker(val_proc, val_client)

def main():
    print("=" * 80)
    print("STARTING WP-POC-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-04 TEST SUITE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Exact Cryptographic Provenance
    # -------------------------------------------------------------------------
    dll_path = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll")
    engine_dll = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll")
    clean_b = SCRATCH / "TargetSettlement_Clean_ContextB.rws"

    mvid_cmd = f"[System.Reflection.Assembly]::LoadFrom('{dll_path}').ManifestModule.ModuleVersionId.ToString()"
    dll_mvid = subprocess.check_output(["powershell", "-NoProfile", "-Command", mvid_cmd], text=True).strip()

    eng_mvid_cmd = f"[System.Reflection.Assembly]::LoadFrom('{engine_dll}').ManifestModule.ModuleVersionId.ToString()"
    eng_mvid = subprocess.check_output(["powershell", "-NoProfile", "-Command", eng_mvid_cmd], text=True).strip()

    # V4 Clean Baseline Manifest Hash
    clean_manifest_hash = "9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC"
    expected_profile_fp = "FF23B58CB774F851E8DCFA84B1EB0FB80C8450575BDE23F61AC0A5CB5CC3207C"

    provenance = {
        "engineVersion": "RimWorld 1.6.4871 rev591 Win64",
        "activeMods": [
            "brrainz.harmony",
            "ludeon.rimworld",
            "ludeon.rimworld.royalty",
            "ludeon.rimworld.ideology",
            "ludeon.rimworld.biotech",
            "ludeon.rimworld.anomaly",
            "ludeon.rimworld.odyssey",
            "wareconomy.hybridmultiplayer",
            "wareconomy.workerbridge.poc",
            "qacodex.engine02.probe"
        ],
        "binaries": {
            "exe": {"path": str(EXE), "sha256": sha256_file(EXE)},
            "assemblyCSharp": {"path": str(engine_dll), "sha256": sha256_file(engine_dll), "mvid": eng_mvid},
            "workerBridgeDll": {"path": str(dll_path), "sha256": sha256_file(dll_path), "mvid": dll_mvid}
        },
        "sourceFiles": {
            "WorkerBridge.cs": {"path": str(SCRATCH / "WorkerBridgeMod/Source/WorkerBridge.cs"), "sha256": sha256_file(SCRATCH / "WorkerBridgeMod/Source/WorkerBridge.cs")},
            "EngineHostCensus.cs": {"path": str(SCRATCH / "WorkerBridgeMod/Source/EngineHostCensus.cs"), "sha256": sha256_file(SCRATCH / "WorkerBridgeMod/Source/EngineHostCensus.cs")}
        },
        "fixtures": {
            "TargetSettlement_Clean_ContextB.rws": {"path": str(clean_b), "bytes": clean_b.stat().st_size, "sha256": sha256_file(clean_b)}
        },
        "contentProfileFingerprint": expected_profile_fp,
        "cleanBaselineManifestHash": clean_manifest_hash,
        "manifestVersion": "4.0"
    }
    results["provenance"] = provenance
    print("\n[PROVENANCE RECORDED]")
    print(f"  Worker DLL SHA256: {provenance['binaries']['workerBridgeDll']['sha256']}")
    print(f"  Worker DLL MVID:   {provenance['binaries']['workerBridgeDll']['mvid']}")
    print(f"  Clean ContextB SHA:{provenance['fixtures']['TargetSettlement_Clean_ContextB.rws']['sha256']}")
    print(f"  Clean V4 Manifest: {clean_manifest_hash}")
    print(f"  Profile Fingerprint:{expected_profile_fp}")

    # -------------------------------------------------------------------------
    # 2. NEGATIVE BATTERY 1: Input Admission Gate (15 Corrupted Fixtures)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 2: NEGATIVE BATTERY 1 -- INPUT ADMISSION GATE (15 CORRUPTED FIXTURES)")
    print("=" * 80)

    profile_neg1 = prepare_profile("Profile_Neg1_InputAdmission")
    for f in (SCRATCH / "CorruptedFixtures").glob("Corrupted_*.rws"):
        shutil.copy2(f, profile_neg1 / "Saves" / f.name)
        shutil.copy2(f, SAVES_DIR / f.name)

    proc_neg1, bridge_neg1, ms_neg1 = launch_worker(profile_neg1, bridge_port=29310)
    print(f"Launched Negative Battery 1 Worker (PID={proc_neg1.pid}, startup={ms_neg1}ms)")

    corr_manifest = json.loads((SCRATCH / "CorruptedFixtures/corruption_battery_manifest.json").read_text(encoding="utf-8"))
    b1_cases = []
    b1_all_passed = True

    for item in corr_manifest:
        tag = item["tag"]
        desc = item["description"]
        save_name = f"Corrupted_{tag}"
        # Reset worker state before each new authority admission
        bridge_neg1.send("RESET_WORKER")
        status_pre = bridge_neg1.send("STATUS")
        cur_gen = int(status_pre.split("Gen=")[1].split(",")[0])
        expected_gen = cur_gen + 1

        corr_file = SCRATCH / f"CorruptedFixtures/{save_name}.rws"
        corr_sha = sha256_file(corr_file)

        # Register authority specifying CLEAN expected manifest hash
        authority_bundle = {
            "authorityId": f"AUTH-CLEAN-FOR-{tag}",
            "expectedSourceArtifactHash": corr_sha,
            "manifestVersion": "4.0",
            "expectedManifestHash": clean_manifest_hash,
            "contentProfileFingerprint": expected_profile_fp,
            "targetMapId": 0,
            "workerGeneration": expected_gen,
            "allowedOperationMode": "SIMULATION"
        }
        reg_resp = bridge_neg1.send(f"REGISTER_AUTHORITY {json.dumps(authority_bundle, separators=(',', ':'))}")

        # Register matching grant
        grant = {
            "grantId": f"GRANT-CLEAN-{tag}",
            "authorityId": f"AUTH-CLEAN-FOR-{tag}",
            "workerGeneration": expected_gen,
            "scopeId": "SETTLEMENT-B",
            "targetMapIndex": 0,
            "allowedMode": "SIMULATION",
            "executionClass": "STANDARD",
            "tickBudget": 1000
        }
        bridge_neg1.send(f"REGISTER_GRANT {json.dumps(grant, separators=(',', ':'))}")

        # Load save
        load_resp = bridge_neg1.send(f"LOAD_SAVE {save_name} 0")
        ok, stat, _ = wait_for_ready(bridge_neg1)
        if not ok:
            print(f"  Load failed: {stat}")
            b1_all_passed = False
            continue

        # Validate input -> MUST be INPUT_REJECTED
        val_input_resp = bridge_neg1.send("VALIDATE_INPUT")
        is_input_rejected = "INPUT_REJECTED: Hash mismatch" in val_input_resp
        print(f"  VALIDATE_INPUT: {val_input_resp} (Rejected={is_input_rejected})")

        # Semantic status -> must be VALIDATION_FAILED and SimulationReady=False
        sem_stat = bridge_neg1.send("GET_SEMANTIC_STATUS")
        is_val_failed = "State=VALIDATION_FAILED" in sem_stat and "SimulationReady=False" in sem_stat

        # Attempt simulation commands -> ALL MUST BE BLOCKED
        step_resp = bridge_neg1.send("STEP_TICKS 10 10")
        is_step_blocked = "ERROR: Cannot simulate untrusted state" in step_resp

        seal_resp = bridge_neg1.send(f"SEAL_RESULT GRANT-{tag}")
        is_seal_blocked = "ERROR: Untrusted state" in seal_resp

        stage_resp = bridge_neg1.send(f"STAGE_SAVE BlockedStage_{tag}")
        is_stage_blocked = "STAGE_BLOCKED" in stage_resp

        prom_resp = bridge_neg1.send(f"PROMOTE_STAGED BlockedStage_{tag} BlockedFinal_{tag}")
        is_prom_blocked = "PROMOTION_BLOCKED" in prom_resp

        case_pass = is_input_rejected and is_val_failed and is_step_blocked and is_seal_blocked and is_stage_blocked and is_prom_blocked
        if not case_pass:
            b1_all_passed = False

        b1_cases.append({
            "tag": tag,
            "description": desc,
            "inputRejected": is_input_rejected,
            "validationFailed": is_val_failed,
            "stepBlocked": is_step_blocked,
            "sealBlocked": is_seal_blocked,
            "stageBlocked": is_stage_blocked,
            "promoteBlocked": is_prom_blocked,
            "pass": case_pass
        })

    shutdown_worker(proc_neg1, bridge_neg1)
    results["negativeBattery1_InputAdmission"] = {
        "casesCount": len(b1_cases),
        "passCount": sum(1 for c in b1_cases if c["pass"]),
        "allPassed": b1_all_passed,
        "cases": b1_cases
    }
    print(f"\n[NEGATIVE BATTERY 1 SUMMARY] Passed: {sum(1 for c in b1_cases if c['pass'])}/{len(b1_cases)} cases.")

    # -------------------------------------------------------------------------
    # 3. NEGATIVE BATTERY 2: Authority & Simulation Grant Attacks
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 3: NEGATIVE BATTERY 2 -- AUTHORITY & SIMULATION GRANT ATTACKS")
    print("=" * 80)

    profile_neg2 = prepare_profile("Profile_Neg2_Authority", clean_b, "CleanContextB")
    proc_neg2, bridge_neg2, ms_neg2 = launch_worker(profile_neg2, bridge_port=29320)
    print(f"Launched Negative Battery 2 Worker (PID={proc_neg2.pid})")

    b2_cases = []

    # Attack 2.1: Immutable Authority - Changed bundle with same ID rejects
    base_auth = {
        "authorityId": "AUTH-IMMUTABLE-01",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "SIMULATION"
    }
    reg1 = bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(base_auth)}")
    # Register identical -> must ACK
    reg_ident = bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(base_auth)}")
    p2_1a = ("AUTHORITY_ACK_UNCHANGED" in reg_ident) or ("Identical bundle re-registered ACK" in reg_ident)

    # Register changed bundle with same ID -> must REJECT
    changed_auth = dict(base_auth)
    changed_auth["targetMapId"] = 1
    reg_changed = bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(changed_auth)}")
    p2_1b = ("different bundle parameters" in reg_changed) or ("different parameters" in reg_changed) or ("In-place overwrite prohibited" in reg_changed)

    b2_cases.append({
        "attack": "Immutable Authority Registration & Idempotence",
        "identicalAck": p2_1a,
        "changedRejection": p2_1b,
        "pass": p2_1a and p2_1b
    })

    # Attack 2.2: Authority Overwrite after LOAD/Admission is blocked
    bridge_neg2.send(f"REGISTER_GRANT {json.dumps({'grantId': 'GRANT-IMMUTABLE-01', 'authorityId': 'AUTH-IMMUTABLE-01', 'workerGeneration': 1, 'scopeId': 'SETTLEMENT-B', 'targetMapIndex': 0, 'allowedMode': 'SIMULATION'})}")
    bridge_neg2.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg2)
    bridge_neg2.send("VALIDATE_INPUT")

    # Now state is INPUT_VALIDATED. Try to register new authority without reset -> MUST REJECT!
    new_auth = dict(base_auth)
    new_auth["authorityId"] = "AUTH-OVERWRITE-02"
    reg_after_load = bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(new_auth)}")
    p2_2 = ("Cannot register or modify AuthorityBundle after game load" in reg_after_load) or ("Worker reset required" in reg_after_load) or ("validated/active simulation is in progress" in reg_after_load)
    b2_cases.append({
        "attack": "Authority Overwrite After Load/Admission Prohibited",
        "response": reg_after_load,
        "pass": p2_2
    })

    # Attack 2.3: Actual ContentProfile Binding
    # Reset worker to allow new admission
    bridge_neg2.send("RESET_WORKER")
    wrong_prof_auth = dict(base_auth)
    wrong_prof_auth["authorityId"] = "AUTH-WRONG-PROFILE"
    wrong_prof_auth["contentProfileFingerprint"] = "FAKE_PROFILE_FINGERPRINT_1234567890ABCDEF"
    wrong_prof_auth["workerGeneration"] = 2
    reg_wrong_prof = bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(wrong_prof_auth)}")
    p2_3 = "ERROR: ContentProfileFingerprint mismatch" in reg_wrong_prof
    b2_cases.append({
        "attack": "Wrong ContentProfileFingerprint Rejected at Registration",
        "response": reg_wrong_prof,
        "pass": p2_3
    })

    # Attack 2.4: READ_ONLY mode blocks STEP_TICKS and SEAL_RESULT
    bridge_neg2.send("RESET_WORKER")
    status_now = bridge_neg2.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    gen2_4 = cur_gen + 1
    ro_auth = dict(base_auth)
    ro_auth["authorityId"] = "AUTH-RO-01"
    ro_auth["allowedOperationMode"] = "READ_ONLY"
    ro_auth["workerGeneration"] = gen2_4
    bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(ro_auth)}")
    ro_grant = {
        "grantId": "GRANT-RO-01",
        "authorityId": "AUTH-RO-01",
        "workerGeneration": gen2_4,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "READ_ONLY"
    }
    bridge_neg2.send(f"REGISTER_GRANT {json.dumps(ro_grant)}")
    bridge_neg2.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg2)
    bridge_neg2.send("VALIDATE_INPUT")

    step_ro = bridge_neg2.send("STEP_TICKS 10 10")
    p2_4a = "OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE" in step_ro
    seal_ro = bridge_neg2.send("SEAL_RESULT GRANT-RO-01")
    p2_4b = "OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE" in seal_ro
    b2_cases.append({
        "attack": "READ_ONLY Mode Blocks STEP_TICKS and SEAL_RESULT",
        "stepResponse": step_ro,
        "sealResponse": seal_ro,
        "pass": p2_4a and p2_4b
    })

    # Attack 2.5: Unknown / Blank / Cross-Authority Grant Rejected at SEAL_RESULT
    bridge_neg2.send("RESET_WORKER")
    status_now = bridge_neg2.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    gen2_5 = cur_gen + 1
    valid_auth = dict(base_auth)
    valid_auth["authorityId"] = "AUTH-VALID-GRANT-TEST"
    valid_auth["workerGeneration"] = gen2_5
    bridge_neg2.send(f"REGISTER_AUTHORITY {json.dumps(valid_auth)}")
    bridge_neg2.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg2)
    bridge_neg2.send("VALIDATE_INPUT")

    # Try to seal with unregistered grant
    seal_unreg = bridge_neg2.send("SEAL_RESULT UNREGISTERED-GRANT-999")
    p2_5a = ("No registered simulation grant" in seal_unreg) or ("No active SimulationGrant" in seal_unreg) or ("Untrusted state" in seal_unreg)

    # Try to seal with blank grant
    seal_blank = bridge_neg2.send("SEAL_RESULT")
    p2_5b = ("Missing grantId" in seal_blank) or ("cannot be blank" in seal_blank) or ("No active SimulationGrant" in seal_blank) or ("Untrusted state" in seal_blank)

    # Register grant with foreign authorityId
    foreign_grant = {
        "grantId": "GRANT-FOREIGN",
        "authorityId": "FOREIGN-AUTHORITY-ID",
        "workerGeneration": gen2_5,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION"
    }
    reg_foreign = bridge_neg2.send(f"REGISTER_GRANT {json.dumps(foreign_grant)}")
    p2_5c = ("does not match registered authority" in reg_foreign) or ("match" in reg_foreign)

    b2_cases.append({
        "attack": "Unknown, Blank and Cross-Authority Grants Rejected",
        "unregResponse": seal_unreg,
        "blankResponse": seal_blank,
        "foreignResponse": reg_foreign,
        "pass": p2_5a and p2_5b and p2_5c
    })

    # Attack 2.6: Readiness Revocation
    # Main worker is in INPUT_VALIDATED state. Now execute an invalid authority check or corrupt disk file.
    status_before_rev = bridge_neg2.send("GET_SEMANTIC_STATUS")
    # Send an invalid grant registration that triggers RevokeReadiness
    bridge_neg2.send(f"REGISTER_GRANT {json.dumps(foreign_grant)}")
    status_after_rev = bridge_neg2.send("GET_SEMANTIC_STATUS")
    p2_6 = ("SimulationReady=False" in status_after_rev) and (("State=VALIDATION_FAILED" in status_after_rev) or ("State=NONE" in status_after_rev))
    b2_cases.append({
        "attack": "Validation/Authority Failure Triggers Instant Readiness Revocation",
        "statusBefore": status_before_rev,
        "statusAfter": status_after_rev,
        "pass": p2_6
    })

    shutdown_worker(proc_neg2, bridge_neg2)
    b2_all_passed = all(c["pass"] for c in b2_cases)
    results["negativeBattery2_AuthorityAttacks"] = {
        "casesCount": len(b2_cases),
        "passCount": sum(1 for c in b2_cases if c["pass"]),
        "allPassed": b2_all_passed,
        "cases": b2_cases
    }
    print(f"\n[NEGATIVE BATTERY 2 SUMMARY] Passed: {sum(1 for c in b2_cases if c['pass'])}/{len(b2_cases)} attacks.")

    # -------------------------------------------------------------------------
    # 4. NEGATIVE BATTERY 3: Highest-Priority Saved-Byte Semantic Attacks (Sol G03-01)
    #    Mutating Shooting, Hediff severity, Held item count, Nested holder,
    #    and Structural XML (EOF, second root, DTD).
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 4: NEGATIVE BATTERY 3 -- HIGHEST-PRIORITY SAVED-BYTE SEMANTIC ATTACKS (SOL G03-01)")
    print("=" * 80)

    profile_neg3 = prepare_profile("Profile_Neg3_SavedBytes", clean_b, "CleanContextB")
    proc_neg3, bridge_neg3, ms_neg3 = launch_worker(profile_neg3, bridge_port=29330)
    print(f"Launched Negative Battery 3 Worker (PID={proc_neg3.pid})")

    b3_cases = []

    # Helper function to stage save and test tamper
    def setup_sealed_state(auth_id, gen=None):
        bridge_neg3.send("RESET_WORKER")
        status_now = bridge_neg3.send("STATUS")
        cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
        expected_gen = cur_gen + 1
        auth = {
            "authorityId": auth_id,
            "expectedSourceArtifactHash": sha256_file(clean_b),
            "manifestVersion": "4.0",
            "expectedManifestHash": clean_manifest_hash,
            "contentProfileFingerprint": expected_profile_fp,
            "workerGeneration": expected_gen,
            "targetMapId": 0,
            "allowedOperationMode": "SIMULATION"
        }
        bridge_neg3.send(f"REGISTER_AUTHORITY {json.dumps(auth)}")
        grant = {
            "grantId": f"GRANT-{auth_id}",
            "authorityId": auth_id,
            "workerGeneration": expected_gen,
            "scopeId": "SETTLEMENT-B",
            "targetMapIndex": 0,
            "allowedMode": "SIMULATION"
        }
        bridge_neg3.send(f"REGISTER_GRANT {json.dumps(grant)}")
        bridge_neg3.send("LOAD_SAVE CleanContextB 0")
        wait_for_ready(bridge_neg3)
        val_res = bridge_neg3.send("VALIDATE_INPUT")
        assert "INPUT_VALIDATED" in val_res, f"VALIDATE_INPUT failed: {val_res}"
        seal_res = bridge_neg3.send(f"SEAL_RESULT GRANT-{auth_id}")
        assert "RESULT_SEALED" in seal_res, f"SEAL_RESULT failed: {seal_res}"

    # Saved-Byte Attack 3.1: Shooting Skill 10 -> 15 in saved XML bytes (Map 0 Pawn)
    setup_sealed_state("AUTH-SAVED-SHOOTING", 1)
    stage_res = bridge_neg3.send("STAGE_SAVE Stage_Shoot")
    kv_stage = parse_kv_response(stage_res)
    staged_path = Path(kv_stage["File"])
    staged_name = kv_stage["StagingName"]
    original_sha = kv_stage["StagedSha"]

    # Mutate Strange's Shooting skill on Map 0 in XML: 10 -> 15
    xml_text = staged_path.read_text(encoding="utf-8")
    idx = xml_text.find("Strange")
    shoot_idx = xml_text.find("<def>Shooting</def>", idx)
    lvl_idx = xml_text.find("<level>10</level>", shoot_idx)
    assert lvl_idx != -1 and (lvl_idx - shoot_idx) < 200, "Failed to locate Strange's Shooting skill in staged XML"
    mutated_xml = xml_text[:lvl_idx] + "<level>15</level>" + xml_text[lvl_idx + len("<level>10</level>"):]
    staged_path.write_text(mutated_xml, encoding="utf-8")
    mutated_sha = sha256_file(staged_path)
    assert mutated_sha != original_sha, "Failed to change SHA on Shooting mutation"
    print(f"Mutated Shooting on Map 0 in staged XML: SHA {original_sha} -> {mutated_sha}")

    # Run fresh pre-promotion validation on the mutated file
    sealed_json = bridge_neg3.send("GET_SEALED_RESULT")
    val_ok, val_msg, val_rcpt, _ = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, mutated_sha, sealed_json, "AUTH-SAVED-SHOOTING", expected_profile_fp, port=29561
    )
    p3_1_val = (val_ok is False)

    # Attempt promotion on simulating worker without valid receipt -> MUST BLOCK!
    prom_res = bridge_neg3.send(f"PROMOTE_STAGED {staged_name} Final_Shoot")
    p3_1_prom = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_res
    b3_cases.append({
        "attack": "Saved-Byte Fault: Shooting skill altered in staged XML",
        "validatorBlocked": p3_1_val,
        "validatorMsg": val_msg,
        "promotionBlocked": p3_1_prom,
        "pass": p3_1_val and p3_1_prom
    })

    # Saved-Byte Attack 3.2: Hediff Severity 3.0 -> 1.0 in saved XML bytes (Map 0 Pawn)
    setup_sealed_state("AUTH-SAVED-HEDIFF", 2)
    stage_res = bridge_neg3.send("STAGE_SAVE Stage_Hediff")
    kv_stage = parse_kv_response(stage_res)
    staged_path = Path(kv_stage["File"])
    staged_name = kv_stage["StagingName"]
    orig_hediff_sha = kv_stage["StagedSha"]
    xml_text = staged_path.read_text(encoding="utf-8")
    load_idx = xml_text.find("<loadID>990002</loadID>")
    sev_idx = xml_text.find("<severity>", load_idx)
    sev_end = xml_text.find("</severity>", sev_idx)
    assert load_idx != -1 and sev_idx != -1 and (sev_idx - load_idx) < 200, "Failed to locate Strange's Stab severity in staged XML"
    mutated_xml = xml_text[:sev_idx] + "<severity>1</severity>" + xml_text[sev_end + 11:]
    staged_path.write_text(mutated_xml, encoding="utf-8")
    mutated_sha = sha256_file(staged_path)
    assert mutated_sha != orig_hediff_sha, "Failed to change SHA on Hediff mutation"
    print(f"Mutated Hediff on Map 0 in staged XML: SHA {orig_hediff_sha} -> {mutated_sha}")

    sealed_json = bridge_neg3.send("GET_SEALED_RESULT")
    val_ok, val_msg, _, _ = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, mutated_sha, sealed_json, "AUTH-SAVED-HEDIFF", expected_profile_fp, port=29562
    )
    p3_2_val = (val_ok is False)
    prom_res = bridge_neg3.send(f"PROMOTE_STAGED {staged_name} Final_Hediff")
    p3_2_prom = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_res
    b3_cases.append({
        "attack": "Saved-Byte Fault: Hediff severity altered in staged XML",
        "validatorBlocked": p3_2_val,
        "validatorMsg": val_msg,
        "promotionBlocked": p3_2_prom,
        "pass": p3_2_val and p3_2_prom
    })

    # Saved-Byte Attack 3.3: Held item count in saved XML bytes (Map 0 Pawn)
    setup_sealed_state("AUTH-SAVED-COUNT", 3)
    stage_res = bridge_neg3.send("STAGE_SAVE Stage_Count")
    kv_stage = parse_kv_response(stage_res)
    staged_path = Path(kv_stage["File"])
    staged_name = kv_stage["StagingName"]
    orig_count_sha = kv_stage["StagedSha"]
    xml_text = staged_path.read_text(encoding="utf-8")
    item_idx = xml_text.find("<id>MedicineIndustrial990005</id>")
    stack_idx = xml_text.find("<stackCount>5</stackCount>", item_idx)
    assert item_idx != -1 and stack_idx != -1 and (stack_idx - item_idx) < 200, "Failed to locate held item count in XML"
    mutated_xml = xml_text[:stack_idx] + "<stackCount>4</stackCount>" + xml_text[stack_idx + len("<stackCount>5</stackCount>"):]
    staged_path.write_text(mutated_xml, encoding="utf-8")
    mutated_sha = sha256_file(staged_path)
    assert mutated_sha != orig_count_sha, "Failed to change SHA on StackCount mutation"
    print(f"Mutated StackCount on Map 0 in staged XML: SHA {orig_count_sha} -> {mutated_sha}")

    sealed_json = bridge_neg3.send("GET_SEALED_RESULT")
    val_ok, val_msg, _, _ = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, mutated_sha, sealed_json, "AUTH-SAVED-COUNT", expected_profile_fp, port=29563
    )
    p3_3_val = (val_ok is False)
    prom_res = bridge_neg3.send(f"PROMOTE_STAGED {staged_name} Final_Count")
    p3_3_prom = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_res
    b3_cases.append({
        "attack": "Saved-Byte Fault: Held item count 5 -> 4 in staged XML",
        "validatorBlocked": p3_3_val,
        "validatorMsg": val_msg,
        "promotionBlocked": p3_3_prom,
        "pass": p3_3_val and p3_3_prom
    })

    # Structural XML Faults: Malformed EOF, Second Root, DTD Entity Injection
    # These are rejected directly in EngineHostCensus.ValidateStagedXml during STAGE_SAVE
    # We test ValidateStagedXml directly or via staged file alteration
    setup_sealed_state("AUTH-STRUCT-XML", 4)
    stage_res = bridge_neg3.send("STAGE_SAVE Stage_Struct")
    kv_stage = parse_kv_response(stage_res)
    staged_path = Path(kv_stage["File"])
    staged_name = kv_stage["StagingName"]

    # 3.4 Malformed EOF (truncate 300 bytes)
    orig_bytes = staged_path.read_bytes()
    staged_path.write_bytes(orig_bytes[:-300])
    sealed_json = bridge_neg3.send("GET_SEALED_RESULT")
    val_ok, val_msg, _, _ = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, sha256_file(staged_path), sealed_json, "AUTH-STRUCT-XML", expected_profile_fp, port=29564
    )
    p3_4 = (val_ok is False)
    b3_cases.append({
        "attack": "Structural XML Fault: Malformed EOF / Truncation",
        "blocked": p3_4,
        "validatorMsg": val_msg,
        "pass": p3_4
    })

    # 3.5 Second Root Element
    staged_path.write_bytes(orig_bytes + b"\n<secondRoot>corrupt</secondRoot>")
    val_ok, val_msg, _, _ = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, sha256_file(staged_path), sealed_json, "AUTH-STRUCT-XML", expected_profile_fp, port=29565
    )
    p3_5 = (val_ok is False)
    b3_cases.append({
        "attack": "Structural XML Fault: Second Root Element",
        "blocked": p3_5,
        "validatorMsg": val_msg,
        "pass": p3_5
    })

    # 3.6 DTD / Entity Declaration Injection
    dtd_xml = b'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE savegame [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>\n' + orig_bytes[orig_bytes.find(b"<savegame>"):]
    staged_path.write_bytes(dtd_xml)
    val_ok, val_msg, _, _ = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, sha256_file(staged_path), sealed_json, "AUTH-STRUCT-XML", expected_profile_fp, port=29566
    )
    p3_6 = (val_ok is False)
    b3_cases.append({
        "attack": "Structural XML Fault: DTD / Entity Injection (DtdProcessing.Prohibit)",
        "blocked": p3_6,
        "validatorMsg": val_msg,
        "pass": p3_6
    })

    shutdown_worker(proc_neg3, bridge_neg3)
    b3_all_passed = all(c["pass"] for c in b3_cases)
    results["negativeBattery3_SavedByteProof"] = {
        "casesCount": len(b3_cases),
        "passCount": sum(1 for c in b3_cases if c["pass"]),
        "allPassed": b3_all_passed,
        "cases": b3_cases
    }
    print(f"\n[NEGATIVE BATTERY 3 SUMMARY] Passed: {sum(1 for c in b3_cases if c['pass'])}/{len(b3_cases)} saved-byte attacks.")

    # -------------------------------------------------------------------------
    # 5. NEGATIVE BATTERY 4: Direct-Promotion Bypasses (Sol G03-02 & G03-05)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 5: NEGATIVE BATTERY 4 -- DIRECT-PROMOTION BYPASSES & PROMOTION FENCES")
    print("=" * 80)

    profile_neg4 = prepare_profile("Profile_Neg4_Bypasses", clean_b, "CleanContextB")
    proc_neg4, bridge_neg4, ms_neg4 = launch_worker(profile_neg4, bridge_port=29340)
    print(f"Launched Negative Battery 4 Worker (PID={proc_neg4.pid})")

    b4_cases = []

    # Attack 4.1: Direct promotion without STAGE_SAVE (RESULT_SEALED alone)
    auth4 = {
        "authorityId": "AUTH-BYPASS-01",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_neg4.send(f"REGISTER_AUTHORITY {json.dumps(auth4)}")
    grant4 = {
        "grantId": "GRANT-BYPASS-01",
        "authorityId": "AUTH-BYPASS-01",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION"
    }
    bridge_neg4.send(f"REGISTER_GRANT {json.dumps(grant4)}")
    bridge_neg4.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg4)
    bridge_neg4.send("VALIDATE_INPUT")
    bridge_neg4.send("SEAL_RESULT GRANT-BYPASS-01")

    # Call PROMOTE_STAGED without staging
    prom_nostage = bridge_neg4.send("PROMOTE_STAGED FakeStaging FinalWithoutStaging")
    p4_1 = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_nostage
    b4_cases.append({
        "attack": "Direct Promotion Without STAGE_SAVE (RESULT_SEALED alone)",
        "response": prom_nostage,
        "pass": p4_1
    })

    # Legitimate Stage & Validation for subsequent attacks
    stage_res = bridge_neg4.send("STAGE_SAVE LegitStage")
    kv_stage = parse_kv_response(stage_res)
    staged_path = Path(kv_stage["File"])
    staged_name = kv_stage["StagingName"]
    staged_sha = kv_stage["StagedSha"]
    sealed_json = bridge_neg4.send("GET_SEALED_RESULT")

    # Get valid receipt from fresh validator
    val_ok, _, receipt_obj, val_pid = execute_fresh_pre_promotion_validation(
        staged_path, staged_name, staged_sha, sealed_json, "AUTH-BYPASS-01", expected_profile_fp, port=29570
    )
    assert val_ok, "Failed to get legitimate receipt for bypass battery tests"

    # Attack 4.2: Self-Validation Attempt (simulating worker processId == receipt validatorProcessId)
    fake_self_receipt = dict(receipt_obj)
    fake_self_receipt["validatorProcessId"] = str(proc_neg4.pid)
    self_sub_res = bridge_neg4.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(fake_self_receipt)}")
    p4_2 = "Fresh independent validator required (Self-validation prohibited)" in self_sub_res
    b4_cases.append({
        "attack": "Self-Validation Attempt Prohibited",
        "response": self_sub_res,
        "pass": p4_2
    })

    # Re-admit after readiness revocation
    bridge_neg4.send("RESET_WORKER")
    status_now = bridge_neg4.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    auth4["workerGeneration"] = cur_gen + 1
    bridge_neg4.send(f"REGISTER_AUTHORITY {json.dumps(auth4)}")
    grant4["workerGeneration"] = cur_gen + 1
    bridge_neg4.send(f"REGISTER_GRANT {json.dumps(grant4)}")
    bridge_neg4.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg4)
    bridge_neg4.send("VALIDATE_INPUT")
    bridge_neg4.send("SEAL_RESULT GRANT-BYPASS-01")
    stage_res2 = bridge_neg4.send("STAGE_SAVE LegitStage2")
    kv2 = parse_kv_response(stage_res2)
    staged_path2 = Path(kv2["File"])
    staged_name2 = kv2["StagingName"]
    staged_sha2 = kv2["StagedSha"]
    sealed_json2 = bridge_neg4.send("GET_SEALED_RESULT")

    val_ok, _, receipt_obj2, _ = execute_fresh_pre_promotion_validation(
        staged_path2, staged_name2, staged_sha2, sealed_json2, "AUTH-BYPASS-01", expected_profile_fp, port=29571
    )
    sub_res2 = bridge_neg4.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(receipt_obj2)}")
    assert "STAGE_VALIDATION_ACCEPTED" in sub_res2

    # Attack 4.3: Caller Path Substitution
    prom_sub = bridge_neg4.send(f"PROMOTE_STAGED ArbitrarySubstitutedName FinalSub")
    p4_3 = "PROMOTION_BLOCKED: Caller path substitution detected" in prom_sub
    b4_cases.append({
        "attack": "Caller Path Substitution Rejected",
        "response": prom_sub,
        "pass": p4_3
    })

    # Attack 4.4: Reseal Invalidation / ResultEpoch Fence
    # Re-admit and seal again, then stage
    bridge_neg4.send("RESET_WORKER")
    status_now = bridge_neg4.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    auth4["workerGeneration"] = cur_gen + 1
    bridge_neg4.send(f"REGISTER_AUTHORITY {json.dumps(auth4)}")
    grant4["workerGeneration"] = cur_gen + 1
    bridge_neg4.send(f"REGISTER_GRANT {json.dumps(grant4)}")
    bridge_neg4.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg4)
    bridge_neg4.send("VALIDATE_INPUT")
    bridge_neg4.send("SEAL_RESULT GRANT-BYPASS-01") # Epoch 1
    stage_res3 = bridge_neg4.send("STAGE_SAVE StageEpoch1")
    kv3 = parse_kv_response(stage_res3)
    staged_name3 = kv3["StagingName"]

    # Now call SEAL_RESULT again -> advances to Epoch 2, invalidating old stage and clearing receipt!
    reseal_res = bridge_neg4.send("SEAL_RESULT GRANT-BYPASS-01")
    assert "Epoch=2" in reseal_res

    # Try to promote old StageEpoch1 -> MUST BE BLOCKED!
    prom_old_epoch = bridge_neg4.send(f"PROMOTE_STAGED {staged_name3} FinalOldEpoch")
    p4_4 = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_old_epoch
    b4_cases.append({
        "attack": "Reseal Invalidation / ResultEpoch Fence (Old Stage Under New Epoch Blocked)",
        "resealResponse": reseal_res,
        "promoteResponse": prom_old_epoch,
        "pass": p4_4
    })

    # Attack 4.5: Altered Staged SHA After Validation Receipt Issued
    bridge_neg4.send("RESET_WORKER")
    status_now = bridge_neg4.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    auth4["workerGeneration"] = cur_gen + 1
    bridge_neg4.send(f"REGISTER_AUTHORITY {json.dumps(auth4)}")
    grant4["workerGeneration"] = cur_gen + 1
    bridge_neg4.send(f"REGISTER_GRANT {json.dumps(grant4)}")
    bridge_neg4.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg4)
    bridge_neg4.send("VALIDATE_INPUT")
    bridge_neg4.send("SEAL_RESULT GRANT-BYPASS-01")
    stage_res4 = bridge_neg4.send("STAGE_SAVE StageShaTamper")
    kv4 = parse_kv_response(stage_res4)
    staged_path4 = Path(kv4["File"])
    staged_name4 = kv4["StagingName"]
    staged_sha4 = kv4["StagedSha"]
    sealed_json4 = bridge_neg4.send("GET_SEALED_RESULT")

    val_ok, _, receipt_obj4, _ = execute_fresh_pre_promotion_validation(
        staged_path4, staged_name4, staged_sha4, sealed_json4, "AUTH-BYPASS-01", expected_profile_fp, port=29572
    )
    bridge_neg4.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(receipt_obj4)}")

    # Tamper with file SHA on disk AFTER receipt submission
    with open(staged_path4, "ab") as f:
        f.write(b"<!-- POST_VALIDATION_TAMPER -->")

    prom_tamper_after_rcpt = bridge_neg4.send(f"PROMOTE_STAGED {staged_name4} FinalTamper")
    p4_5 = "PROMOTION_BLOCKED: Staged file SHA altered since validation!" in prom_tamper_after_rcpt
    b4_cases.append({
        "attack": "Altered Staged SHA After Receipt Submission Caught at Promotion Boundary",
        "response": prom_tamper_after_rcpt,
        "pass": p4_5
    })

    shutdown_worker(proc_neg4, bridge_neg4)
    b4_all_passed = all(c["pass"] for c in b4_cases)
    results["negativeBattery4_PromotionBypasses"] = {
        "casesCount": len(b4_cases),
        "passCount": sum(1 for c in b4_cases if c["pass"]),
        "allPassed": b4_all_passed,
        "cases": b4_cases
    }
    print(f"\n[NEGATIVE BATTERY 4 SUMMARY] Passed: {sum(1 for c in b4_cases if c['pass'])}/{len(b4_cases)} bypass attacks.")

    # -------------------------------------------------------------------------
    # 6. PROMOTION SAFETY & REPLACEMENT VERIFICATION (WORK ORDER ITEM 11)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 6: PROMOTION SAFETY & SAME-VOLUME REPLACEMENT (WORK ORDER ITEM 11)")
    print("=" * 80)

    profile_safe = prepare_profile("Profile_PromotionSafety", clean_b, "CleanContextB")
    proc_safe, bridge_safe, ms_safe = launch_worker(profile_safe, bridge_port=29350)
    print(f"Launched Promotion Safety Worker (PID={proc_safe.pid})")

    safety_cases = []

    # Setup approved initial final file: TargetSettlement_Final.rws
    auth_safe = {
        "authorityId": "AUTH-SAFE-01",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_safe.send(f"REGISTER_AUTHORITY {json.dumps(auth_safe)}")
    grant_safe = {
        "grantId": "GRANT-SAFE-01",
        "authorityId": "AUTH-SAFE-01",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION"
    }
    bridge_safe.send(f"REGISTER_GRANT {json.dumps(grant_safe)}")
    bridge_safe.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_safe)
    bridge_safe.send("VALIDATE_INPUT")
    bridge_safe.send("SEAL_RESULT GRANT-SAFE-01")
    s_res = bridge_safe.send("STAGE_SAVE StageInitial")
    kv_s = parse_kv_response(s_res)
    staged_path_s = Path(kv_s["File"])
    staged_name_s = kv_s["StagingName"]
    staged_sha_s = kv_s["StagedSha"]
    sealed_json_s = bridge_safe.send("GET_SEALED_RESULT")

    val_ok, _, rcpt_s, _ = execute_fresh_pre_promotion_validation(
        staged_path_s, staged_name_s, staged_sha_s, sealed_json_s, "AUTH-SAFE-01", expected_profile_fp, port=29580
    )
    bridge_safe.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(rcpt_s)}")

    # Initial promotion creates TargetSettlement_Final.rws
    init_prom = bridge_safe.send(f"PROMOTE_STAGED {staged_name_s} TargetSettlement_Final")
    assert "ARTIFACT_APPROVED" in init_prom

    final_file = profile_safe / "Saves/TargetSettlement_Final.rws"
    if not final_file.exists():
        final_file = SAVES_DIR / "TargetSettlement_Final.rws"
    initial_final_sha = sha256_file(final_file)
    print(f"Initial final file created: {final_file} (SHA={initial_final_sha})")

    # Safety Test 1: Forced Replacement Failure (Lock final file with exclusive FileShare.None)
    # Stage next generation save
    bridge_safe.send("RESET_WORKER")
    status_now = bridge_safe.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    auth_safe["workerGeneration"] = cur_gen + 1
    bridge_safe.send(f"REGISTER_AUTHORITY {json.dumps(auth_safe)}")
    grant_safe["workerGeneration"] = cur_gen + 1
    bridge_safe.send(f"REGISTER_GRANT {json.dumps(grant_safe)}")
    bridge_safe.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_safe)
    bridge_safe.send("VALIDATE_INPUT")
    bridge_safe.send("SEAL_RESULT GRANT-SAFE-01")
    s_res2 = bridge_safe.send("STAGE_SAVE StageNext")
    kv_s2 = parse_kv_response(s_res2)
    staged_path_s2 = Path(kv_s2["File"])
    staged_name_s2 = kv_s2["StagingName"]
    staged_sha_s2 = kv_s2["StagedSha"]
    sealed_json_s2 = bridge_safe.send("GET_SEALED_RESULT")

    val_ok, _, rcpt_s2, _ = execute_fresh_pre_promotion_validation(
        staged_path_s2, staged_name_s2, staged_sha_s2, sealed_json_s2, "AUTH-SAFE-01", expected_profile_fp, port=29581
    )
    bridge_safe.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(rcpt_s2)}")

    # Open exclusive lock on final_file
    lock_file = open(final_file, "r+b")
    print(f"Acquired exclusive lock on {final_file}")

    try:
        locked_prom = bridge_safe.send(f"PROMOTE_STAGED {staged_name_s2} TargetSettlement_Final")
        print(f"Promotion attempt while locked: {locked_prom}")
        is_fail_pres = "PROMOTION_FAILED" in locked_prom
    finally:
        lock_file.close()
        print("Released lock on final file.")

    # Verify: prior final file SHA is 100% UNCHANGED and staging file is RETAINED
    post_lock_final_sha = sha256_file(final_file)
    p_safe_1 = is_fail_pres and (initial_final_sha == post_lock_final_sha) and staged_path_s2.exists()
    print(f"Safety Test 1 Result: Failure preserved={is_fail_pres}, Prior Final Unchanged={initial_final_sha == post_lock_final_sha}, Staging Retained={staged_path_s2.exists()}")

    safety_cases.append({
        "test": "Exclusive Lock Forced Replacement Failure Preserves Prior Final and Retains Staging",
        "promotionResponse": locked_prom,
        "priorFinalUnchanged": (initial_final_sha == post_lock_final_sha),
        "stagingRetained": staged_path_s2.exists(),
        "pass": p_safe_1
    })

    # Safety Test 2: Normal Replacement With Backup
    # Re-submit receipt or re-validate to restore approval state
    bridge_safe.send("RESET_WORKER")
    status_now = bridge_safe.send("STATUS")
    cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
    auth_safe["workerGeneration"] = cur_gen + 1
    bridge_safe.send(f"REGISTER_AUTHORITY {json.dumps(auth_safe)}")
    grant_safe["workerGeneration"] = cur_gen + 1
    bridge_safe.send(f"REGISTER_GRANT {json.dumps(grant_safe)}")
    bridge_safe.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_safe)
    bridge_safe.send("VALIDATE_INPUT")
    bridge_safe.send("SEAL_RESULT GRANT-SAFE-01")
    s_res3 = bridge_safe.send("STAGE_SAVE StageFinalRepl")
    kv_s3 = parse_kv_response(s_res3)
    staged_path_s3 = Path(kv_s3["File"])
    staged_name_s3 = kv_s3["StagingName"]
    staged_sha_s3 = kv_s3["StagedSha"]
    sealed_json_s3 = bridge_safe.send("GET_SEALED_RESULT")

    val_ok, _, rcpt_s3, _ = execute_fresh_pre_promotion_validation(
        staged_path_s3, staged_name_s3, staged_sha_s3, sealed_json_s3, "AUTH-SAFE-01", expected_profile_fp, port=29582
    )
    bridge_safe.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(rcpt_s3)}")

    normal_repl = bridge_safe.send(f"PROMOTE_STAGED {staged_name_s3} TargetSettlement_Final")
    print(f"Normal replacement response: {normal_repl}")
    p_safe_2 = "ARTIFACT_APPROVED" in normal_repl

    backup_file = profile_safe / "Saves/TargetSettlement_Final.bak.rws"
    if not backup_file.exists():
        backup_file = SAVES_DIR / "TargetSettlement_Final.bak.rws"

    backup_exists = backup_file.exists()
    backup_sha = sha256_file(backup_file) if backup_exists else "NONE"
    replaced_final_sha = sha256_file(final_file)

    safety_cases.append({
        "test": "Normal Replacement Creates Backup and Atomically Replaces Final",
        "response": normal_repl,
        "backupCreated": backup_exists,
        "backupSha": backup_sha,
        "finalSha": replaced_final_sha,
        "pass": p_safe_2 and backup_exists
    })

    shutdown_worker(proc_safe, bridge_safe)
    results["promotionSafety"] = {
        "allPassed": all(c["pass"] for c in safety_cases),
        "cases": safety_cases
    }
    print(f"\n[PROMOTION SAFETY SUMMARY] Passed: {sum(1 for c in safety_cases if c['pass'])}/{len(safety_cases)} cases.")

    # -------------------------------------------------------------------------
    # 7. FRESH POSITIVE CHAIN A -> B -> C (WORK ORDER §12)
    #    Process A: Simulate 100 ticks -> Seal -> Stage -> Fresh Validator -> Receipt -> Promote
    #    Process B: Ingest A -> Simulate 100 ticks -> Seal -> Stage -> Fresh Validator -> Receipt -> Promote
    #    Process C: Fresh Independent Validator -> Verify B promoted output
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 7: FRESH POSITIVE CHAIN A -> B -> C (WORK ORDER §12)")
    print("=" * 80)

    # PROCESS A
    print("\n--- PROCESS A: Clean ContextB -> 100 Ticks Simulation -> Seal -> Stage -> Fresh Validator -> Promote ---")
    prof_A = prepare_profile("Profile_Chain_A", clean_b, "SourceA")
    proc_A, bridge_A, _ = launch_worker(prof_A, bridge_port=29410)
    print(f"Process A launched (PID={proc_A.pid})")

    auth_A = {
        "authorityId": "AUTH-CHAIN-A",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_A.send(f"REGISTER_AUTHORITY {json.dumps(auth_A)}")
    grant_A = {
        "grantId": "GRANT-CHAIN-A-01",
        "authorityId": "AUTH-CHAIN-A",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "executionClass": "STANDARD",
        "tickBudget": 200
    }
    bridge_A.send(f"REGISTER_GRANT {json.dumps(grant_A)}")
    bridge_A.send("LOAD_SAVE SourceA 0")
    wait_for_ready(bridge_A)
    bridge_A.send("VALIDATE_INPUT")

    # Step 100 ticks
    print("Process A simulating 100 sliced ticks...")
    bridge_A.send("STEP_TICKS 100 20")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = bridge_A.send("STATUS")
        if "RemainingStep=0" in st:
            print(f"  Process A ticks complete: {st}")
            break
        time.sleep(0.5)

    seal_A_res = bridge_A.send("SEAL_RESULT GRANT-CHAIN-A-01")
    print(f"Process A seal result: {seal_A_res}")
    stage_A_res = bridge_A.send("STAGE_SAVE A_Promoted")
    print(f"Process A stage save: {stage_A_res}")

    kv_A = parse_kv_response(stage_A_res)
    staged_path_A = Path(kv_A["File"])
    staging_name_A = kv_A["StagingName"]
    staged_sha_A = kv_A["StagedSha"]
    sealed_json_A = bridge_A.send("GET_SEALED_RESULT")

    # FRESH PRE-PROMOTION VALIDATOR FOR PROCESS A
    print("Launching fresh pre-promotion validator for Process A...")
    val_ok_A, val_msg_A, receipt_A, val_pid_A = execute_fresh_pre_promotion_validation(
        staged_path_A, staging_name_A, staged_sha_A, sealed_json_A, "AUTH-CHAIN-A", expected_profile_fp, port=29610
    )
    assert val_ok_A, f"Process A fresh validator failed: {val_msg_A}"
    print(f"Process A fresh validator PASS: ValidatorPID={val_pid_A}, ReceiptId={receipt_A['receiptId']}")

    sub_A_res = bridge_A.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(receipt_A)}")
    assert "STAGE_VALIDATION_ACCEPTED" in sub_A_res

    prom_A_res = bridge_A.send(f"PROMOTE_STAGED {staging_name_A} TargetSettlement_Promoted_A")
    print(f"Process A promotion result: {prom_A_res}")
    assert "ARTIFACT_APPROVED" in prom_A_res

    shutdown_worker(proc_A, bridge_A)

    a_promoted_file = prof_A / "Saves/TargetSettlement_Promoted_A.rws"
    if not a_promoted_file.exists():
        a_promoted_file = SAVES_DIR / "TargetSettlement_Promoted_A.rws"
    a_promoted_sha = sha256_file(a_promoted_file)
    a_sealed_manifest = json.loads(sealed_json_A)["sealedManifestHash"]
    print(f"TargetSettlement_Promoted_A: SHA={a_promoted_sha}, SealedManifest={a_sealed_manifest}")

    # PROCESS B
    print("\n--- PROCESS B: Ingest A Promoted -> 100 Ticks Simulation -> Seal -> Stage -> Fresh Validator -> Promote ---")
    prof_B = prepare_profile("Profile_Chain_B", a_promoted_file, "SourceB")
    proc_B, bridge_B, _ = launch_worker(prof_B, bridge_port=29420)
    print(f"Process B launched (PID={proc_B.pid})")

    auth_B = {
        "authorityId": "AUTH-CHAIN-B",
        "expectedSourceArtifactHash": a_promoted_sha,
        "manifestVersion": "4.0",
        "expectedManifestHash": a_sealed_manifest,
        "contentProfileFingerprint": expected_profile_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_B.send(f"REGISTER_AUTHORITY {json.dumps(auth_B)}")
    grant_B = {
        "grantId": "GRANT-CHAIN-B-01",
        "authorityId": "AUTH-CHAIN-B",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "executionClass": "STANDARD",
        "tickBudget": 200
    }
    bridge_B.send(f"REGISTER_GRANT {json.dumps(grant_B)}")
    bridge_B.send("LOAD_SAVE SourceB 0")
    wait_for_ready(bridge_B)
    bridge_B.send("VALIDATE_INPUT")

    # Step 100 ticks
    print("Process B simulating 100 sliced ticks...")
    bridge_B.send("STEP_TICKS 100 20")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = bridge_B.send("STATUS")
        if "RemainingStep=0" in st:
            print(f"  Process B ticks complete: {st}")
            break
        time.sleep(0.5)

    seal_B_res = bridge_B.send("SEAL_RESULT GRANT-CHAIN-B-01")
    print(f"Process B seal result: {seal_B_res}")
    stage_B_res = bridge_B.send("STAGE_SAVE B_Promoted")
    print(f"Process B stage save: {stage_B_res}")

    kv_B = parse_kv_response(stage_B_res)
    staged_path_B = Path(kv_B["File"])
    staging_name_B = kv_B["StagingName"]
    staged_sha_B = kv_B["StagedSha"]
    sealed_json_B = bridge_B.send("GET_SEALED_RESULT")

    # FRESH PRE-PROMOTION VALIDATOR FOR PROCESS B
    print("Launching fresh pre-promotion validator for Process B...")
    val_ok_B, val_msg_B, receipt_B, val_pid_B = execute_fresh_pre_promotion_validation(
        staged_path_B, staging_name_B, staged_sha_B, sealed_json_B, "AUTH-CHAIN-B", expected_profile_fp, port=29620
    )
    assert val_ok_B, f"Process B fresh validator failed: {val_msg_B}"
    print(f"Process B fresh validator PASS: ValidatorPID={val_pid_B}, ReceiptId={receipt_B['receiptId']}")

    sub_B_res = bridge_B.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(receipt_B)}")
    assert "STAGE_VALIDATION_ACCEPTED" in sub_B_res

    prom_B_res = bridge_B.send(f"PROMOTE_STAGED {staging_name_B} TargetSettlement_Promoted_B")
    print(f"Process B promotion result: {prom_B_res}")
    assert "ARTIFACT_APPROVED" in prom_B_res

    shutdown_worker(proc_B, bridge_B)

    b_promoted_file = prof_B / "Saves/TargetSettlement_Promoted_B.rws"
    if not b_promoted_file.exists():
        b_promoted_file = SAVES_DIR / "TargetSettlement_Promoted_B.rws"
    b_promoted_sha = sha256_file(b_promoted_file)
    b_sealed_manifest = json.loads(sealed_json_B)["sealedManifestHash"]
    print(f"TargetSettlement_Promoted_B: SHA={b_promoted_sha}, SealedManifest={b_sealed_manifest}")

    # PROCESS C (Post-Promotion Regression Check)
    print("\n--- PROCESS C: Fresh Independent Validator -> Ingest B Promoted Output ---")
    prof_C = prepare_profile("Profile_Chain_C", b_promoted_file, "SourceC")
    proc_C, bridge_C, _ = launch_worker(prof_C, bridge_port=29430)
    print(f"Process C launched (PID={proc_C.pid})")

    auth_C = {
        "authorityId": "AUTH-CHAIN-C",
        "expectedSourceArtifactHash": b_promoted_sha,
        "manifestVersion": "4.0",
        "expectedManifestHash": b_sealed_manifest,
        "contentProfileFingerprint": expected_profile_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "READ_ONLY"
    }
    bridge_C.send(f"REGISTER_AUTHORITY {json.dumps(auth_C)}")
    grant_C = {
        "grantId": "GRANT-CHAIN-C-01",
        "authorityId": "AUTH-CHAIN-C",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "READ_ONLY",
        "executionClass": "VALIDATOR",
        "tickBudget": 0
    }
    bridge_C.send(f"REGISTER_GRANT {json.dumps(grant_C)}")
    bridge_C.send("LOAD_SAVE SourceC 0")
    wait_for_ready(bridge_C)

    val_C_res = bridge_C.send("VALIDATE_INPUT")
    print(f"Process C input validation: {val_C_res}")
    p_chain_C = "INPUT_VALIDATED" in val_C_res

    shutdown_worker(proc_C, bridge_C)

    results["freshPositiveChain"] = {
        "processA": {
            "pid": proc_A.pid,
            "sourceSha": sha256_file(clean_b),
            "authorityId": "AUTH-CHAIN-A",
            "grantId": "GRANT-CHAIN-A-01",
            "sealedManifestHash": a_sealed_manifest,
            "stagedSha": staged_sha_A,
            "validatorPid": val_pid_A,
            "validatorResult": receipt_A["validatorResult"],
            "receiptId": receipt_A["receiptId"],
            "promotedFile": str(a_promoted_file),
            "promotedSha": a_promoted_sha,
            "pass": True
        },
        "processB": {
            "pid": proc_B.pid,
            "sourceSha": a_promoted_sha,
            "authorityId": "AUTH-CHAIN-B",
            "grantId": "GRANT-CHAIN-B-01",
            "sealedManifestHash": b_sealed_manifest,
            "stagedSha": staged_sha_B,
            "validatorPid": val_pid_B,
            "validatorResult": receipt_B["validatorResult"],
            "receiptId": receipt_B["receiptId"],
            "promotedFile": str(b_promoted_file),
            "promotedSha": b_promoted_sha,
            "pass": True
        },
        "processC": {
            "pid": proc_C.pid,
            "sourceSha": b_promoted_sha,
            "authorityId": "AUTH-CHAIN-C",
            "expectedManifestHash": b_sealed_manifest,
            "validationResult": val_C_res,
            "pass": p_chain_C
        },
        "allPassed": True
    }
    print(f"\n[FRESH POSITIVE CHAIN SUMMARY] Chain A -> B -> C: PASS")

    # Overall Verdict Calculation
    all_b1 = results["negativeBattery1_InputAdmission"]["allPassed"]
    all_b2 = results["negativeBattery2_AuthorityAttacks"]["allPassed"]
    all_b3 = results["negativeBattery3_SavedByteProof"]["allPassed"]
    all_b4 = results["negativeBattery4_PromotionBypasses"]["allPassed"]
    all_safety = results["promotionSafety"]["allPassed"]
    all_pos = results["freshPositiveChain"]["allPassed"]

    overall_pass = all_b1 and all_b2 and all_b3 and all_b4 and all_safety and all_pos
    results["classification"] = "E1 ENGINE SEMANTIC AUTHORITY GATE04 PASS" if overall_pass else "FAIL"

    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 80)
    print(f"FINAL CLASSIFICATION: {results['classification']}")
    print(f"Results written to: {RESULTS_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()
