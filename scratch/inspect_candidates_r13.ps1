$sha = [System.Security.Cryptography.SHA256]::Create()

function Inspect($p) {
    $b = [System.IO.File]::ReadAllBytes($p)
    $h = [System.BitConverter]::ToString($sha.ComputeHash($b)).Replace("-","")
    $mvid = ""
    if ($p.EndsWith(".dll")) {
        try {
            $asm = [System.Reflection.Assembly]::Load($b)
            $mvid = $asm.ManifestModule.ModuleVersionId.ToString()
        } catch {
            $mvid = "N/A"
        }
    }
    Write-Host "$p -> Size: $($b.Length), SHA: $h, MVID: $mvid"
}

Inspect "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
Inspect "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
Inspect "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
Inspect "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
Inspect "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"
Inspect "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
