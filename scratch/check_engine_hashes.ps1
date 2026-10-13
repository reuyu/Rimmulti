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
$files | ForEach-Object {
    $item = Get-Item $_
    $sha = (Get-FileHash $_ -Algorithm SHA256).Hash
    [PSCustomObject]@{
        Path = $_
        Size = $item.Length
        SHA256 = $sha
    }
} | Format-Table -AutoSize
