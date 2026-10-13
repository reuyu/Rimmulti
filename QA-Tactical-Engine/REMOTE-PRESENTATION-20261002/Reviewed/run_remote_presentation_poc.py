import os
import sys
import time
import json
import socket
import shutil
import hashlib
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows console
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"C:\Users\user\.gemini\antigravity-ide\brain\877c240f-d035-4476-9d3b-3a03f75f1f65\scratch")
RIMWORLD_EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")
FIXTURE_SOURCE = BASE_DIR / "Harden_Manifest" / "Saves" / "EngineComplexFixture.rws"

WORKER_DATA = BASE_DIR / "RemoteTactical_WorkerData"
CLIENT_DATA = BASE_DIR / "RemoteTactical_ClientData"
WORKER_PORT = 7792
CLIENT_PORT = 7793

MODS_CONFIG_XML = """<?xml version="1.0" encoding="utf-8"?>
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
    <li>wareconomy.remotepresentation.poc</li>
  </activeMods>
  <knownExpansions>
    <li>ludeon.rimworld.royalty</li>
    <li>ludeon.rimworld.ideology</li>
    <li>ludeon.rimworld.biotech</li>
    <li>ludeon.rimworld.anomaly</li>
    <li>ludeon.rimworld.odyssey</li>
  </knownExpansions>
</ModsConfigData>
"""

PREFS_XML = """<?xml version="1.0" encoding="utf-8"?>
<PrefsData>
  <volumeGame>0</volumeGame>
  <volumeMusic>0</volumeMusic>
  <volumeAmbient>0</volumeAmbient>
  <pauseOnLoad>false</pauseOnLoad>
  <pauseOnUrgentLetter>false</pauseOnUrgentLetter>
  <devMode>true</devMode>
</PrefsData>
"""

def compute_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().upper()

def setup_profile_folder(folder: Path):
    config_dir = folder / "Config"
    saves_dir = folder / "Saves"
    config_dir.mkdir(parents=True, exist_ok=True)
    saves_dir.mkdir(parents=True, exist_ok=True)

    with open(config_dir / "ModsConfig.xml", "w", encoding="utf-8") as f:
        f.write(MODS_CONFIG_XML)
    with open(config_dir / "Prefs.xml", "w", encoding="utf-8") as f:
        f.write(PREFS_XML)

    target_fixture = saves_dir / "EngineComplexFixture.rws"
    shutil.copy2(FIXTURE_SOURCE, target_fixture)
    print(f"[Setup] Prepared {folder} with fixture {target_fixture.name} (SHA: {compute_hash(target_fixture)[:16]}...)")

def send_tcp_command(port: int, cmd_str: str, timeout: float = 10.0) -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(("127.0.0.1", port))
        s.sendall((cmd_str + "\n").encode("utf-8"))
        f = s.makefile("r", encoding="utf-8-sig")
        line = f.readline()
        return line.strip() if line else ""
    finally:
        s.close()

def wait_for_worker(port: int, max_wait: float = 120.0) -> bool:
    start = time.time()
    ping_cmd = json.dumps({"CommandType": "PING", "Token": "Player_A_Token"})
    while time.time() - start < max_wait:
        try:
            resp = send_tcp_command(port, ping_cmd, timeout=2.0)
            if resp and ("PONG" in resp or "ACCEPTED" in resp):
                print(f"[Wait] Worker TCP port {port} answered at {time.time()-start:.1f}s: {resp[:60]}")
                return True
        except Exception:
            pass
        time.sleep(2.0)
    return False

def wait_for_client(port: int, max_wait: float = 120.0) -> bool:
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = send_tcp_command(port, "PING", timeout=2.0)
            if resp and "PONG" in resp:
                print(f"[Wait] Client TCP port {port} answered at {time.time()-start:.1f}s: {resp[:60]}")
                return True
        except Exception:
            pass
        time.sleep(2.0)
    return False

