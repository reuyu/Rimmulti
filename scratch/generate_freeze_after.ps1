$archiveManifest = Get-Content 'Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json' | ConvertFrom-Json
$records = @()
foreach ($f in $archiveManifest.files) {
    $archPath = $f.archive_path
    $exp = $f.sha256
    $act = (Get-FileHash $archPath -Algorithm SHA256).Hash
    $records += [PSCustomObject]@{
        archive_path = $archPath
        original_path = $f.original_path
        expected = $exp
        actual = $act
        matched = ($exp -eq $act)
    }
}

$output = [PSCustomObject]@{
    at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.ffffffzzz")
    total_files = $records.Count
    all_matched = (($records | Where-Object { -not $_.matched }).Count -eq 0)
    files = $records
}

$output | ConvertTo-Json -Depth 5 | Set-Content 'scratch\MASTER_ENGINE_FREEZE_AFTER_GATE05_R1.json' -Encoding UTF8
Write-Host "Generated scratch\MASTER_ENGINE_FREEZE_AFTER_GATE05_R1.json. all_matched: $($output.all_matched)"
$hash = (Get-FileHash 'scratch\MASTER_ENGINE_FREEZE_AFTER_GATE05_R1.json' -Algorithm SHA256).Hash
Write-Host "SHA256: $hash"
