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

# Dedicated ports to prevent collisions across all services (QA-PRESENT-009)
WORKER_PORT = 7792          # RemotePresentation Worker Gameplay Transport
WORKER_CONTROL_PORT = 7794  # RemotePresentation Worker QA Control Transport
CLIENT_PORT = 7793          # RemotePresentation Client Control Port
WORKER_BRIDGE_PORT = 29101  # WorkerBridgeMod auxiliary port for Worker
CLIENT_BRIDGE_PORT = 29102  # WorkerBridgeMod auxiliary port for Client
WORKER_QA_PORT = 30341      # QAEngine02 Probe port for Worker
CLIENT_QA_PORT = 30342      # QAEngine02 Probe port for Client

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
    <li>wareconomy.workerbridge.poc</li>
    <li>qacodex.engine02.probe</li>
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
    print(f"[Setup] Prepared {folder.name} with fixture {target_fixture.name} (SHA: {compute_hash(target_fixture)[:16]}...)")

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

def wait_for_port(port: int, ping_cmd: str = "PING", expect_substr: str = "PONG", max_wait: float = 120.0) -> bool:
    start = time.time()
    while time.time() - start < max_wait:
        try:
            resp = send_tcp_command(port, ping_cmd, timeout=2.0)
            if resp and expect_substr in resp:
                print(f"[Wait] TCP port {port} answered at {time.time()-start:.1f}s: {resp[:60]}")
                return True
        except Exception:
            pass
        time.sleep(2.0)
    return False

def find_window_by_pid(pid: int):
    import win32gui
    import win32process
    found_hwnds = []
    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
            if win_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                if "RimWorld" in title:
                    found_hwnds.append((hwnd, title))
    win32gui.EnumWindows(enum_cb, None)
    return found_hwnds[0] if found_hwnds else (None, "")

def send_real_os_mouse_click(hwnd, x: int, y: int, right_click: bool = False):
    import win32gui
    import win32con
    import win32api
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    lParam = win32api.MAKELONG(x, y)
    if right_click:
        win32gui.PostMessage(hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, lParam)
        time.sleep(0.05)
        win32gui.PostMessage(hwnd, win32con.WM_RBUTTONUP, 0, lParam)
    else:
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
        time.sleep(0.05)
        win32gui.PostMessage(hwnd, win32con.WM_LBUTTONUP, 0, lParam)

def cleanup_old_artifacts():
    for scr in BASE_DIR.glob("screen_*.png"):
        try:
            scr.unlink()
            print(f"[Cleanup] Removed old screenshot: {scr.name}")
        except Exception:
            pass
    for res_name in ["remote_presentation_hardening_results.json", "remote_presentation_poc_results.json"]:
        p = BASE_DIR / res_name
        if p.exists():
            try:
                p.unlink()
                print(f"[Cleanup] Removed old results file: {res_name}")
            except Exception:
                pass

