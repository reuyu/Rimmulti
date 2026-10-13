$beforePath = 'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_ENGINE_FREEZE_BEFORE.json'
$beforeJson = Get-Content $beforePath -Raw | ConvertFrom-Json

$afterEntries = [System.Collections.Generic.List[PSCustomObject]]::new()
$mismatches = 0

foreach ($f in $beforeJson.files) {
    $p = $f.path
    if (-not (Test-Path $p)) {
        Write-Host "MISSING: $p"
        $mismatches++
        continue
    }
    $expected = if ($f.expected) { $f.expected } else { $f.sha256 }
    $actual = (Get-FileHash -Algorithm SHA256 $p).Hash

    if ($actual -ne $expected) {
        Write-Host "MUTATION DETECTED: $p expected $expected got $actual"
        $mismatches++
    }

    $afterEntries.Add([PSCustomObject]@{
        path = $p
        expected = $expected
        actual = $actual
    })
}

$afterObj = [PSCustomObject]@{
    at = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.ffffffzzz")
    files = $afterEntries
}

$afterPath = 'scratch/MASTER_ENGINE_FREEZE_AFTER_REV6_R1.json'
$afterObj | ConvertTo-Json -Depth 5 | Set-Content $afterPath -Encoding UTF8

Write-Host "Total checked: $($afterEntries.Count), Mismatches: $mismatches"
if ($mismatches -eq 0) {
    Write-Host "GATE05 FREEZE INVARIANT 100% PRESERVED."
} else {
    Write-Host "GATE05 FREEZE INVARIANT BROKEN!"
    exit 1
}
