import hashlib
import json
import os
from datetime import datetime

task_dir = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e"
owned_root = r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R35Publisher-16a25a7e"

ref_files = {
    "instructions": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e\INSTRUCTIONS.md",
    "wp": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R35_PUBLISHER.md",
    "release": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R35_PUBLISHER_20261013.md",
    "contract": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R35_PLAN_ONLY_PUBLISHER_SAFETY_CONTRACT_20261013.md",
    "scope": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e\MASTER_R35_AUTHORIZED_SOURCE_SCOPE.json",
    "baseline": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R35_PUBLISHER_PROTECTED_BASELINE_20261013.json",
    "review": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R34_INDEPENDENT_S1_20261013.md",
    "originalR29contract": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md"
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

engine_verification = []
for p, expected_sha, expected_size in engine9_files:
    with open(p, "rb") as f:
        data = f.read()
    actual_sha = hashlib.sha256(data).hexdigest().upper()
    actual_size = len(data)
    assert actual_sha == expected_sha, f"SHA mismatch on {p}: {actual_sha} vs {expected_sha}"
    assert actual_size == expected_size, f"Size mismatch on {p}: {actual_size} vs {expected_size}"
    engine_verification.append({
        "path": p,
        "sha256": actual_sha,
        "bytes": actual_size,
        "matches": True
    })

# Check publisher original
publisher_path = r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py"
with open(publisher_path, "rb") as f:
    pub_data = f.read()
pub_sha = hashlib.sha256(pub_data).hexdigest().upper()
assert pub_sha == "0204609D1D9D8A697B1A0B88537419D78B9E506558C771CA3EDD4C50FD49D470", f"Publisher sha mismatch: {pub_sha}"
assert len(pub_data) == 10442, f"Publisher size mismatch: {len(pub_data)}"

ack_data = {
    "dispatch_id": "WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e",
    "wp_id": "WP_ENGINE_GATE05_R35_PUBLISHER",
    "wp_revision": "GATE05-R35-PUBLISHER",
    "envelope": 38,
    "status": "ACKNOWLEDGED",
    "task_state": "IN_PROGRESS",
    "acknowledged_at": datetime.now().isoformat(),
    "receiver": "Antigravity Development Agent A",
    "instructions_file": ref_files["instructions"],
    "wp_file": ref_files["wp"],
    "release_file": ref_files["release"],
    "contract_file": ref_files["contract"],
    "scope_baseline_file": ref_files["scope"],
    "protected_baseline_file": ref_files["baseline"],
    "master_review_file": ref_files["review"],
    "original_r29_contract_file": ref_files["originalR29contract"],
    "instructions_sha256": ref_hashes["instructions"]["sha256"],
    "instructions_bytes": ref_hashes["instructions"]["bytes"],
    "wp_sha256": ref_hashes["wp"]["sha256"],
    "wp_bytes": ref_hashes["wp"]["bytes"],
    "release_sha256": ref_hashes["release"]["sha256"],
    "release_bytes": ref_hashes["release"]["bytes"],
    "contract_sha256": ref_hashes["contract"]["sha256"],
    "contract_bytes": ref_hashes["contract"]["bytes"],
    "scope_sha256": ref_hashes["scope"]["sha256"],
    "scope_bytes": ref_hashes["scope"]["bytes"],
    "protected_baseline_sha256": ref_hashes["baseline"]["sha256"],
    "protected_baseline_bytes": ref_hashes["baseline"]["bytes"],
    "master_review_sha256": ref_hashes["review"]["sha256"],
    "master_review_bytes": ref_hashes["review"]["bytes"],
    "original_r29_contract_sha256": ref_hashes["originalR29contract"]["sha256"],
    "original_r29_contract_bytes": ref_hashes["originalR29contract"]["bytes"],
    "new_owned_e1_root": owned_root,
    "scope_policy": "PLAN_ONLY_PUBLISHER_SAFETY_NONOVERWRITE_EXCLUSIVE_NEW_OWNED_ROOT_STRICT_CONFIG14_DECL7_PATH_SHA_BINDING",
    "scope_boundary": "SOURCE_AND_AST_SYNTAX_ONLY_ZERO_PUBLISHER_EXECUTION_ZERO_ENGINE_BUILD_ZERO_UNIT_NATIVE_EXECUTION",
    "allowed_mutable_paths": [
        publisher_path
    ],
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
    "verified_at": datetime.now().isoformat(),
    "all_Engine9_before": [
        {
            "path": p,
            "sha256": s,
            "bytes": b
        } for p, s, b in engine9_files
    ],
    "publisher_original": {
        "path": publisher_path,
        "sha256": pub_sha,
        "bytes": len(pub_data)
    },
    "all_verified": True
}

with open(os.path.join(task_dir, "PRESERVATION_BEFORE.json"), "w", encoding="utf-8") as f:
    json.dump(preservation_before, f, indent=2)

print("Baseline verification and ACK emission successful!")
