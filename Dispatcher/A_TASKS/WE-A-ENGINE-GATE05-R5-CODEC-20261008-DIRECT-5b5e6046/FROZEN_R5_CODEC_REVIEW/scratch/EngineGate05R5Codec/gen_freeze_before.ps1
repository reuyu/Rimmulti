$dir = 'scratch\EngineGate05R5Codec'
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
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
$entries = @()
foreach ($f in $files) {
    if (Test-Path $f) {
        $item = Get-Item $f
        $h = (Get-FileHash $f -Algorithm SHA256).Hash
        $entries += [PSCustomObject]@{
            path = $f.Replace('\', '/')
            sha256 = $h
            size_bytes = $item.Length
        }
    }
}
$freeze = [PSCustomObject]@{
    schema_version = 1
    freeze_type = 'ENGINE_BEFORE'
    task_id = 'WE-A-ENGINE-GATE05-R5-CODEC-20261008-DIRECT-5b5e6046'
    wp_id = 'WP_ENGINE_GATE05_R5_CODEC'
    wp_revision = 'GATE05-R5-CODEC'
    created_at_utc = [DateTime]::UtcNow.ToString('O')
    producer = 'A'
    description = 'Pre-execution immutable freeze manifest of the engine paths before Gate05-R5 codec implementation.'
    entries = $entries
}
$freeze | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $dir 'ENGINE_FREEZE_BEFORE.json') -Encoding utf8
Write-Output 'ENGINE_FREEZE_BEFORE.json generated successfully.'
