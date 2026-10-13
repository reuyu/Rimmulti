$dir = "scratch\EngineGate05R13PolicyCacheLifecycle"
if (-not (Test-Path $dir)) {
    New-Item -ItemType Directory -Path $dir | Out-Null
}

$sha = [System.Security.Cryptography.SHA256]::Create()
$files = @(
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

$list = @()
foreach ($f in $files) {
    $full = (Resolve-Path $f).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $h = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $list += [ordered]@{
        path = $full
        sha256 = $h
        size = $bytes.Length
    }
}

$obj = [ordered]@{
    at = (Get-Date).ToString("o")
    stage = "PRE_RUN_BEFORE_R13"
    files = $list
}

$json = $obj | ConvertTo-Json -Depth 5
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("$dir\ENGINE_FREEZE_BEFORE.json", $json, $utf8NoBom)
Write-Host "Wrote $dir\ENGINE_FREEZE_BEFORE.json successfully."
