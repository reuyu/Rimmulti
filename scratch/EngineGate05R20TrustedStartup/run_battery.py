import os
import sys
import json
import time
import hashlib
import subprocess
from datetime import datetime, timezone

def hash_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest().upper()

def inventory_dir(dir_path):
    inv = {}
    for root, dirs, files in os.walk(dir_path):
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, dir_path).replace('\\', '/')
            if rel == 'OUTPUT_INVENTORY.json':
                continue
            size = os.path.getsize(full)
            sha = hash_file(full)
            inv[rel] = {'path': full, 'rel': rel, 'size': size, 'sha256': sha}
    return inv

def write_output_inventory(dir_path):
    inv = inventory_dir(dir_path)
    inv_list = []
    for rel in sorted(inv.keys()):
        item = inv[rel]
        inv_list.append({
            'relative_path': item['rel'],
            'size_bytes': item['size'],
            'sha256': item['sha256']
        })
    inv_path = os.path.join(dir_path, 'OUTPUT_INVENTORY.json')
    with open(inv_path, 'w', encoding='utf-8') as f:
        json.dump(inv_list, f, indent=2)
    return inv_path, inv_list

def main():
    base_dir = r'C:\Users\user\Desktop\RimMulti'
    scratch_dir = os.path.join(base_dir, r'scratch\EngineGate05R20TrustedStartup')
    harness_exe = os.path.join(scratch_dir, r'Harness\bin\Debug\net472\Gate05R20TrustedStartupRunner.exe')

    if not os.path.exists(harness_exe):
        print(f"ERROR: Harness executable not found at {harness_exe}")
        sys.exit(1)

    print(f"[HOST-ORCHESTRATOR] Initializing Gate05-R20 Trusted Startup Pure Test Battery Orchestration")
    print(f"[HOST-ORCHESTRATOR] Pinned Runner: {harness_exe}")

    pre_runner_sha = hash_file(harness_exe)
    pre_runner_size = os.path.getsize(harness_exe)
    print(f"[HOST-ORCHESTRATOR] Pre-Run Runner SHA256: {pre_runner_sha} ({pre_runner_size} bytes)")

    # Output directories
    run_en_us = os.path.join(scratch_dir, 'run_en_us')
    run_de_de = os.path.join(scratch_dir, 'run_de_de')
    os.makedirs(run_en_us, exist_ok=True)
    os.makedirs(run_de_de, exist_ok=True)

    telemetry = {
        'dispatch_id': 'WE-A-ENGINE-GATE05-R20-TRUSTED-STARTUP-20261011-DIRECT-e35ff656',
        'wp_id': 'WP_ENGINE_GATE05_R20_TRUSTED_STARTUP_ORIGIN',
        'wp_revision': 'GATE05-R20-TRUSTED-STARTUP',
        'envelope': 23,
        'orchestrator': 'Python Host Subprocess',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'pinned_runner': {
            'path': harness_exe,
            'sha256': pre_runner_sha,
            'size': pre_runner_size
        },
        'runs': []
    }

    # =========================================================================
    # RUN 1: en-US
    # =========================================================================
    print(f"\n[HOST-ORCHESTRATOR] Starting Run 1 (en-US)...")
    env1 = os.environ.copy()
    env1['DOTNET_CLI_UI_LANGUAGE'] = 'en-US'

    t0_1 = time.time()
    cmd1 = [harness_exe, '--rundir', run_en_us, '--culture', 'en-US']
    proc1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=scratch_dir, env=env1, text=True)
    child1_pid = proc1.pid
    print(f"[HOST-ORCHESTRATOR] Run 1 child PID: {child1_pid}")

    stdout1, stderr1 = proc1.communicate()
    exit1 = proc1.returncode
    t1_1 = time.time()
    dur1 = t1_1 - t0_1
    print(f"[HOST-ORCHESTRATOR] Run 1 completed in {dur1:.3f}s with exit code {exit1}")

    # Write and explicitly close stdout and stderr before inventory
    stdout1_path = os.path.join(run_en_us, 'stdout.txt')
    stderr1_path = os.path.join(run_en_us, 'stderr.txt')
    with open(stdout1_path, 'w', encoding='utf-8') as f:
        f.write(stdout1)
    with open(stderr1_path, 'w', encoding='utf-8') as f:
        f.write(stderr1)

    # Generate complete OUTPUT_INVENTORY.json including closed stdout/stderr
    inv1_path, inv1_items = write_output_inventory(run_en_us)

    telemetry['runs'].append({
        'run_name': 'run_en_us',
        'culture': 'en-US',
        'child_pid': child1_pid,
        'exit_code': exit1,
        'duration_seconds': dur1,
        'output_directory': run_en_us,
        'stdout_path': stdout1_path,
        'stderr_path': stderr1_path,
        'inventory_path': inv1_path,
        'inventory_count': len(inv1_items)
    })

    if exit1 != 0:
        print(f"ERROR: Run 1 failed with exit code {exit1}")
        print("STDOUT:\n" + stdout1)
        print("STDERR:\n" + stderr1)
        sys.exit(1)

    # Re-hash run 1 files before run 2
    inv1_before_run2 = inventory_dir(run_en_us)

    # =========================================================================
    # RUN 2: de-DE
    # =========================================================================
    print(f"\n[HOST-ORCHESTRATOR] Starting Run 2 (de-DE)...")
    env2 = os.environ.copy()
    env2['DOTNET_CLI_UI_LANGUAGE'] = 'de-DE'

    t0_2 = time.time()
    cmd2 = [harness_exe, '--rundir', run_de_de, '--culture', 'de-DE']
    proc2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=scratch_dir, env=env2, text=True)
    child2_pid = proc2.pid
    print(f"[HOST-ORCHESTRATOR] Run 2 child PID: {child2_pid}")

    stdout2, stderr2 = proc2.communicate()
    exit2 = proc2.returncode
    t1_2 = time.time()
    dur2 = t1_2 - t0_2
    print(f"[HOST-ORCHESTRATOR] Run 2 completed in {dur2:.3f}s with exit code {exit2}")

    # Write and explicitly close stdout and stderr before inventory
    stdout2_path = os.path.join(run_de_de, 'stdout.txt')
    stderr2_path = os.path.join(run_de_de, 'stderr.txt')
    with open(stdout2_path, 'w', encoding='utf-8') as f:
        f.write(stdout2)
    with open(stderr2_path, 'w', encoding='utf-8') as f:
        f.write(stderr2)

    # Generate complete OUTPUT_INVENTORY.json including closed stdout/stderr
    inv2_path, inv2_items = write_output_inventory(run_de_de)

    telemetry['runs'].append({
        'run_name': 'run_de_de',
        'culture': 'de-DE',
        'child_pid': child2_pid,
        'exit_code': exit2,
        'duration_seconds': dur2,
        'output_directory': run_de_de,
        'stdout_path': stdout2_path,
        'stderr_path': stderr2_path,
        'inventory_path': inv2_path,
        'inventory_count': len(inv2_items)
    })

    if exit2 != 0:
        print(f"ERROR: Run 2 failed with exit code {exit2}")
        print("STDOUT:\n" + stdout2)
        print("STDERR:\n" + stderr2)
        sys.exit(1)

    # Re-hash run 1 files after run 2 to verify process isolation
    inv1_after_run2 = inventory_dir(run_en_us)

    print(f"\n[HOST-ORCHESTRATOR] Verifying Process Isolation & Immutability...")
    isolation_passed = True
    for k, v in inv1_before_run2.items():
        if k not in inv1_after_run2:
            print(f"ERROR: File {k} missing from run 1 after run 2!")
            isolation_passed = False
        elif inv1_after_run2[k]['sha256'] != v['sha256']:
            print(f"ERROR: File {k} in run 1 modified during run 2!")
            isolation_passed = False

    if isolation_passed:
        print("[HOST-ORCHESTRATOR] Isolation Verified: 100% of run 1 files identical after run 2.")

    telemetry['isolation_verified'] = isolation_passed
    telemetry_path = os.path.join(scratch_dir, 'HOST_TELEMETRY.json')
    with open(telemetry_path, 'w', encoding='utf-8') as f:
        json.dump(telemetry, f, indent=2)

    print(f"[HOST-ORCHESTRATOR] Saved Telemetry: {telemetry_path}")
    print("[HOST-ORCHESTRATOR] All Orchestration Stages Completed Successfully.")

if __name__ == '__main__':
    main()
