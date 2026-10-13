$completionPath = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01\COMPLETION.json"
$json = Get-Content -Raw $completionPath | ConvertFrom-Json
Write-Host ("Checking Pipeline REV6-R1 artifacts count: " + $json.artifacts.Count)
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
        $allMatch = $false
    }
}
if ($allMatch) {
    Write-Host "ALL 17 PIPELINE REV6-R1 ARTIFACTS VERIFIED BIT-IDENTICAL PRESERVED!" -ForegroundColor Green
} else {
    Write-Host "PIPELINE VERIFICATION FAILED!" -ForegroundColor Red
    exit 1
}
