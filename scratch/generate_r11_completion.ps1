$artifacts = @(
    @{ role = "implementation_report"; path = "docs\POC_EngineHost_Content_Codec_Gate05_R11.md" },
    @{ role = "release_manifest"; path = "docs\RELEASE_MANIFEST_ENGINE_GATE05_R11_POLICY_ENCODING.json" },
    @{ role = "harness"; path = "scratch\EngineGate05R11PolicyEncoding\Harness\Program.cs" },
    @{ role = "harness_project"; path = "scratch\EngineGate05R11PolicyEncoding\Harness\Gate05R11PolicyRunner.csproj" },
    @{ role = "results"; path = "scratch\EngineGate05R11PolicyEncoding\results.json" },
    @{ role = "raw_evidence"; path = "scratch\EngineGate05R11PolicyEncoding\raw_console.txt" },
    @{ role = "candidate_binary"; path = "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"; mvid = "e6c6f6fd-2915-4493-8ef9-dc5d87de1c6b" },
    @{ role = "pdb"; path = "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb" },
    @{ role = "alternate_binary"; path = "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"; mvid = "35dfe68f-6a6f-44cc-a648-7c8153f6a2ad" },
    @{ role = "alternate_pdb"; path = "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb" },
    @{ role = "deployed_assembly"; path = "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"; mvid = "e6c6f6fd-2915-4493-8ef9-dc5d87de1c6b" },
    @{ role = "deployed_pdb"; path = "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb" },
    @{ role = "source"; path = "scratch\WorkerBridgeMod\Source\WorkerBridge.cs" },
    @{ role = "source_census"; path = "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs" },
    @{ role = "source_csproj"; path = "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" },
    @{ role = "pre_run_manifest"; path = "scratch\EngineGate05R11PolicyEncoding\CANDIDATE_PRE_RUN_MANIFEST.json" },
    @{ role = "engine_freeze_before"; path = "scratch\EngineGate05R11PolicyEncoding\ENGINE_FREEZE_BEFORE.json" },
    @{ role = "engine_freeze_after"; path = "scratch\EngineGate05R11PolicyEncoding\ENGINE_FREEZE_AFTER.json" },
    @{ role = "work_log"; path = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\A_WORK_LOG.md" },
    @{ role = "recovery_ack"; path = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\A_RECOVERY_ACK.md" },
    @{ role = "ack_json"; path = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\ACK.json" }
)

$sha = [System.Security.Cryptography.SHA256]::Create()
$artList = @()

foreach ($a in $artifacts) {
    $full = (Resolve-Path $a.path).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $hash = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $entry = [ordered]@{
        role = $a.role
        path = $full
        sha256 = $hash
        size = $bytes.Length
    }
    if ($a.ContainsKey("mvid")) {
        $entry["mvid"] = $a.mvid
    }
    $artList += $entry
}

$completion = [ordered]@{
    schema_version = 1
    producer = "A"
    report_kind = "E1"
    dispatch_id = "WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350"
    wp_id = "WP_ENGINE_GATE05_R11_POLICY_ENCODING"
    wp_revision = "GATE05-R11-POLICY-ENCODING"
    result_id = "WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-RESULT-01"
    status = "COMPLETED"
    completed_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.ffffffZ")
    summary = "WP_ENGINE_GATE05_R11_POLICY_ENCODING / GATE05-R11-POLICY-ENCODING single technical objective POLICY_ENCODING implementation completed and developer E1 verification recorded. Successfully implemented concrete typed versioned canonical package policy declaration (ExpectedPackagePolicyDeclaration with schemaVersion constant WE-PACKAGE-POLICY-V1, policyId, revision, admittedPackageIds), deterministic lossless culture-independent JSON escaping (EscapeJsonString) preserving original spelling, whitespace, Unicode, punctuation of opaque identifiers without Trim, pure canonical compact JSON serialization/deserialization (SerializePackagePolicy / DeserializePackagePolicy), SHA-256 uppercase hex digest calculation of canonical JSON bytes, overload parity routing through the canonical declaration, removed policy-specific Trim in CanonicalNormalize, updated content contract version to ADR-006B-v5-R11 and capability flag to GATE05_R11_POLICY_ENCODING. Preserved R10 scoped PASS, R9 version meaning repair (null modVersion preserved across Invariant, en-US, de-DE), child fail-closed observation, composite key uniqueness, Def family canonical sorting, and immutable baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72,547 bytes SHA F3C4F865...). Executed pure positive normal managed runner controls (14/14 PASS) with 0 configuration lifecycle calls, 0 provider compute calls, and 0 negative/adverse tests. Bound PE MVIDs for Debug (e6c6f6fd-...) and Release (35dfe68f-...) candidates. Steam installed DLL incident remains UNKNOWN OPEN INCIDENT. Full Gate05 and Foundation remain HOLD pending independent Sol QA review and Master governance disposition."
    e1_verdict = "SCOPED_POSITIVE_NORMAL_PASS"
    limitations = @(
        "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY: Verification conducted strictly via isolated positive pure normal managed runner controls (14/14 PASS) with Master-approved frozen dependencies.",
        "NATIVE_PROMOTION_FULL_E2_NOT_RELEASED: In-engine, game runtime, native execution, and operator promotion were strictly prohibited and not executed.",
        "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
        "ORDER_CACHE_PATCHSETTINGS_OPERATOR_SEPARATE: Physical array load-order validation, policy cache generation, patch/settings dynamic evaluation, and real operator provenance remain separate OPEN gates.",
        "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Dedicated Server remains final Domain Authority; Master governs release."
    )
    artifacts = $artList
}

$json = $completion | ConvertTo-Json -Depth 6
$outPath = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R11-POLICY-ENCODING-20261009-DIRECT-bec3d350\COMPLETION.json"
[System.IO.File]::WriteAllText($outPath, $json, [System.Text.Encoding]::UTF8)
Write-Host "Generated COMPLETION.json successfully. Artifacts count: $($artList.Count)"
