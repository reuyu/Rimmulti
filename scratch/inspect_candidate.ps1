$paths = @(
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll',
    'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb'
)

foreach ($p in $paths) {
    if (Test-Path $p) {
        $hash = (Get-FileHash -Algorithm SHA256 $p).Hash
        $len = (Get-Item $p).Length
        $mvid = "N/A"
        if ($p.EndsWith(".dll")) {
            try {
                $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $p))
                $asm = [System.Reflection.Assembly]::Load($bytes)
                $mvid = $asm.ManifestModule.ModuleVersionId.ToString()
            } catch {
                $mvid = "ERR: " + $_.Exception.Message
            }
        }
        Write-Output "$p : Length=$len, SHA256=$hash, MVID=$mvid"
    } else {
        Write-Output "$p : NOT_FOUND"
    }
}
