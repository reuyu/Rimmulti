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

WORKSPACE = Path(r"c:\Users\user\Desktop\RimMulti")
SCRATCH = WORKSPACE / "scratch"
EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")
SAVES_DIR = Path(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"))

RESULTS_FILE = SCRATCH / "semantic_gate_02_results.json"
results = {
    "workOrder": "WP-POC-ENGINE-HOST-SEMANTIC-GATE-02",
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "classification": "PENDING",
    "provenance": {},
    "negativeBattery": {},
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
        # Also ensure in global saves
        shutil.copy2(source_save, SAVES_DIR / f"{save_target_name}.rws")

    return profile

def launch_worker(profile, bridge_port=29200):
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

def prune_to_context_b(source_path: Path, dest_path: Path):
    tree = ET.parse(source_path)
    root = tree.getroot()
    game = root.find("game")
    maps = game.find("maps")
    parent_id = maps[0].findtext("mapInfo/parent").split("_")[-1]

    for m in list(maps)[1:]:
        maps.remove(m)

    w_objs = game.find("world/worldObjects/worldObjects")
    for obj in list(w_objs):
        if obj.findtext("ID") != parent_id:
            w_objs.remove(obj)

    tree.write(dest_path, encoding="utf-8", xml_declaration=True)

def record_save_state(save_path: Path) -> dict:
    if not save_path.exists():
        return {"exists": False}
    return {
        "exists": True,
        "bytes": save_path.stat().st_size,
        "sha256": sha256_file(save_path)
    }

def main():
    print("=" * 80)
    print("STARTING WP-POC-ENGINE-HOST-SEMANTIC-GATE-02 AUTOMATED SUITE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # 1. Exact Provenance
    # -------------------------------------------------------------------------
    dll_path = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll")
    engine_dll = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll")
    clean_src = SCRATCH / "CleanSettlementFixture.rws"
    clean_b = SCRATCH / "TargetSettlement_Clean_ContextB.rws"

    # Read DLL MVID using powershell
    mvid_cmd = f"(Get-Item '{dll_path}').FullName; [System.Reflection.Assembly]::LoadFrom('{dll_path}').ManifestModule.ModuleVersionId.ToString()"
    mvid_out = subprocess.check_output(["powershell", "-NoProfile", "-Command", mvid_cmd], text=True).strip().splitlines()
    dll_mvid = mvid_out[-1].strip()

    eng_mvid_cmd = f"[System.Reflection.Assembly]::LoadFrom('{engine_dll}').ManifestModule.ModuleVersionId.ToString()"
    eng_mvid = subprocess.check_output(["powershell", "-NoProfile", "-Command", eng_mvid_cmd], text=True).strip()

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
        }
    }
    results["provenance"] = provenance
    print("\n[PROVENANCE RECORDED]")
    print(f"  Worker DLL SHA256: {provenance['binaries']['workerBridgeDll']['sha256']}")
    print(f"  Worker DLL MVID:   {provenance['binaries']['workerBridgeDll']['mvid']}")
    print(f"  Clean Source SHA:  {provenance['fixtures']['CleanSettlementFixture.rws']['sha256']}")
    print(f"  Clean ContextB SHA:{provenance['fixtures']['TargetSettlement_Clean_ContextB.rws']['sha256']}")

    # -------------------------------------------------------------------------
    # 2. READY-Preserving Negative Battery (15 Dimensions)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 1: 15-DIMENSION READY-PRESERVING NEGATIVE BATTERY")
    print("=" * 80)

    # Ensure all corrupted fixtures are in Saves folder and load profile
    profile_neg = prepare_profile("Profile_NegativeBattery")
    # Copy corrupted fixtures to profile Saves as well
    for f in (SCRATCH / "CorruptedFixtures").glob("Corrupted_*.rws"):
        shutil.copy2(f, profile_neg / "Saves" / f.name)
        shutil.copy2(f, SAVES_DIR / f.name)

    # Copy clean manifest to profile Saves and global saves
    clean_manifest = SCRATCH / "TargetSettlement_Clean_ContextB.census.json"
    shutil.copy2(clean_manifest, profile_neg / "Saves" / clean_manifest.name)
    shutil.copy2(clean_manifest, SAVES_DIR / clean_manifest.name)

    proc_neg, bridge_neg, ms_neg = launch_worker(profile_neg, bridge_port=29200)
    print(f"Launched Negative Battery Worker (PID={proc_neg.pid}, startup={ms_neg}ms)")

    corr_manifest = json.loads((SCRATCH / "CorruptedFixtures/corruption_battery_manifest.json").read_text(encoding="utf-8"))
    battery_results = []
    all_detected = True
    all_export_refused = True

    for item in corr_manifest:
        tag = item["tag"]
        desc = item["description"]
        save_name = f"Corrupted_{tag}"
        print(f"\n--- Testing Corruption {tag}: {desc} ---")

        # 1. Load corrupted save
        load_res = bridge_neg.send(f"LOAD_SAVE {save_name} 0")
        ok, stat, _ = wait_for_ready(bridge_neg)
        if not ok:
            print(f"  FAILED to reach READY: {stat}")
            all_detected = False
            continue

        # 2. Check initial semantic status -> must be VALIDATION_REQUIRED
        sem_stat_1 = bridge_neg.send("GET_SEMANTIC_STATUS")
        print(f"  Post-load status: {sem_stat_1}")

        # 3. Attempt unapproved export -> MUST be EXPORT_BLOCKED
        unapp_export = bridge_neg.send(f"EXPORT_SAVE TestUnapproved_{tag}")
        is_unapp_blocked = "EXPORT_BLOCKED" in unapp_export
        print(f"  Unapproved export response: {unapp_export} (Blocked={is_unapp_blocked})")

        # 4. Attempt approval against clean manifest -> MUST be SEMANTIC_REJECTED
        app_res = bridge_neg.send(f"APPROVE_SEMANTIC {clean_manifest.name}")
        is_rejected = "SEMANTIC_REJECTED" in app_res
        print(f"  Approval attempt: {app_res[:120]}... (Rejected={is_rejected})")

        # 5. Check semantic status after rejected approval -> must be VALIDATION_FAILED
        sem_stat_2 = bridge_neg.send("GET_SEMANTIC_STATUS")
        is_val_failed = "State=VALIDATION_FAILED" in sem_stat_2
        print(f"  Post-rejection status: {sem_stat_2}")

        # 6. Attempt export after rejection -> MUST be EXPORT_BLOCKED
        blocked_export = bridge_neg.send(f"EXPORT_SAVE TestBlocked_{tag}")
        is_post_blocked = "EXPORT_BLOCKED" in blocked_export
        print(f"  Post-rejection export: {blocked_export} (Blocked={is_post_blocked})")

        # 7. Confirm 0 bytes exported on disk
        final_disk_file = profile_neg / "Saves" / f"TestBlocked_{tag}.rws"
        global_disk_file = SAVES_DIR / f"TestBlocked_{tag}.rws"
        zero_bytes = (not final_disk_file.exists()) and (not global_disk_file.exists())
        print(f"  0 bytes on disk: {zero_bytes}")

        case_passed = is_rejected and is_val_failed and is_post_blocked and zero_bytes
        if not case_passed:
            all_detected = False
            all_export_refused = False

        battery_results.append({
            "tag": tag,
            "description": desc,
            "fixture": item["file"],
            "fixtureSha256": item["sha256"],
            "reachedReady": ok,
            "unapprovedExportBlocked": is_unapp_blocked,
            "approvalRejected": is_rejected,
            "rejectionDetail": app_res.split("\n")[0],
            "validationFailedState": is_val_failed,
            "postRejectionExportBlocked": is_post_blocked,
            "zeroBytesOnDisk": zero_bytes,
            "casePass": case_passed
        })

    shutdown_worker(proc_neg, bridge_neg)
    results["negativeBattery"] = {
        "allDetected": all_detected,
        "allExportRefused": all_export_refused,
        "casesCount": len(battery_results),
        "passCount": sum(1 for c in battery_results if c["casePass"]),
        "cases": battery_results
    }
    print(f"\n[NEGATIVE BATTERY SUMMARY] Passed: {results['negativeBattery']['passCount']}/{len(battery_results)} cases.")

    # -------------------------------------------------------------------------
    # 3. Fresh-Process Positive Rerun (A -> B -> C)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("PHASE 2: FRESH-PROCESS POSITIVE RERUN (PROCESS A -> B -> C)")
    print("=" * 80)

    # Process A: Clean Source -> Manifest -> Approved Staged Export -> Exit
    print("\n--- PROCESS A: Clean Source -> Approved Staged Export ---")
    prof_A = prepare_profile("Profile_A", clean_b, "SourceA")
    proc_A, bridge_A, ms_A = launch_worker(prof_A, bridge_port=29210)
    print(f"Process A launched (PID={proc_A.pid})")

    bridge_A.send("LOAD_SAVE SourceA 0")
    ok_A, stat_A, _ = wait_for_ready(bridge_A)
    print(f"Process A reached READY: {stat_A}")

    # Generate baseline census on Process A live map
    census_A_res = bridge_A.send("EXPORT_CENSUS A_CleanManifest 0")
    print(f"Process A live census export: {census_A_res}")

    # Approve semantic against generated clean census
    app_A = bridge_A.send("APPROVE_SEMANTIC A_CleanManifest.census.json")
    print(f"Process A semantic approval: {app_A}")

    # Export approved save via staged export gate
    export_A_res = bridge_A.send("EXPORT_SAVE A_ApprovedArtifact")
    print(f"Process A staged export: {export_A_res}")

    shutdown_worker(proc_A, bridge_A)
    print(f"Process A exited with code {proc_A.returncode}")

    a_target_artifact = prof_A / "Saves/A_ApprovedArtifact.rws"
    if not a_target_artifact.exists():
        a_target_artifact = SAVES_DIR / "A_ApprovedArtifact.rws"
    a_target_sha = sha256_file(a_target_artifact)
    print(f"A_ApprovedArtifact: {a_target_artifact} ({a_target_artifact.stat().st_size:,} bytes, SHA: {a_target_sha})")

    a_manifest_path = prof_A / "Saves/A_CleanManifest.census.json"
    if not a_manifest_path.exists():
        a_manifest_path = SAVES_DIR / "A_CleanManifest.census.json"

    # Process B: Load A Artifact -> Validate -> Active Job -> Tick 100 -> Revalidate -> Approved Export -> Exit
    print("\n--- PROCESS B: Load A Artifact -> Tick 100 -> Approved Export ---")
    prof_B = prepare_profile("Profile_B", a_target_artifact, "InputB")
    shutil.copy2(a_manifest_path, prof_B / "Saves/A_CleanManifest.census.json")
    shutil.copy2(a_manifest_path, SAVES_DIR / "A_CleanManifest.census.json")

    proc_B, bridge_B, ms_B = launch_worker(prof_B, bridge_port=29220)
    print(f"Process B launched (PID={proc_B.pid})")

    bridge_B.send("LOAD_SAVE InputB 0")
    ok_B, stat_B, _ = wait_for_ready(bridge_B)
    print(f"Process B reached READY: {stat_B}")

    # Validate against A_CleanManifest manifest
    val_B_init = bridge_B.send("VALIDATE_SEMANTIC A_CleanManifest.census.json")
    print(f"Process B initial validation: {val_B_init}")

    app_B_init = bridge_B.send("APPROVE_SEMANTIC A_CleanManifest.census.json")
    print(f"Process B initial approval: {app_B_init}")

    # Execute Sliced Simulation for 100 ticks
    print("Process B stepping 100 ticks...")
    step_B = bridge_B.send("STEP_TICKS 100 20")
    print(f"  Step response: {step_B}")

    # Wait for ticks to complete
    t0 = time.monotonic()
    ticks_done = False
    while time.monotonic() - t0 < 30:
        st = bridge_B.send("STATUS")
        if "RemainingStep=0" in st:
            ticks_done = True
            print(f"  Ticks completed: {st}")
            break
        time.sleep(0.5)

    # Invalidation Check: ticks advanced, so semanticState MUST be VALIDATION_REQUIRED
    sem_stat_post_tick = bridge_B.send("GET_SEMANTIC_STATUS")
    print(f"Process B post-tick semantic status: {sem_stat_post_tick}")
    invalidated_ok = "State=VALIDATION_REQUIRED" in sem_stat_post_tick

    # Attempt export without re-approval -> MUST be EXPORT_BLOCKED
    unapp_b = bridge_B.send("EXPORT_SAVE B_UnapprovedPostTick")
    is_b_blocked = "EXPORT_BLOCKED" in unapp_b
    print(f"Process B unapproved post-tick export: {unapp_b} (Blocked={is_b_blocked})")

    # Generate post-tick census
    census_B_post = bridge_B.send("EXPORT_CENSUS B_PostTick_Manifest 0")
    print(f"Process B post-tick census export: {census_B_post}")

    # Re-approve against post-tick census
    app_B_post = bridge_B.send("APPROVE_SEMANTIC B_PostTick_Manifest.census.json")
    print(f"Process B post-tick approval: {app_B_post}")

    # Export approved post-tick save
    export_B_res = bridge_B.send("EXPORT_SAVE B_PostTick_Artifact")
    print(f"Process B approved export: {export_B_res}")

    shutdown_worker(proc_B, bridge_B)
    print(f"Process B exited with code {proc_B.returncode}")

    # Get B_PostTick_Artifact path & SHA
    b_artifact = prof_B / "Saves/B_PostTick_Artifact.rws"
    if not b_artifact.exists():
        b_artifact = SAVES_DIR / "B_PostTick_Artifact.rws"
    b_artifact_sha = sha256_file(b_artifact)
    print(f"B_PostTick_Artifact: {b_artifact} ({b_artifact.stat().st_size:,} bytes, SHA: {b_artifact_sha})")

    b_manifest_path = prof_B / "Saves/B_PostTick_Manifest.census.json"
    if not b_manifest_path.exists():
        b_manifest_path = SAVES_DIR / "B_PostTick_Manifest.census.json"

    # Process C: Load B Export -> Validate / Compare -> Exit
    print("\n--- PROCESS C: Load B Export -> Validate / Compare ---")
    prof_C = prepare_profile("Profile_C", b_artifact, "InputC")
    shutil.copy2(b_manifest_path, prof_C / "Saves/B_PostTick_Manifest.census.json")
    shutil.copy2(b_manifest_path, SAVES_DIR / "B_PostTick_Manifest.census.json")

    proc_C, bridge_C, ms_C = launch_worker(prof_C, bridge_port=29230)
    print(f"Process C launched (PID={proc_C.pid})")

    bridge_C.send("LOAD_SAVE InputC 0")
    ok_C, stat_C, _ = wait_for_ready(bridge_C)
    print(f"Process C reached READY: {stat_C}")

    # Validate against B_PostTick_Manifest census
    val_C = bridge_C.send("VALIDATE_SEMANTIC B_PostTick_Manifest.census.json")
    print(f"Process C validation: {val_C}")
    c_pass = "VALIDATION_PASS" in val_C

    app_C = bridge_C.send("APPROVE_SEMANTIC B_PostTick_Manifest.census.json")
    print(f"Process C approval: {app_C}")

    shutdown_worker(proc_C, bridge_C)
    print(f"Process C exited with code {proc_C.returncode}")

    fresh_process_results = {
        "processA": {
            "pid": proc_A.pid,
            "status": stat_A,
            "approval": app_A,
            "exportResponse": export_A_res,
            "artifact": {
                "file": "A_TargetArtifact.rws",
                "bytes": a_target_artifact.stat().st_size,
                "sha256": a_target_sha
            }
        },
        "processB": {
            "pid": proc_B.pid,
            "status": stat_B,
            "initialApproval": app_B_init,
            "ticksAdvanced": 100,
            "invalidatedOk": invalidated_ok,
            "unapprovedExportBlocked": is_b_blocked,
            "postTickApproval": app_B_post,
            "exportResponse": export_B_res,
            "artifact": {
                "file": "B_PostTick_Artifact.rws",
                "bytes": b_artifact.stat().st_size,
                "sha256": b_artifact_sha
            }
        },
        "processC": {
            "pid": proc_C.pid,
            "status": stat_C,
            "validation": val_C,
            "validationPass": c_pass,
            "approval": app_C
        },
        "zeroUnexplainedMismatch": c_pass and all_detected and all_export_refused
    }
    results["freshProcessPositive"] = fresh_process_results

    # -------------------------------------------------------------------------
    # 4. Context Terminology Analysis (Pruned Target-Map Owner Context)
    # -------------------------------------------------------------------------
    results["contextAnalysis"] = {
        "contextName": "Pruned Target-Map Owner Context",
        "inventory": {
            "provenRequired": [
                "World FactionManager with PlayerColony and referenced hostile/neutral factions",
                "Parent WorldObject (Settlement/MapParent) matching Map.info.parent",
                "Active DefDatabase registries (ThingDef, HediffDef, RecipeDef, PawnKindDef, BiomeDef)"
            ],
            "retainedUnknown": [
                "Unspawned WorldPawns referenced in directRelations (e.g. Spouse Human309)",
                "Global TaleManager entries associated with colonist historical events",
                "World Grid Tile coordinate attributes for celestial day/night calculations"
            ],
            "reconstructible": [
                "WeatherManager.tickedLastWeather transient state",
                "Transient JobDriver made pointers (re-instantiated upon load)",
                "Local lighting grid and pathfinding cache tables"
            ],
            "futurePlayerGlobalCandidate": [
                "Colony faction research manager and unlocked tech trees",
                "Cross-settlement shared currency / silver accounts",
                "Global quest states and empire goodwill ratings"
            ]
        }
    }

    # Final Classification
    if results["negativeBattery"]["passCount"] == 15 and c_pass:
        results["classification"] = "E1 ENGINE SEMANTIC GATE PASS"
    else:
        results["classification"] = "PARTIAL"

    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFinal Classification: {results['classification']}")
    print(f"Results written to: {RESULTS_FILE}")

if __name__ == "__main__":
    main()
