import os
import hashlib

task_dir = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R23-IDENTIFIER-MAPPING-20261011-DIRECT-31bd3af2"
repo_root = r"C:\Users\user\Desktop\RimMulti"

with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_0.bin"), "rb") as f:
    seg0 = f.read()
with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_1.bin"), "rb") as f:
    seg1 = f.read()
with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_2.bin"), "rb") as f:
    seg2 = f.read()
with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_3.bin"), "rb") as f:
    seg3 = f.read()

span0 = b"                    originId = origin,\n                    launchPlanId = plan,\n                    expectedConfigId = cfgId,\n"

span1 = (
    b"            var desc = descriptor.Clone();\n"
    b'            desc.expectedRole = desc.expectedRole?.Trim() ?? "";\n'
    b'            desc.expectedCapabilityBoundary = desc.expectedCapabilityBoundary?.Trim() ?? "";\n'
)

span2 = span1

assembled = seg0 + span0 + seg1 + span1 + seg2 + span2 + seg3
print("Assembled size:", len(assembled))
print("Assembled sha256:", hashlib.sha256(assembled).hexdigest().upper())

out_file = os.path.join(repo_root, r"scratch\WorkerBridgeMod\Source\WorkerBridge.cs")
with open(out_file, "wb") as f:
    f.write(assembled)
print("Successfully wrote assembled WorkerBridge.cs")
