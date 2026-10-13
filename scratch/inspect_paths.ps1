$files = @(
    'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
    'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb',
    'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
    'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb',
    'scratch\WorkerBridgeMod\Source\WorkerBridge.cs',
    'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs',
    'scratch\WorkerBridgeMod\Source\WorkerBridge.csproj',
    'scratch\EngineGate05R2\Program.cs',
    'scratch\EngineGate05R2\Gate05R2TestRunner.csproj',
    'scratch\EngineGate05R2\results.json',
    'scratch\EngineGate05R2\raw_console.txt',
    'docs\POC_EngineHost_Semantic_Authority_Gate_05_R2.md',
    'docs\RELEASE_MANIFEST_ENGINE_GATE05_R2.json',
    'Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708\A_RECOVERY_ACK.md',
    'Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708\ACK.json',
    'Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708\A_WORK_LOG.md'
)

$results = foreach ($f in $files) {
    [PSCustomObject]@{
        File = $f
        Size = (Get-Item $f).Length
        SHA256 = (Get-FileHash $f).Hash
    }
}
foreach ($r in $results) {
    Write-Host "$($r.File) | $($r.Size) | $($r.SHA256)"
}


