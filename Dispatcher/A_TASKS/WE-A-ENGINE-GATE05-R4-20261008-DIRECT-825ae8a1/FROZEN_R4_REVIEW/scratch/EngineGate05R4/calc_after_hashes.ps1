$files = @(
    'scratch\WorkerBridgeMod\Source\WorkerBridge.cs',
    'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs',
    'scratch\WorkerBridgeMod\Source\WorkerBridge.csproj',
    'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
    'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb',
    'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
    'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb',
    'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll',
    'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb'
)

$results = @()
foreach ($f in $files) {
    if (Test-Path $f) {
        $item = Get-Item $f
        $hash = (Get-FileHash $f -Algorithm SHA256).Hash
        $results += [PSCustomObject]@{
            Path = $f
            SHA256 = $hash
            SizeBytes = $item.Length
        }
    } else {
        $results += [PSCustomObject]@{
            Path = $f
            SHA256 = "MISSING"
            SizeBytes = 0
        }
    }
}

$results | ConvertTo-Json -Depth 3 | Set-Content 'scratch\EngineGate05R4\current_after_hashes.json'
$results | Format-Table -AutoSize
