$files = @(
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb'
)
foreach ($f in $files) {
    if (Test-Path $f) {
        $hash = (Get-FileHash $f -Algorithm SHA256).Hash
        $size = (Get-Item $f).Length
        Write-Output "$f : SHA256=$hash Size=$size"
        if ($f.EndsWith('.dll')) {
            $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $f))
            $asm = [System.Reflection.Assembly]::Load($bytes)
            $mvid = $asm.ManifestModule.ModuleVersionId
            Write-Output "$f : MVID=$mvid"
        }
    } else {
        Write-Output "$f : NOT FOUND"
    }
}