def main():
    print("=" * 70)
    print("WP-POC-REMOTE-TACTICAL-PRESENTATION-01 ORCHESTRATION")
    print("=" * 70)

    # 1. Setup profile data folders
    print("\n--- 1. Setting up Isolated Worker and Client Profiles ---")
    setup_profile_folder(WORKER_DATA)
    setup_profile_folder(CLIENT_DATA)

    # 2. Launch Worker Process
    print("\n--- 2. Launching Authoritative Tactical Worker Process ---")
    worker_cmd = [
        str(RIMWORLD_EXE),
        "-batchmode",
        "-nographics",
        f"-savedatafolder={WORKER_DATA}",
        "-remote-worker",
        "-worker-port",
        str(WORKER_PORT)
    ]
    print(f"[Launch] Worker command: {' '.join(worker_cmd)}")
    worker_proc = subprocess.Popen(worker_cmd)
    print(f"[Launch] Worker PID: {worker_proc.pid}")

    print(f"[Wait] Waiting for Worker TCP listener on port {WORKER_PORT} (up to 120s)...")
    if not wait_for_worker(WORKER_PORT, max_wait=120):
        print("[FAIL] Worker did not start TCP listener within 120s.")
        worker_proc.kill()
        sys.exit(1)

    # 3. Load Save on Worker
    print("\n--- 3. Loading EngineComplexFixture on Worker ---")
    load_cmd = json.dumps({
        "CommandType": "LOAD_SAVE",
        "CustomData": "EngineComplexFixture",
        "Token": "Player_A_Token"
    })
    resp = send_tcp_command(WORKER_PORT, load_cmd, timeout=30.0)
    print(f"[Worker] Load command response: {resp}")

    # Poll Worker status until map loaded
    print("[Worker] Waiting for map to load on Worker...")
    status_cmd = json.dumps({"CommandType": "STATUS", "Token": "Player_A_Token"})
    map_ready = False
    for _ in range(60):
        time.sleep(1.0)
        st_resp = send_tcp_command(WORKER_PORT, status_cmd, timeout=5.0)
        if "MAPS=" in st_resp:
            try:
                st_data = json.loads(st_resp)
                msg = st_data.get("Message", "")
                if "MAPS=" in msg:
                    parts = dict(p.split("=") for p in msg.split(", ") if "=" in p)
                    if int(parts.get("MAPS", 0)) > 0 and int(parts.get("PAWNS", 0)) > 0:
                        print(f"[Worker] Map loaded successfully: {msg}")
                        map_ready = True
                        break
            except Exception as e:
                print(f"[Worker] Status parse note: {e}, raw: {st_resp}")
    if not map_ready:
        print("[FAIL] Worker map failed to load in time.")
        worker_proc.kill()
        sys.exit(1)

    # 4. Launch Presentation Client Process
    print("\n--- 4. Launching Presentation Client Process ---")
    client_cmd = [
        str(RIMWORLD_EXE),
        "-batchmode",
        "-nographics",
        f"-savedatafolder={CLIENT_DATA}",
        "-remote-client",
        "-client-port",
        str(CLIENT_PORT),
        "-connect",
        f"127.0.0.1:{WORKER_PORT}"
    ]
    print(f"[Launch] Client command: {' '.join(client_cmd)}")
    client_proc = subprocess.Popen(client_cmd)
    print(f"[Launch] Client PID: {client_proc.pid}")

    print(f"[Wait] Waiting for Client TCP control listener on port {CLIENT_PORT} (up to 120s)...")
    if not wait_for_client(CLIENT_PORT, max_wait=120):
        print("[FAIL] Client did not start TCP listener within 120s.")
        client_proc.kill()
        worker_proc.kill()
        sys.exit(1)

    # 5. Load Mirror Map on Client
    print("\n--- 5. Loading Mirror EngineComplexFixture on Client ---")
    c_load_resp = send_tcp_command(CLIENT_PORT, "LOAD_SAVE EngineComplexFixture", timeout=30.0)
    print(f"[Client] Load command response: {c_load_resp}")

    print("[Client] Waiting for mirror map to load on Client...")
    c_ready = False
    for _ in range(60):
        time.sleep(1.0)
        st_resp = send_tcp_command(CLIENT_PORT, "STATUS", timeout=5.0)
        if "Maps=" in st_resp:
            try:
                tokens = st_resp.replace("STATUS: ", "").split(", ")
                p_dict = dict(t.split("=") for t in tokens if "=" in t)
                if int(p_dict.get("Maps", 0)) > 0 and int(p_dict.get("Pawns", 0)) > 0:
                    print(f"[Client] Mirror map loaded: {st_resp}")
                    c_ready = True
                    break
            except Exception:
                pass
    if not c_ready:
        print("[FAIL] Client mirror map failed to load in time.")
        client_proc.kill()
        worker_proc.kill()
        sys.exit(1)

    # 6. Connect Client to Worker
    print("\n--- 6. Connecting Client to Worker ---")
    conn_resp = send_tcp_command(CLIENT_PORT, f"CONNECT_WORKER 127.0.0.1:{WORKER_PORT}", timeout=10.0)
    print(f"[Client] Connect response: {conn_resp}")

    # 7. Run Full Automated PoC Test Suite
    print("\n--- 7. Executing Automated Remote Presentation Test Suite ---")
    results_file = BASE_DIR / "remote_presentation_poc_results.json"
    if results_file.exists():
        results_file.unlink()

    suite_resp = send_tcp_command(CLIENT_PORT, "RUN_POC_SUITE", timeout=10.0)
    print(f"[Client] Run suite response: {suite_resp}")

    # 8. Poll for Test Suite Completion
    print("[Wait] Monitoring test suite execution progress...")
    suite_done = False
    for i in range(120):
        time.sleep(1.0)
        if results_file.exists() and results_file.stat().st_size > 100:
            print(f"[Results] Found results file ({results_file.stat().st_size} bytes) at elapsed {i+1}s!")
            suite_done = True
            break
        if (i + 1) % 10 == 0:
            print(f"[Wait] Still running... ({i+1}s elapsed)")

    if not suite_done:
        print("[FAIL] Test suite did not complete within 120s.")
    else:
        print("\n" + "=" * 70)
        print("TEST SUITE EXECUTION RESULTS")
        print("=" * 70)
        try:
            with open(results_file, "r", encoding="utf-8-sig") as f:
                res = json.load(f)

            print(f"Overall Success: {res.get('OverallSuccess')}")
            print(f"RimWorld Version: {res.get('RimWorldVersion')}")
            print(f"Timestamp: {res.get('Timestamp')}")
            print("\nDetailed Test Entries:")
            for t in res.get("Tests", []):
                status_str = "PASS" if t.get("Passed") else "FAIL"
                print(f"  [{status_str}] {t.get('TestId')} ({t.get('DurationMs', 0):.1f}ms): {t.get('Details')}")

            print("\nReplication Latency & Bandwidth Summary:")
            print(f"  Input -> Worker Receipt:           {res.get('AverageInputToWorkerMs', 0):.2f} ms")
            print(f"  Worker Receipt -> Execution:       {res.get('AverageWorkerExecutionMs', 0):.2f} ms")
            print(f"  Execution -> Client Mirror Update: {res.get('AverageExecutionToClientMs', 0):.2f} ms")
            print(f"  Total Round-Trip Latency:          {res.get('AverageTotalRoundtripMs', 0):.2f} ms")
            print(f"  Average Snapshot Size:             {res.get('AverageSnapshotBytes', 0)} bytes")
            avg_bytes = res.get('AverageSnapshotBytes', 0)
            print(f"  Estimated Bandwidth at 10 Hz:      {avg_bytes * 10 / 1024:.2f} KB/s ({avg_bytes * 80 / 1000:.1f} kbps)")
            print(f"  Estimated Bandwidth at 20 Hz:      {avg_bytes * 20 / 1024:.2f} KB/s ({avg_bytes * 160 / 1000:.1f} kbps)")

            print("\nPeaceful Visit UI Reusability Matrix:")
            matrix = res.get("UIReusabilityMatrix", {})
            for k, v in matrix.items():
                print(f"  {k:28}: {v}")

        except Exception as e:
            print(f"[Error] Failed to read/parse results: {e}")

    # 9. Clean up processes
    print("\n--- 8. Terminating Test Processes ---")
    try:
        client_proc.terminate()
        client_proc.wait(timeout=5)
    except Exception:
        client_proc.kill()

    try:
        worker_proc.terminate()
        worker_proc.wait(timeout=5)
    except Exception:
        worker_proc.kill()

    print("[Done] Cleaned up Worker and Client processes.")

if __name__ == "__main__":
    main()
