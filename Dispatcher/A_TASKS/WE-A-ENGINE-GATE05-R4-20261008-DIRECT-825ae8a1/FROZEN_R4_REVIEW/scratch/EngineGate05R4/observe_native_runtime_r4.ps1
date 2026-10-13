# Powershell script to setup RuntimeCopy and observe isolated native execution for Gate05-R4
$ErrorActionPreference = 'Continue'

$steamDir = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld'
$baseR4Dir = 'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R4'
$runtimeDir = Join-Path $baseR4Dir 'RuntimeCopy'
$logFile = Join-Path $baseR4Dir 'native_execution_observation.txt'
$candidateDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
$candidatePdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'

$sb = [System.Text.StringBuilder]::new()
$sb.AppendLine("=== Native Runtime Execution Observation (Gate05-R4 / WP_ENGINE_GATE05_R4) ===") | Out-Null
$sb.AppendLine("Timestamp: $([DateTime]::UtcNow.ToString('O'))") | Out-Null
$sb.AppendLine("Target Isolated Directory: $runtimeDir") | Out-Null
$sb.AppendLine("Rule: Never execute Steam original directory; isolate executable, userdata, and mod under RuntimeCopy.") | Out-Null

# 1. Setup RuntimeCopy structure
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
}

$modDestDir = Join-Path $runtimeDir 'Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies'
New-Item -ItemType Directory -Path $modDestDir -Force | Out-Null

# Copy essential root binaries from Steam as approved copy source (Read-only source)
$binFiles = @('RimWorldWin64.exe', 'UnityPlayer.dll', 'UnityCrashHandler64.exe', 'steam_appid.txt', 'Version.txt')
foreach ($bf in $binFiles) {
    $src = Join-Path $steamDir $bf
    $dst = Join-Path $runtimeDir $bf
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Force
        $h = (Get-FileHash $dst -Algorithm SHA256).Hash
        $sz = (Get-Item $dst).Length
        $sb.AppendLine("Copied Runtime Binary: '$bf' (SHA256=$h, Size=$sz)") | Out-Null
    } else {
        $sb.AppendLine("Source Binary Not Found: '$bf'") | Out-Null
    }
}

# Copy R4 selected candidate into RuntimeCopy mod directory
Copy-Item -Path $candidateDll -Destination (Join-Path $modDestDir 'WarEconomy.WorkerBridge.PoC.dll') -Force
Copy-Item -Path $candidatePdb -Destination (Join-Path $modDestDir 'WarEconomy.WorkerBridge.PoC.pdb') -Force
$candDllHash = (Get-FileHash (Join-Path $modDestDir 'WarEconomy.WorkerBridge.PoC.dll') -Algorithm SHA256).Hash
$candDllSize = (Get-Item (Join-Path $modDestDir 'WarEconomy.WorkerBridge.PoC.dll')).Length
$sb.AppendLine("Deployed Selected R4 Candidate: 'WarEconomy.WorkerBridge.PoC.dll' (SHA256=$candDllHash, Size=$candDllSize)") | Out-Null

# 2. Record Steam Installed DLL discrepancy (UNKNOWN OPEN Incident)
$steamInstalledDll = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
if (Test-Path $steamInstalledDll) {
    $sInstHash = (Get-FileHash $steamInstalledDll -Algorithm SHA256).Hash
    $sInstSize = (Get-Item $steamInstalledDll).Length
    $sb.AppendLine("Steam Installed Mod DLL: '$steamInstalledDll' (SHA256=$sInstHash, Size=$sInstSize) [UNKNOWN OPEN INCIDENT: Preserved unmodified per Master policy]") | Out-Null
}

# 3. Isolated Native Execution Observation
$isolatedExe = Join-Path $runtimeDir 'RimWorldWin64.exe'
$userDataDir = Join-Path $runtimeDir 'UserData'
New-Item -ItemType Directory -Path $userDataDir -Force | Out-Null

$sb.AppendLine("Execution Attempt: '$isolatedExe' -batchmode -nographics -savedatafolder='$userDataDir'") | Out-Null

try {
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $isolatedExe
    $psi.Arguments = "-batchmode -nographics -savedatafolder=`"$userDataDir`""
    $psi.WorkingDirectory = $runtimeDir
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $p = [System.Diagnostics.Process]::Start($psi)
    $procId = $p.Id
    $startTime = $p.StartTime.ToUniversalTime().ToString('O')
    $sb.AppendLine("Started Isolated Process: PID=$procId, StartTimeUtc=$startTime, Cwd='$runtimeDir'") | Out-Null

    # Observe for up to 5000ms
    $exited = $p.WaitForExit(5000)
    $sw.Stop()

    if ($exited) {
        $sb.AppendLine("Process Exited within $($sw.ElapsedMilliseconds)ms: ExitCode=$($p.ExitCode)") | Out-Null
        $stdout = $p.StandardOutput.ReadToEnd()
        $stderr = $p.StandardError.ReadToEnd()
        if (-not [string]::IsNullOrEmpty($stdout)) { $sb.AppendLine("Stdout: $stdout") | Out-Null }
        if (-not [string]::IsNullOrEmpty($stderr)) { $sb.AppendLine("Stderr: $stderr") | Out-Null }
    } else {
        $sb.AppendLine("Process Still Running after 5000ms. Terminating observed test process cleanly...") | Out-Null
        $p.Kill()
        $p.WaitForExit()
        $sb.AppendLine("Terminated PID=$procId cleanly (Managed child lifecycle enforced).") | Out-Null
    }
} catch {
    $sb.AppendLine("Execution Observation Exception: $($_.Exception.Message)") | Out-Null
}

$sb.AppendLine("Classification: NATIVE_UNTESTED / BLOCKER_UNKNOWN") | Out-Null
$sb.AppendLine("Observation Summary: Standalone isolated execution under project scratch RuntimeCopy observed with exact PID, exit code, and managed process termination. Because game content data directories (Data/Managed) were not fully linked into RuntimeCopy, complete mod assembly loading and in-engine semantic progression was not fully executed in native environment.") | Out-Null
$sb.AppendLine("Limitation: Native gate PASS cannot be declared based solely on component harness results. Verdict declared as IMPLEMENTATION_PARTIAL with NATIVE_UNTESTED / BLOCKER_UNKNOWN status.") | Out-Null

[System.IO.File]::WriteAllText($logFile, $sb.ToString())
Write-Output "Observation written to $logFile"
Get-Content $logFile
