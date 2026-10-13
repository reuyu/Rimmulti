$files = @(
    'WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.dll',
    'WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.pdb',
    'WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.exe',
    'WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.dll',
    'WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.pdb',
    'WarEconomyMod/Source/Testing/WarEconomy.Pipeline.TestHarness/bin/Release/net8.0/WarEconomy.Pipeline.TestHarness.dll',
    'WarEconomyMod/Source/Testing/WarEconomy.Pipeline.TestHarness/bin/Release/net8.0/WarEconomy.Pipeline.TestHarness.pdb',
    'scratch/E1_Rev6_Runner/bin/Release/net8.0/E1_Rev6_Runner.dll',
    'scratch/E1_Rev6_Runner/bin/Release/net8.0/E1_Rev6_Runner.pdb',
    'scratch/E1_Rev6_Runner/bin/Release/net8.0/E1_Rev6_Runner.exe',
    'WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs',
    'WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs',
    'WarEconomyMod/Source/Testing/WarEconomy.Pipeline.TestHarness/PipelineE1TestBattery.cs',
    'scratch/E1_Rev6_Runner/Program.cs',
    'scratch/pipeline_e1_rev6_results.json',
    'scratch/pipeline_e1_rev6_raw_console.txt',
    'scratch/MASTER_ENGINE_FREEZE_BEFORE.json',
    'scratch/MASTER_ENGINE_FREEZE_AFTER.json'
)

$results = foreach ($f in $files) {
    if (Test-Path $f) {
        [PSCustomObject]@{
            Path = $f
            SHA256 = (Get-FileHash -Algorithm SHA256 $f).Hash
        }
    } else {
        [PSCustomObject]@{
            Path = $f
            SHA256 = "MISSING"
        }
    }
}

$results | ConvertTo-Json -Depth 4
