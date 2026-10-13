$paths = @(
    "scratch\WorkerBridgeMod\Source\WorkerBridge.cs",
    "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
)

foreach ($p in $paths) {
    $h = (Get-FileHash -Algorithm SHA256 $p).Hash
    $s = (Get-Item $p).Length
    $mvid = ""
    if ($p.EndsWith(".dll")) {
        try {
            $bytes = [System.IO.File]::ReadAllBytes($p)
            $asm = [System.Reflection.Assembly]::Load($bytes)
            $mvid = $asm.ManifestModule.ModuleVersionId.ToString()
        } catch {
            $mvid = "ERROR: " + $_.Exception.Message
        }
    }
    Write-Output "$p | $h | $s | $mvid"
}
