# Step 1: Re-generate release manifest to guarantee fresh hashes of all verification evidence
& "scratch\generate_r12_release_manifest.ps1"

Add-Type -Path "scratch\EngineGate05R12PackageOrder\Harness\bin\Debug\net472\Newtonsoft.Json.dll"

$sha = [System.Security.Cryptography.SHA256]::Create()

function Get-Artifact($role, $path, $mvid = $null) {
    $full = (Resolve-Path $path).Path
    $bytes = [System.IO.File]::ReadAllBytes($full)
    $h = [System.BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "")
    $art = [ordered]@{
        role = $role
        path = $full
        sha256 = $h
        size = $bytes.Length
    }
    if ($mvid) {
        $art["mvid"] = $mvid
    }
    return $art
}

$artifacts = @(
    (Get-Artifact "implementation_report" "docs\POC_EngineHost_Content_Codec_Gate05_R12.md"),
    (Get-Artifact "release_manifest" "docs\RELEASE_MANIFEST_ENGINE_GATE05_R12_PACKAGE_ORDER.json"),
    (Get-Artifact "harness" "scratch\EngineGate05R12PackageOrder\Harness\Program.cs"),
    (Get-Artifact "harness_project" "scratch\EngineGate05R12PackageOrder\Harness\Gate05R12OrderRunner.csproj"),
    (Get-Artifact "results" "scratch\EngineGate05R12PackageOrder\results.json"),
    (Get-Artifact "raw_evidence" "scratch\EngineGate05R12PackageOrder\raw_console.txt"),
    (Get-Artifact "candidate_binary" "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll" "ad4caf3c-88bc-4971-9c2a-ab78eae395e5"),
    (Get-Artifact "pdb" "scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "alternate_binary" "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll" "7b97e307-b06f-40fc-ad6f-5530d180ebe0"),
    (Get-Artifact "alternate_pdb" "scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "deployed_assembly" "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll" "ad4caf3c-88bc-4971-9c2a-ab78eae395e5"),
    (Get-Artifact "deployed_pdb" "scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"),
    (Get-Artifact "source" "scratch\WorkerBridgeMod\Source\WorkerBridge.cs"),
    (Get-Artifact "source_census" "scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"),
    (Get-Artifact "source_csproj" "scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"),
    (Get-Artifact "pre_run_manifest" "scratch\EngineGate05R12PackageOrder\CANDIDATE_PRE_RUN_MANIFEST.json"),
    (Get-Artifact "engine_freeze_before" "scratch\EngineGate05R12PackageOrder\ENGINE_FREEZE_BEFORE.json"),
    (Get-Artifact "engine_freeze_after" "scratch\EngineGate05R12PackageOrder\ENGINE_FREEZE_AFTER.json"),
    (Get-Artifact "work_log" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6\A_WORK_LOG.md"),
    (Get-Artifact "recovery_ack" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6\A_RECOVERY_ACK.md"),
    (Get-Artifact "ack_json" "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6\ACK.json")
)

$summaryText = "WP_ENGINE_GATE05_R12_PACKAGE_ORDER / GATE05-R12-PACKAGE-ORDER single technical objective PACKAGE_ORDER implementation completed and developer E1 verification recorded. Successfully implemented pure package policy comparison based on declared 0-based contiguous loadOrder (0 .. count - 1), ensuring physical transport array permutation invariance while preserving distinct valid execution sequences. CheckPackagePolicy uses a copied ordered view preventing caller activeMods list/element mutation, while recording rawPhysicalPackages for diagnostic traceability alongside effective execution sequence observedPackages. TryAdmitWithPackagePolicy canonical normalization ensures identical canonical JSON and digest across physical permutations. Source-only static guards enforce non-negative, non-duplicate, contiguous loadOrder without runtime game/native execution. Updated content contract version to ADR-006B-v5-R12 and capability flag to GATE05_R12_PACKAGE_ORDER. Fixed R11 release manifest packaging defect by generating fully valid JSON via serializer and pinned candidate pre-run manifest prior to execution with unified run_id (GATE05-R12-PACKAGE-ORDER-RUN-01). Preserved R11 scoped 247 PASS, R9 version meaning semantics, Def family canonical sorting, and immutable baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72,547 bytes SHA F3C4F865...). Executed pure positive normal managed runner controls (18/18 PASS) across multiple cultures (ko-KR, en-US, de-DE) with 0 provider compute calls, 0 configuration lifecycle calls, 0 cache calls, and 0 negative/adverse tests. Bound PE MVIDs for Debug (ad4caf3c-...) and Release (7b97e307-...) candidates. Steam installed DLL incident remains UNKNOWN OPEN INCIDENT. Full Gate05 and Foundation remain HOLD pending independent Sol QA review and Master governance disposition."

$completionObj = [ordered]@{
    schema_version = 1
    producer = "A"
    report_kind = "E1"
    dispatch_id = "WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6"
    wp_id = "WP_ENGINE_GATE05_R12_PACKAGE_ORDER"
    wp_revision = "GATE05-R12-PACKAGE-ORDER"
    result_id = "WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-RESULT-01"
    run_id = "GATE05-R12-PACKAGE-ORDER-RUN-01"
    status = "COMPLETED"
    completed_at = [System.DateTime]::UtcNow.ToString("o")
    summary = $summaryText
    e1_verdict = "SCOPED_POSITIVE_NORMAL_PASS"
    limitations = @(
        "STATIC_MANAGED_NORMAL_EVIDENCE_ONLY: Verification conducted strictly via isolated positive pure normal managed runner controls (18/18 PASS) with Master-approved frozen dependencies.",
        "NATIVE_PROMOTION_FULL_E2_NOT_RELEASED: In-engine, game runtime, native execution, and operator promotion were strictly prohibited and not executed.",
        "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
        "POLICY_CACHE_PATCHSETTINGS_OPERATOR_SEPARATE: Policy cache generation, user mod settings/patch dynamic evaluation, and real operator provenance remain separate OPEN gates.",
        "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Dedicated Server remains final Domain Authority; Master governs release."
    )
    artifacts = $artifacts
}

$jsonText = [Newtonsoft.Json.JsonConvert]::SerializeObject($completionObj, [Newtonsoft.Json.Formatting]::Indented)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$destPath = "Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R12-PACKAGE-ORDER-20261009-DIRECT-e9dcd1e6\COMPLETION.json"
[System.IO.File]::WriteAllText($destPath, $jsonText, $utf8NoBom)

Write-Host "Created $destPath successfully."
Write-Host "Total Artifacts Count: $($artifacts.Count)"
