import os
import hashlib

task_dir = r"C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R23-IDENTIFIER-MAPPING-20261011-DIRECT-31bd3af2"
wb_path = r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"

with open(wb_path, "rb") as f:
    wb = f.read()

with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_0.bin"), "rb") as f:
    s0 = f.read()
with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_1.bin"), "rb") as f:
    s1 = f.read()
with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_2.bin"), "rb") as f:
    s2 = f.read()
with open(os.path.join(task_dir, "WORKER_FIXED_SEGMENT_3.bin"), "rb") as f:
    s3 = f.read()

print("s0 match:", wb[0:len(s0)] == s0)
offset = len(s0)
span0 = b"                    originId = origin,\n                    launchPlanId = plan,\n                    expectedConfigId = cfgId,\n"
print("span0 match:", wb[offset:offset+len(span0)] == span0)
offset += len(span0)

print("s1 match:", wb[offset:offset+len(s1)] == s1)
offset += len(s1)
span1 = (
    b"            var desc = descriptor.Clone();\n"
    b'            desc.expectedRole = desc.expectedRole?.Trim() ?? "";\n'
    b'            desc.expectedCapabilityBoundary = desc.expectedCapabilityBoundary?.Trim() ?? "";\n'
)
print("span1 match:", wb[offset:offset+len(span1)] == span1)
offset += len(span1)

print("s2 match:", wb[offset:offset+len(s2)] == s2)
offset += len(s2)
print("span2 match:", wb[offset:offset+len(span1)] == span1)
offset += len(span1)

print("s3 match:", wb[offset:offset+len(s3)] == s3)
offset += len(s3)
print("Total verified len:", offset == len(wb), "Total bytes:", len(wb))

census_path = r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
with open(census_path, "rb") as f:
    c_bytes = f.read()
print("Census sha:", hashlib.sha256(c_bytes).hexdigest().upper(), "len:", len(c_bytes))

csproj_path = r"C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"
with open(csproj_path, "rb") as f:
    cs_bytes = f.read()
print("csproj sha:", hashlib.sha256(cs_bytes).hexdigest().upper(), "len:", len(cs_bytes))
