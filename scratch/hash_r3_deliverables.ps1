$files = @(
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',
    'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',
    'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj',
    'scratch/EngineGate05R3/Gate05R3TestRunner.csproj',
    'scratch/EngineGate05R3/Program.cs',
    'scratch/EngineGate05R3/results.json',
    'scratch/EngineGate05R3/raw_console.txt',
    'scratch/EngineGate05R3/native_execution_observation.txt',
    'docs/POC_EngineHost_Semantic_Authority_Gate_05_R3.md',
    'docs/RELEASE_MANIFEST_ENGINE_GATE05_R3.json',
    'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/ACK.json',
    'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/A_RECOVERY_ACK.md',
    'Dispatcher/A_TASKS/WE-A-ENGINE-GATE05-R3-20261008-DIRECT-756d5bfa/A_WORK_LOG.md'
)

$out = @{}
foreach ($f in $files) {
    if (Test-Path $f) {
        $hash = (Get-FileHash $f -Algorithm SHA256).Hash
        $size = (Get-Item $f).Length
        $entry = @{
            path = $f
            sha256 = $hash
            bytes = $size
        }
        if ($f.EndsWith('.dll')) {
            $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $f))
            $asm = [System.Reflection.Assembly]::Load($bytes)
            $entry['mvid'] = $asm.ManifestModule.ModuleVersionId.ToString()
        }
        $out[$f] = $entry
        Write-Output "$f | SHA256=$hash | Bytes=$size"
    } else {
        Write-Output "$f | NOT FOUND"
    }
}

$out | ConvertTo-Json -Depth 3 | Set-Content "scratch/r3_deliverables_hashes.json"
