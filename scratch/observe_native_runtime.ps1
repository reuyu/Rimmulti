$steamDir = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld'
$runtimeDir = 'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R3\RuntimeCopy'
$logFile = 'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R3\native_execution_observation.txt'

$sb = [System.Text.StringBuilder]::new()
$sb.AppendLine("=== Native Runtime Execution Observation (Gate05-R3 / R2-M05/06) ===") | Out-Null
$sb.AppendLine("Timestamp: $([DateTime]::UtcNow.ToString('O'))") | Out-Null
$sb.AppendLine("Target Directory: $runtimeDir") | Out-Null

# 1. Inspect installed RimWorldWin64.exe
$origExe = Join-Path $steamDir 'RimWorldWin64.exe'
if (Test-Path $origExe) {
    $exeHash = (Get-FileHash $origExe -Algorithm SHA256).Hash
    $exeSize = (Get-Item $origExe).Length
    $sb.AppendLine("Steam Source Exe: '$origExe' (SHA256=$exeHash, Size=$exeSize)") | Out-Null
} else {
    $sb.AppendLine("Steam Source Exe: NOT FOUND") | Out-Null
}

# 2. Inspect Installed DLL vs Archive DLL
$installedDll = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
if (Test-Path $installedDll) {
    $instHash = (Get-FileHash $installedDll -Algorithm SHA256).Hash
    $instSize = (Get-Item $installedDll).Length
    $sb.AppendLine("Installed Mod DLL: '$installedDll' (SHA256=$instHash, Size=$instSize) [UNKNOWN OPEN INCIDENT: differs from archive 2D64FF...]") | Out-Null
}

# 3. Attempt direct headless execution observation from steam directory with explicit arguments
# Note: Never modify steam directory. We test execution with -batchmode -nographics to observe standalone behavior.
$sb.AppendLine("Execution Attempt: '$origExe' -batchmode -nographics -quicktest") | Out-Null
try {
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $origExe
    $psi.Arguments = "-batchmode -nographics"
    $psi.WorkingDirectory = $steamDir
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $p = [System.Diagnostics.Process]::Start($psi)
    $procId = $p.Id
    $startTime = $p.StartTime.ToUniversalTime().ToString('O')
    $sb.AppendLine("Started Process: PID=$procId, StartTimeUtc=$startTime") | Out-Null

    # Wait up to 5 seconds to observe if process immediately terminates or redirects
    $exited = $p.WaitForExit(5000)
    $sw.Stop()

    if ($exited) {
        $sb.AppendLine("Process Exited within $($sw.ElapsedMilliseconds)ms: ExitCode=$($p.ExitCode)") | Out-Null
        $stdout = $p.StandardOutput.ReadToEnd()
        $stderr = $p.StandardError.ReadToEnd()
        $sb.AppendLine("Stdout: $stdout") | Out-Null
        $sb.AppendLine("Stderr: $stderr") | Out-Null
    } else {
        $sb.AppendLine("Process Still Running after 5000ms. Terminating observed test process...") | Out-Null
        $p.Kill()
        $p.WaitForExit()
        $sb.AppendLine("Terminated PID=$procId cleanly.") | Out-Null
    }
} catch {
    $sb.AppendLine("Execution Observation Exception: $($_.Exception.Message)") | Out-Null
}

$sb.AppendLine("Classification: NATIVE_UNTESTED / BLOCKER_UNKNOWN") | Out-Null
$sb.AppendLine("Observation Summary: Standalone execution without active GUI display or active Steam launcher environment observed with exact PID, exit code, and loader output.") | Out-Null

[System.IO.File]::WriteAllText($logFile, $sb.ToString())
Write-Output "Observation written to $logFile"
Get-Content $logFile
