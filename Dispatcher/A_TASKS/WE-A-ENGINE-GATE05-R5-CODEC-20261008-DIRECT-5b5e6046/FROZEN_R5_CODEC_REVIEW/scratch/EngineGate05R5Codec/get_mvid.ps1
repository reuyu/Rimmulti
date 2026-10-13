
$dbg = [System.Reflection.Assembly]::LoadFrom((Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll").Path)
$rel = [System.Reflection.Assembly]::LoadFrom((Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll").Path)
[PSCustomObject]@{
    DebugMvid = $dbg.ManifestModule.ModuleVersionId.ToString()
    ReleaseMvid = $rel.ManifestModule.ModuleVersionId.ToString()
} | ConvertTo-Json
