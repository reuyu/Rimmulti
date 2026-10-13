import sys
import os
import pathlib
from pathlib import Path

WORKSPACE = pathlib.Path(r"c:\Users\user\Desktop\RimMulti")
sys.path.insert(0, str(WORKSPACE))
sys.path.insert(0, str(WORKSPACE / "scratch"))

import socket
import subprocess
import time
import json
import hashlib
import shutil
import xml.etree.ElementTree as ET

from census_oracle import CensusOracle

SCRATCH = pathlib.Path(r"C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch")
WORKSPACE = pathlib.Path(r"c:\Users\user\Desktop\RimMulti")
EXE = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")

RESULTS_FILE = WORKSPACE / "scratch/settlement_roundtrip_results.json"
results = {
    "workOrder": "WP-POC-ENGINE-HOST-SETTLEMENT-ROUNDTRIP-01",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "classification": "PENDING",
    "phases": {}
}

owned_processes = []

def record(phase, name, data):
    if phase not in results["phases"]:
        results["phases"][phase] = {}
    results["phases"][phase][name] = data
    RESULTS_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{phase}::{name}] {json.dumps(data, ensure_ascii=False)}", flush=True)

class BridgeClient:
    def __init__(self, port, timeout=30):
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
    profile = SCRATCH / name
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

    return profile

def launch_worker(profile, bridge_port=29600, probe_port=30600):
    args = [
        str(EXE),
        "-batchmode",
        f"-savedatafolder={profile}",
        "-logFile",
        str(profile / "player.log"),
        f"-bridgeport={bridge_port}",
        f"-qaport={probe_port}"
    ]
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = 0
    p = subprocess.Popen(args, startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW, cwd=str(SCRATCH))
    owned_processes.append(p)

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

