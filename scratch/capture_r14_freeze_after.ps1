$outDir = "scratch\EngineGate05R14PolicyCapturePublication"
$sha = [System.Security.Cryptography.SHA256]::Create()

$paths = @(
    "scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
)

$entries = @()
foreach ($p in $paths) {
    $full = (Resolve-Path $p).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $entries += [ordered]@{
        path = $p
        sha256 = $hash
        size = $bytes.Length
    }
}

$obj = [ordered]@{
    at = [System.DateTime]::UtcNow.ToString("o")
    work_package = "WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION"
    baseline = "GATE05-R14-POLICY-CAPTURE-PUBLICATION"
    files = $entries
}

Add-Type -Path "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\bin\Debug\net472\Newtonsoft.Json.dll"
$json = [Newtonsoft.Json.JsonConvert]::SerializeObject($obj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("$outDir\ENGINE_FREEZE_AFTER.json", $json, $utf8NoBom)
Write-Host "Created $outDir\ENGINE_FREEZE_AFTER.json"
