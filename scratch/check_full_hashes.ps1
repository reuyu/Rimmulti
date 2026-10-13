$files = @(
    "scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
)
foreach ($f in $files) {
    $item = Get-Item $f
    $sha = (Get-FileHash $f -Algorithm SHA256).Hash
    Write-Host "$f | $($item.Length) | $sha"
}
