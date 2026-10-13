$runId = "GATE05-R12-PACKAGE-ORDER-RUN-01"
$dispatchId = "WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6"
$wpId = "WP_ENGINE_GATE05_R12_PACKAGE_ORDER"
$wpRevision = "GATE05-R12-PACKAGE-ORDER"

$sha = [System.Security.Cryptography.SHA256]::Create()

function Get-FileInfoObj($p, $role = "") {
    $full = (Resolve-Path $p).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $res = [ordered]@{
        path = $full
        sha256 = $hash
        size = $bytes.Length
    }
    if ($role) { $res["role"] = $role }
    return $res
}

$manifest = [ordered]@{
    schema_version = "ADR-006B-v5"
    run_id = $runId
    dispatch_id = $dispatchId
    wp_id = $wpId
    wp_revision = $wpRevision
    created_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
    selected_candidate = [ordered]@{
        path = (Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll").Path
        sha256 = "3035A0D0FDD799D42AC83B7D776998AFF07A8BDD3246959E685AA0F8D7ACF94E"
        size = 237568
        role = "candidate_binary"
        mvid = "ad4caf3c-88bc-4971-9c2a-ab78eae395e5"
        matching_pdb = [ordered]@{
            path = (Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb").Path
            sha256 = "61CDC0E8D28047027BF3EE46FD6C3349AD52FAB0846C03868FEB7FEC538E9993"
            size = 59924
        }
    }
    alternate_release_candidate = [ordered]@{
        path = (Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll").Path
        sha256 = "25F6C21092CA3DDCBF7D80EBBC40B6B3E7A3758595E7B3C106D05474F95C8561"
        size = 225792
        role = "candidate_binary"
        mvid = "7b97e307-b06f-40fc-ad6f-5530d180ebe0"
        matching_pdb = [ordered]@{
            path = (Resolve-Path "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb").Path
            sha256 = "A2366CC60F889135D8A63DBD2BCF2340FF93D0229F64250F75D50E95D6AB8166"
            size = 43852
        }
    }
    deployed_mod_assemblies = [ordered]@{
        path = (Resolve-Path "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll").Path
        sha256 = "3035A0D0FDD799D42AC83B7D776998AFF07A8BDD3246959E685AA0F8D7ACF94E"
        size = 237568
        role = "deployed_mod_binary"
        mvid = "ad4caf3c-88bc-4971-9c2a-ab78eae395e5"
        matching_pdb = [ordered]@{
            path = (Resolve-Path "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb").Path
            sha256 = "61CDC0E8D28047027BF3EE46FD6C3349AD52FAB0846C03868FEB7FEC538E9993"
            size = 59924
        }
    }
    sources = [ordered]@{
        engine_host_census = [ordered]@{
            path = (Resolve-Path "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs").Path
            sha256 = "5E9A4DE9A6280A887E3659CE2D80A8029C2BEF41DC615BB3F6F1BB859B1F020E"
            size = 157554
        }
        prefix_verification = [ordered]@{
            byte_count = 72547
            sha256 = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
            marker = "    public static class ContentProfileProvider"
            status = "IMMUTABLE_VERIFIED"
        }
        worker_bridge_cs = [ordered]@{
            path = (Resolve-Path "scratch\WorkerBridgeMod\Source\WorkerBridge.cs").Path
            sha256 = "BA28C2234B2F77C6E50558825B3C9FB9D54DA7B7853D06D8DF4740366A59C718"
            size = 156431
        }
        worker_bridge_csproj = [ordered]@{
            path = (Resolve-Path "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj").Path
            sha256 = "571A58F599FB13761EE426F7DC547A94AE8FAC27CBBC408F0C6BCBEB7DEAC052"
            size = 1774
        }
    }
    runner_artifacts = [ordered]@{
        runner_project = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\Gate05R12OrderRunner.csproj" "runner_project"
        runner_source = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\Program.cs" "runner_source"
        runner_binary = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\bin\Debug\net472\Gate05R12OrderRunner.exe" "runner_binary"
        runner_pdb = Get-FileInfoObj "scratch\EngineGate05R12PackageOrder\Harness\bin\Debug\net472\Gate05R12OrderRunner.pdb" "runner_pdb"
    }
    content_schema_profile = [ordered]@{
        schema_version = "ADR-006B-v5"
        content_contract_version = "ADR-006B-v5-R12"
        supported_coverage_profile = "POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5"
        mod_patch_support_status = "TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1"
        package_policy_status = "TYPED_CANONICAL_PACKAGE_POLICY_ENCODING_V1"
        package_order_status = "CONTIGUOUS_ZERO_BASED_LOAD_ORDER_CONSISTENCY_V1"
        capability_flag = "GATE05_R12_PACKAGE_ORDER"
        version_semantics = "VERSION_MEANING_DISTINCT_COMPATIBILITY_AND_MOD_VERSION_V1"
        patch_disposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED"
        settings_disposition = "USER_MOD_SETTINGS_EXCLUDED"
        def_families_count = 8
    }
    runtime_candidate_proof = [ordered]@{
        debug_codeview_pdb = "C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\Source\\obj\\Debug\\net472\\WarEconomy.WorkerBridge.PoC.pdb"
        release_codeview_pdb = "C:\\Users\\user\\Desktop\\RimMulti\\scratch\\WorkerBridgeMod\\Source\\obj\\Release\\net472\\WarEconomy.WorkerBridge.PoC.pdb"
    }
    tooling_environment = [ordered]@{
        dotnet_sdk = "10.0.201"
        compiler = "Roslyn C# 10+"
        target_framework = "net472"
        os = "Microsoft Windows 11 / 10 x64"
        build_configuration_selected = "Debug"
        build_configuration_alternate = "Release"
        harness_dependencies = "FROZEN_MANAGED_QA_DEPENDENCIES_V1"
    }
}

$json = $manifest | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText("scratch\EngineGate05R12PackageOrder\CANDIDATE_PRE_RUN_MANIFEST.json", $json, [System.Text.Encoding]::UTF8)
Write-Host "Created CANDIDATE_PRE_RUN_MANIFEST.json successfully."
