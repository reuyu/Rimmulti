$raw = [System.IO.File]::ReadAllText('scratch\WorkerBridgeMod\Source\EngineHostCensus.cs', [System.Text.Encoding]::UTF8)
$marker = "    public static class ContentProfileProvider"
$idx = $raw.IndexOf($marker)
$prefix = $raw.Substring(0, $idx)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($prefix)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '')
Write-Output "Prefix Length: $($prefix.Length), Hash: $hash"
Write-Output "Target Hash:   F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
Write-Output "Matched:       $($hash -eq 'F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887')"
