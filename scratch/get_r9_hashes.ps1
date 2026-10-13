$files = @(
  'C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Content_Codec_Gate05_R9.md',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\Harness\Gate05R9VersionRunner.csproj',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\Harness\Program.cs',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\results.json',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\raw_console.txt',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\CANDIDATE_PRE_RUN_MANIFEST.json',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\ENGINE_FREEZE_BEFORE.json',
  'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R9VersionMeaning\ENGINE_FREEZE_AFTER.json',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll',
  'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb',
  'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b\ACK.json',
  'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b\A_RECOVERY_ACK.md',
  'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R9-VERSION-MEANING-20261009-DIRECT-fbe8a43b\A_WORK_LOG.md'
)

foreach ($f in $files) {
    if (Test-Path $f) {
        $h = (Get-FileHash $f -Algorithm SHA256).Hash
        $s = (Get-Item $f).Length
        Write-Output ("PATH: " + $f)
        Write-Output ("  SHA256: " + $h)
        Write-Output ("  SIZE:   " + $s)
    } else {
        Write-Output ("MISSING: " + $f)
    }
}
