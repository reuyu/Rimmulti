#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_r31_battery.py

Executes Gate05R31LifecycleRunner across en-US and de-DE cultures,
collects detailed host process telemetry (PID, exit code, execution times, streams),
verifies all results, and emits HOST_TELEMETRY.json in the R31 owned root.
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
R31_ROOT = os.path.join(WORKSPACE_ROOT, "scratch", "EngineGate05R31Lifecycle-b8d47a10")
RUNNER_EXE = os.path.join(R31_ROOT, "Harness", "bin", "Debug", "net472", "Gate05R31LifecycleRunner.exe")
TASK_DIR = os.path.join(WORKSPACE_ROOT, "Dispatcher", "A_TASKS", "WE-A-ENGINE-GATE05-R31-LIFECYCLE-20261012-DIRECT-b8d47a10")

if not os.path.isfile(RUNNER_EXE):
    raise FileNotFoundError(f"Runner executable not found: {RUNNER_EXE}")

cultures = ["en-US", "de-DE"]
runs_telemetry = []

for cult in cultures:
    sub_dir_name = f"run_{cult.lower().replace('-', '_')}"
    run_dir = os.path.join(R31_ROOT, sub_dir_name)
    os.makedirs(run_dir, exist_ok=True)
    
    cmd = [RUNNER_EXE, "--rundir", run_dir, "--culture", cult]
    print(f"\n[HOST] Launching managed runner for culture '{cult}'...")
    print(f"[HOST] Command: {' '.join(cmd)}")
    
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        cmd,
        cwd=WORKSPACE_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    pid = proc.pid
    stdout_b, stderr_b = proc.communicate()
    stdout = stdout_b.decode("utf-8", errors="replace")
    stderr = stderr_b.decode("utf-8", errors="replace")
    t1 = time.perf_counter()
    duration = t1 - t0
    exit_code = proc.returncode
    
    print(f"[HOST] Process PID: {pid}, Exit code: {exit_code}, Duration: {duration:.4f}s")
    
    # Write stdout/stderr files
    stdout_file = os.path.join(run_dir, "stdout.txt")
    stderr_file = os.path.join(run_dir, "stderr.txt")
    with open(stdout_file, "w", encoding="utf-8") as f:
        f.write(stdout)
    with open(stderr_file, "w", encoding="utf-8") as f:
        f.write(stderr)
        
    report_file = os.path.join(run_dir, "E1_EXECUTION_REPORT.json")
    if not os.path.isfile(report_file):
        raise FileNotFoundError(f"E1_EXECUTION_REPORT.json was not generated in '{run_dir}'. Stderr: {stderr}")
        
    with open(report_file, "r", encoding="utf-8-sig") as f:
        rep_data = json.load(f)
        
    runs_telemetry.append({
        "culture": cult,
        "pid": pid,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 6),
        "argv": cmd,
        "cwd": WORKSPACE_ROOT,
        "run_directory": run_dir,
        "stdout_path": stdout_file,
        "stdout_sha256": hashlib.sha256(stdout.encode("utf-8")).hexdigest().upper(),
        "stderr_path": stderr_file,
        "stderr_sha256": hashlib.sha256(stderr.encode("utf-8")).hexdigest().upper(),
        "execution_report_path": report_file,
        "execution_report_sha256": hashlib.sha256(open(report_file, "rb").read()).hexdigest().upper(),
        "report_summary": rep_data
    })
    
    if exit_code != 0:
        raise RuntimeError(f"Runner failed for culture {cult} with exit code {exit_code}!\nStderr: {stderr}")

# Write HOST_TELEMETRY.json in R31 root
telemetry_path = os.path.join(R31_ROOT, "HOST_TELEMETRY.json")
with open(telemetry_path, "w", encoding="utf-8") as f:
    json.dump({
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "runner_exe": RUNNER_EXE,
        "runner_sha256": hashlib.sha256(open(RUNNER_EXE, "rb").read()).hexdigest().upper(),
        "runs": runs_telemetry
    }, f, indent=2, ensure_ascii=False)
print(f"\n[HOST] Wrote HOST_TELEMETRY.json to {telemetry_path}")
print("[HOST] SUCCESS: All E1 normal test runs completed with exit code 0.")
