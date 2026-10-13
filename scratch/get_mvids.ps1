$paths = @(
  "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll",
  "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
)

foreach ($p in $paths) {
  $bytes = [System.IO.File]::ReadAllBytes($p)
  $asm = [System.Reflection.Assembly]::Load($bytes)
  $mvid = $asm.ManifestModule.ModuleVersionId
  Write-Output "$p : MVID = $mvid"
}
