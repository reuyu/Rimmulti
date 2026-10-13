$files = @(
    "scratch\EngineGate05R11PolicyEncoding\Harness\Gate05R11PolicyRunner.csproj",
    "scratch\EngineGate05R11PolicyEncoding\Harness\Program.cs",
    "scratch\EngineGate05R11PolicyEncoding\results.json",
    "scratch\EngineGate05R11PolicyEncoding\raw_console.txt",
    "scratch\EngineGate05R11PolicyEncoding\CANDIDATE_PRE_RUN_MANIFEST.json",
    "scratch\EngineGate05R11PolicyEncoding\ENGINE_FREEZE_BEFORE.json",
    "scratch\EngineGate05R11PolicyEncoding\ENGINE_FREEZE_AFTER.json",
    "docs\POC_EngineHost_Content_Codec_Gate05_R11.md"
)

$sha = [System.Security.Cryptography.SHA256]::Create()
foreach ($f in $files) {
    $bytes = [System.IO.File]::ReadAllBytes($f)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    Write-Host "$f | Size: $($bytes.Length) | SHA256: $hash"
}
