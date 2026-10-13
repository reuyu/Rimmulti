$isoDir1 = 'C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch\WorkerData_Inst1'
$isoDir2 = 'C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch\WorkerData_Inst2'

if (Test-Path $isoDir1) { Remove-Item -Recurse -Force $isoDir1 }
if (Test-Path $isoDir2) { Remove-Item -Recurse -Force $isoDir2 }
New-Item -ItemType Directory -Force -Path $isoDir1 | Out-Null
New-Item -ItemType Directory -Force -Path $isoDir2 | Out-Null

$logPath1 = Join-Path $isoDir1 'player.log'
$logPath2 = Join-Path $isoDir2 'player.log'
$exePath = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe'

Write-Host "Launching Worker 1..."
$proc1 = Start-Process -FilePath $exePath -ArgumentList "-batchmode -savedatafolder=$isoDir1 -logfile `"$logPath1`"" -PassThru

Write-Host "Launching Worker 2..."
$proc2 = Start-Process -FilePath $exePath -ArgumentList "-batchmode -savedatafolder=$isoDir2 -logfile `"$logPath2`"" -PassThru

Start-Sleep -Seconds 8

Write-Host "Worker 1 (PID $($proc1.Id)): HasExited = $($proc1.HasExited)"
Write-Host "Worker 2 (PID $($proc2.Id)): HasExited = $($proc2.HasExited)"

if (!$proc1.HasExited -and !$proc2.HasExited) {
    Write-Host "SUCCESS: Both RimWorld worker processes are running concurrently!"
    $mem1 = (Get-Process -Id $proc1.Id).WorkingSet64 / 1MB
    $mem2 = (Get-Process -Id $proc2.Id).WorkingSet64 / 1MB
    Write-Host "Worker 1 Memory: $([math]::Round($mem1, 1)) MB"
    Write-Host "Worker 2 Memory: $([math]::Round($mem2, 1)) MB"
}

if (!$proc1.HasExited) { Stop-Process -Id $proc1.Id -Force }
if (!$proc2.HasExited) { Stop-Process -Id $proc2.Id -Force }
