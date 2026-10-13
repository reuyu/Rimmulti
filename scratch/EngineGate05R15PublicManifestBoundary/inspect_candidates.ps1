$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$paths = @(
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb",
    "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll",
    "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll",
    "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
)

$sha256 = [System.Security.Cryptography.SHA256]::Create()
foreach ($p in $paths) {
    $bytes = [System.IO.File]::ReadAllBytes($p)
    $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
    $mvid = ""
    if ($p.EndsWith(".dll")) {
        $asm = [System.Reflection.Assembly]::Load($bytes)
        $mvid = $asm.ManifestModule.ModuleVersionId.ToString()
    }
    [PSCustomObject]@{
        Path = $p
        Size = $bytes.Length
        SHA256 = $hash
        MVID = $mvid
    } | Format-List
}