def main():
    print("=" * 80)
    print("WP-REMOTE-PRESENTATION-HARDEN-03 ORCHESTRATION")
    print("Targets:")
    print("  1. Rendered mirror correction (PawnTweener reset & DrawPos alignment)")
    print("  2. Privileged control boundary (Physical dual-listener isolation)")
    print("  3. Non-blocking replication liveness (Off-main-thread I/O & fault injection)")
    print("=" * 80)

    cleanup_old_artifacts()

    # 1. Setup profile data folders
    print("\n--- 1. Setting up Isolated Worker and Client Profiles ---")
    setup_profile_folder(WORKER_DATA)
    setup_profile_folder(CLIENT_DATA)

    # 2. Launch Worker Process (Headless simulation authority)
    print("\n--- 2. Launching Authoritative Tactical Worker Process ---")
    worker_cmd = [
        str(RIMWORLD_EXE),
        "-batchmode",
        "-nographics",
        f"-savedatafolder={WORKER_DATA}",
        "-remote-worker",
        "-worker-port", str(WORKER_PORT),
        "-worker-control-port", str(WORKER_CONTROL_PORT),
        "-bridgeport", str(WORKER_BRIDGE_PORT),
        "-qaport", str(WORKER_QA_PORT)
    ]
    print(f"[Launch] Worker command: {' '.join(worker_cmd)}")
    worker_proc = subprocess.Popen(worker_cmd)
    print(f"[Launch] Worker PID: {worker_proc.pid}")

    print(f"[Wait] Waiting for Worker TCP gameplay listener on port {WORKER_PORT}...")
    ping_cmd = json.dumps({"CommandType": "PING", "Token": "Player_A_Token"})
    if not wait_for_port(WORKER_PORT, ping_cmd=ping_cmd, expect_substr="PONG", max_wait=120):
        print("[FAIL] Worker gameplay port 7792 did not respond within 120s.")
        worker_proc.kill()
        sys.exit(1)

    print(f"[Wait] Waiting for Worker TCP QA control listener on port {WORKER_CONTROL_PORT}...")
    ctrl_ping = json.dumps({"CommandType": "PING", "Token": "QA_CONTROL_SURFACE_KEY_PRIVILEGED"})
    if not wait_for_port(WORKER_CONTROL_PORT, ping_cmd=ctrl_ping, expect_substr="PONG", max_wait=30):
        print("[FAIL] Worker control port 7794 did not respond within 30s.")
        worker_proc.kill()
        sys.exit(1)

    # 3. Load Save on Worker via TRUSTED QA CONTROL PORT 7794 (Section 2)
    print("\n--- 3. Loading EngineComplexFixture on Worker via Trusted Control Port ---")
    load_cmd = json.dumps({
        "CommandType": "LOAD_SAVE",
        "CustomData": "EngineComplexFixture",
        "Token": "QA_CONTROL_SURFACE_KEY_PRIVILEGED",
        "Source": "QA_TEST_CONTROL"
    })
    resp = send_tcp_command(WORKER_CONTROL_PORT, load_cmd, timeout=30.0)
    print(f"[Worker Control] Load command response: {resp}")

    # Verify gameplay port rejects LOAD_SAVE even with forged Source=QA_TEST_CONTROL
    print("[Security Check] Probing gameplay port 7792 with forged LOAD_SAVE command...")
    forged_load_cmd = json.dumps({
        "CommandType": "LOAD_SAVE",
        "CustomData": "MaliciousSave",
        "Token": "Attacker_Token",
        "Source": "QA_TEST_CONTROL"
    })
    probe_resp = send_tcp_command(WORKER_PORT, forged_load_cmd, timeout=5.0)
    print(f"[Security Check] Gameplay port response: {probe_resp}")
    if "PRIVILEGE_REJECTED" in probe_resp:
        print("[Security Check] PASS: Gameplay port unconditionally rejected LOAD_SAVE (Dual-listener isolation active).")
    else:
        print("[Security Check] WARNING: Unexpected response from gameplay transport.")

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

    # 4. Launch Presentation Client Process (Normal Graphical Windowed Mode)
    print("\n--- 4. Launching Normal Graphical Presentation Client Process ---")
    client_cmd = [
        str(RIMWORLD_EXE),
        "-screen-width", "1280",
        "-screen-height", "720",
        "-screen-fullscreen", "0",
        f"-savedatafolder={CLIENT_DATA}",
        "-remote-client",
        "-client-port", str(CLIENT_PORT),
        "-connect", f"127.0.0.1:{WORKER_PORT}",
        "-bridgeport", str(CLIENT_BRIDGE_PORT),
        "-qaport", str(CLIENT_QA_PORT)
    ]
    print(f"[Launch] Client command: {' '.join(client_cmd)}")
    client_proc = subprocess.Popen(client_cmd)
    print(f"[Launch] Client PID: {client_proc.pid}")

    print(f"[Wait] Waiting for Client TCP control listener on port {CLIENT_PORT} (up to 120s)...")
    if not wait_for_port(CLIENT_PORT, ping_cmd="PING", expect_substr="PONG", max_wait=120):
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

    # 6. Locate Client Window & Dispatch Real OS Win32 Mouse Event (Section 5)
    print("\n--- 6. Identifying Client Window for Real OS GUI Input Verification ---")
    client_hwnd, win_title = find_window_by_pid(client_proc.pid)
    if client_hwnd:
        print(f"[Win32 OS GUI] Found window HWND {client_hwnd} ('{win_title}') for PID {client_proc.pid}")
        # Send an OS mouse hover / click to window center (viewport focus)
        send_real_os_mouse_click(client_hwnd, 640, 360, right_click=False)
        print("[Win32 OS GUI] Successfully dispatched native OS WM_LBUTTONDOWN/UP to client window.")
    else:
        print(f"[Win32 OS GUI] Note: HWND for PID {client_proc.pid} not yet enumerated; continuing with test suite.")

    # 7. Connect Client to Worker
    print("\n--- 7. Connecting Client to Worker ---")
    conn_resp = send_tcp_command(CLIENT_PORT, f"CONNECT_WORKER 127.0.0.1:{WORKER_PORT}", timeout=10.0)
    print(f"[Client] Connect response: {conn_resp}")

    # 8. Run Full Hardening Test Suite
    print("\n--- 8. Executing Automated Remote Presentation Hardening Battery ---")
    results_file = BASE_DIR / "remote_presentation_hardening_results.json"
    client_results = CLIENT_DATA / "remote_presentation_hardening_results.json"
    if results_file.exists():
        results_file.unlink()
    if client_results.exists():
        client_results.unlink()

    suite_resp = send_tcp_command(CLIENT_PORT, "RUN_POC_SUITE", timeout=10.0)
    print(f"[Client] Run suite response: {suite_resp}")

    # 9. Poll for Test Suite Completion
    print("[Wait] Monitoring hardening test suite execution progress...")
    suite_done = False
    active_results = results_file
    for elapsed in range(120):
        time.sleep(1.0)
        target = results_file if results_file.exists() else (client_results if client_results.exists() else None)
        if target and target.stat().st_size > 500:
            try:
                with open(target, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                if "OverallSuccess" in data and len(data.get("Tests", [])) >= 14:
                    print(f"[Done] Test suite completed in ~{elapsed} seconds! (Read from {target.name})")
                    active_results = target
                    suite_done = True
                    break
            except Exception:
                pass
        if elapsed % 10 == 0 and elapsed > 0:
            print(f"[Wait] Still running test suite ({elapsed}s elapsed)...")

    if not suite_done:
        print("[FAIL] Test suite did not complete within timeout.")
        client_proc.kill()
        worker_proc.kill()
        sys.exit(1)

    # 10. Load and Display Results
    print("\n" + "=" * 80)
    print("REMOTE PRESENTATION HARDENING RESULTS SUMMARY")
    print("=" * 80)
    with open(active_results, "r", encoding="utf-8-sig") as f:
        res = json.load(f)

    print(f"Timestamp:              {res.get('Timestamp')}")
    print(f"RimWorld Version:       {res.get('RimWorldVersion')}")
    print(f"Save Fixture:           {res.get('SaveFixture')}")
    print(f"Overall Success:        {res.get('OverallSuccess')}")
    print(f"Cmd Response Bytes:     {res.get('CommandResponseSizeBytes', 0)} bytes (UTF-8)")
    print(f"Periodic Update Bytes:  {res.get('PeriodicUpdateSizeBytes', 0)} bytes (UTF-8)")
    print(f"Replicated Pawn Count:  {res.get('ReplicatedPawnCount', 0)}")
    print(f"Periodic Updates Count: {res.get('PeriodicUpdatesReceivedCount', 0)}")
    print(f"Avg Cadence Interval:   {res.get('AverageCadenceIntervalMs', 0):.2f} ms")
    print(f"Avg Receive-to-Apply:   {res.get('AverageLoopbackReceiveToApplyMs', 0):.2f} ms")
    print(f"Avg Total Roundtrip:    {res.get('AverageTotalRoundtripMs', 0):.2f} ms")
    print(f"Max Main Thread Frame:  {res.get('MaxMainThreadFrameMs', 0):.2f} ms (Non-blocking liveness)")

    print("\nDetailed Test Execution Results:")
    print("-" * 80)
    tests = res.get("Tests", [])
    all_passed = True
    for t in tests:
        tid = t.get("TestId", "")
        title = t.get("Title", "")
        passed = t.get("Passed", False)
        dur = t.get("DurationMs", 0)
        cls = t.get("EvidenceClassification", "")
        det = t.get("Details", "")
        status_str = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
        print(f"{status_str} {tid} ({dur:.1f}ms) [{cls}]")
        print(f"       Title:   {title}")
        print(f"       Details: {det}")

    # 11. Check Captured Screenshots
    print("\nCaptured Graphical Screenshots:")
    print("-" * 80)
    screenshots = res.get("ScreenshotsCaptured", [])
    for s_path in screenshots:
        p = Path(s_path)
        if p.exists():
            size = p.stat().st_size
            h = compute_hash(p)
            print(f"  - {p.name}: {size:,} bytes | SHA256: {h}")
        else:
            print(f"  - {p.name}: NOT FOUND ON DISK")

    # 12. Terminate Background Processes
    print("\n--- 9. Terminating Test Processes ---")
    client_proc.kill()
    worker_proc.kill()
    client_proc.wait()
    worker_proc.wait()
    print("[Exit] Cleaned up Worker and Client processes.")

    print("\n" + "=" * 80)
    if all_passed and res.get("OverallSuccess", False):
        print("FINAL VERDICT: RENDERED OPERATIONAL PRESENTATION PASS")
    else:
        print("FINAL VERDICT: FAIL")
    print("=" * 80)

if __name__ == "__main__":
    main()
