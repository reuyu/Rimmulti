import json
import os

task_dir = r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c"

ack_data = {
    "dispatch_id": "WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c",
    "wp_id": "WP_ENGINE_GATE05_R34_ROLLBACK",
    "wp_revision": "GATE05-R34-ROLLBACK",
    "envelope": 37,
    "status": "ACKNOWLEDGED",
    "task_state": "IN_PROGRESS",
    "acknowledged_at": "2026-10-13T17:58:00+09:00",
    "receiver": "Antigravity Development Agent A",
    "instructions_file": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c\INSTRUCTIONS.md",
    "wp_file": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R34_ROLLBACK.md",
    "release_file": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R34_ROLLBACK_20261013.md",
    "contract_file": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R34_ROLLBACK_ORDERING_CONTRACT_20261013.md",
    "scope_baseline_file": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c\MASTER_R34_AUTHORIZED_SOURCE_SCOPE.json",
    "protected_baseline_file": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R34_ROLLBACK_PROTECTED_BASELINE_20261013.json",
    "master_review_file": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R33_INDEPENDENT_S1_20261013.md",
    "refobservation_file": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5\MASTER_EXISTING_FULL_COMPILER_REFERENCE_OBSERVATION.json",
    "instructions_sha256": "F795874974DD1DBCFA85763206F38756A9C45BE20BF5B31B3A74B4AF533DC1A2",
    "wp_sha256": "F9B779AE720C1C8903BDFD575C32ABA2D4100D06B43D0F23B40F52C3B9B9BB32",
    "release_sha256": "45D05CF2EDE145D957273F5434B19EDB043D9469C6004E36E084B2AA5DADB62A",
    "contract_sha256": "8FCB97F5CEE651066579AB86941729F7F390092B6FCF4D02313DA21DE8254FB3",
    "scope_sha256": "8B6877DD3B5952BAD84E6DE21E1F9A168B7268C9D739ABFA9AE4615C956DB6FA",
    "protected_baseline_sha256": "109EC11C06B29C322BE3A35E3B1AD6EC2CED1F3542A07CD39403F5A0EA881640",
    "master_review_sha256": "AF82122EB10D1288048FE53247717E0DBB277560E9EA453777B45234B6A6C05B",
    "refobservation_sha256": "64F985576570F823DC765AC01E156A4ADEAA8CDBF4517F51233AF3D89EE94A4A",
    "new_owned_e1_root": r"C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R34Rollback-a4d6866c",
    "scope_policy": "FAILURE_PUBLICATION_BEFORE_CLEANUP_AND_OUTSIDE_LOCK_SAFE_OWNED_CLEANUP_ONE_AWAKE_SPAN_ONLY",
    "scope_boundary": "BUILD_ONLY_PROSPECTIVE_SOURCE_AND_FIRST_BINARY_EVIDENCE_ZERO_RUNNER_ZERO_NATIVE_EXECUTION_ZERO_MODIFICATION_OUTSIDE_ONE_SPAN",
    "allowed_mutable_paths": [
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
        r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
    ],
    "fixed_current_files": [
        {
            "path": r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
            "sha256": "391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1",
            "bytes": 170135
        },
        {
            "path": r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj",
            "sha256": "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052",
            "bytes": 1774
        },
        {
            "path": r"C:\Users\user\Desktop\RimMulti\scratch\OperatorStartupPairR29\publish_operator_pair.py",
            "sha256": "0204609D1D9D8A697B1A0B88537419D78B9E506558C771CA3EDD4C50FD49D470",
            "bytes": 10442
        }
    ]
}

ack_path = os.path.join(task_dir, "ACK.json")
ack_init_path = os.path.join(task_dir, "ACK_INITIAL.json")

with open(ack_path, "w", encoding="utf-8") as f:
    json.dump(ack_data, f, indent=2, ensure_ascii=False)

with open(ack_init_path, "w", encoding="utf-8") as f:
    json.dump(ack_data, f, indent=2, ensure_ascii=False)

print("Wrote ACK.json and ACK_INITIAL.json successfully.")
