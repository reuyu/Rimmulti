$debugDll = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
$releaseDll = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"

$debugAsm = [System.Reflection.Assembly]::LoadFrom($debugDll)
Write-Host "Debug MVID:" $debugAsm.ManifestModule.ModuleVersionId

$releaseAsm = [System.Reflection.Assembly]::LoadFrom($releaseDll)
Write-Host "Release MVID:" $releaseAsm.ManifestModule.ModuleVersionId
