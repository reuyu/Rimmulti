# -*- coding: utf-8 -*-
"""
verify_refs_and_emit_ack.py
Verification of R38 references and emission of ACK_INITIAL.json, ACK.json, and PRESERVATION_BEFORE.json
for WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES (Envelope 41).
"""
import os
import sys
import json
import hashlib
from datetime import datetime, timezone

WORKSPACE_ROOT = r"C:\Users\user\Desktop\RimMulti"
TASK_DIR = os.path.join(WORKSPACE_ROOT, r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e")
OWNED_DIR = os.path.join(WORKSPACE_ROOT, r"scratch\EngineGate05R38PublisherBoundaries-10b9846e")

def compute_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_file_stats(path):
    size = os.path.getsize(path)
    sha = compute_sha256(path)
    return size, sha

refs = [
    ("task", os.path.join(TASK_DIR, "TASK.json"), "TASK.json"),
    ("master_message", os.path.join(TASK_DIR, "MASTER_MESSAGE.txt"), "40275A4EF534DECD0DB7A826A53CC2F59592EB67E03EC18AE3D9B992BB4EE0FE", 417),
    ("scope", os.path.join(TASK_DIR, "MASTER_R38_AUTHORIZED_SOURCE_SCOPE.json"), "1DB85C95377C1FA573445453A5672045A6D218F8B7A24A2B53E3B89536E186C9", 3667),
    ("wp", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES.md", "358ACCF0717BAF257CEF8C80BB821570568698DCA987916C98B054719D1A1BBC", 1036),
    ("release", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES_20261014.md", "14DDA63751DD1E417589BC39806DF702394CD677E3D4C2F1499ABC4C95EF319E", 827),
    ("contract", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R38_PUBLISHER_BOUNDARIES_IMPLEMENTATION_CONTRACT_20261014.md", "BFE455E5E3A9C1C71735AFEDB8732BD3A8AA444E1F03B9DE1FD348E6FC2B69B6", 8140),
    ("r37_review", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R37_INDEPENDENT_STATIC_S1_20261014.md", "84016812620F3ED9D7533955130B60F7AAAF9342433162DFC30EAF42AB7FE41E", 4030),
    ("r37_ts_corr", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R37_ORIGINAL_LITERAL_TIMESTAMP_CORRECTION_20261014.md", "FEC2A1C44D1BD6CEDF4E0EF15F23B7B51E940C863A3E246F09AC0C5AA56026E0", 1239),
    ("r37_raw_witness", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R37_ORIGINAL_LITERAL_TIMESTAMP_RAW_WITNESS_20261014.json", "5C54C5570D88FEDAEA1EFD28329DB0078B0D8AA7D5485B6666844B025491A0F1", 4955),
    ("qa_s1_report", r"C:\Users\user\Desktop\RimMulti\docs\QA_EngineHost_Gate05_R37_Publisher_Independent_Static_S1_20261014.md", "E7CDEBB501D24BB1ABA828066D02757314ADE2A8A6732E957F36E94ABF5B18A4", 13476),
    ("minimal_next", r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014\MINIMAL_NEXT_PUBLISHER_CORRECTIVE_REQUIREMENTS.json", "293F629D7446B40E49AD28DDED8EC9A0F8DB8E6936F5365F5F200DCED1073EDC", 2517),
    ("matrix_source", r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R37-PUBLISHER-INDEPENDENT-STATIC-S1-20261014\ORIGINAL_SIX_LITERAL_SOURCE_COMPATIBILITY_MATRIX.json", "C5A6891F877D75C852C207945AED4248765CB2E64194AF78B63CD42E78FE441F", 48173),
    ("oracle", r"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\GATE05-R35-PUBLISHER-PREPARATION-S1-20261013\NORMAL_PUBLISHER_EXPECTATION_ORACLE.json", "E68672E66E88195CAA25E185446FA1EE44C4399ED18F1211824B496B3DE7D3E0", 185157),
    ("protected_baseline", r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R38_PUBLISHER_BOUNDARIES_PROTECTED_BASELINE_20261014.json", "TASK.json")
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
print(f"\nPublisher current (before R38 modifications): {pub_sz} B, sha={pub_sha}")

ack_time = datetime.now(timezone.utc).isoformat()
ack_data = {
    "dispatch_id": "WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e",
    "wp_id": "WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES",
    "wp_revision": "GATE05-R38-PUBLISHER-BOUNDARIES",
    "delivery_envelope_revision": 41,
    "received_at": ack_time,
    "status": "ACKNOWLEDGED",
    "recipient": "A",
    "route": "MASTER_DIRECT_COMPUTER_USE_ANTIGRAVITY",
    "instruction_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES.md",
    "instruction_sha256": "358ACCF0717BAF257CEF8C80BB821570568698DCA987916C98B054719D1A1BBC",
    "work_package_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES.md",
    "work_package_sha256": "358ACCF0717BAF257CEF8C80BB821570568698DCA987916C98B054719D1A1BBC",
    "release_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R38_PUBLISHER_BOUNDARIES_20261014.md",
    "release_sha256": "14DDA63751DD1E417589BC39806DF702394CD677E3D4C2F1499ABC4C95EF319E",
    "contract_path": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R38_PUBLISHER_BOUNDARIES_IMPLEMENTATION_CONTRACT_20261014.md",
    "contract_sha256": "BFE455E5E3A9C1C71735AFEDB8732BD3A8AA444E1F03B9DE1FD348E6FC2B69B6",
    "scope_baseline_path": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R38-PUBLISHER-BOUNDARIES-20261014-DIRECT-10b9846e\MASTER_R38_AUTHORIZED_SOURCE_SCOPE.json",
    "scope_baseline_sha256": "1DB85C95377C1FA573445453A5672045A6D218F8B7A24A2B53E3B89536E186C9",
    "allowed_mutable_paths": [
        pub_path
    ],
    "new_owned_E1_root": OWNED_DIR,
    "current_publisher_before": {
        "path": pub_path,
        "bytes": pub_sz,
        "sha256": pub_sha,
        "expected_sha256": "8F31D69A26A364BF727ABD029E096C0416B3C7B6BA54AC29A6A6E246FF537FD9",
        "expected_bytes": 40358
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
        "expected_sha256": "8F31D69A26A364BF727ABD029E096C0416B3C7B6BA54AC29A6A6E246FF537FD9",
        "expected_bytes": 40358
    },
    "all_engine_preserved": all_engine_exact
}

pres_path = os.path.join(TASK_DIR, "PRESERVATION_BEFORE.json")
with open(pres_path, "w", encoding="utf-8") as f:
    json.dump(preservation_before, f, indent=2)

print(f"Emitted PRESERVATION_BEFORE.json to {TASK_DIR}")
