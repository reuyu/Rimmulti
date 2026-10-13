$targetDir = 'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy'
if (!(Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
$paths = @(
  'c:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs',
  'c:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj'
)
$list = @()
foreach ($p in $paths) {
  if (Test-Path $p) {
    $h = (Get-FileHash $p -Algorithm SHA256).Hash
    $s = (Get-Item $p).Length
    $list += [PSCustomObject]@{ path = $p; sha256 = $h; size = $s }
  } else {
    $list += [PSCustomObject]@{ path = $p; sha256 = 'MISSING'; size = 0 }
  }
}
$freeze = [PSCustomObject]@{
  at = (Get-Date).ToString('o')
  stage = 'PRE_RUN_BEFORE_R10'
  files = $list
}
$json = ConvertTo-Json $freeze -Depth 5
[System.IO.File]::WriteAllText((Join-Path $targetDir 'ENGINE_FREEZE_BEFORE.json'), $json, [System.Text.Encoding]::UTF8)
Write-Output 'ENGINE_FREEZE_BEFORE written successfully.'
