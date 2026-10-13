Add-Type -AssemblyName System.Reflection
Add-Type -AssemblyName System.Security.Cryptography

$targets = @(
    "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll",
    "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb",
    "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll",
    "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb",
    "scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.dll",
    "scratch/WorkerBridgeMod/1.6/Assemblies/WarEconomy.WorkerBridge.PoC.pdb",
    "scratch/WorkerBridgeMod/Source/EngineHostCensus.cs",
    "scratch/WorkerBridgeMod/Source/WorkerBridge.cs",
    "scratch/WorkerBridgeMod/Source/WorkerBridge.csproj"
)

foreach ($p in $targets) {
    if (Test-Path $p) {
        $bytes = [System.IO.File]::ReadAllBytes($p)
        $sha = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace("-", "")
        $mvid = "N/A"
        if ($p.EndsWith(".dll")) {
            try {
                $asmDef = [System.Reflection.AssemblyName]::GetAssemblyName((Resolve-Path $p).Path)
                $rawAsm = [System.Reflection.Assembly]::Load($bytes)
                $mvid = $rawAsm.ManifestModule.ModuleVersionId.ToString()
            } catch {
                $mvid = "ERR: " + $_.Exception.Message
            }
        }
        Write-Host "$p | Len: $($bytes.Length) | SHA: $sha | MVID: $mvid"
    } else {
        Write-Host "$p | NOT FOUND"
    }
}
