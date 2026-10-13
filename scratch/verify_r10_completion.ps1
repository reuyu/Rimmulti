$completionPath = 'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\COMPLETION.json'
$json = Get-Content $completionPath -Raw | ConvertFrom-Json

Write-Host "Verifying COMPLETION.json: $($json.dispatch_id)"
Write-Host "Verdict: $($json.e1_verdict)"
Write-Host "Artifacts count: $($json.artifacts.Count)"

$failed = 0
foreach ($a in $json.artifacts) {
    if (!(Test-Path $a.path)) {
        Write-Host "[FAIL] Missing file: $($a.path)"
        $failed++
        continue
    }
    $actualHash = (Get-FileHash $a.path -Algorithm SHA256).Hash
    $actualSize = (Get-Item $a.path).Length
    if ($actualHash -ne $a.sha256) {
        Write-Host "[FAIL] Hash mismatch for $($a.role): expected $($a.sha256), actual $actualHash"
        $failed++
    } elseif ($actualSize -ne $a.size) {
        Write-Host "[FAIL] Size mismatch for $($a.role): expected $($a.size), actual $actualSize"
        $failed++
    } else {
        Write-Host "[OK] $($a.role): size=$actualSize, sha=$actualHash"
    }
}

# Prefix check
$censusPath = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs'
$bytes = [System.IO.File]::ReadAllBytes($censusPath)
$sub = New-Object byte[] 72547
[System.Array]::Copy($bytes, 0, $sub, 0, 72547)
$sha = [System.Security.Cryptography.SHA256]::Create()
$prefixHash = [System.BitConverter]::ToString($sha.ComputeHash($sub)).Replace('-', '')
if ($prefixHash -ne 'F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887') {
    Write-Host "[FAIL] Prefix hash mismatch: $prefixHash"
    $failed++
} else {
    Write-Host "[OK] Census prefix (72547 bytes) verified: $prefixHash"
}

if ($failed -eq 0) {
    Write-Host "=== ALL VERIFICATIONS PASSED (0 ERRORS) ==="
} else {
    Write-Host "=== VERIFICATION FAILED WITH $failed ERRORS ==="
    exit 1
}
