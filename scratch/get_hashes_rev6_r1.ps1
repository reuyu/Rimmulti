$files = @(
    'WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.dll',
    'WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.pdb',
    'WarEconomyMod/Source/Server/bin/Release/net8.0/WarEconomy.Server.exe',
    'WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.dll',
    'WarEconomyMod/Source/Common/bin/Release/netstandard2.0/WarEconomy.Common.pdb',
    'scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.dll',
    'scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.pdb',
    'scratch/E1_Rev6_R1_Runner/bin/Release/net8.0/E1_Rev6_R1_Runner.exe',
    'WarEconomyMod/Source/Server/Pipeline/Recovery/RecoveryReconciler.cs',
    'WarEconomyMod/Source/Server/Pipeline/Data/Migrations/PipelineSchemaMigration.cs',
    'scratch/E1_Rev6_R1_Runner/Program.cs',
    'scratch/pipeline_e1_rev6_r1_results.json',
    'scratch/pipeline_e1_rev6_r1_raw_console.txt',
    'Dispatcher/A_TASKS/WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01/MASTER_ENGINE_FREEZE_BEFORE.json',
    'scratch/MASTER_ENGINE_FREEZE_AFTER_REV6_R1.json'
)

$results = foreach ($f in $files) {
    if (Test-Path $f) {
        $mvid = $null
        if ($f.EndsWith(".dll") -or $f.EndsWith(".exe")) {
            try {
                $asm = [System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes((Resolve-Path $f).Path))
                $mvid = $asm.ManifestModule.ModuleVersionId.ToString()
            } catch { }
        }
        [PSCustomObject]@{
            Path = $f
            SHA256 = (Get-FileHash -Algorithm SHA256 $f).Hash
            MVID = $mvid
        }
    } else {
        [PSCustomObject]@{
            Path = $f
            SHA256 = "MISSING"
            MVID = $null
        }
    }
}

$results | ConvertTo-Json -Depth 4
