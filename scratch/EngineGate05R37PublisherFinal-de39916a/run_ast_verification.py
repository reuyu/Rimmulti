# -*- coding: utf-8 -*-
"""
run_ast_verification.py
Launcher script for Gate05 R37 AST syntax verification.
Pins AST_INPUT_MANIFEST.json before execution.
Runs ast_checker.py as a standalone child process.
Captures raw binary streams (ast_stdout.raw.bin, ast_stderr.raw.bin), PID, exit code,
and writes AST_HOST_TOOL_PROOF.json.
"""
import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
OWNED_DIR = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R37PublisherFinal-de39916a")
TARGET_PATH = os.path.join(WORKSPACE_ROOT, r"scratch\OperatorStartupPairR29\publish_operator_pair.py")
CHECKER_PATH = os.path.join(OWNED_DIR, "ast_checker.py")
INTERPRETER_PATH = sys.executable

def compute_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_stats(path):
    size = os.path.getsize(path)
    sha = compute_sha256(path)
    return size, sha

# Pre-pin AST_INPUT_MANIFEST.json
target_size, target_sha = get_file_stats(TARGET_PATH)
interp_size, interp_sha = get_file_stats(INTERPRETER_PATH)
checker_size, checker_sha = get_file_stats(CHECKER_PATH)

child_argv = [INTERPRETER_PATH, CHECKER_PATH, TARGET_PATH]
child_cwd = OWNED_DIR

input_manifest = {
    "schemaVersion": "we-ast-input-manifest/v1",
    "pinned_at_utc": datetime.now(timezone.utc).isoformat(),
    "target_source": {
        "path": TARGET_PATH,
        "bytes": target_size,
        "sha256": target_sha
    },
    "interpreter": {
        "executable_path": INTERPRETER_PATH,
        "bytes": interp_size,
        "sha256": interp_sha,
        "version": sys.version
    },
    "child_tool_script": {
        "path": CHECKER_PATH,
        "bytes": checker_size,
        "sha256": checker_sha
    },
    "child_argv": child_argv,
    "child_cwd": child_cwd,
    "launcher_sys_path": sys.path,
    "launcher_modules_loaded": sorted(list(sys.modules.keys()))
}

manifest_path = os.path.join(OWNED_DIR, "AST_INPUT_MANIFEST.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(input_manifest, f, indent=2)

print(f"Pre-pinned AST_INPUT_MANIFEST.json ({manifest_path})")

# Execute child process
start_time = datetime.now(timezone.utc).isoformat()
proc = subprocess.Popen(
    child_argv,
    cwd=child_cwd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

pid = proc.pid
stdout_bytes, stderr_bytes = proc.communicate()
exit_code = proc.returncode
end_time = datetime.now(timezone.utc).isoformat()

stdout_path = os.path.join(OWNED_DIR, "ast_stdout.raw.bin")
stderr_path = os.path.join(OWNED_DIR, "ast_stderr.raw.bin")

with open(stdout_path, "wb") as f:
    f.write(stdout_bytes)
with open(stderr_path, "wb") as f:
    f.write(stderr_bytes)

stdout_sha = compute_sha256(stdout_path)
stderr_sha = compute_sha256(stderr_path)

print(f"Child execution completed: PID {pid}, ExitCode {exit_code}")
print(f"stdout: {len(stdout_bytes)} bytes (SHA: {stdout_sha})")
print(f"stderr: {len(stderr_bytes)} bytes (SHA: {stderr_sha})")

child_metadata = {}
if exit_code == 0:
    try:
        child_metadata = json.loads(stdout_bytes.decode("utf-8"))
    except Exception as ex:
        print(f"Warning: Failed to parse stdout JSON: {ex}")

proof = {
    "schemaVersion": "we-ast-host-tool-proof/v1",
    "verified_at_utc": end_time,
    "execution": {
        "pid": pid,
        "start_time_utc": start_time,
        "end_time_utc": end_time,
        "exit_code": exit_code,
        "verdict": "SYNTAX_PASS" if exit_code == 0 else "SYNTAX_FAIL"
    },
    "target_source": {
        "path": TARGET_PATH,
        "bytes": target_size,
        "sha256": target_sha
    },
    "streams": {
        "stdout": {
            "path": stdout_path,
            "bytes": len(stdout_bytes),
            "sha256": stdout_sha
        },
        "stderr": {
            "path": stderr_path,
            "bytes": len(stderr_bytes),
            "sha256": stderr_sha
        }
    },
    "child_observed_ast": {
        "body_node_count": child_metadata.get("body_node_count"),
        "function_count": child_metadata.get("function_count"),
        "functions": child_metadata.get("functions"),
        "class_count": child_metadata.get("class_count"),
        "classes": child_metadata.get("classes"),
        "imports": child_metadata.get("imports")
    },
    "child_observed_environment": {
        "child_sys_path": child_metadata.get("child_sys_path"),
        "child_modules_loaded": child_metadata.get("child_modules_loaded")
    }
}

proof_path = os.path.join(OWNED_DIR, "AST_HOST_TOOL_PROOF.json")
with open(proof_path, "w", encoding="utf-8") as f:
    json.dump(proof, f, indent=2)

print(f"Emitted AST_HOST_TOOL_PROOF.json ({proof_path})")
