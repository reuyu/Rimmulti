import json
import hashlib
import os

completion_path = r"Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R33-RESOURCE-COMMIT-20261013-DIRECT-d19c64a5\COMPLETION.json"
with open(completion_path, "r", encoding="utf-8") as f:
    c = json.load(f)

print("Verifying artifacts in COMPLETION.json...")
errors = 0
for art in c["artifacts"]:
    p = art["path"]
    if not os.path.exists(p):
        print(f"MISSING: {p}")
        errors += 1
        continue
    with open(p, "rb") as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest().upper()
    size = len(data)
    if sha != art["sha256"]:
        print(f"SHA MISMATCH in {art['role']}: expected {art['sha256']}, got {sha}")
        errors += 1
    if size != art["size"]:
        print(f"SIZE MISMATCH in {art['role']}: expected {art['size']}, got {size}")
        errors += 1
    print(f"OK: {art['role']} ({size} B)")

print(f"Total errors: {errors}")
