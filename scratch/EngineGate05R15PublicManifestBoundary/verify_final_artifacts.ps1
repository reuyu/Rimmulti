$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$taskDir = "$workspaceRoot\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052"
$scratchDir = "$workspaceRoot\scratch\EngineGate05R15PublicManifestBoundary"

Add-Type -Path "$workspaceRoot\WarEconomyMod\1.6\Assemblies\Newtonsoft.Json.dll"

$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Verify-File([string]$path, [string]$expectedSha, [long]$expectedSize) {
    if (-not (Test-Path $path)) { throw "File does not exist: $path" }
    $bytes = [System.IO.File]::ReadAllBytes($path)
    $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
    if ($bytes.Length -ne $expectedSize) {
        throw "Size mismatch for $path. Expected: $expectedSize, Actual: $($bytes.Length)"
    }
    if ($hash -ne $expectedSha) {
        throw "SHA256 mismatch for $path. Expected: $expectedSha, Actual: $hash"
    }
    Write-Host "[OK] $path (Size: $($bytes.Length), SHA: $hash)"
}

Write-Host "=== 1. Verifying COMPLETION.json ==="
$compJson = [System.IO.File]::ReadAllText("$taskDir\COMPLETION.json")
$comp = [Newtonsoft.Json.Linq.JObject]::Parse($compJson)
$artifacts = $comp["artifacts"]
Write-Host "Total artifacts in COMPLETION.json: $($artifacts.Count)"
foreach ($a in $artifacts) {
    Verify-File $a["path"].ToString() $a["sha256"].ToString() ([long]$a["size"])
}

Write-Host "`n=== 2. Verifying RELEASE_MANIFEST_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.json ==="
$relJson = [System.IO.File]::ReadAllText("$workspaceRoot\docs\RELEASE_MANIFEST_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.json")
$rel = [Newtonsoft.Json.Linq.JObject]::Parse($relJson)

$sel = $rel["selected_candidate"]
Verify-File (Join-Path $workspaceRoot $sel["dll_path"].ToString()) $sel["dll_sha256"].ToString() ([long]$sel["dll_bytes"])
Verify-File (Join-Path $workspaceRoot $sel["pdb_path"].ToString()) $sel["pdb_sha256"].ToString() ([long]$sel["pdb_bytes"])

$alt = $rel["alternate_candidate"]
Verify-File (Join-Path $workspaceRoot $alt["dll_path"].ToString()) $alt["dll_sha256"].ToString() ([long]$alt["dll_bytes"])
Verify-File (Join-Path $workspaceRoot $alt["pdb_path"].ToString()) $alt["pdb_sha256"].ToString() ([long]$alt["pdb_bytes"])

$dep = $rel["deployed_mod_assemblies"]
Verify-File (Join-Path $workspaceRoot $dep["dll_path"].ToString()) $dep["dll_sha256"].ToString() ([long]$dep["dll_bytes"])
Verify-File (Join-Path $workspaceRoot $dep["pdb_path"].ToString()) $dep["pdb_sha256"].ToString() ([long]$dep["pdb_bytes"])

foreach ($src in $rel["source_files"]) {
    Verify-File (Join-Path $workspaceRoot $src["path"].ToString()) $src["sha256"].ToString() ([long]$src["bytes"])
}

$evidence = $rel["verification_evidence"]
foreach ($prop in $evidence.Properties()) {
    $item = $prop.Value
    Verify-File (Join-Path $workspaceRoot $item["path"].ToString()) $item["sha256"].ToString() ([long]$item["bytes"])
}

Write-Host "`n=== 3. Verifying Prefix and Baseline Immutability ==="
$censusBytes = [System.IO.File]::ReadAllBytes("$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs")
$prefixBytes = New-Object byte[] 72547
[System.Array]::Copy($censusBytes, 0, $prefixBytes, 0, 72547)
$prefixHash = -join ($sha256.ComputeHash($prefixBytes) | ForEach-Object { $_.ToString("X2") })
$expectedPrefix = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
if ($prefixHash -ne $expectedPrefix) {
    throw "Census prefix mismatch! Expected: $expectedPrefix, Actual: $prefixHash"
}
Write-Host "[OK] Census prefix 72,547 bytes SHA-256: $prefixHash"

Verify-File "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.cs" "BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718" 156431
Verify-File "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052" 1774

Write-Host "`n=== 4. Verifying Test Results ==="
$resJson = [System.IO.File]::ReadAllText("$scratchDir\run_default\results.json")
$res = [Newtonsoft.Json.Linq.JObject]::Parse($resJson)
if ($res["overall_verdict"].ToString() -ne "PASS") { throw "Verdict is not PASS" }
if ([int]$res["failed_tests"] -ne 0) { throw "failed_tests > 0" }
if ([int]$res["passed_tests"] -ne 25) { throw "passed_tests != 25" }
Write-Host "[OK] Results: $($res["passed_tests"])/$($res["total_tests"]) PASS, verdict: $($res["overall_verdict"])"

Write-Host "`n>>> ALL CHECKS PASSED WITH 100% INTEGRITY! <<<"
