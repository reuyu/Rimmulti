# -*- coding: utf-8 -*-
"""
Verification of references and generation of ACK_INITIAL.json, ACK.json, and PRESERVATION_BEFORE.json
for WP_ENGINE_GATE05_R37_PUBLISHER_FINAL (Envelope 40).
"""
import os
import sys
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a")
OWNED_DIR = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R37PublisherFinal-de39916a")

def compute_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_stats(path):
    size = os.path.getsize(path)
    sha = compute_sha256(path)
    return size, sha

refs = [
    ("task", os.path.join(TASK_DIR, "TASK.json"), "TASK.json"),
    ("master_message", os.path.join(TASK_DIR, "MASTER_MESSAGE.txt"), "27D9FF71606EF7375C9B3A710F05611DCFC9F2659E8EC507B6B663BEA2765BDF", 396),
    ("scope", os.path.join(TASK_DIR, "MASTER_R37_AUTHORIZED_SOURCE_SCOPE.json"), "AD8806EE585D30FE3939D3D51BD5AAD5C91A26B527552F398C10946661696F37", 3657),
    ("wp", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R37_PUBLISHER_FINAL.md", "D721B31197FB92B5B32629251450C0164869EAB83255BC3E4855F7A5D6CA8C6B", 4828),
    ("release", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R37_PUBLISHER_FINAL_20261014.md", "EA11EA70F15B4AA7D5D1D8F7FE424DA2B64A3BFE94EFC10760E4D451439F5197", 1342),
    ("contract", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R37_PUBLISHER_FINAL_IMPLEMENTATION_CONTRACT_20261014.md", "8B5B0DD5B71AF36826036BAE70436A65444260949E2BD68EAB7F9054E8DA130C", 6756),
    ("r36_review", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R36_INDEPENDENT_STATIC_S1_20261014.md", "1FF06D43C72F1DDBB8D167F8C3B615B270EAB4C7F1F8CFAAA6FDCA6565951F24", 3981),
    ("qa_s1_report", r"C:\Users\user\Desktop\RimMulti\docs\QA_EngineHost_Gate05_R36_Publisher_Independent_Static_S1_20261014.md", "3D07EF577FEF682CA37F0ACCF1E4649D589D628A5F585182F2823A9429D524A0", 13776),
    ("minimal_r37", r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014\MINIMAL_R37_CORRECTIVE_REQUIREMENTS.json", "107AE68B366D1441126D12C4A5BE7F71FEBF4928CC074AF4C33B51ADAB146089", 2656),
    ("matrix_source", r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R36-PUBLISHER-INDEPENDENT-STATIC-S1-20261014\ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json", "D968B7A4B7077D5C080BFA9CBDCEE9C9F42B4A2F62F97D670CDCEA518A213E0A", 48785),
    ("oracle", r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R35-PUBLISHER-PREPARATION-S1-20261013\NORMAL_PUBLISHER_EXPECTATION_ORACLE.json", "E68672E66E88195CAA25E185446FA1EE44C4399ED18F1211824B496B3DE7D3E0", 185157),
    ("protected_baseline", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R37_PUBLISHER_FINAL_PROTECTED_BASELINE_20261014.json", "DEDFB36F4728C72A6808BB0640213D509E85A4EC0AB7A37F31F916ADC5973F8B", 5922374)
]

print("=== VERIFYING REFERENCES ===")
ref_results = {}
for item in refs:
    tag = item[0]
    path = item[1]
    if not os.path.exists(path):
        print(f"ERROR: {tag} missing at {path}")
        continue
    sz, sha = get_file_stats(path)
    ref_results[tag] = {"path": path, "size": sz, "sha256": sha}
    if len(item) == 4:
        exp_sha = item[2]
        exp_sz = item[3]
        match_sha = (sha == exp_sha)
        match_sz = (sz == exp_sz)
        print(f"[{'PASS' if match_sha and match_sz else 'FAIL'}] {tag}: sz={sz} (exp {exp_sz}), sha={sha[:16]}... (exp {exp_sha[:16]}...)")
    else:
        print(f"[INFO] {tag}: sz={sz}, sha={sha[:16]}...")

print("\n=== VERIFYING ENGINE 9 BASELINE FILES ===")
engine_9 = [
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs", 276685, "544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs", 170135, "391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", 1774, "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll", 326144, "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb", 79220, "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll", 308224, "9CBA7E69210DE90B069F269744F3140C4ADD802FD868AB0E0C71FB0E5F69D106"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb", 57776, "F05FE976EB522B6A5FC78338B0C35A8CC5341322BACB4CA6310F6AF3682933F5"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll", 326144, "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029"),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb", 79220, "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE")
]

all_engine_exact = True
engine_status = []
for p, exp_sz, exp_sha in engine_9:
    sz, sha = get_file_stats(p)
    exact = (sz == exp_sz and sha == exp_sha)
    if not exact:
        all_engine_exact = False
    print(f"[{'EXACT' if exact else 'MISMATCH'}] {os.path.basename(p)} ({sz} B, {sha[:16]}...)")
    engine_status.append({
        "path": p,
        "expected_bytes": exp_sz,
        "expected_sha256": exp_sha,
        "actual_bytes": sz,
        "actual_sha256": sha,
        "bit_exact": exact
    })

print(f"All 9 Engine baseline bit-exact: {all_engine_exact}")

# Mutable publisher before inspection
pub_path = r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py"
pub_sz, pub_sha = get_file_stats(pub_path)
print(f"\nPublisher current (before R37 modifications): {pub_sz} B, sha={pub_sha}")

ack_time = datetime.now(timezone.utc).isoformat()
ack_data = {
    "dispatch_id": "WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a",
    "wp_id": "WP_ENGINE_GATE05_R37_PUBLISHER_FINAL",
    "wp_revision": "GATE05-R37-PUBLISHER-FINAL",
    "delivery_envelope_revision": 40,
    "received_at": ack_time,
    "status": "ACKNOWLEDGED",
    "recipient": "A",
    "route": "MASTER_DIRECT_COMPUTER_USE_ANTIGRAVITY",
    "instruction_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R37_PUBLISHER_FINAL.md",
    "instruction_sha256": "D721B31197FB92B5B32629251450C0164869EAB83255BC3E4855F7A5D6CA8C6B",
    "work_package_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R37_PUBLISHER_FINAL.md",
    "work_package_sha256": "D721B31197FB92B5B32629251450C0164869EAB83255BC3E4855F7A5D6CA8C6B",
    "release_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R37_PUBLISHER_FINAL_20261014.md",
    "release_sha256": "EA11EA70F15B4AA7D5D1D8F7FE424DA2B64A3BFE94EFC10760E4D451439F5197",
    "contract_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R37_PUBLISHER_FINAL_IMPLEMENTATION_CONTRACT_20261014.md",
    "contract_sha256": "8B5B0DD5B71AF36826036BAE70436A65444260949E2BD68EAB7F9054E8DA130C",
    "scope_baseline_path": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R37-PUBLISHER-FINAL-20261014-DIRECT-de39916a\MASTER_R37_AUTHORIZED_SOURCE_SCOPE.json",
    "scope_baseline_sha256": "AD8806EE585D30FE3939D3D51BD5AAD5C91A26B527552F398C10946661696F37",
    "allowed_mutable_paths": [
        pub_path
    ],
    "new_owned_E1_root": OWNED_DIR,
    "current_publisher_before": {
        "path": pub_path,
        "bytes": pub_sz,
        "sha256": pub_sha
    },
    "all9_engine_bit_exact": all_engine_exact,
    "governance_commitments": {
        "dedicated_server_authority": True,
        "foundation_hold": True,
        "zero_engine_builds": True,
        "zero_publisher_executions": True,
        "zero_native_unit_executions": True,
        "zero_1_7_migrations": True,
        "standalone_ast_verification_only": True
    }
}

ack_initial_path = os.path.join(TASK_DIR, "ACK_INITIAL.json")
ack_path = os.path.join(TASK_DIR, "ACK.json")

with open(ack_initial_path, "w", encoding="utf-8") as f:
    json.dump(ack_data, f, indent=2)
with open(ack_path, "w", encoding="utf-8") as f:
    json.dump(ack_data, f, indent=2)

print(f"Emitted ACK_INITIAL.json and ACK.json to {TASK_DIR}")

preservation_before = {
    "evaluated_at": ack_time,
    "all_Engine9_files": engine_status,
    "publisher_before": {
        "path": pub_path,
        "bytes": pub_sz,
        "sha256": pub_sha,
        "expected_sha256": "F60CBC184C6627F0FE15A5A904D0C45A026E20C5138973066BB8174DD8FBFD3F",
        "expected_bytes": 31689
    },
    "all_engine_preserved": all_engine_exact
}

pres_path = os.path.join(TASK_DIR, "PRESERVATION_BEFORE.json")
with open(pres_path, "w", encoding="utf-8") as f:
    json.dump(preservation_before, f, indent=2)

print(f"Emitted PRESERVATION_BEFORE.json to {TASK_DIR}")
