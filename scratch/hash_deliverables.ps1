$files = @(
    'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',
    'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',
    'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/EngineGate05R1/Program.cs',
    'scratch/EngineGate05R1/Gate05R1TestRunner.csproj',
    'scratch/EngineGate05R1/results.json',
    'scratch/EngineGate05R1/raw_console.txt'
)
foreach ($f in $files) {
    if (Test-Path $f) {
        $h = (Get-FileHash -Algorithm SHA256 $f).Hash
        $len = (Get-Item $f).Length
        Write-Output ("{0} | {1} | {2}" -f $f, $len, $h)
    } else {
        Write-Output ("{0} | MISSING" -f $f)
    }
}
