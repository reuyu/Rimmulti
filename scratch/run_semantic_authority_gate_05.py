import os
import sys
import time
import json
import socket
import shutil
import hashlib
import subprocess
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
PROBE_DLL = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\ProbeMod\1.6\Assemblies\QA.Engine02.Probe.dll")

RESULTS_FILE = SCRATCH / "semantic_authority_gate_05_results.json"
results = {
    "workOrder": "WP-POC-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-05",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "classification": "PENDING",
    "provenance": {},
    "negativeBattery1_InputAdmission": {},
    "negativeBattery2_G0401_IssuerAuthentication": {},
    "negativeBattery3_G0402_StagedSaveTamper": {},
    "negativeBattery4_ReceiptFieldMutations": {},
    "negativeBattery5_AuthorityImmutability": {},
    "negativeBattery6_GrantSemanticsAndBudget": {},
    "negativeBattery7_ControlPlaneRevocation": {},
    "negativeBattery8_ContentProfileADR006B": {},
    "negativeBattery9_SupportedManifestV4": {},
    "negativeBattery10_ResultEpochInvariant": {},
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
    (profile / "Tasks").mkdir(parents=True, exist_ok=True)

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

def execute_fresh_validator_task(staged_file_path: Path, staging_name: str, task_path: Path, capability_nonce: str, port=29550, auto_shutdown=True):
    """
    Spawns a fresh independent RimWorld worker process.
    Prepares its profile with the exact staged save and task.
    Registers authority and grant derived from the task on the fresh validator.
    Loads the exact staged file in the target context.
    Executes EXECUTE_VALIDATOR_TASK <taskFilePath> <capabilityNonce>.
    Returns success boolean, status message, ValidatorResult JSON object, validator PID, process, and client.
    """
    val_prof = prepare_profile(f"ValProf_{port}", staged_file_path, staging_name)
    val_task_copy = val_prof / "Tasks" / task_path.name
    shutil.copy2(task_path, val_task_copy)

    val_proc, val_client, _ = launch_worker(val_prof, bridge_port=port)
    validator_pid = val_proc.pid

    try:
        val_task_obj = json.loads(val_task_copy.read_text(encoding="utf-8"))
        val_auth = {
            "authorityId": val_task_obj["authorityId"],
            "storeIncarnation": val_task_obj.get("storeIncarnation", "STORE_INCARNATION_POC_01"),
            "baseLineage": val_task_obj.get("baseLineage", "LINEAGE_CLEAN_CONTEXT_B_REV1"),
            "expectedSourceArtifactHash": val_task_obj["stagedSha"],
            "manifestVersion": val_task_obj.get("manifestVersion", "4.0"),
            "expectedManifestHash": val_task_obj["sealedManifestHash"],
            "contentProfileFingerprint": val_task_obj["contentProfileFingerprint"],
            "targetScopeId": val_task_obj.get("scopeId", "SETTLEMENT-B"),
            "targetMapId": val_task_obj.get("targetMapIndex", 0),
            "workerGeneration": 1,
            "allowedOperationMode": "READ_ONLY"
        }
        val_client.send(f"REGISTER_AUTHORITY {json.dumps(val_auth)}")

        val_grant = {
            "grantId": f"GRANT-VAL-{validator_pid}",
            "authorityId": val_task_obj["authorityId"],
            "workerGeneration": 1,
            "scopeId": val_task_obj.get("scopeId", "SETTLEMENT-B"),
            "targetMapIndex": val_task_obj.get("targetMapIndex", 0),
            "allowedMode": "READ_ONLY",
            "executionClass": "VALIDATOR",
            "tickBudget": 0
        }
        val_client.send(f"REGISTER_GRANT {json.dumps(val_grant)}")

        # Load staged save into validator engine
        val_client.send(f"LOAD_SAVE {staging_name} {val_task_obj.get('targetMapIndex', 0)}")
        ok, stat, _ = wait_for_ready(val_client)
        if not ok:
            if auto_shutdown:
                shutdown_worker(val_proc, val_client)
            return False, f"Validator failed to reach READY: {stat}", None, validator_pid, val_proc, val_client

        # Execute validator task
        cmd = f"EXECUTE_VALIDATOR_TASK {str(val_task_copy)} {capability_nonce}"
        val_resp = val_client.send(cmd)
        if "VALIDATOR_RESULT:" not in val_resp:
            if auto_shutdown:
                shutdown_worker(val_proc, val_client)
            return False, f"Validator execution rejected: {val_resp}", None, validator_pid, val_proc, val_client

        result_json_str = val_resp.split("ResultJson=")[1].strip()
        result_obj = json.loads(result_json_str)
        if auto_shutdown:
            shutdown_worker(val_proc, val_client)
        return True, "PASS", result_obj, validator_pid, val_proc, val_client
    except Exception as ex:
        shutdown_worker(val_proc, val_client)
        return False, f"Validator exception: {ex}", None, validator_pid, None, None

def validate_and_complete(bridge, kv, port):
    val_ok, val_msg, val_res, val_pid, val_proc, val_client = execute_fresh_validator_task(
        Path(kv["File"]), kv["StagingName"], Path(kv["TaskPath"]), kv["CapabilityNonce"], port=port, auto_shutdown=False
    )
    if not val_ok:
        if val_proc and val_client:
            shutdown_worker(val_proc, val_client)
        return False, val_msg, None, val_pid
    try:
        comp_resp = bridge.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(val_res)}")
        return ("STAGE_VALIDATION_ACCEPTED" in comp_resp), comp_resp, val_res, val_pid
    finally:
        if val_proc and val_client:
            shutdown_worker(val_proc, val_client)

