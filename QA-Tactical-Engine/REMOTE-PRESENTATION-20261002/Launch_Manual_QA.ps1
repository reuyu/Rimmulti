$ErrorActionPreference = 'Stop'
$qaRoot = $PSScriptRoot
$qaSession = Join-Path $qaRoot 'ManualSession3'
$qaGame = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe'
$qaPython = 'C:\Users\user\anaconda3\python.exe'
if (Test-Path -LiteralPath (Join-Path $qaSession 'launch-pair.json')) { throw 'This isolated session has already been launched. Ask QA for a new session instead of opening duplicate processes.' }
& $qaPython (Join-Path $qaRoot 'verify_candidate.py')
if ($LASTEXITCODE -ne 0) { throw 'Frozen candidate hash mismatch.' }
$qaWorkerProfile = Join-Path $qaSession 'Worker'
$qaClientProfile = Join-Path $qaSession 'GraphicalClient'
$qaWorker = $null
$qaClient = $null
try {
    Write-Host 'Starting isolated Tactical Worker and visible RimWorld client...'
    $qaWorkerArgs = @("-savedatafolder=$qaWorkerProfile", '-logfile', (Join-Path $qaWorkerProfile 'player.log'), '-batchmode', '-nographics', '-remote-worker', '-worker-port', '29800', '-qa-port', '31700')
    $qaClientArgs = @("-savedatafolder=$qaClientProfile", '-logfile', (Join-Path $qaClientProfile 'player.log'), '-remote-client', '-client-port', '29801', '-connect', '127.0.0.1:29800', '-qa-port', '31701', '-screen-fullscreen', '0', '-screen-width', '1280', '-screen-height', '900')
    $qaWorker = Start-Process -FilePath $qaGame -ArgumentList $qaWorkerArgs -WindowStyle Hidden -PassThru
    $qaClient = Start-Process -FilePath $qaGame -ArgumentList $qaClientArgs -WindowStyle Normal -PassThru
    @{WorkerPid=$qaWorker.Id;ClientPid=$qaClient.Id;WorkerArgs=$qaWorkerArgs;ClientArgs=$qaClientArgs;LaunchMethod='User double-click / Start-Process Normal';Utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $qaSession 'launch-pair.json') -Encoding UTF8
    @{path=$qaSession;reason='User-launched interactive graphical session.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $qaRoot 'current-manual-session.json') -Encoding UTF8
    & $qaPython (Join-Path $qaRoot 'attach_user_session.py')
    if ($LASTEXITCODE -ne 0) { throw 'Test map loading or Worker connection failed. See the preserved QA log.' }
    Write-Host 'Ready. Use the RimWorld window for the manual checklist. These QA processes remain running for your test.'
} catch {
    Write-Host $_
    if ($null -ne $qaClient -and -not $qaClient.HasExited) { $qaClient.Kill() }
    if ($null -ne $qaWorker -and -not $qaWorker.HasExited) { $qaWorker.Kill() }
    exit 1
}
