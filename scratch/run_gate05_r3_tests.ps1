$exe = Resolve-Path "scratch/EngineGate05R3/bin/Debug/net472/Gate05R3TestRunner.exe"
$out = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R3\raw_console.txt"
$err = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R3\raw_error.txt"

$proc = Start-Process -FilePath $exe -NoNewWindow -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
$proc.WaitForExit()
Write-Output "ExitCode=$($proc.ExitCode)"
Get-Content $out
if (Test-Path $err) {
    $errContent = Get-Content $err
    if ($errContent) {
        Write-Output "--- STDERR ---"
        Write-Output $errContent
    }
}