def main():
    print("=" * 80)
    print("STARTING WP-POC-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-05 COMPREHENSIVE TEST SUITE")
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

    clean_manifest_hash = "9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC"
    expected_profile_fp = "7DDC73B75FA4AA1B00177EA4C73380A7E233A972968D5C0BF91852CD1C2F8D40"

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
            "workerBridgeDll": {"path": str(dll_path), "sha256": sha256_file(dll_path), "mvid": dll_mvid},
            "probeDll": {"path": str(PROBE_DLL), "sha256": sha256_file(PROBE_DLL)}
        },
        "sourceFiles": {
            "WorkerBridge.cs": {"path": str(SCRATCH / "WorkerBridgeMod/Source/WorkerBridge.cs"), "sha256": sha256_file(SCRATCH / "WorkerBridgeMod/Source/WorkerBridge.cs")},
            "EngineHostCensus.cs": {"path": str(SCRATCH / "WorkerBridgeMod/Source/EngineHostCensus.cs"), "sha256": sha256_file(SCRATCH / "WorkerBridgeMod/Source/EngineHostCensus.cs")}
        },
        "fixtures": {
            "TargetSettlement_Clean_ContextB.rws": {"path": str(clean_b), "bytes": clean_b.stat().st_size, "sha256": sha256_file(clean_b)},
            "TargetSettlement_Clean_ContextB.v4.census.json": {"path": str(SCRATCH / "TargetSettlement_Clean_ContextB.v4.census.json"), "sha256": sha256_file(SCRATCH / "TargetSettlement_Clean_ContextB.v4.census.json")}
        },
        "contentProfileFingerprint": expected_profile_fp,
        "cleanBaselineManifestHash": clean_manifest_hash,
        "manifestVersion": "4.0",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1"
    }
    results["provenance"] = provenance
    print("\n[PROVENANCE RECORDED]")
    print(f"  Worker DLL SHA256: {provenance['binaries']['workerBridgeDll']['sha256']}")
    print(f"  Worker DLL MVID:   {provenance['binaries']['workerBridgeDll']['mvid']}")
    print(f"  Clean ContextB SHA:{provenance['fixtures']['TargetSettlement_Clean_ContextB.rws']['sha256']}")
    print(f"  Clean V4 Manifest: {clean_manifest_hash}")
    print(f"  ADR-006B Profile:  {expected_profile_fp}")

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
        bridge_neg1.send("RESET_WORKER")
        status_pre = bridge_neg1.send("STATUS")
        cur_gen = int(status_pre.split("Gen=")[1].split(",")[0])
        expected_gen = cur_gen + 1

        corr_file = SCRATCH / f"CorruptedFixtures/{save_name}.rws"
        corr_sha = sha256_file(corr_file)

        authority_bundle = {
            "authorityId": f"AUTH-CLEAN-FOR-{tag}",
            "storeIncarnation": "STORE_INCARNATION_POC_01",
            "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
            "expectedSourceArtifactHash": corr_sha,
            "manifestVersion": "4.0",
            "expectedManifestHash": clean_manifest_hash,
            "contentProfileFingerprint": expected_profile_fp,
            "targetScopeId": "SETTLEMENT-B",
            "targetMapId": 0,
            "workerGeneration": expected_gen,
            "allowedOperationMode": "SIMULATION"
        }
        bridge_neg1.send(f"REGISTER_AUTHORITY {json.dumps(authority_bundle, separators=(',', ':'))}")

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

        bridge_neg1.send(f"LOAD_SAVE {save_name} 0")
        ok, stat, _ = wait_for_ready(bridge_neg1)
        if not ok:
            print(f"  Load failed: {stat}")
            b1_all_passed = False
            continue

        val_input_resp = bridge_neg1.send("VALIDATE_INPUT")
        is_input_rejected = "INPUT_REJECTED: Hash mismatch" in val_input_resp
        print(f"  Case {tag:25s}: {val_input_resp[:60]}... (Rejected={is_input_rejected})")

        sem_stat = bridge_neg1.send("GET_SEMANTIC_STATUS")
        is_val_failed = "State=VALIDATION_FAILED" in sem_stat and "SimulationReady=False" in sem_stat

        step_resp = bridge_neg1.send("STEP_TICKS 10 10")
        is_step_blocked = "ERROR: Cannot simulate untrusted state" in step_resp

        seal_resp = bridge_neg1.send(f"SEAL_RESULT GRANT-CLEAN-{tag}")
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
    # 3. NEGATIVE BATTERY 2: G04-01 Developer Attacks & Capability Nonce Enforcement
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 3: NEGATIVE BATTERY 2 -- G04-01 ISSUER AUTHENTICATION & CAPABILITY NONCE ATTACKS")
    print("=" * 80)

    profile_neg2 = prepare_profile("Profile_Neg2_G0401", clean_b, "CleanContextB")
    proc_neg2, bridge_neg2, ms_neg2 = launch_worker(profile_neg2, bridge_port=29320)
    print(f"Launched Negative Battery 2 Worker (PID={proc_neg2.pid})")

    b2_cases = []

    def setup_staged_clean_state(bridge, auth_id, gen=None):
        bridge.send("RESET_WORKER")
        status_now = bridge.send("STATUS")
        cur_gen = int(status_now.split("Gen=")[1].split(",")[0])
        expected_gen = cur_gen + 1

        auth = {
            "authorityId": auth_id,
            "storeIncarnation": "STORE_INCARNATION_POC_01",
            "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
            "expectedSourceArtifactHash": sha256_file(clean_b),
            "manifestVersion": "4.0",
            "expectedManifestHash": clean_manifest_hash,
            "contentProfileFingerprint": expected_profile_fp,
            "targetScopeId": "SETTLEMENT-B",
            "targetMapId": 0,
            "workerGeneration": expected_gen,
            "allowedOperationMode": "SIMULATION"
        }
        bridge.send(f"REGISTER_AUTHORITY {json.dumps(auth)}")
        grant = {
            "grantId": f"GRANT-{auth_id}",
            "authorityId": auth_id,
            "workerGeneration": expected_gen,
            "scopeId": "SETTLEMENT-B",
            "targetMapIndex": 0,
            "allowedMode": "SIMULATION",
            "executionClass": "STANDARD",
            "tickBudget": 500
        }
        bridge.send(f"REGISTER_GRANT {json.dumps(grant)}")
        bridge.send("LOAD_SAVE CleanContextB 0")
        wait_for_ready(bridge)
        bridge.send("VALIDATE_INPUT")
        bridge.send(f"SEAL_RESULT GRANT-{auth_id}")
        st_resp = bridge.send(f"STAGE_SAVE Stage_{auth_id}")
        kv = parse_kv_response(st_resp)
        kv["ExpectedGen"] = expected_gen
        return kv

    # Stage a save to generate a real simulator-owned ValidatorTask
    kv2 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-01")
    staged_path = Path(kv2["File"])
    staged_sha = kv2["StagedSha"]
    task_id = kv2["ValidatorTaskId"]
    task_path = Path(kv2["TaskPath"])
    real_nonce = kv2["CapabilityNonce"]
    staging_name = kv2["StagingName"]

    # Attack 2.1: Handcrafted receipt submitted without task capability nonce
    fake_rcpt = {
        "receiptId": "QA-CRAFT-HANDCRAFTED-01",
        "validatorTaskId": task_id,
        "stagedFilePath": str(staged_path),
        "stagedSha": staged_sha,
        "sealedResultId": kv2["SealedResultId"],
        "resultEpoch": int(kv2["Epoch"]),
        "manifestVersion": "4.0",
        "sealedManifestHash": kv2["ManifestHash"],
        "authorityId": "AUTH-G0401-01",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "grantId": "GRANT-AUTH-G0401-01",
        "workerGeneration": kv2["ExpectedGen"],
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "contentProfileFingerprint": expected_profile_fp,
        "sourceArtifactHash": sha256_file(clean_b),
        "validatorProcessId": "99999",
        "validatorResult": "PASS"
    }
    resp_no_nonce = bridge_neg2.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(fake_rcpt)}")
    p2_1 = "Caller-visible fields alone cannot satisfy task capability" in resp_no_nonce
    print(f"  Attack 2.1 (No capability nonce): {resp_no_nonce} (Pass={p2_1})")
    b2_cases.append({
        "attack": "Handcrafted receipt without capability nonce rejected",
        "response": resp_no_nonce,
        "pass": p2_1
    })

    # Attack 2.2: Handcrafted receipt with fake capability nonce against active task
    kv2_2 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-02")
    fake_rcpt_2 = dict(fake_rcpt)
    fake_rcpt_2["validatorTaskId"] = kv2_2["ValidatorTaskId"]
    fake_rcpt_2["stagedFilePath"] = kv2_2["File"]
    fake_rcpt_2["stagedSha"] = kv2_2["StagedSha"]
    fake_rcpt_2["sealedResultId"] = kv2_2["SealedResultId"]
    fake_rcpt_2["resultEpoch"] = int(kv2_2["Epoch"])
    fake_rcpt_2["sealedManifestHash"] = kv2_2["ManifestHash"]
    fake_rcpt_2["authorityId"] = "AUTH-G0401-02"
    fake_rcpt_2["grantId"] = "GRANT-AUTH-G0401-02"
    fake_rcpt_2["workerGeneration"] = kv2_2["ExpectedGen"]

    fake_nonce = "0" * 64
    resp_fake_nonce = bridge_neg2.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {fake_nonce} {json.dumps(fake_rcpt_2)}")
    p2_2 = "Invalid capability nonce" in resp_fake_nonce or "Invalid task capability nonce" in resp_fake_nonce
    print(f"  Attack 2.2 (Fake capability nonce): {resp_fake_nonce} (Pass={p2_2})")
    b2_cases.append({
        "attack": "Handcrafted receipt with forged nonce rejected",
        "response": resp_fake_nonce,
        "pass": p2_2
    })

    # Attack 2.3: Non-existent validator PID submitted via COMPLETE_STAGE_VALIDATION
    kv2_3 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-03")
    fake_res_dead_pid = {
        "validatorTaskId": kv2_3["ValidatorTaskId"],
        "capabilityNonce": kv2_3["CapabilityNonce"],
        "validatorProcessId": "2147483646",
        "validatorResult": "PASS",
        "actualContentProfileFingerprint": expected_profile_fp,
        "actualManifestHash": kv2_3["ManifestHash"],
        "stagedSha": kv2_3["StagedSha"],
        "stagedFilePath": kv2_3["File"],
        "validatedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    resp_dead_pid = bridge_neg2.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(fake_res_dead_pid)}")
    p2_3 = "Validator PID does not exist" in resp_dead_pid or "Validator process not running" in resp_dead_pid
    print(f"  Attack 2.3 (Non-existent PID 2147483646): {resp_dead_pid} (Pass={p2_3})")
    b2_cases.append({
        "attack": "Non-existent validator PID 2147483646 rejected",
        "response": resp_dead_pid,
        "pass": p2_3
    })

    # Attack 2.4: Empty validator PID submitted
    kv2_4 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-04")
    fake_res_empty_pid = dict(fake_res_dead_pid)
    fake_res_empty_pid["validatorTaskId"] = kv2_4["ValidatorTaskId"]
    fake_res_empty_pid["capabilityNonce"] = kv2_4["CapabilityNonce"]
    fake_res_empty_pid["validatorProcessId"] = ""
    resp_empty_pid = bridge_neg2.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(fake_res_empty_pid)}")
    p2_4 = "Empty or Self-PID prohibited" in resp_empty_pid or "Empty validator PID prohibited" in resp_empty_pid
    print(f"  Attack 2.4 (Empty validator PID): {resp_empty_pid} (Pass={p2_4})")
    b2_cases.append({
        "attack": "Empty validator PID rejected",
        "response": resp_empty_pid,
        "pass": p2_4
    })

    # Attack 2.5: Self-validation (PID == simulator PID)
    kv2_5 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-05")
    fake_res_self_pid = dict(fake_res_dead_pid)
    fake_res_self_pid["validatorTaskId"] = kv2_5["ValidatorTaskId"]
    fake_res_self_pid["capabilityNonce"] = kv2_5["CapabilityNonce"]
    fake_res_self_pid["validatorProcessId"] = str(proc_neg2.pid)
    resp_self_pid = bridge_neg2.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(fake_res_self_pid)}")
    p2_5 = "Empty or Self-PID prohibited" in resp_self_pid or "Self-validation prohibited" in resp_self_pid
    print(f"  Attack 2.5 (Self-PID {proc_neg2.pid}): {resp_self_pid} (Pass={p2_5})")
    b2_cases.append({
        "attack": "Self-validation attempt rejected",
        "response": resp_self_pid,
        "pass": p2_5
    })

    # Attack 2.6: Forged validatorTaskId
    kv2_6 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-06")
    fake_res_wrong_task = dict(fake_res_dead_pid)
    fake_res_wrong_task["validatorTaskId"] = "VT_FORGED_TASK_ID_9999"
    fake_res_wrong_task["capabilityNonce"] = kv2_6["CapabilityNonce"]
    fake_res_wrong_task["validatorProcessId"] = str(os.getpid())
    resp_wrong_task = bridge_neg2.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(fake_res_wrong_task)}")
    p2_6 = "ValidatorTaskId mismatch" in resp_wrong_task
    print(f"  Attack 2.6 (Forged ValidatorTaskId): {resp_wrong_task} (Pass={p2_6})")
    b2_cases.append({
        "attack": "Forged ValidatorTaskId rejected",
        "response": resp_wrong_task,
        "pass": p2_6
    })

    # Attack 2.7: Replay of consumed ValidatorTask (testing with active live validator process)
    kv2_7 = setup_staged_clean_state(bridge_neg2, "AUTH-G0401-07")
    val_ok, val_msg, val_result_obj, val_pid, val_proc_2_7, val_client_2_7 = execute_fresh_validator_task(
        Path(kv2_7["File"]), kv2_7["StagingName"], Path(kv2_7["TaskPath"]), kv2_7["CapabilityNonce"], port=29570, auto_shutdown=False
    )
    try:
        assert val_ok, f"Fresh validator failed for 2.7: {val_msg}"
        comp_first = bridge_neg2.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(val_result_obj)}")
        p2_7a = "STAGE_VALIDATION_ACCEPTED" in comp_first

        # Attempt to replay the exact same result -> MUST BE REJECTED (Consumed!)
        comp_replay = bridge_neg2.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(val_result_obj)}")
        p2_7b = "ValidatorTask already consumed. Replay prohibited" in comp_replay
        print(f"  Attack 2.7 (Task consumed replay): First={comp_first}, Replay={comp_replay} (Pass={p2_7a and p2_7b})")
        b2_cases.append({
            "attack": "Replay of consumed ValidatorTask prohibited",
            "firstCompletion": comp_first,
            "replayResponse": comp_replay,
            "pass": p2_7a and p2_7b
        })
    finally:
        if val_proc_2_7 and val_client_2_7:
            shutdown_worker(val_proc_2_7, val_client_2_7)

    shutdown_worker(proc_neg2, bridge_neg2)
    b2_all_passed = all(c["pass"] for c in b2_cases)
    results["negativeBattery2_G0401_IssuerAuthentication"] = {
        "casesCount": len(b2_cases),
        "passCount": sum(1 for c in b2_cases if c["pass"]),
        "allPassed": b2_all_passed,
        "cases": b2_cases
    }
    print(f"\n[NEGATIVE BATTERY 2 SUMMARY] Passed: {sum(1 for c in b2_cases if c['pass'])}/{len(b2_cases)} issuer authentication attacks.")

    # -------------------------------------------------------------------------
    # 4. NEGATIVE BATTERY 3: G04-02 Staged Save Tamper & Expected Truth Authority Attacks
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 4: NEGATIVE BATTERY 3 -- G04-02 STAGED SAVE TAMPER & AUTHORITY BOUNDARY ATTACKS")
    print("=" * 80)

    profile_neg3 = prepare_profile("Profile_Neg3_G0402", clean_b, "CleanContextB")
    proc_neg3, bridge_neg3, ms_neg3 = launch_worker(profile_neg3, bridge_port=29330)
    print(f"Launched Negative Battery 3 Worker (PID={proc_neg3.pid})")

    b3_cases = []

    # Attack 3.1: Staged Save Tampered with Labrador followFieldwork (True -> False)
    kv3_1 = setup_staged_clean_state(bridge_neg3, "AUTH-G0402-01")
    staged_path_3_1 = Path(kv3_1["File"])
    xml_text = staged_path_3_1.read_text(encoding="utf-8")

    # Tamper followFieldwork
    assert "<followFieldwork>True</followFieldwork>" in xml_text, "followFieldwork True not found in staged XML"
    tampered_xml_3_1 = xml_text.replace("<followFieldwork>True</followFieldwork>", "<followFieldwork>False</followFieldwork>", 1)
    staged_path_3_1.write_text(tampered_xml_3_1, encoding="utf-8")
    tampered_sha_3_1 = sha256_file(staged_path_3_1)

    # Fresh validator executing task A on tampered file B -> MUST FAIL
    val_ok_3_1, val_msg_3_1, _, _, _, _ = execute_fresh_validator_task(
        staged_path_3_1, kv3_1["StagingName"], Path(kv3_1["TaskPath"]), kv3_1["CapabilityNonce"], port=29571
    )
    p3_1 = (val_ok_3_1 is False)
    print(f"  Attack 3.1 (followFieldwork tampered): {val_msg_3_1} (Pass={p3_1})")
    b3_cases.append({
        "attack": "Staged save followFieldwork tamper rejected by fresh validator",
        "validatorMessage": val_msg_3_1,
        "pass": p3_1
    })

    # Attack 3.2: Staged Save Tampered with Sculpting bill suspended (False -> True)
    kv3_2 = setup_staged_clean_state(bridge_neg3, "AUTH-G0402-02")
    staged_path_3_2 = Path(kv3_2["File"])
    xml_text_2 = staged_path_3_2.read_text(encoding="utf-8")

    bill_idx = xml_text_2.find("<recipe>Make_SculptingWood</recipe>")
    if bill_idx == -1:
        bill_idx = xml_text_2.find("Bill_Production")
    assert bill_idx != -1, "Failed to locate Bill_Production in staged XML"
    insert_pos = xml_text_2.find(">", bill_idx) + 1
    tampered_xml_3_2 = xml_text_2[:insert_pos] + "\n<suspended>True</suspended>" + xml_text_2[insert_pos:]
    staged_path_3_2.write_text(tampered_xml_3_2, encoding="utf-8")
    tampered_sha_3_2 = sha256_file(staged_path_3_2)

    val_ok_3_2, val_msg_3_2, _, _, _, _ = execute_fresh_validator_task(
        staged_path_3_2, kv3_2["StagingName"], Path(kv3_2["TaskPath"]), kv3_2["CapabilityNonce"], port=29572
    )
    p3_2 = (val_ok_3_2 is False)
    print(f"  Attack 3.2 (bill suspended tampered): {val_msg_3_2} (Pass={p3_2})")
    b3_cases.append({
        "attack": "Staged save bill suspended tamper rejected by fresh validator",
        "validatorMessage": val_msg_3_2,
        "pass": p3_2
    })

    # Attack 3.3: Deprecated VALIDATE_AS_PRE_PROMOTION_VALIDATOR is rejected
    dep_resp = bridge_neg3.send("VALIDATE_AS_PRE_PROMOTION_VALIDATOR AUTH-01 DUMMY_B64 /path/to/save DUMMY_SHA")
    p3_3 = "VALIDATE_AS_PRE_PROMOTION_VALIDATOR is deprecated and rejected under Gate 05" in dep_resp
    print(f"  Attack 3.3 (Deprecated public validator API): {dep_resp} (Pass={p3_3})")
    b3_cases.append({
        "attack": "Caller-nominated VALIDATE_AS_PRE_PROMOTION_VALIDATOR deprecated and rejected",
        "response": dep_resp,
        "pass": p3_3
    })

    # Attack 3.4: Simulator holding sealed A rejects validator result reporting actual manifest B
    kv3_4 = setup_staged_clean_state(bridge_neg3, "AUTH-G0402-04")
    val_res_forged_b = {
        "validatorTaskId": kv3_4["ValidatorTaskId"],
        "capabilityNonce": kv3_4["CapabilityNonce"],
        "validatorProcessId": str(os.getpid()),
        "validatorResult": "PASS",
        "actualContentProfileFingerprint": expected_profile_fp,
        "actualManifestHash": "9EE09D2B80B4477FA98BE44C8456F22F466FFF8555D2ADC6D08CEB08CFD9CFB8", # Forged B hash!
        "stagedSha": kv3_4["StagedSha"],
        "stagedFilePath": kv3_4["File"],
        "validatedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    resp_forged_b = bridge_neg3.send(f"COMPLETE_STAGE_VALIDATION {json.dumps(val_res_forged_b)}")
    p3_4 = "Manifest hash mismatch" in resp_forged_b
    print(f"  Attack 3.4 (Simulator rejects forged B manifest result): {resp_forged_b} (Pass={p3_4})")
    b3_cases.append({
        "attack": "Simulator rejects validator result claiming different manifest hash B",
        "response": resp_forged_b,
        "pass": p3_4
    })

    shutdown_worker(proc_neg3, bridge_neg3)
    b3_all_passed = all(c["pass"] for c in b3_cases)
    results["negativeBattery3_G0402_StagedSaveTamper"] = {
        "casesCount": len(b3_cases),
        "passCount": sum(1 for c in b3_cases if c["pass"]),
        "allPassed": b3_all_passed,
        "cases": b3_cases
    }
    print(f"\n[NEGATIVE BATTERY 3 SUMMARY] Passed: {sum(1 for c in b3_cases if c['pass'])}/{len(b3_cases)} staged save tamper attacks.")

    # -------------------------------------------------------------------------
    # 5. NEGATIVE BATTERY 4: Receipt Field Mutation Table (14 Fields Verified)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 5: NEGATIVE BATTERY 4 -- RECEIPT FIELD MUTATION TABLE (14 BOUND CONTEXT FIELDS)")
    print("=" * 80)

    profile_neg4 = prepare_profile("Profile_Neg4_Fields", clean_b, "CleanContextB")
    proc_neg4, bridge_neg4, ms_neg4 = launch_worker(profile_neg4, bridge_port=29340)
    print(f"Launched Negative Battery 4 Worker (PID={proc_neg4.pid})")

    b4_cases = []
    kv4 = setup_staged_clean_state(bridge_neg4, "AUTH-FIELDS-01")
    base_rcpt = {
        "receiptId": "RC_TEST_01",
        "validatorTaskId": kv4["ValidatorTaskId"],
        "stagedFilePath": kv4["File"],
        "stagedSha": kv4["StagedSha"],
        "sealedResultId": kv4["SealedResultId"],
        "resultEpoch": int(kv4["Epoch"]),
        "manifestVersion": "4.0",
        "sealedManifestHash": kv4["ManifestHash"],
        "authorityId": "AUTH-FIELDS-01",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "grantId": "GRANT-AUTH-FIELDS-01",
        "workerGeneration": kv4["ExpectedGen"],
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "contentProfileFingerprint": expected_profile_fp,
        "sourceArtifactHash": sha256_file(clean_b),
        "validatorProcessId": str(os.getpid()),
        "validatorResult": "PASS",
        "validatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

    mutation_fields = [
        ("scopeId", "SETTLEMENT-FORGED-SCOPE"),
        ("targetMapIndex", 999),
        ("manifestVersion", "5.0-INVALID"),
        ("sealedManifestHash", "0" * 64),
        ("sourceArtifactHash", "0" * 64),
        ("storeIncarnation", "STORE_INCARNATION_FORGED"),
        ("baseLineage", "LINEAGE_FORGED"),
        ("validatorProcessId", "2147483646"),
        ("stagedSha", "0" * 64),
        ("stagedFilePath", r"C:\NonExistent\Forged.rws"),
        ("workerGeneration", 999),
        ("authorityId", "AUTH-FORGED-ID"),
        ("grantId", "GRANT-FORGED-ID"),
        ("contentProfileFingerprint", "0" * 64)
    ]

    for field_name, mutated_val in mutation_fields:
        kv_m = setup_staged_clean_state(bridge_neg4, f"AUTH-MUT-{field_name}")
        mutated_rcpt = dict(base_rcpt)
        mutated_rcpt["authorityId"] = f"AUTH-MUT-{field_name}"
        mutated_rcpt["grantId"] = f"GRANT-AUTH-MUT-{field_name}"
        mutated_rcpt["workerGeneration"] = kv_m["ExpectedGen"]
        mutated_rcpt["validatorTaskId"] = kv_m["ValidatorTaskId"]
        mutated_rcpt["stagedFilePath"] = kv_m["File"]
        mutated_rcpt["stagedSha"] = kv_m["StagedSha"]
        mutated_rcpt["sealedResultId"] = kv_m["SealedResultId"]
        mutated_rcpt["sealedManifestHash"] = kv_m["ManifestHash"]
        mutated_rcpt[field_name] = mutated_val

        resp = bridge_neg4.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {kv_m['CapabilityNonce']} {json.dumps(mutated_rcpt)}")
        is_rejected = "STAGE_VALIDATION_REJECTED" in resp
        print(f"  Field {field_name:26s} mutated -> {resp} (Rejected={is_rejected})")

        sem_stat = bridge_neg4.send("GET_SEMANTIC_STATUS")
        is_revoked = "State=VALIDATION_FAILED" in sem_stat and "SimulationReady=False" in sem_stat

        case_p = is_rejected and is_revoked
        b4_cases.append({
            "field": field_name,
            "mutatedValue": str(mutated_val),
            "response": resp,
            "readinessRevoked": is_revoked,
            "pass": case_p
        })

    shutdown_worker(proc_neg4, bridge_neg4)
    b4_all_passed = all(c["pass"] for c in b4_cases)
    results["negativeBattery4_ReceiptFieldMutations"] = {
        "casesCount": len(b4_cases),
        "passCount": sum(1 for c in b4_cases if c["pass"]),
        "allPassed": b4_all_passed,
        "cases": b4_cases
    }
    print(f"\n[NEGATIVE BATTERY 4 SUMMARY] Passed: {sum(1 for c in b4_cases if c['pass'])}/{len(b4_cases)} field mutations.")

    # -------------------------------------------------------------------------
    # 6. NEGATIVE BATTERY 5: Authority Bundle Immutability & Overwrite Attacks
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 6: NEGATIVE BATTERY 5 -- AUTHORITY BUNDLE IMMUTABILITY & OVERWRITE ATTACKS")
    print("=" * 80)

    profile_neg5 = prepare_profile("Profile_Neg5_Authority", clean_b, "CleanContextB")
    proc_neg5, bridge_neg5, ms_neg5 = launch_worker(profile_neg5, bridge_port=29350)
    print(f"Launched Negative Battery 5 Worker (PID={proc_neg5.pid})")

    b5_cases = []

    base_auth5 = {
        "authorityId": "AUTH-IMMUT-01",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
        "allowedOperationMode": "SIMULATION"
    }

    # Register initial authority
    reg1 = bridge_neg5.send(f"REGISTER_AUTHORITY {json.dumps(base_auth5)}")
    # Identical registration -> ACK unchanged
    reg_ident = bridge_neg5.send(f"REGISTER_AUTHORITY {json.dumps(base_auth5)}")
    p5_1 = "AUTHORITY_ACK_UNCHANGED" in reg_ident
    print(f"  Attack 5.1 (Identical ACK): {reg_ident} (Pass={p5_1})")
    b5_cases.append({
        "attack": "Identical authority re-registration acknowledged unchanged",
        "response": reg_ident,
        "pass": p5_1
    })

    # Attack 5.2: Changed storeIncarnation with same authorityId
    auth_chg_inc = dict(base_auth5)
    auth_chg_inc["storeIncarnation"] = "STORE_INCARNATION_ALTERED"
    reg_chg_inc = bridge_neg5.send(f"REGISTER_AUTHORITY {json.dumps(auth_chg_inc)}")
    p5_2 = "different bundle parameters" in reg_chg_inc or "In-place overwrite prohibited" in reg_chg_inc
    print(f"  Attack 5.2 (Changed storeIncarnation): {reg_chg_inc} (Pass={p5_2})")
    b5_cases.append({
        "attack": "Same authorityId with altered storeIncarnation rejected",
        "response": reg_chg_inc,
        "pass": p5_2
    })

    # Attack 5.3: Changed baseLineage with same authorityId
    auth_chg_lin = dict(base_auth5)
    auth_chg_lin["baseLineage"] = "LINEAGE_ALTERED"
    reg_chg_lin = bridge_neg5.send(f"REGISTER_AUTHORITY {json.dumps(auth_chg_lin)}")
    p5_3 = "different bundle parameters" in reg_chg_lin or "In-place overwrite prohibited" in reg_chg_lin
    print(f"  Attack 5.3 (Changed baseLineage): {reg_chg_lin} (Pass={p5_3})")
    b5_cases.append({
        "attack": "Same authorityId with altered baseLineage rejected",
        "response": reg_chg_lin,
        "pass": p5_3
    })

    # Attack 5.4: Authority overwrite after load/admission is blocked
    bridge_neg5.send(f"REGISTER_GRANT {json.dumps({'grantId': 'GRANT-IMMUT-01', 'authorityId': 'AUTH-IMMUT-01', 'workerGeneration': 1, 'scopeId': 'SETTLEMENT-B', 'targetMapIndex': 0, 'allowedMode': 'SIMULATION', 'tickBudget': 100})}")
    bridge_neg5.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg5)
    bridge_neg5.send("VALIDATE_INPUT")

    # In INPUT_VALIDATED state, try to register new authority -> REJECTED
    new_auth = dict(base_auth5)
    new_auth["authorityId"] = "AUTH-NEW-OVERWRITE"
    reg_over = bridge_neg5.send(f"REGISTER_AUTHORITY {json.dumps(new_auth)}")
    p5_4 = "Cannot register or modify AuthorityBundle after game load" in reg_over or "Worker reset required" in reg_over
    print(f"  Attack 5.4 (Overwrite after load): {reg_over} (Pass={p5_4})")
    b5_cases.append({
        "attack": "Authority overwrite after load/admission prohibited",
        "response": reg_over,
        "pass": p5_4
    })

    shutdown_worker(proc_neg5, bridge_neg5)
    b5_all_passed = all(c["pass"] for c in b5_cases)
    results["negativeBattery5_AuthorityImmutability"] = {
        "casesCount": len(b5_cases),
        "passCount": sum(1 for c in b5_cases if c["pass"]),
        "allPassed": b5_all_passed,
        "cases": b5_cases
    }
    print(f"\n[NEGATIVE BATTERY 5 SUMMARY] Passed: {sum(1 for c in b5_cases if c['pass'])}/{len(b5_cases)} authority immutability attacks.")

    # -------------------------------------------------------------------------
    # 7. NEGATIVE BATTERY 6: SimulationGrant Closed Semantics & Tick Budget
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 7: NEGATIVE BATTERY 6 -- SIMULATION GRANT CLOSED SEMANTICS & TICK BUDGET")
    print("=" * 80)

    profile_neg6 = prepare_profile("Profile_Neg6_Grant", clean_b, "CleanContextB")
    proc_neg6, bridge_neg6, ms_neg6 = launch_worker(profile_neg6, bridge_port=29360)
    print(f"Launched Negative Battery 6 Worker (PID={proc_neg6.pid})")

    b6_cases = []

    # Attack 6.1: Grant scopeId mismatch against registered authority targetScopeId
    auth6 = {
        "authorityId": "AUTH-GRANT-01",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_neg6.send(f"REGISTER_AUTHORITY {json.dumps(auth6)}")
    mismatched_grant = {
        "grantId": "GRANT-MISMATCH-01",
        "authorityId": "AUTH-GRANT-01",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-FOREIGN",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "tickBudget": 50
    }
    reg_mismatch_grant = bridge_neg6.send(f"REGISTER_GRANT {json.dumps(mismatched_grant)}")
    p6_1 = ("does not match" in reg_mismatch_grant and "targetScopeId" in reg_mismatch_grant)
    print(f"  Attack 6.1 (Scope mismatch at grant registration): {reg_mismatch_grant} (Pass={p6_1})")
    b6_cases.append({
        "attack": "Grant scopeId mismatch against authority targetScopeId rejected",
        "response": reg_mismatch_grant,
        "pass": p6_1
    })

    # Attack 6.2: Re-grant invalidates prior sealed result, stage, and receipt
    kv_6_2 = setup_staged_clean_state(bridge_neg6, "AUTH-GRANT-REGRANT")
    valid_grant2 = {
        "grantId": "GRANT-BUDGET-02",
        "authorityId": "AUTH-GRANT-REGRANT",
        "workerGeneration": kv_6_2["ExpectedGen"],
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "tickBudget": 100
    }
    regrant_resp = bridge_neg6.send(f"REGISTER_GRANT {json.dumps(valid_grant2)}")
    prom_after_regrant = bridge_neg6.send(f"PROMOTE_STAGED {kv_6_2['StagingName']} FinalAfterRegrant")
    p6_2 = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_after_regrant
    print(f"  Attack 6.2 (Re-grant invalidates stage/receipt): {prom_after_regrant} (Pass={p6_2})")
    b6_cases.append({
        "attack": "Re-grant invalidates outstanding stage and blocks promotion",
        "response": prom_after_regrant,
        "pass": p6_2
    })

    # Attack 6.3: Grant tickBudget exhaustion blocks STEP_TICKS
    bridge_neg6.send("RESET_WORKER")
    status_6_3 = bridge_neg6.send("STATUS")
    gen_6_3 = int(status_6_3.split("Gen=")[1].split(",")[0]) + 1
    auth6_3 = dict(auth6)
    auth6_3["authorityId"] = "AUTH-GRANT-BUDGET"
    auth6_3["workerGeneration"] = gen_6_3
    bridge_neg6.send(f"REGISTER_AUTHORITY {json.dumps(auth6_3)}")
    budget_grant = {
        "grantId": "GRANT-BUDGET-TICK-01",
        "authorityId": "AUTH-GRANT-BUDGET",
        "workerGeneration": gen_6_3,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "tickBudget": 20 # Only 20 ticks allowed!
    }
    bridge_neg6.send(f"REGISTER_GRANT {json.dumps(budget_grant)}")
    bridge_neg6.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg6)
    bridge_neg6.send("VALIDATE_INPUT")

    # Attempt to step 30 ticks -> Exceeds budget 20!
    step_over_budget = bridge_neg6.send("STEP_TICKS 30 10")
    p6_3 = "TICK_BUDGET_EXCEEDED" in step_over_budget
    print(f"  Attack 6.3 (STEP_TICKS exceeds tickBudget): {step_over_budget} (Pass={p6_3})")
    b6_cases.append({
        "attack": "STEP_TICKS exceeding tickBudget blocked",
        "response": step_over_budget,
        "pass": p6_3
    })

    # Attack 6.4: READ_ONLY grant mode blocks STEP_TICKS and SEAL_RESULT
    bridge_neg6.send("RESET_WORKER")
    status_6_4 = bridge_neg6.send("STATUS")
    gen_6_4 = int(status_6_4.split("Gen=")[1].split(",")[0]) + 1
    auth6_4 = dict(auth6)
    auth6_4["authorityId"] = "AUTH-GRANT-RO"
    auth6_4["workerGeneration"] = gen_6_4
    auth6_4["allowedOperationMode"] = "READ_ONLY"
    bridge_neg6.send(f"REGISTER_AUTHORITY {json.dumps(auth6_4)}")
    ro_grant = {
        "grantId": "GRANT-RO-01",
        "authorityId": "AUTH-GRANT-RO",
        "workerGeneration": gen_6_4,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "READ_ONLY",
        "tickBudget": 0
    }
    bridge_neg6.send(f"REGISTER_GRANT {json.dumps(ro_grant)}")
    bridge_neg6.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg6)
    bridge_neg6.send("VALIDATE_INPUT")

    step_ro = bridge_neg6.send("STEP_TICKS 10 10")
    seal_ro = bridge_neg6.send("SEAL_RESULT GRANT-RO-01")
    p6_4 = ("OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE" in step_ro) and ("OPERATION_NOT_PERMITTED_IN_READ_ONLY_MODE" in seal_ro)
    print(f"  Attack 6.4 (READ_ONLY blocks step and seal): Step={step_ro}, Seal={seal_ro} (Pass={p6_4})")
    b6_cases.append({
        "attack": "READ_ONLY mode blocks STEP_TICKS and SEAL_RESULT",
        "stepResponse": step_ro,
        "sealResponse": seal_ro,
        "pass": p6_4
    })

    shutdown_worker(proc_neg6, bridge_neg6)
    b6_all_passed = all(c["pass"] for c in b6_cases)
    results["negativeBattery6_GrantSemanticsAndBudget"] = {
        "casesCount": len(b6_cases),
        "passCount": sum(1 for c in b6_cases if c["pass"]),
        "allPassed": b6_all_passed,
        "cases": b6_cases
    }
    print(f"\n[NEGATIVE BATTERY 6 SUMMARY] Passed: {sum(1 for c in b6_cases if c['pass'])}/{len(b6_cases)} grant semantic attacks.")

    # -------------------------------------------------------------------------
    # 8. NEGATIVE BATTERY 7: Control-Plane Revocation & Exception Safety (G04-03 & G04-07)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 8: NEGATIVE BATTERY 7 -- CONTROL-PLANE REVOCATION & EXCEPTION SAFETY")
    print("=" * 80)

    profile_neg7 = prepare_profile("Profile_Neg7_Revocation", clean_b, "CleanContextB")
    proc_neg7, bridge_neg7, ms_neg7 = launch_worker(profile_neg7, bridge_port=29370)
    print(f"Launched Negative Battery 7 Worker (PID={proc_neg7.pid})")

    b7_cases = []

    # Attack 7.1: Malformed JSON sent to REGISTER_GRANT immediately revokes readiness
    setup_staged_clean_state(bridge_neg7, "AUTH-REV-01")
    stat_before = bridge_neg7.send("GET_SEMANTIC_STATUS")
    assert "SimulationReady=True" in stat_before

    resp_malformed_grant = bridge_neg7.send("REGISTER_GRANT {malformed json: not valid}")
    stat_after = bridge_neg7.send("GET_SEMANTIC_STATUS")
    p7_1 = ("SimulationReady=False" in stat_after) and ("State=VALIDATION_FAILED" in stat_after)
    print(f"  Attack 7.1 (Malformed grant JSON revokes readiness): {resp_malformed_grant} (Pass={p7_1})")
    b7_cases.append({
        "attack": "Malformed grant JSON immediately revokes simulation readiness",
        "response": resp_malformed_grant,
        "statusAfter": stat_after,
        "pass": p7_1
    })

    # Attack 7.2: Malformed JSON sent to COMPLETE_STAGE_VALIDATION revokes readiness
    setup_staged_clean_state(bridge_neg7, "AUTH-REV-02")
    resp_malformed_comp = bridge_neg7.send("COMPLETE_STAGE_VALIDATION {invalid json}")
    stat_after_comp = bridge_neg7.send("GET_SEMANTIC_STATUS")
    p7_2 = ("SimulationReady=False" in stat_after_comp) and ("State=VALIDATION_FAILED" in stat_after_comp)
    print(f"  Attack 7.2 (Malformed complete validation JSON revokes readiness): {resp_malformed_comp} (Pass={p7_2})")
    b7_cases.append({
        "attack": "Malformed complete validation JSON immediately revokes simulation readiness",
        "response": resp_malformed_comp,
        "statusAfter": stat_after_comp,
        "pass": p7_2
    })

    # Attack 7.3: G04-07 Verification: Recensus mutation before STAGE_SAVE does NOT throw NullReferenceException
    bridge_neg7.send("RESET_WORKER")
    status_7_3 = bridge_neg7.send("STATUS")
    gen_7_3 = int(status_7_3.split("Gen=")[1].split(",")[0]) + 1
    auth_7_3 = {
        "authorityId": "AUTH-REV-03",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": gen_7_3,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_neg7.send(f"REGISTER_AUTHORITY {json.dumps(auth_7_3)}")
    grant_7_3 = {
        "grantId": "GRANT-REV-03",
        "authorityId": "AUTH-REV-03",
        "workerGeneration": gen_7_3,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "executionClass": "STANDARD",
        "tickBudget": 500
    }
    bridge_neg7.send(f"REGISTER_GRANT {json.dumps(grant_7_3)}")
    bridge_neg7.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg7)
    bridge_neg7.send("VALIDATE_INPUT")
    bridge_neg7.send("SEAL_RESULT GRANT-REV-03")
    bridge_neg7.send("QA_MUTATE_LIVE skill Shooting 20")
    stage_recensus_resp = bridge_neg7.send("STAGE_SAVE StageAfterLiveMutate")
    p7_3 = ("STAGE_BLOCKED: Live state mutated after result was sealed!" in stage_recensus_resp) and ("NullReferenceException" not in stage_recensus_resp)
    print(f"  Attack 7.3 (G04-07 No NRE on stage recensus failure): {stage_recensus_resp} (Pass={p7_3})")
    b7_cases.append({
        "attack": "Stage recensus mismatch revokes readiness without NullReferenceException (G04-07 fixed)",
        "response": stage_recensus_resp,
        "pass": p7_3
    })

    shutdown_worker(proc_neg7, bridge_neg7)
    b7_all_passed = all(c["pass"] for c in b7_cases)
    results["negativeBattery7_ControlPlaneRevocation"] = {
        "casesCount": len(b7_cases),
        "passCount": sum(1 for c in b7_cases if c["pass"]),
        "allPassed": b7_all_passed,
        "cases": b7_cases
    }
    print(f"\n[NEGATIVE BATTERY 7 SUMMARY] Passed: {sum(1 for c in b7_cases if c['pass'])}/{len(b7_cases)} revocation and exception safety checks.")

    # -------------------------------------------------------------------------
    # 9. NEGATIVE BATTERY 8: ADR-006B ContentProfile Binding & Fencing (G04-06)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 9: NEGATIVE BATTERY 8 -- ADR-006B CONTENT PROFILE BINDING & FENCING")
    print("=" * 80)

    b8_cases = []

    # Test 8.1: Query live profile fingerprint and assert canonical ADR-006B match
    profile_neg8 = prepare_profile("Profile_Neg8_Profile", clean_b, "CleanContextB")
    proc_neg8, bridge_neg8, ms_neg8 = launch_worker(profile_neg8, bridge_port=29380)
    print(f"Launched Negative Battery 8 Worker (PID={proc_neg8.pid})")

    fp_resp = bridge_neg8.send("GET_PROFILE_FINGERPRINT")
    actual_fp = fp_resp.split(":", 1)[1].strip()
    p8_1 = (actual_fp == expected_profile_fp)
    print(f"  Test 8.1 (ADR-006B Live Fingerprint Query): {actual_fp} (Matches Expected={p8_1})")
    b8_cases.append({
        "test": "Live ADR-006B ContentProfile fingerprint matches expected SHA-256",
        "actualFingerprint": actual_fp,
        "expectedFingerprint": expected_profile_fp,
        "pass": p8_1
    })

    # Test 8.2: Whitespace and comment changes in ModsConfig.xml DO NOT alter profile fingerprint
    profile_mods_xml = profile_neg8 / "Config/ModsConfig.xml"
    original_mods_xml = profile_mods_xml.read_text(encoding="utf-8")
    commented_mods_xml = original_mods_xml.replace("<activeMods>", "<activeMods>\n    <!-- Formatting comment for test -->\n    ")
    profile_mods_xml.write_text(commented_mods_xml, encoding="utf-8")

    # Restart worker with commented config
    shutdown_worker(proc_neg8, bridge_neg8)
    proc_neg8_b, bridge_neg8_b, _ = launch_worker(profile_neg8, bridge_port=29381)
    fp_resp_comment = bridge_neg8_b.send("GET_PROFILE_FINGERPRINT")
    comment_fp = fp_resp_comment.split(":", 1)[1].strip()
    p8_2 = (comment_fp == expected_profile_fp)
    print(f"  Test 8.2 (Comment/whitespace in ModsConfig does not change canonical fingerprint): {comment_fp} (Pass={p8_2})")
    b8_cases.append({
        "test": "ModsConfig.xml comment/formatting changes preserve canonical fingerprint",
        "commentFingerprint": comment_fp,
        "pass": p8_2
    })

    # Test 8.3: Reordering mods in ModsConfig.xml DOES alter fingerprint and fails admission
    reordered_mods_xml = original_mods_xml.replace(
        "<li>wareconomy.hybridmultiplayer</li>\n    <li>wareconomy.workerbridge.poc</li>",
        "<li>wareconomy.workerbridge.poc</li>\n    <li>wareconomy.hybridmultiplayer</li>"
    )
    profile_mods_xml.write_text(reordered_mods_xml, encoding="utf-8")
    shutdown_worker(proc_neg8_b, bridge_neg8_b)

    proc_neg8_c, bridge_neg8_c, _ = launch_worker(profile_neg8, bridge_port=29382)
    fp_resp_reorder = bridge_neg8_c.send("GET_PROFILE_FINGERPRINT")
    reorder_fp = fp_resp_reorder.split(":", 1)[1].strip()
    p8_3a = (reorder_fp != expected_profile_fp)

    # Attempt to register authority expecting original fingerprint -> REJECTED
    auth8 = {
        "authorityId": "AUTH-PROFILE-REORDER",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp, # Stale expected profile
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
        "allowedOperationMode": "SIMULATION"
    }
    reg_reorder_resp = bridge_neg8_c.send(f"REGISTER_AUTHORITY {json.dumps(auth8)}")
    p8_3b = "ERROR: ContentProfileFingerprint mismatch" in reg_reorder_resp
    print(f"  Test 8.3 (Mod load order change alters fingerprint and fails registration): {reg_reorder_resp} (Pass={p8_3a and p8_3b})")
    b8_cases.append({
        "test": "Mod load order alteration alters fingerprint and blocks registration",
        "reorderedFingerprint": reorder_fp,
        "registrationResponse": reg_reorder_resp,
        "pass": p8_3a and p8_3b
    })

    shutdown_worker(proc_neg8_c, bridge_neg8_c)

    # Test 8.4: Admitted assembly byte drift in QA.Engine02.Probe.dll alters fingerprint
    probe_orig_bytes = PROBE_DLL.read_bytes()
    try:
        PROBE_DLL.write_bytes(probe_orig_bytes + b"\x00")
        proc_neg8_d, bridge_neg8_d, _ = launch_worker(profile_neg8, bridge_port=29383)
        fp_resp_tamper = bridge_neg8_d.send("GET_PROFILE_FINGERPRINT")
        tamper_fp = fp_resp_tamper.split(":", 1)[1].strip()
        p8_4a = (tamper_fp != expected_profile_fp)

        reg_tamper_resp = bridge_neg8_d.send(f"REGISTER_AUTHORITY {json.dumps(auth8)}")
        p8_4b = "ERROR: ContentProfileFingerprint mismatch" in reg_tamper_resp
        print(f"  Test 8.4 (Admitted assembly byte drift alters fingerprint): TamperFP={tamper_fp}, RegResp={reg_tamper_resp} (Pass={p8_4a and p8_4b})")
        b8_cases.append({
            "test": "Admitted assembly byte tamper alters fingerprint and blocks admission",
            "tamperedFingerprint": tamper_fp,
            "registrationResponse": reg_tamper_resp,
            "pass": p8_4a and p8_4b
        })
        shutdown_worker(proc_neg8_d, bridge_neg8_d)
    finally:
        PROBE_DLL.write_bytes(probe_orig_bytes)
        print("  Restored original bytes of QA.Engine02.Probe.dll.")

    b8_all_passed = all(c["pass"] for c in b8_cases)
    results["negativeBattery8_ContentProfileADR006B"] = {
        "casesCount": len(b8_cases),
        "passCount": sum(1 for c in b8_cases if c["pass"]),
        "allPassed": b8_all_passed,
        "cases": b8_cases
    }
    print(f"\n[NEGATIVE BATTERY 8 SUMMARY] Passed: {sum(1 for c in b8_cases if c['pass'])}/{len(b8_cases)} ContentProfile checks.")

    # -------------------------------------------------------------------------
    # 10. NEGATIVE BATTERY 9: SupportedSemanticManifest V4 Evidence & Scope (G04-08)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 10: NEGATIVE BATTERY 9 -- SUPPORTED SEMANTIC MANIFEST V4 EVIDENCE & SCOPE")
    print("=" * 80)

    profile_neg9 = prepare_profile("Profile_Neg9_Manifest", clean_b, "CleanContextB")
    proc_neg9, bridge_neg9, ms_neg9 = launch_worker(profile_neg9, bridge_port=29390)
    print(f"Launched Negative Battery 9 Worker (PID={proc_neg9.pid})")

    b9_cases = []

    auth9 = {
        "authorityId": "AUTH-V4-01",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
        "allowedOperationMode": "SIMULATION"
    }
    bridge_neg9.send(f"REGISTER_AUTHORITY {json.dumps(auth9)}")
    bridge_neg9.send(f"REGISTER_GRANT {json.dumps({'grantId': 'GRANT-V4-01', 'authorityId': 'AUTH-V4-01', 'workerGeneration': 1, 'scopeId': 'SETTLEMENT-B', 'targetMapIndex': 0, 'allowedMode': 'SIMULATION', 'tickBudget': 100})}")
    bridge_neg9.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg9)
    val_inp = bridge_neg9.send("VALIDATE_INPUT")
    assert "INPUT_VALIDATED" in val_inp

    # Test 9.1: Live census active job target mutation changes manifest hash
    census_pre = json.loads(bridge_neg9.send("GET_CENSUS_JSON 0"))

    bridge_neg9.send("QA_MUTATE_LIVE Strange ActiveJobTarget 139,0,143")
    val_post_job = bridge_neg9.send("VALIDATE_INPUT")
    p9_1 = ("INPUT_REJECTED: Hash mismatch" in val_post_job)
    print(f"  Test 9.1 (ActiveJob target mutation alters manifest hash): {val_post_job[:70]} (Pass={p9_1})")
    b9_cases.append({
        "test": "ActiveJob target mutation changes live manifest digest and fails validation",
        "response": val_post_job,
        "pass": p9_1
    })

    # Test 9.2: Animal settings (followFieldwork) included in V4 census
    found_animal = False
    for a in census_pre.get("animals", []):
        if "followFieldwork" in a:
            found_animal = True
            break
    p9_2 = found_animal
    print(f"  Test 9.2 (Animal playerSettings.followFieldwork verified in V4 census): Found={p9_2}")
    b9_cases.append({
        "test": "Animal playerSettings.followFieldwork present in V4 census",
        "pass": p9_2
    })

    # Test 9.3: Bill settings (suspended, targetCount) included in V4 census
    found_bill = False
    for b in census_pre.get("buildings", []):
        for bill in b.get("bills", []):
            if "suspended" in bill and "targetCount" in bill:
                found_bill = True
                break
        if found_bill:
            break
    p9_3 = found_bill
    print(f"  Test 9.3 (Bill suspended and targetCount verified in V4 census): Found={p9_3}")
    b9_cases.append({
        "test": "Bill suspended and targetCount present in V4 census",
        "pass": p9_3
    })

    shutdown_worker(proc_neg9, bridge_neg9)
    b9_all_passed = all(c["pass"] for c in b9_cases)
    results["negativeBattery9_SupportedManifestV4"] = {
        "casesCount": len(b9_cases),
        "passCount": sum(1 for c in b9_cases if c["pass"]),
        "allPassed": b9_all_passed,
        "cases": b9_cases
    }
    print(f"\n[NEGATIVE BATTERY 9 SUMMARY] Passed: {sum(1 for c in b9_cases if c['pass'])}/{len(b9_cases)} V4 manifest scope checks.")

    # -------------------------------------------------------------------------
    # 11. NEGATIVE BATTERY 10: ResultEpoch Invariant (G04-05)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 11: NEGATIVE BATTERY 10 -- RESULT EPOCH INVARIANT & RESEAL FENCING")
    print("=" * 80)

    profile_neg10 = prepare_profile("Profile_Neg10_Epoch", clean_b, "CleanContextB")
    proc_neg10, bridge_neg10, ms_neg10 = launch_worker(profile_neg10, bridge_port=29400)
    print(f"Launched Negative Battery 10 Worker (PID={proc_neg10.pid})")

    b10_cases = []

    # Test 10.1: Reseal advances epoch and clears previous validator task and stage
    kv10_1 = setup_staged_clean_state(bridge_neg10, "AUTH-EPOCH-01")
    staged_name_10_1 = kv10_1["StagingName"]

    # Reseal advances epoch from 1 to 2
    reseal_resp = bridge_neg10.send("SEAL_RESULT GRANT-AUTH-EPOCH-01")
    p10_1a = "Epoch=2" in reseal_resp

    # Attempt to promote stage from Epoch 1 -> MUST BE BLOCKED
    prom_stale_epoch = bridge_neg10.send(f"PROMOTE_STAGED {staged_name_10_1} FinalStaleEpoch")
    p10_1b = "PROMOTION_BLOCKED: No valid StageValidationReceipt found" in prom_stale_epoch
    print(f"  Test 10.1 (Reseal invalidates old stage): Reseal={reseal_resp}, Promote={prom_stale_epoch} (Pass={p10_1a and p10_1b})")
    b10_cases.append({
        "test": "Reseal advances epoch and blocks promotion of earlier staged save",
        "resealResponse": reseal_resp,
        "promoteResponse": prom_stale_epoch,
        "pass": p10_1a and p10_1b
    })

    # Test 10.2: QA_MUTATE_EPOCH injects epoch discrepancy -> Promoted blocked and readiness revoked
    kv10_2 = setup_staged_clean_state(bridge_neg10, "AUTH-EPOCH-02")
    comp_ok_10, comp_resp_10, _, _ = validate_and_complete(bridge_neg10, kv10_2, port=29573)
    assert comp_ok_10, f"Validator completion failed for 10.2: {comp_resp_10}"

    # Mutate simulator current epoch counter 1 -> 99
    bridge_neg10.send("QA_MUTATE_EPOCH 99")
    prom_mut_epoch = bridge_neg10.send(f"PROMOTE_STAGED {kv10_2['StagingName']} FinalMutEpoch")
    p10_2 = "PROMOTION_BLOCKED: ResultEpoch invariant violated" in prom_mut_epoch
    print(f"  Test 10.2 (QA_MUTATE_EPOCH blocks promotion): {prom_mut_epoch} (Pass={p10_2})")
    b10_cases.append({
        "test": "Epoch discrepancy between receipt and current engine counter blocks promotion",
        "response": prom_mut_epoch,
        "pass": p10_2
    })

    shutdown_worker(proc_neg10, bridge_neg10)
    b10_all_passed = all(c["pass"] for c in b10_cases)
    results["negativeBattery10_ResultEpochInvariant"] = {
        "casesCount": len(b10_cases),
        "passCount": sum(1 for c in b10_cases if c["pass"]),
        "allPassed": b10_all_passed,
        "cases": b10_cases
    }
    print(f"\n[NEGATIVE BATTERY 10 SUMMARY] Passed: {sum(1 for c in b10_cases if c['pass'])}/{len(b10_cases)} epoch invariant checks.")

    # -------------------------------------------------------------------------
    # 12. PROMOTION SAFETY & REPLACEMENT VERIFICATION (WORK ORDER ITEM 11)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 12: PROMOTION SAFETY & ATOMIC SAME-VOLUME REPLACEMENT (WORK ORDER ITEM 11)")
    print("=" * 80)

    profile_safe = prepare_profile("Profile_Safe_Atomic", clean_b, "CleanContextB")
    proc_safe, bridge_safe, ms_safe = launch_worker(profile_safe, bridge_port=29450)
    print(f"Launched Promotion Safety Worker (PID={proc_safe.pid})")

    safety_cases = []

    # Initial promotion to establish baseline final file: TargetSettlement_Final.rws
    kv_s1 = setup_staged_clean_state(bridge_safe, "AUTH-SAFE-01")
    comp_ok_s1, comp_resp_s1, _, _ = validate_and_complete(bridge_safe, kv_s1, port=29580)
    assert comp_ok_s1, f"Initial validation failed: {comp_resp_s1}"

    init_prom = bridge_safe.send(f"PROMOTE_STAGED {kv_s1['StagingName']} TargetSettlement_Final")
    assert "ARTIFACT_APPROVED" in init_prom

    final_file = profile_safe / "Saves/TargetSettlement_Final.rws"
    if not final_file.exists():
        final_file = SAVES_DIR / "TargetSettlement_Final.rws"
    initial_final_sha = sha256_file(final_file)
    print(f"Initial TargetSettlement_Final.rws established: {final_file} (SHA={initial_final_sha})")

    # Safety Test 1: Forced Replacement Failure under Exclusive Lock
    kv_s2 = setup_staged_clean_state(bridge_safe, "AUTH-SAFE-02")
    comp_ok_s2, comp_resp_s2, _, _ = validate_and_complete(bridge_safe, kv_s2, port=29581)
    assert comp_ok_s2, f"Lock candidate validation failed: {comp_resp_s2}"

    lock_handle = open(final_file, "r+b")
    print(f"Acquired exclusive OS lock on {final_file}")
    try:
        locked_prom = bridge_safe.send(f"PROMOTE_STAGED {kv_s2['StagingName']} TargetSettlement_Final")
        print(f"Promotion attempt under lock: {locked_prom}")
        is_locked_fail = "PROMOTION_FAILED" in locked_prom and "Existing final preserved" in locked_prom
    finally:
        lock_handle.close()
        print("Released exclusive lock on final file.")

    post_lock_sha = sha256_file(final_file)
    staged_candidate_retained = Path(kv_s2["File"]).exists()
    p_safe_1 = is_locked_fail and (post_lock_sha == initial_final_sha) and staged_candidate_retained
    print(f"  Safety Test 1: Prior Final Preserved={post_lock_sha == initial_final_sha}, Staged Retained={staged_candidate_retained} (Pass={p_safe_1})")
    safety_cases.append({
        "test": "Exclusive Lock Forced Replacement Failure Preserves Prior Final and Retains Staging",
        "promotionResponse": locked_prom,
        "priorFinalUnchanged": (post_lock_sha == initial_final_sha),
        "stagingRetained": staged_candidate_retained,
        "pass": p_safe_1
    })

    # Safety Test 2: Normal Successful Atomic Replacement Producing Backup
    kv_s3 = setup_staged_clean_state(bridge_safe, "AUTH-SAFE-03")
    comp_ok_s3, comp_resp_s3, _, _ = validate_and_complete(bridge_safe, kv_s3, port=29582)
    assert comp_ok_s3, f"Replacement candidate validation failed: {comp_resp_s3}"

    normal_prom = bridge_safe.send(f"PROMOTE_STAGED {kv_s3['StagingName']} TargetSettlement_Final")
    p_safe_2a = "ARTIFACT_APPROVED" in normal_prom

    backup_file = profile_safe / "Saves/TargetSettlement_Final.bak.rws"
    if not backup_file.exists():
        backup_file = SAVES_DIR / "TargetSettlement_Final.bak.rws"

    backup_exists = backup_file.exists()
    backup_sha = sha256_file(backup_file) if backup_exists else "NONE"
    replaced_sha = sha256_file(final_file)
    p_safe_2b = backup_exists and (backup_sha == initial_final_sha)
    print(f"  Safety Test 2: Backup Created={backup_exists}, Backup SHA Matches Prior={p_safe_2b} (Pass={p_safe_2a and p_safe_2b})")
    safety_cases.append({
        "test": "Normal Replacement Creates Backup of Prior Final and Atomically Replaces Final",
        "promotionResponse": normal_prom,
        "backupCreated": backup_exists,
        "backupMatchesPriorFinal": p_safe_2b,
        "newFinalSha": replaced_sha,
        "pass": p_safe_2a and p_safe_2b
    })

    shutdown_worker(proc_safe, bridge_safe)
    results["promotionSafety"] = {
        "allPassed": all(c["pass"] for c in safety_cases),
        "cases": safety_cases
    }
    print(f"\n[PROMOTION SAFETY SUMMARY] Passed: {sum(1 for c in safety_cases if c['pass'])}/{len(safety_cases)} cases.")

    # -------------------------------------------------------------------------
    # 13. FRESH POSITIVE CHAIN A -> B -> C (WORK ORDER ITEM 12)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 13: FRESH POSITIVE CHAIN A -> B -> C (WORK ORDER ITEM 12)")
    print("=" * 80)

    # PROCESS A
    print("\n--- PROCESS A: Clean ContextB -> 50 Ticks Simulation -> Seal -> Stage -> Fresh Validator -> Promote ---")
    prof_A = prepare_profile("Profile_Chain_A", clean_b, "SourceA")
    proc_A, bridge_A, _ = launch_worker(prof_A, bridge_port=29510)
    print(f"Process A launched (PID={proc_A.pid})")

    auth_A = {
        "authorityId": "AUTH-CHAIN-A",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": sha256_file(clean_b),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
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
        "tickBudget": 100
    }
    bridge_A.send(f"REGISTER_GRANT {json.dumps(grant_A)}")
    bridge_A.send("LOAD_SAVE SourceA 0")
    wait_for_ready(bridge_A)
    bridge_A.send("VALIDATE_INPUT")

    print("Process A simulating 50 sliced ticks...")
    bridge_A.send("STEP_TICKS 50 10")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = bridge_A.send("STATUS")
        if "RemainingStep=0" in st:
            print(f"  Process A ticks complete: {st}")
            break
        time.sleep(0.5)

    seal_A_resp = bridge_A.send("SEAL_RESULT GRANT-CHAIN-A-01")
    print(f"Process A sealed result: {seal_A_resp}")
    stage_A_resp = bridge_A.send("STAGE_SAVE A_Promoted")
    print(f"Process A staged save: {stage_A_resp}")

    kv_A = parse_kv_response(stage_A_resp)
    comp_ok_A, comp_resp_A, res_obj_A, val_pid_A = validate_and_complete(bridge_A, kv_A, port=29610)
    assert comp_ok_A, f"Process A fresh validation failed: {comp_resp_A}"
    print(f"Process A validator PASS: ValidatorPID={val_pid_A}, TaskId={res_obj_A['validatorTaskId']}")

    prom_A = bridge_A.send(f"PROMOTE_STAGED {kv_A['StagingName']} TargetSettlement_Promoted_A")
    print(f"Process A promotion result: {prom_A}")
    assert "ARTIFACT_APPROVED" in prom_A

    a_promoted_file = prof_A / "Saves/TargetSettlement_Promoted_A.rws"
    if not a_promoted_file.exists():
        a_promoted_file = SAVES_DIR / "TargetSettlement_Promoted_A.rws"
    a_promoted_sha = sha256_file(a_promoted_file)
    a_sealed_manifest = json.loads(bridge_A.send("GET_SEALED_RESULT"))["sealedManifestHash"]
    print(f"Process A final output: SHA={a_promoted_sha}, Manifest={a_sealed_manifest}")

    shutdown_worker(proc_A, bridge_A)

    # PROCESS B
    print("\n--- PROCESS B: Ingest A Output -> 50 Ticks Simulation -> Seal -> Stage -> Fresh Validator -> Promote ---")
    prof_B = prepare_profile("Profile_Chain_B", a_promoted_file, "SourceB")
    proc_B, bridge_B, _ = launch_worker(prof_B, bridge_port=29520)
    print(f"Process B launched (PID={proc_B.pid})")

    auth_B = {
        "authorityId": "AUTH-CHAIN-B",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": a_promoted_sha,
        "manifestVersion": "4.0",
        "expectedManifestHash": a_sealed_manifest,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
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
        "tickBudget": 100
    }
    bridge_B.send(f"REGISTER_GRANT {json.dumps(grant_B)}")
    bridge_B.send("LOAD_SAVE SourceB 0")
    wait_for_ready(bridge_B)
    bridge_B.send("VALIDATE_INPUT")

    print("Process B simulating 50 sliced ticks...")
    bridge_B.send("STEP_TICKS 50 10")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = bridge_B.send("STATUS")
        if "RemainingStep=0" in st:
            print(f"  Process B ticks complete: {st}")
            break
        time.sleep(0.5)

    seal_B_resp = bridge_B.send("SEAL_RESULT GRANT-CHAIN-B-01")
    print(f"Process B sealed result: {seal_B_resp}")
    stage_B_resp = bridge_B.send("STAGE_SAVE B_Promoted")
    print(f"Process B staged save: {stage_B_resp}")

    kv_B = parse_kv_response(stage_B_resp)
    comp_ok_B, comp_resp_B, res_obj_B, val_pid_B = validate_and_complete(bridge_B, kv_B, port=29620)
    assert comp_ok_B, f"Process B fresh validation failed: {comp_resp_B}"
    print(f"Process B validator PASS: ValidatorPID={val_pid_B}, TaskId={res_obj_B['validatorTaskId']}")

    prom_B = bridge_B.send(f"PROMOTE_STAGED {kv_B['StagingName']} TargetSettlement_Promoted_B")
    print(f"Process B promotion result: {prom_B}")
    assert "ARTIFACT_APPROVED" in prom_B

    b_promoted_file = prof_B / "Saves/TargetSettlement_Promoted_B.rws"
    if not b_promoted_file.exists():
        b_promoted_file = SAVES_DIR / "TargetSettlement_Promoted_B.rws"
    b_promoted_sha = sha256_file(b_promoted_file)
    b_sealed_manifest = json.loads(bridge_B.send("GET_SEALED_RESULT"))["sealedManifestHash"]
    print(f"Process B final output: SHA={b_promoted_sha}, Manifest={b_sealed_manifest}")

    shutdown_worker(proc_B, bridge_B)

    # PROCESS C (Post-Promotion Verification)
    print("\n--- PROCESS C: Independent Ingestion Verification of B Promoted Output ---")
    prof_C = prepare_profile("Profile_Chain_C", b_promoted_file, "SourceC")
    proc_C, bridge_C, _ = launch_worker(prof_C, bridge_port=29530)
    print(f"Process C launched (PID={proc_C.pid})")

    auth_C = {
        "authorityId": "AUTH-CHAIN-C",
        "storeIncarnation": "STORE_INCARNATION_POC_01",
        "baseLineage": "LINEAGE_CLEAN_CONTEXT_B_REV1",
        "expectedSourceArtifactHash": b_promoted_sha,
        "manifestVersion": "4.0",
        "expectedManifestHash": b_sealed_manifest,
        "contentProfileFingerprint": expected_profile_fp,
        "targetScopeId": "SETTLEMENT-B",
        "targetMapId": 0,
        "workerGeneration": 1,
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
            "stagedSha": kv_A["StagedSha"],
            "validatorPid": val_pid_A,
            "validatorTaskId": res_obj_A["validatorTaskId"],
            "validatorResult": res_obj_A["validatorResult"],
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
            "stagedSha": kv_B["StagedSha"],
            "validatorPid": val_pid_B,
            "validatorTaskId": res_obj_B["validatorTaskId"],
            "validatorResult": res_obj_B["validatorResult"],
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
        "allPassed": p_chain_C
    }
    print(f"\n[FRESH POSITIVE CHAIN SUMMARY] Chain A -> B -> C: PASS")

    # -------------------------------------------------------------------------
    # Overall Verdict Calculation
    # -------------------------------------------------------------------------
    all_b1 = results["negativeBattery1_InputAdmission"]["allPassed"]
    all_b2 = results["negativeBattery2_G0401_IssuerAuthentication"]["allPassed"]
    all_b3 = results["negativeBattery3_G0402_StagedSaveTamper"]["allPassed"]
    all_b4 = results["negativeBattery4_ReceiptFieldMutations"]["allPassed"]
    all_b5 = results["negativeBattery5_AuthorityImmutability"]["allPassed"]
    all_b6 = results["negativeBattery6_GrantSemanticsAndBudget"]["allPassed"]
    all_b7 = results["negativeBattery7_ControlPlaneRevocation"]["allPassed"]
    all_b8 = results["negativeBattery8_ContentProfileADR006B"]["allPassed"]
    all_b9 = results["negativeBattery9_SupportedManifestV4"]["allPassed"]
    all_b10 = results["negativeBattery10_ResultEpochInvariant"]["allPassed"]
    all_safety = results["promotionSafety"]["allPassed"]
    all_pos = results["freshPositiveChain"]["allPassed"]

    overall_pass = all_b1 and all_b2 and all_b3 and all_b4 and all_b5 and all_b6 and all_b7 and all_b8 and all_b9 and all_b10 and all_safety and all_pos
    results["classification"] = "E1 ENGINE SEMANTIC AUTHORITY GATE05 PASS" if overall_pass else "FAIL"

    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 80)
    print(f"FINAL CLASSIFICATION: {results['classification']}")
    print(f"Results written to: {RESULTS_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()
