$debugDll = 'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.dll'
$debugPdb = 'scratch/WorkerBridgeMod/Source/bin/Debug/net472/WarEconomy.WorkerBridge.PoC.pdb'
$releaseDll = 'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.dll'
$releasePdb = 'scratch/WorkerBridgeMod/Source/bin/Release/net472/WarEconomy.WorkerBridge.PoC.pdb'

$files = @(
  'scratch/WorkerBridgeMod/Source/WorkerBridge.cs',
  'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs',
  'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj',
  'scratch/EngineGate05R10PackagePolicy/Harness/Gate05R10PackageRunner.csproj',
  'scratch/EngineGate05R10PackagePolicy/Harness/Program.cs',
  'scratch/EngineGate05R10PackagePolicy/results.json',
  'scratch/EngineGate05R10PackagePolicy/raw_console.txt',
  'scratch/EngineGate05R10PackagePolicy/CANDIDATE_PRE_RUN_MANIFEST.json',
  'scratch/EngineGate05R10PackagePolicy/ENGINE_FREEZE_BEFORE.json',
  'scratch/EngineGate05R10PackagePolicy/ENGINE_FREEZE_AFTER.json',
  'docs/POC_EngineHost_Content_Codec_Gate05_R10.md'
)

$root = 'C:\Users\user\Desktop\RimMulti'

