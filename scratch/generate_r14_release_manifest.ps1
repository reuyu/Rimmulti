Add-Type -Path "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\bin\Debug\net472\Newtonsoft.Json.dll"

$sha = [System.Security.Cryptography.SHA256]::Create()

function Get-FileInfoObj($p) {
    $full = (Resolve-Path $p).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    return [ordered]@{
        path = $p.Replace("/", "\")
        sha256 = $hash
        bytes = $bytes.Length
    }
}

$censusPath = 'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs'
$censusInfo = Get-FileInfoObj $censusPath

$relObj = [ordered]@{
    manifest_version = "1.0"
    work_package = "WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION"
    candidate_lineage = "GATE05-R14-POLICY-CAPTURE-PUBLICATION"
    created_at_utc = [System.DateTime]::UtcNow.ToString("o")
    agent_role = "Antigravity A"
    dispatch_id = "WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b"
    run_id = "GATE05-R14-POLICY-CAPTURE-PUBLICATION-RUN-01"
    selected_candidate = [ordered]@{
        configuration = "Debug"
        target_framework = "net472"
        dll_path = 'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
        dll_sha256 = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll').sha256
        dll_bytes = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll').bytes
        pdb_path = 'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
        pdb_sha256 = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb').sha256
        pdb_bytes = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb').bytes
        mvid = "acab0270-bc98-4d17-b920-9941950ff024"
    }
    alternate_candidate = [ordered]@{
        configuration = "Release"
        target_framework = "net472"
        dll_path = 'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll'
        dll_sha256 = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll').sha256
        dll_bytes = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll').bytes
        pdb_path = 'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb'
        pdb_sha256 = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb').sha256
        pdb_bytes = (Get-FileInfoObj 'scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb').bytes
        mvid = "874a8ce6-014a-4506-aba5-4648e50abd83"
    }
    deployed_mod_assemblies = [ordered]@{
        dll_path = 'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
        dll_sha256 = (Get-FileInfoObj 'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll').sha256
        dll_bytes = (Get-FileInfoObj 'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll').bytes
        pdb_path = 'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb'
        pdb_sha256 = (Get-FileInfoObj 'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb').sha256
        pdb_bytes = (Get-FileInfoObj 'scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb').bytes
    }
    source_files = @(
        [ordered]@{
            path = 'scratch\WorkerBridgeMod\Source\WorkerBridge.cs'
            sha256 = "BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718"
            bytes = 156431
        },
        [ordered]@{
            path = 'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs'
            sha256 = $censusInfo.sha256
            bytes = $censusInfo.bytes
            prefix_marker = "    public static class ContentProfileProvider"
            prefix_length = 72547
            prefix_sha256 = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
        },
        [ordered]@{
            path = 'scratch\WorkerBridgeMod\Source\WorkerBridge.csproj'
            sha256 = "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052"
            bytes = 1774
        }
    )
    verification_evidence = [ordered]@{
        runner_project = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\Harness\Gate05R14CacheRunner.csproj'
        runner_source = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\Harness\Program.cs'
        runner_binary = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\Harness\bin\Debug\net472\Gate05R14CacheRunner.exe'
        runner_pdb = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\Harness\bin\Debug\net472\Gate05R14CacheRunner.pdb'
        pre_run_manifest = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\CANDIDATE_PRE_RUN_MANIFEST.json'
        freeze_before = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\ENGINE_FREEZE_BEFORE.json'
        freeze_after = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\ENGINE_FREEZE_AFTER.json'
        test_results = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\results.json'
        raw_console = Get-FileInfoObj 'scratch\EngineGate05R14PolicyCapturePublication\raw_console.txt'
        e1_report = Get-FileInfoObj 'docs\POC_EngineHost_Content_Codec_Gate05_R14.md'
    }
    execution_summary = [ordered]@{
        total_tests = 22
        passed_tests = 22
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

$jsonText = [Newtonsoft.Json.JsonConvert]::SerializeObject($relObj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("docs\RELEASE_MANIFEST_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION.json", $jsonText, $utf8NoBom)

Write-Host "Created docs\RELEASE_MANIFEST_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION.json successfully."
