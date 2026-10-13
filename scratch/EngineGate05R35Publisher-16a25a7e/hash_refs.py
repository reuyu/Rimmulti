import hashlib
import json
import os

files = {
    "instructions": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e\INSTRUCTIONS.md",
    "wp": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\WP_ENGINE_GATE05_R35_PUBLISHER.md",
    "release": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\RELEASE_ENGINE_GATE05_R35_PUBLISHER_20261013.md",
    "contract": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R35_PLAN_ONLY_PUBLISHER_SAFETY_CONTRACT_20261013.md",
    "scope": r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R35-PUBLISHER-20261013-DIRECT-16a25a7e\MASTER_R35_AUTHORIZED_SOURCE_SCOPE.json",
    "baseline": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\coordination\MASTER_R35_PUBLISHER_PROTECTED_BASELINE_20261013.json",
    "review": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_REVIEW_ENGINE_GATE05_R34_INDEPENDENT_S1_20261013.md",
    "originalR29contract": r"C:\Users\user\Desktop\RimMulti\docs\WarEconomy_Master_Handoff_20261006\MASTER_R29_OPERATOR_STARTUP_PAIR_CONTRACT_20261012.md"
}

results = {}
for k, path in files.items():
    with open(path, "rb") as f:
        data = f.read()
    results[k] = {
        "path": path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest().upper()
    }

print(json.dumps(results, indent=2))