function Get-Info($relPath) {
    $full = Join-Path $root $relPath
    $h = (Get-FileHash $full -Algorithm SHA256).Hash
    $s = (Get-Item $full).Length
    return @{ path = $relPath.Replace('/', '\'); sha256 = $h; bytes = $s }
}

function Get-MvidProcess($fullPath) {
    $script = "[System.IO.File]::WriteAllText('$env:TEMP\mvid.tmp', [System.Reflection.Assembly]::ReflectionOnlyLoad([System.IO.File]::ReadAllBytes('$fullPath')).ManifestModule.ModuleVersionId.ToString())"
    powershell -NoProfile -Command $script
    $mvid = Get-Content "$env:TEMP\mvid.tmp" -Raw
    return $mvid.Trim()
}

$dbgDllInfo = Get-Info $debugDll
$dbgPdbInfo = Get-Info $debugPdb
$relDllInfo = Get-Info $releaseDll
$relPdbInfo = Get-Info $releasePdb

$dbgMvid = Get-MvidProcess (Join-Path $root $debugDll)
$relMvid = Get-MvidProcess (Join-Path $root $releaseDll)

$releaseManifest = [ordered]@{
  "manifest_version" = "1.0"
  "work_package" = "WP_ENGINE_GATE05_R10_PACKAGE_POLICY"
  "candidate_lineage" = "GATE05-R10-PACKAGE-POLICY"
  "created_at_utc" = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.ffffff+00:00")
  "agent_role" = "Antigravity A"
  "dispatch_id" = "WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb"
  "selected_candidate" = [ordered]@{
    "configuration" = "Debug"
    "target_framework" = "net472"
    "dll_path" = $dbgDllInfo.path
    "dll_sha256" = $dbgDllInfo.sha256
    "dll_bytes" = $dbgDllInfo.bytes
    "pdb_path" = $dbgPdbInfo.path
    "pdb_sha256" = $dbgPdbInfo.sha256
    "pdb_bytes" = $dbgPdbInfo.bytes
    "mvid" = $dbgMvid
  }
  "alternate_candidate" = [ordered]@{
    "configuration" = "Release"
    "target_framework" = "net472"
    "dll_path" = $relDllInfo.path
    "dll_sha256" = $relDllInfo.sha256
    "dll_bytes" = $relDllInfo.bytes
    "pdb_path" = $relPdbInfo.path
    "pdb_sha256" = $relPdbInfo.sha256
    "pdb_bytes" = $relPdbInfo.bytes
    "mvid" = $relMvid
  }
  "source_files" = @(
    [ordered]@{
      "path" = "scratch\WorkerBridgeMod\Source\WorkerBridge.cs"
      "sha256" = (Get-Info 'scratch/WorkerBridgeMod/Source/WorkerBridge.cs').sha256
      "bytes" = (Get-Info 'scratch/WorkerBridgeMod/Source/WorkerBridge.cs').bytes
    },
    [ordered]@{
      "path" = "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
      "sha256" = (Get-Info 'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs').sha256
      "bytes" = (Get-Info 'scratch/WorkerBridgeMod/Source/EngineHostCensus.cs').bytes
      "prefix_marker" = "    public static class ContentProfileProvider"
      "prefix_length" = 72547
      "prefix_sha256" = "F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887"
    },
    [ordered]@{
      "path" = "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"
      "sha256" = (Get-Info 'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj').sha256
      "bytes" = (Get-Info 'scratch/WorkerBridgeMod/Source/WorkerBridge.csproj').bytes
    }
  )
  "verification_evidence" = [ordered]@{
    "runner_project" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\Harness\Gate05R10PackageRunner.csproj"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/Harness/Gate05R10PackageRunner.csproj').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/Harness/Gate05R10PackageRunner.csproj').bytes
    }
    "runner_source" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\Harness\Program.cs"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/Harness/Program.cs').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/Harness/Program.cs').bytes
    }
    "results_json" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\results.json"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/results.json').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/results.json').bytes
    }
    "raw_console_log" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\raw_console.txt"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/raw_console.txt').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/raw_console.txt').bytes
    }
    "pre_run_manifest" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\CANDIDATE_PRE_RUN_MANIFEST.json"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/CANDIDATE_PRE_RUN_MANIFEST.json').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/CANDIDATE_PRE_RUN_MANIFEST.json').bytes
    }
    "engine_freeze_before" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\ENGINE_FREEZE_BEFORE.json"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/ENGINE_FREEZE_BEFORE.json').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/ENGINE_FREEZE_BEFORE.json').bytes
    }
    "engine_freeze_after" = [ordered]@{
      "path" = "scratch\EngineGate05R10PackagePolicy\ENGINE_FREEZE_AFTER.json"
      "sha256" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/ENGINE_FREEZE_AFTER.json').sha256
      "bytes" = (Get-Info 'scratch/EngineGate05R10PackagePolicy/ENGINE_FREEZE_AFTER.json').bytes
    }
    "report_markdown" = [ordered]@{
      "path" = "docs\POC_EngineHost_Content_Codec_Gate05_R10.md"
      "sha256" = (Get-Info 'docs/POC_EngineHost_Content_Codec_Gate05_R10.md').sha256
      "bytes" = (Get-Info 'docs/POC_EngineHost_Content_Codec_Gate05_R10.md').bytes
    }
  }
  "summary" = [ordered]@{
    "total_tests" = 19
    "pass" = 19
    "fail" = 0
    "e1_verdict" = "IMPLEMENTATION_PARTIAL"
    "codec_status" = "POSITIVE_NORMAL_DTO_AND_PACKAGE_POLICY_VERIFIED"
    "native_observation_status" = "NATIVE_UNTESTED (Prohibited under WP_ENGINE_GATE05_R10_PACKAGE_POLICY)"
    "installed_incident_status" = "UNKNOWN OPEN INCIDENT"
    "disposition_note" = "Gate05-R10 implements explicit typed ExpectedPackagePolicyRecord, deterministic canonical policy digest computation, pure package inventory check against observed mods, replaces default-only POC_DECLARED_PACKAGES_ONLY assertion with UNCONFIGURED default and CHECKED_POLICY binding, while preserving R9 version meaning repair across Invariant, en-US, and de-DE. Tested with 19 positive normal controls (19/19 PASS). Full Gate05 and Foundation remain HOLD pending independent QA and Master governance disposition."
  }
}

$outPath = Join-Path $root 'docs\RELEASE_MANIFEST_ENGINE_GATE05_R10_PACKAGE_POLICY.json'
[System.IO.File]::WriteAllText($outPath, ($releaseManifest | ConvertTo-Json -Depth 10), [System.Text.Encoding]::UTF8)
Write-Output "Wrote release manifest to $outPath"
