$sha = [System.Security.Cryptography.SHA256]::Create()
$completionPath = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6\COMPLETION.json"
$completion = Get-Content -Raw $completionPath | ConvertFrom-Json

$allMatch = $true
$count = 0

Write-Host "Verifying all $($completion.artifacts.Count) artifacts in COMPLETION.json against disk..."

foreach ($art in $completion.artifacts) {
    $count++
    if (-not (Test-Path $art.path)) {
        Write-Host "[FAIL] Missing file on disk: $($art.path)" -ForegroundColor Red
        $allMatch = $false
        continue
    }

    $bytes = [System.IO.File]::ReadAllBytes($art.path)
    $actualHash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $actualSize = $bytes.Length

    $hashMatch = ($actualHash -ieq $art.sha256)
    $sizeMatch = ($actualSize -eq $art.size)

    if ($hashMatch -and $sizeMatch) {
        Write-Host "[$count/21 PASS] $($art.role) -> $($art.sha256) ($($art.size) bytes)" -ForegroundColor Green
    } else {
        Write-Host "[$count/21 FAIL] $($art.role) -> Expected SHA: $($art.sha256) Got: $actualHash | Expected Size: $($art.size) Got: $actualSize" -ForegroundColor Red
        $allMatch = $false
    }
}

if ($allMatch) {
    Write-Host "`n>>> 100% VERIFICATION SUCCESS: All 21 artifacts match perfectly! <<<" -ForegroundColor Cyan
} else {
    Write-Host "`n>>> VERIFICATION FAILED: Mismatches detected! <<<" -ForegroundColor Red
    exit 1
}
