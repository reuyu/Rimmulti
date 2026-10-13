import hashlib
from pathlib import Path

task_dir = Path(r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R22-DECLARATION-20261011-DIRECT-9be1579a")
worker_file = Path(r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs")

worker_bytes = worker_file.read_bytes()
print(f"WorkerBridge.cs size: {len(worker_bytes)}, sha256: {hashlib.sha256(worker_bytes).hexdigest().upper()}")

segs = []
for i in range(5):
    p = task_dir / f"WORKER_FIXED_SEGMENT_{i}.bin"
    b = p.read_bytes()
    segs.append(b)
    print(f"Seg {i}: size={len(b)}, sha256={hashlib.sha256(b).hexdigest().upper()}")

# In worker_bytes before edit:
# seg 0: [0:1126]
# reg 0: [1126:5126]
# seg 1: [5126:176897]
# reg 1: [176897:177881]
# seg 2: [177881:178553]
# reg 2: [178553:179597]
# seg 3: [179597:189890]
# reg 3: [189890:199521]
# seg 4: [199521:214277]

slices = [
    (0, 1126, "seg0"),
    (1126, 5126, "reg0 (Region 1: BOOTSTRAP_DECLARATION_ONLY)"),
    (5126, 176897, "seg1"),
    (176897, 177881, "reg1 (Region 2: DESCRIPTOR_DEFAULTS_HELPER_CLONE)"),
    (177881, 178553, "seg2"),
    (178553, 179597, "reg2 (Region 3: PRIVATE_CAPTURE_AND_CONSTRUCTOR_ONLY)"),
    (179597, 189890, "seg3"),
    (189890, 199521, "reg3 (Region 4: RECEIPT_FACTORY_AND_VALIDATION_ONLY)"),
    (199521, 214277, "seg4")
]

for start, end, label in slices:
    part = worker_bytes[start:end]
    print(f"{label}: len={len(part)}, start={start}, end={end}, sha256={hashlib.sha256(part).hexdigest().upper()}")
    if label.startswith("seg"):
        idx = int(label[3])
        match = (part == segs[idx])
        print(f"  Matches seg{idx}: {match}")

# Print the text of the 4 mutable regions
for idx, (start, end, label) in enumerate([(1126, 5126, "Region 1"), (176897, 177881, "Region 2"), (178553, 179597, "Region 3"), (189890, 199521, "Region 4")]):
    print(f"\n{'='*40}\n{label} ({start} to {end}):\n{'='*40}")
    print(worker_bytes[start:end].decode("utf-8"))
