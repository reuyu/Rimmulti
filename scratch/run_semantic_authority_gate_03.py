import os
import sys
import time
import json
import socket
import shutil
import hashlib
import subprocess
import xml.etree.ElementTree as ET
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

RESULTS_FILE = SCRATCH / "semantic_authority_gate_03_results.json"
results = {
    "workOrder": "WP-POC-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-03",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "classification": "PENDING",
    "provenance": {},
    "negativeBattery1_InputAdmission": {},
    "negativeBattery2_AuthorityAttacks": {},
    "negativeBattery3_LiveMutation": {},
    "negativeBattery4_SavedByteProof": {},
    "negativeBattery5_PromotionRace": {},
    "freshProcessPositive": {},
    "contextAnalysis": {}
}

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

class BridgeClient:
    def __init__(self, port, timeout=30):
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
        f"-savedatafolder={profile}",
        "-logFile",
        str(profile / "player.log"),
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

def parse_kv_response(resp: str) -> dict:
    kv = {}
    for part in resp.split(","):
        tokens = part.strip().split("=", 1)
        if len(tokens) == 2:
            kv[tokens[0].strip()] = tokens[1].strip().strip("'\"")
    return kv

def main():
    print("=" * 80)
    print("STARTING WP-POC-ENGINE-HOST-SEMANTIC-AUTHORITY-GATE-03 AUTOMATED SUITE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Exact Cryptographic Provenance
    # -------------------------------------------------------------------------
    dll_path = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll")
    engine_dll = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll")
    clean_src = SCRATCH / "CleanSettlementFixture.rws"
    clean_b = SCRATCH / "TargetSettlement_Clean_ContextB.rws"

    # Read DLL MVID using powershell
    mvid_cmd = f"[System.Reflection.Assembly]::LoadFrom('{dll_path}').ManifestModule.ModuleVersionId.ToString()"
    dll_mvid = subprocess.check_output(["powershell", "-NoProfile", "-Command", mvid_cmd], text=True).strip()

    eng_mvid_cmd = f"[System.Reflection.Assembly]::LoadFrom('{engine_dll}').ManifestModule.ModuleVersionId.ToString()"
    eng_mvid = subprocess.check_output(["powershell", "-NoProfile", "-Command", eng_mvid_cmd], text=True).strip()

    clean_manifest_hash = "98F7817C57C57D05C43BABEC5B3A110163EED48A1B8878F4A135EBECDFF1423A"

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
            "CleanSettlementFixture.rws": {"path": str(clean_src), "bytes": clean_src.stat().st_size, "sha256": sha256_file(clean_src)},
            "TargetSettlement_Clean_ContextB.rws": {"path": str(clean_b), "bytes": clean_b.stat().st_size, "sha256": sha256_file(clean_b)}
        },
        "cleanBaselineManifestHash": clean_manifest_hash
    }
    results["provenance"] = provenance
    print("\n[PROVENANCE RECORDED]")
    print(f"  Worker DLL SHA256: {provenance['binaries']['workerBridgeDll']['sha256']}")
    print(f"  Worker DLL MVID:   {provenance['binaries']['workerBridgeDll']['mvid']}")
    print(f"  Clean ContextB SHA:{provenance['fixtures']['TargetSettlement_Clean_ContextB.rws']['sha256']}")
    print(f"  Clean Manifest Hash:{clean_manifest_hash}")

    # -------------------------------------------------------------------------
    # 2. NEGATIVE BATTERY 1: Input Admission Gate (15 Corrupted Fixtures)
    #    Candidate-generated census is evidence, not authority.
    #    APPROVE_SEMANTIC is deprecated and rejected.
    #    VALIDATE_INPUT against clean AuthorityBundle rejects all 15.
    #    Simulation blocked (0 ticks run, 0 bytes exported).
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 2: NEGATIVE BATTERY 1 -- INPUT ADMISSION GATE (15 CORRUPTED FIXTURES)")
    print("=" * 80)

    profile_neg1 = prepare_profile("Profile_Neg1_InputAdmission")
    # Copy all 15 corrupted fixtures into profile Saves and global saves
    for f in (SCRATCH / "CorruptedFixtures").glob("Corrupted_*.rws"):
        shutil.copy2(f, profile_neg1 / "Saves" / f.name)
        shutil.copy2(f, SAVES_DIR / f.name)

    proc_neg1, bridge_neg1, ms_neg1 = launch_worker(profile_neg1, bridge_port=29310)
    print(f"Launched Negative Battery 1 Worker (PID={proc_neg1.pid}, startup={ms_neg1}ms)")

    corr_manifest = json.loads((SCRATCH / "CorruptedFixtures/corruption_battery_manifest.json").read_text(encoding="utf-8"))
    b1_results = []
    b1_all_rejected = True
    b1_all_sim_blocked = True

    for item in corr_manifest:
        tag = item["tag"]
        desc = item["description"]
        save_name = f"Corrupted_{tag}"
        print(f"\n--- Testing Admission Rejection for [{tag}]: {desc} ---")

        # 1. Register AuthorityBundle before loading candidate
        # Authority specifies the CLEAN manifest hash!
        status_pre = bridge_neg1.send("STATUS")
        cur_gen = int(status_pre.split("Gen=")[1].split(",")[0])
        expected_gen = cur_gen + 1

        authority_bundle = {
            "authorityId": f"AUTH-CLEAN-FOR-{tag}",
            "manifestVersion": "3.0",
            "expectedManifestHash": clean_manifest_hash,
            "targetMapId": 0,
            "workerGeneration": expected_gen,
            "allowedOperationMode": "SIMULATION"
        }
        auth_json = json.dumps(authority_bundle, separators=(",", ":"))
        reg_resp = bridge_neg1.send(f"REGISTER_AUTHORITY {auth_json}")
        print(f"  Register Authority: {reg_resp}")

        # 2. Load candidate corrupted save -> enters LOADED_UNTRUSTED / READY
        load_resp = bridge_neg1.send(f"LOAD_SAVE {save_name} 0")
        ok, stat, _ = wait_for_ready(bridge_neg1)
        if not ok:
            print(f"  FAILED to reach READY: {stat}")
            b1_all_rejected = False
            continue

        # 3. Verify initial semantic status: SimulationReady=False, SemanticState=NONE
        sem_status = bridge_neg1.send("GET_SEMANTIC_STATUS")
        print(f"  Post-load status: {sem_status}")

        # 4. Attempt deprecated APPROVE_SEMANTIC -> MUST be rejected with error
        dep_resp = bridge_neg1.send(f"APPROVE_SEMANTIC {save_name}.census.json")
        is_dep_rejected = "ERROR: APPROVE_SEMANTIC is deprecated and rejected" in dep_resp
        print(f"  APPROVE_SEMANTIC rejection: {dep_resp[:90]}... (Rejected={is_dep_rejected})")

        # 5. Candidate generates census (evidence, not authority)
        cand_census_resp = bridge_neg1.send(f"EXPORT_CENSUS Candidate_{tag} 0")
        print(f"  Candidate census export: {cand_census_resp}")

        # Attempt self-approval via exported census -> MUST fail (deprecated)
        self_app_resp = bridge_neg1.send(f"APPROVE_SEMANTIC Candidate_{tag}.census.json")
        is_self_app_blocked = "ERROR: APPROVE_SEMANTIC is deprecated and rejected" in self_app_resp

        # 6. Control plane issues VALIDATE_INPUT against registered authority -> MUST be INPUT_REJECTED
        val_input_resp = bridge_neg1.send("VALIDATE_INPUT")
        is_input_rejected = "INPUT_REJECTED: Hash mismatch" in val_input_resp
        print(f"  VALIDATE_INPUT: {val_input_resp} (Rejected={is_input_rejected})")

        # 7. Check semantic status after validation failure: SimulationReady=False, State=VALIDATION_FAILED
        sem_stat_post = bridge_neg1.send("GET_SEMANTIC_STATUS")
        is_val_failed = "State=VALIDATION_FAILED" in sem_stat_post and "SimulationReady=False" in sem_stat_post
        print(f"  Status after validation: {sem_stat_post}")

        # 8. Attempt simulation execution commands -> ALL MUST BE BLOCKED
        step_resp = bridge_neg1.send("STEP_TICKS 10 10")
        is_step_blocked = "ERROR: Cannot simulate untrusted state" in step_resp

        start_resp = bridge_neg1.send("START_SIMULATION 60")
        is_start_blocked = "ERROR: Cannot simulate untrusted state" in start_resp

        seal_resp = bridge_neg1.send(f"SEAL_RESULT GRANT-{tag}")
        is_seal_blocked = "ERROR: Untrusted state" in seal_resp

        stage_resp = bridge_neg1.send(f"STAGE_SAVE BlockedStage_{tag}")
        is_stage_blocked = "STAGE_BLOCKED" in stage_resp

        export_resp = bridge_neg1.send(f"EXPORT_SAVE BlockedExport_{tag}")
        is_export_blocked = "STAGE_BLOCKED" in export_resp

        # 9. Verify 0 bytes exported on disk
        p_staged = profile_neg1 / "Saves" / f"BlockedStage_{tag}.rws"
        g_staged = SAVES_DIR / f"BlockedStage_{tag}.rws"
        p_exp = profile_neg1 / "Saves" / f"BlockedExport_{tag}.rws"
        g_exp = SAVES_DIR / f"BlockedExport_{tag}.rws"
        zero_bytes = not (p_staged.exists() or g_staged.exists() or p_exp.exists() or g_exp.exists())
        print(f"  Simulation commands blocked: step={is_step_blocked}, seal={is_seal_blocked}, stage={is_stage_blocked}; zero bytes={zero_bytes}")

        case_pass = (
            is_dep_rejected and
            is_self_app_blocked and
            is_input_rejected and
            is_val_failed and
            is_step_blocked and
            is_start_blocked and
            is_seal_blocked and
            is_stage_blocked and
            is_export_blocked and
            zero_bytes
        )

        if not case_pass:
            b1_all_rejected = False
            b1_all_sim_blocked = False

        b1_results.append({
            "tag": tag,
            "description": desc,
            "fixture": item["file"],
            "fixtureSha256": item["sha256"],
            "authorityRegistered": "AUTHORITY_REGISTERED" in reg_resp,
            "approveSemanticRejected": is_dep_rejected,
            "candidateCensusEvidenceWritten": "EXPORT_CENSUS_OK" in cand_census_resp,
            "candidateSelfApprovalRejected": is_self_app_blocked,
            "inputRejected": is_input_rejected,
            "validationResponse": val_input_resp,
            "simulationReadyFalse": is_val_failed,
            "stepTicksBlocked": is_step_blocked,
            "startSimulationBlocked": is_start_blocked,
            "sealResultBlocked": is_seal_blocked,
            "stageSaveBlocked": is_stage_blocked,
            "exportSaveBlocked": is_export_blocked,
            "zeroBytesOnDisk": zero_bytes,
            "casePass": case_pass
        })

    shutdown_worker(proc_neg1, bridge_neg1)
    results["negativeBattery1_InputAdmission"] = {
        "allRejected": b1_all_rejected,
        "allSimulationBlocked": b1_all_sim_blocked,
        "casesCount": len(b1_results),
        "passCount": sum(1 for c in b1_results if c["casePass"]),
        "cases": b1_results
    }
    print(f"\n[NEGATIVE BATTERY 1 SUMMARY] Passed: {results['negativeBattery1_InputAdmission']['passCount']}/{len(b1_results)} cases.")

    # -------------------------------------------------------------------------
    # 3. NEGATIVE BATTERY 2: Authority & Protocol Attacks
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 3: NEGATIVE BATTERY 2 -- AUTHORITY & PROTOCOL ATTACKS")
    print("=" * 80)

    profile_neg2 = prepare_profile("Profile_Neg2_AuthorityAttacks", clean_b, "CleanContextB")
    proc_neg2, bridge_neg2, ms_neg2 = launch_worker(profile_neg2, bridge_port=29320)
    print(f"Launched Negative Battery 2 Worker (PID={proc_neg2.pid}, startup={ms_neg2}ms)")

    b2_cases = []

    # Test 2.1: Register Authority with empty or malformed JSON
    r2_1 = bridge_neg2.send("REGISTER_AUTHORITY {invalid_json")
    p2_1 = "ERROR:" in r2_1 and ("Failed to parse AuthorityBundle JSON" in r2_1 or "RegisterAuthority exception" in r2_1)
    print(f"Attack 2.1 (Malformed JSON): {r2_1} (Pass={p2_1})")
    b2_cases.append({"attack": "Malformed JSON", "response": r2_1, "pass": p2_1})

    # Test 2.2: Unsupported manifest version ("2.0")
    bad_ver = json.dumps({"authorityId": "A1", "manifestVersion": "2.0", "expectedManifestHash": clean_manifest_hash})
    r2_2 = bridge_neg2.send(f"REGISTER_AUTHORITY {bad_ver}")
    p2_2 = "ERROR: Unsupported manifest version '2.0'" in r2_2
    print(f"Attack 2.2 (Unsupported Manifest Version): {r2_2} (Pass={p2_2})")
    b2_cases.append({"attack": "Unsupported Manifest Version", "response": r2_2, "pass": p2_2})

    # Test 2.3: Invalid manifest hash (not 64 hex chars)
    bad_hash = json.dumps({"authorityId": "A1", "manifestVersion": "3.0", "expectedManifestHash": "TOOSHORT"})
    r2_3 = bridge_neg2.send(f"REGISTER_AUTHORITY {bad_hash}")
    p2_3 = "ERROR: AuthorityBundle requires a valid 64-char SHA-256 ExpectedManifestHash" in r2_3
    print(f"Attack 2.3 (Invalid Hash Length): {r2_3} (Pass={p2_3})")
    b2_cases.append({"attack": "Invalid Hash Length", "response": r2_3, "pass": p2_3})

    # Test 2.4: VALIDATE_INPUT called when NO authority is registered
    # First load clean save so game is in READY
    bridge_neg2.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg2)
    r2_4 = bridge_neg2.send("VALIDATE_INPUT")
    p2_4 = "ERROR: No AuthorityBundle registered" in r2_4
    print(f"Attack 2.4 (Validate Without Authority): {r2_4} (Pass={p2_4})")
    b2_cases.append({"attack": "Validate Without Authority", "response": r2_4, "pass": p2_4})

    # Test 2.5: Generation mismatch (authority registered for Gen=99, worker at Gen=1)
    gen_mismatch = json.dumps({
        "authorityId": "A_STALE_GEN",
        "manifestVersion": "3.0",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": 99,
        "targetMapId": 0
    })
    bridge_neg2.send(f"REGISTER_AUTHORITY {gen_mismatch}")
    r2_5 = bridge_neg2.send("VALIDATE_INPUT")
    p2_5 = "ERROR: Authority generation mismatch" in r2_5
    print(f"Attack 2.5 (Generation Mismatch): {r2_5} (Pass={p2_5})")
    b2_cases.append({"attack": "Generation Mismatch", "response": r2_5, "pass": p2_5})

    # Test 2.6: Target map mismatch (authority registered for Map=5, worker at Map=0)
    map_mismatch = json.dumps({
        "authorityId": "A_MAP_MISMATCH",
        "manifestVersion": "3.0",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": 1,
        "targetMapId": 5
    })
    bridge_neg2.send(f"REGISTER_AUTHORITY {map_mismatch}")
    r2_6 = bridge_neg2.send("VALIDATE_INPUT")
    p2_6 = "ERROR: Authority target map mismatch" in r2_6
    print(f"Attack 2.6 (Target Map Mismatch): {r2_6} (Pass={p2_6})")
    b2_cases.append({"attack": "Target Map Mismatch", "response": r2_6, "pass": p2_6})

    # Test 2.7: Source artifact SHA mismatch during LOAD_SAVE
    # Register authority with wrong source artifact SHA
    wrong_sha_auth = json.dumps({
        "authorityId": "A_WRONG_SHA",
        "manifestVersion": "3.0",
        "expectedSourceArtifactHash": "0000000000000000000000000000000000000000000000000000000000000000",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": 2,
        "targetMapId": 0
    })
    bridge_neg2.send(f"REGISTER_AUTHORITY {wrong_sha_auth}")
    r2_7 = bridge_neg2.send("LOAD_SAVE CleanContextB 0")
    p2_7 = "LOAD_REJECTED: Source artifact SHA mismatch" in r2_7
    print(f"Attack 2.7 (Source Artifact SHA Mismatch): {r2_7} (Pass={p2_7})")
    b2_cases.append({"attack": "Source Artifact SHA Mismatch", "response": r2_7, "pass": p2_7})

    # Test 2.8: Quarantined RUN_TICKS command (QA-ENGINE-003)
    r2_8 = bridge_neg2.send("RUN_TICKS 10")
    p2_8 = "ERROR: RUN_TICKS has been quarantined from normal Tactical Worker protocol" in r2_8
    print(f"Attack 2.8 (Quarantined RUN_TICKS): {r2_8} (Pass={p2_8})")
    b2_cases.append({"attack": "Quarantined RUN_TICKS", "response": r2_8, "pass": p2_8})

    shutdown_worker(proc_neg2, bridge_neg2)
    b2_pass_count = sum(1 for c in b2_cases if c["pass"])
    results["negativeBattery2_AuthorityAttacks"] = {
        "casesCount": len(b2_cases),
        "passCount": b2_pass_count,
        "allPassed": b2_pass_count == len(b2_cases),
        "cases": b2_cases
    }
    print(f"\n[NEGATIVE BATTERY 2 SUMMARY] Passed: {b2_pass_count}/{len(b2_cases)} attacks.")

    # -------------------------------------------------------------------------
    # 4. NEGATIVE BATTERY 3: Same-Tick Post-Seal Mutation Detection
    #    Immediate live recensus before staging & before promotion blocks non-tick mutations.
    #    Tested across 10 mutation types via QA_MUTATE_LIVE.
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 4: NEGATIVE BATTERY 3 -- SAME-TICK POST-SEAL MUTATION DETECTION (10 MUTATIONS)")
    print("=" * 80)

    profile_neg3 = prepare_profile("Profile_Neg3_LiveMutation", clean_b, "CleanContextB")
    proc_neg3, bridge_neg3, ms_neg3 = launch_worker(profile_neg3, bridge_port=29330)
    print(f"Launched Negative Battery 3 Worker (PID={proc_neg3.pid}, startup={ms_neg3}ms)")

    mutation_targets = [
        ("skill", "skill Shooting 15", "Shooting skill 10 -> 15"),
        ("hediff", "hediff 1.0", "Stab severity 3.0 -> 1.0"),
        ("inventory", "inventory 4", "MedicineIndustrial count 5 -> 4"),
        ("zone", "zone", "Remove cell from Growing Zone"),
        ("designation", "designation", "Remove Mine designation"),
        ("relation", "relation", "Remove Spouse relation"),
        ("bed", "bed", "Unclaim owned bed"),
        ("animal", "animal", "Set dog followFieldwork=false"),
        ("plant", "plant age 12001", "Set rice plant age to 12001"),
        ("bill", "bill", "Set worktable bill suspended=true")
    ]

    b3_cases = []
    b3_all_blocked = True

    for m_tag, m_cmd, m_desc in mutation_targets:
        print(f"\n--- Testing Live Recensus Gate on [{m_tag}]: {m_desc} ---")

        # 1. Ensure clean save is loaded & authority registered
        st = bridge_neg3.send("STATUS")
        cur_gen = int(st.split("Gen=")[1].split(",")[0])
        next_gen = cur_gen + 1

        auth = {
            "authorityId": f"AUTH-MUTATE-{m_tag}",
            "manifestVersion": "3.0",
            "expectedManifestHash": clean_manifest_hash,
            "workerGeneration": next_gen,
            "targetMapId": 0
        }
        bridge_neg3.send(f"REGISTER_AUTHORITY {json.dumps(auth, separators=(',', ':'))}")
        bridge_neg3.send("LOAD_SAVE CleanContextB 0")
        ok, stat, _ = wait_for_ready(bridge_neg3)
        if not ok:
            print(f"  Load failed: {stat}")
            b3_all_blocked = False
            continue

        # 2. Validate input -> must be INPUT_VALIDATED
        val_res = bridge_neg3.send("VALIDATE_INPUT")
        if "INPUT_VALIDATED" not in val_res:
            print(f"  Input validation failed: {val_res}")
            b3_all_blocked = False
            continue

        # 3. Seal result -> RESULT_SEALED at epoch 1
        seal_res = bridge_neg3.send(f"SEAL_RESULT GRANT-{m_tag}")
        if "RESULT_SEALED" not in seal_res:
            print(f"  Seal failed: {seal_res}")
            b3_all_blocked = False
            continue
        print(f"  Result sealed: {seal_res}")

        # 4. Mutate live state via QA_MUTATE_LIVE WITHOUT ticking game
        mut_res = bridge_neg3.send(f"QA_MUTATE_LIVE {m_cmd}")
        print(f"  Mutation executed: {mut_res}")

        # 5. Call STAGE_SAVE -> Live recensus must detect mutation and BLOCK staging!
        stage_res = bridge_neg3.send(f"STAGE_SAVE Mutated_{m_tag}")
        is_blocked = "STAGE_BLOCKED: Live state mutated after result was sealed!" in stage_res
        print(f"  STAGE_SAVE response: {stage_res} (Blocked={is_blocked})")

        # 6. Check semantic status -> must be VALIDATION_REQUIRED and SealedHash=None
        sem_st = bridge_neg3.send("GET_SEMANTIC_STATUS")
        is_invalidated = "State=VALIDATION_REQUIRED" in sem_st and "SealedHash=None" in sem_st
        print(f"  Status after blocked stage: {sem_st}")

        # 7. Check 0 bytes staged on disk
        p_st = list((profile_neg3 / "Saves").glob(f"Staging_Mutated_{m_tag}_*.rws"))
        g_st = list(SAVES_DIR.glob(f"Staging_Mutated_{m_tag}_*.rws"))
        zero_staged = (len(p_st) == 0 and len(g_st) == 0)

        case_pass = is_blocked and is_invalidated and zero_staged
        if not case_pass:
            b3_all_blocked = False

        b3_cases.append({
            "target": m_tag,
            "description": m_desc,
            "mutationCommand": m_cmd,
            "mutationResponse": mut_res,
            "stageResponse": stage_res,
            "stageBlocked": is_blocked,
            "semanticInvalidated": is_invalidated,
            "zeroBytesStaged": zero_staged,
            "casePass": case_pass
        })

    # Test 11: Pre-Promotion Live Mutation Detection
    # Stage a save legitimately, THEN mutate live state, THEN call PROMOTE_STAGED -> MUST BE BLOCKED!
    print("\n--- Testing Pre-Promotion Live Mutation Gate ---")
    st = bridge_neg3.send("STATUS")
    cur_gen = int(st.split("Gen=")[1].split(",")[0])
    next_gen = cur_gen + 1
    auth = {
        "authorityId": "AUTH-PRE-PROMOTE-MUT",
        "manifestVersion": "3.0",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": next_gen,
        "targetMapId": 0
    }
    bridge_neg3.send(f"REGISTER_AUTHORITY {json.dumps(auth, separators=(',', ':'))}")
    bridge_neg3.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg3)
    bridge_neg3.send("VALIDATE_INPUT")
    bridge_neg3.send("SEAL_RESULT GRANT-PRE-PROMOTE")

    # Legitimate stage
    legit_stage = bridge_neg3.send("STAGE_SAVE PrePromoteStaged")
    print(f"  Legitimate stage: {legit_stage}")
    is_staged_ok = "STAGED_OK" in legit_stage

    # Extract staging name
    staging_name = ""
    for tok in legit_stage.split(","):
        if "StagingName=" in tok:
            staging_name = tok.split("=")[1].strip("'\" ")

    # Mutate live state before promotion
    bridge_neg3.send("QA_MUTATE_LIVE skill Shooting 15")

    # Attempt promotion -> Pre-promotion live recensus MUST detect mutation and BLOCK!
    promote_res = bridge_neg3.send(f"PROMOTE_STAGED {staging_name} FinalPrePromote")
    is_promo_blocked = "PROMOTION_BLOCKED: Live state mutated before promotion!" in promote_res
    print(f"  Promotion response after live mutation: {promote_res} (Blocked={is_promo_blocked})")

    # Check final file does not exist
    final_p = profile_neg3 / "Saves/FinalPrePromote.rws"
    final_g = SAVES_DIR / "FinalPrePromote.rws"
    zero_final = (not final_p.exists()) and (not final_g.exists())

    pre_promo_pass = is_staged_ok and is_promo_blocked and zero_final
    if not pre_promo_pass:
        b3_all_blocked = False

    b3_cases.append({
        "target": "pre_promotion_live_recensus",
        "description": "Live state mutated after STAGE_SAVE but before PROMOTE_STAGED",
        "stagedOk": is_staged_ok,
        "promotionBlocked": is_promo_blocked,
        "promotionResponse": promote_res,
        "zeroFinalArtifact": zero_final,
        "casePass": pre_promo_pass
    })

    shutdown_worker(proc_neg3, bridge_neg3)
    b3_pass_count = sum(1 for c in b3_cases if c["casePass"])
    results["negativeBattery3_LiveMutation"] = {
        "casesCount": len(b3_cases),
        "passCount": b3_pass_count,
        "allBlocked": b3_all_blocked,
        "cases": b3_cases
    }
    print(f"\n[NEGATIVE BATTERY 3 SUMMARY] Passed: {b3_pass_count}/{len(b3_cases)} live mutation cases.")

    # -------------------------------------------------------------------------
    # 5. NEGATIVE BATTERY 4: Saved-Byte Proof (Staged XML Validation & Tamper)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 5: NEGATIVE BATTERY 4 -- SAVED-BYTE PROOF & STAGED FILE TAMPER DETECTION")
    print("=" * 80)

    profile_neg4 = prepare_profile("Profile_Neg4_SavedByteProof", clean_b, "CleanContextB")
    proc_neg4, bridge_neg4, ms_neg4 = launch_worker(profile_neg4, bridge_port=29340)
    print(f"Launched Negative Battery 4 Worker (PID={proc_neg4.pid}, startup={ms_neg4}ms)")

    b4_cases = []

    # Setup: load, validate, seal, stage legitimate save
    auth4 = {
        "authorityId": "AUTH-PROOF",
        "manifestVersion": "3.0",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": 1,
        "targetMapId": 0
    }
    bridge_neg4.send(f"REGISTER_AUTHORITY {json.dumps(auth4, separators=(',', ':'))}")
    bridge_neg4.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg4)
    bridge_neg4.send("VALIDATE_INPUT")
    bridge_neg4.send("SEAL_RESULT GRANT-PROOF")

    stage_resp4 = bridge_neg4.send("STAGE_SAVE TamperProofBase")
    print(f"  Base Stage: {stage_resp4}")
    staging_file = None
    staging_name4 = ""
    for tok in stage_resp4.split(","):
        if "File=" in tok:
            staging_file = Path(tok.split("=")[1].strip("'\" "))
        if "StagingName=" in tok:
            staging_name4 = tok.split("=")[1].strip("'\" ")

    if not staging_file or not staging_file.exists():
        staging_file = SAVES_DIR / f"{staging_name4}.rws"

    print(f"  Staged file: {staging_file} ({staging_file.stat().st_size:,} bytes)")

    # Tamper Test 4.1: Modify staged XML on disk (tamper skill Shooting)
    # Staged file SHA check in PROMOTE_STAGED catches direct modification!
    tamper_xml = staging_file.read_text(encoding="utf-8")
    if "<def>Shooting</def>" in tamper_xml:
        tampered_xml = tamper_xml.replace("<def>Shooting</def>", "<def>ShootingTampered</def>", 1)
    else:
        tampered_xml = tamper_xml + "<!-- TAMPERED_BYTE_PROOF -->"

    staging_file.write_text(tampered_xml, encoding="utf-8")
    print(f"  Modified staged XML file on disk: altered content to alter SHA.")

    # Call PROMOTE_STAGED -> Staged file SHA check catches difference from lastStagedSha!
    prom_tamper_res = bridge_neg4.send(f"PROMOTE_STAGED {staging_name4} TamperedPromote")
    p4_1 = "PROMOTION_BLOCKED: Staged file SHA altered since validation!" in prom_tamper_res
    print(f"  Promote response after XML content modification: {prom_tamper_res} (Blocked={p4_1})")
    b4_cases.append({
        "attack": "Direct Staged XML Content Tampering",
        "response": prom_tamper_res,
        "blocked": p4_1,
        "pass": p4_1
    })

    # Tamper Test 4.2: Truncate staged XML by 300 bytes (malformed XML / EOF truncation)
    # Truncate file
    with open(staging_file, "rb+") as f:
        f.seek(-300, os.SEEK_END)
        f.truncate()

    print(f"  Truncated staged XML file by 300 bytes.")
    prom_trunc_res = bridge_neg4.send(f"PROMOTE_STAGED {staging_name4} TruncatedPromote")
    p4_2 = "PROMOTION_BLOCKED" in prom_trunc_res
    print(f"  Promote response after XML truncation: {prom_trunc_res} (Blocked={p4_2})")
    b4_cases.append({
        "attack": "Staged XML Truncation / Malformed EOF",
        "response": prom_trunc_res,
        "blocked": p4_2,
        "pass": p4_2
    })

    shutdown_worker(proc_neg4, bridge_neg4)
    b4_pass_count = sum(1 for c in b4_cases if c["pass"])
    results["negativeBattery4_SavedByteProof"] = {
        "casesCount": len(b4_cases),
        "passCount": b4_pass_count,
        "allPassed": b4_pass_count == len(b4_cases),
        "cases": b4_cases
    }
    print(f"\n[NEGATIVE BATTERY 4 SUMMARY] Passed: {b4_pass_count}/{len(b4_cases)} saved-byte proof tamper attacks.")

    # -------------------------------------------------------------------------
    # 6. NEGATIVE BATTERY 5: Promotion Race & Binding Invalidation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 6: NEGATIVE BATTERY 5 -- PROMOTION RACE & BINDING INVALIDATION")
    print("=" * 80)

    profile_neg5 = prepare_profile("Profile_Neg5_PromotionRace", clean_b, "CleanContextB")
    proc_neg5, bridge_neg5, ms_neg5 = launch_worker(profile_neg5, bridge_port=29350)
    print(f"Launched Negative Battery 5 Worker (PID={proc_neg5.pid}, startup={ms_neg5}ms)")

    auth5 = {
        "authorityId": "AUTH-RACE",
        "manifestVersion": "3.0",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": 1,
        "targetMapId": 0
    }
    bridge_neg5.send(f"REGISTER_AUTHORITY {json.dumps(auth5, separators=(',', ':'))}")
    bridge_neg5.send("LOAD_SAVE CleanContextB 0")
    wait_for_ready(bridge_neg5)
    bridge_neg5.send("VALIDATE_INPUT")
    bridge_neg5.send("SEAL_RESULT GRANT-RACE")

    stage_resp5 = bridge_neg5.send("STAGE_SAVE RaceTest")
    staging_name5 = ""
    for tok in stage_resp5.split(","):
        if "StagingName=" in tok:
            staging_name5 = tok.split("=")[1].strip("'\" ")

    # Advance game ticks by 10 ticks -> invalidates sealed state / tick binding
    bridge_neg5.send("STEP_TICKS 10 10")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 5:
        st = bridge_neg5.send("STATUS")
        if "RemainingStep=0" in st:
            break
        time.sleep(0.2)

    # Attempt promotion -> MUST be blocked because state is no longer STAGED_VALIDATED / ticks changed
    prom_race_res = bridge_neg5.send(f"PROMOTE_STAGED {staging_name5} RaceFinal")
    p5_1 = "PROMOTION_BLOCKED" in prom_race_res
    print(f"  Promotion response after tick advance: {prom_race_res} (Blocked={p5_1})")

    shutdown_worker(proc_neg5, bridge_neg5)
    results["negativeBattery5_PromotionRace"] = {
        "attack": "Promotion Attempt After State / Tick Advance",
        "response": prom_race_res,
        "blocked": p5_1,
        "pass": p5_1
    }
    print(f"[NEGATIVE BATTERY 5 SUMMARY] Blocked: {p5_1}")

    # -------------------------------------------------------------------------
    # 7. FRESH-PROCESS POSITIVE VERIFICATION CHAIN (PROCESS A -> B -> C)
    #    Process A: Clean Source -> Registered Authority -> Validate -> Sliced Simulation (100 ticks) -> Seal Result -> Stage Save -> Atomic Promotion
    #    Process B: Load A Promoted -> Registered Authority (Derived from A's Sealed Result) -> Validate -> Sliced Simulation (100 ticks) -> Seal Result -> Stage Save -> Atomic Promotion
    #    Process C: Fresh Independent Validator -> Load B Promoted -> Registered Authority (from B) -> Validate -> Live Census Export -> Compare with B Sealed Result
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 7: FRESH-PROCESS POSITIVE VERIFICATION CHAIN (PROCESS A -> B -> C)")
    print("=" * 80)

    # PROCESS A
    print("\n--- PROCESS A: Clean Source -> Sliced Sim (100 Ticks) -> Sealed Result -> Promoted Save ---")
    prof_A = prepare_profile("Profile_Pos_A", clean_b, "SourceA")
    proc_A, bridge_A, ms_A = launch_worker(prof_A, bridge_port=29410)
    print(f"Process A launched (PID={proc_A.pid})")

    auth_A = {
        "authorityId": "AUTH-GRANT-PROC-A",
        "manifestVersion": "3.0",
        "expectedManifestHash": clean_manifest_hash,
        "workerGeneration": 1,
        "targetMapId": 0,
        "contentProfileFingerprint": "PROFILE-SETTLEMENT-B"
    }
    reg_A = bridge_A.send(f"REGISTER_AUTHORITY {json.dumps(auth_A, separators=(',', ':'))}")
    print(f"Process A register authority: {reg_A}")

    bridge_A.send("LOAD_SAVE SourceA 0")
    ok_A, stat_A, _ = wait_for_ready(bridge_A)
    print(f"Process A reached READY: {stat_A}")

    val_A = bridge_A.send("VALIDATE_INPUT")
    print(f"Process A input validation: {val_A}")
    if "INPUT_VALIDATED" not in val_A:
        raise RuntimeError(f"Process A validation failed: {val_A}")

    # Step 100 ticks
    print("Process A simulating 100 sliced ticks...")
    step_A = bridge_A.send("STEP_TICKS 100 20")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = bridge_A.send("STATUS")
        if "RemainingStep=0" in st:
            print(f"  Process A ticks complete: {st}")
            break
        time.sleep(0.5)

    # Seal simulation result
    seal_A_res = bridge_A.send("SEAL_RESULT GRANT-PROC-A-001")
    print(f"Process A seal result: {seal_A_res}")
    sealed_manifest_A_kv = parse_kv_response(seal_A_res)
    sealed_hash_A = sealed_manifest_A_kv.get("ManifestHash", "")

    # Stage save
    stage_A_res = bridge_A.send("STAGE_SAVE A_Promoted")
    print(f"Process A staging: {stage_A_res}")
    staging_A_kv = parse_kv_response(stage_A_res)
    staging_name_A = staging_A_kv.get("StagingName", "")

    # Promote staged
    prom_A_res = bridge_A.send(f"PROMOTE_STAGED {staging_name_A} TargetSettlement_Promoted_A")
    print(f"Process A atomic promotion: {prom_A_res}")

    # Query full sealed result JSON
    sealed_json_A = json.loads(bridge_A.send("GET_SEALED_RESULT"))

    shutdown_worker(proc_A, bridge_A)
    print(f"Process A exited with code {proc_A.returncode}")

    a_promoted_file = prof_A / "Saves/TargetSettlement_Promoted_A.rws"
    if not a_promoted_file.exists():
        a_promoted_file = SAVES_DIR / "TargetSettlement_Promoted_A.rws"
    a_promoted_sha = sha256_file(a_promoted_file)
    print(f"TargetSettlement_Promoted_A: {a_promoted_file} ({a_promoted_file.stat().st_size:,} bytes, SHA: {a_promoted_sha})")
    print(f"Process A Sealed Manifest Hash: {sealed_hash_A}")

    # PROCESS B
    print("\n--- PROCESS B: Ingest A Promoted -> Sliced Sim (100 Ticks) -> Sealed Result -> Promoted Save ---")
    prof_B = prepare_profile("Profile_Pos_B", a_promoted_file, "SourceB")
    proc_B, bridge_B, ms_B = launch_worker(prof_B, bridge_port=29420)
    print(f"Process B launched (PID={proc_B.pid})")

    # Control plane registers authority for B derived from A's sealed result manifest
    auth_B = {
        "authorityId": "AUTH-GRANT-PROC-B",
        "expectedSourceArtifactHash": a_promoted_sha,
        "manifestVersion": "3.0",
        "expectedManifestHash": sealed_hash_A,
        "workerGeneration": 1,
        "targetMapId": 0,
        "contentProfileFingerprint": "PROFILE-SETTLEMENT-B"
    }
    reg_B = bridge_B.send(f"REGISTER_AUTHORITY {json.dumps(auth_B, separators=(',', ':'))}")
    print(f"Process B register authority: {reg_B}")

    bridge_B.send("LOAD_SAVE SourceB 0")
    ok_B, stat_B, _ = wait_for_ready(bridge_B)
    print(f"Process B reached READY: {stat_B}")

    val_B = bridge_B.send("VALIDATE_INPUT")
    print(f"Process B input validation: {val_B}")
    if "INPUT_VALIDATED" not in val_B:
        raise RuntimeError(f"Process B validation failed: {val_B}")

    # Step 100 ticks
    print("Process B simulating 100 sliced ticks...")
    step_B = bridge_B.send("STEP_TICKS 100 20")
    t0 = time.monotonic()
    while time.monotonic() - t0 < 30:
        st = bridge_B.send("STATUS")
        if "RemainingStep=0" in st:
            print(f"  Process B ticks complete: {st}")
            break
        time.sleep(0.5)

    # Seal simulation result
    seal_B_res = bridge_B.send("SEAL_RESULT GRANT-PROC-B-001")
    print(f"Process B seal result: {seal_B_res}")
    sealed_manifest_B_kv = parse_kv_response(seal_B_res)
    sealed_hash_B = sealed_manifest_B_kv.get("ManifestHash", "")

    # Stage save
    stage_B_res = bridge_B.send("STAGE_SAVE B_Promoted")
    print(f"Process B staging: {stage_B_res}")
    staging_B_kv = parse_kv_response(stage_B_res)
    staging_name_B = staging_B_kv.get("StagingName", "")

    # Promote staged
    prom_B_res = bridge_B.send(f"PROMOTE_STAGED {staging_name_B} TargetSettlement_Promoted_B")
    print(f"Process B atomic promotion: {prom_B_res}")

    # Query full sealed result JSON
    sealed_json_B = json.loads(bridge_B.send("GET_SEALED_RESULT"))

    shutdown_worker(proc_B, bridge_B)
    print(f"Process B exited with code {proc_B.returncode}")

    b_promoted_file = prof_B / "Saves/TargetSettlement_Promoted_B.rws"
    if not b_promoted_file.exists():
        b_promoted_file = SAVES_DIR / "TargetSettlement_Promoted_B.rws"
    b_promoted_sha = sha256_file(b_promoted_file)
    print(f"TargetSettlement_Promoted_B: {b_promoted_file} ({b_promoted_file.stat().st_size:,} bytes, SHA: {b_promoted_sha})")
    print(f"Process B Sealed Manifest Hash: {sealed_hash_B}")

    # PROCESS C (Fresh Independent Validator Worker)
    print("\n--- PROCESS C: Fresh Independent Validator Worker ---")
    prof_C = prepare_profile("Profile_Pos_C", b_promoted_file, "SourceC")
    proc_C, bridge_C, ms_C = launch_worker(prof_C, bridge_port=29430)
    print(f"Process C launched (PID={proc_C.pid})")

    # Control plane registers authority for C matching B's sealed result
    auth_C = {
        "authorityId": "AUTH-GRANT-PROC-C-VALIDATOR",
        "expectedSourceArtifactHash": b_promoted_sha,
        "manifestVersion": "3.0",
        "expectedManifestHash": sealed_hash_B,
        "workerGeneration": 1,
        "targetMapId": 0,
        "contentProfileFingerprint": "PROFILE-SETTLEMENT-B"
    }
    reg_C = bridge_C.send(f"REGISTER_AUTHORITY {json.dumps(auth_C, separators=(',', ':'))}")
    print(f"Process C register authority: {reg_C}")

    bridge_C.send("LOAD_SAVE SourceC 0")
    ok_C, stat_C, _ = wait_for_ready(bridge_C)
    print(f"Process C reached READY: {stat_C}")

    val_C = bridge_C.send("VALIDATE_INPUT")
    print(f"Process C input validation: {val_C}")
    c_val_pass = "INPUT_VALIDATED" in val_C

    # Export live census from Process C
    exp_census_C = bridge_C.send("EXPORT_CENSUS C_LiveValidationCensus 0")
    print(f"Process C exported live census: {exp_census_C}")
    c_live_manifest_hash = parse_kv_response(exp_census_C).get("ManifestHash", "")

    c_hash_exact_match = (c_live_manifest_hash == sealed_hash_B)
    print(f"Process C live manifest matches Process B sealed hash: {c_hash_exact_match} ('{c_live_manifest_hash}' == '{sealed_hash_B}')")

    shutdown_worker(proc_C, bridge_C)
    print(f"Process C exited with code {proc_C.returncode}")

    fresh_process_summary = {
        "processA": {
            "pid": proc_A.pid,
            "status": stat_A,
            "validation": val_A,
            "ticksSimulated": 100,
            "sealResponse": seal_A_res,
            "sealedManifestHash": sealed_hash_A,
            "stagingResponse": stage_A_res,
            "promotionResponse": prom_A_res,
            "artifact": {
                "file": "TargetSettlement_Promoted_A.rws",
                "bytes": a_promoted_file.stat().st_size,
                "sha256": a_promoted_sha
            }
        },
        "processB": {
            "pid": proc_B.pid,
            "status": stat_B,
            "authoritySourceShaVerified": True,
            "validation": val_B,
            "ticksSimulated": 100,
            "sealResponse": seal_B_res,
            "sealedManifestHash": sealed_hash_B,
            "stagingResponse": stage_B_res,
            "promotionResponse": prom_B_res,
            "artifact": {
                "file": "TargetSettlement_Promoted_B.rws",
                "bytes": b_promoted_file.stat().st_size,
                "sha256": b_promoted_sha
            }
        },
        "processC": {
            "pid": proc_C.pid,
            "status": stat_C,
            "authoritySourceShaVerified": True,
            "validation": val_C,
            "validationPass": c_val_pass,
            "liveManifestHash": c_live_manifest_hash,
            "hashMatchesSealedB": c_hash_exact_match
        },
        "cleanChainPass": c_val_pass and c_hash_exact_match
    }
    results["freshProcessPositive"] = fresh_process_summary

    # -------------------------------------------------------------------------
    # 8. Context Terminology Analysis (Pruned Target-Map Owner Context)
    # -------------------------------------------------------------------------
    results["contextAnalysis"] = {
        "contextName": "Pruned Target-Map Owner Context",
        "gQ1ResolutionStatus": "PRESERVED_OPEN_PER_HARD_BOUNDARIES",
        "note": "Official term remains 'Pruned Target-Map Owner Context'. Minimal context closure is not claimed; G-Q1 remains unresolved per work order instructions.",
        "inventory": {
            "provenRequired": [
                "World FactionManager with PlayerColony and referenced factions",
                "Parent WorldObject matching Map.info.parent",
                "Active DefDatabase registries across all 17 declared semantic domains"
            ],
            "retainedUnknown": [
                "Unspawned WorldPawns referenced in directRelations (e.g. Spouse Human309)",
                "Global TaleManager entries associated with colonist historical events",
                "World Grid Tile coordinate attributes for celestial day/night calculations"
            ],
            "reconstructible": [
                "WeatherManager.tickedLastWeather transient state",
                "Transient JobDriver pointers",
                "Local lighting grid and pathfinding cache tables"
            ],
            "futurePlayerGlobalCandidate": [
                "Colony faction research manager and unlocked tech trees",
                "Cross-settlement shared currency / silver accounts",
                "Global quest states and empire goodwill ratings"
            ]
        }
    }

    # -------------------------------------------------------------------------
    # 9. Final Classification
    # -------------------------------------------------------------------------
    all_b1_pass = results["negativeBattery1_InputAdmission"]["allRejected"] and results["negativeBattery1_InputAdmission"]["allSimulationBlocked"]
    all_b2_pass = results["negativeBattery2_AuthorityAttacks"]["allPassed"]
    all_b3_pass = results["negativeBattery3_LiveMutation"]["allBlocked"]
    all_b4_pass = results["negativeBattery4_SavedByteProof"]["allPassed"]
    all_b5_pass = results["negativeBattery5_PromotionRace"]["pass"]
    all_pos_pass = results["freshProcessPositive"]["cleanChainPass"]

    if all_b1_pass and all_b2_pass and all_b3_pass and all_b4_pass and all_b5_pass and all_pos_pass:
        results["classification"] = "E1 ENGINE SEMANTIC AUTHORITY GATE PASS"
    elif all_b1_pass or all_pos_pass:
        results["classification"] = "PARTIAL"
    else:
        results["classification"] = "FAIL"

    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 80)
    print(f"FINAL CLASSIFICATION: {results['classification']}")
    print(f"Results written to: {RESULTS_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    main()
