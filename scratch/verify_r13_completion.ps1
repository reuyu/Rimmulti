$compPath = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749\COMPLETION.json"
$relPath = "docs\RELEASE_MANIFEST_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE.json"

Write-Host "=== VERIFYING R13 COMPLETION AND RELEASE MANIFEST ==="

# 1. Parse JSON files
$comp = Get-Content $compPath -Raw | ConvertFrom-Json
$rel = Get-Content $relPath -Raw | ConvertFrom-Json

Write-Host "COMPLETION.json Status: $($comp.status), Verdict: $($comp.e1_verdict), Artifacts Count: $($comp.artifacts.Count)"
Write-Host "RELEASE_MANIFEST Linage: $($rel.candidate_lineage), Total Tests: $($rel.execution_summary.total_tests), Passed: $($rel.execution_summary.passed_tests)"

$sha = [System.Security.Cryptography.SHA256]::Create()
$allPass = $true

# 2. Check each artifact in COMPLETION.json
foreach ($art in $comp.artifacts) {
    if (-not (Test-Path $art.path)) {
        Write-Host "FAILED: Artifact not found: $($art.path)" -ForegroundColor Red
        $allPass = $false
        continue
    }
    $bytes = [System.IO.File]::ReadAllBytes($art.path)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    if ($bytes.Length -ne $art.size) {
        Write-Host "FAILED: Size mismatch for $($art.role) ($($art.path)): expected $($art.size), got $($bytes.Length)" -ForegroundColor Red
        $allPass = $false
    }
    if ($hash -ne $art.sha256) {
        Write-Host "FAILED: Hash mismatch for $($art.role) ($($art.path)): expected $($art.sha256), got $hash" -ForegroundColor Red
        $allPass = $false
    }
    if ($art.mvid) {
        $mod = [System.Reflection.Assembly]::LoadFile($art.path).ManifestModule
        if ($mod.ModuleVersionId.ToString() -ne $art.mvid) {
            Write-Host "FAILED: MVID mismatch for $($art.role): expected $($art.mvid), got $($mod.ModuleVersionId)" -ForegroundColor Red
            $allPass = $false
        }
    }
    Write-Host "PASS: [$($art.role)] $($art.size) bytes, SHA: $($hash.Substring(0, 16))..."
}

# 3. Check Census prefix immutability
$censusBytes = [System.IO.File]::ReadAllBytes((Resolve-Path "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs").Path)
$prefix = New-Object byte[] 72547
[System.Array]::Copy($censusBytes, 0, $prefix, 0, 72547)
$prefixHash = [System.BitConverter]::ToString($sha.ComputeHash($prefix)).Replace("-", "")
if ($prefixHash -ne "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887") {
    Write-Host "FAILED: EngineHostCensus.cs prefix hash mismatch: $prefixHash" -ForegroundColor Red
    $allPass = $false
} else {
    Write-Host "PASS: EngineHostCensus.cs prefix 72547 bytes SHA match: $prefixHash"
}

# 4. Check WorkerBridge.cs and WorkerBridge.csproj
$wbHash = (Get-FileHash "scratch\WorkerBridgeMod\Source\WorkerBridge.cs" -Algorithm SHA256).Hash
$projHash = (Get-FileHash "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" -Algorithm SHA256).Hash
if ($wbHash -ne "BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718") {
    Write-Host "FAILED: WorkerBridge.cs hash mismatch: $wbHash" -ForegroundColor Red
    $allPass = $false
} else {
    Write-Host "PASS: WorkerBridge.cs SHA match: $wbHash"
}
if ($projHash -ne "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052") {
    Write-Host "FAILED: WorkerBridge.csproj hash mismatch: $projHash" -ForegroundColor Red
    $allPass = $false
} else {
    Write-Host "PASS: WorkerBridge.csproj SHA match: $projHash"
}

if ($allPass) {
    Write-Host "ALL CHECKS PASSED: 100% ARTIFACT AND BASELINE INTEGRITY VERIFIED!" -ForegroundColor Green
} else {
    Write-Host "SOME CHECKS FAILED!" -ForegroundColor Red
    exit 1
}
