
$dlls = @(
    'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
    'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
    'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
)

foreach ($d in $dlls) {
    $bytes = [System.IO.File]::ReadAllBytes($d)
    $asm = [System.Reflection.Assembly]::Load($bytes)
    $mvid = $asm.ManifestModule.ModuleVersionId
    Write-Output ($d + ' | MVID: ' + $mvid.ToString())
}
