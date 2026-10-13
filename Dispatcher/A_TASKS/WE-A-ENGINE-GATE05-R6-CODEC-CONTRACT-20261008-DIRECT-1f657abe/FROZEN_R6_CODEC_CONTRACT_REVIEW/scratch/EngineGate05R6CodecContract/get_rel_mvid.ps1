
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll").Path)
$asm = [System.Reflection.Assembly]::Load($bytes)
Write-Output $asm.ManifestModule.ModuleVersionId.ToString()
