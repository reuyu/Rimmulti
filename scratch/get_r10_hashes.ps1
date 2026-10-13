$debugDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll'
$debugPdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb'
$releaseDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll'
$releasePdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb'
$deployedDll = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll'
$deployedPdb = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb'

$censusCs = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs'
$bridgeCs = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs'
$bridgeCsproj = 'C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj'

function Get-MvidProcess($dllPath) {
    $script = "[System.IO.File]::WriteAllText('$env:TEMP\mvid.tmp', [System.Reflection.Assembly]::ReflectionOnlyLoad([System.IO.File]::ReadAllBytes('$dllPath')).ManifestModule.ModuleVersionId.ToString())"
    powershell -NoProfile -Command $script
    $mvid = Get-Content "$env:TEMP\mvid.tmp" -Raw
    return $mvid.Trim()
}

$dbgMvid = Get-MvidProcess $debugDll
$relMvid = Get-MvidProcess $releaseDll
$depMvid = Get-MvidProcess $deployedDll

$dbgSha = (Get-FileHash $debugDll -Algorithm SHA256).Hash
$dbgSize = (Get-Item $debugDll).Length
$dbgPdbSha = (Get-FileHash $debugPdb -Algorithm SHA256).Hash
$dbgPdbSize = (Get-Item $debugPdb).Length

$relSha = (Get-FileHash $releaseDll -Algorithm SHA256).Hash
$relSize = (Get-Item $releaseDll).Length
$relPdbSha = (Get-FileHash $releasePdb -Algorithm SHA256).Hash
$relPdbSize = (Get-Item $releasePdb).Length

$depSha = (Get-FileHash $deployedDll -Algorithm SHA256).Hash
$depSize = (Get-Item $deployedDll).Length
$depPdbSha = (Get-FileHash $deployedPdb -Algorithm SHA256).Hash
$depPdbSize = (Get-Item $deployedPdb).Length

$censusSha = (Get-FileHash $censusCs -Algorithm SHA256).Hash
$censusSize = (Get-Item $censusCs).Length
$bridgeSha = (Get-FileHash $bridgeCs -Algorithm SHA256).Hash
$bridgeSize = (Get-Item $bridgeCs).Length
$projSha = (Get-FileHash $bridgeCsproj -Algorithm SHA256).Hash
$projSize = (Get-Item $bridgeCsproj).Length

$manifest = [ordered]@{
    "schema_version" = "ADR-006B-v5"
    "run_id" = "GATE05-R10-PACKAGE-POLICY-PRE-RUN-01"
    "dispatch_id" = "WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb"
    "wp_id" = "WP_ENGINE_GATE05_R10_PACKAGE_POLICY"
    "wp_revision" = "GATE05-R10-PACKAGE-POLICY"
    "created_at" = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
    "selected_candidate" = [ordered]@{
        "path" = $debugDll
        "sha256" = $dbgSha
        "size" = $dbgSize
        "role" = "candidate_binary"
        "mvid" = $dbgMvid
        "matching_pdb" = [ordered]@{
            "path" = $debugPdb
            "sha256" = $dbgPdbSha
            "size" = $dbgPdbSize
        }
    }
    "alternate_release_candidate" = [ordered]@{
        "path" = $releaseDll
        "sha256" = $relSha
        "size" = $relSize
        "role" = "candidate_binary"
        "mvid" = $relMvid
        "matching_pdb" = [ordered]@{
            "path" = $releasePdb
            "sha256" = $relPdbSha
            "size" = $relPdbSize
        }
    }
    "deployed_mod_assemblies" = [ordered]@{
        "path" = $deployedDll
        "sha256" = $depSha
        "size" = $depSize
        "role" = "deployed_mod_binary"
        "mvid" = $depMvid
        "matching_pdb" = [ordered]@{
            "path" = $deployedPdb
            "sha256" = $depPdbSha
            "size" = $depPdbSize
        }
    }
    "sources" = [ordered]@{
        "engine_host_census" = [ordered]@{
            "path" = $censusCs
            "sha256" = $censusSha
            "size" = $censusSize
        }
        "prefix_verification" = [ordered]@{
            "byte_count" = 72547
            "sha256" = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
            "marker" = "    public static class ContentProfileProvider"
            "status" = "IMMUTABLE_VERIFIED"
        }
        "worker_bridge_cs" = [ordered]@{
            "path" = $bridgeCs
            "sha256" = $bridgeSha
            "size" = $bridgeSize
        }
        "worker_bridge_csproj" = [ordered]@{
            "path" = $bridgeCsproj
            "sha256" = $projSha
            "size" = $projSize
        }
    }
    "content_schema_profile" = [ordered]@{
        "schema_version" = "ADR-006B-v5"
        "content_contract_version" = "ADR-006B-v5-R10"
        "supported_coverage_profile" = "POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5"
        "mod_patch_support_status" = "TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1"
        "package_policy_status" = "TYPED_EXPECTED_PACKAGE_POLICY_CHECK_V1"
        "version_semantics" = "VERSION_MEANING_DISTINCT_COMPATIBILITY_AND_MOD_VERSION_V1"
        "patch_disposition" = "COUNT_OBSERVED_RAW_AST_EXCLUDED"
        "settings_disposition" = "USER_MOD_SETTINGS_EXCLUDED"
        "def_families_count" = 8
    }
    "runtime_candidate_proof" = [ordered]@{
        "debug_codeview_pdb" = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
        "release_codeview_pdb" = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\obj\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
    }
    "tooling_environment" = [ordered]@{
        "dotnet_sdk" = "10.0.201"
        "compiler" = "Roslyn C# 10+"
        "target_framework" = "net472"
        "os" = "Microsoft Windows 11 / 10 x64"
        "build_configuration_selected" = "Debug"
        "build_configuration_alternate" = "Release"
        "harness_dependencies" = "FROZEN_MANAGED_QA_DEPENDENCIES_V1"
    }
}

$destPath = 'C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\CANDIDATE_PRE_RUN_MANIFEST.json'
[System.IO.File]::WriteAllText($destPath, ($manifest | ConvertTo-Json -Depth 10))
Write-Host "Wrote CANDIDATE_PRE_RUN_MANIFEST.json successfully to $destPath"
