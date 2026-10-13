$steamDir = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld'
$exe = Join-Path $steamDir 'RimWorldWin64.exe'
Write-Output "RimWorldWin64.exe Exists=$([System.IO.File]::Exists($exe))"

$installedDll = 'C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
if (Test-Path $installedDll) {
    $h = (Get-FileHash $installedDll -Algorithm SHA256).Hash
    $size = (Get-Item $installedDll).Length
    Write-Output "Installed DLL SHA256=$h Size=$size"
} else {
    Write-Output "Installed DLL NOT FOUND"
}

$archiveManifest = 'Dispatcher/A_TASKS/ENGINE_GATE05_BASELINE_BEFORE_R1_20261008/ARCHIVE_MANIFEST.json'
if (Test-Path $archiveManifest) {
    Write-Output "Archive Manifest found"
    Get-Content $archiveManifest | Select-String "WarEconomy.WorkerBridge.PoC.dll" -Context 0,2
}
