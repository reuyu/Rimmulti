$files = @(
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
)

$res = @()
foreach ($f in $files) {
  if (Test-Path $f) {
    $h = (Get-FileHash -Algorithm SHA256 $f).Hash
    $len = (Get-Item $f).Length
    $res += [PSCustomObject]@{
      path = $f
      sha256 = $h
      size = $len
    }
  } else {
    $res += [PSCustomObject]@{
      path = $f
      sha256 = "MISSING"
      size = 0
    }
  }
}

$res | Format-Table -AutoSize
$res | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R22-DECLARATION-20261011-DIRECT-9be1579a\ENGINE_FREEZE_AFTER.json"
