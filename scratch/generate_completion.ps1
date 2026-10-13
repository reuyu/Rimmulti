$artifacts = @(
    @{
        role = "implementation_report"
        path = "C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Semantic_Authority_Gate_05_R1.md"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Semantic_Authority_Gate_05_R1.md" -Algorithm SHA256).Hash
    },
    @{
        role = "release_manifest"
        path = "C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R1.json"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R1.json" -Algorithm SHA256).Hash
    },
    @{
        role = "results"
        path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\results.json"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\results.json" -Algorithm SHA256).Hash
    },
    @{
        role = "raw_evidence"
        path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\raw_console.txt"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\raw_console.txt" -Algorithm SHA256).Hash
    },
    @{
        role = "engine_freeze_before"
        path = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\ENGINE_GATE05_BASELINE_BEFORE_R1_20261008\ARCHIVE_MANIFEST.json" -Algorithm SHA256).Hash
    },
    @{
        role = "engine_freeze_after"
        path = "C:\Users\user\Desktop\RimMulti\scratch\MASTER_ENGINE_FREEZE_AFTER_GATE05_R1.json"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\MASTER_ENGINE_FREEZE_AFTER_GATE05_R1.json" -Algorithm SHA256).Hash
    },
    @{
        role = "harness"
        path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\bin\Release\net472\Gate05R1TestRunner.exe"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\bin\Release\net472\Gate05R1TestRunner.exe" -Algorithm SHA256).Hash
    },
    @{
        role = "candidate_binary"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll" -Algorithm SHA256).Hash
    },
    @{
        role = "candidate_binary"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll" -Algorithm SHA256).Hash
    },
    @{
        role = "pdb"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb" -Algorithm SHA256).Hash
    },
    @{
        role = "pdb"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb" -Algorithm SHA256).Hash
    },
    @{
        role = "pdb"
        path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\bin\Release\net472\Gate05R1TestRunner.pdb"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\bin\Release\net472\Gate05R1TestRunner.pdb" -Algorithm SHA256).Hash
    },
    @{
        role = "source"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs" -Algorithm SHA256).Hash
    },
    @{
        role = "source"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs" -Algorithm SHA256).Hash
    },
    @{
        role = "source"
        path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" -Algorithm SHA256).Hash
    },
    @{
        role = "source"
        path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\Program.cs"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\Program.cs" -Algorithm SHA256).Hash
    },
    @{
        role = "source"
        path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\Gate05R1TestRunner.csproj"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R1\Gate05R1TestRunner.csproj" -Algorithm SHA256).Hash
    },
    @{
        role = "pipeline_preservation"
        path = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01\COMPLETION.json"
        sha256 = (Get-FileHash "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-PIPELINE-REV6-R1-20261007-DIRECT-01\COMPLETION.json" -Algorithm SHA256).Hash
    }
)

$completion = [ordered]@{
    schema_version = 1
    dispatch_id = "WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780"
    wp_id = "WP_ENGINE_GATE05_R1"
    wp_revision = "GATE05-R1"
    result_id = "WE-A-ENGINE-GATE05-R1-RESULT-20261008-01"
    producer = "A"
    status = "COMPLETED"
    report_kind = "E1"
    completed_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
    e1_verdict = "PASS"
    summary = "Completed Engine Gate05-R1 repair addressing G05-S01 (validator process registration, capability nonce redaction and leak elimination, protected task-bound channel, caller receipt rejection) and G05-S02 (expanded 8-family Def census with deep gameplay fields, running mod metadata and assembly SHA/MVID inventory, fail-closed profile computation without UNKNOWN_PROFILE, and lifecycle-bound cache invalidation). Preserved historical Gate05 baseline (19 files bit-identical) and Pipeline REV6-R1 candidate (17 artifacts bit-identical). Tested via dedicated regression harness Gate05R1TestRunner (11/11 PASS). Native RimWorld execution against candidate reported as UNTESTED / BLOCKED due to frozen installed DLL boundary."
    limitations = @(
        "Native RimWorld process execution against the new candidate DLL was NOT performed (marked UNTESTED / BLOCKED). Modifying the frozen installed DLL (SHA 2D64FF9C...) in Steam directory is strictly prohibited by Master governance rules, and RimWorld hardcodes its mod directory to RimWorld\Mods on Windows.",
        "This submission represents E1 producer verification only. Per Master rules, E1 PASS does not replace independent E2 verification by Sol / QA.",
        "Engine Host remains a bounded simulation proposal producer; final domain authority remains with the Dedicated Server."
    )
    artifacts = $artifacts
}

$targetDir = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R1-20261008-DIRECT-971a4780"
$tmpPath = Join-Path $targetDir "COMPLETION.json.tmp"
$finalPath = Join-Path $targetDir "COMPLETION.json"

$completion | ConvertTo-Json -Depth 5 | Set-Content $tmpPath -Encoding UTF8
Write-Host "Wrote COMPLETION.json.tmp successfully."

# Verify bit-for-bit that tmp file can be read and contains all artifacts
$readBack = Get-Content $tmpPath | ConvertFrom-Json
Write-Host "Read back tmp file. Artifact count: $($readBack.artifacts.Count)"
foreach ($art in $readBack.artifacts) {
    if (-not (Test-Path $art.path)) {
        throw "Artifact path does not exist: $($art.path)"
    }
    $h = (Get-FileHash $art.path -Algorithm SHA256).Hash
    if ($h -ne $art.sha256) {
        throw "Hash mismatch for $($art.path): expected $($art.sha256), got $h"
    }
}
Write-Host "All artifacts in COMPLETION.json.tmp verified against disk."

# Atomic rename
Move-Item -Path $tmpPath -Destination $finalPath -Force
Write-Host "Atomically published COMPLETION.json at $finalPath"
