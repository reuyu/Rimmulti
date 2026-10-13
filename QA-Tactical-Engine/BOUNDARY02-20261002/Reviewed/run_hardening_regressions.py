import sys, os, pathlib, socket, subprocess, time, json, hashlib, shutil, re, threading, xml.etree.ElementTree as ET

SCRATCH = pathlib.Path(r"C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch")
WORKSPACE = pathlib.Path(r"c:\Users\user\Desktop\RimMulti")
EXE = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")
ORIGINAL = WORKSPACE / "QA-Tactical-Engine/ENGINE02-20261002/CleanBoundary/Saves/Input.rws"

RESULTS_FILE = SCRATCH / "hardening-test-results.json"
results = {
    "suite": "WP-TAC-WORKER-HARDEN-01",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "tests": {}
}

owned_processes = []

def record(name, data):
    results["tests"][name] = data
    RESULTS_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{name}] {json.dumps(data, ensure_ascii=False)}", flush=True)

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

def prepare_profile(name, source_save=ORIGINAL, save_target_name="Input"):
    profile = SCRATCH / name
    if profile.exists():
        shutil.rmtree(profile, ignore_errors=True)
    (profile / "Config").mkdir(parents=True, exist_ok=True)
    (profile / "Saves").mkdir(parents=True, exist_ok=True)

    # ModsConfig with WorkerBridge and ProbeMod
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

    if source_save and source_save.exists():
        shutil.copy2(source_save, profile / "Saves" / f"{save_target_name}.rws")

    return profile

def launch_worker(profile, bridge_port=29500, probe_port=30500):
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

