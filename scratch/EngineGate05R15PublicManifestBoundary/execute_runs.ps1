$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$scratchDir = "$workspaceRoot\scratch\EngineGate05R15PublicManifestBoundary"
$runnerExe = "$scratchDir\Harness\bin\Debug\net472\Gate05R15BoundaryRunner.exe"

if (-not (Test-Path $runnerExe)) {
    throw "Runner exe not found: $runnerExe"
}

$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Build-DirectoryInventory([string]$dirPath, [string]$inventoryFileName) {
    $files = Get-ChildItem -Path $dirPath -File -Recurse | Where-Object { $_.Name -ne $inventoryFileName } | Sort-Object FullName
    $items = @()
    foreach ($f in $files) {
        $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
        $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
        $relPath = $f.FullName.Substring($dirPath.Length).TrimStart('\', '/')
        $items += [ordered]@{
            relative_path = $relPath
            sha256 = $hash
            size = $bytes.Length
        }
    }
    $inv = [ordered]@{
        directory = $dirPath
        captured_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        file_count = $items.Count
        files = $items
    }
    $json = $inv | ConvertTo-Json -Depth 5
    $invPath = Join-Path $dirPath $inventoryFileName
    [System.IO.File]::WriteAllText($invPath, $json, [System.Text.Encoding]::UTF8)

    $invBytes = [System.IO.File]::ReadAllBytes($invPath)
    $invHash = -join ($sha256.ComputeHash($invBytes) | ForEach-Object { $_.ToString("X2") })
    Write-Host "Generated inventory for $dirPath ($($items.Count) files) -> SHA: $invHash"
    return @{ path = $invPath; sha256 = $invHash; size = $invBytes.Length }
}

function Run-ProcessRun([string]$runDirName, [string]$culture) {
    $runDir = Join-Path $scratchDir $runDirName
    if (-not (Test-Path $runDir)) {
        New-Item -ItemType Directory -Path $runDir -Force | Out-Null
    }

    $resultsJson = Join-Path $runDir "results.json"
    $ledgerJson = Join-Path $runDir "api_ledger.json"
    $rawConsole = Join-Path $runDir "raw_console.txt"

    $argsList = @(
        "--output-json=$resultsJson",
        "--output-ledger=$ledgerJson"
    )
    if (![string]::IsNullOrEmpty($culture)) {
        $argsList += "--culture=$culture"
    }

    $cmdLineArgs = [string]::Join(" ", $argsList)
    Write-Host "Starting run $runDirName (Culture: $culture) with args: $cmdLineArgs"

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $startTimeUtc = (Get-Date).ToUniversalTime().ToString("o")

    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $runnerExe
    $pinfo.Arguments = $cmdLineArgs
    $pinfo.WorkingDirectory = $scratchDir
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true

    $proc = [System.Diagnostics.Process]::Start($pinfo)
    $pidNum = $proc.Id

    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()

    $proc.WaitForExit()
    $sw.Stop()
    $endTimeUtc = (Get-Date).ToUniversalTime().ToString("o")

    $stdoutText = $stdoutTask.Result
    $stderrText = $stderrTask.Result
    $fullRaw = $stdoutText
    if (![string]::IsNullOrEmpty($stderrText)) {
        $fullRaw += "`r`nSTDERR:`r`n" + $stderrText
    }
    [System.IO.File]::WriteAllText($rawConsole, $fullRaw, [System.Text.Encoding]::UTF8)

    $exitCode = $proc.ExitCode
    Write-Host "Process $runDirName exited with code $exitCode in $($sw.ElapsedMilliseconds)ms (PID: $pidNum)"

    $meta = [ordered]@{
        run_name = $runDirName
        culture = if ([string]::IsNullOrEmpty($culture)) { "ko-KR (default)" } else { $culture }
        pid = $pidNum
        exit_code = $exitCode
        start_time_utc = $startTimeUtc
        end_time_utc = $endTimeUtc
        elapsed_ms = $sw.ElapsedMilliseconds
        arguments = $argsList
        working_directory = $scratchDir
        runner_executable = $runnerExe
    }
    $metaJson = $meta | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText((Join-Path $runDir "PROCESS_METADATA.json"), $metaJson, [System.Text.Encoding]::UTF8)

    # Build directory inventory and freeze before next run
    $invResult = Build-DirectoryInventory $runDir "OUTPUT_INVENTORY.json"

    if ($exitCode -ne 0) {
        throw "Run $runDirName failed with exit code $exitCode"
    }

    return [ordered]@{
        run_name = $runDirName
        culture = $culture
        exit_code = $exitCode
        pid = $pidNum
        elapsed_ms = $sw.ElapsedMilliseconds
        inventory_sha256 = $invResult.sha256
    }
}

# Run 1: default (ko-KR)
$run1 = Run-ProcessRun "run_default" ""

# Run 2: en-US
$run2 = Run-ProcessRun "run_en_us" "en-US"

# Run 3: de-DE
$run3 = Run-ProcessRun "run_de_de" "de-DE"

Write-Host "All 3 process runs completed with exit code 0!"
