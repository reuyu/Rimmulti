Add-Type -Path "scratch\EngineGate05R12PackageOrder\Harness\bin\Debug\net472\Newtonsoft.Json.dll"

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

$relObj = [ordered]@{
    manifest_version = "1.0"
    work_package = "WP_ENGINE_GATE05_R12_PACKAGE_ORDER"
    candidate_lineage = "GATE05-R12-PACKAGE-ORDER"
    created_at_utc = [System.DateTime]::UtcNow.ToString("o")
    agent_role = "Antigravity A"
    dispatch_id = "WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6"
    run_id = "GATE05-R12-PACKAGE-ORDER-RUN-01"
    selected_candidate = [ordered]@{
        configuration = "Debug"
        target_framework = "net472"
        dll_path = "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
        dll_sha256 = "3035A0D0FDD799D42AC83B7D776998AFF07A8BDD3246959E685AA0F8D7ACF94E"
        dll_bytes = 237568
        pdb_path = "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
        pdb_sha256 = "61CDC0E8D28047027BF3EE46FD6C3349AD52FAB0846C03868FEB7FEC538E9993"
        pdb_bytes = 59924
        mvid = "ad4caf3c-88bc-4971-9c2a-ab78eae395e5"
    }
    alternate_candidate = [ordered]@{
        configuration = "Release"
        target_framework = "net472"
        dll_path = "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
        dll_sha256 = "25F6C21092CA3DDCBF7D80EBBC40B6B3E7A3758595E7B3C106D05474F95C8561"
        dll_bytes = 225792
        pdb_path = "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
        pdb_sha256 = "A2366CC60F889135D8A63DBD2BCF2340FF93D0229F64250F75D50E95D6AB8166"
        pdb_bytes = 43852
        mvid = "7b97e307-b06f-40fc-ad6f-5530d180ebe0"
    }
    deployed_mod_assemblies = [ordered]@{
        dll_path = "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"
        dll_sha256 = "3035A0D0FDD799D42AC83B7D776998AFF07A8BDD3246959E685AA0F8D7ACF94E"
        dll_bytes = 237568
        pdb_path = "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"
        pdb_sha256 = "61CDC0E8D28047027BF3EE46FD6C3349AD52FAB0846C03868FEB7FEC538E9993"
        pdb_bytes = 59924
    }
    source_files = @(
        [ordered]@{
            path = "scratch\WorkerBridgeMod\Source\WorkerBridge.cs"
            sha256 = "BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718"
            bytes = 156431
        },
        [ordered]@{
            path = "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
            sha256 = "5E9A4DE9A6280A887E3659CE2D80A8029C2BEF41DC615BB3F6F1BB859B1F020E"
            bytes = 157554
            prefix_marker = "    public static class ContentProfileProvider"
            prefix_length = 72547
            prefix_sha256 = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
        },
        [ordered]@{
            path = "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"
            sha256 = "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052"
            bytes = 1774
        }
    )
    verification_evidence = [ordered]@{
        runner_project = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\Gate05R12OrderRunner.csproj"
        runner_source = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\Program.cs"
        runner_binary = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\bin\Debug\net472\Gate05R12OrderRunner.exe"
        runner_pdb = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\bin\Debug\net472\Gate05R12OrderRunner.pdb"
        pre_run_manifest = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\CANDIDATE_PRE_RUN_MANIFEST.json"
        freeze_before = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\ENGINE_FREEZE_BEFORE.json"
        freeze_after = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\ENGINE_FREEZE_AFTER.json"
        test_results = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\results.json"
        raw_console = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\raw_console.txt"
        e1_report = Get-FileInfoObj "docs\POC_EngineHost_Content_Codec_Gate05_R12.md"
    }
    execution_summary = [ordered]@{
        total_tests = 18
        passed_tests = 18
        failed_tests = 0
        verdict = "SCOPED_POSITIVE_NORMAL_PASS"
        execution_scope = "PURE_POSITIVE_NORMAL_MANAGED_ONLY"
    }
    limitations = @(
        "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY",
        "PHYSICAL_ARRAY_LOAD_ORDER_ADMISSION_SCOPED_TO_DECLARED_ORDINAL_CONSISTENCY",
        "POLICY_CACHE_GENERATION_NOT_PROVEN",
        "REAL_OPERATOR_ORIGIN_NOT_PROVEN",
        "MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN",
        "NATIVE_PROMOTION_FULL_E2_NOT_RELEASED",
        "FINAL_DOMAIN_AUTHORITY_REMAINS_DEDICATED_SERVER"
    )
}

$jsonText = [Newtonsoft.Json.JsonConvert]::SerializeObject($relObj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText("docs\RELEASE_MANIFEST_ENGINE_GATE05_R12_PACKAGE_ORDER.json", $jsonText, $utf8NoBom)

Write-Host "Created docs\RELEASE_MANIFEST_ENGINE_GATE05_R12_PACKAGE_ORDER.json using Newtonsoft.Json successfully."
