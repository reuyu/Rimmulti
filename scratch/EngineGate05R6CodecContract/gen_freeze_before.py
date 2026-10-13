import os
import hashlib
import json
from datetime import datetime, timezone

os.makedirs("scratch/EngineGate05R6CodecContract", exist_ok=True)

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
    'freeze_type': 'ENGINE_BEFORE',
    'task_id': 'WE-A-ENGINE-GATE05-R6-CODEC-CONTRACT-20261008-DIRECT-1f657abe',
    'wp_id': 'WP_ENGINE_GATE05_R6_CODEC_CONTRACT',
    'wp_revision': 'GATE05-R6-CODEC-CONTRACT',
    'created_at_utc': datetime.now(timezone.utc).isoformat(),
    'producer': 'A',
    'description': 'Pre-execution immutable freeze manifest of engine paths before Gate05-R6 codec contract implementation.',
    'entries': entries
}

out_path = 'scratch/EngineGate05R6CodecContract/ENGINE_FREEZE_BEFORE.json'
with open(out_path, 'w', encoding='utf-8') as fp:
    json.dump(freeze, fp, indent=2)

print('ENGINE_FREEZE_BEFORE.json generated successfully.')
for e in entries:
    print(f"  {e['path']:70} {e['size_bytes']:8} {e['sha256']}")
