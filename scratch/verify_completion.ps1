$json = Get-Content 'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-20261007-DIRECT-01/COMPLETION.json.tmp' -Raw | ConvertFrom-Json
$mismatches = 0
foreach ($art in $json.artifacts) {
    if (-not (Test-Path $art.path)) {
        Write-Host "MISSING FILE: $($art.path) ($($art.role))"
        $mismatches++
        continue
    }
    $actualHash = (Get-FileHash -Algorithm SHA256 $art.path).Hash
    if ($actualHash -ne $art.sha256) {
        Write-Host "HASH MISMATCH: $($art.path) expected $($art.sha256) got $actualHash"
        $mismatches++
    } else {
        Write-Host "OK: [$($art.role)] $([System.IO.Path]::GetFileName($art.path)) (SHA: $($actualHash.Substring(0, 12)))"
    }
}
Write-Host "Total artifacts: $($json.artifacts.Count), Mismatches: $mismatches"
