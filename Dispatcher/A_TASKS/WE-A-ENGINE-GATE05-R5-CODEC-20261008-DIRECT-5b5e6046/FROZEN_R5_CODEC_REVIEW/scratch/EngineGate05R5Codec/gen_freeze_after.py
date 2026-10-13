import os
import hashlib
import json
from datetime import datetime, timezone

files = [
    'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',
    'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',
    'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.pdb'
]

entries = []
for f in files:
    if os.path.exists(f):
        with open(f, 'rb') as fp:
            data = fp.read()
        entries.append({
            'path': f,
            'sha256': hashlib.sha256(data).hexdigest().upper(),
            'size_bytes': len(data)
        })

freeze = {
    'schema_version': 1,
    'freeze_type': 'ENGINE_AFTER',
    'task_id': 'WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046',
    'wp_id': 'WP_ENGINE_GATE05_R5_CODEC',
    'wp_revision': 'GATE05-R5-CODEC',
    'created_at_utc': datetime.now(timezone.utc).isoformat(),
    'producer': 'A',
    'description': 'Post-execution freeze manifest of engine paths after Gate05-R5 codec implementation and verification.',
    'entries': entries
}

out_path = 'scratch/EngineGate05R5Codec/ENGINE_FREEZE_AFTER.json'
with open(out_path, 'w', encoding='utf-8') as fp:
    json.dump(freeze, fp, indent=2)

print('ENGINE_FREEZE_AFTER.json generated successfully.')
print(json.dumps(freeze, indent=2))