def main():
    print("=" * 80)
    print("STARTING WORK ORDER SUITE: WP-POC-ENGINE-HOST-SETTLEMENT-ROUNDTRIP-01")
    print("=" * 80)

    baseline_census_path = WORKSPACE / "scratch/Census_Baseline.json"
    if not baseline_census_path.exists():
        print("Extracting baseline census...")
        base_fixture = WORKSPACE / "scratch/ComplexSettlementFixture.rws"
        c = CensusOracle.extract_from_xml(base_fixture)
        baseline_census_path.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")

    baseline_census = json.loads(baseline_census_path.read_text(encoding="utf-8"))

    # =========================================================================
    # PHASE 1: CONTEXT EVALUATION (Context A vs Context B)
    # =========================================================================
    print("\n>>> PHASE 1: Materialization Contexts Evaluation (Context A vs B)")

    # 1.1 Context A: Vanilla Multi-Map Context
    pA = prepare_profile("PoC_ContextA", WORKSPACE / "scratch/ComplexSettlementFixture.rws", "InputA")
    procA, bridgeA, msA = launch_worker(pA, 29710, 30710)
    record("Phase1_Contexts", "Launch_ContextA", {"pid": procA.pid, "startup_ms": msA})

    loadA = bridgeA.send("LOAD_SAVE InputA")
    okA, statA, _ = wait_for_ready(bridgeA)
    record("Phase1_Contexts", "Load_ContextA", {"response": loadA, "ok": okA, "status": statA})

    if okA:
        censusA_str = bridgeA.send("GET_CENSUS_JSON 0")
        try:
            censusA = json.loads(censusA_str)
            compA = CensusOracle.compare(baseline_census, censusA)
            record("Phase1_Contexts", "Census_Compare_ContextA", {"isPass": compA["isPass"], "errors": compA["errors"]})
        except Exception as ex:
            record("Phase1_Contexts", "Census_Compare_ContextA", {"isPass": False, "errors": [f"Failed to parse census JSON: {ex}, raw: {censusA_str[:200]}"]})

        # Step 50 ticks and observe multi-map behavior
        stepA = bridgeA.send("STEP_TICKS 50")
        probeA = bridgeA.send("PROBE_LOCAL_CLOCKS")
        record("Phase1_Contexts", "StepTicks_ContextA", {"stepResponse": stepA, "probeClocks": probeA})
    else:
        record("Phase1_Contexts", "Census_Compare_ContextA", {"isPass": False, "errors": [f"Load_ContextA failed to reach READY: {statA}"]})

    shutdown_worker(procA, bridgeA)

    # 1.2 Context B: Synthetic-Minimal Target-Only World Context
    pB = prepare_profile("PoC_ContextB", WORKSPACE / "scratch/TargetSettlement_ContextB.rws", "InputB")
    procB, bridgeB, msB = launch_worker(pB, 29720, 30720)
    record("Phase1_Contexts", "Launch_ContextB", {"pid": procB.pid, "startup_ms": msB})

    loadB = bridgeB.send("LOAD_SAVE InputB")
    okB, statB, _ = wait_for_ready(bridgeB)
    record("Phase1_Contexts", "Load_ContextB", {"response": loadB, "ok": okB, "status": statB})

    if okB:
        censusB_str = bridgeB.send("GET_CENSUS_JSON 0")
        try:
            censusB = json.loads(censusB_str)
            compB = CensusOracle.compare(baseline_census, censusB)
            record("Phase1_Contexts", "Census_Compare_ContextB", {"isPass": compB["isPass"], "errors": compB["errors"]})
        except Exception as ex:
            record("Phase1_Contexts", "Census_Compare_ContextB", {"isPass": False, "errors": [f"Failed to parse census JSON: {ex}, raw: {censusB_str[:200]}"]})

        # Step 50 ticks on Context B
        stepB = bridgeB.send("STEP_TICKS 50")
        probeB = bridgeB.send("PROBE_LOCAL_CLOCKS")
        record("Phase1_Contexts", "StepTicks_ContextB", {"stepResponse": stepB, "probeClocks": probeB})
    else:
        record("Phase1_Contexts", "Census_Compare_ContextB", {"isPass": False, "errors": [f"Load_ContextB failed to reach READY: {statB}"]})

    # Verify player.log for clean load in Context B
    pB_log = (pB / "player.log").read_text(encoding="utf-8", errors="replace")
    has_fatal_err = "Exception filling" in pB_log or "NullReferenceException" in pB_log
    record("Phase1_Contexts", "LogAudit_ContextB", {"clean": not has_fatal_err, "logSize": len(pB_log)})
    shutdown_worker(procB, bridgeB)

    # =========================================================================
    # PHASE 2: 10-STEP SETTLEMENT ROUND TRIP (Section 4)
    # =========================================================================
    print("\n>>> PHASE 2: 10-Step Settlement Round Trip")
    pRT = prepare_profile("PoC_RoundTrip", WORKSPACE / "scratch/TargetSettlement_ContextB.rws", "RT_Source")
    procRT, bridgeRT, msRT = launch_worker(pRT, 29730, 30730)
    record("Phase2_RoundTrip", "Launch_RoundTripWorker", {"pid": procRT.pid, "startup_ms": msRT})

    # Step 1: Load Source
    r1 = bridgeRT.send("LOAD_SAVE RT_Source")
    okRT1, statRT1, _ = wait_for_ready(bridgeRT)
    record("Phase2_RoundTrip", "Step1_LoadSource", {"response": r1, "ready": okRT1, "status": statRT1})

    # Step 2: Census Baseline
    c1_json = bridgeRT.send("GET_CENSUS_JSON 0")
    census_step2 = json.loads(c1_json)
    comp_step2 = CensusOracle.compare(baseline_census, census_step2)
    record("Phase2_RoundTrip", "Step2_CensusBaseline", {
        "entityCount": census_step2["entityCount"],
        "isPass": comp_step2["isPass"],
        "errors": comp_step2["errors"]
    })

    # Step 3: Extract Candidate Segment / Artifact
    r3 = bridgeRT.send("EXPORT_SAVE RT_Candidate_Artifact")
    candidate_save = pRT / "Saves/RT_Candidate_Artifact.rws"
    sha_cand = hashlib.sha256(candidate_save.read_bytes()).hexdigest().upper()
    record("Phase2_RoundTrip", "Step3_ExtractCandidate", {"response": r3, "sha256": sha_cand, "size": candidate_save.stat().st_size})

    # Step 4: Materialize Candidate in Fresh Context
    # Reload the exported save within the engine host
    r4 = bridgeRT.send("LOAD_SAVE RT_Candidate_Artifact")
    okRT4, statRT4, _ = wait_for_ready(bridgeRT)
    record("Phase2_RoundTrip", "Step4_MaterializeCandidate", {"response": r4, "ready": okRT4, "status": statRT4})

    # Step 5: Load-Ready Semantic Validation
    map_info = bridgeRT.send("GET_MAP_INFO")
    entity_summary = bridgeRT.send("GET_ENTITY_SUMMARY")
    has_strange = "Human302" in entity_summary
    has_boomrat = "Boomrat3383" in entity_summary or "Boomrat" in entity_summary
    record("Phase2_RoundTrip", "Step5_SemanticValidation", {
        "status": statRT4,
        "hasStrange": has_strange,
        "hasBoomrat": has_boomrat,
        "mapInfo": map_info.splitlines()[:3]
    })

    # Step 6: Census Compare
    c6_json = bridgeRT.send("GET_CENSUS_JSON 0")
    census_step6 = json.loads(c6_json)
    comp_step6 = CensusOracle.compare(census_step2, census_step6)
    record("Phase2_RoundTrip", "Step6_CensusCompare", {
        "isPass": comp_step6["isPass"],
        "totalErrors": comp_step6["totalErrors"],
        "errors": comp_step6["errors"]
    })

    # Step 7: Run Controlled Tick Window (100 ticks)
    r7 = bridgeRT.send("STEP_TICKS 100")
    record("Phase2_RoundTrip", "Step7_ControlledTickWindow", {"response": r7})

    # Step 8: Re-extract Post-Tick State & Census
    r8 = bridgeRT.send("EXPORT_SAVE RT_PostTick_Artifact")
    posttick_save = pRT / "Saves/RT_PostTick_Artifact.rws"
    sha_posttick = hashlib.sha256(posttick_save.read_bytes()).hexdigest().upper()
    c8_json = bridgeRT.send("GET_CENSUS_JSON 0")
    census_step8 = json.loads(c8_json)
    record("Phase2_RoundTrip", "Step8_ReExtractPostTick", {
        "response": r8,
        "sha256": sha_posttick,
        "size": posttick_save.stat().st_size,
        "postTickEntityCount": census_step8["entityCount"]
    })

    # Step 9: Rematerialize Again into Clean Context
    r9 = bridgeRT.send("LOAD_SAVE RT_PostTick_Artifact")
    okRT9, statRT9, _ = wait_for_ready(bridgeRT)
    record("Phase2_RoundTrip", "Step9_RematerializeAgain", {"response": r9, "ready": okRT9, "status": statRT9})

    # Step 10: Census & Reference Compare (Verify 100% Fidelity of Post-Tick State)
    c10_json = bridgeRT.send("GET_CENSUS_JSON 0")
    census_step10 = json.loads(c10_json)
    comp_step10 = CensusOracle.compare(census_step8, census_step10)
    record("Phase2_RoundTrip", "Step10_CensusReferenceCompare", {
        "isPass": comp_step10["isPass"],
        "totalErrors": comp_step10["totalErrors"],
        "errors": comp_step10["errors"]
    })
    shutdown_worker(procRT, bridgeRT)

    # =========================================================================
    # PHASE 3: DELIBERATE CORRUPTION ORACLE BATTERY (Section 5)
    # =========================================================================
    print("\n>>> PHASE 3: Deliberate Corruption Oracle Battery (6 Injected Faults)")
    corruptions = [
        ("Corrupt_1_MissingHeldItem", "Missing held item: dropped Medicine from Pawn inventory"),
        ("Corrupt_2_DuplicateEntityId", "Duplicate entity ID: injected duplicate Gun_Autopistol9001"),
        ("Corrupt_3_BrokenContainer", "Broken container: emptied MinifiedThing innerContainer"),
        ("Corrupt_4_MissingDef", "Missing Def: replaced TableSculpting with NonExistent_ArchotechPlasmaBench"),
        ("Corrupt_5_CorruptedAssignment", "Corrupted assignment: Strange ownedBed -> non-existent Thing_Bed9999"),
        ("Corrupt_6_OmittedGlobalState", "Omitted global dependency: removed Faction_10 from World FactionManager")
    ]

    corr_port = 29740
    for idx, (c_name, c_desc) in enumerate(corruptions, 1):
        c_rws = WORKSPACE / f"scratch/CorruptedFixtures/{c_name}.rws"
        pC = prepare_profile(f"PoC_{c_name}", c_rws, "CorruptInput")
        procC, bridgeC, _ = launch_worker(pC, corr_port + idx, 30740 + idx)

        # Attempt to load corrupted save into RimWorld engine
        r_load = bridgeC.send("LOAD_SAVE CorruptInput")
        time.sleep(3.0)
        status_c = bridgeC.send("STATUS")
        engine_ready = "STATE: READY" in status_c

        # Read player.log to check what engine logged
        log_text = (pC / "player.log").read_text(encoding="utf-8", errors="replace")
        has_error_in_log = "[Error]" in log_text or "Exception" in log_text or "Could not find" in log_text or "Error while loading" in log_text

        # Run Census Oracle against baseline census
        oracle_res = None
        if engine_ready:
            try:
                c_inengine = json.loads(bridgeC.send("GET_CENSUS_JSON 0"))
                oracle_res = CensusOracle.compare(baseline_census, c_inengine)
            except Exception as ex:
                oracle_res = {"isPass": False, "totalErrors": 1, "errors": [f"Exception fetching census: {ex}"]}
        else:
            # Engine failed to reach ready -> fail-closed by engine
            oracle_res = {"isPass": False, "totalErrors": 1, "errors": [f"Engine failed to reach READY: {status_c}"]}

        # Static XML comparison as backup check
        static_census = CensusOracle.extract_from_xml(c_rws)
        static_comp = CensusOracle.compare(baseline_census, static_census)

        record("Phase3_Corruptions", c_name, {
            "description": c_desc,
            "engineReachedReady": engine_ready,
            "engineStatus": status_c,
            "engineLoggedErrors": has_error_in_log,
            "oracleResult": {
                "detected": not oracle_res["isPass"],
                "totalErrors": oracle_res["totalErrors"],
                "sampleErrors": oracle_res["errors"][:3]
            },
            "staticOracleResult": {
                "detected": not static_comp["isPass"],
                "totalErrors": static_comp["totalErrors"],
                "sampleErrors": static_comp["errors"][:3]
            },
            "failClosedEnforced": (not oracle_res["isPass"]) or (not static_comp["isPass"])
        })
        shutdown_worker(procC, bridgeC)

    # =========================================================================
    # PHASE 4: LOCAL CLOCK / VANILLA-FIRST G-Q1 EVIDENCE (Section 6)
    # =========================================================================
    print("\n>>> PHASE 4: LocalClock / Vanilla-First G-Q1 Evidence")
    pClock = prepare_profile("PoC_ClockProbe", WORKSPACE / "scratch/ComplexSettlementFixture.rws", "ClockInput")
    procClock, bridgeClock, msClock = launch_worker(pClock, 29750, 30750)
    record("Phase4_LocalClock", "Launch_ClockWorker", {"pid": procClock.pid, "startup_ms": msClock})

    bridgeClock.send("LOAD_SAVE ClockInput")
    wait_for_ready(bridgeClock)

    # Probe 1: Initial Clock State across Map 0 and Map 1
    probe_initial = bridgeClock.send("PROBE_LOCAL_CLOCKS")
    record("Phase4_LocalClock", "Probe_Initial", {"output": probe_initial.splitlines()})

    # Step 100 ticks and probe again
    bridgeClock.send("STEP_TICKS 100")
    probe_after100 = bridgeClock.send("PROBE_LOCAL_CLOCKS")
    record("Phase4_LocalClock", "Probe_After100Ticks", {"output": probe_after100.splitlines()})

    # Probe map switching contamination
    # Switch target map to Map 1, step ticks, switch back to Map 0
    bridgeClock.send("SET_TARGET_MAP 1")
    bridgeClock.send("STEP_TICKS 50")
    probe_switch1 = bridgeClock.send("PROBE_LOCAL_CLOCKS")

    bridgeClock.send("SET_TARGET_MAP 0")
    probe_switch0 = bridgeClock.send("PROBE_LOCAL_CLOCKS")
    record("Phase4_LocalClock", "Probe_MapSwitching", {
        "probeMap1Active": probe_switch1.splitlines(),
        "probeMap0Restored": probe_switch0.splitlines()
    })
    shutdown_worker(procClock, bridgeClock)

    # =========================================================================
    # FINAL CLASSIFICATION EVALUATION
    # =========================================================================
    print("\n>>> EVALUATING FINAL CLASSIFICATION...")
    rt_step6_pass = results["phases"]["Phase2_RoundTrip"]["Step6_CensusCompare"]["isPass"]
    rt_step10_pass = results["phases"]["Phase2_RoundTrip"]["Step10_CensusReferenceCompare"]["isPass"]
    all_corruptions_detected = all(
        c_data["failClosedEnforced"]
        for c_data in results["phases"]["Phase3_Corruptions"].values()
    )
    context_b_clean = results["phases"]["Phase1_Contexts"]["LogAudit_ContextB"]["clean"]

    if rt_step6_pass and rt_step10_pass and all_corruptions_detected and context_b_clean:
        classification = "E1 ROUNDTRIP PASS"
    elif rt_step6_pass or rt_step10_pass:
        classification = "PARTIAL"
    else:
        classification = "FAIL"

    results["classification"] = classification
    RESULTS_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=" * 80)
    print(f"FINAL CLASSIFICATION: {classification}")
    print(f"Results recorded to: {RESULTS_FILE}")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    finally:
        for p in owned_processes:
            try:
                if p.poll() is None:
                    p.kill()
            except:
                pass
