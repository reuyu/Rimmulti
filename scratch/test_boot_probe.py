import os
import sys
import time
import socket
import subprocess
import shutil
import hashlib
from pathlib import Path

WORKSPACE = Path(r"c:\Users\user\Desktop\RimMulti")
SCRATCH = WORKSPACE / "scratch"
EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")

def prepare_probe_profile():
    profile = SCRATCH / "Profiles/ProbeProfile"
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

    src_save = SCRATCH / "TargetSettlement_Clean_ContextB.rws"
    shutil.copy2(src_save, profile / "Saves/TargetSettlement_Clean_ContextB.rws")
    return profile

def main():
    profile = prepare_probe_profile()
    port = 29555
    args = [
        str(EXE),
        "-batchmode",
        f"-savedatafolder={profile.resolve()}",
        "-logFile",
        str((profile / "player.log").resolve()),
        f"-bridgeport={port}"
    ]
    print(f"Launching probe instance on port {port}...")
    proc = subprocess.Popen(args)
    try:
        s = None
        for i in range(40):
            try:
                s = socket.create_connection(("127.0.0.1", port), timeout=5)
                break
            except Exception:
                time.sleep(1)
        if not s:
            print("Failed to connect to worker TCP!")
            return 1
        
        file = s.makefile("r", encoding="utf-8")
        def send(cmd):
            s.sendall((cmd + "\n").encode("utf-8"))
            lines = []
            while True:
                line = file.readline()
                if not line: break
                line = line.rstrip("\r\n").lstrip("\ufeff")
                if line == "---END---": break
                lines.append(line)
            return "\n".join(lines)

        print("HELLO response:", send("HELLO"))
        fp_resp = send("GET_PROFILE_FINGERPRINT")
        print("GET_PROFILE_FINGERPRINT response:", fp_resp)
        fp = fp_resp.split(":", 1)[1].strip()

        # Check Authority registration
        src_sha = "EA8A02D4EC41CE79E285A7D386F3534EB5E192682FC061A8E008116B2B3DF34B"
        dummy_hash = "0" * 64
        auth = {
            "authorityId": "AUTH_PROBE_01",
            "expectedSourceArtifactHash": src_sha,
            "manifestVersion": "4.0",
            "expectedManifestHash": dummy_hash,
            "contentProfileFingerprint": fp,
            "targetScopeId": "SETTLEMENT-B",
            "targetMapId": 0,
            "workerGeneration": 1,
            "allowedOperationMode": "SIMULATION",
            "storeIncarnation": "STORE_INC_01",
            "baseLineage": "LINEAGE_BASE_01"
        }
        import json
        print("REGISTER_AUTHORITY:", send(f"REGISTER_AUTHORITY {json.dumps(auth)}"))
        print("LOAD_SAVE:", send("LOAD_SAVE TargetSettlement_Clean_ContextB 0"))

        for _ in range(60):
            st = send("STATUS")
            if "STATE: READY" in st or "STATE: LOAD_FAILED" in st:
                print("Status after load:", st)
                break
            time.sleep(1)

        # Get Census JSON
        census_resp = send("GET_CENSUS_JSON 0")
        if census_resp.startswith("{"):
            print("Successfully received Census JSON! Length:", len(census_resp))
            (SCRATCH / "TargetSettlement_Clean_ContextB.v4.census.json").write_text(census_resp, encoding="utf-8")
            # Calculate hash from census JSON
            import hashlib
            census_data = json.loads(census_resp)
            # Live recensus hash
            val_input = send("VALIDATE_INPUT")
            print("VALIDATE_INPUT (against dummy):", val_input)

    finally:
        try:
            send("SHUTDOWN")
        except:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
    print("Done probe.")

if __name__ == "__main__":
    sys.exit(main())
