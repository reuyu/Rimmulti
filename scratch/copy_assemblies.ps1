$srcDll = 'c:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
$srcPdb = 'c:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
$destDir = 'c:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies'

Copy-Item $srcDll -Destination $destDir -Force
Copy-Item $srcPdb -Destination $destDir -Force

Write-Host "Copied Debug DLL and PDB to $destDir"
