$files = @(
    "scratch\EngineGate05R17OwnedBootstrap\Harness\Gate05R17BootstrapRunner.csproj",
    "scratch\EngineGate05R17OwnedBootstrap\Harness\Program.cs",
    "scratch\EngineGate05R17OwnedBootstrap\Harness\bin\Debug\net472\Gate05R17BootstrapRunner.exe",
    "scratch\EngineGate05R17OwnedBootstrap\Harness\bin\Debug\net472\Gate05R17BootstrapRunner.pdb",
    "scratch\EngineGate05R17OwnedBootstrap\run_default\RESULTS.json",
    "scratch\EngineGate05R17OwnedBootstrap\run_default\API_LEDGER.json",
    "docs\POC_EngineHost_Semantic_Authority_Gate_05_R17.md",
    "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R17-OWNED-BOOTSTRAP-20261010-DIRECT-57163c71\ENGINE_FREEZE_BEFORE.json",
    "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R17-OWNED-BOOTSTRAP-20261010-DIRECT-57163c71\ENGINE_FREEZE_AFTER.json"
)
foreach ($f in $files) {
    $item = Get-Item $f
    $sha = (Get-FileHash $f -Algorithm SHA256).Hash
    Write-Host "$f | $($item.Length) | $sha"
}
