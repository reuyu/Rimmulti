$ErrorActionPreference = "Stop"

$workspaceRoot = "C:\Users\user\Desktop\RimMulti"
$scratchDir = "$workspaceRoot\scratch\EngineGate05R15PublicManifestBoundary"

$sha256 = [System.Security.Cryptography.SHA256]::Create()

function Get-Info([string]$path) {
    if (-not (Test-Path $path)) { throw "File not found: $path" }
    $bytes = [System.IO.File]::ReadAllBytes($path)
    $hash = -join ($sha256.ComputeHash($bytes) | ForEach-Object { $_.ToString("X2") })
    $mvid = $null
    if ($path.EndsWith(".dll") -or $path.EndsWith(".exe")) {
        $asm = [System.Reflection.Assembly]::Load($bytes)
        $mvid = $asm.ManifestModule.ModuleVersionId.ToString()
    }
    return @{
        path = $path.Replace("$workspaceRoot\", "")
        sha256 = $hash
        size = $bytes.Length
        mvid = $mvid
    }
}

$selCandidate = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.dll"
$selPdb = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Debug\net472\WarEconomy.WorkerBridge.PoC.pdb"
$altCandidate = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.dll"
$altPdb = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\bin\Release\net472\WarEconomy.WorkerBridge.PoC.pdb"
$depCandidate = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll"
$depPdb = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb"

$srcWorkerBridge = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.cs"
$srcCensus = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\EngineHostCensus.cs"
$srcCsproj = Get-Info "$workspaceRoot\scratch\WorkerBridgeMod\Source\WorkerBridge.csproj"

$runnerCsproj = Get-Info "$scratchDir\Harness\Gate05R15BoundaryRunner.csproj"
$runnerProgram = Get-Info "$scratchDir\Harness\Program.cs"
$runnerBinary = Get-Info "$scratchDir\Harness\bin\Debug\net472\Gate05R15BoundaryRunner.exe"
$runnerPdb = Get-Info "$scratchDir\Harness\bin\Debug\net472\Gate05R15BoundaryRunner.pdb"

$manifest = [ordered]@{
    manifest_version = "1.0"
    run_id = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-RUN-01"
    work_package = "WP_ENGINE_GATE05_R15_PUBLIC_MANIFEST_BOUNDARY"
    revision = "GATE05-R15-PUBLIC-MANIFEST-BOUNDARY"
    pinned_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    agent = "Antigravity A"
    dispatch_id = "WE-A-ENGINE-GATE05-R15-PUBLIC-MANIFEST-BOUNDARY-20261009-DIRECT-03649052"
    selected_candidate = [ordered]@{
        path = $selCandidate.path
        sha256 = $selCandidate.sha256
        size = $selCandidate.size
        mvid = $selCandidate.mvid
    }
    selected_pdb = [ordered]@{
        path = $selPdb.path
        sha256 = $selPdb.sha256
        size = $selPdb.size
    }
    alternate_candidate = [ordered]@{
        path = $altCandidate.path
        sha256 = $altCandidate.sha256
        size = $altCandidate.size
        mvid = $altCandidate.mvid
    }
    alternate_pdb = [ordered]@{
        path = $altPdb.path
        sha256 = $altPdb.sha256
        size = $altPdb.size
    }
    deployed_candidate = [ordered]@{
        path = $depCandidate.path
        sha256 = $depCandidate.sha256
        size = $depCandidate.size
        mvid = $depCandidate.mvid
    }
    deployed_pdb = [ordered]@{
        path = $depPdb.path
        sha256 = $depPdb.sha256
        size = $depPdb.size
    }
    sources = @(
        [ordered]@{ path = $srcWorkerBridge.path; sha256 = $srcWorkerBridge.sha256; size = $srcWorkerBridge.size },
        [ordered]@{ path = $srcCensus.path; sha256 = $srcCensus.sha256; size = $srcCensus.size },
        [ordered]@{ path = $srcCsproj.path; sha256 = $srcCsproj.sha256; size = $srcCsproj.size }
    )
    runner = [ordered]@{
        project = [ordered]@{ path = $runnerCsproj.path; sha256 = $runnerCsproj.sha256; size = $runnerCsproj.size }
        source = [ordered]@{ path = $runnerProgram.path; sha256 = $runnerProgram.sha256; size = $runnerProgram.size }
        binary = [ordered]@{ path = $runnerBinary.path; sha256 = $runnerBinary.sha256; size = $runnerBinary.size; mvid = $runnerBinary.mvid }
        pdb = [ordered]@{ path = $runnerPdb.path; sha256 = $runnerPdb.sha256; size = $runnerPdb.size }
    }
}

$json = $manifest | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText("$scratchDir\CANDIDATE_PRE_RUN_MANIFEST.json", $json, [System.Text.Encoding]::UTF8)

Write-Host "CANDIDATE_PRE_RUN_MANIFEST.json successfully created."
