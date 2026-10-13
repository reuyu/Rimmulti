$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$scratchDir = "$workspaceRoot\scratch\EngineGate05R15PublicManifestBoundary"

$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Get-Artifact([string]$fullPath) {
    if (-not (Test-Path $fullPath)) { throw "Path not found: $fullPath" }
    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
    $rel = $fullPath.Replace("$workspaceRoot\", "")
    return @{
        path = $rel
        sha256 = $hash
        bytes = $bytes.Length
    }
}

$selCandidate = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
$selPdb = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
$altCandidate = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
$altPdb = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
$depCandidate = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"
$depPdb = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"

$srcWorker = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"
$srcCensus = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
$srcCsproj = Get-Artifact "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"

$runCsproj = Get-Artifact "$scratchDir\Harness\Gate05R15BoundaryRunner.csproj"
$runSource = Get-Artifact "$scratchDir\Harness\Program.cs"
$runBinary = Get-Artifact "$scratchDir\Harness\bin\Debug\net472\Gate05R15BoundaryRunner.exe"
$runPdb = Get-Artifact "$scratchDir\Harness\bin\Debug\net472\Gate05R15BoundaryRunner.pdb"

$preRunManifest = Get-Artifact "$scratchDir\CANDIDATE_PRE_RUN_MANIFEST.json"
$freezeBefore = Get-Artifact "$scratchDir\ENGINE_FREEZE_BEFORE.json"
$freezeAfter = Get-Artifact "$scratchDir\ENGINE_FREEZE_AFTER.json"
$resultsJson = Get-Artifact "$scratchDir\run_default\results.json"
$rawConsole = Get-Artifact "$scratchDir\run_default\raw_console.txt"
$e1Report = Get-Artifact "$workspaceRoot\docs\POC_EngineHost_Content_Codec_Gate05_R15.md"

$manifestObj = [ordered]@{
    manifest_version = "1.0"
    work_package = "WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY"
    candidate_lineage = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY"
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    agent_role = "Antigravity A"
    dispatch_id = "WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052"
    run_id = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-RUN-01"
    selected_candidate = [ordered]@{
        configuration = "Debug"
        target_framework = "net472"
        dll_path = $selCandidate.path
        dll_sha256 = $selCandidate.sha256
        dll_bytes = $selCandidate.bytes
        pdb_path = $selPdb.path
        pdb_sha256 = $selPdb.sha256
        pdb_bytes = $selPdb.bytes
        mvid = "4fb1a25f-72c8-426d-b93f-d6cba4f9af72"
    }
    alternate_candidate = [ordered]@{
        configuration = "Release"
        target_framework = "net472"
        dll_path = $altCandidate.path
        dll_sha256 = $altCandidate.sha256
        dll_bytes = $altCandidate.bytes
        pdb_path = $altPdb.path
        pdb_sha256 = $altPdb.sha256
        pdb_bytes = $altPdb.bytes
        mvid = "58766cdc-afee-4682-858a-dab68c96e36e"
    }
    deployed_mod_assemblies = [ordered]@{
        dll_path = $depCandidate.path
        dll_sha256 = $depCandidate.sha256
        dll_bytes = $depCandidate.bytes
        pdb_path = $depPdb.path
        pdb_sha256 = $depPdb.sha256
        pdb_bytes = $depPdb.bytes
    }
    source_files = @(
        [ordered]@{
            path = $srcWorker.path
            sha256 = $srcWorker.sha256
            bytes = $srcWorker.bytes
        },
        [ordered]@{
            path = $srcCensus.path
            sha256 = $srcCensus.sha256
            bytes = $srcCensus.bytes
            prefix_marker = "    public static class ContentProfileProvider"
            prefix_length = 72547
            prefix_sha256 = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
        },
        [ordered]@{
            path = $srcCsproj.path
            sha256 = $srcCsproj.sha256
            bytes = $srcCsproj.bytes
        }
    )
    verification_evidence = [ordered]@{
        runner_project = [ordered]@{ path = $runCsproj.path; sha256 = $runCsproj.sha256; bytes = $runCsproj.bytes }
        runner_source = [ordered]@{ path = $runSource.path; sha256 = $runSource.sha256; bytes = $runSource.bytes }
        runner_binary = [ordered]@{ path = $runBinary.path; sha256 = $runBinary.sha256; bytes = $runBinary.bytes }
        runner_pdb = [ordered]@{ path = $runPdb.path; sha256 = $runPdb.sha256; bytes = $runPdb.bytes }
        pre_run_manifest = [ordered]@{ path = $preRunManifest.path; sha256 = $preRunManifest.sha256; bytes = $preRunManifest.bytes }
        freeze_before = [ordered]@{ path = $freezeBefore.path; sha256 = $freezeBefore.sha256; bytes = $freezeBefore.bytes }
        freeze_after = [ordered]@{ path = $freezeAfter.path; sha256 = $freezeAfter.sha256; bytes = $freezeAfter.bytes }
        test_results = [ordered]@{ path = $resultsJson.path; sha256 = $resultsJson.sha256; bytes = $resultsJson.bytes }
        raw_console = [ordered]@{ path = $rawConsole.path; sha256 = $rawConsole.sha256; bytes = $rawConsole.bytes }
        e1_report = [ordered]@{ path = $e1Report.path; sha256 = $e1Report.sha256; bytes = $e1Report.bytes }
    }
    execution_summary = [ordered]@{
        total_tests = 25
        passed_tests = 25
        failed_tests = 0
        verdict = "SCOPED_POSITIVE_NORMAL_PASS"
        execution_scope = "PURE_POSITIVE_NORMAL_MANAGED_ONLY"
    }
    limitations = @(
        "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY",
        "PURE_INSTANCE_CORE_AND_NORMAL_CONFIGURATION_LIFECYCLE_EVIDENCE_ONLY",
        "NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED",
        "PRODUCER_GLOBAL_PROVIDER_REAL_ENTRY_STATIC_UNTESTED",
        "MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN",
        "NATIVE_PROMOTION_FULL_E2_NOT_RELEASED",
        "FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER"
    )
}

# Use Newtonsoft.Json for serialization
Add-Type -Path "$workspaceRoot\WarEconomyMod\1.6\Assemblies\Newtonsoft.Json.dll"
$jsonString = [Newtonsoft.Json.JsonConvert]::SerializeObject($manifestObj, [Newtonsoft.Json.Formatting]::Indented)

$targetPath = "$workspaceRoot\docs\RELEASE_MANIFEST_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.json"
[System.IO.File]::WriteAllText($targetPath, $jsonString, [System.Text.Encoding]::UTF8)

# Validate parsing
[Newtonsoft.Json.Linq.JObject]::Parse($jsonString) | Out-Null
Write-Host "RELEASE_MANIFEST_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.json created and verified syntax."
