import json
import hashlib
import os
import struct

def get_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()

def get_mvid(dll_path):
    # Search for GUID in .NET metadata (#GUID stream or read via dotnet tool if available, or parse CLI header)
    # Alternatively use dotnet inline or python pefile
    return None

files = [
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.dll",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.exe",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\bin\Release\net8.0\WarEconomy.Server.pdb",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Common\bin\Release\netstandard2.0\WarEconomy.Common.dll",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Common\bin\Release\netstandard2.0\WarEconomy.Common.pdb",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\Pipeline\Recovery\RecoveryReconciler.cs",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\Pipeline\Data\Migrations\PipelineSchemaMigration.cs",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\Pipeline\Coordinator\PipelineTransactionCoordinator.cs",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\Pipeline\Models\PipelineProbeModels.cs",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\Pipeline\Storage\ProbeAggregateStore.cs",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Server\Program.cs",
    r"C:\Users\user\Desktop\RimMulti\WarEconomyMod\Source\Testing\WarEconomy.Pipeline.TestHarness\PipelineE1TestBattery.cs",
    r"C:\Users\user\Desktop\RimMulti\scratch\E1_Rev6_Runner\bin\Release\net8.0\pipeline_e1_rev6_results.json"
]

results = {}
for f in files:
    if os.path.exists(f):
        results[f] = {
            "size": os.path.getsize(f),
            "sha256": get_sha256(f)
        }
    else:
        results[f] = "NOT_FOUND"

print(json.dumps(results, indent=2))
with open(r"C:\Users\user\Desktop\RimMulti\scratch\rev6_provenance_info.json", "w") as fp:
    json.dump(results, fp, indent=2)
