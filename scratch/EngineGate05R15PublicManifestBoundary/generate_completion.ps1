$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$taskDir = "$workspaceRoot\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052"
$scratchDir = "$workspaceRoot\scratch\EngineGate05R15PublicManifestBoundary"

$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Get-Art([string]$role, [string]$fullPath, [string]$mvid = $null) {
    if (-not (Test-Path $fullPath)) { throw "Artifact not found: $fullPath" }
    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
    $res = [ordered]@{
        role = $role
        path = $fullPath
        sha256 = $hash
        size = $bytes.Length
    }
    if ($mvid -ne $null) {
        $res["mvid"] = $mvid
    }
    return $res
}

$artifacts = @(
    (Get-Art "implementation_report" "$workspaceRoot\docs\POC_EngineHost_Content_Codec_Gate05_R15.md"),
    (Get-Art "release_manifest" "$workspaceRoot\docs\RELEASE_MANIFEST_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY.json"),
    (Get-Art "harness" "$scratchDir\Harness\Program.cs"),
    (Get-Art "harness_project" "$scratchDir\Harness\Gate05R15BoundaryRunner.csproj"),
    (Get-Art "results" "$scratchDir\run_default\results.json"),
    (Get-Art "raw_evidence" "$scratchDir\run_default\raw_console.txt"),
    (Get-Art "candidate_binary" "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll" "4fb1a25f-72c8-426d-b93f-d6cba4f9af72"),
    (Get-Art "pdb" "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Art "alternate_binary" "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll" "58766cdc-afee-4682-858a-dab68c96e36e"),
    (Get-Art "alternate_pdb" "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Art "deployed_assembly" "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll" "4fb1a25f-72c8-426d-b93f-d6cba4f9af72"),
    (Get-Art "deployed_pdb" "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Art "source" "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
    (Get-Art "source_census" "$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
    (Get-Art "source_csproj" "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
    (Get-Art "pre_run_manifest" "$scratchDir\CANDIDATE_PRE_RUN_MANIFEST.json"),
    (Get-Art "engine_freeze_before" "$scratchDir\ENGINE_FREEZE_BEFORE.json"),
    (Get-Art "engine_freeze_after" "$scratchDir\ENGINE_FREEZE_AFTER.json"),
    (Get-Art "work_log" "$taskDir\A_WORK_LOG.md"),
    (Get-Art "recovery_ack" "$taskDir\A_RECOVERY_ACK.md"),
    (Get-Art "ack_json" "$taskDir\ACK.json")
)

$completion = [ordered]@{
    schema_version = 1
    producer = "A"
    report_kind = "E1"
    dispatch_id = "WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052"
    wp_id = "WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY"
    wp_revision = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY"
    result_id = "WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-RESULT-01"
    run_id = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-RUN-01"
    status = "COMPLETED"
    completed_at = (Get-Date).ToUniversalTime().ToString("o")
    summary = "WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY / GATE05-R15-PUBLIC-MANIFEST-BOUNDARY single technical objective PUBLIC_MANIFEST_BOUNDARY implementation completed and developer E1 verification recorded. Successfully sealed public caller-policy native collector overload into internal private helper CollectActualContentProfileManifestInternal, preventing external arbitrary policy injection. Established a single trusted provider-owned computation and success linearization helper ComputeAndPublishActualContentProfile shared by parameterless ComputeActualContentProfileManifest and ComputeActualContentProfileFingerprint. Under the single core synchronization lock, validates captured generation and configured policy identity against CURRENT provider state before returning the immutable result; refused publication or currentstamp validation throws an explicit InvalidOperationException without fallback, preventing unadmitted or stale content leakage. Maintained R14 InvalidateCache generation advance (+1), normal core ownership, defensive manifest cloning, pure codec logic, and introduced generation-scoped error protection in SetComputationError. Updated content contract version to ADR-006B-v5-R15 and capability flag to GATE05_R15_PUBLIC_MANIFEST_BOUNDARY. Preserved R14 independent scoped 339 PASS, R12 0-based order, R11 encoding, R9 version meaning semantics, Def family sorting, and immutable baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72,547 bytes SHA F3C4F865...). Executed pure positive normal managed runner controls (25/25 PASS, numeric exit 0) across isolated process directories (ko-KR, en-US, de-DE) performing 55 normal cache lifecycle calls while strictly executing 0 prohibited calls (ComputeActual = 0, GetActual = 0, native = 0, adverse/rejection = 0). Proved via reflection that no public caller-policy native collector overload exists. Bound PE MVIDs for Debug (4fb1a25f-...) and Release (58766cdc-...) candidates. Steam installed DLL incident remains UNKNOWN OPEN INCIDENT. Full Gate05 and Foundation remain HOLD pending independent Sol QA review and Master governance disposition."
    e1_verdict = "SCOPED_POSITIVE_NORMAL_PASS"
    limitations = @(
        "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY: Verification conducted strictly via isolated positive pure normal managed runner controls (25/25 PASS, exit 0) on pure instance core and normal lifecycle calls with Master-approved frozen dependencies.",
        "PURE_INSTANCE_CORE_AND_NORMAL_CONFIGURATION_LIFECYCLE_EVIDENCE_ONLY: Cache publication, defensive copy immutability, generation advance, and reflection verification verified on standalone ContentProfileCacheCore instances and provider metadata; global provider actual compute and entry publication untested in managed harness.",
        "NATIVE_ACTUAL_COMPUTATION_PROHIBITED_AND_UNTESTED: In-engine, game runtime, native execution, and operator promotion were strictly prohibited and not executed.",
        "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
        "MOD_PATCH_SETTINGS_DYNAMIC_EVALUATION_SEPARATE_OPEN: Dynamic evaluation of user mod settings/patches and real operator provenance remain separate OPEN gates.",
        "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Dedicated Server remains final Domain Authority; Master governs release."
    )
    artifacts = $artifacts
}

Add-Type -Path "$workspaceRoot\WarEconomyMod\1.6\Assemblies\Newtonsoft.Json.dll"
$jsonString = [Newtonsoft.Json.JsonConvert]::SerializeObject($completion, [Newtonsoft.Json.Formatting]::Indented)

$targetPath = "$taskDir\COMPLETION.json"
[System.IO.File]::WriteAllText($targetPath, $jsonString, [System.Text.Encoding]::UTF8)

# Validate parsing
[Newtonsoft.Json.Linq.JObject]::Parse($jsonString) | Out-Null
Write-Host "COMPLETION.json created successfully with $($artifacts.Count) artifacts."
