$bytes = [System.IO.File]::ReadAllBytes('scratch/WorkerBridgeMod/Source/EngineHostCensus.cs')
$prefix = New-Object byte[] 72547
[System.Array]::Copy($bytes, 0, $prefix, 0, 72547)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = [System.BitConverter]::ToString($sha.ComputeHash($prefix)).Replace('-', '')
Write-Host "Prefix Length: $($prefix.Length)"
Write-Host "Prefix SHA256: $hash"
$marker = [System.Text.Encoding]::UTF8.GetString($bytes, 72540, 30)
Write-Host "Marker at 72540: $marker"
