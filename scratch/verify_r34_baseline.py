import hashlib
import json

with open(r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R34-ROLLBACK-20261013-DIRECT-a4d6866c\MASTER_R34_AUTHORIZED_SOURCE_SCOPE.json", "r", encoding="utf-8") as f:
    scope = json.load(f)

print("Verifying all9_before...")
all_matched = True
for item in scope["all9_before"]:
    with open(item["path"], "rb") as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest().upper()
    size = len(data)
    match = (sha == item["sha256"] and size == item["bytes"])
    print(f"{item['path']}: {match} ({size} B, {sha[:8]}...)")
    if not match:
        all_matched = False

for item in scope["fixed_current_files"]:
    with open(item["path"], "rb") as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest().upper()
    size = len(data)
    match = (sha == item["sha256"] and size == item["bytes"])
    print(f"FIXED {item['path']}: {match} ({size} B, {sha[:8]}...)")
    if not match:
        all_matched = False

print(f"All matched: {all_matched}")
