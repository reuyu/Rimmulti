$targets = @(
    "scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll",
    "scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll"
)

foreach ($dll in $targets) {
    $bytes = [System.IO.File]::ReadAllBytes($dll)
    # Search for "RSDS" signature in bytes
    for ($i = 0; $i -lt $bytes.Length - 4; $i++) {
        if ($bytes[$i] -eq 0x52 -and $bytes[$i+1] -eq 0x53 -and $bytes[$i+2] -eq 0x44 -and $bytes[$i+3] -eq 0x53) {
            $guidBytes = New-Object byte[] 16
            [System.Array]::Copy($bytes, $i + 4, $guidBytes, 0, 16)
            $guid = [System.Guid]::new($guidBytes)
            $age = [System.BitConverter]::ToInt32($bytes, $i + 20)
            $pathBytes = New-Object System.Collections.Generic.List[byte]
            $p = $i + 24
            while ($p -lt $bytes.Length -and $bytes[$p] -ne 0) {
                $pathBytes.Add($bytes[$p])
                $p++
            }
            $pdbPath = [System.Text.Encoding]::UTF8.GetString($pathBytes.ToArray())
            Write-Host "$dll -> CodeView GUID: $guid, Age: $age, PDB Path: $pdbPath"
            break
        }
    }
}
