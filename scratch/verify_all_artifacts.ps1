$files = @(
    "docs\POC_EngineHost_Semantic_Authority_Gate_05_R1.md",
    "docs\RELEASE_MANIFEST_ENGINE_GATE05_R1.json",
    "scratch\EngineGate05R1\results.json",
    "scratch\EngineGate05R1\raw_console.txt",
    "Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json",
    "scratch\MASTER_ENGINE_FREEZE_AFTER_GATE05_R1.json",
    "scratch\EngineGate05R1\bin\Release\net472\Gate05R1TestRunner.exe",
    "scratch\EngineGate05R1\bin\Release\net472\Gate05R1TestRunner.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj",
    "scratch\EngineGate05R1\Program.cs",
    "scratch\EngineGate05R1\Gate05R1TestRunner.csproj"
)

$results = foreach ($f in $files) {
    $fullPath = Resolve-Path $f
    $item = Get-Item $fullPath
    $hash = (Get-FileHash $fullPath -Algorithm SHA256).Hash
    [PSCustomObject]@{
        Path = $item.FullName
        Relative = $f
        Length = $item.Length
        SHA256 = $hash
    }
}

$results | Format-Table -AutoSize
$results | ConvertTo-Json -Depth 3 | Set-Content 'scratch\artifact_hashes.json' -Encoding UTF8
