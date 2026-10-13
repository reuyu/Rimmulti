$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$scratchDir = "$workspaceRoot\scratch\EngineGate05R15PublicManifestBoundary"
if (-not (Test-Path $scratchDir)) {
    New-Item -ItemType Directory -Path $scratchDir -Force | Out-Null
}

$paths = @(
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"
)

$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Get-FileSha256([string]$filePath) {
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $hash = $sha256.ComputeHash($bytes)
    return -join ($hash | ForEach-Object { $_.ToString("X2") })
}

$entries = @()
foreach ($p in $paths) {
    if (-not (Test-Path $p)) {
        throw "Path does not exist: $p"
    }
    $bytes = [System.IO.File]::ReadAllBytes($p)
    $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
    $entries += [PSCustomObject]@{
        path = $p
        sha256 = $hash
        size = $bytes.Length
    }
}

# Verify Census prefix (72,547 bytes)
$censusPath = "$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
$censusBytes = [System.IO.File]::ReadAllBytes($censusPath)
if ($censusBytes.Length -lt 72547) {
    throw "Census bytes length ($($censusBytes.Length)) < 72547"
}
$prefixBytes = New-Object byte[] 72547
[System.Array]::Copy($censusBytes, 0, $prefixBytes, 0, 72547)
$prefixHash = -join ($sha256.ComputeHash($prefixBytes) | ForEach-Object { $_.ToString("X2") })

$expectedPrefixHash = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
if ($prefixHash -ne $expectedPrefixHash) {
    throw "Census prefix hash mismatch! Expected: $expectedPrefixHash, Actual: $prefixHash"
}

$freeze = [PSCustomObject]@{
    captured_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffffffK")
    dispatch_id = "WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052"
    technical_objective = "PUBLIC_MANIFEST_BOUNDARY"
    census_prefix_72547_sha256 = $prefixHash
    census_prefix_72547_match = $true
    files = $entries
}

$json = $freeze | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText("$scratchDir\ENGINE_FREEZE_BEFORE.json", $json, [System.Text.Encoding]::UTF8)

Write-Host "Freeze before captured successfully. Prefix verified: $prefixHash"
