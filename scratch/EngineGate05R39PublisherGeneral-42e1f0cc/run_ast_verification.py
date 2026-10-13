#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_ast_verification.py
Pre-pins AST_INPUT_MANIFEST.json, launches isolated ast_checker.py child process,
captures raw stdout/stderr streams, and emits AST_HOST_TOOL_PROOF.json for Gate05 R39.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
OWNED_E1_ROOT = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R39PublisherGeneral-42e1f0cc")
TARGET_PUBLISHER = os.path.join(WORKSPACE_ROOT, r"scratch\OperatorStartupPairR29\publish_operator_pair.py")
CHECKER_SCRIPT = os.path.join(OWNED_E1_ROOT, "ast_checker.py")

DISPATCH_ID = "WE-A-ENGINE-GATE05-R39-PUBLISHER-GENERAL-20261014-DIRECT-42e1f0cc"
WP_ID = "WP_ENGINE_GATE05_R39_PUBLISHER_GENERAL"
WP_REVISION = "GATE05-R39-PUBLISHER-GENERAL"
ENVELOPE = 42

def compute_sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_info(path: str) -> dict:
    return {
        "path": os.path.abspath(path),
        "bytes": os.path.getsize(path),
        "sha256": compute_sha256_file(path)
    }

def main():
    print("=== STARTING GATE05 R39 AST VERIFICATION ===")
    
    # 1. Inspect targets and tools
    target_info = get_file_info(TARGET_PUBLISHER)
    checker_info = get_file_info(CHECKER_SCRIPT)
    py_exe = sys.executable
    py_info = get_file_info(py_exe)
    
    # Pre-execution plan
    plan_argv = [py_exe, os.path.abspath(CHECKER_SCRIPT), os.path.abspath(TARGET_PUBLISHER)]
    plan_cwd = os.path.abspath(OWNED_E1_ROOT)
    
    selected_env = {
        "PYTHONHOME": os.environ.get("PYTHONHOME", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "PYTHONIOENCODING": os.environ.get("PYTHONIOENCODING", ""),
        "PYTHONUTF8": os.environ.get("PYTHONUTF8", ""),
        "PATH_SAMPLE": os.environ.get("PATH", "")[:250] + "..." if len(os.environ.get("PATH", "")) > 250 else os.environ.get("PATH", "")
    }
    
    # Sampled loaded modules in launcher (explicitly labeled as sample with actual count)
    loaded_mods = sorted(list(sys.modules.keys()))
    modules_sample = loaded_mods[:25]
    
    input_manifest_data = {
        "schema_version": 1,
        "dispatch_id": DISPATCH_ID,
        "wp_id": WP_ID,
        "envelope": ENVELOPE,
        "pre_pinned_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_file": target_info,
        "checker_script": checker_info,
        "python_interpreter": {
            "executable": py_info["path"],
            "bytes": py_info["bytes"],
            "sha256": py_info["sha256"],
            "version": sys.version,
            "version_info": list(sys.version_info)
        },
        "execution_plan": {
            "argv": plan_argv,
            "cwd": plan_cwd,
            "selected_env": selected_env,
            "launcher_modules_total_count": len(loaded_mods),
            "launcher_modules_sample_count": len(modules_sample),
            "launcher_modules_sample": modules_sample,
            "sample_label": "FIRST_25_LAUNCHER_MODULES_SAMPLE"
        }
    }
    
    # 2. Write AST_INPUT_MANIFEST.json BEFORE execution
    input_manifest_path = os.path.join(OWNED_E1_ROOT, "AST_INPUT_MANIFEST.json")
    with open(input_manifest_path, "w", encoding="utf-8") as f:
        json.dump(input_manifest_data, f, indent=2)
    print(f"[PINNED] Emitted AST_INPUT_MANIFEST.json: {input_manifest_path}")
    
    # 3. Launch isolated child process
    start_dt = datetime.now(timezone.utc)
    t0 = time.perf_counter()
    
    proc = subprocess.Popen(
        plan_argv,
        cwd=plan_cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
    )
    
    raw_stdout, raw_stderr = proc.communicate()
    t1 = time.perf_counter()
    end_dt = datetime.now(timezone.utc)
    duration_ms = (t1 - t0) * 1000.0
    exit_code = proc.returncode
    pid = proc.pid
    
    print(f"[EXEC] Child finished: PID {pid}, exit code {exit_code}, duration {duration_ms:.2f} ms")
    
    # 4. Save raw stdout and stderr streams
    stdout_path = os.path.join(OWNED_E1_ROOT, "ast_stdout.raw.bin")
    stderr_path = os.path.join(OWNED_E1_ROOT, "ast_stderr.raw.bin")
    with open(stdout_path, "wb") as f:
        f.write(raw_stdout)
    with open(stderr_path, "wb") as f:
        f.write(raw_stderr)
        
    stdout_sha = hashlib.sha256(raw_stdout).hexdigest().upper()
    stderr_sha = hashlib.sha256(raw_stderr).hexdigest().upper()
    
    parsed_stdout_json = None
    if exit_code == 0:
        try:
            parsed_stdout_json = json.loads(raw_stdout.decode("utf-8"))
        except Exception as ex:
            print(f"[WARN] Could not parse child stdout as JSON: {ex}")
            
    # 5. Emit AST_HOST_TOOL_PROOF.json
    proof_data = {
        "schema_version": 1,
        "dispatch_id": DISPATCH_ID,
        "wp_id": WP_ID,
        "envelope": ENVELOPE,
        "execution": {
            "pid": pid,
            "exit_code": exit_code,
            "start_at_utc": start_dt.isoformat(),
            "end_at_utc": end_dt.isoformat(),
            "duration_ms": duration_ms
        },
        "target_file": target_info,
        "raw_streams": {
            "stdout_path": stdout_path,
            "stdout_bytes": len(raw_stdout),
            "stdout_sha256": stdout_sha,
            "stderr_path": stderr_path,
            "stderr_bytes": len(raw_stderr),
            "stderr_sha256": stderr_sha
        },
        "child_report": parsed_stdout_json,
        "verdict": "AST_PARSED_SUCCESS" if exit_code == 0 else "AST_PARSED_FAILED"
    }
    
    proof_path = os.path.join(OWNED_E1_ROOT, "AST_HOST_TOOL_PROOF.json")
    with open(proof_path, "w", encoding="utf-8") as f:
        json.dump(proof_data, f, indent=2)
    print(f"[PROOF] Emitted AST_HOST_TOOL_PROOF.json: {proof_path}")
    
    if exit_code != 0:
        print(f"[FAIL] AST verification failed with exit code {exit_code}!")
        sys.exit(1)
        
    print("=== AST VERIFICATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
