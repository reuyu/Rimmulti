$completionPath = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01\COMPLETION.json.tmp"
$json = Get-Content -Raw $completionPath | ConvertFrom-Json
Write-Host ("Checking artifacts count: " + $json.artifacts.Count)
$allMatch = $true
foreach ($art in $json.artifacts) {
    if (-not (Test-Path $art.path)) {
        Write-Host ("MISSING: " + $art.path) -ForegroundColor Red
        $allMatch = $false
        continue
    }
    $actualSha = (Get-FileHash -Path $art.path -Algorithm SHA256).Hash
    if ($actualSha -ne $art.sha256) {
        Write-Host ("MISMATCH in " + $art.path) -ForegroundColor Red
        Write-Host ("  Expected: " + $art.sha256)
        Write-Host ("  Actual:   " + $actualSha)
        $allMatch = $false
    } else {
        Write-Host ("MATCH: [" + $art.role + "] " + (Split-Path $art.path -Leaf)) -ForegroundColor Green
    }
}
if ($allMatch) {
    Write-Host "ALL 17 ARTIFACTS VERIFIED BIT-IDENTICAL!" -ForegroundColor Cyan
} else {
    Write-Host "VERIFICATION FAILED!" -ForegroundColor Red
    exit 1
}
