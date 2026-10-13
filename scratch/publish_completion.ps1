$tmp = 'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-20261007-DIRECT-01/COMPLETION.json.tmp'
$target = 'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-20261007-DIRECT-01/COMPLETION.json'

if (-not (Test-Path $tmp)) {
    Write-Host "ERROR: $tmp does not exist!"
    exit 1
}

Move-Item -Path $tmp -Destination $target -Force

if (Test-Path $target) {
    $hash = (Get-FileHash -Algorithm SHA256 $target).Hash
    Write-Host "SUCCESS: Published $target (SHA: $hash)"
} else {
    Write-Host "ERROR: Failed to publish $target"
    exit 1
}
