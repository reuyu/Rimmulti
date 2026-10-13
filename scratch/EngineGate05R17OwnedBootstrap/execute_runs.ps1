$baseDir = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R17OwnedBootstrap"
$exe = "$baseDir\Harness\bin\Debug\net472\Gate05R17BootstrapRunner.exe"

$runs = @(
    @{ Name = "run_default"; Culture = "en-US" },
    @{ Name = "run_en_us"; Culture = "en-US" },
    @{ Name = "run_de_de"; Culture = "de-DE" }
)

foreach ($r in $runs) {
    $dir = "$baseDir\$($r.Name)"
    if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
    New-Item -ItemType Directory -Path $dir -Force | Out-Null

    Write-Host "Executing $($r.Name) with culture $($r.Culture)..."
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $exe
    $pinfo.Arguments = "`"$dir`""
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true

    $p = [System.Diagnostics.Process]::Start($pinfo)
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()

    Set-Content -Path "$dir\stdout.txt" -Value $stdout
    Set-Content -Path "$dir\stderr.txt" -Value $stderr

    Write-Host "  ExitCode: $($p.ExitCode)"
    if ($p.ExitCode -ne 0) {
        Write-Error "Run $($r.Name) failed with exit code $($p.ExitCode)!"
        exit $p.ExitCode
    }
}

Write-Host "All test runs completed successfully."
