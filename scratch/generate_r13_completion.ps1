Add-Type -Path "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\bin\Debug\net472\Newtonsoft.Json.dll"

$sha = [System.Security.Cryptography.SHA256]::Create()

function Get-Artifact($role, $p) {
    $full = (Resolve-Path $p).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $obj = [ordered]@{
        role = $role
        path = $full
        sha256 = $hash
        size = $bytes.Length
    }
    if ($p.EndsWith(".dll")) {
        $asm = [System.Reflection.AssemblyName]::GetAssemblyName($full)
        $mod = [System.Reflection.Assembly]::LoadFile($full).ManifestModule
        $obj["mvid"] = $mod.ModuleVersionId.ToString()
    }
    return $obj
}

$artifacts = @(
    (Get-Artifact "implementation_report" "docs\POC_EngineHost_Content_Codec_Gate05_R13.md"),
    (Get-Artifact "release_manifest" "docs\RELEASE_MANIFEST_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE.json"),
    (Get-Artifact "harness" "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\Program.cs"),
    (Get-Artifact "harness_project" "scratch\EngineGate05R13PolicyCacheLifecycle\Harness\Gate05R13CacheRunner.csproj"),
    (Get-Artifact "results" "scratch\EngineGate05R13PolicyCacheLifecycle\results.json"),
    (Get-Artifact "raw_evidence" "scratch\EngineGate05R13PolicyCacheLifecycle\raw_console.txt"),
    (Get-Artifact "candidate_binary" "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
    (Get-Artifact "pdb" "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "alternate_binary" "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"),
    (Get-Artifact "alternate_pdb" "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "deployed_assembly" "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
    (Get-Artifact "deployed_pdb" "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "source" "scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
    (Get-Artifact "source_census" "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
    (Get-Artifact "source_csproj" "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
    (Get-Artifact "pre_run_manifest" "scratch\EngineGate05R13PolicyCacheLifecycle\CANDIDATE_PRE_RUN_MANIFEST.json"),
    (Get-Artifact "engine_freeze_before" "scratch\EngineGate05R13PolicyCacheLifecycle\ENGINE_FREEZE_BEFORE.json"),
    (Get-Artifact "engine_freeze_after" "scratch\EngineGate05R13PolicyCacheLifecycle\ENGINE_FREEZE_AFTER.json"),
    (Get-Artifact "work_log" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749\A_WORK_LOG.md"),
    (Get-Artifact "recovery_ack" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749\A_RECOVERY_ACK.md"),
    (Get-Artifact "ack_json" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749\ACK.json")
)

$summary = "WP_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE / GATE05-R13-POLICY-CACHE-LIFECYCLE single technical objective POLICY_CACHE_LIFECYCLE implementation completed and developer E1 verification recorded. Successfully resolved cache retention and invalidation defects observed in R12 by introducing monotonic process-local configuration generation tracking (ConfigurationGeneration), atomic generation advance on ConfigureExpectedPackagePolicy (record/declaration), ClearConfiguredExpectedPackagePolicy, and same-policy reconfigure, with coherent entry binding (CoherentContentProfileCacheEntry) verifying generation, policy digest, contract version, and timestamp. The cache entry owns an immutable JSON snapshot of the manifest, returning defensive clones via CreateManifestSnapshot() to eliminate external mutation leaks. Isolated the cache state machine into pure instance-owned ContentProfileCacheCore, enabling fully independent, non-polluting unit testing of populated cache lifecycle without provider seeding or native collection. Global ContentProfileProvider delegates to internal _globalCache instance and prohibits synthetic seeding, override, reflection, or bypass. Published entries in ComputeActualContentProfileFingerprint are guarded by generation checks. Updated content contract version to ADR-006B-v5-R13 and capability flag to GATE05_R13_POLICY_CACHE_LIFECYCLE. Preserved R12 independent scoped 265 PASS, R11 encoding, R9 version meaning semantics, Def family sorting, and immutable baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72,547 bytes SHA F3C4F865...). Executed pure positive normal managed runner controls (24/24 PASS) across multiple cultures (ko-KR, en-US, de-DE) with 0 provider compute calls, 0 game/native/operator execution, and 0 negative/adverse tests. Bound PE MVIDs for Debug (48adef37-...) and Release (94055e10-...) candidates. Steam installed DLL incident remains UNKNOWN OPEN INCIDENT. Full Gate05 and Foundation remain HOLD pending independent Sol QA review and Master governance disposition."

$limitations = @(
    "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY: Verification conducted strictly via isolated positive pure normal managed runner controls (24/24 PASS) on pure instance core and normal lifecycle calls with Master-approved frozen dependencies.",
    "PURE_INSTANCE_CORE_AND_NORMAL_CONFIGURATION_LIFECYCLE_EVIDENCE_ONLY: Cache population, invalidation, and defensive copy immutability verified on standalone ContentProfileCacheCore instances; global provider actual compute and entry publication untested in managed harness.",
    "NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED: In-engine, game runtime, native execution, and operator promotion were strictly prohibited and not executed.",
    "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
    "MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN: Dynamic evaluation of user mod settings/patches and real operator provenance remain separate OPEN gates.",
    "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Dedicated Server remains final Domain Authority; Master governs release."
)

$compObj = [ordered]@{
    schema_version = 1
    producer = "A"
    report_kind = "E1"
    dispatch_id = "WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749"
    wp_id = "WP_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE"
    wp_revision = "GATE05-R13-POLICY-CACHE-LIFECYCLE"
    result_id = "WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-RESULT-01"
    run_id = "GATE05-R13-POLICY-CACHE-LIFECYCLE-RUN-01"
    status = "COMPLETED"
    completed_at = [System.DateTime]::UtcNow.ToString("o")
    summary = $summary
    e1_verdict = "SCOPED_POSITIVE_NORMAL_PASS"
    limitations = $limitations
    artifacts = $artifacts
}

$jsonText = [Newtonsoft.Json.JsonConvert]::SerializeObject($compObj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$destPath = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R13-POLICY-CACHE-LIFECYCLE-20261009-DIRECT-2661a749\COMPLETION.json"
[System.IO.File]::WriteAllText($destPath, $jsonText, $utf8NoBom)

Write-Host "Created $destPath successfully with $($artifacts.Count) artifacts."
