$dllPath = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
$pdbPath = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'

$dllHash = (Get-FileHash -Algorithm SHA256 $dllPath).Hash
$pdbHash = (Get-FileHash -Algorithm SHA256 $pdbPath).Hash

$bytes = [System.IO.File]::ReadAllBytes($dllPath)
$asm = [System.Reflection.Assembly]::Load($bytes)
$mvid = $asm.ManifestModule.ModuleVersionId.ToString()

Write-Host "DLL SHA256: $dllHash"
Write-Host "DLL MVID:   $mvid"
Write-Host "PDB SHA256: $pdbHash"
