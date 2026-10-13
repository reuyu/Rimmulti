$bytes = [System.IO.File]::ReadAllBytes("scratch\WorkerBridgeMod\Source\EngineHostCensus.cs")
$prefix = New-Object byte[] 72547
[System.Array]::Copy($bytes, $prefix, 72547)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = [System.BitConverter]::ToString($sha.ComputeHash($prefix)).Replace("-", "")
Write-Host "Prefix Hash: $hash"
Write-Host "Matches Expected: $($hash -ieq 'F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887')"
