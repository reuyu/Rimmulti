$debugDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
$debugPdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
$releaseDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll'
$releasePdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb'
$deployedDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
$deployedPdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb'

function Get-MvidProcess($dllPath) {
    $script = "[System.IO.File]::WriteAllText('$env:TEMP\mvid.tmp', [System.Reflection.Assembly]::ReflectionOnlyLoad([System.IO.File]::ReadAllBytes('$dllPath')).ManifestModule.ModuleVersionId.ToString())"
    powershell -NoProfile -Command $script
    $mvid = Get-Content "$env:TEMP\mvid.tmp" -Raw
    return $mvid.Trim()
}

$dbgMvid = Get-MvidProcess $debugDll
$relMvid = Get-MvidProcess $releaseDll
$depMvid = Get-MvidProcess $deployedDll

$dbgSha = (Get-FileHash $debugDll -Algorithm SHA256).Hash
$dbgSize = (Get-Item $debugDll).Length
$relSha = (Get-FileHash $releaseDll -Algorithm SHA256).Hash
$relSize = (Get-Item $releaseDll).Length
$depSha = (Get-FileHash $deployedDll -Algorithm SHA256).Hash
$depSize = (Get-Item $deployedDll).Length

Write-Output ("DEBUG: SHA=" + $dbgSha + " SIZE=" + $dbgSize + " MVID=" + $dbgMvid)
Write-Output ("RELEASE: SHA=" + $relSha + " SIZE=" + $relSize + " MVID=" + $relMvid)
Write-Output ("DEPLOYED: SHA=" + $depSha + " SIZE=" + $depSize + " MVID=" + $depMvid)

$dbgPdbSha = (Get-FileHash $debugPdb -Algorithm SHA256).Hash
$dbgPdbSize = (Get-Item $debugPdb).Length
$relPdbSha = (Get-FileHash $releasePdb -Algorithm SHA256).Hash
$relPdbSize = (Get-Item $releasePdb).Length
$depPdbSha = (Get-FileHash $deployedPdb -Algorithm SHA256).Hash
$depPdbSize = (Get-Item $deployedPdb).Length

Write-Output ("DEBUG PDB: SHA=" + $dbgPdbSha + " SIZE=" + $dbgPdbSize)
Write-Output ("RELEASE PDB: SHA=" + $relPdbSha + " SIZE=" + $relPdbSize)
Write-Output ("DEPLOYED PDB: SHA=" + $depPdbSha + " SIZE=" + $depPdbSize)
