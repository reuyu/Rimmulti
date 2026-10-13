import os
import sys
import time
import json
import socket
import shutil
import hashlib
import subprocess
from pathlib import Path

WORKSPACE = Path(r"c:\Users\user\Desktop\RimMulti")
SCRATCH = WORKSPACE / "scratch"
EXE = Path(r"C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe")
SAVES_DIR = Path(os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves"))

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

def launch_worker(profile, bridge_port=29500):
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

def main():
    clean_b = SCRATCH / "TargetSettlement_Clean_ContextB.rws"
    prof = prepare_profile("Profile_Test_V4", clean_b, "Input")
    port = 29500

    print(f"Launching worker on port {port}...")
    proc, client, elapsed = launch_worker(prof, port)

    print("Connected to worker!")
    fp = client.send("GET_PROFILE_FINGERPRINT")
    print(f"Profile fingerprint response: {fp}")

    actual_fp = fp.split(":")[-1].strip()
    print(f"Parsed profile fingerprint: {actual_fp}")

    clean_manifest_hash = "9F7AA0CDAD9026DC90D25C6209D802D351C0B978D804CD2A04F667543E31E8CC"
    auth = {
        "authorityId": "AUTH-TEST-VALID",
        "expectedSourceArtifactHash": hashlib.sha256(clean_b.read_bytes()).hexdigest().upper(),
        "manifestVersion": "4.0",
        "expectedManifestHash": clean_manifest_hash,
        "contentProfileFingerprint": actual_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "SIMULATION"
    }
    reg_res = client.send(f"REGISTER_AUTHORITY {json.dumps(auth)}")
    print(f"Register authority: {reg_res}")

    grant = {
        "grantId": "GRANT-TEST-001",
        "authorityId": "AUTH-TEST-VALID",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "SIMULATION",
        "executionClass": "STANDARD",
        "tickBudget": 1000
    }
    reg_grant = client.send(f"REGISTER_GRANT {json.dumps(grant)}")
    print(f"Register grant: {reg_grant}")

    load_res = client.send("LOAD_SAVE Input 0")
    print(f"Load save: {load_res}")

    t0 = time.monotonic()
    while time.monotonic() - t0 < 60:
        st = client.send("STATUS")
        if "READY" in st:
            print(f"Worker reached READY: {st}")
            break
        time.sleep(1)

    val_res = client.send("VALIDATE_INPUT")
    print(f"Validate input: {val_res}")
    assert "INPUT_VALIDATED" in val_res, f"Expected INPUT_VALIDATED, got {val_res}"

    # Seal result
    seal_res = client.send("SEAL_RESULT GRANT-TEST-001")
    print(f"Seal result: {seal_res}")
    assert "RESULT_SEALED" in seal_res, f"Expected RESULT_SEALED, got {seal_res}"

    # Stage save
    stage_res = client.send("STAGE_SAVE Staged_Test")
    print(f"Stage save: {stage_res}")
    assert "STAGED_OK" in stage_res, f"Expected STAGED_OK, got {stage_res}"

    stage_kv = parse_kv_response(stage_res)
    staged_file_path = Path(stage_kv["File"])
    staging_name = stage_kv["StagingName"]
    staged_sha = stage_kv["StagedSha"]
    print(f"Staged file on disk: {staged_file_path}, SHA={staged_sha}, StagingName={staging_name}")

    # Launch FRESH PRE-PROMOTION VALIDATOR process!
    print("Launching fresh pre-promotion validator process...")
    val_prof = prepare_profile("Profile_Validator", staged_file_path, staging_name)
    val_proc, val_client, val_ms = launch_worker(val_prof, bridge_port=29510)
    print(f"Fresh validator launched (PID={val_proc.pid})")

    # Get sealed result JSON from worker
    sealed_json_str = client.send("GET_SEALED_RESULT")
    sealed_res_obj = json.loads(sealed_json_str)
    sealed_manifest_hash = sealed_res_obj["sealedManifestHash"]
    import base64
    sealed_b64 = base64.b64encode(sealed_json_str.encode('utf-8')).decode('ascii')

    # Register Authority on Validator derived from Sealed Result
    val_auth = {
        "authorityId": "AUTH-TEST-VALID",
        "expectedSourceArtifactHash": staged_sha,
        "manifestVersion": "4.0",
        "expectedManifestHash": sealed_manifest_hash,
        "contentProfileFingerprint": actual_fp,
        "workerGeneration": 1,
        "targetMapId": 0,
        "allowedOperationMode": "READ_ONLY"
    }
    val_reg = val_client.send(f"REGISTER_AUTHORITY {json.dumps(val_auth)}")
    print(f"Validator register authority: {val_reg}")

    # Register Grant on Validator (READ_ONLY)
    val_grant = {
        "grantId": "GRANT-VAL-001",
        "authorityId": "AUTH-TEST-VALID",
        "workerGeneration": 1,
        "scopeId": "SETTLEMENT-B",
        "targetMapIndex": 0,
        "allowedMode": "READ_ONLY",
        "executionClass": "VALIDATOR",
        "tickBudget": 0
    }
    val_grant_reg = val_client.send(f"REGISTER_GRANT {json.dumps(val_grant)}")
    print(f"Validator register grant: {val_grant_reg}")

    # Load Staged Save in Validator
    val_load = val_client.send(f"LOAD_SAVE {staging_name} 0")
    print(f"Validator load staged save: {val_load}")

    # Wait for Validator to reach READY
    t0 = time.monotonic()
    while time.monotonic() - t0 < 60:
        st = val_client.send("STATUS")
        if "READY" in st:
            print(f"Validator reached READY: {st}")
            break
        time.sleep(1)

    # Validate Input in Validator
    val_inp = val_client.send("VALIDATE_INPUT")
    print(f"Validator input validation: {val_inp}")
    assert "INPUT_VALIDATED" in val_inp, f"Validator input validation failed: {val_inp}"

    # Invoke VALIDATE_AS_PRE_PROMOTION_VALIDATOR on validator process
    val_cmd = f"VALIDATE_AS_PRE_PROMOTION_VALIDATOR AUTH-TEST-VALID {sealed_b64} {str(staged_file_path)} {staged_sha}"
    validator_eval_res = val_client.send(val_cmd)
    print(f"Fresh validator evaluation: {validator_eval_res}")
    assert "STAGE_VALIDATED" in validator_eval_res, f"Validator failed: {validator_eval_res}"

    # Extract receipt JSON
    receipt_json_str = validator_eval_res.split("Receipt=")[-1].strip()
    receipt_obj = json.loads(receipt_json_str)
    print(f"Receipt issued: ID={receipt_obj['receiptId']}, ValidatorPID={receipt_obj['validatorProcessId']}, Result={receipt_obj['validatorResult']}")

    # Shut down validator process
    val_client.send("SHUTDOWN")
    val_client.close()
    val_proc.wait(timeout=10)

    # Submit receipt to main worker
    submit_res = client.send(f"SUBMIT_STAGE_VALIDATION_RECEIPT {json.dumps(receipt_obj)}")
    print(f"Submit receipt: {submit_res}")
    assert "STAGE_VALIDATION_ACCEPTED" in submit_res, f"Receipt rejected: {submit_res}"

    # Promote staged
    prom_res = client.send(f"PROMOTE_STAGED {staging_name} TargetSettlement_Final")
    print(f"Promote staged: {prom_res}")
    assert "ARTIFACT_APPROVED" in prom_res, f"Promotion failed: {prom_res}"
    print("SUCCESS! Full Gate 04 positive flow verified end-to-end!")

    # Also test SHUTDOWN
    client.send("SHUTDOWN")
    client.close()
    proc.wait(timeout=10)
    print("Worker shut down cleanly.")

if __name__ == "__main__":
    main()
