$json = Get-Content "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\COMPLETION.json" -Raw | ConvertFrom-Json
$sha = [System.Security.Cryptography.SHA256]::Create()
$allPass = $true

Write-Host "Verifying $($json.artifacts.Count) artifacts in COMPLETION.json..."

foreach ($a in $json.artifacts) {
    if (-not (Test-Path $a.path)) {
        Write-Host "[FAIL] Missing file: $($a.path)"
        $allPass = $false
        continue
    }
    $bytes = [System.IO.File]::ReadAllBytes($a.path)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    if ($bytes.Length -ne $a.size) {
        Write-Host "[FAIL] Size mismatch on $($a.role): declared $($a.size), actual $($bytes.Length)"
        $allPass = $false
    } elseif ($hash -ne $a.sha256) {
        Write-Host "[FAIL] SHA mismatch on $($a.role): declared $($a.sha256), actual $hash"
        $allPass = $false
    } else {
        Write-Host "[PASS] $($a.role) ($($a.size) bytes, SHA: $hash)"
    }
}

if ($allPass) {
    Write-Host "`n>>> ALL 21 ARTIFACTS VERIFIED 100% MATCH! <<<"
} else {
    Write-Host "`n>>> VERIFICATION FAILED! <<<"
}
