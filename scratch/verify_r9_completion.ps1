$completionPath = 'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b\COMPLETION.json'
$json = Get-Content $completionPath -Raw | ConvertFrom-Json
$artifacts = $json.artifacts

$allMatch = $true
$count = 0

foreach ($art in $artifacts) {
    $count++
    if (!(Test-Path $art.path)) {
        Write-Output ("FAILED: Missing file: " + $art.path)
        $allMatch = $false
        continue
    }
    $h = (Get-FileHash $art.path -Algorithm SHA256).Hash
    $s = (Get-Item $art.path).Length
    if ($h -ne $art.sha256) {
        Write-Output ("FAILED: SHA mismatch on " + $art.path + " Expected: " + $art.sha256 + " Actual: " + $h)
        $allMatch = $false
    }
    if ($s -ne $art.size) {
        Write-Output ("FAILED: Size mismatch on " + $art.path + " Expected: " + $art.size + " Actual: " + $s)
        $allMatch = $false
    }
}

if ($allMatch) {
    Write-Output ("SUCCESS: All " + $count + " artifacts matched 100% in SHA256 and size!")
} else {
    Write-Output "VERIFICATION FAILED."
}