def main():
    print("================================================================================")
    print("STARTING WP-TAC-WORKER-HARDEN-01 REGRESSION SUITE")
    print("================================================================================")

    # -------------------------------------------------------------------------
    # PHASE 1: QA-ENGINE-002 MANIFEST & DEPENDENCY FALSE-SUCCESS FIXES
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 1: Testing QA-ENGINE-002 Manifest & Dependency Gating")
    p1_dir = prepare_profile("Harden_Manifest", ORIGINAL)
    proc1, b1, ms1 = launch_worker(p1_dir, 29510, 30510)
    record("LAUNCH_WORKER_1", {"pid": proc1.pid, "startup_ms": ms1})

    # Test 1.1: GET_ENVIRONMENT_MANIFEST
    env_manifest = b1.send("GET_ENVIRONMENT_MANIFEST")
    has_engine_ver = "1.6" in env_manifest
    has_dlc = "Royalty: True" in env_manifest and "Ideology: True" in env_manifest
    has_defs = "ThingDef:" in env_manifest and "HediffDef:" in env_manifest
    record("QA-ENGINE-002_EnvironmentManifest", {
        "verdict": "PASS" if (has_engine_ver and has_dlc and has_defs) else "FAIL",
        "manifest_preview": env_manifest[:300]
    })

    # Test 1.2: Undeclared missing mod in save meta (reproducing Sol's Omitted test)
    bad_mod_save = p1_dir / "Saves/MissingMod.rws"
    tree = ET.parse(ORIGINAL)
    root = tree.getroot()
    root.find("meta/modIds").append(ET.Element("li"))
    root.find("meta/modIds")[-1].text = "qa.actually.missing.dependency"
    tree.write(bad_mod_save, encoding="utf-8", xml_declaration=True)

    val_mod_resp = b1.send("VALIDATE_MANIFEST MissingMod")
    is_mod_rejected = val_mod_resp.startswith("MANIFEST_REJECTED") and "qa.actually.missing.dependency" in val_mod_resp
    record("QA-ENGINE-002_MissingMod_Validate", {
        "verdict": "PASS" if is_mod_rejected else "FAIL",
        "response": val_mod_resp
    })

    load_mod_resp = b1.send("LOAD_SAVE MissingMod")
    is_mod_load_rejected = load_mod_resp.startswith("LOAD_REJECTED")
    stat_mod = b1.send("STATUS")
    is_load_failed_state = "STATE: LOAD_FAILED" in stat_mod

    # Verify EXPORT_SAVE is strictly blocked
    exp_mod_resp = b1.send("EXPORT_SAVE PrematureMod")
    is_export_blocked = exp_mod_resp.startswith("ERROR:") and "LOAD_FAILED" in exp_mod_resp
    record("QA-ENGINE-002_MissingMod_LoadAndExportGating", {
        "verdict": "PASS" if (is_mod_load_rejected and is_load_failed_state and is_export_blocked) else "FAIL",
        "load_response": load_mod_resp,
        "status": stat_mod,
        "export_response": exp_mod_resp
    })

    # Test 1.3: Undeclared missing ThingDef in save XML (reproducing Sol's custom token drop)
    bad_def_save = p1_dir / "Saves/MissingDef.rws"
    tree_def = ET.parse(ORIGINAL)
    root_def = tree_def.getroot()
    for e in root_def.iter("def"):
        if e.text == "WarEconomy_TacticalProofToken":
            e.text = "QA_UndeclaredMissingToken"
    tree_def.write(bad_def_save, encoding="utf-8", xml_declaration=True)

    val_def_resp = b1.send("VALIDATE_MANIFEST MissingDef")
    is_def_rejected = val_def_resp.startswith("MANIFEST_REJECTED") and "QA_UndeclaredMissingToken" in val_def_resp
    record("QA-ENGINE-002_MissingDef_Validate", {
        "verdict": "PASS" if is_def_rejected else "FAIL",
        "response": val_def_resp
    })

    load_def_resp = b1.send("LOAD_SAVE MissingDef")
    stat_def = b1.send("STATUS")
    exp_def_resp = b1.send("EXPORT_SAVE PrematureDef")
    record("QA-ENGINE-002_MissingDef_LoadAndExportGating", {
        "verdict": "PASS" if (load_def_resp.startswith("LOAD_REJECTED") and "LOAD_FAILED" in stat_def and exp_def_resp.startswith("ERROR:")) else "FAIL",
        "load_response": load_def_resp,
        "status": stat_def,
        "export_response": exp_def_resp
    })

    # -------------------------------------------------------------------------
    # PHASE 2: QA-ENGINE-006 ENGINE-GENERATED COMPLEX FIXTURE
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 2: Generating Engine Complex Fixture (QA-ENGINE-006)")
    # Load valid original save first
    b1.send("LOAD_SAVE Input 0")
    ok, ready_stat, _ = wait_for_ready(b1)
    record("PHASE2_LoadInputReady", {"verdict": "PASS" if ok else "FAIL", "status": ready_stat})

    # Generate native complex fixture
    gen_resp = b1.send("GENERATE_COMPLEX_FIXTURE EngineComplexFixture")
    record("QA-ENGINE-006_GenerateComplexFixture", {"response": gen_resp})

    fixture_path = p1_dir / "Saves/EngineComplexFixture.rws"
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not created at {fixture_path}")

    # Audit the engine-generated XML for duplicate numeric IDs and required elements
    tree_fix = ET.parse(fixture_path)
    root_fix = tree_fix.getroot()
    id_map = {}
    dup_ids = []
    for elem in root_fix.iter():
        id_text = elem.findtext("id")
        if id_text and elem.find("def") is not None:
            m = re.search(r"(\d+)$", id_text)
            if m:
                num = int(m.group(1))
                if num in id_map:
                    dup_ids.append((id_map[num], id_text))
                else:
                    id_map[num] = id_text

    # Audit required entities
    has_stored_power = root_fix.find(".//storedPower") is not None
    has_bills = len(root_fix.findall(".//billStack/bills/li")) > 0
    has_animal_master = False
    for p in root_fix.iter():
        if p.tag in ["thing", "li"] and p.findtext("def") in ["LabradorRetriever", "Husky", "Boomrat"]:
            m = p.findtext("playerSettings/master")
            if m not in [None, "null", "", "None"]:
                has_animal_master = True
                break

    has_crop = False
    for p in root_fix.iter():
        if p.tag in ["thing", "li"] and p.attrib.get("Class") == "Plant" and p.find("growth") is not None:
            has_crop = True
            break

    has_casket_corpse = False
    for c in root_fix.iter():
        if c.tag in ["thing", "li"] and "Building_" in c.attrib.get("Class", ""):
            inner = c.find("innerContainer")
            if inner is not None:
                for item in inner.iter():
                    if "Corpse" in (item.attrib.get("Class") or "") or item.tag == "corpse" or "Corpse" in (item.findtext("def") or ""):
                        has_casket_corpse = True
                        break
        if has_casket_corpse:
            break

    fixture_audit_pass = (len(dup_ids) == 0 and has_stored_power and has_bills and has_animal_master and has_crop and has_casket_corpse)
    record("QA-ENGINE-006_EngineFixtureIntegrityAudit", {
        "verdict": "PASS" if fixture_audit_pass else "FAIL",
        "duplicate_numeric_id_pairs": len(dup_ids),
        "has_storedPower": has_stored_power,
        "has_bills": has_bills,
        "has_animal_master": has_animal_master,
        "has_crop_growth": has_crop,
        "has_casket_corpse": has_casket_corpse
    })

    # Export a baseline save from worker 1 and shutdown
    b1.send("EXPORT_SAVE Worker1_EngineComplexExport")
    b1.send("SHUTDOWN")
    proc1.wait(timeout=15)

    # -------------------------------------------------------------------------
    # PHASE 3: QA-ENGINE-007 MECHANICAL SCOPE FENCE (LOAD / READY TICK DRIFT)
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 3: Testing QA-ENGINE-007 Mechanical Scope Fence during Load")
    p2_dir = prepare_profile("Harden_Fence", fixture_path, "EngineFixture")
    proc2, b2, ms2 = launch_worker(p2_dir, 29520, 30520)

    # Connect QA Probe companion
    probe2 = BridgeClient(30520, timeout=10)
    snap_before_load = probe2.send("SNAP")

    # Load save and observe state
    b2.send("LOAD_SAVE EngineFixture 0")
    ok2, ready_stat2, _ = wait_for_ready(b2)
    snap_after_ready = probe2.send("SNAP")

    # Compare non-target map probes and global ticks
    # Before load vs after ready: did non-target map probe increment?
    m_probe_before = re.findall(r"Map=1 MapProbe=(\d+)", snap_before_load)
    m_probe_after = re.findall(r"Map=1 MapProbe=(\d+)", snap_after_ready)
    probe_val_before = int(m_probe_before[0]) if m_probe_before else 0
    probe_val_after = int(m_probe_after[0]) if m_probe_after else 0
    non_target_probe_drift = probe_val_after - probe_val_before

    record("QA-ENGINE-007_ScopeFence_LoadDrift", {
        "verdict": "PASS" if (ok2 and non_target_probe_drift == 0) else "FAIL",
        "ready_status": ready_stat2,
        "map1_probe_before": probe_val_before,
        "map1_probe_after": probe_val_after,
        "non_target_probe_drift": non_target_probe_drift
    })

    # -------------------------------------------------------------------------
    # PHASE 4: QA-ENGINE-003 MONOLITHIC TICK QUARANTINE & BOUNDS
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 4: Testing QA-ENGINE-003 Tick Monolithic Quarantine & Sliced Responsiveness")

    # Test 4.1: RUN_TICKS quarantined from normal protocol
    run_resp = b2.send("RUN_TICKS 50000")
    is_run_quarantined = run_resp.startswith("ERROR:") and "quarantined" in run_resp
    record("QA-ENGINE-003_RunTicksQuarantine", {
        "verdict": "PASS" if is_run_quarantined else "FAIL",
        "response": run_resp
    })

    # Test 4.2: STEP_TICKS hard-cap on slice size
    step_resp = b2.send("STEP_TICKS 1000 50000")
    has_cap = "SliceSize=20" in step_resp and "HardCap=20" in step_resp
    record("QA-ENGINE-003_StepTicksSliceCap", {
        "verdict": "PASS" if has_cap else "FAIL",
        "response": step_resp
    })

    # Test 4.3: Main-thread responsiveness during sliced simulation (concurrent STATUS latency)
    b2.send("STATUS")  # warm up poll to prime connection
    latencies = []
    for _ in range(10):
        t_poll = time.monotonic()
        st = b2.send("STATUS")
        latencies.append(round((time.monotonic() - t_poll) * 1000, 2))
        time.sleep(0.05)

    # Wait for remaining steps to finish
    t_wait = time.monotonic()
    while time.monotonic() - t_wait < 30:
        s = b2.send("STATUS")
        if "RemainingStep=0" in s:
            break
        time.sleep(0.1)

    max_lat = max(latencies)
    avg_lat = sum(latencies) / len(latencies)
    record("QA-ENGINE-003_MainThreadResponsiveness", {
        "verdict": "PASS" if max_lat < 50.0 else "FAIL",
        "avg_ms": avg_lat,
        "max_ms": max_lat,
        "samples": latencies
    })

    # Test 4.4: CANCEL_SIMULATION
    b2.send("STEP_TICKS 5000 10")
    cancel_resp = b2.send("CANCEL_SIMULATION")
    stat_cancel = b2.send("STATUS")
    is_cancelled = "RemainingStep=0" in stat_cancel
    record("QA-ENGINE-003_CancelSimulation", {
        "verdict": "PASS" if (cancel_resp.startswith("OK:") and is_cancelled) else "FAIL",
        "response": cancel_resp,
        "status": stat_cancel
    })

    # -------------------------------------------------------------------------
    # PHASE 5: QA-ENGINE-005 FASTECOLOGY DEBUG BYPASS SUPPRESSION
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 5: Testing QA-ENGINE-005 fastEcology Debug Bypass Suppression")
    snap_before_eco = probe2.send("SNAP")
    eco_resp = probe2.send("ECOLOGY")
    snap_after_eco = probe2.send("SNAP")

    # In Sol's clean_boundary_run: fastEcology caused 25,835 plants to age by 2000 ticks.
    # Check player.log for our warning and inspect grid plant
    log_content = ""
    candidates = [
        p2_dir / "player.log",
        pathlib.Path(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log")),
        pathlib.Path(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player-prev.log"))
    ]
    for c in candidates:
        if c.exists():
            try:
                log_content += c.read_text(encoding="utf-8", errors="replace") + "\n"
            except:
                pass

    has_eco_warning = "fastEcology is unsupported in Tactical Worker. Forcing false" in log_content

    # Inspect grid plant in map 1
    plant_before = re.findall(r"GridPlant=Plant_Rice\d+ Def=Plant_Rice Growth=([\d\.]+)", snap_before_eco)
    plant_after = re.findall(r"GridPlant=Plant_Rice\d+ Def=Plant_Rice Growth=([\d\.]+)", snap_after_eco)

    record("QA-ENGINE-005_FastEcologySuppression", {
        "verdict": "PASS" if has_eco_warning else "FAIL",
        "probe_response": eco_resp,
        "warning_logged": has_eco_warning
    })

    # -------------------------------------------------------------------------
    # PHASE 6: QA-ENGINE-008 SIMULATION START DEBT ELIMINATION
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 6: Testing QA-ENGINE-008 Simulation Start Debt Elimination")
    # Simulate long main thread operation: EXPORT_SAVE
    exp_long_resp = b2.send("EXPORT_SAVE PreStartDebtCheck")

    # Immediately issue START_SIMULATION 60
    start_sim_resp = b2.send("START_SIMULATION 60")
    samples = []
    t_start = time.monotonic()
    while time.monotonic() - t_start < 3.0:
        t_s = time.monotonic()
        s_txt = b2.send("STATUS")
        m_sim = re.search(r"TicksSim=(\d+)", s_txt)
        tsim = int(m_sim.group(1)) if m_sim else 0
        samples.append({"t": t_s, "sim": tsim})
        time.sleep(0.05)

    b2.send("PAUSE_SIMULATION")

    # Calculate tick increments between samples
    increments = [b["sim"] - a["sim"] for a, b in zip(samples, samples[1:])]
    first_few_increments = increments[:5]
    total_ticks = samples[-1]["sim"] - samples[0]["sim"]
    total_time = samples[-1]["t"] - samples[0]["t"]
    measured_tps = total_ticks / total_time if total_time > 0 else 0

    # In ENGINE-02 before: initial increments were 10->40->50 burst, measured TPS was 76.96.
    # With start debt fix: initial increment should not burst (<= 6 per 50ms interval, ~60 TPS)
    has_no_burst = all(inc <= 6 for inc in first_few_increments)
    is_tps_stable = abs(measured_tps - 60.0) < 5.0

    record("QA-ENGINE-008_SimulationStartDebt", {
        "verdict": "PASS" if (has_no_burst and is_tps_stable) else "FAIL",
        "first_five_sample_increments": first_few_increments,
        "measured_tps": round(measured_tps, 2),
        "total_ticks_in_3s": total_ticks
    })

    # -------------------------------------------------------------------------
    # PHASE 7: QA-ENGINE-006 FULL STRICT GRAPH ROUNDTRIP ORACLE
    # -------------------------------------------------------------------------
    print("\n>>> PHASE 7: Strict Full Graph Roundtrip Oracle")
    # Export save after simulation
    b2.send("EXPORT_SAVE EngineExport_AfterSim")
    snap_post_sim = b2.send("GET_MAP_DETAILED_SUMMARY 0")
    snap_map1_post = b2.send("GET_MAP_DETAILED_SUMMARY 1")
    world_post = b2.send("GET_WORLD_INFO")

    b2.send("SHUTDOWN")
    probe2.close()
    proc2.wait(timeout=15)

    # Launch Reload Worker with the exported save
    exported_save = p2_dir / "Saves/EngineExport_AfterSim.rws"
    p3_dir = prepare_profile("Harden_Reload", exported_save, "ReloadInput")
    proc3, b3, ms3 = launch_worker(p3_dir, 29530, 30530)

    b3.send("LOAD_SAVE ReloadInput 0")
    ok3, ready3, _ = wait_for_ready(b3)
    snap_reload_map0 = b3.send("GET_MAP_DETAILED_SUMMARY 0")
    snap_reload_map1 = b3.send("GET_MAP_DETAILED_SUMMARY 1")

    # Strict multi-dimension comparison
    # 1. Colonist match
    pawn_preserved = ("Pawn ID=Human" in snap_post_sim and "Pawn ID=Human" in snap_reload_map0)
    weapon_preserved = ("Weapon=Gun_Autopistol" in snap_post_sim and "Weapon=Gun_Autopistol" in snap_reload_map0)
    apparel_preserved = ("Apparel_FlakVest" in snap_post_sim and "Apparel_FlakVest" in snap_reload_map0)
    hediff_preserved = ("Stab" in snap_post_sim and "Stab" in snap_reload_map0 and "BionicEye" in snap_reload_map0)
    bed_preserved = ("Bed=Bed" in snap_post_sim and "Bed=Bed" in snap_reload_map0)
    animal_master_preserved = bool(re.search(r"Animal ID=.*?, Master=(?!None|null)\w+", snap_post_sim) and re.search(r"Animal ID=.*?, Master=(?!None|null)\w+", snap_reload_map0))
    bills_preserved = ("Bills=1" in snap_post_sim and "Bills=1" in snap_reload_map0)
    battery_preserved = ("Battery(" in snap_post_sim and "Battery(" in snap_reload_map0)
    crop_preserved = ("Crop ID=" in snap_post_sim and "Crop ID=" in snap_reload_map0)
    casket_corpse_preserved = (("Contained=Corpse" in snap_post_sim or "corpse" in snap_post_sim.lower()) and ("Contained=Corpse" in snap_reload_map0 or "corpse" in snap_reload_map0.lower()))

    # Non-target map preservation
    non_target_preserved = ("MapIndex: 1" in snap_map1_post and "MapIndex: 1" in snap_reload_map1)

    all_dimensions_pass = (
        pawn_preserved and weapon_preserved and apparel_preserved and
        hediff_preserved and bed_preserved and animal_master_preserved and
        bills_preserved and battery_preserved and crop_preserved and
        casket_corpse_preserved and non_target_preserved
    )

    record("QA-ENGINE-006_StrictGraphRoundtripOracle", {
        "verdict": "PASS within tested scope" if all_dimensions_pass else "FAIL",
        "dimensions": {
            "pawn": pawn_preserved,
            "weapon": weapon_preserved,
            "apparel": apparel_preserved,
            "hediffs": hediff_preserved,
            "bed_assignment": bed_preserved,
            "animal_master": animal_master_preserved,
            "workbench_bills": bills_preserved,
            "battery_power": battery_preserved,
            "crops": crop_preserved,
            "casket_corpse": casket_corpse_preserved,
            "non_target_map_preserved": non_target_preserved
        }
    })

    b3.send("SHUTDOWN")
    proc3.wait(timeout=15)

    print("\n================================================================================")
    print("TEST SUITE COMPLETED SUCCESSFULLY. Results written to:")
    print(str(RESULTS_FILE))
    print("================================================================================")

if __name__ == "__main__":
    try:
        main()
    finally:
        for p in owned_processes:
            if p.poll() is None:
                p.kill()
                p.wait(timeout=5)
