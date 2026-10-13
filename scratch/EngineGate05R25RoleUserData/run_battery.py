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
    scratch_dir = os.path.join(base_dir, r'scratch\EngineGate05R25RoleUserData')
    harness_exe = os.path.join(scratch_dir, r'Harness\bin\Debug\net472\Gate05R25RoleUserDataRunner.exe')

    if not os.path.exists(harness_exe):
        print(f"ERROR: Harness executable not found at {harness_exe}")
        sys.exit(1)

    print(f"[HOST-ORCHESTRATOR] Initializing Gate05-R25 Role UserData Test Battery Orchestration")
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
        'dispatch_id': 'WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868',
        'wp_id': 'WP_ENGINE_GATE05_R25_ROLE_USERDATA_SELECTION',
        'wp_revision': 'GATE05-R25-ROLE-USERDATA',
        'envelope': 28,
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
    print(f"[HOST-ORCHESTRATOR] Run 1 Exit Code: {exit1} (Duration: {dur1:.3f}s)")

    # Persist stdout & stderr directly
    stdout1_path = os.path.join(run_en_us, 'stdout.txt')
    stderr1_path = os.path.join(run_en_us, 'stderr.txt')
    with open(stdout1_path, 'w', encoding='utf-8') as f:
        f.write(stdout1)
    with open(stderr1_path, 'w', encoding='utf-8') as f:
        f.write(stderr1)

    inv1_path, inv1_items = write_output_inventory(run_en_us)
    print(f"[HOST-ORCHESTRATOR] Run 1 Output Inventory: {len(inv1_items)} artifacts recorded and sealed")

    telemetry['runs'].append({
        'run_index': 1,
        'culture': 'en-US',
        'child_pid': child1_pid,
        'exit_code': exit1,
        'duration_seconds': dur1,
        'run_dir': run_en_us,
        'stdout_path': stdout1_path,
        'stderr_path': stderr1_path,
        'output_inventory_path': inv1_path,
        'output_count': len(inv1_items)
    })

    if exit1 != 0:
        print(f"ERROR: Run 1 failed with exit code {exit1}")
        print("STDOUT:", stdout1)
        print("STDERR:", stderr1)
        sys.exit(1)

    # Snapshot of Run 1 files for post-run isolation check
    run1_snapshot = {item['relative_path']: item['sha256'] for item in inv1_items}

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
    print(f"[HOST-ORCHESTRATOR] Run 2 Exit Code: {exit2} (Duration: {dur2:.3f}s)")

    # Persist stdout & stderr directly
    stdout2_path = os.path.join(run_de_de, 'stdout.txt')
    stderr2_path = os.path.join(run_de_de, 'stderr.txt')
    with open(stdout2_path, 'w', encoding='utf-8') as f:
        f.write(stdout2)
    with open(stderr2_path, 'w', encoding='utf-8') as f:
        f.write(stderr2)

    inv2_path, inv2_items = write_output_inventory(run_de_de)
    print(f"[HOST-ORCHESTRATOR] Run 2 Output Inventory: {len(inv2_items)} artifacts recorded and sealed")

    telemetry['runs'].append({
        'run_index': 2,
        'culture': 'de-DE',
        'child_pid': child2_pid,
        'exit_code': exit2,
        'duration_seconds': dur2,
        'run_dir': run_de_de,
        'stdout_path': stdout2_path,
        'stderr_path': stderr2_path,
        'output_inventory_path': inv2_path,
        'output_count': len(inv2_items)
    })

    if exit2 != 0:
        print(f"ERROR: Run 2 failed with exit code {exit2}")
        print("STDOUT:", stdout2)
        print("STDERR:", stderr2)
        sys.exit(1)

    # Post-run isolation check on Run 1
    print(f"\n[HOST-ORCHESTRATOR] Verifying Run 1 Isolation Post-Run 2...")
    inv1_post = inventory_dir(run_en_us)
    isolation_ok = True
    for rel, sha in run1_snapshot.items():
        if rel not in inv1_post or inv1_post[rel]['sha256'] != sha:
            print(f"ISOLATION VIOLATION: {rel} in Run 1 was mutated during Run 2!")
            isolation_ok = False
    if isolation_ok:
        print(f"[HOST-ORCHESTRATOR] Run 1 artifacts 100% UNTOUCHED during Run 2. Isolation Verified!")
    else:
        sys.exit(1)

    # Post-run runner check
    post_runner_sha = hash_file(harness_exe)
    post_runner_size = os.path.getsize(harness_exe)
    if pre_runner_sha != post_runner_sha:
        print(f"ERROR: Runner binary was modified during test runs! Pre={pre_runner_sha}, Post={post_runner_sha}")
        sys.exit(1)
    print(f"[HOST-ORCHESTRATOR] Runner binary immutable during runs: SHA256 matches.")

    # Save telemetry
    telemetry_path = os.path.join(scratch_dir, 'HOST_TELEMETRY.json')
    with open(telemetry_path, 'w', encoding='utf-8') as f:
        json.dump(telemetry, f, indent=2)
    print(f"[HOST-ORCHESTRATOR] Host telemetry written to {telemetry_path}")
    print(f"[HOST-ORCHESTRATOR] ALL RUNS COMPLETED SUCCESSFULLY.")

if __name__ == '__main__':
    main()
