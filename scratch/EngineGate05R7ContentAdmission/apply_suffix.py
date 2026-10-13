import hashlib
import os

ws = r"C:\Users\user\Desktop\RimMulti"
census_path = os.path.join(ws, r"scratch\WorkerBridgeMod\Source\EngineHostCensus.cs")
suffix_path = os.path.join(ws, r"scratch\EngineGate05R7ContentAdmission\new_suffix.cs")

with open(census_path, "rb") as f:
    census_data = f.read()

prefix = census_data[:72547]
prefix_sha = hashlib.sha256(prefix).hexdigest().upper()
print(f"Prefix length: {len(prefix)}, SHA256: {prefix_sha}")
assert len(prefix) == 72547, "Prefix length must be 72547"
assert prefix_sha == "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887", "Prefix SHA mismatch!"

with open(suffix_path, "rb") as f:
    suffix_data = f.read()

new_content = prefix + suffix_data

with open(census_path, "wb") as f:
    f.write(new_content)

full_sha = hashlib.sha256(new_content).hexdigest().upper()
print(f"Updated EngineHostCensus.cs: length {len(new_content)}, SHA256: {full_sha}")
