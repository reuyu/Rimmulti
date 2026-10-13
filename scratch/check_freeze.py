import json
import hashlib

before_path = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-20261007-DIRECT-01\MASTER_ENGINE_FREEZE_BEFORE.json"
after_path = r"C:\Users\user\Desktop\RimMulti\scratch\MASTER_ENGINE_FREEZE_AFTER.json"

with open(before_path, "r", encoding="utf-8") as f:
    data = json.load(f)

matched = 0
after_files = []
for item in data["files"]:
    p = item["path"]
    with open(p, "rb") as fp:
        actual = hashlib.sha256(fp.read()).hexdigest().upper()
    is_match = (actual == item["expected"])
    if is_match:
        matched += 1
    after_files.append({
        "path": p,
        "expected": item["expected"],
        "actual": actual,
        "match": is_match
    })

print(f"MATCHED: {matched}/{len(data['files'])}")

after_manifest = {
    "at": "2026-10-07T18:52:00+09:00",
    "total": len(data["files"]),
    "matched": matched,
    "all_matched": (matched == len(data["files"])),
    "files": after_files
}

with open(after_path, "w", encoding="utf-8") as f:
    json.dump(after_manifest, f, indent=2)

print(f"Saved after manifest to {after_path}")
