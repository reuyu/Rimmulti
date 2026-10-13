#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_ast_verification.py
Pins inputs (including interpreter EXE SHA-256, bytes, version, sys.path, and default modules),
executes AST verification tool, and captures telemetry and raw binary streams.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

owned_root = r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R36PublisherContract-d2d6556b"
target_source = r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py"
helper_script = os.path.join(owned_root, "ast_checker.py")

# Compute hashes before execution
with open(target_source, "rb") as f:
    source_bytes = f.read()
source_sha = hashlib.sha256(source_bytes).hexdigest().upper()

with open(helper_script, "rb") as f:
    helper_bytes = f.read()
helper_sha = hashlib.sha256(helper_bytes).hexdigest().upper()

with open(sys.executable, "rb") as f:
    interpreter_bytes = f.read()
interpreter_sha = hashlib.sha256(interpreter_bytes).hexdigest().upper()

argv = [sys.executable, "-B", helper_script, target_source]

input_manifest = {
    "pinned_at": datetime.now(timezone.utc).isoformat(),
    "exact_final_source": {
        "path": os.path.abspath(target_source),
        "bytes": len(source_bytes),
        "sha256": source_sha
    },
    "interpreter_exe": {
        "path": os.path.abspath(sys.executable),
        "bytes": len(interpreter_bytes),
        "sha256": interpreter_sha,
        "version": sys.version
    },
    "helper": {
        "path": os.path.abspath(helper_script),
        "bytes": len(helper_bytes),
        "sha256": helper_sha
    },
    "argv": argv,
    "cwd": os.path.abspath(owned_root),
    "sys_path": sys.path,
    "default_modules": sorted(list(sys.modules.keys()))
}

input_manifest_path = os.path.join(owned_root, "AST_INPUT_MANIFEST.json")
with open(input_manifest_path, "w", encoding="utf-8") as f:
    json.dump(input_manifest, f, indent=2)

print(f"Pinned AST_INPUT_MANIFEST.json at {input_manifest_path}")

# Execute AST checker
start_time = datetime.now(timezone.utc)
t0 = time.perf_counter()

proc = subprocess.Popen(
    argv,
    cwd=owned_root,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

pid = proc.pid
stdout_bytes, stderr_bytes = proc.communicate()
t1 = time.perf_counter()
end_time = datetime.now(timezone.utc)
exit_code = proc.returncode

# Save raw binary streams
stdout_bin_path = os.path.join(owned_root, "ast_stdout.raw.bin")
stderr_bin_path = os.path.join(owned_root, "ast_stderr.raw.bin")

with open(stdout_bin_path, "wb") as f:
    f.write(stdout_bytes)

with open(stderr_bin_path, "wb") as f:
    f.write(stderr_bytes)

stdout_sha = hashlib.sha256(stdout_bytes).hexdigest().upper()
stderr_sha = hashlib.sha256(stderr_bytes).hexdigest().upper()

parsed_stdout = {}
try:
    parsed_stdout = json.loads(stdout_bytes.decode("utf-8"))
except Exception as ex:
    parsed_stdout = {"raw_text": stdout_bytes.decode("utf-8", errors="replace"), "error": str(ex)}

tool_proof = {
    "tool_name": "ast_checker.py",
    "executed_at_utc": start_time.isoformat(),
    "completed_at_utc": end_time.isoformat(),
    "duration_seconds": t1 - t0,
    "pid": pid,
    "exit_code": exit_code,
    "command": argv,
    "cwd": os.path.abspath(owned_root),
    "input_source": {
        "path": os.path.abspath(target_source),
        "bytes": len(source_bytes),
        "sha256": source_sha
    },
    "interpreter_exe": {
        "path": os.path.abspath(sys.executable),
        "bytes": len(interpreter_bytes),
        "sha256": interpreter_sha
    },
    "stdout": {
        "raw_path": os.path.abspath(stdout_bin_path),
        "bytes": len(stdout_bytes),
        "sha256": stdout_sha,
        "parsed": parsed_stdout
    },
    "stderr": {
        "raw_path": os.path.abspath(stderr_bin_path),
        "bytes": len(stderr_bytes),
        "sha256": stderr_sha
    },
    "ast_verdict": "SYNTAX_PASS" if exit_code == 0 else "SYNTAX_FAIL"
}

tool_proof_path = os.path.join(owned_root, "AST_HOST_TOOL_PROOF.json")
with open(tool_proof_path, "w", encoding="utf-8") as f:
    json.dump(tool_proof, f, indent=2)

print(f"Wrote AST_HOST_TOOL_PROOF.json at {tool_proof_path}")
print(f"AST Verification Result: Exit Code {exit_code}, PID {pid}, Verdict: {tool_proof['ast_verdict']}")
