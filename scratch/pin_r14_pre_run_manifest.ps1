$outDir = "scratch\EngineGate05R14PolicyCapturePublication"
$sha = [System.Security.Cryptography.SHA256]::Create()

function Get-FileEntry($p) {
    $full = (Resolve-Path $p).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $entry = [ordered]@{
        path = $p
        sha256 = $hash
        size = $bytes.Length
    }
    if ($p.EndsWith(".dll") -or $p.EndsWith(".exe")) {
        try {
            $mod = [System.Reflection.Assembly]::LoadFile($full).ManifestModule
            $entry["mvid"] = $mod.ModuleVersionId.ToString()
        } catch {}
    }
    return $entry
}

$preRunObj = [ordered]@{
    manifest_version = "1.0"
    run_id = "GATE05-R14-POLICY-CAPTURE-PUBLICATION-RUN-01"
    work_package = "WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION"
    revision = "GATE05-R14-POLICY-CAPTURE-PUBLICATION"
    pinned_at_utc = [System.DateTime]::UtcNow.ToString("o")
    agent = "Antigravity A"
    dispatch_id = "WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b"
    selected_candidate = Get-FileEntry "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
    selected_pdb = Get-FileEntry "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
    alternate_candidate = Get-FileEntry "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
    alternate_pdb = Get-FileEntry "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
    deployed_candidate = Get-FileEntry "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"
    deployed_pdb = Get-FileEntry "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
    sources = @(
        (Get-FileEntry "scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
        (Get-FileEntry "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
        (Get-FileEntry "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj")
    )
    runner = [ordered]@{
        project = Get-FileEntry "scratch\EngineGate05R14PolicyCapturePublication\Harness\Gate05R14CacheRunner.csproj"
        source = Get-FileEntry "scratch\EngineGate05R14PolicyCapturePublication\Harness\Program.cs"
        binary = Get-FileEntry "scratch\EngineGate05R14PolicyCapturePublication\Harness\bin\Debug\net472\Gate05R14CacheRunner.exe"
        pdb = Get-FileEntry "scratch\EngineGate05R14PolicyCapturePublication\Harness\bin\Debug\net472\Gate05R14CacheRunner.pdb"
    }
}

Add-Type -Path "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\bin\Debug\net472\Newtonsoft.Json.dll"
$json = [Newtonsoft.Json.JsonConvert]::SerializeObject($preRunObj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$destPath = "$outDir\CANDIDATE_PRE_RUN_MANIFEST.json"
[System.IO.File]::WriteAllText($destPath, $json, $utf8NoBom)
Write-Host "Created $destPath"
