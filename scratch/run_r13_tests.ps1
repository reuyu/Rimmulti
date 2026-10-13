$runner = "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\bin\Debug\net472\Gate05R13CacheRunner.exe"
$outJson = "scratch\EngineGate05R13PolicyCacheLifecycle\results.json"
$outConsole = "scratch\EngineGate05R13PolicyCacheLifecycle\raw_console.txt"

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = (Resolve-Path $runner).Path
$psi.Arguments = "--output-json=$outJson"
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8

$p = [System.Diagnostics.Process]::Start($psi)
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
$p.WaitForExit()

$fullOutput = $stdout
if ($stderr) {
    $fullOutput += "`nSTDERR:`n" + $stderr
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Resolve-Path ".").Path + "\" + $outConsole, $fullOutput, $utf8NoBom)

Write-Host "Process Exit Code: $($p.ExitCode)"
Write-Host $fullOutput
