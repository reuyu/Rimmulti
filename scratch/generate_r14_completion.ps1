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
        $mod = [System.Reflection.Assembly]::LoadFile($full).ManifestModule
        $obj["mvid"] = $mod.ModuleVersionId.ToString()
    }
    return $obj
}

$artifacts = @(
    (Get-Artifact "implementation_report" "docs\POC_EngineHost_Content_Codec_Gate05_R14.md"),
    (Get-Artifact "release_manifest" "docs\RELEASE_MANIFEST_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION.json"),
    (Get-Artifact "harness" "scratch\EngineGate05R14PolicyCapturePublication\Harness\Program.cs"),
    (Get-Artifact "harness_project" "scratch\EngineGate05R14PolicyCapturePublication\Harness\Gate05R14CacheRunner.csproj"),
    (Get-Artifact "results" "scratch\EngineGate05R14PolicyCapturePublication\results.json"),
    (Get-Artifact "raw_evidence" "scratch\EngineGate05R14PolicyCapturePublication\raw_console.txt"),
    (Get-Artifact "candidate_binary" "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"),
    (Get-Artifact "pdb" "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "alternate_binary" "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"),
    (Get-Artifact "alternate_pdb" "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "deployed_assembly" "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"),
    (Get-Artifact "deployed_pdb" "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "source" "scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
    (Get-Artifact "source_census" "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
    (Get-Artifact "source_csproj" "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
    (Get-Artifact "pre_run_manifest" "scratch\EngineGate05R14PolicyCapturePublication\CANDIDATE_PRE_RUN_MANIFEST.json"),
    (Get-Artifact "engine_freeze_before" "scratch\EngineGate05R14PolicyCapturePublication\ENGINE_FREEZE_BEFORE.json"),
    (Get-Artifact "engine_freeze_after" "scratch\EngineGate05R14PolicyCapturePublication\ENGINE_FREEZE_AFTER.json"),
    (Get-Artifact "work_log" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b\A_WORK_LOG.md"),
    (Get-Artifact "recovery_ack" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b\A_RECOVERY_ACK.md"),
    (Get-Artifact "ack_json" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b\ACK.json")
)

$summary = "WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION / GATE05-R14-POLICY-CAPTURE-PUBLICATION single technical objective POLICY_CAPTURE_PUBLICATION implementation completed and developer E1 verification recorded. Successfully resolved single captured policy pass-through and publication refusal defects by ensuring one immutable policy record captured before collection is passed throughout manifest collection, package policy check, and disposition without rereading global state mid-operation. Removed path where failed publication returned success fingerprint, enforcing explicit InvalidOperationException on refused publication to prevent unadmitted/stale fingerprint leakage. InvalidateCache now advances ConfigurationGeneration (+1) under lock to fence prior in-flight captures. Updated content contract version to ADR-006B-v5-R14 and capability flag to GATE05_R14_POLICY_CAPTURE_PUBLICATION. Preserved R13 independent scoped 339 PASS, R12 0-based order, R11 encoding, R9 version meaning semantics, Def family sorting, and immutable baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72,547 bytes SHA F3C4F865...). Executed pure positive normal managed runner controls (22/22 PASS, numeric exit 0) across multiple cultures (ko-KR, en-US, de-DE) performing 46 normal cache lifecycle calls on pure instance core and provider configuration while strictly executing 0 prohibited calls (ComputeActual = 0, GetActual = 0, native = 0, adverse/rejection = 0). Bound PE MVIDs for Debug (acab0270-...) and Release (874a8ce6-...) candidates. Steam installed DLL incident remains UNKNOWN OPEN INCIDENT. Full Gate05 and Foundation remain HOLD pending independent Sol QA review and Master governance disposition."

$limitations = @(
    "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY: Verification conducted strictly via isolated positive pure normal managed runner controls (22/22 PASS, exit 0) on pure instance core and normal lifecycle calls with Master-approved frozen dependencies.",
    "PURE_INSTANCE_CORE_AND_NORMAL_CONFIGURATION_LIFECYCLE_EVIDENCE_ONLY: Cache publication, defensive copy immutability, and generation advance verified on standalone ContentProfileCacheCore instances; global provider actual compute and entry publication untested in managed harness.",
    "NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED: In-engine, game runtime, native execution, and operator promotion were strictly prohibited and not executed.",
    "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
    "MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN: Dynamic evaluation of user mod settings/patches and real operator provenance remain separate OPEN gates.",
    "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Dedicated Server remains final Domain Authority; Master governs release."
)

$compObj = [ordered]@{
    schema_version = 1
    producer = "A"
    report_kind = "E1"
    dispatch_id = "WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b"
    wp_id = "WP_ENGINE_GATE05_R14_POLICY_CAPTURE_PUBLICATION"
    wp_revision = "GATE05-R14-POLICY-CAPTURE-PUBLICATION"
    result_id = "WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-RESULT-01"
    run_id = "GATE05-R14-POLICY-CAPTURE-PUBLICATION-RUN-01"
    status = "COMPLETED"
    completed_at = [System.DateTime]::UtcNow.ToString("o")
    summary = $summary
    e1_verdict = "SCOPED_POSITIVE_NORMAL_PASS"
    limitations = $limitations
    artifacts = $artifacts
}

$jsonText = [Newtonsoft.Json.JsonConvert]::SerializeObject($compObj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$destPath = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R14-POLICY-CAPTURE-PUBLICATION-20261009-DIRECT-ff285a3b\COMPLETION.json"
[System.IO.File]::WriteAllText($destPath, $jsonText, $utf8NoBom)

Write-Host "Created $destPath successfully with $($artifacts.Count) artifacts."
