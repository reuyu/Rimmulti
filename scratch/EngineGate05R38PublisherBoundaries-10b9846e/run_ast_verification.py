#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_ast_verification.py
Launcher and host tool proof generator for Gate05 R38 publisher boundaries.
Item 7: Pre-pins prospective input manifest, executes isolated child AST checker,
captures first raw binary stdout/stderr, PID, exit code, start/end timestamps,
and writes AST_HOST_TOOL_PROOF.json.
"""

import os
import sys
import ast
import json
import hashlib
import subprocess
from datetime import datetime, timezone

E1_ROOT = r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R38PublisherBoundaries-10b9846e"
TARGET_PUBLISHER = r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py"
CHILD_SCRIPT = os.path.join(E1_ROOT, "ast_checker.py")
THIS_SCRIPT = os.path.join(E1_ROOT, "run_ast_verification.py")

def compute_sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()

def get_file_info(path: str) -> dict:
    with open(path, "rb") as f:
        data = f.read()
    return {
        "path": os.path.abspath(path),
        "size_bytes": len(data),
        "sha256": compute_sha256(data)
    }

def main():
    print("=== STARTING R38 AST VERIFICATION GRAPH ===")
    
    # 1. Syntax precheck of helpers before executing
    helpers_to_check = [
        CHILD_SCRIPT,
        THIS_SCRIPT,
        os.path.join(E1_ROOT, "generate_r38_publisher.py"),
        os.path.join(E1_ROOT, "verify_refs_and_emit_ack.py")
    ]
    for h in helpers_to_check:
        if os.path.isfile(h):
            with open(h, "rb") as f:
                content = f.read()
            ast.parse(content, filename=h)
            print(f"[PRECHECK] Syntax valid: {os.path.basename(h)}")
            
    # 2. Gather prospective inputs
    publisher_info = get_file_info(TARGET_PUBLISHER)
    print(f"[TARGET] {publisher_info['path']} ({publisher_info['size_bytes']} B, SHA {publisher_info['sha256']})")
    
    child_info = get_file_info(CHILD_SCRIPT)
    launcher_info = get_file_info(THIS_SCRIPT)
    
    exe_path = sys.executable
    exe_info = get_file_info(exe_path)
    
    # Observe launcher modules
    launcher_module_obs = []
    for mod_name, mod in sorted(sys.modules.items()):
        fpath = getattr(mod, "__file__", None)
        if fpath and os.path.isfile(fpath):
            try:
                mod_finfo = get_file_info(fpath)
                launcher_module_obs.append({
                    "module": mod_name,
                    "path": mod_finfo["path"],
                    "size_bytes": mod_finfo["size_bytes"],
                    "sha256": mod_finfo["sha256"]
                })
            except Exception:
                pass
                
    argv_plan = [exe_path, CHILD_SCRIPT, TARGET_PUBLISHER]
    cwd_plan = r"C:\Users\user\Desktop\RimMulti"
    
    prospective_manifest = {
        "schemaVersion": "we-ast-input-manifest/v1",
        "pinnedAtUtc": datetime.now(timezone.utc).isoformat(),
        "targetPublisher": publisher_info,
        "childScript": child_info,
        "launcherScript": launcher_info,
        "pythonInterpreter": {
            "executablePath": exe_info["path"],
            "sizeBytes": exe_info["size_bytes"],
            "sha256": exe_info["sha256"],
            "version": sys.version
        },
        "plannedExecution": {
            "argv": argv_plan,
            "cwd": cwd_plan,
            "selectedEnv": {
                "PYTHONIOENCODING": os.environ.get("PYTHONIOENCODING", "N/A"),
                "PYTHONUTF8": os.environ.get("PYTHONUTF8", "N/A")
            }
        },
        "launcherModuleObservationsCount": len(launcher_module_obs),
        "launcherModuleObservations": launcher_module_obs[:20]  # sample of stdlib modules
    }
    
    manifest_path = os.path.join(E1_ROOT, "AST_INPUT_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(prospective_manifest, f, indent=2, ensure_ascii=False)
    print(f"[PINNED] Pinned prospective input manifest: {manifest_path}")
    
    # 3. Launch isolated child process
    start_dt = datetime.now(timezone.utc)
    start_iso = start_dt.isoformat()
    
    proc = subprocess.Popen(
        argv_plan,
        cwd=cwd_plan,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    pid = proc.pid
    stdout_bytes, stderr_bytes = proc.communicate()
    exit_code = proc.returncode
    
    end_dt = datetime.now(timezone.utc)
    end_iso = end_dt.isoformat()
    duration_ms = int((end_dt - start_dt).total_seconds() * 1000)
    
    print(f"[CHILD] PID={pid}, ExitCode={exit_code}, Duration={duration_ms}ms")
    print(f"[CHILD] Stdout bytes={len(stdout_bytes)}, Stderr bytes={len(stderr_bytes)}")
    
    # 4. Save raw streams
    stdout_bin_path = os.path.join(E1_ROOT, "ast_stdout.raw.bin")
    stderr_bin_path = os.path.join(E1_ROOT, "ast_stderr.raw.bin")
    
    with open(stdout_bin_path, "wb") as f:
        f.write(stdout_bytes)
    with open(stderr_bin_path, "wb") as f:
        f.write(stderr_bytes)
        
    # 5. Parse child stdout JSON
    child_json = None
    if exit_code == 0:
        try:
            child_json = json.loads(stdout_bytes.decode("utf-8"))
        except Exception as ex:
            print(f"[WARN] Failed to parse child stdout JSON: {ex}")
            
    # 6. Write AST_HOST_TOOL_PROOF.json
    proof = {
        "schemaVersion": "we-ast-host-tool-proof/v1",
        "createdAtUtc": end_iso,
        "inputManifestPath": manifest_path,
        "inputManifestSha256": compute_sha256(open(manifest_path, "rb").read()),
        "targetPublisher": publisher_info,
        "childExecution": {
            "pid": pid,
            "exitCode": exit_code,
            "startedAtUtc": start_iso,
            "completedAtUtc": end_iso,
            "durationMs": duration_ms,
            "stdoutRawPath": stdout_bin_path,
            "stdoutRawBytes": len(stdout_bytes),
            "stdoutRawSha256": compute_sha256(stdout_bytes),
            "stderrRawPath": stderr_bin_path,
            "stderrRawBytes": len(stderr_bytes),
            "stderrRawSha256": compute_sha256(stderr_bytes),
            "childVerdict": child_json.get("status") if child_json else "UNKNOWN"
        },
        "astVerificationSummary": child_json
    }
    
    proof_path = os.path.join(E1_ROOT, "AST_HOST_TOOL_PROOF.json")
    with open(proof_path, "w", encoding="utf-8") as f:
        json.dump(proof, f, indent=2, ensure_ascii=False)
    print(f"[PROOF] Wrote AST host tool proof: {proof_path}")
    
    if exit_code == 0 and child_json and child_json.get("status") == "AST_PARSED_SUCCESS":
        print("=== R38 AST VERIFICATION SUCCESSFUL ===")
    else:
        print("=== R38 AST VERIFICATION FAILED ===")
        sys.exit(1)

if __name__ == "__main__":
    main()
