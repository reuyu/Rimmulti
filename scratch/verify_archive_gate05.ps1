$manifestPath = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json"
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
Write-Host ("Checking historical archive files count: " + $manifest.files.Count)
$allOk = $true
foreach ($file in $manifest.files) {
    if (-not (Test-Path $file.archive_path)) {
        Write-Host ("MISSING ARCHIVE FILE: " + $file.archive_path) -ForegroundColor Red
        $allOk = $false
        continue
    }
    $sha = (Get-FileHash -Path $file.archive_path -Algorithm SHA256).Hash
    if ($sha -ne $file.sha256) {
        Write-Host ("MISMATCH: " + $file.archive_path) -ForegroundColor Red
        $allOk = $false
    }
}
if ($allOk) {
    Write-Host "ALL 19 HISTORICAL BASELINE ARCHIVE FILES 100% BIT-IDENTICAL PRESERVED!" -ForegroundColor Green
} else {
    Write-Host "ARCHIVE VERIFICATION FAILED!" -ForegroundColor Red
    exit 1
}
