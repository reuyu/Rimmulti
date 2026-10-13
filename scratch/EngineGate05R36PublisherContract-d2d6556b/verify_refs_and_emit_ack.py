import hashlib
import json
import os
from datetime import datetime, timezone

task_dir = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b"
owned_root = r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R36PublisherContract-d2d6556b"

ref_files = {
    "task": os.path.join(task_dir, "TASK.json"),
    "master_message": os.path.join(task_dir, "MASTER_MESSAGE.txt"),
    "scope": os.path.join(task_dir, "MASTER_R36_AUTHORIZED_SOURCE_SCOPE.json"),
    "wp": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT.md",
    "release": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R36_PUBLISHER_CONTRACT_20261013.md",
    "contract": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md",
    "r35_review": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R35_INDEPENDENT_STATIC_S1_20261013.md",
    "r35_correction": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R35_POLICY_AND_FILESYSTEM_CLAIM_CORRECTIONS_20261013.md",
    "qa_s1_report": r"C:\Users\user\Desktop\RimMulti\docs\QA_EngineHost_Gate05_R35_Publisher_Independent_Static_S1_20261013.md",
    "minimal_r36": r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R35-PUBLISHER-INDEPENDENT-STATIC-S1-20261013\MINIMAL_R36_CORRECTIVE_REQUIREMENTS.json",
    "protected_baseline": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R36_PUBLISHER_CONTRACT_PROTECTED_BASELINE_20261013.json"
}

ref_hashes = {}
for k, path in ref_files.items():
    with open(path, "rb") as f:
        data = f.read()
    ref_hashes[k] = {
        "path": path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper()
    }

print("Reference hashes computed:")
for k, v in ref_hashes.items():
    print(f"  {k}: {v['bytes']} B, {v['sha256']}")

# Verify Engine 9 baseline files
engine9_files = [
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs", "544B22178F80C63FE85584BCA93ED1D7B77B59554C93762F38655B87237682FD", 276685),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs", "391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1", 170135),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj", "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052", 1774),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll", "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029", 326144),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb", "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE", 79220),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll", "9CBA7E69210DE90B069F269744F3140C4ADD802FD868AB0E0C71FB0E5F69D106", 308224),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb", "F05FE976EB522B6A5FC78338B0C35A8CC5341322BACB4CA6310F6AF3682933F5", 57776),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll", "8091F4414A29EF5AE224BA67A82A5F7B866C230EEFFC33D78486C28AD3297029", 326144),
    (r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb", "FE75B3D1AFA31C88AE2B8FB56F76F00D8929D28FCE1EA315027A154FFD76F0DE", 79220),
]

for p, s, b in engine9_files:
    with open(p, "rb") as f:
        data = f.read()
    actual_sha = hashlib.sha256(data).hexdigest().upper()
    actual_size = len(data)
    assert actual_sha == s, f"Engine file mismatch {p}: sha {actual_sha} vs {s}"
    assert actual_size == b, f"Engine file mismatch {p}: size {actual_size} vs {b}"

# Check publisher original
pub_path = r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py"
with open(pub_path, "rb") as f:
    pub_data = f.read()
pub_sha = hashlib.sha256(pub_data).hexdigest().upper()
assert pub_sha == "9CAEA2DF0B8F3517DFCBEF080F7D26EC4343CDF4D2FD761453EFA2E4F3B86B4A", f"Publisher sha mismatch: {pub_sha}"
assert len(pub_data) == 22371, f"Publisher size mismatch: {len(pub_data)}"

ack_data = {
    "dispatch_id": "WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b",
    "wp_id": "WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT",
    "wp_revision": "GATE05-R36-PUBLISHER-CONTRACT",
    "envelope": 39,
    "status": "ACKNOWLEDGED",
    "task_state": "IN_PROGRESS",
    "acknowledged_at": datetime.now(timezone.utc).isoformat(),
    "receiver": "Antigravity Development Agent A",
    "instruction_file": ref_files["wp"],
    "task_file": ref_files["task"],
    "release_file": ref_files["release"],
    "contract_file": ref_files["contract"],
    "scope_baseline_file": ref_files["scope"],
    "protected_baseline_file": ref_files["protected_baseline"],
    "master_message_file": ref_files["master_message"],
    "r35_review_file": ref_files["r35_review"],
    "r35_correction_file": ref_files["r35_correction"],
    "qa_s1_report_file": ref_files["qa_s1_report"],
    "minimal_r36_requirements_file": ref_files["minimal_r36"],
    "ref_hashes": ref_hashes,
    "new_owned_e1_root": owned_root,
    "scope_policy": "PUBLISHER_CONTRACT_CORRECTION_AND_SUPPORTED_DOMAIN_ENFORCEMENT_SOURCE_AND_AST_ONLY",
    "scope_boundary": "SOURCE_AND_AST_SYNTAX_ONLY_ZERO_PUBLISHER_EXECUTION_ZERO_ENGINE_BUILD_ZERO_UNIT_NATIVE_EXECUTION",
    "allowed_mutable_paths": [
        pub_path
    ],
    "publisher_original": {
        "path": pub_path,
        "bytes": len(pub_data),
        "sha256": pub_sha
    },
    "fixed_current_files": [
        {
            "path": p,
            "sha256": s,
            "bytes": b
        } for p, s, b in engine9_files
    ]
}

# Write ACK_INITIAL.json and ACK.json in task_dir
with open(os.path.join(task_dir, "ACK_INITIAL.json"), "w", encoding="utf-8") as f:
    json.dump(ack_data, f, indent=2)

with open(os.path.join(task_dir, "ACK.json"), "w", encoding="utf-8") as f:
    json.dump(ack_data, f, indent=2)

# Write PRESERVATION_BEFORE.json in task_dir
preservation_before = {
    "verified_at": datetime.now(timezone.utc).isoformat(),
    "all_Engine9_before": [
        {
            "path": p,
            "sha256": s,
            "bytes": b
        } for p, s, b in engine9_files
    ],
    "publisher_original": {
        "path": pub_path,
        "sha256": pub_sha,
        "bytes": len(pub_data)
    },
    "all_verified": True
}

with open(os.path.join(task_dir, "PRESERVATION_BEFORE.json"), "w", encoding="utf-8") as f:
    json.dump(preservation_before, f, indent=2)

print("Baseline verification and ACK emission successful!")
