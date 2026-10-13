$root = 'C:\Users\user\Desktop\RimMulti'

$artifactDefs = @(
  @{ role = "implementation_report"; path = "C:\Users\user\Desktop\RimMulti\docs\POC_EngineHost_Content_Codec_Gate05_R10.md" },
  @{ role = "release_manifest"; path = "C:\Users\user\Desktop\RimMulti\docs\RELEASE_MANIFEST_ENGINE_GATE05_R10_PACKAGE_POLICY.json" },
  @{ role = "harness"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\Harness\Program.cs" },
  @{ role = "harness_project"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\Harness\Gate05R10PackageRunner.csproj" },
  @{ role = "results"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\results.json" },
  @{ role = "raw_evidence"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\raw_console.txt" },
  @{ role = "candidate_binary"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"; mvid = "7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb" },
  @{ role = "pdb"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb" },
  @{ role = "alternate_binary"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"; mvid = "afe11c93-fc73-4002-a9e2-b976ce10f9e3" },
  @{ role = "alternate_pdb"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb" },
  @{ role = "deployed_assembly"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"; mvid = "7ef10d5b-de1c-4e04-bdb4-3a03c4c316fb" },
  @{ role = "deployed_pdb"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb" },
  @{ role = "source"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.cs" },
  @{ role = "source_census"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs" },
  @{ role = "source_csproj"; path = "C:\Users\user\Desktop\RimMulti\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj" },
  @{ role = "pre_run_manifest"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\CANDIDATE_PRE_RUN_MANIFEST.json" },
  @{ role = "engine_freeze_before"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\ENGINE_FREEZE_BEFORE.json" },
  @{ role = "engine_freeze_after"; path = "C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R10PackagePolicy\ENGINE_FREEZE_AFTER.json" },
  @{ role = "work_log"; path = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\A_WORK_LOG.md" },
  @{ role = "recovery_ack"; path = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\A_RECOVERY_ACK.md" },
  @{ role = "ack_json"; path = "C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\ACK.json" }
)

$artifacts = @()
foreach ($d in $artifactDefs) {
    if (!(Test-Path $d.path)) {
        throw "Missing artifact file: $($d.path)"
    }
    $h = (Get-FileHash $d.path -Algorithm SHA256).Hash
    $s = (Get-Item $d.path).Length
    $item = [ordered]@{
        "role" = $d.role
        "path" = $d.path
        "sha256" = $h
        "size" = $s
    }
    if ($d.ContainsKey("mvid")) {
        $item["mvid"] = $d.mvid
    }
    $artifacts += $item
    Write-Host "$($d.role): $($d.path) ($s bytes, $h)"
}

$completion = [ordered]@{
  "schema_version" = 1
  "producer" = "A"
  "report_kind" = "E1"
  "dispatch_id" = "WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb"
  "wp_id" = "WP_ENGINE_GATE05_R10_PACKAGE_POLICY"
  "wp_revision" = "GATE05-R10-PACKAGE-POLICY"
  "result_id" = "WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-RESULT-01"
  "status" = "COMPLETED"
  "completed_at" = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.ffffff+00:00")
  "summary" = "WP_ENGINE_GATE05_R10_PACKAGE_POLICY / GATE05-R10-PACKAGE-POLICY package policy boundary technical implementation completed and developer E1 verification recorded. Successfully defined typed ExpectedPackagePolicyRecord, deterministic canonical policy digest computation (ComputePackagePolicyDigest), and pure package comparison and admission helpers (CheckPackagePolicy, TryAdmitWithPackagePolicy) comparing observed activeMods against distinct expected policy. Removed default-only POC_DECLARED_PACKAGES_ONLY assertion from ModPatchSettingsDispositionRecord, defaulting to UNCONFIGURED and binding admitted profiles to explicit CHECKED_POLICY:{policyId}:{revision}. Connected ComputeActualContentProfileManifest to the pure package check before trusted fingerprint success with a defensive fail-closed unconfigured configuration seam (ConfigureExpectedPackagePolicy). Preserved R9 version meaning repair (null modVersion preserved across Invariant, en-US, de-DE), child observation fail-closed, composite key uniqueness, Def family canonical sorting, and immutable baselines (WorkerBridge.cs, WorkerBridge.csproj, EngineHostCensus.cs prefix 72,547 bytes SHA F3C4F865...). Executed positive pure normal DTO/helper unit harness (19/19 PASS) with Master-approved frozen managed dependencies. Bound actual PE MVIDs for Debug (7ef10d5b-...) and Release (afe11c93-...) candidates. All historical lineages and installed incident preserved as OPEN."
  "e1_verdict" = "IMPLEMENTATION_PARTIAL"
  "limitations" = @(
    "NATIVE_UNTESTED: In-engine and game runtime execution was strictly prohibited under WP_ENGINE_GATE05_R10_PACKAGE_POLICY. Verification was conducted via isolated positive pure normal DTO and package policy helper unit harness (19/19 PASS).",
    "INSTALLED_DLL_INCIDENT_OPEN: Steam installed DLL (BB3B52...) discrepancy against archive baseline (2D64FF...) remains an UNKNOWN OPEN INCIDENT, preserved unmodified per Master policy.",
    "SEPARATE_OPERATOR_NATIVE_GATE: Configuration seam existence does not prove operator-owned origin; actual policy installation and worker/validator operator provenance remain a separate native gate.",
    "NO_SELF_CLOSURE: Developer A does not self-declare candidate release, E2 verification, or defect closure. Gate05 defects, Engine002/006, Pipeline007, and Foundation HOLD remain OPEN pending Master disposition and independent Sol QA review."
  )
  "artifacts" = $artifacts
}

$destPath = 'C:\Users\user\Desktop\RimMulti\Dispatcher\A_TASKS\WE-A-ENGINE-GATE05-R10-PACKAGE-POLICY-20261009-DIRECT-81a28ecb\COMPLETION.json'
[System.IO.File]::WriteAllText($destPath, ($completion | ConvertTo-Json -Depth 10), [System.Text.Encoding]::UTF8)
Write-Host "Successfully generated COMPLETION.json with 21 artifacts at $destPath"
