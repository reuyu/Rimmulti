$paths = @(
    "scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"
)

$sha = [System.Security.Cryptography.SHA256]::Create()
$files = @()

foreach ($p in $paths) {
    $full = (Resolve-Path $p).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $files += [PSCustomObject]@{
        path = $full
        sha256 = $hash
        size = $bytes.Length
    }
}

$obj = [PSCustomObject]@{
    at = (Get-Date).ToString("o")
    stage = "POST_RUN_AFTER_R11"
    files = $files
}

$json = $obj | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText("scratch\EngineGate05R11PolicyEncoding\ENGINE_FREEZE_AFTER.json", $json, [System.Text.Encoding]::UTF8)
Write-Host "Generated ENGINE_FREEZE_AFTER.json successfully."
